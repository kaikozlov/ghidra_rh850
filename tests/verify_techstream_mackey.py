#!/usr/bin/env python3
"""Verify the recovered Techstream MACKey Registration data flow."""

from __future__ import annotations

import hashlib
import csv
import json
import re
import struct
import subprocess
import sys
from pathlib import Path

import dnfile
import pefile
from dncil.cil.body import CilMethodBody

REPO = Path(__file__).resolve().parents[1]
BIN = (
    REPO
    / "Techstream/unpacked/toyota/Toyota Diagnostics/Techstream/bin"
)
if not (BIN / "IT3UtilityRevNK.dll").exists():
    print("[SKIP] Techstream unpacked tree is not present")
    raise SystemExit(0)

sys.path.insert(0, str(REPO / "tools/techstream"))
from inspect_dotnet_il import MethodBodyReader, format_operand  # noqa: E402

passed = 0
failed = 0


def check(name: str, condition: bool, detail: str = "") -> None:
    global passed, failed
    if condition:
        passed += 1
        print(f"[PASS] {name}" + (f" ({detail})" if detail else ""))
    else:
        failed += 1
        print(f"[FAIL] {name}" + (f" ({detail})" if detail else ""))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def pe_body(pe: pefile.PE, data: bytes, va: int, size: int) -> bytes:
    offset = pe.get_offset_from_rva(va - pe.OPTIONAL_HEADER.ImageBase)
    return data[offset:offset + size]


def count_rel32_calls(body: bytes, body_va: int, target_va: int) -> int:
    count = 0
    for offset in range(max(0, len(body) - 4)):
        if body[offset] != 0xE8:
            continue
        displacement = struct.unpack_from("<i", body, offset + 1)[0]
        if body_va + offset + 5 + displacement == target_va:
            count += 1
    return count


def ascii_va(pe: pefile.PE, data: bytes, value: bytes) -> int:
    offset = data.index(value + b"\x00")
    return pe.OPTIONAL_HEADER.ImageBase + pe.get_rva_from_offset(offset)


def method_ops(
    pe: dnfile.dnPE, type_name: str, method_name: str
) -> list[tuple[str, str]]:
    for type_row in pe.net.mdtables.TypeDef:
        if str(type_row.TypeName) != type_name:
            continue
        for method_index in type_row.MethodList:
            row = method_index.row
            if str(row.Name) == method_name:
                body = CilMethodBody(MethodBodyReader(pe, row))
                return [
                    (str(instruction.opcode), format_operand(pe, instruction.operand))
                    for instruction in body.instructions
                ]
    raise AssertionError(f"method not found: {type_name}::{method_name}")


def operands(ops: list[tuple[str, str]], opcode: str) -> list[str]:
    return [operand for op, operand in ops if op == opcode]


def op_is(
    ops: list[tuple[str, str]], index: int, opcode: str, operand: str = ""
) -> bool:
    actual_opcode, actual_operand = ops[index]
    return actual_opcode == opcode and operand in actual_operand


print("== pinned primary artifacts ==")
expected_hashes = {
    "Techstream.exe": "e6b7ab884c99a941d603251fb856a77a515639fdcd1d266e875cbd1abceb5e54",
    "IT3UtilityNK.dll": "d973ddd452c3405fa38691bebe9b3a809c694e8c2159c28b685082ff168e3653",
    "IT3UtilityRevNK.dll": "8109eac3b3f163111a258f92f87e5e60f114f2da16187307cc9369e0b18c4f0b",
    "eVbBroker.dll": "5d5c937650e6452350ae0bd4ef54dffcc3199e80544612032b1f19ae8f4f6e00",
    "UtilityExNK2.dll": "8d9623f028f23876f69cb02baa10e1881c01fa01a4f906013bd36266f7e0fb33",
}
for name, expected in expected_hashes.items():
    check(f"{name} SHA-256", sha256(BIN / name) == expected)


print("\n== native web-service bridge ==")
native = pefile.PE(str(BIN / "IT3UtilityNK.dll"))
native_bytes = (BIN / "IT3UtilityNK.dll").read_bytes()
exports = {
    symbol.name.decode("ascii")
    for symbol in native.DIRECTORY_ENTRY_EXPORT.symbols
    if symbol.name
}
required_exports = {
    "CallTisGetMacKeyInfo_FromRev",
    "CallTisSendMacKey_FromRev",
    "GetMacKeyResId_FromRev",
    "GetMacKeyResFile_FromRev",
    "GetMacKeyResResult_FromRev",
    "GetSoapFault_FromRev",
}
check("native MACKey bridge exports are present", required_exports <= exports)
imports = {
    entry.name.decode("ascii")
    for descriptor in native.DIRECTORY_ENTRY_IMPORT
    for entry in descriptor.imports
    if entry.name
}
check("bridge imports CWebService::TisServiceSendMacKey",
      any("TisServiceSendMacKey@CWebService" in name for name in imports))
check("bridge imports CWebService::TisServiceGetMacKeyInfo",
      any("TisServiceGetMacKeyInfo@CWebService" in name for name in imports))
mackey_classes = set(re.findall(rb"\.\?AV(CMAC_01[^@]*)@@", native_bytes))
check("native utility contains 24 CMAC_01 RTTI classes",
      len(mackey_classes) == 24, f"got {len(mackey_classes)}")
required_response_tags = {
    b"<ExchangeKeyList>", b"<VehicleIdentificationNumber>",
    b"<HashValue>", b"<ResultCode>", b"<X-RequestID>",
    b"<ECUExchangeKey>", b"<MACK4>", b"<MACM1>", b"<MACM2>", b"<MACM3>",
}
check("native utility contains the recovered response XML vocabulary",
      all(tag in native_bytes for tag in required_response_tags))

techstream_bytes = (BIN / "Techstream.exe").read_bytes()
check("Techstream stores the MACKey SOAP endpoint key",
      b"MACKey_upload" in techstream_bytes)
check("Techstream stores the MACKey login endpoint key",
      b"MACKey_Login" in techstream_bytes)



print("\n== managed online workflow ==")
managed = dnfile.dnPE(str(BIN / "IT3UtilityRevNK.dll"))
user23 = method_ops(managed, "MAC_01_020", "MAC_01_020_bgDoWork_UserType2_3")
user23_strings = set(operands(user23, "ldstr"))
check("online path resolves the native send/get exports",
      {repr(value) for value in required_exports} <= user23_strings)
check("online path formats an explicit UTC timestamp",
      repr("yyyy/MM/dd HH:mm:ss:fffffff") in user23_strings)
check("online path substitutes $36 in the login URL",
      repr("$36") in user23_strings
      and any(operand.endswith("::Replace") for operand in operands(user23, "callvirt")))
check("online path hashes the returned request ID with SHA-256",
      any("SHA256CryptoServiceProvider" in operand
          for operand in operands(user23, "newobj")))
check("native request ID return is converted and stored in local 0x1F",
      op_is(user23, 265, "callvirt", "Invoke")
      and op_is(user23, 268, "call", "PtrToStringAnsi")
      and op_is(user23, 269, "stloc.s", "local(0x001F)"))
check("the same request ID local replaces $36",
      op_is(user23, 286, "ldstr", "$36")
      and op_is(user23, 287, "ldloc.s", "local(0x001F)")
      and op_is(user23, 288, "callvirt", "System.String::Replace"))
check("the same request ID local is UTF-8 encoded then SHA-256 hashed",
      op_is(user23, 359, "call", "Encoding::get_UTF8")
      and op_is(user23, 360, "ldloc.s", "local(0x001F)")
      and op_is(user23, 361, "callvirt", "Encoding::GetBytes")
      and op_is(user23, 363, "newobj", "SHA256CryptoServiceProvider")
      and op_is(user23, 367, "callvirt", "HashAlgorithm::ComputeHash"))
check("poll invocation receives request ID and its uppercase digest",
      op_is(user23, 423, "ldloc.s", "local(0x001F)")
      and op_is(user23, 424, "callvirt", "StringBuilder::Append")
      and op_is(user23, 437, "ldloc.s", "local(0x000A)")
      and op_is(user23, 438, "ldloc.s", "local(0x0029)")
      and op_is(user23, 439, "ldloc.s", "local(0x0028)")
      and op_is(user23, 440, "callvirt", "Invoke"))
check("online path writes the returned key XML file",
      repr("\\Memg\\MAC_01_WriteData.xml") in user23_strings)
check("online path polls result codes 0 through 4",
      {repr(str(value)) for value in range(5)} <= user23_strings)

user1 = method_ops(managed, "MAC_01_020", "MAC_01_020_bgDoWork_UserType1")
check("user-type-1 path opens the configured MACKey URL",
      "GetMACKeyURL" in operands(user1, "callvirt")
      and "Navigate" in operands(user1, "callvirt"))
for method_name in ("MAC_01_IEThreadFuncLow", "MAC_01_IEThreadFuncMed"):
    browser = method_ops(managed, "MAC_01_020", method_name)
    browser_strings = set(operands(browser, "ldstr"))
    check(f"{method_name} targets the ECUExchangeKey DOM field",
          repr("ECUExchangeKey") in browser_strings)
    check(f"{method_name} injects the formatted XML document",
          "GetFormatXmlDocument" in operands(browser, "callvirt"))


print("\n== ECUExchangeKey request construction ==")
create_xml = method_ops(managed, "MAC_01_CommonProcess", "MAC_01_CreateXML")
xml_strings = set(operands(create_xml, "ldstr"))
required_xml_names = {
    "ECUExchangeKey",
    "X-Version",
    "GTS",
    "SoftwareID",
    "SoftwareVersion",
    "LicenseKey",
    "ServicePlantFlag",
    "HashValue",
    "VehicleIdentificationNumber",
    "MasterECU",
    "SafekeyNumber",
    "MACM1",
    "MACM2",
    "MACM3",
    "SlaveECUList",
    "SlaveECU",
}
check("request XML contains every recovered field",
      {repr(value) for value in required_xml_names} <= xml_strings)
check("request HashValue uses SHA256Managed",
      any("SHA256Managed" in operand for operand in operands(create_xml, "newobj")))
copy_lengths = [
    create_xml[index - 2][1]
    for index, (opcode, operand) in enumerate(create_xml[:240])
    if opcode == "call" and "System.Array::Copy" in operand
]
check("hash preimage copies VIN and fixed-width uppercase key fields in order",
      copy_lengths[:5] == ["0x11", "0x20", "0x20", "0x40", "0x20"],
      f"copy lengths={copy_lengths[:5]}")
check("SHA-256 consumes the assembled preimage buffer local 0x17",
      op_is(create_xml, 242, "ldloc.s", "local(0x001A)")
      and op_is(create_xml, 243, "ldloc.s", "local(0x0017)")
      and op_is(create_xml, 244, "callvirt", "HashAlgorithm::ComputeHash")
      and op_is(create_xml, 245, "stloc.s", "local(0x001B)"))
check("computed digest string is assigned to the HashValue element",
      op_is(create_xml, 254, "ldloc.s", "local(0x001B)")
      and op_is(create_xml, 255, "call", "BitConverter::ToString")
      and op_is(create_xml, 381, "ldstr", "HashValue")
      and op_is(create_xml, 385, "ldloc.s", "local(0x001D)")
      and op_is(create_xml, 386, "callvirt", "XmlNode::set_InnerText"))
check("request writes a timestamped XML under ECUSecurityKey",
      repr("\\Techstream\\ECUSecurityKey\\") in xml_strings
      and repr("yyyyMMddHHmmss") in xml_strings)

shared = method_ops(managed, "SharedMemory", "read_xmldata_MAC01")
array_sizes = [
    operand
    for index, (opcode, operand) in enumerate(shared)
    if opcode == "newarr" and index > 0
    for operand in [shared[index - 1][1]]
]
check("shared-memory request fields have 17/16/16/32/16-byte shapes",
      array_sizes[:5] == ["0x11", "0x10", "0x10", "0x20", "0x10"],
      f"got {array_sizes[:5]}")
check("shared-memory reader starts payload at offset 2",
      any(opcode == "ldc.i4.2" for opcode, _ in shared))


print("\n== generated native vehicle protocol ==")
generator = REPO / "tools/generate_techstream_mackey_protocol.py"
generated_json = REPO / "data/generated/techstream_v18/mackey_vehicle_protocol.json"
generated_csv = REPO / "data/generated/techstream_v18/mackey_state_machine.csv"
result = subprocess.run(
    [sys.executable, str(generator), "--check"], cwd=REPO,
    text=True, capture_output=True, check=False,
)
check("generated MACKey evidence is current", result.returncode == 0,
      (result.stdout + result.stderr).strip())
protocol = json.loads(generated_json.read_text())
with generated_csv.open(newline="") as stream:
    state_rows = list(csv.DictReader(stream))

classes = protocol["rtti_classes"]
check("generated RTTI census names all 24 classes", len(classes) == 24)
check("native bridge pins all twelve UtilityEx MACKey imports",
      len(protocol["companion_imports"]) == 12
      and all("Ex2MAC_01" in name for name in protocol["companion_imports"]))
expected_vtables = {
    "CMAC_01": ("0x103ceb10", 84),
    "CMAC_01_000": ("0x103cec64", 118),
    "CMAC_01_000_S": ("0x103cee40", 118),
    "CMAC_01_000A": ("0x103cf01c", 118),
    "CMAC_01_001A": ("0x103cf1f8", 118),
    "CMAC_01_001B": ("0x103cf3d4", 113),
    "CMAC_01_001C": ("0x103cf59c", 118),
    "CMAC_01_001C_S": ("0x103cf778", 118),
    "CMAC_01_001D": ("0x103cf954", 118),
    "CMAC_01_001E": ("0x103cfb30", 113),
    "CMAC_01_001F": ("0x103cfcf8", 118),
    "CMAC_01_001F_S": ("0x103cfed4", 118),
    "CMAC_01_009A": ("0x103d00b0", 118),
    "CMAC_01_009A_S": ("0x103d028c", 118),
    "CMAC_01_009B": ("0x103d0468", 118),
    "CMAC_01_009B_S": ("0x103d0644", 118),
    "CMAC_01_015": ("0x103d0820", 118),
    "CMAC_01_017": ("0x103d09fc", 118),
    "CMAC_01_025_S": ("0x103d0bd8", 113),
    "CMAC_01_028_S": ("0x103d0da0", 118),
    "CMAC_01_031_S": ("0x103d0f7c", 118),
    "CMAC_01_036_S": ("0x103d1158", 118),
    "CMAC_01_038_S": ("0x103d1334", 118),
    "CMAC_01_039_S": ("0x103d1510", 113),
}
actual_vtables = {
    item["name"]: (item["vtable_va"], item["vtable_entries"])
    for item in classes
}
check("all native vtable locations and widths are pinned",
      actual_vtables == expected_vtables)
expected_states = {
    f"S324-{state}"
    for item in classes for state in item["states"]
}
check("all 51 distinct S324 procedure codes are represented",
      len(expected_states) == 51
      and expected_states
      == {value.decode("ascii") for value in re.findall(rb"S324-[0-9A-F]+", native_bytes)},
      f"got {len(expected_states)}")
check("state-machine CSV covers every class/state association",
      len([row for row in state_rows if row["row_kind"] == "state"])
      == sum(len(item["states"]) for item in classes))

expected_body_hashes = {
    "decode_exchange_records": "b8e4a3b44251c8b172053f363947bb95fdbafc9c894d137f3ed53ba93c338334",
    "discover_master_slaves": "7c0d3814f5e81441b19959ad966fc7fa0650845af865376075b290b45d5230cb",
    "parse_exchange_key_entry": "bd71fb24d3ed5bf8d1fba70ca76470be542ec7c1676034d3740e59155a75da43",
    "poll_key_update_3002": "35857d4c2eb7e266fa6a096fc444c3576909e4964797b9ae55295e5ffc7a2093",
    "read_mac_tuple_102e": "a903c56eb8fa3df66435962d9bbeb2551bbcbb6b3ecfe8c6b77d51ad0908c014",
    "read_safekey_1010": "2b95a7bfc3bc8639f12ecf776d931a1144bcf51fca4f711d81b6a80c32748b54",
    "read_vin_f190": "d4b9e46e17cef3e2916415df61b55b0c9a0d3e98e99fb4420cac74e1605a715f",
    "security_key_2742": "f630da58c41f2357a282c40029d7b543a209ffa3cccd72888e779e30886543c4",
    "security_seed_2741": "bc8f0c4b9d856d5682f520a4b5cfca0b3ac2fb13dcb9a41067afccef2d16fff8",
    "start_key_update_3002": "79acd1a60e651c19900f8af5f65a51e3383016450fc062662f3ffb957d5fef43",
    "write_topology_1035": "48356f7d4fa78eff9c55c3a32907b1087753d4326d78ff28983c2b8aee3b7f50",
}
actual_body_hashes = {
    name: details["sha256"] for name, details in protocol["function_bodies"].items()
    if name in expected_body_hashes
}
check("critical parser and diagnostic method bodies are pinned",
      actual_body_hashes == expected_body_hashes)

commands = {item["name"]: item for item in protocol["commands"]}
check("vehicle reads VIN through DID F190",
      commands["read VIN"]["request"] == "22 f1 90"
      and commands["read VIN"]["destination"] == "VIN[17]")
check("vehicle reads M1/M2/M3 through DID 102E",
      commands["read MAC tuple"]["request"] == "22 10 2e"
      and commands["read MAC tuple"]["response_length"] == ">=67")
check("SafekeyNumber is the raw 16-byte DID 1010 payload",
      commands["read SafekeyNumber"]["request"] == "22 10 10"
      and commands["read SafekeyNumber"]["destination"] == "SafekeyNumber[16]")
check("Techstream sends the server M1-M3 package through routine 3002",
      commands["start key update"]["request"]
      == "31 01 30 02 || M1[16] || M2[32] || M3[16]"
      and commands["start key update"]["request_length"] == 68)
check("Techstream polls routine 3002 for the 32+16-byte proof",
      commands["poll key update"]["request"] == "31 03 30 02"
      and commands["poll key update"]["destination"]
      == "state[2], M4[32], M5[16]")
check("Techstream and Sienna DID 1010 are not an exact diagnostic join",
      protocol["firmware_join"]["conclusion"]
      == "same cryptographic envelope; different service/procedure")

response = protocol["response_parser"]
check("response parser iterates bounded exchange-record lists",
      response["maximum_exchange_records"] == {"short_variant": 8, "standard": 28})
check("response parser preserves all M1-M4 field widths",
      response["record_fields"]
      == {"MACM1": 16, "MACM2": 32, "MACM3": 16, "MACK4": 32,
          "SafekeyNumber": 16})
check("master/slave association uses the raw safe-key identity",
      protocol["vehicle_architecture"]["association_key"]
      == "raw 16-byte SafekeyNumber"
      and protocol["vehicle_architecture"]["maximum_ecu_records"] == 8)


print("\n== MACK4 disposition (negative finding) ==")
mack4 = protocol["mack4_disposition"]
check("MACK4 is parsed but never reaches a vehicle write",
      mack4["consumed_by_vehicle_write"] is False)
check("MACK4 start_key_update payload is 68 bytes (header+M1+M2+M3 only)",
      mack4["start_key_update_payload"]
      == "header(4) + M1(16) + M2(32) + M3(16) = 68 bytes")
check("MACK4 does not appear in UtilityExNK2.dll",
      mack4["appears_in_utilityexnk2"] is False)
check("MACK4 does not appear in the managed layer",
      mack4["appears_in_managed"] is False)
check("MACK4 non-parse references are destructors only",
      mack4["non_parse_refs"] == "std::string destructors only")
check("MACK4 string appears exactly once in native DLL bytes",
      native_bytes.count(b"<MACK4>") == 1)
check("MACK4 string is absent from UtilityExNK2.dll",
      b"MACK4" not in (BIN / "UtilityExNK2.dll").read_bytes())
managed_bytes = (BIN / "IT3UtilityRevNK.dll").read_bytes()
check("MACK4 literal is absent from managed IT3UtilityRevNK.dll",
      b"MACK4" not in managed_bytes and "MACK4".encode("utf-16-le") not in managed_bytes)


print("\n== S324 state-reference evidence model ==")
state_model = protocol["state_reference_model"]
check("state model explicitly disclaims per-state operation ownership",
      state_model["meaning"]
      == "S324 string-reference census; no per-state operation ownership")
check("state-reference census has 61 associations across 60 unique functions",
      state_model["reference_associations"] == 61
      and state_model["unique_reference_functions"] == 60)
check("0x10241650 is the sole shared state-reference function",
      state_model["shared_reference_functions"]
      == {"0x10241650": ["08", "19"]})
check("S324-08 and S324-19 both record the shared 0x10241650 reference",
      "0x10241650" in state_model["references"]["08"]
      and state_model["references"]["19"] == ["0x10241650"])

csv_s324_41 = [
    row for row in state_rows
    if row["row_kind"] == "state" and row["class_state"] == "CMAC_01_001C/S324-41"
]
check("state CSV keeps state-code references separate from class operations",
      csv_s324_41
      and csv_s324_41[0]["state_code_reference_rvas"] == "0x23f900"
      and "handler_operations" not in csv_s324_41[0]
      and "handler_comprocess_calls" not in csv_s324_41[0]
      and "0:update_vehicle_status" in csv_s324_41[0]["class_operations"])

# The old review patch incorrectly treated wider class-region call counts as if
# they belonged to one displayed S324 state. Pin two primary counterexamples:
# S324-41's actual reference function has one direct ComProcess call, and a
# single native function references both S324-08 and S324-19 while making one
# direct operation-4 call. This is why operation ownership is not projected
# from S324 labels in the generated CSV.
body_41 = pe_body(native, native_bytes, 0x1023F900, 291)
check("S324-41 reference function has exactly one direct mackey_com_process call",
      count_rel32_calls(body_41, 0x1023F900, 0x10237970) == 1)
body_08_19 = pe_body(native, native_bytes, 0x10241650, 499)
check("shared S324-08/S324-19 reference function has one direct ComProcess call",
      count_rel32_calls(body_08_19, 0x10241650, 0x10237970) == 1)
check("shared function contains references to both S324-08 and S324-19 strings",
      struct.pack("<I", ascii_va(native, native_bytes, b"S324-08")) in body_08_19
      and struct.pack("<I", ascii_va(native, native_bytes, b"S324-19")) in body_08_19)
check("shared S324-08/S324-19 function's direct operation is selector 4",
      b"\x6a\x04\x50\xe8" in body_08_19)


print(f"\n== RESULT: {passed} passed, {failed} failed ==")
sys.exit(1 if failed else 0)
