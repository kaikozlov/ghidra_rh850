#!/usr/bin/env python3
"""Convert retained Camry CAN captures to P1M-E machine event scenarios.

Accepts panda JSON (``t``, ``addr``, ``bus``, ``data``, ``len``) and comma route
NDJSON (``[segment, logMonoTime_ns, src, address, data_hex]``), including gzip.
For the selected bus, emits post-filter ``can-rx`` and EPS ``can-tx-complete``
events using the Camry 8965F3307000 CodeFlash tables below.

The ``.scenario.json`` records the capture identity and event schedule for
the replay runner. Event boundaries are 5 ms foreground-period indices,
multiplied by ``--cycle-instructions``. The ``.candump.log`` contains the
converted traffic; the ``.quantization.json`` counts drops, reorderings,
same-period RX repeats, and payload-length mismatches.
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import struct
from collections import Counter
from pathlib import Path

from tools import REPO_ROOT
from tools.emulation.p1me_machine import SCENARIO_SCHEMA

IMAGE = REPO_ROOT / "firmware" / "camry-8965F3307000" / "CodeFlash.bin"
IMAGE_SHA256 = "42dce8efc42f6ae31718e7713fa2d26bb9191b4a82439778aee4d7afded9b0e7"

# Camry 8965F3307000 CodeFlash: GAFL routes, RX descriptors, and CanIf TX records.
ROUTE_TABLE = 0x230B8
ROUTE_COUNT = 43
RX_DESCRIPTORS = 0x21FE8
DIAG_RULES = 0x23368
DIAG_COUNT = 2
TX_RECORDS = 0x21F58
TX_COUNT = 12

RX_FIFO = 5  # common FIFO 5 = RSCFD channel 1, within-channel index 2
PERIOD_US = 5_000  # EPS foreground period at the nominal 80 MHz timer domain
PERIOD_S = PERIOD_US / 1_000_000

# Retained LocalRAM snapshot used by the emitted scenario template.
SNAPSHOT = REPO_ROOT / "targets/camry-2026/raw-20260826/secoc-recovery/ram/local_ram_pe1.bin"
SNAPSHOT_SHA256 = "0ddef478b15bcf3241c56573463eda25ba018081629daf0042fcae1204c435a7"
RAM_BASE = 0xFEBE0000
RETURN_STUB = 0x798
LANDING = (0xFEBFF9F0, 0xFEBFFBFC)
CONTROL_RANGES = (
    (0xFEBE5628, 0xFEBE562C),
    (0xFEBF117C, 0xFEBF1184),
    (0xFEBF1194, 0xFEBF11A4),
    (0xFEBF11C0, 0xFEBF11D8),
    (0xFEBF131C, 0xFEBF1328),
    (0xFEBF6B04, 0xFEBF6B08),
)
REGISTERS = {"sp": "0xfebe2000", "gp": "0xfebeb800", "tp": "0x23dfc",
             "lp": hex(RETURN_STUB), "PSW": "0x20", "PMR": "0xff00"}

FD_FLAG = 0x40000000
EXT_FLAG = 0x80000000

# CanIf handle -> channel-1 transmit mailbox, per camry-f33-eps-tx.md section 3.
HANDLE_MAILBOX = {0: 0, 1: 3}


class CaptureFormatError(ValueError):
    pass


def sha256_file(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def decode_firmware_rules() -> tuple[dict[int, dict], dict[int, dict]]:
    """Decode RX rules and EPS transmit records from the registered image."""
    image = IMAGE.read_bytes()
    if hashlib.sha256(image).hexdigest() != IMAGE_SHA256:
        raise RuntimeError("exact CodeFlash identity drifted")

    rx_rules: dict[int, dict] = {}
    for index in range(ROUTE_COUNT):
        rule_id, label_word, fifo_word, zero = struct.unpack_from("<4I", image, ROUTE_TABLE + index * 16)
        if fifo_word != 2 or zero != 0:
            raise RuntimeError("route FIFO/padding columns drifted")
        desc_id, dlc = struct.unpack_from("<II", image, RX_DESCRIPTORS + index * 8)
        if desc_id & ~(FD_FLAG | EXT_FLAG) != rule_id:
            raise RuntimeError("RX descriptors and route table disagree")
        rx_rules[rule_id] = {
            "rule": index,
            "label": label_word >> 16,
            "fifo": RX_FIFO,
            "fd": bool(desc_id & FD_FLAG),
            "extended": bool(desc_id & EXT_FLAG),
            "dlc": dlc,
        }
    for offset in range(DIAG_COUNT):
        rule_id, label_word, gaflfdp, zero = struct.unpack_from("<4I", image, DIAG_RULES + offset * 16)
        if zero != 0 or (gaflfdp & (gaflfdp - 1)) != 0 or not 0x100 <= gaflfdp <= 0x2000:
            raise RuntimeError("diagnostic GAFL rule columns drifted")
        fifo = gaflfdp.bit_length() - 9  # one-hot GAFLFDP bit 8+k
        if fifo != RX_FIFO:
            raise RuntimeError("diagnostic rule targets an unexpected FIFO")
        rx_rules[rule_id] = {
            "rule": ROUTE_COUNT + offset,
            "label": label_word >> 16,
            "fifo": fifo,
            "fd": False,
            "extended": False,
            "dlc": None,
        }

    tx_rules: dict[int, dict] = {}
    for index in range(TX_COUNT):
        record_id, handle_word = struct.unpack_from("<II", image, TX_RECORDS + index * 8)
        rule_id = record_id & ~FD_FLAG & ~EXT_FLAG
        handle = handle_word >> 16
        if handle not in HANDLE_MAILBOX:
            continue  # diagnostic request records (handle 8) are never EPS-origin
        tx_rules.setdefault(rule_id, {
            "handle": handle,
            "fd": bool(record_id & FD_FLAG),
            "extended": bool(record_id & EXT_FLAG),
            "buffer": 16 + HANDLE_MAILBOX[handle],
        })
    return rx_rules, tx_rules


def load_panda_capture(path: Path, raw: bytes) -> dict:
    data = json.loads(raw)
    frames = data.get("frames")
    if not isinstance(frames, list) or not frames:
        raise CaptureFormatError(f"{path}: capture has no frame rows")
    parsed = []
    for index, row in enumerate(frames):
        if not isinstance(row, dict):
            raise CaptureFormatError(f"{path}: frame {index} is not an object")
        try:
            t = float(row["t"])
            addr = int(row["addr"])
            bus = int(row["bus"])
            payload = bytes.fromhex(row["data"])
            recorded_len = int(row["len"])
        except (KeyError, TypeError, ValueError) as exc:
            raise CaptureFormatError(f"{path}: frame {index} malformed: {exc}") from exc
        if t < 0:
            raise CaptureFormatError(f"{path}: frame {index} has negative timestamp")
        if len(payload) != recorded_len:
            raise CaptureFormatError(
                f"{path}: frame {index} recorded len {recorded_len} but data holds {len(payload)} bytes")
        parsed.append({"index": index, "t": t, "addr": addr, "bus": bus, "data": payload})
    return {"header": data, "format": "panda-json", "frames": parsed}


def load_ndjson_capture(path: Path, raw: bytes) -> dict:
    """Rows ``[segment, logMonoTime_ns, src, address, data_hex]`` from one route."""
    parsed = []
    for line_number, line in enumerate(raw.splitlines(), start=1):
        if not line.strip():
            continue
        try:
            _segment, t_ns, src, addr, data_hex = json.loads(line)
            payload = bytes.fromhex(data_hex)
        except (TypeError, ValueError) as exc:
            raise CaptureFormatError(f"{path}: row {line_number} malformed: {exc}") from exc
        if not isinstance(t_ns, int) or isinstance(t_ns, bool) or t_ns < 0:
            raise CaptureFormatError(f"{path}: row {line_number} has a negative or non-integer timestamp")
        parsed.append({"index": line_number - 1, "t": t_ns / 1e9, "addr": int(addr),
                       "bus": int(src), "data": payload})
    if not parsed:
        raise CaptureFormatError(f"{path}: capture has no frame rows")
    return {"header": {"format": "route-can-ndjson"}, "format": "route-can-ndjson", "frames": parsed}


def load_capture(path: Path) -> dict:
    raw = path.read_bytes()
    if raw[:2] == b"\x1f\x8b":
        raw = gzip.decompress(raw)
    if raw.lstrip()[:1] == b"{":
        return load_panda_capture(path, raw)
    return load_ndjson_capture(path, raw)


def quantize(frames: list[dict], cycle_instructions: int) -> tuple[list[dict], int]:
    """Assign each frame its foreground period, preserving capture order inside one period.

    Periods come from integer microseconds (``floor(round(t*1e6) / 5000)``) so a
    frame exactly on a period boundary cannot fall into the previous period
    through float rounding.
    """
    for frame in frames:
        frame["period"] = int(round(frame["t"] * 1_000_000)) // PERIOD_US
    ordered = sorted(frames, key=lambda f: (f["period"], f["index"]))
    moved = sum(1 for position, frame in enumerate(ordered) if frame["index"] != position)
    for frame in ordered:
        frame["after_instructions"] = frame["period"] * cycle_instructions
    return ordered, moved


def candump_line(frame: dict) -> str:
    identifier = f"{frame['addr']:08X}" if frame["addr"] > 0x7FF else f"{frame['addr']:03X}"
    data = frame["data"]
    payload = bytes.fromhex(data) if isinstance(data, str) else data
    separator = "##0" if len(payload) > 8 else "#"
    return f"({frame['t']:010.6f}) can{frame['bus']} {identifier}{separator}{payload.hex().upper()}"


def snapshot_checks(snapshot: bytes) -> list[dict]:
    checks = [{
        "name": "landing-zone", "kind": "memory", "address": hex(LANDING[0]),
        "size": LANDING[1] - LANDING[0],
        "equals_hex": snapshot[LANDING[0] - RAM_BASE:LANDING[1] - RAM_BASE].hex(),
    }]
    for start, end in CONTROL_RANGES:
        checks.append({
            "name": f"control-{start:08x}", "kind": "memory", "address": hex(start),
            "size": end - start,
            "equals_hex": snapshot[start - RAM_BASE:end - RAM_BASE].hex(),
        })
    return checks


def convert(capture_path: Path, ordered: list[dict], moved: int, output_dir: Path, bus: int,
            cycle_instructions: int, fd_tx_buffer: int, classic_tx_buffer: int,
            capture_format: str) -> dict:
    rx_rules, tx_rules = decode_firmware_rules()

    events: list[dict] = []
    converted: list[dict] = []
    last_period = None
    rx_by_id: Counter = Counter()
    tx_by_id: Counter = Counter()
    dropped_ids: Counter = Counter()
    other_buses: Counter = Counter()
    same_period: Counter = Counter()
    dlc_mismatch: Counter = Counter()
    previous_period: dict[int, int] = {}
    stem = capture_path.name.removesuffix(".gz").removesuffix(".ndjson").removesuffix(".json")

    for frame in ordered:
        addr = frame["addr"]
        if frame["bus"] != bus:
            other_buses[frame["bus"]] += 1
            continue
        last_period = frame["period"] if last_period is None else max(last_period, frame["period"])
        if addr in tx_rules:
            rule = tx_rules[addr]
            buffer = fd_tx_buffer if rule["fd"] else classic_tx_buffer
            events.append({
                "kind": "can-tx-complete",
                "buffer": buffer,
                "after_instructions": frame["after_instructions"],
                "evidence": f"EPS TX 0x{addr:X} handle {rule['handle']} "
                            f"(capture frame {frame['index']} t={frame['t']:.6f}s period {frame['period']})",
            })
            tx_by_id[addr] += 1
        elif addr in rx_rules:
            rule = rx_rules[addr]
            if rule["dlc"] is not None and len(frame["data"]) != rule["dlc"]:
                dlc_mismatch[addr] += 1
            if previous_period.get(addr) == frame["period"]:
                same_period[addr] += 1
            previous_period[addr] = frame["period"]
            event = {
                "kind": "can-rx",
                "fifo": rule["fifo"],
                "boundary": "post-filter",
                "can_id": hex(addr),
                "data_hex": frame["data"].hex(),
                "label": rule["label"],
                "after_instructions": frame["after_instructions"],
                "evidence": f"GAFL rule {rule['rule']} label 0x{rule['label']:X} "
                            f"(capture frame {frame['index']} t={frame['t']:.6f}s period {frame['period']})",
            }
            if rule["extended"]:
                event["extended"] = True
            if rule["fd"]:
                event["fd"] = True
            events.append(event)
            rx_by_id[addr] += 1
        else:
            dropped_ids[addr] += 1
            continue
        converted.append(frame)

    if last_period is None:
        raise CaptureFormatError(f"{capture_path}: no frames on bus {bus}")
    capture_sha = sha256_file(capture_path)
    scenario = {
        "schema": SCENARIO_SCHEMA,
        "name": f"{stem}_can_replay",
        "source": {"kind": "capture", "path": str(capture_path), "sha256": capture_sha, "bus": bus},
        "entry": {"role": "retained-original-software-state", "scope": "resolved-address",
                  "address": hex(RAM_BASE)},
        "max_instructions": (last_period + 1) * cycle_instructions + 100_000,
        "reset": "none",
        "gpr_fill": "0",
        "registers": dict(REGISTERS),
        "stop_addresses": [hex(RETURN_STUB)],
        "artifacts": [{
            "path": str(SNAPSHOT), "sha256": SNAPSHOT_SHA256, "address": hex(RAM_BASE),
            "executable": False, "evidence": "Retained READY LocalRAM snapshot",
        }],
        "memory": [],
        "events": events,
        "expected_termination": "stop-address",
        "checks": snapshot_checks(SNAPSHOT.read_bytes()),
    }

    output_dir.mkdir(parents=True, exist_ok=True)
    scenario_path = output_dir / f"{stem}.scenario.json"
    scenario_path.write_text(json.dumps(scenario, separators=(",", ":")) + "\n")
    candump_path = output_dir / f"{stem}.candump.log"
    with candump_path.open("w") as stream:
        for frame in converted:
            stream.write(candump_line(frame) + "\n")

    report = {
        "capture": {"path": str(capture_path), "sha256": capture_sha, "frames": len(ordered),
                    "format": capture_format},
        "period_s": PERIOD_S, "periods": last_period + 1,
        "cycle_instructions": cycle_instructions,
        "bus": bus,
        "events": {"can-rx": sum(rx_by_id.values()), "can-tx-complete": sum(tx_by_id.values())},
        "frames_converted": len(converted),
        "frames_dropped": {"total": len(ordered) - len(converted),
                           "other_bus": {str(k): v for k, v in sorted(other_buses.items())},
                           "bus_selected_not_accepted": sum(dropped_ids.values()),
                           "per_id": {f"0x{k:X}": v for k, v in sorted(dropped_ids.items())}},
        "same_period_frames": {f"0x{k:X}": v for k, v in sorted(same_period.items())},
        "reordered_frames": moved,
        "dlc_mismatch": {f"0x{k:X}": v for k, v in sorted(dlc_mismatch.items())},
        "per_id": {f"0x{k:X}": {"can-rx": rx_by_id[k], "can-tx-complete": tx_by_id[k]}
                   for k in sorted(set(rx_by_id) | set(tx_by_id))},
    }
    quantization_path = output_dir / f"{stem}.quantization.json"
    quantization_path.write_text(json.dumps(report, indent=1) + "\n")
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("capture", type=Path,
                        help="retained capture: panda .json/.json.gz or route .ndjson/.ndjson.gz")
    parser.add_argument("--output-dir", type=Path, default=Path("build/out/camry_capture_replay"))
    parser.add_argument("--bus", type=int, default=1,
                        help="CAN bus to convert (panda bus / comma src; default 1)")
    parser.add_argument("--cycle-instructions", type=int, default=1,
                        help="instruction boundaries per foreground period, as measured by the "
                             "machine run; the default 1 emits raw period indices")
    parser.add_argument("--fd-tx-buffer", type=int, default=16,
                        help="RSCFD transmit buffer completing the FD EPS PDU (default 16)")
    parser.add_argument("--classic-tx-buffer", type=int, default=19,
                        help="RSCFD transmit buffer completing classic EPS PDUs (default 19)")
    args = parser.parse_args(argv)
    if args.cycle_instructions < 1:
        parser.error("--cycle-instructions must be positive")

    capture = load_capture(args.capture)
    ordered, moved = quantize(capture["frames"], args.cycle_instructions)
    report = convert(args.capture, ordered, moved, args.output_dir, args.bus,
                     args.cycle_instructions, args.fd_tx_buffer, args.classic_tx_buffer,
                     capture["format"])
    print(json.dumps(report))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
