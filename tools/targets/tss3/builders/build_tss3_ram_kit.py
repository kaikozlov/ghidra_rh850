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

from tools import REPO_ROOT
from exploit.ram_runtime.target_profiles import supported_targets

ROOT = REPO_ROOT
BUILDER = ROOT / "exploit/ephemeral_runtime/build_tss3_request_signer.py"
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


def build(target: str, out: Path, codec: str = DEFAULT_CODEC) -> dict:
    if target not in TARGETS:
        raise RuntimeError(f"unsupported RAM-runtime target: {target}")
    if codec not in CODECS:
        raise RuntimeError(f"unsupported request codec: {codec}")
    _require_empty(out)

    with tempfile.TemporaryDirectory(prefix="tss3-ram-kit-") as td:
        built = Path(td) / "request-signer"
        proc = subprocess.run(
            [
                sys.executable, str(BUILDER), "--target", target,
                "--codec", codec, "--output-dir", str(built),
            ],
            cwd=ROOT, check=True, capture_output=True, text=True,
        )
        metadata = json.loads(proc.stdout)
        stem = f"{target.replace('-', '_')}_request_signer"
        if codec != DEFAULT_CODEC:
            stem += "_compact"
        metadata_path = built / f"{stem}.json"
        payload_path = built / f"{stem}_payload.bin"
        if json.loads(metadata_path.read_text(encoding="utf-8")) != metadata:
            raise RuntimeError("printed metadata differs from the built artifact")
        if metadata.get("target", {}).get("name") != target:
            raise RuntimeError("built metadata target differs from requested target")
        if metadata.get("request", {}).get("codec") != codec:
            raise RuntimeError("built metadata codec differs from requested codec")

        out.mkdir(parents=True, exist_ok=True)
        for path in built.iterdir():
            if path.is_file():
                copy(path, out / "bundle" / path.name)
        copy(metadata_path, out / "bundle/request_signer.json")
        copy(payload_path, out / "bundle/payload.bin")

    for rel in RUNTIME_FILES:
        copy(ROOT / rel, out / "runtime" / rel)
    if codec == "compact":
        copy(ROOT / COMPACT_RUNTIME_FILE, out / "runtime" / COMPACT_RUNTIME_FILE)

    copy(LAUNCHER, out / "tss3-request-signer")
    (out / "tss3-request-signer").chmod(0o755)
    commit = source_commit()
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
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8",
    )
    return manifest


def build_set(out: Path, codec: str = DEFAULT_CODEC) -> dict:
    _require_empty(out)
    kits = {}
    for target in TARGETS:
        target_out = out / target
        manifest = build(target, target_out, codec)
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
        "source_commit": source_commit(),
        "kits": kits,
    }
    out.mkdir(parents=True, exist_ok=True)
    (out / "manifest.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8",
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
