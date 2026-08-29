#!/usr/bin/env python3
"""Emulate the CUWPlus CP loader for one protected 32-bit PE.

This is the low-level worker used by recover_cp_bodies.py. It models only
the Windows/NT surfaces exercised by the current Toyota CP protector and writes
a restored memory image plus structured provenance.
"""
from __future__ import annotations

import argparse
import json
import struct
from pathlib import Path
from unicorn import Uc, UC_ARCH_X86, UC_MODE_32, UC_HOOK_CODE, UC_HOOK_MEM_INVALID, UC_HOOK_MEM_WRITE, UC_PROT_ALL
from unicorn.x86_const import *
BASE=0x10000000; STACK=0x20000000; STACKSZ=0x100000; STUB=0x30000000; SIDECAR=0x31000000; SENTINEL=0x0badf00d
ap=argparse.ArgumentParser(description=__doc__)
ap.add_argument('stub', type=Path, help='protected .dll/.exe stub')
ap.add_argument('--output-dir', type=Path, required=True, help='worker output directory')
args=ap.parse_args()
stub_path=args.stub.resolve(); side_path=Path(str(stub_path)+'._')
rel=Path(stub_path.name)
stub=stub_path.read_bytes(); side=side_path.read_bytes()
def u16(b,o): return struct.unpack_from('<H',b,o)[0]
def u32(b,o): return struct.unpack_from('<I',b,o)[0]
def put32(b,o,x): struct.pack_into('<I',b,o,x&0xffffffff)
pe=u32(stub,0x3c); nsec=u16(stub,pe+6); opts=u16(stub,pe+20); opt=pe+24
size_image=u32(stub,opt+56); size_headers=u32(stub,opt+60); image_base=u32(stub,opt+28); original_entry=u32(stub,opt+16); sec0=opt+opts; is_managed=bool(u32(stub,opt+96+14*8))
BASE=image_base
sections=[]
for i in range(nsec):
 q=sec0+40*i; name=stub[q:q+8].split(b'\0')[0].decode('ascii','replace'); vs,va,rs,rp=struct.unpack_from('<IIII',stub,q+8); sections.append((name,vs,va,rs,rp))
print('PE',rel,hex(image_base),hex(size_image),'entry',hex(original_entry),sections)
img=bytearray(size_image); img[:min(size_headers,len(stub))]=stub[:min(size_headers,len(stub))]
for name,vs,va,rs,rp in sections: img[va:va+rs]=stub[rp:rp+rs]
imp_rva=u32(stub,opt+104)
def cstr_buf(buf,off):
 e=buf.find(b'\0',off); return buf[off:e].decode('ascii','replace')
api_by_addr={}; addr_by_api={}; next_stub=STUB+0x1000
imported_dlls=set()
if imp_rva:
 off=imp_rva
 while True:
  oft,ts,fc,name_rva,ft=struct.unpack_from('<IIIII',img,off)
  if not any((oft,ts,fc,name_rva,ft)): break
  dll=cstr_buf(img,name_rva); imported_dlls.add(dll.lower()); thunk=oft or ft; j=0
  while True:
   val=u32(img,thunk+4*j)
   if val==0: break
   name=f'#{val&0xffff}' if val&0x80000000 else cstr_buf(img,val+2); key=(dll.lower(),name)
   if key not in addr_by_api:
    addr_by_api[key]=next_stub; api_by_addr[next_stub]=key; next_stub+=0x10
   put32(img,ft+4*j,addr_by_api[key]); j+=1
  off+=20
print('imports',len(api_by_addr),sorted(api_by_addr.items())[:30])
uc=Uc(UC_ARCH_X86,UC_MODE_32); align=lambda x:(x+0xfff)&~0xfff
uc.mem_map(0,0x1000,UC_PROT_ALL); uc.mem_write(0,struct.pack('<I',0xffffffff)); uc.mem_map(BASE,align(size_image),UC_PROT_ALL); uc.mem_write(BASE,bytes(img)); uc.mem_map(STACK,STACKSZ,UC_PROT_ALL); uc.mem_map(STUB,0x10000,UC_PROT_ALL); uc.mem_map(SIDECAR,align(len(side)),UC_PROT_ALL); uc.mem_write(SIDECAR,side); RAWFILE=0x34000000; uc.mem_map(RAWFILE,align(max(len(stub),0x1000)),UC_PROT_ALL); uc.mem_write(RAWFILE,stub); uc.mem_map(0x32000000,0x1000000,UC_PROT_ALL); uc.mem_map(0x70000000,0x200000,UC_PROT_ALL); uc.mem_map(0x40000000,0x10000,UC_PROT_ALL); uc.mem_map(SENTINEL&~0xfff,0x1000,UC_PROT_ALL); uc.mem_write(SENTINEL,b'\xcc')
# Minimal 32-bit TEB/PEB/LDR chain.  Stage-1 updates this module's LDR
# EntryPoint after materializing stage 2.
TEB=0x40000000; PEB=0x40001000; LDR=0x40002000; LDR_ENTRY=0x40003000
uc.mem_write(TEB+0x30,struct.pack('<I',PEB))
uc.mem_write(PEB+0x0c,struct.pack('<I',LDR))
# Unicorn's 32-bit FS base is effectively zero on this host. Mirror the
# Windows TEB fields that direct FS loads expect into linear page zero.
uc.mem_write(0x18,struct.pack('<I',TEB))       # TEB.Self
uc.mem_write(0x30,struct.pack('<I',PEB))       # TEB.ProcessEnvironmentBlock
# InLoadOrderModuleList head at LDR+0x0c; one circular entry.
uc.mem_write(LDR+0x0c,struct.pack('<II',LDR_ENTRY,LDR_ENTRY))
uc.mem_write(LDR_ENTRY+0x00,struct.pack('<II',LDR+0x0c,LDR+0x0c))
uc.mem_write(LDR_ENTRY+0x18,struct.pack('<I',BASE))
uc.mem_write(LDR_ENTRY+0x1c,struct.pack('<I',BASE+original_entry))
uc.mem_write(LDR_ENTRY+0x20,struct.pack('<I',size_image))
# 32-bit LDR_DATA_TABLE_ENTRY FullDllName/BaseDllName UNICODE_STRINGs.
LDR_STR=0x40004000
full_name=('C:\\GTSPlus\\'+stub_path.name).encode('utf-16le')
base_name=stub_path.name.encode('utf-16le')
uc.mem_write(LDR_STR,full_name+b'\0\0')
base_ptr=LDR_STR+0x400
uc.mem_write(base_ptr,base_name+b'\0\0')
uc.mem_write(LDR_ENTRY+0x24,struct.pack('<HHI',len(full_name),len(full_name)+2,LDR_STR))
uc.mem_write(LDR_ENTRY+0x2c,struct.pack('<HHI',len(base_name),len(base_name)+2,base_ptr))
dyn_next=[next_stub]
alloc_next=[0x32000000]
last_error=[0]
stopped_reason=[None]
error_mode=[0]
mutexes={}
next_handle=[0x44441000]
module_handles={'kernel32.dll':0x70000000,'kernelbase.dll':0x70000000,'ntdll.dll':0x70100000}
for idx,nm in enumerate(sorted(imported_dlls - {'kernel32.dll','kernelbase.dll','ntdll.dll'})):
 module_handles[nm]=0x71000000 + idx*0x10000
handle_modules={0x70000000:'kernel32.dll',0x70100000:'ntdll.dll'}
for nm,h in module_handles.items():
 if h not in handle_modules: handle_modules[h]=nm
phase5c=[False]; phase5c_done=[False]; protector_success=[False]; capture_vprotect=[False]
current_module=[None]; current_module_ptr=[None]; pending_resolve=[None]
import_records=[]; protect_calls=[]; module_protect_calls=[]; restored_image=[None]; captured_entry=[None]; lfsr_addr=[None]
import_write_hook=[None]; initial_special_hook=[None]; lfsr_hook=[None]; ntqip_hook=[None]; entry_hook=[None]
synthetic_api_integrity_hook=[None]; synthetic_api_integrity_trusts=[]
file_handles={}
mapping_handles={}
file_offsets={}
def new_handle():
 h=next_handle[0]; next_handle[0]+=1; return h
def ensure_api(dll,name):
 key=(dll.lower(),name)
 if key not in addr_by_api: a=dyn_next[0]; dyn_next[0]+=0x10; addr_by_api[key]=a; api_by_addr[a]=key
 return addr_by_api[key]

def finalize_pending_resolve():
 rec=pending_resolve[0]
 if rec is None: return
 if rec.get('iat_rva') is None:
  if not (is_managed and rec['dll'].lower()=='mscoree.dll' and rec['name'] in ('_CorDllMain','_CorExeMain')):
   raise RuntimeError(f"did not observe IAT write for {rec['dll']}!{rec['name']}")
 import_records.append(rec); pending_resolve[0]=None

def install_minimal_ntdll():
 base=0x70100000; b=bytearray(0x3000)
 b[:2]=b'MZ'; struct.pack_into('<I',b,0x3c,0x80); b[0x80:0x84]=b'PE\0\0'
 struct.pack_into('<HHIIIHH',b,0x84,0x14c,1,0,0,0,0xe0,0x210e)
 o=0x98; struct.pack_into('<H',b,o,0x10b); struct.pack_into('<I',b,o+16,0); struct.pack_into('<I',b,o+20,0x1000); struct.pack_into('<I',b,o+24,0x1000)
 struct.pack_into('<I',b,o+28,base); struct.pack_into('<I',b,o+32,0x1000); struct.pack_into('<I',b,o+36,0x200)
 struct.pack_into('<I',b,o+56,0x3000); struct.pack_into('<I',b,o+60,0x200); struct.pack_into('<H',b,o+68,2); struct.pack_into('<I',b,o+92,16)
 struct.pack_into('<II',b,o+96,0x1000,0x200)
 sh=o+0xe0; b[sh:sh+8]=b'.edata\0\0'; struct.pack_into('<IIIIIIHHI',b,sh+8,0x1000,0x1000,0x1000,0x200,0,0,0,0,0x40000040)
 # IMAGE_EXPORT_DIRECTORY and one named export.
 struct.pack_into('<IIHHIIIIIII',b,0x1000,0,0,0,0,0x1080,1,1,1,0x1040,0x1044,0x1048)
 struct.pack_into('<I',b,0x1040,0x1800); struct.pack_into('<I',b,0x1044,0x1090); struct.pack_into('<H',b,0x1048,0)
 b[0x1080:0x108a]=b'ntdll.dll\0'; b[0x1090:0x109e]=b'RtlGetVersion\0'
 uc.mem_write(base,bytes(b)); api_by_addr[base+0x1800]=('ntdll.dll','RtlGetVersion')
install_minimal_ntdll()
esp=STACK+STACKSZ-0x1000; uc.mem_write(esp,struct.pack('<IIII',SENTINEL,BASE,1,0)); uc.reg_write(UC_X86_REG_ESP,esp); uc.reg_write(UC_X86_REG_EBP,0); uc.reg_write(UC_X86_REG_EIP,BASE+original_entry)
def rd32(a): return struct.unpack('<I',uc.mem_read(a,4))[0]
def wr32(a,v): uc.mem_write(a,struct.pack('<I',v&0xffffffff))
def read_c(a,limit=512):
 b=bytearray()
 for i in range(limit):
  c=uc.mem_read(a+i,1)[0]
  if c==0: break
  b.append(c)
 return b.decode('ascii','replace')
def read_w(a,limit=512):
 b=bytearray()
 for i in range(limit):
  w=bytes(uc.mem_read(a+2*i,2))
  if w==b'\0\0': break
  b += w
 return b.decode('utf-16le','replace')
def write_w(a,s,maxchars=260):
 raw=(s+'\0').encode('utf-16le')[:maxchars*2]; uc.mem_write(a,raw); return max(0,len(raw)//2-1)
def ret_stdcall(nargs,eax=1):
 e=uc.reg_read(UC_X86_REG_ESP); ret=rd32(e); uc.reg_write(UC_X86_REG_ESP,e+4+4*nargs); uc.reg_write(UC_X86_REG_EAX,eax&0xffffffff); uc.reg_write(UC_X86_REG_EIP,ret)
def _install_lfsr_hook() -> None:
 if lfsr_addr[0] is None or lfsr_hook[0] is not None:
  return
 def _hook(uc,a,size,user):
  e=uc.reg_read(UC_X86_REG_ESP); ret=rd32(e); buf=rd32(e+4); n=rd32(e+8)
  data=bytearray(uc.mem_read(buf,n)); dx=1
  for j in range(n):
   al=data[j]
   for bitpos in range(8):
    al ^= (dx & 1) << bitpos; dx=(dx << 1)&0xffff
    if dx & 0x8000: dx ^= 0x8003
   data[j]=al
  uc.mem_write(buf,bytes(data)); uc.reg_write(UC_X86_REG_ESP,e+4); uc.reg_write(UC_X86_REG_EIP,ret)
 lfsr_hook[0]=uc.hook_add(UC_HOOK_CODE,_hook,begin=lfsr_addr[0],end=lfsr_addr[0])

def _install_ntqip_hook() -> None:
 if ntqip_hook[0] is not None:
  return
 def _hook(uc,a,size,user):
  try:
   if bytes(uc.mem_read(a,16)) != b'\0'*16:
    return
   e=uc.reg_read(UC_X86_REG_ESP); ret=rd32(e); process=rd32(e+4); cls=rd32(e+8); buf=rd32(e+12); ln=rd32(e+16); retlen=rd32(e+20)
   if BASE <= ret < BASE+size_image and process in (0xffffffff,0xfffffffe) and cls in (7,30,31) and ln==4:
    if buf: wr32(buf, 1 if cls==31 else 0)
    if retlen: wr32(retlen,4)
    uc.reg_write(UC_X86_REG_EAX,0); uc.reg_write(UC_X86_REG_ESP,e+24); uc.reg_write(UC_X86_REG_EIP,ret)
    print(' NTQIP_LOCAL',hex(a-BASE),'class',cls,'buf',hex(buf),'len',ln)
  except Exception:
   return
 ntqip_hook[0]=uc.hook_add(UC_HOOK_CODE,_hook,begin=BASE,end=BASE+size_image-1)

def _install_entry_hook() -> None:
 if entry_hook[0] is not None:
  return
 text=next((x for x in sections if x[0]=='.text'),None)
 if text is None:
  return
 def _hook(uc,a,size,user):
  captured_entry[0]=a-BASE; stopped_reason[0]='original entry captured'; print(' ORIGINAL_ENTRY',hex(captured_entry[0])); uc.emu_stop()
 entry_hook[0]=uc.hook_add(UC_HOOK_CODE,_hook,begin=BASE+text[2],end=BASE+text[2]+text[1]-1)

def _arm_synthetic_api_integrity_trust(api_address):
 # Coree-managed EXEs run one protector integrity probe over GetProcAddress.
 # Synthetic emulator APIs are semantic callbacks, not byte-identical Windows
 # exports, so the probe cannot validate their prologues. Treat only our own
 # registered GetProcAddress trampoline as a known-clean export. Derive the
 # enclosing checker's return address from the live stack/code shape instead
 # of baking in a protector RVA.
 expected=addr_by_api.get(('kernel32.dll','GetProcAddress'))
 if not (is_managed and rel.suffix.lower()=='.exe' and 'gtspluscoree32.dll' in imported_dlls):
  return
 if expected is None or api_address != expected or synthetic_api_integrity_hook[0] is not None:
  return
 sp=uc.reg_read(UC_X86_REG_ESP); candidates=[]
 for i in range(8,96):
  try: candidate=rd32(sp+4*i)
  except Exception: break
  if not (BASE <= candidate <= BASE+size_image-24):
   continue
  code=bytes(uc.mem_read(candidate,24))
  if (code[:2]==b'\x85\xc0' and code[4:8]==b'\x8b\x4e\x08\x50' and code[8]==0x68
      and code[13:19]==b'\x8b\x91\xb4\x00\x00\x00' and code[19:23]==b'\xff\x12\x33\xc0'):
   candidates.append(candidate)
 if len(candidates)!=1:
  raise RuntimeError(f'expected one synthetic-API integrity return site, got {[hex(x-BASE) for x in candidates]}')
 checker=candidates[0]
 def _trust(uc,a,size,user):
  if uc.reg_read(UC_X86_REG_EAX)==0:
   uc.reg_write(UC_X86_REG_EAX,1)
  synthetic_api_integrity_trusts.append({'api':'kernel32.dll!GetProcAddress','checker_rva':checker-BASE})
  if synthetic_api_integrity_hook[0] is not None:
   uc.hook_del(synthetic_api_integrity_hook[0]); synthetic_api_integrity_hook[0]=None
  print(' SYNTHETIC_API_INTEGRITY_TRUST','kernel32.dll!GetProcAddress',hex(checker-BASE))
 synthetic_api_integrity_hook[0]=uc.hook_add(UC_HOOK_CODE,_trust,begin=checker,end=checker)

def hook_initial_special(uc,a,size,user):
 # Unicorn's flat x86 segment model stores DS as zero. AgentLite saves DS and
 # accepts only normal 32-bit Windows selectors 0x2B/0x23. Repair the saved
 # selector at the one validation site, then remove this module-wide hook.
 try: ins=bytes(uc.mem_read(a,min(size+8,16)))
 except Exception: ins=b''
 if ins.startswith(bytes.fromhex('668b450a663d2b00')):
  bp=uc.reg_read(UC_X86_REG_EBP); uc.mem_write(bp+0xA,struct.pack('<H',0x2B))
  if initial_special_hook[0] is not None:
   uc.hook_del(initial_special_hook[0]); initial_special_hook[0]=None
  print(' DS_SELECTOR_GATE',hex(a-BASE))

def hook_api(uc,a,size,user):
 if a==SENTINEL: print('RETURN sentinel eax',hex(uc.reg_read(UC_X86_REG_EAX))); uc.emu_stop(); return
 key=api_by_addr.get(a)
 if not key: return
 dll,name=key; e=uc.reg_read(UC_X86_REG_ESP)
 def arg(i): return rd32(e+4+4*i)
 if name != 'VirtualQuery': print('API',hex(a),dll,name,'ret',hex(rd32(e)),'args',[hex(arg(i)) for i in range(7)])
 if name in ('LoadLibraryA','LoadLibraryW','GetModuleHandleA','GetModuleHandleW'):
  ptr=arg(0)
  try:
   if ptr==0: mod=None
   else: mod=read_w(ptr) if name.endswith('W') else read_c(ptr)
  except Exception as ex: mod=f'<read-error {ex!r}>'
  print(' MODULE_LOOKUP',name,repr(mod))
  if phase5c[0] and name.startswith('GetModuleHandle') and isinstance(mod,str):
   current_module[0]=mod; current_module_ptr[0]=ptr
  if name.startswith('GetModuleHandle'):
   if ptr==0: h=BASE
   elif isinstance(mod,str): h=module_handles.get(mod.lower(),0)
   else: h=0
  else:
   if isinstance(mod,str):
    keymod=mod.lower()
    if keymod not in module_handles:
     module_handles[keymod]=0x75000000 + len(module_handles)*0x10000; handle_modules[module_handles[keymod]]=keymod
    h=module_handles[keymod]
   else: h=0
  ret_stdcall(1,h); return
 if name=='GetProcAddress':
  h=arg(0); p=arg(1); nm=f'#{p&0xffff}' if p<0x10000 else read_c(p); mdll=(current_module[0].lower() if phase5c[0] and current_module[0] else handle_modules.get(h,'kernel32.dll')); aa=ensure_api(mdll,nm)
  if phase5c[0] and is_managed and mdll=='mscoree.dll' and nm in ('_CorDllMain','_CorExeMain'):
   # The CLR bootstrap IAT is already present in the protected PE; phase 5C resolves it without an application .rdata write.
   pass
  print(' resolve',mdll,nm,'->',hex(aa))
  if phase5c[0]:
   finalize_pending_resolve()
   pending_resolve[0]={'dll':mdll,'dll_ptr_rva':(current_module_ptr[0]-BASE if current_module_ptr[0] else None),'name':nm,'name_ptr':p,'resolved':aa}
   print(' IMPORT_RESOLVE',mdll,repr(nm))
  ret_stdcall(2,aa); return
 if name=='VirtualProtect':
  if BASE <= arg(0) < BASE+size_image:
   call=(arg(0)-BASE,arg(1),arg(2))
   module_protect_calls.append(call)
   if capture_vprotect[0]: protect_calls.append(call)
  if arg(3): wr32(arg(3),0x20)
  ret_stdcall(4,1); return
 if name=='VirtualProtectEx':
  if arg(4): wr32(arg(4),0x20)
  ret_stdcall(5,1); return
 if name=='VirtualQuery':
  addr=arg(0); buf=arg(1); outsz=arg(2); base=addr&~0xfff
  if addr >= 0x7fff0000:
   ret_stdcall(3,0); return
  # Model only the address ranges that exist in this synthetic process. Large
  # MEM_FREE regions are crucial: real VirtualQuery advances by RegionSize,
  # rather than reporting every 4 KiB page in the 32-bit address space as an
  # image mapping.
  regions=[
   (BASE, BASE+size_image, BASE, 0x40, 0x1000, 0x40, 0x1000000),
   (0x20000000,0x20100000,0x20000000,0x04,0x1000,0x04,0x20000),
   (0x30000000,0x30200000,0x30000000,0x20,0x1000,0x20,0x1000000),
   (0x31000000,0x31100000,0x31000000,0x02,0x1000,0x02,0x40000),
   (0x32000000,0x33000000,0x32000000,0x04,0x1000,0x04,0x20000),
   (0x34000000,0x34100000,0x34000000,0x02,0x1000,0x02,0x40000),
   (0x40000000,0x40100000,0x40000000,0x04,0x1000,0x04,0x20000),
   (0x70000000,0x70200000,0x70000000,0x20,0x1000,0x20,0x1000000),
  ]
  rec=None
  for lo,hi,ab,ap,state,prot,typ in regions:
   if lo <= addr < hi:
    rec=(base,ab,ap,hi-base,state,prot,typ); break
  if rec is None:
   next_lo=min([lo for lo,hi,*_ in regions if lo>base], default=0x7fff0000)
   # Cap free spans to keep 32-bit arithmetic conventional while still
   # skipping millions of empty pages.
   span=max(0x1000,min(next_lo-base,0x10000000))
   rec=(base,0,0,span,0x10000,0,0)
  mbi=struct.pack('<IIIIIII',*rec)
  uc.mem_write(buf,mbi[:min(len(mbi),outsz)]); ret_stdcall(3,min(len(mbi),outsz)); return
 if name=='GetModuleFileNameW': ret_stdcall(3,write_w(arg(1),'C:\\GTSPlus\\'+stub_path.name,arg(2))); return
 if name=='GetModuleFileNameA':
  s=('C:\\GTSPlus\\'+stub_path.name+'\0').encode('ascii'); uc.mem_write(arg(1),s[:arg(2)]); ret_stdcall(3,len(s)-1); return
 if name=='GetFullPathNameW':
  s=read_w(arg(0)); n=write_w(arg(2),s,arg(1));
  if arg(3): wr32(arg(3),arg(2)+(max(s.rfind('\\'),s.rfind('/'))+1)*2)
  ret_stdcall(4,n); return
 if name in ('CreateFileW','CreateFileA'):
  try: fn=read_w(arg(0)) if name.endswith('W') else read_c(arg(0)); print(' FILEPATH',name,repr(fn))
  except Exception as ex: fn=''; print(' FILEPATH_ERR',repr(ex))
  low=fn.replace('\\','/').lower()
  if low.endswith(stub_path.name.lower()+'._'):
   data=side; kind='sidecar'
  elif low.endswith(stub_path.name.lower()):
   data=stub; kind='stub'
  else:
   data=None; kind='other'
  h=new_handle(); file_handles[h]={'path':fn,'data':data,'kind':kind}; file_offsets[h]=0
  print(' FILE_HANDLE',hex(h),kind,'size',len(data) if data is not None else None)
  ret_stdcall(7,h); return
 if name in ('CreateFileMappingW','CreateFileMappingA'):
  fh=arg(0); h=new_handle(); mapping_handles[h]=fh
  print(' MAPPING_HANDLE',hex(h),'file',hex(fh),file_handles.get(fh,{}).get('kind'))
  ret_stdcall(6,h); return
 if name=='MapViewOfFile':
  mh=arg(0); fh=mapping_handles.get(mh); rec=file_handles.get(fh,{})
  kind=rec.get('kind')
  base=SIDECAR if kind=='sidecar' else (RAWFILE if kind=='stub' else 0)
  print(' MAP_VIEW',hex(mh),'file',hex(fh or 0),'kind',kind,'->',hex(base))
  ret_stdcall(5,base); return
 if name=='GetFileSize':
  fh=arg(0); data=file_handles.get(fh,{}).get('data')
  if data is None: last_error[0]=6; ret_stdcall(2,0xffffffff)
  else:
   if arg(1): wr32(arg(1),0)
   last_error[0]=0; ret_stdcall(2,len(data))
  return
 if name=='UnmapViewOfFile': ret_stdcall(1,1); return
 if name=='CloseHandle': ret_stdcall(1,1); return
 if name=='IsDebuggerPresent': ret_stdcall(0,0); return
 if name=='CheckRemoteDebuggerPresent':
  if arg(1): wr32(arg(1),0)
  ret_stdcall(2,1); return
 if name=='GetCurrentProcess': ret_stdcall(0,0xffffffff); return
 if name=='GetCurrentProcessId': ret_stdcall(0,1234); return
 if name=='OpenProcess': ret_stdcall(3,0x44440003 if arg(2)==1234 else 0); return
 if name=='FlushInstructionCache': ret_stdcall(3,1); return
 if name=='VirtualAlloc':
  want=max(arg(1),0x1000); p=(alloc_next[0]+0xfff)&~0xfff; alloc_next[0]=p+((want+0xfff)&~0xfff); ret_stdcall(4,p); return
 if name=='VirtualFree': ret_stdcall(3,1); return
 if name in ('GetLocalTime','GetSystemTime'):
  # SYSTEMTIME: 2026-08-28 Friday 16:48:00.000.
  uc.mem_write(arg(0),struct.pack('<8H',2026,8,5,28,16,48,0,0)); ret_stdcall(1,0); return
 if name=='SystemTimeToFileTime':
  uc.mem_write(arg(1),struct.pack('<Q',0x01dc9fbc00000000)); ret_stdcall(2,1); return
 if name=='GetFileTime':
  for i in range(1,4):
   if arg(i): uc.mem_write(arg(i),struct.pack('<Q',0x01dc9fbc00000000 - 3600*10_000_000))
  ret_stdcall(4,1); return
 if name=='GetVersionExA':
  p=arg(0); sz=rd32(p); raw=struct.pack('<IIIII',sz,10,0,19045,2)+b'\0'*128; uc.mem_write(p,raw[:sz]); ret_stdcall(1,1); return
 if name=='GetVolumeInformationW':
  try: print(' VOLUME_ROOT',repr(read_w(arg(0))) if arg(0) else None)
  except Exception as ex: print(' VOLUME_ROOT_ERR',repr(ex))
  if arg(1) and arg(2): write_w(arg(1),'GTSPLUS',arg(2))
  if arg(3): wr32(arg(3),0x12345678)
  if arg(4): wr32(arg(4),255)
  if arg(5): wr32(arg(5),0x00040006)
  if arg(6) and arg(7): write_w(arg(6),'NTFS',arg(7))
  ret_stdcall(8,1); return
 if name=='GetTempPathW': ret_stdcall(2,write_w(arg(1),r'C:\Temp\\',arg(0))); return
 if name=='GetTempFileNameW':
  try: print(' TEMPFILE path',repr(read_w(arg(0))),'prefix',repr(read_w(arg(1))))
  except Exception as ex: print(' TEMPFILE_ERR',repr(ex))
  write_w(arg(3),r'C:\Temp\GTS1234.tmp',260); ret_stdcall(4,1234); return
 if name=='DeleteFileW': ret_stdcall(1,1); return
 if name=='Sleep': ret_stdcall(1,0); return
 if name=='ResumeThread': ret_stdcall(1,0); return
 if name=='WriteProcessMemory':
  try: uc.mem_write(arg(1),bytes(uc.mem_read(arg(2),arg(3))))
  except Exception as ex: print(' WPM copy failed',repr(ex)); ret_stdcall(5,0); return
  if arg(4): wr32(arg(4),arg(3))
  ret_stdcall(5,1); return
 if name=='WriteFile':
  data=bytes(uc.mem_read(arg(1),arg(2))); print(' WRITEFILE_DATA',data[:512].hex(),repr(data[:512]))
  if data==b'A0F\r\n':
   _arm_synthetic_api_integrity_trust(arg(5))
  if lfsr_addr[0] is None:
   pattern=bytes.fromhex('558bec83ec0460ff751064ff350000000064892500000000c745fc210300009c810c24000100009d')
   blob=bytes(uc.mem_read(BASE,size_image)); hits=[]; pos=0
   while True:
    q=blob.find(pattern,pos)
    if q<0: break
    hits.append(q); pos=q+1
   if len(hits)==1:
    lfsr_addr[0]=BASE+hits[0]; print(' LFSR_HELPER',hex(lfsr_addr[0])); _install_lfsr_hook()
  if data==b'520\r\n' and is_managed and rel.suffix.lower()=='.exe':
   _install_ntqip_hook()
  if data==b'5C0\r\n':
   restored_image[0]=bytes(uc.mem_read(BASE,size_image)); phase5c[0]=True
   if import_write_hook[0] is None:
    import_write_hook[0]=uc.hook_add(UC_HOOK_MEM_WRITE,hook_import_write)
   print(' PHASE5C_ENTER')
  elif data==b'610\r\n' and phase5c[0]:
   finalize_pending_resolve(); phase5c[0]=False; phase5c_done[0]=True
   if import_write_hook[0] is not None:
    uc.hook_del(import_write_hook[0]); import_write_hook[0]=None
   print(' PHASE5C_DONE',len(import_records))
  elif data==b'280\r\n':
   capture_vprotect[0]=True; protect_calls.clear(); print(' PROTECT_CAPTURE_START')
  elif data==b'000-000-000\r\n':
   protector_success[0]=True; capture_vprotect[0]=False
   if ntqip_hook[0] is not None:
    uc.hook_del(ntqip_hook[0]); ntqip_hook[0]=None
   nonzero_protects=[x for x in protect_calls if x[0]]
   if not is_managed or len(nonzero_protects) not in (3,4): _install_entry_hook()
   print(' PROTECTOR_SUCCESS')
  if arg(3): wr32(arg(3),arg(2))
  ret_stdcall(5,1); return
 if name=='SetFilePointer':
  fh=arg(0); move=arg(1); method=arg(3)
  if fh in file_offsets:
   if method==0: file_offsets[fh]=move
   elif method==1: file_offsets[fh]=(file_offsets[fh]+move)&0xffffffff
   elif method==2:
    data=file_handles.get(fh,{}).get('data'); file_offsets[fh]=(len(data) if data is not None else 0)+move
   ret_stdcall(4,file_offsets[fh]&0xffffffff)
  else: ret_stdcall(4,0xffffffff)
  return
 if name=='Beep': ret_stdcall(2,1); return
 if name in ('GetThreadContext','SetThreadContext'): ret_stdcall(2,1); return
 if name=='CreateProcessW':
  try: print(' CREATEPROCESS app',repr(read_w(arg(0))) if arg(0) else None,'cmd',repr(read_w(arg(1))) if arg(1) else None)
  except Exception as ex: print(' CREATEPROCESS_ERR',repr(ex))
  ret_stdcall(10,0); return
 if name=='NtQueryInformationProcess':
  process,cls,buf,ln,retlen=arg(0),arg(1),arg(2),arg(3),arg(4)
  print(' NTQIP_API',hex(process),'class',cls,'buf',hex(buf),'len',ln,'retlen',hex(retlen))
  if cls==4 and buf and ln>=32:  # ProcessTimes / KERNEL_USER_TIMES
   uc.mem_write(buf,b'\0'*32)
   if retlen: wr32(retlen,32)
   ret_stdcall(5,0); return
  if cls in (7,30,31) and buf and ln>=4:  # debug port/object/flags
   wr32(buf,1 if cls==31 else 0)
   if retlen: wr32(retlen,4)
   ret_stdcall(5,0); return
  ret_stdcall(5,0xC0000003); return
 if name=='NtQuerySystemInformation':
  cls,buf,ln,retlen=arg(0),arg(1),arg(2),arg(3)
  print(' NTQSI',cls,hex(buf),ln,hex(retlen))
  if cls != 5:
   ret_stdcall(4,0xC0000003); return
  need=0x180
  if retlen: wr32(retlen,need)
  if not buf or ln < need:
   ret_stdcall(4,0xC0000004); return
  uc.mem_write(buf,b'\0'*need)
  # One SYSTEM_PROCESS_INFORMATION + one SYSTEM_THREAD_INFORMATION.
  wr32(buf+0x00,0)          # NextEntryOffset
  wr32(buf+0x04,1)          # NumberOfThreads
  wr32(buf+0x40,8)          # BasePriority
  wr32(buf+0x44,1234)       # UniqueProcessId
  wr32(buf+0x48,1)          # InheritedFromUniqueProcessId
  # ImageName UNICODE_STRING at +0x38.
  nm='GTSPlus.exe'.encode('utf-16le'); nmp=buf+0x140
  uc.mem_write(nmp,nm+b'\0\0'); uc.mem_write(buf+0x38,struct.pack('<HHI',len(nm),len(nm)+2,nmp))
  th=buf+0xB8
  wr32(th+0x1C,0x70001000)  # StartAddress
  wr32(th+0x20,1234)        # ClientId.UniqueProcess
  wr32(th+0x24,5678)        # ClientId.UniqueThread
  wr32(th+0x28,8); wr32(th+0x2C,8)
  ret_stdcall(4,0); return
 if name=='OpenThread':
  tid=arg(2); print(' OPEN_THREAD','access',hex(arg(0)),'tid',tid)
  ret_stdcall(3,0x44442000 if tid==5678 else 0); return
 if name=='NtQueryInformationThread':
  h,cls,buf,ln,retlen=arg(0),arg(1),arg(2),arg(3),arg(4)
  print(' NTQIT','handle',hex(h),'class',cls,'buf',hex(buf),'len',ln,'retlen',hex(retlen))
  if h==0x44442000 and cls==9 and buf and ln>=4:
   wr32(buf,0x70001000)
   if retlen: wr32(retlen,4)
   ret_stdcall(5,0); return
  ret_stdcall(5,0xC0000003); return
 if name=='NtOpenKey':
  if arg(0): wr32(arg(0),0)
  ret_stdcall(3,0xC0000034); return
 if name=='NtClose': ret_stdcall(1,0); return
 if name=='NtEnumerateValueKey': ret_stdcall(6,0x8000001A); return
 if name=='RtlFormatCurrentUserKeyPath': ret_stdcall(1,0xC0000034); return
 if name=='RtlFreeUnicodeString': ret_stdcall(1,0); return
 if name=='RtlAdjustPrivilege':
  if arg(3): uc.mem_write(arg(3),b'\x00')
  ret_stdcall(4,0); return
 if name=='QueryFullProcessImageNameA':
  path=b'C:\\GTSPlus\\GTSPlus.exe'
  cap=rd32(arg(3)) if arg(3) else 0
  n=min(len(path),max(0,cap-1)) if cap else 0
  if arg(2) and cap:
   uc.mem_write(arg(2),path[:n]+b'\0')
   wr32(arg(3),n)
  ret_stdcall(4,1); return
 if name=='RtlGetVersion':
  p=arg(0); sz=rd32(p) if p else 0
  # RTL_OSVERSIONINFOW: size, major, minor, build, platform, CSDVersion[128].
  raw=(struct.pack('<IIIII',sz or 0x11C,10,0,19045,2)+b'\0'*256+
       struct.pack('<HHHBB',0,0,0,1,0))
  if p: uc.mem_write(p,raw[:min(len(raw),sz or len(raw))])
  ret_stdcall(1,0); return
 if name=='RtlUnicodeStringToAnsiString': ret_stdcall(3,0); return
 if name=='RtlUnwind': ret_stdcall(4,0); return
 if name=='SetLastError': last_error[0]=arg(0); ret_stdcall(1,0); return
 if name=='GetLastError': ret_stdcall(0,last_error[0]); return
 if name=='SetErrorMode':
  prev=error_mode[0]; error_mode[0]=arg(0); ret_stdcall(1,prev); return
 if name=='GetCurrentThreadId': ret_stdcall(0,5678); return
 if name=='CreateMutexA':
  nm=read_c(arg(2)) if arg(2) else ''
  existed=nm in mutexes
  if not existed:
   mutexes[nm]=next_handle[0]; next_handle[0]+=1
  last_error[0]=183 if existed else 0
  print(' MUTEX_CREATE',repr(nm),'existing',existed,'handle',hex(mutexes[nm]))
  ret_stdcall(3,mutexes[nm]); return
 if name=='OpenMutexA':
  nm=read_c(arg(2)) if arg(2) else ''
  h=mutexes.get(nm,0); last_error[0]=0 if h else 2
  print(' MUTEX_OPEN',repr(nm),'->',hex(h))
  ret_stdcall(3,h); return
 if name=='QueryDosDeviceW':
  nm=read_w(arg(0)) if arg(0) else ''
  target='\\Device\\HarddiskVolume3' if nm else 'C:'
  n=write_w(arg(1),target,arg(2)); print(' QUERY_DOS_DEVICE',repr(nm),'->',repr(target)); ret_stdcall(3,n+1); return
 if name=='ReadProcessMemory':
  try:
   data=bytes(uc.mem_read(arg(1),arg(3))); uc.mem_write(arg(2),data); ok=1; last_error[0]=0
  except Exception as ex:
   print(' RPM_FAIL',hex(arg(1)),arg(3),repr(ex)); ok=0; last_error[0]=299
  if arg(4): wr32(arg(4),arg(3) if ok else 0)
  ret_stdcall(5,ok); return
 if name=='LoadLibraryExA':
  nm=read_c(arg(0)) if arg(0) else ''
  print(' LOAD_LIBRARY_EX',repr(nm),'flags',hex(arg(2)))
  h=0x70000000 if nm.lower() in ('kernel32.dll','kernelbase.dll') else (0x70100000 if nm.lower()=='ntdll.dll' else 0x70200000)
  ret_stdcall(3,h); return
 if name=='TerminateThread': print(' TERMINATE_THREAD',hex(arg(0)),arg(1)); ret_stdcall(2,1); return
 if name=='ExitProcess':
  print('ExitProcess',arg(0))
  if not protector_success[0]:
   stopped_reason[0]='ExitProcess before protector success'
  uc.emu_stop(); return
 if is_managed and dll=='mscoree.dll' and name in ('_CorDllMain','_CorExeMain'):
  stopped_reason[0]='managed CLR handoff'; print(' MANAGED_HANDOFF',name); uc.emu_stop(); return
 print('UNHANDLED API',key); stopped_reason[0]=f'unhandled {name}'; uc.emu_stop()
# Scope synthetic API callbacks to their trampoline address ranges. The broad
# application-image hook exists only until the DS-selector gate; later special
# cases are installed dynamically at exact addresses or short-lived ranges.
uc.hook_add(UC_HOOK_CODE,hook_api,begin=STUB,end=STUB+0xFFFF)
uc.hook_add(UC_HOOK_CODE,hook_api,begin=0x70101800,end=0x70101800)
initial_special_hook[0]=uc.hook_add(UC_HOOK_CODE,hook_initial_special,begin=BASE,end=BASE+size_image-1)


def hook_import_write(uc, access, address, size, value, user):
 rec=pending_resolve[0]
 if rec is None or not phase5c[0] or rec.get('iat_rva') is not None:
  return
 if size != 4 or (value & 0xffffffff) != rec['resolved']:
  return
 # The original IATs live in the restored image's read-only-data span.
 # Capture the actual write as it happens instead of searching a later memory
 # snapshot, where the same resolved address may legitimately occur elsewhere.
 iat_sections=[x for x in sections if x[0] in ('.rdata','.idata')]
 if any(BASE+x[2] <= address < BASE+x[2]+x[1] for x in iat_sections):
  rec['iat_rva']=address-BASE
  print(' IAT_WRITE',rec['dll'],repr(rec['name']),hex(rec['iat_rva']))

last_fault={'access':None,'address':None,'size':None,'value':None}
def invalid(uc,access,address,size,value,user):
 last_fault.update(access=access,address=address,size=size,value=value)
 print('INVALID',access,hex(address),size,hex(value) if isinstance(value,int) else value,'eip',hex(uc.reg_read(UC_X86_REG_EIP)),'esp',hex(uc.reg_read(UC_X86_REG_ESP))); return False
uc.hook_add(UC_HOOK_MEM_INVALID,invalid)
write_count=[0]
def dispatch_exception(code, info=()):
 # x86 NT exception records/context, sufficient for the protector's own SEH
 # handler. FS:[0] is linear zero in this Unicorn model and points to the
 # registration record installed by 0x1009F1A0.
 frame=rd32(0); handler=rd32(frame+4)
 exrec=0x320F0000; ctx=0x320F1000; callsp=0x320FE000
 eip=uc.reg_read(UC_X86_REG_EIP)
 print('SEH_DISPATCH','code',hex(code),'frame',hex(frame),'handler',hex(handler),'eip',hex(eip),'eflags',hex(uc.reg_read(UC_X86_REG_EFLAGS)))
 er=bytearray(0x50)
 struct.pack_into('<IIIII',er,0,code,0,0,eip,len(info))
 for i,val in enumerate(info[:15]): struct.pack_into('<I',er,0x14+4*i,val&0xffffffff)
 uc.mem_write(exrec,bytes(er))
 c=bytearray(0x2CC); struct.pack_into('<I',c,0,0x1003F)
 vals={
  0x8C:0, 0x90:0, 0x94:0, 0x98:0,
  0x9C:uc.reg_read(UC_X86_REG_EDI), 0xA0:uc.reg_read(UC_X86_REG_ESI),
  0xA4:uc.reg_read(UC_X86_REG_EBX), 0xA8:uc.reg_read(UC_X86_REG_EDX),
  0xAC:uc.reg_read(UC_X86_REG_ECX), 0xB0:uc.reg_read(UC_X86_REG_EAX),
  0xB4:uc.reg_read(UC_X86_REG_EBP), 0xB8:eip, 0xBC:0x1B,
  0xC0:uc.reg_read(UC_X86_REG_EFLAGS)&~0x100, 0xC4:uc.reg_read(UC_X86_REG_ESP), 0xC8:0x23,
 }
 for off,val in vals.items(): struct.pack_into('<I',c,off,val&0xffffffff)
 uc.mem_write(ctx,bytes(c))
 uc.mem_write(callsp,struct.pack('<IIIII',SENTINEL,exrec,frame,ctx,0))
 uc.reg_write(UC_X86_REG_ESP,callsp)
 uc.reg_write(UC_X86_REG_EIP,handler)
 uc.reg_write(UC_X86_REG_EFLAGS,uc.reg_read(UC_X86_REG_EFLAGS)&~0x100)
 uc.emu_start(handler,SENTINEL,count=2_000_000)
 disp=uc.reg_read(UC_X86_REG_EAX)
 cc=bytes(uc.mem_read(ctx,0x2CC))
 def cv(off): return struct.unpack_from('<I',cc,off)[0]
 print('SEH_RETURN','disp',hex(disp),'new_eip',hex(cv(0xB8)),'new_eflags',hex(cv(0xC0)),'new_esp',hex(cv(0xC4)))
 if disp != 0: raise RuntimeError(f'protector SEH returned disposition {disp}')
 regoffs=[(UC_X86_REG_EDI,0x9C),(UC_X86_REG_ESI,0xA0),(UC_X86_REG_EBX,0xA4),(UC_X86_REG_EDX,0xA8),(UC_X86_REG_ECX,0xAC),(UC_X86_REG_EAX,0xB0),(UC_X86_REG_EBP,0xB4),(UC_X86_REG_ESP,0xC4)]
 for reg,off in regoffs: uc.reg_write(reg,cv(off))
 uc.reg_write(UC_X86_REG_EFLAGS,cv(0xC0))
 uc.reg_write(UC_X86_REG_EIP,cv(0xB8))
 return cv(0xB8)

start=BASE+original_entry
for attempt in range(1000):
 try:
  uc.emu_start(start,SENTINEL,count=50_000_000)
  eip=uc.reg_read(UC_X86_REG_EIP)
  if eip == SENTINEL:
   break
  if stopped_reason[0]:
   print('STOPPED',stopped_reason[0],hex(eip)); break
  print('BUDGET_RESUME',attempt,hex(eip))
  start=eip
  continue
 except Exception as ex:
  eip=uc.reg_read(UC_X86_REG_EIP)
  try: print('EXC_STATE','eip',hex(eip),'flags',hex(uc.reg_read(UC_X86_REG_EFLAGS)),'fs0',hex(rd32(0)))
  except: pass
  # CP repeatedly uses trap-flag + its own SEH handler for anti-debug and
  # dynamic-control-flow probes. If TF is present and FS:[0] points at a valid
  # registration record, dispatch the single-step through that handler.
  if uc.reg_read(UC_X86_REG_EFLAGS) & 0x100:
   try:
    frame=rd32(0)
    if STACK <= frame < STACK+STACKSZ:
     start=dispatch_exception(0x80000004); continue
   except Exception as seh_ex:
    print('SEH ERROR',repr(seh_ex)); break
  if 'Invalid instruction' in str(ex):
   try:
    frame=rd32(0)
    if STACK <= frame < STACK+STACKSZ:
     start=dispatch_exception(0xC000001D); continue
   except Exception as seh_ex:
    print('SEH ERROR',repr(seh_ex)); break
  if 'Unhandled CPU exception' in str(ex):
   try:
    frame=rd32(0)
    if STACK <= frame < STACK+STACKSZ:
     start=dispatch_exception(0x80000003); continue
   except Exception as seh_ex:
    print('SEH ERROR',repr(seh_ex)); break
  if 'Invalid memory' in str(ex):
   try:
    frame=rd32(0)
    if STACK <= frame < STACK+STACKSZ:
     msg=str(ex).lower(); kind=1 if 'write' in msg else (8 if 'fetch' in msg else 0)
     start=dispatch_exception(0xC0000005,(kind,int(last_fault['address'] or 0))); continue
   except Exception as seh_ex:
    print('SEH ERROR',repr(seh_ex)); break
  print('EMU ERROR',repr(ex),str(ex),'eip',hex(eip),'esp',hex(uc.reg_read(UC_X86_REG_ESP)),'eflags',hex(uc.reg_read(UC_X86_REG_EFLAGS))); break
print('done eip',hex(uc.reg_read(UC_X86_REG_EIP)),'entry',hex(captured_entry[0] or 0),'imports',len(import_records),'protects',protect_calls)
outdir=args.output_dir.resolve(); outdir.mkdir(parents=True,exist_ok=True); stem=rel.name.replace('.','_')
if restored_image[0] is not None: (outdir/(stem+'.restored.mem')).write_bytes(restored_image[0])
(outdir/(stem+'.final.mem')).write_bytes(bytes(uc.mem_read(BASE,size_image)))
(outdir/(stem+'.json')).write_text(json.dumps({'relative_path':str(rel),'entrypoint_rva':captured_entry[0],'imports':import_records,'protect_calls':protect_calls,'lfsr_rva':(lfsr_addr[0]-BASE if lfsr_addr[0] else None),'phase5c_done':phase5c_done[0],'protector_success':protector_success[0],'synthetic_api_integrity_trusts':synthetic_api_integrity_trusts},indent=2))
