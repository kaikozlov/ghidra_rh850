#!/usr/bin/env python3
"""Verify the structural SecOC comparison between Corolla H/F and Sienna."""
from __future__ import annotations

import hashlib
import json
import struct
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
ART = REPO / "data/generated/corolla_h_sienna_secoc_structural_comparison.json"
TOOL = REPO / "tools/build_corolla_h_sienna_secoc_structural_comparison.py"
SIENNA = REPO / "firmware/RH850_P1M-E_CodeFlash.bin"
H = REPO / "community/albinoelephant/normalized/8965H1202000_CodeFlash.bin"
F_RAW = REPO / "community/spanconstant/raw-20260821/span-corolla-2025.20260821-1511/dump_codeflash_00000000_00200000_20260821-152033.bin"
H_EVID = REPO / "data/generated/corolla_8965H1202000_b6_secoc_verification_decompiler_evidence.json"
H_SECOC = REPO / "data/generated/corolla_8965H1202000_b6_secoc_verification.json"
TRANSFER = REPO / "data/generated/corolla_8965H1202000_named_function_transfer_ledger.json"
SIENNA_CORPUS = REPO / "data/generated/decompilations.jsonl"
passed = failed = 0


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def check(name: str, cond: object, detail: str = "") -> None:
    global passed, failed
    ok = bool(cond)
    passed += int(ok)
    failed += int(not ok)
    print(f"[{'PASS' if ok else 'FAIL'}][raw_bytes] {name}" + (f" ({detail})" if detail else ""))


def u16(data: bytes, off: int) -> int:
    return struct.unpack_from("<H", data, off)[0]


def load_sienna_decomp(addresses: set[int]) -> dict[int, str]:
    out: dict[int, str] = {}
    with SIENNA_CORPUS.open() as fh:
        for line in fh:
            row = json.loads(line)
            if row.get("record") != "function":
                continue
            a = int(row["entry_addr"], 16)
            if a in addresses:
                out[a] = row["decompiled_c"]
                if len(out) == len(addresses):
                    break
    return out


with tempfile.TemporaryDirectory() as td:
    out = Path(td) / "comparison.json"
    proc = subprocess.run([sys.executable, str(TOOL), "--out", str(out)], cwd=REPO,
                          capture_output=True, text=True, check=False)
    check("comparison builder exits", proc.returncode == 0,
          (proc.stdout + proc.stderr)[-800:] if proc.returncode else "")
    check("comparison artifact regenerates exactly", proc.returncode == 0 and out.read_bytes() == ART.read_bytes())

art = json.loads(ART.read_text())
h_evid = json.loads(H_EVID.read_text())
h_secoc = json.loads(H_SECOC.read_text())
transfer = json.loads(TRANSFER.read_text())
s = SIENNA.read_bytes()
h = H.read_bytes()
f = F_RAW.read_bytes()[:0x100000]
h_funcs = {row["role"]: row for row in h_evid["functions"]}
transfer_by_ref = {row["reference_entry"].upper(): row for row in transfer["functions"]}
s_decomp = load_sienna_decomp({0x8DB22, 0x8E1A8, 0x8E166, 0x8E382, 0x8E426, 0x8E4BA, 0x8E646,
                                0x8E67A, 0x8E700, 0x8E80A, 0x8E8E6, 0x8E942, 0x8E9FC, 0x8ED0A, 0x8ED88,
                                0x8EE5C, 0x8EECA, 0x8EF9E, 0x8F084, 0x8F0B8, 0x8F112, 0x87ED0, 0x897F4})

print("\n== source binding ==")
check("schema exact", art["schema"] == "corolla-h-sienna-secoc-structural-comparison-v1")
check("Sienna image pinned", len(s) == 0x100000 and sha(s) == art["sources"]["sienna_codeflash"]["sha256"])
check("H image pinned", len(h) == 0x100000 and sha(h) == art["sources"]["corolla_h_codeflash"]["sha256"])
check("H/F application identical", h[0x20000:] == f[0x20000:] and art["applies_to"]["corolla_h_f_application_identical"] is True)
check("all Sienna comparison functions recovered", len(s_decomp) == 23)

print("\n== profile inventory and shared profile classes ==")
sp = art["profile_tables"]["sienna"]["records"]
hp = art["profile_tables"]["corolla_h_f"]["records"]
check("profile record geometry 0x50", art["profile_tables"]["sienna"]["count"] == 6 and art["profile_tables"]["corolla_h_f"]["count"] == 3)
check("Sienna protected inventory exact", [r["data_id"] for r in sp] == ["0x00F", "0x2E4", "0x131", "0x132", "0x090", "0x0D7"])
check("H/F protected inventory exact", [r["data_id"] for r in hp] == ["0x00F", "0x0D7", "0x0B6"])
check("profile DataIDs raw-bound", [u16(s, 0x25970 + i * 0x50 + 0xA) for i in range(6)] == [0xF,0x2E4,0x131,0x132,0x90,0xD7] and [u16(h, 0x2572C + i * 0x50 + 0xA) for i in range(3)] == [0xF,0xD7,0xB6])
check("00F sync profile format identical", art["profile_tables"]["shared_00f"]["format_and_crypto_fields_identical"] is True)
check("00F remains freshness ID0", sp[0]["freshness_id"] == hp[0]["freshness_id"] == 0 and sp[0]["full_freshness_bits"] == hp[0]["full_freshness_bits"] == 36 and sp[0]["transmitted_freshness_bits"] == hp[0]["transmitted_freshness_bits"] == 36)
check("00F CMAC28 and no retries", sp[0]["full_cmac_bits"] == hp[0]["full_cmac_bits"] == 128 and sp[0]["transmitted_cmac_bits"] == hp[0]["transmitted_cmac_bits"] == 28 and sp[0]["authentication_retry_limit"] == hp[0]["authentication_retry_limit"] == 0 and sp[0]["cryptoif_busy_retry_limit"] == hp[0]["cryptoif_busy_retry_limit"] == 0)
sd7 = next(r for r in sp if r["data_id"] == "0x0D7")
hd7 = next(r for r in hp if r["data_id"] == "0x0D7")
hb6 = next(r for r in hp if r["data_id"] == "0x0B6")
check("shared D7 FD profile class identical", art["profile_tables"]["shared_0d7"]["fd_format_crypto_retry_fields_identical"] is True and sd7["secured_pdu_length"] == hd7["secured_pdu_length"] == 32)
check("D7 freshness ID is deliberately not portable", sd7["freshness_id"] == 6 and hd7["freshness_id"] == 1 and art["static_conclusion"]["freshness_ids_portable_across_images"] is False)
check("D7 ordinary slot moves 4 -> 0", art["profile_tables"]["shared_0d7"]["differences"]["ordinary_slot"] == {"sienna": 4, "corolla_h_f": 0})
slot_map = art["profile_tables"]["freshness_id_to_state_slot"]
check("Sienna freshness IDs compact to ordinary slots", slot_map["sienna"] == {"0": "sync", "1": 0, "2": 1, "4": 2, "5": 3, "6": 4} and "sVar8 = sVar8 + 1" in s_decomp[0x8E80A])
check("H/F freshness IDs compact to ordinary slots", slot_map["corolla_h_f"] == {"0": "sync", "1": 0, "2": 1} and "sVar6 = sVar6 + 1" in h_funcs["freshness_profile_lookup"]["decompiled_c"])
check("freshness ID not direct array index", "not the freshness ID used directly as an array index" in slot_map["rule"])
check("B6 instantiates same Sienna FD ordinary class", art["profile_tables"]["b6_as_shared_fd_profile_class"]["matches_sienna_0d7_format_crypto_retry_class"] is True and hb6["secured_pdu_length"] == 32 and hb6["freshness_id"] == 2)
check("ordinary retry class shared", sd7["authentication_retry_limit"] == hd7["authentication_retry_limit"] == hb6["authentication_retry_limit"] == 1 and sd7["cryptoif_busy_retry_limit"] == hd7["cryptoif_busy_retry_limit"] == hb6["cryptoif_busy_retry_limit"] == 2)

print("\n== synchronization manager config ==")
sync_cfg = art["synchronization_manager_config"]
check("32-byte sync-manager config exact relocated", sync_cfg["byte_identical"] is True and s[0x25964:0x25984] == h[0x25720:0x25740])
check("sync-manager wrap threshold exact", sync_cfg["wrap_threshold"] == 15 and sync_cfg["sienna_bytes"] == sync_cfg["corolla_h_f_bytes"])

print("\n== ICU-S selector / command7 ==")
check("slot4 config bytes exact-identical", s[0x25950:0x25964] == h[0x2570C:0x25720] == bytes.fromhex("0100000004000000000000000000000000000000"))
check("config semantics bounded to selector not secret", art["key_and_icus"]["config_semantics"]["icus_slot_selector"] == 4 and art["key_and_icus"]["config_semantics"]["command_word"] == "0x00040007" and "does not prove" in art["key_and_icus"]["slot_secret_transfer_boundary"])
check("Sienna prepare reads config+4", "*(byte *)(param_1 + 1)" in s_decomp[0x87ED0])
check("H prepare reads config+4", "*(byte *)(param_1 + 1)" in h_funcs["icus_command7_descriptor_prepare"]["decompiled_c"])
check("Sienna command7 forms selector<<16|7", "puVar2[4] << 0x10 | 7" in s_decomp[0x897F4])
check("H command7 forms selector<<16|7", "uVar9 << 0x10 | 7" in h_funcs["icus_command7_driver"]["decompiled_c"])
check("lower command7 function geometry retained", transfer_by_ref["0X00087ED0"]["target_entry"] == "0x000822d0" and transfer_by_ref["0X000897F4"]["target_entry"] == "0x00083bf4")

print("\n== exact freshness codec transfers ==")
rows = {row["role"]: row for row in art["function_correspondence"]["rows"]}
expected_exact = {"full_freshness_pack", "sync_freshness_pack", "transmitted_freshness_parse", "sync_freshness_parse"}
check("exact helper set exact", set(art["function_correspondence"]["exact_byte_transfers"]) == expected_exact and art["function_correspondence"]["exact_byte_transfer_count"] == 4)
for role in sorted(expected_exact):
    row = rows[role]
    sa, ha, n = int(row["sienna_entry"], 16), int(row["corolla_h_entry"], 16), row["body_size"]
    check(f"{role} raw bytes identical", s[sa:sa+n] == h[ha:ha+n] and row["byte_identical"] is True)
check("normal full freshness format shared", art["shared_freshness_semantics"]["ordinary_full_freshness"].startswith("46 meaningful bits") and h_secoc["transmitted_freshness"]["full_bits"] == 46)
check("ordinary FV4 split shared", art["shared_freshness_semantics"]["ordinary_transmitted_freshness"].startswith("FV4") and h_secoc["transmitted_freshness"]["wire"] == "B28[7:4]")

print("\n== target-native ordinary freshness algorithm ==")
h_reset = h_funcs["reset_candidate_search"]["decompiled_c"]
s_reset = s_decomp[0x8ED0A]
check("both reset searches have five trial domain", all(t in s_reset and t in h_reset for t in ("0xfffff", "uVar3 == 1", "uVar3 == 2", "uVar3 == 3")))
check("reset candidate order recorded", art["shared_freshness_semantics"]["reset_candidate_order"] == ["current", "current-1", "current+1", "current-2", "current+2"])
h_win = h_funcs["normal_freshness_window_check"]["decompiled_c"]
s_win = s_decomp[0x8ED88]
check("same-epoch message reconstruction shape shared", "1 << uVar6" in h_win and "1 << uVar7" in s_win and "0xff" in h_win and "0xff" in s_win)
check("same-epoch forward semantics recorded", "strictly-forward" in art["shared_freshness_semantics"]["same_epoch_message_rule"] and "1..4" in art["shared_freshness_semantics"]["same_epoch_message_rule"])
h_norm = h_funcs["normal_freshness_reconstruct"]["decompiled_c"]
s_norm = s_decomp[0x8EECA]
check("normal reconstruct cardinality shrinks 5 -> 2", "param_1[1] < 5" in s_norm and "param_1[1] < 2" in h_norm)
check("normal commit cardinality shrinks 5 -> 2", "param_1 < 5" in s_decomp[0x8F084] and "param_1 < 2" in h_funcs["normal_freshness_commit"]["decompiled_c"])

print("\n== 00F synchronization / wrap behavior ==")
check("sync wrap threshold 15 exact in both tables", s[0x2596C] == h[0x25728] == 0x0F)
s_sync = s_decomp[0x8EF9E]
h_sync = h_funcs["sync_freshness_reconstruct"]["decompiled_c"]
check("sync reconstruct has same wrap comparison constants", "0xffff -" in s_sync and "0xffff -" in h_sync and "local_24 != 0" in s_sync and "local_24 != 0" in h_sync)
check("sync reconstruct requires FV36 and zero retry selector", "param_2[1] == 0x24" in s_sync and "param_2[1] == 0x24" in h_sync and "param_3 == 0" in s_sync and "param_3 == 0" in h_sync)
check("authenticated sync commit copies pending -> current", "0xfebe5570" in s_decomp[0x8F112].lower() or "puVar1 + -0x18a4" in s_decomp[0x8F112])
check("H sync commit performs same pending -> current action", "unaff_gp + -0x6354,unaff_gp + -0x634c,8" in h_funcs["sync_freshness_commit"]["decompiled_c"])
check("trip wrap clears linked ordinary windows in both", "uVar3 < 6" in s_decomp[0x8F0B8] and "uVar3 < 3" in h_funcs["trip_wrap_normal_state_clear"]["decompiled_c"])
check("H has additional linked pair outside ordinary array", "unaff_tp + 0x1ab4" in h_funcs["trip_wrap_normal_state_clear"]["decompiled_c"] and art["freshness_state_geometry"]["corolla_h_f"]["extra_linked_pair"]["current"] == "0xFEBE54F8")
check("extra pair is not overnamed", "not assigned" in art["freshness_state_geometry"]["corolla_h_f"]["extra_linked_pair"]["semantic_boundary"])

print("\n== initialization / persistence boundary ==")
init = art["initialization_and_persistence"]
check("Sienna state clear zeros five ordinary arrays", "5x12-byte ordinary current" in init["sienna_state_clear"]["action"] and "0x3c" in s_decomp[0x8E9FC].lower())
check("H/F state clear zeros two ordinary arrays plus extra pair", "2x12-byte ordinary current" in init["corolla_h_f_state_clear"]["action"] and "unaff_gp + -0x6338,0x18" in h_funcs["freshness_state_init"]["decompiled_c"] and "unaff_gp + -0x6308,0xc" in h_funcs["freshness_state_init"]["decompiled_c"])
check("persistence not transferred from Sienna", "does not prove" in init["persistence_boundary"] and "must not be transferred" in init["persistence_boundary"])

print("\n== RAM geometry and generated numbering ==")
geo = art["freshness_state_geometry"]
check("Sienna ordinary state is five 12-byte slots", geo["sienna"]["ordinary_slot_count"] == 5 and geo["sienna"]["ordinary_slot_bytes"] == 12 and geo["sienna"]["ordinary_slot_order"][-1] == "0x0D7")
check("H/F ordinary state is two 12-byte slots", geo["corolla_h_f"]["ordinary_slot_count"] == 2 and geo["corolla_h_f"]["ordinary_slot_bytes"] == 12 and geo["corolla_h_f"]["ordinary_slot_order"] == ["0x0D7", "0x0B6"])
check("B6 slot1 exact addresses retained", geo["corolla_h_f"]["b6_current"] == "0xFEBE54D4" and geo["corolla_h_f"]["b6_pending"] == "0xFEBE54EC")
check("slot numbers explicitly nonportable", art["static_conclusion"]["ram_slot_numbers_portable_across_images"] is False and "must not be transferred by number" in geo["portable_rule"])

print("\n== MAC28 authenticated input / tag assembly ==")
s_builder = s_decomp[0x8DB22]
h_builder = h_funcs["secoc_authenticated_input_build"]["decompiled_c"]
check("both builders prefix big-endian DataID", "param_2[1] = *(undefined1 *)(param_1 + 2)" in s_builder and "param_2[1] = *(undefined1 *)(param_1 + 2)" in h_builder)
check("both builders append payload then freshness", s_builder.count("FUN_00088e3e") == 2 and h_builder.count("FUN_0008323e") == 2)
check("B6 domain is same 36-byte FD class", art["mac28_and_authenticated_input"]["ordinary_fd_authenticated_input_bytes"] == 36 and art["mac28_and_authenticated_input"]["b6_input"] == "00 B6 || B0..B27 || freshness48")
check("both profile tables request AES-CMAC128/MSB28", all(r["full_cmac_bits"] == 128 and r["transmitted_cmac_bits"] == 28 for r in sp + hp))
check("ordinary trailer interpretation bounded", "high nibble=FV4" in art["mac28_and_authenticated_input"]["ordinary_trailer"] and "low nibble" in art["mac28_and_authenticated_input"]["ordinary_trailer"])
check("no extra source ID transferred", "separate source/profile identifier" in art["mac28_and_authenticated_input"]["source_identifier_boundary"] and "Neither implementation adds" in art["mac28_and_authenticated_input"]["source_identifier_boundary"])

print("\n== queue / acceptance reuse and transfer boundary ==")
acc = art["acceptance_and_retry_reuse"]
check("queue state encoding shared", acc["queue_state_bytes"] == {"idle": "E1", "new": "D2", "verify": "C3", "retry": "B4", "freshness_failure": "A5", "generic_failure": "96"} and "-0x2e" in s_decomp[0x8E166] and "-0x3d" in s_decomp[0x8E166] and "-0x4c" in s_decomp[0x8E166] and "-0x6a" in s_decomp[0x8E166])
check("Sienna auth retry uses record +0x10 and B4 re-entry", "DAT_00025980" in s_decomp[0x8E382] and "-0x4c" in s_decomp[0x8E382] and "0x201" in s_decomp[0x8E382])
check("Sienna busy retry uses record +0x2E and B4 re-entry", "DAT_0002599e" in s_decomp[0x8E426] and "-0x4c" in s_decomp[0x8E426])
check("Sienna post-CMAC commits before retry/delivery decision", s_decomp[0x8E67A].find("FUN_0008e646") < s_decomp[0x8E67A].find("if (bVar1)"))
check("Sienna queue dispatch requires verify-worker zero before gate", "secoc_rx_verify_worker" in s_decomp[0x8E700] and "iVar2 == 0" in s_decomp[0x8E700] and "FUN_0008e67a" in s_decomp[0x8E700])
check("seven upper-engine role anchors retained", len(acc["upper_engine_correspondence"]["rows"]) == 7 and all(r["entry_delta"] == "0x5A64" for r in acc["upper_engine_correspondence"]["rows"]))
check("verify worker structural correspondence retained", rows["verify_worker"]["sienna_entry"] == "0x0008E4BA" and rows["verify_worker"]["corolla_h_entry"] == "0x00088A56")
check("post-CMAC gate structural correspondence retained", rows["post_cmac_acceptance"]["sienna_entry"] == "0x0008E67A" and rows["post_cmac_acceptance"]["corolla_h_entry"] == "0x00088C16")
check("ordinary retries structurally shared", art["acceptance_and_retry_reuse"]["ordinary_profile_retry_class"] == {"authentication_candidate_or_mac_mismatch": 1, "cryptoif_submit_busy": 2})
check("commit before delivery shared", "only authenticated success commits freshness before upper-PDU delivery" in art["acceptance_and_retry_reuse"]["shared_queue_model"])
check("safe transfer list includes synchronization arithmetic", any("0x00F" in x for x in art["transferable_sienna_semantics"]["safe_to_transfer_to_h_f_b6"]))
check("target-specific list retains generated IDs/slots", any("freshness ID" in x for x in art["transferable_sienna_semantics"]["must_remain_corolla_target_specific"]))
check("slot4 key material explicitly remains unproved", art["static_conclusion"]["same_slot4_secret_proved"] is False)
check("B6 classified as new PDU on shared class", art["static_conclusion"]["b6_is_new_pdu_on_shared_fd_secoc_class"] is True)
check("evidence boundary rejects sender/key overclaim", "does not infer that the ICU-S slot4 secret is shared" in art["evidence_boundary"] and "does not identify the B6 sender" in art["evidence_boundary"])

print(f"\nResults: {passed} passed, {failed} failed")
raise SystemExit(1 if failed else 0)
