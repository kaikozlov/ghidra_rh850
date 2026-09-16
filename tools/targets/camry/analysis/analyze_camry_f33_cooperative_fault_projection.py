#!/usr/bin/env python3
"""Bind exact-F33 cooperative inhibits to transmitted status and ready-state gates."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from tools.targets.camry.support.camry_f33_corpus import CORPUS, IMAGE, IMAGE_SHA256

ROOT = Path(__file__).resolve().parents[4]
OUTPUT = ROOT / 'data/generated/camry_f33_cooperative_fault_projection.json'


def build() -> dict:
    image = IMAGE.read_bytes()
    if hashlib.sha256(image).hexdigest() != IMAGE_SHA256:
        raise ValueError('wrong F33 image')
    entries = {0x4C2DC, 0x4C97A, 0xBF3AA, 0xD0D7C, 0xCEC72, 0xCEC0C, 0xCEE7C, 0xCEF26, 0xCE772, 0xCE7A6}
    functions = []
    for line in CORPUS.open():
        row = json.loads(line)
        entry = int(row.get('entry_addr', '0'), 16)
        if entry in entries:
            size = row['body_size']
            functions.append({'entry': f'0x{entry:08X}', 'size': size,
                              'sha256': hashlib.sha256(image[entry:entry + size]).hexdigest()})
    if len(functions) != len(entries):
        raise ValueError('incomplete exact-firmware evidence')
    return {
        'schema': 'camry-f33-cooperative-fault-projection-v1',
        'source': {'path': str(IMAGE.relative_to(ROOT)), 'sha256': IMAGE_SHA256, 'functions': functions},
        'command_inhibit': {
            'producer': '0xCEC72', 'expression': 'u8(FEBECAFB) OR u8(FEBECAFD)',
            'rte_path': ['FEBECAFC', 'FEBEAD42', 'FEBEE834', 'FEBE80EC', 'FEBE8C43'],
            'rte_functions': ['0xD0D7C', '0xBF3AA', '0x4C2DC', '0x4C97A'],
            'generated_signal': 25, 'can_id': '0x030', 'byte': 16, 'bit': 0,
            'structural_name': 'F33_COOPERATIVE_COMMAND_INHIBIT',
        },
        'angle_inhibit': {
            'producer_state': 'FEBECAD9',
            'rte_path': ['FEBECAD9', 'FEBEAD4B', 'FEBEE83A', 'FEBE80E0', 'FEBE8C47'],
            'rte_functions': ['0xD0D7C', '0xBF3AA', '0x4C2DC', '0x4C97A'],
            'generated_signal': 31, 'can_id': '0x030', 'byte': 19, 'bit': 0,
            'structural_name': 'F33_COOPERATIVE_ANGLE_INHIBIT',
        },
        'consumer_contract': {
            'ready_entry': '0xCE772 returns ready only when both inhibits are zero and its other predicates pass',
            'active_exit': '0xCE7A6 exits ready immediately when either inhibit is one',
            'normal_clear_case': 'both flags zero neither block entry nor force exit when other predicates pass',
        },
        'recovery_information_loss': {
            'request_failure': '0xCEE7C clears FEBECAFB in inactive profile bank 7',
            'rate_latch': '0xCEF26 retains asserted FEBECAFD even in inactive profile bank 7',
            'subsystem_initialization': '0xCEC0C clears both sources and their combined flag',
            'wire_collision': 'CAFB=1/CAFD=0 and CAFB=0/CAFD=1 both publish the same command-inhibit bit',
            'boundary': 'these transmitted bits cannot independently select restart-required versus self-clearing causes; other diagnostic/status surfaces are not ruled out',
        },
        'openpilot_mapping': {
            'platform': 'TOYOTA_CAMRY_TSS3 only',
            'steerFaultTemporary': 'current selected hardware fault OR cooperative command inhibit OR cooperative angle inhibit',
            'steerFaultPermanent': 'not inferred from these lossy projections',
            'semantics': 'current steering unavailability, not a guarantee of automatic repair; no host-side persistence timer or new engagement policy',
        },
        'verification': {
            'script': 'ghidra/scripts/verify/VerifyCamryCooperativeFaultProjection.java',
            'method': 'stock OR, RTE, readiness and recovery instructions; generated-COM argument capture at the packer boundary',
            'boundary': 'scalar packer/status-submit callbacks are substituted; no CAN hardware or vehicle is exercised',
            'assertions': 59,
        },
    }


if __name__ == '__main__':
    OUTPUT.write_text(json.dumps(build(), indent=2, sort_keys=True) + '\n')
    print(OUTPUT)
