#!/usr/bin/env python3
"""Verify exact-F33 EPS ownership and SecOC Tx construction of CAN-FD 0x030."""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools.targets.camry.analysis.analyze_camry_f33_030_secoc_tx import analyze

IMAGE = ROOT / "firmware/camry-8965F3307000/CodeFlash.bin"
CORPUS = ROOT / "data/generated/camry-8965F3307000/decompilations.jsonl"
ARTIFACT = ROOT / "data/generated/camry_8965F3307000_030_secoc_tx.json"
EXPECTED_IMAGE_SHA256 = "42dce8efc42f6ae31718e7713fa2d26bb9191b4a82439778aee4d7afded9b0e7"


def load_c(entries: set[int]) -> dict[int, str]:
  out: dict[int, str] = {}
  with CORPUS.open(encoding="utf-8") as fh:
    for line in fh:
      rec = json.loads(line)
      if rec.get("record") != "function":
        continue
      entry = int(rec["entry_addr"], 16)
      if entry in entries:
        out[entry] = rec["decompiled_c"]
  assert set(out) == entries
  return out


def main() -> int:
  assert hashlib.sha256(IMAGE.read_bytes()).hexdigest() == EXPECTED_IMAGE_SHA256
  generated = analyze()
  artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))
  assert generated == artifact
  assert artifact["schema"] == "camry-f33-030-secoc-tx-v1"

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

  wire = artifact["wire_layout"]
  assert wire["outer_security"] == "B28[7:4]=FV4; B28[3:0]||B29||B30||B31=MAC28"
  assert wire["fv4_split"] == "B28[7:6]=message counter low2; B28[5:4]=reset counter low2"
  assert artifact["mac_domain"] == {
    "data_id": "0x0030",
    "application_payload_bytes": 28,
    "full_freshness_bits": 46,
    "full_freshness_storage_bytes": 6,
    "total_bytes": 36,
    "composition": "DataID_be16 || application_payload[28] || full_freshness[6]",
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

  c = load_c({0x7DF14, 0x81AB2, 0x88B84, 0x8A720, 0x8ECB2, 0x8ED8E, 0x8F19A, 0x8FABA, 0x8FA5A, 0x8FD90, 0x8FED0, 0x8FFDA, 0x90736})

  # Generated-COM PDU0 crosses PduR into the secure route rather than directly
  # reaching the CAN driver.
  assert "FUN_00081a7e(uStack_26,&puStack_24)" in c[0x7DF14]
  assert "PTR_DAT_0002296e" in c[0x81AB2]
  assert "FUN_0008fa5a(param_1,0,auStack_a)" in c[0x8ED8E]
  assert "sVar1 = DAT_00025964;" in c[0x8FA5A]
  assert "sVar1 = DAT_00025966" in c[0x8FA5A]
  assert "*param_3 = 0;" in c[0x8FA5A]
  assert "FUN_0008faba(auStack_a[0],param_2)" in c[0x8ED8E]
  assert "sStack_14 = *(short *)(param_2 + 1) - *(short *)(puVar2 + 0x1b42);" in c[0x8FABA]

  # 8FD90 obtains full/truncated freshness, binds DataID 0x0030, constructs the
  # authentication input, and submits CryptoIf MAC generation.
  assert "uStack_20 = *(undefined2 *)(&DAT_00025944 + iVar8);" in c[0x8FD90]
  assert "uStack_50 = (uint)(byte)(&DAT_0002594c)[iVar8];" in c[0x8FD90]
  assert "(&DAT_0002594d)[iVar8]" in c[0x8FD90]
  assert "FUN_0008ecb2(&uStack_28,puVar2 + -0x6280);" in c[0x8FD90]
  assert "FUN_0008fcca(*(undefined2 *)(&DAT_00025950 + iVar8),auStack_44);" in c[0x8FD90]

  # Exact MAC domain: DataID big-endian, then 28 application bytes, then the
  # six-byte storage of the configured 46-bit full freshness value.
  assert "*param_2 = (char)((ushort)*(undefined2 *)(param_1 + 2) >> 8);" in c[0x8ECB2]
  assert "param_2[1] = *(undefined1 *)(param_1 + 2);" in c[0x8ECB2]
  assert "FUN_00089f2e(param_2 + 2,*param_1,*(undefined2 *)((int)param_1 + 10));" in c[0x8ECB2]
  assert "FUN_00089f2e(param_2 + iVar1,param_1[1],*(undefined2 *)(param_1 + 3));" in c[0x8ECB2]

  # READY selector descriptor 0 is copied from FEBE5504.  The command-5 job
  # builder takes byte +4 as the key selector, and the ICU-S submit routine
  # writes selector<<16 | 5 to ICUSCMD.  The retained descriptor has selector 4.
  assert "*param_2 = *(undefined4 *)(puVar1 + -0x62fc);" in c[0x8F19A]
  assert "bVar1 = *(byte *)(param_1 + 1);" in c[0x88B84]
  assert "*(uint *)(puVar2 + 0x5a18) = (uint)bVar1;" in c[0x88B84]
  assert "DAT_ffc5d000 = puVar6[2] << 0x10 | 5;" in c[0x8A720]

  # 8FED0 places the transmitted freshness bits first, then the configured 28
  # authenticator bits, giving exactly FV4||MAC28 in four bytes.  8FFDA appends
  # those bytes and submits the secured PDU through lower PDU0.
  assert "(&DAT_0002594d)[param_1 * 0x44]" in c[0x8FED0]
  assert "*(ushort *)(&DAT_0002593a + param_1 * 0x44)" in c[0x8FED0]
  assert "(&DAT_febe5574)[uVar5]" in c[0x8FED0]
  assert "(&DAT_febe55a8)[uVar7]" in c[0x8FED0]
  assert "FUN_0008fed0(param_1,auStack_34,&local_40)" in c[0x8FFDA]
  assert "FUN_0008eaa0(uVar6,extraout_r6,uVar3,&uStack_20)" in c[0x8FFDA]
  assert "FUN_000901d2(uVar2,&uStack_3c)" in c[0x8FFDA]

  # Exact F33's ordinary freshness decoder independently fixes Toyota FV4 as
  # message-low2 in bits7:6 followed by reset-low2 in bits5:4.
  assert "*(ushort *)(param_3 + 2) = (ushort)(*param_1 >> 6);" in c[0x90736]
  assert "bVar1 = *param_1 >> 4;" in c[0x90736]
  assert "*(byte *)((int)param_3 + 10) = bVar1 & 3;" in c[0x90736]

  print("PASS: exact F33 EPS constructs CAN-FD 0x030 as 28-byte application + FV4/MAC28 SecOC using ICU-S command 5 selector 4")
  return 0


if __name__ == "__main__":
  raise SystemExit(main())
