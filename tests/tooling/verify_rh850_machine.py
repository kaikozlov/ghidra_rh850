#!/usr/bin/env python3
"""Exercise target-discovered exact firmware scenarios through the P1M-E machine."""
from __future__ import annotations

import hashlib
import json
import subprocess
import tempfile
from pathlib import Path

import tools.targets.tss3.builders.build_tss3_request_signer as signer_builder
from tsk.ram_runtime.target_profiles import supported_targets, target_spec
from tools import REPO_ROOT
from tools.emulation.p1me_machine import load_scenario
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
    if not FIXTURE_ROOT.is_dir():
        return []
    batches: list[tuple[str, list[Path]]] = []
    for target_dir in sorted(path for path in FIXTURE_ROOT.iterdir() if path.is_dir()):
        scenarios = sorted(target_dir.glob("*.json"))
        if scenarios:
            batches.append((target_dir.name, scenarios))
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
                else "verified-stubbed-execution"
                if scenario.get("icus_startup_stub") is not None
                or scenario.get("dma_master_rewrite_assumption") is not None
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
    targets = supported_targets()
    build_dir = output_root / "dynamic-request-signer-build"
    metadata = signer_builder.build_request_signer(target=targets[0], output_dir=build_dir)
    helper_path = build_dir / metadata["helper"]["path"]
    for target in targets:
        spec = target_spec(target)
        result = verify_request_signer_target(
            target=target,
            contract=spec["contract"],
            helper_path=helper_path,
            output_dir=output_root / "dynamic-request-signer" / target,
        )
        if result["codeflash_sha256"] != spec["sha256"]:
            raise AssertionError(f"{target}: dynamic machine verification image drift")
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
    any RAM write lands. Ordinary checks and the second operand of a memory-equal
    check inspect uninitialized RAM. The report must retain the execution fault
    and publish each structured inspection error without fabricating equal bytes.
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
        "memory": [{
            "address": "0xFEBE0100", "hex": "5a",
            "evidence": "initialized first operand; comparison source remains uninitialized",
        }],
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
            {
                "name": "comparison requires initialized second operand",
                "kind": "memory-equal",
                "address": "0xFEBE0100",
                "source_address": "0xFEBE0104",
                "size": 1,
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


def check_memory_equality_failure(output_root: Path) -> None:
    """A real store producing different bytes must fail a memory-equal check."""
    scenario = {
        "schema": "rh850-p1me-machine-scenario-v2",
        "name": "memory-equal-detects-different-bytes",
        "entry": PORTABLE_STORE_SELECTOR,
        "max_instructions": 20,
        "stop_addresses": ["0x00010000"],
        "gpr_fill": "0",
        "registers": {"r6": "0xFEBE0100", "r7": "0x12", "lp": "0x00010000"},
        "memory": [{
            "address": "0xFEBE0104", "hex": "13",
            "evidence": "comparison byte differs from the real firmware store's input",
        }],
        "checks": [{
            "name": "different stored and source byte",
            "kind": "memory-equal", "address": "0xFEBE0100",
            "source_address": "0xFEBE0104", "size": 1,
        }],
    }
    path = output_root / "memory-equal-different.json"
    path.write_text(json.dumps(scenario, indent=2) + "\n", encoding="utf-8")
    run([
        str(REPO_ROOT / "tools/rh850"), "test", "firmware",
        "camry-8965F3307000", str(path), "--output-dir", str(output_root),
    ], expect_success=False)
    report = json.loads((output_root / "memory-equal-different.report.json").read_text())
    check = report["checks"][0]
    if (report.get("passed") is not False or check.get("passed") is not False
            or check.get("actual") != "different" or "error" in check):
        raise AssertionError(f"unequal initialized bytes must fail comparison: {report!r}")
    print("PASS memory-equal detects different initialized bytes")


def check_expected_termination_boundaries(output_root: Path) -> None:
    """A declared budget end must not hide a fault, early stop, or failed check."""
    output_dir = output_root / "termination-boundaries"
    output_dir.mkdir(parents=True, exist_ok=True)
    fixtures = FIXTURE_ROOT / "camry-8965F3307000"
    cases = [
        ("undeclared-budget", "csih-reset-cancels-relative-completion", "instruction-budget"),
        ("failed-check", "csih-reset-cancels-relative-completion", "instruction-budget"),
        ("early-stop", "csih-transmit-relative-frame-complete-and-poll", "stop-address"),
        ("unexpected-fault", "csih-loopback-mode-is-explicit-boundary", "unexpected-fault"),
    ]
    paths = []
    for name, fixture, _ in cases:
        scenario = json.loads((fixtures / f"{fixture}.json").read_text(encoding="utf-8"))
        scenario["name"] = f"termination-{name}"
        scenario.pop("expected_fault", None)
        if name == "undeclared-budget":
            scenario.pop("expected_termination")
        else:
            scenario["expected_termination"] = "instruction-budget"
        if name == "failed-check":
            scenario["checks"][0]["equals"] = "0"
        path = output_dir / f"{name}.json"
        path.write_text(json.dumps(scenario, indent=2) + "\n", encoding="utf-8")
        paths.append(path)
    run([
        str(REPO_ROOT / "tools/rh850"), "test", "firmware", "camry-8965F3307000",
        *(str(path) for path in paths), "--output-dir", str(output_dir),
    ], expect_success=False)
    for name, _, termination in cases:
        report = json.loads((output_dir / f"{name}.report.json").read_text(encoding="utf-8"))
        if report.get("passed") is not False or report.get("termination_reason") != termination:
            raise AssertionError(f"{name}: unexpected termination acceptance: {report!r}")
        if name == "failed-check":
            if report["checks"][0].get("passed") is not False:
                raise AssertionError("the deliberately wrong PC expectation must fail")
        elif not all(check.get("passed") is True for check in report["checks"]):
            raise AssertionError(f"{name}: unrelated checks failed: {report!r}")
        if name == "unexpected-fault" and report.get("fault", {}).get("kind") != "unsupported-csih-operation":
            raise AssertionError(f"wrong machine fault: {report!r}")
        print(f"PASS termination boundary {name}: {termination}")


def check_serial_repetition_normalization(output_root: Path) -> None:
    """Finite repetitions retain source order and lifetime transmit ordinals."""
    relative_serial = {
        "kind": "csih-word", "unit": 1, "value": "0x1234",
        "after_transmit_words": 3, "delay_instructions": 128,
        "evidence": "scenario: finite transmit-relative input normalization",
    }
    reset = {
        "kind": "peripheral-reset", "reset_class": "power-on", "after_instructions": 0,
        "evidence": "scenario: reset does not restart the lifetime transmitted-word ordinal",
    }
    scenario = {
        "schema": "rh850-p1me-machine-scenario-v2",
        "name": "serial-repetition-normalization",
        "entry": PORTABLE_STORE_SELECTOR,
        "max_instructions": 1,
        "stop_addresses": ["0x00010000"],
        "checks": [],
        "events": [
            {**relative_serial, "repeat": 3, "stride_words": 4},
            reset,
            {**relative_serial, "after_transmit_words": 4, "repeat": 2, "stride_words": 4},
            {**relative_serial, "unit": 2, "repeat": 2},
            {**relative_serial, "unit": 3},
            {
                **relative_serial, "after_transmit_words": (1 << 63) - 1,
                "stride_words": (1 << 63) - 1,
            },
        ],
    }
    path = output_root / "serial-repetition-normalization.json"
    path.write_text(json.dumps(scenario, indent=2) + "\n", encoding="utf-8")
    events = load_scenario(path)["events"]
    boundaries = [(event["unit"], event["after_transmit_words"]) if event["kind"] == "csih-word"
                  else event["kind"] for event in events]
    expected = [
        (1, 3), (1, 7), (1, 11), "peripheral-reset", (1, 4), (1, 8),
        (2, 3), (2, 4), (3, 3), (1, (1 << 63) - 1),
    ]
    if boundaries != expected or any("repeat" in event or "stride_words" in event for event in events):
        raise AssertionError(f"finite CSIH repetition normalization drift: {boundaries!r}")
    print("PASS finite CSIH repetitions normalize without changing order or reset ordinals")


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
    relative_serial = {
        "kind": "csih-word", "unit": 1, "value": "0x1234",
        "after_transmit_words": 1, "delay_instructions": 128,
        "evidence": "scenario: explicit launch-relative serial input",
    }
    adc_sample = {
        "kind": "adc-sample", "unit": 0, "channel": 0, "value": "0x800",
        "boundary": "normal", "after_instructions": 0,
        "evidence": "scenario: explicit synthetic ADC input",
    }
    rsent_frame = {
        "kind": "rsent-frame", "unit": 0,
        "after_spc_triggers": 1, "delay_hsb_cycles": 2000,
        "pulse_samples": [1344, 288, 312, 336, 360, 384, 408, 432, 336],
        "evidence": "scenario: explicit synthetic SPC pulse intervals",
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
            "memory-write-empty",
            {
                "kind": "memory-write",
                "after_instructions": 0,
                "evidence": "scenario: invalid empty asynchronous completion",
                "address": "0xFEBF0000",
                "data_hex": "",
            },
        ),
        (
            "memory-write-address-overflow",
            {
                "kind": "memory-write",
                "after_instructions": 0,
                "evidence": "scenario: invalid overflowing asynchronous completion",
                "address": "0xFFFFFFFF",
                "data_hex": "0000",
            },
        ),
        (
            "register-input-empty-name",
            {
                "kind": "register-input", "after_instructions": 0,
                "register": "", "value": "0",
                "evidence": "scenario: unnamed external register input",
            },
        ),
        (
            "register-input-bool-value",
            {
                "kind": "register-input", "after_instructions": 0,
                "register": "ICUSREG20", "value": True,
                "evidence": "scenario: boolean is not an integer-string input",
            },
        ),
        (
            "register-input-negative",
            {
                "kind": "register-input", "after_instructions": 0,
                "register": "ICUSREG20", "value": "-1",
                "evidence": "scenario: negative device input",
            },
        ),
        (
            "register-input-overflow",
            {
                "kind": "register-input", "after_instructions": 0,
                "register": "ICUSREG20", "value": "0x100000000",
                "evidence": "scenario: oversized device input",
            },
        ),
        (
            "register-read-response-overflow",
            {
                "kind": "register-input", "after_instructions": 0,
                "register": "DFERSTC", "value": "0x100000000",
                "evidence": "scenario: explicit bus response must fit declared 32-bit width",
            },
        ),
        (
            "unknown-event-kind",
            {**receive, "kind": "can-tx"},
        ),
        ("serial-zero-delay", {**relative_serial, "delay_instructions": 0}),
        ("serial-zero-ordinal", {**relative_serial, "after_transmit_words": 0}),
        ("serial-bool-ordinal", {**relative_serial, "after_transmit_words": True}),
        ("serial-mixed-boundaries", {**relative_serial, "after_instructions": 0}),
        ("serial-duplicate-word", [relative_serial, relative_serial]),
        ("serial-repeat-mixed-boundaries", {**relative_serial, "repeat": 2, "after_instructions": 0}),
        (
            "serial-repeat-on-absolute-input",
            {
                "kind": "csih-word", "unit": 1, "value": "0x1234",
                "after_instructions": 0, "repeat": 2,
                "evidence": "scenario: repetition is only transmit-relative",
            },
        ),
        (
            "serial-stride-on-absolute-input",
            {
                "kind": "csih-word", "unit": 1, "value": "0x1234",
                "after_instructions": 0, "stride_words": 2,
                "evidence": "scenario: stride is only transmit-relative",
            },
        ),
        ("serial-repeat-on-can-input", {**receive, "repeat": 2}),
        ("serial-stride-on-adc-input", {**adc_sample, "stride_words": 2}),
        ("serial-repeat-on-spc-input", {**rsent_frame, "repeat": 2}),
        ("serial-stride-on-spc-input", {**rsent_frame, "stride_words": 2}),
        (
            "serial-repeat-ordinal-overflow",
            {**relative_serial, "after_transmit_words": (1 << 63) - 1, "repeat": 2},
        ),
        (
            "serial-repeat-stride-overflow",
            {**relative_serial, "repeat": 3, "stride_words": (1 << 62)},
        ),
        (
            "serial-repeat-collides-with-explicit",
            [{**relative_serial, "repeat": 3}, {**relative_serial, "after_transmit_words": 3}],
        ),
        (
            "serial-explicit-collides-with-repeat",
            [{**relative_serial, "after_transmit_words": 3}, {**relative_serial, "repeat": 3}],
        ),
        (
            "serial-strided-repeat-collision",
            [
                {**relative_serial, "repeat": 3, "stride_words": 4},
                {**relative_serial, "after_transmit_words": 3, "repeat": 2, "stride_words": 2},
            ],
        ),
        (
            "serial-repeat-collision-across-reset",
            [
                {**relative_serial, "repeat": 3},
                {
                    "kind": "peripheral-reset", "reset_class": "power-on", "after_instructions": 0,
                    "evidence": "scenario: reset does not restart the lifetime transmitted-word ordinal",
                },
                {**relative_serial, "after_transmit_words": 3},
            ],
        ),
        ("adc-unit-not-present", {**adc_sample, "unit": 2}),
        ("adc-temperature-on-wrong-unit", {**adc_sample, "channel": 12}),
        ("adc-pin-channel-bool", {**adc_sample, "channel": True}),
        ("adc-code-underflow", {**adc_sample, "value": "-1"}),
        ("adc-code-overflow", {**adc_sample, "value": "0x1000"}),
        ("adc-numeric-code-not-string", {**adc_sample, "value": 2048}),
        ("adc-unknown-boundary", {**adc_sample, "boundary": "injected-result"}),
        ("adc-temperature-pull", {**adc_sample, "unit": 1, "channel": 12, "boundary": "pull-down"}),
        ("rsent-unit-not-present", {**rsent_frame, "unit": 2}),
        ("rsent-zero-ordinal", {**rsent_frame, "after_spc_triggers": 0}),
        ("rsent-negative-delay", {**rsent_frame, "delay_hsb_cycles": -1}),
        ("rsent-mixed-boundaries", {**rsent_frame, "after_instructions": 0}),
        ("rsent-zero-pulse", {**rsent_frame, "pulse_samples": [1344, 0, 312, 336]}),
        ("rsent-pulse-overflow", {**rsent_frame, "pulse_samples": [131072, 288, 312, 336]}),
        ("rsent-pulse-bool", {**rsent_frame, "pulse_samples": [True, 288, 312, 336]}),
        ("rsent-frame-too-long", {**rsent_frame, "pulse_samples": [288] * 10}),
        ("rsent-empty-evidence", {**rsent_frame, "evidence": ""}),
        ("rsent-injected-crc-verdict", {**rsent_frame, "crc_valid": True}),
        ("rsent-duplicate-response", [rsent_frame, rsent_frame]),
    ]
    cases.extend(
        (f"serial-{field}-{name}", {**relative_serial, field: value})
        for field in ("repeat", "stride_words")
        for name, value in (
            ("zero", 0), ("negative", -1), ("bool", True), ("float", 1.5),
            ("string", "2"), ("null", None), ("overflow", 1 << 63),
        )
    )
    invalid_scenarios: list[tuple[str, dict[str, object]]] = [
        (name, {"events": event if isinstance(event, list) else [event]})
        for name, event in cases
    ]
    invalid_scenarios.extend(
        (f"hsb-quantum-{name}", {"events": [], "hsb_cycles_per_instruction": value})
        for name, value in (("zero", 0), ("negative", -1), ("bool", True), ("overflow", 1 << 63))
    )
    cell = {
        "address": "0xff205000", "size": 4, "state": "erased",
        "evidence": "Explicit synthetic flash-cell state, not inferred payload blankness",
    }
    invalid_scenarios.extend(
        (f"dataflash-cells-{name}", {"dataflash_cells": rows})
        for name, rows in (
            ("not-a-list", cell),
            ("unaligned-address", [{**cell, "address": "0xff205001"}]),
            ("unaligned-size", [{**cell, "size": 3}]),
            ("zero-size", [{**cell, "size": 0}]),
            ("bool-size", [{**cell, "size": True}]),
            ("negative-address", [{**cell, "address": "-4"}]),
            ("address-wrap", [{**cell, "address": "0xfffffffc", "size": 8}]),
            ("numeric-address", [{**cell, "address": 0xff205000}]),
            ("unknown-state", [{**cell, "state": "assume-from-bytes"}]),
            ("missing-evidence", [{**cell, "evidence": ""}]),
            ("overlapping-states", [cell, {**cell, "state": "programmed"}]),
        )
    )
    startup_response = {
        "command": "0x7000", "error_bits": "0x0", "completion_hsb_cycles": 32,
    }
    startup_stub = {
        "evidence": "Explicit diagnostic startup assumption, not captured hardware",
        "responses": [startup_response],
    }
    invalid_scenarios.extend(
        (f"icus-startup-{name}", {"icus_startup_stub": value})
        for name, value in (
            ("not-object", []),
            ("missing-evidence", {"responses": [startup_response]}),
            ("empty-evidence", {**startup_stub, "evidence": ""}),
            ("empty-responses", {**startup_stub, "responses": []}),
            ("non-list-responses", {**startup_stub, "responses": startup_response}),
            ("non-object-response", {**startup_stub, "responses": [0]}),
            ("missing-command", {
                **startup_stub, "responses": [{"error_bits": "0", "completion_hsb_cycles": 32}],
            }),
        )
    )
    invalid_scenarios.extend(
        (f"icus-startup-{name}", {
            "icus_startup_stub": {**startup_stub, "responses": [{**startup_response, **changes}]},
        })
        for name, changes in (
            ("crypto-command", {"command": "0x5"}),
            ("selector", {"command": "0x17000"}),
            ("numeric-command", {"command": 0x7000}),
            ("negative-errors", {"error_bits": "-1"}),
            ("error-overflow", {"error_bits": "0x1000"}),
            ("numeric-errors", {"error_bits": 0}),
            ("zero-delay", {"completion_hsb_cycles": 0}),
            ("negative-delay", {"completion_hsb_cycles": -1}),
            ("bool-delay", {"completion_hsb_cycles": True}),
            ("delay-overflow", {"completion_hsb_cycles": 1 << 63}),
            ("output-payload", {"output_words": [0, 0, 0, 0]}),
        )
    )
    invalid_scenarios.extend(
        (f"dma-master-rewrite-{name}", {"dma_master_rewrite_assumption": value})
        for name, value in (("boolean", True), ("object", {}), ("empty", ""), ("blank", "  "))
    )
    for name, overrides in invalid_scenarios:
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
            **overrides,
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
        print(f"PASS scenario {name} rejected before emulation")


def check_execution_event_boundaries(output_root: Path) -> None:
    """Reserved interrupt requests must fault before executing the entry.

    Manual Table6.11 reserves channel292. An external request must not
    synthesize a reset value, handler vector, or delivery event.
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


def check_peripheral_file(output_root: Path) -> None:
    """Opted-in peripheral space reads back the last store and keeps scripted bytes.

    Without the flag, 0xFF000000 stays an unmapped write. The flag is the
    differential harness's model of a peripheral register file.
    """
    output_dir = output_root / "peripheral-file"
    output_dir.mkdir(parents=True, exist_ok=True)
    scenario = {
        "schema": "rh850-p1me-machine-scenario-v2",
        "name": "peripheral-readback",
        "entry": PORTABLE_STORE_SELECTOR,
        "max_instructions": 20,
        "stop_addresses": ["0x00010000"],
        "gpr_fill": "0",
        "peripheral_file": True,
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
        "memory": [{
            "address": "0xFF000000",
            "size": 2,
            "fill": 0x11,
            "evidence": "scripted peripheral bytes around the store",
        }],
        "checks": [
            {
                "name": "stored byte reads back",
                "kind": "memory",
                "address": "0xFF000000",
                "size": 1,
                "equals_hex": "5a",
            },
            {
                "name": "unread peripheral byte stays scripted",
                "kind": "memory",
                "address": "0xFF000001",
                "size": 1,
                "equals_hex": "11",
            },
        ],
    }
    path = output_dir / "peripheral-readback.json"
    path.write_text(json.dumps(scenario, indent=2) + "\n", encoding="utf-8")
    run([
        str(REPO_ROOT / "tools/rh850"), "test", "firmware",
        "camry-8965F3307000", str(path),
        "--output-dir", str(output_dir),
    ])
    report = json.loads((output_dir / "peripheral-readback.report.json").read_text(encoding="utf-8"))
    if report.get("passed") is not True or report.get("termination_reason") != "stop-address":
        raise AssertionError(f"peripheral read-back did not execute: {report!r}")
    print("PASS peripheral file reads back the last write and keeps scripted bytes")


def check_register_input_boundaries(output_root: Path) -> None:
    """External device input cannot alter CPU registers or issue device commands."""
    output_dir = output_root / "register-input-boundaries"
    output_dir.mkdir(parents=True, exist_ok=True)
    for name, register, value in (
        ("cpu-register", "PC", "0x100"),
        ("undeclared-write-only-command", "UCFSERSTCLR", "1"),
        ("byte-register-overflow", "FPMON", "0x100"),
        ("dcra-internal-state", "DCRA1COUT", "0"),
        ("flmd-internal-state", "FLMDCNT", "1"),
    ):
        scenario = {
            "schema": "rh850-p1me-machine-scenario-v2",
            "name": f"reject-register-input-{name}",
            "entry": PORTABLE_STORE_SELECTOR,
            "max_instructions": 4,
            "stop_addresses": ["0x00010000"],
            "gpr_fill": "0",
            "registers": {"lp": "0x00010000"},
            "checks": [],
            "events": [{
                "kind": "register-input", "after_instructions": 0,
                "register": register, "value": value,
                "evidence": "scenario: invalid external device input boundary",
            }],
        }
        path = output_dir / f"{name}.json"
        path.write_text(json.dumps(scenario, indent=2) + "\n", encoding="utf-8")
        run([
            str(REPO_ROOT / "tools/rh850"), "test", "firmware",
            "camry-8965F3307000", str(path), "--output-dir", str(output_dir),
        ], expect_success=False)
        report = json.loads((output_dir / f"{path.stem}.report.json").read_text())
        if (report.get("passed") is not False
                or report.get("termination_reason") != "runner-error"
                or report.get("error", {}).get("type") != "IllegalArgumentException"):
            raise AssertionError(f"{name}: device-input boundary did not reject the scenario")
        print(f"PASS register-input {name} rejected at device-model boundary")


def main() -> int:
    run([str(REPO_ROOT / "tools/rh850"), "model", "check"])
    with tempfile.TemporaryDirectory(prefix="verify-rh850-machine-", dir=REPO_ROOT / "build/tmp") as tmp:
        output_root = Path(tmp)
        check_exact_scenarios(output_root)
        check_dynamic_request_signer_targets(output_root)
        check_schema_rejection(output_root)
        check_expected_termination_boundaries(output_root)
        check_executable_overlay_rejection(output_root)
        check_fault_check_error_boundary(output_root)
        check_memory_equality_failure(output_root)
        check_serial_repetition_normalization(output_root)
        check_event_schema_rejections(output_root)
        check_execution_event_boundaries(output_root)
        check_register_input_boundaries(output_root)
        check_peripheral_file(output_root)
    print("PASS specification-backed multi-target RH850/P1M-E machine")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
