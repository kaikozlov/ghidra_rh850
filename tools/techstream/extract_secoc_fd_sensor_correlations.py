#!/usr/bin/env python3
"""Correlate Sienna SecOC CAN-FD sensor fields with Techstream EMPS2_P5 vocabulary.

This intentionally promotes only cross-source joins with independent firmware evidence.
RR/RL are retained as an unordered pair because no static artifact binds the two 0x090
wire positions to right versus left individually.
"""
from __future__ import annotations

import csv
import hashlib
import json
import struct
import sys
from pathlib import Path

HERE = Path(__file__).resolve()
REPO = HERE.parents[2]
sys.path.insert(0, str(HERE.parent))
from parse_ddb import DDBParser  # noqa: E402

ROOT = REPO / "Techstream/unpacked/toyota/Toyota Diagnostics/Techstream"
OUT = REPO / "data/generated/techstream_v18/secoc_fd_sensor_correlations.json"
RXMAP = REPO / "data/application_rx_map.csv"
FW = REPO / "firmware/RH850_P1M-E_CodeFlash.bin"
REGIONS = ("NA", "EU", "JP")
MONITORS = {
    303: "CAN Vehicle Speed (Speed Sensor RR)",
    304: "CAN Vehicle Speed (Speed Sensor RL)",
    305: "CAN Vehicle Speed (SP1)",
    306: "CAN Steering Angle Speed (SSAV)",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def records(db, table: int) -> list[bytes]:
    section = db.sections[table]
    size = section.decoded_record_size
    return [section.decoded_data[i * size:(i + 1) * size]
            for i in range(section.header.record_count)]


def find_u16(rows: list[bytes], offset: int, key: int) -> tuple[int, bytes]:
    found = [(i, row) for i, row in enumerate(rows)
             if struct.unpack_from("<H", row, offset)[0] == key]
    if len(found) != 1:
        raise ValueError(f"expected one key {key} at +0x{offset:x}, got {len(found)}")
    return found[0]


def decode_region(parser: DDBParser, region: str) -> dict:
    db_path = ROOT / region / "DB/EMPS2_P5.ddb"
    string_path = ROOT / region / "DB/M_English.ddb"
    db = parser.parse_ecu_db(db_path)
    strings = parser.load_string_db(string_path)
    result = {}
    for key, expected_name in MONITORS.items():
        index, mon = find_u16(records(db, 62), 0x24, key)
        name = strings.get_string(struct.unpack_from("<I", mon, 0x18)[0])
        if name != expected_name:
            raise ValueError(f"monitor {key} name changed: {name!r}")
        phy_key = struct.unpack_from("<H", mon, 0x2A)[0]
        phy_index, phy = find_u16(records(db, 13), 0x0C, phy_key)
        unit_key = struct.unpack_from("<H", phy, 0x0E)[0]
        unit_index, unit = find_u16(records(db, 15), 0x04, unit_key)
        unit_string_index = struct.unpack_from("<I", unit, 0x00)[0]
        result[str(key)] = {
            "monitor_index": index,
            "name": name,
            "bit_start": struct.unpack_from("<H", mon, 0x2C)[0],
            "bit_end": struct.unpack_from("<H", mon, 0x2E)[0],
            "range_words_i32": [struct.unpack_from("<i", mon, off)[0] for off in (0, 4, 8, 12, 16, 20)],
            "monitor_raw_hex": mon.hex(),
            "physical_data_key": phy_key,
            "physical_data_index": phy_index,
            "physical_data_raw_hex": phy.hex(),
            "unit_key": unit_key,
            "unit_index": unit_index,
            "unit": strings.get_string(unit_string_index) if unit_string_index else None,
        }
    return {
        "ddb": str(db_path.relative_to(ROOT)),
        "ddb_sha256": sha256(db_path),
        "string_db_sha256": sha256(string_path),
        "monitors": result,
    }


def rx_fields() -> dict[int, dict]:
    with RXMAP.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    wanted = {270, 273, 276, 283}
    out = {}
    for row in rows:
        sid = int(row["signal_id"])
        if sid in wanted:
            out[sid] = {
                "can_id": row["can_id"],
                "wire_field": row["wire_field"],
                "bit_length": int(row["bit_length"]),
                "signed": bool(int(row["signed"])),
                "dest": row["dest"],
            }
    if set(out) != wanted:
        raise ValueError(f"missing Rx signals: {wanted - set(out)}")
    return out


def fw_u16(blob: bytes, off: int) -> int:
    return struct.unpack_from("<H", blob, off)[0]


def build() -> dict:
    parser = DDBParser()
    regions = {region: decode_region(parser, region) for region in REGIONS}
    first = regions["NA"]["monitors"]
    for region in REGIONS[1:]:
        current = regions[region]["monitors"]
        for key in MONITORS:
            k = str(key)
            for field in ("name", "bit_start", "bit_end", "range_words_i32", "physical_data_raw_hex", "unit"):
                if current[k][field] != first[k][field]:
                    raise ValueError(f"{region} monitor {key} differs in {field}")

    fw = FW.read_bytes()
    fields = rx_fields()
    return {
        "schema_version": 1,
        "source": "Toyota Techstream V18.00.003 family vocabulary + Sienna 8965B4512000 firmware static analysis",
        "techstream": {
            "family": "EMPS2_P5",
            "regions": regions,
            "cross_region_identity_fields": [
                "name", "bit_start", "bit_end", "range_words_i32", "physical_data_raw_hex", "unit"
            ],
        },
        "firmware": {
            "codeflash_sha256": hashlib.sha256(fw).hexdigest(),
            "rx_fields": {str(k): v for k, v in sorted(fields.items())},
            "transforms": {
                "rear_wheel_speed_pair": {
                    "signals": [270, 273],
                    "center": 0x200,
                    "gain_numerator": 0x931,
                    "gain_denominator": 0x100,
                    "published_state": "FEBEB6AA -> FEBEAE02",
                    "processor": "0xBBF0E",
                },
                "steering_angle_speed": {
                    "signal": 276,
                    "center": 0x200,
                    "gain_numerator": 0x3E77,
                    "gain_denominator": 0x100,
                    "published_state": "FEBEB714 -> FEBEAF00",
                    "processor": "0xBC766",
                },
                "sp1_vehicle_speed": {
                    "signal": 283,
                    "raw_clamp": 30000,
                    "gain_numerator": 0x147B,
                    "gain_denominator": 0x1000,
                    "published_state": "FEBEB6F2 -> application_vehicle_speed_raw@FEBEE892",
                    "processor": "0xBC484",
                },
            },
            "calibration_words": {
                "0x1A404": fw_u16(fw, 0x1A404),
                "0x1A430": fw_u16(fw, 0x1A430),
            },
        },
        "correlations": [
            {
                "firmware_signals": [270, 273],
                "techstream_monitor_keys": [303, 304],
                "semantic": "CAN rear wheel speeds (RR/RL pair)",
                "unit": "km/h",
                "confidence": "high_pair_low_individual_order",
                "basis": "two same-width/same-scale protected 0x090 channels processed as a redundant speed pair; adjacent EMPS2_P5 monitors 303/304 are RR/RL speed in km/h; firmware does not statically bind first versus second wire field to right versus left",
            },
            {
                "firmware_signals": [276],
                "techstream_monitor_keys": [306],
                "semantic": "CAN Steering Angle Speed (SSAV)",
                "unit": "deg/s",
                "confidence": "high",
                "basis": "unique third protected 0x090 signed-dynamic channel has separate scaling and steering-validity/filter use; EMPS2_P5 monitor 306 is signed16 CAN Steering Angle Speed in deg/s and is adjacent to the RR/RL/SP1 monitor family",
            },
            {
                "firmware_signals": [283],
                "techstream_monitor_keys": [305],
                "semantic": "CAN Vehicle Speed (SP1)",
                "unit": "km/h",
                "confidence": "very_high",
                "basis": "firmware independently proves vehicle-speed use and clamps raw signal at exactly 30000; EMPS2_P5 monitor 305 is CAN Vehicle Speed (SP1), km/h, with range word 30000 in all three regions",
            },
        ],
        "bounded_unknowns": [
            "The static artifacts do not bind 0x090 signal 270 versus 273 individually to RR versus RL; only the unordered RR/RL pair is promoted.",
            "EMPS2_P5 is a Toyota family diagnostic database, not an exact 8965B4512000 calibration transcript; correlations require the independent firmware-shape joins recorded above.",
        ],
    }


def main() -> int:
    if not ROOT.is_dir():
        raise SystemExit(f"missing Techstream tree: {ROOT}")
    result = build()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
