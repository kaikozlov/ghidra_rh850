#!/usr/bin/env python3
"""Exercise Camry F33 nonvolatile write interruption boundaries."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from tools import REPO_ROOT
from tools.emulation.p1me_machine import capture_many

TARGET = "camry-8965F3307000"
FIXTURES = REPO_ROOT / "tests/fixtures/rh850/machine/camry-8965F3307000"
DEFAULT_OUTPUT = REPO_ROOT / "build/out/targets/camry-8965F3307000/nvm-lifecycle"
LIFECYCLE_SPECS: tuple[dict[str, Any], ...] = (
    {
        "schema": "camry-f33-nvm-lifecycle-v1",
        "name": "application-checkpoint-ring",
        "entry": "0x6853e",
        "physical_entries": ["0x762f2", "0x76334", "0x763a4", "0x779b2", "0x77a36"],
        "command_sequence": [
            {"operation": "erase", "commands": ["0x20", "0xd0"], "issue_instructions": [46, 73], "reset_after_instructions": [47, 74]},
            {"operation": "blank-check", "commands": ["0x71", "0xd0"], "issue_instructions": [52, 79], "reset_after_instructions": [53, 80]},
            {"operation": "program-word", "commands": ["0xe8", "0x02", "data-0", "data-1", "0xd0"], "issue_instructions": [40, 47, 67, 86, 126], "reset_after_instructions": [41, 48, 68, 87, 127]},
            {"operation": "readback-verify", "commands": [], "issue_instructions": [], "reset_after_instructions": []},
        ],
        "reader_scenarios": [
            "camry_f33_nvm_recovery_checkpoint_restore_bad_complement_keeps_prior.json",
            "camry_f33_nvm_recovery_checkpoint_restore_bad_complement_no_candidate.json",
            "camry_f33_nvm_recovery_checkpoint_restore_forward_generation.json",
        ],
        "invariant": "Accept the newest committed record whose generation complement and physical trailer validate; otherwise retain the prior valid ring record, or publish defaults when no valid candidate remains.",
    },
    {
        "schema": "camry-f33-nvm-lifecycle-v1",
        "name": "application-triplicate",
        "entry": "0x6869e",
        "physical_entries": ["0x762f2", "0x76334", "0x763a4", "0x779b2", "0x77a36"],
        "command_sequence": [
            {"operation": "erase", "commands": ["0x20", "0xd0"], "issue_instructions": [46, 73], "reset_after_instructions": [47, 74]},
            {"operation": "blank-check", "commands": ["0x71", "0xd0"], "issue_instructions": [52, 79], "reset_after_instructions": [53, 80]},
            {"operation": "program-word", "commands": ["0xe8", "0x02", "data-0", "data-1", "0xd0"], "issue_instructions": [40, 47, 67, 86, 126], "reset_after_instructions": [41, 48, 68, 87, 127]},
            {"operation": "readback-verify", "commands": [], "issue_instructions": [], "reset_after_instructions": []},
        ],
        "reader_scenarios": [
            "camry_f33_nvm_recovery_triplicate_restore_raw_55_pair.json",
            "camry_f33_nvm_recovery_triplicate_restore_raw_aa_pair.json",
            "camry_f33_nvm_recovery_triplicate_restore_three_way_conflict.json",
        ],
        "invariant": "Decode raw, XOR-0x55, and XOR-0xAA lanes and publish only a bytewise two-copy consensus; repair the dissenting lane, or publish the configured invalid/default result when no pair agrees.",
    },
    {
        "schema": "camry-f33-nvm-lifecycle-v1",
        "name": "bootloader-codeflash-erase",
        "entry": "0x41e0",
        "physical_entries": ["0x4428", "0x4332"],
        "command_sequence": [
            {"operation": "codeflash-erase", "commands": ["erase", "execute"], "issue_instructions": [], "reset_after_instructions": []},
            {"operation": "boot-verify", "commands": [], "issue_instructions": [], "reset_after_instructions": []},
        ],
        "reader_scenarios": [],
        "invariant": "After any interrupted erase, the reset boot path must reject application handoff unless both configured CodeFlash regions pass CRC and both marker words equal 0x5aa5a55a.",
        "model_limit": "The P1M-E machine has no mutable CodeFlash cells or CodeFlash FACI erase state, so no command issue count or reset injection can be executed.",
    },
    {
        "schema": "camry-f33-nvm-lifecycle-v1",
        "name": "bootloader-codeflash-program",
        "entry": "0x4188",
        "physical_entries": ["0x4276", "0x43be", "0x4402", "0x5a04", "0x5286"],
        "command_sequence": [
            {"operation": "codeflash-program", "commands": ["program", "execute"], "issue_instructions": [], "reset_after_instructions": []},
            {"operation": "crc-cmac-verify", "commands": [], "issue_instructions": [], "reset_after_instructions": []},
            {"operation": "validity-marker-program", "commands": ["program-5aa5a55a", "execute"], "issue_instructions": [], "reset_after_instructions": []},
        ],
        "reader_scenarios": [],
        "invariant": "An interrupted download remains non-bootable; only successful region verification followed by a completed 0x5aa5a55a marker program may make the reset boot path accept the region.",
        "model_limit": "The P1M-E machine has no mutable CodeFlash cells or CodeFlash FACI program state, so no command issue count or reset injection can be executed.",
    },
    {
        "schema": "camry-f33-nvm-lifecycle-v1",
        "name": "icus-key-provisioning",
        "entry": "0x96354",
        "physical_entries": ["0x8aa1e", "0x68e16", "0x6823c", "0x88936", "0x870a8", "0x86e62", "0x8704c", "0x8997a"],
        "command_sequence": [
            {"operation": "icus-command-8", "commands": ["M1", "M2", "M3", "ICUSCMD=8", "M4", "M5"], "issue_instructions": [], "reset_after_instructions": []},
        ],
        "reader_scenarios": [],
        "invariant": "A key update is committed only when ICU-S authenticates M1-M3, advances its protected counter, persists the selected slot, and returns M4-M5; reset must leave either the authorized old slot or the fully authorized new slot.",
        "model_limit": "The machine models scripted ICU-S responses, not authenticated command-8 protected-slot persistence, so no storage interruption point or warm/cold retention observation is available.",
    },
)
SIGNATURES = {
    0x6853E: "8007e11006d8db001bf02056ff00ecf7",
    0x6869E: "8007e11006d8db001bf0c3f221060caf",
    0x762F2: "8007e10007e020eeff0080ffa2190a30",
    0x76334: "8007e11007d820eeff0080ff60190ae0",
    0x763A4: "8a07e13006d807d020eeff0080ffee18",
    0x779B2: "8407611006e8dd0007d82106aaaaaaaa",
    0x77A36: "8207e13006e8dd003c06786bbffe80de",
    0x78E2A: "8407a1f007e008d808c800d282ca06c0",
    0x78EC6: "8007e13008e006d807d09c00bfff3eff",
    0x41E0: "8807e11006e007d8a40fa19201eae009",
    0x4188: "84076100a40fa19201eae009ba250340",
    0x4276: "06f0e40f9991e50d60900198410ac499",
    0x4428: "8207e1308036ffff80ffee2da4e7a192",
    0x4332: "8207e1102437819100e2bfff9ef16152",
    0x43BE: "8207e11006e006d802eadb00bfffdafe",
    0x4402: "40eebffe234e03003defd10ffdc760f9",
    0x5A04: "82072100a40f1793620aea075f0180ff",
    0x5286: "8207210021065aa5a55a630f0100043a",
}
COMMAND_TEMPLATES = {
    "erase": "original-faci-erase-before-deadline.json",
    "blank-check": "original-faci-blank-check-blank.json",
    "program-word": "original-faci-program-before-deadline.json",
}
RESET_CLASSES = ("power-on", "system-1-pin", "system-1-cvm", "system-2", "application-1")


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text())
    if not isinstance(value, dict):
        raise RuntimeError(f"{path}: object required")
    return value


def validate_firmware() -> None:
    image = (REPO_ROOT / "firmware/camry-8965F3307000/CodeFlash.bin").read_bytes()
    for address, expected in SIGNATURES.items():
        actual = image[address:address + 16].hex()
        if actual != expected:
            raise RuntimeError(f"CodeFlash signature mismatch at 0x{address:x}: {actual}")


def load_specs() -> list[dict[str, Any]]:
    specs = list(LIFECYCLE_SPECS)
    for spec in specs:
        if spec.get("schema") != "camry-f33-nvm-lifecycle-v1":
            raise RuntimeError(f"{spec.get('name')}: invalid lifecycle schema")
        for address in (spec["entry"], *spec["physical_entries"]):
            numeric = int(address, 0)
            if numeric not in SIGNATURES and spec["name"] != "icus-key-provisioning":
                raise RuntimeError(f"{spec['name']}: unpinned function {address}")
    return specs


def reset_scenario(source: dict[str, Any], name: str, instruction: int) -> dict[str, Any]:
    scenario = dict(source)
    scenario["name"] = name
    scenario["max_instructions"] = max(400, instruction + 256)
    scenario["checks"] = []
    scenario.pop("expected_termination", None)
    scenario["expected_fault"] = {
        "kind": "missing-reset-input",
        "address": "0xffd60010",
        "access": "read",
    }
    scenario["events"] = [{
        "kind": "reset-assert",
        "after_instructions": instruction,
        "reset_class": "system-1-pin",
        "evidence": "D7 external RESET-pin injection immediately after a native FACI issue",
    }]
    return scenario


def write_generated(path: Path, scenario: dict[str, Any]) -> Path:
    path.write_text(json.dumps(scenario, indent=2) + "\n")
    return path


def command_trials(specs: list[dict[str, Any]], generated: Path) -> tuple[list[Path], dict[str, dict[str, Any]]]:
    paths: list[Path] = []
    metadata: dict[str, dict[str, Any]] = {}
    for spec in specs[:2]:
        for operation in spec["command_sequence"]:
            kind = operation["operation"]
            template_name = COMMAND_TEMPLATES.get(kind)
            if template_name is None:
                continue
            source = load_json(FIXTURES / template_name)
            issues = operation["issue_instructions"]
            resets = operation["reset_after_instructions"]
            if len(issues) != len(resets):
                raise RuntimeError(f"{spec['name']} {kind}: issue/reset count mismatch")
            for index, (issue, reset) in enumerate(zip(issues, resets, strict=True)):
                name = f"d7_{spec['name'].replace('-', '_')}_{kind.replace('-', '_')}_{index}"
                path = generated / f"{name}.json"
                paths.append(write_generated(path, reset_scenario(source, name, int(reset))))
                metadata[name] = {
                    "path": spec["name"],
                    "operation": kind,
                    "injection_point": operation["commands"][index],
                    "issue_instruction": int(issue),
                    "reset_instruction": int(reset),
                    "expected_ticks": [int(value) for value in issues[:index + 1]],
                }
    return paths, metadata


def reader_paths(specs: list[dict[str, Any]]) -> list[Path]:
    return [FIXTURES / name for spec in specs[:2] for name in spec["reader_scenarios"]]


def reset_class_trials(generated: Path) -> tuple[list[Path], dict[str, str]]:
    paths: list[Path] = []
    classes: dict[str, str] = {}
    for reset_class in RESET_CLASSES:
        source_name = (
            "original-faci-application-reset-retains-erase.json"
            if reset_class == "application-1"
            else "original-faci-reset-cancels-erase.json"
        )
        scenario = load_json(FIXTURES / source_name)
        name = f"d7_reset_class_{reset_class.replace('-', '_')}"
        scenario["name"] = name
        for event in scenario["events"]:
            if event["kind"] == "peripheral-reset":
                event["reset_class"] = reset_class
        path = generated / f"{name}.json"
        paths.append(write_generated(path, scenario))
        classes[name] = reset_class
    return paths, classes


def faci_events(result: dict[str, Any]) -> list[dict[str, Any]]:
    return [event for event in result["device_events"] if event.get("kind") == "faci-command"]


def run(output: Path) -> dict[str, Any]:
    validate_firmware()
    specs = load_specs()
    generated = output / "generated"
    generated.mkdir(parents=True, exist_ok=True)
    command_paths, metadata = command_trials(specs, generated)
    class_paths, class_names = reset_class_trials(generated)
    scenarios = [*command_paths, *reader_paths(specs), *class_paths]
    results = capture_many(TARGET, scenarios, output / "machine")
    by_name = {result["scenario"]: result for result in results}
    failures = [result["scenario"] for result in results if not result["passed"]]
    if failures:
        raise RuntimeError("machine scenario failures: " + ", ".join(failures))

    rows: list[dict[str, Any]] = []
    for name, item in metadata.items():
        result = by_name[name]
        ticks = [int(event["scheduler_tick"]) for event in faci_events(result)]
        if ticks != item["expected_ticks"]:
            raise RuntimeError(f"{name}: FACI ticks {ticks}, expected {item['expected_ticks']}")
        cancelled = any(event.get("kind") == "faci-reset-cancelled" for event in result["device_events"])
        if not cancelled:
            raise RuntimeError(f"{name}: RESET pin did not cancel the pending FACI command")
        operation = item["operation"]
        retained = "old" if operation == "blank-check" else "indeterminate"
        rows.append({
            **item,
            "reset_class": "system-1-pin",
            "retained": retained,
            "property": "model-limit" if retained == "indeterminate" else "held",
            "faci_cancelled": cancelled,
        })

    reset_rows: list[dict[str, Any]] = []
    for name, reset_class in class_names.items():
        result = by_name[name]
        completed = sum(event.get("kind") == "faci-completion" for event in result["device_events"])
        cancelled = sum(event.get("kind") == "faci-reset-cancelled" for event in result["device_events"])
        retained = "erased-new" if reset_class == "application-1" else "indeterminate"
        expected = (completed, cancelled) == ((1, 0) if reset_class == "application-1" else (0, 1))
        if not expected:
            raise RuntimeError(f"{name}: completion={completed} cancellation={cancelled}")
        reset_rows.append({
            "reset_class": reset_class,
            "ram": "generated reset rules",
            "flash": retained,
            "pending_faci": "retained" if reset_class == "application-1" else "cancelled",
        })

    reader_results = [
        {"scenario": path.stem, "property": "held", "termination": by_name[path.stem]["termination_reason"]}
        for path in reader_paths(specs)
    ]
    report = {
        "schema": "camry-f33-nvm-lifecycle-result-v1",
        "target": TARGET,
        "paths": [{
            "name": spec["name"],
            "entry": spec["entry"],
            "physical_entries": spec["physical_entries"],
            "command_sequence": spec["command_sequence"],
            "invariant": spec["invariant"],
            "model_limit": spec.get("model_limit"),
        } for spec in specs],
        "injection_results": rows,
        "reader_results": reader_results,
        "reset_retention": reset_rows,
        "machine_semantics": "DataFlash erase/program mutates no bytes at issue; a cancelling reset before completion marks the target cells indeterminate, while Application Reset 1 retains the operation to completion.",
        "model_requirements": [
            "CodeFlash FACI needs mutable physical cells, command issue/completion events, reset cancellation, indeterminate interrupted cells, and post-reset CRC/marker readback for boot routines 0x4332, 0x43be, and 0x4402.",
            "DataFlash indeterminate-cell reads need the target's ECC/media-error result path so firmware restore can reject the damaged record instead of terminating as an uninitialized read.",
            "ICU-S command 8 needs authenticated M1-M3 handling, protected counter/slot persistence, reset interruption, and M4-M5 completion state.",
        ],
    }
    output.mkdir(parents=True, exist_ok=True)
    (output / "result.json").write_text(json.dumps(report, indent=2) + "\n")
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    report = run(args.output.resolve())
    print(f"{len(report['injection_results'])} FACI reset boundaries; {len(report['reader_results'])} reader invariants; {len(report['reset_retention'])} reset classes")
    print(args.output.resolve() / "result.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
