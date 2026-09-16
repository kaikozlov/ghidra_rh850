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
PROGRAMMING_HELPER_SOURCE_COMMIT = "fdded7183e41bed42d0c74b1a204e8883e543a6f"
PROGRAMMING_HELPER_HASHES = {
    "tsk/lib/programming.py": "ab6aba3b47cd4ab2fa2ad680504dfe9f013c7f936f02169ba3334c1435829905",
    "tsk/lib/diagnostic_route.py": "703739d2257eb27fd0dfbfc60beea3883e661ae05f1ad6b04ee64e57c87c22d9",
}
RUNTIME_FILES = (
    "tsk/__init__.py",
    "tsk/lib/__init__.py",
    "tsk/lib/programming.py",
    "tsk/lib/diagnostic_route.py",
    "exploit/common/ram_exec.py",
    "exploit/ephemeral_runtime/crown_f30_b6_inline_signer.py",
    "exploit/ephemeral_runtime/camry_f33_runtime_monitor.py",
    "exploit/ephemeral_runtime/camry_f33_runtime_replay_discriminator.py",
    "exploit/ephemeral_runtime/f33_panda_lease.sh",
    "tools/targets/crown/live/crown_f30_diag_mailbox_probe.py",
    "tools/targets/crown/live/crown_f30_resident_soak.py",
    "tools/targets/crown/live/crown_f30_authority_probe.py",
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def copy(src: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)


def source_commit() -> str:
    return subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, check=True, capture_output=True, text=True,
    ).stdout.strip()


def testing_text(commit: str) -> str:
    return f"""Toyota Crown 8965F3012000 volatile B6 signer qualification kit
Source commit: {commit}

This is a standalone field qualification kit. It does not require a Crown openpilot port.
It uses the openpilot checkout on the comma device only for the existing Python panda/opendbc environment.
The resident and helper are RAM-only; a full EPS power cycle removes them.
The active control ingress is the stock functional diagnostic path on classic CAN 0x777; this kit does not patch Crown CodeFlash.
The field-proven Toyota programming handoff helper and its diagnostic-route dependency are bundled in runtime/tsk/lib; no TSKM reflash or separate tsk checkout is required.

Run from this directory on the comma device:

  ./crown-tss3-signer doctor

NRTD / Park:

  ./crown-tss3-signer preflight /tmp/crown-preflight.json

Continue only if preflight reports:

  qualified=true
  verdict=stock_functional_mailbox_live

The preflight sends one unsupported functional diagnostic single frame on 0x777, then verifies the stock DCM mailbox through physical SID23. It performs no RAM execution, CodeFlash write, or actuation request.

Still NRTD / Park:

  ./crown-tss3-signer install /tmp/crown-install.json

Require verdict=inline_signer_resident_live_loader_ready.
Then transition directly to READY / Park WITHOUT turning the EPS off.

  ./crown-tss3-signer load-arm /tmp/crown-arm.json

Require native_verification.native_verified=true. This is the no-mutation oracle:
the Crown's own slot-4 signing path must reproduce Toyota's native B6 trailer byte-for-byte.

First bounded replacement, READY / Park / stationary:

  ./crown-tss3-signer replace-current /tmp/crown-replace-current.json

This requests the current measured steering angle, not an offset.

Optional repeated qualification before any openpilot integration:

  ./crown-tss3-signer soak-current /tmp/crown-soak.json

This repeats current-angle replacements for one second with the SAME resident.
It does not intentionally request steering movement.

Only after the current-angle soak is clean, the next moving authority discriminator is:

  ./crown-tss3-signer authority-pulse 1.0 /tmp/crown-authority-plus1.json

This derives a target from the fresh measured 0x025 angle, holds +1.0 degree for
250 ms while the car is already moving, records bus-1 0x025/0x0AA/READY throughout,
then stops C7 so native B6 resumes unchanged. It requires observable wheel motion but
does not hard-code an unrecovered Crown minimum-speed threshold.

At any point, a full EPS power cycle removes the resident/helper and returns the ECU to stock RAM state.
Please retain/send back all /tmp/crown-*.json outputs.
"""


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

    for relative, expected in PROGRAMMING_HELPER_HASHES.items():
        observed = sha256(ROOT / relative)
        if observed != expected:
            raise RuntimeError(f"field-proven programming helper drift: {relative}: {observed} != {expected}")

    commit = source_commit()
    (out / "SOURCE_COMMIT").write_text(commit + "\n", encoding="utf-8")
    (out / "TESTING.txt").write_text(testing_text(commit), encoding="utf-8")

    manifest = {
        "schema": "crown-f30-car-kit-v1",
        "created_at": datetime.now(UTC).isoformat(timespec="seconds"),
        "source_commit": commit,
        "programming_helper": {
            "source_commit": PROGRAMMING_HELPER_SOURCE_COMMIT,
            "files": {relative: {"sha256": expected} for relative, expected in PROGRAMMING_HELPER_HASHES.items()},
        },
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
            "continue only if qualified=true and verdict=stock_functional_mailbox_live",
            "NRTD/Park: ./crown-tss3-signer install /tmp/crown-install.json",
            "transition directly to READY/Park without EPS OFF",
            "./crown-tss3-signer load-arm /tmp/crown-arm.json",
            "continue only if native_verification.native_verified=true",
            "READY/Park/stationary: ./crown-tss3-signer replace-current /tmp/crown-replace-current.json",
            "optional repeated qualification without an openpilot port: ./crown-tss3-signer soak-current /tmp/crown-soak.json",
            "moving authority discriminator only after clean soak: ./crown-tss3-signer authority-pulse 1.0 /tmp/crown-authority-plus1.json",
            "preflight/install/load/control use stock functional UDS 0x777; no Crown CodeFlash patch is used",
            "replace-current/soak-current use the fresh Crown 0x025 measured angle; full EPS power cycle removes the resident",
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
