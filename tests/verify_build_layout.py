#!/usr/bin/env python3
"""Verify the ignored build workspace boundary and clean-core contract."""
from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
import tomllib
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
passed = failed = 0


def check(name: str, condition: object, detail: str = "") -> None:
    global passed, failed
    ok = bool(condition)
    passed += int(ok); failed += int(not ok)
    print(f"[{'PASS' if ok else 'FAIL'}][raw_bytes] {name}" + (f" ({detail})" if detail else ""))


print("== canonical build namespaces ==")
make = (REPO / "Makefile").read_text()
for name in ("BUILD_ROOT", "BUILD_CACHE", "BUILD_WORK", "BUILD_OUT", "BUILD_LOGS", "BUILD_TMP"):
    check(f"Makefile defines {name}", f"{name} ?=" in make)
check("working Ghidra project lives under BUILD_WORK", "PROJECT_DIR ?= $(BUILD_WORK)/project" in make)
check("safe clean target only removes logs/tmp", "tools/build_layout.py clean logs tmp" in make)

build_cli = (REPO / "tools/build_ghidra_cli.sh").read_text(encoding="utf-8")
check(
    "vendored CLI Cargo target stays under BUILD_CACHE",
    'CARGO_TARGET_DIR="${CARGO_TARGET_DIR:-$BUILD_CACHE/ghidra-cli-target}"' in build_cli
    and 'BIN_SRC="$CARGO_TARGET_DIR/release/ghidra"' in build_cli
    and '$VENDOR/target/release/ghidra' not in build_cli,
)

# Operational source must never invent a sixth top-level build namespace.
allowed = {"cache", "work", "out", "logs", "tmp"}
scan_prefixes = ("Makefile", "tools/", "tests/", "exploit/", "ghidra/", ".github/", "AGENTS.md", "README.md", "docs/WORKFLOW.md")
bad: list[str] = []
# A few prose compounds are English, not filesystem namespaces.
prose_segments = {"workspace", "deploy", "reference", "CMAC"}
pat = re.compile(r"\bbuild/([A-Za-z0-9._-]+)")
structured_pat = re.compile(r"[\"']build[\"']\s*/\s*[\"']([A-Za-z0-9._-]+)[\"']")
tracked = subprocess.run(["git", "ls-files", "-z"], cwd=REPO, check=True, capture_output=True).stdout.split(b"\0")
for raw in tracked:
    if not raw:
        continue
    rel = raw.decode()
    if not any(rel == prefix or rel.startswith(prefix) for prefix in scan_prefixes):
        continue
    path = REPO / rel
    try:
        text = path.read_text()
    except UnicodeDecodeError:
        continue
    for m in pat.finditer(text):
        if m.group(1) not in allowed | prose_segments:
            bad.append(f"{rel}:{m.group(0)}")
    for m in structured_pat.finditer(text):
        if m.group(1) not in allowed | prose_segments:
            bad.append(f"{rel}:{m.group(0)}")
check("operational source uses only five build namespaces", not bad, repr(bad[:20]))

print("\n== core verification boundary ==")
manifest = tomllib.loads((REPO / "verification.toml").read_text())
core_external_paths: list[str] = []
for name, entry in manifest["suite"].items():
    if "core" not in entry.get("modes", ["core", "local"]):
        continue
    for path in entry.get("paths", []):
        if path.startswith(("build/", "REFERENCE/", "Techstream/unpacked/")):
            core_external_paths.append(f"{name}:{path}")
check("core suite ownership paths are tracked-repository paths", not core_external_paths, repr(core_external_paths))

live_tests = [
    "tests/verify_application_async_operation_queue_live.py",
    "tests/verify_application_proprietary_ba_live.py",
    "tests/verify_application_rdbi_disclosure_boundary.py",
    "tests/verify_application_rdbi_stale_response_live.py",
    "tests/verify_application_routine_control_1004_event_history_live.py",
    "tests/verify_application_routine_control_remaining_controls_live.py",
    "tests/verify_application_wdbi_0204_maintenance_live.py",
    "tests/verify_application_wdbi_2010_dead_state_live.py",
    "tests/verify_application_wdbi_2012_lifecycle_live.py",
    "tests/verify_application_wdbi_2013_2014_controls_live.py",
    "tests/verify_application_wdbi_surface_live.py",
    "tests/verify_semantic_coverage_live.py",
    "tests/verify_xcp_shadow_write_live.py",
]
owners = {test: (name, entry) for name, entry in manifest["suite"].items() for test in entry.get("tests", [])}
wrong = [(test, owners.get(test, (None, {}))[0], owners.get(test, (None, {}))[1].get("modes")) for test in live_tests
         if test not in owners or owners[test][1].get("modes") != ["local"]]
check("all live-project tests are local-only", not wrong, repr(wrong))

print("\n== promoted canonical inputs ==")
h = REPO / "community/albinoelephant/normalized/8965H1202000_CodeFlash.bin"
check("canonical Corolla H CodeFlash is tracked and exact", h.is_file() and h.stat().st_size == 0x100000 and hashlib.sha256(h.read_bytes()).hexdigest() == "0b47bdc1217835c839e3543e52eab40eb793650a9c159e46f6a9b365ea41a67f")
facts = json.loads((REPO / "data/external/opendbc/toyota_dbc_facts.json").read_text())
check("compact opendbc corroboration is commit/hash bound", facts["repository"]["commit"] == "c9b31d21bc396e8958891e271936bdbdf1a6ca93" and all(row["sha256"] for row in facts["sources"].values()))
for name, size, digest in (
    ("ephemeral_secoc_runtime.bin", 704, "8f486d36ae38d233165563ad2cc4a71d006cf5c8cf9a876345a3b6ab72f10495"),
    ("ephemeral_scheduler_canary.bin", 332, "81176c6e1c33451cfa63bd3b4a0e07b8b0fb952c70b3d67442f1a294ed6b651e"),
    ("ephemeral_command5_proxy.bin", 546, "273202dc591810b2f587ab8fac044599b57b4e07a24ff61d36b7131b97c00660"),
):
    path = REPO / "exploit/ephemeral_runtime/audited" / name
    check(f"audited runtime {name} is tracked-byte exact", path.is_file() and path.stat().st_size == size and hashlib.sha256(path.read_bytes()).hexdigest() == digest)

print("\n== destructive-operation safety ==")
with tempfile.TemporaryDirectory(prefix="rh850-build-layout-clean-") as td:
    external_root = Path(td) / "build"
    sentinel = external_root / "tmp" / "keep-me"
    sentinel.parent.mkdir(parents=True)
    sentinel.write_text("preserve")
    env = dict(os.environ, BUILD_ROOT=str(external_root))
    cp = subprocess.run([sys.executable, str(REPO / "tools/build_layout.py"), "clean", "tmp"], cwd=REPO, env=env, capture_output=True, text=True, timeout=15)
    check("destructive layout operations reject BUILD_ROOT overrides", cp.returncode != 0 and sentinel.read_text() == "preserve", cp.stderr)

print("\n== side-effect-free status path ==")
with tempfile.TemporaryDirectory(prefix="rh850-build-layout-") as td:
    root = Path(td) / "build"
    env = dict(os.environ, BUILD_ROOT=str(root), GHIDRA_NO_BOOTSTRAP="1", GHIDRA_AGENT="1")
    cp = subprocess.run(["bash", str(REPO / "tools/g"), "session-status"], cwd=REPO, env=env, capture_output=True, text=True, timeout=15)
    check("tools/g session-status works with empty build root", cp.returncode == 0, cp.stderr)
    check("session-status does not create cache/work/output state", not root.exists() or not any(root.iterdir()))

print(f"\nResults: {passed} passed, {failed} failed")
raise SystemExit(1 if failed else 0)
