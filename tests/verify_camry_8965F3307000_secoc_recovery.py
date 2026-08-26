#!/usr/bin/env python3
"""Verify retained 8965F3307000 DataFlash/RAM SecOC recovery evidence."""
from __future__ import annotations

import gzip
import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
ROOT = REPO / "community/kai/camry-2026/raw-20260826/secoc-recovery"
ART = REPO / "data/generated/camry_8965F3307000_secoc_recovery.json"
BUILD = REPO / "tools/analyze_camry_8965F3307000_secoc_recovery.py"

passed = failed = 0


def check(name: str, condition: object, detail: str = "") -> None:
    global passed, failed
    ok = bool(condition)
    passed += int(ok)
    failed += int(not ok)
    suffix = f" ({detail})" if detail else ""
    print(f"[{'PASS' if ok else 'FAIL'}][raw_bytes] {name}{suffix}")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


print("== retained source identities ==")
expected = {
    "dataflash/dump_ff200000_ff208000.bin": (0x8000, "231fbdde4ef317931d8f1ff20ff131650f7d773c124a179b0ae3dc98bf8e4432"),
    "ram/local_ram_pe1.bin": (0x20000, "0ddef478b15bcf3241c56573463eda25ba018081629daf0042fcae1204c435a7"),
    "ram/global_ram.bin": (0x10000, "53c8370237c681d4105c513be5096461ac735ffcb9577995c7203216165006a4"),
    "ram/local_ram_pe1.coverage.bin": (0x8000, "bfa5a24faa8ddf576edcc46f4f05e2459ee4a383b8dc14ff7dba0056b9c59ed0"),
    "ram/global_ram.coverage.bin": (0x4000, "111ce3c2a38d83a2e4706bde4abddd509d7f8248116c6832b06745bdc349e09f"),
    "ram/local_ram_pe1.run.json": (None, "ccd6335b2d6f02dcb4dbd76dcb7f436493e34204dbcea7beec509efa3e326d57"),
    "ram/global_ram.run.json": (None, "0474343a39270fa6dfebd267cbc391ce9b6075c8343beafbf7fb1e6ceed52961"),
    "payloads/payload_dataflash_ff200000_ff208000.bin": (0x1000, "d48988366b5e6d2ddd7438caca5e6f6f02daba9b650263c323a2ffd770a06e34"),
    "payloads/payload_local_ram_pe1_febe0000_fec00000.bin": (0x1000, "fbb1f5bd352c3f0bf416d6b1ef6a7696f97cad2b9f49570ca859207f3269e44f"),
    "payloads/payload_global_ram_feef8000_fef08000.bin": (0x1000, "43d00fdaf790c6deb230d3a4e7b8f8bd17e077a100fa53ebb194532f55c510fd"),
    "camry_ram_dump.py": (None, "ac40975761b1a13ca17cdf85131f69fb968934a75de9a3cfe313a231df87cbfe"),
}
for rel, (size, digest) in expected.items():
    path = ROOT / rel
    check(f"{rel} hash", path.is_file() and sha(path) == digest)
    if size is not None:
        check(f"{rel} size", path.stat().st_size == size)

oracle = ROOT / "can_oracle.ndjson.gz"
check("oracle compressed identity", sha(oracle) == "e977f5f0dc3d86786af8ae576d785af46c8facc8e186c4598f692a38ecb95b73")
with gzip.open(oracle, "rb") as stream:
    raw_oracle = stream.read()
check("oracle uncompressed identity", len(raw_oracle) == 37552829 and hashlib.sha256(raw_oracle).hexdigest() == "823622ed360ee1b2c2c156c6196a17d001c845f4d53fbc56922a338a4a46e33c")

print("\n== deterministic artifact regeneration ==")
with tempfile.TemporaryDirectory() as td:
    out = Path(td) / "camry_secoc.json"
    proc = subprocess.run([sys.executable, str(BUILD), "--out", str(out)], cwd=REPO, capture_output=True, text=True, check=False)
    check("recovery analyzer succeeds", proc.returncode == 0, proc.stderr[-300:])
    check("recovery artifact regenerates exactly", proc.returncode == 0 and out.read_bytes() == ART.read_bytes())

art = json.loads(ART.read_text())
check("artifact schema exact", art["schema"] == "camry-8965f3307000-secoc-recovery-v1")
check("artifact exact F33 route", art["target"]["f181"] == "8965F3307000" and art["target"]["secondary_identity"] == "8A3113303100" and art["target"]["diagnostic_route"] == {"bus": 1, "elm327_param": 1, "rx": "0x7A9", "tx": "0x7A1"})

print("\n== DataFlash object-15 disposition ==")
obj15 = art["dataflash"]["object15"]
check("object15 has zero valid copies", obj15["valid_copy_count"] == 0 and not obj15["valid_consensus"])
check("object15 triplicate geometry exact", obj15["copy_addresses"] == ["0xFF206E00", "0xFF206D00", "0xFF206C00"])
check("object15 key-field geometry exact", obj15["key_field_addresses"] == ["0xFF206E14", "0xFF206D14", "0xFF206C14"])
check("all object15 key fields are raw zero", obj15["key_fields_zero"] == [True, True, True])

df = (ROOT / "dataflash/dump_ff200000_ff208000.bin").read_bytes()
for off in (0x6E14, 0x6D14, 0x6C14):
    check(f"DataFlash +0x{off:04X} raw zero16", df[off:off + 16] == bytes(16))

print("\n== RAM acquisition and legacy-table rejection ==")
local = art["local_ram_pe1"]
global_ram = art["global_ram"]
for name, node, expected_words in (("local", local, 32768), ("global", global_ram, 16384)):
    acq = node["acquisition"]
    check(f"{name} RAM acquisition complete", acq["status"] == "complete" and acq["coverage_percent"] == 100.0 and acq["unique_words"] == acq["expected_words"] == expected_words)
    check(f"{name} RAM acquisition clean", acq["duplicate_words"] == 0 and acq["conflicts"] == 0 and acq["spi_errors"] == 0 and acq["coverage"]["all_words_covered"])
    check(f"{name} RAM exact target guard", acq["application_f181_exact"] and acq["boot_f181_exact"] and acq["nrt_ready_values"] == [0])
    check(f"{name} RAM exact old-stack bootstrap", acq["old_stack_zero_dids"] and acq["verify_10f0_accepted"] and acq["ff00_sent"])
check("PE1 acquisition clobber is explicit", local["clobber_range"] == ["0xFEBF0000", "0xFEBF1000"] and local["acquisition"]["clobber_range"] == ["0xfebf0000", "0xfebf1000"])
check("application-SA root mirrors once at FEBF7B80", local["app_sa_root_hits"] == ["0xFEBF7B80"])
check("payload/boot roots are not raw LocalRAM values", local["payload_build_root_hits"] == [] and local["boot_sa_root_hits"] == [])
check("payload/boot/application roots absent from GlobalRAM", global_ram["app_sa_root_hits"] == [] and global_ram["payload_build_root_hits"] == [] and global_ram["boot_sa_root_hits"] == [])
legacy = local["legacy_key_table"]
check("legacy FEBE6E34 layout has 14 records and zero valid checksums", legacy["record_count"] == 14 and legacy["valid_checksum_count"] == 0 and all(not row["checksum_valid"] for row in legacy["records"]))
check("legacy would-be KEY_1 field is zero", legacy["old_extractor_key_1"]["key_field_address"] == "0xFEBE6E60" and legacy["old_extractor_key_1"]["key_field_zero"])
check("legacy would-be KEY_4 record is checksum-invalid", legacy["old_extractor_key_4"]["key_field_address"] == "0xFEBE6EC0" and not legacy["old_extractor_key_4"]["checksum_valid"])
check("legacy FEBF42E0 factory record is zero", legacy["old_factory_record_0xFEBF42E0_zero"])

print("\n== CAN oracle and retained exhaustive matcher result ==")
oracle_art = art["oracle"]
focus = oracle_art["focus_bus1_streams"]
check("oracle is about 60 s", 59000 < oracle_art["duration_ms"] < 61000)
check("native sync 0x00F retained", focus["0x00F"] == {"count": 618, "length_counts": {"8": 618}})
check("native FD 0x0D7 retained", focus["0x0D7"] == {"count": 3095, "length_counts": {"32": 3095}})
check("native FD 0x090 retained", focus["0x090"] == {"count": 6190, "length_counts": {"32": 6190}})
check("B6 absent only in this stationary oracle", focus["0x0B6"]["count"] == 0)
scan = art["offline_key_scan"]
check("matcher provenance exact", scan["matcher"]["repository"] == "kai-openpilot" and scan["matcher"]["commit"] == "2bfbef37fddbdf4e499a4adc55005474f3c5ffcf")
check("matcher oracle sample set exact", scan["oracle"]["sync_samples"] == 208 and scan["oracle"]["protected_samples"] == 813 and scan["oracle"]["malformed"] == 0)
expected_scans = {
    "dataflash": (32753, 32753),
    "local_ram_pe1": (131057, 126946),
    "global_ram": (65521, 65521),
}
for name, (windows, eligible) in expected_scans.items():
    row = scan["scans"][name]
    check(f"{name} scan exhausted every eligible window", row["status"] == "not_found" and row["windows_scanned"] == windows and row["windows_eligible"] == eligible and row["survivors"] == 0 and row["matches"] == 0)
    check(f"{name} scan saw the full capped oracle", row["sync"] == "0/208" and row["protected"] == "0/813")
check("LocalRAM matcher excluded the payload span", scan["scans"]["local_ram_pe1"]["excluded_clobber"] == ["0xFEBF0000", "0xFEBF1000"] and scan["scans"]["local_ram_pe1"]["coverage_known"])

print("\n== documentation ==")
doc = (REPO / "docs/variants/camry-2026-live-baseline.md").read_text()
findings = (REPO / "docs/status/FINDINGS.md").read_text()
readme = (REPO / "community/kai/camry-2026/README.md").read_text()
for token in ("231fbdde4ef31793", "0xFF206E14", "0xFEBF7B80", "126,946", "65,521"):
    check(f"canonical report contains {token}", token in doc)
check("VAR-055 retained", "| VAR-055 |" in findings and "8965F3307000" in findings)
check("community README points to SecOC recovery evidence", "secoc-recovery" in readme and "LocalRAM" in readme and "GlobalRAM" in readme)

print(f"\nResults: {passed} passed, {failed} failed")
raise SystemExit(1 if failed else 0)
