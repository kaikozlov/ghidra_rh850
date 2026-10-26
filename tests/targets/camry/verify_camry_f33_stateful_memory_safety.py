#!/usr/bin/env python3
"""Verify the exact-F33 stateful coverage and memory-safety campaign."""
from __future__ import annotations

import tempfile
from pathlib import Path

from tools import REPO_ROOT
from tools.targets.camry.research import fuzz_camry_f33_dcm_handlers as dcm
from tools.targets.camry.research import fuzz_camry_f33_stateful_coverage as fuzz


def verify_pure_oracles(work: Path) -> None:
    print("== deterministic model and corpus oracles ==")
    assert dcm.crc32_raw_words(b"12345678", 0xFFFFFFFF) == 0x651F2550

    context = fuzz.transport_context(fuzz.request(b"\xBA\xF1"))
    assert len(context) == 28
    assert int.from_bytes(context[0:4], "little") == dcm.SLOT_BUFFERS[0]
    assert int.from_bytes(context[4:8], "little") == 2
    assert int.from_bytes(context[8:12], "little") == dcm.RESP_BUF
    assert int.from_bytes(context[12:16], "little") == 0
    assert int.from_bytes(context[20:24], "little") == fuzz.FULL_RESPONSE_CAPACITY
    assert context[24:] == bytes.fromhex("ba000200")


    first_poison = fuzz.with_final_poison(
        dict(fuzz.producer_templates())["routine_start"], 0xA11CE, "first",
    )
    second_poison = fuzz.with_final_poison(
        dict(fuzz.producer_templates())["routine_start"], 0xB22DF, "second",
    )
    assert fuzz.request_tail_salt(first_poison, 0, first_poison.steps[0]) == (
        fuzz.request_tail_salt(second_poison, 0, second_poison.steps[0])
    )
    branch = work / "branch.txt"
    branch.write_text(
        "branch: v850.igen:185  0x00091234 op :: 0x00091240\n"
        "branch: v850.igen:185  0xfec00010 op :: 0xfec00020\n",
        encoding="utf-8",
    )
    assert fuzz.parse_edges([branch]) == {(0x91234, 0x91240)}

    short = fuzz.make_case("short", [fuzz.request(b"\x22"), fuzz.action("poll")])
    request_trace = work / "request-core.txt"
    request_trace.write_text(
        f"read-2 exec:0x00000100 -> 0x0000\n"
        f"read-1 read:{dcm.SLOT_BUFFERS[0] + 1:#010x} -> 0x00\n"
        f"read-2 exec:0x00000102 -> 0x0000\n"
        f"read-1 read:{dcm.RESP_BUF:#010x} -> 0x00\n"
        f"read-2 exec:0x00000104 -> 0x0000\n"
        f"write-1 write:{dcm.RESP_BUF:#010x} <- 0x62\n"
        f"read-2 exec:0x00000106 -> 0x0000\n"
        f"read-1 read:{dcm.RESP_BUF:#010x} -> 0x62\n"
        f"read-2 exec:0x00000108 -> 0x0000\n"
        f"write-2 write:{dcm.RESP_BUF + fuzz.FULL_RESPONSE_CAPACITY - 1:#010x} <- 0x1234\n",
        encoding="utf-8",
    )
    action_trace = work / "action-core.txt"
    action_trace.write_text(
        f"read-2 exec:0x00000200 -> 0x0000\n"
        f"read-1 read:{dcm.SLOT_BUFFERS[0] + 1:#010x} -> 0x22\n",
        encoding="utf-8",
    )
    result = fuzz.CaseResult(
        short,
        [dcm.SENTINEL, dcm.SENTINEL],
        set(),
        None,
        b"",
        [request_trace, action_trace],
    )
    findings = fuzz.memory_access_findings(result)
    classes = [row["classification"] for row in findings]
    assert classes.count("request-read-beyond-declared-length") == 1
    assert classes.count("response-read-before-step-write-definedness-candidate") == 1
    assert classes.count("response-object-right-boundary-crossing") == 1
    assert classes.count("retained-request-read-beyond-declared-length") == 1

    broad = fuzz.make_case("broad", [fuzz.request(b"\x22")])
    narrow = fuzz.make_case("narrow", [fuzz.request(b"\x22\x01")])
    minimized = fuzz.minimize_corpus([
        (narrow, {(1, 2)}),
        (broad, {(1, 2), (2, 3)}),
    ])
    assert [case.case_id for case, _edges in minimized] == [broad.case_id]


def verify_exact_simulator(work: Path) -> None:
    print("== exact-image branch and core traces ==")
    elf, model = fuzz.prepare_elf(work, 30)
    assert model["expected_result"] == "0x651F2550"
    assert model["entry"] == "0xfef00000"
    assert dcm.verify_request_tail_oracle(elf, work, 30) == {
        "entry": "0x4f9b6",
        "fault_pc": "0x4f9c6",
        "destination": "0xfec00000",
    }

    cases = fuzz.seed_cases()
    lifecycle = next(case for case in cases if case.name == "pending_poll_cancel_reuse")
    branch = fuzz.run_cases(
        elf, [cases[0], lifecycle], work, "branch", 30, 8, "verify-branch",
    )
    assert not branch.hangs
    assert len(branch.results) == 2
    assert all(result.edges for result in branch.results)
    assert all(
        pc == dcm.SENTINEL
        for result in branch.results
        for pc in result.step_pcs
    )

    memory = fuzz.audit_memory_accesses(elf, [lifecycle], work, 30)
    assert memory == {
        "schema": "camry-f33-simulator-memory-access-audit-v1",
        "cases": 1,
        "records": [],
        "hangs": [],
    }

    short = fuzz.Case("short_session", 1, 1, (fuzz.request(b"\x10"),))
    short_audit = fuzz.audit_memory_accesses(elf, [short], work, 30)
    assert short_audit["hangs"] == []
    assert len(short_audit["records"]) == 1
    assert short_audit["records"][0]["access_candidates"] == [{
        "classification": "request-read-beyond-declared-length",
        "step": 0,
        "request_length": 1,
        "slot": 0,
        "pc": "0x91078",
        "address": "0xfebe5652",
        "width": 1,
    }]

    routine_short = next(
        case for case in cases if case.name == "short_routine_1004_poll"
    )
    routine_audit = fuzz.audit_memory_accesses(elf, [routine_short], work, 30)
    assert routine_audit["hangs"] == []
    assert {
        (
            row["classification"],
            row["step"],
            row["request_length"],
            row["pc"],
            row["address"],
        )
        for row in routine_audit["records"][0]["access_candidates"]
    } == {
        (
            "retained-request-read-beyond-declared-length",
            1,
            4,
            "0x9758a",
            "0xfebe5656",
        ),
        (
            "retained-request-read-beyond-declared-length",
            1,
            4,
            "0x9758c",
            "0xfebe5655",
        ),
    }

    ba_stale = next(case for case in cases if case.name == "ba_stale_token_reuse")
    ba_audit = fuzz.audit_memory_accesses(elf, [ba_stale], work, 30)
    assert ba_audit["hangs"] == []
    ba_accesses = ba_audit["records"][0]["access_candidates"]
    assert {
        (row["step"], row["pc"], row["address"]) for row in ba_accesses
    } == {
        (3, "0x34d8e", hex(dcm.SLOT_BUFFERS[0] + offset))
        for offset in range(2, 7)
    }

    network = fuzz.audit_network_short_requests(elf, work, 30)
    assert [row["name"] for row in network["findings"]] == [
        "one_byte_session",
        "short_routine_1004",
    ]
    network_rows = {row["name"]: row for row in network["records"]}
    assert (
        network_rows["zero_length"]["request_phase_after_receive"],
        network_rows["zero_length"]["declared_request_length_after_receive"],
        network_rows["zero_length"]["overread_events"],
    ) == (0, 0, [])
    assert (
        network_rows["one_byte_session"]["request_phase_after_receive"],
        network_rows["one_byte_session"]["declared_request_length_after_receive"],
    ) == (2, 1)
    assert {
        (row["pc"], row["address"])
        for row in network_rows["one_byte_session"]["overread_events"]
    } == {("0x91078", "0xfebe5652")}
    assert (
        network_rows["short_routine_1004"]["request_phase_after_receive"],
        network_rows["short_routine_1004"]["declared_request_length_after_receive"],
    ) == (2, 4)
    assert {
        (row["pc"], row["address"])
        for row in network_rows["short_routine_1004"]["overread_events"]
    } == {
        ("0x9758a", "0xfebe5656"),
        ("0x9758c", "0xfebe5655"),
    }

    empty = fuzz.Case("empty", 1, 0, (fuzz.request(b""),))
    divergence = fuzz.audit_request_tail_divergence(
        elf, work, 30, 8, [short, empty],
    )
    assert divergence["hangs"] == []
    assert [row["request_length"] for row in divergence["findings"]] == [0]
    empty_finding = divergence["findings"][0]
    assert empty_finding["branch_edge_difference_count"] > 0
    assert {"start": "0xfebe562c", "end": "0xfebe562c"} in (
        empty_finding["persistent_post_state_difference_runs"]
    )

    print("== multiservice response extents ==")
    extent = fuzz.audit_producer_extents(elf, work, 30, 32)
    assert extent["families"] == 15
    assert extent["trials"] == 30
    assert extent["findings"] == []
    assert extent["hangs"] == []
    ba = next(row for row in extent["records"] if row["family"] == "proprietary_ba")
    assert ba["first"]["response_length"] == 1
    assert ba["first"]["prefix"] == "fa"
    assert ba["poison_changed_behavior"] is False


def main() -> int:
    out_root = REPO_ROOT / "build/out"
    out_root.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="verify-f33-stateful-", dir=out_root) as td:
        work = Path(td)
        verify_pure_oracles(work)
        verify_exact_simulator(work)
    print("stateful memory-safety oracle verification passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
