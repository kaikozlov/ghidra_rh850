#!/usr/bin/env python3
"""Exercise normal CanIf ingress across real foreground async cycles.

Each trial runs exact F33 CodeFlash from a retained READY LocalRAM snapshot. A
synthetic call-only RAM sequencer feeds hardware-shaped records through the
real software-ring producer, then advances communication, DCM, and crypto
foreground functions. The oracle
reports every firmware write into the executable landing zone or mutable
control cells and rejects any final-state mutation there.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import random
import struct
import tempfile
from pathlib import Path

from tools import REPO_ROOT
from tools.emulation.p1me_machine import capture_many

TARGET = "camry-8965F3307000"
IMAGE = REPO_ROOT / "firmware/camry-8965F3307000/CodeFlash.bin"
IMAGE_SHA256 = "42dce8efc42f6ae31718e7713fa2d26bb9191b4a82439778aee4d7afded9b0e7"
SNAPSHOT = REPO_ROOT / "targets/camry-2026/raw-20260826/secoc-recovery/ram/local_ram_pe1.bin"
SNAPSHOT_SHA256 = "0ddef478b15bcf3241c56573463eda25ba018081629daf0042fcae1204c435a7"
RAM_BASE = 0xFEBE0000
SEQUENCER = RAM_BASE
RECORD_BASE = 0xFEEFA000
RECORD_STRIDE = 0x80
CAN_RING_PRODUCER = 0x80A4A
FOREGROUND = (0x69CA2, 0x7A254, 0x988C2, 0x69E7C)
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
CAN_LENGTHS = tuple(range(9)) + (12, 16, 20, 24, 32, 48, 64)

def additive_checksum_payload(can_id: int, payload: bytes) -> bytes:
    """Return an eight-byte payload accepted by the F33 additive checksum gate."""
    if len(payload) != 7:
        raise ValueError("checksum payload prefix must contain exactly seven bytes")
    checksum = (sum(payload) + can_id + ((can_id & 0x700) >> 8) + 8) & 0xFF
    return payload + bytes((checksum,))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def mov(register: int, value: int) -> bytes:
    return struct.pack("<HI", 0x0620 | register, value & 0xFFFFFFFF)


def append_call(code: bytes, target: int, args: tuple[tuple[int, int], ...] = ()) -> bytes:
    for register, value in args:
        code += mov(register, value)
    continuation = SEQUENCER + len(code) + 14
    return code + mov(31, continuation) + mov(1, target) + struct.pack("<H", 0x0061)


def route_ids(image: bytes) -> tuple[int, ...]:
    ids = tuple(struct.unpack_from("<I", image, 0x230B8 + index * 16)[0] for index in range(43))
    if ids[:4] != (0x3B0, 0x63B, 0x624, 0x63D) or ids[-1] != 0x1DA:
        raise RuntimeError("normal GAFL route table drifted")
    return ids


def overlaps(address: int, size: int, span: tuple[int, int]) -> bool:
    return address < span[1] and address + size > span[0]


def trial_scenario(index: int, routes: tuple[int, ...], lengths: tuple[int, ...],
                   payloads: tuple[bytes, ...], route_table: tuple[int, ...],
                   snapshot: bytes, cycles: int, burst: bool = False,
                   record_flags: tuple[int, ...] | None = None,
                   prelude: tuple[int, ...] = ()) -> dict:
    code = b""
    for target in prelude:
        code = append_call(code, target)
    events: list[dict] = []
    for frame, (route, length, payload) in enumerate(zip(routes, lengths, payloads, strict=True)):
        record = RECORD_BASE + frame * RECORD_STRIDE
        # Software record bit30 marks CAN FD and selects the 64-byte ceiling;
        # bit31, when present in route_table, marks an extended identifier.
        # The downstream acceptance mask selects the fixed rule ID.
        message_id = route_table[route] | (0x40000000 if length > 8 else 0)
        payload_address = record + 0x20
        flags = 1 if record_flags is None else record_flags[frame]
        record_bytes = struct.pack("<IHBBI", message_id, 0, flags, length, payload_address)
        code = append_call(code, CAN_RING_PRODUCER, ((6, 0), (7, record)))
        if not burst:
            for _ in range(cycles):
                for target in FOREGROUND:
                    code = append_call(code, target)
        events.append({
            "kind": "memory-write", "address": hex(record), "data_hex": record_bytes.hex(),
            "after_instructions": 0, "evidence": "Synthetic hardware-shaped accepted CAN record",
        })
        events.append({
            "kind": "memory-write", "address": hex(payload_address),
            "data_hex": payload.ljust(64, b"\0").hex(), "after_instructions": 0,
            "evidence": "Tester-controlled CAN payload with initialized hardware-buffer tail",
        })
    if burst:
        for _ in range(cycles):
            for target in FOREGROUND:
                code = append_call(code, target)
    code += mov(1, RETURN_STUB) + struct.pack("<H", 0x0061)
    events.insert(0, {
        "kind": "memory-write", "address": hex(SEQUENCER), "data_hex": code.hex(),
        "after_instructions": 0,
        "evidence": "Synthetic transparent MOV/JMP call-only sequencer",
    })
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
    return {
        "schema": "rh850-p1me-machine-scenario-v2",
        "name": f"stateful_can_{index:05d}",
        "entry": {"role": "retained-original-software-state", "scope": "resolved-address",
                  "address": hex(SEQUENCER)},
        "max_instructions": 2_000_000,
        "reset": "none",
        "gpr_fill": "0",
        "registers": {"sp": "0xfebe2000", "gp": "0xfebeb800", "tp": "0x23dfc",
                      "lp": hex(RETURN_STUB), "PSW": "0x20", "PMR": "0xff00"},
        "stop_addresses": [hex(RETURN_STUB)],
        "artifacts": [{
            "path": str(SNAPSHOT), "sha256": SNAPSHOT_SHA256, "address": hex(RAM_BASE),
            "executable": False, "evidence": "Retained READY LocalRAM snapshot",
        }],
        "memory": [{"address": hex(SEQUENCER), "hex": code.hex(),
                    "evidence": "Executable-range declaration for event-restored sequencer"}],
        "events": events,
        "expected_termination": "stop-address",
        "checks": checks,
    }


def campaign(out: Path, seed: int, trials: int, frames: int, cycles: int,
             batch_size: int, burst: bool = False, valid_checksum: bool = False) -> dict:
    if min(trials, frames, cycles, batch_size) < 1:
        raise ValueError("trials, frames, cycles, and batch-size must be positive")
    if sha256(IMAGE) != IMAGE_SHA256 or sha256(SNAPSHOT) != SNAPSHOT_SHA256:
        raise RuntimeError("exact CodeFlash or retained READY snapshot identity drifted")
    image = IMAGE.read_bytes()
    snapshot = SNAPSHOT.read_bytes()
    routes = route_ids(image)
    rng = random.Random(seed)
    records: list[dict] = []
    findings: list[dict] = []
    out.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="f33-stateful-can-", dir=REPO_ROOT / "build/tmp") as tmp:
        tmp_path = Path(tmp)
        scenario_paths: list[Path] = []
        trial_inputs: list[dict] = []
        for index in range(trials):
            if index < len(routes):
                selected_routes = (index,) + tuple(rng.randrange(len(routes)) for _ in range(frames - 1))
            else:
                selected_routes = tuple(rng.randrange(len(routes)) for _ in range(frames))
            if valid_checksum:
                lengths = (8,) * frames
                payloads = tuple(
                    additive_checksum_payload(
                        routes[route], bytes(rng.randrange(256) for _ in range(7))
                    )
                    for route in selected_routes
                )
            else:
                lengths = tuple(rng.choice(CAN_LENGTHS) for _ in range(frames))
                payloads = tuple(
                    bytes(rng.randrange(256) for _ in range(length)) for length in lengths
                )
            scenario = trial_scenario(
                index, selected_routes, lengths, payloads, routes, snapshot, cycles, burst
            )
            path = tmp_path / f"trial-{index:05d}.json"
            path.write_text(json.dumps(scenario) + "\n")
            scenario_paths.append(path)
            trial_inputs.append({"routes": selected_routes, "lengths": lengths,
                                 "payloads": tuple(payload.hex() for payload in payloads)})
        for offset in range(0, trials, batch_size):
            batch_paths = scenario_paths[offset:offset + batch_size]
            reports = capture_many(TARGET, batch_paths, out / "reports")
            for relative, report in enumerate(reports):
                index = offset + relative
                critical = []
                for access in report.get("memory_accesses", []):
                    if access.get("kind") != "write":
                        continue
                    address = int(access["address"], 0)
                    size = int(access["size"])
                    if overlaps(address, size, LANDING) or any(
                        overlaps(address, size, span) for span in CONTROL_RANGES
                    ):
                        critical.append(access)
                record = {
                    "index": index, **trial_inputs[index],
                    "passed": report.get("passed", False),
                    "termination": report.get("termination_reason"),
                    "instructions": report.get("instruction_count"),
                    "error": report.get("error"),
                    "fault": report.get("fault"),
                    "recent_pcs": report.get("recent_pcs", []),
                    "critical_writes": critical,
                }
                records.append(record)
                if not record["passed"] or critical:
                    findings.append(record)
                    finding_dir = out / "findings"
                    finding_dir.mkdir(exist_ok=True)
                    (finding_dir / batch_paths[relative].name).write_text(
                        batch_paths[relative].read_text()
                    )
                else:
                    Path(report["report_path"]).unlink(missing_ok=True)
            print(f"completed {min(offset + batch_size, trials)}/{trials}; findings={len(findings)}", flush=True)
    summary = {
        "schema": "camry-f33-stateful-normal-can-original-codeflash-v1",
        "image_sha256": IMAGE_SHA256,
        "snapshot_sha256": SNAPSHOT_SHA256,
        "seed": seed,
        "trials": trials,
        "frames_per_trial": frames,
        "foreground_cycles_per_frame": cycles,
        "burst_before_foreground": burst,
        "valid_additive_checksum": valid_checksum,
        "findings": findings,
        "records": records,
    }
    (out / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed", type=int, default=20261110)
    parser.add_argument("--trials", type=int, default=256)
    parser.add_argument("--frames", type=int, default=4)
    parser.add_argument("--cycles", type=int, default=2)
    parser.add_argument("--batch-size", type=int, default=16)
    parser.add_argument(
        "--burst", action="store_true",
        help="enqueue every frame before the first foreground drain",
    )
    parser.add_argument(
        "--valid-checksum", action="store_true",
        help="use eight-byte random frames with the exact F33 additive checksum",
    )
    parser.add_argument("--out", type=Path, default=REPO_ROOT / "build/out/targets/camry-8965F3307000/stateful-normal-can")
    args = parser.parse_args()
    result = campaign(
        args.out, args.seed, args.trials, args.frames, args.cycles, args.batch_size,
        args.burst, args.valid_checksum,
    )
    print(json.dumps({key: value for key, value in result.items() if key not in ("records", "findings")}, indent=2))
    print(f"findings={len(result['findings'])}")
    return 1 if result["findings"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
