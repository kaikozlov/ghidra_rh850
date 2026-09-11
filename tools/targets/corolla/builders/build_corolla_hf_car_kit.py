#!/usr/bin/env python3
"""Build a minimal in-car RAM-signer kit for one exact Corolla H/F target."""
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
BUILDER = ROOT / "exploit/ephemeral_runtime/build_corolla_hf_b6_inline_signer.py"
LAUNCHER = ROOT / "exploit/ephemeral_runtime/corolla_hf_b6_inline_signer_launcher.sh"
RUNTIME_FILES = (
    "exploit/common/ram_exec.py",
    "exploit/ephemeral_runtime/corolla_hf_b6_inline_signer.py",
    "exploit/ephemeral_runtime/f33_panda_lease.sh",
    "exploit/followups/xcp_read_probe.py",
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def copy(src: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)


def build(target: str, out: Path) -> dict:
    with tempfile.TemporaryDirectory(prefix="corolla-hf-kit-") as td:
        built = Path(td)
        subprocess.run(
            [sys.executable, str(BUILDER), "--target", target, "--output-dir", str(built)],
            cwd=ROOT, check=True, capture_output=True, text=True,
        )
        prefix = f"corolla_{target}_b6_inline_signer"
        payload_src = built / f"{prefix}_payload.bin"
        meta_src = built / f"{prefix}.json"
        meta = json.loads(meta_src.read_text(encoding="utf-8"))

        ram = out / "ram_payloads"
        payload_dst = ram / "corolla_hf_b6_inline_signer_payload.bin"
        meta_dst = ram / "corolla_hf_b6_inline_signer.json"
        copy(payload_src, payload_dst)
        copy(meta_src, meta_dst)

    for relative in RUNTIME_FILES:
        copy(ROOT / relative, out / "runtime" / relative)
    launcher = out / "corolla-tss3-signer"
    copy(LAUNCHER, launcher)
    launcher.chmod(0o755)

    manifest = {
        "schema": "corolla-hf-car-kit-v1",
        "created_at": datetime.now(UTC).isoformat(timespec="seconds"),
        "target": meta["target"],
        "control": meta["control"],
        "review_status": meta["review_status"],
        "files": {
            str(path.relative_to(out)): {"size": path.stat().st_size, "sha256": sha256(path)}
            for path in sorted(p for p in out.rglob("*") if p.is_file())
        },
        "usage": [
            "copy this directory to comma hardware",
            "./corolla-tss3-signer doctor",
            "NRTD: ./corolla-tss3-signer install /tmp/corolla-signer-install.json",
            "READY/Park: ./corolla-tss3-signer status /tmp/corolla-signer-status.json",
            "full EPS power cycle removes the resident",
        ],
    }
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", choices=("8965H1202000", "8965F1208000"), required=True)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    out = args.out or ROOT / "build/out" / f"corolla-{args.target}-car-kit"
    print(json.dumps(build(args.target, out), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
