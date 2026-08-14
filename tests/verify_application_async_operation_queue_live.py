#!/usr/bin/env python3
from __future__ import annotations
import argparse, subprocess, tempfile
from pathlib import Path
REPO=Path(__file__).resolve().parents[1]; PROGRAM='RH850_P1M-E_CodeFlash.bin'
EXPECTED=('ASSERT application-async-operation-queue: operations=5 values=1,2,4,5,6 '
          'op3=absent diagnostic_owned=4 internal_owned=1 op4_selectorless=1 unexpected=0')
def main():
 p=argparse.ArgumentParser(); p.add_argument('--project-dir',type=Path,default=REPO/'build/project'); a=p.parse_args(); project=a.project_dir.resolve()
 if not (project/'rh850_p1me_mapped.rep').is_dir(): print(f'[FAIL] live async queue: missing project {project}'); return 1
 with tempfile.TemporaryDirectory(prefix='async-queue-') as d:
  log=Path(d)/'headless.log'
  r=subprocess.run([str(REPO/'tools/run_headless'),'--project-dir',str(project),'--project','rh850_p1me_mapped','--label','application-async-operation-queue','--log',str(log),'--quiet','--','-process',PROGRAM,'-noanalysis','-readOnly','-postScript','AssertApplicationAsyncOperationQueue.java'],cwd=REPO,text=True,capture_output=True)
  out=log.read_text(errors='replace') if log.exists() else ''
  if r.returncode or EXPECTED not in out:
   print('[FAIL] live async operation queue assertion'); print((r.stdout or '')+(r.stderr or '')+out[-6000:]); return 1
 print('[PASS] live async queue: five-operation ownership/xref topology exact; op3 absent; op4 internal')
 return 0
if __name__=='__main__': raise SystemExit(main())
