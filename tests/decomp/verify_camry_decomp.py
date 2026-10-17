#!/usr/bin/env python3
"""Camry identity link, and equivalent C checked against retained original-byte oracles."""
from __future__ import annotations

import ctypes
import json
import os
import signal
import subprocess
import tempfile
from pathlib import Path

from tools import REPO_ROOT
from tools.camry_decomp import ROOT, identity_image, load_matched, load_symbols
from tools.project.analysis_target import target as resolve_target

ORACLES = ROOT / "oracles.jsonl"
SIGNATURES = {
    row["name"]: row["signature"]
    for row in load_symbols()
    if row.get("signature")
}
INCLUDE = ROOT / "include"
HOST_MEM = Path(__file__).with_name("camry_host_mem.c")
MAX_SPAN = 2_000_000

# r10 is the C return value. memcpy returns the destination pointer.
POINTER_RETURN = {"f33_memcpy_forward"}
VALUE_RETURN = {
    "f33_update_whole_words",
    "f33_load_u8",
    "f33_load_u16",
    "f33_nvm_sum_bytes",
    "f33_nvm_family0_chunk_cost",
    "f33_scale_u16_delta_s16_x4",
    "f33_nvm_payload_length",
    "f33_nvm_base_offset",
    "f33_nvm_payload_page_count",
    "f33_nvm_trailer_offset",
    "f33_nvm_storage_handle",
    "f33_nvm_get_logical_storage_page",
    "f33_nvm_advance_family0_request_index",
    "f33_nvm_advance_family1_request_index",
    "f33_nvm_allocation_pages",
    "f33_nvm_record_offset",
    "f33_nvm_payload_chunk_length",
    "f33_nvm_get_family0_status",
    "f33_nvm_get_family1_completion",
    "f33_nvm_get_family1_record",
    "f33_nvm_get_family1_status",
    "f33_nvm_get_family2_status",
    "f33_read_repair_redundant_u8",
    "f33_nvm_check_family1_checksum",
    "f33_nvm_retain_token_while_reads_pending",
    "f33_force_unconfirmed_terminal_monitor_healthy",
    "f33_freshness_select_reset_candidate",
    "f33_freshness_reconstruct_ordinary",
    "f33_freshness_reconstruct_candidate",
    "f33_nvm_probe_range_rejected",
    "f33_nvm_translate_diagnostic_mask",
    "f33_lookup_u32_value_by_key",
    "f33_poll_word_masks",
    "f33_icus20_read_bit0",
    "f33_nvm_translate_read_driver_result",
    "f33_nvm_translate_saved_driver_result",
    "f33_nvm_get_direct_operation_result",
    "f33_nvm_read_buffer",
    "f33_nvm_write_buffer",
    "f33_nvm_submit_operation",
    "f33_classify_channel_residual_a",
    "f33_curve16_interpolate_with_slope",
    "f33_check_learned_quad_bounds",
    "f33_nvm_enqueue_family0_read",
    "f33_nvm_set_family0_record",
    "f33_dcra1_crc_raw_words",
    "f33_nvm_check_family2_rom_crc",
    "f33_nvm_get_family2_rom_record",
    "f33_nvm_get_record",
    "f33_nvm_refresh_family2_record_status",
    "f33_restore_learned_quad",
    "f33_nvm_pop_queue_head",
    "f33_nvm_enqueue_read",
    "f33_nvm_enqueue_write",
    "f33_nvm_arm_family0_read",
    "f33_nvm_arm_family0_write",
    "f33_nvm_submit_family1_read_copies",
    "f33_nvm_submit_family1_write_copies",
    "f33_nvm_submit_bulk_reads",
    "f33_nvm_step_initial_read_acquisition",
    "f33_nvm_step_acquisition_pass",
    "FUN_00077982",
    "f33_faci_decode_completion_status",
    "f33_priority_mask_enter",
    "f33_dataflash_copy_words_ecc",
}

DCRA1_BASE = 0xFFD51000
DCRA1_SIZE = 0x24
DCRA_CALLS = {
    "f33_dcra1_crc_raw_words",
    "f33_nvm_check_family2_rom_crc",
    "f33_nvm_get_family2_rom_record",
    "f33_nvm_refresh_family2_record_status",
    "f33_nvm_step_acquisition_pass",
}

ROM_TABLES = (
    ("f33_nvm_descriptors", 0x27634, 123 * 6),
    ("f33_nvm_logical_descriptors", 0x26C0C, 124 * 16),
)
ROM_BYTES = (
    ("f33_nvm_family0_request_cell_count", 0x2AD8A),
    ("f33_nvm_family1_request_cell_count", 0x2AD8B),
)


def load_oracles() -> list[dict]:
    rows = []
    with ORACLES.open(encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def compile_sources(directory: Path, optimize: str = "-O2") -> ctypes.CDLL:
    library = directory / "libcamry.dylib"
    sources = sorted((ROOT / "src").glob("*.c"))
    subprocess.run(
        [
            "cc", "-std=c11", optimize, "-Wall", "-Wextra", "-Werror", "-fwrapv",
            "-Wno-unused-variable", "-Wno-unused-parameter",
            "-Wno-unused-function", "-Wno-unused-label",
            "-Wno-pointer-to-int-cast", "-Wno-int-to-pointer-cast",
            "-Wno-bitwise-op-parentheses",             "-Wno-sign-compare", "-Wno-parentheses",
            "-Wno-pointer-sign", "-Wno-incompatible-pointer-types",
            "-DCAMRY_HOST",
            "-I", str(INCLUDE),
            "-dynamiclib", "-o", str(library),
            *[str(path) for path in sources],
            str(HOST_MEM),
        ],
        check=True,
        text=True,
        capture_output=True,
    )
    return ctypes.CDLL(library)


def bind(library: ctypes.CDLL) -> None:
    u8p = ctypes.POINTER(ctypes.c_uint8)
    u32p = ctypes.POINTER(ctypes.c_uint32)
    u32 = ctypes.c_uint32
    library.f33_memcpy_forward.argtypes = [u8p, u8p, u32]
    library.f33_memcpy_forward.restype = u8p
    library.f33_memzero.argtypes = [u8p, u32]
    library.f33_memzero.restype = None
    library.f33_copy_whole_words.argtypes = [u32p, u32p, ctypes.c_uint16]
    library.f33_copy_whole_words.restype = None
    library.f33_update_whole_words.argtypes = [u32p, u32p, ctypes.c_uint16]
    library.f33_update_whole_words.restype = u32
    library.f33_load_u8.argtypes = [u8p]
    library.f33_load_u8.restype = u32
    library.f33_load_u16.argtypes = [u8p]
    library.f33_load_u16.restype = u32
    library.f33_store_u8.argtypes = [u8p, u32]
    library.f33_store_u8.restype = None
    library.f33_store_u16.argtypes = [u8p, u32]
    library.f33_store_u16.restype = None
    library.f33_store_u32.argtypes = [u8p, u32]
    library.f33_store_u32.restype = None
    library.f33_nvm_sum_bytes.argtypes = [u32, u8p]
    library.f33_nvm_sum_bytes.restype = u32
    library.f33_nvm_family0_chunk_cost.argtypes = [u32]
    library.f33_nvm_family0_chunk_cost.restype = u32
    library.f33_scale_u16_delta_s16_x4.argtypes = [u32, u32, u32]
    library.f33_scale_u16_delta_s16_x4.restype = u32
    library.f33_priority_mask_enter.argtypes = [u32]
    library.f33_priority_mask_enter.restype = u32
    library.f33_dataflash_copy_words_ecc.argtypes = [u32, u32, u32]
    library.f33_dataflash_copy_words_ecc.restype = u32
    library.f33_priority_mask_restore.argtypes = [u32]
    library.f33_priority_mask_restore.restype = None
    for name in (
        "f33_nvm_payload_length",
        "f33_nvm_base_offset",
        "f33_nvm_payload_page_count",
        "f33_nvm_trailer_offset",
        "f33_nvm_storage_handle",
        "f33_nvm_advance_family0_request_index",
        "f33_nvm_advance_family1_request_index",
        "FUN_00077982",
    ):
        getattr(library, name).argtypes = [u32]
        getattr(library, name).restype = u32
    library.f33_nvm_record_offset.argtypes = [u32, u32, u32]
    library.f33_nvm_record_offset.restype = u32
    library.f33_nvm_payload_chunk_length.argtypes = [u32, u32]
    library.f33_nvm_payload_chunk_length.restype = u32
    library.f33_nvm_probe_range_rejected.argtypes = [u32, u32]
    library.f33_nvm_probe_range_rejected.restype = u32
    library.f33_lookup_u32_value_by_key.argtypes = [u32, u32, u32]
    library.f33_lookup_u32_value_by_key.restype = u32
    library.f33_poll_word_masks.argtypes = [u32, u32, u32, u32]
    library.f33_poll_word_masks.restype = u32
    library.f33_clear_application_ram_4k.argtypes = []
    library.f33_clear_application_ram_4k.restype = None
    library.f33_nvm_set_physical_result_state.argtypes = [u32]
    library.f33_nvm_set_physical_result_state.restype = None
    library.f33_nvm_set_secondary_result_state.argtypes = [u32]
    library.f33_nvm_set_secondary_result_state.restype = None
    library.f33_icus20_read_bit0.argtypes = []
    library.f33_icus20_read_bit0.restype = u32
    library.f33_faci_decode_completion_status.argtypes = []
    library.f33_faci_decode_completion_status.restype = u32
    library.f33_nvm_lookup_byte_result.argtypes = [u32, u32, u32]
    library.f33_nvm_lookup_byte_result.restype = u32
    library.f33_nvm_translate_read_driver_result.argtypes = [u32]
    library.f33_nvm_translate_read_driver_result.restype = u32
    library.f33_nvm_translate_saved_driver_result.argtypes = []
    library.f33_nvm_translate_saved_driver_result.restype = u32
    library.f33_nvm_get_logical_storage_page.argtypes = [u32, ctypes.POINTER(ctypes.c_uint16)]
    library.f33_nvm_get_logical_storage_page.restype = u32
    library.f33_nvm_get_direct_operation_result.argtypes = []
    library.f33_nvm_get_direct_operation_result.restype = u32
    library.f33_nvm_accumulate_diagnostic_mask.argtypes = [u32]
    library.f33_nvm_accumulate_diagnostic_mask.restype = None
    library.f33_nvm_accumulate_side_status.argtypes = [u32]
    library.f33_nvm_accumulate_side_status.restype = None
    library.f33_nvm_accumulate_result_class.argtypes = [u32]
    library.f33_nvm_accumulate_result_class.restype = None
    library.f33_nvm_initialize_operation.argtypes = []
    library.f33_nvm_initialize_operation.restype = None
    library.f33_nvm_unlink_queue_slot.argtypes = [u32, u32, u32]
    library.f33_nvm_unlink_queue_slot.restype = None
    library.f33_nvm_recover_family0_request_indices.argtypes = [u8p, u8p]
    library.f33_nvm_recover_family0_request_indices.restype = None
    library.f33_nvm_recover_family1_request_indices.argtypes = [u8p, u8p]
    library.f33_nvm_recover_family1_request_indices.restype = None
    library.f33_freshness_encode_wire.argtypes = [u32, u32, u32]
    library.f33_freshness_encode_wire.restype = None
    library.f33_freshness_decode_wire.argtypes = [u32, u32, u32]
    library.f33_freshness_decode_wire.restype = None
    library.f33_nvm_check_family1_checksum.argtypes = [u32]
    library.f33_nvm_check_family1_checksum.restype = u32
    library.f33_nvm_retain_token_while_reads_pending.argtypes = [u32]
    library.f33_nvm_retain_token_while_reads_pending.restype = u32
    library.f33_nvm_publish_family1_checksum.argtypes = [u32]
    library.f33_nvm_publish_family1_checksum.restype = None
    library.f33_pwm_initialize_compare_stages.argtypes = [u32]
    library.f33_pwm_initialize_compare_stages.restype = None
    library.f33_pwm_stage_halfword_compares.argtypes = [u32, u32, u32, u32]
    library.f33_pwm_stage_halfword_compares.restype = None
    library.f33_pwm_stage_word_compares.argtypes = [u32, u32, u32, u32]
    library.f33_pwm_stage_word_compares.restype = None
    library.f33_nvm_set_read_buffer.argtypes = [u32, u32]
    library.f33_nvm_set_read_buffer.restype = None
    library.f33_nvm_set_write_buffer.argtypes = [u32, u32]
    library.f33_nvm_set_write_buffer.restype = None
    library.f33_nvm_submit_operation.argtypes = [u32]
    library.f33_nvm_submit_operation.restype = u32
    library.f33_freshness_select_reset_candidate.argtypes = [u32, u32]
    library.f33_freshness_select_reset_candidate.restype = u32
    library.f33_freshness_commit_pending.argtypes = [u32, u32]
    library.f33_freshness_commit_pending.restype = None
    library.f33_freshness_reconstruct_ordinary.argtypes = [u32, u32, u32, u32]
    library.f33_freshness_reconstruct_ordinary.restype = u32
    library.f33_freshness_reconstruct_candidate.argtypes = [u32, u32, u32, u32]
    library.f33_freshness_reconstruct_candidate.restype = u32
    library.f33_nvm_get_family1_record.argtypes = [u32, u32]
    library.f33_nvm_get_family1_record.restype = u32
    library.f33_nvm_get_family1_status.argtypes = [u32]
    library.f33_nvm_get_family1_status.restype = u32
    library.f33_nvm_get_family2_status.argtypes = [u32]
    library.f33_nvm_get_family2_status.restype = u32
    library.f33_nvm_initialize_family1_application.argtypes = []
    library.f33_nvm_initialize_family1_application.restype = None
    library.f33_nvm_publish_logical_result.argtypes = [u32, u32, u32]
    library.f33_nvm_publish_logical_result.restype = None
    library.f33_read_repair_redundant_u8.argtypes = [u32, u32, u32, u32]
    library.f33_read_repair_redundant_u8.restype = u32
    library.f33_classify_channel_residual_a.argtypes = []
    library.f33_classify_channel_residual_a.restype = u32
    library.f33_check_learned_quad_bounds.argtypes = []
    library.f33_check_learned_quad_bounds.restype = u32
    library.f33_nvm_enqueue_family0_read.argtypes = [u32]
    library.f33_nvm_enqueue_family0_read.restype = u32
    library.f33_nvm_set_family0_record.argtypes = [u32, u32]
    library.f33_nvm_set_family0_record.restype = u32
    library.f33_dcra1_crc_raw_words.argtypes = [u32, u32, u32]
    library.f33_dcra1_crc_raw_words.restype = u32
    library.f33_nvm_check_family2_rom_crc.argtypes = [u32]
    library.f33_nvm_check_family2_rom_crc.restype = u32
    library.f33_nvm_get_family2_rom_record.argtypes = [u32, u32]
    library.f33_nvm_get_family2_rom_record.restype = u32
    library.f33_nvm_get_record.argtypes = [u32, u32]
    library.f33_nvm_get_record.restype = u32
    library.f33_nvm_refresh_family2_record_status.argtypes = [u32]
    library.f33_nvm_refresh_family2_record_status.restype = u32
    library.f33_publish_learned_quad.argtypes = []
    library.f33_publish_learned_quad.restype = None
    library.f33_restore_learned_quad.argtypes = []
    library.f33_restore_learned_quad.restype = u32
    library.f33_curve16_interpolate_with_slope.argtypes = [u32, u32, u32]
    library.f33_curve16_interpolate_with_slope.restype = u32
    library.f33_update_thermal_release_envelope.argtypes = []
    library.f33_update_thermal_release_envelope.restype = None
    library.f33_update_thermal_history_qualification.argtypes = []
    library.f33_update_thermal_history_qualification.restype = None
    library.f33_nvm_initialize_queues.argtypes = []
    library.f33_nvm_initialize_queues.restype = None
    library.f33_nvm_reset_queues_notifying.argtypes = []
    library.f33_nvm_reset_queues_notifying.restype = None
    library.f33_nvm_pop_queue_head.argtypes = [u32, u32]
    library.f33_nvm_pop_queue_head.restype = u32
    library.f33_nvm_enqueue_read.argtypes = [u32, u32]
    library.f33_nvm_enqueue_read.restype = u32
    library.f33_nvm_enqueue_write.argtypes = [u32, u32]
    library.f33_nvm_enqueue_write.restype = u32
    library.f33_nvm_arm_family0_read.argtypes = [u32]
    library.f33_nvm_arm_family0_read.restype = u32
    library.f33_nvm_arm_family0_write.argtypes = [u32]
    library.f33_nvm_arm_family0_write.restype = u32
    library.f33_nvm_submit_family1_read_copies.argtypes = [u32]
    library.f33_nvm_submit_family1_read_copies.restype = u32
    library.f33_nvm_submit_family1_write_copies.argtypes = [u32]
    library.f33_nvm_submit_family1_write_copies.restype = u32
    library.f33_nvm_submit_bulk_reads.argtypes = []
    library.f33_nvm_submit_bulk_reads.restype = u32
    library.f33_nvm_step_initial_read_acquisition.argtypes = []
    library.f33_nvm_step_initial_read_acquisition.restype = u32
    library.f33_nvm_step_acquisition_pass.argtypes = []
    library.f33_nvm_step_acquisition_pass.restype = u32
    library.f33_nvm_run_bounded_initial_acquisition.argtypes = []
    library.f33_nvm_run_bounded_initial_acquisition.restype = None
    library.f33_force_unconfirmed_terminal_monitor_healthy.argtypes = [u32, u32, u32]
    library.f33_force_unconfirmed_terminal_monitor_healthy.restype = u32
    library.f33_nvm_read_buffer.argtypes = [u32]
    library.f33_nvm_read_buffer.restype = u32
    library.f33_nvm_write_buffer.argtypes = [u32]
    library.f33_nvm_write_buffer.restype = u32
    library.camry_host_reset.argtypes = []
    library.camry_host_reset.restype = None
    library.camry_host_add.argtypes = [u32, u8p, u32]
    library.camry_host_add.restype = None
    if (ROOT / "src" / "lifted.c").exists():
        library.camry_lift_run.argtypes = [u32, u32, u32, u32, u32, u32]
        library.camry_lift_run.restype = u32
    library.camry_host_ptr.argtypes = [u32]
    library.camry_host_ptr.restype = u8p


def scenario_regions(scenario: dict) -> list[tuple[int, bytearray]]:
    regions = []
    for row in scenario.get("memory", []):
        address = int(row["address"], 16)
        if "hex" in row:
            payload = bytearray.fromhex(row["hex"])
        else:
            payload = bytearray([row["fill"] & 0xFF]) * row["size"]
        regions.append((address, payload))
    return regions


def read_regions(regions: list[tuple[int, bytearray]], address: int, size: int) -> bytes:
    actual = bytearray(size)
    seen = bytearray(size)
    for base, data in regions:
        start = max(address, base)
        end = min(address + size, base + len(data))
        if start >= end:
            continue
        for cursor in range(start, end):
            actual[cursor - address] = data[cursor - base]
            seen[cursor - address] = 1
    if any(flag == 0 for flag in seen):
        raise AssertionError(f"address {address:#x} size {size} is outside the oracle regions")
    return bytes(actual)


def materialize(scenario: dict) -> tuple[bytearray, int] | None:
    cells: dict[int, int] = {}
    for row in scenario.get("memory", []):
        address = int(row["address"], 16)
        if "hex" in row:
            payload = bytes.fromhex(row["hex"])
        else:
            payload = bytes([row["fill"] & 0xFF]) * row["size"]
        for offset, byte in enumerate(payload):
            cells[address + offset] = byte
    if not cells:
        return bytearray(), 0
    start = min(cells)
    end = max(cells)
    if end - start + 1 > MAX_SPAN:
        return None
    image = bytearray(b"\x00" * (end - start + 1))
    for address, byte in cells.items():
        image[address - start] = byte
    return image, start


def view_of(image: bytearray) -> ctypes.Array:
    return (ctypes.c_uint8 * len(image)).from_buffer(image)


def pointer(view: ctypes.Array, base: int, address: int, kind: type):
    offset = address - base
    if offset < 0 or offset >= len(view):
        raise AssertionError(f"address {address:#x} is outside the mapped oracle memory")
    return ctypes.cast(ctypes.addressof(view) + offset, kind)


def covers(base: int, size: int, address: int, length: int) -> bool:
    if length == 0:
        return True
    offset = address - base
    return 0 <= offset and offset + length <= size


def useful_oracle(scenario: dict) -> bool:
    checks = scenario.get("checks") or []
    has_r10 = any(
        check.get("kind") == "register" and check.get("register") == "r10"
        for check in checks
    )
    has_memory = any(check.get("kind") == "memory" for check in checks)
    has_event = any(check.get("kind") == "event-count" for check in checks)
    if has_event and not has_r10:
        return False
    return has_memory or has_r10


def accessed_ranges(name: str, registers: dict) -> list[tuple[int, int]]:
    r6 = int(registers.get("r6", "0"), 16)
    r7 = int(registers.get("r7", "0"), 16)
    r8 = int(registers.get("r8", "0"), 16)
    if name == "f33_load_u8" or name == "f33_store_u8":
        return [(r6, 1)]
    if name == "f33_load_u16" or name == "f33_store_u16":
        return [(r6, 2)]
    if name == "f33_store_u32":
        return [(r6, 4)]
    if name == "f33_nvm_sum_bytes":
        return [(r7, r6 & 0xFFFF)]
    if name == "f33_memcpy_forward":
        return [(r6, r8), (r7, r8)]
    if name == "f33_memzero":
        return [(r6, r7)]
    if name in {"f33_copy_whole_words", "f33_update_whole_words"}:
        words = (r8 & 0xFFFF) & ~3
        return [(r6, words), (r7, words)]
    if name == "f33_nvm_get_logical_storage_page":
        return [(r7, 2)]
    return []


_DATAFLASH_BYTES: bytearray | None = None
_DATAFLASH_VIEW = None


def dataflash_view():
    global _DATAFLASH_BYTES, _DATAFLASH_VIEW
    if _DATAFLASH_VIEW is None:
        metadata = resolve_target("camry-8965F3307000")[1]
        _DATAFLASH_BYTES = bytearray((REPO_ROOT / metadata["dataflash"]).read_bytes())
        _DATAFLASH_VIEW = view_of(_DATAFLASH_BYTES)
    return _DATAFLASH_VIEW


def install_dataflash(library: ctypes.CDLL) -> None:
    metadata = resolve_target("camry-8965F3307000")[1]
    u8p = ctypes.POINTER(ctypes.c_uint8)
    library.camry_host_add(
        int(metadata["dataflash_base"], 16),
        ctypes.cast(dataflash_view(), u8p),
        len(_DATAFLASH_BYTES),
    )


def install_address_space(library: ctypes.CDLL, code_view, code_size: int, view, base: int, memory: bytearray) -> None:
    u8p = ctypes.POINTER(ctypes.c_uint8)
    library.camry_host_reset()
    library.camry_host_add(0, ctypes.cast(code_view, u8p), code_size)
    install_dataflash(library)
    if memory:
        library.camry_host_add(base & 0xFFFFFFFF, ctypes.cast(view, u8p), len(memory))


def install_regions(library: ctypes.CDLL, code_view, code_size: int, regions: list[tuple[int, bytearray]]) -> list:
    u8p = ctypes.POINTER(ctypes.c_uint8)
    views = []
    library.camry_host_reset()
    library.camry_host_add(0, ctypes.cast(code_view, u8p), code_size)
    install_dataflash(library)
    for base, data in regions:
        view = view_of(data)
        views.append(view)
        library.camry_host_add(base & 0xFFFFFFFF, ctypes.cast(view, u8p), len(data))
    return views


def call_function(library: ctypes.CDLL, name: str, view, base: int, registers: dict) -> int | None:
    r6 = int(registers.get("r6", "0"), 16)
    r7 = int(registers.get("r7", "0"), 16)
    r8 = int(registers.get("r8", "0"), 16)
    r9 = int(registers.get("r9", "0"), 16)
    ctypes.c_uint32.in_dll(library, "camry_gp").value = int(registers.get("gp", "0"), 16) & 0xFFFFFFFF
    ctypes.c_uint32.in_dll(library, "camry_tp").value = int(registers.get("tp", "0"), 16) & 0xFFFFFFFF
    ctypes.c_uint32.in_dll(library, "camry_sp").value = int(registers.get("sp", "0"), 16) & 0xFFFFFFFF
    load_pmr(library, registers)
    u8p = ctypes.POINTER(ctypes.c_uint8)
    u32p = ctypes.POINTER(ctypes.c_uint32)
    if name == "f33_memcpy_forward":
        dest_ptr = pointer(view, base, r6, u8p)
        result = library.f33_memcpy_forward(dest_ptr, pointer(view, base, r7, u8p), r8)
        return int(
            ctypes.cast(result, ctypes.c_void_p).value
            == ctypes.cast(dest_ptr, ctypes.c_void_p).value
        )
    if name == "f33_memzero":
        library.f33_memzero(pointer(view, base, r6, u8p), r7)
        return None
    if name == "f33_copy_whole_words":
        library.f33_copy_whole_words(
            pointer(view, base, r6, u32p),
            pointer(view, base, r7, u32p),
            r8 & 0xFFFF,
        )
        return None
    if name == "f33_update_whole_words":
        return int(library.f33_update_whole_words(
            pointer(view, base, r6, u32p),
            pointer(view, base, r7, u32p),
            r8 & 0xFFFF,
        ))
    if name == "f33_load_u8":
        return int(library.f33_load_u8(pointer(view, base, r6, u8p)))
    if name == "f33_load_u16":
        return int(library.f33_load_u16(pointer(view, base, r6, u8p)))
    if name == "f33_store_u8":
        library.f33_store_u8(pointer(view, base, r6, u8p), r7)
        return None
    if name == "f33_store_u16":
        library.f33_store_u16(pointer(view, base, r6, u8p), r7)
        return None
    if name == "f33_store_u32":
        library.f33_store_u32(pointer(view, base, r6, u8p), r7)
        return None
    if name == "f33_nvm_sum_bytes":
        source = pointer(view, base, r7, u8p) if (r6 & 0xFFFF) else None
        return int(library.f33_nvm_sum_bytes(r6, source))
    if name == "f33_nvm_family0_chunk_cost":
        return int(library.f33_nvm_family0_chunk_cost(r6))
    if name == "f33_scale_u16_delta_s16_x4":
        return int(library.f33_scale_u16_delta_s16_x4(r6, r7, r8)) & 0xFFFFFFFF
    if name == "f33_nvm_record_offset":
        return int(library.f33_nvm_record_offset(r6, r7, r8)) & 0xFFFFFFFF
    if name == "f33_nvm_payload_chunk_length":
        return int(library.f33_nvm_payload_chunk_length(r6, r7)) & 0xFFFFFFFF
    if name == "f33_nvm_probe_range_rejected":
        return int(library.f33_nvm_probe_range_rejected(r6, r7)) & 0xFFFFFFFF
    if name == "f33_lookup_u32_value_by_key":
        return int(library.f33_lookup_u32_value_by_key(r6, r7, r8)) & 0xFFFFFFFF
    if name == "f33_poll_word_masks":
        return int(library.f33_poll_word_masks(r6, r7, r8, r9)) & 0xFFFFFFFF
    if name == "f33_clear_application_ram_4k":
        library.f33_clear_application_ram_4k()
        return None
    if name == "f33_nvm_set_physical_result_state":
        library.f33_nvm_set_physical_result_state(r6)
        return None
    if name == "f33_nvm_set_secondary_result_state":
        library.f33_nvm_set_secondary_result_state(r6)
        return None
    if name == "f33_icus20_read_bit0":
        return int(library.f33_icus20_read_bit0()) & 0xFFFFFFFF
    if name == "f33_faci_decode_completion_status":
        return int(library.f33_faci_decode_completion_status()) & 0xFFFFFFFF
    if name == "f33_nvm_lookup_byte_result":
        return int(library.f33_nvm_lookup_byte_result(r6, r7, r8)) & 0xFFFFFFFF
    if name == "f33_nvm_translate_saved_driver_result":
        return int(library.f33_nvm_translate_saved_driver_result()) & 0xFFFFFFFF
    if name == "f33_nvm_get_logical_storage_page":
        return int(library.f33_nvm_get_logical_storage_page(
            r6, pointer(view, base, r7, ctypes.POINTER(ctypes.c_uint16)),
        )) & 0xFFFFFFFF
    if name == "f33_nvm_get_direct_operation_result":
        return int(library.f33_nvm_get_direct_operation_result()) & 0xFFFFFFFF
    if name == "f33_nvm_accumulate_diagnostic_mask":
        library.f33_nvm_accumulate_diagnostic_mask(r6)
        return None
    if name == "f33_nvm_accumulate_side_status":
        library.f33_nvm_accumulate_side_status(r6)
        return None
    if name == "f33_nvm_accumulate_result_class":
        library.f33_nvm_accumulate_result_class(r6)
        return None
    if name == "f33_nvm_initialize_operation":
        library.f33_nvm_initialize_operation()
        return None
    if name == "f33_nvm_initialize_family1_application":
        library.f33_nvm_initialize_family1_application()
        return None
    if name == "f33_nvm_publish_logical_result":
        library.f33_nvm_publish_logical_result(r6, r7, r8)
        return None
    if name == "f33_nvm_unlink_queue_slot":
        library.f33_nvm_unlink_queue_slot(r6, r7, r8)
        return None
    if name == "f33_nvm_recover_family0_request_indices":
        library.f33_nvm_recover_family0_request_indices(
            pointer(view, base, r6, u8p), pointer(view, base, r7, u8p),
        )
        return None
    if name == "f33_nvm_recover_family1_request_indices":
        library.f33_nvm_recover_family1_request_indices(
            pointer(view, base, r6, u8p), pointer(view, base, r7, u8p),
        )
        return None
    if name == "f33_freshness_encode_wire":
        library.f33_freshness_encode_wire(r6, r7, r8)
        return None
    if name == "f33_freshness_decode_wire":
        library.f33_freshness_decode_wire(r6, r7, r8)
        return None
    if name == "f33_nvm_publish_family1_checksum":
        library.f33_nvm_publish_family1_checksum(r6)
        return None
    if name == "f33_pwm_initialize_compare_stages":
        library.f33_pwm_initialize_compare_stages(r6)
        return None
    if name == "f33_pwm_stage_halfword_compares":
        library.f33_pwm_stage_halfword_compares(r6, r7, r8, r9)
        return None
    if name == "f33_pwm_stage_word_compares":
        library.f33_pwm_stage_word_compares(r6, r7, r8, r9)
        return None
    if name == "f33_nvm_set_read_buffer":
        library.f33_nvm_set_read_buffer(r6, r7)
        return None
    if name == "f33_nvm_set_write_buffer":
        library.f33_nvm_set_write_buffer(r6, r7)
        return None
    if name == "f33_nvm_submit_operation":
        return int(library.f33_nvm_submit_operation(r6)) & 0xFFFFFFFF
    if name == "f33_freshness_select_reset_candidate":
        return int(library.f33_freshness_select_reset_candidate(r7, r8)) & 0xFFFFFFFF
    if name == "f33_freshness_commit_pending":
        library.f33_freshness_commit_pending(r6, r7)
        return None
    if name == "f33_freshness_reconstruct_ordinary":
        return int(library.f33_freshness_reconstruct_ordinary(r6, r7, r8, r9)) & 0xFFFFFFFF
    if name == "f33_freshness_reconstruct_candidate":
        return int(library.f33_freshness_reconstruct_candidate(r6, r7, r8, r9)) & 0xFFFFFFFF
    if name == "f33_nvm_get_family1_record":
        return int(library.f33_nvm_get_family1_record(r6, r7)) & 0xFFFFFFFF
    if name == "f33_read_repair_redundant_u8":
        return int(library.f33_read_repair_redundant_u8(r6, r7, r8, r9)) & 0xFFFFFFFF
    if name == "f33_classify_channel_residual_a":
        return int(library.f33_classify_channel_residual_a()) & 0xFFFFFFFF
    if name == "f33_nvm_submit_bulk_reads":
        return int(library.f33_nvm_submit_bulk_reads()) & 0xFFFFFFFF
    if name == "f33_nvm_step_initial_read_acquisition":
        return int(library.f33_nvm_step_initial_read_acquisition()) & 0xFFFFFFFF
    if name == "f33_nvm_step_acquisition_pass":
        return int(library.f33_nvm_step_acquisition_pass()) & 0xFFFFFFFF
    if name == "f33_nvm_run_bounded_initial_acquisition":
        library.f33_nvm_run_bounded_initial_acquisition()
        return None
    if name == "f33_check_learned_quad_bounds":
        return int(library.f33_check_learned_quad_bounds()) & 0xFFFFFFFF
    if name == "f33_update_thermal_release_envelope":
        library.f33_update_thermal_release_envelope()
        return None
    if name == "f33_update_thermal_history_qualification":
        library.f33_update_thermal_history_qualification()
        return None
    if name == "f33_nvm_initialize_queues":
        library.f33_nvm_initialize_queues()
        return None
    if name == "f33_nvm_reset_queues_notifying":
        library.f33_nvm_reset_queues_notifying()
        return None
    if name == "f33_nvm_pop_queue_head":
        return int(library.f33_nvm_pop_queue_head(r6, r7)) & 0xFFFFFFFF
    if name == "f33_nvm_enqueue_read":
        return int(library.f33_nvm_enqueue_read(r6, r7)) & 0xFFFFFFFF
    if name == "f33_nvm_enqueue_write":
        return int(library.f33_nvm_enqueue_write(r6, r7)) & 0xFFFFFFFF
    if name == "f33_nvm_set_family0_record":
        return int(library.f33_nvm_set_family0_record(r6, r7)) & 0xFFFFFFFF
    if name == "f33_dcra1_crc_raw_words":
        return int(library.f33_dcra1_crc_raw_words(r6, r7, r8)) & 0xFFFFFFFF
    if name == "f33_nvm_get_family2_rom_record":
        return int(library.f33_nvm_get_family2_rom_record(r6, r7)) & 0xFFFFFFFF
    if name == "f33_nvm_get_record":
        return int(library.f33_nvm_get_record(r6, r7)) & 0xFFFFFFFF
    if name == "f33_publish_learned_quad":
        library.f33_publish_learned_quad()
        return None
    if name == "f33_restore_learned_quad":
        return int(library.f33_restore_learned_quad()) & 0xFFFFFFFF
    if name == "f33_curve16_interpolate_with_slope":
        return int(library.f33_curve16_interpolate_with_slope(r6, r7, r8)) & 0xFFFFFFFF
    if name == "f33_force_unconfirmed_terminal_monitor_healthy":
        return int(library.f33_force_unconfirmed_terminal_monitor_healthy(r6, r7, r8)) & 0xFFFFFFFF
    if name == "f33_priority_mask_enter":
        return int(library.f33_priority_mask_enter(r6)) & 0xFFFFFFFF
    if name == "f33_dataflash_copy_words_ecc":
        return int(library.f33_dataflash_copy_words_ecc(r6, r7, r8)) & 0xFFFFFFFF
    if name == "f33_priority_mask_restore":
        library.f33_priority_mask_restore(r6)
        return None
    if name in VALUE_RETURN:
        return int(getattr(library, name)(r6)) & 0xFFFFFFFF
    raise AssertionError(f"no C call for {name}")


def parse_signature(signature: str, name: str) -> tuple[str, list[str]]:
    opening = signature.find("(")
    closing = signature.rfind(")")
    if opening < 0 or closing < opening or name not in signature[:opening]:
        raise AssertionError(f"unparsed signature for {name}")
    return_type = " ".join(signature[:opening].replace(name, "").split())
    body = signature[opening + 1:closing].strip()
    if body in {"", "void"}:
        return return_type, []
    params: list[str] = []
    depth = 0
    start = 0
    for index, char in enumerate(body):
        if char == "(":
            depth += 1
        elif char == ")":
            depth -= 1
        elif char == "," and depth == 0:
            params.append(body[start:index].strip())
            start = index + 1
    params.append(body[start:].strip())
    return return_type, params


def load_pmr(library: ctypes.CDLL, registers: dict) -> None:
    ctypes.c_uint32.in_dll(library, "camry_pmr").value = int(registers.get("PMR", "0"), 16) & 0xFFFFFFFF


def with_pmr(library: ctypes.CDLL, registers: dict) -> dict:
    observed = dict(registers)
    observed["PMR"] = f"{ctypes.c_uint32.in_dll(library, 'camry_pmr').value:#x}"
    return observed


def call_corpus(library: ctypes.CDLL, name: str, signature: str, registers: dict) -> int | None:
    ctypes.c_uint32.in_dll(library, "camry_gp").value = int(registers.get("gp", "0"), 16) & 0xFFFFFFFF
    ctypes.c_uint32.in_dll(library, "camry_tp").value = int(registers.get("tp", "0"), 16) & 0xFFFFFFFF
    ctypes.c_uint32.in_dll(library, "camry_sp").value = int(registers.get("sp", "0"), 16) & 0xFFFFFFFF
    load_pmr(library, registers)
    return_type, params = parse_signature(signature, name)
    if len(params) > 4:
        raise AssertionError(f"{name} has stack arguments")
    values = [
        int(registers.get(f"r{6 + index}", "0"), 16) & 0xFFFFFFFF
        for index in range(len(params))
    ]
    u8p = ctypes.POINTER(ctypes.c_uint8)
    u32 = ctypes.c_uint32
    argtypes = []
    args = []
    for param, value in zip(params, values):
        if "*" in param:
            argtypes.append(u8p)
            args.append(library.camry_host_ptr(value))
        else:
            argtypes.append(u32)
            args.append(value)
    function = getattr(library, name)
    function.argtypes = argtypes
    if return_type == "void":
        function.restype = None
        function(*args)
        return None
    function.restype = u32
    return int(function(*args)) & 0xFFFFFFFF


def corpus_returns(form: str | None, name: str) -> bool | None:
    if form == "lifted":
        return True
    if form != "corpus":
        return None
    return_type, _params = parse_signature(SIGNATURES[name], name)
    return return_type != "void"


def call_matched(
    library: ctypes.CDLL,
    form: str | None,
    address: int,
    name: str,
    registers: dict,
    limit: int,
    view,
    base: int,
) -> int | None:
    if form == "lifted":
        return call_lifted(library, address, registers, limit)
    if form == "corpus":
        return call_corpus(library, name, SIGNATURES[name], registers)
    return call_function(library, name, view, base, registers)


def call_lifted(library: ctypes.CDLL, address: int, registers: dict, limit: int) -> int:
    ctypes.c_uint32.in_dll(library, "camry_gp").value = int(registers.get("gp", "0"), 16) & 0xFFFFFFFF
    ctypes.c_uint32.in_dll(library, "camry_tp").value = int(registers.get("tp", "0"), 16) & 0xFFFFFFFF
    ctypes.c_uint32.in_dll(library, "camry_sp").value = int(registers.get("sp", "0"), 16) & 0xFFFFFFFF
    load_pmr(library, registers)
    ctypes.c_uint32.in_dll(library, "camry_step_limit").value = limit
    ctypes.c_uint32.in_dll(library, "camry_lift_psw").value = int(registers.get("PSW", "0x20"), 16) & 0xFFFFFFFF
    return int(library.camry_lift_run(
        address,
        int(registers.get("r6", "0"), 16),
        int(registers.get("r7", "0"), 16),
        int(registers.get("r8", "0"), 16),
        int(registers.get("r9", "0"), 16),
        int(registers.get("lp", "0"), 16),
    )) & 0xFFFFFFFF


def attach_dcra_window(library: ctypes.CDLL):
    window = bytearray(DCRA1_SIZE)
    view = view_of(window)
    library.camry_host_add(
        DCRA1_BASE,
        ctypes.cast(view, ctypes.POINTER(ctypes.c_uint8)),
        DCRA1_SIZE,
    )
    return window, view


def attach_dcra(library: ctypes.CDLL, name: str):
    if name not in DCRA_CALLS:
        return None, None
    return attach_dcra_window(library)


def check_results(
    scenario: dict,
    name: str,
    image: bytearray | None,
    base: int,
    registers: dict,
    returned: int | None,
    regions: list[tuple[int, bytearray]] | None = None,
    codeflash: bytes | None = None,
    dcra: bytearray | None = None,
    value_return: bool | None = None,
) -> None:
    memory_checks = 0
    r10_checks = 0
    for check in scenario["checks"]:
        kind = check["kind"]
        if kind == "register":
            register = check["register"]
            expected = int(check["equals"], 16)
            if register in {"sp", "PC"}:
                continue
            if register == "r10" and name in POINTER_RETURN:
                r10_checks += 1
                destination = int(registers["r6"], 16)
                if expected == destination:
                    if returned != 1:
                        raise AssertionError(f"{scenario['name']}: memcpy did not return destination")
                elif expected <= 0xFFFF and returned != expected:
                    raise AssertionError(f"{scenario['name']}: r10 {returned} != {expected:#x}")
                continue
            r10_is_return = name in VALUE_RETURN if value_return is None else value_return
            if register == "r10" and r10_is_return:
                r10_checks += 1
                if returned != expected:
                    raise AssertionError(f"{scenario['name']}: r10 {returned:#x} != {expected:#x}")
                continue
            actual = int(registers.get(register, "0"), 16)
            if actual != expected:
                raise AssertionError(
                    f"{scenario['name']}: preserved {register} {actual:#x} != {expected:#x}"
                )
            continue
        if kind not in {"memory", "memory-equal"}:
            continue
        memory_checks += 1
        address = int(check["address"], 16)
        size = check["size"]
        if dcra is not None and DCRA1_BASE <= address and address + size <= DCRA1_BASE + len(dcra):
            actual = bytes(dcra[address - DCRA1_BASE : address - DCRA1_BASE + size])
        elif regions is not None:
            actual = read_regions(regions, address, size)
        else:
            actual = bytes(image[address - base : address - base + size])
        if kind == "memory-equal":
            source = int(check["source_address"], 16)
            if codeflash is not None and source + size <= len(codeflash):
                expected = codeflash[source : source + size]
            elif regions is not None:
                expected = read_regions(regions, source, size)
            else:
                expected = bytes(image[source - base : source - base + size])
        else:
            expected = bytes.fromhex(check["equals_hex"])
        if actual != expected:
            raise AssertionError(f"{scenario['name']}: {check['name']} mismatch")
    if memory_checks == 0 and r10_checks == 0:
        raise AssertionError(f"{scenario['name']}: no memory or r10 check")


def check_rom(library: ctypes.CDLL) -> None:
    metadata = resolve_target("camry-8965F3307000")[1]
    image = (REPO_ROOT / metadata["codeflash"]).read_bytes()
    for name, address, size in ROM_TABLES:
        actual = bytes((ctypes.c_uint8 * size).in_dll(library, name))
        if actual != image[address : address + size]:
            raise SystemExit(f"{name} drifted from CodeFlash {address:#x}")
    for name, address in ROM_BYTES:
        actual = ctypes.c_uint8.in_dll(library, name).value
        if actual != image[address]:
            raise SystemExit(f"{name} drifted from CodeFlash {address:#x}")


def _returns_value(signature: str, name: str) -> bool:
    return_type, _params = parse_signature(signature, name)
    return return_type != "void"


def _run_corpus_scenario(library, scenario, name, signature, codeflash: bytes) -> None:
    registers = scenario.get("registers", {})
    mapped = materialize(scenario)
    code_view = view_of(bytearray(codeflash))
    value_return = _returns_value(signature, name)
    if mapped is None:
        regions = scenario_regions(scenario)
        install_regions(library, code_view, len(codeflash), regions)
        returned = call_corpus(library, name, signature, registers)
        check_results(
            scenario, name, None, 0, with_pmr(library, registers), returned, regions, codeflash,
            value_return=value_return,
        )
        return
    memory, base = mapped
    view = view_of(memory) if memory else view_of(bytearray(b"\x00"))
    install_address_space(library, code_view, len(codeflash), view, base, memory)
    returned = call_corpus(library, name, signature, registers)
    check_results(
        scenario, name, memory, base, with_pmr(library, registers), returned, codeflash=codeflash,
        value_return=value_return,
    )


def screen_corpus(rows: list[dict]) -> list[dict]:
    """Return compiled corpus rows whose useful oracles all pass."""
    by_address = {int(row["addr"]): row for row in rows}
    grouped: dict[int, list[dict]] = {addr: [] for addr in by_address}
    for scenario in load_oracles():
        entry = scenario.get("entry") or {}
        if entry.get("scope") != "resolved-address" or not useful_oracle(scenario):
            continue
        address = int(entry["address"], 16)
        if address in grouped:
            grouped[address].append(scenario)
    metadata = resolve_target("camry-8965F3307000")[1]
    codeflash = (REPO_ROOT / metadata["codeflash"]).read_bytes()
    passed = []
    with tempfile.TemporaryDirectory(prefix="camry-corpus-") as directory:
        library = compile_sources(Path(directory))
        bind(library)
        for address, row in sorted(by_address.items()):
            scenarios = grouped[address]
            if not scenarios:
                continue
            ok = True
            for scenario in scenarios:
                read_fd, write_fd = os.pipe()
                pid = os.fork()
                if pid == 0:
                    os.close(read_fd)
                    signal.signal(signal.SIGALRM, lambda *_args: os._exit(1))
                    signal.alarm(2)
                    try:
                        _run_corpus_scenario(
                            library, scenario, row["name"], row["signature"], codeflash,
                        )
                    except BaseException as exc:
                        os.write(write_fd, str(exc).encode()[:400])
                        os._exit(1)
                    os._exit(0)
                os.close(write_fd)
                _pid, status = os.waitpid(pid, 0)
                detail = os.read(read_fd, 400).decode(errors="replace")
                os.close(read_fd)
                if not (os.WIFEXITED(status) and os.WEXITSTATUS(status) == 0):
                    ok = False
                    print(f"FAIL {row['name']} {scenario['name']} {detail}")
                    break
            if ok:
                passed.append(row)
                print(f"PASS {row['name']} {address:#x} {len(scenarios)}")
    return passed


def main() -> int:
    image, report = identity_image(load_symbols())
    if hashlib_matches(image, report):
        print(
            f"PASS identity: {report['functions']} functions, "
            f"{report['function_bytes']} function bytes, "
            f"{report['gap_bytes']} gap bytes"
        )
    matched = {int(row["addr"], 16): row for row in load_matched()}
    symbol_names = {int(row["addr"], 16): row["name"] for row in load_symbols()}
    for address, row in matched.items():
        if symbol_names.get(address) != row["name"]:
            raise SystemExit(f"matched name drift at {row['addr']}")
        if row["status"] not in {"equivalent", "byte-matched"}:
            raise SystemExit(f"unknown match status {row['status']}")
    executed = {address: 0 for address in matched}
    metadata = resolve_target("camry-8965F3307000")[1]
    codeflash = bytearray((REPO_ROOT / metadata["codeflash"]).read_bytes())
    with tempfile.TemporaryDirectory(prefix="camry-decomp-") as directory:
        library = compile_sources(Path(directory))
        bind(library)
        check_rom(library)
        print("PASS rom tables match CodeFlash")
        code_view = view_of(codeflash)
        for scenario in load_oracles():
            entry = scenario.get("entry", {})
            if entry.get("scope") != "resolved-address":
                continue
            address = int(entry["address"], 16)
            if address not in matched or not useful_oracle(scenario):
                continue
            name = matched[address]["name"]
            form = matched[address].get("form")
            lifted = form == "lifted"
            corpus = form == "corpus"
            registers = scenario.get("registers", {})
            mapped = materialize(scenario)
            ranges = [] if lifted or corpus else accessed_ranges(name, registers)
            limit = int(scenario.get("max_instructions") or 200000)
            if mapped is None:
                if ranges:
                    continue
                regions = scenario_regions(scenario)
                held = install_regions(library, code_view, len(codeflash), regions)
                dcra, dcra_view = attach_dcra(library, name)
                if lifted and dcra is None and 1 + len(regions) < 8:
                    dcra, dcra_view = attach_dcra_window(library)
                returned = call_matched(
                    library, form, address, name, registers, limit, None, 0,
                )
                check_results(
                    scenario, name, None, 0, with_pmr(library, registers), returned, regions, codeflash, dcra,
                    value_return=corpus_returns(form, name) if corpus or lifted else None,
                )
                del held, dcra_view
            else:
                memory, base = mapped
                if any(not covers(base, len(memory), start, length) for start, length in ranges):
                    continue
                view = view_of(memory) if memory else view_of(bytearray(b"\x00"))
                install_address_space(library, code_view, len(codeflash), view, base, memory)
                dcra, dcra_view = attach_dcra(library, name)
                if lifted and dcra is None:
                    dcra, dcra_view = attach_dcra_window(library)
                returned = call_matched(
                    library, form, address, name, registers, limit, view, base,
                )
                check_results(
                    scenario, name, memory, base, with_pmr(library, registers), returned, codeflash=codeflash, dcra=dcra,
                    value_return=corpus_returns(form, name) if corpus or lifted else None,
                )
                del dcra_view
            executed[address] += 1
            print(f"PASS {name} {scenario['name']}")
    missing = [row["name"] for address, row in matched.items() if executed[address] == 0]
    if missing:
        raise SystemExit("matched functions with no executed oracle: " + ", ".join(missing))
    print(f"PASS matched functions: {len(matched)}")
    return 0


def hashlib_matches(image: bytes, report: dict) -> bool:
    import hashlib
    if hashlib.sha256(image).hexdigest() != report["codeflash_sha256"]:
        raise SystemExit("identity image hash drift")
    return True


if __name__ == "__main__":
    raise SystemExit(main())
