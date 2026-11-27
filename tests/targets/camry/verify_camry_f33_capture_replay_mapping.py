#!/usr/bin/env python3
"""Verify retained-capture period mapping and mutation-free replay construction."""
from __future__ import annotations
import json
from tempfile import TemporaryDirectory
from pathlib import Path

from tools import REPO_ROOT
from tools.targets.camry.research import replay_camry_f33_capture_machine as replay
from tools.emulation.p1me_can_bridge import write_bridge_scenario
from tools.emulation.p1me_machine import load_scenario

FIXTURE = REPO_ROOT / "tests/fixtures/targets/camry/capture_replay_mapping.scenario.json"


def main() -> int:
    converted = replay.load_capture_scenario(FIXTURE)
    periods = replay.capture_periods(converted)
    assert [period.index for period in periods] == [0, 1, 2]
    assert [row["evidence"] for row in periods[0].receive] == [
        "fixture frame 0", "fixture frame 2",
    ]
    assert [row["evidence"] for row in periods[0].completions] == ["fixture frame 1"]
    assert periods[1].receive == () and periods[1].completions == ()
    assert [row["evidence"] for row in periods[2].receive] == ["fixture frame 4"]
    assert [row["evidence"] for row in periods[2].completions] == ["fixture frame 3"]

    proof = replay.acceptance_probe_periods(periods)
    proof_rows = [row for period in proof for row in period.receive]
    assert len(proof) == 200
    assert len(proof_rows) == 3
    assert {
        (row["can_id"], len(bytes.fromhex(row["data_hex"])))
        for row in proof_rows
    } == {("0x115", 8), ("0x127", 8), ("0x3BF", 8)}
    assert all(not period.completions for period in proof)

    scenario = replay.build_replay_scenario(
        converted["source"], periods, "mapping_check",
    )
    assert scenario["source"]["sha256"] == converted["source"]["sha256"]
    assert scenario["source"]["board_fixture"].endswith(
        "original-reset-to-runtime-synthetic-board.json"
    )
    assert scenario["reset"] == "power-on"
    assert scenario["entry"]["address"] == "0x0"
    assert scenario["steps"][0] == {
        "kind": "checkpoint", "name": "cold-start", "after_instructions": 0,
    }
    assert scenario["steps"][1]["name"] == "ordinary-power-on-to-foreground"
    assert scenario["steps"][1]["max_instructions"] == 35_000_000
    settle = scenario["steps"][2]
    assert settle["name"] == "settle-pending-serial-completions"
    assert settle["stop_after_arrivals"] == [{"address": "0x66066", "count": 65}]
    bootstrap = scenario["steps"][3:5]
    assert [row["name"] for row in bootstrap] == [
        "bootstrap-native-cycle", "bootstrap-return-to-wait",
    ]
    assert bootstrap[0]["stop_addresses"][-1] == "0x660bc"
    assert bootstrap[1]["stop_after_arrivals"] == [
        {"address": "0x66066", "count": 1},
    ]
    assert scenario["steps"][replay.REPLAY_PREFIX_STEPS - 1] == {
        "kind": "checkpoint",
        "name": "normal-operation",
    }
    trials = [row for row in scenario["steps"] if row["kind"] == "trial"]
    assert len(trials) == replay.REPLAY_PREFIX_TRIALS + 12
    by_name = {row["name"]: row for row in trials}
    boot = by_name["ordinary-power-on-to-foreground"]
    assert boot["events"] == []
    assert boot["stop_after_arrivals"] == [{"address": "0x66066", "count": 2}]
    assert [row["address"] for row in bootstrap[1]["checks"]] == [
        "0xfebee8cc", "0xfebe8c06",
        "0xfebe5091", "0xfebe5096", "0xfebe509b", "0xfebe5624",
        "0xffd2008c",
    ]
    assert by_name["period-00000-receive-000-ingress"]["events"][0]["data_hex"] == (
        "0001020304050607"
    )
    assert by_name["period-00000-receive-001-ingress"]["events"][0]["data_hex"] == (
        "1011121314151617"
    )
    native = by_name["period-00000-native-cycle"]
    assert native["events"] == []
    assert native["stop_addresses"] == ["0x65f5e", "0x619be", "0x660bc"]
    returned = by_name["period-00000-return-to-wait"]
    assert returned["events"] == []
    assert returned["stop_after_arrivals"] == [{"address": "0x66066", "count": 1}]
    completion = by_name["period-00000-transmit-completions"]
    assert completion["events"][0]["evidence"] == "fixture frame 1"
    assert completion["events"][0]["tolerate_no_pending"] is True
    assert by_name["period-00001-transmit-completions"]["events"] == ()
    assert by_name["period-00002-receive-000-ingress"]["events"][0]["evidence"] == (
        "fixture frame 4"
    )
    assert by_name["period-00002-transmit-completions"]["events"][0]["evidence"] == (
        "fixture frame 3"
    )
    serial = [
        row for row in scenario["events"]
        if row["kind"] == "csih-word" and row["unit"] == 1
    ]
    assert [row["value"] for row in serial[:4]] == ["0x6400", "0x1", "0xf000", "0x38"]
    assert [row["after_transmit_words"] for row in serial[:4]] == [1, 2, 3, 4]
    assert len(serial) == 260
    assert serial[-1]["after_transmit_words"] == 1028
    assert all(row["delay_instructions"] == 128 for row in serial)
    assert all(
        "single-field replay mutation" not in str(row.get("evidence", ""))
        for trial in trials for row in trial["events"]
    )
    repeated_periods = (
        periods[0],
        periods[1],
        replay.CapturePeriod(2, (periods[0].receive[0],), ()),
    )
    mutation = replay.FieldMutation(
        0x115, "B0", ((0, 0xFF),), (), period_index=0, receive_index=0,
    )
    mutated = replay.build_replay_scenario(
        converted["source"], repeated_periods, "single_frame_mutation",
        mutations=(mutation,),
    )
    mutated_trials = {
        row["name"]: row for row in mutated["steps"] if row["kind"] == "trial"
    }
    assert (
        mutated_trials["period-00000-receive-000-ingress"]["events"][0]["data_hex"]
        == "ff01020304050607"
    )
    assert (
        mutated_trials["period-00002-receive-000-ingress"]["events"][0]["data_hex"]
        == "0001020304050607"
    )
    policy = {"steps": [
        {"kind": "checkpoint"},
        {"kind": "trial"},
        {"kind": "trial", "capture_rows": True},
        {"kind": "trial", "capture_rows": False},
    ]}
    replay.configure_replay_capture(policy, full_capture_rows=True)
    assert all("capture_event_kinds" not in row for row in policy["steps"])
    replay.configure_replay_capture(policy)
    assert [row.get("capture_event_kinds") for row in policy["steps"]] == [
        None, ["can-rx", "can-rx-discard", "can-rx-pop", "can-tx"], None, None,
    ]

    replay.configure_replay_capture(mutated)
    replay.configure_transmit_observation(mutated)
    assert all(
        row["capture_rows"] is False and "capture_event_kinds" not in row
        for row in mutated["steps"] if row["kind"] == "trial"
    )
    tx_checks = [
        {"name": "tx-19-control", "actual": "01"},
        {
            "name": "tx-19-payload",
            "actual": "a304000000000080000000002100010001000000",
        },
    ]
    observed = replay.observed_transmit_records({
        "checkpointing": {"trials": [
            {"name": "period-00000-native-cycle", "checks": tx_checks},
            {"name": "period-00001-native-cycle", "checks": tx_checks},
            {
                "name": "period-00002-native-cycle",
                "checks": [{"name": "tx-19-control", "actual": "00"}],
            },
        ]},
    })
    assert observed == [{
        "period": 0, "can_id": 0x4A3, "occurrence": 0,
        "data_hex": "2100010001000000", "buffer": 19,
    }]

    batch = replay.batch_replay_scenarios(
        [("first", scenario), ("second", scenario)], "mapping_batch",
    )
    assert batch["steps"][replay.REPLAY_PREFIX_STEPS] == {
        "kind": "restore", "checkpoint": "normal-operation",
    }
    assert sum(row["kind"] == "restore" for row in batch["steps"]) == 2
    split = replay.split_replay_batch_report({
        "termination_reason": "checkpoint-batch-complete",
        "checkpointing": {"trials": [{
            "name": "first::period-00000-native-cycle",
            "checks": [{"kind": "memory", "name": "destination", "actual": "01"}],
        }]},
    }, ["first", "second"])
    assert split[0]["checkpointing"]["trials"][0]["name"] == (
        "period-00000-native-cycle"
    )
    assert split[1]["checkpointing"]["trials"] == []

    baseline_tx = [{
        "period": 1, "can_id": 0x30, "occurrence": 0, "data_hex": "0010",
    }]
    difference = replay.transmit_difference(
        baseline_tx,
        [{"period": 1, "can_id": 0x30, "occurrence": 0, "data_hex": "0015"}],
    )
    assert difference is not None
    assert difference["period"] == 1 and difference["can_id"] == "0x30"
    assert difference["differing_bytes"] == [{
        "byte": 1, "baseline": "0x10", "mutated": "0x15",
        "xor_mask": "0x05", "bits": [0, 2],
    }]
    assert replay.transmit_difference(baseline_tx, baseline_tx) is None

    with TemporaryDirectory() as directory:
        result_dir = Path(directory)
        identities = [
            {"case_name": f"field-{index}", "scenario_sha256": str(index)}
            for index in range(3)
        ]
        calls: list[str] = []

        def produce(name: str) -> dict[str, object]:
            calls.append(name)
            return {"transmit_records": [], "wall_seconds": 1.0}

        for identity in identities:
            replay.load_or_run_discrimination_result(
                result_dir / f"{identity['case_name']}.json",
                identity,
                lambda identity=identity: produce(str(identity["case_name"])),
            )
        assert calls == ["field-0", "field-1", "field-2"]
        (result_dir / "field-2.json").write_text("{", encoding="utf-8")
        calls.clear()
        resumed = []
        for identity in identities:
            _result, was_resumed = replay.load_or_run_discrimination_result(
                result_dir / f"{identity['case_name']}.json",
                identity,
                lambda identity=identity: produce(str(identity["case_name"])),
            )
            resumed.append(was_resumed)
        assert resumed == [True, True, False]
        assert calls == ["field-2"]

    rx = {"kind": "can-rx", "can_id": "0x115", "data_hex": "0001020304050607"}
    pop = {"kind": "can-rx-pop"}
    discard = {"kind": "can-rx-discard", "can_id": "0x127", "data_hex": "1011121314151617"}
    alias_write = {"kind": "alias-write"}
    tx = {"kind": "can-tx", "can_id": "0x30", "data_hex": "0010"}
    native = {"name": "period-00001-native-cycle", "event_rows": [pop, discard, tx]}
    full_report = {"checkpointing": {"trials": [
        {"event_rows": [rx, alias_write, alias_write]},
        native,
    ]}}
    projected_report = {"checkpointing": {"trials": [
        {"event_rows": [rx], "event_kind_counts": {"can-rx": 1, "alias-write": 2}},
        native,
    ]}}
    reception = replay.summarize_reception(projected_report)
    assert reception == replay.summarize_reception(full_report)
    assert reception["popped"] == 1 and reception["dropped"] == 1
    assert reception["device_event_kinds"] == {
        "alias-write": 2, "can-rx": 1, "can-rx-pop": 1, "can-rx-discard": 1, "can-tx": 1,
    }

    with TemporaryDirectory() as directory:
        candump = Path(directory) / "replay.log"
        replay.write_candump(
            candump, converted["source"], periods,
            projected_report,
        )
        lines = candump.read_text(encoding="utf-8").splitlines()
        assert lines[0].startswith(
            f"# capture-sha256={converted['source']['sha256']} "
        )
        assert any(" eps-rx " in line for line in lines[1:])
        assert any(" eps-tx 030#0010" in line for line in lines[1:])
        bridge_path = Path(directory) / "bridge.json"
        write_bridge_scenario(bridge_path, 49152)
        bridge = load_scenario(bridge_path)
        assert bridge["entry"]["address"] == "0x0"
        assert bridge["reset"] == "power-on"
        assert bridge["event_socket"] == {
            "host": "127.0.0.1",
            "port": 49152,
            "ready_after_arrivals": {"address": "0x660bc", "count": 26},
        }
        held_bridge_path = Path(directory) / "held-bridge.json"
        write_bridge_scenario(held_bridge_path, 49153, hold_when_ready=True)
        held_bridge = load_scenario(held_bridge_path)
        assert held_bridge["event_socket"]["hold_when_ready"] is True
        reset_replay = bridge["reset_replay"]
        assert reset_replay["scenario"].endswith("bridge.reset-replay.json")
        assert reset_replay["memory"]
        assert reset_replay["events"]
        assert any(
            row["kind"] == "csih-word"
            and row.get("unit") == 2
            and row.get("after_transmit_words") == 1025
            and row.get("repeat_forever")
            for row in reset_replay["events"]
        )
        assert bridge["stop_addresses"] == []
        assert bridge["expected_termination"] == "halt"
        assert bridge["max_instructions"] == 5_000_000_000
        assert any(
            row["kind"] == "register-input"
            and row.get("register") == "ICUSSTS2"
            and row.get("value") == "0x0"
            for row in bridge["events"]
        )
    lockout = load_scenario(
        REPO_ROOT
        / "tests/fixtures/rh850/machine/camry-8965F3307000"
        / "camry_f33_security_attempt_limit_and_session_lockout.json"
    )
    assert lockout["expected_termination"] is None
    assert [step["name"] for step in lockout["steps"]] == [
        "initial-security-state",
        "attempt-limit-and-session-lockout",
        "external-pin-reset-to-first-foreground",
        "post-reset-operational-readiness",
    ]
    reset_trial = lockout["steps"][2]
    assert reset_trial["stop_after_arrivals"] == [
        {"address": "0x660bc", "count": 1},
    ]
    assert reset_trial["events"] == [{
        "kind": "reset-assert",
        "reset_class": "system-1-pin",
        "after_instructions": 0,
        "evidence": (
            "External RESET pin System Reset 1 after the observed level-2 "
            "attempt limit"
        ),
    }]
    readiness_trial = lockout["steps"][3]
    assert readiness_trial["stop_after_arrivals"] == [
        {"address": "0x660bc", "count": 25},
    ]
    assert readiness_trial["events"] == []
    reset_checks = {check["name"]: check for check in readiness_trial["checks"]}
    assert reset_checks["reset clears level-2 attempt count"]["equals_hex"] == "00"
    assert reset_checks["startup rearms both SecurityAccess delay bits"]["equals_hex"] == "03000000"
    assert reset_checks["reset clears retained seed RAM"]["equals_hex"] == "00" * 16
    assert {
        reset_checks[f"{name} mode reaches operational readiness"]["equals_hex"]
        for name in ("live", "desired", "active")
    } == {"0207", "02070000"}
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
