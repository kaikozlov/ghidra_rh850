#!/usr/bin/env python3
"""Validate load-bearing Techstream artifact provenance and live hashes."""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
ROOT = REPO / "Techstream/unpacked/toyota/Toyota Diagnostics"
lock = json.loads((REPO / "techstream.lock.json").read_text(encoding="utf-8"))
artifacts = lock["artifacts"]
passed = failed = 0


def check(name: str, condition: bool, detail: str = "") -> None:
    global passed, failed
    passed += bool(condition)
    failed += not condition
    print(f"[{'PASS' if condition else 'FAIL'}] {name}" + (f" ({detail})" if detail else ""))


required_pe = {
    "IT3ACNK.dll", "IT3UtilityNK.dll", "IT3UtilityRevNK.dll", "IT3UtilityNeoNK.dll",
    "Techstream.exe", "KgpDataCtrl.dll", "DataCompress_DT.DLL",
    "CUWAccessRKS.dll", "CUWAccessRKSWrapper.dll", "Cuw.exe",
    "TCUWCalibrationFile.dll", "TCUWCanCommonPrepareWriter.dll",
    "TCUWCanCommonFlashWriter.dll", "TCUWCanReproStdPrepareWriter.dll",
    "TCUWCanReproStdFlashWriter.dll", "TCUWCanUnifiedPrepareWriter.dll",
    "TCUWCanUnifiedFlashWriter.dll", "TCUWCanUnifiedFlashWriterEachArea.dll",
    "TCUWCanSecurityVFORESTFlashWriter.dll", "TCUWP4CanVFORESTFlashWriter.dll",
    "TCUWP5CanSecurityPowerTrainPrepareWriter.dll",
    "CommandCommon.dll", "DS2ComNK.dll", "UtilityExNK2.dll", "UtilityEx2TY.dll",
    "TCUWControlCommPhase.dll", "TCUWParameterForVC.dll",
}

required_data = {
    "EPS_P4DK3.ddb", "EPS_CAN_P4DK.ddb", "Security_P4.ddb",
    "Toyota.ddb", "Toyota_EU.ddb", "Toyota_JP.ddb", "M_English.ddb",
    "EMPS_P5.ddb", "EMPS2_P5.ddb", "PCS2_P5.ddb",
}
required = required_pe | required_data

print("== committed lock schema ==")
check("all load-bearing artifacts are pinned", required <= set(artifacts),
      f"missing={sorted(required - set(artifacts))}")
for name in sorted(required):
    item = artifacts[name]
    check(f"{name}: relative path", isinstance(item.get("path"), str)
          and not Path(item["path"]).is_absolute())
    check(f"{name}: size and SHA-256", isinstance(item.get("size"), int)
          and item["size"] > 0 and len(item.get("sha256", "")) == 64)
    if name in required_pe:
        check(f"{name}: PE versions", bool(item.get("product_version"))
              and bool(item.get("file_version")))
    check(f"{name}: purpose and dependencies", bool(item.get("purpose"))
          and bool(item.get("claims_tests")))

if ROOT.is_dir():
    print("\n== live artifact parity ==")
    for name in sorted(required):
        item = artifacts[name]
        path = ROOT / item["path"]
        check(f"{name}: live path exists", path.is_file(), str(path))
        if path.is_file():
            data = path.read_bytes()
            check(f"{name}: live size", len(data) == item["size"])
            check(f"{name}: live SHA-256", hashlib.sha256(data).hexdigest() == item["sha256"])
else:
    print("\n[SKIP] external Techstream tree unavailable; committed lock schema still checked")

print(f"\nResults: {passed} passed, {failed} failed")
raise SystemExit(1 if failed else (0 if ROOT.is_dir() else 77))
