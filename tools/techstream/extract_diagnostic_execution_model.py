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
from parse_ddb import MASTER_TABLE_CLASS_NAMES, DDBParser
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
        "comm_set_table": {
            "master_table_type": 29,
            "class_name": MASTER_TABLE_CLASS_NAMES[29],
            "record_size": master.sections[29].decoded_record_size,
            "record_count": master.sections[29].header.record_count,
            "comm_set_1": resolve_comm_set(parser, master, 1),
        },
        "role_catalog": role_operation_catalog(parser, master, gts_root / "bin"),
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
