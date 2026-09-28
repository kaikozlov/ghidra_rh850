#!/usr/bin/env python3
"""Verify the canonical exact-target TSS3 RAM-resident request signer."""
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

from exploit.ephemeral_runtime import build_tss3_request_signer as build
from exploit.ephemeral_runtime import tss3_request_signer as host
from exploit.ephemeral_runtime import tss3_request_signer_compact as compact_host
from exploit.ephemeral_runtime import camry_f33_request_signer_ui_bringup as ui_bringup
from exploit.ephemeral_runtime import camry_f33_startup_programming as startup_programming
from exploit.common import ram_exec
from tools.targets.tss3.builders import build_tss3_ram_kit as ram_kit

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
compact_target_meta = {}
with tempfile.TemporaryDirectory(prefix="verify-tss3-request-signer-") as td:
    for target in sorted(build.REQUEST_PROFILES):
        if target != CAMRY_TARGET:
            target_out = Path(td) / f"{target}-four"
            proc = subprocess.run(
                [sys.executable, str(build.BUILDER), "--target", target, "--output-dir", str(target_out)],
                cwd=ROOT, check=True, capture_output=True, text=True,
            )
            target_meta[target] = json.loads(proc.stdout)
        compact_out = Path(td) / f"{target}-compact"
        compact_proc = subprocess.run(
            [
                sys.executable, str(build.BUILDER), "--target", target, "--codec", "compact",
                "--output-dir", str(compact_out),
            ],
            cwd=ROOT, check=True, capture_output=True, text=True,
        )
        compact_target_meta[target] = json.loads(compact_proc.stdout)
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

    def diagnostic_session_control(self, session):
        self.session = session


boot_f181 = bytes.fromhex("02" + "21" * 32)
transient_clients = iter((_TransientF181Client(None), _TransientF181Client(boot_f181)))
with mock.patch.object(ram_exec, "_make_uds_client", side_effect=lambda *args, **kwargs: next(transient_clients)):
    identity_client, identity_hex, _, identity_attempts = ram_exec._wait_for_f181_response(
        object(), SimpleNamespace(DATA_IDENTIFIER_TYPE=SimpleNamespace(APPLICATION_SOFTWARE_IDENTIFICATION=0xF181)),
        ram_exec.explicit_route(bus=0, elm327_param=1, uds_variant="old", cpu_index=0), timeout=0.5,
    )
check("caught boot identity retries with a fresh UDS transport after a transient miss",
      identity_client.payload == boot_f181 and identity_hex == boot_f181.hex() and identity_attempts == 2)

app_f181 = bytes.fromhex("023839363546333330373030300000000038413331313333303331303000000000")
transition_clients = iter((_TransientF181Client(app_f181), _TransientF181Client(boot_f181)))
with mock.patch.object(ram_exec, "_make_uds_client", side_effect=lambda *args, **kwargs: next(transition_clients)):
    transition_client, transition_hex, _, transition_attempts = ram_exec._wait_for_f181_response(
        object(), SimpleNamespace(DATA_IDENTIFIER_TYPE=SimpleNamespace(APPLICATION_SOFTWARE_IDENTIFICATION=0xF181)),
        ram_exec.explicit_route(bus=0, elm327_param=1, uds_variant="old", cpu_index=0), timeout=0.5,
        expected_f181_hex=boot_f181.hex(),
    )
check("caught PROGRAMMING ignores transitional application F181 until exact boot identity",
      transition_client.payload == boot_f181 and transition_hex == boot_f181.hex() and transition_attempts == 2)


class _FakeExecPanda:
    def set_safety_mode(self, *_args):
        pass
    def can_recv(self):
        return []

fake_exec_panda = _FakeExecPanda()
fake_boot_client = object()
route = ram_exec.explicit_route(bus=0, elm327_param=1, uds_variant="old", cpu_index=0)
with (mock.patch.dict(sys.modules, {"panda": SimpleNamespace(Panda=lambda *_a, **_k: fake_exec_panda)}),
      mock.patch.object(ram_exec, "ensure_boardd_stopped"),
      mock.patch.object(ram_exec, "_import_uds", return_value=SimpleNamespace()),
      mock.patch.object(ram_exec, "_wait_for_f181_response",
                        return_value=(fake_boot_client, boot_f181.hex(), None, 3)) as wait_exact_boot,
      mock.patch.object(ram_exec, "_enter_programming_bootloader",
                        side_effect=AssertionError("caught startup path must not request PROGRAMMING twice")),
      mock.patch.object(ram_exec, "_prepare_direct_bootloader",
                        return_value=(fake_boot_client, boot_f181.hex(), None,
                                      {"direct_bootloader": True}, {"status": "test"})) as prepare_direct,
      mock.patch.object(ram_exec, "_security_access", return_value=b"\x00" * 16),
      mock.patch.object(ram_exec, "_upload_and_trigger")):
    caught_exec = ram_exec.execute_ram_payload(
        b"\x00" * 0x1000,
        route=route,
        security_secret=b"\x00" * 16,
        timeout=0.0,
        expected_f181_hex=app_f181.hex(),
        expected_boot_f181_hex=boot_f181.hex(),
        geometry=ram_exec.explicit_ram_exec_geometry(load_addr=0xFEBF0000, evidence="test:caught-programming"),
        allow_direct_boot=True,
        programming_already_requested=True,
        panda=fake_exec_panda,
    )
check("caught PROGRAMMING execution path never re-enters the application handoff",
      caught_exec["direct_bootloader"] is True and caught_exec["programming_already_requested"] is True and
      wait_exact_boot.call_args.kwargs["expected_f181_hex"] == boot_f181.hex() and prepare_direct.call_count == 1)


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
      host.STATE_VERSION == build.STATE_VERSION == meta["state"]["version"] == 3 and
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
    with tempfile.TemporaryDirectory(prefix="request-signer-core-sim-", dir=tmp_root) as td:
        elf = Path(td) / "core.elf"
        rel_elf = elf.relative_to(ROOT)
        subprocess.run([
            str(ROOT / "tools/rh850"), "exec", "v850-elf-gcc",
            "-mv850e3v5", "-mno-app-regs", "-ffreestanding", "-fno-builtin", "-Os", "-nostdlib",
            "-Wa,-mv850e3v5,-mextension",
            "-Wl,-T,tests/fixtures/rh850/tss3_request_signer_core_sim.ld",
            "-Wl,--build-id=none",
            "tests/fixtures/rh850/tss3_request_signer_core_sim.S",
            "tests/fixtures/rh850/tss3_request_signer_core_sim.c",
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
      "ORACLE_SIM_RESULT=0x8a0c0de FAILURE=0 PASSES=36" in simulator_output)

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
four_frames = host.build_request(application, 0xA7)
check("host default codec transports all application bytes in four exact frames",
      four_frames == (
          bytes.fromhex("8700010203040506"),
          bytes.fromhex("9a0708090a0b0c0d"),
          bytes.fromhex("a70e0f1011121314"),
          bytes.fromhex("ba15161718191a1b"),
      ) and
      b"".join(frame[1:] for frame in four_frames) == application and
      host.build_request_frames(application, 0xA7) == four_frames)

compact_app = bytearray(host.SAFE_APPLICATION)
compact_app[18], compact_app[19], compact_app[26] = 0x34, 0x12, 0x21
compact_frame = compact_host.build_compact_frame(bytes(compact_app), 0xA1)
check("optional compact module retains its bounded reconstruction contract",
      compact_frame == bytes.fromhex("c0000000341200a1") and
      compact_host.compact_reconstruction(compact_frame)[2:] == bytes(compact_app) and
      compact_host.build_compact_frame(host.SAFE_APPLICATION, 0x40) ==
          bytes.fromhex("c000000000000040"))
for rejected_application, rejected_seq in (
    (bytes(range(28)), 0xA7),
    (host.SAFE_APPLICATION, 0x41),
    (bytes(bytearray(compact_app[:24]) + bytearray([100]) + bytes(compact_app[25:])), 0xA1),
):
    try:
        compact_host.build_compact_frame(rejected_application, rejected_seq)
    except ValueError:
        pass
    else:
        raise AssertionError("optional compact codec accepted a nonrepresentable application")
print("PASS optional compact codec rejects every nonrepresentable application")

expected_targets = {
    "camry-8965F3307000", "crown-8965F3012000",
    "corolla-8965H1202000", "corolla-8965F1208000",
}
check("all exact targets share codec-neutral firmware profiles",
      set(build.REQUEST_PROFILES) == expected_targets and
      all(
          profile["request_id"] == 0x777 and profile["response_id"] == 0x7A9 and
          profile["helper_macros"]["ORACLE_REQUEST_HEADER_WORD"] == 0x00000408 and
          "ORACLE_COMPACT_CODEC" not in profile["helper_macros"] and
          "carrier" not in profile and "frame_count" not in profile
          for profile in build.REQUEST_PROFILES.values()
      ))

four_target_meta = {CAMRY_TARGET: meta, **target_meta}
check("four-frame is the universal default metadata contract",
      set(four_target_meta) == expected_targets and
      all(item["schema"] == build.SCHEMA for item in four_target_meta.values()) and
      all(item["request"]["codec"] == "four-frame" for item in four_target_meta.values()) and
      all(item["request"]["carrier"] == "functional-nibble4" for item in four_target_meta.values()) and
      all(item["request"]["frame_count"] == 4 for item in four_target_meta.values()) and
      all(item["request"]["experimental"] is False for item in four_target_meta.values()) and
      "functional-compact1" not in json.dumps(meta))
check("compact helper builds only through explicit selection on every exact target",
      set(compact_target_meta) == expected_targets and
      all(item["request"]["codec"] == "compact" for item in compact_target_meta.values()) and
      all(item["request"]["carrier"] == "functional-compact1" for item in compact_target_meta.values()) and
      all(item["request"]["frame_count"] == 1 for item in compact_target_meta.values()) and
      all(item["request"]["experimental"] is True for item in compact_target_meta.values()) and
      all(item["helper"]["size"] <= item["helper"]["limit"] == 0x398
          for item in compact_target_meta.values()))
check("Corolla H/F and Crown lifecycle variants compile from the canonical four-frame sources",
      set(target_meta) == expected_targets - {CAMRY_TARGET} and
      all(target_meta[target]["target"]["name"] == target for target in target_meta) and
      all(target_meta[target]["request"]["can_id"] == "0x00000777" for target in target_meta) and
      all(target_meta[target]["request"]["bus"] == 1 for target in target_meta) and
      all(target_meta[target]["response"]["can_id"] == "0x000007A9" for target in target_meta) and
      all(target_meta[target]["state"]["size"] == 0x24 for target in target_meta) and
      all(target_meta[target]["resident"]["size"] <= target_meta[target]["resident"]["limit"] for target in target_meta) and
      all(target_meta[target]["helper"]["size"] <= target_meta[target]["helper"]["limit"] == 0x398 for target in target_meta) and
      all(target_meta[target]["helper"]["transit_limit"] == 0x400 for target in target_meta) and
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
except host.RequestSignerError:
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
        self.sent_frame_counts: list[int] = []
    def can_send_many(self, rows):
        if len(rows) != host.FRAGMENT_COUNT:
            raise AssertionError("default request signer must submit exactly four frames")
        frame_data = [bytes(row[1]) for row in rows]
        if [frame[0] >> 4 for frame in frame_data] != [8, 9, 10, 11]:
            raise AssertionError("default request-signer fragment order drift")
        seq = (frame_data[0][0] & 0x0F) | ((frame_data[1][0] & 0x0F) << 4)
        if b"".join(frame[1:] for frame in frame_data) != bytes(
            bytearray(host.SAFE_APPLICATION[:26]) + bytes((seq & 0x3F,)) + host.SAFE_APPLICATION[27:]
        ):
            raise AssertionError("default request-signer application transport drift")
        with self._lock:
            self.request_count += 1
            trailer = bytes((0x10 | (self.request_count & 0x0F), seq, 0xA5, 0x5A))
            self._rx.append((host.RESPONSE_ID, bytes((host.RESPONSE_MAGIC, seq, 0, seq ^ 0xFF)) + trailer, host.BUS))
            self.sent_frame_counts.append(len(rows))

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
            "codec": host.FOUR_FRAME_CODEC, "carrier": host.REQUEST_CARRIER,
        }
        self.vehicle_guard = {"ready": True}
        _FakePipelinedSession.last = self

    def close(self):
        pass


with mock.patch.object(host, "RequestSignerSession", _FakePipelinedSession):
    pipelined = host.benchmark_pipelined(
        meta_path, count=3, period_ms=10.0, drain_timeout_s=0.1,
    )
pipeline_session = _FakePipelinedSession.last
assert pipeline_session is not None
check("100-Hz benchmark pipelines requests without waiting for each reply",
      pipelined["schema"] == "tss3-request-signer-pipelined-benchmark-v1" and
      pipelined["count_sent"] == pipelined["success_count"] == pipelined["responses_received"] == 3 and
      pipelined["target_rate_hz"] == 100.0 and pipelined["complete_target_rate_run"] is True and
      pipelined["boundaries"]["sender_waits_for_response"] is False and
      pipelined["boundaries"]["transmitted_08a"] is False)

check("pipelined benchmark emits four ordered default frames per request",
      pipeline_session.panda.sent_frame_counts == [4, 4, 4] and
      all(
          len(sent["frames_hex"]) == 4 and
          [int(frame[:2], 16) >> 4 for frame in sent["frames_hex"]] == [8, 9, 10, 11]
          for sent in pipelined["rows"]
      ))



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
          "xcp_protocol_dispatch": False,
          "dcm_or_cantp_use": False,
          "host_08a_transmit": False,
          "b6_transmit": False,
          "secoc_bypass": False,
          "key_extraction": False,
      })

fake_probe_panda = _FakePipelinedPanda()
with (mock.patch.object(host, "verify_nrtd_ready", side_effect=AssertionError("NRTD guard must be skipped from exact boot")),
      mock.patch.object(host, "execute_ram_payload", return_value={"direct_bootloader": True}) as execute,
      mock.patch.object(host, "wait_for_f181", return_value={"ok": True}) as wait_for_application,
      mock.patch.object(host, "_alloutput_mode")):
    direct = host.install(
        OUT / meta["authenticated_payload"]["path"], meta_path,
        direct_boot=True, panda=fake_probe_panda,
    )
check("post-activation install success is proved by the signer response, not a second F181 check",
      direct["entry_condition"] == "exact_bootloader_f181" and direct["nrtd_guard"] is None and
      direct["verdict"] == "request_signer_live_probe_pass" and
      direct["signer_probe"]["passed"] is True and fake_probe_panda.request_count == 1 and
      execute.call_args.kwargs["allow_direct_boot"] is True and
      execute.call_args.kwargs["programming_already_requested"] is True and
      wait_for_application.call_count == 1 and
      wait_for_application.call_args.kwargs["expected_f181_hex"] == meta["target"]["application_f181_hex"])

fake_self_test_panda = _FakePipelinedPanda()
with (mock.patch.object(host, "_alloutput_mode"),
      mock.patch.object(host, "verify_ready_parked_on_panda", return_value={"ready": True})):
    signer_self_test = host.self_test(meta_path, panda=fake_self_test_panda)
check("fresh signer self-test needs no post-activation diagnostic transport",
      signer_self_test["passed"] is True and signer_self_test["response"]["status"] == 0 and
      fake_self_test_panda.request_count == 1)

class _FakeStartupRacePanda:
    def __init__(self):
        self.recv_calls = 0
        self.sent = []
    def set_power_save(self, _enabled):
        pass
    def set_safety_mode(self, *_args):
        pass
    def can_recv(self):
        self.recv_calls += 1
        if self.recv_calls == 2:
            return [(startup_programming.RX_ADDR, startup_programming.POSITIVE_EXTENDED_FRAME, startup_programming.BUS)]
        return []
    def can_send(self, address, data, bus):
        self.sent.append((address, bytes(data), bus))
    def close(self):
        pass

fake_race_panda = _FakeStartupRacePanda()
cancel_checks = iter((False, True))
with (mock.patch.object(startup_programming, "ensure_boardd_stopped"),
      mock.patch.dict(sys.modules, {"panda": SimpleNamespace(Panda=lambda *_a, **_k: fake_race_panda)})):
    try:
        startup_programming.race_to_bootloader(
            timeout=0.2, cancel_requested=lambda: next(cancel_checks),
        )
    except startup_programming.StartupProgrammingError as exc:
        cancel_error = str(exc)
    else:
        raise AssertionError("cooperative cancel crossed the PROGRAMMING boundary")
check("manual cancellation is honored after 50 03 but before the one-way 10 02 send",
      cancel_error == "startup race cancelled before PROGRAMMING" and
      any(data == startup_programming.EXTENDED_FRAME for _, data, _ in fake_race_panda.sent) and
      all(data != startup_programming.PROGRAMMING_FRAME for _, data, _ in fake_race_panda.sent))

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

with tempfile.TemporaryDirectory(prefix="verify-tss3-ram-kit-") as td:
    kit_root = Path(td) / "camry-kit"
    kit_manifest = ram_kit.build(CAMRY_TARGET, kit_root)
    ui_runtime = "runtime/exploit/ephemeral_runtime/camry_f33_request_signer_ui_bringup.py"
    startup_runtime = "runtime/exploit/ephemeral_runtime/camry_f33_startup_programming.py"
    help_result = subprocess.run(
        [str(kit_root / "tss3-request-signer"), "--help"],
        cwd=kit_root, check=True, capture_output=True, text=True,
    )
    check("Camry kit carries the canonical startup bringup backend",
          ui_runtime in kit_manifest["files"] and startup_runtime in kit_manifest["files"])
    check("canonical launcher owns the comma startup commands",
          all(command in help_result.stdout for command in (
              "ui-bringup", "ui-resume", "ui-worker", "ui-resume-warm",
          )))

print("PASS canonical exact-target TSS3 request signer")
