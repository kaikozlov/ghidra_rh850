#!/usr/bin/env python3
"""Verify the complete exact-F33 EPS transmit surface."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools.targets.camry.analysis.analyze_camry_f33_eps_tx import analyze

ARTIFACT = ROOT / "data/generated/camry_8965F3307000_eps_tx.json"


def by_id(obj: dict) -> dict[str, dict]:
  return {row["can_id"]: row for row in obj["normal_messages"]}


def main() -> int:
  generated = analyze()
  artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))
  assert generated == artifact
  assert artifact["schema"] == "camry-f33-eps-tx-v1"
  assert artifact["target"]["software_id"] == "8965F3307000"
  assert artifact["target"]["codeflash_sha256"] == "42dce8efc42f6ae31718e7713fa2d26bb9191b4a82439778aee4d7afded9b0e7"

  summary = artifact["executive_summary"]
  assert summary["normal_ids"] == ["0x030", "0x351", "0x394", "0x4A3", "0x4C8"]
  assert summary["diagnostic_response_ids"] == ["0x7A9", "0x7A8"]
  assert summary["special_extended_response_id"] == "0x1FE00002"
  assert summary["only_secoc_protected_normal_tx"] == "0x030"

  cfg = artifact["generated_configuration"]
  assert cfg["class_counts"] == [5, 0, 4, 0, 0, 1]
  assert cfg["slice_offsets"] == [0, 32, 36, 39, 47]
  assert [row[3] for row in cfg["pdu_descriptors"]] == [32, 4, 3, 8, 8]
  assert cfg["signal_ownership"] == {
    "0": list(range(0, 38)) + [283],
    "1": [38, 39],
    "2": [40, 41, 42, 43],
    "3": list(range(44, 52)),
    "4": [52, 53, 54, 55],
  }

  msgs = by_id(artifact)
  assert [(cid, msgs[cid]["wire_length"], msgs[cid]["cycle_ticks"], msgs[cid]["nominal_cycle_ms"]) for cid in summary["normal_ids"]] == [
    ("0x030", 32, 2, 10.0),
    ("0x351", 4, 200, 1000.0),
    ("0x394", 3, 60, 300.0),
    ("0x4A3", 8, 100, 500.0),
    ("0x4C8", 8, 196, 980.0),
  ]
  assert msgs["0x030"]["configured_without_direct_pack_call"] == [36, 37, 283]
  assert msgs["0x4C8"]["configured_without_direct_pack_call"] == [55]
  assert msgs["0x030"]["unwritten_application_regions"] == [
    "B1", "B2[7:2]", "B10[2:0]", "B16[7:6]", "B18", "B19[7:1]", "B24:B26", "B27[7:2]",
  ]

  p030 = msgs["0x030"]
  assert p030["protection"]["data_id"] == "0x0030"
  assert p030["protection"]["freshness_bits_full"] == 46
  assert p030["protection"]["freshness_bits_transmitted"] == 4
  assert p030["protection"]["authenticator_bits"] == 28
  assert p030["protection"]["icu_s_command"] == 5
  assert p030["protection"]["icu_s_key_selector"] == 4
  assert p030["fields"][10]["wire"] == "B7"
  assert p030["fields"][10]["role"] == "inner additive checksum: low8(sum(B0..B6)+0x38)"
  torque_fields = [r for r in p030["fields"] if r.get("oem") == "Steering Wheel Torque"]
  assert [r["wire"] for r in torque_fields] == ["B8", "B17[3:0]"]

  p351 = msgs["0x351"]
  assert [r["wire"] for r in p351["fields"]] == ["B2[7:5]", "B2[4]"]
  assert p351["fault_join"]["debounce_count"] == 7
  assert p351["fault_join"]["related_techstream_dtc"]["code"] == "C159B49"
  assert p351["fault_join"]["related_techstream_dtc"]["description"] == 'Power Steering Motor "B" Terminal Voltage Detect Circuit'

  p394 = msgs["0x394"]
  assert [r["wire"] for r in p394["fields"]] == ["B1[7:6]", "B1[5:3]", "B2[3:1]", "B2[0]"]
  assert p394["classifier"]["internal_state_count"] == 17
  assert len(p394["classifier"]["table_rows"]) == 17
  assert p394["classifier"]["table_rows"][0] == [0, 0, 0, 0, 0]
  assert p394["classifier"]["table_rows"][16] == [4, 7, 0, 0, 0]

  p4a3 = msgs["0x4A3"]
  assert [r["wire"] for r in p4a3["fields"]] == [f"B{i}" for i in range(8)]
  assert "received 0x025" in p4a3["fields"][1]["role"]
  assert p4a3["fields"][3]["oem"] == "Steering Angle"
  assert p4a3["fields"][5]["oem"] == "Steering Wheel Torque"
  assert p4a3["semantic_join"]["steering_wheel_torque"] == "B5 signed projection at 0.1 N.m/count"

  p4c8 = msgs["0x4C8"]
  assert p4c8["initial_application_bytes"] == "0900000000000000"
  assert p4c8["constant_template"]["normal_packer_result"] == "09 00 00 00 00 00 00 00"
  assert p4c8["constant_template"]["oem_semantic"] == "unresolved"

  scheduler = artifact["scheduler"]
  assert scheduler["tx_group_count"] == 1
  assert scheduler["group_0"]["pdu_count"] == 5
  assert scheduler["group_0"]["membership_masks"] == [0x10] * 5
  assert scheduler["periodic_cycle_ticks"] == [2, 200, 60, 100, 196]
  assert scheduler["packing_semantics"]["event_triggered_pdus"] == ["0x351", "0x394"]
  snap = scheduler["runtime_snapshot"]
  assert snap is not None
  assert snap["group_desired_mask"] == snap["group_current_mask"] == 0x10
  assert snap["pdu_state_bytes"] == [0x81] * 5
  assert snap["periodic_countdowns"] == [2, 139, 23, 31, 143]

  hth = artifact["canif_hardware_routes"]
  routes = {r["can_id"]: r for r in hth["normal_pdu_routes"]}
  assert routes["0x030"]["driver_node"] == routes["0x351"]["driver_node"] == 1
  assert routes["0x030"]["driver_mailbox"] == 0 and routes["0x030"]["lower_writer"] == "0x8549E CAN-FD"
  for cid in ["0x351", "0x394", "0x4A3", "0x4C8"]:
    assert routes[cid]["driver_mailbox"] == 3
    assert routes[cid]["lower_writer"] == "0x853AA classic CAN"

  diag = artifact["noncyclic_transmit"]["diagnostic_transport"]
  assert diag["rx_ids"] == ["0x7A1", "0x777", "0x7A0"]
  assert [r["can_id"] for r in diag["tx_records"]] == ["0x7A9", "0x7A9", "0x7A8", "0x7A8"]
  xcp = artifact["noncyclic_transmit"]["xcp_shaped_extended"]
  assert xcp["response_extended_can_id"] == "0x1FE00002"
  assert xcp["paired_request_extended_can_id"] == "0x1FDC0002"

  dyn = artifact["dynamic_observations"]
  assert dyn["saved_log_positive_native_frames"] == [{
    "address": "0x030",
    "count": 6000,
    "duration_s": 59.993426,
    "event": "can",
    "first_relative_s": 0.0,
    "last_relative_s": 59.993426,
    "length": 32,
    "path": "/Users/kai/dev/inspect/logs/camry-2026/2026-09-04/0000003d--0e812cecba/rlog-8.zst",
    "src": 0,
  }]
  for census in dyn["parked_censuses"].values():
    assert census["controls"]["0x030"] > 0
    assert all(census["absent_carriers"][cid] == 0 for cid in ["0x351", "0x394", "0x4A3", "0x4C8"])

  print("PASS: exact F33 EPS Tx surface closes five normal PDUs, SecOC routing, scheduler/CanIf paths, diagnostics, and special extended transport")
  return 0


if __name__ == "__main__":
  raise SystemExit(main())
