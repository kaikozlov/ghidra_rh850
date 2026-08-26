#!/usr/bin/env python3
"""Verify the retained Albino eps-telescope probe and target-native joins."""
from __future__ import annotations

import hashlib
import json
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / "data/generated/corolla_2023_albino_telescope_analysis.json"
PROBE = ROOT / "community/albinoelephant/telescope/probe.json"
PROBE_MD = ROOT / "community/albinoelephant/telescope/probe.md"
CODEFLASH = ROOT / "community/albinoelephant/normalized/8965H1202000_CodeFlash.bin"
GEN = ROOT / "tools/analyze_albino_telescope_probe.py"
APP_DIAG = ROOT / "data/generated/corolla_8965H1202000_application_diagnostics_diff.json"
APP_DECOMP = ROOT / "data/generated/corolla_8965H1202000_application_diagnostic_decompiler_evidence.json"
GATE = ROOT / "data/generated/secoc_gate_resolution_8965H1202000_minimal.json"

passed = failed = 0


def check(name: str, condition: object, detail: str = "") -> None:
    global passed, failed
    ok = bool(condition)
    passed += int(ok)
    failed += int(not ok)
    suffix = f" ({detail})" if detail else ""
    print(f"[{'PASS' if ok else 'FAIL'}][dynamic_trace] {name}{suffix}")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


art = json.loads(ART.read_text(encoding="utf-8"))
probe = json.loads(PROBE.read_text(encoding="utf-8"))
cf = CODEFLASH.read_bytes()

print("== retained contributor artifacts ==")
check("schema v1", art["schema"] == "corolla-2023-albino-telescope-analysis-v1")
check("probe JSON hash pinned", art["source"]["probe_json_sha256"] == "0a5e318a9c6e8e2278633ea9f4e6f60a8721a666c06fe605993a7447b584733e" == sha(PROBE))
check("probe markdown hash pinned", art["source"]["probe_md_sha256"] == "30e537b6f3e38772201519ab4ed2ead36ae05a3e91910f0dd382c72cff69ec86" == sha(PROBE_MD))
check("probe timestamp/address/depth retained", art["source"]["timestamp"] == "2026-08-26T01:49:18Z" and art["source"]["diagnostic_address"] == "0x7A1" and art["source"]["depth"] == "shellcode")
with tempfile.TemporaryDirectory(prefix="albino-telescope-") as td:
    out = Path(td) / "analysis.json"
    proc = subprocess.run([str(ROOT / ".venv/bin/python"), str(GEN), "--output", str(out)], capture_output=True, text=True)
    check("analysis generator runs", proc.returncode == 0, proc.stderr.strip())
    check("tracked analysis is generator-drift free", proc.returncode == 0 and out.read_bytes() == ART.read_bytes())

print("\n== direct application/boot identity ==")
app = art["identity"]["application_f181"]
check("application F181 is direct two-record response", app["count"] == 2 and [r["ascii"] for r in app["records"]] == ["8965F1208000", "8A3111202000"])
check("application F181 raw transcript is exact", app["raw_hex"] == probe["meta"]["app_f181"])
check("F181 record1 source bytes are exact", cf[0x20860:0x20870] == bytes.fromhex(app["records"][0]["raw_hex"]))
check("F181 record2 source bytes are exact", cf[0x17DC0:0x17DD0] == bytes.fromhex(app["records"][1]["raw_hex"]))
check("8965H1202000 is separate DID2032 identity", art["identity"]["auxiliary_single_record_identity"] == {"ascii": "8965H1202000", "did": "0x2032", "source": "0x17D80"})
boot = art["identity"]["boot_f181"]
check("boot F181 is count2 plus 32 bang placeholders", boot["count"] == 2 and art["identity"]["boot_f181_is_two_bang_placeholders"] and bytes.fromhex(boot["raw_hex"])[1:] == b"\x21" * 32)
check("live PRDNAME identifies R7F701383", art["identity"]["prdname_ascii"] == "R7F701383")

app_diag = json.loads(APP_DIAG.read_text(encoding="utf-8"))
check("target diagnostic artifact maps F181 to callback 4A328", any(row.get("did") == "0xF181" and row.get("corolla_h_callback") == "0x4A328" for row in app_diag.get("declared_length_changes", [])) or '"corolla_h_callback": "0x4A328"' in APP_DIAG.read_text())
check("target diagnostic artifact maps one-record identity producer to 2032", '"0x2032"' in APP_DIAG.read_text() and '"callback": "0x4A2E0"' in APP_DIAG.read_text())
decomp = APP_DECOMP.read_text(encoding="utf-8")
check("target-native F181 producer reads 20860 and 17DC0", "0x20860" in decomp and "DAT_00017dc0" in decomp and "FUN_0004a328" in decomp)

print("\n== live CodeFlash and Gate-2 joins ==")
join = art["live_codeflash_sample_join"]
check("tracked normalized CodeFlash hash pinned", join["tracked_codeflash_sha256"] == "0b47bdc1217835c839e3543e52eab40eb793650a9c159e46f6a9b365ea41a67f" == sha(CODEFLASH))
check("three live CodeFlash samples join exactly", join["all_exact"] and len(join["samples"]) == 3 and join["total_live_bytes_compared"] == 384)
check("sample addresses are exact", [r["address"] for r in join["samples"]] == ["0x8E6A0", "0xFFDE0", "0x17D80"])
check("live egg scan finds only Corolla Gate-2", art["gate2"]["live_egg_candidates"] == ["0x88C62"] and art["gate2"]["candidate_is_exact"])
check("tracked egg bytes are exact", art["gate2"]["tracked_candidate_bytes"] == "e0d19a0d1a38bfff" == cf[0x88C62:0x88C6A].hex())
check("relocated 64-byte gate window equals pinned Sienna fingerprint", art["gate2"]["tracked_64b_window_sha256"] == "50d793a2942716dcf0582238edfe6c2d72378eea8bd4e1bf575a8539cd497350" and art["gate2"]["matches_pinned_sienna_window_sha256"])
check("probe honestly records candidate context as unstaged", art["gate2"]["probe_candidate_window_status"] == "NO_DATA")
gate = json.loads(GATE.read_text(encoding="utf-8"))
check("existing semantic resolver agrees with live egg", gate["patch"] == {"address": "0x00088c62", "original": "e0d1", "replacement": "e001", "operation": "cmp-second-register-to-first-force-fallthrough"})

print("\n== target-native boot integrity ==")
bi = art["boot_integrity"]
check("live and tracked adjust word join", bi["live_adjust_word"] == bi["tracked_adjust_word"] == "0xAD59D70C")
check("tracked H CRC range has valid stock residue", bi["tracked_crc_range"] == ["0x18000", "0xFFDF0"] and bi["tracked_crc32"] == "0xFFFFFFFF")
check("live DCRA terminal registers are retained exactly", bi["live_dcra1cin"] == "0x6DAAE993" and bi["live_dcra1cout"] == "0xFFFFFFFF" and bi["live_dcra1ctl"] == "0x00000000")

print("\n== authenticated RAM bootstrap and live crypto state ==")
b = art["authenticated_ram_bootstrap"]
check("live boot SecurityAccess accepted", b["security_access_ok"] is True)
check("live 10F0 envelope authentication accepted", b["envelope_auth_ok"] is True)
check("live deep-probe stream is valid", b["stream_valid"] is True and b["region_crc_failures"] == [])
check("telescope used zero 0201/0202 session values", b["did_0201_key_material"] == "00" * 16 and b["did_0202_iv"] == "00" * 16)
check("live derived payload key matches recovered KDF", b["derived_payload_key_matches"] and b["derived_payload_key_observed"] == b["derived_payload_key_expected"] == "80d221a05622b4f9d4f287922e6c78d1")
check("boot/payload secrets are image-bound rather than free constants", b["payload_build_secret_source"].endswith("@0xBFD8") and b["boot_sa_secret_source"].endswith("@0xBFE8") and cf[0xBFD8:0xBFE8].hex() == "ba052435f8843f985fd1329d2b6117b0" and cf[0xBFE8:0xBFF8].hex() == "f05f36b7d78c03e24ab4faef2a57d044")
check("live boot SA seed snapshot is nonzero", b["boot_sa_seed_snapshot"] == "ef309a63a0572b7a147b7062aa1073a3")
check("zero-record boot SA stage1 key is exact", b["boot_sa_zero_record_stage1_key"] == "f18878ad2a00e3bf78992beb90684f9f")
check("observed-seed expected SA response is exact", b["boot_sa_expected_response_for_snapshot"] == "1c673fae8a534600c6d529143ed25ce7")
check("four retained boot SA seeds are all distinct", len(b["all_observed_boot_sa_seed_snapshots"]) == 4 and b["all_boot_sa_seed_snapshots_unique"])
check("three earlier range-dump sessions share their payload CMAC scratch", len({r["payload_cmac_work_buffer"] for r in b["prior_retained_ram_snapshots"]}) == 1)
check("telescope payload CMAC scratch differs from earlier dumper", b["payload_cmac_work_buffer"] not in {r["payload_cmac_work_buffer"] for r in b["prior_retained_ram_snapshots"]})

print("\n== register/boundary discipline ==")
r = art["live_registers"]
check("self-programming ID registers are observed, not generalized", r["selfid"] == ["0xFFFFFFFF"] * 4 and r["selfidst"] == "0x00000000" and "not proof" in r["boundary"])
check("probe stayed out of flash P/E entry state", r["fentryr"] == "0x0000" and r["fhve15"] == "0x00000000" and r["fhve3"] == "0x00000000")
check("boundaries exclude slot4 inference", any("slot-4" in text and "not" in text for text in art["boundaries"]))
check("boundaries distinguish prior boot RAM exec from resident application carrier", any("earlier range-dump" in text and "does not prove application-context" in text for text in art["boundaries"]))

print(f"\nResults: {passed} passed, {failed} failed")
raise SystemExit(1 if failed else 0)
