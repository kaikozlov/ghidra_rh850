#!/usr/bin/env python3
"""Verify exact-F33 invalid-MAC value equivalence under cumulative stage 5."""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools.targets.camry.analysis.analyze_camry_f33_b6_mac_equivalence import analyze

IMAGE = ROOT / "firmware/camry-8965F3307000/CodeFlash.bin"
CORPUS = ROOT / "data/generated/camry-8965F3307000/decompilations.jsonl"
ARTIFACT = ROOT / "data/generated/camry_f33_b6_mac_equivalence.json"
EXPECTED_IMAGE_SHA256 = "42dce8efc42f6ae31718e7713fa2d26bb9191b4a82439778aee4d7afded9b0e7"
EXPECTED_STAGE5_SHA256 = "669cedf8c8465ebfd02318cb7708b897b817bc3b40925c89743b64ce49aa01af"

EXPECTED_BODY_SHA256 = {
  "0x04BD46": "db4f6577d4a3250c7277730ee2f3c3e3fb71ffa83c6103ff1cd4c5b982f65b62",
  "0x07D800": "2fabcd172911f9fb0fa807666c7c851537ee45975d43cd6fef343f9ccd0c25e8",
  "0x081CA6": "2b7c5736393c68204635d71cf7306a67685445f4451aeae9f29516e75cdbb4f5",
  "0x088FC0": "885e8edb09d35f0cedea452efa003b4807344487e6394ba156b32491d6eaabd2",
  "0x089646": "4eec6679c98796dc7414b3706482e4fb6d89d6e503bab1f9a113f8a90879af7d",
  "0x089C98": "139547a74d2b9affed13921621766da441817167bf42b4d78f0545b3eb9b7965",
  "0x08E772": "d216bc64825096ddf60a10f32c6110a939b1cab7ba066c1bf7891e58cbafd46f",
  "0x08ECB2": "d1e16041f8e55bec3173a949a783c8dfe9742447c88a3c737fd23e253c4064eb",
  "0x08F434": "23baff101c49428738e2bc8273c7a2fdda32598028fa5665fb8a90d060286bc4",
  "0x08F546": "721f10f71fbf32b5dcada657c963d8034397217950d97088a0af54a6d6a84006",
  "0x08F676": "ce3c560d619403915125698d1dc10f3a8c6c301eb6d8ba32ebb98f9d1bacf68f",
  "0x08F746": "4cb7b08ada0b7e058aed4e9f44083b931a920427548e6d29abeb4f523e4fd1b7",
  "0x08F8D2": "758aab3b401cb94bcb88cd8e04de103fa37c85de872d2ee6b1652ab53a3ab636",
  "0x08F906": "860fc368a14af6365d6ee17c3bbaa4723a157b9c6f4a14023f888c51b42d3be4",
  "0x090204": "6386fa98f892fa79d74a4eb150319cbd6572b1649adaa42880b848e32899ce8a",
  "0x090A48": "bf0be72eb4cef2e510cc57b6b1f1c089aa760cb8f14cb0c6aa1337c91ae8ddd3",
  "0x090D6A": "35f2d6793551e9624ea98bcad296eda11c060b891faf9e25ec34e6d8ff9a2906",
}

EXPECTED_RAW_SHA256 = {
  "freshness_callback_0x903A0": "031775b45fb23dce7c0b12fe8ed8d8bb48db0c3390a98bfb7243783710246cd5",
  "post_crypto_callback_0x90448": "da3592af256b9d473ab9697f5642b95c4f1d6c47fe32b68479cc50aed958b63a",
  "route44_callback_0x7D72C": "ab6c3514c592e1a007d7d38abf723d22b905037b3ae7132cdcc5c1c73ec5b239",
  "icu_command0_start_0x891CC": "c321acfe3d13c38a61a189e5876119a4e73698b471916b9e966f83761d586dc5",
  "icu_command0_completion_0x892CC": "a5df00bb4c1d63efb0870828b647b2c51d902372b3aecfb15081d1db5f2faba9",
}


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
  image = IMAGE.read_bytes()
  assert hashlib.sha256(image).hexdigest() == EXPECTED_IMAGE_SHA256

  generated = analyze()
  artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))
  assert generated == artifact
  assert artifact["schema"] == "camry-f33-b6-invalid-mac-equivalence-v1"
  assert artifact["firmware"]["stage5"]["final_sha256"] == EXPECTED_STAGE5_SHA256
  assert artifact["firmware"]["stage5"]["final_crc_residue"] == "0xFFFFFFFF"

  # Exact B6 secured-profile geometry: four trailer bytes, 28-bit authenticator
  # starting after the FV4 high nibble, command-0 ICU verification, and PduR 44.
  p = artifact["b6_secoc_profile"]
  assert p == {
    "secured_record": 2,
    "data_id": 0x00B6,
    "authenticator_bits": 28,
    "trailer_extract_bytes": 4,
    "authenticator_start_bit_in_trailer": 4,
    "freshness_id": 2,
    "crypto_command_selector": 0,
    "post_crypto_callback": "0x090448",
    "upper_pdur_destination": 44,
    "freshness_callback": "0x0903A0",
  }

  # Pin every recovered stock function/body used in the proof and the raw ranges
  # for functions that the canonical corpus predates as explicit entries.
  assert {k: v["body_sha256"] for k, v in artifact["function_evidence"].items()} == EXPECTED_BODY_SHA256
  assert {k: v["sha256"] for k, v in artifact["raw_function_ranges"].items()} == EXPECTED_RAW_SHA256

  c = load_c({0x88FC0, 0x8F434, 0x8F676, 0x8F746, 0x8F8D2, 0x8F906, 0x8F546, 0x90204, 0x90D6A, 0x4BD46, 0x7D800})

  # Before ICU-S, the tag is extracted and copied as opaque bytes. The command
  # descriptor builder validates pointers and lengths, not tag value/content.
  assert "FUN_00089f2e(param_3,*param_2 + uVar4,bVar2 + 7 >> 3);" in c[0x8F434]
  assert "FUN_00089f2e(&DAT_febf1308,param_4,param_5 + 7 >> 3);" in c[0x88FC0]
  assert "param_4 == 0" in c[0x88FC0]
  assert "param_5 == 0" in c[0x88FC0] and "0x80 < param_5" in c[0x88FC0]
  assert "FUN_00089c98(param_1,puVar1 + -0x62ac,*(undefined4 *)(puVar1 + -0x62b0),puVar1 + -0x629c);" in c[0x8F676]

  refs = artifact["direct_reference_census"]
  assert refs["received_authenticator_buffer_FEBE5554"] == [
    {"function": "0x0008f434", "from": "0x0008f4a0", "type": "WRITE"},
    {"function": "0x0008f434", "from": "0x0008f4b0", "type": "READ"},
    {"function": "0x0008f434", "from": "0x0008f4be", "type": "WRITE"},
    {"function": "0x0008f676", "from": "0x0008f6a2", "type": "PARAM"},
  ]
  assert refs["icu_root_result_byte_FEBE5564"] == [
    {"function": "0x0008f676", "from": "0x0008f6a6", "type": "PARAM"},
    {"function": "0x0008f906", "from": "0x0008f92a", "type": "READ"},
  ]

  # Verify all five cumulative result-neutralization sites are present in the
  # independently reconstructed CRC-valid stage-5 image.
  expected_patches = {
    "stage1_final_delivery_gate": ("0x08F952", "e0d1", "e001"),
    "stage2_post_crypto_callback_result": ("0x08F948", "1a38", "003a"),
    "stage3_root_result_boolean": ("0x08F930", "e10f14d3", "e00714d3"),
    "stage4_freshness_callback_status": ("0x08F7E6", "0ad8", "00da"),
    "stage5_icu_command_return": ("0x08F890", "e051", "e001"),
  }
  for patch in artifact["installed_patch_sites"]:
    address, stock, replacement = expected_patches[patch["name"]]
    assert patch["address"] == address
    assert patch["stock"] == stock
    assert patch["stage5"] == patch["expected_stage5"] == replacement

  # Stage 2 forces the post-crypto callback's result argument to zero.  Exact
  # 8F8D2 removes the 0x10000 failure marker when result==0; 90448 then turns
  # that into success=True and 90D6A commits the pending ordinary freshness.
  assert "if (param_2 == '\\0')" in c[0x8F8D2]
  assert "uVar2 = (uint)(ushort)(&DAT_0002585a)[iVar1 * 0x28];" in c[0x8F8D2]
  assert "FUN_00089f2e(puVar1 + (short)param_1 * 0xc + -0x6224,puVar1 + (short)param_1 * 0xc + -0x620c,0xc" in c[0x90D6A]

  # The verified-success tail delivers through 8F546 -> 90204 -> 81CA6.  Route
  # 44 itself has no optional pre-copy hook; its only enabled gate 7D800 returns
  # 1 unconditionally, and it increments the new-data generation afterward.
  assert "FUN_00090204((&DAT_0002587e)[(short)param_1 * 0x28],&uStack_18);" in c[0x8F546]
  assert "FUN_00081ca6(param_1);" in c[0x90204]
  assert "return 1;" in c[0x7D800]
  r = artifact["route44_upper_delivery"]
  assert r["record_hex"] == "060000002000000c"
  assert r["configured_length"] == 32 and r["flags"] == 0x0C
  assert not r["optional_precopy_hook_enabled"]
  assert r["pass_guard_enabled"] and r["new_data_update_enabled"]
  assert all(not refs for refs in r["trailer_direct_data_refs"].values())

  # The application B6 unpacker consumes only offsets 0x1BA..0x1C1.  For PDU44
  # the 32-byte COM window starts at 0x1B7, so those are B3..B10. B28..B31 live
  # at 0x1D3..0x1D6 and are never application signals or a post-SecOC gate.
  assert r["com_window_base"] == 0x1B7
  assert r["application_unpack_max_offset"] == 0x1C1
  assert r["secured_trailer_bytes"] == [0x1D3, 0x1D6]
  for token in ("0x1ba", "0x1bb", "0x1bd", "0x1be", "0x1bf", "0x1c0", "0x1c1"):
    assert token in c[0x4BD46]
  assert "0x1d3" not in c[0x4BD46] and "0x1d6" not in c[0x4BD46]

  proof = artifact["proof"]
  assert not proof["pre_icu_authenticator_content_branch_recovered"]
  assert proof["freshness_status_forced_success_after_callback"]
  assert proof["icu_command_return_forced_success"]
  assert proof["icu_root_result_forced_success"]
  assert proof["post_crypto_callback_forced_success"]
  assert proof["post_crypto_success_commits_pending_freshness"]
  assert proof["final_delivery_gate_forced_success"]
  assert not proof["route44_post_secoc_content_recheck"]
  assert not proof["application_unpack_reads_secoc_trailer"]
  assert "acceptance-equivalent" in proof["conclusion"]

  print("camry exact-F33 B6 invalid-MAC equivalence: PASS")
  return 0


if __name__ == "__main__":
  raise SystemExit(main())
