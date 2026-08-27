#!/usr/bin/env python3
"""Build the exact-F33 0x394 DEM/classifier fault-status contract."""
from __future__ import annotations

import argparse
import collections
import hashlib
import json
import struct
from pathlib import Path
from corolla_h_constants import CODEFLASH as H_CODEFLASH

from camry_f33_corpus import IMAGE, IMAGE_SHA256

REPO = Path(__file__).resolve().parents[1]
EVID = REPO / "data/generated/camry_8965F3307000_fault_status_decompiler_evidence.json"
TX = REPO / "data/generated/camry_8965F3307000_tss3_opendbc_port.json"
H_TECH = REPO / "data/generated/corolla_8965H1202000_techstream_correlations.json"
H_IMAGE = H_CODEFLASH
OUT = REPO / "data/generated/camry_8965F3307000_fault_status.json"
H_IMAGE_SHA256 = "0b47bdc1217835c839e3543e52eab40eb793650a9c159e46f6a9b365ea41a67f"
STATE_TABLE = 0x2A19C
EVENT_TABLE = 0x2FC50
DTC_TABLE = 0x30850
CAL = 0x30E40
EVENT_COUNT = 0x180
EVENT_REC = 8
STATE_ROWS = 17
NESTED_OPENDDBC_COMMIT = "0d5773bd393bbf3d4109728171d2390b60fcde16"
PARENT_OPENPILOT_COMMIT = "191aeb43df3fb72f3264209be1aad57b9ca42e2d"


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def need(cond: object, msg: str) -> None:
    if not cond:
        raise ValueError(msg)


def token(funcs: dict[int, dict], entry: int, *tokens: str) -> str:
    need(entry in funcs, f"missing decompiler function 0x{entry:08X}")
    text = funcs[entry]["decompiled_c"]
    for item in tokens:
        need(item in text, f"0x{entry:08X} missing token {item!r}")
    return text


def dtc_vocab_by_index(htech: dict) -> dict[int, dict]:
    out: dict[int, dict] = {}
    classes = htech["fault_event_class_catalog"]["classes"]
    for cls in classes.values():
        for event in cls["events"]:
            dtc = event.get("dtc")
            if dtc is None:
                continue
            idx = int(dtc["h_dtc_index"])
            slim = {
                "dtc_index": idx,
                "packed_dtc": dtc["packed_dtc"],
                "techstream_code": dtc["techstream_code"],
                "techstream_description": dtc["techstream_description"],
                "techstream_failure": dtc["techstream_failure"],
            }
            if idx in out:
                need(out[idx] == slim, f"Techstream DTC index {idx} maps inconsistently")
            out[idx] = slim
    return out


def build() -> dict:
    image = IMAGE.read_bytes()
    h_image = H_IMAGE.read_bytes()
    evid = json.loads(EVID.read_text(encoding="utf-8"))
    tx = json.loads(TX.read_text(encoding="utf-8"))
    htech = json.loads(H_TECH.read_text(encoding="utf-8"))
    need(len(image) == 0x100000 and sha(image) == IMAGE_SHA256, "exact F33 image drift")
    need(len(h_image) == 0x100000 and sha(h_image) == H_IMAGE_SHA256, "H reference identity drift")
    need(evid["schema"] == "camry-8965f3307000-fault-status-decompiler-evidence-v1", "fault evidence schema drift")
    need(evid["image"]["sha256"] == IMAGE_SHA256 and evid["function_count"] == 10, "fault evidence target/count drift")
    need(tx["schema"] == "camry-8965f3307000-tss3-opendbc-port-v1", "F33 Tx contract drift")

    funcs = {int(row["entry"], 16): row for row in evid["functions"]}
    need(len(funcs) == 10, "fault evidence duplicate/missing functions")
    for entry, row in funcs.items():
        need(sha(image[entry:entry + int(row["body_size"])]) == row["body_sha256"], f"body hash drift 0x{entry:08X}")

    # Target-native classifier and aging topology.
    token(funcs, 0x50FC8, "puVar1 + -0x3546", "puVar1 + -0x3544", "puVar1 + -0x3542",
          "puVar1 + -0x3540", "puVar1 + -0x353e", "puVar1 + -0x353c",
          "puVar1 + -0x353a", "puVar1 + -0x3538", "puVar1 + -0x3530")
    token(funcs, 0x510B6, "DAT_febe6764", "& 0x8000", "FUN_00050fc8(2)")
    token(funcs, 0x5110A, "DAT_febee8b0", "DAT_00030e46 <= uVar1", "param_4 < uVar2")
    token(funcs, 0x5116C, "DAT_00030e44", "puVar3 + -0x3532")
    token(funcs, 0x511B6, "DAT_00030e40", "DAT_00030e42", "FUN_0005116c")
    classifier = token(funcs, 0x512E4, "FUN_000510b6", "FUN_00051266", "DAT_00030e48", "DAT_00030e4a",
                       "(&DAT_0002a19c)[iVar21]", "puVar19[-0x3560]", "uVar18 = 6", "uVar18 = 7",
                       "uVar18 = 8", "uVar18 = 9", "uVar18 = 10", "uVar18 = 0xb", "uVar18 = 0xc",
                       "uVar18 = 0xd", "uVar18 = 0xe", "uVar18 = 0xf", "uVar18 = 0x10")
    need("uVar18 = 0;" not in classifier, "unexpected explicit state-0 assignment; deepest fallthrough semantics changed")
    token(funcs, 0x51592, "DAT_00030e40", "DAT_00030e42", "DAT_00030e44")

    # Exact target state table and wire projection.
    state_raw = image[STATE_TABLE:STATE_TABLE + STATE_ROWS * 5]
    rows = [list(state_raw[i * 5:(i + 1) * 5]) for i in range(STATE_ROWS)]
    expected_rows = [
        [0,0,0,0,0], [4,3,0,0,0], [4,7,0,0,0], [5,3,0,0,0], [4,3,0,0,0], [1,1,0,0,0],
        [3,3,2,1,2], [3,3,2,1,0], [6,3,3,0,2], [6,3,3,0,0], [3,7,1,1,1], [3,7,4,1,1],
        [6,7,7,0,1], [6,7,6,0,1], [6,7,5,0,1], [2,2,0,0,0], [4,7,0,0,0],
    ]
    need(rows == expected_rows, f"F33 0x394 state table drift: {rows}")
    need(state_raw == h_image[0x29D54:0x29D54 + STATE_ROWS * 5], "F33/H state-table bytes are no longer identical")
    projection: dict[tuple[int,int,int,int], list[int]] = collections.defaultdict(list)
    for state, row in enumerate(rows):
        projection[(row[4], row[1], row[2], row[3])].append(state)
    projection_rows = [
        {"wire": list(key), "states": states, "unique": len(states) == 1}
        for key, states in sorted(projection.items())
    ]
    need(projection[(0,0,0,0)] == [0], "all-zero 0x394 projection no longer uniquely state0")
    need(projection[(0,3,0,0)] == [1,3,4] and projection[(0,7,0,0)] == [2,16], "expected lossy projections drift")

    # Target-native calibration words.  0x30E46 is the primary-clear enable age
    # consumed by 0x5110A; 0x30E48/4A are the two startup holds in 0x512E4.
    cal = [struct.unpack_from("<H", image, CAL + i)[0] for i in range(0, 14, 2)]
    need(cal == [200, 200, 600, 22170, 200, 200, 1000], f"F33 classifier calibration drift: {cal}")

    # Exact F33 event-class census and DTC-index fields.
    events = [image[EVENT_TABLE + i * EVENT_REC:EVENT_TABLE + (i + 1) * EVENT_REC] for i in range(EVENT_COUNT)]
    h_events = [h_image[0x2B988 + i * EVENT_REC:0x2B988 + (i + 1) * EVENT_REC] for i in range(EVENT_COUNT)]
    class_counts = collections.Counter(rec[1] for rec in events if rec[1])
    expected_counts = {0x01:8, 0x02:34, 0x04:1, 0x08:1, 0x0F:1, 0x10:171, 0x20:16, 0x40:1, 0x80:7}
    need(dict(sorted(class_counts.items())) == expected_counts, f"F33 DEM class histogram drift: {class_counts}")
    changed = []
    for i, (old, new) in enumerate(zip(h_events, events)):
        if old != new:
            changed.append({
                "event": f"0x{i:04X}",
                "h_raw": old.hex(),
                "f33_raw": new.hex(),
                "changed_offsets": [j for j, (a,b) in enumerate(zip(old,new)) if a != b],
            })
    need(len(changed) == 31, f"F33/H event-table changed-record count drift: {len(changed)}")
    class_changes = [x for x in changed if bytes.fromhex(x["h_raw"])[1] != bytes.fromhex(x["f33_raw"])[1]]
    dtc_changes = [x for x in changed if bytes.fromhex(x["h_raw"])[2] != bytes.fromhex(x["f33_raw"])[2]]
    need([x["event"] for x in class_changes] == ["0x0085", "0x0088"], "F33 DEM class-change events drift")
    need([x["event"] for x in dtc_changes] == ["0x00AC"], "F33 DEM DTC-index-change events drift")

    # Exact DTC table relocation. Every DTC record still referenced by F33 is
    # byte-identical to H, allowing the pinned EMPS_P5 vocabulary to be joined
    # by exact packed-DTC record rather than by vehicle-name assumption.
    f33_dtc_indexes = sorted({rec[2] for rec in events if rec[2]})
    need(f33_dtc_indexes and max(f33_dtc_indexes) == 133, "F33 DTC index range drift")
    vocab = dtc_vocab_by_index(htech)
    dtc_rows = {}
    for idx in f33_dtc_indexes:
        f33_raw = image[DTC_TABLE + idx * 8:DTC_TABLE + (idx + 1) * 8]
        h_raw = h_image[0x2C588 + idx * 8:0x2C588 + (idx + 1) * 8]
        need(f33_raw == h_raw, f"F33 referenced DTC row {idx} no longer matches pinned H/EMPS_P5 join")
        if idx in vocab:
            dtc_rows[idx] = {**vocab[idx], "raw_hex": f33_raw.hex(), "record_address": f"0x{DTC_TABLE + idx*8:08X}"}

    classes: dict[str, dict] = {}
    for class_code, count in sorted(class_counts.items()):
        rows_for_class = []
        for event_id, rec in enumerate(events):
            if rec[1] != class_code:
                continue
            idx = rec[2]
            rows_for_class.append({
                "event": f"0x{event_id:04X}",
                "event_record_address": f"0x{EVENT_TABLE + event_id*8:08X}",
                "event_raw_hex": rec.hex(),
                "dtc_index": idx,
                "dtc": dtc_rows.get(idx),
            })
        classes[f"0x{class_code:02X}"] = {
            "event_count": count,
            "dtc_indexed_count": sum(bool(row["dtc_index"]) for row in rows_for_class),
            "events": rows_for_class,
        }

    # The two H thermal DTC events are explicitly declassified on F33 while
    # retaining their DTC indexes; they therefore do not drive F33 state10.
    thermal = []
    for event_id in (0x85, 0x88):
        rec = events[event_id]
        idx = rec[2]
        need(rec[1] == 0 and idx in dtc_rows, f"F33 thermal declassification drift at event 0x{event_id:04X}")
        thermal.append({"event": f"0x{event_id:04X}", "f33_class": 0, "dtc": dtc_rows[idx]})
    need(events[0xAC][1] == 0 and events[0xAC][2] == 0, "F33 event 0x00AC disable drift")
    h_idx120 = h_image[0x2C588 + 120*8:0x2C590 + 120*8]
    f_idx120 = image[DTC_TABLE + 120*8:DTC_TABLE + 121*8]
    need(h_idx120.hex() == "8710d10001000000" and f_idx120.hex() == "8710d10000000000", "DTC index120 disable evidence drift")

    state_roles = {
        "0": "deepest clear/normal classifier path after all recovered class/operational predicates pass",
        "1": "startup/settling hold A",
        "2": "startup/settling hold B",
        "3": "internal input invalid/unavailable predicate",
        "4": "retained table row; not directly selected by recovered classifier body",
        "5": "retained table row; not directly selected by recovered classifier body",
        "6": "class-0x02 primary active with secondary latch bit0 set",
        "7": "class-0x02 primary active after secondary latch bit0 clears",
        "8": "class-0x04 primary active with secondary latch bit1 set",
        "9": "class-0x04 primary active after secondary latch bit1 clears",
        "10": "class-0x10 fault family",
        "11": "class-0x20/F0-compatible aggregate branch plus independent internal source",
        "12": "class-0x40 fault branch",
        "13": "class-0x08 branch when operational helper permits",
        "14": "class-0x0F branch when operational helper permits",
        "15": "special operating state selected by distinct operational predicate",
        "16": "fallback/not-normal operational inhibit branch; class-0x80 blocks deepest state0 path",
    }

    return {
        "schema": "camry-8965f3307000-fault-status-v1",
        "target": {"software_id": "8965F3307000", "codeflash_sha256": IMAGE_SHA256},
        "classifier": {
            "entry": "0x000512E4",
            "class_accumulator": "0x00050FC8",
            "class2_additional_injection": "0x000510B6",
            "operational_helper": "0x000510E0",
            "state11_additional_source": "0x00051266",
            "invalid_unavailable_predicate": "0x00051208",
            "init": "0x00051592",
            "state_table": f"0x{STATE_TABLE:08X}",
            "state_table_rows": rows,
            "state_roles": state_roles,
        },
        "wire": {
            "can_id": "0x394",
            "length": 3,
            "projection_order": ["table_column_4", "table_column_1", "table_column_2", "table_column_3"],
            "projection_fields": tx["status_carriers"]["0x394"]["fields"],
            "projection_to_state_candidates": projection_rows,
            "unique_state0_projection": [0,0,0,0],
            "ambiguous_projections": [
                {"wire": [0,3,0,0], "states": [1,3,4]},
                {"wire": [0,7,0,0], "states": [2,16]},
            ],
            "boundary": "The wire projection is lossy. Expose candidate states; do not fabricate a unique state for ambiguous tuples.",
        },
        "aging": {
            "calibration_address": f"0x{CAL:08X}",
            "raw_u16": cal,
            "primary_latch_bank_355d_age": 200,
            "aggregate_latch_bank_355c_age": 200,
            "class2_class4_secondary_latch_age": 600,
            "primary_clear_enable_age": 22170,
            "startup_hold_a": 200,
            "startup_hold_b": 200,
            "unnamed_following_word": 1000,
            "comparison_to_h": {"h_primary_clear_enable_age": 17736, "f33_primary_clear_enable_age": 22170},
            "boundary": "These are exact classifier/latch counter thresholds. No wall-clock or openpilot temporary/permanent meaning is inferred from the counters alone.",
        },
        "dem": {
            "event_table": f"0x{EVENT_TABLE:08X}",
            "event_count": EVENT_COUNT,
            "record_size": EVENT_REC,
            "class_byte_offset": 1,
            "dtc_index_offset": 2,
            "class_counts": {f"0x{k:02X}": v for k,v in sorted(class_counts.items())},
            "classes": classes,
            "comparison_to_h": {
                "changed_record_count": len(changed),
                "changed_records": changed,
                "class_removed_events": ["0x0085", "0x0088"],
                "dtc_index_removed_events": ["0x00AC"],
                "thermal_dtcs_removed_from_class_0x10": thermal,
            },
        },
        "dtc": {
            "table": f"0x{DTC_TABLE:08X}",
            "referenced_index_count": len(f33_dtc_indexes),
            "referenced_indexes": f33_dtc_indexes,
            "referenced_rows_identical_to_h": True,
            "index_120_disabled": {"h_raw": h_idx120.hex(), "f33_raw": f_idx120.hex()},
            "vocabulary_join": (
                "For every DTC index still referenced by F33, the exact 8-byte F33 DTC record equals the pinned H record. "
                "Toyota EMPS_P5 names are therefore joined by identical packed-DTC bytes, not transferred by variant assumption."
            ),
        },
        "passive_opendbc_integration": {
            "nested_opendbc_commit": NESTED_OPENDDBC_COMMIT,
            "parent_kai_openpilot_commit": PARENT_OPENPILOT_COMMIT,
            "behavior": "decode exact-F33 0x394 wire tuples into candidate internal states; unique tuple yields a unique internal-state observer only",
            "public_fault_flags_changed": False,
            "production_output_authorized": False,
            "full_gate": "4077 passed / 719 skipped plus ruff, ty, codespell, cpplint, MISRA",
        },
        "openpilot_policy": {
            "internal_state_exposure": "safe as a diagnostic/status candidate set when 0x394 is present",
            "state0": "unique deepest clear/normal internal classifier state; not independently a Ready authorization bit",
            "steerFaultTemporary": "unresolved policy mapping",
            "steerFaultPermanent": "unresolved policy mapping",
            "reason": (
                "Toyota's internal DEM class/latch distinction does not define openpilot temporary/permanent policy. "
                "Relay-correct asserted/recovery capture or an independent policy proof is still required."
            ),
            "production_output_authorized": False,
        },
        "sources": {
            "codeflash": {"path": str(IMAGE.relative_to(REPO)), "sha256": IMAGE_SHA256},
            "decompiler_evidence": {"path": str(EVID.relative_to(REPO)), "sha256": sha(EVID.read_bytes())},
            "tx_contract": {"path": str(TX.relative_to(REPO)), "sha256": sha(TX.read_bytes())},
            "h_techstream_vocabulary": {"path": str(H_TECH.relative_to(REPO)), "sha256": sha(H_TECH.read_bytes())},
        },
        "boundary": (
            "Exact-F33 firmware closes 0x394 classifier structure, wire-state candidate mapping, DEM class census, DTC-record join, and aging constants. "
            "It does not convert those OEM internal states into openpilot temporary/permanent faults or prove 0x394 availability on the final relay-correct route."
        ),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", type=Path, default=OUT)
    args = ap.parse_args()
    obj = build()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"wrote {args.out}: {sum(obj['dem']['class_counts'].values())} classified events")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
