#!/usr/bin/env python3
"""Verify exact-F33 EPS ownership and SecOC Tx construction of CAN-FD 0x030."""
from __future__ import annotations

import hashlib
import json

from tools import REPO_ROOT
ROOT = REPO_ROOT

from tools.targets.camry.analysis.analyze_camry_f33_030_secoc_tx import analyze

IMAGE = ROOT / "firmware/camry-8965F3307000/CodeFlash.bin"
ARTIFACT = ROOT / "data/generated/camry_8965F3307000_030_secoc_tx.json"
EXPECTED_IMAGE_SHA256 = "42dce8efc42f6ae31718e7713fa2d26bb9191b4a82439778aee4d7afded9b0e7"


def main() -> int:
  assert hashlib.sha256(IMAGE.read_bytes()).hexdigest() == EXPECTED_IMAGE_SHA256
  generated = analyze()
  artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))
  assert generated == artifact

  tx = artifact["tx_identity"]
  assert tx["generated_com_pdu"] == 0
  assert tx["can_id"] == "0x030" and tx["can_fd"] is True and tx["wire_length"] == 32
  assert tx["canif_id_word"] == "0x40000030"
  assert tx["pdu0_descriptor_hex"] == "0200000020000003"

  p = artifact["secoc_tx_profile"]
  assert p["profile_index"] == 0
  assert p["data_id"] == 0x0030
  assert p["freshness_value_id"] == 3
  assert p["authentic_payload_bytes"] == 28
  assert p["security_trailer_bytes"] == 4
  assert p["full_freshness_bits"] == 46
  assert p["full_freshness_storage_bytes"] == 6
  assert p["transmitted_freshness_bits"] == 4
  assert p["authenticator_bits"] == 28
  assert p["key_selector_descriptor_id"] == 0
  assert p["crypto_job_id"] == 0
  assert p["lower_pdu_id"] == 0
  assert p["tx_freshness_callback"] == "0x0903F6"
  assert p["mac_input_bytes"] == 36

  live = artifact["live_crypto"]
  assert live["descriptor_address"] == "0xFEBE5504"
  assert live["descriptor_hex"] == "0100000004000000000000000000000000000000"
  assert live["descriptor_mode"] == 1
  assert live["icu_s_key_selector"] == 4
  assert live["icu_s_command"] == 5

  assert artifact["mac_domain"] == {
    "data_id": "0x0030",
    "application_payload_bytes": 28,
    "full_freshness_bits": 46,
    "full_freshness_storage_bytes": 6,
    "total_bytes": 36,
  }

  # The application layer does not create the SecOC tail.  Retained READY RAM
  # has zero B28..B31 in generated-COM PDU0 while the tracked wire oracle has a
  # nonzero protected tail on the closest 27/28-byte application match.
  rw = artifact["ram_vs_wire"]
  assert rw["generated_com_buffer_address"] == "0xFEBE4A48"
  assert rw["generated_com_B28_B31_hex"] == "00000000"
  assert rw["closest_oracle_application_equal_bytes"] == 27
  assert rw["closest_oracle_B28_B31_hex"] == "b6a71e8c"

  oracle = artifact["tracked_oracle"]
  assert oracle["frame_count"] == 6189 and oracle["sync_count"] == 618
  assert oracle["inner_additive_b7_rule"]["matches"] == 6189
  outer = oracle["outer_trailer"]
  assert outer["unique_B28_B31"] == outer["unique_MAC28_candidates"] == 6189
  assert outer["FV4_high_nibble_values"] == list(range(16))
  assert outer["same_reset_message_low2_deltas"] == {"1": 5981}
  assert outer["preceding_0x00F_reset_low2"]["matches"] == 5786
  assert outer["preceding_0x00F_reset_low2"]["eligible"] == 6180

  print("PASS: exact F33 EPS constructs CAN-FD 0x030 as 28-byte application + FV4/MAC28 SecOC using ICU-S command 5 selector 4")
  return 0


if __name__ == "__main__":
  raise SystemExit(main())
