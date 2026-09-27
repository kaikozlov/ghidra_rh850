#!/usr/bin/env python3
"""Run remaining RoutineControl topology assertions on the live project."""
from __future__ import annotations
import argparse, subprocess, tempfile
from pathlib import Path
from tools import REPO_ROOT
REPO=REPO_ROOT
PROGRAM='RH850_P1M-E_CodeFlash.bin'
EXPECTED='ASSERT application-routine-remaining-controls'
def main():
 p=argparse.ArgumentParser(); p.add_argument('--project-dir',type=Path,default=REPO/'build/work/project'); a=p.parse_args(); project=a.project_dir.resolve()
 if not (project/'rh850_p1me_mapped.rep').is_dir(): print(f'[FAIL] live remaining RoutineControl controls: missing project {project}'); return 1
 with tempfile.TemporaryDirectory(prefix='routine-remaining-') as d:
  log=Path(d)/'headless.log'
  r=subprocess.run([str(REPO/'tools/project/run_headless'),'--project-dir',str(project),'--project','rh850_p1me_mapped','--label','routine-remaining-controls','--log',str(log),'--quiet','--','-process',PROGRAM,'-noanalysis','-readOnly','-postScript','AssertApplicationRoutineRemainingControls.java'],cwd=REPO,text=True,capture_output=True)
  out=log.read_text(errors='replace') if log.exists() else ''
  if r.returncode or EXPECTED not in out:
   print('[FAIL] live remaining RoutineControl controls'); print((r.stdout or '')+(r.stderr or '')+out[-6000:]); return 1
 print('[PASS] live RoutineControl remainder: exact op2/mode/thunk ownership; no direct conditioned-command/dq join'); return 0
if __name__=='__main__': raise SystemExit(main())
