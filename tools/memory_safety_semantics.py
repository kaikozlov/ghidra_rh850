#!/usr/bin/env python3
"""Independent raw-byte oracle for the memory-safety proof matrix.

This deliberately does not import generated Ghidra output or compare whole-body
hashes.  Each proposition pins only the decisive RH850 instructions or tables
whose semantics are independently described in the canonical audit.
"""
from __future__ import annotations

import argparse
import json
import struct
from pathlib import Path
from typing import Callable


REPO = Path(__file__).resolve().parents[1]
DEFAULT_IMAGE = REPO / "firmware" / "RH850_P1M-E_CodeFlash.bin"


def _exact(image: bytes, address: int, hex_bytes: str) -> bool:
    expected = bytes.fromhex(hex_bytes)
    return image[address : address + len(expected)] == expected


def _u16(image: bytes, address: int) -> int:
    return struct.unpack_from("<H", image, address)[0]


def _u32(image: bytes, address: int) -> int:
    return struct.unpack_from("<I", image, address)[0]


def _routine_rows(image: bytes) -> list[tuple[int, int, int, int, int]]:
    return [struct.unpack_from("<I H B B I", image, 0x8F44 + 12 * i) for i in range(5)]


def _access_rows(image: bytes) -> list[tuple[int, int, int, int]]:
    return [struct.unpack_from("<IIII", image, 0x8DA0 + 16 * i) for i in range(3)]


def _secoc_rows(image: bytes) -> list[int]:
    return [0x25970 + 0x50 * i for i in range(6)]


def analyze(image: bytes) -> dict[str, object]:
    """Return claim-specific proposition results for a CodeFlash image."""
    routines = _routine_rows(image)
    accesses = _access_rows(image)
    secoc = _secoc_rows(image)

    propositions: dict[str, dict[str, bool]] = {
        "MEM-SAFE-001": {
            # enqueue count, source, and destination fields
            "enqueue_stores_count_source_destination": _exact(
                image, 0x6BC2, "6437dc930150643fd5936447d993"
            ),
            # cap at 16, floor(count/16), and zero-block edge around AES call
            "worker_caps_and_floors_blocks": _exact(
                image, 0x6BEA, "e4efdd93200e10001d06f0ffe1ef22eb1de0a4e2"
            ),
            "zero_blocks_bypass_aes": (
                _exact(image, 0x6BFE, "f21d")
                and _exact(image, 0x6C06, "80ff0205")
                and _exact(image, 0x6C3C, "24f6dc93")
            ),
            "full_count_subtracted_and_completion_set": _exact(
                image, 0x6C40, "7008bd09800cd00aba054407de93"
            ),
            # ordinary TransferData admits final <=0x400, range-checks, and queues decrypt
            "ordinary_transfer_length_range_and_enqueue_chain": (
                _exact(image, 0x4BF0, "0708bd09820d")
                and _exact(image, 0x4C04, "1d06fffb")
                and _exact(image, 0x4C2E, "bfffa4e6")
                and _exact(image, 0x4C72, "80ff421f")
                and _exact(image, 0x4DDA, "bfffa2fd")
            ),
            # completion reads the validated download destination then calls memcpy
            "raw_staging_reaches_download_memcpy": (
                _exact(image, 0x4F7E, "243fb9921d40bfffb6c5")
                and _exact(image, 0x153A, "06f0e041870d6008")
            ),
            "range_checker_rejects_zero_and_wrap": _exact(
                image, 0x32D6, "e039f21dc6390796fffff231ab1d"
            ),
            "ram_window_is_operation_enabled": accesses
            == [
                (0x10000, 0x17DFF, 0x33, 0),
                (0x18000, 0xFFDFF, 0x33, 0),
                (0xFEBF0000, 0xFEBF0FFF, 0x33, 1),
            ],
            "cmac_success_sets_authorization_bit": _exact(
                image, 0x59D2, "010a4407179324f61193f30fc29860081309800b"
            ),
            "second_download_accepts_state_one": _exact(
                image, 0x5E70, "a40f119301067fff d205".replace(" ", "")
            ),
            "callback_pointer_is_indirectly_consumed": _exact(
                image, 0x434C, "40eebffe3defd10f0ad81c380142234e0300fdc760f9"
            ),
            "sid36_routes_ordinary_transfer": any(
                struct.unpack_from("<BBHI", image, 0x8E54 + i * 8)[0] == 0x36
                and struct.unpack_from("<BBHI", image, 0x8E54 + i * 8)[3] == 0x4DBA
                for i in range(20)
            ),
        },
        "MEM-SAFE-002": {
            "setup_computes_start_plus_length_minus_16": _exact(
                image, 0x715C, "64e7b198dce950ea0ad864efa998"
            ),
            "step_advances_exactly_16": _exact(image, 0x717E, "06e61000"),
            "finality_is_endpoint_equality": _exact(
                image, 0x7182, "e131f205e1e1ea05"
            ),
            "nonfinal_path_feeds_one_cmac_block": _exact(
                image, 0x71A4, "1b381d48630f01002046100080ff5c0c"
            ),
            "step_persists_incremented_pointer": _exact(image, 0x71E6, "64e7b198"),
            "caller_supplies_address_and_length_records": (
                [row[1] for row in routines] == [0x10F0, 0x10F1, 0x10F2, 0x10F3, 0xFF00]
                and routines[0][2:4] == (1, 10)
                and routines[1][2:4] == (1, 10)
            ),
            # Exact direct-call boundary of the step body: one CMAC primitive only.
            "bounded_no_exfiltration_call_consumer": (
                image[0x7170:0x71EE].count(bytes.fromhex("80ff5c0c")) == 1
                and image[0x7170:0x71EE].count(bytes.fromhex("80ff")) == 1
            ),
        },
        "MEM-SAFE-003": {
            "routine_10f3_is_zero_option_compare_arm": routines[3][1:4] == (0x10F3, 1, 0),
            "request_download_uses_operation_bit_five": _exact(
                image, 0x5EC2, "0542234e0200bfff0ad4"
            ),
            "compare_transfer_routes_source_target_length": _exact(
                image, 0x4D60, "0730243fb99280ff061f"
            ),
            "comparison_is_byte_granular": _exact(
                image, 0x6CB4, "939f0100d2f16080f099ea1d"
            ),
            "equality_advances_and_mismatch_stops": (
                _exact(image, 0x6CCA, "d19924f6e893649fe593009dd199b109019d640fe193")
                and _exact(image, 0x6CFA, "4407ed93")
            ),
            "response_distinguishes_equal_and_mismatch": _exact(
                image, 0x4EF8, "840fed93e009ea05030a950dbfff56fcd50520361000bfff2afc"
            ),
            "compare_ranges_include_application_exclude_secrets": (
                accesses[:2]
                == [(0x10000, 0x17DFF, 0x33, 0), (0x18000, 0xFFDFF, 0x33, 0)]
                and all((row[2] & (1 << 5)) != 0 for row in accesses[:2])
                and 0xBFD8 < accesses[0][0]
                and 0xBFE8 < accesses[0][0]
            ),
        },
        "MEM-SAFE-004": {
            "prepare_requires_input_64_and_capacity_at_least_48": (
                _exact(image, 0x86E78, "0706c0ffb205")
                and _exact(image, 0x86E82, "23f71100000d0106d0ffe30712db")
            ),
            "failure_branch_loads_original_length_and_zero_fills": (
                _exact(image, 0x86EF8, "02ed00dd")
                and _exact(image, 0x86F20, "1d30e0e1ea15")
                and _exact(image, 0x86F50, "3b3f010080fff020")
            ),
            "success_path_copies_32_plus_16_and_returns_48": _exact(
                image, 0x86F26,
                "24d6f458204620001a3e480080ff0c1f1d3620001a3e68002046100080fffc1e200e30007b0f0100",
            ),
            "configured_submit_fixes_output_48_and_input_64": (
                _exact(image, 0x6825C, "200e30001d38640f5998")
                and _exact(image, 0x6827A, "204640000648")
                and _exact(image, 0x68284, "240e5898030d82ffac06")
            ),
            "driver_dispatch_has_single_configured_call_site": (
                image.count(bytes.fromhex("82ffac06")) == 1
                and _exact(image, 0x6828A, "82ffac06")
            ),
        },
        "MEM-SAFE-005": {
            "application_copy_is_capacity_gated": _exact(
                image, 0x90472, "80ff261ffb0f0500ea098b0d1d301b381a4080ff4e1c"
            ),
            "secoc_checks_total_before_trailer_subtraction": (
                _exact(image, 0x8E510, "fd0f0700e39f3500e199c125")
                and _exact(image, 0x8E5E2, "9309")
            ),
            "dlc_decoder_is_canonical": image[0x22F10:0x22F20]
            == bytes([0, 1, 2, 3, 4, 5, 6, 7, 8, 12, 16, 20, 24, 32, 48, 64]),
            "secoc_record_lengths_are_bounded": (
                [_u32(image, a + 0x3C) for a in secoc] == [8, 8, 8, 8, 32, 32]
                and [_u32(image, a + 0x44) for a in secoc] == [8, 8, 8, 8, 32, 32]
                and [_u16(image, a + 6) for a in secoc] == [8, 4, 4, 4, 4, 4]
            ),
            "range_checker_zero_and_wrap_boundary": _exact(
                image, 0x32D6, "e039f21dc6390796fffff231ab1d"
            ),
        },
    }

    claim_pass = {claim: all(items.values()) for claim, items in propositions.items()}
    return {
        "schema_version": 1,
        "claims": claim_pass,
        "propositions": propositions,
        "all_pass": all(claim_pass.values()),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("image", nargs="?", type=Path, default=DEFAULT_IMAGE)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = analyze(args.image.read_bytes())
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        for claim, items in result["propositions"].items():
            print(f"== {claim} ==")
            for name, passed in items.items():
                print(f"[{'PASS' if passed else 'FAIL'}] {name}")
        print("PASS" if result["all_pass"] else "FAIL")
    return 0 if result["all_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
