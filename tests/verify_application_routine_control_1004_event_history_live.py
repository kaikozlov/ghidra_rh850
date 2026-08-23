#!/usr/bin/env python3
from __future__ import annotations
import argparse, subprocess, tempfile
from pathlib import Path
REPO=Path(__file__).resolve().parents[1]; PROGRAM='RH850_P1M-E_CodeFlash.bin'
EXPECTED=('ASSERT application-routine-1004-event-history: op5_callers=2 op5_initializer_callers=1 '
          'event_initializer_callers=1 persist_worker_callers=1 history_persist_callers=1 '
          'selector3_refs=4 direct_actuation_refs=0 unexpected=0')
def main():
 p=argparse.ArgumentParser(); p.add_argument('--project-dir',type=Path,default=REPO/'build/work/project'); a=p.parse_args(); project=a.project_dir.resolve()
 if not (project/'rh850_p1me_mapped.rep').is_dir(): print(f'[FAIL] live RoutineControl 1004: missing project {project}'); return 1
 with tempfile.TemporaryDirectory(prefix='routine-1004-') as d:
  log=Path(d)/'headless.log'
  r=subprocess.run([str(REPO/'tools/run_headless'),'--project-dir',str(project),'--project','rh850_p1me_mapped','--label','routine-1004-event-history','--log',str(log),'--quiet','--','-process',PROGRAM,'-noanalysis','-readOnly','-postScript','AssertApplicationRoutine1004EventHistory.java'],cwd=REPO,text=True,capture_output=True)
  out=log.read_text(errors='replace') if log.exists() else ''
  if r.returncode or EXPECTED not in out:
   print('[FAIL] live RoutineControl 1004 event-history assertion'); print((r.stdout or '')+(r.stderr or '')+out[-6000:]); return 1
 print('[PASS] live RoutineControl 1004: op5/event-persist ownership exact; no direct conditioned-command/dq join'); return 0
if __name__=='__main__': raise SystemExit(main())
