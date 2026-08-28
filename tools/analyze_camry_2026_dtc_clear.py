#!/usr/bin/env python3
"""Summarize the 2026 Camry live DTC-clear probe into a deterministic artifact."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
RAW = REPO / "targets/camry-2026/raw-20260827/dtc-clear"
DEFAULT_OUT = REPO / "data/generated/camry_2026_dtc_clear.json"
FAULT_MASK = 0xAF  # failed/current/pending/confirmed/failed-since-clear/warning


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def parse_records(response_hex: str) -> list[dict[str, int | str]]:
    raw = bytes.fromhex(response_hex)
    if not raw:
        return []
    records = []
    for offset in range(1, len(raw) - 3, 4):
        dtc = raw[offset : offset + 3].hex().upper()
        status = raw[offset + 3]
        records.append(
            {
                "dtc_raw": dtc,
                "status": status,
                "status_hex": f"0x{status:02X}",
                "fault_bits": status & FAULT_MASK,
            }
        )
    return records


def by_address(rows: list[dict]) -> dict[str, dict]:
    return {row["address"].lower(): row for row in rows}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = ap.parse_args()

    names = [
        "camry_dtc_sweep_before.json",
        "camry_dtc_clear_results.json",
        "camry_dtc_sweep_after.json",
        "camry_mode04_clear_results.json",
        "camry_functional_mode04_results.json",
        "camry_dtc_final_sweep.json",
        "camry_obd_mode04_clear_20260827.json",
    ]
    source_identity = {
        name: {"bytes": (RAW / name).stat().st_size, "sha256": sha256(RAW / name)}
        for name in names
    }

    before = json.loads((RAW / names[0]).read_text())
    clear_results = json.loads((RAW / names[1]).read_text())
    mode04_physical = json.loads((RAW / names[3]).read_text())
    mode04_per_ecu_func = json.loads((RAW / names[4]).read_text())
    final = json.loads((RAW / names[5]).read_text())
    functional = json.loads((RAW / names[6]).read_text())

    before_map = by_address(before)
    pre_faults = []
    for addr, row in before_map.items():
        if "dtc_response" not in row:
            continue
        for record in parse_records(row["dtc_response"]):
            if record["fault_bits"]:
                pre_faults.append({"address": addr.upper().replace("X", "x"), **record})

    u0131_before = {}
    for addr in ("0x7d2", "0x7b0", "0x7c4", "0x792"):
        records = parse_records(before_map[addr]["dtc_response"])
        matches = [r for r in records if r["dtc_raw"] == "C13187"]
        if len(matches) != 1:
            raise ValueError(f"{addr}: expected one C13187 record, got {matches}")
        u0131_before[addr] = matches[0]["status_hex"]

    uds14 = {row["address"].lower(): row for row in clear_results}
    uds14_success = sorted(addr for addr, row in uds14.items() if row["cleared"])
    uds14_rejected = sorted(addr for addr, row in uds14.items() if not row["cleared"])

    final_responders = [row for row in final if "fault_status_records" in row]
    remaining_faults = [
        {"address": row["address"], "records": row["fault_status_records"]}
        for row in final_responders
        if row["fault_status_records"]
    ]

    artifact = {
        "schema": "camry-2026-dtc-clear-v1",
        "vehicle": "maintainer 2026 Toyota Camry Hybrid",
        "vehicle_state": functional["vehicle_state"],
        "source_identity": source_identity,
        "dtc_status": {
            "fault_mask": "0xAF",
            "pre_clear_fault_records": pre_faults,
            "u0131_87_raw_dtc": "C13187",
            "u0131_87_name": "Lost Communication with Power Steering Control Module — Missing Message",
            "u0131_87_pre_clear_status": u0131_before,
        },
        "physical_uds14": {
            "request": "14 FF FF FF",
            "succeeded": uds14_success,
            "rejected_service_not_supported": uds14_rejected,
        },
        "failed_mode04_routes": {
            "physical_addresses": [row["address"] for row in mode04_physical if not row["mode04_clear"]],
            "per_ecu_func_addresses": [row["functional"] for row in mode04_per_ecu_func if not row["cleared"]],
        },
        "legislated_obd": {
            "request_id": functional["clear"]["request_id"],
            "mode01_probe_request_frame": functional["functional_probe"]["request_frame"],
            "mode01_responders": functional["functional_probe"]["responses"],
            "mode04_clear_request_frame": functional["clear"]["request_frame"],
            "mode04_positive_responses": functional["clear"]["responses"],
            "address_join": functional["address_join"],
        },
        "final_sweep": {
            "responding_ecus": len(final_responders),
            "responders": [row["address"] for row in final_responders],
            "remaining_fault_status_records": remaining_faults,
            "all_responding_ecus_clear_of_fault_bits": not remaining_faults,
        },
        "boundary": (
            "Live exact-vehicle maintenance result. Standard functional OBD Mode 04 cleared the "
            "legislated P5 controllers that reject physical UDS SID 0x14; direct UDS 0x14 cleared "
            "the remaining responding controllers. This does not generalize the route to every Toyota ECU."
        ),
    }

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(artifact, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
