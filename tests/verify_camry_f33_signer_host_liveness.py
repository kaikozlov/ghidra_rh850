#!/usr/bin/env python3
"""Compile the F33 candidate and exercise its actual instructions in Ghidra."""
from __future__ import annotations
import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from exploit.ephemeral_runtime import camry_f33_b6_inline_signer as host

SOURCE = ROOT / 'ghidra/scripts/verify/VerifyCamrySignerHostLiveness.java'
BUILDER = ROOT / 'exploit/ephemeral_runtime/build_camry_f33_b6_inline_signer.py'
AUDITED = ROOT / 'exploit/ephemeral_runtime/audited'
MANIFEST = ROOT / 'exploit/ephemeral_runtime/audited_camry_f33_b6_inline_signer_supervised_build.json'
PREFIX = 'camry_f33_b6_inline_signer_supervised'

for mode in ('continuous-signed', 'supervised-signed'):
    session = SimpleNamespace(bundle=SimpleNamespace(meta={'mode': mode}))
    try:
        host.InlineSignerSession.replace_once(session, target_angle_raw=0)
    except host.InlineSignerError:
        pass
    else:
        raise AssertionError('held-command helper exposed an unsafe one-frame operation')

with tempfile.TemporaryDirectory() as tmp:
    out = Path(tmp)
    subprocess.run([sys.executable, str(BUILDER), '--mode', 'supervised-signed', '--output-dir', str(out)],
                   cwd=ROOT, check=True, stdout=subprocess.DEVNULL)
    meta = json.loads((out / (PREFIX + '.json')).read_text())
    assert meta == json.loads(MANIFEST.read_text())
    for path in out.glob('*.bin'):
        assert path.read_bytes() == (AUDITED / path.name).read_bytes(), path.name
    assert meta['helper']['size'] <= 600 and meta['resident']['size'] <= 524
    assert meta['resident']['sha256'] == '31b1b2c31007f130d6b4679a0c99f5903a58f748daf11978f9c52f504aea3a3a'
    assert not meta['helper']['relocations'] and not meta['resident']['relocations']
    helper = out / (PREFIX + '_helper.bin')
    result = out / 'liveness.json'
    historical = AUDITED / 'camry_f33_b6_inline_signer_continuous_helper.bin'
    command = [str(ROOT / 'tools/gtarget'), 'camry-8965F3307000', 'script', 'run', str(SOURCE), '--', str(helper), str(result), str(historical)]
    subprocess.run(command, cwd=ROOT, check=True, capture_output=True, text=True, timeout=90)
    record = json.loads(result.read_text())
    assert record['passed'] >= 86 and record['vehicle_executed'] is False
    assert record['helper_sha256'] == hashlib.sha256(helper.read_bytes()).hexdigest()
    command[-3] = str(historical)
    command.pop()
    result.unlink()
    regression = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, timeout=90)
    assert regression.returncode != 0
    assert 'host loss expires at seventh tick' in regression.stdout + regression.stderr
    assert not result.exists()
    print(f"PASS: reproducible {meta['helper']['size']}-byte helper; {record['passed']} compiled-instruction assertions; historical helper fails host-loss regression")
