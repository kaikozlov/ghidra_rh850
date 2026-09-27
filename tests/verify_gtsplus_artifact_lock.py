#!/usr/bin/env python3
"""Validate tracked GTS+ provenance and the optional local source corpus."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
ROOT = REPO / "software/Techstream/gtsplus"
LOCK = REPO / "software/locks/gtsplus.json"

passed = failed = 0


def check(name: str, condition: object, detail: str = "") -> None:
    global passed, failed
    ok = bool(condition)
    passed += int(ok)
    failed += int(not ok)
    print(f"[{'PASS' if ok else 'FAIL'}] {name}" + (f" ({detail})" if detail else ""))


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


lock = json.loads(LOCK.read_text(encoding="utf-8"))
dist = lock["distribution"]
source = dist["source_archive"]

cuw = lock["cuwplus"]
artifacts = cuw["artifacts"]
expected = {
    "CUW.dll._",
    "TCUWCalibrationFile.dll._",
    "TCUWCanCommonPrepareWriter.dll._",
    "TCUWCanReproStdFlashWriter.dll._",
    "TCUWCanReproStdPrepareWriter.dll._",
    "TCUWP6CanReprostdFlashWriter.dll._",
    "unpack/CUW.unpack.dll",
    "unpack/TCUWCalibrationFile.unpack.dll",
    "unpack/TCUWCanCommonPrepareWriter.unpack.dll",
    "unpack/TCUWCanReproStdFlashWriter.unpack.dll",
    "unpack/TCUWCanReproStdPrepareWriter.unpack.dll",
    "unpack/TCUWP6CanReprostdFlashWriter.unpack.dll",
    "Ini/P5-Unified.ini",
    "Ini/P5-Unified03.ini",
    "Ini/P5-Unified04.ini",
    "Ini/P5-Unified10.ini",
    "Ini/RKS.ini",
}
check("complete pinned CUWPlus analysis set", set(artifacts) == expected)

if not ROOT.is_dir():
    print("\n[SKIP] external GTS+ corpus unavailable; no live identity checks ran")
    raise SystemExit(77)

print("\n== live artifact parity ==")
archive = ROOT / source["path"]
check("source archive exists", archive.is_file(), str(archive))
if archive.is_file():
    check("source archive size", archive.stat().st_size == source["size"])
    check("source archive SHA-256", sha256(archive) == source["sha256"])
for rel, item in sorted(artifacts.items()):
    path = ROOT / cuw["root"] / rel
    check(f"{rel}: live path exists", path.is_file(), str(path))
    if path.is_file():
        check(f"{rel}: live size", path.stat().st_size == item["size"])
        check(f"{rel}: live SHA-256", sha256(path) == item["sha256"])

print(f"\nResults: {passed} passed, {failed} failed")
raise SystemExit(1 if failed else 0)
