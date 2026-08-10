#!/usr/bin/env python3
"""Behavioral tests for tools/run_headless."""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
RUNNER = REPO / "tools" / "run_headless"

passed = 0
failed = 0


def check(name: str, condition: bool, detail: str = "") -> None:
    global passed, failed
    if condition:
        passed += 1
        print(f"[PASS] {name}")
    else:
        failed += 1
        print(f"[FAIL] {name}{': ' + detail if detail else ''}")


def invoke(fake_home: Path, *args: str, extra_env: dict[str, str] | None = None):
    env = dict(os.environ)
    env.update(
        {
            "GHIDRA_NO_BOOTSTRAP": "1",
            "GHIDRA_HOME": str(fake_home),
            "GHIDRA_ANALYSIS_TIMEOUT": "321",
            "GHIDRA_MAX_CPU": "7",
        }
    )
    if extra_env:
        env.update(extra_env)
    return subprocess.run(
        ["bash", str(RUNNER), *args],
        cwd=REPO,
        env=env,
        text=True,
        capture_output=True,
        timeout=15,
    )


print("== centralized analyzeHeadless runner ==")
runner_text = RUNNER.read_text()
check(
    "caller-supplied GHIDRA_ENV_READY cannot bypass bootstrap validation",
    "GHIDRA_ENV_READY" not in runner_text,
)
with tempfile.TemporaryDirectory() as td:
    temp = Path(td)
    fake_home = temp / "ghidra"
    support = fake_home / "support"
    support.mkdir(parents=True)
    capture = temp / "args.json"
    fake = support / "analyzeHeadless"
    fake.write_text(
        "#!/usr/bin/env python3\n"
        "import json, os, sys\n"
        "from pathlib import Path\n"
        "Path(os.environ['FAKE_CAPTURE']).write_text(json.dumps(sys.argv[1:]))\n"
        "print(os.environ.get('FAKE_OUTPUT', 'fake headless ok'))\n"
        "raise SystemExit(int(os.environ.get('FAKE_RC', '0')))\n"
    )
    fake.chmod(0o755)
    project_dir = temp / "work"
    log = temp / "headless.log"

    result = invoke(
        fake_home,
        "--project-dir", str(project_dir),
        "--project", "fixture",
        "--log", str(log),
        "--label", "fixture-run",
        "--",
        "-import", str(temp / "input.bin"),
        extra_env={"FAKE_CAPTURE": str(capture)},
    )
    check("runner succeeds with fake analyzeHeadless", result.returncode == 0, result.stderr)
    args = json.loads(capture.read_text()) if capture.exists() else []
    check("runner canonicalizes project directory", args[:2] == [str(project_dir.resolve()), "fixture"], repr(args[:2]))
    check("runner injects analysis timeout", "-analysisTimeoutPerFile" in args and "321" in args)
    check("runner injects max CPU", "-max-cpu" in args and "7" in args)
    check("runner injects one canonical scriptPath", args.count("-scriptPath") == 1, repr(args))
    if "-scriptPath" in args:
        script_path = args[args.index("-scriptPath") + 1]
        expected_dirs = [
            REPO / "ghidra/scripts/import",
            REPO / "ghidra/scripts/seed",
            REPO / "ghidra/scripts/annotate",
            REPO / "ghidra/scripts/verify",
        ]
        check("scriptPath uses semicolon separators", script_path == ";".join(map(str, expected_dirs)), script_path)
        check("analysis-safe scriptPath excludes investigate", "/investigate" not in script_path)
    check("runner writes complete log", log.is_file() and "fake headless ok" in log.read_text())

    # A Ghidra post-script failure must fail even when analyzeHeadless returns 0.
    result = invoke(
        fake_home,
        "--project-dir", str(project_dir),
        "--project", "fixture",
        "--log", str(log),
        "--label", "script-error",
        "--",
        "-process", "program",
        extra_env={
            "FAKE_CAPTURE": str(capture),
            "FAKE_OUTPUT": "REPORT SCRIPT ERROR boom",
        },
    )
    check("runner converts REPORT SCRIPT ERROR into failure", result.returncode != 0)
    check("runner reports failing label and log", "script-error" in result.stderr and str(log) in result.stderr)

    result = invoke(
        fake_home,
        "--project-dir", str(project_dir),
        "--project", "fixture",
        "--log", str(log),
        "--",
        "-process", "program",
        extra_env={"FAKE_CAPTURE": str(capture), "FAKE_RC": "9"},
    )
    check("runner propagates nonzero analyzeHeadless failure", result.returncode != 0)

    # Callers may not bypass centralized scriptPath/default ownership.
    result = invoke(
        fake_home,
        "--project-dir", str(project_dir),
        "--project", "fixture",
        "--",
        "-scriptPath", "/tmp/ad-hoc",
        extra_env={"FAKE_CAPTURE": str(capture)},
    )
    check("runner rejects caller-supplied scriptPath", result.returncode != 0 and "scriptPath" in result.stderr)

    result = invoke(
        fake_home,
        "--project-dir", str(REPO / "project"),
        "--project", "rh850_p1me_mapped",
        "--",
        "-process", "program",
        extra_env={"FAKE_CAPTURE": str(capture)},
    )
    check("runner rejects committed snapshot path", result.returncode != 0 and "committed snapshot" in result.stderr)

    # Dot-prefixed components are rejected because Ghidra 12.1 rejects them.
    result = invoke(
        fake_home,
        "--project-dir", str(temp / ".hidden" / "project"),
        "--project", "fixture",
        "--",
        "-import", "input.bin",
        extra_env={"FAKE_CAPTURE": str(capture)},
    )
    check("runner rejects dot-prefixed project paths", result.returncode != 0 and "dot-prefixed" in result.stderr)

print()
if failed:
    print(f"FAILED: {failed} check(s)", file=sys.stderr)
    raise SystemExit(1)
print(f"All {passed} checks passed.")
