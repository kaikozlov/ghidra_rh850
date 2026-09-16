#!/usr/bin/env python3
"""Reproduce the explicit stock-harness oracle when original logs are present."""
import json
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / 'data/generated/camry_2026_stock_harness_topology.json'
EXTRACTOR = ROOT / 'tools/targets/camry/analysis/analyze_camry_2026_stock_harness_topology.py'
OP = ROOT.parent / 'kai-openpilot'
PYTHON = OP / '.venv/bin/python'
LOGS = ROOT.parent.parent / 'logs/camry-2026/2026-09-11'
report = json.loads(ARTIFACT.read_text())
assert report['schema'] == 'camry-stock-harness-topology-v2'
assert report['physical_network_roles']['panda_bus1'].startswith('stock Toyota-B unsplit Toyota Bus-4')
assert report['candidate_direction']['direct_frc_bus1_pdus']['panda_bus'] == 2
assert report['candidate_direction']['protected_bus4_request_result_family']['panda_bus'] == 1
for source in report['sources']:
    rows = source['native_messages']
    for address, bus, size in [
        ('0x20', 2, 12), ('0x160', 2, 32), ('0x230', 2, 64), ('0x440', 2, 32),
        ('0x8a', 1, 32), ('0xc9', 1, 32), ('0xca', 1, 32),
        ('0x25', 1, 32), ('0x101', 1, 8), ('0x412', 1, 8),
    ]:
        matches = [r for r in rows if r['address'] == address]
        assert matches and all((r['bus'], r['length']) == (bus, size) for r in matches)
    for addr in range(0x180, 0x186):
        matches = [r for r in rows if r['address'] == hex(addr)]
        assert matches and all(r['bus'] == 0 and r['length'] == 64 and r['count'] > 1190 for r in matches)
if not PYTHON.exists() or not all((LOGS / r['path']).is_file() for r in report['sources']):
    print('[SKIP] original stock-topology logs/parser environment not present; retained artifact checks passed')
else:
    with tempfile.TemporaryDirectory() as td:
        output = Path(td) / 'topology.json'
        subprocess.run([str(PYTHON), str(EXTRACTOR), '--out', str(output), '--openpilot-root', str(OP), '--log-root', str(LOGS)],
                       check=True, cwd=OP, timeout=120, stdout=subprocess.DEVNULL)
        assert output.read_bytes() == ARTIFACT.read_bytes()
    print('[PASS] four original rlog segments reproduce the stock-harness topology byte-identically')
