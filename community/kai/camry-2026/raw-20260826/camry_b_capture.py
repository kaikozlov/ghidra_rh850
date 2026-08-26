import gzip,json,time
from panda import Panda
p=Panda(Panda.list()[0]); p.set_safety_mode(3,1)
t0=time.monotonic(); frames=[]
end=t0+25
while time.monotonic()<end:
  msgs=p.can_recv() or []
  t=time.monotonic()-t0
  for addr,dat,bus in msgs:
    frames.append({"t":t,"addr":addr,"bus":bus,"data":bytes(dat).hex(),"len":len(dat)})
  if not msgs: time.sleep(0.001)
out={"capture":"2026 Camry READY stationary D-B-D","duration_s":time.monotonic()-t0,"frames":frames}
raw=(json.dumps(out,separators=(",",":"))+"\n").encode()
with open("/cache/tsk/camry_ready_b_20260826.json.gz","wb") as f:
  with gzip.GzipFile(filename="",mode="wb",fileobj=f,mtime=0,compresslevel=9) as g:g.write(raw)
print("frames",len(frames),"duration",out["duration_s"],"raw",len(raw))
