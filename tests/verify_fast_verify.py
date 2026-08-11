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
check("manifest default oracle is valid", default_oracle in ALLOWED_ORACLES)
check("all suite oracle classifications are valid",
      all(entry.get("oracle", default_oracle) in ALLOWED_ORACLES for entry in suites.values()))
external_names = set(manifest.get("external", {}))
check("every external requirement resolves to manifest metadata",
      all(set(entry.get("requires_external", [])) <= external_names for entry in suites.values()))
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
    synthetic_manifest = root / "verification.toml"
    synthetic_manifest.write_text(
        """[verification]
default_oracle = "raw_bytes"
skip_exit_code = 77
gate_glob = "tests/*.py"

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

[suite.external]
tests = ["tests/pass.py"]
paths = ["external/"]
requires_external = ["techstream_v18"]
oracle = "raw_bytes"

[suite.external_late_skip]
tests = ["tests/late_skip.py"]
paths = ["external/"]
requires_external = ["techstream_v18"]
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
    check("absent external source is a skip, not a pass",
          "[SKIP] external" in core_missing.stdout and "2 skipped" in core_missing.stdout)

    required_missing = run("--required-external")
    check("required-external mode fails for the same missing source",
          required_missing.returncode == 1
          and "Required external prerequisite missing" in required_missing.stderr)

    external_root = root / "pinned-techstream"
    external_root.mkdir()
    local_present = run("--agent", "--external-root", str(external_root))
    summary = json.loads(local_present.stdout)
    external_result = next(item for item in summary["results"] if item["suite"] == "external")
    late_skip_result = next(
        item for item in summary["results"] if item["suite"] == "external_late_skip"
    )
    identity_result = next(item for item in summary["results"] if item["suite"] == "identity")
    check("available local source executes and passes",
          local_present.returncode == 0 and external_result["status"] == "pass"
          and late_skip_result["status"] == "skip")
    check("available source reports nonzero raw assertions",
          external_result["assertions"]["passed"].get("raw_bytes", 0) > 0)
    check("identity hashes are counted separately",
          summary["assertions"]["passed_by_oracle"]["identity_hash"] > 0)
    check("identity-only suite cannot claim semantic verification",
          identity_result["semantic_status"] == "not_semantic")
    check("raw-byte suite can claim semantic verification",
          external_result["semantic_status"] == "verified")
    check("aggregate retains each suite's declared default oracle",
          external_result["oracle"] == "raw_bytes"
          and identity_result["oracle"] == "identity_hash")
    check("aggregate lists pass/fail/skip separately",
          all(key in summary for key in ("passed", "failed", "skipped")))

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
