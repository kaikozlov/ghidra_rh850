#!/usr/bin/env python3
"""Compact S/H structural/decompiler evidence needed for final named-residue closure."""
from __future__ import annotations
import hashlib,json
from pathlib import Path
from sienna_target import CODEFLASH as SIENNA_CODEFLASH
from corolla_h_constants import RAW_DUMP as H_RAW_DUMP
ROOT=Path(__file__).resolve().parents[1]
SRAW=SIENNA_CODEFLASH
HRAW=H_RAW_DUMP
SFP=ROOT/'build/work/corpora/sienna_function_structural_fingerprints.jsonl'
HFP=ROOT/'build/work/corpora/h_clean_function_structural_fingerprints.jsonl'
HDC=ROOT/'build/work/corpora/h_small_adapters_forced.jsonl'
OUT=ROOT/'data/generated/corolla_8965H1202000_final_named_residue_evidence.json'
S_ENTRIES={
 0x5778C,0x57980,0x57A7E,0x58404,0x5DB6E,0x64F18,0x656F0,0x6578E,
 0x8A08E,0x8A0C2,0x8A482,0x8A542,0xBEC4C,0xB893E,0xBCB3A,0xB6396,0xCBCC8,
 0x56FC2,0x57BFE,0x5B9C4,0x5C0B6,0x5C666,
}
H_ENTRIES={
 0x52CFA,0x52EEE,0x52FEC,0x5389C,0x58BBC,0x5F258,0x5FA96,0x5FB30,
 0x8448E,0x844C2,0x84882,0x84942,0xBD954,0xB73F0,0xBBA48,0xB5EA4,0xCF27E,
 0x5262C,0x5316C,0x56BAC,0x5722E,0x5778E,0x5F812,0x8441C,0x47C2,0x47C8,0x47CE,0x20880,0x482AE,
}
H_DECOMP={0x47C2,0x47C8,0x47CE,0x5F812,0x5FB30,0xB5EA4}
def sha(b):return hashlib.sha256(b).hexdigest()
def load_jsonl(p,key='entry_addr'):
 out={}
 for l in p.read_text().splitlines():
  r=json.loads(l)
  if key in r:out[int(r[key],16)]=r
 return out
def compact_fp(r,raw):
 a=int(r['entry_addr'],16);n=int(r['body_size'])
 if sum(map(int,r['instruction_lengths']))!=n:raise ValueError(f'noncontiguous fp {a:#x}')
 return {'entry':f'0x{a:08X}','body_size':n,'body_sha256':sha(raw[a:a+n]),'instruction_count':int(r['instruction_count']),
         'direct_call_targets':r.get('direct_call_targets',[]),'direct_call_target_count':int(r['direct_call_target_count']),
         'indirect_call_count':int(r['indirect_call_count']),'conditional_branch_count':int(r['conditional_branch_count']),
         'unconditional_branch_count':int(r['unconditional_branch_count']),'return_count':int(r['return_count'])}
def main():
 sraw=SRAW.read_bytes();hraw=HRAW.read_bytes()[:0x100000]
 sf=load_jsonl(SFP);hf=load_jsonl(HFP);hd=load_jsonl(HDC)
 smiss=S_ENTRIES-set(sf);hmiss=H_ENTRIES-set(hf);dmiss=H_DECOMP-set(hd)
 if smiss or hmiss or dmiss:raise SystemExit(f'missing sf={smiss} hf={hmiss} dc={dmiss}')
 dec=[]
 for a in sorted(H_DECOMP):
  r=hd[a];n=int(r['body_size']);c=r['decompiled_c']
  dec.append({'entry':f'0x{a:08X}','body_size':n,'body_sha256':sha(hraw[a:a+n]),'decompiled_c_sha256':sha(c.encode()),'decompiled_c':c})
 p={'schema':'corolla-h-final-named-residue-evidence-v1','software_id':'8965H1202000',
    'images':{'sienna_sha256':sha(sraw),'h_sha256':sha(hraw)},
    'sources':{'sienna_fingerprints':{'path':str(SFP.relative_to(ROOT)),'sha256':sha(SFP.read_bytes())},'h_clean_fingerprints':{'path':str(HFP.relative_to(ROOT)),'sha256':sha(HFP.read_bytes())},'h_decompiler':{'path':str(HDC.relative_to(ROOT)),'sha256':sha(HDC.read_bytes())}},
    'sienna_fingerprints':[compact_fp(sf[a],sraw) for a in sorted(S_ENTRIES)],
    'h_fingerprints':[compact_fp(hf[a],hraw) for a in sorted(H_ENTRIES)],
    'h_decompiler':dec}
 OUT.write_text(json.dumps(p,indent=2,sort_keys=True)+'\n');print(f'wrote {OUT}: {len(p["sienna_fingerprints"])} S fp, {len(p["h_fingerprints"])} H fp, {len(dec)} H decomp')
if __name__=='__main__':main()
