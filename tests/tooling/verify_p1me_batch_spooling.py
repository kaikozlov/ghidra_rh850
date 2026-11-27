#!/usr/bin/env python3
"""Check batch report isolation and compact trace spooling."""
from __future__ import annotations

import json
import struct
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from tools.emulation.p1me_machine import (
    P1MEMachineError,
    capture_many,
    load_scenario,
)

TARGET = "camry-8965F3307000"


def normalized(report: dict[str, object]) -> dict[str, object]:
    return {key: value for key, value in report.items() if key != "report_path"}


def main() -> None:
    calls: list[list[Path]] = []

    def fake_execute(
        target_name: str,
        scenario_paths: list[Path],
        *,
        instruction_trace: bool = False,
        report_outputs: list[dict[str, str]] | None = None,
    ) -> dict[str, object]:
        assert target_name == TARGET
        assert report_outputs is not None
        assert len(report_outputs) == len(scenario_paths)
        assert len({row["report"] for row in report_outputs}) == len(report_outputs)
        calls.append(list(scenario_paths))
        verdicts = []
        for scenario_path, output in zip(scenario_paths, report_outputs, strict=True):
            scenario = json.loads(scenario_path.read_text())
            report = {
                "schema": "rh850-p1me-machine-report-v2",
                "scenario": scenario["name"],
                "passed": True,
                "termination_reason": "instruction-budget",
                "checks": [],
            }
            report_path = Path(output["report"])
            report_path.parent.mkdir(parents=True, exist_ok=True)
            if instruction_trace:
                report["drcov_path"] = output["drcov_path"]
                Path(output["instruction_spool"]).write_bytes(struct.pack(">IB", 0, 2))
            report_path.write_text(json.dumps(report) + "\n")
            verdicts.append({"passed": True})
        return {
            "schema": "rh850-p1me-machine-report-manifest-v1",
            "reports": verdicts,
            "passed": True,
        }

    with TemporaryDirectory(prefix="p1me-spool-check-") as temp:
        root = Path(temp)
        loader_scenario = {
            "schema": "rh850-p1me-machine-scenario-v2",
            "name": "deferred-instruction-trace-loader",
            "entry": {
                "role": "loader-test",
                "scope": "resolved-address",
                "address": "0x0",
            },
            "max_instructions": 2,
            "stop_addresses": [],
            "checks": [],
            "steps": [
                {
                    "kind": "checkpoint",
                    "name": "readiness",
                    "after_instructions": 1,
                },
                {
                    "kind": "trial",
                    "name": "campaign",
                    "max_instructions": 1,
                    "stop_addresses": [],
                    "events": [],
                    "checks": [],
                },
            ],
            "instruction_trace_start_step": "readiness",
        }
        loader_path = root / "deferred-trace.json"
        loader_path.write_text(json.dumps(loader_scenario), encoding="utf-8")
        loaded = load_scenario(loader_path)
        assert loaded["instruction_trace_start_step"] == "readiness"

        loader_scenario["instruction_trace_start_step"] = "missing"
        loader_path.write_text(json.dumps(loader_scenario), encoding="utf-8")
        try:
            load_scenario(loader_path)
        except P1MEMachineError as exc:
            assert "must name exactly one checkpoint or trial step" in str(exc)
        else:
            raise AssertionError("unknown instruction_trace_start_step was accepted")
        scenarios = []
        for index in range(3):
            path = root / f"trial-{index}.json"
            path.write_text(json.dumps({"name": path.stem}))
            scenarios.append(path)

        with patch("tools.emulation.p1me_machine._execute", side_effect=fake_execute):
            batch = capture_many(TARGET, scenarios, root / "batch")
            singles = [capture_many(TARGET, [path], root / f"single-{index}")[0]
                       for index, path in enumerate(scenarios)]
            traced = capture_many(
                TARGET, [scenarios[0]], root / "trace", instruction_trace=True,
            )[0]

        assert [normalized(report) for report in batch] == [
            normalized(report) for report in singles
        ]
        assert all(Path(report["report_path"]).is_file() for report in batch)
        assert Path(traced["drcov_path"]).is_file()
        assert not (root / "trace/.trial-0.instructions.bin").exists()
        assert [len(call) for call in calls] == [3, 1, 1, 1, 1]

    print("PASS batch and serial reports match; compact instruction spool consumed")


if __name__ == "__main__":
    main()
