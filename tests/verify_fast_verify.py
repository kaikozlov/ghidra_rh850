#!/usr/bin/env python3
"""Verify manifest ownership and pass/fail/skip/oracle runner semantics."""
from __future__ import annotations

import json
import re
import subprocess
import sys
import tempfile
import tomllib
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
RUNNER = REPO / "tools/fast_verify.py"
TEST_COMMAND = REPO / "tools/test"
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
check("canonical tools/test command is executable", TEST_COMMAND.is_file()
      and bool(TEST_COMMAND.stat().st_mode & 0o111))
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
check("FINDINGS.md is only a path on ledger infrastructure suites",
      all("docs/status/FINDINGS.md" not in entry.get("paths", [])
          or name in {"analysis_status", "knowledge_index"}
          for name, entry in suites.items()))
check("lifecycle Ghidra-adjacent suite is serial",
      suites.get("lifecycle", {}).get("serial") is True)
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
pending_paths = set(subprocess.check_output(
    ["git", "ls-files", "--others", "--exclude-standard"], cwd=REPO, text=True
).splitlines())
repository_paths = tracked_paths | pending_paths
untracked_manifest_paths = [
    (suite_name, kind, value)
    for suite_name, kind, value in manifest_paths
    if not (any(path.startswith(value) for path in repository_paths)
            if value.endswith("/") else value in repository_paths)
]
check(
    "every manifest change-routing path is tracked or a pending addition",
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
for target, command in (
    ("verify", "tools/test\n"),
    ("verify-core", "tools/test core"),
    ("verify-full", "tools/test full"),
    ("verify-local", "tools/test local"),
    ("verify-changed", "tools/test\n"),
    ("verify-agent", "tools/test --agent"),
    ("verify-required-external", "tools/test --required-external"),
):
    check(f"Make target {target} delegates to canonical tools/test command",
          f"{target}:" in makefile and command in makefile)
check("Make verify-one preserves exact legacy suite selection",
      'tools/test --suite "$(SUITE)"' in makefile)
check("Make verify-exploit is one tools/test invocation",
      "tools/test exploit_surface" in makefile
      and "tools/fast_verify.py --suite" not in makefile)
src = RUNNER.read_text(encoding="utf-8")
check("firmware is the only portable full invalidator",
      '"firmware/"' in src.split("PORTABLE_BROAD_INVALIDATORS", 1)[1].split(")", 1)[0]
      and "verification.toml" not in src.split("PORTABLE_BROAD_INVALIDATORS", 1)[1].split(")", 1)[0]
      and "pyproject.toml" not in src.split("PORTABLE_BROAD_INVALIDATORS", 1)[1].split(")", 1)[0])
check("portable tests may run concurrently", "ThreadPoolExecutor" in src)
check("live and external suites stay serial", "def suite_is_serial" in src)
check("default changed mode diffs working tree against HEAD",
      "working tree against HEAD" in src and "branch: bool = False" in src)


print("\n== isolated runner behavior ==")
with tempfile.TemporaryDirectory(prefix="verify-runner-") as directory:
    root = Path(directory)
    for subdir in ("tests", "docs/status", "docs/family", "data", "firmware", "scratch"):
        (root / subdir).mkdir(parents=True, exist_ok=True)
    outside = root / "outside"
    outside.mkdir()
    wrapper_plan = subprocess.run(
        [str(TEST_COMMAND), "plan", "fast_verify"],
        cwd=outside, capture_output=True, text=True,
    )
    check("tools/test works outside the repository directory",
          wrapper_plan.returncode == 0 and "fast_verify" in wrapper_plan.stdout,
          wrapper_plan.stderr.strip())
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
    for name in (
        "verify_alpha.py", "verify_beta.py", "verify_camry_one.py",
        "verify_camry_two.py", "verify_analysis_status.py", "verify_doc_links.py",
        "verify_knowledge_index.py", "verify_full_only.py", "verify_local_only.py",
        "verify_status_wide.py",
    ):
        (root / "tests" / name).write_text(
            "print('[PASS][raw_bytes] synthetic route')\n", encoding="utf-8"
        )
    text_files = {
        "docs/ahead.md": "baseline\n",
        "docs/dirty.md": "baseline\n",
        "scratch/rename_source.md": "rename baseline\n",
        "docs/alpha.md": "FIND-001 OQ-001\n",
        "docs/beta.md": "CORR-001\n",
        "docs/family/item.md": "baseline\n",
        "data/foo.json": "{}\n",
        "data/foo.json.backup": "{}\n",
        "firmware/input.bin": "firmware\n",
        "pyproject.toml": "[project]\nname='synthetic'\nversion='0'\n",
        "uv.lock": "version = 1\n",
        "docs/status/FINDINGS.md": (
            "| ID | Claim | Scope | Grade | Checked by | Canonical report |\n"
            "|---|---|---|---|---|---|\n"
            "| FIND-001 | alpha old | scope | verified | `verify_alpha.py` | alpha |\n"
            "| FIND-002 | beta old | scope | verified | `verify_beta.py` | beta |\n"
        ),
        "docs/status/OPEN_QUESTIONS.md": (
            "## Synthetic questions\n\n"
            "- **OQ-001 — Alpha old.** First line.\n"
            "  Continuation old OQ detail.\n"
            "  Cross-reference CORR-001 has old OQ wording.\n"
        ),
        "docs/status/CORRECTIONS.md": (
            "## Evidence-grade: disproved\n\n"
            "### CORR-001 — Beta old\n\n"
            "- **Wrong:** old statement.\n"
            "- **Right:** Continuation old CORR detail.\n"
            "- **Boundary:** OQ-001 has old CORR wording.\n"
        ),
        "docs/status/PRIORITIES.md": (
            "## Synthetic priority\n\n"
            "OQ-001 alpha old priority starts here and\n"
            "continues with old priority detail.\n"
        ),
    }
    for relative, content in text_files.items():
        (root / relative).write_text(content, encoding="utf-8")
    synthetic_manifest = root / "verification.toml"
    synthetic_manifest.write_text(
        """[verification]
default_oracle = "raw_bytes"
skip_exit_code = 77
gate_glob = "tests/*.py"
default_modes = ["core", "full", "local"]
aggregate_infrastructure_suites = ["analysis_status", "doc_links", "knowledge_index"]

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

[suite.alpha]
tests = ["tests/verify_alpha.py"]
paths = ["docs/ahead.md", "docs/alpha.md", "data/foo.json", "docs/status/FINDINGS.md", "docs/status/OPEN_QUESTIONS.md", "docs/status/CORRECTIONS.md", "docs/status/PRIORITIES.md"]

[suite.beta]
tests = ["tests/verify_beta.py"]
paths = ["docs/dirty.md", "docs/renamed.md", "data/foo.json.backup", "docs/beta.md", "docs/status/FINDINGS.md", "docs/status/OPEN_QUESTIONS.md", "docs/status/CORRECTIONS.md", "docs/status/PRIORITIES.md"]

[suite.camry_one]
tests = ["tests/verify_camry_one.py"]
paths = ["docs/untracked.md"]

[suite.camry_two]
tests = ["tests/verify_camry_two.py"]
paths = ["docs/family/"]

[suite.analysis_status]
tests = ["tests/verify_analysis_status.py"]
paths = ["docs/status/FINDINGS.md", "docs/status/OPEN_QUESTIONS.md"]

[suite.doc_links]
tests = ["tests/verify_doc_links.py"]
paths = ["docs/"]

[suite.knowledge_index]
tests = ["tests/verify_knowledge_index.py"]
paths = ["docs/status/FINDINGS.md", "docs/status/OPEN_QUESTIONS.md", "docs/status/CORRECTIONS.md"]

[suite.status_wide]
tests = ["tests/verify_status_wide.py"]
paths = ["docs/status/"]

[suite.full_only]
tests = ["tests/verify_full_only.py"]
paths = ["tests/verify_full_only.py"]
modes = ["full", "local"]

[suite.fast_verify]
tests = ["tests/pass.py"]
paths = ["verification.toml", "pyproject.toml", "uv.lock"]

[suite.ghidra_live]
tests = ["tests/verify_local_only.py"]
paths = ["tests/verify_local_only.py"]
modes = ["local"]
serial = true
""",
        encoding="utf-8",
    )

    def run(*args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(RUNNER), *args, "--repo-root", str(root),
             "--manifest", str(synthetic_manifest)],
            capture_output=True, text=True,
        )

    def selected_from_plan(proc: subprocess.CompletedProcess[str]) -> set[str]:
        return set(re.findall(r"^  ([a-z0-9_]+): \d+ test\(s\)", proc.stdout, re.MULTILINE))

    listed = run("list", "camry")
    check("list discovers a suite-prefix family with counts and modes",
          listed.returncode == 0
          and "Prefix 'camry': 2 suite(s), 2 test(s)" in listed.stdout
          and "camry_one: 1 test(s) modes=core,full,local" in listed.stdout)
    planned_family = run("plan", "camry")
    check("plan resolves a prefix without executing its tests",
          planned_family.returncode == 0
          and selected_from_plan(planned_family) == {"camry_one", "camry_two"}
          and "[PASS]" not in planned_family.stdout)
    planned_exact = run("plan", "alpha")
    check("exact suite ownership wins over prefix expansion",
          planned_exact.returncode == 0 and selected_from_plan(planned_exact) == {"alpha"})

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
    explicit_external_missing = run("external")
    check("explicit external suite fails closed when its prerequisite is missing",
          explicit_external_missing.returncode == 1
          and "Required external prerequisite missing" in explicit_external_missing.stderr)
    explicit_external_skip = run("external", "--allow-skips")
    check("explicit allow-skips restores optional external skip behavior",
          explicit_external_skip.returncode == 0
          and "[SKIP] external: tests/pass.py" in explicit_external_skip.stdout)

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
    legacy_prefix = run("--suite", "camry")
    check("legacy --suite preserves exact-only semantics",
          legacy_prefix.returncode == 2
          and "Unknown suite: camry" in legacy_prefix.stderr)

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

    def git(*args: str) -> str:
        return subprocess.check_output(["git", *args], cwd=root, text=True).strip()

    git("init", "-q")
    git("config", "user.name", "Verifier Test")
    git("config", "user.email", "verifier@example.invalid")
    git("add", ".")
    git("commit", "-qm", "baseline")
    branch = git("branch", "--show-current")
    git("branch", "upstream-base")
    git("config", f"branch.{branch}.remote", ".")
    git("config", f"branch.{branch}.merge", "refs/heads/upstream-base")

    (root / "docs/ahead.md").write_text("ahead commit\n", encoding="utf-8")
    git("add", "docs/ahead.md")
    git("commit", "-qm", "local ahead work")

    git("config", "--unset", f"branch.{branch}.remote")
    git("config", "--unset", f"branch.{branch}.merge")
    no_upstream = run("plan", "changed")
    check("working-tree changed mode does not require upstream",
          no_upstream.returncode == 0)
    branch_no_upstream = run("plan", "branch")
    check("branch mode without upstream requires an explicit committed-change base",
          branch_no_upstream.returncode == 1
          and "has no configured upstream" in branch_no_upstream.stderr
          and "--base <ref>" in branch_no_upstream.stderr)
    git("config", f"branch.{branch}.remote", ".")
    git("config", f"branch.{branch}.merge", "refs/heads/upstream-base")

    git("checkout", "-q", "--detach", "HEAD")
    detached = run("plan", "changed")
    check("working-tree changed mode works on detached HEAD",
          detached.returncode == 0)
    detached_branch = run("plan", "branch")
    check("branch mode on detached HEAD requires an explicit committed-change base",
          detached_branch.returncode == 1
          and "detached HEAD" in detached_branch.stderr
          and "--base <ref>" in detached_branch.stderr)
    git("checkout", "-q", branch)

    (root / "docs/dirty.md").write_text("dirty worktree\n", encoding="utf-8")
    (root / "docs/untracked.md").write_text("untracked worktree\n", encoding="utf-8")

    ahead_and_dirty = run("plan", "changed")
    ahead_and_dirty_names = selected_from_plan(ahead_and_dirty)
    check("default changed detection is working tree against HEAD",
          ahead_and_dirty.returncode == 0
          and "alpha" not in ahead_and_dirty_names
          and {"beta", "camry_one"} <= ahead_and_dirty_names
          and "working tree against HEAD" in ahead_and_dirty.stdout,
          str(sorted(ahead_and_dirty_names)))
    branch_plan = run("plan", "branch")
    branch_names = selected_from_plan(branch_plan)
    check("branch mode includes ahead commit, dirty file, and untracked file",
          branch_plan.returncode == 0
          and {"alpha", "beta", "camry_one"} <= branch_names
          and "merge-base with upstream-base" in branch_plan.stdout,
          str(sorted(branch_names)))
    explicit_head = run("plan", "changed", "--base", "HEAD")
    explicit_head_names = selected_from_plan(explicit_head)
    check("explicit --base HEAD matches the working-tree default",
          explicit_head.returncode == 0
          and "alpha" not in explicit_head_names
          and {"beta", "camry_one"} <= explicit_head_names,
          str(sorted(explicit_head_names)))

    (root / "docs/dirty.md").write_text("baseline\n", encoding="utf-8")
    (root / "docs/untracked.md").unlink()
    no_changes = run("plan", "changed", "--base", "HEAD")
    check("clean explicit-base plan is fast and reports zero selection",
          no_changes.returncode == 0 and "0 suites / 0 tests selected" in no_changes.stdout)

    (root / "docs/dirty.md").write_text("mapped change\n", encoding="utf-8")
    (root / "scratch/unowned.txt").write_text("unowned\n", encoding="utf-8")
    (root / "tests/verify_unowned_new.py").write_text(
        "print('[PASS][raw_bytes] should be manifest-owned')\n", encoding="utf-8"
    )
    mixed_unowned = run("plan", "changed", "--base", "HEAD")
    check("mixed owned and unowned changes fail closed",
          mixed_unowned.returncode == 2
          and "scratch/unowned.txt" in mixed_unowned.stderr
          and "tests/verify_unowned_new.py" in mixed_unowned.stderr)
    (root / "docs/dirty.md").write_text("baseline\n", encoding="utf-8")
    (root / "scratch/unowned.txt").unlink()
    (root / "tests/verify_unowned_new.py").unlink()

    (root / "tests/verify_alpha.py").unlink()
    toml_path = root / "verification.toml"
    toml_original = toml_path.read_text(encoding="utf-8")
    toml_path.write_text(
        toml_original.replace('tests = ["tests/verify_alpha.py"]\n', 'tests = ["tests/pass.py"]\n')
        .replace('paths = ["docs/ahead.md", "docs/alpha.md", "data/foo.json", "docs/status/FINDINGS.md", "docs/status/OPEN_QUESTIONS.md", "docs/status/CORRECTIONS.md", "docs/status/PRIORITIES.md"]\n',
                 'paths = ["docs/ahead.md", "docs/alpha.md", "data/foo.json"]\n'),
        encoding="utf-8",
    )
    (root / "docs/dirty.md").write_text("mapped after retirement\n", encoding="utf-8")
    retired_plan = run("plan", "changed", "--base", "HEAD")
    check("retired verify_*.py deletions are not ownership misses",
          retired_plan.returncode == 0
          and "tests/verify_alpha.py" not in retired_plan.stderr
          and "retired test file(s): tests/verify_alpha.py" in retired_plan.stdout,
          retired_plan.stderr.strip() or retired_plan.stdout[-400:])
    (root / "docs/dirty.md").write_text("baseline\n", encoding="utf-8")
    toml_path.write_text(toml_original, encoding="utf-8")
    (root / "tests/verify_alpha.py").write_text(
        "print('[PASS][raw_bytes] synthetic route')\n", encoding="utf-8"
    )

    (root / "scratch/rename_source.md").rename(root / "docs/renamed.md")
    renamed = run("plan", "changed", "--base", "HEAD")
    check("rename detection retains an unowned source path",
          renamed.returncode == 2
          and "scratch/rename_source.md" in renamed.stderr)
    (root / "docs/renamed.md").rename(root / "scratch/rename_source.md")

    (root / "external").mkdir(exist_ok=True)
    (root / "external/input.bin").write_text("external change\n", encoding="utf-8")
    changed_external = run("--changed", "--base", "HEAD")
    check("changed external-backed suites fail closed on missing prerequisites",
          changed_external.returncode == 1
          and "Required external prerequisite missing" in changed_external.stderr)
    changed_external_skips = run("--changed", "--base", "HEAD", "--allow-skips")
    check("changed mode permits missing external prerequisites only with allow-skips",
          changed_external_skips.returncode == 0
          and "[SKIP] external:" in changed_external_skips.stdout
          and "[SKIP] external_late_skip:" in changed_external_skips.stdout)
    (root / "external/input.bin").unlink()

    (root / "data/foo.json.backup").write_text('{"changed": true}\n', encoding="utf-8")
    exact_file = run("plan", "changed", "--base", "HEAD")
    check("exact file patterns do not match longer backup names",
          exact_file.returncode == 0
          and selected_from_plan(exact_file) == {"beta"},
          str(sorted(selected_from_plan(exact_file))))
    (root / "data/foo.json.backup").write_text("{}\n", encoding="utf-8")

    (root / "docs/family/item.md").write_text("directory change\n", encoding="utf-8")
    directory_match = run("plan", "changed", "--base", "HEAD")
    check("trailing-slash directory patterns match descendants",
          directory_match.returncode == 0
          and {"camry_two", "doc_links"} <= selected_from_plan(directory_match))
    (root / "docs/family/item.md").write_text("baseline\n", encoding="utf-8")

    firmware = root / "firmware/input.bin"
    firmware_original = firmware.read_text(encoding="utf-8")
    firmware.write_text(firmware_original + "# changed\n", encoding="utf-8")
    broad = run("plan", "changed", "--base", "HEAD")
    broad_names = selected_from_plan(broad)
    check("firmware/ is a portable full invalidator",
          broad.returncode == 0
          and "full_only" in broad_names
          and "local_only" not in broad_names
          and "external" not in broad_names,
          str(sorted(broad_names)))
    firmware.write_text(firmware_original, encoding="utf-8")

    for owned in ("verification.toml", "pyproject.toml", "uv.lock"):
        path = root / owned
        original = path.read_text(encoding="utf-8")
        path.write_text(original + "# changed\n", encoding="utf-8")
        mapped = run("plan", "changed", "--base", "HEAD")
        mapped_names = selected_from_plan(mapped)
        check(f"{owned} owns fast_verify rather than the full tier",
              mapped.returncode == 0
              and mapped_names == {"fast_verify"}
              and "full_only" not in mapped_names,
              str(sorted(mapped_names)))
        path.write_text(original, encoding="utf-8")

    unioned = run("plan", "alpha")
    check("exact suite ownership still plans a single suite",
          unioned.returncode == 0 and selected_from_plan(unioned) == {"alpha"})
    unioned_run = run("identity", "legacy")
    check("multiple suite names are unioned in one invocation",
          unioned_run.returncode == 0
          and "[PASS] identity:" in unioned_run.stdout
          and "[PASS] legacy:" in unioned_run.stdout)

    serial_src = RUNNER.read_text(encoding="utf-8")
    check("explicit serial flag is honored",
          "entry.get(\"serial\")" in serial_src or "entry.get('serial')" in serial_src)

    findings = root / "docs/status/FINDINGS.md"
    findings_original = findings.read_text(encoding="utf-8")
    findings.write_text(findings_original.replace("beta old", "beta new"), encoding="utf-8")
    findings_plan = run("plan", "changed", "--base", "HEAD")
    findings_names = selected_from_plan(findings_plan)
    check("FINDINGS changed-row routing uses Checked-by ownership narrowly",
          findings_plan.returncode == 0
          and findings_names == {"analysis_status", "beta", "doc_links", "knowledge_index"}
          and "content-aware stable-ID/test routing" in findings_plan.stdout,
          str(sorted(findings_names)))
    check("aggregate ledgers reached through a directory are excluded from ID scans",
          "status_wide" not in findings_names)
    findings.write_text(findings_original, encoding="utf-8")

    aggregate_cases = (
        ("OPEN_QUESTIONS.md", "Continuation old OQ detail", "Continuation new OQ detail", "alpha"),
        ("CORRECTIONS.md", "Continuation old CORR detail", "Continuation new CORR detail", "beta"),
        ("PRIORITIES.md", "old priority detail", "new priority detail", "alpha"),
    )
    for filename, old, new, owner in aggregate_cases:
        path = root / "docs/status" / filename
        original = path.read_text(encoding="utf-8")
        path.write_text(original.replace(old, new), encoding="utf-8")
        routed = run("plan", "changed", "--base", "HEAD")
        routed_names = selected_from_plan(routed)
        check(f"{filename} multiline edit inherits its enclosing stable ID",
              routed.returncode == 0
              and routed_names == {"analysis_status", owner, "doc_links", "knowledge_index"},
              str(sorted(routed_names)))
        path.write_text(original, encoding="utf-8")

    cross_reference_cases = (
        ("OPEN_QUESTIONS.md", "old OQ wording", "new OQ wording"),
        ("CORRECTIONS.md", "old CORR wording", "new CORR wording"),
    )
    for filename, old, new in cross_reference_cases:
        path = root / "docs/status" / filename
        original = path.read_text(encoding="utf-8")
        path.write_text(original.replace(old, new), encoding="utf-8")
        routed = run("plan", "changed", "--base", "HEAD")
        routed_names = selected_from_plan(routed)
        check(f"{filename} cross-reference unions direct and enclosing IDs",
              routed.returncode == 0
              and routed_names == {
                  "alpha", "analysis_status", "beta", "doc_links", "knowledge_index"
              },
              str(sorted(routed_names)))
        path.write_text(original, encoding="utf-8")

    findings.write_text(findings_original + "\n## Structural heading\n", encoding="utf-8")
    structural = run("plan", "changed", "--base", "HEAD")
    structural_names = selected_from_plan(structural)
    check("structural aggregate-ledger edits fall back to broad path routing",
          structural.returncode == 0
          and {"alpha", "beta", "analysis_status", "doc_links", "knowledge_index"}
          <= structural_names
          and "status_wide" in structural_names
          and "broad fallback (structural change)" in structural.stdout,
          str(sorted(structural_names)))
    findings.write_text(findings_original, encoding="utf-8")

print(f"\nResults: {passed} passed, {failed} failed")
raise SystemExit(1 if failed else 0)
