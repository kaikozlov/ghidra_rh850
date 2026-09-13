#!/usr/bin/env python3
"""Passive EPS-side CAN capture while Toyota GTS+ owns a separate VCI.

This exact-target helper never calls ``can_send``.  It opens the installed USB
Panda as an independent data-frame receiver, forces Panda ``NOOUTPUT`` safety (which
also selects the normal harness CAN routing), and records every received frame
from physical Panda buses 0..2.  GTS+/CUW must use a different interface, such
as the already present Mini-VCI, so the two processes never contend for one
transport.

The binary capture preserves all traffic.  A companion NDJSON stream indexes
the classic-CAN diagnostic range and annotates ISO-TP/UDS framing for the exact
EPS, Brake, and known central-gateway routes.  It deliberately does not send a
flow-control frame: the active GTS+ client owns the complete diagnostic
conversation, and this process is only a witness.

Dry-run is the default and neither imports Panda nor creates an output path.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import signal
import struct
import subprocess
import sys
import time
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, BinaryIO, Callable


SCHEMA = "camry-f33-eps-gts-passive-capture-v1"
ARM_TOKEN = "PASSIVE_F33_GTS_WITNESS"
SILENT_SAFETY_MODE = 0
NOOUTPUT_SAFETY_MODE = 19
DEFAULT_DURATION_SECONDS = 900
MIN_DURATION_SECONDS = 10
MAX_DURATION_SECONDS = 3600
POLL_SECONDS = 0.005
HEARTBEAT_SECONDS = 0.20
PANDA_OWNER_CANDIDATE_PATTERN = "pandad|boardd"
PANDA_OWNER_COMMAND_PATTERN = re.compile(r"(?:^|[./\s])(pandad|boardd)(?:$|[./\s])")
EXPECTED_CAN_SPEED_KBPS = 500
EXPECTED_CAN_DATA_SPEED_KBPS = 2000
GLOBAL_CAPTURE_COUNTERS = ("rx_buffer_overflow", "tx_buffer_overflow")
BUS_CAPTURE_COUNTERS = (
    "total_error_cnt",
    "total_rx_lost_cnt",
    "total_tx_lost_cnt",
    "total_tx_cnt",
    "can_core_reset_count",
    "bus_off_cnt",
)

CANBIN_MAGIC = b"CAMGTS1\0"
CANBIN_HEADER = struct.Struct("<QIBB")  # monotonic_ns, address, bus, dlc

KNOWN_ROUTES = {
    0x750: "central-gateway-request",
    0x758: "central-gateway-response",
    0x751: "gateway-0751-request",
    0x759: "gateway-0751-response",
    0x786: "dh-central-gateway-request",
    0x78E: "dh-central-gateway-response",
    0x7A0: "eps-secondary-request",
    0x7A8: "eps-secondary-response",
    0x7A1: "eps-primary-request",
    0x7A9: "eps-primary-response",
    0x7B0: "brake-request",
    0x7B8: "brake-response",
    0x777: "toyota-functional-request",
    0x7DF: "obd-functional-request",
}

SERVICE_NAMES = {
    0x10: "DiagnosticSessionControl",
    0x11: "ECUReset",
    0x14: "ClearDiagnosticInformation",
    0x19: "ReadDTCInformation",
    0x22: "ReadDataByIdentifier",
    0x27: "SecurityAccess",
    0x28: "CommunicationControl",
    0x2E: "WriteDataByIdentifier",
    0x31: "RoutineControl",
    0x34: "RequestDownload",
    0x35: "RequestUpload",
    0x36: "TransferData",
    0x37: "RequestTransferExit",
    0x3E: "TesterPresent",
    0x50: "DiagnosticSessionControlPositive",
    0x51: "ECUResetPositive",
    0x54: "ClearDiagnosticInformationPositive",
    0x59: "ReadDTCInformationPositive",
    0x62: "ReadDataByIdentifierPositive",
    0x67: "SecurityAccessPositive",
    0x68: "CommunicationControlPositive",
    0x6E: "WriteDataByIdentifierPositive",
    0x71: "RoutineControlPositive",
    0x74: "RequestDownloadPositive",
    0x75: "RequestUploadPositive",
    0x76: "TransferDataPositive",
    0x77: "RequestTransferExitPositive",
    0x7E: "TesterPresentPositive",
    0x7F: "NegativeResponse",
}


class CaptureError(RuntimeError):
    """Fail-closed preflight, hardware, or persistence error."""


class CaptureInterrupted(BaseException):
    """Signal converted into a cleanup-preserving control path."""


def _utc_now() -> str:
    return datetime.now(UTC).isoformat()


def build_plan(duration_seconds: int, output_dir: str | None) -> dict[str, object]:
    return {
        "schema": SCHEMA,
        "mode": "dry-run",
        "target": {
            "vehicle": "2026 Camry Hybrid",
            "eps_software_id": "8965F3307000",
            "primary_route": "0x7A1 -> 0x7A9",
            "secondary_route": "0x7A0 -> 0x7A8",
            "brake_route": "0x7B0 -> 0x7B8",
            "central_gateway_route": (
                "0x750/0x758 address-extension 0x5F is on the separate OBD-mux segment; "
                "normal-route sightings are incidental, not direct GTS/gateway evidence"
            ),
        },
        "duration_seconds": duration_seconds,
        "output_dir": output_dir or "build/out/camry-f33-gts-passive-<UTC timestamp>",
        "panda": {
            "ownership": "one direct USB Panda; pandad/boardd must be stopped",
            "safety_mode": {"name": "NOOUTPUT", "numeric": NOOUTPUT_SAFETY_MODE},
            "exit_safety_mode": {"name": "SILENT", "numeric": SILENT_SAFETY_MODE},
            "routing": "normal harness CAN mode; no OBD mux selection",
            "physical_buses_recorded": [0, 1, 2],
            "can_format": {
                "nominal_kbps": EXPECTED_CAN_SPEED_KBPS,
                "data_kbps": EXPECTED_CAN_DATA_SPEED_KBPS,
                "can_fd_non_iso": False,
            },
        },
        "active_client": "Toyota GTS+/CUW on a physically separate VIM/J2534 interface",
        "files": ["can.bin", "diagnostic.ndjson", "summary.json"],
        "can_transmit_calls": 0,
        "uds_requests": [],
        "flow_control_frames": 0,
        "boundary": (
            "no CAN data-frame submissions; NOOUTPUT remains ACK-capable, Panda USB client "
            "initialization/control remains active, and the witness cannot make a silent EPS answer "
            "or authorize a GTS+/CUW write"
        ),
    }


def write_canbin_header(stream: BinaryIO) -> None:
    stream.write(CANBIN_MAGIC)


def write_canbin_record(stream: BinaryIO, t_ns: int, bus: int, address: int, data: bytes) -> None:
    if not 0 <= bus <= 2:
        raise ValueError(f"physical Panda bus outside 0..2: {bus}")
    if not 0 <= address <= 0x1FFFFFFF:
        raise ValueError(f"CAN address outside 29-bit range: {address:#x}")
    if len(data) > 64:
        raise ValueError(f"CAN payload exceeds 64 bytes: {len(data)}")
    stream.write(CANBIN_HEADER.pack(t_ns, address, bus, len(data)))
    stream.write(data)


def _isotp_view(address: int, data: bytes) -> dict[str, object]:
    """Return a bounded framing hint without participating in the transport."""
    if not data:
        return {"transport": "empty"}

    offset = 0
    extension: int | None = None
    # Toyota's shared 750/758 route uses address extension.  Recognize only the
    # exact node and the two already observed neighboring nodes; never infer an
    # extension on another arbitration ID.
    if address in {0x750, 0x758} and data[0] in {0x0F, 0x5F, 0x6D} and len(data) >= 2:
        extension = data[0]
        offset = 1

    pci = data[offset]
    frame_type = pci >> 4
    view: dict[str, object] = {
        "transport": {
            0: "isotp-single",
            1: "isotp-first",
            2: "isotp-consecutive",
            3: "isotp-flow-control",
        }.get(frame_type, "unknown"),
    }
    if extension is not None:
        view["address_extension"] = f"0x{extension:02X}"

    pdu_prefix = b""
    if frame_type == 0:
        length = pci & 0x0F
        start = offset + 1
        if length == 0 and len(data) > start:
            length = data[start]
            start += 1
        pdu_prefix = data[start:start + length]
        view["declared_pdu_length"] = length
    elif frame_type == 1 and len(data) >= offset + 2:
        length = ((pci & 0x0F) << 8) | data[offset + 1]
        pdu_prefix = data[offset + 2:]
        view["declared_pdu_length"] = length
    elif frame_type == 2:
        view["sequence_number"] = pci & 0x0F
    elif frame_type == 3:
        view["flow_status"] = pci & 0x0F

    if pdu_prefix:
        sid = pdu_prefix[0]
        view["uds_service"] = f"0x{sid:02X}"
        view["uds_service_name"] = SERVICE_NAMES.get(sid, "unknown")
        view["pdu_prefix_hex"] = pdu_prefix.hex()
        if sid == 0x7F and len(pdu_prefix) >= 3:
            view["negative_for_service"] = f"0x{pdu_prefix[1]:02X}"
            view["negative_response_code"] = f"0x{pdu_prefix[2]:02X}"
    return view


def capture_batch(
    panda: Any,
    can_stream: BinaryIO,
    diagnostic_stream: Any,
    stats: dict[str, Any],
    *,
    now_ns: int | None = None,
) -> int:
    """Persist one receive batch.  There is intentionally no transmit handle."""
    rows = list(panda.can_recv() or [])
    stamp = time.monotonic_ns() if now_ns is None else now_ns
    retained = 0
    for address_raw, data_raw, bus_raw in rows:
        address = int(address_raw)
        data = bytes(data_raw)
        bus = int(bus_raw)
        # Panda TX receipts/rejections use synthetic bus values >= 128.  Since
        # this process never transmits, retain their count as contamination but
        # do not mislabel them as vehicle-bus evidence.
        if not 0 <= bus <= 2:
            stats["nonphysical_rows"] += 1
            continue
        write_canbin_record(can_stream, stamp, bus, address, data)
        retained += 1
        stats["frames_total"] += 1
        stats["frames_by_bus"][str(bus)] += 1
        stats["frames_by_address"][f"0x{address:X}"] += 1
        if 0x700 <= address <= 0x7FF:
            view = _isotp_view(address, data)
            row = {
                "schema": SCHEMA,
                "t_ns": stamp,
                "bus": bus,
                "address": f"0x{address:03X}",
                "route": KNOWN_ROUTES.get(address),
                "data_hex": data.hex(),
                **view,
            }
            diagnostic_stream.write(json.dumps(row, sort_keys=True, separators=(",", ":")) + "\n")
            diagnostic_stream.flush()
            stats["diagnostic_frames"] += 1
            if "uds_service" in view:
                stats["uds_service_hints"][str(view["uds_service"])] += 1
            if address in KNOWN_ROUTES:
                stats["known_route_frames"][KNOWN_ROUTES[address]] += 1
    return retained


def _new_stats() -> dict[str, Any]:
    return {
        "frames_total": 0,
        "frames_by_bus": Counter(),
        "frames_by_address": Counter(),
        "diagnostic_frames": 0,
        "known_route_frames": Counter(),
        "uds_service_hints": Counter(),
        "nonphysical_rows": 0,
    }


def _jsonable_stats(stats: dict[str, Any]) -> dict[str, object]:
    return {
        key: dict(sorted(value.items())) if isinstance(value, Counter) else value
        for key, value in stats.items()
    }


def _establish_receive_boundary(panda: Any) -> dict[str, object]:
    # Batch length is not an emptiness test: the USB transfer capacity depends
    # on CAN payload length.  Clear the board's complete RX queue explicitly.
    # This is a USB control operation and does not submit a CAN data frame.
    panda.can_clear(0xFFFF)
    host_partial = bytes(getattr(panda, "can_rx_overflow_buffer", b""))
    if host_partial:
        raise CaptureError(
            f"Panda host parser retained {len(host_partial)} partial bytes after the RX clear"
        )
    return {"method": "panda.can_clear", "queue": "global-rx", "selector": 0xFFFF}


def _safety_issues(health: dict[str, object], expected_mode: int) -> list[str]:
    issues = []
    if int(health.get("safety_mode", -1)) != expected_mode:
        issues.append(f"safety_mode={health.get('safety_mode')!r}, expected {expected_mode}")
    if health.get("controls_allowed") is not False:
        issues.append(f"controls_allowed={health.get('controls_allowed')!r}, expected false")
    if health.get("heartbeat_lost") is not False:
        issues.append(f"heartbeat_lost={health.get('heartbeat_lost')!r}, expected false")
    return issues


def configure_panda_safety(
    panda: Any,
    mode: int,
    sleep_fn: Callable[[float], None] = time.sleep,
) -> dict[str, object]:
    panda.set_safety_mode(mode, 0)
    # A previous direct client may have disabled the board heartbeat watchdog.
    # Sending a disengaged heartbeat re-enables it before every exit path.
    panda.send_heartbeat(engaged=False)
    sleep_fn(0.05)
    health = dict(panda.health())
    issues = _safety_issues(health, mode)
    return {"verified": not issues, "health": health, "issues": issues}


def configure_passive_panda(panda: Any, sleep_fn: Callable[[float], None] = time.sleep) -> dict[str, object]:
    return configure_panda_safety(panda, NOOUTPUT_SAFETY_MODE, sleep_fn=sleep_fn)


def configure_silent_panda(panda: Any, sleep_fn: Callable[[float], None] = time.sleep) -> dict[str, object]:
    return configure_panda_safety(panda, SILENT_SAFETY_MODE, sleep_fn=sleep_fn)


def configure_capture_can(panda: Any) -> dict[str, object]:
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


def _health_snapshot(panda: Any) -> dict[str, object]:
    return {
        "board": dict(panda.health()),
        "can": {str(bus): dict(panda.can_health(bus)) for bus in range(3)},
    }


def _capture_loss_monitor(
    start: dict[str, Any],
    finish: dict[str, Any],
    frames_by_bus: Counter[str],
) -> dict[str, object]:
    issues: list[str] = []
    global_deltas: dict[str, int] = {}
    bus_deltas: dict[str, dict[str, int]] = {}
    receive_coverage: dict[str, dict[str, int]] = {}

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
    for counter in GLOBAL_CAPTURE_COUNTERS:
        change = delta(counter, start_board, finish_board, "board")
        global_deltas[counter] = change
        if change:
            issues.append(f"board {counter} increased by {change}")
    issues.extend(_safety_issues(finish_board, NOOUTPUT_SAFETY_MODE))

    for bus in range(3):
        label = str(bus)
        before = dict(start["can"][label])
        after = dict(finish["can"][label])
        deltas: dict[str, int] = {}
        for counter in BUS_CAPTURE_COUNTERS:
            change = delta(counter, before, after, f"CAN bus {bus}")
            deltas[counter] = change
            if change:
                issues.append(f"CAN bus {bus} {counter} increased by {change}")
        bus_deltas[label] = deltas
        received_delta = delta("total_rx_cnt", before, after, f"CAN bus {bus}")
        captured = int(frames_by_bus.get(label, 0))
        receive_coverage[label] = {
            "hardware_rx_before_tail_drain": received_delta,
            "captured_frames_after_tail_drain": captured,
        }
        if captured < received_delta:
            issues.append(
                f"CAN bus {bus} captured {captured} frames but hardware received at least "
                f"{received_delta} before the final tail drain"
            )
        if int(after.get("can_speed", -1)) != EXPECTED_CAN_SPEED_KBPS:
            issues.append(
                f"CAN bus {bus} speed={after.get('can_speed')!r}, expected {EXPECTED_CAN_SPEED_KBPS} kbps"
            )
        if int(after.get("can_data_speed", -1)) != EXPECTED_CAN_DATA_SPEED_KBPS:
            issues.append(
                f"CAN bus {bus} data speed={after.get('can_data_speed')!r}, "
                f"expected {EXPECTED_CAN_DATA_SPEED_KBPS} kbps"
            )
        if bool(after.get("canfd_non_iso", True)):
            issues.append(f"CAN bus {bus} finished in non-ISO CAN-FD mode")
        if bool(after.get("bus_off", False)):
            issues.append(f"CAN bus {bus} finished bus-off")

    return {
        "start": start,
        "finish": finish,
        "global_deltas": global_deltas,
        "bus_deltas": bus_deltas,
        "receive_coverage": receive_coverage,
        "issues": issues,
        "valid_for_absence_claims": not issues,
    }


def run_capture_loop(
    panda: Any,
    can_stream: BinaryIO,
    diagnostic_stream: Any,
    *,
    duration_seconds: int,
    monotonic_ns_fn: Callable[[], int] = time.monotonic_ns,
    sleep_fn: Callable[[float], None] = time.sleep,
) -> dict[str, object]:
    passive = configure_passive_panda(panda, sleep_fn=sleep_fn)
    if not passive["verified"]:
        raise CaptureError("Panda NOOUTPUT safety could not be verified: " + "; ".join(passive["issues"]))
    receive_boundary = _establish_receive_boundary(panda)
    try:
        health_start = _health_snapshot(panda)
    except (KeyboardInterrupt, CaptureInterrupted):
        raise
    except BaseException as error:
        raise CaptureError(f"could not snapshot starting Panda/CAN health: {error}") from error

    stats = _new_stats()
    start_ns = monotonic_ns_fn()
    deadline_ns = start_ns + duration_seconds * 1_000_000_000
    next_heartbeat_ns = start_ns
    polls = 0
    interrupted: str | None = None
    try:
        while True:
            now_ns = monotonic_ns_fn()
            if now_ns >= deadline_ns:
                break
            if now_ns >= next_heartbeat_ns:
                panda.send_heartbeat(engaged=False)
                next_heartbeat_ns = now_ns + int(HEARTBEAT_SECONDS * 1_000_000_000)
            capture_batch(panda, can_stream, diagnostic_stream, stats, now_ns=now_ns)
            polls += 1
            sleep_fn(POLL_SECONDS)
    except (KeyboardInterrupt, CaptureInterrupted) as error:
        # Preserve the evidence already written.  The caller still returns a
        # nonzero interrupted status after flushing and reasserting NOOUTPUT.
        interrupted = f"{type(error).__name__}: {error}"
    try:
        # Freeze the hardware receive census first, then make one final bulk RX
        # transfer.  Comparing that census to retained frames detects a tail
        # larger than one transfer without pretending a busy bus becomes empty.
        health_finish = _health_snapshot(panda)
        final_tail_rows = capture_batch(
            panda,
            can_stream,
            diagnostic_stream,
            stats,
            now_ns=monotonic_ns_fn(),
        )
        polls += 1
        loss_monitor = _capture_loss_monitor(
            health_start,
            health_finish,
            stats["frames_by_bus"],
        )
        loss_monitor["final_tail_rows"] = final_tail_rows
    except (KeyboardInterrupt, CaptureInterrupted) as error:
        if interrupted is None:
            interrupted = f"{type(error).__name__}: {error}"
        loss_monitor = {
            "start": health_start,
            "finish": None,
            "issues": [f"capture interrupted during ending health/tail boundary: {interrupted}"],
            "valid_for_absence_claims": False,
        }
    except BaseException as error:
        loss_monitor = {
            "start": health_start,
            "finish": None,
            "issues": [f"could not snapshot ending Panda/CAN health: {type(error).__name__}: {error}"],
            "valid_for_absence_claims": False,
        }
    finish_ns = monotonic_ns_fn()
    return {
        "passive_safety": passive,
        "receive_boundary": receive_boundary,
        "start_monotonic_ns": start_ns,
        "finish_monotonic_ns": finish_ns,
        "elapsed_seconds": (finish_ns - start_ns) / 1_000_000_000,
        "polls": polls,
        "interrupted": interrupted,
        "loss_monitor": loss_monitor,
        "stats": _jsonable_stats(stats),
    }


def _find_conflicting_processes() -> list[str]:
    try:
        completed = subprocess.run(
            ["pgrep", "-af", PANDA_OWNER_CANDIDATE_PATTERN],
            capture_output=True,
            text=True,
            check=False,
        )
    except FileNotFoundError as error:
        raise CaptureError("cannot verify Panda ownership because pgrep is unavailable") from error
    if completed.returncode not in (0, 1):
        raise CaptureError(f"could not verify Panda ownership: {completed.stderr.strip()}")
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
        "stationary": args.confirm_stationary,
        "ignition_on_ready_off": args.confirm_ignition_on_ready_off,
        "stable_12v_support": args.confirm_stable_12v_support,
        "openpilot_stopped": args.confirm_openpilot_stopped,
        "gts_uses_separate_vci": args.confirm_gts_separate_vci,
        "arm_token": args.arm == ARM_TOKEN,
    }
    missing = [name for name, present in required.items() if not present]
    if missing:
        raise CaptureError("live capture preflight failed; missing " + ", ".join(missing))
    if not sys.stdin.isatty() or not sys.stderr.isatty():
        raise CaptureError("live capture requires a real interactive stdin/stderr TTY")
    conflicts = _find_conflicting_processes()
    if conflicts:
        raise CaptureError("refusing Panda USB collision; stop openpilot first: " + "; ".join(conflicts))
    return {**required, "direct_panda_owner_check": "passed"}


def _signal_guard():
    previous: dict[int, Any] = {}

    def handler(signum: int, _frame: Any) -> None:
        raise CaptureInterrupted(signal.Signals(signum).name)

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


def _output_path(requested: str | None) -> Path:
    if requested:
        return Path(requested).expanduser().resolve()
    stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    return (Path.cwd() / "build" / "out" / f"camry-f33-gts-passive-{stamp}").resolve()


def execute_live(args: argparse.Namespace) -> tuple[dict[str, object], int]:
    result: dict[str, object] = {
        **build_plan(args.duration_seconds, args.output_dir),
        "mode": "execute",
        "started_utc": _utc_now(),
        "status": "starting",
    }
    panda = None
    summary_path: Path | None = None
    try:
        result["preflight"] = _validate_preflight(args)
        try:
            from panda import Panda
        except ImportError as error:
            raise CaptureError("cannot import Panda; run from the comma/openpilot Panda environment") from error
        serials = Panda.list(usb_only=True)
        if len(serials) != 1:
            raise CaptureError(f"expected exactly one directly connected USB Panda, found {len(serials)}: {serials}")
        panda = Panda(serials[0], disable_checks=False)
        if not panda.is_connected_usb():
            raise CaptureError("passive capture requires a directly connected USB Panda")
        initial_passive = configure_passive_panda(panda)
        result["initial_nooutput"] = initial_passive
        if not initial_passive["verified"]:
            raise CaptureError(
                "Panda NOOUTPUT safety could not be verified immediately after opening: "
                + "; ".join(initial_passive["issues"])
            )
        can_format = configure_capture_can(panda)
        result["capture_can_format"] = can_format
        if not can_format["verified"]:
            raise CaptureError("Panda CAN format setup failed: " + "; ".join(can_format["issues"]))

        output_dir = _output_path(args.output_dir)
        if output_dir.exists():
            raise CaptureError(f"output path already exists; refusing overwrite: {output_dir}")
        output_dir.mkdir(parents=True, exist_ok=False)
        can_path = output_dir / "can.bin"
        diagnostic_path = output_dir / "diagnostic.ndjson"
        summary_path = output_dir / "summary.json"
        result["output"] = {
            "directory": str(output_dir),
            "can": str(can_path),
            "diagnostic": str(diagnostic_path),
            "summary": str(summary_path),
        }
        result["hardware"] = {"panda_usb_serial": serials[0], "direct_usb": True}

        with can_path.open("xb") as can_stream, diagnostic_path.open("x", encoding="utf-8") as diagnostic_stream:
            write_canbin_header(can_stream)
            with _signal_guard():
                capture = run_capture_loop(
                    panda,
                    can_stream,
                    diagnostic_stream,
                    duration_seconds=args.duration_seconds,
                )
            can_stream.flush()
            diagnostic_stream.flush()
            os.fsync(can_stream.fileno())
            os.fsync(diagnostic_stream.fileno())
        result["capture"] = capture
        if capture["interrupted"] is not None:
            result["status"] = "interrupted"
            result["terminal_reason"] = capture["interrupted"]
        elif capture["loss_monitor"]["valid_for_absence_claims"]:
            result["status"] = "capture-complete"
        else:
            result["status"] = "capture-evidence-limited"
            result["terminal_reason"] = "; ".join(capture["loss_monitor"]["issues"])
    except (KeyboardInterrupt, CaptureInterrupted) as error:
        result["status"] = "interrupted"
        result["terminal_reason"] = f"{type(error).__name__}: {error}"
    except CaptureError as error:
        result["status"] = "refused" if panda is None else "stopped"
        result["terminal_reason"] = str(error)
    except BaseException as error:
        result["status"] = "error"
        result["terminal_reason"] = f"{type(error).__name__}: {error}"
    finally:
        if panda is not None:
            try:
                final_silent = configure_silent_panda(panda)
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
        result["finished_utc"] = _utc_now()
        if summary_path is not None:
            try:
                summary_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
            except BaseException as error:
                result["summary_write_error"] = f"{type(error).__name__}: {error}"
                if result.get("status") == "capture-complete":
                    result["status"] = "error"
                    result["terminal_reason"] = "summary persistence failed"

    if result["status"] == "capture-complete":
        return result, 0
    if result["status"] == "interrupted":
        return result, 130
    if result["status"] == "unsafe-stop":
        return result, 4
    if result["status"] == "capture-evidence-limited":
        return result, 3
    return result, 2


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute", action="store_true", help="open Panda only after every preflight gate passes")
    parser.add_argument("--duration-seconds", type=int, default=DEFAULT_DURATION_SECONDS)
    parser.add_argument("--output-dir")
    parser.add_argument("--arm")
    parser.add_argument("--confirm-stationary", action="store_true")
    parser.add_argument("--confirm-ignition-on-ready-off", action="store_true")
    parser.add_argument("--confirm-stable-12v-support", action="store_true")
    parser.add_argument("--confirm-openpilot-stopped", action="store_true")
    parser.add_argument("--confirm-gts-separate-vci", action="store_true")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if not MIN_DURATION_SECONDS <= args.duration_seconds <= MAX_DURATION_SECONDS:
        print(
            f"duration must be between {MIN_DURATION_SECONDS} and {MAX_DURATION_SECONDS} seconds",
            file=sys.stderr,
        )
        return 2
    if not args.execute:
        print(json.dumps(build_plan(args.duration_seconds, args.output_dir), indent=2, sort_keys=True))
        return 0
    result, returncode = execute_live(args)
    print(json.dumps(result, indent=2, sort_keys=True))
    if returncode == 4:
        print(
            "URGENT: final Panda SILENT safety was not verified; disconnect the Panda or stop all owners "
            "until its state is checked.",
            file=sys.stderr,
        )
    return returncode


if __name__ == "__main__":
    raise SystemExit(main())
