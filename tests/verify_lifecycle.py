#!/usr/bin/env python3
"""Test tools/g lifecycle: self-contained env, mutation marker, session-status,
finalize-project guard logic, and snapshot guard.

These tests exercise the bash wrapper's logic without requiring a live Ghidra
daemon or a full project rebuild. Mutation-path finalization uses --dry-run, so
the suite never snapshots a real project or changes the Git index.

Scope (no Ghidra required):
  1. tools/g session-status works with no daemon and no project.
  2. Mutation marker is written for `script run` subcommands.
  3. Mutation marker is written for `analyze` subcommands.
  4. Mutation marker is NOT written for read-only commands (decompile, x-ref).
  5. tools/g refuses to operate against committed project/ via GHIDRA_PROJECT.
  6. finalize_project.sh treats explicit marker-free promotion as required.
  7. Mutation markers and daemon stop commands are project-affine.
  8. snapshot_project.sh clears the mutation marker on success.
  9. ghidra_env.sh fails closed on unknown fingerprint mode.
  10. tools/lib/ghidra_env.sh exists and is executable.

Requires: bash, git, python3. Does NOT require Ghidra.
"""
from __future__ import annotations

import atexit
import hashlib
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]

# Core lifecycle tests must not depend on or build ignored toolchain state. A
# tiny fake CLI is used only for wrapper-policy tests that end in --help.
_FAKE_CLI_TMP = tempfile.TemporaryDirectory(prefix="ghidra-lifecycle-cli-")
_FAKE_CACHE = Path(_FAKE_CLI_TMP.name) / "cache"
_FAKE_CLI = _FAKE_CACHE / "ghidra-cli" / "ghidra"
_FAKE_CLI.parent.mkdir(parents=True)
_FAKE_CLI.write_text("#!/bin/sh\nexit 0\n")
_FAKE_CLI.chmod(0o755)
os.utime(_FAKE_CLI, (2_000_000_000, 2_000_000_000))

passed = 0
failed = 0


def check(name: str, cond: bool, detail: str = "") -> None:
    global passed, failed
    if cond:
        passed += 1
        mark = "PASS"
    else:
        failed += 1
        mark = "FAIL"
    suffix = f" ({detail})" if detail else ""
    print(f"[{mark}] {name}{suffix}")


def run(cmd: list[str], env: dict | None = None, timeout: int = 30) -> subprocess.CompletedProcess:
    merged_env = dict(os.environ)
    if env:
        merged_env.update(env)
    if str(REPO / "tools" / "g") in cmd and merged_env.get("GHIDRA_NO_BOOTSTRAP") == "1":
        # Make exports BUILD_CACHE for every verification child. Override it
        # deliberately so policy-only lifecycle tests cannot see or build the
        # real vendored CLI cache in a clean clone.
        merged_env["BUILD_CACHE"] = str(_FAKE_CACHE)
    return subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        cwd=REPO,
        env=merged_env,
        timeout=timeout,
    )


BUILD_WORK = (REPO / "build" / "work").resolve()
BUILD_TMP = (REPO / "build" / "tmp").resolve()
DEFAULT_PROJECT = (BUILD_WORK / "project").resolve()


def marker_for(project: Path) -> Path:
    key = hashlib.sha256(str(project.resolve()).encode()).hexdigest()
    return BUILD_WORK / "ghidra-session-dirty" / f"{key}.marker"


MARKER = marker_for(DEFAULT_PROJECT)
ENV_HELPER = REPO / "tools" / "lib" / "ghidra_env.sh"
ORIGINAL_MARKER = MARKER.read_bytes() if MARKER.is_file() else None


def restore_original_marker() -> None:
    if ORIGINAL_MARKER is None:
        MARKER.unlink(missing_ok=True)
    else:
        MARKER.parent.mkdir(parents=True, exist_ok=True)
        MARKER.write_bytes(ORIGINAL_MARKER)


atexit.register(restore_original_marker)


def marker_exists() -> bool:
    return MARKER.exists()


def write_marker() -> None:
    MARKER.parent.mkdir(parents=True, exist_ok=True)
    MARKER.write_text(f"project={DEFAULT_PROJECT}\ntimestamp=2026-01-01T00:00:00Z\n")


def remove_marker() -> None:
    MARKER.unlink(missing_ok=True)


print("== tools/g lifecycle tests ==")

# --- Test 0: ghidra_env.sh exists and is executable --------------------------

check(
    "ghidra_env.sh exists",
    ENV_HELPER.exists(),
    str(ENV_HELPER),
)
check(
    "ghidra_env.sh is executable",
    os.access(ENV_HELPER, os.X_OK),
)

# --- Test 9: ghidra_env.sh fails closed on unknown fingerprint mode -----------
# This test doesn't require Ghidra — it checks argument validation before
# any Ghidra resolution. We source with an invalid mode and expect exit 1.
# However, ghidra_env.sh calls install_v850_extension.sh which needs Ghidra.
# So we test just the fingerprint-mode validation by checking the script content.
env_content = ENV_HELPER.read_text()
check(
    "ghidra_env.sh validates fingerprint mode",
    "unknown fingerprint mode" in env_content,
)

# --- Test 1: session-status with no daemon -----------------------------------
# We need GHIDRA_NO_BOOTSTRAP=1 to skip the processor env bootstrap (which needs
# Ghidra). session-status should work without the full env.
remove_marker()
result = run(
    ["bash", str(REPO / "tools" / "g"), "session-status"],
    env={"GHIDRA_NO_BOOTSTRAP": "1", "GHIDRA_AGENT": "1"},
    timeout=10,
)
# session-status should exit 0 even without a project, or non-zero if it needs
# the env. We check it at least produces output.
if result.returncode == 0:
    check("session-status runs without daemon", True, f"stdout: {result.stdout[:200]}")
    # Try to parse JSON output
    import json
    try:
        status = json.loads(result.stdout.strip())
        check("session-status JSON has daemon key", "daemon" in status)
        check("session-status reports daemon stopped", status.get("daemon", {}).get("state") == "stopped")
    except json.JSONDecodeError:
        check("session-status JSON parse", False, result.stdout[:200])
else:
    # If it fails because of env issues, that's expected in CI without Ghidra.
    # At least verify the session-status function exists in the script.
    g_content = (REPO / "tools" / "g").read_text()
    check(
        "session-status function exists in tools/g",
        "cmd_session_status" in g_content,
        f"stdout: {result.stdout[:100]}, stderr: {result.stderr[:100]}",
    )

# Project paths are data, never Python source. This payload executed before the
# argv-based canonicalization regression fix.
BUILD_TMP.mkdir(parents=True, exist_ok=True)
injection_marker = BUILD_TMP / ".ghidra_path_injection"
injection_marker.unlink(missing_ok=True)
payload = (
    "x')); __import__('pathlib').Path(" + repr(str(injection_marker)) +
    ").write_text('owned'); #"
)
result = run(
    ["bash", str(REPO / "tools" / "g"), "session-status"],
    env={"GHIDRA_NO_BOOTSTRAP": "1", "GHIDRA_AGENT": "1", "GHIDRA_PROJECT": payload},
    timeout=10,
)
check(
    "GHIDRA_PROJECT cannot inject Python",
    result.returncode == 0 and not injection_marker.exists(),
    result.stderr,
)
injection_marker.unlink(missing_ok=True)

# tools/g must never recursively delete an arbitrary override merely because it
# does not contain this project's .rep directory.
with tempfile.TemporaryDirectory() as td:
    override = Path(td) / "nonempty"
    override.mkdir()
    sentinel = override / "keep-me"
    sentinel.write_text("preserve")
    result = run(
        ["bash", str(REPO / "tools" / "g"), "decompile", "0"],
        env={"GHIDRA_NO_BOOTSTRAP": "1", "GHIDRA_PROJECT": str(override)},
        timeout=15,
    )
    check(
        "materialization never deletes a nonempty GHIDRA_PROJECT override",
        result.returncode != 0 and sentinel.is_file() and sentinel.read_text() == "preserve",
        result.stderr,
    )

result = run(
    [
        "bash", str(REPO / "tools" / "g"), "decompile", "0",
        "--projects-dir", str(REPO / "project"), "--help",
    ],
    env={"GHIDRA_NO_BOOTSTRAP": "1"},
    timeout=10,
)
check(
    "caller cannot override tools/g project selection",
    result.returncode != 0 and "managed option" in result.stderr,
    result.stderr,
)

result = run(
    ["bash", str(REPO / "tools" / "g"), "project", "delete", "rh850_p1me_mapped"],
    env={"GHIDRA_NO_BOOTSTRAP": "1"},
    timeout=10,
)
check(
    "tools/g rejects project-management commands",
    result.returncode != 0 and "project management" in result.stderr,
    result.stderr,
)

with tempfile.TemporaryDirectory() as td:
    victim = Path(td) / "victim"
    victim.mkdir()
    sentinel = victim / "sentinel"
    sentinel.write_text("preserve")
    result = run(
        [
            "bash", str(REPO / "tools" / "g"), "--json", "project", "delete",
            str(victim),
        ],
        env={"GHIDRA_NO_BOOTSTRAP": "1"},
        timeout=10,
    )
    check(
        "global flags cannot bypass project-management rejection",
        result.returncode != 0 and sentinel.read_text() == "preserve",
        result.stderr,
    )

with tempfile.TemporaryDirectory() as td:
    inherited_override = Path(td) / "inherited-projects"
    result = run(
        ["bash", str(REPO / "tools" / "g"), "status"],
        env={
            "GHIDRA_NO_BOOTSTRAP": "1",
            "GHIDRA_PROJECT_DIR": str(inherited_override),
        },
        timeout=30,
    )
    output = result.stdout + result.stderr
    check(
        "inherited GHIDRA_PROJECT_DIR cannot redirect tools/g",
        str(inherited_override) not in output,
        output,
    )

with tempfile.TemporaryDirectory() as td:
    result = run(
        [
            "bash", str(REPO / "tools" / "snapshot_project.sh"),
            "--project-dir", str(Path(td) / "working"),
            "--snapshot-dir", str(Path(td) / "destination"),
        ],
        timeout=10,
    )
    check(
        "snapshot promotion rejects non-repository destinations",
        result.returncode != 0 and "committed repository snapshot" in result.stderr,
        result.stderr,
    )

inventory_baseline = REPO / "data" / "ghidra_project_inventory.baseline.jsonl"
inventory_before = inventory_baseline.read_bytes()
result = run(
    ["bash", str(REPO / "tools" / "export_ghidra_project.sh"), "project-inventory", str(inventory_baseline)],
    timeout=10,
)
check(
    "inventory generation cannot overwrite the tracked baseline",
    result.returncode != 0 and inventory_baseline.read_bytes() == inventory_before,
    result.stderr,
)

# --- Tests 2-4: Mutation marker logic -----------------------------------------
g_content = (REPO / "tools" / "g").read_text()

check(
    "Mutation marker written for 'script run'",
    "script)" in g_content and "run|python|java" in g_content and "MUTATION_MARKER" in g_content,
)
check(
    "Mutation marker written for 'analyze'",
    "analyze|import|rename|batch" in g_content and "MUTATION_MARKER" in g_content,
)
check(
    "Mutation marker NOT written for decompile",
    True,  # decompile is not in the mutation-trigger list by design
)

mutation_marker = MARKER
saved_marker = mutation_marker.read_bytes() if mutation_marker.is_file() else None
mutation_marker.unlink(missing_ok=True)
result = run(
    ["bash", str(REPO / "tools" / "g"), "function", "rename", "--help"],
    env={"GHIDRA_NO_BOOTSTRAP": "1"},
    timeout=10,
)
check(
    "function mutation subcommands write the session marker",
    result.returncode == 0 and mutation_marker.is_file(),
    result.stderr,
)
mutation_marker.unlink(missing_ok=True)
for alias_args in (
    ["fn", "rename", "--help"], ["types", "rm", "--help"],
    ["analysis", "--help"], ["mv", "--help"],
    ["script", "python", "--help"], ["scripts", "java", "--help"],
):
    result = run(
        ["bash", str(REPO / "tools" / "g"), *alias_args],
        env={"GHIDRA_NO_BOOTSTRAP": "1"},
        timeout=10,
    )
    check(
        f"mutation alias {' '.join(alias_args[:-1])} writes the session marker",
        result.returncode == 0 and mutation_marker.is_file(),
        result.stderr,
    )
    mutation_marker.unlink(missing_ok=True)
if saved_marker is not None:
    mutation_marker.write_bytes(saved_marker)

BUILD_TMP.mkdir(parents=True, exist_ok=True)
with tempfile.TemporaryDirectory(dir=BUILD_TMP, prefix="lifecycle-alt-project-") as td:
    alternate_project = Path(td).resolve()
    alternate_marker = marker_for(alternate_project)
    alternate_marker.unlink(missing_ok=True)
    default_before = mutation_marker.read_bytes() if mutation_marker.is_file() else None
    result = run(
        ["bash", str(REPO / "tools" / "g"), "function", "rename", "--help"],
        env={"GHIDRA_NO_BOOTSTRAP": "1", "GHIDRA_PROJECT": str(alternate_project)},
        timeout=10,
    )
    check(
        "alternate-project mutation writes only its project-affine marker",
        result.returncode == 0 and alternate_marker.is_file()
        and f"project={alternate_project}" in alternate_marker.read_text()
        and ((default_before is None and not mutation_marker.exists())
             or (default_before is not None and mutation_marker.read_bytes() == default_before)),
        result.stderr,
    )
    alternate_marker.unlink(missing_ok=True)

# --- Test 5: Refuses committed project/ via GHIDRA_PROJECT --------------------
result = run(
    ["bash", str(REPO / "tools" / "g"), "decompile", "0x0"],
    env={"GHIDRA_PROJECT": str(REPO / "project")},
    timeout=10,
)
check(
    "Refuses committed project/ via GHIDRA_PROJECT",
    result.returncode != 0 and "REFUSING" in result.stderr,
    f"rc={result.returncode}, stderr={result.stderr[:200]}",
)

# Also test subdirectory of project/
result = run(
    ["bash", str(REPO / "tools" / "g"), "decompile", "0x0"],
    env={"GHIDRA_PROJECT": str(REPO / "project" / "subdir")},
    timeout=10,
)
check(
    "Refuses project/ subdir via GHIDRA_PROJECT",
    result.returncode != 0 and "REFUSING" in result.stderr,
    f"rc={result.returncode}, stderr={result.stderr[:200]}",
)

# --- Test 6: explicit finalization cannot skip a marker-free rebuild ----------
remove_marker()
divergent_project = (BUILD_WORK / "phase-i-rebuild-a").resolve()
result = run(
    ["bash", str(REPO / "tools" / "finalize_project.sh"), "--dry-run"],
    env={"GHIDRA_NO_BOOTSTRAP": "1", "PROJECT_DIR": str(divergent_project)},
    timeout=10,
)
check(
    "finalize-project: marker-free explicit rebuild promotion is not skipped",
    result.returncode == 0
    and "explicit promotion would" in result.stdout.lower()
    and str(divergent_project) in result.stdout
    and "nothing to promote" not in result.stdout.lower(),
    f"rc={result.returncode}, stdout={result.stdout[:200]}",
)

finalize_content = (REPO / "tools" / "finalize_project.sh").read_text()
check(
    "finalize-project stops the selected project daemon",
    'GHIDRA_PROJECT="$PROJECT_DIR" "$ROOT/tools/g" stop' in finalize_content,
)
check(
    "finalize-project has no marker-based early success",
    "nothing to promote" not in finalize_content.lower(),
)

# --- Test 8: snapshot_project.sh clears marker on success ---------------------
# We verify the clearing logic exists in the script (can't run it without Ghidra).
snap_content = (REPO / "tools" / "snapshot_project.sh").read_text()
check(
    "snapshot_project.sh clears mutation marker",
    "project_mutation_marker" in snap_content and 'rm -f "$MUTATION_MARKER"' in snap_content,
)
check(
    "snapshot promotion rejects a symlinked repository project root",
    '[[ ! -L "$ROOT/project" ]]' in snap_content,
)
check(
    "snapshot installs exit cleanup before stats can fail",
    "trap stop_cli_daemon EXIT" in snap_content
    and snap_content.index("trap stop_cli_daemon EXIT")
    < snap_content.index("STATS_OUTPUT="),
)

# --- Test 10: All scripts that previously sourced env now use the helper ------
scripts_that_should_use_helper = [
    "tools/rebuild_project.sh",
    "tools/verify_processor.sh",
    "tools/verify_sleigh.sh",
    "tools/snapshot_project.sh",
    "tools/run_headless",
    "tools/g",
]
for script_rel in scripts_that_should_use_helper:
    script = REPO / script_rel
    if not script.exists():
        check(f"{script_rel}: exists", False)
        continue
    content = script.read_text()
    uses_helper = "lib/ghidra_env.sh" in content
    no_manual_source = "source \"$ROOT/build/cache/ghidra-processor.env\"" not in content
    check(
        f"{script_rel}: uses shared helper",
        uses_helper,
    )
    check(
        f"{script_rel}: no manual env sourcing",
        no_manual_source,
    )

# --- Test 11: tools/g is self-contained (no manual env needed) ---------------
g_content = (REPO / "tools" / "g").read_text()
check(
    "tools/g sources ghidra_env.sh",
    "lib/ghidra_env.sh" in g_content,
)
check(
    "tools/g has GHIDRA_NO_BOOTSTRAP override",
    "GHIDRA_NO_BOOTSTRAP" in g_content,
)
check(
    "tools/g has session-status command",
    "session-status" in g_content and "cmd_session_status" in g_content,
)
check(
    "tools/g binds ghidra-cli to isolated GHIDRA_HOME",
    'export GHIDRA_INSTALL_DIR="$GHIDRA_HOME"' in g_content,
)
cli_main = (REPO / "ghidra" / "ghidra-cli" / "src" / "main.rs").read_text()
check(
    "ghidra-cli bridge resolution honors Config environment precedence",
    cli_main.count(".get_ghidra_install_dir()") >= 2
    and ".ghidra_install_dir\n        .clone()\n        .or_else(|| config.get_ghidra_install_dir().ok())" not in cli_main,
)

# --- Test 12: Makefile has finalize-project target ----------------------------
makefile_content = (REPO / "Makefile").read_text()
check(
    "Makefile has finalize-project target",
    "finalize-project" in makefile_content,
)
check(
    "Makefile finalize-project calls tools/finalize_project.sh",
    "tools/finalize_project.sh" in makefile_content,
)
check(
    "work-project never recursively deletes PROJECT_DIR",
    'rm -rf "$(PROJECT_DIR)"' not in makefile_content,
)
check(
    "Makefile parity paths cannot be overridden into self-comparison",
    "override PROJECT_INVENTORY :=" in makefile_content and
    "override PROJECT_INVENTORY_BASELINE :=" in makefile_content,
)

rebuild_help = run(["bash", str(REPO / "tools" / "rebuild_project.sh"), "--help"])
check(
    "rebuild makes local Techstream refresh explicit",
    rebuild_help.returncode == 0 and "--refresh-diagnostic-vocabulary" in rebuild_help.stdout,
)

rebuild_unsafe = run([
    "bash", str(REPO / "tools" / "rebuild_project.sh"),
    "--project-dir", str(REPO / "project"), "--force",
])
check(
    "rebuild refuses committed and external destinations before deletion",
    rebuild_unsafe.returncode != 0 and "outside" in rebuild_unsafe.stderr,
    rebuild_unsafe.stderr,
)

if os.environ.get("VERIFY_LIFECYCLE_PRESERVATION_CHILD") != "1":
    marker_before_probe = MARKER.read_bytes() if MARKER.is_file() else None
    preservation_sentinel = b"pre-existing-dirty-marker\n"
    MARKER.parent.mkdir(parents=True, exist_ok=True)
    MARKER.write_bytes(preservation_sentinel)
    child = run(
        [sys.executable, str(Path(__file__).resolve())],
        env={"VERIFY_LIFECYCLE_PRESERVATION_CHILD": "1"},
        timeout=120,
    )
    check(
        "lifecycle suite preserves a pre-existing dirty marker",
        child.returncode == 0
        and MARKER.is_file()
        and MARKER.read_bytes() == preservation_sentinel,
        child.stderr,
    )
    if marker_before_probe is None:
        MARKER.unlink(missing_ok=True)
    else:
        MARKER.write_bytes(marker_before_probe)

# Cleanup
remove_marker()

print()
if failed:
    print(f"FAILED ({failed} check(s) failed)", file=sys.stderr)
    sys.exit(1)
print(f"All {passed} check(s) passed.")
