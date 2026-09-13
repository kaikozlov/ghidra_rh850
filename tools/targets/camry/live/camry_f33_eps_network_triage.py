#!/usr/bin/env python3
"""Finite read-only network triage for the exact 2026 Camry F33 EPS incident.

The default mode prints the complete plan without importing Panda or opening
hardware.  Live execution is fixed to the current post-repin normal-harness
route (Panda bus 0, ELM327 parameter 1).  It qualifies that route through
Brake/EPB, reads Brake DTC status, and then makes one primary EPS liveness
request.  Identity reads are allowed only after a correlated primary reply;
the secondary application listener is allowed only after a primary timeout.

An optional central-gateway observation temporarily selects the direct-Panda
OBD route (Panda bus 1, ELM327 parameter 0).  Every path out of that observation
attempts a bounded restoration to ELM327 parameter 1, verifies the remembered
safety mode/parameter through Panda health, and only then performs the final
Brake positive control.  Host/process death, USB loss, or repeated board-control
failure can defeat software cleanup; the result makes an unverified restoration
an urgent stop rather than claiming a guarantee.

There are no caller-selectable addresses, buses, payloads, retries, diagnostic
sessions, resets, SecurityAccess requests, DTC clears, writes, or routines.
"""

from __future__ import annotations

import argparse
import importlib
import json
import re
import signal
import subprocess
import sys
import time
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from typing import Any, Callable


SCHEMA = "camry-f33-eps-network-triage-v1"
ARM_TOKEN = "READ_ONLY_F33_NETWORK_TRIAGE"

ELM327_SAFETY_MODE = 3
SILENT_SAFETY_MODE = 0
NORMAL_ROUTE_PARAM = 1
OBD_ROUTE_PARAM = 0
NORMAL_BUS = 0
OBD_BUS = 1
REQUEST_TIMEOUT_SECONDS = 0.5
RESPONSE_PENDING_TIMEOUT_SECONDS = 2.0
MAX_EXCHANGE_SECONDS = 3.0
HEARTBEAT_POLL_SECONDS = 0.20
ROUTE_SETTLE_SECONDS = 0.05
NORMAL_RESTORE_ATTEMPTS = 3
EXPECTED_CAN_SPEED_KBPS = 500
EXPECTED_CAN_DATA_SPEED_KBPS = 2000
GLOBAL_EXCHANGE_COUNTERS = ("safety_tx_blocked", "tx_buffer_overflow", "rx_buffer_overflow")
CAN_EXCHANGE_COUNTERS = (
    "total_error_cnt",
    "total_tx_lost_cnt",
    "total_rx_lost_cnt",
    "total_tx_checksum_error_cnt",
    "can_core_reset_count",
    "bus_off_cnt",
)
PANDA_OWNER_CANDIDATE_PATTERN = "pandad|boardd"
PANDA_OWNER_COMMAND_PATTERN = re.compile(
    r"(?:^|[./\s])(pandad|boardd)(?:$|[./\s])",
)

BRAKE_DID = 0x102F
BRAKE_DID_LENGTH = 10
U0131_87_RAW = bytes.fromhex("c13187")
EXPECTED_APPLICATION_F181 = bytes.fromhex(
    "02"
    "38393635463333303730303000000000"
    "38413331313333303331303000000000"
)
BOOT_PLACEHOLDER_F181 = b"\x02" + b"!" * 32


class TriageError(RuntimeError):
    """Fail-closed configuration, transport, or protocol error."""


class NoResponse(TriageError):
    """No correlated ISO-TP response arrived inside the fixed window."""


class IncompleteResponse(TriageError):
    """A correlated response began but did not finish inside the fixed window."""

    def __init__(self, message: str, observed_response: bytes = b"") -> None:
        super().__init__(message)
        self.observed_response = bytes(observed_response)


class TriageInterrupted(BaseException):
    """Signal converted into a catchable interruption so cleanup still runs."""


@dataclass(frozen=True)
class Route:
    name: str
    bus: int
    tx_address: int
    rx_address: int
    tx_sub_address: int | None = None
    rx_sub_address: int | None = None


BRAKE_ROUTE = Route("normal-brake", NORMAL_BUS, 0x7B0, 0x7B8)
PRIMARY_EPS_ROUTE = Route("normal-primary-eps", NORMAL_BUS, 0x7A1, 0x7A9)
SECONDARY_EPS_ROUTE = Route("normal-secondary-eps", NORMAL_BUS, 0x7A0, 0x7A8)
GATEWAY_ROUTE = Route("obd-central-gateway-node-5f", OBD_BUS, 0x750, 0x758, 0x5F, 0x5F)

BRAKE_DID_REQUEST = bytes.fromhex("22102f")
BRAKE_DTC_REQUEST = bytes.fromhex("1902ff")
TESTER_PRESENT_REQUEST = bytes.fromhex("3e00")
F186_REQUEST = bytes.fromhex("22f186")
F181_REQUEST = bytes.fromhex("22f181")


# The stage name is part of the allowlist.  It prevents a safe payload from
# being replayed at a different endpoint or in a different conditional branch.
ALLOWED_REQUESTS: frozenset[tuple[str, Route, bytes]] = frozenset({
    ("initial-brake-did", BRAKE_ROUTE, BRAKE_DID_REQUEST),
    ("brake-dtc-status", BRAKE_ROUTE, BRAKE_DTC_REQUEST),
    ("primary-eps-tester-present", PRIMARY_EPS_ROUTE, TESTER_PRESENT_REQUEST),
    ("primary-eps-f186", PRIMARY_EPS_ROUTE, F186_REQUEST),
    ("primary-eps-f181", PRIMARY_EPS_ROUTE, F181_REQUEST),
    ("secondary-eps-tester-present", SECONDARY_EPS_ROUTE, TESTER_PRESENT_REQUEST),
    ("gateway-tester-present", GATEWAY_ROUTE, TESTER_PRESENT_REQUEST),
    ("gateway-f186", GATEWAY_ROUTE, F186_REQUEST),
    ("final-brake-did", BRAKE_ROUTE, BRAKE_DID_REQUEST),
})

ExchangeFn = Callable[[str, Route, bytes], bytes]


class _AddressExtensionAdapter:
    """Discard other logical nodes sharing one CAN response ID.

    opendbc's ``CanClient`` filters the arbitration ID before validating the
    ISO-TP address-extension byte.  Without this prefilter, ordinary traffic
    from gateway nodes 0x0F or 0x6D on 0x758 can raise InvalidSubAddress while
    this command is waiting for node 0x5F.  A full 254-frame Panda batch is its
    queued-RX hint, so keep draining until a non-full batch even when every row
    in the full batch is discarded.
    """

    def __init__(self, panda: Any, rx_sub_address: int) -> None:
        self.can_send = panda.can_send
        self._can_recv = panda.can_recv
        self.rx_sub_address = rx_sub_address

    def can_recv(self) -> list[tuple[int, bytes, int]]:
        retained: list[tuple[int, bytes, int]] = []
        while True:
            frames = list(self._can_recv() or [])
            retained.extend(
                (int(address), bytes(data), int(bus))
                for address, data, bus in frames
                if not data or data[0] == self.rx_sub_address
            )
            if len(frames) < 254:
                return retained


def _utc_now() -> str:
    return datetime.now(UTC).isoformat()


def _route_document(route: Route) -> dict[str, object]:
    return asdict(route)


def _request_document(stage: str, route: Route, request: bytes, condition: str) -> dict[str, object]:
    return {
        "stage": stage,
        "route": _route_document(route),
        "request_hex": request.hex(),
        "condition": condition,
    }


def build_plan(include_gateway: bool = False) -> dict[str, object]:
    requests = [
        _request_document("initial-brake-did", BRAKE_ROUTE, BRAKE_DID_REQUEST, "always"),
        _request_document("brake-dtc-status", BRAKE_ROUTE, BRAKE_DTC_REQUEST, "after positive, well-formed Brake DID 0x102F"),
        _request_document("primary-eps-tester-present", PRIMARY_EPS_ROUTE, TESTER_PRESENT_REQUEST, "after Brake positive control"),
        _request_document("primary-eps-f186", PRIMARY_EPS_ROUTE, F186_REQUEST, "only after a correlated primary TesterPresent reply"),
        _request_document("primary-eps-f181", PRIMARY_EPS_ROUTE, F181_REQUEST, "only after a correlated primary TesterPresent reply"),
        _request_document("secondary-eps-tester-present", SECONDARY_EPS_ROUTE, TESTER_PRESENT_REQUEST, "only after primary TesterPresent timeout"),
    ]
    if include_gateway:
        requests.extend([
            _request_document("gateway-tester-present", GATEWAY_ROUTE, TESTER_PRESENT_REQUEST, "only after primary TesterPresent timeout and verified OBD mux entry"),
            _request_document("gateway-f186", GATEWAY_ROUTE, F186_REQUEST, "only after a correlated gateway TesterPresent reply"),
            _request_document("final-brake-did", BRAKE_ROUTE, BRAKE_DID_REQUEST, "only after verified restoration to ELM327 parameter 1"),
        ])
    return {
        "target": {
            "vehicle": "2026 Camry Hybrid",
            "software_id": "8965F3307000",
            "vehicle_type": 12704,
        },
        "normal_route": {"panda_bus": NORMAL_BUS, "elm327_safety_mode": ELM327_SAFETY_MODE, "elm327_param": NORMAL_ROUTE_PARAM},
        "controller_format": {
            "nominal_kbps": EXPECTED_CAN_SPEED_KBPS,
            "data_kbps": EXPECTED_CAN_DATA_SPEED_KBPS,
            "can_fd_non_iso": False,
        },
        "exchange_evidence_gate": {
            "global_rx_clear_immediately_before_send": True,
            "physical_can_controllers": [0, 1, 2],
            "board_counter_deltas_must_be_zero": list(GLOBAL_EXCHANGE_COUNTERS),
            "can_counter_deltas_must_be_zero": list(CAN_EXCHANGE_COUNTERS),
            "clean_timeout_aggregate_total_tx_delta": 1,
            "tx_delta_meaning": "admitted to one physical controller hardware TX FIFO; not an ACK claim",
        },
        "exit_safety_mode": {"name": "SILENT", "numeric": SILENT_SAFETY_MODE},
        "gateway_route": {
            "requested": include_gateway,
            "panda_bus": OBD_BUS,
            "elm327_safety_mode": ELM327_SAFETY_MODE,
            "temporary_elm327_param": OBD_ROUTE_PARAM,
            "mandatory_restore_param": NORMAL_ROUTE_PARAM,
            "restore_attempts": NORMAL_RESTORE_ATTEMPTS,
        },
        "requests": requests,
        "maximum_uds_requests": 7 if include_gateway else 5,
        "mutating_uds_requests": [],
        "forbidden_operations": [
            "session change", "ECU reset", "SecurityAccess", "DTC clear",
            "write", "download/upload", "RoutineControl", "Active Test",
        ],
    }


def assert_allowed_request(stage: str, route: Route, request: bytes) -> None:
    if (stage, route, bytes(request)) not in ALLOWED_REQUESTS:
        raise TriageError(
            f"request is outside the exact read-only allowlist: stage={stage} "
            f"route={route.name} request={bytes(request).hex()}"
        )


def _classify_response(request: bytes, response: bytes) -> tuple[str, int | None, str | None]:
    if len(response) == 3 and response[0] == 0x7F and response[1] == request[0]:
        return "negative", response[2], None
    if not response:
        return "protocol-error", None, "empty ISO-TP response"

    if request[0] == 0x22:
        expected = bytes([0x62]) + request[1:3]
        if response.startswith(expected):
            return "positive", None, None
        return "protocol-error", None, f"RDBI response does not begin {expected.hex()}"
    if request == BRAKE_DTC_REQUEST:
        if response.startswith(bytes.fromhex("5902")):
            return "positive", None, None
        return "protocol-error", None, "DTC response does not begin 5902"
    if request == TESTER_PRESENT_REQUEST:
        if response == bytes.fromhex("7e00"):
            return "positive", None, None
        return "protocol-error", None, "TesterPresent response is not exactly 7e00"
    return "protocol-error", None, "request parser has no positive-response contract"


def _dtc_code(raw: bytes) -> str:
    if len(raw) != 3:
        raise ValueError("DTC number must be three bytes")
    prefix = "PCBU"[raw[0] >> 6]
    tail = bytes([raw[0] & 0x3F]) + raw[1:]
    return prefix + tail.hex().upper()


def _status_bits(status: int) -> list[str]:
    names = (
        "testFailed",
        "testFailedThisOperationCycle",
        "pendingDTC",
        "confirmedDTC",
        "testNotCompletedSinceLastClear",
        "testFailedSinceLastClear",
        "testNotCompletedThisOperationCycle",
        "warningIndicatorRequested",
    )
    return [name for bit, name in enumerate(names) if status & (1 << bit)]


def parse_brake_dtcs(response: bytes) -> dict[str, object]:
    if not response.startswith(bytes.fromhex("5902")) or len(response) < 3:
        raise TriageError("Brake DTC response is not a 59 02 response")
    availability = response[2]
    payload = response[3:]
    if len(payload) % 4:
        raise TriageError(f"Brake DTC response has malformed record length {len(payload)}")
    records = []
    for offset in range(0, len(payload), 4):
        raw = payload[offset:offset + 3]
        status = payload[offset + 3]
        records.append({
            "code": _dtc_code(raw),
            "raw_hex": raw.hex(),
            "status": status,
            "status_hex": f"0x{status:02X}",
            "status_bits": _status_bits(status),
            "is_u0131_87": raw == U0131_87_RAW,
        })
    return {
        "status_availability_mask": availability,
        "status_availability_mask_hex": f"0x{availability:02X}",
        "records": records,
        "u0131_87": next((row for row in records if row["is_u0131_87"]), None),
    }


def decode_brake_did(response: bytes) -> dict[str, object]:
    if not response.startswith(bytes.fromhex("62102f")):
        raise TriageError("Brake DID response is not 62 10 2F")
    value = response[3:]
    if len(value) != BRAKE_DID_LENGTH:
        raise TriageError(f"Brake DID 0x102F must contain exactly {BRAKE_DID_LENGTH} value bytes, got {len(value)}")
    communication_open = bool(value[9] & 0x20)
    return {
        "did": BRAKE_DID,
        "value_hex": value.hex(),
        "eps_communication_open_bit": communication_open,
        "eps_communication_state": "Under intermittent" if communication_open else "Normal",
        "decode": "MSB0 bit 74 = (value[9] & 0x20) != 0",
    }


def classify_primary_identity(f186: dict[str, object], f181: dict[str, object]) -> str:
    f186_response = bytes.fromhex(str(f186.get("response_hex") or ""))
    f181_response = bytes.fromhex(str(f181.get("response_hex") or ""))
    if f186.get("outcome") == "positive" and f181.get("outcome") == "positive":
        f186_value = f186_response[3:]
        f181_value = f181_response[3:]
        if f181_value == EXPECTED_APPLICATION_F181 and f186_value in (b"\x01", b"\x03"):
            return "exact-application"
        if f181_value == BOOT_PLACEHOLDER_F181:
            return "application-fallback-placeholder"
        return "unexpected-positive-identity"
    if (
        f186.get("outcome") == "negative"
        and f186.get("nrc") == 0x31
        and f181.get("outcome") == "positive"
        and f181_response[3:] == BOOT_PLACEHOLDER_F181
    ):
        return "exact-boot-compatible"
    return "identity-incomplete-or-unclassified"


def _new_result(mode: str, include_gateway: bool) -> dict[str, object]:
    return {
        "schema": SCHEMA,
        "mode": mode,
        "status": "planned" if mode == "dry-run" else "running",
        "terminal_reason": None,
        "started_utc": _utc_now(),
        "finished_utc": None,
        "plan": build_plan(include_gateway),
        "preflight": {},
        "hardware": {},
        "stages": {
            "normal_route_entry": {"state": "not-attempted"},
            "initial_brake": {"state": "not-attempted"},
            "brake_dtcs": {"state": "not-attempted"},
            "primary_eps": {"state": "not-attempted"},
            "secondary_eps": {"state": "not-attempted"},
            "gateway": {"state": "not-requested" if not include_gateway else "not-attempted"},
            "normal_route_restoration": {"state": "not-required" if not include_gateway else "not-attempted"},
            "final_brake": {"state": "not-required" if not include_gateway else "not-attempted"},
        },
        "transmit_ledger": [],
    }


def _perform_exchange(
    result: dict[str, object],
    exchange_fn: ExchangeFn,
    stage: str,
    route: Route,
    request: bytes,
) -> dict[str, object]:
    assert_allowed_request(stage, route, request)
    record: dict[str, object] = {
        "ordinal": len(result["transmit_ledger"]) + 1,
        "stage": stage,
        "route": _route_document(route),
        "request_hex": request.hex(),
        "outcome": "attempting",
        "response_hex": None,
        "observed_response_hex": None,
        "nrc": None,
        "error": None,
    }
    started = time.monotonic()
    try:
        response = bytes(exchange_fn(stage, route, request))
    except NoResponse as error:
        record["outcome"] = "timeout"
        record["error"] = str(error)
    except IncompleteResponse as error:
        record["outcome"] = "response-incomplete"
        record["observed_response_hex"] = error.observed_response.hex() or None
        record["error"] = str(error)
    except (KeyboardInterrupt, TriageInterrupted) as error:
        record["outcome"] = "interrupted"
        record["error"] = f"{type(error).__name__}: {error}"
        raise
    except Exception as error:  # noqa: BLE001 - recorded and fail-closed by caller
        record["outcome"] = "transport-error"
        record["error"] = f"{type(error).__name__}: {error}"
    else:
        record["response_hex"] = response.hex()
        outcome, nrc, error = _classify_response(request, response)
        record["outcome"] = outcome
        record["nrc"] = nrc
        record["error"] = error
    finally:
        record["elapsed_ms"] = round((time.monotonic() - started) * 1000, 3)
        result["transmit_ledger"].append(record)
    return record


def _route_health_issues(health: dict[str, object], param: int) -> list[str]:
    issues = []
    if int(health.get("safety_mode", -1)) != ELM327_SAFETY_MODE:
        issues.append(f"safety_mode={health.get('safety_mode')!r}, expected {ELM327_SAFETY_MODE}")
    if int(health.get("safety_param", -1)) != param:
        issues.append(f"safety_param={health.get('safety_param')!r}, expected {param}")
    if health.get("controls_allowed") is not False:
        issues.append(f"controls_allowed={health.get('controls_allowed')!r}, expected false")
    if health.get("heartbeat_lost") is not False:
        issues.append(f"heartbeat_lost={health.get('heartbeat_lost')!r}, expected false")
    return issues


def _configure_silent(panda: Any, sleep_fn: Callable[[float], None] = time.sleep) -> dict[str, object]:
    panda.send_heartbeat(engaged=False)
    panda.set_safety_mode(SILENT_SAFETY_MODE, 0)
    sleep_fn(ROUTE_SETTLE_SECONDS)
    panda.send_heartbeat(engaged=False)
    health = dict(panda.health())
    issues = []
    if int(health.get("safety_mode", -1)) != SILENT_SAFETY_MODE:
        issues.append(f"safety_mode={health.get('safety_mode')!r}, expected {SILENT_SAFETY_MODE}")
    if health.get("controls_allowed") is not False:
        issues.append(f"controls_allowed={health.get('controls_allowed')!r}, expected false")
    if health.get("heartbeat_lost") is not False:
        issues.append(f"heartbeat_lost={health.get('heartbeat_lost')!r}, expected false")
    return {"verified": not issues, "health": health, "issues": issues}


def _configure_can_format(panda: Any) -> dict[str, object]:
    for bus in range(3):
        panda.set_can_data_speed_kbps(bus, EXPECTED_CAN_DATA_SPEED_KBPS)
        panda.set_canfd_non_iso(bus, False)
    health = {str(bus): dict(panda.can_health(bus)) for bus in range(3)}
    issues = []
    for bus in range(3):
        current = health[str(bus)]
        if int(current.get("can_speed", -1)) != EXPECTED_CAN_SPEED_KBPS:
            issues.append(f"CAN bus {bus} nominal speed is not {EXPECTED_CAN_SPEED_KBPS} kbps")
        if int(current.get("can_data_speed", -1)) != EXPECTED_CAN_DATA_SPEED_KBPS:
            issues.append(f"CAN bus {bus} data speed is not {EXPECTED_CAN_DATA_SPEED_KBPS} kbps")
        if bool(current.get("canfd_non_iso", True)):
            issues.append(f"CAN bus {bus} is not ISO CAN-FD")
    return {"verified": not issues, "can_health": health, "issues": issues}


def _transport_health_snapshot(panda: Any) -> dict[str, object]:
    return {
        "board": dict(panda.health()),
        "can": {str(bus): dict(panda.can_health(bus)) for bus in range(3)},
    }


def _assess_transport_health(
    start: dict[str, Any],
    finish: dict[str, Any],
    route: Route,
    *,
    expected_total_tx_delta: int | None = None,
) -> dict[str, object]:
    issues: list[str] = []
    board_deltas: dict[str, int] = {}
    can_deltas: dict[str, dict[str, int]] = {}

    def delta(counter: str, before: dict[str, Any], after: dict[str, Any], scope: str) -> int:
        if counter not in before or counter not in after:
            issues.append(f"{scope} lacks counter {counter}")
            return 0
        initial = int(before[counter])
        final = int(after[counter])
        if final < initial:
            issues.append(f"{scope} counter {counter} moved backwards ({initial} -> {final})")
            return 0
        return final - initial

    start_board = dict(start["board"])
    finish_board = dict(finish["board"])
    for counter in GLOBAL_EXCHANGE_COUNTERS:
        change = delta(counter, start_board, finish_board, "board")
        board_deltas[counter] = change
        if change:
            issues.append(f"board {counter} increased by {change}")
    issues.extend(_route_health_issues(finish_board, OBD_ROUTE_PARAM if route == GATEWAY_ROUTE else NORMAL_ROUTE_PARAM))

    for bus in range(3):
        label = str(bus)
        before = dict(start["can"][label])
        after = dict(finish["can"][label])
        changes: dict[str, int] = {}
        for counter in CAN_EXCHANGE_COUNTERS:
            change = delta(counter, before, after, f"CAN controller {bus}")
            changes[counter] = change
            if change:
                issues.append(f"CAN controller {bus} {counter} increased by {change}")
        changes["total_tx_cnt"] = delta("total_tx_cnt", before, after, f"CAN controller {bus}")
        changes["total_rx_cnt"] = delta("total_rx_cnt", before, after, f"CAN controller {bus}")
        can_deltas[label] = changes
        if bool(after.get("bus_off", False)):
            issues.append(f"CAN controller {bus} finished bus-off")
        if bool(after.get("error_warning", False)) or bool(after.get("error_passive", False)):
            issues.append(f"CAN controller {bus} finished warning/passive")
        if int(after.get("can_speed", -1)) != EXPECTED_CAN_SPEED_KBPS:
            issues.append(f"CAN controller {bus} nominal speed drifted")
        if int(after.get("can_data_speed", -1)) != EXPECTED_CAN_DATA_SPEED_KBPS:
            issues.append(f"CAN controller {bus} data speed drifted")
        if bool(after.get("canfd_non_iso", True)):
            issues.append(f"CAN controller {bus} entered non-ISO CAN-FD mode")

    aggregate_tx_delta = sum(changes["total_tx_cnt"] for changes in can_deltas.values())
    if expected_total_tx_delta is not None and aggregate_tx_delta != expected_total_tx_delta:
        issues.append(
            "aggregate physical-controller total_tx_cnt delta was "
            f"{aggregate_tx_delta}, expected {expected_total_tx_delta}"
        )

    return {
        "start": start,
        "finish": finish,
        "board_deltas": board_deltas,
        "can_deltas": can_deltas,
        "aggregate_total_tx_delta": aggregate_tx_delta,
        "expected_total_tx_delta": expected_total_tx_delta,
        "clean": not issues,
        "issues": issues,
    }


def _set_route(
    panda: Any,
    param: int,
    *,
    attempts: int,
    sleep_fn: Callable[[float], None],
    resist_interrupts: bool,
) -> dict[str, object]:
    report: dict[str, object] = {
        "requested_param": param,
        "verified": False,
        "attempts": [],
        "interruptions": [],
    }
    for ordinal in range(1, attempts + 1):
        attempt: dict[str, object] = {"ordinal": ordinal, "set_returned": False, "health": None, "issues": []}
        try:
            panda.send_heartbeat(engaged=False)
            panda.set_safety_mode(ELM327_SAFETY_MODE, param)
            attempt["set_returned"] = True
            sleep_fn(ROUTE_SETTLE_SECONDS)
            panda.send_heartbeat(engaged=False)
            health = dict(panda.health())
            attempt["health"] = health
            attempt["issues"] = _route_health_issues(health, param)
            if not attempt["issues"]:
                report["verified"] = True
        except (KeyboardInterrupt, TriageInterrupted) as error:
            attempt["issues"] = [f"{type(error).__name__}: {error}"]
            report["interruptions"].append(attempt["issues"][0])
            if not resist_interrupts:
                report["attempts"].append(attempt)
                raise
        except BaseException as error:  # cleanup must survive ordinary and repeated control-path failures
            attempt["issues"] = [f"{type(error).__name__}: {error}"]
        report["attempts"].append(attempt)
        if report["verified"]:
            break
    return report


def _import_uds() -> Any:
    for module_name in ("opendbc.car.uds", "panda.python.uds", "panda.uds"):
        try:
            module = importlib.import_module(module_name)
        except ImportError:
            continue
        if hasattr(module, "UdsClient") and hasattr(module, "IsoTpMessage"):
            return module
    raise TriageError("cannot import a supported Panda/opendbc UDS module")


def _clear_stale_receive_boundary(panda: Any) -> None:
    # Current opendbc IsoTpMessage.send calls the generator returned by
    # CanClient.recv(drain=True) without iterating it, so its intended stale
    # drain does not execute.  Clear the board RX queue immediately before the
    # allowlisted request and discard any host-side partial packet explicitly.
    # This is a USB control operation; it does not submit a CAN frame.
    panda.can_clear(0xFFFF)
    if hasattr(panda, "can_rx_overflow_buffer"):
        panda.can_rx_overflow_buffer = b""


def _raw_exchange_factory(panda: Any, uds_mod: Any) -> ExchangeFn:
    health_ledger: list[dict[str, object]] = []

    def exchange(stage: str, route: Route, request: bytes) -> bytes:
        kwargs: dict[str, object] = {
            "timeout": REQUEST_TIMEOUT_SECONDS,
            "response_pending_timeout": RESPONSE_PENDING_TIMEOUT_SECONDS,
        }
        if route.tx_sub_address is not None:
            kwargs["sub_addr"] = route.tx_sub_address
        if route.rx_sub_address is not None:
            kwargs["rx_sub_addr"] = route.rx_sub_address
        client_transport = (
            _AddressExtensionAdapter(panda, route.rx_sub_address)
            if route.rx_sub_address is not None
            else panda
        )
        client = uds_mod.UdsClient(
            client_transport,
            route.tx_address,
            route.rx_address,
            route.bus,
            **kwargs,
        )
        message = uds_mod.IsoTpMessage(client._can_client, timeout=REQUEST_TIMEOUT_SECONDS)
        panda.send_heartbeat(engaged=False)
        # Defense in depth: this is the sole diagnostic-PDU send call in the tool.
        assert_allowed_request(stage, route, request)
        health_start = _transport_health_snapshot(panda)
        health_recorded = False

        def finish_health(
            outcome: str,
            *,
            expected_total_tx_delta: int | None = None,
        ) -> dict[str, object]:
            nonlocal health_recorded
            if health_recorded:
                raise TriageError(f"duplicate transport-health finalization for {stage}")
            try:
                health_finish = _transport_health_snapshot(panda)
            except Exception as error:
                health_ledger.append({
                    "stage": stage,
                    "route": _route_document(route),
                    "outcome": outcome,
                    "clean": False,
                    "issues": [f"final transport-health snapshot failed: {type(error).__name__}: {error}"],
                    "start": health_start,
                })
                health_recorded = True
                raise TriageError(f"final transport-health snapshot failed for {stage}") from error
            assessment = _assess_transport_health(
                health_start,
                health_finish,
                route,
                expected_total_tx_delta=expected_total_tx_delta,
            )
            health_ledger.append({
                "stage": stage,
                "route": _route_document(route),
                "outcome": outcome,
                **assessment,
            })
            health_recorded = True
            return assessment

        try:
            _clear_stale_receive_boundary(panda)
            message.send(request)
        except Exception as error:
            try:
                assessment = finish_health("send-error")
            except TriageError as health_error:
                raise health_error from error
            if not assessment["clean"]:
                raise TriageError(
                    "send failed with invalid transport health: " + "; ".join(assessment["issues"])
                ) from error
            raise
        started = time.monotonic()
        overall_deadline = started + MAX_EXCHANGE_SECONDS
        response_deadline = started + REQUEST_TIMEOUT_SECONDS
        response_pending = False
        observed_response = b""

        def expire(reason: str) -> None:
            partial = bytes(getattr(message, "rx_dat", b"") or b"")
            observed = partial or observed_response
            if response_pending or observed:
                finish_health("response-incomplete")
                raise IncompleteResponse(reason, observed)
            assessment = finish_health("timeout", expected_total_tx_delta=1)
            if not assessment["clean"]:
                raise TriageError(
                    "timeout transport health invalid: " + "; ".join(assessment["issues"])
                )
            raise NoResponse(reason)

        while True:
            now = time.monotonic()
            deadline = min(overall_deadline, response_deadline)
            remaining = deadline - now
            if remaining <= 0:
                expire("fixed ISO-TP response window expired")
            panda.send_heartbeat(engaged=False)
            timeout = min(remaining, HEARTBEAT_POLL_SECONDS)
            before = bytes(getattr(message, "rx_dat", b"") or b"")
            try:
                response, _in_progress = message.recv(timeout)
            except Exception as error:  # normalize only the UDS stack's timeout type
                if type(error).__name__ == "MessageTimeoutError":
                    partial = bytes(getattr(message, "rx_dat", b"") or b"")
                    if partial and partial != before:
                        observed_response = partial
                        response_deadline = min(
                            overall_deadline,
                            time.monotonic() + REQUEST_TIMEOUT_SECONDS,
                        )
                    if time.monotonic() >= min(overall_deadline, response_deadline):
                        try:
                            expire(str(error))
                        except (NoResponse, IncompleteResponse) as timeout_error:
                            raise timeout_error from error
                    continue
                try:
                    assessment = finish_health("receive-error")
                except TriageError as health_error:
                    raise health_error from error
                if not assessment["clean"]:
                    raise TriageError(
                        "receive failed with invalid transport health: " + "; ".join(assessment["issues"])
                    ) from error
                raise
            if response is None:
                partial = bytes(getattr(message, "rx_dat", b"") or b"")
                if (_in_progress or partial != before) and partial:
                    observed_response = partial
                    response_deadline = min(
                        overall_deadline,
                        time.monotonic() + REQUEST_TIMEOUT_SECONDS,
                    )
                continue
            raw = bytes(response)
            response_pending = (
                len(raw) == 3
                and raw[0] == 0x7F
                and raw[1] == request[0]
                and raw[2] == 0x78
            )
            observed_response = raw
            if response_pending:
                response_deadline = min(
                    overall_deadline,
                    time.monotonic() + RESPONSE_PENDING_TIMEOUT_SECONDS,
                )
            if not response_pending:
                assessment = finish_health("response-complete")
                if not assessment["clean"]:
                    raise TriageError(
                        "response arrived with invalid transport health: " + "; ".join(assessment["issues"])
                    )
                return raw

    exchange.health_ledger = health_ledger  # type: ignore[attr-defined]
    return exchange


def _native_reply(record: dict[str, object]) -> bool:
    return record.get("outcome") in {"positive", "negative"}


def run_on_panda(
    panda: Any,
    *,
    include_gateway: bool,
    exchange_fn: ExchangeFn,
    sleep_fn: Callable[[float], None] = time.sleep,
) -> dict[str, object]:
    """Run the immutable sequence on an already-open direct Panda.

    ``exchange_fn`` is injected so the complete state machine and cleanup can be
    verified without vehicle hardware or an opendbc dependency.
    """
    result = _new_result("execute", include_gateway)
    stages = result["stages"]

    normal_entry = _set_route(
        panda,
        NORMAL_ROUTE_PARAM,
        attempts=NORMAL_RESTORE_ATTEMPTS,
        sleep_fn=sleep_fn,
        resist_interrupts=False,
    )
    stages["normal_route_entry"] = {"state": "verified" if normal_entry["verified"] else "failed", **normal_entry}
    if not normal_entry["verified"]:
        result["status"] = "unsafe-stop"
        result["terminal_reason"] = "normal-route-entry-not-verified"
        return result

    initial = _perform_exchange(result, exchange_fn, "initial-brake-did", BRAKE_ROUTE, BRAKE_DID_REQUEST)
    stages["initial_brake"] = {"state": initial["outcome"], "exchange": initial}
    if initial["outcome"] != "positive":
        result["status"] = "stopped"
        result["terminal_reason"] = "initial-brake-positive-control-failed"
        return result
    try:
        stages["initial_brake"]["decoded"] = decode_brake_did(bytes.fromhex(str(initial["response_hex"])))
    except TriageError as error:
        initial["outcome"] = "protocol-error"
        initial["error"] = str(error)
        stages["initial_brake"]["state"] = "protocol-error"
        result["status"] = "stopped"
        result["terminal_reason"] = "initial-brake-response-malformed"
        return result

    brake_dtcs = _perform_exchange(result, exchange_fn, "brake-dtc-status", BRAKE_ROUTE, BRAKE_DTC_REQUEST)
    stages["brake_dtcs"] = {"state": brake_dtcs["outcome"], "exchange": brake_dtcs}
    if brake_dtcs["outcome"] == "positive":
        try:
            stages["brake_dtcs"]["decoded"] = parse_brake_dtcs(bytes.fromhex(str(brake_dtcs["response_hex"])))
        except TriageError as error:
            brake_dtcs["outcome"] = "protocol-error"
            brake_dtcs["error"] = str(error)
            stages["brake_dtcs"]["state"] = "protocol-error"
    if brake_dtcs["outcome"] in {"protocol-error", "transport-error", "response-incomplete"}:
        result["status"] = "stopped"
        result["terminal_reason"] = "brake-dtc-exchange-invalid"
        return result

    primary_tp = _perform_exchange(
        result, exchange_fn, "primary-eps-tester-present", PRIMARY_EPS_ROUTE, TESTER_PRESENT_REQUEST,
    )
    primary: dict[str, object] = {
        "state": primary_tp["outcome"],
        "tester_present": primary_tp,
        "f186": {"state": "not-permitted"},
        "f181": {"state": "not-permitted"},
        "identity_classification": None,
        "restore_authorized": False,
    }
    stages["primary_eps"] = primary

    if _native_reply(primary_tp):
        f186 = _perform_exchange(result, exchange_fn, "primary-eps-f186", PRIMARY_EPS_ROUTE, F186_REQUEST)
        primary["f186"] = f186
        if f186["outcome"] in {"protocol-error", "transport-error", "response-incomplete"}:
            result["status"] = "stopped"
            result["terminal_reason"] = "primary-f186-exchange-invalid"
            return result
        f181 = _perform_exchange(result, exchange_fn, "primary-eps-f181", PRIMARY_EPS_ROUTE, F181_REQUEST)
        primary["f181"] = f181
        if f181["outcome"] in {"protocol-error", "transport-error", "response-incomplete"}:
            result["status"] = "stopped"
            result["terminal_reason"] = "primary-f181-exchange-invalid"
            return result
        primary["identity_classification"] = classify_primary_identity(f186, f181)
        stages["secondary_eps"] = {"state": "skipped", "reason": "primary endpoint replied"}
        if include_gateway:
            stages["gateway"] = {"state": "skipped", "reason": "primary endpoint replied"}
            stages["normal_route_restoration"] = {"state": "not-required"}
            stages["final_brake"] = {"state": "not-required"}
        result["status"] = "triage-complete"
        result["terminal_reason"] = "primary-endpoint-replied"
        return result

    if primary_tp["outcome"] != "timeout":
        stages["secondary_eps"] = {"state": "skipped", "reason": "primary outcome was not a clean timeout"}
        if include_gateway:
            stages["gateway"] = {"state": "skipped", "reason": "primary outcome was not a clean timeout"}
        result["status"] = "stopped"
        result["terminal_reason"] = "primary-exchange-invalid"
        return result

    secondary = _perform_exchange(
        result, exchange_fn, "secondary-eps-tester-present", SECONDARY_EPS_ROUTE, TESTER_PRESENT_REQUEST,
    )
    stages["secondary_eps"] = {"state": secondary["outcome"], "tester_present": secondary}

    if secondary["outcome"] in {"protocol-error", "transport-error", "response-incomplete"}:
        if include_gateway:
            stages["gateway"] = {"state": "skipped", "reason": "secondary exchange was invalid"}
            stages["normal_route_restoration"] = {"state": "not-required"}
            stages["final_brake"] = {"state": "not-required"}
        result["status"] = "stopped"
        result["terminal_reason"] = "secondary-exchange-invalid"
        return result

    if not include_gateway:
        result["status"] = "triage-complete"
        result["terminal_reason"] = "primary-timeout-secondary-observed"
        return result

    gateway: dict[str, object] = {
        "state": "entering-obd-route",
        "obd_route_entry": None,
        "tester_present": {"state": "not-attempted"},
        "f186": {"state": "not-permitted"},
    }
    stages["gateway"] = gateway
    interrupted: BaseException | None = None
    gateway_error: BaseException | None = None
    gateway_stage_invalid: str | None = None
    try:
        # Treat the mux as possibly changed before issuing the USB control call:
        # an exception after delivery has ambiguous board-side effect.
        gateway["obd_route_maybe_active"] = True
        obd_entry = _set_route(
            panda, OBD_ROUTE_PARAM, attempts=1, sleep_fn=sleep_fn, resist_interrupts=False,
        )
        gateway["obd_route_entry"] = obd_entry
        if not obd_entry["verified"]:
            gateway["state"] = "obd-route-entry-failed"
            gateway_stage_invalid = "obd-route-entry-not-verified"
        else:
            gateway_tp = _perform_exchange(
                result, exchange_fn, "gateway-tester-present", GATEWAY_ROUTE, TESTER_PRESENT_REQUEST,
            )
            gateway["tester_present"] = gateway_tp
            gateway["state"] = gateway_tp["outcome"]
            if gateway_tp["outcome"] in {"protocol-error", "transport-error", "response-incomplete"}:
                gateway_stage_invalid = "gateway-tester-present-invalid"
            if _native_reply(gateway_tp):
                gateway_f186 = _perform_exchange(
                    result, exchange_fn, "gateway-f186", GATEWAY_ROUTE, F186_REQUEST,
                )
                gateway["f186"] = gateway_f186
                if gateway_f186["outcome"] in {"protocol-error", "transport-error", "response-incomplete"}:
                    gateway_stage_invalid = "gateway-f186-invalid"
    except (KeyboardInterrupt, TriageInterrupted) as error:
        interrupted = error
        gateway["state"] = "interrupted"
    except BaseException as error:  # record, restore, then report rather than escaping cleanup
        gateway_error = error
        gateway["state"] = "error"
        gateway["error"] = f"{type(error).__name__}: {error}"
    finally:
        restoration = _set_route(
            panda,
            NORMAL_ROUTE_PARAM,
            attempts=NORMAL_RESTORE_ATTEMPTS,
            sleep_fn=sleep_fn,
            resist_interrupts=True,
        )
        stages["normal_route_restoration"] = {
            "state": "verified" if restoration["verified"] else "failed",
            **restoration,
        }
        if restoration["interruptions"] and interrupted is None:
            interrupted = TriageInterrupted("; ".join(restoration["interruptions"]))
        if restoration["verified"]:
            try:
                final_brake = _perform_exchange(
                    result, exchange_fn, "final-brake-did", BRAKE_ROUTE, BRAKE_DID_REQUEST,
                )
                stages["final_brake"] = {"state": final_brake["outcome"], "exchange": final_brake}
                if final_brake["outcome"] == "positive":
                    try:
                        stages["final_brake"]["decoded"] = decode_brake_did(
                            bytes.fromhex(str(final_brake["response_hex"]))
                        )
                    except TriageError as error:
                        final_brake["outcome"] = "protocol-error"
                        final_brake["error"] = str(error)
                        stages["final_brake"]["state"] = "protocol-error"
            except (KeyboardInterrupt, TriageInterrupted) as error:
                interrupted = interrupted or error
                stages["final_brake"] = {"state": "interrupted"}
        else:
            stages["final_brake"] = {
                "state": "skipped",
                "reason": "normal mux restoration was not verified; no further vehicle request permitted",
            }

    if not stages["normal_route_restoration"].get("verified"):
        result["status"] = "unsafe-stop"
        result["terminal_reason"] = "normal-route-restoration-not-verified"
    elif stages["final_brake"].get("state") != "positive":
        result["status"] = "unsafe-stop"
        result["terminal_reason"] = "final-brake-positive-control-failed"
    elif interrupted is not None:
        result["status"] = "interrupted"
        result["terminal_reason"] = f"{type(interrupted).__name__}: {interrupted}"
    elif gateway_error is not None:
        result["status"] = "stopped"
        result["terminal_reason"] = f"gateway-error-after-restoration: {type(gateway_error).__name__}"
    elif gateway_stage_invalid is not None:
        result["status"] = "stopped"
        result["terminal_reason"] = gateway_stage_invalid
    else:
        result["status"] = "triage-complete"
        result["terminal_reason"] = "gateway-observed-normal-route-restored"
    return result


def _find_conflicting_processes() -> list[str]:
    try:
        completed = subprocess.run(
            ["pgrep", "-af", PANDA_OWNER_CANDIDATE_PATTERN],
            capture_output=True,
            text=True,
            check=False,
        )
    except FileNotFoundError as error:
        raise TriageError("cannot verify direct Panda ownership because pgrep is unavailable") from error
    if completed.returncode not in (0, 1):
        raise TriageError(f"could not verify direct Panda ownership: {completed.stderr.strip()}")
    conflicts = []
    for line in completed.stdout.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        fields = stripped.split(maxsplit=1)
        command = fields[1] if len(fields) == 2 and fields[0].isdigit() else stripped
        if PANDA_OWNER_COMMAND_PATTERN.search(command):
            conflicts.append(stripped)
    return conflicts


def _validate_preflight(args: argparse.Namespace) -> dict[str, object]:
    required = {
        "--confirm-stationary": args.confirm_stationary,
        "--confirm-ignition-on-ready-off": args.confirm_ignition_on_ready_off,
        "--confirm-stable-12v-support": args.confirm_stable_12v_support,
        "--confirm-openpilot-stopped": args.confirm_openpilot_stopped,
        f"--arm {ARM_TOKEN}": args.arm == ARM_TOKEN,
    }
    missing = [name for name, present in required.items() if not present]
    if missing:
        raise TriageError("live execution preflight failed; missing " + ", ".join(missing))
    if not sys.stdin.isatty() or not sys.stderr.isatty():
        raise TriageError("live execution requires a real interactive stdin/stderr TTY")
    conflicts = _find_conflicting_processes()
    if conflicts:
        raise TriageError("refusing Panda USB collision; stop openpilot first: " + "; ".join(conflicts))
    return {"confirmed": sorted(required), "direct_panda_owner_check": "passed"}


def _signal_guard():
    previous: dict[int, Any] = {}

    def handler(signum: int, _frame: Any) -> None:
        raise TriageInterrupted(signal.Signals(signum).name)

    for signum in (signal.SIGINT, signal.SIGTERM, signal.SIGHUP):
        previous[signum] = signal.getsignal(signum)
        signal.signal(signum, handler)

    class Guard:
        def __enter__(self):
            return self

        def __exit__(self, _type, _value, _traceback):
            for signum, prior in previous.items():
                signal.signal(signum, prior)
            return False

    return Guard()


def execute_live(args: argparse.Namespace) -> tuple[dict[str, object], int]:
    result = _new_result("execute", args.include_gateway)
    panda = None
    exchange_fn: ExchangeFn | None = None
    try:
        result["preflight"] = _validate_preflight(args)
        try:
            from panda import Panda
        except ImportError as error:
            raise TriageError("cannot import Panda; run from the comma/openpilot Panda environment") from error
        uds_mod = _import_uds()
        serials = Panda.list(usb_only=True)
        if len(serials) != 1:
            raise TriageError(f"expected exactly one directly connected USB Panda, found {len(serials)}: {serials}")
        panda = Panda(serials[0], disable_checks=False)
        if not panda.is_connected_usb():
            raise TriageError("network triage requires a directly connected USB Panda")
        initial_silent = _configure_silent(panda)
        result["initial_silent"] = initial_silent
        if not initial_silent["verified"]:
            raise TriageError("initial Panda SILENT safety was not verified: " + "; ".join(initial_silent["issues"]))
        can_format = _configure_can_format(panda)
        result["controller_format"] = can_format
        if not can_format["verified"]:
            raise TriageError("Panda CAN format setup failed: " + "; ".join(can_format["issues"]))
        result["hardware"] = {
            "panda_usb_serial": serials[0],
            "direct_usb": True,
            "heartbeat_checks_enabled": True,
        }
        exchange_fn = _raw_exchange_factory(panda, uds_mod)
        with _signal_guard():
            result = run_on_panda(
                panda,
                include_gateway=args.include_gateway,
                exchange_fn=exchange_fn,
            )
            result["initial_silent"] = initial_silent
            result["controller_format"] = can_format
            result["preflight"] = _validate_preflight_record(args)
            result["hardware"] = {
                "panda_usb_serial": serials[0],
                "direct_usb": True,
                "heartbeat_checks_enabled": True,
            }
    except (KeyboardInterrupt, TriageInterrupted) as error:
        result["status"] = "interrupted"
        result["terminal_reason"] = f"{type(error).__name__}: {error}"
    except TriageError as error:
        result["status"] = "refused" if panda is None else "stopped"
        result["terminal_reason"] = str(error)
    except BaseException as error:
        result["status"] = "error"
        result["terminal_reason"] = f"{type(error).__name__}: {error}"
    finally:
        if exchange_fn is not None:
            result["transport_health_ledger"] = list(getattr(exchange_fn, "health_ledger", []))
        if panda is not None:
            try:
                final_silent = _configure_silent(panda)
                result["final_silent"] = final_silent
                if not final_silent["verified"]:
                    result["status"] = "unsafe-stop"
                    result["terminal_reason"] = "final Panda SILENT safety was not verified"
            except BaseException as error:
                result["final_silent"] = {
                    "verified": False,
                    "error": f"{type(error).__name__}: {error}",
                }
                result["status"] = "unsafe-stop"
                result["terminal_reason"] = "final Panda SILENT safety call failed"
            try:
                panda.close()
                result.setdefault("hardware", {})["panda_closed"] = True
            except BaseException as error:
                result.setdefault("hardware", {})["panda_closed"] = False
                result.setdefault("hardware", {})["close_error"] = f"{type(error).__name__}: {error}"
                if result.get("status") == "triage-complete":
                    result["status"] = "error"
                    result["terminal_reason"] = "Panda close failed"
        result["finished_utc"] = _utc_now()

    status = result.get("status")
    if status == "triage-complete":
        return result, 0
    if status == "interrupted":
        return result, 130
    if status == "unsafe-stop":
        return result, 4
    return result, 2


def _validate_preflight_record(args: argparse.Namespace) -> dict[str, object]:
    return {
        "stationary": bool(args.confirm_stationary),
        "ignition_on_ready_off": bool(args.confirm_ignition_on_ready_off),
        "stable_12v_support": bool(args.confirm_stable_12v_support),
        "openpilot_stopped": bool(args.confirm_openpilot_stopped),
        "arm_token": args.arm,
        "direct_panda_owner_check": "passed",
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--include-gateway", action="store_true", help="include the temporary direct-Panda OBD gateway observation")
    parser.add_argument("--execute", action="store_true", help="open Panda only after every fixed preflight gate passes")
    parser.add_argument("--arm")
    parser.add_argument("--confirm-stationary", action="store_true")
    parser.add_argument("--confirm-ignition-on-ready-off", action="store_true")
    parser.add_argument("--confirm-stable-12v-support", action="store_true")
    parser.add_argument("--confirm-openpilot-stopped", action="store_true")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if not args.execute:
        result = _new_result("dry-run", args.include_gateway)
        result["finished_utc"] = _utc_now()
        print(json.dumps(result, indent=2, sort_keys=True))
        return 0
    result, returncode = execute_live(args)
    print(json.dumps(result, indent=2, sort_keys=True))
    if returncode == 4:
        print(
            "URGENT: normal-route entry/restoration or its final Brake control was not verified; "
            "do not run further diagnostics until ELM327 parameter 1 is restored and Brake 0x102F answers.",
            file=sys.stderr,
        )
    return returncode


if __name__ == "__main__":
    raise SystemExit(main())
