#!/usr/bin/env python3
"""Build the self-contained exact-F33 in-car lateral/receiver bring-up kit."""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools import build_camry_f33_gate2_semantic_patch as stage2

PROBE = ROOT / "exploit/behavioral_proof/camry_f33_b6_stationary_probe.py"
DEFAULT_OPENPILOT = Path("/Users/kai/dev/inspect/repos/kai-openpilot")
RUNTIME_FILES = [
    "exploit/common/payload_package.py",
    "exploit/common/ram_exec.py",
    "exploit/patcher/patch_config.py",
    "exploit/patcher/build_payload.py",
    "exploit/patcher/deploy.py",
    "exploit/patcher/restore.py",
    "exploit/patcher/post_apply_verify.py",
    "tools/__init__.py",
    "tools/build_secoc_patch_manifest.py",
]


def git_state(repo: Path) -> dict:
    if not (repo / ".git").exists():
        return {"path": str(repo), "available": False}
    head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=repo, text=True).strip()
    status = subprocess.check_output(["git", "status", "--porcelain"], cwd=repo, text=True)
    return {"path": str(repo), "available": True, "head": head, "dirty": bool(status.strip())}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def copy_runtime(out: Path) -> dict[str, dict[str, str]]:
    runtime = out / "runtime"
    result: dict[str, dict[str, str]] = {}
    for rel in RUNTIME_FILES:
        src = ROOT / rel
        dst = runtime / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        result[str(Path("runtime") / rel)] = {"sha256": sha256(dst)}
    return result


def patch_runbook() -> str:
    f181 = stage2.EXPECTED_F181_HEX
    boot_f181 = stage2.EXPECTED_BOOT_F181_HEX
    common = f"""--bus 0 --elm327-param 1 --uds-variant old --cpu-index 0 \\
  --security-secret-file /tmp/f33-boot-secret.bin \\
  --payload-secret-file /tmp/f33-payload-secret.bin \\
  --ram-load-addr 0xFEBF0000 \\
  --ram-geometry-evidence dynamic:camry-8965F3307000-20260826 \\
  --expected-f181-hex {f181} \\
  --expected-boot-f181-hex {boot_f181}"""
    return f"""# F33 Gate-2 semantic stage-2 field sequence

This package is for the exact `8965F3307000` EPS only. Stage 1 is already
installed (`0x8F952 = E0 01`, CRC fixup `D9AF33AF`). Stage 2 changes only
`0x8F948: 1A 38 -> 00 3A`, making the pre-branch callback observe result zero,
while preserving stage 1. The final cumulative CRC fixup is `D12ADB05` and the
expected final CodeFlash SHA-256 is `{stage2.EXPECTED_FINAL_SHA256}`.

The source image in this package is the exact reconstructed stage-1 image, not
stock firmware. Therefore every preflight/APPLY CRC is computed over **both**
persistent patch sites.

## Environment

Run from the kit root after openpilot/Panda ownership is stopped:

```bash
export PY=/usr/local/venv/bin/python
export PYTHONPATH=/data/openpilot:$PWD/runtime
pgrep -af 'pandad|boardd' || true
```

Derive the two already-recovered EPS bootstrap inputs from the exact packaged
CodeFlash source. They are temporary and must not be committed or copied out:

```bash
$PY - <<'PY'
from pathlib import Path
p = Path('firmware_patch/CodeFlash.gate2-final-only.bin')
b = p.read_bytes()
Path('/tmp/f33-payload-secret.bin').write_bytes(b[0xBFD8:0xBFE8])
Path('/tmp/f33-boot-secret.bin').write_bytes(b[0xBFE8:0xBFF8])
PY
chmod 600 /tmp/f33-payload-secret.bin /tmp/f33-boot-secret.bin
```

## 1. Zero-write preflight

Car **READY, Park, stationary**. This executes authenticated RAM only and must
report `apply_ready: true`, with live stage-2 preimage `1A38`, source fixup
`D9AF33AF`, source CRC prefix `2650CC50`, and residue `FFFFFFFF`.

```bash
$PY runtime/exploit/patcher/deploy.py \\
  firmware_patch/CodeFlash.gate2-final-only.bin \\
  --manifest firmware_patch/secoc_patch_manifest_f33_callback_success.json \\
  --template firmware_patch/generic_shellcode_template.bin \\
  --run-dir /tmp/f33-stage2-preflight --validate-only --execute \\
  {common}
```

If `apply_ready` is not exactly true, **do not APPLY**.

## 2. APPLY

Only after the immediately preceding preflight is APPLY-ready:

```bash
$PY runtime/exploit/patcher/deploy.py \\
  firmware_patch/CodeFlash.gate2-final-only.bin \\
  --manifest firmware_patch/secoc_patch_manifest_f33_callback_success.json \\
  --template firmware_patch/generic_shellcode_template.bin \\
  --run-dir /tmp/f33-stage2-apply --apply --execute \\
  --restore-artifact firmware_patch/restore/restore.json \\
  --preflight-record /tmp/f33-stage2-preflight/preflight.json \\
  {common}
```

Required completed-write telemetry: target readback `003A`, computed/stored
fixup `D12ADB05`, and final residue `FFFFFFFF`. Then power the vehicle fully
OFF before the post-apply persistence check.

## 3. OFF -> READY, then zero-write persistence verification

After a full power cycle back to READY/Park/stationary:

```bash
$PY runtime/exploit/patcher/post_apply_verify.py \\
  firmware_patch/CodeFlash.gate2-final-only.bin \\
  --manifest firmware_patch/secoc_patch_manifest_f33_callback_success.json \\
  --template firmware_patch/generic_shellcode_template.bin \\
  --apply-run /tmp/f33-stage2-apply/run.json \\
  --run-dir /tmp/f33-stage2-post --execute \\
  {common}
```

`verified` must be true. This proves only persistent bytes/CRC. Then rerun the
B6 admission-only probe from the main `RUNBOOK.md`; do not request the 0.5-degree
offset unless ID11 is `ADMITTED`.

## Recovery

The packaged RESTORE reverses **stage 2 only** (`003A -> 1A38`) and returns to
the already-installed CRC-valid stage-1 image. It intentionally preserves
`0x8F952 = E001`.

```bash
$PY runtime/exploit/patcher/restore.py \\
  firmware_patch/CodeFlash.gate2-final-only.bin \\
  --manifest firmware_patch/secoc_patch_manifest_f33_callback_success.json \\
  --template firmware_patch/generic_shellcode_template.bin \\
  --restore-artifact firmware_patch/restore/restore.json \\
  --run-dir /tmp/f33-stage2-restore --execute \\
  {common}
```

After any completed APPLY or RESTORE, power-cycle before interpreting normal
application behavior. Remove transient input files when finished:

```bash
rm -f /tmp/f33-boot-secret.bin /tmp/f33-payload-secret.bin
```
"""


def build(out: Path, openpilot: Path) -> dict:
    out.mkdir(parents=True, exist_ok=True)
    dst = out / PROBE.name
    shutil.copy2(PROBE, dst)

    patch_dir = out / "firmware_patch"
    patch_package = stage2.build(patch_dir, build_payloads=True)
    runtime_files = copy_runtime(out)
    (out / "FIRMWARE_PATCH.md").write_text(patch_runbook(), encoding="utf-8")

    files = {
        dst.name: {"sha256": sha256(dst)},
        "FIRMWARE_PATCH.md": {"sha256": sha256(out / "FIRMWARE_PATCH.md")},
    }
    files.update(runtime_files)
    for path in sorted(p for p in patch_dir.rglob("*") if p.is_file()):
        files[str(path.relative_to(out))] = {"sha256": sha256(path)}

    manifest = {
        "schema": "camry-f33-car-kit-v2",
        "created_at": datetime.now(UTC).isoformat(timespec="seconds"),
        "target": {
            "eps_f181": "8965F3307000",
            "eps_diag": "0x7A1->0x7A9 bus0",
            "b6": "0x0B6/32 FD bus0",
        },
        "firmware_patch": {
            "stage1_installed": {"address": "0x8F952", "bytes": "e001", "fixup": "0xD9AF33AF"},
            "stage2_candidate": {"address": "0x8F948", "bytes": "003a", "final_fixup": "0xD12ADB05"},
            "source_image_sha256": stage2.EXPECTED_STAGE1_SHA256,
            "final_image_sha256": stage2.EXPECTED_FINAL_SHA256,
            "package": patch_package,
        },
        "files": files,
        "repositories": {
            "analysis": git_state(ROOT),
            "openpilot": git_state(openpilot),
            "opendbc": git_state(openpilot / "opendbc_repo"),
            "panda": git_state(openpilot / "panda"),
        },
    }
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    runbook = """# 2026 Camry F33 in-car lateral bring-up

Target: `8965F3307000`; **current post-repin** EPS diagnostics `0x7A1 -> 0x7A9` on Panda bus 0; B6 `0x0B6/32` CAN-FD on bus 0.

## Current order of operations

The 2026-09-01 admission run with the installed final-branch-only Gate-2 patch transmitted 85/85 active B6 frames but left the application snapshot at ID0/current angle and bank 7. Do not repeat the steering-offset test on that firmware state.

First follow `FIRMWARE_PATCH.md`: zero-write stage-2 preflight, APPLY only if preflight is exact, full OFF->READY, then zero-write persistence verification. Only after stage 2 is persistence-verified should the admission probe below be repeated.

## Before touching the Panda

Park the car, keep it stationary, and keep hands clear of the wheel. Stop openpilot so no `pandad`/`boardd` process owns the Panda. The probe refuses to run if either process remains. Do not run the direct-Panda probe while driving.

Use the openpilot virtual environment:

```bash
export PY=/usr/local/venv/bin/python
export PYTHONPATH=/data/openpilot:$PWD/runtime
$PY - <<'PY'
from panda import Panda
from opendbc.car import structs
print('Panda/opendbc imports OK; allOutput=', structs.CarParams.SafetyModel.allOutput)
PY
pgrep -af 'pandad|boardd' || true
```

## Offline/self-check on comma

```bash
$PY camry_f33_b6_stationary_probe.py
$PY camry_f33_b6_stationary_probe.py --simulate
```

The simulation must report `good_verdict.reason = ADMITTED`.

## First B6 run after stage-2 persistence proof: admission only

```bash
$PY camry_f33_b6_stationary_probe.py --execute --stationary-confirmed \\
  --output /tmp/camry-f33-b6-stage2-admission.ndjson | tee /tmp/camry-f33-b6-stage2-admission.txt
```

Do **not** request a steering offset on the first run. Positive proof is `id11.verdict.reason = ADMITTED`, with `ADB0=11`, the commanded `AE90`, `ADB9=0`, `CAFF=1`, `ACBD=0`, and `CB00=2`. If it is not ADMITTED, stop there and preserve both output files.

## Second B6 run: tiny stationary causal test

Run this only after the admission-only run is ADMITTED:

```bash
$PY camry_f33_b6_stationary_probe.py --execute --stationary-confirmed --small-offset-deg 0.5 \\
  --output /tmp/camry-f33-b6-stage2-offset.ndjson | tee /tmp/camry-f33-b6-stage2-offset.txt
```

The tool hard-caps the offset at +/-2 degrees, refreshes the measured wheel angle immediately before the phase, rate-limits the command to no more than 6 deg/s, and refuses the offset phase unless the immediately preceding ID11 current-angle phase is admitted.

## Normal openpilot after stationary proof

Use the openpilot/opendbc revisions recorded in `manifest.json`. Camry lateral is native `CC.latActive` angle control over B6; Toyota stock DRCC remains longitudinal; `0x08A` is never transmitted by openpilot. Restart openpilot normally only after direct-Panda tooling exits.
"""
    (out / "RUNBOOK.md").write_text(runbook, encoding="utf-8")
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=ROOT / "build/out/camry-f33-car-kit")
    parser.add_argument("--openpilot", type=Path, default=DEFAULT_OPENPILOT)
    args = parser.parse_args()
    manifest = build(args.out, args.openpilot)
    print(json.dumps(manifest, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
