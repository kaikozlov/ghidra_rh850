#!/usr/bin/env python3
"""Verify corpus coverage, function identities, and pseudocode lookup."""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from pathlib import Path
from unittest.mock import patch

from tools import REPO_ROOT
from tools.project import pseudo
from tools.project.generate_decompiler_corpus import load_inventory
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
with tempfile.TemporaryDirectory() as td:
    phase_inventory = Path(td) / "phases.jsonl"
    phase_records = [
        {"record": "meta"},
        {"record": "function", "entry": {"space": "ram", "offset": "00001000"}},
        {"record": "function", "entry": {"space": "boot", "offset": "00002000"}},
        {"record": "memory_block", "overlay": True, "start": {"space": "boot"}},
        {"record": "totals", "functions": 2},
    ]
    phase_inventory.write_text("\n".join(map(json.dumps, phase_records)) + "\n")
    _meta, phase_functions, totals = load_inventory(phase_inventory)
    check("relocated functions retain their address-space identities in the corpus",
          set(phase_functions) == {"0x00001000", "0x00002000"}
          and phase_functions["0x00002000"]["entry"]["space"] == "boot"
          and totals["functions"] == 2)
    phase_records[2]["entry"]["offset"] = "00001000"
    phase_inventory.write_text("\n".join(map(json.dumps, phase_records)) + "\n")
    try:
        load_inventory(phase_inventory)
    except SystemExit:
        duplicate_rejected = True
    else:
        duplicate_rejected = False
    check("ambiguous numeric addresses are rejected rather than merging phases", duplicate_rejected)
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


def invoke_pseudo(*args: str) -> tuple[int, str, str]:
    stdout, stderr = StringIO(), StringIO()
    with patch.object(sys, "argv", ["pseudo", *args]), redirect_stdout(stdout), redirect_stderr(stderr):
        status = pseudo.main()
    return status, stdout.getvalue(), stderr.getvalue()


def fixture_reference(source: str, destination: str) -> dict[str, str | int]:
    return {
        "from_addr": source, "to_addr": destination, "to_space": "ram",
        "ref_type": "READ", "operand_index": 1,
    }


with tempfile.TemporaryDirectory() as td:
    fixture = Path(td)
    inventory_path = fixture / "inventory.jsonl"
    fixture_corpus = fixture / "corpus.jsonl"
    alpha_ref = fixture_reference("0x00001002", "0x00002000")
    alpha_second_ref = fixture_reference("0x00001003", "0x00002000")
    alpha_other_ref = fixture_reference("0x00001004", "0x00002004")
    beta_ref = fixture_reference("0x00001102", "0x00002000")

    def address(offset: int) -> dict[str, str]:
        return {"space": "ram", "offset": f"{offset:08x}"}

    layout = [
        (0x1000, "compute_alpha", [(0x1000, 0x1005), (0x1010, 0x1015)],
         [alpha_ref, alpha_second_ref, alpha_other_ref]),
        (0x1100, "compute_beta", [(0x1100, 0x1104), (0x1015, 0x1017)], [beta_ref]),
    ]
    inventory_path.write_text("\n".join(json.dumps({
        "record": "function", "entry": address(entry),
        "body_ranges": [{"min": address(start), "max": address(end)} for start, end in ranges],
    }) for entry, _, ranges, _ in layout) + "\n", encoding="utf-8")
    fixture_rows = [{
        "record": "metadata",
        "project_inventory_path": str(inventory_path),
        "project_inventory_sha256": sha256(inventory_path),
    }]
    fixture_rows.extend({
        "record": "function", "entry_addr": f"0x{entry:08x}", "name": name,
        "signature": f"int {name}(void)", "decompiled_c": f"int {name}(void) {{ return 1; }}\n",
        "data_references": references,
    } for entry, name, _, references in layout)
    fixture_corpus.write_text("\n".join(map(json.dumps, fixture_rows)) + "\n", encoding="utf-8")
    corpus_args = ("--corpus", str(fixture_corpus))

    queries = ["compute_alpha", "0x1102", "0x1008", "1015", "1014", "compute", "0x1000"]
    with (
        patch.object(pseudo, "load_corpus", wraps=pseudo.load_corpus) as load,
        patch.object(pseudo, "load_function_body_ranges", wraps=pseudo.load_function_body_ranges) as ranges,
    ):
        status, stdout, stderr = invoke_pseudo(queries[0], *corpus_args, "--json", *queries[1:])
    payload = json.loads(stdout)
    results = payload["results"]
    check(
        "JSON batches keep mixed name/address results in input order and mark misses",
        status == 1 and not stderr
        and payload == {"target": None, "corpus": str(fixture_corpus.resolve()), "mode": "function", "results": results}
        and [row["query"] for row in results] == queries
        and [[match["entry"] for match in row["matches"]] for row in results] == [
            ["0x00001000"], ["0x00001100"], [], [], ["0x00001000"],
            ["0x00001000", "0x00001100"], ["0x00001000"],
        ]
        and "no pseudocode function matches" in results[2]["error"]
        and "belongs to multiple functions" in results[3]["error"]
        and all(row["error"] is None for row in (results[0], results[1], *results[4:])),
        stdout,
    )
    check("a mixed batch reads the corpus and pinned inventory only once",
          load.call_count == 1 and ranges.call_count == 1)
    check(
        "normal JSON rows contain exact identity, canonical refs and unambiguous code",
        results[0]["matches"] == [{
            "entry": "0x00001000", "name": "compute_alpha", "signature": "int compute_alpha(void)",
            "references": [alpha_ref, alpha_second_ref, alpha_other_ref], "decompiled_c": fixture_rows[1]["decompiled_c"],
        }]
        and all("decompiled_c" not in row for row in results[5]["matches"]),
    )

    with patch.object(pseudo, "load_function_body_ranges", wraps=pseudo.load_function_body_ranges) as ranges:
        status, stdout, stderr = invoke_pseudo(*corpus_args, "--list", "0x1000", "no_such_name", "compute_beta")
    check(
        "text batches keep successful output on both sides of a miss without reading inventory",
        status == 1 and ranges.call_count == 0 and "no_such_name" in stderr
        and stdout.splitlines() == [
            "0x00001000\tcompute_alpha\tint compute_alpha(void)",
            "0x00001100\tcompute_beta\tint compute_beta(void)",
        ],
    )

    with patch.object(pseudo, "load_function_body_ranges", wraps=pseudo.load_function_body_ranges) as ranges:
        status, stdout, stderr = invoke_pseudo(
            *corpus_args, "--inventory", str(fixture / "missing.jsonl"), "--json", "0x1014", "0x1102", "compute_beta",
        )
    results = json.loads(stdout)["results"]
    check(
        "unavailable inventory is reported per interior query and does not block exact matches",
        status == 1 and not stderr and ranges.call_count == 1
        and all(not row["matches"] and "Pass --inventory" in row["error"] for row in results[:2])
        and results[-1]["error"] is None and results[-1]["matches"][0]["entry"] == "0x00001100",
    )

    ref_queries = ["2004", "0x2001", "invalid", "0X2000"]
    status, stdout, stderr = invoke_pseudo(
        *corpus_args, "--json", *(arg for query in ref_queries for arg in ("--data-ref", query)),
    )
    payload = json.loads(stdout)
    results = payload["results"]
    check(
        "JSON reference batches group only matching canonical references and preserve misses",
        status == 1 and not stderr and payload["mode"] == "data-ref"
        and [row["query"] for row in results] == ref_queries
        and results[0]["matches"] == [{
            "entry": "0x00001000", "name": "compute_alpha",
            "signature": "int compute_alpha(void)", "references": [alpha_other_ref],
        }]
        and results[0]["error"] is None
        and not results[1]["matches"] and "no canonical data references" in results[1]["error"]
        and not results[2]["matches"] and "invalid data-reference address" in results[2]["error"]
        and results[3]["error"] is None
        and [row["references"] for row in results[3]["matches"]] == [[alpha_ref, alpha_second_ref], [beta_ref]],
        stdout,
    )


print(f"\nResults: {passed} passed, {failed} failed")
raise SystemExit(1 if failed else 0)
