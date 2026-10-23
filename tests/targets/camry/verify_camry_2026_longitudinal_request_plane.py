#!/usr/bin/env python3
"""Verify Camry request-plane decoding against retained raw CAN observations."""
from __future__ import annotations

import bisect
import gzip
import hashlib
import json
import subprocess
import sys
import tempfile
from collections import Counter
from pathlib import Path

from tools import REPO_ROOT
from tools.targets.camry.analysis.analyze_camry_2026_longitudinal_request_plane import request_summary

REPO = REPO_ROOT
ART = REPO / "data/generated/camry_2026_longitudinal_request_plane.json"
BUILD = REPO / "tools/targets/camry/analysis/analyze_camry_2026_longitudinal_request_plane.py"
passed = failed = 0


def check(name: str, condition, detail: str = "") -> None:
  global passed, failed
  ok = bool(condition)
  passed += int(ok)
  failed += int(not ok)
  print(f"[{'PASS' if ok else 'FAIL'}] {name}" + (f" ({detail})" if detail else ""))


def decimal_counts(values) -> dict[str, int]:
  return {str(k): v for k, v in sorted(Counter(values).items())}


art = json.loads(ART.read_text())
with tempfile.TemporaryDirectory() as td:
  out = Path(td) / ART.name
  proc = subprocess.run([sys.executable, str(BUILD), "--output", str(out)], cwd=REPO,
                        capture_output=True, text=True, check=False)
  check("analyzer succeeds", proc.returncode == 0, proc.stderr[-300:])
  check("artifact regenerates byte-exact", proc.returncode == 0 and out.read_bytes() == ART.read_bytes())

for label, drive in art["drives"].items():
  source = REPO / drive["source"]["path"]
  check(f"{label}: source identity", hashlib.sha256(source.read_bytes()).hexdigest() == drive["source"]["sha256"])
  request_rows, result_rows = [], []
  with gzip.open(source, "rt") as stream:
    for line in stream:
      _, timestamp, bus, address, payload = json.loads(line)
      data = bytes.fromhex(payload)
      if address == 0x08A and bus == 2 and len(data) == 32:
        request_rows.append((timestamp, data))
      elif address == 0x081 and bus == 0 and len(data) == 32:
        result_rows.append((timestamp, data))
  payloads = [data for _, data in request_rows]
  request = drive["request_0x08A"]
  checksum = request["byte7_checksum"]
  # Sum individual address bytes and the original eight-byte length, not DLC32.
  expected = [(0x8A + 0x00 + 8 + sum(data[0:7])) % 256 for data in payloads]
  mismatches = sum(data[7] != value for data, value in zip(payloads, expected))
  check(f"{label}: every native B7 satisfies Toyota checksum",
        bool(payloads) and mismatches == 0
        and checksum["checked_frames"] == len(payloads)
        and checksum["matching_frames"] == len(payloads)
        and checksum["mismatch_frames"] == mismatches)
  raw_counts = {f"0x{k:02X}": v for k, v in sorted(Counter(data[7] for data in payloads).items())}
  check(f"{label}: checksum census preserves raw bytes",
        checksum["observed_counts"] == raw_counts == checksum["expected_counts"])
  b6 = request["b6_request_state"]
  check(f"{label}: B6-only request state census",
        b6["request_id_counts"] == decimal_counts(data[6] >> 2 for data in payloads)
        and b6["allocation_method_counts"] == decimal_counts(data[6] & 3 for data in payloads))
  words = request["longitudinal_acceleration_words"]
  for offset in (8, 11):
    values = [int.from_bytes(data[offset:offset + 2], "big", signed=True) for data in payloads]
    check(f"{label}: signed acceleration slot B{offset}:B{offset + 1}",
          words[f"B{offset}_B{offset + 1}"]["signed16_raw_range"] == [min(values), max(values)]
          and words[f"B{offset}_B{offset + 1}"]["scale_mps2_per_count"] == 0.001)
  check(f"{label}: acceleration equality measured directly",
        words["equal_frames"] == sum(data[8:10] == data[11:13] for data in payloads))

  result_times = [timestamp for timestamp, _ in result_rows]
  stable_ids = []
  for index, (timestamp, data) in enumerate(request_rows):
    low, high = max(0, index - 4), min(len(request_rows), index + 5)
    if data[6] != 0 or high - low < 5 or any(row[1][6] != 0 for row in request_rows[low:high]):
      continue
    pos = bisect.bisect_left(result_times, timestamp)
    candidates = [j for j in (pos - 1, pos) if 0 <= j < len(result_rows)]
    if candidates:
      nearest = min(candidates, key=lambda j: abs(result_times[j] - timestamp))
      if abs(result_times[nearest] - timestamp) <= 60_000_000:
        stable_ids.append(result_rows[nearest][1][6] & 63)
  context = drive["b6_zero_context"]["result_state"]
  check(f"{label}: stable context selection depends on B6, not checksum",
        context["stable_pair_count"] == len(stable_ids)
        and context["result_id_counts"] == decimal_counts(stable_ids))

  relation = drive["result_0x081"]["longitudinal_result_id_candidate"]["relation_to_b6_request_id"]
  times = [timestamp for timestamp, _ in request_rows]
  paired = []
  for timestamp, result in result_rows:
    pos = bisect.bisect_right(times, timestamp) - 1
    if pos >= 0 and timestamp - times[pos] <= 60_000_000:
      paired.append((request_rows[pos][1], result))
  check(f"{label}: result comparison uses B6 only",
        relation["selected_equals_B6_frames"] == sum((result[6] & 63) == (data[6] >> 2) for data, result in paired)
        and relation["selected_63_absent_from_B6_frames"] == sum((result[6] & 63) == 63 and (data[6] >> 2) != 63 for data, result in paired))

# Alter real retained frames to exercise checksum boundaries, not canned output.
original = payloads[0]
for offset in range(7):
  altered = bytearray(original)
  altered[offset] ^= 1
  decoded = request_summary([(0, bytes(altered))])
  check(f"checksum detects header B{offset} change", decoded["byte7_checksum"]["mismatch_frames"] == 1)
  altered[7] = (0x8A + 8 + sum(altered[:7])) & 255
  repaired = request_summary([(0, bytes(altered))])
  check(f"checksum recomputation covers B{offset}", repaired["byte7_checksum"]["matching_frames"] == 1)
for offset in (8, 11, 21, 28, 31):
  altered = bytearray(original)
  altered[offset] ^= 1
  decoded = request_summary([(0, bytes(altered))])
  check(f"legacy checksum excludes payload B{offset}", decoded["byte7_checksum"]["matching_frames"] == 1)

hold = art["hold_request_semantics"]
upstream = json.loads((REPO / hold["source"]["path"]).read_text())
raw_pairs, hold_pairs = Counter(), Counter()
hold_frames = bit5_frames = 0
for route in ("3b", "3c"):
  state = upstream["routes"][route]["stock_acc_standstill_candidate"]
  raw_pairs.update(state["raw_b6_b7_pair_counts"])
  hold_frames += state["frames"]
  bit5_frames += state["b4_bit5_set_frames_with_cruise_latch"]
  for episode in state["episodes"]:
    hold_pairs.update(episode["raw_b6_b7_pair_counts"])
check("hold source observations preserved without checksum ID decoding",
      hold["route_3b_3c_pair_counts"] == dict(raw_pairs)
      and hold["hold_episode_pair_counts"] == dict(hold_pairs)
      and hold["hold_episode_frames"] == hold_frames
      and hold["structural_hold_state"]["set_frames_with_cruise_latch"] == bit5_frames)

print(f"Summary: {passed} passed, {failed} failed")
raise SystemExit(1 if failed else 0)
