#!/usr/bin/env python3
"""Exercise the exact-F33 ICU-S completion/timeout preemption window."""
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
DEFAULT_OUT = REPO_ROOT / "build/out/targets/camry-8965F3307000/crypto-irq-preemption"
PRELUDE = (0x62E6A, 0x884EA, 0x69064, 0x6A0AE)
ICUS_INPUTS = (
    "ICUSIRQSTS", "ICUSSTS", "ICUSSTS2", "ICUSREG10", "ICUSREG20", "ICUSOUT",
    "ICUSREG90", "ICUSREG94", "ICUSREG98", "ICUSREG9C", "ICUSREGA0",
    "ICUSREGA4", "ICUSREGA8", "ICUSREGAC", "ICUSREGB0", "ICUSREGB4",
    "ICUSREGB8", "ICUSREGBC", "ICUSREGE0", "ICUSREGF0", "ICUSREGF4",
    "ICUSREGF8", "ICUSREGFC",
)
NATIVE_SECOC = tuple(
    (bytes.fromhex(sync), bytes.fromhex(d7))
    for sync, d7 in (
        ("01b6002576d1e72b", "00000000000000df0200000000000000000000000000000000000000ff84051f"),
        ("01b6002576d1e72b", "00000000000000df0200000000000000000000000000000000000000386a0563"),
        ("01b6002576d1e72b", "00000000000000df02000000000000000000000000000000000000007835e116"),
        ("01b6002576d1e72b", "00000000000000df0000000000000000000000000000000000000000b89a3564"),
        ("01b6002576d1e72b", "00000000000000df0000000000000000000000000000000000000000fa740cfe"),
        ("01b6002576d1e72b", "00000000000000df0000000000000000000000000000000000000000360aa99c"),
        ("01b6002576d1e72b", "00000000000000df00000000000000000000000000000000000000007ebb4bc6"),
        ("01b6002576d1e72b", "00000000000000df0200000000000000000000000000000000000000be0255e0"),
        ("01b6002576d1e72b", "00000000000000df0200000000000000000000000000000000000000ffc874dd"),
        ("01b6002576d1e72b", "00000000000000df000000000000000000000000000000000000000049e53a16"),
        ("01b6002580a78958", "00000000000000df00000000000000000000000000000000000000008372c8d8"),
        ("01b6002580a78958", "00000000000000df0200000000000000000000000000000000000000cc8a7612"),
    )
)


def build_base() -> dict[str, Any]:
    image = can.IMAGE.read_bytes()
    snapshot = can.SNAPSHOT.read_bytes()
    route_table = can.route_ids(image)
    routes: list[int] = []
    lengths: list[int] = []
    payloads: list[bytes] = []
    for _ in range(4):
        for route in range(13, 18):
            routes.append(route)
            lengths.append(8)
            payloads.append(bytes([4, 1]) + bytes(6) if route == 13 else bytes([route]) * 8)
    for sync, d7 in NATIVE_SECOC:
        routes.extend((4, 36))
        lengths.extend((8, 32))
        payloads.extend((sync, d7))
    scenario = can.trial_scenario(
        0, tuple(routes), tuple(lengths), tuple(payloads), route_table, snapshot, 1,
        prelude=PRELUDE,
    )
    scenario["name"] = "crypto_irq_preemption_baseline"
    scenario["registers"].update({
        "RBASE": "0", "INTBP": "0x20200", "CTPC": "0", "CTPSW": "0",
        "ISPR": "0", "ICSR": "0", "INTCFG": "0", "PSW": "0", "PMR": "0",
    })
    scenario["events"].extend({
        "kind": "register-input", "register": register, "value": "0",
        "after_instructions": 0,
        "evidence": "Synthetic idle/storage ICU-S input; no cryptographic verdict",
    } for register in ICUS_INPUTS)
    scenario["checks"].extend((
        {
            "name": "crypto-state", "kind": "memory", "address": "0xfebf1000",
            "size": 0x500, "equals_hex": "ff" * 0x500,
        },
        {
            "name": "landing-zone-race", "kind": "memory",
            "address": hex(can.LANDING[0]),
            "size": can.LANDING[1] - can.LANDING[0],
            "equals_hex": "ff" * (can.LANDING[1] - can.LANDING[0]),
        },
    ))
    return scenario


def timeout_entry(report: dict[str, Any]) -> int:
    trace = report["instruction_trace"]
    for index in range(len(trace) - 1, -1, -1):
        if int(trace[index]["pc"], 0) != 0x88EC0:
            continue
        if any(int(row["pc"], 0) == 0x88574 for row in trace[index:index + 80]):
            return int(trace[index]["instruction"])
    raise RuntimeError("command-five timeout/recovery window was not reached")


def add_completion(scenario: dict[str, Any], name: str, tick: int) -> dict[str, Any]:
    result = copy.deepcopy(scenario)
    result["name"] = name
    result["events"].extend((
        {
            "kind": "register-input", "register": "ICUSSTS", "value": "0",
            "after_instructions": tick,
            "evidence": "Synthetic ICU-S idle completion state at an exact instruction boundary",
        },
        {
            "kind": "register-input", "register": "ICUSSTS2", "value": "2",
            "after_instructions": tick,
            "evidence": "Synthetic ICU-S completion flag at an exact instruction boundary",
        },
        {
            "kind": "interrupt", "channel": 292, "firmware_control": "0x48",
            "after_instructions": tick + 1,
            "evidence": (
                "Exact startup 62E6A writes EIC292=0x48 and INTBP[292]=0x66142; "
                "synthetic ICU-S request timing"
            ),
        },
    ))
    return result


def actual(report: dict[str, Any], name: str) -> bytes:
    row = next(check for check in report["checks"] if check["name"] == name)
    return bytes.fromhex(row["actual"])


def summarize(report: dict[str, Any]) -> dict[str, Any]:
    events = Counter(event["kind"] for event in report.get("device_events", []))
    commands = Counter(
        event["command"] for event in report.get("device_events", [])
        if event["kind"] == "icus-command"
    )
    writes = {
        int(access["address"], 0) for access in report.get("memory_accesses", [])
        if access.get("kind") == "write"
    }
    return {
        "scenario": report["scenario"],
        "termination_reason": report.get("termination_reason"),
        "fault": report.get("fault"),
        "instruction_count": report.get("instruction_count"),
        "interrupt_enter": events["interrupt-enter"],
        "interrupt_return": events["interrupt-return"],
        "commands": {str(key): value for key, value in sorted(commands.items())},
        "crypto_state_sha256": hashlib.sha256(actual(report, "crypto-state")).hexdigest(),
        "landing_writes": [
            hex(address) for address in sorted(writes)
            if can.LANDING[0] <= address < can.LANDING[1]
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=True)
    (REPO_ROOT / "build/tmp").mkdir(parents=True, exist_ok=True)
    base = build_base()
    with tempfile.TemporaryDirectory(prefix="crypto-irq-", dir=REPO_ROOT / "build/tmp") as td:
        work = Path(td)
        baseline_path = work / "baseline.json"
        baseline_path.write_text(json.dumps(base), encoding="utf-8")
        baseline = capture_many(TARGET, [baseline_path], out / "baseline", instruction_trace=True)[0]
        entry = timeout_entry(baseline)
        scenarios = (
            add_completion(base, "crypto_irq_before_global_state_load", entry + 3),
            add_completion(base, "crypto_irq_after_global_state_load", entry + 4),
        )
        paths: list[Path] = []
        for scenario in scenarios:
            path = work / f"{scenario['name']}.json"
            path.write_text(json.dumps(scenario), encoding="utf-8")
            paths.append(path)
        reports = capture_many(TARGET, paths, out / "reports")
    summary = {
        "schema": "camry-f33-crypto-irq-preemption-v1",
        "image_sha256": can.IMAGE_SHA256,
        "timeout_entry_instruction": entry,
        "cases": [summarize(report) for report in reports],
    }
    (out / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
