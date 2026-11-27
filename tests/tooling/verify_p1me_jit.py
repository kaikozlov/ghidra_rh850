"""Compare P1M-E interpreter and JIT behavior at instruction, restore, and device boundaries."""
import json
import os
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from tools import REPO_ROOT
from tools.emulation.checkpoint_benchmark import _require_equivalent_trials
from tools.emulation.p1me_machine import (
    P1MEMachineError, _execute, _failure_summary, _run_cli, _target_contract, _write_drcov,
)

TARGET = "camry-8965F3307000"
FIXTURES = REPO_ROOT / "tests/fixtures/rh850/machine" / TARGET
HOT_BUS_ROUNDS = 224
HOT_BUS_SWITCH = 7 * HOT_BUS_ROUNDS


def _hot_bus_fixture(schema: str) -> dict:
    return {
        "schema": schema,
        "name": "hot-indirect-bus",
        "entry": {"role": "indirect-bus-loop", "scope": "resolved-address",
                  "address": "0xFEBE0000"},
        "gpr_fill": "0",
        "registers": {"r6": "0xFFC5B008", "r7": "0xFEBE0100", "lp": "0xFEBE0000"},
        "memory": [{
            "address": "0xFEBE0000",
            "hex": "2637010067370100" * 3 + "7f00",
            "evidence": "Three pairs of ld.w 0[r6],r6; st.w r6,0[r7]; then jmp [lp].",
        }],
        "events": [
            {"kind": "register-input", "register": "DFERSTC", "value": "0xFFC5B008",
             "after_instructions": 0, "evidence": "Bus response points back to DFERSTC."},
            {"kind": "register-input", "register": "DFERSTC", "value": "0xFFC5B010",
             "after_instructions": HOT_BUS_SWITCH,
             "evidence": "After warmup, point to DFOVFSTC, which has no supplied read response."},
        ],
        "max_instructions": HOT_BUS_SWITCH + 7,
        "stop_addresses": [],
        "expected_fault": {"kind": "missing-read-input", "address": "0xFFC5B010",
                           "access": "read"},
        "checks": [
            {"name": "late-response-loaded", "kind": "register", "register": "r6",
             "equals": "0xFFC5B010"},
            {"name": "late-response-stored-before-fault", "kind": "memory",
             "address": "0xFEBE0100", "size": 4, "equals_hex": "10b0c5ff"},
            {"name": "late-store-visible-through-local-ram-alias", "kind": "memory",
             "address": "0xFEDE0100", "size": 4, "equals_hex": "10b0c5ff"},
        ],
    }


def _verify_hot_bus(report: dict) -> None:
    loop = (
        ("0xFEBE0000", 4, "read"), ("0xFEBE0004", 4, "write"),
        ("0xFEBE0008", 4, "read"), ("0xFEBE000C", 4, "write"),
        ("0xFEBE0010", 4, "read"), ("0xFEBE0014", 4, "write"),
        ("0xFEBE0018", 2, None),
    )
    # The final iteration loads the changed response, stores it, then faults
    # at the next load. The fault is traced at entry, but has no bus-access row.
    timeline = loop * HOT_BUS_ROUNDS + loop[:3]
    instructions = report["instruction_trace"]
    assert [(r["instruction"], r["pc"], r["size"]) for r in instructions] == [
        (tick, pc, size) for tick, (pc, size, _) in enumerate(timeline)
    ], report["scenario"]
    accesses = report["memory_accesses"]
    assert [(r["instruction"], r["pc"], r["size"], r["kind"], r["address"])
            for r in accesses] == [
        (tick, pc, size, kind, {"read": "0xFFC5B008", "write": "0xFEBE0100"}[kind])
        for tick, (pc, size, kind) in enumerate(timeline[:-1]) if kind is not None
    ], report["scenario"]
    fault = report["fault"]
    assert report["final_pc"] == fault["pc"] == "0xFEBE0008", fault
    assert (fault["kind"], fault["address"], fault["size"], fault["access"]) == (
        "missing-read-input", "0xFFC5B010", 4, "read",
    ), fault

    response, alias = "external-register-read-response", "alias-write"
    events = [r for r in report["device_events"] if r["kind"] in (response, alias)]
    assert [r["kind"] for r in events] == (
        [response] + [alias] * (3 * HOT_BUS_ROUNDS) + [response, alias]
    ), report["scenario"]
    assert [(r["register"], r["address"], r["value"], r["scheduler_tick"])
            for r in events if r["kind"] == response] == [
        ("DFERSTC", "0xFFC5B008", "0xFFC5B008", 0),
        ("DFERSTC", "0xFFC5B008", "0xFFC5B010", HOT_BUS_SWITCH),
    ], report["scenario"]
    assert all((r["from"], r["to"], r["size"]) == ("0xFEBE0100", "0xFEDE0100", 4)
               for r in events if r["kind"] == alias), report["scenario"]

    compiled = report["jit_compiled_instructions"]
    for kind in ("read", "write"):
        warm_accesses = sum(r["kind"] == kind and r["instruction"] < HOT_BUS_SWITCH
                            for r in accesses)
        # If no access of this kind ran in generated code, at most this many
        # other instructions could have contributed to the compiled count.
        assert compiled > len(instructions) - warm_accesses, (kind, compiled)


def _verify_cli_reports(root: Path, loop: dict) -> None:
    serial = {"kind": "csih-word", "after_transmit_words": 1, "delay_instructions": 2,
              "repeat": 3, "stride_words": 4, "unit": 1, "value": "0x11",
              "evidence": "Three externally supplied, controller-relative words."}
    base = {**loop, "max_instructions": 2, "steps": [], "events": [serial],
            "expected_termination": "instruction-budget"}
    passed, failed = (root / f"{name}.json" for name in ("short", "wrong-register"))
    passed.write_text(json.dumps({**base, "name": passed.stem}))
    failed.write_text(json.dumps({**base, "name": failed.stem, "checks": [
        {"kind": "register", "name": "wrong-lp", "register": "lp", "equals": "1"},
    ]}))
    out = root / "cli"
    try:
        with patch.dict(os.environ):
            os.environ.pop("P1ME_MACHINE_ENGINE", None)
            _run_cli(TARGET, [passed, failed], out, instruction_trace=True)
    except P1MEMachineError:
        pass
    else:
        raise AssertionError("CLI did not report a failed register check")
    target = _target_contract(TARGET)
    for path in (passed, failed):
        report = json.loads((out / f"{path.stem}.report.json").read_bytes())
        assert report["engine"] == "Ghidra JitPcodeEmulator"
        assert report["passed"] == (path == passed)
        assert report["termination_reason"] == "instruction-budget"
        assert [(row["name"], row["passed"]) for row in report["checks"]] == (
            [] if path == passed else [("wrong-lp", False)]
        )
        events = report["resolved_run_contract"]["events"]
        ordinals = [e["after_transmit_words"] + i * e.get("stride_words", 1)
                    for e in events for i in range(e.get("repeat", 1))]
        assert ordinals == [1, 5, 9], events
        expected = root / "reference.drcov"
        _write_drcov(report, target, expected)
        assert Path(report["drcov_path"]).read_bytes() == expected.read_bytes()


def _quiet_clock_fixture(schema: str) -> dict:
    counter = "0xFFE50010"
    checks = [
        {"name": "load-synchronizes-clock", "kind": "register", "register": "r8",
         "equals": "9"},
        {"name": "restore-reload-and-final-quiet-tail", "kind": "memory", "address": counter,
         "size": 4, "equals_hex": "02000000"},
    ]
    trial = {"kind": "trial", "name": "straight", "max_instructions": 16,
             "stop_addresses": ["0xFEBE0024"], "events": [], "checks": checks}
    return {
        "schema": schema, "name": "quiet-hsb",
        "entry": {"role": "quiet-hsb", "scope": "resolved-address", "address": "0xFEBE0000"},
        "gpr_fill": "0", "hsb_cycles_per_instruction": 1,
        "registers": {"r6": "1", "r7": "0xFFE50054", "r8": counter,
                      "r9": "0xFFE50000", "r10": "5", "r11": "0xFEBE0101", "MCTL": "0"},
        "memory": [
            {"address": "0xFEBE0000",
             "hex": "47370000" + "0000" * 3 + "28470100" + "0000" * 2
                    + "69570100" + "0000" * 7 + "2b370100",
             "evidence": "st.b r6,0[r7]; 3 nop; ld.w 0[r8],r8; 2 nop; "
                         "st.w r10,0[r9]; 7 nop; ld.w 0[r11],r6"},
            {"address": "0xFFE50090", "hex": "0000", "evidence": "CK0 divides HSB by one."},
            {"address": "0xFFE50000", "hex": "0c000000", "evidence": "TAUJ0CDR0 reload 12."},
            {"address": "0xFFFFB10A", "hex": "8200", "evidence": "Masked TAUJ0 IRQ."},
        ],
        "events": [{"kind": "clock", "after_instructions": 6, "p_bus_cycles": 2,
                    "evidence": "Explicit clock during a quiet interval."}],
        "max_instructions": 16, "stop_addresses": [], "checks": checks,
        "steps": [
            {"kind": "checkpoint", "name": "quiet", "after_instructions": 4},
            trial, {"kind": "restore", "checkpoint": "quiet"},
            {**trial, "name": "restored"},
        ],
    }


def _verify_interrupt_poll(root: Path, schema: str) -> None:
    start, branch, done = "0xFEBE0000", "0xFEBE0004", "0xFEBE0006"
    edge = {"kind": "interrupt", "channel": 136, "after_instructions": 1001,
            "evidence": "Set the request after the test and before its conditional branch."}
    poll = {"kind": "trial", "name": "poll", "max_instructions": 1009,
            "stop_addresses": [done], "capture_rows": False, "events": [edge], "checks": []}
    paths = []
    for engine in ("plain", "jit"):
        path = root / f"interrupt-poll-{engine}.json"
        path.write_text(json.dumps({
            "schema": schema, "name": path.stem, "engine": engine,
            "entry": {"role": "masked-interrupt-poll", "scope": "resolved-address", "address": start},
            "gpr_fill": "0", "registers": {"PSW": "0"}, "hsb_cycles_per_instruction": 1,
            "memory": [{"address": start, "hex": "c0e711b1e2fd",
                        "evidence": "tst1 4,-0x4eef[r0]; be -4"},
                       {"address": "0xFFFFB110", "hex": "8000", "evidence": "Masked EIC136."}],
            "max_instructions": 1010, "stop_addresses": [], "checks": [],
            "steps": [{"kind": "checkpoint", "name": "start", "after_instructions": 0}, poll,
                      {"kind": "restore", "checkpoint": "start"},
                      {**poll, "name": "captured", "capture_rows": True},
                      {"kind": "restore", "checkpoint": "start"},
                      {**poll, "name": "branch-stop", "stop_addresses": [branch]}],
        }))
        paths.append(path)
    a, b = _execute(TARGET, paths, instruction_trace=False)["reports"]
    assert a["passed"] and b["passed"], (a.get("fault"), b.get("fault"))
    for left, right in zip(a["checkpointing"]["trials"], b["checkpointing"]["trials"], strict=True):
        for key in ("final_pc", "instruction_count", "register_rows", "memory_rows", "event_rows"):
            assert left[key] == right[key], (right["name"], key)
    quiet, captured, stopped = b["checkpointing"]["trials"]
    assert (quiet["final_pc"], quiet["instruction_count"]) == (done, 1004)
    assert quiet["jit_idle_instructions"] > 0
    assert captured["jit_idle_instructions"] == 0 and len(captured["memory_rows"]) == 502
    assert (stopped["final_pc"], stopped["instruction_count"]) == (branch, 1)


def _verify_template_fault(root: Path, schema: str) -> None:
    code, pointer, output = "0xFEBE0000", "0xFEBE6000", "0xFEBE7000"
    paths = []
    for engine in ("plain", "jit"):
        path = root / f"late-ram-fault-{engine}.json"
        path.write_text(json.dumps({
            "schema": schema, "name": path.stem, "engine": engine,
            "entry": {"role": "ram-pointer-loop", "scope": "resolved-address", "address": code},
            "gpr_fill": "0", "registers": {"r6": pointer, "r7": output, "lp": code},
            "memory": [
                {"address": code, "hex": "01522637010067370100263701007f00",
                 "evidence": "mov 1,r10; ld.w [r6],r6; st.w r6,[r7]; ld.w [r6],r6; jmp [lp]"},
                {"address": pointer, "hex": "0060befe", "evidence": "Self-referential pointer."},
                {"address": output, "hex": "00000000", "evidence": "Initialized result word."},
            ],
            "events": [{"kind": "memory-write", "address": pointer, "data_hex": "e898bffe",
                        "after_instructions": 1000, "evidence": "Point to an undefined RAM word."}],
            "stop_addresses": [], "max_instructions": 1010,
            "expected_fault": {"kind": "uninitialized-read", "address": "0xFEBF98E8",
                               "access": "read"},
            "checks": [{"name": "prefix-store-through-alias", "kind": "memory",
                        "address": "0xFEDE7000", "size": 4, "equals_hex": "e898bffe"}],
        }))
        paths.append(path)
    plain, jit = _execute(TARGET, paths, instruction_trace=False)["reports"]
    assert plain["passed"] and jit["passed"], (plain.get("fault"), jit.get("fault"))
    assert jit["jit_compiled_instructions"] > 0
    assert jit["fault"]["pc"] == "0xFEBE000A"
    for key in ("fault", "checks", "final_pc", "instruction_count", "memory_accesses", "device_events"):
        assert plain[key] == jit[key], key


def _verify_hot_divisor_change(root: Path, schema: str) -> None:
    code = "0xFEBE0000"
    paths = []
    for engine in ("plain", "jit"):
        path = root / f"hot-divisor-change-{engine}.json"
        path.write_text(json.dumps({
            "schema": schema, "engine": engine, "name": path.stem,
            "entry": {"role": "divide-loop", "scope": "resolved-address", "address": code},
            "gpr_fill": "0", "registers": {"lp": code, "r6": "2", "PSW": "0"},
            "memory": [{"address": code, "hex": "0752e657fc5a02327f00",
                        "evidence": "mov 7,r10; divq r6,r10,r11; mov 2,r6; jmp [lp]"}],
            "events": [{"kind": "memory-write", "address": "0xFEBE0006", "data_hex": "0032",
                        "after_instructions": 1024, "evidence": "Set up a zero divisor."}],
            "max_instructions": 1030, "stop_addresses": [], "expected_termination": "instruction-budget",
            "steps": [
                {"kind": "checkpoint", "name": "start", "after_instructions": 0},
                {"kind": "trial", "name": "divide-through-overlay", "capture_rows": False,
                 "max_instructions": 1030, "stop_addresses": [], "events": [], "checks": []},
            ],
            "checks": [{"kind": "register", "register": reg, "name": reg, "equals": value}
                       for reg, value in (("r10", "7"), ("r11", "1"))],
        }))
        paths.append(path)
    plain, jit = _execute(TARGET, paths, instruction_trace=False)["reports"]
    assert plain["passed"] and jit["passed"], (plain["checks"], jit["checks"])
    a, = plain["checkpointing"]["trials"]
    b, = jit["checkpointing"]["trials"]
    assert a["register_rows"] == b["register_rows"] and b["instruction_count"] == 1030
    assert b["memory_rows"] == b["event_rows"] == []
    for key in ("final_pc", "instruction_count", "checks", "memory_accesses", "device_events"):
        assert jit[key] == plain[key], key


def _verify_event_projection(root: Path, schema: str) -> None:
    scenario = _hot_bus_fixture(schema)
    del scenario["expected_fault"]
    response = "external-register-read-response"
    trial = {
        "kind": "trial", "max_instructions": 7, "stop_addresses": [],
        "events": [{**scenario["events"][0], "after_instructions": 1}],
        "checks": [{"kind": "event-count", "name": "including-prefix-response",
                    "operation": response, "equals": "2"}],
    }
    restore = {"kind": "restore", "checkpoint": "prefix"}
    scenario.update({
        "engine": "jit", "name": "projected-bus", "checks": [],
        "events": scenario["events"][:1], "expected_termination": "instruction-budget",
        "steps": [{"kind": "checkpoint", "name": "prefix", "after_instructions": 1},
                  {**trial, "name": "full"}, restore,
                  {**trial, "name": "selected", "capture_event_kinds": [response]}, restore,
                  {**trial, "name": "counts", "capture_event_kinds": []}],
    })
    path = root / "projected-bus.json"
    path.write_text(json.dumps(scenario))
    report, = _execute(TARGET, [path])["reports"]
    full, selected, counts = report["checkpointing"]["trials"]
    assert report["passed"], [t["checks"] for t in (full, selected, counts)]
    assert report["trace_lost_address"], "unrecorded writes are not retained address evidence"
    assert full["memory_rows"] and not selected["memory_rows"] and not counts["memory_rows"]
    assert selected["event_rows"] == [r for r in full["event_rows"] if r["kind"] == response]
    assert len(selected["event_rows"]) == 1 and not counts["event_rows"]
    assert selected["event_kind_counts"] == counts["event_kind_counts"] == {
        "alias-write": 3, response: 1,
    }


def main() -> None:
    trial = {"kind": "trial", "name": "warm", "max_instructions": 4097,
             "stop_addresses": [], "events": [], "checks": []}
    loop = {
        "schema": "rh850-p1me-machine-scenario-v2", "name": "ram-clear",
        "entry": {"role": "ram-clear", "scope": "resolved-address", "address": "0x632b2"},
        "gpr_fill": "0", "registers": {"lp": "0x632b2"},
        "max_instructions": 6145, "stop_addresses": [], "checks": [],
        "steps": [{"kind": "checkpoint", "name": "in-loop", "after_instructions": 2048},
                  trial, {"kind": "restore", "checkpoint": "in-loop"},
                  {**trial, "name": "uncaptured", "capture_rows": False},
                  {"kind": "restore", "checkpoint": "in-loop"},
                  {**trial, "name": "restored"}],
    }
    byte_extract = {
        "schema": loop["schema"], "name": "hot-in-place-byte-extension",
        "entry": {"role": "byte-extract", "scope": "resolved-address", "address": "0x611fa"},
        "gpr_fill": "0", "registers": {"lp": "0x611fa", "r6": "0xfebe7000"},
        "memory": [{"address": "0xfebe7000", "hex": "0082000000000000",
                    "evidence": "High byte must not survive the low-byte extraction."}],
        "max_instructions": 3200, "stop_addresses": [], "expected_termination": "instruction-budget",
        "checks": [],
    }
    split_fetch = {
        "schema": loop["schema"], "name": "fetch-crosses-mpu-descriptors",
        "entry": {"role": "straddling-load", "scope": "resolved-address", "address": "0xfebe0002"},
        "gpr_fill": "0", "registers": {
            "MPM": "3", "MPLA0": "0xfebe0000", "MPUA0": "0xfebe0000", "MPAT0": "0xa0",
            "MPLA1": "0xfebe0004", "MPUA1": "0xfebe0004", "MPAT1": "0xa0",
        },
        "memory": [{"address": "0xfebe0002", "hex": "26370100",
                    "evidence": "Four-byte ld.w crosses two adjacent four-byte execute grants."}],
        "max_instructions": 1, "stop_addresses": [], "checks": [],
        "expected_fault": {"kind": "mpu-execute", "address": "0xfebe0002", "access": "execute"},
    }
    # The first fetch permits the whole block. Its own LDSR revokes that grant.
    revoke_pc = 0xFEBE0000
    descriptors = {f"{name}{i}": "0" for i in range(16) for name in ("MPLA", "MPUA", "MPAT")}
    revoke_fetch = {
        "schema": loop["schema"], "name": "revoke-live-fetch-grant",
        "entry": {"role": "mpu-policy-change", "scope": "resolved-address", "address": hex(revoke_pc)},
        "gpr_fill": "0", "registers": {**descriptors, "MPM": "3", "ASID": "0", "r6": "0",
                                         "MPLA15": hex(revoke_pc), "MPUA15": hex(revoke_pc + 4), "MPAT15": "0xe0"},
        "memory": [{"address": hex(revoke_pc), "hex": "0000e6f720380000",
                    "evidence": "nop; ldsr r6,MPAT15; nop (processor fixture ldsr-mpat15)."}],
        "stop_addresses": [], "max_instructions": 4,
        "expected_fault": {"kind": "mpu-execute", "access": "execute", "address": hex(revoke_pc + 6)},
        "checks": [{"kind": "register", "name": "grant-revoked", "register": "MPAT15", "equals": "0"}],
    }
    fixtures = [loop, byte_extract, split_fetch, revoke_fetch] + [json.loads((FIXTURES / name).read_text()) for name in (
        "checkpoint-restore-tauj-identity.json", "intc-csih-edge-acceptance-and-real-eiret.json",
        "reset-factors-undefined-read-bit-needs-input.json",
        "intc-csih-equal-priority-channel-tie.json", "intc-pending-request-delivered-after-native-unmask.json",
        "mpu-region12-write-permitted.json", "mpu-region12-write-denied.json",
    )]
    for psw, expected in ((0, "16"), (2, "1")):
        fixtures.append({
            "schema": loop["schema"], "name": f"conditional-move-psw-{psw}",
            "entry": {"role": "conditional-move", "scope": "resolved-address",
                      "address": "0xFEBE0000"},
            "gpr_fill": "0",
            "registers": {"lp": "0xFEBE0000", "PSW": str(psw), "r1": "1", "r16": "16"},
            "memory": [{"address": "0xFEBE0000", "hex": "f00f3c8b7f00",
                        "evidence": "cmovge r16,r1,r17; jmp [lp]"}],
            "max_instructions": 32, "stop_addresses": [], "expected_termination": "instruction-budget",
            "checks": [{"name": "selected-source", "kind": "register", "register": "r17",
                        "equals": expected}],
        })
    quiet = _quiet_clock_fixture(loop["schema"])
    # Warm the divide-by-zero arm, then take the previously unexecuted quotient arm.
    fixtures.append({
        "schema": loop["schema"], "name": "divide-changes-path",
        "entry": {"role": "divide-loop", "scope": "resolved-address", "address": "0xFEBE0000"},
        "gpr_fill": "0", "registers": {"lp": "0xFEBE0000", "r10": "121", "PSW": "0"},
        "memory": [{"address": "0xFEBE0000", "hex": "e657fc5a00327f00",
                    "evidence": "divq r6,r10,r11; mov 0,r6; jmp [lp]"}],
        "events": [{"kind": "memory-write", "address": "0xFEBE0004", "data_hex": "0232",
                    "after_instructions": 6, "evidence": "Change divisor setup to mov 2,r6."}],
        "max_instructions": 10, "expected_termination": "instruction-budget", "stop_addresses": [],
        "checks": [{"kind": "register", "name": name, "register": reg, "equals": value}
                   for name, reg, value in (("quotient", "r10", "60"), ("remainder", "r11", "1"),
                                            ("overflow-cleared", "PSW", "0"))],
    })
    fixtures.append({
        "schema": loop["schema"], "name": "replace-straddling-instruction",
        "entry": {"role": "load-loop", "scope": "resolved-address", "address": "0xFEBE7FFE"},
        "gpr_fill": "0", "registers": {"lp": "0xFEBE7FFE", "r6": "0xFEBE0100"},
        "memory": [{"address": "0xFEBE7FFE", "hex": "265701007f00",
                    "evidence": "ld.w 0[r6],r10; jmp [lp]"},
                   {"address": "0xFEBE0100", "hex": "0100000002000000",
                    "evidence": "Displacements 0 and 4 give distinct load results."}],
        "events": [{"kind": "memory-write", "address": "0xFEBE8000", "data_hex": "0500",
                    "after_instructions": 192, "evidence": "Rewrite only the second-page displacement."}],
        "max_instructions": 256, "expected_termination": "instruction-budget", "stop_addresses": [],
        "checks": [{"kind": "register", "name": "replacement-load", "register": "r10", "equals": "2"}],
    })
    fixtures += [
        quiet,
        {**quiet, "name": "quiet-hsb-fault", "steps": [],
         "expected_fault": {"kind": "misaligned-read", "address": "0xFEBE0101",
                            "access": "read"}},
    ]
    fixtures.append(_hot_bus_fixture(loop["schema"]))
    with TemporaryDirectory(prefix="p1me-jit-") as temp:
        root = Path(temp)
        paths = []
        for fixture in fixtures:
            for engine in ("plain", "jit"):
                name = f"{fixture['name']}-{engine}"
                path = root / f"{name}.json"
                scenario = {**fixture, "engine": engine, "name": name}
                if fixture["name"] == "quiet-hsb-fault":
                    scenario["snapshot_outputs"] = [{
                        "address": "0xFFE50010", "size": 4,
                        "path": str(root / f"{name}.bin"), "evidence": "Live counter after fault.",
                    }]
                path.write_text(json.dumps(scenario))
                paths.append(path)
        # A generated entry must not survive a byte change at the same PC. Restoring
        # the checkpoint changes those bytes again without a processor STORE.
        ram = "0xfebe0000"
        check = {"kind": "register", "name": "loop-result", "register": "r10"}
        overlay = {
            "schema": loop["schema"], "name": "replace-hot-instruction", "engine": "jit",
            "entry": {"role": "constant-loop", "scope": "resolved-address", "address": ram},
            "gpr_fill": "0", "registers": {"lp": ram},
            "memory": [{"address": ram, "hex": "01527f00", "evidence": "mov 1,r10; jmp [lp]"}],
            "max_instructions": 512, "stop_addresses": [], "checks": [],
            "steps": [
                {"kind": "checkpoint", "name": "hot", "after_instructions": 256},
                {**trial, "name": "replaced", "max_instructions": 256,
                 "events": [{"kind": "memory-write", "address": ram, "data_hex": "0252",
                             "after_instructions": 0, "evidence": "Replace mov 1,r10 with mov 2,r10"}],
                 "checks": [{**check, "equals": "2"}]},
                {"kind": "restore", "checkpoint": "hot"},
                {**trial, "name": "original", "max_instructions": 256,
                 "checks": [{**check, "equals": "1"}]},
            ],
        }
        overlay_path = root / "overlay.json"
        overlay_path.write_text(json.dumps(overlay))
        # The portable timer fixture resolves its instruction shape in the analyzed program.
        reports = _execute(TARGET, [*paths, overlay_path], instruction_trace=True)["reports"]
        for engine in ("plain", "jit"):
            raw = (root / f"quiet-hsb-fault-{engine}.bin").read_bytes()
            assert raw == bytes.fromhex("02000000"), (engine, raw)
        failures = [_failure_summary(report) for report in reports if not report["passed"]]
        assert not failures, "\n".join(failures)
        overlay_report = reports.pop()
        assert overlay_report["jit_compiled_instructions"] > 0, "overlay never ran generated code"
        try:
            _require_equivalent_trials(*overlay_report["checkpointing"]["trials"])
        except P1MEMachineError:
            pass
        else:
            raise AssertionError("checkpoint benchmark accepted different r10 results")
        for plain, jit in zip(reports[::2], reports[1::2], strict=True):
            for key in ("final_pc", "termination_reason", "fault", "instruction_trace",
                        "checks", "memory_accesses", "device_events"):
                assert plain.get(key) == jit.get(key), (plain["scenario"], key)
            left = plain.get("checkpointing", {}).get("trials", [])
            right = jit.get("checkpointing", {}).get("trials", [])
            for a, b in zip(left, right, strict=True):
                for key in ("register_rows", "memory_rows", "event_rows", "instruction_trace",
                            "instruction_count", "final_pc", "checks", "termination_reason"):
                    assert a[key] == b[key], (plain["scenario"], a["name"], key)
        for report in reports:
            if report["scenario"] in ("quiet-hsb-plain", "quiet-hsb-jit"):
                timer_edges = [row for row in report["device_events"] if row["kind"] == "tauj-clock"]
                assert [(row["scheduler_tick"], row["hsb_cycles"], row["start_load"])
                        for row in timer_edges] == [(1, 1, True), (12, 1, False), (12, 1, False)]
        _verify_hot_bus(next(r for r in reports if r["scenario"] == "hot-indirect-bus-jit"))
        plain, jit = reports[:2]
        assert jit["jit_compiled_instructions"] > 0
        for report in (plain, jit):
            warm, uncaptured, restored = report["checkpointing"]["trials"]
            _require_equivalent_trials(warm, restored)
            assert warm["instruction_count"] == trial["max_instructions"]
            assert warm["memory_rows"]
            assert uncaptured["memory_rows"] == uncaptured["event_rows"] == []
            after_prefix = [row for row in report["memory_accesses"]
                            if row["instruction"] >= warm["start_instruction"]]
            assert after_prefix == warm["memory_rows"] + restored["memory_rows"]
        _verify_interrupt_poll(root, loop["schema"])
        _verify_template_fault(root, loop["schema"])
        _verify_hot_divisor_change(root, loop["schema"])
        _verify_event_projection(root, loop["schema"])
        _verify_cli_reports(root, loop)
        print(f"PASS {len(fixtures)} interpreter/JIT differential cases and hot overlay/restore; "
              f"{jit['jit_compiled_instructions']} loop instructions retired in generated code")


if __name__ == "__main__":
    main()
