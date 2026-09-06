#!/usr/bin/env python3
"""Exact-F33 read-only steering-state capture using the ECU's native XCP DAQ.

This tool exists to answer the remaining 2026 Camry stock-lateral question:
which exact-F33 LocalRAM term/gate changes when Toyota publishes an active
0x08A request, and how that value propagates through the recovered steering
command/current funnel?

No ephemeral resident is required for the preferred path. Exact 8965F3307000
already implements measurement-only XCP DAQ on CAN 0x7F7 -> 0x7F8.  Exact
firmware constants configure four DAQ lists, four ODTs per list, and seven
one-byte measurements per ODT.  The target profiles are:

* ``source-terms``: 28 bytes covering every D0218 input/gate plus CC48;
* ``command-funnel``: 28 bytes covering CC48 through CC4C/CC4E/CC60/CC50/
  CC62/CC66/CC64 and the AC54 motor-driving / AC56 diagnostic mirrors;
* ``full-path``: the 52-byte unique union, using lists 0 and 1 in the same
  firmware event so CC48 is sampled once and source-to-output propagation can
  be observed without reproducing the operating condition in a second run.

The source addresses are read-only measurement pointers.  The only XCP
configuration requests are CONNECT, CLEAR_DAQ_LIST, SET_DAQ_PTR, WRITE_DAQ
(pointer configuration only), SET_DAQ_LIST_MODE, START, and STOP.  The target
firmware's DAQ worker dereferences those pointers and copies one byte to DTO
staging; STIM/direction mode is rejected.  This tool never emits DOWNLOAD,
MODIFY_BITS, page-copy, B6, 0x08A, or any steering command.

While DAQ runs, selected native CAN witnesses are captured in the same Panda
receive loop.  Their host monotonic timestamps are batch-observation times, not
wire timestamps.  Four or eight ODT DTOs (depending on profile) are grouped by
the firmware's ascending list/PID order into one event sample; that grouping is
a coherent ECU DAQ event, not an atomic CPU snapshot.

The exact current post-repin route is Panda bus 0, ELM327 param 1.  F33 RSCFD
controller 1 owns both physical EPS UDS 0x7A1 and application XCP 0x7F7, so the
live route follows the already live-proven post-repin EPS diagnostic channel.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from exploit.common.ram_exec import (  # noqa: E402
    ELM327_SAFETY_MODE,
    RX_ADDR,
    TX_ADDR,
    RamExecError,
    _import_uds,
    _read_f181,
    ensure_boardd_stopped,
)
from exploit.followups.xcp_daq_probe import (  # noqa: E402
    ENTRIES_PER_ODT,
    MAX_ENTRIES,
    ODTS_PER_LIST,
    XcpDaqError,
    _exchange_control,
    _parse_control_response,
    assert_no_write_commands,
    clear_daq_list_request,
    control_rtt_statistics,
    set_daq_list_mode_request,
    set_daq_ptr_request,
    start_stop_daq_list_request,
    validate_addresses,
    write_daq_request,
)

SCHEMA = "camry-f33-steering-state-capture-v1"
EXPECTED_F181_HEX = "023839363546333330373030300000000038413331313333303331303000000000"
PANDA_BUS = 0
ELM327_PARAM = 1
DEFAULT_DAQ_PRESCALER = 10
XCP_REQUEST_ID = 0x7F7
XCP_RESPONSE_ID = 0x7F8

# Keep only the steering/reference/context family needed for offline joins.
CAN_WITNESS_IDS = frozenset((0x025, 0x030, 0x081, 0x08A, 0x0B6, 0x0FE, 0x371, 0x412))


@dataclass(frozen=True)
class Field:
    name: str
    address: int
    width: int
    signed: bool
    role: str

    @property
    def byte_addresses(self) -> tuple[int, ...]:
        return tuple(self.address + i for i in range(self.width))


@dataclass(frozen=True)
class Profile:
    name: str
    description: str
    fields: tuple[Field, ...]

    @property
    def addresses(self) -> tuple[int, ...]:
        return tuple(address for field in self.fields for address in field.byte_addresses)


SOURCE_TERMS = Profile(
    "source-terms",
    "all exact D0218 input terms/gates plus CC48 output",
    (
        Field("AC2B_diag_gate", 0xFEBEAC2B, 1, False, "D0218 branch gate; 0x5A selects the reduced branch"),
        Field("C7BF_b6_active", 0xFEBEC7BF, 1, False, "B6/cooperative-path activity gate in D0218"),
        Field("C43C_assist_term", 0xFEBEC43C, 2, True, "D0218 additive short term"),
        Field("C4C0_assist_term", 0xFEBEC4C0, 4, True, "D0218 additive 32-bit term"),
        Field("C3BA_assist_term", 0xFEBEC3BA, 2, True, "D0218 additive short term"),
        Field("CC2C_assist_term", 0xFEBECC2C, 4, True, "D0218 additive 32-bit term"),
        Field("BF3C_assist_term", 0xFEBEBF3C, 4, True, "D0218 additive 32-bit term"),
        Field("CB38_assist_term", 0xFEBECB38, 2, True, "input to the bounded CB38+C5EE contribution"),
        Field("C5EE_moving_term", 0xFEBEC5EE, 2, True, "moving/mode contribution paired with CB38"),
        Field("CBE8_assist_term", 0xFEBECBE8, 2, True, "final D0218 short contribution"),
        Field("CC48_d0218_output", 0xFEBECC48, 4, True, "D0218 summed steering-command intermediate"),
    ),
)

COMMAND_FUNNEL = Profile(
    "command-funnel",
    "exact CC48-to-AC54/AC56 recovered steering command/current funnel",
    (
        Field("CC48_d0218_output", 0xFEBECC48, 4, True, "D0218 summed steering-command intermediate"),
        Field("CC4C_bounded", 0xFEBECC4C, 2, True, "D0284 bounded/scaled CC48 result"),
        Field("CC4E_slewed", 0xFEBECC4E, 2, True, "D02DA optional slew result"),
        Field("AC52_limit", 0xFEBEAC52, 2, True, "D0382 symmetric magnitude limit"),
        Field("CC60_limited", 0xFEBECC60, 2, True, "D0382 limited CC4E"),
        Field("CC50_pre_scale", 0xFEBECC50, 2, True, "D039E pre-scale steering-command value"),
        Field("AC5A_scale", 0xFEBEAC5A, 2, False, "D042C unsigned scale multiplier"),
        Field("AC4C_slew_limit", 0xFEBEAC4C, 2, True, "D042C symmetric CC62-to-CC66 limit"),
        Field("CC62_pre_slew", 0xFEBECC62, 2, True, "D042C scaled command; Command Value Torque diagnostic sibling"),
        Field("CC66_post_slew", 0xFEBECC66, 2, True, "D042C post-limit/post-gate command"),
        Field("CC64_selected", 0xFEBECC64, 2, True, "D047C selected command entering output snapshot"),
        Field("AC54_motor_branch", 0xFEBEAC54, 2, True, "D0AAE motor-driving branch copied from CC64"),
        Field("AC56_diag_branch", 0xFEBEAC56, 2, True, "D0AAE diagnostic sibling copied from CC62"),
    ),
)

FULL_PATH = Profile(
    "full-path",
    "single-event union of all D0218 source terms/gates and the downstream command funnel",
    SOURCE_TERMS.fields + tuple(field for field in COMMAND_FUNNEL.fields if field.name != "CC48_d0218_output"),
)

PROFILES: dict[str, Profile] = {p.name: p for p in (SOURCE_TERMS, COMMAND_FUNNEL, FULL_PATH)}


def profile_list_chunks(profile: Profile) -> tuple[tuple[int, ...], ...]:
    addresses = profile.addresses
    return tuple(tuple(addresses[i:i + MAX_ENTRIES]) for i in range(0, len(addresses), MAX_ENTRIES))


def profile_odt_groups(profile: Profile) -> tuple[tuple[int, ...], ...]:
    groups: list[tuple[int, ...]] = []
    for chunk in profile_list_chunks(profile):
        groups.extend(tuple(chunk[i:i + ENTRIES_PER_ODT]) for i in range(0, len(chunk), ENTRIES_PER_ODT))
    return tuple(groups)


def validate_profile(profile: Profile) -> None:
    addresses = profile.addresses
    if not addresses:
        raise ValueError(f"profile {profile.name} is empty")
    if len(addresses) > MAX_ENTRIES * 4:
        raise ValueError(f"profile {profile.name} exceeds exact F33's four-list DAQ geometry")
    if len(set(addresses)) != len(addresses):
        raise ValueError(f"profile {profile.name} contains overlapping byte addresses")
    for chunk in profile_list_chunks(profile):
        validate_addresses(chunk)
    groups = profile_odt_groups(profile)
    expected = sum((len(chunk) + ENTRIES_PER_ODT - 1) // ENTRIES_PER_ODT for chunk in profile_list_chunks(profile))
    if len(groups) != expected or any(len(group) > ENTRIES_PER_ODT for group in groups):
        raise ValueError(f"profile {profile.name} has invalid ODT layout")


for _profile in PROFILES.values():
    validate_profile(_profile)


def decode_profile_bytes(profile: Profile, values: dict[int, int]) -> dict[str, int]:
    out: dict[str, int] = {}
    for field in profile.fields:
        try:
            raw = bytes(values[address] for address in field.byte_addresses)
        except KeyError as exc:
            raise ValueError(f"profile sample missing address 0x{int(exc.args[0]):08X}") from exc
        out[field.name] = int.from_bytes(raw, "little", signed=field.signed)
    return out


def profile_manifest(profile: Profile) -> dict[str, Any]:
    return {
        "name": profile.name,
        "description": profile.description,
        "byte_count": len(profile.addresses),
        "daq_list_count": len(profile_list_chunks(profile)),
        "odt_count": len(profile_odt_groups(profile)),
        "fields": [
            {
                "name": field.name,
                "address": f"0x{field.address:08X}",
                "width": field.width,
                "signed": field.signed,
                "role": field.role,
            }
            for field in profile.fields
        ],
    }


def camry_configuration_requests(profile: Profile, *, prescaler: int) -> tuple[tuple[str, bytes], ...]:
    if not 1 <= prescaler <= 0xFF:
        raise XcpDaqError("DAQ prescaler must be 1..255")
    chunks = profile_list_chunks(profile)
    requests: list[tuple[str, bytes]] = [("connect", bytes.fromhex("ff00000000000000"))]
    for list_index, chunk in enumerate(chunks):
        requests.append((f"clear_daq_list_{list_index}", clear_daq_list_request(list_index)))
        groups = tuple(chunk[i:i + ENTRIES_PER_ODT] for i in range(0, len(chunk), ENTRIES_PER_ODT))
        for odt, group in enumerate(groups):
            requests.append((f"set_daq_ptr_list_{list_index}_odt_{odt}", set_daq_ptr_request(list_index, odt, 0)))
            for entry, address in enumerate(group):
                requests.append((f"write_daq_list_{list_index}_odt_{odt}_entry_{entry}", write_daq_request(address)))
        requests.append((f"set_daq_list_mode_{list_index}", set_daq_list_mode_request(list_index, prescaler=prescaler)))
    for list_index in range(len(chunks)):
        requests.append((f"start_daq_list_{list_index}", start_stop_daq_list_request(True, list_index)))
    assert_no_write_commands(requests)
    return tuple(requests)


def stop_camry_daq(panda: Any, *, list_count: int, bus: int, timeout: float, timings: list[dict[str, Any]] | None = None) -> None:
    for list_index in reversed(range(list_count)):
        operation = f"stop_daq_list_{list_index}"
        request = start_stop_daq_list_request(False, list_index)
        response = _exchange_control(panda, bus=bus, request=request, timeout=timeout, operation=operation, timings=timings)
        _parse_control_response(response, operation)


def configure_camry_daq(
    panda: Any, *, profile: Profile, bus: int, timeout: float, prescaler: int
) -> tuple[dict[str, int], list[dict[str, Any]]]:
    requests = camry_configuration_requests(profile, prescaler=prescaler)
    timings: list[dict[str, Any]] = []
    started_lists: list[int] = []
    try:
        for operation, request in requests:
            if operation.startswith("start_daq_list_"):
                list_index = int(operation.rsplit("_", 1)[1])
                started_lists.append(list_index)  # timeout after TX may still mean started
            response = _exchange_control(
                panda, bus=bus, request=request, timeout=timeout, operation=operation, timings=timings
            )
            parsed = _parse_control_response(response, operation)
            if operation.startswith("start_daq_list_"):
                list_index = int(operation.rsplit("_", 1)[1])
                expected_pid = list_index * ODTS_PER_LIST
                if parsed[1] != expected_pid:
                    raise XcpDaqError(
                        f"list {list_index} start response first PID 0x{parsed[1]:02X}, expected 0x{expected_pid:02X}"
                    )
    except Exception:
        for list_index in reversed(started_lists):
            try:
                operation = f"cleanup_stop_daq_list_{list_index}"
                request = start_stop_daq_list_request(False, list_index)
                response = _exchange_control(panda, bus=bus, request=request, timeout=timeout, operation=operation)
                _parse_control_response(response, operation)
            except Exception:
                pass
        raise
    return {
        "configuration_requests": len(requests),
        "daq_list_count": len(profile_list_chunks(profile)),
        "odt_count": len(profile_odt_groups(profile)),
        "entry_count": len(profile.addresses),
        "prescaler": prescaler,
    }, timings


def decode_profile_dto(data: bytes, profile: Profile) -> dict[str, Any] | None:
    if len(data) != 8:
        raise XcpDaqError("DAQ DTO must be exactly eight bytes")
    pid = data[0]
    groups = profile_odt_groups(profile)
    if pid >= len(groups):
        return None
    group = groups[pid]
    return {
        "pid": pid,
        "values": [
            {"address": f"0x{address:08X}", "value": data[1 + i]}
            for i, address in enumerate(group)
        ],
    }


def plan(profile: Profile, *, prescaler: int = DEFAULT_DAQ_PRESCALER) -> dict[str, Any]:
    return {
        "schema": SCHEMA,
        "mode": "plan",
        "target": "8965F3307000",
        "expected_f181_hex": EXPECTED_F181_HEX,
        "route": {
            "panda_bus": PANDA_BUS,
            "elm327_param": ELM327_PARAM,
            "xcp_request": f"0x{XCP_REQUEST_ID:03X}",
            "xcp_response": f"0x{XCP_RESPONSE_ID:03X}",
            "basis": "exact F33 RSCFD controller1 owns both 0x7A1 UDS and 0x7F7 XCP; post-repin EPS UDS is live on Panda bus0",
        },
        "operation": "read-only native-XCP-DAQ LocalRAM observation plus passive CAN witnesses",
        "daq_prescaler": prescaler,
        "profile": profile_manifest(profile),
        "can_witness_ids": [f"0x{x:03X}" for x in sorted(CAN_WITNESS_IDS)],
        "mutation_boundary": {
            "source_memory_writes": False,
            "steering_commands": False,
            "b6_transmit": False,
            "flash_writes": False,
            "ephemeral_resident": False,
            "volatile_xcp_daq_configuration": True,
        },
        "timing_boundary": (
            "DAQ ODTs are grouped by PID order into ECU-event samples; host monotonic timestamps and "
            "Panda receive batches are not physical wire timestamps or atomic CPU snapshots; raw Panda busTime is retained without assigning units"
        ),
    }


class EventAssembler:
    """Assemble one/two-list ODT PIDs into one complete profile event."""

    def __init__(self, profile: Profile):
        self.profile = profile
        self.addresses = profile.addresses
        self.groups = profile_odt_groups(profile)
        self.expected_pids = set(range(len(self.groups)))
        self._values: dict[int, int] = {}
        self._seen_pids: set[int] = set()
        self._started_ns: int | None = None
        self._bus_times: list[int] = []
        self.complete = 0
        self.dropped_partial = 0
        self.out_of_order = 0

    def feed(self, data: bytes, observed_ns: int, bus_time: int | None = None) -> dict[str, Any] | None:
        dto = decode_profile_dto(data, self.profile)
        if dto is None:
            return None
        pid = int(dto["pid"])
        if pid == 0:
            if self._seen_pids:
                self.dropped_partial += 1
            self._values = {}
            self._seen_pids = set()
            self._bus_times = []
            self._started_ns = observed_ns
        elif not self._seen_pids:
            self.out_of_order += 1
            return None
        if pid in self._seen_pids:
            self.out_of_order += 1
            return None
        self._seen_pids.add(pid)
        if bus_time is not None:
            self._bus_times.append(bus_time)
        for row in dto["values"]:
            self._values[int(row["address"], 16)] = int(row["value"])
        if self._seen_pids != self.expected_pids:
            return None
        decoded = decode_profile_bytes(self.profile, self._values)
        self.complete += 1
        result = {
            "type": "ram_sample",
            "sample_index": self.complete - 1,
            "profile": self.profile.name,
            "started_monotonic_ns": self._started_ns,
            "completed_monotonic_ns": observed_ns,
            "assembly_span_ns": observed_ns - int(self._started_ns or observed_ns),
            "panda_bus_time_raw": list(self._bus_times),
            "values": decoded,
        }
        self._values = {}
        self._seen_pids = set()
        self._bus_times = []
        self._started_ns = None
        return result

    def finish(self) -> None:
        if self._seen_pids:
            self.dropped_partial += 1
            self._values = {}
            self._seen_pids = set()
            self._bus_times = []
            self._started_ns = None


def _panda_row(row: Any) -> tuple[int, int, bytes, int] | None:
    if len(row) < 4:
        return None
    try:
        return int(row[0]), int(row[1]), bytes(row[-2]), int(row[-1])
    except (TypeError, ValueError):
        return None


def capture_loop(
    panda: Any,
    *,
    profile: Profile,
    duration_seconds: float,
    max_ram_samples: int,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    if duration_seconds <= 0:
        raise ValueError("duration must be positive")
    if max_ram_samples <= 0:
        raise ValueError("max RAM sample count must be positive")
    assembler = EventAssembler(profile)
    records: list[dict[str, Any]] = []
    can_counts: Counter[tuple[int, int, int]] = Counter()
    dto_frames = 0
    started_mono = time.monotonic()
    started_wall = datetime.now(timezone.utc).isoformat(timespec="milliseconds")
    deadline = started_mono + duration_seconds
    while time.monotonic() < deadline and assembler.complete < max_ram_samples:
        batch_ns = time.monotonic_ns()
        for row in panda.can_recv():
            parsed = _panda_row(row)
            if parsed is None:
                continue
            address, bus_time, data, bus = parsed
            if address == XCP_RESPONSE_ID and bus == PANDA_BUS and len(data) == 8:
                # FF/FE are command responses/errors, not DAQ DTOs.
                if data[0] not in (0xFE, 0xFF):
                    dto_frames += 1
                    assembled = assembler.feed(data, batch_ns, bus_time)
                    if assembled is not None:
                        records.append(assembled)
                continue
            if address in CAN_WITNESS_IDS and bus < 128:
                can_counts[(bus, address, len(data))] += 1
                records.append({
                    "type": "can",
                    "observed_monotonic_ns": batch_ns,
                    "bus": bus,
                    "panda_bus_time_raw": bus_time,
                    "address": f"0x{address:03X}",
                    "dlc": len(data),
                    "data": data.hex(),
                })
        time.sleep(0.001)
    assembler.finish()
    finished_mono = time.monotonic()
    return records, {
        "started_monotonic": started_mono,
        "finished_monotonic": finished_mono,
        "started_wall_utc": started_wall,
        "finished_wall_utc": datetime.now(timezone.utc).isoformat(timespec="milliseconds"),
        "elapsed_seconds": finished_mono - started_mono,
        "ram_samples": assembler.complete,
        "observed_ram_sample_rate_hz": assembler.complete / (finished_mono - started_mono) if finished_mono > started_mono else None,
        "dto_frames": dto_frames,
        "dropped_partial_ram_samples": assembler.dropped_partial,
        "out_of_order_dto_frames": assembler.out_of_order,
        "can_counts": [
            {"bus": bus, "address": f"0x{address:03X}", "dlc": dlc, "count": count}
            for (bus, address, dlc), count in sorted(can_counts.items())
        ],
        "stopped_by_sample_cap": assembler.complete >= max_ram_samples,
    }


def run_live(profile: Profile, *, duration_seconds: float, max_ram_samples: int, timeout: float, prescaler: int) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    ensure_boardd_stopped()
    try:
        from panda import Panda
    except ImportError as exc:
        raise RamExecError("cannot import panda; execute on the comma/openpilot environment") from exc

    uds_mod = _import_uds()
    panda = Panda()
    panda.set_safety_mode(ELM327_SAFETY_MODE, ELM327_PARAM)
    uds_client = uds_mod.UdsClient(
        panda, TX_ADDR, RX_ADDR, PANDA_BUS, timeout=0.1, response_pending_timeout=1.0
    )
    f181_hex, f181_ascii = _read_f181(uds_client, uds_mod)
    if f181_hex is None or f181_hex.lower() != EXPECTED_F181_HEX:
        raise XcpDaqError(f"F181 mismatch: expected {EXPECTED_F181_HEX}, observed {f181_hex}")

    blocked_before = int(panda.health()["safety_tx_blocked"])
    configured = False
    control_timings: list[dict[str, Any]] = []
    config_counts: dict[str, int] = {}
    records: list[dict[str, Any]] = []
    capture_meta: dict[str, Any] = {}
    try:
        config_counts, control_timings = configure_camry_daq(
            panda, profile=profile, bus=PANDA_BUS, timeout=timeout, prescaler=prescaler
        )
        configured = True
        records, capture_meta = capture_loop(
            panda,
            profile=profile,
            duration_seconds=duration_seconds,
            max_ram_samples=max_ram_samples,
        )
    finally:
        if configured:
            stop_camry_daq(
                panda, list_count=len(profile_list_chunks(profile)), bus=PANDA_BUS, timeout=timeout, timings=control_timings
            )

    blocked_after = int(panda.health()["safety_tx_blocked"])
    if blocked_after != blocked_before:
        raise XcpDaqError("Panda blocked at least one XCP DAQ request; discard the run")
    if capture_meta.get("ram_samples", 0) == 0:
        raise XcpDaqError("XCP configured but no complete profile RAM sample was observed")
    return records, {
        "route": {"bus": PANDA_BUS, "elm327_param": ELM327_PARAM},
        "f181_hex": f181_hex,
        "f181_ascii": f181_ascii,
        "panda_safety_tx_blocked_delta": blocked_after - blocked_before,
        "configuration": config_counts,
        "control_timing": {
            "requests": control_timings,
            "rtt_statistics": control_rtt_statistics(control_timings),
        },
        "capture": capture_meta,
    }


def write_records(path: Path, records: Iterable[dict[str, Any]]) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as stream:
        for row in records:
            stream.write(json.dumps(row, sort_keys=True) + "\n")
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--profile", choices=tuple(PROFILES), default="full-path")
    ap.add_argument("--execute", action="store_true")
    ap.add_argument(
        "--stock-observation-confirmed",
        action="store_true",
        help="required live acknowledgement: openpilot control is stopped and this run is observation-only",
    )
    ap.add_argument("--duration-seconds", type=float, default=10.0)
    ap.add_argument("--max-ram-samples", type=int, default=10000)
    ap.add_argument("--timeout", type=float, default=0.25)
    ap.add_argument("--daq-prescaler", type=int, default=DEFAULT_DAQ_PRESCALER, help="XCP DAQ event prescaler (1..255); default 10")
    ap.add_argument("--capture-output", type=Path)
    ap.add_argument("--result-output", type=Path)
    args = ap.parse_args()

    try:
        profile = PROFILES[args.profile]
        if not 1 <= args.daq_prescaler <= 0xFF:
            raise XcpDaqError("--daq-prescaler must be 1..255")
        result = plan(profile, prescaler=args.daq_prescaler)
        records: list[dict[str, Any]] = []
        live = None
        capture_sha = None
        if args.execute:
            if not args.stock_observation_confirmed:
                raise XcpDaqError("--execute requires --stock-observation-confirmed")
            if args.capture_output is None:
                raise XcpDaqError("live execution requires --capture-output")
            records, live = run_live(
                profile,
                duration_seconds=args.duration_seconds,
                max_ram_samples=args.max_ram_samples,
                timeout=args.timeout,
                prescaler=args.daq_prescaler,
            )
            capture_sha = write_records(args.capture_output, records)
            result["mode"] = "live"
        elif args.stock_observation_confirmed:
            raise XcpDaqError("--stock-observation-confirmed is meaningful only with --execute")

        result["created_at"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
        result["capture"] = {
            "output": str(args.capture_output) if args.capture_output is not None else None,
            "sha256": capture_sha,
            "record_count": len(records),
        }
        result["live"] = live
        if args.result_output is not None:
            args.result_output.parent.mkdir(parents=True, exist_ok=True)
            args.result_output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
        print(json.dumps(result, indent=2, sort_keys=True))
        return 0
    except (OSError, ValueError, XcpDaqError, RamExecError) as exc:
        ap.error(str(exc))


if __name__ == "__main__":
    raise SystemExit(main())
