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

def queue_copy_precedes_publication(image: bytes) -> bool:
    """Prove the exact SecOC enqueue copy/length-publication instruction sequence.

    8E9FA loads descriptor+4 into r8 and bounds it by capacity. The successful
    branch computes r6=buffer+slot offset, loads descriptor[0] into r7, and calls
    the forward copy at 89F2E. Only afterward does 8EA24 store descriptor+4 to
    the selected queue record. This does not depend on decompiler names/types.
    """
    return image[0x8E9FA:0x8EA26] == bytes.fromhex(
        "fa470500230f0500e141bb4d03f000350a0d3a3f0100c131bfff1cb5"
        "23f70d001de0fa0f0500c3e2dcf1800c"
    )

__all__ = [
    "CAPTURE", "CORPUS", "DATAFLASH", "IMAGE", "IMAGE_SHA256", "INVENTORY",
    "TARGET", "TARGET_NAME", "body_bytes", "display_path", "queue_copy_precedes_publication",
]
