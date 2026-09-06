#!/usr/bin/env python3
"""Census every road-observed Camry TSS3 Target-Lateral-ID steering-family request.

The report keeps the three relevant planes separate:
  * native FRC-side 0x08A request/reference publications;
  * native chassis-side 0x081 returned/reference identity (B13 low 6); and
  * exact-F33 external ingress 0x0B6, distinguishing native receive traffic from
    openpilot sendcan and Panda TX/reject echoes.

It also records exact-F33 selector/gating structure from the canonical complete
CodeFlash decompilation corpus. Raw road logs stay outside the git repository.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import tempfile
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
DEFAULT_OPENPILOT = Path('/Users/kai/dev/inspect/repos/kai-openpilot')
DEFAULT_LOG_ROOT = Path('/Users/kai/dev/inspect/logs/camry-2026')
DEFAULT_CAP_ROOT = Path('/Users/kai/dev/inspect/captures')
DEFAULT_OUT = REPO / 'data/generated/camry_2026_lateral_family_census.json'

ROUTES = {
  '1c': ('archive', '0000001c--574c06b528'),
  '27': ('archive', '00000027--885099a1d4'),
  '29': ('archive', '00000029--bae47e927f'),
  '2a': ('archive', '0000002a--c5647fd694'),
  '2c': ('archive', '0000002c--c784367b7e'),
  '2d': ('capture', '0000002d--4a4806c524'),
  '37': ('dated', '2026-09-01', '00000037--dec6fe39cb'),
  '3b': ('dated', '2026-09-04', '0000003b--62262eb7a1'),
  '3c': ('dated', '2026-09-04', '0000003c--97b9e7a69a'),
  '3d': ('dated', '2026-09-04', '0000003d--0e812cecba'),
  '3e': ('dated', '2026-09-06', '0000003e--1a2f20417d'),
  '3f': ('dated', '2026-09-06', '0000003f--36e72f5fdc'),
}

LABELS = {
  0: 'No Request (Manual Operation)', 1: 'PCS', 4: 'LDA', 10: 'Hands Off LTA',
  11: 'LTA/LCA', 13: 'DESA (Slow Deceleration Control)',
  15: 'DESA (Deceleration Stop Control)', 18: 'SDG', 19: 'PDA', 25: 'AP',
  27: 'Remote Parking', 35: 'AD (Lv.3)', 37: 'EM (Lv.3)', 39: 'DES (Lv.3)',
  41: 'AD (Lv.4)', 43: 'EM (Lv.4)', 45: 'DES (Lv.4)',
  49: 'Self-Propelled Transport', 63: 'Driver Operation',
}
F33_ACCEPTED = {1, 4, 10, 11, 18, 19}


def load_logreader(root: Path):
  sys.path.insert(0, str(root))
  from openpilot.tools.lib.logreader import LogReader  # type: ignore[import-not-found]
  return LogReader


def segnum(path: Path) -> int:
  s = str(path)
  m = re.search(r'--(\d+)(?:/rlog|\.rlog|$)', s)
  if m:
    return int(m.group(1))
  m = re.search(r'rlog-(\d+)', path.name)
  return int(m.group(1)) if m else 0


def discover(route: tuple[str, ...], log_root: Path, cap_root: Path) -> tuple[Path, list[Path]]:
  kind = route[0]
  if kind == 'archive':
    route_dir = log_root / 'archive' / route[1]
  elif kind == 'capture':
    route_dir = cap_root / route[1]
  else:
    route_dir = log_root / route[1] / route[2]
  pats = ['rlog-*.zst', '*.rlog.zst', '*/rlog.zst']
  files: set[Path] = set()
  for pat in pats:
    files.update(route_dir.glob(pat))
  return route_dir, sorted(files, key=segnum)


def s16be(b: bytes) -> int:
  return int.from_bytes(b, 'big', signed=True)


def new_episode(lid: int, t: float, dat: bytes) -> dict:
  raw = s16be(dat[18:20])
  return {
    'target_lateral_id': lid,
    'label': LABELS.get(lid, f'Unknown {lid}'),
    'start_s': t,
    'end_s': t,
    'frames': 0,
    'target_angle_raw_min': raw,
    'target_angle_raw_max': raw,
    'request_level_counts': Counter(),
    'cruise_latch_counts': Counter(),
    'b23_counts': Counter(),
  }


def close_episode(ep: dict | None, base_t: float | None, out: list[dict]) -> None:
  if ep is None or base_t is None:
    return
  ep['duration_s'] = round(ep['end_s'] - ep['start_s'], 6)
  ep['start_s'] = round(ep['start_s'] - base_t, 6)
  ep['end_s'] = round(ep['end_s'] - base_t, 6)
  ep['request_level_counts'] = {str(k): v for k, v in sorted(ep['request_level_counts'].items())}
  ep['cruise_latch_counts'] = {str(k): v for k, v in sorted(ep['cruise_latch_counts'].items())}
  ep['b23_counts'] = {f'0x{k:02X}': v for k, v in sorted(ep['b23_counts'].items())}
  out.append(ep)


def scan_route(LogReader, files: list[Path]) -> dict:
  id_counts: Counter[int] = Counter()
  id_level: dict[int, Counter[int]] = {}
  id_cruise: dict[int, Counter[int]] = {}
  id_b23: dict[int, Counter[int]] = {}
  id_angle_min: dict[int, int] = {}
  id_angle_max: dict[int, int] = {}
  transitions: Counter[tuple[int, int]] = Counter()
  ref81_counts: Counter[int] = Counter()
  ref81_pairs = Counter()
  b6_can_src: Counter[int] = Counter()
  b6_src012_raw_ids: Counter[int] = Counter()
  b6_same_event_echo_duplicate_ids: Counter[int] = Counter()
  b6_unmatched_native_candidate_ids: Counter[int] = Counter()
  b6_echo_ids: Counter[int] = Counter()
  b6_send_ids: Counter[int] = Counter()
  episodes: list[dict] = []
  cur_ep = None
  prior_id = None
  first_08a_id = None
  latest_08a: tuple[float, int] | None = None
  first_t = last_t = None

  for path in files:
    for evt in LogReader(str(path), sort_by_time=True):
      t = evt.logMonoTime / 1e9
      if first_t is None:
        first_t = t
      last_t = t
      which = evt.which()
      if which not in {'can', 'sendcan'}:
        continue
      frames = getattr(evt, which)
      # A historical pre-repin route records our own B6 transmission twice in
      # the same CAN event: once as the Panda TX echo (src128) and once as an
      # exact relay-side src2 copy.  Pre-collect echo payload multiplicity so a
      # raw src0/1/2 observation is not mislabeled stock/native merely because
      # its source number is below 128.
      event_b6_echo_remaining = Counter(
        bytes(f.dat) for f in frames
        if which == 'can' and int(f.address) == 0x0B6 and 128 <= int(f.src) < 192
      )
      for f in frames:
        addr, src, dat = int(f.address), int(f.src), bytes(f.dat)
        if which == 'sendcan' and addr == 0x0B6 and len(dat) >= 4:
          b6_send_ids[dat[3] & 0x3f] += 1
          continue
        if which != 'can':
          continue
        if addr == 0x0B6 and len(dat) >= 4:
          b6_can_src[src] += 1
          lid = dat[3] & 0x3f
          if src in (0, 1, 2):
            b6_src012_raw_ids[lid] += 1
            if event_b6_echo_remaining[dat] > 0:
              event_b6_echo_remaining[dat] -= 1
              b6_same_event_echo_duplicate_ids[lid] += 1
            else:
              b6_unmatched_native_candidate_ids[lid] += 1
          elif 128 <= src < 192:
            b6_echo_ids[lid] += 1
          continue
        if src == 2 and addr == 0x08A and len(dat) >= 25:
          lid = dat[21] & 0x3f
          raw = s16be(dat[18:20])
          id_counts[lid] += 1
          if first_08a_id is None:
            first_08a_id = lid
          id_level.setdefault(lid, Counter())[dat[24]] += 1
          id_cruise.setdefault(lid, Counter())[1 if dat[3] & 0x08 else 0] += 1
          id_b23.setdefault(lid, Counter())[dat[23]] += 1
          id_angle_min[lid] = min(raw, id_angle_min.get(lid, raw))
          id_angle_max[lid] = max(raw, id_angle_max.get(lid, raw))
          latest_08a = (t, lid)
          if prior_id is not None and lid != prior_id:
            transitions[(prior_id, lid)] += 1
          if lid != prior_id:
            close_episode(cur_ep, first_t, episodes)
            cur_ep = None if lid == 0 else new_episode(lid, t, dat)
          if cur_ep is not None:
            cur_ep['end_s'] = t
            cur_ep['frames'] += 1
            cur_ep['target_angle_raw_min'] = min(cur_ep['target_angle_raw_min'], raw)
            cur_ep['target_angle_raw_max'] = max(cur_ep['target_angle_raw_max'], raw)
            cur_ep['request_level_counts'][dat[24]] += 1
            cur_ep['cruise_latch_counts'][1 if dat[3] & 0x08 else 0] += 1
            cur_ep['b23_counts'][dat[23]] += 1
          prior_id = lid
        elif src == 0 and addr == 0x081 and len(dat) >= 14:
          lid81 = dat[13] & 0x3f
          ref81_counts[lid81] += 1
          if latest_08a is not None and 0 <= t - latest_08a[0] <= 0.1:
            ref81_pairs['eligible'] += 1
            if lid81 == latest_08a[1]:
              ref81_pairs['match'] += 1
            else:
              ref81_pairs[f'{latest_08a[1]}->{lid81}'] += 1

  close_episode(cur_ep, first_t, episodes)
  per_id = {}
  for lid in sorted(id_counts):
    per_id[str(lid)] = {
      'label': LABELS.get(lid, f'Unknown {lid}'),
      'frames': id_counts[lid],
      'target_angle_raw_range': [id_angle_min[lid], id_angle_max[lid]],
      'target_angle_deg_equiv_range': [round(id_angle_min[lid] * 1024 / 17870, 6), round(id_angle_max[lid] * 1024 / 17870, 6)],
      'request_level_counts': {str(k): v for k, v in sorted(id_level[lid].items())},
      'cruise_latch_counts': {str(k): v for k, v in sorted(id_cruise[lid].items())},
      'b23_counts': {f'0x{k:02X}': v for k, v in sorted(id_b23[lid].items())},
    }
  return {
    'segment_count': len(files),
    'first_mono_s': first_t,
    'last_mono_s': last_t,
    'first_08a_id': first_08a_id,
    'last_08a_id': prior_id,
    'duration_s': round((last_t - first_t), 6) if first_t is not None and last_t is not None else 0,
    'native_08a_frames': sum(id_counts.values()),
    'target_lateral_ids': per_id,
    'nonzero_episode_count': len(episodes),
    'nonzero_episodes': episodes,
    'id_transition_counts': {f'{a}->{b}': n for (a, b), n in sorted(transitions.items())},
    'native_081_id_counts': {str(k): v for k, v in sorted(ref81_counts.items())},
    'native_081_latest_08a_pairing': dict(ref81_pairs),
    'b6': {
      'can_src_counts': {str(k): v for k, v in sorted(b6_can_src.items())},
      'src_0_1_2_id_counts_raw': {str(k): v for k, v in sorted(b6_src012_raw_ids.items())},
      'same_event_tx_echo_duplicate_id_counts': {str(k): v for k, v in sorted(b6_same_event_echo_duplicate_ids.items())},
      'unmatched_native_candidate_id_counts': {str(k): v for k, v in sorted(b6_unmatched_native_candidate_ids.items())},
      'panda_tx_echo_id_counts': {str(k): v for k, v in sorted(b6_echo_ids.items())},
      'sendcan_id_counts': {str(k): v for k, v in sorted(b6_send_ids.items())},
    },
  }



def scan_route_worker(args: tuple[str, tuple[str, ...], str, str, str]) -> tuple[str, dict]:
  short, spec, openpilot_root_s, log_root_s, cap_root_s = args
  openpilot_root = Path(openpilot_root_s)
  log_root = Path(log_root_s)
  cap_root = Path(cap_root_s)
  LogReader = load_logreader(openpilot_root)
  route_dir, files = discover(spec, log_root, cap_root)
  if not files:
    raise FileNotFoundError(route_dir)
  row = scan_route(LogReader, files)
  row['route'] = spec[-1]
  row['source_dir'] = str(route_dir)
  return short, row


def _merge_count_dict(dst: Counter, src: dict, key=int) -> None:
  for k, v in src.items():
    dst[key(k)] += int(v)


def aggregate_segment_rows(rows: list[dict]) -> dict:
  if not rows:
    raise ValueError('no segment rows')
  rows = sorted(rows, key=lambda r: r['first_mono_s'])
  agg_ids: dict[int, dict] = {}
  transitions: Counter[str] = Counter()
  ref81: Counter[int] = Counter()
  pair81: Counter[str] = Counter()
  b6src: Counter[int] = Counter(); b6src012: Counter[int] = Counter(); b6dupe: Counter[int] = Counter(); b6native: Counter[int] = Counter(); b6echo: Counter[int] = Counter(); b6send: Counter[int] = Counter()
  abs_eps: list[dict] = []
  prev_last_id = None
  for r in rows:
    for lid_s, v in r['target_lateral_ids'].items():
      lid=int(lid_s)
      a=agg_ids.setdefault(lid, {'label':v['label'],'frames':0,'target_angle_raw_range':[32767,-32768], 'request_level_counts':Counter(), 'cruise_latch_counts':Counter(), 'b23_counts':Counter()})
      a['frames'] += v['frames']; a['target_angle_raw_range'][0]=min(a['target_angle_raw_range'][0],v['target_angle_raw_range'][0]); a['target_angle_raw_range'][1]=max(a['target_angle_raw_range'][1],v['target_angle_raw_range'][1])
      _merge_count_dict(a['request_level_counts'],v['request_level_counts']); _merge_count_dict(a['cruise_latch_counts'],v['cruise_latch_counts']); _merge_count_dict(a['b23_counts'],v['b23_counts'],lambda x:int(x,16))
    _merge_count_dict(transitions,r['id_transition_counts'],str)
    if prev_last_id is not None and r['first_08a_id'] is not None and prev_last_id != r['first_08a_id']:
      transitions[f'{prev_last_id}->{r["first_08a_id"]}'] += 1
    if r['last_08a_id'] is not None: prev_last_id=r['last_08a_id']
    _merge_count_dict(ref81,r['native_081_id_counts']); _merge_count_dict(pair81,r['native_081_latest_08a_pairing'],str)
    _merge_count_dict(b6src,r['b6']['can_src_counts']); _merge_count_dict(b6src012,r['b6']['src_0_1_2_id_counts_raw']); _merge_count_dict(b6dupe,r['b6']['same_event_tx_echo_duplicate_id_counts']); _merge_count_dict(b6native,r['b6']['unmatched_native_candidate_id_counts']); _merge_count_dict(b6echo,r['b6']['panda_tx_echo_id_counts']); _merge_count_dict(b6send,r['b6']['sendcan_id_counts'])
    base=r['first_mono_s']
    for ep in r['nonzero_episodes']:
      e=dict(ep); e['_abs_start']=base+ep['start_s']; e['_abs_end']=base+ep['end_s']; abs_eps.append(e)
  for lid,a in agg_ids.items():
    lo,hi=a['target_angle_raw_range']; a['target_angle_deg_equiv_range']=[round(lo*1024/17870,6),round(hi*1024/17870,6)]
    a['request_level_counts']={str(k):v for k,v in sorted(a['request_level_counts'].items())}; a['cruise_latch_counts']={str(k):v for k,v in sorted(a['cruise_latch_counts'].items())}; a['b23_counts']={f'0x{k:02X}':v for k,v in sorted(a['b23_counts'].items())}
  # Merge an active run split only by a logger segment boundary.
  merged=[]
  for e in sorted(abs_eps,key=lambda x:x['_abs_start']):
    if merged and merged[-1]['target_lateral_id']==e['target_lateral_id'] and e['_abs_start']-merged[-1]['_abs_end'] <= 0.25:
      m=merged[-1]; m['_abs_end']=e['_abs_end']; m['end_s']=e['end_s']; m['frames']+=e['frames']; m['target_angle_raw_min']=min(m['target_angle_raw_min'],e['target_angle_raw_min']); m['target_angle_raw_max']=max(m['target_angle_raw_max'],e['target_angle_raw_max'])
      for fld in ('request_level_counts','cruise_latch_counts','b23_counts'):
        c=Counter(m[fld]); c.update(e[fld]); m[fld]=dict(c)
    else: merged.append(e)
  route_base=rows[0]['first_mono_s']
  for e in merged:
    e['start_s']=round(e.pop('_abs_start')-route_base,6); e['end_s']=round(e.pop('_abs_end')-route_base,6); e['duration_s']=round(e['end_s']-e['start_s'],6)
  return {
    'segment_count':len(rows), 'first_mono_s':rows[0]['first_mono_s'], 'last_mono_s':rows[-1]['last_mono_s'], 'first_08a_id':rows[0]['first_08a_id'], 'last_08a_id':rows[-1]['last_08a_id'],
    'duration_s':round(rows[-1]['last_mono_s']-rows[0]['first_mono_s'],6), 'native_08a_frames':sum(a['frames'] for a in agg_ids.values()),
    'target_lateral_ids':{str(k):v for k,v in sorted(agg_ids.items())}, 'nonzero_episode_count':len(merged), 'nonzero_episodes':merged,
    'id_transition_counts':dict(sorted(transitions.items())), 'native_081_id_counts':{str(k):v for k,v in sorted(ref81.items())}, 'native_081_latest_08a_pairing':dict(pair81),
    'b6':{'can_src_counts':{str(k):v for k,v in sorted(b6src.items())}, 'src_0_1_2_id_counts_raw':{str(k):v for k,v in sorted(b6src012.items())}, 'same_event_tx_echo_duplicate_id_counts':{str(k):v for k,v in sorted(b6dupe.items())}, 'unmatched_native_candidate_id_counts':{str(k):v for k,v in sorted(b6native.items())}, 'panda_tx_echo_id_counts':{str(k):v for k,v in sorted(b6echo.items())}, 'sendcan_id_counts':{str(k):v for k,v in sorted(b6send.items())}},
  }

def exact_f33() -> dict:
  corpus = REPO / 'data/generated/camry-8965F3307000/decompilations.jsonl'
  rows = {}
  for line in corpus.open():
    row = json.loads(line)
    if row.get('record') == 'function':
      rows[int(row['entry_addr'], 16)] = row
  funcs = {a: r.get('decompiled_c', '') for a, r in rows.items()}
  ceffc = funcs[0xCEFFC]
  unpack = funcs[0x4BD46]
  cef26 = funcs[0xCEF26]
  ce7fe = funcs[0xCE7FE]
  cefa4 = funcs[0xCEFA4]
  writes_cb00 = sorted(f'0x{a:08X}' for a, c in funcs.items() if re.search(r'DAT_febecb00\s*=', c))
  reads_adb0 = sorted(f'0x{a:08X}' for a, c in funcs.items() if 'DAT_febeadb0' in c)

  expected_bank_map = {1: 0, 4: 1, 10: 3, 11: 2, 18: 5, 19: 4}
  literals = {1: r'\\x01', 4: r'\\x04', 10: r'\\n', 11: r'\\v', 18: r'\\x12', 19: r'\\x13'}
  for lid, bank in expected_bank_map.items():
    if not re.search(rf"DAT_febeadb0 == '{literals[lid]}'.*?DAT_febecb00 = {bank};", ceffc, re.S):
      raise RuntimeError(f'exact F33 selector mapping missing ID {lid} -> bank {bank}')

  rx_art = json.loads((REPO / 'data/generated/camry_8965F3307000_external_lateral_ingress.json').read_text())
  accepted_rx = {int(x['can_id'], 16) for x in rx_art['normal_rx']['accepted']}
  state_carriers = {0x08A, 0x081, 0x0FE, 0x251, 0x371, 0x412}
  if state_carriers & accepted_rx:
    raise RuntimeError(f'unexpected FRC/cruise state carrier in exact F33 Rx: {state_carriers & accepted_rx}')

  def direct_refs(addr: int, ref_type: str = 'READ') -> list[str]:
    out = set()
    for entry, row in rows.items():
      for ref in row.get('data_references', []):
        try:
          to_addr = int(ref['to_addr'], 16)
        except (KeyError, TypeError, ValueError):
          continue
        if to_addr == addr and ref.get('ref_type') == ref_type:
          out.add(f'0x{entry:08X}')
    return sorted(out)

  # Exact F33 signal261..273 application fields as unpacked by 0x4BD46.  The
  # standard generated-COM -> stage -> broad-snapshot propagation is explicit
  # for every entry below except signal266, whose staged F135 byte is never
  # copied into the broad BCD66 snapshot.  This is a bounded direct-reference
  # consumer census, not an OEM naming claim for the unnamed fields.
  secondary_specs = {
    261: ('B3[5:0]', 0xFEBEADB0, 'Target Lateral ID; sole ordinary profile selector value'),
    262: ('B4:B5', 0xFEBEAE90, 'signed target steering-angle command'),
    263: ('B6[7]', 0xFEBEADDD, 'participant in CB664/C7B4 state; CB73A subsequently requires ID49 Self-Propelled Transport'),
    264: ('B6[6:4]', 0xFEBEADB1, 'no recovered downstream direct reader after snapshot'),
    265: ('B6[2]', 0xFEBEADBB, 'when 1 suppresses one additive controller contribution'),
    266: ('B6[1:0]', None, 'staged at FEBEF135 but not propagated into the broad input snapshot; no recovered downstream direct reader'),
    267: ('B7[7:6]', 0xFEBEADC2, 'no recovered downstream direct reader after snapshot'),
    268: ('B7[5:0]', 0xFEBEADBC, 'application modulo-64 sequence'),
    269: ('B8', 0xFEBEADBD, 'percentage contribution divided by 100; special 201/202/203 calibration behavior'),
    270: ('B9', 0xFEBEADBE, 'percentage contribution divided by 100'),
    271: ('B10[7]', 0xFEBEADC1, 'no recovered downstream direct reader after snapshot'),
    272: ('B10[5]', 0xFEBEADE0, 'no recovered downstream direct reader after snapshot'),
    273: ('B10[2:0]', 0xFEBEADD9, 'valid-gated 3-bit status/mode republished through CFDA0/CFDD4; not a profile-selector input'),
  }
  secondary = {}
  for sig, (wire, snapshot, role) in secondary_specs.items():
    secondary[str(sig)] = {
      'wire': wire,
      'snapshot': None if snapshot is None else f'0x{snapshot:08X}',
      'direct_reader_entries': [] if snapshot is None else direct_refs(snapshot),
      'role': role,
      'exact_oem_name': 'Target Lateral ID' if sig == 261 else ('Target Steering Angle' if sig == 262 else None),
    }

  expected_readers = {
    '261': ['0x000CB73A', '0x000CEFFC'],
    '262': ['0x000CBA80', '0x000CBB66', '0x000CCF0E', '0x000CEE80'],
    '263': ['0x000CB664'],
    '264': [], '265': ['0x000CDA20'], '266': [], '267': [],
    '268': ['0x000CEC8A'], '269': ['0x000CE3AA'], '270': ['0x000CDFF8'],
    '271': [], '272': [], '273': ['0x000CFDA0'],
  }
  for sig, readers in expected_readers.items():
    if secondary[sig]['direct_reader_entries'] != readers:
      raise RuntimeError(f'exact F33 signal{sig} reader census changed: {secondary[sig]["direct_reader_entries"]} != {readers}')

  return {
    'selector_entry': '0x000CEFFC',
    'selector_direct_inputs': ['FEBEACBD', 'FEBECAFF', 'FEBEADB0(Target Lateral ID snapshot)'],
    'selector_requires': {'FEBEACBD': 0, 'FEBECAFF': 1},
    'selector_bank_map': {str(k): v for k, v in expected_bank_map.items()},
    'selector_resets_to_default_each_invocation': "DAT_febecb00 = '\\a'" in ceffc or 'DAT_febecb00 = 7' in ceffc,
    'selector_writer_entries_complete_decompilation_corpus': writes_cb00,
    'target_id_snapshot_reader_entries_complete_decompilation_corpus': reads_adb0,
    'unpacker_new_generation_gate': 'DAT_febe80c8 != DAT_febe5364' in unpack and 'DAT_febe7f68 < 2' in unpack,
    'unpacker_has_previous_target_id_comparison': 'DAT_febe80bc ==' in unpack or 'DAT_febe80bc !=' in unpack,
    'communication_timeout': {'pdu': 44, 'nominal_ms': 35, 'basis': 'seven exact-F33 foreground ticks at 5 ms'},
    'profile_supervision': {
      'entry': '0x000CEF26',
      'thresholds_by_bank': {
        '0_PCS': {'abs_signal_threshold': 1536, 'persistence_cycles': 96},
        '1_LDA': {'abs_signal_threshold': 1280, 'persistence_cycles': 96},
        '2_LTA_LCA': {'abs_signal_threshold': 1280, 'persistence_cycles': 96},
        '3_HandsOffLTA': {'abs_signal_threshold': 1280, 'persistence_cycles': 96},
        '4_PDA': {'abs_signal_threshold': 1280, 'persistence_cycles': 96},
        '5_SDG': {'abs_signal_threshold': 2048, 'persistence_cycles': 96},
      },
      'interpretation': 'profile-indexed threshold/persistence supervisor feeding common readiness/fault state; not a Target-Lateral-ID ownership timer',
      'evidence': 'CEF26 indexes the common bank, while CE7FE readiness is separately recomputed and CEFFC continues to select from the current delivered ID',
      'cef26_reads_current_bank': 'DAT_febecb00' in cef26,
      'ce7fe_recomputes_common_readiness': all(x in ce7fe for x in ('FUN_000ce772', 'FUN_000ce7a6')),
    },
    'secondary_application_fields': secondary,
    'secondary_field_authorization_boundary': {
      'generic_command_enable_recovered': False,
      'basis': 'CEFFC reads only ACBD, CAFF and Target Lateral ID. ACBD is a staged COM/extraction-status value; CEFA4 builds CAFF from communication-monitor/validity state. No signal263..273 snapshot is a direct CEFFC input, and their complete direct-reader census resolves the live consumers above.',
      'signal263_scope': 'CB664 uses signal263 as an inhibit condition in the C7B4 state that CB73A then gates on Target Lateral ID 49 (Self-Propelled Transport); it is not ordinary LTA/LDA/PDA/SDG enablement.',
      'signal273_scope': 'CFDA0 conditionally republishes signal273 into a separate status/mode machine consumed by CFDD4/CFE64; it is not a CEFFC selector input.',
      'cefa4_communication_validity_shape': all(x in cefa4 for x in ('FUN_000bdb76(0x11)', 'FUN_000bdb76(0x1a)', 'puVar2[0x12ff]')),
    },
    'known_frc_state_carriers_absent_from_exact_rx': [f'0x{x:03X}' for x in sorted(state_carriers)],
    'exact_normal_rx_descriptor_count': len(accepted_rx),
    'boundary': 'This does not mean EPS is state-blind: the common controller has SecOC/freshness, PDU health, speed, angle/rate, fault and slew/limit supervision. It means the recovered B6 profile selector has no DRCC/LTA engagement authorization input and no per-profile ownership latch.',
  }


def main() -> None:
  ap = argparse.ArgumentParser()
  ap.add_argument('--openpilot-root', type=Path, default=DEFAULT_OPENPILOT)
  ap.add_argument('--log-root', type=Path, default=DEFAULT_LOG_ROOT)
  ap.add_argument('--capture-root', type=Path, default=DEFAULT_CAP_ROOT)
  ap.add_argument('--out', type=Path, default=DEFAULT_OUT)
  ap.add_argument('--single-route', choices=sorted(ROUTES), help=argparse.SUPPRESS)
  ap.add_argument('--single-file', type=Path, help=argparse.SUPPRESS)
  args = ap.parse_args()
  if args.single_file:
    LogReader = load_logreader(args.openpilot_root)
    row = scan_route(LogReader, [args.single_file])
    args.out.write_text(json.dumps(row, sort_keys=True) + '\n')
    return
  if args.single_route:
    short = args.single_route
    route_dir, files = discover(ROUTES[short], args.log_root, args.capture_root)
    if not files:
      raise FileNotFoundError(route_dir)
    parts=[]
    for path in files:
      with tempfile.NamedTemporaryFile(prefix='camry-seg-', suffix='.json', delete=False) as tf: tmp=Path(tf.name)
      try:
        subprocess.run([sys.executable, str(Path(__file__).resolve()), '--single-file', str(path), '--openpilot-root', str(args.openpilot_root), '--out', str(tmp)], check=True)
        parts.append(json.loads(tmp.read_text()))
      finally: tmp.unlink(missing_ok=True)
    row=aggregate_segment_rows(parts)
    row['route']=ROUTES[short][-1]; row['source_dir']=str(route_dir)
    args.out.write_text(json.dumps(row, sort_keys=True)+'\n')
    return
  routes = {}
  agg_ids = Counter(); agg_b6_src012 = Counter(); agg_b6_dupe = Counter(); agg_b6_native = Counter(); agg_b6_send = Counter(); agg_episodes = Counter(); agg_081 = Counter(); agg_081_pairs = Counter()
  total_segments = 0
  for short in ROUTES:
    with tempfile.NamedTemporaryFile(prefix=f'camry-{short}-', suffix='.json', delete=False) as tf:
      tmp = Path(tf.name)
    try:
      cmd = [sys.executable, str(Path(__file__).resolve()), '--single-route', short, '--openpilot-root', str(args.openpilot_root), '--log-root', str(args.log_root), '--capture-root', str(args.capture_root), '--out', str(tmp)]
      subprocess.run(cmd, check=True)
      row = json.loads(tmp.read_text())
    finally:
      tmp.unlink(missing_ok=True)
    routes[short] = row
    total_segments += row['segment_count']
    for k, v in row['target_lateral_ids'].items(): agg_ids[int(k)] += v['frames']
    for k, v in row['b6']['src_0_1_2_id_counts_raw'].items(): agg_b6_src012[int(k)] += v
    for k, v in row['b6']['same_event_tx_echo_duplicate_id_counts'].items(): agg_b6_dupe[int(k)] += v
    for k, v in row['b6']['unmatched_native_candidate_id_counts'].items(): agg_b6_native[int(k)] += v
    for k, v in row['native_081_id_counts'].items(): agg_081[int(k)] += v
    agg_081_pairs.update(row['native_081_latest_08a_pairing'])
    for k, v in row['b6']['sendcan_id_counts'].items(): agg_b6_send[int(k)] += v
    for ep in row['nonzero_episodes']: agg_episodes[ep['target_lateral_id']] += 1
    print(short, row['segment_count'], {k:v['frames'] for k,v in row['target_lateral_ids'].items()}, 'episodes', row['nonzero_episode_count'], flush=True)
  observed = sorted(agg_ids)
  report = {
    'schema': 'camry-2026-lateral-family-census-v1',
    'corpus': {
      'route_count': len(routes), 'segment_count': total_segments,
      'selection': 'all retained normal-logger road routes whose qlogs showed vehicle motion before Sep-4, plus complete Sep-4/Sep-6 road routes; route 1c retains the marginal-motion case',
      'boundary': 'LogReader emits a corrupted-events RuntimeWarning while reading route 1c; its recovered 0x08A population is ID0 only, so it does not create any positive steering-profile witness. The other selected routes reduce without that warning.',
    },
    'oem_target_lateral_id_dictionary': {str(k): v for k,v in LABELS.items()},
    'exact_f33': exact_f33(),
    'aggregate': {
      'native_08a_target_lateral_id_counts': {str(k): v for k,v in sorted(agg_ids.items())},
      'observed_target_lateral_ids': observed,
      'observed_nonzero_ids': [x for x in observed if x],
      'unobserved_exact_f33_profiles': sorted(F33_ACCEPTED - set(observed)),
      'nonzero_episode_counts_by_id': {str(k): v for k,v in sorted(agg_episodes.items())},
      'b6_src_0_1_2_id_counts_raw': {str(k): v for k,v in sorted(agg_b6_src012.items())},
      'b6_same_event_tx_echo_duplicate_id_counts': {str(k): v for k,v in sorted(agg_b6_dupe.items())},
      'unmatched_native_b6_candidate_id_counts': {str(k): v for k,v in sorted(agg_b6_native.items())},
      'native_081_target_lateral_id_counts': {str(k): v for k,v in sorted(agg_081.items())},
      'native_081_latest_08a_pairing': dict(sorted(agg_081_pairs.items())),
      'native_081_latest_08a_match_fraction': (agg_081_pairs['match'] / agg_081_pairs['eligible']) if agg_081_pairs['eligible'] else None,
      'synthetic_sendcan_b6_id_counts': {str(k): v for k,v in sorted(agg_b6_send.items())},
    },
    'routes': routes,
    'interpretation': {
      'request_plane': '0x08A is the FRC-side request/reference carrier; it is not accepted by exact F33.',
      'eps_ingress': '0x0B6/PDU44 is exact F33 external Target-Lateral-ID/target-angle ingress and is expected from the brake-system source domain. Native B6 absence therefore must not be conflated with absence of FRC steering requests.',
      'profile_switching': 'A newly delivered healthy B6 generation can replace the current Target Lateral ID without a recovered previous-ID ownership check. The common controller retains ordinary filters/slew/supervision state across ticks.',
    },
  }
  args.out.parent.mkdir(parents=True, exist_ok=True)
  args.out.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n')
  print('wrote', args.out)
  print('aggregate ids', dict(sorted(agg_ids.items())))
  print('aggregate raw src0/1/2 b6', dict(sorted(agg_b6_src012.items())))
  print('aggregate same-event TX-echo duplicates', dict(sorted(agg_b6_dupe.items())))
  print('aggregate unmatched native b6 candidates', dict(sorted(agg_b6_native.items())))
  print('aggregate sendcan b6', dict(sorted(agg_b6_send.items())))

if __name__ == '__main__': main()
