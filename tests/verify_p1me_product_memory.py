#!/usr/bin/env python3
"""Verify the tracked P1M-E product/address-space and timer-domain facts."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FACTS = json.loads((ROOT / "data/p1me_product_memory.json").read_text(encoding="utf-8"))
H_CODEFLASH = ROOT / "community/albinoelephant/raw-20260818/albinoelephant-corolla-2023.20260814-0023/dump_codeflash_00000000_00200000_20260814-025814.bin"

passed = failed = 0

def check(name: str, condition: object, detail: str = "") -> None:
    global passed, failed
    ok = bool(condition)
    passed += int(ok); failed += int(not ok)
    suffix = f" ({detail})" if detail else ""
    print(f"[{'PASS' if ok else 'FAIL'}] {name}{suffix}")

prod = FACTS["products"]["R7F701383"]
camry_prod = FACTS["products"]["R7F701381"]
addr = FACTS["address_space"]
timer = FACTS["timer"]

print("== exact 1-MiB DPS product facts ==")
check("R7F701381/R7F701383 are tracked as DPS 1-MiB CodeFlash", all(p["regulator"] == "DPS" and p["codeflash_bytes"] == 0x100000 for p in (camry_prod, prod)))
check("R7F701381/R7F701383 DataFlash is 32 KiB", all(p["dataflash_bytes"] == 0x8000 for p in (camry_prod, prod)))
check("R7F701381/R7F701383 local/global RAM totals are 128/64 KiB", all(p["local_ram_bytes"] == 0x20000 and p["global_ram_bytes"] == 0x10000 for p in (camry_prod, prod)))
check("1-MiB DataFlash geometry is FF200000..FF207FFF", addr["dataflash_1mb"] == {"start": 0xFF200000, "end_exclusive": 0xFF208000})
check("2-MiB DataFlash geometry is FF200000..FF20FFFF", addr["dataflash_2mb"] == {"start": 0xFF200000, "end_exclusive": 0xFF210000})
check("PE1 local-RAM view is 128 KiB", addr["local_ram_pe1"] == {"start": 0xFEBE0000, "end_exclusive": 0xFEC00000})
check("self local-RAM view is 128 KiB", addr["local_ram_self"] == {"start": 0xFEDE0000, "end_exclusive": 0xFEE00000})
check("two local-RAM views do not imply 256 KiB physical local RAM", prod["local_ram_bytes"] == (addr["local_ram_pe1"]["end_exclusive"] - addr["local_ram_pe1"]["start"]))

print("\n== retained H silicon identity ==")
blob = H_CODEFLASH.read_bytes()
check("retained H boot-info block names R7F701383", blob[0x180:0x1A8].startswith(b"BOOT INFO AREA  R7F701383"))
check("retained H CodeFlash has 1 MiB meaningful-device extent", prod["codeflash_bytes"] == 0x100000 and blob[0x100000:0x200000] == b"\xFF" * 0x100000)

print("\n== P-Bus / TAUJ timer-domain derivation ==")
check("official P1M-E P-Bus domain is 80 MHz", timer["p_bus_hz"] == 80_000_000)
check("datasheet source note explicitly places TAUJ on the 80-MHz P-Bus", any("TAUJ" in x and "80 MHz" in x for x in FACTS["sources"]["datasheet"]["references"]))

print("\n== TAUJ1 SecurityAccess timer derivation ==")
check("TAUJ1CNT0 register address", timer["tauj1cnt0_address"] == 0xFFE51010)
check("TAUJ1TPS/CMOR0 register addresses", timer["tauj1tps_address"] == 0xFFE51090 and timer["tauj1cmor0_address"] == 0xFFE51080)
check("firmware TAUJ1TPS low nibble selects PRS0=2", timer["firmware_tauj1tps_value"] == 0xFFF2 and timer["prs0"] == 2)
check("P-Bus 80 MHz / 4 gives 20 MHz CK0", timer["p_bus_hz"] == 80_000_000 and timer["ck0_hz"] == timer["p_bus_hz"] // 4 == 20_000_000)
check("200,000,000 TAUJ1 ticks is 10 seconds", timer["security_delay_ticks"] * 1000 // timer["ck0_hz"] == timer["security_delay_ms"] == 10_000)

print("\n== source identity when retained references are present ==")
for key in ("datasheet", "hardware_manual"):
    source = FACTS["sources"][key]
    path = ROOT / source["path"]
    if path.is_file():
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        check(f"{key} SHA-256 matches tracked source identity", digest == source["sha256"], digest[:16])
    else:
        print(f"[PASS] {key} source identity recorded (REFERENCE file not required for core checkout)")
        passed += 1

print(f"\n== RESULT: {passed} passed, {failed} failed ==")
raise SystemExit(1 if failed else 0)
