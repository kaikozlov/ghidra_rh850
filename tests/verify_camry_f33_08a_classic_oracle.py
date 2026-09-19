#!/usr/bin/env python3
"""Verify the exact-F33 raw classic-CAN 0x08A signing mailbox contract."""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from exploit.ephemeral_runtime import build_camry_f33_08a_classic_oracle as build
from exploit.ephemeral_runtime import camry_f33_08a_classic_oracle as host

OUT = ROOT / "build/out/ephemeral-runtime/camry-f33-08a-classic-oracle"
AUDIT = ROOT / "exploit/ephemeral_runtime/audited_camry_f33_08a_classic_oracle_build.json"
AUDITED_STAGE = ROOT / "exploit/ephemeral_runtime/audited/camry_f33_08a_classic_oracle.bin"

subprocess.run([sys.executable, str(build.BUILDER)], cwd=ROOT, check=True, stdout=subprocess.DEVNULL)
meta = json.loads((OUT / "camry_f33_08a_classic_oracle.json").read_text())
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


check("audited build is byte/metadata exact",
      json.loads(AUDIT.read_text()) == meta and AUDITED_STAGE.read_bytes() == stage)
check("resident/helper fit proven RAM geometry",
      len(resident) == 424 and meta["resident"]["headroom"] == 100 and
      len(helper) == 848 and meta["helper"]["headroom"] == 176 and
      meta["resident"]["relocations"] == 0 and meta["helper"]["relocations"] == 0)
check("artifact hashes self-consistent",
      sha(resident) == meta["resident"]["sha256"] and
      sha(helper) == meta["helper"]["sha256"] and
      sha(stage) == meta["staging"]["sha256"] and
      sha(payload) == meta["authenticated_payload"]["sha256"])

fw = meta["firmware_contract"]
check("dead XCP hardware endpoint is dedicated raw-classic request carrier",
      fw["request"] == {
          "can_id": "0x1FDC0002",
          "hardware_classic_word": "0x9FDC0002",
          "label": "0x37",
          "rfifo": 1,
          "rfifo_payload_bytes": 32,
          "rule": 46,
      })
check("software RX ring exposes independent producer geometry",
      fw["rx_ring"]["base"] == "0xFEBE4038" and
      fw["rx_ring"]["end_inclusive"] == "0xFEBE48D7" and
      fw["rx_ring"]["capacity_words"] == 0x228 and
      fw["rx_ring"]["classic8_record_words"] == 5 and
      fw["rx_ring"]["classic8_record_bytes"] == 20)
check("paired response uses stock controller1 resource8",
      fw["response"]["can_id"] == "0x1FE00002" and
      fw["response"]["lower_handle"] == 55 and
      fw["response"]["controller"] == 1 and fw["response"]["resource"] == 8 and
      fw["response"]["software_confirmation_handle"] == "0x00F0")

application = bytes(range(28))
req = host.build_request(application, 0x92, 0x12345, 0x07)
check("host request is five ordered classic fragments", req == [
    bytes.fromhex("0700010203040506"),
    bytes.fromhex("270708090a0b0c0d"),
    bytes.fromhex("470e0f1011121314"),
    bytes.fromhex("6715161718191a1b"),
    bytes.fromhex("879245c9a8f85aa5"),
])
resp = host.parse_response(bytes.fromhex("c90700f8d64e2a5e"), expected_seq=0x07)
check("host response decoder matches resident layout",
      resp.seq == 0x07 and resp.status == 0 and resp.cmac4 == bytes.fromhex("d64e2a5e"))

# Application RMBA cannot read the FEF0.... GlobalRAM helper span. Installer
# attestation must therefore read only the LocalRAM resident/state and defer
# helper execution proof to the live native-MAC known-answer.
state = bytearray(host.STATE_SIZE)
state[0:4] = host.STATE_MAGIC.to_bytes(4, "little")
state[4] = host.STATE_VERSION
state[5] = 1
orig_read_exact = host._read_exact
reads: list[int] = []
def fake_read_exact(_client, _uds_mod, address: int, size: int, *, label: str, attempts: int = 4) -> bytes:
    reads.append(address)
    if address == host.RESIDENT_BASE:
        return resident
    if address == host.STATE_BASE:
        return bytes(state)
    raise AssertionError(f"unexpected RMBA read 0x{address:08X} ({label})")
host._read_exact = fake_read_exact
try:
    sess = host.ClassicOracleSession.__new__(host.ClassicOracleSession)
    sess.meta = meta
    sess.client = object()
    sess.uds_mod = object()
    att = sess._attest()
finally:
    host._read_exact = orig_read_exact
check("live attestation never RMBA-reads GlobalRAM helper",
      reads == [host.RESIDENT_BASE, host.STATE_BASE] and
      att["resident_sha256"] == meta["resident"]["sha256"] and
      att["helper_attestation"] == "deferred_to_known_answer_execution")

# Native truth is captured at a real reset boundary where message8 is known to
# restart at one; this avoids pretending a historical freshness tuple is valid today.
def sync_frame(trip: int, reset: int) -> bytes:
    data = bytearray(8)
    data[0:2] = trip.to_bytes(2, "big")
    data[2] = (reset >> 12) & 0xFF
    data[3] = (reset >> 4) & 0xFF
    data[4] = (reset & 0xF) << 4
    return bytes(data)

def native_frame(b26: int, reset: int, message: int, mac28: int) -> bytes:
    app = bytearray(range(28))
    app[26] = (app[26] & 0xC0) | (b26 & 0x3F)
    fv4 = ((message & 0x3) << 2) | (reset & 0x3)
    return bytes(app) + ((fv4 << 28) | mac28).to_bytes(4, "big")

class FakePanda:
    def __init__(self, rows): self.rows = rows
    def can_recv(self):
        rows, self.rows = self.rows, []
        return rows

trip = 0x026C
reset0, reset1 = 0x12344, 0x12345
mac1 = 0x1234567
fake = FakePanda([
    (host.SYNC_ID, sync_frame(trip, reset0), host.SYNC_BUS),
    (host.NATIVE_08A_ID, native_frame(10, reset0, 0, 0x7654321), host.NATIVE_08A_BUS),
    (host.SYNC_ID, sync_frame(trip, reset1), host.SYNC_BUS),
    (host.NATIVE_08A_ID, native_frame(11, reset1, 1, mac1), host.NATIVE_08A_BUS),
])
vector = host.capture_native_vector(fake, timeout=0.1)
check("known-answer captures live native reset-boundary truth",
      vector.message_counter == 1 and vector.reset_counter == reset1 and
      vector.b26 == 11 and vector.native_mac28 == f"{mac1:07x}")

check("no diagnostic transport or RSCFD mutation remains",
      meta["request"]["diagnostic_stack_used"] is False and
      meta["request"]["stock_xcp_protocol_used"] is False and
      meta["mutation_boundary"] == {
          "persistent_flash_write": False,
          "rscfd_reconfiguration": False,
          "rx_queue_mutation": False,
          "fragment_retransmission_state": False,
          "xcp_protocol_dispatch": False,
          "dcm_or_cantp_use": False,
          "host_08a_transmit": False,
          "b6_transmit": False,
          "secoc_bypass": False,
          "key_extraction": False,
      })

resident_src = build.RESIDENT_SOURCE.read_text()
helper_src = build.HELPER_SOURCE.read_text()
check("resident private tap runs after stock receive drain",
      resident_src.index("jarl32 target_rx_3, lp") < resident_src.index("jarl32 helper_entry, lp") and
      "ld.hu -0x6f08[gp]" in resident_src and "st.h r7, 0x4a7c[gp]" in resident_src)
check("helper matches only exact classic rule46 ring record",
      "mov 0x00002008" in helper_src and "mov 0x9fdc0002" in helper_src and
      "movea 0xc9, r0, r8" in helper_src and "movea 0xa8, r0, r8" in helper_src and
      "movea 0x5a, r0, r8" in helper_src and "movea 0xa5, r0, r8" in helper_src)
check("helper has no truncated cmp-immediate literals",
      all(token not in helper_src for token in ("cmp 0xc9", "cmp 0xa8", "cmp 0x5a", "cmp 0xa5", "cmp 16")))
check("helper uses local freshness and fixed selector4",
      "ld.w -0x623c[gp]" in helper_src and "ld.w -0x6240[gp]" in helper_src and
      "jarl32 freshness_encode, lp" in helper_src and "jarl32 command5_sync, lp" in helper_src)
check("helper advances an independent producer cursor across stock drains and signing",
      "ld.hu -0x6f08[gp]" in helper_src and "ld.hu 0x4a7c[gp]" in helper_src and
      "st.h r18, 0x4a7c[gp]" in helper_src and "st.h r19, 0x4a7e[gp]" in helper_src and
      "br .L_reload_scan" in helper_src and "ld.hu -0x6f06[gp]" not in helper_src and
      "ld.hu -0x6f04[gp]" not in helper_src)
check("response bypasses XCP protocol completion",
      "movea 0x00f0" in helper_src and "movea 55, r0, r6" in helper_src and
      "jarl32 lower_can_write, lp" in helper_src)

print("PASS camry F33 raw classic-CAN 0x08A oracle")
