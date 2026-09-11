#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
ART=ROOT/"data/generated/camry_8965F3307000_prefault_control_flow.json"
STORE=ROOT/"data/generated/camry_8965F3307000_prefault_control_flow_store_audit.json"
OPS=ROOT/"data/generated/camry_8965F3307000_prefault_control_flow_ops.json"
BUILD=ROOT/"tools/targets/camry/builders/build_camry_8965F3307000_prefault_control_flow.py"
EXTRACT=ROOT/"tools/targets/camry/extract/extract_camry_8965F3307000_prefault_control_flow_audits.py"
GH_STORE=ROOT/"ghidra/scripts/investigate/AuditCallConeStores.java"
GH_OPS=ROOT/"ghidra/scripts/investigate/AuditCallConeMemoryOps.java"

passed=failed=0
def check(name:str,cond:object,detail:str="") -> None:
    global passed,failed
    ok=bool(cond); passed+=int(ok); failed+=int(not ok)
    print(f"[{'PASS' if ok else 'FAIL'}] {name}"+(f" ({detail})" if detail else ""))

art=json.loads(ART.read_text()); store=json.loads(STORE.read_text()); ops=json.loads(OPS.read_text())
check("artifact schema",art["schema"]=="camry-8965f3307000-prefault-control-flow-v1")
check("expanded store schema",store["schema"]=="camry-8965f3307000-prefault-control-flow-store-audit-v1")
check("expanded store denominator",store["summary"]=={"computed":366,"functions":307,"ranged":56,"stores":412,"unknown":307})
check("expanded pointer-store denominator",store["pointer_parameter_dependent"]["store_count"]==283 and store["pointer_parameter_dependent"]["function_count"]==76)
check("memory-op denominator",ops["summary"]=={"arith":0,"functions":307,"indirects":20,"loads":854,"param_arith":0,"param_indirects":5,"param_loads":620})
check("audit sources retained",GH_STORE.exists() and GH_OPS.exists() and "CALLIND" in GH_OPS.read_text() and EXTRACT.exists())
with tempfile.TemporaryDirectory() as td:
    out=Path(td)/"control.json"
    p=subprocess.run([sys.executable,str(BUILD),"--out",str(out)],cwd=ROOT,env={**os.environ,"PYTHONPATH":str(ROOT)},capture_output=True,text=True,check=False)
    check("builder succeeds",p.returncode==0,p.stderr[-300:])
    check("artifact regenerates exactly",p.returncode==0 and out.read_bytes()==ART.read_bytes())

cone=art["expanded_cone"]
check("expanded cone includes all DCM callbacks",len(cone["roots"])==15 and cone["store_summary"]["functions"]==307 and cone["memory_op_summary"]["functions"]==307)
check("expanded critical coarse hits explicitly closed",cone["critical_known_range_rows"]==15 and cone["critical_known_range_functions"]==["0x0008E7BA","0x00093C6C","0x00093C9A","0x00093DE8","0x00093E5C","0x00093EF6","0x00093F4E","0x0009405C"] and cone["dcm_route_domain"]==[0,1,2])
ecm=art["ecm_reset_routing"]
check("ECM runtime source set exact",ecm["runtime_micfg0"]=="0x100B001E" and ecm["maskable_sources"]==[1,2,3,4,16,17,19,28])
check("RSCFD ECM reset/interrupt route absent",ecm["rscfd_sources_routed"]==[] and set(ecm["rscfd_ecm_sources"])=={"22","37","54"})
can=art["can_interrupt_error_surface"]
check("CAN1 only RX/TX error-neighbor lines enabled",can["eic"]["186"].startswith("masked") and can["eic"]["187"].startswith("enabled") and can["eic"]["188"].startswith("enabled") and can["eic"]["189"].startswith("masked") and can["eic"]["190"].startswith("masked"))
check("CAN error IRQs disabled",can["can1_cctr"]=="0x00A00001" and can["bus_off_mode"]==1 and not any(can["channel_error_interrupt_enables"].values()) and not any(can["global_error_interrupt_enables"].values()))
check("default CAN error vector is nonreturn loop",can["default_handler"]["entry"]=="0x00062E1E" and "self-loop" in can["default_handler"]["terminal"])
wdt=art["watchdog_boundary"]
check("WDTA has no CodeFlash references",wdt["codeflash_reference_count"]==0 and not wdt["runtime_ecm_routed"] and "unknown" in wdt["option_byte_startup"])
dma=art["rscfd_dma"]
check("RSCFD DMA/DTS trigger is disabled",dma["cdtct"]=="0xFFD20490" and dma["reference_functions"]==["0x0008488C","0x00084C2C","0x00084E16"] and "write zero" in dma["writers"])
ind=art["indirect_control_flow"]
check("five parameter-dependent indirect sites exact",[(x["function"],x["site"]) for x in ind["parameter_dependent_sites"]]==[("0x00080884","0x000808BE"),("0x000810F2","0x0008115C"),("0x000810F2","0x0008117A"),("0x00081938","0x00081988"),("0x00081D30","0x00081DD4")])
check("no divide/remainder exceptional operation",ind["integer_divide_or_remainder_ops"]==0 and "no payload-controlled indirect call" in ind["classification"])
sync=art["synchronous_ingress"]
check("normal CAN ingress exact partition",sync["normal_rule_count"]==43 and sync["protected_rules"]==[4,36,39] and sync["protected_can_ids"]==["0x00F","0x0D7","0x0B6"] and sync["raw_com_rule_count"]==40)
check("raw COM has no enabled pre-copy hooks",sync["raw_com_pdu_records"]=={"flags":"0x0C","ids":"5..47","pre_copy_hook_enabled":False,"selector":0})
check("raw COM synchronous effect is bookkeeping only","generation-byte" in sync["raw_com_effect"] and "deferred" in sync["raw_com_effect"])
gb=art["guard_and_boot"]
check("FE01 guard has no post-startup writer",not gb["post_startup_guard_writer"] and gb["guard_writers"]==[{"function":"0x0007A132","site":"0x0007A13A","value":"0xFD02"},{"function":"0x0007A132","site":"0x0007A184","value":"0xFE01"}])
check("bad JARL cannot be conditionally skipped inside aggregate",gb["bad_callsite"]=="0x0007A272" and gb["recorded_bad_four_bytes"]=="FF 02 92 5B" and gb["bad_instruction_with_stock_successor"]=="FF 02 92 5B 24 36" and gb["bad_target"]=="0x362BFE04" and gb["stock_replaced_instruction"]=={"bytes":"80 FF EE 1C","target":"0x0007BF60"} and not gb["conditional_bypass_between_79EDE_and_bad_call"])
check("valid cold boot has no CAN catch window",not gb["cold_boot_can_race"] and "FFDB8/0x20880 directly" in gb["cold_boot"])
v=art["verdict"]
check("no recovered network reset/pivot/guard transition",not v["network_guard_transition_recovered"] and not v["network_reset_recovered"] and not v["network_control_flow_pivot_recovered"] and not v["bootloader_can_catch_with_valid_application"])
print(f"\n{passed} passed, {failed} failed")
raise SystemExit(1 if failed else 0)
