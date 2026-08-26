#!/usr/bin/env python3
"""Promote exact-H decompiler evidence for the TMS-053 B6/openpilot closure pass."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
IMAGE = REPO / "community/albinoelephant/normalized/8965H1202000_CodeFlash.bin"
OUT = REPO / "data/generated/corolla_8965H1202000_tms053_followup_decompiler_evidence.json"
ENTRIES = [
    # TAUJ0 foreground timing / H LocalRAM initialization
    0x5262C, 0x5F660, 0x5F812, 0x6149A, 0xB8EE4,
    # physical driver-torque acquisition/export family
    0x30384, 0x434D6, 0x434DC, 0x46C4C, 0x47188, 0x4D372, 0x4E6B2, 0x4E8F4,
    0x50B7A, 0x525E6, 0x5389C, 0x5701E, 0x57692,
    # exact-H ICU-S command-5 machinery
    0x81E94, 0x82070, 0x82702, 0x82750, 0x82ED2, 0x83A30,
    # B6 companion consumers not in the older receiver evidence set
    0xCBEEE, 0xCBFCE, 0xCC442, 0xCCF40, 0xCCF8C,
]


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--image", type=Path, default=IMAGE)
    ap.add_argument("--corpus", type=Path, required=True)
    ap.add_argument("--out", type=Path, default=OUT)
    args = ap.parse_args()
    image = args.image.read_bytes()
    if len(image) != 0x100000:
        raise SystemExit(f"expected 1 MiB H CodeFlash, got {len(image):#x}")
    rows: dict[int, dict] = {}
    for line in args.corpus.open():
        row = json.loads(line)
        if row.get("record") == "function":
            rows[int(row["entry_addr"], 16)] = row
    funcs = []
    for entry in ENTRIES:
        row = rows.get(entry)
        if not row or not row.get("decompile_completed") or not row.get("decompiled_c"):
            raise SystemExit(f"missing complete decompile 0x{entry:X}")
        size = int(row["body_size"])
        body = image[entry:entry + size]
        if len(body) != size:
            raise SystemExit(f"function body outside image 0x{entry:X}")
        text = row["decompiled_c"]
        funcs.append({
            "entry": f"0x{entry:08X}",
            "body_size": size,
            "body_sha256": sha(body),
            "decompiled_c_sha256": sha(text.encode()),
            "decompiled_c": text,
            "data_references": row.get("data_references", []),
        })
    rel_image = str(args.image.resolve().relative_to(REPO.resolve())) if args.image.resolve().is_relative_to(REPO.resolve()) else str(args.image)
    rel_corpus = str(args.corpus.resolve().relative_to(REPO.resolve())) if args.corpus.resolve().is_relative_to(REPO.resolve()) else str(args.corpus)
    census_terms = {
        "driver_torque_native_named": "febe7b08",
        "driver_torque_snapshot_named": "febe6554",
        "driver_torque_native_gp": "-0x3cf8",
        "driver_torque_snapshot_gp": "-0x52ac",
        "cooperative_system_mode_named": "febeacbd",
        "cooperative_system_mode_gp": "-0xb43",
    }
    text_census = {}
    for name, term in census_terms.items():
        matches = []
        for entry, row in sorted(rows.items()):
            text = row.get("decompiled_c", "")
            lines = [line.strip() for line in text.splitlines() if term.lower() in line.lower()]
            if lines:
                size = int(row["body_size"])
                matches.append({
                    "entry": f"0x{entry:08X}",
                    "body_size": size,
                    "body_sha256": sha(image[entry:entry + size]),
                    "matching_lines": lines,
                })
        text_census[name] = {"term": term, "match_count": len(matches), "matches": matches}
    driver_names = ("driver_torque_native_named", "driver_torque_snapshot_named", "driver_torque_native_gp", "driver_torque_snapshot_gp")
    driver_entries = sorted({int(m["entry"], 16) for name in driver_names for m in text_census[name]["matches"]})
    acbd_names = ("cooperative_system_mode_named", "cooperative_system_mode_gp")
    acbd_entries = sorted({int(m["entry"], 16) for name in acbd_names for m in text_census[name]["matches"]})

    out = {
        "schema": "corolla-h-tms053-followup-decompiler-evidence-v1",
        "software_id": "8965H1202000",
        "image": {"path": rel_image, "size": len(image), "sha256": sha(image)},
        "source_corpus": {"path": rel_corpus, "sha256": sha(args.corpus.read_bytes())},
        "function_count": len(funcs),
        "functions": funcs,
        "text_census": text_census,
        "driver_torque_direct_reference_union": {
            "entries": [f"0x{x:08X}" for x in driver_entries],
            "match_count": len(driver_entries),
            "target_to_motor_control_cone": ["0x000C8000", "0x000CF000"],
            "entries_inside_control_cone": [f"0x{x:08X}" for x in driver_entries if 0xC8000 <= x < 0xCF000],
        },
        "cooperative_system_mode_direct_reference_union": {
            "entries": [f"0x{x:08X}" for x in acbd_entries],
            "match_count": len(acbd_entries),
            "tx_packer_window": ["0x00046000", "0x00048000"],
            "entries_inside_tx_packer_window": [f"0x{x:08X}" for x in acbd_entries if 0x46000 <= x < 0x48000],
        },
        "boundary": (
            "Target-native exact-H pseudocode/data-reference observations for TAUJ0-CH3 timing, B6 companion consumers, "
            "physical driver-torque acquisition/export, H command-5 machinery, and H LocalRAM startup clears. Every body "
            "is bound to raw 8965H1202000 CodeFlash; whole-program negatives remain bounded to the stated census/query."
        ),
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    print(f"wrote {args.out}: {len(funcs)} functions")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
