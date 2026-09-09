import time,collections
from exploit.ephemeral_runtime.camry_f33_runtime_monitor import MonitorSession
s=MonitorSession(require_ready_parked=True)
ids={0x030,0x08A,0x025,0x00F,0x0D7,0x051E,0x07A9}
c=collections.Counter(); ex={}
t=time.monotonic()+3
while time.monotonic()<t:
    for a,d,b in s.panda.can_recv():
        if a in ids and b<128:
            c[(a,b)]+=1; ex.setdefault((a,b),bytes(d).hex())
    time.sleep(.001)
for k,v in sorted(c.items()): print(hex(k[0]),'bus',k[1],v,ex[k])
