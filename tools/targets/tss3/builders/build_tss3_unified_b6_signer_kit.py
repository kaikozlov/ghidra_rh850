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
        built = Path(td)
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
    for rel in RUNTIME_FILES: copy(ROOT / rel, out / "runtime" / rel)
    copy(LAUNCHER, out / "tss3-unified-signer"); (out / "tss3-unified-signer").chmod(0o755)
    commit = source_commit(); (out / "SOURCE_COMMIT").write_text(commit + "\n", encoding="utf-8")
    testing = f"""Unified TSS3 functional-0x777 signer test kit\nTarget: {target}\nSource commit: {commit}\n\nPreferred tester flow:\n1. ./tss3-unified-signer doctor\n2. Put the vehicle in NRTD/READY=0 and Park.\n3. ./tss3-unified-signer bringup /tmp/tss3-bringup\n   The command proves the stock 0x777 mailbox, installs and attests the volatile resident, then pauses.\n   Transition directly to READY/Park WITHOUT powering the EPS off, remain stationary, and press Enter.\n   On Camry/Crown, qualification transfers the padded helper over functional C6, reads it back byte-exact, and arms it. Camry then proves stock authenticated route44 publication while released.\n   On exact Camry, bringup next performs the live-proven same-ignition recovery automatically: Brake/EPB 0x7B0 enters 10 02 then 11 01 and must return exact F181 F152633K0000; only then FRC 0x792 enters 10 02 then 11 01 and must return exact F181 8646F3315000. The final FRC 1903/1905/1906 state must show DRCC permission restored. EPS is never reset or power-cycled, and bringup re-reads resident status afterward.\n   Continue only if the complete sequence passes.\n4. READY/Park/stationary: ./tss3-unified-signer replace-current /tmp/tss3-replace-current.json\n   This derives the live 0x025 steering angle, verifies fresh healthy stationary/Park state, sends one no-offset C7 generation, then sequence zero to release.\n5. STOP after stationary qualification. Do not infer road readiness from a passing signer pulse; Corolla's native-shape stock-ACC cancel carrier is implemented but receiver acceptance, physical steering, and stock-system coexistence remain vehicle qualification items.\n6. Once those vehicle-level contracts are closed, normal openpilot integration streams changed nonzero C7 generations on functional 0x777 and sends sequence zero when lateral is inactive.\n\nCamry F33 recovery note: `recover-drcc` is retained only to preserve/clear bootstrap\nDTC evidence; DTC clear alone does not restore the state machine. The live-proven\nrecovery is `restart-control-domains`: exact Brake/EPB reset first, exact FRC reset\nsecond, with no SecurityAccess and no EPS reset/power cycle. Normal Camry `bringup`\nexecutes this recovery automatically after EPS qualification and then verifies the\nresident remains present.\n\nCamry F33 prevention experiment: on a fresh ignition cycle in NRTD/Park,\n`./tss3-unified-signer bringup-stale-030-bridge /tmp/tss3-030-bridge` captures the\nlast genuine native bus1 0x030, repeats that exact frame at 100 Hz only across the\nEPS programming/bootstrap outage, stops on the first resumed native 0x030, and reads\nFRC 0x1903/0x1905/0x1906 without clearing DTCs. The guided command refuses to continue\nto READY qualification unless Cruise Control Permission remains allowed and ACC Not\nAvailable remains clear. This is a bounded stale-SecOC liveness discriminator, not a\nproduction keepalive.\n\nManual equivalent on Camry: preflight -> install in NRTD -> direct NRTD->READY without OFF -> qualify EPS -> restart-control-domains (Brake then FRC) -> status.\nC7 is the only recurring steering-control tag. Camry/Crown field kits use functional C6 only as the post-startup helper loader; Corolla embeds the helper in the authenticated payload. Camry field runtime is post-authenticated route44 application override and does not invoke command 5 during lateral control. No packaged field path performs boot-context GlobalRAM helper staging. The experimental all-target self-dispatching/GlobalRAM payload stays separate from this tester path. This runtime does not patch CodeFlash and retains the legacy target-specific signer for recovery.\nA full EPS power cycle removes the RAM resident and requires bringup again.\n"""
    (out / "TESTING.txt").write_text(testing, encoding="utf-8")
    manifest = {
        "schema": "tss3-unified-b6-signer-kit-v1", "created_at": datetime.now(UTC).isoformat(timespec="seconds"),
        "source_commit": commit, "target": meta["target"], "control": meta["control"],
        "install_strategy": meta["install_strategy"], "runtime_backend": meta.get("runtime_backend"), "review_status": meta["review_status"],
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
