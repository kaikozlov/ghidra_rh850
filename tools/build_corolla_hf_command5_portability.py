#!/usr/bin/env python3
"""Build the exact-H/F ICU-S command-5 portability and resident-carrier boundary."""
from __future__ import annotations

import argparse
import hashlib
import json
import struct
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
H = REPO / "community/albinoelephant/normalized/8965H1202000_CodeFlash.bin"
F = REPO / "community/spanconstant/raw-20260821/span-corolla-2025.20260821-1511/dump_codeflash_00000000_00200000_20260821-152033.bin"
FOLLOWUP = REPO / "data/generated/corolla_8965H1202000_tms053_followup_decompiler_evidence.json"
EQUIV = REPO / "data/generated/corolla_8965F1208000_vs_8965H1202000_codeflash_equivalence.json"
RAMREQ = REPO / "data/variant_ram_exec_requirements.json"
XCP = REPO / "data/generated/corolla_8965H1202000_xcp.json"
OUT = REPO / "data/generated/corolla_hf_command5_portability.json"


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def u32(b: bytes, a: int) -> int:
    return struct.unpack_from("<I", b, a)[0]


def need(cond: bool, msg: str) -> None:
    if not cond:
        raise SystemExit(msg)


def token(text: str, *parts: str) -> None:
    miss = [x for x in parts if x not in text]
    need(not miss, f"missing command5 evidence token(s): {miss}")


def build() -> dict:
    h = H.read_bytes(); f = F.read_bytes()[:0x100000]
    ev = json.loads(FOLLOWUP.read_text())
    equiv = json.loads(EQUIV.read_text())
    req = json.loads(RAMREQ.read_text())
    xcp = json.loads(XCP.read_text())
    need(len(h) == len(f) == 0x100000, "H/F image size drift")
    need(h[0x20000:] == f[0x20000:], "H/F application region no longer identical")
    funcs = {int(x["entry"], 16): x["decompiled_c"] for x in ev["functions"]}
    for row in ev["functions"]:
        a = int(row["entry"], 16); n = row["body_size"]
        need(sha(h[a:a+n]) == row["body_sha256"], f"raw body drift {a:#x}")

    # The exact H command-5 driver table has two 32-byte records. Record 0 is
    # enough for the RAM proxy: its completion, adapter, worker and config
    # pointer are explicit raw words, independent of Ghidra's function-boundary
    # decisions around the callbacks.
    rec = 0x27C88
    raw = h[rec:rec + 0x20]
    fields = {
        "header": u32(h, rec + 0x00),
        "completion_callback": u32(h, rec + 0x04),
        "adapter_callback": u32(h, rec + 0x14),
        "worker_callback": u32(h, rec + 0x18),
        "config_pointer": u32(h, rec + 0x1C),
    }
    need(fields == {
        "header": 0xFFFF0000,
        "completion_callback": 0x82F5C,
        "adapter_callback": 0x820CC,
        "worker_callback": 0x821D0,
        "config_pointer": 0x27C84,
    }, f"H command5 record0 drift: {fields}")
    need(u32(h, 0x27C84) == 1, "command5 config type drift")
    need(raw == f[rec:rec+0x20], "H/F command5 record0 differs")

    token(funcs[0x82750], "FUN_00082702(param_1)", "+ 0x14", "+ 0x1c", "(*pcVar6)(uVar3")
    token(funcs[0x81E94], "*param_1 == 1", "param_3 < 0x51", "bVar1 = *(byte *)(param_1 + 1)")
    token(funcs[0x82070], "FUN_00083a30(0xfebf10cc)")
    token(funcs[0x83A30], "Ramffc5d000 = puVar6[2] << 0x10 | 5")
    token(funcs[0x82ED2], "uRamfebf1280 = 0;", "uRamfebf1281 = 1;", "FUN_00082750", "uVar2 < 0xe07")

    # This is the load-bearing negative for carrying the Sienna single-stage
    # resident proxy across variants. H application initialization owns/clears
    # substantial pieces of the authenticated FEBF0xxx page.
    clear = funcs[0x6149A]
    token(clear, "uVar1 + 0xfebf05cc", "uVar1 + 0xfebf0b4c", "uVar1 < 0x400")
    clear_ranges = [[0xFEBF05CC, 0xFEBF09CB], [0xFEBF0B4C, 0xFEBF0F4B]]

    variant_ids = {row["id"] for row in req["variants"]}
    need("sienna-8965b4512000" in variant_ids, "verified Sienna RAM geometry missing")
    need("corolla-8965h1202000" not in variant_ids and "corolla-8965f1208000" not in variant_ids,
         "H/F must not be promoted to verified Sienna-like RAM execution geometry")

    need(equiv["application_equivalence"]["identical"] is True, "tracked H/F app equivalence drift")
    need(xcp["static_conclusion"]["xcp_residue_closed"] is True, "H XCP surface drift")

    return {
        "schema": "corolla-hf-command5-portability-v1",
        "applies_to": ["8965H1202000", "8965F1208000"],
        "sources": {
            "h_codeflash": {"path": str(H.relative_to(REPO)), "sha256": sha(h)},
            "f_codeflash": {"path": str(F.relative_to(REPO)), "sha256": sha(F.read_bytes())},
            "followup_decompiler_evidence": {"path": str(FOLLOWUP.relative_to(REPO)), "sha256": sha(FOLLOWUP.read_bytes())},
            "hf_equivalence": {"path": str(EQUIV.relative_to(REPO)), "sha256": sha(EQUIV.read_bytes())},
            "ram_exec_requirements": {"path": str(RAMREQ.relative_to(REPO)), "sha256": sha(RAMREQ.read_bytes())},
            "xcp": {"path": str(XCP.relative_to(REPO)), "sha256": sha(XCP.read_bytes())},
        },
        "command5_core": {
            "driver_record_index": 0,
            "driver_record_address": f"0x{rec:08X}",
            "driver_record_raw_hex": raw.hex(),
            "record_fields": {k: f"0x{v:08X}" for k, v in fields.items()},
            "config_type_word_address": "0x00027C84",
            "config_type_word": 1,
            "serialized_dispatcher": "0x00082750",
            "record_lookup": "0x00082702",
            "variable_length_prepare": "0x00081E94",
            "maximum_input_bytes": 80,
            "adapter_callback": "0x000820CC",
            "worker_callback": "0x000821D0",
            "lower_icus_engine": "0x00083A30",
            "completion_callback": "0x00082F5C",
            "synchronous_wrapper": "0x00082ED2",
            "done_flag": "0xFEBF1280",
            "status_flag": "0xFEBF1281",
            "key_selector_argument": "low byte of config[1]; a caller may request selector 4 exactly as the proven Sienna proxy does",
            "command_word_formula": "(key_selector << 16) | 5",
            "b6_authenticated_input_fits": True,
            "b6_authenticated_input_bytes": 36,
            "h_f_application_byte_identical": True,
        },
        "resident_runtime_boundary": {
            "sienna_single_stage_geometry_transfers": False,
            "h_startup_clear_entry": "0x0006149A",
            "h_startup_clear_ranges_inclusive": [[f"0x{a:08X}", f"0x{b:08X}"] for a,b in clear_ranges],
            "lower_page_also_contains_live_h_application_structures": True,
            "h_f_verified_ram_exec_requirement_entry_present": False,
            "interpretation": "The ICU-S command-5 software machinery transfers, but the Sienna resident-code placement contract does not. H/F need a target-native application-context carrier; do not build or link the Sienna 546-byte proxy at FEBF0000 as if FEBF0000..0307 were retained free code space.",
        },
        "two_stage_candidate": {
            "status": "hypothesis-not-verified-carrier",
            "xcp_write_shadow_bounds": ["0xFEBF7C00", "0xFEBFFBFF"],
            "xcp_application_write_architecture_recovered": True,
            "interpretation": "The existing no-XCP-SA H shadow-write architecture is a plausible staging component for a future target-native two-stage signer, but this artifact does not prove a post-start control transfer into it, lifetime safety, or live selector-4 permission/latency.",
        },
        "remaining_dynamic_or_runtime_work": [
            "recover/validate a target-native H/F resident or re-enterable application-context carrier",
            "exercise live ICU-S command5 selector4 permission on H/F",
            "measure command5 signing latency/jitter against the B6 transmit deadline",
            "validate mailbox/control-flow lifetime under normal steering application execution",
        ],
        "static_conclusion": {
            "h_f_command5_software_machinery_transfers": True,
            "b6_36_byte_input_supported": True,
            "sienna_single_stage_resident_geometry_transfers": False,
            "h_f_resident_signer_runtime_closed": False,
            "slot4_live_permission_closed": False,
            "signing_latency_closed": False,
        },
        "evidence_boundary": "This closes exact-H/F command-5 software portability and disproves the naive Sienna resident-page port. It does not claim a working H/F in-application signing oracle until target-native carrier placement/control-flow plus live slot-4 permission and latency are validated.",
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", type=Path, default=OUT)
    args = ap.parse_args()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(build(), indent=2, sort_keys=True) + "\n")
    print(f"wrote {args.out}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
