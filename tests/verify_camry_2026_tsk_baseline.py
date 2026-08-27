#!/usr/bin/env python3
"""Verify the tracked maintainer-operated 2026 Camry TSK/CAN baseline."""
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
ART = REPO / "data/generated/camry_2026_tsk_baseline.json"
BUILD = REPO / "tools/analyze_camry_2026_baseline.py"
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
  "can_oracle.ndjson.gz": (3265598, "db47d483016c409b5c3a1ecdf58310f68ca8105a4c16eae54185016a6eaf3f41"),
  "identity.json": (1559, "5feffa176a0a0293de53fee91486788c577d603ad72cc6e93064dd3710cad234"),
  "programming_probe.json": (2135, "c8dec4197585622a511a03a629e44b2b69369ce3b5b7978a584dfa5e4fa27817"),
  "xcp_probe.json": (702, "b8d96ae5cb97f18d1138196e2a0cb95de5938ec0ff7e512ee9f752f86645e273"),
}
for name, (size, digest) in expected.items():
  p = RAW / name
  check(f"{name} exact tracked identity", p.stat().st_size == size and sha(p) == digest)
raw = gzip.decompress((RAW / "can_oracle.ndjson.gz").read_bytes())
check("uncompressed CAN oracle exact identity", len(raw) == 37628790 and hashlib.sha256(raw).hexdigest() == "7c7b72b11a7a76f3059d63fba5b34f7a6177f8b9d51229e6209df7304b364147")

print("\n== deterministic generated artifact ==")
with tempfile.TemporaryDirectory() as td:
  out = Path(td) / "camry.json"
  proc = subprocess.run([sys.executable, str(BUILD), "--out", str(out)], cwd=REPO, capture_output=True, text=True, check=False)
  check("baseline analyzer succeeds", proc.returncode == 0, proc.stderr[-300:])
  check("baseline artifact regenerates exactly", proc.returncode == 0 and out.read_bytes() == ART.read_bytes())
check("schema is v1", art["schema"] == "camry-2026-tsk-baseline-v1")
check("vehicle attribution stays external to wire facts", art["vehicle_attribution"]["vehicle"] == "2026 Toyota Camry" and "operator context" in art["vehicle_attribution"]["boundary"])

print("\n== exact identity and route ==")
ident = art["identity"]
check("exact two-record F181", ident["f181_records"] == ["8965F3307000", "8A3113303100"])
check("exact ECU serial", ident["ecu_serial"] == "8965033K9011J2740743")
check("normal-harness bus1 7A1/7A9 route", ident["route"] == {"elm327_param": 1, "eps_bus": 1, "eps_rx": "0x7a9", "eps_rx_bus": 1, "eps_tx": "0x7a1", "semantic_path": "normal-harness"})
check("F181 is new to prior corpus", ident["exact_f181_known_in_prior_repo_corpus"] is False)

print("\n== programming and XCP boundary ==")
prog = art["programming"]
check("PROGRAMMING handoff entered and route preserved", prog["status"] == "entered" and prog["handoff_switched"] and prog["route_preserved"])
check("boot F181 is two bang placeholders", prog["bootloader_f181_is_two_bang_placeholders"] and bytes.fromhex(prog["bootloader_f181_hex"]) == b"\x02" + b"!" * 32)
check("RAM-exec transfer remains unclaimed", all(x in prog["boundary"] for x in ("not established", "must not be inferred")))
xcp = art["xcp"]
check("tested XCP route is negative", xcp["status"] == "unreachable" and xcp["request_id"] == "0x7f7" and xcp["response_id"] == "0x7f8" and xcp["connect_response"] == "")
check("XCP negative remains route/session bounded", "not a universal physical absence proof" in xcp["boundary"])

print("\n== TSS3 CAN topology ==")
can = art["can_capture"]
check("capture is approximately one minute", 59.98 < can["duration_s"] < 60.01)
check("bus stream census is exact", can["stream_count_by_bus"] == {"0": 22, "1": 179, "2": 22})
check("bus0/bus2 share exact 22-ID/DLC set", can["bus0_bus2_same_id_dlc_set"] and can["bus0_bus2_stream_count"] == 22)
check("only 189 payload sequence differs across bus0/bus2", can["bus0_bus2_payload_sequence_unequal"] == ["0x189/64"])
check("classic 131/2E4 steering is absent", can["legacy_steering_commands_absent"] and can["legacy_steering_counts"] == {"0x131/8": 0, "0x2E4/8": 0})
check("B6 absent only in non-LTA segment", can["b6_absent_in_stationary_ready_segment"] and "stock-LTA" in can["b6_absence_boundary"] and "segment-level negative" in can["b6_absence_boundary"])
streams = can["selected_streams"]
for key, expected_count in (("0x00F/8", 619), ("0x025/32", 6188), ("0x030/32", 6188), ("0x090/32", 6187), ("0x0D7/32", 3094), ("0x0AA/8", 6187), ("0x101/8", 3095), ("0x116/8", 2627), ("0x127/8", 3777), ("0x176/8", 1949), ("0x51E/8", 61)):
  check(f"{key} retained count", streams[key]["count"] == expected_count and streams[key]["bus"] == 1)
check("H/F auxiliary Tx set absent in this segment", all(streams[x]["count"] == 0 for x in ("0x351/4", "0x394/3", "0x4A3/8", "0x4C8/8")))

print("\n== H/F wire-format transfer ==")
hf = art["hf_transfer_observations"]
check("classification does not overclaim Camry firmware equivalence", "wire-format transfer" in hf["classification"] and "unproved without CodeFlash" in hf["classification"])
f030 = hf["0x030"]
check("030 additive rule matches every frame", f030["frame_count"] == f030["additive_rule_matches"] == 6188 and "+ 0x38" in f030["additive_rule"])
check("030 torque is dynamic/plausible", f030["steering_wheel_torque_nm"] == {"count": 6188, "max": 1.8, "min": -1.75, "unique_count": 143})
check("030 candidate fault/inhibit bit stays clear", f030["b6_status_values"]["b6_bit2"] == [0])
check("030 invalid candidate clears early", f030["b6_status_transitions"]["b6_bit0"][:2] == [{"seconds": 0.01764, "value": 1}, {"seconds": 0.201959, "value": 0}])
f025 = hf["0x025"]
check("025 steering layout decodes coherent dynamic values", f025["steering_angle_deg"]["min"] == -12.0 and f025["steering_angle_deg"]["max"] == 19.5 and f025["steering_rate_raw_or_prior_art_deg_s"]["min"] == -80 and f025["steering_rate_raw_or_prior_art_deg_s"]["max"] == 70)
for addr, count in (("0x101", 3095), ("0x127", 3777), ("0x176", 1949)):
  c = hf["legacy_checksum_carriers"][addr]
  check(f"{addr} Toyota checksum all valid", c["frames"] == c["checksum_matches"] == count)
check("127 raw0 P candidate is bounded", hf["0x127"]["gear_raw_values"] == [0] and "prior-art-compatible with P" in hf["0x127"]["interpretation"] and "transition validation remains required" in hf["0x127"]["interpretation"])
ready = hf["0x51E"]
check("51E Ready wire exercises 0->1", ready["ready_values"] == [0, 1] and [x["value"] for x in ready["transition_timeline"][:2]] == [0, 1])
check("51E Ready transition timing is exact", ready["transition_timeline"][0] == {"payload": "0000610000000000", "seconds": 0.01764, "value": 0} and ready["transition_timeline"][1] == {"payload": "8000610000000000", "seconds": 0.994317, "value": 1})
check("Ready interpretation retains causal boundary", "strongly corroborating" in ready["interpretation"] and "not independently recorded" in ready["interpretation"])

print("\n== documentation ==")
doc = (REPO / "docs/variants/camry-2026-live-baseline.md").read_text()
for token in ("8965F3307000", "8A3113303100", "0x7A1", "0x7A9", "0x030", "0x51E", "0x0B6", "Ready Status"):
  check(f"variant report preserves {token}", token in doc)
check("report preserves firmware-transfer boundary", "not a Camry CodeFlash analysis" in doc and "Production output remains disabled" in doc)

print(f"\nResults: {passed} passed, {failed} failed")
raise SystemExit(1 if failed else 0)
