#!/usr/bin/env python3
"""Extract instruction-pinned, offline current-release P6 per-DTC FFD evidence.

This is a research evidence generator, not a portable response decoder. Native
function intervals retain the bytes underlying the derived grammar; regional
DDB witnesses retain the exact rows behind each join and request template.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import struct
from collections import Counter
from pathlib import Path
from typing import Any

from tools import REPO_ROOT
from tools.techstream.ddb_semantics import extract_monitor_records, records
from tools.techstream.extract_gtsplus_tss3_native_recorder import (
    export_body, exports, operation_anchor, pe_info, read_va,
)
from tools.techstream.gts.master import _master_variable
from tools.techstream.extract_gtsplus_p6_data_list import native_frame_witness, native_source_census
from tools.techstream.parse_ddb import DDBParser
from tools.techstream.techstream_paths import resolve_gts_root
from tools.techstream.recover_all_gtsplus_bodies import DEFAULT_OUTPUT, qualify_recovered_source

DEFAULT_OUT = REPO_ROOT / "data/generated/gtsplus_2026/p6_freeze_frame_semantics.json"
DEFAULT_RECOVERED = DEFAULT_OUTPUT / "GTSPlus"
PLUGIN = "GetEachFrzFrmDatP6_DT.dll"
IDENTITIES = {
    PLUGIN: "c2eded32d5569552062c79a7d8d38f2626ec0347d32ffc27fe09559004cec658",
    "CommandCommon.dll": "98e313d197eb7115d037a2d46e71343b4b44862356e9d772c8f2f03d96e638d3",
    "GetEachFrzFrmDatP5_DT.dll": "41bdb268af943c6b00cf8b901a48cc162d4b0eaedfb589ba4e3b8e937622cb99",
}
PLUGIN_FUNCTIONS = {
    "selected_dtc_orchestration": (0x10001160, 0x100017C0),
    "confirmed_parser": (0x10001B40, 0x10002270),
    "confirmed_request": (0x10002270, 0x10002600),
    "predictive_parser": (0x100028D0, 0x10003000),
    "predictive_request": (0x10003000, 0x10003390),
    "additional_info_parser": (0x100035D0, 0x10003A90),
    "additional_info_request": (0x10003A90, 0x10003DE0),
}
P5_FUNCTIONS = {
    "ordinary_parser": (0x10001190, 0x10001A30),
    "all_records_first_request": (0x10001A30, 0x10001E60),
    "individual_record_fallback": (0x10001E90, 0x10002260),
}
COMMON_FUNCTIONS = (
    "AnalyzeSingleDataId", "CheckSupportBit", "CheckSupportPid", "GetFFDType",
    "GetPidIdFromSSRDataId", "InitFrzFrmDat", "SelectGetDIDLength",
    "SetDTCToSndFrame", "SetDTCToSndFrameSSRNo", "SetFrzFrmDat", "SetSignalInfo",
    "SetTimeStampOdoPidId", "SortMultiDataOrderByTimeStamp",
)
# These exact instruction anchors were checked in Ghidra disassembly after
# decompiling the containing functions. Addresses refer to the pinned images.
PLUGIN_ANCHORS = {
    "header_and_single_snapshot": (0x10001E0F, "83ff08", 0x10001E18, "6a06", 0x10001E25, "6a00", 0x10001E50, "6a07", 0x10001E5A, "be08000000"),
    "zero_count_unbounded_by_count": (0x10001E71, "3bc17c0885c90f85b6010000"),
    "inline_length_modes": (0x10001F03, "8a45ef3c01752c", 0x10001F36, "3c027549"),
    "truncated_payload_break": (0x10001F98, "0fb7c14803c63b85f4feffff0f8d89000000"),
    "confirmed_selector": (0x100022D5, "68cf000000"),
    "predictive_selector": (0x10003065, "68d0000000"),
    "prune_result_codes": (
        0x10002453, "81fe09000191", 0x1000245F, "81fe21030290",
        0x1000246B, "81fe23030290", 0x10002477, "81fe010204a0",
        0x1000247F, "81fe010004c0", 0x10002487, "81fe020204a0",
        0x1000248F, "81fe27030290", 0x10002497, "81fe20030291",
        0x1000249F, "81fe10030291", 0x100024A7, "81fe22030291"),
}
COMMON_ANCHORS = {
    "fixed_or_inline_length": (0x100A0107, "0fb778046685ff750e", 0x100A0110, "b800900000663945081adb80c302"),
    "ffd_membership_and_bit_geometry": (0x1009F3EE, "f6403002", 0x1009F3F8, "0fb7483c0fb7403e", 0x1009F41F, "663955180f8296000000"),
    "support_modes": (0x1009F853, "0fb6400683e800746383e801743283e8017459"),
    "mode_one_preceding_byte": (0x1009F893, "8bf2ba80000000c1ee03", 0x1009F8AB, "8a4406ff22c23ac2"),
    "ffd_condition_table": (0x1009F8CA, "6683783800", 0x1009F8EE, "6850020000"),
    "alternate_did_to_monitor_key": (0x1009FB46, "6639484875120fb74034"),
    "condition_did_and_type": (0x1009F5CB, "0fb6160fafd00fb646016603d0", 0x1009F602, "807b0607"),
    "p6_lsb_gate": (0x100142C3, "8a4160241f3c167406"),
    "additional_info_table": (0x100A3C03, "0fb686a8000000", 0x100A3C18, "68ab020000"),
    "additional_info_condition_remap": (0x100A380A, "8d0445fca10d10", 0x100A3831, "0fb75514"),
    "snapshot_type_ranges": (
        0x1009FA27, "3c01", 0x1009FA36, "2c203c0f",
        0x1009FA47, "3ca1", 0x1009FA56, "0450ba100200003c0f"),
    "selected_nonzero_record": (
        0x100A0324, "817d08ffffff00", 0x100A0335, "84db7429",
        0x100A0340, "6a05", 0x100A0352, "885808"),
}
PRUNED_RESULTS = (
    0x91010009, 0x90020321, 0x90020323, 0xA0040201, 0xC0040001,
    0xA0040202, 0x90020327, 0x91020320, 0x91020310, 0x91020322,
)


def u16(raw: bytes, offset: int) -> int:
    return struct.unpack_from("<H", raw, offset)[0]


def source(path: Path, root: Path) -> dict[str, Any]:
    data = path.read_bytes()
    return {"path": path.relative_to(root).as_posix(), "size": len(data),
            "sha256": hashlib.sha256(data).hexdigest()}


def intern_evidence(pool: dict[str, Any], value: dict[str, Any]) -> str:
    canonical = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    key = "sha256:" + hashlib.sha256(canonical).hexdigest()
    pool.setdefault(key, value)
    return key


def frame_references(frames: dict[str, dict[str, Any]],
                     pool: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        selector: {**program, "frames": [
            {"frame_ref": intern_evidence(pool, frame)}
            for frame in program["frames"]]}
        for selector, program in frames.items()
    }


def interval(pe: Any, data: bytes, base: int, start: int, end: int) -> dict[str, Any]:
    body = read_va(pe, data, base, start, end - start)
    if len(body) != end - start:
        raise ValueError(f"truncated native function interval at {start:#x}")
    return {"va": f"0x{start:08X}", "rva": f"0x{start - base:X}",
            "end_va": f"0x{end:08X}", "size": len(body),
            "sha256": hashlib.sha256(body).hexdigest(), "bytes": body.hex()}


def native(gts: Path, recovered: Path) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for name, path, root in (
        (PLUGIN, gts / "bin" / PLUGIN, gts),
        ("CommandCommon.dll", recovered / "bin/CommandCommon.dll", recovered),
        ("GetEachFrzFrmDatP5_DT.dll", gts / "bin/GetEachFrzFrmDatP5_DT.dll", gts),
    ):
        qualification = (
            qualify_recovered_source(path, gts / "bin" / name, component_root=recovered)
            if name == "CommandCommon.dll" else None
        )
        ident = source(path, root)
        if ident["sha256"] != IDENTITIES[name]:
            raise ValueError(f"{name}: unsupported release SHA-256 {ident['sha256']}")
        pe, data, base = pe_info(path)
        functions = {}
        if name == PLUGIN:
            for role, (start, end) in PLUGIN_FUNCTIONS.items():
                functions[role] = interval(pe, data, base, start, end)
            anchors = PLUGIN_ANCHORS
        elif name == "GetEachFrzFrmDatP5_DT.dll":
            for role, (start, end) in P5_FUNCTIONS.items():
                functions[role] = interval(pe, data, base, start, end)
            anchors = {"inline_u8_length": (0x100015D3, "8d4703", 0x10001626, "8a580884db")}
        else:
            exps = exports(pe, base)
            for role in COMMON_FUNCTIONS:
                matches = [key for key in exps if key.startswith(f"?{role}@CGetFrzFrmDatP6Base@@")]
                if len(matches) != 1:
                    raise ValueError(f"ambiguous P6 export {role}: {matches}")
                key = matches[0]
                pin = export_body(pe, data, base, exps, key)
                functions[role] = {"export": key, "boundary": "export to next exported address (includes alignment)",
                                   **interval(pe, data, base, int(pin["va"], 16), int(pin["end_va"], 16))}
            for role in ("AnalyzeSingleDataId", "CheckSupportBit", "CheckSupportPid",
                         "GetPidIdFromPreAddInfo", "SetFrzFrmDat", "SetTimeStampPidIdforPreAddInfo"):
                key = next(key for key in exps if key.startswith(f"?{role}@CGetFrzFrmDatPreAddInfo@@"))
                pin = export_body(pe, data, base, exps, key)
                functions[f"additional_info_{role}"] = {"export": key,
                    "boundary": "export to next exported address (includes alignment)",
                    **interval(pe, data, base, int(pin["va"], 16), int(pin["end_va"], 16))}
            functions["extract_msb0_u32"] = interval(pe, data, base, 0x100BFF7C, 0x100C003C)
            for role, start, end in (
                ("p6_lsb_metadata_wrapper", 0x100142C0, 0x10014300),
                ("p6_lsb_metadata_conversion", 0x10014930, 0x10014B50),
                ("p6_lsb_init", 0x10014B50, 0x10014C00),
            ):
                functions[role] = interval(pe, data, base, start, end)
            map_name = "?m_lstDIDMap@CGetFrzFrmDatPreAddInfo@@2QAY112$$CBGA"
            map_va = exps[map_name]
            functions["additional_info_did_map"] = {"export": map_name, **interval(pe, data, base, map_va, map_va + 36)}
            anchors = COMMON_ANCHORS
        out[name] = {"source": ident, "image_base": f"0x{base:08X}",
                     "functions": functions,
                     "instruction_anchors": {key: operation_anchor(pe, data, base, spec) for key, spec in anchors.items()}}
        if qualification is not None:
            out[name]["qualification"] = qualification
    return out


def raw_rows(db: Any, table: int) -> list[bytes]:
    return list(records(db.sections[table])) if table in db.sections else []


def condition_witness(db: Any, master: Any, key: int) -> list[dict[str, Any]]:
    out = []
    for index, raw in enumerate(raw_rows(db, 80)):
        if u16(raw, 0) != key:
            continue
        variable = _master_variable(master, u16(raw, 2))
        payload = bytes.fromhex(variable["bytes"])
        out.append({"table": 80, "index": index, "raw": raw.hex(), "key": key,
                    "variable": variable, "referenced_did": int.from_bytes(payload[:2], "big") if len(payload) >= 2 else None,
                    "bit_start": u16(raw, 6), "bit_end": u16(raw, 8), "condition_type": raw[11]})
    return out


def monitor_witness(db: Any, strings: Any, master: Any, row: Any,
                    did_rows: dict[int, tuple[int, bytes]]) -> dict[str, Any]:
    found = did_rows.get(row.alternate_did)
    did = None if found is None else found[1]
    fixed = 0 if did is None else u16(did, 4)
    physical = next((r for r in raw_rows(db, 13) if u16(r, 12) == row.physical_data_key), None)
    unit = None if physical is None else next((r for r in raw_rows(db, 15) if u16(r, 4) == u16(physical, 14)), None)
    patterns = [r for r in raw_rows(db, 14) if row.pattern_display_key and u16(r, 12) == row.pattern_display_key]
    return {
        "table": 62, "index": row.index, "raw": row.raw.hex(),
        "name": None if strings is None else strings.get_string(row.name_string_index), "name_string_index": row.name_string_index,
        "monitor_key": row.monitor_key,
        "flags": row.flags, "ffd_member": bool(row.flags & 2),
        "primary_did": row.primary_did, "snapshot_did": row.alternate_did,
        "bit_start": row.bit_start, "bit_end": row.bit_end,
        "presentation_mode_4b": row.raw[0x4B], "byte_4a": row.raw[0x4A],
        "did_row": None if did is None else {"table": 61, "index": found[0], "raw": did.hex(),
                                                "did": u16(did, 2), "fixed_length": fixed, "support_mode": did[6]},
        "length_geometry": "ddb_fixed" if fixed else "inline_be16" if row.alternate_did >= 0x9000 else "inline_u8",
        "minimum_signal_payload_length": (row.bit_end >> 3) + 1,
        "ffd_condition_key": row.ffd_support_condition_key,
        "conditions": condition_witness(db, master, row.ffd_support_condition_key) if row.ffd_support_condition_key else [],
        "physical": None if physical is None else {"table": 13, "raw": physical.hex(),
             "key": row.physical_data_key, "mul": struct.unpack_from("<i", physical, 0)[0],
             "div": struct.unpack_from("<i", physical, 4)[0], "offset": struct.unpack_from("<i", physical, 8)[0],
             "signed": physical[20], "decimal_places": physical[21]},
        "unit": None if unit is None else {"table": 15, "raw": unit.hex(),
            "string_index": struct.unpack_from("<I", unit)[0],
            "text": None if strings is None else strings.get_string(struct.unpack_from("<I", unit)[0])},
        "patterns": [{"table": 14, "raw": r.hex(), "value": struct.unpack_from("<I", r, 4)[0],
                      "string_index": struct.unpack_from("<I", r)[0],
                      "text": None if strings is None else strings.get_string(struct.unpack_from("<I", r)[0])} for r in patterns],
    }


def region_evidence(gts: Path, region: str, evidence: dict[str, dict[str, Any]]) -> dict[str, Any]:
    parser = DDBParser()
    context, sources_raw, selection = native_source_census(parser, gts, region, 0xB5, PLUGIN)
    monitor_pool = evidence["monitors"]
    census = Counter()
    category_rows = []
    targets = []
    additional_info = []
    unresolved = []
    mode_witnesses: dict[tuple[Any, ...], dict[str, Any]] = {}
    sources = selection["context"]["files"]
    for occurrence, category, master, strings in sources_raw:
        frames = {f"0x{s:X}": native_frame_witness(context, category.category_id, s) for s in (0xCF, 0xD0, 0x13E)}
        frame_refs = frame_references(frames, evidence["frames"])
        path = Path(occurrence.source.path).parent / category.database_name
        if not category.database_name or not path.is_file():
            category_rows.append({"category_id": category.category_id, "database": category.database_name,
                                  "category_occurrence": occurrence.as_dict(), "selectors": frame_refs,
                                  "status": "no ECU DDB filename" if not category.database_name else "DDB missing"})
            continue
        db = parser.parse_ecu_db(path)
        monitors = extract_monitor_records(db.sections[62]) if 62 in db.sections else []
        ffd = [row for row in monitors if row.flags & 2]
        did_rows = {u16(raw, 2): (index, raw) for index, raw in enumerate(raw_rows(db, 61))}
        counts = Counter()
        census["databases_with_type64"] += 64 in db.sections
        for row in ffd:
            item = did_rows.get(row.alternate_did)
            did = None if item is None else item[1]
            fixed = 0 if did is None else u16(did, 4)
            geometry = "ddb_fixed" if fixed else "inline_be16" if row.alternate_did >= 0x9000 else "inline_u8"
            mode = "missing" if did is None else str(did[6])
            counts[f"length:{geometry}"] += 1
            counts[f"support:{mode}"] += 1
            counts[f"presentation:{row.raw[0x4B]}"] += 1
            counts["conditioned_rows"] += bool(row.ffd_support_condition_key)
            counts["different_primary_and_snapshot_dids"] += row.primary_did != row.alternate_did
            counts["mode1_preceding_byte_underflow"] += did is not None and did[6] == 1 and row.bit_end < 8
            counts["bit_width_over_32"] += row.bit_end - row.bit_start + 1 > 32
            counts["inverted_bit_range"] += row.bit_end < row.bit_start
            if mode not in {"0", "1", "2"} or row.raw[0x4B] not in {0, 1, 2}:
                unresolved.append({"category_id": category.category_id, "database": category.database_name,
                    "monitor_key": row.monitor_key, "raw": row.raw.hex(),
                    "support_mode": mode, "presentation_mode_4b": row.raw[0x4B]})
            signature = (geometry, mode, row.raw[0x4B], bool(row.ffd_support_condition_key), row.primary_did != row.alternate_did)
            if signature not in mode_witnesses:
                mode_witnesses[signature] = {"category_id": category.category_id, "database": category.database_name,
                    "source": source(path, gts),
                    "row_ref": intern_evidence(monitor_pool, monitor_witness(db, strings, master, row, did_rows))}
        census.update(counts)
        census["categories_with_ddb"] += 1
        census["ffd_rows"] += len(ffd)
        category_rows.append({"category_id": category.category_id, "database": category.database_name,
                              "category_occurrence": occurrence.as_dict(),
                              "source": source(path, gts), "monitor_rows": len(monitors), "ffd_rows": len(ffd),
                              "row_mode_census": dict(sorted(counts.items())), "selectors": frame_refs})
        if frames["0x13E"]["frames"]:
            memberships = raw_rows(db, 171)
            monitor_by_key = {row.monitor_key: row for row in monitors}
            by_group = {}
            group_counts: dict[int, Counter[str]] = {}
            for index, raw in enumerate(memberships):
                monitor = monitor_by_key.get(u16(raw, 2))
                counts171 = group_counts.setdefault(raw[6], Counter())
                counts171["rows"] += 1
                if monitor is None:
                    counts171["missing_monitor"] += 1
                else:
                    conditioned = bool(monitor.ffd_support_condition_key)
                    counts171["conditioned" if conditioned else "unconditioned"] += 1
                    by_group.setdefault((raw[6], conditioned), (index, raw))
            additional_info.append({"category_id": category.category_id, "database": category.database_name,
                "source": source(path, gts), "selector": frame_refs["0x13E"],
                "table171": {
                    "record_size": db.sections[171].decoded_record_size if 171 in db.sections else None,
                    "record_count": len(memberships),
                    "decoded_rows_sha256": hashlib.sha256(b"".join(memberships)).hexdigest(),
                    "group_census": [{"byte6": group, **dict(sorted(counts171.items()))}
                                     for group, counts171 in sorted(group_counts.items())]},
                "monitor_witnesses": [{"byte6": group, "conditioned": conditioned,
                    "membership_index": index, "membership_raw": raw.hex(),
                    "monitor_ref": intern_evidence(monitor_pool,
                        monitor_witness(db, strings, master, monitor_by_key[u16(raw, 2)], did_rows))}
                    for (group, conditioned), (index, raw) in sorted(by_group.items())]})
        if Path(category.database_name).stem not in {"ADCU_P6", "Engine_CM_P6"}:
            continue
        # Keep one concrete witness per distinct relevant row mode, plus every
        # FFD-condition key. This preserves joins without duplicating the catalog.
        chosen: dict[tuple[Any, ...], Any] = {}
        for row in ffd:
            found = did_rows.get(row.alternate_did)
            did = None if found is None else found[1]
            fixed = 0 if did is None else u16(did, 4)
            signature = ("fixed" if fixed else "be16" if row.alternate_did >= 0x9000 else "u8",
                         None if did is None else did[6], row.raw[0x4B], row.raw[0x4A],
                         row.ffd_support_condition_key, row.primary_did != row.alternate_did)
            chosen.setdefault(signature, row)
        targets.append({"category_id": category.category_id, "database": category.database_name,
            "category_occurrence": occurrence.as_dict(),
            "generation": category.generation, "source": source(path, gts),
            "native_initial_category": str(category.category_id),
            "table_inventory": [{"table": t, "records": db.sections[t].header.record_count,
                                  "record_size": db.sections[t].decoded_record_size} for t in (61, 62, 64, 80, 89, 156, 157, 171) if t in db.sections],
            "row_mode_census": dict(sorted(counts.items())), "ffd_rows": len(ffd),
            "selectors": frame_refs,
            "request_materialization_examples": [
                {"selector": key, "dtc": "0x123456", "snapshot_record": record,
                 "bytes": (bytes.fromhex(frame["send"]["bytes"])[:2] + bytes.fromhex("123456" + record)).hex()}
                for key, record in (("0xCF", "01"), ("0xD0", "a1")) for frame in frames[key]["frames"]],
            "witness_refs": [intern_evidence(monitor_pool, monitor_witness(db, strings, master, row, did_rows))
                             for row in sorted(chosen.values(), key=lambda r: r.index)]})
    return {"region": region, "sources": sources, **selection,
            "census": dict(sorted(census.items())), "categories": category_rows,
            "mode_witnesses": list(mode_witnesses.values()), "targets": targets,
            "additional_info_categories": additional_info, "unresolved_row_modes": unresolved}


def semantics() -> dict[str, Any]:
    return {
        "scope": "Current GTS+ 2026.03.002.02 host per-DTC P6 FFD; offline source evidence",
        "consumer_tables": {"monitor": 62, "did_length_and_support": 61, "ffd_condition": 80,
            "physical": 13, "unit": 15, "pattern": 14,
            "selection": "P6 FFD explicitly queries 0x23E/0x23D/0x250; does not merge type157/156/89"},
        "requests": {"confirmed": {"selector": "0xCF", "function": "GetEachFrzFrmDatP6_DT:0x10002270"},
            "predictive": {"selector": "0xD0", "function": "GetEachFrzFrmDatP6_DT:0x10003000"},
            "materialization": "SetDTCToSndFrameSSRNo @0x100A0320 rejects record 0, writes byte5; SetDTCToSndFrame @0x100A02A0 requires DTC<0x1000000 and writes DTC be24 at bytes2..4. Input supplies selected confirmed/predictive record lists separately.",
            "additional_info": "Optional @0x10003A90 uses selector13E and exported CGetFrzFrmDatPreAddInfo::m_lstDIDMap, writes DID at bytes1/2; activation follows command bytes+50/+51 in @0x10001160. Availability is recorded per category, not presumed."},
        "responses": {
            "positive_check": "Master frame receive_check (5904 in the concrete CF/D0 witnesses); parser itself starts at fixed offsets after transport matching.",
            "geometry": "DTC:be24 at2..4 | status at5 (read but not used here) | snapshot_record:u8 at6 | identifier_count:u8 at7 | DID entries from8. One snapshot header per selected-record response, not a repeated outer-record loop.",
            "length": "SelectGetDIDLength @0x100A0080 queries type61 by DID(+2). Nonzero u16+4 supplies fixed payload length with NO inline length bytes. Absent row or zero length: DID<9000 uses inline u8 length; DID>=9000 uses inline be16 length.",
            "counts": "Nonzero identifier_count bounds entries. Zero means parse until the next bounds failure. Zero-length entries are not added. Duplicate DIDs retain the first complete entry.",
            "snapshot_types": {"confirmed": {"01": "0x1", "20..2F": "0x10"},
                               "predictive": {"A1": "0x101", "B0..BF": "0x210"}},
            "type_gate": "GetFFDType @0x1009FA10 returns0 for other record numbers; parser abandons that response path.",
            "truncation": "Header<8, incomplete DID/inline length/payload break parsing without manufacturing a DID. A truncated later entry leaves earlier complete DIDs available for signal analysis. These breaks normally return success, not a structural-error status.",
            "transaction_results": {"discard_selected_record_and_continue": [f"0x{x:08X}" for x in PRUNED_RESULTS],
                "other_nonzero": "Propagate and abort request operation", "cancel": "0xA0040003",
                "success": "Append returned CCommFrameData for parser; prune empty DTC lists after removal"}},
        "signals": {
            "join": "GetPidIdFromSSRDataId @0x1009FA70 scans type62 alternate DID u16+48 and returns monitor u16+34; AnalyzeSingleDataId @0x1009F230 requires byte+30&2.",
            "bounds_and_extract": "bit_start/end=u16+3C/+3E. Required bytes=(end>>3)+1; short fields are skipped. Zero computed byte span is C0040102. FUN_100BFF7C extracts inclusive MSB0 bits into a 32-bit result; end<start returns C0000001.",
            "support": "CheckSupportPid @0x1009F720 resolves type61 using alternate DID. Mode0 and2 include; mode1 requires (payload[(end>>3)-1] & (80>>(end&7))) == mask. End must be below payload_length*8. Missing DID rows/unknown modes are diagnostic paths, not new supported modes. Support result is cached by monitor key within this base object.",
            "condition": "Nonzero monitor+38 resets support then queries type80 by key+0. Variable ref+2 resolves Toyota master variable bytes; its first two bytes are referenced DID be16. CheckSupportBit @0x1009F580 searches the same parsed snapshot for that DID, requires condition type+0B==7, extracts bits+6/+8 and tests nonzero. Missing referenced DID excludes. CheckSupportPid does not propagate the CheckSupportBit return code.",
            "presentation": "SetFrzFrmDat @0x100A0600 appends ordinary signals only for monitor+4B=0/1; timestamp/odometer/absolute-time special destinations are separate branches. Mode2 is therefore not an unknown transport mode. SetSignalInfo @0x100A1190 copies OEM name, type13 Mul/Div/Offset/signedness/decimal count, type15 unit, type14 patterns and calls P6 ChangeSignalLSB, not P5 ChangeSignalLSB.",
            "conversion": "SetSignalInfo uses CCmdCommSignalLSBP6::InitInstance and ChangeSignalLSB. ChangeSignalLSB @0x100142C0 delegates only when category mode&1F==16. GetSignalLSB @0x10014930 looks up type64 by monitor key; missing-table A0030107 is a successful no-op. A row triggers live P6 support/ExecuteCommand before changing metadata; Mul/Div are normalized with GetCommonDivisorEuclid. The regional census records table64 availability."},
        "ordinary_p5_difference": "Ordinary current P5 parser @0x10001190 repeats snapshot headers and uses an inline u8 length after every DID. Request @0x10001A30 attempts FF first, falling back to selected records @0x10001E90 on the first handled transport result or first zero-count response. P6 starts with selected nonzero records, separates confirmed/predictive readers, and uses DDB-fixed / inline-u8 / inline-be16 lengths. P6 requires the returned DTC already in its selected list; P5 can add a missing returned DTC. Both alternate-DID join and FFD flag were independently recovered in P6.",
        "additional_info": {
            "did_map": [["1301", "1302", "1303"], ["1304", "1305", "1306"],
                        ["1307", "1308", "1309"], ["130A", "130B", "130C"],
                        ["129A", "129B", "129C"], ["129D", "129E", "129F"]],
            "request": "Selector13E is22FFFF/check62/maskFF on current HE_PCM_A_P6. Request @0x10003A90 chooses map row base0 for vehicle-type0..3/10..14, base2 for20..25, base4 for40..43; add record-family argument0/1, then column0..2. It writes the mapped DID at bytes1/2, requires returned DID echo, and uses the ordinary handled-result set as a successful omission.",
            "parser": "At0x100035D0 each62+DID response yields payload from offset3 with length=response_length-3 (no snapshot/DID-length header). It de-duplicates DIDs, tags map column2 as type101 and columns0/1 as type210, then invokes CGetFrzFrmDatPreAddInfo.",
            "monitor_selection": "GetPidIdFromPreAddInfo @0x100A3B90 queries type171 (2AB) with this+A8 vehicle selector, collecting monitor keys at row+2; AnalyzeSingleDataId @0x100A33B0 resolves type62 and extracts its+3C/+3E without the ordinary FFD-membership bit gate.",
            "support": "Additional-info CheckSupportPid @0x100A3A10 directly uses monitor+38 type80 condition (zero includes), not type61 mode handling. CheckSupportBit @0x100A3760 maps a referenced canonical DID found in either of the selected vehicle-type family's two three-DID map rows to the actual current response DID before the same type7/nonzero-bit test. This condition function admits vehicle groups0..3/10..14 and40..43; it excludes20..25 even though the request/parser recognize that group.",
            "storage": "SetFrzFrmDat @0x100A3CB0 uses the same P6 SetSignalInfo and ordinary+4B0/1 gate with separate time/odometer destinations."},
        "source_derived_smoke_inputs": {
            "basis": "Synthetic response bytes derived from native branches and current NA DDB rows; these are not captured vehicle responses or executed tests. Supply selected DTC123456 and use a fresh support cache for each support case.",
            "cases": [
                {"database": "Engine_CM_P6", "monitor_key": 1, "response": "590412345600010110021234",
                 "expected": "type61 raw0000021002000000 supplies fixed2; DID1002 payload1234 (no length byte), MSB0 bits0..15 raw1234"},
                {"database": "Engine_CM_P6", "monitor_key": 1, "response": "5904123456000101100212",
                 "expected": "incomplete fixed2 payload: no DID added"},
                {"database": "Engine_CM_P6", "monitor_key": 3, "response": "590412345600010110050101",
                 "expected": "DID1005 fixed2/support1; preceding byte01 supplies mask01 for end15, extracted bit15=1"},
                {"database": "Engine_CM_P6", "monitor_key": 3, "response": "590412345600010110050001",
                 "expected": "same raw signal bit1 but support mask absent: exclude"},
                {"database": "Engine_CM_P6", "monitor_key": 948, "response": "5904123456000101900000028080",
                 "expected": "DID9000 zero DDB length: consume inline be16 length0002; support80 in preceding byte, extracted bit8=1"},
                {"database": "HVAC_CM_P6", "monitor_key": 3002, "response": "5904123456000101501201a5",
                 "expected": "type61 raw0000125000000000: consume inline u8 length01; payloadA5"},
                {"database": "Engine_CM_P6", "monitor_key": 1, "response": "590412345600010010021234",
                 "expected": "identifier_count0 parses complete DID1002 then ends at bounds"},
                {"database": "Engine_CM_P6", "monitor_key": 1, "response": "590412345600010210021234100501",
                 "expected": "first DID1002 retained; incomplete later DID1005 omitted"},
                {"database": "Engine_CM_P6", "monitor_key": 1721, "response": "5904123456000101f46801010000000000",
                 "expected": "DIDF468 fixed7/support2; condition key1 raw01003b350000070007000007 variable353B=>F468, MSB0 bit7 (byte0 LSB, mask0x01) nonzero; signal bits8..15 raw1"},
                {"database": "Engine_CM_P6", "monitor_key": 1721, "response": "5904123456000101f46800010000000000",
                 "expected": "same signal raw1; condition MSB0 bit7 (byte0 LSB, mask0x01) zero excludes"}]},
        "residual_questions": [
            "Live support payload bits and selected snapshot numbers are vehicle responses, absent from this offline corpus.",
            "Which command+50/+51 vehicle-type/additional-info selection is supplied for a particular vehicle requires its selected-DTC input; raw type171 groups and regional selector bindings are retained.",
            "The additional-info request/parser accept vehicle types20..25 but their condition helper excludes that range. Current type171 row groups are retained rather than treating those branches as interchangeable."]}


def build(gts_root: Path | None = None, recovered_root: Path = DEFAULT_RECOVERED) -> dict[str, Any]:
    gts = resolve_gts_root(gts_root)
    evidence: dict[str, dict[str, Any]] = {"frames": {}, "monitors": {}}
    regions = [region_evidence(gts, region, evidence) for region in ("NA", "EU", "JP")]
    return {"schema": "gtsplus-p6-per-dtc-ffd-evidence-v4", "native": native(gts, recovered_root),
            "evidence": evidence,
            "evidence_reference_format": "sha256 of canonical UTF-8 JSON (sorted keys, compact separators); selector envelopes retain native query/status and ordered frame_ref entries into evidence.frames, including complete per-frame source and selection provenance. row_ref/monitor_ref/witness_refs resolve in evidence.monitors. Physical category occurrences, raw role rows and initial native resolution remain distinct. Type171 retains full row counts, decoded-row digest, per-group census, and one raw membership per group/condition branch.",
            "semantics": semantics(), "regions": regions}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--gts-root", type=Path)
    ap.add_argument("--recovered-root", type=Path, default=DEFAULT_RECOVERED)
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = ap.parse_args()
    result = build(args.gts_root, args.recovered_root)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
    print(args.out)


if __name__ == "__main__":
    main()
