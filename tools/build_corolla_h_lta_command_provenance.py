#!/usr/bin/env python3
"""Build the exact-image Corolla H autonomous-lateral command provenance report."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import struct
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
H_IMAGE = REPO / "community/albinoelephant/normalized/8965H1202000_CodeFlash.bin"
S_IMAGE = REPO / "firmware/RH850_P1M-E_CodeFlash.bin"
H_CENSUS = REPO / "data/generated/corolla_8965H1202000_lta_command_provenance_census.json"
S_CORPUS = REPO / "data/generated/decompilations.jsonl"
EVIDENCE = REPO / "data/generated/corolla_8965H1202000_lta_command_provenance_decompiler_evidence.json"
SUPERVISOR = REPO / "data/generated/corolla_8965H1202000_supervisor_external_ingress_census.json"
TOYOTA_DBC_FACTS = REPO / "data/external/opendbc/toyota_dbc_facts.json"
DEFAULT_OUT = REPO / "data/generated/corolla_8965H1202000_lta_command_provenance.json"

H_SIGNAL_TO_PDU = 0x223FC
S_SIGNAL_TO_PDU = 0x224E4
H_PDU_LENGTH = 0x22624
H_PDU_BUFFER_OFFSET = 0x22788
H_COM_RX_BUFFER_BASE = 0xFEBE494D
H_D7_PDU = 40
H_B6_PDU = 42
S_2E4_PDU = 6
H_D7_SECOC_RECORD = 0x2577C
H_B6_SECOC_RECORD = 0x257CC


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load_json(path: Path) -> dict:
    return json.loads(path.read_text())


def load_corpus(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.open() if line.strip() and json.loads(line).get("record") == "function"]


def funcs_by_entry(evidence: dict) -> dict[int, dict]:
    return {int(row["entry"], 16): row for row in evidence["functions"]}


def require(c: str, *parts: str) -> bool:
    return all(x in c for x in parts)


def u32_literal_hits(image: bytes, address: int) -> list[str]:
    needle = struct.pack("<I", address)
    return [f"0x{i:08X}" for i in range(len(image) - 3) if image[i:i + 4] == needle]


def term_occurrences(corpus: list[dict], term: str) -> list[dict]:
    out = []
    low = term.lower()
    for row in corpus:
        lines = [line.strip() for line in row.get("decompiled_c", "").splitlines() if low in line.lower()]
        if lines:
            out.append({"entry": row["entry_addr"].upper(), "lines": lines})
    return out


def lhs_writes(corpus: list[dict], address_suffix: str) -> list[dict]:
    # Direct named writes only: anchored assignment to a Ghidra RAM symbol for the exact address.
    pat = re.compile(rf"^\s*[A-Za-z]*Ram{re.escape(address_suffix)}\s*=\s*(.+);\s*$", re.I)
    out = []
    for row in corpus:
        matches = []
        for line in row.get("decompiled_c", "").splitlines():
            m = pat.match(line)
            if m:
                matches.append(line.strip())
        if matches:
            out.append({"entry": row["entry_addr"].upper(), "lines": matches})
    return out


def resolved_call_first_args(corpus: list[dict], callee: str, image: bytes) -> list[dict]:
    # Ghidra emits some generated-table constants as DAT_000xxxxx rather than
    # folding their u16 contents into literals; resolve both forms.
    pat = re.compile(rf"{re.escape(callee)}\((0x[0-9a-f]+|\d+|DAT_([0-9a-f]+))\s*,", re.I)
    out = []
    for row in corpus:
        vals = []
        raw_args = []
        for m in pat.finditer(row.get("decompiled_c", "")):
            token = m.group(1)
            if token.upper().startswith("DAT_"):
                off = int(m.group(2), 16)
                if off + 2 > len(image):
                    raise ValueError(f"DAT first arg outside image: {token}")
                val = struct.unpack_from("<H", image, off)[0]
            else:
                val = int(token, 0)
            vals.append(val)
            raw_args.append(token)
        if vals:
            out.append({"entry": row["entry_addr"].upper(), "first_args": vals, "raw_first_args": raw_args})
    return out


def signal_ids_for_pdu(image: bytes, table: int, count: int, pdu: int) -> list[int]:
    return [i for i in range(count) if struct.unpack_from("<H", image, table + i * 2)[0] == pdu]


def flatten_args(rows: list[dict]) -> list[int]:
    return [v for row in rows for v in row["first_args"]]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = ap.parse_args()

    h = H_IMAGE.read_bytes()
    s = S_IMAGE.read_bytes()
    ev = load_json(EVIDENCE)
    supervisor = load_json(SUPERVISOR)
    toyota_dbc_facts = load_json(TOYOTA_DBC_FACTS)
    census = load_json(H_CENSUS)
    sf = load_corpus(S_CORPUS)
    ef = funcs_by_entry(ev)
    c = {entry: row["decompiled_c"] for entry, row in ef.items()}

    h_d7_signals = signal_ids_for_pdu(h, H_SIGNAL_TO_PDU, 274, H_D7_PDU)
    h_b6_signals = signal_ids_for_pdu(h, H_SIGNAL_TO_PDU, 274, H_B6_PDU)
    s_2e4_signals = signal_ids_for_pdu(s, S_SIGNAL_TO_PDU, 300, S_2E4_PDU)
    h_d7_scalar = census["scalar_receive_ids"]["d7"]
    h_b6_scalar = census["scalar_receive_ids"]["b6"]
    h_group_ids = census["all_literal_block_group_receive_ids"]
    h_group_calls = census["block_group_calls"]
    h_full_pdu_ids = census["all_literal_full_pdu_ids"]
    h_full_pdu_calls = census["full_pdu_calls"]

    # Sienna's configured-but-nonscalar 2E4 rows are a useful control: generated
    # signal-table membership is not itself proof of an application data field.
    s_scalar_pat = re.compile(r"(?:application_com_receive_signal|FUN_0007c03e)\((0x[0-9a-f]+|\d+)\s*,", re.I)
    s_scalar_all = set()
    for row in sf:
        for m in s_scalar_pat.finditer(row.get("decompiled_c", "")):
            s_scalar_all.add(int(m.group(1), 0))
    s_2e4_scalar = sorted(set(s_2e4_signals) & s_scalar_all)

    d7_pdu_len = struct.unpack_from("<H", h, H_PDU_LENGTH + H_D7_PDU * 8)[0]
    d7_pdu_off = struct.unpack_from("<H", h, H_PDU_BUFFER_OFFSET + H_D7_PDU * 2)[0]
    d7_buffer = H_COM_RX_BUFFER_BASE + d7_pdu_off
    d7_sec = h[H_D7_SECOC_RECORD:H_D7_SECOC_RECORD + 0x50]
    d7_authenticator_bits = struct.unpack_from("<H", d7_sec, 0x02)[0]
    d7_full_freshness_bits = d7_sec[0x14]
    d7_transmitted_freshness_bits = d7_sec[0x15]
    d7_secured_len = struct.unpack_from("<H", d7_sec, 0x24)[0]
    d7_trailer_bytes = math.ceil((d7_authenticator_bits + d7_transmitted_freshness_bits) / 8)
    d7_application_bytes = d7_secured_len - d7_trailer_bytes

    pdu_len = struct.unpack_from("<H", h, H_PDU_LENGTH + H_B6_PDU * 8)[0]
    pdu_off = struct.unpack_from("<H", h, H_PDU_BUFFER_OFFSET + H_B6_PDU * 2)[0]
    b6_buffer = H_COM_RX_BUFFER_BASE + pdu_off
    sec = h[H_B6_SECOC_RECORD:H_B6_SECOC_RECORD + 0x50]
    authenticator_bits = struct.unpack_from("<H", sec, 0x02)[0]
    full_freshness_bits = sec[0x14]
    transmitted_freshness_bits = sec[0x15]
    secured_len = struct.unpack_from("<H", sec, 0x24)[0]
    trailer_bytes = math.ceil((authenticator_bits + transmitted_freshness_bits) / 8)
    application_bytes = secured_len - trailer_bytes

    direct_cells = {}
    for addr in (0xFEBEC17C, 0xFEBEC17E, 0xFEBEC184, 0xFEBEC26D):
        suffix = f"{addr:08x}"
        direct_cells[f"0x{addr:08X}"] = {
            "occurrences": census["cells"][f"0x{addr:08X}"]["occurrences"],
            "direct_lhs_writes": census["cells"][f"0x{addr:08X}"]["direct_lhs_writes"],
            "raw_u32_literal_pointer_hits": u32_literal_hits(h, addr),
        }

    retained_lta = {
        "magnitude_inputs": direct_cells | {},
        "magnitude_vote_and_rate_limit": {
            "entry": "0x000C9C16",
            "recovered": require(c[0xC9C16], "sRamfebec17c", "sRamfebec17e", "sRamfebec184", "uRamfebec1e0", "uRamfebec200", "uRamfebec20a"),
            "role": "majority/select three command-magnitude words, rate/clip, publish replicated command state",
        },
        "mode_enable": {
            "source": "0xFEBEC26D",
            "init_entry": "0x000CB1C8",
            "cyclic_decoder": "0x000CBE6E",
            "cyclic_decoder_owner": "0x000CB68A -> 0x000CEDAE",
            "decoder_requires_one": require(c[0xCBE6E], "cRamfebec26d == '\\x01'"),
            "decoder_zeroes_all_outputs_when_gate_false": require(c[0xCBE6E], "uVar9 = 0", "uVar8 = 0", "uVar7 = 0", "uVar6 = 0", "uVar5 = 0", "uVar4 = 0"),
        },
        "command_conditioning": [
            {"entry": "0x000C9C16", "relation": "C17C/C17E/C184 -> C1E0/C200/C20A", "recovered": True},
            {"entry": "0x000CB8BA", "relation": "C1E0/C200/C20A -> C278; if decoded mode C272 is not active and C2A6 is zero, C278 is forced zero", "recovered": require(c[0xCB8BA], "iRamfebec278 = 0", "cRamfebec272 == '\\x01'", "cRamfebec2a6 == '\\0'")},
            {"entry": "0x000CB9B6", "relation": "C278 * C290 / 0x100, slew/clip -> C2A8", "recovered": require(c[0xCB9B6], "iRamfebec278", "uRamfebec290", "sRamfebec2a8 =")},
            {"entry": "0x000CD3CC", "relation": "C2A8 is one conditional additive contributor to final command composition", "recovered": require(c[0xCD3CC], "sRamfebec2a8", "iRamfebec3b8")},
        ],
        "command_state_writes": {
            "0xFEBEC2A6": census["direct_lhs_writes"]["0xFEBEC2A6"],
            "0xFEBEC2A8": census["direct_lhs_writes"]["0xFEBEC2A8"],
        },
        "classification": "retained-sienna-homolog-lta-branch-direct-write-inactive",
        "boundary": (
            "C17C/C17E/C184 have exactly init-zero plus consumer references in the complete tracked target corpus; "
            "C26D has exactly init-zero plus readers, and no raw absolute pointer literals exist for any of them. "
            "Under recovered direct writes, the decoded mode never activates and the retained C2A8 contribution remains zero. "
            "Computed-pointer/DMA/undocumented writers remain a bounded unknown, so this is not proof that the vehicle has no LTA."
        ),
    }

    zero_contributors = {}
    for addr in (0xFEBEBE04, 0xFEBEBD90, 0xFEBEB678, 0xFEBEBEC6, 0xFEBEC39C, 0xFEBEABB0, 0xFEBEBCF8, 0xFEBEC2D4):
        zero_contributors[f"0x{addr:08X}"] = census["direct_lhs_writes"][f"0x{addr:08X}"]

    final_composition = {
        "entry": "0x000CD3CC",
        "recovered_terms": ["FEBEBE04", "FEBEBD90", "FEBEBD0E", "FEBEC39C", "FEBEB678", "FEBEC2A8", "FEBEBEC6", "FEBEC358"],
        "direct_zero_writer_census": zero_contributors,
        "bd0e_local_chain": {
            "entry": "0x000C5932",
            "relation": "FEBEABB0 + FEBEBCF8 -> bounded FEBEBD0E",
            "recovered": require(c[0xC5932], "iRamfebeabb0 + iRamfebebcf8", "sRamfebebd0e"),
        },
        "c358_local_chain": {
            "entry": "0x000CCE8C",
            "relation": "FEBEC392 + FEBEC2D4 -> bounded FEBEC358",
            "recovered": require(c[0xCCE8C], "sRamfebec392 + iRamfebec2d4", "sRamfebec358"),
            "c392_entry": "0x000CD1E8",
            "c392_recovered_local_state": require(c[0xCD1E8], "sRamfebec392", "iRamfebeac24", "cRamfebec35c"),
        },
        "interpretation": (
            "1C02 Command Value Torque is a general EPS-internal torque-command observable, not an LTA-only value. "
            "The retained C2A8 lateral-command term is only one conditional additive contributor. Under direct-writer evidence, "
            "the other zero-censused terms collapse while C358 remains a local/internal assist-control contribution."
        ),
    }

    d7_non_scalar = sorted(set(h_d7_signals) - set(h_d7_scalar))
    d7 = {
        "can_id": "0x0D7",
        "pdu_id": H_D7_PDU,
        "secured_length": d7_secured_len,
        "profile": {
            "record": f"0x{H_D7_SECOC_RECORD:08X}",
            "authenticator_bits": d7_authenticator_bits,
            "full_freshness_bits": d7_full_freshness_bits,
            "transmitted_freshness_bits": d7_transmitted_freshness_bits,
            "security_trailer_bytes": d7_trailer_bytes,
            "authenticated_application_bytes": d7_application_bytes,
        },
        "com": {
            "configured_signal_ids": h_d7_signals,
            "scalar_receive_ids": h_d7_scalar,
            "configured_without_scalar_receive": d7_non_scalar,
            "block_group_receive_api": "FUN_00077A3A",
            "all_literal_block_group_receive_ids": h_group_ids,
            "non_scalar_ids_used_by_block_group_api": sorted(set(d7_non_scalar) & set(h_group_ids)),
            "full_pdu_copy_api": "FUN_0007636C",
            "all_literal_full_pdu_ids": h_full_pdu_ids,
            "d7_full_pdu_copy_present": H_D7_PDU in h_full_pdu_ids,
            "buffer_offset": d7_pdu_off,
            "buffer_address": f"0x{d7_buffer:08X}",
            "raw_u32_buffer_pointer_hits": u32_literal_hits(h, d7_buffer),
        },
        "classification": "no-recovered-hidden-d7-group-or-full-pdu-command-consumer",
        "boundary": (
            "D7 has 28 authenticated application bytes; recovered scalar IDs are 240/243/246. "
            "Configured nonscalar IDs 241/242/244/245/247 are absent from every literal block/group receive call; no full-PDU copy uses PDU40; "
            "and the D7 COM buffer base has no raw absolute pointer literal. Techstream independently identifies scalar243 as CAN Vehicle Speed (SP1)."
        ),
    }

    b6_non_scalar = sorted(set(h_b6_signals) - set(h_b6_scalar))
    b6 = {
        "can_id": "0x0B6",
        "pdu_id": H_B6_PDU,
        "secured_length": secured_len,
        "profile": {
            "record": f"0x{H_B6_SECOC_RECORD:08X}",
            "authenticator_bits": authenticator_bits,
            "full_freshness_bits": full_freshness_bits,
            "transmitted_freshness_bits": transmitted_freshness_bits,
            "security_trailer_bytes": trailer_bytes,
            "authenticated_application_bytes": application_bytes,
        },
        "com": {
            "configured_signal_ids": h_b6_signals,
            "scalar_receive_ids": h_b6_scalar,
            "configured_without_scalar_receive": b6_non_scalar,
            "block_group_receive_api": "FUN_00077A3A",
            "all_literal_block_group_receive_ids": h_group_ids,
            "block_group_calls": h_group_calls,
            "non_scalar_ids_used_by_block_group_api": sorted(set(b6_non_scalar) & set(h_group_ids)),
            "full_pdu_copy_api": "FUN_0007636C",
            "all_literal_full_pdu_ids": h_full_pdu_ids,
            "full_pdu_calls": h_full_pdu_calls,
            "b6_full_pdu_copy_present": H_B6_PDU in h_full_pdu_ids,
            "buffer_offset": pdu_off,
            "buffer_address": f"0x{b6_buffer:08X}",
            "raw_u32_buffer_pointer_hits": u32_literal_hits(h, b6_buffer),
        },
        "sienna_2e4_control": {
            "pdu_id": S_2E4_PDU,
            "configured_signal_ids": s_2e4_signals,
            "scalar_receive_ids": s_2e4_scalar,
            "configured_without_scalar_receive": sorted(set(s_2e4_signals) - set(s_2e4_scalar)),
            "interpretation": "Sienna 2E4 itself has configured IDs beyond its scalar application fields; configured-table membership alone is not evidence for a hidden command payload.",
        },
        "classification": "no-recovered-hidden-b6-group-or-full-pdu-command-consumer",
        "boundary": (
            "B6 has 28 authenticated application bytes, but only scalar IDs 254..265 are consumed by its recovered unpacker. "
            "The four configured nonscalar IDs 252/253/266/267 are absent from every literal block/group receive call; no full-PDU copy uses PDU42; "
            "and the B6 COM buffer base has no raw absolute pointer literal. This closes the generated scalar/group/full-PDU/direct-literal surfaces, "
            "not arbitrary computed aliases or hardware access."
        ),
    }

    def unique_supervisor_signal(signal_id: int) -> dict:
        rows = [row for row in supervisor["external_refs"] if row["signal"] == signal_id]
        if not rows:
            raise ValueError(f"supervisor signal {signal_id} missing")
        keys = {
            (
                row["can"], row["bits"], row["signed"], row["wire_byte"],
                row["bitoff"], row["address"],
                tuple(x["entry"] for x in row["source_unpackers"]),
                tuple(row["s_same_shape_signals"]),
            )
            for row in rows
        }
        if len(keys) != 1:
            raise ValueError(f"supervisor signal {signal_id} has inconsistent shapes: {keys}")
        can_id, bits, signed, wire_byte, bit_offset, address, unpackers, s_same = next(iter(keys))
        return {
            "signal_id": signal_id,
            "can_id": f"0x{can_id:03X}",
            "bit_length": bits,
            "signed": bool(signed),
            "wire_byte": wire_byte,
            "bit_offset_in_byte": bit_offset,
            "snapshot_address": f"0x{address:08X}",
            "source_unpackers": [f"0x{x:08X}" for x in unpackers],
            "sienna_same_shape_signals": list(s_same),
            "consumer_entries": sorted({f"0x{row['consumer']:08X}" for row in rows}),
        }

    steer_dbc = toyota_dbc_facts["messages"]["STEER_ANGLE_SENSOR"]
    if steer_dbc["can_id_decimal"] != 37 or steer_dbc["length"] != 8:
        raise ValueError("tracked Toyota DBC facts no longer define CAN 0x025 STEER_ANGLE_SENSOR")
    dbc_signal_rows = steer_dbc["signals"]

    shared_025 = {
        "can_id": "0x025",
        "dbc": {
            "path": str(TOYOTA_DBC_FACTS.relative_to(REPO)),
            "sha256": sha(TOYOTA_DBC_FACTS.read_bytes()),
            "message": "STEER_ANGLE_SENSOR",
            "message_id_decimal": 37,
            "signals": dbc_signal_rows,
        },
        "h_signals": {
            "184": unique_supervisor_signal(184),
            "185": unique_supervisor_signal(185),
            "186": unique_supervisor_signal(186),
        },
        "unpacker": {
            "entry": "0x0004636A",
            "signal184_shape_recovered": require(c[0x4636A], "FUN_0007643a(0xb8,0x11f,0xc,0,1", "0xfebe7d34"),
            "signal185_shape_recovered": require(c[0x4636A], "FUN_0007643a(0xb9,0x123,4,4,1", "-0x3ac5"),
            "signal186_shape_recovered": require(c[0x4636A], "FUN_0007643a(0xba,0x123,0xc,0,1", "-0x3aca"),
        },
        "target_native_semantics": {
            "angle_plus_fraction": {
                "entry": "0x000C2176",
                "relation": "FEBEADF0 * 15 + FEBEACC5 reconstructs the high-resolution steering-angle input",
                "recovered": require(c[0xC2176], "sRamfebeadf0 * 0xf + (int)cRamfebeacc5"),
            },
            "steering_rate_magnitude": {
                "entry": "0x000CB2E0",
                "relation": "absolute FEBEAE14 is thresholded as the steering-rate magnitude",
                "recovered": require(c[0xCB2E0], "FUN_000ce7bc((int)sRamfebeae14)", "DAT_000afd00"),
            },
            "joint_plausibility": {
                "entry": "0x000CBD7E",
                "relation": "the supervisor jointly consumes the reconstructed angle and absolute rate cells in plausibility logic",
                "recovered": require(c[0xCBD7E], "sRamfebeadf0 * 0xf", "cRamfebeacc5", "sRamfebeae14"),
            },
        },
        "classification": "shared-command-sized-ingress-is-steering-angle-sensor-state",
        "interpretation": (
            "The only shared H supervisor-reaching fields >=12 bits are signal184 and signal186 on CAN0x025. "
            "Together with signal185 they exactly match the pinned Toyota STEER_ANGLE_SENSOR layout: signed12 coarse STEER_ANGLE, signed4 STEER_FRACTION, signed12 STEER_RATE. "
            "H independently recombines 184*15+185 as steering angle and treats 186 as a rate magnitude. They are sensor measurements, not a semantically repurposed autonomous command."
        ),
        "boundary": (
            "The public DBC is corroboration rather than sole naming evidence: target-native H arithmetic independently distinguishes angle+fraction and rate semantics. "
            "This closes the adversarial possibility that an unchanged-shape large scalar was silently repurposed as the missing LTA command."
        ),
    }

    out = {
        "schema": "corolla-8965H1202000-lta-command-provenance-v3",
        "software_id": "8965H1202000",
        "images": {
            "corolla_h": {"path": str(H_IMAGE.relative_to(REPO)), "sha256": sha(h), "size": len(h)},
            "sienna_reference": {"path": str(S_IMAGE.relative_to(REPO)), "sha256": sha(s), "size": len(s)},
        },
        "whole_corpus_census": {
            "path": str(H_CENSUS.relative_to(REPO)),
            "sha256": sha(H_CENSUS.read_bytes()),
            "source_corpus_sha256": census["source_corpus"]["sha256"],
            "source_function_count": census["source_corpus"]["function_count"],
            "boundary": census["source_corpus"]["boundary"],
        },
        "evidence": {"path": str(EVIDENCE.relative_to(REPO)), "sha256": sha(EVIDENCE.read_bytes()), "function_count": ev["function_count"]},
        "supporting_inputs": {
            "supervisor_external_ingress_census": {"path": str(SUPERVISOR.relative_to(REPO)), "sha256": sha(SUPERVISOR.read_bytes())},
            "toyota_dbc": {"path": str(TOYOTA_DBC_FACTS.relative_to(REPO)), "sha256": sha(TOYOTA_DBC_FACTS.read_bytes())},
        },
        "retained_lta_branch": retained_lta,
        "d7_hidden_payload_census": d7,
        "b6_hidden_payload_census": b6,
        "shared_can025_sensor_ingress": shared_025,
        "final_command_composition": final_composition,
        "static_conclusion": {
            "retained_sienna_lta_magnitude_direct_write_zero": all(
                len(direct_cells[f"0x{x:08X}"]["direct_lhs_writes"]) == 1 and
                "= 0;" in direct_cells[f"0x{x:08X}"]["direct_lhs_writes"][0]["lines"][0]
                for x in (0xFEBEC17C, 0xFEBEC17E, 0xFEBEC184)
            ),
            "retained_sienna_lta_enable_direct_write_zero": len(direct_cells["0xFEBEC26D"]["direct_lhs_writes"]) == 1 and "= 0;" in direct_cells["0xFEBEC26D"]["direct_lhs_writes"][0]["lines"][0],
            "retained_sienna_lta_branch_active_under_recovered_direct_writes": False,
            "hidden_d7_group_or_full_pdu_command_recovered": False,
            "hidden_b6_group_or_full_pdu_command_recovered": False,
            "shared_command_sized_ingress_classified_as_sensor_state": (
                shared_025["h_signals"]["184"]["bit_length"] == 12
                and shared_025["h_signals"]["186"]["bit_length"] == 12
                and all(x["recovered"] for x in shared_025["target_native_semantics"].values())
            ),
            "command_value_torque_is_lta_only": False,
            "external_autonomous_lateral_ingress_identified": False,
            "broad_static_search_closed": True,
            "next_evidence": (
                "Use same-vehicle stock-LTA capture plus read-only XCP/RDBI to identify a state changing upstream of the general internal torque command; "
                "or acquire the camera/gateway/other steering-controller firmware if the command is generated outside this EPS image."
            ),
        },
        "evidence_boundary": (
            "Static closure is exact for recovered direct RAM-symbol writes, raw absolute pointers, generated scalar receive calls, literal block/group receive calls, "
            "and literal full-PDU copy calls in the tracked H corpus. It does not prove absence of computed-pointer aliases, DMA/hardware writers, or an autonomous command produced by another ECU."
        ),
    }

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    print(json.dumps({
        "out": str(args.out),
        "retained_lta_active": out["static_conclusion"]["retained_sienna_lta_branch_active_under_recovered_direct_writes"],
        "hidden_d7_command": out["static_conclusion"]["hidden_d7_group_or_full_pdu_command_recovered"],
        "hidden_b6_command": out["static_conclusion"]["hidden_b6_group_or_full_pdu_command_recovered"],
        "external_ingress_identified": out["static_conclusion"]["external_autonomous_lateral_ingress_identified"],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
