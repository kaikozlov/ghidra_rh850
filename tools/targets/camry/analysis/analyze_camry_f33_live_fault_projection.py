#!/usr/bin/env python3
"""Describe the exact F33 live fault projection, separate from latched history."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from tools.targets.camry.support.camry_f33_corpus import CORPUS, IMAGE, IMAGE_SHA256

ROOT = Path(__file__).resolve().parents[4]
OUTPUT = ROOT / 'data/generated/camry_f33_live_fault_projection.json'


def build() -> dict:
    image = IMAGE.read_bytes()
    if hashlib.sha256(image).hexdigest() != IMAGE_SHA256:
        raise ValueError('wrong F33 image')
    entries = {0x4C000, 0x4C97A, 0x50FC8, 0x514BC, 0x51C66, 0x51D5E}
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
    classes = {2: [], 16: [], 32: []}
    for event in range(0x180):
        record = image[0x2FC50 + event * 8:0x2FC58 + event * 8]
        if record[1] in classes:
            classes[record[1]].append(event)
    return {
        'schema': 'camry-f33-live-fault-projection-v1',
        'source': {'path': str(IMAGE.relative_to(ROOT)), 'sha256': IMAGE_SHA256, 'functions': functions},
        'projection': {'producer': '0x0004C000', 'value': '0xFEBE80DE', 'transmit_staging': '0xFEBE8C35',
                       'packer': '0x0004C97A', 'pdu': 0, 'signal': 7, 'can_id': '0x030', 'byte': 6, 'bit': 2,
                       'operator': 'OR',
                       'nonzero_u16_inputs': ['0xFEBE82BA', '0xFEBE82C2', '0xFEBE82C4'],
                       'equals_0x22_u8_inputs': ['0xFEBEE857', '0xFEBEE858', '0xFEBEE859']},
        'live_event_classes': {f'0x{key:02X}': {'count': len(value), 'events': [f'0x{v:04X}' for v in value]}
                               for key, value in sorted(classes.items())},
        'event_lifecycle': {'assertion': '0x51C66 increments a selected class only on a newly active event via 0x50FC8',
                            'recovery': '0x51D5E decrements a previously active class via 0x514BC, saturating at zero',
                            'history': '0xFEBE82A3/82A4/82A5 latched class history is NOT read by this live projection'},
        'openpilot_mapping': {'platform': 'TOYOTA_CAMRY_TSS3',
                              'steerFaultTemporary': 'current EPS_FAULT_INHIBIT contribution OR the separately recovered cooperative-command and angle inhibits',
                              'cooperative_evidence': 'data/generated/camry_f33_cooperative_fault_projection.json',
                              'steerFaultPermanent': 'not supplied by this one-bit current-state projection',
                              'interpretation': 'Temporary means current steering unavailability in the ordinary openpilot interface, not a prediction that every underlying hardware fault will self-repair.',
                              'missing_coverage': 'Only selected classes/statuses are represented. Other fault classes and restart-required causes cannot be reconstructed from this bit.',
                              'other_variants': 'No H/F or Crown policy transfer is made.'},
        'verification': {'script': 'ghidra/scripts/verify/VerifyCamryFaultProjection.java',
                          'method': 'execute actual stock instruction truth table plus assertion/recovery counts in emulator-local RAM',
                          'vehicle_execution': False},
    }


if __name__ == '__main__':
    OUTPUT.write_text(json.dumps(build(), indent=2, sort_keys=True) + '\n')
    print(OUTPUT)
