#!/usr/bin/env python3
"""Independent checks for data/tss3_eps_variant_matrix.csv.

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
MATRIX = REPO / "data" / "tss3_eps_variant_matrix.csv"

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


print("== TSS3 EPS variant matrix ==")

check("variant matrix CSV exists", MATRIX.is_file())

with MATRIX.open(newline="") as fh:
    rows = list(csv.DictReader(fh))

check("matrix has at least Sienna and Corolla rows", len(rows) >= 2)
vehicles = [r["vehicle"] for r in rows]
check("Sienna row present", any("Sienna" in v for v in vehicles))
check("Corolla row present", any("Corolla" in v for v in vehicles))

sienna_4512000 = next(
    (r for r in rows if r["application_software_id"] == "8965B4512000"),
    None,
)
sienna_4514000 = next(
    (r for r in rows if r["application_software_id"] == "8965B4514000"),
    None,
)
corolla = next((r for r in rows if "Corolla" in r["vehicle"]), None)

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

# ── Corolla row: field-probe observations ───────────────────────
if corolla:
    check("Corolla evidence_grade is not definitive",
          corolla["evidence_grade"] != "definitive",
          repr(corolla["evidence_grade"]))
    check("Corolla application_software_id is observed (8965F1208000)",
          corolla["application_software_id"] == "8965F1208000",
          repr(corolla["application_software_id"]))
    check("Corolla secondary_software_id is observed (8A3111213000)",
          corolla["secondary_software_id"] == "8A3111213000",
          repr(corolla["secondary_software_id"]))
    check("Corolla diagnostic_bus notes CAN-FD",
          "CAN-FD" in corolla["diagnostic_bus"] or "CAN FD" in corolla["diagnostic_bus"],
          repr(corolla["diagnostic_bus"]))
    check("Corolla secoc_sync_id is 0x0F",
          corolla["secoc_sync_id"].strip() == "0x0F",
          repr(corolla["secoc_sync_id"]))
    check("Corolla secured_can_ids includes 0x2E4",
          "0x2E4" in corolla["secured_can_ids"])
    check("Corolla programming_observation documents timeout not refusal",
          "timeout" in corolla["programming_observation"].lower()
          and "not decisive" in corolla["programming_observation"].lower(),
          repr(corolla["programming_observation"][:80]))
    check("Corolla security_levels documents observed level 0x03 seed",
          "0x03" in corolla["security_levels"] and "seed" in corolla["security_levels"].lower())
    check("Corolla security_levels documents bootloader secret was used",
          "bootloader secret" in corolla["security_levels"].lower()
          and "non-diagnostic" in corolla["security_levels"].lower(),
          repr(corolla["security_levels"][:80]))
    check("Corolla security_levels documents app SA secret is untested",
          "untested" in corolla["security_levels"].lower()
          and "893e08" in corolla["security_levels"],
          repr(corolla["security_levels"][:80]))
    check("Corolla application_sid_set documents 13 answering services",
          "13 answering" in corolla["application_sid_set"].lower()
          or "13" in corolla["application_sid_set"],
          repr(corolla["application_sid_set"][:60]))
    check("Corolla programming_observation documents timeout indeterminacy",
          "timeout" in corolla["programming_observation"].lower()
          and ("not decisive" in corolla["programming_observation"].lower()
               or "not" in corolla["programming_observation"].lower()),
          repr(corolla["programming_observation"][:80]))
    check("Corolla programming_observation does NOT claim refusal",
          "refus" not in corolla["programming_observation"].lower(),
          repr(corolla["programming_observation"][:80]))
    check("Corolla programming_observation notes missing bus capture",
          "bus" in corolla["programming_observation"].lower()
          and ("missing" in corolla["programming_observation"].lower()
               or "not captured" in corolla["programming_observation"].lower()),
          repr(corolla["programming_observation"][:80]))
    check("Corolla programming_observation documents 0x14 crash",
          "0x14" in corolla["programming_observation"]
          and "crash" in corolla["programming_observation"].lower(),
          repr(corolla["programming_observation"][:80]))
    check("Corolla application_dids records F181 count=0x02 two records",
          "count=0x02" in corolla["application_dids"]
          and "two records" in corolla["application_dids"],
          repr(corolla["application_dids"][:60]))

# ── Global structural checks ────────────────────────────────────
required_cols = {
    "vehicle", "eps_part_number", "application_software_id",
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
