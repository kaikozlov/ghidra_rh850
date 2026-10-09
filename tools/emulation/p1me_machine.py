#!/usr/bin/env python3
"""Resolve exact targets and execute strict P1M-E machine scenarios in Ghidra."""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import tempfile
from collections.abc import Sequence
from pathlib import Path
from typing import Any

from tools import REPO_ROOT
from tools.project.analysis_target import target as resolve_target

ROOT = REPO_ROOT
SCRIPT = ROOT / "ghidra" / "scripts" / "emulate" / "RunP1MEMachine.java"
MODEL = ROOT / "data/generated/p1me_machine.json"
SCENARIO_SCHEMA = "rh850-p1me-machine-scenario-v2"
CONTRACT_SCHEMA = "rh850-p1me-machine-run-v2"
MODEL_SCHEMA = "rh850-p1me-machine-v2"
GPR_NAMES = (
    "r1", "r2", "sp", "gp", "tp",
    *(f"r{index}" for index in range(6, 30)),
    "ep", "lp",
)


class P1MEMachineError(RuntimeError):
    pass


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _absolute_input(path: Path, *, base: Path | None = None) -> Path:
    if path.is_absolute():
        return path.resolve()
    return ((base if base is not None else Path.cwd()) / path).resolve()


def _require_keys(
    value: dict[str, Any], *, allowed: set[str], required: set[str], context: str,
) -> None:
    unknown = sorted(set(value) - allowed)
    missing = sorted(required - set(value))
    if unknown:
        raise P1MEMachineError(f"{context}: unsupported fields: {', '.join(unknown)}")
    if missing:
        raise P1MEMachineError(f"{context}: missing fields: {', '.join(missing)}")


def _require_list(value: Any, context: str) -> list[Any]:
    if not isinstance(value, list):
        raise P1MEMachineError(f"{context}: expected a list")
    return value


def _validate_entry(entry: Any, context: str) -> dict[str, Any]:
    if not isinstance(entry, dict):
        raise P1MEMachineError(f"{context}: expected an object")
    scope = entry.get("scope")
    if scope == "resolved-address":
        _require_keys(
            entry,
            allowed={"role", "scope", "address"},
            required={"role", "scope", "address"},
            context=context,
        )
        try:
            address = int(entry["address"], 0)
        except (TypeError, ValueError) as exc:
            raise P1MEMachineError(
                f"{context}.address: expected an integer string",
            ) from exc
        if not 0 <= address <= 0xFFFFFFFF:
            raise P1MEMachineError(f"{context}.address: outside 32-bit address space")
        return entry

    allowed = {
        "role", "scope", "shape_sha256", "instruction_count", "body_size",
        "offset", "requirements",
    }
    required = {"role", "scope", "shape_sha256", "instruction_count", "body_size"}
    _require_keys(entry, allowed=allowed, required=required, context=context)
    if scope not in {"function", "instructions"}:
        raise P1MEMachineError(
            f"{context}.scope: expected function, instructions, or resolved-address",
        )
    digest = entry["shape_sha256"]
    if not isinstance(digest, str) or len(digest) != 64:
        raise P1MEMachineError(f"{context}.shape_sha256: expected 64 hex characters")
    try:
        int(digest, 16)
    except ValueError as exc:
        raise P1MEMachineError(f"{context}.shape_sha256: expected hexadecimal") from exc
    if not isinstance(entry["instruction_count"], int) or entry["instruction_count"] <= 0:
        raise P1MEMachineError(f"{context}.instruction_count: expected a positive integer")
    if not isinstance(entry["body_size"], int) or entry["body_size"] <= 0:
        raise P1MEMachineError(f"{context}.body_size: expected a positive integer")
    requirements = _require_list(entry.get("requirements", []), f"{context}.requirements")
    normalized_requirements: list[dict[str, Any]] = []
    for index, requirement in enumerate(requirements):
        item_context = f"{context}.requirements[{index}]"
        if not isinstance(requirement, dict):
            raise P1MEMachineError(f"{item_context}: expected an object")
        _require_keys(
            requirement,
            allowed={"index", "mnemonic", "operand", "scalar"},
            required={"index", "mnemonic"},
            context=item_context,
        )
        if not isinstance(requirement["index"], int) or requirement["index"] < 0:
            raise P1MEMachineError(f"{item_context}.index: expected a non-negative integer")
        if "scalar" in requirement and "operand" not in requirement:
            raise P1MEMachineError(f"{item_context}: scalar requires operand")
        normalized_requirements.append(requirement)
    return {
        **entry,
        "offset": entry.get("offset", 0),
        "requirements": normalized_requirements,
    }


def _validate_memory_rows(rows: Any, context: str) -> list[dict[str, Any]]:
    normalized = _require_list(rows, context)
    for index, row in enumerate(normalized):
        item_context = f"{context}[{index}]"
        if not isinstance(row, dict):
            raise P1MEMachineError(f"{item_context}: expected an object")
        _require_keys(
            row,
            allowed={"address", "size", "hex", "fill", "evidence"},
            required={"address", "evidence"},
            context=item_context,
        )
        if ("hex" in row) == ("fill" in row):
            raise P1MEMachineError(f"{item_context}: specify exactly one of hex or fill")
        if "fill" in row and "size" not in row:
            raise P1MEMachineError(f"{item_context}: fill requires size")
    return normalized


def _validate_artifacts(rows: Any, context: str, base: Path) -> list[dict[str, Any]]:
    normalized = _require_list(rows, context)
    out: list[dict[str, Any]] = []
    for index, row in enumerate(normalized):
        item_context = f"{context}[{index}]"
        if not isinstance(row, dict):
            raise P1MEMachineError(f"{item_context}: expected an object")
        _require_keys(
            row,
            allowed={"address", "path", "sha256", "executable", "evidence"},
            required={"address", "path", "sha256", "executable", "evidence"},
            context=item_context,
        )
        out.append({**row, "path": str(_absolute_input(Path(row["path"]), base=base))})
    return out


def _validate_checks(rows: Any, context: str) -> list[dict[str, Any]]:
    normalized = _require_list(rows, context)
    for index, row in enumerate(normalized):
        item_context = f"{context}[{index}]"
        if not isinstance(row, dict):
            raise P1MEMachineError(f"{item_context}: expected an object")
        _require_keys(
            row,
            allowed={"name", "kind", "register", "address", "size", "operation", "equals", "equals_hex"},
            required={"name", "kind"},
            context=item_context,
        )
        if row["kind"] not in {"register", "memory", "sync-count", "event-count"}:
            raise P1MEMachineError(f"{item_context}.kind: unsupported check kind")
    return normalized


def _validate_events(rows: Any, context: str) -> list[dict[str, Any]]:
    normalized = _require_list(rows, context)
    fields = {
        "clock": {"p_bus_cycles"},
        "can-rx": {"fifo", "can_id", "data_hex", "extended", "fd", "boundary", "label", "timestamp"},
        "interrupt": {"channel"},
    }
    for index, row in enumerate(normalized):
        item_context = f"{context}[{index}]"
        if not isinstance(row, dict) or row.get("kind") not in fields:
            raise P1MEMachineError(f"{item_context}: unsupported external event")
        kind = row["kind"]
        required = {
            "clock": {"p_bus_cycles"},
            "can-rx": {"fifo", "can_id", "data_hex", "boundary"},
            "interrupt": {"channel"},
        }[kind]
        _require_keys(
            row,
            allowed={"kind", "after_instructions", "evidence"} | fields[kind],
            required={"kind", "after_instructions", "evidence"} | required,
            context=item_context,
        )
        tick = row["after_instructions"]
        if type(tick) is not int or not 0 <= tick <= 0x7FFFFFFFFFFFFFFF:
            raise P1MEMachineError(f"{item_context}: after_instructions must be a nonnegative signed-64 integer")
        if kind == "clock":
            if type(row["p_bus_cycles"]) is not int or not 0 < row["p_bus_cycles"] <= 0x7FFFFFFFFFFFFFFF:
                raise P1MEMachineError(f"{item_context}: p_bus_cycles must be a positive signed-64 integer")
        elif kind == "interrupt":
            if type(row["channel"]) is not int or not 0 <= row["channel"] < 512:
                raise P1MEMachineError(f"{item_context}: invalid interrupt channel")
        else:
            if row["boundary"] != "post-filter":
                raise P1MEMachineError(f"{item_context}: only the explicit post-filter receive boundary is supported")
            if type(row["fifo"]) is not int or not 0 <= row["fifo"] < 9:
                raise P1MEMachineError(f"{item_context}: invalid common receive FIFO")
            for field, maximum in (("label", 0xFFF), ("timestamp", 0xFFFF)):
                if field in row and (type(row[field]) is not int or not 0 <= row[field] <= maximum):
                    raise P1MEMachineError(f"{item_context}: invalid receive {field}")
            for flag in ("extended", "fd"):
                if flag in row and type(row[flag]) is not bool:
                    raise P1MEMachineError(f"{item_context}: {flag} must be boolean")
            try:
                identifier = int(row["can_id"], 0)
                payload = bytes.fromhex(row["data_hex"])
            except (ValueError, TypeError) as exc:
                raise P1MEMachineError(f"{item_context}: invalid CAN identifier or data") from exc
            if not 0 <= identifier <= (0x1FFFFFFF if row.get("extended") else 0x7FF):
                raise P1MEMachineError(f"{item_context}: CAN identifier exceeds frame format")
            lengths = {0, 1, 2, 3, 4, 5, 6, 7, 8}
            if row.get("fd"):
                lengths |= {12, 16, 20, 24, 32, 48, 64}
            if len(payload) not in lengths:
                raise P1MEMachineError(f"{item_context}: invalid CAN payload length")
            row["can_id"] = hex(identifier)
            row["data_hex"] = payload.hex()
    return normalized


def load_scenario(path: Path) -> dict[str, Any]:
    scenario_path = _absolute_input(path)
    try:
        raw = json.loads(scenario_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise P1MEMachineError(f"cannot load scenario {scenario_path}: {exc}") from exc
    if not isinstance(raw, dict):
        raise P1MEMachineError(f"{scenario_path}: scenario root must be an object")
    allowed = {
        "schema", "name", "entry", "max_instructions", "reset", "stop_addresses",
        "gpr_fill", "registers", "memory", "pre_reset_memory", "artifacts", "checks",
        "expected_fault", "events",
    }
    required = {"schema", "name", "entry", "max_instructions", "stop_addresses", "checks"}
    _require_keys(raw, allowed=allowed, required=required, context=str(scenario_path))
    if raw["schema"] != SCENARIO_SCHEMA:
        raise P1MEMachineError(f"{scenario_path}: scenario schema drift")
    if not isinstance(raw["max_instructions"], int) or raw["max_instructions"] <= 0:
        raise P1MEMachineError(f"{scenario_path}: max_instructions must be positive")
    registers = raw.get("registers", {})
    if not isinstance(registers, dict):
        raise P1MEMachineError(f"{scenario_path}: registers must be an object")
    if "gpr_fill" in raw:
        fill = raw["gpr_fill"]
        if not isinstance(fill, str):
            raise P1MEMachineError(f"{scenario_path}: gpr_fill must be an integer string")
        registers = {**dict.fromkeys(GPR_NAMES, fill), **registers}
    expected_fault = raw.get("expected_fault")
    if expected_fault is not None:
        if not isinstance(expected_fault, dict):
            raise P1MEMachineError(f"{scenario_path}: expected_fault must be an object or null")
        _require_keys(
            expected_fault,
            allowed={"kind", "address", "access"},
            required=set(),
            context=f"{scenario_path}.expected_fault",
        )
    normalized = {
        "schema": raw["schema"],
        "name": raw["name"],
        "entry": _validate_entry(raw["entry"], f"{scenario_path}.entry"),
        "max_instructions": raw["max_instructions"],
        "reset": raw.get("reset", "none"),
        "stop_addresses": _require_list(raw["stop_addresses"], f"{scenario_path}.stop_addresses"),
        "registers": registers,
        "memory": _validate_memory_rows(raw.get("memory", []), f"{scenario_path}.memory"),
        "pre_reset_memory": _validate_memory_rows(
            raw.get("pre_reset_memory", []), f"{scenario_path}.pre_reset_memory",
        ),
        "artifacts": _validate_artifacts(
            raw.get("artifacts", []), f"{scenario_path}.artifacts", scenario_path.parent,
        ),
        "checks": _validate_checks(raw["checks"], f"{scenario_path}.checks"),
        "expected_fault": expected_fault,
        "events": _validate_events(raw.get("events", []), f"{scenario_path}.events"),
    }
    return normalized


def _hex_base(value: int | str) -> str:
    return f"0x{(int(value, 0) if isinstance(value, str) else value):08X}"


def _target_contract(target_name: str) -> dict[str, Any]:
    resolved_name, target = resolve_target(target_name)
    codeflash = ROOT / target["codeflash"]
    if not codeflash.is_file():
        raise P1MEMachineError(f"registered CodeFlash is missing: {codeflash}")
    result: dict[str, Any] = {
        "name": resolved_name,
        "mcu": target["mcu"],
        "processor": target["processor"],
        "codeflash": {
            "path": str(codeflash),
            "sha256": target["codeflash_sha256"],
            "size": target["codeflash_size"],
            "base": _hex_base(target["codeflash_base"]),
        },
        "dataflash": None,
    }
    if target.get("dataflash"):
        dataflash = ROOT / target["dataflash"]
        if not dataflash.is_file():
            raise P1MEMachineError(f"registered DataFlash is missing: {dataflash}")
        result["dataflash"] = {
            "path": str(dataflash),
            "sha256": target["dataflash_sha256"],
            "size": target["dataflash_size"],
            "base": _hex_base(target["dataflash_base"]),
        }
    return result


def _load_model() -> tuple[dict[str, Any], str]:
    try:
        model = json.loads(MODEL.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise P1MEMachineError(f"cannot load generated machine model: {exc}") from exc
    if model.get("schema") != MODEL_SCHEMA:
        raise P1MEMachineError("generated machine model schema drift")
    return model, _sha256(MODEL)


def _failure_summary(report: dict[str, Any]) -> str:
    scenario = report.get("scenario", "<unknown>")
    pieces = [f"{scenario}: {report.get('termination_reason', 'failed')}"]
    if error := report.get("error"):
        pieces.append(f"{error.get('type')}: {error.get('detail')}")
    if fault := report.get("fault"):
        pieces.append(
            f"fault={fault.get('kind')} pc={fault.get('pc')} address={fault.get('address')}"
        )
    failed_check = next(
        (row for row in report.get("checks", []) if not row.get("passed")), None,
    )
    if failed_check:
        pieces.append(
            f"check={failed_check.get('name')} expected={failed_check.get('expected')} "
            f"actual={failed_check.get('actual')}"
        )
    if recent := report.get("recent_pcs"):
        pieces.append("recent_pcs=" + ",".join(recent))
    return "; ".join(pieces)


def _execute(target_name: str, scenario_paths: Sequence[Path]) -> dict[str, Any]:
    if not scenario_paths:
        raise P1MEMachineError("at least one scenario is required")
    target = _target_contract(target_name)
    model, model_sha = _load_model()
    products = {row["product_id"] for row in model["products"]}
    if target["mcu"] not in products:
        raise P1MEMachineError(f"machine model does not describe MCU {target['mcu']}")
    scenarios = [load_scenario(path) for path in scenario_paths]
    names = [scenario["name"] for scenario in scenarios]
    if len(names) != len(set(names)):
        raise P1MEMachineError("scenario names must be unique within one batch")
    contract = {
        "schema": CONTRACT_SCHEMA,
        "target": target,
        "model_path": str(MODEL),
        "model_sha256": model_sha,
        "scenarios": scenarios,
    }
    with tempfile.TemporaryDirectory(prefix="p1me-machine-", dir=ROOT / "build" / "tmp") as tmp:
        tmp_path = Path(tmp)
        contract_path = tmp_path / "run-contract.json"
        batch_report_path = tmp_path / "batch-report.json"
        contract_path.write_text(json.dumps(contract, indent=2) + "\n", encoding="utf-8")
        command = [
            str(ROOT / "tools" / "gtarget"), target_name, "script", "run", str(SCRIPT),
            "--", str(contract_path), str(batch_report_path),
        ]
        proc = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, check=False)
        if not batch_report_path.is_file():
            detail = (proc.stderr or proc.stdout).strip()
            raise P1MEMachineError(f"P1M-E machine runner failed before reporting: {detail}")
        batch = json.loads(batch_report_path.read_text(encoding="utf-8"))
    if batch.get("schema") != "rh850-p1me-machine-batch-report-v1":
        raise P1MEMachineError("P1M-E machine batch report schema drift")
    return batch


def run_many(
    target_name: str, scenario_paths: Sequence[Path], output_dir: Path,
) -> list[dict[str, Any]]:
    output_dir = _absolute_input(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    batch = _execute(target_name, scenario_paths)
    reports = batch["reports"]
    for scenario_path, report in zip(scenario_paths, reports, strict=True):
        output = output_dir / f"{Path(scenario_path).stem}.report.json"
        output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        report["report_path"] = str(output)
    failures = [report for report in reports if not report.get("passed")]
    if failures:
        raise P1MEMachineError("; ".join(_failure_summary(report) for report in failures))
    return reports


def run(target_name: str, scenario_path: Path, report_path: Path) -> dict[str, Any]:
    batch = _execute(target_name, [scenario_path])
    report = batch["reports"][0]
    report_path = _absolute_input(report_path)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    report["report_path"] = str(report_path)
    if not report.get("passed"):
        raise P1MEMachineError(_failure_summary(report))
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("target")
    parser.add_argument("scenarios", nargs="+", type=Path)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    try:
        reports = run_many(args.target, args.scenarios, args.output_dir)
    except P1MEMachineError as exc:
        parser.error(str(exc))
    print(json.dumps({"reports": [report["report_path"] for report in reports]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
