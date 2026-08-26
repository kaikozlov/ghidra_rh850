#!/usr/bin/env python3
"""Build the exact H/F FEBE7C58 -> FEBEF000 -> FEBEACBD monitor contract."""
from __future__ import annotations

import argparse
import hashlib
import json
import struct
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
IMAGE = REPO / "community/albinoelephant/normalized/8965H1202000_CodeFlash.bin"
EVIDENCE = REPO / "data/generated/corolla_8965H1202000_power_supply_monitor_decompiler_evidence.json"
FOLLOWUP = REPO / "data/generated/corolla_8965H1202000_tms053_followup_decompiler_evidence.json"
TECH = REPO / "data/generated/corolla_8965H1202000_techstream_correlations.json"
EQUIV = REPO / "data/generated/corolla_8965F1208000_vs_8965H1202000_codeflash_equivalence.json"
OUT = REPO / "data/generated/corolla_8965H1202000_power_supply_monitor_gate.json"
GP = 0xFEBEB800


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def need(text: str, *tokens: str) -> None:
    missing = [token for token in tokens if token not in text]
    if missing:
        raise ValueError("missing decompiler token(s): " + ", ".join(missing))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--image", type=Path, default=IMAGE)
    ap.add_argument("--evidence", type=Path, default=EVIDENCE)
    ap.add_argument("--out", type=Path, default=OUT)
    args = ap.parse_args()
    image = args.image.read_bytes()
    ev = json.loads(args.evidence.read_text())
    follow = json.loads(FOLLOWUP.read_text())
    tech = json.loads(TECH.read_text())
    equiv = json.loads(EQUIV.read_text())
    if len(image) != 0x100000 or sha(image) != ev["image"]["sha256"]:
        raise ValueError("H image/evidence identity drift")
    if ev["function_count"] != 14:
        raise ValueError("monitor evidence count drift")
    funcs = {int(x["entry"], 16): x["decompiled_c"] for x in ev["functions"]}
    follow_funcs = {int(x["entry"], 16): x["decompiled_c"] for x in follow["functions"]}

    # Dispatcher, three classifiers, and the shared output-state setters.
    need(funcs[0x450FC], "DAT_0002b864 == 'Z'", "FUN_00044d84();",
         "DAT_0002b865 == 'Z'", "FUN_00044ec2();", "DAT_0002b866 == 'Z'", "FUN_00044fc4();")
    need(funcs[0x4516A], "uRamfebe65e4 & 3", "cRamfebe7c5f != 'Z'", "uRamfebe63b0",
         "uRamfebe63a6", "uRamfebe63a8", "return 0x22;", "return 0x11;")
    need(funcs[0x451C4], "bRamfebe65e4 & 2", "uRamfebe63b0", "uRamfebe63a6", "return 0x22;")
    need(funcs[0x45212], "bRamfebe65e4 & 1", "uRamfebe63b0", "uRamfebe63a8", "return 0x22;")
    for entry, helper, local, final in (
        (0x44D84, "FUN_0004516a", "febe7c5c", "FUN_0004527a"),
        (0x44EC2, "FUN_000451c4", "febe7c5d", "FUN_0004528a"),
        (0x44FC4, "FUN_00045212", "febe7c5e", "FUN_0004529a"),
    ):
        need(funcs[entry], helper, local, "FUN_00045260();", "FUN_00045272();", final, "FUN_00045268();")
    need(funcs[0x45260], "uRamfebe7c58 = 1;")
    need(funcs[0x45268], "uRamfebe7c58 = 0;", "uRamfebe7c59 = 0;")
    need(funcs[0x45272], "uRamfebe7c58 = 2;")
    need(funcs[0x4527A], "uRamfebe7c58 = 3;", "uRamfebe7c59 = 0x5a;")
    need(funcs[0x4528A], "uRamfebe7c58 = 3;", "uRamfebe7c5a = 0x5a;")
    need(funcs[0x4529A], "uRamfebe7c58 = 3;", "uRamfebe7c5b = 0x5a;")

    # Exact stage copy and normalization.  The tracked corpus represents B8EE4
    # as an 8-byte overlapping prologue and B8EEC as its 2646-byte continuation.
    need(follow_funcs[0x5262C], "uRamfebef000 = uRamfebe7c58;")
    need(funcs[0xB8EEC], "cVar1 = *(char *)(iVar15 + 0x3800);", "cVar1 != '\\0'",
         "cVar1 != '\\x02'", "cVar1 == '\\x03'", "cVar21 = '\\x04';",
         "cVar21 = '\\x01';", "*(char *)(iVar15 + -0xb43) = cVar21;")
    if not (GP - 0x3BA8 == 0xFEBE7C58 and GP + 0x3800 == 0xFEBEF000 and GP - 0xB43 == 0xFEBEACBD):
        raise AssertionError("fixed-GP address arithmetic drift")

    thresholds = struct.unpack_from("<14H", image, 0x2B69A)
    expected_thresholds = (0x1000, 0x0900, 0x1000, 0x0900, 5, 200, 0, 200, 5, 200, 0, 5, 200, 0)
    if thresholds != expected_thresholds:
        raise ValueError(f"power monitor calibration drift: {thresholds!r}")
    feature_bytes = image[0x2B864:0x2B867]
    if feature_bytes != b"\0\0\0":
        raise ValueError(f"power monitor feature bytes drift: {feature_bytes.hex()}")

    # Join only the raw cells that exact H diagnostic producers expose.  The
    # same FEBE63A6 cell has two OEM display rows, so neither label is selected
    # as the unique firmware-variable name.
    rows = tech["ddb_overlap"]["emps_p5"]["monitor_rows"]
    by_callback = {}
    for callback in ("0x488E6", "0x48918", "0x48CFC", "0x48E90"):
        by_callback[callback] = sorted({
            (row["primary_data_id"], row["name"])
            for row in rows if row.get("h_callback") == callback
        })
    expected_labels = {
        "0x488E6": [("0x1061", "IG Power Supply"), ("0x1067", "IG Power Supply (System 2)")],
        "0x48918": [("0x1062", "PIG Power Supply"), ("0x1068", "PIG Power Supply (System 2)")],
        "0x48CFC": [("0x10CA", "Motor 1 Power Supply")],
        "0x48E90": [("0x10FA", "Motor 2 Power Supply")],
    }
    if by_callback != expected_labels:
        raise ValueError(f"Techstream power-supply join drift: {by_callback!r}")
    application_equivalence = equiv["application_equivalence"]
    if not (application_equivalence["identical"] is True
            and application_equivalence["start"] == "0x20000"
            and application_equivalence["end_exclusive"] == "0x100000"):
        raise ValueError("H/F application equivalence drift")

    census = ev["direct_text_reference_census"]
    if {key: census[key]["match_count"] for key in census} != {
        "native_state": 47, "normalized_state": 21, "snapshot_state": 31,
    }:
        raise ValueError("direct-reference census drift")

    out = {
        "schema": "corolla-8965H1202000-power-supply-monitor-gate-v1",
        "software_id": "8965H1202000",
        "applies_to": ["8965H1202000", "8965F1208000"],
        "sources": {
            "codeflash": {"path": str(args.image.relative_to(REPO)), "sha256": sha(image)},
            "decompiler_evidence": {"path": str(args.evidence.relative_to(REPO)), "sha256": sha(args.evidence.read_bytes()), "function_count": ev["function_count"]},
            "tms053_followup_evidence": {"path": str(FOLLOWUP.relative_to(REPO)), "sha256": sha(FOLLOWUP.read_bytes())},
            "techstream_correlations": {"path": str(TECH.relative_to(REPO)), "sha256": sha(TECH.read_bytes())},
            "hf_application_equivalence": {"path": str(EQUIV.relative_to(REPO)), "sha256": sha(EQUIV.read_bytes()), "region": application_equivalence},
        },
        "state_chain": {
            "native_state": "0xFEBE7C58",
            "snapshot_copy": {"entry": "0x0005262C", "destination": "0xFEBEF000"},
            "normalizer": {"entry": "0x000B8EE4", "tracked_body_continuation": "0x000B8EEC"},
            "normalized_output": "0xFEBEACBD",
            "mapping": {"0": 0, "2": 2, "3": 4, "other_nonzero": 1},
            "exact_fixed_gp_arithmetic": {
                "gp": "0xFEBEB800", "native": "GP-0x3BA8", "snapshot": "GP+0x3800", "normalized": "GP-0x0B43"
            },
            "direct_text_reference_census": {
                key: {"address": value["address"], "match_count": value["match_count"], "terms": value["terms"]}
                for key, value in census.items()
            },
        },
        "monitor_dispatch": {
            "entry": "0x000450FC",
            "feature_bytes": {"address": "0x0002B864", "raw_hex": feature_bytes.hex(), "meaning": "zero selects each monitor; 0x5A bypasses and clears the shared state"},
            "channels": [
                {
                    "monitor": "0x00044D84", "classifier": "0x0004516A", "local_state": "0xFEBE7C5C", "terminal_marker": "0xFEBE7C59",
                    "supply_inputs": ["0xFEBE63B0", "0xFEBE63A6", "0xFEBE63A8"],
                    "predicate_boundary": "common IG-window condition plus both A6 and A8 below the low threshold or both above the high threshold; also gated by FEBE63A4, FEBE65E4 bits[1:0], and FEBE7C5F",
                },
                {
                    "monitor": "0x00044EC2", "classifier": "0x000451C4", "local_state": "0xFEBE7C5D", "terminal_marker": "0xFEBE7C5A",
                    "supply_inputs": ["0xFEBE63B0", "0xFEBE63A6"],
                    "predicate_boundary": "common IG-window condition plus A6 outside the low/high window; also gated by FEBE63A4, FEBE65E4 bit1, and FEBE7C5F",
                },
                {
                    "monitor": "0x00044FC4", "classifier": "0x00045212", "local_state": "0xFEBE7C5E", "terminal_marker": "0xFEBE7C5B",
                    "supply_inputs": ["0xFEBE63B0", "0xFEBE63A8"],
                    "predicate_boundary": "common IG-window condition plus A8 outside the low/high window; also gated by FEBE63A4, FEBE65E4 bit0, and FEBE7C5F",
                },
            ],
            "classifier_codes": {"0x11": "non-fault classifier result", "0x22": "out-of-window classifier result", "0x44": "disabled/not-ready classifier result"},
            "shared_state_writes": {"0": "0x00045268", "1": "0x00045260", "2": "0x00045272", "3": ["0x0004527A", "0x0004528A", "0x0004529A"]},
            "calibration": {"address": "0x0002B69A", "raw_hex": image[0x2B69A:0x2B6B6].hex(), "u16_le": list(thresholds)},
        },
        "diagnostic_input_join": {
            "0xFEBE63B0": {"producer": "0x000488E6", "rows": [{"did": did, "name": name} for did, name in by_callback["0x488E6"]]},
            "0xFEBE63A6": {"producers": ["0x00048918", "0x00048CFC"], "rows": [{"did": did, "name": name} for cb in ("0x48918", "0x48CFC") for did, name in by_callback[cb]]},
            "0xFEBE63A8": {"producer": "0x00048E90", "rows": [{"did": did, "name": name} for did, name in by_callback["0x48E90"]]},
            "boundary": "The exact diagnostic producers identify a power-supply-monitor subsystem. FEBE63A6 is exposed under both PIG and Motor 1 labels, so the artifact does not choose one as its unique variable name. No OEM names are assigned to FEBE63A4, FEBE65E4, FEBE7C5F, the three local monitor states, FEBE7C58, FEBEF000, or FEBEACBD.",
        },
        "classification": {
            "recovered": "FEBE7C58 is a shared graded power-supply receive-validity/freeze state; FEBEF000 is its scheduler snapshot; FEBEACBD is its normalized downstream gate code.",
            "firmware_effect": "Native values 2/3 suppress ordinary generated receive-unpacker updates under the direct textual census; downstream cooperative selection requires FEBEACBD == 0.",
            "not_established": ["literal OEM name for any of the three state bytes", "physical units of the raw supply cells", "wall-clock debounce durations", "a wire-visible FEBEACBD feedback field", "arbitrary computed-pointer aliases outside the census"],
            "distinct_from_b6_loss": "B6 missing-message loss remains the separate FEBEADB9 -> FEBEC26D path.",
        },
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
