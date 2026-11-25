#!/usr/bin/env python3
"""Compare replaying a scenario prefix with restoring its checkpoint."""
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

from tools.emulation.p1me_machine import P1MEMachineError, run


def _require_equivalent_trials(straight: dict, restored: dict) -> None:
    if not (straight["passed"] and restored["passed"]):
        raise P1MEMachineError("both benchmark trials must pass")
    if straight["instruction_count"] == 0:
        raise P1MEMachineError("benchmark trial retired no instructions")
    for field in (
        "start_instruction", "instruction_count", "termination_reason", "final_pc",
        "register_rows", "checks", "memory_rows", "event_rows", "compare_operands",
        "input_derived_table_indices",
    ):
        if straight[field] != restored[field]:
            raise P1MEMachineError(f"checkpoint replay mismatch: {field}")
    for field in ("halt", "instruction_trace"):
        if straight.get(field) != restored.get(field):
            raise P1MEMachineError(f"checkpoint replay mismatch: {field}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("target")
    parser.add_argument("scenario", type=Path)
    parser.add_argument("--checkpoint-after", type=int, required=True)
    parser.add_argument("--trial-instructions", type=int, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.checkpoint_after < 0 or args.trial_instructions <= 0:
        parser.error("checkpoint and trial instruction counts must be nonnegative/positive")

    scenario_path = args.scenario.resolve()
    scenario = json.loads(scenario_path.read_text(encoding="utf-8"))
    if scenario.get("steps"):
        parser.error("benchmark source scenario already has steps")
    trial = {
        "max_instructions": args.trial_instructions,
        "stop_addresses": scenario["stop_addresses"],
        "events": [],
        "checks": scenario["checks"],
    }
    scenario["name"] = f"{scenario['name']}-checkpoint-benchmark"
    scenario["max_instructions"] = max(
        scenario["max_instructions"],
        args.checkpoint_after + args.trial_instructions,
    )
    scenario["steps"] = [
        {
            "kind": "checkpoint",
            "name": "benchmark-prefix",
            "after_instructions": args.checkpoint_after,
        },
        {"kind": "trial", "name": "straight", **trial},
        {"kind": "restore", "checkpoint": "benchmark-prefix"},
        {"kind": "trial", "name": "restored", **trial},
    ]

    output = args.output.resolve()
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", prefix="checkpoint-benchmark-",
            dir=scenario_path.parent, encoding="utf-8",
        ) as stream:
            json.dump(scenario, stream, indent=2)
            stream.write("\n")
            stream.flush()
            report = run(args.target, Path(stream.name), output)
        checkpoint = report["checkpointing"]["checkpoints"][0]
        straight, restored = report["checkpointing"]["trials"]
        _require_equivalent_trials(straight, restored)
    except (OSError, json.JSONDecodeError, KeyError, P1MEMachineError) as exc:
        parser.error(str(exc))

    replay_ns = checkpoint["prefix_nanoseconds"] + straight["execution_nanoseconds"]
    checkpoint_ns = restored["restore_nanoseconds"] + restored["execution_nanoseconds"]
    result = {
        "scenario": str(args.scenario),
        "checkpoint_after": args.checkpoint_after,
        "trial_instructions": restored["instruction_count"],
        "checkpoint_capture_nanoseconds": checkpoint["capture_nanoseconds"],
        "checkpoint_memory_pages": checkpoint["memory_pages"],
        "checkpoint_memory_page_bytes": checkpoint["memory_page_bytes"],
        "initialized_bytes": checkpoint["initialized_bytes"],
        "restore_nanoseconds": restored["restore_nanoseconds"],
        "trial_nanoseconds": restored["execution_nanoseconds"],
        "instructions_per_second": restored["instructions_per_second"],
        "prefix_replay_and_trial_nanoseconds": replay_ns,
        "restore_and_trial_nanoseconds": checkpoint_ns,
        "prefix_replay_to_restore_ratio": replay_ns / checkpoint_ns,
        "report": str(output),
    }
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
