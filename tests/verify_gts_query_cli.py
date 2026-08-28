#!/usr/bin/env python3
"""Verify the unified read-only GTS+ query surface against pinned external artifacts."""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools" / "techstream"))

import ddb_strings
import gts_cli
from parse_ddb import DDBParser


def check(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)
    print(f"[PASS] {message}")


gts = gts_cli._resolve_gts_root()
db_root = gts_cli._db_root(gts)
cuwplus = gts_cli._resolve_cuwplus_root(gts)
corpus = gts_cli._resolve_cuw_corpus()

check((db_root / "EMPS_P5.ddb").is_file(), "current GTS+ EMPS_P5 database is available")
check((db_root / "M_English.ddb").is_file(), "current GTS+ English OEM string database is available")
check((cuwplus / "Ini/P5-Unified04.ini").is_file(), "current CUWPlus P5-Unified04 route is available")
check((corpus / "T-0051-26.cuw").is_file(), "pinned Camry CUW is available")

with tempfile.TemporaryDirectory(prefix="gts-cache-prune-") as td:
    cache_root = Path(td)
    current_cache = cache_root / "M_English-current.bin"
    current_cache.write_bytes(b"current")
    for index in range(6):
        (cache_root / f"M_English-old{index}.bin").write_bytes(bytes([index]))
    ddb_strings._prune(current_cache)
    remaining = list(cache_root.glob("M_English-*.bin"))
    check(current_cache in remaining, "string-cache pruning always preserves the current decode")
    check(
        len(remaining) == ddb_strings.CACHE_GENERATIONS_TO_KEEP,
        "string-cache pruning keeps a bounded multi-release working set",
    )

with tempfile.TemporaryDirectory(prefix="gts-root-routing-") as td:
    fixture = Path(td)
    selected_gts = fixture / "release/unpacked/gtsplus/Toyota Diagnostics/GTSPlus"
    adjacent_cuwplus = fixture / "release/cuwplus/CUWPlus"
    explicit_cuwplus = fixture / "explicit/CUWPlus"
    selected_gts.mkdir(parents=True)
    adjacent_cuwplus.mkdir(parents=True)
    explicit_cuwplus.mkdir(parents=True)
    check(
        gts_cli._resolve_cuwplus_root(selected_gts) == adjacent_cuwplus.resolve(),
        "selected GTS+ tree prefers its adjacent CUWPlus routes over repository defaults",
    )
    check(
        gts_cli._resolve_cuwplus_root(selected_gts, explicit_cuwplus) == explicit_cuwplus.resolve(),
        "explicit CUWPlus root overrides adjacent/default route trees",
    )
    adjacent_cuwplus.rmdir()
    unresolved = gts_cli._resolve_cuwplus_root(selected_gts)
    check(
        not unresolved.exists() and unresolved != cuwplus,
        "alternate GTS+ tree without CUWPlus never borrows repository-default writer routes",
    )

parser = DDBParser()
strings = gts_cli._english_strings(parser, db_root)
master = parser.parse_master_db(db_root / "Toyota.ddb")
hybrid = gts_cli._resolve_master_category(parser, master, strings, "HV_P5")
check(hybrid["category_id"] == 397 and hybrid["name"] == "Hybrid Control", "master category resolver joins HV_P5 to category 397 Hybrid Control")
plugins = gts_cli._master_plugins(parser, master, hybrid["category_id"])
check(any(row == {"role": 25, "role_hex": "0x19", "dll": "DelDiagCodeP4.dll"} for row in plugins), "current master plugin resolver decodes DelDiagCodeP4 role 0x19")
commsets = gts_cli._master_comm_set_rows(parser, master)
commset1 = next(row for row in commsets if row["comm_set_id"] == 1)
check(len(commsets) == 13 and commset1["raw"] == "e8030000fc0300000000010000000100", "current master exposes 13 stable 16-byte CommSet rows")
check(commset1["receive_timeout"] == 1020 and commset1["retry_count"] == 1, "current CommSet 1 resolves receive timeout 1020 and one retry")
timers = gts_cli._master_timer_rows(parser, master, hybrid["category_id"])
check(
    timers == [{"category_id": 397, "timer_id": 1, "delay_ms": 0, "unknown_dword_08": 0, "raw": "000000008d01010000000000"}],
    "current Hybrid timer 1 resolves to zero-millisecond post-command delay",
)

role_catalog = gts_cli._master_role_catalog(parser, master, gts / "bin")
role19 = next(row for row in role_catalog if row["role"] == 25)
check(len(role_catalog) == 191 and role19["binding_count"] == 536 and role19["category_count"] == 536 and role19["binding_surface_counts"] == {"direct_transport": 536} and role19["plugins"][0]["dll"] == "DelDiagCodeP4.dll" and role19["plugins"][0]["binding_count"] == 424, "current master role census resolves operation surfaces as well as 6194 -> 191 role compression")
role5 = next(row for row in role_catalog if row["role"] == 5)
check(role5["plugins"][0]["surface"] == "support_cache_v18_proven" and role5["plugins"][1]["surface"] == "delegated_transport_v18_proven", "role query distinguishes P4 cached support from P5 delegated support probing")
primary = gts_cli._master_frame_rows(parser, master, hybrid["category_id"], 0x01)
check(len(primary) == 1 and primary[0]["comm_set_metadata"]["receive_timeout"] == 1020 and primary[0]["comm_set_metadata"]["retry_count"] == 1 and primary[0]["send"] == {"id": "0x2743", "normalized_id": "0x33", "bytes": "04"} and primary[0]["receive_check"] == {"id": "0x28F7", "normalized_id": "0x1E7", "bytes": "44"}, "current master selector 1 resolves namespaced variables to 04 -> 44")
fallback = gts_cli._master_frame_rows(parser, master, hybrid["category_id"], 0x102)
check(len(fallback) == 1 and fallback[0]["send"] == {"id": "0x2D28", "normalized_id": "0x618", "bytes": "14ffffff"} and fallback[0]["receive_check"] == {"id": "0x28E4", "normalized_id": "0x1D4", "bytes": "54"}, "current master selector 0x102 resolves namespaced variables to 14FFFFFF -> 54")
emps = parser.parse_ecu_db(db_root / "EMPS_P5.ddb")
rows = gts_cli._monitor_rows(emps, strings, "EMPS_P5.ddb")
rows_1cee = [row for row in rows if row["primary_did"] == 0x1CEE]
names_1cee = {row["name"] for row in rows_1cee}
check("Advanced Drive Target Steering Angle" in names_1cee, "DID 0x1CEE resolves Advanced Drive Target Steering Angle")
check("Target Steering Angle After Output Compensation" in names_1cee, "DID 0x1CEE retains the second Toyota interpretation")
check(
    len({(row["name"], row["primary_did"], row["alternate_did"]) for row in rows}) == len(rows),
    "overlapping current Data List table aliases are deduplicated",
)

routes = gts_cli._route_rows(cuwplus)
route04 = [row for row in routes if row["contact_type"] == "P5-Unified04"]
check(len(route04) == 1, "P5-Unified04 resolves one current CUWPlus route")
check(route04[0]["cid_getter"] == "TCUWCanUnifiedCIDGetter.dll", "P5-Unified04 resolves Unified CID getter")
check(route04[0]["prepare_writer"] == "TCUWCanReproStdPrepareWriter.dll", "P5-Unified04 resolves ReproStd prepare writer")
check(route04[0]["flash_writer"] == "TCUWCanReproStdFlashWriter.dll", "P5-Unified04 resolves ReproStd flash writer")
check(gts_cli._route_match("P5-Unified04", route04[0]), "route matcher searches semantic route values")
check(
    not gts_cli._route_match("DLLFileNameForPrepareWrite", route04[0]),
    "route matcher does not leak raw CSV header names into search results",
)

fast_outer, fast_descriptor = gts_cli._cuw_descriptor_fast(corpus / "T-0051-26.cuw")
check(fast_outer["format_type"] == 0x67, "fast CUW header path resolves format 0x67 without reading flash members")
check(fast_outer["validation"] == "header-and-first-member-only", "fast CUW path labels its bounded validation level")
check(fast_descriptor["Vehicle"]["ContactType"] == "P5-Unified", "fast CUW descriptor path resolves contact type")

outer, descriptor = gts_cli._cuw_descriptor(corpus / "T-0051-26.cuw")
check(outer["format_type"] == 0x67, "fully validated Camry CUW outer format remains 0x67")
check(outer["validation"] == "full-container", "full CUW path labels full-container validation")
check(descriptor["Vehicle"]["VehicleName"] == "CAMRY", "Camry CUW OEM vehicle name resolves")
check(descriptor["Vehicle"]["ContactType"] == "P5-Unified", "Camry CUW contact type resolves")
check(descriptor["Node01"]["DiagID"] == "0724", "Camry CUW diagnostic ID resolves")
check(
    gts_cli._new_cids(descriptor) == ["8A2810602100", "8A2910601100", "8A2A10602100"],
    "Camry CUW logical-block NewCIDs resolve",
)
check(
    gts_cli._target_calibrations(descriptor) == ["8A2810602000", "8A2910601000", "8A2A10602000"],
    "Camry CUW target calibrations resolve",
)

p5_route = [row for row in routes if row["contact_type"] == "P5-Unified"]
check(len(p5_route) == 1, "Camry P5-Unified contact type resolves one current route")
check(p5_route[0]["prepare_writer"] == "TCUWCanUnifiedPrepareWriter.dll", "Camry CUW resolves current Unified prepare writer")
check(p5_route[0]["flash_writer"] == "TCUWCanUnifiedFlashWriter.dll", "Camry CUW resolves current Unified flash writer")

kgp = gts_cli._resolve_pe(gts, cuwplus, "KgpDataCtrl.dll")
check(kgp.is_file(), "PE resolver finds current KgpDataCtrl.dll")
strings_in_kgp = gts_cli._binary_strings(kgp.read_bytes())
check(any("CDbDatamonitorP5Table" in value for value in strings_in_kgp), "PE string surface exposes current Data Monitor implementation class")

print("verified unified GTS+ DDB/CUW/PE query surface")
