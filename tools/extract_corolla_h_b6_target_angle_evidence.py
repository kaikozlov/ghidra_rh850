#!/usr/bin/env python3
"""Promote exact H decompiler evidence for the B6 target-angle ingress chain."""
from __future__ import annotations
import argparse, json
from pathlib import Path
from corolla_h_constants import CODEFLASH as H_CODEFLASH

from decompiler_evidence import bind_entries, load_function_corpus, sha256_bytes

REPO = Path(__file__).resolve().parents[1]
IMAGE = H_CODEFLASH
OUT = REPO / "data/generated/corolla_8965H1202000_b6_target_angle_decompiler_evidence.json"
ENTRIES = [
    0x42676, 0x4636A, 0x46A10, 0x5262C, 0x638AA,
    0xB23A2, 0xB24D0, 0xB8EEC,
    0xC825A, 0xC86E8, 0xC87FC, 0xC9CEA, 0xC9DB0, 0xC9E54, 0xC9ED0, 0xCBE6E,
    0xCBD7E, 0xCB096, 0xCA138, 0xCB4F4,
    0xCAC24, 0xCA940, 0xCAD1C,
    0xCC7F8, 0xCC18E, 0xCC442, 0xCBFCE, 0xCC2EC, 0xCAD62,
    0xC9C16, 0xCB8BA, 0xCB9B6, 0xCD3CC, 0xCD440, 0xCD496, 0xCD53E, 0xCD55A, 0xCD5DC, 0xCE928, 0xCE974, 0xCEDAE,
]

def sha(b: bytes) -> str: return sha256_bytes(b)

def main() -> int:
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--image',type=Path,default=IMAGE)
    ap.add_argument('--corpus',type=Path,required=True,help='disposable corrected-context H decompiler corpus JSONL')
    ap.add_argument('--out',type=Path,default=OUT)
    a=ap.parse_args(); image=a.image.read_bytes()
    if len(image)!=0x100000: raise SystemExit(f'expected 1 MiB CodeFlash, got {len(image):#x}')
    rows,_=load_function_corpus(a.corpus)
    funcs=bind_entries(image,rows,ENTRIES,include_data_references=False,include_body_ranges=False,honor_body_ranges=False)
    out={
      'schema':'corolla-h-b6-target-angle-decompiler-evidence-v1','software_id':'8965H1202000',
      'image':{'path':str(a.image.resolve().relative_to(REPO.resolve())) if a.image.resolve().is_relative_to(REPO.resolve()) else str(a.image),'size':len(image),'sha256':sha(image)},
      'source_corpus':{'path':str(a.corpus.resolve().relative_to(REPO.resolve())) if a.corpus.resolve().is_relative_to(REPO.resolve()) else str(a.corpus),'sha256':sha(a.corpus.read_bytes())},
      'function_count':len(funcs),'functions':funcs,
      'boundary':'Target-native H decompiler observations for the B6 mode+signed16 target-angle ingress, exact FD025 coarse+fraction angle representation, measured-angle comparator, downstream steering conditioner, and handoff into the general command-torque chain. Raw body hashes bind all pseudocode to exact 8965H1202000 bytes.'
    }
    a.out.parent.mkdir(parents=True,exist_ok=True); a.out.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n'); print(f'wrote {a.out}: {len(funcs)} functions'); return 0
if __name__=='__main__': raise SystemExit(main())
