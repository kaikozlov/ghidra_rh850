#!/usr/bin/env python3
"""Verify exact-F33 target-native lateral/static closure from tracked bytes/evidence."""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IMAGE = ROOT / "community/kai/camry-2026/normalized/8965F3307000_CodeFlash.bin"
EVID = ROOT / "data/generated/camry_8965F3307000_lateral_decompiler_evidence.json"
ART = ROOT / "data/generated/camry_8965F3307000_lateral_static.json"
BUILD = ROOT / "tools/build_camry_8965F3307000_lateral_static.py"
CODEFLASH = ROOT / "data/generated/camry_8965F3307000_codeflash.json"
PRODUCT = ROOT / "data/p1me_product_memory.json"
RUNTIME = ROOT / "data/generated/camry_8965F3307000_command5_runtime_carrier.json"
BASELINE = ROOT / "docs/variants/camry-2026-live-baseline.md"
FINDINGS = ROOT / "docs/status/FINDINGS.md"

p = f = 0


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def check(name: str, ok: object) -> None:
    global p, f
    yes = bool(ok)
    p += int(yes)
    f += int(not yes)
    print(f"[{'PASS' if yes else 'FAIL'}] {name}")


img = IMAGE.read_bytes()
evid = json.loads(EVID.read_text(encoding="utf-8"))
art = json.loads(ART.read_text(encoding="utf-8"))
codeflash = json.loads(CODEFLASH.read_text(encoding="utf-8"))
product = json.loads(PRODUCT.read_text(encoding="utf-8"))
runtime = json.loads(RUNTIME.read_text(encoding="utf-8"))
funcs = {int(row["entry"], 16): row for row in evid["functions"]}

print("== deterministic target evidence ==")
check("artifact schema/target exact", art["schema"] == "camry-8965f3307000-lateral-static-v1" and art["target"]["software_id"] == "8965F3307000" and art["target"]["mcu"] == "R7F701381")
check("decompiler evidence exact schema/image", evid["schema"] == "camry-8965f3307000-lateral-decompiler-evidence-v1" and evid["function_count"] == len(funcs) == 31 and evid["image"]["sha256"] == sha(img) == art["target"]["codeflash_sha256"])
for entry, row in sorted(funcs.items()):
    check(f"0x{entry:08X} body hash", sha(img[entry:entry + row["body_size"]]) == row["body_sha256"])
with tempfile.TemporaryDirectory(prefix="camry-f33-lateral-") as td:
    out = Path(td) / "lateral.json"
    r = subprocess.run([sys.executable, str(BUILD), "--out", str(out)], cwd=ROOT, capture_output=True, text=True)
    check("builder exits cleanly", r.returncode == 0)
    check("builder reproduces artifact byte-exact", out.exists() and out.read_bytes() == ART.read_bytes())

print("\n== exact timer / B6 deadline ==")
t = art["foreground_timing"]
check("R7F701381 exact 1MiB product pinned", product["products"]["R7F701381"]["codeflash_bytes"] == 0x100000 and product["products"]["R7F701381"]["regulator"] == "DPS")
check("TAUJ official 80MHz P-Bus source pinned", product["timer"]["p_bus_hz"] == 80_000_000 and any("TAUJ" in x and "80 MHz" in x for x in product["sources"]["datasheet"]["references"]))
check("target timer entries exact", t["loop"] == "0x00066062" and t["timer_init"] == "0x0006639C" and t["timer_reload"] == "0x00066512")
check("target timer config no prescale", t["tps"] == t["brs"] == t["cmor_ch3"] == 0 and "Ramffe50090 = 0;" in funcs[0x6639C]["decompiled_c"] and "Ramffe50080 = 0;" in funcs[0x6639C]["decompiled_c"])
terms = [int.from_bytes(img[0x30DF0 + 4*i:0x30DF4 + 4*i], "little") for i in range(8)]
check("target timer raw terms exact", terms == [16000, 800, 32000, 9200, 80000, 9600, 400000, 10000])
check("first interval 410000 / 5.125ms", t["initial_counts"] == 410000 and t["initial_period_ms"] == 5.125)
check("steady interval 400000 / 5ms", t["steady_counts"] == 400000 and t["steady_period_ms"] == 5.0)
check("foreground polls/clears channel3 flag", t["tick_flag"] == "FFFFB111 bit4" and "(bVar1 & 0x10) == 0" in funcs[0x66062]["decompiled_c"] and "Ramffffb111 = bVar1 & 0xef;" in funcs[0x66062]["decompiled_c"])
check("B6 deadline seven ticks / 35ms", t["b6_successful_receive_reload_ticks"] == codeflash["b6_com"]["deadline_descriptor"]["successful_receive_reload_ticks"] == 7 and t["b6_nominal_steady_timeout_ms"] == 35.0)

print("\n== mode2 command envelope / sequence ==")
e = art["lta_lca_mode2_envelope"]
check("Target Lateral ID11 selects mode2", e["target_lateral_id"] == 11 and e["oem_name"] == "LTA/LCA" and e["internal_mode"] == 2 and "cVar1 == '\\v'" in funcs[0xCEFFC]["decompiled_c"])
check("mode2 absolute 1745 exact", e["absolute_target_raw"] == 1745 and int.from_bytes(img[0x12978:0x1297A], "little") == int.from_bytes(img[0x1A978:0x1A97A], "little") == 1745)
check("mode2 per-gap 78 exact", e["per_effective_sequence_gap_raw"] == 78 and int.from_bytes(img[0x1297A:0x1297C], "little") == int.from_bytes(img[0x1A97A:0x1A97C], "little") == 78)
check("absolute controller-equivalent about 100deg", 99.98 < e["absolute_target_deg_controller_equivalent"] < 100.01)
check("per-gap controller-equivalent about 4.47deg", 4.46 < e["per_effective_sequence_gap_deg_controller_equivalent"] < 4.48)
check("sequence modulus/gap cap exact", e["sequence_modulus"] == 64 and e["sequence_gap_cap"] == 8 and int.from_bytes(img[0xB0620:0xB0622], "little") == 63 and int.from_bytes(img[0xB0622:0xB0624], "little") == 8)
check("maximum ECU relaxed gap exact", e["max_relaxed_gap_delta_raw"] == 624)
check("conditioned internal limits exact", e["conditioned_absolute_doubled_domain"] == int.from_bytes(img[0xB0666:0xB0668], "little") == 3490 and e["conditioned_per_call_doubled_domain"] == int.from_bytes(img[0x1299A:0x1299C], "little") == int.from_bytes(img[0x1A99A:0x1A99C], "little") == 7)
check("target delta deadband exact", e["delta_deadband_raw"] == int.from_bytes(img[0xB061C:0xB061E], "little") == 87)
scale = e["b6_scale"]
check("B6 physical scale exact fraction", scale["fraction_deg_per_b6_count"] == {"numerator": 1024, "denominator": 17870} and abs(scale["mrad_per_b6_count"] - 1.0001215187701138) < 1e-15)
check("Panda boundary rejects ECU gap relaxation", "exact modulo-64 +1" in e["panda_boundary"] and "should not use the ECU gap relaxation" in e["panda_boundary"])

print("\n== companion B6 fields ==")
s = art["secondary_b6_fields"]
check("signal265 suppressor exact role", s["signal265"]["wire"] == "B6[2]" and s["signal265"]["exact_oem_name"] is None and "suppress" in s["signal265"]["role"] and "unaff_gp + -0xa45" in funcs[0xCDA20]["decompiled_c"])
check("signal268 application sequence exact role", s["signal268"]["wire"] == "B7[5:0]" and s["signal268"]["exact_oem_name"] is None and "modulo-64 sequence" in s["signal268"]["role"] and "unaff_gp + -0xa44" in funcs[0xCEC8A]["decompiled_c"])
check("signal269 percentage contribution exact role", s["signal269"]["wire"] == "B8" and "/100" not in s["signal269"]["role"] and "divided by 100" in s["signal269"]["role"] and "unaff_gp + -0xa43" in funcs[0xCE3AA]["decompiled_c"] and ") / 100" in funcs[0xCE3AA]["decompiled_c"])
check("signal270 percentage contribution exact role", s["signal270"]["wire"] == "B9" and "divided by 100" in s["signal270"]["role"] and "unaff_gp + -0xa42" in funcs[0xCDFF8]["decompiled_c"] and ") / 100" in funcs[0xCDFF8]["decompiled_c"])
check("unnamed-field boundary preserved", all(s[k]["exact_oem_name"] is None for k in ("signal265", "signal268", "signal269", "signal270")) and "stay unnamed" in s["boundary"])

print("\n== steering-rate monitor ==")
r = art["steering_rate_monitor"]
check("025 signal189 is Steering Angle Velocity", r["can_id"] == "0x025" and r["signal_id"] == 189 and r["techstream_name"] == "Steering Angle Velocity" and r["did"] == "0x1036")
check("rate callback exact", r["callback"] == "0x0004DBBC" and int.from_bytes(img[0x2939C:0x2939E], "little") == 0x1036 and int.from_bytes(img[0x293A0:0x293A4], "little") == 0x4DBBC)
check("rate raw extraction exact", r["raw_destination"] == "gp-0x37B6" and "FUN_0007d12a(0xbd,299,0xc,0,1,unaff_gp + -0x37b6)" in funcs[0x4B59E]["decompiled_c"])
check("rate diagnostic conversion exact", "unaff_gp + -0x515c" in funcs[0x4DBBC]["decompiled_c"] and "* 0x168) / 0x400" in funcs[0x4DBBC]["decompiled_c"])
check("rate monitor raw threshold exact", r["mode2_abs_raw_threshold"] == int.from_bytes(img[0xB066E:0xB0670], "little") == 100 and r["monitor_entry"] == "0x000CED28")
check("rate monitor persistence exact", r["mode2_persistence_cycles"] == int.from_bytes(img[0x12968:0x1296A], "little") == int.from_bytes(img[0x1A968:0x1A96A], "little") == 79)
check("rate persistence is 395ms at steady tick", r["steady_persistence_time_ms_if_continuously_violating"] == 395.0)
check("rate threshold policy boundary explicit", "not" not in r["boundary"].lower() or "production Panda policy" in r["boundary"])

print("\n== driver torque / Q-current boundaries ==")
d = art["driver_torque"]
check("DID1035 exact Toyota identity/source", d["did"] == "0x1035" and d["techstream_name"] == "Steering Wheel Torque" and d["callback"] == "0x0004DB70" and d["raw_source"] == "gp-0x5158")
check("DID1035 physical formula and display clamp", d["physical_formula"] == "N.m = raw / 256" and d["diagnostic_display_clamp_nm"] == 25.0 and "* 1000) / 0x100" in funcs[0x4DB70]["decompiled_c"] and "25000" in funcs[0x4DB70]["decompiled_c"])
check("DID1035 validity magic exact", d["validity_magic"] == "0xA5AA5AA5" and "-0x5aa5a55b" in funcs[0x4DB70]["decompiled_c"])
check("correct normalized torque acquisition clamp is 2109", d["sensor_acquisition_saturation_raw"] == int.from_bytes(img[0x30E52:0x30E54], "little") == 2109 and d["sensor_acquisition_saturation_calibration"] == "normalized CodeFlash 0x00030E52")
check("2109 raw is about 8.238Nm representation limit", abs(d["sensor_acquisition_saturation_nm"] - 8.23828125) < 1e-12 and d["override_threshold_recovered"] is False and "not a driver-override threshold" in d["boundary"])
check("torque whole-corpus direct/fixed-GP census exact", d["direct_fixed_gp_reference_entries"] == ["0x00035A06", "0x0004DB70", "0x00054244", "0x000564CE"] and evid["fixed_gp_census"]["driver_torque_source"]["token"] == "gp-0x5158")
check("torque cooperative cone direct/fixed-GP intersection empty", d["cooperative_c8_d1_direct_fixed_gp_intersection"] == [])
q = art["q_current"]
check("DID1151 exact Toyota identity/source", q["did"] == "0x1151" and q["techstream_name"] == "Motor Actual Current (Q Axis)" and q["callback"] == "0x0004E394" and q["raw_source"] == "gp-0x50F2")
check("DID1151 formula exact", q["physical_formula"] == "A = raw / 128" and q["diagnostic_formula"] == "displayed centi-A = (raw * 100) / 0x80" and "* 100) / 0x80" in funcs[0x4E394]["decompiled_c"])
check("Q-current whole-corpus direct/fixed-GP census exact", q["direct_fixed_gp_reference_entries"] == ["0x0004E394", "0x00054244", "0x000564CE"] and evid["fixed_gp_census"]["q_current_source"]["token"] == "gp-0x50F2")
check("Q-current cooperative cone direct/fixed-GP intersection empty", q["cooperative_c8_d1_direct_fixed_gp_intersection"] == [] and q["response_threshold_recovered"] is False)
check("negative census boundary explicit", "computed aliases" in evid["fixed_gp_census"]["boundary"].lower() and "dma" in evid["fixed_gp_census"]["boundary"].lower())

print("\n== runtime/static-live boundary ==")
rr = art["runtime_readiness"]
check("runtime anchors exact", rr["application_context_init"] == "0x000715B4" and rr["startup_coordinator"] == "0x000637EE" and rr["startup_final_init"] == "0x000701EA" and rr["foreground_loop"] == "0x00066062")
check("runtime carrier linked/static constructed", rr["static_carrier_constructed"] is True and rr["static_command5_carrier_artifact"] == "data/generated/camry_8965F3307000_command5_runtime_carrier.json" and runtime["boundary"]["static_target_native_carrier_candidate_closed"] is True)
check("live signer gates remain open", rr["live_retention_closed"] is False and rr["live_slot4_permission_closed"] is False and rr["command5_latency_closed"] is False)
b = art["boundary"]
check("static envelope/timing/rate closed", b["target_native_mode2_envelope_closed"] and b["target_native_rate_monitor_closed"] and b["target_native_timing_closed"])
check("override/current response not invented", not b["driver_override_numeric_threshold_closed"] and not b["motor_current_response_threshold_closed"])
check("stock sender/relay/production remain open", not b["stock_b6_cadence_template_freshness_closed"] and not b["relay_suppression_live_closed"] and not b["production_lateral_output_authorized"])
check("runtime carrier itself forbids actuation", runtime["boundary"]["vehicle_actuation_authorized"] is False and runtime["boundary"]["steering_can_transmit_used"] is False)

print("\n== canonical docs ==")
doc = BASELINE.read_text(encoding="utf-8")
for token in ("5.000-ms", "35 ms", "±1745", "78 counts", "signal 265", "Steering Angle Velocity", "±2109", "0x637EE", "FEBF0307"):
    check(f"Camry §12 contains {token}", token in doc)
findings = FINDINGS.read_text(encoding="utf-8")
check("VAR-056 registered", "| VAR-056 |" in findings and "8965F3307000" in findings)
check("VAR-056 verifier named", "verify_camry_8965F3307000_lateral_static.py" in findings)

print(f"\nResults: {p} passed, {f} failed")
raise SystemExit(1 if f else 0)
