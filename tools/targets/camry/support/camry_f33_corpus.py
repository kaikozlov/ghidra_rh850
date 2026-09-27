"""Registry-backed exact-F33 target/canonical-corpus helpers."""
from __future__ import annotations

from tools.project.analysis_target import path, target, verified_file
from tools.project.decompiler_evidence import body_bytes, display_path

TARGET_NAME = "camry-8965F3307000"
_, TARGET = target(TARGET_NAME)
IMAGE = verified_file(TARGET_NAME, "codeflash")
IMAGE_SHA256 = TARGET["codeflash_sha256"]
DATAFLASH = verified_file(TARGET_NAME, "dataflash")
CAPTURE = path(TARGET_NAME, "capture_root")
CORPUS = path(TARGET_NAME, "decompiler_corpus")
INVENTORY = path(TARGET_NAME, "inventory_baseline")

__all__ = [
    "CAPTURE", "CORPUS", "DATAFLASH", "IMAGE", "IMAGE_SHA256", "INVENTORY",
    "TARGET", "TARGET_NAME", "body_bytes", "display_path",
]
