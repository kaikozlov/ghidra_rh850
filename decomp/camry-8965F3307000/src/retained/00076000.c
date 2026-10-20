#include "common.h"

undefined4 nvm_poll_and_retry_alternate_record_erase_76018(undefined4 param_1,int *param_2)

{
  uint32_t puVar1;
  int iVar2;
  undefined4 uVar3;
  undefined4 uVar4;
  
  puVar1 = 0x23dfcu;
  iVar2 = nvm_get_state_machine_result_word_783d4();
  uVar3 = nvm_get_storage_handle_77c9e();
  if (iVar2 == 1) {
    uVar3 = 0x1e;
  }
  else {
    if (DAT_febf6c52 < (byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x3b2f)))))) {
      DAT_febf6c52 = DAT_febf6c52 + 1;
      uVar4 = nvm_compute_next_record_slot_low_two_bits_7543c(DAT_febf6c3e);
      iVar2 = nvm_erase_record_slot_allocation_76e36(uVar3,uVar4);
      if (iVar2 == 2) {
        return 0xff;
      }
    }
    *param_2 = iVar2;
    uVar3 = 0;
  }
  return uVar3;
}

undefined4 nvm_step_blank_alternate_record_header_76072(undefined4 param_1,int *param_2)

{
  undefined4 uVar1;
  undefined4 uVar2;
  int iVar3;
  undefined4 uVar4;
  
  uVar4 = 0xff;
  uVar1 = nvm_get_storage_handle_77c9e();
  uVar2 = nvm_compute_next_record_slot_low_two_bits_7543c(DAT_febf6c3e);
  iVar3 = nvm_begin_record_slot_blank_fill_76f04(uVar1,uVar2);
  if (iVar3 != 2) {
    *param_2 = iVar3;
    uVar4 = 0;
  }
  return uVar4;
}

undefined4 nvm_poll_result_to_phase31_or_delay_760a6(undefined4 param_1,undefined4 param_2)

{
  int iVar1;
  undefined4 uVar2;
  
  iVar1 = nvm_get_state_machine_result_word_783d4();
  if (iVar1 == 1) {
    uVar2 = 0x1f;
  }
  else {
    uVar2 = nvm_delay_phase29_then_publish_result_75fb0(((undefined *)camry_host_ptr((uint32_t)(iVar1))), ((undefined4 *)camry_host_ptr((uint32_t)(param_2))));
  }
  return uVar2;
}

undefined4 nvm_step_gated_current_selector_marker1_760c6(int param_1,int *param_2)

{
  uint8_t stack_record_28[40];
  undefined4 *puVar1;
  undefined4 uVar2;
  int iVar3;
  undefined4 uVar4;
  undefined4 *puVar5;
  undefined4 uVar6;
  undefined4 *puVar7;
  
  puVar1 = ((uint32_t *)(stack_record_28));
  uVar6 = 0xff;
  uVar2 = nvm_get_storage_handle_77c9e();
  puVar7 = ((undefined4 *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)((param_1 + 4))))))));
  puVar5 = puVar7 + 5;
  do {
    uVar4 = *puVar7;
    puVar7 = puVar7 + 1;
    *puVar1 = uVar4;
    puVar1 = puVar1 + 1;
  } while (camry_host_addr(puVar5)!=camry_host_addr(puVar7));
  iVar3 = nvm_claim_marker_submission_when_gate_zero_74f88(stack_record_28[16]);
  if ((iVar3 != 0) && (iVar3 = nvm_submit_four_byte_record_marker_write_7808c(uVar2,DAT_febf6c3e,1), iVar3 != 2)) {
    *param_2 = iVar3;
    uVar6 = 0;
  }
  return uVar6;
}

undefined4 nvm_arm_and_step_current_selector_marker1_7611c(undefined4 param_1, undefined4 param_2)

{
  nvm_arm_record_marker_submission_74f72();
  return nvm_step_gated_current_selector_marker1_760c6(param_1, ((int *)camry_host_ptr((uint32_t)(param_2))));
}

undefined4 thunk_nvm_step_gated_current_selector_marker1_760c6(undefined4 param_1, undefined4 param_2)

{
  return nvm_step_gated_current_selector_marker1_760c6(param_1, ((int *)camry_host_ptr((uint32_t)(param_2))));
}

undefined4 nvm_switch_selector_and_choose_mode_phase_76138(undefined4 *param_1)

{
  uint32_t puVar1;
  uint uVar2;
  int iVar3;
  
  puVar1 = 0x23dfcu;
  DAT_febf6c3e = nvm_compute_next_record_slot_low_two_bits_7543c(DAT_febf6c3e);
  uVar2 = nvm_get_storage_handle_77c9e();
  if (uVar2 < (*((ushort *)camry_host_ptr((uint32_t)(puVar1 + 0x3b2c))))) {
    DAT_febf6c53 = 2;
    iVar3 = nvm_get_request_mode_77c64();
    if (iVar3 == 1) {
      DAT_febf6c52 = 0;
      return 2;
    }
    if (iVar3 == 2) {
      return 6;
    }
  }
  *param_1 = ((uint32_t)(0xfffbu));
  return 0;
}

undefined4 nvm_poll_marker_retry_or_switch_selector_7618e(undefined4 param_1,undefined4 *param_2)

{
  undefined4 camry_r10_0;

  uint32_t puVar1;
  uint32_t puVar2;
  undefined4 uVar3;
  
  puVar1 = 0x23dfcu;
  (camry_r10_0 = nvm_get_state_machine_result_word_783d4());
  puVar2 = (nvm_clear_record_marker_submission_latch_74f7e(), camry_r10_0);
  if (puVar2 == 0x1) {
    uVar3 = nvm_switch_selector_and_choose_mode_phase_76138(param_2);
  }
  else if (DAT_febf6c52 < (byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x3b2f)))))) {
    DAT_febf6c52 = DAT_febf6c52 + 1;
    nvm_arm_record_marker_submission_74f72();
    uVar3 = nvm_step_gated_current_selector_marker1_760c6(param_1,param_2);
  }
  else {
    *param_2 = puVar2;
    uVar3 = 0;
    if (puVar2 == 0xfffdu) {
      nvm_mark_attempt_compare_mismatch_76992();
    }
  }
  return uVar3;
}

void nvm_reset_commit_step_state_761e6(void)

{
  DAT_febf6c56 = 0;
  DAT_febf6c57 = 0;
  DAT_febf6c58 = 0;
  thunk_nvm_reset_active_record_and_checksum_772f8();
  return;
}

undefined4 nvm_reset_commit_step_state_return_one_7620a(void)

{
  nvm_reset_commit_step_state_761e6();
  return 1;
}

void nvm_store_raw_result_select_phase1_76224(undefined4 param_1)

{
  nvm_set_state_machine_result_word_783ca(param_1);
  nvm_set_state_machine_event_783c0(1);
  return;
}

void nvm_store_raw_result_select_phase2_76236(undefined4 param_1)

{
  nvm_set_state_machine_result_word_783ca(param_1);
  nvm_set_state_machine_event_783c0(2);
  return;
}

void nvm_store_raw_result_mark_commit_ready_76248(undefined4 param_1)

{
  nvm_set_state_machine_result_word_783ca(param_1);
  DAT_febf6c58 = 1;
  return;
}

undefined4 nvm_retry_base_allocation_erase_7625e(int param_1,int *param_2)

{
  uint32_t puVar1;
  undefined4 uVar2;
  
  puVar1 = 0x23dfcu;
  uVar2 = nvm_get_storage_handle_77c9e();
  if (DAT_febf6c57 < (byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x3b30)))))) {
    DAT_febf6c57 = DAT_febf6c57 + 1;
    param_1 = nvm_erase_base_record_allocation_77982(uVar2);
    if (param_1 == 2) {
      return 1;
    }
  }
  *param_2 = param_1;
  return 0;
}

undefined4 nvm_delay_commit_retry_then_publish_76298(undefined *param_1,undefined4 *param_2)

{
  undefined4 uVar1;
  
  if (DAT_febf6c57 < DAT_0002792c) {
    DAT_febf6c57 = DAT_febf6c57 + 1;
    uVar1 = 1;
  }
  else {
    *param_2 = camry_host_addr(param_1);
    uVar1 = 0;
    if (camry_host_addr(param_1)==((uint32_t)(0xfffdu))) {
      nvm_mark_attempt_compare_mismatch_76992();
    }
  }
  return uVar1;
}

undefined4 nvm_choose_commit_mode_phase_762ca(void)

{
  int iVar1;
  undefined4 uVar2;
  
  iVar1 = nvm_get_request_mode_77c64();
  if (iVar1 == 1) {
    DAT_febf6c57 = 0;
    uVar2 = 1;
  }
  else if (iVar1 == 2) {
    uVar2 = 4;
  }
  else {
    uVar2 = 0xff;
  }
  return uVar2;
}

undefined4 nvm_step_erase_base_allocation_762f2(undefined4 param_1,int *param_2)

{
  undefined4 uVar1;
  int iVar2;
  undefined4 uVar3;
  
  uVar3 = 0xff;
  uVar1 = nvm_get_storage_handle_77c9e();
  iVar2 = nvm_erase_base_record_allocation_77982(uVar1);
  if (iVar2 != 2) {
    *param_2 = iVar2;
    uVar3 = 0;
  }
  return uVar3;
}

undefined4 nvm_poll_result_to_phase2_or_retry_erase_76316(undefined4 param_1,undefined4 param_2)

{
  int iVar1;
  undefined4 uVar2;
  
  iVar1 = nvm_get_state_machine_result_word_783d4();
  if (iVar1 == 1) {
    uVar2 = 2;
  }
  else {
    uVar2 = nvm_retry_base_allocation_erase_7625e(iVar1, ((int *)camry_host_ptr((uint32_t)(param_2))));
  }
  return uVar2;
}

undefined4 nvm_step_write_base_record_76334(undefined4 param_1,int *param_2)

{
  undefined4 uVar1;
  undefined4 uVar2;
  int iVar3;
  undefined4 uVar4;
  
  uVar4 = 0xff;
  uVar1 = nvm_get_storage_handle_77c9e();
  uVar2 = nvm_get_write_source_77cbe();
  iVar3 = nvm_begin_base_record_write_with_commit_checksum_779b2(uVar1,uVar2);
  if (iVar3 != 2) {
    *param_2 = iVar3;
    uVar4 = 0;
  }
  return uVar4;
}

undefined4 nvm_poll_result_to_phase3_or_delay_76360(undefined4 param_1,undefined4 param_2)

{
  int iVar1;
  undefined4 uVar2;
  
  iVar1 = nvm_get_state_machine_result_word_783d4();
  if (iVar1 == 1) {
    uVar2 = 3;
  }
  else {
    uVar2 = nvm_delay_commit_retry_then_publish_76298(((undefined *)camry_host_ptr((uint32_t)(iVar1))), ((undefined4 *)camry_host_ptr((uint32_t)(param_2))));
  }
  return uVar2;
}

void nvm_arm_commit_marker_gate_7637e(void)

{
  DAT_febf6c56 = 1;
  return;
}

undefined4 nvm_consume_commit_marker_gate_if_zero_7638a(char param_1)

{
  undefined4 uVar1;
  
  uVar1 = 0;
  if ((param_1 == '\0') && (DAT_febf6c56 == '\x01')) {
    DAT_febf6c56 = '\x02';
    uVar1 = 1;
  }
  return uVar1;
}

undefined4 nvm_step_gated_commit_trailer_write_763a4(int param_1,int *param_2)

{
  uint8_t stack_record_28[40];
  undefined4 *puVar1;
  undefined4 uVar2;
  int iVar3;
  undefined4 uVar4;
  undefined4 *puVar5;
  undefined4 uVar6;
  undefined4 *puVar7;
  
  puVar1 = ((uint32_t *)(stack_record_28));
  uVar6 = 0xff;
  uVar2 = nvm_get_storage_handle_77c9e();
  puVar7 = ((undefined4 *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)((param_1 + 4))))))));
  puVar5 = puVar7 + 5;
  do {
    uVar4 = *puVar7;
    puVar7 = puVar7 + 1;
    *puVar1 = uVar4;
    puVar1 = puVar1 + 1;
  } while (camry_host_addr(puVar5)!=camry_host_addr(puVar7));
  iVar3 = nvm_consume_commit_marker_gate_if_zero_7638a(stack_record_28[16]);
  if ((iVar3 != 0) && (iVar3 = camry_host_addr(nvm_write_commit_trailer_marker_77a36(uVar2)), iVar3 != 2)) {
    *param_2 = iVar3;
    uVar6 = 0;
  }
  return uVar6;
}

undefined4 nvm_arm_and_step_commit_trailer_write_763f0(undefined4 param_1, undefined4 param_2)

{
  nvm_arm_commit_marker_gate_7637e();
  return nvm_step_gated_commit_trailer_write_763a4(param_1, ((int *)camry_host_ptr((uint32_t)(param_2))));
}

undefined4 thunk_nvm_step_gated_commit_trailer_write_763a4(undefined4 param_1, undefined4 param_2)

{
  return nvm_step_gated_commit_trailer_write_763a4(param_1, ((int *)camry_host_ptr((uint32_t)(param_2))));
}

void nvm_clear_commit_marker_gate_7640c(void)

{
  DAT_febf6c56 = 0;
  return;
}

undefined4 nvm_poll_commit_result_and_finish_or_delay_76416(undefined4 param_1,undefined4 param_2)

{
  undefined4 camry_r10_0;

  int iVar1;
  int iVar2;
  undefined4 uVar3;
  
  iVar1 = (camry_r10_0 = nvm_get_state_machine_result_word_783d4());
  iVar2 = (nvm_clear_commit_marker_gate_7640c(), (int)(uintptr_t)camry_r10_0);
  if ((iVar2 == 1) || (iVar1 == 0xffff)) {
    uVar3 = 0;
    nvm_snapshot_completion_mode_handle_and_reset_request_77ce8();
    nvm_set_completion_raw_result_77d14(iVar1);
    nvm_finish_physical_result();
    nvm_reset_commit_step_state_761e6();
  }
  else {
    uVar3 = nvm_delay_commit_retry_then_publish_76298(((undefined *)camry_host_ptr((uint32_t)(iVar2))), ((undefined4 *)camry_host_ptr((uint32_t)(param_2))));
  }
  return uVar3;
}

undefined4 nvm_finish_read_when_commit_ready_76456(void)

{
  undefined4 uVar1;
  
  if (DAT_febf6c58 == '\x01') {
    uVar1 = nvm_get_state_machine_result_word_783d4();
    nvm_snapshot_completion_mode_handle_and_reset_request_77ce8();
    nvm_set_completion_raw_result_77d14(uVar1);
    nvm_finish_physical_result();
    nvm_reset_commit_step_state_761e6();
    uVar1 = 0;
  }
  else {
    uVar1 = 0xff;
  }
  return uVar1;
}

undefined4 nvm_begin_current_record_read_and_finish_ready_7648a(void)

{
  ushort handle;
  uchar *destination;
  
  handle = nvm_get_storage_handle_77c9e();
  destination = ((uchar *)camry_host_ptr((uint32_t)(nvm_get_read_destination_77cde())));
  DAT_febf6c58 = 0;
  nvm_begin_record_read(handle,destination,'\0');
  return nvm_finish_read_when_commit_ready_76456();
}

undefined4 nvm_continue_payload_read_and_finish_ready_764b2(void)

{
  thunk_nvm_continue_record_payload_read_77824();
  return nvm_finish_read_when_commit_ready_76456();
}

void nvm_set_service_enabled_764c2(void)

{
  DAT_febf6b77 = 1;
  return;
}

void nvm_reset_physical_result_and_enable_service_764ce(void)

{
  nvm_physical_result_state = '\0';
  nvm_set_service_enabled_764c2();
  return;
}

uint32_t run_init_chain_764e2(void)

{
  uint32_t camry_r10_result;
  nvm_initialize_dataflash_read_controls();
  nvm_reset_physical_result_and_enable_service_764ce();
  thunk_nvm_reset_secondary_result_and_attempt_flags_76782();
  nvm_clear_flash_callback_guard_781a0();
  nvm_reset_request_and_completion_contexts_77c32();
  (camry_r10_result = thunk_nvm_initialize_driver_transfer_context_74b3c());
  (camry_r10_result = nvm_reset_block_and_two_descriptor_callbacks_782de());
  return_only_stub_7936c();
  return camry_r10_result;
}

undefined2 zero_extend_u16_identity_7650c(undefined2 param_1)

{
  return param_1;
}

undefined4 nvm_admit_record_read_mode2_76512(undefined2 param_1,undefined4 param_2)

{
  uint32_t puVar1;
  int iVar2;
  undefined4 uVar3;
  
  puVar1 = 0x23dfcu;
  uVar3 = 1;
  iVar2 = nvm_get_request_mode_77c64();
  if (iVar2 == 0) {
    iVar2 = camry_host_addr(nvm_validate_and_set_storage_handle_77c82(param_1));
    if ((iVar2 == 1) && (iVar2 = camry_host_addr(nvm_validate_and_set_read_destination_77cc8(param_2)), iVar2 == 1)) {
      nvm_set_request_mode_77c5a(2);
      nvm_set_state_machine_timeout_783de((*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + 0x3b1c)))));
      uVar3 = 0;
    }
    else {
      uVar3 = 2;
    }
  }
  return uVar3;
}

undefined4 nvm_request_record_read_mode2_76572(undefined2 param_1,undefined4 param_2,undefined4 param_3)

{
  uchar result_class;
  undefined4 uVar1;
  int iVar2;
  
  nvm_set_request_handle_snapshot_77c6e((uint)(ushort)param_1);
  uVar1 = zero_extend_u16_identity_7650c(param_1);
  iVar2 = nvm_admit_record_read_mode2_76512(uVar1,param_3);
  if (iVar2 == 0) {
    nvm_set_physical_result_state('\x02');
    nvm_begin_attempt_snapshot_76af4();
    uVar1 = 0;
  }
  else {
    uVar1 = 1;
    if (iVar2 == 2) {
      result_class = '\"';
    }
    else {
      result_class = '!';
    }
    nvm_report_physical_class(result_class);
  }
  return uVar1;
}

undefined4 nvm_admit_record_write_mode1_765ba(undefined2 param_1,undefined4 param_2)

{
  uint32_t puVar1;
  int iVar2;
  undefined4 uVar3;
  
  puVar1 = 0x23dfcu;
  uVar3 = 1;
  iVar2 = nvm_get_request_mode_77c64();
  if (iVar2 == 0) {
    iVar2 = camry_host_addr(nvm_validate_and_set_storage_handle_77c82(param_1));
    if ((iVar2 == 1) && (iVar2 = camry_host_addr(nvm_validate_and_set_write_source_77ca8(param_2)), iVar2 == 1)) {
      nvm_set_request_mode_77c5a(1);
      nvm_set_state_machine_timeout_783de((*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + 0x3b1c)))));
      uVar3 = 0;
    }
    else {
      uVar3 = 2;
    }
  }
  return uVar3;
}

undefined4 nvm_request_record_write_mode1_765fc(undefined2 param_1,undefined4 param_2)

{
  uchar result_class;
  undefined4 uVar1;
  int iVar2;
  
  nvm_set_request_handle_snapshot_77c6e((uint)(ushort)param_1);
  uVar1 = zero_extend_u16_identity_7650c(param_1);
  iVar2 = nvm_admit_record_write_mode1_765ba(uVar1,param_2);
  if (iVar2 == 0) {
    nvm_set_physical_result_state('\x02');
    nvm_begin_attempt_snapshot_76af4();
    uVar1 = 0;
  }
  else {
    uVar1 = 1;
    if (iVar2 == 2) {
      result_class = '\"';
    }
    else {
      result_class = '!';
    }
    nvm_report_physical_class(result_class);
  }
  return uVar1;
}

void nvm_clear_service_enabled_76644(void)

{
  DAT_febf6b77 = 0;
  return;
}

void nvm_cancel_physical_operation(void)

{
  int iVar1;
  
  nvm_reset_request_and_completion_contexts_77c32();
  nvm_reset_block_and_two_descriptor_callbacks_782de();
  nvm_enter_paired_call_guard_79aaa();
  nvm_clear_service_enabled_76644();
  iVar1 = nvm_suspend_state_is_nonzero_79b0e();
  if (iVar1 == 0) {
    nvm_abort_sync_transfer_and_reset_driver_state_74e94();
    nvm_set_service_enabled_764c2();
  }
  nvm_leave_paired_call_guard_79abe();
  nvm_set_physical_result_state('\x03');
  nvm_set_secondary_result_state5_76ae6();
  return_only_stub_73ca2();
  return;
}

undefined4 nvm_classify_active_or_enabled_driver_state_76688(void)

{
  int iVar1;
  undefined4 uVar2;
  
  iVar1 = nvm_get_request_mode_77c64();
  if (iVar1 == 1 || iVar1 == 2) {
    uVar2 = 2;
  }
  else if ((DAT_febf6b77 == '\0') || (iVar1 = nvm_get_sync_driver_busy_status_74e6e(), iVar1 != 1 && iVar1 != 2)) {
    uVar2 = 1;
  }
  else {
    uVar2 = 3;
  }
  return uVar2;
}

undefined4 thunk_nvm_classify_active_or_enabled_driver_state_76688(void)

{
  return nvm_classify_active_or_enabled_driver_state_76688();
}

uchar nvm_get_physical_result_state_766c6(void)

{
  return nvm_physical_result_state;
}

void nvm_guarded_reset_read_controls_and_operation_state_766f4(void)

{
  int iVar1;
  
  nvm_enter_paired_call_guard_79aaa();
  iVar1 = nvm_get_direct_mode_or_suspend_marker_79c76();
  if (iVar1 == 0) {
    nvm_initialize_dataflash_read_controls_wrapper_79388();
    nvm_abort_flash_unless_phase_fourteen_781be();
    nvm_poll_driver_and_optional_timers_74e46(0);
    nvm_clear_completed_request_mode_77c42();
    nvm_step_state_machine_and_tick_timeout_78466();
  }
  nvm_leave_paired_call_guard_79abe();
  return;
}

void thunk_nvm_set_service_enabled_764c2(void)

{
  nvm_set_service_enabled_764c2();
  return;
}

bool nvm_is_service_enabled_76762(void)

{
  return DAT_febf6b77 != '\0';
}

uint32_t nvm_refresh_driver_result_and_enable_service_76772(void)

{
  uint32_t camry_r10_result;
  (camry_r10_result = nvm_abort_sync_transfer_and_reset_driver_state_74e94());
  nvm_set_service_enabled_764c2();
  return camry_r10_result;
}

void nvm_reset_secondary_result_and_attempt_flags_76782(void)

{
  nvm_secondary_result_state = '\0';
  nvm_physical_attempt_flags = '\0';
  return;
}

void nvm_clear_physical_attempt_flags_76794(void)

{
  nvm_physical_attempt_flags = '\0';
  return;
}

void nvm_snapshot_request_handle_mode_and_option_7679e(void)

{
  char cVar1;
  undefined1 uVar2;
  uint32_t puVar3;
  uint uVar4;
  int iVar5;
  
  puVar3 = 0x23dfcu;
  uVar4 = nvm_get_storage_handle_77c9e();
  iVar5 = nvm_get_request_mode_77c64();
  cVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)((uVar4 & 0xffff) * 6 + 0x383c)))));
  DAT_febf6b70 = nvm_get_request_handle_snapshot_77c78();
  uVar2 = 0;
  if ((iVar5 == 2) || (uVar2 = 1, iVar5 == 1)) {
    DAT_febf6b74 = uVar2;
  }
  if ((cVar1 == '\0') || (cVar1 == '\x01')) {
    DAT_febf6b75 = cVar1;
  }
  return;
}

void nvm_guarded_reset_dispatch_mode1_767ea(void)

{
  int iVar1;
  
  nvm_enter_paired_call_guard_79aaa();
  iVar1 = nvm_get_direct_mode_or_suspend_marker_79c76();
  if (iVar1 == 0) {
    nvm_poll_driver_and_optional_timers_74e46(1);
    nvm_step_state_machine_mode_one_7840c();
  }
  nvm_leave_paired_call_guard_79abe();
  return;
}

undefined4 nvm_guarded_submit_write_service11_7682e(undefined4 param_1,undefined2 param_2,undefined4 param_3)

{
  int iVar1;
  undefined4 uVar2;
  
  nvm_enter_paired_call_guard_79aaa();
  iVar1 = nvm_suspend_state_is_nonzero_79b0e();
  if (iVar1 == 0) {
    iVar1 = nvm_stage_and_submit_program_with_optional_deferral_74c54(param_1, param_2, ((uchar *)camry_host_ptr((uint32_t)(param_3))), 0xb, 0);
    uVar2 = 8;
    if (iVar1 == 2) {
      uVar2 = 7;
      nvm_set_secondary_result_state('\x01');
    }
  }
  else {
    uVar2 = 9;
  }
  nvm_leave_paired_call_guard_79abe();
  return uVar2;
}

uint nvm_guarded_erase_admission(uint byte_offset,uint page_count)

{
  int iVar1;
  uint uVar2;
  uint uVar3;
  
  nvm_enter_paired_call_guard_79aaa();
  iVar1 = nvm_suspend_state_is_nonzero_79b0e();
  if (iVar1 == 0) {
    uVar2 = nvm_start_reverse_erase(byte_offset,page_count & 0xffff,0xb);
    uVar3 = 8;
    if (uVar2 == 2) {
      uVar3 = 7;
      nvm_set_secondary_result_state('\x01');
    }
  }
  else {
    uVar3 = 9;
  }
  nvm_leave_paired_call_guard_79abe();
  return uVar3;
}

void nvm_guarded_direct_poll(void)

{
  int iVar1;
  
  nvm_enter_paired_call_guard_79aaa();
  iVar1 = nvm_suspend_state_is_nonzero_79b0e();
  if (iVar1 == 0) {
    nvm_initialize_dataflash_read_controls_wrapper_79388();
    nvm_abort_flash_unless_phase_fourteen_781be();
    nvm_poll_driver_and_optional_timers_74e46(1);
  }
  nvm_set_service_state_byte_cdb_79c56(iVar1 != 0);
  nvm_leave_paired_call_guard_79abe();
  return;
}

undefined4 nvm_guarded_read_map_service_status_768e8(uint param_1,ushort param_2,uchar *param_3)

{
  int iVar1;
  uint uVar2;
  undefined4 uVar3;
  
  nvm_enter_paired_call_guard_79aaa();
  iVar1 = nvm_suspend_state_is_nonzero_79b0e();
  if (iVar1 == 0) {
    uVar2 = nvm_read_with_optional_blank_check(param_1,param_2,param_3,'\0');
    if (uVar2 == 1) {
      uVar3 = 0;
    }
    else if (uVar2 == 0xffff0000) {
      uVar3 = 6;
    }
    else {
      uVar3 = 4;
    }
  }
  else {
    uVar3 = 9;
  }
  nvm_leave_paired_call_guard_79abe();
  return uVar3;
}

uint nvm_probe_storage_range(uint byte_offset,ushort byte_count)

{
  int iVar1;
  uint uVar2;
  uchar auStack_4c [64];
  
  nvm_enter_paired_call_guard_79aaa();
  iVar1 = nvm_suspend_state_is_nonzero_79b0e();
  if (iVar1 == 0) {
    uVar2 = nvm_read_with_optional_blank_check(byte_offset,byte_count,auStack_4c,'\x01');
    if (uVar2 == 1) {
      uVar2 = 3;
    }
    else if (uVar2 == 3) {
      uVar2 = 2;
    }
    else if (uVar2 == 0xffff0000) {
      uVar2 = 6;
    }
    else {
      uVar2 = 4;
    }
  }
  else {
    uVar2 = 9;
  }
  nvm_leave_paired_call_guard_79abe();
  return uVar2;
}

void nvm_mark_attempt_header_mismatch_76988(void)

{
  nvm_physical_attempt_flags = nvm_physical_attempt_flags | 2;
  return;
}

void nvm_mark_attempt_compare_mismatch_76992(void)

{
  nvm_physical_attempt_flags = nvm_physical_attempt_flags | 4;
  return;
}

void nvm_mark_attempt_bit3_7699c(void)

{
  nvm_physical_attempt_flags = nvm_physical_attempt_flags | 8;
  return;
}

uchar nvm_get_attempt_snapshot_and_flags_769a6(undefined2 *param_1,undefined1 *param_2,undefined1 *param_3)

{
  *param_1 = DAT_febf6b70;
  *param_2 = DAT_febf6b74;
  *param_3 = DAT_febf6b75;
  return nvm_physical_attempt_flags;
}

void nvm_publish_erase_driver_result(uint driver_result)

{
  uchar state;
  
  if (driver_result == 1) {
    state = '\0';
  }
  else if (driver_result == 0xffff0000) {
    state = '\x06';
  }
  else {
    state = '\x04';
  }
  nvm_set_secondary_result_state(state);
  return;
}

bool thunk_return_false_via_zero_hook_79432(void)

{
  return return_false_via_zero_hook_79432();
}

undefined4 thunk_nvm_is_current_service_twelve_79444(void)

{
  return nvm_is_current_service_twelve_79444();
}

void nvm_enable_guard_mask_for_index0_or1_76a8c(char param_1)

{
  if ((param_1 == '\0') || (param_1 == '\x01')) {
    nvm_set_diagnostic_group_bits_796be((uint)(byte)param_1);
  }
  return;
}

void nvm_disable_guard_mask_for_index0_76aa2(char param_1)

{
  if (param_1 == '\0') {
    nvm_clear_diagnostic_group_bits_796f4((uint)(byte)param_1);
  }
  return;
}

void thunk_nvm_reset_secondary_result_and_attempt_flags_76782(void)

{
  nvm_reset_secondary_result_and_attempt_flags_76782();
  return;
}

void nvm_set_secondary_result_state5_76ae6(void)

{
  nvm_set_secondary_result_state('\x05');
  return;
}

void nvm_begin_attempt_snapshot_76af4(void)

{
  nvm_clear_physical_attempt_flags_76794();
  nvm_snapshot_request_handle_mode_and_option_7679e();
  return;
}

undefined * nvm_compare_record_header_handle_bytes_76b1c(void)

{
  undefined4 uVar1;
  int iVar2;
  undefined *puVar3;
  uchar auStack_c [4];
  
  puVar3 = ((undefined *)camry_host_ptr(0xfffbu));
  if ((DAT_febf6c44 < nvm_descriptor_count) &&
     (puVar3 = ((undefined *)camry_host_ptr((uint32_t)(nvm_read_with_optional_blank_check(DAT_febf6c24,4,auStack_c,'\0')))),camry_host_addr(puVar3)==((uint32_t)((uint32_t)(0x1))))) {
    uVar1 = thunk_return_argument_word_7490e((0xfebf6b80u));
    iVar2 = compare_unsigned_byte_ranges_7484a(uVar1, camry_host_addr(auStack_c), 2);
    if (iVar2 != 0) {
      puVar3 = ((undefined *)camry_host_ptr(0xfffdu));
    }
  }
  return puVar3;
}

undefined * nvm_compare_copied_payload_chunk_76b6e(void)

{
  ushort handle;
  uint32_t puVar1;
  undefined4 uVar2;
  uint uVar3;
  uint uVar4;
  int iVar5;
  undefined *puVar6;
  uchar auStack_54 [64];
  
  handle = DAT_febf6c44;
  iVar5 = DAT_febf6c24;
  puVar1 = 0x23dfcu;
  puVar6 = ((undefined *)camry_host_ptr(0xfffbu));
  uVar2 = nvm_record_context_get_payload_source_772b4((0xfebf6b80u));
  if (handle < (*((ushort *)camry_host_ptr((uint32_t)(puVar1 + 0x3b2c))))) {
    uVar3 = nvm_payload_page_count(handle);
    uVar3 = (uVar3 - nvm_payload_chunks_remaining) * 0x40;
    uVar4 = nvm_payload_chunk_length(handle,(ushort)uVar3);
    puVar6 = ((undefined *)camry_host_ptr((uint32_t)(nvm_read_with_optional_blank_check
                       (iVar5 + (uVar3 & 0xffff) + 4,(ushort)uVar4,auStack_54,'\0'))));
    if ((camry_host_addr(puVar6)==((uint32_t)((uint32_t)(0x1)))) && (iVar5 = compare_unsigned_byte_ranges_7484a(uVar2, camry_host_addr(auStack_54), uVar4), iVar5 != 0))
    {
      puVar6 = ((undefined *)camry_host_ptr(0xfffdu));
    }
  }
  return puVar6;
}

uint nvm_write_all_ones_payload_chunk_76be8(ushort param_1)

{
  int iVar1;
  uint uVar2;
  uint uVar3;
  undefined1 auStack_4c [64];
  
  iVar1 = DAT_febf6c24;
  uVar2 = nvm_payload_page_count(param_1);
  uVar2 = (uVar2 - nvm_payload_chunks_remaining) * 0x40;
  uVar3 = nvm_payload_chunk_length(param_1,(ushort)uVar2);
  fill_byte_range_74872(camry_host_addr(auStack_4c), 0xff, uVar3);
  return nvm_stage_and_submit_program_with_optional_deferral_74c54(iVar1 + (uVar2 & 0xffff) + 4,uVar3,auStack_4c,5,0);
}

void nvm_after_blank_header_start_payload_fill_76c3e(int param_1)

{
  if ((param_1 == 1) && (param_1 = camry_host_addr(nvm_compare_record_header_handle_bytes_76b1c()), param_1 == 1)) {
    param_1 = nvm_write_all_ones_payload_chunk_76be8(DAT_febf6c44);
  }
  if (param_1 != 2) {
    nvm_dispatch_selected_descriptor_callback_slot_seven_7849e(param_1);
    thunk_nvm_reset_active_record_and_checksum_772f8();
  }
  return;
}

uint nvm_write_all_ones_checksum_trailer_76c6e(ushort param_1)

{
  ushort uVar1;
  int iVar2;
  uint32_t puVar3;
  undefined4 uVar4;
  
  iVar2 = DAT_febf6c24;
  puVar3 = 0x23dfcu;
  uVar4 = nvm_record_context_checksum_trailer_address_772ea((0xfebf6b80u));
  uVar1 = (*((ushort *)camry_host_ptr((uint32_t)(puVar3 + (uint)param_1 * 6 + 0x383a))));
  nvm_record_context_set_checksum_trailer_772e4((0xfebf6b80u),(int)0xffffffff);
  return nvm_stage_and_submit_program_with_optional_deferral_74c54(iVar2 + uVar1 + 4, 4, ((uchar *)camry_host_ptr((uint32_t)(uVar4))), 7, 0);
}

void nvm_continue_all_ones_payload_write_76cb2(int param_1)

{
  if (param_1 == 1) {
    nvm_payload_chunks_remaining = nvm_payload_chunks_remaining - 1;
    if (nvm_payload_chunks_remaining == 0) {
      if (0x20 < (*((volatile uint16_t *)camry_host_ptr((uint32_t)((uint32_t)(0x27634u + (uint32_t)(DAT_febf6c44) * (uint32_t)sizeof(F33NvmDescriptor)) + (uint32_t)(0) * (uint32_t)sizeof(F33NvmDescriptor) + (uint32_t)offsetof(F33NvmDescriptor, payload_bytes)))))) {
        param_1 = nvm_write_all_ones_checksum_trailer_76c6e(DAT_febf6c44);
      }
    }
    else {
      param_1 = nvm_write_all_ones_payload_chunk_76be8((*((volatile uint16_t *)camry_host_ptr(0xfebf6c44u))));
    }
  }
  if (param_1 != 2) {
    nvm_dispatch_selected_descriptor_callback_slot_seven_7849e(param_1);
    thunk_nvm_reset_active_record_and_checksum_772f8();
  }
  return;
}

void nvm_dispatch_write_completion_and_reset_record_76d02(uint param_1)

{
  nvm_dispatch_selected_descriptor_callback_slot_seven_7849e(param_1);
  thunk_nvm_reset_active_record_and_checksum_772f8();
  return;
}

int nvm_copy_record_payload_chunk_to_active_slot_76d12(ushort param_1)

{
  int iVar1;
  uint uVar2;
  uint uVar3;
  int iVar4;
  undefined4 uVar5;
  uint uVar6;
  
  iVar1 = DAT_febf6c24;
  uVar2 = nvm_record_offset(param_1,DAT_febf6c42,0);
  uVar3 = nvm_payload_page_count(param_1);
  uVar3 = (uVar3 - nvm_payload_chunks_remaining) * 0x40;
  uVar6 = uVar3 & 0xffff;
  uVar3 = nvm_payload_chunk_length(param_1,(ushort)uVar3);
  iVar4 = nvm_read_map_blank_and_failure_status_776fa(uVar6 + 4 + uVar2,uVar3,((undefined *)camry_host_ptr(0xfebf6b90u)),0);
  if (iVar4 == 1) {
    uVar2 = nvm_sum_bytes((ushort)uVar3,((undefined *)camry_host_ptr(0xfebf6b90u)));
    nvm_checksum_accumulator = nvm_checksum_accumulator + uVar2;
    nvm_record_context_set_payload_source_772ba((0xfebf6b80u), (int)((uint32_t)(0xfebf6b90u)));
    uVar5 = nvm_record_context_get_payload_source_772b4((0xfebf6b80u));
    return nvm_stage_and_submit_program_with_optional_deferral_74c54(iVar1 + uVar6 + 4, uVar3, ((uchar *)camry_host_ptr((uint32_t)(uVar5))), 8, 0);
  }
  return iVar4;
}

void nvm_verify_copied_chunk_and_continue_76dac(int param_1)

{
  uint32_t puVar1;
  puVar1 = 0x23dfcu;
  if ((param_1 == 1) && (param_1 = camry_host_addr(nvm_compare_copied_payload_chunk_76b6e()), param_1 == 1)) {
    nvm_payload_chunks_remaining = nvm_payload_chunks_remaining - 1;
    if (nvm_payload_chunks_remaining == 0) {
      if (0x20 < (*((ushort *)camry_host_ptr((uint32_t)(puVar1 + (uint)DAT_febf6c44 * 6 + 0x383a))))) {
        param_1 = nvm_write_accumulated_checksum_trailer_7749e(DAT_febf6c44);
      }
    }
    else {
      param_1 = nvm_copy_record_payload_chunk_to_active_slot_76d12((*((volatile uint16_t *)camry_host_ptr(0xfebf6c44u))));
    }
  }
  if (param_1 != 2) {
    nvm_dispatch_selected_descriptor_callback_slot_seven_7849e(param_1);
    nvm_reset_active_record_and_checksum_772f8();
  }
  return;
}

void nvm_verify_header_then_copy_payload_76e06(int param_1)

{
  if ((param_1 == 1) && (param_1 = camry_host_addr(nvm_compare_full_record_header_77548()), param_1 == 1)) {
    param_1 = nvm_copy_record_payload_chunk_to_active_slot_76d12(DAT_febf6c44);
  }
  if (param_1 != 2) {
    nvm_dispatch_selected_descriptor_callback_slot_seven_7849e(param_1);
    nvm_reset_active_record_and_checksum_772f8();
  }
  return;
}

uint nvm_erase_record_slot_allocation_76e36(ushort param_1,ushort param_2)

{
  if (nvm_descriptor_count <= param_1) {
    return 0xfffb;
  }
  return nvm_start_reverse_erase_with_flag1_77650(nvm_record_offset(param_1,param_2,0),nvm_allocation_pages(param_1));
}

uint nvm_begin_record_slot_write_76e6a(ushort param_1,ushort param_2,int param_3)

{
  uint uVar1;
  
  if ((param_1 < nvm_descriptor_count) && (param_3 != 0)) {
    DAT_febf6c44 = param_1;
    nvm_record_context_set_payload_source_772ba((0xfebf6b80u),param_3);
    uVar1 = nvm_payload_page_count(param_1);
    nvm_payload_chunks_remaining = (ushort)uVar1;
    DAT_febf6c24 = nvm_record_offset(param_1,param_2,0);
    return nvm_write_record_header_from_payload_source_77660(param_1);
  }
  return 0xfffb;
}

uint nvm_write_all_ones_record_header_76ec4(void)

{
  undefined4 uVar1;
  
  uVar1 = thunk_return_argument_word_7490e((0xfebf6b80u));
  nvm_record_context_set_handle_772a2(((undefined2 *)camry_host_ptr((uint32_t)((0xfebf6b80u)))), 0xffff);
  nvm_record_context_set_header_checksum_772ae((0xfebf6b80u),0xffff);
  return nvm_stage_and_submit_program_with_optional_deferral_74c54(DAT_febf6c24, 4, ((uchar *)camry_host_ptr((uint32_t)(uVar1))), 6, 0);
}

uint nvm_begin_record_slot_blank_fill_76f04(ushort param_1,ushort param_2)

{
  uint uVar1;
  
  if (param_1 < nvm_descriptor_count) {
    DAT_febf6c44 = param_1;
    uVar1 = nvm_payload_page_count(param_1);
    nvm_payload_chunks_remaining = (ushort)uVar1;
    DAT_febf6c24 = nvm_record_offset(param_1,param_2,0);
    return nvm_write_all_ones_record_header_76ec4();
  }
  return 0xfffb;
}

void nvm_begin_record_slot_payload_read_76f4e(ushort param_1,ushort param_2,uchar *param_3,uchar param_4)

{
  uint32_t puVar1;
  uint uVar2;
  uint uVar3;
  
  puVar1 = 0x23dfcu;
  uVar3 = (uint)param_1;
  if ((uVar3 < nvm_descriptor_count) && (camry_host_addr((param_3))!= 0)) {
    nvm_record_context.destination_buffer = camry_host_addr(param_3);
    DAT_febf6c44 = param_1;
    uVar2 = nvm_payload_page_count(param_1);
    nvm_payload_chunks_remaining = (ushort)uVar2;
    DAT_febf6c24 = nvm_record_offset(param_1,param_2,0);
    uVar2 = nvm_read_header_validate_handle_and_accumulate_7786a(uVar3,DAT_febf6c24,0);
    if ((uVar2 == 1) &&
       (uVar2 = nvm_read_payload_chunk(param_1,DAT_febf6c24,param_4), uVar2 == 1)) {
      if (nvm_payload_chunks_remaining != 0) {
        return;
      }
      if (0x20 < (*((ushort *)camry_host_ptr((uint32_t)(puVar1 + uVar3 * 6 + 0x383a))))) {
        uVar2 = nvm_read_payload_checksum(param_1,DAT_febf6c24,param_4);
      }
    }
    nvm_dispatch_read_completion_and_reset_record_77640(uVar2);
  }
  return;
}

int nvm_read_chunk_accumulate_and_check_inline_checksum_76ff0(ushort param_1,int param_2,undefined1 param_3)

{
  ushort uVar1;
  uint uVar2;
  uint uVar3;
  int iVar4;
  uchar auStack_5c [64];
  
  uVar1 = (*((volatile uint16_t *)camry_host_ptr((uint32_t)((uint32_t)(0x27634u + (uint32_t)(param_1) * (uint32_t)sizeof(F33NvmDescriptor)) + (uint32_t)(0) * (uint32_t)sizeof(F33NvmDescriptor) + (uint32_t)offsetof(F33NvmDescriptor, payload_bytes)))));
  uVar2 = nvm_payload_page_count(param_1);
  uVar2 = (uVar2 - nvm_payload_chunks_remaining) * 0x40;
  uVar3 = nvm_payload_chunk_length(param_1,(ushort)uVar2);
  iVar4 = nvm_read_map_blank_and_failure_status_776fa(param_2 + (uVar2 & 0xffff) + 4,uVar3,auStack_5c,param_3);
  if (iVar4 == 1) {
    if (uVar1 < 0x21) {
      uVar2 = nvm_sum_bytes((ushort)uVar3,auStack_5c);
      nvm_checksum_accumulator = nvm_checksum_accumulator + uVar2 + 0xc000;
      uVar2 = nvm_header_checksum(((F33NvmRecordContext *)camry_host_ptr((uint32_t)((0xfebf6b80u)))));
      if (uVar2 != (nvm_checksum_accumulator & 0xffff)) {
        iVar4 = 0xfffc;
      }
    }
    else {
      uVar2 = nvm_sum_bytes((ushort)uVar3,auStack_5c);
      nvm_checksum_accumulator = nvm_checksum_accumulator + uVar2;
    }
    nvm_payload_chunks_remaining = nvm_payload_chunks_remaining - 1;
  }
  return iVar4;
}
