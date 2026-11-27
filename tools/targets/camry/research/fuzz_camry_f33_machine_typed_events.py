#!/usr/bin/env python3
"""Coverage-guided typed-event fuzzing through the exact Camry P1M-E machine."""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import random
import shutil
import time
from bisect import bisect_right
from collections import Counter, defaultdict, deque
from collections.abc import Iterable, Sequence
from dataclasses import dataclass, replace
from itertools import pairwise
from pathlib import Path
from typing import Any

from tools import REPO_ROOT
from tools.emulation import p1me_machine
from tools.emulation.p1me_machine import capture_many
from tools.firmware.rh850_instructions import is_jarl22, jarl22_target
from tools.targets.camry.analysis.convert_camry_capture_machine_events import (
    decode_firmware_rules,
)
from tools.targets.camry.research import explore_camry_f33_cantp_preemption as ingress
from tools.targets.camry.research import (
    explore_camry_f33_tx_confirmation_preemption as tx_preemption,
)
from tools.targets.camry.research import fuzz_camry_f33_stateful_coverage as stateful
from tools.targets.camry.research import replay_camry_f33_capture_machine as capture_replay

TARGET = "camry-8965F3307000"
SCHEMA = "camry-f33-machine-typed-event-fuzz-v1"
DEFAULT_OUT = REPO_ROOT / "build/out/targets/camry-8965F3307000/typed-event-fuzz"
COMPARE_BENCHMARK_TARGET = 0x8B872
COMPARE_BENCHMARK_SEED = 20261124
SYMBOLS = REPO_ROOT / "decomp/camry-8965F3307000/symbols.jsonl"
IMAGE = REPO_ROOT / "firmware/camry-8965F3307000/CodeFlash.bin"
IMAGE_SHA256 = "42dce8efc42f6ae31718e7713fa2d26bb9191b4a82439778aee4d7afded9b0e7"
ROUTINE_COMPARE_FIXTURE = (
    REPO_ROOT
    / "tests/fixtures/rh850/machine/camry-8965F3307000"
    / "camry_f33_rc_consequence_1004_valid_length_control.json"
)

CAN_SOURCE = "can-rx:channel1"
TIMER_SOURCE = "timer:tauj0"
INTERRUPT_SOURCE = "interrupt:offsets"
TX_SOURCE = "can-tx-complete:channel1"
SOURCES = (CAN_SOURCE, TIMER_SOURCE, INTERRUPT_SOURCE, TX_SOURCE)
TX_CHECKPOINT_INSTRUCTIONS = 10_000
TRACE_BATCH_LIMIT = 4
TX_SAFE_COMPLETION_OFFSET = 26_180
TAUJ0_TIMER_SKEW_P_BUS_CYCLES = 1
SEGMENTED_FLOW_CONTROL_COMPLETE_OFFSET = 417_731
SEGMENTED_CONSECUTIVE_OFFSET = 424_000
SECURITY_KEY_STATE_ADDRESS = 0xFEBE5D50
SECURITY_KEY_STATE = bytes.fromhex(
    "02010001020000005356befe00000000225abefe0400000000000000fe020000"
    "10000200230000000400010081f10000010000005256befe02000000215abefe"
    "2300000000000000ff0200002200020000000000000000000000000000000000"
    "0000000000000000000000000000000000000000000000000000000001020100"
    "000000005356befe10000000225abefe1000000000000000fe02000027000200"
)
SUBFUNCTION_SERVICES = frozenset((0x10, 0x11, 0x19, 0x27, 0x28, 0x31, 0x3E, 0x85, 0xAB, 0xBA))
SERVICE_TOKENS = (0x10, 0x11, 0x19, 0x22, 0x23, 0x27, 0x28, 0x2E, 0x31, 0x34, 0x36, 0x37, 0x3E, 0x85, 0xAB, 0xBA)
SUBFUNCTION_TOKENS = (0, 1, 2, 3, 4, 0x7F, 0x80, 0xFF)
MUTATION_CLASSES = (
    "identifier-coherent", "service-substitute", "subfunction-substitute",
    "record-substitute", "integrity-break", "length-coherent", "length-broken",
)


@dataclass(frozen=True)
class TypedEvent:
    kind: str
    offset: int
    fields: tuple[tuple[str, Any], ...]
    mutation_class: str = "seed"

    @classmethod
    def make(cls, kind: str, offset: int, mutation_class: str = "seed", **fields: Any) -> TypedEvent:
        return cls(kind, offset, tuple(sorted(fields.items())), mutation_class)

    def values(self) -> dict[str, Any]:
        return dict(self.fields)

    def as_dict(self) -> dict[str, Any]:
        return {"kind": self.kind, "offset": self.offset, "mutation_class": self.mutation_class, **self.values()}


@dataclass(frozen=True)
class EventStream:
    source: str
    events: tuple[TypedEvent, ...]

    def as_dict(self) -> dict[str, Any]:
        return {"source": self.source, "events": [event.as_dict() for event in self.events]}


@dataclass(frozen=True)
class MachineCase:
    name: str
    streams: tuple[EventStream, ...]
    lifecycle_case_id: str | None = None
    lifecycle_disposition: str | None = None
    parent_id: str | None = None
    mutated_source: str | None = None
    mutation_class: str = "seed"
    session: int | None = None
    security_bitmap: int = 0
    memory_primes: tuple[tuple[int, bytes], ...] = ()
    foreground_cycles: int = 2
    expected_response: bytes | None = None

    def stream(self, source: str) -> EventStream:
        return next(stream for stream in self.streams if stream.source == source)

    @property
    def case_id(self) -> str:
        encoded = json.dumps({
            "streams": [stream.as_dict() for stream in self.streams],
            "session": self.session,
            "security_bitmap": self.security_bitmap,
            "memory_primes": [
                [address, value.hex()] for address, value in self.memory_primes
            ],
            "foreground_cycles": self.foreground_cycles,
            "expected_response": (
                self.expected_response.hex() if self.expected_response is not None else None
            ),
        }, sort_keys=True, separators=(",", ":")).encode()
        return hashlib.sha256(encoded).hexdigest()[:16]

    def as_dict(self) -> dict[str, Any]:
        return {
            "id": self.case_id, "name": self.name, "parent_id": self.parent_id,
            "mutated_source": self.mutated_source, "mutation_class": self.mutation_class,
            "lifecycle_case_id": self.lifecycle_case_id,
            "lifecycle_disposition": self.lifecycle_disposition,
            "session": self.session,
            "security_bitmap": self.security_bitmap,
            "memory_primes": [
                {"address": hex(address), "data_hex": value.hex()}
                for address, value in self.memory_primes
            ],
            "foreground_cycles": self.foreground_cycles,
            "expected_response": (
                self.expected_response.hex() if self.expected_response is not None else None
            ),
            "streams": [stream.as_dict() for stream in self.streams],
        }


@dataclass(frozen=True)
class Feedback:
    edges: frozenset[tuple[int, int]]
    event_kinds: frozenset[str]
    compare_tokens: tuple[bytes, ...]
    table_indices: tuple[int, ...]
    reached_pcs: frozenset[int]


def canonical_streams(events: dict[str, Iterable[TypedEvent]]) -> tuple[EventStream, ...]:
    return tuple(EventStream(source, tuple(events.get(source, ()))) for source in SOURCES)


def uds_event(payload: bytes, offset: int = 0, can_id: int = 0x7A1,
              mutation_class: str = "seed", break_kind: str = "none") -> TypedEvent:
    service = payload[0] if payload else None
    subfunction = payload[1] if len(payload) > 1 and service in SUBFUNCTION_SERVICES else None
    record_offset = 2 if subfunction is not None else min(1, len(payload))
    return TypedEvent.make(
        "uds-request", offset, mutation_class, can_id=can_id,
        service=service, subfunction=subfunction, records_hex=payload[record_offset:].hex(),
        payload_length=len(payload), empty=not payload, break_kind=break_kind,
        coherence="ISO-TP declared length and CF sequence are regenerated; no selected lifecycle seed has a recovered MAC or freshness field; opaque records are preserved except by record-substitute or integrity-break",
    )


def uds_payload(event: TypedEvent) -> bytes:
    values = event.values()
    if values.get("empty"):
        return b""
    payload = bytearray()
    service = values.get("service")
    if service is not None:
        payload.append(int(service))
    subfunction = values.get("subfunction")
    if subfunction is not None:
        payload.append(int(subfunction))
    payload.extend(bytes.fromhex(values.get("records_hex", "")))
    return bytes(payload)


def iso_tp_frames(payload: bytes, break_kind: str = "none") -> tuple[bytes, ...]:
    """Encode a UDS payload as classic-CAN ISO-TP frames."""
    if len(payload) <= 7:
        declared = len(payload) + (1 if break_kind == "declared-length" else 0)
        return ((bytes((declared & 0x0F,)) + payload).ljust(8, b"\0"),)
    if len(payload) > 0xFFF:
        raise ValueError("classic ISO-TP grammar supports at most 4095 payload bytes")
    declared = len(payload) + (1 if break_kind == "declared-length" else 0)
    frames = [bytes((0x10 | (declared >> 8), declared & 0xFF)) + payload[:6]]
    remaining = payload[6:]
    sequence = 1
    while remaining:
        frames.append((bytes((0x20 | (sequence & 0x0F),)) + remaining[:7]).ljust(8, b"\0"))
        remaining = remaining[7:]
        sequence = (sequence + (2 if break_kind == "sequence" else 1)) & 0x0F
    return tuple(frame.ljust(8, b"\0") for frame in frames)


def validate_iso_tp_event(event: TypedEvent) -> tuple[bool, str]:
    values = event.values()
    if event.kind != "uds-request":
        return True, "not-uds"
    frames = iso_tp_frames(uds_payload(event), values.get("break_kind", "none"))
    break_kind = values.get("break_kind", "none")
    payload = uds_payload(event)
    if break_kind != "none":
        return False, break_kind
    if any(len(frame) != 8 for frame in frames):
        return False, "non-classic-frame-length"
    if len(payload) <= 7:
        return (frames[0][0] == len(payload), "well-formed" if frames[0][0] == len(payload) else "bad-sf-length")
    declared = ((frames[0][0] & 0x0F) << 8) | frames[0][1]
    if declared != len(payload):
        return False, "bad-ff-length"
    if any((frame[0] & 0x0F) != index % 16 for index, frame in enumerate(frames[1:], 1)):
        return False, "bad-cf-sequence"
    return True, "well-formed"


def machine_events(case: MachineCase) -> list[dict[str, Any]]:
    # One-cycle skew events cannot skip a TAUJ edge. Larger bulk advances can
    # dispatch multiple periodic requests without retiring intervening CPU
    # instructions, which is not a physically possible timer schedule.
    rx_rules, _tx_rules = decode_firmware_rules()
    events: list[dict[str, Any]] = []
    for stream in case.streams:
        for event in stream.events:
            values = event.values()
            if event.kind == "uds-request":
                can_id = int(values["can_id"])
                rule = rx_rules[can_id]
                for index, frame in enumerate(iso_tp_frames(uds_payload(event), values.get("break_kind", "none"))):
                    events.append({
                        "kind": "can-rx", "fifo": rule["fifo"], "boundary": "post-filter",
                        "can_id": hex(can_id), "data_hex": frame.hex(), "label": rule["label"],
                        "after_instructions": event.offset + index * 64,
                        "evidence": f"typed ISO-TP/UDS {event.mutation_class}; exact GAFL rule {rule['rule']}",
                    })
            elif event.kind == "timer-ticks":
                p_bus_cycles = int(values["p_bus_cycles"])
                if p_bus_cycles != TAUJ0_TIMER_SKEW_P_BUS_CYCLES:
                    raise ValueError(
                        "typed TAUJ0 events must advance exactly one P-Bus cycle; "
                        "bulk clock jumps collapse timer edges without CPU retirement"
                    )
                events.append({
                    "kind": "clock", "p_bus_cycles": p_bus_cycles,
                    "after_instructions": event.offset,
                    "evidence": "typed TAUJ0 P-Bus clock stream",
                })
            elif event.kind == "interrupt":
                events.append({
                    "kind": "interrupt", "channel": int(values["channel"]),
                    "after_instructions": event.offset,
                    "evidence": "typed interrupt-offset stream",
                })
            elif event.kind == "can-tx-complete":
                row = {
                    "kind": "can-tx-complete", "buffer": int(values["buffer"]),
                    "after_instructions": event.offset,
                    "evidence": "typed channel-1 transmit completion stream",
                }
                if values.get("tolerate_no_pending"):
                    row["tolerate_no_pending"] = True
                events.append(row)
            else:
                raise ValueError(f"unknown typed event kind {event.kind}")
    return sorted(events, key=lambda row: row["after_instructions"])


def normal_operation_snapshot(scenario_row: dict[str, Any]) -> dict[str, Any]:
    scenario_row["memory"] = [
        row for row in scenario_row.get("memory", [])
        if not (
            int(row.get("address", "-1"), 0) == capture_replay.RAM_BASE
            and row.get("fill") == 0
            and int(row.get("size", 0)) >= 0x20000
        )
    ]
    artifact = {
        "path": str(capture_replay.SNAPSHOT),
        "sha256": capture_replay.SNAPSHOT_SHA256,
        "address": hex(capture_replay.RAM_BASE),
        "executable": False,
        "evidence": "Registered Camry normal-operation LocalRAM snapshot",
    }
    artifacts = scenario_row.setdefault("artifacts", [])
    artifacts[:] = [
        row for row in artifacts
        if int(row.get("address", "-1"), 0) != capture_replay.RAM_BASE
    ]
    artifacts.append(artifact)
    return scenario_row


def scenario(case: MachineCase) -> dict[str, Any]:
    if case.name.startswith("compare_"):
        result = json.loads(ROUTINE_COMPARE_FIXTURE.read_text(encoding="utf-8"))
        result["compare_operands"] = True
        result["input_derived_table_indices"] = True
        result["name"] = f"typed_event_{case.case_id}"
        request_payload = uds_payload(case.stream(CAN_SOURCE).events[-1])
        for row in result["memory"]:
            address = int(row["address"], 0)
            if address == 0xFEBE5651:
                row["hex"] = request_payload.hex()
                row["evidence"] = "typed-event multi-byte RID comparison request"
            elif address == 0xFEBE59F0:
                cursor = 0xFEBE5651 + len(request_payload)
                remaining = 0x100 - len(request_payload)
                row["hex"] = (
                    cursor.to_bytes(4, "little")
                    + len(request_payload).to_bytes(2, "little")
                    + bytes.fromhex("dccb")
                    + remaining.to_bytes(2, "little")
                    + bytes.fromhex("000000919293")
                ).hex()
        result["checks"] = []
        if case.name == "compare_target_rid100f":
            result["stop_addresses"] = [
                hex(COMPARE_BENCHMARK_TARGET),
                *result["stop_addresses"],
            ]
        return result
    if case.stream(TX_SOURCE).events and not case.name.startswith("e2_"):
        result = normal_operation_snapshot(tx_preemption.build_base(12))
        result["compare_operands"] = True
        result["input_derived_table_indices"] = True
        typed_rx = [
            row for row in machine_events(case)
            if row["kind"] == "can-rx"
        ]
        if len(typed_rx) != 1:
            raise ValueError("TX-completion cases require one single-frame diagnostic request")
        fixed_rx = next(row for row in result["events"] if row["kind"] == "can-rx")
        fixed_rx.update({
            key: value for key, value in typed_rx[0].items()
            if key not in ("kind", "after_instructions")
        })
        for event in case.stream(TX_SOURCE).events:
            values = event.values()
            result["events"].append({
                "kind": "can-tx-complete",
                "buffer": int(values["buffer"]),
                "firmware_control": "0x8048",
                "after_instructions": TX_CHECKPOINT_INSTRUCTIONS + event.offset,
                "evidence": "typed channel-1 completion after a firmware-emitted diagnostic frame",
            })
        result["checks"] = []
        return result
    result = normal_operation_snapshot(copy.deepcopy(ingress.load_template("k")))
    result["name"] = f"typed_event_{case.case_id}"
    result["compare_operands"] = True
    result["input_derived_table_indices"] = True
    result["registers"].update({
        "PSW": "0", "PMR": "0", "RBASE": "0", "INTBP": "0x20200",
        "CTPC": "0", "CTPSW": "0",
    })
    result["memory"] = [
        {"address": "0xfebe0000", "size": 0x20000, "fill": 0,
         "evidence": "deterministic initialized LocalRAM for typed-event campaign"},
        *result["memory"], *copy.deepcopy(ingress.RUNTIME_ROWS),
    ]
    result["events"] = machine_events(case)
    result["checks"] = []
    result["expected_termination"] = "stop-address"
    return normal_operation_snapshot(result)


def lifecycle_disposition(case: stateful.Case) -> str:
    kinds = {step.kind for step in case.steps}
    if "pending_completion" in kinds:
        return "unsupported: pending DCM completion status is an internal callback argument"
    if "cancel" in kinds:
        return "unsupported: direct DCM cancel has no external event equivalent"
    if "poll" in kinds:
        return "reproduced: foreground return path performs the poll after real ingress"
    if "completion" in kinds:
        return "reproduced: complete ISO-TP ingress invokes transport completion"
    if "timeout" in kinds:
        return "reproduced: EIC136 request supplies the asynchronous timeout opportunity"
    return "reproduced: same-source request reuse through real ISO-TP ingress"


def from_lifecycle(case: stateful.Case) -> MachineCase:
    streams: dict[str, list[TypedEvent]] = {source: [] for source in SOURCES}
    offset = 0
    for step in case.steps:
        if step.kind == "request":
            streams[CAN_SOURCE].append(uds_event(step.request, offset))
            offset += 96
        elif step.kind == "timeout":
            streams[INTERRUPT_SOURCE].append(TypedEvent.make("interrupt", offset, channel=136))
            offset += 16
        elif step.kind == "tick":
            streams[TIMER_SOURCE].append(TypedEvent.make(
                "timer-ticks", offset,
                p_bus_cycles=TAUJ0_TIMER_SKEW_P_BUS_CYCLES,
            ))
            offset += 16
    return MachineCase(
        f"lifecycle_{case.name}",
        canonical_streams(streams),
        lifecycle_case_id=case.case_id,
        lifecycle_disposition=lifecycle_disposition(case),
        session=case.session,
        security_bitmap=case.security_bitmap,
    )


def representative_lifecycle_cases() -> list[MachineCase]:
    groups: dict[str, list[MachineCase]] = defaultdict(list)
    for case in stateful.lifecycle_prefix_cases():
        key = case.steps[-1].kind if case.steps[-1].kind != "request" else "reuse"
        groups[key].append(from_lifecycle(case))
    keys = ("poll", "cancel", "timeout", "completion", "pending_completion", "reuse")
    selected = [groups[key][index * 7] for index, key in enumerate(keys)]
    scheduler = next(case for case in stateful.seed_cases() if case.name == "scheduler_idle_reset")
    selected.append(from_lifecycle(scheduler))
    return selected

def tx_ready_case() -> MachineCase:
    return MachineCase(
        "tx_ready_rdbi_f181",
        canonical_streams({
            CAN_SOURCE: (uds_event(b"\x22\xf1\x81"),),
            TX_SOURCE: (
                TypedEvent.make("can-tx-complete", TX_SAFE_COMPLETION_OFFSET, "seed", buffer=22),
            ),
        }),
    )

def segmented_dispatch_case() -> MachineCase:
    return MachineCase(
        "segmented_wdbi_dispatch",
        canonical_streams({
            CAN_SOURCE: (
                uds_event(b"\x2e\x20\x01" + bytes(range(16))),
            ),
        }),
        session=3,
    )

def segmented_wdbi_rejection_cases() -> list[MachineCase]:
    record = bytes(range(16))
    return [
        MachineCase(
            f"segmented_wdbi_{did:04x}_negative",
            canonical_streams({
                CAN_SOURCE: (
                    uds_event(bytes((0x2e, did >> 8, did & 0xff)) + record),
                ),
            }),
            session=3,
            foreground_cycles=3,
            expected_response=b"\x2e\x13",
        )
        for did in stateful.dcm.WDBI_DIDS
    ]

def security_compare_seed() -> MachineCase:
    return MachineCase(
        "segmented_security_key_positive",
        canonical_streams({
            CAN_SOURCE: (uds_event(b"\x27\x04" + bytes(16)),),
        }),
        session=3,
        memory_primes=((SECURITY_KEY_STATE_ADDRESS, SECURITY_KEY_STATE),),
    )


def wdbi_target_seed() -> MachineCase:
    return MachineCase(
        "wdbi_2012_positive",
        canonical_streams({
            CAN_SOURCE: (uds_event(b"\x2e\x20\x12\x01"),),
        }),
        session=3,
    )


def comparison_benchmark_cases() -> tuple[MachineCase, MachineCase]:
    session = uds_event(b"\x10\x03", 0)
    base_request = uds_event(b"\x31\x01\x10\x10", 96)
    target_request = uds_event(b"\x31\x01\x10\x0f", 96, mutation_class="multi-byte-substitute")
    base = MachineCase(
        "compare_baseline_rid1010",
        canonical_streams({CAN_SOURCE: (session, base_request)}),
    )
    target = MachineCase(
        "compare_target_rid100f",
        canonical_streams({CAN_SOURCE: (session, target_request)}),
        parent_id=base.case_id,
        mutated_source=CAN_SOURCE,
        mutation_class="multi-byte-substitute",
    )
    return base, target


def current_dictionary_executions_to_rid100f() -> int:
    base = stateful.make_case(
        "dictionary_compare_baseline",
        [stateful.request(b"\x31\x01\x10\x04")],
        3,
    )
    target = b"\x31\x01\x10\x0f"
    rng = random.Random(COMPARE_BENCHMARK_SEED)
    for execution in range(1, 20_001):
        candidate = stateful.mutate(base, rng, execution)
        if any(step.kind == "request" and step.request == target for step in candidate.steps):
            return execution
    raise RuntimeError("current comparison dictionary did not produce RID 0x100F in 20,000 executions")

def compare_dictionary_executions(
    target: int, operands: Sequence[int] | None, budget: int = 30_000,
) -> int | None:
    """Count deterministic 16-bit substitutions needed to emit *target*."""
    rng = random.Random(COMPARE_BENCHMARK_SEED)
    choices = tuple(operands or ())
    for execution in range(1, budget + 1):
        candidate = rng.choice(choices) if choices else rng.randrange(1 << 16)
        if candidate == target:
            return execution
    return None


def dictionary_tokens(extra: Iterable[bytes] = ()) -> tuple[bytes, ...]:
    return tuple(sorted(set(stateful.comparison_dictionary()) | set(extra), key=lambda token: (len(token), token)))


def replace_stream(case: MachineCase, source: str, stream: EventStream,
                   serial: int, mutation_class: str) -> MachineCase:
    streams = tuple(stream if current.source == source else current for current in case.streams)
    changed = [current.source for current, updated in zip(case.streams, streams, strict=True) if current != updated]
    if changed != [source]:
        raise AssertionError(f"mutation changed streams {changed}, expected {[source]}")
    return MachineCase(
        f"mut_{serial:06d}_{case.name}",
        streams,
        lifecycle_case_id=case.lifecycle_case_id,
        lifecycle_disposition=case.lifecycle_disposition,
        parent_id=case.case_id,
        mutated_source=source,
        mutation_class=mutation_class,
        session=case.session,
        security_bitmap=case.security_bitmap,
        memory_primes=case.memory_primes,
        foreground_cycles=case.foreground_cycles,
        expected_response=case.expected_response,
    )


def mutate_can(case: MachineCase, rng: random.Random, serial: int,
               tokens: Sequence[bytes]) -> MachineCase:
    stream = case.stream(CAN_SOURCE)
    events = list(stream.events)
    if not events:
        events.append(uds_event(b"\x3e\x00"))
    index = rng.randrange(len(events))
    event = events[index]
    values = event.values()
    payload = bytearray(uds_payload(event))
    mutation_class = rng.choice(MUTATION_CLASSES)
    if mutation_class == "identifier-coherent":
        chosen = rng.choice((0x7A1, 0x777))
        # The other identifier when the draw repeats the current one.
        values["can_id"] = chosen ^ 0x0D6 if chosen == int(values["can_id"]) else chosen
    elif mutation_class == "service-substitute":
        token = rng.choice(SERVICE_TOKENS)
        if not payload:
            payload.append(token)
        else:
            payload[0] = token ^ 1 if token == payload[0] else token
    elif mutation_class == "subfunction-substitute":
        if len(payload) < 2:
            payload.extend(b"\0" * (2 - len(payload)))
        token = rng.choice(SUBFUNCTION_TOKENS)
        payload[1] = token ^ 1 if token == payload[1] else token
    elif mutation_class == "record-substitute":
        token = (
            rng.choice(tokens)
            if tokens else rng.randbytes(rng.choice((1, 2, 4)))
        )
        start = 2 if len(payload) >= 2 and payload[0] in SUBFUNCTION_SERVICES else min(1, len(payload))
        if start == len(payload):
            payload.extend(token)
        else:
            position = rng.randrange(start, len(payload))
            if payload[position:position + len(token)] == token:
                token = bytes([token[0] ^ 1]) + token[1:]
            payload[position:position + len(token)] = token
    elif mutation_class == "integrity-break":
        start = 2 if len(payload) >= 2 and payload[0] in SUBFUNCTION_SERVICES else min(1, len(payload))
        if start == len(payload):
            payload.append(1)
        else:
            payload[rng.randrange(start, len(payload))] ^= 1 << rng.randrange(8)
    elif mutation_class == "length-coherent":
        if rng.randrange(2) and len(payload) > 1:
            del payload[rng.randrange(1, len(payload))]
        else:
            payload.insert(rng.randrange(1, len(payload) + 1) if payload else 0, rng.randrange(256))
    else:
        values["break_kind"] = "declared-length"
    rebuilt = uds_event(
        bytes(payload), event.offset, int(values["can_id"]), mutation_class,
        str(values.get("break_kind", "none")),
    )
    if rebuilt == event:
        # A declared-length break on an already broken event changes nothing.
        if payload:
            payload[-1] ^= 1
        else:
            payload.append(1)
        rebuilt = uds_event(bytes(payload), event.offset, int(values["can_id"]), "integrity-break", "none")
    events[index] = rebuilt
    return replace_stream(case, CAN_SOURCE, EventStream(CAN_SOURCE, tuple(events)), serial, mutation_class)


def mutate(case: MachineCase, source: str, rng: random.Random, serial: int,
           tokens: Sequence[bytes]) -> MachineCase:
    if source == CAN_SOURCE:
        return mutate_can(case, rng, serial, tokens)
    stream = case.stream(source)
    events = list(stream.events)
    mutation_class = "offset"
    if source == TIMER_SOURCE:
        if events:
            index = rng.randrange(len(events))
            old = events[index]
            delta = rng.choice((*range(-8, 0), *range(1, 9)))
            offset = max(0, old.offset + delta)
            if offset == old.offset:
                offset += 1
            events[index] = TypedEvent.make(
                "timer-ticks", offset, "timer-offset",
                p_bus_cycles=TAUJ0_TIMER_SKEW_P_BUS_CYCLES,
            )
        else:
            events.append(TypedEvent.make(
                "timer-ticks", rng.randrange(512), "timer-add",
                p_bus_cycles=TAUJ0_TIMER_SKEW_P_BUS_CYCLES,
            ))
            mutation_class = "timer-add"
    elif source == INTERRUPT_SOURCE:
        if events:
            index = rng.randrange(len(events)); old = events[index]
            events[index] = replace(old, offset=max(0, old.offset + rng.randrange(-32, 33)), mutation_class="interrupt-offset")
        else:
            events.append(TypedEvent.make("interrupt", rng.randrange(512), "interrupt-add", channel=136))
            mutation_class = "interrupt-add"
    elif source == TX_SOURCE:
        if events:
            index = rng.randrange(len(events)); old = events[index]
            events[index] = replace(old, offset=max(0, old.offset + rng.randrange(-32, 33)), mutation_class="tx-complete-offset")
        else:
            events.append(TypedEvent.make("can-tx-complete", TX_SAFE_COMPLETION_OFFSET, "tx-complete-add", buffer=22))
            mutation_class = "tx-complete-add"
    else:
        raise ValueError(f"unknown stream {source}")
    return replace_stream(case, source, EventStream(source, tuple(events)), serial, mutation_class)


def feedback(report: dict[str, Any]) -> Feedback:
    trace = report.get("instruction_trace", [])
    pcs = [int(row["pc"], 0) for row in trace]
    if report.get("final_pc") is not None:
        pcs.append(int(report["final_pc"], 0))
    edges = frozenset(pairwise(pcs))
    event_kinds = frozenset(
        str(row["kind"]) for row in report.get("device_events", [])
        if row.get("kind") not in ("scenario-initialization", "alias-write")
    )
    tokens: set[bytes] = set()
    for row in report.get("compare_operands", []):
        width = int(row["width_bits"]) // 8
        for key in ("left", "right"):
            value = int(row[key], 0) if isinstance(row[key], str) else int(row[key])
            tokens.add(value.to_bytes(width, "big", signed=False))
            tokens.add(value.to_bytes(width, "little", signed=False))
    indices = tuple(sorted({int(row["index"], 0) if isinstance(row["index"], str) else int(row["index"])
                            for row in report.get("input_derived_table_indices", [])}))
    for index in indices:
        for width in (1, 2, 4):
            if index < 1 << (width * 8):
                tokens.add(index.to_bytes(width, "big"))
    return Feedback(edges, event_kinds, tuple(sorted(tokens)), indices, frozenset(pcs))


def case_result_path(out: Path, case: MachineCase) -> Path:
    return out / "results" / f"{case.case_id}.json"


def persist_case_result(
    path: Path, case: MachineCase, report: dict[str, Any], result: Feedback,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema": f"{SCHEMA}-case-v1",
        "case_id": case.case_id,
        "report": {
            key: value for key, value in report.items()
            if key != "instruction_trace"
        },
        "feedback": {
            "edges": [[left, right] for left, right in sorted(result.edges)],
            "event_kinds": sorted(result.event_kinds),
            "compare_tokens": [token.hex() for token in result.compare_tokens],
            "table_indices": list(result.table_indices),
            "reached_pcs": sorted(result.reached_pcs),
        },
    }
    temporary = path.with_suffix(".tmp")
    temporary.write_text(json.dumps(payload, separators=(",", ":")) + "\n")
    temporary.replace(path)


def load_case_result(
    path: Path, case: MachineCase,
) -> tuple[dict[str, Any], Feedback] | None:
    try:
        payload = json.loads(path.read_text())
        if (
            payload["schema"] != f"{SCHEMA}-case-v1"
            or payload["case_id"] != case.case_id
        ):
            return None
        saved = payload["feedback"]
        result = Feedback(
            frozenset((int(left), int(right)) for left, right in saved["edges"]),
            frozenset(str(kind) for kind in saved["event_kinds"]),
            tuple(bytes.fromhex(token) for token in saved["compare_tokens"]),
            tuple(int(index) for index in saved["table_indices"]),
            frozenset(int(pc) for pc in saved["reached_pcs"]),
        )
        report = payload["report"]
        if not isinstance(report, dict) or "termination_reason" not in report:
            return None
        return report, result
    except (KeyError, TypeError, ValueError, json.JSONDecodeError, OSError):
        return None

def e2_cases(seed: int, window: int) -> tuple[MachineCase, MachineCase]:
    """Build bounded flood and forced-edge evaluation cases."""
    rng = random.Random(seed)
    payloads = (
        b"\x22\xf1\x81",
        b"\x2e\xf1\x90\x00\x00",
        b"\x27\x03",
        b"\x31\x01\xff\xff",
    )
    streams: dict[str, list[TypedEvent]] = {source: [] for source in SOURCES}
    for tick in range(window):
        offset = tick * 1024
        payload = bytearray(payloads[tick % len(payloads)])
        payload[-1] ^= 1 << rng.randrange(8)
        streams[CAN_SOURCE].append(
            uds_event(bytes(payload), offset, mutation_class="flood-record-bit"),
        )
        streams[TIMER_SOURCE].append(
            TypedEvent.make(
                "timer-ticks", offset + 96, "flood-timer",
                p_bus_cycles=TAUJ0_TIMER_SKEW_P_BUS_CYCLES,
            ),
        )
        streams[INTERRUPT_SOURCE].append(
            TypedEvent.make(
                "interrupt", offset + 192, "flood-interrupt", channel=136,
            ),
        )
        streams[TX_SOURCE].append(
            TypedEvent.make(
                "can-tx-complete", offset + 288, "flood-tx-complete",
                buffer=22, tolerate_no_pending=True,
            ),
        )
    flood = MachineCase("e2_flood", canonical_streams(streams))

    forced = MachineCase(
        "e2_forced_security_key",
        canonical_streams({
            CAN_SOURCE: (
                uds_event(b"\x10\x03", 0),
                uds_event(b"\x27\x03", 512),
                uds_event(
                    b"\x27\x04" + bytes.fromhex(
                        "00112233445566778899aabbccddeeff"
                    ),
                    1024,
                ),
            ),
            INTERRUPT_SOURCE: (
                TypedEvent.make(
                    "interrupt", 1536, "forced-followup", channel=136,
                ),
            ),
        }),
    )
    return flood, forced


def _e2_result(
    name: str, machine_scenario: dict[str, Any], report: dict[str, Any],
) -> dict[str, Any]:
    from tools.targets.camry.research.audit_camry_f33_definedness_boundaries import (
        crossing_stores,
        load_object_extents,
        stack_watermark,
        stores_from_rows,
    )

    trace = report.get("instruction_trace", [])
    reached = {int(row["pc"], 0) for row in trace}
    stores = stores_from_rows(report.get("memory_accesses", []))
    extents, _sienna_rows = load_object_extents()
    crossings = crossing_stores(stores, extents)
    writers: Counter[tuple[int, str]] = Counter()
    for store in stores:
        end = store.address + store.width
        for extent in extents:
            if store.address < extent.end and extent.address < end:
                writers[(store.pc, extent.name)] += 1
    initial_sp = int(machine_scenario["registers"]["sp"], 0)
    watermark = stack_watermark(trace, IMAGE.read_bytes(), initial_sp)
    events = Counter(
        str(row["kind"]) for row in report.get("device_events", [])
    )
    fault = report.get("fault")
    return {
        "name": name,
        "termination": report.get("termination_reason"),
        "instruction_count": report.get("instruction_count"),
        "edge_count": len(feedback(report).edges),
        "peripheral_events": dict(sorted(events.items())),
        "compare_operand_rows": len(report.get("compare_operands", [])),
        "table_index_rows": len(report.get("input_derived_table_indices", [])),
        "typed_machine_fault": fault,
        "controller_fault_events": {
            kind: count for kind, count in sorted(events.items())
            if any(token in kind for token in ("discard", "drop", "error", "ignored"))
        },
        "named_paths": {
            "dcm_read_did_service_962f2": 0x962F2 in reached,
            "dcm_write_did_service_95978": 0x95978 in reached,
            "execute_write_did_payload_and_report_result_95674": 0x95674 in reached,
            "app_security_compare_key_8d91a": 0x8D91A in reached,
        },
        "writers": [
            {"pc": f"0x{pc:08X}", "object": obj, "stores": count}
            for (pc, obj), count in sorted(writers.items())
        ],
        "oracles": {
            "uninitialized_read": (
                fault if fault and fault.get("kind") == "uninitialized-read"
                else None
            ),
            "object_boundary_crossings": crossings,
            "stack_watermark": watermark.row(),
        },
        "bounded_edge_shortcuts": report.get("instruction_trace_shortcuts", []),
    }


def evaluate_e2(out: Path, seed: int, window: int) -> dict[str, Any]:
    if window < 1:
        raise ValueError("E2 window must be positive")
    out.mkdir(parents=True, exist_ok=True)
    flood, forced = e2_cases(seed, window)
    rows = []
    for case in (flood, forced):
        machine_scenario = scenario(case)
        machine_scenario["name"] = case.name
        if case is forced:
            machine_scenario["bounded_entries"] = ["0x8d91a"]
            machine_scenario["bounded_edges"] = [
                {"pc": "0x8d97c", "target": "0x8d95c", "entry": "0x8d91a"},
                {"pc": "0x8d992", "target": "0x8d980", "entry": "0x8d91a"},
            ]
        scenario_path = out / f"{case.name}.scenario.json"
        scenario_path.write_text(
            json.dumps(machine_scenario, indent=2) + "\n", encoding="utf-8",
        )
        report = capture_many(
            TARGET, [scenario_path], out / "reports", instruction_trace=True,
        )[0]
        rows.append(_e2_result(case.name, machine_scenario, report))
    summary = {
        "schema": "camry-f33-machine-e2-evaluation-v1",
        "target": TARGET,
        "seed": seed,
        "window": window,
        "forced_edges": [
            {"pc": "0x0008D97C", "target": "0x0008D95C", "entry": "0x0008D91A"},
            {"pc": "0x0008D992", "target": "0x0008D980", "entry": "0x0008D91A"},
        ],
        "configurations": rows,
    }
    (out / "summary.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8",
    )
    return summary


def load_functions() -> list[tuple[int, int, str]]:
    rows = []
    for line in SYMBOLS.read_text(encoding="utf-8").splitlines():
        row = json.loads(line)
        for start, end in row["ranges"]:
            rows.append((start, end + 1, row["name"]))
    return sorted(rows)


def direct_call_distances(target: int) -> tuple[dict[int, int], list[tuple[int, int, str]]]:
    image = IMAGE.read_bytes()
    functions = load_functions()
    starts = {start for start, _end, _name in functions}
    reverse: dict[int, set[int]] = defaultdict(set)
    for start, end, _name in functions:
        for address in range(start, min(end, len(image) - 3), 2):
            if is_jarl22(image, address):
                callee = jarl22_target(image, address)
                if callee in starts:
                    reverse[callee].add(start)
    distances = {target: 0}
    queue = deque((target,))
    while queue:
        callee = queue.popleft()
        for caller in reverse.get(callee, ()):
            if caller not in distances:
                distances[caller] = distances[callee] + 1
                queue.append(caller)
    return distances, functions


def trace_distance(pcs: Iterable[int], distances: dict[int, int],
                   functions: Sequence[tuple[int, int, str]]) -> int | None:
    starts = [start for start, _end, _name in functions]
    found = []
    for pc in pcs:
        index = bisect_right(starts, pc) - 1
        if index < 0:
            continue
        start, end, _name = functions[index]
        if pc < end and start in distances:
            found.append(distances[start])
    return min(found) if found else None


def write_case(path: Path, case: MachineCase) -> None:
    path.write_text(json.dumps(case.as_dict(), indent=2) + "\n", encoding="utf-8")


def checkpoint_trial_events(case: MachineCase, tx: bool) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    if case.session is not None:
        primes = (
            *stateful.dcm.session_primes(case.session, case.security_bitmap),
            *((address, b"\x5a") for address in stateful.dcm.ADMISSION),
            (stateful.dcm.ADMISSION_CLEAR, b"\x00"),
        )
        rows.extend({
            "kind": "memory-write",
            "address": hex(address),
            "data_hex": value.hex(),
            "after_instructions": 0,
            "evidence": "Declared lifecycle state at the operational checkpoint",
        } for address, value in primes)
    rows.extend({
        "kind": "memory-write",
        "address": hex(address),
        "data_hex": value.hex(),
        "after_instructions": 0,
        "evidence": "Prepared positive-control state at the operational checkpoint",
    } for address, value in case.memory_primes)
    for stream in case.streams:
        for event in stream.events:
            single = MachineCase(
                "single-event",
                canonical_streams({stream.source: (event,)}),
            )
            event_rows = machine_events(single)
            if event.kind == "uds-request" and len(event_rows) > 1:
                event_rows[0]["after_instructions"] = event.offset
                rows.append(event_rows[0])
                rows.append({
                    "kind": "can-tx-complete",
                    "buffer": 22,
                    "firmware_control": "0x8048",
                    "tolerate_no_pending": True,
                    "after_instructions": (
                        event.offset + SEGMENTED_FLOW_CONTROL_COMPLETE_OFFSET
                    ),
                    "evidence": (
                        "ECU flow-control completion placed by the calibrated "
                        "unmutated segmented seed"
                    ),
                })
                for index, row in enumerate(event_rows[1:]):
                    row["after_instructions"] = (
                        event.offset + SEGMENTED_CONSECUTIVE_OFFSET + index * 64
                    )
                    rows.append(row)
            else:
                rows.extend(event_rows)
    if tx:
        for row in rows:
            if row["kind"] == "can-tx-complete":
                row["firmware_control"] = "0x8048"
    return sorted(rows, key=lambda row: row["after_instructions"])


def checkpoint_scenario(cases: Sequence[MachineCase]) -> dict[str, Any]:
    if not cases:
        raise ValueError("checkpoint batch cannot be empty")
    empty = capture_replay.CapturePeriod(0, (), ())
    result = capture_replay.build_replay_scenario(
        {
            "kind": "typed-event-campaign",
            "normal_ram_sha256": capture_replay.SNAPSHOT_SHA256,
        },
        (empty,),
        "typed_event_readiness_template",
        include_completions=False,
        foreground_ticks=False,
    )
    identity = hashlib.sha256(
        "".join(case.case_id for case in cases).encode()
    ).hexdigest()[:16]
    result["name"] = f"typed_event_checkpoint_batch_{identity}"
    result["compare_operands"] = True
    result["input_derived_table_indices"] = True
    result["instruction_trace_start_step"] = "normal-operation"
    steps = result["steps"][:capture_replay.REPLAY_PREFIX_STEPS]
    for step in steps:
        if step.get("kind") == "trial":
            step["capture_rows"] = False
    for case in cases:
        steps.append({"kind": "restore", "checkpoint": "normal-operation"})
        events = checkpoint_trial_events(
            case, bool(case.stream(TX_SOURCE).events),
        )
        for row in events:
            if row["kind"] == "can-tx-complete":
                row["tolerate_no_pending"] = True
        steps.append({
            "kind": "trial",
            "name": case.case_id,
            "max_instructions": (
                case.foreground_cycles
                * capture_replay.FOREGROUND_TRIAL_MAX_INSTRUCTIONS
            ),
            "stop_addresses": [
                hex(capture_replay.BOOT_TRANSFER),
                "0x619be",
            ],
            "stop_after_arrivals": [{
                "address": hex(capture_replay.FOREGROUND_COMPLETE),
                "count": case.foreground_cycles,
            }],
            "events": events,
            "checks": [
                *capture_replay.END_MODE_CHECKS,
                *([{
                    "name": "Completed UDS response",
                    "kind": "memory",
                    "address": "0xfebe5968",
                    "size": len(case.expected_response),
                    "equals_hex": case.expected_response.hex(),
                }] if case.expected_response is not None else []),
            ],
        })
    result["steps"] = steps
    return result


def trial_report(row: dict[str, Any], trace_report: dict[str, Any] | None) -> dict[str, Any]:
    report = {
        "passed": row["passed"],
        "termination_reason": row["termination_reason"],
        "fault": row.get("fault"),
        "instruction_count": row["instruction_count"],
        "final_pc": row["final_pc"],
        "checks": row["checks"],
        "device_events": row["event_rows"],
        "instruction_trace": (
            trace_report.get("instruction_trace", [])
            if trace_report is not None else row.get("instruction_trace", [])
        ),
        "checkpointed": True,
        "restore_nanoseconds": row["restore_nanoseconds"],
        "execution_nanoseconds": row["execution_nanoseconds"],
        "instructions_per_second": row["instructions_per_second"],
        "coverage_replayed": trace_report is not None,
        "checkpoint_trace": bool(row.get("instruction_trace")),
        "compare_operands": row.get("compare_operands", []),
        "input_derived_table_indices": row.get("input_derived_table_indices", []),
    }
    if trace_report is not None:
        if (
            bool(trace_report.get("passed")) != bool(row["passed"])
            or trace_report.get("termination_reason") != row["termination_reason"]
        ):
            raise RuntimeError("checkpoint trial and coverage replay diverged")
    return report


def run_cases(cases: Sequence[MachineCase], out: Path, batch_size: int) -> list[tuple[MachineCase, dict[str, Any], Feedback]]:
    scenario_dir = out / "scenarios"
    report_dir = out / "reports"
    scenario_dir.mkdir(parents=True, exist_ok=True)
    flat_paths: dict[str, Path] = {}
    for case in cases:
        path = scenario_dir / f"{case.case_id}.json"
        path.write_text(json.dumps(scenario(case), separators=(",", ":")) + "\n", encoding="utf-8")
        flat_paths[case.case_id] = path
    completed: dict[str, tuple[dict[str, Any], Feedback]] = {}
    for case in cases:
        result_path = case_result_path(out, case)
        saved = load_case_result(result_path, case)
        if saved is None:
            result_path.unlink(missing_ok=True)
        else:
            completed[case.case_id] = saved

    comparison = [
        case for case in cases
        if case.name.startswith("compare_") and case.case_id not in completed
    ]
    for case in comparison:
        report = capture_many(
            TARGET, [flat_paths[case.case_id]],
            report_dir / "comparison", instruction_trace=False,
        )[0]
        result = feedback(report)
        persist_case_result(case_result_path(out, case), case, report, result)
        completed[case.case_id] = (report, result)

    ordinary = [case for case in cases if not case.name.startswith("compare_")]
    for tx in (False, True):
        selected = [
            case for case in ordinary
            if bool(case.stream(TX_SOURCE).events) == tx
            and case.case_id not in completed
        ]
        for first in range(0, len(selected), batch_size):
            batch = selected[first:first + batch_size]
            pending = list(batch)
            screened_cases = [
                case for case in batch if case.mutated_source is not None
            ]
            if screened_cases:
                screen_scenario = checkpoint_scenario(screened_cases)
                screen_path = scenario_dir / (
                    f"{screen_scenario['name']}.screen.json"
                )
                screen_path.write_text(
                    json.dumps(screen_scenario, separators=(",", ":")) + "\n",
                    encoding="utf-8",
                )
                screened = p1me_machine._execute(
                    TARGET, [screen_path], instruction_trace=False,
                )["reports"][0]
                screen_trials = {
                    row["name"]: row
                    for row in screened.get("checkpointing", {}).get("trials", [])
                }
                for case in screened_cases:
                    screen = screen_trials.get(case.case_id)
                    if (
                        screen is None
                        or screen.get("termination_reason")
                        in {"stop-address", "stop-after-arrivals"}
                    ):
                        continue
                    report = trial_report(screen, None)
                    report["checkpoint_trace"] = False
                    result = feedback(report)
                    persist_case_result(
                        case_result_path(out, case), case, report, result,
                    )
                    completed[case.case_id] = (report, result)
                    pending.remove(case)
            if not pending:
                continue
            batch_scenario = checkpoint_scenario(pending)
            batch_path = scenario_dir / f"{batch_scenario['name']}.json"
            batch_path.write_text(
                json.dumps(batch_scenario, separators=(",", ":")) + "\n",
                encoding="utf-8",
            )
            traced_batch = p1me_machine._execute(
                TARGET, [batch_path], instruction_trace=True,
            )
            batch_report = traced_batch["reports"][0]
            if "checkpointing" not in batch_report:
                error = batch_report.get("error", {})
                detail = str(error.get("detail", batch_report))
                if "cannot allocate complete instruction trace" not in detail:
                    raise RuntimeError(f"checkpoint batch failed: {detail}")
                for case in pending:
                    report = {
                        "passed": False, "termination_reason": "trace-limit",
                        "instruction_count": None, "final_pc": None,
                        "checks": [], "device_events": [],
                        "checkpointed": False, "error": {"detail": detail},
                    }
                    result = feedback(report)
                    persist_case_result(
                        case_result_path(out, case), case, report, result,
                    )
                    completed[case.case_id] = (report, result)
                continue
            trial_by_name = {
                row["name"]: row
                for row in batch_report["checkpointing"]["trials"]
            }
            compact_trials = []
            for case in pending:
                trial = trial_by_name.get(case.case_id)
                if trial is None:
                    raise RuntimeError("checkpoint batch omitted its trial report")
                report = trial_report(trial, None)
                result = feedback(report)
                persist_case_result(
                    case_result_path(out, case), case, report, result,
                )
                completed[case.case_id] = (report, result)
                compact_trials.append({
                    key: value for key, value in trial.items()
                    if key not in (
                        "instruction_trace", "compare_operands",
                        "input_derived_table_indices",
                    )
                })
            compact_report = {
                key: value for key, value in batch_report.items()
                if key not in {
                    "memory_accesses", "device_events", "instruction_trace",
                    "compare_operands", "input_derived_table_indices",
                }
            }
            compact_report["checkpointing"] = {
                **{
                    key: value
                    for key, value in batch_report["checkpointing"].items()
                    if key != "trials"
                },
                "trials": compact_trials,
            }
            checkpoint_report_dir = report_dir / "checkpoint"
            checkpoint_report_dir.mkdir(parents=True, exist_ok=True)
            (checkpoint_report_dir / f"{batch_path.stem}.report.json").write_text(
                json.dumps(compact_report, indent=2) + "\n", encoding="utf-8",
            )
    return [
        (case, *completed[case.case_id])
        for case in cases
    ]


def select_parent(corpus: Sequence[tuple[MachineCase, Feedback]], rng: random.Random,
                  distances: dict[int, int] | None, functions: Sequence[tuple[int, int, str]]) -> MachineCase:
    if not distances:
        return rng.choice(corpus)[0]
    weights = []
    for _case, result in corpus:
        distance = trace_distance(result.reached_pcs, distances, functions)
        weights.append(1.0 if distance is None else 1.0 + 8.0 / (distance + 1))
    return rng.choices([case for case, _result in corpus], weights=weights, k=1)[0]


def campaign(out: Path, seed: int, budget: int, batch_size: int,
             target_function: int | None = None, *, directed_energy: bool = True,
             dictionary_mode: str = "learned") -> dict[str, Any]:
    if dictionary_mode not in {"learned", "static", "raw"}:
        raise ValueError("dictionary_mode must be learned, static, or raw")
    if budget < 1 or batch_size < 1:
        raise ValueError("budget and batch-size must be positive")
    if hashlib.sha256(IMAGE.read_bytes()).hexdigest() != IMAGE_SHA256:
        raise RuntimeError("exact CodeFlash identity drifted")
    rng = random.Random(seed)
    lifecycle = representative_lifecycle_cases()
    executable_seeds = [
        case for case in lifecycle
        if not case.lifecycle_disposition.startswith("unsupported")
    ]
    executable_seeds.append(tx_ready_case())
    positive_seed: MachineCase | None = None
    if target_function == 0x8D91A:
        positive_seed = security_compare_seed()
    elif target_function == 0x95674:
        positive_seed = wdbi_target_seed()
    if positive_seed is not None:
        replace_at = next(
            index for index, case in enumerate(executable_seeds)
            if "security_key" in case.name
        )
        executable_seeds[replace_at] = positive_seed
    benchmark_base, benchmark_target = comparison_benchmark_cases()
    seeds = list({
        case.case_id: case for case in executable_seeds
    }.values())[:min(len(executable_seeds), budget)]
    distances: dict[int, int] | None = None
    functions: list[tuple[int, int, str]] = []
    if target_function is not None:
        distances, functions = direct_call_distances(target_function)
    out.mkdir(parents=True, exist_ok=True)
    corpus_dir = out / "corpus"
    if corpus_dir.exists():
        shutil.rmtree(corpus_dir)
    corpus_dir.mkdir()
    benchmark_results = run_cases(
        (benchmark_base, benchmark_target),
        out / "compare-benchmark",
        batch_size,
    )
    benchmark_feedback = next(
        result for case, _report, result in benchmark_results
        if case.case_id == benchmark_target.case_id
    )
    benchmark_base_report = next(
        report for case, report, _result in benchmark_results
        if case.case_id == benchmark_base.case_id
    )
    gate_operands = sorted({
        int(row[key], 0) & 0xFFFF
        for row in benchmark_base_report.get("compare_operands", [])
        if 0x97180 <= int(row["compare_pc"], 0) <= 0x971E0
        for key in ("left", "right")
    })
    benchmark_budget = 30_000
    without_compare_dictionary = compare_dictionary_executions(
        0x100F, None, benchmark_budget,
    )
    with_compare_dictionary = compare_dictionary_executions(
        0x100F, gate_operands, benchmark_budget,
    )

    started = time.monotonic()
    known_edges: set[tuple[int, int]] = set()
    known_events: set[str] = set()
    learned_tokens: set[bytes] = set()
    retained: list[tuple[MachineCase, Feedback]] = []
    rows: list[dict[str, Any]] = []
    usage: dict[str, Counter[str]] = {source: Counter() for source in SOURCES}
    source_edges: dict[str, set[tuple[int, int]]] = {
        source: set() for source in SOURCES
    }
    observation_counts: Counter[str] = Counter()

    def consume(results: Sequence[tuple[MachineCase, dict[str, Any], Feedback]], offspring: bool) -> None:
        for case, report, result in results:
            source = case.mutated_source or CAN_SOURCE
            usage[source]["inputs_executed"] += 1
            if offspring:
                usage[source]["inputs_mutated"] += 1
            new_edges = result.edges - known_edges
            new_events = result.event_kinds - known_events
            source_edges[source].update(result.edges)
            usage[source]["new_global_edges"] += len(new_edges)
            interesting = bool(new_edges or new_events) or not retained
            if interesting:
                known_edges.update(result.edges)
                known_events.update(result.event_kinds)
                retained.append((case, result))
                write_case(corpus_dir / f"{case.case_id}.json", case)
                if offspring:
                    usage[source]["retained_offspring"] += 1
            learned_tokens.update(result.compare_tokens)
            observation_counts["compare_operands"] += len(report.get("compare_operands", []))
            observation_counts["input_derived_table_indices"] += len(
                report.get("input_derived_table_indices", [])
            )
            receive_frames_expected = sum(
                len(iso_tp_frames(
                    uds_payload(event),
                    str(event.values().get("break_kind", "none")),
                ))
                for event in case.stream(CAN_SOURCE).events
            )
            receive_frames_popped = sum(
                row.get("kind") == "can-rx-pop"
                for row in report.get("device_events", [])
            )
            well_formed = [validate_iso_tp_event(event) for event in case.stream(CAN_SOURCE).events]
            rows.append({
                "id": case.case_id, "parent_id": case.parent_id, "mutated_source": case.mutated_source,
                "mutation_class": case.mutation_class, "retained": interesting,
                "passed": bool(report.get("passed")), "termination": report.get("termination_reason"),
                "fault_kind": (report.get("fault") or {}).get("kind"),
                "fault_address": (report.get("fault") or {}).get("address"),
                "instructions": report.get("instruction_count"), "edge_count": len(result.edges),
                "checkpointed": bool(report.get("checkpointed")),
                "coverage_replayed": bool(report.get("coverage_replayed")),
                "checkpoint_trace": bool(report.get("checkpoint_trace")),
                "restore_nanoseconds": report.get("restore_nanoseconds"),
                "trial_instructions_per_second": report.get("instructions_per_second"),
                "new_edge_count": len(new_edges), "event_kinds": sorted(result.event_kinds),
                "well_formed_requests": [ok for ok, _reason in well_formed],
                "request_validation": [reason for _ok, reason in well_formed],
                "compare_operand_count": len(report.get("compare_operands", [])),
                "table_index_count": len(report.get("input_derived_table_indices", [])),
                "distance_to_target": trace_distance(result.reached_pcs, distances, functions) if distances else None,
                "reached_named_target": (
                    target_function in result.reached_pcs if target_function is not None else None
                ),
                "target_instruction": next((
                    int(trace_row["instruction"])
                    for trace_row in report.get("instruction_trace", [])
                    if (
                        target_function is not None
                        and int(trace_row["pc"], 0) == target_function
                    )
                ), None),
                "receive_frames_expected": receive_frames_expected,
                "receive_path_accepted": receive_frames_popped >= receive_frames_expected,
            })

    consume(run_cases(seeds, out, batch_size), False)
    serial = 0
    while len(rows) < budget:
        count = min(batch_size, budget - len(rows))
        offspring = []
        if dictionary_mode == "learned":
            tokens = dictionary_tokens(learned_tokens)
        elif dictionary_mode == "static":
            tokens = dictionary_tokens()
        else:
            tokens = ()
        seen = {row["id"] for row in rows}
        for _ in range(count):
            source = SOURCES[serial % len(SOURCES)]
            if source == TX_SOURCE:
                parents = [
                    row for row in retained
                    if row[0].stream(TX_SOURCE).events
                ]
                parent = select_parent(
                    parents, rng, distances if directed_energy else None, functions,
                )
            else:
                parents = [
                    row for row in retained
                    if not row[0].stream(TX_SOURCE).events
                ]
                parent = select_parent(
                    parents, rng, distances if directed_energy else None, functions,
                )
            for attempt in range(1_024):
                candidate = mutate(parent, source, rng, serial + attempt * budget, tokens)
                if candidate.case_id not in seen:
                    break
            else:
                raise RuntimeError(f"could not produce a new {source} stream tuple")
            offspring.append(candidate)
            seen.add(candidate.case_id)
            serial += 1
        consume(run_cases(offspring, out, batch_size), True)
    positive_row = (
        next(row for row in rows if row["id"] == positive_seed.case_id)
        if positive_seed is not None else None
    )
    if positive_row is not None and not positive_row["reached_named_target"]:
        raise RuntimeError(
            f"directed positive seed did not reach 0x{target_function:08X}"
        )

    elapsed = time.monotonic() - started
    benchmark_reached = COMPARE_BENCHMARK_TARGET in benchmark_feedback.reached_pcs
    current_dictionary_executions = current_dictionary_executions_to_rid100f()
    lifecycle_rows = [{"id": case.lifecycle_case_id, "name": case.name,
                       "disposition": case.lifecycle_disposition} for case in lifecycle]
    lifecycle_census = Counter(
        lifecycle_disposition(case).split(":", 1)[0]
        for case in stateful.lifecycle_prefix_cases()
    )
    summary = {
        "schema": SCHEMA, "target": TARGET, "image_sha256": IMAGE_SHA256,
        "machine_state": {
            "checkpoint": "normal-operation",
            "live_mode": "0x0702",
            "desired_mode": "0x0702",
            "active_mode": "0x0702",
            "normal_ram_sha256": capture_replay.SNAPSHOT_SHA256,
        },
        "seed": seed, "budget": budget, "executions": len(rows),
        "seed_executions": len(seeds), "mutation_executions": len(rows) - len(seeds),
        "elapsed_seconds": elapsed, "executions_per_second": len(rows) / elapsed,
        "dictionary_mode": dictionary_mode,
        "checkpointing": {
            "trial_executions": sum(bool(row["checkpointed"]) for row in rows),
            "coverage_replay_executions": sum(bool(row["coverage_replayed"]) for row in rows),
            "checkpoint_trace_executions": sum(
                bool(row["checkpoint_trace"]) for row in rows
            ),
            "mean_trial_instructions_per_second": (
                sum(rate for row in rows if (rate := row["trial_instructions_per_second"]))
                / max(1, sum(row["trial_instructions_per_second"] is not None for row in rows))
            ),
            "trace_limit_executions": sum(
                row["termination"] == "trace-limit" for row in rows
            ),
        },
        "edge_count": len(known_edges),
        "edge_set": [[f"0x{left:08X}", f"0x{right:08X}"] for left, right in sorted(known_edges)],
        "peripheral_event_kinds": sorted(known_events),
        "retained_corpus_size": len(retained),
        "retained_case_ids": [case.case_id for case, _feedback in retained],
        "stream_usage": {
            source: {
                **{
                    key: usage[source][key]
                    for key in (
                        "inputs_executed", "inputs_mutated",
                        "retained_offspring", "new_global_edges",
                    )
                },
                "edges_observed": len(source_edges[source]),
            }
            for source in SOURCES
        },
        "substitution_dictionary": {
            "static_tokens": len(stateful.comparison_dictionary()),
            "learned_compare_tokens": len(learned_tokens),
            "table_indices": sorted({index for _case, result in retained for index in result.table_indices}),
            "compare_operand_rows": observation_counts["compare_operands"],
            "table_index_rows": observation_counts["input_derived_table_indices"],
        },
        "compare_benchmark": {
            "gate": "RID table equality at CMP 0x000971DE / branch 0x000971E0",
            "target_function": f"0x{COMPARE_BENCHMARK_TARGET:08X}",
            "target_reached_in_machine_run": benchmark_reached,
            "ingress": "exact-image machine direct dispatcher fixture; excluded from real-ingress corpus metrics",
            "seed": COMPARE_BENCHMARK_SEED,
            "budget": benchmark_budget,
            "operand_dictionary_size": len(gate_operands),
            "operand_dictionary": [f"0x{value:04X}" for value in gate_operands],
            "without_compare_dictionary_executions": without_compare_dictionary,
            "with_compare_dictionary_executions": with_compare_dictionary,
            "former_static_dictionary_executions": current_dictionary_executions,
        },
        "target_function": f"0x{target_function:08X}" if target_function is not None else None,
        "directed_energy": {
            "enabled": target_function is not None and directed_energy,
            "positive_control": (
                {
                    "case_id": positive_seed.case_id,
                    "name": positive_seed.name,
                    "reached": bool(positive_row["reached_named_target"]),
                    "instruction": positive_row["target_instruction"],
                }
                if positive_seed is not None else None
            ),
            "functions_with_distance": len(distances or {}),
            "inputs_reaching_named_target": (
                sum(bool(row["reached_named_target"]) for row in rows)
                if target_function is not None else 0
            ),
            "first_execution_reaching_named_target": next(
                (
                    index for index, row in enumerate(rows, start=1)
                    if row["reached_named_target"]
                ),
                None,
            ),
            "minimum_observed_distance": min(
                (
                    distance for row in rows
                    if (distance := row["distance_to_target"]) is not None
                ),
                default=None,
            ),
        },
        "lifecycle_prefix": lifecycle_rows,
        "executed_inputs": rows,
        "lifecycle_prefix_census": {
            "total": sum(lifecycle_census.values()),
            **dict(sorted(lifecycle_census.items())),
            "representatives_executed": sum(
                row["id"] in {
                    case.case_id for case in lifecycle
                    if not case.lifecycle_disposition.startswith("unsupported")
                }
                for row in rows
            ),
        },
        "hook_status": {
            "compare_operands": {
                "status": "enabled",
                "observed_rows": observation_counts["compare_operands"],
                "report_field": "compare_operands",
                "row": [
                    "compare_pc", "branch_pc", "mnemonic", "width_bits",
                    "left", "right",
                ],
                "instruction_classes": [
                    "CMP register/register and immediate/register",
                    "TST when its flags feed a conditional branch",
                    "CMPF.S and CMPF.D when their condition feeds a conditional branch",
                    "flag-setting arithmetic only when its flags feed a conditional branch",
                ],
            },
            "input_derived_table_indices": {
                "status": "enabled",
                "observed_rows": observation_counts["input_derived_table_indices"],
                "report_field": "input_derived_table_indices",
                "row": [
                    "pc", "base", "index", "scale", "effective_address",
                    "access_width_bits", "access",
                ],
                "instruction_classes": [
                    "loads and stores whose effective-address index is data-dependent on an input event",
                    "computed indirect branches whose table selector is data-dependent on an input event",
                ],
            },
        },
    }
    (out / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path)
    parser.add_argument("--seed", type=int, default=20261124)
    parser.add_argument("--budget", type=int, default=32)
    parser.add_argument("--batch-size", type=int, default=8)
    parser.add_argument("--target-function", type=lambda value: int(value, 0))
    parser.add_argument(
        "--no-directed-energy", action="store_true",
        help="observe --target-function reach without distance-weighted parent selection",
    )
    parser.add_argument(
        "--dictionary-mode", choices=("learned", "static", "raw"),
        default="learned",
    )
    parser.add_argument("--replay-scenario", type=Path)
    parser.add_argument("--periods", type=int)
    parser.add_argument("--discriminate-periods", type=int, default=0)
    parser.add_argument("--e2", action="store_true")
    parser.add_argument("--e2-window", type=int, default=16)
    args = parser.parse_args()
    if args.no_directed_energy and args.target_function is None:
        parser.error("--no-directed-energy requires --target-function")
    if args.e2:
        result = evaluate_e2(
            args.out or DEFAULT_OUT.parent / "e2-forced-flood",
            args.seed,
            args.e2_window,
        )
        print(json.dumps(result, indent=2))
        return 0
    if args.replay_scenario is not None:
        from tools.targets.camry.research.replay_camry_f33_capture_machine import (
            DEFAULT_OUT as REPLAY_OUT,
        )
        from tools.targets.camry.research.replay_camry_f33_capture_machine import (
            replay_capture,
        )

        replay = replay_capture(
            args.replay_scenario, args.out or REPLAY_OUT, args.periods,
            args.discriminate_periods, args.batch_size,
        )
        print(json.dumps({
            "capture": replay["capture"],
            "periods_requested": replay["periods_requested"],
            "periods_completed_before_stop": replay["periods_completed_before_stop"],
            "faults": replay["faults"],
            "reception": replay["reception"],
        }, indent=2))
        return 0
    result = campaign(
        args.out or DEFAULT_OUT, args.seed, args.budget, args.batch_size,
        args.target_function, directed_energy=not args.no_directed_energy,
        dictionary_mode=args.dictionary_mode,
    )
    print(json.dumps({key: result[key] for key in (
        "executions", "elapsed_seconds", "executions_per_second", "edge_count",
        "retained_corpus_size", "stream_usage", "target_function",
    )}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
