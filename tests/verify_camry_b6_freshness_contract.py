#!/usr/bin/env python3
"""Verify exact-F33 B6 freshness semantics and the complete retained Camry corpus summary."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IMAGE = ROOT / "firmware/camry-8965F3307000/CodeFlash.bin"
CORPUS = ROOT / "data/generated/camry-8965F3307000/decompilations.jsonl"
ARTIFACT = ROOT / "data/generated/camry_b6_freshness_contract.json"
EXPECTED_IMAGE_SHA256 = "42dce8efc42f6ae31718e7713fa2d26bb9191b4a82439778aee4d7afded9b0e7"


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


def body_bytes(image: bytes, rec: dict) -> bytes:
  chunks = []
  for r in rec["body_ranges"]:
    assert r["space"] == "ram"
    lo = int(r["min"], 16)
    hi = int(r["max"], 16)
    chunks.append(image[lo:hi + 1])
  return b"".join(chunks)


def main() -> int:
  image = IMAGE.read_bytes()
  assert hashlib.sha256(image).hexdigest() == EXPECTED_IMAGE_SHA256

  wanted = {0x8F746, 0x90248, 0x90736, 0x909CA, 0x90A48, 0x90B1C, 0x90B8A, 0x90D6A}
  funcs = load_functions(wanted)
  assert set(funcs) == wanted
  expected_body_sha = {
    0x8F746: "4cb7b08ada0b7e058aed4e9f44083b931a920427548e6d29abeb4f523e4fd1b7",
    0x90248: "45bf715e450ba5263edaf86b14822b07f5fe49a8bd318198f9a4dbd75ea2ac45",
    0x90736: "686f0eec344c1661f8074016e751e9021d50ca752f7368aabf1d003c040d7389",
    0x909CA: "d1cb5ad7edcb0043ea74dae46a90015a6eadeb58199dff3c06cfa56c65252f7f",
    0x90A48: "bf0be72eb4cef2e510cc57b6b1f1c089aa760cb8f14cb0c6aa1337c91ae8ddd3",
    0x90B1C: "2204f55e2a6c3d524c76e245c298df39306401d179e92274c7bd5adec0c61fca",
    0x90B8A: "cbf0a4dbcfd4ac88cfe0d54f2657f2874d1fbea48b872404743d3b86e99eccd4",
    0x90D6A: "35f2d6793551e9624ea98bcad296eda11c060b891faf9e25ec34e6d8ff9a2906",
  }
  for entry, rec in funcs.items():
    assert hashlib.sha256(body_bytes(image, rec)).hexdigest() == expected_body_sha[entry]

  # Freshness is resolved before the CMAC worker.  A freshness hard failure/retry
  # therefore normally precedes Gate-2; the installed stage-4 development patch is
  # a separate receiver modification and does not change the stock contract proved here.
  c = funcs[0x8F746]["decompiled_c"]
  assert c.index("FUN_0008f434") < c.index("iVar8 == 0x22") < c.index("FUN_0008f676")
  assert "iVar8 == 0x23" in c and "iVar8 == 0x24" in c

  # FV4 is exactly message-low2 || reset-low2 for the four-byte B6 trailer.
  c = funcs[0x90736]["decompiled_c"]
  assert "param_2 == 4" in c
  assert "*(ushort *)(param_3 + 2) = (ushort)(*param_1 >> 6)" in c
  assert "bVar1 = *param_1 >> 4" in c
  assert "= bVar1 & 3" in c

  # Exact reset reconstruction searches current,-1,+1,-2,+2.  The arithmetic is
  # target-native; this is why a frame near a 0x00F transition can remain fresh.
  c = funcs[0x909CA]["decompiled_c"]
  for token in ("DAT_febe55c4", "uVar1 = uVar1 - 1", "uVar1 = uVar1 + 1",
                "uVar1 = uVar1 - 2", "uVar1 = uVar1 + 2"):
    assert token in c

  # The decisive point: when authenticated trip/reset is newer than B6's committed
  # ordinary slot, F33 copies the *received* message-low bits into pending message8.
  # There is no fixed first-in-epoch value of 0 or 1 to satisfy.
  c = funcs[0x90A48]["decompiled_c"]
  assert "uVar3 = *(undefined2 *)(param_2 + 8);" in c
  assert "*(undefined2 *)(param_4 + 2) = uVar3;" in c
  assert "if ((uVar6 == uVar7) && (param_3[2] == uVar8))" in c
  assert "uVar4 = *(ushort *)(param_2 + 8) | ~((short)uVar8 - 1U) & uVar2;" in c
  assert "*(ushort *)(param_4 + 2) = (short)uVar6 + uVar4;" in c

  # B6's normal profile is one of the two ordinary current/pending freshness slots.
  c = funcs[0x90248]["decompiled_c"]
  assert "if (2 < uVar7)" in c
  assert "param_2[1] = sVar3" in c
  c = funcs[0x90B8A]["decompiled_c"]
  assert "FUN_00090736" in c and "FUN_00090b1c" in c
  assert "param_1[1] * 0xc + -0x620c" in c  # pending ordinary slots
  c = funcs[0x90D6A]["decompiled_c"]
  assert "param_1 < 2" in c and "param_2 == '\\x01'" in c
  assert "-0x6224" in c and "-0x620c" in c  # pending -> committed

  data = json.loads(ARTIFACT.read_text())
  assert data["schema"] == "camry-b6-freshness-contract-v1"
  assert data["scope"]["eps"] == "8965F3307000"
  assert len(data["routes"]) == 13
  assert sum(len(r["inventory"]) for r in data["routes"]) == 530
  assert sum(r["total_rlog_bytes"] for r in data["routes"]) == 5_328_786_933
  assert all(len(x["sha256"]) == 64 for r in data["routes"] for x in r["inventory"])

  phase = data["phase_exhaustive_check"]
  assert phase["new_epoch_start_low2_accepted"] == {"0": True, "1": True, "2": True, "3": True}
  assert phase["same_epoch_next_from_message_0"] == {"0": 4, "1": 1, "2": 2, "3": 3}

  agg = data["aggregate"]
  # Every retained B6 send maps to the exact F33 reset/message reconstruction model.
  # The single sendcan reset mismatch is reconstructed by the stock ±2 reset window.
  b6 = agg["comma_b6"]
  assert b6["send_frames"] == b6["mapped_frames"] == b6["receiver_model_accept_count"] == 1_696_097
  assert b6["unmapped_before_same_bus_sync"] == 0
  assert b6["reset_candidate_offsets"] == {"-1": 1, "0": 1_696_096}
  assert b6["same_epoch_delta_mod4"] == {"1": 1_593_784}
  assert b6["first_message_low2"] == {"0": 99_214, "1": 1_033, "2": 1_028, "3": 1_038}
  # These routes all predate CORR-176's restored dummy-CMAC sender.
  assert b6["zero_mac28_frames_historical_corpus"] == 1_696_097

  # More importantly, model the frames Panda reports as actually transmitted.  All
  # 1.55M successful echoes remain within F33's ordinary freshness reconstruction;
  # rejected returns are counted separately and were not treated as received by EPS.
  tx = agg["panda_b6_tx"]
  assert tx["successful_echoes"] == tx["mapped_successful_echoes"] == tx["receiver_model_accept_count"] == 1_554_213
  assert tx["rejected_returns"] == 141_875
  assert sum(tx["receiver_model_reasons"].values()) == tx["successful_echoes"]

  # The only incoming src<3 B6 population is an old route-27 reflection/forward of
  # comma traffic: every payload occurs exactly in that route's sendcan set.  No
  # independent factory B6 sample is hidden in the retained Camry corpus.
  assert agg["incoming_b6_frames_all_native_planes"] == 106_800
  assert agg["incoming_b6_exact_payload_matches_route_sendcan"] == 106_800
  assert agg["incoming_b6_payload_not_in_route_sendcan"] == 0

  # Latest corrected-format routes are the most relevant current-state witnesses.
  routes = {r["route_name"]: r for r in data["routes"]}
  for route_name, send_count, echo_count, reject_count in (
    ("00000045--805b7ca6ab", 43_093, 43_083, 9),
    ("00000048--709f22277b", 21_347, 21_339, 8),
  ):
    r = routes[route_name]
    send = r["comma_b6"]["0"]
    txr = r["panda_b6_tx"]["0"]
    assert send["send_count"] == send_count
    assert send["first_message_low2_by_observed_epoch"] == {"0": send["receiver_model_reasons"]["newer_epoch_seed_from_wire_low2"]}
    assert send["same_epoch_message_low2_delta_mod4"] == {"1": send["same_epoch_pairs"]}
    assert send["receiver_model_accept_count"] == send_count
    assert txr["successful_echoes"] == txr["receiver_model_accept_count"] == echo_count
    assert txr["rejected_returns"] == reject_count

  route48 = routes["00000048--709f22277b"]
  sync0 = route48["native"]["0"]
  assert sync0["sync_trip_changes"] == 0
  assert sync0["sync_same_trip_reset_deltas"] == {"1": 1_461}
  assert sync0["first_sync_trip_reset"] == [506, 48]
  assert sync0["last_sync_trip_reset"] == [506, 1509]

  print("camry exact-F33 B6 freshness contract: PASS")
  return 0


if __name__ == "__main__":
  raise SystemExit(main())
