#!/usr/bin/env python3
"""Extract exact-F33 incident structure offline; never connect to or write an ECU.

This reports raw call instructions, configured receive callbacks, and interrupt
entries. It is not a whole-device execution model or a recovery implementation.
Semantic interpretation belongs in the accompanying recovery report.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
IMAGE = ROOT / "firmware/camry-8965F3307000/CodeFlash.bin"
IMAGE_SHA256 = "42dce8efc42f6ae31718e7713fa2d26bb9191b4a82439778aee4d7afded9b0e7"
TP = 0x23DFC


def address(value: int) -> str:
    return f"0x{value:08X}"


def jarl22_target(raw: bytes, pc: int) -> int:
    """Decode only an ordinary four-byte RH850 JARL with link register lp."""
    if len(raw) != 4:
        raise ValueError("JARL disp22 requires exactly four bytes")
    first, second = struct.unpack("<HH", raw)
    if first & 0xFFC0 != 0xFF80 or second & 1:
        raise ValueError(f"not JARL disp22,lp at {address(pc)}: {raw.hex()}")
    displacement = ((first & 0x3F) << 16) | second
    if displacement & 0x200000:
        displacement -= 0x400000
    return (pc + displacement) & 0xFFFFFFFF


def subset_displacements(value: int) -> list[int]:
    """Return every unsigned value obtainable by clearing bits in *value*."""
    bits = [bit for bit in range(32) if value & (1 << bit)]
    return [
        sum(1 << bit for index, bit in enumerate(bits) if selector & (1 << index))
        for selector in range(1 << len(bits))
    ]


def analyze(image: bytes) -> dict[str, object]:
    digest = hashlib.sha256(image).hexdigest()
    if len(image) != 0x100000 or digest != IMAGE_SHA256:
        raise ValueError("this layout is specific to the exact stock F33 image")

    def u16(offset: int) -> int:
        return struct.unpack_from("<H", image, offset)[0]

    def u32(offset: int) -> int:
        return struct.unpack_from("<I", image, offset)[0]

    def span(offset: int, size: int) -> dict[str, object]:
        return {"address": address(offset), "size": size,
                "bytes": image[offset:offset + size].hex()}

    def call(offset: int) -> dict[str, object]:
        return {**span(offset, 4),
                "target": address(jarl22_target(image[offset:offset + 4], offset))}

    # Incident record, not a generated replacement image. Include the following
    # stock halfword: the defect cannot be decoded from its four stored bytes alone.
    incident_stream = bytes.fromhex("ff02925b") + image[0x7A276:0x7A278]
    incident_displacement = struct.unpack_from("<I", incident_stream, 2)[0]
    incident_target = (0x7A272 + struct.unpack_from("<i", incident_stream, 2)[0]) & 0xFFFFFFFF

    # Encoding geometry only: the P1M-E manual prohibits programming the same
    # CodeFlash range twice after erasure.  This does not assert that a
    # clear-bits-only write is executable on the device.  It records that, if a
    # proper erase/RMW executor is obtained, the malformed JARL32 has one useful
    # same-prefix re-encoding whose destination is a matching one-LP epilogue.
    epilogue_stream = bytes.fromhex("ff0212010000")
    if any(
        after & ~before
        for before, after in zip(incident_stream, epilogue_stream, strict=True)
    ):
        raise ValueError("recovery epilogue encoding requires setting a programmed bit")
    epilogue_target = (
        0x7A272 + struct.unpack_from("<i", epilogue_stream, 2)[0]
    ) & 0xFFFFFFFF
    if (
        epilogue_target != 0x7A384
        or image[epilogue_target:epilogue_target + 4] != bytes.fromhex("40063f00")
    ):
        raise ValueError("recovery epilogue geometry drift")
    subset_targets = {
        (0x7A272 + displacement) & 0xFFFFFFFF
        for displacement in subset_displacements(incident_displacement)
    }
    resident_spans = ((0xFFE04, 0xFFEF4), (0xFFF04, 0xFFFFE))
    resident_subset_targets = sorted(
        target for target in subset_targets
        if any(start <= target < end for start, end in resident_spans)
    )

    # Restrict this census to the reviewed interrupt slots. Adjacent data words
    # must not be promoted to vector targets merely because they look address-like.
    vector_slots = (0x20220, 0x20414, 0x20418, 0x2041C, 0x204EC,
                    0x204F0, 0x20690, 0x20694, 0x207EC)
    vectors = [{"slot": address(slot), "target": address(u32(slot)),
                "entry_bytes": image[u32(slot):u32(slot) + 12].hex()}
               for slot in vector_slots]
    direct_vectors = []
    for offset in (0x10, 0x20, 0x30, 0x40, 0x50, 0x60, 0x70,
                   0x80, 0x90, 0xA0, 0xB0, 0xC0, 0xE0, 0xF0):
        pc = 0x20000 + offset
        raw = image[pc:pc + 8]
        if raw[:4] != bytes.fromhex("1f00e006"):
            raise ValueError(f"unexpected direct-vector form at {address(pc)}")
        direct_vectors.append({**span(pc, 8), "target": address(u32(pc + 4))})

    # INTECM is EIINT8 on P1M-E. Exact F33 uses an orphan/table-driven handler
    # at INTBP[8], so preserve it explicitly rather than relying only on
    # Ghidra's direct-call function closure.
    ecm_mask = 0x100B001E
    if image[0x6376A:0x6376E] != struct.pack("<I", ecm_mask):
        raise ValueError("exact F33 ECM mask immediate drift")
    ecm_enabled_sources = [bit for bit in range(32) if ecm_mask & (1 << bit)]
    if ecm_enabled_sources != [1, 2, 3, 4, 16, 17, 19, 28]:
        raise ValueError("unexpected exact F33 ECM mask source set")

    # Owner 0, class 2 is the real 7A1 / 777 / 7A0 diagnostic route.
    diagnostic_ids = [address(u32(0x21FA0 + 8 * n)) for n in range(3)]
    upper_routes = []
    channel_base = u32(0x22C70)
    for n in range(image[0x22C7C]):
        channel = channel_base + n * 12
        for row in range(image[channel + 9]):
            record = u32(channel) + row * 32
            upper = u16(record + 8)
            route_table = u32(0x21D40 + (upper >> 11) * 4)
            route_row = route_table + (upper & 0x7FF) * 4
            mapped, local = u16(route_row), u16(route_row + 2)
            vtable = u32(0x21CBC) if local != 0xFFFF else u32(0x21EE4 + (mapped >> 11) * 4)
            upper_routes.append({
                "transport_record": address(record),
                "lower_handle": address(u16(record + 4)),
                "upper_handle": address(upper), "route_row": address(route_row),
                "vtable": address(vtable),
                "start_of_reception": address(u32(vtable + 12)),
                "copy_receive_data": address(u32(vtable + 16)),
                "receive_completion": address(u32(vtable + 24)),
            })

    return {
        "schema": "f33-offline-recovery-structure-v1",
        "source": {"image": str(IMAGE.relative_to(ROOT)), "sha256": digest,
                   "size": len(image), "va_equals_file_offset": True},
        "scope": "Raw structural evidence; no ECU access, flash output, or complete execution proof",
        "incident": {"hook_address": address(0x7A272),
                     "stock_instruction": call(0x7A272),
                     "recorded_bad_four_bytes": "ff02925b",
                     "instruction_with_stock_successor": incident_stream.hex(),
                     "decoded_bad_target": address(incident_target),
                     "clear_bits_encoding_geometry": {
                         "candidate_instruction": epilogue_stream.hex(),
                         "cleared_bit_mask": bytes(
                             before ^ after
                             for before, after in zip(incident_stream, epilogue_stream, strict=True)
                         ).hex(),
                         "candidate_target": address(epilogue_target),
                         "candidate_target_bytes": image[epilogue_target:epilogue_target + 4].hex(),
                         "matching_entry_prologue": span(0x7A254, 4),
                         "subset_displacement_count": len(subset_targets),
                         "resident_subset_targets": [address(target) for target in resident_subset_targets],
                         "scope": (
                             "encoding relation only; does not assert that CodeFlash "
                             "can be overwritten without erase"
                         ),
                     },
                     "live_exception_registers_observed": False},
        "foreground_order": [call(pc) for pc in range(0x667EA, 0x66802, 4)],
        "pre_hook_calls": [call(pc) for pc in (0x7A262, 0x7A266, 0x7A26A, 0x7A26E)],
        "comm_initialized_guard": {
            "read_compare_branch": span(0x7A258, 10),
            "startup_terminal_assignment": span(0x7A180, 8)},
        "receive_owner_callbacks": [address(u32(0x21A24 + 4 * n)) for n in range(6)],
        "diagnostic_can_ids": diagnostic_ids,
        "diagnostic_callback": address(u32(0x21A94)),
        "diagnostic_transport_to_upper_routes": upper_routes,
        "upper_adapter_targets": {
            "start_of_reception": address(u32(0x2188C)),
            "copy_receive_data": address(u32(0x21890)),
            "receive_completion": address(u32(0x21898))},
        "unused_special_callback": span(0x814AC, 2),
        "stock_xcp_dispatch_gate": span(0x30D68, 1),
        "reviewed_nondefault_interrupt_entries": vectors,
        "application_direct_vectors": direct_vectors,
        "default_exception": span(0x62E1E, 38),
        "vector_90_saved_pc_adjustment": span(0x65BDC, 12),
        "vector_90_return": span(0x65C50, 20),
        "foreground_mpu_context_selector": image[0x31683],
        "mpu_region_zero": {"lower": address(u32(0x31688)),
                            "upper_inclusive": address(u32(0x3168C) | 3),
                            "attributes_context_0": address(u32(0x31708)),
                            "attributes_context_1": address(u32(0x31748))},
        "boot_validity_call": call(0x13C4),
        "boot_application_entry_cell": {"address": address(0xFFDB8),
                                        "value": address(u32(0xFFDB8))},
        "boot_marker_words": [span(pc, 4) for pc in (0xFFE00, 0x17E00)],
        "boot_hardware_error_check": span(0x115A, 68),
        "boot_cold_flash_error_clear": span(0x802, 0x12),
        "boot_retained_reset_record": {
            "reader": span(0xE54, 170),
            "reader_call": call(0x13B8),
            "validity_call_after_reader": call(0x13C4),
        },
        "application_errorout_mask_init": {
            "startup_call": call(0x6380E),
            "ecmemk0": {"register": "0xFFD62028", "value": "0xFFFFFFE1",
                        "program_sequence": span(0x63354, 0x1A)},
            "ecmemk1": {"register": "0xFFD6202C", "value": "0xFFFFFFFF",
                        "program_sequence": span(0x63384, 0x18)},
            "ecmemk2": {"register": "0xFFD62030", "value": "0x3FFFFFFF",
                        "program_sequence": span(0x633B2, 0x20)},
        },
        "application_ecm_maskable_interrupt": {
            "interrupt_number": 8,
            "manual_interrupt_name": "INTECM",
            "intbp_slot": address(0x20220),
            "intbp_target": address(u32(0x20220)),
            "micfg0_register": "0xFFD62004",
            "micfg0_value": address(ecm_mask),
            "micfg0_program_sequence": span(0x63760, 0x28),
            "enabled_sources": ecm_enabled_sources,
            "handler": {
                "entry": address(0x71AE4),
                "master_status_register": "0xFFD60008",
                "checker_status_register": "0xFFD61008",
                "dispatch_sequence": span(0x71AE4, 0xD0),
                "source_1_to_4_target": address(0x7162E),
                "source_16_17_target": address(0x65CDA),
                "source_19_target": address(0x65DD6),
                "source_28_target": address(0x65F24),
                "unclassified_fallback_reset": call(0x71BB0),
            },
            "manual_source_semantics": {
                "1": "CPU DCLS compare error",
                "2": "DMA/GRAM PFSS compare error",
                "3": "internal bus-bridge arbitration error",
                "4": "redundant functional-block compare error",
                "16": "local-RAM uncorrectable ECC",
                "17": "global-RAM uncorrectable ECC",
                "19": "CodeFlash uncorrectable ECC/address parity",
                "28": "internal System-Interconnect/P-Bus ECC DED",
            },
            "rscanfd_ecm_sources_not_enabled": [22, 37, 54],
            "scope": (
                "exact F33 vector/mask/dispatch bytes plus P1M-E ECM source names; "
                "does not claim that a physical silicon fault is impossible to induce"
            ),
        },
        "external_supervisor_clock": {
            "collective_port_table_base": address(0x87A0),
            "port4_record": span(0x8860, 0x30),
            "p4_5": {
                "bit": 5,
                "p": (u16(0x8860 + 0x24) >> 5) & 1,
                "pmc": (u16(0x8860 + 0x26) >> 5) & 1,
                "pm": (u16(0x8860 + 0x28) >> 5) & 1,
                "pfc": (u16(0x8860 + 0x1C) >> 5) & 1,
                "pfce": (u16(0x8860 + 0x1E) >> 5) & 1,
                "pfcae": (u16(0x8860 + 0x20) >> 5) & 1,
                "pibc": (u16(0x8860 + 0x2A) >> 5) & 1,
                "pbdc": (u16(0x8860 + 0x2C) >> 5) & 1,
                "selector_bits_pfcae_pfce_pfc": "010",
                "manual_decode": "third-alternative output EXTCLK1O",
            },
            "boot_clock_init": {
                "function": address(0x10C6),
                "source_select_register": "0xFFF890C0",
                "source_select_value": 4,
                "divider_register": "0xFFF88818",
                "divider_value": "0x00000050",
                "source_select_sequence": span(0x10CA, 0x16),
                "divider_enable_sequence": span(0x1122, 0x10),
            },
            "periodic_repair": {
                "function": address(0x619C0),
                "caller": address(0x667B6),
                "expected_divider": "0x00000050",
                "sequence": span(0x619C0, 0x2A),
            },
            "terminal_reset": {
                "function": address(0x61940),
                "clock_stop_via": address(0x61906),
                "clock_stop_mode": "0xFF",
                "p4_set_reset_register": "0xFFC10104",
                "p4_mode_set_reset_register": "0xFFC10124",
                "p4_function_set_reset_register": "0xFFC10120",
                "p4_5_update_mask": "0x00200000",
                "sequence": span(0x61982, 0x1E),
            },
            "boot_reset": {
                "function": address(0x1560),
                "p4_bit": 5,
                "sequence": span(0x1560, 0x3C),
            },
            "scope": (
                "raw exact-F33 clock/port/reset geometry; EXTCLK1O and clock-frequency semantics "
                "are interpreted from the P1M-E hardware manual"
            ),
        },
        "application_to_boot_call": call(0x65F82),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="write the JSON report here instead of stdout")
    args = parser.parse_args()
    try:
        text = json.dumps(analyze(IMAGE.read_bytes()), indent=2, sort_keys=True) + "\n"
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(text, encoding="utf-8")
            print(args.output)
        else:
            print(text, end="")
    except (OSError, ValueError, struct.error) as exc:
        parser.exit(2, f"F33 offline structure: {exc}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
