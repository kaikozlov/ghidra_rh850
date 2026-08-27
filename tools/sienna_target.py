"""Registry-backed primary Sienna target files used by cross-variant tools."""
from __future__ import annotations

try:
    from .analysis_target import REPO, target, verified_file
except ImportError:  # direct script execution
    from analysis_target import REPO, target, verified_file

TARGET_NAME = "sienna-8965B4512000"
_, TARGET = target(TARGET_NAME)
CODEFLASH = verified_file(TARGET_NAME, "codeflash")
DATAFLASH = verified_file(TARGET_NAME, "dataflash")
CODEFLASH_SHA256 = TARGET["codeflash_sha256"]
DATAFLASH_SHA256 = TARGET["dataflash_sha256"]
