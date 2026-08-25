#!/usr/bin/env python3
"""Build the byte/bit-complete H/F protected-0x0B6 EPS receiver contract."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import struct
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
IMAGE = REPO / "community/albinoelephant/normalized/8965H1202000_CodeFlash.bin"
EVID = REPO / "data/generated/corolla_8965H1202000_b6_full_receiver_decompiler_evidence.json"
BASE = REPO / "data/generated/corolla_8965H1202000_b6_receiver_contract.json"
FD = REPO / "data/generated/corolla_8965H1202000_fd_control_interface.json"
LTA = REPO / "data/generated/corolla_8965H1202000_lta_command_provenance.json"
CENSUS = REPO / "data/generated/corolla_8965H1202000_lta_command_provenance_census.json"
KEYS = REPO / "data/generated/corolla_8965H1202000_secoc_key_provenance.json"
EQUIV = REPO / "data/generated/corolla_8965F1208000_vs_8965H1202000_codeflash_equivalence.json"
OUT = REPO / "data/generated/corolla_8965H1202000_b6_full_receiver_contract.json"

SECOC_RECORD = 0x257CC
SECOC_RECORD_SIZE = 0x50
TP = 0x23D6C
B6_PDU = 42
B6_BUFFER = 0xFEBE4AF4


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def need(text: str, *tokens: str) -> None:
    missing = [token for token in tokens if token not in text]
    if missing:
        raise ValueError("missing decompiler token(s): " + ", ".join(missing))


def bit_mask(lo: int, hi: int) -> list[int]:
    return list(range(lo, hi + 1))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--image", type=Path, default=IMAGE)
    ap.add_argument("--evidence", type=Path, default=EVID)
    ap.add_argument("--out", type=Path, default=OUT)
    args = ap.parse_args()

    image = args.image.read_bytes()
    evidence = json.loads(args.evidence.read_text())
    fd = json.loads(FD.read_text())
    lta = json.loads(LTA.read_text())
    census = json.loads(CENSUS.read_text())
    keys = json.loads(KEYS.read_text())
    equiv = json.loads(EQUIV.read_text())
    if len(image) != 0x100000 or sha(image) != evidence["image"]["sha256"]:
        raise ValueError("H image/evidence identity drift")
    if evidence["function_count"] != 15:
        raise ValueError("full B6 receiver evidence count drift")
    funcs = {int(row["entry"], 16): row["decompiled_c"] for row in evidence["functions"]}

    # Exact 0x50-byte B6 SecOC profile record.
    record = image[SECOC_RECORD:SECOC_RECORD + SECOC_RECORD_SIZE]
    if len(record) != SECOC_RECORD_SIZE:
        raise ValueError("B6 SecOC record truncated")
    full_auth_bits = struct.unpack_from("<H", record, 0x00)[0]
    tx_auth_bits = struct.unpack_from("<H", record, 0x02)[0]
    trailer_bytes_cfg = struct.unpack_from("<H", record, 0x06)[0]
    freshness_kind = record[0x09]
    data_id = struct.unpack_from("<H", record, 0x0A)[0]
    profile_word = struct.unpack_from("<I", record, 0x10)[0]
    freshness_id = struct.unpack_from("<H", record, 0x12)[0]
    full_freshness_bits = record[0x14]
    tx_freshness_bits = record[0x15]
    crypto_handle = struct.unpack_from("<I", record, 0x20)[0]
    secured_len = struct.unpack_from("<I", record, 0x24)[0]
    freshness_commit = struct.unpack_from("<I", record, 0x30)[0]
    application_pdu_id = struct.unpack_from("<H", record, 0x34)[0]
    upper_route_id = struct.unpack_from("<H", record, 0x36)[0]
    secured_len_2 = struct.unpack_from("<I", record, 0x3C)[0]
    secured_len_3 = struct.unpack_from("<I", record, 0x44)[0]
    freshness_get = struct.unpack_from("<I", record, 0x48)[0]
    state_callback = struct.unpack_from("<I", record, 0x4C)[0]
    trailer_bytes = math.ceil((tx_auth_bits + tx_freshness_bits) / 8)
    application_bytes = secured_len - trailer_bytes
    freshness_bytes = math.ceil(full_freshness_bits / 8)
    authenticated_input_bytes = 2 + application_bytes + freshness_bytes
    if not (
        full_auth_bits == 128 and tx_auth_bits == 28 and trailer_bytes_cfg == 4
        and freshness_kind == 0 and data_id == 0x0B6 and profile_word == 0x00020001
        and freshness_id == 2 and full_freshness_bits == 46 and tx_freshness_bits == 4
        and crypto_handle == 0 and secured_len == secured_len_2 == secured_len_3 == 32
        and trailer_bytes == 4 and application_bytes == 28 and freshness_bytes == 6
        and authenticated_input_bytes == 36 and freshness_commit == 0x89758
        and application_pdu_id == upper_route_id == 42 and freshness_get == 0x896B0
        and state_callback == 0x634BA
    ):
        raise ValueError("B6 SecOC profile geometry drift")

    # Receiver-side SecOC mechanics.  0x88744 locates the trailer at
    # received_length - 4 and left-shifts the shared B28..B31 bytes by FV4.
    need(funcs[0x88744],
         "*(ushort *)(param_2 + 1) - *(ushort *)(&LAB_000019c6 + iVar1)",
         "FUN_0008323e(param_3,*param_2 + uVar4,bVar3 + 7 >> 3);",
         "uVar5 = bVar3 & 7;",
         "pcVar2[-1] = pcVar2[-1] | (byte)((int)(uint)bVar3 >> 8 - uVar5);",
         "*pcVar2 = bVar3 << uVar5;")
    need(funcs[0x87FC2],
         "*param_2 = (char)((ushort)*(undefined2 *)(param_1 + 2) >> 8);",
         "param_2[1] = *(undefined1 *)(param_1 + 2);",
         "FUN_0008323e(param_2 + 2,*param_1,*(undefined2 *)((int)param_1 + 10));",
         "FUN_0008323e(param_2 + iVar1,param_1[1],*(undefined2 *)(param_1 + 3));",
         "*param_3 = (uint)*(ushort *)(param_1 + 3) + iVar1;")
    need(funcs[0x89876],
         "if (bVar1 == 0x2e)",
         "param_2[4] = (byte)(*(ushort *)(param_1 + 2) >> 4) | bVar1;",
         "param_2[5] = *(char *)((int)param_1 + 10) << 2 | bVar1;")
    need(funcs[0x89A46],
         "if (param_2 == 4)", "if (param_2 != 0x2e)",
         "*(ushort *)(param_3 + 2) = (ushort)(param_1[5] >> 4) | (param_1[4] & 0xf) << 4;",
         "*(byte *)((int)param_3 + 10) = bVar1 & 3;")
    need(funcs[0x89E9A], "FUN_00089a46", "FUN_00089e2c", "FUN_00089876")
    need(funcs[0x88A56],
         "uStack_24 = *(undefined2 *)(&LAB_000019ca + iVar4);",
         "sStack_22 = uStack_30 - *(short *)(&LAB_000019c6 + iVar4);",
         "puStack_28 = auStack_58;",
         "uStack_20 = (undefined2)(uStack_5c + 7 >> 3);",
         "FUN_00087fc2(&uStack_2c,unaff_gp + -0x63e8);",
         "FUN_00088986")
    need(funcs[0x896B0], "FUN_00089558", "FUN_00089e9a")
    need(funcs[0x89758], "FUN_00089558", "FUN_0008a07a")

    # Verified upper delivery remains a 32-byte COM PDU.  This proves the trailer
    # may remain present in COM RAM; application-consumer closure below, rather
    # than an asserted stripping step, is what makes B28..B31 SecOC-only.
    need(funcs[0x8865A], "uStack_10 = *(ushort *)(param_2 + 1);", "FUN_00087cd6(1,uVar4,&local_14)")
    need(funcs[0x87E2C], "*(ushort *)(param_3 + 1) = uVar1;", "*param_3 = local_30 + iStack_20;")
    need(funcs[0x88856], "FUN_00087e2c(1,(uint)param_1,&local_20);", "uStack_18 = local_20;", "uStack_14 = uStack_1c;", "FUN_00089514")
    need(funcs[0x89514], "FUN_0007afb6(param_1);")

    # Resolve the exact PduR route for upper route 42 from raw generated tables.
    mode = image[TP - 0x209C]
    alt_map = struct.unpack_from("<I", image, TP - 0x2080)[0]
    route_word = struct.unpack_from("<H", image, alt_map + upper_route_id * 4)[0]
    callback_table = struct.unpack_from("<I", image, TP - 0x1EDC)[0]
    callback = struct.unpack_from("<I", image, callback_table + ((route_word >> 11) * 4) + 8)[0]
    if not (mode == 1 and route_word & 0x7FF == 42 and callback == 0x76A3C):
        raise ValueError("B6 upper route no longer resolves to COM RxIndication PDU42")
    need(funcs[0x7AFB6], "uVar3 = uVar1 & 0x7ff;", "(*pcVar4)(uVar3);")

    # Whole-corpus application access closure.
    hidden = lta["b6_hidden_payload_census"]
    com = hidden["com"]
    fields = fd["secured_fd_0x0b6"]["fields"]
    scalar_ids = [field["signal_id"] for field in fields]
    if scalar_ids != list(range(254, 266)):
        raise ValueError("B6 scalar field set drift")
    if com["configured_signal_ids"] != list(range(252, 268)):
        raise ValueError("B6 configured signal set drift")
    if com["configured_without_scalar_receive"] != [252, 253, 266, 267]:
        raise ValueError("B6 nonscalar configured set drift")
    if com["non_scalar_ids_used_by_block_group_api"] or com["b6_full_pdu_copy_present"] or com["raw_u32_buffer_pointer_hits"]:
        raise ValueError("new hidden B6 generic application consumer found")
    if census["scalar_receive_ids"]["b6"] != list(range(254, 266)):
        raise ValueError("whole-corpus scalar census drift")

    # Partition all 256 wire bits into application-semantic, extracted-but-no-
    # downstream-consumer, authenticated-with-no-recovered-application-consumer,
    # and the two SecOC trailer roles.
    categories: list[list[str]] = [["authenticated_application_no_recovered_consumer"] * 8 for _ in range(28)]
    semantic_ids: list[int] = []
    extracted_no_consumer_ids: list[int] = []
    for field in fields:
        sid = field["signal_id"]
        category = "application_semantic" if field["direct_consumers"] else "extracted_no_recovered_downstream_consumer"
        (semantic_ids if field["direct_consumers"] else extracted_no_consumer_ids).append(sid)
        byte = field["wire_byte"]
        for bit in range(field["bit_offset"], field["bit_offset"] + field["bit_length"]):
            b = byte + bit // 8
            local_bit = bit % 8
            if b >= 28 or categories[b][local_bit] != "authenticated_application_no_recovered_consumer":
                raise ValueError(f"overlapping/out-of-range B6 scalar field {sid}")
            categories[b][local_bit] = category
    categories.extend([
        ["secoc_transmitted_authenticator"] * 4 + ["secoc_transmitted_freshness"] * 4,
        ["secoc_transmitted_authenticator"] * 8,
        ["secoc_transmitted_authenticator"] * 8,
        ["secoc_transmitted_authenticator"] * 8,
    ])
    counts: dict[str, int] = {}
    for byte in categories:
        for category in byte:
            counts[category] = counts.get(category, 0) + 1
    if sum(counts.values()) != 256 or counts["secoc_transmitted_freshness"] != 4 or counts["secoc_transmitted_authenticator"] != 28:
        raise ValueError("wire-bit partition drift")
    if extracted_no_consumer_ids != [256, 257, 259]:
        raise ValueError("B6 extracted-no-consumer set drift")

    byte_map = []
    field_by_byte: dict[int, list[dict]] = {}
    for field in fields:
        for b in range(field["wire_byte"], field["wire_byte"] + math.ceil((field["bit_offset"] + field["bit_length"]) / 8)):
            if b <= 10:
                field_by_byte.setdefault(b, []).append({
                    "signal_id": field["signal_id"],
                    "role": field["role"],
                    "bit_length": field["bit_length"],
                    "bit_offset": field["bit_offset"] if b == field["wire_byte"] else 0,
                    "direct_consumers": field["direct_consumers"],
                })
    for index, bit_categories in enumerate(categories):
        if index < 28:
            role = "authenticated_application_data"
        else:
            role = "secoc_security_trailer"
        byte_map.append({
            "byte": index,
            "role": role,
            "bit_categories_lsb_to_msb": bit_categories,
            "scalar_fields": field_by_byte.get(index, []),
        })

    # H/F application and all receiver tables/functions used here are inside the
    # byte-identical 0x20000..0xFFFFF region.
    app_eq = equiv["application_equivalence"]
    relevant_addresses = [SECOC_RECORD, 0x22770, 0x46A10, *funcs.keys()]
    if not (app_eq["identical"] is True and app_eq["different_bytes"] == 0 and app_eq["start"] == "0x20000" and app_eq["end_exclusive"] == "0x100000"):
        raise ValueError("H/F application identity drift")
    if not all(0x20000 <= address < 0x100000 for address in relevant_addresses):
        raise ValueError("receiver proof uses address outside H/F identical application region")

    key_sel = keys["shared_crypto_selection"]
    if not (key_sel["secoc_crypto_config_id"] == 0 and key_sel["cryptoif_job_handle"] == 0 and key_sel["icus_slot_selector"] == 4 and key_sel["config_type"] == 1):
        raise ValueError("H slot-4 key selection drift")

    out = {
        "schema": "corolla-8965H1202000-b6-full-receiver-contract-v1",
        "software_id": "8965H1202000",
        "applies_to": ["8965H1202000", "8965F1208000"],
        "sources": {
            "codeflash": {"path": str(args.image.relative_to(REPO)), "sha256": sha(image)},
            "decompiler_evidence": {"path": str(args.evidence.relative_to(REPO)), "sha256": sha(args.evidence.read_bytes()), "function_count": evidence["function_count"]},
            "base_receiver_contract": {"path": str(BASE.relative_to(REPO)), "sha256": sha(BASE.read_bytes())},
            "fd_control_interface": {"path": str(FD.relative_to(REPO)), "sha256": sha(FD.read_bytes())},
            "lta_provenance": {"path": str(LTA.relative_to(REPO)), "sha256": sha(LTA.read_bytes())},
            "whole_corpus_census": {"path": str(CENSUS.relative_to(REPO)), "sha256": sha(CENSUS.read_bytes())},
            "secoc_key_provenance": {"path": str(KEYS.relative_to(REPO)), "sha256": sha(KEYS.read_bytes())},
            "hf_equivalence": {"path": str(EQUIV.relative_to(REPO)), "sha256": sha(EQUIV.read_bytes())},
        },
        "wire_envelope": {
            "can_id": "0x0B6",
            "pdu_id": 42,
            "secured_bytes": 32,
            "authenticated_application_region": {"first_byte": 0, "last_byte": 27, "bytes": 28},
            "security_trailer_region": {"first_byte": 28, "last_byte": 31, "bytes": 4},
            "profile_record": {"address": f"0x{SECOC_RECORD:08X}", "raw_hex": record.hex()},
            "profile": {
                "full_authenticator_bits": full_auth_bits,
                "transmitted_authenticator_bits": tx_auth_bits,
                "full_freshness_bits": full_freshness_bits,
                "transmitted_freshness_bits": tx_freshness_bits,
                "freshness_id": freshness_id,
                "freshness_kind": "normal",
                "cryptoif_job_handle": crypto_handle,
                "secoc_crypto_config_id": key_sel["secoc_crypto_config_id"],
                "icus_slot_selector": key_sel["icus_slot_selector"],
                "key_value_cpu_visible": keys["static_storage_derivation_conclusion"]["cpu_visible_raw_slot4_key"],
            },
            "trailer_bits": {
                "B28[7:4]": "transmitted freshness FV4 = message_counter_low2 || reset_counter_low2",
                "B28[3:0]": "CMAC_MSB28 bits27:24",
                "B29": "CMAC_MSB28 bits23:16",
                "B30": "CMAC_MSB28 bits15:8",
                "B31": "CMAC_MSB28 bits7:0",
            },
            "full_freshness": {
                "meaningful_bits": 46,
                "storage_bytes": 6,
                "packing": "trip16 || reset20 || message8 || reset_low2 || 00b",
                "transmitted_nibble": "message_low2 || reset_low2",
                "packer": "0x00089876",
                "parser": "0x00089A46",
                "normal_reconstruction": "0x00089E2C/0x00089E9A",
            },
            "authenticated_input": {
                "bytes": authenticated_input_bytes,
                "packing": "DataID_be16(0x00B6) || B0..B27 || reconstructed_freshness48",
                "data_id_bytes": "00b6",
                "application_bytes": 28,
                "freshness_storage_bytes": 6,
                "builder": "0x00087FC2",
                "algorithm": "AES-CMAC-128 via ICU-S slot 4; receiver compares transmitted MSB28",
            },
        },
        "verified_delivery": {
            "queue_ingress": "0x0008865A",
            "verify_worker": "0x00088A56",
            "queue_getter": "0x00087E2C",
            "upper_wrapper": "0x00088856 -> 0x00089514 -> 0x0007AFB6",
            "route_id": upper_route_id,
            "resolved_upper_callback": f"0x{callback:08X}",
            "upper_callback_role": "COM RxIndication for PDU42",
            "length_boundary": (
                "The recovered queue/delivery path preserves a PduInfo length and PDU42's COM descriptor is 32 bytes. "
                "Static evidence does not prove that B28..B31 are physically stripped before COM RAM; the application-consumer census, not a stripping assumption, is the basis for classifying them as SecOC-only."
            ),
        },
        "application_consumption": {
            "com_buffer": f"0x{B6_BUFFER:08X}",
            "configured_signal_ids": com["configured_signal_ids"],
            "scalar_extracted_signal_ids": scalar_ids,
            "configured_without_scalar_receive": com["configured_without_scalar_receive"],
            "application_semantic_signal_ids": semantic_ids,
            "extracted_no_recovered_downstream_consumer_signal_ids": extracted_no_consumer_ids,
            "generic_escape_census": {
                "non_scalar_ids_used_by_block_group_api": com["non_scalar_ids_used_by_block_group_api"],
                "b6_full_pdu_copy_present": com["b6_full_pdu_copy_present"],
                "raw_u32_buffer_pointer_hits": com["raw_u32_buffer_pointer_hits"],
                "direct_com_region_reference_census": evidence["direct_b6_com_region_reference_census"],
                "all_literal_block_group_receive_ids": com["all_literal_block_group_receive_ids"],
                "all_literal_full_pdu_ids": com["all_literal_full_pdu_ids"],
                "boundary": "Closes generated scalar plus all literal block/group/full-PDU APIs, direct raw-u32 buffer pointers, and the complete application-corpus named/absolute/simple-GP-alias constant-displacement census; arbitrary value-set/computed-base aliases and hardware/DMA accesses remain outside the proof."
            },
            "bit_category_counts": counts,
            "byte_map": byte_map,
            "receiver_semantic_concentration": (
                "Recovered EPS application semantics are confined to selected bits in B3..B10. B0..B2 and B11..B27 are authenticated but have no recovered application consumer under the bounded generic-access census."
            ),
            "sender_boundary": (
                "No recovered EPS application semantic consumer means these bytes impose no recovered receiver-application meaning, not that a sender may choose them freely: all B0..B27 are inside the CMAC input, and upstream producer-side formatting constraints remain unexamined."
            ),
        },
        "cross_variant": {
            "h_f_application_identical": True,
            "identical_range": [app_eq["start"], app_eq["end_exclusive"]],
            "different_bytes_in_range": app_eq["different_bytes"],
            "range_sha256": app_eq["baseline_sha256"],
            "receiver_contract_byte_identical": True,
            "boundary": "All receiver tables and functions used by this proof lie inside the byte-identical application range. Low-region H/F calibration/identity differences are outside this proof and can still affect downstream limits/calibration."
        },
        "static_conclusion": {
            "full_32_byte_receiver_partition_closed": True,
            "receiver_secoc_envelope_closed": True,
            "receiver_freshness_layout_closed": True,
            "receiver_transmitted_trailer_layout_closed": True,
            "receiver_authenticated_input_closed": True,
            "receiver_application_generic_consumption_closed": True,
            "receiver_key_slot_selection_closed": True,
            "receiver_key_value_closed": False,
            "secondary_oem_field_names_closed": False,
            "sender_wall_clock_cadence_closed": False,
            "sender_freshness_state_ownership_closed": False,
            "upstream_producer_closed": False,
            "short_form": "EPS semantics are concentrated in B3..B10; B0..B27 are all authenticated; B28..B31 are FV4+CMAC28 SecOC trailer."
        },
        "evidence_boundary": (
            "This closes the exact H/F receiver-side 32-byte partition, normal-freshness/trailer format, CMAC input, slot selection, verified upper route, and bounded application-consumer surface. It does not recover the ICU-S slot-4 secret value, sender cadence, sender freshness-state ownership, upstream producer formatting, arbitrary hardware/DMA aliases, or OEM names for every secondary B6 scalar."
        ),
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"out": str(args.out), "bit_counts": counts, "callback": hex(callback)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
