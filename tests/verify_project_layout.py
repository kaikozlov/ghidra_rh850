#!/usr/bin/env python3
"""Behavioral tests for committed/working Ghidra project layout conversion."""
from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
TOOL = REPO / "tools" / "project_layout.py"
NAME = "rh850_p1me_mapped"

passed = 0
failed = 0


def check(name: str, condition: bool, detail: str = "") -> None:
    global passed, failed
    if condition:
        passed += 1
        print(f"[PASS] {name}")
    else:
        failed += 1
        suffix = f": {detail}" if detail else ""
        print(f"[FAIL] {name}{suffix}")


def run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(TOOL), *args],
        cwd=REPO,
        text=True,
        capture_output=True,
    )


print("== project snapshot layout ==")

with tempfile.TemporaryDirectory() as td:
    root = Path(td)
    snapshot = root / "snapshot"
    working = root / "working"
    packed = root / "packed"
    snapshot.mkdir()
    (snapshot / f"{NAME}.gpr.snapshot").write_text("")
    rep = snapshot / f"{NAME}.rep.snapshot"
    rep.mkdir()
    (rep / "project.prp").write_text("fixture")
    (snapshot / "processor_manifest.json").write_text("{}\n")
    (snapshot / ".gitignore").write_text("*.lock\n")

    result = run(
        "materialize",
        "--snapshot-dir", str(snapshot),
        "--project-dir", str(working),
        "--project-name", NAME,
    )
    check("materialize succeeds", result.returncode == 0, result.stderr)
    check("materialize restores live .gpr", (working / f"{NAME}.gpr").is_file())
    check("materialize restores live .rep", (working / f"{NAME}.rep").is_dir())
    check("materialize removes snapshot suffixes", not list(working.glob("*.snapshot")))
    check("materialize copies metadata", (working / "processor_manifest.json").is_file())

    live_rep = working / f"{NAME}.rep"
    (live_rep / ".lock").write_text("transient")
    (live_rep / "checkout.dat").write_text("absolute path and timestamp")
    (live_rep / "tmp123").write_text("transient")

    result = run(
        "pack",
        "--project-dir", str(working),
        "--snapshot-dir", str(packed),
        "--project-name", NAME,
    )
    check("pack succeeds", result.returncode == 0, result.stderr)
    check("pack creates .gpr.snapshot", (packed / f"{NAME}.gpr.snapshot").is_file())
    check("pack creates .rep.snapshot", (packed / f"{NAME}.rep.snapshot").is_dir())
    check("pack leaves no live .gpr", not (packed / f"{NAME}.gpr").exists())
    check("pack leaves no live .rep", not (packed / f"{NAME}.rep").exists())
    check("pack preserves repository metadata", (packed / "processor_manifest.json").is_file())
    packed_rep = packed / f"{NAME}.rep.snapshot"
    check("pack excludes .lock", not (packed_rep / ".lock").exists())
    check("pack excludes checkout state", not (packed_rep / "checkout.dat").exists())
    check("pack excludes tmp files", not (packed_rep / "tmp123").exists())

    result = run(
        "validate-snapshot",
        "--snapshot-dir", str(packed),
        "--project-name", NAME,
    )
    check("packed snapshot validates", result.returncode == 0, result.stderr)

    # A live project in a snapshot directory must fail closed.
    packed.mkdir(exist_ok=True)
    (packed / f"{NAME}.gpr").write_text("")
    result = run(
        "validate-snapshot",
        "--snapshot-dir", str(packed),
        "--project-name", NAME,
    )
    check(
        "snapshot validation rejects live Ghidra names",
        result.returncode != 0 and "live Ghidra project" in result.stderr,
        result.stderr,
    )

    # Refuse accidental in-place conversion: source and destination must differ.
    result = run(
        "materialize",
        "--snapshot-dir", str(snapshot),
        "--project-dir", str(snapshot),
        "--project-name", NAME,
    )
    check("materialize rejects in-place conversion", result.returncode != 0)

    nested_source = root / "nested-source"
    nested_source.mkdir()
    (nested_source / f"{NAME}.gpr").write_text("")
    (nested_source / f"{NAME}.rep").mkdir()
    result = run(
        "pack",
        "--project-dir", str(nested_source),
        "--snapshot-dir", str(nested_source / "snapshot"),
        "--project-name", NAME,
    )
    check(
        "pack rejects destination nested inside source",
        result.returncode != 0 and "must not be nested" in result.stderr,
        result.stderr,
    )

    external = root / "external"
    external.mkdir()
    external_gpr = external / "external.gpr"
    external_gpr.write_text("outside")
    external_rep = external / "external.rep"
    external_rep.mkdir()

    linked_snapshot = root / "linked-snapshot"
    linked_snapshot.mkdir()
    (linked_snapshot / f"{NAME}.gpr.snapshot").symlink_to(external_gpr)
    (linked_snapshot / f"{NAME}.rep.snapshot").symlink_to(
        external_rep, target_is_directory=True
    )
    result = run(
        "materialize",
        "--snapshot-dir", str(linked_snapshot),
        "--project-dir", str(root / "linked-working"),
        "--project-name", NAME,
    )
    check("materialize rejects symlinked snapshot objects", result.returncode != 0)

    linked_working = root / "linked-live"
    linked_working.mkdir()
    (linked_working / f"{NAME}.gpr").symlink_to(external_gpr)
    (linked_working / f"{NAME}.rep").symlink_to(
        external_rep, target_is_directory=True
    )
    result = run(
        "pack",
        "--project-dir", str(linked_working),
        "--snapshot-dir", str(root / "linked-packed"),
        "--project-name", NAME,
    )
    check("pack rejects symlinked live project objects", result.returncode != 0)

    external_destination = root / "external-destination"
    external_destination.mkdir()
    linked_destination = root / "linked-destination"
    linked_destination.symlink_to(external_destination, target_is_directory=True)
    result = run(
        "materialize",
        "--snapshot-dir", str(snapshot),
        "--project-dir", str(linked_destination),
        "--project-name", NAME,
    )
    check(
        "materialize rejects a symlinked destination root",
        result.returncode != 0 and not any(external_destination.iterdir()),
    )

print("== committed snapshot repository invariant ==")
if TOOL.exists():
    result = run(
        "validate-snapshot",
        "--snapshot-dir", str(REPO / "project"),
        "--project-name", NAME,
    )
    check("repository project/ uses non-live names", result.returncode == 0, result.stderr)
else:
    check("project layout tool exists", False, str(TOOL))

print()
if failed:
    print(f"FAILED: {failed} check(s)", file=sys.stderr)
    raise SystemExit(1)
print(f"All {passed} checks passed.")
