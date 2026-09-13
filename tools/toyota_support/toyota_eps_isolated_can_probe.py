#!/usr/bin/env python3
"""Probe the isolated Camry EPS-side CAN segment without persistent writes.

The default is a JSON dry run.  Live execution is intentionally awkward: it
requires an A30-disconnected, rack-only topology, power-off resistance
measurements, exact physical attestations, and interactive power sequencing.
The Panda is powered by a battery-powered USB host (not vehicle or mains) and
put in NOOUTPUT (host data TX blocked, protocol ACK enabled) before the
auxiliary battery is reconnected.
Panda heartbeat checks stay enabled; the live TTY prompts and mandated waits
refresh them at bounded intervals, so loss of the host falls back to SILENT.
The fixed allowlist contains TesterPresent and F186 in Classical and ISO CAN-FD
forms; the gated state machine emits at most three host submissions.
TesterPresent can refresh a transient session timer, but this tool never sends
flow control, enters a diagnostic session, requests security access, or invokes
any write/download/routine service.

Panda returned frames (source bus + 128) prove only host-to-controller queue
acceptance.  They are kept separate from native frames (source bus), rejected
frames (source bus + 192), and the per-phase CAN-health delta used to distinguish
a response/ACK-consistent transmission from AckError or CAN-core reset.  Panda
FDCAN can automatically retry one host submission multiple times on wire; the
tool cannot report an exact wire-attempt count.  Only a validated positive
TesterPresent reply gets exactly one same-format F186 follow-up, then probing
stops.  A validated negative TesterPresent proves the DCM executor and stops
without F186.  A positive F186 response identifies the application service;
NRC 0x31 is only boot-compatible under the exact retained tables.
"""

from __future__ import annotations

import argparse
import inspect
import json
import math
import select
import subprocess
import sys
import time
from collections.abc import Callable, Iterable
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from typing import Any

TX_ADDR = 0x7A1
RX_ADDR = 0x7A9
ELM327_SAFETY_MODE = 3
ELM327_NORMAL_ROUTE_PARAM = 1
SILENT_SAFETY_MODE = 0
NOOUTPUT_SAFETY_MODE = 19
NOMINAL_BITRATE_KBPS = 500
DATA_BITRATE_KBPS = 2000
RACK_ONLY_OHMS_RANGE = (108.0, 132.0)
COMPLETE_BUS_OHMS_RANGE = (54.0, 66.0)
CAN_TO_GROUND_MIN_OHMS = 200.0
CAN_TO_AUX_POSITIVE_MIN_OHMS = 6000.0
DEFAULT_BUS = 1
PHYSICAL_CAN_BUSES = (0, 1, 2)
DEFAULT_PASSIVE_SECONDS = 1.0
MIN_PASSIVE_SECONDS = 0.20
MAX_PASSIVE_SECONDS = 5.00
DEFAULT_SETTLE_SECONDS = 0.35
MIN_SETTLE_SECONDS = 0.20
MAX_SETTLE_SECONDS = 1.00
MAX_CAN_DRAIN_CALLS = 32
MAX_CAN_DRAIN_ROWS = 8192
VALID_CAN_DATA_LENGTHS = frozenset((*range(9), 12, 16, 20, 24, 32, 48, 64))
WATCHDOG_HEARTBEAT_INTERVAL_SECONDS = 0.5
MIN_SHUTDOWN_QUIET_SECONDS = 60.0
MIN_POST_DISCONNECT_SECONDS = 60.0
ARM_TOKEN = "A30_DOWNSTREAM_RACK_ONLY_READS"
AUX_RECONNECTED_TOKEN = "AUX_NEGATIVE_RECONNECTED_IG_OFF_A30_STILL_DISCONNECTED"
IGNITION_ON_TOKEN = "IG_ON_NOT_READY_A30_STILL_DISCONNECTED"
SHUTDOWN_TOKEN = "IG_OFF_1MIN_QUIET_AUX_NEGATIVE_DISCONNECTED_1MIN_WAIT_A30_STILL_DISCONNECTED"
IG_OFF_TOKEN = "IG_OFF_A30_STILL_DISCONNECTED_BEGIN_QUIET_WAIT"
AUX_NEGATIVE_DISCONNECTED_TOKEN = "AUX_NEGATIVE_DISCONNECTED_A30_STILL_DISCONNECTED_BEGIN_FINAL_WAIT"

TESTER_PRESENT_FRAME = bytes.fromhex("023e000000000000")
F186_FRAME = bytes.fromhex("0322f18600000000")

CAN_HEALTH_CUMULATIVE_FIELDS = (
    "bus_off_cnt",
    "total_error_cnt",
    "total_tx_lost_cnt",
    "total_rx_lost_cnt",
    "total_tx_cnt",
    "total_rx_cnt",
    "total_fwd_cnt",
    "total_tx_checksum_error_cnt",
    "can_core_reset_count",
)
ACK_ERROR_FIELDS = (
    "last_error",
    "last_stored_error",
    "last_data_error",
    "last_data_stored_error",
)
CAN_HEALTH_REQUIRED_FLAG_FIELDS = (
    "bus_off",
    "error_warning",
    "error_passive",
)
CAN_HEALTH_CONFIGURATION = {
    "can_speed": NOMINAL_BITRATE_KBPS,
    "can_data_speed": DATA_BITRATE_KBPS,
    "canfd_enabled": True,
    "brs_enabled": True,
    "canfd_non_iso": False,
}
PANDA_HEALTH_CUMULATIVE_FIELDS = (
    "safety_tx_blocked",
    "safety_rx_invalid",
    "tx_buffer_overflow",
    "rx_buffer_overflow",
)


class ProbeError(RuntimeError):
    """Fail-closed error for an invalid plan, topology, or Panda state."""


@dataclass(frozen=True)
class TxPhase:
    name: str
    service: str
    data: bytes
    fd: bool


TX_PHASES = (
    TxPhase("tester-present-classical", "TesterPresent 0x3E00", TESTER_PRESENT_FRAME, False),
    TxPhase("f186-classical", "ReadDataByIdentifier 0xF186", F186_FRAME, False),
    TxPhase("tester-present-fd", "TesterPresent 0x3E00", TESTER_PRESENT_FRAME, True),
    TxPhase("f186-fd", "ReadDataByIdentifier 0xF186", F186_FRAME, True),
)
TX_FORMAT_PHASES = (
    (TX_PHASES[0], TX_PHASES[1]),
    (TX_PHASES[2], TX_PHASES[3]),
)


@dataclass(frozen=True)
class PhysicalPreflight:
    a30_disconnected: bool
    a30_mating_connector_correct_terminals_no_backprobe_no_piercing_no_generic_pin: bool
    stationary: bool
    parking_brake_set: bool
    level_ground: bool
    wheel_chocks: bool
    foot_off_brake: bool
    probe_will_use_ignition_on_not_ready: bool
    ignition_off_now: bool
    auxiliary_battery_negative_disconnected_now: bool
    usb_host_battery_powered_not_vehicle_or_mains: bool
    rack_only_peer: bool
    common_ground: bool
    dc1_polarity_verified: bool
    resistance_measured_power_off: bool
    battery_negative_disconnected_for_isolation_checks: bool
    meter_removed: bool
    openpilot_stopped: bool
    rack_only_ohms: float | None
    complete_bus_ohms: float | None
    dc1h_to_ground_ohms: float | None
    dc1l_to_ground_ohms: float | None
    dc1h_to_aux_positive_ohms: float | None
    dc1l_to_aux_positive_ohms: float | None
    external_can1_termination_installed: bool
    unused_can1_pass_through_unconnected: bool
    only_can1_connected: bool
    arm: str | None


def _resistance_in_range(value: float | None, bounds: tuple[float, float]) -> bool:
    return value is not None and math.isfinite(value) and bounds[0] <= value <= bounds[1]


def _resistance_at_least(value: float | None, minimum: float) -> bool:
    return value is not None and math.isfinite(value) and value >= minimum


def _validate_runtime_parameters(bus: int, settle_seconds: float, passive_seconds: float) -> None:
    if type(bus) is not int or bus != DEFAULT_BUS:
        raise ProbeError(
            "isolated probe is fixed to logical bus 1; buses 0/2 can swap physical controllers"
        )
    for name, value, minimum, maximum in (
        ("settle interval", settle_seconds, MIN_SETTLE_SECONDS, MAX_SETTLE_SECONDS),
        ("passive interval", passive_seconds, MIN_PASSIVE_SECONDS, MAX_PASSIVE_SECONDS),
    ):
        if (
            not isinstance(value, (int, float))
            or isinstance(value, bool)
            or not math.isfinite(value)
            or not minimum <= value <= maximum
        ):
            raise ProbeError(f"{name} must be between {minimum:g} and {maximum:g} seconds")


def validate_preflight(preflight: PhysicalPreflight, bus: int) -> None:
    """Validate every physical gate before importing or opening Panda."""
    missing: list[str] = []
    if type(bus) is not int or bus != DEFAULT_BUS:
        missing.append("--bus 1 (the only orientation-stable isolated route)")
    confirmations = (
        (preflight.a30_disconnected, "--confirm-a30-disconnected"),
        (
            preflight.a30_mating_connector_correct_terminals_no_backprobe_no_piercing_no_generic_pin,
            "--confirm-a30-mating-connector-correct-terminals-no-backprobe-no-piercing-no-generic-pin",
        ),
        (preflight.stationary, "--confirm-stationary"),
        (preflight.parking_brake_set, "--confirm-parking-brake-set"),
        (preflight.level_ground, "--confirm-level-ground"),
        (preflight.wheel_chocks, "--confirm-wheel-chocks"),
        (preflight.foot_off_brake, "--confirm-foot-off-brake"),
        (
            preflight.probe_will_use_ignition_on_not_ready,
            "--confirm-probe-will-use-ignition-on-not-ready",
        ),
        (preflight.ignition_off_now, "--confirm-ignition-off-now"),
        (
            preflight.auxiliary_battery_negative_disconnected_now,
            "--confirm-auxiliary-battery-negative-disconnected-now",
        ),
        (
            preflight.usb_host_battery_powered_not_vehicle_or_mains,
            "--confirm-usb-host-battery-powered-not-vehicle-or-mains",
        ),
        (preflight.rack_only_peer, "--confirm-rack-only-peer"),
        (preflight.common_ground, "--confirm-common-ground"),
        (preflight.dc1_polarity_verified, "--confirm-dc1h-dc1l-polarity"),
        (preflight.resistance_measured_power_off, "--confirm-resistance-measured-power-off"),
        (
            preflight.battery_negative_disconnected_for_isolation_checks,
            "--confirm-battery-negative-was-disconnected-for-isolation-checks",
        ),
        (preflight.meter_removed, "--confirm-meter-removed"),
        (
            preflight.external_can1_termination_installed,
            "--confirm-external-can1-120-ohm-termination",
        ),
        (
            preflight.unused_can1_pass_through_unconnected,
            "--confirm-unused-can1-pass-through-unconnected",
        ),
        (preflight.only_can1_connected, "--confirm-only-can1-connected"),
        (preflight.openpilot_stopped, "--confirm-openpilot-stopped"),
    )
    missing.extend(flag for confirmed, flag in confirmations if not confirmed)
    if preflight.arm != ARM_TOKEN:
        missing.append(f"--arm {ARM_TOKEN}")
    if not _resistance_in_range(preflight.rack_only_ohms, RACK_ONLY_OHMS_RANGE):
        missing.append(
            f"--rack-only-ohms within {RACK_ONLY_OHMS_RANGE[0]:g}..{RACK_ONLY_OHMS_RANGE[1]:g}"
        )
    if not _resistance_in_range(preflight.complete_bus_ohms, COMPLETE_BUS_OHMS_RANGE):
        missing.append(
            f"--complete-bus-ohms within {COMPLETE_BUS_OHMS_RANGE[0]:g}..{COMPLETE_BUS_OHMS_RANGE[1]:g}"
        )
    isolation_readings = (
        (preflight.dc1h_to_ground_ohms, CAN_TO_GROUND_MIN_OHMS, "--dc1h-to-ground-ohms"),
        (preflight.dc1l_to_ground_ohms, CAN_TO_GROUND_MIN_OHMS, "--dc1l-to-ground-ohms"),
        (
            preflight.dc1h_to_aux_positive_ohms,
            CAN_TO_AUX_POSITIVE_MIN_OHMS,
            "--dc1h-to-aux-positive-ohms",
        ),
        (
            preflight.dc1l_to_aux_positive_ohms,
            CAN_TO_AUX_POSITIVE_MIN_OHMS,
            "--dc1l-to-aux-positive-ohms",
        ),
    )
    for value, minimum, flag in isolation_readings:
        if not _resistance_at_least(value, minimum):
            missing.append(f"{flag} >= {minimum:g}")
    if missing:
        raise ProbeError("live execution preflight failed; missing/invalid: " + ", ".join(missing))


def assert_allowed_tx(bus: int, address: int, data: bytes, fd: bool) -> None:
    """Mode/liveness allowlist immediately in front of the sole TX call."""
    allowed = {(phase.data, phase.fd) for phase in TX_PHASES}
    if (
        type(bus) is not int
        or bus != DEFAULT_BUS
        or address != TX_ADDR
        or not isinstance(fd, bool)
        or (bytes(data), fd) not in allowed
    ):
        raise ProbeError(
            f"TX blocked outside fixed mode/liveness allowlist: bus={bus!r} "
            f"addr=0x{address:X} data={bytes(data).hex()} fd={fd}"
        )


def _phase_json(phase: TxPhase) -> dict[str, object]:
    return {
        "name": phase.name,
        "service": phase.service,
        "address": f"0x{TX_ADDR:03X}",
        "data_hex": phase.data.hex(),
        "fd": phase.fd,
        "brs": phase.fd,
    }


def build_plan(
    bus: int = DEFAULT_BUS,
    settle_seconds: float = DEFAULT_SETTLE_SECONDS,
    passive_seconds: float = DEFAULT_PASSIVE_SECONDS,
) -> dict[str, object]:
    _validate_runtime_parameters(bus, settle_seconds, passive_seconds)
    return {
        "schema": "toyota-eps-isolated-can-probe-v1",
        "target_segment": "A30 disconnected; downstream DC1H/DC1L to C50 EPS only",
        "route": {
            "panda_bus": bus,
            "controller": "FDCAN2 / logical bus 1; not swapped by harness orientation",
            "can0_can2_intercept_relay": (
                "no direct/debug control; SILENT/NOOUTPUT/ELM use Panda default pass-through, "
                "with CAN0/CAN2 physically unconnected"
            ),
            "physical_topology": (
                "standalone USB Panda CAN1 endpoint; unused CAN1 pass-through physically unconnected"
            ),
            "termination": "external/interface-side 120 ohm required",
            "phase_reset": (
                "clear queues/reset CAN during pre-power NOOUTPUT setup; after passive capture, the "
                "single NOOUTPUT-to-ELM safety transition reinitializes CAN and the tool reapplies its "
                "configuration without clearing RX; thereafter preserve live RX and require an empty, "
                "counter-stable pre-TX drain barrier at every phase"
            ),
        },
        "can": {
            "nominal_kbps": NOMINAL_BITRATE_KBPS,
            "data_kbps": DATA_BITRATE_KBPS,
            "canfd_non_iso": False,
            "canfd_auto": False,
            "controller_loopback": False,
            "explicit_frame_format": True,
        },
        "tx_phases": [_phase_json(phase) for phase in TX_PHASES],
        "max_host_submissions": 3,
        "state_machine": (
            "TesterPresent Classical; only a validated positive 7E00 reply plus complete clean "
            "controller/Panda health permits one Classical F186, then stop. Validated negative 7F/3E "
            "stops without F186. FD TesterPresent fallback is allowed only after clean ACK-consistent "
            "Classical silence or clean unmatched native peer traffic. Rejection, missing TX receipt, "
            "health/schema error, link/controller fault, core reset, RX loss, or overflow stops all TX."
        ),
        "automatic_retransmission": (
            "Panda FDCAN can retry each host submission on wire until ACK or error recovery; "
            "exact wire-attempt count is unavailable"
        ),
        "submission_accounting": (
            "record each phase before entering can_send; count normal API returns as confirmed host "
            "submissions and retain every API entry as the upper bound after an ambiguous exception"
        ),
        "host_failure": (
            "Panda heartbeat checks remain enabled; interactive prompts, passive/response waits, "
            "and shutdown waits refresh the watchdog every 0.5 seconds, so host/process loss falls "
            "back to SILENT"
        ),
        "early_stop": (
            "a validated positive TesterPresent reply permits exactly the following same-format F186 "
            "request, then stops even if F186 is silent; a validated negative TesterPresent stops "
            "without F186; any validated F186 reply stops"
        ),
        "passive_listen": {
            "settle_seconds_after_each_transition": passive_seconds,
            "transitions": ["aux-negative reconnect with IG OFF", "IG ON / not READY"],
            "panda_safety": "NOOUTPUT (host data frames blocked; protocol ACK bits enabled)",
            "tx_count": 0,
            "collection": (
                "baseline before each prompt through post-attestation settle; drain direct USB "
                "through its empty transfer, then reconcile native rows for all three physical "
                "controllers to their own RX deltas and recheck every counter snapshot"
            ),
            "loss_policy": (
                "any controller/Panda fault or drift, off-bus controller activity, unexpected host "
                "TX receipt, controller RX loss, or Panda RX overflow stops before active TX"
            ),
        },
        "settle_seconds_per_phase": settle_seconds,
        "preflight": {
            "arm_token": ARM_TOKEN,
            "rack_only_ohms": {
                "min": RACK_ONLY_OHMS_RANGE[0],
                "max": RACK_ONLY_OHMS_RANGE[1],
                "when": "A30 and tester disconnected, all vehicle/tester power off",
            },
            "complete_bus_ohms": {
                "min": COMPLETE_BUS_OHMS_RANGE[0],
                "max": COMPLETE_BUS_OHMS_RANGE[1],
                "when": "tester termination connected, all vehicle/tester power off",
            },
            "a30_34_dc1h_to_body_ground_ohms": {
                "min": CAN_TO_GROUND_MIN_OHMS,
                "when": "A30 disconnected and auxiliary-battery negative disconnected",
            },
            "a30_35_dc1l_to_body_ground_ohms": {
                "min": CAN_TO_GROUND_MIN_OHMS,
                "when": "A30 disconnected and auxiliary-battery negative disconnected",
            },
            "a30_34_dc1h_to_aux_positive_ohms": {
                "min": CAN_TO_AUX_POSITIVE_MIN_OHMS,
                "when": "A30 disconnected and auxiliary-battery negative disconnected",
            },
            "a30_35_dc1l_to_aux_positive_ohms": {
                "min": CAN_TO_AUX_POSITIVE_MIN_OHMS,
                "when": "A30 disconnected and auxiliary-battery negative disconnected",
            },
            "meter": "remove before reconnecting auxiliary-battery negative and before IG ON",
            "power_sequence": (
                "start IG OFF with auxiliary negative disconnected; configure independently powered "
                "Panda NOOUTPUT; interactively reconnect negative with IG OFF; then IG ON, never READY"
            ),
            "usb_power": (
                "Panda host must be battery-powered, not vehicle-powered or mains-powered, to avoid a "
                "second power/ground path while auxiliary negative is disconnected"
            ),
            "immobilization": "level ground, parking brake set, wheels chocked, foot off brake",
            "a30_connection": (
                "correct mating connector/terminals only; no backprobe, insulation piercing, or generic pin"
            ),
            "common_ground_required": True,
            "openpilot_must_be_stopped": True,
        },
        "rx_accounting": {
            "native": f"source {bus}",
            "tx_echo": f"source {bus + 128}; queue acceptance only",
            "tx_rejected": f"source {bus + 192}",
            "wire_format_limit": "Panda tuple RX does not retain an FDF/BRS field",
            "loss_counters": (
                "all physical-controller cumulative schemas/deltas, selected-controller "
                "total_rx_lost_cnt, and Panda rx_buffer_overflow"
            ),
            "tx_receipt_gate": (
                "exactly one source bus+128 echo matching 0x7A1/current payload and total_tx_cnt delta 1"
            ),
            "bounded_drain": (
                f"up to {MAX_CAN_DRAIN_CALLS} can_recv calls/{MAX_CAN_DRAIN_ROWS} rows; native rows must "
                "reconcile exactly to each physical controller's total_rx_cnt delta, and late RX/TX "
                "counter movement forces another drain or invalidates the phase"
            ),
        },
        "ack_discriminator": {
            "inputs": [
                "phase-matched native 0x7A9 UDS response",
                "AckError in LEC/DLEC fields",
                "transmit error counter",
                "bus-off/error cumulative deltas",
                "CAN-core reset cumulative delta",
                "controller RX-loss and Panda RX-overflow deltas",
                "Panda safety/fault/power/counter/uptime stability",
                "CAN REC/configuration/forwarding stability",
                "absence of any competing/stale source outside standalone CAN1",
                "absence of a native 0x7A1 mirror of the host request (internal-loopback guard)",
            ],
            "boundary": (
                "Only an exact phase-matched response confirms the DCM executor. An unmatched native "
                "0x7A9 proves only peer/frame activity. A native mirror of the 0x7A1 request invalidates "
                "the phase as possible internal loopback. Otherwise complete clean health is merely "
                "ACK-consistent; a Panda TX echo alone is never called physical ACK."
            ),
        },
        "mode_classification": {
            "application": "04 62 F1 86 <session>: exact application current-session producer",
            "boot_compatible": (
                "03 7F 22 31: F186 is absent from the exact boot readable-DID table; this is "
                "boot-compatible, not boot proof"
            ),
            "unknown": "another NRC, silence, or malformed response does not identify software mode",
            "restore_authorization": False,
        },
        "forbidden": [
            "DiagnosticSessionControl",
            "SecurityAccess",
            "WriteDataByIdentifier",
            "RoutineControl",
            "RequestDownload",
            "TransferData",
            "RequestTransferExit",
            "flow-control TX",
            "functional-address TX",
            "any CAN ID other than 0x7A1",
        ],
        "shutdown": (
            "tool restores NOOUTPUT first; live execution separately attests power switch/IG OFF, "
            "enforces at least 60 seconds with no key/door/pedal activity, separately attests "
            "auxiliary-battery-negative disconnection, and enforces at least 60 more seconds before "
            "SILENT/close or A30 handling while refreshing the enabled Panda watchdog "
            "(PIG remains supplied while only IG is off)."
        ),
    }


def _plain_mapping(raw: Any) -> dict[str, Any]:
    if hasattr(raw, "_asdict"):
        raw = raw._asdict()
    if not isinstance(raw, dict):
        return {"repr": repr(raw)}
    return {
        str(key): value if value is None or isinstance(value, (bool, int, float, str)) else repr(value)
        for key, value in raw.items()
    }


def _snapshot_all_can_health(panda: Any) -> dict[int, dict[str, Any]]:
    return {
        controller_bus: _plain_mapping(panda.can_health(controller_bus))
        for controller_bus in PHYSICAL_CAN_BUSES
    }


def _all_can_counter_signature(
    all_health: dict[int, dict[str, Any]],
) -> tuple[tuple[int, str, object], ...]:
    return tuple(
        (controller_bus, field, all_health.get(controller_bus, {}).get(field))
        for controller_bus in PHYSICAL_CAN_BUSES
        for field in CAN_HEALTH_CUMULATIVE_FIELDS
    )


def _panda_counter_signature(panda_health: dict[str, Any]) -> tuple[tuple[str, object], ...]:
    return tuple(
        (field, panda_health.get(field)) for field in PANDA_HEALTH_CUMULATIVE_FIELDS
    )


def can_health_delta(before: dict[str, Any], after: dict[str, Any]) -> dict[str, int]:
    return {
        key: (int(after[key]) - int(before[key])) & 0xFFFFFFFF
        for key in CAN_HEALTH_CUMULATIVE_FIELDS
        if isinstance(before.get(key), (bool, int)) and isinstance(after.get(key), (bool, int))
    }


def classify_frames(
    rows: Iterable[tuple[int, bytes, int]], bus: int
) -> dict[str, list[dict[str, object]]]:
    out: dict[str, list[dict[str, object]]] = {
        "native": [],
        "tx_echo": [],
        "tx_rejected": [],
        "other_source": [],
    }
    for address, data, source in rows:
        row = {
            "address": f"0x{int(address):03X}",
            "data_hex": bytes(data).hex(),
            "source": int(source),
        }
        if source == bus:
            out["native"].append(row)
        elif source == bus + 128:
            out["tx_echo"].append(row)
        elif source == bus + 192:
            out["tx_rejected"].append(row)
        else:
            out["other_source"].append(row)
    return out


def _is_ack_error(value: object) -> bool:
    return isinstance(value, str) and value.casefold().replace(" ", "") == "ackerror"


def _is_clean_lec(value: object) -> bool:
    return isinstance(value, str) and value.casefold().replace(" ", "") in {
        "noerror",
        "nochange",
    }


def _lec_transition_is_error(before: object, after: object) -> bool:
    if _is_clean_lec(before) and _is_clean_lec(after):
        return False
    return before != after


def _single_frame_payload(data: bytes) -> tuple[bytes, bool] | None:
    raw = bytes(data)
    if not raw or len(raw) not in VALID_CAN_DATA_LENGTHS or raw[0] & 0xF0:
        return None
    payload_length = raw[0] & 0x0F
    payload_offset = 1
    extended = False
    if payload_length == 0:
        if len(raw) <= 8:
            return None
        payload_length = raw[1]
        payload_offset = 2
        extended = True
    elif len(raw) > 8:
        return None
    if payload_length == 0 or payload_offset + payload_length > len(raw):
        return None
    return raw[payload_offset : payload_offset + payload_length], extended


def classify_f186_mode_response(data: bytes) -> str | None:
    """Classify the exact F33 read-only application/boot distinction."""
    single_frame = _single_frame_payload(bytes(data))
    if single_frame is None:
        return None
    payload, _extended = single_frame
    if len(payload) == 4 and payload[:3] == bytes.fromhex("62f186"):
        session = payload[3]
        session_name = {1: "default", 2: "programming", 3: "extended"}.get(
            session,
            f"unknown-0x{session:02x}",
        )
        return f"application-{session_name}-session"
    if len(payload) == 3 and payload[:2] == bytes.fromhex("7f22"):
        if payload[2] == 0x31:
            return "boot-compatible-unknown-did"
        return f"negative-nrc-0x{payload[2]:02x}-mode-unknown"
    return None


def classify_phase_response(request_data: bytes, response_data: bytes) -> str | None:
    """Validate only the bounded ISO-TP/UDS replies for the current request."""
    raw = bytes(response_data)
    single_frame = _single_frame_payload(raw)
    payload = single_frame[0] if single_frame is not None else None
    if bytes(request_data) == TESTER_PRESENT_FRAME:
        if payload == bytes.fromhex("7e00"):
            return "tester-present-positive"
        if payload is not None and len(payload) == 3 and payload[:2] == bytes.fromhex("7f3e"):
            return "tester-present-negative"
        return None
    if bytes(request_data) != F186_FRAME:
        return None
    if payload is not None and len(payload) == 4 and payload[:3] == bytes.fromhex("62f186"):
        return "f186-positive"
    if payload is not None and len(payload) == 3 and payload[:2] == bytes.fromhex("7f22"):
        return "f186-negative"
    return None


def _can_health_contract_errors(
    health_before: dict[str, Any],
    health_after: dict[str, Any],
) -> list[str]:
    errors: list[str] = []
    for label, health in (("before", health_before), ("after", health_after)):
        for field in (*CAN_HEALTH_CUMULATIVE_FIELDS, "transmit_error_cnt"):
            value = health.get(field)
            if not isinstance(value, int) or isinstance(value, bool) or value < 0:
                errors.append(f"{label}.{field}={value!r}")
        for field in CAN_HEALTH_REQUIRED_FLAG_FIELDS:
            value = health.get(field)
            if value not in (False, True, 0, 1):
                errors.append(f"{label}.{field}={value!r}")
        for field in ACK_ERROR_FIELDS:
            value = health.get(field)
            if not isinstance(value, str):
                errors.append(f"{label}.{field}={value!r}")
        value = health.get("receive_error_cnt")
        if not isinstance(value, int) or isinstance(value, bool) or value < 0:
            errors.append(f"{label}.receive_error_cnt={value!r}")
        for field in ("can_speed", "can_data_speed"):
            value = health.get(field)
            if not isinstance(value, int) or isinstance(value, bool) or value < 0:
                errors.append(f"{label}.{field}={value!r}")
        for field in ("canfd_enabled", "brs_enabled", "canfd_non_iso"):
            value = health.get(field)
            if value not in (False, True, 0, 1):
                errors.append(f"{label}.{field}={value!r}")
    return errors


def _panda_health_contract_errors(
    panda_health_before: dict[str, Any],
    panda_health_after: dict[str, Any],
) -> list[str]:
    errors: list[str] = []
    for label, health in (("before", panda_health_before), ("after", panda_health_after)):
        for field in (
            *PANDA_HEALTH_CUMULATIVE_FIELDS,
            "uptime",
            "faults",
            "fault_status",
            "safety_mode",
            "safety_param",
            "car_harness_status",
        ):
            value = health.get(field)
            if not isinstance(value, int) or isinstance(value, bool) or value < 0:
                errors.append(f"{label}.{field}={value!r}")
        for field in ("heartbeat_lost", "power_save_enabled", "safety_rx_checks_invalid"):
            value = health.get(field)
            if value not in (False, True, 0, 1):
                errors.append(f"{label}.{field}={value!r}")
    return errors


def _counter_delta_mod32(before: dict[str, Any], after: dict[str, Any], field: str) -> int | None:
    before_value = before.get(field)
    after_value = after.get(field)
    if (
        not isinstance(before_value, int)
        or isinstance(before_value, bool)
        or not isinstance(after_value, int)
        or isinstance(after_value, bool)
    ):
        return None
    return (after_value - before_value) & 0xFFFFFFFF


def _panda_health_delta(
    before: dict[str, Any],
    after: dict[str, Any],
) -> dict[str, int]:
    return {
        field: delta
        for field in PANDA_HEALTH_CUMULATIVE_FIELDS
        if (delta := _counter_delta_mod32(before, after, field)) is not None
    }


def _panda_runtime_issues(
    before: dict[str, Any],
    after: dict[str, Any],
    *,
    expected_safety_mode: int,
    expected_safety_param: int,
) -> tuple[list[str], dict[str, int], bool]:
    issues: list[str] = []
    delta = _panda_health_delta(before, after)
    for label, health in (("before", before), ("after", after)):
        if health.get("safety_mode") != expected_safety_mode:
            issues.append(f"{label} safety_mode={health.get('safety_mode')!r}")
        if health.get("safety_param") != expected_safety_param:
            issues.append(f"{label} safety_param={health.get('safety_param')!r}")
        if health.get("heartbeat_lost") not in (False, 0):
            issues.append(f"{label} heartbeat_lost={health.get('heartbeat_lost')!r}")
        if health.get("power_save_enabled") not in (False, 0):
            issues.append(f"{label} power_save_enabled={health.get('power_save_enabled')!r}")
        if health.get("faults") != 0:
            issues.append(f"{label} faults={health.get('faults')!r}")
        if health.get("fault_status") != 0:
            issues.append(f"{label} fault_status={health.get('fault_status')!r}")
        if health.get("safety_rx_checks_invalid") not in (False, 0):
            issues.append(
                f"{label} safety_rx_checks_invalid={health.get('safety_rx_checks_invalid')!r}"
            )
    for field in PANDA_HEALTH_CUMULATIVE_FIELDS:
        if delta.get(field, 0) != 0:
            issues.append(f"{field} delta={delta.get(field)!r}")
    uptime_before = before.get("uptime")
    uptime_after = after.get("uptime")
    uptime_reset = (
        isinstance(uptime_before, int)
        and not isinstance(uptime_before, bool)
        and isinstance(uptime_after, int)
        and not isinstance(uptime_after, bool)
        and uptime_after < uptime_before
    )
    if uptime_reset:
        issues.append(f"uptime reset: {uptime_before!r}->{uptime_after!r}")
    if before.get("car_harness_status") != after.get("car_harness_status"):
        issues.append(
            f"car_harness_status drift: {before.get('car_harness_status')!r}->"
            f"{after.get('car_harness_status')!r}"
        )
    return issues, delta, uptime_reset


def _can_configuration_issues(
    before: dict[str, Any],
    after: dict[str, Any],
) -> list[str]:
    issues: list[str] = []
    for label, health in (("before", before), ("after", after)):
        for field, expected in CAN_HEALTH_CONFIGURATION.items():
            value = health.get(field)
            if value != expected:
                issues.append(f"{label} {field}={value!r}, expected {expected!r}")
        if health.get("receive_error_cnt") != 0:
            issues.append(f"{label} receive_error_cnt={health.get('receive_error_cnt')!r}")
    return issues


def assess_phase(
    frames: dict[str, list[dict[str, object]]],
    health_before: dict[str, Any],
    health_after: dict[str, Any],
    *,
    request_data: bytes,
    panda_health_before: dict[str, Any],
    panda_health_after: dict[str, Any],
    drain_complete: bool = True,
    drain_errors: Iterable[str] = (),
) -> dict[str, object]:
    native_responses = [
        row for row in frames["native"] if row["address"].casefold() == f"0x{RX_ADDR:03X}".casefold()
    ]
    matched_responses = [
        (row, classification)
        for row in native_responses
        if (
            classification := classify_phase_response(
                request_data,
                bytes.fromhex(str(row["data_hex"])),
            )
        )
        is not None
    ]
    mode_classes = [
        classification
        for row, _response_kind in matched_responses
        if (
            classification := classify_f186_mode_response(
                bytes.fromhex(str(row["data_hex"]))
            )
        )
        is not None
    ]
    response_count_unambiguous = len(matched_responses) <= 1
    health_contract_errors = _can_health_contract_errors(health_before, health_after)
    panda_health_contract_errors = _panda_health_contract_errors(
        panda_health_before,
        panda_health_after,
    )
    all_health_contract_errors = health_contract_errors + panda_health_contract_errors
    delta = can_health_delta(health_before, health_after)
    panda_runtime_issues, panda_delta, panda_uptime_reset = _panda_runtime_issues(
        panda_health_before,
        panda_health_after,
        expected_safety_mode=ELM327_SAFETY_MODE,
        expected_safety_param=ELM327_NORMAL_ROUTE_PARAM,
    )
    can_configuration_issues = _can_configuration_issues(health_before, health_after)
    rx_buffer_overflow_delta = _counter_delta_mod32(
        panda_health_before,
        panda_health_after,
        "rx_buffer_overflow",
    )
    rejected = bool(frames["tx_rejected"])
    topology_contaminated = bool(frames["other_source"])
    native_tx_mirrors = [
        row
        for row in frames["native"]
        if row["address"].casefold() == f"0x{TX_ADDR:03X}".casefold()
        and row["data_hex"].casefold() == bytes(request_data).hex()
    ]
    internal_loopback_suspected = bool(native_tx_mirrors)
    matching_tx_echoes = [
        row
        for row in frames["tx_echo"]
        if row["address"].casefold() == f"0x{TX_ADDR:03X}".casefold()
        and row["data_hex"].casefold() == bytes(request_data).hex()
    ]
    tx_delta = delta.get("total_tx_cnt")
    host_tx_receipt_confirmed = (
        len(frames["tx_echo"]) == 1
        and len(matching_tx_echoes) == 1
        and tx_delta == 1
    )
    tx_receipt_errors: list[str] = []
    if len(frames["tx_echo"]) != 1:
        tx_receipt_errors.append(f"tx_echo_count={len(frames['tx_echo'])}, expected 1")
    if len(matching_tx_echoes) != 1:
        tx_receipt_errors.append(
            f"matching_tx_echo_count={len(matching_tx_echoes)}, expected 1"
        )
    if tx_delta != 1:
        tx_receipt_errors.append(f"total_tx_cnt_delta={tx_delta!r}, expected 1")
    expected_native_rx_count = delta.get("total_rx_cnt")
    observed_native_rx_count = len(frames["native"])
    native_rx_reconciled = expected_native_rx_count == observed_native_rx_count
    drain_errors_out = list(drain_errors)

    common: dict[str, object] = {
        "native_eps_frame_count": len(native_responses),
        "matched_diagnostic_response_count": len(matched_responses),
        "unmatched_native_eps_frame_count": len(native_responses) - len(matched_responses),
        "diagnostic_response_kinds": [kind for _row, kind in matched_responses],
        # Syntax is retained even when the surrounding capture is not trusted.
        # The singular classification below is populated only after the entire
        # phase (receipt, topology, drain, and health) has validated.
        "f186_response_syntax_classifications": mode_classes,
        "f186_mode_classification": None,
        "matched_diagnostic_response_count_unambiguous": response_count_unambiguous,
        "restore_authorized": False,
        "tx_echo_count": len(frames["tx_echo"]),
        "matching_tx_echo_count": len(matching_tx_echoes),
        "host_tx_receipt_confirmed": host_tx_receipt_confirmed,
        "tx_receipt_errors": tx_receipt_errors,
        "tx_rejected_count": len(frames["tx_rejected"]),
        "other_source_frame_count": len(frames["other_source"]),
        "topology_contaminated": topology_contaminated,
        "native_tx_mirror_count": len(native_tx_mirrors),
        "internal_loopback_suspected": internal_loopback_suspected,
        "expected_native_rx_count_mod32": expected_native_rx_count,
        "observed_native_rx_count": observed_native_rx_count,
        "native_rx_reconciled": native_rx_reconciled,
        "drain_complete": drain_complete,
        "drain_errors": drain_errors_out,
        "can_health_delta_mod32": delta,
        "panda_health_delta_mod32": panda_delta,
        "panda_rx_buffer_overflow_delta_mod32": rx_buffer_overflow_delta,
        "can_health_contract_errors": health_contract_errors,
        "panda_health_contract_errors": panda_health_contract_errors,
        "can_configuration_issues": can_configuration_issues,
        "panda_runtime_issues": panda_runtime_issues,
        "panda_uptime_reset": panda_uptime_reset,
    }

    if all_health_contract_errors:
        if rejected:
            verdict = "host-safety-rejected"
            ack = "not-transmitted"
        elif matched_responses:
            verdict = "can-health-incomplete"
            ack = "confirmed-by-native-response-health-incomplete"
        else:
            verdict = "can-health-incomplete"
            ack = "indeterminate"
        return {
            **common,
            "verdict": verdict,
            "wire_ack": ack,
            "controller_health_clean": False,
            "panda_health_clean": False,
            "phase_evidence_valid": False,
            "fd_fallback_eligible": False,
            "new_ack_error": None,
            "new_controller_error": None,
            "reported_controller_error": None,
            "controller_error_field_changed": None,
            "transmit_error_count_before": None,
            "transmit_error_count_after": None,
            "can_core_reset": None,
            "bus_off": None,
            "can_rx_evidence_lost": None,
        }

    ack_error_now = any(_is_ack_error(health_after[field]) for field in ACK_ERROR_FIELDS)
    transmit_error_before = int(health_before["transmit_error_cnt"])
    transmit_error_after = int(health_after["transmit_error_cnt"])
    new_ack_error = ack_error_now and (
        delta.get("total_error_cnt", 0) != 0
        or transmit_error_after != transmit_error_before
        or delta.get("can_core_reset_count", 0) != 0
        or not any(_is_ack_error(health_before[field]) for field in ACK_ERROR_FIELDS)
    )
    core_reset = delta.get("can_core_reset_count", 0) != 0
    bus_off = delta["bus_off_cnt"] != 0 or bool(health_after["bus_off"])
    can_rx_evidence_lost = (
        delta["total_rx_lost_cnt"] != 0
        or rx_buffer_overflow_delta is None
        or rx_buffer_overflow_delta != 0
    )
    controller_error_field_changed = any(
        _lec_transition_is_error(health_before[field], health_after[field])
        for field in ACK_ERROR_FIELDS
    )
    new_controller_error = any(
        delta.get(field, 0) != 0
        for field in (
            "total_error_cnt",
            "total_tx_lost_cnt",
            "total_tx_checksum_error_cnt",
            "can_core_reset_count",
            "total_fwd_cnt",
        )
    ) or transmit_error_after != transmit_error_before or controller_error_field_changed
    reported_controller_error = any(
        not _is_clean_lec(health_after[field])
        for field in ("last_error", "last_data_error")
    )
    controller_health_clean = not (
        new_ack_error
        or core_reset
        or bus_off
        or new_controller_error
        or reported_controller_error
        or transmit_error_before != 0
        or transmit_error_after != 0
        or bool(health_after["error_warning"])
        or bool(health_after["error_passive"])
        or can_rx_evidence_lost
        or can_configuration_issues
    )
    panda_health_clean = not panda_runtime_issues
    if rejected:
        verdict = "host-safety-rejected"
        ack = "not-transmitted"
    elif internal_loopback_suspected:
        verdict = "internal-loopback-or-self-receive"
        ack = "indeterminate-due-to-native-request-mirror"
    elif topology_contaminated:
        verdict = "unexpected-source-topology-contamination"
        ack = "indeterminate-due-to-competing-or-stale-source"
    elif not drain_complete or not native_rx_reconciled:
        verdict = "native-rx-evidence-unreconciled"
        ack = "indeterminate-due-to-uncollected-rx-evidence"
    elif can_rx_evidence_lost:
        verdict = "can-rx-evidence-loss-or-overflow"
        ack = "indeterminate-due-to-rx-evidence-loss"
    elif panda_runtime_issues:
        verdict = "panda-health-fault-or-drift"
        ack = "indeterminate-due-to-panda-health"
    elif can_configuration_issues:
        verdict = "can-configuration-or-receive-health-drift"
        ack = "indeterminate-due-to-can-configuration"
    elif new_ack_error or core_reset or bus_off:
        verdict = "ack-error-or-link-fault"
        ack = (
            "confirmed-by-native-response-with-controller-fault"
            if matched_responses
            else "not-observed"
        )
    elif new_controller_error or bool(health_after["error_warning"]) or bool(health_after["error_passive"]):
        verdict = "can-controller-error-or-link-fault"
        ack = (
            "confirmed-by-native-response-with-controller-fault"
            if matched_responses
            else "not-observed"
        )
    elif not response_count_unambiguous:
        verdict = "multiple-matched-diagnostic-responses"
        ack = "indeterminate-due-to-duplicate-or-stale-response"
    elif matched_responses:
        verdict = "matched-eps-diagnostic-response"
        ack = "confirmed-by-native-response"
    elif native_responses:
        verdict = "native-eps-frame-diagnostic-unmatched"
        ack = "request-ack-indeterminate"
    elif host_tx_receipt_confirmed and controller_health_clean and panda_health_clean:
        verdict = "ack-consistent-no-eps-response"
        ack = "inferred-from-clean-controller-health"
    elif frames["tx_echo"]:
        verdict = "tx-queued-health-indeterminate"
        ack = "indeterminate"
    else:
        verdict = "no-tx-receipt"
        ack = "indeterminate"

    phase_evidence_valid = (
        not rejected
        and not internal_loopback_suspected
        and not topology_contaminated
        and host_tx_receipt_confirmed
        and native_rx_reconciled
        and drain_complete
        and controller_health_clean
        and panda_health_clean
        and response_count_unambiguous
    )
    validated_mode = (
        mode_classes[0]
        if phase_evidence_valid
        and verdict == "matched-eps-diagnostic-response"
        and len(mode_classes) == 1
        else None
    )
    return {
        **common,
        "f186_mode_classification": validated_mode,
        "verdict": verdict,
        "wire_ack": ack,
        "controller_health_clean": controller_health_clean,
        "panda_health_clean": panda_health_clean,
        "phase_evidence_valid": phase_evidence_valid,
        "fd_fallback_eligible": not rejected
        and not internal_loopback_suspected
        and not topology_contaminated
        and host_tx_receipt_confirmed
        and native_rx_reconciled
        and drain_complete
        and controller_health_clean
        and panda_health_clean
        and response_count_unambiguous
        and verdict in {"ack-consistent-no-eps-response", "native-eps-frame-diagnostic-unmatched"},
        "new_ack_error": new_ack_error,
        "new_controller_error": new_controller_error,
        "reported_controller_error": reported_controller_error,
        "controller_error_field_changed": controller_error_field_changed,
        "transmit_error_count_before": transmit_error_before,
        "transmit_error_count_after": transmit_error_after,
        "can_core_reset": core_reset,
        "bus_off": bus_off,
        "can_rx_evidence_lost": can_rx_evidence_lost,
    }


def _verify_panda_configuration(
    panda_health: dict[str, Any],
    can_health: dict[str, Any],
    *,
    expected_safety_mode: int,
    expected_safety_param: int,
) -> None:
    failures: list[str] = []
    if panda_health.get("safety_mode") != expected_safety_mode:
        failures.append(f"safety_mode={panda_health.get('safety_mode')!r}")
    if panda_health.get("safety_param") != expected_safety_param:
        failures.append(f"safety_param={panda_health.get('safety_param')!r}")
    for field, expected in CAN_HEALTH_CONFIGURATION.items():
        if can_health.get(field) != expected:
            failures.append(f"{field}={can_health.get(field)!r}")
    for field in CAN_HEALTH_REQUIRED_FLAG_FIELDS:
        if can_health.get(field) not in (False, 0):
            failures.append(f"{field}={can_health.get(field)!r}")
    if can_health.get("transmit_error_cnt") != 0:
        failures.append(f"transmit_error_cnt={can_health.get('transmit_error_cnt')!r}")
    if can_health.get("receive_error_cnt") != 0:
        failures.append(f"receive_error_cnt={can_health.get('receive_error_cnt')!r}")
    for field in ("last_error", "last_data_error"):
        value = can_health.get(field)
        if not _is_clean_lec(value):
            failures.append(f"{field}={value!r}")
    if panda_health.get("heartbeat_lost") not in (False, 0):
        failures.append(f"heartbeat_lost={panda_health.get('heartbeat_lost')!r}")
    if panda_health.get("power_save_enabled") not in (False, 0):
        failures.append(f"power_save_enabled={panda_health.get('power_save_enabled')!r}")
    if panda_health.get("faults") != 0:
        failures.append(f"faults={panda_health.get('faults')!r}")
    if panda_health.get("fault_status") != 0:
        failures.append(f"fault_status={panda_health.get('fault_status')!r}")
    if panda_health.get("safety_rx_checks_invalid") not in (False, 0):
        failures.append(
            f"safety_rx_checks_invalid={panda_health.get('safety_rx_checks_invalid')!r}"
        )
    failures.extend(
        f"can_health contract {failure}"
        for failure in _can_health_contract_errors(can_health, can_health)
    )
    failures.extend(
        f"panda_health contract {failure}"
        for failure in _panda_health_contract_errors(panda_health, panda_health)
    )
    if failures:
        raise ProbeError("Panda configuration did not read back as 500k/2M ISO CAN-FD: " + ", ".join(failures))


def _configure_bus(
    panda: Any,
    bus: int,
    *,
    safety_mode: int,
    safety_param: int,
    clear_rx_queue: bool,
) -> tuple[dict[str, Any], dict[str, Any]]:
    # Establish the host-TX policy before touching queues or resetting cores.
    # Bus 1 is independent, so the CAN0/CAN2 relay is never touched.
    panda.set_safety_mode(safety_mode, safety_param)
    _send_watchdog_heartbeat(panda, "bus configuration")
    panda.set_power_save(0)
    panda.can_clear(bus)
    if clear_rx_queue:
        panda.can_clear(0xFFFF)
    panda.set_can_loopback(False)
    panda.set_can_speed_kbps(bus, NOMINAL_BITRATE_KBPS)
    panda.set_can_data_speed_kbps(bus, DATA_BITRATE_KBPS)
    panda.set_canfd_non_iso(bus, False)
    panda.set_canfd_auto(bus, False)
    panda_health = _plain_mapping(panda.health())
    can_health = _plain_mapping(panda.can_health(bus))
    _verify_panda_configuration(
        panda_health,
        can_health,
        expected_safety_mode=safety_mode,
        expected_safety_param=safety_param,
    )
    return panda_health, can_health


def _configure_active_phase(panda: Any, bus: int) -> tuple[dict[str, Any], dict[str, Any]]:
    # This is the sole live NOOUTPUT->ELM transition. Panda's safety-mode change
    # reinitializes every CAN core and clears CAN-FD enablement, so restore and
    # verify the exact bus configuration once, then never repeat this function
    # between allowed requests. The global host RX queue remains untouched.
    panda.set_safety_mode(ELM327_SAFETY_MODE, ELM327_NORMAL_ROUTE_PARAM)
    _send_watchdog_heartbeat(panda, "active phase safety configuration")
    panda.set_power_save(0)
    panda.can_clear(bus)
    panda.set_can_speed_kbps(bus, NOMINAL_BITRATE_KBPS)
    panda.set_can_data_speed_kbps(bus, DATA_BITRATE_KBPS)
    panda.set_canfd_non_iso(bus, False)
    panda.set_canfd_auto(bus, False)
    panda_health = _plain_mapping(panda.health())
    can_health = _plain_mapping(panda.can_health(bus))
    _verify_panda_configuration(
        panda_health,
        can_health,
        expected_safety_mode=ELM327_SAFETY_MODE,
        expected_safety_param=ELM327_NORMAL_ROUTE_PARAM,
    )
    return panda_health, can_health


def _configure_nooutput(panda: Any, bus: int) -> tuple[dict[str, Any], dict[str, Any]]:
    return _configure_bus(
        panda,
        bus,
        safety_mode=NOOUTPUT_SAFETY_MODE,
        safety_param=0,
        clear_rx_queue=True,
    )


def _require_nooutput_health(
    panda: Any,
    stage: str,
    *,
    require_heartbeat_clear: bool = True,
) -> dict[str, Any]:
    health = _plain_mapping(panda.health())
    failures: list[str] = []
    if health.get("safety_mode") != NOOUTPUT_SAFETY_MODE:
        failures.append(f"safety_mode={health.get('safety_mode')!r}")
    if health.get("safety_param") != 0:
        failures.append(f"safety_param={health.get('safety_param')!r}")
    if require_heartbeat_clear and health.get("heartbeat_lost") not in (False, 0):
        failures.append(f"heartbeat_lost={health.get('heartbeat_lost')!r}")
    if health.get("power_save_enabled") not in (False, 0):
        failures.append(f"power_save_enabled={health.get('power_save_enabled')!r}")
    if health.get("faults") != 0:
        failures.append(f"faults={health.get('faults')!r}")
    if health.get("fault_status") != 0:
        failures.append(f"fault_status={health.get('fault_status')!r}")
    if health.get("safety_rx_checks_invalid") not in (False, 0):
        failures.append(f"safety_rx_checks_invalid={health.get('safety_rx_checks_invalid')!r}")
    failures.extend(
        f"Panda-health contract {failure}"
        for failure in _panda_health_contract_errors(health, health)
    )
    if failures:
        raise ProbeError(f"Panda left NOOUTPUT before {stage}: " + ", ".join(failures))
    return health


def _send_watchdog_heartbeat(panda: Any, stage: str) -> None:
    send_heartbeat = getattr(panda, "send_heartbeat", None)
    if not callable(send_heartbeat):
        raise ProbeError(f"current Panda send_heartbeat API is required for {stage}")
    send_heartbeat(False)


def _arm_nooutput_watchdog(panda: Any, stage: str) -> dict[str, Any]:
    # Keep Panda's heartbeat fail-safe enabled. The real interactive callbacks
    # refresh it at bounded intervals; a dead host therefore falls back to
    # SILENT instead of leaving ACKing/TX-capable safety active indefinitely.
    health_before = _require_nooutput_health(
        panda,
        f"watchdog guard for {stage}",
        require_heartbeat_clear=False,
    )
    _send_watchdog_heartbeat(panda, stage)
    health_after = _require_nooutput_health(panda, stage)
    issues, _delta, _uptime_reset = _panda_runtime_issues(
        health_before,
        health_after,
        expected_safety_mode=NOOUTPUT_SAFETY_MODE,
        expected_safety_param=0,
    )
    if issues:
        raise ProbeError(f"Panda health changed while arming {stage}: " + ", ".join(issues))
    return health_after


def _wait_with_watchdog(
    panda: Any,
    seconds: float,
    *,
    stage: str,
    sleep_fn: Callable[[float], None],
) -> None:
    remaining = seconds
    while remaining > 0:
        _send_watchdog_heartbeat(panda, stage)
        step = min(remaining, WATCHDOG_HEARTBEAT_INTERVAL_SECONDS)
        sleep_fn(step)
        remaining -= step
    _send_watchdog_heartbeat(panda, stage)


def _drain_can_evidence(
    panda: Any,
    *,
    bus: int,
    health_before: dict[str, Any],
    all_can_health_before: dict[int, dict[str, Any]],
    require_initial_read: bool,
) -> dict[str, object]:
    rows: list[tuple[int, bytes, int]] = []
    drain_errors: list[str] = []
    drain_calls = 0
    must_read = require_initial_read
    all_can_health_after = _snapshot_all_can_health(panda)
    health_after = all_can_health_after[bus]
    panda_health_after = _plain_mapping(panda.health())

    while True:
        expected_native_by_bus = {
            controller_bus: _counter_delta_mod32(
                all_can_health_before.get(controller_bus, {}),
                all_can_health_after.get(controller_bus, {}),
                "total_rx_cnt",
            )
            for controller_bus in PHYSICAL_CAN_BUSES
        }
        observed_native_by_bus = {
            controller_bus: sum(
                1 for _address, _data, source in rows if source == controller_bus
            )
            for controller_bus in PHYSICAL_CAN_BUSES
        }
        unavailable_buses = [
            controller_bus
            for controller_bus, expected in expected_native_by_bus.items()
            if expected is None
        ]
        over_collected_buses = [
            controller_bus
            for controller_bus in PHYSICAL_CAN_BUSES
            if expected_native_by_bus[controller_bus] is not None
            and observed_native_by_bus[controller_bus]
            > int(expected_native_by_bus[controller_bus])
        ]
        if unavailable_buses:
            drain_errors.append(
                "total_rx_cnt delta unavailable for CAN "
                + ",".join(str(controller_bus) for controller_bus in unavailable_buses)
            )
            break
        if over_collected_buses:
            for controller_bus in over_collected_buses:
                drain_errors.append(
                    f"CAN{controller_bus} drained native rows "
                    f"{observed_native_by_bus[controller_bus]} exceed total_rx_cnt delta "
                    f"{expected_native_by_bus[controller_bus]}"
                )
            break
        all_native_rx_reconciled = all(
            observed_native_by_bus[controller_bus]
            == expected_native_by_bus[controller_bus]
            for controller_bus in PHYSICAL_CAN_BUSES
        )

        if not must_read and all_native_rx_reconciled:
            # Eligibility snapshots must be taken after the final USB drain.
            # Re-read every physical CAN controller: a late CAN0/CAN2 row or
            # receipt is as disqualifying as a selected-controller mismatch.
            prior_panda_signature = _panda_counter_signature(panda_health_after)
            first_final_panda_health = _plain_mapping(panda.health())
            final_all_can_health = _snapshot_all_can_health(panda)
            panda_health_after = _plain_mapping(panda.health())
            can_counters_stable = _all_can_counter_signature(
                final_all_can_health
            ) == _all_can_counter_signature(all_can_health_after)
            panda_counters_stable = (
                _panda_counter_signature(first_final_panda_health)
                == prior_panda_signature
                and _panda_counter_signature(panda_health_after)
                == _panda_counter_signature(first_final_panda_health)
            )
            if can_counters_stable and panda_counters_stable:
                all_can_health_after = final_all_can_health
                health_after = all_can_health_after[bus]
                break
            all_can_health_after = final_all_can_health
            health_after = all_can_health_after[bus]
            must_read = True
            continue

        if drain_calls >= MAX_CAN_DRAIN_CALLS:
            drain_errors.append(f"CAN drain exceeded {MAX_CAN_DRAIN_CALLS} calls")
            break
        counters_before_read = _all_can_counter_signature(all_can_health_after)
        panda_counters_before_read = _panda_counter_signature(panda_health_after)
        batch = list(panda.can_recv())
        drain_calls += 1
        rows.extend(batch)
        # Direct USB Panda returns a zero-length packet for an empty CAN queue.
        if len(rows) > MAX_CAN_DRAIN_ROWS:
            drain_errors.append(f"CAN drain exceeded {MAX_CAN_DRAIN_ROWS} rows")
            break
        all_can_health_after = _snapshot_all_can_health(panda)
        health_after = all_can_health_after[bus]
        panda_health_after = _plain_mapping(panda.health())
        can_counters_changed_during_read = (
            _all_can_counter_signature(all_can_health_after) != counters_before_read
        )
        panda_counters_changed_during_read = (
            _panda_counter_signature(panda_health_after) != panda_counters_before_read
        )
        # A nonempty transfer always requires a following empty boundary. A
        # counter change observed around an empty transfer requires one more
        # read so late native or receipt rows cannot be cleared unseen.
        counters_changed_during_read = (
            can_counters_changed_during_read or panda_counters_changed_during_read
        )
        must_read = bool(batch) or counters_changed_during_read
        if not batch and not counters_changed_during_read and not all_native_rx_reconciled:
            missing = ", ".join(
                f"CAN{controller_bus}={observed_native_by_bus[controller_bus]}/"
                f"{expected_native_by_bus[controller_bus]}"
                for controller_bus in PHYSICAL_CAN_BUSES
                if observed_native_by_bus[controller_bus]
                != expected_native_by_bus[controller_bus]
            )
            drain_errors.append(f"CAN drain stalled with unreconciled native rows: {missing}")
            break

    # Even an incomplete drain returns final post-drain health for fail-closed assessment.
    prior_final_can_signature = _all_can_counter_signature(all_can_health_after)
    prior_final_panda_signature = _panda_counter_signature(panda_health_after)
    first_post_loop_panda_health = _plain_mapping(panda.health())
    all_can_health_after = _snapshot_all_can_health(panda)
    health_after = all_can_health_after[bus]
    panda_health_after = _plain_mapping(panda.health())
    if (
        _all_can_counter_signature(all_can_health_after) != prior_final_can_signature
        or _panda_counter_signature(first_post_loop_panda_health)
        != prior_final_panda_signature
        or _panda_counter_signature(panda_health_after)
        != _panda_counter_signature(first_post_loop_panda_health)
    ):
        drain_errors.append("CAN/Panda counters changed after the stable drain boundary")
    expected_native_by_bus = {
        controller_bus: _counter_delta_mod32(
            all_can_health_before.get(controller_bus, {}),
            all_can_health_after.get(controller_bus, {}),
            "total_rx_cnt",
        )
        for controller_bus in PHYSICAL_CAN_BUSES
    }
    observed_native_by_bus = {
        controller_bus: sum(1 for _address, _data, source in rows if source == controller_bus)
        for controller_bus in PHYSICAL_CAN_BUSES
    }
    for controller_bus in PHYSICAL_CAN_BUSES:
        expected = expected_native_by_bus[controller_bus]
        observed = observed_native_by_bus[controller_bus]
        if expected != observed and not any(
            f"CAN{controller_bus}" in error or "delta unavailable" in error
            for error in drain_errors
        ):
            drain_errors.append(
                f"final CAN{controller_bus} native RX evidence unreconciled: "
                f"rows={observed}, total_rx_cnt_delta={expected!r}"
            )
    all_can_health_delta = {
        controller_bus: can_health_delta(
            all_can_health_before.get(controller_bus, {}),
            all_can_health_after.get(controller_bus, {}),
        )
        for controller_bus in PHYSICAL_CAN_BUSES
    }
    all_can_health_contract_errors: dict[int, list[str]] = {}
    for controller_bus in PHYSICAL_CAN_BUSES:
        contract_errors = _can_health_contract_errors(
            all_can_health_before.get(controller_bus, {}),
            all_can_health_after.get(controller_bus, {}),
        )
        all_can_health_contract_errors[controller_bus] = contract_errors
        drain_errors.extend(
            f"CAN{controller_bus} health contract {error}" for error in contract_errors
        )
    for controller_bus in PHYSICAL_CAN_BUSES:
        if controller_bus == bus:
            continue
        for field, delta in all_can_health_delta[controller_bus].items():
            if delta != 0:
                drain_errors.append(
                    f"off-bus CAN{controller_bus} {field} delta={delta} contradicts "
                    "exclusive standalone-CAN1 topology"
                )
    expected_native = expected_native_by_bus[bus]
    observed_native = observed_native_by_bus[bus]
    all_native_rx_reconciled = all(
        expected_native_by_bus[controller_bus] == observed_native_by_bus[controller_bus]
        for controller_bus in PHYSICAL_CAN_BUSES
    )
    return {
        "rows": rows,
        "can_health_after": health_after,
        "all_can_health_before": all_can_health_before,
        "all_can_health_after": all_can_health_after,
        "all_can_health_delta_mod32": all_can_health_delta,
        "all_can_health_contract_errors": all_can_health_contract_errors,
        "panda_health_after": panda_health_after,
        "drain_calls": drain_calls,
        "drained_row_count": len(rows),
        "expected_native_rx_count_mod32": expected_native,
        "observed_native_rx_count": observed_native,
        "expected_native_rx_count_by_bus_mod32": expected_native_by_bus,
        "observed_native_rx_count_by_bus": observed_native_by_bus,
        "all_controller_native_rx_reconciled": all_native_rx_reconciled,
        "complete": not drain_errors and all_native_rx_reconciled,
        "errors": drain_errors,
    }


def _establish_pre_tx_baseline(
    panda: Any,
    *,
    bus: int,
) -> tuple[dict[str, Any], dict[str, Any], dict[int, dict[str, Any]], dict[str, object]]:
    all_can_health_before = _snapshot_all_can_health(panda)
    panda_health_before = _plain_mapping(panda.health())
    health_before = all_can_health_before[bus]
    _verify_panda_configuration(
        panda_health_before,
        health_before,
        expected_safety_mode=ELM327_SAFETY_MODE,
        expected_safety_param=ELM327_NORMAL_ROUTE_PARAM,
    )
    drain = _drain_can_evidence(
        panda,
        bus=bus,
        health_before=health_before,
        all_can_health_before=all_can_health_before,
        require_initial_read=True,
    )
    rows = drain["rows"]
    panda_health_after = drain["panda_health_after"]
    health_after = drain["can_health_after"]
    all_can_health_after = drain["all_can_health_after"]
    if (
        not isinstance(rows, list)
        or not isinstance(panda_health_after, dict)
        or not isinstance(health_after, dict)
        or not isinstance(all_can_health_after, dict)
    ):
        raise ProbeError("pre-TX queue barrier returned invalid evidence")
    issues = [str(error) for error in drain["errors"]]
    if rows:
        issues.append(f"{len(rows)} queued CAN row(s) existed before the phase baseline")
    all_can_health_delta = drain["all_can_health_delta_mod32"]
    if not isinstance(all_can_health_delta, dict):
        issues.append("all-controller CAN-health delta unavailable")
    else:
        for controller_bus, delta in all_can_health_delta.items():
            if not isinstance(delta, dict):
                issues.append(f"CAN{controller_bus} counter delta unavailable")
                continue
            for field, value in delta.items():
                if value != 0:
                    issues.append(f"CAN{controller_bus} {field} changed by {value} in pre-TX barrier")
    panda_issues, _panda_delta, _uptime_reset = _panda_runtime_issues(
        panda_health_before,
        panda_health_after,
        expected_safety_mode=ELM327_SAFETY_MODE,
        expected_safety_param=ELM327_NORMAL_ROUTE_PARAM,
    )
    issues.extend(f"Panda health: {issue}" for issue in panda_issues)
    issues.extend(
        f"CAN configuration: {issue}"
        for issue in _can_configuration_issues(health_before, health_after)
    )
    if issues:
        raise ProbeError("pre-TX queue/evidence barrier failed: " + "; ".join(issues))
    _verify_panda_configuration(
        panda_health_after,
        health_after,
        expected_safety_mode=ELM327_SAFETY_MODE,
        expected_safety_param=ELM327_NORMAL_ROUTE_PARAM,
    )
    barrier_output = {
        "panda_health_before": panda_health_before,
        "panda_health_after": panda_health_after,
        "all_can_health_before": all_can_health_before,
        "all_can_health_after": all_can_health_after,
        "drain": {
            key: value
            for key, value in drain.items()
            if key not in {"rows", "can_health_after", "panda_health_after"}
        },
        "queued_rows": [],
        "valid": True,
    }
    return panda_health_after, health_after, all_can_health_after, barrier_output


def capture_transition(
    panda: Any,
    *,
    bus: int,
    name: str,
    panda_health_before: dict[str, Any],
    health_before: dict[str, Any],
    all_can_health_before: dict[int, dict[str, Any]],
    duration_seconds: float,
    sleep_fn: Callable[[float], None],
) -> dict[str, object]:
    _wait_with_watchdog(
        panda,
        duration_seconds,
        stage=f"{name} passive capture",
        sleep_fn=sleep_fn,
    )
    drain = _drain_can_evidence(
        panda,
        bus=bus,
        health_before=health_before,
        all_can_health_before=all_can_health_before,
        # total_rx_cnt covers only the selected CAN controller.  Always make
        # one USB read so a queued receipt or row from another controller
        # cannot be erased by the next reconfiguration without inspection.
        require_initial_read=True,
    )
    health_after = drain["can_health_after"]
    panda_health_after = drain["panda_health_after"]
    if not isinstance(health_after, dict) or not isinstance(panda_health_after, dict):
        raise ProbeError("internal CAN drain returned invalid health mappings")
    delta = can_health_delta(health_before, health_after)
    can_contract_errors = _can_health_contract_errors(health_before, health_after)
    panda_contract_errors = _panda_health_contract_errors(
        panda_health_before,
        panda_health_after,
    )
    rx_buffer_overflow_delta = _counter_delta_mod32(
        panda_health_before,
        panda_health_after,
        "rx_buffer_overflow",
    )
    evidence_loss_reasons: list[str] = []
    evidence_loss_reasons.extend(str(error) for error in drain["errors"])
    if can_contract_errors:
        evidence_loss_reasons.append("CAN-health schema incomplete")
    if panda_contract_errors:
        evidence_loss_reasons.append("Panda-health schema incomplete")
    if delta.get("total_rx_lost_cnt", 0) != 0:
        evidence_loss_reasons.append("CAN controller RX loss increased")
    if rx_buffer_overflow_delta is None:
        evidence_loss_reasons.append("Panda RX overflow delta unavailable")
    elif rx_buffer_overflow_delta != 0:
        evidence_loss_reasons.append("Panda RX buffer overflow increased")
    panda_runtime_issues, panda_delta, panda_uptime_reset = _panda_runtime_issues(
        panda_health_before,
        panda_health_after,
        expected_safety_mode=NOOUTPUT_SAFETY_MODE,
        expected_safety_param=0,
    )
    evidence_loss_reasons.extend(f"Panda health: {issue}" for issue in panda_runtime_issues)
    can_configuration_issues = _can_configuration_issues(health_before, health_after)
    evidence_loss_reasons.extend(
        f"CAN configuration: {issue}" for issue in can_configuration_issues
    )
    for field in (
        "total_tx_cnt",
        "total_tx_lost_cnt",
        "total_tx_checksum_error_cnt",
        "total_error_cnt",
        "can_core_reset_count",
        "bus_off_cnt",
        "total_fwd_cnt",
    ):
        if delta.get(field, 0) != 0:
            evidence_loss_reasons.append(f"unexpected {field} change during NOOUTPUT capture")
    if health_after.get("transmit_error_cnt") != health_before.get("transmit_error_cnt"):
        evidence_loss_reasons.append("CAN transmit error counter changed during NOOUTPUT capture")
    for field in CAN_HEALTH_REQUIRED_FLAG_FIELDS:
        if health_after.get(field) not in (False, 0):
            evidence_loss_reasons.append(f"CAN {field} active after NOOUTPUT capture")
    for field in ACK_ERROR_FIELDS:
        if _lec_transition_is_error(health_before.get(field), health_after.get(field)):
            evidence_loss_reasons.append(f"CAN {field} changed during NOOUTPUT capture")
    for field in ("last_error", "last_data_error"):
        if not _is_clean_lec(health_after.get(field)):
            evidence_loss_reasons.append(f"CAN {field} reports a current error")
    receive_count = delta.get("total_rx_cnt", 0)
    rows = drain["rows"]
    if not isinstance(rows, list):
        raise ProbeError("internal CAN drain returned invalid rows")
    frames = classify_frames(rows, bus)
    contaminated_by_host_receipt = bool(frames["tx_echo"] or frames["tx_rejected"])
    if contaminated_by_host_receipt:
        evidence_loss_reasons.append("unexpected host TX receipt during NOOUTPUT capture")
    if frames["other_source"]:
        evidence_loss_reasons.append(
            "unexpected other-source frame contradicts exclusive standalone CAN1 topology"
        )
    return {
        "name": name,
        "settle_seconds_after_attestation": duration_seconds,
        "observed_interval": "baseline before prompt through post-attestation settle",
        "mode": "Panda NOOUTPUT (host data frames blocked; protocol ACK bits enabled)",
        "tx_count": 0,
        "panda_health_before": panda_health_before,
        "panda_health_after": panda_health_after,
        "can_health_before": health_before,
        "can_health_after": health_after,
        "all_can_health_before": drain["all_can_health_before"],
        "all_can_health_after": drain["all_can_health_after"],
        "all_can_health_delta_mod32": drain["all_can_health_delta_mod32"],
        "can_health_delta_mod32": delta,
        "panda_health_delta_mod32": panda_delta,
        "panda_rx_buffer_overflow_delta_mod32": rx_buffer_overflow_delta,
        "can_health_contract_errors": can_contract_errors,
        "panda_health_contract_errors": panda_contract_errors,
        "panda_runtime_issues": panda_runtime_issues,
        "panda_uptime_reset": panda_uptime_reset,
        "can_configuration_issues": can_configuration_issues,
        "evidence_valid": not evidence_loss_reasons,
        "evidence_loss_reasons": evidence_loss_reasons,
        "controller_rx_count_mod32": receive_count,
        "drain_calls": drain["drain_calls"],
        "drained_row_count": drain["drained_row_count"],
        "native_rx_reconciled": drain["complete"],
        "frames": frames,
        "native_frame_count": len(frames["native"]),
        "contaminated_by_host_receipt": contaminated_by_host_receipt,
    }


def _best_effort_nooutput(panda: Any, bus: int) -> dict[str, object]:
    errors: list[str] = []
    actions: list[tuple[str, Callable[[], object]]] = [
        ("restore NOOUTPUT safety", lambda: panda.set_safety_mode(NOOUTPUT_SAFETY_MODE, 0)),
        ("retry NOOUTPUT safety before controller reset", lambda: panda.set_safety_mode(NOOUTPUT_SAFETY_MODE, 0)),
        ("clear probe TX queue", lambda: panda.can_clear(bus)),
        ("clear host RX queue", lambda: panda.can_clear(0xFFFF)),
        ("reset CAN cores", lambda: panda.set_can_loopback(False)),
        ("restore nominal bitrate", lambda: panda.set_can_speed_kbps(bus, NOMINAL_BITRATE_KBPS)),
        ("restore data bitrate", lambda: panda.set_can_data_speed_kbps(bus, DATA_BITRATE_KBPS)),
        ("restore ISO CAN-FD", lambda: panda.set_canfd_non_iso(bus, False)),
        ("disable CAN-FD auto", lambda: panda.set_canfd_auto(bus, False)),
    ]
    for label, action in actions:
        try:
            action()
        except (Exception, KeyboardInterrupt) as error:  # noqa: BLE001 - cleanup must survive a second Ctrl+C
            errors.append(f"{label}: {type(error).__name__}: {error}")
    panda_health: dict[str, Any] = {}
    can_health: dict[str, Any] = {}
    verified = False
    try:
        panda_health = _plain_mapping(panda.health())
        can_health = _plain_mapping(panda.can_health(bus))
        _verify_panda_configuration(
            panda_health,
            can_health,
            expected_safety_mode=NOOUTPUT_SAFETY_MODE,
            expected_safety_param=0,
        )
        if panda_health.get("heartbeat_lost") not in (False, 0):
            raise ProbeError(f"heartbeat_lost={panda_health.get('heartbeat_lost')!r}")
        # Only a read-back-verified NOOUTPUT state may be kept alive during the
        # mandatory physical shutdown sequence.
        _send_watchdog_heartbeat(panda, "verified NOOUTPUT cleanup")
        panda_health = _require_nooutput_health(panda, "verified NOOUTPUT cleanup")
        verified = True
    except (Exception, KeyboardInterrupt) as error:  # noqa: BLE001 - retain cleanup/readback failure
        errors.append(f"verify NOOUTPUT configuration: {type(error).__name__}: {error}")
    return {
        "errors": errors,
        "verified": verified,
        "panda_health": panda_health,
        "can_health": can_health,
    }


def _enter_silent_after_shutdown(panda: Any, bus: int) -> list[str]:
    errors: list[str] = []
    actions: list[tuple[str, Callable[[], object]]] = [
        ("enter SILENT safety", lambda: panda.set_safety_mode(SILENT_SAFETY_MODE, 0)),
        ("clear probe TX queue", lambda: panda.can_clear(bus)),
        ("clear host RX queue", lambda: panda.can_clear(0xFFFF)),
        ("reset CAN cores", lambda: panda.set_can_loopback(False)),
        ("reassert SILENT safety after reset", lambda: panda.set_safety_mode(SILENT_SAFETY_MODE, 0)),
    ]
    for label, action in actions:
        try:
            action()
        except (Exception, KeyboardInterrupt) as error:  # noqa: BLE001 - cleanup must survive a second Ctrl+C
            errors.append(f"{label}: {type(error).__name__}: {error}")
    try:
        health = _plain_mapping(panda.health())
        if health.get("safety_mode") != SILENT_SAFETY_MODE:
            raise ProbeError(f"safety_mode={health.get('safety_mode')!r}")
        if health.get("safety_param") != 0:
            raise ProbeError(f"safety_param={health.get('safety_param')!r}")
    except (Exception, KeyboardInterrupt) as error:  # noqa: BLE001 - cleanup readback is safety-critical
        errors.append(f"verify SILENT cleanup: {type(error).__name__}: {error}")
    return errors


def _run_tx_phase(
    panda: Any,
    *,
    bus: int,
    phase: TxPhase,
    settle_seconds: float,
    sleep_fn: Callable[[float], None],
    submission_log: list[dict[str, object]] | None = None,
) -> dict[str, object]:
    # Do not change safety mode, reset CAN, or clear either queue here. The
    # one-time active transition already restored CAN-FD configuration, and
    # this barrier must observe anything arriving since the last capture.
    _send_watchdog_heartbeat(panda, f"{phase.name} pre-TX barrier")
    panda.set_power_save(0)
    (
        panda_health_before,
        health_before,
        all_can_health_before,
        pre_tx_barrier,
    ) = _establish_pre_tx_baseline(
        panda,
        bus=bus,
    )
    assert_allowed_tx(bus, TX_ADDR, phase.data, phase.fd)
    attempt: dict[str, object] | None = None
    if submission_log is not None:
        attempt = {
            **_phase_json(phase),
            "host_submission_attempted": True,
            "can_send_returned": False,
            "phase_evidence_recorded": False,
        }
        submission_log.append(attempt)
    try:
        panda.can_send(TX_ADDR, phase.data, bus, fd=phase.fd)
    except (Exception, KeyboardInterrupt) as error:  # preserve an ambiguous partial USB submission
        if attempt is not None:
            attempt["can_send_error"] = f"{type(error).__name__}: {error}"
        raise
    if attempt is not None:
        attempt["can_send_returned"] = True
    _wait_with_watchdog(
        panda,
        settle_seconds,
        stage=f"{phase.name} response capture",
        sleep_fn=sleep_fn,
    )
    drain = _drain_can_evidence(
        panda,
        bus=bus,
        health_before=health_before,
        all_can_health_before=all_can_health_before,
        require_initial_read=True,
    )
    health_after = drain["can_health_after"]
    panda_health_after = drain["panda_health_after"]
    rows = drain["rows"]
    if (
        not isinstance(health_after, dict)
        or not isinstance(panda_health_after, dict)
        or not isinstance(rows, list)
    ):
        raise ProbeError("internal CAN drain returned invalid phase evidence")
    frames = classify_frames(rows, bus)
    assessment = assess_phase(
        frames,
        health_before,
        health_after,
        request_data=phase.data,
        panda_health_before=panda_health_before,
        panda_health_after=panda_health_after,
        drain_complete=bool(drain["complete"]),
        drain_errors=(str(error) for error in drain["errors"]),
    )
    output = {
        **_phase_json(phase),
        "host_submissions": 1,
        "wire_attempts": "unknown; Panda automatic retransmission may exceed one",
        "pre_tx_queue_barrier": pre_tx_barrier,
        "panda_health_before": panda_health_before,
        "panda_health_after": panda_health_after,
        "can_health_before": health_before,
        "can_health_after": health_after,
        "drain": {
            key: value
            for key, value in drain.items()
            if key not in {"rows", "can_health_after", "panda_health_after"}
        },
        "frames": frames,
        "assessment": assessment,
    }
    if attempt is not None:
        attempt["phase_evidence_recorded"] = True
    return output


def _invoke_shutdown_confirmation(
    shutdown_confirm_fn: Callable[..., str],
    keepalive_allowed: bool,
) -> str:
    """Pass watchdog authority to new callbacks while retaining mock/API compatibility."""
    try:
        parameters = inspect.signature(shutdown_confirm_fn).parameters.values()
    except (TypeError, ValueError):
        return shutdown_confirm_fn(keepalive_allowed)
    accepts_argument = any(
        parameter.kind
        in {
            inspect.Parameter.POSITIONAL_ONLY,
            inspect.Parameter.POSITIONAL_OR_KEYWORD,
            inspect.Parameter.VAR_POSITIONAL,
        }
        for parameter in parameters
    )
    return (
        shutdown_confirm_fn(keepalive_allowed)
        if accepts_argument
        else shutdown_confirm_fn()
    )


def run_on_panda(
    panda: Any,
    *,
    bus: int,
    passive_seconds: float,
    settle_seconds: float,
    aux_reconnect_confirm_fn: Callable[[], str],
    ignition_on_confirm_fn: Callable[[], str],
    shutdown_confirm_fn: Callable[..., str],
    sleep_fn: Callable[[float], None] = time.sleep,
) -> dict[str, object]:
    """Run the fixed probe against an already-open Panda (mockable in tests)."""
    _validate_runtime_parameters(bus, settle_seconds, passive_seconds)
    submission_attempts: list[dict[str, object]] = []
    result: dict[str, object] = {
        "status": "running",
        "started_utc": datetime.now(UTC).isoformat(),
        "phases": [],
        "submission_attempts": submission_attempts,
        "host_submission_attempt_count": 0,
        "host_submission_count": 0,
        "host_submission_count_upper_bound": 0,
        "host_submission_count_scope": (
            "confirmed normal can_send returns; upper bound includes ambiguous API exceptions"
        ),
    }
    try:
        armed_panda_health, armed_can_health = _configure_nooutput(panda, bus)
        armed_panda_health = _arm_nooutput_watchdog(panda, "auxiliary-battery reconnect prompt")
        armed_can_health = _plain_mapping(panda.can_health(bus))
        _verify_panda_configuration(
            armed_panda_health,
            armed_can_health,
            expected_safety_mode=NOOUTPUT_SAFETY_MODE,
            expected_safety_param=0,
        )
        result["nooutput_armed_while_aux_negative_disconnected"] = {
            "panda_health": armed_panda_health,
            "can_health": armed_can_health,
        }
        transition_captures: list[dict[str, object]] = []
        result["passive_listen"] = {
            "safety_mode": "NOOUTPUT; host data TX blocked, protocol ACK enabled",
            "transitions": transition_captures,
        }

        aux_all_can_health_before = _snapshot_all_can_health(panda)
        aux_panda_before = _plain_mapping(panda.health())
        aux_health_before = aux_all_can_health_before[bus]
        if aux_reconnect_confirm_fn() != AUX_RECONNECTED_TOKEN:
            raise ProbeError(f"auxiliary-battery transition requires exact token {AUX_RECONNECTED_TOKEN}")
        _require_nooutput_health(panda, "post-auxiliary-battery transition capture")
        result["aux_negative_reconnect_attested"] = True
        aux_capture = capture_transition(
            panda,
            bus=bus,
            name="aux-negative-reconnect-ig-off",
            panda_health_before=aux_panda_before,
            health_before=aux_health_before,
            all_can_health_before=aux_all_can_health_before,
            duration_seconds=passive_seconds,
            sleep_fn=sleep_fn,
        )
        transition_captures.append(aux_capture)
        if not aux_capture["evidence_valid"]:
            raise ProbeError(
                "passive aux-reconnect capture lost evidence: "
                + ", ".join(str(reason) for reason in aux_capture["evidence_loss_reasons"])
            )

        _arm_nooutput_watchdog(panda, "IG ON / not READY prompt")
        ignition_all_can_health_before = _snapshot_all_can_health(panda)
        ignition_panda_before = _plain_mapping(panda.health())
        ignition_health_before = ignition_all_can_health_before[bus]
        _verify_panda_configuration(
            ignition_panda_before,
            ignition_health_before,
            expected_safety_mode=NOOUTPUT_SAFETY_MODE,
            expected_safety_param=0,
        )
        if ignition_on_confirm_fn() != IGNITION_ON_TOKEN:
            raise ProbeError(f"ignition transition requires exact token {IGNITION_ON_TOKEN}")
        _require_nooutput_health(panda, "post-ignition transition capture")
        result["ignition_on_not_ready_attested"] = True
        ignition_capture = capture_transition(
            panda,
            bus=bus,
            name="ignition-on-not-ready",
            panda_health_before=ignition_panda_before,
            health_before=ignition_health_before,
            all_can_health_before=ignition_all_can_health_before,
            duration_seconds=passive_seconds,
            sleep_fn=sleep_fn,
        )
        transition_captures.append(ignition_capture)
        if not ignition_capture["evidence_valid"]:
            raise ProbeError(
                "passive ignition capture lost evidence: "
                + ", ".join(str(reason) for reason in ignition_capture["evidence_loss_reasons"])
            )

        active_panda_health, active_can_health = _configure_active_phase(panda, bus)
        result["active_bus_configured_once_after_passive"] = {
            "panda_health": active_panda_health,
            "can_health": active_can_health,
            "rx_queue_cleared": False,
        }
        phases_out: list[dict[str, object]] = []
        result["phases"] = phases_out
        for tester_phase, f186_phase in TX_FORMAT_PHASES:
            tester_output = _run_tx_phase(
                panda,
                bus=bus,
                phase=tester_phase,
                settle_seconds=settle_seconds,
                sleep_fn=sleep_fn,
                submission_log=submission_attempts,
            )
            phases_out.append(tester_output)
            tester_assessment = tester_output["assessment"]
            if not isinstance(tester_assessment, dict):
                result["stopped_early"] = (
                    f"invalid assessment after {tester_phase.name}; no further TX"
                )
                break
            response_kinds = tester_assessment["diagnostic_response_kinds"]
            if "tester-present-negative" in response_kinds:
                if (
                    tester_assessment["phase_evidence_valid"]
                    and tester_assessment["verdict"] == "matched-eps-diagnostic-response"
                    and tester_assessment["matched_diagnostic_response_count"] == 1
                ):
                    result["stopped_early"] = (
                        f"validated negative TesterPresent during {tester_phase.name}; "
                        "F186 not sent"
                    )
                else:
                    result["stopped_early"] = (
                        f"syntactically matched negative TesterPresent lacked complete accepted "
                        f"phase evidence during {tester_phase.name}; F186 not sent"
                    )
                break
            if "tester-present-positive" not in response_kinds:
                if not tester_phase.fd and tester_assessment["fd_fallback_eligible"]:
                    continue
                result["stopped_early"] = (
                    f"no safe further-TX gate after {tester_phase.name}: "
                    f"{tester_assessment['verdict']}"
                )
                break
            if (
                not tester_assessment["controller_health_clean"]
                or not tester_assessment["phase_evidence_valid"]
                or tester_assessment["verdict"] != "matched-eps-diagnostic-response"
            ):
                result["stopped_early"] = (
                    f"positive TesterPresent lacked complete clean accepted phase evidence during "
                    f"{tester_phase.name}; F186 not sent"
                )
                break

            f186_output = _run_tx_phase(
                panda,
                bus=bus,
                phase=f186_phase,
                settle_seconds=settle_seconds,
                sleep_fn=sleep_fn,
                submission_log=submission_attempts,
            )
            phases_out.append(f186_output)
            f186_assessment = f186_output["assessment"]
            if (
                isinstance(f186_assessment, dict)
                and f186_assessment["phase_evidence_valid"]
                and f186_assessment["verdict"] == "matched-eps-diagnostic-response"
                and f186_assessment["matched_diagnostic_response_count"] == 1
                and f186_assessment["f186_mode_classification"] is not None
            ):
                result["stopped_early"] = (
                    f"validated F186 response during {f186_phase.name}: "
                    f"{f186_assessment['f186_mode_classification']}"
                )
            else:
                result["stopped_early"] = (
                    f"validated positive same-format TesterPresent completed its one F186 follow-up at "
                    f"{f186_phase.name}, but F186 mode was not validated; "
                    f"assessment={f186_assessment.get('verdict') if isinstance(f186_assessment, dict) else 'invalid'}, "
                    f"syntax={f186_assessment.get('f186_response_syntax_classifications') if isinstance(f186_assessment, dict) else 'invalid'}"
                )
            break
        result["wire_attempt_count"] = "not observable; inspect per-phase CAN health"
        result["status"] = "probe-complete-awaiting-shutdown"
    except (Exception, KeyboardInterrupt) as error:  # noqa: BLE001 - preserve evidence, then force shutdown gate
        result["status"] = "error"
        result["error"] = f"{type(error).__name__}: {error}"
    finally:
        result["host_submission_attempt_count"] = len(submission_attempts)
        result["host_submission_count"] = sum(
            bool(item["can_send_returned"]) for item in submission_attempts
        )
        result["host_submission_count_upper_bound"] = len(submission_attempts)
        result["nooutput_restore"] = _best_effort_nooutput(panda, bus)
        nooutput_verified = bool(result["nooutput_restore"].get("verified"))
        result["shutdown_watchdog_keepalive_allowed"] = nooutput_verified
        result["pre_shutdown_silent_cleanup_errors"] = (
            [] if nooutput_verified else _enter_silent_after_shutdown(panda, bus)
        )
        shutdown_confirmed = False
        try:
            shutdown_confirmed = (
                _invoke_shutdown_confirmation(shutdown_confirm_fn, nooutput_verified)
                == SHUTDOWN_TOKEN
            )
            if not shutdown_confirmed:
                result["shutdown_error"] = f"shutdown requires exact token {SHUTDOWN_TOKEN}"
        except (Exception, KeyboardInterrupt) as error:  # noqa: BLE001 - leave ACKing NOOUTPUT in place
            result["shutdown_error"] = f"{type(error).__name__}: {error}"
        result["shutdown_confirmed"] = shutdown_confirmed
        result["silent_cleanup_errors"] = (
            _enter_silent_after_shutdown(panda, bus) if shutdown_confirmed else []
        )
        if not shutdown_confirmed:
            if nooutput_verified:
                result["urgent_shutdown_instruction"] = (
                    "Panda was left in verified NOOUTPUT/ACKing mode. Keep A30 disconnected; power "
                    "switch/IG OFF, avoid key/door/pedal activity for at least 1 minute, disconnect "
                    "auxiliary-battery negative, then wait at least 1 additional minute before A30."
                )
            else:
                result["urgent_shutdown_instruction"] = (
                    "NOOUTPUT could not be verified; SILENT was attempted and the heartbeat is not "
                    "being refreshed. Keep A30 disconnected; power switch/IG OFF, avoid key/door/pedal "
                    "activity for at least 1 minute, disconnect auxiliary-battery negative, then wait "
                    "at least 1 additional minute before A30."
                )
        elif result["silent_cleanup_errors"]:
            result["urgent_cleanup_instruction"] = (
                "SILENT cleanup was not verified. Keep A30 disconnected and keep the "
                "auxiliary-battery negative disconnected; do not restore power or touch A30."
            )
        result["finished_utc"] = datetime.now(UTC).isoformat()
        cleanup_failed = bool(
            result["nooutput_restore"]["errors"]
            or result["pre_shutdown_silent_cleanup_errors"]
            or result["silent_cleanup_errors"]
        )
        if result["status"] == "probe-complete-awaiting-shutdown" and shutdown_confirmed and not cleanup_failed:
            result["status"] = "complete"
        elif result["status"] != "error":
            result["status"] = "error"
            result["error"] = "mandatory shutdown attestation or Panda cleanup was incomplete"
    return result


def _find_conflicting_processes() -> list[str]:
    try:
        completed = subprocess.run(
            ["pgrep", "-af", "(^|/)(pandad|boardd)([[:space:]]|$)"],
            capture_output=True,
            text=True,
            check=False,
        )
    except FileNotFoundError:
        return []
    if completed.returncode not in (0, 1):
        raise ProbeError(f"could not check Panda process ownership: {completed.stderr.strip()}")
    return [line for line in completed.stdout.splitlines() if line.strip()]


def _tty_token(
    instructions: str,
    token: str,
    *,
    retry: bool = False,
    keepalive_fn: Callable[[], None] | None = None,
) -> str:
    print(f"\n{instructions}\n", file=sys.stderr, flush=True)
    while True:
        try:
            print(f"Type exactly {token}: ", end="", file=sys.stderr, flush=True)
            if keepalive_fn is None:
                entered = input()
            else:
                while True:
                    keepalive_fn()
                    readable, _writable, _exceptional = select.select(
                        [sys.stdin],
                        [],
                        [],
                        WATCHDOG_HEARTBEAT_INTERVAL_SECONDS,
                    )
                    if readable:
                        line = sys.stdin.readline()
                        if line == "":
                            raise EOFError
                        entered = line.rstrip("\r\n")
                        break
        except (EOFError, KeyboardInterrupt) as error:
            raise ProbeError(f"interactive attestation interrupted; required token {token}") from error
        if entered == token:
            return entered
        if not retry:
            raise ProbeError(f"interactive attestation mismatch; required token {token}")
        print(f"Token mismatch. DO NOT TOUCH A30. Required token: {token}", file=sys.stderr, flush=True)


def _wait_minimum_monotonic(
    seconds: float,
    *,
    monotonic_fn: Callable[[], float] = time.monotonic,
    sleep_fn: Callable[[float], None] = time.sleep,
    keepalive_fn: Callable[[], None] | None = None,
) -> float:
    start = monotonic_fn()
    deadline = start + seconds
    while True:
        remaining = deadline - monotonic_fn()
        if remaining <= 0:
            return monotonic_fn() - start
        if keepalive_fn is not None:
            keepalive_fn()
        sleep_fn(min(remaining, WATCHDOG_HEARTBEAT_INTERVAL_SECONDS))


def _live_shutdown_sequence(
    timing: dict[str, object],
    keepalive_fn: Callable[[], None] | None,
) -> str:
    _tty_token(
        "MANDATORY SHUTDOWN STEP 1: power switch/IG OFF now. Keep A30 disconnected and avoid "
        "all key, door, brake, and pedal activity. The tool will enforce the full quiet minute "
        "after your attestation.",
        IG_OFF_TOKEN,
        retry=True,
        keepalive_fn=keepalive_fn,
    )
    print("Timing at least 60 seconds of IG-OFF quiet; do not touch the vehicle...", file=sys.stderr)
    timing["ig_off_quiet_elapsed_seconds"] = _wait_minimum_monotonic(
        MIN_SHUTDOWN_QUIET_SECONDS,
        keepalive_fn=keepalive_fn,
    )
    _tty_token(
        "MANDATORY SHUTDOWN STEP 2: disconnect auxiliary-battery negative now. Keep A30 "
        "disconnected. The tool will enforce the full final minute before SILENT cleanup.",
        AUX_NEGATIVE_DISCONNECTED_TOKEN,
        retry=True,
        keepalive_fn=keepalive_fn,
    )
    print("Timing at least 60 seconds after auxiliary-negative disconnect...", file=sys.stderr)
    timing["post_disconnect_elapsed_seconds"] = _wait_minimum_monotonic(
        MIN_POST_DISCONNECT_SECONDS,
        keepalive_fn=keepalive_fn,
    )
    timing["minimum_waits_enforced"] = True
    return SHUTDOWN_TOKEN


def execute_live(bus: int, settle_seconds: float, passive_seconds: float) -> dict[str, object]:
    _validate_runtime_parameters(bus, settle_seconds, passive_seconds)
    if not sys.stdin.isatty() or not sys.stderr.isatty():
        raise ProbeError("live execution requires a real interactive stdin/stderr TTY for staged power attestations")
    conflicts = _find_conflicting_processes()
    if conflicts:
        raise ProbeError("refusing Panda USB collision; stop openpilot first: " + "; ".join(conflicts))
    try:
        from panda import Panda
    except ImportError as error:
        raise ProbeError("cannot import panda; run on a comma/openpilot environment") from error

    serials = Panda.list(usb_only=True)
    if len(serials) != 1:
        raise ProbeError(f"expected exactly one USB Panda, found {len(serials)}: {serials}")
    panda = Panda(serials[0], disable_checks=False)
    try:
        if not panda.is_connected_usb():
            raise ProbeError("isolated live probe requires a directly USB-connected Panda")
        pre_power_evidence: dict[str, object] = {"panda_usb_serial": serials[0]}
        try:
            pre_power_evidence["panda_type_hex"] = bytes(panda.get_type()).hex()
        except Exception as error:  # noqa: BLE001 - evidence query must not bypass cleanup
            pre_power_evidence["panda_type_error"] = f"{type(error).__name__}: {error}"
        try:
            pre_power_evidence["panda_firmware_version"] = str(panda.get_version())
        except Exception as error:  # noqa: BLE001 - evidence query must not bypass cleanup
            pre_power_evidence["panda_firmware_version_error"] = (
                f"{type(error).__name__}: {error}"
            )
        shutdown_timing: dict[str, object] = {}
        watchdog_keepalive = lambda: _send_watchdog_heartbeat(
            panda,
            "interactive staged execution",
        )
        result = run_on_panda(
            panda,
            bus=bus,
            passive_seconds=passive_seconds,
            settle_seconds=settle_seconds,
            aux_reconnect_confirm_fn=lambda: _tty_token(
                "Panda is configured NOOUTPUT while auxiliary-battery negative remains disconnected. "
                "Reconnect auxiliary-battery negative now; keep IG OFF, A30 disconnected, and foot off brake.",
                AUX_RECONNECTED_TOKEN,
                keepalive_fn=watchdog_keepalive,
            ),
            ignition_on_confirm_fn=lambda: _tty_token(
                "NOOUTPUT is ACKing the isolated bus. Turn IG ON without pressing the brake; never enter READY. "
                "Keep A30 disconnected, parking brake set, and wheels chocked.",
                IGNITION_ON_TOKEN,
                keepalive_fn=watchdog_keepalive,
            ),
            shutdown_confirm_fn=lambda keepalive_allowed: _live_shutdown_sequence(
                shutdown_timing,
                watchdog_keepalive if keepalive_allowed else None,
            ),
        )
        result["shutdown_timing"] = shutdown_timing
        result["panda_pre_power_evidence"] = pre_power_evidence
        if not result.get("shutdown_confirmed"):
            panda_state = (
                "VERIFIED NOOUTPUT/ACKING"
                if result.get("shutdown_watchdog_keepalive_allowed")
                else "UNVERIFIED NOOUTPUT; SILENT WAS ATTEMPTED AND WATCHDOG REFRESH STOPPED"
            )
            print(
                "\n!!! SHUTDOWN NOT ATTESTED: DO NOT TOUCH A30. POWER SWITCH/IG OFF; NO KEY/DOOR/PEDAL "
                "ACTIVITY FOR >=1 MINUTE; DISCONNECT AUXILIARY-BATTERY NEGATIVE; WAIT >=1 MORE MINUTE. "
                f"PANDA STATE: {panda_state}. !!!\n",
                file=sys.stderr,
                flush=True,
            )
        return result
    finally:
        panda.close()


def parse_bus(value: str) -> int:
    try:
        bus = int(value, 0)
    except ValueError as error:
        raise argparse.ArgumentTypeError(f"invalid bus: {value}") from error
    if bus != DEFAULT_BUS:
        raise argparse.ArgumentTypeError("isolated probe is fixed to logical bus 1")
    return bus


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bus", type=parse_bus, default=DEFAULT_BUS)
    parser.add_argument("--passive-seconds", type=float, default=DEFAULT_PASSIVE_SECONDS)
    parser.add_argument("--settle", type=float, default=DEFAULT_SETTLE_SECONDS)
    parser.add_argument("--execute", action="store_true", help="open Panda only after every gate passes")
    parser.add_argument("--arm")
    parser.add_argument("--confirm-a30-disconnected", action="store_true")
    parser.add_argument(
        "--confirm-a30-mating-connector-correct-terminals-no-backprobe-no-piercing-no-generic-pin",
        action="store_true",
    )
    parser.add_argument("--confirm-stationary", action="store_true")
    parser.add_argument("--confirm-parking-brake-set", action="store_true")
    parser.add_argument("--confirm-level-ground", action="store_true")
    parser.add_argument("--confirm-wheel-chocks", action="store_true")
    parser.add_argument("--confirm-foot-off-brake", action="store_true")
    parser.add_argument("--confirm-probe-will-use-ignition-on-not-ready", action="store_true")
    parser.add_argument("--confirm-ignition-off-now", action="store_true")
    parser.add_argument("--confirm-auxiliary-battery-negative-disconnected-now", action="store_true")
    parser.add_argument(
        "--confirm-usb-host-battery-powered-not-vehicle-or-mains",
        action="store_true",
    )
    parser.add_argument("--confirm-rack-only-peer", action="store_true")
    parser.add_argument("--confirm-common-ground", action="store_true")
    parser.add_argument("--confirm-dc1h-dc1l-polarity", action="store_true")
    parser.add_argument("--confirm-resistance-measured-power-off", action="store_true")
    parser.add_argument(
        "--confirm-battery-negative-was-disconnected-for-isolation-checks",
        action="store_true",
    )
    parser.add_argument("--confirm-meter-removed", action="store_true")
    parser.add_argument("--confirm-external-can1-120-ohm-termination", action="store_true")
    parser.add_argument("--confirm-unused-can1-pass-through-unconnected", action="store_true")
    parser.add_argument("--confirm-only-can1-connected", action="store_true")
    parser.add_argument("--confirm-openpilot-stopped", action="store_true")
    parser.add_argument("--rack-only-ohms", type=float)
    parser.add_argument("--complete-bus-ohms", type=float)
    parser.add_argument("--dc1h-to-ground-ohms", type=float)
    parser.add_argument("--dc1l-to-ground-ohms", type=float)
    parser.add_argument("--dc1h-to-aux-positive-ohms", type=float)
    parser.add_argument("--dc1l-to-aux-positive-ohms", type=float)
    return parser


def _preflight_from_args(args: argparse.Namespace) -> PhysicalPreflight:
    return PhysicalPreflight(
        a30_disconnected=args.confirm_a30_disconnected,
        a30_mating_connector_correct_terminals_no_backprobe_no_piercing_no_generic_pin=(
            args.confirm_a30_mating_connector_correct_terminals_no_backprobe_no_piercing_no_generic_pin
        ),
        stationary=args.confirm_stationary,
        parking_brake_set=args.confirm_parking_brake_set,
        level_ground=args.confirm_level_ground,
        wheel_chocks=args.confirm_wheel_chocks,
        foot_off_brake=args.confirm_foot_off_brake,
        probe_will_use_ignition_on_not_ready=(
            args.confirm_probe_will_use_ignition_on_not_ready
        ),
        ignition_off_now=args.confirm_ignition_off_now,
        auxiliary_battery_negative_disconnected_now=(
            args.confirm_auxiliary_battery_negative_disconnected_now
        ),
        usb_host_battery_powered_not_vehicle_or_mains=(
            args.confirm_usb_host_battery_powered_not_vehicle_or_mains
        ),
        rack_only_peer=args.confirm_rack_only_peer,
        common_ground=args.confirm_common_ground,
        dc1_polarity_verified=args.confirm_dc1h_dc1l_polarity,
        resistance_measured_power_off=args.confirm_resistance_measured_power_off,
        battery_negative_disconnected_for_isolation_checks=(
            args.confirm_battery_negative_was_disconnected_for_isolation_checks
        ),
        meter_removed=args.confirm_meter_removed,
        openpilot_stopped=args.confirm_openpilot_stopped,
        rack_only_ohms=args.rack_only_ohms,
        complete_bus_ohms=args.complete_bus_ohms,
        dc1h_to_ground_ohms=args.dc1h_to_ground_ohms,
        dc1l_to_ground_ohms=args.dc1l_to_ground_ohms,
        dc1h_to_aux_positive_ohms=args.dc1h_to_aux_positive_ohms,
        dc1l_to_aux_positive_ohms=args.dc1l_to_aux_positive_ohms,
        external_can1_termination_installed=args.confirm_external_can1_120_ohm_termination,
        unused_can1_pass_through_unconnected=args.confirm_unused_can1_pass_through_unconnected,
        only_can1_connected=args.confirm_only_can1_connected,
        arm=args.arm,
    )


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        plan = build_plan(args.bus, args.settle, args.passive_seconds)
    except (ProbeError, ValueError) as error:
        parser.error(str(error))

    output: dict[str, object] = {"mode": "execute" if args.execute else "dry-run", "plan": plan}
    if args.execute:
        preflight = _preflight_from_args(args)
        try:
            validate_preflight(preflight, args.bus)
            output["preflight"] = asdict(preflight)
            output["result"] = execute_live(args.bus, args.settle, args.passive_seconds)
        except ProbeError as error:
            parser.error(str(error))

    print(json.dumps(output, indent=2, sort_keys=True))
    if args.execute:
        result = output.get("result")
        if not isinstance(result, dict) or result.get("status") != "complete":
            return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
