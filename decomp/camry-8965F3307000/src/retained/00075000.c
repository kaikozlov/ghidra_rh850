#include "common.h"

void nvm_store_result_and_set_completion_tag_one_75008(undefined4 param_1)

{
  nvm_set_state_machine_result_word_783ca(param_1);
  nvm_set_state_machine_event_783c0(1);
  return;
}

void nvm_store_result_and_set_completion_tag_two_7501a(undefined4 param_1)

{
  nvm_set_state_machine_result_word_783ca(param_1);
  nvm_set_state_machine_event_783c0(2);
  return;
}

void nvm_store_result_and_mark_payload_callback_done_7502c(undefined4 param_1)

{
  nvm_set_state_machine_result_word_783ca(param_1);
  DAT_febf6c55 = 1;
  return;
}

void run_init_chain_75042(undefined4 param_1)

{
  nvm_snapshot_completion_mode_handle_and_reset_request_77ce8();
  nvm_set_completion_raw_result_77d14(param_1);
  nvm_finish_physical_result();
  fill_constant_block_74fa2();
  return;
}

undefined4 nvm_select_state_ten_or_six_by_operation_kind_7505e(char param_1)

{
  undefined4 uVar1;
  
  if (param_1 == '\x01') {
    uVar1 = 10;
    DAT_febf6c52 = 0;
    nvm_set_nonzero_completion_side_status_77d1e((uint)(byte)param_1);
  }
  else {
    uVar1 = 6;
  }
  return uVar1;
}

undefined4 nvm_retry_state_three_or_publish_result_75080(undefined *param_1,undefined4 *param_2)

{
  undefined4 uVar1;
  
  if (DAT_febf6c52 < DAT_0002792b) {
    DAT_febf6c52 = DAT_febf6c52 + 1;
    uVar1 = 3;
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

undefined4 nvm_finish_result_by_physical_operation_kind_750b2(undefined *param_1,undefined4 *param_2)

{
  int iVar1;
  
  iVar1 = nvm_get_request_mode_77c64();
  if (iVar1 == 1) {
    *param_2 = camry_host_addr(param_1);
    if (camry_host_addr(param_1)==((uint32_t)(0xfffdu))) {
      nvm_mark_attempt_compare_mismatch_76992();
    }
  }
  else if (iVar1 == 2) {
    nvm_mark_attempt_bit3_7699c();
    nvm_mark_physical_attempt_error();
    if (camry_host_addr(param_1)==((uint32_t)(0xfffdu))) {
      nvm_mark_attempt_compare_mismatch_76992();
    }
    run_init_chain_75042(1);
  }
  else {
    *param_2 = ((uint32_t)(0xfffbu));
  }
  return 0;
}

undefined4 nvm_retry_state_fifteen_or_finish_result_750fe(undefined4 param_1, undefined4 param_2)

{
  undefined4 uVar1;
  
  if (DAT_febf6c52 < DAT_0002792b) {
    DAT_febf6c52 = DAT_febf6c52 + 1;
    uVar1 = 0xf;
  }
  else {
    uVar1 = nvm_finish_result_by_physical_operation_kind_750b2(((undefined *)camry_host_ptr((uint32_t)(param_1))), ((undefined4 *)camry_host_ptr((uint32_t)(param_2))));
  }
  return uVar1;
}

undefined4 nvm_select_state_from_marker_codes_twelve_fourteen_75122(char param_1,ushort param_2,undefined4 *param_3)

{
  int iVar1;
  undefined4 uVar2;
  
  iVar1 = nvm_get_request_mode_77c64();
  if (param_1 == '\f') {
    DAT_febf6c3e = param_2 & 0xff;
    uVar2 = nvm_select_state_ten_or_six_by_operation_kind_7505e(iVar1);
  }
  else if (param_1 == '\x0e') {
    if (iVar1 == 1) {
      uVar2 = 0x13;
    }
    else {
      uVar2 = 0;
      if (iVar1 == 2) {
        *param_3 = 0xfffc;
        nvm_mark_attempt_bit3_7699c();
      }
      else {
        *param_3 = ((uint32_t)(0xfffbu));
      }
    }
    nvm_set_nonzero_completion_side_status_77d1e(2);
  }
  else {
    uVar2 = 0;
    *param_3 = ((uint32_t)(0xfffbu));
  }
  return uVar2;
}

undefined4 nvm_select_initial_state_from_record_markers_7518a(undefined2 param_1,char param_2,int *param_3)

{
  uint8_t stack_record_12[18];
  int iVar1;
  undefined4 uVar2;
  
  iVar1 = nvm_get_request_mode_77c64();
  stack_record_12[0] = 0xff;
  stack_record_12[1] = 0xff;
  if (param_2 == '\r') {
    uVar2 = 1;
  }
  else if (param_2 == '\x0f') {
    if (iVar1 == 1) {
      uVar2 = 0x14;
    }
    else {
      uVar2 = 0;
      if (iVar1 == 2) {
        *param_3 = 0xfffc;
        nvm_mark_attempt_bit3_7699c();
      }
      else {
        *param_3 = (int)0xfffbu;
      }
    }
    nvm_set_nonzero_completion_side_status_77d1e(2);
  }
  else {
    if (param_2 == -1) {
      iVar1 = nvm_match_three_markers_to_final_table_entries_77f7e(param_1,((uint8_t *)(stack_record_12)),((uint8_t *)((stack_record_12 + 1))));
      if (iVar1 == 1) {
        uVar2 = nvm_select_state_from_marker_codes_twelve_fourteen_75122(stack_record_12[0],stack_record_12[1],param_3);
        return uVar2;
      }
      *param_3 = iVar1;
    }
    else {
      *param_3 = (int)0xfffbu;
    }
    uVar2 = 0;
  }
  return uVar2;
}

undefined4 nvm_classify_current_record_for_initial_state_7521c(undefined4 param_1,int *param_2)

{
  uint32_t puVar1;
  int iVar2;
  uint uVar3;
  undefined4 uVar4;
  undefined1 uStack_d;
  
  puVar1 = 0x23dfcu;
  uVar4 = 0xff;
  iVar2 = nvm_get_request_mode_77c64();
  uStack_d = 0xff;
  if (iVar2 != 0) {
    uVar3 = nvm_get_storage_handle_77c9e();
    if (uVar3 < (*((ushort *)camry_host_ptr((uint32_t)(puVar1 + 0x3b2c))))) {
      DAT_febf6c50 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)((uVar3 & 0xffff) * 6 + 0x383c)))));
      iVar2 = nvm_classify_two_record_presence_markers_78010(uVar3,&uStack_d);
      if (iVar2 == 1) {
        uVar4 = nvm_select_initial_state_from_record_markers_7518a(uVar3,uStack_d,param_2);
        return uVar4;
      }
      *param_2 = iVar2;
    }
    else {
      *param_2 = (int)0xfffbu;
    }
    uVar4 = 0;
  }
  return uVar4;
}

undefined4 nvm_select_next_state_from_marker_codes_ten_eleven_thirteen_75282(char param_1,undefined4 *param_2)

{
  int iVar1;
  undefined4 uVar2;
  
  iVar1 = nvm_get_request_mode_77c64();
  if (param_1 == '\n') {
    if (iVar1 == 1) {
      uVar2 = 2;
      DAT_febf6c52 = 0;
    }
    else if (iVar1 == 2) {
      uVar2 = 6;
    }
    else {
      uVar2 = 0;
    }
  }
  else if (param_1 == '\v') {
    uVar2 = nvm_select_state_ten_or_six_by_operation_kind_7505e(iVar1);
  }
  else if (param_1 == '\r') {
    if (iVar1 == 1) {
      uVar2 = 0x12;
    }
    else {
      uVar2 = 0;
      if (iVar1 == 2) {
        *param_2 = 0xfffc;
        nvm_mark_attempt_bit3_7699c();
      }
      else {
        *param_2 = ((uint32_t)(0xfffbu));
      }
    }
    nvm_set_nonzero_completion_side_status_77d1e(2);
  }
  else {
    uVar2 = 0;
    *param_2 = ((uint32_t)(0xfffbu));
  }
  return uVar2;
}

undefined4 nvm_scan_three_markers_and_select_record_state_752fa(undefined4 param_1,int *param_2)

{
  uint8_t stack_record_e[14];
  uint32_t puVar1;
  int iVar2;
  uint uVar3;
  undefined4 uVar4;
  
  puVar1 = 0x23dfcu;
  uVar4 = 0xff;
  iVar2 = nvm_get_request_mode_77c64();
  stack_record_e[1] = 0xff;
  stack_record_e[0] = 0xd;
  if (iVar2 != 0) {
    uVar3 = nvm_get_storage_handle_77c9e();
    if (uVar3 < (*((ushort *)camry_host_ptr((uint32_t)(puVar1 + 0x3b2c))))) {
      if (DAT_febf6c50 == '\x01') {
        DAT_febf6c53 = 2;
      }
      iVar2 = camry_host_addr(nvm_read_three_record_markers_and_decode_77eba(uVar3,((uint8_t *)(stack_record_e)),((uint8_t *)((stack_record_e + 1)))));
      if (iVar2 == 1) {
        DAT_febf6c3e = (ushort)stack_record_e[1];
        uVar4 = nvm_select_next_state_from_marker_codes_ten_eleven_thirteen_75282(stack_record_e[0],param_2);
        return uVar4;
      }
      *param_2 = iVar2;
    }
    else {
      *param_2 = (int)0xfffbu;
    }
    uVar4 = 0;
  }
  return uVar4;
}

undefined4 nvm_submit_mode_two_record_marker_when_gate_clear_75376(int param_1,int *param_2)

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
  if ((iVar3 != 0) && (iVar3 = nvm_submit_four_byte_record_marker_write_7808c(uVar2,DAT_febf6c3e,2), iVar3 != 2)) {
    *param_2 = iVar3;
    uVar6 = 0;
  }
  return uVar6;
}

undefined4 nvm_arm_and_submit_mode_two_record_marker_753cc(undefined4 param_1, undefined4 param_2)

{
  nvm_arm_record_marker_submission_74f72();
  return nvm_submit_mode_two_record_marker_when_gate_clear_75376(param_1, ((int *)camry_host_ptr((uint32_t)(param_2))));
}

undefined4 thunk_nvm_submit_mode_two_record_marker_when_gate_clear_75376(undefined4 param_1, undefined4 param_2)

{
  return nvm_submit_mode_two_record_marker_when_gate_clear_75376(param_1, ((int *)camry_host_ptr((uint32_t)(param_2))));
}

undefined4 nvm_poll_mode_two_marker_or_retry_state_three_753e8(undefined4 param_1,int *param_2)

{
  undefined4 camry_r10_0;

  uint32_t puVar1;
  uint32_t puVar2;
  int iVar3;
  undefined4 uVar4;
  
  puVar1 = 0x23dfcu;
  puVar2 = (camry_r10_0 = nvm_get_state_machine_result_word_783d4());
  iVar3 = (nvm_clear_record_marker_submission_latch_74f7e(), (int)(uintptr_t)camry_r10_0);
  if (iVar3 == 1) {
    uVar4 = 3;
  }
  else if (DAT_febf6c52 < (byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x3b2f)))))) {
    DAT_febf6c52 = DAT_febf6c52 + 1;
    nvm_arm_record_marker_submission_74f72();
    uVar4 = nvm_submit_mode_two_record_marker_when_gate_clear_75376(param_1,param_2);
  }
  else {
    *param_2 = iVar3;
    uVar4 = 0;
    if (puVar2 == 0xfffdu) {
      nvm_mark_attempt_compare_mismatch_76992();
    }
  }
  return uVar4;
}

uint nvm_compute_next_record_slot_low_two_bits_7543c(uint param_1)

{
  return 1 << (param_1 & 0x1f) & 3;
}

undefined4 nvm_start_erase_next_record_slot_7544a(undefined4 param_1,int *param_2)

{
  undefined4 uVar1;
  undefined4 uVar2;
  int iVar3;
  undefined4 uVar4;
  
  uVar4 = 0xff;
  uVar1 = nvm_get_storage_handle_77c9e();
  uVar2 = nvm_compute_next_record_slot_low_two_bits_7543c(DAT_febf6c3e);
  iVar3 = nvm_erase_record_slot_allocation_76e36(uVar1,uVar2);
  if (iVar3 != 2) {
    *param_2 = iVar3;
    uVar4 = 0;
  }
  return uVar4;
}

undefined4 nvm_poll_erase_or_retry_state_four_7547e(undefined4 param_1,int *param_2)

{
  uint32_t puVar1;
  int iVar2;
  undefined4 uVar3;
  undefined4 uVar4;
  
  puVar1 = 0x23dfcu;
  iVar2 = nvm_get_state_machine_result_word_783d4();
  uVar3 = nvm_get_storage_handle_77c9e();
  if (iVar2 == 1) {
    uVar3 = 4;
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

undefined4 nvm_start_payload_write_next_record_slot_754d6(undefined4 param_1,int *param_2)

{
  undefined4 uVar1;
  undefined4 uVar2;
  int iVar3;
  undefined4 uVar4;
  undefined4 uVar5;
  
  uVar4 = 0xff;
  uVar1 = nvm_get_storage_handle_77c9e();
  uVar5 = nvm_get_write_source_77cbe();
  uVar2 = nvm_compute_next_record_slot_low_two_bits_7543c(DAT_febf6c3e);
  iVar3 = nvm_begin_record_slot_write_76e6a(uVar1,uVar2,uVar5);
  if (iVar3 != 2) {
    *param_2 = iVar3;
    uVar4 = 0;
  }
  return uVar4;
}

undefined4 nvm_poll_payload_write_or_retry_state_five_75510(undefined4 param_1,undefined4 param_2)

{
  int iVar1;
  undefined4 uVar2;
  
  iVar1 = nvm_get_state_machine_result_word_783d4();
  if (iVar1 == 1) {
    uVar2 = 5;
  }
  else {
    uVar2 = nvm_retry_state_three_or_publish_result_75080(((undefined *)camry_host_ptr((uint32_t)(iVar1))), ((undefined4 *)camry_host_ptr((uint32_t)(param_2))));
  }
  return uVar2;
}

undefined4 nvm_submit_mode_one_record_marker_when_gate_clear_7552e(int param_1,int *param_2)

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

undefined4 nvm_arm_and_submit_mode_one_record_marker_75584(undefined4 param_1, undefined4 param_2)

{
  nvm_arm_record_marker_submission_74f72();
  return nvm_submit_mode_one_record_marker_when_gate_clear_7552e(param_1, ((int *)camry_host_ptr((uint32_t)(param_2))));
}

undefined4 thunk_nvm_submit_mode_one_record_marker_when_gate_clear_7552e(undefined4 param_1, undefined4 param_2)

{
  return nvm_submit_mode_one_record_marker_when_gate_clear_7552e(param_1, ((int *)camry_host_ptr((uint32_t)(param_2))));
}

undefined4 nvm_finish_mode_one_marker_or_rotate_and_retry_755a0(undefined4 param_1,undefined4 *param_2)

{
  undefined4 camry_r10_0;

  uint32_t puVar1;
  uint32_t puVar2;
  undefined4 uVar3;
  
  puVar1 = 0x23dfcu;
  (camry_r10_0 = nvm_get_state_machine_result_word_783d4());
  puVar2 = (nvm_clear_record_marker_submission_latch_74f7e(), camry_r10_0);
  if (puVar2 == 0x1) {
    if (DAT_febf6c50 == '\x01') {
      DAT_febf6c53 = DAT_febf6c53 + -1;
      if (DAT_febf6c53 != '\0') {
        DAT_febf6c3e = nvm_compute_next_record_slot_low_two_bits_7543c(DAT_febf6c3e);
        DAT_febf6c52 = 0;
        return 2;
      }
    }
    else if (DAT_febf6c50 != '\0') {
      *param_2 = ((uint32_t)(0xfffbu));
      return 0;
    }
    uVar3 = 0;
    run_init_chain_75042(1);
  }
  else if (DAT_febf6c52 < (byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x3b2f)))))) {
    DAT_febf6c52 = DAT_febf6c52 + 1;
    nvm_arm_record_marker_submission_74f72();
    uVar3 = nvm_submit_mode_one_record_marker_when_gate_clear_7552e(param_1,param_2);
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

undefined4 nvm_finish_payload_read_or_select_retry_state_75642(void)

{
  int iVar1;
  undefined4 uVar2;
  
  if (DAT_febf6c55 == '\x01') {
    iVar1 = nvm_get_state_machine_result_word_783d4();
    if (iVar1 == 1) {
      run_init_chain_75042(1);
      uVar2 = 0;
    }
    else {
      uVar2 = 8;
      nvm_mark_physical_attempt_error();
      nvm_mark_attempt_bit3_7699c();
    }
  }
  else {
    uVar2 = 7;
  }
  return uVar2;
}

uint nvm_compute_second_next_record_slot_low_two_bits_75678(uint param_1)

{
  return 1 << (1 << (param_1 & 0x1f) & 3U) & 3;
}

undefined4 nvm_finish_alternate_payload_read_or_wait_7568e(void)

{
  undefined4 uVar1;
  
  if (DAT_febf6c55 == '\x01') {
    uVar1 = nvm_get_state_machine_result_word_783d4();
    run_init_chain_75042(uVar1);
    uVar1 = 0;
  }
  else {
    uVar1 = 9;
  }
  return uVar1;
}

uint32_t nvm_read_selected_payload_with_alternate_slot_fallback_756b2(void)

{
  uint32_t camry_r10_result;
  undefined4 uVar1;
  undefined4 uVar2;
  int iVar3;
  undefined4 uVar4;
  
  uVar1 = (camry_r10_result = nvm_get_storage_handle_77c9e());
  uVar2 = (camry_r10_result = nvm_get_read_destination_77cde());
  DAT_febf6c55 = 0;
  nvm_begin_record_slot_payload_read_76f4e(uVar1, DAT_febf6c3e, ((uchar *)camry_host_ptr((uint32_t)(uVar2))), 0);
  iVar3 = (camry_r10_result = nvm_finish_payload_read_or_select_retry_state_75642());
  if (iVar3 == 8) {
    uVar4 = (camry_r10_result = nvm_compute_second_next_record_slot_low_two_bits_75678(DAT_febf6c3e));
    DAT_febf6c55 = 0;
    nvm_begin_record_slot_payload_read_76f4e(uVar1, uVar4, ((uchar *)camry_host_ptr((uint32_t)(uVar2))), 0);
    (camry_r10_result = nvm_finish_alternate_payload_read_or_wait_7568e());
  }
  return camry_r10_result;
}

undefined4 nvm_continue_payload_read_and_finish_75708(void)

{
  thunk_nvm_continue_record_payload_read_77824();
  return nvm_finish_payload_read_or_select_retry_state_75642();
}

undefined4 nvm_start_alternate_slot_payload_read_75718(void)

{
  undefined4 uVar1;
  undefined4 uVar2;
  undefined4 uVar3;
  
  uVar1 = nvm_compute_second_next_record_slot_low_two_bits_75678(DAT_febf6c3e);
  uVar2 = nvm_get_storage_handle_77c9e();
  uVar3 = nvm_get_read_destination_77cde();
  DAT_febf6c55 = 0;
  nvm_begin_record_slot_payload_read_76f4e(uVar2, uVar1, ((uchar *)camry_host_ptr((uint32_t)(uVar3))), 0);
  return nvm_finish_alternate_payload_read_or_wait_7568e();
}

undefined4 nvm_continue_alternate_payload_read_and_finish_75750(void)

{
  thunk_nvm_continue_record_payload_read_77824();
  return nvm_finish_alternate_payload_read_or_wait_7568e();
}

undefined4 nvm_save_successful_primary_slot_or_select_read_retry_75760(void)

{
  int iVar1;
  undefined4 uVar2;
  
  if (DAT_febf6c55 == '\x01') {
    iVar1 = nvm_get_state_machine_result_word_783d4();
    if (iVar1 == 1) {
      DAT_febf6c54 = 1;
      uVar2 = 0xf;
      DAT_febf6c40 = DAT_febf6c3e;
    }
    else {
      uVar2 = 0xc;
      nvm_mark_physical_attempt_error();
    }
  }
  else {
    uVar2 = 0xb;
  }
  return uVar2;
}

undefined4 nvm_save_successful_alternate_slot_or_report_read_failure_757a4(char param_1,undefined4 *param_2)

{
  int iVar1;
  undefined4 uVar2;
  
  if (DAT_febf6c55 == '\x01') {
    iVar1 = nvm_get_state_machine_result_word_783d4();
    if (iVar1 == 1) {
      DAT_febf6c54 = 2;
      DAT_febf6c40 = nvm_compute_second_next_record_slot_low_two_bits_75678(DAT_febf6c3e);
      uVar2 = 0xf;
    }
    else if (param_1 == '\x01') {
      uVar2 = 0x1d;
      nvm_mark_physical_attempt_error();
    }
    else {
      uVar2 = 0;
      if (param_1 == '\x02') {
        *param_2 = 0xfffc;
        nvm_mark_attempt_bit3_7699c();
      }
      else {
        *param_2 = ((uint32_t)(0xfffbu));
      }
    }
  }
  else {
    uVar2 = 0xd;
  }
  return uVar2;
}

uint32_t nvm_check_or_read_selected_payload_with_alternate_fallback_75818(undefined4 param_1,undefined4 param_2)

{
  uint32_t camry_r10_result;
  int iVar1;
  undefined4 uVar2;
  undefined4 uVar3;
  int iVar4;
  undefined4 uVar5;
  
  iVar1 = (camry_r10_result = nvm_get_request_mode_77c64());
  uVar2 = (camry_r10_result = nvm_get_storage_handle_77c9e());
  uVar3 = (camry_r10_result = nvm_get_read_destination_77cde());
  DAT_febf6c55 = 0;
  if (iVar1 == 1) {
    nvm_begin_record_slot_checksum_scan_7708c(uVar2,DAT_febf6c3e,0);
  }
  else {
    nvm_begin_record_slot_payload_read_76f4e(uVar2, DAT_febf6c3e, ((uchar *)camry_host_ptr((uint32_t)(uVar3))), 0);
  }
  iVar4 = (camry_r10_result = nvm_save_successful_primary_slot_or_select_read_retry_75760());
  if (iVar4 == 0xc) {
    uVar5 = (camry_r10_result = nvm_compute_second_next_record_slot_low_two_bits_75678(DAT_febf6c3e));
    DAT_febf6c55 = 0;
    if (iVar1 == 1) {
      nvm_begin_record_slot_checksum_scan_7708c(uVar2,uVar5,0);
    }
    else {
      nvm_begin_record_slot_payload_read_76f4e(uVar2, uVar5, ((uchar *)camry_host_ptr((uint32_t)(uVar3))), 0);
    }
    (camry_r10_result = nvm_save_successful_alternate_slot_or_report_read_failure_757a4(iVar1, ((undefined4 *)camry_host_ptr((uint32_t)(param_2)))));
  }
  return camry_r10_result;
}

undefined4 nvm_continue_primary_payload_check_or_read_75892(void)

{
  int iVar1;
  
  iVar1 = nvm_get_request_mode_77c64();
  if (iVar1 == 1) {
    nvm_continue_record_checksum_scan_7712a();
  }
  else {
    thunk_nvm_continue_record_payload_read_77824();
  }
  return nvm_save_successful_primary_slot_or_select_read_retry_75760();
}

undefined4 nvm_start_alternate_payload_check_or_read_758b0(undefined4 param_1,undefined4 param_2)

{
  undefined4 uVar1;
  undefined4 uVar2;
  int iVar3;
  undefined4 uVar4;
  
  uVar1 = nvm_compute_second_next_record_slot_low_two_bits_75678(DAT_febf6c3e);
  uVar2 = nvm_get_storage_handle_77c9e();
  iVar3 = nvm_get_request_mode_77c64();
  uVar4 = nvm_get_read_destination_77cde();
  DAT_febf6c55 = 0;
  if (iVar3 == 1) {
    nvm_begin_record_slot_checksum_scan_7708c(uVar2,uVar1,0);
  }
  else {
    nvm_begin_record_slot_payload_read_76f4e(uVar2, uVar1, ((uchar *)camry_host_ptr((uint32_t)(uVar4))), 0);
  }
  return nvm_save_successful_alternate_slot_or_report_read_failure_757a4(iVar3, ((undefined4 *)camry_host_ptr((uint32_t)(param_2))));
}

undefined4 nvm_continue_alternate_payload_check_or_read_75902(undefined4 param_1,undefined4 param_2)

{
  int iVar1;
  
  iVar1 = nvm_get_request_mode_77c64();
  if (iVar1 == 1) {
    nvm_continue_record_checksum_scan_7712a();
  }
  else {
    thunk_nvm_continue_record_payload_read_77824();
  }
  return nvm_save_successful_alternate_slot_or_report_read_failure_757a4(iVar1, ((undefined4 *)camry_host_ptr((uint32_t)(param_2))));
}

undefined4 nvm_submit_mode_two_marker_with_kind_specific_errors_75928(int param_1,undefined4 param_2)

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
  if ((iVar3 != 0) && (iVar3 = nvm_submit_four_byte_record_marker_write_7808c(uVar2,DAT_febf6c3e,2), iVar3 != 2)) {
    uVar6 = nvm_finish_result_by_physical_operation_kind_750b2(((undefined *)camry_host_ptr((uint32_t)(iVar3))), ((undefined4 *)camry_host_ptr((uint32_t)(param_2))));
  }
  return uVar6;
}

undefined4 nvm_arm_mode_two_marker_with_kind_specific_errors_75982(undefined4 param_1, undefined4 param_2)

{
  nvm_arm_record_marker_submission_74f72();
  return nvm_submit_mode_two_marker_with_kind_specific_errors_75928(param_1, param_2);
}

undefined4 thunk_nvm_submit_mode_two_marker_with_kind_specific_errors_75928(undefined4 param_1, undefined4 param_2)

{
  return nvm_submit_mode_two_marker_with_kind_specific_errors_75928(param_1, param_2);
}

undefined4 nvm_poll_mode_two_marker_or_retry_state_fifteen_7599e(undefined4 param_1,undefined4 param_2)

{
  undefined4 camry_r10_0;

  uint32_t puVar1;
  int iVar2;
  undefined4 uVar3;
  
  puVar1 = 0x23dfcu;
  (camry_r10_0 = nvm_get_state_machine_result_word_783d4());
  iVar2 = (nvm_clear_record_marker_submission_latch_74f7e(), (int)(uintptr_t)camry_r10_0);
  if (iVar2 == 1) {
    uVar3 = 0xf;
  }
  else if (DAT_febf6c52 < (byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x3b2f)))))) {
    DAT_febf6c52 = DAT_febf6c52 + 1;
    nvm_arm_record_marker_submission_74f72();
    uVar3 = nvm_submit_mode_two_marker_with_kind_specific_errors_75928(param_1, param_2);
  }
  else {
    uVar3 = nvm_finish_result_by_physical_operation_kind_750b2(((undefined *)camry_host_ptr((uint32_t)(iVar2))), ((undefined4 *)camry_host_ptr((uint32_t)(param_2))));
  }
  return uVar3;
}

undefined4 nvm_erase_next_slot_with_kind_specific_errors_759e2(undefined4 param_1,undefined4 param_2)

{
  undefined4 uVar1;
  undefined4 uVar2;
  int iVar3;
  undefined4 uVar4;
  
  uVar4 = 0xff;
  uVar1 = nvm_get_storage_handle_77c9e();
  uVar2 = nvm_compute_next_record_slot_low_two_bits_7543c(DAT_febf6c3e);
  iVar3 = nvm_erase_record_slot_allocation_76e36(uVar1,uVar2);
  if (iVar3 != 2) {
    uVar4 = nvm_finish_result_by_physical_operation_kind_750b2(((undefined *)camry_host_ptr((uint32_t)(iVar3))), ((undefined4 *)camry_host_ptr((uint32_t)(param_2))));
  }
  return uVar4;
}

undefined4 nvm_poll_erase_or_retry_state_sixteen_75a1a(undefined4 param_1,undefined4 param_2)

{
  uint32_t puVar1;
  int iVar2;
  undefined4 uVar3;
  undefined4 uVar4;
  
  puVar1 = 0x23dfcu;
  iVar2 = nvm_get_state_machine_result_word_783d4();
  uVar3 = nvm_get_storage_handle_77c9e();
  if (iVar2 == 1) {
    uVar3 = 0x10;
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
    uVar3 = nvm_finish_result_by_physical_operation_kind_750b2(((undefined *)camry_host_ptr((uint32_t)(iVar2))), ((undefined4 *)camry_host_ptr((uint32_t)(param_2))));
  }
  return uVar3;
}

undefined4 nvm_start_record_copy_to_next_slot_75a78(undefined4 param_1,undefined4 param_2)

{
  undefined4 uVar1;
  undefined4 uVar2;
  int iVar3;
  undefined4 uVar4;
  
  uVar4 = 0xff;
  uVar1 = nvm_get_storage_handle_77c9e();
  uVar2 = nvm_compute_next_record_slot_low_two_bits_7543c(DAT_febf6c3e);
  iVar3 = camry_host_addr(nvm_begin_record_slot_copy_7723c(uVar1,uVar2,DAT_febf6c40));
  if (iVar3 != 2) {
    uVar4 = nvm_finish_result_by_physical_operation_kind_750b2(((undefined *)camry_host_ptr((uint32_t)(iVar3))), ((undefined4 *)camry_host_ptr((uint32_t)(param_2))));
  }
  return uVar4;
}

undefined4 nvm_poll_record_copy_or_retry_state_seventeen_75ab8(undefined4 param_1,undefined4 param_2)

{
  int iVar1;
  undefined4 uVar2;
  
  iVar1 = nvm_get_state_machine_result_word_783d4();
  if (iVar1 == 1) {
    uVar2 = 0x11;
  }
  else {
    uVar2 = nvm_retry_state_fifteen_or_finish_result_750fe(iVar1,param_2);
  }
  return uVar2;
}

undefined4 nvm_submit_mode_one_marker_with_kind_specific_errors_75ad8(int param_1,undefined4 param_2)

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
    uVar6 = nvm_finish_result_by_physical_operation_kind_750b2(((undefined *)camry_host_ptr((uint32_t)(iVar3))), ((undefined4 *)camry_host_ptr((uint32_t)(param_2))));
  }
  return uVar6;
}

undefined4 nvm_arm_mode_one_marker_with_kind_specific_errors_75b32(undefined4 param_1, undefined4 param_2)

{
  nvm_arm_record_marker_submission_74f72();
  return nvm_submit_mode_one_marker_with_kind_specific_errors_75ad8(param_1, param_2);
}

undefined4 thunk_nvm_submit_mode_one_marker_with_kind_specific_errors_75ad8(undefined4 param_1, undefined4 param_2)

{
  return nvm_submit_mode_one_marker_with_kind_specific_errors_75ad8(param_1, param_2);
}

undefined1 nvm_advance_record_copy_slots_and_select_state_75b4e(undefined4 *param_1)

{
  char cVar1;
  undefined1 uVar2;
  int iVar3;
  
  cVar1 = DAT_febf6c54 + -1;
  DAT_febf6c54 = cVar1;
  DAT_febf6c3e = nvm_compute_next_record_slot_low_two_bits_7543c(DAT_febf6c3e);
  if (cVar1 == '\0') {
    DAT_febf6c53 = 2;
    iVar3 = nvm_get_request_mode_77c64();
    if (iVar3 == 1) {
      uVar2 = 2;
      DAT_febf6c52 = 0;
    }
    else if (iVar3 == 2) {
      uVar2 = 6;
    }
    else {
      *param_1 = ((uint32_t)(0xfffbu));
      uVar2 = 0;
    }
  }
  else {
    uVar2 = 0xe;
    DAT_febf6c40 = DAT_febf6c3e;
  }
  return uVar2;
}

uint32_t nvm_poll_mode_one_marker_then_advance_copy_slots_75bb6(undefined4 param_1,undefined4 param_2)

{
  uint32_t camry_r10_result;
  undefined4 camry_r10_0;

  uint32_t puVar1;
  int iVar2;
  
  puVar1 = 0x23dfcu;
  (camry_r10_0 = (camry_r10_result = nvm_get_state_machine_result_word_783d4()));
  iVar2 = (nvm_clear_record_marker_submission_latch_74f7e(), (int)(uintptr_t)camry_r10_0);
  if (iVar2 == 1) {
    (camry_r10_result = nvm_advance_record_copy_slots_and_select_state_75b4e(((undefined4 *)camry_host_ptr((uint32_t)(param_2)))));
  }
  else if (DAT_febf6c52 < (byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x3b2f)))))) {
    DAT_febf6c52 = DAT_febf6c52 + 1;
    nvm_arm_record_marker_submission_74f72();
    (camry_r10_result = nvm_submit_mode_one_marker_with_kind_specific_errors_75ad8(param_1, param_2));
  }
  else {
    (camry_r10_result = nvm_finish_result_by_physical_operation_kind_750b2(((undefined *)camry_host_ptr((uint32_t)(iVar2))), ((undefined4 *)camry_host_ptr((uint32_t)(param_2)))));
  }
  return camry_r10_result;
}

uint nvm_write_marker_for_current_descriptor_slot_75bfe(undefined2 param_1,undefined1 param_2)

{
  undefined4 uVar1;
  
  uVar1 = nvm_get_storage_handle_77c9e();
  return nvm_submit_four_byte_record_marker_write_7808c(uVar1,param_1,param_2);
}

uint nvm_erase_current_descriptor_slot_75c1c(undefined2 param_1)

{
  undefined4 uVar1;
  
  uVar1 = nvm_get_storage_handle_77c9e();
  return nvm_erase_record_slot_allocation_76e36(uVar1,param_1);
}

uint nvm_write_current_source_to_descriptor_slot_75c34(undefined2 param_1)

{
  undefined4 uVar1;
  undefined4 uVar2;
  
  uVar1 = nvm_get_storage_handle_77c9e();
  uVar2 = nvm_get_write_source_77cbe();
  return nvm_begin_record_slot_write_76e6a(uVar1,param_1,uVar2);
}

undefined4 nvm_start_mode_three_marker_slot_two_75c54(undefined4 param_1,int *param_2)

{
  int iVar1;
  undefined4 uVar2;
  
  uVar2 = 0xff;
  iVar1 = nvm_write_marker_for_current_descriptor_slot_75bfe(2,3);
  if (iVar1 != 2) {
    *param_2 = iVar1;
    uVar2 = 0;
  }
  return uVar2;
}

undefined4 nvm_poll_slot_two_marker_select_state_nineteen_75c76(undefined4 param_1,undefined4 *param_2)

{
  uint status;
  undefined4 uVar2;
  
  status = nvm_get_state_machine_result_word_783d4();
  if (status == 1) {
    uVar2 = 0x13;
  }
  else {
    *param_2 = status;
    uVar2 = 0;
    if (status == 0xfffd) {
      nvm_mark_attempt_compare_mismatch_76992();
    }
  }
  return uVar2;
}

undefined4 nvm_start_mode_three_marker_slot_one_75ca0(undefined4 param_1,int *param_2)

{
  int iVar1;
  undefined4 uVar2;
  
  uVar2 = 0xff;
  iVar1 = nvm_write_marker_for_current_descriptor_slot_75bfe(1,3);
  if (iVar1 != 2) {
    *param_2 = iVar1;
    uVar2 = 0;
  }
  return uVar2;
}

undefined4 nvm_poll_slot_one_marker_select_state_twenty_75cc2(undefined4 param_1,undefined4 *param_2)

{
  uint status;
  undefined4 uVar2;
  
  status = nvm_get_state_machine_result_word_783d4();
  if (status == 1) {
    uVar2 = 0x14;
  }
  else {
    *param_2 = status;
    uVar2 = 0;
    if (status == 0xfffd) {
      nvm_mark_attempt_compare_mismatch_76992();
    }
  }
  return uVar2;
}

undefined4 nvm_start_current_descriptor_slot_zero_erase_75cec(undefined4 param_1,int *param_2)

{
  int iVar1;
  undefined4 uVar2;
  
  uVar2 = 0xff;
  iVar1 = nvm_erase_current_descriptor_slot_75c1c(0);
  if (iVar1 != 2) {
    *param_2 = iVar1;
    uVar2 = 0;
  }
  return uVar2;
}

undefined4 nvm_poll_slot_zero_erase_select_state_twenty_one_75d0c(undefined4 param_1,int *param_2)

{
  int iVar1;
  undefined4 uVar2;
  
  iVar1 = nvm_get_state_machine_result_word_783d4();
  if (iVar1 == 1) {
    uVar2 = 0x15;
  }
  else {
    *param_2 = iVar1;
    uVar2 = 0;
  }
  return uVar2;
}

undefined4 nvm_start_current_descriptor_slot_one_erase_75d2a(undefined4 param_1,int *param_2)

{
  int iVar1;
  undefined4 uVar2;
  
  uVar2 = 0xff;
  iVar1 = nvm_erase_current_descriptor_slot_75c1c(1);
  if (iVar1 != 2) {
    *param_2 = iVar1;
    uVar2 = 0;
  }
  return uVar2;
}

undefined4 nvm_poll_slot_one_erase_select_state_twenty_two_75d4a(undefined4 param_1,int *param_2)

{
  int iVar1;
  undefined4 uVar2;
  
  iVar1 = nvm_get_state_machine_result_word_783d4();
  if (iVar1 == 1) {
    uVar2 = 0x16;
  }
  else {
    *param_2 = iVar1;
    uVar2 = 0;
  }
  return uVar2;
}

undefined4 nvm_step_erase_record_selector2_75d68(undefined4 param_1,int *param_2)

{
  int iVar1;
  undefined4 uVar2;
  
  uVar2 = 0xff;
  iVar1 = nvm_erase_current_descriptor_slot_75c1c(2);
  if (iVar1 != 2) {
    *param_2 = iVar1;
    uVar2 = 0;
  }
  return uVar2;
}

undefined4 nvm_poll_result_to_phase23_75d88(undefined4 param_1,int *param_2)

{
  int iVar1;
  undefined4 uVar2;
  
  iVar1 = nvm_get_state_machine_result_word_783d4();
  if (iVar1 == 1) {
    uVar2 = 0x17;
  }
  else {
    *param_2 = iVar1;
    uVar2 = 0;
  }
  return uVar2;
}

undefined4 nvm_step_write_record_selector2_75da6(undefined4 param_1,int *param_2)

{
  int iVar1;
  undefined4 uVar2;
  
  uVar2 = 0xff;
  iVar1 = nvm_write_current_source_to_descriptor_slot_75c34(2);
  if (iVar1 != 2) {
    *param_2 = iVar1;
    uVar2 = 0;
  }
  return uVar2;
}

undefined4 nvm_poll_result_to_phase24_mark_mismatch_75dc6(undefined4 param_1,undefined4 *param_2)

{
  uint status;
  undefined4 uVar2;
  
  status = nvm_get_state_machine_result_word_783d4();
  if (status == 1) {
    uVar2 = 0x18;
  }
  else {
    *param_2 = status;
    uVar2 = 0;
    if (status == 0xfffd) {
      nvm_mark_attempt_compare_mismatch_76992();
    }
  }
  return uVar2;
}

undefined4 nvm_step_write_record_selector1_75df0(undefined4 param_1,int *param_2)

{
  int iVar1;
  undefined4 uVar2;
  
  uVar2 = 0xff;
  iVar1 = nvm_write_current_source_to_descriptor_slot_75c34(1);
  if (iVar1 != 2) {
    *param_2 = iVar1;
    uVar2 = 0;
  }
  return uVar2;
}

undefined4 nvm_poll_result_to_phase25_mark_mismatch_75e10(undefined4 param_1,undefined4 *param_2)

{
  uint status;
  undefined4 uVar2;
  
  status = nvm_get_state_machine_result_word_783d4();
  if (status == 1) {
    uVar2 = 0x19;
  }
  else {
    *param_2 = status;
    uVar2 = 0;
    if (status == 0xfffd) {
      nvm_mark_attempt_compare_mismatch_76992();
    }
  }
  return uVar2;
}

undefined4 nvm_step_write_selector1_marker2_75e3a(undefined4 param_1,int *param_2)

{
  int iVar1;
  undefined4 uVar2;
  
  uVar2 = 0xff;
  iVar1 = nvm_write_marker_for_current_descriptor_slot_75bfe(1,2);
  if (iVar1 != 2) {
    *param_2 = iVar1;
    uVar2 = 0;
  }
  return uVar2;
}

undefined4 nvm_poll_result_to_phase26_mark_mismatch_75e5c(undefined4 param_1,undefined4 *param_2)

{
  uint status;
  undefined4 uVar2;
  
  status = nvm_get_state_machine_result_word_783d4();
  if (status == 1) {
    uVar2 = 0x1a;
  }
  else {
    *param_2 = status;
    uVar2 = 0;
    if (status == 0xfffd) {
      nvm_mark_attempt_compare_mismatch_76992();
    }
  }
  return uVar2;
}

undefined4 nvm_step_write_selector1_marker1_75e86(undefined4 param_1,int *param_2)

{
  int iVar1;
  undefined4 uVar2;
  
  uVar2 = 0xff;
  iVar1 = nvm_write_marker_for_current_descriptor_slot_75bfe(1,1);
  if (iVar1 != 2) {
    *param_2 = iVar1;
    uVar2 = 0;
  }
  return uVar2;
}

undefined4 nvm_poll_result_to_phase27_mark_mismatch_75ea8(undefined4 param_1,undefined4 *param_2)

{
  uint status;
  undefined4 uVar2;
  
  status = nvm_get_state_machine_result_word_783d4();
  if (status == 1) {
    uVar2 = 0x1b;
  }
  else {
    *param_2 = status;
    uVar2 = 0;
    if (status == 0xfffd) {
      nvm_mark_attempt_compare_mismatch_76992();
    }
  }
  return uVar2;
}

undefined4 nvm_step_write_selector0_marker2_75ed2(undefined4 param_1,int *param_2)

{
  int iVar1;
  undefined4 uVar2;
  
  uVar2 = 0xff;
  iVar1 = nvm_write_marker_for_current_descriptor_slot_75bfe(0,2);
  if (iVar1 != 2) {
    *param_2 = iVar1;
    uVar2 = 0;
  }
  return uVar2;
}

undefined4 nvm_poll_result_to_phase28_mark_mismatch_75ef4(undefined4 param_1,undefined4 *param_2)

{
  uint status;
  undefined4 uVar2;
  
  status = nvm_get_state_machine_result_word_783d4();
  if (status == 1) {
    uVar2 = 0x1c;
  }
  else {
    *param_2 = status;
    uVar2 = 0;
    if (status == 0xfffd) {
      nvm_mark_attempt_compare_mismatch_76992();
    }
  }
  return uVar2;
}

undefined4 nvm_step_gated_selector0_marker1_75f1e(int param_1,int *param_2)

{
  uint8_t stack_record_20[32];
  undefined4 *puVar1;
  int iVar2;
  undefined4 uVar3;
  undefined4 *puVar4;
  undefined4 uVar5;
  undefined4 *puVar6;
  
  puVar1 = ((uint32_t *)(stack_record_20));
  puVar6 = ((undefined4 *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)((param_1 + 4))))))));
  uVar5 = 0xff;
  puVar4 = puVar6 + 5;
  do {
    uVar3 = *puVar6;
    puVar6 = puVar6 + 1;
    *puVar1 = uVar3;
    puVar1 = puVar1 + 1;
  } while (camry_host_addr(puVar4)!=camry_host_addr(puVar6));
  iVar2 = nvm_claim_marker_submission_when_gate_zero_74f88(stack_record_20[16]);
  if ((iVar2 != 0) && (iVar2 = nvm_write_marker_for_current_descriptor_slot_75bfe(0,1), iVar2 != 2)) {
    *param_2 = iVar2;
    uVar5 = 0;
  }
  return uVar5;
}

undefined4 nvm_arm_and_step_selector0_marker1_75f64(undefined4 param_1, undefined4 param_2)

{
  nvm_arm_record_marker_submission_74f72();
  return nvm_step_gated_selector0_marker1_75f1e(param_1, ((int *)camry_host_ptr((uint32_t)(param_2))));
}

undefined4 thunk_nvm_step_gated_selector0_marker1_75f1e(undefined4 param_1, undefined4 param_2)

{
  return nvm_step_gated_selector0_marker1_75f1e(param_1, ((int *)camry_host_ptr((uint32_t)(param_2))));
}

undefined4 nvm_poll_marker_then_initialize_or_publish_75f80(undefined4 param_1,undefined4 *param_2)

{
  uint32_t puVar1;
  
  puVar1 = nvm_get_state_machine_result_word_783d4();
  nvm_clear_record_marker_submission_latch_74f7e();
  if (puVar1 == 0x1) {
    run_init_chain_75042(1);
  }
  else {
    *param_2 = puVar1;
    if (puVar1 == 0xfffdu) {
      nvm_mark_attempt_compare_mismatch_76992();
    }
  }
  return 0;
}

undefined4 nvm_delay_phase29_then_publish_result_75fb0(undefined *param_1,undefined4 *param_2)

{
  undefined4 uVar1;
  
  if (DAT_febf6c52 < DAT_0002792b) {
    DAT_febf6c52 = DAT_febf6c52 + 1;
    uVar1 = 0x1d;
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

undefined4 nvm_step_erase_alternate_selector_75fe4(undefined4 param_1,int *param_2)

{
  undefined4 uVar1;
  undefined4 uVar2;
  int iVar3;
  undefined4 uVar4;
  
  uVar4 = 0xff;
  uVar1 = nvm_get_storage_handle_77c9e();
  uVar2 = nvm_compute_next_record_slot_low_two_bits_7543c(DAT_febf6c3e);
  iVar3 = nvm_erase_record_slot_allocation_76e36(uVar1,uVar2);
  if (iVar3 != 2) {
    *param_2 = iVar3;
    uVar4 = 0;
  }
  return uVar4;
}
