#!/usr/bin/env python3
"""Coverage-guided, stateful memory-safety campaign for exact Camry F33 DCM.

Unlike the fixed-matrix fuzzer, this driver keeps firmware state across request,
poll, cancel, timeout, completion, reset, and slot-reuse steps.  GNU sim tracing
is switched at GDB stops, so every case gets exact branch edges or memory
accesses without starting one simulator per input.  A failed batch is bisected;
it is never expanded into a linear retry of every member.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import random
import re
from collections.abc import Iterable, Sequence
from dataclasses import dataclass, replace
from pathlib import Path

from tools import REPO_ROOT
from tools.rh850_codeflash import CodeFlashSimError, run, run_elf
from tools.targets.camry.research import fuzz_camry_f33_dcm_handlers as dcm

SCHEMA = "camry-f33-stateful-coverage-fuzz-v1"
BRANCH_RE = re.compile(
    r"^branch:\s+\S+:\d+\s+(0x[0-9a-fA-F]+).*::\s+(0x[0-9a-fA-F]+)\s*$",
    re.MULTILINE,
)
STEP_RE = re.compile(r"^SEQSTEP ([0-9a-f]{16}) (\d+) (\d+)$", re.MULTILINE)
CORE_RE = re.compile(
    r"^(read|write)-(\d+) (exec|read|write):(0x[0-9a-fA-F]+) (?:->|<-) (0x[0-9a-fA-F]+)$"
)

CALLS: dict[str, tuple[int, tuple[tuple[str, int], ...]]] = {
    "poll": (0x916AC, ()),
    "cancel": (0x91E6E, ()),
    "timeout": (0x91D20, ()),
    "reset": (0x9887C, ()),
    "completion": (0x912BE, (("$r6", 0), ("$r7", 0))),
    "pending_completion": (0x912BE, (("$r6", 0), ("$r7", 1))),
}

# The proprietary-transport completion callback copies this saved message
# context back into DCM. Direct slot injection bypasses its ingress snapshot,
# so every injected request must supply the coherent context that real ingress
# would have installed. Leaving it pattern-filled creates an artificial
# uninitialized-context result for rejected proprietary services.
TRANSPORT_CONTEXT = 0xFEBE52BC
FULL_RESPONSE_CAPACITY = 0x300
STATEFUL_ENVELOPE = [
    *dcm.ENVELOPE,
    [TRANSPORT_CONTEXT, TRANSPORT_CONTEXT + 27],
]


@dataclass(frozen=True)
class Step:
    kind: str
    request: bytes = b""
    slot: int = 0
    response_poison: int | None = None
    request_tail_salt: int | None = None

    def as_dict(self) -> dict:
        row = {"kind": self.kind}
        if self.kind == "request":
            row.update({"request_hex": self.request.hex(), "slot": self.slot})
            if self.response_poison is not None:
                row["response_poison"] = self.response_poison
            if self.request_tail_salt is not None:
                row["request_tail_salt"] = self.request_tail_salt
        return row


@dataclass(frozen=True)
class Case:
    name: str
    session: int
    security_bitmap: int
    steps: tuple[Step, ...]

    def identity_payload(self) -> dict:
        return {
            "session": self.session,
            "security_bitmap": self.security_bitmap,
            "steps": [step.as_dict() for step in self.steps],
        }

    @property
    def case_id(self) -> str:
        encoded = json.dumps(
            self.identity_payload(), sort_keys=True, separators=(",", ":")
        ).encode()
        return hashlib.sha256(encoded).hexdigest()[:16]

    def as_dict(self) -> dict:
        return {"id": self.case_id, "name": self.name, **self.identity_payload()}


@dataclass
class CaseResult:
    case: Case
    step_pcs: list[int]
    edges: set[tuple[int, int]]
    dump: bytes | None
    initial: bytes
    trace_paths: list[Path]


@dataclass
class RunCollection:
    results: list[CaseResult]
    hangs: list[dict]


def request(
    data: bytes,
    slot: int = 0,
    response_poison: int | None = None,
    request_tail_salt: int | None = None,
) -> Step:
    if len(data) > 0x100:
        raise ValueError("DCM slot requests are capped at 0x100 bytes")
    if slot not in range(3):
        raise ValueError("DCM slot index must be 0..2")
    return Step("request", data, slot, response_poison, request_tail_salt)


def action(kind: str) -> Step:
    if kind != "tick" and kind not in CALLS:
        raise ValueError(f"unknown lifecycle action {kind}")
    return Step(kind)


def make_case(name: str, steps: Iterable[Step], session: int = 1,
              security_bitmap: int = 0) -> Case:
    materialized = tuple(steps)
    if not materialized:
        raise ValueError("stateful case must contain at least one step")
    return Case(name, session, security_bitmap, materialized)


def publication_dids() -> list[int]:
    return sorted({did for did, _length, _reader in dcm.publication_rows()})


def seed_cases() -> list[Case]:
    cases: list[Case] = []
    basic = (
        ("session_default", b"\x10\x01", 1),
        ("session_extended", b"\x10\x03", 1),
        ("ecu_reset", b"\x11\x01", 2),
        ("clear_dtc", b"\x14\xff\xff\xff", 1),
        ("dtc_count", b"\x19\x01\xff", 1),
        ("dtc_list", b"\x19\x02\xff", 1),
        ("dtc_snapshot", b"\x19\x04\x00\x00\x00\xff", 1),
        ("security_seed", b"\x27\x03" + bytes(16), 3),
        ("security_key", b"\x27\x04" + bytes(16), 3),
        ("communication_control", b"\x28\x01\x01", 3),
        ("request_download", b"\x34\x00", 2),
        ("transfer_data", b"\x36\x01\x00", 2),
        ("transfer_exit", b"\x37", 2),
        ("tester_present", b"\x3e\x00", 1),
        ("control_dtc", b"\x85\x01", 3),
        ("event_list", b"\xab\x01", 1),
        ("ba_unknown", b"\xba\x00", 3),
        ("unknown_sid", b"\xff\xa5\x5a", 1),
        ("empty_request", b"", 1),
    )
    for name, payload, session in basic:
        cases.append(make_case(name, [request(payload)], session))

    for did in publication_dids():
        cases.append(make_case(
            f"rdbi_{did:04x}", [request(bytes((0x22, did >> 8, did & 0xFF)))], 1,
        ))
    cases.append(make_case(
        "rdbi_segmented_multi",
        [request(b"\x22\x20\x30\xf1\x81\xf1\x8c\x10\x37")],
        1,
    ))
    cases.append(make_case(
        "rmba_ram_16",
        [request(b"\x23\x15\x01\xfe\xbe\x70\x00\x10")],
        3,
    ))

    for did in dcm.WDBI_DIDS:
        payload_length = 2 if did in (0x0204, 0x2013) else 1
        cases.append(make_case(
            f"wdbi_{did:04x}",
            [request(bytes((0x2E, did >> 8, did & 0xFF)) + b"\x5A" * payload_length)],
            3,
        ))
    routine_payloads = {0x1004: b"\xFF\xFF", 0x1010: bytes(64)}
    for rid in dcm.ROUTINE_RIDS:
        cases.append(make_case(
            f"routine_{rid:04x}",
            [request(
                bytes((0x31, 0x01, rid >> 8, rid & 0xFF))
                + routine_payloads.get(rid, b"")
            )],
            3,
        ))
    for selector, operation_data in (
        (0xF1, b"JTEKM"),
        (0xF3, b"TMPCL"),
        (0xF4, b"JTRM1"),
        (0xF5, b"JTRM2"),
        (0xF6, b"BADIS"),
        (0xF7, b"BAENA"),
        (0xF8, b"TZCLR"),
        (0xF9, b"JTRM3"),
        (0xFA, b"\x40VSPD"),
        (0xFB, b"ASINC"),
    ):
        cases.append(make_case(
            f"ba_{selector:02x}",
            [request(bytes((0xBA, selector)) + operation_data)],
            3,
            0xFFFFFFFF,
        ))

    # Exact lifecycle transitions.  These preserve all RAM between steps and
    # only perform the same slot admission writes that CanTp/DCM performs.
    cases.extend((
        make_case("short_session_request", (
            request(b"\x10", 0),
        ), 1),
        make_case("short_routine_1004_poll", (
            request(b"\x31\x01\x10\x04", 0), action("poll"),
        ), 1, 0xFFFFFFFF),
        make_case("ba_stale_token_reuse", (
            request(b"\xFF\x00BAENA", 0), request(b"\xBA\x00", 0),
            action("poll"), request(b"\xBA\x00", 0),
        ), 3),
        make_case("ba_stale_selector_token_reuse", (
            request(b"\xFF\xF7BAENA", 0), request(b"\xBA", 0),
            action("poll"), request(b"\xBA", 0),
        ), 3),
        make_case("pending_poll_cancel_reuse", (
            request(b"\x31\x01\x10\x0f", 0), action("poll"), action("cancel"),
            request(b"\x22\x20\x30", 0),
        ), 3),
        make_case("pending_completion_reuse", (
            request(b"\x31\x01\x10\x0f", 0), action("pending_completion"),
            action("completion"), request(b"\x22\xf1\x81", 0),
        ), 3),
        make_case("timeout_cancel_reuse", (
            request(b"\x31\x01\x10\x0f", 0), action("timeout"),
            request(b"\x19\x01\xff", 0),
        ), 3),
        make_case("reset_reuse", (
            request(b"\x2e\x20\x12\x01", 0), action("reset"),
            request(b"\x22\x20\x30", 0),
        ), 3),
        make_case("three_slot_interleave", (
            request(b"\x22\x20\x30", 0), request(b"\x31\x01\x10\x0f", 1),
            action("poll"), request(b"\x19\x02\xff", 2), action("cancel"),
            request(b"\x22\xf1\x81", 1),
        ), 3),
        make_case("session_security_sequence", (
            request(b"\x10\x03", 0), request(b"\x27\x03" + bytes(16), 1),
            request(b"\x27\x04" + bytes(16), 1), request(b"\x31\x01\x10\x0f", 2),
        ), 1),
        make_case("programming_null_transfer_sequence", (
            request(b"\x10\x02", 0), request(b"\x34\x00", 0),
            request(b"\x36\x01" + bytes(range(16)), 0), request(b"\x37", 0),
        ), 3),
        make_case("wdbi_poll_cancel", (
            request(b"\x2e\x20\x12\x01", 0), action("poll"), action("cancel"),
            request(b"\x2e\x20\x12\x00", 0),
        ), 3),
        make_case("scheduler_idle_reset", (
            request(b"\x22\x20\x30", 0), action("tick"), action("tick"),
            request(b"\x22\x20\x30", 0),
        ), 1),
    ))
    unique = {case.case_id: case for case in cases}
    return list(unique.values())

def truncated_request_cases() -> list[Case]:
    """Systematically exercise every distinct strict prefix of one-message seeds."""
    cases: dict[str, Case] = {}
    for seed in seed_cases():
        if len(seed.steps) != 1 or seed.steps[0].kind != "request":
            continue
        original = seed.steps[0]
        for length in range(len(original.request)):
            candidate = Case(
                f"truncated_{length}_{seed.name}",
                seed.session,
                seed.security_bitmap,
                (replace(original, request=original.request[:length]),),
            )
            cases[candidate.case_id] = candidate
    return list(cases.values())

def lifecycle_prefix_cases() -> list[Case]:
    """Pair every strict prefix with asynchronous and same-slot reuse steps."""
    cases: dict[str, Case] = {}
    for base in truncated_request_cases():
        step = base.steps[0]
        for action_name in ("poll", "cancel", "timeout", "completion", "pending_completion"):
            candidate = Case(
                f"{base.name}_{action_name}",
                base.session,
                base.security_bitmap,
                (step, action(action_name)),
            )
            cases[candidate.case_id] = candidate
        reused = Case(
            f"{base.name}_reuse",
            base.session,
            base.security_bitmap,
            (step, step),
        )
        cases[reused.case_id] = reused
    return list(cases.values())


def comparison_dictionary() -> tuple[bytes, ...]:
    tokens: set[bytes] = {
        bytes((value,)) for value in (
            0, 1, 2, 3, 4, 7, 8, 0x0F, 0x10, 0x11, 0x13, 0x20, 0x22,
            0x23, 0x27, 0x2E, 0x31, 0x34, 0x36, 0x37, 0x3E, 0x40, 0x5A,
            0x7F, 0x80, 0xA5, 0xFE, 0xFF,
        )
    }
    for value in (*dcm.WDBI_DIDS, *dcm.ROUTINE_RIDS, *publication_dids()):
        tokens.add(value.to_bytes(2, "big"))
        tokens.add(value.to_bytes(2, "little"))
    for value in (
        0, 1, 2, 7, 8, 0x10, 0x3F, 0x40, 0x43, 0x44, 0xFE, 0xFF,
        0x100, 0x101, 0xFFF, 0xFFFF, 0x10000,
    ):
        for width in (1, 2, 4):
            if value < 1 << (8 * width):
                tokens.add(value.to_bytes(width, "big"))
    for address in (
        0xFEBE0000, 0xFEBE37FF, 0xFEBE3800, 0xFEBE503B, 0xFEBE503C,
        0xFEBE52A7, 0xFEBE52A8, 0xFEBE7000, 0xFEBFFFFF, 0xFEC00000,
        0xFF200000, 0xFFFFFFFF,
    ):
        tokens.add(address.to_bytes(4, "big"))
        tokens.add(address.to_bytes(4, "little"))
    return tuple(sorted(tokens, key=lambda value: (len(value), value)))


def mutate(case: Case, rng: random.Random, serial: int) -> Case:
    steps = list(case.steps)
    request_indices = [index for index, step in enumerate(steps) if step.kind == "request"]
    operation = rng.randrange(8)
    if operation == 0 and len(steps) < 8:
        source = rng.choice(request_indices) if request_indices else 0
        steps.insert(rng.randrange(len(steps) + 1), steps[source])
    elif operation == 1 and len(steps) > 1:
        del steps[rng.randrange(len(steps))]
    elif operation == 2 and len(steps) > 1:
        left = rng.randrange(len(steps))
        right = rng.randrange(len(steps))
        steps[left], steps[right] = steps[right], steps[left]
    elif operation == 3:
        steps.insert(rng.randrange(len(steps) + 1), action(rng.choice(tuple(CALLS) + ("tick",))))
        steps = steps[:8]
    elif request_indices:
        index = rng.choice(request_indices)
        step = steps[index]
        payload = bytearray(step.request)
        if operation == 4 and payload:
            payload[rng.randrange(len(payload))] ^= 1 << rng.randrange(8)
        elif operation == 5:
            token = rng.choice(comparison_dictionary())
            position = rng.randrange(len(payload) + 1)
            payload[position:position] = token
        elif operation == 6 and payload:
            start = rng.randrange(len(payload))
            width = rng.randrange(1, min(8, len(payload) - start) + 1)
            del payload[start:start + width]
        else:
            token = rng.choice(comparison_dictionary())
            if not payload:
                payload.extend(token)
            else:
                position = rng.randrange(len(payload))
                payload[position:position + len(token)] = token
        del payload[0x100:]
        steps[index] = replace(
            step, request=bytes(payload), slot=rng.randrange(3) if rng.randrange(4) == 0 else step.slot,
        )
    return Case(
        f"mut_{serial:06d}_{case.name}",
        rng.choice((case.session, 1, 2, 3)),
        rng.choice((case.security_bitmap, 0, 1, 0xFFFFFFFF)),
        tuple(steps),
    )


def base_image(case: Case) -> bytes:
    primes = (
        dcm.session_primes(case.session, case.security_bitmap)
        + tuple((address, b"\x5A") for address in dcm.ADMISSION)
        + ((dcm.ADMISSION_CLEAR, b"\x00"),)
        + ((dcm.RMEM_SOURCE, bytes((0x40 + index) & 0xFF for index in range(0x100))),)
    )
    return dcm.trial_image(dcm.Trial(case.name, dcm.DISPATCH_TASK, (), primes), salt=0)


def lean_prelude() -> list[str]:
    return [
        f"set $r4={dcm.GP:#x}", f"set $r5={dcm.TP_BASE:#x}", f"set $tp={dcm.TP_BASE:#x}",
        "set {unsigned short}0x6a45e = 0x007f", "set {unsigned short}0x6a4c4 = 0x007f",
        "set {unsigned short}0x6a4c0 = 0x0000", "set {unsigned short}0x6a51e = 0x0000",
        "set {unsigned short}0x701c4 = 0x007f", "set {unsigned short}0x70204 = 0x007f",
        f"break *{dcm.SENTINEL:#x}",
        f"restore /out/{dcm.DCRA1_MODEL_NAME} binary {dcm.DCRA1_MODEL_ENTRY:#x}",
        "break *0x67060", "commands 2", "silent",
        f"set $pc={dcm.DCRA1_MODEL_ENTRY:#x}", "continue", "end",
        "set {unsigned short}0xFEBE40E4 = 0", "set $r6=0xFFFF", "set $r7=0xFEBE40E0",
        f"set $r3={dcm.STACK_TOP:#x}", f"set $r31={dcm.SENTINEL:#x}", "set $pc=0x7A57A",
        "continue",
    ]


def call_commands(case_id: str, step_index: int, entry: int,
                  registers: Sequence[tuple[str, int]] = ()) -> list[str]:
    commands = [
        f"set $r4={dcm.GP:#x}", f"set $r5={dcm.TP_BASE:#x}", f"set $tp={dcm.TP_BASE:#x}",
        f"set $r3={dcm.STACK_TOP:#x}", f"set $r31={dcm.SENTINEL:#x}",
    ]
    commands.extend(f"set {register}={value:#x}" for register, value in registers)
    commands.extend((
        f"set $pc={entry:#x}", "continue",
        f'printf "SEQSTEP {case_id} {step_index} %u\\n", $pc',
    ))
    return commands


def transport_context(step: Step) -> bytes:
    service_id = step.request[0] if step.request else 0
    return (
        dcm.SLOT_BUFFERS[step.slot].to_bytes(4, "little")
        + len(step.request).to_bytes(4, "little")
        + dcm.RESP_BUF.to_bytes(4, "little")
        + (0).to_bytes(4, "little")
        + bytes(4)
        + FULL_RESPONSE_CAPACITY.to_bytes(4, "little")
        + bytes((service_id, 0))
        + (2).to_bytes(2, "little")
    )


def request_tail_salt(case: Case, step_index: int, step: Step) -> int:
    if step.request_tail_salt is not None:
        return step.request_tail_salt
    digest = hashlib.sha256(
        bytes((case.session, step.slot))
        + case.security_bitmap.to_bytes(4, "little")
        + step_index.to_bytes(2, "little")
        + step.request
    ).digest()
    return int.from_bytes(digest[:4], "little")


def request_commands(
    case: Case,
    step_index: int,
    step: Step,
    work: Path,
    initialize_tail: bool,
) -> list[str]:
    slot_base = dcm.SLOT_BUFFERS[step.slot]
    request_name = f"state-{case.case_id}-{step_index:02d}-request.bin"
    commands: list[str] = []
    if initialize_tail or step.request_tail_salt is not None:
        payload = bytearray(dcm.pattern_image(request_tail_salt(case, step_index, step))[:0x100])
        payload[:len(step.request)] = step.request
    else:
        # Real CanTp reception overwrites only the declared bytes. Preserve the
        # previous message tail when a receive slot is reused.
        payload = bytearray(step.request)
    if payload:
        (work / request_name).write_bytes(payload)
        commands.append(f"restore /out/{request_name} binary {slot_base:#x}")
    if step.response_poison is not None:
        response_name = f"state-{case.case_id}-{step_index:02d}-response.bin"
        (work / response_name).write_bytes(dcm.response_poison(step.response_poison))
        commands.append(f"restore /out/{response_name} binary {dcm.RESP_BUF:#x}")
    context_name = f"state-{case.case_id}-{step_index:02d}-transport-context.bin"
    (work / context_name).write_bytes(transport_context(step))
    commands.append(f"restore /out/{context_name} binary {TRANSPORT_CONTEXT:#x}")
    row = dcm.SLOT_STATE + 0x10 * step.slot
    commands.extend((
        f"set {{unsigned int}}{row:#x} = {slot_base:#x}",
        f"set {{unsigned int}}{row + 4:#x} = {len(step.request)}",
        f"set {{unsigned short}}{row + 8:#x} = 0x100",
        f"set {{unsigned short}}{row + 0xA:#x} = 0",
        f"set {{unsigned char}}{dcm.REQUEST_PHASE:#x} = 2",
        f"set {{unsigned short}}{dcm.PENDING_SLOT:#x} = {step.slot}",
    ))
    commands.extend(call_commands(case.case_id, step_index, dcm.DISPATCH_TASK))
    return commands


def action_commands(case: Case, step_index: int, step: Step) -> list[str]:
    if step.kind == "tick":
        return [
            f"set {{unsigned char}}{dcm.REQUEST_PHASE:#x} = 0",
            *call_commands(case.case_id, step_index, dcm.DISPATCH_TASK),
        ]
    entry, registers = CALLS[step.kind]
    return call_commands(case.case_id, step_index, entry, registers)


def trace_name(case: Case, kind: str, step_index: int | None = None) -> str:
    suffix = "" if step_index is None else f"-{step_index:02d}"
    return f"trace-{kind}-{case.case_id}{suffix}.txt"


def group_script(cases: Sequence[Case], work: Path, trace_kind: str,
                 marker: str) -> tuple[list[str], dict[str, bytes], dict[str, list[Path]]]:
    commands = lean_prelude()
    initial: dict[str, bytes] = {}
    traces: dict[str, list[Path]] = {}
    per_step = trace_kind == "core"
    for case in cases:
        image = base_image(case)
        initial[case.case_id] = image
        image_name = f"state-{case.case_id}-initial.bin"
        (work / image_name).write_bytes(image)
        commands.append(f"restore /out/{image_name} binary {dcm.RAM_BASE:#x}")
        traces[case.case_id] = []
        initialized_slots: set[int] = set()
        if not per_step:
            name = trace_name(case, trace_kind)
            path = work / name
            path.unlink(missing_ok=True)
            traces[case.case_id].append(path)
            commands.extend((f"sim trace-file /out/{name}", f"sim trace-{trace_kind} on"))
        for step_index, step in enumerate(case.steps):
            if per_step:
                name = trace_name(case, trace_kind, step_index)
                path = work / name
                path.unlink(missing_ok=True)
                traces[case.case_id].append(path)
                commands.extend((f"sim trace-file /out/{name}", f"sim trace-{trace_kind} on"))
            if step.kind == "request":
                commands.extend(request_commands(
                    case, step_index, step, work, step.slot not in initialized_slots,
                ))
                initialized_slots.add(step.slot)
            else:
                commands.extend(action_commands(case, step_index, step))
            if per_step:
                commands.append(f"sim trace-{trace_kind} off")
        if not per_step:
            commands.append(f"sim trace-{trace_kind} off")
        commands.extend((
            (
                f"dump binary memory /out/state-{case.case_id}-dump.bin "
                f"{dcm.RAM_BASE:#x} {dcm.RAM_BASE + dcm.RAM_SIZE:#x}"
            ),
            f"set $pc={dcm.SENTINEL:#x}",
        ))
    commands.append(f'printf "{marker}\\n"')
    return commands, initial, traces


def parse_edges(paths: Sequence[Path]) -> set[tuple[int, int]]:
    edges: set[tuple[int, int]] = set()
    for path in paths:
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        for match in BRANCH_RE.finditer(text):
            source = int(match.group(1), 16)
            target = int(match.group(2), 16)
            if 0 <= source < 0x100000:
                edges.add((source, target))
    return edges


def remove_case_inputs(case: Case, work: Path, keep_traces: bool = False) -> None:
    for path in work.glob(f"state-{case.case_id}-*.bin"):
        if not path.name.endswith("-dump.bin"):
            path.unlink(missing_ok=True)
    if not keep_traces:
        for path in work.glob(f"trace-*-{case.case_id}*.txt"):
            path.unlink(missing_ok=True)


def run_group(elf: Path, cases: Sequence[Case], out: Path, trace_kind: str,
              timeout: float, label: str) -> list[CaseResult]:
    marker = "SEQBATCH_" + hashlib.sha256(
        "".join(case.case_id for case in cases).encode()
    ).hexdigest()[:16]
    commands, initial, traces = group_script(cases, elf.parent, trace_kind, marker)
    log_path = out / f"{label}.txt"
    output = run_elf(
        root=REPO_ROOT,
        elf_path=elf,
        stop=f"{dcm.SENTINEL:#x}",
        memory_regions=dcm.SIM_MEMORY_REGIONS,
        gdb_commands=commands,
        expected_output=[marker],
        timeout=timeout,
        output_path=log_path,
    )
    observed: dict[str, list[int]] = {case.case_id: [] for case in cases}
    for match in STEP_RE.finditer(output):
        if match.group(1) in observed:
            observed[match.group(1)].append(int(match.group(3)))
    results = []
    for case in cases:
        dump_path = elf.parent / f"state-{case.case_id}-dump.bin"
        dump = dump_path.read_bytes() if dump_path.is_file() else None
        if len(observed[case.case_id]) != len(case.steps) or dump is None or len(dump) != dcm.RAM_SIZE:
            raise CodeFlashSimError(
                f"case {case.case_id} incomplete: steps={len(observed[case.case_id])}/{len(case.steps)} "
                f"dump={0 if dump is None else len(dump):#x}"
            )
        results.append(CaseResult(
            case, observed[case.case_id], parse_edges(traces[case.case_id]),
            dump, initial[case.case_id], traces[case.case_id],
        ))
    log_path.unlink(missing_ok=True)
    return results


def run_cases(elf: Path, cases: Sequence[Case], out: Path, trace_kind: str,
              timeout: float, batch_size: int, label: str) -> RunCollection:
    results: list[CaseResult] = []
    hangs: list[dict] = []

    def isolated(group: Sequence[Case], group_label: str) -> None:
        try:
            results.extend(run_group(
                elf, group, out, trace_kind,
                min(timeout, 8.0) if len(group) == 1 else timeout,
                group_label,
            ))
        except (CodeFlashSimError, RuntimeError) as error:
            if len(group) > 1:
                midpoint = len(group) // 2
                isolated(group[:midpoint], group_label + "a")
                isolated(group[midpoint:], group_label + "b")
                return
            case = group[0]
            hangs.append({
                "id": case.case_id,
                "name": case.name,
                "classification": "isolated-timeout-or-incomplete-simulator-execution",
                "detail": str(error).splitlines()[-1][:240],
            })
            remove_case_inputs(case, elf.parent)

    for offset in range(0, len(cases), batch_size):
        isolated(cases[offset:offset + batch_size], f"{label}-{offset // batch_size:04d}")
    return RunCollection(results, hangs)


def retain_interesting(results: Sequence[CaseResult], known: set[tuple[int, int]],
                       corpus_dir: Path) -> tuple[list[tuple[Case, set[tuple[int, int]]]], int]:
    retained = []
    new_edge_count = 0
    for result in results:
        new = result.edges - known
        if new:
            known.update(new)
            new_edge_count += len(new)
            retained.append((result.case, result.edges))
            path = corpus_dir / f"{result.case.case_id}.json"
            path.write_text(json.dumps({
                **result.case.as_dict(),
                "edge_count": len(result.edges),
                "new_edge_count_at_discovery": len(new),
            }, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return retained, new_edge_count


def minimize_corpus(corpus: Sequence[tuple[Case, set[tuple[int, int]]]]) -> list[tuple[Case, set[tuple[int, int]]]]:
    uncovered = set().union(*(edges for _case, edges in corpus)) if corpus else set()
    remaining = list(corpus)
    selected = []
    while uncovered:
        best = max(
            remaining,
            key=lambda row: (
                len(row[1] & uncovered),
                -sum(len(step.request) for step in row[0].steps),
                -len(row[0].steps),
                row[0].case_id,
            ),
        )
        gain = best[1] & uncovered
        if not gain:
            break
        selected.append(best)
        uncovered.difference_update(gain)
        remaining.remove(best)
    return selected


def producer_templates() -> list[tuple[str, Case]]:
    return [
        ("negative_unknown", make_case("extent_negative_unknown", [request(b"\xff")], 1)),
        ("negative_short_rdbi", make_case("extent_negative_short_rdbi", [request(b"\x22")], 1)),
        ("wdbi", make_case("extent_wdbi", [request(b"\x2e\x20\x12\x01")], 3)),
        ("routine_start", make_case("extent_routine_start", [request(b"\x31\x01\x10\x0f")], 3)),
        ("routine_pending", make_case("extent_routine_pending", [
            request(b"\x31\x01\x10\x0f"), action("pending_completion"),
        ], 3)),
        ("dtc", make_case("extent_dtc", [request(b"\x19\x02\xff")], 1)),
        ("security_seed", make_case("extent_security_seed", [request(b"\x27\x03" + bytes(16))], 3)),
        ("security_key", make_case("extent_security_key", [request(b"\x27\x04" + bytes(16))], 3)),
        ("request_download", make_case("extent_request_download", [request(b"\x34\x00")], 2)),
        ("transfer_data", make_case("extent_transfer_data", [request(b"\x36\x01" + bytes(16))], 2)),
        ("transfer_exit", make_case("extent_transfer_exit", [request(b"\x37")], 2)),
        ("segmented_rdbi", make_case("extent_segmented_rdbi", [
            request(b"\x22\x20\x30\xf1\x81\xf1\x8c\x10\x37")
        ], 1)),
        ("read_memory", make_case("extent_read_memory", [
            request(b"\x23\x15\x01\xfe\xbe\x70\x00\x10")
        ], 3)),
        ("proprietary_event", make_case("extent_event", [request(b"\xab\x01")], 1)),
        ("proprietary_ba", make_case("extent_ba", [request(b"\xba\xf1" + bytes(62))], 3)),
    ]


def with_final_poison(case: Case, salt: int, label: str) -> Case:
    steps = list(case.steps)
    index = max(index for index, step in enumerate(steps) if step.kind == "request")
    steps[index] = replace(steps[index], response_poison=salt)
    return Case(f"{label}_{case.name}", case.session, case.security_bitmap, tuple(steps))


def response_observation(result: CaseResult, salt: int) -> dict:
    assert result.dump is not None
    context = dcm.ACTIVE_DCM_CONTEXT - dcm.RAM_BASE
    response = dcm.RESP_BUF - dcm.RAM_BASE
    length = int.from_bytes(result.dump[context + 12:context + 16], "little")
    capacity = int.from_bytes(result.dump[context + 20:context + 24], "little")
    poison = dcm.response_poison(salt)
    bounded = min(length, len(poison))
    unchanged = [
        offset for offset in range(bounded)
        if result.dump[response + offset] == poison[offset]
    ]
    return {
        "response_length": length,
        "response_capacity": capacity,
        "prefix": result.dump[response:response + min(length, 16)].hex(),
        "unchanged_offsets": unchanged,
        "step_pcs": [hex(pc) for pc in result.step_pcs],
    }


def audit_producer_extents(elf: Path, out: Path, timeout: float,
                           batch_size: int) -> dict:
    templates = producer_templates()
    salts = (0xA11CE, 0xB22DF)
    cases: list[Case] = []
    metadata: dict[str, tuple[str, int]] = {}
    for label, case in templates:
        for pass_index, salt in enumerate(salts):
            poisoned = with_final_poison(case, salt, f"extent{pass_index}")
            cases.append(poisoned)
            metadata[poisoned.case_id] = (label, salt)
    collection = run_cases(elf, cases, out, "branch", timeout, batch_size, "extent")
    observations: dict[str, dict[int, dict]] = {}
    for result in collection.results:
        label, salt = metadata[result.case.case_id]
        observations.setdefault(label, {})[salt] = response_observation(result, salt)
        (elf.parent / f"state-{result.case.case_id}-dump.bin").unlink(missing_ok=True)
        remove_case_inputs(result.case, elf.parent)
    findings = []
    records = []
    for label, _case in templates:
        pair = observations.get(label, {})
        if len(pair) != 2:
            continue
        first, second = (pair[salt] for salt in salts)
        common = sorted(set(first["unchanged_offsets"]) & set(second["unchanged_offsets"]))
        behavior_changed = (
            first["response_length"], first["response_capacity"], first["prefix"]
        ) != (
            second["response_length"], second["response_capacity"], second["prefix"]
        )
        record = {
            "family": label,
            "first": first,
            "second": second,
            "common_unwritten_offsets": common,
            "poison_changed_behavior": behavior_changed,
        }
        records.append(record)
        if (common or behavior_changed
                or first["response_length"] > FULL_RESPONSE_CAPACITY
                or second["response_length"] > FULL_RESPONSE_CAPACITY):
            findings.append(record)
    return {
        "schema": "camry-f33-multiservice-response-extent-v1",
        "families": len(templates),
        "trials": len(cases),
        "records": records,
        "findings": findings,
        "hangs": collection.hangs,
    }


def differing_runs(
    left: bytes,
    right: bytes,
    ignored: Sequence[tuple[int, int]],
) -> list[dict]:
    if len(left) != dcm.RAM_SIZE or len(right) != dcm.RAM_SIZE:
        raise ValueError("state divergence inputs must cover the full RAM window")
    runs: list[dict] = []
    start: int | None = None
    for offset, (first, second) in enumerate(zip(left, right)):
        address = dcm.RAM_BASE + offset
        different = first != second and not any(lo <= address <= hi for lo, hi in ignored)
        if different and start is None:
            start = address
        elif not different and start is not None:
            runs.append({"start": hex(start), "end": hex(address - 1)})
            start = None
    if start is not None:
        runs.append({"start": hex(start), "end": hex(dcm.RAM_BASE + dcm.RAM_SIZE - 1)})
    return runs


def audit_request_tail_divergence(
    elf: Path,
    out: Path,
    timeout: float,
    batch_size: int,
    bases: Sequence[Case] | None = None,
) -> dict:
    base_cases = list(truncated_request_cases() if bases is None else bases)
    salts = (0x13579, 0x2468A)
    cases: list[Case] = []
    metadata: dict[str, tuple[str, int]] = {}
    for base in base_cases:
        if len(base.steps) != 1 or base.steps[0].kind != "request":
            raise ValueError("request-tail divergence requires one-request cases")
        for pass_index, salt in enumerate(salts):
            step = replace(base.steps[0], request_tail_salt=salt)
            candidate = Case(
                f"tail{pass_index}_{base.name}",
                base.session,
                base.security_bitmap,
                (step,),
            )
            cases.append(candidate)
            metadata[candidate.case_id] = (base.case_id, salt)
    collection = run_cases(
        elf, cases, out, "branch", timeout, batch_size, "tail-divergence",
    )
    observed: dict[str, dict[int, CaseResult]] = {}
    for result in collection.results:
        base_id, salt = metadata[result.case.case_id]
        observed.setdefault(base_id, {})[salt] = result

    records = []
    findings = []
    for base in base_cases:
        pair = observed.get(base.case_id, {})
        if len(pair) != 2:
            continue
        first, second = (pair[salt] for salt in salts)
        assert first.dump is not None and second.dump is not None
        step = base.steps[0]
        tail_start = dcm.SLOT_BUFFERS[step.slot] + len(step.request)
        ignored = (
            (tail_start, dcm.SLOT_BUFFERS[step.slot] + 0xFF),
            *dcm.DIVERGENCE_DEAD_RANGES,
        )
        post_state_runs = differing_runs(first.dump, second.dump, ignored)
        edge_difference = first.edges ^ second.edges
        record = {
            "id": base.case_id,
            "name": base.name,
            "request_hex": step.request.hex(),
            "request_length": len(step.request),
            "branch_edge_difference_count": len(edge_difference),
            "branch_edge_difference_sample": [
                f"{source:#x}->{target:#x}"
                for source, target in sorted(edge_difference)[:32]
            ],
            "persistent_post_state_difference_runs": post_state_runs,
            "step_pcs": [
                [hex(pc) for pc in first.step_pcs],
                [hex(pc) for pc in second.step_pcs],
            ],
        }
        records.append(record)
        if edge_difference or post_state_runs or first.step_pcs != second.step_pcs:
            findings.append(record)
    for result in collection.results:
        (elf.parent / f"state-{result.case.case_id}-dump.bin").unlink(missing_ok=True)
        remove_case_inputs(result.case, elf.parent)
    return {
        "schema": "camry-f33-request-tail-divergence-v1",
        "base_cases": len(base_cases),
        "trials": len(cases),
        "records": records,
        "findings": findings,
        "hangs": collection.hangs,
    }


def spans(address: int, width: int, start: int, end: int) -> bool:
    return address < end and start < address + width


def parse_core_accesses(path: Path) -> list[dict]:
    accesses = []
    pc: int | None = None
    if not path.is_file():
        return accesses
    with path.open(encoding="utf-8", errors="replace") as stream:
        for raw in stream:
            match = CORE_RE.match(raw.rstrip())
            if match is None:
                continue
            operation, width_text, space, address_text, value_text = match.groups()
            address = int(address_text, 16)
            if space == "exec":
                pc = address
                continue
            accesses.append({
                "operation": operation,
                "width": int(width_text),
                "address": address,
                "value": int(value_text, 16),
                "pc": pc,
            })
    return accesses


def memory_access_findings(result: CaseResult) -> list[dict]:
    findings: list[dict] = []
    declared_lengths: dict[int, int] = {}
    defined_response: set[int] = set()
    response_start = dcm.RESP_BUF
    response_end = response_start + FULL_RESPONSE_CAPACITY
    for step_index, (step, path) in enumerate(zip(result.case.steps, result.trace_paths)):
        accesses = parse_core_accesses(path)
        if step.kind == "request":
            defined_response.clear()
        for access in accesses:
            address, width = access["address"], access["width"]
            pc = None if access["pc"] is None else hex(access["pc"])
            if access["operation"] == "read" and spans(
                address, width, response_start, response_end
            ):
                first = max(address, response_start)
                last = min(address + width, response_end)
                undefined = [
                    byte - response_start
                    for byte in range(first, last)
                    if byte not in defined_response
                ]
                if undefined:
                    findings.append({
                        "classification": "response-read-before-step-write-definedness-candidate",
                        "step": step_index,
                        "pc": pc,
                        "address": hex(address),
                        "width": width,
                        "undefined_offsets": undefined,
                    })
            if access["operation"] == "write":
                first = max(address, response_start)
                last = min(address + width, response_end)
                defined_response.update(range(first, last))
                if response_start <= address < response_end < address + width:
                    findings.append({
                        "classification": "response-object-right-boundary-crossing",
                        "step": step_index,
                        "pc": pc,
                        "address": hex(address),
                        "width": width,
                    })

            if step.kind == "request":
                slot_start = dcm.SLOT_BUFFERS[step.slot]
                slot_end = slot_start + 0x100
                logical_end = slot_start + len(step.request)
                if access["operation"] == "read" and spans(
                    address, width, logical_end, slot_end
                ):
                    findings.append({
                        "classification": "request-read-beyond-declared-length",
                        "step": step_index,
                        "request_length": len(step.request),
                        "slot": step.slot,
                        "pc": pc,
                        "address": hex(address),
                        "width": width,
                    })
                if spans(address, width, slot_start, slot_end) and not (
                    slot_start <= address and address + width <= slot_end
                ):
                    findings.append({
                        "classification": "slot-object-boundary-crossing",
                        "step": step_index,
                        "operation": access["operation"],
                        "pc": pc,
                        "address": hex(address),
                        "width": width,
                    })
            elif access["operation"] == "read":
                for slot, declared_length in declared_lengths.items():
                    start = dcm.SLOT_BUFFERS[slot]
                    logical_end = start + declared_length
                    if spans(address, width, logical_end, start + 0x100):
                        findings.append({
                            "classification": "retained-request-read-beyond-declared-length",
                            "step": step_index,
                            "action": step.kind,
                            "slot": slot,
                            "request_length": declared_length,
                            "pc": pc,
                            "address": hex(address),
                            "width": width,
                        })
        if step.kind == "request":
            declared_lengths[step.slot] = len(step.request)
    unique = {json.dumps(row, sort_keys=True): row for row in findings}
    return list(unique.values())


def audit_memory_accesses(elf: Path, corpus: Sequence[Case], out: Path,
                          timeout: float) -> dict:
    collection = run_cases(elf, corpus, out, "core", timeout, 8, "core")
    records = []
    for result in collection.results:
        findings = memory_access_findings(result)
        outside = [] if result.dump is None else [
            {"start": hex(start), "end": hex(end)}
            for start, end in dcm.outside_runs(
                result.dump, result.initial, STATEFUL_ENVELOPE
            )
        ]
        if findings or outside or any(pc != dcm.SENTINEL for pc in result.step_pcs):
            records.append({
                "id": result.case.case_id,
                "name": result.case.name,
                "step_pcs": [hex(pc) for pc in result.step_pcs],
                "access_candidates": findings,
                "persistent_outside_envelope_runs": outside,
            })
        (elf.parent / f"state-{result.case.case_id}-dump.bin").unlink(missing_ok=True)
        remove_case_inputs(result.case, elf.parent)
    return {
        "schema": "camry-f33-simulator-memory-access-audit-v1",
        "cases": len(corpus),
        "records": records,
        "hangs": collection.hangs,
    }

def audit_network_short_requests(elf: Path, out: Path, timeout: float) -> dict:
    """Drive malformed short requests through exact CanTp ingress and DCM."""
    from tools.targets.camry.research import fuzz_camry_f33_cantp_ingress as cantp

    specs = (
        (
            "zero_length",
            cantp.Frame(0x804, 8, bytes(8)),
            1,
            0,
            (),
        ),
        (
            "one_byte_session",
            cantp.sf(0x804, 1, b"\x10"),
            1,
            1,
            (),
        ),
        (
            "short_routine_1004",
            cantp.sf(0x804, 4, b"\x31\x01\x10\x04"),
            1,
            0xFFFFFFFF,
            ("poll",),
        ),
    )
    records = []
    target_pcs = {0x91078, 0x9758A, 0x9758C}
    for name, frame, session, security_bitmap, actions in specs:
        trial = cantp.Trial(name, (frame,))
        image = bytearray(cantp.trial_image(trial, 0))

        for address, data in (
            *dcm.session_primes(session, security_bitmap),
            *((address, b"\x5A") for address in dcm.ADMISSION),
            (dcm.ADMISSION_CLEAR, b"\x00"),
        ):
            offset = address - dcm.RAM_BASE
            image[offset:offset + len(data)] = data

        image_name = f"network-short-{name}.bin"
        (elf.parent / image_name).write_bytes(image)
        trace_name_value = f"network-short-{name}-core.txt"
        trace_path = elf.parent / trace_name_value
        trace_path.unlink(missing_ok=True)
        case_id = hashlib.sha256(name.encode()).hexdigest()[:16]
        commands = [
            *lean_prelude(),
            f"restore /out/{image_name} binary {dcm.RAM_BASE:#x}",
            f"sim trace-file /out/{trace_name_value}",
            "sim trace-core on",
            *call_commands(
                case_id,
                0,
                cantp.ENTRY,
                (("$r6", frame.canif_id), ("$r7", cantp.PDU_INFO)),
            ),
            (
                f'printf "NETRX {name} %u %u\\n", '
                f"*(unsigned char*){dcm.REQUEST_PHASE:#x}, "
                f"*(unsigned short*){dcm.SLOT_STATE + 4:#x}"
            ),
        ]
        step_index = 1
        if frame.data[0] & 0xF:
            commands.extend(call_commands(case_id, step_index, dcm.DISPATCH_TASK))
            step_index += 1
            for action_name in actions:
                entry, registers = CALLS[action_name]
                commands.extend(call_commands(
                    case_id, step_index, entry, registers,
                ))
                step_index += 1
        commands.append("sim trace-core off")
        marker = f"SEQSTEP {case_id} {step_index - 1} {dcm.SENTINEL}"
        output = run_elf(
            root=REPO_ROOT,
            elf_path=elf,
            stop=f"{dcm.SENTINEL:#x}",
            memory_regions=dcm.SIM_MEMORY_REGIONS,
            gdb_commands=commands,
            expected_output=[marker],
            timeout=timeout,
            output_path=out / f"network-short-{name}.txt",
        )
        received = re.search(rf"^NETRX {name} (\d+) (\d+)$", output, re.MULTILINE)
        if received is None:
            raise CodeFlashSimError(f"missing network receive state for {name}")
        reads = [
            {
                "pc": hex(access["pc"]),
                "address": hex(access["address"]),
                "width": access["width"],
                "value": hex(access["value"]),
            }
            for access in parse_core_accesses(trace_path)
            if access["operation"] == "read" and access["pc"] in target_pcs
        ]
        records.append({
            "name": name,
            "canif_id": hex(frame.canif_id),
            "isotp_frame": frame.data.hex(),
            "request_phase_after_receive": int(received.group(1)),
            "declared_request_length_after_receive": int(received.group(2)),
            "overread_events": reads,
        })
        (elf.parent / image_name).unlink(missing_ok=True)
    return {
        "schema": "camry-f33-network-short-request-audit-v1",
        "records": records,
        "findings": [record for record in records if record["overread_events"]],
    }


def prepare_elf(out: Path, timeout: float) -> tuple[Path, dict]:
    sim_out = out / "linked-image"
    sim_out.mkdir(parents=True, exist_ok=True)
    _output, elf = run(
        root=REPO_ROOT,
        image_path=dcm.IMAGE,
        entry=0x7A57A,
        stop=f"{dcm.SENTINEL:#x}",
        memory_regions=dcm.SIM_MEMORY_REGIONS,
        gdb_commands=(
            f"set $r4={dcm.GP:#x}", f"set $r3={dcm.STACK_TOP:#x}",
            f"set $r31={dcm.SENTINEL:#x}", f"set $tp={dcm.TP_BASE:#x}",
            f"set $r5={dcm.TP_BASE:#x}", "set $r7=0",
            f"break *{dcm.SENTINEL:#x}", "continue",
        ),
        expected_output=("RH850_EXECUTION_VERIFIED",),
        timeout=timeout,
        output_dir=sim_out,
    )
    assert elf is not None
    dcm.build_dcra1_model(sim_out)
    model = dcm.verify_dcra1_model(elf, timeout)
    dcm._LIFECYCLE_BASES.clear()
    dcm.prepare_pattern_lifecycle(elf, out, 0, timeout)
    return elf, model


def campaign(out: Path, seed: int, generations: int, mutations: int,
             plateau_limit: int, batch_size: int, timeout: float) -> dict:
    out.mkdir(parents=True, exist_ok=True)
    corpus_dir = out / "corpus" / "interesting"
    corpus_dir.mkdir(parents=True, exist_ok=True)
    for pattern in ("*.txt", "summary.json"):
        for path in out.glob(pattern):
            path.unlink()
    for path in corpus_dir.glob("*.json"):
        path.unlink()

    elf, dcra1_model = prepare_elf(out, timeout)
    producer_extent = audit_producer_extents(elf, out, timeout, batch_size)
    network_short_requests = audit_network_short_requests(elf, out, timeout)
    request_tail_divergence = audit_request_tail_divergence(
        elf, out, timeout, batch_size,
    )

    rng = random.Random(seed)
    known_edges: set[tuple[int, int]] = set()
    corpus: list[tuple[Case, set[tuple[int, int]]]] = []
    hangs: list[dict] = []
    abnormal: list[dict] = []
    generation_rows = []

    pending = seed_cases()
    seen_ids = {case.case_id for case in pending}
    plateau = 0
    for generation in range(generations + 1):
        if generation:
            source = [case for case, _edges in corpus] or seed_cases()
            pending = []
            attempts = 0
            while len(pending) < mutations and attempts < mutations * 20:
                attempts += 1
                candidate = mutate(rng.choice(source), rng, generation * 1_000_000 + attempts)
                if candidate.case_id in seen_ids:
                    continue
                seen_ids.add(candidate.case_id)
                pending.append(candidate)
        collection = run_cases(
            elf, pending, out, "branch", timeout, batch_size, f"coverage-g{generation:02d}",
        )
        hangs.extend(collection.hangs)
        for result in collection.results:
            bad = [
                {"step": index, "pc": hex(pc), "kind": result.case.steps[index].kind}
                for index, pc in enumerate(result.step_pcs) if pc != dcm.SENTINEL
            ]
            outside = [] if result.dump is None else dcm.outside_runs(
                result.dump, result.initial, STATEFUL_ENVELOPE
            )
            if bad or outside:
                abnormal.append({
                    "id": result.case.case_id,
                    "name": result.case.name,
                    "abnormal_steps": bad,
                    "persistent_outside_envelope_runs": [
                        {"start": hex(start), "end": hex(end)} for start, end in outside
                    ],
                })
            (elf.parent / f"state-{result.case.case_id}-dump.bin").unlink(missing_ok=True)
            remove_case_inputs(result.case, elf.parent)
        retained, new_edges = retain_interesting(collection.results, known_edges, corpus_dir)
        corpus.extend(retained)
        plateau = plateau + 1 if new_edges == 0 else 0
        generation_rows.append({
            "generation": generation,
            "executed": len(collection.results),
            "isolated_hangs": len(collection.hangs),
            "retained": len(retained),
            "new_edges": new_edges,
            "total_edges": len(known_edges),
            "plateau_generations": plateau,
        })
        if generation and plateau >= plateau_limit:
            break

    minimized = minimize_corpus(corpus)
    minimized_path = out / "corpus" / "minimized.jsonl"
    minimized_path.write_text("".join(
        json.dumps({**case.as_dict(), "edge_count": len(edges)}, sort_keys=True) + "\n"
        for case, edges in minimized
    ), encoding="utf-8")
    audit_cases = {
        case.case_id: case
        for case in (
            *(case for case, _edges in minimized),
            *truncated_request_cases(),
            *lifecycle_prefix_cases(),
        )
    }
    memory_access = audit_memory_accesses(
        elf, list(audit_cases.values()), out, timeout,
    )
    summary = {
        "schema": SCHEMA,
        "target": {
            "name": "camry-8965F3307000",
            "codeflash_sha256": dcm.IMAGE_SHA256,
        },
        "seed": seed,
        "comparison_dictionary_tokens": len(comparison_dictionary()),
        "seed_cases": len(seed_cases()),
        "executed_cases": sum(row["executed"] for row in generation_rows),
        "branch_edges": len(known_edges),
        "truncated_request_cases": len(truncated_request_cases()),
        "lifecycle_prefix_cases": len(lifecycle_prefix_cases()),
        "memory_audit_cases": len(audit_cases),
        "interesting_cases": len(corpus),
        "minimized_cases": len(minimized),
        "generation_progress": generation_rows,
        "coverage_plateau_reached": bool(generation_rows and generation_rows[-1]["plateau_generations"] >= plateau_limit),
        "isolated_hangs": hangs,
        "abnormal_or_outside_envelope": abnormal,
        "producer_extent": producer_extent,
        "network_short_requests": network_short_requests,
        "request_tail_divergence": request_tail_divergence,
        "memory_access": memory_access,
        "dcra1_model": dcra1_model,
    }
    (out / "summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed", type=int, default=0x5AFE)
    parser.add_argument("--generations", type=int, default=8)
    parser.add_argument("--mutations", type=int, default=96)
    parser.add_argument("--plateau", type=int, default=3)
    parser.add_argument("--batch-size", type=int, default=32)
    parser.add_argument("--timeout", type=float, default=60.0)
    parser.add_argument(
        "--out", type=Path,
        default=REPO_ROOT / "build/out/targets/camry-8965F3307000/stateful-coverage-fuzz",
    )
    args = parser.parse_args()
    if not args.out.resolve().is_relative_to(REPO_ROOT / "build/out"):
        raise SystemExit("fuzz outputs must live under build/out/")
    if min(args.generations, args.mutations, args.plateau, args.batch_size) <= 0:
        raise SystemExit("generation, mutation, plateau, and batch values must be positive")
    result = campaign(
        args.out, args.seed, args.generations, args.mutations,
        args.plateau, args.batch_size, args.timeout,
    )
    print(json.dumps({
        key: value for key, value in result.items()
        if key not in (
            "producer_extent", "network_short_requests",
            "request_tail_divergence", "memory_access", "isolated_hangs",
            "abnormal_or_outside_envelope",
        )
    }, indent=2, sort_keys=True))
    confirmed = (
        result["isolated_hangs"]
        or result["abnormal_or_outside_envelope"]
        or result["producer_extent"]["findings"]
        or result["producer_extent"]["hangs"]
        or result["network_short_requests"]["findings"]
        or result["request_tail_divergence"]["findings"]
        or result["request_tail_divergence"]["hangs"]
        or result["memory_access"]["records"]
        or result["memory_access"]["hangs"]
    )
    return 1 if confirmed else 0


if __name__ == "__main__":
    raise SystemExit(main())
