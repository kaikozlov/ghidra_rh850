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

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))
from exploit.common.payload_package import package_shellcode
from exploit.common.ram_exec import (
    TOYOTA_P1ME_BOOT_SECURITY_ACCESS_SECRET,
    TOYOTA_P1ME_PAYLOAD_BUILD_SECRET,
)
from exploit.ephemeral_runtime import camry_f33_08a_oracle_stream as eps08a_oracle
from exploit.ephemeral_runtime import camry_f33_08a_fd_oracle as eps08a_fd_oracle
from exploit.ephemeral_runtime import camry_f33_fd_ingress_probe as fd_ingress_probe
from exploit.ephemeral_runtime import camry_f33_08a_tx_probe as eps08a_probe
from exploit.ephemeral_runtime import camry_f33_b6_bridge_install as bridge_install
from exploit.ephemeral_runtime import (
    camry_f33_b6_midaggregate_observer as midaggregate_observer,
)
from exploit.ephemeral_runtime import (
    camry_f33_b6_transaction_observer_install as observer_install,
)
from exploit.ephemeral_runtime import camry_f33_command5_probe as command5_probe
from exploit.ephemeral_runtime import camry_f33_runtime_monitor as runtime_monitor
from exploit.ephemeral_runtime import (
    camry_f33_runtime_monitor_intertick as intertick_monitor,
)
from exploit.ephemeral_runtime import (
    camry_f33_runtime_monitor_preaggregate as preaggregate_monitor,
)
from exploit.ephemeral_runtime import (
    camry_f33_runtime_replay_discriminator as replay_discriminator,
)
from tools.targets.camry.builders import build_camry_f33_crypto_result_patch as stage5
from tools.targets.camry.builders import (
    build_camry_f33_gate2_root_result_patch as stage3,
)
from tools.targets.camry.builders import (
    build_camry_f33_persistent_signer_patch as persistent_patch,
)

PROBE = ROOT / "exploit/behavioral_proof/camry_f33_b6_stationary_probe.py"
RUNBOOK_TEMPLATE = ROOT / "exploit/ephemeral_runtime/camry_f33_runtime_monitor_runbook.md"
PERSISTENT_RUNBOOK = ROOT / "exploit/ephemeral_runtime/camry_f33_persistent_signer_runbook.md"
EPS08A_RUNBOOK = ROOT / "exploit/ephemeral_runtime/camry_f33_08a_sender_experiments.md"
FIELD_LAUNCHER = ROOT / "exploit/ephemeral_runtime/camry_f33_field_launcher.sh"
PREAGG_FIELD_LAUNCHER = ROOT / "exploit/ephemeral_runtime/camry_f33_field_preaggregate_launcher.sh"
MIDAGG_FIELD_LAUNCHER = ROOT / "exploit/ephemeral_runtime/camry_f33_field_midaggregate_launcher.sh"
COMMAND5_LAUNCHER = ROOT / "exploit/ephemeral_runtime/camry_f33_command5_launcher.sh"
EPS08A_TX_LAUNCHER = ROOT / "exploit/ephemeral_runtime/camry_f33_08a_tx_probe_launcher.sh"
EPS08A_ORACLE_LAUNCHER = ROOT / "exploit/ephemeral_runtime/camry_f33_08a_oracle_stream_launcher.sh"
EPS08A_FD_ORACLE_LAUNCHER = ROOT / "exploit/ephemeral_runtime/camry_f33_08a_fd_oracle_launcher.sh"
FD_INGRESS_LAUNCHER = ROOT / "exploit/ephemeral_runtime/camry_f33_fd_ingress_probe_launcher.sh"
INLINE_SIGNER_LAUNCHER = ROOT / "exploit/ephemeral_runtime/camry_f33_b6_inline_signer_launcher.sh"
ICUS_RAMKEY_LAUNCHER = ROOT / "exploit/ephemeral_runtime/camry_f33_icus_ramkey_probe_launcher.sh"
PERSISTENT_SIGNER_LAUNCHER = ROOT / "exploit/ephemeral_runtime/camry_f33_persistent_signer_launcher.sh"
F33_IMAGE = ROOT / "firmware/camry-8965F3307000/CodeFlash.bin"
OBSERVER_BIN = ROOT / "exploit/ephemeral_runtime/audited/camry_f33_b6_transaction_observer.bin"
BRIDGE_BIN = ROOT / "exploit/ephemeral_runtime/audited/camry_f33_b6_bridge.bin"
REPLAY_BIN = ROOT / "exploit/ephemeral_runtime/audited/camry_f33_runtime_replay_discriminator.bin"
MONITOR_BIN = ROOT / "exploit/ephemeral_runtime/audited/camry_f33_runtime_monitor.bin"
PREAGG_MONITOR_BIN = ROOT / "exploit/ephemeral_runtime/audited/camry_f33_runtime_monitor_preaggregate.bin"
INTERTICK_MONITOR_BIN = ROOT / "exploit/ephemeral_runtime/audited/camry_f33_runtime_monitor_intertick.bin"
MIDAGG_OBSERVER_BIN = ROOT / "exploit/ephemeral_runtime/audited/camry_f33_b6_midaggregate_observer.bin"
COMMAND5_PROBE_BIN = ROOT / "exploit/ephemeral_runtime/audited/camry_f33_command5_probe.bin"
EPS08A_TX_PROBE_BIN = ROOT / "exploit/ephemeral_runtime/audited/camry_f33_08a_tx_probe.bin"
EPS08A_TX_PROBE_META = ROOT / "exploit/ephemeral_runtime/audited_camry_f33_08a_tx_probe_build.json"
EPS08A_ORACLE_BIN = ROOT / "exploit/ephemeral_runtime/audited/camry_f33_08a_oracle_stream.bin"
EPS08A_ORACLE_META = ROOT / "exploit/ephemeral_runtime/audited_camry_f33_08a_oracle_stream_build.json"
EPS08A_FD_ORACLE_BIN = ROOT / "exploit/ephemeral_runtime/audited/camry_f33_08a_fd_oracle.bin"
EPS08A_FD_ORACLE_META = ROOT / "exploit/ephemeral_runtime/audited_camry_f33_08a_fd_oracle_build.json"
FD_INGRESS_BIN = ROOT / "exploit/ephemeral_runtime/audited/camry_f33_fd_ingress_probe.bin"
FD_INGRESS_META = ROOT / "exploit/ephemeral_runtime/audited_camry_f33_fd_ingress_probe_build.json"
# Supervised continuous substitution preserves the road helper's steady-state
# behavior, but stops after seven foreground ticks without a changed host
# generation. Its new identity has instruction-level, not vehicle, validation.
INLINE_SIGNER_BIN = ROOT / "exploit/ephemeral_runtime/audited/camry_f33_b6_inline_signer_supervised.bin"
INLINE_SIGNER_HELPER = ROOT / "exploit/ephemeral_runtime/audited/camry_f33_b6_inline_signer_supervised_helper_padded.bin"
INLINE_SIGNER_META = ROOT / "exploit/ephemeral_runtime/audited_camry_f33_b6_inline_signer_supervised_build.json"
ICUS_RAMKEY_HELPER9 = ROOT / "exploit/ephemeral_runtime/audited/camry_f33_icus_ramkey_cmd9_helper_padded.bin"
ICUS_RAMKEY_HELPER10 = ROOT / "exploit/ephemeral_runtime/audited/camry_f33_icus_ramkey_cmd10_helper_padded.bin"
ICUS_RAMKEY_META = ROOT / "exploit/ephemeral_runtime/audited/camry_f33_icus_ramkey_probe.json"
INGRESS_HELPER = ROOT / "exploit/ephemeral_runtime/audited/camry_f33_b6_ingress_helper_helper_padded.bin"
INGRESS_META = ROOT / "exploit/ephemeral_runtime/audited_camry_f33_b6_ingress_helper_build.json"
DEFAULT_OPENPILOT = Path("/Users/kai/dev/inspect/repos/kai-openpilot")
RUNTIME_FILES = [
    "tsk/__init__.py",
    "tsk/lib/__init__.py",
    "tsk/lib/programming.py",
    "tsk/lib/diagnostic_route.py",
    "exploit/common/payload_package.py",
    "exploit/common/ram_exec.py",
    "exploit/ephemeral_runtime/camry_f33_b6_transaction_observer.py",
    "exploit/ephemeral_runtime/camry_f33_b6_transaction_observer_install.py",
    "exploit/ephemeral_runtime/camry_f33_b6_bridge_install.py",
    "exploit/ephemeral_runtime/camry_f33_runtime_replay_discriminator.py",
    "exploit/ephemeral_runtime/camry_f33_runtime_monitor.py",
    "exploit/ephemeral_runtime/camry_f33_runtime_monitor_preaggregate.py",
    "exploit/ephemeral_runtime/camry_f33_runtime_monitor_intertick.py",
    "exploit/ephemeral_runtime/camry_f33_b6_midaggregate_observer.py",
    "exploit/ephemeral_runtime/camry_f33_b6_ingress_helper.py",
    "exploit/ephemeral_runtime/camry_f33_command5_probe.py",
    "exploit/ephemeral_runtime/camry_f33_08a_tx_probe.py",
    "exploit/ephemeral_runtime/camry_f33_08a_oracle_stream.py",
    "exploit/ephemeral_runtime/camry_f33_08a_fd_oracle.py",
    "exploit/ephemeral_runtime/camry_f33_fd_ingress_probe.py",
    "exploit/ephemeral_runtime/camry_f33_b6_inline_signer.py",
    "exploit/ephemeral_runtime/camry_f33_post_install_recovery.py",
    "exploit/ephemeral_runtime/camry_f33_icus_ramkey_probe.py",
    "exploit/ephemeral_runtime/camry_f33_persistent_signer.py",
    "exploit/ephemeral_runtime/f33_panda_lease.sh",
    "exploit/followups/xcp_read_probe.py",
    "exploit/followups/xcp_daq_probe.py",
    "exploit/followups/xcp_runtime_state_probe.py",
    "exploit/followups/application_rmba_probe.py",
    "exploit/patcher/patch_config.py",
    "exploit/patcher/build_payload.py",
    "exploit/patcher/deploy.py",
    "exploit/patcher/restore.py",
    "exploit/patcher/post_apply_verify.py",
    "tools/__init__.py",
    "tools/security/build_secoc_patch_manifest.py",
    "tools/targets/camry/live/camry_f33_steering_state_capture.py",
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
    f181 = stage3.EXPECTED_F181_HEX
    boot_f181 = stage3.EXPECTED_BOOT_F181_HEX
    common = f"""--bus 0 --elm327-param 1 --uds-variant old --cpu-index 0 \\
  --ram-load-addr 0xFEBF0000 \\
  --ram-geometry-evidence dynamic:camry-8965F3307000-20260826 \\
  --expected-f181-hex {f181} \\
  --expected-boot-f181-hex {boot_f181}"""
    return f"""# F33 Gate-2 root-result stage-3 field sequence (historical record)

This package is for the exact `8965F3307000` EPS only.

**Historical-provenance label.** The sequence below records the historical
stage-2 -> stage-3 progression as it was performed and reboot-verified at the
time. It is **not** a fresh live identity measurement of the currently
installed firmware. The kit manifest's `last_observed_firmware` block is the
historical installed-state record at that checkpoint (stage 5, SHA-256
`{stage5.EXPECTED_FINAL_SHA256}`, persistence-verified 2026-09-01);
verify the live image against that record before any operation. Earlier kit
builds described the stage-2 image as "currently installed"; that wording
referred to the stage-2 image *as it was when this sequence was executed*:

```text
0x8F948 = 00 3A
0x8F952 = E0 01
CRC prefix = 2ED524FA
CRC fixup  = D12ADB05
SHA-256    = {stage3.EXPECTED_STAGE2_SHA256}
```

That image was tested live with 84/84 B6 TX echoes and still returned
`payload_not_delivered`; stage 2 is therefore disproved as sufficient.

Full-function recovery of `FUN_0008F906` identifies the actual root boolean:

```text
8F92A  ld.bu FEBE5564,r1
8F92E  cmp   r0,r1
8F930  cmovne 1,r1,r26    # r26 = (FEBE5564 != 0)
...
8F94C  FUN_8F8D2(id,...)
8F952  cmp r0,r26         # stock final success/failure branch
...
8F958  FUN_8F4D0(id,0)    # native success bookkeeping
8F960  FUN_8F546(id,0)    # native PduR/COM delivery
8F96A  FUN_8F60E(id,0x200)# native failure arm
```

Stage 3 changes only **`0x8F930: E1 0F 14 D3 -> E0 07 14 D3`**, the exact
same-width RH850 `cmovne 0,r0,r26` encoding. This forces the one root result
boolean to zero so the entire remaining function follows its native
verified-success values and branch. The existing stage-1/stage-2 tail edits are
semantically redundant when `r26=0`; they are intentionally left untouched for
this one-new-site discriminator.

Expected cumulative stage-3 state:

```text
0x8F930 = E0 07 14 D3
0x8F948 = 00 3A
0x8F952 = E0 01
CRC prefix = 13ADA3CC
CRC fixup  = EC525C33
CRC residue = FFFFFFFF
SHA-256 = {stage3.EXPECTED_FINAL_SHA256}
```

## Important vehicle-state requirement

The exact F33 rejected DiagnosticSessionControl programming (`0x10 02`) with
NRC `0x22` in READY during the 2026-09-01 field run. The same operation succeeds
in **NRTD / ignition-on, Park, stationary**. Therefore preflight, APPLY, RESTORE,
and post-reboot persistence verification are NRTD-only operations. B6 behavior
is tested later in READY.

## Environment

Run from the kit root after openpilot/Panda ownership is stopped:

```bash
export PY=/usr/local/venv/bin/python
export PYTHONPATH=/data/openpilot:$PWD/runtime
pgrep -af 'pandad|boardd' || true
```

The Toyota P1M-E payload-build and boot SecurityAccess roots are built into the
runtime. They are byte-identical in the tracked Sienna and exact-F33 CodeFlash
images and public in LoChuan's RH850_P1M-E image. No temporary secret files or
environment variables are required.

## 1. NRTD zero-write preflight

Vehicle **NRTD, Park, stationary**. This executes authenticated RAM only and
must report `apply_ready: true`, with exact F181, live root preimage
`E10F14D3`, source fixup `D12ADB05`, source CRC prefix `2ED524FA`, and residue
`FFFFFFFF`.

```bash
$PY runtime/exploit/patcher/deploy.py \\
  firmware_patch/CodeFlash.gate2-stage2.bin \\
  --manifest firmware_patch/secoc_patch_manifest_f33_root_result.json \\
  --template firmware_patch/generic_shellcode_template.bin \\
  --run-dir /tmp/f33-stage3-preflight --validate-only --execute \\
  {common}
```

If `apply_ready` is not exactly true, **do not APPLY**.

## 2. NRTD APPLY

Only after the immediately preceding preflight is APPLY-ready. If the EPS does
not reappear after the preflight programming cycle, power fully OFF then return
to NRTD before retrying APPLY; never bypass the preflight binding.

```bash
$PY runtime/exploit/patcher/deploy.py \\
  firmware_patch/CodeFlash.gate2-stage2.bin \\
  --manifest firmware_patch/secoc_patch_manifest_f33_root_result.json \\
  --template firmware_patch/generic_shellcode_template.bin \\
  --run-dir /tmp/f33-stage3-apply --apply --execute \\
  --restore-artifact firmware_patch/restore/restore.json \\
  --preflight-record /tmp/f33-stage3-preflight/preflight.json \\
  {common}
```

Required completed-write telemetry: target readback `E00714D3`, computed/stored
fixup `EC525C33`, CRC prefix `13ADA3CC`, and final residue `FFFFFFFF`.

## 3. Full OFF -> NRTD, then zero-write persistence verification

Power the vehicle fully OFF. Return to **NRTD/Park/stationary**, not READY, then:

```bash
$PY runtime/exploit/patcher/post_apply_verify.py \\
  firmware_patch/CodeFlash.gate2-stage2.bin \\
  --manifest firmware_patch/secoc_patch_manifest_f33_root_result.json \\
  --template firmware_patch/generic_shellcode_template.bin \\
  --apply-run /tmp/f33-stage3-apply/run.json \\
  --run-dir /tmp/f33-stage3-post --execute \\
  {common}
```

`verified` must be true. This proves only persistent bytes/CRC.

## 4. Full OFF -> READY, then admission-only B6

Power fully OFF, then return to READY/Park/stationary. Follow the main
`RUNBOOK.md`. The first stage-3 B6 test is ID0/current-angle then
ID11/current-angle with **no steering offset**. Do not request 0.5 degrees unless
ID11 reports `ADMITTED`.

## Recovery

The packaged RESTORE reverses **stage 3 only** (`E00714D3 -> E10F14D3`) and
returns exactly to the reboot-verified stage-2 image, including `8F948=003A`,
`8F952=E001`, and fixup `D12ADB05`.

RESTORE also requires NRTD/Park/stationary:

```bash
$PY runtime/exploit/patcher/restore.py \\
  firmware_patch/CodeFlash.gate2-stage2.bin \\
  --manifest firmware_patch/secoc_patch_manifest_f33_root_result.json \\
  --template firmware_patch/generic_shellcode_template.bin \\
  --restore-artifact firmware_patch/restore/restore.json \\
  --run-dir /tmp/f33-stage3-restore --execute \\
  {common}
```

After any completed APPLY or RESTORE, power-cycle before interpreting normal
application behavior.
"""


def build(out: Path, openpilot: Path) -> dict:
    out.mkdir(parents=True, exist_ok=True)
    dst = out / PROBE.name
    shutil.copy2(PROBE, dst)

    patch_dir = out / "firmware_patch"
    patch_package = stage3.build(patch_dir, build_payloads=True)
    persistent_dir = out / "persistent_patch"
    persistent_package = persistent_patch.build(persistent_dir)
    runtime_files = copy_runtime(out)
    (out / "FIRMWARE_PATCH.md").write_text(patch_runbook(), encoding="utf-8")

    ram_dir = out / "ram_payloads"
    ram_dir.mkdir(parents=True, exist_ok=True)
    f33_image = F33_IMAGE.read_bytes()
    if f33_image[0xBFD8:0xBFE8] != TOYOTA_P1ME_PAYLOAD_BUILD_SECRET:
        raise RuntimeError("F33 payload-build root differs from built-in Toyota P1M-E root")
    if f33_image[0xBFE8:0xBFF8] != TOYOTA_P1ME_BOOT_SECURITY_ACCESS_SECRET:
        raise RuntimeError("F33 boot SecurityAccess root differs from built-in Toyota P1M-E root")
    observer_payload = package_shellcode(OBSERVER_BIN.read_bytes(), secret=TOYOTA_P1ME_PAYLOAD_BUILD_SECRET)
    bridge_payload = package_shellcode(BRIDGE_BIN.read_bytes(), secret=TOYOTA_P1ME_PAYLOAD_BUILD_SECRET)
    replay_payload = package_shellcode(REPLAY_BIN.read_bytes(), secret=TOYOTA_P1ME_PAYLOAD_BUILD_SECRET)
    monitor_payload = package_shellcode(MONITOR_BIN.read_bytes(), secret=TOYOTA_P1ME_PAYLOAD_BUILD_SECRET)
    preaggregate_monitor_payload = package_shellcode(PREAGG_MONITOR_BIN.read_bytes(), secret=TOYOTA_P1ME_PAYLOAD_BUILD_SECRET)
    intertick_monitor_payload = package_shellcode(INTERTICK_MONITOR_BIN.read_bytes(), secret=TOYOTA_P1ME_PAYLOAD_BUILD_SECRET)
    midaggregate_observer_payload = package_shellcode(MIDAGG_OBSERVER_BIN.read_bytes(), secret=TOYOTA_P1ME_PAYLOAD_BUILD_SECRET)
    command5_probe_payload = package_shellcode(COMMAND5_PROBE_BIN.read_bytes(), secret=TOYOTA_P1ME_PAYLOAD_BUILD_SECRET)
    eps08a_tx_meta = json.loads(EPS08A_TX_PROBE_META.read_text(encoding="utf-8"))
    eps08a_tx_stage = EPS08A_TX_PROBE_BIN.read_bytes()
    if hashlib.sha256(eps08a_tx_stage).hexdigest() != eps08a_tx_meta["staging"]["sha256"]:
        raise RuntimeError("0x08A Tx probe audited staging identity drift")
    eps08a_tx_payload = package_shellcode(eps08a_tx_stage, secret=TOYOTA_P1ME_PAYLOAD_BUILD_SECRET)
    eps08a_oracle_meta = json.loads(EPS08A_ORACLE_META.read_text(encoding="utf-8"))
    eps08a_oracle_stage = EPS08A_ORACLE_BIN.read_bytes()
    if hashlib.sha256(eps08a_oracle_stage).hexdigest() != eps08a_oracle_meta["staging"]["sha256"]:
        raise RuntimeError("0x08A oracle audited staging identity drift")
    eps08a_oracle_payload = package_shellcode(eps08a_oracle_stage, secret=TOYOTA_P1ME_PAYLOAD_BUILD_SECRET)
    if hashlib.sha256(eps08a_oracle_payload).hexdigest() != eps08a_oracle_meta["authenticated_payload"]["sha256"]:
        raise RuntimeError("0x08A oracle authenticated payload identity drift")
    eps08a_fd_oracle_meta = json.loads(EPS08A_FD_ORACLE_META.read_text(encoding="utf-8"))
    eps08a_fd_oracle_stage = EPS08A_FD_ORACLE_BIN.read_bytes()
    if hashlib.sha256(eps08a_fd_oracle_stage).hexdigest() != eps08a_fd_oracle_meta["staging"]["sha256"]:
        raise RuntimeError("0x08A raw-FD oracle audited staging identity drift")
    eps08a_fd_oracle_payload = package_shellcode(eps08a_fd_oracle_stage, secret=TOYOTA_P1ME_PAYLOAD_BUILD_SECRET)
    if hashlib.sha256(eps08a_fd_oracle_payload).hexdigest() != eps08a_fd_oracle_meta["authenticated_payload"]["sha256"]:
        raise RuntimeError("0x08A raw-FD oracle authenticated payload identity drift")
    fd_ingress_meta = json.loads(FD_INGRESS_META.read_text(encoding="utf-8"))
    fd_ingress_stage = FD_INGRESS_BIN.read_bytes()
    if hashlib.sha256(fd_ingress_stage).hexdigest() != fd_ingress_meta["staging"]["sha256"]:
        raise RuntimeError("FD ingress probe audited staging identity drift")
    fd_ingress_payload = package_shellcode(fd_ingress_stage, secret=TOYOTA_P1ME_PAYLOAD_BUILD_SECRET)
    if hashlib.sha256(fd_ingress_payload).hexdigest() != fd_ingress_meta["authenticated_payload"]["sha256"]:
        raise RuntimeError("FD ingress probe authenticated payload identity drift")
    inline_meta = json.loads(INLINE_SIGNER_META.read_text(encoding="utf-8"))
    inline_staging = INLINE_SIGNER_BIN.read_bytes()
    inline_helper = INLINE_SIGNER_HELPER.read_bytes()
    if hashlib.sha256(inline_staging).hexdigest() != inline_meta["staging"]["sha256"]:
        raise RuntimeError("inline signer audited staging identity drift")
    if hashlib.sha256(inline_helper).hexdigest() != inline_meta["helper"]["padded_sha256"]:
        raise RuntimeError("inline signer audited helper identity drift")
    inline_signer_payload = package_shellcode(inline_staging, secret=TOYOTA_P1ME_PAYLOAD_BUILD_SECRET)
    icus_ramkey_meta = json.loads(ICUS_RAMKEY_META.read_text(encoding="utf-8"))
    icus_ramkey_helper9 = ICUS_RAMKEY_HELPER9.read_bytes()
    icus_ramkey_helper10 = ICUS_RAMKEY_HELPER10.read_bytes()
    if icus_ramkey_meta.get("schema") != "camry-f33-icus-ramkey-probe-build-v1":
        raise RuntimeError("ICU-S RAM_KEY audited metadata schema drift")
    for name, helper in (("command9", icus_ramkey_helper9), ("command10", icus_ramkey_helper10)):
        if hashlib.sha256(helper).hexdigest() != icus_ramkey_meta["helpers"][name]["sha256"]:
            raise RuntimeError(f"ICU-S RAM_KEY {name} audited helper identity drift")
    reused_resident = icus_ramkey_meta["reused_live_qualified_payload"]["resident"]
    # Continuous and one-shot signer bundles intentionally reuse the exact same
    # r6-correct staging/resident while carrying different post-startup helpers.
    # Artifact filenames differ, so bind the executable identity, not the path.
    for key in ("base", "size", "sha256"):
        if reused_resident[key] != inline_meta["resident"][key]:
            raise RuntimeError(f"ICU-S RAM_KEY probe no longer reuses the r6-correct resident ({key})")
    if icus_ramkey_meta["reused_live_qualified_payload"]["authenticated_payload_sha256"] != hashlib.sha256(inline_signer_payload).hexdigest():
        raise RuntimeError("ICU-S RAM_KEY authenticated payload identity drift")
    ingress_meta = json.loads(INGRESS_META.read_text(encoding="utf-8"))
    ingress_padded_helper = INGRESS_HELPER.read_bytes()
    if ingress_meta.get("mode") != "ingress-observer":
        raise RuntimeError("ingress observer audited metadata mode drift")
    if hashlib.sha256(inline_staging).hexdigest() != ingress_meta["staging"]["sha256"]:
        raise RuntimeError("ingress observer audited staging identity drift")
    if hashlib.sha256(ingress_padded_helper).hexdigest() != ingress_meta["helper"]["padded_sha256"]:
        raise RuntimeError("ingress observer audited helper identity drift")
    ingress_payload = package_shellcode(inline_staging, secret=TOYOTA_P1ME_PAYLOAD_BUILD_SECRET)
    if hashlib.sha256(ingress_payload).hexdigest() != ingress_meta["authenticated_payload"]["sha256"]:
        raise RuntimeError("ingress observer authenticated payload identity drift")
    if hashlib.sha256(observer_payload).hexdigest() != observer_install.EXPECTED_PAYLOAD_SHA256:
        raise RuntimeError("observer authenticated payload identity drift")
    if hashlib.sha256(bridge_payload).hexdigest() != bridge_install.EXPECTED_PAYLOAD_SHA256:
        raise RuntimeError("bridge authenticated payload identity drift")
    if hashlib.sha256(replay_payload).hexdigest() != replay_discriminator.EXPECTED_PAYLOAD_SHA256:
        raise RuntimeError("runtime replay discriminator authenticated payload identity drift")
    if hashlib.sha256(monitor_payload).hexdigest() != runtime_monitor.EXPECTED_PAYLOAD_SHA256:
        raise RuntimeError("runtime monitor authenticated payload identity drift")
    if hashlib.sha256(preaggregate_monitor_payload).hexdigest() != preaggregate_monitor.EXPECTED_PAYLOAD_SHA256:
        raise RuntimeError("pre-aggregate runtime monitor authenticated payload identity drift")
    if hashlib.sha256(intertick_monitor_payload).hexdigest() != intertick_monitor.EXPECTED_PAYLOAD_SHA256:
        raise RuntimeError("inter-tick runtime monitor authenticated payload identity drift")
    if hashlib.sha256(midaggregate_observer_payload).hexdigest() != midaggregate_observer.EXPECTED_PAYLOAD_SHA256:
        raise RuntimeError("mid-aggregate observer authenticated payload identity drift")
    if hashlib.sha256(command5_probe_payload).hexdigest() != command5_probe.EXPECTED_PAYLOAD_SHA256:
        raise RuntimeError("command-5 probe authenticated payload identity drift")
    if hashlib.sha256(eps08a_tx_payload).hexdigest() != eps08a_probe.EXPECTED_PAYLOAD_SHA256:
        raise RuntimeError("0x08A Tx probe authenticated payload identity drift")
    if hashlib.sha256(inline_signer_payload).hexdigest() != inline_meta["authenticated_payload"]["sha256"]:
        raise RuntimeError("inline signer authenticated payload identity drift")
    (ram_dir / "camry_f33_b6_transaction_observer_payload.bin").write_bytes(observer_payload)
    (ram_dir / "camry_f33_b6_bridge_payload.bin").write_bytes(bridge_payload)
    (ram_dir / "camry_f33_runtime_replay_discriminator_payload.bin").write_bytes(replay_payload)
    (ram_dir / "camry_f33_runtime_monitor_payload.bin").write_bytes(monitor_payload)
    (ram_dir / "camry_f33_runtime_monitor_preaggregate_payload.bin").write_bytes(preaggregate_monitor_payload)
    (ram_dir / "camry_f33_runtime_monitor_intertick_payload.bin").write_bytes(intertick_monitor_payload)
    (ram_dir / "camry_f33_b6_midaggregate_observer_payload.bin").write_bytes(midaggregate_observer_payload)
    (ram_dir / "camry_f33_command5_probe_payload.bin").write_bytes(command5_probe_payload)
    (ram_dir / "camry_f33_08a_tx_probe_payload.bin").write_bytes(eps08a_tx_payload)
    (ram_dir / "camry_f33_08a_tx_probe.json").write_text(json.dumps(eps08a_tx_meta, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (ram_dir / "camry_f33_08a_oracle_stream_payload.bin").write_bytes(eps08a_oracle_payload)
    (ram_dir / "camry_f33_08a_oracle_stream.json").write_text(json.dumps(eps08a_oracle_meta, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (ram_dir / "camry_f33_08a_fd_oracle_payload.bin").write_bytes(eps08a_fd_oracle_payload)
    (ram_dir / "camry_f33_08a_fd_oracle.json").write_text(json.dumps(eps08a_fd_oracle_meta, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (ram_dir / "camry_f33_fd_ingress_probe_payload.bin").write_bytes(fd_ingress_payload)
    (ram_dir / "camry_f33_fd_ingress_probe.json").write_text(json.dumps(fd_ingress_meta, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (ram_dir / "camry_f33_b6_inline_signer_payload.bin").write_bytes(inline_signer_payload)
    (ram_dir / "camry_f33_b6_inline_signer_helper_padded.bin").write_bytes(inline_helper)
    (ram_dir / "camry_f33_b6_inline_signer.json").write_text(json.dumps(inline_meta, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (ram_dir / "camry_f33_icus_ramkey_probe_payload.bin").write_bytes(inline_signer_payload)
    (ram_dir / "camry_f33_icus_ramkey_cmd9_helper_padded.bin").write_bytes(icus_ramkey_helper9)
    (ram_dir / "camry_f33_icus_ramkey_cmd10_helper_padded.bin").write_bytes(icus_ramkey_helper10)
    (ram_dir / "camry_f33_icus_ramkey_probe.json").write_text(json.dumps(icus_ramkey_meta, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (ram_dir / "camry_f33_b6_ingress_helper_payload.bin").write_bytes(ingress_payload)
    (ram_dir / "camry_f33_b6_ingress_helper_helper_padded.bin").write_bytes(ingress_padded_helper)
    (ram_dir / "camry_f33_b6_ingress_helper.json").write_text(json.dumps(ingress_meta, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    shutil.copy2(RUNBOOK_TEMPLATE, out / "RUNBOOK.md")
    shutil.copy2(PERSISTENT_RUNBOOK, out / "PERSISTENT_SIGNER.md")
    shutil.copy2(EPS08A_RUNBOOK, out / "08A_SENDER_EXPERIMENTS.md")
    launcher = out / "f33"
    shutil.copy2(FIELD_LAUNCHER, launcher)
    launcher.chmod(0o755)
    preagg_launcher = out / "f33-pre"
    shutil.copy2(PREAGG_FIELD_LAUNCHER, preagg_launcher)
    preagg_launcher.chmod(0o755)
    ingress_launcher = out / "f33-ingress"
    shutil.copy2(MIDAGG_FIELD_LAUNCHER, ingress_launcher)
    ingress_launcher.chmod(0o755)
    command5_launcher = out / "f33-sign"
    shutil.copy2(COMMAND5_LAUNCHER, command5_launcher)
    command5_launcher.chmod(0o755)
    eps08a_tx_launcher = out / "f33-08a-route"
    shutil.copy2(EPS08A_TX_LAUNCHER, eps08a_tx_launcher)
    eps08a_tx_launcher.chmod(0o755)
    eps08a_oracle_launcher = out / "f33-08a-oracle"
    shutil.copy2(EPS08A_ORACLE_LAUNCHER, eps08a_oracle_launcher)
    eps08a_oracle_launcher.chmod(0o755)
    eps08a_fd_oracle_launcher = out / "f33-08a-fd-oracle"
    shutil.copy2(EPS08A_FD_ORACLE_LAUNCHER, eps08a_fd_oracle_launcher)
    eps08a_fd_oracle_launcher.chmod(0o755)
    fd_ingress_launcher = out / "f33-fd-ingress"
    shutil.copy2(FD_INGRESS_LAUNCHER, fd_ingress_launcher)
    fd_ingress_launcher.chmod(0o755)
    inline_signer_launcher = out / "f33-secoc"
    shutil.copy2(INLINE_SIGNER_LAUNCHER, inline_signer_launcher)
    inline_signer_launcher.chmod(0o755)
    icus_ramkey_launcher = out / "f33-icus-ramkey"
    shutil.copy2(ICUS_RAMKEY_LAUNCHER, icus_ramkey_launcher)
    icus_ramkey_launcher.chmod(0o755)
    persistent_signer_launcher = out / "f33-persist"
    shutil.copy2(PERSISTENT_SIGNER_LAUNCHER, persistent_signer_launcher)
    persistent_signer_launcher.chmod(0o755)
    files = {
        dst.name: {"sha256": sha256(dst)},
        "FIRMWARE_PATCH.md": {"sha256": sha256(out / "FIRMWARE_PATCH.md")},
        "RUNBOOK.md": {"sha256": sha256(out / "RUNBOOK.md")},
        "PERSISTENT_SIGNER.md": {"sha256": sha256(out / "PERSISTENT_SIGNER.md")},
        "08A_SENDER_EXPERIMENTS.md": {"sha256": sha256(out / "08A_SENDER_EXPERIMENTS.md")},
        "f33": {"sha256": sha256(launcher)},
        "f33-pre": {"sha256": sha256(preagg_launcher)},
        "f33-ingress": {"sha256": sha256(ingress_launcher)},
        "f33-sign": {"sha256": sha256(command5_launcher)},
        "f33-08a-route": {"sha256": sha256(eps08a_tx_launcher)},
        "f33-08a-oracle": {"sha256": sha256(eps08a_oracle_launcher)},
        "f33-08a-fd-oracle": {"sha256": sha256(eps08a_fd_oracle_launcher)},
        "f33-fd-ingress": {"sha256": sha256(fd_ingress_launcher)},
        "f33-secoc": {"sha256": sha256(inline_signer_launcher)},
        "f33-icus-ramkey": {"sha256": sha256(icus_ramkey_launcher)},
        "f33-persist": {"sha256": sha256(persistent_signer_launcher)},
    }
    files.update(runtime_files)
    for path in sorted(p for p in ram_dir.rglob("*") if p.is_file()):
        files[str(path.relative_to(out))] = {"sha256": sha256(path)}
    for path in sorted(p for p in patch_dir.rglob("*") if p.is_file()):
        files[str(path.relative_to(out))] = {"sha256": sha256(path)}
    for path in sorted(p for p in persistent_dir.rglob("*") if p.is_file()):
        files[str(path.relative_to(out))] = {"sha256": sha256(path)}
    manifest = {
        "schema": "camry-f33-car-kit-v19",
        "created_at": datetime.now(UTC).isoformat(timespec="seconds"),
        "target": {
            "eps_f181": "8965F3307000",
            "eps_diag": "0x7A1->0x7A9 bus0 (post-repin EPS diagnostics and 0x08A MAC-oracle transport)",
            "request_source": "0x08A/32 FD bus2 (FRC native source on relay-correct repin)",
            "request_sink": "0x08A/32 FD bus0 (host replacement toward chassis/Brake)",
        },
        "last_observed_firmware": {
            "stage": 5,
            "sha256": stage5.EXPECTED_FINAL_SHA256,
            "crc_prefix": f"0x{stage5.EXPECTED_STAGE5_PREFIX:08X}",
            "crc_fixup": f"0x{stage5.EXPECTED_STAGE5_FIXUP:08X}",
            "observed_at": "2026-09-01",
            "note": "historical maintainer-rack state only; do not infer the currently installed rack/image from this record",
        },
        "runtime_firmware_contract": {
            "software_id": "8965F3307000",
            "persistent_patch_required": False,
            "stage5_receiver_bypass_required": False,
            "current_lateral_path": "relay-correct FRC 0x08A source replacement; EPS resident is CMAC service only",
            "reason": "the live-qualified volatile oracle runs stock ICU-S command 5 selector 4 over the host-supplied exact 0x008A SecOC domain; it does not bypass the EPS receiver or transmit the request",
            "live_qualified_oracle_on_current_exact_f33": True,
            "request_plane_road_qualified": False,
            "historical_direct_b6_path": "retained as development evidence only; do not arm f33-secoc or f33-persist alongside the 0x08A request-plane path",
        },
        "persistent_b6_signer": {
            "launcher": "f33-persist",
            "historical_only": True,
            "superseded_by": "volatile 0x08A MAC oracle + host selective native-ID11 request replacement",
            "package": "persistent_patch/package.json",
            "stage6_sha256": persistent_package["stage6_resident"]["sha256"],
            "stage7_sha256": persistent_package["stage7_hook"]["sha256"],
            "segments": persistent_package["stage6_resident"]["segments"],
            "hook_address": persistent_package["stage7_hook"]["hook_address"],
            "input": "fresh 0x1FDC0002 C7 sideband; sequence zero/inactive or repeated is ignored",
            "output": "replace B3..B9 in one internally generated native B6 and sign with EPS ICU-S selector 4",
            "stock_08a_modified": False,
            "stock_081_modified": False,
            "longitudinal_0ca_modified": False,
            "normal_boot_programming_session": False,
            "required_preflight": "f33-sign verify-native-08a must match every captured native sample",
            "install_order": persistent_package["ordering"]["install"],
            "remove_order": persistent_package["ordering"]["remove"],
            "diagnostic_route": "0x7A1->0x7A9 on post-repin Panda bus 0, ELM327 param 1",
            "control_route": "extended 0x1FDC0002 C7 sideband on unsplit Panda bus 1",
            "openpilot_requirement": "exact-F33 stock-Toyota-B support with Classical C7 on Panda bus 1",
            "development_only": True,
            "historical_only": True,
        },
        "live_observers": {
            "native_xcp_steering_state": {
                "tool": "runtime/tools/targets/camry/live/camry_f33_steering_state_capture.py",
                "preferred_before_ephemeral_resident": False,
                "profiles": ["full-path", "source-terms", "command-funnel"],
                "default_profile": "full-path",
                "full_path_bytes": 52,
                "full_path_daq_lists": 2,
                "default_daq_prescaler": 10,
                "route": "extended 0x1FDC0002->0x1FE00002 on F33 RSCFD controller1; stock command dispatch disabled",
                "source_memory_write": False,
                "steering_transmit": False,
                "live_status": "stock-native execution disabled: Sep-6 ingress reaches FEBE4C34, but fixed CodeFlash 0x30D68=0x5A blocks CONNECT/DAQ; the generic runtime monitor reuses only the proven staging transport with a non-XCP control frame",
            },
        },
        "ram_experiments": {
            "icus_ramkey_opcode_probe": {
                "launcher": "f33-icus-ramkey",
                "payload": "ram_payloads/camry_f33_icus_ramkey_probe_payload.bin",
                "payload_sha256": icus_ramkey_meta["reused_live_qualified_payload"]["authenticated_payload_sha256"],
                "resident": icus_ramkey_meta["reused_live_qualified_payload"]["resident"],
                "helpers": icus_ramkey_meta["helpers"],
                "known_answer": icus_ramkey_meta["known_answer"],
                "telemetry": icus_ramkey_meta["telemetry"],
                "operation": icus_ramkey_meta["operation"],
                "mutation_boundary": icus_ramkey_meta["mutation_boundary"],
                "field_sequence": [
                    "./f33-icus-ramkey install in NRTD/Park/stationary",
                    "direct NRTD->READY without OFF",
                    "./f33-icus-ramkey run in READY/Park/stationary",
                ],
                "persistent_flash_write": False,
                "persistent_key_update": False,
                "volatile_ram_key_modified_until_reset": True,
                "live_qualified": False,
            },
            "08a_mac_oracle": {
                "launcher": "f33-08a-oracle",
                "payload": "ram_payloads/camry_f33_08a_oracle_stream_payload.bin",
                "payload_sha256": eps08a_oracle_meta["authenticated_payload"]["sha256"],
                "staging_sha256": eps08a_oracle_meta["staging"]["sha256"],
                "resident_base": eps08a_oracle_meta["resident"]["base"],
                "resident_size": eps08a_oracle_meta["resident"]["size"],
                "resident_sha256": eps08a_oracle_meta["resident"]["sha256"],
                "helper_base": eps08a_oracle_meta["helper"]["base"],
                "helper_size": eps08a_oracle_meta["helper"]["size"],
                "helper_sha256": eps08a_oracle_meta["helper"]["sha256"],
                "request": eps08a_oracle_meta["request"],
                "response": eps08a_oracle_meta["response"],
                "command5": eps08a_oracle_meta["command5"],
                "state": eps08a_oracle_meta["state"],
                "mutation_boundary": eps08a_oracle_meta["mutation_boundary"],
                "operation": "generic DataID-0x008A CMAC service for host-owned native-generation request replacement; no ID0/ID11/application-field policy exists in the resident",
                "field_sequence": [
                    "./f33-08a-oracle install in NRTD/Park/stationary",
                    "direct NRTD->READY without OFF; openpilot then owns normal Panda access",
                    "request-plane host qualifies native MAC/freshness before arming 0x08A relay ownership",
                    "while moving, only native ID11 + CC.latActive is re-signed after B18:B19 substitution; all other requests are exact clones",
                    "full EPS power-off removes the resident",
                ],
                "persistent_flash_write": False,
                "live_qualified": True,
                "live_result": "2026-09-18 production-shaped 100-request 25-ms pipeline: 100/100 responses, resident counters +100/+100/+100, p95 24.094 ms, max 28.946 ms",
            },
            "08a_fd_mac_oracle": {
                "launcher": "f33-08a-fd-oracle",
                "payload": "ram_payloads/camry_f33_08a_fd_oracle_payload.bin",
                "payload_sha256": eps08a_fd_oracle_meta["authenticated_payload"]["sha256"],
                "staging_sha256": eps08a_fd_oracle_meta["staging"]["sha256"],
                "resident": eps08a_fd_oracle_meta["resident"],
                "helper": eps08a_fd_oracle_meta["helper"],
                "request": eps08a_fd_oracle_meta["request"],
                "response": eps08a_fd_oracle_meta["response"],
                "command5": eps08a_fd_oracle_meta["command5"],
                "mutation_boundary": eps08a_fd_oracle_meta["mutation_boundary"],
                "field_sequence": [
                    "./f33-08a-fd-oracle install in NRTD/Park/stationary",
                    "direct NRTD->READY without OFF",
                    "./f33-08a-fd-oracle known-answer in READY/Park/stationary",
                    "only after known-answer passes: ./f33-08a-fd-oracle benchmark 20",
                ],
                "persistent_flash_write": False,
                "live_qualified": False,
            },
            "standard_fd_ingress_probe": {
                "launcher": "f33-fd-ingress",
                "payload": "ram_payloads/camry_f33_fd_ingress_probe_payload.bin",
                "payload_sha256": fd_ingress_meta["authenticated_payload"]["sha256"],
                "staging_sha256": fd_ingress_meta["staging"]["sha256"],
                "resident": fd_ingress_meta["resident"],
                "helper": fd_ingress_meta["helper"],
                "state": fd_ingress_meta["state"],
                "firmware_contract": fd_ingress_meta["firmware_contract"],
                "marker_prefix_hex": fd_ingress_meta["marker_prefix_hex"],
                "mutation_boundary": fd_ingress_meta["mutation_boundary"],
                "field_sequence": [
                    "./f33-fd-ingress install in NRTD/Park/stationary",
                    "./f33-fd-ingress status; require native fd090_count > 0",
                    "./f33-fd-ingress probe in NRTD/Park/stationary; exactly one host standard-ID FD32 frame",
                    "positive result closes standard-vs-extended route-class discriminator; negative must be repeated with matched F33 70-percent Panda data timing before promotion",
                ],
                "persistent_flash_write": False,
                "live_qualified": False,
            },
            "b6_inline_signer": {
                "launcher": "f33-secoc",
                "payload": "ram_payloads/camry_f33_b6_inline_signer_payload.bin",
                "payload_sha256": inline_meta["authenticated_payload"]["sha256"],
                "resident_base": inline_meta["resident"]["base"],
                "resident_size": inline_meta["resident"]["size"],
                "resident_sha256": inline_meta["resident"]["sha256"],
                "helper_base": inline_meta["helper"]["base"],
                "helper_padded_size": inline_meta["helper"]["padded_size"],
                "helper_word_count": inline_meta["helper"]["word_count"],
                "helper_padded_sha256": inline_meta["helper"]["padded_sha256"],
                "control_can_id": inline_meta["loader"]["can_id"],
                "state": inline_meta["loader"]["state"],
                "telemetry": inline_meta["loader"]["telemetry"],
                "operation": "post-startup helper load; first prove local slot-4 signing against an untouched native B6, then replace/re-sign native B6 only while a changed nonzero C7 generation has renewed the seven-tick lease",
                "trigger": inline_meta["signer"]["trigger"],
                "domain": inline_meta["signer"]["domain"],
                "freshness_owner": inline_meta["signer"]["freshness_owner"],
                "native_oracle": inline_meta["signer"]["native_oracle"],
                "replacement": inline_meta["signer"]["replacement"],
                "runtime_control_frame": inline_meta["loader"]["runtime_control_frame"],
                "scratch": inline_meta["loader"]["scratch"],
                "mutation_boundary": inline_meta["mutation_boundary"],
                "field_sequence": [
                    "./f33-secoc install in NRTD/Park/stationary",
                    "direct NRTD->READY without OFF",
                    "./f33-secoc load-arm in READY/Park/stationary; require native Toyota trailer == locally computed trailer",
                    "./f33-secoc quiet-source in READY/Park/stationary to measure distinct native B6 rate with host C7 neutral",
                    "return Panda ownership to openpilot; CarController C7 sequence zero leaves native B6 untouched; each changed nonzero sequence renews seven foreground ticks; unchanged/zero commands cannot sustain replacement indefinitely",
                ],
                "persistent_flash_write": False,
                "stage5_receiver_bypass_required": False,
                "live_qualified": False,
                "historical_only": True,
                "superseded_by": "08a_mac_oracle + selective native ID11 request-plane replacement",
                "host_liveness": inline_meta["signer"]["host_liveness"],
                "historical_continuous_qualification": {
                    "route": "0000008d--a9f348691a",
                    "corroborating_route": "00000093--4066e7ae51",
                    "helper_padded_sha256": "b417e12dde0dc7d6478ea6f242fe9eaa246a00a9fbbcc711a5d2d3adcf159a28",
                    "boundary": "historical continuous helper only, not the current supervised default; the route records C7 and vehicle response but not EPS LocalRAM bytes",
                },
                "same_cycle_drcc_recovery": {
                    "command": "./f33-secoc recover-drcc",
                    "role": "diagnostic_only",
                    "tool": "runtime/exploit/ephemeral_runtime/camry_f33_post_install_recovery.py",
                    "physical_clear": "14FFFFFF on the six exact-car responders that accepted it",
                    "functional_clear": "0x7DF Mode 04 on Panda bus 0; require 0x7E8/7EA/7EB/7ED/7EE positive 44",
                    "acceptance": "all 11 known physical responders have no status&0xAF fault records and FRC DID1905 permits cruise without DID1906 ACC-not-available",
                    "eps_power_cycle": False,
                    "persistent_flash_write": False,
                    "live_qualified_clear_transport": True,
                    "live_qualified_after_signer_bootstrap": False,
                    "observed_vehicle_result": "dtc_clear_did_not_restore_drcc_same_ignition_cycle",
                    "restoration_observed_only_after": "full vehicle restart (also removes RAM signer)",
                },
            },
            "command5_probe": {
                "payload": "ram_payloads/camry_f33_command5_probe_payload.bin",
                "payload_sha256": command5_probe.EXPECTED_PAYLOAD_SHA256,
                "staging_sha256": command5_probe.EXPECTED_STAGING_SHA256,
                "resident_sha256": command5_probe.EXPECTED_RESIDENT_SHA256,
                "resident_base": f"0x{command5_probe.RESIDENT_BASE:08X}",
                "resident_size": command5_probe.RESIDENT_SIZE,
                "mailbox": f"0x{command5_probe.MAILBOX_BASE:08X}..0x{command5_probe.MAILBOX_BASE + command5_probe.MAILBOX_SIZE - 1:08X}",
                "operation": "stock synchronous command-5 wrapper, driver record 0, selector 4, exactly 36 input bytes and 16 output bytes",
                "config_layout": "u32 type=1 at config+0; u32 selector=4 at config+4",
                "transient_retry": "wrapper rc2 only; at most 3 total execute attempts",
                "fast_host_path": {
                    "command": "f33-sign generate-fast",
                    "foreground_tick_ms": 5,
                    "word_interval_ms": 10,
                    "behavior": "pace changed input words without intermediate SID23 reads; verify exact full input/bitmap once before EXECUTE; retry missing words only",
                    "b6_transmit": False,
                    "live_timing_qualified": False,
                },
                "negative_semantics": "a failed/ambiguous result does not prove slot 4 is forbidden",
                "input_domain": "DataID 00B6 || B6 application B0..B27 || full 6-byte freshness",
                "success_verdict": "slot4_command5_permitted=true with wrapper rc=0, done=1, status=0, output_length=16",
                "next_after_success": "f33-sign signed-id0 binds live 0x00F plus committed B6 freshness to one EPS-signed ID0/current-angle/additive-suppressed host transmission",
                "signed_id0_host_discriminator": {
                    "frame_count": 1,
                    "target_lateral_id": 0,
                    "target_angle": "fresh bus0 0x025 current angle",
                    "companion_shape": "additive suppressed, contribution 0/0",
                    "freshness": "live 0x00F epoch plus strictly-forward committed slot1 message counter",
                    "signing_race": "sign a bounded future reset, reuse unchanged resident input words, wait passively for that epoch, then transmit only in exact F33 current/current-1/current-2 cases",
                    "b6_com_window_witness": "FEBE4C02..FEBE4C1E exact B3..B31",
                    "persistent_flash_write": False,
                    "active_steering_request": False,
                },
                "panda_ownership": "cooperative exact-token lease: keep Python pandad supervisor alive, release only native child, then restart native child without reset/recovery/flash when lease ends",
                "persistent_flash_write": False,
                "dynamic_call": False,
                "key_extraction": False,
                "resident_steering_transmit": False,
                "resident_b6_transmit": False,
                "secoc_bypass": False,
                "live_qualified": True,
                "live_result": "2026-09-09 selector4 command5 generated 16-byte CMAC for exact 36-byte B6 domain on first attempt",
                "live_zero_domain_cmac": "00d0b1eca59d0760eddc5efb5b58d1d5",
            },
            "eps_origin_08a_routing_probe": {
                "launcher": "f33-08a-route",
                "payload": "ram_payloads/camry_f33_08a_tx_probe_payload.bin",
                "payload_sha256": eps08a_probe.EXPECTED_PAYLOAD_SHA256,
                "staging_sha256": eps08a_probe.EXPECTED_STAGING_SHA256,
                "resident_sha256": eps08a_probe.EXPECTED_RESIDENT_SHA256,
                "helper_sha256": eps08a_probe.EXPECTED_HELPER_SHA256,
                "resident_base": f"0x{eps08a_probe.RESIDENT_BASE:08X}",
                "resident_size": eps08a_probe.RESIDENT_SIZE,
                "helper_base": f"0x{eps08a_probe.HELPER_BASE:08X}",
                "helper_size": eps08a_probe.HELPER_SIZE,
                "operation": "capture one fresh stock Target-Lateral-ID0 0x08A and replay the exact unchanged 32-byte FV4+MAC-bearing frame once through the EPS stock lower CAN-FD writer",
                "lower_can_write": eps08a_tx_meta["tx"]["stock_lower_write"],
                "canif_hth_index": eps08a_tx_meta["tx"]["canif_hth_index"],
                "lower_driver_object_id": eps08a_tx_meta["tx"]["lower_driver_object_id"],
                "lower_driver_node": eps08a_tx_meta["tx"]["lower_driver_node"],
                "lower_driver_mailbox": eps08a_tx_meta["tx"]["lower_driver_mailbox"],
                "pending_handle_cell": eps08a_tx_meta["tx"]["pending_handle_cell"],
                "software_pdu_handle": eps08a_tx_meta["tx"]["sw_pdu_handle"],
                "completion_witness": eps08a_tx_meta["tx"]["tx_confirmation"],
                "can_id_word": eps08a_tx_meta["tx"]["can_id_word"],
                "pre_tx_uniqueness": "require the exact captured frame to be absent from a bounded pre-Tx 0x08A window before interpreting a post-Tx duplicate",
                "positive_verdict": "eps_origin_08a_visible_at_panda",
                "negative_verdict": "eps_origin_08a_not_observed_at_panda",
                "field_sequence": [
                    "first run ./f33-sign verify-native-08a and require every stock sample MAC28 to reproduce",
                    "./f33-08a-route install in NRTD/Park/stationary",
                    "direct NRTD->READY without OFF",
                    "./f33-08a-route route-native-id0 in READY/Park/stationary",
                ],
                "mutation_boundary": eps08a_tx_meta["mutation_boundary"],
                "proves": "whether the EPS-local lower CAN-FD 0x08A path reaches the Panda-visible Bus-4 domain",
                "does_not_prove": ["Brake accepts a newly fresh EPS-origin 0x08A", "stock SecOC-Tx profile retargeting", "longitudinal actuation"],
                "live_qualified": False,
            },
            "b6_midaggregate_observer": {
                "payload": "ram_payloads/camry_f33_b6_midaggregate_observer_payload.bin",
                "payload_sha256": midaggregate_observer.EXPECTED_PAYLOAD_SHA256,
                "staging_sha256": midaggregate_observer.EXPECTED_STAGING_SHA256,
                "resident_sha256": midaggregate_observer.EXPECTED_RESIDENT_SHA256,
                "resident_base": f"0x{midaggregate_observer.RESIDENT_BASE:08X}",
                "resident_size": midaggregate_observer.RESIDENT_SIZE,
                "mailbox": f"0x{midaggregate_observer.MAILBOX_BASE:08X}..0x{midaggregate_observer.MAILBOX_BASE + midaggregate_observer.MAILBOX_SIZE - 1:08X}",
                "install_success_verdict": "runtime_midaggregate_observer_live",
                "selfcheck_success_verdict": "midaggregate_observer_selfcheck_pass",
                "marker_success_verdict": "exact_id63_b6_seen_after_canif_before_secoc",
                "marker_negative_verdict": "id63_not_seen_at_midaggregate_boundary",
                "observation_boundary": "after exact 0x79EDE/0x809FE normal receive-ring drain and before untouched 0x7A272 reaches 0x6A410 SecOC consumption",
                "same_scheduler_positive_control": "native protected 0x0D7 profile-1 queue32 at FEBE5472",
                "b6_queue_witness": "profile-2 queue32 at FEBE547A; marker identity from FEBE54D4 secured bytes",
                "treatment_marker": "Target Lateral ID63 with additive contribution suppressed",
                "marker_jitter_ms": list(midaggregate_observer.JITTER_MS),
                "sid23_reads_during_treatment": 0,
                "signature_match": "resident B0..B11||B28..B31 must equal one transmitted marker frame",
                "nrt_d_attestation": "resident SHA plus mailbox magic/version only; receive-gated observation liveness is deferred to READY D7 selfcheck",
                "source_memory_write": False,
                "dynamic_call": False,
                "resident_steering_transmit": False,
                "resident_b6_transmit": False,
                "host_marker_b6_transmit": True,
                "secoc_bypass": False,
                "route44_publish": False,
                "codeflash_write": False,
                "live_qualified": False,
                "next_after_install": "direct NRTD->READY without OFF; run ./f33-ingress selfcheck and require D7 positive control before ./f33-ingress marker",
                "superseded_by": "b6_ingress_observer",
                "live_result": "2026-09-10 full-runtime install failed before observer initialization; no ingress conclusion",
            },
            "b6_ingress_observer": {
                "launcher": "f33-ingress",
                "payload": "ram_payloads/camry_f33_b6_ingress_helper_payload.bin",
                "payload_sha256": ingress_meta["authenticated_payload"]["sha256"],
                "resident_base": ingress_meta["resident"]["base"],
                "resident_size": ingress_meta["resident"]["size"],
                "resident_sha256": ingress_meta["resident"]["sha256"],
                "helper_base": ingress_meta["helper"]["base"],
                "helper_size": ingress_meta["helper"]["size"],
                "helper_padded_size": ingress_meta["helper"]["padded_size"],
                "helper_padded_sha256": ingress_meta["helper"]["padded_sha256"],
                "telemetry": ingress_meta["loader"]["telemetry"],
                "observation_boundary": ingress_meta["static_pins"]["midaggregate_boundary"],
                "mutation_boundary": ingress_meta["mutation_boundary"],
                "field_sequence": [
                    "./f33-ingress install in NRTD/Park/stationary; require inline_signer_resident_live_loader_ready",
                    "direct NRTD->READY without OFF",
                    "./f33-ingress load-arm; require exact padded helper readback",
                    "./f33-ingress selfcheck; require midaggregate_observer_selfcheck_pass",
                    "./f33-ingress marker --bus 0; interpret exact signature match or bounded D7-positive no-marker verdict",
                ],
                "live_qualified": True,
                "live_result": "2026-09-10 selfcheck deltas observation/D7/B6=409/102/205; marker sent/returned 121/121, observer deltas=434/109/217, ID63 delta=0; verdict id63_not_seen_at_midaggregate_boundary",
                "persistent_flash_write": False,
            },
            "runtime_monitor": {
                "payload": "ram_payloads/camry_f33_runtime_monitor_payload.bin",
                "payload_sha256": runtime_monitor.EXPECTED_PAYLOAD_SHA256,
                "staging_sha256": runtime_monitor.EXPECTED_STAGING_SHA256,
                "resident_sha256": runtime_monitor.EXPECTED_RESIDENT_SHA256,
                "resident_base": f"0x{runtime_monitor.RESIDENT_BASE:08X}",
                "resident_size": runtime_monitor.RESIDENT_SIZE,
                "control_can_id": f"0x{runtime_monitor.CONTROL_CAN_ID:08X}",
                "control_frame": "00 F3 seq opcode arg32-le",
                "watch_slots": runtime_monitor.WATCH_SLOTS,
                "watch_window_bytes": 4,
                "success_verdict": "runtime_monitor_live",
                "next_after_success": "NRTD->READY without OFF; use phase A..G for current-angle B6 localization or status/watch/run/stop/snapshot/capture/shell without another RAM execute",
                "source_memory_write": False,
                "dynamic_call": False,
                "resident_steering_transmit": False,
                "resident_b6_transmit": False,
                "host_phase_b6_transmit": True,
                "host_phase_b6_construction": "imports current /data/openpilot opendbc Toyota TSS3 helper; ID11, active companions 0/100/100, dummy-CMAC envelope, target=fresh 0x025 steering angle",
                "stationary_monitor_phases": {k: [f"0x{x:08X}" for x in v] for k, v in runtime_monitor.MONITOR_PHASES.items()},
                "secoc_bypass": False,
            },
            "runtime_monitor_intertick": {
                "payload": "ram_payloads/camry_f33_runtime_monitor_intertick_payload.bin",
                "payload_sha256": intertick_monitor.EXPECTED_PAYLOAD_SHA256,
                "staging_sha256": intertick_monitor.EXPECTED_STAGING_SHA256,
                "resident_sha256": intertick_monitor.EXPECTED_RESIDENT_SHA256,
                "resident_base": f"0x{runtime_monitor.RESIDENT_BASE:08X}",
                "resident_size": intertick_monitor.RESIDENT_SIZE,
                "control_can_id": f"0x{runtime_monitor.CONTROL_CAN_ID:08X}",
                "sample_point": "tight queue poll while waiting for each foreground tick; queue test occurs before the tick test and before stock 0x667E6 consumption",
                "run_trigger": "exact profile-2 queue length FEBE547A == 32 AND secured B3 low6 == ID63 marker; native parked ID0 cannot steal the latch",
                "phase": {k: [f"0x{x:08X}" if x else None for x in v] for k, v in intertick_monitor.INTERTICK_PHASES.items()},
                "host_phase_b6_construction": "current opendbc framing/freshness with Target Lateral ID63 and additive contribution suppressed; ID63 is outside the recovered F33 command-mode decoder",
                "success_verdict": "exact_phase_b6_queued_intertick",
                "next_after_success": "superseded before live use: exact scheduler recovery shows the queue can be created and consumed inside one 0x7A254 invocation, outside this between-tick sample point",
                "source_memory_write": False,
                "dynamic_call": False,
                "resident_steering_transmit": False,
                "resident_b6_transmit": False,
                "host_phase_b6_transmit": True,
                "secoc_bypass": False,
                "live_qualified": False,
                "superseded_by": "b6_midaggregate_observer",
                "superseded_before_live_use": True,
            },
            "runtime_monitor_preaggregate": {
                "payload": "ram_payloads/camry_f33_runtime_monitor_preaggregate_payload.bin",
                "payload_sha256": preaggregate_monitor.EXPECTED_PAYLOAD_SHA256,
                "staging_sha256": preaggregate_monitor.EXPECTED_STAGING_SHA256,
                "resident_sha256": preaggregate_monitor.EXPECTED_RESIDENT_SHA256,
                "resident_base": f"0x{runtime_monitor.RESIDENT_BASE:08X}",
                "resident_size": preaggregate_monitor.RESIDENT_SIZE,
                "control_can_id": f"0x{runtime_monitor.CONTROL_CAN_ID:08X}",
                "sample_point": "after fg_pre_3, immediately before stock fg_aggregate",
                "run_trigger": "sticky snapshot only when exact profile-2 queue length FEBE547A is nonzero",
                "phase": {k: [f"0x{x:08X}" for x in v] for k, v in preaggregate_monitor.PREAGGREGATE_PHASES.items()},
                "success_verdict": "runtime_monitor_live",
                "next_after_success": "NRTD->READY without OFF; run ./f33-pre phase P and require exact_phase_b6_queued_preaggregate before interpreting route44 transformation",
                "source_memory_write": False,
                "dynamic_call": False,
                "resident_steering_transmit": False,
                "resident_b6_transmit": False,
                "host_phase_b6_transmit": True,
                "secoc_bypass": False,
                "live_qualified": True,
                "live_result": "2026-09-08 Phase P observed queue zero at the immediately-pre-aggregate point; exact scheduler review shows this sample point is insufficient to exclude asynchronous enqueue/consume between foreground observations",
                "superseded_by": "b6_midaggregate_observer",
            },
            "runtime_replay_discriminator": {
                "payload": "ram_payloads/camry_f33_runtime_replay_discriminator_payload.bin",
                "payload_sha256": replay_discriminator.EXPECTED_PAYLOAD_SHA256,
                "staging_sha256": replay_discriminator.EXPECTED_STAGING_SHA256,
                "resident_sha256": replay_discriminator.EXPECTED_RESIDENT_SHA256,
                "resident_base": f"0x{replay_discriminator.RESIDENT_BASE:08X}",
                "resident_size": replay_discriminator.RESIDENT_SIZE,
                "clean_window_ticks": replay_discriminator.FIRST_SNAPSHOT_TICK,
                "clean_window_nominal_seconds": replay_discriminator.FIRST_SNAPSHOT_NOMINAL_SECONDS,
                "source_terms_mailbox": f"0x{replay_discriminator.MAILBOX_BASE:08X}..0x{replay_discriminator.MAILBOX_BASE + replay_discriminator.MAILBOX_SIZE - 1:08X}",
                "purpose": "qualify ABI-preserving startup/foreground replay and recover the canonical D0218 source-term profile",
                "success_verdict": "abi_preserving_runtime_and_source_terms_live",
                "next_after_success": "NRTD->READY without OFF; run same tool --read-existing --parked-stationary-confirmed for parked source-term liveness",
                "ready_read_existing_success_verdict": "ready_parked_source_terms_live",
                "bypass": False,
                "live_qualified": False,
                "superseded_by": "runtime_monitor",
            },
            "observer": {
                "payload": "ram_payloads/camry_f33_b6_transaction_observer_payload.bin",
                "payload_sha256": observer_install.EXPECTED_PAYLOAD_SHA256,
                "shellcode_sha256": observer_install.OBSERVER_SHELLCODE_SHA256,
                "telemetry_base": f"0x{observer_install.TELEMETRY_BASE:08X}",
                "telemetry_size": observer_install.TELEMETRY_SIZE,
                "bypass": False,
                "live_qualified": False,
                "blocked_by": "superseded C call0(address) startup/foreground trampoline corrupts RH850 r6; rebuild with ABI-preserving calls before live use",
            },
            "bridge": {
                "payload": "ram_payloads/camry_f33_b6_bridge_payload.bin",
                "payload_sha256": bridge_install.EXPECTED_PAYLOAD_SHA256,
                "shellcode_sha256": bridge_install.BRIDGE_SHELLCODE_SHA256,
                "mailbox": "FEBF0000 v3; stock foreground tick is the liveness witness",
                "call_abi": "direct linker-resolved JARL32; no C call0(address) trampoline",
                "behavior": "snapshot exact queued 32-byte B6 before aggregate, conservatively skip when post-aggregate raw route44 B3 matches saved B3, otherwise re-publish saved bytes through stock route44 callback 0x7D72C",
                "bypass": "SecOC adjudication only; re-enters stock route44 callback",
                "arm_guards": ["--arm-bridge", "--parked-stationary-confirmed"],
                "live_qualified": False,
                "requires_before_arm": "first prove the exact injected ID63 frame reaches profile2 with b6_midaggregate_observer; bridge is a later controlled transformation experiment",
            },
            "order": [
                "08a_mac_oracle is the production volatile signer service: install in NRTD, transition directly to READY without OFF, then openpilot signs exact observed native 0x08A generations through the generic DataID-0x008A command-5 oracle while Panda owns relay replacement",
                "b6_inline_signer is retained only as historical direct-B6 development evidence and must not be armed alongside the request-plane path",
                "command5_probe is retained as the earlier bounded diagnostic oracle; the 0x08A streaming oracle is the continuous signing service",
                "eps_origin_08a_routing_probe is the non-actuating topology discriminator: after passive native-0x08A MAC reproduction, replay one unchanged stock ID0 frame from the EPS lower CAN-FD path and observe whether that exact FV4+MAC frame reaches Panda",
                "b6_ingress_observer is the live-qualified two-stage topology discriminator; its 2026-09-10 D7-positive marker run closed bounded negative for direct Panda ID63 at post-CanIf/pre-SecOC",
                "the original b6_midaggregate_observer full-runtime install failed before initialization and is retained only as a superseded artifact",
                "runtime_monitor_preaggregate and runtime_monitor_intertick are retained only as timing-insufficient/superseded predecessors and should not be rerun",
                "runtime_monitor remains the general post-aggregate A-G gate monitor for later downstream localization after ingress identity is settled",
                "ABI-safe bridge is available only as a later parked/stationary queue->route44 transformation experiment after exact marker ingress is proven",
                "runtime replay discriminator and legacy C B6 observer retained as artifacts only",
            ],
        },
        "firmware_patch": {
            "historical_only": True,
            "stage2_installed": {
                "sites": [
                    {"address": "0x8F948", "bytes": "003a"},
                    {"address": "0x8F952", "bytes": "e001"},
                ],
                "fixup": "0xD12ADB05",
                "sha256": stage3.EXPECTED_STAGE2_SHA256,
            },
            "stage3_candidate": {
                "address": "0x8F930",
                "bytes": "e00714d3",
                "final_prefix": "0x13ADA3CC",
                "final_fixup": "0xEC525C33",
            },
            "source_image_sha256": stage3.EXPECTED_STAGE2_SHA256,
            "final_image_sha256": stage3.EXPECTED_FINAL_SHA256,
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
