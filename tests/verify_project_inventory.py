#!/usr/bin/env python3
"""Behavioral tests for canonical normalized Ghidra JSONL inventories."""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
TOOL = REPO / "tools/project_inventory.py"

passed = 0
failed = 0


def check(name: str, condition: bool, detail: str = "") -> None:
    global passed, failed
    if condition:
        passed += 1
        print(f"[PASS] {name}")
    else:
        failed += 1
        print(f"[FAIL] {name}{': ' + detail if detail else ''}")


def run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(TOOL), *args],
        cwd=REPO,
        text=True,
        capture_output=True,
    )


def write_inventory(path: Path, function_name: str = "entry") -> None:
    address = {"space": "ram", "offset": "00000100"}
    records = [
        {
            "record": "meta",
            "schema_version": 1,
            "ghidra_version": "12.1.3",
            "program_name": "firmware.bin",
            "executable_sha256": "a" * 64,
            "executable_format": "Raw Binary",
            "language_id": "v850e3:LE:32:default",
            "compiler_spec_id": "default",
        },
        {
            "record": "memory_block",
            "name": "CodeFlash",
            "start": address,
            "end": {"space": "ram", "offset": "000001ff"},
            "size": 256,
            "block_type": "DEFAULT",
            "initialized": True,
            "overlay": False,
            "loaded": True,
            "read": True,
            "write": False,
            "execute": True,
            "volatile": False,
            "artificial": False,
            "source_infos": [{
                "destination_min": address,
                "destination_max": {"space": "ram", "offset": "000001ff"},
                "length": 256,
                "mapped_range": None,
                "byte_mapping": None,
                "file_bytes": None,
            }],
        },
        {
            "record": "function",
            "entry": address,
            "body_ranges": [{"min": address, "max": address}],
            "body_address_count": 1,
            "is_thunk": False,
            "thunk_target": {"space": "NO_ADDRESS", "offset": None},
            "is_inline": False,
            "is_external": False,
            "user_name": function_name,
            "name_source": "USER_DEFINED",
            "signature_source": "DEFAULT",
            "calling_convention": "__stdcall",
            "return": {
                "source": "DEFAULT",
                "formal_type": {"path": "/undefined", "length": 1},
                "data_type": {"path": "/undefined", "length": 1},
                "storage": "<UNASSIGNED>",
            },
            "parameters": [],
            "varargs": False,
            "no_return": False,
            "custom_storage": False,
            "stack_purge_size": -1,
        },
        {
            "record": "user_symbol",
            "address": address,
            "symbol_type": "Function",
            "qualified_name": function_name,
            "primary": True,
        },
        {"record": "listing_comment", "address": address, "comment_type": "PLATE", "text": "comment"},
        {"record": "function_comment", "entry": address, "comment_type": "regular", "text": "function comment"},
        {"record": "bookmark", "address": address, "type": "Analysis", "category": "test", "comment": "bookmark"},
        {
            "record": "totals",
            "functions": 1,
            "instructions": 1,
            "symbols": 1,
            "memory_blocks": 1,
            "body_ranges": 1,
            "body_addresses": 1,
            "user_function_names": 1,
            "user_symbols": 1,
            "listing_comments": 1,
            "function_comments": 1,
            "bookmarks": 1,
            "name_sources": {"USER_DEFINED": 1},
            "calling_conventions": {"__stdcall": 1},
            "signature_sources": {"DEFAULT": 1},
        },
    ]
    path.write_text("".join(json.dumps(row, separators=(",", ":"), ensure_ascii=False) + "\n" for row in records))


print("== canonical JSONL project inventory ==")
with tempfile.TemporaryDirectory() as td:
    root = Path(td)
    baseline = root / "baseline.jsonl"
    current = root / "current.jsonl"
    second = root / "second.jsonl"
    write_inventory(baseline)
    write_inventory(current)
    write_inventory(second)

    result = run("validate", str(baseline))
    check("valid canonical inventory passes", result.returncode == 0, result.stderr)
    result = run("compare", str(baseline), str(second))
    check("identical inventories compare equal", result.returncode == 0, result.stderr)

    result = run("compare", str(baseline), str(baseline))
    check("parity comparison requires distinct artifacts", result.returncode != 0)

    write_inventory(current, "replacement")
    result = run("compare", str(baseline), str(current))
    check(
        "identity substitution fails despite equal totals",
        result.returncode != 0 and "normalized project inventory mismatch" in result.stderr,
        result.stderr,
    )
    check("mismatch emits unified diff", "baseline/" in result.stdout and "current/" in result.stdout)

    destination = root / "tracked.jsonl"
    result = run("update", str(baseline), str(second), str(destination))
    check("two matching rebuilds permit update", result.returncode == 0, result.stderr)
    check(
        "update copies exact bytes",
        destination.is_file() and destination.read_bytes() == baseline.read_bytes(),
    )

    before = destination.read_bytes() if destination.is_file() else b""
    result = run("update", str(baseline), str(current), str(destination))
    check("disagreeing rebuilds block update", result.returncode != 0)
    check(
        "failed update preserves baseline",
        destination.is_file() and destination.read_bytes() == before,
    )

    polluted = [json.loads(line) for line in baseline.read_text().splitlines()]
    polluted[0]["project_path"] = "/tmp/nondeterministic"
    bad = root / "bad.jsonl"
    bad.write_text("".join(json.dumps(row, separators=(",", ":")) + "\n" for row in polluted))
    result = run("validate", str(bad))
    check("nondeterministic meta fields fail closed", result.returncode != 0)

    inconsistent = [json.loads(line) for line in baseline.read_text().splitlines()]
    inconsistent[-1]["memory_blocks"] = 2
    bad.write_text("".join(json.dumps(row, separators=(",", ":")) + "\n" for row in inconsistent))
    result = run("validate", str(bad))
    check("inconsistent totals fail validation", result.returncode != 0)

    wrong_total_type = [json.loads(line) for line in baseline.read_text().splitlines()]
    wrong_total_type[-1]["instructions"] = str(wrong_total_type[-1]["instructions"])
    bad.write_text("".join(json.dumps(row, separators=(",", ":")) + "\n" for row in wrong_total_type))
    result = run("validate", str(bad))
    check("totals require nonnegative integer counts", result.returncode != 0)

    wrong_boolean = [json.loads(line) for line in baseline.read_text().splitlines()]
    wrong_boolean[1]["read"] = "true"
    bad.write_text("".join(json.dumps(row, separators=(",", ":")) + "\n" for row in wrong_boolean))
    result = run("validate", str(bad))
    check("boolean fields reject string lookalikes", result.returncode != 0)

    wrong_nested_type = [json.loads(line) for line in baseline.read_text().splitlines()]
    wrong_nested_type[2]["return"]["formal_type"]["length"] = "1"
    bad.write_text("".join(json.dumps(row, separators=(",", ":")) + "\n" for row in wrong_nested_type))
    result = run("validate", str(bad))
    check("nested schema values enforce scalar types", result.returncode != 0)

    duplicate = [json.loads(line) for line in baseline.read_text().splitlines()]
    duplicate.insert(-1, dict(duplicate[-2]))
    duplicate[-1]["bookmarks"] = 2
    bad.write_text("".join(json.dumps(row, separators=(",", ":")) + "\n" for row in duplicate))
    result = run("validate", str(bad))
    check("duplicate semantic identities are rejected", result.returncode != 0)

    reordered_keys = [json.loads(line) for line in baseline.read_text().splitlines()]
    reordered_keys[2] = dict(reversed(list(reordered_keys[2].items())))
    bad.write_text("".join(json.dumps(row, separators=(",", ":")) + "\n" for row in reordered_keys))
    result = run("validate", str(bad))
    check("record key order is canonical", result.returncode != 0)

    reordered_nested = [json.loads(line) for line in baseline.read_text().splitlines()]
    reordered_nested[1]["start"] = {
        "offset": reordered_nested[1]["start"]["offset"],
        "space": reordered_nested[1]["start"]["space"],
    }
    bad.write_text("".join(json.dumps(row, separators=(",", ":")) + "\n" for row in reordered_nested))
    result = run("validate", str(bad))
    check("nested key order is canonical", result.returncode != 0)

    short_offset = [json.loads(line) for line in baseline.read_text().splitlines()]
    short_offset[1]["start"]["offset"] = "0"
    bad.write_text("".join(json.dumps(row, separators=(",", ":")) + "\n" for row in short_offset))
    result = run("validate", str(bad))
    check("addresses require fixed-width offsets", result.returncode != 0)

    body_lie = [json.loads(line) for line in baseline.read_text().splitlines()]
    body_lie[2]["body_address_count"] += 1
    body_lie[-1]["body_addresses"] += 1
    bad.write_text("".join(json.dumps(row, separators=(",", ":")) + "\n" for row in body_lie))
    result = run("validate", str(bad))
    check("function body counts are derived from ranges", result.returncode != 0)

    name_source_lie = [json.loads(line) for line in baseline.read_text().splitlines()]
    name_source_lie[2]["name_source"] = "DEFAULT"
    name_source_lie[-1]["name_sources"] = {"DEFAULT": 1}
    bad.write_text("".join(json.dumps(row, separators=(",", ":")) + "\n" for row in name_source_lie))
    result = run("validate", str(bad))
    check("user function names require USER_DEFINED provenance", result.returncode != 0)

    memory_size_lie = [json.loads(line) for line in baseline.read_text().splitlines()]
    memory_size_lie[1]["size"] += 1
    bad.write_text("".join(json.dumps(row, separators=(",", ":")) + "\n" for row in memory_size_lie))
    result = run("validate", str(bad))
    check("memory block size is derived from its range", result.returncode != 0)

    out_of_order = [json.loads(line) for line in baseline.read_text().splitlines()]
    second_bookmark = dict(out_of_order[-2])
    second_bookmark["address"] = {"space": "ram", "offset": "00000000"}
    out_of_order.insert(-1, second_bookmark)
    out_of_order[-1]["bookmarks"] = 2
    bad.write_text("".join(json.dumps(row, separators=(",", ":")) + "\n" for row in out_of_order))
    result = run("validate", str(bad))
    check("semantic record ordering is enforced", result.returncode != 0)

    result = run("update", str(baseline), str(destination))
    check("single-source baseline update is impossible", result.returncode != 0)

    result = run("update", str(baseline), str(baseline), str(destination))
    check("same rebuild cannot be supplied twice", result.returncode != 0)

    hardlink = root / "hardlink.jsonl"
    os.link(baseline, hardlink)
    result = run("compare", str(baseline), str(hardlink))
    check("parity comparison rejects hard-linked aliases", result.returncode != 0)
    result = run("update", str(baseline), str(hardlink), str(destination))
    check("hard-linked rebuild inputs are not independent", result.returncode != 0)

    baseline_before = baseline.read_bytes()
    result = run("update", str(baseline), str(second), str(baseline))
    check("baseline cannot double as rebuild input", result.returncode != 0)
    check("aliased update leaves baseline unchanged", baseline.read_bytes() == baseline_before)

print()
if failed:
    print(f"FAILED: {failed} check(s)")
    raise SystemExit(1)
print(f"All {passed} checks passed.")