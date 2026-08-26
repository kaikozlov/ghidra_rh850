#!/usr/bin/env python3
"""Verify the exact H/F cooperative-authority five-PDU wire boundary."""
from __future__ import annotations

import hashlib
import json
import struct
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / "data/generated/corolla_hf_cooperative_authority_wire_visibility.json"
EVID = ROOT / "data/generated/corolla_8965H1202000_cooperative_authority_wire_decompiler_evidence.json"
BUILDER = ROOT / "tools/build_corolla_hf_cooperative_authority_wire_visibility.py"
H = ROOT / "community/albinoelephant/normalized/8965H1202000_CodeFlash.bin"
H_RAW = ROOT / "community/albinoelephant/raw-20260818/albinoelephant-corolla-2023.20260814-0023/dump_codeflash_00000000_00200000_20260814-025814.bin"
F_RAW = ROOT / "community/spanconstant/raw-20260821/span-corolla-2025.20260821-1511/dump_codeflash_00000000_00200000_20260821-152033.bin"

passed = failed = 0


def check(name: str, condition: bool) -> None:
    global passed, failed
    if condition:
        passed += 1
        print(f"PASS: {name}")
    else:
        failed += 1
        print(f"FAIL: {name}")


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


artifact = json.loads(ART.read_text())
evidence = json.loads(EVID.read_text())
h = H.read_bytes()

check("schema exact", artifact["schema"] == "corolla-hf-cooperative-authority-wire-visibility-v1")
check("exact variants only", artifact["software_ids"] == ["8965H1202000", "8965F1208000"])
check("exact H image identity", len(h) == 0x100000 and sha(h) == "0b47bdc1217835c839e3543e52eab40eb793650a9c159e46f6a9b365ea41a67f")
check("promoted evidence count", evidence["function_count"] == 16 and artifact["sources"]["decompiler_evidence"]["function_count"] == 16)

# Every promoted decompilation remains tied to exact H function bytes and text.
body_ok = True
for row in evidence["functions"]:
    entry = int(row["entry"], 16)
    body_ok &= sha(h[entry:entry + row["body_size"]]) == row["body_sha256"]
    body_ok &= sha(row["decompiled_c"].encode()) == row["decompiled_c_sha256"]
check("all 16 promoted functions raw/text bound", body_ok)

gate = artifact["exact_cooperative_gate"]
check("raw stage and normalizer exact", gate["raw_mode_source"] == "0xFEBE7C58" and gate["raw_mode_stage"] == "0xFEBEF000" and gate["stage_copy"] == "0x0005262C" and gate["normalizer"] == "0x000B8EEC")
check("normalization distinguishes raw modes 0 and 1", gate["normalization"]["0"] == 0 and gate["normalization"]["1"] == 1)
check("exact acceptance condition", gate["acceptance_decoder"] == "0x000CBE6E" and gate["acceptance_condition"] == "FEBEACBD == 0 AND FEBEC26D == 1")

coarse = artifact["positive_coarse_mode_wire_path"]
check("coarse path endpoints", coarse["path"][0] == "FEBE7C58" and coarse["path"][-1] == "CAN 0x030")
check("fixed-GP/computed chain exact", all(x in coarse["path"] for x in ["FEBEF000", "0x000B23A2", "FEBEB118", "0x000BBA48", "FEBEE887", "0x000470C6", "0x0004766A"]))
check("coarse predicate exact", coarse["raw_mode_predicate"] == "FEBEF000 < 2" and "larger aggregate" in coarse["predicate_role"])
check("three exact 0x030 wire bits", coarse["wire_bits"] == [
    {"signal_id": 5, "source": "0xFEBE7E09", "wire": "B6[3]"},
    {"signal_id": 12, "source": "0xFEBE7E0B", "wire": "B10[3]"},
    {"signal_id": 15, "source": "0xFEBE7E0D", "wire": "B13[4]"},
])

negative = artifact["exact_authority_negative"]
check("mode-0/mode-1 counterexample retained", "FEBEACBD=0" in negative["distinguishing_pair"]["raw_mode_0"] and "FEBEACBD=1" in negative["distinguishing_pair"]["raw_mode_1"])
check("exact authority negative", negative["exact_wire_visible_cooperative_authority_bit_recovered"] is False and "opposite exact-gate outcomes" in negative["proof"])

pdus = artifact["five_pdu_boundary"]
check("five normal Tx PDUs exact", [row["can_id"] for row in pdus] == ["0x030", "0x351", "0x394", "0x4A3", "0x4C8"])
check("five packers exact", [row["packer"] for row in pdus] == ["0x0004766A", "0x00047BA2", "0x00047ADA", "0x0004749A", "0x000475D0"])
check("five direct exact-root sets empty", all(row["direct_cooperative_root_references"] == [] for row in pdus))
check("five exact authority results negative", all(row["exact_wire_visible_cooperative_authority_bit_recovered"] is False for row in pdus))
check("0x030 alone carries recovered coarse path", "three duplicated coarse" in pdus[0]["classification"] and all("coarse" not in row["classification"] for row in pdus[1:]))

# Independently check every raw absolute pointer occurrence and the two table
# families. This catches a new fixed CodeFlash indirect surface.
occ = artifact["indirect_profile_flag_consumers"]["absolute_pointer_occurrences"]
expected_offsets = {
    0xFEBEC26E: [0xD0E24, 0xD0E60, 0xD1124, 0xD1160],
    0xFEBEC26F: [0xD0E30, 0xD0E6C, 0xD1130, 0xD116C],
    0xFEBEC270: [0xD0E3C, 0xD0E78, 0xD113C, 0xD1178],
    0xFEBEC271: [0xD0E48, 0xD0E84, 0xD1148, 0xD1184],
}
raw_occ_ok = True
for address, expected in expected_offsets.items():
    needle = struct.pack("<I", address)
    actual = [offset for offset in range(len(h)) if h.startswith(needle, offset)]
    raw_occ_ok &= actual == expected
check("profile absolute-pointer occurrence census exact", raw_occ_ok)
check("non-profile exact/chain roots have zero pointer literals", all(occ[name] == [] for name in [
    "raw_mode", "normalized_mode", "health_gate", "common_active", "profile_1_mirror",
    "aggregate_stage", "aggregate_snapshot", "wire_source_signal_5", "wire_source_signal_12", "wire_source_signal_15",
]))

table_ok = True
for base in (0xD0E18, 0xD1118):
    for bank in range(2):
        flags = [struct.unpack_from("<I", h, base + bank * 0x3C + row * 0x0C)[0] for row in range(5)]
        table_ok &= flags == [0, 0xFEBEC26E, 0xFEBEC26F, 0xFEBEC270, 0xFEBEC271]
check("both two-bank computed profile tables exact", table_ok)
check("indirect profile consumers are internal gains", artifact["indirect_profile_flag_consumers"]["classification"].endswith("internal gain selectors, not discrete Tx fields"))

# Independently normalize both tracked 2-MiB range dumps and compare the exact
# application interval used by every cited function and table.
h_raw = H_RAW.read_bytes()
f_raw = F_RAW.read_bytes()
check("raw range dumps normalize to exact identities", len(h_raw) == len(f_raw) == 0x200000 and h_raw[:0x100000] == h and sha(f_raw[:0x100000]) == "fdb35b76891cf84a8b89e0a05c9c7c5cfcd27994cf85ccc01ff32828f53091f6")
check("H/F application bytes independently identical", h_raw[0x20000:0x100000] == f_raw[0x20000:0x100000] and sha(h_raw[0x20000:0x100000]) == "2ccb79cda1e8689ec91c389d3d7e3921c010ddc9c9d917f23c1705916a0e0d7f")

conclusion = artifact["static_conclusion"]
check("positive and negative both explicit", conclusion["coarse_mode_aggregate_bits_recovered"] is True and conclusion["coarse_mode_wire_can_id"] == "0x030" and conclusion["exact_wire_visible_cooperative_authority_bit_recovered"] is False)
check("negative boundary names excluded mechanisms", all(term in artifact["evidence_boundary"] for term in ["mutable runtime pointers", "DMA/peripheral", "physical actuator", "No live authority transition"]))

with tempfile.TemporaryDirectory(prefix="hf-coop-wire-") as td:
    out = Path(td) / "artifact.json"
    proc = subprocess.run([sys.executable, str(BUILDER), "--out", str(out)], cwd=ROOT, capture_output=True, text=True)
    check("builder exits cleanly", proc.returncode == 0)
    check("builder reproduces artifact byte-for-byte", out.exists() and out.read_bytes() == ART.read_bytes())


print("\n== documentation/status integration ==")
state_doc = (ROOT / "docs/variants/corolla-h-f-openpilot-state-bridge.md").read_text()
findings = (ROOT / "docs/status/FINDINGS.md").read_text()
check("canonical report records coarse-not-exact authority boundary", all(x in state_doc for x in ("### 6.6", "FEBEF000 < 2", "B6[3]", "B10[3]", "B13[4]", "cannot be used as an exact cooperative-authority signal")))
check("TMS-056 integrated", "| TMS-056 |" in findings and "cooperative_authority_wire_visibility.json" in findings)

print(f"\n{passed} passed, {failed} failed")
raise SystemExit(1 if failed else 0)
