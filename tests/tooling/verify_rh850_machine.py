#!/usr/bin/env python3
"""Exercise target-discovered exact firmware scenarios through the P1M-E machine."""
from __future__ import annotations

import hashlib
import json
import subprocess
import tempfile
from pathlib import Path

from tools import REPO_ROOT

FIXTURE_ROOT = REPO_ROOT / "tests/fixtures/rh850/machine"
PORTABLE_STORE_SELECTOR = {
    "role": "p1me-byte-store-primitive",
    "scope": "function",
    "shape_sha256": "8e49a0bf8bf3a1a29e104d2a16a92e063499f8ea357df01e11a0bca0db68aa41",
    "instruction_count": 14,
    "body_size": 36,
    "offset": -18,
    "requirements": [],
}


def run(command: list[str], *, expect_success: bool = True) -> subprocess.CompletedProcess[str]:
    proc = subprocess.run(command, cwd=REPO_ROOT, text=True, capture_output=True, check=False)
    if (proc.returncode == 0) != expect_success:
        raise AssertionError(
            f"unexpected exit {proc.returncode}: {' '.join(command)}\n{proc.stdout}\n{proc.stderr}"
        )
    return proc


def fixture_batches() -> list[tuple[str, list[Path]]]:
    batches: list[tuple[str, list[Path]]] = []
    for target_dir in sorted(path for path in FIXTURE_ROOT.iterdir() if path.is_dir()):
        scenarios = sorted(target_dir.glob("*.json"))
        if not scenarios:
            raise AssertionError(f"target fixture directory is empty: {target_dir}")
        batches.append((target_dir.name, scenarios))
    if not batches:
        raise AssertionError("no target machine fixtures discovered")
    return batches


def check_exact_scenarios(output_root: Path) -> None:
    for target, scenarios in fixture_batches():
        output_dir = output_root / target
        proc = run([
            str(REPO_ROOT / "tools/rh850"),
            "test",
            "firmware",
            target,
            *(str(path) for path in scenarios),
            "--output-dir",
            str(output_dir),
        ])
        result = json.loads(proc.stdout)
        rows = result["reports"]
        if len(rows) != len(scenarios):
            raise AssertionError(f"{target}: report count drift")
        for scenario_path, row in zip(scenarios, rows, strict=True):
            report = json.loads(Path(row["report"]).read_text(encoding="utf-8"))
            scenario = json.loads(scenario_path.read_text(encoding="utf-8"))
            expected_status = (
                "verified-expected-fault"
                if scenario.get("expected_fault") is not None
                else "verified-local-execution"
            )
            if report["status"] != expected_status or not report["passed"]:
                raise AssertionError(f"{scenario_path.name}: machine result drift: {report!r}")
            if report["target"] != target:
                raise AssertionError(f"{scenario_path.name}: exact execution target drift")
            if report["executable_overlays"] is not False:
                raise AssertionError(f"{scenario_path.name}: executable overlay was accepted")
            resolution = report["entry_resolution"]
            if resolution["candidate_count"] != 1 or resolution["role"] != scenario["entry"]["role"]:
                raise AssertionError(f"{scenario_path.name}: dynamic entry resolution drift")
            print(
                f"PASS {target}/{scenario_path.name}: {report['status']}, "
                f"entry={resolution['resolved_address']}, "
                f"{report['instruction_count']} exact instructions"
            )


def check_schema_rejection(output_root: Path) -> None:
    scenario = {
        "schema": "rh850-p1me-machine-scenario-v2",
        "name": "reject-unknown-scenario-field",
        "entry": PORTABLE_STORE_SELECTOR,
        "max_instructions": 1,
        "stop_addresses": ["0x00010000"],
        "gpr_fill": "0",
        "registers": {"lp": "0x00010000"},
        "checks": [],
        "mystery": True,
    }
    path = output_root / "invalid-schema.json"
    path.write_text(json.dumps(scenario, indent=2) + "\n", encoding="utf-8")
    proc = run([
        str(REPO_ROOT / "tools/rh850"), "test", "firmware",
        "camry-8965F3307000", str(path),
        "--output-dir", str(output_root / "invalid-schema-output"),
    ], expect_success=False)
    if "unsupported fields: mystery" not in proc.stderr:
        raise AssertionError(f"wrong strict-schema failure:\n{proc.stderr}")
    print("PASS unknown scenario fields are rejected before execution")


def check_executable_overlay_rejection(output_root: Path) -> None:
    artifact = output_root / "forbidden-overlay.bin"
    artifact.write_bytes(b"\x00\x00")
    scenario = {
        "schema": "rh850-p1me-machine-scenario-v2",
        "name": "reject-codeflash-overlay",
        "entry": PORTABLE_STORE_SELECTOR,
        "max_instructions": 1,
        "stop_addresses": ["0x00010000"],
        "gpr_fill": "0",
        "registers": {"lp": "0x00010000"},
        "memory": [],
        "artifacts": [{
            "address": "0x00000000",
            "path": str(artifact),
            "sha256": hashlib.sha256(artifact.read_bytes()).hexdigest(),
            "executable": True,
            "evidence": "negative-test",
        }],
        "checks": [],
    }
    scenario_path = output_root / "forbidden-overlay.json"
    scenario_path.write_text(json.dumps(scenario, indent=2) + "\n", encoding="utf-8")
    proc = run([
        str(REPO_ROOT / "tools/rh850"), "test", "firmware",
        "camry-8965F3307000", str(scenario_path),
        "--output-dir", str(output_root / "forbidden-overlay-output"),
    ], expect_success=False)
    if "cannot overlay registered image region codeflash_user" not in proc.stderr:
        raise AssertionError(f"wrong executable-overlay failure:\n{proc.stderr}")
    print("PASS executable CodeFlash overlays are rejected")


def main() -> int:
    run([str(REPO_ROOT / "tools/rh850"), "model", "check"])
    with tempfile.TemporaryDirectory(prefix="verify-rh850-machine-", dir=REPO_ROOT / "build/tmp") as tmp:
        output_root = Path(tmp)
        check_exact_scenarios(output_root)
        check_schema_rejection(output_root)
        check_executable_overlay_rejection(output_root)
    print("PASS specification-backed multi-target RH850/P1M-E machine")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
