"""Canonical paths for ignored repository build/workspace state."""
from __future__ import annotations
import os
from dataclasses import dataclass
from pathlib import Path

@dataclass(frozen=True)
class BuildPaths:
    root: Path
    cache: Path
    work: Path
    out: Path
    logs: Path
    tmp: Path

    def ensure(self) -> "BuildPaths":
        for p in (self.cache, self.work, self.out, self.logs, self.tmp):
            p.mkdir(parents=True, exist_ok=True)
        return self


def for_repo(repo: Path) -> BuildPaths:
    repo = repo.resolve()
    root = Path(os.environ.get("BUILD_ROOT", repo / "build")).expanduser().resolve()
    return BuildPaths(
        root=root,
        cache=Path(os.environ.get("BUILD_CACHE", root / "cache")).expanduser().resolve(),
        work=Path(os.environ.get("BUILD_WORK", root / "work")).expanduser().resolve(),
        out=Path(os.environ.get("BUILD_OUT", root / "out")).expanduser().resolve(),
        logs=Path(os.environ.get("BUILD_LOGS", root / "logs")).expanduser().resolve(),
        tmp=Path(os.environ.get("BUILD_TMP", root / "tmp")).expanduser().resolve(),
    )
