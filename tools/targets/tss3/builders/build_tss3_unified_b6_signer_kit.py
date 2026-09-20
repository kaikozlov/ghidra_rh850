#!/usr/bin/env python3
"""Package one exact-target unified functional-0x777 TSS3 signer test kit."""
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
BUILDER = ROOT / "exploit/ephemeral_runtime/build_tss3_unified_b6_signer.py"
ORACLE_BUILDER = ROOT / "exploit/ephemeral_runtime/build_camry_f33_08a_classic_oracle.py"
LAUNCHER = ROOT / "exploit/ephemeral_runtime/tss3_unified_b6_signer_launcher.sh"
TARGETS = (
    "camry-8965F3307000", "corolla-8965H1202000",
    "corolla-8965F1208000", "crown-8965F3012000",
)
RUNTIME_FILES = (
    "tsk/__init__.py", "tsk/lib/__init__.py", "tsk/lib/programming.py", "tsk/lib/diagnostic_route.py",
    "exploit/common/ram_exec.py",
    "exploit/ephemeral_runtime/tss3_unified_b6_signer.py",
    "exploit/ephemeral_runtime/camry_f33_post_install_recovery.py",
    "exploit/ephemeral_runtime/camry_f33_runtime_monitor.py",
    "exploit/ephemeral_runtime/camry_f33_runtime_replay_discriminator.py",
    "exploit/ephemeral_runtime/f33_panda_lease.sh",
)
CAMRY_ORACLE_RUNTIME_FILES = (
    "exploit/ephemeral_runtime/camry_f33_08a_classic_oracle.py",
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def copy(src: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True); shutil.copy2(src, dst)


def source_commit() -> str:
    return subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, check=True, capture_output=True, text=True).stdout.strip()


def build(target: str, out: Path) -> dict:
    if out.exists() and any(p.is_file() for p in out.rglob("*")):
        raise RuntimeError(f"refusing nonempty output directory: {out}")
    with tempfile.TemporaryDirectory(prefix="tss3-unified-kit-") as td:
        built = Path(td) / "signer"
        oracle_built = Path(td) / "oracle"
        proc = subprocess.run(
            [sys.executable, str(BUILDER), "--target", target, "--bootstrap", "exact-target", "--output-dir", str(built)],
            cwd=ROOT, check=True, capture_output=True, text=True,
        )
        meta = json.loads(proc.stdout)
        meta_path = built / f"{target.replace('-', '_')}_unified_b6_signer.json"
        if not meta_path.is_file():
            raise RuntimeError(f"exact target metadata missing: {meta_path}")
        out.mkdir(parents=True, exist_ok=True)
        for p in built.iterdir():
            if p.is_file(): copy(p, out / "bundle" / p.name)
        copy(out / "bundle" / meta_path.name, out / "bundle/unified.json")
        if target == "camry-8965F3307000":
            oracle_proc = subprocess.run(
                [sys.executable, str(ORACLE_BUILDER), "--output-dir", str(oracle_built)],
                cwd=ROOT, check=True, capture_output=True, text=True,
            )
            oracle_meta = json.loads(oracle_proc.stdout)
            oracle_meta_path = oracle_built / "camry_f33_08a_classic_oracle.json"
            oracle_payload_path = oracle_built / "camry_f33_08a_classic_oracle_payload.bin"
            if json.loads(oracle_meta_path.read_text(encoding="utf-8")) != oracle_meta:
                raise RuntimeError("classic-oracle printed metadata differs from its artifact")
            copy(oracle_meta_path, out / "bundle/oracle/classic.json")
            copy(oracle_payload_path, out / "bundle/oracle/classic_payload.bin")
    for rel in RUNTIME_FILES: copy(ROOT / rel, out / "runtime" / rel)
    if target == "camry-8965F3307000":
        for rel in CAMRY_ORACLE_RUNTIME_FILES: copy(ROOT / rel, out / "runtime" / rel)
    copy(LAUNCHER, out / "tss3-unified-signer"); (out / "tss3-unified-signer").chmod(0o755)
    commit = source_commit(); (out / "SOURCE_COMMIT").write_text(commit + "\n", encoding="utf-8")
    if target == "camry-8965F3307000":
        flow = """2. Choose exactly one runtime architecture.
   Current relay-correct 0x08A request plane: ./tss3-unified-signer oracle-bringup /tmp/tss3-oracle-bringup
   Direct-B6 signer, ordinary harness: ./tss3-unified-signer --topology stock bringup /tmp/tss3-bringup
   Direct-B6 signer, relay-correct repin: ./tss3-unified-signer --topology camry-post-repin bringup /tmp/tss3-bringup
3. For signer bringup, put the vehicle in Park and keep it stationary; READY is allowed.
4. ./tss3-unified-signer [--topology ...] bringup /tmp/tss3-bringup"""
    else:
        flow = """2. Put the vehicle in Park and keep it stationary; READY is allowed.
3. ./tss3-unified-signer bringup /tmp/tss3-bringup"""
    testing = f"""Unified TSS3 functional-0x777 signer test kit
Target: {target}
Source commit: {commit}

Preferred tester flow:
1. ./tss3-unified-signer doctor
{flow}
   The command takes one cooperative Panda lease, proves the stock 0x777 mailbox, installs/attests the volatile EPS resident, and keeps that same lease across all operator-paced stages until the command exits.
   Keep EPS powered; if not already READY, enter READY/Park, remain stationary, and press Enter to qualify the runtime helper.
   On exact Camry, bringup then becomes deliberately operator-paced while retaining the same Panda lease: it waits for you before restarting Brake/EPB only. The Brake stage uses the exact field-proven standalone UdsClient procedure: 10 02 with timeout 1.0/2.0, up to two fresh-client 11 01 attempts at 0.35/0.35 with a 50-ms pause after the first exception, then a 2-s quiet wait and F181 polling every 250 ms using 0.25/0.25 clients for up to 6 s. No extra EPS/Brake pre-reads, custom ISO-TP requests, or canfd_auto changes are inserted. Only after you decide the vehicle has had enough quiet time does bringup restart FRC. After the FRC application returns it waits for you to decide when the Toyota network has settled before final DRCC/EPS-resident verification. There is no chained automatic peer reset and no DTC clear.
   The individual Camry commands are also exposed as `restart-brake`, `restart-frc`, and `recovery-state`.
Next, READY/Park/stationary: ./tss3-unified-signer [--topology ...] replace-current /tmp/tss3-replace-current.json
   This derives the live 0x025 steering angle, verifies fresh healthy stationary/Park state, sends one no-offset C7 generation, then sequence zero to release.

Camry F33 recovery note: the field result is timing-sensitive. Exact application F181 returning proves the ECU application is back, not that every peer-facing state machine has finished initializing. The maintained guided flow therefore lets each stage finish while retaining one cooperative Panda lease; Panda ownership is not treated as a recovery primitive. `recover-drcc` remains legacy DTC-evidence tooling and is not part of this recovery.

Manual equivalent on Camry: Park/stationary preflight -> install (READY allowed) -> keep EPS powered -> qualify EPS -> wait -> restart-brake -> wait -> restart-frc -> wait -> recovery-state -> status.
C7 is the only recurring steering-control tag. Camry/Crown field kits use functional C6 only as the post-startup helper loader; Corolla embeds its helper in the authenticated payload. Camry field runtime is post-authenticated route44 application override and does not invoke command 5 during lateral control. This runtime does not patch CodeFlash.
A full EPS power cycle removes the RAM resident and requires bringup again.
"""
    (out / "TESTING.txt").write_text(testing, encoding="utf-8")
    oracle = None
    if target == "camry-8965F3307000":
        oracle = {
            "transport": "extended classic 0x1FDC0002 -> 0x1FE00002 on post-repin Panda bus0",
            "metadata": "bundle/oracle/classic.json",
            "payload": "bundle/oracle/classic_payload.bin",
            "peer_recovery": "Brake/EPB -> FRC while retaining one Panda lease",
        }
    manifest = {
        "schema": "tss3-unified-b6-signer-kit-v1", "created_at": datetime.now(UTC).isoformat(timespec="seconds"),
        "source_commit": commit, "target": meta["target"], "control": meta["control"],
        "install_strategy": meta["install_strategy"], "runtime_backend": meta.get("runtime_backend"), "review_status": meta["review_status"],
        "camry_classic_08a_oracle": oracle,
        "files": {str(p.relative_to(out)): {"size": p.stat().st_size, "sha256": sha256(p)} for p in sorted(out.rglob("*")) if p.is_file()},
    }
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return manifest


def main() -> int:
    ap=argparse.ArgumentParser(description=__doc__); ap.add_argument("--target", choices=TARGETS, required=True); ap.add_argument("--out", type=Path, required=True); args=ap.parse_args()
    try: result=build(args.target,args.out)
    except (OSError,RuntimeError,subprocess.CalledProcessError,json.JSONDecodeError) as exc:
        print(f"refusing: {exc}", file=sys.stderr); return 2
    print(json.dumps(result, indent=2, sort_keys=True)); return 0

if __name__ == "__main__": raise SystemExit(main())
