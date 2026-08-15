#!/usr/bin/env python3
"""Run the XCP shadow-write consumer boundary against the live Ghidra project."""
from __future__ import annotations
import argparse, subprocess, tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
PROGRAM='RH850_P1M-E_CodeFlash.bin'
EXPECTED='ASSERT xcp-shadow-write-boundary: block=LocalRAM bytes=32768 read=true write=true execute=false refs=3 writes=3 reads=0 params=0 calls=0 other=0 functions=0 unexpected=0'
def main()->int:
    p=argparse.ArgumentParser(); p.add_argument('--project-dir',type=Path,default=ROOT/'build/project'); a=p.parse_args()
    project=a.project_dir.resolve()
    if not (project/'rh850_p1me_mapped.rep').is_dir():
        print(f'[FAIL] XCP shadow write live: missing project {project}'); return 1
    with tempfile.TemporaryDirectory(prefix='xcp-shadow-write-') as d:
        log=Path(d)/'headless.log'
        r=subprocess.run([str(ROOT/'tools/run_headless'),'--project-dir',str(project),'--project','rh850_p1me_mapped','--label','xcp-shadow-write','--log',str(log),'--quiet','--','-process',PROGRAM,'-noanalysis','-readOnly','-postScript','AssertXcpShadowWriteBoundary.java'],cwd=ROOT,text=True,capture_output=True)
        out=log.read_text(errors='replace') if log.exists() else ''
        if r.returncode or EXPECTED not in out:
            print('[FAIL] XCP shadow write live'); print((r.stdout or '')+(r.stderr or '')+out[-10000:]); return 1
    print('[PASS] XCP shadow write live: RW/non-exec window; exact 3 WRITE refs; no function-owned READ/PARAM/callback consumer')
    return 0
if __name__=='__main__': raise SystemExit(main())
