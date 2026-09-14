#!/usr/bin/env python3
"""Build a self-contained exact-8965F3012000 volatile signer field kit."""
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

ROOT = Path(__file__).resolve().parents[4]
BUILDER = ROOT / "exploit/ephemeral_runtime/build_crown_f30_b6_inline_signer.py"
LAUNCHER = ROOT / "exploit/ephemeral_runtime/crown_f30_b6_inline_signer_launcher.sh"
RUNTIME_FILES = (
    "exploit/common/ram_exec.py",
    "exploit/ephemeral_runtime/crown_f30_b6_inline_signer.py",
    "exploit/ephemeral_runtime/camry_f33_runtime_monitor.py",
    "exploit/ephemeral_runtime/camry_f33_runtime_replay_discriminator.py",
    "exploit/ephemeral_runtime/f33_panda_lease.sh",
    "tools/targets/crown/live/crown_f30_sideband_preflight.py",
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def copy(src: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)


def build(out: Path) -> dict:
    if out.exists():
        retained = sorted(p for p in out.rglob("*") if p.is_file())
        if retained:
            preview = ", ".join(str(p.relative_to(out)) for p in retained[:5])
            raise RuntimeError(f"refusing nonempty Crown kit directory {out}: {preview}")
    with tempfile.TemporaryDirectory(prefix="crown-f30-kit-") as td:
        built = Path(td)
        result = subprocess.run(
            [sys.executable, str(BUILDER), "--output-dir", str(built)],
            cwd=ROOT, check=True, capture_output=True, text=True,
        )
        meta = json.loads(result.stdout)
        ram = out / "ram_payloads"
        for name in (
            "crown_f30_b6_inline_signer_payload.bin",
            "crown_f30_b6_inline_signer_helper_padded.bin",
            "crown_f30_b6_inline_signer.json",
        ):
            copy(built / name, ram / name)

    for relative in RUNTIME_FILES:
        copy(ROOT / relative, out / "runtime" / relative)
    launcher = out / "crown-tss3-signer"
    copy(LAUNCHER, launcher)
    launcher.chmod(0o755)

    manifest = {
        "schema": "crown-f30-car-kit-v1",
        "created_at": datetime.now(UTC).isoformat(timespec="seconds"),
        "target": meta["target"],
        "review_status": meta["review_status"],
        "control": meta["loader"],
        "files": {
            str(path.relative_to(out)): {"size": path.stat().st_size, "sha256": sha256(path)}
            for path in sorted(p for p in out.rglob("*") if p.is_file())
        },
        "usage": [
            "copy this directory to comma hardware",
            "./crown-tss3-signer doctor",
            "NRTD/Park: ./crown-tss3-signer preflight /tmp/crown-preflight.json",
            "continue only if safe_to_experiment=true",
            "NRTD/Park: ./crown-tss3-signer install /tmp/crown-install.json",
            "transition directly to READY/Park without EPS OFF",
            "./crown-tss3-signer load-arm /tmp/crown-arm.json",
            "continue only if native_verification.native_verified=true",
            "READY/Park/stationary: ./crown-tss3-signer replace-current /tmp/crown-replace-current.json",
            "replace-current derives the nearest B6 raw target from a fresh Crown 0x025 measured angle; full EPS power cycle removes the resident",
        ],
    }
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return manifest


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", type=Path, default=ROOT / "build/out/crown-8965F3012000-car-kit")
    args = ap.parse_args()
    try:
        manifest = build(args.out)
    except (OSError, RuntimeError, subprocess.CalledProcessError, json.JSONDecodeError) as exc:
        print(f"refusing: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(manifest, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
