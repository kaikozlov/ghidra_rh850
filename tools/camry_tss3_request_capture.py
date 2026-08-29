#!/usr/bin/env python3
"""Synchronized read-only Brake/FRC TSS3-request capture for the exact 2026 Camry.

This is the OQ-052 longitudinal discriminator acquisition tool. It polls the
two OEM-named read-only request surfaces identified by TMS-085/VAR-069 in one
USB-owner loop with a common monotonic clock:

- Brake `0x7B0` (RX `0x7B8`, category 435 `ABS_P5`) DIDs `0x10A1..0x10A4`,
  explicitly named ``... from Toyota Safety Sense`` request acceleration and
  request/deceleration IDs;
- FRC `0x792` (RX `0x79A`, category 498 `FRC_P5`) DIDs `0x1B03..0x1B07`, the
  upper-limit ISA request vocabulary.

Every request is a classic-CAN single-frame UDS ReadDataByIdentifier
``03 22 <DID>`` in the default diagnostic session. There is no
DiagnosticSessionControl, SecurityAccess, RoutineControl, WriteDataByIdentifier,
or any transmit other than those nine fixed RDBI frames plus one ISO-TP
flow-control frame per multiframe response (FRC DID ``0x1B05`` declares a
five-byte value record, so its positive response cannot fit a single frame).
Responses are reassembled single-frame or first/consecutive-frame PDUs.
Negative responses are retained with their NRC; positive payloads are decoded
through the tracked Toyota diagnostics registry and its canonical
``p5-linear-msb0-v1`` decoder contract — no ad-hoc value scale lives in this
file.

All incoming Panda buses 0..2 are retained in the same compact ``can.bin``
format used by :mod:`tools.camry_frc_lta_capture`, whose pandad ownership guard,
ELM327 safety configuration, and canbin plumbing are reused directly. The
companion analyzer is :mod:`tools.analyze_camry_tss3_request_capture`.

Live PID support on this car is **unmeasured**; this tool records whatever the
ECUs answer and claims nothing about runtime behavior until a live artifact is
retained and analyzed.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[1]
for _path in (str(REPO), str(REPO / "tools" / "techstream")):
    if _path not in sys.path:
        sys.path.insert(0, _path)

from tools.camry_frc_lta_capture import (
    ELM327_PARAM,
    ELM327_SAFETY_MODEL,
    find_pandad_processes,
    load_panda_class,
    write_canbin_header,
    write_canbin_record,
)
from ddb_semantics import decode_p5_signal

REGISTRY_PATH = REPO / "data/generated/gtsplus_2026/toyota_diag_registry_camry_2026.json"
EXPECTED_SCHEMA = "toyota-diagnostics-registry-v4"
EXPECTED_PROFILE = "camry-2026-f33"
DIAG_BUS = 0
DEFAULT_POLL_HZ = 2.0
MAX_POLL_HZ = 10.0
# VAR-069 pins the exact Camry brake diagnostic pair 0x7B0 -> 0x7B8; the
# 2026-08-27 post-repin DTC sweep live-reached 0x7B0 on Panda bus 0 (live-baseline
# report §17). FRC 0x792 -> 0x79A is the live-proven route behind VAR-064 that
# tools/camry_frc_lta_capture.py already polls.
BRAKE_TX = 0x7B0
BRAKE_RX = 0x7B8
FRC_TX = 0x792
FRC_RX = 0x79A
ROUTE_SOURCE = (
    "post-repin Panda bus0: FRC 0x792 live-proven by the relay-correct 2026-08-27 "
    "sweep (VAR-064); Brake 0x7B0 live-reached by the same sweep's DTC read "
    "(0x7B0->0x7B8 pinned by VAR-069)"
)
# (ecu key, TX, RX, registry category, target DIDs)
TARGET_ECUS = (
    ("brake", BRAKE_TX, BRAKE_RX, 435, (0x10A1, 0x10A2, 0x10A3, 0x10A4)),
    ("frc", FRC_TX, FRC_RX, 498, (0x1B03, 0x1B04, 0x1B05, 0x1B06, 0x1B07)),
)
P5_DECODER = "p5-linear-msb0-v1"
FLOW_CONTROL_FRAME = bytes((0x30, 0x00, 0x00)) + bytes(5)
MAX_RESPONSE_BYTES = 64
ASSEMBLY_TIMEOUT_NS = 200_000_000


@dataclass(frozen=True)
class SignalSpec:
    name: str
    bit_start: int
    bit_end: int
    mul: int
    div: int
    offset: int
    signed: bool
    decimal_point_count: int
    patterns: dict[int, str | None]
    unit: str | None


@dataclass(frozen=True)
class DidTarget:
    ecu: str
    tx: int
    rx: int
    did: int
    request: bytes
    signals: tuple[SignalSpec, ...]

    @property
    def key(self) -> str:
        return f"{self.ecu}/0x{self.did:04X}"


def rdbi_request_frame(did: int) -> bytes:
    """Fixed read-only single-frame request: 03 22 DID 00*5 (default session)."""
    return bytes((0x03, 0x22, (did >> 8) & 0xFF, did & 0xFF)) + bytes(4)


def load_registry(path: Path = REGISTRY_PATH) -> dict[str, Any]:
    registry = json.loads(path.read_text())
    profile = registry.get("profile", {})
    if registry.get("schema") != EXPECTED_SCHEMA or profile.get("profile") != EXPECTED_PROFILE:
        raise SystemExit(
            f"registry {path} is not {EXPECTED_SCHEMA}/{EXPECTED_PROFILE}; refusing to guess routes")
    if profile.get("panda_bus") != DIAG_BUS:
        raise SystemExit(f"registry profile panda_bus is not {DIAG_BUS}; refusing to guess routes")
    ecus = {row["key"]: row for row in profile.get("ecus", [])}
    for ecu_key, tx, _rx, _category, _dids in TARGET_ECUS:
        if ecus.get(ecu_key, {}).get("address") != tx:
            raise SystemExit(
                f"registry ECU {ecu_key!r} is not at 0x{tx:03X}; refusing to guess routes")
    return registry


def build_did_table(registry: dict[str, Any]) -> tuple[DidTarget, ...]:
    """Resolve the pinned (ECU, DID) poll set from the tracked registry."""
    targets: list[DidTarget] = []
    for ecu_key, tx, rx, category, dids in TARGET_ECUS:
        catalog = registry["catalogs"].get(str(category))
        if catalog is None:
            raise SystemExit(f"registry is missing category {category} for ECU {ecu_key!r}")
        catalog_dids = catalog["dids"]
        for did in dids:
            rows = catalog_dids.get(f"0x{did:04X}")
            if not rows:
                raise SystemExit(
                    f"registry category {category} is missing DID 0x{did:04X} for ECU {ecu_key!r}")
            signals = []
            for row in rows:
                if row.get("decoder") != P5_DECODER:
                    raise SystemExit(
                        f"registry DID 0x{did:04X} signal {row['name']!r} does not use "
                        f"{P5_DECODER}; refusing ad-hoc decode")
                signals.append(SignalSpec(
                    name=row["name"],
                    bit_start=row["bit_start"],
                    bit_end=row["bit_end"],
                    mul=row["mul"],
                    div=row["div"],
                    offset=row["offset"],
                    signed=row["signed"],
                    decimal_point_count=row["decimal_point_count"],
                    patterns={int(key): value for key, value in row.get("patterns", {}).items()},
                    unit=row.get("unit"),
                ))
            targets.append(DidTarget(ecu=ecu_key, tx=tx, rx=rx, did=did,
                                     request=rdbi_request_frame(did),
                                     signals=tuple(signals)))
    return tuple(targets)


def decode_signals(target: DidTarget, payload: bytes) -> list[dict[str, Any]]:
    """Decode every registry signal of one DID payload; never raise on short payloads."""
    decoded = []
    for signal in target.signals:
        row: dict[str, Any] = {
            "name": signal.name,
            "bit_start": signal.bit_start,
            "bit_end": signal.bit_end,
        }
        try:
            result = decode_p5_signal(
                payload,
                bit_start=signal.bit_start,
                bit_end=signal.bit_end,
                mul=signal.mul,
                div=signal.div,
                offset=signal.offset,
                signed=signal.signed,
                decimal_point_count=signal.decimal_point_count,
                patterns=signal.patterns,
            )
        except ValueError as exc:
            row["decode_error"] = str(exc)
        else:
            row.update(result)
            if signal.unit is not None:
                row["unit"] = signal.unit
        decoded.append(row)
    return decoded


def parse_response_pdu(pdu: bytes, ecu_targets: tuple[DidTarget, ...]) -> dict[str, Any] | None:
    """Parse one reassembled UDS response PDU against one responder's polled DID set.

    ``ecu_targets`` must already be scoped to the responder address so a DID
    number echoed from the wrong ECU cannot be mis-attributed.
    """
    if not pdu:
        return None
    if pdu[0] == 0x62 and len(pdu) >= 4:
        did = (pdu[1] << 8) | pdu[2]
        for target in ecu_targets:
            if did == target.did:
                return {
                    "ecu": target.ecu,
                    "did": f"0x{did:04X}",
                    "status": "positive",
                    "raw": pdu[3:].hex(),
                    "signals": decode_signals(target, pdu[3:]),
                }
        return None
    if pdu[0] == 0x7F and len(pdu) >= 3 and pdu[1] == 0x22:
        # ISO 14229 negative responses carry no DID echo; attribute per ECU only.
        return {
            "ecu": ecu_targets[0].ecu,
            "did": None,
            "status": "negative",
            "nrc": f"0x{pdu[2]:02X}",
            "raw_pdu": pdu.hex(),
        }
    return None


def plan(targets: tuple[DidTarget, ...]) -> dict[str, Any]:
    return {
        "operation": "single-Panda passive all-CAN capture plus synchronized read-only "
                     "Brake/FRC TSS3-request RDBI polling",
        "schema": "camry-tss3-request-capture-v1",
        "diag_bus": DIAG_BUS,
        "route_source": ROUTE_SOURCE,
        "requests": [
            {
                "ecu": target.ecu,
                "tx": f"0x{target.tx:03X}",
                "rx": f"0x{target.rx:03X}",
                "did": f"0x{target.did:04X}",
                "request": target.request.hex(),
                "signals": [
                    {"name": signal.name,
                     "bits": f"{signal.bit_start}..{signal.bit_end}",
                     "unit": signal.unit,
                     "patterns": {str(key): value for key, value in signal.patterns.items()}}
                    for signal in target.signals
                ],
            }
            for target in targets
        ],
        "decoder": {
            "source": "data/generated/gtsplus_2026/toyota_diag_registry_camry_2026.json",
            "contract": P5_DECODER,
            "payload_origin": "UDS DID value bytes (positive SID/DID echo excluded)",
            "implementation": "tools/techstream/ddb_semantics.py::decode_p5_signal",
        },
        "poll_hz_default_per_did": DEFAULT_POLL_HZ,
        "synchronization": "round-robin over every (ECU, DID) with one common monotonic clock; "
                           "queries and responses are timestamped in oracle.ndjson",
        "transport": "receive-side ISO-TP assembly of single-frame and first/consecutive-frame "
                     "positive and negative responses; the only non-request transmit is one "
                     "flow-control frame (30 00) per multiframe response, as required to "
                     "complete the read",
        "safety": {"model": "ELM327", "numeric": ELM327_SAFETY_MODEL, "param": ELM327_PARAM},
        "hard_guard": "refuse execution while pandad is running; one process must own Panda USB",
        "session_control": False,
        "security_access": False,
        "routine_control": False,
        "vehicle_control_tx": False,
        "flash_write": False,
        "boundary": "live PID support on the exact Camry is unmeasured; this plan claims "
                    "tooling only, not any live result",
    }


def _oracle_write(stream, row: dict[str, Any]) -> None:
    stream.write(json.dumps(row, sort_keys=True, separators=(",", ":")) + "\n")
    stream.flush()


class PendingAssembly:
    """One in-progress multiframe response (classic-CAN ISO-TP FF/CF)."""

    __slots__ = ("t0_ns", "total", "data", "next_sn", "frames")

    def __init__(self, t0_ns: int, total: int, first: bytes, frame_hex: str) -> None:
        self.t0_ns = t0_ns
        self.total = total
        self.data = bytearray(first[:total])
        self.next_sn = 1
        self.frames = [frame_hex]

    def feed(self, frame: bytes) -> bool:
        """Append one consecutive frame; return True when the PDU is complete."""
        self.frames.append(frame.hex())
        self.data.extend(frame[1:])
        sn = frame[0] & 0x0F
        self.next_sn = (sn + 1) & 0x0F
        return len(self.data) >= self.total


def _emit_response(oracle_stream, stats: dict, *, t_ns: int, bus: int, address: int,
                   parsed: dict[str, Any], frames: list[str] | None) -> None:
    row = {"type": "response", "t_ns": t_ns, "bus": bus, "address": f"0x{address:03X}", **parsed}
    if frames is not None:
        row["transport"] = "multiframe"
        row["frames"] = frames
    else:
        row["transport"] = "single-frame"
    _oracle_write(oracle_stream, row)
    bucket = stats["responses"][parsed["ecu"]]
    if parsed["status"] == "positive":
        bucket["positive_by_did"][parsed["did"]] += 1
    else:
        bucket["negative"] += 1
        bucket["nrc"][parsed["nrc"]] += 1


def _expire_stale(pending: dict[int, PendingAssembly], oracle_stream, stats: dict,
                  *, now_ns: int) -> None:
    for address, assembly in list(pending.items()):
        if now_ns - assembly.t0_ns <= ASSEMBLY_TIMEOUT_NS:
            continue
        del pending[address]
        _oracle_write(oracle_stream, {
            "type": "response",
            "t_ns": now_ns,
            "address": f"0x{address:03X}",
            "ecu": stats["rx_ecu"][address],
            "status": "assembly_timeout",
            "frames": assembly.frames,
            "partial_pdu": bytes(assembly.data).hex(),
        })


def _capture_messages(panda, can_stream, oracle_stream, targets_by_rx, *,
                      stats: dict, pending: dict[int, PendingAssembly],
                      now_ns: int | None = None) -> None:
    """Drain one Panda batch, persist incoming buses 0..2, retain matching responses.

    ``now_ns`` overrides the receive timestamp for deterministic tests.
    """
    msgs = panda.can_recv() or []
    recv_ns = time.monotonic_ns() if now_ns is None else now_ns
    _expire_stale(pending, oracle_stream, stats, now_ns=recv_ns)
    for address, data, bus in msgs:
        # Echo/rejected frames use synthetic bus numbers >=128. Preserve only
        # actual incoming vehicle buses in the bulk capture.
        if 0 <= bus <= 2:
            write_canbin_record(can_stream, recv_ns, bus, address, data)
            stats["frames_by_bus"][str(bus)] += 1
            ecu_targets = targets_by_rx.get(address)
            if ecu_targets is None:
                continue
            frame = bytes(data)
            pci = frame[0] >> 4 if frame else -1
            if pci == 0:
                # A new single frame supersedes any stale partial assembly.
                pending.pop(address, None)
                length = frame[0] & 0x0F
                parsed = parse_response_pdu(frame[1:1 + length], ecu_targets)
                if parsed is not None:
                    _emit_response(oracle_stream, stats, t_ns=recv_ns, bus=bus,
                                   address=address, parsed=parsed, frames=None)
            elif pci == 1 and len(frame) >= 2:
                total = ((frame[0] & 0x0F) << 8) | frame[1]
                if total > MAX_RESPONSE_BYTES:
                    continue
                # One flow-control frame to the ECU's request address is
                # required to receive the consecutive frames at all.
                panda.can_send(ecu_targets[0].tx, FLOW_CONTROL_FRAME, DIAG_BUS)
                assembly = PendingAssembly(recv_ns, total,
                                            frame[2:], frame.hex())
                if len(assembly.data) >= total:
                    parsed = parse_response_pdu(bytes(assembly.data), ecu_targets)
                    if parsed is not None:
                        _emit_response(oracle_stream, stats, t_ns=recv_ns, bus=bus,
                                       address=address, parsed=parsed, frames=assembly.frames)
                else:
                    pending[address] = assembly
            elif pci == 2 and address in pending:
                assembly = pending[address]
                sn = frame[0] & 0x0F
                if sn != assembly.next_sn:
                    del pending[address]
                    _oracle_write(oracle_stream, {
                        "type": "response", "t_ns": recv_ns, "bus": bus,
                        "address": f"0x{address:03X}", "ecu": ecu_targets[0].ecu,
                        "status": "assembly_sequence_error",
                        "frames": assembly.frames + [frame.hex()],
                    })
                    continue
                if assembly.feed(frame):
                    del pending[address]
                    parsed = parse_response_pdu(bytes(assembly.data[:assembly.total]), ecu_targets)
                    if parsed is not None:
                        _emit_response(oracle_stream, stats, t_ns=recv_ns, bus=bus,
                                       address=address, parsed=parsed, frames=assembly.frames)


def execute(out_dir: Path, *, duration_s: float | None, poll_hz: float) -> int:
    if poll_hz <= 0 or poll_hz > MAX_POLL_HZ:
        raise SystemExit(f"--poll-hz must be >0 and <={MAX_POLL_HZ:g}")
    running = find_pandad_processes()
    if running:
        details = "; ".join(f"pid={pid} {cmd}" for pid, cmd in running)
        raise SystemExit(f"refusing Panda USB collision: pandad is running ({details})")

    registry = load_registry()
    targets = build_did_table(registry)
    targets_by_rx: dict[int, tuple[DidTarget, ...]] = {}
    for target in targets:
        targets_by_rx.setdefault(target.rx, tuple(t for t in targets if t.rx == target.rx))

    Panda = load_panda_class()
    serials = Panda.list()
    if len(serials) != 1:
        raise SystemExit(f"expected exactly one Panda, found {len(serials)}: {serials}")

    out_dir.mkdir(parents=True, exist_ok=False)
    can_path = out_dir / "can.bin"
    oracle_path = out_dir / "oracle.ndjson"
    meta_path = out_dir / "metadata.json"
    stats: dict[str, Any] = {
        "frames_by_bus": Counter({"0": 0, "1": 0, "2": 0}),
        "queries": {target.key: 0 for target in targets},
        "responses": {ecu: {"positive_by_did": Counter(), "negative": 0, "nrc": Counter()}
                      for ecu in dict.fromkeys(target.ecu for target in targets)},
        "rx_ecu": {rx: targets_[0].ecu for rx, targets_ in targets_by_rx.items()},
    }
    started_wall = time.time()
    started_ns = time.monotonic_ns()
    pending: dict[int, PendingAssembly] = {}
    error: str | None = None

    panda = Panda(serials[0])
    try:
        panda.set_safety_mode(ELM327_SAFETY_MODEL, ELM327_PARAM)
        with can_path.open("wb", buffering=1024 * 1024) as can_stream, \
                oracle_path.open("w", buffering=1) as oracle_stream:
            write_canbin_header(can_stream)
            _oracle_write(oracle_stream, {"type": "meta", "t_ns": started_ns, "plan": plan(targets)})
            # Drain the initial backlog into the retained capture. Both target
            # routes are already live-proven on Panda bus 0; do not probe
            # unrelated buses.
            for _ in range(3):
                _capture_messages(panda, can_stream, oracle_stream, targets_by_rx,
                                  stats=stats, pending=pending)

            # poll_hz is per DID; round-robin every (ECU, DID) so brake and FRC
            # state share one monotonic timeline without back-to-back queries
            # to a single ECU.
            query_spacing_ns = int(1e9 / (poll_hz * len(targets)))
            next_query_ns = time.monotonic_ns()
            query_index = 0
            stop_ns = None if duration_s is None else started_ns + int(duration_s * 1e9)
            last_guard_ns = 0
            while stop_ns is None or time.monotonic_ns() < stop_ns:
                now_ns = time.monotonic_ns()
                if now_ns - last_guard_ns >= 1_000_000_000:
                    if find_pandad_processes():
                        raise RuntimeError("pandad appeared during capture; aborting to protect Panda USB ownership")
                    last_guard_ns = now_ns
                if now_ns >= next_query_ns:
                    target = targets[query_index]
                    panda.can_send(target.tx, target.request, DIAG_BUS)
                    stats["queries"][target.key] += 1
                    _oracle_write(oracle_stream, {
                        "type": "query",
                        "t_ns": now_ns,
                        "bus": DIAG_BUS,
                        "ecu": target.ecu,
                        "address": f"0x{target.tx:03X}",
                        "did": f"0x{target.did:04X}",
                        "request": target.request.hex(),
                    })
                    query_index = (query_index + 1) % len(targets)
                    while next_query_ns <= now_ns:
                        next_query_ns += query_spacing_ns
                _capture_messages(panda, can_stream, oracle_stream, targets_by_rx,
                                  stats=stats, pending=pending)
    except KeyboardInterrupt:
        error = "keyboard_interrupt"
    except Exception as exc:
        error = f"{type(exc).__name__}: {exc}"
        raise
    finally:
        finished_ns = time.monotonic_ns()
        metadata = {
            "schema": "camry-tss3-request-capture-v1",
            "plan": plan(targets),
            "panda_serial": serials[0],
            "diag_bus": DIAG_BUS,
            "started_unix_s": started_wall,
            "started_monotonic_ns": started_ns,
            "finished_monotonic_ns": finished_ns,
            "duration_s": (finished_ns - started_ns) / 1e9,
            "error": error,
            "frames_by_bus": dict(stats["frames_by_bus"]),
            "queries": dict(stats["queries"]),
            "responses": {
                ecu: {"positive_by_did": dict(bucket["positive_by_did"]),
                      "positive": sum(bucket["positive_by_did"].values()),
                      "negative": bucket["negative"],
                      "nrc": dict(bucket["nrc"])}
                for ecu, bucket in stats["responses"].items()
            },
            "files": {"can": can_path.name, "oracle": oracle_path.name},
        }
        meta_path.write_text(json.dumps(metadata, indent=2, sort_keys=True) + "\n")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--execute", action="store_true", help="perform the read-only capture; default prints the plan")
    ap.add_argument("--out", type=Path, help="new output directory (required with --execute)")
    ap.add_argument("--duration", type=float, help="capture seconds; omit to run until Ctrl-C")
    ap.add_argument("--poll-hz", type=float, default=DEFAULT_POLL_HZ,
                    help=f"poll rate per DID across the round-robin (default: {DEFAULT_POLL_HZ:g} Hz each)")
    args = ap.parse_args()
    if not args.execute:
        targets = build_did_table(load_registry())
        print(json.dumps(plan(targets), indent=2, sort_keys=True))
        return 0
    if args.out is None:
        ap.error("--out is required with --execute")
    return execute(args.out, duration_s=args.duration, poll_hz=args.poll_hz)


if __name__ == "__main__":
    raise SystemExit(main())
