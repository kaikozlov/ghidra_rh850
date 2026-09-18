#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json, shutil, subprocess, sys, tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
sys.path.insert(0,str(ROOT))
BUILDER=ROOT/'exploit/ephemeral_runtime/build_camry_f33_early030_discriminator.py'
LAUNCHER=ROOT/'exploit/ephemeral_runtime/camry_f33_early030_launcher.sh'
RUNTIME=(
 'exploit/common/ram_exec.py',
 'exploit/ephemeral_runtime/camry_f33_early030_bootstrap_probe.py',
 'exploit/ephemeral_runtime/tss3_unified_b6_signer.py',
 'exploit/ephemeral_runtime/camry_f33_runtime_monitor.py',
 'exploit/ephemeral_runtime/camry_f33_runtime_replay_discriminator.py',
 'exploit/ephemeral_runtime/f33_panda_lease.sh',
 'tsk/__init__.py','tsk/lib/__init__.py','tsk/lib/programming.py','tsk/lib/diagnostic_route.py',
)
def cp(src,dst): dst.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(src,dst)
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def main()->int:
 ap=argparse.ArgumentParser(); ap.add_argument('--out',type=Path,required=True); a=ap.parse_args()
 if a.out.exists() and any(a.out.rglob('*')): ap.error('output directory not empty')
 with tempfile.TemporaryDirectory(prefix='early030-kit-') as td:
  b=Path(td)/'bundle'; b.mkdir()
  subprocess.run([sys.executable,str(BUILDER),'--output-dir',str(b)],cwd=ROOT,check=True,capture_output=True,text=True)
  a.out.mkdir(parents=True,exist_ok=True)
  for p in b.iterdir(): cp(p,a.out/'bundle'/p.name)
 for rel in RUNTIME: cp(ROOT/rel,a.out/'runtime'/rel)
 cp(LAUNCHER,a.out/'camry-f33-early030'); (a.out/'camry-f33-early030').chmod(0o755)
 commit=subprocess.run(['git','rev-parse','HEAD'],cwd=ROOT,check=True,capture_output=True,text=True).stdout.strip()
 (a.out/'SOURCE_COMMIT').write_text(commit+'\n')
 meta=json.loads((a.out/'bundle/camry_f33_early030.json').read_text())
 manifest={'schema':'camry-f33-early030-kit-v1','source_commit':commit,'target':meta['target'],'files':{str(p.relative_to(a.out)):{'size':p.stat().st_size,'sha256':sha(p)} for p in sorted(a.out.rglob('*')) if p.is_file()}}
 (a.out/'manifest.json').write_text(json.dumps(manifest,indent=2,sort_keys=True)+'\n')
 print(json.dumps(manifest,indent=2,sort_keys=True)); return 0
if __name__=='__main__': raise SystemExit(main())
