#!/usr/bin/env python3
"""Behavioral tests for cached, fail-closed Ghidra environment bootstrap."""
from __future__ import annotations

import os
import subprocess
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
HELPER = REPO / "tools/lib/ghidra_env.sh"

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


print("== isolated Ghidra environment cache ==")
with tempfile.TemporaryDirectory() as td:
    temp = Path(td)
    fake_home = temp / "ghidra"
    (fake_home / "Ghidra").mkdir(parents=True)
    (fake_home / "Ghidra/application.properties").write_text("application.version=12.1.2\n")
    ext = temp / "extension"
    (ext / "data/languages").mkdir(parents=True)
    sla = ext / "data/languages/v850e3.sla"
    sla.write_text("fixture")
    manifest = temp / "manifest.json"
    manifest.write_text("{}\n")
    env_file = temp / "ghidra-processor.env"
    env_template = temp / "ghidra-processor.env.template"
    install_count = temp / "install-count"
    fingerprint_log = temp / "fingerprint-args"

    def write_env() -> None:
        text = (
            f'export GHIDRA_HOME="{fake_home}"\n'
            f'export GHIDRA_ISOLATED_HOME="{temp / "user-home"}"\n'
            f'export V850_EXT_DIR="{ext}"\n'
            f'export V850_BUILD_DIR="{temp / "build-ext"}"\n'
            f'export PROCESSOR_MANIFEST="{manifest}"\n'
            'export GHIDRA_VERSION="12.1.2"\n'
            'export GHIDRA_CLI_VERSION="0.2.1"\n'
            f'export GHIDRA_JAVA_OPTIONS="-Duser.home={temp / "user-home"}"\n'
            f'export GHIDRA_HEADLESS_JAVA_OPTIONS="-Duser.home={temp / "user-home"}"\n'
        )
        env_file.write_text(text)
        env_template.write_text(text)

    write_env()
    installer = temp / "install.sh"
    installer.write_text(
        "#!/usr/bin/env bash\n"
        "set -euo pipefail\n"
        "n=0; [[ ! -f \"$FAKE_INSTALL_COUNT\" ]] || n=$(cat \"$FAKE_INSTALL_COUNT\")\n"
        "printf '%s\\n' \"$((n + 1))\" > \"$FAKE_INSTALL_COUNT\"\n"
        "cp \"$FAKE_ENV_TEMPLATE\" \"$GHIDRA_PROCESSOR_ENV_FILE\"\n"
        "eval \"$FAKE_REPAIR_COMMAND\"\n"
    )
    installer.chmod(0o755)
    fingerprint = temp / "fingerprint.py"
    fingerprint.write_text(
        "#!/usr/bin/env python3\n"
        "import os, sys\n"
        "from pathlib import Path\n"
        "Path(os.environ['FAKE_FINGERPRINT_LOG']).write_text(' '.join(sys.argv[1:]))\n"
        "raise SystemExit(int(os.environ.get('FAKE_FINGERPRINT_RC', '0')))\n"
    )
    fingerprint.chmod(0o755)

    base_env = dict(os.environ)
    base_env.update(
        {
            "GHIDRA_PROCESSOR_ENV_FILE": str(env_file),
            "GHIDRA_INSTALL_SCRIPT": str(installer),
            "GHIDRA_FINGERPRINT_TOOL": str(fingerprint),
            "FAKE_INSTALL_COUNT": str(install_count),
            "FAKE_ENV_TEMPLATE": str(env_template),
            "FAKE_FINGERPRINT_LOG": str(fingerprint_log),
            "FAKE_REPAIR_COMMAND": f"mkdir -p '{sla.parent}'; printf fixture > '{sla}'",
        }
    )

    def source(mode: str = "none", extra: dict[str, str] | None = None):
        env = dict(base_env)
        if extra:
            env.update(extra)
        return subprocess.run(
            ["bash", "-c", f'set -euo pipefail; source "{HELPER}" {mode}; printf "%s" "$GHIDRA_ENV_READY"'],
            cwd=REPO,
            env=env,
            text=True,
            capture_output=True,
            timeout=15,
        )

    result = source()
    check("valid cached environment succeeds", result.returncode == 0, result.stderr)
    check("valid cached environment exports ready marker", result.stdout == "1", result.stdout)
    check("valid cached environment skips installer", not install_count.exists())

    env_file.unlink()
    # Installer in the real world rewrites the env file; make the fixture do so.
    result = source()
    check("missing env triggers installer", result.returncode == 0, result.stderr)
    check(
        "missing env installer called once",
        install_count.exists() and install_count.read_text().strip() == "1",
    )

    # A stale env (missing compiled SLA) must trigger reinstall.
    sla.unlink()
    result = source()
    check("stale env triggers installer", result.returncode == 0, result.stderr)
    check(
        "stale env installer called again",
        install_count.exists() and install_count.read_text().strip() == "2",
    )

    result = source("full")
    args = fingerprint_log.read_text() if fingerprint_log.exists() else ""
    check("full mode invokes fingerprint verification", result.returncode == 0 and "--sla" in args and "--expect" in args, args)

    result = subprocess.run(
        [
            "bash",
            "-c",
            f'set -euo pipefail; source "{HELPER}" none; source "{HELPER}" full',
        ],
        cwd=REPO,
        env=base_env,
        text=True,
        capture_output=True,
        timeout=15,
    )
    args = fingerprint_log.read_text() if fingerprint_log.exists() else ""
    check(
        "later source can escalate fingerprint mode",
        result.returncode == 0 and "--sla" in args,
        args,
    )

print()
if failed:
    print(f"FAILED: {failed} check(s)")
    raise SystemExit(1)
print(f"All {passed} checks passed.")
