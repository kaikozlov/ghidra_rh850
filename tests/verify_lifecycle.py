#!/usr/bin/env python3
"""Test Ghidra wrapper markers, project-path guards, and finalization selection.

Uses a fixture CLI and dry-run finalization; no project is opened or promoted.
"""
from __future__ import annotations

import atexit
import hashlib
import json
import os
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
_REGISTRY = json.loads((REPO / "data" / "analysis_targets.json").read_text())
_DEFAULT_TARGET = _REGISTRY["default_target"]
_DEFAULT_ROW = _REGISTRY["targets"][_DEFAULT_TARGET]
DEFAULT_PROJECT = (REPO / _DEFAULT_ROW["work_dir"]).resolve()
DEFAULT_PROJECT_NAME = _DEFAULT_ROW["project_name"]


def marker_for(project: Path) -> Path:
    key = hashlib.sha256(str(project.resolve()).encode()).hexdigest()
    return BUILD_WORK / "ghidra-session-dirty" / f"{key}.marker"


MARKER = marker_for(DEFAULT_PROJECT)
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

# --- Test 1: session-status is environment-independent ------------------------
# We need GHIDRA_NO_BOOTSTRAP=1 to skip the processor env bootstrap (which needs
# Ghidra). session-status should work without the full env.
remove_marker()
result = run(
    ["bash", str(REPO / "tools" / "g"), "session-status"],
    env={"GHIDRA_NO_BOOTSTRAP": "1", "GHIDRA_AGENT": "1"},
    timeout=10,
)
check("session-status runs without daemon", result.returncode == 0, result.stderr)
if result.returncode == 0:
    try:
        status = json.loads(result.stdout.strip())
        check("session-status reports a valid daemon state",
              status.get("daemon", {}).get("state") in {"running", "stopped"})
    except json.JSONDecodeError:
        check("session-status JSON parse", False, result.stdout[:200])

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
        "--projects-dir", str(REPO / "projects"), "--help",
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
    ["bash", str(REPO / "tools" / "g"), "project", "delete", DEFAULT_PROJECT_NAME],
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
            "bash", str(REPO / "tools" / "project" / "snapshot_project.sh"),
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
    ["bash", str(REPO / "tools" / "project" / "export_ghidra_project.sh"), "project-inventory", str(inventory_baseline)],
    timeout=10,
)
check(
    "inventory generation cannot overwrite the tracked baseline",
    result.returncode != 0 and inventory_baseline.read_bytes() == inventory_before,
    result.stderr,
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
result = run(
    ["bash", str(REPO / "tools" / "g"), "batch", "--read-only", "--help"],
    env={"GHIDRA_NO_BOOTSTRAP": "1"},
    timeout=10,
)
check(
    "preflight-enforced read-only batch does not write the session marker",
    result.returncode == 0 and not mutation_marker.exists(),
    result.stderr,
)
result = run(
    ["bash", str(REPO / "tools" / "g"), "batch", "--help"],
    env={"GHIDRA_NO_BOOTSTRAP": "1"},
    timeout=10,
)
check(
    "ordinary batch remains conservatively mutation-marked",
    result.returncode == 0 and mutation_marker.is_file(),
    result.stderr,
)
mutation_marker.unlink(missing_ok=True)
result = run(
    ["bash", str(REPO / "tools" / "g"), "batch", "--", "--read-only", "--help"],
    env={"GHIDRA_NO_BOOTSTRAP": "1"},
    timeout=10,
)
check(
    "batch filename cannot spoof the read-only marker exemption",
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

# --- Test 5: Refuses committed projects/ via GHIDRA_PROJECT --------------------
result = run(
    ["bash", str(REPO / "tools" / "g"), "decompile", "0x0"],
    env={"GHIDRA_PROJECT": str(REPO / "projects")},
    timeout=10,
)
check(
    "Refuses committed projects/ via GHIDRA_PROJECT",
    result.returncode != 0 and "REFUSING" in result.stderr,
    f"rc={result.returncode}, stderr={result.stderr[:200]}",
)

# Also test subdirectory of project/
result = run(
    ["bash", str(REPO / "tools" / "g"), "decompile", "0x0"],
    env={"GHIDRA_PROJECT": str(REPO / "projects" / "subdir")},
    timeout=10,
)
check(
    "Refuses projects/ subdir via GHIDRA_PROJECT",
    result.returncode != 0 and "REFUSING" in result.stderr,
    f"rc={result.returncode}, stderr={result.stderr[:200]}",
)

# --- Test 6: explicit finalization cannot skip a marker-free rebuild ----------
remove_marker()
divergent_project = (BUILD_WORK / "phase-i-rebuild-a").resolve()
result = run(
    ["bash", str(REPO / "tools" / "project" / "finalize_project.sh"), "--dry-run"],
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


rebuild_unsafe = run([
    "bash", str(REPO / "tools" / "project" / "rebuild_project.sh"),
    "--project-dir", str(REPO / "projects"), "--force",
])
check(
    "rebuild refuses committed and external destinations before deletion",
    rebuild_unsafe.returncode != 0 and "outside" in rebuild_unsafe.stderr,
    rebuild_unsafe.stderr,
)


# Cleanup
remove_marker()

print()
if failed:
    print(f"FAILED ({failed} check(s) failed)", file=sys.stderr)
    sys.exit(1)
print(f"All {passed} check(s) passed.")
