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
from tools.camry_f33_corpus import IMAGE, IMAGE_SHA256, body_bytes  # noqa: E402
EVID = REPO / "data/generated/camry_8965F3307000_tss3_tx_decompiler_evidence.json"
OUT = REPO / "data/generated/camry_8965F3307000_tss3_opendbc_port.json"
NESTED_OPENDDBC_COMMIT = "ab60fd95d8a7b566e10ed1cf59738292f3498932"
PARENT_OPENPILOT_COMMIT = "d7d7dfd7e49961e9d35eb7a7681e8756ceee8d04"
DEVELOPMENT_NESTED_OPENDDBC_COMMIT = "dde0fcf0fbaf875750c54a072b0dcb3857f8829b"
DEVELOPMENT_PARENT_OPENPILOT_COMMIT = "15f3550365e2eee54ca5645ae9c24d9d41ae4f31"
UPSTREAM_REQUEST_NESTED_OPENDDBC_COMMIT = "b9e86924b96eac248b6b9e6bcf0d4dfdc95b62d0"
RUNTIME_REMOVAL_PARENT_OPENPILOT_COMMIT = "abf3ca70a713d21b88a0cd0241f0650a3d96db7a"
CURRENT_NESTED_OPENDDBC_COMMIT = "525ee987f32167f7e579a4cc773d0d4a8ab7794b"
CURRENT_PARENT_OPENPILOT_COMMIT = "1f26280ac6f2a0733877a08540aa3336d0a50d47"
TX = struct.Struct("<IBBH")
PDU = struct.Struct("<HBBHBB")
TX_TABLE = 0x21F58
SIGNAL_TO_PDU = 0x22488
PDU_TABLE = 0x226C0
PDU_SLICE_TABLE = 0x22840
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
    need(evid["function_count"] == 16, "Tx evidence function count drift")

    funcs = {int(row["entry"], 16): row for row in evid["functions"]}
    need(len(funcs) == 16, "duplicate/missing Tx evidence functions")
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
    # FUN_0007d05c submits each PDU by copying its descriptor length out of the shared
    # pack buffer at FEBE4A48 starting at the per-PDU u16 slice offset in the table at
    # 0x22840. FUN_0007d31e's second argument is an absolute buffer byte offset, so a
    # signal's wire bytes are (buffer_offset - pdu_slice_offset).
    pdu_slice = list(struct.unpack_from("<5H", image, PDU_SLICE_TABLE))
    need(pdu_slice == [0, 32, 36, 39, 47], f"F33 PDU slice-offset table drift: {pdu_slice}")
    # 0x4A3 anchor: signal 44 buffer offset 0x27 - PDU3 slice 39 => wire B0.
    need(0x27 - pdu_slice[3] == 0, "0x4A3 signal-44 wire anchor drift")
    # 0x030 mapped motor feedback: signal 33 buffer offset 0x16 - PDU0 slice 0 => B22:B23.
    need(0x16 - pdu_slice[0] == 22 and 22 + 2 <= pdu_rows[0][3], "signal-33 wire byte derivation drift")

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
    need_tokens(funcs, 0x4C97A,
                "FUN_0007d31e(0,0,8,0", "FUN_0007d31e(0x21,0x16,0x10,0",
                "FUN_0007d31e(10,7,8,0", "FUN_0007d0ea(0)")

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

    # The live 0x030 current-like field is target-native, not a transferred H
    # interpretation.  The extended Q-axis sum is clamped into the DID1151
    # upstream cell and independently enters a nonlinear two-axis map.  That
    # mapped result is mirrored through GP-0x50E8, scaled, and packed at B22:B23.
    aggregate = need_tokens(funcs, 0x37E48,
                            "DAT_febe6e28", "DAT_febe6e2c", "DAT_febe6e30", "DAT_febe6e34",
                            "DAT_febe6d78 = iVar2 + iVar4", "DAT_febe6d72 = (short)iVar5")
    mapped = need_tokens(funcs, 0x38678,
                         "DAT_00031d44", "DAT_00031d46", "DAT_00031d48", "DAT_00031d4a", "DAT_00031d4c",
                         "(&PTR_DAT_000210f4)", "if ((int)param_1 < 1)")
    publish = need_tokens(funcs, 0x3879E, "DAT_febe6d78", "DAT_febe6d70", "FUN_00038678")
    tx030_source = need_tokens(funcs, 0x4C490,
                               "puVar4 + -0x50e8", "puVar4 + 0x30d8", "puVar4 + -0x3694")
    need(all(token in aggregate for token in ("DAT_febe6d70", "DAT_febe6d72", "DAT_febe6d78")),
         "actual-current aggregate staging drift")
    need("return iVar2" in mapped and "UNK_ffffb600" in publish,
         "mapped current-feedback publication drift")
    need("* 100) / 0x2000" in tx030_source, "0x030 current scale formula drift")

    def ref_types(entry: int, address: int) -> set[str]:
        return {
            ref["ref_type"] for ref in funcs[entry]["data_references"]
            if int(ref["to_addr"], 16) == address
        }

    need(ref_types(0x3879E, 0xFEBE6E00) == {"WRITE"}, "mapped feedback destination drift")
    need(ref_types(0x4C490, 0xFEBE6718) == {"READ"} and
         ref_types(0x4C490, 0xFEBEE8D8) == {"READ"} and
         ref_types(0x4C490, 0xFEBE816C) == {"WRITE"}, "0x030 current source/stage refs drift")

    census = evid["fixed_gp_census"]
    torque_refs = [row["entry"] for row in census["driver_torque_source_gp_minus_0x5158"]]
    current_alt_refs = [row["entry"] for row in census["alternate_4a3_current_source_gp_minus_0x50e8"]]
    did1151_refs = [row["entry"] for row in census["did1151_q_current_source_gp_minus_0x50f2"]]
    need(torque_refs == ["0x00035A06", "0x0004C000", "0x0004C490", "0x0004DB70", "0x00052CA0", "0x00054244", "0x000564CE", "0x00059448", "0x0005D5E0"], "canonical torque census drift")
    need(current_alt_refs == ["0x0004C000", "0x0004C490", "0x00059448", "0x0005D12C"], "0x4A3 alternate-current census drift")
    need(did1151_refs == ["0x0004E394", "0x00052CA0", "0x00054244", "0x000564CE", "0x00059448", "0x0005D12C"], "DID1151 Q-current census drift")
    mapped_refs = [row["entry"] for row in census["mapped_current_feedback_gp_minus_0x4a00"]]
    qsum_refs = [row["entry"] for row in census["did1151_q_current_upstream_gp_minus_0x4a8e"]]
    scale_refs = [row["entry"] for row in census["tx030_current_scale_gp_plus_0x30d8"]]
    need(mapped_refs == ["0x0003879E", "0x00057FD2", "0x00059448", "0x0005D12C"], "mapped-feedback census drift")
    need(qsum_refs == ["0x00037E48", "0x00037F92", "0x00059448", "0x0005C7B6", "0x0005CA3A", "0x0005D12C"], "extended Q-axis-sum census drift")
    need(scale_refs == ["0x0004C490", "0x000BF3AA", "0x000BF97A"], "0x030 runtime-scale census drift")

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
            "pdu_slice_offset_table": f"0x{PDU_SLICE_TABLE:08X}",
            "pdu_slice_offsets": pdu_slice,
            "wire_byte_rule": "FUN_0007d31e param_2 is an absolute pack-buffer byte offset; wire bytes = buffer_offset - pdu_slice_offsets[pdu]",
            "signal_count": SIGNAL_COUNT,
            "pdu_descriptors": {str(i): list(row) for i, row in enumerate(pdu_rows)},
            "signal_allocations": {str(i): values for i, values in allocations.items()},
        },
        "status_carriers": {
            "0x030": {
                "pdu": 0,
                "length": 32,
                "source_preparation": "0x0004C490",
                "packer": "0x0004C97A",
                "driver_torque_fields": [
                    {"wire": "B8", "signal_id": 11, "role": "coarse signed Steering Wheel Torque", "scale": "0.1 N.m/count"},
                    {"wire": "B17[3:0]", "signal_id": 30, "role": "signed decimal digit of Steering Wheel Torque", "scale": "0.01 N.m/count"},
                    {"wire": "B8 plus B17[3:0]", "role": "combined signed Steering Wheel Torque", "formula": "signed8(B8)*0.1 + signed4(B17[3:0])*0.01 N.m"},
                ],
                "mapped_motor_feedback": {
                    "signal_id": 33,
                    "wire": "B22:B23",
                    "wire_derivation": "FUN_0007d31e(0x21,0x16,0x10,0) buffer offset 0x16 - PDU0 slice offset 0 => 0x030 wire bytes 22:23, big-endian",
                    "pdu_slice_offset_table": "0x00022840",
                    "wire_decode": "signed big-endian 16-bit",
                    "source_chain": [
                        "0x00037E48: dual-channel feedback sums -> FEBE6D70 plus extended Q-axis sum FEBE6D78; saturated FEBE6D72 is the DID1151 upstream source",
                        "0x00038678: abs/sign-preserving lookup interpolation over FEBE6D78, conditioned by FEBE6D70",
                        "0x0003879E: mapped result -> FEBE6E00",
                        "0x00059448/0x0005D12C: FEBE6E00 -> FEBE6718",
                        "0x0004C490: FEBE6718 plus unsigned scale FEBEE8D8 -> FEBE816C",
                        "0x0004C97A: signal33 -> 0x030 B22:B23",
                    ],
                    "staging_formula": "signed16(((((int)(-signed16(FEBE6718)) * unsigned16(FEBEE8D8)) / 0x100) * 100) / 0x2000)",
                    "alternate_staging_writer": "0x00058C9A also writes FEBE816C (and signal-0 source FEBE8132); it is not decompiled here and carries no semantic claim",
                    "classification": "nonlinear mapped motor-feedback/current-family proxy sharing the pre-clamp Q-axis aggregate that feeds DID 0x1151",
                    "semantic_boundary": "The source family is now target-natively joined to DID1151's pre-clamp Q-axis aggregate, but B22:B23 is not DID1151 in wire units: a sibling-axis-conditioned lookup and a separate runtime scale intervene. Treat it as a signed motor-feedback/assist proxy, not amperes, commanded torque, or LTA authority. Motor feedback is never by itself proof of an external lateral command: driver EPS assist also creates current.",
                },
            },
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
                    "F33 0x4A3 uses GP-0x50E8, while DID 0x1151 Motor Actual Current (Q Axis) reads GP-0x50F2. "
                    "The upstream join is now closed: GP-0x50E8 is a nonlinear sibling-axis-conditioned map of the same extended Q-axis sum that is saturated into the DID1151 source. "
                    "It is therefore a motor-current-family feedback proxy, but not DID1151 in wire units and not yet amperes or commanded torque."
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
            "current_nested_opendbc_commit": CURRENT_NESTED_OPENDDBC_COMMIT,
            "current_parent_kai_openpilot_commit": CURRENT_PARENT_OPENPILOT_COMMIT,
            "upstream_request_decode_commit": UPSTREAM_REQUEST_NESTED_OPENDDBC_COMMIT,
            "lateral_request_observation": "passive 0x08A Target Lateral ID / target-angle / modulo-64 sequence; exact F33 neither accepts 0x08A as normal Rx nor lists it among the five generated-COM Tx IDs",
            "remaining_live_gates": [
                "identify the observed Bus-4 0x08A producer and exact SecOC/security ownership",
                "identify which exact external/local state selects or modulates F33's B6-independent D0218/CC60/CC50 assist path during stock LTA/LCA",
                "decide whether protected B6 is the intended openpilot actuation interface; if so recover its signing/freshness/suppression contract separately from the stock-LTA path",
                "driver override and motor-current response policy",
                "live 0x351/0x394/0x4A3 availability and fault-policy transitions",
            ],
        },
        "gate2_development_integration": {
            "status": "historical-runtime-removed",
            "historical_nested_opendbc_commit": DEVELOPMENT_NESTED_OPENDDBC_COMMIT,
            "historical_parent_kai_openpilot_commit": DEVELOPMENT_PARENT_OPENPILOT_COMMIT,
            "removed_in_nested_opendbc_commit": UPSTREAM_REQUEST_NESTED_OPENDDBC_COMMIT,
            "removed_in_parent_kai_openpilot_commit": RUNTIME_REMOVAL_PARENT_OPENPILOT_COMMIT,
            "current_nested_opendbc_commit": CURRENT_NESTED_OPENDDBC_COMMIT,
            "current_parent_kai_openpilot_commit": CURRENT_PARENT_OPENPILOT_COMMIT,
            "default_enabled": False,
            "runtime_selectable": False,
            "release_branch_allowed": False,
            "historical_target_binding": "exact TOYOTA_CAMRY_TSS3 + current EPS F181 containing 8965F3307000 + relay-correct bus0 topology",
            "historical_runtime_config": {
                "master_enable": "ToyotaTSS3DevLateral",
                "json": "ToyotaTSS3DevLateralConfig",
                "required_live_fields": [
                    "f181=8965F3307000",
                    "stock-captured 28-byte b6_template_hex",
                    "stock-captured cadence_frames",
                    "gate2_bypass_validated=true",
                    "exclusive_b6_authority_validated=true",
                ],
            },
            "historical_sender": (
                "Active ID11 only; exact-F33 +/-1745 raw clamp and +78 raw command-step clamp; "
                "required a strictly newer stock 0x00F epoch, used FV46/FV4 replacement counters, "
                "and intentionally transmitted zero MAC28 for the historical Gate-2 bypass experiment."
            ),
            "panda_debug_test_boundary": (
                "ALLOW_DEBUG-only Toyota TSS3 development safety flag remains for tests and installs a dedicated bus0/32-byte 0x0B6-only TX whitelist; "
                "no current Camry CarParams/CarInterface/CarController path selects it. The hook enforces ID11, +/-1745 raw, strict +1 sequence, "
                "+/-78 raw step, abs steering-rate <=100, and 35-ms active timeout. Ordinary Toyota modes still cannot TX B6."
            ),
            "historical_inactive_behavior": (
                "removed sender emitted no invented inactive B6 frame; it disarmed after active->inactive and required a newer sync epoch before reactivation"
            ),
            "production_output_authorized": False,
            "current_blocker": (
                "OQ-054: identify the observed Bus-4 0x08A producer/security ownership and independently recover the exact "
                "external/local authority input to F33's B6-independent stock-LTA assist path; do not assume an 0x08A-to-B6 transform. "
                "Only after that should B6 be evaluated separately as a candidate openpilot actuation interface."
            ),
        },
        "sources": {
            "codeflash": {"path": str(IMAGE.relative_to(REPO)), "sha256": IMAGE_SHA256},
            "decompiler_evidence": {"path": str(EVID.relative_to(REPO)), "sha256": sha(EVID.read_bytes())},
        },
        "boundary": (
            "The F33 Tx/status carrier geometry and passive software integration are closed at the stated evidence grades; the former Gate-2 runtime sender is retained here only as historical/test provenance and is removed from current integration. "
            "This artifact does not authorize steering CAN transmission: current Camry output is noOutput/zero CAN. The observed Bus-4 0x08A producer/security ownership and the exact authority input to F33's B6-independent stock-LTA path remain unresolved; B6 is a separate external cooperative-control interface whose production use requires its own signing/freshness/suppression contract."
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
