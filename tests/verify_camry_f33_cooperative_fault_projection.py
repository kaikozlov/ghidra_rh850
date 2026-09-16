#!/usr/bin/env python3
"""Verify exact stock readiness, wire binding and recovery information loss."""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools.targets.camry.analysis import analyze_camry_f33_cooperative_fault_projection as evidence

assert evidence.build() == json.loads(evidence.OUTPUT.read_text())
with tempfile.TemporaryDirectory() as tmp:
    output = Path(tmp) / 'result.json'
    subprocess.run([str(ROOT / 'tools/gtarget'), 'camry-8965F3307000', 'script', 'run',
                    str(ROOT / 'ghidra/scripts/verify/VerifyCamryCooperativeFaultProjection.java'), '--',
                    str(evidence.IMAGE), str(output)], cwd=ROOT, check=True, capture_output=True, timeout=90)
    report = json.loads(output.read_text())
    assert report['passed'] == 59 and report['vehicle_executed'] is False
    print('PASS: exact image/corpus and 59 stock-instruction cooperative fault/readiness/wire assertions')
