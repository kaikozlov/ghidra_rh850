#!/usr/bin/env python3
"""Verify the canonical exact-target classic-CAN 0x08A signing mailbox."""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import threading
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

from tools import REPO_ROOT
ROOT = REPO_ROOT

from exploit.ephemeral_runtime import build_camry_f33_08a_classic_oracle as build
from exploit.ephemeral_runtime import camry_f33_08a_classic_oracle as host
from exploit.ephemeral_runtime import camry_f33_oracle_ui_bringup as ui_bringup
from exploit.common import ram_exec

CAMRY_TARGET = "camry-8965F3307000"
CAMRY_STEM = build.output_stem(CAMRY_TARGET)
OUT = build.default_output_dir(CAMRY_TARGET, idle_fast_path=True)
FOREGROUND_OUT = build.default_output_dir(CAMRY_TARGET, idle_fast_path=False)

subprocess.run(
    [sys.executable, str(build.BUILDER), "--target", CAMRY_TARGET],
    cwd=ROOT, check=True, stdout=subprocess.DEVNULL,
)
subprocess.run(
    [sys.executable, str(build.BUILDER), "--target", CAMRY_TARGET, "--foreground-only"],
    cwd=ROOT, check=True, stdout=subprocess.DEVNULL,
)
target_meta = {}
with tempfile.TemporaryDirectory(prefix="verify-tss3-08a-oracle-") as td:
    for target in sorted(set(build.ORACLE_PROFILES) - {CAMRY_TARGET}):
        target_out = Path(td) / target
        proc = subprocess.run(
            [sys.executable, str(build.BUILDER), "--target", target, "--output-dir", str(target_out)],
            cwd=ROOT, check=True, capture_output=True, text=True,
        )
        target_meta[target] = json.loads(proc.stdout)
meta_path = OUT / f"{CAMRY_STEM}.json"
meta = json.loads(meta_path.read_text())
foreground_meta = json.loads((FOREGROUND_OUT / f"{CAMRY_STEM}.json").read_text())
resident = (OUT / meta["resident"]["path"]).read_bytes()
foreground_resident = (FOREGROUND_OUT / foreground_meta["resident"]["path"]).read_bytes()
helper = (OUT / meta["helper"]["path"]).read_bytes()


def check(name: str, cond: object) -> None:
    if not cond:
        raise AssertionError(name)
    print(f"PASS {name}")


class _TransientF181Client:
    def __init__(self, payload: bytes | None):
        self.payload = payload

    def read_data_by_identifier(self, _did):
        if self.payload is None:
            raise TimeoutError("boot endpoint is still transitioning")
        return self.payload


boot_f181 = bytes.fromhex("02" + "21" * 32)
transient_clients = iter((_TransientF181Client(None), _TransientF181Client(boot_f181)))
with mock.patch.object(ram_exec, "_make_uds_client", side_effect=lambda *args, **kwargs: next(transient_clients)):
    identity_client, identity_hex, _, identity_attempts = ram_exec._wait_for_f181_response(
        object(), SimpleNamespace(DATA_IDENTIFIER_TYPE=SimpleNamespace(APPLICATION_SOFTWARE_IDENTIFICATION=0xF181)),
        ram_exec.explicit_route(bus=0, elm327_param=1, uds_variant="old", cpu_index=0), timeout=0.5,
    )
check("caught boot identity retries with a fresh UDS transport after a transient miss",
      identity_client.payload == boot_f181 and identity_hex == boot_f181.hex() and identity_attempts == 2)


check("idle-fast Camry default and foreground-only reference remain separate",
      len(foreground_resident) <= foreground_meta["resident"]["limit"] and
      foreground_resident != resident and foreground_meta["helper"]["sha256"] == meta["helper"]["sha256"])
check("resident/helper fit proven RAM geometry",
      len(resident) <= meta["resident"]["limit"] and
      len(helper) <= meta["helper"]["limit"] and
      meta["resident"]["headroom"] == meta["resident"]["limit"] - len(resident) and
      meta["helper"]["headroom"] == meta["helper"]["limit"] - len(helper) and
      meta["resident"]["relocations"] == 0 and meta["helper"]["relocations"] == 0)
check("host-visible state and private scratch preserve exact safe boundaries",
      host.STATE_SIZE == build.STATE_SIZE == 0x24 and
      build.STATE_BASE + build.STATE_SIZE == build.CLASSIC_SCRATCH_BASE == 0xFEBF0280 and
      build.STATE_BASE + build.STATE_SIZE <= build.APPLICATION_RMBA_PROTECTED_START and
      build.CLASSIC_SCRATCH_BASE + build.CLASSIC_SCRATCH_SIZE == build.SECOC_OBJECT15_BASE and
      meta["state"]["application_sid23_readable"] is True and
      meta["scratch"] == {
          "base": "0xFEBF0280", "size": 0x68, "end_exclusive": "0xFEBF02E8",
          "object15_overlap": False,
      })


def run_core_simulator() -> str:
    tmp_root = ROOT / "build/tmp"
    tmp_root.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="oracle-core-sim-", dir=tmp_root) as td:
        elf = Path(td) / "core.elf"
        rel_elf = elf.relative_to(ROOT)
        subprocess.run([
            str(ROOT / "tools/rh850"), "exec", "v850-elf-gcc",
            "-mv850e3v5", "-mno-app-regs", "-ffreestanding", "-fno-builtin", "-Os", "-nostdlib",
            "-Wa,-mv850e3v5,-mextension",
            "-Wl,-T,tests/fixtures/rh850/camry_f33_08a_oracle_core_sim.ld",
            "-Wl,--build-id=none",
            "tests/fixtures/rh850/camry_f33_08a_oracle_core_sim.S",
            "tests/fixtures/rh850/camry_f33_08a_oracle_core_sim.c",
            "-o", str(rel_elf),
        ], cwd=ROOT, check=True, capture_output=True, text=True)
        proc = subprocess.run([
            str(ROOT / "tools/rh850"), "sim", str(rel_elf),
            "--memory-region", "0xFEBF0000,0x10000",
            "-ex", "break rh850_sim_stop",
            "-ex", "run",
            "-ex", (
                'printf "ORACLE_SIM_RESULT=0x%x FAILURE=%u PASSES=%u\\n", '
                '*(unsigned int *)&oracle_sim_result, '
                '*(unsigned int *)&oracle_sim_failure, '
                '*(unsigned int *)&oracle_sim_passes'
            ),
        ], cwd=ROOT, check=True, capture_output=True, text=True)
        return proc.stdout + proc.stderr


simulator_output = run_core_simulator()
check("production pure-core macros execute under GNU RH850 sim",
      "ORACLE_SIM_RESULT=0x8a0c0de FAILURE=0 PASSES=30" in simulator_output)

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
check("stock functional rule supplies the canonical raw-ring request carrier",
      fw["request"] == {
          "can_id": "0x00000777",
          "hardware_classic_word": "0x00000777",
          "label": "0x35",
          "rule": 53,
          "record_header": "0x00000408",
          "canif_row": "0x00021FA8",
      })
check("software RX ring exposes independent producer geometry",
      fw["rx_ring"]["base"] == "0xFEBE4038" and
      fw["rx_ring"]["end_inclusive"] == "0xFEBE48D7" and
      fw["rx_ring"]["capacity_words"] == 0x228 and
      fw["rx_ring"]["classic8_record_words"] == 5 and
      fw["rx_ring"]["classic8_record_bytes"] == 20)
check("paired response uses the stock primary diagnostic resource",
      fw["response"]["can_id"] == "0x000007A9" and
      fw["response"]["lower_handle"] == 53 and
      fw["response"]["controller"] == 1 and fw["response"]["resource"] == 6 and
      fw["response"]["software_confirmation_handle"] == "0x00F0")
check("state read boundary is pinned to the exact application SID23 exclusion",
      fw["application_rmba_exclusion"] == {
          "start": "0xFEBF0288", "end_inclusive": "0xFEBF13CB",
      } and meta["state"]["base"] == "0xFEBF025C" and meta["state"]["size"] == 0x24)

application = bytes(range(28))
req = host.build_request(application, 0xA7)
check("host request is the four-frame full-payload nibble codec used by every target",
      len(req) == 4 and all(len(frame) == 8 for frame in req) and
      [frame[0] for frame in req] == [0x87, 0x9A, 0xA7, 0xBA] and
      b"".join(frame[1:] for frame in req) == application)
check("all exact targets select that same wire protocol from profile data",
      set(build.ORACLE_PROFILES) == {
          "camry-8965F3307000", "crown-8965F3012000",
          "corolla-8965H1202000", "corolla-8965F1208000",
      } and all(
          profile["carrier"] == "functional-nibble4" and profile["request_id"] == 0x777 and
          profile["response_id"] == 0x7A9 and profile["fragment_count"] == 4 and
          profile["helper_macros"]["ORACLE_REQUEST_HEADER_WORD"] == 0x00000408
          for profile in build.ORACLE_PROFILES.values()
      ))
check("Corolla H/F and Crown lifecycle variants compile from the same canonical sources",
      set(target_meta) == {
          "crown-8965F3012000", "corolla-8965H1202000", "corolla-8965F1208000",
      } and all(target_meta[target]["target"]["name"] == target for target in target_meta) and
      all(target_meta[target]["request"]["carrier"] == "functional-nibble4" for target in target_meta) and
      all(target_meta[target]["request"]["can_id"] == "0x00000777" for target in target_meta) and
      all(target_meta[target]["request"]["bus"] == 1 for target in target_meta) and
      all(target_meta[target]["response"]["can_id"] == "0x000007A9" for target in target_meta) and
      all(target_meta[target]["state"]["size"] == 0x24 for target in target_meta) and
      all(target_meta[target]["resident"]["size"] <= target_meta[target]["resident"]["limit"] for target in target_meta) and
      all(target_meta[target]["helper"]["size"] <= target_meta[target]["helper"]["limit"] for target in target_meta) and
      target_meta["corolla-8965H1202000"]["resident"]["sha256"] ==
          target_meta["corolla-8965F1208000"]["resident"]["sha256"] and
      target_meta["corolla-8965H1202000"]["helper"]["sha256"] ==
          target_meta["corolla-8965F1208000"]["helper"]["sha256"] and
      target_meta["corolla-8965H1202000"]["scratch"]["base"] == "0xFEF07F98" and
      target_meta["corolla-8965F1208000"]["scratch"]["base"] == "0xFEF07F98" and
      target_meta["crown-8965F3012000"]["scratch"]["base"] == "0xFEBF0280" and
      target_meta["crown-8965F3012000"]["runtime_profile"]["response_lower_handle"] == 51)
try:
    host.meta_transport({
        "request": {"can_id": "0x1FDC0002", "bus": 0, "carrier": "raw-extended"},
        "response": {"can_id": "0x1FE00002", "bus": 0},
    })
except host.ClassicOracleError:
    pass
else:
    raise AssertionError("host accepted the retired second carrier")
print("PASS host rejects the retired extended-XCP carrier")
resp = host.parse_response(bytes.fromhex("c90700f8d64e2a5e"), expected_seq=0x07)
check("host response decoder matches resident layout",
      resp.seq == 0x07 and resp.status == 0 and resp.trailer == bytes.fromhex("d64e2a5e"))
summary = host.latency_summary([4.0, 1.0, 3.0, 2.0])
check("parked benchmark reports deterministic distribution statistics",
      {name: round(value, 3) for name, value in summary.items()} == {
          "mean_ms": 2.5, "median_ms": 2.5, "p95_ms": 3.85, "p99_ms": 3.97, "max_ms": 4.0,
      })


class _FakePipelinedPanda:
    def __init__(self):
        self._lock = threading.Lock()
        self._rx: list[tuple[int, bytes, int]] = []
        self.request_count = 0

    def can_send_many(self, rows):
        first = int(rows[0][1][0])
        second = int(rows[1][1][0])
        seq = ((second & 0x0F) << 4) | (first & 0x0F)
        with self._lock:
            self.request_count += 1
            trailer = bytes((0x10 | (self.request_count & 0x0F), seq, 0xA5, 0x5A))
            self._rx.append((host.RESPONSE_ID, bytes((host.RESPONSE_MAGIC, seq, 0, seq ^ 0xFF)) + trailer, host.BUS))

    def can_recv(self):
        with self._lock:
            rows, self._rx = self._rx, []
        return rows


class _FakePipelinedSession:
    last = None

    def __init__(self, *_args, **_kwargs):
        self.panda = _FakePipelinedPanda()
        self.transport = {
            "request_id": host.REQUEST_ID, "request_bus": host.BUS,
            "response_id": host.RESPONSE_ID, "response_bus": host.BUS,
            "carrier": host.REQUEST_CARRIER,
        }
        self.attestation = {"state": {"initialized": True}}
        self.refreshed = False
        _FakePipelinedSession.last = self

    def read_state(self):
        count = self.panda.request_count
        return {
            "assembly_seq": 0,
            "request_count": count,
            "success_count": count,
            "response_count": count,
        }

    def refresh_extended_session(self):
        self.refreshed = True

    def close(self):
        pass


with mock.patch.object(host, "ClassicOracleSession", _FakePipelinedSession):
    pipelined = host.benchmark_pipelined(
        meta_path, count=3, period_ms=10.0, drain_timeout_s=0.1,
    )
check("100-Hz benchmark pipelines requests without waiting for each reply",
      pipelined["schema"] == "tss3-08a-classic-oracle-pipelined-benchmark-v1" and
      pipelined["count_sent"] == pipelined["success_count"] == pipelined["responses_received"] == 3 and
      pipelined["target_rate_hz"] == 100.0 and pipelined["complete_target_rate_run"] is True and
      pipelined["resident_counter_deltas"] == {"request_count": 3, "success_count": 3, "response_count": 3} and
      pipelined["boundaries"]["sender_waits_for_response"] is False and
      pipelined["boundaries"]["transmitted_08a"] is False and
      _FakePipelinedSession.last is not None and _FakePipelinedSession.last.refreshed)


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
# helper execution proof to the live fresh-signing self-test.
state = bytearray(host.STATE_SIZE)
state[0:4] = host.STATE_MAGIC.to_bytes(4, "little")
state[4] = host.STATE_VERSION
state[5] = 1
state[24:28] = (0x34567).to_bytes(4, "little")
state[28:30] = (0x1234).to_bytes(2, "little")
state[30] = 0x56
state[31] = 1
state[32:34] = (0x01A3).to_bytes(2, "little")
state[34] = 0x0B
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
      att["helper_attestation"] == "deferred_to_self_test_execution" and
      att["state"]["freshness_reset"] == 0x34567 and
      att["state"]["freshness_trip"] == 0x1234 and
      att["state"]["freshness_message"] == 0x56 and
      att["state"]["freshness_initialized"] is True and
      att["state"]["tap_cursor"] == 0x01A3 and att["state"]["last_fv4"] == 0x0B)

check("no diagnostic transport or RSCFD mutation remains",
      meta["request"]["diagnostic_acceptance_route_used"] is True and
      meta["request"]["diagnostic_stack_used"] is False and
      meta["request"]["isotp_reassembly_used"] is False and
      meta["request"]["dcm_buffer_used"] is False and
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

class _FakeOracleSession:
    def __init__(self, *_args, **_kwargs):
        self.attestation = {"state": {"initialized": True}}
    def close(self):
        pass

with (mock.patch.object(host, "verify_nrtd_ready", side_effect=AssertionError("NRTD guard must be skipped from exact boot")),
      mock.patch.object(host, "execute_ram_payload", return_value={"direct_bootloader": True}) as execute,
      mock.patch.object(host, "wait_for_f181", return_value={"ok": True}) as wait_for_application,
      mock.patch.object(host, "ClassicOracleSession", _FakeOracleSession),
      mock.patch.object(host.time, "sleep", return_value=None)):
    direct = host.install(OUT / meta["authenticated_payload"]["path"], meta_path, direct_boot=True)
check("classic oracle can continue directly from exact caught bootloader without NRTD recheck",
      direct["entry_condition"] == "exact_bootloader_f181" and direct["nrtd_guard"] is None and
      direct["verdict"] == "runtime_08a_classic_fresh_signer_live_helper_pending_self_test" and
      execute.call_args.kwargs["allow_direct_boot"] is True and
      wait_for_application.call_args.kwargs["timeout"] == host.APPLICATION_REAPPEAR_TIMEOUT_SECONDS == 3.0)

native_marker = {
    "schema": "tss3-oracle-native-catch-v1",
    "target": "TOYOTA_CAMRY_TSS3",
    "pandad_wrapper_pid": 1234,
    "ignition_monotonic_ns": 100,
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

print("PASS canonical exact-target classic-CAN 0x08A oracle")
