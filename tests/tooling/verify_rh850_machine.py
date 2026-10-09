#!/usr/bin/env python3
"""Exercise target-discovered exact firmware scenarios through the P1M-E machine."""
from __future__ import annotations

import hashlib
import json
import subprocess
import tempfile
from pathlib import Path

from exploit.ram_runtime.target_profiles import supported_targets, target_spec
from tools import REPO_ROOT
from tools.targets.tss3.request_signer_machine import verify_request_signer_target

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

def check_dynamic_request_signer_targets(output_root: Path) -> None:
    for target in supported_targets():
        spec = target_spec(target)
        result = verify_request_signer_target(
            target=target,
            contract=spec["contract"],
            output_dir=output_root / "dynamic-request-signer" / target,
        )
        if result["codeflash_sha256"] != spec["sha256"]:
            raise AssertionError(f"{target}: dynamic machine verification image drift")
        if result["scenario_count"] != 8:
            raise AssertionError(f"{target}: dynamic machine scenario count drift")
        for row in result["scenarios"]:
            resolution = row["entry_resolution"]
            if row["status"] != "verified-local-execution":
                raise AssertionError(f"{target}/{row['name']}: execution status drift")
            if resolution["candidate_count"] != 1:
                raise AssertionError(f"{target}/{row['name']}: entry resolution is ambiguous")
            print(
                f"PASS {target}/{row['name']}: entry={resolution['resolved_address']}, "
                f"{row['instruction_count']} exact instructions"
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


def check_fault_check_error_boundary(output_root: Path) -> None:
    """Original execution fault must survive failing postcondition inspections.

    The retained byte-store primitive faults on an unmapped destination before
    any RAM write lands, so both postcondition checks inspect memory that was
    never initialized. The runner must publish the per-scenario report with the
    execution fault at the top, a termination_reason that reflects that fault,
    and one structured inspection error per failing check instead of throwing
    away or replacing the report.
    """
    scenario = {
        "schema": "rh850-p1me-machine-scenario-v2",
        "name": "unmapped-write-preserves-fault-with-failing-checks",
        "entry": PORTABLE_STORE_SELECTOR,
        "max_instructions": 20,
        "stop_addresses": ["0x00010000"],
        "gpr_fill": "0",
        "registers": {
            "sp": "0xFEBE2000",
            "gp": "0xFEBEB800",
            "tp": "0x00023DFC",
            "r6": "0xFF000000",
            "r7": "0x5A",
            "lp": "0x00010000",
            "PSW": "0",
            "PMR": "0",
        },
        "memory": [],
        "artifacts": [],
        "checks": [
            {
                "name": "rejected unmapped store leaves local RAM uninitialized",
                "kind": "memory",
                "address": "0xFEBE0000",
                "size": 4,
                "equals_hex": "00000000",
            },
            {
                "name": "rejected unmapped store leaves global RAM uninitialized",
                "kind": "memory",
                "address": "0xFEEF8000",
                "size": 1,
                "equals_hex": "00",
            },
        ],
        "expected_fault": {
            "kind": "unmapped-write",
            "address": "0xFF000000",
            "access": "write",
        },
    }
    path = output_root / "fault-check-boundary.json"
    path.write_text(json.dumps(scenario, indent=2) + "\n", encoding="utf-8")
    proc = run([
        str(REPO_ROOT / "tools/rh850"), "test", "firmware",
        "camry-8965F3307000", str(path),
        "--output-dir", str(output_root / "fault-check-boundary-output"),
    ], expect_success=False)
    report_path = (
        output_root / "fault-check-boundary-output" / "fault-check-boundary.report.json"
    )
    if not report_path.is_file():
        raise AssertionError(
            "failed scenario must still publish its report: "
            f"{proc.stderr}\n{proc.stdout}"
        )
    report = json.loads(report_path.read_text(encoding="utf-8"))
    fault = report.get("fault") or {}
    if fault.get("kind") != "unmapped-write" or fault.get("address") != "0xFF000000":
        raise AssertionError(f"original execution fault not preserved at report top: {fault!r}")
    if report.get("termination_reason") != "expected-fault":
        raise AssertionError(
            "termination_reason must reflect the expected execution fault, got "
            f"{report.get('termination_reason')!r}"
        )
    if report.get("passed") is not False or report.get("status") != "failed":
        raise AssertionError(f"failing inspection checks must fail the report: {report!r}")
    if not report.get("checks"):
        raise AssertionError("boundary scenario requires failing inspection checks")
    for row in report["checks"]:
        if row.get("passed") is not False:
            raise AssertionError(f"uninitialized-RAM inspection must fail: {row!r}")
        error = row.get("error")
        if not isinstance(error, dict) or error.get("kind") != "uninitialized-read":
            raise AssertionError(f"check must carry structured inspection fault: {row!r}")
        if row.get("actual") != "unavailable":
            raise AssertionError(f"failed inspection must not fabricate a value: {row!r}")
    for fragment in ("expected-fault", "fault=unmapped-write", "address=0xFF000000"):
        if fragment not in proc.stderr:
            raise AssertionError(
                f"consumer failure summary dropped {fragment!r}:\n{proc.stderr}"
            )
    print("PASS original execution fault survives failing uninitialized-RAM inspection checks")


def check_event_schema_rejections(output_root: Path) -> None:
    """Reject invalid external inputs before producing execution reports."""
    output_dir = output_root / "event-schema-rejections"
    output_dir.mkdir(parents=True, exist_ok=True)
    receive = {
        "kind": "can-rx",
        "after_instructions": 0,
        "evidence": "scenario: foreground receive frame probe",
        "fifo": 5,
        "can_id": "0x7A1",
        "data_hex": "085a",
        "boundary": "post-filter",
    }
    cases = [
        (
            "pre-filter-boundary",
            {**receive, "boundary": "pre-filter"},
        ),
        (
            "missing-boundary",
            {key: value for key, value in receive.items() if key != "boundary"},
        ),
        (
            "standard-identifier-overflow",
            {**receive, "can_id": "0x800", "data_hex": "08"},
        ),
        (
            "extended-identifier-overflow",
            {**receive, "can_id": "0x20000000", "data_hex": "08", "extended": True},
        ),
        (
            "classic-frame-dlc-twelve",
            {**receive, "data_hex": "000102030405060708090a0b"},
        ),
        (
            "fd-frame-dlc-nine",
            {**receive, "data_hex": "000102030405060708", "fd": True},
        ),
        (
            "receive-fifo-out-of-range",
            {**receive, "fifo": 9},
        ),
        (
            "bool-as-clock-cycles",
            {
                "kind": "clock",
                "after_instructions": 0,
                "evidence": "scenario: boolean p-bus cycle count probe",
                "p_bus_cycles": True,
            },
        ),
        (
            "bool-as-clock-tick",
            {
                "kind": "clock",
                "after_instructions": True,
                "evidence": "scenario: boolean schedule tick probe",
                "p_bus_cycles": 8,
            },
        ),
        (
            "unknown-event-kind",
            {**receive, "kind": "can-tx"},
        ),
    ]
    for name, event in cases:
        scenario = {
            "schema": "rh850-p1me-machine-scenario-v2",
            "name": f"reject-event-{name}",
            "entry": PORTABLE_STORE_SELECTOR,
            "max_instructions": 1,
            "stop_addresses": ["0x00010000"],
            "gpr_fill": "0",
            "registers": {"lp": "0x00010000"},
            "memory": [],
            "artifacts": [],
            "checks": [],
            "events": [event],
        }
        scenario_path = output_dir / f"{name}.json"
        scenario_path.write_text(json.dumps(scenario, indent=2) + "\n", encoding="utf-8")
        proc = run([
            str(REPO_ROOT / "tools/rh850"), "test", "firmware",
            "camry-8965F3307000", str(scenario_path),
            "--output-dir", str(output_dir),
        ], expect_success=False)
        if proc.returncode != 2:
            raise AssertionError(f"{name}: expected CLI input rejection, got {proc.returncode}")
        if (output_dir / f"{name}.report.json").exists():
            raise AssertionError(f"{name}: rejected scenario must not produce a report")
        print(f"PASS event {name} rejected before emulation")


def check_execution_event_boundaries(output_root: Path) -> None:
    """External clock and interrupt requests must land only on modeled device state.

    Both scenarios retain the exact byte-store primitive entry so the failure is
    the external-event dispatch boundary itself: no entry instruction executes.
    The clock scenario selects valid but unimplemented CK3, so the event must
    yield an unsupported-timer-mode fault rather than invent clock progression.
    Interrupt channel 292 has no reset row in the device model (manual Table
    6.11 reserves it), so the request must fault instead of synthesizing a
    reset value, handler vector, or delivery event.
    """
    output_dir = output_root / "execution-event-boundaries"
    output_dir.mkdir(parents=True, exist_ok=True)
    registers = {
        "sp": "0xFEBE2000",
        "gp": "0xFEBEB800",
        "tp": "0x00023DFC",
        "lp": "0x00010000",
        "PSW": "0",
        "PMR": "0",
    }
    scenarios = {
        "clock-unsupported-timer-mode.json": {
            "schema": "rh850-p1me-machine-scenario-v2",
            "name": "clock-on-unsupported-timer-mode-faults",
            "entry": PORTABLE_STORE_SELECTOR,
            "max_instructions": 4,
            "stop_addresses": ["0x00010000"],
            "gpr_fill": "0",
            "registers": registers,
            "memory": [
                {
                    "address": "0xFFE50050",
                    "hex": "01",
                    "evidence": "scenario: TAUJ0 channel 0 counting enabled",
                },
                {
                    "address": "0xFFE50080",
                    "hex": "00c0",
                    "evidence": "scenario: TAUJ0 CMOR0 selects valid but unimplemented CK3",
                },
            ],
            "artifacts": [],
            "checks": [
                {
                    "name": "unsupported timer mode emits no tauj-clock event",
                    "kind": "event-count",
                    "operation": "tauj-clock",
                    "equals": "0",
                },
                {
                    "name": "unsupported timer mode invents no interrupt request",
                    "kind": "event-count",
                    "operation": "interrupt-request",
                    "equals": "0",
                },
            ],
            "events": [{
                "kind": "clock",
                "after_instructions": 0,
                "evidence": "scenario: one p-bus clock burst onto the enabled channel",
                "p_bus_cycles": 8,
            }],
            "expected_fault": {
                "kind": "unsupported-timer-mode",
                "address": "0xFFE50080",
                "access": "clock",
            },
        },
        "interrupt-292-reserved.json": {
            "schema": "rh850-p1me-machine-scenario-v2",
            "name": "reserved-interrupt-channel-292-faults",
            "entry": PORTABLE_STORE_SELECTOR,
            "max_instructions": 4,
            "stop_addresses": ["0x00010000"],
            "gpr_fill": "0",
            "registers": registers,
            "memory": [],
            "artifacts": [],
            "checks": [
                {
                    "name": "reserved channel invents no interrupt request",
                    "kind": "event-count",
                    "operation": "interrupt-request",
                    "equals": "0",
                },
                {
                    "name": "reserved channel enters no handler",
                    "kind": "event-count",
                    "operation": "interrupt-enter",
                    "equals": "0",
                },
                {
                    "name": "reserved channel returns from nothing",
                    "kind": "event-count",
                    "operation": "interrupt-return",
                    "equals": "0",
                },
            ],
            "events": [{
                "kind": "interrupt",
                "after_instructions": 0,
                "evidence": "scenario: manual Table 6.11 reserves channel 292 with no reset row",
                "channel": 292,
            }],
            "expected_fault": {
                "kind": "unsupported-interrupt",
                "address": "0x00000124",
                "access": "request",
            },
        },
    }
    expectations = {
        "clock-unsupported-timer-mode.json": ("unsupported-timer-mode", "0xFFE50080", "clock"),
        "interrupt-292-reserved.json": ("unsupported-interrupt", "0x00000124", "request"),
    }
    paths = []
    for filename, scenario in scenarios.items():
        path = output_dir / filename
        path.write_text(json.dumps(scenario, indent=2) + "\n", encoding="utf-8")
        paths.append(path)
    run([
        str(REPO_ROOT / "tools/rh850"), "test", "firmware",
        "camry-8965F3307000", *(str(path) for path in paths),
        "--output-dir", str(output_dir),
    ])
    for path in paths:
        kind, address, access = expectations[path.name]
        report_path = output_dir / f"{path.stem}.report.json"
        if not report_path.is_file():
            raise AssertionError(f"{path.name}: expected-fault scenario lost its report")
        report = json.loads(report_path.read_text(encoding="utf-8"))
        fault = report.get("fault") or {}
        if report["status"] != "verified-expected-fault" or report.get("passed") is not True:
            raise AssertionError(f"{path.name}: structured fault not verified: {report!r}")
        if (fault.get("kind"), fault.get("address"), fault.get("access")) != (kind, address, access):
            raise AssertionError(f"{path.name}: wrong structured fault: {fault!r}")
        if report.get("termination_reason") != "expected-fault":
            raise AssertionError(
                f"{path.name}: termination drift: {report.get('termination_reason')!r}"
            )
        if report.get("instruction_count") != 0:
            raise AssertionError(
                f"{path.name}: fault must precede any entry instruction: {report!r}"
            )
        print(f"PASS {path.stem}: {kind} faults at the external-event boundary")


def main() -> int:
    run([str(REPO_ROOT / "tools/rh850"), "model", "check"])
    with tempfile.TemporaryDirectory(prefix="verify-rh850-machine-", dir=REPO_ROOT / "build/tmp") as tmp:
        output_root = Path(tmp)
        check_exact_scenarios(output_root)
        check_dynamic_request_signer_targets(output_root)
        check_schema_rejection(output_root)
        check_executable_overlay_rejection(output_root)
        check_fault_check_error_boundary(output_root)
        check_event_schema_rejections(output_root)
        check_execution_event_boundaries(output_root)
    print("PASS specification-backed multi-target RH850/P1M-E machine")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
