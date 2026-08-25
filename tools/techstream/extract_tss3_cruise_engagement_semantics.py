#!/usr/bin/env python3
"""Extract Toyota P5 cruise/engagement diagnostic vocabulary from Techstream DDBs."""
from __future__ import annotations

import argparse
import hashlib
import json
import struct
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
ROOT = REPO / "Techstream/unpacked/toyota/Toyota Diagnostics/Techstream/NA/DB"
OUT = REPO / "data/generated/techstream_v18/tss3_cruise_engagement_semantics.json"
sys.path.insert(0, str(Path(__file__).resolve().parent))
from parse_ddb import DDBParser  # noqa: E402

FRC_MONITORS = {
    23: "ACC Installation Availability",
    94: "Cruise Control Permission Flag",
    95: "Main Switch Recognition Flag",
    96: "Set Cancel Switch Condition",
    101: "ACC Not Available Icon Lighting Request Flag",
    102: "ACC Control in Operation Flag",
    104: "ACC Brake Control in Operation",
    106: "ACC Installed Flag",
    201: "Set Vehicle Interval Time",
    217: "Current Vehicle Speed",
    218: "Memory Vehicle Speed",
}
SUPPORTING = {
    "Engine_P5.ddb": {400: "Cruise Main SW"},
    "ECT_P5.ddb": {400: "Cruise Main SW"},
    "Meter_P5.ddb": {
        63: "Radar Cruise System",
        217: "Radar Cruise Indicator",
        218: "Radar Cruise Indicator (Yellow)",
        219: "Cruise Indicator",
        220: "Cruise Indicator (Yellow)",
        440: "Main Switch",
    },
}


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def records(section) -> list[bytes]:
    n = section.header.record_count
    s = section.record_size
    return [section.raw_data[i * s:(i + 1) * s] for i in range(n)]


def u16(raw: bytes, off: int) -> int:
    return struct.unpack_from("<H", raw, off)[0]


def u32(raw: bytes, off: int) -> int:
    return struct.unpack_from("<I", raw, off)[0]


def find_record(rows: list[bytes], off: int, key: int) -> bytes:
    hits = [row for row in rows if u16(row, off) == key]
    if len(hits) != 1:
        raise ValueError(f"expected one record key={key} off=0x{off:X}, got {len(hits)}")
    return hits[0]


def pattern_values(db, strings, key: int) -> dict[str, str]:
    if key == 0:
        return {}
    out: dict[int, str] = {}
    for raw in records(db.sections[14]):
        if u16(raw, 0x0C) == key:
            out[u32(raw, 0x04)] = strings.get_string(u32(raw, 0x00))
    return {str(k): v for k, v in sorted(out.items())}


def decode_monitor(parser: DDBParser, strings, db_path: Path, key: int, expected_name: str) -> dict:
    db = parser.parse_ecu_db(db_path)
    monitor = find_record(records(db.sections[62]), 0x24, key)
    name = strings.get_string(u32(monitor, 0x18))
    if name != expected_name:
        raise ValueError(f"{db_path.name} monitor {key}: expected {expected_name!r}, got {name!r}")
    physical_key = u16(monitor, 0x2A)
    physical = find_record(records(db.sections[13]), 0x0C, physical_key)
    unit_key = u16(physical, 0x0E)
    unit = None
    if unit_key:
        unit_raw = find_record(records(db.sections[15]), 0x04, unit_key)
        unit = strings.get_string(u32(unit_raw, 0x00))
    pat_key = u16(monitor, 0x32)
    return {
        "monitor_key": key,
        "name": name,
        "primary_data_id": f"0x{u16(monitor, 0x36):04X}",
        "bit_range": [u16(monitor, 0x2C), u16(monitor, 0x2E)],
        "physical_data_key": physical_key,
        "conversion": {
            "mul": struct.unpack_from("<i", physical, 0x00)[0],
            "div": struct.unpack_from("<i", physical, 0x04)[0],
            "offset": struct.unpack_from("<i", physical, 0x08)[0],
            "signed": bool(physical[0x14]),
            "decimal_point_count": physical[0x15],
            "unit": unit,
        },
        "pattern_display_key": pat_key,
        "pattern_values": pattern_values(db, strings, pat_key),
        "monitor_record_sha256": sha(monitor),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", type=Path, default=OUT)
    args = ap.parse_args()
    parser = DDBParser()
    strings_path = ROOT / "M_English.ddb"
    strings = parser.load_string_db(strings_path)

    frc_path = ROOT / "FRC_P5.ddb"
    frc = [decode_monitor(parser, strings, frc_path, k, name) for k, name in FRC_MONITORS.items()]
    supporting: dict[str, list[dict]] = {}
    for db_name, wanted in SUPPORTING.items():
        path = ROOT / db_name
        supporting[db_name] = [decode_monitor(parser, strings, path, k, name) for k, name in wanted.items()]

    source_paths = [strings_path, frc_path, *(ROOT / name for name in SUPPORTING)]
    out = {
        "schema": "techstream-p5-tss3-cruise-engagement-semantics-v1",
        "sources": [{
            "path": str(path.relative_to(REPO)),
            "size": path.stat().st_size,
            "sha256": sha(path.read_bytes()),
        } for path in source_paths],
        "frc_p5": {
            "database": "FRC_P5.ddb",
            "monitors": frc,
            "openpilot_oracle_mapping": {
                "platform_installed": ["ACC Installation Availability", "ACC Installed Flag"],
                "permission": ["Cruise Control Permission Flag"],
                "main_switch": ["Main Switch Recognition Flag"],
                "enabled": ["ACC Control in Operation Flag"],
                "not_available_or_fault_display": ["ACC Not Available Icon Lighting Request Flag"],
                "set_speed_candidate": ["Memory Vehicle Speed"],
                "current_speed_reference": ["Current Vehicle Speed"],
                "following_interval": ["Set Vehicle Interval Time"],
                "driver_switch_activity": ["Set Cancel Switch Condition"],
                "brake_control_activity": ["ACC Brake Control in Operation"],
            },
            "boundary": (
                "These are exact Toyota P5 diagnostic monitor names, primary Data IDs, bit ranges, conversions, and display dictionaries. "
                "The Data IDs are not automatically UDS ReadDataByIdentifier DIDs; they define validation oracles for cruise/engagement semantics "
                "but do not identify the corresponding CAN wire fields or diagnostic transport service."
            ),
        },
        "supporting_p5": supporting,
        "interpretation": (
            "P5 diagnostics separate ACC installation, cruise permission, main-switch recognition, and actual ACC control-in-operation. "
            "A TSS3 CarState implementation should preserve those distinctions instead of guessing a single replacement for older MAIN_ON/CRUISE_ACTIVE."
        ),
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    print(args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
