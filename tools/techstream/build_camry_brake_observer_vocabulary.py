#!/usr/bin/env python3
"""Build the compact current-GTS+ category-435 observer vocabulary proof."""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

from techstream_paths import gts_db_root, resolve_gts_root

REPO = Path(__file__).resolve().parents[2]
LIVE = REPO / "data/generated/camry_2026_nrtd_p5.json"
DEFAULT_OUT = REPO / "data/generated/gtsplus_2026/camry_brake_observer_vocabulary.json"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def gts_json(*args: str) -> Any:
    proc = subprocess.run(
        [str(REPO / "tools/gts"), *args, "--json"],
        cwd=REPO,
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        raise RuntimeError(f"tools/gts {' '.join(args)} failed: {proc.stderr[-500:]}")
    return json.loads(proc.stdout)


def only_row(did: int, expected_name: str) -> dict[str, Any]:
    rows = gts_json("did", "ABS_P5", f"0x{did:04X}")
    if len(rows) != 1 or rows[0]["name"] != expected_name:
        raise ValueError(f"ABS_P5 0x{did:04X} identity drift: {rows}")
    return rows[0]


def observer(row: dict[str, Any], interpretation: str) -> dict[str, Any]:
    info = row["signal_info"]
    return {
        "did": f"0x{row['primary_did']:04X}",
        "alternate_did": f"0x{row['alternate_did']:04X}" if row["alternate_did"] else None,
        "name": row["name"],
        "monitor_key": row["monitor_key"],
        "table": row["table"],
        "mirrored_tables": row["tables"],
        "bit_range_inclusive": [row["bit_start"], row["bit_end"]],
        "width_bits": info["bit_width"],
        "width_bytes": (info["bit_width"] + 7) // 8,
        "physical_data_key": row["physical_data_key"],
        "signed": info["signed"],
        "mul": info["mul"],
        "div": info["div"],
        "offset": info["offset"],
        "decimal_point_count": info["decimal_point_count"],
        "unit": info["unit"],
        "pattern_display": info["pattern_display"],
        "interpretation": interpretation,
        "semantic_role": "diagnostic_data_monitor_observer_candidate",
    }


def build() -> dict[str, Any]:
    gts_root = resolve_gts_root()
    abs_ddb = gts_db_root(gts_root) / "ABS_P5.ddb"
    live = json.loads(LIVE.read_text(encoding="utf-8"))

    category = gts_json("category", "435")["category"]
    expected_category = {
        "category_id": 435,
        "database": "ABS_P5.ddb",
        "generation": 20,
        "name": "Brake/EPB",
        "short_name": "",
    }
    if category != expected_category:
        raise ValueError(f"current category-435 identity drift: {category}")

    angle_row = only_row(0x107E, "ADS Control EPS Pinion Angle2")
    auth_row = only_row(0x10AF, "Software Number for Authentication")
    angle = observer(
        angle_row,
        "signed 24-bit angle; display radians = raw * 25 / 100000 (0.00025 rad/count)",
    )
    auth = observer(
        auth_row,
        "opaque 136-bit (17-byte) authentication software-number field; no unit or value dictionary",
    )
    if angle["bit_range_inclusive"] != [0, 23] or angle["unit"] != "rad":
        raise ValueError(f"0x107E geometry drift: {angle}")
    if auth["bit_range_inclusive"] != [0, 135] or auth["pattern_display"] != {}:
        raise ValueError(f"0x10AF geometry drift: {auth}")

    command = gts_json("command", "435", "0x05")
    plan = command["list_model"]["category_plan"]
    expected_partition = {
        "direct_exclude": 0,
        "direct_include": 0,
        "runtime_check_support_pid": 554,
    }
    if plan["candidate_table"] != 62 or plan["candidate_partition"] != expected_partition:
        raise ValueError(f"category-435 monitor-list partition drift: {plan}")

    brake = live["module_identity"]["Brake_EPB_category_435"]
    oracle = live["brake_read_only_oracles"]
    if (
        brake["f181"] != "F152633K0000"
        or oracle["0x107E_default"]["status"] != "negative_or_timeout"
        or "request out of range" not in oracle["0x107E_default"]["error"]
    ):
        raise ValueError("exact Camry Brake identity/live 0x107E boundary drift")

    return {
        "schema": "camry-brake-observer-vocabulary-v1",
        "title": "Current GTS+ category-435 Brake observer vocabulary",
        "sources": {
            "current_gtsplus_abs_p5": {
                "path": "NA/DB/Gen/ABS_P5.ddb",
                "size": abs_ddb.stat().st_size,
                "sha256": sha256_file(abs_ddb),
            },
            str(LIVE.relative_to(REPO)): {"sha256": sha256_file(LIVE)},
        },
        "category_435": {
            **category,
            "monitor_schema": {
                "table": 62,
                "table_class": plan["candidate_table_class"],
                "record_size": plan["record_size"],
                "candidate_count": plan["candidate_count"],
            },
        },
        "observer_vocabulary": {
            "ads_control_eps_pinion_angle2": angle,
            "software_number_for_authentication": auth,
        },
        "runtime_support_boundary": {
            "role": "0x05 Data Monitor list",
            "plugin": command["plugin"],
            "candidate_partition": plan["candidate_partition"],
            "conclusion": (
                "Both rows are static DDB candidates. Category 435 runtime-probes every monitor candidate via "
                "CheckSupportPid, so DDB presence does not prove that the exact Camry exposes either DID."
            ),
        },
        "exact_camry_boundary": {
            "brake_identity": brake,
            "did_107e_default": oracle["0x107E_default"],
            "did_107e_extended": oracle["0x107E_extended"],
            "did_10af_live_support": "not_measured",
        },
        "producer_boundary": {
            "changes_acquisition_or_producer_hypothesis": False,
            "conclusion": (
                "0x10AF is observer vocabulary for a software-number field. Its name and 17-byte geometry do not "
                "identify a SecurityAccess secret, CMAC/freshness implementation, B6 producer, or package. It does "
                "not replace the exact F181/0105 acquisition inputs recorded separately."
            ),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()
    artifact = build()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(artifact, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
