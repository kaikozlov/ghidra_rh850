#!/usr/bin/env python3
"""Build the exact-8965F3307000 target-native lateral/static contract.

The builder is intentionally portable: it consumes only tracked exact-F33 bytes and
tracked generated evidence. Ghidra workspace state under build/ is not an input.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import struct
from pathlib import Path
import sys

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))
from tools.camry_f33_corpus import IMAGE, IMAGE_SHA256, body_bytes  # noqa: E402
EVID = REPO / "data/generated/camry_8965F3307000_lateral_decompiler_evidence.json"
CODEFLASH = REPO / "data/generated/camry_8965F3307000_codeflash.json"
PRODUCT = REPO / "data/p1me_product_memory.json"
RUNTIME = REPO / "data/generated/camry_8965F3307000_command5_runtime_carrier.json"
TECH = REPO / "data/generated/corolla_8965H1202000_techstream_correlations.json"
OUT = REPO / "data/generated/camry_8965F3307000_lateral_static.json"



def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha_file(path: Path) -> str:
    return sha(path.read_bytes())


def u16(image: bytes, off: int) -> int:
    return struct.unpack_from("<H", image, off)[0]


def u32(image: bytes, off: int) -> int:
    return struct.unpack_from("<I", image, off)[0]


def need(cond: object, msg: str) -> None:
    if not cond:
        raise ValueError(msg)


def require_tokens(functions: dict[int, dict], entry: int, *tokens: str) -> str:
    need(entry in functions, f"missing evidence function 0x{entry:08X}")
    body = functions[entry]["decompiled_c"]
    for token in tokens:
        need(token in body, f"0x{entry:08X} missing token {token!r}")
    return body


def tech_name(tech: dict, did: str) -> str:
    found: set[str] = set()

    def walk(node: object) -> None:
        if isinstance(node, dict):
            if node.get("primary_data_id") == did and isinstance(node.get("name"), str):
                found.add(node["name"])
            for value in node.values():
                walk(value)
        elif isinstance(node, list):
            for value in node:
                walk(value)

    walk(tech)
    need(len(found) == 1, f"Techstream DID {did} name not unique: {sorted(found)}")
    return next(iter(found))


def build() -> dict:
    image = IMAGE.read_bytes()
    evidence = json.loads(EVID.read_text(encoding="utf-8"))
    codeflash = json.loads(CODEFLASH.read_text(encoding="utf-8"))
    product = json.loads(PRODUCT.read_text(encoding="utf-8"))
    runtime = json.loads(RUNTIME.read_text(encoding="utf-8"))
    tech = json.loads(TECH.read_text(encoding="utf-8"))

    need(len(image) == 0x100000 and sha(image) == IMAGE_SHA256, "exact F33 image drift")
    need(evidence["schema"] == "camry-8965f3307000-lateral-decompiler-evidence-v1", "lateral evidence schema drift")
    need(evidence["software_id"] == "8965F3307000" and evidence["function_count"] == 31, "lateral evidence target/count drift")
    need(evidence["image"]["sha256"] == IMAGE_SHA256, "lateral evidence image drift")

    functions = {int(row["entry"], 16): row for row in evidence["functions"]}
    need(len(functions) == 31, "duplicate/missing lateral evidence entries")
    for entry, row in functions.items():
        need(sha(body_bytes(image, row)) == row["body_sha256"], f"body hash drift 0x{entry:08X}")

    # Timer: 0x6639C clears TAUJ0 TPS/BRS/CMOR and loads the first TDR values;
    # 0x66512 reloads channel 3 with the steady value. The product record binds
    # R7F701381 and the official 80-MHz P-Bus/TAUJ domain.
    require_tokens(functions, 0x66062, "DAT_ffffb110._1_1_", "(bVar1 & 0x10) == 0", "DAT_ffffb110._1_1_ = bVar1 & 0xef;")
    require_tokens(functions, 0x6639C, "Ramffe50090 = 0;", "Ramffe50080 = 0;", "Ramffe5000c = PTR_LAB_0000270e_2_00030e0c + DAT_00030e08 + -1;")
    require_tokens(functions, 0x66512, "Ramffe5000c = DAT_00030e08 + -1;", "FUN_000701ea(uVar3);")
    timer_terms = [u32(image, 0x30DF0 + i * 4) for i in range(8)]
    need(timer_terms == [16000, 800, 32000, 9200, 80000, 9600, 400000, 10000], "F33 TAUJ0 timer terms drift")
    p_bus_hz = product["timer"]["p_bus_hz"]
    need(p_bus_hz == 80_000_000, "P1M-E P-Bus clock drift")
    need(product["products"]["R7F701381"]["codeflash_bytes"] == 0x100000, "R7F701381 product identity drift")
    refs = product["sources"]["datasheet"]["references"]
    need(any("TAUJ" in x and "80 MHz" in x for x in refs), "official TAUJ/P-Bus source note missing")
    initial_counts = timer_terms[6] + timer_terms[7]
    steady_counts = timer_terms[6]

    # Exact mode-2 command envelope and application-sequence behavior.
    require_tokens(functions, 0xCEFFC, "DAT_febeadb0 == '\\v'", "DAT_febecb00 = 2;")
    require_tokens(functions, 0xCEC8A, "DAT_febeadbc", "DAT_000b0620", "DAT_000b0622")
    require_tokens(functions, 0xCEE80, "puVar11 + 0x12de", "puVar11 + 0x12ec")
    require_tokens(functions, 0xCCF0E, "* 2")
    require_tokens(functions, 0xCCFB6, "DAT_febec8b4", "DAT_febec9fe", "DAT_febeca00")
    for off in (0x12978, 0x1A978):
        need(u16(image, off) == 1745 and u16(image, off + 2) == 78, f"mode2 envelope calibration drift at 0x{off:X}")
    need(u16(image, 0xB061C) == 87, "target delta deadband drift")
    need(u16(image, 0xB0620) == 63 and u16(image, 0xB0622) == 8, "sequence modulus/gap cap drift")
    need(u16(image, 0xB0666) == 3490, "conditioned absolute clamp drift")
    need(u16(image, 0x1299A) == u16(image, 0x1A99A) == 7, "conditioned per-call limit drift")

    scale = codeflash["b6_steering_command"]["controller_equivalent_scale"]
    need(scale["fraction_deg_per_b6_count"] == {"numerator": 1024, "denominator": 17870}, "B6 controller-equivalent scale drift")
    deg_per_count = 1024 / 17870

    # Secondary fields: retain consumer behavior, not guessed OEM names.
    require_tokens(functions, 0xCDA20, "DAT_febeadbb", "FUN_000d0a06")
    require_tokens(functions, 0xCE3AA, "DAT_febeadbd", ") / 100")
    require_tokens(functions, 0xCDFF8, "DAT_febeadbe", ") / 100")

    # Steering-rate monitor / diagnostic joins.
    require_tokens(functions, 0x4B59E, "FUN_0007d12a(0xbd,299,0xc,0,1,puVar2 + -0x37b6)")
    require_tokens(functions, 0x4DBBC, "DAT_febe66a4", "* 0x168) / 0x400")
    require_tokens(functions, 0xCED28, "DAT_febeae22", "uVar7 + 1")
    need(u16(image, 0x2939C) == 0x1036 and u32(image, 0x293A0) == 0x4DBBC, "DID1036 row drift")
    need(tech_name(tech, "0x1036") == "Steering Angle Velocity", "DID1036 Techstream name drift")
    need(u16(image, 0xB066E) == 100, "mode2 steering-rate threshold drift")
    need(u16(image, 0x12968) == u16(image, 0x1A968) == 79, "mode2 steering-rate persistence drift")

    # Driver torque diagnostic source and acquisition saturation.
    require_tokens(functions, 0x484D2, "DAT_00030e52")
    require_tokens(functions, 0x4DB70, "DAT_febe6af0 == -0x5aa5a55b", "DAT_febe66a8", "* 1000) / 0x100", "&LAB_000061a8")
    need(u16(image, 0x2938C) == 0x1035 and u32(image, 0x29390) == 0x4DB70, "DID1035 row drift")
    need(u16(image, 0x30E52) == 2109, "normalized F33 torque acquisition saturation drift")
    need(tech_name(tech, "0x1035") == "Steering Wheel Torque", "DID1035 Techstream name drift")

    # Q-axis current diagnostic source.
    require_tokens(functions, 0x4E394, "DAT_febe670e", "* 100) / 0x80")
    need(u16(image, 0x2979C) == 0x1151 and u32(image, 0x297A0) == 0x4E394, "DID1151 row drift")
    need(tech_name(tech, "0x1151") == "Motor Actual Current (Q Axis)", "DID1151 Techstream name drift")

    census = evidence["fixed_gp_census"]
    torque_entries = [row["entry"] for row in census["driver_torque_source"]["entries"]]
    torque_reads = [row["entry"] for row in census["driver_torque_source"]["read_entries"]]
    torque_writes = [row["entry"] for row in census["driver_torque_source"]["write_entries"]]
    q_entries = [row["entry"] for row in census["q_current_source"]["entries"]]
    q_reads = [row["entry"] for row in census["q_current_source"]["read_entries"]]
    q_writes = [row["entry"] for row in census["q_current_source"]["write_entries"]]
    need(torque_entries == ["0x00035A06", "0x0004C000", "0x0004C490", "0x0004DB70", "0x00052CA0", "0x00054244", "0x000564CE", "0x00059448", "0x0005D5E0"], "torque canonical data-reference census drift")
    need(torque_reads == torque_entries[:7] and torque_writes == torque_entries[7:], "torque read/write census drift")
    need(q_entries == ["0x0004E394", "0x00052CA0", "0x00054244", "0x000564CE", "0x00059448", "0x0005D12C"], "Q-current canonical data-reference census drift")
    need(q_reads == q_entries[:4] and q_writes == q_entries[4:], "Q-current read/write census drift")
    need(census["driver_torque_source"]["cooperative_c8_d1_intersection"] == [], "torque cooperative-cone census drift")
    need(census["q_current_source"]["cooperative_c8_d1_intersection"] == [], "Q-current cooperative-cone census drift")

    # Runtime-carrier static linkage only; every live/actuation gate remains false.
    need(runtime["schema"] == "camry-8965f3307000-command5-runtime-carrier-v1", "runtime carrier schema drift")
    need(runtime["scheduler_transfer"]["application_context_init"] == "0x000715B4", "runtime context init drift")
    need(runtime["scheduler_transfer"]["startup_jarl_first"] == "0x000637F6", "runtime startup window drift")
    need(runtime["scheduler_transfer"]["foreground_loop"] == "0x00066062", "runtime foreground drift")
    rb = runtime["boundary"]
    need(rb["static_low_carrier_candidate_closed"] is True and rb["low_carrier_disproved"] is True, "runtime low-carrier correction not closed")
    need(rb["verified_high_tail_live_retention_closed"] is True and rb["verified_variant_ram_exec_requirement_promoted"] is True, "runtime high-tail retention not promoted")
    need(not rb["live_slot4_command5_permission_closed"] and not rb["command5_latency_jitter_closed"] and not rb["application_mode_execution_pivot_closed"], "runtime signer/pivot gates unexpectedly closed")
    need(not rb["vehicle_actuation_authorized"] and not rb["steering_can_transmit_used"], "runtime actuation boundary drift")

    out = {
        "boundary": {
            "driver_override_numeric_threshold_closed": False,
            "interpretation": "The exact F33 external-B6 command envelope, wall-clock receive timeout, sequence semantics, steering-rate monitor, diagnostic torque/current sources, and runtime construction prerequisites are closed at their stated evidence grades. Driver override policy, motor-current response policy, live signer gates, and relay-correct actuation remain dynamic/open. Stock B6 sender/template behavior is not a prerequisite for explaining factory LTA because exact F33 has a B6-independent internal assist path and retained LTA/LCA intervals contain zero B6.",
            "motor_current_response_threshold_closed": False,
            "production_lateral_output_authorized": False,
            "relay_suppression_live_closed": False,
            "stock_b6_cadence_template_freshness_closed": False,
            "stock_b6_template_is_current_camry_prerequisite": False,
            "target_native_mode2_envelope_closed": True,
            "target_native_rate_monitor_closed": True,
            "target_native_timing_closed": True,
        },
        "driver_torque": {
            "boundary": "The 2109-raw acquisition/representation saturation is not a driver-override threshold. The canonical whole-project data-reference census includes both readers and writers of FEBE66A8; the negative control-cone result remains empty. Computed aliases without a Ghidra data reference and DMA remain outside the census.",
            "callback": "0x0004DB70",
            "cooperative_c8_d1_direct_fixed_gp_intersection": census["driver_torque_source"]["cooperative_c8_d1_intersection"],
            "diagnostic_display_clamp_nm": 25.0,
            "did": "0x1035",
            "direct_fixed_gp_reference_entries": torque_entries,
            "read_reference_entries": torque_reads,
            "write_reference_entries": torque_writes,
            "resolved_source_address": census["driver_torque_source"]["resolved_address"],
            "override_threshold_recovered": False,
            "physical_formula": "N.m = raw / 256",
            "raw_source": "gp-0x5158",
            "sensor_acquisition_saturation_calibration": "normalized CodeFlash 0x00030E52",
            "sensor_acquisition_saturation_nm": 2109 / 256,
            "sensor_acquisition_saturation_raw": 2109,
            "techstream_name": "Steering Wheel Torque",
            "validity_magic": "0xA5AA5AA5",
        },
        "foreground_timing": {
            "b6_nominal_steady_timeout_ms": 7 * steady_counts * 1000 / p_bus_hz,
            "b6_successful_receive_reload_ticks": codeflash["b6_com"]["deadline_descriptor"]["successful_receive_reload_ticks"],
            "boundary": "The wall-clock conversion is target-native: exact R7F701381 uses TAUJ on the P1M-E 80-MHz P-Bus and F33 programs TPS/BRS/CMOR=0. This supersedes the prior H-timing transfer boundary.",
            "brs": 0,
            "cmor_ch3": 0,
            "initial_counts": initial_counts,
            "initial_period_ms": initial_counts * 1000 / p_bus_hz,
            "loop": "0x00066062",
            "p_bus_hz": p_bus_hz,
            "steady_counts": steady_counts,
            "steady_period_ms": steady_counts * 1000 / p_bus_hz,
            "tick_flag": "FFFFB111 bit4",
            "timer": "TAUJ0 channel 3",
            "timer_init": "0x0006639C",
            "timer_reload": "0x00066512",
            "tps": 0,
        },
        "lta_lca_mode2_envelope": {
            "absolute_target_deg_controller_equivalent": 1745 * deg_per_count,
            "absolute_target_raw": 1745,
            "b6_scale": scale,
            "conditioned_absolute_doubled_domain": 3490,
            "conditioned_per_call_doubled_domain": 7,
            "delta_deadband_raw": 87,
            "internal_mode": 2,
            "max_relaxed_gap_delta_raw": 8 * 78,
            "oem_name": "LTA/LCA",
            "panda_boundary": "The ECU tolerates repeated/skipped application counters by widening the delta window up to 8x. A Panda implementation should instead require exact modulo-64 +1 and should not use the ECU gap relaxation as a sender allowance.",
            "per_effective_sequence_gap_deg_controller_equivalent": 78 * deg_per_count,
            "per_effective_sequence_gap_raw": 78,
            "sequence_gap_cap": 8,
            "sequence_modulus": 64,
            "target_lateral_id": 11,
        },
        "q_current": {
            "boundary": "No target-native measured-Q-current-vs-command comparator is recovered through canonical direct data references in the cooperative cone. The whole-project census includes readers and writers of FEBE670E; numeric representation limits are not a motor-response safety threshold.",
            "callback": "0x0004E394",
            "cooperative_c8_d1_direct_fixed_gp_intersection": census["q_current_source"]["cooperative_c8_d1_intersection"],
            "diagnostic_formula": "displayed centi-A = (raw * 100) / 0x80",
            "did": "0x1151",
            "direct_fixed_gp_reference_entries": q_entries,
            "read_reference_entries": q_reads,
            "write_reference_entries": q_writes,
            "resolved_source_address": census["q_current_source"]["resolved_address"],
            "physical_formula": "A = raw / 128",
            "raw_source": "gp-0x50F2",
            "response_threshold_recovered": False,
            "techstream_name": "Motor Actual Current (Q Axis)",
        },
        "runtime_readiness": {
            "application_context_init": runtime["scheduler_transfer"]["application_context_init"],
            "application_mode_execution_pivot_closed": rb["application_mode_execution_pivot_closed"],
            "command5_latency_closed": rb["command5_latency_jitter_closed"],
            "foreground_loop": runtime["scheduler_transfer"]["foreground_loop"],
            "high_tail_live_retention_closed": rb["verified_high_tail_live_retention_closed"],
            "high_tail_base": runtime["verified_high_tail_carrier"]["base"],
            "high_tail_end_exclusive": runtime["verified_high_tail_carrier"]["end_exclusive"],
            "live_slot4_permission_closed": rb["live_slot4_command5_permission_closed"],
            "low_carrier_disproved": rb["low_carrier_disproved"],
            "startup_coordinator": "0x000637EE",
            "startup_final_init": runtime["scheduler_transfer"]["startup_final_init"],
            "static_low_carrier_constructed": rb["static_low_carrier_candidate_closed"],
            "static_command5_carrier_artifact": str(RUNTIME.relative_to(REPO)),
        },
        "schema": "camry-8965f3307000-lateral-static-v1",
        "secondary_b6_fields": {
            "boundary": "Only consumer behavior is named. Remaining protected B6 secondary fields stay unnamed without an exact Toyota engineering label.",
            "signal265": {"exact_oem_name": None, "role": "when 1, suppress one additive controller contribution", "wire": "B6[2]"},
            "signal268": {"exact_oem_name": None, "role": "application modulo-64 sequence", "wire": "B7[5:0]"},
            "signal269": {"exact_oem_name": None, "role": "percentage contribution divided by 100; zero eliminates that contribution", "special_values": "201/202/203 select calibration-specific alternate behavior", "wire": "B8"},
            "signal270": {"exact_oem_name": None, "role": "percentage contribution divided by 100; zero eliminates that contribution", "wire": "B9"},
        },
        "sources": {
            "codeflash": {"path": str(IMAGE.relative_to(REPO)), "sha256": IMAGE_SHA256},
            "codeflash_contract": {"path": str(CODEFLASH.relative_to(REPO)), "sha256": sha_file(CODEFLASH)},
            "decompiler_evidence": {"path": str(EVID.relative_to(REPO)), "sha256": sha_file(EVID)},
            "p1me_product_memory": {"path": str(PRODUCT.relative_to(REPO)), "sha256": sha_file(PRODUCT)},
            "runtime_carrier": {"path": str(RUNTIME.relative_to(REPO)), "sha256": sha_file(RUNTIME)},
            "techstream_correlations": {"path": str(TECH.relative_to(REPO)), "sha256": sha_file(TECH)},
        },
        "steering_rate_monitor": {
            "boundary": "The raw threshold and 79-cycle persistence are firmware facts. The diagnostic callback independently names this measurement Steering Angle Velocity; production Panda policy may trip immediately above the raw threshold instead of reproducing EPS persistence.",
            "callback": "0x0004DBBC",
            "can_id": "0x025",
            "did": "0x1036",
            "mode2_abs_raw_threshold": 100,
            "mode2_persistence_cycles": 79,
            "monitor_entry": "0x000CED28",
            "raw_destination": "gp-0x37B6",
            "signal_id": 189,
            "steady_persistence_time_ms_if_continuously_violating": 79 * steady_counts * 1000 / p_bus_hz,
            "techstream_name": "Steering Angle Velocity",
            "wire": "signed12 at COM offset 0x12B",
        },
        "target": {"codeflash_sha256": IMAGE_SHA256, "mcu": "R7F701381", "software_id": "8965F3307000"},
    }
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", type=Path, default=OUT)
    args = ap.parse_args()
    obj = build()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
