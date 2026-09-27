#!/usr/bin/env python3
"""Verify evidence tooling behavior.

Covers the profile-driven Corolla-H evidence extractor (corpus filtering and
merged-source precedence), artifact catalog queries, caller-relative wrapper
paths, the working-project exporter's output guard, and the cross-variant
evidence extraction modes.
"""
from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools/targets/corolla/extract/extract_corolla_h_evidence.py"
VARIANT_TOOL = ROOT / "tools/variants/extract_variant_evidence.py"
EXPORTER = ROOT / "tools/project/export_ghidra_project.sh"
GTS_TOOL = ROOT / "tools/gts"
ARTIFACT_TOOL = ROOT / "tools/artifact"
VARIANT_MODES = ("structural", "function", "application-diagnostics", "reference-census")

spec = importlib.util.spec_from_file_location("corolla_h_evidence", TOOL)
assert spec and spec.loader
mod = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = mod
spec.loader.exec_module(mod)

variant_spec = importlib.util.spec_from_file_location("variant_evidence", VARIANT_TOOL)
assert variant_spec and variant_spec.loader
variant_mod = importlib.util.module_from_spec(variant_spec)
sys.modules[variant_spec.name] = variant_mod
variant_spec.loader.exec_module(variant_mod)


def check(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)
    print(f"[PASS] {message}")


# Preserve the old extractors' distinction between whole JSONL corpora and
# Ghidra function-only corpora. A later non-function record with the same entry
# must not overwrite the function record when the profile requests filtering.
(ROOT / "build/tmp").mkdir(parents=True, exist_ok=True)
with tempfile.TemporaryDirectory(prefix="evidence-tooling-", dir=ROOT / "build/tmp") as td:
    corpus = Path(td) / "fixture.jsonl"
    corpus.write_text(
        json.dumps({
            "record": "function",
            "entry_addr": "0x10",
            "body_size": 4,
            "decompile_completed": True,
            "decompiled_c": "FUNCTION",
        })
        + "\n"
        + json.dumps({
            "record": "metadata",
            "entry_addr": "0x10",
            "body_size": 4,
            "decompile_completed": True,
            "decompiled_c": "NOT_FUNCTION",
        })
        + "\n"
    )
    filtered = mod.load_corpus(corpus, function_records_only=True)
    unfiltered = mod.load_corpus(corpus)
    check(filtered[0x10]["decompiled_c"] == "FUNCTION", "function-only corpus filter is preserved")
    check(unfiltered[0x10]["decompiled_c"] == "NOT_FUNCTION", "unfiltered corpus semantics are preserved")

    # The retired XCP extractor merged command rows first and helper rows
    # second, so a helper-corpus duplicate had to win. Pin that otherwise easy
    # to lose behavior with an intentional overlapping fixture.
    raw = Path(td) / "raw.bin"
    raw.write_bytes(bytes(range(256)) * 0x1000)
    commands = Path(td) / "commands.jsonl"
    helpers = Path(td) / "helpers.jsonl"
    commands.write_text(json.dumps({
        "entry_addr": "10", "body_size": 4, "decompile_completed": True,
        "decompiled_c": "COMMAND_VERSION",
    }) + "\n")
    helpers.write_text(json.dumps({
        "entry_addr": "10", "body_size": 4, "decompile_completed": True,
        "decompiled_c": "HELPER_VERSION",
    }) + "\n")
    overlap_profile = mod.Profile(
        summary="precedence fixture",
        schema="test-v1",
        output="build/tmp/unused.json",
        sources={
            "commands": mod.Source(str(commands.relative_to(ROOT))),
            "helpers": mod.Source(str(helpers.relative_to(ROOT))),
        },
        selections=(mod.Selection(0x10, "commands"),),
        source_format="list",
        row_source_precedence=("commands", "helpers"),
    )
    overlap_payload = mod.build_artifact(
        overlap_profile,
        raw_path=raw,
        source_paths={"commands": commands, "helpers": helpers},
    )
    check(overlap_payload["functions"][0]["decompiled_c"] == "HELPER_VERSION", "merged-corpus later-source precedence is preserved")

# The wrapper must resolve its own environment from the repository root while
# keeping caller-relative artifact paths intact.
with tempfile.TemporaryDirectory(prefix="gts-wrapper-cwd-") as td:
    local_cuw = Path(td) / "local.cuw"
    local_cuw.write_bytes(b"x")
    proc = subprocess.run(
        [str(GTS_TOOL), "cuw", "./local.cuw"], cwd=td, text=True, capture_output=True,
    )
    check(
        proc.returncode != 0 and "truncated CUW header" in proc.stderr,
        "GTS+ query wrapper runs from any cwd and preserves caller-relative artifact paths",
    )

proc = subprocess.run(
    [str(ARTIFACT_TOOL), "show", "camry_8965F3307000_fault_status.json", "--json"],
    cwd=ROOT, text=True, capture_output=True,
)
artifact_row = json.loads(proc.stdout) if proc.returncode == 0 else {}
check(
    proc.returncode == 0
    and artifact_row.get("producers") == ["tools/targets/camry/builders/build_camry_8965F3307000_fault_status.py"],
    "artifact catalog derives producer without a hand-maintained builder list",
)
proc = subprocess.run([str(ARTIFACT_TOOL), "list", "fault_status"], cwd=ROOT, text=True, capture_output=True)
check(proc.returncode == 0 and "camry_8965F3307000_fault_status.json" in proc.stdout, "artifact catalog provides substring discovery")

# BUILD_ROOT may be supplied through a symlink. The inventory guard must compare
# canonical paths, and a failed headless preflight must not delete a pre-existing
# output artifact before the shared safety runner has succeeded.
with tempfile.TemporaryDirectory(prefix="exporter-symlink-", dir=ROOT / "build/tmp") as td:
    fixture = Path(td)
    actual = fixture / "actual"
    actual.mkdir()
    linked = fixture / "linked"
    linked.symlink_to(actual, target_is_directory=True)
    project_dir = linked / "work/project"
    (actual / "work/project/rh850_p1me_mapped.rep").mkdir(parents=True)
    fake_home = fixture / "fake-ghidra"
    (fake_home / "support").mkdir(parents=True)
    fake_analyze = fake_home / "support/analyzeHeadless"
    fake_analyze.write_text("#!/bin/sh\nexit 7\n")
    fake_analyze.chmod(0o755)
    inventory_out = linked / "out/inventory.jsonl"
    (actual / "out").mkdir(parents=True)
    inventory_out.write_text("sentinel\n")
    environment = os.environ.copy()
    environment.update({
        "BUILD_ROOT": str(linked),
        "PROJECT_DIR": str(project_dir),
        "GHIDRA_NO_BOOTSTRAP": "1",
        "GHIDRA_HOME": str(fake_home),
    })
    failed_export = subprocess.run(
        [str(EXPORTER), "project-inventory", str(inventory_out)],
        cwd=ROOT,
        env=environment,
        text=True,
        capture_output=True,
        check=False,
    )
    check(failed_export.returncode != 0, "inventory fake-headless failure is surfaced")
    check("refusing inventory output outside" not in failed_export.stderr, "inventory guard accepts canonicalized symlinked build root")
    check(inventory_out.read_text() == "sentinel\n", "failed inventory export preserves prior output")

# Exercise every variant mode on one synthetic image/corpus so the shared
# extraction implementation itself stays pinned.
with tempfile.TemporaryDirectory(prefix="variant-evidence-", dir=ROOT / "build/tmp") as td:
    fixture = Path(td)
    image = bytearray((index * 17 + 5) & 0xFF for index in range(0x100000))
    did_offset = 0x200
    routine_offset = 0x300
    variant_mod.DID.pack_into(image, did_offset, 0xF410, 4, 0x40, 0, 0)
    variant_mod.RID_CB.pack_into(image, routine_offset, 0x0203, 0, 0x80, 0xC0)
    image_path = fixture / "image.bin"
    image_path.write_bytes(image)

    fingerprints = fixture / "fingerprints.jsonl"
    fingerprints.write_text(json.dumps({
        "entry_addr": "40",
        "body_size": 4,
        "instruction_count": 2,
        "mnemonics": ["mov", "ret"],
        "instruction_lengths": [2, 2],
        "conditional_branch_count": 0,
        "unconditional_branch_count": 0,
        "direct_call_target_count": 0,
        "indirect_call_count": 0,
        "return_count": 1,
    }) + "\n")

    corpus = fixture / "corpus.jsonl"
    corpus.write_text("\n".join(json.dumps(row) for row in [
        {
            "entry_addr": "40", "body_size": 4, "decompile_completed": True,
            "decompiled_c": "int a(void) { return TOKEN; }",
        },
        {
            "entry_addr": "80", "body_size": 6, "decompile_completed": True,
            "decompiled_c": "int b(void) { return 2; }",
        },
        {
            "entry_addr": "c0", "body_size": 8, "decompile_completed": True,
            "decompiled_c": "int c(void) { return 3; }",
        },
    ]) + "\n")

    outputs = {name: fixture / f"{name}.json" for name in VARIANT_MODES}
    subprocess.run([
        sys.executable, str(VARIANT_TOOL), "structural",
        "--image", str(image_path), "--fingerprints", str(fingerprints),
        "--software-id", "TEST", "--address", "0x40", "--out", str(outputs["structural"]),
    ], cwd=ROOT, check=True, capture_output=True, text=True)
    structural_payload = json.loads(outputs["structural"].read_text())
    check(structural_payload["functions"][0]["body_sha256"] == variant_mod.sha256(bytes(image[0x40:0x44])), "structural mode binds raw body")

    subprocess.run([
        sys.executable, str(VARIANT_TOOL), "function",
        "--image", str(image_path), "--corpus", str(corpus),
        "--software-id", "TEST", "--address", "0x80", "--out", str(outputs["function"]),
    ], cwd=ROOT, check=True, capture_output=True, text=True)
    function_payload = json.loads(outputs["function"].read_text())
    check(function_payload["functions"][0]["entry"] == "0x00000080", "function mode selects requested address")
    check(function_payload["functions"][0]["decompiled_c"] == "int b(void) { return 2; }", "function mode preserves decompilation")

    subprocess.run([
        sys.executable, str(VARIANT_TOOL), "application-diagnostics",
        "--image", str(image_path), "--corpus", str(corpus),
        "--did-table", hex(did_offset), "--did-count", "1",
        "--routine-callback-table", hex(routine_offset), "--routine-count", "1",
        "--extra", "0xc0", "--software-id", "TEST", "--out", str(outputs["application-diagnostics"]),
    ], cwd=ROOT, check=True, capture_output=True, text=True)
    diagnostic_payload = json.loads(outputs["application-diagnostics"].read_text())
    diagnostic_rows = {row["entry"]: row for row in diagnostic_payload["functions"]}
    check(set(diagnostic_rows) == {"0x00000040", "0x00000080", "0x000000C0"}, "diagnostic mode resolves image callback tables")
    check(diagnostic_rows["0x00000040"]["selection_roles"] == ["rdbi_producer"], "diagnostic mode labels RDBI role")
    check(diagnostic_rows["0x000000C0"]["selection_roles"] == ["extra_helper_or_downstream", "routine_control_callback"], "diagnostic mode preserves overlapping roles")

    subprocess.run([
        sys.executable, str(VARIANT_TOOL), "reference-census",
        "--image", str(image_path), "--corpus", str(corpus),
        "--software-id", "TEST", "--term", "token=TOKEN", "--out", str(outputs["reference-census"]),
    ], cwd=ROOT, check=True, capture_output=True, text=True)
    census_payload = json.loads(outputs["reference-census"].read_text())
    check(census_payload["terms"]["token"]["match_count"] == 1, "reference census finds exact substring")
    check(census_payload["terms"]["token"]["matches"][0]["entry"] == "0x00000040", "reference census binds matching function")

    malformed = fixture / "blank-line.jsonl"
    malformed.write_text(json.dumps({"entry_addr": "40"}) + "\n\n")
    try:
        list(variant_mod.iter_corpus(malformed))
    except json.JSONDecodeError:
        pass
    else:
        raise AssertionError("variant corpus parser silently accepted a blank JSONL record")
    print("[PASS] variant corpus parser preserves strict blank-line rejection")

print(
    "verified evidence tooling: corpus filtering, merged-source precedence, "
    "artifact catalog queries, caller-relative wrapper paths, exporter output "
    f"guard, and {len(VARIANT_MODES)} variant evidence modes"
)
