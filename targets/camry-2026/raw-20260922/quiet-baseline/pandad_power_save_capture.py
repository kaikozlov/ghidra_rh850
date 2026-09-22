#!/usr/local/venv/bin/python
import gzip, json, time, datetime
import openpilot.cereal.messaging as messaging

DURATION = 60.0
OUT = "/data/camry_quiet_baseline_20260922.json.gz"
can_sock = messaging.sub_sock("can", conflate=False, timeout=0)
panda_sock = messaging.sub_sock("pandaStates", conflate=False, timeout=0)
start_mono = time.monotonic()
start_wall = datetime.datetime.now(datetime.timezone.utc).isoformat()
can_rows=[]
panda_rows=[]
while time.monotonic() - start_mono < DURATION:
  for x in messaging.drain_sock(can_sock, wait_for_one=False):
    for y in x.can:
      row={"logMonoTime":int(x.logMonoTime),"src":int(y.src),"address":int(y.address),"busTime":int(y.busTime),"dat":bytes(y.dat).hex()}
      for k in ("fd","brs","returned","rejected"):
        try: row[k]=bool(getattr(y,k))
        except Exception: pass
      can_rows.append(row)
  for x in messaging.drain_sock(panda_sock, wait_for_one=False):
    panda_rows.append({"logMonoTime":int(x.logMonoTime),"states":[p.to_dict() for p in x.pandaStates]})
  time.sleep(0.02)
end_mono = time.monotonic()
end_wall = datetime.datetime.now(datetime.timezone.utc).isoformat()
obj={"schema":"camry-quiet-baseline-v1","duration_s":end_mono-start_mono,"start_wall_utc":start_wall,"end_wall_utc":end_wall,"capture_method":"read-only subscription to existing pandad can+pandaStates publications; no Panda open/configuration; no CAN TX; no diagnostics","can":can_rows,"pandaStates":panda_rows}
with gzip.open(OUT,"wt",encoding="utf-8",mtime=0) if False else gzip.GzipFile(filename=OUT,mode="wb",mtime=0) as f:
  f.write(json.dumps(obj,separators=(",",":"),sort_keys=True).encode())
print(json.dumps({"out":OUT,"duration_s":obj["duration_s"],"can_frames":len(can_rows),"panda_samples":len(panda_rows),"start":start_wall,"end":end_wall},indent=2))
