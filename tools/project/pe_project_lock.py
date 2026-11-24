"""Hold the project-open lock shared with the vendored Rust bridge launcher."""

import fcntl
import hashlib
import os
import shlex
import subprocess
import sys
from pathlib import Path

from tools import REPO_ROOT


def _bridge_data_dir() -> Path:
    # Match dirs::data_local_dir() in ghidra-cli.
    if sys.platform == "darwin":
        return Path.home() / "Library/Application Support/ghidra-cli"
    data_home = Path(os.environ.get("XDG_DATA_HOME", ""))
    if not data_home.is_absolute():
        data_home = Path.home() / ".local/share"
    return data_home / "ghidra-cli"


def _bridge_key(project: str) -> str:
    # Rust hashes the UTF-8 lossy rendering of the native project path.
    utf8 = os.fsencode(project).decode("utf-8", errors="replace").encode()
    return "bridge-" + hashlib.md5(utf8, usedforsecurity=False).hexdigest()


def _bridge_pid_is_live(pid_file: Path) -> bool:
    try:
        pid = int(pid_file.read_text())
    except (FileNotFoundError, ValueError):
        return False
    if not 0 < pid <= 2**31 - 1:
        return False
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        pass
    return True


def _main(project_dir: str, project: str, quiet: str, binary: str, program: str, *args: str) -> None:
    data_dir = _bridge_data_dir()
    canonical_dir = Path(project_dir).expanduser().resolve()
    key = _bridge_key(str(canonical_dir / project))
    # Also recognize a bridge started by an older wrapper with a relative path
    # or symlink. Do not dispatch status: this probe must not clean up anything.
    legacy_key = _bridge_key(os.path.join(project_dir, project))
    data_dir.mkdir(parents=True, exist_ok=True)
    with (data_dir / f"{key}.open.lock").open("ab") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        if any(_bridge_pid_is_live(data_dir / f"{k}.pid") for k in (key, legacy_key)):
            stop = f"PE_PROJECT={shlex.quote(project)} tools/pe stop"
            if project_dir != str(REPO_ROOT / "build/work/pe-project"):
                stop = f"BUILD_WORK={shlex.quote(os.environ['BUILD_WORK'])} {stop}"
            raise SystemExit(
                f"ERROR: Ghidra bridge is active or shutting down for PE project {project!r}. "
                f"Stop it cleanly before importing: {stop}"
            )

        scripts = REPO_ROOT / "tools/project"
        ghidra_home = subprocess.check_output([scripts / "resolve_ghidra_home.sh"], text=True).rstrip("\n")
        if quiet == "0":
            print(f"Importing {program}...", file=sys.stderr, flush=True)
        env = dict(os.environ, GHIDRA_HOME=ghidra_home, GHIDRA_NO_BOOTSTRAP="1")
        runner = scripts / "run_headless"
        # Transfer the lease to the runner and its children, including the
        # quiescence check after analyzeHeadless exits.
        os.set_inheritable(lock.fileno(), True)
        command = [
            str(runner), "--project-dir", str(canonical_dir), "--project", project,
            "--label", "pe-import", "--quiet", "--", "-import", binary, "-overwrite", *args,
        ]
        os.execve(runner, command, env)


if __name__ == "__main__":
    try:
        _main(*sys.argv[1:])
    except subprocess.CalledProcessError as error:
        raise SystemExit(error.returncode) from None
    except OSError as error:
        raise SystemExit(f"ERROR: PE import coordination failed: {error}") from None
