#!/usr/bin/env python3
import json, signal, sys, time, traceback
from pathlib import Path
sys.path.insert(0,"/data/openpilot")
sys.path.insert(0,"/data/openpilot/opendbc_repo")
from panda import Panda
from opendbc.car.uds import UdsClient

TX,RX,BUS=0x7A1,0x7A9,0
EXT=bytes.fromhex("0210030000000000")
PROG=bytes.fromhex("0210020000000000")
APP_F181="023839363546333330373030300000000038413331313333303331303000000000"
BOOT_F181="02"+"21"*32
OUT=Path("/tmp/f33-startup-programming-race.json")
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
      ai,bi,bb=int(a),int(b),bytes(d)
      if ai in (0x030,0x101,0x51e,0x7a9,0x7a1):
        self.events.append({"t_ms":(now-self.t0)/1e6,"addr":f"0x{ai:03X}","bus":bi,"data":bb.hex()})
    return rows
  def __getattr__(self,n): return getattr(self.p,n)

def drain(tap, seconds):
  end=time.monotonic()+seconds
  while time.monotonic()<end:
    tap.can_recv(); time.sleep(.001)

def main():
  t0=time.monotonic_ns(); p=None; events=[]; tx=[]; f181=[]
  result={"schema":"f33-startup-programming-race-v1","persistent_writes":False,
          "payload_upload":False,"security_access":False,"ecu_reset":False,
          "route":{"bus":BUS,"tx":hex(TX),"rx":hex(RX)},"events":events,"tx":tx,"f181":f181}
  try:
    p=Panda(); p.set_power_save(0); p.set_safety_mode(3,1)
    tap=Tap(p,t0,events)
    result["panda_health"]={k:p.health().get(k) for k in ("power_save_enabled","ignition_line","ignition_can","car_harness_status")}
    drain(tap,.25)
    print("ARMED: press brake and POWER normally NOW",flush=True)
    result["armed_t_ms"]=(time.monotonic_ns()-t0)/1e6

    first_51e=None; ready_t=None; first_030=None; first_7a9=None
    hard_deadline=time.monotonic()+35.0
    cycle=0
    while time.monotonic()<hard_deadline and not stop:
      # Drain first so startup markers are timestamped independently of TX.
      rows=tap.can_recv(); now=time.monotonic_ns()
      for a,d,b in rows:
        ai,bi,bb=int(a),int(b),bytes(d)
        if bi<128 and ai==0x51e and len(bb)>=1:
          if first_51e is None: first_51e=now
          if (bb[0]&0x80) and ready_t is None: ready_t=now
        elif bi<128 and ai==0x030 and first_030 is None:
          first_030=now
        elif bi<128 and ai==0x7a9 and first_7a9 is None:
          first_7a9=now

      # Once normal startup traffic appears, keep covering the critical window,
      # but do not spam indefinitely. READY gets 300 ms tail; first 51E gets 1.5 s.
      if ready_t is not None and (now-ready_t)>=300_000_000: break
      if first_51e is not None and (now-first_51e)>=1_500_000_000: break

      cycle+=1
      ts=time.monotonic_ns(); p.can_send(TX,EXT,BUS); tx.append({"t_ms":(ts-t0)/1e6,"kind":"10_03"})
      # Small offset. If this pair lands too early, the next pair is ~10 ms later.
      end=time.monotonic()+.003
      while time.monotonic()<end:
        tap.can_recv(); time.sleep(.0005)
      ts=time.monotonic_ns(); p.can_send(TX,PROG,BUS); tx.append({"t_ms":(ts-t0)/1e6,"kind":"10_02"})
      end=time.monotonic()+.007
      while time.monotonic()<end:
        tap.can_recv(); time.sleep(.0005)

    result["race_cycles"]=cycle
    result["race_stop_t_ms"]=(time.monotonic_ns()-t0)/1e6
    for name,val in (("first_51e",first_51e),("ready",ready_t),("first_030",first_030),("first_7a9",first_7a9)):
      result[name+"_t_ms"]=None if val is None else (val-t0)/1e6

    # Stop all session-control traffic before identification.
    drain(tap,.08)
    print("RACE STOPPED; identifying endpoint read-only",flush=True)
    # Drop stale session-control responses so F181 parsing cannot consume them.
    p.can_clear(0xFFFF) if hasattr(p,"can_clear") else None
    time.sleep(.03)

    ident_deadline=time.monotonic()+3.0
    outcome="no_f181"
    while time.monotonic()<ident_deadline and not stop:
      row={"t_ms":(time.monotonic_ns()-t0)/1e6}
      c=UdsClient(tap,TX,RX,BUS,timeout=.12,tx_timeout=.12,response_pending_timeout=.25)
      try:
        v=bytes(c.read_data_by_identifier(0xF181)); hx=v.hex().lower()
        row.update(ok=True,hex=hx)
        if hx==BOOT_F181:
          outcome="bootloader"; f181.append(row); break
        if hx==APP_F181:
          outcome="application"; f181.append(row); break
        row["identity"]="unexpected"
      except Exception as e:
        row.update(ok=False,error=type(e).__name__,detail=str(e)[:160])
      f181.append(row); time.sleep(.04)
    result["outcome"]=outcome
    result["status"]="complete"
    print("OUTCOME",outcome,flush=True)
  except Exception as e:
    result["status"]="error"; result["error"]={"type":type(e).__name__,"detail":str(e),"traceback":traceback.format_exc()}
    print("ERROR",type(e).__name__,str(e),flush=True)
  finally:
    result["events"]=events; result["tx"]=tx; result["f181"]=f181
    OUT.write_text(json.dumps(result,indent=2)+"\n")
    if p is not None:
      try:p.close()
      except:pass
    print("RESULT",OUT,flush=True)
if __name__=="__main__": main()
