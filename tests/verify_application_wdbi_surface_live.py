#!/usr/bin/env python3
"""Execute the true application WDBI surface assertion on the live project."""
from __future__ import annotations
import argparse, subprocess, tempfile
from pathlib import Path

REPO=Path(__file__).resolve().parents[1]
PROGRAM="RH850_P1M-E_CodeFlash.bin"
EXPECTED="ASSERT application-wdbi-surface: implemented=13 speed_gated=12 no_speed_gate=2012 persistent_nvm_dids=8 live_override_refs=7 control_parameter_refs=4 control_mode_refs=5 unexpected=0"

def main()->int:
    p=argparse.ArgumentParser(); p.add_argument('--project-dir',type=Path,default=REPO/'build/work/project'); a=p.parse_args()
    project=a.project_dir.resolve()
    if not (project/'rh850_p1me_mapped.rep').is_dir():
        print(f"[FAIL] live WDBI surface: missing project {project}"); return 1
    with tempfile.TemporaryDirectory(prefix='wdbi-surface-') as d:
        log=Path(d)/'headless.log'
        r=subprocess.run([
            str(REPO/'tools/run_headless'),'--project-dir',str(project),'--project','rh850_p1me_mapped',
            '--label','application-wdbi-surface','--log',str(log),'--quiet','--',
            '-process',PROGRAM,'-noanalysis','-readOnly','-postScript','AssertApplicationWdbiSurface.java'],
            cwd=REPO,text=True,capture_output=True)
        out=log.read_text(errors='replace') if log.exists() else ''
        if r.returncode or EXPECTED not in out:
            print('[FAIL] live WDBI surface assertion')
            print((r.stdout or '')+(r.stderr or '')+out[-4000:]); return 1
    print('[PASS] live WDBI surface: 13 callbacks; 2012/2013/2014 xref topologies exact')
    return 0
if __name__=='__main__': raise SystemExit(main())
