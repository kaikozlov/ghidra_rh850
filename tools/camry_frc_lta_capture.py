#!/usr/bin/env python3
"""Capture exact-Camry FRC LTA state and all Panda CAN traffic with one USB owner.

This is a read-only diagnostic capture helper for the remaining VAR-063/065/066
live discriminator.  It deliberately refuses to run while ``pandad`` owns the
Panda, avoiding the checksum/USB collision that invalidated the earlier
parallel-reader capture.

The only transmitted vehicle request is classic-CAN UDS ReadDataByIdentifier
for FRC_P5 DID 0x1601::

    0x792  03 22 16 01 00 00 00 00

A positive single-frame response is::

    0x79A  07 62 16 01 SS LL HC HH

where the four data bytes are Toyota/GTS+ ``LTA Switch Condition Flag``,
``LTA Control Condition``, ``Hands-Off Customize Condition Flag``, and
``Hands-Off Control Condition`` respectively.

The CAN stream is stored in a compact binary format so a Python process on the
comma can sustain the full relay-correct traffic rate without JSON/gzip work in
the receive loop.  Oracle requests/responses are separately retained as NDJSON.
"""
from __future__ import annotations

import argparse
import json
import struct
import sys
import time
from collections import Counter
from collections.abc import Iterable
from pathlib import Path
from typing import BinaryIO

FRC_TX = 0x792
FRC_RX = 0x79A
FRC_DID = 0x1601
ELM327_SAFETY_MODEL = 3
ELM327_PARAM = 1
UDS_RDBI_REQUEST = bytes.fromhex("0322160100000000")
CANBIN_MAGIC = b"CAMFRC1\0"
CANBIN_HEADER = struct.Struct("<QIBB")  # monotonic_ns, address, bus, dlc
DEFAULT_POLL_HZ = 10.0
LTA_SWITCH_LABELS = {0: "OFF", 1: "ON"}
LTA_CONTROL_LABELS = {0: "LTA Enabled", 1: "LTA Disabled"}
HANDS_OFF_CUSTOMIZE_LABELS = {0: "OFF", 1: "ON"}
HANDS_OFF_CONTROL_LABELS = {0: "Hands-Off Enabled", 1: "Hands-off Disabled"}


def positive_1601_payload(frame: bytes) -> bytes | None:
    if len(frame) != 8 or frame[:4] != bytes.fromhex("07621601"):
        return None
    return frame[4:8]


def parse_1601_frame(frame: bytes) -> dict | None:
    payload = positive_1601_payload(frame)
    if payload is not None:
        return {
            "status": "positive",
            "raw": payload.hex(),
            "lta_switch_condition": payload[0],
            "lta_control_condition": payload[1],
            "hands_off_customize_condition": payload[2],
            "hands_off_control_condition": payload[3],
            "lta_switch_label": LTA_SWITCH_LABELS.get(payload[0]),
            "lta_control_label": LTA_CONTROL_LABELS.get(payload[1]),
            "hands_off_customize_label": HANDS_OFF_CUSTOMIZE_LABELS.get(payload[2]),
            "hands_off_control_label": HANDS_OFF_CONTROL_LABELS.get(payload[3]),
            "lta_enabled_oracle": payload[0] == 1 and payload[1] == 0,
        }
    # Single-frame negative response to SID 0x22: 03 7F 22 NRC ...
    if len(frame) == 8 and frame[0] == 0x03 and frame[1:3] == b"\x7f\x22":
        return {"status": "negative", "nrc": frame[3], "raw_frame": frame.hex()}
    return None


def write_canbin_header(stream: BinaryIO) -> None:
    stream.write(CANBIN_MAGIC)


def write_canbin_record(stream: BinaryIO, t_ns: int, bus: int, address: int, data: bytes) -> None:
    if not (0 <= bus <= 255):
        raise ValueError(f"invalid bus: {bus}")
    if not (0 <= address <= 0x1FFFFFFF):
        raise ValueError(f"invalid CAN address: {address:#x}")
    if len(data) > 64:
        raise ValueError(f"invalid CAN payload length: {len(data)}")
    stream.write(CANBIN_HEADER.pack(t_ns, address, bus, len(data)))
    stream.write(data)


def iter_canbin_records(stream: BinaryIO) -> Iterable[tuple[int, int, int, bytes]]:
    magic = stream.read(len(CANBIN_MAGIC))
    if magic != CANBIN_MAGIC:
        raise ValueError(f"bad CANBIN magic: {magic!r}")
    while True:
        raw = stream.read(CANBIN_HEADER.size)
        if not raw:
            return
        if len(raw) != CANBIN_HEADER.size:
            raise ValueError("truncated CANBIN record header")
        t_ns, address, bus, dlc = CANBIN_HEADER.unpack(raw)
        data = stream.read(dlc)
        if len(data) != dlc:
            raise ValueError("truncated CANBIN payload")
        yield t_ns, bus, address, data


def _process_cmdlines_linux() -> list[tuple[int, str]]:
    proc = Path("/proc")
    if not proc.is_dir():
        return []
    rows: list[tuple[int, str]] = []
    for child in proc.iterdir():
        if not child.name.isdigit():
            continue
        try:
            cmdline = (child / "cmdline").read_bytes().replace(b"\0", b" ").decode(errors="replace").strip()
        except (FileNotFoundError, PermissionError, ProcessLookupError):
            continue
        if cmdline:
            rows.append((int(child.name), cmdline))
    return rows


def cmdline_is_pandad(cmdline: str) -> bool:
    for word in cmdline.split():
        name = Path(word).name
        if name in {"pandad", "_pandad"} or name.startswith("pandad-") or word.endswith(".pandad.pandad"):
            return True
    return False


def find_pandad_processes() -> list[tuple[int, str]]:
    return [(pid, cmdline) for pid, cmdline in _process_cmdlines_linux() if cmdline_is_pandad(cmdline)]


def load_panda_class():
    try:
        from panda import Panda  # type: ignore
        return Panda
    except ModuleNotFoundError:
        for candidate in (Path("/data/openpilot"), Path("/data/openpilot/current")):
            if candidate.is_dir():
                sys.path.insert(0, str(candidate))
                try:
                    from panda import Panda  # type: ignore
                    return Panda
                except ModuleNotFoundError:
                    pass
    raise SystemExit("cannot import panda.Panda; run from the comma openpilot environment")


def _oracle_write(stream, row: dict) -> None:
    stream.write(json.dumps(row, sort_keys=True, separators=(",", ":")) + "\n")
    stream.flush()


def _capture_messages(panda, can_stream: BinaryIO, oracle_stream, *, diag_bus: int | None,
                      stats: dict, stop_ns: int | None = None) -> list[int]:
    """Drain one Panda batch, persist incoming buses 0..2, return positive-1601 buses."""
    msgs = panda.can_recv() or []
    recv_ns = time.monotonic_ns()
    positive_buses: list[int] = []
    for address, data, bus in msgs:
        # Echo/rejected frames use synthetic bus numbers >=128.  Preserve only
        # actual incoming vehicle buses in the bulk capture.
        if 0 <= bus <= 2:
            write_canbin_record(can_stream, recv_ns, bus, address, data)
            stats["frames_by_bus"][str(bus)] += 1
            if address == 0x0B6:
                stats["b6_by_bus"][str(bus)] += 1
            if address == FRC_RX:
                parsed = parse_1601_frame(data)
                if parsed is not None:
                    _oracle_write(oracle_stream, {
                        "type": "response",
                        "t_ns": recv_ns,
                        "bus": bus,
                        "address": f"0x{address:03X}",
                        **parsed,
                    })
                    if parsed["status"] == "positive":
                        stats["oracle_positive"] += 1
                        stats["lta_control_counts"][str(parsed["lta_control_condition"])] += 1
                        positive_buses.append(bus)
                    else:
                        stats["oracle_negative"] += 1
        if stop_ns is not None and recv_ns >= stop_ns:
            break
    return positive_buses


def auto_probe_diag_bus(panda, can_stream: BinaryIO, oracle_stream, stats: dict,
                        buses: tuple[int, ...] = (0, 1, 2), wait_s: float = 0.18) -> int:
    positives: set[int] = set()
    for bus in buses:
        t_ns = time.monotonic_ns()
        panda.can_send(FRC_TX, UDS_RDBI_REQUEST, bus)
        _oracle_write(oracle_stream, {
            "type": "query",
            "phase": "probe",
            "t_ns": t_ns,
            "bus": bus,
            "address": f"0x{FRC_TX:03X}",
            "request": UDS_RDBI_REQUEST.hex(),
        })
        deadline = time.monotonic() + wait_s
        while time.monotonic() < deadline:
            positives.update(_capture_messages(panda, can_stream, oracle_stream, diag_bus=None, stats=stats))
    if len(positives) != 1:
        raise RuntimeError(
            f"0x1601 probe did not resolve one diagnostic bus; positive buses={sorted(positives)}. "
            "Re-run with --diag-bus after reviewing oracle.ndjson."
        )
    return next(iter(positives))


def plan() -> dict:
    return {
        "operation": "single-Panda passive all-CAN capture plus read-only FRC SID22 polling",
        "tx": f"0x{FRC_TX:03X}",
        "rx": f"0x{FRC_RX:03X}",
        "did": f"0x{FRC_DID:04X}",
        "request_frame": UDS_RDBI_REQUEST.hex(),
        "poll_hz_default": DEFAULT_POLL_HZ,
        "gtsplus_value_dictionary": {
            "lta_switch_condition": LTA_SWITCH_LABELS,
            "lta_control_condition": LTA_CONTROL_LABELS,
            "hands_off_customize_condition": HANDS_OFF_CUSTOMIZE_LABELS,
            "hands_off_control_condition": HANDS_OFF_CONTROL_LABELS,
        },
        "lta_enabled_oracle": "switch=ON (1) and control=LTA Enabled (0)",
        "safety": {"model": "ELM327", "numeric": ELM327_SAFETY_MODEL, "param": ELM327_PARAM},
        "hard_guard": "refuse execution while pandad is running; one process must own Panda USB",
        "vehicle_control_tx": False,
        "flash_write": False,
        "security_access": False,
        "routine_control": False,
    }


def execute(out_dir: Path, *, diag_bus: int | None, duration_s: float | None, poll_hz: float) -> int:
    if poll_hz <= 0 or poll_hz > 25:
        raise SystemExit("--poll-hz must be >0 and <=25")
    running = find_pandad_processes()
    if running:
        details = "; ".join(f"pid={pid} {cmd}" for pid, cmd in running)
        raise SystemExit(f"refusing Panda USB collision: pandad is running ({details})")

    Panda = load_panda_class()
    serials = Panda.list()
    if len(serials) != 1:
        raise SystemExit(f"expected exactly one Panda, found {len(serials)}: {serials}")

    out_dir.mkdir(parents=True, exist_ok=False)
    can_path = out_dir / "can.bin"
    oracle_path = out_dir / "oracle.ndjson"
    meta_path = out_dir / "metadata.json"
    stats = {
        "frames_by_bus": Counter({"0": 0, "1": 0, "2": 0}),
        "b6_by_bus": Counter({"0": 0, "1": 0, "2": 0}),
        "oracle_positive": 0,
        "oracle_negative": 0,
        "lta_control_counts": Counter(),
    }
    started_wall = time.time()
    started_ns = time.monotonic_ns()
    selected_bus = diag_bus
    error: str | None = None

    panda = Panda(serials[0])
    try:
        panda.set_safety_mode(ELM327_SAFETY_MODEL, ELM327_PARAM)
        with can_path.open("wb", buffering=1024 * 1024) as can_stream, oracle_path.open("w", buffering=1) as oracle_stream:
            write_canbin_header(can_stream)
            _oracle_write(oracle_stream, {"type": "meta", "t_ns": started_ns, "plan": plan()})
            # Drain initial backlog into the retained capture before probing.
            for _ in range(3):
                _capture_messages(panda, can_stream, oracle_stream, diag_bus=None, stats=stats)
            if selected_bus is None:
                selected_bus = auto_probe_diag_bus(panda, can_stream, oracle_stream, stats)
            if selected_bus not in (0, 1, 2):
                raise RuntimeError(f"invalid selected diagnostic bus: {selected_bus}")

            interval_ns = int(1e9 / poll_hz)
            next_query_ns = time.monotonic_ns()
            stop_ns = None if duration_s is None else started_ns + int(duration_s * 1e9)
            last_guard_ns = 0
            while stop_ns is None or time.monotonic_ns() < stop_ns:
                now_ns = time.monotonic_ns()
                if now_ns - last_guard_ns >= 1_000_000_000:
                    if find_pandad_processes():
                        raise RuntimeError("pandad appeared during capture; aborting to protect Panda USB ownership")
                    last_guard_ns = now_ns
                if now_ns >= next_query_ns:
                    panda.can_send(FRC_TX, UDS_RDBI_REQUEST, selected_bus)
                    _oracle_write(oracle_stream, {
                        "type": "query",
                        "phase": "capture",
                        "t_ns": now_ns,
                        "bus": selected_bus,
                        "address": f"0x{FRC_TX:03X}",
                        "request": UDS_RDBI_REQUEST.hex(),
                    })
                    while next_query_ns <= now_ns:
                        next_query_ns += interval_ns
                _capture_messages(panda, can_stream, oracle_stream, diag_bus=selected_bus, stats=stats, stop_ns=stop_ns)
    except KeyboardInterrupt:
        error = "keyboard_interrupt"
    except Exception as exc:
        error = f"{type(exc).__name__}: {exc}"
        raise
    finally:
        finished_ns = time.monotonic_ns()
        metadata = {
            "schema": "camry-frc-lta-capture-v1",
            "plan": plan(),
            "panda_serial": serials[0],
            "diag_bus": selected_bus,
            "started_unix_s": started_wall,
            "started_monotonic_ns": started_ns,
            "finished_monotonic_ns": finished_ns,
            "duration_s": (finished_ns - started_ns) / 1e9,
            "error": error,
            "frames_by_bus": dict(stats["frames_by_bus"]),
            "b6_by_bus": dict(stats["b6_by_bus"]),
            "oracle_positive": stats["oracle_positive"],
            "oracle_negative": stats["oracle_negative"],
            "lta_control_counts": dict(stats["lta_control_counts"]),
            "files": {"can": can_path.name, "oracle": oracle_path.name},
        }
        meta_path.write_text(json.dumps(metadata, indent=2, sort_keys=True) + "\n")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--execute", action="store_true", help="perform the read-only capture; default prints the plan")
    ap.add_argument("--out", type=Path, help="new output directory (required with --execute)")
    ap.add_argument("--diag-bus", type=int, choices=(0, 1, 2), help="skip read-only 0x1601 bus auto-probe")
    ap.add_argument("--duration", type=float, help="capture seconds; omit to run until Ctrl-C")
    ap.add_argument("--poll-hz", type=float, default=DEFAULT_POLL_HZ)
    args = ap.parse_args()
    if not args.execute:
        print(json.dumps(plan(), indent=2, sort_keys=True))
        return 0
    if args.out is None:
        ap.error("--out is required with --execute")
    return execute(args.out, diag_bus=args.diag_bus, duration_s=args.duration, poll_hz=args.poll_hz)


if __name__ == "__main__":
    raise SystemExit(main())
