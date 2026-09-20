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
OUT=Path("/tmp/f33-startup-programming-race-v2.json")
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

def main():
  t0=time.monotonic_ns(); p=None; events=[]; tx=[]; f181=[]; responses=[]
  result={"schema":"f33-startup-programming-race-v2","persistent_writes":False,
          "payload_upload":False,"security_access":False,"ecu_reset":False,
          "strategy":"repeat 10 03 until first exact 50 03; then one immediate 10 02",
          "route":{"bus":BUS,"tx":hex(TX),"rx":hex(RX)},"events":events,"tx":tx,"responses":responses,"f181":f181}
  try:
    p=Panda(); p.set_power_save(0); p.set_safety_mode(3,1)
    tap=Tap(p,t0,events)
    result["panda_health"]={k:p.health().get(k) for k in ("power_save_enabled","ignition_line","ignition_can","car_harness_status")}
    # Clear stale receive state before arming.
    end=time.monotonic()+.25
    while time.monotonic()<end: tap.can_recv(); time.sleep(.001)
    print("ARMED: press brake and POWER normally NOW",flush=True)
    result["armed_t_ms"]=(time.monotonic_ns()-t0)/1e6

    # Phase 1: no identity pre-read. Offer EXTENDED at 20 ms cadence until the
    # first *completed* positive response is observed. 20 ms exceeds the v1
    # measured 15.3 ms worst 50 03 latency, avoiding intentional overlap.
    next_ext=time.monotonic()
    deadline=time.monotonic()+35.0
    ext_positive_ns=None
    while time.monotonic()<deadline and not stop and ext_positive_ns is None:
      now_m=time.monotonic()
      if now_m>=next_ext:
        ns=time.monotonic_ns(); p.can_send(TX,EXT,BUS); tx.append({"t_ms":(ns-t0)/1e6,"kind":"10_03"})
        next_ext=now_m+.020
      rows=tap.can_recv(); now_ns=time.monotonic_ns()
      for a,d,b in rows:
        ai,bi,bb=int(a),int(b),bytes(d)
        if bi==BUS and ai==RX:
          responses.append({"t_ms":(now_ns-t0)/1e6,"phase":"wait_ext","data":bb.hex()})
          if len(bb)>=3 and bb[0]==0x06 and bb[1]==0x50 and bb[2]==0x03:
            ext_positive_ns=now_ns
            break
      if ext_positive_ns is None: time.sleep(.0005)

    if ext_positive_ns is None:
      result["outcome"]="no_50_03"
      result["status"]="complete"
      print("OUTCOME no_50_03",flush=True)
      return

    result["ext_positive_t_ms"]=(ext_positive_ns-t0)/1e6
    # Phase 2: send PROGRAMMING exactly once, immediately after completed 50 03.
    prog_ns=time.monotonic_ns(); p.can_send(TX,PROG,BUS); tx.append({"t_ms":(prog_ns-t0)/1e6,"kind":"10_02"})
    result["programming_tx_t_ms"]=(prog_ns-t0)/1e6
    result["programming_after_50_03_ms"]=(prog_ns-ext_positive_ns)/1e6
    print(f"50 03 observed; 10 02 sent {result[programming_after_50_03_ms]:.3f} ms later",flush=True)

    # Phase 3: no more SessionControl TX. Capture the asynchronous response/reset
    # behavior and startup state for 350 ms before identity polling.
    observe_end=time.monotonic()+.350
    nrc=None; pos_prog=None
    while time.monotonic()<observe_end and not stop:
      rows=tap.can_recv(); now_ns=time.monotonic_ns()
      for a,d,b in rows:
        ai,bi,bb=int(a),int(b),bytes(d)
        if bi==BUS and ai==RX:
          responses.append({"t_ms":(now_ns-t0)/1e6,"phase":"after_prog","data":bb.hex()})
          if len(bb)>=4 and bb[0]==0x03 and bb[1]==0x7f and bb[2]==0x10:
            nrc=bb[3]
          if len(bb)>=3 and bb[1]==0x50 and bb[2]==0x02:
            pos_prog=bb.hex()
      time.sleep(.0005)
    result["programming_nrc"]=nrc
    result["programming_positive_frame"]=pos_prog

    # Phase 4: identify whichever endpoint exists. No session changes, no SA.
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
    result["events"]=events; result["tx"]=tx; result["responses"]=responses; result["f181"]=f181
    # Derive first native startup markers from captured events, including frames
    # consumed inside the tight response loops.
    def first(addr,pred=lambda e:True):
      return next((e for e in events if e["addr"]==addr and e["bus"]==BUS and pred(e)),None)
    result["first_030"]=first("0x030")
    result["first_51e"]=first("0x51E")
    result["first_ready_51e"]=first("0x51E",lambda e:(int(e["data"][:2],16)&0x80)!=0)
    OUT.write_text(json.dumps(result,indent=2)+"\n")
    if p is not None:
      try:p.close()
      except:pass
    print("RESULT",OUT,flush=True)
if __name__=="__main__": main()
