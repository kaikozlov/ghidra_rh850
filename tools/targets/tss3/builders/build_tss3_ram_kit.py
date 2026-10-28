#!/usr/bin/env python3
"""Package the canonical TSS3 RAM-resident request signer for exact targets."""
from __future__ import annotations

import argparse
import json
import shutil
import sys
import tempfile
from pathlib import Path

from exploit.ram_runtime.target_profiles import (
    BOOT_F181_HEX,
    registered_specs,
    registered_targets,
    supported_targets,
)
from tools import REPO_ROOT
from tools.targets.tss3.builders.build_tss3_request_signer import build_request_signer
from tools.targets.tss3.console import render_kit

ROOT = REPO_ROOT
LAUNCHER = ROOT / "exploit/ram_runtime/tss3_request_signer_launcher.sh"
TARGETS = supported_targets()
RUNTIME_FILES = (
    "tools/__init__.py",
    "tsk/__init__.py",
    "tsk/lib/__init__.py",
    "tsk/lib/programming.py",
    "tsk/lib/diagnostic_route.py",
    "exploit/common/ram_exec.py",
    "exploit/ram_runtime/tss3_request_signer.py",
    "exploit/ram_runtime/tss3_post_install_recovery.py",
    "exploit/ram_runtime/panda_eps.py",
    "exploit/ram_runtime/tss3_panda_lease.sh",
)
# Shared repinned runtime topology: vehicle network + EPS diagnostics on bus 0.
REPINNED_RUNTIME_BUS = 0
UI_RUNTIME_FILES = (
    "exploit/ram_runtime/tss3_request_signer_ui_bringup.py",
    "exploit/ram_runtime/tss3_startup_programming.py",
)


def _require_empty(out: Path) -> None:
    if out.exists() and any(path.is_file() for path in out.rglob("*")):
        raise RuntimeError(f"refusing nonempty output directory: {out}")


def _copy(src: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)


def _bound_metadata(metadata: dict, record: dict, spec: dict) -> dict:
    """Bind one universal build to an exact target on the repinned runtime bus."""
    runtime = record["ram_runtime"]
    return {
        "schema": metadata["schema"],
        "toolchain": metadata["toolchain"],
        "debug": metadata["debug"],
        "target": {
            "name": record["name"],
            "application_f181_hex": runtime["application_f181_hex"],
            "boot_f181_hex": BOOT_F181_HEX,
        },
        "request": {
            **metadata["request"],
            "bus": REPINNED_RUNTIME_BUS,
        },
        "response": {
            **metadata["response"],
            "bus": REPINNED_RUNTIME_BUS,
        },
        "state": {
            **metadata["state"],
            "base": f"0x{int(spec['contract']['memory']['state_base']):08X}",
            "layout": spec["contract"]["memory"]["layout"],
        },
        "authenticated_payload": {
            "path": "payload.bin",
            "sha256": metadata["authenticated_payload"]["sha256"],
        },
    }


def _package(target: str, out: Path, metadata: dict, payload_path: Path) -> dict:
    _require_empty(out)
    out.mkdir(parents=True, exist_ok=True)
    bundle = out / "bundle"
    bundle.mkdir()
    (bundle / "request_signer.json").write_text(
        json.dumps(metadata, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    _copy(payload_path, bundle / "payload.bin")
    debug_directory = metadata["debug"]["directory"]
    shutil.copytree(payload_path.parent / debug_directory, bundle / debug_directory)

    for rel in RUNTIME_FILES:
        _copy(ROOT / rel, out / "runtime" / rel)
    for rel in UI_RUNTIME_FILES:
        _copy(ROOT / rel, out / "runtime" / rel)

    _copy(LAUNCHER, out / "tss3-request-signer")
    (out / "tss3-request-signer").chmod(0o755)
    return {
        "schema": "tss3-ram-kit-v1",
        "target": target,
        "codec": metadata["request"]["codec"],
        "payload_sha256": metadata["authenticated_payload"]["sha256"],
    }


def build(target: str, out: Path) -> dict:
    if target not in TARGETS:
        raise RuntimeError(f"unsupported RAM-runtime target: {target}")
    _require_empty(out)
    record = {**registered_targets()[target], "name": target}
    spec = registered_specs()[target]
    with tempfile.TemporaryDirectory(prefix="tss3-ram-kit-") as td:
        metadata = build_request_signer(target=target, output_dir=Path(td))
        payload = Path(td) / metadata["authenticated_payload"]["path"]
        return _package(target, out, _bound_metadata(metadata, record, spec), payload)


def build_set(out: Path) -> dict:
    _require_empty(out)
    records = registered_targets()
    specs = registered_specs()
    with tempfile.TemporaryDirectory(prefix="tss3-ram-kit-") as td:
        metadata = build_request_signer(
            target=TARGETS[0],
            output_dir=Path(td),
            stem="tss3_request_signer",
        )
        payload = Path(td) / metadata["authenticated_payload"]["path"]
        kits = {}
        for target in TARGETS:
            kits[target] = _package(
                target,
                out / target,
                _bound_metadata(
                    metadata,
                    {**records[target], "name": target},
                    specs[target],
                ),
                payload,
            )
    return {
        "schema": "tss3-ram-kit-set-v1",
        "codec": metadata["request"]["codec"],
        "kits": kits,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", choices=(*TARGETS, "all"), required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--json", action="store_true", help="print the full JSON result instead of the human summary")
    args = parser.parse_args()
    try:
        result = (
            build_set(args.out)
            if args.target == "all"
            else build(args.target, args.out)
        )
    except (OSError, RuntimeError, ValueError) as exc:
        print(f"refusing: {exc}", file=sys.stderr)
        return 2
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(render_kit(result, str(args.out)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
