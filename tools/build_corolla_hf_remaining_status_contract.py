#!/usr/bin/env python3
"""Build exact H/F contracts for remaining 0x030 B6[1] and 0x351 force-7 status paths."""
from __future__ import annotations

import argparse
import hashlib
import json
import struct
from pathlib import Path
from corolla_h_constants import CODEFLASH as H_CODEFLASH

REPO = Path(__file__).resolve().parents[1]
IMAGE = H_CODEFLASH
EVID = REPO / "data/generated/corolla_8965H1202000_remaining_status_decompiler_evidence.json"
FD = REPO / "data/generated/corolla_8965H1202000_fd_control_interface.json"
SPAN = REPO / "data/generated/corolla_2025_span_discord_rlog_opendbc_evidence.json"
TECH = REPO / "data/generated/corolla_8965H1202000_techstream_correlations.json"
EQUIV = REPO / "data/generated/corolla_8965F1208000_vs_8965H1202000_codeflash_equivalence.json"
OUT = REPO / "data/generated/corolla_hf_remaining_status_contract.json"


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def need(text: str, *tokens: str) -> None:
    missing = [t for t in tokens if t not in text]
    if missing:
        raise ValueError("missing decompiler token(s): " + ", ".join(missing))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", type=Path, default=OUT)
    args = ap.parse_args()
    image = IMAGE.read_bytes()
    evid_b = EVID.read_bytes(); evid = json.loads(evid_b)
    fd_b = FD.read_bytes(); fd = json.loads(fd_b)
    span_b = SPAN.read_bytes(); span = json.loads(span_b)
    tech_b = TECH.read_bytes(); tech = json.loads(tech_b)
    equiv_b = EQUIV.read_bytes(); equiv = json.loads(equiv_b)
    if len(image) != 0x100000 or sha(image) != evid["image"]["sha256"]:
        raise ValueError("H image/evidence drift")
    app = equiv["application_equivalence"]
    if not (app["identical"] and app["different_bytes"] == 0 and app["start"] == "0x20000" and app["end_exclusive"] == "0x100000"):
        raise ValueError("H/F application equivalence drift")
    funcs = {int(x["entry"], 16): x["decompiled_c"] for x in evid["functions"]}

    # 0x030 B6[1]: Q-current actual -> snapshot -> absolute-threshold detector -> debounce -> wire.
    need(funcs[0x5258A], "uRamfebeec0c = uRamfebe6bae;")
    need(funcs[0xBBFE6], "uRamfebeafc4 = uRamfebeec0c;")
    need(funcs[0xBD50C], "uRamfebeafc4 = uRamfebeec0c;")
    need(funcs[0xCF070], "if (iVar1 < 0)", "param_1 = -param_1", "param_1 = 0x7fff")
    need(funcs[0xBB8F6], "FUN_000cf070((int)sRamfebeafc4", "DAT_000aeed8", "DAT_000aeeda", "DAT_000aeedc", "iVar3 + -0x1b3")
    need(funcs[0xBB942], "cRamfebeb64d == 'Z'", "DAT_000aeede", "cRamfebeb64c")
    need(funcs[0xBB98E], "FUN_000bb8f6();", "FUN_000bb942();")
    need(funcs[0xBBF8A], "uRamfebeb64c = 0;")
    need(funcs[0xBBA48], "uRamfebee848 = uRamfebeb64c;")
    need(funcs[0x46EE0], "uRamfebe7db3 = uRamfebee848;")
    qactual = tech["motor_current_bridge"]["q_axis_actual_chain"]
    if not any(x["entry"] == "0x00033160" and "FEBE6BAE" in x["relation"] for x in qactual):
        raise ValueError("Q-axis actual-current semantic join drift")
    fd7 = next(x for x in fd["fd_0x030_transmit"]["fields"] if x["signal_id"] == 7)
    if (fd7["wire_byte"], fd7["bit_offset"], fd7["bit_length"], fd7["source"], fd7["nondefault_writer_functions"]) != (6, 1, 1, "0xFEBE7DB3", ["0x00046EE0"]):
        raise ValueError("0x030 B6[1] FD geometry drift")
    span_bit1 = span["direct_reuse_evidence"]["0x030"]["steering_state_bridge"]["b6_bit1"]
    qcal = {
        "feature_flag": image[0xAEED8],
        "threshold_a": struct.unpack_from("<h", image, 0xAEEDA)[0],
        "threshold_b": struct.unpack_from("<h", image, 0xAEEDC)[0],
        "debounce_count": struct.unpack_from("<H", image, 0xAEEDE)[0],
    }
    if qcal != {"feature_flag": 0x5A, "threshold_a": 5120, "threshold_b": 2560, "debounce_count": 0}:
        raise ValueError(f"B6[1] calibration drift: {qcal!r}")

    # 0x351 force-7: status bitmap bits0/1 AND bit15 of a 24-record aggregate.
    need(funcs[0x36AAA], "FUN_00069d5e(param_1,iVar2 + -0x484c", "param_1 = param_1 & 0xffff")
    need(funcs[0x36B9E], "FUN_00069abc(0xfebe6fb4,0xfebe6ed0,0xfebe6ed2")
    need(funcs[0x36BBE], "uVar5 = (uint)uRamfebe6fb6", "uVar4 = FUN_00036b9e();", "FUN_00036aaa(uVar5);")
    need(funcs[0x36CEC], "iVar2 + -0x17", "uVar5 = uVar5 | *(ushort *)(iVar9 + 6);", "uVar5 = uVar5 | uRamfebe720e;", "FUN_0003738c(uVar5);")
    need(funcs[0x3738C], "uVar7 = uRamfebe6fb4 & 0x8000;", "param_1 & 0x8000", "FUN_000472e0(uVar6);")
    need(funcs[0x472E0], "uRamfebe7e13 = param_1;")
    need(funcs[0x5778E], "uRamfebe65e4 = uRamfebe6fb4;")
    need(funcs[0x46E62], "(uRamfebe65e4 & 3) == 0", "cRamfebe7e13 == '\\0'", "param_1 = 7;", "uRamfebe7dd1 = 1;")

    out = {
        "schema": "corolla-hf-remaining-status-contract-v1",
        "software_ids": ["8965H1202000", "8965F1208000"],
        "sources": {
            "h_codeflash": {"path": str(IMAGE.relative_to(REPO)), "sha256": sha(image)},
            "decompiler_evidence": {"path": str(EVID.relative_to(REPO)), "sha256": sha(evid_b), "function_count": evid["function_count"]},
            "fd_control_interface": {"path": str(FD.relative_to(REPO)), "sha256": sha(fd_b)},
            "span_moving_rlog_evidence": {"path": str(SPAN.relative_to(REPO)), "sha256": sha(span_b)},
            "techstream_correlations": {"path": str(TECH.relative_to(REPO)), "sha256": sha(tech_b)},
            "hf_application_equivalence": {"path": str(EQUIV.relative_to(REPO)), "sha256": sha(equiv_b), "application": app},
        },
        "can_0x030_b6_bit1": {
            "wire": "0x030 B6[1]",
            "signal_id": 7,
            "chain": [
                "FEBE6BAE Motor Actual Current (Q Axis)",
                "0x5258A -> FEBEEC0C",
                "0xBBFE6/0xBD50C -> FEBEAFC4",
                "0xBB8F6 + 0xCF070 -> FEBEB64D absolute-current threshold detector",
                "0xBB942 -> FEBEB64C debounced status",
                "0xBBA48 -> FEBEE848",
                "0x46EE0 -> FEBE7DB3",
                "0x030 B6[1]",
            ],
            "calibration": {"address": "0x000AEED8", **qcal},
            "exact_h_calibration_effect": (
                "feature flag 0x5A makes the BB8F6 detector's enabled-only set branch unreachable and forces its raw detector output FEBEB64D to zero on each execution; debounce calibration is zero. "
                "This closes the physical source family and detector-disable state, not an OEM display name for the final debounced bit."
            ),
            "span_observation": {"values": span_bit1["values"], "boundary": "Span's moving rlog is not exact-F181-joined and therefore cannot override exact-H calibration identity; its 0/1 variation is useful cross-specimen evidence only."},
            "classification": "Q-axis actual-current-derived debounced status; exact H's threshold detector is calibration-disabled",
            "openpilot_consequence": "Do not treat B6[1] as a generic steering-ready/authority bit. Its source is motor Q-current monitoring and its exact-H detector is disabled by calibration.",
        },
        "can_0x351_force7": {
            "wire_effect": "0x46E62 forces the 0x351 status code to 7 and sets FEBE7DD1=1",
            "condition": "(FEBE65E4 & 0x0003) != 0 AND FEBE7E13 != 0",
            "status_bitmap_side": {
                "chain": ["0x36BBE resolves/merges the current 16-bit status value", "0x36AAA stores it at FEBE6FB4 with XOR-redundant mirrors FEBE6ED0/FEBE6ED2", "0x5778E copies FEBE6FB4 -> FEBE65E4"],
                "bits_used": [0, 1],
                "boundary": "FEBE6FB4 is a broad internally consumed 16-bit status bitmap; current static evidence does not assign Toyota names to bits0/1.",
            },
            "record_aggregate_side": {
                "record_count": 24,
                "mode_table": "FEBE6F94[24] selects one of two 12-byte record banks rooted at FEBE6FC8 or FEBE70E8",
                "aggregate": "0x36CEC ORs each valid record's +6 ushort into one aggregate (plus FEBE720E under its recovered gate)",
                "bit_used": 15,
                "chain": ["0x36CEC aggregate bit15", "0x3738C -> 0x472E0(0x5A/0)", "FEBE7E13", "0x46E62 force-7"],
                "boundary": "The exact source geometry and bit are closed; an OEM/DTC name for record +6 bit15 is not recovered from the current corpus.",
            },
            "classification": "independent severe/special status override, distinct from the C159B49-linked 0x351 base electrical-monitor code path",
            "openpilot_consequence": "Treat the force-7 indication as a distinct conservative fault/status input if 0x351 becomes available, but do not rename it C159B49 or map it to temporary/permanent without dynamic policy evidence.",
        },
        "static_exhaustion": {
            "0x030_b6_bit1": "physical source and exact-H calibration behavior closed; only Toyota display/policy naming remains unavailable",
            "0x351_force7": "source topology and exact gating bits closed; current corpus has no unique Toyota/DTC semantic label for the two internal status inputs",
            "boundary": "These are semantic-name boundaries, not invitations to infer names from packet position or neighboring DTCs.",
        },
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
