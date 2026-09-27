#!/usr/bin/env python3
"""Verify corpus coverage, function identities, and pseudocode lookup."""
from __future__ import annotations

import hashlib
import json
import subprocess
import tempfile
from pathlib import Path

from tools import REPO_ROOT
REPO = REPO_ROOT
CORPUS = REPO / "data/generated/decompilations.jsonl"
INVENTORY = REPO / "data/ghidra_project_inventory.baseline.jsonl"
PSEUDO = REPO / "tools/pseudo"
passed = failed = 0


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check(name: str, condition: object, detail: str = "") -> None:
    global passed, failed
    ok = bool(condition)
    passed += int(ok)
    failed += int(not ok)
    print(f"[{'PASS' if ok else 'FAIL'}] {name}" + (f" ({detail})" if detail else ""))


inventory_meta = None
inventory_totals = None
inventory_functions = {}
for line in INVENTORY.read_text(encoding="utf-8").splitlines():
    record = json.loads(line)
    if record["record"] == "meta":
        inventory_meta = record
    elif record["record"] == "totals":
        inventory_totals = record
    elif record["record"] == "function":
        entry = f"0x{int(record['entry']['offset'], 16):08x}"
        inventory_functions[entry] = record
assert inventory_meta is not None and inventory_totals is not None

records = [json.loads(line) for line in CORPUS.read_text(encoding="utf-8").splitlines()]
metadata, functions = records[0], records[1:]

check("corpus and inventory describe the same firmware",
      metadata["executable_sha256"] == inventory_meta["executable_sha256"])
check("interior-address lookup uses the matching inventory",
      metadata["project_inventory_sha256"] == sha256(INVENTORY))
check(
    "artifact has exactly one function per inventory address",
    len(functions) == len(inventory_functions) == inventory_totals["functions"]
    and {record["entry_addr"] for record in functions} == set(inventory_functions),
)
check("artifact is address-sorted", [int(r["entry_addr"], 16) for r in functions] == sorted(int(r["entry_addr"], 16) for r in functions))

print("\n== function identity and pseudocode integrity ==")
errors = []
for record in functions:
    entry = record["entry_addr"]
    expected = inventory_functions[entry]
    code = record["decompiled_c"]
    if record["record"] != "function":
        errors.append(f"{entry}: record kind")
    if record["address_space"] != expected["entry"]["space"]:
        errors.append(f"{entry}: address space")
    if record["body_size"] != expected["body_address_count"]:
        errors.append(f"{entry}: body size")
    if record["is_thunk"] != expected["is_thunk"]:
        errors.append(f"{entry}: thunk")
    if record["calling_convention"] != expected["calling_convention"]:
        errors.append(f"{entry}: convention")
    if expected["user_name"] is not None and record["name"] != expected["user_name"]:
        errors.append(f"{entry}: user name")
    if record["decompile_completed"] is not True or record["decompile_error"]:
        errors.append(f"{entry}: decompile failure")
    if not code.strip() or not record["name"] or not record["signature"]:
        errors.append(f"{entry}: empty decompiler identity/output")
    references = record["data_references"]
    expected_ref_keys = {"from_addr", "to_addr", "to_space", "ref_type", "operand_index"}
    if not isinstance(references, list):
        errors.append(f"{entry}: data reference list")
    else:
        ref_sort = []
        for ref in references:
            if set(ref) != expected_ref_keys:
                errors.append(f"{entry}: data reference schema")
                break
            try:
                ref_sort.append((int(ref["from_addr"], 16), int(ref["to_addr"], 16),
                                 ref["to_space"], ref["ref_type"], int(ref["operand_index"])))
            except (TypeError, ValueError):
                errors.append(f"{entry}: data reference identity")
                break
        if ref_sort != sorted(ref_sort):
            errors.append(f"{entry}: data reference order")
check("all function records match the canonical project", not errors, repr(errors[:12]))

probe = subprocess.run(
    [str(PSEUDO), "0x6fec", "--corpus", str(CORPUS)],
    cwd=REPO,
    capture_output=True,
    text=True,
)
check(
    "tools/pseudo resolves a canonical address to persisted pseudocode",
    probe.returncode == 0 and "security_access_derive_stage1_key" in probe.stdout,
    probe.stderr.strip(),
)
interior_probe = subprocess.run(
    [str(PSEUDO), "0x6fee", "--corpus", str(CORPUS)],
    cwd=REPO,
    capture_output=True,
    text=True,
)
check(
    "tools/pseudo resolves an interior address to its containing function",
    interior_probe.returncode == 0
    and "security_access_derive_stage1_key" in interior_probe.stdout,
    interior_probe.stderr.strip(),
)
with tempfile.TemporaryDirectory() as td:
    unpinned = Path(td) / "unpinned.jsonl"
    stripped_metadata = dict(metadata)
    stripped_metadata.pop("project_inventory_sha256", None)
    function_6fec = next(record for record in functions if record["entry_addr"] == "0x00006fec")
    unpinned.write_text(
        json.dumps(stripped_metadata, sort_keys=True) + "\n"
        + json.dumps(function_6fec, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    unpinned_probe = subprocess.run(
        [str(PSEUDO), "0x6fee", "--corpus", str(unpinned)],
        cwd=REPO, capture_output=True, text=True,
    )
check(
    "tools/pseudo refuses interior lookup without corpus-to-inventory provenance",
    unpinned_probe.returncode != 0
    and "lacks project_inventory_sha256 provenance" in unpinned_probe.stderr,
    unpinned_probe.stderr.strip(),
)
search = subprocess.run(
    [str(PSEUDO), "security_access", "--list", "--corpus", str(CORPUS)],
    cwd=REPO,
    capture_output=True,
    text=True,
)
check(
    "tools/pseudo supports semantic name search",
    search.returncode == 0 and "security_access_derive_stage1_key" in search.stdout,
    search.stderr.strip(),
)
alias_lookup = subprocess.run(
    [str(PSEUDO), "--data-ref", "0xfebef02a", "--corpus", str(CORPUS)],
    cwd=REPO,
    capture_output=True,
    text=True,
)
check(
    "tools/pseudo resolves canonical RAM references despite decompiler base aliases",
    alias_lookup.returncode == 0
    and "0x000ba7fe\tREAD\t0xfebef02a\t0x000ba43a\tsystem_mode_telemetry_snapshot" in alias_lookup.stdout,
    alias_lookup.stderr.strip(),
)
structured_lookup = subprocess.run(
    [str(PSEUDO), "--data-ref", "0xfebe8001", "--corpus", str(CORPUS)],
    cwd=REPO,
    capture_output=True,
    text=True,
)
check(
    "tools/pseudo resolves structured/interior-byte aliases to the canonical byte",
    structured_lookup.returncode == 0
    and "0x000572b0\tREAD\t0xfebe8001\t0x00056fc2\tapplication_rx_signal_consumer_56fc2" in structured_lookup.stdout,
    structured_lookup.stderr.strip(),
)

print(f"\nResults: {passed} passed, {failed} failed")
raise SystemExit(1 if failed else 0)
