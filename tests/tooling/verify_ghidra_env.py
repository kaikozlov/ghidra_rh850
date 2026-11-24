#!/usr/bin/env python3
"""Behavioral tests for cached, fail-closed Ghidra environment bootstrap."""
from __future__ import annotations

import fcntl
import os
import signal
import subprocess
import tempfile
import time
from pathlib import Path

from tools import REPO_ROOT
REPO = REPO_ROOT
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
    (fake_home / "Ghidra/application.properties").write_text("application.version=12.2\n")
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
            'export GHIDRA_VERSION="12.2"\n'
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
        "printf 'install\\n' >> \"$FAKE_INSTALL_COUNT\"\n"
        "if [[ ${FAKE_INSTALL_RC:-0} != 0 ]]; then exit \"$FAKE_INSTALL_RC\"; fi\n"
        "if [[ -n ${FAKE_INSTALL_STARTED:-} ]]; then\n"
        "  touch \"$FAKE_INSTALL_STARTED\"\n"
        "  while [[ ! -f \"$FAKE_RELEASE_INSTALL\" ]]; do sleep 0.01; done\n"
        "fi\n"
        "cp \"$FAKE_ENV_TEMPLATE\" \"$GHIDRA_PROCESSOR_ENV_FILE\"\n"
        "eval \"$FAKE_REPAIR_COMMAND\"\n"
        "if [[ -n ${FAKE_CURRENT_CACHE:-} ]]; then touch \"$FAKE_CURRENT_CACHE\"; fi\n"
    )
    installer.chmod(0o755)
    fingerprint = temp / "fingerprint.py"
    fingerprint.write_text(
        "#!/usr/bin/env python3\n"
        "import os, sys\n"
        "from pathlib import Path\n"
        "Path(os.environ['FAKE_FINGERPRINT_LOG']).write_text(' '.join(sys.argv[1:]))\n"
        "current = os.environ.get('FAKE_CURRENT_CACHE')\n"
        "if current and not Path(current).exists():\n"
        "    checked = os.environ.get('FAKE_STALE_CHECKED')\n"
        "    if checked:\n"
        "        Path(checked).touch()\n"
        "    raise SystemExit(1)\n"
        "raise SystemExit(int(os.environ.get('FAKE_FINGERPRINT_RC', '0')))\n"
    )
    fingerprint.chmod(0o755)

    base_env = dict(os.environ)
    base_env.update(
        {
            "BUILD_ROOT": str(temp / "build"),
            "BUILD_CACHE": str(temp / "cache"),
            "GHIDRA_PROCESSOR_ENV_FILE": str(env_file),
            "GHIDRA_ENV_FORCE_REBUILD": "0",
            "GHIDRA_INSTALL_SCRIPT": str(installer),
            "GHIDRA_FINGERPRINT_TOOL": str(fingerprint),
            "FAKE_INSTALL_COUNT": str(install_count),
            "FAKE_ENV_TEMPLATE": str(env_template),
            "FAKE_FINGERPRINT_LOG": str(fingerprint_log),
            "FAKE_REPAIR_COMMAND": f"mkdir -p '{sla.parent}'; printf fixture > '{sla}'",
        }
    )

    def bootstrap_command(mode: str = "none", *, errexit: bool = True) -> list[str]:
        options = "-euo" if errexit else "-uo"
        return [
            "bash", "-c", f'set {options} pipefail; source "$1" "$2"; printf "%s" "$GHIDRA_ENV_READY"',
            "bootstrap", str(HELPER), mode,
        ]

    def installs(path: Path = install_count) -> int:
        return len(path.read_text().splitlines()) if path.exists() else 0

    def source(mode: str = "none", extra: dict[str, str] | None = None, *, errexit: bool = True):
        env = dict(base_env)
        if extra:
            env.update(extra)
        return subprocess.run(
            bootstrap_command(mode, errexit=errexit),
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
        installs() == 1,
    )

    # A stale env (missing compiled SLA) must trigger reinstall.
    sla.unlink()
    result = source()
    check("stale env triggers installer", result.returncode == 0, result.stderr)
    check(
        "stale env installer called again",
        installs() == 2,
    )

    # A cache produced by the previous pinned Ghidra release must never be reused.
    stale_text = env_template.read_text().replace('GHIDRA_VERSION="12.2"', 'GHIDRA_VERSION="12.1.4"')
    env_file.write_text(stale_text)
    result = source()
    check("previous-version cache triggers installer", result.returncode == 0, result.stderr)
    check(
        "previous-version cache is replaced",
        installs() == 3,
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

    forced = {"GHIDRA_ENV_FORCE_REBUILD": "1"}
    result = source(extra={**forced, "FAKE_INSTALL_RC": "17"}, errexit=False)
    check("forced installer failure fails closed without errexit",
          result.returncode == 17 and not result.stdout, result.stderr)
    result = source(extra=forced)
    check("failed installer releases lock; forcing still rebuilds a warm cache",
          result.returncode == 0 and result.stdout == "1" and installs() == 5, result.stderr)

    concurrent_count = temp / "concurrent-install-count"
    install_started = temp / "install-started"
    release_install = temp / "release-install"
    current_cache = temp / "current-cache"
    second_checked_stale = temp / "second-checked-stale"
    concurrent_env = {
        **base_env,
        "FAKE_INSTALL_COUNT": str(concurrent_count),
        "FAKE_INSTALL_STARTED": str(install_started),
        "FAKE_RELEASE_INSTALL": str(release_install),
        "FAKE_CURRENT_CACHE": str(current_cache),
    }

    def start_caller(env: dict[str, str]) -> subprocess.Popen[str]:
        return subprocess.Popen(
            bootstrap_command(), cwd=REPO, env=env, text=True,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, start_new_session=True,
        )

    def wait_for_marker(path: Path, caller: subprocess.Popen[str]) -> None:
        deadline = time.monotonic() + 15
        while not path.exists():
            if caller.poll() is not None:
                _, stderr = caller.communicate()
                raise RuntimeError(f"caller exited before writing {path.name}: {stderr}")
            if time.monotonic() >= deadline:
                raise TimeoutError(f"timed out waiting for {path.name}")
            time.sleep(0.01)

    # The first caller cannot publish until the second has observed stale state.
    # Even if publication wins the next scheduling race, that probe returns stale.
    callers = [start_caller(concurrent_env)]
    try:
        wait_for_marker(install_started, callers[0])
        callers.append(start_caller({**concurrent_env, "FAKE_STALE_CHECKED": str(second_checked_stale)}))
        wait_for_marker(second_checked_stale, callers[1])
        release_install.touch()
        for idx, caller in enumerate(callers, 1):
            stdout, stderr = caller.communicate(timeout=15)
            check(f"concurrent cold caller {idx} reads ready cache", caller.returncode == 0 and stdout == "1", stderr)
        check("concurrent cold callers share one rebuild", installs(concurrent_count) == 1)
    finally:
        # Also terminate a timed-out lock helper or installer, not just its shell.
        for caller in callers:
            if caller.poll() is None:
                try:
                    os.killpg(caller.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
                caller.wait()

    lock_file = Path(base_env["BUILD_CACHE"]) / "ghidra-processor.lock"
    with lock_file.open("r+") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        result = source(extra=concurrent_env)
    check("warm cache does not wait for the writer lock",
          result.returncode == 0 and result.stdout == "1" and installs(concurrent_count) == 1, result.stderr)

print()
if failed:
    print(f"FAILED: {failed} check(s)")
    raise SystemExit(1)
print(f"All {passed} checks passed.")
