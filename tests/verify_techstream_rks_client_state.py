#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json,struct,subprocess,sys,tempfile
from pathlib import Path
import pefile
REPO=Path(__file__).resolve().parents[1]; CUW=REPO/'Techstream/unpacked/toyota/Toyota Diagnostics/Calibration Update Wizard'; ART=REPO/'data/generated/techstream_v18/rks_client_state.json'
p=f=0; oracle='raw_bytes'
def check(n,c,d=''):
 global p,f
 ok=bool(c);p+=ok;f+=not ok;print(f"[{'PASS' if ok else 'FAIL'}][{oracle}] {n}"+(f' ({d})' if d else ''))
if not CUW.is_dir(): print('[SKIP] V18 unavailable');raise SystemExit(77)
obj=json.loads(ART.read_text()); data=(CUW/'Cuw.exe').read_bytes(); pe=pefile.PE(data=data); base=pe.OPTIONAL_HEADER.ImageBase
print('== Delphi method table -> exact handlers ==')
for h in obj['ui_handlers']:
 off=data.find(h['name'].encode()); ptr=struct.unpack_from('<I',data,off-5)[0] if off>=5 else 0
 check(h['name'],off>=5 and data[off-1]==len(h['name']) and ptr==h['va']==h['method_table_va'],hex(ptr))
print('\n== pinned native bodies ==')
for r in obj['function_identities']:
 check(r['role'],hashlib.sha256(pe.get_data(r['va']-base,r['size'])).hexdigest()==r['sha256'])
print('\n== managed field mapping / validity ==')
wrapper=subprocess.check_output([sys.executable,str(REPO/'tools/techstream/inspect_dotnet_il.py'),str(CUW/'CUWAccessRKSWrapper.dll'),'--type','<Module>','--method','SetDataForReproKey'],text=True)
for x in obj['request_fields']:
 token='ldarg.0' if x['wrapper_offset']==0 else None
 off=x['wrapper_offset']
 if off:
  if off == 3:
   token='ldc.i4.3'
  else:
   token=('ldc.i4.s       0x%02x'%off) if off<0x80 else ('ldc.i4         0x%x'%off)
 check(f"managed mapping {x['name']}",x['name'] in wrapper and (token in wrapper if token else True))
check('IsStored set true in wrapper','ldc.i4.1' in wrapper and 'set_mblnIsStored' in wrapper)
managed=subprocess.check_output([sys.executable,str(REPO/'tools/techstream/inspect_dotnet_il.py'),str(CUW/'CUWAccessRKS.dll'),'--type','CUWAccessRKS.AccessRKS','--method','ImportReproKey'],text=True)
check('managed file import requires XML Signature element',"ldstr          'Signature'" in managed)
check('managed file import requires 0x200 chars','ldc.i4         0x200' in managed)
check('managed file import requires alphanumeric regex',"'^[0-9a-zA-Z]+$'" in managed)
print('\n== native request builder/state anchors ==')
# Native wrapper data starts at object+0x215. The SetDataForReproKey offsets above
# therefore pin the full native layout independently of decompiler variable names.
check('native field offsets = base 0x215 + managed offsets',all(x['native_offset']==0x215+x['wrapper_offset'] for x in obj['request_fields']))
# Exact native fixed-width check and success/failure state setter/getter.
check('native 0x200 length compare',pe.get_data(0x480021-base,6)==b'\x81\xfa\x00\x02\x00\x00')
check('controller state setter/getter are +4 byte accessors',pe.get_data(0x4801c0-base,8)==bytes.fromhex('885004c38a4004c3'))
# Both import-next VCL handlers call the same shared 0x49c304 routine.
for va,name in [(0x49c2c0,'online import Next'),(0x49cd24,'offline import Next')]:
 body=pe.get_data(va-base,68); target=0x49c304; found=False
 for i,b in enumerate(body[:-4]):
  if b==0xe8:
   rel=struct.unpack_from('<i',body,i+1)[0]
   if va+i+5+rel==target: found=True
 check(f'{name} converges at shared importer',found)
# Request struct builder must be reached after the known config/VIN setup.
body=pe.get_data(0x49bcfe-base,989)
def has_call(target):
 for i,b in enumerate(body[:-4]):
  if b==0xe8 and 0x49bcfe+i+5+struct.unpack_from('<i',body,i+1)[0]==target:return True
 return False
check('RKS builder uses config object',has_call(0x43dfbc))
check('RKS builder sends native request object to wrapper',has_call(0x47fb24))
print('\n== shipped UI policy boundary ==')
# Regional catalogs retain the English msgids even when the en catalog is sparse.
mo=(CUW/'locale/no/LC_MESSAGES/default.mo').read_bytes()
for s in [b'Refer to the repair manual whether the target vehicle needs Signature Request.',b'If Signature Request is not necessary, press "No" to continue reprogramming.',b'Press "Offline" to perform offline Signature Request.']:
 check('locale: '+s.decode(),s in mo)
print('\n== deterministic regeneration ==')
with tempfile.TemporaryDirectory() as td:
 out=Path(td)/'x.json';r=subprocess.run([sys.executable,str(REPO/'tools/techstream/generate_rks_client_state.py'),'--output',str(out)],check=False)
 check('generator exits',r.returncode==0);check('byte-identical regeneration',out.read_bytes()==ART.read_bytes())
print(f'\nResults: {p} passed, {f} failed');raise SystemExit(1 if f else 0)
