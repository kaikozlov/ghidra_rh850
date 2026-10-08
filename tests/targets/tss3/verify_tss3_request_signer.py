#!/usr/bin/env python3
"""Verify the dump-resolved universal TSS3 RAM-resident request signer."""
from __future__ import annotations

import copy
import tempfile
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

from exploit.ephemeral_runtime import build_tss3_request_signer as build
from exploit.ephemeral_runtime import tss3_request_signer as host
from exploit.ephemeral_runtime import tss3_request_signer_compact as compact_host
from exploit.ram_runtime.target_profiles import registered_specs, spec_from_codeflash
from exploit.ram_runtime.tss3_request_signer_contract import (
    ContractError,
    resolve_request_signer_contract,
)
from tools import REPO_ROOT

ROOT = REPO_ROOT

CAMRY_TARGET = "camry-8965F3307000"
SPECS = registered_specs()
BUILD_TEMP = tempfile.TemporaryDirectory(prefix="verify-tss3-request-signer-")
BUILD_ROOT = Path(BUILD_TEMP.name)
OUT = BUILD_ROOT / "default"
COMPACT_OUT = BUILD_ROOT / "compact"

meta = build.build_request_signer(target=CAMRY_TARGET, output_dir=OUT)
compact_meta = build.build_request_signer(target=CAMRY_TARGET, codec="compact", output_dir=COMPACT_OUT)
meta_path = OUT / "camry_8965F3307000_request_signer.json"


def check(name: str, cond: object) -> None:
    if not cond:
        raise AssertionError(name)
    print(f"PASS {name}")


synthetic_image = bytearray(SPECS[CAMRY_TARGET]["image"].read_bytes())
old_selector = SPECS[CAMRY_TARGET]["runtime_software_id"].encode("ascii")
new_selector = b"8965F3307999"
if synthetic_image.count(old_selector) != 1:
    raise AssertionError("Camry selector identity is not unique")
selector_offset = synthetic_image.find(old_selector)
synthetic_image[selector_offset:selector_offset + len(old_selector)] = new_selector
synthetic_path = BUILD_ROOT / "synthetic-new-profile-CodeFlash.bin"
synthetic_path.write_bytes(synthetic_image)
synthetic_spec = spec_from_codeflash(synthetic_path, known_specs=SPECS)
current_profiles = build.runtime_profiles(SPECS)
synthetic_compatibility = build.profile_status(synthetic_spec, current_profiles)
synthetic_profiles = build.runtime_profiles({
    **SPECS,
    synthetic_spec["name"]: synthetic_spec,
})


def run_core_simulator() -> str:
    import subprocess

    tmp_root = ROOT / "build/tmp"
    tmp_root.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="request-signer-core-sim-", dir=tmp_root) as td:
        elf = Path(td) / "core.elf"
        rel_elf = elf.relative_to(ROOT)
        subprocess.run([
            str(ROOT / "tools/rh850"), "toolchain", "run", "v850-elf-gcc",
            "-mv850e3v5", "-mno-app-regs", "-ffreestanding", "-fno-builtin", "-Os", "-nostdlib",
            "-Wa,-mv850e3v5,-mextension",
            "-Wl,-T,tests/fixtures/rh850/tss3_request_signer_core_sim.ld",
            "-Wl,--build-id=none",
            "tests/fixtures/rh850/tss3_request_signer_core_sim.S",
            "tests/fixtures/rh850/tss3_request_signer_core_sim.c",
            "-o", str(rel_elf),
        ], cwd=ROOT, check=True, capture_output=True, text=True)
        proc = subprocess.run([
            str(ROOT / "tools/rh850"), "test", "payload", str(rel_elf),
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

check("registered dump is already covered by the universal build",
      meta["compatibility"]["status"] == "covered-by-current-build")
check("missing selector extends the universal profile table without compilation",
      synthetic_compatibility["status"] == "compatible-profile-missing" and
      len(synthetic_profiles) == len(current_profiles) + 1 and
      any(
          row["software_id"] == new_selector.decode("ascii")
          for row in synthetic_profiles
      ))

conflicting_spec = copy.deepcopy(SPECS[CAMRY_TARGET])
conflicting_spec["runtime_config"]["app_context"] += 4
try:
    build.runtime_profiles({**SPECS, "conflict": conflicting_spec})
except RuntimeError:
    pass
else:
    raise AssertionError("universal profile table accepted an ambiguous selector")
print("PASS universal profile table rejects an ambiguous selector")

damaged_image = bytearray(SPECS[CAMRY_TARGET]["image"].read_bytes())
camry_contract = SPECS[CAMRY_TARGET]["contract"]
freshness_address = camry_contract["signer_abi"]["freshness_encode"]
damaged_image[freshness_address:freshness_address + 16] = b"\0" * 16
try:
    resolve_request_signer_contract(bytes(damaged_image))
except ContractError:
    pass
else:
    raise AssertionError("dump resolver accepted firmware without the signer freshness primitive")
print("PASS dump resolver rejects firmware with an unresolved signer ABI")

check("generated transports satisfy the host metadata contract",
      host.meta_transport(meta)["codec"] == "four-frame" and
      host.meta_transport(compact_meta)["codec"] == "compact")
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




class _FakeProbePanda:
    def __init__(self):
        self.request_count = 0
        self.rx: list[tuple[int, bytes, int]] = []

    def set_safety_mode(self, *_args):
        pass

    def can_send_many(self, frames):
        self.request_count += 1
        data = [bytes(frame[1]) for frame in frames]
        seq = (data[0][0] & 0x0F) | ((data[1][0] & 0x0F) << 4)
        self.rx.append((0x7A9, bytes((0xC9, seq, 0x00, seq ^ 0xFF, 0x10 | (self.request_count & 0x0F), seq, 0xA5, 0x5A)), 0))

    def can_recv(self):
        rows, self.rx = self.rx, []
        return rows

    def close(self):
        pass


fake_probe_panda = _FakeProbePanda()
with (mock.patch.object(host, "load_security_secret", return_value=(b"\x00" * 16, "test")),
      mock.patch.object(host, "execute_ram_payload", return_value={"direct_bootloader": True}) as execute,
      mock.patch.object(host, "wait_for_f181", return_value={"ok": True}) as wait_for_application,
      mock.patch.object(host, "set_alloutput_mode")):
    direct = host.install(
        OUT / meta["authenticated_payload"]["path"], meta_path,
        direct_boot=True, panda=fake_probe_panda,
    )
check("post-activation install success is proved by the signer response, not a second F181 check",
      direct["entry_condition"] == "exact_bootloader_f181" and
      direct["verdict"] == "request_signer_live_probe_pass" and
      fake_probe_panda.request_count == 1 and
      execute.call_args.kwargs["allow_direct_boot"] is True and
      execute.call_args.kwargs["programming_already_requested"] is True and
      wait_for_application.call_count == 1 and
      wait_for_application.call_args.kwargs["expected_f181_hex"] == meta["target"]["application_f181_hex"])

fake_self_test_panda = _FakeProbePanda()
with (mock.patch.dict("sys.modules", {"panda": SimpleNamespace(Panda=lambda *_a, **_k: fake_self_test_panda)}),
      mock.patch.object(host, "set_alloutput_mode")):
    signer_self_test = host.self_test(meta_path, panda=fake_self_test_panda)
check("fresh signer self-test needs no post-activation diagnostic transport",
      signer_self_test["passed"] is True and signer_self_test["response"]["status"] == 0 and
      fake_self_test_panda.request_count == 1)

BUILD_TEMP.cleanup()
print("PASS TSS3 request signer behavior")
