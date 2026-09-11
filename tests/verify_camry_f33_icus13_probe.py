#!/usr/bin/env python3
"""Verify the exact-F33 immediate sign-then-ICU-S-command-13 experiment."""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from exploit.ephemeral_runtime import build_camry_f33_icus13_probe as build
from exploit.ephemeral_runtime import camry_f33_icus13_probe as host

passed = failed = 0


def check(name: str, condition: object) -> None:
    global passed, failed
    ok = bool(condition)
    passed += int(ok)
    failed += int(not ok)
    print(f"[{'PASS' if ok else 'FAIL'}] {name}")


meta_path = ROOT / "exploit/ephemeral_runtime/audited/camry_f33_icus13_probe.json"
helper_path = ROOT / "exploit/ephemeral_runtime/audited/camry_f33_icus13_probe_helper_padded.bin"
meta = json.loads(meta_path.read_text())
helper = helper_path.read_bytes()
source = build.SOURCE.read_text()
resident = build.INLINE_SOURCE.read_text()

image = build.IMAGE.read_bytes()
check("exact Camry F33 firmware and recovered gate-code pins",
      hashlib.sha256(image).hexdigest() == build.IMAGE_SHA256 and all(
          image[address:address + len(expected)] == expected
          for address, expected in build.FIRMWARE_PINS.items()
      ))

check("audited helper is the exact 150-word resident-loader payload",
      len(helper) == 600 and hashlib.sha256(helper).hexdigest() == meta["helper"]["sha256"] and
      meta["helper"]["size"] == 600 and meta["helper"]["relocations"] == 0)
check("helper source matches the audited generated artifact",
      hashlib.sha256(build.SOURCE.read_bytes()).hexdigest() == meta["source"]["sha256"])
check("experiment submits command 13 only after clean command-5 slot-4 gating",
      source.index("jarl32 command5_sync, lp") < source.index("mov 0x0004000d, r7") and
      "movea 4, r0, r6" in source and "movea 13, r0, r8" in source and
      "movea 4, r0, r8\n    st.w r8, 0x5b34[gp]" in source)
check("command-13 driver setup preserves callback and pointer complements",
      all(token in source for token in (
          "mov 0x0008a5ae, r6", "mov 0x0008a600, r7", "st.w r9, 0x5b50[gp]",
          "st.w r9, 0x5b54[gp]", "st.w r8, 0x5b64[gp]", "st.w r8, 0x5b68[gp]",
      )))
check("probe has bounded timeout, stock recovery, and explicit disarm",
      "abort on the 64th incomplete poll" in source and "jarl32 icus_abort_recover, lp" in source and
      "st.b r0, 0x4a62[gp]" in source)

transition = "jarl32 startup_20, lp\n    mov 0, r6\n    jarl32 app_startup_final_init, lp"
check("reused resident retains exact r6 application transition",
      transition in resident and resident.index(transition) < resident.index("    ei") and
      meta["reused_live_qualified_payload"]["resident"]["sha256"] ==
      "31b1b2c31007f130d6b4679a0c99f5903a58f748daf11978f9c52f504aea3a3a")
check("private output is exposed through five bounded pages and page-FF disarm",
      host.RESULT_SIZE == 0x80 and host.PAGE_COUNT == 5 and host.PAGE_SIZE == 24 and
      host.control_frame(sequence=7, page=4) == bytes.fromhex("00c8070400000000") and
      host.control_frame(sequence=8, page=0xff) == bytes.fromhex("00c808ff00000000"))

key = bytes.fromhex("00112233445566778899aabbccddeeff")
raw = bytearray(host.RESULT_SIZE)
raw[:16] = key
raw[0x40:0x50] = host._cmac(key, host.FIXED_DOMAIN)
raw[0x50:0x54] = host.RESULT_MAGIC
raw[0x60:0x64] = (1).to_bytes(4, "little")
decoded = host.decode_result(bytes(raw), terminal=1, poll_count=3)
check("host reports a key only when it reproduces the immediate command-5 CMAC",
      decoded["verdict"] == "secoc_key_validated_by_immediate_command5_cmac" and
      decoded["validated_secoc_key_candidates"] == [{
          "offset": 0, "transform": "raw", "key_hex": key.hex(),
      }])
raw[0x40] ^= 1
check("host rejects unverified command-13 bytes as a SecOC key",
      host.decode_result(bytes(raw), terminal=1, poll_count=3)["validated_secoc_key_candidates"] == [])

launcher = (ROOT / "exploit/ephemeral_runtime/camry_f33_icus13_probe_launcher.sh").read_text()
kit = (ROOT / "tools/targets/camry/builders/build_camry_f33_car_kit.py").read_text()
check("Car Kit packages a bounded Camry-only ICU-S-13 launcher",
      'icus13_launcher = out / "f33-icus13"' in kit and
      '"camry_f33_icus13_probe_payload.bin"' in kit and
      "run_bounded 20 run --execute --parked-stationary-confirmed" in launcher and
      "camry_f33_icus13_probe.py" in launcher)

print(f"Results: {passed} passed, {failed} failed")
raise SystemExit(1 if failed else 0)
