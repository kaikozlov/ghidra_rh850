"""Native compilation, object caching, and ctypes bindings."""
from __future__ import annotations

import ctypes
import hashlib
import os
import re
import subprocess
import sys
from pathlib import Path

from tools import REPO_ROOT

from ..tree import ROOT, load_symbols
from ..sources import retained_paths
from ..bindings import write_gap_thunks, write_indirect_table


INCLUDE = ROOT / "include"


HOST_MEM = Path(__file__).with_name("host_memory.c")
HOST_CPU = Path(__file__).with_name("host_cpu.c")
C_FLAGS = (
    "-std=c11", "-Wall", "-Wextra", "-Werror", "-fwrapv",
    "-ferror-limit=0",
    "-Wno-unused-variable", "-Wno-unused-parameter",
    "-Wno-unused-function", "-Wno-unused-label",
    "-Wno-pointer-to-int-cast", "-Wno-int-to-pointer-cast",
    "-Wno-bitwise-op-parentheses", "-Wno-sign-compare", "-Wno-parentheses",
    "-Wno-pointer-sign", "-Wno-incompatible-pointer-types",
    "-Wno-unused-but-set-variable",
    "-Wno-uninitialized", "-Wno-deprecated-non-prototype",
    "-DCAMRY_HOST",
)


# Hand-written native leaves expose the ABI declared here, which can differ
# from a decompiler's pointer guesses for 32-bit firmware-address parameters.
NATIVE_SIGNATURES = {
    match.group(2): match.group(1)
    for match in re.finditer(
        r"(?m)^((?:void|int|u?int(?:8|16|32|64)_t)\s+(?:\*\s*)?"
        r"([A-Za-z_]\w*)\s*\([^;{}]*\))\s*;",
        (INCLUDE / "camry.h").read_text(encoding="utf-8"),
    )
}


def _header_stamp() -> bytes:
    """Bytes of the headers a shard includes, so an edit misses the object cache."""
    digest = hashlib.sha256()
    for path in [*sorted(INCLUDE.glob("*.h")), HOST_CPU.with_suffix(".h")]:
        digest.update(path.name.encode())
        digest.update(path.read_bytes())
    return digest.digest()


def _compile_object(source: Path, flags: list[str], stamp: bytes) -> tuple[Path | None, str]:
    """Compile one translation unit, reusing the object when its inputs match."""
    digest = hashlib.sha256()
    digest.update(b"\0".join(item.encode() for item in flags))
    digest.update(stamp)
    digest.update(source.read_bytes())
    key = digest.hexdigest()[:24]
    cache = REPO_ROOT / "build" / "cache" / "camry-verify"
    cache.mkdir(parents=True, exist_ok=True)
    obj = cache / f"{key}.o"
    if obj.is_file() and obj.stat().st_size > 0:
        return obj, ""
    temporary = cache / f".{key}.{os.getpid()}.o"
    result = subprocess.run(
        ["cc", *flags, "-c", "-o", str(temporary), str(source)],
        check=False,
        text=True,
        capture_output=True,
    )
    if result.returncode != 0:
        if temporary.exists():
            temporary.unlink()
        return None, result.stderr or result.stdout
    os.replace(temporary, obj)
    return obj, ""


def compile_sources(
    directory: Path, optimize: str = "-O2", *, lifted: Path | None = None,
) -> ctypes.CDLL:
    library = directory / "libcamry.dylib"
    sources = sorted((ROOT / "src").glob("*.c"))
    from .host_rewrite import rewrite_host_translation_unit

    addresses = {row["name"]: int(row["addr"], 16) for row in load_symbols()}
    for retained in retained_paths():
        original = retained.read_text(encoding="utf-8")
        rewritten = rewrite_host_translation_unit(original, addresses)
        if rewritten != original:
            copy = directory / f"retained_{retained.name}"
            copy.write_text(rewritten, encoding="utf-8")
            sources.append(copy)
        else:
            sources.append(retained)
    if lifted is not None:
        sources.append(lifted)
    table = directory / "indirect_table.c"
    gaps = directory / "gap_thunks.c"
    write_indirect_table(table, sources)
    write_gap_thunks(gaps)
    sources = [*sources, table, gaps, HOST_MEM, HOST_CPU]
    # One compile reports every diagnostic. A shard whose inputs are unchanged
    # is the cached object; the link is the only step that runs again.
    flags = [
        optimize, *C_FLAGS,
        "-I", str(INCLUDE),
        "-I", str(HOST_CPU.parent),
    ]
    stamp = _header_stamp()
    objects: list[Path] = []
    logs: list[str] = []
    for source in sources:
        obj, log = _compile_object(source, flags, stamp)
        if obj is None:
            logs.append(log)
        else:
            objects.append(obj)
    if logs:
        sys.stderr.write("\n".join(logs))
        raise SystemExit(1)
    result = subprocess.run(
        ["cc", "-dynamiclib", "-o", str(library), *[str(path) for path in objects]],
        check=False,
        text=True,
        capture_output=True,
    )
    if result.returncode != 0:
        sys.stderr.write(result.stderr or result.stdout)
        raise SystemExit(result.returncode)
    return ctypes.CDLL(library)


def bind(library: ctypes.CDLL, *, lifted: bool = False) -> None:
    u8p = ctypes.POINTER(ctypes.c_uint8)
    u32p = ctypes.POINTER(ctypes.c_uint32)
    u32 = ctypes.c_uint32
    library.memcpy_forward.argtypes = [u8p, u8p, u32]
    library.memcpy_forward.restype = u8p
    library.memzero.argtypes = [u8p, u32]
    library.memzero.restype = None
    library.copy_whole_words.argtypes = [u32p, u32p, ctypes.c_uint16]
    library.copy_whole_words.restype = None
    library.update_whole_words.argtypes = [u32p, u32p, ctypes.c_uint16]
    library.update_whole_words.restype = u32
    library.load_u8.argtypes = [u8p]
    library.load_u8.restype = u32
    library.load_u16.argtypes = [u8p]
    library.load_u16.restype = u32
    library.store_u8.argtypes = [u8p, u32]
    library.store_u8.restype = None
    library.store_u16.argtypes = [u8p, u32]
    library.store_u16.restype = None
    library.store_u32.argtypes = [u8p, u32]
    library.store_u32.restype = None
    library.nvm_sum_bytes.argtypes = [u32, u8p]
    library.nvm_sum_bytes.restype = u32
    library.nvm_family0_chunk_cost.argtypes = [u32]
    library.nvm_family0_chunk_cost.restype = u32
    library.scale_u16_delta_s16_x4.argtypes = [u32, u32, u32]
    library.scale_u16_delta_s16_x4.restype = u32
    library.priority_mask_enter.argtypes = [u32]
    library.priority_mask_enter.restype = u32
    library.dataflash_copy_words_ecc.argtypes = [u32, u32, u32]
    library.dataflash_copy_words_ecc.restype = u32
    library.priority_mask_restore.argtypes = [u32]
    library.priority_mask_restore.restype = None
    for name in (
        "nvm_payload_length",
        "nvm_base_offset",
        "nvm_payload_page_count",
        "nvm_trailer_offset",
        "nvm_storage_handle",
        "nvm_advance_family0_request_index",
        "nvm_advance_family1_request_index",
        "nvm_erase_base_record_allocation_77982",
    ):
        getattr(library, name).argtypes = [u32]
        getattr(library, name).restype = u32
    library.nvm_record_offset.argtypes = [u32, u32, u32]
    library.nvm_record_offset.restype = u32
    library.nvm_payload_chunk_length.argtypes = [u32, u32]
    library.nvm_payload_chunk_length.restype = u32
    library.nvm_probe_range_rejected.argtypes = [u32, u32]
    library.nvm_probe_range_rejected.restype = u32
    library.lookup_u32_value_by_key.argtypes = [u32, u32, u32]
    library.lookup_u32_value_by_key.restype = u32
    library.poll_word_masks.argtypes = [u32, u32, u32, u32]
    library.poll_word_masks.restype = u32
    library.clear_application_ram_4k.argtypes = []
    library.clear_application_ram_4k.restype = None
    library.nvm_set_physical_result_state.argtypes = [u32]
    library.nvm_set_physical_result_state.restype = None
    library.nvm_set_secondary_result_state.argtypes = [u32]
    library.nvm_set_secondary_result_state.restype = None
    library.icus20_read_bit0.argtypes = []
    library.icus20_read_bit0.restype = u32
    library.faci_decode_completion_status.argtypes = []
    library.faci_decode_completion_status.restype = u32
    library.nvm_lookup_byte_result.argtypes = [u32, u32, u32]
    library.nvm_lookup_byte_result.restype = u32
    library.nvm_translate_read_driver_result.argtypes = [u32]
    library.nvm_translate_read_driver_result.restype = u32
    library.nvm_translate_saved_driver_result.argtypes = []
    library.nvm_translate_saved_driver_result.restype = u32
    library.nvm_get_logical_storage_page.argtypes = [u32, ctypes.POINTER(ctypes.c_uint16)]
    library.nvm_get_logical_storage_page.restype = u32
    library.nvm_get_direct_operation_result.argtypes = []
    library.nvm_get_direct_operation_result.restype = u32
    library.nvm_accumulate_diagnostic_mask.argtypes = [u32]
    library.nvm_accumulate_diagnostic_mask.restype = None
    library.nvm_accumulate_side_status.argtypes = [u32]
    library.nvm_accumulate_side_status.restype = None
    library.nvm_accumulate_result_class.argtypes = [u32]
    library.nvm_accumulate_result_class.restype = None
    library.nvm_initialize_operation.argtypes = []
    library.nvm_initialize_operation.restype = None
    library.nvm_unlink_queue_slot.argtypes = [u32, u32, u32]
    library.nvm_unlink_queue_slot.restype = None
    library.nvm_recover_family0_request_indices.argtypes = [u8p, u8p]
    library.nvm_recover_family0_request_indices.restype = None
    library.nvm_recover_family1_request_indices.argtypes = [u8p, u8p]
    library.nvm_recover_family1_request_indices.restype = None
    library.freshness_encode_wire.argtypes = [u32, u32, u32]
    library.freshness_encode_wire.restype = None
    library.freshness_decode_wire.argtypes = [u32, u32, u32]
    library.freshness_decode_wire.restype = None
    library.nvm_check_family1_checksum.argtypes = [u32]
    library.nvm_check_family1_checksum.restype = u32
    library.nvm_retain_token_while_reads_pending.argtypes = [u32]
    library.nvm_retain_token_while_reads_pending.restype = u32
    library.nvm_publish_family1_checksum.argtypes = [u32]
    library.nvm_publish_family1_checksum.restype = None
    library.pwm_initialize_compare_stages.argtypes = [u32]
    library.pwm_initialize_compare_stages.restype = None
    library.pwm_stage_halfword_compares.argtypes = [u32, u32, u32, u32]
    library.pwm_stage_halfword_compares.restype = None
    library.pwm_stage_word_compares.argtypes = [u32, u32, u32, u32]
    library.pwm_stage_word_compares.restype = None
    library.nvm_set_read_buffer.argtypes = [u32, u32]
    library.nvm_set_read_buffer.restype = None
    library.nvm_set_write_buffer.argtypes = [u32, u32]
    library.nvm_set_write_buffer.restype = None
    library.nvm_submit_operation.argtypes = [u32]
    library.nvm_submit_operation.restype = u32
    library.freshness_select_reset_candidate.argtypes = [u32, u32]
    library.freshness_select_reset_candidate.restype = u32
    library.freshness_commit_pending.argtypes = [u32, u32]
    library.freshness_commit_pending.restype = None
    library.freshness_reconstruct_ordinary.argtypes = [u32, u32, u32, u32]
    library.freshness_reconstruct_ordinary.restype = u32
    library.freshness_reconstruct_candidate.argtypes = [u32, u32, u32, u32]
    library.freshness_reconstruct_candidate.restype = u32
    library.nvm_get_family1_record.argtypes = [u32, u32]
    library.nvm_get_family1_record.restype = u32
    library.nvm_get_family1_status.argtypes = [u32]
    library.nvm_get_family1_status.restype = u32
    library.nvm_get_family2_status.argtypes = [u32]
    library.nvm_get_family2_status.restype = u32
    library.nvm_initialize_family1_application.argtypes = []
    library.nvm_initialize_family1_application.restype = None
    library.nvm_publish_logical_result.argtypes = [u32, u32, u32]
    library.nvm_publish_logical_result.restype = None
    library.read_repair_redundant_u8.argtypes = [u32, u32, u32, u32]
    library.read_repair_redundant_u8.restype = u32
    library.classify_channel_residual_a.argtypes = []
    library.classify_channel_residual_a.restype = u32
    library.check_learned_quad_bounds.argtypes = []
    library.check_learned_quad_bounds.restype = u32
    library.nvm_enqueue_family0_read.argtypes = [u32]
    library.nvm_enqueue_family0_read.restype = u32
    library.nvm_set_family0_record.argtypes = [u32, u32]
    library.nvm_set_family0_record.restype = u32
    library.dcra1_crc_raw_words.argtypes = [u32, u32, u32]
    library.dcra1_crc_raw_words.restype = u32
    library.nvm_check_family2_rom_crc.argtypes = [u32]
    library.nvm_check_family2_rom_crc.restype = u32
    library.nvm_get_family2_rom_record.argtypes = [u32, u32]
    library.nvm_get_family2_rom_record.restype = u32
    library.nvm_get_record.argtypes = [u32, u32]
    library.nvm_get_record.restype = u32
    library.nvm_refresh_family2_record_status.argtypes = [u32]
    library.nvm_refresh_family2_record_status.restype = u32
    library.publish_learned_quad.argtypes = []
    library.publish_learned_quad.restype = None
    library.restore_learned_quad.argtypes = []
    library.restore_learned_quad.restype = u32
    library.curve16_interpolate_with_slope.argtypes = [u32, u32, u32]
    library.curve16_interpolate_with_slope.restype = u32
    library.update_thermal_release_envelope.argtypes = []
    library.update_thermal_release_envelope.restype = None
    library.update_thermal_history_qualification.argtypes = []
    library.update_thermal_history_qualification.restype = None
    library.nvm_initialize_queues.argtypes = []
    library.nvm_initialize_queues.restype = None
    library.nvm_reset_queues_notifying.argtypes = []
    library.nvm_reset_queues_notifying.restype = None
    library.nvm_pop_queue_head.argtypes = [u32, u32]
    library.nvm_pop_queue_head.restype = u32
    library.nvm_enqueue_read.argtypes = [u32, u32]
    library.nvm_enqueue_read.restype = u32
    library.nvm_enqueue_write.argtypes = [u32, u32]
    library.nvm_enqueue_write.restype = u32
    library.nvm_arm_family0_read.argtypes = [u32]
    library.nvm_arm_family0_read.restype = u32
    library.nvm_arm_family0_write.argtypes = [u32]
    library.nvm_arm_family0_write.restype = u32
    library.nvm_submit_family1_read_copies.argtypes = [u32]
    library.nvm_submit_family1_read_copies.restype = u32
    library.nvm_submit_family1_write_copies.argtypes = [u32]
    library.nvm_submit_family1_write_copies.restype = u32
    library.nvm_submit_bulk_reads.argtypes = []
    library.nvm_submit_bulk_reads.restype = u32
    library.nvm_step_initial_read_acquisition.argtypes = []
    library.nvm_step_initial_read_acquisition.restype = u32
    library.nvm_step_acquisition_pass.argtypes = []
    library.nvm_step_acquisition_pass.restype = u32
    library.nvm_run_bounded_initial_acquisition.argtypes = []
    library.nvm_run_bounded_initial_acquisition.restype = None
    library.force_unconfirmed_terminal_monitor_healthy.argtypes = [u32, u32, u32]
    library.force_unconfirmed_terminal_monitor_healthy.restype = u32
    library.nvm_read_buffer.argtypes = [u32]
    library.nvm_read_buffer.restype = u32
    library.nvm_write_buffer.argtypes = [u32]
    library.nvm_write_buffer.restype = u32
    library.camry_host_reset.argtypes = []
    library.camry_host_reset.restype = None
    library.camry_host_add.argtypes = [u32, u8p, u32]
    library.camry_host_add.restype = None
    if lifted:
        library.camry_lift_run.argtypes = [u32, u32, u32, u32, u32, u32]
        library.camry_lift_run.restype = u32
    library.camry_host_ptr.argtypes = [u32]
    library.camry_host_ptr.restype = u8p


