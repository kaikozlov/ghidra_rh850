#!/usr/bin/env python3
"""Compact target-native H evidence for the remaining SecOC/ICU-S named roles."""
from __future__ import annotations
import hashlib,json
from pathlib import Path
from corolla_h_constants import RAW_DUMP as H_RAW_DUMP
ROOT=Path(__file__).resolve().parents[1]
RAW=H_RAW_DUMP
SC=ROOT/'data/generated/decompilations.jsonl'
SOURCES={
 'core':ROOT/'build/work/corpora/h_8965H1202000_secoc_core_decompilations.jsonl',
 'key':ROOT/'build/work/corpora/h_8965H1202000_secoc_key_decompilations.jsonl',
 'freshness':ROOT/'build/work/corpora/h_8965H1202000_secoc_freshness_decompilations.jsonl',
 'rxind':ROOT/'build/work/corpora/h_8965H1202000_secoc_rxind_final_decompilations.jsonl',
 'app':ROOT/'build/work/corpora/h_8965H1202000_secoc_app_decompilations.jsonl',
 'app_correct':ROOT/'build/work/corpora/h_8965H1202000_secoc_app_correct_decompilations.jsonl',
 'clean':ROOT/'build/work/corpora/h_8965H1202000_rdbihelper2_decompilations.jsonl',
}
OUT=ROOT/'data/generated/corolla_8965H1202000_secoc_surface_decompiler_evidence.json'
CORE=[0x8704c,0x870a8,0x871a0,0x87610,0x87636,0x8783c,0x87b46,0x87bba,0x87c14,0x87c70,0x87ccc,0x87dd0,0x88028,0x88080,0x880dc,0x881dc,0x888fa,0x889cc,0x88b5c,0x88b6a,0x88b9c,0x88c0a,0x89448,0x894be,0x89510]
PAIRS=[]
for s in CORE: PAIRS.append((s,s-0x5c00,'core'))
PAIRS += [
 (0x8db84,0x88024,'key'),(0x8dc64,0x8818c,'rxind'),
 (0x8e80a,0x89558,'freshness'),(0x8e8e6,0x896b0,'freshness'),(0x8e942,0x89758,'freshness'),
 (0x8eeca,0x89e9a,'freshness'),(0x8ef9e,0x89f6e,'freshness'),(0x8f084,0x8a07a,'freshness'),(0x8f112,0x8a130,'freshness'),
 (0x650ac,0x5f3ec,'app'),(0x650ee,0x5f42e,'app'),
 (0x69068,0x633a0,'app_correct'),(0x6920a,0x63542,'app_correct'),(0x6922c,0x63564,'app_correct'),(0x69246,0x6357e,'app_correct'),(0x6926a,0x635a2,'app_correct'),
 (0x4b3aa,0x468fa,'clean'),
]
def sha(b):return hashlib.sha256(b).hexdigest()
def load(p):
 d={}
 for l in p.read_text().splitlines():
  r=json.loads(l)
  if r.get('entry_addr'):d[int(r['entry_addr'],16)]=r
 return d
def main():
 raw=RAW.read_bytes();img=raw[:0x100000];srows=load(SC);src={k:load(v) for k,v in SOURCES.items()};out=[]
 assert len(PAIRS)==42 and len({x[0] for x in PAIRS})==42
 for s,h,sk in PAIRS:
  sr=srows[s];hr=src[sk].get(h)
  if not hr or not hr.get('decompile_completed') or not hr.get('decompiled_c'):raise SystemExit(f'missing H {h:#x} from {sk}')
  refn=int(sr['body_size']);hrep=int(hr['body_size']);c=hr['decompiled_c'];window=img[h:h+refn]
  out.append({'reference_entry':f'0x{s:08X}','reference_name':sr['name'],'reference_body_size':refn,'target_entry':f'0x{h:08X}','target_reported_body_size':hrep,'raw_window_size':refn,'raw_window_sha256':sha(window),'decompiled_c_sha256':sha(c.encode()),'decompiled_c':c,'source_corpus':sk,'boundary_note':('forced callback body is fragmented by preexisting disposable-project overlaps; raw window is pinned to canonical role span and decompiled semantics are used' if sk=='app_correct' else 'target-native function/body evidence')})
 payload={'schema':'corolla-h-secoc-surface-decompiler-evidence-v1','software_id':'8965H1202000','image':{'path':str(RAW.relative_to(ROOT)),'codeflash_size':len(img),'codeflash_sha256':sha(img)},'function_count':len(out),'functions':out,'source_corpora':{k:{'path':str(v.relative_to(ROOT)),'sha256':sha(v.read_bytes())} for k,v in SOURCES.items()},'evidence_boundary':'42 residual canonical SecOC/ICU-S roles only. Forced callback bodies may be fragmented in the disposable project; raw canonical-size windows plus target-native decompiler semantics are pinned rather than treating Ghidra reported body size as contiguous truth.'}
 OUT.write_text(json.dumps(payload,indent=2,sort_keys=True)+'\n');print(f'wrote {OUT}: {len(out)} role records')
if __name__=='__main__':main()
