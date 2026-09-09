import time,collections
from exploit.ephemeral_runtime.camry_f33_runtime_monitor import MonitorSession,OP_SET_WATCH_BASE
s=MonitorSession(require_ready_parked=True)
# controller1 common FIFO0/1/2: CFID and CFDF0, plus CFDF1 for likely fifo1
addrs=[0xFFD23580,0xFFD2358C,0xFFD23600,0xFFD2360C,0xFFD23680,0xFFD2368C,0xFFD23610,0xFFD23604]
for i,a in enumerate(addrs):
    s._send(OP_SET_WATCH_BASE+i,a,lambda st,i=i,a=a: st['watch_addresses_raw'][i]==a)
s.set_running(True)
rows=[]; t=time.monotonic()+2
try:
    while time.monotonic()<t:
        st=s.read_state(); vals=[v['raw_u32'] for v in st['values']]; rows.append(vals); time.sleep(.005)
finally: s.set_running(False)
for fi,(ididx,dataidx) in enumerate([(0,1),(2,3),(4,5)]):
    ids=collections.Counter(v[ididx]&0x1fffffff for v in rows)
    print('fifo',fi,'ids',[(hex(k),n) for k,n in ids.most_common(12)])
    print('fifo',fi,'data0 unique',[(hex(k),n) for k,n in collections.Counter(v[dataidx] for v in rows).most_common(8)])
print('fifo1 data1',[(hex(k),n) for k,n in collections.Counter(v[6] for v in rows).most_common(8)])
print('fifo1 ptr',[(hex(k),n) for k,n in collections.Counter(v[7] for v in rows).most_common(8)])
