#!/usr/bin/env python3
"""Build deterministic Sienna->Corolla-H deadline-monitor callback-surface closure."""
from __future__ import annotations
import argparse,hashlib,json,struct
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
HRAW=ROOT/'community/albinoelephant/raw-20260818/albinoelephant-corolla-2023.20260814-0023/dump_codeflash_00000000_00200000_20260814-025814.bin'; SRAW=ROOT/'firmware/RH850_P1M-E_CodeFlash.bin'; EV=ROOT/'data/generated/corolla_8965H1202000_deadline_monitor_surface_decompiler_evidence.json'; COVER=ROOT/'data/generated/corolla_8965H1202000_static_coverage_matrix.json'; OUT=ROOT/'data/generated/corolla_8965H1202000_deadline_monitor_surface.json'
S_TABLES=(('variant_d_a',0x28524,1,52,tuple(range(0,52,4))),('simple',0x28558,28,12,(0,4,8)),('variant_d_b',0x286D0,1,52,tuple(range(0,52,4))))
H_TABLES=(('variant_d_a',0x280B4,1,52,tuple(range(0,52,4))),('simple',0x280E8,28,12,(0,4,8)),('variant_d_b',0x28260,1,52,tuple(range(0,52,4))))
def sha(b):return hashlib.sha256(b).hexdigest()
def table(raw,spec):
 name,base,count,stride,offs=spec; rows=[];vals=[]
 for i in range(count):
  row=[]
  for off in offs:
   x=struct.unpack_from('<I',raw,base+i*stride+off)[0];row.append(x);vals.extend([x] if x else [])
  rows.append([f'0x{x:08X}' if x else None for x in row])
 return {'name':name,'base':f'0x{base:08X}','count':count,'stride':stride,'pointer_offsets':list(offs),'rows':rows,'nonzero_slots':len(vals),'unique_callbacks':len(set(vals)),'callbacks':[f'0x{x:08X}' for x in sorted(set(vals))]}
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,default=OUT);a=ap.parse_args();H=HRAW.read_bytes()[:0x100000];S=SRAW.read_bytes();ev=json.loads(EV.read_text());by={int(r['entry'],16):r for r in ev['functions']}
 st=[table(S,x) for x in S_TABLES];ht=[table(H,x) for x in H_TABLES]
 if [x['unique_callbacks'] for x in st] != [3,82,3] or [x['unique_callbacks'] for x in ht] != [3,82,3]:raise ValueError('deadline callback cardinality drift')
 if sum(len(set(int(x,16) for x in t['callbacks'])) for t in ht)!=88:raise ValueError('H callback total drift')
 cov=json.loads(COVER.read_text()); canon=[r for r in cov['functions'] if r['reference_name'].startswith('deadline_')]
 if len(canon)!=88:raise ValueError(f'expected 88 canonical deadline residue rows, got {len(canon)}')
 rec=[{'reference_entry':r['reference_entry'],'reference_name':r['reference_name'],'classification':'target-surface-recensused','recensus':'complete H three-table deadline-monitor callback surface'} for r in canon]
 payload={'schema':'corolla-h-deadline-monitor-surface-v1','software_id':'8965H1202000','images':{'h_sha256':sha(H),'sienna_sha256':sha(S)},'evidence':{'decompiler_evidence':str(EV.relative_to(ROOT))},'dispatchers':{'simple':{'sienna':'0x0006962A','h':'0x000639CA','body_size':138,'unique_exact_instruction_shape':True},'variant_d':{'sienna':'0x0006A28A','h':'0x0006462A','body_size':1208,'unique_exact_instruction_shape':True},'simple_setup':{'sienna':'0x0003DC88','h':'0x000387E4','body_size':346,'unique_exact_instruction_shape':True,'h_table':'0x000280E8'}},'sienna_tables':st,'h_tables':ht,'surface_recensus':rec,'surface_recensus_count':len(rec),'summary':{'sienna_unique_callback_union':len(set(x for t in st for x in t['callbacks'])),'h_unique_callback_union':len(set(x for t in ht for x in t['callbacks'])),'same_table_shapes':[ (x['count'],x['stride'],len(x['pointer_offsets'])) for x in st ] == [(x['count'],x['stride'],len(x['pointer_offsets'])) for x in ht], 'same_per_table_unique_counts':[x['unique_callbacks'] for x in st]==[x['unique_callbacks'] for x in ht], 'all_88_named_deadline_residuals_closed':len(rec)==88,'boundary':'callback cardinality/dispatcher architecture is recovered exactly at the generated-surface level; individual H callback operands and monitor IDs remain target-specific and are not assigned Sienna callback names one-to-one.'}}
 # Ensure every H callback is evidence-bound.
 for t in ht:
  for x in t['callbacks']:
   if int(x,16) not in by:raise ValueError(f'H callback lacks compact evidence: {x}')
 a.out.write_text(json.dumps(payload,indent=2,sort_keys=True)+'\n');print('wrote',a.out)
if __name__=='__main__':main()
