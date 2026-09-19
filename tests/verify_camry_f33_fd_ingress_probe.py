#!/usr/bin/env python3
"""Verify exact-F33 standard-ID CAN-FD ingress probe."""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from exploit.ephemeral_runtime import build_camry_f33_fd_ingress_probe as build
from exploit.ephemeral_runtime import camry_f33_fd_ingress_probe as host

OUT = ROOT / "build/out/ephemeral-runtime/camry-f33-fd-ingress-probe"
AUDIT = ROOT / "exploit/ephemeral_runtime/audited_camry_f33_fd_ingress_probe_build.json"
AUDITED_STAGE = ROOT / "exploit/ephemeral_runtime/audited/camry_f33_fd_ingress_probe.bin"

subprocess.run([sys.executable, str(build.BUILDER)], cwd=ROOT, check=True, stdout=subprocess.DEVNULL)
meta = json.loads((OUT / "camry_f33_fd_ingress_probe.json").read_text())
resident = (OUT / meta["resident"]["path"]).read_bytes()
helper = (OUT / meta["helper"]["path"]).read_bytes()
stage = (OUT / meta["staging"]["path"]).read_bytes()
payload = (OUT / meta["authenticated_payload"]["path"]).read_bytes()


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def check(name: str, cond: object) -> None:
    if not cond:
        raise AssertionError(name)
    print(f"PASS {name}")


check("audited build exact", json.loads(AUDIT.read_text()) == meta and AUDITED_STAGE.read_bytes() == stage)
check("resident/helper fit RAM",
      len(resident) == 412 and meta["resident"]["headroom"] == 112 and
      len(helper) == 232 and meta["helper"]["headroom"] == 792 and
      meta["resident"]["relocations"] == 0 and meta["helper"]["relocations"] == 0)
check("hashes self-consistent",
      sha(resident) == meta["resident"]["sha256"] and
      sha(helper) == meta["helper"]["sha256"] and
      sha(stage) == meta["staging"]["sha256"] and
      sha(payload) == meta["authenticated_payload"]["sha256"])

probe = meta["firmware_contract"]["probe"]
check("probe is exact native standard FD090 route",
      probe == {
          "can_id": "0x090",
          "format": "standard CAN-FD",
          "length": 32,
          "rule_index": 35,
          "rule": ["0x00000090", "0x002C0000", "0x00000002", "0x00000000"],
          "canif_word": "0x40000090",
          "pdu": 40,
          "secoc_lower_destination": "0xFFFF",
      })
check("observer is pre-checksum ring boundary",
      meta["firmware_contract"]["rx_ring"]["base"] == "0xFEBE4038" and
      meta["firmware_contract"]["rx_ring"]["fd32_record_words"] == 11 and
      "pre-CanIf checksum gate" in meta["firmware_contract"]["rx_ring"]["observation"])
check("mutation contract observational only",
      meta["mutation_boundary"] == {
          "persistent_flash_write": False,
          "rscfd_reconfiguration": False,
          "rx_queue_mutation": False,
          "checksum_state_mutation": False,
          "com_state_mutation": False,
          "secoc_state_mutation": False,
          "eps_can_transmit": False,
      })

native = bytes(range(32))
marker = host.build_marker(native)
check("host marker exact",
      len(marker) == 32 and marker[:8] == b"PFD090!!" and marker[8:] == native[8:] and marker != native)

raw = bytearray(host.STATE_SIZE)
raw[0:4] = host.STATE_MAGIC.to_bytes(4, "little")
raw[4] = host.STATE_VERSION
raw[5] = 1
raw[8:12] = (123).to_bytes(4, "little")
raw[12:16] = (1).to_bytes(4, "little")
raw[16:20] = (0x00000120).to_bytes(4, "little")
raw[20:24] = (0x40000090).to_bytes(4, "little")
raw[24:56] = marker
raw[56:60] = int.from_bytes(marker[:4], "little").to_bytes(4, "little")
raw[60:64] = int.from_bytes(marker[4:8], "little").to_bytes(4, "little")
state = host.decode_state(bytes(raw))
check("state decoder exact",
      state["magic_ok"] and state["version_ok"] and state["initialized"] and
      state["fd090_count"] == 123 and state["marker_count"] == 1 and
      state["last_id_word"] == "0x40000090" and state["last_marker_payload_hex"] == marker.hex())

resident_src = build.RESIDENT_SOURCE.read_text()
helper_src = build.HELPER_SOURCE.read_text()
check("helper runs before stock drain",
      resident_src.index("jarl32 helper_entry, lp") < resident_src.index("jarl32 target_rx_3, lp"))
check("helper exact-matches standard FD090",
      "mov 0x40000090" in helper_src and "PFD090!!" in helper_src and
      "cmp 32, r11" in helper_src)
check("helper has no external calls or RX-ring writes",
      "jarl32 " not in helper_src and
      "st.h" not in helper_src and
      "-0x6f06[gp]" in helper_src and "-0x6f04[gp]" in helper_src)

print("PASS camry F33 standard-ID CAN-FD ingress probe")
