#!/usr/bin/env python3
"""Verify the exact-F33 volatile ICU-S RAM_KEY opcode characterization probe."""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from exploit.ephemeral_runtime import build_camry_f33_icus_ramkey_probe as build
from exploit.ephemeral_runtime import camry_f33_icus_ramkey_probe as host

passed = failed = 0


def check(name: str, condition: object) -> None:
    global passed, failed
    ok = bool(condition)
    passed += int(ok)
    failed += int(not ok)
    print(f"[{'PASS' if ok else 'FAIL'}] {name}")


image = build.IMAGE.read_bytes()
check("exact Camry F33 firmware is pinned",
      hashlib.sha256(image).hexdigest() == build.IMAGE_SHA256)
check("command-8 engine fixes four input and three output blocks",
      image[0x8AAB2:0x8AABC] == bytes.fromhex("040a640f2d5b030a640f") and
      image[0x8AB1A:0x8AB22] == bytes.fromhex("080a80070f08a08b"))
check("literal command 11 has no stock input/output callback setup",
      image[0x8AB26:0x8AB82].count((0x0008A538).to_bytes(4, "little")) == 0 and
      image[0x8AB26:0x8AB82].count((0x0008A5AE).to_bytes(4, "little")) == 0 and
      image[0x8AB74:0x8AB7E] == bytes.fromhex("440f6c5b0b0a80070f08"))
check("literal command 0x22 configures one input and two output blocks",
      image[0x8AC00:0x8AC02] == bytes.fromhex("0252") and
      image[0x8AC26:0x8AC2C] == bytes.fromhex("010a640f2d5b") and
      image[0x8AC4E:0x8AC52] == bytes.fromhex("6457355b"))

meta_path = ROOT / "exploit/ephemeral_runtime/audited/camry_f33_icus_ramkey_probe.json"
helper9_path = ROOT / "exploit/ephemeral_runtime/audited/camry_f33_icus_ramkey_cmd9_helper_padded.bin"
helper10_path = ROOT / "exploit/ephemeral_runtime/audited/camry_f33_icus_ramkey_cmd10_helper_padded.bin"
meta = json.loads(meta_path.read_text())
helper9 = helper9_path.read_bytes()
helper10 = helper10_path.read_bytes()
source9 = build.CMD9_SOURCE.read_text()
source10 = build.CMD10_SOURCE.read_text()

check("audited metadata is exact-target and reuses the live-qualified resident",
      meta["schema"] == host.BUILD_SCHEMA and meta["target"] == {
          "software_id": "8965F3307000", "codeflash_sha256": build.IMAGE_SHA256,
      } and meta["reused_live_qualified_payload"]["resident"] == host.EXPECTED_RESIDENT)
check("both helpers are exact 150-word audited loader images",
      len(helper9) == len(helper10) == 600 and
      hashlib.sha256(helper9).hexdigest() == meta["helpers"]["command9"]["sha256"] and
      hashlib.sha256(helper10).hexdigest() == meta["helpers"]["command10"]["sha256"] and
      meta["helpers"]["command9"]["word_count"] == meta["helpers"]["command10"]["word_count"] == 150)
check("helper source hashes are pinned by audited metadata",
      hashlib.sha256(build.CMD9_SOURCE.read_bytes()).hexdigest() == meta["helpers"]["command9"]["source_sha256"] and
      hashlib.sha256(build.CMD10_SOURCE.read_bytes()).hexdigest() == meta["helpers"]["command10"]["source_sha256"])
check("command-9 helper is one-input/no-output and proves RAM_KEY through selector E command 5",
      "movea 9, r0, r9\n    st.w r9, 0[r10]" in source9 and
      "movea 1, r0, r9\n    st.w r9, 0x5b2c[gp]" in source9 and
      "st.w r0, 0x5b34[gp]" in source9 and
      "movea 14, r0, r6" in source9 and "jarl32 command5_sync, lp" in source9 and
      "mov 0x4f394b52, r7" in source9)
check("command-10 helper is zero-input/seven-output and requires command-9 continuity marker",
      source10.index("mov 0x4f394b52, r7") < source10.index("movea 10, r0, r9\n    st.w r9, 0[r10]") and
      "st.w r0, 0x5b2c[gp]" in source10 and
      "movea 7, r0, r9\n    st.w r9, 0x5b34[gp]" in source10)
check("both direct commands require the stock ICU-S driver idle state and bounded abort recovery",
      all("movea 0xe1, r0, r7" in s and "jarl32 icus_abort_recover, lp" in s for s in (source9, source10)))
check("command-10 last telemetry page cannot expose bytes past the 112-byte export",
      "Page 4 contains only the final 16 export bytes" in source10 and
      "st.w r0, 0x4a80[gp]" in source10 and "st.w r0, 0x4a84[gp]" in source10)
check("probe never issues persistent command 8",
      "movea 8, r0, r9\n    st.w r9, 0[r10]" not in source9 and
      "movea 8, r0, r9\n    st.w r9, 0[r10]" not in source10 and
      meta["mutation_boundary"]["command8"] is False and
      meta["mutation_boundary"]["persistent_key_update"] is False and
      meta["mutation_boundary"]["flash_write"] is False)

kat = host.known_answers()
check("independent known-answer derivation matches audited metadata",
      kat == meta["known_answer"] and
      kat["command5_cmac_hex"] == "f61a27173ca7706ce44e7b5d6d7c69d3" and
      kat["k3_hex"] == "118a46447a770d87828a69c222e2d17e" and
      kat["k4_hex"] == "2ebb2a3da62dbd64b18ba6493e9fbe22" and
      kat["m4_star_hex"] == "f89b6935656806387f127eb839739e9e")
raw9 = bytearray(32)
raw9[:4] = host.CMD9_MAGIC
raw9[4] = 1
raw9[16:32] = bytes.fromhex(kat["command5_cmac_hex"])
check("host requires all 128 CMAC bits before treating command 9 as LOAD_PLAIN_KEY",
      host.decode_command9(bytes(raw9))["verdict"] == "command9_load_plain_ram_key_proven")
raw9[16] ^= 1
check("one-bit command-9 KAT mismatch blocks the mapping",
      host.decode_command9(bytes(raw9))["verdict"] == "command9_not_proven")

m1 = bytes.fromhex("00112233445566778899aabbccddee") + b"\xe0"
m4 = m1 + bytes.fromhex(kat["m4_star_hex"])
k4 = bytes.fromhex(kat["k4_hex"])
export = m1 + bytes(32) + bytes(16) + m4 + host.cmac(k4, m4)
validated = host.validate_export(export)
check("host proves candidate command 10 only with independent SHE RAM_KEY export invariants",
      validated["verdict"] == "command10_export_ram_key_proven" and all(validated["checks"].values()))
corrupt = bytearray(export)
corrupt[80] ^= 1
check("one-bit M4 known-answer mismatch rejects candidate command 10",
      host.validate_export(bytes(corrupt))["verdict"] == "command10_not_proven")
check("private control protocol uses nonzero sequence and explicit page-FF disarm",
      host.control_frame(sequence=7, page=4) == bytes.fromhex("00c8070400000000") and
      host.control_frame(sequence=8, page=0xff) == bytes.fromhex("00c808ff00000000"))

launcher = (ROOT / "exploit/ephemeral_runtime/camry_f33_icus_ramkey_probe_launcher.sh").read_text()
kit = (ROOT / "tools/targets/camry/builders/build_camry_f33_car_kit.py").read_text()
check("Car Kit exposes the bounded RAM_KEY characterization instead of the stale command-13 key-export probe",
      'icus_ramkey_launcher = out / "f33-icus-ramkey"' in kit and
      '"camry_f33_icus_ramkey_probe_payload.bin"' in kit and
      '"icus_ramkey_opcode_probe"' in kit and
      "f33-icus13" not in kit and "icus13_key_export_probe" not in kit and
      "run_bounded 20 run --execute --parked-stationary-confirmed" in launcher and
      "Command 8 is never issued" in launcher)

print(f"Results: {passed} passed, {failed} failed")
raise SystemExit(1 if failed else 0)
