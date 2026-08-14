#!/usr/bin/env python3
"""Run SID-0xBA topology and actuation-boundary assertions on the live project."""
from __future__ import annotations
import argparse,subprocess,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; PROGRAM='RH850_P1M-E_CodeFlash.bin'
EXPECTED='ASSERT application-proprietary-ba: starts=10 completions=10 marker_readers=2 countdown_readers=1 vspda_snapshot_readers=1 cone_functions=41 direct_actuation_refs=0 unexpected=0'
def main():
 p=argparse.ArgumentParser();p.add_argument('--project-dir',type=Path,default=ROOT/'build/project');a=p.parse_args();project=a.project_dir.resolve()
 if not (project/'rh850_p1me_mapped.rep').is_dir(): print(f'[FAIL] live BA surface: missing project {project}');return 1
 with tempfile.TemporaryDirectory(prefix='ba-surface-') as d:
  log=Path(d)/'headless.log';r=subprocess.run([str(ROOT/'tools/run_headless'),'--project-dir',str(project),'--project','rh850_p1me_mapped','--label','application-proprietary-ba','--log',str(log),'--quiet','--','-process',PROGRAM,'-noanalysis','-readOnly','-postScript','AssertApplicationProprietaryBaSurface.java'],cwd=ROOT,text=True,capture_output=True)
  out=log.read_text(errors='replace') if log.exists() else ''
  if r.returncode or EXPECTED not in out:
   print('[FAIL] live BA surface');print((r.stdout or '')+(r.stderr or '')+out[-8000:]);return 1
 print('[PASS] live BA surface: exact descriptor ownership, authorization readers, VSPDA separation, no direct conditioned-command/dq join');return 0
if __name__=='__main__': raise SystemExit(main())
