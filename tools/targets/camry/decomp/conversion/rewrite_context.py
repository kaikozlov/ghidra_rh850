"""Firmware exception and paired-register context reconstruction."""
from __future__ import annotations

import re

from tools.targets.camry.decomp import c_text, syntax



def _rewrite_split_pointer_words(code: str) -> str:
    """Slots four bytes apart that a callee indexes are firmware address words.

    Ghidra emits one host pointer per slot. The callee reads word N at byte
    offset N*4. A host pointer is eight bytes, so that word is not slot N.
    """
    declaration = re.compile(
        r"^([ \t]*)((?:[A-Za-z_][A-Za-z0-9_]*[ \t*]+)*)"
        r"([A-Za-z_][A-Za-z0-9_]*_([0-9a-fA-F]+))\s*;[ \t]*$"
    )
    while True:
        lines = code.split("\n")
        run: list[tuple[int, str, str, str, str]] = []
        runs: list[list[tuple[int, str, str, str, str]]] = []

        def finish(items: list[tuple[int, str, str, str, str]]) -> None:
            if len(items) < 3:
                return
            offsets = [int(item[4], 16) for item in items]
            if any(offsets[index] - offsets[index + 1] != 4 for index in range(len(offsets) - 1)):
                return
            if any("*" not in item[2] for item in items[1:]):
                return
            runs.append(items)

        for index, line in enumerate(lines):
            match = declaration.match(line)
            if match is not None and "[" not in line:
                run.append((index, match.group(1), match.group(2), match.group(3), match.group(4)))
                continue
            finish(run)
            run = []
        finish(run)
        chosen = None
        for items in runs:
            names = [item[3] for item in items]
            usable = True
            for slot, name in enumerate(names):
                uses = len(re.findall(rf"\b{re.escape(name)}\b", code))
                assigns = re.findall(rf"\b{re.escape(name)}\s*=", code)
                taken = re.findall(rf"(?<![&])&{re.escape(name)}\b", code)
                expected_taken = 1 if slot == 0 else 0
                if len(assigns) != 1 or len(taken) != expected_taken or uses != (3 if slot == 0 else 2):
                    usable = False
                    break
            if usable:
                chosen = items
                break
        if chosen is None:
            return code
        indent = chosen[0][1]
        first = chosen[0][3]
        names = [item[3] for item in chosen]
        is_pointer = ["*" in item[2] for item in chosen]
        start = chosen[0][0]
        end = chosen[-1][0]
        lines[start:end + 1] = [f"{indent}int {first}[{len(names)}];"]
        code = "\n".join(lines)

        def store(slot: int, expr: str) -> str:
            expr = expr.strip()
            if is_pointer[slot] and not expr.startswith("camry_host_addr("):
                expr = f"camry_host_addr({expr})"
            return f"{first}[{slot}] = {expr};"

        for slot, name in enumerate(names):
            code = re.sub(
                rf"\b{re.escape(name)}\s*=\s*([^;]+);",
                lambda found, slot=slot: store(slot, found.group(1)),
                code,
                count=1,
            )
        code = re.sub(rf"(?<![&])&{re.escape(first)}\b", first, code, count=1)


def _rewrite_exception_context(code: str) -> str:
    """Recover the concrete context instructions discarded by decompilation."""
    code = re.sub(
        r"\(\(void\)\(([^()]*)\), \(void\)\(([^()]*)\), set_selected_mpu_region_attributes_659f8\(\)\)",
        r"set_selected_mpu_region_attributes_659f8(\1, \2)", code,
    )
    name = syntax._signature_name(syntax._c_signature(code))
    if name == "scan_dtc_status_snapshot":
        # 5261A leaves r7/r8 intact; 52818/5281E store through those original
        # pointers. Retained extraout casts must not truncate host-local outputs.
        for output in ("dtc", "status"):
            code = code.replace(
                f"{output} = ((void *)camry_host_ptr((uint32_t)(((uint32_t)({output})))));",
                "",
            )
    if name == "application_entry":
        # 20880 saves incoming LP on the old stack at a stack-relative address.
        code = re.sub(r"\s*undefined4 unaff_retaddr\s*;", "", code)
        code = re.sub(r"\s*DAT_febe1ffc = unaff_retaddr\s*;", "", code)
    if name == "boot_advance_crc_authentication_routine_5936" and "LAB_00005a00:" not in code:
        # 59CC is the BR after the state store and real context cleanup.
        code = code.replace(
            "boot_region_authentication_clear_contexts();\n        return;",
            "boot_region_authentication_clear_contexts();\n        goto LAB_00005a00;",
        )
        terminal = list(re.finditer(r"\breturn\s*;", code))[-1]
        code = code[:terminal.start()] + "LAB_00005a00:\n  " + code[terminal.start():]
    # These concrete PREPARE/JARL/DISPOSE chains can stop inside a callee.
    # Keep their architectural frames live; C locals still implement the body.
    frames = {
        "boot_hardware_ram_init_and_select_image": (31,),
        "boot_select_application_or_resident": (29, 31),
        "select_clock3_and_set_divider_80_10c6": (31,),
        "run_ch0_application_task": (29, 31),
        "record_ch0_dispatch": (31,),
        "record_supervised_task_dispatch": (27, 28, 29, 31),
        "request_logical_controller_run_stop": (31,),
        "set_controller_cache_6b94_and_start_channels_7f4b0": (31,),
        "request_start_on_matching_controller_channels_7f882": (27, 28, 29, 31),
        "driver_request_channel_start_stop": (28, 29, 31),
        "nvm_dispatch_family0_page_span": tuple(range(24, 30)) + (31,),
        "nvm_dispatch_family1_page_span": tuple(range(25, 30)) + (31,),
        "nvm_service_logical_and_physical_driver": (31,),
        "nvm_service_scheduler": (31,),
        "service_active_nvm_scheduler_operation_723d6": (29, 31),
        "advance_nvm_scheduler_operation_phase_72342": (27, 28, 29, 31),
        "nvm_leave_service_guard": (31,),
        "nvm_finish_deferred_guard": (29, 31),
        "dcm_read_dtc_list_service": (29, 31),
        "start_dtc_list_response_by_status_mask_8ca8a": (27, 29, 31),
        "dcm_advance_dtc_list_request": tuple(range(21, 30)) + (31,),
        "dcm_resume_queued_dtc_list": (31,),
        "dcm_proprietary_operation_service": (31,),
        "dcm_advance_proprietary_operation": (28, 29, 31),
        "dcm_resume_queued_proprietary_operation": (31,),
        "dcm_dispatch_entry_event_generation": (26, 27, 28, 29, 31),
        "step_mode600_stimulus_fit": (26, 27, 28, 29, 31),
        "boot_service_security_access": (29, 31),
        "boot_security_seed_request": (29, 31),
        "boot_security_key_request": (29, 31),
        "boot_security_access_negative_response_52ca": (31,),
        "boot_security_access_positive_challenge_response_52de": (31,),
        "boot_negative_response": (31,),
        "boot_dispatch_diagnostic_service": (29, 31),
        "boot_transport_receive_frame": (28, 29, 31),
        "validate_and_dispatch_transport_single_frame_242a": (26, 27, 28, 29, 31),
        "admit_append_and_complete_single_frame_request_23b8": (28, 29, 31),
        "boot_transport_receive_complete": (31,),
        "boot_region_authentication_progress": (31,),
        "boot_advance_crc_authentication_routine_5936": (31,),
        "application_entry": (31,),
        "startup_coordinator": (31,),
    }
    if name in frames:
        marker = "camry_write32((camry_sp - 4u) & ~3u, camry_gpr["
        if marker in code:
            return code
        call_sites = {
            "boot_hardware_ram_init_and_select_image": {
                "initialize_ffc604_and_ffc614_register_pairs_79a": (0x140c, []),
                "configure_ffc654_registers_and_poll_7b6": (0x1410, []),
                "initialize_codeflash_ecc_controls_and_poll_802": (0x1414, []),
                "configure_ffc5b0_registers_and_poll_zero_880": (0x1418, []),
                "configure_ffc640_registers_and_poll_8c8": (0x141c, []),
                "configure_and_poll_multiple_register_banks_96e": (0x1420, []),
                "initialize_six_610_8000_register_pairs_c52": (0x1424, []),
                "boot_select_application_or_resident": (0x1474, []),
            },
            "boot_select_application_or_resident": {
                "load_tp_configuration_into_ffc1_ffc2_ffc3_banks_c9a": (0x13b8, []),
                "snapshot_validated_ecm_status_and_clear_errors_e54": (0x13bc, []),
                "configure_ecm_masks_and_clear_error_outputs_f80": (0x13c0, []),
                "select_clock3_and_set_divider_80_10c6": (0x13c4, []),
                "boot_validate_application_images": (0x13c8, []),
                "clear_fffee980_register_block_1206": (0x13d0, []),
                "boot_resident_main": (0x13f0, []),
            },
            "select_clock3_and_set_divider_80_10c6": {
                "spin_forever_10c4": (0x1136, []),
            },
            "run_ch0_application_task": {
                "begin_execution_profile_slot0": (0x65fc6, []),
                "record_ch0_dispatch": (0x65fce, ["camry_gpr[29] = iVar2"]),
                "fast_control_cycle": (0x65fd2, ["camry_gpr[29] = iVar2"]),
                "end_execution_profile_slot0": (0x65fdc, ["camry_gpr[29] = iVar2"]),
            },
            "record_ch0_dispatch": {
                "record_supervised_task_dispatch": (0x652f4, [
                    "camry_gpr[6] = camry_gp - 0x2a50u",
                    "camry_r7 = camry_gpr[7] = 0x30dc0u",
                ]),
            },
            "record_supervised_task_dispatch": {
                "priority_mask_enter": (0x652ba, [
                    "camry_gpr[28] = camry_host_addr(state)",
                    "camry_gpr[27] = camry_host_addr(policy)", "camry_gpr[6] = 0xffc0u",
                ]),
                "priority_mask_restore": (0x652d2, [
                    "camry_gpr[29] = bVar1", "camry_gpr[10] = saved_mask",
                    "camry_gpr[6] = saved_mask",
                ]),
                "enter_terminal_hardware_sequence": (0x652de, []),
            },
            "request_logical_controller_run_stop": {
                "change_controller_cache_6b94_to_57a8_7f486": (0x7f4ec, [
                    "camry_gpr[6] = logical_controller", "camry_r7 = camry_gpr[7] = requested_mode",
                ]),
                "set_controller_cache_6b94_and_start_channels_7f4b0": (0x7f4f8, [
                    "camry_gpr[6] = logical_controller", "camry_r7 = camry_gpr[7] = requested_mode",
                    "camry_gpr[10] = 1u",
                ]),
            },
            "set_controller_cache_6b94_and_start_channels_7f4b0": {
                "request_start_on_matching_controller_channels_7f882": (0x7f4d8, ["camry_gpr[6] = param_1 & 0xffu"]),
            },
            "request_start_on_matching_controller_channels_7f882": {
                "driver_request_channel_start_stop": (0x7f8a6, [
                    "camry_gpr[27] = uVar3", "camry_gpr[28] = param_1",
                    "camry_gpr[29] = uVar4", "camry_gpr[6] = uVar4",
                    "camry_r7 = camry_gpr[7] = 1u",
                ]),
            },
            "driver_request_channel_start_stop": {
                "clear_driver_busoff_observation_latch_835c6": (0x84038, []),
                "enter_channel_mode_zero_after_global_activation_84a5e": (0x8403e, []),
                "driver_observe_and_clear_bus_off_entry": (0x8408c, []),
                "cancel_pending_channel_transmits_before_mode_one_84b74": (0x84092, []),
            },
            "dcm_read_dtc_list_service": {
                "start_dtc_list_response_by_status_mask_8ca8a": (0x8cb6a, []),
                "dcm_cancel_retained_dtc_list": (0x8cb74, ["camry_gpr[29] = 0"]),
            },
            "start_dtc_list_response_by_status_mask_8ca8a": {
                "dcm_advance_dtc_list_request": (0x8cadc, [
                    "camry_gpr[27] = 0", "camry_gpr[29] = 0xfebf3f24u",
                    "camry_gpr[6] = 0xfebf3f24u",
                ]),
                "dcm_report_positive_response": (0x8caf8, [
                    "camry_gpr[27] = 0", "camry_gpr[29] = 0xfebf3f24u",
                    "camry_gpr[6] = 0xfebf3f24u",
                ]),
                "dcm_report_negative_or_pending": (0x8caf0, [
                    "camry_gpr[27] = 0", "camry_gpr[29] = 0xfebf3f24u",
                    "camry_gpr[6] = 0xfebf3f24u", "camry_r7 = camry_gpr[7] = nrc",
                ]),
            },
            "dcm_advance_dtc_list_request": {
                "dcm_report_positive_response": (0x8ca3c, [
                    "camry_gpr[21] = camry_host_addr(message)", "camry_gpr[22] = uVar2",
                    "camry_gpr[23] = uVar3", "camry_gpr[24] = 0xfebf3f40u",
                    "camry_gpr[25] = uVar4", "camry_gpr[26] = iVar5",
                    "camry_gpr[27] = uVar6", "camry_gpr[28] = uVar7",
                    "camry_gpr[29] = 0xfebf3f18u", "camry_gpr[6] = camry_host_addr(message)",
                ]),
            },
            "dcm_resume_queued_dtc_list": {
                "dcm_advance_dtc_list_request": (0x8cb88, ["camry_gpr[6] = 0xfebf3f24u"]),
            },
            "dcm_proprietary_operation_service": {
                "dcm_advance_proprietary_operation": (0x8e49e, ["camry_gpr[6] = 0xfebf48ecu"]),
                "dcm_cancel_retained_proprietary_operation": (0x8e4a4, []),
            },
            "dcm_advance_proprietary_operation": {
                "dcm_join_proprietary_start": (0x8e3c0, [
                    "camry_gpr[28] = camry_host_addr(message)", "camry_gpr[29] = 0xfebf48e4u",
                    "camry_gpr[6] = camry_host_addr(message)",
                    "camry_r7 = camry_gpr[7] = camry_sp + 3u",
                ]),
                "proprietary_operation_finish_join": (0x8e3d2, [
                    "camry_gpr[6] = camry_read8(camry_sp + 3u)",
                    "camry_r7 = camry_gpr[7] = camry_sp + 4u",
                ]),
                "dcm_complete_proprietary_message": (0x8e402, [
                    "camry_gpr[6] = camry_host_addr(message)",
                    "camry_r7 = camry_gpr[7] = uVar1", "camry_gpr[10] = uVar1",
                ]),
                "dcm_reject_proprietary_message": (0x8e408, [
                    "camry_gpr[6] = camry_host_addr(message)",
                    "camry_r7 = camry_gpr[7] = uVar1", "camry_gpr[10] = uVar1",
                ]),
            },
            "dcm_resume_queued_proprietary_operation": {
                "dcm_advance_proprietary_operation": (0x8e4b8, ["camry_gpr[6] = 0xfebf48ecu"]),
            },
            "dcm_dispatch_entry_event_generation": {},
            "step_mode600_stimulus_fit": {},
            "nvm_dispatch_family0_page_span": {
                "nvm_begin_page_erase_span": (0x68884, [
                    "camry_gpr[24] = unaff_r24", "camry_gpr[26] = uVar6",
                    "camry_gpr[27] = first_page", "camry_gpr[29] = nvm_family0_object_count",
                    "camry_gpr[6] = first_page",
                    "camry_r7 = camry_gpr[7] = (uVar2 + uVar6 - first_page) & 0xffffu",
                ]),
            },
            "nvm_dispatch_family1_page_span": {
                "nvm_begin_page_erase_span": (0x6890e, [
                    "camry_gpr[26] = uVar5", "camry_gpr[27] = first_page",
                    "camry_gpr[29] = uVar9", "camry_gpr[6] = first_page",
                    "camry_r7 = camry_gpr[7] = (uVar5 + 1u - first_page) & 0xffffu",
                ]),
            },
            "nvm_service_logical_and_physical_driver": {
                "nvm_driver_gate_rejected": (0x74170, ["camry_gpr[6] = 0x14u"]),
                "nvm_service_uninitialized": (0x74178, []),
                "nvm_enter_service_guard": (0x74180, []),
                "nvm_reconcile_probe_mode": (0x74184, []),
                "nvm_select_service_poll": (0x7418e, ["camry_gpr[6] = 1u"]),
                "nvm_service_scheduler": (0x74192, []),
                "nvm_store_service_mode_nonzero": (0x74198, ["camry_gpr[6] = uVar1 != 0"]),
                "nvm_leave_service_guard": (0x7419c, []),
            },
            "nvm_service_scheduler": {
                "nvm_snapshot_scheduler_operation": (0x72ef4, ["camry_gpr[6] = camry_sp"]),
                "nvm_map_operation_state_two_to_two_else_one_73c76": (0x72efc, []),
                "load_next_nvm_operation_into_scheduler_72e70": (0x72f04, []),
                "record_nvm_integrity_fault_72130": (0x72f0a, []),
                "request_nvm_preemption_for_reserved_queue_head_72ed4": (0x72f16, ["camry_gpr[6] = camry_sp"]),
                "service_active_nvm_scheduler_operation_723d6": (0x72f1a, []),
            },
            "service_active_nvm_scheduler_operation_723d6": {
                "lookup_u32_pair_value_or_default_73a5c": (0x723f8, [
                    "camry_gpr[6] = nvm_scheduler_operation.operation",
                    "camry_r7 = camry_gpr[7] = 0xffu", "camry_gpr[8] = camry_tp + 0x3604u",
                ]),
                "reject_nvm_scheduler_handle_for_operation_class_72298": (0x72404, ["camry_gpr[29] = uVar1", "camry_gpr[6] = uVar1"]),
                "advance_nvm_scheduler_operation_phase_72342": (0x7240e, ["camry_gpr[29] = uVar1", "camry_gpr[6] = uVar1"]),
                "record_nvm_integrity_fault_72130": (0x72414, []),
            },
            "advance_nvm_scheduler_operation_phase_72342": {
                "lookup_u32_pair_value_or_default_73a5c": (0x7237a, [
                    "camry_gpr[27] = 0xfebf6124u", "camry_gpr[28] = param_1",
                    "camry_gpr[29] = uVar3", "camry_gpr[6] = DAT_febf6114",
                    "camry_r7 = camry_gpr[7] = 0xffu", "camry_gpr[8] = camry_tp + 0x3614u",
                ]),
                "nvm_poll_pending_operation_73c14": (0x7239e, ["camry_gpr[29] = uVar3"]),
                "dispatch_nvm_scheduler_completion_phase_722d4": (0x723ba, [
                    "camry_gpr[6] = param_1", "camry_r7 = camry_gpr[7] = uVar3",
                ]),
            },
            "nvm_leave_service_guard": {
                "nvm_finish_deferred_guard": (0x79aa6, []),
            },
            "nvm_finish_deferred_guard": {
                "nvm_start_suspend_and_publish_status_7990e": (0x79a8a, ["camry_gpr[29] = 0xfebf6ccdu"]),
            },
            "boot_service_security_access": {
                "boot_get_request_buffer_and_clear_append_index_67d0": (0x5522, ["camry_gpr[29] = request_length"]),
                "boot_security_seed_request": (0x556a, ["camry_gpr[6] = request_length"]),
                "boot_security_key_request": (0x5576, ["camry_gpr[6] = request_length"]),
                "boot_security_access_negative_response_52ca": (0x5580, ["camry_gpr[6] = uVar5"]),
            },
            "boot_security_seed_request": {
                "boot_security_access_negative_response_52ca": (0x534e, ["camry_gpr[29] = uVar7", "camry_gpr[6] = uVar6"]),
                "boot_security_generate_challenge": (0x5384, ["camry_gpr[6] = camry_gp - 0x6cdcu"]),
                "boot_security_access_positive_challenge_response_52de": (0x53ea, ["camry_gpr[29] = uVar7"]),
            },
            "boot_security_key_request": {
                "boot_security_access_negative_response_52ca": (0x542c, ["camry_gpr[29] = uVar8", "camry_gpr[6] = uVar6"]),
                "boot_security_derive_expected_key": (0x546c, [
                    "camry_gpr[6] = camry_gp - 0x6cccu", "camry_r7 = camry_gpr[7] = camry_gp - 0x6cdcu",
                    "camry_gpr[8] = camry_sp",
                ]),
                "boot_security_access_positive_challenge_response_52de": (0x5504, ["camry_gpr[29] = uVar8"]),
            },
            "boot_security_access_negative_response_52ca": {
                "boot_negative_response": (0x52da, [
                    "camry_r7 = camry_gpr[7] = param_1", "camry_gpr[6] = 0x27u",
                ]),
            },
            "boot_security_access_positive_challenge_response_52de": {
                "boot_response_submit": (0x5324, [
                    "camry_gpr[6] = (uVar3 >> 7) ^ 1u",
                    "camry_r7 = camry_gpr[7] = camry_gp - 0x6d30u", "camry_gpr[8] = length",
                ]),
            },
            "boot_negative_response": {
                "boot_response_submit": (0x521e, [
                    "camry_gpr[6] = mode", "camry_r7 = camry_gpr[7] = camry_gp - 0x6d30u",
                    "camry_gpr[8] = 3u",
                ]),
            },
            "boot_dispatch_diagnostic_service": {
                "boot_negative_response": (0x5266, [
                    "camry_gpr[6] = sid", "camry_r7 = camry_gpr[7] = 0x11u",
                ]),
            },
            "boot_transport_receive_frame": {
                "find_receive_route_and_extract_frame_nibble_2284": (0x2bba, [
                    "camry_gpr[28] = camry_host_addr(puVar3)", "camry_gpr[29] = uVar4",
                    "camry_gpr[6] = selector", "camry_r7 = camry_gpr[7] = camry_gpr[28]",
                    "camry_gpr[8] = camry_sp + 3u",
                ]),
                "validate_and_dispatch_transport_single_frame_242a": (0x2bfe, ["camry_gpr[6] = uVar2"]),
                "validate_and_dispatch_transport_first_frame_27d8": (0x2c08, ["camry_gpr[6] = uVar2"]),
                "validate_consecutive_request_sequence_and_dispatch_2946": (0x2c12, ["camry_gpr[6] = uVar2"]),
                "handle_transport_flow_control_frame_2ae4": (0x2bf4, ["camry_gpr[6] = uVar2"]),
            },
            "validate_and_dispatch_transport_single_frame_242a": {
                "admit_append_and_complete_single_frame_request_23b8": (0x24cc, [
                    "camry_gpr[26] = camry_host_addr((void *)(uintptr_t)param_3)",
                    "camry_gpr[27] = param_1 & 0xffu",
                    "camry_gpr[28] = uVar4", "camry_gpr[29] = uVar5 + 1u",
                    "camry_gpr[6] = param_1", "camry_r7 = camry_gpr[7] = uVar4",
                    "camry_gpr[8] = camry_gpr[26] + uVar5 + 1u",
                ]),
            },
            "admit_append_and_complete_single_frame_request_23b8": {
                "boot_transport_request_admit": (0x23f0, [
                    "camry_gpr[28] = param_2", "camry_gpr[29] = channel",
                    "camry_gpr[6] = channel", "camry_r7 = camry_gpr[7] = camry_sp + 4u",
                    "camry_gpr[8] = param_2", "camry_gpr[9] = camry_sp + 2u",
                    "camry_write32(camry_sp + 4u, camry_host_addr(param_3))",
                    "camry_write16(camry_sp + 8u, param_2)",
                    "camry_write16(camry_sp + 2u, uStack_16)",
                ]),
                "boot_transport_request_append": (0x240a, [
                    "camry_gpr[6] = channel", "camry_r7 = camry_gpr[7] = camry_sp + 4u",
                    "camry_gpr[8] = camry_sp + 2u",
                    "camry_write16(camry_sp + 2u, uStack_16)",
                ]),
                "boot_transport_receive_complete": (0x2426, [
                    "camry_gpr[6] = channel", "camry_r7 = camry_gpr[7] = status",
                ]),
            },
            "boot_transport_receive_complete": {
                "boot_request_receive_complete": (0x6b86, [
                    "camry_gpr[6] = channel", "camry_r7 = camry_gpr[7] = status",
                ]),
            },
            "boot_region_authentication_progress": {
                "boot_image_authentication_step": (0x6ef0, []),
            },
            "boot_advance_crc_authentication_routine_5936": {
                "boot_get_combined_request_response_state_67f6": (0x593e, []),
                "boot_region_authentication_clear_contexts": (0x59cc, []),
            },
            "application_entry": {
                "startup_coordinator": (0x20888, []),
            },
            "startup_coordinator": {
                "application_context_init": (0x637f6, []),
            },
        }[name]
        brace = syntax._opening_brace(code)
        edits = []
        for callee, opening, _closing in c_text._direct_calls(code[brace + 1:], syntax._SKIP_CALLS):
            if name == "step_mode600_stimulus_fit" and callee == "abort_mode600_stimulus_fit":
                end = opening + brace + 1
                while code[end - 1].isspace():
                    end -= 1
                # 3438C begins the real stack-argument setup for 343AE's JARL.
                setup = [
                    "camry_gpr[26] = (uint32_t)iVar12;", "camry_gpr[27] = uVar13;",
                    "camry_gpr[28] = uVar14;", "camry_gpr[29] = 0x30ed8u;",
                    "camry_gpr[1] = camry_sp + 0x12u;",
                    "camry_gpr[30] = camry_sp;", "camry_write32(camry_sp, camry_gpr[1]);",
                    "camry_gpr[6] = camry_sp + 0x10u;", "camry_gpr[1] += 2u;",
                    "camry_r7 = camry_gpr[7] = camry_sp + 0xfu;",
                    "camry_write32(camry_sp + 4u, camry_gpr[1]);",
                    "camry_gpr[8] = camry_sp + 0x18u;", "camry_gpr[1] = camry_sp + 0x11u;",
                    "camry_gpr[9] = camry_sp + 0x16u;",
                    "camry_write32(camry_sp + 8u, camry_gpr[1]);", "camry_gpr[31] = 0x343b2u;",
                ]
                edits.append((end - len(callee), end - len(callee), "\n  ".join(setup) + "\n  "))
                continue
            if callee not in call_sites:
                continue
            return_pc, updates = call_sites[callee]
            if name == "boot_advance_crc_authentication_routine_5936" and callee == "boot_region_authentication_clear_contexts":
                tail = code[_closing + brace + 2:].lstrip()
                return_pc = 0x59cc if re.match(r";\s*goto LAB_00005a00;", tail) else 0x5990
            if name == "boot_transport_receive_frame" and callee != "find_receive_route_and_extract_frame_nibble_2284":
                updates += [
                    "camry_r7 = camry_gpr[7] = uVar4", "camry_gpr[8] = camry_host_addr(puVar3)",
                ]
            if name == "driver_request_channel_start_stop":
                updates = [
                    "camry_gpr[28] = uVar4", "camry_gpr[29] = camry_host_addr(pFVar5)",
                    "camry_gpr[6] = uVar4",
                ] + updates
            end = opening + brace + 1
            while code[end - 1].isspace():
                end -= 1
            prefix = ", ".join([*updates, f"camry_gpr[31] = 0x{return_pc:x}u", callee])
            edits.append((end - len(callee), end, f"({prefix})"))
        code = syntax._apply_spans(code, edits)
        if name in {"request_start_on_matching_controller_channels_7f882", "dcm_dispatch_entry_event_generation"}:
            if name == "request_start_on_matching_controller_channels_7f882":
                updates = [
                    "camry_gpr[29] = (uint32_t)(uintptr_t)pcVar5",
                    "camry_gpr[6] = param_1", "camry_gpr[31] = 0x7f8c4u",
                ]
            else:
                updates = [
                    "camry_gpr[26] = uVar1", "camry_gpr[27] = (uint32_t)(uintptr_t)pcVar6",
                    "camry_gpr[28] = bVar7", "camry_gpr[29] = uVar8",
                    "camry_gpr[6] = uVar8", "camry_gpr[31] = 0x989c4u",
                ]
            code = code.replace("camry_indirect(", "(" + ", ".join(updates + ["camry_indirect"]) + ")(", 1)
        if name == "advance_nvm_scheduler_operation_phase_72342":
            # 72394 JARL [r29],lp transfers to the table-selected handler.
            updates = [
                "camry_gpr[27] = 0xfebf6124u", "camry_gpr[28] = param_1",
                "camry_gpr[29] = (uint32_t)(uintptr_t)pcVar4",
                "camry_gpr[30] = camry_tp + (uint32_t)((int16_t)param_1 * 24)"
                " + (uVar3 == 1 ? 0u : 0x36d0u)",
                "camry_gpr[31] = 0x72398u",
            ]
            code = code.replace("camry_indirect(", "(" + ", ".join(updates + ["camry_indirect"]) + ")(", 1)
        registers = frames[name]
        extra = {"start_dtc_list_response_by_status_mask_8ca8a": 8, "dcm_advance_dtc_list_request": 32,
                 "boot_select_application_or_resident": 4,
                 "nvm_service_scheduler": 16,
                 "nvm_dispatch_family0_page_span": 4,
                 "nvm_dispatch_family1_page_span": 4,
                 "dcm_advance_proprietary_operation": 8,
                 "step_mode600_stimulus_fit": 32,
                 "boot_security_key_request": 16,
                 "boot_transport_receive_frame": 4,
                 "admit_append_and_complete_single_frame_request_23b8": 12}.get(name, 0)
        size = len(registers) * 4 + extra
        if name in {"nvm_dispatch_family0_page_span", "nvm_dispatch_family1_page_span"}:
            # 68812/688CC pass SP+2; PREPARE reserves one local word.
            local = "uStack_1e" if name == "nvm_dispatch_family0_page_span" else "uStack_1a"
            code = re.sub(rf"^\s*ushort\s+{local}\s*;", "", code, flags=re.M)
            code = re.sub(rf"\b{local}\b",
                          "(*((ushort *)camry_host_ptr(camry_sp + 2u)))", code)
        if name == "boot_security_key_request":
            code = re.sub(r"\buchar\s+local_18\s*\[\s*16\s*\]\s*;",
                          "uchar *local_18 = (uchar *)camry_host_ptr(camry_sp);", code)
        if name == "boot_transport_receive_frame":
            code = re.sub(r"\bchar\s+cStack_d\s*;",
                          "char *camry_boot_frame_type = (char *)camry_host_ptr(camry_sp + 3u);", code)
            code = re.sub(r"\bcStack_d\b", "(*camry_boot_frame_type)", code)
        if name == "start_dtc_list_response_by_status_mask_8ca8a":
            code = re.sub(r"\buchar\s+auStack_11\s*\[\s*5\s*\]\s*;",
                          "uchar *auStack_11 = (uchar *)camry_host_ptr(camry_sp + 3u);", code)
        if name == "nvm_service_scheduler":
            # 72EEE passes SP to the sixteen-byte scheduler snapshot.
            code = re.sub(r"^\s*F33NvmOperation\s+FStack_14\s*;", "", code, flags=re.M)
            code = re.sub(r"\bFStack_14\b",
                          "(*((F33NvmOperation *)camry_host_ptr(camry_sp)))", code)
        if name in {"dcm_advance_dtc_list_request", "dcm_advance_proprietary_operation"}:
            record, displacement = (("44", 4) if name == "dcm_advance_dtc_list_request" else ("11", 3))
            code = re.sub(
                rf"\buint8_t\s+stack_record_{record}\s*\[\s*\d+\s*\]\s*;",
                f"uint8_t *stack_record_{record} = (uint8_t *)camry_host_ptr(camry_sp + {displacement}u);", code,
            )
        if name == "step_mode600_stimulus_fit":
            code = re.sub(r"\buint8_t\s+stack_record_25\s*\[\s*\d+\s*\]\s*;",
                          "uint8_t *stack_record_25 = (uint8_t *)camry_host_ptr(camry_sp + 15u);", code)
        if name == "dcm_advance_dtc_list_request":
            for local, displacement in (("FStack_40", 8), ("FStack_38", 16)):
                code = re.sub(rf"^\s*F33DiagSourceBuffer\s+{local}\s*;", "", code, flags=re.M)
                code = re.sub(rf"\b{local}\b",
                              f"(*((F33DiagSourceBuffer *)camry_host_ptr(camry_sp + {displacement}u)))", code)
        restore = " ".join(
            f"camry_gpr[{reg}] = camry_read32((camry_sp + {size - 4 * (index + 1)}u) & ~3u);"
            for index, reg in enumerate(registers)
        )
        restore += f" camry_sp += {size}u; camry_gpr[3] = camry_sp;"

        def frame_return(match: re.Match[str]) -> str:
            value = match.group(1).strip()
            if value:
                # A returned callee executes before DISPOSE.
                return ("{ uint32_t camry_return_value = (" + value + "); "
                        "if (camry_halted) return 0; " + restore + " return camry_return_value; }")
            return "{ if (!camry_halted) { " + restore + " } return; }"

        comments = c_text._comment_spans(code)
        code = syntax._apply_spans(code, [
            (match.start(), match.end(), frame_return(match))
            for match in re.finditer(r"\breturn\b([^;{}]*);", code)
            if not c_text._span_contains(comments, match.start())
        ])
        prologue = "\n" + "\n".join(
            f"  camry_write32((camry_sp - {4 * (index + 1)}u) & ~3u, camry_gpr[{reg}]);"
            for index, reg in enumerate(registers)
        )
        prologue += f"\n  camry_sp -= {size}u;\n  camry_gpr[3] = camry_sp;\n"
        return code[:brace + 1] + prologue + code[brace + 1:]
    if name in {"boot_ram_dispatch", "boot_relocated_8370"}:
        # PREPARE saves r29, then LP; the indirect JARL runs before DISPOSE.
        # Keep that live ABI frame when the callback stops without returning.
        return_pc = 0x8396 if name == "boot_ram_dispatch" else 0xFEBF1026
        return "\n".join([
            f"void {name}(int param_1)", "{",
            "  uint32_t slot = 0xfebf0f00u;",
            "  uint32_t key;",
            "  camry_write32((camry_sp - 4u) & ~3u, camry_gpr[29]);",
            "  camry_write32((camry_sp - 8u) & ~3u, camry_gpr[31]);",
            "  camry_sp -= 8u;",
            "  camry_gpr[3] = camry_sp;",
            "  camry_gpr[1] = 0;",
            "  for (;;) {",
            "    key = camry_read32(slot);",
            "    if (key == 0xffffffffu || key == (uint32_t)param_1) break;",
            "    slot += 8u;",
            "    camry_gpr[1] += 1u;",
            "  }",
            "  camry_gpr[19] = key;",
            "  camry_gpr[30] = slot;",
            "  camry_gpr[29] = camry_read32(slot + 4u);",
            "  camry_gpr[6] = (uint32_t)param_1;",
            f"  camry_gpr[31] = 0x{return_pc:x}u;",
            "  camry_gpr[10] = ((uint32_t (*)(uint32_t, uint32_t, uint32_t, uint32_t))",
            "      camry_indirect(camry_gpr[29]))",
            "      (camry_gpr[6], camry_gpr[7], camry_gpr[8], camry_gpr[9]);",
            "  if (camry_halted) return;",
            "  camry_gpr[31] = camry_read32(camry_sp & ~3u);",
            "  camry_gpr[29] = camry_read32((camry_sp + 4u) & ~3u);",
            "  camry_sp += 8u;",
            "  camry_gpr[3] = camry_sp;",
            "  return;", "}",
        ]) + "\n"
    if name not in {
        "apply_mpu_attribute_profile", "set_selected_mpu_region_attributes_659f8", "increment_saturating_exception_counter_and_feret_65bd4",
        "save_registers_and_callt_state_to_ep_frame_712ce", "restore_ep_exception_frame_and_eiret_71322", "run_ch2_task_with_saved_exception_context_71508",
    }:
        return code

    def push() -> list[str]:
        return [
            "  camry_gpr_import_aliases();",
            "  cursor = camry_sp;",
            "  for (unsigned reg = 1; reg <= 31; ++reg) {",
            "    cursor -= 4u;",
            "    camry_write32(cursor & ~3u, camry_gpr[reg]);",
            "  }",
            "  camry_sp = cursor;",
        ]

    def pop() -> list[str]:
        return [
            "  cursor = camry_sp;",
            "  for (unsigned reg = 31; reg != 0; --reg) {",
            "    if (reg != 3) camry_gpr[reg] = camry_read32(cursor & ~3u);",
            "    cursor += 4u;",
            "  }",
            "  camry_gpr[3] = cursor;",
            "  camry_gpr_export_aliases();",
        ]

    def acknowledge(pc: str) -> list[str]:
        return [
            "  camry_gpr_import_aliases();",
            "  camry_SR[2][12] &= ~2u;",
            "  if ((camry_SR[0][11] & 1u) != 0) {",
            "    uint32_t priority = camry_SR[1][7] & 31u;",
            "    if (priority > 16u) priority = 16u;",
            "    unsigned mask_priority = priority > 15u ? 15u : priority;",
            "    uint32_t masked = (camry_pmr >> mask_priority) & 1u;",
            "    camry_SR[2][12] |= masked << 1;",
            "    if (!masked && !(camry_SR[2][10] & ((1u << (priority + 1u)) - 1u) & 0xffffu)",
            "        && !(camry_psw & 0xa0u)) {",
            "      uint32_t vector = (camry_SR[1][(camry_psw & 0x8000u) ? 3 : 2] & 0xfffffe00u) + 0x70u;",
            "      camry_SR[0][11] = 0;",
            f"      camry_SR[0][0] = {pc};",
            "      camry_SR[0][1] = camry_psw;",
            "      camry_SR[0][13] = 0x72u;",
            "      camry_psw = (camry_psw & 0xbfffffffu) | 0x60u;",
            "      camry_gpr_export_aliases();",
            "      camry_gpr[10] = ((uint32_t (*)(uint32_t, uint32_t, uint32_t, uint32_t))camry_indirect(vector))",
            "          (camry_gpr[6], camry_gpr[7], camry_gpr[8], camry_gpr[9]);",
            "      camry_gpr_import_aliases();",
            "    }",
            "  }",
        ]

    def returning(fe: bool = False, void: bool = False) -> list[str]:
        pc, psw = (2, 3) if fe else (0, 1)
        return [
            "  camry_gpr[3] = camry_sp;",
            "  camry_gpr_export_aliases();",
            "  if (!(camry_psw & 0x40u) && !(camry_SR[2][13] & 1u))",
            "    camry_SR[2][10] &= camry_SR[2][10] - 1u;",
            f"  camry_psw = camry_SR[0][{psw}];",
            *acknowledge(f"camry_SR[0][{pc}]"),
            "  camry_gpr_import_aliases();",
            "  return;" if void else "  return camry_gpr[10];",
            "}",
        ]

    if name == "apply_mpu_attribute_profile":
        lines = [
            "void apply_mpu_attribute_profile(uchar selector)", "{",
            "  camry_gpr[6] = selector;",
            "  camry_gpr[30] = 0x31708u + ((uint32_t)selector << 6);",
        ]
        for index in range(16):
            sel, reg = 6 + index // 8, 2 + 4 * (index % 8)
            lines += [
                f"  camry_gpr[10] = camry_read32(camry_gpr[30] + {4 * index}u);",
                f"  camry_SR[{sel}][{reg}] = camry_gpr[10];",
            ]
        lines += ["  __synchronize();", "  return;", "}"]
    elif name == "set_selected_mpu_region_attributes_659f8":
        lines = [
            "void set_selected_mpu_region_attributes_659f8(uint32_t mask, uint32_t attributes)", "{",
            "  camry_gpr[6] = mask;",
            "  camry_r7 = camry_gpr[7] = attributes;",
            "  camry_gpr[10] = mask;",
            "  camry_gpr[11] = attributes;",
        ]
        for index in range(16):
            sel, reg = 6 + index // 8, 2 + 4 * (index % 8)
            if index:
                lines += ["  camry_gpr[10] >>= 1;"]
            lines += [
                "  camry_gpr[12] = camry_gpr[10] & 1u;",
                f"  if (camry_gpr[12]) camry_SR[{sel}][{reg}] = attributes;",
            ]
        lines += ["  __synchronize();", "  return;", "}"]
    elif name == "save_registers_and_callt_state_to_ep_frame_712ce":
        lines = [
            "void save_registers_and_callt_state_to_ep_frame_712ce(undefined4 param_1, undefined4 param_2, undefined4 param_3, undefined4 param_4)", "{",
            "  camry_gpr_import_aliases();",
            "  camry_gpr[6] = param_1;", "  camry_gpr[7] = param_2;",
            "  camry_gpr[8] = param_3;", "  camry_gpr[9] = param_4;",
        ]
        for reg in range(19, 5, -1):
            lines += [f"  camry_write32(camry_gpr[30] + {24 + 4 * reg}u, camry_gpr[{reg}]);"]
        lines += [
            "  camry_write32(camry_gpr[30] + 36u, camry_gpr[2]);",
            "  camry_gpr[1] = camry_SR[0][17];",
            "  camry_write32(camry_gpr[30] + 16u, camry_gpr[1]);",
            "  camry_gpr[1] = camry_SR[0][16];",
            "  camry_write32(camry_gpr[30] + 12u, camry_gpr[1]);",
            "  camry_gpr_export_aliases();", "  return;", "}",
        ]
    elif name == "restore_ep_exception_frame_and_eiret_71322":
        lines = [
            "uint32_t restore_ep_exception_frame_and_eiret_71322(void)", "{",
            "  camry_gpr_import_aliases();",
            "  camry_gpr[30] = camry_sp;",
        ]
        for reg in (*range(19, 13, -1), *range(11, 5, -1)):
            lines += [f"  camry_gpr[{reg}] = camry_read32(camry_sp + {24 + 4 * reg}u);"]
        lines += [
            "  camry_gpr[1] = camry_read32(camry_sp + 12u);",
            "  camry_gpr[12] = camry_read32(camry_sp + 16u);",
            "  camry_SR[0][16] = camry_gpr[1];",
            "  camry_SR[0][17] = camry_gpr[12];",
            "  __disable_irq();",
            "  camry_gpr[1] = camry_read32(camry_sp);",
            "  camry_gpr[12] = camry_read32(camry_sp + 20u);",
            "  camry_gpr[13] = camry_read32(camry_sp + 24u);",
            "  camry_SR[0][13] = camry_gpr[1];",
            "  camry_SR[0][0] = camry_gpr[12];",
            "  camry_SR[0][1] = camry_gpr[13];",
            "  camry_gpr[13] = camry_read32(camry_sp + 76u);",
            "  camry_gpr[12] = camry_read32(camry_sp + 72u);",
            "  camry_gpr[1] = camry_read32(camry_sp + 32u);",
            "  camry_gpr[30] = camry_read32(camry_sp + 28u);",
            "  camry_gpr[31] = (uint32_t)(int32_t)(int16_t)camry_read16(camry_gpr[31]);",
            "  camry_sp += camry_gpr[31];",
            "  camry_gpr[31] = camry_read32(camry_sp);",
            "  camry_sp += 4u;",
            *returning(),
        ]
    elif name == "increment_saturating_exception_counter_and_feret_65bd4":
        # No saved-frame address escapes this handler. Its dead stack slots
        # are C locals; the architectural effects are MPAT6, the counter, FERET.
        lines = [
            "void increment_saturating_exception_counter_and_feret_65bd4(void)", "{",
            "  uint32_t saved_mpat6 = camry_SR[6][26];",
            "  camry_SR[6][26] = 0xb8u;",
            "  __synchronize();",
            "  uint32_t count = camry_read8(0xfebf3400u);",
            "  if (count != 0xffu) camry_write8(0xfebf3400u, count + 1u);",
            "  camry_SR[6][26] = saved_mpat6;",
            "  __synchronize();",
            "  camry_SR[0][2] += 4u;",
            *returning(fe=True, void=True),
        ]
    else:
        saved = [
            (24, None), (20, 0), (16, 1), (12, 13), (8, 28), (4, 16), (0, 17),
        ]
        lines = [
            "void run_ch2_task_with_saved_exception_context_71508(void)", "{", "  uint32_t cursor;",
            "  camry_gpr_import_aliases();",
            "  __synchronize();",
            "  camry_sp -= 28u;",
        ]
        for offset, reg in saved:
            if reg is not None:
                lines += [f"  camry_gpr[10] = camry_SR[0][{reg}];"]
            lines += [f"  camry_write32(camry_sp + {offset}u, camry_gpr[10]);"]
        lines += [
            "  camry_psw = (camry_psw & ~15u) | 10u;", "  __enable_irq();",
            *acknowledge("0x71546u"), *push(),
            "  camry_gpr[31] = 0x7154eu;",
            "  camry_gpr[10] = push_sixteen_mpu_attributes_65ac0();",
            "  camry_gpr[31] = 0x7155au;",
            "  apply_mpu_attribute_profile(camry_read8(0x31682u));",
            "  camry_gpr[2] = camry_sp;",
            "  camry_gpr[6] = 0xfebe0000u;",
            "  camry_sp = camry_gpr[3] = 0xfebe1800u;",
            "  camry_gpr[31] = 0x71568u;",
            "  run_ch2_application_task();",
            "  camry_sp = camry_gpr[2];",
            "  camry_gpr[31] = 0x7156eu;",
            "  camry_gpr[10] = pop_sixteen_mpu_attributes_65b4a();",
            *pop(),
            "  __disable_irq();",
        ]
        for offset, reg in reversed(saved[1:]):
            lines += [
                f"  camry_gpr[10] = camry_read32(camry_sp + {offset}u);",
                f"  camry_SR[0][{reg}] = camry_gpr[10];",
            ]
        lines += [
            "  camry_gpr[10] = camry_read32(camry_sp + 24u);",
            "  camry_sp += 28u;",
            *returning(void=True),
        ]
    return "\n".join(lines) + "\n"


def _rewrite_paired_mpat_frame(code: str) -> str:
    """Keep the MPAT frame live across the firmware's paired save/restore calls."""
    name = syntax._signature_name(syntax._c_signature(code))
    if name not in {"push_sixteen_mpu_attributes_65ac0", "pop_sixteen_mpu_attributes_65b4a"}:
        return code
    saving = name == "push_sixteen_mpu_attributes_65ac0"
    lines = [
        f"uint32_t {name}(void)",
        "{",
        "  uint32_t value;",
    ]
    # 65ac0 reserves 64 bytes; 65ac4..65b40 save MPAT0..15 at
    # SP+60 down to SP+0. 65b4a..65bc6 restore those exact words.
    # Neither call owns an ordinary C frame: only 65bce releases it.
    if saving:
        lines.append("  camry_sp -= 64u;")
    for index in range(16):
        selector, register = 6 + index // 8, 2 + 4 * (index % 8)
        address = f"camry_sp + {60 - 4 * index}u"
        if saving:
            lines.extend([
                f"  value = camry_SR[{selector}][{register}];",
                f"  camry_write32({address}, value);",
            ])
        else:
            lines.extend([
                f"  value = camry_read32({address});",
                f"  camry_SR[{selector}][{register}] = value;",
            ])
    lines.append("  __synchronize();")
    if not saving:
        lines.append("  camry_sp += 64u;")
    # Both helpers leave the last saved/restored MPAT word in r10.
    lines.extend(["  return value;", "}"])
    return "\n".join(lines) + "\n"

def _rewrite_paired_gpr_context(code: str) -> str:
    """Recover the live PUSHSP frame and the custom r2/r20 continuation ABI."""
    name = syntax._signature_name(syntax._c_signature(code))
    if name not in {"save_registers_switch_stack_apply_mpu_profile_71378", "apply_mpu_profile_restore_stack_and_registers_71398"}:
        return code
    saving = name == "save_registers_switch_stack_apply_mpu_profile_71378"
    lines = [
        f"uint32_t {name}(void)",
        "{",
        "  uint32_t cursor;",
        "  unsigned int reg;",
        "  camry_gpr_import_aliases();",
    ]
    if saving:
        lines.extend([
            "  cursor = camry_gpr[3];",
            "  for (reg = 1; reg <= 30; ++reg) {",
            "    cursor -= 4u;",
            "    camry_write32(cursor & ~3u, camry_gpr[reg]);",
            "  }",
            "  camry_gpr[3] = cursor;",
            "  camry_gpr[2] = cursor;",
            "  camry_gpr[3] = 0xfebe2800u;",
        ])
    lines.extend([
        "  camry_gpr[20] = camry_gpr[31];",
        f"  camry_gpr[6] = camry_read8(0x{0x31684 if saving else 0x31683:x}u);",
        f"  camry_gpr[31] = 0x{0x71394 if saving else 0x713a6:x}u;",
        "  camry_gpr_export_aliases();",
        "  apply_mpu_attribute_profile((uchar)camry_gpr[6]);",
    ])
    if saving:
        lines.append("  camry_gpr[31] = camry_gpr[20];")
    else:
        lines.extend([
            "  cursor = camry_gpr[2];",
            "  camry_gpr[31] = camry_gpr[20];",
            "  for (reg = 30; reg != 0; --reg) {",
            "    if (reg != 3) camry_gpr[reg] = camry_read32(cursor & ~3u);",
            "    cursor += 4u;",
            "  }",
            "  camry_gpr[3] = cursor;",
        ])
    lines.extend([
        "  camry_gpr_export_aliases();",
        "  return camry_gpr[10];",
        "}",
    ])
    return "\n".join(lines) + "\n"
