#!/usr/bin/env python3
"""Build the byte- and structure-bounded Span-vs-H low-CodeFlash delta report.

This analysis intentionally stops short of inventing OEM names.  It proves the
layout of the changed low CodeFlash, the A000 unit-calibration/identity record family,
the exact lookup-table deltas, the XCP shadow-copy boundary, and the identity /
CRC consequences.  Semantic role labels are bounded to control-flow already
recovered target-natively from the byte-identical H/Span application.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import struct
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
H_DEFAULT = ROOT / "community/albinoelephant/raw-20260818/albinoelephant-corolla-2023.20260814-0023/dump_codeflash_00000000_00200000_20260814-025814.bin"
SPAN_DEFAULT = ROOT / "community/spanconstant/raw-20260821/span-corolla-2025.20260821-1511/dump_codeflash_00000000_00200000_20260821-152033.bin"
OUT_DEFAULT = ROOT / "data/generated/corolla_8965F1208000_low_calibration_delta.json"

CODEFLASH_SIZE = 0x100000
A_DESC_BASE = 0x2AB8C
A_RECORD_COUNT = 9
A_RECORD_COUNT_VA = 0x2A974
A_DESC_STRIDE = 12
SHADOW_SOURCE_START = 0x10000
SHADOW_SOURCE_END = 0x17DF0
SHADOW_RAM_START = 0xFEBF7C00
# Boot integrity-region table (3 rows x 28 bytes) and the AES-CMAC verify chain that
# consumes it.  Row shape: u32 start, u32 end-inclusive, u32 cmac_tag_address (field +8,
# returned by boot_memory_region_get_cmac_tag), u32 marker_address (+0xC, returned by
# boot_memory_region_get_marker_address), u32 field_10 (+0x10), u32 enabled, u32 crc
# descriptor pointer.  Named functions are Sienna ledger names proven as exact-byte
# transfers at identical H addresses.
REGION_TABLE_VA = 0x8DE0
REGION_TABLE_ROWS = 3
REGION_TABLE_STRIDE = 28

# Function sizes are target-native H Ghidra boundaries.  Span is byte-identical
# over every one of these application bodies, so the raw-body hashes are also
# Span body hashes.  The role names are deliberately structural/bounded.
FUNCTIONS = {
    0x20880: (12, "application_entry_to_startup_initializer"),
    0x3376: (58, "boot_memory_region_get_cmac_tag"),
    0x33B0: (54, "boot_memory_region_get_marker_address"),
    0x6E9E: (38, "payload_cmac_verify_enqueue"),
    0x6EC4: (36, "cmac_block_pump_driver"),
    0x7106: (78, "payload_cmac_verify_setup"),
    0x7154: (126, "payload_cmac_verify_step"),
    0x7336: (148, "aes_block_encrypt_core"),
    0x7DF0: (424, "aes_cmac_process_block"),
    0x2DA0A: (30, "record3_staging_to_live_copy"),
    0x2DAA8: (76, "record3_calibration_read_to_staging"),
    0x2DE9A: (114, "record0_staging_to_live_copy"),
    0x2DF98: (158, "record0_calibration_read_to_staging"),
    0x2F318: (174, "record2_staging_to_live_copy"),
    0x2F40A: (84, "record2_staging_to_live_gate"),
    0x2FB36: (236, "record2_calibration_read_to_staging"),
    0x2FC22: (358, "record2_live_coefficient_bounds_checker"),
    0x50E6A: (8, "a000_unit_calibration_record_base_getter"),
    0x42B98: (86, "three_mode_signed_byte_angle_correction_lut"),
    0x42C42: (208, "motor_angle_correction_mode_selector"),
    0x42D28: (184, "record6_zero_lut_angle_correction_consumer"),
    0x42BEE: (84, "corrected_angle_wrap_unwrap"),
    0x429EE: (242, "redundant_channel_angle_vector_builder"),
    0x69EF0: (166, "quadrant_angle_solver"),
    0x428F6: (38, "motor_rotation_angle_wrap_extender"),
    0x2EDE6: (1004, "six_channel_calibration_state_machine"),
    0x2F46A: (426, "record2_calibration_bounds_checker"),
    0x30008: (756, "record2_runtime_shadow_update"),
    0x43528: (1632, "multi_channel_gain_offset_runtime_consumer"),
    0x42700: (32, "record3_three_way_coefficient_selector"),
    0x42720: (462, "record3_angle_offset_consumer"),
    0x5C992: (36, "startup_low_codeflash_shadow_copy"),
    0x5CAAC: (98, "application_startup_initializer"),
    0x92700: (36, "xcp_e4_low_codeflash_shadow_copy"),
    0x60010: (92, "calibration_family_dispatch_write_runtime_shadow"),
    0x6009E: (50, "calibration_family_dispatch_validate_read"),
    0x602A0: (98, "a000_record_ram_clear_init"),
    0x60302: (48, "a000_record_crc_worker"),
    0x60332: (52, "a000_record_crc_validator"),
    0x60418: (90, "a000_record_runtime_shadow_copy_in"),
    0x604AA: (110, "a000_record_validate_and_copy_out"),
}

# Exact low-region bins chosen only after the full byte diff was exhausted.
LOW_BINS = [
    (0xA000, 0xA528, "a000_unit_calibration_identity_records"),
    (0x10000, 0x10100, "low_bank_header"),
    (0x10100, 0x11400, "structured_lookup_bank_a"),
    (0x11400, 0x120F4, "unchanged_low_bank_gap_a"),
    (0x120F4, 0x1237C, "structured_lookup_bank_b"),
    (0x1237C, 0x13E00, "unchanged_low_bank_gap_b"),
    (0x13E00, 0x13E80, "isolated_changed_scalar_region"),
    (0x13E80, 0x17D80, "unchanged_low_bank_tail"),
    (0x17D80, 0x17D90, "single_record_identity"),
    (0x17D90, 0x17DC0, "identity_gap"),
    (0x17DC0, 0x17DD0, "f181_secondary_record"),
    (0x17DD0, 0x17DEC, "pre_crc_fixup_tail"),
    (0x17DEC, 0x17DF0, "low_region_terminal_crc_fixup"),
    (0x17DF0, 0x17E00, "region0_cmac_tag"),
]

RECORD_ROLES = {
    0: {
        "classification": "active-unit-calibration",
        "role": "multi_channel_gain_offset_calibration",
        "boundary": "0x2DF98 validates/reads fixed family index 0x200 into FEBE679E..FEBE67C0 staging; 0x2DE9A copies that staging block to live FEBE6776..FEBE6798, whose sign-dependent gains/offsets are consumed by 0x43528 in a redundant multi-channel motor/sensor path. Exact OEM channel naming remains bounded.",
        "evidence_chain": ["0x6009E(0x200)->0x604AA", "0x2DF98->FEBE679E..FEBE67C0", "0x2DE9A->FEBE6776..FEBE6798", "0x43528"],
    },
    1: {"classification": "unchanged-record", "role": "unresolved_8_byte_unit_record"},
    2: {
        "classification": "active-unit-calibration",
        "role": "six_channel_calibration_state_coefficients",
        "boundary": "0x2FB36 validates/reads fixed family index 0x202 into FEBE68F4..FEBE6928 staging; 0x2F318 copies that block into live FEBE6896..FEBE68CA under 0x2F40A's integrity/state gate, and 0x2FC22 bounds-checks the live coefficients. The related six-channel state machine 0x2EDE6 and 0x30008 can feed derived/current values back through 0x60010(0x202) to the runtime RAM copy. No CodeFlash self-programming is claimed.",
        "evidence_chain": ["0x6009E(0x202)->0x604AA", "0x2FB36->FEBE68F4..FEBE6928", "0x2F40A->0x2F318", "0x2F318->FEBE6896..FEBE68CA", "0x2FC22", "0x2EDE6/0x30008->0x60010(0x202) runtime-copy path"],
    },
    3: {
        "classification": "active-unit-calibration",
        "role": "three_way_motor_angle_offset_coefficients",
        "boundary": "0x2DAA8 validates/reads fixed family index 0x203 into staging FEBE671A/1C/1E; 0x2DA0A copies those three signed coefficients to live FEBE6712/14/16. 0x42700 selects one by status bits and 0x42720 adds it to the motor-rotation-angle path before trig/vector generation.",
        "evidence_chain": ["0x6009E(0x203)->0x604AA", "0x2DAA8->FEBE671A/1C/1E", "0x2DA0A->FEBE6712/14/16", "0x42700", "0x42720"],
    },
    4: {
        "classification": "identity",
        "role": "ecu_part_number_record",
        "boundary": "Payload is marker A55A5AA5 followed by the 10-character Toyota part number '8965012N50' (i.e. 89650-12N50) and two NUL bytes, identical in both Corolla specimens. The Sienna calibration's same-shaped record 4 at 0xA0A0 carries '8965045170' (89650-45170), matching its F181 identity family. Techstream's English string database contains the exact OEM vocabulary 'ECU Part Number' (M_English entries 2665884 and 10040272) used by diagnostic part-number displays. No target-native firmware consumer of this record's staged RAM (FEBEF6A0) was recovered, so the classification rests on the cross-variant Toyota part-number shape plus OEM vocabulary, not on a decompiled reader.",
    },
    5: {
        "classification": "active-unit-calibration",
        "role": "three_mode_motor_rotation_angle_correction_luts",
        "boundary": "Three 256-byte signed lookup curves at payload+8 are selected by 0x42C42 and linearly interpolated by 0x42B98; Techstream vocabulary corroborates the motor-rotation-angle domain but does not name these exact tables.",
    },
    6: {
        "classification": "active-addressed-null-record",
        "role": "zero_filled_angle_correction_lut",
        "boundary": "Record 6 payload+8 is a 256-byte all-zero table in both images. 0x42D28 obtains A000 through 0x50E6A and indexes base+0x3D0, exactly record6 payload+8, in the same angle-correction domain. The full 0x108-byte payload is zero (including the absent 5AA5/A55A marker); it is active-addressed structure but contributes zero with the retained bytes.",
    },
    7: {
        "classification": "identity",
        "role": "ecu_serial_record",
        "boundary": "Payload is marker A55A5AA5 followed by the 20-character unit serial (e.g. '8965012N50A05G310920' -> '8965012N50E12H030731'), zero padded. The serial embeds the same 89650-12N50 part-number family as record 4 plus a unit-unique suffix. Techstream's English string database carries the OEM vocabulary 'Display of ECU Product Serial Number' (M_English entry 7345514) and 'Sensor Serial Number' (entry 2665916) used by diagnostic serial displays; no target-native firmware reader of the staged copy at FEBEFAD8 was recovered, so the serial classification rests on the live F18C/serial observation and the record shape.",
    },
    8: {
        "classification": "changed-opaque-unit-record",
        "role": "opaque_24_byte_unit_record",
        "boundary": "Only three payload bytes differ. No target-native semantic consumer beyond the generic record family has been recovered; do not assign an OEM meaning or manufacturing origin.",
    },
}


def sha256(blob: bytes) -> str:
    return hashlib.sha256(blob).hexdigest()


def load(path: Path) -> tuple[bytes, dict]:
    raw = path.read_bytes()
    if len(raw) == 0x200000 and raw[CODEFLASH_SIZE:] == b"\xff" * CODEFLASH_SIZE:
        code = raw[:CODEFLASH_SIZE]
        norm = "trim-all-ff-upper-1mib-from-2mib-range-dump"
    elif len(raw) == CODEFLASH_SIZE:
        code = raw
        norm = "bare-codeflash"
    else:
        raise ValueError(f"unexpected CodeFlash geometry: {path}: {len(raw):#x}")
    return code, {"path": str(path.resolve().relative_to(ROOT)), "source_size": len(raw), "source_sha256": sha256(raw), "normalized_sha256": sha256(code), "normalization": norm}


def diff_count(a: bytes, b: bytes, start: int, end: int) -> int:
    return sum(x != y for x, y in zip(a[start:end], b[start:end]))


def body_rows(h: bytes, s: bytes) -> list[dict]:
    out = []
    for addr, (size, role) in sorted(FUNCTIONS.items()):
        hb = h[addr:addr + size]
        sb = s[addr:addr + size]
        out.append({
            "entry": f"0x{addr:08X}", "body_size": size, "role": role,
            "baseline_body_sha256": sha256(hb), "target_body_sha256": sha256(sb),
            "byte_identical": hb == sb,
        })
    return out


def signed16_list(blob: bytes) -> list[int]:
    return list(struct.unpack("<" + "h" * (len(blob) // 2), blob))


def build_report(h_path: Path = H_DEFAULT, span_path: Path = SPAN_DEFAULT) -> dict:
    h, hm = load(h_path)
    s, sm = load(span_path)
    changed = {i for i, (x, y) in enumerate(zip(h, s)) if x != y}

    record_count_u16 = struct.unpack_from("<H", h, A_RECORD_COUNT_VA)[0]
    target_record_count_u16 = struct.unpack_from("<H", s, A_RECORD_COUNT_VA)[0]
    if record_count_u16 != A_RECORD_COUNT or target_record_count_u16 != A_RECORD_COUNT:
        raise ValueError(f"A000 record count drift: baseline={record_count_u16} target={target_record_count_u16}")

    descriptors = []
    for idx in range(A_RECORD_COUNT):
        off = A_DESC_BASE + idx * A_DESC_STRIDE
        length, pad_u16, ram, source = struct.unpack_from("<HHII", h, off)
        length_s, pad_s_u16, ram_s, source_s = struct.unpack_from("<HHII", s, off)
        if (length_s, pad_s_u16, ram_s, source_s) != (length, pad_u16, ram, source):
            raise ValueError(f"A000 descriptor {idx} changed between variants")
        if pad_u16 != 0:
            raise ValueError(f"A000 descriptor {idx} has nonzero length padding {pad_u16:#x}")
        payload_h = h[source:source + length]
        payload_s = s[source:source + length]
        fix_h = struct.unpack_from("<I", h, source + length)[0]
        fix_s = struct.unpack_from("<I", s, source + length)[0]
        crc_h = zlib.crc32(h[source:source + length + 4]) & 0xFFFFFFFF
        crc_s = zlib.crc32(s[source:source + length + 4]) & 0xFFFFFFFF
        row = {
            "index": idx, "descriptor_va": f"0x{off:X}", "length": length,
            "length_width_bits": 16, "padding_u16": pad_u16,
            "ram_destination": f"0x{ram:08X}", "codeflash_source": f"0x{source:X}",
            "payload_changed_bytes": diff_count(h, s, source, source + length),
            "payload_baseline_sha256": sha256(payload_h), "payload_target_sha256": sha256(payload_s),
            "stored_crc_fixup_baseline": f"0x{fix_h:08X}", "stored_crc_fixup_target": f"0x{fix_s:08X}",
            "zlib_crc32_payload_plus_fixup_baseline": f"0x{crc_h:08X}",
            "zlib_crc32_payload_plus_fixup_target": f"0x{crc_s:08X}",
            "standard_terminal_residue_ffffffff_baseline": crc_h == 0xFFFFFFFF,
            "standard_terminal_residue_ffffffff_target": crc_s == 0xFFFFFFFF,
            **RECORD_ROLES[idx],
        }
        if idx in (0, 2, 3, 8):
            row["baseline_signed16"] = signed16_list(payload_h)
            row["target_signed16"] = signed16_list(payload_s)
        if idx == 6:
            row["payload_all_zero_baseline"] = not any(payload_h)
            row["payload_all_zero_target"] = not any(payload_s)
            row["a55a5aa5_marker_present_baseline"] = payload_h[:4] == bytes.fromhex("a55a5aa5")
            row["a55a5aa5_marker_present_target"] = payload_s[:4] == bytes.fromhex("a55a5aa5")
        if idx == 7:
            row["baseline_serial"] = payload_h[4:].split(b"\0", 1)[0].decode("ascii", "replace")
            row["target_serial"] = payload_s[4:].split(b"\0", 1)[0].decode("ascii", "replace")
        descriptors.append(row)

    # Record 5 contains marker+4 reserved bytes followed by 3 contiguous signed-byte LUTs.
    lut_rows = []
    lut_base = 0xA0C0
    for mode in range(3):
        start = lut_base + mode * 0x100
        hv = list(struct.unpack_from("<256b", h, start))
        sv = list(struct.unpack_from("<256b", s, start))
        deltas = [abs(x-y) for x, y in zip(hv, sv)]
        lut_rows.append({
            "mode_index": mode, "start": f"0x{start:X}", "end_exclusive": f"0x{start+0x100:X}",
            "changed_bytes": sum(x != y for x, y in zip(hv, sv)),
            "baseline_min": min(hv), "baseline_max": max(hv),
            "target_min": min(sv), "target_max": max(sv),
            "mean_absolute_delta": round(sum(deltas) / 256, 6), "max_absolute_delta": max(deltas),
        })

    low_bins = [
        {"start": f"0x{a:X}", "end_exclusive": f"0x{b:X}", "label": label,
         "size": b-a, "changed_bytes": diff_count(h, s, a, b)}
        for a, b, label in LOW_BINS
    ]

    # Table-bank structural invariants: same sentinel geometry, changed numeric coefficients.
    sentinel_values = (0xFFFF7FFF, 0x7FFFFFFF)
    sentinel_offsets_h = {f"0x{v:08X}": [f"0x{o:X}" for o in range(0x10100, 0x11400, 4) if struct.unpack_from("<I", h, o)[0] == v] for v in sentinel_values}
    sentinel_offsets_s = {f"0x{v:08X}": [f"0x{o:X}" for o in range(0x10100, 0x11400, 4) if struct.unpack_from("<I", s, o)[0] == v] for v in sentinel_values}
    bank_b_record_start, bank_b_record_end, bank_b_stride = 0x120F4, 0x1237C, 0x24
    bank_b_records = []
    for a in range(bank_b_record_start, bank_b_record_end, bank_b_stride):
        baseline_sentinel = struct.unpack_from("<I", h, a + bank_b_stride - 4)[0]
        target_sentinel = struct.unpack_from("<I", s, a + bank_b_stride - 4)[0]
        if baseline_sentinel != 0x7FFFFFFF or target_sentinel != 0x7FFFFFFF:
            raise ValueError(f"structured bank-B sentinel drift at 0x{a:X}")
        bank_b_records.append({
            "start": f"0x{a:X}", "changed_bytes": diff_count(h, s, a, a + bank_b_stride),
            "terminal_sentinel": "0x7FFFFFFF",
            "baseline_sha256": sha256(h[a:a+bank_b_stride]), "target_sha256": sha256(s[a:a+bank_b_stride]),
        })

    # False-pointer audit: aligned application dwords that numerically fall in the changed low bank.
    # These are retained only as triage; semantic consumers require target-native code review.
    aligned_numeric_hits = []
    for off in range(0x20000, CODEFLASH_SIZE - 3, 4):
        val = struct.unpack_from("<I", h, off)[0]
        if 0x10000 <= val < 0x17E00 and any((val + d) in changed for d in range(4)):
            aligned_numeric_hits.append({"application_offset": f"0x{off:X}", "numeric_value": f"0x{val:X}"})

    # Boot integrity-region table + AES-CMAC tag verification chain.
    # 0x8DE0 table is byte-identical between H and Span (asserted below).
    region_rows = []
    for i in range(REGION_TABLE_ROWS):
        off = REGION_TABLE_VA + i * REGION_TABLE_STRIDE
        start, end_incl, tag, marker, field_10, enabled, crc_desc = struct.unpack_from("<7I", h, off)
        if struct.unpack_from("<7I", s, off) != (start, end_incl, tag, marker, field_10, enabled, crc_desc):
            raise ValueError(f"integrity region table row {i} changed between variants")
        region_rows.append({
            "row": i, "start": f"0x{start:X}", "end_inclusive": f"0x{end_incl:X}",
            "cmac_tag_address": f"0x{tag:X}", "marker_address": f"0x{marker:X}",
            "field_10": f"0x{field_10:X}", "enabled": enabled, "crc_descriptor_table": f"0x{crc_desc:X}",
            "tag_is_final_16_bytes_of_region": tag == end_incl - 0xF,
            "marker_value_baseline": f"0x{struct.unpack_from('<I', h, marker)[0]:08X}",
            "marker_value_target": f"0x{struct.unpack_from('<I', s, marker)[0]:08X}",
        })
    cmac_tag_h = h[0x17DF0:0x17E00]
    cmac_tag_s = s[0x17DF0:0x17E00]


    return {
        "schema": "corolla-span-low-calibration-delta-v1",
        "baseline_id": "8965H1202000", "target_id": "8965F1208000",
        "target_id_basis": "observed/application F181 primary 8965F1208000 at 0x20860; distinct single-record identity 8965H1213000 at 0x17D80 is retained separately",
        "baseline": hm, "target": sm,
        "summary": {
            "different_codeflash_bytes": len(changed), "first_difference": f"0x{min(changed):X}", "last_difference": f"0x{max(changed):X}",
            "application_start": "0x20000", "application_different_bytes": diff_count(h, s, 0x20000, CODEFLASH_SIZE),
            "all_differences_below_0x17e00": all(i < 0x17E00 for i in changed),
            "a000_record_bank_changed_bytes": diff_count(h, s, 0xA000, 0xA528),
            "low_shadow_source_changed_bytes": diff_count(h, s, SHADOW_SOURCE_START, SHADOW_SOURCE_END),
            "post_crc_opaque_tag_changed_bytes": diff_count(h, s, 0x17DF0, 0x17E00),
            "region0_cmac_tag_changed_bytes": diff_count(h, s, 0x17DF0, 0x17E00),
            "delta_partition_complete": len(changed) == (diff_count(h, s, 0xA000, 0xA528) + diff_count(h, s, SHADOW_SOURCE_START, SHADOW_SOURCE_END) + diff_count(h, s, 0x17DF0, 0x17E00)),
        },
        "low_region_bins": low_bins,
        "a000_record_family": {
            "descriptor_table": f"0x{A_DESC_BASE:X}", "record_count": A_RECORD_COUNT,
            "record_count_source": {"va": f"0x{A_RECORD_COUNT_VA:X}", "width_bits": 16, "baseline": record_count_u16, "target": target_record_count_u16},
            "descriptor_shape": "u16 length, u16 zero padding, u32 runtime-RAM destination, u32 CodeFlash source",
            "records": descriptors,
            "standard_crc_note": "Eight records use a 4-byte terminal fixup such that zlib.crc32(payload||fixup)==0xFFFFFFFF. Record 1 is the sole special all-zero-fixup exception and is left unclassified.",
            "runtime_family_boundary": "0x60010 updates the RAM copy for family 0x200; 0x6009E/0x604AA validate/read CodeFlash-backed records. This does not prove application self-programming of CodeFlash.",
        },
        "motor_rotation_angle_luts": lut_rows,
        "record3_coefficients": {
            "baseline": list(struct.unpack_from("<hhh", h, 0xA08C)),
            "target": list(struct.unpack_from("<hhh", s, 0xA08C)),
            "selector": "0x42700", "consumer": "0x42720",
            "formula_boundary": "selected coefficient is added to 5*(motor_rotation_angle - comparison/state angle) before trigonometric/vector generation",
        },
        "low_shadow_bank": {
            "source_start": f"0x{SHADOW_SOURCE_START:X}", "source_end_exclusive": f"0x{SHADOW_SOURCE_END:X}",
            "destination_start": f"0x{SHADOW_RAM_START:08X}", "length": SHADOW_SOURCE_END-SHADOW_SOURCE_START,
            "startup_copy_function": "0x0005C992", "startup_call_chain": ["0x00020880", "0x0005CAAC", "0x0005C992"],
            "xcp_e4_copy_function": "0x00092700",
            "structured_bank_a": {
                "start": "0x10100", "end_exclusive": "0x11400", "changed_bytes": diff_count(h, s, 0x10100, 0x11400),
                "sentinel_offsets_baseline": sentinel_offsets_h, "sentinel_offsets_target": sentinel_offsets_s,
                "sentinel_geometry_identical": sentinel_offsets_h == sentinel_offsets_s,
            },
            "structured_bank_b": {
                "start": "0x120F4", "end_exclusive": "0x1237C", "record_stride": bank_b_stride,
                "record_count": len(bank_b_records), "record_shape": "eight u32 values followed by u32 0x7FFFFFFF sentinel",
                "records": bank_b_records,
            },
            "cpu_consumer_boundary": "Target-native H/Span review found no recovered application CPU semantic dereference of the 0x10000+ shadow beyond the startup/E4 copies and XCP calibration-page bookkeeping. Apparent low-address references reviewed in the decompiler resolve to scalar/control-word uses or numeric/packed metadata rather than reads of the low-bank contents. Computed-pointer or undocumented hardware-overlay use is not disproved.",
            "aligned_application_numeric_hits_near_changed_low_bytes": aligned_numeric_hits,
        },
        "boot_integrity_regions": {
            "region_table_va": f"0x{REGION_TABLE_VA:X}",
            "row_count": REGION_TABLE_ROWS,
            "row_stride": REGION_TABLE_STRIDE,
            "row_shape": "u32 start, u32 end-inclusive, u32 cmac_tag_address (+8), u32 marker_address (+0xC), u32 field_10, u32 enabled, u32 crc descriptor table pointer",
            "table_identical_between_variants": True,
            "rows": region_rows,
            "cmac_verify_chain": [
                {"entry": "0x00005BEA", "role": "integrity task dispatcher by FEBF2B64 mode (0x10F0/0x10F1 -> routine_verify_crc_cmac_task 0x591A)"},
                {"entry": "0x0000591A", "role": "routine_verify_crc_cmac_task: resolves region start/len from FEBF2B58/5C and starts the CMAC session"},
                {"entry": "0x00006E9E", "role": "payload_cmac_verify_enqueue: gates on FEBF2BFD and calls payload_cmac_verify_setup"},
                {"entry": "0x00007106", "role": "payload_cmac_verify_setup: boot_memory_region_get_cmac_tag stores the tag pointer, initializes the AES-CMAC IV block, sets current=start and end=start+len-0x10"},
                {"entry": "0x00003376", "role": "boot_memory_region_get_cmac_tag: iterates the 0x8DE0 table and returns field +8 (region-0 = 0x17DF0)"},
                {"entry": "0x00006EC4/0x00007154", "role": "payload_cmac_verify_step: processes 16-byte blocks; on the final block byte-compares all 16 generated CMAC bytes against the stored tag"},
                {"entry": "0x00007DF0", "role": "aes_cmac_process_block: CBC-MAC style XOR + subkey handling with 0x80 padding on the final partial block"},
                {"entry": "0x00007336", "role": "AES block encryption core (10-round loop)"},
                {"entry": "0x00007D34", "role": "aes_cmac_generate_subkeys"},
            ],
            "region0_cmac_tag_baseline": cmac_tag_h.hex(),
            "region0_cmac_tag_target": cmac_tag_s.hex(),
            "region0_cmac_semantics": "For region 0 (0x10000..0x17DFF), the final 16 bytes at 0x17DF0..0x17DFF are the AES-CMAC tag over 0x10000..0x17DEF under a boot-derived key. The tag is verified by routine_verify_crc_cmac_task (0x591A). The complete 16/16-byte tag change between H and Span is therefore expected cryptographic integrity fallout of the changed calibration page, not independent tuning data. Boundary: the verification role and code path are proven, but the exact DID 0x201 key material and the DID 0x202 IV/build-time inputs used by the factory to produce the stored low-region tag are not recovered from this static image/session; zero-valued DID material used by public RAM fixtures does not reproduce the stored tag. The boot payload-build root at 0xBFD8 is present in the image; non-reproduction with zero inputs is an input-recovery boundary, not a statement that the key is absent.",
            "high_region_boundary": "Region 1 (0x18000..0xFFDFF) has its CMAC tag at 0xFFDF0 and validity marker at 0xFFE00; because H and Span are byte-identical over 0x18000..0xFFDF0, that tag is also identical and does not enter this delta. The 0x40004000-pattern filler at 0xFFDF0..0xFFDFF is retained as observed; whether the high-region tag slot is programmed on this generation is not asserted here.",
        },
        "identity_and_integrity_tail": {
            "single_record_identity_baseline": h[0x17D80:0x17D90].split(b"\0",1)[0].decode("ascii","replace"),
            "single_record_identity_target": s[0x17D80:0x17D90].split(b"\0",1)[0].decode("ascii","replace"),
            "f181_secondary_baseline": h[0x17DC0:0x17DD0].split(b"\0",1)[0].decode("ascii","replace"),
            "f181_secondary_target": s[0x17DC0:0x17DD0].split(b"\0",1)[0].decode("ascii","replace"),
            "low_region_crc_fixup_baseline": h[0x17DEC:0x17DF0].hex(),
            "low_region_crc_fixup_target": s[0x17DEC:0x17DF0].hex(),
            "low_region_crc32_residue_baseline": f"0x{zlib.crc32(h[0x10000:0x17DF0]) & 0xFFFFFFFF:08X}",
            "low_region_crc32_residue_target": f"0x{zlib.crc32(s[0x10000:0x17DF0]) & 0xFFFFFFFF:08X}",
            "low_region_crc_geometry": "zlib.crc32(0x10000..0x17DEF including terminal fixup)==0xFFFFFFFF",
            "post_crc_opaque_tag_baseline": cmac_tag_h.hex(), "post_crc_opaque_tag_target": cmac_tag_s.hex(),
            "opaque_tag_cpu_xref_status": "superseded: the 16 bytes at 0x17DF0..0x17DFF are the region-0 AES-CMAC tag per boot_integrity_regions; no separate opaque-tag interpretation remains",
            "opaque_tag_algorithm": "superseded-by-boot-integrity-region-0-aes-cmac-tag",
            "shadow_identity_mirrors": {
                "0x17D80_to_ram": "0xFEBFF980",
                "0x17DC0_to_ram": "0xFEBFF9C0"
            },
        },
        "application_function_evidence": body_rows(h, s),
        "interpretation": {
            "same_executable_generation": True,
            "low_delta_is_not_identity_only": True,
            "unit_specific_motor_calibration_differs": True,
            "model_year_tuning_change_proven": False,
            "security_secoc_diagnostic_xcp_code_changed": False,
            "steering_command_interface_changed_by_code": False,
            "note": "The changed A000 records contain active motor/sensor calibration, including motor-rotation-angle correction. Because the specimens are different physical ECUs, the bytes may be per-unit manufacturing calibration, service calibration, or variant tuning rather than a 2023->2025 software-generation tune change. The evidence does not distinguish those origins.",
        },
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--baseline", type=Path, default=H_DEFAULT)
    ap.add_argument("--target", type=Path, default=SPAN_DEFAULT)
    ap.add_argument("--output", type=Path, default=OUT_DEFAULT)
    args = ap.parse_args()
    report = build_report(args.baseline, args.target)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report["summary"], indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
