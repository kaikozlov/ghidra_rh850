#!/usr/bin/env python3
"""Probe the isolated Camry EPS-side CAN segment without persistent writes.

The default is a JSON dry run.  Live execution is intentionally awkward: it
requires an A30-disconnected, rack-only topology, power-off resistance
measurements, exact physical attestations, and interactive power sequencing.
The Panda is powered by a battery-powered USB host (not vehicle or mains) and
put in NOOUTPUT (host data TX blocked, protocol ACK enabled) before the
auxiliary battery is reconnected.
The fixed allowlist contains TesterPresent and F181 in Classical and ISO CAN-FD
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
TesterPresent reply gets exactly one same-format F181 follow-up, then probing
stops.  A validated negative TesterPresent proves the DCM executor and stops
without F181; a validated F181 response is classified without FlowControl.
"""

from __future__ import annotations

import argparse
import json
import math
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
DEFAULT_PASSIVE_SECONDS = 1.0
MIN_PASSIVE_SECONDS = 0.20
MAX_PASSIVE_SECONDS = 5.00
DEFAULT_SETTLE_SECONDS = 0.35
MIN_SETTLE_SECONDS = 0.20
MAX_SETTLE_SECONDS = 1.00
MAX_CAN_DRAIN_CALLS = 32
MAX_CAN_DRAIN_ROWS = 8192
ARM_TOKEN = "A30_DOWNSTREAM_RACK_ONLY_READS"
AUX_RECONNECTED_TOKEN = "AUX_NEGATIVE_RECONNECTED_IG_OFF_A30_STILL_DISCONNECTED"
IGNITION_ON_TOKEN = "IG_ON_NOT_READY_A30_STILL_DISCONNECTED"
SHUTDOWN_TOKEN = "IG_OFF_1MIN_QUIET_AUX_NEGATIVE_DISCONNECTED_1MIN_WAIT_A30_STILL_DISCONNECTED"

TESTER_PRESENT_FRAME = bytes.fromhex("023e000000000000")
F181_FRAME = bytes.fromhex("0322f18100000000")
BOOT_F181_BODY = bytes([0x02]) + bytes([0x21]) * 32
APPLICATION_F181_BODY = bytes.fromhex(
    "02"
    "38393635463333303730303000000000"
    "38413331313333303331303000000000"
)

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
    TxPhase("f181-classical", "ReadDataByIdentifier 0xF181", F181_FRAME, False),
    TxPhase("tester-present-fd", "TesterPresent 0x3E00", TESTER_PRESENT_FRAME, True),
    TxPhase("f181-fd", "ReadDataByIdentifier 0xF181", F181_FRAME, True),
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


def validate_preflight(preflight: PhysicalPreflight, bus: int) -> None:
    """Validate every physical gate before importing or opening Panda."""
    missing: list[str] = []
    if bus != DEFAULT_BUS:
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


def assert_allowed_tx(address: int, data: bytes, fd: bool) -> None:
    """Identity/liveness allowlist immediately in front of the sole TX call."""
    allowed = {(phase.data, phase.fd) for phase in TX_PHASES}
    if address != TX_ADDR or not isinstance(fd, bool) or (bytes(data), fd) not in allowed:
        raise ProbeError(
            f"TX blocked outside fixed identity/liveness allowlist: addr=0x{address:X} "
            f"data={bytes(data).hex()} fd={fd}"
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
    if bus != DEFAULT_BUS:
        raise ProbeError("isolated probe is fixed to logical bus 1; buses 0/2 can swap physical controllers")
    if not MIN_SETTLE_SECONDS <= settle_seconds <= MAX_SETTLE_SECONDS:
        raise ProbeError(
            f"--settle must be {MIN_SETTLE_SECONDS:g}..{MAX_SETTLE_SECONDS:g} seconds"
        )
    if not MIN_PASSIVE_SECONDS <= passive_seconds <= MAX_PASSIVE_SECONDS:
        raise ProbeError(
            f"--passive-seconds must be {MIN_PASSIVE_SECONDS:g}..{MAX_PASSIVE_SECONDS:g} seconds"
        )
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
            "phase_reset": "clear TX/RX queues; reset CAN cores before reconfiguration",
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
            "controller/Panda health permits one Classical F181, then stop. Validated negative 7F/3E "
            "stops without F181. FD TesterPresent fallback is allowed only after clean ACK-consistent "
            "Classical silence or clean unmatched native peer traffic. Rejection, missing TX receipt, "
            "health/schema error, link/controller fault, core reset, RX loss, or overflow stops all TX."
        ),
        "automatic_retransmission": (
            "Panda FDCAN can retry each host submission on wire until ACK or error recovery; "
            "exact wire-attempt count is unavailable"
        ),
        "early_stop": (
            "a validated positive TesterPresent reply permits exactly the following same-format F181 "
            "request, then stops even if F181 is silent; a validated negative TesterPresent stops "
            "without F181; any validated F181 reply (including a FirstFrame) stops without flow control"
        ),
        "passive_listen": {
            "settle_seconds_after_each_transition": passive_seconds,
            "transitions": ["aux-negative reconnect with IG OFF", "IG ON / not READY"],
            "panda_safety": "NOOUTPUT (host data frames blocked; protocol ACK bits enabled)",
            "tx_count": 0,
            "collection": (
                "baseline before each prompt through post-attestation settle; read CAN-health RX "
                "delta first and call can_recv only when queued RX is proven"
            ),
            "loss_policy": (
                "any controller/Panda fault or drift, unexpected host TX receipt, controller RX loss, "
                "or Panda RX overflow stops before active TX"
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
            "loss_counters": "controller total_rx_lost_cnt and Panda rx_buffer_overflow",
            "tx_receipt_gate": (
                "exactly one source bus+128 echo matching 0x7A1/current payload and total_tx_cnt delta 1"
            ),
            "bounded_drain": (
                f"up to {MAX_CAN_DRAIN_CALLS} can_recv calls/{MAX_CAN_DRAIN_ROWS} rows; native rows must "
                "reconcile exactly to total_rx_cnt delta using final post-drain health"
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
            ],
            "boundary": (
                "Only an exact phase-matched response confirms the DCM executor. An unmatched native "
                "0x7A9 proves only peer/frame activity. Otherwise complete clean health is merely "
                "ACK-consistent; a Panda TX echo alone is never called physical ACK."
            ),
        },
        "identity_classification": {
            "first_frame": "8-byte FF can label only boot-prefix/application-prefix/unknown",
            "extended_single_frame": (
                "full label requires exact 0x24 payload: boot 02+32*21 or exact two Camry 16-byte records"
            ),
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
            "tool restores NOOUTPUT first; power switch/IG OFF with no key, door, or pedal activity "
            "for at least 1 minute; disconnect auxiliary-battery negative; wait at least 1 additional "
            "minute before A30. Only then does the tool enter SILENT/close and permit A30 handling "
            "(PIG is always powered)."
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


def classify_f181_identity_response(data: bytes) -> str | None:
    """Classify bounded F181 prefixes separately from complete identities."""
    raw = bytes(data)
    response_kind = classify_phase_response(F181_FRAME, raw)
    if response_kind == "f181-positive-first-frame":
        if raw.startswith(bytes.fromhex("102462f181022121")):
            return "boot-prefix"
        if raw.startswith(bytes.fromhex("102462f181023839")):
            return "application-prefix"
        return "unknown"
    if response_kind != "f181-positive-extended-single-frame":
        return None
    single_frame = _single_frame_payload(raw)
    if single_frame is None:
        return "unknown"
    payload, _extended = single_frame
    if payload == bytes.fromhex("62f181") + BOOT_F181_BODY:
        return "boot-full"
    if payload == bytes.fromhex("62f181") + APPLICATION_F181_BODY:
        return "application-full"
    return "unknown"


def _single_frame_payload(data: bytes) -> tuple[bytes, bool] | None:
    raw = bytes(data)
    if not raw or raw[0] & 0xF0:
        return None
    payload_length = raw[0] & 0x0F
    payload_offset = 1
    extended = False
    if payload_length == 0:
        if len(raw) < 2:
            return None
        payload_length = raw[1]
        payload_offset = 2
        extended = True
    if payload_length == 0 or payload_offset + payload_length > len(raw):
        return None
    return raw[payload_offset : payload_offset + payload_length], extended


def classify_phase_response(request_data: bytes, response_data: bytes) -> str | None:
    """Validate only the bounded ISO-TP/UDS replies for the current request."""
    raw = bytes(response_data)
    single_frame = _single_frame_payload(raw)
    payload = single_frame[0] if single_frame is not None else None
    extended_single_frame = single_frame[1] if single_frame is not None else False
    if bytes(request_data) == TESTER_PRESENT_FRAME:
        if payload == bytes.fromhex("7e00"):
            return "tester-present-positive"
        if payload is not None and len(payload) == 3 and payload[:2] == bytes.fromhex("7f3e"):
            return "tester-present-negative"
        return None
    if bytes(request_data) != F181_FRAME:
        return None
    if (
        payload is not None
        and extended_single_frame
        and len(payload) == 0x24
        and payload[:3] == bytes.fromhex("62f181")
    ):
        return "f181-positive-extended-single-frame"
    if payload is not None and len(payload) == 3 and payload[:2] == bytes.fromhex("7f22"):
        return "f181-negative"
    if len(raw) >= 6 and raw[:5] == bytes.fromhex("102462f181"):
        return "f181-positive-first-frame"
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
            "safety_mode",
            "safety_param",
            "car_harness_status",
        ):
            value = health.get(field)
            if not isinstance(value, int) or isinstance(value, bool) or value < 0:
                errors.append(f"{label}.{field}={value!r}")
        for field in ("heartbeat_lost", "power_save_enabled"):
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
    identity_classes = [
        classification
        for row, _response_kind in matched_responses
        if (
            classification := classify_f181_identity_response(
                bytes.fromhex(str(row["data_hex"]))
            )
        )
        is not None
    ]
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
        "f181_identity_classification": identity_classes[0] if identity_classes else None,
        "f181_identity_scope": (
            "full"
            if identity_classes and identity_classes[0].endswith("-full")
            else "prefix"
            if identity_classes and identity_classes[0].endswith("-prefix")
            else None
        ),
        "restore_authorized": False,
        "tx_echo_count": len(frames["tx_echo"]),
        "matching_tx_echo_count": len(matching_tx_echoes),
        "host_tx_receipt_confirmed": host_tx_receipt_confirmed,
        "tx_receipt_errors": tx_receipt_errors,
        "tx_rejected_count": len(frames["tx_rejected"]),
        "other_source_frame_count": len(frames["other_source"]),
        "topology_contaminated": topology_contaminated,
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

    return {
        **common,
        "verdict": verdict,
        "wire_ack": ack,
        "controller_health_clean": controller_health_clean,
        "panda_health_clean": panda_health_clean,
        "phase_evidence_valid": not rejected
        and not topology_contaminated
        and host_tx_receipt_confirmed
        and native_rx_reconciled
        and drain_complete
        and controller_health_clean
        and panda_health_clean,
        "fd_fallback_eligible": not rejected
        and not topology_contaminated
        and host_tx_receipt_confirmed
        and native_rx_reconciled
        and drain_complete
        and controller_health_clean
        and panda_health_clean
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
) -> tuple[dict[str, Any], dict[str, Any]]:
    # Establish the host-TX policy before touching queues or resetting cores.
    # Bus 1 is independent, so the CAN0/CAN2 relay is never touched.
    panda.set_safety_mode(safety_mode, safety_param)
    panda.can_clear(bus)
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
    return _configure_bus(
        panda,
        bus,
        safety_mode=ELM327_SAFETY_MODE,
        safety_param=ELM327_NORMAL_ROUTE_PARAM,
    )


def _configure_nooutput(panda: Any, bus: int) -> tuple[dict[str, Any], dict[str, Any]]:
    return _configure_bus(
        panda,
        bus,
        safety_mode=NOOUTPUT_SAFETY_MODE,
        safety_param=0,
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
    failures.extend(
        f"Panda-health contract {failure}"
        for failure in _panda_health_contract_errors(health, health)
    )
    if failures:
        raise ProbeError(f"Panda left NOOUTPUT before {stage}: " + ", ".join(failures))
    return health


def _arm_nooutput_heartbeat_guard(panda: Any, stage: str) -> dict[str, Any]:
    # Panda firmware ignores heartbeat-disable while in a car safety mode.  The
    # caller must establish NOOUTPUT first; reset the counter, then disable it.
    health_before = _require_nooutput_health(
        panda,
        f"heartbeat guard for {stage}",
        require_heartbeat_clear=False,
    )
    send_heartbeat = getattr(panda, "send_heartbeat", None)
    if not callable(send_heartbeat):
        raise ProbeError("current Panda send_heartbeat API is required for staged live execution")
    send_heartbeat(False)
    panda.set_heartbeat_disabled()
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


def _drain_can_evidence(
    panda: Any,
    *,
    bus: int,
    health_before: dict[str, Any],
    require_initial_read: bool,
) -> dict[str, object]:
    rows: list[tuple[int, bytes, int]] = []
    drain_errors: list[str] = []
    drain_calls = 0
    must_read = require_initial_read
    health_after = _plain_mapping(panda.can_health(bus))
    panda_health_after = _plain_mapping(panda.health())

    while True:
        expected_native = _counter_delta_mod32(
            health_before,
            health_after,
            "total_rx_cnt",
        )
        observed_native = sum(1 for _address, _data, source in rows if source == bus)
        if expected_native is None:
            drain_errors.append("total_rx_cnt delta unavailable")
            break
        if observed_native > expected_native:
            drain_errors.append(
                f"drained native rows {observed_native} exceed total_rx_cnt delta {expected_native}"
            )
            break

        if not must_read and observed_native == expected_native:
            # Eligibility snapshots must be taken after the final USB drain.
            panda_health_after = _plain_mapping(panda.health())
            final_health = _plain_mapping(panda.can_health(bus))
            panda_health_after = _plain_mapping(panda.health())
            final_expected = _counter_delta_mod32(
                health_before,
                final_health,
                "total_rx_cnt",
            )
            if final_expected == observed_native:
                health_after = final_health
                break
            health_after = final_health
            continue

        if drain_calls >= MAX_CAN_DRAIN_CALLS:
            drain_errors.append(f"CAN drain exceeded {MAX_CAN_DRAIN_CALLS} calls")
            break
        batch = list(panda.can_recv())
        drain_calls += 1
        rows.extend(batch)
        must_read = False
        if len(rows) > MAX_CAN_DRAIN_ROWS:
            drain_errors.append(f"CAN drain exceeded {MAX_CAN_DRAIN_ROWS} rows")
            break
        if not batch and observed_native < expected_native:
            drain_errors.append(
                f"CAN drain stalled at {observed_native}/{expected_native} native rows"
            )
            break
        health_after = _plain_mapping(panda.can_health(bus))
        panda_health_after = _plain_mapping(panda.health())

    # Even an incomplete drain returns final post-drain health for fail-closed assessment.
    panda_health_after = _plain_mapping(panda.health())
    health_after = _plain_mapping(panda.can_health(bus))
    panda_health_after = _plain_mapping(panda.health())
    expected_native = _counter_delta_mod32(health_before, health_after, "total_rx_cnt")
    observed_native = sum(1 for _address, _data, source in rows if source == bus)
    if expected_native != observed_native and not any(
        "native rows" in error or "stalled" in error or "delta unavailable" in error
        for error in drain_errors
    ):
        drain_errors.append(
            f"final native RX evidence unreconciled: rows={observed_native}, "
            f"total_rx_cnt_delta={expected_native!r}"
        )
    return {
        "rows": rows,
        "can_health_after": health_after,
        "panda_health_after": panda_health_after,
        "drain_calls": drain_calls,
        "drained_row_count": len(rows),
        "expected_native_rx_count_mod32": expected_native,
        "observed_native_rx_count": observed_native,
        "complete": not drain_errors and expected_native == observed_native,
        "errors": drain_errors,
    }


def capture_transition(
    panda: Any,
    *,
    bus: int,
    name: str,
    panda_health_before: dict[str, Any],
    health_before: dict[str, Any],
    duration_seconds: float,
    sleep_fn: Callable[[float], None],
) -> dict[str, object]:
    sleep_fn(duration_seconds)
    drain = _drain_can_evidence(
        panda,
        bus=bus,
        health_before=health_before,
        require_initial_read=False,
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
        ("clear probe TX queue", lambda: panda.can_clear(bus)),
        ("clear host RX queue", lambda: panda.can_clear(0xFFFF)),
        ("reset CAN cores", lambda: panda.set_can_loopback(False)),
        ("restore nominal bitrate", lambda: panda.set_can_speed_kbps(bus, NOMINAL_BITRATE_KBPS)),
        ("restore data bitrate", lambda: panda.set_can_data_speed_kbps(bus, DATA_BITRATE_KBPS)),
        ("restore ISO CAN-FD", lambda: panda.set_canfd_non_iso(bus, False)),
        ("disable CAN-FD auto", lambda: panda.set_canfd_auto(bus, False)),
        ("reassert NOOUTPUT safety after reset", lambda: panda.set_safety_mode(NOOUTPUT_SAFETY_MODE, 0)),
        ("reset heartbeat counter in NOOUTPUT", lambda: panda.send_heartbeat(False)),
        ("disable heartbeat checks in NOOUTPUT", panda.set_heartbeat_disabled),
    ]
    for label, action in actions:
        try:
            action()
        except (Exception, KeyboardInterrupt) as error:  # noqa: BLE001 - cleanup must survive a second Ctrl+C
            errors.append(f"{label}: {type(error).__name__}: {error}")
    panda_health: dict[str, Any] = {}
    can_health: dict[str, Any] = {}
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
    except (Exception, KeyboardInterrupt) as error:  # noqa: BLE001 - retain cleanup/readback failure
        errors.append(f"verify NOOUTPUT configuration: {type(error).__name__}: {error}")
    return {"errors": errors, "panda_health": panda_health, "can_health": can_health}


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
) -> dict[str, object]:
    # Reset the controller/configuration boundary so an unacknowledged frame
    # cannot keep retrying into the next request/format.
    panda_health_before, health_before = _configure_active_phase(panda, bus)
    assert_allowed_tx(TX_ADDR, phase.data, phase.fd)
    panda.can_send(TX_ADDR, phase.data, bus, fd=phase.fd)
    sleep_fn(settle_seconds)
    drain = _drain_can_evidence(
        panda,
        bus=bus,
        health_before=health_before,
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
    return {
        **_phase_json(phase),
        "host_submissions": 1,
        "wire_attempts": "unknown; Panda automatic retransmission may exceed one",
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


def run_on_panda(
    panda: Any,
    *,
    bus: int,
    passive_seconds: float,
    settle_seconds: float,
    aux_reconnect_confirm_fn: Callable[[], str],
    ignition_on_confirm_fn: Callable[[], str],
    shutdown_confirm_fn: Callable[[], str],
    sleep_fn: Callable[[float], None] = time.sleep,
) -> dict[str, object]:
    """Run the fixed probe against an already-open Panda (mockable in tests)."""
    result: dict[str, object] = {
        "status": "running",
        "started_utc": datetime.now(UTC).isoformat(),
        "phases": [],
    }
    try:
        armed_panda_health, armed_can_health = _configure_nooutput(panda, bus)
        armed_panda_health = _arm_nooutput_heartbeat_guard(panda, "auxiliary-battery reconnect prompt")
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

        aux_panda_before = _plain_mapping(panda.health())
        aux_health_before = _plain_mapping(panda.can_health(bus))
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
            duration_seconds=passive_seconds,
            sleep_fn=sleep_fn,
        )
        transition_captures.append(aux_capture)
        if not aux_capture["evidence_valid"]:
            raise ProbeError(
                "passive aux-reconnect capture lost evidence: "
                + ", ".join(str(reason) for reason in aux_capture["evidence_loss_reasons"])
            )

        ignition_panda_before = _arm_nooutput_heartbeat_guard(panda, "IG ON / not READY prompt")
        ignition_health_before = _plain_mapping(panda.can_health(bus))
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
            duration_seconds=passive_seconds,
            sleep_fn=sleep_fn,
        )
        transition_captures.append(ignition_capture)
        if not ignition_capture["evidence_valid"]:
            raise ProbeError(
                "passive ignition capture lost evidence: "
                + ", ".join(str(reason) for reason in ignition_capture["evidence_loss_reasons"])
            )

        phases_out: list[dict[str, object]] = []
        result["phases"] = phases_out
        for tester_phase, f181_phase in TX_FORMAT_PHASES:
            tester_output = _run_tx_phase(
                panda,
                bus=bus,
                phase=tester_phase,
                settle_seconds=settle_seconds,
                sleep_fn=sleep_fn,
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
                result["stopped_early"] = (
                    f"validated negative TesterPresent during {tester_phase.name}; F181 not sent"
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
                    f"{tester_phase.name}; F181 not sent"
                )
                break

            f181_output = _run_tx_phase(
                panda,
                bus=bus,
                phase=f181_phase,
                settle_seconds=settle_seconds,
                sleep_fn=sleep_fn,
            )
            phases_out.append(f181_output)
            f181_assessment = f181_output["assessment"]
            if isinstance(f181_assessment, dict) and f181_assessment[
                "matched_diagnostic_response_count"
            ]:
                result["stopped_early"] = f"validated F181 response during {f181_phase.name}"
            else:
                result["stopped_early"] = (
                    f"validated positive same-format TesterPresent completed its one F181 follow-up at "
                    f"{f181_phase.name}; F181 assessment={f181_assessment.get('verdict') if isinstance(f181_assessment, dict) else 'invalid'}"
                )
            break
        result["host_submission_count"] = len(phases_out)
        result["wire_attempt_count"] = "not observable; inspect per-phase CAN health"
        result["status"] = "probe-complete-awaiting-shutdown"
    except (Exception, KeyboardInterrupt) as error:  # noqa: BLE001 - preserve evidence, then force shutdown gate
        result["status"] = "error"
        result["error"] = f"{type(error).__name__}: {error}"
    finally:
        result["nooutput_restore"] = _best_effort_nooutput(panda, bus)
        shutdown_confirmed = False
        try:
            shutdown_confirmed = shutdown_confirm_fn() == SHUTDOWN_TOKEN
            if not shutdown_confirmed:
                result["shutdown_error"] = f"shutdown requires exact token {SHUTDOWN_TOKEN}"
        except (Exception, KeyboardInterrupt) as error:  # noqa: BLE001 - leave ACKing NOOUTPUT in place
            result["shutdown_error"] = f"{type(error).__name__}: {error}"
        result["shutdown_confirmed"] = shutdown_confirmed
        result["silent_cleanup_errors"] = (
            _enter_silent_after_shutdown(panda, bus) if shutdown_confirmed else []
        )
        if not shutdown_confirmed:
            result["urgent_shutdown_instruction"] = (
                "Panda was left in best-effort NOOUTPUT/ACKing mode. Keep A30 disconnected; power "
                "switch/IG OFF, avoid key/door/pedal activity for at least 1 minute, disconnect "
                "auxiliary-battery negative, then wait at least 1 additional minute before A30."
            )
        elif result["silent_cleanup_errors"]:
            result["urgent_cleanup_instruction"] = (
                "SILENT cleanup was not verified. Keep A30 disconnected and keep the "
                "auxiliary-battery negative disconnected; do not restore power or touch A30."
            )
        result["finished_utc"] = datetime.now(UTC).isoformat()
        cleanup_failed = bool(result["nooutput_restore"]["errors"] or result["silent_cleanup_errors"])
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


def _tty_token(instructions: str, token: str, *, retry: bool = False) -> str:
    print(f"\n{instructions}\n", file=sys.stderr, flush=True)
    while True:
        try:
            print(f"Type exactly {token}: ", end="", file=sys.stderr, flush=True)
            entered = input()
        except (EOFError, KeyboardInterrupt) as error:
            raise ProbeError(f"interactive attestation interrupted; required token {token}") from error
        if entered == token:
            return entered
        if not retry:
            raise ProbeError(f"interactive attestation mismatch; required token {token}")
        print(f"Token mismatch. DO NOT TOUCH A30. Required token: {token}", file=sys.stderr, flush=True)


def execute_live(bus: int, settle_seconds: float, passive_seconds: float) -> dict[str, object]:
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
    panda = Panda(serials[0])
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
        result = run_on_panda(
            panda,
            bus=bus,
            passive_seconds=passive_seconds,
            settle_seconds=settle_seconds,
            aux_reconnect_confirm_fn=lambda: _tty_token(
                "Panda is configured NOOUTPUT while auxiliary-battery negative remains disconnected. "
                "Reconnect auxiliary-battery negative now; keep IG OFF, A30 disconnected, and foot off brake.",
                AUX_RECONNECTED_TOKEN,
            ),
            ignition_on_confirm_fn=lambda: _tty_token(
                "NOOUTPUT is ACKing the isolated bus. Turn IG ON without pressing the brake; never enter READY. "
                "Keep A30 disconnected, parking brake set, and wheels chocked.",
                IGNITION_ON_TOKEN,
            ),
            shutdown_confirm_fn=lambda: _tty_token(
                "MANDATORY SHUTDOWN: power switch/IG OFF; avoid key, door, and pedal activity for at "
                "least 1 minute; disconnect auxiliary-battery negative; then wait at least 1 additional "
                "minute. Keep A30 disconnected until the tool confirms SILENT cleanup.",
                SHUTDOWN_TOKEN,
                retry=True,
            ),
        )
        result["panda_pre_power_evidence"] = pre_power_evidence
        if not result.get("shutdown_confirmed"):
            print(
                "\n!!! SHUTDOWN NOT ATTESTED: DO NOT TOUCH A30. POWER SWITCH/IG OFF; NO KEY/DOOR/PEDAL "
                "ACTIVITY FOR >=1 MINUTE; DISCONNECT AUXILIARY-BATTERY NEGATIVE; WAIT >=1 MORE MINUTE. "
                "PANDA WAS LEFT BEST-EFFORT NOOUTPUT/ACKING. !!!\n",
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
