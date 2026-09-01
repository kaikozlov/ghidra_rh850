#!/usr/bin/env python3
"""Build the small file bundle needed for the exact-F33 in-car lateral bring-up."""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROBE = ROOT / "exploit/behavioral_proof/camry_f33_b6_stationary_probe.py"
DEFAULT_OPENPILOT = Path("/Users/kai/dev/inspect/repos/kai-openpilot")


def git_state(repo: Path) -> dict:
    if not (repo / ".git").exists():
        return {"path": str(repo), "available": False}
    head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=repo, text=True).strip()
    status = subprocess.check_output(["git", "status", "--porcelain"], cwd=repo, text=True)
    return {"path": str(repo), "available": True, "head": head, "dirty": bool(status.strip())}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build(out: Path, openpilot: Path) -> dict:
    out.mkdir(parents=True, exist_ok=True)
    dst = out / PROBE.name
    shutil.copy2(PROBE, dst)

    manifest = {
        "schema": "camry-f33-car-kit-v1",
        "created_at": datetime.now(UTC).isoformat(timespec="seconds"),
        "target": {
            "eps_f181": "8965F3307000",
            "eps_diag": "0x7A1->0x7A9 bus0",
            "b6": "0x0B6/32 FD bus0",
        },
        "files": {dst.name: {"sha256": sha256(dst)}},
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

## Before touching the Panda

Park the car, keep it stationary, and keep hands clear of the wheel. Stop openpilot so no `pandad`/`boardd` process owns the Panda. The probe refuses to run if either process remains. Do not run the direct-Panda probe while driving.

Confirm the comma environment can import Panda/opendbc and that the Panda is free:

```bash
python3 - <<'PY'
from panda import Panda
from opendbc.car import structs
print('Panda/opendbc imports OK; allOutput=', structs.CarParams.SafetyModel.allOutput)
PY
pgrep -af 'pandad|boardd' || true
```

## Offline/self-check on comma

```bash
python3 camry_f33_b6_stationary_probe.py
python3 camry_f33_b6_stationary_probe.py --simulate
```

The simulation must report `good_verdict.reason = ADMITTED`.

## First live run: admission only

```bash
python3 camry_f33_b6_stationary_probe.py --execute --stationary-confirmed \\
  --output /tmp/camry-f33-b6-admission.ndjson | tee /tmp/camry-f33-b6-admission.json
```

Do **not** request a steering offset on the first run. Positive proof is `id11.verdict.reason = ADMITTED`, with `ADB0=11`, the commanded `AE90`, `ADB9=0`, `CAFF=1`, `ACBD=0`, and `CB00=2`. If it is not ADMITTED, stop there and preserve both output files.

## Second live run: tiny stationary causal test

Run this only after the admission-only run is ADMITTED:

```bash
python3 camry_f33_b6_stationary_probe.py --execute --stationary-confirmed --small-offset-deg 0.5 \\
  --output /tmp/camry-f33-b6-offset.ndjson | tee /tmp/camry-f33-b6-offset.json
```

The tool hard-caps the offset at +/-2 degrees, refreshes the measured wheel angle immediately before the phase, rate-limits the command to no more than 6 deg/s, and refuses the offset phase unless the immediately preceding ID11 current-angle phase is admitted.

## Normal openpilot after stationary proof

Use the openpilot/opendbc revisions recorded in `manifest.json`. Camry lateral is native `CC.latActive` angle control over B6; Toyota stock DRCC remains longitudinal; `0x08A` is never transmitted by openpilot. Restart openpilot normally only after the direct-Panda probe exits.
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
