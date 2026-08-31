#!/usr/bin/env python3
"""Verify the retained Camry native-Bus-1 E2E integrity/freshness shape."""
from __future__ import annotations

import gzip
import json
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
ART = REPO / "data/generated/camry_2026_bus1_e2e.json"
BUILD = REPO / "tools/analyze_camry_2026_bus1_e2e.py"

passed = failed = 0


def make_crc16_table() -> tuple[int, ...]:
    table = []
    for value in range(256):
        crc = value << 8
        for _ in range(8):
            crc = ((crc << 1) & 0xFFFF) ^ (0x1021 if crc & 0x8000 else 0)
        table.append(crc)
    return tuple(table)


CRC16_TABLE = make_crc16_table()


def crc16_ccitt_independent(data: bytes) -> int:
    """Independent table implementation of the recovered Profile-5 CRC."""
    crc = 0xFFFF
    for value in data:
        crc = ((crc << 8) & 0xFFFF) ^ CRC16_TABLE[((crc >> 8) ^ value) & 0xFF]
    return crc


def check(name: str, cond, detail: str = "") -> None:
    global passed, failed
    ok = bool(cond)
    passed += int(ok)
    failed += int(not ok)
    print(f"[{'PASS' if ok else 'FAIL'}] {name}" + (f" ({detail})" if detail else ""))


art = json.loads(ART.read_text())
check("schema", art["schema"] == "camry-2026-bus1-e2e-v2")

print("== deterministic regeneration ==")
with tempfile.TemporaryDirectory() as td:
    out = Path(td) / ART.name
    proc = subprocess.run(
        [sys.executable, str(BUILD), "--out", str(out)],
        cwd=REPO,
        capture_output=True,
        text=True,
        check=False,
    )
    check("analyzer succeeds", proc.returncode == 0, proc.stderr[-300:])
    check("artifact regenerates byte-exact", proc.returncode == 0 and out.read_bytes() == ART.read_bytes())

expected = {
    "drive_a": {
        "sha": "be0c02946818fafc48b7d3e2be5d2fde31d796e057ab29d8bf59a879c7553db5",
        "x160_n": 20510,
        "pairs": 20501,
        "plus1": 20351,
        "plus1_fraction": 0.992683284,
        "020_n": 10270,
        "020_recur": 12.802331357,
    },
    "drive_b": {
        "sha": "641eee57eaffc579002708185178ea08c189155527354712dd43a1f0e309bb3a",
        "x160_n": 23998,
        "pairs": 23988,
        "plus1": 23988,
        "plus1_fraction": 1.0,
        "020_n": 11999,
        "020_recur": 12.802446447,
    },
}

for label, e in expected.items():
    d = art["drives"][label]
    x = d["periodic_streams"]["0x160/32"]
    c = d["0x160_counter"]
    c020 = d["0x020_control"]
    print(f"== {label} ==")
    check(f"{label}: raw route identity", d["source_sha256"] == e["sha"])
    check(f"{label}: 0x160 frame count", x["n"] == e["x160_n"])
    check(f"{label}: 0x160 B0:B1 affine model has zero conflicts", x["affine_conflicts"] == 0)
    check(f"{label}: identical visible suffix never has two integrity words",
          x["suffix_determinism"]["suffixes_with_multiple_headers"] == 0
          and x["suffix_determinism"]["max_headers_per_suffix"] == 1)
    check(f"{label}: 0x160 trailing four bytes remain zero", x["last4_histogram"] == {"00000000": e["x160_n"]})
    check(f"{label}: 0x160 B2 rolling counter", c["pairs"] == e["pairs"] and c["plus1"] == e["plus1"]
          and c["plus1_fraction"] == e["plus1_fraction"])
    check(f"{label}: 0x020 has exactly 256 complete wire images", c020["unique_full_frames"] == 256
          and c020["counter_values"] == 256)
    check(f"{label}: 0x020 integrity map is exactly affine over all counter pairs",
          c020["affine_pair_tests"] == 65536 and c020["affine_pair_violations"] == 0)
    check(f"{label}: 0x020 byte-exact frame repeats after counter wrap",
          abs(c020["exact_frame_recurrence_s_median"] - e["020_recur"]) < 1e-9)

print("== all periodic native-Bus-1 streams ==")
for label, d in art["drives"].items():
    streams = d["periodic_streams"]
    check(f"{label}: 22 periodic streams retained", len(streams) == 22)
    check(f"{label}: every periodic stream has zero affine conflicts",
          all(s["affine_conflicts"] == 0 for s in streams.values()))
    check(f"{label}: every periodic stream is deterministic for identical visible suffix",
          all(s["suffix_determinism"]["suffixes_with_multiple_headers"] == 0 for s in streams.values()))
    check(f"{label}: every periodic frame matches exact Profile-5 generator",
          all(s["profile5_matches"] == s["n"] and s["profile5_mismatches"] == 0 for s in streams.values()))
    check(f"{label}: first/last wire images independently recover DataID=CAN ID",
          all(s["profile5_recovered_data_ids_first_last"] == [f"0x{int(name.split('/')[0], 16):04X}"] * 2
              for name, s in streams.items()))

print("== exact AUTOSAR E2E Profile 5 recovery ==")
p05 = art["exact_profile5"]
check("profile identified as AUTOSAR E2E Profile 5", p05["profile"] == "AUTOSAR E2E Profile 5")
check("CRC-16/CCITT parameters recovered",
      p05["crc"] == {
          "width_bits": 16,
          "polynomial": "0x1021",
          "initial_value": "0xFFFF",
          "xorout": "0x0000",
          "reflected_input": False,
          "reflected_output": False,
          "wire_storage": "little-endian B0:B1",
      })
check("Profile-5 counter/offset recovered",
      p05["offset_bytes"] == 0 and p05["counter"] == {"byte": 2, "width_bits": 8, "wrap": 256})
check("implicit Data ID is CAN ID in little-endian append order",
      p05["implicit_data_id"] == {
          "width_bits": 16,
          "value": "CAN ID",
          "crc_append_order": "low byte, then high byte",
      })
check("all 438,380 retained periodic frames match exact generator",
      p05["frames"] == 438380 and p05["matches"] == 438380 and p05["mismatches"] == 0)

# Reparse the raw routes and recompute the checksum independently of the analyzer/helper.
independent_frames = independent_mismatches = 0
for label, drive in art["drives"].items():
    periodic = {
        (int(key.split("/")[0], 16), int(key.split("/")[1]))
        for key in drive["periodic_streams"]
    }
    with gzip.open(REPO / drive["source"], "rt") as f:
        for line in f:
            _seg, _t, src, addr, hx = json.loads(line)
            frame = bytes.fromhex(hx)
            if src != 1 or (addr, len(frame)) not in periodic:
                continue
            independent_frames += 1
            stored = int.from_bytes(frame[:2], "little")
            expected_crc = crc16_ccitt_independent(
                frame[2:] + bytes((addr & 0xFF, (addr >> 8) & 0xFF))
            )
            independent_mismatches += stored != expected_crc
check("independent raw-route recomputation covers 438,380 frames",
      independent_frames == 438380, str(independent_frames))
check("independent raw-route Profile-5 recomputation has zero mismatches",
      independent_mismatches == 0, str(independent_mismatches))

print("== 0x160 recoverable integrity deltas ==")
x = art["combined_0x160"]
check("combined 0x160 count/rank/conflicts", x["frames"] == 44508 and x["affine_rank"] == 111 and x["affine_conflicts"] == 0)
h = x["heldout_prediction"]
check("1/5 training predicts essentially all held-out frames exactly",
      h == {"stride": 5, "train_frames": 8902, "train_rank": 110, "train_conflicts": 0,
            "holdout_frames": 35606, "covered": 35605, "correct": 35605})
check("0x160 B2 checksum deltas recovered for all 8 counter bits",
      x["B2_checksum_xor_contribution_by_bit0_to_7"] ==
      ["0x4659", "0x8CB2", "0x3975", "0x72EA", "0xC5C4", "0xAB99", "0x7723", "0xEE46"])
check("0x160 B12 checksum deltas recovered for every used signed7 bit",
      x["B12_checksum_xor_contribution_by_bit0_to_7"] ==
      ["0xD86D", "0xB0DB", "0x41A7", "0xA35E", "0x46BD", "0xAD6A", "0x5AD5", None]
      and x["B12_used_bits"] == list(range(7)))

print("== common-code / Data-ID witnesses ==")
w = art["common_code_witnesses"]
vals = list(w["dlc32_B2_contributions"].values())
check("DLC32 0x160/0x440/0x450 share the identical B2->integrity transform",
      len(vals) == 3 and vals[0] == vals[1] == vals[2])
ids = w["same_suffix_id_bit0"]
check("same CAN-ID bit change produces same fixed header XOR on two 64-byte pairs",
      len(ids) == 2 and all(r["header_xor_histogram"] == {"0x3133": r["overlapping_suffixes"]} for r in ids)
      and ids[0]["overlapping_suffixes"] == 257 and ids[1]["overlapping_suffixes"] == 256)

print("== interpretation boundary ==")
interp = art["interpretation"]
check("integrity identified as exact Profile-5 CRC rather than cryptographic MAC",
      "AUTOSAR E2E Profile 5" in interp["integrity"] and "0x1021" in interp["integrity"]
      and "cryptographic MAC" in interp["integrity"])
check("receiver counter window remains unproved", "do not prove" in interp["freshness"])
check("wire replay boundary records 8-bit wrap", "256 complete wire images" in interp["replay_boundary"])
check("producer/acceptance remain bounded", "does not identify" in interp["security_boundary"] and "acceptance" in interp["security_boundary"])

print(f"Summary: {passed} passed, {failed} failed")
raise SystemExit(1 if failed else 0)
