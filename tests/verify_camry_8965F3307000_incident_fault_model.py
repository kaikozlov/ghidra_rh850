#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / "data/generated/camry_8965F3307000_incident_fault_model.json"
BUILD = ROOT / "tools/targets/camry/builders/build_camry_8965F3307000_incident_fault_model.py"

passed = failed = 0

def check(name: str, cond: object, detail: str = "") -> None:
    global passed, failed
    ok = bool(cond)
    passed += int(ok); failed += int(not ok)
    suffix = f" ({detail})" if detail else ""
    print(f"[{'PASS' if ok else 'FAIL'}] {name}{suffix}")

a = json.loads(ART.read_text())
check("schema", a["schema"] == "camry-8965f3307000-incident-fault-model-v1")

with tempfile.TemporaryDirectory() as td:
    out = Path(td) / "fault.json"
    p = subprocess.run(
        [sys.executable, str(BUILD), "--out", str(out)], cwd=ROOT,
        env={**os.environ, "PYTHONPATH": str(ROOT)}, capture_output=True, text=True,
    )
    check("builder succeeds", p.returncode == 0, p.stderr[-300:])
    check("artifact regenerates exactly", p.returncode == 0 and out.read_bytes() == ART.read_bytes())

i = a["incident_instruction"]
check(
    "incident bytes stay separate from stock image",
    i["recorded_write_bytes"] == "ff02925b"
    and i["reconstructed_bytes"] == "ff02925b2436"
    and i["decoded"] == "JARL 0x362BFE04,LP"
    and i["stock_replaced_instruction"]["bytes"] == "80ffee1c",
)
check("incident JARL sets LP to 7A278", i["link_register_after_jarl"] == "0x0007A278")
check("target is access-prohibited", "0x20000000..0xFEBDFFFF" in i["target_address_space"])
check("fault registers not promoted to observed", not i["exception_registers_observed_live"] and not i["target_observed_live"])

v = a["vector_selection"]
check(
    "whole-image PSW writer census",
    [(x["address"],x["bytes"]) for x in v["raw_psw_ldsr_writers"]]
    == [("0x00000204","ea2f2000"),("0x00009F28","ea2f2000")],
)
check("RBASE is never written", v["raw_rbase_ldsr_writers"] == [])
check(
    "whole-image EBASE writer census",
    [x["address"] for x in v["raw_ebase_ldsr_writers"]]
    == ["0x0000026E","0x00008508","0x00008514","0x00009F38","0x000715C8"],
)
check("reset core init sets EBV", v["reset_core_init_psw"] == "0x00018020" and v["reset_core_init_ebv"] == 1)
check("application selects EBASE 20000", v["application_ebase"] == "0x00020000")
check("SYSERR vector is EBASE+10", v["syserr_vector_offset"] == "0x10" and v["predicted_vector"] == "0x00020010")
check("application vector targets 62E1E", v["vector_bytes"].startswith("1f00e0061e2e0600") and v["vector_target"] == "0x00062E1E")
check(
    "low boot EBASE helper has only low direct callers",
    [(x["callsite"],x["target"]) for x in v["low_ebase_setter_direct_calls"]]
    == [("0x00008578","0x000084F8"),("0x00008618","0x000084F8"),("0x0000863C","0x000084F8"),("0x0000868E","0x000084F8")]
    and v["low_ebase_setter_fixed_pointer_literals"] == 0,
)

a_arch = a["architecture_prediction"]
check("fault remains architecture-predicted", a_arch["grade"].startswith("architecture-predicted") and "not observed" in a_arch["boundary"])
check("product FEIC mapping", a_arch["p1m_e_feic"].startswith("0x13"))
check("G3M class is fetch SYSERR", "resumable FE-level SYSERR" in a_arch["g3m_exception_class"])
check("SYSERR sets NP and ID", a_arch["g3m_acknowledgement_effects"]["PSW.NP"] == 1 and a_arch["g3m_acknowledgement_effects"]["PSW.ID"] == 1)
check("SYSERR retains EBV", a_arch["g3m_acknowledgement_effects"]["PSW.EBV"] == "retained")

h = a["terminal_handler"]
check("terminal handler body pinned", h["entry"] == "0x00062E1E" and h["bytes_sha256"] == "487dbbad9e4dcc90fe3fdf935b7513d17bacedb99a75fdc9a2e1e209bbc596d5")
check("handler is a non-returning self-loop", h["terminal"] == "self-loop at 0x62E42; no FERET/EIRET")
check("handler frame geometry", h["stack_frame"] == {"start":"0xFEBE1F94","end_inclusive":"0xFEBE1FFF","saved_lp":"0xFEBE1FFC"})
check("saved LP prediction", h["saved_lp_predicted_value"] == "0x0007A278")
check("handler does not persist FE context", h["does_not_copy_to_ram"] == ["FEPC","FEPSW","FEIC"])
check("EI does not clear NP", h["executes_ei"] and "does not clear NP" in h["important_np_effect"])

n = a["post_fault_network_surface"]
check("CAN EIINT cannot run after predicted SYSERR", n["can_eiint_after_predicted_syserr"] is False and "ID=0 and NP=0" in n["reason"])
check("periodic EIINT cannot run after predicted SYSERR", n["timer_eiint_after_predicted_syserr"] is False)
check("no network non-maskable/reset route recovered", not n["network_fenmi_route_recovered"] and not n["network_internal_reset_route_recovered"])

ver = a["verdict"]
check("live FE registers stay unknown", ver["exact_live_fault_registers_known"] is False)
check("predicted terminal fault is explicit", ver["architecture_predicted_fault"] == "instruction-fetch SYSERR, FEIC 0x13" and "62E42" in ver["architecture_predicted_terminal_handler"])
check("no post-fault CAN primitive", not ver["maskable_can_service_survives_predicted_fault"] and not ver["post_fault_can_recovery_primitive_recovered"])
check("remaining boundary preserved", "live FEIC/FEPC/FEPSW capture" in ver["remaining_boundary"])

print(f"\n{passed} passed, {failed} failed")
raise SystemExit(1 if failed else 0)
