#!/usr/bin/env python3
"""Verify manifest ownership and pass/fail/skip/oracle runner semantics."""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import tomllib
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
RUNNER = REPO / "tools/fast_verify.py"
MANIFEST = REPO / "verification.toml"
MAKEFILE = REPO / "Makefile"
ALLOWED_ORACLES = {
    "identity_hash", "documentation_lint", "generated_self_check", "raw_bytes",
    "instruction_semantics", "cfg_dataflow", "dynamic_trace",
    "independent_external_artifact",
}
passed = failed = 0


def check(name: str, condition: object, detail: str = "") -> None:
    global passed, failed
    ok = bool(condition)
    passed += int(ok)
    failed += int(not ok)
    print(f"[{'PASS' if ok else 'FAIL'}][raw_bytes] {name}" + (f" ({detail})" if detail else ""))


manifest = tomllib.loads(MANIFEST.read_text(encoding="utf-8"))
suites = manifest["suite"]
ownership: dict[str, list[str]] = {}
for suite_name, entry in suites.items():
    for test in entry.get("tests", []):
        ownership.setdefault(test, []).append(suite_name)
gate_glob = manifest["verification"]["gate_glob"]
discovered = {path.relative_to(REPO).as_posix() for path in REPO.glob(gate_glob)}

print("== authoritative ownership ==")
check("every verify gate is manifest-owned", discovered == set(ownership),
      f"missing={sorted(discovered - set(ownership))} stale={sorted(set(ownership) - discovered)}")
check("every gate has exactly one owner",
      all(len(owners) == 1 for owners in ownership.values()),
      str({test: owners for test, owners in ownership.items() if len(owners) != 1}))
check("changed-suite routing includes owned test paths",
      '*entry.get("tests", [])' in RUNNER.read_text(encoding="utf-8"))
for required in (
    "tests/verify_techstream_rks.py",
    "tests/verify_techstream_layerb.py",
    "tests/verify_techstream_dtc_failure_types.py",
):
    check(f"required claim gate is owned: {required}", len(ownership.get(required, [])) == 1)

default_oracle = manifest["verification"]["default_oracle"]
default_modes = manifest["verification"]["default_modes"]
check("manifest default oracle is valid", default_oracle in ALLOWED_ORACLES)
check("manifest default modes define core/full/local tiers", default_modes == ["core", "full", "local"])
check("all explicit suite modes are known",
      all(set(entry.get("modes", default_modes)) <= {"core", "full", "local"}
          for entry in suites.values()))
check("all suite oracle classifications are valid",
      all(entry.get("oracle", default_oracle) in ALLOWED_ORACLES for entry in suites.values()))
external_names = set(manifest.get("external", {}))
check("every external requirement resolves to manifest metadata",
      all(set(entry.get("requires_external", [])) <= external_names for entry in suites.values()))
check("external-backed suites are local-only",
      all(entry.get("modes") == ["local"]
          for entry in suites.values() if entry.get("requires_external")))
check("exhaustive Corolla DataFlash scan is outside the edit-loop core",
      suites["albinoelephant_corolla_dataflash"].get("modes") == ["full", "local"])
manifest_paths = [
    (suite_name, kind, value)
    for suite_name, entry in suites.items()
    for kind in ("tests", "paths")
    for value in entry.get(kind, [])
]
missing_manifest_paths = [
    (suite_name, kind, value)
    for suite_name, kind, value in manifest_paths
    if not (REPO / value.rstrip("/")).exists()
]
check(
    "every manifest test/change path exists",
    not missing_manifest_paths,
    str(missing_manifest_paths[:10]),
)
tracked_paths = set(subprocess.check_output(["git", "ls-files"], cwd=REPO, text=True).splitlines())
untracked_manifest_paths = [
    (suite_name, kind, value)
    for suite_name, kind, value in manifest_paths
    if not (any(path.startswith(value) for path in tracked_paths) if value.endswith("/") else value in tracked_paths)
]
check(
    "every manifest change-routing path is tracked repository state",
    not untracked_manifest_paths,
    str(untracked_manifest_paths[:10]),
)
check("every external Techstream suite declares its prerequisite",
      all("techstream_v18" in suites[name].get("requires_external", []) for name in (
          "techstream_rks", "techstream_layerb", "techstream_ddb_residuals",
          "techstream_master_routes", "techstream_priority_ddb_semantics",
          "techstream_dtc_failure_types", "techstream_mackey",
          "techstream_crypto_inventory", "techstream_artifact_lock",
          "techstream_cuw_writer_routes",
      )))

makefile = MAKEFILE.read_text(encoding="utf-8")
check("Makefile has no duplicate VERIFY_SUITES manifest", "VERIFY_SUITES" not in makefile)
for target, mode in (
    ("verify-core", "--core"),
    ("verify-full", "--full"),
    ("verify-local", "--local"),
    ("verify-changed", "--changed"),
    ("verify-agent", "--agent"),
    ("verify-required-external", "--required-external"),
):
    check(f"Make target {target} delegates to manifest runner",
          f"{target}:" in makefile and f"tools/fast_verify.py {mode}" in makefile)


print("\n== isolated runner behavior ==")
with tempfile.TemporaryDirectory(prefix="verify-runner-") as directory:
    root = Path(directory)
    (root / "tests").mkdir()
    (root / "tests/pass.py").write_text(
        "print('[PASS][raw_bytes] pinned record')\n"
        "print('[PASS][identity_hash] body hash')\n",
        encoding="utf-8",
    )
    (root / "tests/identity.py").write_text(
        "print('[PASS] identity only')\n", encoding="utf-8"
    )
    (root / "tests/legacy.py").write_text(
        "print('PASS: legacy assertion')\n", encoding="utf-8"
    )
    (root / "tests/printed_fail.py").write_text(
        "print('[FAIL][cfg_dataflow] decisive assertion')\n", encoding="utf-8"
    )
    (root / "tests/late_skip.py").write_text(
        "print('[SKIP] artifact-level prerequisite unavailable')\n"
        "raise SystemExit(77)\n",
        encoding="utf-8",
    )
    (root / "tests/portable_env.py").write_text(
        "import os\n"
        "ok = os.environ.get('RH850_VERIFY_EXTERNAL') == '0'\n"
        "print(('[PASS]' if ok else '[FAIL]') + '[raw_bytes] portable external flag')\n"
        "raise SystemExit(0 if ok else 1)\n",
        encoding="utf-8",
    )
    (root / "tests/local_env.py").write_text(
        "import os\n"
        "ok = os.environ.get('RH850_VERIFY_EXTERNAL') == '1'\n"
        "print(('[PASS]' if ok else '[FAIL]') + '[raw_bytes] local external flag')\n"
        "raise SystemExit(0 if ok else 1)\n",
        encoding="utf-8",
    )
    synthetic_manifest = root / "verification.toml"
    synthetic_manifest.write_text(
        """[verification]
default_oracle = "raw_bytes"
skip_exit_code = 77
gate_glob = "tests/*.py"
default_modes = ["core", "full", "local"]

[external.techstream_v18]
path = "missing-techstream"

[suite.core]
tests = ["tests/pass.py"]
paths = ["tests/pass.py"]
oracle = "raw_bytes"

[suite.identity]
tests = ["tests/identity.py"]
paths = ["tests/identity.py"]
oracle = "identity_hash"

[suite.legacy]
tests = ["tests/legacy.py"]
paths = ["tests/legacy.py"]
oracle = "raw_bytes"

[suite.printed_fail]
tests = ["tests/printed_fail.py"]
paths = ["tests/printed_fail.py"]
oracle = "raw_bytes"
modes = []

[suite.portable_env]
tests = ["tests/portable_env.py"]
paths = ["tests/portable_env.py"]
modes = ["core", "full"]
oracle = "raw_bytes"

[suite.local_env]
tests = ["tests/local_env.py"]
paths = ["tests/local_env.py"]
modes = ["local"]
oracle = "raw_bytes"

[suite.external]
tests = ["tests/pass.py"]
paths = ["external/"]
requires_external = ["techstream_v18"]
modes = ["local"]
oracle = "raw_bytes"

[suite.external_late_skip]
tests = ["tests/late_skip.py"]
paths = ["external/"]
requires_external = ["techstream_v18"]
modes = ["local"]
oracle = "independent_external_artifact"
""",
        encoding="utf-8",
    )

    def run(*args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(RUNNER), *args, "--repo-root", str(root),
             "--manifest", str(synthetic_manifest)],
            capture_output=True, text=True,
        )

    core_missing = run("--core")
    check("repository-only mode succeeds with absent optional source", core_missing.returncode == 0)
    check("core excludes external-backed suites instead of probing local state",
          "external:" not in core_missing.stdout and "0 skipped" in core_missing.stdout)
    full_missing = run("--full")
    check("portable full mode also excludes external-backed suites",
          full_missing.returncode == 0
          and "external:" not in full_missing.stdout and "0 skipped" in full_missing.stdout)
    check("core/full children explicitly disable opportunistic external reads",
          "[PASS] portable_env: tests/portable_env.py" in core_missing.stdout
          and "[PASS] portable_env: tests/portable_env.py" in full_missing.stdout)

    required_missing = run("--required-external")
    check("required-external mode fails for the same missing source",
          required_missing.returncode == 1
          and "Required external prerequisite missing" in required_missing.stderr)

    external_root = root / "pinned-techstream"
    external_root.mkdir()
    local_present = run("--local", "--external-root", str(external_root))
    check("available local source executes and passes",
          local_present.returncode == 0
          and "[PASS] external: tests/pass.py" in local_present.stdout
          and "[SKIP] external_late_skip: tests/late_skip.py" in local_present.stdout)
    check("local children explicitly enable opportunistic external reads",
          "[PASS] local_env: tests/local_env.py" in local_present.stdout)

    agent_core = run("--agent", "--external-root", str(external_root))
    summary = json.loads(agent_core.stdout)
    core_result = next(item for item in summary["results"] if item["suite"] == "core")
    identity_result = next(item for item in summary["results"] if item["suite"] == "identity")
    check("agent mode is compact core, not the expensive local superset",
          agent_core.returncode == 0 and summary["mode"] == "core"
          and all(item["suite"] not in {"external", "external_late_skip"}
                  for item in summary["results"]))
    check("core agent summary reports nonzero raw assertions",
          core_result["assertions"]["passed"].get("raw_bytes", 0) > 0)
    check("identity hashes are counted separately",
          summary["assertions"]["passed_by_oracle"]["identity_hash"] > 0)
    check("identity-only suite cannot claim semantic verification",
          identity_result["semantic_status"] == "not_semantic")
    check("raw-byte suite can claim semantic verification",
          core_result["semantic_status"] == "verified")
    check("aggregate retains each suite's declared default oracle",
          core_result["oracle"] == "raw_bytes"
          and identity_result["oracle"] == "identity_hash")
    check("aggregate lists pass/fail/skip separately",
          all(key in summary for key in ("passed", "failed", "skipped")))
    check("aggregate reports per-test execution durations",
          "test_duration_seconds" in summary
          and all("duration_seconds" in item for item in summary["results"]))

    legacy = run("--suite", "legacy")
    check("legacy PASS: assertions are counted with the declared oracle",
          legacy.returncode == 0 and '"raw_bytes": 1' in legacy.stdout)

    printed_fail = run("--suite", "printed_fail")
    check("printed FAIL assertion overrides a zero process exit",
          printed_fail.returncode == 1
          and "printed 1 failed assertion" in printed_fail.stderr)

    required_late_skip = run(
        "--required-external", "--external-root", str(external_root)
    )
    check("required mode rejects a test-level exit-77 skip",
          required_late_skip.returncode == 1
          and "required external suite reported skip" in required_late_skip.stderr)

print(f"\nResults: {passed} passed, {failed} failed")
raise SystemExit(1 if failed else 0)
