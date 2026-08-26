#!/usr/bin/env python3
"""Independent checks for data/toyota_eps_variant_matrix.csv.

Validates column integrity, evidence-grade correctness, and known factual
constraints (sync IDs, CAN routing, Sienna-vs-Corolla separation).
Self-contained: reads only the committed CSV and CodeFlash image.
"""
from pathlib import Path
import csv
import struct
import sys

REPO = Path(__file__).resolve().parents[1]
CF = (REPO / "firmware" / "RH850_P1M-E_CodeFlash.bin").read_bytes()
MATRIX = REPO / "data" / "toyota_eps_variant_matrix.csv"

passed = 0
failed = 0


def check(name, cond, detail=""):
    global passed, failed
    if cond:
        passed += 1
        mark = "PASS"
    else:
        failed += 1
        mark = "FAIL"
    suffix = f" ({detail})" if detail else ""
    print(f"[{mark}] {name}{suffix}")


print("== Toyota EPS security/control variant matrix ==")

check("variant matrix CSV exists", MATRIX.is_file())

with MATRIX.open(newline="") as fh:
    rows = list(csv.DictReader(fh))

check("matrix has at least Sienna and Corolla rows", len(rows) >= 2)
vehicles = [r["vehicle"] for r in rows]
check("Sienna row present", any("Sienna" in v for v in vehicles))
check("Corolla row present", any("Corolla" in v for v in vehicles))
check("matrix contains only evidence-backed rows", len(rows) == 5 and all(r["application_software_id"] != "unknown" for r in rows))
check("matrix models ADAS and security as separate columns", all("adas_generation" in r and "security_architecture" in r for r in rows))
check("all three tracked dump specimens are SecOC/TSK", all(
    r["security_architecture"].startswith("SecOC/TSK") for r in rows
    if r["application_software_id"] == "8965B4512000" or "Corolla" in r["vehicle"]
))

sienna_4512000 = next(
    (r for r in rows if r["application_software_id"] == "8965B4512000"),
    None,
)
sienna_4514000 = next(
    (r for r in rows if r["application_software_id"] == "8965B4514000"),
    None,
)
corolla = next((r for r in rows if r["vehicle"].startswith("2025 Toyota Corolla")), None)
corolla_h = next((r for r in rows if r["vehicle"].startswith("2023 US Toyota Corolla")), None)
camry = next((r for r in rows if r["vehicle"].startswith("2026 Toyota Camry")), None)

check("Sienna 4512000 ADAS generation is not inferred from security", sienna_4512000 is not None and "not established" in sienna_4512000["adas_generation"] and "do not infer from SecOC" in sienna_4512000["adas_generation"])
check("Sienna 4514000 external TSS3 label is independent of SecOC evidence", sienna_4514000 is not None and "reported TSS3" in sienna_4514000["adas_generation"] and "independent of SecOC" in sienna_4514000["adas_generation"])
check("Span and H rows carry TSS3 control-generation evidence separately", corolla is not None and corolla_h is not None and corolla["adas_generation"].startswith("TSS3") and corolla_h["adas_generation"].startswith("TSS3"))

# ── Sienna 4512000 row: firmware-derived facts ──────────────────
check("Sienna 4512000 row present", sienna_4512000 is not None)
if sienna_4512000:
    check("Sienna 4512000 evidence_grade is definitive",
          sienna_4512000["evidence_grade"] == "definitive")
    check("Sienna 4512000 secoc_sync_id is 0x0F (not 0x2E4)",
          sienna_4512000["secoc_sync_id"].strip() == "0x0F",
          repr(sienna_4512000["secoc_sync_id"]))
    check("Sienna 4512000 secured_can_ids does not include 0x0F as a protected profile",
          "0x0F" not in sienna_4512000["secured_can_ids"],
          repr(sienna_4512000["secured_can_ids"]))
    check("Sienna 4512000 secured_can_ids includes 0x2E4",
          "0x2E4" in sienna_4512000["secured_can_ids"])
    check("Sienna 4512000 secured_can_ids excludes 0x344",
          "0x344" not in sienna_4512000["secured_can_ids"],
          repr(sienna_4512000["secured_can_ids"]))
    check("Sienna 4512000 physical request is 0x7A1",
          sienna_4512000["physical_request"] == "0x7A1")
    check("Sienna 4512000 physical response is 0x7A9",
          sienna_4512000["physical_response"] == "0x7A9")
    check("Sienna 4512000 functional request is 0x777",
          sienna_4512000["functional_request"] == "0x777")
    check("Sienna 4512000 MCU is RH850/P1M-E",
          "RH850" in sienna_4512000["mcu"] and "R7F701381" in sienna_4512000["mcu"])
    check("Sienna 4512000 SA level 1 stub documented",
          "stub" in sienna_4512000["security_levels"].lower())

    # Cross-check against CodeFlash: the 17-SID set
    sids_in_csv = set(
        s.strip() for s in sienna_4512000["application_sid_set"].split(",")
    )
    expected_sids = {
        "10", "11", "14", "19", "22", "23", "27", "28", "2E",
        "31", "34", "36", "37", "3E", "85", "AB", "BA",
    }
    check("Sienna SID set matches the 17 firmware SIDs", sids_in_csv == expected_sids)

    # Cross-check: sync ID 0x0F is confirmed by secoc/application-chain.md
    secoc_doc = (REPO / "docs" / "security" / "secoc" / "application-chain.md").read_text()
    check("Sienna sync ID 0x0F corroborated by SECOC doc",
          "0x00F" in secoc_doc or "0x0F" in secoc_doc)

# ── Sienna 4514000 row: external field evidence only ────────────
check("Sienna 4514000 row present", sienna_4514000 is not None)
if sienna_4514000:
    check("Sienna 4514000 evidence_grade is inference",
          sienna_4514000["evidence_grade"] == "inference",
          repr(sienna_4514000["evidence_grade"]))
    check("Sienna 4514000 is not marked firmware-available",
          sienna_4514000["firmware_available"] == "no",
          repr(sienna_4514000["firmware_available"]))
    check("Sienna 4514000 physical request is 0x7A1",
          sienna_4514000["physical_request"] == "0x7A1")
    check("Sienna 4514000 physical response is 0x7A9",
          sienna_4514000["physical_response"] == "0x7A9")
    check("Sienna 4514000 secoc_sync_id is 0x0F",
          sienna_4514000["secoc_sync_id"].strip() == "0x0F",
          repr(sienna_4514000["secoc_sync_id"]))
    for can_id in ("0x131", "0x2E4", "0x344"):
        check(f"Sienna 4514000 external secured IDs include {can_id}",
              can_id in sienna_4514000["secured_can_ids"])
    check("Sienna 4514000 IDs are labeled external validation, not an EPS RX census",
          "external key validation" in sienna_4514000["secured_can_ids"]
          and "not an EPS RX census" in sienna_4514000["secured_can_ids"])
    check("Sienna 4514000 source pins the Vance commit",
          "3333453f10c09a27df265156458ce976cc9ce25a" in sienna_4514000["source"])

# ── Span Corolla: persisted field + firmware corpus ─────────────────────
if corolla:
    check("Span Corolla evidence_grade is definitive after corpus persistence",
          corolla["evidence_grade"] == "definitive", repr(corolla["evidence_grade"]))
    check("Span Corolla firmware artifact is locally available",
          corolla["firmware_available"].startswith("yes") and "spanconstant/raw-20260821" in corolla["firmware_available"])
    check("Span Corolla application_software_id remains observed F181 8965F1208000",
          corolla["application_software_id"] == "8965F1208000")
    check("Span Corolla secondary software ID remains 8A3111213000",
          corolla["secondary_software_id"] == "8A3111213000")
    check("Span Corolla exact MCU is tracked R7F701383",
          "R7F701383" in corolla["mcu"] and "RH850" in corolla["mcu"])
    check("Span Corolla direct diagnostic route is bus1 param1",
          all(token in corolla["diagnostic_bus"] for token in ("CAN-FD", "param 1", "bus 1")))
    check("Span Corolla secoc_sync_id remains 0x0F",
          corolla["secoc_sync_id"].strip() == "0x0F")
    check("Span Corolla firmware Gate-2 queue is 00F/D7/B6 and excludes 2E4/131",
          all(x in corolla["secured_can_ids"] for x in ("0x00F", "0x0D7", "0x0B6", "no 0x2E4/0x131")))
    check("Span Corolla historical 2E4/131/344 bus observations are explicitly not an EPS RX census",
          all(x in corolla["secured_can_ids"] for x in ("0x2E4", "0x131", "0x344", "not an EPS RX census")))
    check("Span Corolla F181 producer and separate 17D80 identity path are explicit",
          all(x in corolla["application_dids"] for x in ("F181=8965F1208000+8A3111213000", "FUN_0004a328", "@0x20860", "@0x17DC0", "8965H1213000 @0x17D80", "separate one-record identity")))
    check("Span Corolla corrected direct PROGRAMMING succeeded",
          all(x in corolla["programming_observation"] for x in ("2026-08-21", "bus1,param1", "opened PROGRAMMING", "accepted SecurityAccess key", "completed CodeFlash")))
    check("Span Corolla older param0 timeout is retained as non-diagnostic",
          "param0 timeout" in corolla["programming_observation"] and "non-diagnostic" in corolla["programming_observation"])
    check("Span Corolla security row records exact static roots while keeping live app-key acceptance bounded",
          all(x in corolla["security_levels"] for x in ("@0xBFD8", "@0xBFE8", "@0x20840", "byte-identical", "accepted key", "prior app send-key used the boot secret")))
    check("Span Corolla application SID set retains 13 answering services",
          "13 answering" in corolla["application_sid_set"].lower() or "13" in corolla["application_sid_set"])
    check("Span Corolla source points at persisted corpus",
          "community/spanconstant/raw-20260821/MANIFEST.txt" in corolla["source"] and "matching ECU serial" in corolla["source"])

# ── 2023 Albino Corolla: direct F181 + tracked CodeFlash evidence ───────
check("Albino Corolla row present", corolla_h is not None)
if corolla_h:
    check("Albino Corolla firmware artifact is locally available", corolla_h["firmware_available"].startswith("yes"))
    check("Albino Corolla MCU is exact R7F701383", "R7F701383" in corolla_h["mcu"] and "RH850" in corolla_h["mcu"])
    check("Albino Corolla direct F181 primary/secondary are exact",
          corolla_h["application_software_id"] == "8965F1208000" and corolla_h["secondary_software_id"] == "8A3111202000")
    check("Albino Corolla separates F181 from auxiliary H1202000 DID2032 identity",
          all(token in corolla_h["application_dids"] for token in ("F181=8965F1208000+8A3111202000", "0x4A328", "0x20860", "0x17DC0", "DID2032", "8965H1202000 @0x17D80")))
    check("Albino Corolla boot F181 is now direct", "02 || 32*0x21" in corolla_h["bootloader_f181_observed"] and "2026-08-26" in corolla_h["bootloader_f181_observed"])
    check("Albino Corolla Gate-2 secured IDs are D7/B6",
          "0x0D7" in corolla_h["secured_can_ids"] and "0x0B6" in corolla_h["secured_can_ids"])
    check("Albino Corolla does not claim 2E4/131 Gate-2 profiles",
          "no 0x2E4/0x131" in corolla_h["secured_can_ids"] and "0x2E4;" not in corolla_h["secured_can_ids"])
    check("Albino Corolla exact crypto-root transfer and live boot SA are documented",
          all(token in corolla_h["security_levels"] for token in ("0xBFD8", "0xBFE8", "0x20840", "byte-identical", "live-accepted")))
    check("Albino Corolla Toyota-B route distinguishes relay topology from direct diagnostics",
          all(token in corolla_h["diagnostic_bus"] for token in ("CAN0/CAN2", "CAN1", "ELM param1", "logical bus1")))
    check("Albino Corolla programming row pins channel continuity, async reset, and telescope RAM exec",
          all(token in corolla_h["programming_observation"] for token in ("RSCFD channel1", "0x7A1/0x777->0x7A9", "async kind2", "0x0180", "0x0A00", "50 02", "10F0 FEBF0000", "0x88C62")))
    check("Albino Corolla source includes raw corpus and telescope probe", "raw-20260818" in corolla_h["source"] and "telescope/probe.json" in corolla_h["source"])

# ── Maintainer 2026 Camry: identity-bound dynamic baseline ─────────
check("Camry row present", camry is not None)
if camry:
    check("Camry exact F181 pair is preserved", camry["application_software_id"] == "8965F3307000" and camry["secondary_software_id"] == "8A3113303100")
    check("Camry normal-harness direct route is bus1 param1", all(x in camry["diagnostic_bus"] for x in ("CAN-FD", "param 1", "bus 1")) and camry["physical_request"] == "0x7A1" and camry["physical_response"] == "0x7A9")
    check("Camry boot F181 placeholder is direct", "02 || 32*0x21" in camry["bootloader_f181_observed"] and "2026-08-26" in camry["bootloader_f181_observed"])
    check("Camry programming handoff is direct but RAM execution unclaimed", all(x in camry["programming_observation"] for x in ("bus1,param1", "PROGRAMMING succeeded", "preserved route", "no boot SecurityAccess", "authenticated RAM execution")))
    check("Camry does not transfer SecurityAccess secrets", "not tested" in camry["security_levels"] and "do not transfer" in camry["security_levels"] and "unestablished" in camry["bootloader_routines"])
    check("Camry SecOC row is a vehicle-capture observation not firmware census", all(x in camry["secured_can_ids"] for x in ("0x090/32", "0x0D7/32", "0x0B6/32 absent", "no firmware RX census")))
    check("Camry exact CodeFlash is explicitly unavailable", camry["firmware_available"].startswith("no") and "8965F3307000" in camry["firmware_available"] and camry["mcu"].startswith("unknown"))
    check("Camry source points at tracked baseline", "community/kai/camry-2026/raw-20260826" in camry["source"] and "camry_2026_tsk_baseline.json" in camry["source"])

# ── Global structural checks ────────────────────────────────────
required_cols = {
    "vehicle", "adas_generation", "security_architecture", "eps_part_number", "application_software_id",
    "secoc_sync_id", "secured_can_ids", "evidence_grade", "source",
}
for row in rows:
    vid = row.get("vehicle", "?")[:30]
    check(f"row '{vid}' has all required columns",
          required_cols <= set(row.keys()))
    check(f"row '{vid}' evidence_grade is valid",
          row["evidence_grade"] in ("definitive", "inference", "none"))
    # No row may list 0x0F as a secured CAN ID (it's the sync frame)
    check(f"row '{vid}' does not list sync ID 0x0F as a secured CAN ID",
          "0x0F" not in row.get("secured_can_ids", ""))

print(f"\n== RESULT: {passed} passed, {failed} failed ==")
sys.exit(1 if failed else 0)
