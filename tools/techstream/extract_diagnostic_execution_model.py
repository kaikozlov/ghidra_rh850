#!/usr/bin/env python3
"""Recover Techstream's database-driven diagnostic execution model.

This is deliberately architecture-first: it pins the shared dispatcher/runtime
that turns Toyota master-DDB records into plugin selection, frame templates, and
transport calls instead of recovering one endpoint at a time.
"""
from __future__ import annotations

import argparse
import collections
import hashlib
import json
import os
import struct
from pathlib import Path

import pefile
from diagnostic_role_model import role_operation_catalog
from parse_ddb import ECU_TABLE_CLASS_NAMES, MASTER_TABLE_CLASS_NAMES, DDBParser
from techstream_paths import resolve_gts_root

REPO = Path(__file__).resolve().parents[2]
DEFAULT_OUT = REPO / "data/generated/techstream_v18/diagnostic_execution_model.json"

CORE_V18 = (
    "CommandAPI.dll",
    "DiagCommCtrlMain.dll",
    "CommandCommon.dll",
    "KgpDataCtrl.dll",
    "GetEcuFuncList.dll",
)

# Instruction windows are short byte anchors around the recovered GetDbRecord
# class-ID pushes and the shared transport calls.  VAs are from the pinned V18
# PE identities and are converted to file offsets through the PE section map.
ANCHORS = {
    "DiagCommCtrlMain.dll": {
        "plugin_db_class_0x113": (0x10001301, "578d4424146a0a5068130100"),
    },
    "CommandCommon.dll": {
        "func_comm_frame_db_class_0x112": (0x1005E1C6, "50565168120100008d8fbc00"),
        "comm_frame_db_class_0x111": (0x1006A986, "50518b4e10681101000081c1"),
        "comm_set_db_class_0x11d": (0x1006ABCB, "50518b4e10681d01000081c1"),
        "comm_set_field_copy": (0x1006ABEF, "8b4424148b108b0a894e188b108b4a04894e1c8b1033c08a420e894620"),
        "comm_set_retry_bound": (0x1005D211, "8b5e40894424508b46203bdd8944241c"),
        "comm_set_receive_timeout_convert": (0x1005D305, "8b5424508d6e1c8bc88b461455518b4e10525051e8c2e80000"),
        "comm_set_retry_loop": (0x1005D378, "8b4424188b4c241c403bc1894424187f7b"),
        "transport_send_sink": (0x1005D29D, "8b4e0c52ff1540040b10eb4a"),
        "transport_receive_sink": (0x1005D344, "ff1550040b108bf881ff2303"),
        "p5_support_pid_frame_lookup": (0x10063338, "68ca000000e8deadffff"),
        "p5_support_pid_transport": (0x1006339E, "e86da6ffff"),
        "p4_support_bit_frame_lookup": (0x1005F29C, "e87feeffff"),
        "p4_support_bit_transport": (0x1005F617, "e8e4e5ffff"),
        "enable_data_id_frame_lookup": (0x10056BA1, "e87a750000"),
        "enable_data_id_transport": (0x10056BC4, "e837720000"),
        "enable_rid_frame_lookup": (0x1005733D, "e8de6d0000"),
        "enable_rid_transport": (0x10057363, "e8986a0000"),
    },
    "KgpDataCtrl.dll": {
        "comm_set_lookup_key": (0x10014816, "8b148133c0668b420a8945e8"),
    },
    "GetEcuFuncList.dll": {
        "ecu_func_info_db_class_0x11a": (0x1000142E, "518b4e14681a01000081c1bc"),
        "ecu_func_detail_db_class_0x11b": (0x10001564, "8b4e1452681b01000081c1bc"),
    },
}

SELECTED_COMMON_PRIMITIVES = (
    "?GetCommFrmInfo@CCommCachePlus@@QAEKGPAUtagCOMMAND_DATA@@PAV?$CCmdList@VCCommFrameData@@@@K@Z",
    "?CommFrameSendReceive@CCommCachePlus@@QAEKPAVCCommFrameData@@G@Z",
    "?CommFrameSendReceiveExt@CCommCachePlus@@QAEKPAVCCommFrameData@@G@Z",
    "?CheckEcuFunc@CFuncInfoCache@@QAEHPAVCDataCtrl@@KGGGPAK@Z",
    "?GetEcuFunc@CFuncInfoCache@@QAEKPAVCDataCtrl@@KPAPAVCEcuFuncInfo@@PAH@Z",
    "?GetBusId@CEcuConnectBufferList@@QAEGK@Z",
)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def file_identity(path: Path, root: Path) -> dict:
    data = path.read_bytes()
    return {
        "path": path.relative_to(root).as_posix(),
        "size": len(data),
        "sha256": sha256(data),
    }


def parse_pe(path: Path) -> pefile.PE:
    pe = pefile.PE(str(path), fast_load=True)
    pe.parse_data_directories(
        directories=[
            pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_EXPORT"],
            pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_IMPORT"],
        ]
    )
    return pe


def exports(pe: pefile.PE) -> list[str]:
    directory = getattr(pe, "DIRECTORY_ENTRY_EXPORT", None)
    return [
        (symbol.name or b"").decode(errors="replace")
        for symbol in (directory.symbols if directory else [])
        if symbol.name
    ]


def imports(pe: pefile.PE) -> list[tuple[str, str]]:
    result: list[tuple[str, str]] = []
    for entry in getattr(pe, "DIRECTORY_ENTRY_IMPORT", []):
        dll = entry.dll.decode(errors="replace")
        for symbol in entry.imports:
            result.append((dll, (symbol.name or b"").decode(errors="replace")))
    return result


def plugin_census(bin_root: Path) -> dict:
    export_shapes: collections.Counter[tuple[str, ...]] = collections.Counter()
    command_common_importers = 0
    command_common_symbols: collections.Counter[str] = collections.Counter()
    parsed = 0
    dlls = sorted(bin_root.glob("*.dll"))
    for path in dlls:
        try:
            pe = parse_pe(path)
        except pefile.PEFormatError:
            continue
        parsed += 1
        shape = tuple(sorted(exports(pe)))
        if shape:
            export_shapes[shape] += 1
        cc = False
        for dll, name in imports(pe):
            if dll.lower() == "commandcommon.dll":
                cc = True
                command_common_symbols[name] += 1
        command_common_importers += int(cc)
    return {
        "dll_count": len(dlls),
        "parsed_pe_count": parsed,
        "execute_only_export_count": export_shapes[("Execute",)],
        "command_common_importer_count": command_common_importers,
        "selected_command_common_import_counts": {
            name: command_common_symbols[name] for name in SELECTED_COMMON_PRIMITIVES
        },
        "top_command_common_imports": [
            {"name": name, "dll_count": count}
            for name, count in command_common_symbols.most_common(20)
        ],
    }


def anchor(path: Path, va: int, expected_hex: str) -> dict:
    pe = pefile.PE(str(path), fast_load=True)
    raw = path.read_bytes()
    offset = pe.get_offset_from_rva(va - pe.OPTIONAL_HEADER.ImageBase)
    expected = bytes.fromhex(expected_hex)
    actual = raw[offset : offset + len(expected)]
    if actual != expected:
        raise ValueError(
            f"{path.name} VA 0x{va:X}: {actual.hex()} != expected {expected_hex}"
        )
    return {"va": f"0x{va:X}", "file_offset": f"0x{offset:X}", "bytes": expected_hex}


def records(section) -> list[bytes]:
    size = section.decoded_record_size
    data = section.decoded_data
    return [data[i * size : (i + 1) * size] for i in range(section.header.record_count)]


def variable_blob(master, index: int, *, namespace_base: int = 0) -> bytes:
    if index == 0:
        return b""
    if namespace_base and index > namespace_base:
        index -= namespace_base
    section = master.sections[0]
    count = section.header.record_count
    if not 1 <= index <= count:
        raise ValueError(f"variable index {index} outside 1..{count}")
    data = section.decoded_data
    table_end = count * 6
    rel, length = struct.unpack_from("<IH", data, (index - 1) * 6)
    start = table_end + rel
    return data[start : start + length]


def resolve_comm_set(parser: DDBParser, master, comm_set_id: int) -> dict:
    matches = [
        row for row in parser.extract_master_comm_sets(master.sections[29])
        if row.comm_set_id == comm_set_id
    ]
    if len(matches) != 1:
        raise ValueError(f"CommSet {comm_set_id}: {len(matches)} rows")
    row = matches[0]
    return {
        "comm_set_id": row.comm_set_id,
        "send_parameter": row.send_parameter,
        "receive_timeout": row.receive_timeout,
        "exception_handler_id": row.exception_handler_id,
        "unknown_word_0c": row.unknown_word_0c,
        "retry_count": row.retry_count,
        "exception_handler_flag": row.exception_handler_flag,
        "raw": row.raw.hex(),
    }


def resolve_timer(parser: DDBParser, master, category_id: int, timer_id: int) -> dict:
    matches = [
        row for row in parser.extract_master_timers(master.sections[25])
        if row.category_id == category_id and row.timer_id == timer_id
    ]
    if len(matches) != 1:
        raise ValueError(f"Timer ({category_id}, {timer_id}): {len(matches)} rows")
    row = matches[0]
    return {
        "category_id": row.category_id,
        "timer_id": row.timer_id,
        "delay_ms": row.delay_ms,
        "unknown_dword_08": row.unknown_dword_08,
        "raw": row.raw.hex(),
    }


def resolve_frame(parser: DDBParser, master, category: int, selector: int, *, variable_namespace_base: int = 0) -> dict:
    frows = [
        raw
        for raw in records(master.sections[18])
        if struct.unpack_from("<HH", raw, 0) == (category, selector)
    ]
    if len(frows) != 1:
        raise ValueError(f"category {category} selector 0x{selector:X}: {len(frows)} rows")
    frow = frows[0]
    comm_set, frame_id = struct.unpack_from("<HH", frow, 4)
    crows = [raw for raw in records(master.sections[17]) if struct.unpack_from("<H", raw, 0)[0] == frame_id]
    if len(crows) != 1:
        raise ValueError(f"frame 0x{frame_id:X}: {len(crows)} rows")
    crow = crows[0]
    send_var, mask_var, check_var = struct.unpack_from("<HHH", crow, 2)
    return {
        "category_id": category,
        "selector": f"0x{selector:X}",
        "func_comm_frame_raw": frow.hex(),
        "comm_set": comm_set,
        "comm_set_metadata": resolve_comm_set(parser, master, comm_set),
        "comm_frame_id": f"0x{frame_id:X}",
        "comm_frame_raw": crow.hex(),
        "variables": {
            "send": {
                "id": f"0x{send_var:X}",
                "normalized_id": f"0x{(send_var - variable_namespace_base) if variable_namespace_base and send_var > variable_namespace_base else send_var:X}",
                "bytes": variable_blob(master, send_var, namespace_base=variable_namespace_base).hex(),
            },
            "receive_mask": {
                "id": f"0x{mask_var:X}",
                "normalized_id": f"0x{(mask_var - variable_namespace_base) if variable_namespace_base and mask_var > variable_namespace_base else mask_var:X}",
                "bytes": variable_blob(master, mask_var, namespace_base=variable_namespace_base).hex(),
            },
            "receive_check": {
                "id": f"0x{check_var:X}",
                "normalized_id": f"0x{(check_var - variable_namespace_base) if variable_namespace_base and check_var > variable_namespace_base else check_var:X}",
                "bytes": variable_blob(master, check_var, namespace_base=variable_namespace_base).hex(),
            },
        },
    }


def dll_binding(parser: DDBParser, master, category: int, role: int) -> dict:
    matches = [
        entry
        for entry in parser.extract_master_dlls(master.sections[19])
        if entry.category_id == category and entry.dll_role_id == role
    ]
    if len(matches) != 1:
        raise ValueError(f"DLL binding ({category}, {role}): {len(matches)} rows")
    entry = matches[0]
    return {
        "category_id": category,
        "dll_role_id": role,
        "dll_role_hex": f"0x{role:X}",
        "dll_name": entry.dll_name,
        "raw": entry.raw.hex(),
    }


def master_examples(techstream_root: Path) -> dict:
    parser = DDBParser()
    path = techstream_root / "NA/DB/Toyota.ddb"
    master = parser.parse_master_db(path)
    return {
        "source": file_identity(path, techstream_root),
        "comm_set_table_record_count": master.sections[29].header.record_count,
        "comm_set_1": resolve_comm_set(parser, master, 1),
        "hybrid_clear": {
            "binding": dll_binding(parser, master, 397, 25),
            "primary": resolve_frame(parser, master, 397, 0x01),
            "fallback": resolve_frame(parser, master, 397, 0x102),
        },
        "brake_current_cid": {
            "binding": dll_binding(parser, master, 435, 82),
            "frame": resolve_frame(parser, master, 435, 0xDC),
        },
    }


def core_binary_model(techstream_root: Path) -> dict:
    bin_root = techstream_root / "bin"
    result = {}
    for name in CORE_V18:
        path = bin_root / name
        pe = parse_pe(path)
        imps = imports(pe)
        result[name] = {
            **file_identity(path, techstream_root),
            "exports_selected": [
                item
                for item in exports(pe)
                if item == "Execute"
                or "CommandExecute" in item
                or "EcuFuncListAPI" in item
                or "GetCommFrmInfo" in item
                or "CommFrameSendReceive" in item
                or "CFuncInfoCache" in item
            ],
            "imports_selected": [
                {"dll": dll, "name": symbol}
                for dll, symbol in imps
                if symbol in ("LoadLibraryA", "GetProcAddress")
                or "CDbDllResRecords" in symbol
                or "CCommCtrlMain::CommandExecute" in symbol
                or "KGP_CommFrameCtrl" in dll
            ],
            "anchors": {
                key: anchor(path, va, expected)
                for key, (va, expected) in ANCHORS.get(name, {}).items()
            },
        }
    return result



def dll_role_catalog(parser: DDBParser, master) -> dict:
    by_role: dict[int, list] = collections.defaultdict(list)
    for entry in parser.extract_master_dlls(master.sections[19]):
        by_role[entry.dll_role_id].append(entry)
    roles = []
    for role, entries in by_role.items():
        names = collections.Counter(entry.dll_name for entry in entries)
        roles.append({
            "role": role,
            "role_hex": f"0x{role:X}",
            "binding_count": len(entries),
            "category_count": len({entry.category_id for entry in entries}),
            "plugin_count": len(names),
            "plugins": [
                {"dll": name, "binding_count": count}
                for name, count in names.most_common()
            ],
        })
    roles.sort(key=lambda row: (-row["binding_count"], row["role"]))
    return {
        "binding_count": sum(row["binding_count"] for row in roles),
        "role_count": len(roles),
        "roles": roles,
    }


def gtsplus_command_common_surface(gts_root: Path) -> dict:
    path = gts_root / "bin/CommandCommon.dll"
    pe = parse_pe(path)
    text = next(section for section in pe.sections if section.Name.rstrip(b"\0") == b".text")
    exported = set(exports(pe))
    helpers = [
        "?CheckSupportPid@CCommCachePlusP5@@QAEKPAUtagCOMMAND_DATA@@GPAHPAVCCmdDataIdList@@H@Z",
        "?CheckSupportDid@CCommCachePlusP5@@QAEKPAUtagCOMMAND_DATA@@GPAHPAVCCmdDataIdList@@H@Z",
        "?CreateEnableDataIdList@CCmdSupportDataIdList@@QAEKPAUtagCOMMAND_DATA@@PAVCCmdDataIdList@@K@Z",
        "?CreateEnableRIdList@CCmdSupportDataIdList@@QAEKPAUtagCOMMAND_DATA@@PAVCCmdDataIdList@@K@Z",
    ]
    return {
        "identity": file_identity(path, gts_root),
        "text_virtual_size": text.Misc_VirtualSize,
        "text_raw_size": text.SizeOfRawData,
        "text_rva": f"0x{text.VirtualAddress:X}",
        "helper_exports_present": {name: name in exported for name in helpers},
        "body_boundary": "current on-disk PE keeps these helper exports in virtual .text beyond the materialized raw .text page; use V18 executable bodies only as API-continuity evidence",
    }


def gtsplus_plugin_semantics(parser: DDBParser, master, gts_root: Path) -> dict:
    """Pin current-GTS plugin control-flow/response semantics for representative roles."""
    bin_root = gts_root / "bin"
    cid = bin_root / "GetCID_SID22_DT.dll"
    clear = bin_root / "DelDiagCodeP4.dll"
    monitor_list = bin_root / "GetDatMonListP5_DT.dll"
    active_test_list = bin_root / "GetActTstListP5_DT.dll"
    signal_info = bin_root / "GetDatMonSignalInfoP5_DT.dll"
    kgp = bin_root / "KgpDataCtrl.dll"
    return {
        "role_0x06_p5_active_test_list": {
            "plugin": file_identity(active_test_list, gts_root),
            "example_binding": dll_binding(parser, master, 397, 0x06),
            "list_model": {
                "purpose": "construct the Active Test catalog from DID-backed direct tests and RID-backed routine tests after runtime support evaluation",
                "category_mode": "low byte of master category generation field (+0x48 raw) masked with 0xE0",
                "direct_test_table": {"table": 68, "class": ECU_TABLE_CLASS_NAMES[68], "record_size": 64},
                "routine_test_table": {"table": 71, "class": ECU_TABLE_CLASS_NAMES[71], "record_size": 72},
                "multi_did_table": {"table": 33, "class": ECU_TABLE_CLASS_NAMES[33], "optional": True},
                "normal_support_builders": ["CreateEnableDataIdList", "CreateEnableRIdList"],
                "subaru_mode_0x20_builders": ["CreateEnableDataIdListForSubaruCheckDID", "CreateEnableRIdListforSUBARU"],
                "direct_support": {
                    "primary_did_key": "type-68 u16 +0x20",
                    "normal_helper": "CCommCachePlusP5::CheckSupportDid(command, did, &supported, enabled_did_list, 1)",
                    "subaru_helper": "CCommCachePlusP5::CheckSupportDidForSUBARU(command, did, &supported)",
                    "multi_did": "when a type-33 MultiDID association exists, its additional DIDs are individually support-checked before the active test is emitted",
                },
                "routine_support": {
                    "rid_key": "type-71 u16 +0x1E",
                    "normal_helper": "CCommCachePlusP5::CheckSupportRid(command, rid, &supported, enabled_rid_list, 1)",
                    "subaru_helper": "CCommCachePlusP5::CheckSupportRidForSUBARU(command, rid, &supported, enabled_rid_list, 1)",
                },
                "runtime_boundary": "offline DDB parsing enumerates direct/routine candidates but cannot determine DID/RID support outcomes without support-cache/live ECU state",
                "output": "supported direct and routine entries are normalized/sorted and emitted as CCmdActTstData (id, name, short name, help id)",
            },
            "anchors": {
                "category_mode_subaru_builders": anchor(active_test_list, 0x100014B4, "8d4dd48b008a404824e03c200f85a20100008b06ff701c8d45b45056ff15045000108bf885ff0f855a0500008d8de8feffffff15a85000108d8d34ffffffc645fc05ff15185000108d8d54ffffffc645fc06ff1534500010a15c500010c645fc07897dec8985c4feffff397e100f8420"),
                "normal_support_builders": anchor(active_test_list, 0x10001668, "6a008d45b45056ff15005000108bf885ff74165768980000006878510010685052001057e9a00300006a008d8514ffffff50568d4dd4ff15085000108bf885ff74165768a0000000687851001068b852001057e9710300008d45b48bcb5056e8c40300008b"),
                "direct_table_68": anchor(active_test_list, 0x10001B33, "ff701c8b35bc5000108d856cffffff5081c1cc0000006844020000ffd68bf881ff070103a0750733ffe9a002000085ff0f85980200006683bd70ffffff010f8c8a0200008d4da0ff15c85000108b038b4b1081c1cc000000c645fc02"),
                "direct_check_support_did": anchor(active_test_list, 0x10001C45, "8b8d7cffffff8d45ec6a01ffb55cffffff500fbfc28b04818d4db80fb7402050ffb560ffffffff15205000108bf885ff"),
                "routine_table_71": anchor(active_test_list, 0x100016D6, "8d8de8feffffff15a85000108d8d54ffffffc645fc08ff15345000108b4e108b155c500010c645fc09897dec8995c4feffff85c90f84c40000008b0685c00f84ba000000ff701c8d85e8feffff81c1cc00000050a1bc5000106847020000ffd08bf881ff070103"),
                "routine_check_support_rid": anchor(active_test_list, 0x10001770, "6a018d8514ffffff0fbfce508d45ecc745ec00000000508b85f8feffff8b04888d8d54ffffff0fb7401e50ffb5c8feffffff15305000108bf885ff7546"),
                "subaru_check_support_did": anchor(active_test_list, 0x10001FF8, "0fb7402050ffb560ffffffff15245000108bf885ff0f8509010000837dec010f"),
                "subaru_check_support_rid": anchor(active_test_list, 0x100015A0, "6a018d8534ffffff0fbfce508d45ecc745ec00000000508b85f8feffff8b04888d8d54ffffff0fb7401e50ffb5c8feffffff15285000108bf8"),
                "final_output": anchor(active_test_list, 0x10001948, "508bcbe8800800008bf0668b0e66894d8c8d4e04518d4d90ff153c5000108d4e14518d4da0ff153c5000108b46248b8db4feffff8945b08d458450ff1550500010"),
            },
        },
        "role_0x05_p5_monitor_list": {
            "plugin": file_identity(monitor_list, gts_root),
            "example_binding": dll_binding(parser, master, 405, 0x05),
            "list_model": {
                "purpose": "construct the Data Monitor list from current P5 DDB candidates plus runtime support state",
                "category_mode": "low byte of master category generation field (+0x48 raw) masked with 0xE0",
                "monitor_table_selection": {
                    "0x60": {"table": 157, "class": ECU_TABLE_CLASS_NAMES[157]},
                    "otherwise": {"table": 62, "class": ECU_TABLE_CLASS_NAMES[62]},
                },
                "support_list_builder": {
                    "0x20": "CreateEnableDataIdListForSubaruCheckDID",
                    "otherwise": "CreateEnableDataIdList",
                },
                "candidate_id": "current 80-byte monitor record u16 +0x34",
                "candidate_flag": "current 80-byte monitor record byte +0x30",
                "candidate_decision": {
                    "flag_bit4_clear": "call CCommCachePlusP5::CheckSupportPid(command, candidate_id, &supported, enable_data_id_list, 1); include only when call succeeds and supported == 1",
                    "flag_bit4_set_bit0_set": "include directly without CheckSupportPid",
                    "flag_bit4_set_bit0_clear": "exclude directly without CheckSupportPid",
                },
                "runtime_boundary": "offline DB parsing can enumerate and partition candidates, but cannot know CheckSupportPid outcomes without support-cache/live ECU state",
                "post_filter": "MultiPID validation/merge followed by CCmdDatMonData construction; final conversion path joins physical/unit metadata and ChangeSignalLSB",
            },
            "anchors": {
                "category_mode_support_builder": anchor(monitor_list, 0x10001BD4, "8a404824e08885ebfeffff3c208d8554ffffff752e565053ff15185000108bf885ff744e5768de00000068c0510010689053001057ff157850001083c414e9870200006a005053ff151c5000108bf885ff741f5768"),
                "monitor_table_selection": anchor(monitor_list, 0x10001C77, "80bdebfeffff6050a1f4500010755c689d020000ffd08bf885ff7420575668f400000068c0510010688054001057ff157850001083c418e9df010000668b850cffffff6683f8017d7e5668f900000068c051001068205500106a00ff157850001083c41433ffe9b0010000683e020000ffd08b"),
                "candidate_fields": anchor(monitor_list, 0x10001D66, "8b04b10fb74034668945948b04b18b40308945988b04b10fb7403a6689459c8b04b18b40248945a08b04b1f20f1000f20f1145a48b04b1f20f104008f20f1145ac8b04b18b40148945b48b04b18b40188945b88b04b18b402c8945bc8b04b18d8d08ffffff8b40288945c0ff15f0500010508d4dc4ff15605000108a45988975e4a81074"),
                "flag_and_support_probe": anchor(monitor_list, 0x10001DE1, "8a45988975e4a810740ca80174598bb5e0feffffeb3b6a018d8554ffffffc745ec00000000508d45ec50ff75948d8d24ffffffffb5dcfeffffff150c5000108bf885ff7556837dec01751c8bb5d8fe"),
                "final_conversion_output": anchor(monitor_list, 0x10002B82, "668b483e662b483c66410fb7c18d8d64ffffff518d8d54ffffff518d8d50ffffff51ffb558ffffff8d8d94feffffffb528feffff50ffb55cffffffff7584ff15385000108bf085f60f85230100008b852cfeffff8b48048d8504ffffff508d4920ff156c5000108d8d"),
            },
        },
        "role_0x41_p5_signal_info": {
            "plugin": file_identity(signal_info, gts_root),
            "example_binding": dll_binding(parser, master, 405, 0x41),
            "metadata_model": {
                "transport": "none in this plugin; constructs CCmdDatMonSignalInfo metadata from DDB records",
                "monitor_tables": [62, 157],
                "physical_data_table": 13,
                "unit_table": 15,
                "pattern_display_table": 14,
                "conversion_fields": {
                    "mul": "CDbPhyData +0x00 -> CCmdDatMonSignalInfo +0x60",
                    "div": "CDbPhyData +0x04 -> +0x64",
                    "offset": "CDbPhyData +0x08 -> +0x68",
                    "signed": "CDbPhyData +0x14 -> +0x6E",
                    "decimal_point_count": "CDbPhyData +0x15 -> +0x45",
                    "unit_key": "CDbPhyData +0x0E -> CDbUnit lookup",
                    "unit_text": "CDbUnit::GetDefaultUnitStr -> CCmdString at +0x34",
                    "unit_genre_id": "CDbUnit +0x06 -> +0x6C",
                    "bit_width": "monitor bit_end(+0x3E) - bit_start(+0x3C) + 1 -> +0x70 (current 80-byte monitor geometry)",
                    "pattern_display": "monitor +0x42 key -> CDbPatDisp; value/string pairs -> display-info list at +0x74",
                },
                "cli_join": "tools/gts did enriches current monitor rows with signal_info from these exact tables",
            },
            "anchors": {
                "physical_key_lookup": anchor(signal_info, 0x10001142, "0fb7403a50ff75188d45b050680d020000ff1584400010"),
                "unit_key_lookup": anchor(signal_info, 0x10001192, "8b45c08b8d74ffffff8b04018b8d7cffffff0fb7400e50ff75188d458050680f020000ff15844000108b"),
                "conversion_copies": anchor(signal_info, 0x1000120F, "8b9574ffffff2bfe8b4dc0478b040a0fb640158843458b45908b0402668b40066689436c8b040a8b008943608b040a8b40048943648b040a8b40088943688b040a8b8d70ffffff0fb6401488436e66897b70"),
                "pattern_key_lookup": anchor(signal_info, 0x100012B0, "0fb74042898578ffffff0fb7c050ff75188d459850680e020000ff15844000108b"),
                "pattern_output": anchor(signal_info, 0x10001310, "8b8d78ffffff0fb7c18d4d988945cc8b45a8568b04b08b008945e0ff1598400010508d4dd0ff15304000108b45a88d4b748b04b08b40048945e48d45c450ff1524"),
            },
        },
        "role_0x52_generic_cid": {
            "plugin": file_identity(cid, gts_root),
            "example_binding": dll_binding(parser, master, 405, 0x52),
            "example_frame": resolve_frame(parser, master, 405, 0xDC, variable_namespace_base=0x2710),
            "response_model": {
                "positive_prefix": "62f181",
                "echoed_did_receive_indexes": [1, 2],
                "payload_offset": 4,
                "record_size": 16,
                "record_count_source": "received_length_minus_4, chunked until exhausted; receive byte 3 is skipped, not used as count",
                "string_conversion": "Windows MultiByteToWideChar code page 0 (CP_ACP) from zero-terminated <=16-byte chunk",
                "value_capacity_chars": 17,
                "entry_name_prefix": "CID",
                "entry_name_format": "%s%d",
                "entry_numbering": "1-based",
                "output_list_offset": "command output object +0x20",
            },
            "anchors": {
                "selector_dc_lookup": anchor(cid, 0x10001527, "68dc0000008d8d68fcffffff15184000"),
                "response_count_minus_4": anchor(cid, 0x100015C0, "ffd38b406883e804898564fcffff"),
                "did_echo_index_1": anchor(cid, 0x10001618, "6a018d7858ffd66a018bcf8a5808ffd63a58"),
                "did_echo_index_2": anchor(cid, 0x1000164E, "8b3d3c4000106a028d4858ffd76a028bce8a5808ffd73858"),
                "payload_copy_from_4": anchor(cid, 0x10001680, "6a008d8de8fcffffffd78d48588d460450ffd3508d8dc0fcffffff153840"),
                "chunk_size_16": anchor(cid, 0x100016DC, "8b8564fcffffbe100000003bf87d1d578d8dc0fc"),
                "zero_terminated_buffer": anchor(cid, 0x10001713, "8d85fcfeffff68ff0000005650e8751e000083c40c85"),
                "convert_and_set_value": anchor(cid, 0x1000174C, "6a018d8d98fcffffff15284000108d855cfbffff898558fbffff8d8d58fbffff6a008d85fcfeffff50e8b6fbffff6a11ffb558fbffff8d8da0fcffffff1524400010"),
                "cid_literal": anchor(cid, 0x10004270, "4300490044000000"),
                "cid_format_literal": anchor(cid, 0x10004278, "25007300250064000000"),
            },
        },
        "role_0x19_dtc_clear": {
            "plugin": file_identity(clear, gts_root),
            "example_binding": dll_binding(parser, master, 397, 0x19),
            "primary": resolve_frame(parser, master, 397, 0x01, variable_namespace_base=0x2710),
            "fallback": resolve_frame(parser, master, 397, 0x102, variable_namespace_base=0x2710),
            "timer": {
                "db_record_class": "0x119",
                "master_table_type": 25,
                "table": MASTER_TABLE_CLASS_NAMES[25],
                "record_size": master.sections[25].decoded_record_size,
                "record_count": master.sections[25].header.record_count,
                "lookup_key": [397, 1],
                "hybrid_timer_1": resolve_timer(parser, master, 397, 1),
            },
            "control_flow": {
                "primary_selector": "0x1",
                "primary_addressing": "normal GetCommFrmSndRcv unless ECU detail flag == 1, then DifferentAddress",
                "special_bus_ids": [0x12, 0x22, 0x18, 0x78],
                "fallback_selector": "0x102",
                "fallback_error_codes_when_function_gate_set": [
                    "0x91010009", "0x90020321", "0x90020323", "0xA0040201", "0xC0040001",
                    "0xA0040202", "0x90020327", "0x91020320", "0x91020310", "0x91020322",
                ],
                "fallback_when_function_gate_clear": "only 0x91010009 (logged as first-message TIMEOUT)",
                "fallback_addressing": "FunctionAddress only when bus ID == 0x22; otherwise normal GetCommFrmSndRcv",
                "fallback_c0040101_behavior": "restore/return primary error; in timeout-only branch restore 0x91010009",
                "success": "return 0; Sleep(timer delay_ms); set command output +0x20 m_bDelDiagCode=1",
            },
            "anchors": {
                "timer_class_0x119_key_1": anchor(clear, 0x100010E3, "81c1cc0000006a0156506819010000ff1580300010"),
                "special_bus_ids": anchor(clear, 0x10001156, "b9120000008d50228b45f0663bc87419663bd07414b918000000663bc8740ab978000000663bc875718bb564ff"),
                "primary_addressing": anchor(clear, 0x100011F3, "83f8018d4dc08d45ac50576a017508ff152c300010eb06ff1500300010837d"),
                "fallback_error_set": anchor(clear, 0x1000121C, "81fe09000191744c81fe21030290744481fe23030290743c81fe010204a0743481fe010004c0742c81fe020204a0742481fe27030290741c81fe20030291741481fe10030291740c81fe220302910f85"),
                "fallback_selector_0x102": anchor(clear, 0x1000129A, "b822000000663b45f08d45d45057680201000075188d8d7cffffffff1530300010684832001068ea000000eb14a1003000108d4dc0ffd0688c"),
                "fallback_restore_primary": anchor(clear, 0x100012ED, "81fe010104c075228b8564ffffff8bf068bc32001068fb000000681031001068b831001050ffd383c4148b3d1c300010"),
                "timeout_fallback_0x102": anchor(clear, 0x10001327, "81fe09000191757ba1183000108d4dd4ffd068e83200106809010000681031001068b831001056ffd383c4148d45d48d4dc050a100300010576802010000ffd0688c3200106812"),
                "success_sleep_and_flag": anchor(clear, 0x100013B0, "85f675348b8578ffffff8b00ff30ff15543000108b8560ffffff6a01682d0100006810310010682433001056c7402001000000ffd383c4"),
                "timer_record_pointer": anchor(kgp, 0x100CFE87, "8b45fc8b4dfc8b510c8950108be55d"),
                "timer_key_1": anchor(kgp, 0x100D0100, "0fb742048945ec837df400752c8b4dec3b4de87522c745f4010000"),
                "timer_key_pair": anchor(kgp, 0x100D0380, "6b4d100c034dec894dfc8b55fc0fb742048b4d148b55f88b0c8a0fb751043bc275488b45fc0fb748068b55148b45f88b14900fb742063bc87509b80100"),
            },
        },
    }


def gtsplus_role_layout(gts_root: Path) -> dict:
    parser = DDBParser()
    master_path = gts_root / "NA/DB/Gen/Toyota.ddb"
    master = parser.parse_master_db(master_path)
    kgp = gts_root / "bin/KgpDataCtrl.dll"
    return {
        "source": file_identity(master_path, gts_root),
        "kgp_identity": file_identity(kgp, gts_root),
        "role_layout": {
            "logical_key": "DLL role",
            "v18": "u8 +0x56 (CDbDllTable::FindDbItem1)",
            "gtsplus": "u16 +0x54 (CDbDllTable::FindDbItem1)",
            "gtsplus_role_anchor": anchor(kgp, 0x100AB310, "0fb742548945ec837df40075"),
            "gtsplus_category_anchor": anchor(kgp, 0x100AB420, "0fb742508945ec837df40075"),
        },
        "variable_layout": {
            "logical_model": "same 1-based 6-byte [u32 relative offset][u16 length] table as V18 after namespace normalization",
            "gtsplus_namespace_base": "0x2710",
            "rule": "when the base variable table is selected and variable_id > 0x2710, subtract 0x2710 before lookup",
            "compare_anchor": anchor(kgp, 0x100651F4, "0fb74d0881f9102700007e0e0fb75508"),
            "subtract_anchor": anchor(kgp, 0x10065200, "0fb7550881ea10270000668955088b45"),
        },
        "command_common_surface": gtsplus_command_common_surface(gts_root),
        "timer_table": {
            "master_table_type": 25,
            "class_name": MASTER_TABLE_CLASS_NAMES[25],
            "record_size": master.sections[25].decoded_record_size,
            "record_count": master.sections[25].header.record_count,
        },
        "comm_set_table": {
            "master_table_type": 29,
            "class_name": MASTER_TABLE_CLASS_NAMES[29],
            "record_size": master.sections[29].decoded_record_size,
            "record_count": master.sections[29].header.record_count,
            "comm_set_1": resolve_comm_set(parser, master, 1),
        },
        "role_catalog": role_operation_catalog(parser, master, gts_root / "bin"),
        "plugin_semantics": gtsplus_plugin_semantics(parser, master, gts_root),
        "hybrid_clear_binding": dll_binding(parser, master, 397, 25),
        "hybrid_clear_primary": resolve_frame(parser, master, 397, 0x01, variable_namespace_base=0x2710),
        "hybrid_clear_fallback": resolve_frame(parser, master, 397, 0x102, variable_namespace_base=0x2710),
    }

def build(techstream_root: Path, gts_root: Path | None) -> dict:
    v18_bin = techstream_root / "bin"
    if not (v18_bin / "CommandCommon.dll").is_file():
        raise FileNotFoundError(f"not a Techstream root: {techstream_root}")
    gts = None
    if gts_root is not None:
        gts_bin = gts_root / "bin"
        if not (gts_bin / "CommandCommon.dll").is_file():
            raise FileNotFoundError(f"not a GTS+ root: {gts_root}")
        gts = {
            "plugin_census": plugin_census(gts_bin),
            "dll_role_schema": gtsplus_role_layout(gts_root),
            "core_identities": {
                name: file_identity(gts_bin / name, gts_root)
                for name in ("DiagCommCtrlMain.dll", "CommandCommon.dll", "KgpDataCtrl.dll", "GetEcuFuncList.dll")
            },
        }

    return {
        "schema": "techstream-diagnostic-execution-model-v1",
        "interpretation": (
            "Techstream's ordinary diagnostic command layer is a database-driven execution engine: "
            "the controller resolves an ECU/category plus DLL-role through CDbDllTable, dynamically "
            "loads a one-export Execute plugin, and the plugin selects master FuncCommFrame selectors. "
            "Shared CommandCommon code materializes CommSet/CommFrame send-mask-check bytes and sends "
            "them through KGP_CommFrameCtrl. Plugins remain necessary for control flow and specialized "
            "response handling, but the wire contracts are predominantly database material."
        ),
        "v18": {
            "plugin_census": plugin_census(v18_bin),
            "core_binaries": core_binary_model(techstream_root),
            "db_record_classes": {
                "0x113": {"result": "CDbDllResRecords", "master_table_type": 19, "table": MASTER_TABLE_CLASS_NAMES[19], "role": "(ECU/category, DLL role) -> plugin filename"},
                "0x11A": {"result": "CDbEcuFuncInfoResRecords", "master_table_type": 26, "table": MASTER_TABLE_CLASS_NAMES[26], "role": "ECU function-list discovery"},
                "0x11B": {"result": "CDbEcuFuncDetailsResRecords", "master_table_type": 27, "table": MASTER_TABLE_CLASS_NAMES[27], "role": "function detail discovery"},
                "0x119": {"result": "CDbTimerResRecords", "master_table_type": 25, "table": MASTER_TABLE_CLASS_NAMES[25], "role": "per-category command timer metadata"},
                "0x112": {"result": "CDbFuncCommFrameResRecords", "master_table_type": 18, "table": MASTER_TABLE_CLASS_NAMES[18], "role": "(ECU/category, selector) -> CommSet + CommFrame"},
                "0x111": {"result": "CDbCommFrameResRecords", "master_table_type": 17, "table": MASTER_TABLE_CLASS_NAMES[17], "role": "CommFrame -> send / receive-mask / receive-check variable references"},
                "0x11D": {"result": "CDbComSetResRecords", "master_table_type": 29, "table": MASTER_TABLE_CLASS_NAMES[29], "role": "communication-set / diagnostic transport metadata"},
            },
            "comm_set_table": {
                "master_table_type": 29,
                "class_name": MASTER_TABLE_CLASS_NAMES[29],
                "record_size": 16,
                "record_count": master_examples(techstream_root)["comm_set_table_record_count"],
                "comm_set_1": master_examples(techstream_root)["comm_set_1"],
                "field_semantics": {
                    "+0x00": "send_parameter; copied to SendInt argument 4; common CAN SendProc does not consume it",
                    "+0x04": "receive_timeout input; passed by pointer through CheckAndConvertRcvTimeOut before Receive",
                    "+0x08": "exception-handler ID (CDbComSetTable::GetExceptahandId)",
                    "+0x0A": "CommSet lookup key (CDbComSetTable::FindDbItem1)",
                    "+0x0C": "unresolved u16",
                    "+0x0E": "retry bound consumed by CommFrameSendReceive",
                    "+0x0F": "exception-handler flag (CDbComSetTable::GetExceptahandFlag)",
                },
            },
            "function_discovery": {
                "plugin": "GetEcuFuncList.dll",
                "entry_export": "Execute",
                "cache": "CFuncInfoCache / CShareData slot 0x0B",
                "cache_miss": "CDbEcuFuncInfoResRecords (0x11A) + CDbEcuFuncDetailsResRecords (0x11B), support-gated by CCmdCheckSupport, then SetFuncList",
            },
            "execution_spine": [
                "Techstream UI -> CommandAPI typed request/response objects",
                "CommandAPI -> DiagCommCtrlMain::CCommCtrlMain::CommandExecute",
                "DB 0x113 / CDbDllTable: (ECU/category, DLL-role) -> DLL filename",
                "LoadLibraryA/GetProcAddress(\"Execute\") -> one-export command plugin",
                "plugin chooses one or more FuncCommFrame selector IDs and control-flow/fallback policy",
                "DB 0x112 / CDbFuncCommFrameTable: (ECU/category, selector) -> CommSet + CommFrame",
                "DB 0x111 / CDbCommFrameTable + CDbVariableTable: CommFrame -> send/mask/check bytes",
                "DB 0x11D / CDbComSetTable: communication-set transport metadata",
                "CCommCachePlus::CommFrameSendReceive -> KGP_CommFrameCtrl::SendInt* / Receive*",
            ],
            "representative_routes": master_examples(techstream_root),
        },
        "gtsplus_continuity": gts,
        "boundary": (
            "This recovers the common diagnostic execution architecture, not a claim that every plugin "
            "is declarative or that all Toyota diagnostics can be implemented without plugin semantics. "
            "Specialized parsing, retries, session changes, security, and state machines remain executable behavior."
        ),
    }


def resolve_techstream_root(value: Path) -> Path:
    value = value.expanduser()
    for candidate in (value, value / "Techstream"):
        if (candidate / "bin/CommandCommon.dll").is_file() and (candidate / "NA/DB/Toyota.ddb").is_file():
            return candidate.resolve()
    return value.resolve()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--techstream-root",
        type=Path,
        default=Path(os.environ.get("TECHSTREAM_UNPACKED_ROOT", REPO / "software/Techstream/v18/unpacked/toyota/Toyota Diagnostics/Techstream")),
    )
    ap.add_argument("--gts-root", type=Path, default=Path(os.environ["GTSPLUS_ROOT"]) if "GTSPLUS_ROOT" in os.environ else None)
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = ap.parse_args()
    techstream_root = resolve_techstream_root(args.techstream_root)
    gts_root = resolve_gts_root(args.gts_root) if args.gts_root else None
    result = build(techstream_root, gts_root)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
