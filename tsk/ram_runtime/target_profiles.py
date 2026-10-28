"""Exact firmware-bound profiles for maintained RAM-resident runtimes."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from tools import REPO_ROOT
from tsk.common.rh850_build import sha_bytes
from tsk.ram_runtime.tss3_request_signer_contract import (
    resolve_request_signer_contract,
)

REGISTRY = REPO_ROOT / "data/analysis_targets.json"
PAYLOAD_NAME = "tss3-request-signer"
BOOT_F181_HEX = "02" + "21" * 32


def _registry() -> dict[str, Any]:
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    if registry.get("schema") != "ghidra-rh850-analysis-targets-v1":
        raise RuntimeError("analysis target registry schema drift")
    return registry


def registered_targets() -> dict[str, dict[str, Any]]:
    return {
        name: target
        for name, target in _registry()["targets"].items()
        if PAYLOAD_NAME in target.get("ram_runtime", {}).get("payloads", ())
    }


def supported_targets() -> tuple[str, ...]:
    return tuple(registered_targets())


def _spec_from_contract(
    *,
    name: str,
    image_path: Path,
    contract: dict[str, Any],
    request_bus: int | None,
    response_bus: int | None,
) -> dict[str, Any]:
    resolved_request = contract["request"]
    identity = contract["identity"]
    return {
        "name": name,
        "runtime_software_id": identity["runtime_software_id"],
        "application_f181_hex": identity["application_f181_hex"],
        "image": image_path,
        "sha256": contract["codeflash_sha256"],
        "request": {
            "request_id": resolved_request["request_id"],
            "response_id": resolved_request["response_id"],
            "request_bus": request_bus,
            "response_bus": response_bus,
        },
        "contract": contract,
    }


def _registered_spec(
    name: str,
    registry_target: dict[str, Any],
    image_path: Path,
    image: bytes,
    contract: dict[str, Any],
) -> dict[str, Any]:
    runtime = registry_target["ram_runtime"]
    identity = contract["identity"]
    if (
        contract["codeflash_sha256"] != registry_target["codeflash_sha256"]
        or registry_target["software_id"].encode("ascii") not in image
        or identity["application_f181_hex"] != runtime["application_f181_hex"]
    ):
        raise RuntimeError(f"{name} firmware identity drift")
    return _spec_from_contract(
        name=name,
        image_path=image_path,
        contract=contract,
        request_bus=runtime["request_bus"],
        response_bus=runtime["response_bus"],
    )


def _load_registered_spec(name: str, registry_target: dict[str, Any]) -> dict[str, Any]:
    image_path = REPO_ROOT / registry_target["codeflash"]
    image = image_path.read_bytes()
    if sha_bytes(image) != registry_target["codeflash_sha256"]:
        raise RuntimeError(f"{name} CodeFlash identity drift")
    return _registered_spec(
        name,
        registry_target,
        image_path,
        image,
        resolve_request_signer_contract(image),
    )


def target_spec(name: str) -> dict[str, Any]:
    registry_target = registered_targets().get(name)
    if registry_target is None:
        raise RuntimeError(f"unsupported RAM runtime target {name}")
    return _load_registered_spec(name, registry_target)


def registered_specs() -> dict[str, dict[str, Any]]:
    return {
        name: _load_registered_spec(name, target)
        for name, target in registered_targets().items()
    }


def spec_from_codeflash(image_path: Path) -> dict[str, Any]:
    image_path = image_path.resolve()
    image = image_path.read_bytes()
    digest = sha_bytes(image)
    contract = resolve_request_signer_contract(image)
    for name, target in registered_targets().items():
        if target["codeflash_sha256"] == digest:
            return _registered_spec(name, target, image_path, image, contract)
    identity = contract["identity"]
    return _spec_from_contract(
        name=f"tss3-{identity['firmware_software_id']}",
        image_path=image_path,
        contract=contract,
        request_bus=None,
        response_bus=None,
    )
