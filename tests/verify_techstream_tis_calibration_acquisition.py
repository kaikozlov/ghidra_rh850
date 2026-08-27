#!/usr/bin/env python3
"""Verify Toyota/TIS calibration acquisition and ECU-supply-change search inputs.

This suite independently pins the V18 remote calibration service, the local
managed download/extraction sink, and the exact part-number data flow used to
build the ECU-supply-change search XML. It deliberately distinguishes the TIS
client/PEC identity from ECU software part numbers and does not claim that a
missing package is available on Toyota's service.
"""
from __future__ import annotations

import hashlib
import struct
import sys
from pathlib import Path

import dnfile
import pefile
from dncil.cil.body import CilMethodBody

REPO = Path(__file__).resolve().parents[1]
ROOT = REPO / "software/Techstream/v18/unpacked/toyota/Toyota Diagnostics/Techstream"
BIN = ROOT / "bin"
sys.path.insert(0, str(REPO / "tools/techstream"))
from inspect_dotnet_il import MethodBodyReader, format_operand  # noqa: E402
from parse_ddb import DDBParser  # noqa: E402

passed = failed = 0
oracle = "independent_external_artifact+raw_bytes"


def check(name: str, condition: object, detail: str = "") -> None:
    global passed, failed
    ok = bool(condition)
    passed += int(ok)
    failed += int(not ok)
    print(f"[{'PASS' if ok else 'FAIL'}][{oracle}] {name}" + (f" ({detail})" if detail else ""))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_pe(path: Path) -> tuple[bytes, pefile.PE]:
    data = path.read_bytes()
    pe = pefile.PE(str(path))
    pe.parse_data_directories()
    return data, pe


def off(pe: pefile.PE, va: int) -> int:
    return pe.get_offset_from_rva(va - pe.OPTIONAL_HEADER.ImageBase)


def anchor(data: bytes, pe: pefile.PE, va: int, hex_bytes: str) -> bool:
    want = bytes.fromhex(hex_bytes)
    start = off(pe, va)
    return data[start:start + len(want)] == want


def cstr(data: bytes, pe: pefile.PE, va: int, limit: int = 512) -> bytes:
    start = off(pe, va)
    return data[start:start + limit].split(b"\0", 1)[0]


def imports(pe: pefile.PE) -> set[str]:
    return {
        item.name.decode(errors="replace")
        for desc in pe.DIRECTORY_ENTRY_IMPORT
        for item in desc.imports
        if item.name
    }


def exports(pe: pefile.PE) -> set[str]:
    return {
        item.name.decode(errors="replace")
        for item in pe.DIRECTORY_ENTRY_EXPORT.symbols
        if item.name
    }


def records(section) -> list[bytes]:
    size = section.decoded_record_size
    data = section.decoded_data
    return [data[i * size:(i + 1) * size] for i in range(section.header.record_count)]


def u16(raw: bytes, pos: int) -> int:
    return struct.unpack_from("<H", raw, pos)[0]


def master_variable_blob(master, index: int) -> bytes:
    sec = master.sections[0]
    count = sec.header.record_count
    table_end = count * 6
    rel, length = struct.unpack_from("<IH", sec.decoded_data, (index - 1) * 6)
    return sec.decoded_data[table_end + rel:table_end + rel + length]


def method_ops(pe: dnfile.dnPE, type_name: str, method_name: str) -> list[tuple[str, str]]:
    for type_row in pe.net.mdtables.TypeDef:
        if str(type_row.TypeName) != type_name:
            continue
        for method_index in type_row.MethodList:
            row = method_index.row
            if str(row.Name) == method_name:
                body = CilMethodBody(MethodBodyReader(pe, row))
                return [
                    (str(ins.opcode), format_operand(pe, ins.operand))
                    for ins in body.instructions
                ]
    raise AssertionError(f"missing managed method {type_name}::{method_name}")


def op_indexes(ops: list[tuple[str, str]], needle: str) -> list[int]:
    return [i for i, (_, operand) in enumerate(ops) if needle in operand]


required = [
    "Techstream.exe", "tiswebapi.dll", "IT3TechstreamDotNetUtilityAPI.dll",
    "IT3TechstreamDotNetUtility.dll", "CommandAPI.dll", "GetPartNumber_DT.dll",
]
if not ROOT.is_dir() or any(not (BIN / name).is_file() for name in required):
    print("[SKIP] Techstream V18 acquisition artifacts unavailable")
    raise SystemExit(77)

expected = {
    "Techstream.exe": (35852288, "e6b7ab884c99a941d603251fb856a77a515639fdcd1d266e875cbd1abceb5e54"),
    "tiswebapi.dll": (565248, "73d8251c46fb0c9b9cac4005f257443f5574d018cb4dc4bbda486c23829e55fe"),
    "IT3TechstreamDotNetUtilityAPI.dll": (167936, "d30e769964a8c387d4d76fabda9872c17adc9007b3146c7c4d1a2fc299eb6a5f"),
    "IT3TechstreamDotNetUtility.dll": (17408, "35667480bac46f6b9b2e8bef90c2c5076c9ad90e50ce79af9942a403d84e6a6d"),
    "CommandAPI.dll": (1257472, "43913a3baeef678b70dd3f7a533575824d9d88e2acb61acb23702983e5b337f3"),
    "GetPartNumber_DT.dll": (57344, "76d175eb5cb075c6efe5f693f8edfcb90d6ff2d5e1fcc828bfc77a0ca73ab523"),
}
for name, identity in expected.items():
    p = BIN / name
    check(f"{name} exact identity", (p.stat().st_size, sha(p)) == identity)

tech_data, tech_pe = load_pe(BIN / "Techstream.exe")
tis_data, tis_pe = load_pe(BIN / "tiswebapi.dll")
bridge_data, bridge_pe = load_pe(BIN / "IT3TechstreamDotNetUtilityAPI.dll")
part_data, part_pe = load_pe(BIN / "GetPartNumber_DT.dll")
cmd_data, cmd_pe = load_pe(BIN / "CommandAPI.dll")

print("\n== remote TIS calibration service ==")
tis_exports = exports(tis_pe)
for operation in (
    "TisServiceSendSearchInfo", "TisServiceGetSearchInfo",
    "TisServiceDownloadCalFile", "TisServiceGetCalFileURL",
):
    check(f"tiswebapi exports {operation}", any(operation in name for name in tis_exports))

# This statically-unpacked Techstream image no longer has a normal PE import
# directory for tiswebapi, but its import-name table and IAT call sites remain
# byte-visible. Pin the decorated imported names directly.
for operation in (
    "TisServiceSendSearchInfo", "TisServiceGetSearchInfo",
    "TisServiceDownloadCalFile", "TisServiceGetCalFileURL",
):
    check(
        f"Techstream carries imported tiswebapi symbol {operation}",
        operation.encode() in tech_data and b"@CWebService@@" in tech_data,
    )

for token in (
    b"requestSearchInfo", b"sendSearchInfo", b"ecuhardwareid", b"ecusoftwareid",
    b"CalibrationFile_URL", b"CalibrationId", b"NewCalibrationId",
    b"<Filename>", b"<Filesize>",
):
    check(f"tiswebapi protocol token {token.decode(errors='replace')}", token in tis_data)

check(
    "Techstream exposes ECU-supply-change search/login endpoint configuration keys",
    b"ECUSupplyChange_upload|URL\0" in tech_data
    and b"ECUSupplyChange_Login|URL\0" in tech_data
    and b"ECUSupplyChange_uploadgetcal|URL\0" in tech_data
    and b"ECUSupplyChange_Logingetcal|URL\0" in tech_data,
)
check(
    "SendSearchInfo request logs file path, client software ID and timestamp",
    b"-- Send -- strFileNamePath[%s] strSoftwareId[%s] strTimeStamp[%s]\0" in tech_data,
)
check(
    "SendSearchInfo obtains strSoftwareId from CTISCommon::GetPecID before the web call",
    anchor(tech_data, tech_pe, 0x00B99978, "8d9568ffffff8bce52e8eabdffff")
    and b" CTISCommon::GetPecID \0" in tech_data
    and anchor(tech_data, tech_pe, 0x00B99A7C, "8d4dcc8d55e4518d45d452508bceff15b833f500"),
)

print("\n== search XML inputs ==")
for token in (
    b"reqData\0", b"vinNo\0", b"ecuInfo\0", b"ecuId\0", b"ecuAssyNo\0",
    b"writeFlg\0", b"baseSwNoLst\0", b"baseSwNo\0",
):
    check(f"Techstream search XML token {token[:-1].decode()}", token in tech_data)

# SaveEcuSupplyChangeSendXmlFile creates baseSwNoLst then inserts <=16-byte
# baseSwNo strings fetched from the per-ECU record's +0x0C string-array member.
check(
    "search XML creates baseSwNoLst and writes 16-byte baseSwNo entries",
    anchor(tech_data, tech_pe, 0x005209A8, "c00f858402000057ff151c30f5006aff6800961e01")
    and anchor(tech_data, tech_pe, 0x00520A58, "e0c645fc1be82a858a008d4da4c645fc15e818858a006a016a0157576a016a106a0151"),
)

# AddEcuSupplyChangeDataPerEcu receives CGetPartNumberApiRcv at [ebp-0xE8].
# Its +0x04 CString is copied to output+0x04; its +0x08 CStringArray count/list
# is iterated and non-empty strings are appended to output+0x0C.
check(
    "ECU-supply-change caller requests both ECU and software part numbers",
    anchor(tech_data, tech_pe, 0x0051F634, "8b550c8b4d08c6459001c6459101"),
)
check(
    "GetPartNumber receive ECU part number is copied to per-ECU record +0x04",
    anchor(tech_data, tech_pe, 0x0051F657, "e8549b65008bf03bf38975dc0f858e000000")
    and anchor(tech_data, tech_pe, 0x0051F669, "8b45108d951cffffff528d4804e811998a00"),
)
check(
    "GetPartNumber software-part array is iterated into per-ECU record +0x0C",
    anchor(tech_data, tech_pe, 0x0051F67B, "8bbd28ffffff33f63bf77d6d8d4dec56518d8d20ffffff")
    and anchor(tech_data, tech_pe, 0x0051F6C6, "8b45108d55e0528d480c8b401450e8339a8a00"),
)

print("\n== Toyota GetPartNumber API semantics ==")
for token in (
    b"-- Send -- m_dwEcuId[%d], m_bEcuPartNum[%d], m_bSoftPartNum[%d]",
    b"-- Receive -- m_strEcuPartNum=[%s], m_cSoftPartNumArray Count=[%d]",
    b"-- Receive -- m_cSoftPartNumArray(%d/%d)=[%s]",
):
    check(f"CommandAPI field vocabulary {token.decode()}", token + b"\0" in cmd_data)
check(
    "CGetPartNumberApiRcv layout is CString +0x04 and CStringArray +0x08",
    anchor(cmd_data, cmd_pe, 0x100945E2, "8d4e04")
    and anchor(cmd_data, cmd_pe, 0x100945F2, "8d4e08"),
)

# The phase-5 plugin selects operation 0x66. For category 435 this maps to
# ComSet1/frame 0x03E9; that static frame is only 3E00. The part-number plugin
# then replaces/materializes its working frame using code-local 22/62 templates.
p = DDBParser()
EXPECTED_FUNC = bytes.fromhex("b30166000100e9030000010000000000")
EXPECTED_FRAME = bytes.fromhex("e903070500000000")
for region in ("NA", "EU", "JP"):
    master = p.parse_master_db(ROOT / region / "DB/Toyota.ddb")
    funcs = [r for r in records(master.sections[18]) if u16(r, 0) == 435 and u16(r, 2) == 0x66]
    frames = [r for r in records(master.sections[17]) if u16(r, 0) == 0x03E9]
    check(f"{region} category-435 GetPartNumber selector 0x66 exact row", funcs == [EXPECTED_FUNC])
    check(
        f"{region} selector 0x66 base frame is 3E00",
        frames == [EXPECTED_FRAME] and master_variable_blob(master, 0x0507) == bytes.fromhex("3e00"),
    )

check(
    "GetPartNumber_DT selects GetCommFrmInfo 0x66",
    anchor(part_data, part_pe, 0x10001148, "8b481c8b70208d8424900000005150526a668d8c24b4000000ff1514700010"),
)
check(
    "GetPartNumber_DT embeds ECU-part 0105 and software-part F181 request/mask/check templates",
    part_data[off(part_pe, 0x10007150):off(part_pe, 0x10007150) + 24]
    == bytes.fromhex("22010500ffffff006201050022f18100ffffff0062f18100"),
)
check(
    "0105 branch parses one 12-byte record from response index 3 into ECU-part field +0x20",
    anchor(part_data, part_pe, 0x1000133B, "8d5424188bcf526a036a0c6a0155e842040000")
    and anchor(part_data, part_pe, 0x1000135A, "6a008d4c241cff1534700010508b4424188d4820"),
)
check(
    "F181 branch uses response byte 3 as count and parses 16-byte records from index 4",
    anchor(part_data, part_pe, 0x100014AB, "6a038d4d58ff152c7000108a50088d4c241888542410")
    and anchor(part_data, part_pe, 0x100014C1, "518b4424146a0425ff0000006a1050558bcfe8b8020000"),
)
check(
    "F181 parsed records append to software-part output list +0x30",
    anchor(part_data, part_pe, 0x100014EE, "8b5424148d6a30578d4c241cff15347000108bcd8bd8ff1528700010"),
)

print("\n== remote URL to local calibration store ==")
check(
    "Techstream dynamically loads managed utility bridge and resolves auto-download API",
    anchor(tech_data, tech_pe, 0x0052CC31, "68e8a41e01ff157019f500")
    and anchor(tech_data, tech_pe, 0x0052CC60, "687ca41e0157ff157419f500"),
)
check(
    "managed utility bridge exports EcuSupplyChangeAutoDownloadCalFileAPI",
    "EcuSupplyChangeAutoDownloadCalFileAPI" in exports(bridge_pe),
)
managed = dnfile.dnPE(str(BIN / "IT3TechstreamDotNetUtility.dll"))
ops = method_ops(managed, "CEcuSupplyChange", "EcuSupplyChangeAutoDownloadCalFile")
for field in ("strDownloadUrl", "strDestinationDir"):
    check(f"managed downloader consumes {field}", bool(op_indexes(ops, field)))
for call in (
    "System.Net.WebClient::.ctor", "System.Net.WebClient::DownloadFile",
    "UncompressZipFile", "System.IO.Directory::GetFiles", "System.IO.File::Copy",
    "System.IO.Directory::Delete",
):
    check(f"managed downloader contains {call}", bool(op_indexes(ops, call)))
idx_download = op_indexes(ops, "System.Net.WebClient::DownloadFile")[0]
idx_unzip = op_indexes(ops, "UncompressZipFile")
idx_copy = op_indexes(ops, "System.IO.File::Copy")[0]
idx_cleanup = op_indexes(ops, "System.IO.Directory::Delete")[0]
check(
    "managed downloader order is download -> unzip/nested unzip -> copy -> cleanup",
    idx_download < idx_unzip[0] < idx_unzip[-1] < idx_copy < idx_cleanup
    and len(idx_unzip) >= 2,
)
check(
    "managed downloader searches nested zip archives",
    any(op == "ldstr" and operand == repr("*.zip") for op, operand in ops)
    and any(op == "ldstr" and operand == repr(".zip") for op, operand in ops),
)

print(f"\nResults: {passed} passed, {failed} failed")
raise SystemExit(1 if failed else 0)
