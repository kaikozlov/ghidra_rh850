#!/usr/bin/env python3
"""Verify target-native live fault aggregation and recovery using stock instructions."""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools.targets.camry.analysis import analyze_camry_f33_live_fault_projection as evidence

assert evidence.build() == json.loads(evidence.OUTPUT.read_text())
with tempfile.TemporaryDirectory() as tmp:
    result = Path(tmp) / 'result.json'
    subprocess.run([str(ROOT / 'tools/gtarget'), 'camry-8965F3307000', 'script', 'run',
                    str(ROOT / 'ghidra/scripts/verify/VerifyCamryFaultProjection.java'), '--',
                    str(evidence.IMAGE), str(result)], cwd=ROOT, check=True, capture_output=True, timeout=90)
    report = json.loads(result.read_text())
    assert report['passed'] == 85 and not report['vehicle_executed']
    print('PASS: exact image/corpus regeneration and 85 stock-instruction fault truth-table/recovery assertions')
