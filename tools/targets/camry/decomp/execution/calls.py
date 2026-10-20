"""Native ABI, register arguments, invocation, and retained input timing."""
from __future__ import annotations

import ctypes
import hashlib
import json
import re
import tempfile
from pathlib import Path

from tools import REPO_ROOT
from tools.project.analysis_target import target as resolve_target

from .. import c_text
from ..tree import SYSTEM_REGISTERS, load_oracles, load_symbols
from .build import NATIVE_SIGNATURES
from .memory import MEMORY_MODEL_SHA256, MACHINE_REGISTERS, configure_native_model, pointer


SIGNATURES = {
    row["name"]: row["signature"]
    for row in load_symbols()
    if row.get("signature")
}


# r10 is the C return value. memcpy returns the destination pointer.
POINTER_RETURN = {"memcpy_forward"}


VALUE_RETURN = {
    "update_whole_words",
    "load_u8",
    "load_u16",
    "nvm_sum_bytes",
    "nvm_family0_chunk_cost",
    "scale_u16_delta_s16_x4",
    "nvm_payload_length",
    "nvm_base_offset",
    "nvm_payload_page_count",
    "nvm_trailer_offset",
    "nvm_storage_handle",
    "nvm_get_logical_storage_page",
    "nvm_advance_family0_request_index",
    "nvm_advance_family1_request_index",
    "nvm_allocation_pages",
    "nvm_record_offset",
    "nvm_payload_chunk_length",
    "nvm_get_family0_status",
    "nvm_get_family1_completion",
    "nvm_get_family1_record",
    "nvm_get_family1_status",
    "nvm_get_family2_status",
    "read_repair_redundant_u8",
    "nvm_check_family1_checksum",
    "nvm_retain_token_while_reads_pending",
    "force_unconfirmed_terminal_monitor_healthy",
    "freshness_select_reset_candidate",
    "freshness_reconstruct_ordinary",
    "freshness_reconstruct_candidate",
    "nvm_probe_range_rejected",
    "nvm_translate_diagnostic_mask",
    "lookup_u32_value_by_key",
    "poll_word_masks",
    "icus20_read_bit0",
    "nvm_translate_read_driver_result",
    "nvm_translate_saved_driver_result",
    "nvm_get_direct_operation_result",
    "nvm_read_buffer",
    "nvm_write_buffer",
    "nvm_submit_operation",
    "classify_channel_residual_a",
    "curve16_interpolate_with_slope",
    "check_learned_quad_bounds",
    "nvm_enqueue_family0_read",
    "nvm_set_family0_record",
    "dcra1_crc_raw_words",
    "nvm_check_family2_rom_crc",
    "nvm_get_family2_rom_record",
    "nvm_get_record",
    "nvm_refresh_family2_record_status",
    "restore_learned_quad",
    "nvm_pop_queue_head",
    "nvm_enqueue_read",
    "nvm_enqueue_write",
    "nvm_arm_family0_read",
    "nvm_arm_family0_write",
    "nvm_submit_family1_read_copies",
    "nvm_submit_family1_write_copies",
    "nvm_submit_bulk_reads",
    "nvm_step_initial_read_acquisition",
    "nvm_step_acquisition_pass",
    "nvm_erase_base_record_allocation_77982",
    "faci_decode_completion_status",
    "priority_mask_enter",
    "dataflash_copy_words_ecc",
}


def call_expected_fault(library: ctypes.CDLL, function, args: list | tuple, scenario: dict):
    expected = scenario["expected_fault"]
    if len(args) > 4:
        raise AssertionError(f"{scenario['name']}: expected-fault root exceeds register ABI")
    values = [
        ctypes.cast(value, ctypes.c_void_p).value or 0
        if isinstance(value, ctypes._Pointer) else int(value)
        for value in args
    ]
    word = ctypes.c_size_t
    arguments = (word * len(values))(*values)
    library.camry_host_fault_call.argtypes = [
        ctypes.c_void_p, ctypes.POINTER(word), ctypes.c_uint32,
    ]
    library.camry_host_fault_call.restype = None
    # The return is deliberately discarded: a successful return is a missing
    # fault, and no result exists when the native bus operation faults.
    library.camry_host_fault_call(ctypes.cast(function, ctypes.c_void_p), arguments, len(values))
    raw_kind = ctypes.c_char_p.in_dll(library, "camry_host_fault_kind").value
    actual_kind = raw_kind.decode() if raw_kind else None
    address = ctypes.c_uint32.in_dll(library, "camry_host_fault_address").value
    write = ctypes.c_uint32.in_dll(library, "camry_host_fault_write").value
    expected_address = expected.get("address")
    if expected_address is None:
        name = function.__name__
        if name.startswith(("store_u", "load_u")):
            expected_address = scenario["registers"]["r6"]
        elif name == "faci_submit_range_command":
            expected_address = "0xFFA20000"
        else:
            raise AssertionError(f"{scenario['name']}: no exact fault address contract for {name}")
    actual_access = "write" if write else "read"
    expected_access = expected.get("access") or (
        "write" if function.__name__.startswith("store_u")
        or function.__name__ == "faci_submit_range_command" else "read"
    )
    if (actual_kind != expected["kind"] or address != int(expected_address, 16)
            or actual_access != expected_access):
        raise AssertionError(
            f"{scenario['name']}: native fault {actual_kind} at {address:#x} {actual_access}"
            f" != {expected['kind']} at {expected_address} {expected_access}"
        )
    return 0


def call_function(library: ctypes.CDLL, name: str, registers: dict, scenario: dict | None = None) -> int | None:
    configure_native_model(library, scenario)
    r6 = int(registers.get("r6", "0"), 16)
    r7 = int(registers.get("r7", "0"), 16)
    r8 = int(registers.get("r8", "0"), 16)
    r9 = int(registers.get("r9", "0"), 16)
    ctypes.c_uint32.in_dll(library, "camry_gp").value = int(registers.get("gp", "0"), 16) & 0xFFFFFFFF
    ctypes.c_uint32.in_dll(library, "camry_tp").value = int(registers.get("tp", "0"), 16) & 0xFFFFFFFF
    ctypes.c_uint32.in_dll(library, "camry_sp").value = int(registers.get("sp", "0"), 16) & 0xFFFFFFFF
    load_registers(library, registers)
    u8p = ctypes.POINTER(ctypes.c_uint8)
    u32p = ctypes.POINTER(ctypes.c_uint32)

    def host(function, *args):
        converted = list(args)
        for index, kind in enumerate(function.argtypes or []):
            if index < len(args) and isinstance(args[index], int) and issubclass(kind, ctypes._Pointer):
                converted[index] = pointer(library, args[index], kind)
        if scenario and scenario.get("expected_fault"):
            return call_expected_fault(library, function, converted, scenario)
        return function(*converted)

    if name == "memcpy_forward":
        dest_ptr = pointer(library, r6, u8p)
        result = host(library.memcpy_forward, dest_ptr, pointer(library, r7, u8p), r8)
        return int(
            ctypes.cast(result, ctypes.c_void_p).value
            == ctypes.cast(dest_ptr, ctypes.c_void_p).value
        )
    if name == "memzero":
        host(library.memzero, pointer(library, r6, u8p), r7)
        return None
    if name == "copy_whole_words":
        host(library.copy_whole_words, pointer(library, r6, u32p),
        pointer(library, r7, u32p),
        r8 & 0xFFFF,)
        return None
    if name == "update_whole_words":
        return int(host(library.update_whole_words, pointer(library, r6, u32p),
        pointer(library, r7, u32p),
        r8 & 0xFFFF,))
    if name == "load_u8":
        return int(host(library.load_u8, pointer(library, r6, u8p)))
    if name == "load_u16":
        return int(host(library.load_u16, pointer(library, r6, u8p)))
    if name == "store_u8":
        host(library.store_u8, pointer(library, r6, u8p), r7)
        return None
    if name == "store_u16":
        host(library.store_u16, pointer(library, r6, u8p), r7)
        return None
    if name == "store_u32":
        host(library.store_u32, pointer(library, r6, u8p), r7)
        return None
    if name == "nvm_sum_bytes":
        source = pointer(library, r7, u8p) if (r6 & 0xFFFF) else None
        return int(host(library.nvm_sum_bytes, r6, source))
    if name == "nvm_family0_chunk_cost":
        return int(host(library.nvm_family0_chunk_cost, r6))
    if name == "scale_u16_delta_s16_x4":
        return int(host(library.scale_u16_delta_s16_x4, r6, r7, r8)) & 0xFFFFFFFF
    if name == "nvm_record_offset":
        return int(host(library.nvm_record_offset, r6, r7, r8)) & 0xFFFFFFFF
    if name == "nvm_payload_chunk_length":
        return int(host(library.nvm_payload_chunk_length, r6, r7)) & 0xFFFFFFFF
    if name == "nvm_probe_range_rejected":
        return int(host(library.nvm_probe_range_rejected, r6, r7)) & 0xFFFFFFFF
    if name == "lookup_u32_value_by_key":
        return int(host(library.lookup_u32_value_by_key, r6, r7, r8)) & 0xFFFFFFFF
    if name == "poll_word_masks":
        return int(host(library.poll_word_masks, r6, r7, r8, r9)) & 0xFFFFFFFF
    if name == "clear_application_ram_4k":
        host(library.clear_application_ram_4k)
        return None
    if name == "nvm_set_physical_result_state":
        host(library.nvm_set_physical_result_state, r6)
        return None
    if name == "nvm_set_secondary_result_state":
        host(library.nvm_set_secondary_result_state, r6)
        return None
    if name == "icus20_read_bit0":
        return int(host(library.icus20_read_bit0)) & 0xFFFFFFFF
    if name == "faci_decode_completion_status":
        return int(host(library.faci_decode_completion_status)) & 0xFFFFFFFF
    if name == "nvm_lookup_byte_result":
        return int(host(library.nvm_lookup_byte_result, r6, r7, r8)) & 0xFFFFFFFF
    if name == "nvm_translate_saved_driver_result":
        return int(host(library.nvm_translate_saved_driver_result)) & 0xFFFFFFFF
    if name == "nvm_get_logical_storage_page":
        return int(host(library.nvm_get_logical_storage_page, r6, pointer(library, r7, ctypes.POINTER(ctypes.c_uint16)),)) & 0xFFFFFFFF
    if name == "nvm_get_direct_operation_result":
        return int(host(library.nvm_get_direct_operation_result)) & 0xFFFFFFFF
    if name == "nvm_accumulate_diagnostic_mask":
        host(library.nvm_accumulate_diagnostic_mask, r6)
        return None
    if name == "nvm_accumulate_side_status":
        host(library.nvm_accumulate_side_status, r6)
        return None
    if name == "nvm_accumulate_result_class":
        host(library.nvm_accumulate_result_class, r6)
        return None
    if name == "nvm_initialize_operation":
        host(library.nvm_initialize_operation)
        return None
    if name == "nvm_initialize_family1_application":
        host(library.nvm_initialize_family1_application)
        return None
    if name == "nvm_publish_logical_result":
        host(library.nvm_publish_logical_result, r6, r7, r8)
        return None
    if name == "nvm_unlink_queue_slot":
        host(library.nvm_unlink_queue_slot, r6, r7, r8)
        return None
    if name == "nvm_recover_family0_request_indices":
        host(library.nvm_recover_family0_request_indices, pointer(library, r6, u8p), pointer(library, r7, u8p),)
        return None
    if name == "nvm_recover_family1_request_indices":
        host(library.nvm_recover_family1_request_indices, pointer(library, r6, u8p), pointer(library, r7, u8p),)
        return None
    if name == "freshness_encode_wire":
        host(library.freshness_encode_wire, r6, r7, r8)
        return None
    if name == "freshness_decode_wire":
        host(library.freshness_decode_wire, r6, r7, r8)
        return None
    if name == "nvm_publish_family1_checksum":
        host(library.nvm_publish_family1_checksum, r6)
        return None
    if name == "pwm_initialize_compare_stages":
        host(library.pwm_initialize_compare_stages, r6)
        return None
    if name == "pwm_stage_halfword_compares":
        host(library.pwm_stage_halfword_compares, r6, r7, r8, r9)
        return None
    if name == "pwm_stage_word_compares":
        host(library.pwm_stage_word_compares, r6, r7, r8, r9)
        return None
    if name == "nvm_set_read_buffer":
        host(library.nvm_set_read_buffer, r6, r7)
        return None
    if name == "nvm_set_write_buffer":
        host(library.nvm_set_write_buffer, r6, r7)
        return None
    if name == "nvm_submit_operation":
        return int(host(library.nvm_submit_operation, r6)) & 0xFFFFFFFF
    if name == "freshness_select_reset_candidate":
        return int(host(library.freshness_select_reset_candidate, r7, r8)) & 0xFFFFFFFF
    if name == "freshness_commit_pending":
        host(library.freshness_commit_pending, r6, r7)
        return None
    if name == "freshness_reconstruct_ordinary":
        return int(host(library.freshness_reconstruct_ordinary, r6, r7, r8, r9)) & 0xFFFFFFFF
    if name == "freshness_reconstruct_candidate":
        return int(host(library.freshness_reconstruct_candidate, r6, r7, r8, r9)) & 0xFFFFFFFF
    if name == "nvm_get_family1_record":
        return int(host(library.nvm_get_family1_record, r6, r7)) & 0xFFFFFFFF
    if name == "read_repair_redundant_u8":
        return int(host(library.read_repair_redundant_u8, r6, r7, r8, r9)) & 0xFFFFFFFF
    if name == "classify_channel_residual_a":
        return int(host(library.classify_channel_residual_a)) & 0xFFFFFFFF
    if name == "nvm_submit_bulk_reads":
        return int(host(library.nvm_submit_bulk_reads)) & 0xFFFFFFFF
    if name == "nvm_step_initial_read_acquisition":
        return int(host(library.nvm_step_initial_read_acquisition)) & 0xFFFFFFFF
    if name == "nvm_step_acquisition_pass":
        return int(host(library.nvm_step_acquisition_pass)) & 0xFFFFFFFF
    if name == "nvm_run_bounded_initial_acquisition":
        host(library.nvm_run_bounded_initial_acquisition)
        return None
    if name == "check_learned_quad_bounds":
        return int(host(library.check_learned_quad_bounds)) & 0xFFFFFFFF
    if name == "update_thermal_release_envelope":
        host(library.update_thermal_release_envelope)
        return None
    if name == "update_thermal_history_qualification":
        host(library.update_thermal_history_qualification)
        return None
    if name == "nvm_initialize_queues":
        host(library.nvm_initialize_queues)
        return None
    if name == "nvm_reset_queues_notifying":
        host(library.nvm_reset_queues_notifying)
        return None
    if name == "nvm_pop_queue_head":
        return int(host(library.nvm_pop_queue_head, r6, r7)) & 0xFFFFFFFF
    if name == "nvm_enqueue_read":
        return int(host(library.nvm_enqueue_read, r6, r7)) & 0xFFFFFFFF
    if name == "nvm_enqueue_write":
        return int(host(library.nvm_enqueue_write, r6, r7)) & 0xFFFFFFFF
    if name == "nvm_set_family0_record":
        return int(host(library.nvm_set_family0_record, r6, r7)) & 0xFFFFFFFF
    if name == "dcra1_crc_raw_words":
        return int(host(library.dcra1_crc_raw_words, r6, r7, r8)) & 0xFFFFFFFF
    if name == "nvm_get_family2_rom_record":
        return int(host(library.nvm_get_family2_rom_record, r6, r7)) & 0xFFFFFFFF
    if name == "nvm_get_record":
        return int(host(library.nvm_get_record, r6, r7)) & 0xFFFFFFFF
    if name == "publish_learned_quad":
        host(library.publish_learned_quad)
        return None
    if name == "restore_learned_quad":
        return int(host(library.restore_learned_quad)) & 0xFFFFFFFF
    if name == "curve16_interpolate_with_slope":
        return int(host(library.curve16_interpolate_with_slope, r6, r7, r8)) & 0xFFFFFFFF
    if name == "force_unconfirmed_terminal_monitor_healthy":
        return int(host(library.force_unconfirmed_terminal_monitor_healthy, r6, r7, r8)) & 0xFFFFFFFF
    if name == "priority_mask_enter":
        return int(host(library.priority_mask_enter, r6)) & 0xFFFFFFFF
    if name == "dataflash_copy_words_ecc":
        return int(host(library.dataflash_copy_words_ecc, r6, r7, r8)) & 0xFFFFFFFF
    if name == "priority_mask_restore":
        host(library.priority_mask_restore, r6)
        return None
    if name in VALUE_RETURN:
        return int(host(getattr(library, name), r6)) & 0xFFFFFFFF
    raise AssertionError(f"no C call for {name}")


def parse_signature(signature: str, name: str) -> tuple[str, list[str]]:
    signature = NATIVE_SIGNATURES.get(name, signature)
    opening = signature.find("(")
    closing = signature.rfind(")")
    if opening < 0 or closing < opening or name not in signature[:opening]:
        raise AssertionError(f"unparsed signature for {name}")
    return_type = " ".join(signature[:opening].replace(name, "").split())
    body = signature[opening + 1:closing].strip()
    if body in {"", "void"}:
        return return_type, []
    return return_type, [part.strip() for part in c_text._split_args(body)]


_GPR_ALIASES = {"sp": 3, "gp": 4, "tp": 5, "ep": 30, "lp": 31}


def load_registers(library: ctypes.CDLL, registers: dict, gpr_fill: int = 0x11111111) -> None:
    gpr = (ctypes.c_uint32 * 32).in_dll(library, "camry_gpr")
    for index in range(32):
        gpr[index] = gpr_fill & 0xFFFFFFFF
    for index, name in ((3, "camry_sp"), (4, "camry_gp"), (5, "camry_tp")):
        gpr[index] = ctypes.c_uint32.in_dll(library, name).value
    for name, raw in registers.items():
        label = name.lower()
        index = _GPR_ALIASES.get(label)
        if index is None and re.fullmatch(r"r(?:[0-9]|[12][0-9]|3[01])", label):
            index = int(label[1:])
        if index is not None:
            gpr[index] = (int(raw, 0) if isinstance(raw, str) else int(raw)) & 0xFFFFFFFF
    gpr[0] = 0
    library.camry_gpr_export_aliases()
    ctypes.c_uint32.in_dll(library, "camry_pmr").value = int(registers.get("PMR", "0"), 16) & 0xFFFFFFFF
    ctypes.c_uint32.in_dll(library, "camry_psw").value = int(registers.get("PSW", "0x20"), 16) & 0xFFFFFFFF
    for name in ("CDBCR", "ICCTRL"):
        ctypes.c_uint32.in_dll(library, name).value = int(registers.get(name, "0"), 16) & 0xFFFFFFFF
    state = ((ctypes.c_uint32 * 32) * 14).in_dll(library, "camry_SR")
    ctypes.memset(ctypes.addressof(state), 0, ctypes.sizeof(state))
    for name, (selector, index) in SYSTEM_REGISTERS.items():
        if name in registers:
            state[selector][index] = int(registers[name], 16) & 0xFFFFFFFF


def with_registers(library: ctypes.CDLL, registers: dict) -> dict:
    observed = dict(registers)
    library.camry_gpr_import_aliases()
    gpr = (ctypes.c_uint32 * 32).in_dll(library, "camry_gpr")
    observed.update({f"r{index}": hex(value) for index, value in enumerate(gpr)})
    observed.update({name: hex(gpr[index]) for name, index in _GPR_ALIASES.items()})
    observed["PMR"] = f"{ctypes.c_uint32.in_dll(library, 'camry_pmr').value:#x}"
    for label, name in (("PSW", "camry_psw"), ("gp", "camry_gp"), ("tp", "camry_tp"), ("sp", "camry_sp"), ("CDBCR", "CDBCR"), ("ICCTRL", "ICCTRL")):
        observed[label] = f"{ctypes.c_uint32.in_dll(library, name).value:#x}"
    state = ((ctypes.c_uint32 * 32) * 14).in_dll(library, "camry_SR")
    for name, (selector, index) in SYSTEM_REGISTERS.items():
        observed[name] = hex(state[selector][index])
    return observed


def scenario_u32(scenario: dict | None, address: int) -> int:
    """Little-endian word from scenario memory. A later row overrides an earlier one."""
    found = None
    if scenario is None:
        raise AssertionError(f"stack argument at {address:#x} is not in the scenario")
    for region in scenario.get("memory") or []:
        base = int(region["address"], 16)
        if "hex" in region:
            raw = bytes.fromhex(region["hex"])
            size = len(raw)
            if base <= address and address + 4 <= base + size:
                found = int.from_bytes(raw[address - base:address - base + 4], "little")
        elif base <= address and address + 4 <= base + int(region.get("size") or 0):
            fill = int(region["fill"]) & 0xFF
            found = fill * 0x01010101
    if found is None:
        raise AssertionError(f"stack argument at {address:#x} is not in the scenario")
    return found


# A prototyped parameter narrower than 32 bits is zero- or sign-extended by
# the caller. The callee uses that container. A pointer buffer still held in
# the register is the full address; the firmware zxh/zxb keeps the low part.
_ABI_WIDTH = {
    "ushort": (16, False), "uint16_t": (16, False), "undefined2": (16, False),
    "short": (16, True), "int16_t": (16, True),
    "uchar": (8, False), "uint8_t": (8, False), "undefined1": (8, False),
    "byte": (8, False), "undefined": (8, False), "bool": (8, False),
    "char": (8, True), "int8_t": (8, True),
}


def _abi_integer(param: str, value: int) -> int:
    value &= 0xFFFFFFFF
    name = re.search(r"([A-Za-z_][A-Za-z0-9_]*)\s*$", param.strip())
    type_text = param.strip()[:name.start()] if name else param
    words = [
        word for word in type_text.replace("const", " ").replace("volatile", " ").split()
        if word not in {"unsigned", "signed"}
    ]
    if words and words[-1] == "int" and "unsigned" in type_text:
        return value
    spec = _ABI_WIDTH.get(words[-1] if words else "")
    if spec is None:
        return value
    bits, signed = spec
    value &= (1 << bits) - 1
    if signed and value & (1 << (bits - 1)):
        value -= 1 << bits
    return value & 0xFFFFFFFF


class NativeInput(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "after_instructions", "address", "value", "width",
    )]


class NativeAccess(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "instruction", "address", "width", "write",
    )]


def _native_timing(library: ctypes.CDLL, scenario: dict | None):
    events = (scenario or {}).get("events") or []
    if not events:
        return None
    name = scenario["name"]
    if Path(name).name != name:
        raise AssertionError("invalid native timing scenario name")
    # The primary's timing is reusable only with the original tracked inputs.
    retained = next((row for row in load_oracles() if row["name"] == name), None)
    input_fields = (
        "entry", "registers", "gpr_fill", "memory", "pre_reset_memory",
        "peripheral_file", "reset", "max_instructions", "stop_addresses", "events",
    )
    if retained is None or any(scenario.get(key) != retained.get(key) for key in input_fields):
        raise AssertionError(f"{name}: timing requires the original retained inputs")
    path = REPO_ROOT / "build" / "tmp" / f"{name}.timing-report.json"
    if path.is_file():
        report = json.loads(path.read_text(encoding="utf-8"))
    else:
        from tools.emulation.p1me_machine import run

        path.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(prefix="camry-native-timing-", dir=path.parent) as tmp:
            original = Path(tmp) / "scenario.json"
            original.write_text(json.dumps(retained) + "\n", encoding="utf-8")
            report = run("camry-8965F3307000", original, path)
    metadata = resolve_target("camry-8965F3307000")[1]
    code_sha = hashlib.sha256((REPO_ROOT / metadata["codeflash"]).read_bytes()).hexdigest()
    contract = report.get("resolved_run_contract") or {}
    if (
        report.get("schema") != "rh850-p1me-machine-report-v2"
        or report.get("target") != "camry-8965F3307000"
        or report.get("scenario") != name
        or report.get("codeflash_sha256") != code_sha
        or code_sha != metadata["codeflash_sha256"]
        or report.get("model_sha256") != MEMORY_MODEL_SHA256
        or report.get("executable_overlays") is not False
        or report.get("passed") is not True
        or report.get("trace_lost_address") is not False
        or int((contract.get("entry") or {}).get("resolved_address", "-1"), 16)
            != int(scenario["entry"]["address"], 16)
        or contract.get("stop_addresses") != scenario.get("stop_addresses", [])
        or contract.get("max_instructions") != scenario.get("max_instructions")
        or contract.get("reset") != scenario.get("reset", "none")
    ):
        raise AssertionError(f"{name}: primary timing identity/contract mismatch")
    event_fields = ("kind", "after_instructions", "register", "value", "evidence")
    if [tuple(event.get(key) for key in event_fields) for event in events] != [
        tuple(event.get(key) for key in event_fields) for event in contract.get("events", [])
    ]:
        raise AssertionError(f"{name}: primary external-input contract mismatch")
    inputs = []
    for event in sorted(events, key=lambda row: row["after_instructions"]):
        if event["kind"] != "register-input" or event["register"] not in MACHINE_REGISTERS:
            raise AssertionError(f"{name}: unsupported native timed event {event['kind']}")
        register = MACHINE_REGISTERS[event["register"]]
        tick, value, width = event["after_instructions"], int(event["value"], 16), int(register["size"])
        if not 0 <= tick <= 0xFFFFFFFF or width not in (1, 2, 4) or not 0 <= value < 1 << (width * 8):
            raise AssertionError(f"{name}: unsupported native input width/value/clock")
        inputs.append(NativeInput(tick, int(register["address"]), value, width))
    accesses = []
    previous = 0
    if len(report.get("memory_accesses", [])) >= 1048576:
        raise AssertionError(f"{name}: primary timing trace reached its recording cap")
    for access in report.get("memory_accesses", []):
        if "instruction" not in access:
            raise AssertionError(f"{name}: primary report lacks instruction positions")
        address = int(access["address"], 16)
        if address < 0xFF000000:
            continue
        tick = access["instruction"]
        if not previous <= tick <= 0xFFFFFFFF or access["kind"] not in {"read", "write"}:
            raise AssertionError(f"{name}: invalid primary bus ordering")
        previous = tick
        accesses.append(NativeAccess(tick, address, access["size"], access["kind"] == "write"))
    final_tick = report["instruction_count"]
    if not accesses or not previous < final_tick <= 0xFFFFFFFF:
        raise AssertionError(f"{name}: incomplete primary bus timing")
    input_view = (NativeInput * len(inputs))(*inputs)
    access_view = (NativeAccess * len(accesses))(*accesses)
    library.camry_native_set_inputs.argtypes = [ctypes.POINTER(NativeInput), ctypes.c_uint32]
    library.camry_native_set_inputs.restype = None
    library.camry_native_set_accesses.argtypes = [ctypes.POINTER(NativeAccess), ctypes.c_uint32]
    library.camry_native_set_accesses.restype = None
    library.camry_native_finish.argtypes = [ctypes.c_uint32]
    library.camry_native_finish.restype = None
    library.camry_native_set_inputs(input_view, len(inputs))
    library.camry_native_set_accesses(access_view, len(accesses))
    # The primary stops before dispatching events at instruction_count.
    return input_view, access_view, final_tick - 1


def call_corpus(
    library: ctypes.CDLL,
    name: str,
    signature: str,
    registers: dict,
    scenario: dict | None = None,
) -> int | None:
    ctypes.c_uint32.in_dll(library, "camry_gp").value = int(registers.get("gp", "0"), 16) & 0xFFFFFFFF
    ctypes.c_uint32.in_dll(library, "camry_tp").value = int(registers.get("tp", "0"), 16) & 0xFFFFFFFF
    ctypes.c_uint32.in_dll(library, "camry_sp").value = int(registers.get("sp", "0"), 16) & 0xFFFFFFFF
    ctypes.c_uint32.in_dll(library, "camry_peripheral_file").value = bool(
        scenario and scenario.get("peripheral_file", False)
    )
    # The byte machine reads an unwritten local as the scenario fill. The
    # oracle host compare sets this; a verifier child has to use the same byte.
    fill_byte = 0
    if scenario is not None:
        for region in scenario.get("memory") or []:
            if "fill" in region:
                fill_byte = int(region["fill"]) & 0xFF
                break
    ctypes.c_uint8.in_dll(library, "camry_fill").value = fill_byte
    fill = 0x11111111
    if scenario is not None and scenario.get("gpr_fill"):
        fill = int(scenario["gpr_fill"], 16)
    if scenario and scenario.get("events") and registers != scenario.get("registers", {}):
        raise AssertionError(f"{name}: timing requires the original retained register inputs")
    load_registers(library, registers, fill)
    configure_native_model(library, scenario)
    timing = _native_timing(library, scenario)
    return_type, params = parse_signature(signature, name)
    if len(params) > 32:
        raise AssertionError(f"{name} has stack arguments")
    gpr = (ctypes.c_uint32 * 32).in_dll(library, "camry_gpr")
    sp = int(gpr[3])
    library.camry_read32.argtypes = [ctypes.c_uint32]
    library.camry_read32.restype = ctypes.c_uint32
    values = []
    for index in range(len(params)):
        if index < 4:
            values.append(int(gpr[6 + index]))
        else:
            values.append(int(library.camry_read32(sp + (index - 4) * 4)))
    u8p = ctypes.POINTER(ctypes.c_uint8)
    u32 = ctypes.c_uint32
    argtypes = []
    args = []
    for param, value in zip(params, values):
        if "*" in param:
            argtypes.append(u8p)
            args.append(pointer(library, value, u8p))
        else:
            argtypes.append(u32)
            args.append(_abi_integer(param, value))
    function = getattr(library, name)
    function.argtypes = argtypes
    entry = (scenario or {}).get("entry", {}).get("address")
    if entry is None:
        root = u32()
        library.camry_code_address.argtypes = [ctypes.c_void_p, ctypes.POINTER(u32)]
        library.camry_code_address.restype = ctypes.c_int
        if not library.camry_code_address(ctypes.cast(function, ctypes.c_void_p), ctypes.byref(root)):
            raise AssertionError(f"{name} has no firmware address")
        root_address = root.value
    else:
        root_address = int(entry, 16)
    ctypes.c_uint32.in_dll(library, "camry_note_root").value = root_address

    def invoke():
        if scenario and scenario.get("expected_fault"):
            call_expected_fault(library, function, args, scenario)
            return 0
        result = function(*args)
        if timing is not None:
            library.camry_native_finish(timing[2])
        return result

    if return_type == "void":
        function.restype = None
        invoke()
        return None
    if "*" in return_type:
        function.restype = ctypes.c_void_p
        result = invoke()
        if not result:
            return 0
        firmware = u32()
        library.camry_host_firmware.argtypes = [ctypes.c_void_p, ctypes.POINTER(u32)]
        library.camry_host_firmware.restype = ctypes.c_int
        if library.camry_host_firmware(result, ctypes.byref(firmware)):
            return int(firmware.value) & 0xFFFFFFFF
        # A status or firmware address returned through a pointer-typed
        # signature is the integer in r10, not a host pointer.
        if result <= 0xFFFFFFFF:
            return int(result) & 0xFFFFFFFF
        library.camry_host_addr.argtypes = [ctypes.c_void_p]
        library.camry_host_addr.restype = u32
        return int(library.camry_host_addr(result)) & 0xFFFFFFFF
    if return_type in {"byte", "uchar", "uint8_t", "undefined1", "char", "bool"}:
        function.restype = ctypes.c_uint8
    elif return_type in {"ushort", "short", "uint16_t", "int16_t", "undefined2"}:
        function.restype = ctypes.c_uint16
    else:
        function.restype = u32
    return int(invoke()) & 0xFFFFFFFF


def corpus_returns(form: str | None, name: str, signature: str | None = None) -> bool | None:
    if form == "lifted":
        return True
    if form != "corpus":
        return None
    text = signature or SIGNATURES[name]
    return_type, _params = parse_signature(text, name)
    return return_type != "void"


def call_matched(
    library: ctypes.CDLL,
    form: str | None,
    address: int,
    name: str,
    registers: dict,
    limit: int,
    signature: str | None = None,
    scenario: dict | None = None,
) -> int | None:
    if scenario and scenario.get("events") and form != "corpus":
        raise AssertionError(f"{name}: timed external inputs require native corpus C")
    if scenario is not None:
        ctypes.c_uint32.in_dll(library, "camry_peripheral_file").value = bool(
            scenario.get("peripheral_file", False)
        )
        from .host_rewrite import native_workflow_stops
        from .native import call_native_workflow

        stops = native_workflow_stops(scenario)
        if stops:
            return call_native_workflow(
                library, name, signature or SIGNATURES[name], registers, scenario, stops,
            )
    if form == "lifted":
        return call_lifted(library, address, registers, limit)
    if form == "corpus":
        return call_corpus(library, name, signature or SIGNATURES[name], registers, scenario)
    return call_function(library, name, registers, scenario)


def call_lifted(library: ctypes.CDLL, address: int, registers: dict, limit: int) -> int:
    ctypes.c_uint32.in_dll(library, "camry_gp").value = int(registers.get("gp", "0"), 16) & 0xFFFFFFFF
    ctypes.c_uint32.in_dll(library, "camry_tp").value = int(registers.get("tp", "0"), 16) & 0xFFFFFFFF
    ctypes.c_uint32.in_dll(library, "camry_sp").value = int(registers.get("sp", "0"), 16) & 0xFFFFFFFF
    load_registers(library, registers)
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


