#!/usr/bin/env python3
"""Probe the F33 SID 0xAB merge path in the original RH850 CodeFlash image.

This function-level harness restores LocalRAM and a separate simulator RAM
region before every trial, calls the stock 0x8DEE2 or 0x8E074 entry directly,
and uses simulator instruction/core traces to count instructions and record
all data reads and writes.  It intentionally does not patch either target
function.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path

from tools import REPO_ROOT
from tools.rh850_codeflash import run, run_elf

IMAGE = REPO_ROOT / "firmware/camry-8965F3307000/CodeFlash.bin"
IMAGE_SHA256 = "42dce8efc42f6ae31718e7713fa2d26bb9191b4a82439778aee4d7afded9b0e7"
DEFAULT_OUT = (
    REPO_ROOT
    / "build/out/targets/camry-8965F3307000/ab-merge-capacity-20261123/isolated"
)
NULL_SOURCE_WINDOW = 0x1000

MERGE_ENTRY = 0x8DEE2
SERIALIZE_ENTRY = 0x8E074
SENTINEL = 0x798
MERGE_LOOP_GUARD_PC = 0x8DF24
MERGE_LOOP_GUARD_IGNORE = 40000

GP = 0xFEBEB800
TP = 0x23DFC
STACK_TOP = 0xFEBE2000
RAM_BASE = 0xFEBE0000
RAM_SIZE = 0x20000
RAM_REGION = f"{RAM_BASE:#x},{RAM_SIZE:#x}"

# This simulator-only region keeps synthetic descriptors, sources, and output
# separate from LocalRAM.  The 16-bit merge index can address B..B+0xFFFF.
ISO_BASE = 0xFE800000
ISO_SIZE = 0x40000
ISO_REGION = f"{ISO_BASE:#x},{ISO_SIZE:#x}"
A_DESC1 = ISO_BASE + 0x100
A_DESC2 = ISO_BASE + 0x110
A_OUT_DESC = ISO_BASE + 0x120
A_LENGTH = ISO_BASE + 0x130
A_SOURCE1 = ISO_BASE + 0x1000
A_SOURCE2 = ISO_BASE + 0x11000
B_CAPACITY_WORD = ISO_BASE + 0x100
B_NRC = ISO_BASE + 0x108
OUTPUT_B = ISO_BASE + 0x20000
OUTPUT_CAPACITY = 0x300

AB_STATE = 0xFEBF45D0
AB_STAGING = 0xFEBF45E4
AB_STAGING_CAPACITY = 0x300
EVENT_SERIALIZER_SELECTOR = 0xFEBE81AD
LATCHED_EVENT_BITMAP = 0xFEBE8A04
EVENT_CATALOGUE = 0x2AB70
EVENT_CATALOGUE_SLOTS = 64
EVENT_CATALOGUE_STRIDE = 8

REQUIRED_N1 = (0, 2, 16, 0x2FC, 0x300, 0x302, 0xFFFE, 0xFFFF)
REQUIRED_N2 = (0, 2, 0x40)
ODD_N1 = (1, 3, 0x2FD, 0x2FF, 0x301)
ODD_N2 = (1, 3, 0x3F)

TPR_RE = re.compile(
    r"^TPR (\d+) (\d+) (\d+) (\d+) (\d+) (\d+) (\d+) (\d+)$",
    re.MULTILINE,
)
CORE_RE = re.compile(
    r"^(read|write)-(\d+) (exec|read|write):0x([0-9a-fA-F]+) (?:->|<-) 0x([0-9a-fA-F]+)$"
)


@dataclass(frozen=True)
class Trial:
    experiment: str
    family: str
    entry: int
    inputs: dict
    regs: tuple[int, int, int]
    local_image: bytes
    iso_image: bytes
    loop_guard: bool = False


@dataclass(frozen=True)
class TraceObservation:
    instruction_count: int
    writes: tuple[tuple[int, int, int], ...]
    reads: tuple[tuple[int, int, int], ...]


def hex_or_none(value: int | None) -> str | None:
    return None if value is None else hex(value)


def write_bytes(image: bytearray, base: int, address: int, data: bytes) -> None:
    offset = address - base
    if offset < 0 or offset + len(data) > len(image):
        raise ValueError(f"write {address:#x}+{len(data):#x} escapes image {base:#x}")
    image[offset:offset + len(data)] = data


def poison_image(salt: int) -> bytearray:
    return bytearray(((offset * 0x3D + salt * 0x11 + 0xA5) & 0xFF)
                     for offset in range(ISO_SIZE))


def descriptor(status: int, count: int, pointer: int) -> bytes:
    return bytes((status & 0xFF, 0)) + count.to_bytes(2, "little") + pointer.to_bytes(4, "little")


def sorted_be16_source(size: int, parity: int) -> bytes:
    rounded = min((size + 1) & ~1, 0x10000)
    result = bytearray(rounded)
    for offset in range(0, rounded, 2):
        value = ((offset // 2) * 2 + parity) & 0xFFFF
        result[offset:offset + 2] = value.to_bytes(2, "big")
    return bytes(result)


def populated_catalogue_slots(image: bytes) -> tuple[int, ...]:
    slots = tuple(
        index
        for index in range(EVENT_CATALOGUE_SLOTS)
        if int.from_bytes(
            image[
                EVENT_CATALOGUE + index * EVENT_CATALOGUE_STRIDE:
                EVENT_CATALOGUE + index * EVENT_CATALOGUE_STRIDE + 2
            ],
            "little",
        )
    )
    if len(slots) != 51:
        raise SystemExit(f"event catalogue population changed: expected 51, got {len(slots)}")
    return slots


def make_a_trial(
    index: int,
    *,
    status_mode: str,
    n1: int,
    n2: int,
    ptr2: str,
) -> Trial:
    status = 1 if status_mode == "specified-one" else 0
    local = bytes(RAM_SIZE)
    iso = poison_image(index)
    write_bytes(iso, ISO_BASE, A_DESC1, descriptor(status, n1, A_SOURCE1))
    pointer2 = 0 if ptr2 == "null" else A_SOURCE2
    write_bytes(iso, ISO_BASE, A_DESC2, descriptor(status, n2, pointer2))
    # The stock ABI at 0x8DFEA loads a u32 pointer from out+4, then 0x8DFEE
    # stores the u16 result through it.  A_LENGTH itself starts at zero.
    write_bytes(
        iso,
        ISO_BASE,
        A_OUT_DESC,
        OUTPUT_B.to_bytes(4, "little") + A_LENGTH.to_bytes(4, "little"),
    )
    write_bytes(iso, ISO_BASE, A_LENGTH, b"\x00\x00")
    write_bytes(iso, ISO_BASE, A_SOURCE1, sorted_be16_source(n1, 0))
    if ptr2 == "valid":
        write_bytes(iso, ISO_BASE, A_SOURCE2, sorted_be16_source(n2, 1))
    loop_guard = status == 0 and n1 == 0xFFFF
    return Trial(
        experiment="A-direct-merge",
        family=status_mode,
        entry=MERGE_ENTRY,
        inputs={
            "status_mode": status_mode,
            "status1": status,
            "status2": status,
            "n1": n1,
            "n2": n2,
            "ptr2": ptr2,
            "output_capacity": OUTPUT_CAPACITY,
            "output_descriptor_length_pointer": hex(A_LENGTH),
            "output_length_initial": 0,
        },
        regs=(A_DESC1, A_DESC2, A_OUT_DESC),
        local_image=local,
        iso_image=bytes(iso),
        loop_guard=loop_guard,
    )

def make_b_trial(
    index: int,
    populated_slots: tuple[int, ...],
    *,
    phase: int,
    capacity: int,
    n1: int,
    n2: int,
    selector: int,
    selected_count: int | None,
) -> Trial:
    local = bytearray(RAM_SIZE)
    iso = poison_image(index)
    state = bytearray(0x320)
    state[0x04:0x06] = (n1 if phase == 2 else 0).to_bytes(2, "little")
    state[0x06:0x08] = AB_STAGING_CAPACITY.to_bytes(2, "little")
    state[0x08:0x0A] = n2.to_bytes(2, "little")
    state[0x0C] = 1                 # merge arm
    state[0x0D] = 0 if phase == 2 else 1
    state[0x0E] = 0
    state[0x0F] = 1                 # second-list status
    state[0x10] = 0
    state[0x11] = phase
    state[0x12] = 0xFF
    state[0x13] = 1
    if phase == 2:
        source = sorted_be16_source(n1, 0)
        state[0x14:0x14 + len(source)] = source
    write_bytes(local, RAM_BASE, AB_STATE, state)
    write_bytes(local, RAM_BASE, EVENT_SERIALIZER_SELECTOR, bytes((selector,)))
    if selected_count is not None:
        bitmap = 0
        for slot in populated_slots[:selected_count]:
            bitmap |= 1 << slot
        write_bytes(local, RAM_BASE, LATCHED_EVENT_BITMAP, bitmap.to_bytes(8, "little"))
    write_bytes(iso, ISO_BASE, B_CAPACITY_WORD, capacity.to_bytes(4, "little"))
    write_bytes(iso, ISO_BASE, B_NRC, b"\x00")
    expected_serialized = None if selected_count is None else selected_count * 2
    return Trial(
        experiment="B-serialize-and-merge",
        family=f"phase-{phase}-selector-{selector}",
        entry=SERIALIZE_ENTRY,
        inputs={
            "phase": phase,
            "merge_flag": 1,
            "capacity_in": capacity,
            "state_n1_initial": n1 if phase == 2 else 0,
            "state_n2": n2,
            "state_status1_initial": 0 if phase == 2 else 1,
            "state_status2": 1,
            "serializer_selector": selector,
            "selected_event_count": selected_count,
            "expected_phase0_serialized_bytes": expected_serialized,
            "r6_observed_role": "output-pointer",
            "r7_observed_role": "pointer-to-capacity-in-and-length-out-u32",
            "r8_observed_role": "nrc-output-pointer",
        },
        regs=(OUTPUT_B, B_CAPACITY_WORD, B_NRC),
        local_image=bytes(local),
        iso_image=bytes(iso),
    )


def generate_trials(image: bytes) -> list[Trial]:
    populated = populated_catalogue_slots(image)
    trials: list[Trial] = []

    # Literal requested matrix: both status bytes are one.  Stock code returns
    # at 0x8DF0C, so the second matrix uses the observed success value zero to
    # exercise the actual merge loop.
    for n1 in REQUIRED_N1:
        for n2 in REQUIRED_N2:
            for ptr2 in ("null", "valid"):
                trials.append(make_a_trial(
                    len(trials), status_mode="specified-one", n1=n1, n2=n2, ptr2=ptr2,
                ))
    expanded_n1 = tuple(dict.fromkeys((*REQUIRED_N1, *ODD_N1)))
    expanded_n2 = tuple(dict.fromkeys((*REQUIRED_N2, *ODD_N2)))
    for n1 in expanded_n1:
        for n2 in expanded_n2:
            for ptr2 in ("null", "valid"):
                trials.append(make_a_trial(
                    len(trials), status_mode="merge-zero", n1=n1, n2=n2, ptr2=ptr2,
                ))

    # Phase 0 drives the stock event serializer.  Selector one serializes the
    # selected catalogue identifiers as BE16 values; selector zero is the
    # reset/idle control that returns status 10.
    phase0_counts = (0, 1, 2, 16, 32, 51)
    phase0_capacities = (0, 2, 16, 64, 102, 0x2FE, 0x2FF, 0x300)
    for selected_count in phase0_counts:
        for capacity in phase0_capacities:
            for n2 in (0, 2, 0x40):
                trials.append(make_b_trial(
                    len(trials), populated,
                    phase=0,
                    capacity=capacity,
                    n1=0,
                    n2=n2,
                    selector=1,
                    selected_count=selected_count,
                ))
    for capacity in (0, 0x2FF, 0x300, 0x10000):
        trials.append(make_b_trial(
            len(trials), populated,
            phase=0,
            capacity=capacity,
            n1=0,
            n2=0,
            selector=0,
            selected_count=None,
        ))
    for selected_count, n2 in ((51, 0), (0, 0x40)):
        trials.append(make_b_trial(
            len(trials), populated,
            phase=0,
            capacity=0x10000,
            n1=0,
            n2=n2,
            selector=1,
            selected_count=selected_count,
        ))

    # Phase 2 with status != 2 skips the serializer and exposes the direct
    # state-to-merge contract: the incoming capacity word is not consulted.
    phase2_capacities = (0, 1, 2, 0x2FE, 0x2FF, 0x300)
    phase2_lengths = (0, 1, 2, 0x2FC, 0x2FD, 0x2FE, 0x2FF, 0x300, 0x301, 0x302)
    for capacity in phase2_capacities:
        for n1 in phase2_lengths:
            trials.append(make_b_trial(
                len(trials), populated,
                phase=2,
                capacity=capacity,
                n1=n1,
                n2=0,
                selector=0,
                selected_count=None,
            ))
    for capacity in (0x2FE, 0x2FF, 0x300):
        for n1 in (0x2FC, 0x2FD, 0x2FE, 0x2FF, 0x300):
            for n2 in (2, 0x40):
                trials.append(make_b_trial(
                    len(trials), populated,
                    phase=2,
                    capacity=capacity,
                    n1=n1,
                    n2=n2,
                    selector=0,
                    selected_count=None,
                ))
    for n2 in (2, 0x40):
        trials.append(make_b_trial(
            len(trials), populated,
            phase=2,
            capacity=0,
            n1=0,
            n2=n2,
            selector=0,
            selected_count=None,
        ))
    return trials

def gdb_prelude() -> list[str]:
    return [
        f"set $r4={GP:#x}",
        f"set $r5={TP:#x}",
        f"set $tp={TP:#x}",
        # Established simulator-only PMR thunk patches.  0x007f is jmp [lp].
        "set {unsigned short}0x6a45e = 0x007f",
        "set {unsigned short}0x6a4c4 = 0x007f",
        "set {unsigned short}0x701c4 = 0x007f",
        "set {unsigned short}0x70204 = 0x007f",
        f"break *{SENTINEL:#x}",
    ]


def trial_commands(index: int, trial: Trial) -> list[str]:
    r6, r7, r8 = trial.regs
    commands = [
        f"restore /out/local-{index:06d}.bin binary {RAM_BASE:#x}",
        f"restore /out/iso-{index:06d}.bin binary {ISO_BASE:#x}",
        f"set $r3={STACK_TOP:#x}",
        f"set $r31={SENTINEL:#x}",
        f"set $r5={TP:#x}",
        f"set $tp={TP:#x}",
        f"set $r6={r6:#x}",
        f"set $r7={r7:#x}",
        f"set $r8={r8:#x}",
        f"set $pc={trial.entry:#x}",
    ]
    if trial.loop_guard:
        commands.extend((
            f"break *{MERGE_LOOP_GUARD_PC:#x}",
            "set $loop_guard=$bpnum",
            f"ignore $loop_guard {MERGE_LOOP_GUARD_IGNORE}",
        ))
    commands.extend((
        f"sim trace-file /out/trace-{index:06d}.txt",
        "sim trace-insn on",
        "sim trace-core on",
        "continue",
        "sim trace-insn off",
        "sim trace-core off",
        f"dump binary memory /out/dump-{index:06d}.bin {ISO_BASE:#x} {ISO_BASE + ISO_SIZE:#x}",
        (f'printf "TPR {index} %u %u %u %u %u %u %u\\n", '
         "$pc, $r10, $r1, $r18, $r19, $r3, $r31"),
    ))
    if trial.loop_guard:
        commands.append("delete $loop_guard")
    commands.append(f"set $pc={SENTINEL:#x}")
    return commands


def batch_commands(indexed: list[tuple[int, Trial]]) -> list[str]:
    commands = gdb_prelude()
    for index, trial in indexed:
        commands.extend(trial_commands(index, trial))
    commands.append(f'printf "TP_END={indexed[-1][0]}\\n"')
    return commands


def parse_trace(path: Path) -> TraceObservation:
    instruction_count = 0
    writes: list[tuple[int, int, int]] = []
    reads: list[tuple[int, int, int]] = []
    with path.open(encoding="utf-8") as stream:
        for line in stream:
            if line.startswith("insn:"):
                if " dbtrap " not in line:
                    instruction_count += 1
                continue
            match = CORE_RE.match(line.rstrip())
            if match is None:
                continue
            operation, width, kind, address, value = match.groups()
            if kind == "exec":
                continue
            row = (int(address, 16), int(width), int(value, 16))
            if operation == "write":
                writes.append(row)
            else:
                reads.append(row)
    return TraceObservation(instruction_count, tuple(writes), tuple(reads))


def expand_addresses(events: Iterable[tuple[int, int, int]]) -> set[int]:
    result: set[int] = set()
    for address, width, _value in events:
        result.update(range(address, address + width))
    return result


def address_runs(addresses: Iterable[int], *, relative_to: int | None = None) -> list[list[str]]:
    values = sorted(set(addresses))
    if not values:
        return []
    runs: list[tuple[int, int]] = []
    lo = hi = values[0]
    for value in values[1:]:
        if value == hi + 1:
            hi = value
        else:
            runs.append((lo, hi))
            lo = hi = value
    runs.append((lo, hi))
    if relative_to is not None:
        runs = [(lo - relative_to, hi - relative_to) for lo, hi in runs]
    return [[hex(lo), hex(hi)] for lo, hi in runs]


def intersect_event_addresses(
    events: Iterable[tuple[int, int, int]], lo: int, hi: int,
) -> set[int]:
    result: set[int] = set()
    for address, width, _value in events:
        start = max(address, lo)
        end = min(address + width, hi)
        if start < end:
            result.update(range(start, end))
    return result


def summarize_output(dump: bytes, trace: TraceObservation, capacity: int) -> dict:
    output_addresses = intersect_event_addresses(
        trace.writes, OUTPUT_B, ISO_BASE + ISO_SIZE,
    )
    max_offset = max(output_addresses) - OUTPUT_B if output_addresses else None
    span = b"" if max_offset is None else dump[
        OUTPUT_B - ISO_BASE:OUTPUT_B - ISO_BASE + max_offset + 1
    ]
    boundary_lo = OUTPUT_B - ISO_BASE + 0x2F0
    boundary_hi = OUTPUT_B - ISO_BASE + 0x310
    event_count = sum(
        1 for address, width, _value in trace.writes
        if address < ISO_BASE + ISO_SIZE and address + width > OUTPUT_B
    )
    return {
        "write_event_count": event_count,
        "unique_byte_count": len(output_addresses),
        "absolute_runs": address_runs(output_addresses),
        "relative_runs": address_runs(output_addresses, relative_to=OUTPUT_B),
        "max_offset": hex_or_none(max_offset),
        "exceeds_0x300": max_offset is not None and max_offset >= OUTPUT_CAPACITY,
        "exceeds_caller_capacity": max_offset is not None and max_offset >= capacity,
        "bytes_b_through_b_plus_31": dump[
            OUTPUT_B - ISO_BASE:OUTPUT_B - ISO_BASE + 0x20
        ].hex(),
        "bytes_around_0x300_boundary": dump[boundary_lo:boundary_hi].hex(),
        "written_span_sha256": hashlib.sha256(span).hexdigest() if span else None,
    }


def read_runs(trace: TraceObservation, lo: int, hi: int) -> list[list[str]]:
    return address_runs(intersect_event_addresses(trace.reads, lo, hi))


def record_trial(
    index: int,
    trial: Trial,
    stop_values: tuple[int, int, int, int, int, int, int],
    trace: TraceObservation,
    dump: bytes,
) -> dict:
    pc, r10, r1, r18, r19, sp, lp = stop_values
    if trial.experiment == "A-direct-merge":
        capacity = OUTPUT_CAPACITY
        length_out = int.from_bytes(
            dump[A_LENGTH - ISO_BASE:A_LENGTH - ISO_BASE + 2], "little"
        )
    else:
        capacity = int(trial.inputs["capacity_in"])
        length_out = int.from_bytes(
            dump[B_CAPACITY_WORD - ISO_BASE:B_CAPACITY_WORD - ISO_BASE + 4], "little"
        )
    output = summarize_output(dump, trace, capacity)
    low_reads = intersect_event_addresses(trace.reads, 0, NULL_SOURCE_WINDOW)
    write_addresses = expand_addresses(trace.writes)
    termination = "returned" if pc == SENTINEL else (
        "loop-wrap-guard" if pc == MERGE_LOOP_GUARD_PC and trial.loop_guard else "abnormal-stop"
    )
    return {
        "index": index,
        "experiment": trial.experiment,
        "family": trial.family,
        "inputs": trial.inputs,
        "registers": {
            "input": {
                "pc": hex(trial.entry),
                "r3_sp": hex(STACK_TOP),
                "r4_gp": hex(GP),
                "r5_tp_alias": hex(TP),
                "tp": hex(TP),
                "r6": hex(trial.regs[0]),
                "r7": hex(trial.regs[1]),
                "r8": hex(trial.regs[2]),
                "r31_lp": hex(SENTINEL),
            },
            "stop": {
                "pc": hex(pc),
                "r10": hex(r10),
                "r1": hex(r1),
                "r18": hex(r18),
                "r19": hex(r19),
                "r3_sp": hex(sp),
                "r31_lp": hex(lp),
            },
        },
        "stop_pc": hex(pc),
        "termination": termination,
        "instruction_count": trace.instruction_count,
        "instruction_count_scope": (
            "entry-through-return" if termination == "returned" else "entry-through-loop-wrap-guard"
        ),
        "reported_output_length": length_out,
        "write_summary": {
            "all_write_event_count": len(trace.writes),
            "all_unique_byte_count": len(write_addresses),
            "all_write_runs": address_runs(write_addresses),
            "output_at_and_after_b": output,
            "length_pointer_writes": address_runs(intersect_event_addresses(
                trace.writes,
                A_LENGTH if trial.experiment == "A-direct-merge" else B_CAPACITY_WORD,
                (A_LENGTH + 2) if trial.experiment == "A-direct-merge" else (B_CAPACITY_WORD + 4),
            )),
        },
        "read_summary": {
            "null_pointer_codeflash_source_runs": address_runs(low_reads),
            "null_pointer_codeflash_source_unique_bytes": len(low_reads),
            "list1_source_runs": read_runs(
                trace,
                A_SOURCE1 if trial.experiment == "A-direct-merge" else AB_STAGING,
                (A_SOURCE1 + 0x10000) if trial.experiment == "A-direct-merge" else (AB_STAGING + 0x1000),
            ),
            "valid_list2_source_runs": read_runs(trace, A_SOURCE2, A_SOURCE2 + 0x100),
        },
    }


def make_batches(trials: list[Trial]) -> list[list[tuple[int, Trial]]]:
    batches: list[list[tuple[int, Trial]]] = []
    current: list[tuple[int, Trial]] = []
    heavy = False
    for indexed in enumerate(trials):
        trial_heavy = indexed[1].loop_guard or (
            indexed[1].experiment == "A-direct-merge"
            and indexed[1].family == "merge-zero"
            and int(indexed[1].inputs["n1"]) >= 0xFFFE
        )
        limit = 2 if trial_heavy else 16
        if current and (trial_heavy != heavy or len(current) >= limit):
            batches.append(current)
            current = []
        if not current:
            heavy = trial_heavy
        current.append(indexed)
    if current:
        batches.append(current)
    return batches


def run_batch(
    elf: Path,
    indexed: list[tuple[int, Trial]],
    out: Path,
    batch_number: int,
    timeout: float,
) -> list[dict]:
    work = elf.parent
    for index, trial in indexed:
        (work / f"local-{index:06d}.bin").write_bytes(trial.local_image)
        (work / f"iso-{index:06d}.bin").write_bytes(trial.iso_image)
        (work / f"trace-{index:06d}.txt").unlink(missing_ok=True)
        (work / f"dump-{index:06d}.bin").unlink(missing_ok=True)
    log_path = out / f"batch-{batch_number:04d}.txt"
    marker = f"TP_END={indexed[-1][0]}"
    output = run_elf(
        root=REPO_ROOT,
        elf_path=elf,
        stop=f"{SENTINEL:#x}",
        memory_regions=[RAM_REGION, ISO_REGION],
        gdb_commands=batch_commands(indexed),
        expected_output=[marker],
        timeout=timeout,
        output_path=log_path,
    )
    stops = {
        int(match.group(1)): tuple(int(match.group(column)) for column in range(2, 9))
        for match in TPR_RE.finditer(output)
    }
    if stops.keys() != {index for index, _trial in indexed}:
        missing = sorted({index for index, _trial in indexed} - stops.keys())
        raise RuntimeError(f"batch {batch_number} lacks observed TPR for {missing}")
    records: list[dict] = []
    for index, trial in indexed:
        trace_path = work / f"trace-{index:06d}.txt"
        dump_path = work / f"dump-{index:06d}.bin"
        if not trace_path.is_file() or not dump_path.is_file():
            raise RuntimeError(f"trial {index} lacks trace or dump")
        trace = parse_trace(trace_path)
        dump = dump_path.read_bytes()
        if len(dump) != ISO_SIZE:
            raise RuntimeError(f"trial {index} dump has {len(dump):#x} bytes")
        records.append(record_trial(index, trial, stops[index], trace, dump))
        for path in (
            work / f"local-{index:06d}.bin",
            work / f"iso-{index:06d}.bin",
            trace_path,
            dump_path,
        ):
            path.unlink(missing_ok=True)
    log_path.unlink(missing_ok=True)
    return records


def summary_for(records: list[dict]) -> dict:
    a = [record for record in records if record["experiment"] == "A-direct-merge"]
    a_merge = [record for record in a if record["family"] == "merge-zero"]
    a_specified = [record for record in a if record["family"] == "specified-one"]
    b = [record for record in records if record["experiment"] == "B-serialize-and-merge"]
    b_phase0 = [record for record in b if record["inputs"]["phase"] == 0]
    b_phase2 = [record for record in b if record["inputs"]["phase"] == 2]

    def output(record: dict) -> dict:
        return record["write_summary"]["output_at_and_after_b"]

    def excess(record: dict) -> int:
        return max(0, output(record)["unique_byte_count"] - int(record["inputs"].get(
            "capacity_in", OUTPUT_CAPACITY,
        )))

    null_by_n2: dict[str, list[list[str]]] = {}
    for n2 in sorted({int(record["inputs"]["n2"]) for record in a_merge}):
        candidates = [
            record for record in a_merge
            if record["inputs"]["ptr2"] == "null"
            and int(record["inputs"]["n2"]) == n2
            and int(record["inputs"]["n1"]) == 0
        ]
        runs = candidates[0]["read_summary"]["null_pointer_codeflash_source_runs"] if candidates else []
        null_by_n2[hex(n2)] = runs

    wrap = [
        record for record in a_merge
        if int(record["inputs"]["n1"]) == 0xFFFF
    ]
    return {
        "records": len(records),
        "experiment_a": {
            "records": len(a),
            "specified_status_one_records": len(a_specified),
            "specified_status_one_output_writes": sum(
                output(record)["unique_byte_count"] for record in a_specified
            ),
            "merge_status_zero_records": len(a_merge),
            "records_exceeding_0x300": sum(
                output(record)["exceeds_0x300"] for record in a_merge
            ),
            "maximum_unique_output_bytes": max(
                output(record)["unique_byte_count"] for record in a_merge
            ),
            "maximum_written_offset": hex(max(
                int(output(record)["max_offset"], 16)
                for record in a_merge if output(record)["max_offset"] is not None
            )),
            "n1_ffff_merge_records": len(wrap),
            "n1_ffff_loop_wrap_guard_records": sum(
                record["termination"] == "loop-wrap-guard" for record in wrap
            ),
            "n1_ffff_unique_output_bytes": sorted({
                output(record)["unique_byte_count"] for record in wrap
            }),
            "null_list2_codeflash_reads_by_n2": null_by_n2,
        },
        "experiment_b": {
            "records": len(b),
            "phase0_records": len(b_phase0),
            "phase2_records": len(b_phase2),
            "phase0_capacity_exceeding_records": sum(
                output(record)["exceeds_caller_capacity"] for record in b_phase0
            ),
            "phase2_capacity_exceeding_records": sum(
                output(record)["exceeds_caller_capacity"] for record in b_phase2
            ),
            "maximum_output_bytes": max(output(record)["unique_byte_count"] for record in b),
            "maximum_capacity_excess_bytes": max(excess(record) for record in b),
        },
    }


def probe(out: Path, timeout: float) -> dict:
    image = IMAGE.read_bytes()
    if hashlib.sha256(image).hexdigest() != IMAGE_SHA256:
        raise SystemExit("CodeFlash.bin sha256 mismatch")
    out.mkdir(parents=True, exist_ok=True)
    (out / "isolated-merge.json").unlink(missing_ok=True)
    for stale in out.glob("batch-*.txt"):
        stale.unlink()
    linked = out / "linked-image"
    linked.mkdir(exist_ok=True)
    for pattern in ("local-*.bin", "iso-*.bin", "trace-*.txt", "dump-*.bin"):
        for stale in linked.glob(pattern):
            stale.unlink()

    _output, elf = run(
        root=REPO_ROOT,
        image_path=IMAGE,
        entry=MERGE_ENTRY,
        stop=f"{SENTINEL:#x}",
        memory_regions=[RAM_REGION, ISO_REGION],
        gdb_commands=[
            *gdb_prelude(),
            f"set $r3={STACK_TOP:#x}",
            f"set $r31={SENTINEL:#x}",
            "set $r6=0",
            "set $r7=0",
            "set $r8=0",
            f"set $pc={MERGE_ENTRY:#x}",
            "continue",
        ],
        expected_output=["RH850_EXECUTION_VERIFIED"],
        timeout=timeout,
        output_dir=linked,
    )
    assert elf is not None

    trials = generate_trials(image)
    batches = make_batches(trials)
    records: list[dict] = []
    observed = 0
    for batch_number, indexed in enumerate(batches):
        batch_records = run_batch(elf, indexed, out, batch_number, timeout)
        records.extend(batch_records)
        observed += len(batch_records)
        print(f"simulated {observed}/{len(trials)}", flush=True)
    records.sort(key=lambda record: record["index"])
    if len(records) != len(trials) or {record["index"] for record in records} != set(range(len(trials))):
        raise SystemExit("not every generated matrix cell produced an observed record")

    result = {
        "schema": "camry-f33-ab-merge-isolated-probe-v1",
        "image": str(IMAGE.relative_to(REPO_ROOT)),
        "image_sha256": IMAGE_SHA256,
        "entries": {
            "merge": hex(MERGE_ENTRY),
            "serialize_and_merge": hex(SERIALIZE_ENTRY),
        },
        "environment": {
            "gp": hex(GP),
            "tp": hex(TP),
            "sp": hex(STACK_TOP),
            "return_sentinel": hex(SENTINEL),
            "local_ram": [hex(RAM_BASE), hex(RAM_BASE + RAM_SIZE - 1)],
            "isolated_ram": [hex(ISO_BASE), hex(ISO_BASE + ISO_SIZE - 1)],
            "output_b": hex(OUTPUT_B),
            "nominal_output_capacity": OUTPUT_CAPACITY,
            "pmr_thunk_sim_patches": ["0x6a45e", "0x6a4c4", "0x701c4", "0x70204"],
            "loop_wrap_guard": {
                "pc": hex(MERGE_LOOP_GUARD_PC),
                "ignored_hits": MERGE_LOOP_GUARD_IGNORE,
            },
        },
        "observed_contract": {
            "merge_descriptor": {
                "list": "u8 status @ +0, u16 byte_count @ +2, u32 data_pointer @ +4",
                "output": "u32 data_pointer @ +0, u32 length_pointer @ +4",
                "length_pointer_evidence": ["0x8dfea ld.w 4[r8],ep", "0x8dfee sst.h r1,0[ep]"],
            },
            "serialize_state": {
                "0xfebf45d4": "list1 accumulated byte count; read 0x8e0aa, stored into descriptor 0x8e16e",
                "0xfebf45d6": "staging bytes remaining; read 0x8e0ac",
                "0xfebf45d8": "list2 byte count; read 0x8e0b2, stored 0x8e176",
                "0xfebf45dc": "mode; value 1 selects merge at 0x8e170/0x8e182/0x8e184",
                "0xfebf45dd": "list1/serializer status; read 0x8e0a6, stored 0x8e164",
                "0xfebf45df": "list2 status; read 0x8e0b0, stored 0x8e174",
                "0xfebf45e1": "phase; read 0x8e096, compared at 0x8e0a8 and 0x8e104",
                "0xfebf45e4": "list1 staging pointer; formed 0x8e08a, stored 0x8e168",
                "list2_pointer": "hard-coded zero at 0x8e178",
                "r6": "copied to merge output pointer by 0x8e150 and 0x8e17c",
                "r7_pointee": "capacity input for serializer at 0x8e0ce..0x8e0da; length output at 0x8e1a2",
                "r8": "NRC output pointer retained at output descriptor +0xc",
            },
        },
        "matrix": {
            "required_n1": list(REQUIRED_N1),
            "required_n2": list(REQUIRED_N2),
            "odd_n1_additions": list(ODD_N1),
            "odd_n2_additions": list(ODD_N2),
            "generated_cells": len(trials),
            "observed_cells": len(records),
            "batches": len(batches),
        },
        "summary": summary_for(records),
        "records": records,
    }
    (out / "isolated-merge.json").write_text(json.dumps(result, indent=2) + "\n")
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--timeout", type=float, default=300.0)
    args = parser.parse_args()
    out = args.out.resolve()
    build_out = (REPO_ROOT / "build/out").resolve()
    if out == REPO_ROOT or not out.is_relative_to(build_out):
        raise SystemExit("probe outputs must live under build/out/")
    result = probe(out, args.timeout)
    print(json.dumps({
        "schema": result["schema"],
        "matrix": result["matrix"],
        "summary": result["summary"],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
