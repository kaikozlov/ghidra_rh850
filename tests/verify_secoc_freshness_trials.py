#!/usr/bin/env python3
"""Verify offline SecOC reset/future-sync and tag-guess trial construction."""

from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from exploit.followups.secoc_freshness_trials import (  # noqa: E402
    FreshnessTrialError,
    TAG_MASK,
    build_fd_suffix_alias,
    build_future_sync,
    build_reset_replay,
    build_tag_guesses,
    parse_protected_frame,
    parse_sync_frame,
    replace_tag,
    sync_candidate_is_forward,
)
from tools.toyota_secoc_signer import sign_classic_frame, sign_sync_frame  # noqa: E402

KEY = bytes(range(16))
passed = failed = 0


def check(label: str, condition: bool, detail: str = "") -> None:
    global passed, failed
    if condition:
        passed += 1
        print(f"[PASS] {label}" + (f" ({detail})" if detail else ""))
    else:
        failed += 1
        print(f"[FAIL] {label}" + (f" ({detail})" if detail else ""))


def rejects(fn) -> bool:
    try:
        fn()
    except FreshnessTrialError:
        return True
    return False


print("== synchronization parsing and firmware ordering model ==")
sync = sign_sync_frame(KEY, 0x1234, 0x56789)
parsed_sync = parse_sync_frame(sync)
check("sync parser recovers trip/reset", (parsed_sync.trip, parsed_sync.reset) == (0x1234, 0x56789))
check("sync parser preserves exact tag28", parsed_sync.tag28 == (int.from_bytes(sync, "big") & TAG_MASK))
check("equal sync rejected", not sync_candidate_is_forward(7, 9, 7, 9))
check("rollback sync rejected", not sync_candidate_is_forward(7, 9, 6, 0xFFFFF))
check("same-trip reset advance accepted", sync_candidate_is_forward(7, 9, 7, 10))
check("large forward trip jump accepted", sync_candidate_is_forward(1, 0, 0xE000, 0))
check("configured wrap accepted", sync_candidate_is_forward(0xFFF0, 4, 1, 0))

print("\n== reset replay artifact ==")
protected = sign_classic_frame(KEY, 0x2E4, bytes.fromhex("01020304"), 0x1234, 0x56789, 0xAB)
replay = build_reset_replay(sync, [(0x2E4, protected)])
check("reset replay binds SECOC-012", replay["finding_ids"] == ["SECOC-012"])
check("captured positive sync is forward from zero", replay["captured_sync"]["structurally_forward_from_post_init_zero"] is True)
check("reset replay preserves signed sync bytes unchanged", replay["captured_sync"]["frame"] == sync.hex())
check("reset replay preserves protected bytes unchanged", replay["protected_replays"][0]["frame"] == protected.hex())
check("reset replay exposes startup suppression as dynamic unknown", any("startup" in item for item in replay["dynamic_unknowns"]))
check("zero sync cannot masquerade as replay candidate", rejects(lambda: build_reset_replay(bytes(8), [(0x2E4, protected)])))

print("\n== future synchronization artifact ==")
current = sign_sync_frame(KEY, 10, 20)
future = sign_sync_frame(KEY, 0xE000, 1)
future_plan = build_future_sync(current, future)
check("future-sync binds SECOC-012", future_plan["finding_ids"] == ["SECOC-012"])
check("future sync is structurally forward", future_plan["candidate_sync"]["structurally_forward"] is True)
check("future-sync requires independently valid MAC", "valid MAC" in future_plan["cryptographic_precondition"])
backward = sign_sync_frame(KEY, 9, 0xFFFFF)
check("backward candidate is rejected offline", rejects(lambda: build_future_sync(current, backward)))

print("\n== FD ignored-suffix alias artifact ==")
base32 = bytes(range(32))
alias48 = build_fd_suffix_alias(base32, bytes.fromhex("aa" * 16))
alias64 = build_fd_suffix_alias(base32, bytes.fromhex("55" * 32))
check("FD alias binds SECOC-014", alias48["finding_ids"] == ["SECOC-014"])
check("DLC48 alias preserves exact first 32 bytes", bytes.fromhex(alias48["physical_frame"])[:32] == base32 and alias48["physical_dlc"] == 48)
check("DLC64 alias preserves exact first 32 bytes", bytes.fromhex(alias64["physical_frame"])[:32] == base32 and alias64["physical_dlc"] == 64)
check("FD alias declares EPS effective length 32", alias48["eps_secoc_effective_length"] == 32 and alias48["eps_authenticated_view_unchanged"] is True)
check("invalid FD suffix width rejected", rejects(lambda: build_fd_suffix_alias(base32, bytes(8))))

print("\n== bounded tag-guess artifact ==")
parsed = parse_protected_frame(protected)
mutated = replace_tag(protected, 0x0123456)
mutated_parsed = parse_protected_frame(mutated)
check("tag replacement preserves authentic payload", mutated_parsed.payload == parsed.payload)
check("tag replacement preserves transmitted freshness nibble", mutated_parsed.transmitted_freshness == parsed.transmitted_freshness)
check("tag replacement changes only requested tag28", mutated_parsed.tag28 == 0x0123456)
summary, rows = build_tag_guesses(0x2E4, protected, 0x100, 4)
check("tag-guess artifact binds SECOC-013", summary["finding_ids"] == ["SECOC-013"])
check("tag-guess mean work factor is 2^27", summary["mean_blind_work_factor"] == 134_217_728)
check("tag-guess preserves failure-freshness/no-lockout static facts",
      summary["firmware_static_properties"]["failed_mac_advances_freshness"] is False
      and summary["firmware_static_properties"]["recovered_per_source_failure_lockout"] is False)
check("candidate tags advance deterministically", [row["tag28"] for row in rows] == ["0x0000100", "0x0000101", "0x0000102", "0x0000103"])
check("candidate frames all preserve payload/freshness",
      all(parse_protected_frame(bytes.fromhex(row["frame"])).payload == parsed.payload
          and parse_protected_frame(bytes.fromhex(row["frame"])).transmitted_freshness == parsed.transmitted_freshness
          for row in rows))
check("tag range overflow rejected", rejects(lambda: build_tag_guesses(0x2E4, protected, TAG_MASK, 2)))
check("unbounded artifact generation rejected", rejects(lambda: build_tag_guesses(0x2E4, protected, 0, 65537)))

print("\n== CLI remains offline only ==")
probe = REPO / "exploit/followups/secoc_freshness_trials.py"
source = probe.read_text(encoding="utf-8")
check("freshness trial source has no Panda import", "from panda import" not in source and "import panda" not in source)
check("freshness trial source has no execute flag", "--execute" not in source)
cli = subprocess.run(
    [
        sys.executable,
        str(probe),
        "reset-replay",
        "--sync-frame",
        sync.hex(),
        "--protected",
        f"0x2e4:{protected.hex()}",
    ],
    cwd=REPO, capture_output=True, text=True, check=False,
)
check("reset-replay CLI emits offline plan", cli.returncode == 0 and '"operation": "reset_window_replay"' in cli.stdout and '"can_transmit_implemented": false' in cli.stdout)
alias_cli = subprocess.run(
    [
        sys.executable,
        str(probe),
        "fd-suffix-alias",
        "--base32", base32.hex(),
        "--suffix", (b"\xAA" * 16).hex(),
    ],
    cwd=REPO, capture_output=True, text=True, check=False,
)
check("FD alias CLI emits offline SECOC-014 plan", alias_cli.returncode == 0 and '"SECOC-014"' in alias_cli.stdout and '"physical_dlc": 48' in alias_cli.stdout)

with tempfile.TemporaryDirectory() as directory:
    candidates = Path(directory) / "guesses.ndjson"
    guess_cli = subprocess.run(
        [
            sys.executable,
            str(probe),
            "tag-guesses",
            "--can-id", "0x2e4",
            "--frame", protected.hex(),
            "--start", "0x20",
            "--count", "3",
            "--candidates-output", str(candidates),
        ],
        cwd=REPO, capture_output=True, text=True, check=False,
    )
    check("tag CLI writes exactly bounded candidate rows", guess_cli.returncode == 0 and len(candidates.read_text().splitlines()) == 3)

print(f"\nResults: {passed} passed, {failed} failed")
raise SystemExit(1 if failed else 0)
