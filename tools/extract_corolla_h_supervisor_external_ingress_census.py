#!/usr/bin/env python3
"""Extract and close H generated-COM provenance into the CEDAE supervisor cone.

This is an exact-image/corpus extraction tool. It compares wire fields by CAN ID,
relative byte/bit layout and signedness, then follows generated raw->staging->snapshot
copies into the H steering-supervisor call cone. It fails closed if a non-B6
H-only/wire-changed field or a changed >=12-bit scalar survives.
"""
import json,re,struct,hashlib
from pathlib import Path
GP=0xFEBEB800
SIMG=Path('firmware/RH850_P1M-E_CodeFlash.bin').read_bytes()
HIMG=Path('community/albinoelephant/normalized/8965H1202000_CodeFlash.bin').read_bytes()

def load_corpus(path):
 d={}
 for l in open(path):
  r=json.loads(l)
  if 'entry_addr' in r:d[int(r['entry_addr'],16)]=r
 return d
S=load_corpus('data/generated/decompilations.jsonl'); H=load_corpus('build/work/corpora/h_8965H1202000_rdbihelper2_decompilations.jsonl')

def addr_from(expr,varnames=('iVar1','iVar2','iVar3','iVar4','iVar15','puVar1','puVar2')):
 e=expr.strip()
 m=re.search(r'(?:[A-Za-z_]*Ram|DAT_)(febe[0-9a-f]{4})',e,re.I)
 if m:return int(m.group(1),16)
 m=re.search(r'0x(febe[0-9a-f]{4})',e,re.I)
 if m:return int(m.group(1),16)
 for var in varnames:
  m=re.search(re.escape(var)+r'\s*\+\s*(-?0x[0-9a-f]+)',e,re.I)
  if m:return (GP+int(m.group(1),0))&0xffffffff
  m=re.search(re.escape(var)+r'\s*-\s*(0x[0-9a-f]+)',e,re.I)
  if m:return (GP-int(m.group(1),0))&0xffffffff
 return None

def assignment_map(rec,varnames):
 out=[]
 for raw in rec['decompiled_c'].splitlines():
  line=raw.strip()
  # single plain assignment only
  if '=' not in line or any(op in line for op in ['==','!=','>=','<=']):continue
  lhs,rhs=line.split('=',1);da=addr_from(lhs,varnames);sa=addr_from(rhs,varnames)
  if da is not None:out.append((da,sa,line))
 return out
stage_assign=assignment_map(H[0x5262c],('iVar3',))
snap_assign=assignment_map(H[0xb8ee4],('iVar38',))
# Prefer last assignment only if duplicate destination; preserve all in diagnostics.
stage={d:(s,l) for d,s,l in stage_assign};snap={d:(s,l) for d,s,l in snap_assign}

def scalar_calls(corpus,call_names):
 rows=[]
 names='|'.join(re.escape(n) for n in call_names)
 pat=re.compile(r'(?:'+names+r')\((0x[0-9a-f]+|\d+),(0x[0-9a-f]+|\d+),(0x[0-9a-f]+|\d+),(0x[0-9a-f]+|\d+),(0x[0-9a-f]+|\d+),([^;]+)\);',re.I)
 for e,r in corpus.items():
  for m in pat.finditer(r['decompiled_c']):
   vals=[int(m.group(i),0) for i in range(1,6)];dest=addr_from(m.group(6))
   rows.append({'signal':vals[0],'offset':vals[1],'bits':vals[2],'bitoff':vals[3],'signed':vals[4], 'dest':dest,'unpacker':e,'ptr':m.group(6).strip()})
 return rows
Scalls=scalar_calls(S,['application_com_receive_signal','FUN_0007c03e'])
Hcalls=scalar_calls(H,['FUN_0007643a'])

def sigmap(img,base,count):return [struct.unpack_from('<H',img,base+2*i)[0] for i in range(count)]
Sm=sigmap(SIMG,0x224e4,300);Hm=sigmap(HIMG,0x223fc,274)
# Rx descriptor maps known and already raw-regression-pinned.
def rxmap(img,base,count,firstpdu):
 out={}
 for i in range(count):
  raw,n=struct.unpack_from('<II',img,base+8*i);out[firstpdu+i]={'can':raw&0x1fffffff,'length':n,'fd':bool(raw&0x40000000)}
 return out
Srx=rxmap(SIMG,0x22018,47,6);Hrx=rxmap(HIMG,0x21f94,40,5)
# Discover per-PDU COM data buffer-offset table using all scalar calls.
def discover_offsets(img,calls,mapping,rx,pdu_count):
 cands=[]
 for base in range(0x22000,0x23000,2):
  vals=[struct.unpack_from('<H',img,base+2*i)[0] for i in range(pdu_count)]
  ok=True;used=0
  for c in calls:
   sid=c['signal']
   if sid>=len(mapping):continue
   pdu=mapping[sid]
   if pdu not in rx:continue
   used+=1;off=c['offset'];lo=vals[pdu];hi=lo+rx[pdu]['length']
   if not (lo<=off<hi):ok=False;break
  if ok and used>50:
   cands.append((base,vals,used))
 if len(cands)!=1:
  raise SystemExit(f'offset table candidates {[(hex(x[0]),x[2]) for x in cands]}')
 return cands[0]
SoBase,So,_=discover_offsets(SIMG,Scalls,Sm,Srx,53)
HoBase,Ho,_=discover_offsets(HIMG,Hcalls,Hm,Hrx,45)
# Normalize wire fields by CAN ID + relative byte/bits/bitoff/signed.
def norm_fields(calls,mapping,rx,offs):
 bycan={}
 rawdest={}
 for c in calls:
  sid=c['signal'];
  if sid>=len(mapping):continue
  pdu=mapping[sid]
  if pdu not in rx:continue
  desc=rx[pdu];rel=c['offset']-offs[pdu]
  row={**c,'pdu':pdu,'can':desc['can'],'length':desc['length'],'fd':desc['fd'],'wire_byte':rel,'wire_shape':(rel,c['bits'],c['bitoff'],c['signed'])}
  bycan.setdefault(desc['can'],[]).append(row)
  if c['dest'] is not None:rawdest.setdefault(c['dest'],[]).append(row)
 return bycan,rawdest
Sby,Sraw=norm_fields(Scalls,Sm,Srx,So);Hby,Hraw=norm_fields(Hcalls,Hm,Hrx,Ho)
# COM provenance tiers
# stage destination whose source is raw COM destination
com_stage={}
for st,(src,line) in stage.items():
 if src in Hraw:com_stage[st]={'raw':src,'signals':Hraw[src],'line':line}
com_snap={}
for sn,(st,line) in snap.items():
 if st in com_stage:com_snap[sn]={'stage':st,**com_stage[st],'snap_line':line}
# Build full H call graph; bound to application control-ish direct descendants but collect arbitrary helpers to depth 5.
def calls_from(code):
 return {int(x,16) for x in re.findall(r'FUN_([0-9a-fA-F]{8})\(',code)}
graph={e:(calls_from(r['decompiled_c'])-{e}) for e,r in H.items()}
root=0xcedae
q=[(root,[root])];seen={root:0};paths={root:[root]}
while q:
 e,path=q.pop(0)
 if len(path)>=6:continue
 for n in graph.get(e,set()):
  if n not in H:continue
  # avoid descending into low-level generic library/motor/crypto regions except local control range.
  # Supervisor/control functions are overwhelmingly >=0xB0000; allow wrappers/helpers >=0xB0000 only.
  if n<0xB0000:continue
  if n not in seen or len(path)<seen[n]:
   seen[n]=len(path);paths[n]=path+[n];q.append((n,path+[n]))
cone=set(paths)
# External addresses tiers -> signal rows
addrprov={}
for raw,rows in Hraw.items():addrprov.setdefault(raw,[]).extend([('raw',r) for r in rows])
for st,v in com_stage.items():addrprov.setdefault(st,[]).extend([('stage',r) for r in v['signals']])
for sn,v in com_snap.items():addrprov.setdefault(sn,[]).extend([('snapshot',r) for r in v['signals']])
# Collect direct references from cone via data refs plus textual symbolic abs.
proven=[]
for e in sorted(cone):
 r=H[e];refs=set()
 for dr in r.get('data_references',[]):
  try:a=int(dr.get('to_addr','0'),16)
  except:continue
  if a in addrprov:refs.add(a)
 code=r['decompiled_c'].lower()
 for a in addrprov:
  if f'{a:08x}' in code:refs.add(a)
 for a in refs:
  for tier,sig in addrprov[a]:
   # classify field relative to S same CAN/wire shape
   sfields=Sby.get(sig['can'],[]); same=[x for x in sfields if x['wire_shape']==sig['wire_shape']]
   if sig['can'] not in Sby:wireclass='h_only_can'
   elif same:wireclass='shared_wire_field'
   else:wireclass='h_changed_wire_field'
   proven.append({'consumer':e,'consumer_path':paths[e],'address':a,'tier':tier,'signal':sig['signal'],'can':sig['can'],'fd':sig['fd'],'wire_byte':sig['wire_byte'],'bits':sig['bits'],'bitoff':sig['bitoff'],'signed':sig['signed'],'wire_class':wireclass,'s_same_shape_signals':[x['signal'] for x in same]})
# unique paths by sig+consumer+address/tier
uniq=[];keys=set()
for x in proven:
 k=(x['consumer'],x['address'],x['tier'],x['signal'])
 if k not in keys:keys.add(k);uniq.append(x)
# Potential command-ish fields: H-only/changed wire shape, >=12 bits signed or unsigned, directly reaches supervisor cone.
cands=[x for x in uniq if x['wire_class']!='shared_wire_field' and x['bits']>=12]
# Summary by CAN/wireclass/signed large
from collections import Counter
summary={
 's_offset_table':hex(SoBase),'h_offset_table':hex(HoBase),'h_cone_functions':len(cone),
 'h_scalar_rx_calls':len(Hcalls),'h_com_stage_cells':len(com_stage),'h_com_snapshot_cells':len(com_snap),
 'external_refs':len(uniq),'external_signals':len(set(x['signal'] for x in uniq)),
 'can_counts':{hex(k):v for k,v in sorted(Counter(x['can'] for x in uniq).items())},
 'wire_class_counts':dict(Counter(x['wire_class'] for x in uniq)),
 'potential_changed_large_fields':len(cands),
}
out={'summary':summary,'potential_changed_large_fields':cands,'external_refs':uniq}
# Bind every cited consumer/unpacker to exact raw function bytes.
def fhash(corpus, entry, image):
    r=corpus[entry]; body=image[entry:entry+r['body_size']]
    return hashlib.sha256(body).hexdigest()
for x in uniq:
    x['consumer_body_size']=H[x['consumer']]['body_size']
    x['consumer_body_sha256']=fhash(H,x['consumer'],HIMG)
    # Source unpackers are deterministic from signal/raw provenance; bind each exact body.
    rows=[r for r in Hcalls if r['signal']==x['signal'] and r['dest'] in addrprov and r['unpacker'] in H]
    x['source_unpackers']=sorted(
        ({'entry':r['unpacker'],'body_size':H[r['unpacker']]['body_size'],'body_sha256':fhash(H,r['unpacker'],HIMG)} for r in rows),
        key=lambda q:q['entry'])
out={'schema':'corolla-8965H1202000-supervisor-external-ingress-census-v1',
     'evidence_boundary':'Complete scalar generated-COM -> raw/staging/snapshot direct-reference census over the supplied target-native H decompiler corpus and CEDAE call cone to depth 5. Direct-reference and generated-copy proof does not exclude opaque/computed-pointer flows outside this model.',
     'images':{'sienna_sha256':hashlib.sha256(SIMG).hexdigest(),'corolla_h_sha256':hashlib.sha256(HIMG).hexdigest()},
     'source_corpora':{'sienna':'data/generated/decompilations.jsonl','corolla_h':'build/work/corpora/h_8965H1202000_rdbihelper2_decompilations.jsonl',
                      'sienna_sha256':hashlib.sha256(Path('data/generated/decompilations.jsonl').read_bytes()).hexdigest(),
                      'corolla_h_sha256':hashlib.sha256(Path('build/work/corpora/h_8965H1202000_rdbihelper2_decompilations.jsonl').read_bytes()).hexdigest()},
     'summary':summary,'potential_changed_large_fields':cands,'external_refs':uniq}
Path('data/generated/corolla_8965H1202000_supervisor_external_ingress_census.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
# Encode result into a small text artifact for easy inspection.
lines=[json.dumps(summary,sort_keys=True),'CANDIDATES:']
for x in cands:lines.append(json.dumps(x,sort_keys=True))
changed=[x for x in uniq if x['wire_class']!='shared_wire_field']
other=[x for x in changed if x['can']!=0xB6]
if cands:
    raise SystemExit(f'H supervisor ingress retains H-only/wire-changed >=12-bit candidates: {cands}')
if other:
    raise SystemExit(f'H supervisor ingress retains non-B6 H-only/wire-changed fields: {other}')
print(json.dumps(summary,sort_keys=True))
