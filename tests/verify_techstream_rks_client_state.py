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
print('\n== RKS SeedValue producer chain (static closure) ==')
# The whole producer is static Cuw.exe code: registration -> globals -> invoker
# thunk -> CentralGW P5-CAN SecurityAccess 27 21 seed -> callback -> 27 22 || token[256].
for r in obj['raw_anchors']:
 raw=pe.get_data(r['va']-base,r['len'])
 check('anchor '+r['name'],raw.hex()==r['hex'],f"{r['va']:#x}={raw.hex()}")
for c in obj['call_anchors']:
 o=pe.get_offset_from_rva(c['va']-base); op=data[o]
 dest=c['va']+5+struct.unpack_from('<i',data,o+1)[0] if op==0xE8 else 0
 check('call '+c['name'],op==0xE8 and dest==c['target'],f"{c['va']:#x}->{dest:#x}")
for s in obj['string_anchors']:
 o=pe.get_offset_from_rva(s['va']-base); got=data[o:data.find(b'\0',o)]
 check('string '+s['name'],got.decode()==s['value'],repr(got))
# Invoker thunk must reference the seed/token globals and the callback-code global.
thunk=pe.get_data(0x590858-base,0x1C)
for imm,nm in [(bytes.fromhex('ec9c6200'),'token buf 0x629CEC'),(bytes.fromhex('dc9c6200'),'seed buf 0x629CDC'),
               (bytes.fromhex('d49c6200'),'callback self 0x629CD4'),(bytes.fromhex('d09c6200'),'callback code 0x629CD0')]:
 check('thunk references '+nm,imm in thunk)
def off(va): return pe.get_offset_from_rva(va-base)
# CentralGW SecurityAccess grammar: 27 21/67 21 then 27 22||token[0x100] (len 0x107)/67 22,
# with the 7F 27 {13,35,36} negative gate.
check('request 27 21 + expected 67 21',data[off(0x590364)+6]==0x27 and data[off(0x590364)+13]==0x21 and data[off(0x590392)+6]==0x67 and data[off(0x590392)+13]==0x21)
check('send-key 27 22 + expected 67 22',data[off(0x5904a4)+6]==0x27 and data[off(0x5904a4)+13]==0x22 and data[off(0x5904ea)+6]==0x67 and data[off(0x5904ea)+13]==0x22)
check('token copy is 0x100 bytes and request length 0x107',struct.unpack_from('<I',data,off(0x5904b2)+1)[0]==0x100 and struct.unpack_from('<I',data,off(0x5904d3)+6)[0]==0x107)
check('seed record copy is 0x10 bytes',data[off(0x5903f6)]==0x6A and data[off(0x5903f6)+1]==0x10)
check('NRC gate is 7F 27 with 13/35/36',data[off(0x59056d)+2]==0x7F and data[off(0x59057a)+2]==0x27 and sorted(data[off(x)+2] for x in (0x590587,0x59058c,0x590591))==[0x13,0x35,0x36])
print('\n== shipped RKS.ini provenance ==')
# Ini/RKS.ini is obfuscated per-nibble: n -> 0x20+4n, two chars per byte.
ini=(CUW/'Ini/RKS.ini').read_bytes()
dec=bytearray()
for i in range(0,len(ini)-1,2):
 dec.append(((((ini[i]-0x20)&0xff)>>2)<<4)|(((ini[i+1]-0x20)&0xff)>>2))
dec=bytes(dec)
prov=obj['rks_ini_provenance']
check('RKS.ini sha256 pinned',hashlib.sha256(ini).hexdigest()==prov['sha256'])
check('RKS.ini decoded sha256 pinned',hashlib.sha256(dec).hexdigest()==prov['decoded_sha256'])
text=dec.decode('ascii','replace')
check('decoded ini is [ReproKeyRequest] plaintext','[ReproKeyRequest]' in text and 'InternetExplorerDownLoadURL' in text)
fields=dict(l.split('=',1) for l in text.replace('\r\n','\n').split('\n') if '=' in l and not l.startswith('['))
check('RequesterKind=0 (shipped)',fields.get('RequesterKind')=='0' and prov['decoded_section_fields']['RequesterKind']=='0')
check('KeypairID=RK0001 (shipped)',fields.get('KeypairID')=='RK0001' and prov['decoded_section_fields']['KeypairID']=='RK0001')
check('loader strings present in Cuw.exe',b'Ini\\RKS.ini\0' in data and b'ReproKeyRequest\0' in data)
check('config accessors return +0x18/+0x1C',pe.get_data(0x43f06c-base,11)==bytes.fromhex('558bec8b450883c0185dc3') and pe.get_data(0x43f078-base,11)==bytes.fromhex('558bec8b450883c01c5dc3'))
check('SeedValue native source is the 27 21 seed chain', '27 21' in obj['request_fields'][-1]['source'] and '0x629CDC' in obj['request_fields'][-1]['source'])
print('\n== static boundary statement ==')
sb=obj['static_boundary']
check('no missing producer code claimed',sb['producer'].startswith('fully recovered'))
check('external residues are seed value + server key only',[x for x in sb['external_residues'] if 'seed VALUE' in x or 'private key' in x].__len__()==2)
check('IsStored semantics preserved','validity flag' in obj['managed_mapping']['is_stored'] and 'cached server token' in obj['managed_mapping']['is_stored'])
print('\n== deterministic regeneration ==')
with tempfile.TemporaryDirectory() as td:
 out=Path(td)/'x.json';r=subprocess.run([sys.executable,str(REPO/'tools/techstream/generate_rks_client_state.py'),'--output',str(out)],check=False)
 check('generator exits',r.returncode==0);check('byte-identical regeneration',out.read_bytes()==ART.read_bytes())
print(f'\nResults: {p} passed, {f} failed');raise SystemExit(1 if f else 0)
