#!/usr/bin/env python3
"""Verify the Techstream ↔ Corolla 8965H1202000 steering correlation."""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
ART = REPO / "data/generated/corolla_8965H1202000_techstream_correlations.json"
EVID = REPO / "data/generated/corolla_8965H1202000_techstream_steering_decompiler_evidence.json"
TOOL = REPO / "tools/build_corolla_h_techstream_correlations.py"
RAW = REPO / "community/albinoelephant/raw-20260818/albinoelephant-corolla-2023.20260814-0023/dump_codeflash_00000000_00200000_20260814-025814.bin"
TECHROOT = REPO / "Techstream/unpacked/toyota/Toyota Diagnostics/Techstream"
passed = failed = 0


def check(name: str, cond: object, detail: str = "") -> None:
    global passed, failed
    ok = bool(cond)
    passed += int(ok); failed += int(not ok)
    suffix = f" ({detail})" if detail else ""
    print(f"[{'PASS' if ok else 'FAIL'}][raw_bytes] {name}{suffix}")


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


with tempfile.TemporaryDirectory() as td:
    out = Path(td) / "corolla-techstream.json"
    subprocess.run([sys.executable, str(TOOL), "--out", str(out)], cwd=REPO, check=True,
                   stdout=subprocess.DEVNULL)
    check("tracked Corolla Techstream report regenerates exactly", out.read_bytes() == ART.read_bytes())

d = json.loads(ART.read_text())
e = json.loads(EVID.read_text())
raw = RAW.read_bytes()

print("\n== source identity ==")
check("tracked raw Corolla dump is 2 MiB", len(raw) == 0x200000)
check("report binds raw Corolla dump", sha(raw) == d["sources"]["corolla_codeflash"]["sha256"])
for key, rel in (("na_emps_p5", "NA/DB/EMPS_P5.ddb"), ("na_emps2_p5", "NA/DB/EMPS2_P5.ddb")):
    src = TECHROOT / rel
    check(f"{rel} hash matches pinned semantics", sha(src.read_bytes()) == d["sources"][key]["sha256"])

print("\n== compact target-native evidence ==")
check("ten H functions support the Command Value Torque chain", e["function_count"] == 10)
for row in e["functions"]:
    start = int(row["entry"], 16); size = row["body_size"]
    check(f"raw body hash {row['entry']}", sha(raw[start:start+size]) == row["body_sha256"])

print("\n== recovered P5 data-ID layout ==")
for name in ("emps_p5", "emps2_p5"):
    x = d["data_id_layout_recovery"][name]
    check(f"{name} primary data-ID words resolve except sentinel",
          x["primary_nonzero_count"] == x["primary_resolves_in_type61_or_fffe"])
    check(f"{name} alternate data-ID words all resolve",
          x["alternate_nonzero_count"] == x["alternate_resolves_in_type61"])
check("P5 list host uses support-ID filtering", "CheckSupportPid" in d["data_id_layout_recovery"]["host_consumer"])

print("\n== Corolla vocabulary fit ==")
ov = d["ddb_overlap"]
check("H has 226 readable RDBI DIDs", ov["h_readable_did_count"] == 226)
check("EMPS_P5 overlaps 124 H DIDs", ov["emps_p5"]["h_type61_overlap_count"] == 124)
check("EMPS_P5 yields 137 H-supported named monitor rows", ov["emps_p5"]["h_supported_monitor_rows"] == 137)
check("EMPS2_P5 overlap is smaller", ov["emps2_p5"]["h_type61_overlap_count"] == 112)

print("\n== Command Value Torque exact join ==")
t = d["command_value_torque"]
check("monitor 402 is Command Value Torque in Nm",
      t["techstream"]["monitor_key"] == 402 and t["techstream"]["name"] == "Command Value Torque" and t["techstream"]["unit"] == "Nm")
check("monitor 402 primary/alternate IDs are 1C02/3C02",
      t["techstream"]["primary_data_id"] == "0x1C02" and t["techstream"]["alternate_data_id"] == "0x3C02")
check("H DID 1C02 is a live 2-byte callback", t["corolla_h_rdbi"]["callback"] == "0x000495A0" and t["corolla_h_rdbi"]["callback_classification"] == "direct_fixed" and t["corolla_h_rdbi"]["declared_length"] == 2)
check("H DID 1C02 formula is recovered", t["corolla_h_rdbi"]["formula_recovered"])
check("all target-native producer-chain relations are recovered", all(x["recovered"] for x in t["target_native_producer_chain"]))
check("active pipeline order is CD55A -> CD5DC -> CE928",
      t["target_native_producer_chain"][-1]["relation"].endswith("CD55A -> CD5DC -> CE928 in order"))

print("\n== angle-domain negative ==")
a = d["modern_angle_domain"]
check("target-angle monitor family is grouped under 1CEE/1CEF", a["primary_data_ids"] == ["0x1CEE", "0x1CEF"])
check("H supports none of the 2069..2076 target-angle family", not a["corolla_h_supports_any"] and all(not x["corolla_h_rdbi_supported"] for x in a["rows"]))

print("\n== interpretation boundary ==")
c = d["static_conclusion"]
check("exact H Command Value Torque DID join is asserted", c["command_value_torque_exact_did_join"])
check("live internal H producer pipeline is asserted", c["command_value_torque_live_internal_pipeline"])
check("external CAN-field equivalence remains false", c["external_can_field_equivalence"] is False)

print(f"\nResults: {passed} passed, {failed} failed")
raise SystemExit(1 if failed else 0)
