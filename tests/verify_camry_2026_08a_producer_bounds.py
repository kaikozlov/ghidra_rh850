#!/usr/bin/env python3
"""Verify Bus-4 0x08A producer/SecOC bounds over retained drives + GTS+ canbus."""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
ART = REPO / "data/generated/camry_2026_08a_producer_bounds.json"
BUILD = REPO / "tools/analyze_camry_2026_08a_producer_bounds.py"

passed = failed = 0


def check(name, condition, detail=""):
    global passed, failed
    ok = bool(condition)
    passed += int(ok)
    failed += int(not ok)
    print(f"[{'PASS' if ok else 'FAIL'}] {name}" + (f" ({detail})" if detail else ""))


art = json.loads(ART.read_text())

print("== deterministic regeneration ==")
with tempfile.TemporaryDirectory() as td:
    out = Path(td) / ART.name
    proc = subprocess.run(
        [sys.executable, str(BUILD), "--out", str(out)],
        cwd=REPO,
        capture_output=True,
        text=True,
        check=False,
    )
    check("offline analyzer succeeds", proc.returncode == 0, proc.stderr[-300:])
    check(
        "artifact regenerates byte-identically",
        proc.returncode == 0 and out.read_bytes() == ART.read_bytes(),
    )

check("schema is v4", art["schema"] == "camry-2026-08a-producer-bounds-v4")
check(
    "F33 generated-COM Tx excludes 0x08A",
    art["f33_generated_com_tx"] == ["0x030", "0x351", "0x394", "0x4A3", "0x4C8"],
)

print("== observed rate, timestamp boundary, and bus placement ==")
for drive in ("drive_a", "drive_b"):
    d = art["drives"][drive]
    c08 = d["cadence"]["0x08A"]
    batching = d["event_timestamp_batching"]
    check(f"{drive}: zero 0x08A on bus 1", d["0x08A_bus_counts"]["1"] == 0)
    check(
        f"{drive}: 0x08A mean 35..42 Hz",
        35.0 <= c08["mean_hz"] <= 42.0,
        str(c08["mean_hz"]),
    )
    check(
        f"{drive}: CAN publications contain many frames per timestamp",
        batching["median_bus0_frames_per_event"] >= 10,
        str(batching["median_bus0_frames_per_event"]),
    )
    check(
        f"{drive}: over 99.9% of 0x08A uses multi-frame publication timestamps",
        batching["0x08A_frames_in_multi_frame_events"] <= batching["0x08A_frame_count"]
        and batching["0x08A_multi_frame_event_fraction"] >= 0.999,
    )
    check(
        f"{drive}: timestamp boundary rejects wire attribution",
        "not an individual CAN frame" in batching["boundary"]
        and "cannot identify physical arbitration" in batching["boundary"],
    )
    neg = d["bus1_auth_negative"]
    check(f"{drive}: zero 0x00F on bus 1", neg["0x00F_count"] == 0)
    check(
        f"{drive}: no MAC-like last-4 on periodic bus 1",
        neg["maclike_last4_stream_count"] == 0,
        str(neg["maclike_last4_stream_count"]),
    )
    check(
        f"{drive}: bus 1 max last-4 unique frac < 0.01",
        neg["max_last4_unique_frac"] is not None and neg["max_last4_unique_frac"] < 0.01,
        str(neg["max_last4_unique_frac"]),
    )
    check(f"{drive}: 0x180 last-4 is constant", neg["0x180_unique_last4"] == 1)
    check(
        f"{drive}: bus-0 0x08A last-4 is frame-unique",
        d["bus0_08a_last4_unique_frac"] is not None
        and d["bus0_08a_last4_unique_frac"] >= 0.99,
        str(d["bus0_08a_last4_unique_frac"]),
    )

print("== GTS+ canbus 12984 ==")
gts = art["gtsplus_canbus_12984"]
check("vehicle is Camry HV 12984", gts["vehicle_name"] == "Camry HV" and gts["vehicle_type"] == 12984)
bus1 = set(gts["domains_by_bus"]["Bus 1"])
bus4 = set(gts["domains_by_bus"]["Bus 4"])
check("Front Camera Module is Bus 1", "Front Camera Module" in bus1)
check("Front Camera Module is not Bus 4", "Front Camera Module" not in bus4)
check(
    "Bus 4 native set is brake-family + EPS + SAS + airbag",
    bus4
    == {
        "Airbag",
        "Brake Booster",
        "Power Steering (EPS)",
        "Skid Control (ABS/VSC/TRAC)",
        "Spiral cable (Steering Angle Sensor)",
    },
    str(sorted(bus4)),
)

cl = art["classification"]
check("FRC recorder object is joined without naming transmitter", "FRC-hosted" in cl["recorder_object"])
check(
    "batched timestamps forbid queue attribution",
    "cannot reject a shared controller" in cl["timestamp_attribution_boundary"],
)
check("SecOC remains 0x00F-domain FV4||MAC28", "FV4||MAC28" in cl["secoc"] and "unrecovered" in cl["secoc"])
check(
    "camera Bus-1 output terminates before the TSK signing boundary",
    "do not carry an ordinary-P5 FV4||MAC28 trailer" in cl["camera_output_auth_boundary"]
    and "FRC is not a TSK key-holder/signing participant" in cl["camera_output_auth_boundary"]
    and "downstream TSK-capable proxy" in cl["camera_output_auth_boundary"],
)
check(
    "physical transmitter/proxy signer remains bounded to downstream chassis candidates",
    "FRC is excluded as the TSK key holder/signer" in cl["physical_tx_and_signer_bounds"]
    and "Skid Control" in cl["physical_tx_and_signer_bounds"]
    and "Brake Booster" in cl["physical_tx_and_signer_bounds"]
    and "Central Gateway" in cl["physical_tx_and_signer_bounds"]
    and "remains unidentified" in cl["physical_tx_and_signer_bounds"],
)
check("regression forbids sending 0x08A to EPS", "Do not send 0x08A to EPS" in cl["regression_rule"])

print(f"\nResults: {passed} passed, {failed} failed")
raise SystemExit(1 if failed else 0)
