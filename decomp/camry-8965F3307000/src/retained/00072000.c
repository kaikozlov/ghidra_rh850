#include "common.h"

int call_nvm_status_stub_zero_without_read_override_72010(undefined2 param_1)

{
  int iVar1;
  
  iVar1 = nvm_has_read_buffer_override_7475a();
  if (iVar1 == 0) {
    ((void)(param_1), (void)(0), return_only_stub_71ce0());
  }
  return iVar1;
}

void set_nvm_write_buffer_wrapper_7202c(ushort param_1,void *param_2)

{
  nvm_set_write_buffer(param_1, camry_host_addr(param_2));
  return;
}

int call_nvm_status_stub_70_without_write_override_7203a(undefined2 param_1)

{
  int iVar1;
  
  iVar1 = nvm_has_write_buffer_override_7476a();
  if (iVar1 == 0) {
    ((void)(param_1), (void)(0x70), return_only_stub_71ce0());
  }
  return iVar1;
}

int call_nvm_status_stub_zero_without_write_override_72058(undefined2 param_1)

{
  int iVar1;
  
  iVar1 = nvm_has_write_buffer_override_7476a();
  if (iVar1 == 0) {
    ((void)(param_1), (void)(0), return_only_stub_71ce0());
  }
  return iVar1;
}

void set_nvm_read_buffer_wrapper_72074(ushort param_1,void *param_2)

{
  nvm_set_read_buffer(param_1, camry_host_addr(param_2));
  return;
}

int call_nvm_status_stub_77_without_read_override_72082(undefined2 param_1)

{
  int iVar1;
  
  iVar1 = nvm_has_read_buffer_override_7475a();
  if (iVar1 == 0) {
    ((void)(param_1), (void)(0x77), return_only_stub_71ce0());
  }
  return iVar1;
}

int call_nvm_status_stub_zero_without_read_override_720a0(undefined2 param_1)

{
  int iVar1;
  
  iVar1 = nvm_has_read_buffer_override_7475a();
  if (iVar1 == 0) {
    ((void)(param_1), (void)(0), return_only_stub_71ce0());
  }
  return iVar1;
}

void set_nvm_category_six_state_one_720bc(void)

{
  DAT_febf6100 = 1;
  return;
}

void notify_nvm_category_six_720c8(void)

{
  notify_nvm_category_state_one_or_two_71e88(6);
  return;
}

void set_nvm_category_three_state_one_720d6(void)

{
  DAT_febf60fd = 1;
  return;
}

void notify_nvm_category_three_720e2(void)

{
  notify_nvm_category_state_one_or_two_71e88(3);
  return;
}

void change_nvm_category_state_four_to_one_720f0(uint param_1)

{
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebf60fau + (uint32_t)(param_1 & 0xff) * 1u)))) == '\x04') {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebf60fau + (uint32_t)(param_1 & 0xff) * 1u)))) = '\x01';
  }
  return;
}

void set_nvm_category_state_two_72108(uint param_1)

{
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebf60fau + (uint32_t)(param_1 & 0xff) * 1u)))) = 2;
  return;
}

void accumulate_nvm_diagnostic_mask_by_category_7211a(uint param_1)

{
  nvm_accumulate_diagnostic_mask((uint)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x273dcu + (uint32_t)(param_1 & 0xff) * 4u)))));
  return;
}

void record_nvm_integrity_fault_72130(void)

{
  nvm_set_diagnostic_group_bits_796be(2);
  DAT_febf6102 = 0xf;
  return;
}

uint nvm_service_uninitialized(void)

{
  return (uint)(((int8_t)DAT_febf6102) != -0x10);
}

int dispatch_nvm_callback_from_26c04_7215a(undefined2 param_1)

{
  return (*(int (*)())camry_indirect((uint32_t)(PTR_return_const_0_68f6e_00026c04)))(param_1);
}

int dispatch_nvm_callback_from_26c00_7216c(undefined2 param_1)

{
  return (*(int (*)())camry_indirect((uint32_t)(PTR_return_const_0_68f6a_00026c00)))(param_1);
}

void reset_nvm_scheduler_state_7217e(void)

{
  nvm_scheduler_phase = '\x01';
  DAT_febf6114 = 0x9da70ae7;
  nvm_scheduler_operation.operation = 0x9da70ae7;
  nvm_scheduler_operation.logical_handle = 0xffff;
  nvm_scheduler_operation.buffer_08 = 0;
  nvm_scheduler_operation.buffer_0c = 0;
  DAT_febf6120 = 0;
  DAT_febf6122 = 0xffff;
  DAT_febf6125 = 0;
  return;
}

void thunk_reset_nvm_scheduler_state_7217e(void)

{
  reset_nvm_scheduler_state_7217e();
  return;
}

uint nvm_snapshot_scheduler_operation(F33NvmOperation *output)

{
  ushort uVar1;
  uint uVar2;
  
  uVar1 = nvm_scheduler_operation.logical_handle;
  uVar2 = (uint)(nvm_scheduler_operation.operation != 0x9da70ae7);
  if (nvm_scheduler_operation.operation != 0x9da70ae7) {
    if (((nvm_scheduler_phase == '\b') || (nvm_scheduler_phase == '\x10')) ||
       (nvm_scheduler_phase == ' ')) {
      uVar2 = 2;
    }
    output->operation = nvm_scheduler_operation.operation;
    output->logical_handle = uVar1;
    output->buffer_08 = nvm_scheduler_operation.buffer_08;
    output->buffer_0c = nvm_scheduler_operation.buffer_0c;
  }
  return uVar2;
}

bool accept_nvm_scheduler_operation_if_idle_7220e(uint *param_1)

{
  bool bVar1;
  
  bVar1 = nvm_scheduler_operation.operation != 0x9da70ae7;
  if (!bVar1) {
    nvm_scheduler_operation.operation = *param_1;
    nvm_scheduler_phase = '\x01';
    nvm_scheduler_operation.logical_handle = (ushort)param_1[1];
    nvm_scheduler_operation.buffer_08 = ((uint32_t)(param_1[2]));
    nvm_scheduler_operation.buffer_0c = ((uint32_t)(param_1[3]));
  }
  return bVar1;
}

void cancel_nvm_operation_and_select_scheduler_phase_72248(char param_1)

{
  uchar uVar1;
  bool bVar2;
  
  nvm_cancel_logical_operation();
  if (nvm_scheduler_operation.operation == 0x9da70ae7) {
    return;
  }
  if (param_1 == '\0') {
    if (nvm_scheduler_phase == ' ') {
      return;
    }
    uVar1 = '\b';
    bVar2 = nvm_scheduler_phase == '\x10';
  }
  else {
    if (param_1 == '\x02') {
      nvm_scheduler_phase = ' ';
      return;
    }
    uVar1 = '\x10';
    bVar2 = nvm_scheduler_phase == ' ';
  }
  if (!bVar2) {
    nvm_scheduler_phase = uVar1;
    return;
  }
  return;
}

undefined4 reject_nvm_scheduler_handle_for_operation_class_72298(int param_1)

{
  ushort uVar1;
  undefined4 uVar2;
  
  uVar2 = 1;
  uVar1 = nvm_scheduler_operation.logical_handle;
  if ((((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x27408u + (uint32_t)(param_1) * 1u)))) != '\0') &&
      (uVar1 = DAT_febf6122, nvm_scheduler_phase == '\x01')) ||
     ((uVar1 <= (ushort)(nvm_logical_descriptor_count - 1) && (1 < uVar1)))) {
    uVar2 = 0;
  }
  return uVar2;
}

uint dispatch_nvm_scheduler_completion_phase_722d4(short param_1,uint param_2)

{
  undefined *puVar1;
  int iVar2;
  uint uVar3;
  uint32_t pcVar4;
  
  puVar1 = ((undefined *)camry_host_ptr(0x23dfcu));
  param_2 = param_2 & 0xff;
  iVar2 = nvm_map_operation_state_two_to_two_else_one_73c76();
  if (iVar2 == 1) {
    iVar2 = param_1 * 0x18;
    if (param_2 == 4) {
      uVar3 = lookup_u32_pair_value_or_default_73a5c(DAT_febf6114, 0xff, ((uint *)camry_host_ptr((uint32_t)(0x3614u + (int)camry_host_addr(puVar1)))));
      if ((byte)puVar1[iVar2 + 0x36d4] <= uVar3) {
        return 4;
      }
      pcVar4 = (uint32_t)(camry_host_addr(*((code * *)camry_host_ptr((uint32_t)(uVar3 * 4 + *(int *)(puVar1 + iVar2 + 0x36d8))))));
    }
    else {
      puVar1 = puVar1 + iVar2;
      if (param_2 == 8) {
        pcVar4 = (uint32_t)((uint32_t)((*((volatile uint32_t *)((((undefined *)camry_host_ptr((uint32_t)(0x36dcu + (uint32_t)((int)camry_host_addr(puVar1)) * 1u)))))))));
      }
      else if (param_2 == 0x20) {
        pcVar4 = (uint32_t)((uintptr_t)(*((volatile uint32_t *)(puVar1 + 0x36e4))));
      }
      else {
        pcVar4 = (uint32_t)(camry_host_addr(*((code * *)camry_host_ptr((uint32_t)(0x36deu + (int)camry_host_addr((puVar1 + 2)))))));
      }
    }
    param_2 = (*(int (*)())camry_indirect((uint32_t)(pcVar4)))();
  }
  return param_2;
}

void advance_nvm_scheduler_operation_phase_72342(undefined4 param_1)

{
  camry_write32((camry_sp - 4u) & ~3u, camry_gpr[27]);
  camry_write32((camry_sp - 8u) & ~3u, camry_gpr[28]);
  camry_write32((camry_sp - 12u) & ~3u, camry_gpr[29]);
  camry_write32((camry_sp - 16u) & ~3u, camry_gpr[31]);
  camry_sp -= 16u;
  camry_gpr[3] = camry_sp;

  uint32_t puVar1;
  uint uVar2;
  uint uVar3;
  uint32_t pcVar4;
  int iVar5;
  
  uVar3 = (uint)nvm_scheduler_phase;
  puVar1 = 0x23dfcu;
  if (uVar3 == 1) {
    pcVar4 = (uint32_t)((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x274ccu + (uint32_t)((short)param_1 * 6) * 4u)))));
  }
  else {
    if (uVar3 != 2) goto LAB_0007239a;
    uVar2 = (camry_gpr[27] = 0xfebf6124u, camry_gpr[28] = param_1, camry_gpr[29] = uVar3, camry_gpr[6] = DAT_febf6114, camry_r7 = camry_gpr[7] = 0xffu, camry_gpr[8] = camry_tp + 0x3614u, camry_gpr[31] = 0x7237au, lookup_u32_pair_value_or_default_73a5c)(DAT_febf6114,0xff,((undefined *)camry_host_ptr(0x27410u)));
    iVar5 = (short)param_1 * 0x18;
    if ((byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(iVar5 + 0x36d4))))) <= uVar2) goto LAB_0007239a;
    pcVar4 = (uint32_t)((uintptr_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(uVar2 * 4 + (*((int *)camry_host_ptr((uint32_t)(puVar1 + iVar5 + 0x36d8)))))))));
  }
  uVar3 = (*(int (*)())camry_indirect((camry_gpr[27] = 0xfebf6124u, camry_gpr[28] = param_1, camry_gpr[29] = (uint32_t)(uintptr_t)pcVar4, camry_gpr[30] = camry_tp + (uint32_t)((int16_t)param_1 * 24) + (uVar3 == 1 ? 0u : 0x36d0u), camry_gpr[31] = 0x72398u, (uint32_t)(pcVar4))))();
LAB_0007239a:
  (camry_gpr[29] = uVar3, camry_gpr[31] = 0x7239eu, nvm_poll_pending_operation_73c14)();
  if ((((uVar3 == 4) || (uVar3 == 8)) || (uVar3 == 0x10)) || (uVar3 == 0x20)) {
    uVar3 = (camry_gpr[6] = param_1, camry_r7 = camry_gpr[7] = uVar3, camry_gpr[31] = 0x723bau, dispatch_nvm_scheduler_completion_phase_722d4)(param_1,uVar3);
  }
  if (uVar3 == 1) {
    nvm_scheduler_operation.operation = 0x9da70ae7;
  }
  nvm_scheduler_phase = (uchar)uVar3;
  { if (!camry_halted) { camry_gpr[27] = camry_read32((camry_sp + 12u) & ~3u); camry_gpr[28] = camry_read32((camry_sp + 8u) & ~3u); camry_gpr[29] = camry_read32((camry_sp + 4u) & ~3u); camry_gpr[31] = camry_read32((camry_sp + 0u) & ~3u); camry_sp += 16u; camry_gpr[3] = camry_sp; } return; }
}

void service_active_nvm_scheduler_operation_723d6(void)

{
  camry_write32((camry_sp - 4u) & ~3u, camry_gpr[29]);
  camry_write32((camry_sp - 8u) & ~3u, camry_gpr[31]);
  camry_sp -= 8u;
  camry_gpr[3] = camry_sp;

  uint uVar1;
  int iVar2;
  
  if (nvm_scheduler_operation.operation != 0x9da70ae7) {
    uVar1 = (camry_gpr[6] = nvm_scheduler_operation.operation, camry_r7 = camry_gpr[7] = 0xffu, camry_gpr[8] = camry_tp + 0x3604u, camry_gpr[31] = 0x723f8u, lookup_u32_pair_value_or_default_73a5c)(nvm_scheduler_operation.operation,0xff,((undefined *)camry_host_ptr(0x27400u)));
    if ((uVar1 < 8) && (iVar2 = (camry_gpr[29] = uVar1, camry_gpr[6] = uVar1, camry_gpr[31] = 0x72404u, reject_nvm_scheduler_handle_for_operation_class_72298)(uVar1), iVar2 == 0)) {
      (camry_gpr[29] = uVar1, camry_gpr[6] = uVar1, camry_gpr[31] = 0x7240eu, advance_nvm_scheduler_operation_phase_72342)(uVar1);
    }
    else {
      (camry_gpr[31] = 0x72414u, record_nvm_integrity_fault_72130)();
    }
  }
  { if (!camry_halted) { camry_gpr[29] = camry_read32((camry_sp + 4u) & ~3u); camry_gpr[31] = camry_read32((camry_sp + 0u) & ~3u); camry_sp += 8u; camry_gpr[3] = camry_sp; } return; }
}

bool sample_nvm_gate_and_set_wait_count_72418(void)

{
  int iVar1;
  
  iVar1 = nvm_query_crypto_activation_nonzero_79420();
  if (iVar1 != 0) {
    set_nvm_wait_count_five_or_65000_7305e(0);
  }
  else {
    set_nvm_wait_count_five_or_65000_7305e(1);
  }
  return iVar1 != 0;
}

undefined4 complete_nvm_single_operation_and_clear_suboperation_7243c(undefined1 param_1)

{
  uint uVar1;
  ushort uVar2;
  
  uVar2 = nvm_scheduler_operation.logical_handle;
  uVar1 = nvm_scheduler_operation.operation;
  finish_nvm_batch_item_event_and_notify_categories_71f82(nvm_scheduler_operation.logical_handle,nvm_scheduler_operation.operation);
  complete_nvm_queued_operation_unless_status16_72fde(uVar2,uVar1,param_1);
  DAT_febf6114 = 0x9da70ae7;
  return 1;
}

undefined4 submit_nvm_single_read_or_finish_failure_72474(void)

{
  ushort uVar1;
  uint uVar2;
  undefined4 uVar3;
  F33NvmOperation local_18;
  
  uVar1 = nvm_scheduler_operation.logical_handle;
  local_18.operation = 1;
  local_18.buffer_0c = 0;
  local_18.logical_handle = nvm_scheduler_operation.logical_handle;
  local_18.buffer_08 = DAT_febf6118;
  uVar2 = nvm_submit_operation(camry_host_addr(&local_18));
  if (uVar2 == 0) {
    uVar3 = 4;
    DAT_febf6114 = 0xa1a62093;
  }
  else {
    call_nvm_status_stub_zero_without_read_override_72010(uVar1);
    uVar3 = complete_nvm_single_operation_and_clear_suboperation_7243c(1);
  }
  return uVar3;
}

undefined4 begin_nvm_single_read_after_gate_724c0(void)

{
  ushort logical_handle;
  int iVar2;
  undefined4 uVar3;
  
  logical_handle = nvm_scheduler_operation.logical_handle;
  begin_nvm_batch_item_event_and_mark_categories_71f28(nvm_scheduler_operation.logical_handle,nvm_scheduler_operation.operation);
  iVar2 = sample_nvm_gate_and_set_wait_count_72418();
  if (iVar2 == 0) {
    set_nvm_read_buffer_wrapper_71fe4(logical_handle,(void *)camry_host_ptr(nvm_scheduler_operation.buffer_08));
    DAT_febf6118 = nvm_read_buffer(logical_handle);
    uVar3 = submit_nvm_single_read_or_finish_failure_72474();
  }
  else {
    uVar3 = 2;
    DAT_febf6114 = 0x3f721401;
  }
  return uVar3;
}

void dispatch_nvm_read_status_zero_or_eight_7250e(undefined2 param_1,char param_2)

{
  if (param_2 == '\0') {
    call_nvm_status_stub_70_without_read_override_71ff2((uint)(ushort)param_1);
  }
  else if (param_2 == '\b') {
    call_nvm_status_stub_77_without_read_override_72082(param_1);
  }
  return;
}

undefined4 finish_nvm_read_after_buffer_mode_callback_7252c(undefined1 param_1)

{
  ushort uVar1;
  int iVar2;
  undefined4 uVar3;
  
  uVar1 = nvm_scheduler_operation.logical_handle;
  iVar2 = nvm_acquire_mode_four_read_buffer_or_retry_7465a(nvm_scheduler_operation.logical_handle);
  if (iVar2 == 0) {
    dispatch_nvm_read_status_zero_or_eight_7250e(uVar1,param_1);
  }
  else {
    if (iVar2 != 1) {
      if (iVar2 != 2) {
        return 2;
      }
      DAT_febf6114 = 0x22aa8a36;
      return 2;
    }
    set_nvm_category_state_two_72108(4);
    accumulate_nvm_diagnostic_mask_by_category_7211a(1);
    call_nvm_status_stub_zero_without_read_override_72010(uVar1);
    param_1 = 1;
  }
  uVar3 = complete_nvm_single_operation_and_clear_suboperation_7243c(param_1);
  return uVar3;
}

uint32_t complete_nvm_read_after_buffer_callback_7258c(undefined1 param_1)

{
  uint32_t camry_r10_result;
  ushort uVar1;
  int iVar2;
  
  uVar1 = nvm_scheduler_operation.logical_handle;
  iVar2 = ((void)(nvm_scheduler_operation.logical_handle), (void)(DAT_febf6118), (camry_r10_result = return_const_1_745c0()));
  if (iVar2 == 0) {
    DAT_febf6125 = 8;
    (camry_r10_result = finish_nvm_read_after_buffer_mode_callback_7252c(0x8));
  }
  else {
    (camry_r10_result = call_nvm_status_stub_zero_without_read_override_72010(uVar1));
    (camry_r10_result = complete_nvm_single_operation_and_clear_suboperation_7243c(param_1));
  }
  return camry_r10_result;
}

undefined4 process_nvm_single_read_result_725ce(void)

{
  uint32_t puVar1;
  int iVar2;
  undefined4 uVar3;
  uint uVar4;
  
  puVar1 = 0x23dfcu;
  uVar4 = (uint)nvm_scheduler_operation.logical_handle;
  iVar2 = nvm_get_operation_state_u8_73c6c();
  DAT_febf6125 = (undefined1)iVar2;
  if (iVar2 == 0) {
    if (((*((ushort *)camry_host_ptr((uint32_t)(puVar1 + uVar4 * 0x10 + 0x2e1a)))) >> 0xb & 1) != 0) {
      set_nvm_logical_write_inhibit_71ce2(uVar4,1);
    }
    uVar3 = finish_nvm_read_after_buffer_mode_callback_7252c(0);
  }
  else {
    uVar3 = 2;
    if ((iVar2 == 1) || (iVar2 == 3)) {
      uVar3 = complete_nvm_read_after_buffer_callback_7258c(iVar2);
    }
    else if (iVar2 == 5) {
      call_nvm_status_stub_zero_without_read_override_72010(uVar4);
      uVar3 = complete_nvm_single_operation_and_clear_suboperation_7243c(5);
    }
  }
  return uVar3;
}

undefined4 resume_nvm_single_read_with_saved_result_72632(void)

{
  return finish_nvm_read_after_buffer_mode_callback_7252c(DAT_febf6125);
}

undefined4 submit_nvm_single_write_after_buffer_mode_callback_72646(void)

{
  ushort logical_handle;
  int iVar1;
  uint uVar2;
  undefined4 uVar3;
  F33NvmOperation local_20;
  
  logical_handle = nvm_scheduler_operation.logical_handle;
  iVar1 = nvm_acquire_mode_four_write_buffer_or_retry_74708(nvm_scheduler_operation.logical_handle);
  if (iVar1 == 0) {
    DAT_febf611c = nvm_write_buffer(logical_handle);
    local_20.buffer_08 = 0;
    local_20.logical_handle = logical_handle;
    local_20.operation = 2;
    local_20.buffer_0c = DAT_febf611c;
    uVar2 = nvm_submit_operation(camry_host_addr(&local_20));
    if (uVar2 == 0) {
      DAT_febf6114 = 0x22aa8a36;
      return 4;
    }
  }
  else {
    if (iVar1 != 1) {
      if (iVar1 != 2) {
        return 2;
      }
      DAT_febf6114 = 0xa1a62093;
      return 2;
    }
    set_nvm_category_state_two_72108(4);
    accumulate_nvm_diagnostic_mask_by_category_7211a(1);
  }
  call_nvm_status_stub_zero_without_write_override_72058(logical_handle);
  uVar3 = complete_nvm_single_operation_and_clear_suboperation_7243c(1);
  return uVar3;
}

undefined4 begin_nvm_single_write_after_gate_726c4(void)

{
  ushort uVar1;
  void *pvVar2;
  int iVar3;
  undefined4 uVar4;
  
  pvVar2 = ((void *)camry_host_ptr((uint32_t)(nvm_scheduler_operation.buffer_0c)));
  uVar1 = nvm_scheduler_operation.logical_handle;
  begin_nvm_batch_item_event_and_mark_categories_71f28(nvm_scheduler_operation.logical_handle,nvm_scheduler_operation.operation);
  iVar3 = sample_nvm_gate_and_set_wait_count_72418();
  if (iVar3 == 0) {
    set_nvm_write_buffer_wrapper_7202c(uVar1,pvVar2);
    uVar4 = submit_nvm_single_write_after_buffer_mode_callback_72646();
  }
  else {
    uVar4 = 2;
    DAT_febf6114 = 0x3f721401;
  }
  return uVar4;
}

undefined4 thunk_submit_nvm_single_write_after_buffer_mode_callback_72646(void)

{
  return submit_nvm_single_write_after_buffer_mode_callback_72646();
}

undefined4 process_nvm_single_write_result_72710(void)

{
  uint32_t puVar1;
  int iVar2;
  undefined4 uVar3;
  uint uVar4;
  
  puVar1 = 0x23dfcu;
  uVar4 = (uint)nvm_scheduler_operation.logical_handle;
  iVar2 = nvm_get_operation_state_u8_73c6c();
  if (iVar2 == 0) {
    if (((*((ushort *)camry_host_ptr((uint32_t)(puVar1 + uVar4 * 0x10 + 0x2e1a)))) >> 0xb & 1) != 0) {
      set_nvm_logical_write_inhibit_71ce2(uVar4,1);
    }
    call_nvm_status_stub_70_without_write_override_7203a(uVar4);
  }
  else {
    if (iVar2 != 1) {
      return 2;
    }
    call_nvm_status_stub_zero_without_write_override_72058(uVar4);
  }
  uVar3 = complete_nvm_single_operation_and_clear_suboperation_7243c(iVar2);
  return uVar3;
}

undefined4 finish_nvm_buffer_read_after_mode_callback_7275e(void)

{
  ushort uVar1;
  undefined4 uVar2;
  int iVar3;
  
  uVar1 = nvm_scheduler_operation.logical_handle;
  iVar3 = nvm_acquire_mode_four_read_buffer_or_retry_7465a(nvm_scheduler_operation.logical_handle);
  if (iVar3 == 0) {
    call_nvm_status_stub_77_without_read_override_72082(uVar1);
    uVar2 = 0;
  }
  else {
    if (iVar3 != 1) {
      if (iVar3 != 2) {
        return 2;
      }
      DAT_febf6114 = 0xa1a62093;
      return 2;
    }
    accumulate_nvm_diagnostic_mask_by_category_7211a(1);
    call_nvm_status_stub_zero_without_read_override_720a0(uVar1);
    uVar2 = 1;
  }
  uVar2 = complete_nvm_single_operation_and_clear_suboperation_7243c(uVar2);
  return uVar2;
}

undefined4 invoke_nvm_buffer_callback_then_finish_buffer_read_727b2(void)

{
  ((void)(nvm_scheduler_operation.logical_handle), (void)(DAT_febf6118), return_const_1_745c0());
  return finish_nvm_buffer_read_after_mode_callback_7275e();
}

undefined4 begin_nvm_buffer_read_after_gate_727d2(void)

{
  ushort logical_handle;
  void *pvVar1;
  int iVar2;
  undefined4 uVar3;
  
  pvVar1 = ((void *)camry_host_ptr((uint32_t)(nvm_scheduler_operation.buffer_08)));
  logical_handle = nvm_scheduler_operation.logical_handle;
  begin_nvm_batch_item_event_and_mark_categories_71f28(nvm_scheduler_operation.logical_handle,nvm_scheduler_operation.operation);
  iVar2 = sample_nvm_gate_and_set_wait_count_72418();
  if (iVar2 == 0) {
    set_nvm_read_buffer_wrapper_72074(logical_handle,pvVar1);
    DAT_febf6118 = nvm_read_buffer(logical_handle);
    uVar3 = invoke_nvm_buffer_callback_then_finish_buffer_read_727b2();
  }
  else {
    uVar3 = 2;
    DAT_febf6114 = 0x3f721401;
  }
  return uVar3;
}

undefined4 thunk_finish_nvm_buffer_read_after_mode_callback_7275e(void)

{
  return finish_nvm_buffer_read_after_mode_callback_7275e();
}

undefined4 find_next_nvm_descriptor_with_flag_mask_7282c(uint param_1,ushort param_2,undefined2 *param_3)

{
  uint uVar1;
  
  while( true ) {
    uVar1 = param_1 & 0xffff;
    if ((ushort)(nvm_logical_descriptor_count - 1) < uVar1) {
      return 1;
    }
    if (param_2 == ((*((volatile uint16_t *)camry_host_ptr((uint32_t)((uint32_t)(0x26c0cu + (uint32_t)(uVar1) * (uint32_t)sizeof(F33NvmLogicalDescriptor)) + (uint32_t)(0) * (uint32_t)sizeof(F33NvmLogicalDescriptor) + (uint32_t)offsetof(F33NvmLogicalDescriptor, opaque_0a))))) & param_2)) break;
    param_1 = uVar1 + 1;
  }
  *param_3 = (short)param_1;
  return 0;
}

undefined4 check_nvm_callback_status_77_7285c(undefined2 param_1)

{
  int iVar1;
  undefined4 uVar2;
  char cStack_9;
  
  uVar2 = 0;
  iVar1 = ((void)(param_1), (void)(&cStack_9), return_const_1_71cf4());
  if ((iVar1 == 0) && (cStack_9 == 'w')) {
    accumulate_nvm_diagnostic_mask_by_category_7211a(5);
    uVar2 = 1;
  }
  return uVar2;
}

void accumulate_nvm_batch_failure_flag_72888(char param_1)

{
  if ((param_1 != '\0') && (param_1 != '\x04')) {
    DAT_febf6120 = 1;
  }
  return;
}

undefined4 complete_nvm_batch_and_reset_cursor_7289e(undefined1 param_1)

{
  complete_nvm_zero_handle_operation_unless_status16_73024(nvm_scheduler_operation.operation,param_1);
  DAT_febf6122 = 0xffff;
  DAT_febf6120 = 0;
  DAT_febf6114 = 0x9da70ae7;
  return 1;
}

undefined4 select_next_nvm_flag100_batch_item_728d2(undefined2 param_1)

{
  int iVar1;
  undefined4 uVar2;
  undefined2 uStack_a;
  
  iVar1 = find_next_nvm_descriptor_with_flag_mask_7282c(param_1,0x100,&uStack_a);
  if (iVar1 == 0) {
    uVar2 = 2;
    DAT_febf6122 = uStack_a;
    begin_nvm_batch_item_event_and_mark_categories_71f28(uStack_a,nvm_scheduler_operation.operation);
    DAT_febf6114 = 0x3f721401;
  }
  else {
    uVar2 = complete_nvm_batch_and_reset_cursor_7289e(DAT_febf6120);
  }
  return uVar2;
}

undefined4 publish_nvm_batch_item_result_and_advance_72920(ushort param_1,undefined1 param_2)

{
  accumulate_nvm_batch_failure_flag_72888(param_2);
  nvm_publish_logical_result(param_1,nvm_scheduler_operation.operation,param_2);
  finish_nvm_batch_item_event_and_notify_categories_71f82(param_1,nvm_scheduler_operation.operation);
  return select_next_nvm_flag100_batch_item_728d2(param_1 + 1);
}

undefined4 submit_nvm_batch_read_or_advance_failure_72958(void)

{
  ushort logical_handle;
  undefined4 uVar1;
  int iVar2;
  uint uVar3;
  F33NvmOperation local_18;
  
  logical_handle = DAT_febf6122;
  iVar2 = check_nvm_callback_status_77_7285c(DAT_febf6122);
  if (iVar2 == 1) {
    uVar1 = 4;
  }
  else {
    set_nvm_read_buffer_wrapper_71fe4(logical_handle,(void *)camry_host_ptr(0));
    DAT_febf6118 = nvm_read_buffer(logical_handle);
    local_18.buffer_0c = 0;
    local_18.logical_handle = logical_handle;
    local_18.operation = 1;
    local_18.buffer_08 = DAT_febf6118;
    uVar3 = nvm_submit_operation(camry_host_addr(&local_18));
    if (uVar3 == 0) {
      DAT_febf6114 = 0xa1a62093;
      return 4;
    }
    call_nvm_status_stub_zero_without_read_override_72010(logical_handle);
    uVar1 = 1;
  }
  uVar1 = publish_nvm_batch_item_result_and_advance_72920(logical_handle,uVar1);
  return uVar1;
}

undefined4 retry_nvm_batch_read_after_gate_729c2(void)

{
  int iVar1;
  undefined4 uVar2;
  
  iVar1 = sample_nvm_gate_and_set_wait_count_72418();
  if (iVar1 == 0) {
    uVar2 = submit_nvm_batch_read_or_advance_failure_72958();
  }
  else {
    uVar2 = 2;
    DAT_febf6114 = 0x3f721401;
  }
  return uVar2;
}

void begin_nvm_flag100_read_batch_729e8(void)

{
  ushort uVar1;
  bool bVar2;
  short sVar3;
  int iVar4;
  ushort uVar5;
  ushort uVar6;
  ushort uStack_1e;
  
  sVar3 = 2;
  uVar5 = 2;
  bVar2 = false;
  DAT_febf6120 = 0;
  uVar6 = 2;
  uVar1 = nvm_logical_descriptor_count - 1;
  while ((uVar6 <= uVar1 && (iVar4 = find_next_nvm_descriptor_with_flag_mask_7282c(sVar3,0x100,&uStack_1e), iVar4 == 0))) {
    nvm_publish_logical_result(uStack_1e,nvm_scheduler_operation.operation,'\x02');
    if (!bVar2) {
      bVar2 = true;
      uVar5 = uStack_1e;
    }
    uVar6 = uVar6 + 1;
    sVar3 = uStack_1e + 1;
  }
  if (bVar2) {
    DAT_febf6122 = uVar5;
    begin_nvm_batch_item_event_and_mark_categories_71f28(uVar5,nvm_scheduler_operation.operation);
    retry_nvm_batch_read_after_gate_729c2();
  }
  else {
    complete_nvm_batch_and_reset_cursor_7289e(DAT_febf6120);
  }
  return;
}

undefined4 thunk_retry_nvm_batch_read_after_gate_729c2(void)

{
  return retry_nvm_batch_read_after_gate_729c2();
}

undefined4 finish_nvm_batch_read_after_mode_callback_72a76(undefined2 param_1,undefined1 param_2)

{
  int iVar1;
  undefined4 uVar2;
  
  iVar1 = nvm_acquire_mode_four_read_buffer_or_retry_7465a((uint)(ushort)param_1);
  if (iVar1 == 0) {
    dispatch_nvm_read_status_zero_or_eight_7250e(param_1,param_2);
  }
  else {
    if (iVar1 != 1) {
      if (iVar1 != 2) {
        return 2;
      }
      DAT_febf6114 = 0x22aa8a36;
      return 2;
    }
    set_nvm_category_state_two_72108(4);
    accumulate_nvm_diagnostic_mask_by_category_7211a(1);
    call_nvm_status_stub_zero_without_read_override_72010(param_1);
    param_2 = 1;
  }
  uVar2 = publish_nvm_batch_item_result_and_advance_72920(param_1,param_2);
  return uVar2;
}

undefined4 finish_nvm_batch_read_after_buffer_callback_72ad4(undefined2 param_1,undefined1 param_2)

{
  int iVar1;
  
  iVar1 = ((void)(param_1), (void)(DAT_febf6118), return_const_1_745c0());
  if (iVar1 == 0) {
    DAT_febf6125 = 8;
    return finish_nvm_batch_read_after_mode_callback_72a76((uint)(ushort)param_1, 0x8);
  }
  return publish_nvm_batch_item_result_and_advance_72920(param_1,param_2);
}

undefined4 process_nvm_batch_read_result_72b0c(void)

{
  uint32_t puVar1;
  int iVar2;
  undefined4 uVar3;
  uint uVar4;
  
  puVar1 = 0x23dfcu;
  uVar4 = (uint)DAT_febf6122;
  iVar2 = nvm_get_operation_state_u8_73c6c();
  DAT_febf6125 = (undefined1)iVar2;
  if (iVar2 == 0) {
    if (((*((ushort *)camry_host_ptr((uint32_t)(puVar1 + uVar4 * 0x10 + 0x2e1a)))) >> 0xb & 1) != 0) {
      set_nvm_logical_write_inhibit_71ce2(uVar4,1);
    }
    uVar3 = finish_nvm_batch_read_after_mode_callback_72a76(uVar4,0);
  }
  else {
    uVar3 = 2;
    if ((iVar2 == 1) || (iVar2 == 3)) {
      uVar3 = finish_nvm_batch_read_after_buffer_callback_72ad4(uVar4, iVar2);
    }
    else if (iVar2 == 5) {
      ((void)(5), call_nvm_status_stub_zero_without_read_override_72010(uVar4));
      uVar3 = publish_nvm_batch_item_result_and_advance_72920(uVar4,5);
    }
  }
  return uVar3;
}

undefined4 resume_nvm_batch_read_with_saved_result_72b76(void)

{
  return finish_nvm_batch_read_after_mode_callback_72a76(DAT_febf6122,DAT_febf6125);
}

undefined4 abort_nvm_single_operation_with_diagnostic_72bae(undefined1 param_1,undefined1 param_2)

{
  uint uVar1;
  ushort uVar2;
  
  uVar2 = nvm_scheduler_operation.logical_handle;
  uVar1 = nvm_scheduler_operation.operation;
  ((void)(0), return_only_stub_73c86());
  accumulate_nvm_diagnostic_mask_by_category_7211a(param_2);
  if ((uVar1 == 0xa1a62093) || (uVar1 == 0xb6e96af1)) {
    call_nvm_status_stub_zero_without_read_override_72010(uVar2);
  }
  else if ((uVar1 == 0x22aa8a36) || (uVar1 == 0x1c646989)) {
    call_nvm_status_stub_zero_without_write_override_72058(uVar2);
  }
  else if ((uVar1 == 0xb9145954) || (uVar1 == 0x9c1f8709)) {
    call_nvm_status_stub_zero_without_read_override_720a0(uVar2);
  }
  return complete_nvm_single_operation_and_clear_suboperation_7243c(param_1);
}

undefined4 abort_nvm_single_with_status16_diagnostic8_72c2c(void)

{
  return abort_nvm_single_operation_with_diagnostic_72bae(0x16,8);
}

undefined4 abort_nvm_single_with_status26_diagnostic0_72c3e(void)

{
  return abort_nvm_single_operation_with_diagnostic_72bae(0x26,0);
}

undefined4 abort_nvm_single_with_status36_diagnostic6_72c50(void)

{
  return abort_nvm_single_operation_with_diagnostic_72bae(0x36,6);
}

void publish_nvm_result_to_remaining_masked_descriptors_72c62(uint param_1,ushort param_2,uint param_3,uchar param_4,undefined1 param_5)

{
  ushort uVar1;
  undefined8 uVar2;
  uint uVar3;
  
  uVar2 = 0x23dfc00000000;
  uVar1 = nvm_logical_descriptor_count - 1;
  while( true ) {
    uVar3 = param_1 & 0xffff;
    if (uVar1 < uVar3) break;
    if (param_2 == ((*((ushort *)camry_host_ptr((uint32_t)(uVar3 * 0x10 + (int)((ulonglong)uVar2 >> 0x20) + 0x2e1a)))) & param_2))
    {
      begin_nvm_batch_item_event_and_mark_categories_71f28(uVar3,param_3);
      accumulate_nvm_diagnostic_mask_by_category_7211a(param_5);
      nvm_publish_logical_result((ushort)param_1,param_3,param_4);
      finish_nvm_batch_item_event_and_notify_categories_71f82(uVar3,param_3);
    }
    param_1 = uVar3 + 1;
  }
  return;
}

undefined4 abort_nvm_batch_and_optionally_publish_remaining_72cba(undefined2 param_1,uint param_2,undefined1 param_3,uchar param_4,
                 undefined1 param_5,char param_6)

{
  ushort logical_handle;
  
  logical_handle = DAT_febf6122;
  ((void)(0), return_only_stub_73c86());
  accumulate_nvm_diagnostic_mask_by_category_7211a(param_5);
  if (param_2 == 0x2ece2284) {
    call_nvm_status_stub_zero_without_read_override_72010(logical_handle);
  }
  else if (param_2 == 0xea907101) {
    call_nvm_status_stub_zero_without_write_override_72058(logical_handle);
  }
  if (param_6 == '\x01') {
    nvm_publish_logical_result(logical_handle,param_2,param_4);
  }
  finish_nvm_batch_item_event_and_notify_categories_71f82(logical_handle,param_2);
  if (param_6 == '\x01') {
    publish_nvm_result_to_remaining_masked_descriptors_72c62(logical_handle + 1,param_1,param_2,param_4,param_5);
  }
  return complete_nvm_batch_and_reset_cursor_7289e(param_3);
}

undefined4 abort_nvm_flag100_batch_status16_diagnostic8_72d48(void)

{
  return abort_nvm_batch_and_optionally_publish_remaining_72cba(0x100,nvm_scheduler_operation.operation,0x16,6,8,1);
}

undefined4 abort_nvm_flag100_batch_status26_diagnostic0_72d70(void)

{
  return abort_nvm_batch_and_optionally_publish_remaining_72cba(0x100,nvm_scheduler_operation.operation,0x26,1,0,1);
}

undefined4 abort_nvm_flag100_batch_status36_diagnostic6_72d94(void)

{
  return abort_nvm_batch_and_optionally_publish_remaining_72cba(0x100,nvm_scheduler_operation.operation,0x36,6,6,1);
}

undefined4 abort_nvm_flag200_batch_status16_diagnostic8_72dba(void)

{
  return abort_nvm_batch_and_optionally_publish_remaining_72cba(0x200,nvm_scheduler_operation.operation,0x16,6,8,1);
}

undefined4 abort_nvm_flag200_batch_status26_diagnostic0_72de2(void)

{
  return abort_nvm_batch_and_optionally_publish_remaining_72cba(0x200,nvm_scheduler_operation.operation,0x26,1,0,1);
}

undefined4 abort_nvm_flag200_batch_status36_diagnostic6_72e06(void)

{
  return abort_nvm_batch_and_optionally_publish_remaining_72cba(0x200,nvm_scheduler_operation.operation,0x36,6,6,1);
}

void return_only_stub_72e2c(void)

{
  return;
}

uint enqueue_nvm_operation_and_publish_pending_result_72e2e(uint param_1,ushort param_2,void *param_3,void *param_4)

{
  uint uVar1;
  F33NvmOperation local_20;
  
  local_20.operation = param_1;
  local_20.logical_handle = param_2;
  local_20.buffer_08 = camry_host_addr(param_3);
  local_20.buffer_0c = camry_host_addr(param_4);
  set_nvm_category_three_state_one_720d6();
  if (param_2 == 0) {
    uVar1 = store_nvm_zero_handle_operation_if_empty_739a8(&local_20);
  }
  else {
    uVar1 = nvm_enqueue_pooled_operation(&local_20);
  }
  notify_nvm_category_three_720e2();
  if (uVar1 == 0) {
    nvm_publish_logical_result(param_2,param_1,'\x02');
  }
  return uVar1;
}

void load_next_nvm_operation_into_scheduler_72e70(void)

{
  int iVar1;
  uint local_14[4];
  
  iVar1 = peek_nvm_queued_operation_with_opcode_validation_7347e((int *)local_14);
  if ((iVar1 == 0) || (iVar1 = snapshot_nvm_zero_handle_operation_if_present_73978(local_14), iVar1 == 0)) {
    accept_nvm_scheduler_operation_if_idle_7220e(local_14);
    set_shared_countdown_from_second_argument_747c8(0,5);
    begin_nvm_operation_event_and_mark_categories_71e26((short)(local_14[1] & 0xffff),local_14[0]);
  }
  else {
    scan_five_nvm_pending_results_for_fault_71d3e();
  }
  return;
}

bool has_reserved_nvm_head_for_nonreserved_operation_72eac(uint *param_1)

{
  int iVar1;
  uint uVar2;
  bool bVar3;
  undefined1 auStack_1c [16];
  
  bVar3 = false;
  iVar1 = peek_nvm_reserved_queue_operation_73516(auStack_1c);
  if (iVar1 == 0) {
    uVar2 = nvm_uses_reserved_queue((ushort)param_1[1],*param_1);
    bVar3 = uVar2 != 1;
  }
  return bVar3;
}

void request_nvm_preemption_for_reserved_queue_head_72ed4(undefined4 param_1)

{
  int iVar1;
  
  iVar1 = has_reserved_nvm_head_for_nonreserved_operation_72eac(((uint *)camry_host_ptr((uint32_t)(param_1))));
  if (iVar1 == 1) {
    cancel_nvm_operation_and_select_scheduler_phase_72248(0);
  }
  return;
}

void nvm_service_scheduler(void)

{
  camry_write32((camry_sp - 4u) & ~3u, camry_gpr[31]);
  camry_sp -= 20u;
  camry_gpr[3] = camry_sp;

  uint uVar1;
  int iVar2;

  
  uVar1 = (camry_gpr[6] = camry_sp, camry_gpr[31] = 0x72ef4u, nvm_snapshot_scheduler_operation)(&(*((F33NvmOperation *)camry_host_ptr(camry_sp))));
  if (uVar1 == 0) {
    iVar2 = (camry_gpr[31] = 0x72efcu, nvm_map_operation_state_two_to_two_else_one_73c76)();
    if (iVar2 == 1) {
      (camry_gpr[31] = 0x72f04u, load_next_nvm_operation_into_scheduler_72e70)();
    }
    else {
      (camry_gpr[31] = 0x72f0au, record_nvm_integrity_fault_72130)();
    }
  }
  else if (uVar1 != 2) {
    (camry_gpr[6] = camry_sp, camry_gpr[31] = 0x72f16u, request_nvm_preemption_for_reserved_queue_head_72ed4)(camry_host_addr(&(*((F33NvmOperation *)camry_host_ptr(camry_sp)))));
  }
  (camry_gpr[31] = 0x72f1au, service_active_nvm_scheduler_operation_723d6)();
  { if (!camry_halted) { camry_gpr[31] = camry_read32((camry_sp + 16u) & ~3u); camry_sp += 20u; camry_gpr[3] = camry_sp; } return; }
}

bool is_nvm_handle_currently_scheduled_72f1e(ushort param_1)

{
  uint uVar1;
  F33NvmOperation FStack_1c;
  
  uVar1 = nvm_snapshot_scheduler_operation(&FStack_1c);
  return (uVar1 == 1 || uVar1 == 2) && FStack_1c.logical_handle == param_1;
}

undefined4 remove_unscheduled_nvm_handle_and_publish_six_72f44(undefined2 param_1)

{
  uint8_t stack_record_1c[28];
  int iVar1;
  undefined4 uVar2;
  
  uVar2 = 1;
  iVar1 = is_nvm_handle_currently_scheduled_72f1e((uint)(ushort)param_1);
  if ((iVar1 == 0) && (iVar1 = remove_nvm_handle_and_recycle_queue_slot_738e2(param_1, camry_host_addr(((uint32_t *)(stack_record_1c)))), iVar1 == 0)) {
    nvm_publish_logical_result((*((uint16_t *)(stack_record_1c + 4))),(*((uint32_t *)(stack_record_1c + 0))),'\x06');
    uVar2 = 0;
  }
  return uVar2;
}

void select_nvm_cancellation_phase_wrapper_72f76(undefined1 param_1)

{
  cancel_nvm_operation_and_select_scheduler_phase_72248(param_1);
  return;
}

void reset_nvm_queues_preserving_scheduled_operation_72f84(void)

{
  uint uVar1;
  F33NvmOperation FStack_18;
  
  uVar1 = nvm_snapshot_scheduler_operation(&FStack_18);
  nvm_reset_notification_exclusion = 0xffff;
  if (uVar1 != 0) {
    nvm_reset_notification_exclusion = FStack_18.logical_handle;
  }
  nvm_reset_queues_notifying();
  if (uVar1 != 0) {
    if (FStack_18.logical_handle == 0) {
      store_nvm_zero_handle_operation_if_empty_739a8(&FStack_18);
    }
    else {
      nvm_enqueue_pooled_operation(&FStack_18);
    }
  }
  cancel_nvm_operation_and_select_scheduler_phase_72248(2);
  return;
}

char normalize_nvm_completion_status_72fc8(char param_1)

{
  if (param_1 != '&') {
    if (param_1 == '6') {
      param_1 = '\x06';
    }
    return param_1;
  }
  return '\x01';
}

void complete_nvm_queued_operation_unless_status16_72fde(undefined2 param_1,undefined4 param_2,char param_3)

{
  uint8_t stack_record_28[40];
  uint operation;
  uchar result;
  int iVar1;
  
  if ((param_3 != '\x16') && (iVar1 = pop_matching_nvm_head_and_recycle_slot_73784(param_1, param_2, camry_host_addr(((uint32_t *)(stack_record_28)))), iVar1 == 0)) {
    result = ((void)(operation = (*((uint32_t *)(stack_record_28 + 0)))), normalize_nvm_completion_status_72fc8(param_3));
    nvm_publish_logical_result((*((uint16_t *)(stack_record_28 + 4))),operation,result);
    finish_nvm_operation_event_and_notify_categories_71eb4(param_1,param_2);
  }
  ((void)(0), clear_shared_countdown_747d2());
  return;
}
