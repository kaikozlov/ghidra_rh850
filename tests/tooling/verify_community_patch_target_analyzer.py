#!/usr/bin/env python3
"""Verify the pre-acquisition community SecOC patch-target analyzer."""

from __future__ import annotations

import json
import subprocess
import sys

from tools import REPO_ROOT
REPO = REPO_ROOT

from tools.security.analyze_secoc_patch_target import (
    EGG,
    KNOWN_SIENNA_EGG_VA,
    KNOWN_SIENNA_SECOC_WORKER,
    analyze,
    find_all,
)

passed = failed = 0


def check(name: str, condition: object, detail: str = "") -> None:
    global passed, failed
    ok = bool(condition)
    passed += int(ok)
    failed += int(not ok)
    suffix = f" ({detail})" if detail else ""
    print(f"[{'PASS' if ok else 'FAIL'}] {name}{suffix}")


cf_path = REPO / "firmware" / "RH850_P1M-E_CodeFlash.bin"
cf = cf_path.read_bytes()

print("== raw candidate location contract ==")
check("Sienna image contains exactly one raw egg", find_all(cf, EGG) == [KNOWN_SIENNA_EGG_VA])

result = analyze(cf_path)
check("known Sienna image is recognized by full SHA", result.get("known_image", {}).get("name") == "8965B4512000")
check("known Sienna candidate VA is 0x3485A", result["matches"][0]["virtual_address"] == 0x3485A)
check("known Sienna actual SecOC worker remains 0x8E4BA", result["known_image"]["actual_secoc_rx_verify_worker"] == KNOWN_SIENNA_SECOC_WORKER == 0x8E4BA)
check("raw output contains no caller attribution", all("caller" not in key.lower() for key in result["matches"][0]))

print("\n== multiple/zero-match behavior ==")
blob = b"\x00" * 7 + EGG + b"\x11" * 5 + EGG + b"\x22" * 3
check("raw finder retains every occurrence", find_all(blob, EGG) == [7, 20])
check("raw finder returns empty for no occurrence", find_all(b"\x00" * 128, EGG) == [])

print("\n== committed reference artifact ==")
artifact_path = REPO / "data" / "generated" / "community_patch_target_4512000.json"
committed = json.loads(artifact_path.read_text(encoding="utf-8"))
check("reference artifact does not emit raw secret material", "key" not in json.dumps(committed).lower())

print("\n== companion Ghidra script contract ==")
script = (REPO / "ghidra" / "scripts" / "investigate" / "AnalyzeCommunityPatchTarget.java").read_text(encoding="utf-8")
check("Ghidra script contains no save call", "saveProgram" not in script and ".save(" not in script)
check("Ghidra script contains no rename mutation", "setName(" not in script and "createLabel(" not in script)

print("\n== CLI ==")
run = subprocess.run(
    [sys.executable, str(REPO / "tools" / "security" / "analyze_secoc_patch_target.py"), str(cf_path)],
    cwd=REPO,
    capture_output=True,
    text=True,
    check=False,
)
check("CLI exits successfully", run.returncode == 0, run.stderr.strip())
cli = json.loads(run.stdout)
check("CLI reports one Sienna candidate", cli["egg_match_count"] == 1)
check("CLI reports immediate-return patch semantics", "r10=1" in cli["patch_semantics"])

print(f"\n== RESULT: {passed} passed, {failed} failed ==")
if failed:
    raise SystemExit(1)
