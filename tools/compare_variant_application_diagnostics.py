#!/usr/bin/env python3
"""Compare canonical Sienna application diagnostics with tracked 8965H1202000.

The comparison intentionally mixes two evidence layers and labels them:
  * raw CodeFlash tables/configuration, which are deterministic byte evidence;
  * a compact target-native Ghidra evidence set, used only for producer/output
    bounds and the few RoutineControl semantic deltas called out explicitly.

It does not assume a whole-application relocation and it does not infer OEM
meaning for H-only lifecycle states.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import struct
from collections import Counter, defaultdict
from pathlib import Path
from sienna_target import CODEFLASH as SIENNA_CODEFLASH
from corolla_h_constants import RAW_DUMP as H_RAW_DUMP

REPO = Path(__file__).resolve().parents[1]
SERVICE = struct.Struct("<IIIIBBBBB3x")
DID = struct.Struct("<HHIII")
RID = struct.Struct("<HBBI")
RID_CB = struct.Struct("<HHII")

SERVICE_SIDS = [0x10, 0x11, 0x14, 0x19, 0x22, 0x23, 0x27, 0x28,
                0x2E, 0x31, 0x34, 0x36, 0x37, 0x3E, 0x85, 0xAB, 0xBA]
ROUTINE_RIDS = [0x1000, 0x1001, 0x1002, 0x1004, 0x1007, 0x1008, 0x1009,
                0x100E, 0x100F, 0x1010, 0x1100, 0x1103, 0x1106, 0x1108,
                0x1109, 0x110A, 0x110B, 0x110C, 0x110D]
SUCCESS_STUB = bytes.fromhex("00527f00")

# RoutineControl configuration locations are exact-image facts. Pointer-bearing
# tables move, but decoded policy/support/width semantics are compared below.
ROUTINE_LAYOUT = {
    "sienna": {
        "rid": 0x26AEC, "callbacks": 0x25804, "policy_index": 0x26690,
        "policy_counts": 0x26420, "policy_ptrs": 0x26678,
        "config": 0x26B8D, "size_bits": 0x263AC,
        "descriptor_ptrs": {
            "type1_input": 0x2686C, "type1_output": 0x268BC,
            "type2_input": 0x269AC, "type2_output": 0x269FC,
            "type3_output": 0x267CC,
        },
    },
    "corolla_h": {
        "rid": 0x267FC, "callbacks": 0x255C0, "policy_index": 0x263A0,
        "policy_counts": 0x26130, "policy_ptrs": 0x26388,
        "config": 0x2689D, "size_bits": 0x260BC,
        "descriptor_ptrs": {
            "type1_input": 0x2657C, "type1_output": 0x265CC,
            "type2_input": 0x266BC, "type2_output": 0x2670C,
            "type3_output": 0x264DC,
        },
    },
}
CONFIG_STRIDE = 15
CONTROL_SUPPORTED_OFFSET = {1: 4, 2: 9, 3: 1}
COUNT_OFFSET = {
    "type1_input": 6, "type1_output": 8,
    "type2_input": 11, "type2_output": 13, "type3_output": 3,
}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def hx(value: int, width: int = 0) -> str:
    return f"0x{value:0{width}X}" if width else f"0x{value:X}"


def display_path(path: Path) -> str:
    resolved = path.resolve()
    try:
        return str(resolved.relative_to(REPO.resolve()))
    except ValueError:
        return str(path)


def load_codeflash(path: Path) -> tuple[bytes, str]:
    data = path.read_bytes()
    if len(data) == 0x100000:
        return data, "bare-codeflash"
    if len(data) == 0x200000 and data[0x100000:] == b"\xff" * 0x100000:
        return data[:0x100000], "trim-all-ff-upper-1mib-from-2mib-range-dump"
    raise ValueError(f"unsupported CodeFlash geometry: {path} size={len(data):#x}")


def find_service_table(image: bytes) -> int:
    hits = []
    span = SERVICE.size * len(SERVICE_SIDS)
    for off in range(0, len(image) - span + 1, 4):
        if all(image[off + i * SERVICE.size + 0x10] == sid
               for i, sid in enumerate(SERVICE_SIDS)):
            hits.append(off)
    if len(hits) != 1:
        raise ValueError(f"application service table is not unique: {[hx(x) for x in hits]}")
    return hits[0]


def parse_service_table(image: bytes, base: int) -> list[dict]:
    rows = []
    for i in range(len(SERVICE_SIDS)):
        callback, security_ptr, session_ptr, subfn_ptr, sid, has_subfn, sec_count, sess_count, subfn_count = SERVICE.unpack_from(
            image, base + i * SERVICE.size
        )
        rows.append({
            "sid": hx(sid, 2),
            "direct_callback": hx(callback) if callback else None,
            "direct_callback_present": callback != 0,
            "security_list_present": security_ptr != 0,
            "session_list_present": session_ptr != 0,
            "subfunction_table_present": subfn_ptr != 0,
            "has_subfunction": has_subfn,
            "security_count": sec_count,
            "session_count": sess_count,
            "subfunction_count": subfn_count,
        })
    return rows


def valid_did_record(image: bytes, off: int) -> tuple[int, int, int, int, int] | None:
    if off < 0 or off + DID.size > len(image):
        return None
    did, length, callback, aux, tail = DID.unpack_from(image, off)
    if not (0x0100 <= did <= 0xF18C and 0 < length <= 0x100):
        return None
    if callback == 0 or callback >= len(image) or callback & 1:
        return None
    if aux and (aux >= len(image) or aux & 1):
        return None
    if tail > 0x100:
        return None
    return did, length, callback, aux, tail


def find_did_table(image: bytes) -> tuple[int, list[tuple[int, int, int, int, int]]]:
    candidates = []
    needle = struct.pack("<HH", 0x0100, 32)
    start = 0
    while True:
        off = image.find(needle, start)
        if off < 0:
            break
        start = off + 1
        if off & 3:
            continue
        rows = []
        cursor = off
        previous = -1
        while True:
            row = valid_did_record(image, cursor)
            if row is None or row[0] <= previous:
                break
            rows.append(row)
            previous = row[0]
            cursor += DID.size
        if len(rows) >= 100 and rows[-1][0] == 0xF18C:
            candidates.append((off, rows))
    if len(candidates) != 1:
        raise ValueError(
            "readable-DID table is not unique: "
            + repr([(hx(off), len(rows)) for off, rows in candidates])
        )
    return candidates[0]


def find_routine_table(image: bytes, stride: int) -> int:
    hits = []
    span = stride * len(ROUTINE_RIDS)
    for off in range(0, len(image) - span + 1, 2):
        if all(struct.unpack_from("<H", image, off + i * stride)[0] == rid
               for i, rid in enumerate(ROUTINE_RIDS)):
            hits.append(off)
    if len(hits) != 1:
        raise ValueError(f"RID stride-{stride} table not unique: {[hx(x) for x in hits]}")
    return hits[0]


def u16(image: bytes, off: int) -> int:
    return struct.unpack_from("<H", image, off)[0]


def u32(image: bytes, off: int) -> int:
    return struct.unpack_from("<I", image, off)[0]


def descriptor_width(image: bytes, layout: dict, index: int, kind: str) -> int:
    cfg = layout["config"] + index * CONFIG_STRIDE
    count = image[cfg + COUNT_OFFSET[kind]]
    if count == 0:
        return 0
    ptr = u32(image, layout["descriptor_ptrs"][kind] + index * 4)
    if not 0 < ptr < len(image):
        raise ValueError(f"bad descriptor pointer {ptr:#x} for index {index} {kind}")
    desc = ptr + (count - 1) * 6
    field_type = image[desc + 1]
    bit_offset = u16(image, desc + 4)
    field_bits = u16(image, desc + 2) if field_type == 7 else image[layout["size_bits"] + field_type]
    return (field_bits + bit_offset + 7) // 8


def parse_routines(image: bytes, layout: dict) -> list[dict]:
    rows = []
    for i, expected_rid in enumerate(ROUTINE_RIDS):
        rid, _pad, enabled, policy_ptr = RID.unpack_from(image, layout["rid"] + i * RID.size)
        cb_rid, cb_pad, precondition, action = RID_CB.unpack_from(
            image, layout["callbacks"] + i * RID_CB.size
        )
        if rid != expected_rid or cb_rid != rid or cb_pad != 0:
            raise ValueError(f"RoutineControl row mismatch at {i}: {rid:#x}/{cb_rid:#x}")
        policy_index = u16(image, layout["policy_index"] + i * 2)
        sec_count = image[layout["policy_counts"] + policy_index * 2]
        session_count = image[layout["policy_counts"] + policy_index * 2 + 1]
        _sec_ptr, session_ptr = struct.unpack_from(
            "<II", image, layout["policy_ptrs"] + policy_index * 8
        )
        sessions = []
        for j in range(session_count):
            record = u32(image, session_ptr + j * 4)
            if not 0 < record < len(image) - 1:
                raise ValueError(f"bad RoutineControl session record {record:#x}")
            sessions.append(image[record + 1])
        cfg = layout["config"] + i * CONFIG_STRIDE
        rows.append({
            "rid": hx(rid, 4),
            "enabled": enabled,
            "policy_index": policy_index,
            "security_count": sec_count,
            "sessions": sessions,
            "control_type_support": {
                str(t): image[cfg + CONTROL_SUPPORTED_OFFSET[t]] for t in (1, 2, 3)
            },
            "widths": {kind: descriptor_width(image, layout, i, kind) for kind in COUNT_OFFSET},
            "precondition_callback": hx(precondition) if precondition else None,
            "action_callback": hx(action) if action else None,
            "policy_record_pointer": hx(policy_ptr),
        })
    return rows


def semantic_routine_config(row: dict) -> dict:
    return {k: row[k] for k in (
        "rid", "enabled", "policy_index", "security_count", "sessions",
        "control_type_support", "widths"
    )}


def load_evidence(path: Path, image: bytes) -> tuple[dict, dict[int, dict]]:
    evidence = json.loads(path.read_text(encoding="utf-8"))
    if evidence["image"]["sha256"] != sha256(image):
        raise ValueError("decompiler evidence is bound to a different CodeFlash image")
    functions = {}
    for row in evidence["functions"]:
        addr = int(row["entry"], 16)
        size = row["body_size"]
        if sha256(image[addr : addr + size]) != row["body_sha256"]:
            raise ValueError(f"raw body hash mismatch for evidence function {addr:#x}")
        code = row["decompiled_c"]
        if sha256(code.encode("utf-8")) != row["decompiled_c_sha256"]:
            raise ValueError(f"decompiler C hash mismatch for evidence function {addr:#x}")
        functions[addr] = row
    return evidence, functions


def direct_write_extent(code: str) -> tuple[int, list[str]]:
    extent = 0
    leftovers = []
    helpers = {
        "FUN_00063824": 2, "FUN_0006385c": 2,
        "func_0x0006380c": 4, "FUN_0006380c": 4,
        "func_0x00063844": 4, "FUN_00063844": 4,
    }
    for line in code.splitlines():
        text = line.strip()
        if not text or text.startswith(("undefined", "int ", "uint ", "char ", "byte ", "short ", "ushort ", "bool ", "void ")):
            continue
        matched = False
        for pattern, width in (
            (r"^\*param_1\s*=", 1),
            (r"^\*\(bool \*\)param_1\s*=", 1),
            (r"^\*\(undefined1 \*\)param_1\s*=", 1),
            (r"^\*\(ushort \*\)param_1\s*=", 2),
            (r"^\*\(undefined2 \*\)param_1\s*=", 2),
            (r"^\*\(undefined4 \*\)param_1\s*=", 4),
        ):
            if re.search(pattern, text):
                extent = max(extent, width)
                matched = True
                break
        if matched:
            continue
        match = re.search(r"^param_1\[(0x[0-9a-f]+|\d+)\]\s*=", text)
        if match:
            extent = max(extent, int(match.group(1), 0) + 1)
            continue
        match = re.search(
            r"^\*\(undefined([124]) \*\)\(param_1 \+ (0x[0-9a-f]+|\d+)\)\s*=", text
        )
        if match:
            extent = max(extent, int(match.group(2), 0) + int(match.group(1)))
            continue
        for helper, width in helpers.items():
            if helper + "(" in text and "param_1" in text:
                offset_match = re.search(r"param_1 \+ (0x[0-9a-f]+|\d+)", text)
                offset = int(offset_match.group(1), 0) if offset_match else 0
                extent = max(extent, offset + width)
                matched = True
                break
        if matched:
            continue
        if "param_1" in text:
            leftovers.append(text)
    return extent, leftovers


def classify_h_rdbi(image: bytes, did_rows: list[tuple[int, int, int, int, int]], evidence: dict[int, dict]) -> dict:
    uses: dict[int, list[tuple[int, int]]] = defaultdict(list)
    for did, length, callback, _aux, _tail in did_rows:
        uses[callback].append((did, length))

    fixed_by_did = {
        0x0105: 12,
        0x010B: 16,
        0x2030: 16,
        0x2031: 16,
        0x2032: 17,
        0xF181: 33,
    }
    entries = []
    for callback, callback_uses in sorted(uses.items()):
        lengths = {length for _did, length in callback_uses}
        if len(lengths) != 1:
            raise ValueError(f"callback {callback:#x} serves multiple declared lengths {lengths}")
        declared = next(iter(lengths))
        record = evidence.get(callback)
        if record is None:
            raise ValueError(f"RDBI producer missing decompiler evidence: {callback:#x}")
        code = record["decompiled_c"]
        size = record["body_size"]
        body = image[callback : callback + size]
        dids = {did for did, _length in callback_uses}

        if body == SUCCESS_STUB:
            cls, extent, basis = "success_stub", 0, "body is exact `00 52 7F 00` return-success stub"
        elif 0xF186 in dids:
            if "FUN_0008ae04();" not in code:
                raise ValueError("F186 delegate shape drifted")
            lower = evidence[0x8B80C]["decompiled_c"]
            if "*param_1 =" not in lower:
                raise ValueError("F186 lower session getter no longer performs one-byte output")
            cls, extent, basis = "session_delegate", 1, "0x4A37E -> 0x8AE04 -> 0x8B80C; lower getter writes one byte"
        elif 0xF18C in dids:
            if "iVar3 - (param_2 & 0xffff)" not in code:
                raise ValueError("F18C declared-length loop bound drifted")
            cls, extent, basis = "declared_bounded_loop", declared, "copy/fill loops are bounded by `(param_2 & 0xffff)`"
        elif "func_0x00047e76(param_1,param_2)" in code or "FUN_00047e76(param_1,param_2)" in code:
            helper = evidence[0x47E76]["decompiled_c"]
            if "uVar4 < (param_2 & 0xffff)" not in helper or "uVar4 < (param_2 & 0xff)" not in helper:
                raise ValueError("0x47E76 declared-bound proof drifted")
            cls, extent, basis = "declared_bounded_bitmap", declared, "0x47E76 clears declared_len and bounds every bit update by declared_len"
        elif "func_0x00047f38(" in code or "FUN_00047f38(" in code:
            helper = evidence[0x47F38]["decompiled_c"]
            if "uVar3 < (param_3 & 0xffff)" not in helper or "uVar7 < (param_3 & 0xff)" not in helper:
                raise ValueError("0x47F38 declared-bound proof drifted")
            cls, extent, basis = "declared_bounded_bitmap", declared, "0x47F38 clears declared_len and bounds every bit update by declared_len"
        elif "func_0x0004d044(param_1,param_2)" in code or "FUN_0004d044(param_1,param_2)" in code:
            helper = evidence[0x4D044]["decompiled_c"]
            if "iVar4 - (param_2 & 0xffff)" not in helper or "uVar5 + 3" not in helper:
                raise ValueError("0x4D044 declared-bound proof drifted")
            cls, extent, basis = "declared_bounded_engine", declared, "0x4D044 clear/copy engine is bounded by forwarded declared_len"
        elif any(did in fixed_by_did for did in dids):
            fixed = {fixed_by_did[did] for did in dids if did in fixed_by_did}
            if len(fixed) != 1:
                raise ValueError(f"fixed-loop producer has inconsistent extents: {callback_uses}")
            extent = next(iter(fixed))
            # Pin the dynamic-loop cases to their target-native decompiler forms.
            required = {
                0x0105: ["iVar4 + param_1", "param_1 + 10", "param_1 + 0xb"],
                0x010B: ["iVar4 + param_1"],
                0x2030: ["uVar3 + param_1", "puVar1[8]"],
                0x2031: ["uVar3 + param_1", "puVar1[8]"],
                0x2032: ["param_1[iVar2 + 1]"],
                0xF181: ["*param_1 = 2", "param_1[iVar2 + 0x11]"],
            }
            for did in dids:
                for needle in required.get(did, []):
                    if needle not in code:
                        raise ValueError(f"fixed-loop evidence drifted for DID {did:04X}: {needle}")
            cls, basis = "fixed_extent_loop", "target-native loop/store form pinned for configured DID width"
        else:
            extent, leftovers = direct_write_extent(code)
            if leftovers:
                raise ValueError(
                    f"unclassified destination use in RDBI producer {callback:#x}: {leftovers!r}"
                )
            if extent == 0:
                raise ValueError(f"non-stub RDBI producer has no classified output: {callback:#x}")
            cls, basis = "direct_fixed", "only fixed-offset direct stores / pinned 2- or 4-byte endian helpers"

        if extent > declared:
            relation = "overrun"
        elif extent < declared:
            relation = "underwrite"
        else:
            relation = "exact_or_declared_bounded"
        entries.append({
            "callback": hx(callback),
            "dids": [hx(did, 4) for did, _length in callback_uses],
            "declared_length": declared,
            "classification": cls,
            "max_write_extent": extent,
            "write_relation": relation,
            "basis": basis,
        })

    overruns = [entry for entry in entries if entry["write_relation"] == "overrun"]
    understates = [entry for entry in entries if entry["write_relation"] == "underwrite"]
    nonstub_under = [entry for entry in understates if entry["classification"] != "success_stub"]
    stale_dids = sorted(
        int(did, 16)
        for entry in understates
        for did in entry["dids"]
    )
    if overruns or nonstub_under:
        raise ValueError(f"unexpected H RDBI output-bound result: overruns={overruns} nonstub_under={nonstub_under}")
    return {
        "unique_producer_count": len(entries),
        "classification_counts": dict(sorted(Counter(entry["classification"] for entry in entries).items())),
        "overrun_producer_count": len(overruns),
        "nonstub_underwrite_producer_count": len(nonstub_under),
        "stale_response_dids": [hx(did, 4) for did in stale_dids],
        "stale_response_did_count": len(stale_dids),
        "stale_response_basis": "every underwriter is an exact 4-byte return-success stub; no non-stub underwriter or overrun remains after exhaustive 180-producer classification",
        "producers": entries,
    }


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--sienna", type=Path, default=SIENNA_CODEFLASH)
    p.add_argument("--target", type=Path, default=H_RAW_DUMP)
    p.add_argument("--target-evidence", type=Path, default=REPO / "data/generated/corolla_8965H1202000_application_diagnostic_decompiler_evidence.json")
    p.add_argument("--sienna-disclosure-audit", type=Path, default=REPO / "data/generated/response_disclosure_audit.json")
    p.add_argument("--out", type=Path, default=REPO / "data/generated/corolla_8965H1202000_application_diagnostics_diff.json")
    args = p.parse_args()

    sienna, sienna_norm = load_codeflash(args.sienna)
    target, target_norm = load_codeflash(args.target)
    evidence_meta, evidence = load_evidence(args.target_evidence, target)

    s_service_base = find_service_table(sienna)
    h_service_base = find_service_table(target)
    s_services = parse_service_table(sienna, s_service_base)
    h_services = parse_service_table(target, h_service_base)
    service_semantic_fields = [
        "sid", "direct_callback_present", "security_list_present", "session_list_present",
        "subfunction_table_present", "has_subfunction", "security_count", "session_count", "subfunction_count"
    ]
    service_shape_same = all(
        {k: s[k] for k in service_semantic_fields} == {k: h[k] for k in service_semantic_fields}
        for s, h in zip(s_services, h_services)
    )

    s_did_base, s_dids = find_did_table(sienna)
    h_did_base, h_dids = find_did_table(target)
    s_by_did = {row[0]: row for row in s_dids}
    h_by_did = {row[0]: row for row in h_dids}
    removed = sorted(s_by_did.keys() - h_by_did.keys())
    added = sorted(h_by_did.keys() - s_by_did.keys())
    length_changes = [
        {"did": hx(did, 4), "sienna": s_by_did[did][1], "corolla_h": h_by_did[did][1]}
        for did in sorted(s_by_did.keys() & h_by_did.keys())
        if s_by_did[did][1] != h_by_did[did][1]
    ]

    h_rdbi = classify_h_rdbi(target, h_dids, evidence)
    s_audit = json.loads(args.sienna_disclosure_audit.read_text(encoding="utf-8"))
    s_stale = sorted(
        int(row["selector"], 16)
        for row in s_audit["findings"]
        if row["surface"] == "application_rdbi" and not row["producer_writes_declared"]
    )
    h_stale = sorted(int(value, 16) for value in h_rdbi["stale_response_dids"])

    # RoutineControl table discovery is independently checked against the exact
    # decoded-layout bases used for policy/descriptor parsing.
    if find_routine_table(sienna, RID.size) != ROUTINE_LAYOUT["sienna"]["rid"]:
        raise ValueError("Sienna RID table discovery/layout disagreement")
    if find_routine_table(target, RID.size) != ROUTINE_LAYOUT["corolla_h"]["rid"]:
        raise ValueError("H RID table discovery/layout disagreement")
    if find_routine_table(sienna, RID_CB.size) != ROUTINE_LAYOUT["sienna"]["callbacks"]:
        raise ValueError("Sienna RoutineControl callback table discovery/layout disagreement")
    if find_routine_table(target, RID_CB.size) != ROUTINE_LAYOUT["corolla_h"]["callbacks"]:
        raise ValueError("H RoutineControl callback table discovery/layout disagreement")
    s_routines = parse_routines(sienna, ROUTINE_LAYOUT["sienna"])
    h_routines = parse_routines(target, ROUTINE_LAYOUT["corolla_h"])
    routine_config_same = all(
        semantic_routine_config(s) == semantic_routine_config(h)
        for s, h in zip(s_routines, h_routines)
    )

    h_routine_by_id = {int(row["rid"], 16): row for row in h_routines}
    def body_is_stub(addr_text: str | None) -> bool:
        if not addr_text:
            return False
        addr = int(addr_text, 16)
        record = evidence[addr]
        return target[addr : addr + record["body_size"]] == SUCCESS_STUB

    no_op_rids = [
        hx(rid, 4) for rid, row in h_routine_by_id.items()
        if body_is_stub(row["precondition_callback"]) and body_is_stub(row["action_callback"])
    ]

    # Target-native semantic pins for the material callback-generation changes.
    h110b = h_routine_by_id[0x110B]
    c110b_pre = evidence[int(h110b["precondition_callback"], 16)]["decompiled_c"]
    c110b_act = evidence[int(h110b["action_callback"], 16)]["decompiled_c"]
    c_b5d92 = evidence[0xB5D92]["decompiled_c"]
    c_b5d2c = evidence[0xB5D2C]["decompiled_c"]
    for needle in ("uRam0002d452 < uRamfebee892", "cRamfebe7e78 == '\\x01'"):
        if needle not in c110b_pre:
            raise ValueError(f"H 110B precondition semantic pin missing: {needle}")
    for needle in ("FUN_000fe18c();", "-0x3988) = 1"):
        if needle not in c110b_act:
            raise ValueError(f"H 110B action semantic pin missing: {needle}")
    if "uRamfebeb32c = 0x11" not in c_b5d92:
        raise ValueError("H 110B lifecycle start cell pin missing")
    for needle in ("cRamfebeb32c == '\\x11'", "FUN_000ff0c4(0x1c)", "cVar3 = 'D'", "cVar3 = -0x78"):
        if needle not in c_b5d2c:
            raise ValueError(f"H 110B lifecycle worker pin missing: {needle}")

    h1009 = h_routine_by_id[0x1009]
    c1009 = evidence[int(h1009["action_callback"], 16)]["decompiled_c"]
    if "FUN_000fe0b0();" not in c1009 or "-0x398f) = 1" not in c1009:
        raise ValueError("H 1009 direct lifecycle action pin missing")
    h1106 = h_routine_by_id[0x1106]
    c1106 = evidence[int(h1106["action_callback"], 16)]["decompiled_c"]
    if "FUN_000fde6c();" not in c1106 or "-0x398c) = 1" not in c1106:
        raise ValueError("H 1106 direct lifecycle action pin missing")

    f181 = evidence[h_by_did[0xF181][2]]["decompiled_c"]
    for needle in ("*param_1 = 2", "iVar2 + 0x20860", "param_1[iVar2 + 0x11]", "&DAT_00017dc0"):
        if needle not in f181:
            raise ValueError(f"H F181 two-record pin missing: {needle}")

    payload = {
        "schema": "corolla-8965H1202000-application-diagnostics-diff-v1",
        "evidence_boundary": "Raw tables/configuration are verified byte evidence. RDBI output bounds and highlighted RoutineControl semantics additionally use the image-bound compact target-native Ghidra evidence set; no OEM names are inferred for H-only states.",
        "images": {
            "sienna": {"sha256": sha256(sienna), "normalization": sienna_norm},
            "corolla_h": {"sha256": sha256(target), "normalization": target_norm},
        },
        "application_service_objects": {
            "sienna_base": hx(s_service_base),
            "corolla_h_base": hx(h_service_base),
            "count": len(SERVICE_SIDS),
            "sid_sequence": [hx(x, 2) for x in SERVICE_SIDS],
            "semantic_policy_shape_same": service_shape_same,
            "sienna": s_services,
            "corolla_h": h_services,
        },
        "readable_dids": {
            "sienna_base": hx(s_did_base),
            "corolla_h_base": hx(h_did_base),
            "sienna_count": len(s_dids),
            "corolla_h_count": len(h_dids),
            "shared_count": len(s_by_did.keys() & h_by_did.keys()),
            "removed": [hx(x, 4) for x in removed],
            "added": [hx(x, 4) for x in added],
            "declared_length_changes": length_changes,
            "corolla_h_unique_producer_count": h_rdbi["unique_producer_count"],
            "corolla_h_rdbi_output_audit": h_rdbi,
            "stale_response_comparison": {
                "sienna_count": len(s_stale),
                "corolla_h_count": len(h_stale),
                "shared": [hx(x, 4) for x in sorted(set(s_stale) & set(h_stale))],
                "sienna_stale_fixed_or_removed_on_h": [hx(x, 4) for x in sorted(set(s_stale) - set(h_stale))],
                "new_h_stale_vs_sienna": [hx(x, 4) for x in sorted(set(h_stale) - set(s_stale))],
            },
            "f181": {
                "sienna_declared_length": s_by_did[0xF181][1],
                "corolla_h_declared_length": h_by_did[0xF181][1],
                "corolla_h_callback": hx(h_by_did[0xF181][2]),
                "corolla_h_semantics": "writes count byte 2 plus two 16-byte software-ID records from CodeFlash 0x20860 and 0x17DC0; failure path fills both records with 0x21",
            },
        },
        "routine_control": {
            "rid_sequence": [hx(x, 4) for x in ROUTINE_RIDS],
            "sienna_rid_table": hx(ROUTINE_LAYOUT["sienna"]["rid"]),
            "corolla_h_rid_table": hx(ROUTINE_LAYOUT["corolla_h"]["rid"]),
            "sienna_callback_table": hx(ROUTINE_LAYOUT["sienna"]["callbacks"]),
            "corolla_h_callback_table": hx(ROUTINE_LAYOUT["corolla_h"]["callbacks"]),
            "decoded_policy_support_and_widths_identical": routine_config_same,
            "corolla_h_noop_precondition_and_action_rids": no_op_rids,
            "material_semantic_differences": {
                "0x1009": "H action directly starts its lifecycle worker and latches status; Sienna's feature/aggregate conditional action and request-results clear logic do not transfer.",
                "0x1106": "H keeps the speed gate and starts the structurally matched multigroup lifecycle worker, but its action no longer conditions start/clear on Sienna's aggregate-health cell.",
                "0x110A": "H precondition/action are exact four-byte success stubs; Sienna internal service-mode-2 action does not transfer.",
                "0x110B": "H is newly active: speed-gated type-1 starts lifecycle cell FEBEB32C=0x11. Periodic worker advances 0x11->0x22, polls operation 0x1C, then reaches 0x44 success or 0x88 abnormal completion. Sienna 110B is no-op/status.",
                "0x110C": "H precondition/action are exact four-byte success stubs; Sienna internal service-mode-3 action does not transfer.",
                "0x110D": "H precondition/action are exact four-byte success stubs; Sienna internal service-mode-4 action does not transfer.",
            },
            "sienna": s_routines,
            "corolla_h": h_routines,
        },
        "decompiler_evidence": {
            "path": display_path(args.target_evidence),
            "sha256": sha256(args.target_evidence.read_bytes()),
            "function_count": evidence_meta["selection"]["function_count"],
        },
    }
    if not service_shape_same:
        raise ValueError("application service-object semantic policy shape differs unexpectedly")
    if added:
        raise ValueError(f"unexpected H-only readable DIDs: {added}")
    if not routine_config_same:
        raise ValueError("RoutineControl decoded policy/support/width configuration differs")

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "out": str(args.out),
        "service_table": hx(h_service_base),
        "did_table": hx(h_did_base),
        "did_count": len(h_dids),
        "removed_dids": [hx(x, 4) for x in removed],
        "h_stale_count": len(h_stale),
        "h_noop_rids": no_op_rids,
    }, indent=2))


if __name__ == "__main__":
    main()
