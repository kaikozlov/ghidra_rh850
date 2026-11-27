#!/usr/bin/env python3
"""Replay retained Camry CAN captures through continuous READY-state machine cycles."""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import re
import struct
import statistics
import time
from collections import Counter, defaultdict, deque
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from tools import REPO_ROOT
from tools.emulation.p1me_machine import capture_many
from tools.targets.camry.analysis.convert_camry_capture_machine_events import (
    RAM_BASE,
    SNAPSHOT as PROGRAMMING_SNAPSHOT,
    decode_firmware_rules,
    load_capture,
)
from tools.targets.camry.research import explore_camry_f33_stateful_can_cycles as cycles

TARGET = "camry-8965F3307000"
SCHEMA = "camry-f33-capture-machine-replay-v1"
CATALOG = REPO_ROOT / "data/generated/camry_8965F3307000_execution_contexts.json"
MACHINE_MODEL = REPO_ROOT / "data/generated/p1me_machine.json"
SNAPSHOT = PROGRAMMING_SNAPSHOT.with_name("normal_operation_local_ram_pe1.bin")
SNAPSHOT_SHA256 = "8b34342ee4f97da849621d96bcc02ffbb796021533702f025dc3607e168448cf"
SERIAL_INITIALIZER = 0x61260
BOARD_FIXTURE = (
    REPO_ROOT
    / "tests/fixtures/rh850/machine/camry-8965F3307000"
    / "original-reset-to-runtime-synthetic-board.json"
)
DEFAULT_OUT = REPO_ROOT / "build/out/targets/camry-8965F3307000/capture-replay"
PRELUDE = cycles.SEQUENCER
RETURN_STUB = cycles.RETURN_STUB
CAN_INIT = 0x7A132
INTERRUPT_INITIALIZER = 0x62E6A
CAN_PREPARE = 0x7FAFA
CAN_ACTIVATE = 0x7C830
NORMAL_CHECKPOINT_REGISTERS = {
    "r1": "0x1", "r2": "0", "r6": "0", "r7": "0",
    "r8": "0xfebe8c0a", "r9": "0xfebe8c14",
    "r10": "0", "r11": "0", "r12": "4", "r13": "0",
    "r14": "1", "r15": "1", "r16": "0x3e7f", "r17": "0x1387",
    "r18": "0x3e7f", "r19": "0x3e7f",
    "r20": "0", "r21": "0", "r22": "0", "r23": "0",
    "r24": "0", "r25": "0", "r26": "0", "r27": "0",
    "r28": "0", "r29": "0", "ep": "0xfebe39db",
    "sp": "0xfebe1ff8", "gp": "0xfebeb800", "tp": "0x23dfc",
    "lp": "0x660a8",
    "ASID": "0", "CTPC": "0", "CTPSW": "0",
    "EBASE": "0x20000", "EIIC": "0x1085", "EIPC": "0x65986",
    "EIPSW": "0x18001", "EIWR": "0", "FEPC": "0",
    "FPCC": "0", "FPCFG": "0x100", "FPEPC": "0",
    "FPSR": "0x60000", "FPST": "0",
    "ICDATL": "0", "ICSR": "0", "ICTAGH": "0", "ICTAGL": "0",
    "INTBP": "0x20200", "INTCFG": "0", "ISPR": "0",
    "MCA": "0", "MEA": "0", "MPM": "0", "PMR": "0",
    "PSW": "0x18000", "RBASE": "0", "SCCFG": "0",
    "MPLA0": "0", "MPLA1": "0xfebf7c00",
    "MPLA2": "0xfebe0000", "MPLA3": "0xfebe2000",
    "MPLA4": "0xfebe3800", "MPLA5": "0xfebef400",
    "MPLA6": "0xfebf3400", "MPLA7": "0xfebf3800",
    "MPLA8": "0xfebf6000", "MPLA9": "0", "MPLA10": "0",
    "MPLA11": "0xfebffc00", "MPLA12": "0xfec00000",
    "MPLA13": "0", "MPLA14": "0", "MPLA15": "0",
    "MPUA0": "0xfebdfffc", "MPUA1": "0xfebffbfc",
    "MPUA2": "0xfebe1ffc", "MPUA3": "0xfebe37fc",
    "MPUA4": "0xfebef3fc", "MPUA5": "0xfebf33fc",
    "MPUA6": "0xfebf37fc", "MPUA7": "0xfebf5ffc",
    "MPUA8": "0xfebf7bfc", "MPUA9": "0", "MPUA10": "0",
    "MPUA11": "0xfebffffc", "MPUA12": "0xfffffffc",
    "MPUA13": "0", "MPUA14": "0", "MPUA15": "0",
}
FOREGROUND_WAIT = 0x66066
FOREGROUND_COMPLETE = 0x660BC
FOREGROUND_TRIAL_MAX_INSTRUCTIONS = 600_000
DIAGNOSTIC_READY_EMPTY_CYCLES = 25
BOOT_TRANSFER = 0x65F5E
REFERENCE_CYCLE_INSTRUCTIONS = 862
REFERENCE_INSTRUCTIONS_PER_SECOND = 175_000
ESTIMATED_SECONDS_PER_PERIOD = (
    REFERENCE_CYCLE_INSTRUCTIONS / REFERENCE_INSTRUCTIONS_PER_SECOND
)
REPLAY_PREFIX_TRIALS = 4 + DIAGNOSTIC_READY_EMPTY_CYCLES * 3
REPLAY_PREFIX_STEPS = 6 + DIAGNOSTIC_READY_EMPTY_CYCLES * 3
REPLAY_EVENT_KINDS = ("can-rx", "can-rx-discard", "can-rx-pop", "can-tx")

@dataclass(frozen=True)
class CapturePeriod:
    index: int
    receive: tuple[dict[str, Any], ...]
    completions: tuple[dict[str, Any], ...]


@dataclass(frozen=True)
class FieldMutation:
    can_id: int
    name: str
    masks: tuple[tuple[int, int], ...]
    destinations: tuple[tuple[int, int, str], ...]
    period_index: int
    receive_index: int


def load_capture_scenario(path: Path) -> dict[str, Any]:
    scenario = json.loads(path.read_text(encoding="utf-8"))
    source = scenario.get("source", {})
    if source.get("kind") != "capture" or not source.get("sha256"):
        raise ValueError(f"{path}: scenario lacks capture identity")
    return scenario


def capture_periods(scenario: dict[str, Any], limit: int | None = None) -> list[CapturePeriod]:
    """Map converted events to periods without reordering within each event class."""
    events = scenario.get("events", [])
    if any(int(row["after_instructions"]) < 0 for row in events):
        raise ValueError("capture event has a negative period")
    last = max((int(row["after_instructions"]) for row in events), default=-1)
    count = last + 1 if limit is None else limit
    if count < 0:
        raise ValueError("period limit must be nonnegative")
    receive: dict[int, list[dict[str, Any]]] = defaultdict(list)
    completions: dict[int, list[dict[str, Any]]] = defaultdict(list)
    previous = -1
    for row in events:
        period = int(row["after_instructions"])
        if period < previous:
            raise ValueError("capture events are not ordered by period")
        previous = period
        if period >= count:
            continue
        normalized = copy.deepcopy(row)
        normalized["after_instructions"] = 0
        if row["kind"] == "can-rx":
            receive[period].append(normalized)
        elif row["kind"] == "can-tx-complete":
            completions[period].append(normalized)
        else:
            raise ValueError(f"capture contains unsupported event {row['kind']}")
    return [
        CapturePeriod(index, tuple(receive[index]), tuple(completions[index]))
        for index in range(count)
    ]

def acceptance_probe_periods(
    periods: Sequence[CapturePeriod], window_periods: int = 200,
) -> list[CapturePeriod]:
    """Spread one captured frame per (identifier, DLC) across a quiet proof window."""
    first: dict[tuple[int, int], dict[str, Any]] = {}
    for period in periods:
        for row in period.receive:
            key = (int(row["can_id"], 0), len(bytes.fromhex(row["data_hex"])))
            first.setdefault(key, copy.deepcopy(row))
    if len(first) > window_periods:
        raise ValueError("acceptance proof window is shorter than its (identifier, DLC) set")
    receive: list[list[dict[str, Any]]] = [[] for _ in range(window_periods)]
    stride = max(1, window_periods // max(1, len(first)))
    for index, row in enumerate(first.values()):
        receive[min(index * stride, window_periods - 1)].append(row)
    return [
        CapturePeriod(index, tuple(rows), ())
        for index, rows in enumerate(receive)
    ]

def append_call_at(code: bytes, base: int, target: int) -> bytes:
    continuation = base + len(code) + 14
    return code + cycles.mov(31, continuation) + cycles.mov(1, target) + struct.pack("<H", 0x0061)


def prelude_bytes() -> bytes:
    code = append_call_at(b"", PRELUDE, INTERRUPT_INITIALIZER)
    code = append_call_at(code, PRELUDE, SERIAL_INITIALIZER)
    code = append_call_at(code, PRELUDE, CAN_INIT)
    code += cycles.mov(6, 0)
    code = append_call_at(code, PRELUDE, CAN_PREPARE)
    code += cycles.mov(6, 0)
    code = append_call_at(code, PRELUDE, CAN_ACTIVATE)
    code += cycles.mov(1, FOREGROUND_WAIT) + struct.pack("<H", 0x0061)
    return code


def probe_checks(mutations: Sequence[FieldMutation], snapshot: bytes) -> list[dict[str, Any]]:
    spans = sorted({destination for mutation in mutations for destination in mutation.destinations})
    return [
        {
            "name": f"destination-{address:08x}-{size}",
            "kind": "memory",
            "address": hex(address),
            "size": size,
            "equals_hex": snapshot[address - RAM_BASE:address - RAM_BASE + size].hex(),
        }
        for address, size, _name in spans
        if address >= RAM_BASE
    ]

READINESS_MODE_CHECKS = (
    {
        "name": "end-live-mode",
        "kind": "memory", "address": "0xfebeb11a", "size": 2,
        "equals_hex": "0207",
    },
    {
        "name": "end-desired-mode",
        "kind": "memory", "address": "0xfebee8cc", "size": 4,
        "equals_hex": "02070000",
    },
    {
        "name": "end-active-mode",
        "kind": "memory", "address": "0xfebe8c06", "size": 2,
        "equals_hex": "0207",
    },
)
END_MODE_CHECKS = READINESS_MODE_CHECKS


def build_replay_scenario(
    source: dict[str, Any],
    periods: Sequence[CapturePeriod],
    name: str,
    *,
    include_completions: bool = True,
    foreground_ticks: bool = True,
    mutations: Sequence[FieldMutation] = (),
    checks: Sequence[dict[str, Any]] = (),
    final_receive_limit: int | None = None,
    final_completion_limit: int | None = None,
) -> dict[str, Any]:
    """Build state-continuous native foreground cycles after an ordinary full boot."""
    snapshot = SNAPSHOT.read_bytes()
    if hashlib.sha256(snapshot).hexdigest() != SNAPSHOT_SHA256:
        raise RuntimeError("normal-operation RAM snapshot identity drifted")
    vehicle_snapshot = PROGRAMMING_SNAPSHOT.read_bytes()
    retained_vehicle_modes = {
        "0xFEBEB11A": int.from_bytes(
            vehicle_snapshot[0xFEBEB11A - RAM_BASE:0xFEBEB11C - RAM_BASE], "little",
        ),
        "0xFEBEE8CC": int.from_bytes(
            vehicle_snapshot[0xFEBEE8CC - RAM_BASE:0xFEBEE8D0 - RAM_BASE], "little",
        ),
        "0xFEBE8C06": int.from_bytes(
            vehicle_snapshot[0xFEBE8C06 - RAM_BASE:0xFEBE8C08 - RAM_BASE], "little",
        ),
    }
    if set(retained_vehicle_modes.values()) != {0x0900}:
        raise RuntimeError(
            f"retained vehicle programming-mode cells drifted: {retained_vehicle_modes}",
        )
    board = json.loads(BOARD_FIXTURE.read_text(encoding="utf-8"))
    mutation_by_id: dict[int, list[FieldMutation]] = defaultdict(list)
    for mutation in mutations:
        mutation_by_id[mutation.can_id].append(mutation)

    boot_checks = [
        {
            "name": "desired mode below programming band",
            "kind": "memory", "address": "0xfebee8cc", "size": 4,
            "equals_hex": "00010000",
        },
        {
            "name": "active mode below programming band",
            "kind": "memory", "address": "0xfebe8c06", "size": 2,
            "equals_hex": "0000",
        },
        *[
            {
                "name": f"{name} inactive",
                "kind": "memory", "address": address, "size": size,
                "equals_hex": "00" * size,
            }
            for name, address, size in (
                ("direct crypto operation", "0xfebe5091", 2),
                ("collected crypto operation", "0xfebe5096", 2),
                ("test crypto operation", "0xfebe509b", 2),
                ("DCM transaction context", "0xfebe5624", 32),
            )
        ],
        {
            "name": "RSCFD global operation status clear",
            "kind": "memory", "address": "0xffd2008c", "size": 4,
            "equals_hex": "00000000",
        },
    ]
    steps: list[dict[str, Any]] = [
        {
            "kind": "checkpoint",
            "name": "cold-start",
            "after_instructions": 0,
        },
        {
            "kind": "trial",
            "name": "ordinary-power-on-to-foreground",
            "max_instructions": 35_000_000,
            "stop_addresses": [hex(BOOT_TRANSFER), "0x619be"],
            "stop_after_arrivals": [{"address": hex(FOREGROUND_WAIT), "count": 2}],
            "events": [],
            "checks": [],
        },
        {
            "kind": "trial",
            "name": "settle-pending-serial-completions",
            "max_instructions": 512,
            "stop_addresses": [hex(BOOT_TRANSFER), "0x619be"],
            "stop_after_arrivals": [{"address": hex(FOREGROUND_WAIT), "count": 65}],
            "events": [],
            "checks": [],
        },
        {
            "kind": "trial",
            "name": "bootstrap-native-cycle",
            "max_instructions": FOREGROUND_TRIAL_MAX_INSTRUCTIONS,
            "stop_addresses": [hex(BOOT_TRANSFER), "0x619be", hex(FOREGROUND_COMPLETE)],
            "stop_after_arrivals": [],
            "events": [],
            "checks": [],
        },
        {
            "kind": "trial",
            "name": "bootstrap-return-to-wait",
            "max_instructions": 4,
            "stop_addresses": [hex(BOOT_TRANSFER), "0x619be"],
            "stop_after_arrivals": [
                {"address": hex(FOREGROUND_WAIT), "count": 1},
            ],
            "events": [],
            "checks": boot_checks,
        },
    ]
    for activation_index in range(DIAGNOSTIC_READY_EMPTY_CYCLES):
        final_activation = activation_index == DIAGNOSTIC_READY_EMPTY_CYCLES - 1
        steps.extend((
            {
                "kind": "trial",
                "name": f"diagnostic-readiness-{activation_index:02d}-native-cycle",
                "max_instructions": FOREGROUND_TRIAL_MAX_INSTRUCTIONS,
                "stop_addresses": [hex(BOOT_TRANSFER), "0x619be", hex(FOREGROUND_COMPLETE)],
                "stop_after_arrivals": [],
                "events": [],
                "checks": [],
            },
            {
                "kind": "trial",
                "name": f"diagnostic-readiness-{activation_index:02d}-return-to-wait",
                "max_instructions": 4,
                "stop_addresses": [hex(BOOT_TRANSFER), "0x619be"],
                "stop_after_arrivals": [
                    {"address": hex(FOREGROUND_WAIT), "count": 1},
                ],
                "events": [],
                "checks": [],
            },
            {
                "kind": "trial",
                "name": f"diagnostic-readiness-{activation_index:02d}-tx-completions",
                "max_instructions": 1,
                "stop_addresses": [],
                "stop_after_arrivals": [
                    {"address": hex(FOREGROUND_WAIT), "count": 1},
                ],
                "events": [
                    {
                        "kind": "can-tx-complete",
                        "buffer": buffer,
                        "after_instructions": 0,
                        "tolerate_no_pending": True,
                        "evidence": "Empty-cycle bus completion before capture period zero",
                    }
                    for buffer in range(16, 32)
                ],
                "checks": list(READINESS_MODE_CHECKS) if final_activation else [],
            },
        ))
    steps.append({
        "kind": "checkpoint",
        "name": "normal-operation",
    })
    for period in periods:
        receive = list(copy.deepcopy(period.receive))
        if period.index == periods[-1].index and final_receive_limit is not None:
            receive = receive[:final_receive_limit]
        for receive_index, row in enumerate(receive):
            can_id = int(row["can_id"], 0)
            payload = bytearray.fromhex(row["data_hex"])
            applied = False
            for mutation in mutation_by_id.get(can_id, ()):
                if (period.index, receive_index) != (
                    mutation.period_index, mutation.receive_index,
                ):
                    continue
                for byte_index, mask in mutation.masks:
                    if byte_index < len(payload):
                        payload[byte_index] ^= mask
                        applied = True
            row["data_hex"] = payload.hex()
            if applied:
                row["evidence"] += "; single-field replay mutation"
        for receive_index, row in enumerate(receive):
            steps.append({
                "kind": "trial",
                "name": (
                    f"period-{period.index:05d}-receive-{receive_index:03d}-ingress"
                ),
                "max_instructions": 100_000,
                "stop_addresses": [],
                "stop_after_arrivals": [
                    {"address": hex(FOREGROUND_WAIT), "count": 2},
                ],
                "events": [row],
                "checks": [],
            })
        if foreground_ticks:
            steps.append({
                "kind": "trial",
                "name": f"period-{period.index:05d}-native-cycle",
                "max_instructions": FOREGROUND_TRIAL_MAX_INSTRUCTIONS,
                "stop_addresses": [hex(BOOT_TRANSFER), "0x619be", hex(FOREGROUND_COMPLETE)],
                "stop_after_arrivals": [],
                "events": [],
                "checks": [],
            })
            steps.append({
                "kind": "trial",
                "name": f"period-{period.index:05d}-return-to-wait",
                "max_instructions": 4,
                "stop_addresses": [hex(BOOT_TRANSFER), "0x619be"],
                "stop_after_arrivals": [
                    {"address": hex(FOREGROUND_WAIT), "count": 1},
                ],
                "events": [],
                "checks": [],
            })
        completions = copy.deepcopy(period.completions) if include_completions else []
        if period.index == periods[-1].index and final_completion_limit is not None:
            completions = completions[:final_completion_limit]
        for row in completions:
            row["tolerate_no_pending"] = True
        steps.append({
            "kind": "trial",
            "name": f"period-{period.index:05d}-transmit-completions",
            "max_instructions": 1,
            "stop_addresses": [],
            "stop_after_arrivals": [{"address": hex(FOREGROUND_WAIT), "count": 1}],
            "events": completions,
            "checks": list(checks) if period.index == periods[-1].index else [],
        })

    board.update({
        "name": name,
        "source": {
            **copy.deepcopy(source),
            "board_fixture": str(BOARD_FIXTURE.relative_to(REPO_ROOT)),
            "normal_ram_sha256": SNAPSHOT_SHA256,
            "empty_cycles_before_capture": DIAGNOSTIC_READY_EMPTY_CYCLES + 1,
            "operational_replay_mode": "0x0702",
            "retained_vehicle_mode_cells": {
                address: hex(value) for address, value in retained_vehicle_modes.items()
            },
            "retained_vehicle_mode_interpretation": (
                "programming transition; request 9 at 0x4D618 reaches boot transfer 0x65F5E"
            ),
        },
        "max_instructions": 2_000_000_000,
        "stop_addresses": [hex(RETURN_STUB)],
        "steps": steps,
        "expected_termination": "stop-address",
        "checks": [],
    })
    return board


def write_scenario(path: Path, scenario: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(scenario, separators=(",", ":")) + "\n", encoding="utf-8")


def trial_rows(report: dict[str, Any]) -> list[dict[str, Any]]:
    return list(report.get("checkpointing", {}).get("trials", []))


def successful(report: dict[str, Any], expected_trials: int) -> bool:
    rows = trial_rows(report)
    return (
        len(rows) == expected_trials
        and report.get("termination_reason") != "runner-error"
        and all(
            row.get("termination_reason") == (
                "stop-address" if row["name"].endswith("native-cycle")
                else "stop-after-arrivals"
            )
            for row in rows
        )
        and all(
            not row["name"].endswith("native-cycle")
            or row.get("final_pc") == "0x000660BC"
            for row in rows
        )
    )


def expected_trial_count(
    periods: Sequence[CapturePeriod], foreground_ticks: bool = True,
) -> int:
    return REPLAY_PREFIX_TRIALS + sum(
        len(period.receive)
        + (2 if foreground_ticks else 0)
        + 1
        for period in periods
    )

def batch_replay_scenarios(
    cases: Sequence[tuple[str, dict[str, Any]]], name: str,
) -> dict[str, Any]:
    combined = copy.deepcopy(cases[0][1])
    combined["name"] = name
    combined["source"] = {
        **combined["source"],
        "batch_cases": [case_name for case_name, _scenario in cases],
    }
    steps = combined["steps"][:REPLAY_PREFIX_STEPS]
    for case_name, scenario in cases:
        steps.append({"kind": "restore", "checkpoint": "normal-operation"})
        for original in scenario["steps"][REPLAY_PREFIX_STEPS:]:
            step = copy.deepcopy(original)
            if step["kind"] == "trial":
                step["name"] = f"{case_name}::{step['name']}"
            steps.append(step)
    combined["steps"] = steps
    return combined


def split_replay_batch_report(
    report: dict[str, Any], case_names: Sequence[str],
) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = {name: [] for name in case_names}
    for original in trial_rows(report):
        name = str(original.get("name", ""))
        if "::" not in name:
            continue
        case_name, trial_name = name.split("::", 1)
        if case_name not in grouped:
            continue
        trial = copy.deepcopy(original)
        trial["name"] = trial_name
        grouped[case_name].append(trial)
    return [{
        "termination_reason": report.get("termination_reason"),
        "error": report.get("error"),
        "checkpointing": {"trials": grouped[name]},
    } for name in case_names]


def configure_replay_capture(scenario: dict[str, Any], *, full_capture_rows: bool = False) -> None:
    """Keep rows used by reception, transmit and candump reports unless asked for full evidence."""
    if full_capture_rows:
        return
    for step in scenario["steps"]:
        if step.get("kind") == "trial" and "capture_rows" not in step:
            step.setdefault("capture_event_kinds", list(REPLAY_EVENT_KINDS))


def run_once(
    source: dict[str, Any], periods: Sequence[CapturePeriod], out: Path, name: str,
    *, full_capture_rows: bool = False, **kwargs: Any,
) -> tuple[dict[str, Any], Path]:
    scenario = build_replay_scenario(source, periods, name, **kwargs)
    configure_replay_capture(scenario, full_capture_rows=full_capture_rows)
    scenario_path = out / "scenarios" / f"{name}.json"
    write_scenario(scenario_path, scenario)
    report = capture_many(TARGET, [scenario_path], out / "reports", instruction_trace=False)[0]
    return report, scenario_path


def event_rows(report: dict[str, Any]) -> Iterable[dict[str, Any]]:
    for trial in trial_rows(report):
        yield from trial.get("event_rows", [])


def capture_frame_identity(row: dict[str, Any]) -> tuple[int, int] | None:
    if row.get("kind") not in ("can-rx", "can-rx-discard"):
        return None
    return int(row["can_id"], 0), len(bytes.fromhex(row["data_hex"]))


def summarize_reception(report: dict[str, Any]) -> dict[str, Any]:
    queued: deque[tuple[int, int]] = deque()
    enqueued: Counter[tuple[int, int]] = Counter()
    popped: Counter[tuple[int, int]] = Counter()
    discarded: Counter[tuple[int, int]] = Counter()
    device_counts: Counter[str] = Counter()
    for trial in trial_rows(report):
        counts = trial.get("event_kind_counts")
        if counts is not None:
            device_counts.update(counts)
        for row in trial.get("event_rows", []):
            kind = str(row.get("kind"))
            if counts is None:
                device_counts[kind] += 1
            identity = capture_frame_identity(row)
            if kind == "can-rx" and identity is not None:
                queued.append(identity)
                enqueued[identity] += 1
            elif kind == "can-rx-discard" and identity is not None:
                discarded[identity] += 1
            elif kind == "can-rx-pop" and queued:
                popped[queued.popleft()] += 1
    keys = sorted(set(enqueued) | set(popped) | set(discarded))
    unconsumed = sum(enqueued.values()) - sum(popped.values())
    return {
        "frames_presented": sum(enqueued.values()) + sum(discarded.values()),
        "enqueued": sum(enqueued.values()),
        "popped": sum(popped.values()),
        "dropped": sum(discarded.values()) + unconsumed,
        "per_id_dlc": [
            {
                "can_id": f"0x{can_id:X}",
                "dlc": dlc,
                "enqueued": enqueued[(can_id, dlc)],
                "popped": popped[(can_id, dlc)],
                "discarded": discarded[(can_id, dlc)],
                "dropped": (
                    discarded[(can_id, dlc)]
                    + enqueued[(can_id, dlc)] - popped[(can_id, dlc)]
                ),
            }
            for can_id, dlc in keys
        ],
        "device_event_kinds": dict(sorted(device_counts.items())),
    }


def reception_table(periods: Sequence[CapturePeriod], reception: dict[str, Any]) -> list[dict[str, Any]]:
    captured: Counter[tuple[int, int]] = Counter()
    for period in periods:
        for row in period.receive:
            captured[(int(row["can_id"], 0), len(bytes.fromhex(row["data_hex"])))] += 1
    runtime = {
        (int(row["can_id"], 0), int(row["dlc"])): row
        for row in reception["per_id_dlc"]
    }
    return [
        {
            "can_id": f"0x{can_id:X}",
            "dlc": dlc,
            "capture_frames": count,
            "enqueued_before_stop": runtime.get((can_id, dlc), {}).get("enqueued", 0),
            "popped_before_stop": runtime.get((can_id, dlc), {}).get("popped", 0),
            "discarded_before_stop": runtime.get((can_id, dlc), {}).get("discarded", 0),
            "dropped_before_stop": runtime.get((can_id, dlc), {}).get("dropped", 0),
        }
        for (can_id, dlc), count in sorted(captured.items())
    ]


def machine_transmits(report: dict[str, Any]) -> list[dict[str, Any]]:
    return [row for row in event_rows(report) if row.get("kind") == "can-tx"]

def machine_transmit_records(report: dict[str, Any]) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    occurrence: Counter[tuple[int, int]] = Counter()
    for trial in trial_rows(report):
        match = re.match(r"period-(\d+)-", str(trial.get("name", "")))
        period = int(match.group(1)) if match else -1
        for row in trial.get("event_rows", []):
            if row.get("kind") != "can-tx":
                continue
            can_id = int(row["can_id"], 0)
            key = (period, can_id)
            records.append({
                "period": period,
                "can_id": can_id,
                "occurrence": occurrence[key],
                "data_hex": row["data_hex"],
            })
            occurrence[key] += 1
    return records
def transmit_probe_metadata() -> list[dict[str, int]]:
    model = json.loads(MACHINE_MODEL.read_text(encoding="utf-8"))
    rows = []
    for register in model["manual"]["registers"]:
        if register.get("trigger") != "rscfd-transmit":
            continue
        address = int(register["address"])
        rows.append({
            "buffer": address - 0xFFD20250,
            "control_address": address,
            "payload_address": int(register["payload_address"]),
        })
    return rows


def configure_transmit_observation(scenario: dict[str, Any]) -> None:
    probes = transmit_probe_metadata()
    for step in scenario["steps"]:
        if step.get("kind") != "trial":
            continue
        step.pop("capture_event_kinds", None)
        step["capture_rows"] = False
        if not re.fullmatch(r"period-\d+-native-cycle", str(step.get("name", ""))):
            continue
        step["checks"] = [
            *step.get("checks", []),
            *[
                check
                for probe in probes
                for check in (
                    {
                        "name": f"tx-{probe['buffer']}-control",
                        "kind": "memory",
                        "address": hex(probe["control_address"]),
                        "size": 1,
                    },
                    {
                        "name": f"tx-{probe['buffer']}-payload",
                        "kind": "memory",
                        "address": hex(probe["payload_address"]),
                        "size": 20,
                    },
                )
            ],
        ]


def observed_transmit_records(report: dict[str, Any]) -> list[dict[str, Any]]:
    probes = {row["buffer"]: row for row in transmit_probe_metadata()}
    pending = {buffer: False for buffer in probes}
    occurrence: Counter[tuple[int, int]] = Counter()
    records = []
    for trial in trial_rows(report):
        match = re.fullmatch(r"period-(\d+)-native-cycle", str(trial.get("name", "")))
        if match is None:
            continue
        period = int(match.group(1))
        checks = {
            str(row["name"]): str(row.get("actual", "unavailable"))
            for row in trial.get("checks", [])
        }
        for buffer in probes:
            control_hex = checks.get(f"tx-{buffer}-control", "unavailable")
            payload_hex = checks.get(f"tx-{buffer}-payload", "unavailable")
            if not re.fullmatch(r"[0-9a-fA-F]{2}", control_hex):
                continue
            active = bool(int.from_bytes(bytes.fromhex(control_hex), "little") & 1)
            if active and not pending[buffer] and re.fullmatch(
                r"[0-9a-fA-F]{40}", payload_hex,
            ):
                raw = bytes.fromhex(payload_hex)
                can_id = int.from_bytes(raw[:4], "little") & 0x1FFFFFFF
                key = (period, can_id)
                records.append({
                    "period": period,
                    "can_id": can_id,
                    "occurrence": occurrence[key],
                    "data_hex": raw[12:20].hex(),
                    "buffer": buffer,
                })
                occurrence[key] += 1
            pending[buffer] = active
    return records


def transmit_difference(
    baseline: Sequence[dict[str, Any]], mutated: Sequence[dict[str, Any]],
) -> dict[str, Any] | None:
    def keyed(rows: Sequence[dict[str, Any]]) -> dict[tuple[int, int, int], bytes]:
        return {
            (int(row["period"]), int(row["can_id"]), int(row["occurrence"])):
            bytes.fromhex(row["data_hex"])
            for row in rows
        }

    left, right = keyed(baseline), keyed(mutated)
    for key in sorted(set(left) | set(right)):
        before, after = left.get(key), right.get(key)
        if before == after:
            continue
        differences = []
        for index in range(max(len(before or b""), len(after or b""))):
            old = before[index] if before is not None and index < len(before) else None
            new = after[index] if after is not None and index < len(after) else None
            if old == new:
                continue
            xor = (old or 0) ^ (new or 0)
            differences.append({
                "byte": index,
                "baseline": None if old is None else f"0x{old:02X}",
                "mutated": None if new is None else f"0x{new:02X}",
                "xor_mask": f"0x{xor:02X}",
                "bits": [bit for bit in range(8) if xor & (1 << bit)],
            })
        return {
            "period": key[0], "can_id": f"0x{key[1]:X}",
            "occurrence": key[2],
            "baseline_hex": None if before is None else before.hex(),
            "mutated_hex": None if after is None else after.hex(),
            "differing_bytes": differences,
        }
    return None

def transmit_differences(
    baseline: Sequence[dict[str, Any]], changed: Sequence[dict[str, Any]],
) -> list[dict[str, Any]]:
    remaining = list(changed)
    differences = []
    while difference := transmit_difference(baseline, remaining):
        differences.append(difference)
        key = (
            int(difference["period"]),
            int(difference["can_id"], 0),
            int(difference["occurrence"]),
        )
        baseline_by_key = {
            (int(row["period"]), int(row["can_id"]), int(row["occurrence"])): row
            for row in baseline
        }
        replacement = baseline_by_key.get(key)
        remaining = [
            row for row in remaining
            if (int(row["period"]), int(row["can_id"]), int(row["occurrence"])) != key
        ]
        if replacement is not None:
            remaining.append(replacement)
    return differences


def write_candump(
    path: Path, source: dict[str, Any], periods: Sequence[CapturePeriod],
    report: dict[str, Any],
) -> None:
    rows: list[tuple[float, int, str, int, bytes]] = []
    sequence = 0
    for period in periods:
        for receive in period.receive:
            rows.append((
                period.index * 0.005, sequence, "eps-rx",
                int(receive["can_id"], 0), bytes.fromhex(receive["data_hex"]),
            ))
            sequence += 1
    for transmit in machine_transmit_records(report):
        rows.append((
            int(transmit["period"]) * 0.005 + 0.004999,
            sequence, "eps-tx", int(transmit["can_id"]),
            bytes.fromhex(transmit["data_hex"]),
        ))
        sequence += 1
    lines = [
        f"# capture-sha256={source['sha256']} source={source['path']} "
        "rx=retained-capture tx=exact-image-simulation"
    ]
    for timestamp, _sequence, interface, can_id, payload in sorted(rows):
        separator = "##1" if len(payload) > 8 else "#"
        lines.append(
            f"({timestamp:.6f}) {interface} {can_id:03X}{separator}{payload.hex().upper()}"
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def captured_transmits(periods: Sequence[CapturePeriod]) -> list[dict[str, Any]]:
    rows = []
    for period in periods:
        for row in period.completions:
            match = re.search(r"EPS TX 0x([0-9A-Fa-f]+)", str(row.get("evidence", "")))
            rows.append({
                "can_id": int(match.group(1), 16) if match else None,
                "buffer": int(row["buffer"]),
                "period": period.index,
                "evidence": row.get("evidence"),
            })
    return rows


def compare_transmits(machine: Sequence[dict[str, Any]], capture: Sequence[dict[str, Any]],
                      capture_payloads: dict[int, list[bytes]]) -> list[dict[str, Any]]:
    machine_by_id: dict[int, list[bytes]] = defaultdict(list)
    for row in machine:
        machine_by_id[int(row["can_id"], 0)].append(bytes.fromhex(row["data_hex"]))
    captured_counts = Counter(row["can_id"] for row in capture if row["can_id"] is not None)
    rows = []
    for can_id in sorted(set(machine_by_id) | set(captured_counts)):
        requested = machine_by_id[can_id]
        observed = capture_payloads.get(can_id, [])
        compared = list(zip(requested, observed, strict=False))[:min(len(requested), len(observed))]
        equal = sum(a == b for a, b in compared)
        equal_bytes = sum(sum(x == y for x, y in zip(a, b, strict=False)) for a, b in compared)
        byte_total = sum(min(len(a), len(b)) for a, b in compared)
        rows.append({
            "can_id": f"0x{can_id:X}", "requested": len(requested),
            "captured": captured_counts[can_id], "payload_pairs": len(compared),
            "payload_equal": equal,
            "byte_equality_rate": equal_bytes / byte_total if byte_total else None,
        })
    return rows


def captured_tx_payloads(scenario_path: Path, bus: int) -> dict[int, list[bytes]]:
    source = load_capture(Path(load_capture_scenario(scenario_path)["source"]["path"]))
    _rx, tx_rules = decode_firmware_rules()
    result: dict[int, list[bytes]] = defaultdict(list)
    for row in source["frames"]:
        if row["bus"] == bus and row["addr"] in tx_rules:
            result[row["addr"]].append(row["data"])
    return result


def wire_masks(field: str, payload_length: int) -> tuple[tuple[int, int], ...]:
    matches = list(re.finditer(r"B(\d+)(?:\[(\d+)(?::(\d+))?\])?", field))
    if not matches:
        return ()
    masks: dict[int, int] = {}
    for match in matches:
        index = int(match.group(1))
        if index >= payload_length:
            continue
        high = match.group(2)
        low = match.group(3)
        if high is None:
            masks[index] = 0xFF
        else:
            hi = int(high)
            lo = int(low) if low is not None else hi
            masks[index] = ((1 << (hi - lo + 1)) - 1) << lo
    if ".." in field and len(matches) >= 2:
        first = int(matches[0].group(1))
        last = int(matches[-1].group(1))
        for index in range(first + 1, min(last, payload_length - 1)):
            masks[index] = 0xFF
    return tuple(sorted(masks.items()))


def catalog_mutations(periods: Sequence[CapturePeriod]) -> list[FieldMutation]:
    catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
    routes = {
        int(route["can_id"], 0): route
        for interrupt in catalog["receive_interrupts"]
        for route in interrupt["routes"]
    }
    first_frames: dict[int, tuple[int, int, int]] = {}
    for period in periods:
        for receive_index, row in enumerate(period.receive):
            can_id = int(row["can_id"], 0)
            first_frames.setdefault(
                can_id,
                (len(bytes.fromhex(row["data_hex"])), period.index, receive_index),
            )
    mutations = []
    for can_id, (length, period_index, receive_index) in sorted(first_frames.items()):
        sources = [row for row in routes.get(can_id, {}).get("payload_sources", []) if row.get("wire_field")]
        if not sources:
            mutations.extend(
                FieldMutation(
                    can_id, f"B{index}", ((index, 0xFF),), (),
                    period_index, receive_index,
                )
                for index in range(length)
            )
            continue
        for source in sources:
            masks = wire_masks(source["wire_field"], length)
            if not masks:
                continue
            destination = source.get("destination") or {}
            destinations = ()
            if destination.get("address") is not None:
                destinations = ((
                    int(destination["address"], 0), int(destination["width_bytes"]),
                    str(destination["object"]),
                ),)
            mutations.append(FieldMutation(
                can_id, source["wire_field"], masks, destinations,
                period_index, receive_index,
            ))
    return mutations


def final_check_bytes(report: dict[str, Any]) -> dict[str, str]:
    trials = trial_rows(report)
    if not trials:
        return {}
    return {
        row["name"]: row.get("actual", "unavailable")
        for row in trials[-1].get("checks", [])
    }


def observed_checks(
    report: dict[str, Any], names: set[str], *, first: bool,
) -> dict[str, str]:
    matches = []
    for trial in trial_rows(report):
        for row in trial.get("checks", []):
            if row.get("name") in names and row.get("actual") != "unavailable":
                matches.append((str(row["name"]), str(row["actual"])))
    selected = matches if first else reversed(matches)
    result: dict[str, str] = {}
    for name, value in selected:
        result.setdefault(name, value)
    return result

def mode_values(checks: dict[str, str]) -> dict[str, str | None]:
    return {
        role: (
            f"0x{int.from_bytes(bytes.fromhex(checks[name]), 'little'):04X}"
            if name in checks else None
        )
        for role, name in (
            ("live", "end-live-mode"),
            ("desired", "end-desired-mode"),
            ("active", "end-active-mode"),
        )
    }


def discrimination_plan(periods: Sequence[CapturePeriod]) -> dict[str, Any]:
    mutations = catalog_mutations(periods)
    return {
        "window_periods": len(periods),
        "idle_runs": 1,
        "baseline_runs": 1,
        "field_runs": len(mutations),
        "total_runs": len(mutations) + 2,
        "mutation_scope": "one field in one frame; 200-period window",
        "timing_estimate": {
            "reference_cycle_instructions": REFERENCE_CYCLE_INSTRUCTIONS,
            "reference_instructions_per_second": REFERENCE_INSTRUCTIONS_PER_SECOND,
            "seconds_per_period": ESTIMATED_SECONDS_PER_PERIOD,
            "scope": "scheduler-only lower bound; CAN ingress adds instructions",
        },
        "estimated_seconds_per_run": len(periods) * ESTIMATED_SECONDS_PER_PERIOD,
        "estimated_total_seconds": (
            (len(mutations) + 2) * len(periods) * ESTIMATED_SECONDS_PER_PERIOD
        ),
        "fields": [
            {
                "can_id": f"0x{mutation.can_id:X}",
                "field": mutation.name,
                "masks": [
                    {"byte": index, "mask": f"0x{mask:02X}"}
                    for index, mask in mutation.masks
                ],
                "mutated_period": mutation.period_index,
                "mutated_receive_index": mutation.receive_index,
                "destinations": [
                    {
                        "address": f"0x{address:08X}",
                        "size": size,
                        "object": name,
                    }
                    for address, size, name in mutation.destinations
                ],
            }
            for mutation in mutations
        ],
    }


def scenario_sha256(scenario: dict[str, Any]) -> str:
    encoded = json.dumps(
        scenario, sort_keys=True, separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def load_or_run_discrimination_result(
    path: Path,
    identity: dict[str, Any],
    produce: Any,
) -> tuple[dict[str, Any], bool]:
    try:
        saved = json.loads(path.read_text(encoding="utf-8"))
        result = saved["result"]
        valid = (
            saved.get("schema") == "camry-f33-capture-discrimination-result-v1"
            and saved.get("identity") == identity
            and isinstance(result, dict)
            and isinstance(result.get("transmit_records"), list)
            and isinstance(result.get("wall_seconds"), (int, float))
        )
        if valid:
            return result, True
    except (FileNotFoundError, json.JSONDecodeError, KeyError, TypeError):
        pass
    path.unlink(missing_ok=True)
    result = produce()
    payload = {
        "schema": "camry-f33-capture-discrimination-result-v1",
        "identity": identity,
        "result": result,
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(payload, indent=2) + "\n", encoding="utf-8",
    )
    temporary.replace(path)
    return result, False


def discrimination(source: dict[str, Any], periods: Sequence[CapturePeriod], out: Path,
                   batch_size: int, max_new_runs: int | None = None) -> dict[str, Any]:
    if max_new_runs is not None and max_new_runs < 1:
        raise ValueError("max_new_runs must be positive")
    if batch_size != 1:
        raise ValueError("capture discrimination requires batch_size=1")
    mutations = catalog_mutations(periods)
    period_positions = {period.index: index for index, period in enumerate(periods)}
    checks = probe_checks(mutations, SNAPSHOT.read_bytes())
    scenario_dir = out / "discrimination" / "scenarios"
    result_dir = out / "discrimination" / "results"

    idle_periods = tuple(CapturePeriod(period.index, (), ()) for period in periods)
    idle = build_replay_scenario(source, idle_periods, "field_idle", checks=checks)
    configure_transmit_observation(idle)
    idle_path = scenario_dir / "field_idle.json"
    write_scenario(idle_path, idle)

    baseline = build_replay_scenario(source, periods, "field_baseline", checks=checks)
    configure_transmit_observation(baseline)
    baseline_path = scenario_dir / "field_baseline.json"
    write_scenario(baseline_path, baseline)

    cases: list[tuple[str, str, FieldMutation | None, Path, dict[str, Any]]] = [
        ("baseline", "baseline", None, baseline_path, baseline),
        ("idle", "idle", None, idle_path, idle),
    ]
    for index, mutation in enumerate(mutations):
        name = f"field_{index:03d}_{mutation.can_id:03x}"
        path = scenario_dir / f"{name}.json"
        scenario = build_replay_scenario(
            source, periods, name, mutations=(mutation,), checks=checks,
        )
        configure_transmit_observation(scenario)
        write_scenario(path, scenario)
        cases.append((name, "field", mutation, path, scenario))

    baseline_hash = scenario_sha256(baseline)
    result_rows: dict[str, dict[str, Any]] = {}
    resumed = 0
    executed = 0
    campaign_started = time.perf_counter()
    for case_index, (name, role, mutation, scenario_path, scenario) in enumerate(cases):
        identity = {
            "case_name": name,
            "role": role,
            "scenario_sha256": scenario_sha256(scenario),
            "baseline_scenario_sha256": baseline_hash,
        }

        def produce() -> dict[str, Any]:
            nonlocal executed
            started = time.perf_counter()
            report = capture_many(
                TARGET, [scenario_path],
                out / "discrimination" / "faults", instruction_trace=False,
            )[0]
            elapsed = time.perf_counter() - started
            transmit_records = observed_transmit_records(report)
            baseline_records = (
                transmit_records
                if role == "baseline"
                else result_rows["baseline"]["transmit_records"]
            )
            comparison = (
                None
                if role == "baseline"
                else transmit_difference(baseline_records, transmit_records)
            )
            if comparison is not None and mutation is not None:
                comparison["periods_after_first_mutated_input"] = (
                    int(comparison["period"]) - mutation.period_index
                )
            executed += 1
            return {
                "case_name": name,
                "role": role,
                "wall_seconds": elapsed,
                "transmit_records": transmit_records,
                "published_anything": bool(transmit_records),
                "transmit_comparison": comparison,
                "all_transmit_differences": (
                    []
                    if role == "baseline"
                    else transmit_differences(baseline_records, transmit_records)
                ),
                "termination_reason": report.get("termination_reason"),
                "stop": report.get("error") if not trial_rows(report) else None,
            }

        result, was_resumed = load_or_run_discrimination_result(
            result_dir / f"{name}.json", identity, produce,
        )
        result_rows[name] = result
        resumed += int(was_resumed)
        if (
            max_new_runs is not None
            and executed >= max_new_runs
            and case_index + 1 < len(cases)
        ):
            progress = {
                "complete": False,
                "executed_runs": executed,
                "resumed_runs": resumed,
                "remaining_runs": len(cases) - case_index - 1,
                "campaign_wall_seconds": time.perf_counter() - campaign_started,
            }
            (out / "discrimination" / "progress.json").write_text(
                json.dumps(progress, indent=2) + "\n", encoding="utf-8",
            )
            return progress

    campaign_wall_seconds = time.perf_counter() - campaign_started
    baseline_tx = result_rows["baseline"]["transmit_records"]
    idle_tx = result_rows["idle"]["transmit_records"]
    rows = []
    for name, _role, mutation, _scenario_path, _scenario in cases[2:]:
        assert mutation is not None
        result = result_rows[name]
        tx_difference = result["transmit_comparison"]
        tx_changed = tx_difference is not None
        tx_now = result["transmit_records"]
        rows.append({
            "can_id": f"0x{mutation.can_id:X}", "field": mutation.name,
            "masks": [[index, f"0x{mask:02X}"] for index, mask in mutation.masks],
            "consumed": tx_changed,
            "destinations_moved": [],
            "transmit_payloads_changed": tx_changed,
            "transmit_difference": tx_difference,
            "transmit_frames": len(tx_now),
            "published_nothing": not result["published_anything"],
            "mutated_period": mutation.period_index,
            "mutated_receive_index": mutation.receive_index,
            "run_periods": len(periods),
            "wall_seconds": result["wall_seconds"],
            "stop": result["stop"],
        })
    baseline_vs_idle = transmit_differences(idle_tx, baseline_tx)
    receive_ids_by_period: dict[int, set[int]] = defaultdict(set)
    for period in periods:
        receive_ids_by_period[period.index].update(
            int(row["can_id"], 0) for row in period.receive
        )
    associated_changes = [
        {
            **difference,
            "receive_ids": [
                f"0x{can_id:X}"
                for can_id in sorted(receive_ids_by_period[difference["period"]])
            ],
        }
        for difference in baseline_vs_idle
    ]
    run_seconds = [float(result["wall_seconds"]) for result in result_rows.values()]
    summary = {
        "complete": True,
        "window_periods": len(periods),
        "batch_size": 1,
        "campaign_wall_seconds": campaign_wall_seconds,
        "run_wall_seconds_total": sum(run_seconds),
        "executed_runs": executed,
        "resumed_runs": resumed,
        "per_run_wall_seconds": {
            "minimum": min(run_seconds),
            "median": statistics.median(run_seconds),
            "maximum": max(run_seconds),
        },
        "idle_transmit_frames": len(idle_tx),
        "baseline_transmit_frames": len(baseline_tx),
        "baseline_vs_idle_transmit_differences": associated_changes,
        "fields_tried": len(rows),
        "fields_consumed": sum(row["consumed"] for row in rows),
        "fields_with_response": sum(row["transmit_payloads_changed"] for row in rows),
        "fields_with_no_response": sum(not row["transmit_payloads_changed"] for row in rows),
        "fields_with_transmit_change": sum(row["transmit_payloads_changed"] for row in rows),
        "fields_with_no_transmit_change": sum(not row["transmit_payloads_changed"] for row in rows),
        "runs_published_nothing": sum(row["published_nothing"] for row in rows),
        "rows": rows,
    }
    (out / "discrimination" / "summary.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8",
    )
    (out / "discrimination" / "progress.json").write_text(
        json.dumps({
            "complete": True,
            "executed_runs": executed,
            "resumed_runs": resumed,
            "remaining_runs": 0,
            "campaign_wall_seconds": campaign_wall_seconds,
        }, indent=2) + "\n",
        encoding="utf-8",
    )
    return summary

def run_diagnostic_probes(
    source: dict[str, Any], out: Path, *, full_capture_rows: bool = False,
) -> dict[str, Any]:
    requests = (
        ("rdbi-f189", "0322f18900000000", 0x22, {0x62, 0x7F}),
        ("session-1003", "0210030000000000", 0x10, {0x50, 0x7F}),
    )
    cases = []
    expected: dict[str, tuple[int, set[int]]] = {}
    for name, payload, service, response_services in requests:
        event = {
            "kind": "can-rx",
            "fifo": 5,
            "boundary": "post-filter",
            "can_id": "0x7a1",
            "data_hex": payload,
            "label": 52,
            "after_instructions": 0,
            "evidence": f"diagnostic readiness probe {name}",
        }
        periods = tuple(
            CapturePeriod(index, (event,) if index == 0 else (), ())
            for index in range(12)
        )
        scenario = build_replay_scenario(
            source, periods, name, include_completions=False,
            checks=READINESS_MODE_CHECKS,
        )
        cases.append((name, scenario))
        expected[name] = (service, response_services)
    scenario = batch_replay_scenarios(cases, "diagnostic_readiness_probes")
    configure_replay_capture(scenario, full_capture_rows=full_capture_rows)
    scenario_path = out / "scenarios" / "diagnostic_readiness_probes.json"
    write_scenario(scenario_path, scenario)
    report = capture_many(
        TARGET, [scenario_path], out / "reports", instruction_trace=False,
    )[0]
    split = split_replay_batch_report(report, [name for name, _scenario in cases])
    result: dict[str, Any] = {}
    for (name, _scenario), case_report in zip(cases, split, strict=True):
        service, response_services = expected[name]
        records = machine_transmit_records(case_report)
        responses = []
        for row in records:
            payload = bytes.fromhex(row["data_hex"])
            if len(payload) < 2 or payload[1] not in response_services:
                continue
            if payload[1] == 0x7F and (len(payload) < 3 or payload[2] != service):
                continue
            responses.append({
                **row,
                "can_id": f"0x{int(row['can_id']):X}",
            })
        result[name] = {
            "answered": bool(responses),
            "responses": responses,
            "all_transmits": [
                {**row, "can_id": f"0x{int(row['can_id']):X}"}
                for row in records
            ],
        }
    return {
        "scenario": str(scenario_path),
        "requests": result,
    }


def run_acceptance_proof(
    source: dict[str, Any], periods: Sequence[CapturePeriod], out: Path,
    *, full_capture_rows: bool = False,
) -> dict[str, Any]:
    proof_window = acceptance_probe_periods(periods)
    proof_periods = [period for period in proof_window if period.receive]
    report, scenario_path = run_once(
        source,
        proof_periods,
        out / "acceptance-proof",
        "firmware_initialized_capture_pair_acceptance",
        include_completions=False,
        foreground_ticks=False,
        full_capture_rows=full_capture_rows,
    )
    reception = summarize_reception(report)
    rows = reception_table(proof_periods, reception)
    passed = (
        successful(report, expected_trial_count(proof_periods, foreground_ticks=False))
        and len(rows) == 21
        and all(
            row["capture_frames"] == 1
            and row["enqueued_before_stop"] == 1
            and row["popped_before_stop"] == 1
            and row["discarded_before_stop"] == 0
            and row["dropped_before_stop"] == 0
            for row in rows
        )
    )
    return {
        "passed": passed,
        "window_periods": len(proof_window),
        "pair_count": len(rows),
        "scenario": str(scenario_path),
        "termination_reason": report.get("termination_reason"),
        "error": report.get("error"),
        "reception": reception,
        "per_id_dlc": rows,
    }


def replay_capture(
    scenario_path: Path, out: Path, periods_limit: int | None,
    discrimination_periods: int, batch_size: int, *, full_capture_rows: bool = False,
) -> dict[str, Any]:
    converted = load_capture_scenario(scenario_path)
    all_periods = capture_periods(converted)
    periods = all_periods if periods_limit is None else all_periods[:periods_limit]
    out.mkdir(parents=True, exist_ok=True)
    acceptance_proof = run_acceptance_proof(
        converted["source"], all_periods, out, full_capture_rows=full_capture_rows,
    )
    if not acceptance_proof["passed"]:
        summary = {
            "schema": SCHEMA,
            "capture": converted["source"],
            "scenario": str(scenario_path),
            "acceptance_proof": acceptance_proof,
            "replay_not_run": "firmware-initialized native acceptance proof failed",
            "mutation_enabled": False,
        }
        (out / "summary.json").write_text(
            json.dumps(summary, indent=2) + "\n", encoding="utf-8",
        )
        raise RuntimeError(
            "firmware-initialized native acceptance proof failed; see summary.json"
        )
    plan_periods = periods[:min(50, len(periods))]
    (out / "discrimination-plan.json").write_text(
        json.dumps(discrimination_plan(plan_periods), indent=2) + "\n",
        encoding="utf-8",
    )
    cycle_probe, cycle_probe_path = run_once(
        converted["source"], periods[:1], out / "cycle-preflight",
        "snapshot_native_cycle_preflight", include_completions=False,
        full_capture_rows=full_capture_rows,
    )
    cycle_trial = next(
        (
            row for row in trial_rows(cycle_probe)
            if row["name"] == "period-00000-native-cycle"
        ),
        None,
    )
    if (
        cycle_trial is None
        or cycle_trial.get("termination_reason") != "stop-address"
        or cycle_trial.get("final_pc") != "0x000660BC"
    ):
        candump_path = out / "capture-replay.candump.log"
        write_candump(candump_path, converted["source"], periods[:1], cycle_probe)
        fault = {
            "period": 0,
            "phase": "foreground-cycle",
            "typed_machine_fault": None,
            "termination_reason": (
                cycle_trial.get("termination_reason") if cycle_trial else
                cycle_probe.get("termination_reason")
            ),
            "pc": cycle_trial.get("final_pc") if cycle_trial else None,
            "firmware_gate": (
                "0x5F9BC mode >= 0x900 -> 0x56CF6; "
                "application_nvm_is_ready @ 0x66F1E returns 1; "
                "0x56D06 calls boot transfer 0x65F5E"
            ),
        }
        reception = summarize_reception(cycle_probe)
        summary = {
            "schema": SCHEMA,
            "capture": converted["source"],
            "scenario": str(scenario_path),
            "replay_scenario": str(cycle_probe_path),
            "periods_requested": len(periods),
            "periods_completed_before_stop": 0,
            "faults": [fault],
            "reception": reception,
            "receive_table": reception_table(periods[:1], reception),
            "transmit_comparison": compare_transmits(
                machine_transmits(cycle_probe), captured_transmits(periods[:1]), {},
            ),
            "acceptance_proof": acceptance_proof,
            "snapshot_start_transmit_comparison": [],
            "discrimination": None,
            "candump_log": str(candump_path),
            "replay_not_run": "READY snapshot enters firmware programming-shutdown boot transfer",
            "mutation_enabled": False,
        }
        (out / "summary.json").write_text(
            json.dumps(summary, indent=2) + "\n", encoding="utf-8",
        )
        return summary
    payloads = captured_tx_payloads(scenario_path, int(converted["source"]["bus"]))
    probe_count = min(20, len(periods))
    probe_report, _ = run_once(
        converted["source"], periods[:probe_count], out / "start-probe",
        "snapshot_start_transmit_probe", include_completions=False,
        full_capture_rows=full_capture_rows,
    )
    start_transmit_comparison = compare_transmits(
        machine_transmits(probe_report),
        captured_transmits(periods[:probe_count]),
        payloads,
    )
    report, replay_path = run_once(
        converted["source"], periods, out, f"{scenario_path.stem}_continuous",
        checks=END_MODE_CHECKS,
        full_capture_rows=full_capture_rows,
    )
    fault = None
    accepted_report = report
    completed_periods = len(periods)
    if not successful(report, expected_trial_count(periods)):
        low, high = 0, len(periods)
        while low < high:
            middle = (low + high + 1) // 2
            candidate, _ = run_once(
                converted["source"], periods[:middle], out / "localize",
                f"prefix_{middle:05d}",
                full_capture_rows=full_capture_rows,
            )
            if successful(candidate, expected_trial_count(periods[:middle])):
                low = middle
                accepted_report = candidate
            else:
                high = middle - 1
        completed_periods = low
        fault_period = low
        if fault_period < len(periods):
            period = periods[fault_period]
            receive_only, _ = run_once(
                converted["source"], periods[:fault_period + 1], out / "localize",
                f"period_{fault_period:05d}_receive_only",
                final_completion_limit=0,
                full_capture_rows=full_capture_rows,
            )
            if successful(
                receive_only, expected_trial_count(periods[:fault_period + 1]),
            ):
                accepted_report = receive_only
                first_frame = period.completions[0].get("evidence") if period.completions else None
                phase = "can-tx-complete"
            else:
                first_frame = period.receive[0].get("evidence") if period.receive else None
                phase = "can-rx"
            fault = {
                "period": fault_period, "phase": phase, "frame": first_frame,
                "error": report.get("error"),
            }
    reception = summarize_reception(accepted_report)
    mode_names = {str(row["name"]) for row in READINESS_MODE_CHECKS}
    start_mode = mode_values(observed_checks(accepted_report, mode_names, first=True))
    end_mode = mode_values(observed_checks(accepted_report, mode_names, first=False))
    tx_compare = compare_transmits(
        machine_transmits(accepted_report), captured_transmits(periods), payloads,
    )
    candump_path = out / "capture-replay.candump.log"
    write_candump(
        candump_path, converted["source"], periods[:completed_periods], accepted_report,
    )
    diagnostic_result = run_diagnostic_probes(
        converted["source"], out / "diagnostic-probes", full_capture_rows=full_capture_rows,
    )
    discrimination_result = None
    if discrimination_periods:
        window = periods[:min(discrimination_periods, len(periods))]
        discrimination_result = discrimination(
            converted["source"], window, out, batch_size,
        )
    summary = {
        "schema": SCHEMA,
        "capture": converted["source"],
        "scenario": str(scenario_path),
        "replay_scenario": str(replay_path),
        "periods_requested": len(periods),
        "periods_completed_before_stop": completed_periods,
        "faults": [fault] if fault else [],
        "reception": reception,
        "receive_table": reception_table(periods, reception),
        "transmit_comparison": tx_compare,
        "candump_log": str(candump_path),
        "acceptance_proof": acceptance_proof,
        "snapshot_start_transmit_comparison": start_transmit_comparison,
        "mode_cells": {
            "period_0": start_mode,
            f"period_{completed_periods}": end_mode,
        },
        "diagnostic_probes": diagnostic_result,
        "discrimination": discrimination_result,
        "mutation_enabled": False,
    }
    (out / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("scenario", type=Path, help="converted capture .scenario.json")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--periods", type=int)
    parser.add_argument("--discriminate-periods", type=int, default=0)
    parser.add_argument("--batch-size", type=int, choices=(1,), default=1)
    parser.add_argument(
        "--full-capture-rows", action="store_true",
        help="retain all device and memory rows in replay reports (not checks-only discrimination)",
    )
    args = parser.parse_args()
    if args.periods is not None and args.periods < 1:
        parser.error("--periods must be positive")
    if args.discriminate_periods < 0 or args.batch_size < 1:
        parser.error("discrimination periods must be nonnegative and batch size must be positive")
    result = replay_capture(
        args.scenario, args.out, args.periods, args.discriminate_periods,
        args.batch_size, full_capture_rows=args.full_capture_rows,
    )
    print(json.dumps({
        "summary": str(args.out / "summary.json"),
        "capture": result["capture"],
        "periods_requested": result["periods_requested"],
        "periods_completed_before_stop": result["periods_completed_before_stop"],
        "faults": result["faults"],
        "reception": result["reception"],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
