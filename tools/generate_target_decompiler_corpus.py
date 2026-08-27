#!/usr/bin/env python3
"""Generate a provenance-locked canonical decompiler corpus for a registered non-default target."""
from __future__ import annotations
import argparse, hashlib, json, os, subprocess, sys, tempfile
from pathlib import Path
from typing import Any

REPO=Path(__file__).resolve().parents[1]
BUILD=REPO/'build'; BUILD_WORK=BUILD/'work'; BUILD_LOGS=BUILD/'logs'; BUILD_TMP=BUILD/'tmp'
EXPORTER=REPO/'ghidra/scripts/verify/ExportDecompilerCorpus.java'

def sha(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()
def registry_target(name:str)->dict:
    o=json.loads((REPO/'data/analysis_targets.json').read_text())
    if name==o['default_target']: raise SystemExit('use tools/generate_decompiler_corpus.py for the default Sienna target')
    try:return o['targets'][name]
    except KeyError:raise SystemExit(f'unknown analysis target: {name}')
def run(cmd:list[str],env=None):
    r=subprocess.run(cmd,cwd=REPO,env=env,capture_output=True,text=True)
    if r.returncode: raise SystemExit(f"command failed ({r.returncode}): {' '.join(cmd)}\n{r.stdout}\n{r.stderr}")
    return r
def load_inventory(path:Path):
    meta=None; funcs={}; totals=None
    for line in path.read_text().splitlines():
        r=json.loads(line); k=r['record']
        if k=='meta':meta=r
        elif k=='function': funcs[f"0x{int(r['entry']['offset'],16):08x}"]=r
        elif k=='totals':totals=r
    if meta is None or totals is None or totals['functions']!=len(funcs): raise SystemExit('invalid target inventory baseline')
    return meta,funcs,totals
def canonicalize(raw:Path,inv:dict[str,dict[str,Any]]):
    out=[]; seen=set(); errors=[]; failures=[]
    for n,line in enumerate(raw.read_text().splitlines(),1):
        r=json.loads(line); e=r.get('entry_addr')
        if e not in inv: errors.append(f'line {n}: unexpected entry {e}'); continue
        if e in seen: errors.append(f'duplicate {e}'); continue
        seen.add(e); x=inv[e]
        for got,want,label in [(r.get('address_space'),x['entry']['space'],'space'),(r.get('body_size'),x['body_address_count'],'body size'),(r.get('is_thunk'),x['is_thunk'],'thunk'),(r.get('calling_convention'),x['calling_convention'],'calling convention')]:
            if got!=want: errors.append(f'{e}: {label} {got!r} != {want!r}')
        if x['user_name'] is not None and r.get('name')!=x['user_name']: errors.append(f"{e}: name {r.get('name')!r} != {x['user_name']!r}")
        code=str(r.get('decompiled_c','')).replace('\r\n','\n').replace('\r','\n')
        if r.get('decompile_completed') is not True or not code.strip(): failures.append(e)
        refs=[]
        for q in r.get('data_references',[]):
            try: refs.append({'from_addr':f"0x{int(q['from_addr'],16):08x}",'to_addr':f"0x{int(q['to_addr'],16):08x}",'to_space':str(q['to_space']),'ref_type':str(q['ref_type']),'operand_index':int(q['operand_index'])})
            except Exception as ex: errors.append(f'{e}: invalid reference: {ex}')
        refs.sort(key=lambda q:(int(q['from_addr'],16),int(q['to_addr'],16),q['to_space'],q['ref_type'],q['operand_index']))
        ranges=[{'min':f"0x{int(z['min']['offset'],16):08x}",'max':f"0x{int(z['max']['offset'],16):08x}",'space':z['min']['space']} for z in x['body_ranges']]
        out.append({'record':'function','entry_addr':e,'address_space':r.get('address_space'),'name':r.get('name'),'signature':r.get('signature'),'calling_convention':r.get('calling_convention'),'body_size':r.get('body_size'),'body_ranges':ranges,'is_thunk':r.get('is_thunk'),'decompile_completed':True,'decompile_error':'','data_references':refs,'decompiled_c_sha256':hashlib.sha256(code.encode()).hexdigest(),'decompiled_c':code})
    missing=sorted(set(inv)-seen)
    if missing:errors.append(f'missing {len(missing)} inventory functions')
    if errors:raise SystemExit('target corpus identity errors:\n  '+'\n  '.join(errors[:30]))
    if failures:raise SystemExit(f'{len(failures)} target functions failed to decompile: {failures[:20]}')
    return sorted(out,key=lambda r:int(r['entry_addr'],16))
def main()->int:
    ap=argparse.ArgumentParser(description=__doc__); ap.add_argument('--target',required=True); ap.add_argument('--project-dir',type=Path); ap.add_argument('--output',type=Path); ap.add_argument('--timeout-seconds',type=int,default=60); a=ap.parse_args()
    t=registry_target(a.target); project=(a.project_dir or REPO/t['work_dir']).expanduser().resolve(); work=BUILD_WORK.resolve(); committed=(REPO/'project').resolve()
    if project==work or work not in project.parents:raise SystemExit(f'refusing project outside build/work descendant: {project}')
    if project==committed or committed in project.parents:raise SystemExit(f'refusing committed snapshot project: {project}')
    pname=t['project_name']; prog=t['program_name'];
    if not (project/f'{pname}.rep').is_dir():raise SystemExit(f'missing target project: {project}/{pname}.rep')
    inv_path=(REPO/t['inventory_baseline']).resolve(); output=(a.output or REPO/t['decompiler_corpus']).resolve(); meta,funcs,totals=load_inventory(inv_path)
    env=os.environ.copy(); env['GHIDRA_ANALYSIS_TARGET']=a.target; env['GHIDRA_PROJECT']=str(project); env['PROJECT_DIR']=str(project)
    # Stop only this target bridge; then independently establish live inventory parity.
    run([str(REPO/'tools/g'),'stop'],env)
    BUILD_TMP.mkdir(parents=True,exist_ok=True); BUILD_LOGS.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=f'{a.target}-corpus-',dir=BUILD_TMP) as td:
        td=Path(td); live=td/'live_inventory.jsonl'; raw=td/'raw.jsonl'
        run([str(REPO/'tools/export_ghidra_project.sh'),'project-inventory',str(live)],env)
        run([sys.executable,str(REPO/'tools/project_inventory.py'),'compare',str(inv_path),str(live)])
        log=BUILD_LOGS/f'generate-{a.target}-decompiler-corpus.log'
        run([str(REPO/'tools/run_headless'),'--project-dir',str(project),'--project',pname,'--label',f'{a.target}-decompiler-corpus','--log',str(log),'--quiet','--','-process',prog,'-noanalysis','-readOnly','-postScript',EXPORTER.name,str(raw),str(a.timeout_seconds)],env)
        records=canonicalize(raw,funcs)
    metadata={'record':'metadata','schema_version':3,'analysis_target':a.target,'software_id':t['software_id'],'function_count':len(records),'decompiled_count':len(records),'failed_count':0,'decompiler_timeout_seconds':a.timeout_seconds,'project_inventory_path':inv_path.relative_to(REPO).as_posix(),'project_inventory_sha256':sha(inv_path),'generator_path':Path(__file__).resolve().relative_to(REPO).as_posix(),'generator_sha256':sha(Path(__file__).resolve()),'exporter_path':EXPORTER.relative_to(REPO).as_posix(),'exporter_sha256':sha(EXPORTER),'ghidra_version':meta['ghidra_version'],'program_name':meta['program_name'],'executable_sha256':meta['executable_sha256'],'language_id':meta['language_id'],'compiler_spec_id':meta['compiler_spec_id'],'inventory_function_count':totals['functions']}
    output.parent.mkdir(parents=True,exist_ok=True)
    with tempfile.NamedTemporaryFile('w',encoding='utf-8',newline='\n',dir=output.parent,prefix=f'.{output.name}.',delete=False) as f:
        tmp=Path(f.name)
        for r in [metadata,*records]: f.write(json.dumps(r,sort_keys=True,separators=(',',':'))+'\n')
    tmp.replace(output); output.chmod(0o644)
    print(f'Wrote {len(records)} canonical target decompilations to {output}')
    return 0
if __name__=='__main__':raise SystemExit(main())
