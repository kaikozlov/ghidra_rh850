#!/usr/bin/env python3
"""Verify safe cleanup and Ghidra wrapper output with disposable tool fixtures."""
from __future__ import annotations

import hashlib
import json
import os
import shlex
import subprocess
import sys
import tempfile
import time
from pathlib import Path

from tools import REPO_ROOT
REPO = REPO_ROOT
passed = failed = 0


def check(name: str, condition: object, detail: str = "") -> None:
    global passed, failed
    ok = bool(condition)
    passed += int(ok); failed += int(not ok)
    print(f"[{'PASS' if ok else 'FAIL'}] {name}" + (f" ({detail})" if detail else ""))


print("\n== destructive-operation safety ==")
with tempfile.TemporaryDirectory(prefix="rh850-build-layout-clean-") as td:
    external_root = Path(td) / "build"
    sentinel = external_root / "tmp" / "keep-me"
    sentinel.parent.mkdir(parents=True)
    sentinel.write_text("preserve")
    env = dict(os.environ, BUILD_ROOT=str(external_root))
    cp = subprocess.run([sys.executable, str(REPO / "tools/project/build_layout.py"), "clean", "tmp"], cwd=REPO, env=env, capture_output=True, text=True, timeout=15)
    check("destructive layout operations reject BUILD_ROOT overrides", cp.returncode != 0 and sentinel.read_text() == "preserve", cp.stderr)

print("\n== side-effect-free status path ==")
with tempfile.TemporaryDirectory(prefix="rh850-build-layout-") as td:
    root = Path(td) / "build"
    env = dict(os.environ, BUILD_ROOT=str(root), GHIDRA_NO_BOOTSTRAP="1", GHIDRA_AGENT="0")
    for args, format_name in (
        (["session-status"], "text"),
        (["--json", "session-status"], "json"),
        (["session-status", "--json"], "json"),
        (["--pretty", "session-status"], "pretty"),
        (["session-status", "--pretty"], "pretty"),
    ):
        cp = subprocess.run(["bash", str(REPO / "tools/g"), *args], cwd=REPO, env=env, capture_output=True, text=True, timeout=15)
        check(f"tools/g {' '.join(args)} works with empty build root", cp.returncode == 0, cp.stderr)
        if format_name == "text":
            check("piped session-status defaults to text", cp.stdout.startswith("daemon:"))
        else:
            try:
                status = json.loads(cp.stdout)
            except json.JSONDecodeError:
                status = {}
            check(f"{' '.join(args)} emits parseable JSON", status.get("daemon", {}).get("state") in {"running", "stopped"})
            check(f"{' '.join(args)} uses requested JSON layout", ("\n" in cp.stdout.strip()) == (format_name == "pretty"))
        check("session-status does not create cache/work/output state", not root.exists() or not any(root.iterdir()))

print("\n== PE import output and dispatch ==")
with tempfile.TemporaryDirectory(prefix="pe-wrapper-") as td:
    temp = Path(td).resolve()
    fake_home = temp / "ghidra"
    fake_headless = fake_home / "support" / "analyzeHeadless"
    fake_headless.parent.mkdir(parents=True)
    capture = temp / "headless-args.json"
    fake_headless.write_text(
        "#!/usr/bin/env python3\n"
        "import json, os, sys, time\n"
        "from pathlib import Path\n"
        "Path(os.environ['FAKE_CAPTURE']).write_text(json.dumps(sys.argv[1:]))\n"
        "if gate := os.environ.get('FAKE_GATE'):\n"
        "    deadline = time.monotonic() + 30\n"
        "    while not Path(gate).exists() and time.monotonic() < deadline:\n"
        "        time.sleep(0.02)\n"
        "    if not Path(gate).exists(): sys.exit(98)\n"
        "print(os.environ.get('FAKE_OUTPUT', 'INFO fake headless complete'))\n"
        "raise SystemExit(int(os.environ.get('FAKE_RC', '0')))\n"
    )
    fake_headless.chmod(0o755)
    binary = temp / "sample with spaces.dll"
    binary.write_bytes(b"MZ")
    build = temp / "build space"
    home = temp / "home"
    data = temp / "data"
    env = dict(os.environ, BUILD_ROOT=str(build), GHIDRA_HOME=str(fake_home),
               GHIDRA_AGENT="0", GHIDRA_ANALYSIS_TIMEOUT="300",
               PE_PROJECT="fixture_pe", FAKE_CAPTURE=str(capture),
               HOME=str(home), XDG_DATA_HOME=str(data))
    for name in ("CACHE", "WORK", "OUT", "LOGS", "TMP"):
        env[f"BUILD_{name}"] = str(build / name.lower())
    fake_cli = build / "cache" / "ghidra-cli" / "ghidra"
    fake_cli.parent.mkdir(parents=True)
    fake_cli.write_text("#!/bin/sh\necho 'unexpected bridge invocation' >&2\nexit 99\n")
    fake_cli.chmod(0o755)
    os.utime(fake_cli, (2_000_000_000, 2_000_000_000))

    for args, format_name in (
        (["import", str(binary)], "text"),
        (["--json", "import", str(binary)], "json"),
        (["import", "--json", str(binary)], "json"),
        (["import", str(binary), "--json"], "json"),
        (["--pretty", "import", str(binary)], "pretty"),
        (["import", str(binary), "--pretty"], "pretty"),
    ):
        capture.unlink(missing_ok=True)
        cp = subprocess.run(["bash", str(REPO / "tools/pe"), *args], cwd=REPO, env=env, capture_output=True, text=True, timeout=15)
        check(f"PE import {format_name} succeeds", cp.returncode == 0, cp.stderr if cp.returncode else "")
        headless_args = json.loads(capture.read_text()) if capture.exists() else []
        check("PE import always runs full headless analysis", "-import" in headless_args and str(binary) in headless_args and "-overwrite" in headless_args)
        check("PE output flags do not reach analyzeHeadless", "--json" not in headless_args and "--pretty" not in headless_args)
        check("PE headless logs stay out of result output", "INFO" not in cp.stdout)
        if format_name == "text":
            check("PE import defaults to a compact result", cp.stdout.startswith(f"imported {binary.name}"))
        else:
            try:
                result = json.loads(cp.stdout)
            except json.JSONDecodeError:
                result = None
            check("PE import emits the JSON success result", result == [{"status": "success", "program": binary.name}])
            check("PE import uses requested JSON layout", ("\n" in cp.stdout.strip()) == (format_name == "pretty"))

    cp = subprocess.run(["bash", str(REPO / "tools/pe"), "-qv", "import", str(binary)], cwd=REPO, env=dict(env, GHIDRA_AGENT="1"), capture_output=True, text=True, timeout=15)
    check("PE import honors legacy JSON with combined quiet/verbose flags", cp.returncode == 0 and cp.stdout.startswith('[{"status":"success"') and not cp.stderr.strip())

    cp = subprocess.run(["bash", str(REPO / "tools/pe"), "--json", "import", str(binary), "--", "-postScript", "Example.java", "--json"], cwd=REPO, env=env, capture_output=True, text=True, timeout=15)
    headless_args = json.loads(capture.read_text())
    check("PE import preserves arguments after --", cp.returncode == 0 and headless_args[-3:] == ["-postScript", "Example.java", "--json"])

    capture.unlink()
    cp = subprocess.run(["bash", str(REPO / "tools/pe"), "--json", "import", "--help"], cwd=REPO, env=env, capture_output=True, text=True, timeout=15)
    check("PE import help needs no Ghidra process", cp.returncode == 0 and "Usage:" in cp.stdout and not capture.exists())

    cp = subprocess.run(["bash", str(REPO / "tools/pe"), "--json", "import", str(binary)], cwd=REPO, env=dict(env, FAKE_OUTPUT="REPORT SCRIPT ERROR: fixture failure"), capture_output=True, text=True, timeout=15)
    check("PE import does not report success after a headless script error", cp.returncode != 0 and not cp.stdout.strip() and "fixture failure" in cp.stderr)

    bridge_dir = (home / "Library/Application Support" if sys.platform == "darwin" else data) / "ghidra-cli"
    project_dir = build / "work" / "pe-project"
    quoted_project = "a PE project's name"
    bridge_key = "bridge-" + hashlib.md5(str(project_dir / quoted_project).encode(), usedforsecurity=False).hexdigest()
    pid_file = bridge_dir / f"{bridge_key}.pid"
    native_lock = project_dir / f"{quoted_project}.lock"
    pid_file.write_text(str(os.getpid()))
    native_lock.write_text("keep")
    capture.unlink()
    pe_import = ["bash", str(REPO / "tools/pe"), "--json", "import", str(binary)]
    cp = subprocess.run(pe_import, cwd=REPO, env=dict(env, PE_PROJECT=quoted_project), capture_output=True, text=True, timeout=15)
    command = cp.stderr.rsplit("before importing: ", 1)[-1]
    check("PE import refuses a live bridge with the selected project's clean stop command",
          cp.returncode == 1 and not cp.stdout and not capture.exists()
          and shlex.split(command) == [f"BUILD_WORK={env['BUILD_WORK']}",
                                       f"PE_PROJECT={quoted_project}", "tools/pe", "stop"],
          cp.stderr)
    check("PE import does not mutate bridge metadata or Ghidra locks",
          pid_file.read_text() == str(os.getpid()) and native_lock.read_text() == "keep")
    pid_file.write_text("malformed")
    cp = subprocess.run(pe_import, cwd=REPO, env=dict(env, PE_PROJECT=quoted_project), capture_output=True, text=True, timeout=15)
    check("PE import ignores stale malformed metadata without removing it",
          cp.returncode == 0 and capture.exists() and pid_file.read_text() == "malformed"
          and native_lock.read_text() == "keep", cp.stderr)

    gate = temp / "release"
    first_capture = temp / "first"
    second_capture = temp / "second"
    overlap_capture = temp / "overlap"
    with subprocess.Popen(pe_import, cwd=REPO, env=dict(env, FAKE_CAPTURE=str(first_capture), FAKE_GATE=str(gate)),
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True) as first:
        try:
            deadline = time.monotonic() + 15
            while not first_capture.exists() and first.poll() is None and time.monotonic() < deadline:
                time.sleep(0.02)
            check("PE import reaches headless with its project lease", first_capture.exists())
            with subprocess.Popen(pe_import, cwd=REPO, env=dict(env, FAKE_CAPTURE=str(second_capture)),
                                  stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True) as second:
                try:
                    cp = subprocess.run(pe_import, cwd=REPO, env=dict(env, PE_PROJECT="fixture_pe_other", FAKE_CAPTURE=str(overlap_capture)),
                                        capture_output=True, text=True, timeout=15)
                    check("different PE projects can import concurrently",
                          cp.returncode == 0 and overlap_capture.exists() and first.poll() is None, cp.stderr)
                    check("same-project PE import queues before invoking headless",
                          second.poll() is None and not second_capture.exists())
                finally:
                    gate.touch()
                _, second_stderr = second.communicate(timeout=15)
                check("queued PE import succeeds after the first finishes",
                      second.returncode == 0 and second_capture.exists(), second_stderr)
        finally:
            gate.touch()
        _, first_stderr = first.communicate(timeout=15)
        check("the first PE import succeeds", first.returncode == 0, first_stderr)

    other_gate = temp / "release-other"
    other_process = [
        sys.executable, "-c",
        "import sys, time; from pathlib import Path\n"
        "deadline = time.monotonic() + 20\n"
        "while not Path(sys.argv[1]).exists() and time.monotonic() < deadline: time.sleep(0.02)",
        str(other_gate), "ghidra.app.util.headless.AnalyzeHeadless",
        str(project_dir), "fixture_pe suffix", "-scriptPath", "fixture",
    ]
    with subprocess.Popen(other_process) as other:
        try:
            cp = subprocess.run(pe_import, cwd=REPO, env=dict(env, GHIDRA_HEADLESS_QUIESCE_TIMEOUT="0"),
                                capture_output=True, text=True, timeout=15)
            check("headless quiescence ignores a different project sharing the same name prefix",
                  cp.returncode == 0 and other.poll() is None, cp.stderr)
        finally:
            other_gate.touch()

print(f"\nResults: {passed} passed, {failed} failed")
raise SystemExit(1 if failed else 0)
