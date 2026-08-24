#!/usr/bin/env python3
"""Verify task-oriented tooling consolidation and stale-wrapper removal."""
from __future__ import annotations

import importlib.util
import json
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

print(
    f"verified {len(EXPECTED)} Corolla-H evidence profiles and "
    f"{len(EXPORT_PROFILES)} working-project export profiles"
)
