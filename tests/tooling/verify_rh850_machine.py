#!/usr/bin/env python3
"""Exercise target-discovered exact firmware scenarios through the P1M-E machine."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import tempfile
from collections import Counter
from pathlib import Path

import tools.targets.tss3.builders.build_tss3_request_signer as signer_builder
from tsk.ram_runtime.target_profiles import supported_targets, target_spec
from tools import REPO_ROOT
from tools.emulation.execution_coverage import read_drcov
from tools.emulation.p1me_machine import (
    P1MEMachineError,
    _target_contract,
    _write_drcov,
    capture_many,
    load_scenario,
)
from tools.emulation.p1me_can_bridge import write_bridge_scenario

from tools.targets.camry.research import replay_camry_f33_capture_machine as replay
from tools.targets.tss3.request_signer_machine import verify_request_signer_target

JIT_BATCH_THRESHOLD = 1_000_000

FIXTURE_ROOT = REPO_ROOT / "tests/fixtures/rh850/machine"

RESET_TO_RUNTIME_FIXTURE = replay.BOARD_FIXTURE
SLOW_FIXTURES = {RESET_TO_RUNTIME_FIXTURE}

PORTABLE_STORE_SELECTOR = {
    "role": "p1me-byte-store-primitive",
    "scope": "function",
    "shape_sha256": "8e49a0bf8bf3a1a29e104d2a16a92e063499f8ea357df01e11a0bca0db68aa41",
    "instruction_count": 14,
    "body_size": 36,
    "offset": -18,
    "requirements": [],
}


def run(
    command: list[str], *, expect_success: bool = True,
    env: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    proc = subprocess.run(
        command, cwd=REPO_ROOT, text=True, capture_output=True, check=False, env=env,
    )
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

def check_fixture_schemas() -> None:
    failures: list[str] = []
    for _target, scenarios in fixture_batches():
        for path in scenarios:
            try:
                load_scenario(path)
            except P1MEMachineError as exc:
                failures.append(f"{path.relative_to(REPO_ROOT)}: {exc}")
    if failures:
        raise AssertionError(
            "machine fixture schema rejection:\n" + "\n".join(failures)
        )
    print("PASS every tracked machine fixture satisfies the scenario schema")

def check_slow_fixture_contracts() -> None:
    scenario = load_scenario(RESET_TO_RUNTIME_FIXTURE)
    ready_check = any(
        row["kind"] == "memory" and row["address"] == "0xfebe3800"
        and row["size"] == 1 and row.get("equals_hex") == "5a"
        for row in scenario["checks"]
    )
    if (
        scenario["entry"]["address"] != "0x0"
        or scenario["reset"] != "power-on"
        or scenario["stop_addresses"] != ["0x660bc"]
        or scenario["expected_termination"] != "stop-address"
        or not ready_check
    ):
        raise AssertionError("tracked reset-to-runtime contract drifted")
    print("PASS reset-to-runtime slow fixture schema and milestone contract")

def check_bridge_ready_contract(output_root: Path) -> None:
    replay_scenario = replay.build_replay_scenario(
        {}, [replay.CapturePeriod(0, (), ())], "diagnostic-ready-prefix",
    )
    readiness = replay_scenario["steps"][:replay.REPLAY_PREFIX_STEPS]
    completion_address = hex(replay.FOREGROUND_COMPLETE)
    empty_cycles = sum(
        step["kind"] == "trial" and completion_address in step["stop_addresses"]
        and not step["events"] for step in readiness
    )
    bridge_path = output_root / "diagnostic-ready-bridge.json"
    write_bridge_scenario(bridge_path, 12345)
    bridge = load_scenario(bridge_path)
    if (
        bridge["event_socket"] != {
            "host": "127.0.0.1",
            "port": 12345,
            "ready_after_arrivals": {"address": completion_address, "count": empty_cycles},
        }
        or empty_cycles != 26
        or bridge["max_instructions"] != 5_000_000_000
        or bridge["expected_termination"] != "halt"
        or bridge["stop_addresses"]
    ):
        raise AssertionError("diagnostic-ready bridge or replay prefix drifted")
    print("PASS bridge readiness threshold matches the replay's 26 empty cycles")


def check_exact_scenarios(output_root: Path) -> None:
    for target, all_scenarios in fixture_batches():
        scenarios = [path for path in all_scenarios if path not in SLOW_FIXTURES]
        # Interpretation wins for short, isolated fixtures because class generation
        # cannot amortize before they stop. Keep long cases on the default JIT.
        groups = (
            ("plain", [
                path for path in scenarios
                if int(json.loads(path.read_text())["max_instructions"])
                <= JIT_BATCH_THRESHOLD
            ]),
            ("jit", [
                path for path in scenarios
                if int(json.loads(path.read_text())["max_instructions"])
                > JIT_BATCH_THRESHOLD
            ]),
        )
        rows_by_path = {}
        for engine, engine_scenarios in groups:
            if not engine_scenarios:
                continue
            output_dir = output_root / target / engine
            proc = run([
                str(REPO_ROOT / "tools/rh850"),
                "test",
                "firmware",
                target,
                *(str(path) for path in engine_scenarios),
                "--output-dir",
                str(output_dir),
            ], env={**os.environ, "P1ME_MACHINE_ENGINE": engine})
            engine_rows = json.loads(proc.stdout)["reports"]
            if len(engine_rows) != len(engine_scenarios):
                raise AssertionError(f"{target}/{engine}: report count drift")
            rows_by_path.update(zip(engine_scenarios, engine_rows, strict=True))
        rows = [rows_by_path[path] for path in scenarios]
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
            if scenario_path.name == "checkpoint-restore-tauj-identity.json":
                trials = report["checkpointing"]["trials"]
                if [trial["name"] for trial in trials] != [
                    "straight", "restored-1", "restored-2",
                ]:
                    raise AssertionError(
                        f"{scenario_path.name}: checkpoint identity trial set drift",
                    )
                identity_fields = (
                    "register_rows", "memory_rows", "event_rows", "checks",
                    "final_pc", "instruction_count", "termination_reason", "passed",
                )
                expected = {field: trials[0][field] for field in identity_fields}
                for trial in trials[1:]:
                    actual = {field: trial[field] for field in identity_fields}
                    if actual != expected:
                        raise AssertionError(
                            f"{scenario_path.name}/{trial['name']}: "
                            "checkpoint state leaked or identity drifted",
                        )
                if report["checkpointing"]["uncaptured_components"]:
                    raise AssertionError(
                        f"{scenario_path.name}: machine component was not checkpointed",
                    )
                print(
                    f"PASS {target}/{scenario_path.name}: straight and two restored "
                    "trials have byte-identical register, memory, event, and check rows",
                )
            if scenario_path.name == "camry_f33_security_attempt_limit_and_session_lockout.json":
                trial_names = [
                    trial["name"] for trial in report["checkpointing"]["trials"]
                ]
                if trial_names != [
                    "attempt-limit-and-session-lockout",
                    "external-pin-reset-to-first-foreground",
                    "post-reset-operational-readiness",
                ]:
                    raise AssertionError(
                        f"{scenario_path.name}: reset readiness trial set drift",
                    )
                diagnostic_payloads = [
                    event["data_hex"]
                    for event in report["device_events"]
                    if event["kind"] == "can-tx"
                    and event.get("can_id", "").lower() == "0x000007a9"
                ]
                expected_seed_frames = [
                    "10126703bdcd5f4d",
                    "21ce052555b348ee",
                    "22bfa98c278c0000",
                ]
                positions = iter(diagnostic_payloads)
                if not all(any(payload == expected for payload in positions)
                           for expected in expected_seed_frames):
                    raise AssertionError(
                        f"{scenario_path.name}: complete seed response frames drifted",
                    )
                print(
                    f"PASS {target}/{scenario_path.name}: complete seed response and "
                    "external reset reach the 26-cycle operational readiness gate",
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


def check_drcov_text_grammar(output_root: Path) -> None:
    """The text table grammar follows DynamoRIO's drcov text dump fields."""
    target = _target_contract("camry-8965F3307000")
    module = target["codeflash"]
    module_path = Path(module["path"]).resolve().relative_to(REPO_ROOT)
    reference_path = output_root / "reference-text.drcov"
    reference_path.write_text(
        "DRCOV VERSION: 3\n"
        "DRCOV FLAVOR: drcov\n"
        "Module Table: version 5, count 1\n"
        "Columns: id, containing_id, start, end, entry, offset, preferred_base, path\n"
        f"{0:3d}, {0:3d}, 0x{int(module['base'], 0):016x}, "
        f"0x{int(module['base'], 0) + module['size']:016x}, 0x{0:016x}, "
        f"0x{0:016x}, 0x{int(module['base'], 0):016x},  {module_path}\n"
        "BB Table: 2 bbs\n"
        "module id, start, size:\n"
        "module[  0]: 0x0000000000000002,   4\n"
        "module[  0]: 0x0000000000000000,   2\n",
        encoding="utf-8",
    )
    reference = read_drcov(reference_path)
    if reference.blocks != ((2, 4), (0, 2)):
        raise AssertionError(f"reference drcov grammar parsed incorrectly: {reference.blocks!r}")

    writer_path = output_root / "writer-text.drcov"
    report = {"instruction_trace": [
        {"pc": "0x00000002", "size": 4},
        {"pc": "0x00000000", "size": 2},
        {"pc": "0x00000002", "size": 4},
    ]}
    _write_drcov(report, target, writer_path)
    written = read_drcov(writer_path)
    if written.module != reference.module or written.blocks != reference.blocks:
        raise AssertionError("writer did not emit the module and unique first-seen blocks")
    print("PASS DynamoRIO text drcov grammar and unique first-seen writer")


def check_scenario_source_contract(output_root: Path) -> None:
    fixture = FIXTURE_ROOT / "camry-8965F3307000" / "strict-counted-loop.json"
    scenario = json.loads(fixture.read_text(encoding="utf-8"))
    scenario["name"] = "strict-counted-loop-with-source"
    source = {
        "kind": "captured-can",
        "sha256": "7f" * 32,
        "detail": {"channels": [0, 1], "reviewed": True},
    }
    scenario["source"] = source
    path = output_root / "scenario-source.json"
    path.write_text(json.dumps(scenario, indent=2) + "\n", encoding="utf-8")
    report = capture_many(
        "camry-8965F3307000", [path], output_root / "scenario-source-output",
    )[0]
    if report["resolved_run_contract"].get("source") != source:
        raise AssertionError("scenario source object did not survive into resolved_run_contract")

    scenario["source"] = None
    path.write_text(json.dumps(scenario, indent=2) + "\n", encoding="utf-8")
    try:
        load_scenario(path)
    except P1MEMachineError:
        pass
    else:
        raise AssertionError("explicit null scenario source was accepted")
    print("PASS optional scenario source object is preserved and non-objects are rejected")

def check_reset_replay_contract(output_root: Path) -> None:
    """A reset can replay a validated scenario's board inputs relative to restart."""
    fragment = {
        "schema": "rh850-p1me-machine-scenario-v2",
        "name": "reset-replay-fragment",
        "entry": {"role": "reset-replay-fragment", "scope": "resolved-address", "address": "0x78ae6"},
        "max_instructions": 4,
        "stop_addresses": ["0x10000"],
        "gpr_fill": "0",
        "registers": {"lp": "0x10000"},
        "memory": [{
            "address": "0xfebe0100", "hex": "a5",
            "evidence": "reset replay immediate memory row",
        }],
        "events": [{
            "kind": "memory-write", "after_instructions": 2,
            "address": "0xfebe0101", "data_hex": "5a",
            "evidence": "reset replay instruction-relative event",
        }],
        "checks": [],
    }
    fragment_path = output_root / "reset-replay-fragment.json"
    fragment_path.write_text(json.dumps(fragment, indent=2) + "\n", encoding="utf-8")
    scenario = {
        "schema": "rh850-p1me-machine-scenario-v2",
        "name": "reset-replay-contract",
        "entry": {"role": "reset-replay-test", "scope": "resolved-address", "address": "0x78ae6"},
        "max_instructions": 512,
        "stop_addresses": ["0x10000"],
        "gpr_fill": "0",
        "registers": {"lp": "0x10000"},
        "reset_replay": {"scenario": fragment_path.name},
        "events": [{
            "kind": "reset-assert", "after_instructions": 1,
            "reset_class": "system-1-pin",
            "evidence": "exercise reset-relative board input replay",
        }],
        "expected_fault": {
            "kind": "missing-reset-input", "address": "0xffd60010", "access": "read",
        },
        "checks": [
            {
                "name": "replayed memory row", "kind": "memory",
                "address": "0xfebe0100", "size": 1, "equals_hex": "a5",
            },
            {
                "name": "replayed relative event", "kind": "memory",
                "address": "0xfebe0101", "size": 1, "equals_hex": "5a",
            },
        ],
    }
    path = output_root / "reset-replay-contract.json"
    path.write_text(json.dumps(scenario, indent=2) + "\n", encoding="utf-8")
    report = capture_many(
        "camry-8965F3307000", [path], output_root / "reset-replay-output",
    )[0]
    reset_rows = [row for row in report["device_events"] if row["kind"] == "reset-assert"]
    if (
        not report["passed"]
        or len(reset_rows) != 1
        or reset_rows[0].get("replayed_scenario") != str(fragment_path.resolve())
        or reset_rows[0].get("replayed_memory_rows") != 1
        or reset_rows[0].get("replayed_event_rows") != 1
    ):
        raise AssertionError(f"reset replay contract drifted: {report!r}")
    print("PASS reset replays validated board memory and instruction-relative events")


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
    partial_reads = [
        ("0xFEBE00FF", 2, "0xFEBE00FF"),  # Initialized suffix.
        ("0xFEBE0100", 2, "0xFEBE0101"),  # Initialized prefix.
        ("0xFEBE0FFF", 3, "0xFEBE1000"),  # Hole across a storage-page boundary.
    ]
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
        }, {
            "address": "0xFEBE0FFF", "hex": "5a",
            "evidence": "initialized byte before a one-byte hole at the storage-page boundary",
        }, {
            "address": "0xFEBE1001", "hex": "a5",
            "evidence": "initialized byte after the one-byte hole",
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
            *({
                "name": f"partial RAM range {address}",
                "kind": "memory", "address": address, "size": size,
                "equals_hex": "00" * size,
            } for address, size, _ in partial_reads),
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
    checks_by_name = {row["name"]: row for row in report["checks"]}
    for address, _, missing in partial_reads:
        error = checks_by_name[f"partial RAM range {address}"]["error"]
        if error.get("address") != missing:
            raise AssertionError(f"partial read lost its first uninitialized byte: {error!r}")
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
    """Unknown interrupt requests fail closed unless exact firmware supplies the EIC control.

    Manual Table6.11 reserves channel292. The exact Camry image nevertheless
    initializes EIC292 and installs its table-vector handler. A scenario must
    supply that firmware-derived control word explicitly to exercise the handler.
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

    firmware_path = output_dir / "interrupt-292-firmware-derived.json"
    firmware_path.write_text(json.dumps({
        "schema": "rh850-p1me-machine-scenario-v2",
        "name": "firmware-derived-interrupt-channel-292-enters-exact-vector",
        "entry": PORTABLE_STORE_SELECTOR,
        "max_instructions": 4,
        "stop_addresses": ["0x00066146"],
        "gpr_fill": "0",
        "registers": {
            **registers,
            "RBASE": "0",
            "INTBP": "0x00020200",
        },
        "memory": [],
        "artifacts": [],
        "checks": [{
            "name": "firmware-derived channel requests once",
            "kind": "event-count",
            "operation": "interrupt-request",
            "equals": "1",
        }, {
            "name": "firmware-derived channel enters exact vector",
            "kind": "event-count",
            "operation": "interrupt-enter",
            "equals": "1",
        }],
        "events": [{
            "kind": "interrupt",
            "after_instructions": 0,
            "evidence": (
                "Exact Camry startup 62E6A writes EIC292=0x48 and "
                "INTBP[292] contains 0x66142"
            ),
            "channel": 292,
            "firmware_control": "0x48",
        }],
        "expected_termination": "stop-address",
    }, indent=2) + "\n", encoding="utf-8")
    run([
        str(REPO_ROOT / "tools/rh850"), "test", "firmware",
        "camry-8965F3307000", str(firmware_path),
        "--output-dir", str(output_dir),
    ])
    firmware_report = json.loads(
        (output_dir / "interrupt-292-firmware-derived.report.json").read_text(
            encoding="utf-8"
        )
    )
    if firmware_report.get("passed") is not True:
        raise AssertionError(
            f"firmware-derived channel292 did not enter exact vector: {firmware_report!r}"
        )
    events = Counter(event["kind"] for event in firmware_report["device_events"])
    if events["interrupt-request"] != 1 or events["interrupt-enter"] != 1:
        raise AssertionError(
            f"firmware-derived channel292 event count drift: {events!r}"
        )
    print("PASS firmware-derived interrupt292 enters exact table vector")


def check_rscfd_transmit_results(output_root: Path) -> None:
    """Verify Tx results plus global reset status and FIFO initialization."""
    output_dir = output_root / "rscfd-transmit-results"
    output_dir.mkdir(parents=True, exist_ok=True)
    registers = {
        "sp": "0xFEBE2000",
        "gp": "0xFEBEB800",
        "tp": "0x00023DFC",
        "lp": "0x00010000",
        "PSW": "0x20",
        "PMR": "0",
    }
    scenarios = [{
        "schema": "rh850-p1me-machine-scenario-v2",
        "name": "rscfd-transmit-completion-summary",
        "entry": PORTABLE_STORE_SELECTOR,
        "max_instructions": 20,
        "stop_addresses": ["0x00010000"],
        "gpr_fill": "0",
        "registers": {
            **registers,
            "r6": "0xFFD20266",
            "r7": "1",
        },
        "memory": [
            {"address": "0xFFD20266", "hex": "00",
             "evidence": "Idle channel1 local-resource6 transmit control"},
            {"address": "0xFFD242C0", "hex": "a9070000",
             "evidence": "Synthetic standard identifier"},
            {"address": "0xFFD242C4", "hex": "00000000",
             "evidence": "Synthetic pointer word"},
            {"address": "0xFFD242C8", "hex": "00000000",
             "evidence": "Synthetic FD status word"},
            {"address": "0xFFD242CC", "hex": "01020304",
             "evidence": "Synthetic payload bytes0..3"},
            {"address": "0xFFD242D0", "hex": "05060708",
             "evidence": "Synthetic payload bytes4..7"},
        ],
        "artifacts": [],
        "checks": [
            {"name": "one transmit", "kind": "event-count",
             "operation": "can-tx", "equals": "1"},
            {"name": "one completion", "kind": "event-count",
             "operation": "can-tx-complete", "equals": "1"},
            {"name": "resource6 summary", "kind": "memory",
             "address": "0xFFD20372", "size": 2, "equals_hex": "4000"},
            {"name": "resource6 result", "kind": "memory",
             "address": "0xFFD202E6", "size": 1, "equals_hex": "04"},
            {"name": "request clears", "kind": "memory",
             "address": "0xFFD20266", "size": 1, "equals_hex": "00"},
        ],
        "events": [
            {"kind": "register-input", "register": "TMIEC0", "value": "0x00c00000",
             "after_instructions": 0, "evidence": "Channel1 resources6 and7 interrupt enabled"},
            {"kind": "can-tx-complete", "buffer": 22, "firmware_control": "0x8048",
             "after_instructions": 2, "evidence": "External completion of emitted buffer22"},
        ],
        "expected_termination": "stop-address",
    }, {
        "schema": "rh850-p1me-machine-scenario-v2",
        "name": "rscfd-transmit-result-clear",
        "entry": PORTABLE_STORE_SELECTOR,
        "max_instructions": 20,
        "stop_addresses": ["0x00010000"],
        "gpr_fill": "0",
        "registers": {
            **registers,
            "r6": "0xFFD202E6",
            "r7": "0",
        },
        "memory": [
            {"address": "0xFFD202E6", "hex": "04",
             "evidence": "Completed channel1 local-resource6 transmit result"},
            {"address": "0xFFD20372", "hex": "4000",
             "evidence": "Channel1 result summary bit6"},
            {"address": "0xFFFFB178", "hex": "4890",
             "evidence": "Exact level-triggered EIC188 control with EIRF asserted"},
        ],
        "artifacts": [],
        "checks": [
            {"name": "summary clears", "kind": "memory",
             "address": "0xFFD20372", "size": 2, "equals_hex": "0000"},
            {"name": "result clears", "kind": "memory",
             "address": "0xFFD202E6", "size": 1, "equals_hex": "00"},
            {"name": "level request clears", "kind": "memory",
             "address": "0xFFFFB178", "size": 2, "equals_hex": "4880"},
        ],
        "events": [
            {"kind": "register-input", "register": "TMIEC0", "value": "0x00c00000",
             "after_instructions": 0, "evidence": "Channel1 resources6 and7 interrupt enabled"},
        ],
        "expected_termination": "stop-address",
    }, {
        "schema": "rh850-p1me-machine-scenario-v2",
        "name": "rscfd-global-reset-mode-and-fifo",
        "entry": {
            "role": "original-ecc-word-store-and-readback",
            "scope": "resolved-address",
            "address": "0x7e0",
        },
        "max_instructions": 4,
        "stop_addresses": ["0x000007E4"],
        "gpr_fill": "0",
        "registers": {
            **registers,
            "ep": "0xFFD20088",
            "r1": "1",
        },
        "memory": [
            {"address": "0xFFD20088", "hex": "00000000",
             "evidence": "Global operating mode before reset request"},
            {"address": "0xFFD20014", "hex": "00000000",
             "evidence": "Channel1 communication mode"},
            {"address": "0xFFD2012C", "hex": "03110000",
             "evidence": "Enabled diagnostic common FIFO5"},
        ],
        "artifacts": [],
        "checks": [
            {"name": "global reset status sets and RAM initialization completes",
             "kind": "memory", "address": "0xFFD2008C", "size": 4,
             "equals_hex": "01000000"},
            {"name": "global reset empties FIFO5", "kind": "memory",
             "address": "0xFFD2018C", "size": 4,
             "equals_hex": "01000000"},
        ],
        "events": [{
            "kind": "can-rx", "fifo": 5, "boundary": "post-filter",
            "can_id": "0x7A1", "data_hex": "0210030000000000",
            "label": 52, "after_instructions": 0,
            "evidence": "Populate FIFO before global reset",
        }],
        "expected_termination": "stop-address",
    }]
    paths: list[Path] = []
    for scenario in scenarios:
        path = output_dir / f"{scenario['name']}.json"
        path.write_text(json.dumps(scenario, indent=2) + "\n", encoding="utf-8")
        paths.append(path)
    run([
        str(REPO_ROOT / "tools/rh850"), "test", "firmware",
        "camry-8965F3307000", *(str(path) for path in paths),
        "--output-dir", str(output_dir),
    ])
    for path in paths:
        report = json.loads(
            (output_dir / f"{path.stem}.report.json").read_text(encoding="utf-8")
        )
        if report.get("passed") is not True or report.get("termination_reason") != "stop-address":
            raise AssertionError(f"{path.stem}: RSCFD result lifecycle drift: {report!r}")
    print("PASS RSCFD transmit results, global mode status, and FIFO reset")


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


def check_runtime_soak(output_root: Path) -> None:
    target = "camry-8965F3307000"
    fixture = RESET_TO_RUNTIME_FIXTURE
    boot_output = output_root / "boot-milestone"
    boot_output.mkdir(parents=True, exist_ok=True)
    boot_proc = run([
        str(REPO_ROOT / "tools/rh850"), "test", "firmware", target, str(fixture),
        "--output-dir", str(boot_output),
    ])
    boot_result = json.loads(boot_proc.stdout)
    boot_report = json.loads(
        Path(boot_result["reports"][0]["report"]).read_text(encoding="utf-8")
    )
    if (
        not boot_report["passed"]
        or boot_report["termination_reason"] != "stop-address"
        or boot_report["final_pc"].lower() != "0x000660bc"
        or not all(row["passed"] for row in boot_report["checks"])
    ):
        raise AssertionError("reset-to-runtime milestone scenario failed")
    print(
        f"PASS reset-to-runtime slow milestone: "
        f"{boot_report['instruction_count']} instructions"
    )

    scenario = json.loads(fixture.read_text(encoding="utf-8"))
    scenario.update(
        name="original-reset-runtime-soak",
        max_instructions=80_000_000,
        stop_addresses=[],
        expected_termination="instruction-budget",
    )
    path = output_root / f"{scenario['name']}.json"
    path.write_text(json.dumps(scenario, indent=2) + "\n", encoding="utf-8")
    proc = run([
        str(REPO_ROOT / "tools/rh850"), "test", "firmware", target, str(path),
        "--output-dir", str(output_root),
    ])
    result = json.loads(proc.stdout)
    report = json.loads(Path(result["reports"][0]["report"]).read_text(encoding="utf-8"))
    if not report["passed"] or report["status"] != "verified-stubbed-execution":
        raise AssertionError("runtime soak did not complete its declared execution contract")
    events = report["device_events"]
    interrupts = Counter(row["kind"] for row in events if row["kind"].startswith("interrupt-"))
    if interrupts["interrupt-enter"] < 2 or interrupts["interrupt-enter"] != interrupts["interrupt-return"]:
        raise AssertionError(f"runtime soak did not sustain balanced interrupt delivery: {interrupts}")
    flash = Counter(
        row["operation"] for row in events
        if row["kind"] == "faci-completion" and row["operation"] in {"erase", "program"}
    )
    if flash != {"erase": 9, "program": 85}:
        raise AssertionError(f"runtime soak DataFlash lifecycle changed: {flash}")
    serial = Counter(row["unit"] for row in events if row["kind"] == "csih-word")
    if serial[1] <= 252 or serial[2] < 2 or serial[3] < 2:
        raise AssertionError(f"runtime soak did not continue all CSIH units beyond startup: {serial}")
    print(
        f"PASS runtime soak: {report['instruction_count']} instructions, "
        f"{interrupts['interrupt-return']} interrupt round trips, "
        f"DataFlash={dict(flash)}, CSIH={dict(serial)}"
    )


def check_campaign_machine_features(output_root: Path) -> None:
    """Check execution observations and boundary events."""
    output_dir = output_root / "campaign-features"
    output_dir.mkdir(parents=True, exist_ok=True)

    compare = {
        "schema": "rh850-p1me-machine-scenario-v2",
        "name": "campaign-compare-and-index",
        "entry": {
            "role": "security-delay-bit-helper",
            "scope": "resolved-address",
            "address": "0x96622",
        },
        "max_instructions": 30,
        "stop_addresses": ["0x10000"],
        "gpr_fill": "0",
        "registers": {
            "r6": "0", "r7": "1", "gp": "0xfebeb800",
            "lp": "0x10000", "PSW": "0",
        },
        "memory": [{
            "address": "0xfebe5dc8", "hex": "00000000",
            "evidence": "Synthetic SecurityAccess delay-bit cell",
        }],
        "checks": [],
        "compare_operands": True,
    }
    compare_path = output_dir / "compare-index.json"
    compare_path.write_text(json.dumps(compare, indent=2) + "\n", encoding="utf-8")
    compare_report = capture_many(
        "camry-8965F3307000", [compare_path], output_dir,
    )[0]
    rows = compare_report["compare_operands"]
    expected = [
        ("0x00096626", "0x00096628", "0x00000002", "0x00000000"),
        ("0x00096634", "0x00096636", "0x00000001", "0x00000001"),
    ]
    actual = [
        (row["compare_pc"], row["branch_pc"], row["left"], row["right"])
        for row in rows
    ]
    if actual != expected:
        raise AssertionError(f"compare operand observations drifted: {actual!r}")

    index = {
        "schema": "rh850-p1me-machine-scenario-v2",
        "name": "campaign-indexed-load",
        "entry": {
            "role": "synthetic-indexed-load",
            "scope": "resolved-address",
            "address": "0xfebe0000",
        },
        "max_instructions": 10,
        "stop_addresses": ["0x10000"],
        "gpr_fill": "0",
        "registers": {
            "r6": "2", "r7": "0xfebe0100",
            "lp": "0x10000", "PSW": "0",
        },
        "memory": [
            {
                "address": "0xfebe0000",
                "hex": "c232c731264701007f00",
                "evidence": "shl 2,r6; add r7,r6; ld.w 0[r6],r8; jmp [lp]",
            },
            {
                "address": "0xfebe0108", "hex": "5a000000",
                "evidence": "Synthetic indexed-load source",
            },
        ],
        "checks": [],
        "input_derived_table_indices": True,
    }
    snapshot_path = output_dir / "indexed-load-snapshot.bin"
    snapshots = [{
        "path": str(snapshot_path),
        "address": "0xfebe0108",
        "size": 4,
        "evidence": "Synthetic snapshot-output contract",
    }]
    index_path = output_dir / "index.json"
    index_path.write_text(
        json.dumps({**index, "snapshot_outputs": snapshots}, indent=2) + "\n",
        encoding="utf-8",
    )
    index_report = capture_many(
        "camry-8965F3307000", [index_path], output_dir,
    )[0]
    indices = index_report["input_derived_table_indices"]
    if not any(
        row["base"] == "0xFEBE0100"
        and row["index"] == "0x00000002"
        and row["scale"] == 4
        and row["effective_address"] == "0xFEBE0108"
        and row["access"] == "load"
        for row in indices
    ):
        raise AssertionError(f"indexed load observation missing: {indices!r}")
    if (
        snapshot_path.read_bytes() != b"\x5a\x00\x00\x00"
        or index_report["snapshot_outputs"][0]["sha256"]
            != hashlib.sha256(b"\x5a\x00\x00\x00").hexdigest()
    ):
        raise AssertionError("snapshot output did not preserve exact initialized bytes")

    wait_fixture = FIXTURE_ROOT / "camry-8965F3307000" / (
        "camry_f33_scheduler_publication_foreground_wait_no_service.json"
    )
    trial = json.loads(wait_fixture.read_text(encoding="utf-8"))
    trial.update(
        name="campaign-stop-after-arrivals",
        entry={
            "role": "foreground-wait-loop",
            "scope": "resolved-address",
            "address": "0x66066",
        },
        max_instructions=20,
        stop_addresses=[],
        checks=[],
        expected_termination="instruction-budget",
        steps=[
            {"kind": "checkpoint", "name": "wait", "after_instructions": 0},
            {
                "kind": "trial", "name": "second-arrival",
                "max_instructions": 20, "stop_addresses": [],
                "stop_after_arrivals": [{"address": "0x66066", "count": 2}],
                "events": [], "checks": [],
            },
            {"kind": "checkpoint", "name": "current"},
            {"kind": "restore", "checkpoint": "wait"},
            {
                "kind": "trial", "name": "budget-before-third",
                "max_instructions": 2, "stop_addresses": [],
                "stop_after_arrivals": [{"address": "0x66066", "count": 3}],
                "events": [], "checks": [], "capture_rows": False,
            },
        ],
    )
    trial_path = output_dir / "stop-after-arrivals.json"
    trial_path.write_text(json.dumps(trial, indent=2) + "\n", encoding="utf-8")
    trial_report = capture_many(
        "camry-8965F3307000", [trial_path], output_dir,
        instruction_trace=True,
    )[0]
    first, second = trial_report["checkpointing"]["trials"]
    current_checkpoint = trial_report["checkpointing"]["checkpoints"][1]
    if (
        first["termination_reason"] != "stop-after-arrivals"
        or first["stop_after_arrivals"][0]["arrivals"] != 2
        or not first["instruction_trace"]
        or current_checkpoint["instruction"]
            != first["start_instruction"] + first["instruction_count"]
        or second["termination_reason"] != "instruction-budget"
        or second["stop_after_arrivals"][0]["arrivals"] != 2
        or second["capture_rows"] is not False
        or second["memory_rows"]
        or second["event_rows"]
        or not second["instruction_trace"]
    ):
        raise AssertionError(f"arrival or trial-trace contract drifted: {first!r} {second!r}")
    native_fixture = FIXTURE_ROOT / "camry-8965F3307000" / (
        "camry_f33_scheduler_publication_native_ch1_single_request_returns.json"
    )
    native = json.loads(native_fixture.read_text(encoding="utf-8"))
    native_events = native.pop("events")
    native.update(
        name="campaign-real-foreground-arrival",
        max_instructions=30_000,
        stop_addresses=[],
        checks=[],
        steps=[
            {"kind": "checkpoint", "name": "prepared", "after_instructions": 1},
            {
                "kind": "trial", "name": "one-native-cycle",
                "max_instructions": 30_000, "stop_addresses": [],
                "stop_after_arrivals": [{"address": "0x66066", "count": 2}],
                "events": native_events, "checks": [],
            },
        ],
    )
    native.pop("expected_termination", None)
    native_path = output_dir / "real-foreground-arrival.json"
    native_path.write_text(json.dumps(native, indent=2) + "\n", encoding="utf-8")
    native_report = capture_many(
        "camry-8965F3307000", [native_path], output_dir,
    )[0]
    native_trial = native_report["checkpointing"]["trials"][0]
    if (
        native_trial["termination_reason"] != "stop-after-arrivals"
        or native_trial["final_pc"] != "0x00066066"
        or native_trial["stop_after_arrivals"][0]["arrivals"] != 2
    ):
        raise AssertionError(
            f"real foreground 0x660BC -> 0x66066 arrival drifted: {native_trial!r}",
        )

    completion = {
        "kind": "can-tx-complete", "buffer": 22,
        "after_instructions": 0,
        "evidence": "Synthetic completion without a firmware request",
    }
    strict = {
        **index,
        "name": "strict-unrequested-transmit-completion",
        "input_derived_table_indices": False,
        "events": [completion],
    }
    tolerated = {
        **strict,
        "name": "tolerated-unrequested-transmit-completion",
        "events": [{**completion, "tolerate_no_pending": True}],
    }
    tolerated_path = output_dir / "tolerated-completion.json"
    strict_path = output_dir / "strict-completion.json"
    tolerated_path.write_text(json.dumps(tolerated, indent=2) + "\n", encoding="utf-8")
    strict_path.write_text(json.dumps(strict, indent=2) + "\n", encoding="utf-8")
    tolerated_report, strict_report = capture_many(
        "camry-8965F3307000", [tolerated_path, strict_path], output_dir,
    )
    if not any(
        row["kind"] == "can-tx-complete-ignored" and row["buffer"] == 22
        for row in tolerated_report["device_events"]
    ):
        raise AssertionError("tolerated completion did not publish its ignored row")
    if not tolerated_report["passed"] or tolerated_report["termination_reason"] != "stop-address":
        raise AssertionError("tolerated completion did not let execution reach the stop address")
    if strict_report["passed"] or strict_report["termination_reason"] != "runner-error":
        raise AssertionError("strict unrequested completion no longer fails")

    reset = {
        "schema": "rh850-p1me-machine-scenario-v2",
        "name": "external-pin-reset-restarts-cpu",
        "entry": PORTABLE_STORE_SELECTOR,
        "max_instructions": 1,
        "stop_addresses": [],
        "expected_termination": "instruction-budget",
        "gpr_fill": "0",
        "registers": {"PSW": "0"},
        "memory": [
            {
                "address": "0xfebe0100", "hex": "a5",
                "evidence": "Local RAM before external pin reset",
            },
            {
                "address": "0xfeef8000", "hex": "5a",
                "evidence": "Global RAM before external pin reset",
            },
        ],
        "events": [{
            "kind": "reset-assert", "reset_class": "system-1-pin",
            "after_instructions": 0,
            "evidence": "External RESET pin assertion; R01UH0585EJ0120 Tables 8.1 and 8.2",
        }],
        "checks": [
            {
                "name": "local RAM cleared", "kind": "memory",
                "address": "0xfebe0100", "size": 1, "equals_hex": "00",
            },
            {
                "name": "global RAM cleared", "kind": "memory",
                "address": "0xfeef8000", "size": 1, "equals_hex": "00",
            },
            {
                "name": "pin and field-BIST reset factors", "kind": "memory",
                "address": "0xfff81000", "size": 4, "equals_hex": "02040000",
            },
        ],
    }
    reset_path = output_dir / "external-pin-reset.json"
    reset_path.write_text(json.dumps(reset, indent=2) + "\n", encoding="utf-8")
    reset_report = capture_many(
        "camry-8965F3307000", [reset_path], output_dir,
    )[0]
    reset_rows = [
        row for row in reset_report["device_events"] if row["kind"] == "reset-assert"
    ]
    if (
        not reset_report["passed"]
        or len(reset_rows) != 1
        or reset_rows[0]["reset_cause_value"] != "0x00000402"
        or not reset_rows[0]["changed_memory_ranges"]
    ):
        raise AssertionError(f"external pin reset contract drifted: {reset_report!r}")
    print(
        "PASS trial traces, compare operands, indexed accesses, arrival stops, "
        "tolerated completions, and external reset"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runtime-soak", action="store_true",
                        help="run only the explicit long-duration lifecycle bench")
    args = parser.parse_args()
    run([str(REPO_ROOT / "tools/rh850"), "model", "check"])
    with tempfile.TemporaryDirectory(prefix="verify-rh850-machine-", dir=REPO_ROOT / "build/tmp") as tmp:
        output_root = Path(tmp)
        if args.runtime_soak:
            check_runtime_soak(output_root)
            return 0
        check_drcov_text_grammar(output_root)
        check_scenario_source_contract(output_root)
        check_reset_replay_contract(output_root)
        check_fixture_schemas()
        check_slow_fixture_contracts()
        check_bridge_ready_contract(output_root)
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
        check_rscfd_transmit_results(output_root)
        check_campaign_machine_features(output_root)
    print("PASS specification-backed multi-target RH850/P1M-E machine")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
