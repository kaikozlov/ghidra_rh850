#!/usr/bin/env python3
"""Verify the exact-F33 ABI-preserving RAM-only B6 bridge and installer guards."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from exploit.common.payload_package import inspect_payload, package_shellcode
from exploit.ephemeral_runtime import build_camry_f33_b6_bridge as builder

MOD = ROOT / "exploit/ephemeral_runtime/camry_f33_b6_bridge_install.py"
AUDITED_BIN = ROOT / "exploit/ephemeral_runtime/audited/camry_f33_b6_bridge.bin"
AUDIT = ROOT / "exploit/ephemeral_runtime/audited_camry_f33_b6_bridge_build.json"
SOURCE = ROOT / "exploit/ephemeral_runtime/camry_f33_b6_bridge.S"
BUILDER = ROOT / "exploit/ephemeral_runtime/build_camry_f33_b6_bridge.py"
IMAGE = ROOT / "firmware/camry-8965F3307000/CodeFlash.bin"
SPEC = importlib.util.spec_from_file_location("camry_f33_b6_bridge_install", MOD)
assert SPEC and SPEC.loader
m = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = m
SPEC.loader.exec_module(m)

audit = json.loads(AUDIT.read_text())
blob = AUDITED_BIN.read_bytes()
image = IMAGE.read_bytes()
payload = package_shellcode(blob, secret=image[0xBFD8:0xBFE8])
inspection = inspect_payload(payload, secret=image[0xBFD8:0xBFE8])
source = SOURCE.read_text()

passed = failed = 0


def check(name: str, condition: object) -> None:
    global passed, failed
    ok = bool(condition)
    passed += int(ok)
    failed += int(not ok)
    print(f"[{'PASS' if ok else 'FAIL'}] {name}")


check("exact target identities",
      m.EXPECTED_F181_HEX == "023839363546333330373030300000000038413331313333303331303000000000" and
      m.EXPECTED_BOOT_F181_HEX == "02" + "21" * 32)
check("exact post-repin route",
      m.ROUTE.bus == 0 and m.ROUTE.elm327_param == 1 and m.ROUTE.uds_variant == "old" and m.ROUTE.cpu_index == 0)
check("field-proven F33 RAM geometry",
      m.GEOMETRY.load_addr == 0xFEBF0000 and m.GEOMETRY.load_size == 0x1000 and
      m.GEOMETRY.evidence == "dynamic:camry-8965F3307000-20260826")
check("v3 low-RAM mailbox and stock tick witness exact",
      (m.MAILBOX_BASE, m.MAILBOX_SIZE, m.MAILBOX_MAGIC, m.MAILBOX_VERSION) ==
      (0xFEBF0000, 0x30, 0x42364252, 3) and m.FOREGROUND_TICK == 0xFEBE39DB)

check("audited bridge source/builder are hash-bound",
      audit["schema"] == "camry-f33-b6-bridge-build-v3" and
      audit["source"]["path"] == "exploit/ephemeral_runtime/camry_f33_b6_bridge.S" and
      audit["source"]["sha256"] == hashlib.sha256(SOURCE.read_bytes()).hexdigest() and
      audit["builder"]["sha256"] == hashlib.sha256(BUILDER.read_bytes()).hexdigest())
check("audited staging identity exact",
      len(blob) == audit["staging"]["size"] == 648 and
      hashlib.sha256(blob).hexdigest() == audit["staging"]["sha256"] == m.BRIDGE_SHELLCODE_SHA256 and
      audit["staging"]["relocations"] == 0 and audit["staging"]["resident_offset"] == 128)
check("resident fits exact retained 524-byte tail",
      audit["resident"]["base"] == "0xFEBFF9F0" and audit["resident"]["size"] == 520 and
      audit["resident"]["headroom"] == 4 and audit["resident"]["relocations"] == 0 and
      audit["resident"]["end_limit"] == "0xFEBFFBFC")
expected_targets = [
    *builder.EXPECTED_RESIDENT_JARL_TARGETS[:29],
    builder.B6_COM_RX_CALLBACK,
    *builder.EXPECTED_RESIDENT_JARL_TARGETS[29:],
]
check("bridge call path is direct-JARL and ABI preserving",
      audit["resident"]["jarl_targets"] == [f"0x{x:08X}" for x in expected_targets] and
      audit["resident"]["jarl_targets"][28:31] == ["0x000667E6", "0x0007D72C", "0x00071378"] and
      "call0(" not in source and "jmp [r" not in source and "jarl [r" not in source)
check("valid RUN/STOP cancels stale pending before applying running state",
      source.index("valid RUN/STOP cancels any stale pending snapshot") <
      source.index("st.b r6, 0x4805[gp]") < source.index("st.b r7, 0x4806[gp]"))
check("bridge snapshots queued secured B6, deduplicates conservatively, then publishes after stock aggregate",
      source.index("movea -0x632c, gp, r6") < source.index("jarl32 fg_aggregate, lp") <
      source.index("ld.bu 0x4813[gp], r6") < source.index("jarl32 b6_com_rx, lp") and
      "ld.bu -0x6bfe[gp], r7" in source and "be .L_clear_pending" in source and
      audit["mutation_boundary"]["b6_source"].startswith("byte-exact snapshot of FEBE54D4") and
      audit["mutation_boundary"]["delivery"].startswith("native PduR group-0 callback 0x7D72C") and
      "conservative false negative" in audit["mutation_boundary"]["deduplication"])
check("static bridge pins re-derive against exact CodeFlash",
      builder.verify_static_pins(image) == {k: int(v, 16) for k, v in audit["static_pins"].items()})
check("bridge has no CAN transmit, code patch, or dynamic call primitive",
      audit["mutation_boundary"]["dynamic_call"] is False and
      audit["mutation_boundary"]["can_transmit_call"] is False and
      audit["mutation_boundary"]["stock_code_patch"] is False and
      audit["mutation_boundary"]["codeflash_write"] is False)

check("payload identity exact and authenticated",
      len(payload) == 0x1000 and hashlib.sha256(payload).hexdigest() == m.EXPECTED_PAYLOAD_SHA256 and
      audit["authenticated_payload"]["sha256"] == m.EXPECTED_PAYLOAD_SHA256 and
      inspection.cmac_valid and inspection.crc_residue == 0xFFFFFFFF and
      inspection.callback_address == 0xFEBF0000)
p = m.plan(Path("/nonexistent/camry_f33_b6_bridge_payload.bin"))
check("plan declares RAM-only behavior and explicit parked arm gate",
      p["ram"]["persistent_flash_writes"] is False and
      p["payload"]["expected_sha256"] == m.EXPECTED_PAYLOAD_SHA256 and
      "built-in Toyota P1M-E boot SecurityAccess root" in p["live_requirements"] and
      p["arm_requirements"] == ["--arm-bridge", "--parked-stationary-confirmed"])
src = MOD.read_text()
check("live install requires explicit NRTD confirmation",
      "live RAM install requires --nrtd-confirmed" in src)
check("installer uses authenticated RAM executor only",
      "execute_ram_payload(" in src and all(x not in src for x in ("flash_program", "erase_codeflash", "RequestDownload(")))
check("attestation requires F181, mailbox identity, and stock tick movement",
      "application F181 mismatch after RAM execute" in src and
      "bridge mailbox identity mismatch" in src and
      "stock foreground tick did not advance" in src)
check("arming requires explicit parked/stationary confirmation",
      "arming the B6 bridge requires --parked-stationary-confirmed" in src and
      "if args.arm_bridge and not args.parked_stationary_confirmed" in src)
check("installer requires no temporary boot-secret file", "--boot-secret-file" not in src)
check("secret value is never recorded", '"secret_value_recorded": False' in src)

print(f"\nResults: {passed} passed, {failed} failed")
raise SystemExit(1 if failed else 0)
