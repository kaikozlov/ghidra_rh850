#!/usr/bin/env python3
"""Verify the deterministic Camry 0x08A signer-continuity artifact."""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
ART = REPO / "data/generated/camry_2026_08a_signer_continuity.json"
BUILD = REPO / "tools/analyze_camry_2026_08a_signer_continuity.py"

passed = failed = 0


def check(name, condition, detail=""):
    global passed, failed
    ok = bool(condition)
    passed += ok
    failed += not ok
    print(f"[{'PASS' if ok else 'FAIL'}] {name}" + (f" ({detail})" if detail else ""))


art = json.loads(ART.read_text())

print("== deterministic regeneration ==")
with tempfile.TemporaryDirectory() as td:
    out = Path(td) / ART.name
    proc = subprocess.run([sys.executable, str(BUILD), "--out", str(out)],
                          capture_output=True, text=True, check=False)
    check("generator exits cleanly", proc.returncode == 0,
          proc.stderr[-200:] if proc.returncode else "")
    check("artifact regenerates byte-identically",
          proc.returncode == 0 and out.read_bytes() == ART.read_bytes())
check("schema is v1", art["schema"] == "camry-2026-08a-signer-continuity-v1")
check("production output remains unauthorized", art["production_output_authorized"] is False)

print("\n== zero-request signing continuity (stationary READY, B21=0) ==")
ready = art["stationary_ready_detail"]
check("stationary capture is READY-regime", ready["stationary"] is True)
check("B21 census is exactly zero-request", ready["b21_census"] == {"0": 2475},
      f"census={ready['b21_census']}")
check("0x08A streams at zero request", ready["a8_frames"] == 2475)
check("0x00F streams with advancing epoch",
      ready["f00f_frames"] == 619 and ready["f00f_reset_span"][1] > ready["f00f_reset_span"][0],
      f"reset span={ready['f00f_reset_span']}")
fv = ready["fv4_reset_low2_agreement"]
check("FV4 reset-low2 tracks live 0x00F epoch at >= 0.98",
      fv["total"] == 2475 and fv["fraction"] >= 0.98,
      f"{fv['agree']}/{fv['total']} = {fv['fraction']:.4f}")
check("B26 advances +1 mod 64 at >= 0.99",
      ready["b26_plus1_mod64_fraction"] >= 0.99,
      f"{ready['b26_plus1_mod64_fraction']:.4f}")
check("MAC28 stays frame-unique at zero request",
      ready["mac28_last4_unique_fraction"] >= 0.98,
      f"{ready['mac28_last4_unique_fraction']:.4f}")
check("all 16 FV4 phases cycle", len(ready["fv4_census"]) == 16)

print("\n== active-request contrast (relay-correct drives, B21=11/18 present) ==")
expected_b21 = {
    "drive_a": {"0": 18868, "11": 646, "18": 1101},
    "drive_b": {"0": 20914, "11": 2288, "18": 797},
}
for name, exp in expected_b21.items():
    d = art["active_request_contrast"][name]
    check(f"{name} B21 census exact", d["b21_census"] == {k: str(v) for k, v in
          {kk: vv for kk, vv in exp.items()}.items()} or
          d["b21_census"] == {str(k): v for k, v in exp.items()},
          f"census={d['b21_census']}")
    check(f"{name} B26 +1 cadence holds across request regimes",
          d["b26_plus1_mod64_fraction"] >= 0.99,
          f"{d['b26_plus1_mod64_fraction']:.4f}")
    check(f"{name} MAC28 stays frame-unique",
          d["mac28_last4_unique_fraction"] >= 0.98,
          f"{d['mac28_last4_unique_fraction']:.4f}")

print("\n== interpretation boundaries ==")
res = art["zero_request_result"]
check("signing_continues is true at zero request", res["signing_continues"] is True)
check("continuity interpretation is recorded",
      "always-on chassis engine" in res["interpretation"])
check("boundary keeps signer identity open",
      "does not identify the signer" in res["boundary"])
ident = art["signer_identity"]
check("identity verdict is hypothesis-graded",
      ident["grade"] == "hypothesis")
check("brake-family/CGW hypothesis names the candidate set",
      "brake family" in ident["verdict"] and "Central Gateway" in ident["verdict"])
check("decisive evidence names producer firmware",
      "producer firmware" in ident["decisive_evidence"])
check("FRC pre-authentication branch is not overclaimed",
      "not excluded by signing continuity alone" in ident["frc_branch_disposition"])
check("grades separate observed continuity from hypothesis identity",
      ident["grades"]["zero_request_signing_continuity"] == "observed"
      and ident["grades"]["signer_identity_brake_family_or_cgw"] == "hypothesis"
      and ident["grades"]["frc_excluded_as_key_holder"] == "hypothesis")

print(f"\n{passed} passed, {failed} failed")
sys.exit(1 if failed else 0)
