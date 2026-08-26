#!/usr/bin/env python3
"""Verify the maintainer-operated 2026 Camry NRTD P5/cruise evidence."""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
RAW = REPO / "community/kai/camry-2026/raw-20260826"
ART = REPO / "data/generated/camry_2026_nrtd_p5.json"
BUILD = REPO / "tools/analyze_camry_2026_nrtd_p5.py"
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
  "camry_nrtd_module_identity_20260826.json": (5398, "0ed09e5abec3a555d9e8b26c03a740747f04675859de8d12f49c8afb0eb53bdd"),
  "camry_nrtd_p5_oracles_20260826.json": (1179, "17d9870cc65f71c9890389a22fa3f0f9561ec3d4f2679cc9e61076ed6977bcba"),
  "camry_nrtd_p5_oracles_extra_20260826.json": (586, "4a59d82a2f027b5d6413bf6608905503975afa40ce87dfa350b36e8459da62f6"),
  "camry_nrtd_brake_107e_extended_20260826.json": (281, "3475f1df52cf69fc56fea51cdaa85cc00797cd720e3583e29d0aaa7b1b80af2c"),
  "camry_nrtd_cruise_buttons_20260826.json": (72108, "1977d05439f632017369d761641726536b635cc95b66cd5d5079af8096f4877e"),
  "camry_nrtd_cruise_MAIN_20260826.json": (35980, "ca7c3911e402a763f23af00c92f449c75afa8c8b0e94b10293b710aad95d337b"),
  "camry_nrtd_cruise_RESPLUS_20260826.json": (35882, "1d176f20e9c2b11e46ebe6d069c1d653dd3026a3f4895dde85730f9742e1ce07"),
  "camry_nrtd_cruise_SETMINUS_20260826.json": (35881, "f9ea74fd5846222d38884183c12eb19ec20fd80c6730f21dc1bcd5a377efa9aa"),
  "camry_nrtd_cruise_CANCEL_20260826.json": (35884, "432fc309de02bfdd4f5927af6928382cf0f0617f68258484eabac05f3fb06111"),
  "camry_nrtd_cruise_DISTANCE_20260826.json": (35862, "024f1df8b783da1b4d1485b824bf3092ea412c112efb2f12ad2ebdbf4cfddcdb"),
  "camry_nrtd_cruise_can_sync_20260826.json.gz": (1103765, "083435105745d928ceea5dea2a614b7a1fbd32341ba4c94987c73ef6287e87fa"),
}
for name, (size, digest) in expected.items():
  p = RAW / name
  check(f"{name} exact tracked identity", p.stat().st_size == size and sha(p) == digest)
manifest = (RAW / "NRTD_MANIFEST.txt").read_text()
check("NRTD manifest pins every raw source", all(name in manifest and digest in manifest for name, (_, digest) in expected.items()))
check("NRTD manifest preserves read-only boundary", all(x in manifest for x in ("Not Ready to Drive", "No SecurityAccess key, RoutineControl start, write, reset, download", "vehicle-control transmission", "separate from MANIFEST.txt")))

print("\n== deterministic generated artifact ==")
with tempfile.TemporaryDirectory() as td:
  out = Path(td) / "camry_nrtd.json"
  proc = subprocess.run([sys.executable, str(BUILD), "--out", str(out)], cwd=REPO, capture_output=True, text=True, check=False)
  check("NRTD analyzer succeeds", proc.returncode == 0, proc.stderr[-300:])
  check("NRTD artifact regenerates exactly", proc.returncode == 0 and out.read_bytes() == ART.read_bytes())
check("schema is v1", art["schema"] == "camry-2026-nrtd-p5-v1")
check("vehicle state is explicitly NRTD/stationary", "Not Ready to Drive" in art["vehicle_state"] and "stationary" in art["vehicle_state"])

print("\n== exact P5 module identities ==")
mods = art["module_identity"]
frc = mods["FRC_P5"]
brake = mods["Brake_EPB_category_435"]
check("normal-harness ELM param1 retained", mods["elm327_param"] == 1)
check("FRC route and exact F181", frc["bus"] == 1 and frc["tx"] == "0x792" and frc["rx"] == "0x79A" and frc["f181"] == "8646F3315000")
check("FRC exact supporting identities", frc["f18c_serial"] == "TN69400026030404235J" and frc["ecu_part_0105"] == "8646C06091" and frc["swin_1fff"] == "06000000000000000000")
check("FRC direct route is bus1-only in bounded sweep", frc["bus0_bus2_f181_timeout"] is True)
check("Brake/EPB route and exact F181", brake["bus"] == 1 and brake["tx"] == "0x7B0" and brake["rx"] == "0x7B8" and brake["f181"] == "F152633K0000")
check("Brake exact supporting identities", brake["f18c_serial"] == "8954147040CFC1800985" and brake["ecu_part_0105"] == "8954147040")
check("Brake direct route is bus1-only in bounded sweep", brake["bus0_bus2_f181_timeout"] is True)

print("\n== read-only Techstream-oracle transfer ==")
fo = art["frc_read_only_oracles"]
expected_oracles = {
  "0X1202": ("febcf6d2", 4), "0X1901": ("0000000000000000", 8),
  "0X1905": ("8080", 2), "0X1906": ("e080e0008000", 6),
  "0X1912": ("02", 1), "0X1914": ("8000", 2),
  "0X1918": ("8000", 2), "0X1928": ("c0c0", 2),
}
check("all selected FRC P5 oracles answer", all(fo[k]["status"] == "positive" and (fo[k]["hex"], fo[k]["length"]) == v for k, v in expected_oracles.items()))
bo = art["brake_read_only_oracles"]
check("Brake 0x102F answers", bo["0x102F"] == {"hex": "f700fd007c00a9000000", "length": 10, "status": "positive"})
check("Brake 0x107E rejected in default", bo["0x107E_default"]["status"] == "negative_or_timeout" and "request out of range" in bo["0x107E_default"]["error"])
check("Brake 0x107E rejected in extended and ECU returned default", bo["0x107E_extended"]["extended_session"] == "positive" and bo["0x107E_extended"]["status"] == "negative_or_timeout" and "request out of range" in bo["0x107E_extended"]["error"] and bo["0x107E_extended"]["returned_default"] is True)
check("0x107E Corolla live-oracle transfer is explicitly rejected", "Do not transfer" in bo["boundary"])

print("\n== isolated cruise controls ==")
iso = art["isolated_cruise_controls"]
def values(label: str, field: str) -> list[str]:
  return [x[field] for x in iso[label]["transitions"]]
check("MAIN isolated 1906 event", iso["MAIN"]["sample_count"] == 373 and values("MAIN", "1906") == ["e080e0008000", "e0c0e0008000", "e080e0008000"])
check("RES+ isolated two-phase 1906 event", iso["RES+"]["sample_count"] == 372 and values("RES+", "1906") == ["e080e0008000", "e080e0808000", "e0a0e0808000", "e080e0008000"])
check("SET- isolated 1906 event", values("SET-", "1906") == ["e080e0008000", "e080e0408000", "e080e0008000"])
check("CANCEL isolated 1906 event", values("CANCEL", "1906") == ["e080e0008000", "e080e0208000", "e080e0008000"])
check("distance isolated persistent 1912 change", values("DISTANCE", "1912") == ["03", "04"])

print("\n== synchronized diagnostic/CAN join ==")
sync = art["synchronized_capture"]
check("synchronized capture exact sample/frame counts", sync["oracle_sample_count"] == 1742 and sync["can_frame_count"] == 90932)
check("exact synchronized event times", sync["event_times_s"] == {"CANCEL": 15.285071, "DISTANCE": 16.874632, "MAIN": 9.884382, "RES+": 11.7243, "SET-": 13.624379})
carrier = sync["0x0FE_momentary_switch_carrier"]
check("0x0FE/32 bus1 momentary carrier cadence", carrier["bus"] == 1 and carrier["address"] == "0x0FE" and carrier["dlc"] == 32 and 33.0 < carrier["rate_hz"] < 33.4)
check("0x0FE baseline tuple exact", carrier["baseline_B3_B4_B6_B7"] == {"B3": 0x3F, "B4": 0, "B6": 0xC3, "B7": 0x62})
expected_events = {
  "MAIN": ({"B3": 0x3F, "B4": 0, "B6": 0xC3, "B7": 0x66}, {"B3": 0, "B4": 0, "B6": 0, "B7": 0x04}),
  "RES+": ({"B3": 0xBF, "B4": 0, "B6": 0x43, "B7": 0x62}, {"B3": 0x80, "B4": 0, "B6": 0x80, "B7": 0}),
  "SET-": ({"B3": 0x3F, "B4": 0x80, "B6": 0xC3, "B7": 0x22}, {"B3": 0, "B4": 0x80, "B6": 0, "B7": 0x40}),
  "CANCEL": ({"B3": 0x3F, "B4": 0x40, "B6": 0xC3, "B7": 0x42}, {"B3": 0, "B4": 0x40, "B6": 0, "B7": 0x20}),
}
for label, (event_tuple, xor) in expected_events.items():
  e = carrier["events"][label]
  check(f"0x0FE {label} event tuple exact", e["event_B3_B4_B6_B7"] == event_tuple and e["xor"] == xor)
check("0x0FE interpretation is dynamic join, not producer claim", "direct dynamic join" in carrier["interpretation"] and "Counter/integrity" in carrier["interpretation"])

dist = sync["distance_state"]
check("distance DID 1912 validated twice", dist["isolated_transition"] == "03->04" and dist["synchronized_transition"] == "04->01" and dist["frc_did"] == "0x1912")
c251 = dist["candidate_can_carriers"]["0x251/8"]
c5af = dist["candidate_can_carriers"]["0x5AF/32"]
check("0x251 distance candidate exact", c251["bus"] == 1 and c251["byte_index"] == 5 and c251["before"] == 0x88 and c251["after"] == 0x28 and c251["payload_before"] == "a00000488088a080" and c251["payload_after"] == "a00000488028a080" and 0 < c251["latency_from_1912_change_ms"] < 20)
check("0x5AF distance candidate exact", c5af["bus"] == 1 and c5af["byte_index"] == 24 and c5af["before"] == 0xF0 and c5af["after"] == 0xE4 and c5af["xor"] == 0x14 and 0 < c5af["latency_from_1912_change_ms"] < 20)
check("distance ordinary-CAN semantics remain bounded", all("candidate only" in x["boundary"] for x in (c251, c5af)) and "pending an independent repeat/enum sweep" in dist["interpretation"])
check("production boundary remains observation-only", all(x in art["production_boundary"] for x in ("identities and observation carriers only", "does not establish Camry B6", "production safety policy")))

print("\n== documentation ==")
doc = (REPO / "docs/variants/camry-2026-live-baseline.md").read_text()
for token in ("8646F3315000", "F152633K0000", "0x0FE", "0x1906", "0x1912", "0x251", "0x5AF", "0x107E"):
  check(f"Camry report preserves {token}", token in doc)

print(f"\nResults: {passed} passed, {failed} failed")
raise SystemExit(1 if failed else 0)
