#!/usr/bin/env python3
"""Verify Corolla 8965H1202000 SecOC key-selector/provisioning provenance."""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
ART = REPO / "data/generated/corolla_8965H1202000_secoc_key_provenance.json"
EVIDENCE = REPO / "data/generated/corolla_8965H1202000_secoc_key_provenance_decompiler_evidence.json"
BUILDER = REPO / "tools/build_corolla_h_secoc_key_provenance.py"
HRAW = REPO / "community/albinoelephant/raw-20260818/albinoelephant-corolla-2023.20260814-0023/dump_codeflash_00000000_00200000_20260814-025814.bin"
SIMG = REPO / "firmware/RH850_P1M-E_CodeFlash.bin"
DF = REPO / "data/generated/corolla_2023_albino_dataflash_analysis.json"

passed = failed = 0

def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def check(name: str, condition: object, detail: str = "") -> None:
    global passed, failed
    ok = bool(condition)
    passed += int(ok)
    failed += int(not ok)
    suffix = f" ({detail})" if detail else ""
    print(f"[{'PASS' if ok else 'FAIL'}][raw_bytes] {name}{suffix}")

hraw = HRAW.read_bytes()
h = hraw[:0x100000]
s = SIMG.read_bytes()
d = json.loads(ART.read_text())
ev = json.loads(EVIDENCE.read_text())
df = json.loads(DF.read_text())

print("== deterministic generator ==")
with tempfile.TemporaryDirectory() as td:
    out = Path(td) / "secoc.json"
    cp = subprocess.run(
        [sys.executable, str(BUILDER), "--out", str(out)],
        cwd=REPO,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        check=False,
    )
    check("builder exits successfully", cp.returncode == 0, cp.stdout[-500:] if cp.returncode else "")
    check("builder reproduces tracked artifact", cp.returncode == 0 and json.loads(out.read_text()) == d)

print("\n== image/evidence binding ==")
check("H image hash is pinned", sha(h) == d["images"]["corolla_h_sha256"] == ev["image"]["sha256"])
check("Sienna image hash is pinned", sha(s) == d["images"]["sienna_sha256"])
check("decompiler evidence contains 22 functions", ev["function_count"] == 22 == len(ev["functions"]))
all_bodies = True
all_c = True
for row in ev["functions"]:
    entry = int(row["entry"], 16)
    all_bodies &= sha(h[entry:entry + row["body_size"]]) == row["body_sha256"]
    all_c &= sha(row["decompiled_c"].encode()) == row["decompiled_c_sha256"]
check("all cited H raw function bodies validate", all_bodies)
check("all cited decompiler records validate", all_c)

print("\n== queue records and shared selector ==")
check("exact H protected queue IDs", [r["can_id"] for r in d["secoc_records"]] == ["0x00F", "0x0D7", "0x0B6"])
check("all queue records use SecOC config ID 0", all(r["secoc_crypto_config_id"] == 0 for r in d["secoc_records"]))
check("all queue records use CryptoIf job handle 0", all(r["cryptoif_job_handle"] == 0 for r in d["secoc_records"]))
check("config object is exact type1/slot4", d["shared_crypto_selection"]["config_bytes"] == "0100000004000000000000000000000000000000")
check("config object selects ICU-S slot 4", d["shared_crypto_selection"]["config_type"] == 1 and d["shared_crypto_selection"]["icus_slot_selector"] == 4)
check("H and Sienna use the same slot-4 config bytes", d["shared_crypto_selection"]["same_bytes_as_sienna"])
check("raw H config bytes agree", h[0x2570C:0x25720].hex() == d["shared_crypto_selection"]["config_bytes"])
check("raw Sienna config bytes agree", s[0x25950:0x25964].hex() == d["shared_crypto_selection"]["config_bytes"])

print("\n== command-7 CPU/ICU boundary ==")
path = d["command7_cpu_to_icus_path"]
check("command-7 path retains no raw key bytes", path["raw_key_bytes_in_cpu_command_descriptor"] is False)
check("command-7 prepare is pinned", path["icus_command7_prepare"] == "0x822D0")
check("command-7 driver is pinned", path["icus_command7"] == "0x83BF4")
check("selector flow ends in ICUSCMD command 7", "writes (word4 << 16) | 7 to ICUSCMD" in path["selector_flow"][-1])
check("disabled H KAT uses same config", d["slot4_kat"]["config_bytes"] == d["shared_crypto_selection"]["config_bytes"])
check("disabled H KAT gate is zero", d["slot4_kat"]["compile_gate_address"] == "0x2CA9F" and h[0x2CA9F] == 0 and not d["slot4_kat"]["enabled"])

print("\n== authenticated key update boundary ==")
ku = d["command8_key_update"]
check("key update accepts exact 64-byte package", ku["request_length"] == 64 and ku["staging_shape"] == [16, 32, 16])
check("key update returns 48-byte proof/result", ku["success_output_length"] == 48)
check("key update submits literal ICU command 8", ku["icus_command"] == 8 and ku["driver"] == "0x83D7A")
check("CPU descriptor has no fixed target slot", ku["fixed_cpu_side_target_slot_selector"] is None)

print("\n== DataFlash evidence boundary ==")
neg = d["dataflash_raw_key_negative"]
check("tracked DataFlash hash is pinned", neg["snapshot_sha256"] == df["dump_sha256"])
check("raw-window scan denominator is 23,277", neg["candidates_tested"] == df["key_domain_scan"]["candidates_tested"] == 23277)
check("raw-window scan found no candidate match", neg["matches"] == df["key_domain_scan"]["matches"] == [])
check("report preserves cross-epoch/derivation caveat", "not proven same-runtime-epoch" in neg["boundary"] and "does not exclude transformed/derived" in neg["boundary"])

print("\n== final static model ==")
model = d["static_storage_derivation_conclusion"]
check("slot selector is CPU-visible", model["cpu_visible_slot4_selector"] is True)
check("raw slot-4 key is not CPU-visible on mapped verify path", model["cpu_visible_raw_slot4_key"] is False)
check("mapped SecOC init has no recovered raw-key load", model["mapped_secoc_init_raw_key_load_found"] is False)
check("mapped SecOC init has no recovered key derivation", model["mapped_secoc_init_key_derivation_found"] is False)
check("authenticated provisioning interface is recovered", model["provisioning_interface_found"] is True)

print(f"\nResults: {passed} passed, {failed} failed")
raise SystemExit(1 if failed else 0)
