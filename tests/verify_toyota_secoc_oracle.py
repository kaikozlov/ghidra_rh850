#!/usr/bin/env python3
"""Verify the generic Toyota classic-CAN SecOC capture/dump oracle."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from tools.toyota_secoc_oracle import (
    ProtectedSample,
    SyncSample,
    candidate_message_counters,
    decode_protected_frame,
    decode_sync_frame,
    known_protected_ids,
    load_capture,
    load_profile,
    scan_dump,
    verify_key,
    verify_protected_sample,
    verify_sync_sample,
)
from tools.toyota_secoc_signer import sign_classic_frame, sign_sync_frame

passed = failed = 0


def check(name: str, condition: object, detail: str = "") -> None:
    global passed, failed
    ok = bool(condition)
    passed += int(ok)
    failed += int(not ok)
    suffix = f" ({detail})" if detail else ""
    print(f"[{'PASS' if ok else 'FAIL'}] {name}{suffix}")


KEY = bytes.fromhex("00112233445566778899aabbccddeeff")
WRONG_KEY = bytes.fromhex("ffeeddccbbaa99887766554433221100")
TRIP = 0x4321
RESET = 0x34567
BUS = 1

print("== profile ==")
profile = load_profile()
ids = {entry.can_id for entry in profile}
check("profile has one synchronization entry", sum(entry.kind == "sync" for entry in profile) == 1)
check("profile synchronization ID is 0x00F", next(entry.can_id for entry in profile if entry.kind == "sync") == 0x00F)
check("profile includes Corolla-observed 0x116", 0x116 in ids)
check("profile includes Corolla-observed 0x24D", 0x24D in ids)
check("profile includes steering 0x131", 0x131 in ids)
check("profile includes steering 0x2E4", 0x2E4 in ids)
check("profile includes PRE_COLLISION_2 0x344", 0x344 in ids)
check("known protected set excludes synchronization", 0x00F not in known_protected_ids())
check("known protected set has eight IDs", len(known_protected_ids()) == 8)

print("\n== frame decoding and verification ==")
sync_bytes = sign_sync_frame(KEY, TRIP, RESET)
trip, reset, sync_auth = decode_sync_frame(sync_bytes)
sync_sample = SyncSample(BUS, trip, reset, sync_auth)
check("sync decode preserves trip", trip == TRIP)
check("sync decode preserves reset", reset == RESET)
check("correct key verifies sync", verify_sync_sample(KEY, sync_sample))
check("wrong key rejects sync", not verify_sync_sample(WRONG_KEY, sync_sample))

frame_116 = sign_classic_frame(KEY, 0x116, bytes.fromhex("10203040"), TRIP, RESET, 0xA5)
payload, nibble, auth = decode_protected_frame(frame_116)
sample_116 = ProtectedSample(BUS, 0x116, payload, nibble, auth, TRIP, RESET)
check("protected decode preserves payload", payload == bytes.fromhex("10203040"))
check("transmitted nibble restricts message counter to 64 values", len(tuple(candidate_message_counters(sample_116))) == 64)
check("candidate set contains actual full message counter", 0xA5 in candidate_message_counters(sample_116))
ok, recovered_counter = verify_protected_sample(KEY, sample_116)
check("correct key verifies protected 0x116", ok)
check("verified message counter respects full counter", recovered_counter == 0xA5, str(recovered_counter))
check("wrong key rejects protected 0x116", not verify_protected_sample(WRONG_KEY, sample_116)[0])

print("\n== capture is bus-agnostic and ID-generic ==")
frame_24d = sign_classic_frame(KEY, 0x24D, bytes.fromhex("a1b2c3d4"), TRIP, RESET, 0x3E)
frame_2e4 = sign_classic_frame(KEY, 0x2E4, bytes.fromhex("01020304"), TRIP, RESET, 0x22)
with tempfile.TemporaryDirectory() as td:
    root = Path(td)
    capture = root / "capture.ndjson"
    rows = [
        {"addr": 0x0F, "bus": BUS, "data": sync_bytes.hex()},
        {"addr": 0x116, "bus": BUS, "data": frame_116.hex()},
        {"addr": 0x24D, "bus": BUS, "data": frame_24d.hex()},
        # Another known protected ID is intentionally on a different bus with no
        # sync state. It must not contaminate the bus-1 oracle.
        {"addr": 0x2E4, "bus": 2, "data": frame_2e4.hex()},
        {"addr": 0x123, "bus": BUS, "data": "0000000000000000"},
    ]
    capture.write_text("\n".join(json.dumps(row) for row in rows) + "\n", encoding="utf-8")

    sync_samples, protected_samples, summary = load_capture(capture)
    check("collector accepts synchronization on bus 1", len(sync_samples) == 1 and sync_samples[0].bus == 1)
    check("collector accepts 0x116 without steering IDs", any(s.can_id == 0x116 for s in protected_samples))
    check("collector accepts 0x24D without steering IDs", any(s.can_id == 0x24D for s in protected_samples))
    check("orphan 0x2E4 is not falsely associated across buses", all(s.can_id != 0x2E4 for s in protected_samples))
    check("orphan summary records bus-2 0x2E4", summary["orphan_protected"].get("bus2:0x2E4") == 1)

    result = verify_key(KEY, sync_samples, protected_samples)
    check("generic verifier matches all synchronization samples", result["sync"] == {"matches": 1, "total": 1})
    check("generic verifier matches Corolla-observed 0x116", result["protected"]["0x116"] == {"matches": 1, "total": 1})
    check("generic verifier matches Corolla-observed 0x24D", result["protected"]["0x24D"] == {"matches": 1, "total": 1})

    wrong = verify_key(WRONG_KEY, sync_samples, protected_samples)
    check("wrong key has zero sync matches", wrong["sync"]["matches"] == 0)
    check("wrong key has zero protected matches", all(v["matches"] == 0 for v in wrong["protected"].values()))

    print("\n== sliding-window dump scan ==")
    key_offset = 73
    dump = bytearray((i * 37 + 11) & 0xFF for i in range(256))
    dump[key_offset:key_offset + 16] = KEY
    matches = scan_dump(bytes(dump), sync_samples, protected_samples, min_entropy=0.0, sync_probes=1)
    check("sliding scan finds unaligned key", any(match["offset"] == key_offset for match in matches), str(matches))
    found = next(match for match in matches if match["offset"] == key_offset)
    check("scan result records all sync matches", found["verification"]["sync"] == {"matches": 1, "total": 1})
    check("scan result records 0x116 match", found["verification"]["protected"]["0x116"]["matches"] == 1)
    check("scan result records 0x24D match", found["verification"]["protected"]["0x24D"]["matches"] == 1)
    check("scan result exposes hash, not raw key", "sha256" in found and "key" not in found)

    print("\n== command-line profile ==")
    cli = subprocess.run(
        [sys.executable, str(REPO / "tools" / "toyota_secoc_oracle.py"), "profile"],
        capture_output=True,
        text=True,
        check=False,
        cwd=REPO,
    )
    check("profile CLI exits successfully", cli.returncode == 0, cli.stderr.strip())
    cli_profile = json.loads(cli.stdout)
    check("profile CLI exposes 0x116", any(row["can_id"] == 0x116 for row in cli_profile))
    check("profile CLI exposes 0x24D", any(row["can_id"] == 0x24D for row in cli_profile))

print(f"\n== RESULT: {passed} passed, {failed} failed ==")
if failed:
    raise SystemExit(1)
