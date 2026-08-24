#!/usr/bin/env python3
"""Build the exact Corolla H protected-B6 request/validity/loss receiver contract."""
from __future__ import annotations
import argparse, hashlib, json, struct
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
IMAGE = REPO / "community/albinoelephant/normalized/8965H1202000_CodeFlash.bin"
EVID = REPO / "data/generated/corolla_8965H1202000_b6_receiver_contract_decompiler_evidence.json"
CAN_EVID = REPO / "data/generated/corolla_8965H1202000_can_com_decompiler_evidence.json"
TECH = REPO / "data/generated/corolla_8965H1202000_techstream_correlations.json"
P5 = REPO / "data/generated/techstream_v18/p5_lateral_control_semantics.json"
OUT = REPO / "data/generated/corolla_8965H1202000_b6_receiver_contract.json"

GP = 0xFEBEB800
TP = 0x00023D6C
PDU_TABLE = 0x22620
STATUS_CFG = 0x28CCC
PDU42 = 42
STATUS_SLOT = 0x18

def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def need(text: str, *tokens: str) -> None:
    missing = [x for x in tokens if x not in text]
    if missing:
        raise ValueError("missing decompiler token(s): " + ", ".join(missing))

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--image", type=Path, default=IMAGE)
    ap.add_argument("--evidence", type=Path, default=EVID)
    ap.add_argument("--out", type=Path, default=OUT)
    args = ap.parse_args()
    image = args.image.read_bytes()
    ev = json.loads(args.evidence.read_text())
    can_ev = json.loads(CAN_EVID.read_text())
    tech = json.loads(TECH.read_text())
    p5 = json.loads(P5.read_text())
    if len(image) != 0x100000 or sha(image) != ev["image"]["sha256"]:
        raise ValueError("H image/evidence identity drift")
    if ev["function_count"] != 33:
        raise ValueError("B6 receiver evidence count drift")
    funcs = {int(x["entry"], 16): x["decompiled_c"] for x in ev["functions"]}
    can_funcs = {int(x["entry"], 16): x["decompiled_c"] for x in can_ev["functions"]}
    rx = can_funcs[0x76A3C]

    # Exact PDU42 descriptor.  The first u16 is consumed by 769F6/7683C as the
    # receive deadline reload/countdown value; flag 0x04 enables the activity marker.
    pdu_addr = PDU_TABLE + PDU42 * 8
    pdu_raw = image[pdu_addr:pdu_addr + 8]
    pdu = struct.unpack("<HBBHBB", pdu_raw)
    if pdu != (6, 0, 0, 32, 0, 12):
        raise ValueError(f"PDU42 descriptor drift: {pdu!r}")
    if TP - 0x174C != PDU_TABLE:
        raise AssertionError("TP-relative PDU table arithmetic")
    need(funcs[0x769F6], "* 8 + unaff_tp + -0x174c", "+ param_2;", "*puVar2 < uVar1", "*puVar2 = uVar1")
    need(funcs[0x7683C], "sVar9 = sVar9 + -1;", "sVar9 == 0", "*pbVar3 = *pbVar3 | 2;", "FUN_00087aa0")
    need(rx, "FUN_000769f6(param_1,1);", "if ((bVar2 & 4) != 0)", "FUN_00087a82(param_1);")
    need(funcs[0x87A5E], "-0x663c) = 0x5a")
    need(funcs[0x87A82], "-0x663c) = 0;", "-0x65dc + param_1", "+ '\\x01'")
    need(funcs[0x87AA0], "-0x663c) = 0x5a")

    # Exact status-slot configuration for B6.  This is a second, slower receive
    # status qualifier; the direct activity marker is ORed into the exposed status
    # immediately, so the 440 count is not the primary steering-loss cutoff.
    status_addr = STATUS_CFG + STATUS_SLOT * 8
    status_raw = image[status_addr:status_addr + 8]
    if status_raw.hex() != "2a00000bb8010200":
        raise ValueError(f"slot18 status config drift: {status_raw.hex()}")
    status_threshold = struct.unpack_from("<H", status_raw, 4)[0]
    if status_raw[0] != PDU42 or status_threshold != 440:
        raise AssertionError("slot18 config decode")
    need(funcs[0x44538], "-0x3bff) = 1;", "-0x3c50) = 0;")
    need(funcs[0x445C0], "(&DAT_00028ccc)[param_1 * 8]", "-0x663c) == 'Z'", "uVar3 = 0x22;", "uVar3 = 0x11;", "uVar3 = 0;")
    need(funcs[0x4460C], "-0x663c) != 'Z'", "uVar2 = 0x22;", "uVar2 = 0;")
    need(funcs[0x44658], "FUN_000445c0(param_1)", "FUN_0004460c(param_1)", "uVar2 = 2;")
    need(funcs[0x446EC], "FUN_00044658(iVar5)", "bVar4 | cVar3 != '\\0'", "-0x3bff")
    need(funcs[0x44744], "< 0x1b", "-0x3bff", "return 1;")

    # Both deadline and status work are executed from the same CH3 foreground tick.
    need(funcs[0x5F30C], "DAT_ffffb111", "& 0x10", "FUN_0005faf2();")
    need(funcs[0x5FAF2], "FUN_00073564();", "FUN_00053030();")
    need(funcs[0x73564], "FUN_0007683c();")
    need(funcs[0x53030], "FUN_00058bbc", "FUN_00059574")
    need(funcs[0x58BBC], "FUN_000446ec();", "FUN_00046a10();", "FUN_0005262c();")
    need(funcs[0x59574], "FUN_000446ec();", "FUN_00046a10();", "FUN_0005262c();")

    # Status chain: B6 slot18 -> generated raw status -> staging -> snapshot ADB9.
    need(funcs[0x46A10], "FUN_00044744(0x18);", "unaff_gp + -0x3a60")
    need(funcs[0x5262C], "*(undefined1 *)(unaff_gp + 0x3932) = *(undefined1 *)(unaff_gp + -0x3a60);")
    need(funcs[0xB8EE4], "*(undefined1 *)(unaff_gp + -0xa47) = *(undefined1 *)(unaff_gp + 0x3932);")
    if not (GP - 0x3A60 == 0xFEBE7DA0 and GP + 0x3932 == 0xFEBEF132 and GP - 0xA47 == 0xFEBEADB9):
        raise AssertionError("B6 status GP arithmetic")

    # Main cooperative request gate and request selector.
    need(funcs[0xCC7F8], "FUN_000ba090(0x10)", "FUN_000ba090(0x18)", "(uVar2 | uVar3) != 0x5a", "-0xa47) == '\\0'", "+ 0xa6d")
    need(funcs[0xCBE6E], "-0xb43) == '\\0'", "+ 0xa6d) == '\\x01'", "+ 0xa72", "-0xa50")
    target_id = p5["power_steering"]["target_lateral_id_semantics"]
    values = {int(k): v for k, v in target_id["value_dictionary"].items()}
    accepted = {1: "PCS", 4: "LDA", 10: "Hands Off LTA", 11: "LTA/LCA", 19: "PDA"}
    if values.get(0) != "No Request (Manual Operation)" or any(values.get(k) != v for k, v in accepted.items()):
        raise ValueError("Target Lateral ID request dictionary drift")

    # The generated B6 unpacker itself pins signal ID, payload offset, width, bit
    # offset and signedness. PDU42 starts at buffer offset 0x1A7, so
    # 0x1AD/0x1AE/0x1B1 are B6 bytes 6/7/10.
    need(funcs[0x46A10],
         "FUN_0007643a(0x102,0x1ad,1,2,0,unaff_gp + -0x3a68);",
         "FUN_0007643a(0x104,0x1ae,2,6,0,unaff_gp + -0x3a66);",
         "FUN_0007643a(0x105,0x1ae,6,0,0,unaff_gp + -0x3a65);",
         "FUN_0007643a(0x108,0x1b1,1,7,0,unaff_gp + -0x3a62);",
         "FUN_0007643a(0x109,0x1b1,3,0,0,unaff_gp + -0x3a5f);")

    # Companion B6 scalar fields and sequence semantics.
    need(funcs[0x5262C], "0x3929) = *(undefined1 *)(unaff_gp + -0x3a68)", "0x392b) = *(undefined1 *)(unaff_gp + -0x3a66)", "0x392c) = *(undefined1 *)(unaff_gp + -0x3a65)", "0x392f) = *(undefined1 *)(unaff_gp + -0x3a62)", "0x3941) = *(undefined1 *)(unaff_gp + -0x3a5f)")
    need(funcs[0xB8EE4], "-0xa45) = *(undefined1 *)(unaff_gp + 0x3929)", "-0xa3e) = *(undefined1 *)(unaff_gp + 0x392b)", "-0xa44) = *(undefined1 *)(unaff_gp + 0x392c)", "-0xa3f) = *(undefined1 *)(unaff_gp + 0x392f)", "-0xa27) = *(undefined1 *)(unaff_gp + 0x3941)")
    if struct.unpack_from("<H", image, 0xAFCE8)[0] != 63 or struct.unpack_from("<H", image, 0xAFCEA)[0] != 8:
        raise ValueError("B6 sequence constants drift")
    need(funcs[0xCB246], "-0xa44", "DAT_000afce8", "DAT_000afcea", "+ 0xa48", "+ 0xa4a", "+ 0xa4c")
    need(funcs[0xCB4F4], "+ 0xa4c")
    need(funcs[0xCBEEE], "-0xa45) != '\\x01'", "+ 0xa6e", "+ 0xa6f", "+ 0xa70", "+ 0xa71")
    need(funcs[0xC89D2], "-0xa3e", "cVar2 == '\\0'", "cVar2 == '\\x03'", "cVar2 == '\\x01' || cVar2 == '\\x02'")
    need(funcs[0xC8D42], "-0xa3e", "cVar3 == '\\x02'")
    need(funcs[0xC819E], "-0xa47) == 0", "-0xa3f) == '\\0'", "-0xa3f) != '\\0'", "-0xa47) & 2")
    need(funcs[0xC825A], "-0xa50", "\\x19", "\\x1b", "+ 0x779")
    need(funcs[0xCCF58], "FUN_000ba090(0x18)", "-0xa47) != '\\0'", "-0xa27")

    # Exact OEM missing-message join.
    b6row = next(x for x in tech["communication_monitor_dtc"]["rows"] if x["can_id"] == "0x0B6")
    if not (b6row["pdu_id"] == 42 and b6row["status_slot"] == "0x18" and b6row["dtc"]["techstream_code"] == "U012987" and b6row["dtc"]["techstream_failure"] == "Missing Message"):
        raise ValueError("B6 Techstream missing-message join drift")

    out = {
        "schema": "corolla-8965H1202000-b6-receiver-contract-v1",
        "software_id": "8965H1202000",
        "sources": {
            "codeflash": {"path": str(args.image.relative_to(REPO)), "sha256": sha(image)},
            "decompiler_evidence": {"path": str(args.evidence.relative_to(REPO)), "sha256": sha(args.evidence.read_bytes()), "function_count": ev["function_count"]},
            "can_com_evidence": {"path": str(CAN_EVID.relative_to(REPO)), "sha256": sha(CAN_EVID.read_bytes()), "rx_indication": "0x00076A3C"},
            "techstream_correlations": {"path": str(TECH.relative_to(REPO)), "sha256": sha(TECH.read_bytes())},
            "p5_lateral_semantics": {"path": str(P5.relative_to(REPO)), "sha256": sha(P5.read_bytes())},
        },
        "request_contract": {
            "signal_id": 254,
            "wire_byte": 3,
            "bit_length": 6,
            "snapshot": "0xFEBEADB0",
            "oem_dictionary": "Target Lateral ID",
            "no_request": {"value": 0, "label": values[0]},
            "accepted_active_requests": {str(k): v for k, v in accepted.items()},
            "decoder": "0x000CBE6E",
            "common_active_flag": "0xFEBEC272",
            "receiver_gates": ["0xFEBEACBD == 0", "0xFEBEC26D == 1"],
            "classification": "supported-target-lateral-request-id",
            "boundary": "Signal254 itself carries the OEM request/source ID. H only activates the common cooperative-control flag for the five supported active IDs; unsupported/No-Request values do not select the active controller."
        },
        "communication_supervision": {
            "can_id": "0x0B6",
            "pdu_id": 42,
            "status_slot": "0x18",
            "pdu_descriptor": {
                "address": f"0x{pdu_addr:08X}",
                "raw_hex": pdu_raw.hex(),
                "deadline_value_ticks": pdu[0],
                "successful_rx_reload_ticks": pdu[0] + 1,
                "length": pdu[3],
                "flags": pdu[5],
                "activity_tracking_enabled": bool(pdu[5] & 4),
            },
            "successful_receive": {
                "entry": "0x00076A3C",
                "actions": ["0x769F6(pdu, 1) reloads the deadline countdown", "0x87A82(pdu) clears activity[pdu] to 0 when descriptor flag 0x04 is set"],
            },
            "deadline_expiry": {
                "countdown": "0x0007683C",
                "expiry_action": "0x87AA0(pdu) sets activity[pdu] to 0x5A",
                "primary_cutout_after_foreground_ticks": pdu[0] + 1,
                "absolute_time_supported": False,
                "absolute_time_boundary": "Both paths run from the TAUJ0-CH3 foreground cyclic tick, but the CH3 timer prescaler/TDR is not statically recoverable from this image; do not convert the 7-tick receiver deadline to milliseconds.",
            },
            "status_qualifier": {
                "config_address": f"0x{status_addr:08X}",
                "raw_hex": status_raw.hex(),
                "pdu_id": status_raw[0],
                "configured_extended_threshold_ticks": status_threshold,
                "extended_state_condition": "0x445C0 emits state 0x22 only after its counter exceeds 440 while activity[PDU42] remains 0x5A; 0x44658 exposes bit/value 2 for that extended state",
                "primary_cutout_precedes_extended_state": True,
            },
            "status_dataflow": {
                "slot_accessor": "0x44744(0x18)",
                "raw": "0xFEBE7DA0",
                "staging": "0xFEBEF132",
                "snapshot": "0xFEBEADB9",
                "initial_value": 1,
                "healthy_value": 0,
                "loss_value": "nonzero immediately on activity[PDU42]==0x5A; extended bit 0x02 may appear after the slower qualifier",
            },
            "steering_enable_gate": {
                "entry": "0x000CC7F8",
                "health_slots": ["0x10 (CAN 0x025)", "0x18 (CAN 0x0B6)"],
                "output": "0xFEBEC26D",
                "condition": "combined slot health is not 0x5A and B6 receive-status snapshot 0xFEBEADB9 == 0",
                "effect": "CBE6E cannot assert any cooperative profile/common-active flag when this gate is false",
            },
            "scheduler": {
                "foreground_loop": "0x0005F30C",
                "tick_source": "TAUJ0 CH3 EIRF at 0xFFFFB111 bit 0x10",
                "lower_deadline_chain": "5F30C -> 5FAF2 -> 73564 -> 7683C",
                "status_chain": "5F30C -> 5FAF2 -> 53030 -> (58BBC transition | 59574 steady) -> 446EC/46A10/5262C",
                "same_tick_domain": True,
            },
            "techstream": {
                "dtc": b6row["dtc"]["techstream_code"],
                "description": b6row["dtc"]["techstream_description"],
                "failure": b6row["dtc"]["techstream_failure"],
                "dem_event": b6row["dem_event"],
            },
        },
        "companion_fields": {
            "258": {
                "wire": "B6 bit2",
                "snapshot": "0xFEBEADBB",
                "consumer": "0x000CBEEE",
                "semantics": "profile-dependent cooperative-control contribution gate; value 1 is required for one B6/profile-dependent controller contribution when profile flags are active",
                "oem_name_identified": False,
                "family_vocabulary_candidate": "Cooperative Control in Progress Flag",
                "boundary": "The P5 diagnostic family exposes this OEM name, but exact H lacks DID 0x1CEE and static evidence does not prove signal258 is that diagnostic field."
            },
            "260": {
                "wire": "B7 bits7:6",
                "snapshot": "0xFEBEADC2",
                "consumers": ["0x000C89D2", "0x000C8D42"],
                "semantics": "four-state controller mode/transition selector with distinct behavior for 0/1/2/3",
                "oem_name_identified": False,
            },
            "261": {
                "wire": "B7 bits5:0",
                "snapshot": "0xFEBEADBC",
                "consumer": "0x000CB246",
                "classification": "rolling-sequence-counter",
                "counter_bits": 6,
                "wrap_max": 63,
                "modulus": 64,
                "gap_cap": 8,
                "delta_formula": "delta = (current - previous) mod 64",
                "effective_gap_formula": "effective_gap = 1 when delta <= 1, otherwise min(delta, 8)",
                "downstream": "raw delta and capped effective gap are stored at GP+0xA4A/GP+0xA4C; CB4F4 consumes the capped gap in target plausibility/supervision",
                "strict_plus_one_required": False,
            },
            "264": {
                "wire": "B10 bit7",
                "snapshot": "0xFEBEADC1",
                "consumer": "0x000C819E",
                "semantics": "special-control validity/inhibit input; zero is required to enter/retain the C819E latch and nonzero clears it",
                "scope_boundary": "C825A uses that latch around AP/Remote Parking IDs 25/27, so this must not be generalized as the primary LTA request bit.",
                "oem_name_identified": False,
            },
            "265": {
                "wire": "B10 bits2:0",
                "snapshot": "0xFEBEADD9",
                "consumer": "0x000CCF58",
                "semantics": "mode/status value republished only while B6 receive status is healthy",
                "oem_name_identified": False,
            },
        },
        "static_conclusion": {
            "request_selection_closed": True,
            "primary_loss_cutout_closed_in_ticks": True,
            "primary_loss_cutout_ticks": pdu[0] + 1,
            "wall_clock_timeout_closed": False,
            "sequence_counter_closed": True,
            "sequence_modulus": 64,
            "sequence_gap_cap": 8,
            "secondary_field_names_closed": False,
            "upstream_producer_closed": False,
            "next_static_target": "recover the upstream FRC_P5/Brake producer and SecOC sender/freshness contract; exact signal258/260/264/265 OEM names remain bounded unless an independent producer/diagnostic join appears",
        },
        "evidence_boundary": (
            "This closes the H/F EPS receiver-side request and communication-loss contract in scheduler ticks: signal254 selects the active Target Lateral ID, PDU42 is reloaded to 7 foreground ticks on successful reception, expiry marks B6 unhealthy and disables cooperative selection through ADB9/C26D, and signal261 is a modulo-64 rolling sequence counter with an 8-gap cap. "
            "It does not infer milliseconds, sender cadence, sender implementation, SecOC freshness/key behavior, or exact OEM names for the secondary B6 fields."
        ),
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"out": str(args.out), "loss_ticks": pdu[0] + 1, "sequence_modulus": 64}, indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
