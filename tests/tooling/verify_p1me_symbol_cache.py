#!/usr/bin/env python3
"""Black-box baseline/pass probe for Ghidra 12.2 JIT symbol-cache roots."""
from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
from unittest.mock import patch

from tools import REPO_ROOT
from tools.emulation.p1me_machine import _execute

TARGET = "camry-8965F3307000"
REPETITIONS = 6


def _scenario(index: int) -> dict:
    ram = "0xFEBE0000"
    expected = "2" if index % 2 else "1"
    return {
        "schema": "rh850-p1me-machine-scenario-v2",
        "name": f"symbol-cache-probe-{index}",
        "engine": "jit",
        "entry": {"role": "constant-loop", "scope": "resolved-address", "address": ram},
        "gpr_fill": "0",
        "registers": {"lp": ram},
        "memory": [{
            "address": ram,
            "hex": "01527f00",
            "evidence": "Bounded mov 1,r10; jmp [lp] loop warms repeated JIT passages.",
        }],
        "max_instructions": 192,
        "stop_addresses": [],
        "expected_termination": "instruction-budget",
        "checks": [{"name": "intentional-alternating-verdict", "kind": "register",
                    "register": "r10", "equals": expected}],
    }


def _clone_project(source: Path, destination: Path) -> None:
    if sys.platform == "darwin":
        subprocess.run(["cp", "-cR", str(source), str(destination)], check=True)
    else:
        subprocess.run(
            ["cp", "-a", "--reflink=auto", str(source), str(destination)], check=True,
        )
    for lock in destination.glob("*.lock*"):
        lock.unlink()


def _run(project: Path, paths: list[Path], *, patched: bool) -> list[dict]:
    isolated_home = project.parent / f"{project.name}-home"
    extension = (
        isolated_home / "Library/ghidra/ghidra_12.2_PUBLIC/Extensions/Renesas_v850"
    )
    extension.parent.mkdir(parents=True)
    build_root = Path(os.environ.get("BUILD_ROOT", REPO_ROOT / "build"))
    if not build_root.is_absolute():
        build_root = REPO_ROOT / build_root
    canonical_extension = (
        build_root / "cache/ghidra-home/Library/ghidra/ghidra_12.2_PUBLIC"
        / "Extensions/Renesas_v850"
    )
    extension.symlink_to(canonical_extension, target_is_directory=True)
    options = " ".join(
        option for option in os.environ.get("GHIDRA_HEADLESS_JAVA_OPTIONS", "").split()
        if "ghidra.external.modules=" not in option
    )
    java_options = " ".join(
        option for option in os.environ.get("GHIDRA_JAVA_OPTIONS", "").split()
        if "ghidra.external.modules=" not in option
    )
    environment = {
        "GHIDRA_PROJECT": str(project),
        "GHIDRA_JAVA_OPTIONS": java_options,
        "GHIDRA_HEADLESS_JAVA_OPTIONS": (
            f"{options} -Duser.home={isolated_home} -Dp1me.symbolCacheProbe=true"
        ).strip(),
        "GHIDRA_DISABLE_EMULATION_PATCH": "0" if patched else "1",
    }
    try:
        with patch.dict(os.environ, environment):
            return _execute(TARGET, paths)["reports"]
    finally:
        subprocess.run(
            [str(REPO_ROOT / "tools" / "gtarget"), TARGET, "stop"],
            cwd=REPO_ROOT, env={**os.environ, **environment}, check=False,
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )


def main() -> None:
    registry = json.loads((REPO_ROOT / "data" / "analysis_targets.json").read_text())
    source_project = REPO_ROOT / registry["targets"][TARGET]["work_dir"]
    if not source_project.is_dir():
        raise AssertionError(f"missing deployed project: {source_project}")

    temp_parent = REPO_ROOT / "build" / "tmp"
    temp_parent.mkdir(parents=True, exist_ok=True)
    with TemporaryDirectory(prefix="p1me-symbol-cache-", dir=temp_parent) as temp:
        root = Path(temp)
        paths: list[Path] = []
        for index in range(REPETITIONS):
            path = root / f"probe-{index}.json"
            path.write_text(json.dumps(_scenario(index)), encoding="utf-8")
            paths.append(path)

        baseline_project = root / "baseline-project"
        patched_project = root / "patched-project"
        _clone_project(source_project, baseline_project)
        _clone_project(source_project, patched_project)
        baseline = _run(baseline_project, paths, patched=False)
        fixed = _run(patched_project, paths, patched=True)

    expected_passes = [index % 2 == 0 for index in range(REPETITIONS)]
    for label, reports in (("baseline", baseline), ("patched", fixed)):
        assert len(reports) == REPETITIONS, (label, len(reports))
        assert [report["passed"] for report in reports] == expected_passes, label
        compiled = [report["jit_compiled_instructions"] for report in reports]
        assert all(count > 0 for count in compiled), (label, compiled)

    baseline_sources = [report["daemon_symbols_cache_source"] for report in baseline]
    fixed_sources = [report["daemon_symbols_cache_source"] for report in fixed]
    assert all(source.startswith("jar:") and "Emulation.jar!" in source
               for source in baseline_sources), baseline_sources
    assert all(source.startswith("file:") and
               "/EmulationSymbolsCache/bin/main/ghidra/pcode/exec/SymbolsCache.class" in source
               for source in fixed_sources), fixed_sources

    baseline_roots = [
        report["daemon_jit_dataflow_symbol_cache_roots"] for report in baseline
    ]
    fixed_roots = [report["daemon_jit_dataflow_symbol_cache_roots"] for report in fixed]
    assert all(count > 0 for count in baseline_roots), baseline_roots
    assert baseline_roots == sorted(baseline_roots), baseline_roots
    assert fixed_roots == [0] * REPETITIONS, fixed_roots
    print(
        f"PASS {REPETITIONS} bounded compilations including failed scenarios: "
        f"12.2 baseline roots {baseline_roots}; patched roots {fixed_roots}"
    )


if __name__ == "__main__":
    main()
