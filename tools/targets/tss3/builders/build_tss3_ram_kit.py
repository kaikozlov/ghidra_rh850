#!/usr/bin/env python3
"""Package the canonical TSS3 RAM-resident request signer for exact targets."""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
from datetime import UTC, datetime
from pathlib import Path

from exploit.ephemeral_runtime import build_tss3_request_signer as signer_builder
from exploit.ram_runtime.target_profiles import registered_targets, supported_targets
from tools import REPO_ROOT

ROOT = REPO_ROOT
LAUNCHER = ROOT / "exploit/ephemeral_runtime/tss3_request_signer_launcher.sh"
TARGETS = supported_targets()
DEFAULT_CODEC = "four-frame"
CODECS = (DEFAULT_CODEC, "compact")
RUNTIME_FILES = (
    "tsk/__init__.py",
    "tsk/lib/__init__.py",
    "tsk/lib/programming.py",
    "tsk/lib/diagnostic_route.py",
    "exploit/common/ram_exec.py",
    "exploit/ephemeral_runtime/tss3_request_signer.py",
    "exploit/ephemeral_runtime/tss3_post_install_recovery.py",
    "exploit/ephemeral_runtime/camry_f33_runtime_monitor.py",
    "exploit/ephemeral_runtime/camry_f33_runtime_replay_discriminator.py",
    "exploit/ephemeral_runtime/tss3_panda_lease.sh",
)
CAMRY_UI_RUNTIME_FILES = (
    "exploit/ephemeral_runtime/camry_f33_request_signer_ui_bringup.py",
    "exploit/ephemeral_runtime/camry_f33_startup_programming.py",
)
COMPACT_RUNTIME_FILE = "exploit/ephemeral_runtime/tss3_request_signer_compact.py"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def copy(src: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)


def source_commit() -> str:
    return subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, check=True,
        capture_output=True, text=True,
    ).stdout.strip()


def _require_empty(out: Path) -> None:
    if out.exists() and any(path.is_file() for path in out.rglob("*")):
        raise RuntimeError(f"refusing nonempty output directory: {out}")


def _build_once(target: str, built: Path, codec: str) -> tuple[dict, Path]:
    proc = subprocess.run(
        [
            sys.executable,
            str(signer_builder.BUILDER),
            "--target",
            target,
            "--codec",
            codec,
            "--output-dir",
            str(built),
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    metadata = json.loads(proc.stdout)
    return metadata, built / metadata["authenticated_payload"]["path"]


def _bind_target(metadata: dict, target: str, record: dict) -> dict:
    bound = {
        **metadata,
        "request": dict(metadata["request"]),
        "response": dict(metadata["response"]),
    }
    runtime = record["ram_runtime"]
    bound["target"] = {
        "name": target,
        "vehicle": record["vehicle"],
        "profile": runtime["profile"],
        "software_id": record["software_id"],
        "codeflash_sha256": record["codeflash_sha256"],
        "application_f181_hex": runtime["application_f181_hex"],
        "boot_f181_hex": signer_builder.BOOT_F181_HEX,
        "registered": True,
    }
    bound["request"]["bus"] = runtime["request_bus"]
    bound["response"]["bus"] = runtime["response_bus"]
    return bound


def _package(
    target: str,
    out: Path,
    codec: str,
    metadata: dict,
    payload_path: Path,
    commit: str,
) -> dict:
    metadata = {
        "schema": metadata["schema"],
        "target": metadata["target"],
        "request": metadata["request"],
        "response": metadata["response"],
        "state": metadata["state"],
        "resident": {"sha256": metadata["resident"]["sha256"]},
        "helper": {"sha256": metadata["helper"]["sha256"]},
        "authenticated_payload": {
            **metadata["authenticated_payload"],
            "path": "payload.bin",
        },
    }
    out.mkdir(parents=True, exist_ok=True)
    bundle = out / "bundle"
    bundle.mkdir()
    (bundle / "request_signer.json").write_text(
        json.dumps(metadata, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    copy(payload_path, bundle / "payload.bin")

    for rel in RUNTIME_FILES:
        copy(ROOT / rel, out / "runtime" / rel)
    if target == "camry-8965F3307000":
        for rel in CAMRY_UI_RUNTIME_FILES:
            copy(ROOT / rel, out / "runtime" / rel)
    if codec == "compact":
        copy(ROOT / COMPACT_RUNTIME_FILE, out / "runtime" / COMPACT_RUNTIME_FILE)

    copy(LAUNCHER, out / "tss3-request-signer")
    (out / "tss3-request-signer").chmod(0o755)
    (out / "SOURCE_COMMIT").write_text(commit + "\n", encoding="utf-8")
    (out / "TESTING.txt").write_text(
        "\n".join((
            "TSS3 RAM-resident request-signer kit",
            f"Target: {target}",
            f"Codec: {codec}",
            f"Source commit: {commit}",
            "",
            "This kit is exact-target-bound. Do not use it on another EPS identity.",
            "1. Run: ./tss3-request-signer doctor",
            "2. In NRTD/READY=0, Park, and stationary, run: ./tss3-request-signer install",
            "3. Transition directly to READY/Park without powering EPS off.",
            "4. Run: ./tss3-request-signer self-test",
            "5. Optional parked throughput gate: ./tss3-request-signer benchmark-100hz 200",
            "",
            "The default four-frame standard-0x777 request transports all 28 application bytes.",
            "The standard-0x7A9 response returns status plus FV4||MAC28.",
            "The resident is volatile; a full EPS power cycle removes it.",
            "No CodeFlash write is performed.",
            "",
        )),
        encoding="utf-8",
    )

    manifest = {
        "schema": "tss3-ram-kit-v1",
        "created_at": datetime.now(UTC).isoformat(timespec="seconds"),
        "source_commit": commit,
        "payload": "tss3-request-signer",
        "target": metadata["target"],
        "request": metadata["request"],
        "response": metadata["response"],
        "artifacts": {
            "metadata": "bundle/request_signer.json",
            "payload": "bundle/payload.bin",
        },
        "files": {
            str(path.relative_to(out)): {
                "size": path.stat().st_size,
                "sha256": sha256(path),
            }
            for path in sorted(out.rglob("*"))
            if path.is_file()
        },
    }
    (out / "manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return manifest


def build(target: str, out: Path, codec: str = DEFAULT_CODEC) -> dict:
    if target not in TARGETS:
        raise RuntimeError(f"unsupported RAM-runtime target: {target}")
    if codec not in CODECS:
        raise RuntimeError(f"unsupported request codec: {codec}")
    _require_empty(out)
    with tempfile.TemporaryDirectory(prefix="tss3-ram-kit-") as td:
        metadata, payload_path = _build_once(target, Path(td), codec)
        return _package(target, out, codec, metadata, payload_path, source_commit())


def build_set(out: Path, codec: str = DEFAULT_CODEC) -> dict:
    if codec not in CODECS:
        raise RuntimeError(f"unsupported request codec: {codec}")
    _require_empty(out)
    records = registered_targets()
    first = TARGETS[0]
    commit = source_commit()
    kits = {}
    with tempfile.TemporaryDirectory(prefix="tss3-ram-kit-") as td:
        metadata, payload_path = _build_once(first, Path(td), codec)
        for target in TARGETS:
            target_out = out / target
            manifest = _package(
                target,
                target_out,
                codec,
                _bind_target(metadata, target, records[target]),
                payload_path,
                commit,
            )
            kits[target] = {
                "path": target,
                "manifest": f"{target}/manifest.json",
                "manifest_sha256": sha256(target_out / "manifest.json"),
                "payload": manifest["payload"],
                "codec": manifest["request"]["codec"],
            }
    result = {
        "schema": "tss3-ram-kit-set-v1",
        "created_at": datetime.now(UTC).isoformat(timespec="seconds"),
        "source_commit": commit,
        "kits": kits,
    }
    out.mkdir(parents=True, exist_ok=True)
    (out / "manifest.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return result


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
        result = build_set(args.out, args.codec) if args.target == "all" else build(args.target, args.out, args.codec)
    except (OSError, RuntimeError, subprocess.CalledProcessError, json.JSONDecodeError) as exc:
        print(f"refusing: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
