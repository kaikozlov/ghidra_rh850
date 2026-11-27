#!/usr/bin/env python3
"""Run definedness, object-boundary, and stack-watermark checks on Camry DCM paths."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import shutil
import struct
from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable, Sequence

from tools import REPO_ROOT
from tools.emulation.p1me_machine import capture_many
from tools.targets.camry.analysis.convert_camry_capture_machine_events import RAM_BASE
from tools.targets.camry.research.replay_camry_f33_capture_machine import (
    SNAPSHOT,
    SNAPSHOT_SHA256,
)
from tools.targets.camry.decomp.lifting.decode import decode_at
from tools.targets.camry.research import explore_camry_f33_stateful_can_cycles as cycles
from tools.targets.camry.research import fuzz_camry_f33_machine_typed_events as typed
from tools.targets.camry.research import fuzz_camry_f33_dcm_handlers as dcm

TARGET = "camry-8965F3307000"
SCHEMA = "camry-f33-machine-definedness-boundaries-v1"
IMAGE = REPO_ROOT / "firmware/camry-8965F3307000/CodeFlash.bin"
IMAGE_SHA256 = "42dce8efc42f6ae31718e7713fa2d26bb9191b4a82439778aee4d7afded9b0e7"
STRUCT_LAYOUTS = REPO_ROOT / "decomp/camry-8965F3307000/struct_layouts.json"
DATA = REPO_ROOT / "decomp/camry-8965F3307000/data.jsonl"
SIENNA_OVERLAYS = REPO_ROOT / "ghidra/scripts/import/ApplyRamTypes.java"
DEFAULT_GNU_SUMMARY = (
    REPO_ROOT / "build/out/targets/camry-8965F3307000/dcm-handlers-fuzz-d5/summary.json"
)
DEFAULT_OUT = REPO_ROOT / "build/out/targets/camry-8965F3307000/d5-machine-oracles"
RETURN_STUB = 0x798
RESPONSE = 0xFEBE5A20
RESPONSE_SIZE = 768
ACTIVE_CONTEXT = 0xFEBE5630
ACTIVE_CONTEXT_SIZE = 28
APP_STACK_BAND = (0xFEBE1800, 0xFEBE2000)
STACK_FINDING_MARGIN = 0x100
LENGTH_SHAPES = (
    ("empty", bytes.fromhex("22")),
    ("short", bytes.fromhex("220f")),
    ("one", bytes.fromhex("220f01")),
    ("odd", bytes.fromhex("220f010f")),
    ("two", bytes.fromhex("220f010f01")),
    ("two-pad", bytes.fromhex("220f010f01a5")),
)

def _transport_shape_records() -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    sf_payload = bytes.fromhex("222030")
    for nibble in range(16):
        frame = (bytes((nibble,)) + sf_payload).ljust(8, b"\0")
        records.append({
            "category": "length-shape", "name": f"sf-nibble-{nibble:x}",
            "session": 1, "frames_hex": [frame.hex()],
        })

    first = bytes.fromhex("1040222030a1a2a3")
    cf1 = bytes.fromhex("21b1b2b3b4b5b6b7")
    cf3 = bytes.fromhex("23c1c2c3c4c5c6c7")
    records.extend((
        {"category": "length-shape", "name": "ff-fragment-only", "session": 1,
         "frames_hex": [first.hex()]},
        {"category": "length-shape", "name": "ff-one-fragment", "session": 1,
         "frames_hex": [first.hex(), cf1.hex()]},
        {"category": "length-shape", "name": "ff-sequence-skip", "session": 1,
         "frames_hex": [first.hex(), cf1.hex(), cf3.hex()]},
    ))
    for length in (0x100, 0x101):
        payload = (bytes.fromhex("222030") + bytes((index & 0xFF for index in range(length))))[:length]
        frames = [bytes((0x10 | (length >> 8), length & 0xFF)) + payload[:6]]
        offset, sequence = 6, 1
        while offset < length:
            frames.append(bytes((0x20 | (sequence & 0x0F),)) + payload[offset:offset + 7].ljust(7, b"\0"))
            offset += 7
            sequence += 1
        records.append({
            "category": "length-shape", "name": f"ff-oversized-{length:x}",
            "session": 1, "frames_hex": [frame.hex() for frame in frames],
        })
    return records


@dataclass(frozen=True)
class Extent:
    address: int
    size: int
    name: str
    source: str
    target_scope: str = TARGET

    @property
    def end(self) -> int:
        return self.address + self.size

    def row(self) -> dict[str, Any]:
        return {
            "address": hex(self.address), "end_exclusive": hex(self.end),
            "size": self.size, "name": self.name, "source": self.source,
            "target_scope": self.target_scope,
        }


@dataclass(frozen=True)
class Store:
    pc: int
    address: int
    width: int
    instruction: int | None = None


@dataclass(frozen=True)
class StackWatermark:
    initial_sp: int
    lowest_sp: int
    widest_use: int
    band_start: int
    band_end: int
    margin_to_lower_edge: int
    finding_margin: int
    finding: bool
    unknown_sp_writes: tuple[int, ...]

    def row(self) -> dict[str, Any]:
        result = asdict(self)
        for key in ("initial_sp", "lowest_sp", "band_start", "band_end"):
            result[key] = hex(result[key])
        result["unknown_sp_writes"] = [hex(pc) for pc in self.unknown_sp_writes]
        return result


def _int(value: Any) -> int:
    return int(value, 0) if isinstance(value, str) else int(value)


def _type_size(type_name: str, layouts: dict[str, int]) -> int | None:
    array = re.fullmatch(r"(.+?)\[(\d+)\]", type_name)
    if array:
        inner = _type_size(array.group(1), layouts)
        return None if inner is None else inner * int(array.group(2))
    primitives = {
        "u8": 1, "uchar": 1, "char": 1, "u16": 2, "ushort": 2,
        "u32": 4, "uint": 4, "int": 4, "undefined4": 4,
    }
    return primitives.get(type_name, layouts.get(type_name))


def load_object_extents() -> tuple[list[Extent], list[dict[str, Any]]]:
    """Load exact Camry DCM/CanTp extents and retain the Sienna source boundary."""
    layout_doc = json.loads(STRUCT_LAYOUTS.read_text(encoding="utf-8"))
    layouts = {row["name"]: int(row["size"]) for row in layout_doc["structs"]}
    wanted = re.compile(r"(?:^|_)(?:dcm|cantp)(?:_|$)|response|receive", re.I)
    extents: list[Extent] = []
    for line in DATA.read_text(encoding="utf-8").splitlines():
        row = json.loads(line)
        if not wanted.search(row["name"]):
            continue
        size = _type_size(row["type"], layouts)
        if size is None:
            continue
        extents.append(Extent(
            int(row["addr"], 16), size, row["name"],
            "decomp/camry-8965F3307000/data.jsonl + struct_layouts.json",
        ))

    image = IMAGE.read_bytes()
    for index in range(3):
        capacity, base = struct.unpack_from("<II", image, 0x25E90 + index * 8)
        extents.append(Extent(
            base, capacity, f"dcm_receive_buffer_{index}",
            f"firmware table 0x{0x25E90 + index * 8:05X} typed as F33DcmReceiveBufferConfiguration",
        ))

    sienna_rows = []
    for line_number, line in enumerate(SIENNA_OVERLAYS.read_text(encoding="utf-8").splitlines(), 1):
        match = re.search(r"applyScalar\(0x([0-9A-Fa-f]+)L,\s*([^,]+),\s*\"([^\"]+)", line)
        if match and re.search(r"uds|response|receive|channel", match.group(3), re.I):
            sienna_rows.append({
                "address": hex(int(match.group(1), 16)), "type_expression": match.group(2).strip(),
                "name": match.group(3), "line": line_number,
                "target_scope": "Sienna overlay; not transferred to Camry",
            })
    extents = sorted({(e.address, e.size, e.name, e.source): e for e in extents}.values(), key=lambda e: (e.address, e.size, e.name))
    return extents, sienna_rows


def crossing_stores(stores: Iterable[Store], extents: Sequence[Extent]) -> list[dict[str, Any]]:
    extents = tuple(extents)
    findings: list[dict[str, Any]] = []
    for store in stores:
        end = store.address + store.width
        for extent in extents:
            crosses_start = store.address < extent.address < end
            crosses_end = store.address < extent.end < end
            if not (crosses_start or crosses_end):
                continue
            findings.append({
                "pc": hex(store.pc), "address": hex(store.address), "width": store.width,
                "end_exclusive": hex(end), "instruction": store.instruction,
                "extent": extent.row(),
                "crossed_edge": "start" if crosses_start else "end",
            })
    return findings


def stores_from_rows(rows: Iterable[dict[str, Any]]) -> list[Store]:
    return [
        Store(_int(row["pc"]), _int(row["address"]), int(row.get("size", row.get("width", 0))), row.get("instruction"))
        for row in rows
        if row.get("kind") in ("write", "store") and int(row.get("size", row.get("width", 0))) > 0
    ]


def stack_watermark(
    trace: Iterable[dict[str, Any]], image: bytes, initial_sp: int,
    band: tuple[int, int] = APP_STACK_BAND, finding_margin: int = STACK_FINDING_MARGIN,
) -> StackWatermark:
    sp = initial_sp
    lowest = sp
    unknown: list[int] = []
    for row in trace:
        pc = _int(row["pc"])
        if pc >= len(image):
            continue
        instruction = decode_at(image, pc)
        if instruction is None:
            continue
        text, statement = instruction.text, instruction.stmt
        prepare = re.match(r"prepare (0x[0-9a-f]+), (\d+),", text)
        if prepare:
            sp -= 4 * (int(prepare.group(1), 16).bit_count() + int(prepare.group(2)))
        elif instruction.kind == "dispose":
            sp += 4 * (instruction.mask.bit_count() + instruction.slots)
        else:
            add = re.fullmatch(r"camry_addi\(3, 3, (-?\d+)\);", statement)
            add_short = re.fullmatch(r"camry_addi_imm5\(3, (-?\d+)\);", statement)
            if add or add_short:
                sp += int((add or add_short).group(1))
            elif re.match(r"camry_(?:mov|movi|add|sub|subr)\(3,", statement):
                unknown.append(pc)
        lowest = min(lowest, sp)
    margin = lowest - band[0]
    return StackWatermark(
        initial_sp, lowest, initial_sp - lowest, band[0], band[1], margin,
        finding_margin, margin < finding_margin, tuple(unknown),
    )






def _memory_check(name: str, address: int, size: int, snapshot: bytes) -> dict[str, Any]:
    return {
        "name": name, "kind": "memory", "address": hex(address), "size": size,
        "equals_hex": snapshot[address - RAM_BASE:address - RAM_BASE + size].hex(),
    }


def _record_name(record: dict[str, Any]) -> str:
    if record.get("category") == "length-shape":
        return f"rdbi-length-{record['name']}"
    return f"rdbi-{int(record['did'], 16):04x}-s{int(record['session'])}"


def _record_payload(record: dict[str, Any]) -> bytes:
    if record.get("category") == "length-shape":
        return bytes.fromhex(record["payload_hex"])
    did = int(record["did"], 16)
    return bytes((0x22, did >> 8, did & 0xFF))


def materialize_readiness_ram(out: Path) -> tuple[Path, str]:
    path = (out / "readiness_local_ram.bin").resolve()
    scenario = typed.capture_replay.build_replay_scenario(
        {"kind": "d5-readiness-snapshot"},
        (typed.capture_replay.CapturePeriod(0, (), ()),),
        "camry-f33-d5-readiness-snapshot",
        include_completions=False,
        checks=typed.capture_replay.END_MODE_CHECKS,
    )
    scenario["snapshot_outputs"] = [{
        "path": str(path),
        "address": hex(RAM_BASE),
        "size": 0x20000,
        "evidence": "D5 LocalRAM after normal-operation full-board checkpoint",
    }]
    scenario_path = out / "scenarios/readiness.scenario.json"
    scenario_path.parent.mkdir(parents=True, exist_ok=True)
    scenario_path.write_text(
        json.dumps(scenario, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )
    report = capture_many(
        TARGET, [scenario_path], out / "reports/readiness",
        instruction_trace=False,
    )[0]
    if report.get("termination_reason") == "runner-error" or not path.exists():
        raise RuntimeError(f"readiness snapshot failed: {report.get('error', report)}")
    payload = path.read_bytes()
    modes = {
        address: int.from_bytes(
            payload[address - RAM_BASE:address - RAM_BASE + size], "little",
        )
        for address, size in (
            (0xFEBEB11A, 2), (0xFEBEE8CC, 4), (0xFEBE8C06, 2),
        )
    }
    if set(modes.values()) != {0x0702}:
        raise RuntimeError(f"D5 readiness modes drifted: {modes}")
    return path, hashlib.sha256(payload).hexdigest()


def build_rdbi_batch(
    records: Sequence[dict[str, Any]],
    snapshot_path: Path = SNAPSHOT,
    snapshot_sha256: str = SNAPSHOT_SHA256,
) -> dict[str, Any]:
    snapshot = snapshot_path.read_bytes()
    if hashlib.sha256(snapshot).hexdigest() != snapshot_sha256:
        raise RuntimeError("D5 snapshot identity drifted")
    event_sets: list[list[dict[str, Any]]] = []
    for record in records:
        if "frames_hex" in record:
            event_sets.append([
                {
                    "kind": "can-rx", "fifo": 5, "can_id": "0x7a1",
                    "boundary": "post-filter", "label": 0x34,
                    "data_hex": frame_hex, "after_instructions": 2_000 + index * 96,
                    "evidence": f"GNU CanTp length-shape corpus: {record['name']}",
                }
                for index, frame_hex in enumerate(record["frames_hex"])
            ])
            continue
        case = typed.MachineCase(
            _record_name(record).replace("-", "_"),
            typed.canonical_streams({
                typed.CAN_SOURCE: (
                    typed.uds_event(_record_payload(record), 2_000),
                ),
            }),
        )
        event_sets.append(typed.checkpoint_trial_events(case, False))

    # Start each direct service trial from the registered normal-operation RAM
    # image. Execute the exact firmware reset/init paths, publish the trial's
    # session through the exact DCM setter, then alternate original
    # communication and DCM foreground functions until the queued RDBI settles.
    def sequencer(session: int) -> bytes:
        result = cycles.append_call(b"", 0x9887C)
        result = cycles.append_call(result, 0x79D60)
        result = cycles.append_call(result, 0x920B0, ((6, 0),))
        result = cycles.append_call(result, 0x9254A, ((6, session), (7, 0)))
        for _ in range(4):
            result = cycles.append_call(result, 0x7A254)
            result = cycles.append_call(result, 0x988C2)
        return result + cycles.mov(1, RETURN_STUB) + struct.pack("<H", 0x0061)

    code = sequencer(int(records[0]["session"]))
    scenario: dict[str, Any] = {
        "schema": "rh850-p1me-machine-scenario-v2",
        "name": "camry-f33-d5-rdbi-definedness",
        "entry": {
            "role": "sim-only-d5-rdbi-sequencer",
            "scope": "resolved-address",
            "address": hex(RAM_BASE),
        },
        "max_instructions": 180_000,
        "reset": "none",
        "gpr_fill": "0",
        "registers": {
            "sp": "0xfebe2000", "gp": "0xfebeb800", "tp": "0x23dfc",
            "lp": hex(RETURN_STUB), "PSW": "0", "PMR": "0", "RBASE": "0",
            "EBASE": "0", "INTBP": "0x20200", "CTPC": "0", "CTPSW": "0",
        },
        "stop_addresses": [hex(RETURN_STUB)],
        "artifacts": [{
            "path": str(snapshot_path), "sha256": snapshot_sha256,
            "address": hex(RAM_BASE), "executable": False,
            "evidence": "Normal-operation LocalRAM checkpoint snapshot",
        }],
        "memory": [
            {"address": hex(RAM_BASE), "hex": code.hex(),
             "evidence": "Executable RAM declaration; trial memory-write reinstalls after snapshot"},
            *[dict(row) for row in typed.ingress.RUNTIME_ROWS],
        ],
        "events": [],
        "checks": [],
        "steps": [{
            "kind": "checkpoint", "name": "ready-with-sequencer", "after_instructions": 0,
        }],
    }
    for index, (record, record_events) in enumerate(zip(records, event_sets, strict=True)):
        if index:
            scenario["steps"].append({
                "kind": "restore", "checkpoint": "ready-with-sequencer",
            })
        scenario["steps"].append({
            "kind": "trial", "name": _record_name(record),
            "max_instructions": scenario["max_instructions"],
            "stop_addresses": scenario["stop_addresses"],
            "events": [
                {"kind": "memory-write", "address": hex(RAM_BASE),
                 "data_hex": sequencer(int(record["session"])).hex(),
                 "after_instructions": 0, "evidence": "Install D5 firmware-call sequencer"},
                *record_events,
            ],
            "checks": [
                _memory_check("active-dcm-context", ACTIVE_CONTEXT, ACTIVE_CONTEXT_SIZE, snapshot),
                _memory_check("dcm-communication-modes", 0xFEBE564C, 4, snapshot),
                _memory_check("shared-response", RESPONSE, RESPONSE_SIZE, snapshot),
            ],
        })
    return scenario


def _trial_fault(trial: dict[str, Any]) -> dict[str, Any] | None:
    fault = trial.get("fault")
    if fault:
        return fault
    for row in trial.get("event_rows", []):
        if row.get("kind") == "uninitialized-read":
            return row
    return None


def summarize_rdbi(report: dict[str, Any], records: Sequence[dict[str, Any]], extents: Sequence[Extent]) -> dict[str, Any]:
    metadata = {_record_name(record): record for record in records}
    rows: list[dict[str, Any]] = []
    length_rows: list[dict[str, Any]] = []
    all_crossings: list[dict[str, Any]] = []
    observed_names: set[str] = set()
    for trial in report.get("checkpointing", {}).get("trials", []):
        name = trial.get("name", "")
        record = metadata.get(name)
        if record is None:
            continue
        observed_names.add(name)
        tx = [row for row in trial.get("event_rows", []) if row.get("kind") == "can-tx"]
        fault = _trial_fault(trial)
        memory_rows = trial.get("memory_rows", [])
        stores = stores_from_rows(memory_rows)
        crossings = crossing_stores(stores, extents)
        for crossing in crossings:
            crossing["case"] = name
        all_crossings.extend(crossings)
        reaches: bool | None = None
        if fault:
            address = _int(fault["address"])
            if RESPONSE <= address < RESPONSE + RESPONSE_SIZE:
                reaches = True
        row = {
            "case": name, "termination": trial.get("termination_reason"),
            "completed": bool(tx), "response_frames": [event.get("data_hex", "") for event in tx],
            "uninitialized_read": fault, "uninitialized_byte_reaches_response": reaches,
            "boundary_crossings": len(crossings), "stores_checked": len(stores),
            "rdbi_service_reached": any(_int(access["pc"]) == 0x962F2 for access in memory_rows),
        }
        if record.get("category") == "length-shape":
            row.update({"shape": record["name"]})
            if "frames_hex" in record:
                row["request_frames_hex"] = record["frames_hex"]
            else:
                row["request_hex"] = record["payload_hex"]
            length_rows.append(row)
        else:
            row.update({"did": record["did"], "session": int(record["session"])})
            rows.append(row)
    rdbi_records = [record for record in records if record.get("category") != "length-shape"]
    length_records = [record for record in records if record.get("category") == "length-shape"]
    return {
        "requested": len(rdbi_records), "observed": len(rows),
        "missing": sorted(_record_name(record) for record in records if _record_name(record) not in observed_names),
        "completed": sum(row["completed"] for row in rows),
        "incomplete": sum(not row["completed"] for row in rows),
        "uninitialized_reads": sum(row["uninitialized_read"] is not None for row in rows),
        "boundary_crossings": sum(row["boundary_crossings"] for row in rows),
        "stores_checked": sum(row["stores_checked"] for row in rows),
        "rdbi_service_reached": sum(row["rdbi_service_reached"] for row in rows),
        "records": rows,
        "length_shape": {
            "requested": len(length_records), "observed": len(length_rows),
            "uninitialized_reads": sum(row["uninitialized_read"] is not None for row in length_rows),
            "boundary_crossings": sum(row["boundary_crossings"] for row in length_rows),
            "stores_checked": sum(row["stores_checked"] for row in length_rows),
            "rdbi_service_reached": sum(row["rdbi_service_reached"] for row in length_rows),
            "records": length_rows,
        },
        "crossings": all_crossings,
    }

def merge_campaign_summaries(parts: Sequence[dict[str, Any]]) -> dict[str, Any]:
    scalar_keys = (
        "requested", "observed", "completed", "incomplete",
        "uninitialized_reads", "boundary_crossings", "stores_checked",
        "rdbi_service_reached",
    )
    result: dict[str, Any] = {key: sum(part[key] for part in parts) for key in scalar_keys}
    result["missing"] = sorted(name for part in parts for name in part["missing"])
    result["records"] = [row for part in parts for row in part["records"]]
    result["crossings"] = [row for part in parts for row in part["crossings"]]
    result["length_shape"] = {
        key: sum(part["length_shape"][key] for part in parts)
        for key in (
            "requested", "observed", "uninitialized_reads", "boundary_crossings",
            "stores_checked", "rdbi_service_reached",
        )
    }
    result["length_shape"]["records"] = [
        row for part in parts for row in part["length_shape"]["records"]
    ]
    return result


def _base_scenario(name: str, entry: int, memory: list[dict[str, Any]], registers: dict[str, str],
                   artifacts: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    return {
        "schema": "rh850-p1me-machine-scenario-v2", "name": name,
        "entry": {"role": "sim-only-oracle-positive-control", "scope": "resolved-address", "address": hex(entry)},
        "max_instructions": 10_000, "reset": "none", "gpr_fill": "0",
        "registers": {"sp": "0xfebe2000", "gp": "0xfebeb800", "tp": "0x23dfc", "lp": hex(RETURN_STUB), **registers},
        "stop_addresses": [hex(RETURN_STUB)], "artifacts": artifacts or [], "memory": memory,
        "events": [], "checks": [],
    }


def control_scenarios(extents: Sequence[Extent]) -> list[dict[str, Any]]:
    # Sim-only no-write producer returns immediately; exact memcpy_forward then
    # attempts to publish its uninitialized bytes into the DCM response object.
    no_write = RAM_BASE + 0x100
    source = 0xFEEF9000
    code = cycles.append_call(b"", no_write)
    code = cycles.append_call(code, 0x89F2E, ((6, RESPONSE), (7, source), (8, 16)))
    code += cycles.mov(1, RETURN_STUB) + struct.pack("<H", 0x0061)
    definedness = _base_scenario(
        "d5-definedness-positive-control", RAM_BASE,
        [{"address": hex(RAM_BASE), "hex": code.hex(), "evidence": "Sim-only DID no-write/publish control"},
         {"address": hex(no_write), "hex": "7f00", "evidence": "No-write producer: jmp [lp]"},
         {"address": hex(RESPONSE), "hex": "00" * 16, "evidence": "Initialized publication destination"}],
        {},
    )

    boundary_code = (
        cycles.mov(30, RESPONSE + RESPONSE_SIZE - 1)
        + cycles.mov(16, 0xA5A5)
        + bytes.fromhex("8084")  # exact sst.h 0[ep],r16 encoding from CodeFlash 0xDF4
        + cycles.mov(1, RETURN_STUB)
        + struct.pack("<H", 0x0061)
    )
    boundary = _base_scenario(
        "d5-boundary-positive-control", RAM_BASE,
        [{"address": hex(RAM_BASE), "hex": boundary_code.hex(),
          "evidence": "Sim-only halfword store starting at the response object's final byte"}],
        {"MCTL": "2"},
    )

    stack = _base_scenario(
        "d5-stack-positive-control", 0x65AC0, [], {},
    )
    stack["stop_addresses"] = ["0x65AC4"]
    return [definedness, boundary, stack]


def run_controls(out: Path, extents: Sequence[Extent]) -> dict[str, Any]:
    scenario_dir, report_dir = out / "controls/scenarios", out / "controls/reports"
    scenario_dir.mkdir(parents=True, exist_ok=True)
    paths = []
    for scenario in control_scenarios(extents):
        path = scenario_dir / f"{scenario['name']}.json"
        path.write_text(json.dumps(scenario, indent=2) + "\n", encoding="utf-8")
        paths.append(path)
    definedness = capture_many(
        TARGET, paths[:1], report_dir / "definedness", instruction_trace=False,
    )[0]
    boundary = capture_many(
        TARGET, paths[1:2], report_dir / "boundary", instruction_trace=False,
    )[0]
    stack = capture_many(
        TARGET, paths[2:], report_dir / "traced", instruction_trace=True,
    )[0]
    fault = definedness.get("fault")
    boundary_crossings = crossing_stores(stores_from_rows(boundary.get("memory_accesses", [])), extents)
    watermark = stack_watermark(stack.get("instruction_trace", []), IMAGE.read_bytes(), 0xFEBE2000)
    result = {
        "definedness": {
            "patch": "RAM no-write producer (jmp [lp]) followed by exact memcpy_forward publication of 16 uninitialized bytes",
            "expected": {"kind": "uninitialized-read", "address": "0xFEEF9000", "reaches_response": True},
            "observed": fault,
            "passed": bool(fault and fault.get("kind") == "uninitialized-read" and _int(fault["address"]) == 0xFEEF9000),
        },
        "boundary": {
            "patch": "Sim-only sst.h starts at the response object's final byte",
            "expected": {"extent": "dcm_shared_response_buffer", "edge": hex(RESPONSE + RESPONSE_SIZE)},
            "observed": boundary_crossings,
            "passed": any(row["extent"]["name"] == "dcm_shared_response_buffer" for row in boundary_crossings),
        },
        "stack": {
            "patch": "Sim-only entry at exact addi -64,sp,sp @ 0x65AC0; stop at 0x65AC4",
            "expected": {"lowest_sp": "0xFEBE1FC0", "widest_use": 64},
            "observed": watermark.row(),
            "passed": watermark.lowest_sp == 0xFEBE1FC0 and watermark.widest_use == 64,
        },
    }
    result["passed"] = all(row["passed"] for key, row in result.items() if key != "passed")
    return result


@dataclass(frozen=True)
class IngressCase:
    name: str
    category: str
    frames: tuple[bytes, ...]
    extended_session: bool = False
    shape: str = "valid"
    response_flow_control: tuple[bytes, ...] = (bytes.fromhex("3000000000000000"),)

    @property
    def case_id(self) -> str:
        encoded = json.dumps({
            "name": self.name,
            "category": self.category,
            "frames": [frame.hex() for frame in self.frames],
            "extended_session": self.extended_session,
            "response_flow_control": [frame.hex() for frame in self.response_flow_control],
        }, sort_keys=True, separators=(",", ":")).encode()
        return hashlib.sha256(encoded).hexdigest()[:16]


def _isotp(payload: bytes) -> tuple[bytes, ...]:
    return typed.iso_tp_frames(payload)


def _surface(name: str, key: str) -> dict[int, dict[str, str]]:
    with (REPO_ROOT / "data" / name).open(newline="", encoding="utf-8") as handle:
        return {int(row[key], 16): row for row in csv.DictReader(handle)}


WDBI_SURFACE = _surface("application_wdbi_surface.csv", "did")
ROUTINE_SURFACE = _surface("application_routine_control_surface.csv", "rid")


def wdbi_record(did: int) -> bytes:
    """Configured `2E` request: SID, DID and a zero payload of the configured
    length (`2012` takes the documented `01`)."""
    payload = b"\x01" if did == 0x2012 else bytes(int(WDBI_SURFACE[did]["payload_len"]))
    return bytes((0x2E, did >> 8, did & 0xFF)) + payload


def routine_records(rid: int) -> list[tuple[str, bytes]]:
    """Configured `31` requests: every supported control type with a zero
    option record of the configured length (`1004` takes `FF FF`; stop
    carries no record)."""
    row = ROUTINE_SURFACE[rid]
    records: list[tuple[str, bytes]] = []
    for control, label, column in (
        (1, "start", "control_type1_input_bytes"),
        (2, "results", "control_type2_input_bytes"),
        (3, "stop", None),
    ):
        if int(row[f"control_type{control}_supported"]):
            length = int(row[column]) if column else 0
            options = b"\xff" * length if rid == 0x1004 else bytes(length)
            records.append((label, bytes((0x31, control, rid >> 8, rid & 0xFF)) + options))
    return records


def ingress_cases() -> list[IngressCase]:
    cases = [
        IngressCase(
            f"rdbi-{did:04x}", "rdbi", _isotp(bytes((0x22, did >> 8, did & 0xFF))),
        )
        for did, _length, _reader in dcm.publication_rows()
    ]
    cases.extend(
        IngressCase(
            f"wdbi-{did:04x}-valid", "wdbi", _isotp(wdbi_record(did)),
            extended_session=True,
        )
        for did in dcm.WDBI_DIDS
    )
    cases.extend(
        IngressCase(
            f"routine-{rid:04x}-{label}", "routine", _isotp(record),
            extended_session=True,
        )
        for rid in dcm.ROUTINE_RIDS
        for label, record in routine_records(rid)
    )
    record = bytes(range(0x10))
    cases.extend(
        IngressCase(
            f"wdbi-{did:04x}-long", "wdbi",
            _isotp(bytes((0x2E, did >> 8, did & 0xFF)) + record),
            extended_session=True, shape="overlong",
        )
        for did in dcm.WDBI_DIDS
    )
    cases.extend(
        IngressCase(
            f"routine-{rid:04x}-long", "routine",
            _isotp(bytes((0x31, 0x01, rid >> 8, rid & 0xFF)) + record),
            extended_session=True, shape="overlong",
        )
        for rid in dcm.ROUTINE_RIDS
    )
    first = bytes.fromhex("10402e2001000102")
    cases.extend((
        IngressCase(
            "shape-ff-declared-more-than-supplied", "transport-shape",
            (first, bytes.fromhex("2103040506070809")),
            extended_session=True, shape="transport",
        ),
        IngressCase(
            "shape-cf-overrun", "transport-shape",
            (
                bytes.fromhex("100c2e2001000102"),
                bytes.fromhex("2103040506070809"),
                bytes.fromhex("220a0b0c0d0e0f10"),
            ),
            extended_session=True, shape="transport",
        ),
        IngressCase(
            "shape-response-fc-wait", "transport-shape",
            _isotp(bytes.fromhex("22f181")),
            shape="transport",
            response_flow_control=(
                bytes.fromhex("3100000000000000"),
                bytes.fromhex("3000000000000000"),
            ),
        ),
        IngressCase(
            "shape-response-fc-overflow", "transport-shape",
            _isotp(bytes.fromhex("22f181")),
            shape="transport",
            response_flow_control=(bytes.fromhex("3200000000000000"),),
        ),
        *(
            IngressCase(
                f"shape-response-block-size-{block_size}", "transport-shape",
                _isotp(bytes.fromhex("22f181")),
                shape="transport",
                response_flow_control=tuple(
                    bytes((0x30, block_size, 0, 0, 0, 0, 0, 0))
                    for _ in range({0: 1, 1: 5, 2: 3}[block_size])
                ),
            )
            for block_size in (0, 1, 2)
        ),
    ))
    return cases


def _rx_event(frame: bytes, at: int, evidence: str) -> dict[str, Any]:
    return {
        "kind": "can-rx", "fifo": 5, "can_id": "0x7a1",
        "boundary": "post-filter", "label": 0x34,
        "data_hex": frame.hex(), "after_instructions": at,
        "evidence": evidence,
    }


def _tx_complete(at: int, evidence: str) -> dict[str, Any]:
    return {
        "kind": "can-tx-complete", "buffer": 22,
        "firmware_control": "0x8048", "tolerate_no_pending": True,
        "after_instructions": at, "evidence": evidence,
    }


def ingress_events(case: IngressCase) -> list[dict[str, Any]]:
    events: list[dict[str, Any]] = []
    request_at = 900_000 if case.extended_session else 10_000
    if case.extended_session:
        events.extend((
            _rx_event(bytes.fromhex("0210030000000000"), 10_000, "Enter extended session through FIFO5"),
            _tx_complete(850_000, "Complete the session-control response"),
        ))
    events.append(_rx_event(case.frames[0], request_at, f"{case.name} first request frame"))
    if len(case.frames) > 1:
        request_flow_completion = (
            1_800_000 if case.extended_session else request_at + 30_000
        )
        consecutive_at = (
            1_850_000 if case.extended_session else request_at + 40_000
        )
        events.append(_tx_complete(
            request_flow_completion,
            f"Complete ECU flow control for {case.name}",
        ))
        events.extend(
            _rx_event(frame, consecutive_at + index * 128, f"{case.name} consecutive frame")
            for index, frame in enumerate(case.frames[1:])
        )
    response_completion = 2_700_000 if case.extended_session else 850_000
    end = 5_900_000 if case.extended_session else 3_900_000
    events.extend(
        _tx_complete(at, f"{case.name} response-frame completion")
        for at in range(response_completion, end, 50_000)
    )
    if case.name == "shape-response-block-size-1":
        flow_spacing = 400_000
    elif case.name == "shape-response-block-size-2":
        flow_spacing = 800_000
    else:
        flow_spacing = 100_000
    for index, frame in enumerate(case.response_flow_control):
        events.append(_rx_event(
            frame, response_completion + 50_000 + index * flow_spacing,
            f"{case.name} tester flow control",
        ))
    return sorted(events, key=lambda row: row["after_instructions"])


def build_ingress_scenario(
    case: IngressCase, *, instruction_trace: bool = False,
) -> dict[str, Any]:
    empty = typed.capture_replay.CapturePeriod(0, (), ())
    scenario = typed.capture_replay.build_replay_scenario(
        {"kind": "d5-ingress-oracles", "case_id": case.case_id},
        (empty,), f"d5_ingress_{case.case_id}",
        include_completions=False,
        checks=typed.capture_replay.END_MODE_CHECKS,
        foreground_ticks=False,
    )
    steps = scenario["steps"][:typed.capture_replay.REPLAY_PREFIX_STEPS]
    for step in steps:
        if step.get("kind") == "trial":
            step["capture_rows"] = False
    steps.extend((
        {"kind": "restore", "checkpoint": "normal-operation"},
        {
            "kind": "trial", "name": case.case_id,
            "max_instructions": 6_000_000 if case.extended_session else 4_000_000,
            "stop_addresses": [hex(typed.capture_replay.BOOT_TRANSFER)],
            "events": ingress_events(case),
            "checks": list(typed.capture_replay.END_MODE_CHECKS),
        },
    ))
    scenario["steps"] = steps
    if instruction_trace:
        scenario["instruction_trace_start_step"] = "normal-operation"
    return scenario


def _completed_isotp_messages(events: Sequence[dict[str, Any]]) -> list[dict[str, Any]]:
    messages: list[dict[str, Any]] = []
    current: dict[str, Any] | None = None
    for row in events:
        if row.get("kind") != "can-tx" or _int(row.get("can_id", 0)) != 0x7A9:
            continue
        frame = bytes.fromhex(row.get("data_hex", ""))
        if not frame:
            continue
        pci = frame[0] >> 4
        if pci == 0:
            length = frame[0] & 0x0F
            messages.append({
                "complete": True, "declared_length": length,
                "payload_hex": frame[1:1 + length].hex(),
                "frames": [frame.hex()],
            })
            current = None
        elif pci == 1 and len(frame) >= 2:
            length = ((frame[0] & 0x0F) << 8) | frame[1]
            current = {
                "complete": False, "declared_length": length,
                "payload": bytearray(frame[2:]), "frames": [frame.hex()],
                "next_sequence": 1,
            }
            if len(current["payload"]) >= length:
                current["complete"] = True
        elif pci == 2 and current is not None:
            if (frame[0] & 0x0F) != current["next_sequence"]:
                current = None
                continue
            current["next_sequence"] = (current["next_sequence"] + 1) & 0x0F
            current["payload"].extend(frame[1:])
            current["frames"].append(frame.hex())
            if len(current["payload"]) >= current["declared_length"]:
                current["complete"] = True
                messages.append({
                    "complete": True,
                    "declared_length": current["declared_length"],
                    "payload_hex": bytes(
                        current["payload"][:current["declared_length"]]
                    ).hex(),
                    "frames": current["frames"],
                })
                current = None
    if current is not None:
        messages.append({
            "complete": False,
            "declared_length": current["declared_length"],
            "payload_hex": bytes(current["payload"]).hex(),
            "frames": current["frames"],
        })
    return messages


def summarize_ingress_trial(
    case: IngressCase, report: dict[str, Any], extents: Sequence[Extent],
) -> dict[str, Any]:
    trial = next(
        (
            row for row in report.get("checkpointing", {}).get("trials", [])
            if row.get("name") == case.case_id
        ),
        None,
    )
    if trial is None:
        return {
            "schema": "camry-f33-d5-ingress-case-v1",
            "case_id": case.case_id,
            "name": case.name,
            "category": case.category,
            "request_frames": [frame.hex() for frame in case.frames],
            "termination": report.get("termination_reason", "runner-error"),
            "instruction_count": report.get("instruction_count"),
            "messages": [],
            "target_response_complete": False,
            "machine_fault": report.get("error"),
            "uninitialized_read": None,
            "boundary_crossings": [],
            "stores_checked": 0,
            "stack_watermark": None,
            "peripheral_events": {},
        }
    memory_rows = trial.get("memory_rows", [])
    stores = stores_from_rows(memory_rows)
    crossings = crossing_stores(stores, extents)
    messages = _completed_isotp_messages(trial.get("event_rows", []))
    target_sids = {
        "rdbi": {0x62, 0x7F},
        "wdbi": {0x6E, 0x7F},
        "routine": {0x71, 0x7F},
        "transport-shape": {0x62, 0x6E, 0x7F},
    }[case.category]
    target = [
        message for message in messages
        if message["payload_hex"]
        and int(message["payload_hex"][:2], 16) in target_sids
    ]
    fault = _trial_fault(trial)
    return {
        "schema": "camry-f33-d5-ingress-case-v1",
        "case_id": case.case_id,
        "name": case.name,
        "category": case.category,
        "request_frames": [frame.hex() for frame in case.frames],
        "termination": trial.get("termination_reason"),
        "instruction_count": trial.get("instruction_count"),
        "messages": messages,
        "target_response_complete": any(message["complete"] for message in target),
        "machine_fault": fault,
        "uninitialized_read": (
            fault if fault and fault.get("kind") == "uninitialized-read" else None
        ),
        "boundary_crossings": crossings,
        "stores_checked": len(stores),
        "stack_watermark": (
            stack_watermark(
                trial.get("instruction_trace", []),
                IMAGE.read_bytes(),
                0xFEBE7800,
                (0xFEBE7000, 0xFEBE7800),
            ).row()
            if trial.get("instruction_trace") is not None else None
        ),
        "peripheral_events": dict(sorted(Counter(
            str(row.get("kind")) for row in trial.get("event_rows", [])
        ).items())),
    }


def _load_ingress_result(
    path: Path, case: IngressCase, *, instruction_trace: bool,
) -> dict[str, Any] | None:
    try:
        result = json.loads(path.read_text())
        if (
            result.get("schema") != "camry-f33-d5-ingress-case-v1"
            or result.get("case_id") != case.case_id
            or not isinstance(result.get("messages"), list)
            or (instruction_trace and not isinstance(result.get("stack_watermark"), dict))
        ):
            return None
        return result
    except (OSError, json.JSONDecodeError):
        return None


def _tally(rows: Sequence[dict[str, Any]]) -> dict[str, int]:
    return {
        "executions": len(rows),
        "completed_responses": sum(row["target_response_complete"] for row in rows),
        "machine_failures": sum(
            row.get("termination") == "runner-error" for row in rows
        ),
        "uninitialized_reads": sum(row["uninitialized_read"] is not None for row in rows),
        "boundary_crossings": sum(len(row["boundary_crossings"]) for row in rows),
        "stores_checked": sum(row["stores_checked"] for row in rows),
    }


def run_ingress_campaign(
    out: Path, limit: int | None = None, *, instruction_trace: bool = False,
) -> dict[str, Any]:
    extents, sienna = load_object_extents()
    cases = ingress_cases()
    if limit is not None:
        cases = cases[:limit]
    scenario_dir = out / "ingress/scenarios"
    result_dir = out / "ingress/results"
    report_dir = out / "ingress/reports"
    for directory in (scenario_dir, result_dir, report_dir):
        directory.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, Any]] = []
    for case in cases:
        result_path = result_dir / f"{case.case_id}.json"
        result = _load_ingress_result(
            result_path, case, instruction_trace=instruction_trace,
        )
        if result is None:
            result_path.unlink(missing_ok=True)
            scenario = build_ingress_scenario(
                case, instruction_trace=instruction_trace,
            )
            scenario_path = scenario_dir / f"{case.case_id}.json"
            scenario_path.write_text(
                json.dumps(scenario, separators=(",", ":")) + "\n",
                encoding="utf-8",
            )
            report = capture_many(
                TARGET, [scenario_path], report_dir / case.case_id,
                instruction_trace=instruction_trace,
            )[0]
            result = summarize_ingress_trial(case, report, extents)
            temporary = result_path.with_suffix(".tmp")
            temporary.write_text(json.dumps(result, separators=(",", ":")) + "\n")
            temporary.replace(result_path)
            if result.get("termination") != "runner-error":
                shutil.rmtree(report_dir / case.case_id, ignore_errors=True)
        rows.append(result)
        progress = {
            "schema": "camry-f33-d5-ingress-progress-v1",
            "scheduled": len(cases),
            "completed_runs": len(rows),
            "transport_complete": sum(row["target_response_complete"] for row in rows),
            "machine_failures": sum(
                row.get("termination") == "runner-error" for row in rows
            ),
        }
        (out / "ingress/progress.json").write_text(
            json.dumps(progress, indent=2) + "\n",
        )
    paired = list(zip(cases, rows, strict=True))
    categories = {
        category: _tally([row for case, row in paired if case.category == category])
        for category in sorted({case.category for case in cases})
    }
    shapes = {
        f"{category}/{shape}": _tally([
            row for case, row in paired
            if case.category == category and case.shape == shape
        ])
        for category, shape in sorted({(case.category, case.shape) for case in cases})
    }
    summary = {
        "schema": "camry-f33-d5-ingress-oracles-v1",
        "image_sha256": IMAGE_SHA256,
        "object_extents": [extent.row() for extent in extents],
        "sienna_overlay_reference": sienna,
        "executions": len(rows),
        "completed_responses": sum(row["target_response_complete"] for row in rows),
        "machine_failures": sum(
            row.get("termination") == "runner-error" for row in rows
        ),
        "uninitialized_reads": sum(row["uninitialized_read"] is not None for row in rows),
        "boundary_crossings": sum(len(row["boundary_crossings"]) for row in rows),
        "stores_checked": sum(row["stores_checked"] for row in rows),
        "stack_watermarks": [
            {"case": row["name"], **row["stack_watermark"]}
            for row in rows
            if isinstance(row.get("stack_watermark"), dict)
        ],
        "failing_cases": [
            {
                "case": row["name"],
                "case_id": row["case_id"],
                "termination": row["termination"],
                "error": row.get("machine_fault"),
                "report_path": str(
                    (report_dir / row["case_id"] / f"{row['case_id']}.report.json")
                    .relative_to(REPO_ROOT)
                ),
            }
            for row in rows
            if row.get("termination") == "runner-error"
        ],
        "categories": categories,
        "shapes": shapes,
        "records": rows,
    }
    (out / "ingress-summary.json").write_text(
        json.dumps(summary, indent=2) + "\n",
        encoding="utf-8",
    )
    return summary


def run_campaign(gnu_summary: Path, out: Path, limit: int | None) -> dict[str, Any]:
    if hashlib.sha256(IMAGE.read_bytes()).hexdigest() != IMAGE_SHA256:
        raise RuntimeError("exact CodeFlash identity drifted")
    source = json.loads(gnu_summary.read_text(encoding="utf-8"))
    records = list(source["response_extent"].get("incomplete", []))
    if not records:
        raise RuntimeError("GNU summary lacks response_extent.incomplete; regenerate it with the current producer")
    if limit is not None:
        records = records[:limit]
    if limit is None:
        records.extend({
            "category": "length-shape", "name": name, "session": 1,
            "payload_hex": payload.hex(),
        } for name, payload in LENGTH_SHAPES)
        records.extend(_transport_shape_records())
    extents, sienna = load_object_extents()
    out.mkdir(parents=True, exist_ok=True)
    scenario_dir = out / "scenarios"
    scenario_dir.mkdir(parents=True, exist_ok=True)
    readiness_path, readiness_sha256 = materialize_readiness_ram(out)
    parts = []
    for batch_index, start in enumerate(range(0, len(records), 24)):
        batch = records[start:start + 24]
        scenario = build_rdbi_batch(batch, readiness_path, readiness_sha256)
        scenario["name"] = f"camry-f33-d5-rdbi-definedness-{batch_index:02d}"
        scenario_path = scenario_dir / f"rdbi-incomplete-{batch_index:02d}.scenario.json"
        scenario_path.write_text(json.dumps(scenario, separators=(",", ":")) + "\n", encoding="utf-8")
        report = capture_many(
            TARGET, [scenario_path], out / f"reports/batch-{batch_index:02d}",
            instruction_trace=False,
        )[0]
        parts.append(summarize_rdbi(report, batch, extents))
    campaign = merge_campaign_summaries(parts)
    controls = run_controls(out, extents)
    summary = {
        "schema": SCHEMA, "image_sha256": IMAGE_SHA256,
        "machine_state": {
            "checkpoint": "normal-operation",
            "live_mode": "0x0702",
            "desired_mode": "0x0702",
            "active_mode": "0x0702",
            "readiness_ram_sha256": readiness_sha256,
        },
        "gnu_source": str(gnu_summary.resolve().relative_to(REPO_ROOT)),
        "object_extents": [extent.row() for extent in extents],
        "sienna_overlay_reference": sienna,
        "machine_requirement": None,
        "rdbi": campaign, "controls": controls,
    }
    (out / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--gnu-summary", type=Path, default=DEFAULT_GNU_SUMMARY)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--limit", type=int)
    parser.add_argument("--controls-only", action="store_true")
    parser.add_argument("--ingress-only", action="store_true")
    parser.add_argument("--ingress-trace", action="store_true")
    args = parser.parse_args()
    extents, sienna = load_object_extents()
    if args.ingress_only:
        result = run_ingress_campaign(
            args.out, args.limit, instruction_trace=args.ingress_trace,
        )
        print(json.dumps({
            key: value for key, value in result.items()
            if key not in {"records", "object_extents"}
        }, indent=2))
        return 0
    if args.controls_only:
        result = {"controls": run_controls(args.out, extents), "object_extents": [row.row() for row in extents],
                  "sienna_overlay_reference": sienna}
        args.out.mkdir(parents=True, exist_ok=True)
        (args.out / "controls-summary.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    else:
        result = run_campaign(args.gnu_summary, args.out, args.limit)
    rdbi = dict(result.get("rdbi", {}))
    rdbi.pop("records", None)
    rdbi.pop("crossings", None)
    if "length_shape" in rdbi:
        rdbi["length_shape"] = dict(rdbi["length_shape"])
        rdbi["length_shape"].pop("records", None)
    print(json.dumps({"rdbi": rdbi, "controls": result["controls"]}, indent=2))
    return 0 if result["controls"].get("passed") else 1


if __name__ == "__main__":
    raise SystemExit(main())
