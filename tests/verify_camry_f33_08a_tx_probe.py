#!/usr/bin/env python3
"""Verify the exact-F33 non-actuating EPS-origin 0x08A routing discriminator."""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from exploit.ephemeral_runtime import (
  build_camry_f33_08a_tx_probe as build,
)
from exploit.ephemeral_runtime import camry_f33_08a_tx_probe as probe
from exploit.ephemeral_runtime.camry_f33_runtime_monitor import PandaTap


def sha(raw: bytes) -> str:
  return hashlib.sha256(raw).hexdigest()


def main() -> int:
  print("== deterministic build ==")
  with tempfile.TemporaryDirectory(prefix="verify-camry-f33-08a-tx-") as td:
    out = Path(td)
    run = subprocess.run(
      [sys.executable, str(build.BUILDER), "--output-dir", str(out)],
      cwd=ROOT, capture_output=True, text=True, check=False,
    )
    assert run.returncode == 0, run.stderr[-1000:]
    meta = json.loads((out / "camry_f33_08a_tx_probe.json").read_text(encoding="utf-8"))
    resident = (out / meta["resident"]["path"]).read_bytes()
    helper = (out / meta["helper"]["path"]).read_bytes()
    stage = (out / meta["staging"]["path"]).read_bytes()
    payload = (out / meta["authenticated_payload"]["path"]).read_bytes()

  audited_stage = ROOT / "exploit/ephemeral_runtime/audited/camry_f33_08a_tx_probe.bin"
  audited_meta = ROOT / "exploit/ephemeral_runtime/audited_camry_f33_08a_tx_probe_build.json"
  assert audited_stage.read_bytes() == stage
  assert json.loads(audited_meta.read_text(encoding="utf-8")) == meta

  assert meta["schema"] == "camry-f33-08a-tx-probe-build-v1"
  assert meta["target"] == {"software_id": "8965F3307000", "codeflash_sha256": build.IMAGE_SHA256}
  assert (len(resident), sha(resident)) == (probe.RESIDENT_SIZE, probe.EXPECTED_RESIDENT_SHA256)
  assert (len(helper), sha(helper)) == (probe.HELPER_SIZE, probe.EXPECTED_HELPER_SHA256)
  assert (len(stage), sha(stage)) == (978, probe.EXPECTED_STAGING_SHA256)
  assert (len(payload), sha(payload)) == (0x1000, probe.EXPECTED_PAYLOAD_SHA256)
  assert meta["resident"]["headroom"] == build.RESIDENT_LIMIT - probe.RESIDENT_SIZE == 240
  assert meta["helper"]["headroom"] == build.UNIVERSAL_HELPER_TRANSIT_LIMIT - probe.HELPER_SIZE == 714
  assert meta["helper"]["jarl_targets"] == ["0x00085112"]
  assert meta["resident"]["jarl_targets"][-1] == "0xFEF07C00"
  assert meta["staging"]["resident_offset"] == 0x180
  assert meta["staging"]["helper_offset"] == 0x29C
  assert meta["helper"]["mpu"]["mpu_region"] == 12
  assert meta["helper"]["mpu"]["ctx0_mpat"] == meta["helper"]["mpu"]["ctx1_mpat"] == "0x000000B8"
  assert meta["helper"]["mpu"]["aligned_codeflash_pointer_hits"] == []

  print("== exact lower-Tx contract ==")
  tx = meta["tx"]
  assert tx == {
    "stock_lower_write": "0x00085112",
    "canif_hth_index": 0,
    "lower_driver_object_id": 47,
    "lower_driver_node": 1,
    "lower_driver_mailbox": 0,
    "pending_handle_cell": "0xFEBE502A",
    "can_id": "0x08A",
    "can_id_word": "0x4000008A",
    "can_fd": True,
    "length": 32,
    "sw_pdu_handle": "0x00F0",
    "idle_sw_pdu_handle": "0xFFFF",
    "tx_confirmation": "0x00F0 pending ownership ends on completion; successor may be idle 0xFFFF or stock 0x030; 0x00F0 confirmation itself dispatches FUN_0008043C special path -> no-op 0x0008152E",
    "semantic_guard": "B21[5:0] must equal Target Lateral ID 0",
    "success_limit_per_boot": 1,
    "completion_required_before_routing_verdict": True,
  }
  image = build.IMAGE.read_bytes()
  assert image[0x85112:0x8511A] == bytes.fromhex("8607e1f006c8d900")
  assert image[0x85168:0x85170] == bytes.fromhex("039d034080ff3203")
  assert image[0x21F58:0x21F60] == bytes.fromhex("3000004000000000")
  assert int.from_bytes(image[0x218E4:0x218E8], "little") == 0x21ACC
  assert image[0x21ACC:0x21AD6] == bytes.fromhex("0d00020100002f000000")
  assert int.from_bytes(image[0x22E38:0x22E3C], "little") == 0x22DB8
  assert image[0x22DB8 + 47 * 2:0x22DB8 + 47 * 2 + 2] == bytes((1, 0))
  assert int.from_bytes(image[0x22E3C:0x22E3E], "little") == 47
  assert image[0x8152E:0x81530] == bytes.fromhex("7f00")
  helper_source = build.HELPER_SOURCE.read_text(encoding="utf-8")
  assert "mov 0x4000008a, r6" in helper_source
  assert "ld.bu 0x4825[gp], r6" in helper_source and "andi 0x3f, r6, r6" in helper_source
  assert "jarl32 lower_can_write, lp" in helper_source
  assert "command5" not in helper_source and "0x0b6" not in helper_source.lower()

  print("== host protocol and fail-closed shape ==")
  assert probe.command_frame(0x12, 0x45, 0x44332211) == bytes.fromhex("00c8124511223344")
  frame = bytearray(32)
  frame[21] = 0
  frame[28:32] = bytes.fromhex("d1234567")
  raw = bytearray(probe.MAILBOX_SIZE)
  raw[0:4] = probe.MAILBOX_MAGIC.to_bytes(4, "little")
  raw[4:8] = bytes((probe.MAILBOX_VERSION, 0x44, 3, 0))
  raw[8] = 0xFF
  raw[0x0A] = 1
  raw[0x0B] = 1
  raw[0x0C:0x0E] = (0xFFFF).to_bytes(2, "little")
  raw[0x10:0x30] = frame
  raw[0x30:0x32] = (0x00F0).to_bytes(2, "little")
  raw[0x32] = 32
  raw[0x34:0x38] = (0x4000008A).to_bytes(4, "little")
  raw[0x38:0x3C] = (0xFEBF0010).to_bytes(4, "little")
  decoded = probe.decode_mailbox(bytes(raw))
  assert decoded["magic_ok"] and decoded["version_ok"]
  assert decoded["state_name"] == "tx_completed" and decoded["enqueue_count"] == 1 and decoded["completion_count"] == 1 and decoded["completion_successor_handle"] == "0xFFFF"
  assert decoded["input_complete"] and decoded["frame_hex"] == frame.hex()
  assert decoded["target_lateral_id"] == 0
  assert decoded["can_pdu"] == {
    "sw_pdu_handle": 0x00F0, "length": 32, "id_word": "0x4000008A", "data_pointer": "0xFEBF0010",
  }

  fake = object.__new__(probe.TxProbeSession)
  fake_state = {
    **decoded, "last_sequence": 0, "input_bitmap": 0, "input_complete": False,
    "frame_hex": (bytes(32)).hex(), "target_lateral_id": 0, "tx_count": 0,
    "enqueue_count": 0, "completion_count": 0,
  }
  staged = bytearray(32)
  bitmap = 0
  def fake_send(opcode: int, argument: int, predicate):
    nonlocal bitmap
    word = opcode - probe.OP_WORD_BASE
    staged[word * 4:(word + 1) * 4] = argument.to_bytes(4, "little")
    bitmap |= 1 << word
    state = {
      **fake_state,
      "last_sequence": word + 1,
      "input_bitmap": bitmap,
      "input_complete": bitmap == 0xFF,
      "frame_hex": bytes(staged).hex(),
      "target_lateral_id": staged[21] & 0x3F,
    }
    assert predicate(state)
    return {"sequence": word + 1, "opcode": f"0x{opcode:02X}", "frame_hex": "", "state": state}
  def fake_read_state():
    return {
      **fake_state,
      "input_bitmap": bitmap,
      "input_complete": bitmap == 0xFF,
      "frame_hex": bytes(staged).hex(),
      "target_lateral_id": staged[21] & 0x3F,
    }
  fake._send = fake_send
  fake.read_state = fake_read_state
  loaded = fake.load_exact_frame(bytes(frame))
  assert loaded["state"]["input_complete"] and loaded["state"]["frame_hex"] == frame.hex()
  active = bytearray(frame)
  active[21] = 11
  try:
    fake.load_exact_frame(bytes(active))
  except probe.TxProbeError:
    pass
  else:
    raise AssertionError("host accepted active Target Lateral ID")

  print("== physical completion host contract ==")
  tx_session = object.__new__(probe.TxProbeSession)
  initial = {**decoded, "state": 0, "state_name": "assembling", "lower_driver_return_code": 0,
             "enqueue_count": 0, "completion_count": 0, "tx_count": 0,
             "completion_successor_handle": "0x0000"}
  pending = {**initial, "state": 2, "state_name": "tx_pending", "enqueue_count": 1, "tx_count": 1}
  completed = {**pending, "state": 3, "state_name": "tx_completed", "completion_count": 1,
               "completion_successor_handle": "0x0000"}
  read_states = [initial, completed]
  tx_session.read_state = lambda: read_states.pop(0)
  def fake_tx_send(opcode: int, argument: int, predicate):
    assert opcode == probe.OP_TRANSMIT and argument == 0 and predicate(pending)
    return {"sequence": 0x55, "opcode": "0x48", "frame_hex": "", "state": pending}
  tx_session._send = fake_tx_send
  final, attempts = tx_session.transmit_once()
  assert final["state_name"] == "tx_completed" and final["completion_count"] == 1
  assert final["completion_successor_handle"] == "0x0000"  # stock 0x030 may already own HTH0
  assert len(attempts) == 1 and attempts[0]["enqueue_count"] == 1

  print("== Panda observation persistence ==")
  class FakePanda:
    def __init__(self):
      self.rows = [[
        (0x08A, bytes(frame), 1),
        (0x0B6, bytes(range(32)), 1),
        (0x08A, bytes(frame), 129),
      ]]
    def can_recv(self):
      return self.rows.pop(0) if self.rows else []
  tap = PandaTap(FakePanda())
  tap.can_recv()
  assert tap.latest(1, 0x08A)[1] == bytes(frame)
  snap = tap.native_08a_snapshot()
  assert snap["count"] == 1 and snap["events"][0]["bus"] == 1 and snap["events"][0]["data_hex"] == frame.hex()
  assert tap.native_b6_snapshot()["count"] == 1

  print("== mutation boundary ==")
  boundary = meta["mutation_boundary"]
  assert boundary == {
    "persistent_flash_write": False,
    "command5_call": False,
    "secoc_bypass": False,
    "b6_transmit": False,
    "host_08a_transmit": False,
    "eps_08a_transmit_max": 1,
    "frame_mutation_inside_eps": False,
    "intended_input": "byte-exact captured native 0x08A with Target Lateral ID 0",
  }
  launcher = (ROOT / "exploit/ephemeral_runtime/camry_f33_08a_tx_probe_launcher.sh").read_text(encoding="utf-8")
  assert "./f33-08a-route route-native-id0 [OUTPUT_JSON]" in launcher
  assert "camry_f33_08a_tx_probe_payload.bin" in launcher
  assert probe.EXPECTED_PAYLOAD_SHA256 in launcher
  assert "route-native-id0 does NOT construct or sign a new 0x08A" in launcher
  assert "run_probe_bounded 20 route-native-id0 --execute --parked-stationary-confirmed" in launcher

  plan = probe.plan(None)
  assert plan["boundaries"]["host_transmitted_08a"] is False
  assert plan["boundaries"]["eps_transmitted_08a_max"] == 1
  assert plan["boundaries"]["frame_mutation"] is False
  assert plan["boundaries"]["active_lateral_request"] is False
  assert "prove that exact FV4/MAC-bearing frame does not naturally repeat" in plan["field_sequence"][3]

  print("PASS: exact-F33 EPS-origin 0x08A routing discriminator")
  return 0


if __name__ == "__main__":
  raise SystemExit(main())
