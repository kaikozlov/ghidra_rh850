#!/usr/bin/env python3
"""Verify annotation recording, normalization, and atomic conflict rejection."""
from __future__ import annotations

import json
import subprocess
import tempfile
from pathlib import Path

from tools import REPO_ROOT
ROOT = REPO_ROOT
TOOL = ROOT / "tools/annotations"

passed = 0
failed = 0


def check(name: str, condition: bool, detail: str = "") -> None:
    global passed, failed
    if condition:
        passed += 1
        print(f"[PASS] {name}")
    else:
        failed += 1
        print(f"[FAIL] {name}: {detail}")


def run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run([str(TOOL), *args], cwd=ROOT, capture_output=True, text=True)


print("\n== recording ergonomics and fail-closed conflicts ==")
with tempfile.TemporaryDirectory() as td:
    ledger = Path(td) / "annotations.jsonl"
    base = ("--ledger", str(ledger))
    # Intentionally add the higher address first: the writer must sort before
    # validating, rather than making insertion order part of the API.
    first = run(*base, "add", "function", "0X200", "example_function", "--comment", "example")
    second = run(*base, "add", "label", "0x100", "example_data")
    third = run(*base, "add", "comment", "0x204", "site", "--comment-type", "eol")
    check("function/label/comment adds succeed", all(p.returncode == 0 for p in (first, second, third)), first.stderr + second.stderr + third.stderr)
    parsed = [json.loads(line) for line in ledger.read_text().splitlines()]
    check("records are normalized and address-sorted", [r["address"] for r in parsed] == ["0x00000100", "0x00000200", "0x00000204"], str(parsed))
    check("no-comment symbol add does not invent comment_type", "comment_type" not in parsed[0], str(parsed[0]))

    before = ledger.read_bytes()
    duplicate = run(*base, "add", "function", "0x200", "example_function", "--comment", "example")
    check("exact duplicate add is idempotent", duplicate.returncode == 0 and ledger.read_bytes() == before, duplicate.stderr)
    conflict = run(*base, "add", "label", "0x200", "not_data")
    check("symbol-kind conflict fails before rewrite", conflict.returncode != 0 and ledger.read_bytes() == before, conflict.stderr)
    same_name_other_address = run(*base, "add", "label", "0x300", "example_function")
    check(
        "duplicate desired symbol name fails before rewrite",
        same_name_other_address.returncode != 0
        and ledger.read_bytes() == before,
        same_name_other_address.stderr,
    )
    invalid = run(*base, "add", "function", "not-an-address", "bad")
    check("invalid address fails before rewrite", invalid.returncode != 0 and ledger.read_bytes() == before, invalid.stderr)
    invalid_list = run(*base, "list", "--address", "not-an-address")
    check("invalid list address is a clean user error", invalid_list.returncode == 2, invalid_list.stderr)
    missing = run("--ledger", str(Path(td) / "missing.jsonl"), "validate")
    check("missing rebuild input fails closed", missing.returncode == 2, missing.stderr)
    validate = run(*base, "validate")
    check("temporary ledger round-trips through validator", validate.returncode == 0, validate.stderr)
    removed = run(*base, "remove", "comment", "0x204", "--comment-type", "eol")
    check("record removal rewrites a valid canonical ledger", removed.returncode == 0 and run(*base, "validate").returncode == 0 and "0x00000204" not in ledger.read_text(), removed.stderr)

print(f"\nResults: {passed} passed, {failed} failed")
raise SystemExit(1 if failed else 0)
