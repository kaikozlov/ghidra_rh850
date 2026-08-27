#!/usr/bin/env python3
"""Validate the tracked identity manifest for the local Toyota CUW corpus."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
ROOT = REPO / "software/Techstream/cuw"
LOCK = REPO / "software/locks/toyota-cuw-corpus.json"

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
check("schema version", lock.get("schema_version") == 1)
corpus = lock["corpus"]
check("canonical root", corpus.get("root") == "software/Techstream/cuw")
items = lock["artifacts"]
check("manifest count", corpus.get("artifact_count") == len(items) == 26)
names = [item.get("filename") for item in items]
check(
    "filenames sorted and unique",
    names == sorted(names) and len(set(names)) == len(names),
)
for item in items:
    check(
        f"{item.get('filename')}: identity fields",
        item.get("size", 0) > 0 and len(item.get("sha256", "")) == 64,
    )

if not ROOT.is_dir():
    print(
        "\n[SKIP] external Toyota CUW corpus unavailable; committed lock schema still checked"
    )
    raise SystemExit(77 if not failed else 1)

print("\n== live artifact parity ==")
live = sorted(p.name for p in ROOT.glob("*.cuw"))
check("live corpus has exact manifest membership", live == names)
for item in items:
    path = ROOT / item["filename"]
    check(f"{item['filename']}: live path exists", path.is_file(), str(path))
    if path.is_file():
        check(f"{item['filename']}: live size", path.stat().st_size == item["size"])
        check(f"{item['filename']}: live SHA-256", sha256(path) == item["sha256"])

print(f"\nResults: {passed} passed, {failed} failed")
raise SystemExit(1 if failed else 0)
