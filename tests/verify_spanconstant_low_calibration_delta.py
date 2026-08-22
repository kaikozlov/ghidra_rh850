#!/usr/bin/env python3
"""Verify the exhausted Span-vs-albino low-CodeFlash calibration/identity delta."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import struct
import zlib
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
BASELINE = REPO / "community/albinoelephant/raw-20260818/albinoelephant-corolla-2023.20260814-0023/dump_codeflash_00000000_00200000_20260814-025814.bin"
TARGET = REPO / "community/spanconstant/raw-20260821/span-corolla-2025.20260821-1511/dump_codeflash_00000000_00200000_20260821-152033.bin"
ARTIFACT = REPO / "data/generated/corolla_8965F1208000_low_calibration_delta.json"
TOOL = REPO / "tools/analyze_spanconstant_low_calibration_delta.py"


def check(label: str, ok: bool) -> None:
    if not ok:
        raise AssertionError(label)
    print(f"[ok] {label}")


def sha256(blob: bytes) -> str:
    return hashlib.sha256(blob).hexdigest()


spec = importlib.util.spec_from_file_location("span_low_delta", TOOL)
assert spec is not None and spec.loader is not None
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

tracked = json.loads(ARTIFACT.read_text(encoding="utf-8"))
fresh = mod.build_report(BASELINE, TARGET)
check("tracked low-delta report regenerates exactly from both raw CodeFlash images", tracked == fresh)

h = BASELINE.read_bytes()[:0x100000]
s = TARGET.read_bytes()[:0x100000]
changed = {i for i, (a, b) in enumerate(zip(h, s)) if a != b}
summary = tracked["summary"]
check("exactly 2190 CodeFlash bytes differ", len(changed) == summary["different_codeflash_bytes"] == 2190)
check("low delta remains bounded to 0xA004..0x17DFF", min(changed) == 0xA004 and max(changed) == 0x17DFF)
check("application 0x20000..0xFFFFF remains byte-identical", h[0x20000:] == s[0x20000:] and summary["application_different_bytes"] == 0)
check("delta partitions exactly into A000 records, low shadow source, and post-CRC tag", summary["delta_partition_complete"] and (summary["a000_record_bank_changed_bytes"], summary["low_shadow_source_changed_bytes"], summary["post_crc_opaque_tag_changed_bytes"]) == (863, 1311, 16) and 863 + 1311 + 16 == 2190)

# Count width is intentionally pinned as u16.  Reading a u32 here would merge the
# adjacent 0x0012 field and manufacture the bogus value 0x00120009.
family = tracked["a000_record_family"]
check("A000 family count is the u16 9 at 0x2A974", struct.unpack_from("<H", h, 0x2A974)[0] == 9 and struct.unpack_from("<H", s, 0x2A974)[0] == 9 and family["record_count_source"] == {"va": "0x2A974", "width_bits": 16, "baseline": 9, "target": 9})
check("adjacent metadata proves the count must not be read as u32", struct.unpack_from("<I", h, 0x2A974)[0] == 0x00120009)

expected_desc = [
    (0x28, 0xFEBEF600, 0xA000),
    (0x08, 0xFEBEF630, 0xA030),
    (0x40, 0xFEBEF640, 0xA040),
    (0x10, 0xFEBEF688, 0xA088),
    (0x10, 0xFEBEF6A0, 0xA0A0),
    (0x308, 0xFEBEF6B8, 0xA0B8),
    (0x108, 0xFEBEF9C8, 0xA3C8),
    (0x28, 0xFEBEFAD8, 0xA4D8),
    (0x18, 0xFEBEFB08, 0xA508),
]
actual_desc = [struct.unpack_from("<HHII", h, 0x2AB8C + i * 12) for i in range(9)]
check("all nine 12-byte A000 descriptors use u16 length + zero pad + two pointers", actual_desc == [(ln, 0, ram, src) for ln, ram, src in expected_desc] and h[0x2AB8C:0x2ABF8] == s[0x2AB8C:0x2ABF8])
check("artifact pins 16-bit descriptor lengths rather than relying on zero-extended u32 coincidence", all(r["length_width_bits"] == 16 and r["padding_u16"] == 0 for r in family["records"]))

records = family["records"]
check("A000 payload changed-byte census is exact", [r["payload_changed_bytes"] for r in records] == [26, 0, 37, 6, 0, 758, 0, 9, 3])
check("record-0 staged consumption chain is explicitly retained", records[0]["evidence_chain"] == ["0x6009E(0x200)->0x604AA", "0x2DF98->FEBE679E..FEBE67C0", "0x2DE9A->FEBE6776..FEBE6798", "0x43528"])
check("record-2 staged consumption/update chain is explicitly retained", records[2]["evidence_chain"] == ["0x6009E(0x202)->0x604AA", "0x2FB36->FEBE68F4..FEBE6928", "0x2F40A->0x2F318", "0x2F318->FEBE6896..FEBE68CA", "0x2FC22", "0x2EDE6/0x30008->0x60010(0x202) runtime-copy path"])
check("record-3 staged-to-live selector chain is explicitly retained", records[3]["evidence_chain"] == ["0x6009E(0x203)->0x604AA", "0x2DAA8->FEBE671A/1C/1E", "0x2DA0A->FEBE6712/14/16", "0x42700", "0x42720"])
for idx, (length, _ram, source) in enumerate(expected_desc):
    residue_h = zlib.crc32(h[source:source + length + 4]) & 0xFFFFFFFF
    residue_s = zlib.crc32(s[source:source + length + 4]) & 0xFFFFFFFF
    if idx == 1:
        check("record 1 is the sole zero-fixup CRC exception", struct.unpack_from("<I", h, source + length)[0] == 0 and struct.unpack_from("<I", s, source + length)[0] == 0 and residue_h == residue_s == 0x7BD5C66F)
    else:
        check(f"record {idx} payload+fixup has 0xFFFFFFFF zlib residue in both images", residue_h == residue_s == 0xFFFFFFFF)

# Record 5 is exactly header[8] + three signed-byte 256-entry LUTs.
luts = tracked["motor_rotation_angle_luts"]
check("record-5 three-mode LUT geometry is exact", [(x["start"], x["end_exclusive"]) for x in luts] == [("0xA0C0", "0xA1C0"), ("0xA1C0", "0xA2C0"), ("0xA2C0", "0xA3C0")])
check("record-5 LUT changed-byte counts are exact", [x["changed_bytes"] for x in luts] == [254, 253, 251])
check("record-5 LUT deltas are numerically pinned", [(x["baseline_min"], x["baseline_max"], x["target_min"], x["target_max"], x["max_absolute_delta"]) for x in luts] == [(-32, 30, -27, 26, 34), (-38, 38, -23, 22, 36), (-30, 30, -27, 26, 37)])

# Record 6 is an active-addressed but all-zero sibling table in both specimens.
check("record-6 payload+8 table is exactly 256 zero bytes in both images", h[0xA3D0:0xA4D0] == s[0xA3D0:0xA4D0] == bytes(0x100))
check("record-6 role remains explicitly zero-filled rather than inferred tuned", records[6]["role"] == "zero_filled_angle_correction_lut" and records[6]["classification"] == "active-addressed-null-record" and records[6]["payload_changed_bytes"] == 0 and records[6]["payload_all_zero_baseline"] and records[6]["payload_all_zero_target"] and not records[6]["a55a5aa5_marker_present_baseline"] and not records[6]["a55a5aa5_marker_present_target"])

coeff = tracked["record3_coefficients"]
check("record-3 selected angle-offset coefficients are exact", coeff["baseline"] == [244, 0, 270] and coeff["target"] == [-786, -795, -723])
check("record-4 payload is marker + Toyota part number 89650-12N50, identical in both specimens", h[0xA0A0:0xA0B0] == s[0xA0A0:0xA0B0] and struct.unpack_from("<I", h, 0xA0A0)[0] == 0xA55A5AA5 and h[0xA0A4:0xA0AE] == b"8965012N50" and records[4]["role"] == "ecu_part_number_record" and records[4]["classification"] == "identity")
SIENNA = (REPO / "firmware/RH850_P1M-E_CodeFlash.bin").read_bytes()
check("Sienna same-shaped record 4 carries its own part number 89650-45170", struct.unpack_from("<I", SIENNA, 0xA0A0)[0] == 0xA55A5AA5 and SIENNA[0xA0A4:0xA0AE] == b"8965045170")
check("record-4 part-number classification remains evidence-bounded (no recovered firmware reader)", "No target-native firmware consumer" in records[4]["boundary"] and "ECU Part Number" in records[4]["boundary"])
check("serial identity changes are exact", records[7]["baseline_serial"] == "8965012N50A05G310920" and records[7]["target_serial"] == "8965012N50E12H030731")
check("Span target label is explicitly tied to observed/application F181, not the separate 0x17D80 identity", tracked["target_id"] == "8965F1208000" and "0x20860" in tracked["target_id_basis"] and "8965H1213000" in tracked["target_id_basis"])

bank_b = tracked["low_shadow_bank"]["structured_bank_b"]
check("structured bank-B has 18 correctly aligned 0x24-byte rows with exact per-row delta census", bank_b["start"] == "0x120F4" and bank_b["end_exclusive"] == "0x1237C" and bank_b["record_stride"] == 0x24 and bank_b["record_count"] == 18 and [r["changed_bytes"] for r in bank_b["records"]] == [0,0,8,8,8,8,12,12,12,12,12,12,12,12,8,8,8,8])
check("every structured-bank-B row terminates in 0x7FFFFFFF in both images", all(struct.unpack_from("<I", h, int(r["start"], 16) + 0x20)[0] == 0x7FFFFFFF and struct.unpack_from("<I", s, int(r["start"], 16) + 0x20)[0] == 0x7FFFFFFF for r in bank_b["records"]))

# Pin exact bodies for the role-critical target-native H functions.  Span carries
# the same bytes; semantic names remain bounded to the reviewed decompilation.
critical_bodies = {
    0x20880: (12, "b9a074cdc45397ba3280936e41004cc89349741987c0dc30b0ff1096c4cdcea8"),
    0x2DA0A: (30, "3abb7917543506aa512f3305aa43db8352e72b0b9344998085bf4a83b308312f"),
    0x2DAA8: (76, "8267b219728798c75e114016dc6e14d3462d6bcbc86a224402748b8f1ac0ca49"),
    0x2DE9A: (114, "4048d75cff367588d216df84a12ff7527c03cf51d86493a29cfc783d06024a46"),
    0x2DF98: (158, "4b582527ee25091758f3a2740d69bc498b938b55e63d456d6d26fc9a5a58e38e"),
    0x2F318: (174, "5fd2df992c7c8a0c0977ff75dd04cd765cf5a5c6db6587d6438d63487592f266"),
    0x2F40A: (84, "52068a58965879d675dc8cbdb777fc6df0c49f5882046ea135b8943631b05756"),
    0x2FB36: (236, "7784fea0dbbd56eb0a9b57a8ce536c08d776152bd6542d4836d9859a212b4b0e"),
    0x2FC22: (358, "8a5777067e1b3db7bdbef8d6f6a991c876fbdff0cd794f75907608f65d5e7275"),
    0x42700: (32, "c2de75d0be21e7679428ca2e12db63f07b64ccb9e3ec5f7f30c12869762d425a"),
    0x42720: (462, "e5e7934e934c33a069d9b87e2dd1710d0a010e179dd1b18599960b5248ef285e"),
    0x42B98: (86, "3c18e76bb4c15652771bf8f0f888b136b13b4873ada71f12294760311df56254"),
    0x42C42: (208, "7f46bd2257f3af0d2c6ec537688c5394cf1c15a5fde5e0a4eecaba0fd378051b"),
    0x42D28: (184, "17edb8a5c2acfd47373e0722fd457771918a03810d30275909a45eff5f1ab1e0"),
    0x43528: (1632, "95a65b941a1927412d8b195cd599fc2402e3d907e7c620496e1bb0d570a13c7c"),
    0x50E6A: (8, "069adea92809ff18277718f63f617d18eaf4bd41b8bbd4d2f402609c33670a16"),
    0x5CAAC: (98, "783e8a3519e75cacffae2489a5e42e1a69cf05a989d2aeb3a3af3352f591dbf9"),
    0x6009E: (50, "d49d1c703a5a3ec6b15beeefc357d73578ba4e7f19e447e486409f7c31a7b512"),
    0x604AA: (110, "bfea50e9d2a853b368efe551ffa784ff48b45c7891115ceb09a053ddfc9861e8"),
}
for addr, (size, expected_sha) in critical_bodies.items():
    hb = h[addr:addr + size]
    sb = s[addr:addr + size]
    check(f"role-critical body 0x{addr:08X} is pinned and byte-identical", hb == sb and sha256(hb) == expected_sha)

shadow = tracked["low_shadow_bank"]
check("startup and XCP-E4 shadow-copy bodies are exact twins", sha256(h[0x5C992:0x5C992 + 36]) == sha256(h[0x92700:0x92700 + 36]) == "969ee65ec1d2a2523c1bd97a317de7923bc05a7e5ca3785760e5cb78296dc8b2")
check("shadow-copy geometry remains 0x10000..0x17DF0 -> FEBF7C00", shadow["source_start"] == "0x10000" and shadow["source_end_exclusive"] == "0x17DF0" and shadow["destination_start"] == "0xFEBF7C00" and shadow["length"] == 0x7DF0)
check("startup copy is pinned to application-entry initialization chain", shadow["startup_call_chain"] == ["0x00020880", "0x0005CAAC", "0x0005C992"])

ident = tracked["identity_and_integrity_tail"]
check("low shadow region terminal fixups and 0xFFFFFFFF CRC32 residues are exact", struct.unpack_from("<I", h, 0x17DEC)[0] == 0x722611BD and struct.unpack_from("<I", s, 0x17DEC)[0] == 0x01A011A0 and zlib.crc32(h[0x10000:0x17DF0]) & 0xFFFFFFFF == zlib.crc32(s[0x10000:0x17DF0]) & 0xFFFFFFFF == 0xFFFFFFFF and ident["low_region_crc32_residue_baseline"] == ident["low_region_crc32_residue_target"] == "0xFFFFFFFF")

# The 16 bytes at 0x17DF0..0x17DFF are the region-0 AES-CMAC tag, verified by the
# boot integrity chain, not an opaque/unresolved field.
regions = tracked["boot_integrity_regions"]
check("boot integrity region table is pinned at 0x8DE0 with three identical rows", regions["region_table_va"] == "0x8DE0" and regions["row_count"] == 3 and regions["row_stride"] == 28 and h[0x8DE0:0x8DE0 + 3*28] == s[0x8DE0:0x8DE0 + 3*28] and regions["table_identical_between_variants"])
expected_rows = [
    ("0x10000", "0x17DFF", "0x17DF0", "0x17E00", "0x8DB0"),
    ("0x18000", "0xFFDFF", "0xFFDF0", "0xFFE00", "0x8DC0"),
    ("0xFEBF0000", "0xFEBF0FFF", "0xFEBF0FF0", "0x0", "0x8DD0"),
]
actual_rows = [(r["start"], r["end_inclusive"], r["cmac_tag_address"], r["marker_address"], r["crc_descriptor_table"]) for r in regions["rows"]]
check("integrity region rows carry exact start/end/tag/marker/descriptor tuples", actual_rows == expected_rows)
check("each region tag address is exactly the final 16 bytes of its region", all(r["tag_is_final_16_bytes_of_region"] for r in regions["rows"]))
check("region-0 and region-1 validity markers are 0x5AA5A55A in both images", all(r["marker_value_baseline"] == r["marker_value_target"] == "0x5AA5A55A" for r in regions["rows"][:2]))
cmac_chain_entries = {c["entry"].split("/")[0] for c in regions["cmac_verify_chain"]}
check("CMAC verify chain pins all named boot functions", cmac_chain_entries == {"0x00005BEA", "0x0000591A", "0x00006E9E", "0x00007106", "0x00003376", "0x00006EC4", "0x00007DF0", "0x00007336", "0x00007D34"})
check("region-0 AES-CMAC tag is fully changed (16/16) and recorded", regions["region0_cmac_tag_baseline"] == h[0x17DF0:0x17E00].hex() and regions["region0_cmac_tag_target"] == s[0x17DF0:0x17E00].hex() and sum(a != b for a, b in zip(h[0x17DF0:0x17E00], s[0x17DF0:0x17E00])) == 16)
check("0x17DF0 tag semantics are promoted from unresolved to AES-CMAC", tracked["identity_and_integrity_tail"]["opaque_tag_algorithm"] == "superseded-by-boot-integrity-region-0-aes-cmac-tag")
check("high-region tag slot at 0xFFDF0 is identical between specimens and not asserted programmed", h[0xFFDF0:0xFFE00] == s[0xFFDF0:0xFFE00])
# Role-critical CMAC chain bodies are byte-identical between H and Span.
cmac_bodies = {
    0x3376: (58, "273d630364ce881bf6f650f608ac8fb827976f8295e008d8688d1201070558eb", "boot_memory_region_get_cmac_tag"),
    0x33B0: (54, "6810ac24f3352e2c76c849533f1c8b0257e2c2a2a4253f07b8554f8c3bad0f08", "boot_memory_region_get_marker_address"),
    0x6E9E: (38, "a0baa6aad16f29ea7db82777a045644c47e98a36613eb7d43645ba4ed27535ce", "payload_cmac_verify_enqueue"),
    0x6EC4: (36, "8290e60e9b154a0176f2c810dd82ffcf449b510c8448833dd31dd75ce932b135", "cmac_block_pump_driver"),
    0x7106: (78, "5b3bb8aed8ad88461607d99ad93d0aab9d98af2e7917b955a83724a71c0523e1", "payload_cmac_verify_setup"),
    0x7154: (126, "71e860cb6ed0162187da9999684b10b4492ed27d3b34f5da3a85a1146a87bc58", "payload_cmac_verify_step"),
    0x7336: (148, "cc4aef610ab09029bfe3490300a4aaa348e4450c9644caa4b32f6ea766217261", "aes_block_encrypt_core"),
    0x7DF0: (424, "6b6c6949b1182832ff07ab16ce67234f31ace090797160a68068b626e5327017", "aes_cmac_process_block"),
}
for addr, (size, expected_sha, name) in cmac_bodies.items():
    hb = h[addr:addr + size]
    sb = s[addr:addr + size]
    check(f"CMAC chain body {name} 0x{addr:08X} is pinned and byte-identical", hb == sb and sha256(hb) == expected_sha)

check("0x17E00 validity marker itself is unchanged", h[0x17E00:0x17E04] == s[0x17E00:0x17E04] == bytes.fromhex("5aa5a55a"))
check("shadow geometry exactly explains the two retained identity mirrors", ident["shadow_identity_mirrors"] == {"0x17D80_to_ram": "0xFEBFF980", "0x17DC0_to_ram": "0xFEBFF9C0"})
check("isolated scalar byte change at 0x13E46 is pinned without inventing record framing", struct.unpack_from("<H", h, 0x13E46)[0] == 0x0929 and struct.unpack_from("<H", s, 0x13E46)[0] == 0x0989)

interp = tracked["interpretation"]
check("artifact refuses to promote specimen differences to a model-year tuning claim", interp["unit_specific_motor_calibration_differs"] and not interp["model_year_tuning_change_proven"])
check("artifact preserves the unresolved 0x10000+ CPU-consumer boundary", "no recovered application CPU semantic dereference" in shadow["cpu_consumer_boundary"] and "not disproved" in shadow["cpu_consumer_boundary"])

# ---- second-slice closures ----
# Runtime shadow liveness across every retained snapshot.
live = shadow["runtime_shadow_liveness"]["captures"]
check("all five runtime snapshots hold the shadow byte-identical to their own CodeFlash low page", len(live) == 5 and all(c["diffs_vs_own_codeflash"] == 0 for c in live) and {c["capture"] for c in live} == {"albino-PE1-002502", "albino-PE1-004452", "albino-PE1-005055", "span-PE1-151834", "span-self-152418"})
# Independent re-derivation from the raw captures.
for cap, rel, base, img in (
    ("albino-PE1-002502", "community/albinoelephant/raw-20260818/albinoelephant-corolla-2023.20260814-0023/dump_local_ram_pe1_febe0000_fec00000_20260814-002502.bin", 0xFEBE0000, h),
    ("albino-PE1-004452", "community/albinoelephant/raw-20260818/albinoelephant-corolla-2023.20260814-0023/dump_local_ram_pe1_febe0000_fec00000_20260814-004452.bin", 0xFEBE0000, h),
    ("albino-PE1-005055", "community/albinoelephant/raw-20260818/albinoelephant-corolla-2023.20260814-0023/dump_local_ram_pe1_febe0000_fec00000_20260814-005055.bin", 0xFEBE0000, h),
    ("span-PE1-151834", "community/spanconstant/raw-20260821/span-corolla-2025.20260821-1511/dump_local_ram_pe1_febe0000_fec00000_20260821-151834.bin", 0xFEBE0000, s),
    ("span-self-152418", "community/spanconstant/raw-20260821/span-corolla-2025.20260821-1511/dump_local_ram_self_fede0000_fee00000_20260821-152418.bin", 0xFEDE0000, s),
):
    ram = (REPO / rel).read_bytes()
    shadow_va = 0xFEBF7C00 if base == 0xFEBE0000 else base + 0x17C00
    sh = ram[shadow_va - base:shadow_va - base + 0x7DF0]
    check(f"{cap}: RAM shadow equals same-image CodeFlash 0x10000..0x17DEF", sh == img[0x10000:0x10000 + 0x7DF0])

# High-template boundary.
ht = shadow["high_template_boundary"]
check("high 0x18000..0x1FDEF is identical between specimens and ~84.9% homologous to the low page", ht["identical_between_variants"] and h[0x18000:0x1FDF0] == s[0x18000:0x1FDF0] and ht["byte_homology_fraction_with_low_page"] == 0.8488)
check("high template is neither specimen's calibration at the changed offsets", ht["at_changed_low_offsets"] == {"high_equals_baseline": 60, "high_equals_target": 11, "third_value": 1240})
check("high template carries no marker/tag structure and the checked XCP config area is zero", ht["no_marker_at_0x1FE00"] and struct.unpack_from("<I", h, 0x1FE00)[0] != 0x5AA5A55A and ht["xcp_config_area_0x261F0_all_zero"] and not any(h[0x261F0:0x26230]))

# Bank-A exact structural partition (33x0x44 + 4x0x24 + interstitial + 32x0x28 + tail = 1143).
part = shadow["structured_bank_a"]["exact_partition"]
check("bank-A 0x44 row family: 33 rows, every-8th unchanged, 645 changed bytes", part["curve_rows_0x44"]["count"] == 33 and part["curve_rows_0x44"]["unchanged_row_indices"] == [0, 8, 16, 24, 32] and part["curve_rows_0x44"]["total_changed"] == 645)
check("bank-A 0x24 row family unchanged", part["rows_0x24"]["count"] == 4 and part["rows_0x24"]["total_changed"] == 0)
check("bank-A interstitial carries 28 changes", part["interstitial"]["changed_bytes"] == 28)
check("bank-A 0x28 row family: 32 rows, every-8th unchanged, 240 changed bytes", part["rows_0x28"]["count"] == 32 and part["rows_0x28"]["unchanged_row_indices"] == [0, 8, 16, 24] and part["rows_0x28"]["total_changed"] == 240)
diff_total_bank_a = sum(1 for k in range(0x10100, 0x11400) if h[k] != s[k])
check("bank-A tail carries 230 changes and the partition closes to 1143", part["tail"]["changed_bytes"] == 230 and part["total_changed"] == 1143 == diff_total_bank_a)
check("bank-A 0x44 rows end in FFFF7FFF and 0x28 rows end in 7FFFFFFF", all(struct.unpack_from("<I", h, a + 0x40)[0] == 0xFFFF7FFF for a in range(0x10100, 0x109C4, 0x44)) and all(struct.unpack_from("<I", h, a + 0x24)[0] == 0x7FFFFFFF for a in range(0x10B54, 0x11054, 0x28)))

# Bank-B packed point schema: rows 2..17 share the same u16 axis; only i16 values change.
rowsB = list(range(0x120F4, 0x1237C, 0x24))
axis_2_17 = {tuple(struct.unpack_from("<H", s, a + 4 * k)[0] for k in range(8)) for a in rowsB[2:]}
check("bank-B rows 2..17 share the exact u16 axis {6400,7680,10240,12800,15360,19200,25600,32000}", axis_2_17 == {(6400, 7680, 10240, 12800, 15360, 19200, 25600, 32000)})
axis_0_1 = {tuple(struct.unpack_from("<H", h, a + 4 * k)[0] for k in range(8)) for a in rowsB[:2]}
check("bank-B rows 0/1 use the distinct small axis and are unchanged", axis_0_1 == {(0, 80, 480, 960, 1920, 3200, 4800, 11520)} and all(h[a:a + 0x24] == s[a:a + 0x24] for a in rowsB[:2]))

# Compiled-default override semantics: defaults are zero in both specimens; records differ.
cdo = shadow["compiled_default_override_semantics"]
check("compiled default blocks for records 0/2/3 are byte-identical zero pages in both specimens", all(d["identical_between_variants"] and d["all_zero_baseline"] and d["all_zero_target"] for d in cdo["default_blocks"]) and h[0x21000:0x21078] == s[0x21000:0x21078] and not any(h[0x21000:0x21078]))
check("default blocks are pinned at the exact reader-seeded addresses", [(d["va"], d["length"], d["family_index"]) for d in cdo["default_blocks"]] == [("0x21000", 0x10, "0x203"), ("0x21010", 0x28, "0x200"), ("0x21038", 0x40, "0x202")])
check("records 0/2/3 are classified as per-unit/service overrides over unchanged software defaults", "not a compile-time 2023->2025 tuning revision" in cdo["interpretation"] and "Torque Sensor Adjustment" in cdo["interpretation"])

# XCP page-state handlers.
xps = shadow["xcp_page_state"]
check("XCP page-state cells and handlers are pinned", xps["state_cells"] == ["0xFEBE5DB0", "0xFEBE5DB1"] and xps["set_cal_page_handler"] == "0x9261E (custom selector 0xEB)" and xps["get_cal_page_handler"] == "0x92698 (custom selector 0xEA)" and xps["e4_copy_handler"] == "0x92724 (custom selector 0xE4) -> 0x92700")

# Record-8 authoritative unit field.
check("record-8 differing field is the u32 at payload+0x10 with byte 0 zero", struct.unpack_from("<I", h, 0xA518)[0] == 0x7FCF4D00 and struct.unpack_from("<I", s, 0xA518)[0] == 0x3AA4B800 and h[0xA518] == 0 and records[8]["role"] == "family_standard_unit_value_record")
SIENNA_R8 = struct.unpack_from("<I", SIENNA, 0xA638)[0]
check("Sienna final unit record carries the same schema with value 0x1AEBBD00", SIENNA_R8 == 0x1AEBBD00 and struct.unpack_from("<I", SIENNA, 0xA628)[0] == 0xA55A5AA5)

# Isolated scalar region authoritative bytes.
iso = ident["isolated_scalar_region"]
check("isolated scalar u16 sequences are exact", iso["u16_sequence_baseline"] == [2, 104, 2345, 2345, 2442, 2442, 2442, 0] and iso["u16_sequence_target"] == [2, 104, 2345, 2441, 2442, 2442, 2442, 0] and list(struct.unpack_from("<8H", h, 0x13E40)) == iso["u16_sequence_baseline"] and list(struct.unpack_from("<8H", s, 0x13E40)) == iso["u16_sequence_target"])

print("\nSpan low-CodeFlash calibration delta verification passed.")
