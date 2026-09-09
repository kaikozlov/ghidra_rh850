#!/usr/bin/env python3
"""Reconcile retained Camry B6 road traffic with the exact-F33 command gate ladder.

The raw rlogs are maintainer-local.  This reducer emits a compact portable artifact
that separates what the road capture can prove from EPS-internal state that still
requires the RAM monitor.  Panda TX echoes are never treated as F33 reception.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import statistics
import sys
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[4]
DEFAULT_LOG_ROOT = Path('/Users/kai/dev/inspect/logs/camry-2026')
DEFAULT_OPENPILOT = Path('/Users/kai/dev/inspect/repos/kai-openpilot')
DEFAULT_OUT = ROOT / 'data/generated/camry_f33_b6_gate_log_reconciliation.json'
FRESHNESS_ART = ROOT / 'data/generated/camry_b6_freshness_contract.json'
EXTERNAL_INGRESS_ART = ROOT / 'data/generated/camry_8965F3307000_external_lateral_ingress.json'
F33_PORT_ART = ROOT / 'data/generated/camry_8965F3307000_tss3_opendbc_port.json'
F33_CORPUS = ROOT / 'data/generated/camry-8965F3307000/decompilations.jsonl'


def sha256(path: Path) -> str:
  h = hashlib.sha256()
  with path.open('rb') as f:
    for chunk in iter(lambda: f.read(1 << 20), b''):
      h.update(chunk)
  return h.hexdigest()


def load_logreader(openpilot_root: Path):
  sys.path.insert(0, str(openpilot_root))
  from openpilot.tools.lib.logreader import LogReader  # type: ignore[import-not-found]
  return LogReader


def discover_route_files(log_root: Path, route_name: str) -> list[tuple[int, Path]]:
  candidates = list(log_root.rglob(route_name))
  route_dirs = [p for p in candidates if p.is_dir() and p.name == route_name]
  if len(route_dirs) != 1:
    raise RuntimeError(f'expected one route directory for {route_name}, got {route_dirs}')
  route = route_dirs[0]
  rows: dict[int, Path] = {}
  for p in route.glob('*/rlog.zst'):
    try: rows[int(p.parent.name.rsplit('--', 1)[1])] = p
    except (IndexError, ValueError): pass
  for p in route.glob('rlog-*.zst'):
    try: rows[int(p.name[5:-4])] = p
    except ValueError: pass
  for p in route.glob('*.rlog.zst'):
    try: rows[int(p.name.removesuffix('.rlog.zst').rsplit('--', 1)[1])] = p
    except (IndexError, ValueError): pass
  if not rows:
    raise RuntimeError(f'no rlogs for {route}')
  return sorted(rows.items())


def b6_app_tuple(dat: bytes) -> tuple[int, ...]:
  return (
    dat[3] & 0x3F,
    (dat[6] >> 7) & 1,
    (dat[6] >> 4) & 7,
    (dat[6] >> 2) & 1,
    dat[6] & 3,
    (dat[7] >> 6) & 3,
    dat[8], dat[9],
    (dat[10] >> 7) & 1,
    (dat[10] >> 5) & 1,
    dat[10] & 7,
  )


def counter_json(c: Counter[Any]) -> dict[str, int]:
  def key(k: Any) -> str:
    if isinstance(k, tuple): return ','.join(str(x) for x in k)
    return str(k)
  return {key(k): v for k, v in sorted(c.items(), key=lambda kv: str(kv[0]))}


def scan_route(LogReader, route_name: str, files: list[tuple[int, Path]]) -> dict[str, Any]:
  patterns: Counter[tuple[int, ...]] = Counter()
  ids: Counter[int] = Counter()
  seq_deltas: Counter[int] = Counter()
  accd_active: Counter[int] = Counter()
  adbf_active: Counter[int] = Counter()
  cafc_active: Counter[int] = Counter()
  cad9_active: Counter[int] = Counter()
  d7_all: Counter[int] = Counter()
  adbf_all: Counter[int] = Counter()
  cafc_all: Counter[int] = Counter()
  cad9_all: Counter[int] = Counter()
  d7_src: Counter[int] = Counter()
  m30_src: Counter[int] = Counter()
  diag_payloads: Counter[str] = Counter()
  diag_services: Counter[int] = Counter()
  b6_send = 0
  active = 0
  inactive = 0
  zero_mac = 0
  nonzero_mac = 0
  b6_gaps_ms: list[float] = []
  d7_gaps_ms: list[float] = []
  m30_gaps_ms: list[float] = []
  active_accd_ages_ms: list[float] = []
  active_adbf_ages_ms: list[float] = []
  active_cafc_ages_ms: list[float] = []
  active_cad9_ages_ms: list[float] = []
  active_angles_raw_abs: list[int] = []
  last_b6_t: int | None = None
  last_d7_t: int | None = None
  last_30_t: int | None = None
  last_d7: tuple[int, int] | None = None
  last_adbf: tuple[int, int] | None = None
  last_cafc: tuple[int, int] | None = None
  last_cad9: tuple[int, int] | None = None
  last_seq: int | None = None
  init: dict[str, Any] = {}

  for _seg, p in files:
    for e in LogReader(str(p), sort_by_time=True, only_union_types=True):
      t = int(e.logMonoTime)
      which = e.which()
      if which == 'initData' and not init:
        x = e.initData
        init = {'gitCommit': str(x.gitCommit), 'gitBranch': str(x.gitBranch), 'dirty': bool(x.dirty), 'version': str(x.version)}
      elif which == 'can':
        for m in e.can:
          src, a, d = int(m.src), int(m.address), bytes(m.dat)
          if a == 0x0D7:
            d7_src[src] += 1
            if src == 0 and len(d) >= 1:
              v = (d[0] >> 7) & 1
              d7_all[v] += 1
              if last_d7_t is not None: d7_gaps_ms.append((t - last_d7_t) / 1e6)
              last_d7_t = t
              last_d7 = (t, v)
          elif a == 0x030:
            m30_src[src] += 1
            if src == 0 and len(d) >= 20:
              adbf = d[13] & 0x3
              cafc = d[16] & 0x1
              cad9 = d[19] & 0x1
              adbf_all[adbf] += 1
              cafc_all[cafc] += 1
              cad9_all[cad9] += 1
              if last_30_t is not None: m30_gaps_ms.append((t - last_30_t) / 1e6)
              last_30_t = t
              last_adbf = (t, adbf)
              last_cafc = (t, cafc)
              last_cad9 = (t, cad9)
      elif which == 'sendcan':
        for m in e.sendcan:
          a, d = int(m.address), bytes(m.dat)
          if a == 0x7A1 and d:
            diag_payloads[d.hex()] += 1
            sf_len = d[0] & 0xF if (d[0] >> 4) == 0 else 0
            if sf_len >= 1 and len(d) > 1: diag_services[d[1]] += 1
          if a != 0x0B6 or len(d) != 32:
            continue
          b6_send += 1
          if last_b6_t is not None: b6_gaps_ms.append((t - last_b6_t) / 1e6)
          last_b6_t = t
          zero_mac += int((d[28] & 0x0F) == 0 and d[29:32] == b'\0\0\0')
          nonzero_mac += int(not ((d[28] & 0x0F) == 0 and d[29:32] == b'\0\0\0'))
          pat = b6_app_tuple(d)
          patterns[pat] += 1
          tid = pat[0]
          ids[tid] += 1
          seq = d[7] & 0x3F
          if last_seq is not None: seq_deltas[(seq - last_seq) & 0x3F] += 1
          last_seq = seq
          if tid == 11:
            active += 1
            active_angles_raw_abs.append(abs(int.from_bytes(d[4:6], 'big', signed=True)))
            if last_d7 is not None:
              age = (t - last_d7[0]) / 1e6
              if 0 <= age <= 25:
                accd_active[last_d7[1]] += 1
                active_accd_ages_ms.append(age)
            if last_adbf is not None:
              age = (t - last_adbf[0]) / 1e6
              if 0 <= age <= 25:
                adbf_active[last_adbf[1]] += 1
                active_adbf_ages_ms.append(age)
            if last_cafc is not None:
              age = (t - last_cafc[0]) / 1e6
              if 0 <= age <= 25:
                cafc_active[last_cafc[1]] += 1
                active_cafc_ages_ms.append(age)
            if last_cad9 is not None:
              age = (t - last_cad9[0]) / 1e6
              if 0 <= age <= 25:
                cad9_active[last_cad9[1]] += 1
                active_cad9_ages_ms.append(age)
          elif tid == 0:
            inactive += 1

  def gap_stats(xs: list[float]) -> dict[str, Any]:
    return {
      'count': len(xs),
      'min_ms': round(min(xs), 6) if xs else None,
      'median_ms': round(statistics.median(xs), 6) if xs else None,
      'max_ms': round(max(xs), 6) if xs else None,
      'gt_35ms': sum(x > 35.0 for x in xs),
    }
  def age_stats(xs: list[float]) -> dict[str, Any]:
    return {'joined': len(xs), 'median_ms': round(statistics.median(xs), 6) if xs else None, 'max_ms': round(max(xs), 6) if xs else None}

  expected_active = (11, 0, 0, 0, 0, 0, 100, 100, 0, 0, 0)
  expected_inactive = (0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0)
  active_expected = patterns[expected_active]
  inactive_expected = patterns[expected_inactive]
  non_tester_diag = sum(v for k, v in diag_services.items() if k != 0x3E)
  return {
    'route_name': route_name,
    'segment_count': len(files),
    'init': init,
    'b6': {
      'send_frames': b6_send,
      'target_id_counts': counter_json(ids),
      'active_id11': active,
      'inactive_id0': inactive,
      'zero_mac28': zero_mac,
      'nonzero_mac28': nonzero_mac,
      'application_pattern_counts': counter_json(patterns),
      'expected_active_pattern': ','.join(str(x) for x in expected_active),
      'expected_active_pattern_count': active_expected,
      'unexpected_active_pattern_count': active - active_expected,
      'expected_inactive_pattern': ','.join(str(x) for x in expected_inactive),
      'expected_inactive_pattern_count': inactive_expected,
      'unexpected_inactive_pattern_count': inactive - inactive_expected,
      'sequence_delta_mod64': counter_json(seq_deltas),
      'cadence': gap_stats(b6_gaps_ms),
      'max_abs_target_raw_active': max(active_angles_raw_abs) if active_angles_raw_abs else None,
    },
    'road_gate_observables': {
      'ACCD': {
        'static_source': '0x0D7 B0[7] / signal243 -> FEBE80A0 -> FEBEF094 -> FEBEACCD',
        'native_src0_all_values': counter_json(d7_all),
        'active_b6_latest_within_25ms': counter_json(accd_active),
        'join_age': age_stats(active_accd_ages_ms),
        'native_src_counts': counter_json(d7_src),
        'native_src0_cadence': gap_stats(d7_gaps_ms),
        'passing_condition': 'ACCD == 0',
      },
      'ADBF': {
        'static_source': 'FEBE817C -> FEBEF145 -> FEBEADBF; exact F33 0x030 packer signal19 = B13[1:0]',
        'native_src0_all_values': counter_json(adbf_all),
        'active_b6_latest_within_25ms': counter_json(adbf_active),
        'join_age': age_stats(active_adbf_ages_ms),
        'native_src_counts': counter_json(m30_src),
        'native_src0_cadence': gap_stats(m30_gaps_ms),
        'passing_condition': 'ADBF < 2',
      },
      'ACCC': {
        'direct_road_proxy': False,
        'static_source': 'FEBE80A5 = FUN_000498E0(0x17) generated status -> FEBEF093 -> FEBEACCC; not a directly encoded CAN scalar',
        'road_bound': 'continuous 0x0D7 proves source-PDU wire liveness but not the internal generated status byte itself',
      },
      'CAFC': {
        'static_source': 'CAFC -> AD42 -> E834 -> 80EC; exact F33 0x030 packer signal25 = B16[0]',
        'native_src0_all_values': counter_json(cafc_all),
        'active_b6_latest_within_25ms': counter_json(cafc_active),
        'join_age': age_stats(active_cafc_ages_ms),
        'native_src0_cadence': gap_stats(m30_gaps_ms),
        'passing_condition': 'CAFC == 0',
      },
      'CAD9': {
        'static_source': 'CAD9 -> AD4B -> E83A -> 80E0; exact F33 0x030 packer signal31 = B19[0]',
        'native_src0_all_values': counter_json(cad9_all),
        'active_b6_latest_within_25ms': counter_json(cad9_active),
        'join_age': age_stats(active_cad9_ages_ms),
        'native_src0_cadence': gap_stats(m30_gaps_ms),
        'passing_condition': 'CAD9 == 0',
      },
    },
    'diagnostic_requests': {
      'sendcan_0x7A1_payload_counts': counter_json(diag_payloads),
      'single_frame_service_counts': {f'0x{k:02X}': v for k, v in sorted(diag_services.items())},
      'non_tester_present_single_frame_requests': non_tester_diag,
    },
  }


def static_proof() -> dict[str, Any]:
  ingress = json.loads(EXTERNAL_INGRESS_ART.read_text())
  chain = next(x for x in ingress['scalar_command_cone_census']['chains'] if x.get('signal') == 243)
  if not (chain['can_id'] == '0x0D7' and chain['byte_offset'] == 0 and chain['bit_offset'] == 7 and chain['snapshot'] == '0xFEBEACCD'):
    raise RuntimeError(f'ACCD chain drift: {chain}')

  # The exact-F33 pdu0 packer is independently recovered in the canonical port artifact.
  port = json.loads(F33_PORT_ART.read_text())
  if port['generated_com_tx']['pdu_descriptors']['0'][3] != 32:
    raise RuntimeError('0x030 PDU geometry drift')

  wanted = {0xD0D7C, 0xBF3AA, 0x4C2DC, 0x4C97A}
  funcs: dict[int, str] = {}
  with F33_CORPUS.open(encoding='utf-8') as fh:
    for line in fh:
      rec = json.loads(line)
      if rec.get('record') != 'function':
        continue
      entry = int(rec['entry_addr'], 16)
      if entry in wanted:
        funcs[entry] = rec['decompiled_c']
  if set(funcs) != wanted:
    raise RuntimeError(f'exact-F33 mirror function drift: {sorted(set(wanted) - set(funcs))}')
  cafc_tokens = {
    0xD0D7C: 'DAT_febead42 = DAT_febecafc',
    0xBF3AA: 'DAT_febee834 = DAT_febead42',
    0x4C2DC: 'DAT_febe80ec = DAT_febee834',
    0x4C97A: 'FUN_0007d31e(0x19,0x10,1,0,puVar3 + -0x2bbd)',
  }
  cad9_tokens = {
    0xD0D7C: 'DAT_febead4b = DAT_febecad9',
    0xBF3AA: 'DAT_febee83a = DAT_febead4b',
    0x4C2DC: 'DAT_febe80e0 = DAT_febee83a',
    0x4C97A: 'FUN_0007d31e(0x1f,0x13,1,0,puVar3 + -0x2bb9)',
  }
  for addr, token in cafc_tokens.items():
    if token not in funcs[addr]:
      raise RuntimeError(f'CAFC mirror drift at {addr:#x}: {token}')
  for addr, token in cad9_tokens.items():
    if token not in funcs[addr]:
      raise RuntimeError(f'CAD9 mirror drift at {addr:#x}: {token}')
  return {
    'ACCD': chain,
    'ADBF': {
      'snapshot': '0xFEBEADBF', 'stage': '0xFEBEF145', 'raw': '0xFEBE817C',
      'wire': '0x030 B13[1:0]', 'packer': '0x0004C97A', 'packer_signal': 19,
      'proof': '4C97A stages FEBE817C at FEBE8C3E then FUN_0007D31E(0x13,0x0D,2,0,&FEBE8C3E)',
    },
    'CAFC': {
      'chain': ['0x000D0D7C CAFC->AD42', '0x000BF3AA AD42->E834', '0x0004C2DC E834->80EC', '0x0004C97A signal25'],
      'wire': '0x030 B16[0]', 'packer_signal': 25,
    },
    'CAD9': {
      'chain': ['0x000D0D7C CAD9->AD4B', '0x000BF3AA AD4B->E83A', '0x0004C2DC E83A->80E0', '0x0004C97A signal31'],
      'wire': '0x030 B19[0]', 'packer_signal': 31,
    },
    'readiness_predicate': {
      'assert': 'CE772 promotes when ACCC==0 && ACCD==0 && ADBF<2 && CAFC==0 && CAD9==0',
      'withdraw': 'CE7A6 withdraws for ACCC!=0, debounced ACCD!=0, ADBF in {2,3}, CAFC==1, or CAD9==1',
    },
    'sig263_correction': {
      'signal': 263,
      'snapshot': '0xFEBEADDD',
      'sole_runtime_reader': '0x000CB664',
      'CB664_output': 'FEBEC7B4',
      'C7B4_only_runtime_consumer': '0x000CB73A',
      'CB73A_arm_id': '0x31',
      'normal_id11': '0x0B',
      'conclusion': 'sig263=0 and CB664 speed qualification belong to the special 0x31 transient, not normal ID11 bank2 admission',
    },
  }


def main() -> int:
  ap = argparse.ArgumentParser()
  ap.add_argument('--log-root', type=Path, default=DEFAULT_LOG_ROOT)
  ap.add_argument('--openpilot-root', type=Path, default=DEFAULT_OPENPILOT)
  ap.add_argument('--out', type=Path, default=DEFAULT_OUT)
  args = ap.parse_args()

  freshness = json.loads(FRESHNESS_ART.read_text())
  route_names = [r['route_name'] for r in freshness['routes']]
  LogReader = load_logreader(args.openpilot_root)
  routes = []
  for name in route_names:
    print(f'[scan] {name}', file=sys.stderr, flush=True)
    routes.append(scan_route(LogReader, name, discover_route_files(args.log_root, name)))

  recent_names = {
    '00000037--dec6fe39cb', '0000003e--1a2f20417d', '0000003f--36e72f5fdc',
    '00000045--805b7ca6ab', '00000048--709f22277b',
  }
  recent = [r for r in routes if r['route_name'] in recent_names]
  # Current-shape cohort is derived from the bytes rather than a date cut: every
  # active ID11 frame in the route must match the current application template.
  current_shape = [r for r in routes if r['b6']['active_id11'] > 0 and r['b6']['unexpected_active_pattern_count'] == 0]
  active_recent = sum(r['b6']['active_id11'] for r in recent)
  active_current_shape = sum(r['b6']['active_id11'] for r in current_shape)
  accd_recent = Counter()
  adbf_recent = Counter()
  cafc_recent = Counter()
  cad9_recent = Counter()
  for r in recent:
    accd_recent.update({int(k): v for k, v in r['road_gate_observables']['ACCD']['active_b6_latest_within_25ms'].items()})
    adbf_recent.update({int(k): v for k, v in r['road_gate_observables']['ADBF']['active_b6_latest_within_25ms'].items()})
    cafc_recent.update({int(k): v for k, v in r['road_gate_observables']['CAFC']['active_b6_latest_within_25ms'].items()})
    cad9_recent.update({int(k): v for k, v in r['road_gate_observables']['CAD9']['active_b6_latest_within_25ms'].items()})

  current_shape_gate_counts = {name: Counter() for name in ('ACCD', 'ADBF', 'CAFC', 'CAD9')}
  for r in current_shape:
    for name, counter in current_shape_gate_counts.items():
      counter.update({int(k): v for k, v in r['road_gate_observables'][name]['active_b6_latest_within_25ms'].items()})

  all_active = sum(r['b6']['active_id11'] for r in routes)
  all_expected_active = sum(r['b6']['expected_active_pattern_count'] for r in routes)
  all_gaps_gt35 = sum(r['b6']['cadence']['gt_35ms'] for r in routes)
  out = {
    'schema': 'camry-f33-b6-gate-log-reconciliation-v1',
    'sources': {
      'freshness_artifact': str(FRESHNESS_ART.relative_to(ROOT)),
      'freshness_artifact_sha256': sha256(FRESHNESS_ART),
      'external_ingress_artifact': str(EXTERNAL_INGRESS_ART.relative_to(ROOT)),
      'external_ingress_artifact_sha256': sha256(EXTERNAL_INGRESS_ART),
      'f33_port_artifact': str(F33_PORT_ART.relative_to(ROOT)),
      'f33_port_artifact_sha256': sha256(F33_PORT_ART),
      'exact_f33_corpus': str(F33_CORPUS.relative_to(ROOT)),
      'exact_f33_corpus_sha256': sha256(F33_CORPUS),
      'retained_routes': len(route_names),
      'retained_rlogs': sum(len(r['inventory']) for r in freshness['routes']),
      'retained_rlog_bytes': sum(r['total_rlog_bytes'] for r in freshness['routes']),
    },
    'static_gate_proof': static_proof(),
    'routes': routes,
    'aggregate': {
      'b6_send_frames': sum(r['b6']['send_frames'] for r in routes),
      'active_id11_frames': all_active,
      'active_id11_expected_application_shape': all_expected_active,
      'active_id11_unexpected_application_shape': all_active - all_expected_active,
      'zero_mac28_frames': sum(r['b6']['zero_mac28'] for r in routes),
      'nonzero_mac28_frames': sum(r['b6']['nonzero_mac28'] for r in routes),
      'b6_cadence_gt35ms_within_retained_sequence': all_gaps_gt35,
      'recent_route_names': sorted(recent_names),
      'recent_active_id11_frames': active_recent,
      'current_shape_route_names': sorted(r['route_name'] for r in current_shape),
      'current_shape_active_id11_frames': active_current_shape,
      'current_shape_active_gate_values_within_25ms': {name: counter_json(counter) for name, counter in current_shape_gate_counts.items()},
      'recent_active_ACCD_latest_within_25ms': counter_json(accd_recent),
      'recent_active_ADBF_latest_within_25ms': counter_json(adbf_recent),
      'recent_active_CAFC_latest_within_25ms': counter_json(cafc_recent),
      'recent_active_CAD9_latest_within_25ms': counter_json(cad9_recent),
    },
    'conclusions': {
      'current_application_shape_is_supported_by_recent_road_logs': all(r['b6']['unexpected_active_pattern_count'] == 0 for r in recent),
      'historical_corpus_active_shape_is_uniform': all_active == all_expected_active,
      'recent_B6_cadence_crosses_35ms_loss_threshold': any(r['b6']['cadence']['gt_35ms'] for r in recent),
      'recent_ACCD_observable_satisfies_zero_when_joined': set(accd_recent) <= {0} and bool(accd_recent),
      'recent_ADBF_observable_satisfies_lt2_when_joined': all(k < 2 for k in adbf_recent) and bool(adbf_recent),
      'ACCC_is_directly_proven_from_road_CAN': False,
      'recent_CAFC_observable_satisfies_zero_when_joined': set(cafc_recent) <= {0} and bool(cafc_recent),
      'recent_CAD9_observable_satisfies_zero_when_joined': set(cad9_recent) <= {0} and bool(cad9_recent),
      'road_logs_prove_F33_internal_B6_admission': False,
      'highest_value_next_witness': 'queue -> route44 -> generated COM -> ADB0/CAFF/CB00 before downstream controller/output monitoring',
      'sig263_or_CB664_speed_is_normal_ID11_gate': False,
    },
  }
  args.out.parent.mkdir(parents=True, exist_ok=True)
  args.out.write_text(json.dumps(out, indent=2, sort_keys=True) + '\n')
  print(json.dumps(out['aggregate'], indent=2, sort_keys=True))
  return 0


if __name__ == '__main__':
  raise SystemExit(main())
