#!/usr/bin/env python3
"""Resolve exact targets and execute strict P1M-E machine scenarios in Ghidra."""
from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any

from tools import REPO_ROOT
from tools.emulation.generate_p1me_model import MACHINE_OUTPUT, generate
from tools.project.analysis_target import target as resolve_target
from tools.project.analysis_target import verified_file

ROOT = REPO_ROOT
SCRIPT = ROOT / "ghidra" / "scripts" / "emulate" / "RunP1MEMachine.java"
SCENARIO_SCHEMA = "rh850-p1me-machine-scenario-v1"
CONTRACT_SCHEMA = "rh850-p1me-machine-run-v1"


class P1MEMachineError(RuntimeError):
    pass


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _absolute_input(path: Path, *, base: Path | None = None) -> Path:
    if path.is_absolute():
        return path.resolve()
    return ((base if base is not None else Path.cwd()) / path).resolve()


def _load_scenario(path: Path) -> dict[str, Any]:
    try:
        scenario = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise P1MEMachineError(f"cannot read machine scenario {path}: {exc}") from exc
    if not isinstance(scenario, dict) or scenario.get("schema") != SCENARIO_SCHEMA:
        raise P1MEMachineError(f"machine scenario schema drift: {path}")
    forbidden = {"overlay", "overlays", "instruction_overlay", "instruction_overlays"}
    present = forbidden.intersection(scenario)
    if present:
        raise P1MEMachineError(
            "machine scenarios cannot contain executable-byte overlays: "
            + ", ".join(sorted(present))
        )
    if not isinstance(scenario.get("name"), str) or not scenario["name"]:
        raise P1MEMachineError("machine scenario requires a nonempty name")
    if not isinstance(scenario.get("entry"), str):
        raise P1MEMachineError("machine scenario entry must be an address string")
    if not isinstance(scenario.get("max_instructions"), int) or scenario["max_instructions"] <= 0:
        raise P1MEMachineError("machine scenario max_instructions must be positive")
    scenario.setdefault("stop_addresses", [])
    scenario.setdefault("reset", "none")
    scenario.setdefault("registers", {})
    scenario.setdefault("memory", [])
    scenario.setdefault("artifacts", [])
    scenario.setdefault("checks", [])
    scenario_dir = path.parent
    for artifact in scenario["artifacts"]:
        if not isinstance(artifact, dict) or not isinstance(artifact.get("path"), str):
            raise P1MEMachineError("every machine artifact requires a path")
        artifact_path = _absolute_input(Path(artifact["path"]), base=scenario_dir)
        if not artifact_path.is_file():
            raise P1MEMachineError(f"machine artifact does not exist: {artifact_path}")
        expected = artifact.get("sha256")
        if not isinstance(expected, str):
            raise P1MEMachineError(f"machine artifact requires sha256: {artifact_path}")
        actual = _sha256(artifact_path)
        if actual != expected.lower():
            raise P1MEMachineError(f"machine artifact identity drift: {artifact_path}")
        artifact["path"] = str(artifact_path)
    return scenario


def _image_contract(target_name: str, row: dict[str, Any], field: str) -> dict[str, Any] | None:
    if field not in row:
        return None
    path = verified_file(target_name, field)
    return {
        "path": str(path),
        "sha256": row[f"{field}_sha256"],
        "size": int(row[f"{field}_size"]),
        "base": str(row[f"{field}_base"]),
    }


def run(*, target: str, scenario_path: Path, output_dir: Path) -> dict[str, Any]:
    generate(check=True)
    scenario_path = _absolute_input(scenario_path)
    scenario = _load_scenario(scenario_path)
    target_name, row = resolve_target(target)
    if row.get("processor") != "v850e3:LE:32:default":
        raise P1MEMachineError(
            f"target {target_name} uses unsupported processor {row.get('processor')!r}"
        )
    codeflash = _image_contract(target_name, row, "codeflash")
    if codeflash is None:
        raise P1MEMachineError(f"target {target_name} has no registered CodeFlash")
    model_sha = _sha256(MACHINE_OUTPUT)
    contract = {
        "schema": CONTRACT_SCHEMA,
        "target": {
            "name": target_name,
            "mcu": row["mcu"],
            "processor": row["processor"],
            "codeflash": codeflash,
            "dataflash": _image_contract(target_name, row, "dataflash"),
        },
        "model_path": str(MACHINE_OUTPUT.resolve()),
        "model_sha256": model_sha,
        "scenario": scenario,
    }
    output_dir = _absolute_input(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    contract_path = output_dir / "run-contract.json"
    report_path = output_dir / "report.json"
    contract_path.write_text(json.dumps(contract, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    report_path.unlink(missing_ok=True)
    command = [
        str(ROOT / "tools" / "gtarget"),
        target_name,
        "script",
        "run",
        str(SCRIPT),
        "--",
        str(contract_path),
        str(report_path),
    ]
    proc = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, check=False)
    if not report_path.is_file():
        detail = (proc.stderr or proc.stdout).strip()
        raise P1MEMachineError(f"P1M-E machine did not produce a report: {detail}")
    try:
        report = json.loads(report_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise P1MEMachineError(f"invalid P1M-E machine report: {report_path}") from exc
    if proc.returncode != 0 or report.get("passed") is not True:
        detail = report.get("fault") or report.get("status") or proc.stderr.strip()
        raise P1MEMachineError(f"P1M-E machine scenario failed: {detail}")
    return report
