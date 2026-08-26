#!/usr/bin/env python3
"""Build the exact H/F 0x394 DEM-class/fault-state contract."""
from __future__ import annotations

import argparse
import hashlib
import json
import struct
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
IMAGE = REPO / "community/albinoelephant/normalized/8965H1202000_CodeFlash.bin"
EVID = REPO / "data/generated/corolla_8965H1202000_openpilot_state_bridge_decompiler_evidence.json"
TECH = REPO / "data/generated/corolla_8965H1202000_techstream_correlations.json"
EQUIV = REPO / "data/generated/corolla_8965F1208000_vs_8965H1202000_codeflash_equivalence.json"
OUT = REPO / "data/generated/corolla_hf_fault_state_contract.json"


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def need(text: str, *tokens: str) -> None:
    missing = [t for t in tokens if t not in text]
    if missing:
        raise ValueError("missing decompiler token(s): " + ", ".join(missing))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", type=Path, default=OUT)
    args = ap.parse_args()

    image = IMAGE.read_bytes()
    evid_b = EVID.read_bytes(); evid = json.loads(evid_b)
    tech_b = TECH.read_bytes(); tech = json.loads(tech_b)
    equiv_b = EQUIV.read_bytes(); equiv = json.loads(equiv_b)
    if len(image) != 0x100000 or sha(image) != "0b47bdc1217835c839e3543e52eab40eb793650a9c159e46f6a9b365ea41a67f":
        raise ValueError("exact H image identity drift")
    app = equiv["application_equivalence"]
    if not (app["identical"] and app["different_bytes"] == 0 and app["start"] == "0x20000" and app["end_exclusive"] == "0x100000"):
        raise ValueError("H/F application equivalence drift")

    funcs = {int(x["entry"], 16): x["decompiled_c"] for x in evid["functions"]}
    for entry in (0x46E96, 0x47ADA, 0x4B692, 0x4B780, 0x4B7D4, 0x4B836, 0x4B880, 0x4B8D2, 0x4B930, 0x4B9AE):
        if entry not in funcs:
            raise ValueError(f"missing state-bridge decompiler evidence 0x{entry:08X}")
    need(funcs[0x4B692], "param_1 == '\\x02'", "param_1 != '\\x04'", "param_1 == '\\b'", "param_1 == '\\x0f'", "param_1 == '\\x10'", "param_1 == ' '", "param_1 == '@'", "param_1 == -0x80", "param_1 != -0x10")
    need(funcs[0x4B780], "FUN_0004b692(2);", "uRamfebe65e4 & 0x8000")
    need(funcs[0x4B880], "DAT_0002cb8c", "DAT_0002cb8e", "FUN_0004b836();")
    need(funcs[0x4B836], "DAT_0002cb90", "iVar3 + -0x38a3")
    need(funcs[0x4B7D4], "DAT_0002cb92 <= uVar1")
    need(funcs[0x4B930], "bRamfebe7f5c = bRamfebe7f5c | 0x20")
    need(funcs[0x4B9AE], "uVar18 = 7;", "uVar18 = 6;", "uVar18 = 9;", "uVar18 = 8;", "uVar18 = 10;", "uVar18 = 0xb;", "uVar18 = 0xc;", "uVar18 = 0xd;", "uVar18 = 0xe;", "uVar18 = 0x10;")
    need(funcs[0x46E96], "uRamfebe7dd5 = uRamfebe7f65;", "uRamfebe7dd6 = uRamfebe7f62;", "uRamfebe7dd7 = uRamfebe7f63;", "uRamfebe7dd9 = uRamfebe7f64;")
    need(funcs[0x47ADA], "FUN_000764ec(0x27,0x25,2,6", "FUN_000764ec(0x28,0x25,3,3", "FUN_000764ec(0x29,0x26,3,1", "FUN_000764ec(0x2a,0x26,1,0")

    rows = [list(image[0x29D54 + i * 5:0x29D59 + i * 5]) for i in range(17)]
    calibration = {
        "class2_primary_age": struct.unpack_from("<H", image, 0x2CB8C)[0],
        "class4_primary_age": struct.unpack_from("<H", image, 0x2CB8E)[0],
        "class2_class4_secondary_age": struct.unpack_from("<H", image, 0x2CB90)[0],
        "primary_clear_enable_age": struct.unpack_from("<H", image, 0x2CB92)[0],
        "startup_hold_a": struct.unpack_from("<H", image, 0x2CB94)[0],
        "startup_hold_b": struct.unpack_from("<H", image, 0x2CB96)[0],
    }
    if calibration != {
        "class2_primary_age": 200,
        "class4_primary_age": 200,
        "class2_class4_secondary_age": 600,
        "primary_clear_enable_age": 17736,
        "startup_hold_a": 200,
        "startup_hold_b": 200,
    }:
        raise ValueError(f"0x394 aging calibration drift: {calibration!r}")

    catalog = tech["fault_event_class_catalog"]
    expected_counts = {"0x01": 8, "0x02": 34, "0x04": 1, "0x08": 1, "0x0F": 1, "0x10": 173, "0x20": 16, "0x40": 1, "0x80": 7}
    if catalog["class_counts"] != expected_counts:
        raise ValueError(f"fault class census drift: {catalog['class_counts']!r}")
    if "0xF0" in catalog["classes"]:
        raise ValueError("current exact-H event table unexpectedly populated class 0xF0")

    def named(class_code: str) -> list[dict]:
        out: list[dict] = []
        seen: set[tuple] = set()
        for row in catalog["classes"][class_code]["events"]:
            d = row["dtc"]
            if d is None:
                continue
            key = (d["techstream_code"], d["techstream_description"], d["techstream_failure"])
            if key in seen:
                continue
            seen.add(key)
            out.append({"code": key[0], "description": key[1], "failure": key[2]})
        return out

    class_to_state = {
        "0x02": {
            "states": [6, 7],
            "selection": "class-2 primary active => state 6 while secondary bit FEBE7F5D[0] is set, else state 7",
            "lifetime": "primary latch uses calibration 200 and additionally requires FEBEE8B0 >= 17736 before clearing; secondary latch uses calibration 600",
        },
        "0x04": {
            "states": [8, 9],
            "selection": "class-4 primary active => state 8 while secondary bit FEBE7F5D[1] is set, else state 9",
            "lifetime": "primary latch uses calibration 200 and additionally requires FEBEE8B0 >= 17736 before clearing; shared secondary latch uses calibration 600",
        },
        "0x10": {"states": [10], "selection": "dedicated class-0x10 counter/bit branch"},
        "0x20": {"states": [11], "selection": "class-0x20 counter/aggregate bit is one direct state-11 cause"},
        "0xF0": {"states": [11], "selection": "supported by 0x4B692 and the state-11 branch, but no exact-H event-table row currently carries class 0xF0"},
        "0x40": {"states": [12], "selection": "dedicated class-0x40 counter/bit branch"},
        "0x08": {"states": [13], "selection": "class-0x08 counter/bit selects state 13 when the additional 0x4B7AA condition permits; otherwise the classifier can fall through to state 16"},
        "0x0F": {"states": [14], "selection": "class-0x0F counter/bit selects state 14 when the additional 0x4B7AA condition permits; otherwise the classifier can fall through to state 16"},
        "0x80": {"states": [16], "selection": "class-0x80 counter blocks the deepest state-0 normal path; state 16 is a general fallback and is not unique to class 0x80"},
        "0x01": {"states": [], "selection": "populated in the exact-H event table but not consumed by recovered accumulator 0x4B692"},
    }

    named_counts = {c: len(named(c)) for c in ("0x01", "0x02", "0x10", "0x20")}
    if named_counts != {"0x01": 6, "0x02": 11, "0x10": 50, "0x20": 6}:
        raise ValueError(f"named DTC family counts drift: {named_counts!r}")

    out = {
        "schema": "corolla-hf-0x394-fault-state-contract-v1",
        "software_ids": ["8965H1202000", "8965F1208000"],
        "sources": {
            "h_codeflash": {"path": str(IMAGE.relative_to(REPO)), "sha256": sha(image)},
            "state_bridge_decompiler_evidence": {"path": str(EVID.relative_to(REPO)), "sha256": sha(evid_b)},
            "techstream_correlations": {"path": str(TECH.relative_to(REPO)), "sha256": sha(tech_b)},
            "hf_application_equivalence": {"path": str(EQUIV.relative_to(REPO)), "sha256": sha(equiv_b), "application": app},
        },
        "wire": {
            "can_id": "0x394",
            "length": 3,
            "classifier_entry": "0x0004B9AE",
            "state_table": "0x00029D54",
            "state_table_rows": rows,
            "projection": {
                "B1[7:6]": "table column 4 via FEBE7F65 -> FEBE7DD5",
                "B1[5:3]": "table column 1 via FEBE7F62 -> FEBE7DD6",
                "B2[3:1]": "table column 2 via FEBE7F63 -> FEBE7DD7",
                "B2[0]": "table column 3 via FEBE7F64 -> FEBE7DD9",
                "not_on_0x394": "table column 0 is staged through FEBE7F66/FEBE7DD2; FEBE7DDA is separate",
            },
        },
        "dem": {
            "class_accumulator": "0x0004B692",
            "event_table": catalog["event_table"],
            "event_count_scanned": catalog["event_count_scanned"],
            "class_counts": catalog["class_counts"],
            "class_to_state": class_to_state,
            "class2_additional_injection": "0x4B780 injects class 0x02 when FEBE65E4 bit15 is set",
            "state11_additional_source": "0x4B930 can set the shared 0x20 aggregate bit from three internal 0x22-valued conditions; state 11 is therefore not exclusively class-0x20/F0 DTC events",
        },
        "aging": {
            "calibration_address": "0x0002CB8C",
            **calibration,
            "boundary": "These are exact classifier/latch counter thresholds. Counter wall-clock meaning is not asserted here, and the paired states are not renamed temporary/permanent.",
        },
        "named_dtc_families": {
            "class_0x01_no_direct_394_accumulator_effect": named("0x01"),
            "class_0x02_states_6_7": named("0x02"),
            "class_0x10_state_10": named("0x10"),
            "class_0x20_state_11": named("0x20"),
        },
        "internal_only_classes": {
            c: {"event_count": catalog["classes"][c]["event_count"], "dtc_indexed_count": catalog["classes"][c]["dtc_indexed_count"]}
            for c in ("0x04", "0x08", "0x0F", "0x40", "0x80")
        },
        "openpilot_boundary": {
            "static_closure": "states 6-14 are now partitioned by exact DEM class family and named Toyota DTC families where the H event has a DTC index; states 6/7 and 8/9 also have exact latch-selection/aging structure",
            "steerFaultTemporary": "unresolved policy mapping",
            "steerFaultPermanent": "unresolved policy mapping",
            "reason": "Toyota's internal class/latch distinction does not define openpilot's temporary/permanent contract. A live induced-fault/recovery sequence or an independently proved policy mapping is still required before assigning those labels.",
        },
        "evidence_boundary": (
            "All class/state selection logic and aging constants are exact-H firmware-static and transfer byte-for-byte to F. "
            "Toyota DTC names come from the pinned EMPS_P5 Techstream table via the committed Corolla Techstream correlation catalog. "
            "Classes with DTC index 0 remain internal/no-named-DTC. State 16 is a general fallback, not a unique class-0x80 code."
        ),
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    print(f"wrote {args.out}: {sum(catalog['class_counts'].values())} classified DEM events")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
