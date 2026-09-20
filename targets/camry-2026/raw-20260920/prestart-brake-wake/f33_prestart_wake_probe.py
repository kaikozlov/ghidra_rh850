#!/usr/bin/env python3
import json, signal, sys, time, traceback
from pathlib import Path
from collections import Counter
sys.path.insert(0,"/data/openpilot")
sys.path.insert(0,"/data/openpilot/opendbc_repo")
from panda import Panda
from opendbc.car.uds import UdsClient

OUT=Path("/tmp/f33-prestart-wake-probe.json")
TX,RX,BUS=0x7A1,0x7A9,0
EXPECTED="023839363546333330373030300000000038413331313333303331303000000000"
stop=False
def sig(*_):
  global stop; stop=True
signal.signal(signal.SIGINT,sig); signal.signal(signal.SIGTERM,sig)

class Tap:
  def __init__(self,p,t0,events): self.p,self.t0,self.events=p,t0,events
  def can_send(self,*a,**kw): return self.p.can_send(*a,**kw)
  def can_recv(self):
    rows=self.p.can_recv(); now=time.monotonic_ns()
    for a,d,b in rows:
      bi=int(b)
      if bi<128:
        self.events.append({"t_ms":(now-self.t0)/1e6,"addr":int(a),"bus":bi,"data":bytes(d).hex()})
    return rows
  def __getattr__(self,n): return getattr(self.p,n)

def do_f181(tap,t0):
  row={"t_ms":(time.monotonic_ns()-t0)/1e6}
  c=UdsClient(tap,TX,RX,BUS,timeout=.08,tx_timeout=.08,response_pending_timeout=.15)
  try:
    v=bytes(c.read_data_by_identifier(0xF181))
    row.update(ok=True,hex=v.hex(),identity_match=(v.hex().lower()==EXPECTED))
  except Exception as e:
    row.update(ok=False,error=type(e).__name__,detail=str(e)[:160])
  return row

def main():
  p=None; events=[]; probes=[]; t0=time.monotonic_ns()
  result={"schema":"f33-prestart-wake-probe-v1","read_only":True,"only_uds_service":"0x22 F181","events":events,"probes":probes}
  try:
    p=Panda()
    # Fully wake Panda CAN side; inherited offroad power-save would otherwise hide buses.
    p.set_power_save(0)
    p.set_safety_mode(3,1)
    tap=Tap(p,t0,events)
    h=p.health(); result["panda_health_after_wake"]={k:h.get(k) for k in ("power_save_enabled","ignition_line","ignition_can","car_harness_status")}
    print("BASELINE: F181 polling with car OFF, foot OFF brake",flush=True)
    base_end=time.monotonic()+3.0
    while time.monotonic()<base_end and not stop:
      probes.append({"phase":"baseline",**do_f181(tap,t0)})
      time.sleep(.10)
    result["armed_t_ms"]=(time.monotonic_ns()-t0)/1e6
    print("ARMED: press and HOLD brake NOW; DO NOT press POWER",flush=True)
    post_end=time.monotonic()+18.0
    while time.monotonic()<post_end and not stop:
      probes.append({"phase":"post",**do_f181(tap,t0)})
      time.sleep(.10)
    # passive tail
    tail=time.monotonic()+.5
    while time.monotonic()<tail:
      tap.can_recv(); time.sleep(.005)
    result["status"]="complete"
  except Exception as e:
    result["status"]="error"; result["error"]={"type":type(e).__name__,"detail":str(e),"traceback":traceback.format_exc()}
  finally:
    if p is not None:
      try:p.close()
      except:pass
    result["events"]=events; result["probes"]=probes
    ok=[x for x in probes if x.get("ok")]
    result["first_success"]=ok[0] if ok else None
    for phase in ("baseline","post"):
      result[phase+"_successes"]=sum(1 for x in probes if x.get("phase")==phase and x.get("ok"))
    c=Counter((e["bus"],e["addr"]) for e in events)
    result["traffic_census"]=[{"bus":b,"addr":f"0x{a:03X}","count":n} for (b,a),n in sorted(c.items())]
    for a in (0x030,0x101,0x51e,0x7a9):
      xs=[e for e in events if e["addr"]==a]
      result[f"0x{a:03X}"]={"count":len(xs),"first":xs[0] if xs else None,"last":xs[-1] if xs else None}
    OUT.write_text(json.dumps(result,indent=2)+"\n")
    print("COMPLETE",flush=True)
if __name__=="__main__": main()
