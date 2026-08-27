"""Shared exact-F33 target/canonical-corpus helpers."""
from __future__ import annotations
from pathlib import Path

from analysis_target import REPO, target, verified_file
from decompiler_evidence import body_bytes, display_path

TARGET_NAME = "camry-8965F3307000"
_, TARGET = target(TARGET_NAME)
IMAGE = verified_file(TARGET_NAME, "codeflash")
IMAGE_SHA256 = TARGET["codeflash_sha256"]
CORPUS = REPO / TARGET["decompiler_corpus"]

__all__ = [
    "CORPUS", "IMAGE", "IMAGE_SHA256", "REPO", "TARGET", "TARGET_NAME",
    "body_bytes", "display_path",
]
