#!/usr/bin/env python3
"""Test Ghidra wrapper markers, project-path guards, and finalization selection.

Uses a fixture CLI and dry-run finalization; no project is opened or promoted.
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

from tools import REPO_ROOT
REPO = REPO_ROOT

# Keep CLI and mutation marker fixtures outside the active workspace.
_FAKE_CLI_TMP = tempfile.TemporaryDirectory(prefix="ghidra-lifecycle-cli-")
_FAKE_CACHE = Path(_FAKE_CLI_TMP.name) / "cache"
_FIXTURE_WORK = Path(_FAKE_CLI_TMP.name) / "work"
_FAKE_CLI = _FAKE_CACHE / "ghidra-cli" / "ghidra"
_FAKE_CLI.parent.mkdir(parents=True)
_FAKE_CLI.write_text('#!/bin/sh\nprintf "%s\\n" "${GHIDRA_PROJECT_DIR-unset}"\n')
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
    if str(REPO / "tools" / "g") in cmd:
        merged_env["BUILD_WORK"] = str(_FIXTURE_WORK)
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
_REGISTRY = json.loads((REPO / "data" / "analysis_targets.json").read_text())
_DEFAULT_TARGET = _REGISTRY["default_target"]
_DEFAULT_ROW = _REGISTRY["targets"][_DEFAULT_TARGET]
DEFAULT_PROJECT = (REPO / _DEFAULT_ROW["work_dir"]).resolve()
DEFAULT_PROJECT_NAME = _DEFAULT_ROW["project_name"]


def marker_for(project: Path) -> Path:
    key = hashlib.sha256(str(project.resolve()).encode()).hexdigest()
    return _FIXTURE_WORK / "ghidra-session-dirty" / f"{key}.marker"


print("== tools/g lifecycle tests ==")

# --- Test 1: session-status is environment-independent ------------------------
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

# Help must bypass Java and project setup even when the command can mutate.
with tempfile.TemporaryDirectory() as td:
    project = Path(td) / "missing"
    help_env = {
        "GHIDRA_AGENT": "0",
        "GHIDRA_PROJECT": str(project),
        "GHIDRA_NO_BOOTSTRAP": "0",
        "GHIDRA_ENV_FORCE_REBUILD": "1",
        "GHIDRA_INSTALL_SCRIPT": str(Path(td) / "missing-installer"),
    }
    for args in (
        [],
        ["help"],
        ["--help"],
        ["-h"],
        ["help", "function", "rename"],
        ["fn", "rename", "--help"],
        ["batch", "-h"],
        ["help", "session-status"],
        ["session-status", "--help"],
    ):
        result = run(["bash", str(REPO / "tools" / "g"), *args], env=help_env, timeout=10)
        check(
            f"tools/g {' '.join(args)} works without Java or a working project",
            result.returncode == 0 and not project.exists() and not _FIXTURE_WORK.exists(),
            result.stderr,
        )

# Project paths are data, never Python source. This payload executed before the
# argv-based canonicalization regression fix.
injection_marker = Path(_FAKE_CLI_TMP.name) / "path-injection"
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
        result.returncode == 0 and result.stdout.strip() == "unset",
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

with tempfile.TemporaryDirectory() as td:
    alternate_project = Path(td).resolve()
    (alternate_project / f"{DEFAULT_PROJECT_NAME}.rep").mkdir()
    alternate_marker = marker_for(alternate_project)
    alternate_marker.unlink(missing_ok=True)
    default_marker = marker_for(DEFAULT_PROJECT)
    mutation_env = {
        "GHIDRA_ANALYSIS_TARGET": _DEFAULT_TARGET,
        "GHIDRA_NO_BOOTSTRAP": "1",
        "GHIDRA_PROJECT": str(alternate_project),
    }
    for args, mutates in (
        (["function", "rename", "old", "new"], True),
        (["batch", "--read-only", "commands.txt"], False),
        (["batch", "commands.txt"], True),
        (["batch", "--", "--read-only"], True),
        (["batch", "--", "--help"], True),
        (["fn", "rename", "old", "new"], True),
        (["types", "rm", "old"], True),
        (["analysis"], True),
        (["mv", "old", "new"], True),
        (["script", "python", "pass"], True),
        (["scripts", "java", "return;"], True),
    ):
        result = run(
            ["bash", str(REPO / "tools" / "g"), *args],
            env=mutation_env,
            timeout=10,
        )
        if mutates:
            check(
                f"{' '.join(args)} writes a project-affine mutation marker",
                result.returncode == 0 and alternate_marker.is_file()
                and f"project={alternate_project}" in alternate_marker.read_text(),
                result.stderr,
            )
        else:
            check(
                f"{' '.join(args)} does not write a mutation marker",
                result.returncode == 0 and not alternate_marker.exists(),
                result.stderr,
            )
        alternate_marker.unlink(missing_ok=True)
    check("alternate-project commands leave the default project marker unchanged",
          not default_marker.exists())

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

print()
if failed:
    print(f"FAILED ({failed} check(s) failed)", file=sys.stderr)
    sys.exit(1)
print(f"All {passed} check(s) passed.")
