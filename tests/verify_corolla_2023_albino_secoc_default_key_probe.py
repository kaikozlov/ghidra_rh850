#!/usr/bin/env python3
"""Verify the Albino Corolla obvious/default/static SecOC-key falsification."""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
ART_PATH = REPO / "data/generated/corolla_2023_albino_secoc_default_key_probe.json"
ART = json.loads(ART_PATH.read_text())
LOCK = json.loads((REPO / "external-references.lock.json").read_text())
passed = failed = 0


def check(name: str, condition: object, detail: str = "") -> None:
    global passed, failed
    ok = bool(condition)
    passed += int(ok); failed += int(not ok)
    print(f"[{'PASS' if ok else 'FAIL'}] {name}" + (f" ({detail})" if detail else ""))


print("== source/oracle identity ==")
check("schema pinned", ART["schema"] == "corolla-2023-albino-secoc-default-key-probe-v1")
pub = ART["oracles"]["public_route"]
loc = ART["oracles"]["local_tskm"]
check("public route has 588 sync samples at trip 0xCE9", pub["sync_samples"] == 588 and pub["trip_values"] == [0xCE9])
check("first public 00F decodes trip/reset/MAC28 exactly", pub["first_sync_decoded"] == {"trip": 0xCE9, "reset": 0xE0, "authenticator28": 0xB3E61D5})
check("public route has 2496 usable 116 and 59 usable 24D protected samples",
      ART["legacy_public_example_key4"]["public_route_verification"]["protected"] == {"0x116": {"matches": 0, "total": 2496}, "0x24D": {"matches": 0, "total": 59}})
check("local TSKM has 1232 sync samples at trip 0xD0D", loc["sync_samples"] == 1232 and loc["trip_values"] == [0xD0D] and loc["protected_samples"] == 0)
check("first local 00F decodes trip/reset/MAC28 exactly", loc["first_sync_decoded"] == {"trip": 0xD0D, "reset": 0x74C, "authenticator28": 0x286D644})
check("route/F181 boundary explicit", "no carFw/F181" in pub["identity_boundary"])
check("TSKM/dump runtime-epoch boundary explicit", "separate jobs/runtime epochs" in loc["identity_boundary"])

print("\n== pinned public legacy KEY_4 falsification ==")
legacy = ART["legacy_public_example_key4"]
check("legacy source commit pinned", legacy["source_commit"] == LOCK["repositories"]["icanhack_secoc"]["commit"] == "4ce19cc31ff560b697bcd59cc3db55711f50b7b3")
readme_rows = [r for r in LOCK["artifacts"] if r.get("repository") == "icanhack_secoc" and r.get("path") == "README.md"]
check("legacy README hash is provenance-locked", len(readme_rows) == 1 and readme_rows[0]["sha256"] == legacy["source_readme_sha256"] == "3f40cddb47ff954cb4f2c30b2c2ea6764ae62f32d111a63ba1c4f05b3c08cb60")
check("public KEY_4 value represented by hash only in artifact", legacy["key_sha256"] == "b78f0b127aead747322d13f7923e233edc42a29adcf5ad004feb442c32275f0c")
check("legacy KEY_4 authenticates zero public sync frames", legacy["public_route_verification"]["sync"] == {"matches": 0, "total": 588})
check("legacy KEY_4 authenticates zero local sync frames", legacy["local_tskm_verification"]["sync"] == {"matches": 0, "total": 1232})

print("\n== low-complexity/default key family ==")
low = ART["low_complexity_key_family"]
check("all 65536 repeated-u16 keys tested", low["candidate_count"] == 65536)
check("family includes zero, FF, and every repeated-byte key", low["includes_all_zero"] and low["includes_all_ff"] and low["includes_all_repeated_single_byte_keys"])
check("no periodic key authenticates first public sync", low["public_route_first_sync_hits"] == [])
check("no periodic key authenticates first local sync", low["local_tskm_first_sync_hits"] == [])

print("\n== retained CPU-visible raw-key census ==")
scan = ART["retained_cpu_visible_raw_key_scan"]
check("711279 unique 16-byte values tested", scan["unique_16byte_windows_tested"] == 711279)
check("15 retained memory captures/classes represented", len(scan["files"]) == 15)
check("all five DataFlash host reads bounded to real first 32 KiB", sum(r["source_size"] == 0x10000 and r["considered_size"] == 0x8000 for r in scan["files"] if "dump_dataflash_" in r["path"]) == 5)
check("no retained raw value authenticates first public sync", scan["public_route_first_sync_hits"] == [])
check("no retained raw value authenticates first local sync", scan["local_tskm_first_sync_hits"] == [])

print("\n== interpretation boundaries ==")
con = ART["conclusions"]
check("classic SecOC observation remains affirmative", con["classic_secoc_is_observed"] is True)
check("legacy example key specifically disproved", con["legacy_public_example_key4_disproved_for_retained_albino_oracles"] is True)
check("periodic dumb-key family specifically disproved", con["two_byte_periodic_default_key_family_disproved"] is True)
check("raw-corpus negative is epoch-qualified", con["raw_static_key_absent_from_retained_cpu_visible_corpus_under_oracle_epoch_assumptions"] is True)
check("preprovisioning/automatic provisioning/ICU slot remain plausible", all(any(term in x for x in con["still_plausible"]) for term in ("pre-provisioned", "automatic provisioning", "ICU-S slot-4")))
check("service replacement boundary explicit", "does not establish absence of SecOC" in con["service_boundary"])

print("\n== generator drift ==")
with tempfile.TemporaryDirectory(prefix="albino-secoc-default-") as td:
    out = Path(td) / "out.json"
    proc = subprocess.run([sys.executable, str(REPO / "tools/build_corolla_2023_albino_secoc_default_key_probe.py"), "--output", str(out)], cwd=REPO, capture_output=True, text=True)
    check("generator succeeds", proc.returncode == 0, proc.stderr.strip()[:160])
    if proc.returncode == 0:
        check("tracked artifact is generator-drift free", json.loads(out.read_text()) == ART)

print(f"\n== RESULT: {passed} passed, {failed} failed ==")
raise SystemExit(1 if failed else 0)
