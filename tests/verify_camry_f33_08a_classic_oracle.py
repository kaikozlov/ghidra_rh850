#!/usr/bin/env python3
"""Verify the exact-F33 raw classic-CAN 0x08A signing mailbox contract."""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from exploit.ephemeral_runtime import build_camry_f33_08a_classic_oracle as build
from exploit.ephemeral_runtime import camry_f33_08a_classic_oracle as host
from exploit.ephemeral_runtime import camry_f33_oracle_ui_bringup as ui_bringup

OUT = ROOT / "build/out/ephemeral-runtime/camry-f33-08a-classic-oracle"
FAST_OUT = ROOT / "build/out/ephemeral-runtime/camry-f33-08a-classic-oracle-idle-fast"
AUDIT = ROOT / "exploit/ephemeral_runtime/audited_camry_f33_08a_classic_oracle_build.json"
AUDITED_STAGE = ROOT / "exploit/ephemeral_runtime/audited/camry_f33_08a_classic_oracle.bin"
LAUNCHER = ROOT / "exploit/ephemeral_runtime/camry_f33_08a_classic_oracle_launcher.sh"

subprocess.run([sys.executable, str(build.BUILDER)], cwd=ROOT, check=True, stdout=subprocess.DEVNULL)
subprocess.run(
    [sys.executable, str(build.BUILDER), "--idle-fast-path"],
    cwd=ROOT, check=True, stdout=subprocess.DEVNULL,
)
meta = json.loads((OUT / "camry_f33_08a_classic_oracle.json").read_text())
fast_meta = json.loads((FAST_OUT / "camry_f33_08a_classic_oracle.json").read_text())
resident = (OUT / meta["resident"]["path"]).read_bytes()
fast_resident = (FAST_OUT / fast_meta["resident"]["path"]).read_bytes()
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
check("road-qualified default remains byte-exact while idle-fast is separate",
      meta["variant"] == "road-qualified-baseline" and
      meta["idle_fast_path"]["enabled"] is False and
      fast_meta["variant"] == "idle-fast-path-candidate" and
      fast_meta["idle_fast_path"] == {
          "behavior": "while the foreground flag is clear, scan only when the private cursor trails the producer and more than 3 ms remains; recheck the flag immediately before helper entry; retain the post-drain fallback",
          "count_hz": 80_000_000,
          "counter": "TAUJ0CNT3",
          "counter_address": "0xFFE5001C",
          "direction": "down",
          "enabled": True,
          "foreground_flag": "FFFFB111 bit4",
          "minimum_remaining_counts": 240_000,
          "minimum_remaining_us": 3_000,
      } and
      len(fast_resident) == 476 and fast_meta["resident"]["headroom"] == 48 and
      fast_resident != resident and fast_meta["helper"]["sha256"] == meta["helper"]["sha256"])
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
check("idle-fast timer gate is bound to exact firmware geometry",
      fw["foreground_timer"] == {
          "timer": "TAUJ0 channel 3",
          "counter": "TAUJ0CNT3",
          "counter_address": "0xFFE5001C",
          "count_hz": 80_000_000,
          "steady_counts": 400_000,
          "steady_period_us": 5_000,
          "direction": "down",
          "flag": "FFFFB111 bit4",
      })
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
summary = host.latency_summary([4.0, 1.0, 3.0, 2.0])
check("parked benchmark reports deterministic distribution statistics",
      {name: round(value, 3) for name, value in summary.items()} == {
          "mean_ms": 2.5, "median_ms": 2.5, "p95_ms": 3.85, "p99_ms": 3.97, "max_ms": 4.0,
      })

class FakeDiagnosticClient:
    def __init__(self): self.sessions = []
    def diagnostic_session_control(self, session): self.sessions.append(session)

diagnostic_session = host.ClassicOracleSession.__new__(host.ClassicOracleSession)
diagnostic_session.client = FakeDiagnosticClient()
diagnostic_session.uds_mod = SimpleNamespace(
    SESSION_TYPE=SimpleNamespace(EXTENDED_DIAGNOSTIC="extended"),
)
diagnostic_session.refresh_extended_session()
check("benchmark can refresh extended diagnostic after a long timing run",
      diagnostic_session.client.sessions == ["extended"])

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
      resident_src.index("jarl32 target_rx_3, lp") < resident_src.rindex("jarl32 helper_entry, lp") and
      "ld.hu -0x6f08[gp]" in resident_src and "st.h r7, 0x4a7c[gp]" in resident_src)
check("idle-fast gate is timer-bounded and preserves post-drain fallback",
      ".ifdef ORACLE_IDLE_FAST_PATH" in resident_src and
      "mov 0xffe5001c, r8" in resident_src and "ld.w 0[r8], r8" in resident_src and
      "mov 240000, r9" in resident_src and "bnh .L_tick_wait" in resident_src and
      resident_src.count("tst1 4, -0x4eef[r0]") >= 2 and
      resident_src.index("jarl32 helper_entry, lp") < resident_src.index("jarl32 target_rx_3, lp"))
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

class _FakeOracleSession:
    def __init__(self, *_args, **_kwargs):
        self.attestation = {"state": {"initialized": True}}
    def close(self):
        pass

with (mock.patch.object(host, "verify_nrtd_ready", side_effect=AssertionError("NRTD guard must be skipped from exact boot")),
      mock.patch.object(host, "execute_ram_payload", return_value={"direct_bootloader": True}) as execute,
      mock.patch.object(host, "wait_for_f181", return_value={"ok": True}),
      mock.patch.object(host, "ClassicOracleSession", _FakeOracleSession),
      mock.patch.object(host.time, "sleep", return_value=None)):
    direct = host.install(OUT / meta["authenticated_payload"]["path"], OUT / "camry_f33_08a_classic_oracle.json", direct_boot=True)
check("classic oracle can continue directly from exact caught bootloader without NRTD recheck",
      direct["entry_condition"] == "exact_bootloader_f181" and direct["nrtd_guard"] is None and
      direct["verdict"] == "runtime_08a_classic_oracle_resident_live_helper_pending_known_answer" and
      execute.call_args.kwargs["allow_direct_boot"] is True)

startup_src = (ROOT / "exploit/ephemeral_runtime/camry_f33_startup_programming.py").read_text(encoding="utf-8")
ui_src = (ROOT / "exploit/ephemeral_runtime/camry_f33_oracle_ui_bringup.py").read_text(encoding="utf-8")
check("startup catcher uses the field-proven response-synchronized minimum ladder",
      'EXTENDED_FRAME = bytes.fromhex("0210030000000000")' in startup_src and
      'PROGRAMMING_FRAME = bytes.fromhex("0210020000000000")' in startup_src and
      'POSITIVE_EXTENDED_FRAME = bytes.fromhex("065003003201f400")' in startup_src and
      startup_src.index('data == POSITIVE_EXTENDED_FRAME') < startup_src.index('panda.can_send(TX_ADDR, PROGRAMMING_FRAME, BUS)') and
      'SecurityAccess' in startup_src and 'persistent_flash_writes' in startup_src)
check("UI backend verifies healthy peers and oracle KAT without mandatory peer resets",
      ui_src.index('race_to_bootloader()') < ui_src.index('install(payload, meta, direct_boot=True)') <
      ui_src.index('ready_guard = wait_ready_parked') < ui_src.index('state = control_domain_state') <
      ui_src.index('kat = known_answer(meta)') and
      'restart_brake_known_good' not in ui_src and 'restart_one_domain' not in ui_src and
      'peer_resets_performed": False' in ui_src)

native_marker = {
    "schema": "tss3-oracle-native-catch-v1",
    "target": "TOYOTA_CAMRY_TSS3",
    "armed_monotonic_ns": 100,
    "ignition_observed_monotonic_ns": 200,
    "first_extended_tx_monotonic_ns": 110,
    "positive_extended_monotonic_ns": 300,
    "programming_tx_monotonic_ns": 310,
    "verdict": "programming_request_sent_after_exact_50_03",
}
with tempfile.TemporaryDirectory() as td:
    marker_path = Path(td) / "native-catch.json"
    marker_path.write_text(json.dumps(native_marker), encoding="utf-8")
    check("UI resume accepts only an ordered exact-F33 native startup catch",
          ui_bringup.load_native_catch(marker_path) == native_marker)
    marker_path.write_text(json.dumps({**native_marker, "target": "TOYOTA_COROLLA_TSS3"}), encoding="utf-8")
    try:
        ui_bringup.load_native_catch(marker_path)
    except ui_bringup.UiBringupError:
        pass
    else:
        raise AssertionError("UI resume accepted a non-F33 native startup catch")

launcher = LAUNCHER.read_text(encoding="utf-8")
recovery = launcher.split("  recover-peers)\n", 1)[1].split("  status)", 1)[0]
check("standalone classic-oracle kit includes guarded Brake then FRC peer recovery",
      "camry_f33_post_install_recovery.py" in launcher and
      "--nrtd-confirmed" in launcher and "NRTD / Park / stationary" in launcher and
      recovery.index("quiesce_panda_owner") <
      recovery.index("restart-domain --domain brake") <
      recovery.index("restart-domain --domain frc") <
      recovery.index("state --output") and
      "output directory is not empty" in recovery)

print("PASS camry F33 raw classic-CAN 0x08A oracle")
