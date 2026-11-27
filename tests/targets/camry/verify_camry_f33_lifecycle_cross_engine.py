#!/usr/bin/env python3
"""Check deterministic lifecycle selection and checkpoint divergence reporting."""
from __future__ import annotations

from tools.targets.camry.research import compare_camry_f33_lifecycle_engines as cross
from tools.targets.camry.research import fuzz_camry_f33_stateful_coverage as stateful


def main() -> int:
    selected = cross.selected_cases()
    rows = cross.checkpoints(selected)
    assert len(selected) == 338
    assert len(rows) == 392
    assert sum(case.name.startswith("truncated_") for case in selected) == 20
    for excluded_lo, excluded_hi, _reason in cross.DIRECT_ONLY_RANGES:
        assert all(
            hi < excluded_lo or excluded_hi < lo
            for lo, hi in cross.STATE_RANGES
        )

    segmented_case = stateful.make_case(
        "seeded_segmented", [stateful.request(b"\x22\xF1\x89" + bytes(range(40)))],
    )
    segmented = cross.Checkpoint(
        segmented_case.name, segmented_case.case_id, "seed", "reproduced", 1, "request",
        segmented_case,
    )
    segmented_scenario = cross.ready_machine_scenario(segmented, {})
    names = [step.get("name") for step in segmented_scenario["steps"]]
    ingress = [name for name in names if name and "receive-" in name]
    assert len(ingress) == 7
    assert names.index("period-00000-flow-control-completion") == names.index(ingress[0]) + 1
    assert names.index("period-00000-processing-return-to-wait") == names.index(ingress[-1]) + 1
    assert names.index("period-00000-native-cycle") == names.index(ingress[-1]) + 2
    for name in (ingress[0], ingress[-1]):
        step = next(step for step in segmented_scenario["steps"] if step.get("name") == name)
        assert step["stop_after_arrivals"] == []
        assert "0x660bc" in step["stop_addresses"]
    middle = next(step for step in segmented_scenario["steps"] if step.get("name") == ingress[1])
    assert middle["stop_after_arrivals"] == [{"address": "0x66066", "count": 2}]
    completions = next(
        step for step in segmented_scenario["steps"]
        if step.get("name") == "period-00000-transmit-completions"
    )
    assert [row["kind"] for row in completions["events"]] == ["can-tx-complete"]


    case = stateful.make_case("seeded_divergence", [stateful.request(b"\x10\x01")])
    first = cross.Checkpoint(
        case.name, case.case_id, "seed", "reproduced", 1, "request", case,
    )
    second_case = stateful.make_case(
        "seeded_divergence_second",
        [stateful.request(b"\x10\x01"), stateful.action("poll")],
    )
    second = cross.Checkpoint(
        second_case.name, second_case.case_id, "poll", "reproduced", 2, "poll", second_case,
    )
    common = {"0xFEBE5954": "01020304"}
    changed = {"0xFEBE5954": "0102ff04"}
    gnu = {case.case_id: common, second_case.case_id: common}
    native = {case.case_id: common, second_case.case_id: common}
    machine = {case.case_id: common, second_case.case_id: changed}
    batch = cross.ready_machine_batch([first, second], gnu, "seeded_batch")
    assert batch["steps"][cross.capture_replay.REPLAY_PREFIX_STEPS - 1] == {
        "kind": "checkpoint", "name": "normal-operation",
    }
    assert sum(step["kind"] == "restore" for step in batch["steps"]) == 2
    assert all(
        step["capture_rows"] is False
        for step in batch["steps"] if step["kind"] == "trial"
    )
    report = cross.build_report(
        [first, second], gnu, native, machine,
        {"gnu": [], "native": [], "machine": []},
        {"returncode": 0},
    )
    assert report["summary"] == {
        "cases": 2, "checkpoints": 2, "equal": 1, "foreground_only": 0, "diverged": 1,
        "unavailable": 0,
    }
    divergence = report["results"][1]
    assert not divergence["equal"]
    assert divergence["gnu_vs_machine"]["first_difference"] == {
        "address": "0xFEBE5956", "left": "0304", "right": "ff04",
    }
    assert divergence["checkpoint"] == 2
    assert divergence["diagnosis"] == (
        "contract state differs at app_dcm_security_bitmap+0x2"
    )
    assert divergence["gnu_vs_machine"]["groups"] == {
        "foreground-cycle": [], "contract": ["app_dcm_security_bitmap+0x2"],
    }
    unavailable = cross.build_report(
        [first], {case.case_id: common}, {case.case_id: common}, {},
        {"gnu": [], "native": [], "machine": [{
            "id": case.case_id,
            "detail": "firmware entered boot transfer before request service",
        }]},
        {"returncode": 0},
    )
    assert unavailable["summary"] == {
        "cases": 1, "checkpoints": 1, "equal": 0, "foreground_only": 0, "diverged": 0,
        "unavailable": 1,
    }

    parsed = cross.states_from_machine_batch({
        "checkpointing": {"trials": [{
            "name": f"{case.case_id}::period-00000-native-cycle",
            "checks": [{
                "kind": "memory",
                "name": f"{case.case_id}::state-0xFEBE5954",
                "actual": "01020304",
            }],
        }, {
            "name": f"{second_case.case_id}::period-00000-native-cycle",
            "checks": [{
                "kind": "memory",
                "name": f"{second_case.case_id}::state-0xFEBE5954",
                "actual": "0102ff04",
            }],
        }]},
    })
    assert parsed == {
        case.case_id: common,
        second_case.case_id: changed,
    }
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
