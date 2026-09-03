#!/usr/bin/env python3
"""Verify exact-F33 RAM-only B6 observer/bridge installer guards."""
from __future__ import annotations

import hashlib
import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MOD = ROOT / "exploit/ephemeral_runtime/camry_f33_b6_bridge_install.py"
PAYLOAD = ROOT / "build/out/ephemeral-runtime/camry-f33-observer/camry_f33_b6_bridge_payload.bin"
SPEC = importlib.util.spec_from_file_location("camry_f33_b6_bridge_install", MOD)
assert SPEC and SPEC.loader
m = importlib.util.module_from_spec(SPEC); sys.modules[SPEC.name] = m; SPEC.loader.exec_module(m)

passed = failed = 0
def check(name, cond):
  global passed, failed
  ok=bool(cond); passed += int(ok); failed += int(not ok); print(f"[{'PASS' if ok else 'FAIL'}] {name}")

check("exact target identities", m.EXPECTED_F181_HEX == "023839363546333330373030300000000038413331313333303331303000000000" and m.EXPECTED_BOOT_F181_HEX == "02" + "21"*32)
check("exact post-repin route", m.ROUTE.bus == 0 and m.ROUTE.elm327_param == 1 and m.ROUTE.uds_variant == "old" and m.ROUTE.cpu_index == 0)
check("field-proven F33 RAM geometry", m.GEOMETRY.load_addr == 0xFEBF0000 and m.GEOMETRY.load_size == 0x1000 and m.GEOMETRY.evidence == "dynamic:camry-8965F3307000-20260826")
check("telemetry cells exact", m.TELEMETRY == {"heartbeat":0xFEBFFBEC,"queue_present":0xFEBFFBF0,"zero_mac_seen":0xFEBFFBF4,"injected":0xFEBFFBF8})
check("payload identity exact", PAYLOAD.is_file() and PAYLOAD.stat().st_size == 0x1000 and hashlib.sha256(PAYLOAD.read_bytes()).hexdigest() == m.EXPECTED_PAYLOAD_SHA256)
p=m.plan(PAYLOAD)
check("plan declares RAM-only behavior and built-in P1M-E root",
      p["ram"]["persistent_flash_writes"] is False and p["payload"]["sha256"] == m.EXPECTED_PAYLOAD_SHA256 and
      "built-in Toyota P1M-E boot SecurityAccess root" in p["live_requirements"])
src=MOD.read_text()
check("live install requires explicit NRTD confirmation", 'live RAM install requires --nrtd-confirmed' in src)
check("installer uses authenticated RAM executor only", 'execute_ram_payload(' in src and all(x not in src for x in ('flash_program', 'erase_codeflash', 'RequestDownload(')))
check("attestation requires application F181 and heartbeat advancement", 'application F181 mismatch after RAM execute' in src and 'bridge heartbeat did not advance' in src)
check("installer requires no temporary boot-secret file", "--boot-secret-file" not in src)
check("secret value is never recorded", '"secret_value_recorded": False' in src)
print(f"\nResults: {passed} passed, {failed} failed")
raise SystemExit(1 if failed else 0)
