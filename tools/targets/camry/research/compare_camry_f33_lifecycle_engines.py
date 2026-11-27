#!/usr/bin/env python3
"""Compare Camry DCM lifecycle checkpoints across GNU sim, P1M-E, and native C."""
from __future__ import annotations

import argparse
import ctypes
import json
import hashlib
import subprocess
import os
import tempfile
from bisect import bisect_right
from collections import Counter, defaultdict
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any, Iterable, Sequence

from tools import REPO_ROOT
from tools.emulation.p1me_machine import capture_many
from tools.targets.camry.analysis.convert_camry_capture_machine_events import (
    RAM_BASE,
    SNAPSHOT,
    SNAPSHOT_SHA256,
)
from tools.targets.camry.decomp import tree
from tools.targets.camry.decomp.execution.calls import call_corpus
from tools.targets.camry.decomp.execution.checks import check_results
from tools.targets.camry.decomp.execution.link import _compile
from tools.targets.camry.decomp.execution.memory import install_address_space, view_of
from tools.targets.camry.decomp.execution.native import _bind_host
from tools.targets.camry.decomp.sources import _load_bodies
from tools.targets.camry.decomp.tree import load_symbols
from tools.targets.camry.research import fuzz_camry_f33_dcm_handlers as dcm
from tools.targets.camry.research import fuzz_camry_f33_machine_typed_events as machine_fuzz
from tools.targets.camry.research import fuzz_camry_f33_stateful_coverage as stateful
from tools.targets.camry.research import replay_camry_f33_capture_machine as capture_replay

TARGET = "camry-8965F3307000"
SCHEMA = "camry-f33-lifecycle-cross-engine-v1"
DEFAULT_OUT = REPO_ROOT / "build/out/targets/camry-8965F3307000/lifecycle-cross-engine"
IMAGE = REPO_ROOT / "firmware/camry-8965F3307000/CodeFlash.bin"
MACHINE_CLASSES = ("poll", "completion", "timeout", "reuse")
SYNTHETIC_BASE_IMAGE = stateful.base_image
REPRESENTATIVES_PER_CLASS = 5
DIRECT_ONLY_RANGES = (
    (
        0xFEBE39C0, 0xFEBE3DDF,
        "Dcm software timers advance on the machine foreground clock; direct "
        "Dcm calls have no elapsed-time boundary",
    ),
    (
        0xFEBE5060, 0xFEBE50C0,
        "crypto-bank state is owned by full communication-cycle callbacks "
        "outside the Dcm call contract",
    ),
    (
        0xFEBE5624, 0xFEBE564D,
        "CanTp ingress owns the active Dcm transaction/message context around "
        "the Dcm call; direct engines inject after that boundary",
    ),
    (
        0xFEBE5651, 0xFEBE5950,
        "CanTp receive slots retain wire request payloads; direct Dcm calls "
        "inject requests without populating transport buffers",
    ),
    (
        0xFEBE4EFC, 0xFEBE4FB1,
        "CanTp channel state changes only under real ingress; the direct-call "
        "GNU/native checkpoint bypasses CanTp",
    ),
    (
        0xFEBE5960, 0xFEBE59EF,
        "Dcm request phase, response transport state, NRC cells, response queue "
        "and nodes, P2 retention, and pending dispatch slot are set by CanTp "
        "receive indication and retired by transmit confirmation; the direct "
        "engines prime them and never receive a confirmation",
    ),
    (
        0xFEBE59F0, 0xFEBE5A1F,
        "receive-buffer cursor, length, and remaining are filled by CanTp from "
        "the wire; the direct executor writes the slot row itself",
    ),
    (
        0xFEBE5E51, 0xFEBE5EC7,
        "Dcm event ring and software timers follow transport notifications and "
        "the foreground clock",
    ),
    (
        stateful.TRANSPORT_CONTEXT,
        stateful.TRANSPORT_CONTEXT + len(stateful.transport_context(stateful.seed_cases()[0].steps[0])) - 1,
        "direct harness synthetic proprietary-callback context; firmware creates "
        "it only through snapshot_seven_word_context_and_call_4d4c2_8e672",
    ),
)
# Application work that the machine's foreground cycle runs after the Dcm call
# (NVM jobs, DTC engine, health monitor, DMA windows, per-cycle counters). The
# direct engines execute the Dcm call only, so these bytes are compared but
# attributed to the cycle rather than to the Dcm contract.
FOREGROUND_CYCLE_RANGES = (
    (0xFEBE5F4C, 0xFEBE602C),  # BA application work, DTC status iteration snapshot
    (0xFEBE6054, 0xFEBE67F0),  # derived classified DTC bitmap
    (0xFEBE6A84, 0xFEBE6AE6),  # per-cycle counters in retained fit coefficients
    (0xFEBE7F68, 0xFEBE802E),  # per-cycle counters in source admission state
    (0xFEBE8198, 0xFEBE8A68),  # DTC request mask, iteration, cached DTC, capture slots
    (0xFEBE8DC0, 0xFEBEB18C),  # DMA progress windows
    (0xFEBEB196, 0xFEBEB49E),  # health receive generation
    (0xFEBF0308, 0xFEBF0328),  # NVM family-0 status
    (0xFEBF0488, 0xFEBF067B),  # NVM family-0 request cells and producer
    (0xFEBF3B19, 0xFEBF3BD4),  # programming pending latch
    (0xFEBF6C10, 0xFEBF6CC0),  # NVM completion result, checksum, chunks, side status
)
QUIESCENT_DIRECT_PRIMES = ((0xFEBE3DE0, b"\x0F"),)
DATA_LABELS = tree.ROOT / "data.jsonl"


# Envelope endpoints are inclusive in the stateful fuzzer.
STATE_COMPONENTS = (
    (dcm.SESSION, dcm.SESSION + 3, "session"),
    (dcm.SECURITY_BITMAP, dcm.SECURITY_BITMAP + 7, "security-bitmap"),
    (dcm.ACTIVE_DCM_CONTEXT + 12, dcm.ACTIVE_DCM_CONTEXT + 15, "response-length"),
    (dcm.RESP_BUF, dcm.RESP_BUF + 0x2FF, "response-buffer"),
    (0xFEBE5E10, 0xFEBE5E60, "pending-operation-state"),
)


@dataclass(frozen=True)
class Checkpoint:
    owner_name: str
    owner_id: str
    lifecycle_class: str
    disposition: str
    index: int
    step_kind: str
    case: stateful.Case


def merged_state_ranges() -> tuple[tuple[int, int], ...]:
    ranges = [(int(lo), int(hi)) for lo, hi, _name in STATE_COMPONENTS]
    ranges.extend((int(lo), int(hi)) for lo, hi in stateful.STATEFUL_ENVELOPE)
    merged: list[list[int]] = []
    for lo, hi in sorted(ranges):
        if merged and lo <= merged[-1][1] + 1:
            merged[-1][1] = max(merged[-1][1], hi)
        else:
            merged.append([lo, hi])
    compared: list[tuple[int, int]] = []
    for lo, hi in merged:
        fragments = [(lo, hi)]
        for ignored_lo, ignored_hi, _reason in (
            *((dead_lo, dead_hi, "stateful divergence dead range") for dead_lo, dead_hi in dcm.DIVERGENCE_DEAD_RANGES),
            *DIRECT_ONLY_RANGES,
        ):
            next_fragments: list[tuple[int, int]] = []
            for start, end in fragments:
                if ignored_hi < start or end < ignored_lo:
                    next_fragments.append((start, end))
                    continue
                if start < ignored_lo:
                    next_fragments.append((start, ignored_lo - 1))
                if ignored_hi < end:
                    next_fragments.append((ignored_hi + 1, end))
            fragments = next_fragments
        compared.extend(fragments)
    return tuple(compared)


def load_data_labels() -> list[tuple[int, str]]:
    rows: list[tuple[int, str]] = []
    with DATA_LABELS.open(encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                row = json.loads(line)
                rows.append((int(row["addr"], 16), row["name"]))
    rows.sort()
    return rows


_LABELS = load_data_labels()
DATA_LABEL_ADDRESSES = [address for address, _name in _LABELS]
DATA_LABEL_NAMES = [name for _address, name in _LABELS]


def label_for(address: int) -> str:
    index = bisect_right(DATA_LABEL_ADDRESSES, address) - 1
    if index < 0:
        return f"0x{address:08X}"
    base, name = DATA_LABEL_ADDRESSES[index], DATA_LABEL_NAMES[index]
    return name if address == base else f"{name}+0x{address - base:X}"


def difference_groups(differences: Sequence[dict[str, str]]) -> dict[str, Any]:
    foreground: list[str] = []
    contract: list[str] = []
    for row in differences:
        address = int(row["address"], 16)
        target = (
            foreground
            if any(lo <= address <= hi for lo, hi in FOREGROUND_CYCLE_RANGES)
            else contract
        )
        label = label_for(address)
        if label not in target:
            target.append(label)
    return {"foreground-cycle": foreground, "contract": contract}


STATE_RANGES = merged_state_ranges()


def lifecycle_class(case: stateful.Case) -> str:
    last = case.steps[-1].kind
    return "reuse" if last == "request" and len(case.steps) > 1 else last


def selected_cases() -> list[stateful.Case]:
    selected = list(stateful.seed_cases())
    groups: dict[str, list[stateful.Case]] = defaultdict(list)
    for case in stateful.lifecycle_prefix_cases():
        kind = lifecycle_class(case)
        if kind in MACHINE_CLASSES:
            groups[kind].append(case)
    for kind in MACHINE_CLASSES:
        selected.extend(sorted(groups[kind], key=lambda case: case.case_id)[:REPRESENTATIVES_PER_CLASS])
    unique: dict[str, stateful.Case] = {}
    for case in selected:
        unique.setdefault(case.case_id, case)
    return list(unique.values())


def explicit_salts(case: stateful.Case) -> tuple[stateful.Step, ...]:
    return tuple(
        replace(step, request_tail_salt=stateful.request_tail_salt(case, index, step))
        if step.kind == "request" and step.request_tail_salt is None else step
        for index, step in enumerate(case.steps)
    )


def checkpoints(cases: Sequence[stateful.Case]) -> list[Checkpoint]:
    rows: list[Checkpoint] = []
    for owner in cases:
        salted = explicit_salts(owner)
        disposition = machine_fuzz.lifecycle_disposition(owner)
        kind = lifecycle_class(owner)
        for index, step in enumerate(salted):
            prefix = stateful.Case(
                f"cross_{owner.name}_checkpoint_{index + 1}",
                owner.session,
                owner.security_bitmap,
                salted[:index + 1],
            )
            rows.append(Checkpoint(
                owner.name, owner.case_id, kind, disposition,
                index + 1, step.kind, prefix,
            ))
    return rows


def snapshot_from_dump(dump: bytes) -> dict[str, str]:
    return {
        f"0x{lo:08X}": dump[lo - RAM_BASE:hi - RAM_BASE + 1].hex()
        for lo, hi in STATE_RANGES
    }


def snapshot_from_memory(memory: bytearray) -> dict[str, str]:
    return snapshot_from_dump(bytes(memory))


def byte_differences(left: dict[str, str], right: dict[str, str],
                     per_range: int = 8, limit: int = 64) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for address in sorted(set(left) | set(right), key=lambda value: int(value, 0)):
        a = bytes.fromhex(left.get(address, ""))
        b = bytes.fromhex(right.get(address, ""))
        common = min(len(a), len(b))
        offsets = [index for index in range(common) if a[index] != b[index]]
        if len(a) != len(b):
            offsets.append(common)
        for offset in offsets[:per_range]:
            rows.append({
                "address": f"0x{int(address, 0) + offset:08X}",
                "left": a[offset:offset + 8].hex(),
                "right": b[offset:offset + 8].hex(),
            })
            if len(rows) >= limit:
                return rows
    return rows


def comparison(left: dict[str, str], right: dict[str, str]) -> dict[str, Any]:
    differences = byte_differences(left, right)
    return {
        "equal": not differences,
        "first_difference": differences[0] if differences else None,
        "differences": differences,
        "groups": difference_groups(differences),
    }


def initial_image(case: stateful.Case) -> bytes:
    """READY snapshot with only the direct harness's declared case primes."""
    ready = bytearray(SNAPSHOT.read_bytes())
    if len(ready) != dcm.RAM_SIZE:
        raise RuntimeError("READY snapshot does not cover LocalRAM")
    primes = (
        QUIESCENT_DIRECT_PRIMES
        + dcm.session_primes(case.session, case.security_bitmap)
        + tuple((address, b"\x5A") for address in dcm.ADMISSION)
        + ((dcm.ADMISSION_CLEAR, b"\x00"),)
        + ((dcm.RMEM_SOURCE, bytes((0x40 + index) & 0xFF for index in range(0x100))),)
    )
    for address, value in primes:
        offset = address - RAM_BASE
        ready[offset:offset + len(value)] = value
    return bytes(ready)


def initial_overlay_events(case: stateful.Case) -> list[dict[str, Any]]:
    ready = SNAPSHOT.read_bytes()
    initialized = initial_image(case)
    rows: list[dict[str, Any]] = []
    start: int | None = None
    for index, (before, after) in enumerate(zip(ready, initialized, strict=True)):
        different = before != after
        if different and start is None:
            start = index
        elif not different and start is not None:
            rows.append({
                "kind": "memory-write",
                "address": hex(RAM_BASE + start),
                "data_hex": initialized[start:index].hex(),
                "after_instructions": 0,
                "evidence": "Shared READY-image lifecycle prime",
            })
            start = None
    if start is not None:
        rows.append({
            "kind": "memory-write",
            "address": hex(RAM_BASE + start),
            "data_hex": initialized[start:].hex(),
            "after_instructions": 0,
            "evidence": "Shared READY-image lifecycle prime",
        })
    return rows


def state_checks(expected: dict[str, str]) -> list[dict[str, Any]]:
    return [
        {
            "name": f"state-{address[2:].lower()}",
            "kind": "memory",
            "address": address,
            "size": len(bytes.fromhex(value)),
            "equals_hex": value,
        }
        for address, value in expected.items()
    ]


def run_gnu(rows: Sequence[Checkpoint], out: Path, timeout: float,
            batch_size: int) -> tuple[dict[str, dict[str, str]], list[dict[str, Any]]]:
    elf, _model = stateful.prepare_elf(out / "gnu", timeout)
    stateful.base_image = initial_image
    try:
        collection = stateful.run_cases(
            elf, [row.case for row in rows], out / "gnu", "branch",
            timeout, batch_size, "cross-engine",
        )
    finally:
        stateful.base_image = SYNTHETIC_BASE_IMAGE
    states = {
        result.case.case_id: snapshot_from_dump(result.dump)
        for result in collection.results if result.dump is not None
    }
    return states, collection.hangs


def write_memory(library: ctypes.CDLL, address: int, value: bytes) -> None:
    for offset, item in enumerate(value):
        library.camry_write8(address + offset, item)


def native_registers(extra: Iterable[tuple[str, int]] = ()) -> dict[str, str]:
    rows = {
        "gp": hex(dcm.GP), "tp": hex(dcm.TP_BASE), "sp": hex(dcm.STACK_TOP),
        "r6": "0", "r7": "0",
    }
    rows.update({name.removeprefix("$"): hex(value) for name, value in extra})
    return rows


def run_native_step(library: ctypes.CDLL, step: stateful.Step,
                    case: stateful.Case, index: int, initialized: set[int]) -> None:
    if step.kind == "request":
        slot_base = dcm.SLOT_BUFFERS[step.slot]
        if step.slot not in initialized or step.request_tail_salt is not None:
            payload = bytearray(dcm.pattern_image(stateful.request_tail_salt(case, index, step))[:0x100])
            payload[:len(step.request)] = step.request
        else:
            payload = bytearray(step.request)
        write_memory(library, slot_base, payload)
        initialized.add(step.slot)
        if step.response_poison is not None:
            write_memory(library, dcm.RESP_BUF, dcm.response_poison(step.response_poison))
        write_memory(library, stateful.TRANSPORT_CONTEXT, stateful.transport_context(step))
        row = dcm.SLOT_STATE + 0x10 * step.slot
        write_memory(library, row, slot_base.to_bytes(4, "little"))
        write_memory(library, row + 4, len(step.request).to_bytes(4, "little"))
        write_memory(library, row + 8, (0x100).to_bytes(2, "little"))
        write_memory(library, row + 0xA, bytes(2))
        write_memory(library, dcm.REQUEST_PHASE, b"\x02")
        write_memory(library, dcm.PENDING_SLOT, step.slot.to_bytes(2, "little"))
        address = dcm.DISPATCH_TASK
        registers = native_registers()
    elif step.kind == "tick":
        write_memory(library, dcm.REQUEST_PHASE, b"\x00")
        address = dcm.DISPATCH_TASK
        registers = native_registers()
    else:
        address, extra = stateful.CALLS[step.kind]
        registers = native_registers(extra)
    symbol = next(row for row in load_symbols() if int(row["addr"], 16) == address)
    call_corpus(library, symbol["name"], symbol["signature"], registers)


def compile_native(directory: Path) -> ctypes.CDLL:
    bodies, _duplicates = _load_bodies(candidates=True)
    library, log = _compile(directory, list(bodies), bodies)
    if library is None:
        raise RuntimeError("native lifecycle link failed: " + " ".join(log.split())[-500:])
    _bind_host(library)
    library.camry_write8.argtypes = [ctypes.c_uint32, ctypes.c_uint32]
    library.camry_write8.restype = None
    return library


def run_native(rows: Sequence[Checkpoint], expected: dict[str, dict[str, str]],
               out: Path) -> tuple[dict[str, dict[str, str]], list[dict[str, Any]]]:
    code = bytearray(IMAGE.read_bytes())
    states: dict[str, dict[str, str]] = {}
    failures: list[dict[str, Any]] = []
    result_dir = out / "native/results"
    result_dir.mkdir(parents=True, exist_ok=True)
    fault_dir = out / "native/faults"
    fault_dir.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="camry-lifecycle-native-", dir=out) as directory:
        library = compile_native(Path(directory))
        for row in rows:
            path = result_dir / f"{row.case.case_id}.json"
            fault_path = fault_dir / f"{row.case.case_id}.log"
            path.unlink(missing_ok=True)
            fault_path.unlink(missing_ok=True)
            pid = os.fork()
            if pid == 0:
                descriptor = os.open(fault_path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
                os.dup2(descriptor, 2)
                os.close(descriptor)
                payload: dict[str, Any]
                try:
                    memory = bytearray(initial_image(row.case))
                    library.camry_host_reset()
                    install_address_space(
                        library, view_of(code), len(code), view_of(memory), RAM_BASE, memory,
                    )
                    initialized: set[int] = set()
                    for index, step in enumerate(row.case.steps):
                        run_native_step(library, step, row.case, index, initialized)
                    current = snapshot_from_memory(memory)
                    contract_error = None
                    want = expected.get(row.case.case_id)
                    if want is not None:
                        scenario = {
                            "name": row.case.name,
                            "checks": state_checks(want),
                        }
                        try:
                            check_results(scenario, row.case.name, memory, RAM_BASE, {}, None)
                        except AssertionError as error:
                            contract_error = str(error)
                    payload = {"state": current, "contract_error": contract_error}
                except BaseException as error:
                    payload = {
                        "error": f"{type(error).__name__}: {error}",
                    }
                path.write_text(json.dumps(payload))
                os._exit(0 if "state" in payload else 1)
            _child, status = os.waitpid(pid, 0)
            fault = fault_path.read_text(errors="replace").strip() if fault_path.is_file() else ""
            if os.WIFSIGNALED(status):
                detail = f"native signal {os.WTERMSIG(status)}"
                if fault:
                    detail += f": {fault}"
                failures.append({"id": row.case.case_id, "detail": detail})
                continue
            if not path.is_file():
                detail = f"native child exit {os.WEXITSTATUS(status)} without result"
                if fault:
                    detail += f": {fault}"
                failures.append({"id": row.case.case_id, "detail": detail})
                continue
            payload = json.loads(path.read_text())
            if "state" in payload:
                states[row.case.case_id] = payload["state"]
            if payload.get("contract_error"):
                failures.append({
                    "id": row.case.case_id,
                    "detail": payload["contract_error"],
                })
            if payload.get("error"):
                failures.append({
                    "id": row.case.case_id,
                    "detail": payload["error"],
                })
    return states, failures


DIAGNOSTIC_TX_BUFFER = 22


def foreground_iteration() -> dict[str, Any]:
    return {
        "max_instructions": 100_000,
        "stop_after_arrivals": [
            {"address": hex(capture_replay.FOREGROUND_WAIT), "count": 2},
        ],
    }


def transmit_completion(evidence: str) -> dict[str, Any]:
    return {
        "kind": "can-tx-complete",
        "buffer": DIAGNOSTIC_TX_BUFFER,
        "firmware_control": "0x8048",
        "tolerate_no_pending": True,
        "after_instructions": 0,
        "evidence": evidence,
    }


def ready_machine_scenario(row: Checkpoint, expected: dict[str, str]) -> dict[str, Any]:
    periods: list[capture_replay.CapturePeriod] = []
    segmented: set[int] = set()
    for index, step in enumerate(row.case.steps):
        receive: tuple[dict[str, Any], ...] = ()
        completions: tuple[dict[str, Any], ...] = ()
        if step.kind == "request":
            single = stateful.Case(
                f"{row.case.name}_machine_step_{index + 1}",
                row.case.session,
                row.case.security_bitmap,
                (step,),
            )
            machine_case = machine_fuzz.from_lifecycle(single)
            frames = [
                item for item in machine_fuzz.machine_events(machine_case)
                if item["kind"] == "can-rx"
            ]
            for item in frames:
                item["after_instructions"] = 0
            receive = tuple(frames)
            if len(frames) > 1:
                segmented.add(index)
            completions = (
                transmit_completion(f"{row.case.name} response-frame completion"),
            )
        periods.append(capture_replay.CapturePeriod(index, receive, completions))
    scenario = capture_replay.build_replay_scenario(
        {
            "kind": "cross-engine-lifecycle",
            "gnu_case_id": row.case.case_id,
            "ready_snapshot_sha256": SNAPSHOT_SHA256,
        },
        periods,
        f"cross_engine_{row.case.case_id}",
        checks=state_checks(expected),
    )
    full_cycle = {
        "max_instructions": capture_replay.FOREGROUND_TRIAL_MAX_INSTRUCTIONS,
        "stop_addresses": [
            hex(capture_replay.BOOT_TRANSFER), "0x619be",
            hex(capture_replay.FOREGROUND_COMPLETE),
        ],
        "stop_after_arrivals": [],
    }

    def position(name: str) -> int:
        return next(
            item for item, step in enumerate(scenario["steps"])
            if step.get("name") == name
        )

    # A segmented period takes two foreground cycles after its frames. The
    # first frame is processed by the communication phase, which transmits flow
    # control; CanTp confirms that frame before it accepts consecutive frames,
    # and the foreground turns a confirmation into the next transmission, so
    # the confirmation needs one wait-loop iteration after the event. The
    # consecutive frames are processed by the communication phase of the next
    # full cycle, which indicates the request to Dcm and posts its dispatch
    # after a delay; the period's native cycle is that dispatch cycle.
    for index in sorted(segmented, reverse=True):
        frames = len(next(period.receive for period in periods if period.index == index))
        last = f"period-{index:05d}-receive-{frames - 1:03d}-ingress"
        scenario["steps"][position(last)].update(full_cycle)
        wait = json.loads(json.dumps(scenario["steps"][position(f"period-{index:05d}-return-to-wait")]))
        wait["name"] = f"period-{index:05d}-processing-return-to-wait"
        scenario["steps"].insert(position(last) + 1, wait)
        first = position(f"period-{index:05d}-receive-000-ingress")
        scenario["steps"][first].update(full_cycle)
        scenario["steps"].insert(first + 1, {
            "kind": "trial",
            "name": f"period-{index:05d}-flow-control-completion",
            **foreground_iteration(),
            "stop_addresses": [],
            "events": [
                transmit_completion(f"{row.case.name} ECU flow-control completion"),
            ],
            "checks": [],
        })
    for index, step in enumerate(row.case.steps):
        if step.kind != "request":
            continue
        completion_step = next(
            item for item in scenario["steps"]
            if item.get("name") == f"period-{index:05d}-transmit-completions"
        )
        completion_step.update(foreground_iteration())
    scenario["steps"].insert(capture_replay.REPLAY_PREFIX_STEPS, {
        "kind": "trial",
        "name": "lifecycle-primes",
        "max_instructions": 1,
        "stop_addresses": [],
        "stop_after_arrivals": [
            {"address": hex(capture_replay.FOREGROUND_WAIT), "count": 1},
        ],
        "events": initial_overlay_events(row.case),
        "checks": [],
    })
    for step in scenario["steps"]:
        if step.get("kind") == "trial":
            step["capture_rows"] = False
    return scenario

def ready_machine_batch(
    rows: Sequence[Checkpoint], expected: dict[str, dict[str, str]], name: str,
) -> dict[str, Any]:
    scenarios = [ready_machine_scenario(row, expected[row.case.case_id]) for row in rows]
    combined = capture_replay.batch_replay_scenarios(
        [(row.case.case_id, scenario) for row, scenario in zip(rows, scenarios, strict=True)],
        name,
    )
    combined["source"] = {
        "kind": "cross-engine-lifecycle-batch",
        "case_ids": [row.case.case_id for row in rows],
        "ready_snapshot_sha256": SNAPSHOT_SHA256,
    }
    for step in combined["steps"]:
        trial_name = str(step.get("name", ""))
        if step.get("kind") != "trial" or "::" not in trial_name:
            continue
        case_id = trial_name.split("::", 1)[0]
        for check in step.get("checks", []):
            check["name"] = f"{case_id}::{check['name']}"
    return combined


def states_from_machine_batch(report: dict[str, Any]) -> dict[str, dict[str, str]]:
    states: dict[str, dict[str, str]] = defaultdict(dict)
    for trial in report.get("checkpointing", {}).get("trials", []):
        for row in trial.get("checks", []):
            name = row.get("name", "")
            if (
                row.get("kind") != "memory"
                or "::state-" not in name
                or row.get("actual") == "unavailable"
            ):
                continue
            case_id, address = name.split("::state-", 1)
            states[case_id]["0x" + address.removeprefix("0x").upper()] = row["actual"]
    return dict(states)


def state_from_machine_report(report: dict[str, Any]) -> dict[str, str]:
    checks = list(report.get("checks", []))
    for trial in report.get("checkpointing", {}).get("trials", []):
        checks.extend(trial.get("checks", []))
    return {
        "0x" + row["name"].removeprefix("state-").upper(): row["actual"]
        for row in checks
        if (
            row.get("kind") == "memory"
            and row.get("name", "").startswith("state-")
            and row.get("actual") != "unavailable"
        )
    }


def run_machine(
    rows: Sequence[Checkpoint], expected: dict[str, dict[str, str]],
    out: Path, batch_size: int,
) -> tuple[dict[str, dict[str, str]], list[dict[str, Any]]]:
    scenario_dir = out / "machine/scenarios"
    scenario_dir.mkdir(parents=True, exist_ok=True)
    selected: list[Checkpoint] = []
    failures: list[dict[str, Any]] = []
    seen: set[str] = set()
    for row in rows:
        if row.case.case_id in seen:
            continue
        seen.add(row.case.case_id)
        if row.case.case_id not in expected:
            failures.append({"id": row.case.case_id, "detail": "GNU checkpoint unavailable"})
            continue
        selected.append(row)
    batches = [
        selected[offset:offset + batch_size]
        for offset in range(0, len(selected), batch_size)
    ]
    report_dir = out / "machine/reports"
    report_dir.mkdir(parents=True, exist_ok=True)
    reports = []
    for index, batch in enumerate(batches):
        scenario_text = json.dumps(
            ready_machine_batch(batch, expected, f"cross_engine_batch_{index:03d}"),
            separators=(",", ":"),
        ) + "\n"
        path = scenario_dir / f"batch_{index:03d}.json"
        path.write_text(scenario_text)
        digest = hashlib.sha256(scenario_text.encode()).hexdigest()
        report_path = report_dir / f"batch_{index:03d}.report.json"
        digest_path = report_dir / f"batch_{index:03d}.sha256"
        if (
            report_path.exists() and digest_path.exists()
            and digest_path.read_text().strip() == digest
        ):
            reports.append(json.loads(report_path.read_text()))
            continue
        # One batch per machine run: a daemon death costs one batch, and a
        # rerun resumes from every batch whose report matches its scenario.
        report = capture_many(
            TARGET, [path], report_dir, instruction_trace=False,
        )[0]
        digest_path.write_text(f"{digest}\n")
        reports.append(report)
    states: dict[str, dict[str, str]] = {}
    for batch, report in zip(batches, reports, strict=True):
        batch_states = states_from_machine_batch(report)
        boot_cases = {
            str(trial["name"]).split("::", 1)[0]
            for trial in report.get("checkpointing", {}).get("trials", [])
            if (
                "::" in str(trial.get("name", ""))
                and trial.get("termination_reason") == "stop-address"
                and int(trial.get("final_pc", "0"), 0) == capture_replay.BOOT_TRANSFER
            )
        }
        for case_id in boot_cases:
            batch_states.pop(case_id, None)
            failures.append({
                "id": case_id,
                "detail": (
                    "READY snapshot mode 0x0900 takes 0x5F9BC -> 0x56CF6; "
                    "NVM-ready gate 0x66F1E returns 1 and call 0x56D06 enters "
                    "boot transfer 0x65F5E before the request is serviced"
                ),
            })
        states.update(batch_states)
        if report.get("termination_reason") in {
            "runner-error", "unexpected-fault", "instruction-budget",
        }:
            detail = report.get("error", report.get("termination_reason"))
            failures.extend(
                {"id": row.case.case_id, "detail": detail}
                for row in batch
                if row.case.case_id not in boot_cases
            )
            continue
        for row in batch:
            if row.case.case_id in boot_cases:
                continue
            if row.case.case_id not in states:
                failures.append({
                    "id": row.case.case_id,
                    "detail": "batch completed without a state checkpoint",
                })
    return states, failures


def diagnose(machine_cmp: dict[str, Any], native_cmp: dict[str, Any],
             disposition: str, native_available: bool,
             machine_available: bool, native_failure: str = "",
             machine_failure: str = "") -> str:
    if not native_available:
        return f"native C checkpoint unavailable: {native_failure or 'isolated host fault'}"
    if not machine_available:
        return f"machine checkpoint unavailable: {machine_failure or 'engine failure'}"
    if native_cmp["equal"] and machine_cmp["equal"]:
        return "all three engines agree on the compared state"
    if not native_cmp["equal"]:
        return "reconstructed C departs from GNU-sim execution of the original bytes at the reported address"
    groups = machine_cmp["groups"]
    if not groups["contract"]:
        return (
            "machine foreground cycle ran the service's application work after the "
            "Dcm call (foreground-cycle state); direct engines execute the Dcm call only"
        )
    if disposition.startswith("unsupported"):
        return (
            "machine ingress has no external event for this synthetic DCM callback "
            "action; contract state differs at " + ", ".join(groups["contract"])
        )
    return "contract state differs at " + ", ".join(groups["contract"])


def oracle_contract(out: Path) -> dict[str, Any]:
    path = out / "native-oracle.txt"
    result = subprocess.run(
        [str(REPO_ROOT / "tools/toyota"), "decomp", "oracle"],
        cwd=REPO_ROOT, text=True, capture_output=True,
    )
    text = result.stdout + result.stderr
    path.write_text(text)
    return {
        "command": "tools/toyota decomp oracle",
        "returncode": result.returncode,
        "output": str(path),
        "tail": text.splitlines()[-8:],
        "contract": "existing original-byte/native-C register and memory comparison",
    }


def build_report(rows: Sequence[Checkpoint], gnu: dict[str, dict[str, str]],
                 native: dict[str, dict[str, str]], machine: dict[str, dict[str, str]],
                 engine_failures: dict[str, list[dict[str, Any]]], oracle: dict[str, Any]) -> dict[str, Any]:
    failure_details = {
        engine: {
            case_id: "; ".join(
                detail if isinstance(detail := item["detail"], str)
                else json.dumps(detail, sort_keys=True)
                for item in failures if item["id"] == case_id
            )
            for case_id in {item["id"] for item in failures}
        }
        for engine, failures in engine_failures.items()
    }
    results = []
    for row in rows:
        gnu_state = gnu.get(row.case.case_id, {})
        native_state = native.get(row.case.case_id, {})
        machine_state = machine.get(row.case.case_id, {})
        native_available = bool(native_state)
        machine_available = bool(machine_state)
        unavailable = {
            "equal": False, "first_difference": None,
            "differences": [], "groups": difference_groups(()),
        }
        native_cmp = comparison(gnu_state, native_state) if gnu_state and native_state else unavailable
        machine_cmp = comparison(gnu_state, machine_state) if gnu_state and machine_state else dict(unavailable)
        equal = native_cmp["equal"] and machine_cmp["equal"]
        results.append({
            "case": row.owner_name,
            "case_id": row.owner_id,
            "checkpoint": row.index,
            "step": row.step_kind,
            "class": row.lifecycle_class,
            "machine_disposition": row.disposition,
            "engine_available": {
                "gnu": bool(gnu_state),
                "native": native_available,
                "machine": machine_available,
            },
            "equal": equal,
            "contract_equal": not machine_cmp["groups"]["contract"],
            "gnu_vs_native": native_cmp,
            "gnu_vs_machine": machine_cmp,
            "diagnosis": diagnose(
                machine_cmp, native_cmp, row.disposition,
                native_available, machine_available,
                failure_details.get("native", {}).get(row.case.case_id, ""),
                failure_details.get("machine", {}).get(row.case.case_id, ""),
            ),
        })
    counts = Counter(
        "unavailable" if not all(row["engine_available"].values()) else
        "equal" if row["equal"] else
        "foreground_only" if row["contract_equal"] else
        "diverged"
        for row in results
    )
    return {
        "schema": SCHEMA,
        "target": TARGET,
        "scope": {
            "seed_cases": len(stateful.seed_cases()),
            "representatives_per_machine_class": REPRESENTATIVES_PER_CLASS,
            "machine_classes": list(MACHINE_CLASSES),
            "cases": len({row.owner_id for row in rows}),
            "checkpoints": len(rows),
        },
        "state_ranges": [
            {"address": f"0x{lo:08X}", "size": hi - lo + 1}
            for lo, hi in STATE_RANGES
        ],
        "state_exclusions": [
            {"address": f"0x{lo:08X}", "size": hi - lo + 1, "reason": reason}
            for lo, hi, reason in DIRECT_ONLY_RANGES
        ],
        "foreground_cycle_ranges": [
            {"address": f"0x{lo:08X}", "size": hi - lo + 1}
            for lo, hi in FOREGROUND_CYCLE_RANGES
        ],
        "register_comparison": {
            "gnu_vs_native": oracle,
            "machine": "not compared: real ingress and direct calls do not share an ABI checkpoint",
        },
        "summary": {
            "cases": len({row.owner_id for row in rows}),
            "checkpoints": len(rows),
            "equal": counts["equal"],
            "foreground_only": counts["foreground_only"],
            "diverged": counts["diverged"],
            "unavailable": counts["unavailable"],
        },
        "engine_failures": engine_failures,
        "results": results,
    }


def materialize_readiness_ram(out: Path) -> tuple[Path, str]:
    path = (out / "ready_local_ram.bin").resolve()
    empty = capture_replay.CapturePeriod(0, (), ())
    scenario = capture_replay.build_replay_scenario(
        {"kind": "cross-engine-readiness-snapshot"},
        (empty,),
        "cross-engine-readiness-snapshot",
        include_completions=False,
        checks=capture_replay.END_MODE_CHECKS,
    )
    for step in scenario["steps"]:
        if step.get("kind") == "trial":
            step["capture_rows"] = False
    scenario["snapshot_outputs"] = [{
        "path": str(path),
        "address": hex(RAM_BASE),
        "size": dcm.RAM_SIZE,
        "evidence": "Cross-engine common normal-operation LocalRAM image",
    }]
    scenario_path = out / "machine/scenarios/readiness.json"
    scenario_path.parent.mkdir(parents=True, exist_ok=True)
    scenario_path.write_text(
        json.dumps(scenario, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )
    report = capture_many(
        TARGET, [scenario_path], out / "machine/readiness",
        instruction_trace=False,
    )[0]
    if report.get("termination_reason") == "runner-error" or not path.exists():
        raise RuntimeError(f"readiness snapshot failed: {report.get('error', report)}")
    payload = path.read_bytes()
    digest = hashlib.sha256(payload).hexdigest()
    return path, digest


def campaign(out: Path, timeout: float, batch_size: int) -> dict[str, Any]:
    global SNAPSHOT, SNAPSHOT_SHA256
    out.mkdir(parents=True, exist_ok=True)
    SNAPSHOT, SNAPSHOT_SHA256 = materialize_readiness_ram(out)
    rows = checkpoints(selected_cases())
    gnu, gnu_failures = run_gnu(rows, out, timeout, batch_size)
    native, native_failures = run_native(rows, gnu, out)
    try:
        machine, machine_failures = run_machine(rows, gnu, out, batch_size)
    except RuntimeError as first_error:
        try:
            machine, machine_failures = run_machine(rows, gnu, out, batch_size)
            machine_failures.insert(0, {
                "id": "campaign",
                "detail": f"first machine attempt failed, retry completed: {first_error}",
            })
        except RuntimeError as second_error:
            machine = {}
            machine_failures = [{
                "id": "campaign",
                "detail": (
                    f"machine failed during in-flight owner edits; first={first_error}; "
                    f"retry={second_error}"
                ),
            }]
    oracle = oracle_contract(out)
    report = build_report(
        rows, gnu, native, machine,
        {"gnu": gnu_failures, "native": native_failures, "machine": machine_failures},
        oracle,
    )
    (out / "report.json").write_text(json.dumps(report, indent=2) + "\n")
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--timeout", type=float, default=120.0)
    parser.add_argument("--batch-size", type=int, default=16)
    args = parser.parse_args()
    if args.timeout <= 0 or args.batch_size < 1:
        parser.error("timeout and batch size must be positive")
    report = campaign(args.out, args.timeout, args.batch_size)
    print(json.dumps({"report": str(args.out / "report.json"), **report["summary"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
