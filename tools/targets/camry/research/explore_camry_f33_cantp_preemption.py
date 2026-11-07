#!/usr/bin/env python3
"""Explore instruction-boundary CanTp/DCM preemption on original Camry F33 CodeFlash."""
from __future__ import annotations

import argparse
import copy
import json
from collections import Counter
from pathlib import Path
from typing import Any

from tools import REPO_ROOT
from tools.emulation.p1me_machine import capture_many

TARGET = "camry-8965F3307000"
FIXTURE_DIR = REPO_ROOT / "tests/fixtures/rh850/machine/camry-8965F3307000"
TEMPLATES = {
    "k": FIXTURE_DIR / "camry_f33_cantp_foreground_k_timeout_dcm_cleanup.json",
    "z": FIXTURE_DIR / "camry_f33_cantp_foreground_z_timeout_dcm_cleanup.json",
}
DEFAULT_OUT = REPO_ROOT / "build/out/targets/camry-8965F3307000/bootstrap-preemption"

# Post-filter diagnostic frames carry GAFL rule 43's label into CanIf. FIFO 5 is
# the configured controller-1 diagnostic receive FIFO. EIC187 is its level IRQ.
CAN_EVENT = {
    "kind": "can-rx",
    "fifo": 5,
    "can_id": "0x7a1",
    "boundary": "post-filter",
    "label": 0x34,
    "evidence": (
        "Synthetic post-filter controller-1 diagnostic frame at an explicit instruction "
        "boundary; exact FIFO/label from GAFL rule43 and the original 83D40 receive path"
    ),
}
FRAME_DATA = {
    "sf": "0322f181a1a2a3a4",
    "ff100": "110022f181a1a2a3",
    "ff101": "110122f181a1a2a3",
    "cf1": "21d1d2d3d4d5d6d7",
    "cf2": "22e1e2e3e4e5e6e7",
}

# Exact application configuration: EIC187 was written as 0x8048 by original
# startup at 0x62E4C in the reset-to-runtime machine proof. CFCC5 enables an
# every-message, four-entry, eight-byte receive FIFO; GCTR/C1CTR are operating.
RUNTIME_ROWS = (
    {
        "address": "0xffffb176",
        "hex": "4880",
        "evidence": "Original startup store at 62E4C: EIC187=8048 (table vector, priority8, unmasked)",
    },
    {
        "address": "0xffd2012c",
        "hex": "03110000",
        "evidence": "Modeled FIFO5 receive boundary: CFE|CFRXIE|CFDC=4|CFIM=every message",
    },
    {
        "address": "0xffd20088",
        "hex": "00000000",
        "evidence": "Normal RSCFD global operating mode required by receiveFrame",
    },
    {
        "address": "0xffd20014",
        "hex": "00000000",
        "evidence": "Normal RSCFD channel1 operating mode required by receiveFrame",
    },
    {
        "address": "0xffd20018",
        "hex": "00000000",
        "evidence": "Normal RSCFD channel1 status required by original receive-service gate 83EF2",
    },
)

PROBES = (
    ("cantp-cells", 0xFEBE4F3C, 0x80),
    ("dcm-buffers", 0xFEBE5651, 0x300),
    ("dcm-control", 0xFEBE5950, 0xF0),
    ("callback-pivot", 0xFEBF1180, 0x30),
    ("landing-zone", 0xFEBFF9F0, 524),
)
SLOT_BASES = (0xFEBE5651, 0xFEBE5751, 0xFEBE5851)
SLOT_STATE_OFFSET = 0xFEBE59F0 - 0xFEBE5950


def parse_ticks(value: str) -> list[int]:
    ticks: list[int] = []
    for part in value.split(","):
        fields = part.split(":")
        if len(fields) == 1:
            ticks.append(int(fields[0], 0))
            continue
        if len(fields) not in (2, 3):
            raise argparse.ArgumentTypeError(f"invalid tick range: {part}")
        start, stop = (int(field, 0) for field in fields[:2])
        step = int(fields[2], 0) if len(fields) == 3 else 1
        if step <= 0 or stop < start:
            raise argparse.ArgumentTypeError(f"invalid tick range: {part}")
        ticks.extend(range(start, stop + 1, step))
    return sorted(set(ticks))


def load_template(state: str) -> dict[str, Any]:
    return json.loads(TEMPLATES[state].read_text(encoding="utf-8"))


def memory_probe(name: str, address: int, size: int) -> dict[str, Any]:
    return {
        "name": name,
        "kind": "memory",
        "address": hex(address),
        "size": size,
        # capture_many retains actual bytes from deliberately mismatched checks.
        "equals_hex": "00" * size,
    }


def make_scenario(state: str, tick: int, frame: str) -> dict[str, Any]:
    scenario = copy.deepcopy(load_template(state))
    scenario["name"] = f"cantp_preempt_{state}_{frame}_t{tick}"
    scenario["registers"].update({
        "PSW": "0",
        "PMR": "0",
        "RBASE": "0",
        "INTBP": "0x20200",
        "CTPC": "0",
        "CTPSW": "0",
    })
    scenario["memory"] = [
        {
            "address": "0xfebe0000",
            "size": 0x20000,
            "fill": 0,
            "evidence": (
                "Deterministic initialized LocalRAM baseline for the original interrupt path; "
                "specific recovered CanTp/DCM rows below override this fill"
            ),
        },
        *scenario["memory"],
        *copy.deepcopy(RUNTIME_ROWS),
    ]
    scenario["events"] = [{
        **CAN_EVENT,
        "data_hex": FRAME_DATA[frame],
        "after_instructions": tick,
    }]
    scenario["checks"] = [
        {
            "name": "can-rx-accepted",
            "kind": "event-count",
            "operation": "can-rx",
            "equals": 1,
        },
        {
            "name": "receive-interrupt-entered",
            "kind": "event-count",
            "operation": "interrupt-enter",
            "equals": 1,
        },
        {
            "name": "receive-interrupt-returned",
            "kind": "event-count",
            "operation": "interrupt-return",
            "equals": 1,
        },
        *(memory_probe(name, address, size) for name, address, size in PROBES),
    ]
    scenario["expected_termination"] = "stop-address"
    return scenario


def check_actual(report: dict[str, Any], name: str) -> bytes:
    row = next(check for check in report["checks"] if check["name"] == name)
    return bytes.fromhex(row["actual"])


def slot_anomalies(dcm_control: bytes) -> list[str]:
    anomalies: list[str] = []
    for slot, base in enumerate(SLOT_BASES):
        offset = SLOT_STATE_OFFSET + slot * 0x10
        row = dcm_control[offset:offset + 0x10]
        cursor = int.from_bytes(row[0:4], "little")
        length = int.from_bytes(row[4:6], "little")
        remaining = int.from_bytes(row[8:10], "little")
        receiving = row[10]
        if not base <= cursor <= base + 0x100:
            anomalies.append(f"slot{slot}-cursor={cursor:#x}")
        if length > 0x100:
            anomalies.append(f"slot{slot}-length={length:#x}")
        if remaining > 0x100:
            anomalies.append(f"slot{slot}-remaining={remaining:#x}")
        if receiving not in (0, 1):
            anomalies.append(f"slot{slot}-receiving={receiving:#x}")
    return anomalies


def summarize(report: dict[str, Any], state: str, tick: int, frame: str) -> dict[str, Any]:
    events = Counter(event.get("kind") for event in report.get("device_events", []))
    if "checks" not in report:
        termination = report.get("termination_reason")
        return {
            "scenario": report["scenario"],
            "state": state,
            "tick": tick,
            "frame": frame,
            "instruction_count": report.get("instruction_count"),
            "termination_reason": termination,
            "fault": report.get("fault"),
            "error": report.get("error"),
            "events": dict(sorted(events.items())),
            "slot_anomalies": [],
            "pivot_nonzero": False,
            "landing_nonzero": False,
            "anomalies": [f"termination={termination}"],
            "dcm_control_hex": None,
        }
    dcm_control = check_actual(report, "dcm-control")
    pivot = check_actual(report, "callback-pivot")
    landing = check_actual(report, "landing-zone")
    anomalies = slot_anomalies(dcm_control)
    if any(pivot):
        anomalies.append("callback-pivot-nonzero")
    if any(landing):
        anomalies.append("landing-zone-nonzero")
    if report.get("fault"):
        anomalies.append("machine-fault")
    if report.get("termination_reason") != "stop-address":
        anomalies.append(f"termination={report.get('termination_reason')}")
    return {
        "scenario": report["scenario"],
        "state": state,
        "tick": tick,
        "frame": frame,
        "instruction_count": report.get("instruction_count"),
        "termination_reason": report.get("termination_reason"),
        "fault": report.get("fault"),
        "events": dict(sorted(events.items())),
        "slot_anomalies": slot_anomalies(dcm_control),
        "pivot_nonzero": any(pivot),
        "landing_nonzero": any(landing),
        "anomalies": anomalies,
        "dcm_control_hex": dcm_control.hex(),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--states", default="k,z", help="comma-separated timeout states: k,z")
    parser.add_argument("--ticks", type=parse_ticks, default=parse_ticks("418:436"))
    parser.add_argument("--frames", default="sf,ff100,ff101,cf1,cf2")
    parser.add_argument(
        "--full-instruction-sweep",
        action="store_true",
        help="inject every selected frame after every baseline instruction in each state",
    )
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT / "matrix")
    parser.add_argument("--instruction-trace", action="store_true")
    args = parser.parse_args()

    states = [value.strip() for value in args.states.split(",") if value.strip()]
    frames = [value.strip() for value in args.frames.split(",") if value.strip()]
    unknown_states = sorted(set(states) - set(TEMPLATES))
    unknown_frames = sorted(set(frames) - set(FRAME_DATA))
    if unknown_states or unknown_frames:
        parser.error(f"unknown states={unknown_states} frames={unknown_frames}")

    out = args.out.resolve()
    scenario_dir = out / "scenarios"
    report_dir = out / "reports"
    scenario_dir.mkdir(parents=True, exist_ok=True)
    if args.full_instruction_sweep:
        baseline_reports = capture_many(
            TARGET,
            [TEMPLATES[state] for state in states],
            out / "baseline",
        )
        ticks_by_state = {
            state: list(range(report["instruction_count"]))
            for state, report in zip(states, baseline_reports, strict=True)
        }
    else:
        ticks_by_state = {state: args.ticks for state in states}

    records: list[tuple[str, int, str, Path]] = []
    for state in states:
        for tick in ticks_by_state[state]:
            for frame in frames:
                scenario = make_scenario(state, tick, frame)
                path = scenario_dir / f"{scenario['name']}.json"
                path.write_text(json.dumps(scenario, indent=2) + "\n", encoding="utf-8")
                records.append((state, tick, frame, path))

    reports = capture_many(
        TARGET,
        [record[3] for record in records],
        report_dir,
        instruction_trace=args.instruction_trace,
    )
    rows = [
        summarize(report, state, tick, frame)
        for report, (state, tick, frame, _path) in zip(reports, records, strict=True)
    ]
    summary = {
        "schema": "camry-f33-cantp-preemption-matrix-v1",
        "target": TARGET,
        "scenario_count": len(rows),
        "states": states,
        "ticks": "full" if args.full_instruction_sweep else args.ticks,
        "ticks_by_state": ticks_by_state,
        "frames": frames,
        "anomaly_count": sum(bool(row["anomalies"]) for row in rows),
        "event_totals": dict(sorted(sum((Counter(row["events"]) for row in rows), Counter()).items())),
        "rows": rows,
    }
    summary_path = out / "summary.json"
    summary_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "summary": str(summary_path),
        "scenario_count": len(rows),
        "anomaly_count": summary["anomaly_count"],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
