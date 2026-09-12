#!/usr/bin/env python3
"""Verify exact-F33 incident branch and recovery-epilogue byte geometry."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools.targets.camry.analysis import analyze_f33_recovery_structure as recovery

passed = failed = 0


def check(name: str, condition: object) -> None:
    global passed, failed
    ok = bool(condition)
    passed += int(ok)
    failed += int(not ok)
    print(f"[{'PASS' if ok else 'FAIL'}] {name}")


image = recovery.IMAGE.read_bytes()
report = recovery.analyze(image)
incident = report["incident"]
geometry = incident["clear_bits_encoding_geometry"]

check("exact stock image identity", report["source"]["sha256"] == recovery.IMAGE_SHA256)
check(
    "recorded malformed JARL32 stream is exact",
    incident["instruction_with_stock_successor"] == "ff02925b2436",
)
check("malformed target is reconstructed", incident["decoded_bad_target"] == "0x362BFE04")
check(
    "candidate clears bits only",
    geometry["candidate_instruction"] == "ff0212010000"
    and geometry["cleared_bit_mask"] == "0000805a2436",
)
check(
    "candidate reaches matching one-LP epilogue",
    geometry["candidate_target"] == "0x0007A384"
    and geometry["candidate_target_bytes"] == "40063f00"
    and geometry["matching_entry_prologue"]["bytes"] == "80072100",
)
check("displacement-subset census is exact", geometry["subset_displacement_count"] == 16384)
check("no clear-bits displacement reaches resident signer", geometry["resident_subset_targets"] == [])

# Boot/reset/safety outputs relevant to post-incident recovery.
clear = report["boot_cold_flash_error_clear"]
check(
    "cold startup clears CodeFlash ECC status before validity",
    clear["address"] == "0x00000802"
    and clear["bytes"].startswith("3e060420c6ff0f0a010d010a030d"),
)
retained = report["boot_retained_reset_record"]
check(
    "retained reset record is read before ordinary validity call",
    retained["reader_call"]["target"] == "0x00000E54"
    and retained["validity_call_after_reader"]["target"] == "0x0000119E"
    and int(retained["reader_call"]["address"], 16) < int(retained["validity_call_after_reader"]["address"], 16),
)
errout = report["application_errorout_mask_init"]
check(
    "application programs bounded ECM ERROROUT masks",
    errout["startup_call"]["target"] == "0x00063338"
    and errout["ecmemk0"]["value"] == "0xFFFFFFE1"
    and errout["ecmemk1"]["value"] == "0xFFFFFFFF"
    and errout["ecmemk2"]["value"] == "0x3FFFFFFF",
)

ecm = report["application_ecm_maskable_interrupt"]
check(
    "INTECM vector and exact enabled-source set are recovered",
    ecm["interrupt_number"] == 8
    and ecm["manual_interrupt_name"] == "INTECM"
    and ecm["intbp_slot"] == "0x00020220"
    and ecm["intbp_target"] == "0x00071AE4"
    and ecm["micfg0_value"] == "0x100B001E"
    and ecm["enabled_sources"] == [1, 2, 3, 4, 16, 17, 19, 28],
)
check(
    "INTECM handler reset fallback and dedicated source handlers are exact",
    ecm["handler"]["source_1_to_4_target"] == "0x0007162E"
    and ecm["handler"]["source_16_17_target"] == "0x00065CDA"
    and ecm["handler"]["source_19_target"] == "0x00065DD6"
    and ecm["handler"]["source_28_target"] == "0x00065F24"
    and ecm["handler"]["unclassified_fallback_reset"]["target"] == "0x00061940",
)
check(
    "RS-CANFD ECM sources are outside exact F33 INTECM mask",
    ecm["rscanfd_ecm_sources_not_enabled"] == [22, 37, 54]
    and not ({22, 37, 54} & set(ecm["enabled_sources"])),
)

# The board-level reset/supervisor clock is exported on P4_5 as EXTCLK1O.
sup = report["external_supervisor_clock"]
p45 = sup["p4_5"]
check(
    "reset-time port table selects P4_5 third-alternative output",
    p45["p"] == 0
    and p45["pmc"] == 1
    and p45["pm"] == 0
    and p45["pfc"] == 0
    and p45["pfce"] == 1
    and p45["pfcae"] == 0
    and p45["selector_bits_pfcae_pfce_pfc"] == "010",
)
clock_init = sup["boot_clock_init"]
check(
    "boot initializes EXTCLK1O source selector and 0x50 divider",
    clock_init["function"] == "0x000010C6"
    and clock_init["source_select_register"] == "0xFFF890C0"
    and clock_init["source_select_value"] == 4
    and clock_init["divider_register"] == "0xFFF88818"
    and clock_init["divider_value"] == "0x00000050",
)
check(
    "periodic supervisor repairs divider to 0x50",
    sup["periodic_repair"]["function"] == "0x000619C0"
    and sup["periodic_repair"]["caller"] == "0x000667B6"
    and sup["periodic_repair"]["expected_divider"] == "0x00000050",
)
check(
    "terminal reset explicitly stops clock and forces P4_5 low port mode",
    sup["terminal_reset"]["function"] == "0x00061940"
    and sup["terminal_reset"]["clock_stop_via"] == "0x00061906"
    and sup["terminal_reset"]["clock_stop_mode"] == "0xFF"
    and sup["terminal_reset"]["p4_5_update_mask"] == "0x00200000",
)

# Ordinary alternate sessions are selected through ROM lists, including a
# callback absent from the canonical function inventory. Do not infer absence
# of a service or an executor merely from a direct-call/function-name census.
modes = report["network_diagnostic_modes"]
service_lists = {row["source_key"]: row for row in modes["service_lists"]}
check("all three runtime service-list selectors are represented", set(service_lists) == {2, 3, 4})
check(
    "runtime list sizes and shared-object counts are exact",
    [len(service_lists[key]["services"]) for key in (2, 3, 4)] == [17, 6, 5]
    and {s["index"] for row in service_lists.values() for s in row["services"]} == set(range(23)),
)

def configured_modes(key: int, service: str) -> list[int]:
    selected = [row for row in service_lists[key]["services"] if row["service"] == service]
    return [s["subfunction"] for row in selected for s in row["mode_subfunctions"]]

check(
    "alternate 0x40 session belongs to the third list, not the primary programming list",
    configured_modes(2, "0x10") == [1, 2, 3]
    and configured_modes(3, "0x10") == [1, 3]
    and configured_modes(4, "0x10") == [1, 0x40],
)
sessions = {row["session"]: row for row in modes["session_definitions"]}
check(
    "0x40 uses immediate-session kind, not the programming handoff kind",
    sessions[0x40]["transition_kind"] == 0
    and sessions[2]["transition_kind"] == 2
    and sessions[0x40]["address"] == "0x00026140",
)
check(
    "0x40 and programming wrappers call the same ordinary session processor",
    modes["session_40_wrapper"]["body"]["bytes"] == "80072100860020464000bfff0cff40063f00"
    and modes["session_40_wrapper"]["common_handler_call"]["target"] == "0x00095C52"
    and modes["session_02_wrapper"]["common_handler_call"]["target"] == "0x00095C52",
)
event = modes["ordinary_dispatch_event"]
check(
    "event zero reaches the shared dispatcher through the previously unnamed callback",
    event["handler"] == "0x000922AA"
    and event["dispatcher_adapter_call"]["target"] == "0x00091C0A"
    and event["service_dispatcher_call"]["target"] == "0x00091566",
)
check(
    "enhanced-address CommunicationControl subfunctions are not in any selected list",
    configured_modes(2, "0x28") == [0, 1, 3]
    and configured_modes(3, "0x28") == [0, 1, 3]
    and configured_modes(4, "0x28") == [],
)
comm = modes["communication_control_configuration"]
check(
    "one ordinary communication channel, no configured specific subnet or subnode",
    comm["all_channel_count"] == 1
    and comm["all_channels"] == [{"enabled": 1, "channel": 0}]
    and comm["specific_channel_count"] == comm["subnode_count"] == 0
    and comm["specific_channel_table"] == comm["subnode_table"] == "0x00000000",
)

print(f"Results: {passed} passed, {failed} failed")
raise SystemExit(1 if failed else 0)
