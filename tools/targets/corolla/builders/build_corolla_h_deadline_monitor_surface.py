#!/usr/bin/env python3
"""Build Sienna->Corolla-H deadline-monitor native-role and callback closure."""
from __future__ import annotations

import argparse
import hashlib
import json
import struct
from pathlib import Path

from tools import REPO_ROOT
from tools.project.analysis_target import path as target_path
from tools.targets.corolla.support.corolla_h_constants import H_DEADLINE_TABLES, SIENNA_DEADLINE_TABLES

ROOT = REPO_ROOT
S_TARGET = 'sienna-8965B4512000'
H_TARGET = 'corolla-8965H1202000'
EV = ROOT / 'data/generated/corolla_8965H1202000_deadline_monitor_surface_decompiler_evidence.json'
OUT = ROOT / 'data/generated/corolla_8965H1202000_deadline_monitor_surface.json'
S_FP = ROOT / 'data/function_structural_fingerprints.jsonl'
H_FP = ROOT / 'data/targets/corolla-8965H1202000/function_structural_fingerprints.jsonl'


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def addr(value):
    return f'0x{value:08X}'


def records(path, kind):
    return {int(row['entry_addr'], 16): row for line in path.read_text().splitlines()
            if (row := json.loads(line)).get('record') == kind}


def source(path):
    return {'path': str(path.relative_to(ROOT)), 'sha256': sha(path.read_bytes())}


def table(raw, spec):
    name, base, count, stride, offsets = spec
    rows, values = [], []
    for i in range(count):
        row = [struct.unpack_from('<I', raw, base + i * stride + off)[0] for off in offsets]
        values.extend(value for value in row if value)
        rows.append([addr(value) if value else None for value in row])
    return {'name': name, 'base': addr(base), 'count': count, 'stride': stride,
            'pointer_offsets': list(offsets), 'rows': rows, 'nonzero_slots': len(values),
            'unique_callbacks': len(set(values)), 'callbacks': [addr(x) for x in sorted(set(values))]}


def signature(row):
    return row['mnemonics'], row['instruction_lengths']


def dispatcher(sienna, h, size, s_fps, h_fps):
    s_row, h_row = s_fps[sienna], h_fps[h]
    if s_row['body_size'] != size or h_row['body_size'] != size or signature(s_row) != signature(h_row):
        raise ValueError('deadline dispatcher instruction shape drift')
    s_matches = [entry for entry, row in s_fps.items() if signature(row) == signature(s_row)]
    h_matches = [entry for entry, row in h_fps.items() if signature(row) == signature(s_row)]
    return {'sienna': addr(sienna), 'h': addr(h), 'body_size': size,
            'unique_exact_instruction_shape': len(s_matches) == len(h_matches) == 1}, s_matches, h_matches


def native_registration(raw, target, fps, entry, table_base, dispatcher_entry):
    """Bind the variant-D B table to the active dispatcher, including its gates."""
    corpus_path = target_path(target, 'decompiler_corpus')
    row = records(corpus_path, 'function')[entry]
    if not row.get('decompile_completed') or not row.get('decompiled_c'):
        raise ValueError(f'missing native registration decompilation: {target} {entry:#x}')
    fp = fps[entry]
    pc, instructions = entry, []
    for mnemonic, length in zip(fp['mnemonics'], fp['instruction_lengths']):
        length = int(length)
        instructions.append({'address': addr(pc), 'mnemonic': mnemonic, 'bytes': raw[pc:pc + length].hex()})
        pc += length
    if pc != entry + 302:
        raise ValueError('variant-D B registration body drift')
    load = entry + 0x68
    if raw[load:load + 6] != b'\x3b\x06' + struct.pack('<I', table_base):
        raise ValueError('variant-D B callback-table MOV r27 drift')
    calls = []
    for site in (entry + 0x86, entry + 0xAA, entry + 0xCE):
        w0, w1 = struct.unpack_from('<HH', raw, site)
        high = w0 & 0x3F
        if high & 0x20:
            high -= 0x40
        destination = site + (high << 16) + w1
        if ((w0 >> 6) & 0x1F) != 0x1E or (w0 >> 11) != 31 or (w1 & 1) or destination != dispatcher_entry:
            raise ValueError('variant-D B direct JARL lp drift')
        calls.append({'site': addr(site), 'target': addr(destination), 'bytes': raw[site:site + 4].hex()})
    return {'target': target, 'entry': addr(entry), 'body_size': fp['body_size'],
            'body_sha256': sha(raw[entry:pc]), 'corpus': source(corpus_path),
            'decompiled_c_sha256': sha(row['decompiled_c'].encode()),
            'table_load': {'site': addr(load), 'table': addr(table_base), 'register': 'r27',
                           'bytes': raw[load:load + 6].hex()},
            'direct_calls': calls,
            'gate_instructions': [item for item in instructions if entry + 0x3A <= int(item['address'], 16) < entry + 0x64],
            'data_references': [ref for ref in row['data_references'] if entry + 0x3A <= int(ref['from_addr'], 16) <= entry + 0x80],
            'gate': 'feature byte == 0x5A resets; otherwise flags bit0 must be clear and FEBEEB85 == 0x5A to dispatch; other cases call the non-dispatch fallback',
            'monitor_ids': ['0x43', '0x44', '0x45']}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', type=Path, default=OUT)
    args = parser.parse_args()
    h_path, s_path = target_path(H_TARGET, 'codeflash'), target_path(S_TARGET, 'codeflash')
    h, s = h_path.read_bytes(), s_path.read_bytes()
    ev = json.loads(EV.read_text())
    by = {int(row['entry'], 16): row for row in ev['functions']}
    if sha(h) != ev['image']['codeflash_sha256']:
        raise ValueError('H deadline compact evidence image mismatch')
    s_fps = records(S_FP, 'function-structural-fingerprint')
    h_fps = records(H_FP, 'function-structural-fingerprint')
    st = [table(s, spec) for spec in SIENNA_DEADLINE_TABLES]
    ht = [table(h, spec) for spec in H_DEADLINE_TABLES]
    if [t['unique_callbacks'] for t in st] != [3, 82, 3] or [t['unique_callbacks'] for t in ht] != [3, 82, 3]:
        raise ValueError('deadline callback cardinality drift')
    s_callbacks = sorted({x for t in st for x in t['callbacks']})
    h_callbacks = sorted({x for t in ht for x in t['callbacks']})
    if len(s_callbacks) != 88 or len(h_callbacks) != 88:
        raise ValueError('deadline callback union drift')
    # The reference cohort is the actual configured table union, not whichever
    # entries happen to retain deadline_* names in a changing coverage matrix.
    recensus = [{'reference_entry': x, 'reference_name': s_fps[int(x, 16)]['name'],
                 'classification': 'target-surface-recensused',
                 'recensus': 'complete H three-table deadline-monitor callback surface'} for x in s_callbacks]
    simple, _, _ = dispatcher(0x6962A, 0x639CA, 138, s_fps, h_fps)
    setup, _, _ = dispatcher(0x3DC88, 0x387E4, 346, s_fps, h_fps)
    setup['h_table'] = '0x000280E8'
    variant, s_matches, h_matches = dispatcher(0x6A28A, 0x6462A, 1208, s_fps, h_fps)
    body = s[0x6A28A:0x6A28A + 1208]
    if h[0x6462A:0x6462A + 1208] != body or sha(body) != by[0x6462A]['body_sha256']:
        raise ValueError('variant-D native body mismatch')
    variant.update({'method': 'exact-body-and-native-callback-dispatch', 'body_sha256': sha(body),
                    'sienna_shape_candidates': [addr(x) for x in s_matches],
                    'h_shape_candidates': [addr(x) for x in h_matches],
                    'sienna_exact_body_occurrences': [addr(i) for i in range(len(s)) if s.startswith(body, i)],
                    'h_exact_body_occurrences': [addr(i) for i in range(len(h)) if h.startswith(body, i)]})
    registration = [native_registration(s, S_TARGET, s_fps, 0x417EE, 0x286D0, 0x6A28A),
                    native_registration(h, H_TARGET, h_fps, 0x3C34A, 0x28260, 0x6462A)]
    payload = {
        'schema': 'corolla-h-deadline-monitor-surface-v1', 'software_id': '8965H1202000',
        'images': {'h_sha256': sha(h), 'sienna_sha256': sha(s)},
        'evidence': {'decompiler_evidence': str(EV.relative_to(ROOT)),
                     'sienna_codeflash': source(s_path), 'h_codeflash': source(h_path),
                     'sienna_fingerprints': source(S_FP), 'h_fingerprints': source(H_FP)},
        'dispatchers': {'simple': simple, 'variant_d': variant, 'simple_setup': setup},
        'native_variant_d_registration': registration,
        'role_closure': [{'reference_entry': '0x0006A28A', 'reference_name': 'com_signal_deadline_monitor_d',
                          'target_entry': '0x0006462A', 'method': variant['method'],
                          'proof': '1208-byte exact body; active variant-D B registrations S417EE/H3C34A load tables 286D0/28260 and call 6A28A/6462A three times under equivalent gates'}],
        'sienna_tables': st, 'h_tables': ht, 'surface_recensus': recensus,
        'surface_recensus_count': len(recensus),
        'surface_recensus_basis': 'raw Sienna three-table callback union',
        'summary': {'sienna_unique_callback_union': len(s_callbacks), 'h_unique_callback_union': len(h_callbacks),
                    'same_table_shapes': [(t['count'], t['stride'], len(t['pointer_offsets'])) for t in st] == [(t['count'], t['stride'], len(t['pointer_offsets'])) for t in ht],
                    'same_per_table_unique_counts': [t['unique_callbacks'] for t in st] == [t['unique_callbacks'] for t in ht],
                    'reference_callback_named_count': sum(row['reference_name'].startswith('deadline_') for row in recensus),
                    'all_reference_table_callbacks_recensused': len(recensus) == len(s_callbacks)},
    }
    for callback in h_callbacks:
        if int(callback, 16) not in by:
            raise ValueError(f'H callback lacks compact evidence: {callback}')
    args.out.write_text(json.dumps(payload, indent=2, sort_keys=True) + '\n')
    print('wrote', args.out)


if __name__ == '__main__':
    main()
