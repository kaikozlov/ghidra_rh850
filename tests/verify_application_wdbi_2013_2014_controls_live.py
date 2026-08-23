#!/usr/bin/env python3
"""Run the application WDBI-2013/2014 control-cone assertion on the live project."""
from __future__ import annotations
import argparse, subprocess, tempfile
from pathlib import Path

REPO=Path(__file__).resolve().parents[1]
PROGRAM='RH850_P1M-E_CodeFlash.bin'
EXPECTED=('ASSERT application-wdbi-2013-2014-controls: states=17 direct_actuation_refs=0 '
          'direct_actuation_calls=0 staging_mirrors_without_readers=4 unexpected=0')

def main()->int:
    p=argparse.ArgumentParser(); p.add_argument('--project-dir',type=Path,default=REPO/'build/work/project'); a=p.parse_args()
    project=a.project_dir.resolve()
    if not (project/'rh850_p1me_mapped.rep').is_dir():
        print(f'[FAIL] live WDBI-2013/2014 controls: missing project {project}'); return 1
    with tempfile.TemporaryDirectory(prefix='wdbi-2013-2014-') as d:
        log=Path(d)/'headless.log'
        r=subprocess.run([
            str(REPO/'tools/run_headless'),'--project-dir',str(project),'--project','rh850_p1me_mapped',
            '--label','application-wdbi-2013-2014-controls','--log',str(log),'--quiet','--',
            '-process',PROGRAM,'-noanalysis','-readOnly','-postScript','AssertApplicationWdbi2013And2014Controls.java'],
            cwd=REPO,text=True,capture_output=True)
        out=log.read_text(errors='replace') if log.exists() else ''
        if r.returncode or EXPECTED not in out:
            print('[FAIL] live WDBI-2013/2014 control-cone assertion')
            print((r.stdout or '')+(r.stderr or '')+out[-6000:]); return 1
    print('[PASS] live WDBI-2013/2014 controls: exact state topology; no direct d/q/PWM join')
    return 0
if __name__=='__main__': raise SystemExit(main())
