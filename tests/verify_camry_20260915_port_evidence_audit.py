#!/usr/bin/env python3
"""Check the port audit against original retained logs when they are available."""
from __future__ import annotations
import json
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / 'data/generated/camry_20260915_port_evidence_audit.json'
BUILDER = ROOT / 'tools/targets/camry/analysis/analyze_camry_20260915_port_audit.py'
OP = ROOT.parent / 'kai-openpilot'
LOGS = ROOT.parent.parent / 'logs/camry-2026'
report = json.loads(ART.read_text())
assert report['schema'] == 'camry-port-evidence-audit-v1'
assert report['vehicle_access'] is False
assert sum(len(rows) for rows in report['route_groups'].values()) == 7
for group in ('working_repin', 'working_repin_corroboration'):
    for row in report['route_groups'][group]:
        cp = row['recorded_car_params']
        assert abs(cp['tireStiffnessFactor'] - 0.7933) < 1e-6
        assert row['learned_stiffness_multiplier']['min'] > 0.99
        assert row['lag_estimates']['distinct'] == 1
        assert abs(row['lag_estimates']['median'] - 0.3837597370147705) < 1e-9
        modes = {m['value'] for m in row['cruise_mode_b0']}
        assert '0x90' in modes and not modes.intersection({'0xA0', '0xC0'})
for row in report['route_groups']['stock_harness_eps_absent']:
    messages = row['native_can']
    assert not any(m['address'] == '0x030' for m in messages)
    for address, bus, length in (('0x025', 1, 32), ('0x412', 1, 8), ('0x101', 1, 8),
                                 ('0x160', 2, 32), ('0x180', 0, 64)):
        matches = [m for m in messages if m['address'] == address]
        assert matches and all(m['bus'] == bus and m['length'] == length for m in matches)
for row, total, outside in zip(report['native_longitudinal_handoff'], (20510, 23998), (127, 1373), strict=True):
    assert row['frames'] == total and row['outside_host_command_bounds'] == outside
    assert row['bad_crc'] == 0
    assert row['b12_high_bit_set'] == 0
sources = [LOGS / row['source'] for rows in report['route_groups'].values() for row in rows]
python = OP / '.venv/bin/python'
if python.is_file() and all(path.is_file() for path in sources):
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / ART.name
        subprocess.run([str(python), str(BUILDER), '--out', str(out), '--logs-root', str(LOGS), '--openpilot-root', str(OP)],
                       cwd=OP, check=True, timeout=120, stdout=subprocess.DEVNULL)
        assert out.read_bytes() == ART.read_bytes()
    print('[PASS] seven pinned rlog segments and both complete August captures regenerate byte-identically')
else:
    print('[SKIP] original-log regeneration unavailable; all retained artifact contract checks passed')
