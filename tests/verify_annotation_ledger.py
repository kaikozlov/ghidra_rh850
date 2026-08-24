#!/usr/bin/env python3
"""Verify declarative Ghidra annotation recording and rebuild integration."""
from __future__ import annotations

import json
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools/annotations"
LEDGER = ROOT / "data/annotations/annotation_ledger.jsonl"
APPLIER = ROOT / "ghidra/scripts/annotate/ApplyAnnotationLedger.java"
REBUILD = ROOT / "tools/rebuild_project.sh"
ANNOTATE_PAYLOAD = ROOT / "ghidra/scripts/annotate/AnnotatePayloadGate.java"

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


print("== tracked annotation ledger ==")
probe = run("validate")
check("tracked ledger validates", probe.returncode == 0 and "valid: 1 records" in probe.stdout, probe.stderr or probe.stdout)
path_probe = run("path")
check("tool and rebuild share the tracked ledger path", path_probe.returncode == 0 and Path(path_probe.stdout.strip()) == LEDGER, path_probe.stdout)
records = [json.loads(line) for line in LEDGER.read_text().splitlines()]
check(
    "migrated payload-gate annotation is ledger-owned",
    records == [{
        "op": "function",
        "address": "0x000032d2",
        "name": "boot_memory_range_check_access",
        "comment_type": "plate",
        "comment": "Validate address/length and operation bit against boot_memory_access_table; return memory class.",
    }],
)
check("migrated annotation is removed from imperative Java", "fn(0x32D2L" not in ANNOTATE_PAYLOAD.read_text())

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
    check("exact duplicate add is idempotent", duplicate.returncode == 0 and ledger.read_bytes() == before and "already present" in duplicate.stdout, duplicate.stderr)
    conflict = run(*base, "add", "label", "0x200", "not_data")
    check("symbol-kind conflict fails before rewrite", conflict.returncode != 0 and ledger.read_bytes() == before and "conflict" in conflict.stderr, conflict.stderr)
    same_name_other_address = run(*base, "add", "label", "0x300", "example_function")
    check(
        "duplicate desired symbol name fails before rewrite",
        same_name_other_address.returncode != 0
        and ledger.read_bytes() == before
        and "symbol name" in same_name_other_address.stderr,
        same_name_other_address.stderr,
    )
    invalid = run(*base, "add", "function", "not-an-address", "bad")
    check("invalid address fails before rewrite", invalid.returncode != 0 and ledger.read_bytes() == before and "address is not" in invalid.stderr, invalid.stderr)
    invalid_list = run(*base, "list", "--address", "not-an-address")
    check("invalid list address is a clean user error", invalid_list.returncode == 2 and "address is not" in invalid_list.stderr, invalid_list.stderr)
    missing = run("--ledger", str(Path(td) / "missing.jsonl"), "validate")
    check("missing rebuild input fails closed", missing.returncode == 2 and "does not exist" in missing.stderr, missing.stderr)
    validate = run(*base, "validate")
    check("temporary ledger round-trips through validator", validate.returncode == 0, validate.stderr)
    removed = run(*base, "remove", "comment", "0x204", "--comment-type", "eol")
    check("record removal rewrites a valid canonical ledger", removed.returncode == 0 and run(*base, "validate").returncode == 0 and "0x00000204" not in ledger.read_text(), removed.stderr)

print("\n== canonical rebuild integration ==")
rebuild = REBUILD.read_text()
check(
    "rebuild validates tracked ledger before stage 1",
    '"$ROOT/tools/annotations" --ledger "$ANNOTATION_LEDGER" validate' in rebuild
    and rebuild.index('tools/annotations') < rebuild.index('[1/4] Import mapped images without analysis'),
)
check("rebuild uses the canonical ledger path", 'ANNOTATION_LEDGER="$ROOT/data/annotations/annotation_ledger.jsonl"' in rebuild)
check(
    "ledger applier runs exactly once after existing stage-4 annotations",
    rebuild.count("-postScript ApplyAnnotationLedger.java") == 1
    and rebuild.index("-postScript ApplyCallingConventions.java") < rebuild.index("-postScript ApplyAnnotationLedger.java"),
)
applier = APPLIER.read_text()
check(
    "applier preflights the complete ledger before mutation",
    "Pass 1: parse and validate the COMPLETE plan" in applier
    and "preflightRecord(record, ledger, line, plannedNames)" in applier
    and applier.index("preflightRecord(record, ledger, line, plannedNames)")
        < applier.index("Pass 2: all deterministic failures are behind us"),
)
check("applier fails closed on missing functions", "no function at " in applier and "IllegalStateException" in applier)
check(
    "applier rejects unmapped/data-label-in-code targets defensively",
    "getMemory().contains(address)" in applier
    and "getFunctionContaining(address)" in applier,
)
check("applier supports only the three mechanical operations", all(f'case "{op}"' in applier for op in ("function", "label", "comment")))
tool_source = TOOL.read_text()
check(
    "apply command delegates to the CLI's teardown-backed durable script path",
    '[runner, "script", "run", "--save", script' in tool_source,
)

print(f"\nResults: {passed} passed, {failed} failed")
raise SystemExit(1 if failed else 0)
