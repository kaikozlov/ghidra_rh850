"""Python interface to the repository's single RH850 toolchain."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
RH850 = ROOT / "tools" / "rh850"


def command(work_dir: Path, *args: str) -> list[str]:
    """Return a pinned-toolchain command with work_dir mounted at /out."""
    return [
        str(RH850),
        "toolchain",
        "run",
        "--work-dir",
        str(work_dir),
        *args,
    ]


def metadata() -> dict[str, Any]:
    """Return canonical image provenance after verifying that the image exists."""
    proc = subprocess.run(
        [str(RH850), "toolchain", "info"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(proc.stdout)
