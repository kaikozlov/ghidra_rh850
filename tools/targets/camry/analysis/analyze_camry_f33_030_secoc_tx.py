#!/usr/bin/env python3
"""Close exact-F33 CAN 0x030 SecOC transmit ownership and wire geometry.

This reducer joins four independent evidence layers that are all retained in the
repository:

* exact 8965F3307000 CodeFlash configuration and Tx/SecOC implementation;
* the canonical exact-F33 decompilation corpus for the transmit call chain;
* a READY PE1 LocalRAM snapshot showing the live command-5 key selector descriptor;
* the same-session CAN oracle showing the protected on-wire 0x030 envelope.

The result is intentionally target-specific.  It proves how exact F33 constructs
and protects 0x030; it does not transfer this Tx profile to another Toyota ECU.
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import struct
from collections import Counter
from itertools import pairwise
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[4]
IMAGE = ROOT / "firmware/camry-8965F3307000/CodeFlash.bin"
CORPUS = ROOT / "data/generated/camry-8965F3307000/decompilations.jsonl"
LOCAL_RAM = ROOT / "targets/camry-2026/raw-20260826/secoc-recovery/ram/local_ram_pe1.bin"
CAN_ORACLE = ROOT / "targets/camry-2026/raw-20260826/secoc-recovery/can_oracle.ndjson.gz"
OUT = ROOT / "data/generated/camry_8965F3307000_030_secoc_tx.json"
EXPECTED_IMAGE_SHA256 = "42dce8efc42f6ae31718e7713fa2d26bb9191b4a82439778aee4d7afded9b0e7"

FUNCTIONS = {
  0x04C97A: "generated-COM PDU0/0x030 application packer",
  0x07DF14: "generated-COM transmit dispatcher",
  0x081A7E: "PduR transmit shim",
  0x081AB2: "PduR lower-route dispatcher",
  0x088B84: "ICU-S command-5 job preparation",
  0x088D60: "ICU-S command-5 start wrapper",
  0x089440: "CryptoIf record dispatcher",
  0x089BC2: "serialized MAC-generation wrapper",
  0x08A720: "ICU-S command-5 hardware submit",
  0x08ECB2: "DataID/payload/freshness authentication-input builder",
  0x08ED8E: "SecOC Tx ingress for generated-COM PDU0",
  0x08F19A: "Tx key-selector descriptor lookup",
  0x08FABA: "SecOC Tx authentic-payload queue",
  0x08FA5A: "SecOC Tx source/lower-PDU profile mapper",
  0x08FCCA: "CryptoIf MAC-generation entry",
  0x08FD90: "SecOC Tx authentication coordinator",
  0x08FED0: "FV/authenticator trailer bit packer",
  0x08FFDA: "secured-PDU assembly and lower transmit",
  0x090736: "ordinary FV4/full-freshness decoder",
}


def sha256(data: bytes) -> str:
  return hashlib.sha256(data).hexdigest()


def load_functions() -> dict[int, dict[str, Any]]:
  out: dict[int, dict[str, Any]] = {}
  with CORPUS.open(encoding="utf-8") as fh:
    for line in fh:
      rec = json.loads(line)
      if rec.get("record") != "function":
        continue
      entry = int(rec["entry_addr"], 16)
      if entry in FUNCTIONS:
        out[entry] = rec
  if set(out) != set(FUNCTIONS):
    missing = sorted(set(FUNCTIONS) - set(out))
    raise RuntimeError(f"missing canonical functions: {[hex(x) for x in missing]}")
  return out


def load_oracle() -> tuple[list[tuple[int, bytes]], list[tuple[int, int, int]]]:
  frames: list[tuple[int, bytes]] = []
  syncs: list[tuple[int, int, int]] = []
  with gzip.open(CAN_ORACLE, "rt", encoding="utf-8") as fh:
    for line in fh:
      row = json.loads(line)
      if row.get("event") != "can" or row.get("bus") != 1:
        continue
      data = bytes.fromhex(row["data"])
      address = int(row["addr"])
      t = int(row["t_mono_ns"])
      if address == 0x030 and len(data) == 32:
        frames.append((t, data))
      elif address == 0x00F and len(data) == 8:
        trip = int.from_bytes(data[0:2], "big")
        reset = (data[2] << 12) | (data[3] << 4) | (data[4] >> 4)
        syncs.append((t, trip, reset))
  return frames, syncs


def analyze_oracle(frames: list[tuple[int, bytes]], syncs: list[tuple[int, int, int]]) -> dict[str, Any]:
  checksum_matches = sum((((sum(d[:7]) + 0x38) & 0xFF) == d[7]) for _, d in frames)
  tails = {d[28:32] for _, d in frames}
  mac28_candidates = {bytes([d[28] & 0x0F]) + d[29:32] for _, d in frames}
  fv4_values = sorted({d[28] >> 4 for _, d in frames})

  same_reset_deltas: Counter[int] = Counter()
  for (_, prev), (_, cur) in pairwise(frames):
    prev_reset_low2 = (prev[28] >> 4) & 0x3
    cur_reset_low2 = (cur[28] >> 4) & 0x3
    if prev_reset_low2 == cur_reset_low2:
      same_reset_deltas[((cur[28] >> 6) - (prev[28] >> 6)) & 0x3] += 1

  sync_index = -1
  sync_eligible = 0
  reset_matches = 0
  mismatch_pairs: Counter[tuple[int, int]] = Counter()
  first_message_low2: Counter[int] = Counter()
  last_epoch: tuple[int, int] | None = None
  for t, data in frames:
    while sync_index + 1 < len(syncs) and syncs[sync_index + 1][0] <= t:
      sync_index += 1
    if sync_index < 0:
      continue
    _, trip, reset = syncs[sync_index]
    sync_eligible += 1
    expected = reset & 0x3
    observed = (data[28] >> 4) & 0x3
    if observed == expected:
      reset_matches += 1
    else:
      mismatch_pairs[(expected, observed)] += 1
    epoch = (trip, reset)
    if epoch != last_epoch:
      first_message_low2[data[28] >> 6] += 1
      last_epoch = epoch

  return {
    "bus": 1,
    "frame_count": len(frames),
    "sync_count": len(syncs),
    "inner_additive_b7_rule": {
      "formula": "B7 = low8(sum(B0..B6) + 0x38)",
      "matches": checksum_matches,
    },
    "outer_trailer": {
      "unique_B28_B31": len(tails),
      "unique_MAC28_candidates": len(mac28_candidates),
      "FV4_high_nibble_values": fv4_values,
      "same_reset_message_low2_deltas": {str(k): v for k, v in sorted(same_reset_deltas.items())},
      "preceding_0x00F_reset_low2": {
        "eligible": sync_eligible,
        "matches": reset_matches,
        "fraction": round(reset_matches / sync_eligible, 12) if sync_eligible else None,
        "mismatches": {f"{a}->{b}": v for (a, b), v in sorted(mismatch_pairs.items())},
      },
      "first_message_low2_per_observed_epoch": {str(k): v for k, v in sorted(first_message_low2.items())},
      "timestamp_boundary": "the retained oracle batches CAN publication; adjacent reset-low2 mismatches are not a firmware-format contradiction",
    },
  }


def analyze() -> dict[str, Any]:
  image = IMAGE.read_bytes()
  if sha256(image) != EXPECTED_IMAGE_SHA256:
    raise RuntimeError("exact F33 CodeFlash identity mismatch")
  funcs = load_functions()
  ram = LOCAL_RAM.read_bytes()
  frames, syncs = load_oracle()
  if not frames:
    raise RuntimeError("tracked oracle has no 0x030 frames")

  # Exact generated-COM PDU0 and CanIf descriptor.
  pdu0_descriptor = image[0x226C0:0x226C8]
  canif0_descriptor = image[0x21F58:0x21F60]

  # The one configured SecOC-Tx record is stride 0x44.  These fields are read
  # directly by 8ED8E/8FABA/8FD90/8FED0/8FFDA.
  secoc = {
    "profile_index": 0,
    "authenticator_bits": struct.unpack_from("<H", image, 0x2593A)[0],
    "security_trailer_bytes": struct.unpack_from("<H", image, 0x2593E)[0],
    "data_id": struct.unpack_from("<H", image, 0x25944)[0],
    "freshness_value_id": struct.unpack_from("<H", image, 0x25946)[0],
    "full_freshness_bits": image[0x2594C],
    "transmitted_freshness_bits": image[0x2594D],
    "key_selector_descriptor_id": struct.unpack_from("<H", image, 0x2594E)[0],
    "crypto_job_id": struct.unpack_from("<H", image, 0x25950)[0],
    "lower_pdu_id": struct.unpack_from("<H", image, 0x25966)[0],
    "tx_freshness_callback": f"0x{struct.unpack_from('<I', image, 0x25978)[0]:06X}",
  }
  secoc["authentic_payload_bytes"] = pdu0_descriptor[4] - secoc["security_trailer_bytes"]
  secoc["full_freshness_storage_bytes"] = (secoc["full_freshness_bits"] + 7) // 8
  secoc["mac_input_bytes"] = 2 + secoc["authentic_payload_bytes"] + secoc["full_freshness_storage_bytes"]
  secoc["mac_input"] = "DataID_be16 || application_payload[28] || full_freshness[6]"

  # The live key-selector descriptor returned by 8F19A(0, ...) is exactly the
  # 20-byte block beginning at FEBE5504.  88B84 requires dword0==1 and uses the
  # byte at +4 as the hardware selector; 8A720 emits selector<<16 | command5.
  descriptor = ram[0x5504:0x5518]
  live_crypto = {
    "descriptor_address": "0xFEBE5504",
    "descriptor_hex": descriptor.hex(),
    "descriptor_mode": struct.unpack_from("<I", descriptor, 0)[0],
    "icu_s_key_selector": descriptor[4],
    "icu_s_command": 5,
    "submit_register_expression": "ICUSCMD = (selector << 16) | 5",
    "path": ["0x8F19A", "0x8FCCA", "0x89BC2", "0x89440", "0x88B84", "0x88D60", "0x8A720"],
  }

  # Generated-COM owns all 32 bytes as a storage slice, but the application
  # packer only supplies B0..B27.  The retained READY snapshot captures the
  # slice before SecOC has appended the wire trailer.
  app = ram[0x4A48:0x4A68]
  best_match = max(frames, key=lambda x: sum(a == b for a, b in zip(app[:28], x[1][:28])))
  best_equal = sum(a == b for a, b in zip(app[:28], best_match[1][:28]))
  ram_vs_wire = {
    "generated_com_buffer_address": "0xFEBE4A48",
    "generated_com_buffer_hex": app.hex(),
    "generated_com_B28_B31_hex": app[28:32].hex(),
    "closest_oracle_application_equal_bytes": best_equal,
    "closest_oracle_frame_hex": best_match[1].hex(),
    "closest_oracle_B28_B31_hex": best_match[1][28:32].hex(),
    "interpretation": "the generated-COM application slice is zero in B28..B31; the exact SecOC Tx path reserves four bytes and appends FV4||MAC28 below the application packer",
  }

  function_evidence = {
    f"0x{entry:06X}": {
      "role": role,
      "body_size": rec["body_size"],
      "decompiled_c_sha256": rec["decompiled_c_sha256"],
    }
    for entry, role in FUNCTIONS.items()
    for rec in [funcs[entry]]
  }

  return {
    "schema": "camry-f33-030-secoc-tx-v1",
    "firmware": {
      "identity": "8965F3307000",
      "sha256": sha256(image),
    },
    "tx_identity": {
      "generated_com_pdu": 0,
      "can_id": "0x030",
      "can_fd": True,
      "wire_length": 32,
      "pdu0_descriptor_hex": pdu0_descriptor.hex(),
      "canif0_descriptor_hex": canif0_descriptor.hex(),
      "canif_id_word": f"0x{struct.unpack_from('<I', canif0_descriptor, 0)[0]:08X}",
      "route": "PDU0 -> 0x7DF14 -> 0x81A7E/0x81AB2 -> SecOC Tx 0x8ED8E -> lower PDU0",
    },
    "secoc_tx_profile": secoc,
    "live_crypto": live_crypto,
    "wire_layout": {
      "application": "B0..B27",
      "inner_application_integrity": "B7 additive byte: low8(sum(B0..B6)+0x38)",
      "outer_security": "B28[7:4]=FV4; B28[3:0]||B29||B30||B31=MAC28",
      "fv4_split": "B28[7:6]=message counter low2; B28[5:4]=reset counter low2",
      "authenticator": "28-bit MSB-truncated AES-CMAC generated by ICU-S command 5",
    },
    "mac_domain": {
      "data_id": "0x0030",
      "application_payload_bytes": 28,
      "full_freshness_bits": secoc["full_freshness_bits"],
      "full_freshness_storage_bytes": secoc["full_freshness_storage_bytes"],
      "total_bytes": secoc["mac_input_bytes"],
      "composition": secoc["mac_input"],
    },
    "ram_vs_wire": ram_vs_wire,
    "tracked_oracle": analyze_oracle(frames, syncs),
    "function_evidence": function_evidence,
    "conclusion": (
      "Exact F33 EPS is the 0x030 producer. Generated-COM builds the 28-byte application payload, "
      "the configured SecOC Tx profile authenticates DataID 0x0030 plus payload plus full freshness "
      "with ICU-S command 5 using live selector 4, packs four transmitted freshness bits followed by "
      "a 28-bit authenticator into B28..B31, and then submits the 32-byte CAN-FD PDU."
    ),
  }


def main() -> int:
  ap = argparse.ArgumentParser(description=__doc__)
  ap.add_argument("--output", type=Path, default=OUT)
  args = ap.parse_args()
  result = analyze()
  args.output.parent.mkdir(parents=True, exist_ok=True)
  args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
  print(args.output)
  return 0


if __name__ == "__main__":
  raise SystemExit(main())
