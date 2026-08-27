#!/usr/bin/env python3
"""Regenerate committed Corolla H builder artifacts (full/local only)."""
from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
passed = failed = 0

def check(name, cond, detail=''):
    global passed, failed
    ok = bool(cond)
    passed += int(ok)
    failed += int(not ok)
    suffix = f' ({detail})' if detail else ''
    print(f"[{'PASS' if ok else 'FAIL'}] {name}{suffix}")

BUILDERS = [
    ('application callback tables', 'tools/build_corolla_h_application_callback_tables.py', 'data/generated/corolla_8965H1202000_application_callback_tables.json'),
    ('application diagnostics', 'tools/compare_variant_application_diagnostics.py', 'data/generated/corolla_8965H1202000_application_diagnostics_diff.json'),
    ('application interrupt bodies', 'tools/build_corolla_h_application_interrupt_bodies.py', 'data/generated/corolla_8965H1202000_application_interrupt_bodies.json'),
    ('application interrupt vectors', 'tools/build_corolla_h_application_interrupt_vectors.py', 'data/generated/corolla_8965H1202000_application_interrupt_vectors.json'),
    ('application transport residue', 'tools/build_corolla_h_application_transport_residue.py', 'data/generated/corolla_8965H1202000_application_transport_residue.json'),
    ('b6 full receiver contract', 'tools/build_corolla_h_b6_full_receiver_contract.py', 'data/generated/corolla_8965H1202000_b6_full_receiver_contract.json'),
    ('b6 receiver contract', 'tools/build_corolla_h_b6_receiver_contract.py', 'data/generated/corolla_8965H1202000_b6_receiver_contract.json'),
    ('b6 secoc verification', 'tools/build_corolla_h_b6_secoc_verification.py', 'data/generated/corolla_8965H1202000_b6_secoc_verification.json'),
    ('b6 target angle ingress', 'tools/build_corolla_h_b6_target_angle_ingress.py', 'data/generated/corolla_8965H1202000_b6_target_angle_ingress.json'),
    ('can com', 'tools/build_corolla_h_can_com.py', 'data/generated/corolla_8965H1202000_can_com.json'),
    ('crypto residue', 'tools/build_corolla_h_crypto_residue.py', 'data/generated/corolla_8965H1202000_crypto_residue.json'),
    ('deadline monitor surface', 'tools/build_corolla_h_deadline_monitor_surface.py', 'data/generated/corolla_8965H1202000_deadline_monitor_surface.json'),
    ('diagnostic residue', 'tools/build_corolla_h_diagnostic_residue.py', 'data/generated/corolla_8965H1202000_diagnostic_residue.json'),
    ('direct call surface', 'tools/build_corolla_h_direct_call_surface.py', 'data/generated/corolla_8965H1202000_direct_call_surface.json'),
    ('fd control', 'tools/build_corolla_h_fd_control_interface.py', 'data/generated/corolla_8965H1202000_fd_control_interface.json'),
    ('final named residue', 'tools/build_corolla_h_final_named_residue.py', 'data/generated/corolla_8965H1202000_final_named_residue.json'),
    ('lta command provenance', 'tools/build_corolla_h_lta_command_provenance.py', 'data/generated/corolla_8965H1202000_lta_command_provenance.json'),
    ('motor control', 'tools/build_corolla_h_motor_control.py', 'data/generated/corolla_8965H1202000_motor_control.json'),
    ('openpilot state bridge', 'tools/build_corolla_h_openpilot_state_bridge.py', 'data/generated/corolla_8965H1202000_openpilot_state_bridge.json'),
    ('plausibility monitor', 'tools/build_corolla_h_plausibility_monitor.py', 'data/generated/corolla_8965H1202000_plausibility_monitor.json'),
    ('power supply monitor gate', 'tools/build_corolla_h_power_supply_monitor_gate.py', 'data/generated/corolla_8965H1202000_power_supply_monitor_gate.json'),
    ('secoc key provenance', 'tools/build_corolla_h_secoc_key_provenance.py', 'data/generated/corolla_8965H1202000_secoc_key_provenance.json'),
    ('secoc surface', 'tools/build_corolla_h_secoc_surface.py', 'data/generated/corolla_8965H1202000_secoc_surface.json'),
    ('small adapters', 'tools/build_corolla_h_small_adapters.py', 'data/generated/corolla_8965H1202000_small_adapters.json'),
    ('static coverage', 'tools/build_corolla_h_static_coverage_matrix.py', 'data/generated/corolla_8965H1202000_static_coverage_matrix.json'),
    ('steering nested', 'tools/build_corolla_h_steering_nested.py', 'data/generated/corolla_8965H1202000_steering_nested.json'),
    ('steering supervisor', 'tools/build_corolla_h_steering_supervisor_stage_ledger.py', 'data/generated/corolla_8965H1202000_steering_supervisor_stage_ledger.json'),
    ('storage nvm', 'tools/build_corolla_h_storage_nvm.py', 'data/generated/corolla_8965H1202000_storage_nvm.json'),
    ('system orchestration', 'tools/build_corolla_h_system_orchestration.py', 'data/generated/corolla_8965H1202000_system_orchestration.json'),
    ('techstream correlations', 'tools/build_corolla_h_techstream_correlations.py', 'data/generated/corolla_8965H1202000_techstream_correlations.json'),
    ('veneer bank', 'tools/build_corolla_h_veneer_bank.py', 'data/generated/corolla_8965H1202000_veneer_bank.json'),
    ('xcp', 'tools/build_corolla_h_xcp.py', 'data/generated/corolla_8965H1202000_xcp.json'),
]

for title, builder, artifact in BUILDERS:
    print(f'== {title} regen ==')
    tool = ROOT / builder
    art = ROOT / artifact
    with tempfile.TemporaryDirectory() as td:
        out = Path(td) / 'out.json'
        proc = subprocess.run(
            [sys.executable, str(tool), '--out', str(out)],
            cwd=ROOT, capture_output=True, text=True, check=False,
        )
        check(f'{title} builder exits cleanly', proc.returncode == 0,
              (proc.stderr or proc.stdout)[-300:] if proc.returncode else '')
        check(
            f'{title} artifact regenerates exactly',
            proc.returncode == 0 and out.exists() and out.read_bytes() == art.read_bytes(),
        )
    print()
print(f'\n== RESULT: {passed} passed, {failed} failed ==')
raise SystemExit(1 if failed else 0)
