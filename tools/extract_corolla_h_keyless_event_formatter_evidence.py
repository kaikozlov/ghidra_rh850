#!/usr/bin/env python3
"""Compact target-native Corolla-H evidence for the keyless event-formatter re-audit."""
from __future__ import annotations
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
RAW=ROOT/'community/albinoelephant/raw-20260818/albinoelephant-corolla-2023.20260814-0023/dump_codeflash_00000000_00200000_20260814-025814.bin'
SRC=ROOT/'build/work/corpora/h_8965H1202000_keyless_event_formatter_decompilations.jsonl'
OUT=ROOT/'data/generated/corolla_8965H1202000_keyless_event_formatter_decompiler_evidence.json'
TARGETS=[0x50038,0x50122,0x501A6,0x5031A,0x50D10,0x87384]
def sha(b:bytes)->str:return hashlib.sha256(b).hexdigest()
def main()->None:
 raw=RAW.read_bytes()[:0x100000]; rows={}
 for line in SRC.read_text().splitlines():
  r=json.loads(line); rows[int(r['entry_addr'],16)]=r
 out=[]
 for a in TARGETS:
  r=rows.get(a)
  if not r or not r.get('decompile_completed') or not r.get('decompiled_c'): raise SystemExit(f'missing target-native decompilation {a:#x}')
  n=int(r['body_size']); c=r['decompiled_c']
  out.append({'entry':f'0x{a:08X}','name':r.get('name',f'FUN_{a:08x}'),'body_size':n,'body_sha256':sha(raw[a:a+n]),'decompiled_c_sha256':sha(c.encode()),'decompiled_c':c})
 payload={'schema':'corolla-h-keyless-event-formatter-evidence-v1','software_id':'8965H1202000','image':{'path':str(RAW.relative_to(ROOT)),'codeflash_size':len(raw),'codeflash_sha256':sha(raw)},'source_corpus':{'path':str(SRC.relative_to(ROOT)),'sha256':sha(SRC.read_bytes()),'boundary':'six target-native functions recovered from the disposable H Ghidra project; downstream verification consumes only this compact image-bound evidence'},'functions':out,'function_count':len(out),'boundary':'This artifact establishes the H formatter/wrapper/sibling/config helper and AB worker semantics. Reachable output bounds remain a separate deterministic raw-table calculation.'}
 OUT.write_text(json.dumps(payload,indent=2,sort_keys=True)+'\n'); print(f'wrote {OUT}: {len(out)} functions')
if __name__=='__main__':main()
