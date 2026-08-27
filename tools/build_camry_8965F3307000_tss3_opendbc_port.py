#!/usr/bin/env python3
"""Build exact-F33 TSS3 Tx/status evidence for the passive openpilot/opendbc port."""
from __future__ import annotations

import argparse
import hashlib
import json
import struct
from pathlib import Path
import sys

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))
from tools.camry_f33_corpus import body_bytes  # noqa: E402
IMAGE = REPO / "firmware/camry-8965F3307000/CodeFlash.bin"
EVID = REPO / "data/generated/camry_8965F3307000_tss3_tx_decompiler_evidence.json"
OUT = REPO / "data/generated/camry_8965F3307000_tss3_opendbc_port.json"
IMAGE_SHA256 = "42dce8efc42f6ae31718e7713fa2d26bb9191b4a82439778aee4d7afded9b0e7"
NESTED_OPENDDBC_COMMIT = "ab60fd95d8a7b566e10ed1cf59738292f3498932"
PARENT_OPENPILOT_COMMIT = "d7d7dfd7e49961e9d35eb7a7681e8756ceee8d04"
TX = struct.Struct("<IBBH")
PDU = struct.Struct("<HBBHBB")
TX_TABLE = 0x21F58
SIGNAL_TO_PDU = 0x22488
PDU_TABLE = 0x226C0
SIGNAL_COUNT = 284


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def need(cond: object, msg: str) -> None:
    if not cond:
        raise ValueError(msg)


def need_tokens(funcs: dict[int, dict], entry: int, *tokens: str) -> str:
    need(entry in funcs, f"missing evidence function 0x{entry:08X}")
    text = funcs[entry]["decompiled_c"]
    for token in tokens:
        need(token in text, f"0x{entry:08X} missing token {token!r}")
    return text


def build() -> dict:
    image = IMAGE.read_bytes()
    evid = json.loads(EVID.read_text(encoding="utf-8"))
    need(len(image) == 0x100000 and sha(image) == IMAGE_SHA256, "exact F33 image drift")
    need(evid["schema"] == "camry-8965f3307000-tss3-tx-decompiler-evidence-v1", "Tx evidence schema drift")
    need(evid["software_id"] == "8965F3307000" and evid["image"]["sha256"] == IMAGE_SHA256, "Tx evidence target drift")
    need(evid["function_count"] == 11, "Tx evidence function count drift")

    funcs = {int(row["entry"], 16): row for row in evid["functions"]}
    need(len(funcs) == 11, "duplicate/missing Tx evidence functions")
    for entry, row in funcs.items():
        need(sha(body_bytes(image, row)) == row["body_sha256"], f"body hash drift 0x{entry:08X}")

    # Exact F33 generated-COM transmit table and PDU allocation.
    tx_rows = [TX.unpack_from(image, TX_TABLE + i * TX.size) for i in range(5)]
    tx_ids = [(raw_id & 0x7FF, bool(raw_id & 0x40000000), period, length, flags) for raw_id, period, length, flags in tx_rows]
    expected_tx = [
        (0x030, True, 0, 0, 0),
        (0x351, False, 0, 0, 1),
        (0x394, False, 0, 0, 1),
        (0x4A3, False, 0, 0, 1),
        (0x4C8, False, 0, 0, 1),
    ]
    need(tx_ids == expected_tx, f"F33 first-five Tx descriptor drift: {tx_ids}")

    pdu_rows = [PDU.unpack_from(image, PDU_TABLE + i * PDU.size) for i in range(5)]
    expected_pdu = [
        (2, 0, 0, 32, 0, 3),
        (200, 0, 0, 4, 0, 3),
        (60, 0, 0, 3, 0, 3),
        (100, 0, 0, 8, 0, 3),
        (196, 0, 0, 8, 0, 3),
    ]
    need(pdu_rows == expected_pdu, f"F33 first-five Tx PDU descriptor drift: {pdu_rows}")

    signal_map = [struct.unpack_from("<H", image, SIGNAL_TO_PDU + i * 2)[0] for i in range(SIGNAL_COUNT)]
    allocations = {pdu: [i for i, mapped in enumerate(signal_map) if mapped == pdu] for pdu in range(5)}
    need(allocations[0] == list(range(38)) + [283], "F33 PDU0 signal allocation drift")
    need(allocations[1] == [38, 39], "F33 PDU1/0x351 signal allocation drift")
    need(allocations[2] == [40, 41, 42, 43], "F33 PDU2/0x394 signal allocation drift")
    need(allocations[3] == list(range(44, 52)), "F33 PDU3/0x4A3 signal allocation drift")
    need(allocations[4] == list(range(52, 56)), "F33 PDU4/0x4C8 signal allocation drift")

    # Target-native generated pack helpers and exact carrier fields.
    need_tokens(funcs, 0x7D1DC, "&DAT_00022488 + (param_1 & 0xffff) * 2", "param_3 < 0x11", "(param_2 & 0xffff) - 0x6db8")
    need_tokens(funcs, 0x4CED0,
                "FUN_0007d1dc(0x26,0x22,3,5", "FUN_0007d1dc(0x27,0x22,1,4", "FUN_0007d0ea(1)")
    need_tokens(funcs, 0x4CE08,
                "FUN_0007d1dc(0x28,0x25,2,6", "FUN_0007d1dc(0x29,0x25,3,3",
                "FUN_0007d1dc(0x2a,0x26,3,1", "FUN_0007d1dc(0x2b,0x26,1,0", "FUN_0007d0ea(2)")
    need_tokens(funcs, 0x4C7AA,
                "FUN_0007d31e(0x2c,0x27,8,0", "FUN_0007d31e(0x33,0x2e,8,0", "FUN_0007d0ea(3)")

    source = need_tokens(funcs, 0x4C000,
                         "DAT_febe66a8", "* 100) / 0x100", "DAT_febe8152 = 1000", "DAT_febe8152 = -1000",
                         "DAT_febe6718", "* -100) / 0x80")
    stage = need_tokens(funcs, 0x4C14E,
                        "DAT_febe8048", ">> 8) & 0xf", "DAT_febe7d46", "0x7ff", "0xfffff800",
                        "puVar1 + -0x36ae", "puVar1 + -0x36a8")
    need("DAT_febe66a8" in source and "DAT_febe6718" in source, "0x4A3 source-stage drift")
    need("DAT_febe8048" in stage and "DAT_febe7d46" in stage, "0x4A3 angle-stage drift")

    need_tokens(funcs, 0x4C1C0, "DAT_febe8100", "DAT_0002fbf8")
    need_tokens(funcs, 0x4C216, "param_1 = 7;", "DAT_febe8100", "DAT_febe8101")
    need_tokens(funcs, 0x4C24A, "uVar1 = DAT_febe82a0 - 1", "DAT_febe810a", "DAT_febe8102")

    census = evid["fixed_gp_census"]
    torque_refs = [row["entry"] for row in census["driver_torque_source_gp_minus_0x5158"]]
    current_alt_refs = [row["entry"] for row in census["alternate_4a3_current_source_gp_minus_0x50e8"]]
    did1151_refs = [row["entry"] for row in census["did1151_q_current_source_gp_minus_0x50f2"]]
    need(torque_refs == ["0x00035A06", "0x0004C000", "0x0004C490", "0x0004DB70", "0x00052CA0", "0x00054244", "0x000564CE", "0x00059448", "0x0005D5E0"], "canonical torque census drift")
    need(current_alt_refs == ["0x0004C000", "0x0004C490", "0x00059448", "0x0005D12C"], "0x4A3 alternate-current census drift")
    need(did1151_refs == ["0x0004E394", "0x00052CA0", "0x00054244", "0x000564CE", "0x00059448", "0x0005D12C"], "DID1151 Q-current census drift")

    return {
        "schema": "camry-8965f3307000-tss3-opendbc-port-v1",
        "target": {
            "software_id": "8965F3307000",
            "codeflash_sha256": IMAGE_SHA256,
        },
        "generated_com_tx": {
            "tx_table": f"0x{TX_TABLE:08X}",
            "first_five": [
                {"can_id": f"0x{can_id:03X}", "can_fd": can_fd, "period_field": period, "length_field": length, "flags": flags}
                for can_id, can_fd, period, length, flags in tx_ids
            ],
            "signal_to_pdu_table": f"0x{SIGNAL_TO_PDU:08X}",
            "pdu_table": f"0x{PDU_TABLE:08X}",
            "signal_count": SIGNAL_COUNT,
            "pdu_descriptors": {str(i): list(row) for i, row in enumerate(pdu_rows)},
            "signal_allocations": {str(i): values for i, values in allocations.items()},
        },
        "status_carriers": {
            "0x351": {
                "pdu": 1,
                "length": 4,
                "producer": "0x0004C216",
                "debounce": "0x0004C1C0",
                "packer": "0x0004CED0",
                "fields": ["B2[7:5] status code", "B2[4] companion/force flag"],
                "policy_boundary": "Exact wire projection only; no openpilot temporary/permanent fault mapping is inferred.",
            },
            "0x394": {
                "pdu": 2,
                "length": 3,
                "projection": "0x0004C24A",
                "packer": "0x0004CE08",
                "fields": ["B1[7:6] table column 4", "B1[5:3] table column 1", "B2[3:1] table column 2", "B2[0] table column 3"],
                "policy_boundary": "Exact lossy state-table projection only; state 0 is not promoted to Ready or an openpilot fault class.",
            },
            "0x4A3": {
                "pdu": 3,
                "length": 8,
                "source_preparation": "0x0004C000",
                "staging": "0x0004C14E",
                "packer": "0x0004C7AA",
                "fields": [
                    {"wire": "B0[5]", "role": "marker bit from staged status byte OR 0x20"},
                    {"wire": "B0[0]", "role": "selected steering fault/inhibit status bit"},
                    {"wire": "B1[3:0]:B2", "role": "signed12 coarse steering-angle source", "scale": "1.5 deg/count"},
                    {"wire": "B3[3:0]:B4", "role": "signed12 filtered/voted steering-angle quantity", "scale": "1.5 deg/count"},
                    {"wire": "B5", "role": "Steering Wheel Torque telemetry", "scale": "0.1 N.m/count after source staging"},
                    {"wire": "B6:B7", "role": "alternate motor-current telemetry source", "formula": "signed16 = (GP-0x50E8 * -100) / 0x80"},
                ],
                "current_semantic_boundary": (
                    "F33 0x4A3 uses GP-0x50E8, while target-native DID 0x1151 Motor Actual Current (Q Axis) uses GP-0x50F2. "
                    "The packet field must therefore remain structurally named until an F33 source join or live correlation closes equivalence."
                ),
            },
        },
        "census_correction": {
            "supersedes": "VAR-056/VAR-058 scratch-corpus direct/fixed-GP torque-source counts",
            "old_recovered_count": 5,
            "new_recovered_count": 9,
            "new_read_count": 7,
            "new_write_count": 2,
            "new_entry": "0x0004C490",
            "driver_torque_direct_fixed_gp_entries": torque_refs,
            "control_cone_conclusion_changed": False,
            "reason": (
                "The first-class 6,065-function project resolves GP and exposes a canonical Ghidra data-reference graph. It finds seven readers and two writers of FEBE66A8, including previously unrecovered 0x4C490/0x52CA0 and source writers, while preserving zero direct references inside the cooperative C8xxx-D1xxx control cone."
            ),
        },
        "passive_opendbc_integration": {
            "nested_opendbc_commit": NESTED_OPENDDBC_COMMIT,
            "parent_kai_openpilot_commit": PARENT_OPENPILOT_COMMIT,
            "exact_platform": "TOYOTA_CAMRY_TSS3",
            "identity_binding": "byte-exact EPS F181 02||8965F3307000[16]||8A3113303100[16], with present FRC/Brake identities required not to conflict",
            "can_census": "179-ID source-real Camry census retained separately from legacy fingerprinting because the current 147-ID Corolla TSS3 fingerprint is a strict subset",
            "carstate_replay": ["0x025", "0x030", "0x127 P/R/N/D/B", "0x51E Ready 0/1"],
            "static_presence_bounded_carstate": ["0x4A3", "0x351", "0x394"],
            "b6_shadow": "28-byte application template + exact known scalar fields + FV46/FV4 + CMAC128/MSB28 signer interface and authenticated-0x00F replacement freshness state",
            "controller_boundary": "computes a shadow B6 application/safety decision but returns zero CAN",
            "panda_boundary": "F33 C candidate helper is ALLOW_DEBUG-only, not called from toyota_tx_hook, 0x0B6 is absent from Toyota TX whitelists, and CarParams remains SafetyModel.noOutput",
            "production_output_authorized": False,
            "remaining_live_gates": [
                "stock B6 cadence/template/freshness",
                "exclusive relay/source suppression",
                "slot-4 command-5 generation permission and latency/contention",
                "driver override and motor-current response policy",
                "live 0x351/0x394/0x4A3 availability and fault-policy transitions",
            ],
        },
        "sources": {
            "codeflash": {"path": str(IMAGE.relative_to(REPO)), "sha256": IMAGE_SHA256},
            "decompiler_evidence": {"path": str(EVID.relative_to(REPO)), "sha256": sha(EVID.read_bytes())},
        },
        "boundary": (
            "The F33 Tx/status carrier geometry and passive software integration are closed at the stated evidence grades. "
            "This artifact does not authorize steering CAN transmission or claim that the still-unobserved status carriers are available on the production relay-correct route."
        ),
    }


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
