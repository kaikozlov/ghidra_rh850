#include "common.h"

undefined4 nvm_enqueue_buffered_operation_b9145954_checked_74040(undefined2 param_1,undefined4 param_2)

{
  int iVar1;
  undefined4 uVar2;
  
  uVar2 = 1;
  iVar1 = nvm_validate_buffered_operation_service_eight_74494((uint)(ushort)param_1, ((void *)camry_host_ptr((uint32_t)(param_2))));
  if (iVar1 == 0) {
    uVar2 = enqueue_nvm_operation_and_publish_pending_result_72e2e((int)0xb9145954, param_1, ((void *)camry_host_ptr((uint32_t)(param_2))), 0);
  }
  return uVar2;
}

undefined4 nvm_enqueue_operation_b6e96af1_checked_74074(undefined2 param_1)

{
  int iVar1;
  undefined4 uVar2;
  
  uVar2 = 1;
  iVar1 = nvm_validate_default_buffer_service_twenty_two_744de((uint)(ushort)param_1);
  if (iVar1 == 0) {
    uVar2 = enqueue_nvm_operation_and_publish_pending_result_72e2e((int)0xb6e96af1,param_1,0,0);
  }
  return uVar2;
}

undefined4 nvm_enqueue_operation_1c646989_checked_7409e(undefined2 param_1)

{
  int iVar1;
  undefined4 uVar2;
  
  uVar2 = 1;
  iVar1 = nvm_validate_write_allowed_service_twenty_three_7451e((uint)(ushort)param_1);
  if (iVar1 == 0) {
    uVar2 = enqueue_nvm_operation_and_publish_pending_result_72e2e(0x1c646989,param_1,0,0);
  }
  return uVar2;
}

undefined4 nvm_enqueue_operation_9c1f8709_checked_740c8(undefined2 param_1)

{
  int iVar1;
  undefined4 uVar2;
  
  uVar2 = 1;
  iVar1 = nvm_validate_default_buffer_service_twenty_four_74568((uint)(ushort)param_1);
  if (iVar1 == 0) {
    uVar2 = enqueue_nvm_operation_and_publish_pending_result_72e2e((int)0x9c1f8709,param_1,0,0);
  }
  return uVar2;
}

void nvm_enqueue_zero_handle_operation_2ece2284_740f2(void)

{
  int iVar1;
  
  iVar1 = return_const_0_745b8();
  if (iVar1 == 0) {
    enqueue_nvm_operation_and_publish_pending_result_72e2e(0x2ece2284,0,0,0);
  }
  return;
}

void nvm_service_application_cycle(void)

{
  uint uVar1;
  
  uVar1 = nvm_driver_gate_rejected(0x14);
  if ((uVar1 == 0) && (uVar1 = nvm_service_uninitialized(), uVar1 == 0)) {
    nvm_enter_service_guard();
    uVar1 = nvm_reconcile_probe_mode();
    if (uVar1 == 0) {
      nvm_select_service_poll('\0');
      nvm_service_scheduler();
      tick_shared_countdown_and_call_expiry_index_74790();
    }
    nvm_set_service_state_byte_cd9_79c42(uVar1 != 0);
    nvm_leave_service_guard();
  }
  return;
}

void thunk_reset_nvm_queues_preserving_scheduled_operation_72f84(void)

{
  reset_nvm_queues_preserving_scheduled_operation_72f84();
  return;
}

void nvm_service_logical_and_physical_driver(void)

{
  camry_write32((camry_sp - 4u) & ~3u, camry_gpr[31]);
  camry_sp -= 4u;
  camry_gpr[3] = camry_sp;

  uint uVar1;
  
  uVar1 = (camry_gpr[6] = 0x14u, camry_gpr[31] = 0x74170u, nvm_driver_gate_rejected)(0x14);
  if ((uVar1 == 0) && (uVar1 = (camry_gpr[31] = 0x74178u, nvm_service_uninitialized)(), uVar1 == 0)) {
    (camry_gpr[31] = 0x74180u, nvm_enter_service_guard)();
    uVar1 = (camry_gpr[31] = 0x74184u, nvm_reconcile_probe_mode)();
    if (uVar1 == 0) {
      (camry_gpr[6] = 1u, camry_gpr[31] = 0x7418eu, nvm_select_service_poll)('\x01');
      (camry_gpr[31] = 0x74192u, nvm_service_scheduler)();
    }
    (camry_gpr[6] = uVar1 != 0, camry_gpr[31] = 0x74198u, nvm_store_service_mode_nonzero)(uVar1 != 0);
    (camry_gpr[31] = 0x7419cu, nvm_leave_service_guard)();
  }
  { if (!camry_halted) { camry_gpr[31] = camry_read32((camry_sp + 0u) & ~3u); camry_sp += 4u; camry_gpr[3] = camry_sp; } return; }
}

undefined4 nvm_get_service_and_queue_status_741a0(void)

{
  int iVar1;
  uint uVar2;
  int iVar3;
  undefined4 uVar4;
  undefined1 auStack_1c [16];
  
  iVar3 = 0;
  iVar1 = validate_nvm_pool_counts_and_test_nonempty_73274();
  if (iVar1 == 0) {
    iVar3 = snapshot_nvm_zero_handle_operation_if_present_73978(auStack_1c);
  }
  uVar2 = nvm_service_uninitialized();
  if (uVar2 == 0) {
    if (iVar3 == 0) {
      uVar4 = 2;
    }
    else {
      uVar4 = 1;
    }
  }
  else {
    uVar4 = 4;
  }
  return uVar4;
}

void nvm_cancel_scheduler_operation_mode_zero_741d0(void)

{
  select_nvm_cancellation_phase_wrapper_72f76(0);
  return;
}

void nvm_cancel_physical_operation_wrapper_741de(void)

{
  nvm_cancel_physical_operation();
  return;
}

void return_only_stub_741ea(void)

{
  return;
}

uint nvm_check_logical_handle(ushort logical_handle,uchar api,uchar allow_zero)

{
  uint uVar1;
  
  uVar1 = 1;
  if (((logical_handle < 2) || ((ushort)(nvm_logical_descriptor_count - 1) < logical_handle)) &&
     ((allow_zero != '\x01' || (logical_handle != 0)))) {
    ((void)(0x14), (void)(0), (void)(api), (void)(10), return_const_0_71d88());
  }
  else {
    uVar1 = 0;
  }
  return uVar1;
}

bool nvm_is_invalid_boolean_u8_74228(char param_1)

{
  if (param_1 != '\x01') {
    return param_1 != '\0';
  }
  return false;
}

uint nvm_check_not_pending(ushort logical_handle,uchar api)

{
  bool bVar1;
  uchar uStack_d;
  
  uStack_d = '\x02';
  nvm_read_logical_result(logical_handle,&uStack_d);
  bVar1 = uStack_d == '\x02';
  if (bVar1) {
    ((void)(0x14), (void)(0), (void)(api), (void)(0x15), return_const_0_71d88());
  }
  return (uint)bVar1;
}

bool nvm_check_logical_option_bit_eleven_74274(uint param_1,undefined1 param_2)

{
  bool bVar1;
  
  bVar1 = ((ushort)(*((volatile uint16_t *)camry_host_ptr((uint32_t)((uint32_t)(0x26c0cu + (uint32_t)(param_1 & 0xffff) * (uint32_t)sizeof(F33NvmLogicalDescriptor)) + (uint32_t)(0) * (uint32_t)sizeof(F33NvmLogicalDescriptor) + (uint32_t)offsetof(F33NvmLogicalDescriptor, opaque_0a))))) >> 0xb & 1) != 0;
  if (bVar1) {
    ((void)(0x14), (void)(0), (void)(param_2), (void)(0x18), return_const_0_71d88());
  }
  return bVar1;
}

undefined4 nvm_validate_write_inhibit_update_742a2(ushort param_1,undefined1 param_2)

{
  uint uVar1;
  int iVar2;
  undefined4 uVar3;
  
  uVar3 = 1;
  uVar1 = nvm_check_logical_handle(param_1,'\x03','\0');
  iVar2 = nvm_is_invalid_boolean_u8_74228(param_2);
  if ((uVar1 == 0) && (iVar2 == 0)) {
    uVar1 = nvm_check_not_pending(param_1,'\x03');
    iVar2 = nvm_check_logical_option_bit_eleven_74274(param_1,3);
    if (uVar1 == 0) {
      if (iVar2 == 0) {
        uVar3 = 0;
      }
      else {
        uVar3 = 1;
      }
    }
  }
  return uVar3;
}

bool nvm_check_null_pointer_error_fourteen_742ea(int param_1,undefined1 param_2)

{
  if (param_1 == 0) {
    ((void)(0x14), (void)(0), (void)(param_2), (void)(0xe), return_const_0_71d88());
  }
  return param_1 == 0;
}

undefined4 nvm_validate_logical_result_output_7430c(ushort param_1,undefined4 param_2)

{
  uint uVar1;
  int iVar2;
  undefined4 uVar3;
  
  uVar3 = 1;
  uVar1 = nvm_check_logical_handle(param_1,'\x04','\x01');
  iVar2 = nvm_check_null_pointer_error_fourteen_742ea(param_2,4);
  if (uVar1 == 0) {
    if (iVar2 == 0) {
      uVar3 = 0;
    }
    else {
      uVar3 = 1;
    }
  }
  return uVar3;
}

bool nvm_check_null_pointer_error_fifteen_74338(int param_1,undefined1 param_2)

{
  if (param_1 == 0) {
    ((void)(0x14), (void)(0), (void)(param_2), (void)(0xf), return_const_0_71d88());
  }
  return param_1 == 0;
}

bool nvm_validate_configuration_output_pointer_7435a(undefined4 param_1)

{
  int iVar1;
  
  iVar1 = nvm_check_null_pointer_error_fifteen_74338(param_1,0xf);
  return iVar1 != 0;
}

bool nvm_validate_queue_removal_handle_7436e(ushort param_1)

{
  uint uVar1;
  
  uVar1 = nvm_check_logical_handle(param_1,'\x10','\0');
  return uVar1 != 0;
}

uint nvm_check_buffer_argument(ushort logical_handle,void *buffer,uchar api)

{
  uint uVar1;
  
  uVar1 = 0;
  if (((camry_host_addr((buffer))== 0) &&
      ((*((volatile uint8_t *)camry_host_ptr((uint32_t)((uint32_t)(0x26c0cu + (uint32_t)(logical_handle) * (uint32_t)sizeof(F33NvmLogicalDescriptor)) + (uint32_t)(0) * (uint32_t)sizeof(F33NvmLogicalDescriptor) + (uint32_t)offsetof(F33NvmLogicalDescriptor, buffer_mode))))) != '\x04')) &&
     ((*((volatile uint8_t *)camry_host_ptr((uint32_t)((uint32_t)(0x26c0cu + (uint32_t)(logical_handle) * (uint32_t)sizeof(F33NvmLogicalDescriptor)) + (uint32_t)(0) * (uint32_t)sizeof(F33NvmLogicalDescriptor) + (uint32_t)offsetof(F33NvmLogicalDescriptor, buffer_mode))))) != '\x02')) {
    ((void)(0x14), (void)(0), (void)(api), (void)(0xd), return_const_0_71d88());
    uVar1 = 1;
  }
  return uVar1;
}

uint nvm_check_read_request(ushort logical_handle,void *buffer)

{
  uint uVar1;
  uint uVar2;
  uint uVar3;
  
  uVar3 = 1;
  uVar1 = nvm_check_logical_handle(logical_handle,'\x06','\0');
  if (uVar1 == 0) {
    uVar1 = nvm_check_not_pending(logical_handle,'\x06');
    uVar2 = nvm_check_buffer_argument(logical_handle,buffer,'\x06');
    if (uVar1 == 0) {
      if (uVar2 == 0) {
        uVar3 = 0;
      }
      else {
        uVar3 = 1;
      }
    }
  }
  return uVar3;
}

uint nvm_check_write_inhibit(ushort logical_handle)

{
  uint uVar1;
  
  set_nvm_category_six_state_one_720bc();
  uVar1 = nvm_get_write_inhibit(logical_handle);
  if (uVar1 == 1) {
    set_nvm_category_state_two_72108(6);
  }
  notify_nvm_category_six_720c8();
  return (uint)(uVar1 == 1);
}

uint nvm_check_write_request(ushort logical_handle,void *buffer)

{
  uint uVar1;
  uint uVar2;
  uint uVar3;
  
  uVar3 = 1;
  uVar1 = nvm_check_logical_handle(logical_handle,'\a','\0');
  if (uVar1 == 0) {
    uVar1 = nvm_check_not_pending(logical_handle,'\a');
    uVar2 = nvm_check_buffer_argument(logical_handle,buffer,'\a');
    if ((uVar1 == 0) && (uVar2 == 0)) {
      uVar3 = nvm_check_write_inhibit(logical_handle);
      if (uVar3 == 0) {
        uVar3 = 0;
      }
      else {
        uVar3 = 1;
      }
    }
  }
  return uVar3;
}

bool nvm_check_zero_permission_gate_74468(undefined2 param_1,undefined1 param_2)

{
  int iVar1;
  
  iVar1 = ((void)(param_1), return_const_0_745c4());
  if (iVar1 == 0) {
    ((void)(0x14), (void)(0), (void)(param_2), (void)(0x18), return_const_0_71d88());
  }
  return iVar1 == 0;
}

undefined4 nvm_validate_buffered_operation_service_eight_74494(ushort param_1,void *param_2)

{
  uint uVar1;
  int iVar2;
  uint uVar3;
  undefined4 uVar4;
  
  uVar4 = 1;
  uVar1 = nvm_check_logical_handle(param_1,'\b','\0');
  if (uVar1 == 0) {
    uVar1 = nvm_check_not_pending(param_1,'\b');
    iVar2 = nvm_check_zero_permission_gate_74468(param_1,8);
    uVar3 = nvm_check_buffer_argument(param_1,param_2,'\b');
    if ((uVar1 == 0) && (iVar2 == 0)) {
      if (uVar3 == 0) {
        uVar4 = 0;
      }
      else {
        uVar4 = 1;
      }
    }
  }
  return uVar4;
}

undefined4 nvm_validate_default_buffer_service_twenty_two_744de(ushort param_1)

{
  uint uVar1;
  uint uVar2;
  undefined4 uVar3;
  
  uVar3 = 1;
  uVar1 = nvm_check_logical_handle(param_1,'\x16','\0');
  if (uVar1 == 0) {
    uVar1 = nvm_check_not_pending(param_1,'\x16');
    uVar2 = nvm_check_buffer_argument(param_1,(void *)0x0,'\x16');
    if (uVar1 == 0) {
      if (uVar2 == 0) {
        uVar3 = 0;
      }
      else {
        uVar3 = 1;
      }
    }
  }
  return uVar3;
}

undefined4 nvm_validate_write_allowed_service_twenty_three_7451e(ushort param_1)

{
  uint uVar1;
  uint uVar2;
  undefined4 uVar3;
  
  uVar3 = 1;
  uVar1 = nvm_check_logical_handle(param_1,'\x17','\0');
  if (uVar1 == 0) {
    uVar1 = nvm_check_not_pending(param_1,'\x17');
    uVar2 = nvm_check_buffer_argument(param_1,(void *)0x0,'\x17');
    if ((uVar1 == 0) && (uVar2 == 0)) {
      uVar1 = nvm_check_write_inhibit(param_1);
      if (uVar1 == 0) {
        uVar3 = 0;
      }
      else {
        uVar3 = 1;
      }
    }
  }
  return uVar3;
}

undefined4 nvm_validate_default_buffer_service_twenty_four_74568(ushort param_1)

{
  uint uVar1;
  int iVar2;
  uint uVar3;
  undefined4 uVar4;
  
  uVar4 = 1;
  uVar1 = nvm_check_logical_handle(param_1,'\x18','\0');
  if (uVar1 == 0) {
    uVar1 = nvm_check_not_pending(param_1,'\x18');
    iVar2 = nvm_check_zero_permission_gate_74468(param_1,0x18);
    uVar3 = nvm_check_buffer_argument(param_1,(void *)0x0,'\x18');
    if ((uVar1 == 0) && (iVar2 == 0)) {
      if (uVar3 == 0) {
        uVar4 = 0;
      }
      else {
        uVar4 = 1;
      }
    }
  }
  return uVar4;
}

undefined4 return_const_0_745b8(void)

{
  return 0;
}

void return_only_stub_745bc(void)

{
  return;
}

void return_only_stub_745be(void)

{
  return;
}

undefined4 return_const_1_745c0(void)

{
  return 1;
}

undefined4 return_const_0_745c4(void)

{
  return 0;
}

void nvm_clear_buffer_overrides_745c8(void)

{
  nvm_read_buffer_override = 0;
  nvm_write_buffer_override = 0;
  return;
}

void nvm_reset_buffer_retry(void)

{
  nvm_buffer_retry = '\0';
  return;
}

undefined4 nvm_advance_buffer_retry_or_fail_7463e(void)

{
  if (nvm_buffer_retry < DAT_00026bf4) {
    nvm_buffer_retry = nvm_buffer_retry + '\x01';
    return 2;
  }
  return 1;
}

undefined4 nvm_acquire_mode_four_read_buffer_or_retry_7465a(uint param_1)

{
  int iVar1;
  undefined4 uVar2;
  
  param_1 = param_1 & 0xffff;
  uVar2 = 0;
  if ((nvm_read_buffer_override == 0) &&
     ((*((volatile uint8_t *)camry_host_ptr((uint32_t)((uint32_t)(0x26c0cu + (uint32_t)(param_1) * (uint32_t)sizeof(F33NvmLogicalDescriptor)) + (uint32_t)(0) * (uint32_t)sizeof(F33NvmLogicalDescriptor) + (uint32_t)offsetof(F33NvmLogicalDescriptor, buffer_mode))))) == '\x04')) {
    change_nvm_category_state_four_to_one_720f0(4);
    iVar1 = ((void)(((undefined *)camry_host_ptr(0xfebf6b10u))), dispatch_nvm_callback_from_26c00_7216c(param_1));
    if (iVar1 == 0) {
      ((void)(param_1), (void)(0), return_only_stub_71ce0());
    }
    else {
      uVar2 = nvm_advance_buffer_retry_or_fail_7463e();
    }
  }
  return uVar2;
}

undefined4 nvm_acquire_mode_four_write_buffer_or_retry_74708(uint param_1)

{
  int iVar1;
  undefined4 uVar2;
  
  param_1 = param_1 & 0xffff;
  uVar2 = 0;
  if ((nvm_write_buffer_override == 0) &&
     ((*((volatile uint8_t *)camry_host_ptr((uint32_t)((uint32_t)(0x26c0cu + (uint32_t)(param_1) * (uint32_t)sizeof(F33NvmLogicalDescriptor)) + (uint32_t)(0) * (uint32_t)sizeof(F33NvmLogicalDescriptor) + (uint32_t)offsetof(F33NvmLogicalDescriptor, buffer_mode))))) == '\x04')) {
    change_nvm_category_state_four_to_one_720f0(4);
    iVar1 = ((void)(((undefined *)camry_host_ptr(0xfebf6b10u))), dispatch_nvm_callback_from_26c04_7215a(param_1));
    if (iVar1 == 0) {
      ((void)(param_1), (void)(0x77), return_only_stub_71ce0());
    }
    else {
      uVar2 = nvm_advance_buffer_retry_or_fail_7463e();
    }
  }
  return uVar2;
}

bool nvm_has_read_buffer_override_7475a(void)

{
  return nvm_read_buffer_override != 0;
}

bool nvm_has_write_buffer_override_7476a(void)

{
  return nvm_write_buffer_override != 0;
}

void clear_shared_countdown_if_configured_7477a(void)

{
  uint uVar1;
  
  for (uVar1 = (uint)DAT_00027624; uVar1 != 0; uVar1 = uVar1 - 1) {
    DAT_febf6b18 = 0;
  }
  return;
}

void tick_shared_countdown_and_call_expiry_index_74790(void)

{
  int iVar1;
  ushort uVar2;
  undefined8 uVar3;
  ushort uVar4;
  
  uVar2 = DAT_00027624;
  uVar3 = 0x23dfc00000000;
  for (uVar4 = 0; uVar4 < uVar2; uVar4 = uVar4 + 1) {
    iVar1 = DAT_febf6b18;
    if ((DAT_febf6b18 != 0) && (iVar1 = DAT_febf6b18 + -1, DAT_febf6b18 == 1)) {
      (*(int (*)())camry_indirect((uint32_t)(((((code *)(uintptr_t)((uint32_t)((uintptr_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)((int)((ulonglong)uVar3 >> 0x20) + 0x382c)))))))))))))(uVar4);
    }
    DAT_febf6b18 = iVar1;
  }
  return;
}

void set_shared_countdown_from_second_argument_747c8(undefined4 param_1,undefined4 param_2)

{
  DAT_febf6b18 = param_2;
  return;
}

void clear_shared_countdown_747d2(void)

{
  DAT_febf6b18 = 0;
  return;
}

void return_only_stub_747dc(void)

{
  return;
}

void return_only_stub_747de(void)

{
  return;
}

void copy_bytes_forward(uchar *destination,uchar *source,uint byte_count)

{
  uint uVar1;
  
  for (uVar1 = 0; uVar1 < byte_count; uVar1 = uVar1 + 1) {
    destination[uVar1] = source[uVar1];
  }
  return;
}

undefined4 compare_unsigned_byte_ranges_7484a(int param_1,int param_2,uint param_3)

{
  uint uVar1;
  undefined4 uVar2;
  
  uVar1 = 0;
  while( true ) {
    if (param_3 <= uVar1) {
      return 0;
    }
    if ((*((byte *)camry_host_ptr((uint32_t)(uVar1 + param_1)))) != (*((byte *)camry_host_ptr((uint32_t)(uVar1 + param_2))))) break;
    uVar1 = uVar1 + 1;
  }
  if ((*((byte *)camry_host_ptr((uint32_t)(uVar1 + param_1)))) < (*((byte *)camry_host_ptr((uint32_t)(uVar1 + param_2))))) {
    uVar2 = 0xffffffff;
  }
  else {
    uVar2 = 1;
  }
  return uVar2;
}

void fill_byte_range_74872(int param_1,undefined1 param_2,uint param_3)

{
  uint uVar1;
  
  for (uVar1 = 0; uVar1 < param_3; uVar1 = uVar1 + 1) {
    (*((undefined1 *)camry_host_ptr((uint32_t)(uVar1 + param_1)))) = param_2;
  }
  return;
}

uint nvm_descriptor_option(ushort handle)

{
  return (uint)(*((volatile uint8_t *)camry_host_ptr((uint32_t)((uint32_t)(0x27634u + (uint32_t)(handle) * (uint32_t)sizeof(F33NvmDescriptor)) + (uint32_t)(0) * (uint32_t)sizeof(F33NvmDescriptor) + (uint32_t)offsetof(F33NvmDescriptor, option)))));
}

undefined * nvm_translate_driver_completion_state_74960(void)

{
  undefined *puVar1;
  
  if (DAT_febf6b20 != 0) {
    if (DAT_febf6b20 == 1) {
      return ((undefined *)camry_host_ptr((uint32_t)(0x1)));
    }
    if (DAT_febf6b20 < 3) {
      puVar1 = ((undefined *)camry_host_ptr((uint32_t)(nvm_translate_saved_driver_result())));
      return puVar1;
    }
    if (DAT_febf6b20 == 3) {
      return ((undefined *)camry_host_ptr(0xfffau));
    }
    if (DAT_febf6b20 < 6) {
      return ((undefined *)camry_host_ptr(0xfffbu));
    }
    if (DAT_febf6b20 == 0x11) {
      return ((undefined *)camry_host_ptr((uint32_t)(0xffff)));
    }
    if (DAT_febf6b20 == 0xff) {
      return (undefined *)0x0;
    }
  }
  return ((undefined *)camry_host_ptr((uint32_t)(0xffffffff)));
}

void nvm_reset_driver_completion_bytes_749ae(void)

{
  DAT_febf6b20 = 0xff;
  DAT_febf6b21 = 0xff;
  return;
}

void nvm_set_driver_completion_state_u8_749bc(undefined1 param_1)

{
  DAT_febf6b20 = param_1;
  return;
}

void nvm_set_saved_driver_result_u8_749c6(undefined1 param_1)

{
  DAT_febf6b21 = param_1;
  return;
}

void nvm_reset_deferred_program_state_749d0(void)

{
  nvm_driver_phase = '\0';
  DAT_febf6b24 = 0;
  DAT_febf6b1c = 0;
  DAT_febf6b68 = 0xffffffff;
  DAT_febf6b6c = 0;
  return;
}

void nvm_reset_driver_timeout_and_deferred_state_749e4(void)

{
  DAT_febf6c34 = 0;
  nvm_reset_driver_completion_bytes_749ae();
  nvm_reset_deferred_program_state_749d0();
  return;
}

void nvm_reset_transfer_context_and_staging_buffer_749fc(void)

{
  DAT_febf6c5a = 0xff;
  DAT_febf6c59 = 0;
  DAT_febf6c30 = 0xffffffff;
  DAT_febf6c48 = 0;
  fill_byte_range_74872((int)((uint32_t)(0xfebf6bd0u)), 0, 0x40);
  return;
}

uint nvm_sync_access_blocked(void)

{
  int iVar1;
  uint uVar2;
  
  uVar2 = 1;
  if (nvm_driver_block_latch == '\0') {
    iVar1 = dataflash_get_job_result_78896();
    uVar2 = (uint)(iVar1 == 0x80);
  }
  return uVar2;
}

uint nvm_sync_admission_result(void)

{
  uint uVar1;
  uint32_t puVar2;
  
  uVar1 = nvm_sync_access_blocked();
  if (uVar1 == 1) {
    puVar2 = (uint32_t)((uint32_t)(0xffff0000));
  }
  else if (nvm_driver_phase == '\0') {
    puVar2 = (uint32_t)((uint32_t)(0x1));
  }
  else {
    puVar2 = (uint32_t)(0xfff9u);
  }
  return (uint)puVar2;
}

void nvm_set_driver_timeout_ticks_74a82(undefined4 param_1)

{
  DAT_febf6c34 = param_1;
  return;
}

uint nvm_submit_previous_erase_block(void)

{
  uint32_t puVar1;
  uint uVar2;
  int iVar3;
  
  puVar1 = 0x23dfcu;
  uVar2 = nvm_sync_admission_result();
  if (uVar2 == 1) {
    nvm_reset_driver_completion_bytes_749ae();
    DAT_febf6c30 = DAT_febf6c30 + -0x40;
    iVar3 = dataflash_start_sixty_four_byte_block_erase_7867a(DAT_febf6c30,0x40);
    if (iVar3 == 0) {
      nvm_set_driver_timeout_ticks_74a82((*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + 0x3b28)))));
      uVar2 = 2;
    }
    else {
      uVar2 = nvm_translate_saved_driver_result();
    }
  }
  return uVar2;
}

void nvm_complete_transfer_or_continue_reverse_erase_74aca(uint param_1)

{
  uint32_t puVar1;
  int extraout_r6;
  uint uVar2;
  
  puVar1 = 0x23dfcu;
  uVar2 = (uint)DAT_febf6c5a;
  nvm_reset_driver_timeout_and_deferred_state_749e4();
  if (uVar2 < 0xc) {
    if (DAT_febf6c59 == '\x01') {
      if ((((int)(param_1)) == 1) && (DAT_febf6c48 = DAT_febf6c48 + -1, DAT_febf6c48 != 0)) {
        param_1 = nvm_submit_previous_erase_block();
      }
      if (param_1 == 2) {
        return;
      }
    }
    nvm_reset_transfer_context_and_staging_buffer_749fc();
    (*(int (*)())camry_indirect((uint32_t)(((((code *)(uintptr_t)((uint32_t)((uintptr_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(puVar1 + uVar2 * 4 + 0x3be8))))))))))))(param_1);
  }
  return;
}

void nvm_dispatch_nonpending_driver_completion_74b20(void)

{
  int iVar1;
  
  iVar1 = camry_host_addr(nvm_translate_driver_completion_state_74960());
  if (iVar1 != 0) {
    nvm_complete_transfer_or_continue_reverse_erase_74aca(iVar1);
    nvm_set_suspend_policy_byte_781aa(0);
  }
  return;
}

uint nvm_initialize_driver_transfer_context_74b3c(void)

{
  uint32_t puVar1;
  uint uVar2;
  
  puVar1 = 0x23dfcu;
  nvm_driver_block_latch = '\0';
  nvm_reset_driver_timeout_and_deferred_state_749e4();
  nvm_reset_transfer_context_and_staging_buffer_749fc();
  ((void)(((undefined *)camry_host_ptr((uint32_t)(puVar1 + 0x3b34)))), dataflash_initialize_driver_and_clock_78500());
  uVar2 = nvm_translate_saved_driver_result();
  nvm_set_suspend_policy_byte_781aa(0);
  return uVar2;
}

uint thunk_nvm_initialize_driver_transfer_context_74b3c(void)

{
  return nvm_initialize_driver_transfer_context_74b3c();
}

uint nvm_start_reverse_erase(uint byte_offset,uint page_count,uint callback_selector)

{
  uint uVar1;
  
  DAT_febf6c30 = (page_count & 0xffff) * 0x40 + byte_offset;
  uVar1 = nvm_submit_previous_erase_block();
  if (uVar1 == 2) {
    DAT_febf6c59 = 1;
    DAT_febf6c5a = (undefined1)callback_selector;
    DAT_febf6c48 = (undefined2)page_count;
  }
  return uVar1;
}

int u16_bytes_to_word_count_74bb4(uint param_1)

{
  return (int)(param_1 & 0xffff) >> 2;
}

uint nvm_submit_program_and_set_scaled_timeout_74bbc(undefined4 param_1,undefined2 param_2, undefined4 param_3)

{
  uint32_t puVar1;
  int iVar2;
  uint uVar3;
  
  puVar1 = 0x23dfcu;
  nvm_reset_driver_completion_bytes_749ae();
  iVar2 = dataflash_start_buffered_word_program_78566(param_1, param_3, (uint)(ushort)param_2);
  if (iVar2 == 0) {
    iVar2 = u16_bytes_to_word_count_74bb4(param_2);
    nvm_set_driver_timeout_ticks_74a82((*((int *)camry_host_ptr((uint32_t)(0x3b20u + (int)(puVar1 + 4))))) * iVar2);
    uVar3 = 2;
  }
  else {
    uVar3 = nvm_translate_saved_driver_result();
  }
  return uVar3;
}

undefined4 nvm_schedule_deferred_program_retry_74bf2(void)

{
  if (DAT_febf6b24 < DAT_0002792d) {
    DAT_febf6b24 = DAT_febf6b24 + 1;
    DAT_febf6b1c = DAT_0002791c;
    nvm_driver_phase = 0xaa;
    return 2;
  }
  return 0xffff;
}

int nvm_stage_deferred_program_request_74c20(undefined4 param_1,ushort param_2)

{
  undefined4 extraout_r6;
  uchar *source;
  int iVar1;
  
  DAT_febf6b24 = 0;
  iVar1 = nvm_schedule_deferred_program_retry_74bf2();
  if (iVar1 == 2) {
    DAT_febf6b68 = param_1;
    DAT_febf6b6c = param_2;
    copy_bytes_forward(((undefined *)camry_host_ptr(0xfebf6b28u)),source,(uint)param_2);
  }
  return iVar1;
}

uint nvm_stage_and_submit_program_with_optional_deferral_74c54(undefined4 param_1,uint param_2,uchar *param_3,undefined1 param_4,char param_5)

{
  uint uVar1;
  int iVar2;
  
  param_2 = param_2 & 0xffff;
  uVar1 = nvm_sync_admission_result();
  if (uVar1 == 1) {
    copy_bytes_forward(((undefined *)camry_host_ptr(0xfebf6bd0u)),param_3,param_2);
    if (param_5 == '\x01') {
      iVar2 = thunk_return_false_via_zero_hook_79432();
      if (iVar2 == 0) {
        uVar1 = nvm_submit_program_and_set_scaled_timeout_74bbc(param_1, (uint)(ushort)param_2, (int)0xfebf6bd0);
        if (uVar1 == 2) {
          nvm_set_suspend_policy_byte_781aa(1);
          DAT_febf6c59 = 2;
          DAT_febf6c5a = param_4;
          return 2;
        }
        return uVar1;
      }
      uVar1 = ((void)(((undefined *)camry_host_ptr(0xfebf6bd0u))), nvm_stage_deferred_program_request_74c20(param_1, param_2));
    }
    else {
      uVar1 = nvm_submit_program_and_set_scaled_timeout_74bbc(param_1, param_2, (int)((uint32_t)(0xfebf6bd0u)));
    }
  }
  if (uVar1 == 2) {
    DAT_febf6c5a = param_4;
    DAT_febf6c59 = 2;
    return 2;
  }
  return uVar1;
}

undefined4 nvm_map_read_errors_to_block_actions_74cd2(char param_1)

{
  undefined4 uVar1;
  
  if (param_1 != '\t') {
    uVar1 = 0xff;
    if (param_1 == '\v') {
      uVar1 = 2;
    }
    return uVar1;
  }
  return 1;
}

void nvm_apply_driver_block_action_74ce8(char param_1)

{
  undefined4 uVar1;
  
  if (param_1 == '\x01') {
    uVar1 = 0;
    nvm_driver_block_latch = '\x01';
  }
  else {
    if (param_1 != '\x02') {
      return;
    }
    uVar1 = 1;
  }
  nvm_enable_guard_mask_for_index0_or1_76a8c(uVar1);
  return;
}

uint nvm_map_blank_check_result(uint byte_offset,ushort byte_count)

{
  uint uVar1;
  undefined4 uVar2;
  uint uVar3;
  
  uVar1 = dataflash_blank_check(byte_offset,(uint)byte_count);
  if (uVar1 == 2) {
    uVar3 = 3;
  }
  else {
    uVar3 = 4;
    if (uVar1 != 7) {
      uVar3 = nvm_translate_read_driver_result((uchar)uVar1);
      uVar2 = nvm_map_read_errors_to_block_actions_74cd2(uVar1);
      nvm_apply_driver_block_action_74ce8(uVar2);
    }
  }
  return uVar3;
}

uint nvm_read_words_and_translate_driver_result_74d40(uint param_1,uint param_2,uint *param_3)

{
  uint uVar1;
  undefined4 uVar2;
  uint uVar3;
  
  uVar1 = dataflash_read_words(param_1,param_3,param_2 & 0xffff);
  if ((uVar1 == 2) || (uVar1 == 5)) {
    uVar3 = 1;
  }
  else {
    uVar3 = nvm_translate_read_driver_result((uchar)uVar1);
    uVar2 = nvm_map_read_errors_to_block_actions_74cd2(uVar1);
    nvm_apply_driver_block_action_74ce8(uVar2);
  }
  return uVar3;
}

uint nvm_read_with_optional_blank_check
               (uint byte_offset,ushort byte_count,uchar *destination,uchar blank_option)

{
  uint uVar1;
  
  uVar1 = nvm_sync_admission_result();
  if (uVar1 == 1) {
    nvm_reset_driver_completion_bytes_749ae();
    if ((blank_option != '\x01') ||
       (uVar1 = nvm_map_blank_check_result(byte_offset,byte_count), uVar1 == 4)) {
      uVar1 = nvm_read_words_and_translate_driver_result_74d40(byte_offset,byte_count,destination);
    }
  }
  else {
    uVar1 = 0xffff0000;
  }
  return uVar1;
}

void nvm_tick_and_retry_deferred_program_74db8(void)

{
  undefined4 uVar1;
  int iVar2;
  
  if (nvm_driver_phase == '\0') {
    return;
  }
  if (nvm_driver_phase == 0xaa) {
    DAT_febf6b1c = DAT_febf6b1c + -1;
    if (0 < DAT_febf6b1c) {
      return;
    }
    iVar2 = thunk_return_false_via_zero_hook_79432();
    if (iVar2 == 0) {
      iVar2 = nvm_submit_program_and_set_scaled_timeout_74bbc(DAT_febf6b68, DAT_febf6b6c, (int)((uint32_t)(0xfebf6b28u)));
      if (iVar2 == 2) {
        nvm_set_suspend_policy_byte_781aa(1);
        goto LAB_00074e14;
      }
      uVar1 = 4;
    }
    else {
      iVar2 = nvm_schedule_deferred_program_retry_74bf2();
      if (iVar2 == 2) {
        return;
      }
      uVar1 = 0x11;
    }
    nvm_set_driver_completion_state_u8_749bc(uVar1);
  }
LAB_00074e14:
  nvm_reset_deferred_program_state_749d0();
  return;
}

void nvm_tick_program_timeout_and_abort_74e1c(void)

{
  if (0 < (int32_t)DAT_febf6c34) {
    DAT_febf6c34 = DAT_febf6c34 - (uint)DAT_0002792a;
    if ((int32_t)DAT_febf6c34 < 1) {
      dataflash_abort_operation_and_reset_driver_78766();
      nvm_set_driver_completion_state_u8_749bc(3);
    }
  }
  return;
}

void nvm_poll_driver_and_optional_timers_74e46(char param_1)

{
  uint uVar1;
  
  uVar1 = nvm_sync_access_blocked();
  if (uVar1 == 0) {
    dataflash_poll_and_advance_active_operation_787fa();
    if (param_1 == '\0') {
      nvm_tick_and_retry_deferred_program_74db8();
      nvm_tick_program_timeout_and_abort_74e1c();
    }
    nvm_dispatch_nonpending_driver_completion_74b20();
  }
  return;
}

undefined4 nvm_get_sync_driver_busy_status_74e6e(void)

{
  uint uVar1;
  int iVar2;
  
  uVar1 = nvm_sync_access_blocked();
  if (uVar1 != 1) {
    iVar2 = dataflash_get_driver_state_7888c();
    if (iVar2 == 1) {
      return 0;
    }
    if (iVar2 == 2) {
      return 1;
    }
  }
  return 2;
}

uint nvm_abort_sync_transfer_and_reset_driver_state_74e94(void)

{
  uint uVar1;
  
  uVar1 = nvm_sync_access_blocked();
  if (uVar1 == 1) {
    uVar1 = 0xffff0000;
  }
  else {
    nvm_reset_driver_completion_bytes_749ae();
    dataflash_abort_operation_and_reset_driver_78766();
    uVar1 = nvm_translate_saved_driver_result();
    if (uVar1 == 0) {
      uVar1 = 1;
    }
  }
  nvm_reset_driver_timeout_and_deferred_state_749e4();
  return uVar1;
}

void nvm_set_driver_completion_state_one_74ec2(void)

{
  nvm_set_driver_completion_state_u8_749bc(1);
  return;
}

void nvm_set_driver_completion_from_saved_result_74ed0(void)

{
  nvm_set_driver_completion_state_u8_749bc(2);
  return;
}

undefined4 nvm_map_driver_errors_to_block_actions_74ede(char param_1)

{
  undefined4 uVar1;
  
  if ((param_1 != '\x05') && (-0x7f < param_1)) {
    uVar1 = 0xff;
    if (param_1 == -0x7e) {
      uVar1 = 2;
    }
    return uVar1;
  }
  return 1;
}

undefined4 nvm_capture_module_5c_driver_error_unless_masked_74efe(short param_1,undefined4 param_2,undefined4 param_3,undefined1 param_4)

{
  int iVar1;
  undefined4 uVar2;
  
  iVar1 = nvm_get_flash_callback_guard_781da();
  if ((iVar1 != 1) && (param_1 == 0x5c)) {
    nvm_set_saved_driver_result_u8_749c6(param_4);
    uVar2 = nvm_map_driver_errors_to_block_actions_74ede((uint)(byte)param_4);
    nvm_apply_driver_block_action_74ce8(uVar2);
  }
  return 0;
}

uchar nvm_get_descriptor_option_or_ff_74f2e(uint param_1)

{
  uchar uVar1;
  
  if ((param_1 & 0xffff) < (uint)nvm_descriptor_count) {
    uVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)((uint32_t)(0x27634u + (uint32_t)(param_1 & 0xffff) * (uint32_t)sizeof(F33NvmDescriptor)) + (uint32_t)(0) * (uint32_t)sizeof(F33NvmDescriptor) + (uint32_t)offsetof(F33NvmDescriptor, option)))));
  }
  else {
    uVar1 = 0xff;
  }
  return uVar1;
}

int nvm_store_inverted_current_descriptor_option_74f4a(void)

{
  undefined4 uVar1;
  int iVar2;
  
  uVar1 = nvm_get_storage_handle_77c9e();
  iVar2 = nvm_get_descriptor_option_or_ff_74f2e(uVar1);
  if (iVar2 == 0) {
    uVar1 = 1;
  }
  else {
    uVar1 = 0xff;
    if (iVar2 == 1) {
      uVar1 = 0;
    }
  }
  nvm_set_state_machine_selector_783b6(uVar1);
  return iVar2;
}

void nvm_arm_record_marker_submission_74f72(void)

{
  DAT_febf6c51 = 1;
  return;
}

void nvm_clear_record_marker_submission_latch_74f7e(void)

{
  DAT_febf6c51 = 0;
  return;
}

undefined4 nvm_claim_marker_submission_when_gate_zero_74f88(char param_1)

{
  undefined4 uVar1;
  
  uVar1 = 0;
  if ((param_1 == '\0') && (DAT_febf6c51 == '\x01')) {
    DAT_febf6c51 = '\x02';
    uVar1 = 1;
  }
  return uVar1;
}

void fill_constant_block_74fa2(void)

{
  DAT_febf6c55 = 0;
  DAT_febf6c54 = 0;
  DAT_febf6c53 = 0;
  DAT_febf6c52 = 0;
  DAT_febf6c51 = 0;
  DAT_febf6c50 = 0;
  DAT_febf6c3e = 0xffff;
  DAT_febf6c40 = 0xffff;
  return;
}

undefined4 nvm_reset_record_operation_context_return_one_74fe6(void)

{
  fill_constant_block_74fa2();
  thunk_nvm_reset_active_record_and_checksum_772f8();
  thunk_nvm_invalidate_marker_write_address_77df2();
  return 1;
}
