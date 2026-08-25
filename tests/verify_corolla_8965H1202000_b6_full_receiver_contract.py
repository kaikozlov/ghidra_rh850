#!/usr/bin/env python3
"""Verify the byte/bit-complete H/F protected-0x0B6 receiver contract."""
from __future__ import annotations

import hashlib
import json
import struct
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
ART = REPO / "data/generated/corolla_8965H1202000_b6_full_receiver_contract.json"
EVID = REPO / "data/generated/corolla_8965H1202000_b6_full_receiver_decompiler_evidence.json"
H = REPO / "community/albinoelephant/normalized/8965H1202000_CodeFlash.bin"
F_RAW = REPO / "community/spanconstant/raw-20260821/span-corolla-2025.20260821-1511/dump_codeflash_00000000_00200000_20260821-152033.bin"
LTA = REPO / "data/generated/corolla_8965H1202000_lta_command_provenance.json"
KEYS = REPO / "data/generated/corolla_8965H1202000_secoc_key_provenance.json"
TOOL = REPO / "tools/build_corolla_h_b6_full_receiver_contract.py"
EXTRACTOR = REPO / "tools/extract_corolla_h_b6_full_receiver_evidence.py"
passed = failed = 0


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def check(name: str, cond: object, detail: str = "") -> None:
    global passed, failed
    ok = bool(cond)
    passed += int(ok)
    failed += int(not ok)
    print(f"[{'PASS' if ok else 'FAIL'}][raw_bytes] {name}" + (f" ({detail})" if detail else ""))


with tempfile.TemporaryDirectory() as td:
    out = Path(td) / "full.json"
    proc = subprocess.run([sys.executable, str(TOOL), "--out", str(out)], cwd=REPO,
                          capture_output=True, text=True, check=False)
    check("full receiver builder exits", proc.returncode == 0,
          (proc.stdout + proc.stderr)[-700:] if proc.returncode else "")
    check("full receiver artifact regenerates exactly",
          proc.returncode == 0 and out.read_bytes() == ART.read_bytes())

art = json.loads(ART.read_text())
ev = json.loads(EVID.read_text())
h = H.read_bytes()
f = F_RAW.read_bytes()[:0x100000]
lta = json.loads(LTA.read_text())
keys = json.loads(KEYS.read_text())
funcs = {int(row["entry"], 16): row for row in ev["functions"]}

print("\n== exact source and H/F binding ==")
check("schema exact", art["schema"] == "corolla-8965H1202000-b6-full-receiver-contract-v1")
check("H image pinned", len(h) == 0x100000 and sha(h) == "0b47bdc1217835c839e3543e52eab40eb793650a9c159e46f6a9b365ea41a67f")
check("15 promoted SecOC/delivery functions", ev["function_count"] == len(funcs) == 15)
check("evidence generator source-bound",
      ev["generator"] == {"path": "tools/extract_corolla_h_b6_full_receiver_evidence.py", "sha256": sha(EXTRACTOR.read_bytes())})
check("whole application corpus source identity pinned",
      ev["source_corpus"]["sha256"] == "5cc79174e8ea917356b9d4758d086df1209c85c9665f122782cff7d88261c387")
check("all promoted functions raw-bound",
      all(sha(h[a:a + row["body_size"]]) == row["body_sha256"] for a, row in funcs.items()))
check("H/F application bytes identical", h[0x20000:0x100000] == f[0x20000:0x100000])
check("H/F contract explicitly shared", art["applies_to"] == ["8965H1202000", "8965F1208000"] and art["cross_variant"]["receiver_contract_byte_identical"] is True)
check("cross-variant boundary retains low-region calibration caveat", "Low-region" in art["cross_variant"]["boundary"])

print("\n== raw B6 SecOC profile ==")
record = h[0x257CC:0x2581C]
check("B6 record raw exact", len(record) == 0x50 and art["wire_envelope"]["profile_record"]["raw_hex"] == record.hex())
check("CMAC width is 128/full and 28/transmitted", struct.unpack_from("<H", record, 0)[0] == 128 and struct.unpack_from("<H", record, 2)[0] == 28)
check("trailer is four bytes", struct.unpack_from("<H", record, 6)[0] == 4)
check("normal profile and Data ID B6 exact", record[9] == 0 and struct.unpack_from("<H", record, 0xA)[0] == 0xB6)
check("freshness profile id2, FV46/FV4 exact", struct.unpack_from("<H", record, 0x12)[0] == 2 and record[0x14] == 46 and record[0x15] == 4)
check("secured lengths all 32", struct.unpack_from("<I", record, 0x24)[0] == struct.unpack_from("<I", record, 0x3C)[0] == struct.unpack_from("<I", record, 0x44)[0] == 32)
check("application and route PDU both 42", struct.unpack_from("<H", record, 0x34)[0] == struct.unpack_from("<H", record, 0x36)[0] == 42)
check("freshness callbacks exact", struct.unpack_from("<I", record, 0x30)[0] == 0x89758 and struct.unpack_from("<I", record, 0x48)[0] == 0x896B0)
check("profile partitions frame 28+4", art["wire_envelope"]["authenticated_application_region"] == {"first_byte": 0, "last_byte": 27, "bytes": 28} and art["wire_envelope"]["security_trailer_region"] == {"first_byte": 28, "last_byte": 31, "bytes": 4})

print("\n== trailer and freshness arithmetic ==")
# Synthetic trailer: high B28 nibble is FV4; remaining 28 wire bits are CMAC_MSB28.
b28, b29, b30, b31 = 0xDA, 0x12, 0x34, 0x56
fv4 = b28 >> 4
cmac28 = ((b28 & 0xF) << 24) | (b29 << 16) | (b30 << 8) | b31
shifted = bytes([((b28 << 4) | (b29 >> 4)) & 0xFF,
                 ((b29 << 4) | (b30 >> 4)) & 0xFF,
                 ((b30 << 4) | (b31 >> 4)) & 0xFF,
                 (b31 << 4) & 0xFF])
check("B28 high nibble is FV4", fv4 == 0xD)
check("B28 low nibble plus B29..31 is CMAC28", cmac28 == 0x0A123456)
check("receiver left-shift reconstructs top-aligned CMAC28", shifted.hex() == "a1234560")
# Independent reference pack for trip16/reset20/message8/reset-low2/00.
trip, reset, message = 0x1234, 0x56789, 0xAB
freshness = struct.pack(">HI", trip, ((reset & 0xFFFFF) << 12) | (message << 4) | ((reset & 3) << 2))
check("full freshness is six bytes", len(freshness) == 6 and freshness.hex() == "123456789ab4")
check("46-bit full freshness leaves low two pad bits zero", freshness[-1] & 3 == 0)
check("transmitted FV4 is message-low2 then reset-low2", ((message & 3) << 2 | (reset & 3)) == 0xD)
check("artifact pins exact full-freshness packing", art["wire_envelope"]["full_freshness"]["packing"] == "trip16 || reset20 || message8 || reset_low2 || 00b")

print("\n== authenticated input and slot selection ==")
auth = art["wire_envelope"]["authenticated_input"]
check("authenticated input is exactly 36 bytes", auth["bytes"] == 36 and auth["application_bytes"] == 28 and auth["freshness_storage_bytes"] == 6)
check("authenticated input exact shape", auth["packing"] == "DataID_be16(0x00B6) || B0..B27 || reconstructed_freshness48" and auth["data_id_bytes"] == "00b6")
check("CMAC compare is MSB28", "MSB28" in auth["algorithm"])
sel = keys["shared_crypto_selection"]
check("B6 selects generated config0/job0/ICU-S slot4", sel["secoc_crypto_config_id"] == 0 and sel["cryptoif_job_handle"] == 0 and sel["icus_slot_selector"] == 4)
check("slot4 key value remains CPU-opaque", art["wire_envelope"]["profile"]["key_value_cpu_visible"] is False and art["static_conclusion"]["receiver_key_value_closed"] is False)

print("\n== verified upper delivery ==")
delivery = art["verified_delivery"]
check("verified route resolves to COM PDU42", delivery["route_id"] == 42 and delivery["resolved_upper_callback"] == "0x00076A3C" and "COM RxIndication" in delivery["upper_callback_role"])
check("delivery chain exact", delivery["queue_ingress"] == "0x0008865A" and delivery["verify_worker"] == "0x00088A56" and delivery["upper_wrapper"] == "0x00088856 -> 0x00089514 -> 0x0007AFB6")
check("no trailer-stripping overclaim", "does not prove" in delivery["length_boundary"] and "application-consumer census" in delivery["length_boundary"])

print("\n== application-consumer closure ==")
app = art["application_consumption"]
check("configured B6 IDs are exactly 252..267", app["configured_signal_ids"] == list(range(252, 268)))
check("scalar B6 IDs are exactly 254..265", app["scalar_extracted_signal_ids"] == list(range(254, 266)))
check("nonscalar configured IDs exact", app["configured_without_scalar_receive"] == [252, 253, 266, 267])
check("semantic scalar IDs exact", app["application_semantic_signal_ids"] == [254, 255, 258, 260, 261, 262, 263, 264, 265])
check("extracted/no-downstream IDs exact", app["extracted_no_recovered_downstream_consumer_signal_ids"] == [256, 257, 259])
escape = app["generic_escape_census"]
check("no B6 nonscalar block/group consumer", escape["non_scalar_ids_used_by_block_group_api"] == [])
check("no B6 full-PDU copy", escape["b6_full_pdu_copy_present"] is False and 42 not in escape["all_literal_full_pdu_ids"])
check("no raw absolute B6 COM-buffer pointer", escape["raw_u32_buffer_pointer_hits"] == [])
direct_region = escape["direct_com_region_reference_census"]
check("no direct named/simple-GP-alias B6 COM-window reference in application corpus",
      direct_region["hit_count"] == 0 and direct_region["direct_hits"] == []
      and direct_region["first_byte"] == "0xFEBE4AF4" and direct_region["last_byte"] == "0xFEBE4B13"
      and direct_region["application_first"] == "0x00020000"
      and direct_region["application_end_exclusive"] == "0x00100000"
      and direct_region["scanned_application_function_count"] == 5138)
check("direct-region negative states its remaining alias boundary",
      "simple GP aliases/constants/copies" in direct_region["boundary"]
      and "computed-base/value-set aliases" in direct_region["boundary"])
check("bounded escape wording preserved", "computed-base aliases" in escape["boundary"] and "hardware/DMA" in escape["boundary"])

print("\n== complete 256-bit partition ==")
counts = app["bit_category_counts"]
check("all 256 wire bits partitioned once", sum(counts.values()) == 256)
check("51 bits have recovered application semantics", counts["application_semantic"] == 51)
check("6 bits extracted but have no recovered downstream consumer", counts["extracted_no_recovered_downstream_consumer"] == 6)
check("167 authenticated app bits have no recovered app consumer", counts["authenticated_application_no_recovered_consumer"] == 167)
check("security trailer partitions 4 FV + 28 MAC bits", counts["secoc_transmitted_freshness"] == 4 and counts["secoc_transmitted_authenticator"] == 28)
byte_map = app["byte_map"]
check("byte map covers B0..B31", [row["byte"] for row in byte_map] == list(range(32)))
check("B0..B2 are authenticated/no-consumer", all(set(byte_map[i]["bit_categories_lsb_to_msb"]) == {"authenticated_application_no_recovered_consumer"} for i in range(3)))
check("B3 includes Target Lateral ID and two no-consumer bits", {f["signal_id"] for f in byte_map[3]["scalar_fields"]} == {254} and byte_map[3]["bit_categories_lsb_to_msb"].count("application_semantic") == 6)
check("B4/B5 are entirely target-angle semantics", all(set(byte_map[i]["bit_categories_lsb_to_msb"]) == {"application_semantic"} for i in (4, 5)))
check("B6 partitions snapshot/gate/staged and one unconsumed bit", byte_map[6]["bit_categories_lsb_to_msb"].count("application_semantic") == 1 and byte_map[6]["bit_categories_lsb_to_msb"].count("extracted_no_recovered_downstream_consumer") == 6 and byte_map[6]["bit_categories_lsb_to_msb"].count("authenticated_application_no_recovered_consumer") == 1)
check("B7/B8/B9 are entirely recovered application semantics", all(set(byte_map[i]["bit_categories_lsb_to_msb"]) == {"application_semantic"} for i in (7, 8, 9)))
check("B10 has four semantic and four no-consumer bits", byte_map[10]["bit_categories_lsb_to_msb"].count("application_semantic") == 4 and byte_map[10]["bit_categories_lsb_to_msb"].count("authenticated_application_no_recovered_consumer") == 4)
check("B11..B27 are authenticated/no-consumer", all(set(byte_map[i]["bit_categories_lsb_to_msb"]) == {"authenticated_application_no_recovered_consumer"} for i in range(11, 28)))
check("B28 splits CMAC/FV nibble", byte_map[28]["bit_categories_lsb_to_msb"] == ["secoc_transmitted_authenticator"] * 4 + ["secoc_transmitted_freshness"] * 4)
check("B29..B31 are all transmitted authenticator", all(set(byte_map[i]["bit_categories_lsb_to_msb"]) == {"secoc_transmitted_authenticator"} for i in range(29, 32)))

print("\n== sender/application boundary ==")
check("receiver semantics explicitly concentrated B3..B10", "B3..B10" in app["receiver_semantic_concentration"])
check("unconsumed application bytes still authenticated", "all B0..B27 are inside the CMAC input" in app["sender_boundary"])
conclusion = art["static_conclusion"]
check("full receiver partition and SecOC envelope closed", conclusion["full_32_byte_receiver_partition_closed"] is True and conclusion["receiver_secoc_envelope_closed"] is True and conclusion["receiver_authenticated_input_closed"] is True)
check("receiver freshness/trailer closed", conclusion["receiver_freshness_layout_closed"] is True and conclusion["receiver_transmitted_trailer_layout_closed"] is True)
check("receiver app generic consumption closed", conclusion["receiver_application_generic_consumption_closed"] is True)
check("sender cadence/ownership still open", conclusion["sender_wall_clock_cadence_closed"] is False and conclusion["sender_freshness_state_ownership_closed"] is False and conclusion["upstream_producer_closed"] is False)
check("evidence boundary rejects sender/key overclaim", "does not recover the ICU-S slot-4 secret value" in art["evidence_boundary"] and "sender cadence" in art["evidence_boundary"])

print(f"\nResults: {passed} passed, {failed} failed")
raise SystemExit(1 if failed else 0)
