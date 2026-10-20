#include "common.h"

undefined4 faci_map_fstatr_error_mask_to_seven_79026(void)

{
  uint uVar1;
  undefined4 uVar2;
  
  uVar1 = camry_read32(0xffa10080u);
  if ((uVar1 & 0x24068) == 0) {
    uVar2 = 0;
  }
  else {
    uVar2 = 7;
  }
  return uVar2;
}

bool faci_decode_and_clear_completion_status_79084(char *param_1)

{
  char cVar1;
  uint uVar2;
  
  uVar2 = faci_decode_completion_status();
  *param_1 = (char)uVar2;
  faci_clear_error_status_78c30();
  cVar1 = *param_1;
  if (cVar1 != '\0') {
    faci_select_dataflash_pe_or_read_mode_78c70(0);
  }
  return cVar1 == '\0';
}

bool faci_check_errors_and_stop_failed_command_790ae(undefined1 *param_1)

{
  int iVar1;
  
  iVar1 = faci_map_fstatr_error_mask_to_seven_79026();
  if (iVar1 != 0) {
    faci_force_stop_and_poll();
    faci_select_dataflash_pe_or_read_mode_78c70(0);
    *param_1 = (char)iVar1;
  }
  return iVar1 == 0;
}

uint32_t faci_poll_ready_and_decode_result_byte_790d6(undefined1 *param_1)

{
  uint32_t camry_r10_result;
  int iVar1;
  undefined1 uStack_9;
  
  uStack_9 = 1;
  iVar1 = (camry_r10_result = read_fstatr_ready_bit_78bfa());
  if ((iVar1 == 1) && (iVar1 = (camry_r10_result = faci_check_errors_and_stop_failed_command_790ae(&uStack_9)), iVar1 == 1)) {
    (camry_r10_result = faci_decode_and_clear_completion_status_79084(&uStack_9));
  }
  *param_1 = uStack_9;
  return camry_r10_result;
}

void faci_wait_ready_decode_and_clear_saved_operation_7910a(undefined1 *param_1)

{
  uint uVar1;
  int iVar2;
  undefined1 uStack_9;
  
  uStack_9 = 1;
  uVar1 = poll_word_masks((0xffa10080u),0x8000,0x8000,0x393);
  if (uVar1 < 2) {
    iVar2 = faci_check_errors_and_stop_failed_command_790ae(&uStack_9);
    if (iVar2 == 1) {
      faci_decode_and_clear_completion_status_79084(&uStack_9);
    }
  }
  else {
    uStack_9 = 8;
    faci_force_stop_and_poll();
    faci_select_dataflash_pe_or_read_mode_78c70(0);
  }
  *param_1 = uStack_9;
  dataflash_clear_saved_range_and_program_buffer_78af8();
  return;
}

void dataflash_finalize_job_and_notify_result_79164(char param_1)

{
  undefined4 uVar1;
  
  if (param_1 == '\0') {
    DAT_febf6cb1 = 0;
    DAT_febf6cb0 = 1;
    DAT_febf6cb3 = 0;
    nvm_set_driver_completion_state_one_74ec2();
    dataflash_clear_saved_range_and_program_buffer_78af8();
  }
  else {
    DAT_febf6cb3 = 0;
    DAT_febf6cb0 = 1;
    DAT_febf6cb1 = 1;
    if (DAT_febf6cac == '\x01') {
      uVar1 = 7;
    }
    else {
      uVar1 = 8;
    }
    nvm_set_driver_completion_from_saved_result_74ed0();
    dataflash_clear_saved_range_and_program_buffer_78af8();
    nvm_forward_flash_driver_error_7939c(0x5c,0,6,uVar1);
  }
  return;
}

undefined4 dataflash_wait_completion_and_translate_result_791b2(void)

{
  int iVar1;
  char cStack_5;
  
  faci_wait_ready_decode_and_clear_saved_operation_7910a(&cStack_5);
  if (cStack_5 == '\0') {
    iVar1 = faci_select_dataflash_pe_or_read_mode_78c70(0);
    if (iVar1 == 0) {
      return 2;
    }
  }
  else if (cStack_5 == '\x05') {
    return 7;
  }
  return 8;
}

undefined4 faci_request_suspend_when_command_suspendable_791e2(void)

{
  uint uVar1;
  undefined4 uVar2;
  
  uVar1 = camry_read32(0xffa10080u);
  if ((uVar1 >> 0xf & 1) == 0) {
    if ((uVar1 >> 0xb & 1) == 0) {
      uVar1 = poll_word_masks((0xffa10080u),0x8000,0x800,0x73);
      if (uVar1 == 0) goto LAB_00079210;
      if (uVar1 != 1) {
        return 8;
      }
    }
    camry_write8(0xffa20000u, 0xb0);
    uVar2 = 2;
  }
  else {
LAB_00079210:
    uVar2 = 10;
  }
  return uVar2;
}

undefined4 dataflash_select_suspend_policy_7922c(char param_1)

{
  undefined4 uVar1;
  int iVar2;
  
  if (param_1 == '\x01') {
    iVar2 = read_fstatr_ready_bit_78bfa();
    if (iVar2 == 1) {
      uVar1 = 10;
    }
    else {
      uVar1 = 2;
    }
  }
  else {
    uVar1 = faci_request_suspend_when_command_suspendable_791e2();
  }
  return uVar1;
}

uint faci_decode_suspended_or_completed_command_79250(void)

{
  uint uVar1;
  
  uVar1 = camry_read32(0xffa10080u);
  if ((uVar1 & 0x300) == 0) {
    uVar1 = faci_map_fstatr_error_mask_to_seven_79026();
    if ((uVar1 == 0) && (uVar1 = faci_decode_completion_status(), uVar1 == 0)) {
      uVar1 = 2;
    }
  }
  else {
    uVar1 = 1;
  }
  return uVar1;
}

undefined4 dataflash_save_suspend_result_and_exit_pe_mode_7927e(void)

{
  int iVar1;
  undefined4 uVar2;
  
  DAT_febf6cb3 = faci_decode_suspended_or_completed_command_79250();
  iVar1 = faci_select_dataflash_pe_or_read_mode_78c70(0);
  if (iVar1 == 0) {
    uVar2 = 0;
  }
  else {
    uVar2 = 4;
  }
  flash_set_software_enables(0);
  return uVar2;
}

bool faci_has_program_or_erase_suspend_bits_792a6(void)

{
  uint uVar1;
  
  uVar1 = camry_read32(0xffa10080u);
  return (uVar1 & 0x300) != 0;
}

int faci_resume_if_suspend_bits_set_792c0(void)

{
  int iVar1;
  
  iVar1 = faci_has_program_or_erase_suspend_bits_792a6();
  if (iVar1 == 1) {
    camry_write8(0xffa20000u, 0xd0);
  }
  return iVar1;
}

undefined1 unmask_eic379_interrupt_and_sync_792dc(void)

{
  byte bVar1;
  undefined1 uVar2;
  
  bVar1 = camry_read8(0xffffb2f6u);
  camry_write8(0xffffb2f6u, bVar1 & 0x7f);
  uVar2 = camry_read8(0xffffb2f6u);
  __synchronize();
  return uVar2;
}

uint icus20_second_read_bit0(void)

{
  uint *source;
  uint uVar1;
  
  load_u32(((uint *)camry_host_ptr((uint32_t)((0xffc5d020u)))));
  uVar1 = load_u32(((uint *)camry_host_ptr((uint32_t)((int)0xffc5d020))));
  return uVar1 & 1;
}

void dataflash_handle_suspend_ready_notification_79316(void)

{
  uint uVar1;
  int iVar2;
  undefined1 uStack_9;
  
  mask_eic379_interrupt_and_sync_78b90();
  uVar1 = icus20_second_read_bit0();
  if (uVar1 == 0) {
    iVar2 = read_fstatr_ready_bit_78bfa();
    if (iVar2 == 1) {
      if (DAT_febf6cb2 == '\x0f') {
        iVar2 = dataflash_save_suspend_result_and_exit_pe_mode_7927e();
        uStack_9 = (undefined1)iVar2;
        if (iVar2 == 0) {
          DAT_febf6cb2 = '\x10';
        }
      }
      else {
        uStack_9 = 3;
      }
    }
    else {
      uStack_9 = 2;
    }
  }
  else {
    uStack_9 = 1;
  }
  nvm_forward_pointed_suspend_result_793dc(&uStack_9);
  return;
}

void return_only_stub_7936c(void)

{
  return;
}

void nvm_initialize_dataflash_read_controls(void)

{
  camry_write8(0xffc59810u, '\x0f');
  camry_write32(0xffc5b000u, 0x4000);
  camry_write32(0xffc5b014u, 0);
  camry_write32(0xffc5b01cu, 0x4000);
  return;
}

void nvm_initialize_dataflash_read_controls_wrapper_79388(void)

{
  nvm_initialize_dataflash_read_controls();
  return;
}

undefined4 nvm_forward_flash_driver_error_7939c(undefined2 param_1,undefined1 param_2,undefined1 param_3,undefined1 param_4)

{
  return nvm_capture_module_5c_driver_error_unless_masked_74efe(param_1,param_2,param_3,param_4);
}

undefined4 nvm_copy_suspend_policy_to_output_793c8(undefined1 *param_1)

{
  undefined1 uVar1;
  
  uVar1 = nvm_get_suspend_policy_byte_781b4();
  *param_1 = uVar1;
  return 0;
}

void nvm_forward_pointed_suspend_result_793dc(undefined1 *param_1)

{
  nvm_forward_flash_suspend_notification_7813e(*param_1);
  return;
}

void syncp(void)

{
  __synchronize();
  return;
}

bool nvm_query_crypto_activation_nonzero_79420(void)

{
  int iVar1;
  
  iVar1 = is_either_crypto_activation_enabled_79d12();
  return iVar1 != 0;
}

bool return_false_via_zero_hook_79432(void)

{
  int iVar1;
  
  iVar1 = return_const_0_79d24();
  return iVar1 != 0;
}

undefined4 nvm_is_current_service_twelve_79444(void)

{
  int iVar1;
  undefined4 uVar2;
  
  uVar2 = 1;
  iVar1 = nvm_get_current_service_byte_79b5c();
  if (iVar1 != 0xc) {
    iVar1 = return_const_0_79d28();
    if (iVar1 == 0) {
      uVar2 = 0;
    }
    else {
      uVar2 = 1;
    }
  }
  return uVar2;
}

void invoke_noop_halfword_hook_79462(undefined2 param_1)

{
  ((void)(param_1), return_only_stub_79d2c());
  return;
}

uint nvm_driver_gate_rejected(ushort ignored_service)

{
  uint uVar1;
  
  uVar1 = nvm_driver_gate_hook();
  return (uint)(uVar1 != 0);
}

int nvm_direct_write_if_mode_and_range_allowed_7949c(undefined4 param_1,uint param_2,undefined4 param_3,uint param_4)

{
  int iVar1;
  uint uVar2;
  int iVar3;
  
  iVar1 = nvm_get_direct_operation_mode_79c94();
  iVar3 = 8;
  if ((((iVar1 != 0) && (uVar2 = nvm_probe_range_rejected(param_2,param_4), uVar2 == 0)) &&
      (iVar1 = nvm_guarded_submit_write_service11_7682e(param_2,param_4,param_3), iVar3 = iVar1, iVar1 != 7)) &&
     (iVar3 = 8, iVar1 == 9)) {
    iVar3 = iVar1;
  }
  return iVar3;
}

uint nvm_request_erase_span(uint unused_selector,uint byte_offset,uint byte_count)

{
  int iVar1;
  uint uVar2;
  uint uVar3;
  uint page_count;
  
  iVar1 = nvm_get_direct_operation_mode_79c94();
  uVar3 = 8;
  if (iVar1 != 0) {
    page_count = byte_count + 0x3f >> 6 & 0xffff;
    uVar2 = nvm_erase_span_outside_region(byte_offset,page_count);
    if (((uVar2 == 0) &&
        (uVar2 = nvm_guarded_erase_admission(byte_offset,page_count), uVar3 = uVar2, uVar2 != 7)
        ) && (uVar3 = 8, uVar2 == 9)) {
      uVar3 = uVar2;
    }
  }
  return uVar3;
}

void nvm_poll_direct_operation(void)

{
  int iVar1;
  
  iVar1 = nvm_get_direct_operation_mode_79c94();
  if (iVar1 != 0) {
    nvm_guarded_direct_poll();
  }
  return;
}

int nvm_direct_read_if_mode_and_range_allowed_79554(undefined4 param_1,uint param_2,undefined4 param_3,uint param_4)

{
  int iVar1;
  uint uVar2;
  int iVar3;
  int iVar4;
  
  iVar4 = 4;
  iVar1 = nvm_get_direct_operation_mode_79c94();
  iVar3 = iVar4;
  if ((((iVar1 != 0) && (uVar2 = nvm_probe_range_rejected(param_2,param_4), uVar2 == 0)) &&
      (iVar3 = nvm_guarded_read_map_service_status_768e8(param_2, param_4, ((uchar *)camry_host_ptr((uint32_t)(param_3)))), iVar3 != 0)) && ((iVar3 != 6 && (iVar3 != 9)))
     ) {
    iVar3 = iVar4;
  }
  return iVar3;
}

uint nvm_classify_storage_range(uint ignored_selector,uint byte_offset,uint byte_count)

{
  int iVar1;
  uint uVar2;
  uint uVar3;
  uint uVar4;
  
  uVar4 = 4;
  iVar1 = nvm_get_direct_operation_mode_79c94();
  uVar3 = uVar4;
  if ((((iVar1 != 0) && (uVar2 = nvm_probe_range_rejected(byte_offset,byte_count), uVar2 == 0))
      && (uVar3 = nvm_probe_storage_range(byte_offset,(ushort)byte_count), uVar3 != 2)) &&
     (((uVar3 != 3 && (uVar3 != 6)) && (uVar3 != 9)))) {
    uVar3 = uVar4;
  }
  return uVar3;
}

uint nvm_erase_span_outside_region(uint byte_offset,uint page_count)

{
  uint uVar1;
  uint uVar2;
  
  uVar2 = 1;
  if (nvm_region_first_page != 0xffff) {
    uVar1 = byte_offset >> 6 & 0xffff;
    if (nvm_region_first_page <= uVar1) {
      uVar2 = (uint)((((uint)nvm_region_page_count + (uint)nvm_region_first_page) - 1 &
                     0xffff) < ((page_count + uVar1) - 1 & 0xffff));
    }
  }
  return uVar2;
}

void nvm_reset_diagnostic_service_state_79638(void)

{
  nvm_service_diagnostic_mask = 0;
  DAT_febf6cbc = 0xffff;
  nvm_service_cd_diagnostic_mask = 0;
  DAT_febf6cc4 = 0xffff;
  DAT_febf6cb4 = 0;
  DAT_febf6cb8 = 0;
  nvm_diagnostic_service = 0xff;
  return;
}

void nvm_begin_diagnostic_service_and_snapshot_record_79662(uint param_1)

{
  param_1 = param_1 & 0xff;
  if (2 < param_1 - 6) {
    if (param_1 == 0xc || param_1 == 0xd) goto LAB_00079686;
    if (2 < param_1 - 0x16) {
      param_1 = 0xffffffff;
    }
  }
  nvm_diagnostic_service = (uchar)param_1;
LAB_00079686:
  DAT_febf6cbc = nvm_get_current_record_identifier_79b66();
  nvm_service_diagnostic_mask = 0;
  return;
}

void nvm_begin_cd_diagnostic_service_7969a(uchar param_1)

{
  nvm_service_cd_diagnostic_mask = 0;
  DAT_febf6cc4 = 0;
  if (param_1 != '\f' && param_1 != '\r') {
    param_1 = 0xff;
  }
  nvm_diagnostic_service = param_1;
  return;
}

void return_only_stub_796ba(void)

{
  return;
}

void return_only_stub_796bc(void)

{
  return;
}

void nvm_set_diagnostic_group_bits_796be(uint param_1)

{
  uint uVar1;
  
  uVar1 = DAT_febf6cb4;
  if ((param_1 & 0xff) < 3) {
    DAT_febf6cb4 = *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x27cccu + (uint32_t)((param_1 & 0xff) * 8) * 1u)))) | DAT_febf6cb4;
    nvm_recompute_derived_diagnostic_mask_797f6();
    if (uVar1 != DAT_febf6cb4) {
      ((void)(((undefined *)camry_host_ptr(0xfebf6cb4u))), return_only_stub_79d36());
    }
  }
  return;
}

void nvm_clear_diagnostic_group_bits_796f4(uint param_1)

{
  if ((param_1 & 0xff) < 3) {
    DAT_febf6cb4 = DAT_febf6cb4 & ~*(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x27cccu + (uint32_t)((param_1 & 0xff) * 8) * 1u))));
    nvm_recompute_derived_diagnostic_mask_797f6();
  }
  return;
}

undefined4 nvm_get_diagnostic_service_record_and_mask_79780(uint param_1,undefined2 *param_2)

{
  int iVar1;
  undefined4 uVar2;
  
  param_1 = param_1 & 0xff;
  uVar2 = 1;
  iVar1 = nvm_reject_null_output_or_mismatched_diagnostic_service_79848((uint)(byte)param_1, camry_host_addr(param_2));
  if ((iVar1 == 0) &&
     (((param_1 - 6 < 3 || (param_1 == 0xc || param_1 == 0xd)) || (param_1 - 0x16 < 3)))) {
    *param_2 = DAT_febf6cbc;
    *(uint *)(param_2 + 2) = nvm_service_diagnostic_mask;
    uVar2 = 0;
  }
  return uVar2;
}

undefined4 nvm_get_cd_diagnostic_record_and_mask_797c2(char param_1,undefined2 *param_2)

{
  int iVar1;
  undefined4 uVar2;
  
  uVar2 = 1;
  iVar1 = nvm_reject_null_output_or_mismatched_diagnostic_service_79848((uint)(byte)param_1, camry_host_addr(param_2));
  if ((iVar1 == 0) && (param_1 == '\f' || param_1 == '\r')) {
    *param_2 = DAT_febf6cc4;
    *(uint *)(param_2 + 2) = nvm_service_cd_diagnostic_mask;
    uVar2 = 0;
  }
  return uVar2;
}

void nvm_recompute_derived_diagnostic_mask_797f6(void)

{
  uint uVar1;
  uint uVar2;
  
  DAT_febf6cb8 = 0;
  uVar1 = 0;
  uVar2 = 0;
  do {
    if ((*(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x27cccu + (uint32_t)(uVar2 * 8) * 1u)))) & DAT_febf6cb4) != 0) {
      uVar1 = uVar1 | *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x27cd0u + (uint32_t)(uVar2 * 8) * 1u))));
      DAT_febf6cb8 = uVar1;
    }
    uVar2 = uVar2 + 1;
  } while (uVar2 < 3);
  return;
}

bool nvm_reject_null_output_or_mismatched_diagnostic_service_79848(uchar param_1,int param_2)

{
  if (param_2 != 0) {
    return param_1 != nvm_diagnostic_service;
  }
  return true;
}

void nvm_reset_suspend_notification_latch_79862(void)

{
  DAT_febf6cd2 = 0;
  DAT_febf6cd4 = 0xff;
  DAT_febf6cd3 = 0xff;
  return;
}

void nvm_set_suspend_state_and_mirror_7987e(undefined1 param_1)

{
  DAT_febf6cd0 = param_1;
  DAT_febf6cd1 = param_1;
  return;
}

void nvm_finish_pending_suspend_success_7988a(void)

{
  if (DAT_febf6cd0 == '\x01') {
    nvm_set_suspend_state_and_mirror_7987e(2);
    nvm_forward_suspend_report_to_status_callback_79d38(0);
  }
  return;
}

void nvm_finish_pending_suspend_failure_798aa(void)

{
  if (DAT_febf6cd0 == '\x01') {
    nvm_set_suspend_state_and_mirror_7987e(0);
    nvm_forward_suspend_report_to_status_callback_79d38(2);
  }
  return;
}

void nvm_dispatch_suspend_notification_result_798ca(char param_1)

{
  if (param_1 == '\0') {
    nvm_finish_pending_suspend_success_7988a();
  }
  else if (param_1 != '\x05') {
    nvm_finish_pending_suspend_failure_798aa();
  }
  return;
}

void nvm_enable_and_drain_suspend_notification_798e6(void)

{
  DAT_febf6cd2 = 1;
  if (DAT_febf6cd3 == '\x01') {
    nvm_dispatch_suspend_notification_result_798ca(DAT_febf6cd4);
  }
  DAT_febf6cd3 = 0xff;
  DAT_febf6cd4 = 0xff;
  return;
}

void nvm_start_suspend_and_publish_status_7990e(void)

{
  int iVar1;
  undefined1 uVar2;
  
  if (DAT_febf6cd0 == '\0') {
    nvm_reset_suspend_notification_latch_79862();
    iVar1 = nvm_suspend_flash_and_mark_access_flag_7812a();
    if (iVar1 == 2) {
      nvm_set_suspend_state_and_mirror_7987e(1);
      uVar2 = 1;
    }
    else if (iVar1 == 10) {
      nvm_set_suspend_state_and_mirror_7987e(2);
      uVar2 = 0;
    }
    else {
      nvm_set_suspend_state_and_mirror_7987e(0);
      uVar2 = 2;
    }
    nvm_forward_suspend_report_to_status_callback_79d38(uVar2);
    nvm_enable_and_drain_suspend_notification_798e6();
  }
  else {
    nvm_forward_suspend_report_to_status_callback_79d38(3);
  }
  return;
}

void nvm_request_suspend_with_service_guards_7995c(void)

{
  if ((nvm_service_guards.service == '\0') || (nvm_service_guards.paired_call == '\0')) {
    nvm_service_guards.deferred = '\0';
    nvm_forward_suspend_report_to_status_callback_79d38(1);
  }
  else {
    nvm_start_suspend_and_publish_status_7990e();
  }
  return;
}

void nvm_buffer_or_dispatch_suspend_result_7998a(undefined1 param_1)

{
  if (DAT_febf6cd2 == '\0') {
    DAT_febf6cd3 = 1;
    DAT_febf6cd4 = param_1;
  }
  else {
    nvm_dispatch_suspend_notification_result_798ca((uint)(byte)param_1);
  }
  return;
}

void nvm_resume_completed_suspend_and_clear_state_799b0(void)

{
  if (DAT_febf6cd0 == '\x02') {
    nvm_resume_flash_or_reset_physical_path_7814c();
  }
  nvm_set_suspend_state_and_mirror_7987e(0);
  return;
}

void thunk_nvm_resume_completed_suspend_and_clear_state_799b0(void)

{
  nvm_resume_completed_suspend_and_clear_state_799b0();
  return;
}

void nvm_cancel_or_resume_suspend_and_clear_state_799da(void)

{
  if (DAT_febf6cd0 == '\x01') {
    nvm_abort_selected_flash_path_with_guard_78176();
  }
  else if (DAT_febf6cd0 == '\x02') {
    nvm_resume_flash_or_reset_physical_path_7814c();
  }
  nvm_set_suspend_state_and_mirror_7987e(0);
  return;
}

void nvm_initialize_suspend_guards_and_state_79a0e(void)

{
  DAT_febf6cd4 = 0xff;
  DAT_febf6cd3 = 0xff;
  DAT_febf6cd2 = 1;
  nvm_service_guards.deferred = 0xff;
  nvm_service_guards.paired_call = '\x01';
  nvm_service_guards.service = '\x01';
  nvm_set_suspend_state_and_mirror_7987e(0);
  return;
}

void nvm_consume_deferred_guard(void)

{
  if ((nvm_service_guards.service == '\x01') && (nvm_service_guards.paired_call == '\x01'))
  {
    nvm_service_guards.deferred = 0xff;
  }
  return;
}

void nvm_enter_service_guard(void)

{
  nvm_consume_deferred_guard();
  nvm_service_guards.service = '\0';
  return;
}

void nvm_finish_deferred_guard(void)

{
  camry_write32((camry_sp - 4u) & ~3u, camry_gpr[29]);
  camry_write32((camry_sp - 8u) & ~3u, camry_gpr[31]);
  camry_sp -= 8u;
  camry_gpr[3] = camry_sp;

  if ((nvm_service_guards.service == '\x01') && (nvm_service_guards.paired_call == '\x01'))
  {
    if (nvm_service_guards.deferred == '\0') {
      (camry_gpr[29] = 0xfebf6ccdu, camry_gpr[31] = 0x79a8au, nvm_start_suspend_and_publish_status_7990e)();
    }
    nvm_service_guards.deferred = 0xff;
  }
  { if (!camry_halted) { camry_gpr[29] = camry_read32((camry_sp + 4u) & ~3u); camry_gpr[31] = camry_read32((camry_sp + 0u) & ~3u); camry_sp += 8u; camry_gpr[3] = camry_sp; } return; }
}

void nvm_leave_service_guard(void)

{
  camry_write32((camry_sp - 4u) & ~3u, camry_gpr[31]);
  camry_sp -= 4u;
  camry_gpr[3] = camry_sp;

  nvm_service_guards.service = '\x01';
  (camry_gpr[31] = 0x79aa6u, nvm_finish_deferred_guard)();
  { if (!camry_halted) { camry_gpr[31] = camry_read32((camry_sp + 0u) & ~3u); camry_sp += 4u; camry_gpr[3] = camry_sp; } return; }
}

void nvm_enter_paired_call_guard_79aaa(void)

{
  nvm_consume_deferred_guard();
  nvm_service_guards.paired_call = '\0';
  return;
}

void nvm_leave_paired_call_guard_79abe(void)

{
  nvm_service_guards.paired_call = '\x01';
  nvm_finish_deferred_guard();
  return;
}

undefined1 nvm_suspend_state_mirror_differs_79ad4(void)

{
  if (DAT_febf6cd0 != DAT_febf6cd1) {
    return 1;
  }
  return 0;
}

undefined1 nvm_get_suspend_state_with_mirror_recovery_79af0(void)

{
  int iVar1;
  
  iVar1 = nvm_suspend_state_mirror_differs_79ad4();
  if (iVar1 != 0) {
    nvm_set_suspend_state_and_mirror_7987e(0);
  }
  return DAT_febf6cd0;
}

bool nvm_suspend_state_is_nonzero_79b0e(void)

{
  return DAT_febf6cd0 != '\0';
}

void nvm_initialize_service_diagnostics_and_suspend_state_79b1e(void)

{
  DAT_febf6cdb = 0;
  nvm_service_mode_nonzero = '\0';
  DAT_febf6cd9 = 0;
  DAT_febf6cd6 = 0xffff;
  DAT_febf6cd8 = 0xff;
  nvm_clear_direct_operation_mode_79c6c();
  nvm_reset_diagnostic_service_state_79638();
  nvm_initialize_suspend_guards_and_state_79a0e();
  return;
}

undefined1 nvm_get_current_service_byte_79b5c(void)

{
  return DAT_febf6cd8;
}

undefined2 nvm_get_current_record_identifier_79b66(void)

{
  return DAT_febf6cd6;
}

undefined4 nvm_encode_service_readiness_status_79b70(void)

{
  int iVar1;
  undefined4 uVar2;
  
  iVar1 = nvm_get_service_and_queue_status_741a0();
  if (iVar1 == 2) {
    uVar2 = 0x1e;
  }
  else if ((iVar1 == 4) ||
          ((iVar1 = nvm_get_direct_operation_mode_79c94(), iVar1 == 0 && (iVar1 = thunk_nvm_classify_active_or_enabled_driver_state_76688(), iVar1 != 1)))) {
    uVar2 = 0xf0;
  }
  else {
    uVar2 = 0xf;
  }
  return uVar2;
}

void nvm_set_record_and_begin_diagnostic_service_79bc0(undefined2 param_1,char param_2)

{
  if ((param_2 != '\f') && (param_2 != '\r')) {
    DAT_febf6cd8 = param_2;
  }
  DAT_febf6cd6 = param_1;
  nvm_begin_diagnostic_service_and_snapshot_record_79662(param_2);
  return;
}

void nvm_set_service_and_begin_cd_diagnostics_79be8(undefined1 param_1)

{
  DAT_febf6cd8 = param_1;
  nvm_begin_cd_diagnostic_service_7969a((uint)(byte)param_1);
  return;
}

void nvm_clear_record_and_non_cd_service_79bfe(undefined4 param_1,char param_2)

{
  if ((param_2 != '\f') && (param_2 != '\r')) {
    DAT_febf6cd8 = 0xff;
  }
  DAT_febf6cd6 = 0xffff;
  ((void)(param_2), return_only_stub_796ba());
  return;
}

void nvm_clear_current_service_byte_79c2a(undefined1 param_1)

{
  DAT_febf6cd8 = 0xff;
  ((void)(param_1), return_only_stub_796bc());
  return;
}

void nvm_set_service_state_byte_cd9_79c42(undefined1 param_1)

{
  DAT_febf6cd9 = param_1;
  return;
}

void nvm_store_service_mode_nonzero(uchar value)

{
  nvm_service_mode_nonzero = value;
  return;
}

void nvm_set_service_state_byte_cdb_79c56(undefined1 param_1)

{
  DAT_febf6cdb = param_1;
  return;
}

void nvm_service_acquisition_driver(void)

{
  nvm_service_logical_and_physical_driver();
  return;
}

void nvm_clear_direct_operation_mode_79c6c(void)

{
  nvm_direct_operation_mode = '\0';
  return;
}

uchar nvm_get_direct_mode_or_suspend_marker_79c76(void)

{
  uchar uVar1;
  int iVar2;
  
  iVar2 = nvm_get_suspend_state_with_mirror_recovery_79af0();
  uVar1 = 'U';
  if (iVar2 == 0) {
    uVar1 = nvm_direct_operation_mode;
  }
  return uVar1;
}

uchar nvm_get_direct_operation_mode_79c94(void)

{
  return nvm_direct_operation_mode;
}

uint nvm_reconcile_probe_mode(void)

{
  int iVar1;
  uint uVar2;
  
  iVar1 = nvm_get_suspend_state_with_mirror_recovery_79af0();
  uVar2 = nvm_refresh_direct_probe_mode();
  if (iVar1 != 0) {
    uVar2 = 0x55;
  }
  return uVar2;
}

uint nvm_poll_probe_mode(void)

{
  uint uVar1;
  
  uVar1 = nvm_reconcile_probe_mode();
  return uVar1;
}

bool nvm_cancel_physical_operation_if_direct_mode_79cc4(void)

{
  bool bVar1;
  
  bVar1 = nvm_direct_operation_mode == '\0';
  if (!bVar1) {
    nvm_cancel_physical_operation_wrapper_741de();
  }
  return bVar1;
}

uint nvm_refresh_direct_probe_mode(void)

{
  int iVar1;
  uint uVar2;
  
  iVar1 = ((void)(0), nvm_direct_operation_request_equals_5a_79d46());
  if (iVar1 == 0) {
    if (nvm_direct_operation_mode != '\0') {
      nvm_cancel_scheduler_operation_mode_zero_741d0();
    }
    uVar2 = 0;
  }
  else {
    uVar2 = 0x55;
  }
  nvm_direct_operation_mode = (uchar)uVar2;
  return uVar2;
}

bool is_either_crypto_activation_enabled_79d12(void)

{
  int iVar1;
  
  iVar1 = get_crypto_activation_is_one_5a_6a192();
  return iVar1 != 0;
}

undefined4 return_const_0_79d24(void)

{
  return 0;
}

undefined4 return_const_0_79d28(void)

{
  return 0;
}

void return_only_stub_79d2c(void)

{
  return;
}

uint nvm_driver_gate_hook(void)

{
  return 0;
}

void return_only_stub_79d32(void)

{
  return;
}

void return_only_stub_79d34(void)

{
  return;
}

void return_only_stub_79d36(void)

{
  return;
}

void nvm_forward_suspend_report_to_status_callback_79d38(undefined1 param_1)

{
  translate_icus_scheduler_result_and_update_crypto_state_87ef6(param_1);
  return;
}

bool nvm_direct_operation_request_equals_5a_79d46(void)

{
  int iVar1;
  
  iVar1 = get_nvm_direct_operation_request_byte_68f64();
  return iVar1 == 0x5a;
}

void cantp_initialize_default_configuration_wrapper_79d60(void)

{
  ((void)(0), initialize_cantp_flags_and_configuration_state_7a30e());
  return;
}

void cantp_foreground_cycle_wrapper_79d7a(void)

{
  cantp_foreground_cycle();
  return;
}

void invoke_noop_byte_hook_7b204_79d86(undefined1 param_1)

{
  ((void)(param_1), return_only_stub_7b204());
  return;
}

void invoke_noop_byte_hook_7b206_79d94(undefined1 param_1)

{
  ((void)(param_1), return_only_stub_7b206());
  return;
}

void cantp_confirm_can_frame_wrapper_79da2(ushort param_1)

{
  cantp_confirm_can_frame(param_1);
  return;
}

void cantp_receive_can_frame_wrapper_79db0(ushort param_1,F33PduInfo *param_2)

{
  cantp_receive_can_frame(param_1,param_2);
  return;
}

uint pdur_cantp_transmit_adapter(ushort transmit_id,F33PduInfo *response)

{
  uint uVar1;
  
  uVar1 = cantp_transmit_descriptor(transmit_id,response);
  return uVar1;
}

uint cantp_cancel_transmit_wrapper_79dcc(undefined2 param_1)

{
  return cancel_cantp_transmit_if_initialized_and_in_range_7a38c(param_1);
}

undefined4 cantp_update_receive_flow_parameter_wrapper_79dda(undefined2 param_1,undefined1 param_2,undefined2 param_3)

{
  return validate_and_change_cantp_receive_connection_81fa6(param_1,param_2,param_3);
}

uint cantp_cancel_receive_wrapper_79dec(undefined2 param_1)

{
  return cancel_cantp_receive_if_initialized_and_in_range_7a3ca(param_1);
}

void run_init_chain_79dfa(void)

{
  initialize_normal_network_channel_state_and_hooks_7c2ee();
  ((void)(0), return_only_stub_81588());
  ((void)(0), initialize_driver_channels_and_registers_83f3e());
  ((void)(0), initialize_controller_request_tokens_and_bytes_7f75a());
  walk_all_normal_channels_through_three_notification_hooks_7c478();
  broadcast_21b70_callback_slot_zero_7f250(0);
  ((void)(0), initialize_selected_network_modes_and_recovery_7c710());
  cantp_initialize_default_configuration_wrapper_79d60();
  return;
}

void initialize_network_controllers_and_transport_state_79e2c(void)

{
  byte bVar1;
  uint32_t puVar2;
  byte logical_controller;
  
  puVar2 = 0x23dfcu;
  walk_all_normal_channels_through_two_notification_hooks_7c4a2();
  bVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x25c0)))));
  for (logical_controller = 0; logical_controller < bVar1;
      logical_controller = logical_controller + 1) {
    request_logical_controller_run_stop(logical_controller,'\x03');
  }
  set_all_controller_cache_6e91_and_reset_7fac6();
  broadcast_21b70_callback_slot_four_7f27c();
  set_selected_network_modes_07f8_and_clear_fault_causes_7c748();
  thunk_mark_cantp_uninitialized_with_clear_fault_status_7b3a6();
  return;
}

void run_init_chain_79e60(void)

{
  walk_all_normal_channels_through_two_notification_hooks_7c4a2();
  reset_all_channel_states_and_quiesce_registers_84160();
  return_only_stub_8158e();
  set_all_controller_cache_6e91_and_reset_7fac6();
  broadcast_21b70_callback_slot_four_7f27c();
  set_selected_network_modes_07f8_and_clear_fault_causes_7c748();
  thunk_mark_cantp_uninitialized_with_clear_fault_status_7b3a6();
  return;
}

void run_init_chain_79e84(void)

{
  reset_normal_network_policy_bytes_and_run_hooks_7c4c6();
  ((void)(0), return_only_stub_81588());
  ((void)(0), initialize_driver_channels_and_registers_83f3e());
  ((void)(0), initialize_controller_request_tokens_and_bytes_7f75a());
  walk_all_normal_channels_through_three_notification_hooks_7c478();
  broadcast_21b70_callback_slot_zero_7f250(0);
  ((void)(0), initialize_selected_network_modes_and_recovery_7c710());
  cantp_initialize_default_configuration_wrapper_79d60();
  restart_channel_setup_preserving_valid_zero_fault_classes_7c50a();
  return;
}

void dispatch_two_active_channel_callback_passes_79eba(void)

{
  poll_transmit_completions_for_state_57a8_channels_851b8();
  service_receive_path_one_for_state_57a8_channels_83ce4();
  return;
}

void service_can_transmit_timers_and_queues_wrapper_79eca(void)

{
  return_only_stub_7f364();
  return_only_stub_7c60c();
  tick_active_tx_queue_delays_and_service_802ee();
  return;
}

void service_receive_and_mark_eligible_network_states_79ede(void)

{
  char cVar1;
  byte bVar2;
  uint32_t puVar3;
  int iVar4;
  byte bVar5;
  
  puVar3 = 0x23dfcu;
  return_only_stub_7c60a();
  service_enabled_controller_message_rings_809fe();
  cVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x25bf)))));
  bVar2 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x25c0)))));
  for (bVar5 = 0; bVar5 < bVar2; bVar5 = bVar5 + 1) {
    iVar4 = test_matching_channel_stub_returns_zero_7f6a4(bVar5);
    if (iVar4 == 1) {
      set_record_4937_token_e1_7ed4e(cVar1 + bVar5);
    }
  }
  return;
}

void run_init_chain_79f16(void)

{
  driver_poll_pending_channel_modes();
  service_driver_busoff_observation_latches_835d4();
  check_channel_state_integrity_and_dispatch_first_failure_83724();
  poll_cached_controller_hooks_and_status_80c88();
  service_selected_network_recovery_and_mode_delays_7c93e();
  broadcast_21b00_callback_slot_eight_7f33c();
  return;
}

void thunk_cantp_foreground_cycle_wrapper_79d7a(void)

{
  cantp_foreground_cycle_wrapper_79d7a();
  return;
}

void clear_upper_network_software_indications_79f42(void)

{
  uint uVar1;
  uint uVar2;
  
  uVar2 = (uint)DAT_00021865;
  for (uVar1 = 0; uVar1 < uVar2; uVar1 = uVar1 + 1 & 0xff) {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe3df0u + (uint32_t)(uVar1) * 1u)))) = '\0';
  }
  return;
}

undefined4 check_ready_networks_and_selected_mode_activity_79f5c(void)

{
  byte bVar1;
  uint32_t puVar2;
  int iVar3;
  undefined4 uVar4;
  byte bVar5;
  
  puVar2 = 0x23dfcu;
  if (((int16_t)DAT_febe3df2) == -0x1ff) {
    return_only_stub_7be40();
    bVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x2597)))));
    for (bVar5 = 0; bVar5 < bVar1; bVar5 = bVar5 + 1) {
      iVar3 = compose_record_status_flags_7e804(bVar5);
      if (iVar3 != 0) {
        return 0xff;
      }
    }
    uVar4 = check_normal_network_transition_or_mode_activity_7c58c();
  }
  else {
    uVar4 = 0;
  }
  return uVar4;
}

void set_upper_network_indication_one_79f9a(uint param_1)

{
  if ((param_1 & 0xff) < (uint)DAT_00021865) {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe3df0u + (uint32_t)(param_1 & 0xff) * 1u)))) = '\x01';
    return_only_stub_7be4c();
  }
  return;
}

void set_upper_network_indication_three_79fba(uint param_1)

{
  if ((param_1 & 0xff) < (uint)DAT_00021865) {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe3df0u + (uint32_t)(param_1 & 0xff) * 1u)))) = '\x03';
    return_only_stub_7be4a();
  }
  return;
}

void clear_upper_network_indication_and_notify_79fda(uint param_1)

{
  param_1 = param_1 & 0xff;
  if (param_1 < DAT_00021865) {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe3df0u + (uint32_t)(param_1) * 1u)))) = '\0';
    disable_packet_channel_and_notify_if_current_82eb0(param_1);
    ((void)(param_1), return_only_stub_7be48());
  }
  return;
}
