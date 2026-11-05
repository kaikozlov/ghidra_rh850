#!/usr/bin/env python3
"""Extract current-release P6 RoB acquisition and signal contracts, offline.

The P6 plugin is independent of the P5 AB-service family. Native function
extents below were decompiled in Ghidra and the decisive branches checked in
x86 disassembly. Exact release hashes fail closed before exporting evidence.
No vehicle communication or generic interpreter configuration is performed.
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
from tools.techstream.ddb_semantics import _physical_info, records
from tools.techstream.gts.master import _master_variable
from tools.techstream.extract_gtsplus_p6_data_list import native_frame_witness, native_source_census
from tools.techstream.parse_ddb import DDBParser, _fixed_utf16le
from tools.techstream.techstream_paths import resolve_gts_root
from tools.techstream.extract_gtsplus_tss3_native_recorder import pe_info, read_va
from tools.techstream.recover_all_gtsplus_bodies import DEFAULT_OUTPUT, qualify_recovered_source

DEFAULT_OUT = REPO_ROOT / "data/generated/gtsplus_2026/p6_rob_semantics.json"
DEFAULT_RECOVERED_ROOT = DEFAULT_OUTPUT / "GTSPlus"
REGIONS = ("NA", "EU", "JP")
SELECTORS = (0xCC, 0x12A, 0x12B, 0x12C, 0x12D)
TABLES = (13, 14, 15, 66, 89, 90, 91, 118, 151, 152, 153, 163, 164)
PINNED_SHA256 = {
    "GetRoBP6_DT.dll": "4432db034cdaf3d7d41105da914c22b5fd6eb18ff592c09b5844ceb01212ffca",
    "KgpDataCtrl.dll": "19e709e12e53f485a84ccfbf6b226922b88502206c34b767db543c7f3df101f8",
    "CommandDataLib.dll": "ffce12af45554a552dbf616545c4c4e02780702e4cb9e2c6f8235ff4f05c79ab",
    "CommandCommon.dll": "98e313d197eb7115d037a2d46e71343b4b44862356e9d772c8f2f03d96e638d3",
}
# (VA, contiguous function-body size, derivation). No executable defaults or
# Ghidra project state are needed to reproduce the artifact.
FUNCTIONS = {
    "GetRoBP6_DT.dll": {
        "parse_behaviors": (0x10001160, 453, "Entries begin at 4; floor((receive_count-4)/4) entries of DTCbe24,status8. Status availability is byte3; matching masks select records."),
        "send_behavior_query": (0x10001330, 506, "Replace request bytes2/3 with resolved status-mask OR and memory11/12/13; NRC31 clears receive data and records success."),
        "resolve_status_masks": (0x10001710, 480, "Each requested status-key bit resolves type66 (0x242); row+8 is mask, +9 comparison value; OR comparison values into request byte2."),
        "init_behavior_query": (0x100018F0, 350, "GetCommFrmInfo selector12A."),
        "join_behavior_dictionary": (0x10001A50, 776, "Type163 key is returned DTCbe24; enabled byte3E gates known codes; byte3F overrides memory when nonzero; absent rows use fallback XP/XC/XB/XU signature and ??? name. Duplicate DTCs merge status masks."),
        "parse_snapshot_blocks": (0x10001EF0, 1246, "Count at8, blocks at9; type90 fixed length+4 or wire u8/<9000,be16/>=9000; stop on truncated header/payload; count0 scans to response end; retain first duplicate DID."),
        "join_signals": (0x100023D0, 764, "Scan type164 rows whose DID+24 matches block; collect key+14 then keyed lookup. Require (bit_end>>3)+1 <= payload_count; extraction4 uses buffer helper, all other modes scalar helper."),
        "cross_did_support": (0x100026D0, 601, "Variable length must equal2; interpret its two bytes as DIDbe16. Find that DID in the same returned record, require condition7, extract MSB0 bits and admit nonzero."),
        "local_support": (0x10002930, 838, "Type90 modes0/2 include;1 uses preceding-byte MSB0 mask at signal end-bit; other modes log error. Nonzero signal+16 joins type89. Presentation1 forces include after successful support evaluation; internal support errors are logged and this helper returns success with default exclusion."),
        "fetch_snapshot": (0x10002E00, 490, "Selector12C request bytes2..4=DTCbe24,5=frame8,6=memory; successful receive calls parse_snapshot_blocks."),
        "special_signal_keys": (0x10002FF0, 283, "Type91 key selects row+2 signal key."),
        "init_snapshot": (0x10003110, 378, "Load type164 (0x2A4), initialize special keys, GetCommFrmInfo selector12C."),
        "emit_signal": (0x10003290, 1986, "Presentation0/1 emits signal;2 only contributes special fields. Special keys1/2 select output slots with raw invalid sentinels FFFF/FFFFFFFF; key11 for categories1783/1977 uses1FFFFFFF. Keys4..9 decode BCD year/month/day/hour/minute/second with limits100,1..12,1..31,24,60,60; FF is invalid. Complete six-field date sets valid flag."),
        "signal_metadata": (0x10003A60, 1267, "Name+10, extraction+28, physical key+18 -> type13, unit from physical+E ->type15; copy mul/div/offset/sign/precision and signal bit width. Copy double bounds+0/+8, pattern+20 ->type14; absent pattern optionally joins type118 by signal key for factor text/help. No dynamic-LSB call."),
        "init_special_slots": (0x10003F60, 623, "Resolve type91 keys1,2,4..9; categories1783/1977 additionally key11."),
        "finalize_special_slots": (0x100041D0, 224, "For categories1783/1977, if any record uses special key11, clear key2's competing slot."),
        "parse_routine_blocks": (0x10004310, 1246, "Same block grammar as snapshot, but count at9 and blocks at10."),
        "fetch_routine_record": (0x10004980, 517, "Selector12D request bytes2..3=returned RIDbe16;4..7=framebe32; successful receive calls parse_routine_blocks."),
        "init_routine_record": (0x10004B90, 372, "Load type164 (0x2A4), initialize special keys, GetCommFrmInfo selector12D."),
        "parse_byte_frames": (0x10004DE0, 491, "Entries from12, one byte each. Keep1..1F and80..EF; sort and deduplicate."),
        "parse_dword_frames": (0x10004FD0, 648, "Entries from12, floor((receive_count-12)/4) big-endian dwords. Reject0 and values whose high nibble in byte0 or2 isF; sort and deduplicate."),
        "send_frame_query": (0x10005260, 445, "Selector12B request4..6=DTCbe24,7=memory. If receive_count>=12, format=byte9 and fetch RID=be16[10:12]."),
        "dispatch_frame_format": (0x10005460, 295, "Format0 dispatches byte-frame parser;1 dword-frame parser; others succeed with no parsed frame entries."),
        "init_frame_query": (0x10005590, 247, "GetCommFrmInfo selector12B."),
        "execute": (0x100056A0, 4082, "Accept request mode2 and acquisition kind1/2; input memory IDs11/12/13 carry status-key masks. Kind1 prepares frame/fetch objects, runs P6 enabled-RID discovery and fetches only if D000 supported; kind2 enumerates only. Set session wait70ms. Enumerated entries survive ten accepted communication-error results; fatal errors propagate. No supported status query returns A004020B."),
        "extract_scalar": (0x10006946, 192, "MSB0 inclusive extraction to u32. For ranges<=32 bits this is ordinary big-endian extraction; wider ranges OR-fold bytes because x86 shifts use count&31 and results wrap32. Caller enforces payload end bounds."),
        "extract_buffer": (0x10006B1B, 277, "Mode4 copies inclusive byte span into a 4096-byte local buffer; first byte shifted left by start&7, last byte right by7-(end&7), interior bytes unchanged. Single-byte span is additionally width-masked."),
    },
    "KgpDataCtrl.dll": {
        "table_kind": (0x10064F10, 239, "Logical table high byte selects family, low byte is physical table index: 2A3->163,2A4->164,25A->90,259->89,25B->91. No151/153 substitution."),
        "support_key": (0x1009D2C0, 269, "Type90 FindDbItem1 compares DID u16+2."),
        "behavior_strings": (0x100C4210, 1355, "Type163 string refs+30,+38,+34 feed name/comment/division respectively; signature is inline UTF16 at0."),
        "behavior_key": (0x100C4AD0, 268, "Type163 FindDbItem1 compares u32+2C."),
        "behavior_stride": (0x100C4BE0, 51, "GetRecordAddress multiplies index by44h."),
        "signal_name": (0x100C4E40, 585, "Type164 OEM name string reference is u32+10."),
        "signal_order": (0x100C5230, 228, "SortInOrder compares u16+1E."),
        "signal_key": (0x100C54E0, 269, "Type164 FindDbItem1 compares u16+14."),
        "signal_stride": (0x100C55F0, 51, "GetRecordAddress multiplies index by30h."),
    },
    "CommandDataLib.dll": {
        "physical_arithmetic": (0x10022AC0, 153, "Sign0 unsigned,1 two's-complement,3 sign-magnitude; other modes unsigned. Signed64 multiply, signed division truncated toward zero unless divisor's u32 value<=1, then add offset to low32 result."),
        "conversion_table": (0x10022C20, 38, "CComDataConvert basic overload receives conversion-table mul+8,div+C,offset+10,sign+16,width+18."),
        "pattern_lookup": (0x10034CF0, 99, "CCmdFrzFrmDat GetString calls GetValue then compares converted integer to pattern entries; unmatched returns null."),
        "freeze_frame_value": (0x10034D60, 222, "CCmdFrzFrmDat GetValue selects multi-data by index and passes raw u32 to basic conversion-table overload; extraction/presentation mode does not choose the special-format arithmetic overload."),
    },
    "CommandCommon.dll": {
        "routine_bitmap": (0x100678D0, 206, "MSB-first bitmap sets IDs base+byte_index*8+bit_index when shift-mode0."),
        "routine_support": (0x10067CF0, 839, "SelectorCC reads D100 root, at most32 bitmap bytes from response5; reads enabled D1nn pages except D1F0..D1FE and expands from base(page<<8). Cached per ECU; failed communication may yield empty enabled set."),
    },
}
ANCHORS = {
    "GetRoBP6_DT.dll": {
        "count8_blocks9": (0x10001FD3, "6a088d4858ffd683c9ffc7857cffffff00000000bf09000000"),
        "fixed_length": (0x1000208C, "0fb77004"),
        "wire_length_boundary": (0x1000209F, "b800900000663bd8732e"),
        "signal_bit_geometry": (0x100024F3, "0fb7501c0fb7481a"),
        "extraction_mode4": (0x10002569, "807828047539"),
        "preceding_support_byte": (0x10002AEA, "8a4401ff22c23ac2"),
    },
    "KgpDataCtrl.dll": {
        "behavior_stride44": (0x100C4C06, "6b450c44"),
        "signal_stride30": (0x100C5616, "6b450c30"),
    },
    "CommandDataLib.dll": {
        "signed_modes": (0x10022ACB, "83e800744a83e801742783e8027540"),
        "integer_divisor_gate": (0x10022B35, "8b451483f8017612"),
    },
    "CommandCommon.dll": {
        "exclude_inclusive_d1f0_d1fe": (0x10067EEA, "b9f0d10000894590663bc1720eb9fed10000663bc10f8691000000"),
    },
}


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def identity(path: Path, root: Path) -> dict[str, Any]:
    data = path.read_bytes()
    return {"path": path.relative_to(root).as_posix(), "size": len(data), "sha256": digest(data)}


def u16(raw: bytes, offset: int) -> int:
    return struct.unpack_from("<H", raw, offset)[0]


def u32(raw: bytes, offset: int) -> int:
    return struct.unpack_from("<I", raw, offset)[0]


def raw_rows(db: Any, table: int) -> list[bytes]:
    section = db.sections.get(table)
    return [] if section is None else list(records(section))


def native_evidence(root: Path, recovered_root: Path) -> dict[str, Any]:
    out = {}
    for name, expected in PINNED_SHA256.items():
        source_root = recovered_root if name == "CommandCommon.dll" else root
        path = source_root / "bin" / name
        qualification = (
            qualify_recovered_source(path, root / "bin" / name, component_root=recovered_root)
            if name == "CommandCommon.dll" else None
        )
        src = identity(path, source_root)
        if src["sha256"] != expected:
            raise ValueError(f"unsupported current-release bytes: {path}: {src['sha256']}")
        pe, data, base = pe_info(path)
        functions = {}
        for role, (va, size, derivation) in FUNCTIONS[name].items():
            body = read_va(pe, data, base, va, size)
            if len(body) != size:
                raise ValueError(f"truncated native function {name}:{va:#x}")
            functions[role] = {"va": f"0x{va:08X}", "rva": f"0x{va-base:X}", "size": size,
                               "sha256": digest(body), "bytes": body.hex(), "derivation": derivation}
        anchors = {}
        for role, (va, hex_bytes) in ANCHORS.get(name, {}).items():
            expected_bytes = bytes.fromhex(hex_bytes)
            if read_va(pe, data, base, va, len(expected_bytes)) != expected_bytes:
                raise ValueError(f"native instruction drift {name}:{va:#x}")
            anchors[role] = {"va": f"0x{va:08X}", "rva": f"0x{va-base:X}", "bytes": hex_bytes}
        out[name] = {"source": src, "source_kind": "installer-original plaintext twin" if name == "CommandCommon.dll" else "installed plaintext PE",
                     "image_base": f"0x{base:X}", "functions": functions, "instruction_anchors": anchors}
        if qualification is not None:
            out[name]["qualification"] = qualification
    return out


def table_census(db: Any) -> dict[str, Any]:
    return {str(t): {"count": db.sections[t].header.record_count, "record_size": db.sections[t].decoded_record_size,
                     "decoded_sha256": digest(db.sections[t].decoded_data)} for t in TABLES if t in db.sections}


def histogram(values: Any) -> dict[str, int]:
    return {str(k): v for k, v in sorted(Counter(values).items())}

def native_scalar(payload: bytes, start: int, end: int) -> int:
    """Express FUN_10006946, including its observed wide-field u32 folding."""
    if start < 0 or end < start or end >= len(payload) * 8:
        raise ValueError("invalid scalar byte witness")
    first, last = start >> 3, end >> 3
    shift = -(~end & 7)
    value = payload[last] >> (~end & 7)
    if first == last:
        return value & ((1 << (end - start + 1)) - 1)
    for index in range(last - 1, first, -1):
        shift += 8
        value |= (payload[index] << (shift & 31)) & 0xFFFFFFFF
    head = (payload[first] << (start & 7)) & 0xFF
    width_minus_one = end - start
    if width_minus_one < 7:
        head >>= (7 - width_minus_one) & 31
    else:
        head <<= (width_minus_one - 7) & 31
    return (value | head) & 0xFFFFFFFF



def catalog(db: Any, strings: Any, master: Any) -> dict[str, Any]:
    """Keep first witnesses of independent semantic dimensions, not a catalog."""
    support_rows = raw_rows(db, 90)
    support = {u16(r, 2): r for r in support_rows}
    conditions = {u16(r, 0): r for r in raw_rows(db, 89)}
    physical_rows = {u16(r, 0x0C): r for r in raw_rows(db, 13)}
    seen: set[tuple[str, Any]] = set()

    def newly_covered(features: dict[str, Any]) -> list[str]:
        reasons = []
        for dimension, value in features.items():
            token = (dimension, value)
            if token not in seen:
                seen.add(token)
                reasons.append(f"{dimension}={value}")
        return reasons

    codes = []
    for i, r in enumerate(raw_rows(db, 163)):
        signature = _fixed_utf16le(r[:0x2C])
        reasons = newly_covered({"behavior_class": signature[:2], "behavior_enabled": r[0x3E],
                                 "behavior_memory_override": r[0x3F]})
        if not reasons:
            continue
        codes.append({"record": i, "raw": r.hex(), "signature": signature, "witness_for": reasons,
                      "dtc": u32(r, 0x2C), "name_string_index": u32(r, 0x30),
                      "name": strings.get_string(u32(r, 0x30)),
                      "division_string_index": u32(r, 0x34), "division": strings.get_string(u32(r, 0x34)),
                      "comment_string_index": u32(r, 0x38), "comment": strings.get_string(u32(r, 0x38)),
                      "enabled": r[0x3E], "memory_override": r[0x3F]})
    signals = []
    for i, r in enumerate(raw_rows(db, 164)):
        key, condition, physical, start, end, order, pattern = struct.unpack_from("<7H", r, 0x14)
        did = u16(r, 0x24)
        phy_raw = physical_rows.get(physical)
        cond_raw = conditions.get(condition)
        support_raw = support.get(did)
        width = end - start + 1
        features = {"extraction": r[0x28], "presentation": r[0x29], "width": width,
                    "bit_alignment": (start & 7, end & 7),
                    "local_support": None if support_raw is None else support_raw[6],
                    "condition": None if cond_raw is None else cond_raw[0x0B],
                    "length": "missing" if support_raw is None else
                              "fixed" if u16(support_raw, 4) else "wire8" if did < 0x9000 else "wire16",
                    "pattern": bool(pattern)}
        if phy_raw is not None:
            mul, div, offset = struct.unpack_from("<3i", phy_raw)
            features.update({"sign_mode": phy_raw[0x14], "decimal_precision": phy_raw[0x15],
                             "multiplier": "identity" if mul == 1 else "negative" if mul < 0 else "nonidentity",
                             "divisor": "skip" if div in (0, 1) else "divide",
                             "offset": "zero" if offset == 0 else "negative" if offset < 0 else "positive"})
        reasons = newly_covered(features)
        if key == 0x060F and strings.get_string(u32(r, 0x10)) == "PCS PB Request Flag":
            reasons.append("required_ADCUpcs_key060F")
        if width > 32:
            reasons.append("wide_native_scalar_geometry")
        if not reasons:
            continue
        phy = _physical_info(db, strings, physical_data_key=physical, bit_start=start, bit_end=end, pattern_display_key=pattern)
        if phy is not None and phy_raw is not None:
            phy["sign_mode"] = phy_raw[0x14]
            phy.pop("signed", None)
        signals.append({"record": i, "raw": r.hex(), "key": key, "witness_for": reasons,
                        "name_string_index": u32(r, 0x10), "name": strings.get_string(u32(r, 0x10)), "did": did,
                        "support_condition_key": condition, "physical_data_key": physical,
                        "bit_start": start, "bit_end": end, "sort_key": order, "pattern_display_key": pattern,
                        "extraction_mode": r[0x28], "presentation_mode": r[0x29],
                        "maximum": struct.unpack_from("<d", r, 0)[0], "minimum": struct.unpack_from("<d", r, 8)[0],
                        "did_support_mode": None if support_raw is None else support_raw[6],
                        "did_fixed_length": None if support_raw is None else u16(support_raw, 4),
                        "condition_variable": None if cond_raw is None else _master_variable(master, u16(cond_raw, 2)),
                        "physical": phy})
    support_witnesses = []
    for i, r in enumerate(support_rows):
        did = u16(r, 2)
        reasons = newly_covered({"support_table_mode": r[6],
                                 "support_table_length": "fixed" if u16(r, 4) else "wire8" if did < 0x9000 else "wire16"})
        if did == 0xA802:
            reasons.append("required_Engine_type90_only_A802")
        if reasons:
            support_witnesses.append({"record": i, "did": did, "raw": r.hex(), "witness_for": reasons})
    physical_keys = {s["physical_data_key"] for s in signals}
    pattern_keys = {s["pattern_display_key"] for s in signals}
    signal_keys = {s["key"] for s in signals}
    condition_keys = {s["support_condition_key"] for s in signals}
    did_keys = {s["did"] for s in signals} | {s["did"] for s in support_witnesses}
    did_keys.update(int(s["condition_variable"]["bytes"], 16) for s in signals
                    if s["condition_variable"] is not None and len(s["condition_variable"]["bytes"]) == 4)
    unit_keys = {u16(r, 0x0E) for k, r in physical_rows.items() if k in physical_keys}
    keep = {
        13: lambda r: u16(r, 0x0C) in physical_keys,
        14: lambda r: u16(r, 0x0C) in pattern_keys,
        15: lambda r: u16(r, 4) in unit_keys,
        89: lambda r: u16(r, 0) in condition_keys,
        90: lambda r: u16(r, 2) in did_keys,
        91: lambda r: u16(r, 2) in signal_keys,
        118: lambda r: u16(r, 0x0C) in signal_keys,
    }
    libraries = {
        str(t): [{"record": i, "raw": r.hex()} for i, r in enumerate(raw_rows(db, t)) if keep[t](r)]
        for t in keep if t in db.sections
    }
    a, b = {r.hex() for r in support_rows}, {r.hex() for r in raw_rows(db, 151)}
    selected_support = {r["raw"] for r in support_witnesses}
    return {"selection": "representative NA evidence; first row covering each independent dimension plus explicitly required witnesses",
            "covered_dimensions": {dimension: sorted((str(value) for name, value in seen if name == dimension))
                                   for dimension in sorted({name for name, _ in seen})},
            "tables": table_census(db), "behavior_codes": codes, "signals": signals,
            "support_witnesses": support_witnesses, "raw_join_tables": libraries,
            "type90_vs151": {"used_by_plugin": 90, "only90_count": len(a-b), "only151_count": len(b-a),
                              "selected_only90": sorted((a-b) & selected_support),
                              "selected_only151": sorted((b-a) & selected_support)},
            "signal_geometry": "inclusive MSB0 within DID payload; native scalar accumulator and x86 shifts wrap32, including wide fields",
            "physical_formula": "converted_integer=low32(trunc_toward_zero(sign_interpret(raw)*mul/div)+offset); divisor0/1 skips division; decimal precision is separate metadata; patterns compare converted_integer"}


def request_witnesses(category: int, db: Any, context: Any) -> dict[str, Any]:
    codes = raw_rows(db, 163)
    dtc = u32(codes[0], 0x2C)
    mask_rows = raw_rows(db, 66)
    comparison = 0
    for row in mask_rows:
        comparison |= row[9]
    return {"selectors": {f"0x{s:X}": native_frame_witness(context, category, s) for s in SELECTORS},
            "status_mask_rows": [r.hex() for r in mask_rows], "example_dtc": dtc,
            "all_db_status_keys_mask": sum({u32(r, 0) for r in mask_rows}),
            "behavior_queries": [(bytes((0x19, 0x17, comparison, memory))).hex() for memory in (0x11, 0x12, 0x13)],
            "frame_queries": [(bytes.fromhex("3101d000") + dtc.to_bytes(3, "big") + bytes((memory,))).hex() for memory in (0x11, 0x12, 0x13)],
            "snapshot_fetch_example": (bytes.fromhex("1918") + dtc.to_bytes(3, "big") + bytes((1, 0x11))).hex(),
            "routine_fetch_template": "31 01 <RID returned at frame-response10:12,be16> <frame returned after12,be32>",
            "example_frame_is_synthetic": True,
            "live_inputs": ["enabled-RID bitmap contains D000", "frame response format0/1", "routine fetch RID and record selectors from frame response"]}


def extract(root: Path, recovered_root: Path) -> dict[str, Any]:
    native = native_evidence(root, recovered_root)
    parser = DDBParser()
    regions = {}
    selected = {}
    for region in REGIONS:
        context, sources, selection = native_source_census(parser, root, region, 0xA0, "GetRoBP6_DT.dll")
        rows = []
        missing = []
        mode_examples: dict[str, Any] = {}
        for occurrence, cat, master, strings in sources:
            path = Path(occurrence.source.path).parent / cat.database_name
            if path.suffix != ".ddb":
                path = path.with_suffix(".ddb")
            if not cat.database_name or not path.is_file():
                missing.append({"category": cat.category_id, "database": cat.database_name,
                                "category_occurrence": occurrence.as_dict()})
                continue
            db = parser.parse_ecu_db(path)
            rr = raw_rows(db, 164)
            row = {"category": cat.category_id, "database": cat.database_name, "source": identity(path, root),
                   "category_occurrence": occurrence.as_dict(),
                   "tables": table_census(db), "extraction_modes": histogram(r[0x28] for r in rr),
                   "presentation_modes": histogram(r[0x29] for r in rr),
                   "support_conditions_nonzero": sum(bool(u16(r, 0x16)) for r in rr),
                   "local_support_modes": histogram(r[6] for r in raw_rows(db, 90)),
                   "fixed_length_dids": sum(bool(u16(r, 4)) for r in raw_rows(db, 90)),
                   "wire_length_dids": sum(not u16(r, 4) for r in raw_rows(db, 90)),
                   "wide_scalar_rows": [{"record": i, "key": u16(r, 0x14),
                                         "name": None if strings is None else strings.get_string(u32(r, 0x10)), "raw": r.hex()}
                                        for i, r in enumerate(rr) if u16(r, 0x1C) - u16(r, 0x1A) + 1 > 32],
                   "selector_witnesses": {f"0x{s:X}": native_frame_witness(context, cat.category_id, s) for s in SELECTORS}}
            rows.append(row)
            for i, raw in enumerate(rr):
                mode = str(raw[0x28])
                if mode not in mode_examples:
                    mode_examples[mode] = {"category": cat.category_id, "database": cat.database_name, "record": i,
                                           "name": None if strings is None else strings.get_string(u32(raw, 0x10)), "raw": raw.hex()}
            if region == "NA" and strings is not None and path.stem in ("ADCU_P6", "Engine_CM_P6", "NCM_P6", "BSCM_A_P6"):
                key = f"{region}:{occurrence.source.family}:{occurrence.ordinal}:{row['source']['sha256']}"
                if key not in selected:
                    selected[key] = catalog(db, strings, master)
                    selected[key]["request_witnesses"] = request_witnesses(cat.category_id, db, context)
                    selected[key]["source"] = row["source"]
                row["selected_catalog"] = key
        totals = Counter()
        modes = Counter()
        presentation = Counter()
        for row in rows:
            for table, meta in row["tables"].items():
                totals[table] += meta["count"]
            modes.update(row["extraction_modes"])
            presentation.update(row["presentation_modes"])
        regions[region] = {**selection,
                           "role": "0xA0", "plugin": "GetRoBP6_DT.dll",
                           "source_occurrence_count": len(rows), "missing_databases": missing, "table_totals": dict(sorted(totals.items(), key=lambda p: int(p[0]))),
                           "extraction_modes": dict(sorted(modes.items())), "presentation_modes": dict(sorted(presentation.items())),
                           "mode_examples": mode_examples, "categories": rows}
    return {"schema": "gtsplus-current-p6-rob-semantics-3", "scope": "offline current-release host acquisition and DDB signal interpretation",
            "native_evidence": native, "regions": regions, "selected_catalogs": selected,
            "transport_contract": {
                "behavior": "12A:19 17 status memory ->59 17; memory11/12/13; response byte3 availability, entries4 DTCbe24/status8",
                "frames": "12B:31 01 D0 00 DTCbe24 memory ->71 01 D0 00; format9,RIDbe16@10,entries12;0=u8,1=be32",
                "snapshot": "12C:19 18 DTCbe24 frame8 memory ->59 18; count8,blocks9",
                "routine": "12D:31 01 returnedRIDbe16 framebe32 ->71 01; count9,blocks10",
                "block": "DIDbe16 | optional wire length | data; type90+4 nonzero omits wire length; else u8 for DID<9000 orbe16 for>=9000",
                "bounds": "behavior list requires>=4 bytes and ignores partial final4-byte entry; frame response<12 leaves formatFF and emits no frames; block headers and payloads must fit receive length; truncated tail stops parsing; count0 scans complete blocks to end; duplicate DID keeps first",
                "echo_checks": "plugin does not independently validate echoed DTC/frame/RID beyond master receive mask/check",
                "accepted_nonfatal_communication_errors": ["91010009", "90020321", "90020323", "A0040201", "C0040001", "A0040202", "90020327", "91020320", "91020310", "91020322"],
            },
            "synthetic_scalar_witnesses": [
                {"payload": "000102030405060708090a", "bit_start": 8, "bit_end": 87,
                 "raw_u32": native_scalar(bytes(range(11)), 8, 87),
                 "source": "NCM_P6/P6F type164 rows32..34 use this 80-bit span; payload is synthetic"}
            ],
            "p5_differences": ["P5 AB01/11 behaviorbe16 becomes P6 1917 DTCbe24/status8 with three memory selections.",
                               "P5 AB02/12 framebe16 becomes P6 D000 routine enumerating either frame8 or framebe32 plus a returned fetch RID.",
                               "P5 AB03/13 count6/blocks7 becomes P6 1918 count8/blocks9 or routine count9/blocks10.",
                               "P5 DID6000..6FFF has wirebe32 length; P6 prioritizes type90 fixed length, then wireu8/<9000 orwirebe16/>=9000.",
                               "P5 type87/88 (behavior16,signal72B) becomes P6 type163/164 (DTC24,signal48B); no type151/153 substitution and no ChangeSignalLSB in the recovered P6 RoB metadata path."],
            "remaining_questions": ["ECU-specific enabled RIDs, returned frame format/fetch RID/record IDs and actual payloads require an observed response; offline DDBs contain no runtime record catalog.",
                                    "Mode4 buffer extraction has no current NA/EU/JP bound-catalog witness; its native helper is retained, including its fixed4096-byte local-buffer assumption.",
                                    "Unconsumed row bytes remain raw; missing regional ECU databases are enumerated, not treated as zero-signal catalogs."]}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--gts-root", type=Path)
    ap.add_argument("--recovered-root", type=Path, default=DEFAULT_RECOVERED_ROOT,
                    help="Qualified aggregate GTSPlus component root")
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = ap.parse_args()
    result = extract(resolve_gts_root(args.gts_root), args.recovered_root)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2, ensure_ascii=False, allow_nan=False) + "\n", encoding="utf-8")
    print(args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
