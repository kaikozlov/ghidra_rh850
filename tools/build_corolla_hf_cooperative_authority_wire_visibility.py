#!/usr/bin/env python3
"""Build the exact H/F cooperative-authority wire-visibility boundary."""
from __future__ import annotations

import argparse
import hashlib
import json
import struct
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]
IMAGE = REPO / "community/albinoelephant/normalized/8965H1202000_CodeFlash.bin"
EVIDENCE = REPO / "data/generated/corolla_8965H1202000_cooperative_authority_wire_decompiler_evidence.json"
FD = REPO / "data/generated/corolla_8965H1202000_fd_control_interface.json"
STATE = REPO / "data/generated/corolla_8965H1202000_openpilot_state_bridge.json"
EQUIV = REPO / "data/generated/corolla_8965F1208000_vs_8965H1202000_codeflash_equivalence.json"
OUT = REPO / "data/generated/corolla_hf_cooperative_authority_wire_visibility.json"

GP = 0xFEBEB800
ROOTS = {
    "raw_mode": 0xFEBEF000,
    "normalized_mode": 0xFEBEACBD,
    "health_gate": 0xFEBEC26D,
    "profile_1": 0xFEBEC26E,
    "profile_4": 0xFEBEC26F,
    "profile_10": 0xFEBEC270,
    "profile_11_or_19": 0xFEBEC271,
    "common_active": 0xFEBEC272,
    "profile_1_mirror": 0xFEBEC273,
    "aggregate_stage": 0xFEBEB118,
    "aggregate_snapshot": 0xFEBEE887,
    "wire_source_signal_5": 0xFEBE7E09,
    "wire_source_signal_12": 0xFEBE7E0B,
    "wire_source_signal_15": 0xFEBE7E0D,
}
PACKERS = {
    "0x030": 0x4766A,
    "0x351": 0x47BA2,
    "0x394": 0x47ADA,
    "0x4A3": 0x4749A,
    "0x4C8": 0x475D0,
}
PROFILE_TABLES = (0xD0E18, 0xD1118)


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def need(text: str, *tokens: str) -> None:
    missing = [token for token in tokens if token not in text]
    if missing:
        raise ValueError("missing decompiler token(s): " + ", ".join(missing))


def rel(path: Path) -> str:
    return str(path.resolve().relative_to(REPO.resolve()))


def pointer_occurrences(image: bytes, address: int) -> list[str]:
    needle = struct.pack("<I", address)
    return [f"0x{offset:08X}" for offset in range(len(image)) if image.startswith(needle, offset)]


def decode_profile_tables(image: bytes) -> list[dict]:
    families = []
    for base in PROFILE_TABLES:
        banks = []
        for bank in range(2):
            rows = []
            bank_base = base + bank * 0x3C
            for index in range(5):
                address = bank_base + index * 0x0C
                flag, lower, upper = struct.unpack_from("<III", image, address)
                rows.append({
                    "index": index,
                    "address": f"0x{address:08X}",
                    "flag_pointer": f"0x{flag:08X}" if flag else None,
                    "lower_calibration_pointer": f"0x{lower:08X}" if lower else None,
                    "upper_calibration_pointer": f"0x{upper:08X}" if upper else None,
                })
            banks.append({"bank": bank, "base": f"0x{bank_base:08X}", "rows": rows})
        families.append({"base": f"0x{base:08X}", "banks": banks})
    return families


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--image", type=Path, default=IMAGE)
    ap.add_argument("--evidence", type=Path, default=EVIDENCE)
    ap.add_argument("--out", type=Path, default=OUT)
    args = ap.parse_args()

    image = args.image.read_bytes()
    evidence_bytes = args.evidence.read_bytes()
    evidence = json.loads(evidence_bytes)
    fd = json.loads(FD.read_text())
    state = json.loads(STATE.read_text())
    equiv = json.loads(EQUIV.read_text())
    if len(image) != 0x100000 or sha(image) != "0b47bdc1217835c839e3543e52eab40eb793650a9c159e46f6a9b365ea41a67f":
        raise ValueError("exact H image identity drift")
    if evidence["schema"] != "corolla-h-cooperative-authority-wire-decompiler-evidence-v1" or evidence["function_count"] != 16:
        raise ValueError("cooperative-authority evidence identity drift")

    funcs: dict[int, str] = {}
    for row in evidence["functions"]:
        entry = int(row["entry"], 16)
        body = image[entry:entry + row["body_size"]]
        text = row["decompiled_c"]
        if sha(body) != row["body_sha256"] or sha(text.encode()) != row["decompiled_c_sha256"]:
            raise ValueError(f"raw/decompiler evidence drift at 0x{entry:08X}")
        funcs[entry] = text
    if set(funcs) != {
        0x470C6, 0x4749A, 0x475D0, 0x4766A, 0x47ADA, 0x47BA2,
        0x5262C, 0xB23A2, 0xB8EEC, 0xBBA48, 0xC5156, 0xC51EA,
        0xC6D16, 0xC6DAA, 0xCAF84, 0xCBE6E,
    }:
        raise ValueError("promoted function set drift")

    # Raw mode staging, normalized gate, and exact cooperative selection.
    need(funcs[0x5262C], "uRamfebef000 = uRamfebe7c58;")
    need(funcs[0xB8EEC],
         "cVar1 = *(char *)(iVar15 + 0x3800);",
         "if ((cVar1 != '\\0') && (cVar1 != '\\x02'))",
         "if (cVar1 == '\\x03')",
         "cVar21 = '\\x04';",
         "cVar21 = '\\x01';",
         "*(char *)(iVar15 + -0xb43) = cVar21;")
    need(funcs[0xCBE6E],
         "if ((cRamfebeacbd == '\\0') && (cRamfebec26d == '\\x01'))",
         "*(undefined1 *)(iVar2 + 0xa72) = uVar9;",
         "*(undefined1 *)(iVar2 + 0xa73) = uVar8;",
         "*(undefined1 *)(iVar2 + 0xa6e) = uVar7;",
         "*(undefined1 *)(iVar2 + 0xa71) = uVar4;")
    if not (GP + 0x3800 == ROOTS["raw_mode"] and GP - 0xB43 == ROOTS["normalized_mode"]):
        raise AssertionError("normalized-mode GP arithmetic")

    # The missed fixed-GP/computed-alias chain. The raw-mode comparison is one
    # conjunct of a larger predicate and deliberately groups values 0 and 1.
    need(funcs[0xB23A2],
         "bVar3 = bRamfebef000;", "bVar3 < 2", "cRamfebef146",
         "cRamfebef069", "cRamfebeb13e", "cRamfebeb054",
         "*(undefined1 *)(iVar6 + -0x6e8) = uVar7;", "uVar7 = 0x5a;")
    need(funcs[0xBBA48], "uRamfebee887 = uRamfebeb118;")
    need(funcs[0x470C6],
         "bRamfebe7e0d = cRamfebee887 == 'Z';",
         "bRamfebe7e09 = bRamfebe7e0d;",
         "bRamfebe7e0b = bRamfebe7e0d;")
    need(funcs[0x4766A],
         "uRamfebe88ef = uRamfebe7e09;",
         "uRamfebe88dd = uRamfebe7e0b;",
         "uRamfebe88df = uRamfebe7e0d;",
         "FUN_0007662e(5,6,1,3",
         "FUN_0007662e(0xc,10,1,3",
         "FUN_0007662e(0xf,0xd,1,4")
    if not (GP - 0x6E8 == ROOTS["aggregate_stage"]):
        raise AssertionError("aggregate-stage GP arithmetic")

    # The profile flags have no named/direct Tx-packer consumer. Their only raw
    # absolute pointer materializations are two fixed table families used by
    # CAF84 as flag predicates for internal gain products.
    need(funcs[0xC5156], "&DAT_000d0e18", "FUN_000caf84(&local_2c);", "+ 0x452) = (short)uVar6;")
    need(funcs[0xC51EA], "uRamfebebc52 * iRamfebebc40")
    need(funcs[0xC6D16], "&DAT_000d1118", "FUN_000caf84(&local_2c);", "+ 0x628) = (short)uVar6;")
    need(funcs[0xC6DAA], "uRamfebebe28 * (int)sRamfebebe26")
    need(funcs[0xCAF84], "*(char *)*param_1", "FUN_000ce650(param_1[2],iVar5)")
    tables = decode_profile_tables(image)
    expected_flags = [None, "0xFEBEC26E", "0xFEBEC26F", "0xFEBEC270", "0xFEBEC271"]
    for family in tables:
        for bank in family["banks"]:
            if [row["flag_pointer"] for row in bank["rows"]] != expected_flags:
                raise ValueError(f"profile pointer table drift at {bank['base']}")

    occurrences = {name: pointer_occurrences(image, address) for name, address in ROOTS.items()}
    expected_profile_occurrences = {
        "profile_1": ["0x000D0E24", "0x000D0E60", "0x000D1124", "0x000D1160"],
        "profile_4": ["0x000D0E30", "0x000D0E6C", "0x000D1130", "0x000D116C"],
        "profile_10": ["0x000D0E3C", "0x000D0E78", "0x000D113C", "0x000D1178"],
        "profile_11_or_19": ["0x000D0E48", "0x000D0E84", "0x000D1148", "0x000D1184"],
    }
    for name, expected in expected_profile_occurrences.items():
        if occurrences[name] != expected:
            raise ValueError(f"absolute pointer occurrence drift for {name}: {occurrences[name]!r}")
    for name in set(ROOTS) - set(expected_profile_occurrences):
        if occurrences[name]:
            raise ValueError(f"unexpected absolute pointer materialization for {name}: {occurrences[name]!r}")

    fd_fields = {row["signal_id"]: row for row in fd["fd_0x030_transmit"]["fields"]}
    expected_wire = {
        5: ("0xFEBE7E09", 6, 3, 1),
        12: ("0xFEBE7E0B", 10, 3, 1),
        15: ("0xFEBE7E0D", 13, 4, 1),
    }
    for signal, expected in expected_wire.items():
        row = fd_fields[signal]
        actual = (row["source"], row["wire_byte"], row["bit_offset"], row["bit_length"])
        if actual != expected:
            raise ValueError(f"0x030 signal {signal} geometry drift: {actual!r}")

    descriptors = {row["can_id"]: row for row in state["h_tx_pdu_descriptors"]}
    expected_descriptors = {
        "0x030": [2, 0, 0, 32, 0, 3],
        "0x351": [200, 0, 0, 4, 0, 3],
        "0x394": [60, 0, 0, 3, 0, 3],
        "0x4A3": [100, 0, 0, 8, 0, 3],
        "0x4C8": [196, 0, 0, 8, 0, 3],
    }
    if {key: value["descriptor"] for key, value in descriptors.items()} != expected_descriptors:
        raise ValueError("five-PDU descriptor set drift")
    if {key: int(value["packer"], 16) if "packer" in value else PACKERS[key] for key, value in descriptors.items()} != PACKERS:
        raise ValueError("five-PDU packer map drift")
    need(funcs[0x475D0], "uRamfebe8900 = 9;", "uRamfebe8901 = 0;", "uRamfebe88d4 = 0;")

    authority_root_names = (
        "raw_mode", "normalized_mode", "health_gate", "profile_1", "profile_4",
        "profile_10", "profile_11_or_19", "common_active", "profile_1_mirror",
    )
    authority_root_addresses = tuple(ROOTS[name] for name in authority_root_names)
    root_spellings = tuple(f"{address:08x}" for address in authority_root_addresses)
    direct_root_hits = {}
    for can_id, entry in PACKERS.items():
        direct_root_hits[can_id] = sorted({
            f"0x{address:08X}" for address in authority_root_addresses
            if f"{address:08x}" in funcs[entry].lower()
        })
    if any(direct_root_hits.values()):
        raise ValueError(f"direct cooperative-root Tx-packer reference drift: {direct_root_hits!r}")
    if len(root_spellings) != len(authority_root_names):
        raise AssertionError("root spelling construction")

    app = equiv["application_equivalence"]
    if not (app["identical"] and app["different_bytes"] == 0 and app["start"] == "0x20000" and app["end_exclusive"] == "0x100000"):
        raise ValueError("H/F application equivalence drift")
    if min(funcs) < 0x20000 or max(PROFILE_TABLES) >= 0x100000:
        raise AssertionError("evidence escaped H/F byte-identical application range")

    five_pdu = []
    roles = {
        "0x030": "three duplicated coarse aggregate-status bits are recovered; they are not exact cooperative authority",
        "0x351": "mixed electrical-monitor status and a separate force-7 path; no exact cooperative-authority bit recovered",
        "0x394": "17-state fault/status classifier; no exact cooperative-authority bit recovered",
        "0x4A3": "telemetry/status including measured angle, torque, and Q-current; no exact cooperative-authority bit recovered",
        "0x4C8": "packer sources are fixed to 9, 0, and 0; no exact cooperative-authority bit recovered",
    }
    for can_id, entry in PACKERS.items():
        five_pdu.append({
            "can_id": can_id,
            "pdu": descriptors[can_id]["pdu"],
            "descriptor": descriptors[can_id]["descriptor"],
            "packer": f"0x{entry:08X}",
            "direct_cooperative_root_references": direct_root_hits[can_id],
            "classification": roles[can_id],
            "exact_wire_visible_cooperative_authority_bit_recovered": False,
        })

    result = {
        "schema": "corolla-hf-cooperative-authority-wire-visibility-v1",
        "software_ids": ["8965H1202000", "8965F1208000"],
        "sources": {
            "h_codeflash": {"path": rel(args.image), "sha256": sha(image)},
            "decompiler_evidence": {"path": rel(args.evidence), "sha256": sha(evidence_bytes), "function_count": len(funcs)},
            "fd_control_interface": {"path": rel(FD), "sha256": sha(FD.read_bytes())},
            "openpilot_state_bridge": {"path": rel(STATE), "sha256": sha(STATE.read_bytes())},
            "h_f_equivalence": {"path": rel(EQUIV), "sha256": sha(EQUIV.read_bytes()), "application_sha256": app["baseline_sha256"]},
        },
        "exact_cooperative_gate": {
            "raw_mode_source": "0xFEBE7C58",
            "raw_mode_stage": "0xFEBEF000",
            "stage_copy": "0x0005262C",
            "normalizer": "0x000B8EEC",
            "normalized_mode": "0xFEBEACBD",
            "normalization": {"0": 0, "1": 1, "2": 2, "3": 4, "other_nonzero": 1},
            "acceptance_decoder": "0x000CBE6E",
            "acceptance_condition": "FEBEACBD == 0 AND FEBEC26D == 1",
            "outputs": ["0xFEBEC26E", "0xFEBEC26F", "0xFEBEC270", "0xFEBEC271", "0xFEBEC272", "0xFEBEC273"],
        },
        "positive_coarse_mode_wire_path": {
            "path": [
                "FEBE7C58", "0x0005262C", "FEBEF000", "0x000B23A2", "FEBEB118",
                "0x000BBA48", "FEBEE887", "0x000470C6",
                "FEBE7E09/FEBE7E0B/FEBE7E0D", "0x0004766A", "CAN 0x030",
            ],
            "raw_mode_predicate": "FEBEF000 < 2",
            "predicate_role": "one conjunct in a larger aggregate predicate also using FEBEF146, FEBEF069, FEBEB13E, FEBEB054, and a calibrated residual threshold",
            "asserted_value": "0x5A is propagated through FEBEB118/FEBEE887 and compared at 0x470C6",
            "wire_bits": [
                {"signal_id": signal, "source": expected[0], "wire": f"B{expected[1]}[{expected[2]}]"}
                for signal, expected in expected_wire.items()
            ],
            "classification": "wire-visible coarse aggregate system-mode status influenced by raw mode; not an exact authority or authority-loss indicator",
        },
        "exact_authority_negative": {
            "distinguishing_pair": {
                "raw_mode_0": "FEBEF000<2 is true and B8EEC emits FEBEACBD=0, permitting CBE6E when the health gate is 1",
                "raw_mode_1": "FEBEF000<2 is also true but B8EEC emits FEBEACBD=1, preventing CBE6E",
            },
            "proof": "The recovered 0x030 path cannot encode exact FEBEACBD authority because its mode predicate maps two raw values with opposite exact-gate outcomes to the same branch input; the aggregate also depends on five other conditions.",
            "exact_wire_visible_cooperative_authority_bit_recovered": False,
        },
        "indirect_profile_flag_consumers": {
            "absolute_pointer_occurrences": occurrences,
            "tables": tables,
            "consumer_chain": [
                "0xD0E18/0xD0E54 -> 0xC5156 -> 0xCAF84 -> FEBEBC52 -> 0xC51EA internal gain product",
                "0xD1118/0xD1154 -> 0xC6D16 -> 0xCAF84 -> FEBEBE28 -> 0xC6DAA internal gain product",
            ],
            "classification": "fixed CodeFlash pointer-table use of profile flags as internal gain selectors, not discrete Tx fields",
        },
        "five_pdu_boundary": five_pdu,
        "static_conclusion": {
            "coarse_mode_aggregate_bits_recovered": True,
            "coarse_mode_wire_can_id": "0x030",
            "exact_wire_visible_cooperative_authority_bit_recovered": False,
            "confidence": "verified raw structure and recovered interpretation",
            "transfer_to_8965F1208000": "exact: all cited code and tables lie in the byte-identical 0x20000..0x0FFFFF application range",
        },
        "evidence_boundary": (
            "The five configured normal H/F Tx PDUs were checked at their packers for direct cooperative-root reads; the missed raw-mode route was followed through fixed-GP copies and computed aliases; and all raw absolute pointer materializations of the exact/profile roots were enumerated, with the profile pointers resolved through both fixed CodeFlash table families to internal gain consumers. This proves no exact discrete cooperative-authority bit under those direct, fixed-GP, simple computed-alias, and fixed-CodeFlash-pointer-table surfaces. It does not exclude arbitrary mutable runtime pointers, DMA/peripheral mutation, physical actuator-response inference, or another ECU assigning a different meaning to the coarse 0x030 bits. No live authority transition is claimed."
        ),
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(f"wrote {args.out}: five PDUs, exact authority negative, 0x030 coarse path positive")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
