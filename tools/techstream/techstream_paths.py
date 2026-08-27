#!/usr/bin/env python3
"""Canonical repository-local Techstream/GTS+/CUW corpus paths and resolvers."""
from __future__ import annotations

import os
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
V18_DIAGNOSTICS_ROOT = REPO / "software/Techstream/v18/unpacked/toyota/Toyota Diagnostics"
V18_TECHSTREAM_ROOT = V18_DIAGNOSTICS_ROOT / "Techstream"
V18_DB_ROOT = V18_TECHSTREAM_ROOT / "NA/DB"
V18_CUW_ROOT = V18_DIAGNOSTICS_ROOT / "Calibration Update Wizard"
GTSPLUS_EXTERNAL_ROOT = REPO / "software/Techstream/gtsplus"
CUW_CORPUS_ROOT = REPO / "software/Techstream/cuw"


def v18_diagnostics_root() -> Path:
    return V18_DIAGNOSTICS_ROOT


def v18_techstream_root() -> Path:
    return V18_TECHSTREAM_ROOT


def v18_db_root(region: str = "NA") -> Path:
    return V18_TECHSTREAM_ROOT / region / "DB"


def v18_cuw_root() -> Path:
    return V18_CUW_ROOT


def resolve_gts_root(value: str | Path | None = None) -> Path:
    base = Path(value or os.environ.get("GTSPLUS_ROOT", GTSPLUS_EXTERNAL_ROOT)).expanduser()
    candidates = [
        base,
        base / "unpacked/gtsplus/Toyota Diagnostics/GTSPlus",
        base / "Toyota Diagnostics/GTSPlus",
    ]
    for candidate in candidates:
        if (candidate / "NA/DB/Gen").is_dir():
            return candidate.resolve()
    return candidates[0].resolve()


def resolve_cuwplus_root(gts_root: Path, value: str | Path | None = None) -> Path:
    override = value or os.environ.get("GTSPLUS_CUW_ROOT")
    if override:
        return Path(override).expanduser().resolve()
    for parent in (gts_root, *gts_root.parents):
        candidate = parent / "cuwplus/CUWPlus"
        if candidate.is_dir():
            return candidate.resolve()
    default_gts = resolve_gts_root(GTSPLUS_EXTERNAL_ROOT)
    if gts_root.resolve() == default_gts:
        external = REPO / "software/Techstream/gtsplus/cuwplus/CUWPlus"
        return external.resolve()
    # Never silently combine writer routes from a different GTS release.
    return (gts_root / "__missing_cuwplus__").resolve()


def resolve_cuw_corpus(value: str | Path | None = None) -> Path:
    return Path(value or os.environ.get("TOYOTA_CUW_CORPUS_ROOT", CUW_CORPUS_ROOT)).expanduser().resolve()


def gts_db_root(gts_root: Path, region: str = "NA", family: str = "Gen") -> Path:
    return gts_root / region / "DB" / family
