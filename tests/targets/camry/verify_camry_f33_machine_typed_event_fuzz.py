#!/usr/bin/env python3
"""Verify the deterministic Camry P1M-E typed-event fuzz campaign."""
from __future__ import annotations

import json
import random
import shutil

from tools import REPO_ROOT
from tools.targets.camry.research import fuzz_camry_f33_machine_typed_events as fuzz


def verify_single_stream_mutation() -> None:
    base = fuzz.representative_lifecycle_cases()[0]
    for serial, source in enumerate(fuzz.SOURCES):
        mutated = fuzz.mutate(
            base, source, random.Random(1000 + serial), serial,
            fuzz.dictionary_tokens(),
        )
        changed = [
            before.source
            for before, after in zip(base.streams, mutated.streams, strict=True)
            if before != after
        ]
        assert changed == [source]
        assert mutated.case_id != base.case_id


def verify_grammar() -> None:
    requests = (
        b"\x10\x03",
        b"\x22\xf1\x81",
        b"\x31\x01\x10\x0f",
        b"\x27\x04" + bytes(range(16)),
    )
    for payload in requests:
        event = fuzz.uds_event(payload)
        assert fuzz.validate_iso_tp_event(event) == (True, "well-formed")
        frames = fuzz.iso_tp_frames(payload)
        assert all(len(frame) == 8 for frame in frames)
    broken = fuzz.uds_event(b"\x31\x01\x10\x0f", break_kind="declared-length")
    assert fuzz.validate_iso_tp_event(broken) == (False, "declared-length")


def verify_timer_schedule() -> None:
    for case in fuzz.representative_lifecycle_cases():
        for event in case.stream(fuzz.TIMER_SOURCE).events:
            assert (
                event.values()["p_bus_cycles"]
                == fuzz.TAUJ0_TIMER_SKEW_P_BUS_CYCLES
            )
    base = next(
        case for case in fuzz.representative_lifecycle_cases()
        if not case.stream(fuzz.TIMER_SOURCE).events
    )
    mutated = fuzz.mutate(
        base, fuzz.TIMER_SOURCE, random.Random(20261127), 0,
        fuzz.dictionary_tokens(),
    )
    timer_event, = mutated.stream(fuzz.TIMER_SOURCE).events
    assert (
        timer_event.values()["p_bus_cycles"]
        == fuzz.TAUJ0_TIMER_SKEW_P_BUS_CYCLES
    )

    invalid = fuzz.MachineCase(
        "invalid_bulk_timer_event",
        fuzz.canonical_streams({
            fuzz.TIMER_SOURCE: (
                fuzz.TypedEvent.make(
                    "timer-ticks", 0,
                    p_bus_cycles=2 * fuzz.TAUJ0_TIMER_SKEW_P_BUS_CYCLES,
                ),
            ),
        }),
    )
    try:
        fuzz.machine_events(invalid)
    except ValueError as error:
        assert "bulk clock jumps" in str(error)
    else:
        raise AssertionError("bulk timer event was accepted")


def verify_campaign() -> None:
    out = REPO_ROOT / "build/out/targets/camry-8965F3307000/typed-event-fuzz-check"
    shutil.rmtree(out, ignore_errors=True)
    summary = fuzz.campaign(out, seed=424242, budget=10, batch_size=10)
    usage = summary["stream_usage"]
    assert sum(row.get("inputs_executed", 0) for row in usage.values()) == summary["executions"]
    executed_ids = {row["id"] for row in summary["executed_inputs"]}
    assert sum(row.get("inputs_mutated", 0) for row in usage.values()) == summary["mutation_executions"]
    assert summary["mutation_executions"] >= len(fuzz.SOURCES)
    assert set(summary["retained_case_ids"]) <= executed_ids
    assert all(row.get("inputs_mutated", 0) == 1 for row in usage.values())
    assert all("retained_offspring" in row for row in usage.values())
    assert summary["checkpointing"]["trial_executions"] == summary["executions"]
    assert summary["checkpointing"]["coverage_replay_executions"] == 0
    screened_faults = sum(
        bool(not row["checkpoint_trace"] and row["fault_kind"] and row["fault_address"])
        for row in summary["executed_inputs"]
    )
    assert (
        summary["checkpointing"]["checkpoint_trace_executions"] + screened_faults
        == summary["executions"]
    )
    assert summary["checkpointing"]["mean_trial_instructions_per_second"] > 0
    assert any(row["restore_nanoseconds"] > 0 for row in summary["executed_inputs"])
    for row in summary["executed_inputs"]:
        for well_formed, reason in zip(
            row["well_formed_requests"], row["request_validation"], strict=True,
        ):
            assert well_formed or reason in {"declared-length", "sequence"}
        if (
            row["termination"] in {"stop-address", "stop-after-arrivals"}
            and row["well_formed_requests"]
            and all(row["well_formed_requests"])
        ):
            assert row["receive_path_accepted"]
        assert row["termination"] != "runner-error"
        if row["termination"] in {"stop-address", "stop-after-arrivals"}:
            assert row["fault_kind"] is None and row["fault_address"] is None
        else:
            assert row["termination"] == "unexpected-fault"
            assert row["fault_kind"] and row["fault_address"]
        result_path = out / "results" / f"{row['id']}.json"
        payload = json.loads(result_path.read_text())
        assert payload["case_id"] == row["id"]
        assert payload["report"]["termination_reason"] == row["termination"]
        if row["fault_kind"]:
            assert payload["report"]["fault"]["kind"] == row["fault_kind"]
            assert payload["report"]["fault"]["address"] == row["fault_address"]
    timer_rows = [
        row for row in summary["executed_inputs"]
        if row["mutated_source"] == fuzz.TIMER_SOURCE
    ]
    assert timer_rows
    assert all(
        row["fault_kind"] != "unsupported-csih-operation"
        for row in timer_rows
    )
    segmented_results = fuzz.run_cases(
        fuzz.segmented_wdbi_rejection_cases(),
        out / "segmented-wdbi-rejections",
        batch_size=8,
    )
    for _case, report, feedback in segmented_results:
        assert 0x95978 in feedback.reached_pcs
        assert 0x95734 in feedback.reached_pcs
        assert 0x95674 not in feedback.reached_pcs
        assert report.get("fault") is None
        response_check = next(
            row for row in report["checks"]
            if row["name"] == "Completed UDS response"
        )
        assert response_check["passed"]
        assert response_check["actual"] == "2e13"
    assert (out / "summary.json").is_file()
    assert summary["edge_count"] > 0
    assert summary["retained_corpus_size"] > 0
    assert summary["substitution_dictionary"]["compare_operand_rows"] > 0
    assert summary["substitution_dictionary"]["table_index_rows"] > 0
    benchmark = summary["compare_benchmark"]
    assert benchmark["target_reached_in_machine_run"]
    assert (
        benchmark["with_compare_dictionary_executions"]
        < benchmark["without_compare_dictionary_executions"]
    )
    print(
        f"typed-event campaign: executions={summary['executions']} "
        f"edges={summary['edge_count']} retained={summary['retained_corpus_size']}"
    )



def verify_e2_shapes() -> None:
    flood, forced = fuzz.e2_cases(seed=20261124, window=4)
    assert all(len(flood.stream(source).events) == 4 for source in fuzz.SOURCES)
    flood_scenario = fuzz.scenario(flood)
    events = flood_scenario["events"]
    assert sum(row["kind"] == "can-rx" for row in events) == 4
    assert sum(row["kind"] == "clock" for row in events) == 4
    assert sum(row["kind"] == "interrupt" for row in events) == 4
    completions = [row for row in events if row["kind"] == "can-tx-complete"]
    assert len(completions) == 4
    assert all(row["tolerate_no_pending"] for row in completions)
    assert len(forced.stream(fuzz.CAN_SOURCE).events) == 3


def verify_case_result_resume() -> None:
    out = REPO_ROOT / "build/tmp/camry-f33-machine-typed-event-resume"
    shutil.rmtree(out, ignore_errors=True)
    case = fuzz.representative_lifecycle_cases()[0]
    result = fuzz.Feedback(
        frozenset({(0x100, 0x104)}),
        frozenset({"can-rx-pop"}),
        (b"\x10\x0f",),
        (3,),
        frozenset({0x100, 0x104}),
    )
    report = {"termination_reason": "stop-address", "passed": True}
    path = fuzz.case_result_path(out, case)
    fuzz.persist_case_result(path, case, report, result)
    assert fuzz.load_case_result(path, case) == (report, result)
    path.write_text("{")
    assert fuzz.load_case_result(path, case) is None
    shutil.rmtree(out)


def verify_deferred_trace_shape() -> None:
    case = fuzz.representative_lifecycle_cases()[0]
    scenario = fuzz.checkpoint_scenario([case])
    assert scenario["instruction_trace_start_step"] == "normal-operation"
    named = [
        step for step in scenario["steps"]
        if step.get("name") == "normal-operation"
    ]
    assert len(named) == 1
    assert named[0]["kind"] == "checkpoint"


def main() -> int:
    verify_single_stream_mutation()
    verify_grammar()
    verify_timer_schedule()
    verify_campaign()
    verify_e2_shapes()
    verify_case_result_resume()
    verify_deferred_trace_shape()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
