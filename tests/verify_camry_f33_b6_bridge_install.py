#!/usr/bin/env python3
"""Verify exact-F33 RAM-only B6 observer/bridge installer guards."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from exploit.common.payload_package import inspect_payload, package_shellcode

MOD = ROOT / "exploit/ephemeral_runtime/camry_f33_b6_bridge_install.py"
AUDITED_BIN = ROOT / "exploit/ephemeral_runtime/audited/camry_f33_b6_bridge.bin"
AUDIT = ROOT / "exploit/ephemeral_runtime/audited_camry_f33_b6_bridge_build.json"
SOURCE = ROOT / "exploit/ephemeral_runtime/camry_f33_b6_bridge.c"
BUILDER = ROOT / "exploit/ephemeral_runtime/build_camry_f33_b6_bridge.py"
IMAGE = ROOT / "firmware/camry-8965F3307000/CodeFlash.bin"
SPEC = importlib.util.spec_from_file_location("camry_f33_b6_bridge_install", MOD)
assert SPEC and SPEC.loader
m = importlib.util.module_from_spec(SPEC); sys.modules[SPEC.name] = m; SPEC.loader.exec_module(m)
audit = json.loads(AUDIT.read_text())
blob = AUDITED_BIN.read_bytes()
image = IMAGE.read_bytes()
payload = package_shellcode(blob, secret=image[0xBFD8:0xBFE8])
inspection = inspect_payload(payload, secret=image[0xBFD8:0xBFE8])

passed = failed = 0
def check(name, cond):
  global passed, failed
  ok=bool(cond); passed += int(ok); failed += int(not ok); print(f"[{'PASS' if ok else 'FAIL'}] {name}")

check("exact target identities", m.EXPECTED_F181_HEX == "023839363546333330373030300000000038413331313333303331303000000000" and m.EXPECTED_BOOT_F181_HEX == "02" + "21"*32)
check("exact post-repin route", m.ROUTE.bus == 0 and m.ROUTE.elm327_param == 1 and m.ROUTE.uds_variant == "old" and m.ROUTE.cpu_index == 0)
check("field-proven F33 RAM geometry", m.GEOMETRY.load_addr == 0xFEBF0000 and m.GEOMETRY.load_size == 0x1000 and m.GEOMETRY.evidence == "dynamic:camry-8965F3307000-20260826")
check("telemetry cells exact", m.TELEMETRY == {"heartbeat":0xFEBFFBEC,"queue_present":0xFEBFFBF0,"zero_mac_seen":0xFEBFFBF4,"injected":0xFEBFFBF8})
check("audited bridge identity exact", len(blob) == audit["shellcode"]["size"] == 608 and
      hashlib.sha256(blob).hexdigest() == audit["shellcode"]["sha256"] == m.BRIDGE_SHELLCODE_SHA256)
check("audited bridge source/builder and retained-tail contract exact",
      audit["schema"] == "camry-f33-b6-bridge-build-v2" and
      audit["source"]["sha256"] == hashlib.sha256(SOURCE.read_bytes()).hexdigest() and
      audit["builder"]["sha256"] == hashlib.sha256(BUILDER.read_bytes()).hexdigest() and
      audit["compile_contract"]["resident_size_incl_marker_slack"] == 508 and
      audit["compile_contract"]["resident_limit"] == 508 and
      audit["compile_contract"]["relocations"] == 0)
check("bridge deduplicates against the exact raw COM window before reinjection",
      "TARGET_B6_COM_WINDOW + i" in SOURCE.read_text() and
      "if (delivered == 0u)" in SOURCE.read_text() and
      audit["static_pins"]["B6_COM_WINDOW"] == "0xFEBE4BFF")
check("payload identity exact and authenticated", len(payload) == 0x1000 and
      hashlib.sha256(payload).hexdigest() == m.EXPECTED_PAYLOAD_SHA256 and
      inspection.cmac_valid and inspection.crc_residue == 0xFFFFFFFF)
p=m.plan(Path("/nonexistent/camry_f33_b6_bridge_payload.bin"))
check("plan declares RAM-only behavior and built-in P1M-E root",
      p["ram"]["persistent_flash_writes"] is False and p["payload"]["expected_sha256"] == m.EXPECTED_PAYLOAD_SHA256 and
      "built-in Toyota P1M-E boot SecurityAccess root" in p["live_requirements"])
src=MOD.read_text()
check("live install requires explicit NRTD confirmation", 'live RAM install requires --nrtd-confirmed' in src)
check("installer uses authenticated RAM executor only", 'execute_ram_payload(' in src and all(x not in src for x in ('flash_program', 'erase_codeflash', 'RequestDownload(')))
check("attestation requires application F181 and heartbeat advancement", 'application F181 mismatch after RAM execute' in src and 'bridge heartbeat did not advance' in src)
check("installer requires no temporary boot-secret file", "--boot-secret-file" not in src)
check("secret value is never recorded", '"secret_value_recorded": False' in src)
print(f"\nResults: {passed} passed, {failed} failed")
raise SystemExit(1 if failed else 0)
