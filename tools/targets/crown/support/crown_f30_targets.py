"""Registry-backed exact Crown F30 target constants for offline analysis.

Resolution lives in the analysis-target registry; nothing here re-derives repo
paths. Semantic proof logic remains in the individual extractors/builders.
"""
from __future__ import annotations

from tools.project.analysis_target import path, target, verified_file

TARGET_NAME = "crown-8965F3012000"
_, TARGET = target(TARGET_NAME)
CODEFLASH = verified_file(TARGET_NAME, "codeflash")
CODEFLASH_SHA256 = TARGET["codeflash_sha256"]
DATAFLASH = verified_file(TARGET_NAME, "dataflash")
CAPTURE = path(TARGET_NAME, "capture_root")
CORPUS = path(TARGET_NAME, "decompiler_corpus")
INVENTORY = path(TARGET_NAME, "inventory_baseline")

__all__ = [
    "CAPTURE", "CODEFLASH", "CODEFLASH_SHA256", "CORPUS", "DATAFLASH",
    "INVENTORY", "TARGET", "TARGET_NAME",
]
