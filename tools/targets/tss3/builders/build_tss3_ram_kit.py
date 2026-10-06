#!/usr/bin/env python3
"""Package the canonical TSS3 RAM-resident request signer for exact targets."""
from __future__ import annotations

import argparse
import json
import shutil
import sys
import tempfile
from pathlib import Path

from exploit.ephemeral_runtime.build_tss3_request_signer import (
    DEFAULT_CODEC,
    build_request_signer,
)
from exploit.ram_runtime.target_profiles import (
    BOOT_F181_HEX,
    registered_targets,
    supported_targets,
)
from tools import REPO_ROOT

ROOT = REPO_ROOT
LAUNCHER = ROOT / "exploit/ephemeral_runtime/tss3_request_signer_launcher.sh"
TARGETS = supported_targets()
CODECS = (DEFAULT_CODEC, "compact")
RUNTIME_FILES = (
    "tsk/__init__.py",
    "tsk/lib/__init__.py",
    "tsk/lib/programming.py",
    "tsk/lib/diagnostic_route.py",
    "exploit/common/ram_exec.py",
    "exploit/ephemeral_runtime/tss3_request_signer.py",
    "exploit/ephemeral_runtime/tss3_post_install_recovery.py",
    "exploit/ephemeral_runtime/panda_eps.py",
    "exploit/ephemeral_runtime/tss3_panda_lease.sh",
)
# Shared repinned runtime topology: vehicle network + EPS diagnostics on bus 0.
REPINNED_RUNTIME_BUS = 0
UI_RUNTIME_FILES = (
    "exploit/ephemeral_runtime/tss3_request_signer_ui_bringup.py",
    "exploit/ephemeral_runtime/tss3_startup_programming.py",
)
COMPACT_RUNTIME_FILE = "exploit/ephemeral_runtime/tss3_request_signer_compact.py"


def _require_empty(out: Path) -> None:
    if out.exists() and any(path.is_file() for path in out.rglob("*")):
        raise RuntimeError(f"refusing nonempty output directory: {out}")


def _copy(src: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)


def _bound_metadata(metadata: dict, record: dict) -> dict:
    """Bind the universal build to one target's identity on the shared runtime bus.

    Every maintained TSS3 vehicle runs the Toyota-B repin: the vehicle network
    and EPS diagnostics (signer request/response, 0x7A1 session traffic) sit on
    Panda bus 0 (opendbc tss3.py topology). The registry's per-target
    request_bus/response_bus are stock-vehicle observations kept as provenance
    and must never select a runtime bus, so all kits bind the repinned bus.
    """
    runtime = record["ram_runtime"]
    return {
        "schema": metadata["schema"],
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
        "state": metadata["state"],
        "authenticated_payload": {
            "path": "payload.bin",
            "sha256": metadata["authenticated_payload"]["sha256"],
        },
    }


def _package(target: str, out: Path, codec: str, metadata: dict, payload_path: Path) -> dict:
    _require_empty(out)
    out.mkdir(parents=True, exist_ok=True)
    bundle = out / "bundle"
    bundle.mkdir()
    (bundle / "request_signer.json").write_text(
        json.dumps(metadata, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    _copy(payload_path, bundle / "payload.bin")

    for rel in RUNTIME_FILES:
        _copy(ROOT / rel, out / "runtime" / rel)
    for rel in UI_RUNTIME_FILES:
        _copy(ROOT / rel, out / "runtime" / rel)
    if codec == "compact":
        _copy(ROOT / COMPACT_RUNTIME_FILE, out / "runtime" / COMPACT_RUNTIME_FILE)

    _copy(LAUNCHER, out / "tss3-request-signer")
    (out / "tss3-request-signer").chmod(0o755)
    return {
        "schema": "tss3-ram-kit-v1",
        "target": target,
        "codec": codec,
        "payload_sha256": metadata["authenticated_payload"]["sha256"],
    }


def build(target: str, out: Path, codec: str = DEFAULT_CODEC) -> dict:
    if target not in TARGETS:
        raise RuntimeError(f"unsupported RAM-runtime target: {target}")
    if codec not in CODECS:
        raise RuntimeError(f"unsupported request codec: {codec}")
    _require_empty(out)
    record = {**registered_targets()[target], "name": target}
    with tempfile.TemporaryDirectory(prefix="tss3-ram-kit-") as td:
        metadata = build_request_signer(target=target, codec=codec, output_dir=Path(td))
        payload = Path(td) / metadata["authenticated_payload"]["path"]
        return _package(target, out, codec, _bound_metadata(metadata, record), payload)


def build_set(out: Path, codec: str = DEFAULT_CODEC) -> dict:
    if codec not in CODECS:
        raise RuntimeError(f"unsupported request codec: {codec}")
    _require_empty(out)
    records = registered_targets()
    with tempfile.TemporaryDirectory(prefix="tss3-ram-kit-") as td:
        metadata = build_request_signer(target=TARGETS[0], codec=codec, output_dir=Path(td))
        payload = Path(td) / metadata["authenticated_payload"]["path"]
        kits = {}
        for target in TARGETS:
            kits[target] = _package(
                target,
                out / target,
                codec,
                _bound_metadata(metadata, {**records[target], "name": target}),
                payload,
            )
    return {"schema": "tss3-ram-kit-set-v1", "codec": codec, "kits": kits}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", choices=(*TARGETS, "all"), required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument(
        "--codec", choices=CODECS, default=DEFAULT_CODEC,
        help="four-frame is the default; compact is experimental and explicit",
    )
    args = parser.parse_args()
    try:
        result = (
            build_set(args.out, args.codec)
            if args.target == "all"
            else build(args.target, args.out, args.codec)
        )
    except (OSError, RuntimeError, ValueError) as exc:
        print(f"refusing: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
