#!/usr/bin/env python3
"""Compact target-native decompiler evidence for the final unique-shape cohort.

The cohort is stable across regeneration: include current structural-only rows, plus
rows whose only target-native inspection evidence is this artifact itself.
"""
from __future__ import annotations
import hashlib,json
from pathlib import Path
from corolla_h_constants import RAW_DUMP as H_RAW_DUMP
ROOT=Path(__file__).resolve().parents[1]
RAW=H_RAW_DUMP
MATRIX=ROOT/'data/generated/corolla_8965H1202000_static_coverage_matrix.json'
STRUCT=ROOT/'data/generated/corolla_8965H1202000_structural_function_transfer.json'
SRC=ROOT/'build/work/corpora/h_small_adapters_forced.jsonl'
OUT=ROOT/'data/generated/corolla_8965H1202000_structural_residue_decompiler_evidence.json'
SELF=str(OUT.relative_to(ROOT))
def sha(b):return hashlib.sha256(b).hexdigest()
def main():
 raw=RAW.read_bytes()[:0x100000];m=json.loads(MATRIX.read_text());st=json.loads(STRUCT.read_text());sm={int(x['reference_entry'],16):x for x in st['matches']}
 refs=[]
 for r in m['functions']:
  owners=r.get('target_native_evidence_files',[])
  if r['coverage']=='structural-candidate-only' or (r['coverage']=='target-native-inspected-unique-shape' and owners==[SELF]):
   refs.append(int(r['reference_entry'],16))
 if len(refs)!=96:raise SystemExit(f'expected stable 96-row structural residue, got {len(refs)}')
 targets={int(sm[r]['target_entry'],16):r for r in refs}
 if any(sm[r]['classification']!='unique-exact-shape' for r in refs):raise SystemExit('cohort contains non-unique-exact-shape row')
 by={}
 for l in SRC.read_text().splitlines():
  x=json.loads(l)
  if x.get('record')=='function':by[int(x['entry_addr'],16)]=x
 missing=sorted(set(targets)-set(by))
 if missing:raise SystemExit(f'missing H decomp targets: {[hex(x) for x in missing]}')
 funcs=[]
 for a in sorted(targets):
  x=by[a]
  if not x.get('decompile_completed') or not x.get('decompiled_c'):raise SystemExit(f'incomplete decompile {a:#x}')
  n=int(x['body_size']);c=x['decompiled_c'];ref=targets[a]
  funcs.append({'entry':f'0x{a:08X}','reference_entry':f'0x{ref:08X}','reference_name':next(r['reference_name'] for r in m['functions'] if int(r['reference_entry'],16)==ref),'body_size':n,'body_sha256':sha(raw[a:a+n]),'decompiled_c_sha256':sha(c.encode()),'decompiled_c':c})
 p={'schema':'corolla-h-structural-residue-decompiler-evidence-v1','software_id':'8965H1202000','image':{'path':str(RAW.relative_to(ROOT)),'codeflash_size':len(raw),'codeflash_sha256':sha(raw)},'source_corpus':{'path':str(SRC.relative_to(ROOT)),'sha256':sha(SRC.read_bytes()),'boundary':'bounded existing H corpus; no new Ghidra analysis'},'structural_source':{'path':str(STRUCT.relative_to(ROOT)),'sha256':sha(STRUCT.read_bytes())},'functions':funcs,'function_count':len(funcs),'static_conclusion':{'all_96_unique_shape_candidates_target_native_inspected':True,'boundary':'This evidence records H operands/dataflow/decompiler text for each unique complete-instruction-shape candidate. It promotes inspection evidence only; it does not assert semantic-role or field-for-field homology.'}}
 OUT.write_text(json.dumps(p,indent=2,sort_keys=True)+'\n');print(f'wrote {OUT}: {len(funcs)} target-native inspected candidates')
if __name__=='__main__':main()
