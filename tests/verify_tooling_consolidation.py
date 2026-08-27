#!/usr/bin/env python3
"""Verify task-oriented tooling consolidation and stale-wrapper removal."""
from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools/extract_corolla_h_evidence.py"

spec = importlib.util.spec_from_file_location("corolla_h_evidence", TOOL)
assert spec and spec.loader
mod = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = mod
spec.loader.exec_module(mod)

EXPECTED = {
    "application-interrupt-bodies": ("application_interrupt_body", 7, "single", True),
    "application-transport": ("application_transport", 5, "single", True),
    "can-com": ("can_com", 19, "mapping", False),
    "crypto-residue": ("crypto_residue", 7, "mapping", False),
    "keyless-event-formatter": ("keyless_event_formatter", 6, "single", False),
    "motor-control": ("motor_control", 13, "single", False),
    "plausibility-monitor": ("plausibility_monitor", 12, "single", True),
    "small-adapters": ("small_adapter", 18, "single", True),
    "steering-nested": ("steering_nested", 14, "single", True),
    "storage-nvm": ("storage_nvm", 3, "single", False),
    "xcp": ("xcp", 11, "list", False),
}


def check(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)
    print(f"[PASS] {message}")


check(set(mod.PROFILES) == set(EXPECTED), "profile set is exact")
for name, (stem, count, source_format, function_only) in EXPECTED.items():
    profile = mod.PROFILES[name]
    check(len(profile.selections) == count, f"{name}: selection count")
    check(profile.source_format == source_format, f"{name}: source metadata shape")
    check(
        profile.output
        == f"data/generated/corolla_8965H1202000_{stem}_decompiler_evidence.json",
        f"{name}: tracked output path",
    )
    check(
        any(source.function_records_only for source in profile.sources.values()) == function_only,
        f"{name}: legacy function-record filtering",
    )

listed = json.loads(
    subprocess.check_output([sys.executable, str(TOOL), "list"], cwd=ROOT, text=True)
)
check([row["name"] for row in listed] == sorted(EXPECTED), "CLI lists profiles deterministically")
check(
    all(row["output"] == mod.PROFILES[row["name"]].output for row in listed),
    "CLI reports tracked default outputs",
)

# Keep the small set of deliberately distinct top-level tooling entry points
# discoverable and pinned rather than hiding them behind a tools/ catch-all.
pe_tool = ROOT / "tools/pe"
pe_source = pe_tool.read_text(encoding="utf-8")
check(pe_tool.is_file() and os.access(pe_tool, os.X_OK), "PE analysis wrapper is an executable task entry point")
check(
    'source "$ROOT/tools/lib/build_paths.sh"' in pe_source
    and 'PROJECT_DIR="$BUILD_WORK/pe-project"' in pe_source
    and '"$ROOT/tools/resolve_ghidra_home.sh"' in pe_source
    and 'exec "$GHIDRA_CLI"' in pe_source,
    "PE analysis wrapper preserves isolated build and Ghidra routing",
)
gts_tool = ROOT / "tools/gts"
gts_source = gts_tool.read_text(encoding="utf-8")
check(gts_tool.is_file() and os.access(gts_tool, os.X_OK), "GTS+ query wrapper is an executable task entry point")
check(
    'uv run --project "$ROOT" --locked python "$ROOT/tools/techstream/gts_cli.py" "$@"' in gts_source,
    "GTS+ query wrapper bootstraps the locked repository environment from any cwd",
)
with tempfile.TemporaryDirectory(prefix="gts-wrapper-cwd-") as td:
    proc = subprocess.run(
        [str(gts_tool), "--help"], cwd=td, text=True, capture_output=True,
    )
    check(proc.returncode == 0 and "GTS+/Techstream" in proc.stdout, "GTS+ query wrapper is location-independent")
    local_cuw = Path(td) / "local.cuw"
    local_cuw.write_bytes(b"x")
    proc = subprocess.run(
        [str(gts_tool), "cuw", "./local.cuw"], cwd=td, text=True, capture_output=True,
    )
    check(
        proc.returncode != 0 and "truncated CUW header" in proc.stderr,
        "GTS+ query wrapper preserves caller-relative artifact paths",
    )
artifact_tool = ROOT / "tools/artifact"
artifact_catalog = ROOT / "tools/artifact_catalog.py"
check(artifact_tool.is_file() and os.access(artifact_tool, os.X_OK), "artifact catalog is an executable task entry point")
check(artifact_catalog.is_file(), "artifact producer/owner catalog lives in one shared module")
proc = subprocess.run(
    [str(artifact_tool), "show", "camry_8965F3307000_fault_status.json", "--json"],
    cwd=ROOT, text=True, capture_output=True,
)
artifact_row = json.loads(proc.stdout) if proc.returncode == 0 else {}
check(
    proc.returncode == 0
    and artifact_row.get("producers") == ["tools/build_camry_8965F3307000_fault_status.py"]
    and "camry_8965f3307000_fault_status" in artifact_row.get("suites", []),
    "artifact catalog derives producer and verification owner without a hand-maintained builder list",
)
proc = subprocess.run([str(artifact_tool), "list", "fault_status"], cwd=ROOT, text=True, capture_output=True)
check(proc.returncode == 0 and "camry_8965F3307000_fault_status.json" in proc.stdout, "artifact catalog provides substring discovery")

check(
    (ROOT / "tools/__init__.py").read_text(encoding="utf-8")
    == '"""Repository tooling modules used by deterministic verification tests."""\n',
    "tools package marker remains side-effect free",
)

# Preserve the old extractors' distinction between whole JSONL corpora and
# Ghidra function-only corpora. A later non-function record with the same entry
# must not overwrite the function record when the profile requests filtering.
(ROOT / "build/tmp").mkdir(parents=True, exist_ok=True)
with tempfile.TemporaryDirectory(prefix="tooling-consolidation-", dir=ROOT / "build/tmp") as td:
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
    check(mod.PROFILES["xcp"].row_source_precedence == ("commands", "helpers"), "XCP profile pins retired helper-corpus precedence")

# No compatibility shims: every tracked caller must migrate to the shared
# profile-driven tool. Generate the retired names so the verifier itself does
# not contain stale literal references.
search_roots = ["AGENTS.md", "Makefile", "verification.toml", "docs", "tests", "tools", ".github"]
for _name, (stem, *_rest) in EXPECTED.items():
    retired = f"tools/extract_corolla_h_{stem}_evidence.py"
    check(not (ROOT / retired).exists(), f"retired tool removed: {stem}")
    proc = subprocess.run(
        ["git", "grep", "-n", "-F", retired, "--", *search_roots],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    check(proc.returncode == 1, f"no stale tracked references: {stem}")

EXPORTER = ROOT / "tools/export_ghidra_project.sh"
EXPORT_PROFILES = [
    "application-rx-signals",
    "application-rx-consumers",
    "application-tx-producers",
    "outside-functions",
    "semantic-coverage",
    "project-inventory",
]
export_list = subprocess.check_output([str(EXPORTER), "list"], cwd=ROOT, text=True).splitlines()
check(export_list == EXPORT_PROFILES, "working-project exporter lists the six semantic profiles")
export_source = EXPORTER.read_text()
check("tools/run_headless" in export_source, "working-project exporter delegates headless safety")
check("-noanalysis" in export_source and "-readOnly" in export_source, "all shared exports are read-only/no-analysis")
check("lib/ghidra_env.sh" not in export_source, "export profiles do not duplicate environment bootstrap")
check("refusing inventory output outside" in export_source, "project inventory retains build-owned output guard")

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

retired_exporters = [
    "application_rx_signal_evidence",
    "application_rx_consumer_audit",
    "application_tx_producer_evidence",
    "outside_function_candidates",
    "semantic_coverage_ledger",
    "project_inventory",
]
for stem in retired_exporters:
    retired = f"tools/generate_{stem}.sh"
    check(not (ROOT / retired).exists(), f"retired export wrapper removed: {stem}")
    proc = subprocess.run(
        ["git", "grep", "-n", "-F", retired, "--", *search_roots],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    check(proc.returncode == 1, f"no stale export-wrapper references: {stem}")

# --- Cross-variant image-bound evidence extraction -------------------------
#
# The former one-file-per-selection variant extractors are consolidated behind
# one subcommand runner. The four modes must remain enumerated, each must keep
# its selection contract, and no tracked reference to the retired files may
# survive.
VARIANT_TOOL = ROOT / "tools/extract_variant_evidence.py"
variant_spec = importlib.util.spec_from_file_location("variant_evidence", VARIANT_TOOL)
assert variant_spec and variant_spec.loader
variant_mod = importlib.util.module_from_spec(variant_spec)
sys.modules[variant_spec.name] = variant_mod
variant_spec.loader.exec_module(variant_mod)

VARIANT_MODES = {
    "structural": "explicit --address list",
    "function": "explicit --address list",
    "application-diagnostics": "DID/routine callback tables read from the image plus explicit --extra addresses",
    "reference-census": "whole-corpus --term NAME=SUBSTRING census",
}
listed_modes = json.loads(
    subprocess.check_output(
        [sys.executable, str(VARIANT_TOOL), "list"], cwd=ROOT, text=True
    )
)
check(set(listed_modes) == set(VARIANT_MODES), "variant evidence mode set is exact")
for mode, selection in VARIANT_MODES.items():
    check(listed_modes[mode]["selection"] == selection, f"{mode}: selection contract")

variant_source = VARIANT_TOOL.read_text()
for mode in VARIANT_MODES:
    check(f'"{mode}"' in variant_source, f"{mode}: subcommand implemented")
# All four modes must share one image-size guard while preserving the retired
# structural tool's user-facing "image" wording.
check(
    variant_source.count("def load_codeflash") == 1,
    "variant modes share one CodeFlash size guard",
)
check(
    variant_source.count("def sha256") == 1,
    "variant modes share one hashing helper",
)

# Exercise every mode on one synthetic image/corpus. This keeps the actual
# shared implementation pinned, rather than relying only on source-shape checks
# or the one-off migration differential harness.
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
    check(structural_payload["schema"] == "rh850-variant-structural-evidence-v1", "structural mode schema")
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

for stem in [
    "extract_variant_structural_evidence",
    "extract_variant_function_evidence",
    "extract_variant_application_diagnostic_evidence",
    "extract_variant_decompiler_reference_census",
]:
    retired = f"tools/{stem}.py"
    check(not (ROOT / retired).exists(), f"retired variant extractor removed: {stem}")
    proc = subprocess.run(
        ["git", "grep", "-n", "-F", retired, "--", *search_roots],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    check(proc.returncode == 1, f"no stale variant-extractor references: {stem}")
# Distinct semantic variant tools that deliberately stay separate.
for separate in [
    "tools/check_variant_acquisition.py",
    "tools/compare_variant_application_diagnostics.py",
    "tools/compare_variant_application_rx.py",
    "tools/compare_variant_function_bodies.py",
    "tools/match_variant_function_structure.py",
    "tools/build_variant_named_transfer_ledger.py",
]:
    check((ROOT / separate).exists(), f"semantic variant tool stays separate: {separate}")

# Pin the deliberate non-consolidation boundaries documented in
# docs/tooling/README.md. These files encode distinct evidence/safety contracts,
# not profile variants of one operation.
for separate in [
    "tools/techstream/parse_cuw_container.py",
    "tools/techstream/inspect_cuw_legacy.py",
    "tools/techstream/inspect_cuw_vforest.py",
    "tools/techstream/inspect_cuw_vforest_corpus.py",
    "tools/techstream/inspect_cuw_frc_corpus.py",
    "tools/techstream/generate_cuw_writer_inventory.py",
    "tools/techstream/generate_cuw_writer_protocol_grammar.py",
    "tools/techstream/generate_cuw_writer_family_matrix.py",
    "tools/extract_corolla_h_direct_call_surface_evidence.py",
    "tools/extract_corolla_h_deadline_monitor_surface_evidence.py",
    "tools/extract_corolla_h_diagnostic_residue_evidence.py",
    "tools/extract_corolla_h_structural_residue_evidence.py",
    "tools/extract_corolla_h_secoc_surface_evidence.py",
    "tools/extract_corolla_h_final_named_residue_evidence.py",
    "tools/resolve_secoc_patch_image.sh",
    "tools/resolve_ephemeral_runtime_image.sh",
    "tools/resolve_secoc_patch.sh",
]:
    check((ROOT / separate).exists(), f"documented distinct tool stays separate: {separate}")

print(
    f"verified {len(EXPECTED)} Corolla-H evidence profiles, "
    f"{len(EXPORT_PROFILES)} working-project export profiles, and "
    f"{len(VARIANT_MODES)} variant evidence modes"
)
