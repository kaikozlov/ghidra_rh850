#!/usr/bin/env python3
"""Run the four Camry F33 preemption scenarios and report shared memory ranges."""
from __future__ import annotations

import argparse
import bisect
import json
from collections import Counter
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from tools import REPO_ROOT
from tools.emulation import p1me_machine
from tools.targets.camry.research import (
    explore_camry_f33_cantp_preemption as cantp,
)
from tools.targets.camry.research import (
    explore_camry_f33_crypto_irq_preemption as crypto,
)
from tools.targets.camry.research import (
    explore_camry_f33_tx_confirmation_preemption as tx,
)

TARGET = "camry-8965F3307000"
DEFAULT_OUT = (
    REPO_ROOT / "build/out/targets/camry-8965F3307000/preemption-shared-ranges"
)
SCHEDULER_FIXTURE = (
    REPO_ROOT
    / "tests/fixtures/rh850/machine/camry-8965F3307000/"
    "camry_f33_scheduler_publication_native_ch1_single_request_returns.json"
)
CORPUS = REPO_ROOT / "data/generated/camry-8965F3307000/decompilations.jsonl"
IMAGE = REPO_ROOT / "firmware/camry-8965F3307000/CodeFlash.bin"
ISR_CATALOG = REPO_ROOT / "data/generated/camry_8965F3307000_execution_contexts.json"
SCHEMA = "camry-f33-preemption-shared-ranges-v1"


@dataclass(frozen=True)
class FunctionRange:
    start: int
    end: int
    entry: int
    name: str


class FunctionIndex:
    def __init__(self, ranges: Iterable[FunctionRange]):
        self.ranges = sorted(ranges, key=lambda row: (row.start, row.end))
        self.starts = [row.start for row in self.ranges]

    @classmethod
    def from_corpus(cls, path: Path = CORPUS) -> FunctionIndex:
        ranges: list[FunctionRange] = []
        with path.open(encoding="utf-8") as stream:
            header = json.loads(next(stream))
            if header.get("analysis_target") != TARGET:
                raise ValueError(f"{path}: target identity mismatch")
            for line in stream:
                row = json.loads(line)
                if row.get("record") != "function" or row.get("address_space") != "ram":
                    continue
                entry = int(row["entry_addr"], 0)
                for body in row["body_ranges"]:
                    if body["space"] != "ram":
                        continue
                    ranges.append(FunctionRange(
                        int(body["min"], 0),
                        int(body["max"], 0) + 1,
                        entry,
                        row["name"],
                    ))
        return cls(ranges)

    def owner(self, pc: int) -> FunctionRange | None:
        index = bisect.bisect_right(self.starts, pc) - 1
        if index < 0:
            return None
        row = self.ranges[index]
        return row if pc < row.end else None


@dataclass(frozen=True)
class InterruptWindow:
    enter: dict[str, Any]
    returned: dict[str, Any]

    @property
    def start(self) -> int:
        return int(self.enter["scheduler_tick"])

    @property
    def end(self) -> int:
        return int(self.returned["scheduler_tick"])


def _number(value: Any) -> int:
    return int(value, 0) if isinstance(value, str) else int(value)


def _function(row: FunctionRange | None) -> dict[str, Any] | None:
    if row is None:
        return None
    return {"entry": f"0x{row.entry:08X}", "name": row.name}


def _interrupt_windows(report: dict[str, Any]) -> list[InterruptWindow]:
    stack: list[dict[str, Any]] = []
    windows: list[InterruptWindow] = []
    for event in report.get("device_events", []):
        if event.get("kind") == "interrupt-enter":
            stack.append(event)
        elif event.get("kind") == "interrupt-return":
            if not stack:
                raise ValueError(f"{report['scenario']}: unmatched interrupt-return")
            windows.append(InterruptWindow(stack.pop(), event))
    if stack:
        raise ValueError(f"{report['scenario']}: interrupt did not return")
    return sorted(windows, key=lambda row: (row.start, -row.end))


def _merge(spans: Iterable[tuple[int, int]]) -> list[tuple[int, int]]:
    merged: list[list[int]] = []
    for start, end in sorted(spans):
        if start >= end:
            continue
        if merged and start <= merged[-1][1]:
            merged[-1][1] = max(merged[-1][1], end)
        else:
            merged.append([start, end])
    return [(start, end) for start, end in merged]


def _intersect(
    left: Iterable[tuple[int, int]], right: Iterable[tuple[int, int]],
) -> list[tuple[int, int]]:
    a = _merge(left)
    b = _merge(right)
    result: list[tuple[int, int]] = []
    left_index = right_index = 0
    while left_index < len(a) and right_index < len(b):
        start = max(a[left_index][0], b[right_index][0])
        end = min(a[left_index][1], b[right_index][1])
        if start < end:
            result.append((start, end))
        if a[left_index][1] <= b[right_index][1]:
            left_index += 1
        else:
            right_index += 1
    return _merge(result)


def _access_span(row: dict[str, Any]) -> tuple[int, int]:
    start = _number(row["address"])
    return start, start + int(row["size"])


def _overlaps(row: dict[str, Any], start: int, end: int) -> bool:
    row_start, row_end = _access_span(row)
    return row_start < end and row_end > start


def _access(row: dict[str, Any]) -> dict[str, Any]:
    result = {
        "instruction": int(row["instruction"]),
        "pc": f"0x{_number(row['pc']):08X}",
        "kind": row["kind"],
        "address": f"0x{_number(row['address']):08X}",
        "width": int(row["size"]),
    }
    if "value" in row:
        result["value"] = row["value"]
    return result


def _instruction_bytes(image: bytes, pc: int, size: int) -> bytes:
    if pc < 0 or pc + size > len(image):
        return b""
    return image[pc:pc + size]


def _mask_states(
    report: dict[str, Any], image: bytes, initial_psw: int, initial_pmr: int,
) -> list[dict[str, Any]]:
    """Recover delivery masks from DI/EI and the target's balanced PMR stack."""
    events_at: dict[int, list[dict[str, Any]]] = {}
    for event in report.get("device_events", []):
        if event.get("kind") in ("interrupt-enter", "interrupt-return"):
            events_at.setdefault(int(event["scheduler_tick"]), []).append(event)
    trace_at = {
        int(row["instruction"]): row for row in report.get("instruction_trace", [])
    }
    ticks = sorted(set(events_at) | set(trace_at))
    psw_id = 1 if initial_psw & 0x20 else 0
    pmr: int | None = initial_pmr
    exception_ids: list[int] = []
    pmr_stack: list[int | None] = []
    last_pmr_pc: int | None = None
    states: list[dict[str, Any]] = []
    for tick in ticks:
        events = events_at.get(tick, ())
        for event in events:
            if event["kind"] != "interrupt-return":
                continue
            if not exception_ids:
                raise ValueError(f"{report['scenario']}: interrupt return without saved PSW")
            psw_id = exception_ids.pop()
        for event in events:
            if event["kind"] != "interrupt-enter":
                continue
            event_id = event.get("psw_id")
            if event_id is None and "psw" in event:
                event_id = 1 if _number(event["psw"]) & 0x20 else 0
            delivered_id = psw_id if event_id is None else int(event_id)
            event_pmr = event.get("pmr")
            delivered_pmr = pmr if event_pmr is None else _number(event_pmr)
            priority = int(event.get("priority", 0))
            states.append({
                "instruction": tick,
                "channel": int(event["channel"]),
                "psw_id": delivered_id,
                "pmr": delivered_pmr,
                "pmr_source_pc": None if last_pmr_pc is None else f"0x{last_pmr_pc:08X}",
                "pmr_masks_priority": (
                    None if delivered_pmr is None or priority > 15
                    else bool(delivered_pmr & (1 << priority))
                ),
            })
            exception_ids.append(psw_id)
            psw_id = 1
        trace = trace_at.get(tick)
        if trace is None:
            continue
        pc = _number(trace["pc"])
        raw = _instruction_bytes(image, pc, int(trace["size"]))
        if pc == 0x6A45E:
            pmr_stack.append(pmr)
        elif pc == 0x6A4C4 and not pmr_stack:
            pmr = None
        if raw == bytes.fromhex("e0076001"):
            psw_id = 1
        elif raw == bytes.fromhex("e0876001"):
            psw_id = 0
        if pc in (0x6A494, 0x6A4BC):
            pmr = 0xFF00
            last_pmr_pc = pc
        elif pc in (0x6A4F0, 0x6A51A):
            pmr = pmr_stack.pop() if pmr_stack else None
            last_pmr_pc = pc
    return states


def _handler(
    window: InterruptWindow, functions: FunctionIndex,
    handlers: dict[int, dict[str, Any]],
) -> dict[str, Any]:
    direct = functions.owner(_number(window.enter["handler"]))
    if direct is not None:
        return _function(direct) or {}
    channel = int(window.enter["channel"])
    if channel in handlers:
        return handlers[channel]
    return {
        "entry": f"0x{_number(window.enter['handler']):08X}",
        "name": f"unrecovered_{_number(window.enter['handler']):08x}",
    }


def _load_handlers(path: Path = ISR_CATALOG) -> dict[int, dict[str, Any]]:
    catalog = json.loads(path.read_text(encoding="utf-8"))
    return {
        int(row["eic_channel"]): {
            "entry": row["entry"]["address"],
            "name": row["entry"]["name"],
            "role": row["role"],
        }
        for row in catalog["isr_catalog"]
    }


def analyze_report(
    report: dict[str, Any], scenario: str, functions: FunctionIndex,
    *, image: bytes = b"", initial_psw: int = 0, initial_pmr: int = 0,
    handlers: dict[int, dict[str, Any]] | None = None,
) -> dict[str, Any]:
    windows = _interrupt_windows(report)
    mask_states = _mask_states(report, image, initial_psw, initial_pmr)
    masks = {
        (row["instruction"], row["channel"]): row for row in mask_states
    }
    accesses = report.get("memory_accesses", [])
    rows: list[dict[str, Any]] = []
    deliveries: list[dict[str, Any]] = []
    handlers = handlers or {}
    trace = report.get("instruction_trace", [])
    for window in windows:
        interrupted = functions.owner(_number(window.enter["return_pc"]))
        if interrupted is None:
            raise ValueError(
                f"{report['scenario']}: no function owns return PC {window.enter['return_pc']}"
            )
        handler = _handler(window, functions, handlers)
        entries = [
            int(row["instruction"]) for row in trace
            if _number(row["pc"]) == interrupted.entry
        ]
        invocation_start = max(
            (instruction for instruction in entries if instruction <= window.start),
            default=-1,
        )
        invocation_end = min(
            (instruction for instruction in entries if instruction > window.end),
            default=1 << 63,
        )
        before = [
            row for row in accesses
            if invocation_start <= int(row["instruction"]) < window.start
            and functions.owner(_number(row["pc"])) == interrupted
        ]
        after = [
            row for row in accesses
            if window.end <= int(row["instruction"]) < invocation_end
            and functions.owner(_number(row["pc"])) == interrupted
        ]
        writes = [
            row for row in accesses
            if window.start <= int(row["instruction"]) < window.end
            and row["kind"] == "write"
        ]
        shared = _intersect(
            _intersect(map(_access_span, writes), map(_access_span, before)),
            map(_access_span, after),
        )
        mask = masks.get((window.start, int(window.enter["channel"])), {
            "psw_id": None,
            "pmr": None,
            "pmr_source_pc": None,
            "pmr_masks_priority": None,
        })
        delivery = {
            "scenario": scenario,
            "report_scenario": report["scenario"],
            "pc": window.enter["return_pc"],
            "instruction": window.start,
            "return_instruction": window.end,
            "channel": int(window.enter["channel"]),
            "priority": int(window.enter.get("priority", 0)),
            "interrupted_function": _function(interrupted),
            "handler_function": handler,
            "psw_id": mask["psw_id"],
            "pmr": None if mask["pmr"] is None else f"0x{mask['pmr']:04X}",
            "pmr_source_pc": mask["pmr_source_pc"],
            "pmr_masks_priority": mask["pmr_masks_priority"],
            "shared_range_count": len(shared),
        }
        if mask["psw_id"] == 1:
            delivery["delivery_status"] = "forced, ID masked at delivery"
        elif mask["pmr_masks_priority"]:
            delivery["delivery_status"] = "forced, PMR masked priority at delivery"
        else:
            delivery["delivery_status"] = "delivered with ID and PMR clear"
        deliveries.append(delivery)
        for start, end in shared:
            before_rows = [_access(row) for row in before if _overlaps(row, start, end)]
            after_rows = [_access(row) for row in after if _overlaps(row, start, end)]
            write_rows = [_access(row) for row in writes if _overlaps(row, start, end)]
            if mask["psw_id"] == 1:
                disposition = "protected by DI/EI"
            elif mask["pmr_masks_priority"]:
                disposition = "protected by PMR"
            elif any(row["kind"] == "read" for row in before_rows) and any(
                row["kind"] == "read" for row in after_rows
            ):
                disposition = "shared without protection"
            else:
                disposition = "unprotected but consistent"
            rows.append({
                **{key: value for key, value in delivery.items() if key != "shared_range_count"},
                "range": {
                    "start": f"0x{start:08X}",
                    "end": f"0x{end - 1:08X}",
                    "width": end - start,
                },
                "handler_writes": write_rows,
                "before_accesses": before_rows,
                "after_accesses": after_rows,
                "disposition": disposition,
            })
    return {"deliveries": deliveries, "rows": rows}




def _write_scenario(path: Path, scenario: dict[str, Any]) -> Path:
    path.write_text(json.dumps(scenario, indent=2) + "\n", encoding="utf-8")
    return path

def _capture_trace_reports(
    scenario_paths: Sequence[Path], output_dir: Path,
) -> list[dict[str, Any]]:
    """Capture traces without requiring CodeFlash-only drcov conversion."""
    output_dir.mkdir(parents=True, exist_ok=True)
    batch = p1me_machine._execute(TARGET, scenario_paths, instruction_trace=True)
    reports = batch["reports"]
    if len(reports) != len(scenario_paths):
        raise ValueError("machine batch report count drifted")
    for scenario_path, report in zip(scenario_paths, reports, strict=True):
        report_path = output_dir / f"{scenario_path.stem}.report.json"
        report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        report["report_path"] = str(report_path)
    return reports


def _run_scenarios(out: Path) -> list[tuple[str, dict[str, Any]]]:
    scenario_dir = out / "scenarios"
    report_dir = out / "machine-reports"
    scenario_dir.mkdir(parents=True, exist_ok=True)
    (REPO_ROOT / "build/tmp").mkdir(parents=True, exist_ok=True)

    cantp_scenario = cantp.make_scenario("k", 425, "sf")
    cantp_scenario["name"] = "preemption_shared_ranges_cantp"
    tx_base = tx.build_base(12)
    tx_base["name"] = "preemption_shared_ranges_tx_baseline"
    crypto_base = crypto.build_base()
    crypto_base["name"] = "preemption_shared_ranges_crypto_baseline"
    initial_paths = [
        _write_scenario(scenario_dir / "cantp.json", cantp_scenario),
        _write_scenario(scenario_dir / "tx-baseline.json", tx_base),
        _write_scenario(scenario_dir / "crypto-baseline.json", crypto_base),
        SCHEDULER_FIXTURE,
    ]
    cantp_report, tx_baseline, crypto_baseline, scheduler_report = (
        _capture_trace_reports(initial_paths, report_dir / "initial")
    )

    tx_event = tx.can_tx_event(tx_baseline)
    tx_tick = int(tx_event["scheduler_tick"]) + tx.TX_OWNERSHIP_PUBLICATION_INSTRUCTIONS
    tx_scenario = tx.add_completion(
        tx_base, "preemption_shared_ranges_tx_confirmation", tx_tick,
        tx.completion_resource(tx_event),
    )
    crypto_entry = crypto.timeout_entry(crypto_baseline)
    crypto_before = crypto.add_completion(
        crypto_base, "preemption_shared_ranges_crypto_before_load", crypto_entry + 3,
    )
    crypto_after = crypto.add_completion(
        crypto_base, "preemption_shared_ranges_crypto_after_load", crypto_entry + 4,
    )
    final_paths = [
        _write_scenario(scenario_dir / "tx-confirmation.json", tx_scenario),
        _write_scenario(scenario_dir / "crypto-before-load.json", crypto_before),
        _write_scenario(scenario_dir / "crypto-after-load.json", crypto_after),
    ]
    tx_report, crypto_before_report, crypto_after_report = _capture_trace_reports(
        final_paths, report_dir / "preemption",
    )
    return [
        ("CanTp receive EIC187 during DCM cleanup", cantp_report),
        ("CAN1 Tx confirmation EIC188 after ownership publication", tx_report),
        ("ICU-S completion EIC292 before timeout-state load", crypto_before_report),
        ("ICU-S completion EIC292 after timeout-state load", crypto_after_report),
        ("scheduler CH1 native publication EIC134", scheduler_report),
    ]


def _markdown(result: dict[str, Any]) -> str:
    lines = [
        "# Camry F33 interrupt preemption shared ranges",
        "",
        "Reproduce:",
        "",
        "```bash",
        "uv run --locked python -m tools.targets.camry.research.report_camry_f33_preemption_shared_ranges",
        "```",
        "",
        "## Deliveries",
        "",
        "| Scenario | Delivery | Interrupted | Handler | PSW.ID | PMR | Shared ranges |",
        "|---|---|---|---|---:|---:|---:|",
    ]
    for row in result["deliveries"]:
        interrupted = row["interrupted_function"]["name"]
        handler = row["handler_function"]["name"] if row["handler_function"] else "unnamed vector"
        lines.append(
            f"| {row['scenario']} | `{row['pc']}` / {row['instruction']} / "
            f"EIC{row['channel']} | `{interrupted}` | `{handler}` | "
            f"{row['psw_id']} | {row['pmr'] or 'unknown'} | {row['shared_range_count']} |"
        )
    lines.extend((
        "",
        "## Shared ranges",
        "",
        "| Scenario | Delivery | Range | Before | After | PSW.ID / PMR | Disposition |",
        "|---|---|---|---|---|---|---|",
    ))
    for row in result["rows"]:
        before = ", ".join(
            f"`{access['pc']}` {access['kind']}{access['width']}"
            for access in row["before_accesses"]
        )
        after = ", ".join(
            f"`{access['pc']}` {access['kind']}{access['width']}"
            for access in row["after_accesses"]
        )
        span = row["range"]
        lines.append(
            f"| {row['scenario']} | `{row['pc']}` / {row['instruction']} / EIC{row['channel']} | "
            f"`{span['start']}..{span['end']}` ({span['width']}) | {before} | {after} | "
            f"{row['psw_id']} / {row['pmr'] or 'unknown'} | {row['disposition']} |"
        )
    if not result["rows"]:
        lines.append("| _No shared ranges_ | | | | | | |")
    return "\n".join(lines) + "\n"


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args(argv)
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=True)
    functions = FunctionIndex.from_corpus()
    handlers = _load_handlers()
    image = IMAGE.read_bytes()
    analyses = [
        analyze_report(report, label, functions, image=image, handlers=handlers)
        for label, report in _run_scenarios(out)
    ]
    deliveries = [row for result in analyses for row in result["deliveries"]]
    rows = [row for result in analyses for row in result["rows"]]
    result = {
        "schema": SCHEMA,
        "target": TARGET,
        "scenarios": sorted({row["scenario"] for row in deliveries}),
        "delivery_count": len(deliveries),
        "shared_range_count": len(rows),
        "dispositions": dict(sorted(Counter(row["disposition"] for row in rows).items())),
        "deliveries": deliveries,
        "rows": rows,
    }
    report_path = out / "report.json"
    table_path = out / "report.md"
    report_path.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    table_path.write_text(_markdown(result), encoding="utf-8")
    print(json.dumps({
        "report": str(report_path),
        "table": str(table_path),
        "delivery_count": len(deliveries),
        "shared_range_count": len(rows),
        "dispositions": result["dispositions"],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
