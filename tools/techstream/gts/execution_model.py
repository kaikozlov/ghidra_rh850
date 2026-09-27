"""Pinned GTS+ execution-model/vehicle-resolver artifacts, plugin identity hashing, and recovered semantic-kind tables."""

from __future__ import annotations

import functools
import hashlib
import json
import re
from pathlib import Path
from typing import Any

from tools import REPO_ROOT

EXECUTION_MODEL = REPO_ROOT / "data/generated/techstream_v18/diagnostic_execution_model.json"
VEHICLE_RESOLVER = REPO_ROOT / "data/generated/gtsplus_2026/vehicle_resolver_semantics.json"


def _file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


@functools.lru_cache(maxsize=1)
def _execution_model() -> dict[str, Any]:
    return json.loads(EXECUTION_MODEL.read_text())


def _execution_plugin_profiles() -> dict[str, dict[str, Any]]:
    return _execution_model()["gtsplus_continuity"]["dll_role_schema"]["plugin_semantics"]


@functools.cache
def _semantic_profile_for_plugin(plugin_path: Path, role: int) -> tuple[str | None, dict[str, Any] | None, str]:
    if not plugin_path.is_file():
        return None, None, "plugin_file_missing"
    actual_sha = _file_sha256(plugin_path)
    for name, profile in _execution_plugin_profiles().items():
        binding = profile.get("example_binding", {})
        plugin = profile.get("plugin", {})
        if binding.get("dll_role_id") == role and plugin.get("sha256") == actual_sha:
            return name, profile, "exact_plugin_identity"
    return None, None, "plugin_semantics_unrecovered_for_identity"


# Recovered semantic kinds for the generic (category-0) command-plugin families
# the runtime utility surface needs.  The six lifecycle wrappers are cross-checked
# at build time against the pinned execution model; the four routine Active-Test
# wrappers are the recovered shared P5 routine executors (TMS-073).  Every other
# generic role stays opaque and is not classified here.
GENERIC_UTILITY_ROLE_KINDS = {
    0x3A: "test_present_start",
    0x3B: "test_present_stop",
    0x61: "check_mode_frame_get",
    0x62: "check_mode_frame_confirm",
    0xB0: "active_test_start",
    0xAE: "routine_active_test_init",
    0xAF: "routine_active_test_signal_info",
    0xBF: "set_default_session",
    0xCA: "move_session_cgwd",
    0xD4: "single_routine_active_test",
}

P6_ACTIVE_TEST_PLUGIN_KINDS = {
    (0x06, "2bf137cccfdc063f20d27e73eca89b5c1f409dd5d929ce8f7af5c6745a3d52ee"): "p6_active_test_list",
    (0x08, "0c1ea2ed81271b86ca92ee46f3b3379da4a8664c379409881f35c5945c6dc195"): "p6_active_test_init",
    (0x70, "5106c7d9e14781b2ae7596324889de1d9b0fe00f16247df606b15c411e7fc621"): "p6_active_test_signal_info",
    (0xAE, "8967ac19164ff91cae26a229b28753656c369bcc01a493ee912bcdcf77af846d"): "p6_routine_active_test_init",
    (0xAF, "f009fe6c1d59bb8413e119937d10bdf9687ed983ec747911290d992d21df92e1"): "p6_routine_active_test_signal_info",
}


_SEMANTIC_KIND_PATTERN = re.compile(r"^role_0x[0-9A-Fa-f]+_(?P<kind>.+)$")


def _semantic_kind_for_profile(profile_name: str | None) -> str | None:
    if profile_name is None:
        return None
    match = _SEMANTIC_KIND_PATTERN.match(profile_name)
    return match.group("kind") if match else None
