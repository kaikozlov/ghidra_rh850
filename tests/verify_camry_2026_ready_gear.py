#!/usr/bin/env python3
"""Verify the retained 2026 Camry NRTD->READY and stationary gear captures."""
from __future__ import annotations

import gzip
import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
RAW = REPO / "targets/camry-2026/raw-20260826"
ART = REPO / "data/generated/camry_2026_ready_gear.json"
BUILD = REPO / "tools/analyze_camry_2026_ready_gear.py"
passed = failed = 0


def check(name: str, condition: object, detail: str = "") -> None:
  global passed, failed
  ok = bool(condition)
  passed += int(ok)
  failed += int(not ok)
  suffix = f" ({detail})" if detail else ""
  print(f"[{'PASS' if ok else 'FAIL'}][dynamic_trace] {name}{suffix}")


def sha(path: Path) -> str:
  return hashlib.sha256(path.read_bytes()).hexdigest()


art = json.loads(ART.read_text())

print("== source provenance ==")
expected = {
  "camry_ready_gear_capture.py": (774, "b79857ffa38f7ad94030313a5c5609cbd3e35178c31f8d72fa72a912c20740fb"),
  "camry_ready_gear_20260826.json.gz": (1660906, "379ec28fba65191d2898ebb156fe83e2e8e59c38bbf5fcfb7166ec9ff32c3889"),
  "camry_b_capture.py": (755, "2d72ec4ace3ab01ecae440d8d4f8324e3d7166a15f9bdd868d6a5c2d2a2ae153"),
  "camry_ready_b_20260826.json.gz": (715102, "7bae994dea1caff06d8f31f58558f67d646da38bd9531557875858eb33fa4db3"),
}
for name, (size, digest) in expected.items():
  p = RAW / name
  check(f"{name} exact tracked identity", p.stat().st_size == size and sha(p) == digest)
check("READY gear manifest pins missed-B first run and B repeat", "B had been missed" in (RAW / "READY_GEAR_MANIFEST.txt").read_text() and "D/B/D" in (RAW / "READY_GEAR_MANIFEST.txt").read_text())
for name, raw_size, raw_sha in (
  ("camry_ready_gear_20260826.json.gz", 16814179, "c03524036e531c22d60646be65c57b85fb1e9fb0c8b5d2c50e4b3055dbecef52"),
  ("camry_ready_b_20260826.json.gz", 7278095, "733b7a6fe9aa2f12401077489d662657a5abd20588c1d53a600ffbeec41b40f2"),
):
  raw = gzip.decompress((RAW / name).read_bytes())
  check(f"{name} uncompressed identity", len(raw) == raw_size and hashlib.sha256(raw).hexdigest() == raw_sha)

print("\n== passive capture boundary ==")
for name in ("camry_ready_gear_capture.py", "camry_b_capture.py"):
  src = (RAW / name).read_text()
  check(f"{name} uses can_recv", "can_recv" in src)
  check(f"{name} has no CAN transmit", "can_send" not in src and "can_send_many" not in src)
  check(f"{name} has no UDS/security path", all(x not in src for x in ("UdsClient", "SecurityAccess", "RoutineControl", "request_download", "0x27")))
check("artifact preserves observation-only boundary", art["capture_boundary"]["no_vehicle_control_transmission"] is True and "passive" in art["capture_boundary"]["operation"])

print("\n== deterministic artifact ==")
with tempfile.TemporaryDirectory() as td:
  out = Path(td) / "camry-ready-gear.json"
  proc = subprocess.run([sys.executable, str(BUILD), "--out", str(out)], cwd=REPO, capture_output=True, text=True, check=False)
  check("READY/gear analyzer succeeds", proc.returncode == 0, proc.stderr[-300:])
  check("READY/gear artifact regenerates exactly", proc.returncode == 0 and out.read_bytes() == ART.read_bytes())
check("schema is v1", art["schema"] == "camry-2026-ready-gear-v1")

print("\n== controlled Ready transition ==")
ready = art["ready_status"]
check("51E Ready sequence is 0->1", ready["first_run_sequence"] == [0, 1])
check("51E transition bytes/timing exact", ready["transition"] == [
  {"payload": "0000640000000000", "seconds": 0.070314, "value": 0},
  {"payload": "80006e0000000000", "seconds": 5.213083, "value": 1},
])
check("Ready causality strengthened but latency bounded", "logger was already running in NRTD" in ready["interpretation"] and "not machine-timestamped" in ready["interpretation"])

print("\n== full 0x127 gear enum ==")
gear = art["gear"]
check("first sequence P-R-N-D-N-R-P exact", gear["first_run_sequence"] == [0, 1, 2, 3, 2, 1, 0])
check("B repeat sequence exact", gear["second_run_sequence"] == [0, 3, 4, 3])
check("complete enum exact", gear["validated_enum"] == {"0": "P", "1": "R", "2": "N", "3": "D", "4": "B"})
check("first 0x127 checksum all valid", gear["checksum"]["first_run"] == {"frames": 3777, "matches": 3777})
check("B-run 0x127 checksum all valid", gear["checksum"]["b_run"] == {"frames": 1634, "matches": 1634})
p1 = gear["evidence"]["P_R_N_D_roundtrip"]
check("P/R/N/D transition times exact", [(x["seconds"], x["value"]) for x in p1] == [
  (0.016697, 0), (12.560082, 1), (14.443866, 2), (17.525321, 3), (21.129039, 2), (23.014504, 1), (25.192386, 0),
])
b = gear["evidence"]["B_roundtrip"]
check("D/B/D transition times exact", [(x["seconds"], x["value"]) for x in b] == [
  (0.020694, 0), (5.107709, 3), (9.480908, 4), (13.626834, 3),
])
check("B exact stable payload", b[2]["payload"] == "00100000004e8d1b")
check("gear interpretation closes Camry measurement only", "complete prior-art enum" in gear["interpretation"] and "cross-model" in gear["interpretation"])

print("\n== stationary corroboration ==")
for name, count in (("nrtd_to_ready_gear", 6187), ("ready_b", 2677)):
  wheels = art["captures"][name]["0x0AA_stationary_corroboration"]
  check(f"{name} stationary wheel carrier exact", wheels["frame_count"] == count and wheels["unique_payloads"] == ["1a6f1a6f1a6f1a6f"])

print("\n== documentation ==")
doc = (REPO / "docs/variants/camry-2026-live-baseline.md").read_text()
for token in ("VAR-053", "P=0", "R=1", "N=2", "D=3", "B=4", "5.213083", "9.480908"):
  check(f"Camry report preserves {token}", token in doc)
check("production boundary remains read-only", "Production output remains disabled" in doc and "does not authorize" in doc)

print(f"\nResults: {passed} passed, {failed} failed")
raise SystemExit(1 if failed else 0)
