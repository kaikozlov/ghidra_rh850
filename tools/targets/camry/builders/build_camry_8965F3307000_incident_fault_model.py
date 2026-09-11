#!/usr/bin/env python3
"""Build the exact-F33 post-incident fault/vector model.

The incident instruction is reconstructed from the retained four-byte write plus
its untouched stock successor halfword.  CodeFlash.bin itself is the stock image;
this builder never substitutes stock bytes for the incident write.

Architecture-derived exception semantics are deliberately labeled as predicted,
not dynamically observed: no live FEPC/FEPSW/FEIC capture exists for the incident.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import struct
from pathlib import Path

from tools.targets.camry.support.camry_f33_corpus import IMAGE, IMAGE_SHA256

ROOT = Path(__file__).resolve().parents[4]
OUT = ROOT / "data/generated/camry_8965F3307000_incident_fault_model.json"
RECOVERY = ROOT / "data/generated/camry_f33_recovery_structure.json"


def need(ok: bool, msg: str) -> None:
    if not ok:
        raise ValueError(msg)


def u16(b: bytes, off: int) -> int:
    return struct.unpack_from("<H", b, off)[0]


def u32(b: bytes, off: int) -> int:
    return struct.unpack_from("<I", b, off)[0]


def signed(v: int, bits: int) -> int:
    return v - (1 << bits) if v & (1 << (bits - 1)) else v


def scan_ldsr(image: bytes, kind: str) -> list[dict[str, int | str]]:
    # Encodings are exact RH850G3M LDSR forms used in this image.
    if kind == "PSW":
        maskval, second = 0x2FE0, 0x0020
    elif kind == "RBASE":
        maskval, second = 0x17E0, 0x0820
    elif kind == "EBASE":
        maskval, second = 0x1FE0, 0x0820
    else:
        raise ValueError(kind)
    out = []
    for off in range(0, len(image) - 3, 2):
        h0, h1 = struct.unpack_from("<HH", image, off)
        if (h0 & 0xFFE0) == maskval and h1 == second:
            out.append({"address": off, "source_register": h0 & 0x1F, "bytes": image[off:off+4].hex()})
    return out


def direct_jarl_targets(image: bytes) -> list[tuple[int, int, int, str]]:
    """Decode direct JARL disp22/disp32 targets sufficiently for call provenance."""
    out: list[tuple[int, int, int, str]] = []
    # JARL disp22, reg2: op0610=0x1E, link register in bits 11..15.
    for off in range(0, len(image) - 3, 2):
        h0, h1 = struct.unpack_from("<HH", image, off)
        reg = (h0 >> 11) & 0x1F
        if ((h0 >> 6) & 0x1F) == 0x1E and reg != 0:
            disp = signed(((h0 & 0x3F) << 16) | h1, 22)
            out.append((off, (off + disp) & 0xFFFFFFFF, reg, image[off:off+4].hex()))
    # JARL disp32, reg1: op0515=0x017 and op1616=0.  The displacement is
    # represented modulo 2^32, so ordinary unsigned wrap gives the target.
    for off in range(0, len(image) - 5, 2):
        h0, h1, h2 = struct.unpack_from("<HHH", image, off)
        reg = h0 & 0x1F
        if ((h0 >> 5) & 0x7FF) == 0x017 and reg != 0 and (h1 & 1) == 0:
            disp = ((h2 << 16) | (h1 & 0xFFFE)) & 0xFFFFFFFF
            out.append((off, (off + disp) & 0xFFFFFFFF, reg, image[off:off+6].hex()))
    return out


def literal_occurrences(image: bytes, value: int) -> list[int]:
    needle = struct.pack("<I", value)
    out = []
    pos = 0
    while True:
        pos = image.find(needle, pos)
        if pos < 0:
            return out
        out.append(pos)
        pos += 1


def build() -> dict:
    image = IMAGE.read_bytes()
    need(len(image) == 0x100000, "exact F33 CodeFlash size drift")
    need(hashlib.sha256(image).hexdigest() == IMAGE_SHA256, "exact F33 CodeFlash hash drift")
    recovery = json.loads(RECOVERY.read_text())
    incident = recovery["incident"]

    need(incident["hook_address"] == "0x0007A272", "incident hook address drift")
    need(incident["recorded_bad_four_bytes"] == "ff02925b", "incident write drift")
    need(incident["instruction_with_stock_successor"] == "ff02925b2436", "incident six-byte instruction drift")
    need(incident["decoded_bad_target"] == "0x362BFE04", "incident decoded target drift")
    need(incident["live_exception_registers_observed"] is False, "incident exception-register evidence unexpectedly changed")
    need(incident["stock_instruction"] == {
        "address": "0x0007A272", "bytes": "80ffee1c", "size": 4, "target": "0x0007BF60"
    }, "stock replaced instruction drift")
    need(image[0x7A272:0x7A278].hex() == "80ffee1c2436", "stock hook-neighborhood bytes drift")

    bad_target = int(incident["decoded_bad_target"], 16)
    need(0x20000000 <= bad_target <= 0xFEBDFFFF, "incident target left P1M-E PE1 access-prohibited range")
    # P1M-E implements PC31..1, PC0=0; there is no 512-MB PC sign-extension here.
    need((bad_target & 1) == 0, "incident target unexpectedly odd")

    # Whole-image raw system-register census, not a Ghidra-function census.
    psw_writes = scan_ldsr(image, "PSW")
    rbase_writes = scan_ldsr(image, "RBASE")
    ebase_writes = scan_ldsr(image, "EBASE")
    need([x["address"] for x in psw_writes] == [0x204, 0x9F28], f"PSW LDSR set drift: {psw_writes}")
    need(rbase_writes == [], f"RBASE unexpectedly written: {rbase_writes}")
    need([x["address"] for x in ebase_writes] == [0x26E, 0x8508, 0x8514, 0x9F38, 0x715C8], f"EBASE LDSR set drift: {ebase_writes}")

    # Hidden reset/core-init stub.  It is outside the canonical function graph but
    # raw bytes set PSW=0x18020, whose bit15 (EBV) is 1.
    need(image[0x1FE:0x204].hex() == "2a0620800100", "reset PSW-value load drift")
    need(image[0x204:0x208].hex() == "ea2f2000", "reset PSW LDSR drift")
    reset_psw = 0x00018020
    need((reset_psw >> 15) & 1 == 1, "reset-core-init PSW no longer selects EBASE")

    # Application context installs EBASE=0x20000 before application initialization.
    need(image[0x715C0:0x715C6].hex() == "2b0600000200", "application EBASE value load drift")
    need(image[0x715C8:0x715CC].hex() == "eb1f2008", "application EBASE LDSR drift")
    application_ebase = 0x00020000
    syserr_vector = application_ebase + 0x10

    # The two other low-region EBASE setters have no fixed application caller.
    low_setters = {0x84F8}
    calls = direct_jarl_targets(image)
    low_setter_calls = sorted((off, target, reg, enc) for off, target, reg, enc in calls if target in low_setters)
    need(low_setter_calls == [
        (0x8578,0x84F8,31,"bfff80ff"),
        (0x8618,0x84F8,31,"bfffe0fe"),
        (0x863C,0x84F8,31,"bfffbcfe"),
        (0x868E,0x84F8,31,"bfff6afe"),
    ], f"low EBASE setter callers drift: {low_setter_calls}")
    need(all(off < 0x10000 for off, *_ in low_setter_calls), "application gained direct call to low EBASE setter")
    need(all(literal_occurrences(image, x) == [] for x in low_setters), "low EBASE setter gained fixed pointer literal")

    # The only later PSW writer is the explicit application -> boot handoff path;
    # retain its exact PSW value/load but do not treat it as cold-start execution.
    need(image[0x9F22:0x9F28].hex() == "2a0620800100" and image[0x9F28:0x9F2C].hex() == "ea2f2000", "handoff PSW writer drift")

    # EBASE+0x10 direct vector: SYNCP; JMP 0x62E1E,r0.
    vector_bytes = image[syserr_vector:syserr_vector+16]
    need(vector_bytes[:8].hex() == "1f00e0061e2e0600", f"application SYSERR vector drift: {vector_bytes.hex()}")
    handler = 0x62E1E

    # Exact terminal handler.  It saves an EI-context-shaped frame, executes EI,
    # calls the common register saver, then self-branches forever.  It contains no
    # FERET/EIRET and does not copy FEPC/FEPSW/FEIC into this RAM frame.
    handler_bytes = image[handler:0x62E44]
    need(handler_bytes.hex() == "031e94ff63f71d0003f035fde1ff40000dfde0ff40000bfde0876001630f210080ff90e48505", "terminal handler bytes drift")
    need(image[0x62E42:0x62E44].hex() == "8505", "terminal handler self-loop drift")
    handler_sha = hashlib.sha256(handler_bytes).hexdigest()

    # Stack frame geometry under the application context SP=FEBE2000.
    app_sp = 0xFEBE2000
    frame_lo = app_sp - 0x6C
    frame_hi = app_sp - 1
    saved_lp = frame_lo + 0x68
    need((frame_lo, frame_hi, saved_lp) == (0xFEBE1F94,0xFEBE1FFF,0xFEBE1FFC), "fault-frame geometry drift")

    return {
        "schema": "camry-8965f3307000-incident-fault-model-v1",
        "target": {"software_id": "8965F3307000", "codeflash_sha256": IMAGE_SHA256},
        "incident_instruction": {
            "address": "0x0007A272",
            "recorded_write_bytes": incident["recorded_bad_four_bytes"],
            "reconstructed_bytes": incident["instruction_with_stock_successor"],
            "decoded": "JARL 0x362BFE04,LP",
            "target": "0x362BFE04",
            "link_register_after_jarl": "0x0007A278",
            "target_address_space": "P1M-E PE1 access-prohibited range 0x20000000..0xFEBDFFFF",
            "target_observed_live": False,
            "exception_registers_observed_live": False,
            "stock_replaced_instruction": incident["stock_instruction"],
        },
        "vector_selection": {
            "raw_psw_ldsr_writers": [{**x, "address": f"0x{x['address']:08X}"} for x in psw_writes],
            "raw_rbase_ldsr_writers": rbase_writes,
            "raw_ebase_ldsr_writers": [{**x, "address": f"0x{x['address']:08X}"} for x in ebase_writes],
            "reset_core_init_psw": f"0x{reset_psw:08X}",
            "reset_core_init_ebv": 1,
            "application_ebase": f"0x{application_ebase:08X}",
            "syserr_vector_offset": "0x10",
            "predicted_vector": f"0x{syserr_vector:08X}",
            "vector_bytes": vector_bytes.hex(),
            "vector_target": f"0x{handler:08X}",
            "low_ebase_setter_direct_calls": [
                {"callsite":f"0x{o:08X}","target":f"0x{t:08X}","link_register":r,"bytes":enc}
                for o,t,r,enc in low_setter_calls
            ],
            "low_ebase_setter_fixed_pointer_literals": 0,
            "classification": "raw-image proof: EBV is set before the valid application and no recovered application path reselects another EBASE before the incident",
        },
        "architecture_prediction": {
            "grade": "architecture-predicted; not dynamically observed in this incident",
            "p1m_e_fetch_space": "PE1 instruction fetch is supported from CodeFlash, local RAM self, and global RAM; 0x362BFE04 is access-prohibited",
            "p1m_e_feic": "0x13 = instruction fetch from other than Code Flash",
            "g3m_exception_class": "resumable FE-level SYSERR due error input during instruction fetch",
            "g3m_acknowledgement_effects": {"PSW.ID":1,"PSW.NP":1,"PSW.EP":1,"PSW.EBV":"retained"},
            "g3m_vector_rule": "PSW.EBV=1 selects EBASE; SYSERR offset is +0x10",
            "boundary": "FEIC/FEPC/FEPSW were never captured after the live incident; exact silicon response is therefore predicted from the matching Renesas architecture, not observed",
        },
        "terminal_handler": {
            "entry": f"0x{handler:08X}",
            "bytes_sha256": handler_sha,
            "stack_frame": {"start":f"0x{frame_lo:08X}","end_inclusive":f"0x{frame_hi:08X}","saved_lp":f"0x{saved_lp:08X}"},
            "saved_lp_predicted_value": "0x0007A278",
            "saves": ["ordinary register frame", "EIPC", "EIPSW", "CTPC/CTPSW via 0x712CE"],
            "does_not_copy_to_ram": ["FEPC", "FEPSW", "FEIC"],
            "executes_ei": True,
            "terminal": "self-loop at 0x62E42; no FERET/EIRET",
            "important_np_effect": "EI clears ID but does not clear NP; SYSERR leaves NP=1, so maskable EIINTs remain unacknowledgeable",
        },
        "post_fault_network_surface": {
            "can_eiint_after_predicted_syserr": False,
            "timer_eiint_after_predicted_syserr": False,
            "reason": "G3M EIINT acknowledgement requires ID=0 and NP=0; handler EI only clears ID while FE-level SYSERR has NP=1",
            "network_fenmi_route_recovered": False,
            "network_internal_reset_route_recovered": False,
            "implication": "ordinary CAN RX/TX and periodic maskable service cannot run after the predicted SYSERR fault; any network-only recovery must act before 0x7A272 or use an unrecovered non-EIINT hardware/reset path",
        },
        "manual_evidence": {
            "p1m_e": "RH850/P1M-E Hardware User's Manual R01UH0585EJ0120 Rev.1.20: CPU/PSW, SEG Table 3.80, address space Figure 4.1",
            "g3m": "RH850G3M User's Manual: Software R01US0123EJ0140 Rev.1.40: Table 4-1 exception class/ack conditions and Table 4-4 SYSERR +0x10 vector",
        },
        "verdict": {
            "exact_live_fault_registers_known": False,
            "architecture_predicted_fault": "instruction-fetch SYSERR, FEIC 0x13",
            "architecture_predicted_terminal_handler": "0x00062E1E -> 0x00062E42 self-loop",
            "maskable_can_service_survives_predicted_fault": False,
            "post_fault_can_recovery_primitive_recovered": False,
            "combined_with_prefault_audit": "no recovered CAN-only software recovery route remains: pre-fault synchronous ingress cannot alter the guard/reset/control flow, and the predicted post-fault SYSERR blocks maskable CAN service",
            "remaining_boundary": "a live FEIC/FEPC/FEPSW capture or board-level/non-maskable reset/debug mechanism could refine or change the predicted post-fault model",
        },
        "evidence": {
            "incident_reconstruction": "data/generated/camry_f33_recovery_structure.json",
            "prefault_control_flow": "data/generated/camry_8965F3307000_prefault_control_flow.json",
            "codeflash": "firmware/camry-8965F3307000/CodeFlash.bin",
        },
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=OUT)
    args = ap.parse_args()
    obj = build()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n")
    print(args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
