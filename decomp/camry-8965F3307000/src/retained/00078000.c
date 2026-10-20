#include "common.h"

int nvm_classify_two_record_presence_markers_78010(undefined2 param_1,undefined1 *param_2)

{
  uint8_t stack_record_e[14];
  undefined1 uVar1;
  int iVar2;
  
  *param_2 = 0xd;
  iVar2 = camry_host_addr(nvm_read_record_presence_marker_77f26(param_1,2,(stack_record_e + 1)));
  if (((iVar2 == 1) && (stack_record_e[1] == 'U')) && (iVar2 = camry_host_addr(nvm_read_record_presence_marker_77f26(param_1,1,stack_record_e)), iVar2 == 1)
     ) {
    if (stack_record_e[0] == 'U') {
      uVar1 = 0xf;
    }
    else {
      uVar1 = 0xff;
    }
    *param_2 = uVar1;
  }
  return iVar2;
}

void nvm_recheck_saved_record_and_dispatch_result_7805e(uint param_1)

{
  uchar auStack_8 [4];
  
  if (param_1 != 0xffff) {
    param_1 = nvm_read_with_optional_blank_check(DAT_febf6c2c,4,auStack_8,'\x01');
    if (param_1 == 3) {
      param_1 = 0xfffd;
    }
  }
  nvm_dispatch_selected_descriptor_callback_slot_seven_7849e(param_1);
  return;
}

uint nvm_submit_four_byte_record_marker_write_7808c(ushort param_1,ushort param_2,char param_3)

{
  uint byte_offset;
  undefined4 uVar1;
  uint32_t puVar2;
  undefined4 uVar3;
  uint result;
  
  puVar2 = (0x23dfcu);
  return_argument_word_7490a(0);
  if (param_3 == '\x02') {
    byte_offset = nvm_allocation_end_minus_trailer_words_77e0a(param_1,2);
    uVar1 = return_argument_word_7490a((puVar2 + 0x3e7c));
    uVar3 = 1;
  }
  else if (param_3 == '\x01') {
    byte_offset = nvm_allocation_end_minus_trailer_words_77e0a(param_1,1);
    uVar1 = return_argument_word_7490a(0x3e80u + (int)(puVar2));
    uVar3 = 1;
  }
  else {
    if (param_3 != '\x03') {
      return 0xfffb;
    }
    byte_offset = nvm_allocation_end_minus_trailer_words_77e0a(param_1,3);
    uVar1 = return_argument_word_7490a((puVar2 + 0x3e84));
    uVar3 = 0;
  }
  if (param_1 < (*((volatile uint16_t *)camry_host_ptr((uint32_t)(puVar2 + 0x3b2c))))) {
    DAT_febf6c2c = nvm_record_offset(param_1,param_2,byte_offset);
    result = nvm_stage_and_submit_program_with_optional_deferral_74c54(DAT_febf6c2c, 4, ((uchar *)camry_host_ptr((uint32_t)(uVar1))), 0, uVar3);
  }
  else {
    result = 0xfffb;
  }
  return result;
}

undefined4 nvm_suspend_flash_and_mark_access_flag_7812a(void)

{
  undefined4 uVar1;
  
  uVar1 = dataflash_request_suspend_789e2();
  thunk_nvm_set_service_enabled_764c2();
  return uVar1;
}

void nvm_forward_flash_suspend_notification_7813e(undefined1 param_1)

{
  nvm_buffer_or_dispatch_suspend_result_7998a(param_1);
  return;
}

undefined4 nvm_resume_flash_or_reset_physical_path_7814c(void)

{
  int iVar1;
  undefined4 uVar2;
  
  iVar1 = nvm_is_service_enabled_76762();
  if (iVar1 == 0) {
    DAT_febf6c5c = 1;
    nvm_refresh_driver_result_and_enable_service_76772();
    DAT_febf6c5c = 0;
    uVar2 = 2;
  }
  else {
    uVar2 = dataflash_resume_suspended_operation_78a56();
  }
  return uVar2;
}

void nvm_abort_selected_flash_path_with_guard_78176(void)

{
  int iVar1;
  
  iVar1 = nvm_is_service_enabled_76762();
  DAT_febf6c5c = 1;
  if (iVar1 == 0) {
    nvm_refresh_driver_result_and_enable_service_76772();
  }
  else {
    dataflash_abort_operation_and_reset_driver_78766();
  }
  DAT_febf6c5c = 0;
  return;
}

void nvm_clear_flash_callback_guard_781a0(void)

{
  DAT_febf6c5c = 0;
  return;
}

void nvm_set_suspend_policy_byte_781aa(undefined1 param_1)

{
  DAT_febf6c5b = param_1;
  return;
}

undefined1 nvm_get_suspend_policy_byte_781b4(void)

{
  return DAT_febf6c5b;
}

void nvm_abort_flash_unless_phase_fourteen_781be(void)

{
  int iVar1;
  
  DAT_febf6c5c = 0;
  iVar1 = dataflash_get_suspend_phase_78aca();
  if (iVar1 != 0xe) {
    dataflash_abort_operation_and_reset_driver_78766();
  }
  return;
}

undefined1 nvm_get_flash_callback_guard_781da(void)

{
  return DAT_febf6c5c;
}

void fill_constant_block_781e4(void)

{
  DAT_febf6c20 = 0;
  DAT_febf6c4f = 0xff;
  DAT_febf6c4e = 0;
  DAT_febf6c4d = 0xff;
  DAT_febf6c1c = 1;
  return;
}

uint dispatch_state_callback_and_optional_transition_78212(int param_1,undefined4 param_2,undefined4 param_3,uint param_4,byte param_5)

{
  uint uVar1;
  uint uVar2;
  
  param_4 = param_4 & 0xff;
  uVar1 = (*(int (*)())camry_indirect((uint32_t)(*((code * *)camry_host_ptr((uint32_t)((uint)param_5 * 4 + (*((volatile int32_t *)camry_host_ptr((uint32_t)(param_1 + 0xc))))))))))(param_2,param_3, param_3, param_4);
  if ((((uVar1 != 0xff) && (param_4 != uVar1)) &&
      (uVar2 = (uint)(*((byte *)camry_host_ptr((uint32_t)((*((volatile int32_t *)camry_host_ptr((uint32_t)(param_1 + 8)))) + uVar1)))), param_4 = uVar1, uVar2 != 0xff)) &&
     (uVar1 = (*(int (*)())camry_indirect((uint32_t)(*((code * *)camry_host_ptr((uint32_t)(uVar2 * 4 + (*((volatile int32_t *)camry_host_ptr((uint32_t)(param_1 + 0xc))))))))))(param_2,param_3), uVar1 != 0xff)) {
    param_4 = uVar1;
  }
  return param_4;
}

uint dispatch_bounded_state_event_matrix_78276(byte *param_1,byte *param_2, undefined4 param_3)

{
  uint uVar1;
  byte bVar2;
  
  uVar1 = (uint)*param_2;
  if ((uVar1 < *param_1) && ((uint)param_2[1] < (uint)param_1[1])) {
    bVar2 = *((char *)camry_host_ptr((uint32_t)((uint)param_2[1] + (int)(short)(ushort)param_1[1] * (int)(short)(ushort)*param_2 +
               *(int *)(param_1 + 4))));
    if ((int8_t)bVar2 != -1) {
      uVar1 = dispatch_state_callback_and_optional_transition_78212(camry_host_addr(param_1), camry_host_addr(param_2), param_3, uVar1, bVar2);
    }
  }
  return uVar1;
}

undefined1 nvm_get_state_machine_selector_782b2(void)

{
  return DAT_febf6c4d;
}

undefined4 nvm_invoke_two_descriptor_pre_step_callbacks_782bc(void)

{
  int iVar1;
  int iVar2;
  undefined8 uVar3;
  int iVar4;
  
  uVar3 = 0x23dfc00000000;
  iVar4 = 0;
  do {
    (*(int (*)())camry_indirect((uint32_t)(((((code *)(uintptr_t)((uint32_t)((uintptr_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)((*((int *)camry_host_ptr((uint32_t)(iVar4 * 4 + (int)((ulonglong)uVar3 >> 0x20) + 0x3ec4)))) + 0x14)))))))))))))();
    iVar2 = iVar4 + 1;
    iVar1 = iVar4 + -1;
    iVar4 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  return 1;
}

undefined4 nvm_reset_block_and_two_descriptor_callbacks_782de(void)

{
  int iVar1;
  int iVar2;
  undefined8 uVar3;
  int iVar4;
  
  uVar3 = 0x23dfc00000000;
  fill_constant_block_781e4();
  iVar4 = 0;
  do {
    (*(int (*)())camry_indirect((uint32_t)(((((code *)(uintptr_t)((uint32_t)((uintptr_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)((*((int *)camry_host_ptr((uint32_t)(iVar4 * 4 + (int)((ulonglong)uVar3 >> 0x20) + 0x3ec4)))) + 0x10)))))))))))))();
    iVar2 = iVar4 + 1;
    iVar1 = iVar4 + -1;
    iVar4 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  return 1;
}

uint32_t nvm_step_selected_state_machine_and_finish_errors_78304(void)

{
  uint8_t stack_record_34[52];
  uint32_t camry_r10_result;
  uint8_t stack_record_1c[28];
  uint32_t puVar1;
  undefined1 uVar2;
  uint uVar3;
  int *piStack_18;
  
  puVar1 = 0x23dfcu;
  ((int32_t *)(stack_record_34))[0] = 1;
  uVar3 = (camry_r10_result = nvm_get_state_machine_selector_782b2());
  if (uVar3 < 2) {
    (*((uint32_t *)(stack_record_34 + 16))) = 0;
    (*((uint32_t *)(stack_record_34 + 12))) = 0;
    (*((uint16_t *)(stack_record_34 + 10))) = 0xffff;
    (*((uint16_t *)(stack_record_34 + 8))) = 0;
    ((int32_t *)(stack_record_34))[1] = 0xffffffff;
    (camry_r10_result = nvm_invoke_two_descriptor_pre_step_callbacks_782bc());
    if (((int8_t)DAT_febf6c4f) == -1) {
      DAT_febf6c4f = '\0';
    }
    stack_record_1c[0] = DAT_febf6c4e;
    piStack_18 = ((int32_t *)(stack_record_34)) + 1;
    stack_record_1c[1] = DAT_febf6c4f;
    uVar2 = (camry_r10_result = dispatch_bounded_state_event_matrix_78276(((byte *)camry_host_ptr((uint32_t)((*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + uVar3 * 4 + 0x3ec4))))))), stack_record_1c, camry_host_addr(((int32_t *)(stack_record_34)))));
    DAT_febf6c4f = 0xff;
    if (((int32_t *)(stack_record_34))[0] != 1) {
      nvm_snapshot_completion_mode_handle_and_reset_request_77ce8();
      nvm_set_completion_raw_result_77d14(((int32_t *)(stack_record_34))[0]);
      nvm_finish_physical_result();
      fill_constant_block_781e4();
      (camry_r10_result = nvm_reset_block_and_two_descriptor_callbacks_782de());
      uVar2 = DAT_febf6c4e;
    }
  }
  else {
    DAT_febf6c4f = 0xff;
    DAT_febf6c4d = 0xff;
    DAT_febf6c4e = 0;
    DAT_febf6c1c = 1;
    uVar2 = DAT_febf6c4e;
  }
  DAT_febf6c4e = uVar2;
  return camry_r10_result;
}

void nvm_set_state_machine_selector_783b6(undefined1 param_1)

{
  DAT_febf6c4d = param_1;
  return;
}

void nvm_set_state_machine_event_783c0(undefined1 param_1)

{
  DAT_febf6c4f = param_1;
  return;
}

void nvm_set_state_machine_result_word_783ca(undefined4 param_1)

{
  DAT_febf6c1c = param_1;
  return;
}

undefined4 nvm_get_state_machine_result_word_783d4(void)

{
  return DAT_febf6c1c;
}

void nvm_refresh_selector_from_completion_mode_783e8(void)

{
  int iVar1;
  
  iVar1 = nvm_get_request_mode_77c64();
  if ((iVar1 == 0) || (iVar1 != 1 && iVar1 != 2)) {
    nvm_set_state_machine_selector_783b6(0xff);
  }
  else {
    nvm_store_inverted_current_descriptor_option_74f4a();
  }
  return;
}

void nvm_step_state_machine_mode_one_7840c(void)

{
  nvm_refresh_selector_from_completion_mode_783e8();
  ((void)(1), nvm_step_selected_state_machine_and_finish_errors_78304());
  return;
}

void nvm_tick_timeout_and_abort_expired_operation_7841e(void)

{
  if (0 < DAT_febf6c20) {
    DAT_febf6c20 = DAT_febf6c20 - (uint)DAT_0002792a;
    if (0 < DAT_febf6c20) {
      return;
    }
    nvm_snapshot_completion_mode_handle_and_reset_request_77ce8();
    nvm_set_completion_raw_result_77d14(0xfffa);
    nvm_finish_physical_result();
    if (0 < DAT_febf6c20) {
      return;
    }
  }
  fill_constant_block_781e4();
  nvm_reset_block_and_two_descriptor_callbacks_782de();
  nvm_abort_sync_transfer_and_reset_driver_state_74e94();
  return;
}

void nvm_step_state_machine_and_tick_timeout_78466(void)

{
  nvm_refresh_selector_from_completion_mode_783e8();
  ((void)(0), nvm_step_selected_state_machine_and_finish_errors_78304());
  nvm_tick_timeout_and_abort_expired_operation_7841e();
  return;
}

void nvm_dispatch_selected_descriptor_callback_slot_six_7847c(uint param_1)

{
  if (DAT_febf6c4d < 2) {
    (*(void (*)(uint))camry_indirect((uint32_t)(((((code *)(uintptr_t)((uint32_t)((uintptr_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x27cc0u + (uint32_t)(DAT_febf6c4d) * 4u)))) + 0x18))))))))))))(param_1);
  }
  return;
}

void nvm_dispatch_selected_descriptor_callback_slot_seven_7849e(uint param_1)

{
  if (DAT_febf6c4d < 2) {
    (*(void (*)(uint))camry_indirect((uint32_t)(((((code *)(uintptr_t)((uint32_t)((uintptr_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x27cc0u + (uint32_t)(DAT_febf6c4d) * 4u)))) + 0x1c))))))))))))(param_1);
  }
  return;
}

void nvm_dispatch_selected_descriptor_callback_slot_eight_784c0(uint param_1)

{
  if (DAT_febf6c4d < 2) {
    (*(void (*)(uint))camry_indirect((uint32_t)(((((code *)(uintptr_t)((uint32_t)((uintptr_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x27cc0u + (uint32_t)(DAT_febf6c4d) * 4u)))) + 0x20))))))))))))(param_1);
  }
  return;
}

void dataflash_initialize_driver_and_clock_78500(void)

{
  bool bVar1;
  uint uVar2;
  int iVar3;
  undefined4 unaff_r27;
  
  return_only_stub_79d32();
  uVar2 = icus20_second_read_bit0();
  if (uVar2 == 0) {
    mask_eic379_interrupt_and_sync_78b90();
    reset_fsuinitr_if_flash_ready_78c12();
    iVar3 = faci_force_stop_in_dataflash_mode_and_exit_78d3e();
    if (iVar3 == 0) {
      dataflash_initialize_idle_state_78b1c();
      dataflash_reset_interrupt_and_software_controls_78b60();
      bVar1 = false;
      goto LAB_00078542;
    }
    unaff_r27 = 5;
  }
  else {
    unaff_r27 = 0x82;
  }
  bVar1 = true;
  DAT_febf6cb1 = 1;
LAB_00078542:
  return_only_stub_79d34();
  if (bVar1) {
    nvm_forward_flash_driver_error_7939c(0x5c,0,0,unaff_r27);
  }
  else {
    dataflash_set_fpckar_1e28_78bb0();
    DAT_febf6cb1 = 0;
  }
  return;
}

int dataflash_start_buffered_word_program_78566(int param_1,int param_2,uint param_3)

{
  undefined4 uVar1;
  uint uVar2;
  int iVar3;
  int iVar4;
  
  uVar2 = icus20_second_read_bit0();
  if (uVar2 == 0) {
    if (DAT_febf6cb0 == '\x01') {
      if (DAT_febf6cb2 == '\x0e') {
        iVar3 = is_null_program_source_78d80(param_2);
        if (iVar3 != 0) {
          uVar1 = 4;
          goto LAB_00078668;
        }
        iVar3 = dataflash_reject_out_of_range_or_unaligned_address_78d88(param_1,4);
        if (iVar3 != 0) {
          uVar1 = 2;
          goto LAB_00078668;
        }
        iVar3 = dataflash_reject_invalid_program_range_78d9e(param_1,param_3,4);
        if (iVar3 != 0) {
          uVar1 = 3;
          goto LAB_00078668;
        }
        return_only_stub_79d32();
        dataflash_configure_faci_operation_controls_78bc6();
        iVar4 = faci_select_dataflash_pe_or_read_mode_78c70(0x80);
        iVar3 = 1;
        if (iVar4 != 0) {
          return_only_stub_79d34();
          faci_select_dataflash_pe_or_read_mode_78c70(0);
          uVar1 = 8;
          goto LAB_00078668;
        }
        flash_set_software_enables(1);
        for (uVar2 = 0; uVar2 < param_3 >> 2; uVar2 = uVar2 + 1) {
          *(undefined4 *)(((undefined *)camry_host_ptr((uint32_t)(0xfebf6c6cu + (uint32_t)(uVar2 * 4) * 1u)))) = (*((undefined4 *)camry_host_ptr((uint32_t)(uVar2 * 4 + param_2))));
        }
        iVar3 = faci_submit_program_halfwords_78e2a(((undefined *)camry_host_ptr(0xfebf6c6cu)),param_1,4);
        return_only_stub_79d34();
        if (iVar3 == 1) {
          DAT_febf6c60 = param_1 + 4;
          DAT_febf6c64 = ((uint32_t)(0xfebf6c70u));
          DAT_febf6c68 = param_3 + param_1 + -1;
          DAT_febf6cac = 2;
          DAT_febf6cb0 = 2;
          DAT_febf6cb1 = 2;
          return 0;
        }
        faci_read_command_area_twice_then_force_stop_78f7a();
        flash_set_software_enables(0);
        faci_select_dataflash_pe_or_read_mode_78c70(0);
        uVar1 = 8;
      }
      else {
        uVar1 = 0x83;
      }
    }
    else {
      uVar1 = 6;
    }
  }
  else {
    uVar1 = 0x82;
  }
  iVar3 = 1;
LAB_00078668:
  nvm_forward_flash_driver_error_7939c(0x5c,0,2,uVar1);
  return iVar3;
}

int dataflash_start_sixty_four_byte_block_erase_7867a(uint param_1,uint param_2)

{
  undefined4 uVar1;
  uint uVar2;
  int iVar3;
  int iVar4;
  uint uVar5;
  
  uVar2 = icus20_second_read_bit0();
  if (uVar2 == 0) {
    if (DAT_febf6cb0 == '\x01') {
      if (DAT_febf6cb2 == '\x0e') {
        iVar3 = dataflash_reject_out_of_range_or_unaligned_address_78d88(param_1,0x40);
        if (iVar3 != 0) {
          uVar1 = 2;
          goto LAB_00078754;
        }
        iVar3 = dataflash_reject_zero_or_out_of_range_length_78dca(param_1,param_2);
        if (iVar3 != 0) {
          uVar1 = 3;
          goto LAB_00078754;
        }
        return_only_stub_79d32();
        dataflash_configure_faci_operation_controls_78bc6();
        iVar4 = faci_select_dataflash_pe_or_read_mode_78c70(0x80);
        iVar3 = 1;
        if (iVar4 != 0) {
          return_only_stub_79d34();
          faci_select_dataflash_pe_or_read_mode_78c70(0);
          uVar1 = 7;
          goto LAB_00078754;
        }
        flash_set_software_enables(1);
        uVar2 = param_2 >> 6;
        if ((param_2 & 0x3f) != 0) {
          uVar2 = uVar2 + 1;
        }
        uVar5 = faci_submit_range_command(param_1,param_1 + 0x3f,' ');
        return_only_stub_79d34();
        if (uVar5 == 1) {
          DAT_febf6c60 = param_1 + 0x40;
          DAT_febf6c68 = uVar2 * 0x40 + param_1 + -1;
          DAT_febf6cac = 1;
          DAT_febf6cb0 = 2;
          DAT_febf6cb1 = 2;
          return 0;
        }
        faci_read_command_area_twice_then_force_stop_78f7a();
        flash_set_software_enables(0);
        faci_select_dataflash_pe_or_read_mode_78c70(0);
        uVar1 = 7;
      }
      else {
        uVar1 = 0x83;
      }
    }
    else {
      uVar1 = 6;
    }
  }
  else {
    uVar1 = 0x82;
  }
  iVar3 = 1;
LAB_00078754:
  nvm_forward_flash_driver_error_7939c(0x5c,0,1,uVar1);
  return iVar3;
}

void dataflash_abort_operation_and_reset_driver_78766(void)

{
  uint uVar1;
  int iVar2;
  undefined4 unaff_r27;
  undefined1 uStack_11;
  
  uVar1 = icus20_second_read_bit0();
  if (uVar1 == 0) {
    return_only_stub_79d32();
    mask_eic379_interrupt_and_sync_78b90();
    return_only_stub_79d34();
    iVar2 = faci_force_stop_in_dataflash_mode_and_exit_78d3e();
    if (iVar2 == 0) {
      if (DAT_febf6cb1 == '\x02') {
        DAT_febf6cb1 = '\x03';
        nvm_set_driver_completion_from_saved_result_74ed0();
      }
      dataflash_clear_saved_range_and_program_buffer_78af8();
      DAT_febf6cb0 = 1;
      if (DAT_febf6cb2 == '\x0f') {
        uStack_11 = 5;
        nvm_forward_pointed_suspend_result_793dc(&uStack_11);
      }
      DAT_febf6cb3 = 0;
      DAT_febf6cb2 = '\x0e';
    }
    else {
      unaff_r27 = 6;
      DAT_febf6cb1 = '\x01';
    }
    flash_set_software_enables(0);
    if (iVar2 == 0) {
      return;
    }
  }
  else {
    unaff_r27 = 0x82;
    DAT_febf6cb1 = '\x01';
  }
  nvm_forward_flash_driver_error_7939c(0x5c,0,3,unaff_r27);
  return;
}

void dataflash_poll_and_advance_active_operation_787fa(void)

{
  byte bVar1;
  uint uVar2;
  int iVar3;
  byte bStack_9;
  
  bStack_9 = 0;
  uVar2 = icus20_second_read_bit0();
  if (uVar2 != 0) {
    return;
  }
  if (DAT_febf6cb0 != '\x02') {
    faci_select_dataflash_pe_or_read_mode_78c70(0);
    DAT_febf6cb0 = 1;
    return;
  }
  if (DAT_febf6cb2 != '\x0e') {
    return;
  }
  if (DAT_febf6cb3 < 2) {
    iVar3 = faci_poll_ready_and_decode_result_byte_790d6(&bStack_9);
    if (iVar3 == 1) goto LAB_0007883e;
  }
  else {
    if (DAT_febf6cb3 != 2) {
      faci_force_stop_in_dataflash_mode_and_exit_78d3e();
      faci_select_dataflash_pe_or_read_mode_78c70(0);
      bVar1 = DAT_febf6cb3;
      goto LAB_00078870;
    }
    DAT_febf6cb3 = 0;
LAB_0007883e:
    iVar3 = dataflash_submit_next_saved_program_or_erase_unit_78f92(&bStack_9);
    if ((iVar3 == 1) && (iVar3 = faci_select_dataflash_pe_or_read_mode_78c70(0), iVar3 != 0)) {
      bStack_9 = (byte)iVar3;
    }
  }
  bVar1 = bStack_9;
  if (bStack_9 == 1) {
    return;
  }
LAB_00078870:
  dataflash_finalize_job_and_notify_result_79164(bVar1);
  flash_set_software_enables(0);
  return;
}

undefined1 dataflash_get_driver_state_7888c(void)

{
  return DAT_febf6cb0;
}

undefined1 dataflash_get_job_result_78896(void)

{
  return DAT_febf6cb1;
}

uint dataflash_read_words(uint dataflash_offset,uint *destination,uint byte_count)

{
  uint uVar1;
  int iVar2;
  
  uVar1 = icus20_second_read_bit0();
  if (uVar1 == 0) {
    if (DAT_febf6cb0 == '\x01') {
      if (DAT_febf6cb2 == '\x0e') {
        iVar2 = is_null_program_source_78d80(camry_host_addr(destination));
        if (((iVar2 == 0) && (iVar2 = dataflash_reject_out_of_range_or_unaligned_address_78d88(dataflash_offset,4), iVar2 == 0)) &&
           (iVar2 = dataflash_reject_invalid_program_range_78d9e(dataflash_offset,byte_count,4), iVar2 == 0)) {
          uVar1 = dataflash_copy_words_ecc(dataflash_offset, camry_host_addr(destination), byte_count);
          if (uVar1 == 0) {
            uVar1 = 2;
          }
          else {
            uVar1 = 5;
          }
        }
        else {
          uVar1 = 3;
        }
      }
      else {
        uVar1 = 0xc;
      }
    }
    else {
      uVar1 = 4;
    }
  }
  else {
    uVar1 = 0xb;
  }
  return uVar1;
}

uint dataflash_blank_check(uint dataflash_offset,uint byte_count)

{
  uint uVar1;
  int iVar2;
  
  uVar1 = icus20_second_read_bit0();
  if (uVar1 == 0) {
    if (DAT_febf6cb0 == '\x01') {
      if (DAT_febf6cb2 == '\x0e') {
        iVar2 = dataflash_reject_out_of_range_or_unaligned_address_78d88(dataflash_offset,4);
        if ((iVar2 == 0) && (iVar2 = dataflash_reject_invalid_program_range_78d9e(dataflash_offset,byte_count,4), iVar2 == 0)) {
          return_only_stub_79d32();
          dataflash_configure_faci_operation_controls_78bc6();
          iVar2 = faci_select_dataflash_pe_or_read_mode_78c70(0x80);
          if (iVar2 == 0) {
            flash_set_software_enables(1);
            DAT_febf6cac = 3;
            uVar1 = faci_submit_range_command
                              (dataflash_offset,(byte_count + dataflash_offset) - 1,'q');
            return_only_stub_79d34();
            if (uVar1 == 1) {
              uVar1 = dataflash_wait_completion_and_translate_result_791b2();
            }
            else {
              faci_read_command_area_twice_then_force_stop_78f7a();
              faci_select_dataflash_pe_or_read_mode_78c70(0);
              uVar1 = 8;
            }
            flash_set_software_enables(0);
          }
          else {
            return_only_stub_79d34();
            faci_select_dataflash_pe_or_read_mode_78c70(0);
            uVar1 = 8;
          }
        }
        else {
          uVar1 = 3;
        }
      }
      else {
        uVar1 = 0xc;
      }
    }
    else {
      uVar1 = 4;
    }
  }
  else {
    uVar1 = 0xb;
  }
  return uVar1;
}

int dataflash_request_suspend_789e2(void)

{
  uint uVar1;
  int iVar2;
  undefined1 uStack_d;
  
  uVar1 = icus20_second_read_bit0();
  if (uVar1 == 0) {
    if (DAT_febf6cb2 == '\x0e') {
      if (DAT_febf6cb0 == '\x02') {
        nvm_copy_suspend_policy_to_output_793c8(&uStack_d);
        iVar2 = dataflash_select_suspend_policy_7922c(uStack_d);
        if (iVar2 == 2) {
          DAT_febf6cb2 = 0xf;
          return_only_stub_79d32();
          unmask_eic379_interrupt_and_sync_792dc();
          return_only_stub_79d34();
          return 2;
        }
        if (iVar2 != 10) {
          return iVar2;
        }
        iVar2 = dataflash_save_suspend_result_and_exit_pe_mode_7927e();
        if (iVar2 != 0) {
          return 8;
        }
      }
      iVar2 = 10;
      DAT_febf6cb2 = '\x10';
    }
    else {
      iVar2 = 0xc;
    }
  }
  else {
    iVar2 = 0xb;
  }
  return iVar2;
}

undefined4 dataflash_resume_suspended_operation_78a56(void)

{
  uint uVar1;
  int iVar2;
  
  uVar1 = icus20_second_read_bit0();
  if (uVar1 != 0) {
    return 0xb;
  }
  if (DAT_febf6cb2 != '\x10') {
    return 0xc;
  }
  if (DAT_febf6cb0 == '\x02') {
    return_only_stub_79d32();
    dataflash_configure_faci_operation_controls_78bc6();
    return_only_stub_79d34();
    iVar2 = faci_select_dataflash_pe_or_read_mode_78c70(0x80);
    if (iVar2 != 0) {
LAB_00078ab8:
      faci_select_dataflash_pe_or_read_mode_78c70(0);
      return 8;
    }
    flash_set_software_enables(1);
    if (DAT_febf6cb3 == '\x01') {
      faci_resume_if_suspend_bits_set_792c0();
    }
    else {
      iVar2 = faci_has_program_or_erase_suspend_bits_792a6();
      if (iVar2 != 0) goto LAB_00078ab8;
    }
  }
  DAT_febf6cb2 = 0xe;
  return 2;
}

undefined1 dataflash_get_suspend_phase_78aca(void)

{
  return DAT_febf6cb2;
}

uint load_u32(uint *source)

{
  #ifdef CAMRY_HOST
  if (!camry_peripheral_file)
    return camry_read32(camry_host_addr(source));
#endif
  return *(const volatile uint32_t *)source;
}

void dataflash_clear_saved_range_and_program_buffer_78af8(void)

{
  int iVar1;
  uint uVar2;
  
  DAT_febf6c64 = 0;
  uVar2 = 0;
  DAT_febf6c60 = 0;
  DAT_febf6c68 = 0;
  DAT_febf6cac = 0;
  do {
    iVar1 = uVar2 * 4;
    uVar2 = uVar2 + 1;
    *(undefined4 *)(((undefined *)camry_host_ptr((uint32_t)(0xfebf6c6cu + (uint32_t)(iVar1) * 1u)))) = 0;
  } while (uVar2 < 0x10);
  return;
}

void dataflash_initialize_idle_state_78b1c(void)

{
  dataflash_clear_saved_range_and_program_buffer_78af8();
  DAT_febf6cb1 = 1;
  DAT_febf6cb3 = 0;
  DAT_febf6cb2 = 0xe;
  DAT_febf6cb0 = 1;
  return;
}

void flash_set_software_enables(uint value)

{
  uint uVar1;
  
  camry_write32(0xfff8a430u, value);
  camry_write32(0xfff82410u, value);
  uVar1 = camry_read32(0xfff82410u);
  __synchronize();
  return;
}

void dataflash_reset_interrupt_and_software_controls_78b60(void)

{
  camry_write8(0xffa10014u, '\0');
  camry_write16(0xffa1008cu, 0x2d00);
  camry_write8(0xffa1009cu, '\0');
  flash_set_software_enables(0);
  return;
}

undefined1 mask_eic379_interrupt_and_sync_78b90(void)

{
  byte bVar1;
  undefined1 uVar2;
  
  bVar1 = camry_read8(0xffffb2f6u);
  camry_write8(0xffffb2f6u, bVar1 | 0x80);
  uVar2 = camry_read8(0xffffb2f6u);
  __synchronize();
  return uVar2;
}

void dataflash_set_fpckar_1e28_78bb0(void)

{
  camry_write16(0xffa100e4u, 0x1e28);
  return;
}

void dataflash_configure_faci_operation_controls_78bc6(void)

{
  mask_eic379_interrupt_and_sync_78b90();
  camry_write16(0xffa1008cu, 0x2d00);
  camry_write16(0xffa10104u, 0xa630);
  camry_write8(0xffa100f0u, '\0');
  dataflash_set_fpckar_1e28_78bb0();
  return;
}

uint read_fstatr_ready_bit_78bfa(void)

{
  uint uVar1;
  
  uVar1 = camry_read32(0xffa10080u);
  return (uVar1 & 0x8000) >> 0xf;
}

int reset_fsuinitr_if_flash_ready_78c12(void)

{
  int iVar1;
  
  iVar1 = read_fstatr_ready_bit_78bfa();
  if (iVar1 == 1) {
    camry_write16(0xffa1008cu, 0x2d00);
  }
  return iVar1;
}

void faci_clear_error_status_78c30(void)

{
  uchar uVar1;
  uint uVar2;
  
  uVar2 = camry_read32(0xffa10080u);
  if (((uVar2 & 0x4000) == 0x4000) && (uVar1 = camry_read8(0xffa10010u), uVar1 != '\x10')) {
    camry_write8(0xffa10010u, '\x10');
  }
  camry_write8(0xffa20000u, 'P');
  return;
}

undefined4 faci_select_dataflash_pe_or_read_mode_78c70(ushort param_1)

{
  uint uVar1;
  ushort uVar2;
  undefined4 uVar3;
  
  if (param_1 == 0) {
    uVar1 = camry_read32(0xffa10080u);
    if ((uVar1 & 0x7000) != 0) {
      faci_clear_error_status_78c30();
    }
    camry_write16(0xffa10084u, 0xaa00);
  }
  else {
    uVar2 = camry_read16(0xffa10084u);
    if (param_1 != (uVar2 & 0x81)) {
      camry_write16(0xffa10084u, 0xaa80);
      camry_write32(0xffa10030u, 0);
      camry_write32(0xffa10034u, 0);
    }
  }
  uVar2 = camry_read16(0xffa10084u);
  uVar2 = camry_read16(0xffa10084u);
  if (param_1 == (uVar2 & 0x81)) {
    uVar3 = 0;
  }
  else {
    uVar3 = 7;
  }
  return uVar3;
}

uint faci_force_stop_and_poll(void)

{
  uchar *destination;
  uint uVar1;
  
  uVar1 = load_u32(((uint *)camry_host_ptr((uint32_t)((0xffa10080u)))));
  if (((uVar1 & 0x4000) == 0x4000) && (uVar1 = load_u8(((const void *)camry_host_ptr((uint32_t)((0xffa10010u))))), uVar1 != 0x10)) {
    store_u8(((void *)camry_host_ptr((uint32_t)((int)0xffa10010))), '\x10');
  }
  store_u8(((void *)camry_host_ptr((uint32_t)((0xffa20000u)))), 0xb3);
  uVar1 = poll_word_masks((0xffa10080u),0x8000,0x8000,0xe5);
  if (uVar1 < 2) {
    uVar1 = 0;
  }
  else {
    uVar1 = 8;
  }
  return uVar1;
}

uint faci_force_stop_in_dataflash_mode_and_exit_78d3e(void)

{
  undefined2 uVar1;
  uint uVar2;
  
  uVar2 = faci_select_dataflash_pe_or_read_mode_78c70(0x80);
  if (uVar2 == 0) {
    uVar2 = faci_force_stop_and_poll();
    if (uVar2 == 0) {
      uVar2 = faci_select_dataflash_pe_or_read_mode_78c70(0);
      return uVar2;
    }
    uVar1 = (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xffa20000u))));
    uVar1 = (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xffa20000u))));
    faci_clear_error_status_78c30();
  }
  faci_select_dataflash_pe_or_read_mode_78c70(0);
  return uVar2;
}

bool is_null_program_source_78d80(int param_1)

{
  return param_1 == 0;
}

undefined4 dataflash_reject_out_of_range_or_unaligned_address_78d88(uint param_1,int param_2)

{
  if ((param_1 < 0x8000) && ((param_2 - 1U & param_1) == 0)) {
    return 0;
  }
  return 1;
}

bool dataflash_reject_invalid_program_range_78d9e(uint param_1,uint param_2,int param_3)

{
  if ((((param_2 != 0) && (param_2 < 0x41)) && ((param_3 - 1U & param_1) == 0)) &&
     ((param_3 - 1U & param_2) == 0)) {
    return 0x7fff < (param_2 + param_1) - 1;
  }
  return true;
}

bool dataflash_reject_zero_or_out_of_range_length_78dca(int param_1,int param_2)

{
  if (param_2 != 0) {
    return 0x7fff < (param_2 + param_1) - 1U;
  }
  return true;
}

uint faci_check_dataflash_addresses(void)

{
  uint uVar1;
  uint uVar2;
  
  uVar2 = camry_read32(0xffa10030u);
  if (uVar2 < 0x8000) {
    uVar2 = 1;
  }
  else {
    uVar2 = 7;
  }
  uVar1 = camry_read32(0xffa10034u);
  if (0x7fff < (int)uVar1 + 3) {
    uVar2 = 7;
  }
  return uVar2;
}

undefined1 clear_eic379_high_byte_and_sync_78e10(void)

{
  undefined1 uVar1;
  
  camry_write8(0xffffb2f7u, 0);
  uVar1 = camry_read8(0xffffb2f7u);
  __synchronize();
  return uVar1;
}

uint faci_submit_program_halfwords_78e2a(undefined4 *param_1,uint param_2,uint param_3)

{
  uint uVar1;
  undefined4 uVar2;
  uint uVar3;
  uint uVar4;
  undefined2 local_20 [4];
  
  uVar3 = 0;
  clear_eic379_high_byte_and_sync_78e10();
  camry_write32(0xffa10030u, param_2);
  camry_write32(0xffa10034u, (param_2 + param_3) - 1);
  camry_write8(0xffa20000u, 0xe8);
  camry_write8(0xffa20000u, (uchar)(param_3 >> 1));
  do {
    uVar2 = *param_1;
    param_1 = param_1 + 1;
    local_20[0] = (short)uVar2;
    uVar3 = uVar3 + 1;
    local_20[1] = (short)((uint)uVar2 >> 0x10);
    for (uVar4 = 0; uVar4 < param_3 >> 1; uVar4 = uVar4 + 1) {
      (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xffa20000u)))) = local_20[uVar4];
      uVar1 = camry_read32(0xffa10080u);
      if ((uVar1 >> 10 & 1) != 0) {
        return 7;
      }
    }
  } while (uVar3 < param_3 >> 2);
  uVar3 = faci_check_dataflash_addresses();
  if (uVar3 == 1) {
    camry_write8(0xffa20000u, 0xd0);
  }
  return uVar3;
}

uint faci_submit_range_command(uint start_offset,uint end_offset,uchar command)

{
  int extraout_r6;
  uint uVar1;
  uint extraout_r10;
  
  clear_eic379_high_byte_and_sync_78e10();
  if (command == 'q') {
    store_u8(((void *)camry_host_ptr((uint32_t)((0xffa100d0u)))), '\0');
  }
  store_u16(((void *)camry_host_ptr((uint32_t)((0xffa100e0u)))), 0);
  store_u32(((void *)camry_host_ptr((uint32_t)((0xffa10030u)))), start_offset);
  store_u32(((uint *)camry_host_ptr((uint32_t)(((int)((int)0xffa10030)) + 4))),end_offset);
  store_u8(((void *)camry_host_ptr((uint32_t)((0xffa20000u)))), command);
  uVar1 = faci_check_dataflash_addresses();
  if (uVar1 == 1) {
    store_u8(((void *)camry_host_ptr((uint32_t)((0xffa20000u)))), 0xd0);
    uVar1 = ((uint)(uVar1));
  }
  return uVar1;
}

uint faci_read_command_area_twice_then_force_stop_78f7a(void)

{
  undefined2 uVar1;
  
  uVar1 = (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xffa20000u))));
  uVar1 = (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xffa20000u))));
  return faci_force_stop_and_poll();
}

undefined4 dataflash_submit_next_saved_program_or_erase_unit_78f92(char *param_1)

{
  char cVar1;
  uint uVar2;
  undefined4 uVar3;
  
  if (DAT_febf6c60 < DAT_febf6c68) {
    if (DAT_febf6cac == '\x02') {
      return_only_stub_79d32();
      cVar1 = faci_submit_program_halfwords_78e2a(((undefined4 *)camry_host_ptr((uint32_t)(DAT_febf6c64))), DAT_febf6c60, 4);
      *param_1 = cVar1;
      return_only_stub_79d34();
      DAT_febf6c60 = DAT_febf6c60 + 4;
      DAT_febf6c64 = DAT_febf6c64 + 4;
    }
    else if (DAT_febf6cac == '\x01') {
      return_only_stub_79d32();
      uVar2 = faci_submit_range_command(DAT_febf6c60,DAT_febf6c60 + 0x3f,' ');
      *param_1 = (char)uVar2;
      return_only_stub_79d34();
      DAT_febf6c60 = DAT_febf6c60 + 0x40;
    }
    else {
      *param_1 = '\a';
    }
    if (*param_1 != '\x01') {
      faci_read_command_area_twice_then_force_stop_78f7a();
      faci_select_dataflash_pe_or_read_mode_78c70(0);
    }
    uVar3 = 0;
  }
  else {
    uVar3 = 1;
  }
  return uVar3;
}
