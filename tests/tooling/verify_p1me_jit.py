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
            _run_cli(TARGET, [passed, failed], out, instruction_trace=True, private_headless=False)
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
        assert [e["after_transmit_words"] for e in events] == [1, 5, 9]
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
    fixtures = [loop, byte_extract, split_fetch] + [json.loads((FIXTURES / name).read_text()) for name in (
        "checkpoint-restore-tauj-identity.json", "intc-csih-edge-acceptance-and-real-eiret.json",
        "reset-factors-undefined-read-bit-needs-input.json",
        "intc-csih-equal-priority-channel-tie.json", "intc-pending-request-delivered-after-native-unmask.json",
        "mpu-region12-write-permitted.json", "mpu-region12-write-denied.json",
    )]
    quiet = _quiet_clock_fixture(loop["schema"])
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
        reports = _execute(TARGET, [*paths, overlay_path], private_headless=False,
                           instruction_trace=True)["reports"]
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
        _verify_cli_reports(root, loop)
        print(f"PASS {len(fixtures)} interpreter/JIT differential cases and hot overlay/restore; "
              f"{jit['jit_compiled_instructions']} loop instructions retired in generated code")


if __name__ == "__main__":
    main()
