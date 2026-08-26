#!/usr/bin/env python3
"""Verify the static Corolla H/F command-5 runtime-carrier candidate and audited builds."""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / "data/generated/corolla_hf_command5_runtime_carrier.json"
EVID = ROOT / "data/generated/corolla_hf_command5_runtime_carrier_evidence.json"
EXTRACTOR = ROOT / "tools/extract_corolla_hf_command5_runtime_carrier_evidence.py"
BUILDER = ROOT / "tools/build_corolla_hf_command5_runtime_carrier.py"
RUNTIME_BUILDER = ROOT / "exploit/ephemeral_runtime/build_corolla_hf_command5_carrier.py"
PROXY_SOURCE = ROOT / "exploit/ephemeral_runtime/corolla_hf_command5_proxy.c"
CANARY_SOURCE = ROOT / "exploit/ephemeral_runtime/corolla_hf_canary.c"
PROXY_AUDIT = ROOT / "exploit/ephemeral_runtime/audited_corolla_hf_command5_proxy_build.json"
CANARY_AUDIT = ROOT / "exploit/ephemeral_runtime/audited_corolla_hf_canary_build.json"
PROXY_BIN = ROOT / "exploit/ephemeral_runtime/audited/corolla_hf_command5_proxy.bin"
CANARY_BIN = ROOT / "exploit/ephemeral_runtime/audited/corolla_hf_runtime_canary.bin"
H = ROOT / "community/albinoelephant/normalized/8965H1202000_CodeFlash.bin"
F = ROOT / "community/spanconstant/raw-20260821/span-corolla-2025.20260821-1511/dump_codeflash_00000000_00200000_20260821-152033.bin"
RAMREQ = ROOT / "data/variant_ram_exec_requirements.json"
DOC = ROOT / "docs/variants/corolla-h-f-openpilot-state-bridge.md"
FINDINGS = ROOT / "docs/status/FINDINGS.md"
PRIORITIES = ROOT / "docs/status/PRIORITIES.md"
OPEN = ROOT / "docs/status/OPEN_QUESTIONS.md"
SENDER = ROOT / "docs/security/secoc/sender-implementation.md"

passed = failed = 0


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def check(name: str, cond: object) -> None:
    global passed, failed
    ok = bool(cond)
    passed += int(ok)
    failed += int(not ok)
    print(f"[{'PASS' if ok else 'FAIL'}] {name}")


a = json.loads(ART.read_text())
ev = json.loads(EVID.read_text())
h = H.read_bytes()
fraw = F.read_bytes()
proxy_audit = json.loads(PROXY_AUDIT.read_text())
canary_audit = json.loads(CANARY_AUDIT.read_text())

print("== promoted static evidence ==")
check("artifact schema/scope", a["schema"] == "corolla-hf-command5-runtime-carrier-v1" and a["applies_to"] == ["8965H1202000", "8965F1208000"])
check("evidence schema", ev["schema"] == "corolla-hf-command5-runtime-carrier-evidence-v1")
check("evidence extractor hash pinned", ev["generator"]["sha256"] == sha(EXTRACTOR.read_bytes()))
check("exact H normalized image pinned", ev["sources"]["h_normalized_codeflash"]["sha256"] == sha(h) == "0b47bdc1217835c839e3543e52eab40eb793650a9c159e46f6a9b365ea41a67f")
check("exact F source range dump pinned", ev["sources"]["f_source_range_dump"]["sha256"] == sha(fraw) == "b8fa3d951f59fb75c190ce1b2c73164adb952f871650cfcd3b7656f08a9c448d")
check("F normalized first MiB identity distinct/pinned", ev["sources"]["f_normalized_first_mib"]["sha256"] == sha(fraw[:0x100000]) == "fdb35b76891cf84a8b89e0a05c9c7c5cfcd27994cf85ccc01ff32828f53091f6")
check("listed H/F prerequisites byte-identical", ev["h_f_exact_transfer"]["all_ranges_byte_equal"] and all(r["byte_equal"] for r in ev["h_f_exact_transfer"]["ranges"]))

print("\n== carrier pocket / MPU ==")
g = a["carrier_geometry"]
check("candidate is exact 464-byte lower-page pocket", g["base"] == "0xFEBF0000" and g["end_inclusive"] == "0xFEBF01CF" and g["end_exclusive"] == "0xFEBF01D0" and g["size"] == 464)
check("first normalized direct reference starts exactly after pocket", g["first_recovered_normalized_reference"] == "0xFEBF01D0" and g["normalized_direct_reference_count_inside"] == 0)
check("negative proof boundary is explicit", "computed aliases" in g["static_negative_boundary"] and "DMA" in g["static_negative_boundary"] and "live canary" in g["static_negative_boundary"])
check("candidate resides in exact H MPU region5", g["mpu_region_index"] == 5 and g["mpu_bounds"] == ["0xFEBEF400", "0xFEBF33FC"])
check("candidate MPAT is B8 in both contexts", g["mpat_contexts"] == ["0x000000B8", "0x000000B8"] and "read-write-execute" in g["permissions"])

print("\n== mailbox ==")
m = a["mailbox_geometry"]
check("mailbox geometry exact", m["base"] == "0xFEBFFB80" and m["end_exclusive"] == "0xFEBFFBBC" and m["size"] == 60)
check("mailbox has zero recovered normalized direct refs", m["normalized_direct_reference_count_inside"] == 0)
check("mailbox stays in H XCP shadow and above startup copy", m["xcp_shadow_window"] == ["0xFEBF7C00", "0xFEBFFBFF"] and m["startup_shadow_copy_end_inclusive"] == "0xFEBFF9EF")
check("proxy self-initializes request byte before interrupts", all(x in m["request_state_initialization"] for x in ("proxy initializes", "request_state", "0", "before enabling interrupts", "sampled once per foreground tick")))
check("proxy mirrors driver status into host-readable mailbox", m["result_status_offset"] == 1 and all(x in m["result_status_protocol"] for x in ("FEBF1280/FEBF1281", "mailbox byte +1", "request_state=0", "immediate non-busy")))

print("\n== audited executable candidates ==")
canary = a["runtime_candidates"]["inert_canary"]
proxy = a["runtime_candidates"]["fixed_b6_command5_proxy"]
check("canary exact audited bytes", canary["size"] == CANARY_BIN.stat().st_size == 332 and canary["headroom"] == 132 and canary["sha256"] == sha(CANARY_BIN.read_bytes()) == "a32baf46dd8e0599021b5c174763887513b3ba903d40ebe284f19d31c97424f4")
check("proxy exact audited bytes", proxy["size"] == PROXY_BIN.stat().st_size == 462 and proxy["headroom"] == 2 and proxy["sha256"] == sha(PROXY_BIN.read_bytes()) == "3bb96eefae06005c99a0ac52b7f0c64cc5d52e2b0b1fcbb73e0b4ec69609f8d3")
check("both executables entry0/no relocations", canary["entry_offset"] == proxy["entry_offset"] == 0 and canary["relocations"] == proxy["relocations"] == 0)
check("proxy exact B6 command5 contract", proxy["input_length"] == 36 and proxy["driver_record"] == 0 and proxy["key_selector"] == 4 and proxy["dispatcher"] == "0x00082750" and proxy["done_flag"] == "0xFEBF1280" and proxy["status_flag"] == "0xFEBF1281")
check("proxy shared-driver busy retry semantics", "busy result 2" in proxy["busy_behavior"] and "retries" in proxy["busy_behavior"] and "no command-7 abort" in proxy["busy_behavior"])
check("proxy source fixes input length at 36", "(void *)m->input" in PROXY_SOURCE.read_text() and "36u" in PROXY_SOURCE.read_text())
check("proxy source leaves busy request pending", "else if (rc != 2)" in PROXY_SOURCE.read_text())
check("proxy source self-initializes mailbox after startup before interrupts", "m->request_state = 0u;\n  __asm__ volatile(\"ei\");" in PROXY_SOURCE.read_text())
check("proxy caches host request state once per foreground tick", "unsigned char request_state = m->request_state;" in PROXY_SOURCE.read_text() and "else if (request_state == 1u)" in PROXY_SOURCE.read_text())
check("proxy atomically samples adjacent done/status and mirrors both completion paths", "volatile unsigned short *completion" in PROXY_SOURCE.read_text() and "unsigned short completion_state = *completion;" in PROXY_SOURCE.read_text() and "m->result_status = (unsigned char)(completion_state >> 8);" in PROXY_SOURCE.read_text() and "m->result_status = (unsigned char)rc;" in PROXY_SOURCE.read_text())
check("H completion callback raw body is pinned before halfword sampling", H.read_bytes()[0x82F5C:0x82F5C+14].hex() == "4437815a010a440f805a00527f00")
check("canary source is inert wrt command5", "TARGET_COMMAND5_DISPATCH" not in CANARY_SOURCE.read_text() and "TARGET_CANARY_HEARTBEAT" in CANARY_SOURCE.read_text())

print("\n== audit/toolchain trust ==")
for label, audit, source in (("proxy", proxy_audit, PROXY_SOURCE), ("canary", canary_audit, CANARY_SOURCE)):
    check(f"{label} audit source hash", audit["source"]["sha256"] == sha(source.read_bytes()))
    check(f"{label} audit builder hash", audit["builder"]["sha256"] == sha(RUNTIME_BUILDER.read_bytes()))
    check(f"{label} compiler equivalence", audit["toolchain"]["reproduced_byte_exact"] is True and audit["toolchain"]["reference_sha256"] == "273202dc591810b2f587ab8fac044599b57b4e07a24ff61d36b7131b97c00660")
    check(f"{label} static-only review grade", audit["review_status"] == "static-carrier-candidate-not-live-validated")
check("artifact records compiler-equivalence rule", a["toolchain_reproducibility"]["selected_build_reproduced_canonical_reference"] and "byte-exact" in a["toolchain_reproducibility"]["noncanonical_image_acceptance_rule"])

print("\n== dynamic boundary ==")
b = a["boundary"]
check("static carrier candidate is closed", b["static_target_native_carrier_candidate_closed"] is True)
check("verified RAM requirement intentionally not promoted", b["verified_variant_ram_exec_requirement_promoted"] is False)
check("live retention/permission/latency remain open", not b["live_retention_closed"] and not b["live_slot4_permission_closed"] and not b["command5_latency_jitter_closed"])
check("production signer and actuation remain disabled", not b["production_b6_signer_closed"] and not b["vehicle_actuation_authorized"])
variants = {row["id"] for row in json.loads(RAMREQ.read_text())["variants"]}
check("H/F absent from verified variant RAM geometry", "corolla-8965h1202000" not in variants and "corolla-8965f1208000" not in variants)
stages = a["validation_sequence"]
check("canary is mandatory first live stage", [r["stage"] for r in stages] == [1,2,3,4] and stages[0]["name"] == "inert carrier canary" and "before exposing command-5" in stages[0]["purpose"])
check("slot4 permission precedes timing", stages[1]["name"] == "known-input slot4 command5 permission" and stages[3]["name"] == "latency and contention characterization")

print("\n== canonical documentation ==")
doc = DOC.read_text(); findings = FINDINGS.read_text(); priorities = PRIORITIES.read_text(); oq = OPEN.read_text(); sender = SENDER.read_text()
check("canonical report records target-native pocket", "FEBF0000..FEBF01CF" in doc and "462-byte" in doc and "332-byte" in doc)
check("canonical report preserves live-canary boundary", "required first live payload" in doc.lower() and "canary" in doc.lower() and "2 bytes" in doc)
check("TMS-054 registered", "| TMS-054 |" in findings and "462 bytes" in findings and "332-byte" in findings)
check("priority now asks for canary before command5", "inert H/F carrier canary" in priorities and "FEBFFB80" in priorities)
check("OQ-021 reflects static carrier closure", "462-byte" in oq and "332-byte" in oq and "live retention" in oq.lower())
check("sender design separates H/F static carrier from Sienna live runtime", "Corolla H/F target-native carrier candidate" in sender and "not verified RAM geometry" in sender and "live_installer.py" in sender)

print("\n== deterministic artifact builder ==")
with tempfile.TemporaryDirectory(prefix="hf-command5-carrier-") as td:
    out = Path(td) / "carrier.json"
    p = subprocess.run([sys.executable, str(BUILDER), "--out", str(out)], cwd=ROOT, capture_output=True, text=True, check=False)
    check("builder exits cleanly", p.returncode == 0)
    check("builder reproduces artifact exactly", out.exists() and out.read_bytes() == ART.read_bytes())

print(f"\nResults: {passed} passed, {failed} failed")
raise SystemExit(1 if failed else 0)
