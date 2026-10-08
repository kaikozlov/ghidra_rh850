#!/usr/bin/env python3
"""Exercise exact Camry CodeFlash paths through the specification-backed P1M-E machine."""

from __future__ import annotations

import hashlib
import json
import subprocess
import tempfile
from pathlib import Path

from tools import REPO_ROOT

TARGET = "camry-8965F3307000"
FIXTURE_ROOT = REPO_ROOT / "tests/fixtures/rh850/machine"
SCENARIOS = {
    "camry_f33_ring_producer.json": "verified-local-execution",
    "camry_f33_rscfd_tx.json": "verified-local-execution",
    "camry_f33_rscfd_subword_read.json": "verified-local-execution",
    "camry_f33_rscfd_uninitialized_tx.json": "verified-expected-fault",
    "camry_f33_tauj_init.json": "verified-local-execution",
    "camry_f33_intc_ack.json": "verified-local-execution",
    "camry_f33_tauj_uninitialized_start.json": "verified-expected-fault",
    "camry_f33_faci_command.json": "verified-local-execution",
    "camry_f33_faci_access_error_lock.json": "verified-local-execution",
    "camry_f33_faci_not_ready.json": "verified-expected-fault",
    "camry_f33_faci_subword_read.json": "verified-local-execution",
    "camry_f33_faci_unsupported.json": "verified-expected-fault",
    "camry_f33_icus_command5.json": "verified-local-execution",
    "camry_f33_icus_command5_callback.json": "verified-local-execution",
    "camry_f33_icus_command5_output.json": "verified-local-execution",
    "camry_f33_icus_unsupported.json": "verified-expected-fault",
    "camry_f33_application_reset.json": "verified-local-execution",
    "camry_f33_application_reset_retention.json": "verified-local-execution",
    "camry_f33_system_reset.json": "verified-local-execution",
    "camry_f33_system1_pin_reset.json": "verified-local-execution",
    "camry_f33_system1_cvm_reset.json": "verified-local-execution",
    "camry_f33_mpu_write_denied.json": "verified-expected-fault",
    "camry_f33_mpu_execute_span_denied.json": "verified-expected-fault",
    "camry_f33_mpu_overlap_grant.json": "verified-local-execution",
    "camry_f33_misaligned_write.json": "verified-expected-fault",
    "camry_f33_misaligned_allowed.json": "verified-local-execution",
    "camry_f33_mmio_width.json": "verified-expected-fault",
    "camry_f33_unmapped_write.json": "verified-expected-fault",
}


def run(command: list[str], *, expect_success: bool = True) -> subprocess.CompletedProcess[str]:
    proc = subprocess.run(command, cwd=REPO_ROOT, text=True, capture_output=True, check=False)
    if (proc.returncode == 0) != expect_success:
        raise AssertionError(
            f"unexpected exit {proc.returncode}: {' '.join(command)}\n{proc.stdout}\n{proc.stderr}"
        )
    return proc


def check_exact_scenarios(output_root: Path) -> None:
    for fixture_name, expected_status in SCENARIOS.items():
        output_dir = output_root / fixture_name.removesuffix(".json")
        proc = run(
            [
                str(REPO_ROOT / "tools/rh850"),
                "machine",
                "run",
                TARGET,
                str(FIXTURE_ROOT / fixture_name),
                "--output-dir",
                str(output_dir),
            ]
        )
        result = json.loads(proc.stdout)
        report = json.loads(Path(result["report"]).read_text(encoding="utf-8"))
        if result["status"] != expected_status or report["status"] != expected_status:
            raise AssertionError(f"{fixture_name}: status drift: {result!r}")
        if report["target"] != TARGET:
            raise AssertionError(f"{fixture_name}: exact execution target drift")
        if report["executable_overlays"] is not False:
            raise AssertionError(f"{fixture_name}: executable overlay was accepted")
        if not report["passed"]:
            raise AssertionError(f"{fixture_name}: machine checks failed")
        print(
            f"PASS {fixture_name}: {report['status']}, "
            f"{report['instruction_count']} exact instructions"
        )


def check_executable_overlay_rejection(output_root: Path) -> None:
    artifact = output_root / "forbidden-overlay.bin"
    artifact.write_bytes(b"\x00\x00")
    scenario = {
        "schema": "rh850-p1me-machine-scenario-v1",
        "name": "reject-codeflash-overlay",
        "entry": "0x00000000",
        "max_instructions": 1,
        "stop_addresses": ["0x00000000"],
        "registers": {},
        "memory": [],
        "artifacts": [
            {
                "address": "0x00000000",
                "path": str(artifact),
                "sha256": hashlib.sha256(artifact.read_bytes()).hexdigest(),
                "executable": True,
                "evidence": "negative-test",
            }
        ],
        "checks": [],
    }
    scenario_path = output_root / "forbidden-overlay.json"
    scenario_path.write_text(json.dumps(scenario, indent=2) + "\n", encoding="utf-8")
    proc = run(
        [
            str(REPO_ROOT / "tools/rh850"),
            "machine",
            "run",
            TARGET,
            str(scenario_path),
            "--output-dir",
            str(output_root / "forbidden-overlay-output"),
        ],
        expect_success=False,
    )
    if "cannot overlay registered image region codeflash_user" not in proc.stderr:
        raise AssertionError(f"wrong executable-overlay failure:\n{proc.stderr}")
    print("PASS executable CodeFlash overlays are rejected")


def main() -> int:
    run([str(REPO_ROOT / "tools/rh850"), "machine", "model", "--check"])
    with tempfile.TemporaryDirectory(prefix="verify-rh850-machine-", dir=REPO_ROOT / "build/tmp") as tmp:
        output_root = Path(tmp)
        check_exact_scenarios(output_root)
        check_executable_overlay_rejection(output_root)
    print("PASS specification-backed RH850/P1M-E machine")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
