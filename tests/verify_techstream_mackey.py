#!/usr/bin/env python3
"""Verify the recovered Techstream MACKey Registration data flow."""

from __future__ import annotations

import hashlib
import re
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


print(f"\n== RESULT: {passed} passed, {failed} failed ==")
sys.exit(1 if failed else 0)
