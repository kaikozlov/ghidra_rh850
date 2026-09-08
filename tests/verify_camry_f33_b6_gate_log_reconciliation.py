#!/usr/bin/env python3
"""Verify the retained-road-log reconciliation against exact-F33 B6 gates."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / "data/generated/camry_f33_b6_gate_log_reconciliation.json"
FRESH = ROOT / "data/generated/camry_b6_freshness_contract.json"
INGRESS = ROOT / "data/generated/camry_8965F3307000_external_lateral_ingress.json"
PORT = ROOT / "data/generated/camry_8965F3307000_tss3_opendbc_port.json"
CORPUS = ROOT / "data/generated/camry-8965F3307000/decompilations.jsonl"


def sha(path: Path) -> str:
  return hashlib.sha256(path.read_bytes()).hexdigest()


def load_functions(entries: set[int]) -> dict[int, dict]:
  out: dict[int, dict] = {}
  with CORPUS.open(encoding="utf-8") as fh:
    for line in fh:
      rec = json.loads(line)
      if rec.get("record") != "function":
        continue
      entry = int(rec["entry_addr"], 16)
      if entry in entries:
        out[entry] = rec
  return out


def refs(funcs: dict[int, dict], target: int, ref_type: str) -> list[int]:
  out: set[int] = set()
  for entry, rec in funcs.items():
    for ref in rec.get("data_references", []):
      try:
        to_addr = int(ref["to_addr"], 16)
      except (KeyError, ValueError):
        continue
      if to_addr == target and ref.get("ref_type") == ref_type:
        out.add(entry)
  return sorted(out)


def main() -> int:
  data = json.loads(ART.read_text())
  fresh = json.loads(FRESH.read_text())
  ingress = json.loads(INGRESS.read_text())

  assert data["schema"] == "camry-f33-b6-gate-log-reconciliation-v1"
  assert data["sources"]["freshness_artifact_sha256"] == sha(FRESH)
  assert data["sources"]["external_ingress_artifact_sha256"] == sha(INGRESS)
  assert data["sources"]["f33_port_artifact_sha256"] == sha(PORT)
  assert data["sources"]["exact_f33_corpus_sha256"] == sha(CORPUS)
  assert data["sources"]["retained_routes"] == 13
  assert data["sources"]["retained_rlogs"] == 530
  assert data["sources"]["retained_rlog_bytes"] == 5_328_786_933
  assert len(fresh["routes"]) == 13

  # Independent exact-F33 static closure for the two readiness inputs that ordinary
  # road CAN can actually observe.
  chain = next(x for x in ingress["scalar_command_cone_census"]["chains"] if x.get("signal") == 243)
  assert chain["can_id"] == "0x0D7"
  assert chain["length"] == 32 and chain["byte_offset"] == 0 and chain["bit_offset"] == 7
  assert chain["raw"] == "0xFEBE80A0" and chain["stage"] == "0xFEBEF094" and chain["snapshot"] == "0xFEBEACCD"

  funcs = load_functions({0x4C2DC, 0x4C97A, 0x58074, 0xBCD62, 0xBF3AA, 0xCB548, 0xCB664, 0xCB73A, 0xCB81C, 0xCE772, 0xCE7A6, 0xCEFFC, 0xD0D7C})
  assert len(funcs) == 13
  c = {a: rec["decompiled_c"] for a, rec in funcs.items()}
  assert "DAT_febe8c3e = DAT_febe817c" in c[0x4C97A]
  assert "FUN_0007d31e(0x13,0xd,2,0" in c[0x4C97A]
  assert "DAT_febef145 = DAT_febe817c" in c[0x58074]
  assert "puVar38[-0xa41] = FUN_00003942[(int)(puVar38 + 3)]" in c[0xBCD62]  # GP+0x3945 F145 -> GP-0xA41 ADBF
  # Exact F33 also exports CAFC and CAD9 through its own 0x030 PDU.
  assert "DAT_febead42 = DAT_febecafc" in c[0xD0D7C]
  assert "DAT_febee834 = DAT_febead42" in c[0xBF3AA]
  assert "DAT_febe80ec = DAT_febee834" in c[0x4C2DC]
  assert "DAT_febe8c43 = DAT_febe80ec" in c[0x4C97A]
  assert "FUN_0007d31e(0x19,0x10,1,0,puVar3 + -0x2bbd)" in c[0x4C97A]
  assert "DAT_febead4b = DAT_febecad9" in c[0xD0D7C]
  assert "DAT_febee83a = DAT_febead4b" in c[0xBF3AA]
  assert "DAT_febe80e0 = DAT_febee83a" in c[0x4C2DC]
  assert "DAT_febe8c47 = DAT_febe80e0" in c[0x4C97A]
  assert "FUN_0007d31e(0x1f,0x13,1,0,puVar3 + -0x2bb9)" in c[0x4C97A]
  for token in ("DAT_febeaccc == '\\0'", "DAT_febeaccd == '\\0'", "DAT_febeadbf < 2", "DAT_febecafc == '\\0'", "DAT_febecad9 == '\\0'"):
    assert token in c[0xCE772]
  for token in ("DAT_febeaccc != '\\0'", "DAT_febeaccd != '\\0'", "DAT_febeadbf == '\\x02'", "DAT_febecafc == '\\x01'", "DAT_febecad9 == '\\x01'"):
    assert token in c[0xCE7A6]

  # CORR-182: sig263/CB664 only qualifies the special ADB0==0x31 transient.
  assert "DAT_febeaddd" in c[0xCB664] and "DAT_febec7b4" in c[0xCB664]
  assert "DAT_febeadb0 == '1'" in c[0xCB73A] and "DAT_febec7bf = '\\x01'" in c[0xCB73A]
  assert c[0xCB81C].index("FUN_000cb664") < c[0xCB81C].index("FUN_000cb73a")
  assert "DAT_febeadb0 == '\\v'" in c[0xCEFFC] and "DAT_febecb00 = 2" in c[0xCEFFC]
  assert refs(funcs, 0xFEBEC7B4, "READ") == [0xCB664, 0xCB73A]
  assert refs(funcs, 0xFEBEC7B4, "WRITE") == [0xCB548, 0xCB664]

  routes = {r["route_name"]: r for r in data["routes"]}
  expected_recent = {
    "00000037--dec6fe39cb": (18_456, 9_755),
    "0000003e--1a2f20417d": (232_557, 160_798),
    "0000003f--36e72f5fdc": (249_066, 165_071),
    "00000045--805b7ca6ab": (43_093, 17_463),
    "00000048--709f22277b": (21_347, 11_826),
  }
  for name, (send, active) in expected_recent.items():
    r = routes[name]
    b6 = r["b6"]
    assert b6["send_frames"] == send and b6["active_id11"] == active
    assert b6["expected_active_pattern_count"] == active
    assert b6["unexpected_active_pattern_count"] == 0
    assert b6["cadence"]["gt_35ms"] == 0
    assert set(r["road_gate_observables"]["ACCD"]["active_b6_latest_within_25ms"]) <= {"0"}
    assert set(r["road_gate_observables"]["ADBF"]["active_b6_latest_within_25ms"]) <= {"0"}
    assert set(r["road_gate_observables"]["CAFC"]["active_b6_latest_within_25ms"]) <= {"0"}
    assert set(r["road_gate_observables"]["CAD9"]["active_b6_latest_within_25ms"]) <= {"0"}

  # The older corpus is useful as a sender-evolution control: route27 had sig265=1
  # with zero supervisor weights, route2A retained sig265=1 with 100/100 weights,
  # and route2C already matches the current active application shape.
  assert routes["00000027--885099a1d4"]["b6"]["application_pattern_counts"]["11,0,0,1,0,0,0,0,0,0,0"] == 78_088
  assert routes["0000002a--c5647fd694"]["b6"]["application_pattern_counts"]["11,0,0,1,0,0,100,100,0,0,0"] == 13_410
  assert routes["0000002c--c784367b7e"]["b6"]["application_pattern_counts"]["11,0,0,0,0,0,100,100,0,0,0"] == 8_323

  agg = data["aggregate"]
  assert agg["b6_send_frames"] == 1_696_097
  assert agg["zero_mac28_frames"] == 1_696_097 and agg["nonzero_mac28_frames"] == 0
  assert agg["b6_cadence_gt35ms_within_retained_sequence"] == 0
  assert agg["recent_active_id11_frames"] == 364_913
  assert agg["recent_active_ACCD_latest_within_25ms"] == {"0": 364_911}
  assert agg["recent_active_ADBF_latest_within_25ms"] == {"0": 364_910}
  assert agg["recent_active_CAFC_latest_within_25ms"] == {"0": 364_910}
  assert agg["recent_active_CAD9_latest_within_25ms"] == {"0": 364_910}
  assert agg["current_shape_active_id11_frames"] == 833_730
  assert agg["current_shape_route_names"] == [
    "0000002c--c784367b7e", "00000037--dec6fe39cb", "0000003b--62262eb7a1",
    "0000003c--97b9e7a69a", "0000003d--0e812cecba", "0000003e--1a2f20417d",
    "0000003f--36e72f5fdc", "00000045--805b7ca6ab", "00000048--709f22277b",
  ]
  assert all(set(v) <= {"0"} for v in agg["current_shape_active_gate_values_within_25ms"].values())

  # No recent road route invokes the diagnostic/service API that can set the AC2B
  # branch source.  Their only single-frame EPS diagnostic service is TesterPresent.
  for name in expected_recent:
    assert routes[name]["diagnostic_requests"]["single_frame_service_counts"] == {"0x3E": 3}
    assert routes[name]["diagnostic_requests"]["non_tester_present_single_frame_requests"] == 0

  conclusions = data["conclusions"]
  assert conclusions["current_application_shape_is_supported_by_recent_road_logs"] is True
  assert conclusions["historical_corpus_active_shape_is_uniform"] is False
  assert conclusions["recent_B6_cadence_crosses_35ms_loss_threshold"] is False
  assert conclusions["recent_ACCD_observable_satisfies_zero_when_joined"] is True
  assert conclusions["recent_ADBF_observable_satisfies_lt2_when_joined"] is True
  assert conclusions["ACCC_is_directly_proven_from_road_CAN"] is False
  assert conclusions["recent_CAFC_observable_satisfies_zero_when_joined"] is True
  assert conclusions["recent_CAD9_observable_satisfies_zero_when_joined"] is True
  assert conclusions["road_logs_prove_F33_internal_B6_admission"] is False
  assert conclusions["sig263_or_CB664_speed_is_normal_ID11_gate"] is False
  assert conclusions["highest_value_next_witness"].startswith("queue -> route44")

  print("camry F33 B6 road-log/gate reconciliation: PASS")
  return 0


if __name__ == "__main__":
  raise SystemExit(main())
