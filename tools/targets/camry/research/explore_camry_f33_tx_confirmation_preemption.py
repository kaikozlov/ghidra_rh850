#!/usr/bin/env python3
"""Exercise stock CAN-Tx confirmation preemption against CanTp/DCM foreground."""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import tempfile
from collections import Counter
from pathlib import Path
from typing import Any

from tools import REPO_ROOT
from tools.emulation.p1me_machine import capture_many
from tools.targets.camry.research import explore_camry_f33_stateful_can_cycles as can

TARGET = "camry-8965F3307000"
DEFAULT_OUT = REPO_ROOT / "build/out/targets/camry-8965F3307000/tx-confirmation-preemption"
LOCAL_RAM = (0xFEBE0000, 0xFEC00000)
# The exact trace reaches the Tx-ownership publication at 0x8024A 56 retired
# instructions after CFDTMC.TMTR emits the frame at 0x853A4. The diagnostic
# frame is eight-byte classic CAN at 500 kbit/s; it cannot complete during
# this straight-line pre-publication window.
TX_OWNERSHIP_PUBLICATION_INSTRUCTIONS = 56
STACK = (0xFEBE1C00, 0xFEBE2000)
RUNTIME_ROWS = (
    {
        "address": "0xffffb176", "hex": "4880",
        "evidence": "Original startup EIC187=0x8048",
    },
    {
        "address": "0xffffb178", "hex": "4880",
        "evidence": "Original startup EIC188=0x8048",
    },
    {
        "address": "0xffd2012c", "hex": "03110000",
        "evidence": "Exact diagnostic FIFO5 receive configuration",
    },
    {
        "address": "0xffd20088", "hex": "00000000",
        "evidence": "RSCFD global operating mode",
    },
    {
        "address": "0xffd20014", "hex": "00000000",
        "evidence": "RSCFD channel1 operating mode",
    },
    {
        "address": "0xffd20018", "hex": "00000000",
        "evidence": "RSCFD channel1 normal status",
    },
)
PROBES = (
    ("local-ram", LOCAL_RAM[0], LOCAL_RAM[1] - LOCAL_RAM[0]),
    ("cantp-state", 0xFEBE4F3C, 0x80),
    ("tx-route-slots", 0xFEBE502A, 0x20),
    ("dcm-message", 0xFEBE5628, 0x30),
    ("dcm-queue", 0xFEBE5950, 0xD0),
    ("dcm-response-and-contexts", 0xFEBE5A20, 0x500),
    ("landing-zone", can.LANDING[0], can.LANDING[1] - can.LANDING[0]),
)


def memory_probe(name: str, address: int, size: int) -> dict[str, Any]:
    return {
        "name": name, "kind": "memory", "address": hex(address), "size": size,
        "equals_hex": "00" * size,
    }


def build_base(cycles: int) -> dict[str, Any]:
    image = can.IMAGE.read_bytes()
    snapshot = can.SNAPSHOT.read_bytes()
    scenario = can.trial_scenario(
        0, (), (), (), can.route_ids(image), snapshot, cycles, burst=True,
        prelude=(0x79D60, 0x9887C),
    )
    code = b""
    for target in (0x79D60, 0x9887C):
        code = can.append_call(code, target)
    foreground = (0x69CA2, 0x7A254, 0x79EDE, 0x79ECA, 0x988C2, 0x69E7C)
    for cycle in range(cycles):
        for target in foreground:
            code = can.append_call(code, target)
    code += can.mov(1, can.RETURN_STUB) + b"\x61\x00"
    scenario["memory"][0]["hex"] = code.hex()
    scenario["events"][0]["data_hex"] = code.hex()
    scenario["name"] = "tx_confirmation_preemption_baseline"
    scenario["max_instructions"] = 2_000_000
    scenario["registers"].update({
        "RBASE": "0", "INTBP": "0x20200", "CTPC": "0", "CTPSW": "0",
        "ISPR": "0", "ICSR": "0", "INTCFG": "0", "PSW": "0", "PMR": "0",
    })
    scenario["memory"].extend(copy.deepcopy(RUNTIME_ROWS))
    scenario["events"].extend((
        {
            "kind": "register-input", "register": "CFDTMSTS_CH1", "value": "0",
            "after_instructions": 0,
            "evidence": (
                "Idle status for channel1 local transmit resources0..3; the retained LocalRAM "
                "snapshot cannot carry RSCFD peripheral state"
            ),
        },
        {
            "kind": "register-input", "register": "TMIEC1", "value": "0xc0",
            "after_instructions": 0,
            "evidence": (
                "Original CodeFlash channel1 interrupt-completion mask at 0x22ec0; "
                "the retained LocalRAM snapshot cannot carry RSCFD peripheral state"
            ),
        },
        {
            "kind": "memory-write", "address": "0xfebe564c", "data_hex": "02000200",
            "after_instructions": 9_999,
            "evidence": "Exact configured DCM communication-slot modes used by the transport fixtures",
        },
        {
            "kind": "can-rx", "fifo": 5, "can_id": "0x7a1",
            "data_hex": "0322f18100000000", "boundary": "post-filter", "label": 0x34,
            "after_instructions": 10_000,
            "evidence": (
                "Exact FIFO5/GAFL-rule43 post-filter physical diagnostic request; "
                "single-frame RDBI F181"
            ),
        },
    ))
    scenario["checks"] = [memory_probe(*probe) for probe in PROBES]
    return scenario


def actual(report: dict[str, Any], name: str) -> bytes:
    row = next(check for check in report["checks"] if check["name"] == name)
    return bytes.fromhex(row["actual"])


def can_tx_event(report: dict[str, Any]) -> dict[str, Any]:
    events = [row for row in report.get("device_events", []) if row.get("kind") == "can-tx"]
    if len(events) != 1:
        raise RuntimeError(f"expected one stock diagnostic CAN transmit, got {len(events)}")
    return events[0]


def completion_resource(event: dict[str, Any]) -> int:
    for key in ("resource", "buffer_index", "mailbox"):
        if key in event:
            return int(event[key], 0) if isinstance(event[key], str) else int(event[key])
    if "buffer" in event:
        buffer = int(event["buffer"], 0) if isinstance(event["buffer"], str) else int(event["buffer"])
        if 16 <= buffer < 32:
            return buffer - 16
        return buffer
    address = int(event.get("address", "0"), 0)
    # Channel1 transmit message buffers n=16..31 are 0x20-byte rows at FFD24200.
    if 0xFFD24200 <= address < 0xFFD24400:
        return (address - 0xFFD24200) // 0x20
    raise RuntimeError(f"CAN transmit event lacks a resource identity: {event}")


def add_completion(base: dict[str, Any], name: str, tick: int, resource: int) -> dict[str, Any]:
    if resource not in (6, 7):
        raise ValueError(f"unsupported channel1 completion resource {resource}")
    scenario = copy.deepcopy(base)
    scenario["name"] = name
    scenario["events"].append({
        "kind": "can-tx-complete", "buffer": 16 + resource, "firmware_control": "0x8048",
        "after_instructions": tick,
        "evidence": (
            "Original startup EIC188=0x8048 and INTBP[188]=0x660BE; "
            "external completion of a previously emitted RSCFD frame"
        ),
    })
    return scenario


def differing_runs(left: bytes, right: bytes) -> list[dict[str, Any]]:
    runs: list[dict[str, Any]] = []
    start: int | None = None
    for offset, (a, b) in enumerate(zip(left, right, strict=True)):
        address = LOCAL_RAM[0] + offset
        differs = a != b and not STACK[0] <= address < STACK[1]
        if differs and start is None:
            start = address
        elif not differs and start is not None:
            runs.append({"start": hex(start), "end": hex(address - 1)})
            start = None
    if start is not None:
        runs.append({"start": hex(start), "end": hex(LOCAL_RAM[1] - 1)})
    return runs


def summarize(report: dict[str, Any], reference_ram: bytes | None = None) -> dict[str, Any]:
    events = Counter(row.get("kind") for row in report.get("device_events", []))
    ram = actual(report, "local-ram")
    landing = actual(report, "landing-zone")
    row = {
        "scenario": report["scenario"],
        "termination_reason": report.get("termination_reason"),
        "fault": report.get("fault"),
        "instruction_count": report.get("instruction_count"),
        "interrupt_enter": events["interrupt-enter"],
        "interrupt_return": events["interrupt-return"],
        "landing_sha256": hashlib.sha256(landing).hexdigest(),
        "route_slots": actual(report, "tx-route-slots").hex(),
        "cantp_state": actual(report, "cantp-state").hex(),
        "dcm_message": actual(report, "dcm-message").hex(),
        "dcm_queue": actual(report, "dcm-queue").hex(),
    }
    if reference_ram is not None:
        row["nonstack_differences_from_safe_completion"] = differing_runs(reference_ram, ram)
    return row


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--cycles", type=int, default=12)
    parser.add_argument("--window", type=int, default=256)
    parser.add_argument("--step", type=int, default=1)
    parser.add_argument("--batch-size", type=int, default=32)
    parser.add_argument("--baseline-only", action="store_true")
    args = parser.parse_args()
    if min(args.cycles, args.window, args.step, args.batch_size) < 1:
        parser.error("cycles, window, step, and batch-size must be positive")

    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=True)
    (REPO_ROOT / "build/tmp").mkdir(parents=True, exist_ok=True)
    base = build_base(args.cycles)
    with tempfile.TemporaryDirectory(prefix="tx-confirmation-", dir=REPO_ROOT / "build/tmp") as td:
        work = Path(td)
        baseline_path = work / "baseline.json"
        baseline_path.write_text(json.dumps(base), encoding="utf-8")
        baseline = capture_many(TARGET, [baseline_path], out / "baseline", instruction_trace=True)[0]
        tx = can_tx_event(baseline)
        resource = completion_resource(tx)
        tx_tick = int(tx["scheduler_tick"])
        if args.baseline_only:
            summary = {
                "schema": "camry-f33-tx-confirmation-preemption-v1",
                "image_sha256": can.IMAGE_SHA256,
                "snapshot_sha256": can.SNAPSHOT_SHA256,
                "can_tx": tx,
                "resource": resource,
                "baseline": summarize(baseline),
            }
            (out / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
            print(json.dumps(summary, indent=2))
            return 0

        safe_tick = tx_tick + args.window + 16
        safe = add_completion(base, "tx_completion_safe", safe_tick, resource)
        safe_path = work / "safe.json"
        safe_path.write_text(json.dumps(safe), encoding="utf-8")
        safe_report = capture_many(TARGET, [safe_path], out / "safe")[0]
        safe_ram = actual(safe_report, "local-ram")

        ticks = list(range(tx_tick + 1, tx_tick + args.window + 1, args.step))
        records: list[tuple[int, Path]] = []
        for tick in ticks:
            scenario = add_completion(base, f"tx_completion_t{tick}", tick, resource)
            path = work / f"t{tick}.json"
            path.write_text(json.dumps(scenario), encoding="utf-8")
            records.append((tick, path))
        reports: list[dict[str, Any]] = []
        for offset in range(0, len(records), args.batch_size):
            reports.extend(capture_many(
                TARGET, [row[1] for row in records[offset:offset + args.batch_size]],
                out / "reports",
            ))
        rows = [
            {"tick": tick, **summarize(report, safe_ram)}
            for report, (tick, _path) in zip(reports, records, strict=True)
        ]
    candidate_findings = [
        row for row in rows
        if row["fault"] or row["termination_reason"] != "stop-address"
        or row["interrupt_enter"] != 2 or row["interrupt_return"] != 2
        or row["nonstack_differences_from_safe_completion"]
    ]
    earliest_physical_tick = tx_tick + TX_OWNERSHIP_PUBLICATION_INSTRUCTIONS
    simulator_only_early_findings = [
        row for row in candidate_findings if row["tick"] < earliest_physical_tick
    ]
    findings = [
        row for row in candidate_findings if row["tick"] >= earliest_physical_tick
    ]
    summary = {
        "schema": "camry-f33-tx-confirmation-preemption-v2",
        "image_sha256": can.IMAGE_SHA256,
        "snapshot_sha256": can.SNAPSHOT_SHA256,
        "can_tx": tx,
        "resource": resource,
        "tx_tick": tx_tick,
        "safe_tick": safe_tick,
        "tx_ownership_publication_instructions": TX_OWNERSHIP_PUBLICATION_INSTRUCTIONS,
        "earliest_physical_tick": earliest_physical_tick,
        "baseline": summarize(baseline),
        "safe_completion": summarize(safe_report),
        "case_count": len(rows),
        "finding_count": len(findings),
        "simulator_only_early_finding_count": len(simulator_only_early_findings),
        "simulator_only_early_findings": simulator_only_early_findings,
        "findings": findings,
        "rows": rows,
    }
    (out / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "summary": str(out / "summary.json"), "tx": tx, "resource": resource,
        "case_count": len(rows), "finding_count": len(findings),
        "simulator_only_early_finding_count": len(simulator_only_early_findings),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
