#include "common.h"

void complete_nvm_zero_handle_operation_unless_status16_73024(uint param_1,char param_2)

{
  uchar result;
  
  if (param_2 != '\x16') {
    reset_nvm_zero_handle_operation_739e8();
    return_only_stub_73a06();
    result = normalize_nvm_completion_status_72fc8(param_2);
    nvm_publish_logical_result(0,param_1,result);
    finish_nvm_operation_event_and_notify_categories_71eb4(0,param_1);
  }
  ((void)(0), clear_shared_countdown_747d2());
  return;
}

void set_nvm_wait_count_five_or_65000_7305e(char param_1)

{
  uint32_t puVar1;
  
  puVar1 = ((uint32_t)(0x5));
  if (param_1 == '\x01') {
    puVar1 = (0xfde8u);
  }
  set_shared_countdown_from_second_argument_747c8(0, (puVar1));
  return;
}

void nvm_notify_reset_result(ushort logical_handle,uint operation)

{
  if (nvm_reset_notification_exclusion != logical_handle) {
    nvm_publish_logical_result(logical_handle,operation,'\x06');
  }
  return;
}

void request_nvm_cancellation_phase_one_73094(void)

{
  select_nvm_cancellation_phase_wrapper_72f76(1);
  return;
}

void nvm_clear_queue_headers(void)

{
  uint uVar1;
  uint uVar2;
  
  uVar2 = 0;
  do {
    uVar1 = uVar2 + 1;
    (*((volatile uint16_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebf68e8u + (uint32_t)(uVar2) * (uint32_t)sizeof(F33NvmQueueHeader)) + (uint32_t)(0) * (uint32_t)sizeof(F33NvmQueueHeader) + (uint32_t)offsetof(F33NvmQueueHeader, head))))) = 0xffff;
    (*((volatile uint16_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebf68e8u + (uint32_t)(uVar2) * (uint32_t)sizeof(F33NvmQueueHeader)) + (uint32_t)(0) * (uint32_t)sizeof(F33NvmQueueHeader) + (uint32_t)offsetof(F33NvmQueueHeader, tail))))) = 0xffff;
    uVar2 = uVar1;
  } while (uVar1 < 0x7f);
  return;
}

uint nvm_queue_index(uint base,uint offset)

{
  return offset + base & 0xffff;
}

void nvm_reset_slot_range_notifying(ushort queue,ushort first,ushort last)

{
  ushort uVar1;
  ushort logical_handle;
  uint operation;
  uint uVar2;
  
  uVar1 = nvm_logical_descriptor_count - 1;
  (*((volatile uint16_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebf68e8u + (uint32_t)(queue) * (uint32_t)sizeof(F33NvmQueueHeader)) + (uint32_t)(0) * (uint32_t)sizeof(F33NvmQueueHeader) + (uint32_t)offsetof(F33NvmQueueHeader, head))))) = first;
  (*((volatile uint16_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebf68e8u + (uint32_t)(queue) * (uint32_t)sizeof(F33NvmQueueHeader)) + (uint32_t)(0) * (uint32_t)sizeof(F33NvmQueueHeader) + (uint32_t)offsetof(F33NvmQueueHeader, tail))))) = last;
  for (uVar2 = (uint)first; uVar2 <= last; uVar2 = uVar2 + 1 & 0xffff) {
    operation = (*((volatile uint32_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebf6128u + (uint32_t)(uVar2) * (uint32_t)sizeof(F33NvmQueueSlot)) + (uint32_t)(0) * (uint32_t)sizeof(F33NvmQueueSlot) + (uint32_t)offsetof(F33NvmQueueSlot, operation)))));
    if (operation != 0x9da70ae7) {
      logical_handle = (*((volatile uint16_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebf6128u + (uint32_t)(uVar2) * (uint32_t)sizeof(F33NvmQueueSlot)) + (uint32_t)(0) * (uint32_t)sizeof(F33NvmQueueSlot) + (uint32_t)offsetof(F33NvmQueueSlot, logical_handle)))));
      if ((uVar1 < logical_handle) || (logical_handle < 2)) {
        record_nvm_integrity_fault_72130();
      }
      else {
        nvm_notify_reset_result(logical_handle,operation);
      }
    }
    (*((volatile uint32_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebf6128u + (uint32_t)(uVar2) * (uint32_t)sizeof(F33NvmQueueSlot)) + (uint32_t)(0) * (uint32_t)sizeof(F33NvmQueueSlot) + (uint32_t)offsetof(F33NvmQueueSlot, operation))))) = 0x9da70ae7;
    (*((volatile uint16_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebf6128u + (uint32_t)(uVar2) * (uint32_t)sizeof(F33NvmQueueSlot)) + (uint32_t)(0) * (uint32_t)sizeof(F33NvmQueueSlot) + (uint32_t)offsetof(F33NvmQueueSlot, logical_handle))))) = 0xffff;
    (*((volatile uint32_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebf6128u + (uint32_t)(uVar2) * (uint32_t)sizeof(F33NvmQueueSlot)) + (uint32_t)(0) * (uint32_t)sizeof(F33NvmQueueSlot) + (uint32_t)offsetof(F33NvmQueueSlot, read_buffer))))) = 0;
    (*((volatile uint32_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebf6128u + (uint32_t)(uVar2) * (uint32_t)sizeof(F33NvmQueueSlot)) + (uint32_t)(0) * (uint32_t)sizeof(F33NvmQueueSlot) + (uint32_t)offsetof(F33NvmQueueSlot, write_buffer))))) = 0;
    (*((volatile uint16_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebf6128u + (uint32_t)(uVar2) * (uint32_t)sizeof(F33NvmQueueSlot)) + (uint32_t)(0) * (uint32_t)sizeof(F33NvmQueueSlot) + (uint32_t)offsetof(F33NvmQueueSlot, next))))) = (short)uVar2 + 1;
  }
  (*((volatile uint16_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebf6128u + (uint32_t)(last) * (uint32_t)sizeof(F33NvmQueueSlot)) + (uint32_t)(0) * (uint32_t)sizeof(F33NvmQueueSlot) + (uint32_t)offsetof(F33NvmQueueSlot, next))))) = 0xffff;
  return;
}

void nvm_reset_slot_range(ushort queue,ushort first,ushort last)

{
  uint uVar1;
  
  (*((volatile uint16_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebf68e8u + (uint32_t)(queue) * (uint32_t)sizeof(F33NvmQueueHeader)) + (uint32_t)(0) * (uint32_t)sizeof(F33NvmQueueHeader) + (uint32_t)offsetof(F33NvmQueueHeader, head))))) = first;
  (*((volatile uint16_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebf68e8u + (uint32_t)(queue) * (uint32_t)sizeof(F33NvmQueueHeader)) + (uint32_t)(0) * (uint32_t)sizeof(F33NvmQueueHeader) + (uint32_t)offsetof(F33NvmQueueHeader, tail))))) = last;
  for (uVar1 = (uint)first; uVar1 <= last; uVar1 = uVar1 + 1 & 0xffff) {
    (*((volatile uint32_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebf6128u + (uint32_t)(uVar1) * (uint32_t)sizeof(F33NvmQueueSlot)) + (uint32_t)(0) * (uint32_t)sizeof(F33NvmQueueSlot) + (uint32_t)offsetof(F33NvmQueueSlot, operation))))) = 0x9da70ae7;
    (*((volatile uint32_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebf6128u + (uint32_t)(uVar1) * (uint32_t)sizeof(F33NvmQueueSlot)) + (uint32_t)(0) * (uint32_t)sizeof(F33NvmQueueSlot) + (uint32_t)offsetof(F33NvmQueueSlot, read_buffer))))) = 0;
    (*((volatile uint32_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebf6128u + (uint32_t)(uVar1) * (uint32_t)sizeof(F33NvmQueueSlot)) + (uint32_t)(0) * (uint32_t)sizeof(F33NvmQueueSlot) + (uint32_t)offsetof(F33NvmQueueSlot, write_buffer))))) = 0;
    (*((volatile uint16_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebf6128u + (uint32_t)(uVar1) * (uint32_t)sizeof(F33NvmQueueSlot)) + (uint32_t)(0) * (uint32_t)sizeof(F33NvmQueueSlot) + (uint32_t)offsetof(F33NvmQueueSlot, logical_handle))))) = 0xffff;
    (*((volatile uint16_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebf6128u + (uint32_t)(uVar1) * (uint32_t)sizeof(F33NvmQueueSlot)) + (uint32_t)(0) * (uint32_t)sizeof(F33NvmQueueSlot) + (uint32_t)offsetof(F33NvmQueueSlot, next))))) = (short)uVar1 + 1;
  }
  (*((volatile uint16_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebf6128u + (uint32_t)(last) * (uint32_t)sizeof(F33NvmQueueSlot)) + (uint32_t)(0) * (uint32_t)sizeof(F33NvmQueueSlot) + (uint32_t)offsetof(F33NvmQueueSlot, next))))) = 0xffff;
  return;
}

void nvm_reset_pooled_queues(uchar notify)

{
  uint uVar1;
  uint uVar2;
  uint uVar3;
  
  nvm_clear_queue_headers();
  uVar2 = nvm_queue_index(0,0);
  uVar3 = nvm_queue_index(1,0);
  uVar1 = 0x7a;
  if (notify == '\x01') {
    nvm_reset_slot_range_notifying((ushort)uVar2,0x7a,0x7a);
    nvm_reset_slot_range_notifying((ushort)uVar3,0,0x79);
  }
  else {
    (*((volatile uint16_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebf68e8u + (uint32_t)(uVar2 & 0xffff) * (uint32_t)sizeof(F33NvmQueueHeader)) + (uint32_t)(0) * (uint32_t)sizeof(F33NvmQueueHeader) + (uint32_t)offsetof(F33NvmQueueHeader, head))))) = 0x7a;
    (*((volatile uint16_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebf68e8u + (uint32_t)(uVar2 & 0xffff) * (uint32_t)sizeof(F33NvmQueueHeader)) + (uint32_t)(0) * (uint32_t)sizeof(F33NvmQueueHeader) + (uint32_t)offsetof(F33NvmQueueHeader, tail))))) = 0x7a;
    for (; uVar1 < 0x7b; uVar1 = uVar1 + 1 & 0xffff) {
      (*((volatile uint32_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebf6128u + (uint32_t)(uVar1) * (uint32_t)sizeof(F33NvmQueueSlot)) + (uint32_t)(0) * (uint32_t)sizeof(F33NvmQueueSlot) + (uint32_t)offsetof(F33NvmQueueSlot, operation))))) = 0x9da70ae7;
      (*((volatile uint32_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebf6128u + (uint32_t)(uVar1) * (uint32_t)sizeof(F33NvmQueueSlot)) + (uint32_t)(0) * (uint32_t)sizeof(F33NvmQueueSlot) + (uint32_t)offsetof(F33NvmQueueSlot, read_buffer))))) = 0;
      (*((volatile uint32_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebf6128u + (uint32_t)(uVar1) * (uint32_t)sizeof(F33NvmQueueSlot)) + (uint32_t)(0) * (uint32_t)sizeof(F33NvmQueueSlot) + (uint32_t)offsetof(F33NvmQueueSlot, write_buffer))))) = 0;
      (*((volatile uint16_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebf6128u + (uint32_t)(uVar1) * (uint32_t)sizeof(F33NvmQueueSlot)) + (uint32_t)(0) * (uint32_t)sizeof(F33NvmQueueSlot) + (uint32_t)offsetof(F33NvmQueueSlot, logical_handle))))) = 0xffff;
      (*((volatile uint16_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebf6128u + (uint32_t)(uVar1) * (uint32_t)sizeof(F33NvmQueueSlot)) + (uint32_t)(0) * (uint32_t)sizeof(F33NvmQueueSlot) + (uint32_t)offsetof(F33NvmQueueSlot, next))))) = (short)uVar1 + 1;
    }
    (*((volatile uint16_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebf6128u + (uint32_t)(0x7a) * (uint32_t)sizeof(F33NvmQueueSlot)) + (uint32_t)(0) * (uint32_t)sizeof(F33NvmQueueSlot) + (uint32_t)offsetof(F33NvmQueueSlot, next))))) = 0xffff;
                    /* WARNING: Could not inline here */
    nvm_reset_slot_range((ushort)uVar3,0,0x79);
  }
  nvm_reserved_free_count = 1;
  nvm_normal_free_count = 0x7a;
  nvm_reserved_used_count = 0;
  nvm_normal_used_count = 0;
  return;
}

void nvm_reset_zero_handle_operation(uchar notify)

{
  if ((notify == '\x01') && (nvm_zero_handle_operation.operation != 0x9da70ae7)) {
    nvm_notify_reset_result(0,nvm_zero_handle_operation.operation);
  }
  nvm_zero_handle_operation.operation = 0x9da70ae7;
  nvm_zero_handle_operation.logical_handle = 0xffff;
  nvm_zero_handle_operation.buffer_08 = 0;
  nvm_zero_handle_operation.buffer_0c = 0;
  return;
}

bool validate_nvm_pool_counts_and_test_nonempty_73274(void)

{
  bool bVar1;
  
  bVar1 = false;
  if (((ushort)(nvm_reserved_free_count + nvm_reserved_used_count) == 1) &&
     ((ushort)(nvm_normal_free_count + nvm_normal_used_count) == 0x7a)) {
    bVar1 = (ushort)(nvm_normal_used_count + nvm_reserved_used_count) != 0;
  }
  else {
    record_nvm_integrity_fault_72130();
  }
  return bVar1;
}

uint nvm_check_queue_empty(F33NvmQueueHeader *header,uchar *empty)

{
  if (header->head == 0xffff) {
    if (header->tail == 0xffff) {
      *empty = '\x01';
      return 0;
    }
  }
  else if (header->tail != 0xffff) {
    *empty = '\0';
    return 0;
  }
  record_nvm_integrity_fault_72130();
  return 1;
}

uint nvm_check_slot_partition(ushort index,ushort queue)

{
  ushort uVar1;
  uint uVar2;
  ushort uVar3;
  
  uVar2 = 0;
  if ((queue == 0) || (queue == 2)) {
    uVar1 = 0x7a;
    uVar3 = uVar1;
  }
  else {
    uVar1 = 0;
    uVar3 = 0x79;
  }
  if ((uVar3 < index) || (index < uVar1)) {
    record_nvm_integrity_fault_72130();
    uVar2 = 1;
  }
  return uVar2;
}

uint nvm_queue_key(ushort logical_handle)

{
  return (uint)(*((volatile uint8_t *)camry_host_ptr((uint32_t)((uint32_t)(0x26c0cu + (uint32_t)(logical_handle) * (uint32_t)sizeof(F33NvmLogicalDescriptor)) + (uint32_t)(0) * (uint32_t)sizeof(F33NvmLogicalDescriptor) + (uint32_t)offsetof(F33NvmLogicalDescriptor, queue_key)))));
}

bool reject_nvm_queue_slot_key_mismatch_73334(uint param_1,short param_2)

{
  ushort logical_handle;
  uint uVar1;
  uint uVar2;
  bool bVar3;
  
  logical_handle = (*((volatile uint16_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebf6128u + (uint32_t)(param_1 & 0xffff) * (uint32_t)sizeof(F33NvmQueueSlot)) + (uint32_t)(0) * (uint32_t)sizeof(F33NvmQueueSlot) + (uint32_t)offsetof(F33NvmQueueSlot, logical_handle)))));
  bVar3 = true;
  if ((logical_handle <= (ushort)(nvm_logical_descriptor_count - 1)) && (1 < logical_handle)) {
    uVar2 = nvm_queue_key(logical_handle);
    uVar1 = 0;
    if (param_2 != 2) {
      uVar1 = (uint)(ushort)(param_2 - 3);
    }
    bVar3 = uVar2 != uVar1;
    if (uVar2 == uVar1) {
      return false;
    }
  }
  record_nvm_integrity_fault_72130();
  return bVar3;
}

undefined4 peek_validated_nvm_queue_head_index_73380(ushort param_1,ushort *param_2)

{
  ushort index;
  uint uVar1;
  int iVar2;
  undefined4 uVar3;
  uchar uStack_15;
  
  uVar3 = 1;
  uStack_15 = '\0';
  uVar1 = nvm_check_queue_empty(((volatile F33NvmQueueHeader *)camry_host_ptr((uint32_t)(0xfebf68e8u + (uint32_t)(param_1) * (uint32_t)sizeof(F33NvmQueueHeader)))),&uStack_15);
  if ((uVar1 == 0) && (uStack_15 == '\0')) {
    index = (*((volatile uint16_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebf68e8u + (uint32_t)(param_1) * (uint32_t)sizeof(F33NvmQueueHeader)) + (uint32_t)(0) * (uint32_t)sizeof(F33NvmQueueHeader) + (uint32_t)offsetof(F33NvmQueueHeader, head)))));
    uVar1 = nvm_check_slot_partition(index,param_1);
    if ((uVar1 == 0) && (iVar2 = reject_nvm_queue_slot_key_mismatch_73334(index,(uint)param_1), iVar2 == 0)) {
      *param_2 = index;
      uVar3 = 0;
    }
  }
  return uVar3;
}

undefined4 find_first_nonempty_nvm_queue_in_range_733da(ushort param_1,short param_2,undefined2 *param_3)

{
  ushort uVar1;
  int iVar2;
  uint uVar3;
  undefined2 uStack_16;
  
  uVar1 = param_2 + param_1;
  uStack_16 = 0xffff;
  while( true ) {
    if (uVar1 <= param_1) {
      return 1;
    }
    iVar2 = peek_validated_nvm_queue_head_index_73380(param_1,&uStack_16);
    if (iVar2 == 0) break;
    param_1 = param_1 + 1;
  }
  uVar3 = nvm_service_uninitialized();
  if (uVar3 != 0) {
    return 1;
  }
  *param_3 = uStack_16;
  return 0;
}

void copy_nvm_queue_slot_to_operation_record_73424(undefined4 *param_1,undefined4 *param_2)

{
  *param_1 = *param_2;
  *(undefined2 *)(param_1 + 1) = *(undefined2 *)(param_2 + 3);
  param_1[2] = param_2[1];
  param_1[3] = param_2[2];
  return;
}

int peek_nvm_operation_across_queue_range_73440(uint param_1,uint param_2,undefined4 param_3,undefined4 param_4)

{
  undefined4 extraout_r8;
  uint uVar1;
  int iVar2;
  ushort auStack_e [3];
  
  auStack_e[0] = 0xffff;
  uVar1 = nvm_queue_index(param_1 & 0xffff,param_2 & 0xffff);
  iVar2 = find_first_nonempty_nvm_queue_in_range_733da(uVar1,((undefined4)((uint)(ushort)param_3)),auStack_e);
  if (iVar2 == 0) {
    copy_nvm_queue_slot_to_operation_record_73424(((undefined4 *)camry_host_ptr((uint32_t)(param_4))), ((volatile F33NvmQueueSlot *)camry_host_ptr((uint32_t)(0xfebf6128u + (uint32_t)(auStack_e[0]) * (uint32_t)sizeof(F33NvmQueueSlot)))));
  }
  return iVar2;
}

undefined4 peek_nvm_queued_operation_with_opcode_validation_7347e(int *param_1)

{
  int iVar1;
  undefined4 uVar2;
  
  uVar2 = 1;
  iVar1 = validate_nvm_pool_counts_and_test_nonempty_73274();
  if (iVar1 == 1) {
    iVar1 = peek_nvm_operation_across_queue_range_73440(2, 0, 0x7d, camry_host_addr(param_1));
    if ((iVar1 == 0) &&
       ((((iVar1 = *param_1, iVar1 == 0x1c646989 || (iVar1 == 0x22aa8a36)) || (iVar1 == -0x63e078f7)
         ) || (((iVar1 == -0x5e59df6d || (iVar1 == -0x4916950f)) || (iVar1 == -0x46eba6ac)))))) {
      uVar2 = 0;
    }
    else {
      record_nvm_integrity_fault_72130();
    }
  }
  return uVar2;
}

uint nvm_uses_reserved_queue(ushort logical_handle,uint operation)

{
  uint uVar1;
  
  uVar1 = 0;
  if (((*((volatile uint8_t *)camry_host_ptr((uint32_t)((uint32_t)(0x26c0cu + (uint32_t)(logical_handle) * (uint32_t)sizeof(F33NvmLogicalDescriptor)) + (uint32_t)(0) * (uint32_t)sizeof(F33NvmLogicalDescriptor) + (uint32_t)offsetof(F33NvmLogicalDescriptor, queue_key))))) == '\0') &&
     ((operation == 0x22aa8a36 || (operation == 0x1c646989)))) {
    uVar1 = 1;
  }
  return uVar1;
}

bool peek_nvm_reserved_queue_operation_73516(uint *param_1)

{
  int iVar1;
  uint uVar2;
  bool bVar3;
  
  bVar3 = true;
  iVar1 = validate_nvm_pool_counts_and_test_nonempty_73274();
  if ((iVar1 == 1) && (iVar1 = peek_nvm_operation_across_queue_range_73440(2, 0, 1, camry_host_addr(param_1)), iVar1 == 0)) {
    uVar2 = nvm_uses_reserved_queue((ushort)param_1[1],*param_1);
    bVar3 = uVar2 != 1;
    if (bVar3) {
      record_nvm_integrity_fault_72130();
    }
  }
  return bVar3;
}

uint nvm_append_queue_slot(ushort queue,ushort index)

{
  ushort index_00;
  uint uVar1;
  
  index_00 = (*((volatile uint16_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebf68e8u + (uint32_t)(queue) * (uint32_t)sizeof(F33NvmQueueHeader)) + (uint32_t)(0) * (uint32_t)sizeof(F33NvmQueueHeader) + (uint32_t)offsetof(F33NvmQueueHeader, tail)))));
  if (index_00 == 0xffff) {
    (*((volatile uint16_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebf68e8u + (uint32_t)(queue) * (uint32_t)sizeof(F33NvmQueueHeader)) + (uint32_t)(0) * (uint32_t)sizeof(F33NvmQueueHeader) + (uint32_t)offsetof(F33NvmQueueHeader, head))))) = index;
  }
  else {
    uVar1 = nvm_check_slot_partition(index_00,queue);
    if (uVar1 != 0) {
      return 1;
    }
    (*((volatile uint16_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebf6128u + (uint32_t)(index_00) * (uint32_t)sizeof(F33NvmQueueSlot)) + (uint32_t)(0) * (uint32_t)sizeof(F33NvmQueueSlot) + (uint32_t)offsetof(F33NvmQueueSlot, next))))) = index;
  }
  (*((volatile uint16_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebf68e8u + (uint32_t)(queue) * (uint32_t)sizeof(F33NvmQueueHeader)) + (uint32_t)(0) * (uint32_t)sizeof(F33NvmQueueHeader) + (uint32_t)offsetof(F33NvmQueueHeader, tail))))) = index;
  (*((volatile uint16_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebf6128u + (uint32_t)(index) * (uint32_t)sizeof(F33NvmQueueSlot)) + (uint32_t)(0) * (uint32_t)sizeof(F33NvmQueueSlot) + (uint32_t)offsetof(F33NvmQueueSlot, next))))) = 0xffff;
  return 0;
}

void nvm_copy_operation_to_slot(F33NvmQueueSlot *slot,F33NvmOperation *operation)

{
  slot->operation = operation->operation;
  slot->logical_handle = operation->logical_handle;
  slot->read_buffer = operation->buffer_08;
  slot->write_buffer = operation->buffer_0c;
  return;
}

uint nvm_append_operation(ushort queue,ushort index,F33NvmOperation *operation)

{
  uint uVar1;
  
  uVar1 = nvm_append_queue_slot(queue,index);
  if (uVar1 == 0) {
    (*((volatile uint32_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebf6128u + (uint32_t)(index) * (uint32_t)sizeof(F33NvmQueueSlot)) + (uint32_t)(0) * (uint32_t)sizeof(F33NvmQueueSlot) + (uint32_t)offsetof(F33NvmQueueSlot, operation))))) = operation->operation;
    (*((volatile uint16_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebf6128u + (uint32_t)(index) * (uint32_t)sizeof(F33NvmQueueSlot)) + (uint32_t)(0) * (uint32_t)sizeof(F33NvmQueueSlot) + (uint32_t)offsetof(F33NvmQueueSlot, logical_handle))))) = operation->logical_handle;
    (*((volatile uint32_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebf6128u + (uint32_t)(index) * (uint32_t)sizeof(F33NvmQueueSlot)) + (uint32_t)(0) * (uint32_t)sizeof(F33NvmQueueSlot) + (uint32_t)offsetof(F33NvmQueueSlot, read_buffer))))) = operation->buffer_08;
    (*((volatile uint32_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebf6128u + (uint32_t)(index) * (uint32_t)sizeof(F33NvmQueueSlot)) + (uint32_t)(0) * (uint32_t)sizeof(F33NvmQueueSlot) + (uint32_t)offsetof(F33NvmQueueSlot, write_buffer))))) = operation->buffer_0c;
  }
  return uVar1;
}

uint nvm_enqueue_pooled_operation(F33NvmOperation *operation)

{
  ushort uVar1;
  uint uVar2;
  uint offset;
  uint base;
  ushort *puVar3;
  ushort *puVar4;
  ushort uStack_22;
  
  uVar1 = operation->logical_handle;
  uStack_22 = 0xffff;
  uVar2 = nvm_uses_reserved_queue(uVar1,operation->operation);
  if (uVar2 != 1) {
    base = 3;
    offset = nvm_queue_key(uVar1);
    puVar4 = ((void *)camry_host_ptr((uint32_t)((0xfebf6ae6u))));
    puVar3 = ((void *)camry_host_ptr((uint32_t)((0xfebf6aeau))));
  }
  else {
    base = 2;
    offset = 0;
    puVar4 = ((void *)camry_host_ptr((uint32_t)((0xfebf6ae4u))));
    puVar3 = ((void *)camry_host_ptr((uint32_t)((0xfebf6ae8u))));
  }
  uVar2 = nvm_queue_index((uint)(uVar2 != 1),0);
  uVar2 = nvm_pop_queue_head((ushort)uVar2, camry_host_addr(&uStack_22));
  uVar1 = uStack_22;
  if (uVar2 == 0) {
    if ((*((volatile uint32_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebf6128u + (uint32_t)(uStack_22) * (uint32_t)sizeof(F33NvmQueueSlot)) + (uint32_t)(0) * (uint32_t)sizeof(F33NvmQueueSlot) + (uint32_t)offsetof(F33NvmQueueSlot, operation))))) == 0x9da70ae7) {
      uVar2 = nvm_queue_index(base,offset);
      uVar2 = nvm_append_operation((ushort)uVar2,uVar1,operation);
      if (uVar2 != 0) {
        return uVar2;
      }
      *puVar4 = *puVar4 - 1;
      *puVar3 = *puVar3 + 1;
      return 0;
    }
  }
  else if (*puVar4 == 0) {
    set_nvm_category_state_two_72108(3);
    return 1;
  }
  record_nvm_integrity_fault_72130();
  return 1;
}

uint recycle_nvm_queue_slot_and_copy_operation_73748(ushort param_1,ushort param_2,undefined4 param_3)

{
  undefined4 *extraout_r7;
  uint uVar1;
  
  uVar1 = nvm_append_queue_slot(param_1,param_2);
  if (uVar1 == 0) {
    copy_nvm_queue_slot_to_operation_record_73424(((undefined4 *)camry_host_ptr((uint32_t)(param_3))), ((volatile F33NvmQueueSlot *)camry_host_ptr((uint32_t)(0xfebf6128u + (uint32_t)(param_2) * (uint32_t)sizeof(F33NvmQueueSlot)))));
    *((undefined4 *)(((volatile F33NvmQueueSlot *)camry_host_ptr((uint32_t)(0xfebf6128u + (uint32_t)(param_2) * (uint32_t)sizeof(F33NvmQueueSlot)))))) = 0x9da70ae7;
    ((undefined4 *)(((volatile F33NvmQueueSlot *)camry_host_ptr((uint32_t)(0xfebf6128u + (uint32_t)(param_2) * (uint32_t)sizeof(F33NvmQueueSlot))))))[1] = 0;
    ((undefined4 *)(((volatile F33NvmQueueSlot *)camry_host_ptr((uint32_t)(0xfebf6128u + (uint32_t)(param_2) * (uint32_t)sizeof(F33NvmQueueSlot))))))[2] = 0;
    (*((volatile undefined2 *)((uint8_t *)((undefined4 *)(((volatile F33NvmQueueSlot *)camry_host_ptr((uint32_t)(0xfebf6128u + (uint32_t)(param_2) * (uint32_t)sizeof(F33NvmQueueSlot)))))) + 12u))) = 0xffff;
  }
  return uVar1;
}

int pop_matching_nvm_head_and_recycle_slot_73784(ushort param_1,uint param_2,undefined4 param_3)

{
  uint uVar1;
  uint uVar2;
  uint base;
  ushort *puVar3;
  ushort *puVar4;
  int iVar5;
  ushort uStack_22;
  
  iVar5 = 1;
  uStack_22 = 0xffff;
  uVar2 = nvm_uses_reserved_queue(param_1,param_2);
  if (uVar2 != 1) {
    base = 3;
    uVar1 = nvm_queue_key(param_1);
    puVar4 = ((void *)camry_host_ptr((uint32_t)((0xfebf6ae6u))));
    puVar3 = ((void *)camry_host_ptr((uint32_t)((0xfebf6aeau))));
  }
  else {
    uVar1 = 0;
    base = 2;
    puVar4 = ((void *)camry_host_ptr((uint32_t)((0xfebf6ae4u))));
    puVar3 = ((void *)camry_host_ptr((uint32_t)((0xfebf6ae8u))));
  }
  uVar1 = nvm_queue_index(base,uVar1);
  uVar1 = nvm_pop_queue_head((ushort)uVar1, camry_host_addr(&uStack_22));
  if (uVar1 == 0) {
    uVar1 = (uint)uStack_22;
    if (param_1 == (*((volatile uint16_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebf6128u + (uint32_t)(uVar1) * (uint32_t)sizeof(F33NvmQueueSlot)) + (uint32_t)(0) * (uint32_t)sizeof(F33NvmQueueSlot) + (uint32_t)offsetof(F33NvmQueueSlot, logical_handle)))))) {
      uVar2 = nvm_queue_index((uint)(uVar2 != 1),0);
      iVar5 = recycle_nvm_queue_slot_and_copy_operation_73748(uVar2,uVar1,param_3);
      if (iVar5 == 0) {
        *puVar4 = *puVar4 + 1;
        *puVar3 = *puVar3 - 1;
      }
    }
    else {
      record_nvm_integrity_fault_72130();
    }
  }
  return iVar5;
}

undefined4 find_nvm_handle_in_slot_chain_73828(ushort *param_1,ushort param_2,ushort *param_3,undefined2 *param_4)

{
  ushort uVar1;
  uint uVar2;
  uint uVar3;
  int iVar4;
  
  uVar1 = *param_1;
  iVar4 = 0x7b;
  uVar3 = 0xffffffff;
  do {
    uVar2 = (uint)uVar1;
    if (uVar2 == 0xffff) {
      return 1;
    }
    if (0x7a < uVar2) {
      record_nvm_integrity_fault_72130();
      return 1;
    }
    if (param_2 == (*((volatile uint16_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebf6128u + (uint32_t)(uVar2) * (uint32_t)sizeof(F33NvmQueueSlot)) + (uint32_t)(0) * (uint32_t)sizeof(F33NvmQueueSlot) + (uint32_t)offsetof(F33NvmQueueSlot, logical_handle)))))) {
      *param_3 = uVar1;
      *param_4 = (short)uVar3;
      return 0;
    }
    uVar1 = (*((volatile uint16_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebf6128u + (uint32_t)(uVar2) * (uint32_t)sizeof(F33NvmQueueSlot)) + (uint32_t)(0) * (uint32_t)sizeof(F33NvmQueueSlot) + (uint32_t)offsetof(F33NvmQueueSlot, next)))));
    iVar4 = iVar4 + -1;
    uVar3 = uVar2;
  } while (iVar4 != 0);
  return 1;
}

int unlink_nvm_handle_from_queue_73878(undefined2 param_1,uint param_2,ushort *param_3)

{
  uint8_t stack_record_19[25];
  F33NvmQueueHeader *header;
  ushort uVar1;
  uint uVar2;
  int iVar3;
  
  (*((uint16_t *)(stack_record_19 + 1))) = 0xffff;
  (*((uint16_t *)(stack_record_19 + 3))) = 0xffff;
  iVar3 = 1;
  stack_record_19[0] = '\0';
  header = ((volatile F33NvmQueueHeader *)camry_host_ptr((uint32_t)(0xfebf68e8u + (uint32_t)((param_2 & 0xffff)) * (uint32_t)sizeof(F33NvmQueueHeader))));
  uVar2 = nvm_check_queue_empty(header,((uint8_t *)(stack_record_19)));
  if (((uVar2 == 0) && (stack_record_19[0] == '\0')) &&
     (iVar3 = find_nvm_handle_in_slot_chain_73828(header,param_1,((uint16_t *)((stack_record_19 + 1))),((uint16_t *)((stack_record_19 + 3)))), iVar3 == 0)) {
    uVar1 = (*((volatile uint16_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebf6128u + (uint32_t)((*((uint16_t *)(stack_record_19 + 1)))) * (uint32_t)sizeof(F33NvmQueueSlot)) + (uint32_t)(0) * (uint32_t)sizeof(F33NvmQueueSlot) + (uint32_t)offsetof(F33NvmQueueSlot, next)))));
    if ((*((uint16_t *)(stack_record_19 + 3))) == 0xffff) {
      header->head = uVar1;
      (*((uint16_t *)(stack_record_19 + 3))) = uVar1;
    }
    else {
      (*((volatile uint16_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebf6128u + (uint32_t)((*((uint16_t *)(stack_record_19 + 3)))) * (uint32_t)sizeof(F33NvmQueueSlot)) + (uint32_t)(0) * (uint32_t)sizeof(F33NvmQueueSlot) + (uint32_t)offsetof(F33NvmQueueSlot, next))))) = uVar1;
      uVar1 = (*((volatile uint16_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebf6128u + (uint32_t)((*((uint16_t *)(stack_record_19 + 1)))) * (uint32_t)sizeof(F33NvmQueueSlot)) + (uint32_t)(0) * (uint32_t)sizeof(F33NvmQueueSlot) + (uint32_t)offsetof(F33NvmQueueSlot, next)))));
    }
    if (uVar1 == 0xffff) {
      (*((volatile uint16_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebf68e8u + (uint32_t)(param_2 & 0xffff) * (uint32_t)sizeof(F33NvmQueueHeader)) + (uint32_t)(0) * (uint32_t)sizeof(F33NvmQueueHeader) + (uint32_t)offsetof(F33NvmQueueHeader, tail))))) = (*((uint16_t *)(stack_record_19 + 3)));
    }
    *param_3 = (*((uint16_t *)(stack_record_19 + 1)));
  }
  return iVar3;
}

int remove_nvm_handle_and_recycle_queue_slot_738e2(ushort param_1,undefined4 param_2)

{
  uint uVar1;
  uint uVar2;
  int iVar3;
  ushort *puVar4;
  ushort *puVar5;
  undefined2 uStack_1e;
  
  uStack_1e = 0xffff;
  uVar1 = nvm_queue_key(param_1);
  if (uVar1 == 0) {
    uVar2 = nvm_queue_index(2,0);
    iVar3 = unlink_nvm_handle_from_queue_73878(param_1,uVar2,&uStack_1e);
    uVar2 = 0;
    puVar5 = ((void *)camry_host_ptr((uint32_t)((0xfebf6ae4u))));
    puVar4 = ((void *)camry_host_ptr((uint32_t)((0xfebf6ae8u))));
    if (iVar3 == 0) goto LAB_0007394a;
  }
  uVar1 = nvm_queue_index(3,uVar1);
  iVar3 = unlink_nvm_handle_from_queue_73878(param_1,uVar1,&uStack_1e);
  uVar2 = 1;
  puVar5 = ((void *)camry_host_ptr((uint32_t)((0xfebf6ae6u))));
  puVar4 = ((void *)camry_host_ptr((uint32_t)((0xfebf6aeau))));
  if (iVar3 != 0) {
    return 1;
  }
LAB_0007394a:
  uVar1 = nvm_queue_index(uVar2,0);
  iVar3 = recycle_nvm_queue_slot_and_copy_operation_73748(uVar1,uStack_1e,param_2);
  if (iVar3 == 0) {
    *puVar5 = *puVar5 + 1;
    *puVar4 = *puVar4 - 1;
  }
  return iVar3;
}

undefined4 snapshot_nvm_zero_handle_operation_if_present_73978(uint *param_1)

{
  if (nvm_zero_handle_operation.operation != 0x9da70ae7) {
    *param_1 = nvm_zero_handle_operation.operation;
    *(ushort *)(param_1 + 1) = nvm_zero_handle_operation.logical_handle;
    param_1[2] = (uint)nvm_zero_handle_operation.buffer_08;
    param_1[3] = (uint)nvm_zero_handle_operation.buffer_0c;
    return 0;
  }
  return 1;
}

bool store_nvm_zero_handle_operation_if_empty_739a8(uint *param_1)

{
  bool bVar1;
  
  bVar1 = nvm_zero_handle_operation.operation != 0x9da70ae7;
  if (bVar1) {
    set_nvm_category_state_two_72108(3);
  }
  else {
    nvm_zero_handle_operation.operation = *param_1;
    nvm_zero_handle_operation.logical_handle = (ushort)param_1[1];
    nvm_zero_handle_operation.buffer_08 = ((uint32_t)(param_1[2]));
    nvm_zero_handle_operation.buffer_0c = ((uint32_t)(param_1[3]));
  }
  return bVar1;
}

void reset_nvm_zero_handle_operation_739e8(void)

{
  nvm_zero_handle_operation.operation = 0x9da70ae7;
  nvm_zero_handle_operation.logical_handle = 0xffff;
  nvm_zero_handle_operation.buffer_08 = 0;
  nvm_zero_handle_operation.buffer_0c = 0;
  return;
}

void return_only_stub_73a06(void)

{
  return;
}

undefined4 lookup_u32_pair_value_or_default_73a5c(int param_1,undefined4 param_2,uint *param_3)

{
  uint uVar1;
  
  uVar1 = 0;
  while( true ) {
    if (*param_3 <= uVar1) {
      return param_2;
    }
    if ((*((int *)camry_host_ptr((uint32_t)(param_3[1] + uVar1 * 8)))) == param_1) break;
    uVar1 = uVar1 + 1;
  }
  return (*((undefined4 *)camry_host_ptr((uint32_t)(param_3[1] + uVar1 * 8 + 4))));
}

void nvm_copy_operation(F33NvmOperation *request)

{
  nvm_pending_operation.operation = request->operation;
  nvm_pending_operation.logical_handle = request->logical_handle;
  nvm_pending_operation.buffer_08 = request->buffer_08;
  nvm_pending_operation.buffer_0c = request->buffer_0c;
  return;
}

void nvm_select_service_poll(uchar full_service)

{
  nvm_set_service_poll(full_service);
  return;
}

uchar thunk_nvm_get_physical_result_state_766c6(void)

{
  return nvm_get_physical_result_state_766c6();
}

uint dispatch_nvm_operation_step_or_phase_eight_callback_73b46(int param_1,uint param_2)

{
  uint32_t puVar1;
  int iVar2;
  uint32_t pcVar3;
  
  puVar1 = 0x23dfcu;
  param_2 = param_2 & 0xffff;
  iVar2 = ((void)(nvm_pending_operation.logical_handle), thunk_nvm_get_physical_result_state_766c6());
  if (iVar2 != 2) {
    if (param_2 == 4) {
      if ((uint)(*((ushort *)camry_host_ptr((uint32_t)(puVar1 + param_1 * 0x10 + 0x37b4)))) <= (uint)nvm_operation_step) {
        return 4;
      }
      pcVar3 = (uint32_t)((uintptr_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)((uint)nvm_operation_step * 4 +
                         (*((int *)camry_host_ptr((uint32_t)(puVar1 + param_1 * 0x10 + 0x37b8))))))))));
    }
    else {
      if (param_2 != 8) {
        return param_2;
      }
      pcVar3 = (uint32_t)((uintptr_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x37bcu + (int)(puVar1 + param_1 * 0x10))))));
    }
    param_2 = (*(int (*)())camry_indirect((uint32_t)(pcVar3)))();
  }
  return param_2;
}

uint32_t nvm_dispatch_operation_phase_73ba0(int param_1)

{
  uint32_t camry_r10_result;
  uint uVar1;
  int iVar2;
  uint uVar3;
  uint32_t pcVar4;
  
  uVar3 = (uint)nvm_operation_phase;
  if (uVar3 == 1) {
    pcVar4 = (uint32_t)((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x275acu + (uint32_t)(param_1 * 4) * 4u)))));
  }
  else {
    uVar1 = uVar3;
    if (uVar3 != 2) goto LAB_00073bee;
    if ((uint)*(ushort *)(((undefined *)camry_host_ptr((uint32_t)(0x275b0u + (uint32_t)(param_1 * 0x10) * 1u)))) <= (uint)nvm_operation_step)
    goto LAB_00073bee;
    pcVar4 = (uint32_t)(camry_host_addr(*((code * *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x275b4u + (uint32_t)(param_1 * 4) * 4u)))) + (uint)nvm_operation_step * 4)))));
  }
  uVar1 = (*(int (*)())camry_indirect((uint32_t)(pcVar4)))(param_1);
LAB_00073bee:
  nvm_poll_selected_service_73eda();
  iVar2 = (camry_r10_result = dispatch_nvm_operation_step_or_phase_eight_callback_73b46(param_1,uVar1));
  if ((uVar3 != 1) && (iVar2 == 1)) {
    nvm_pending_operation.operation = 0xffffffff;
  }
  nvm_operation_phase = (ushort)iVar2;
  return camry_r10_result;
}

void nvm_poll_pending_operation_73c14(void)

{
  uint uVar1;
  
  if (nvm_operation_state == '\x02') {
    uVar1 = lookup_u32_pair_value_or_default_73a5c(nvm_pending_operation.operation,(int)0xffffffff,((undefined *)camry_host_ptr(0x2758cu)));
    if (uVar1 < 2) {
      nvm_dispatch_operation_phase_73ba0(uVar1);
    }
    else {
      record_nvm_integrity_fault_72130();
    }
  }
  return;
}

void nvm_cancel_logical_operation(void)

{
  nvm_cancel_physical_operation();
  if (nvm_operation_state == '\x02') {
    nvm_operation_phase = 8;
  }
  return;
}

uchar nvm_get_operation_state_u8_73c6c(void)

{
  return nvm_operation_state;
}

undefined1 nvm_map_operation_state_two_to_two_else_one_73c76(void)

{
  undefined1 uVar1;
  
  if (nvm_operation_state == '\x02') {
    uVar1 = 2;
  }
  else {
    uVar1 = 1;
  }
  return uVar1;
}

void return_only_stub_73c86(void)

{
  return;
}

undefined4 nvm_submit_logical_read_to_physical_73cb0(ushort param_1,undefined4 param_2,undefined2 param_3,undefined4 param_4,
                 undefined2 param_5)

{
  uint uVar1;
  
  uVar1 = nvm_storage_handle(param_1);
  change_nvm_category_state_four_to_one_720f0(4);
  return ((void)(param_5), nvm_request_record_read_mode2_76572(uVar1, param_3, param_4));
}

undefined4 nvm_submit_logical_write_to_physical_73cdc(ushort param_1,undefined4 param_2,undefined4 param_3)

{
  uint uVar1;
  
  uVar1 = nvm_storage_handle(param_1);
  change_nvm_category_state_four_to_one_720f0(4);
  return nvm_request_record_write_mode1_765fc(uVar1,param_3);
}

undefined4 nvm_start_pending_read_73cfe(void)

{
  int iVar1;
  undefined4 uVar2;
  
  iVar1 = nvm_submit_logical_read_to_physical_73cb0((uint)nvm_pending_operation.logical_handle,0,0,
                       nvm_pending_operation.buffer_08,
                       (*((volatile uint16_t *)camry_host_ptr((uint32_t)((uint32_t)(0x26c0cu + (uint32_t)(nvm_pending_operation.logical_handle) * (uint32_t)sizeof(F33NvmLogicalDescriptor)) + (uint32_t)(0) * (uint32_t)sizeof(F33NvmLogicalDescriptor) + (uint32_t)offsetof(F33NvmLogicalDescriptor, payload_bytes))))));
  if (iVar1 == 0) {
    change_nvm_category_state_four_to_one_720f0(0);
    change_nvm_category_state_four_to_one_720f0(1);
    change_nvm_category_state_four_to_one_720f0(7);
    uVar2 = 4;
    nvm_operation_step = 0;
  }
  else {
    uVar2 = 1;
    set_nvm_category_state_two_72108(4);
    nvm_operation_state = '\x01';
  }
  return uVar2;
}

void nvm_publish_read_attempt_flags_73d5a(void)

{
  uint8_t stack_record_c[12];
  uint uVar1;
  
  (*((uint16_t *)(stack_record_c + 2))) = 0xffff;
  stack_record_c[0] = 0xff;
  stack_record_c[1] = -1;
  uVar1 = nvm_get_attempt_snapshot_and_flags_769a6(((uint16_t *)((stack_record_c + 2))),((uint8_t *)(stack_record_c)),((int8_t *)((stack_record_c + 1))));
  if ((uVar1 & 1) != 0) {
    set_nvm_category_state_two_72108(4);
  }
  if ((uVar1 >> 1 & 1) != 0) {
    set_nvm_category_state_two_72108(7);
  }
  if ((stack_record_c[1] == '\x01') && (change_nvm_category_state_four_to_one_720f0(2), (uVar1 >> 3 & 1) != 0)) {
    set_nvm_category_state_two_72108(2);
  }
  return;
}

ushort nvm_finish_pending_read_73daa(void)

{
  ushort uVar1;
  ushort uVar2;
  uchar uVar3;
  int iVar4;
  
  uVar1 = nvm_pending_operation.logical_handle;
  ((void)(nvm_pending_operation.logical_handle), nvm_publish_read_attempt_flags_73d5a());
  uVar2 = nvm_operation_phase;
  iVar4 = ((void)(uVar1), thunk_nvm_get_physical_result_state_766c6());
  uVar3 = '\0';
  if (iVar4 != 0) {
    if (iVar4 == 1) {
      set_nvm_category_state_two_72108(0);
      set_nvm_category_state_two_72108(4);
      uVar3 = '\x01';
    }
    else {
      if (iVar4 != 4) {
        return uVar2;
      }
      set_nvm_category_state_two_72108(0);
      set_nvm_category_state_two_72108(1);
      uVar3 = '\x03';
    }
  }
  nvm_operation_state = uVar3;
  nvm_operation_step = 0xffff;
  return 1;
}

undefined4 nvm_start_pending_write_73e0e(void)

{
  int iVar1;
  undefined4 uVar2;
  
  iVar1 = nvm_submit_logical_write_to_physical_73cdc(nvm_pending_operation.logical_handle,0,
                       nvm_pending_operation.buffer_0c);
  if (iVar1 == 0) {
    change_nvm_category_state_four_to_one_720f0(0);
    change_nvm_category_state_four_to_one_720f0(5);
    uVar2 = 4;
    nvm_operation_step = 0;
  }
  else {
    uVar2 = 1;
    set_nvm_category_state_two_72108(4);
    nvm_operation_state = '\x01';
  }
  return uVar2;
}

void nvm_publish_write_attempt_flags_73e54(void)

{
  uint8_t stack_record_c[12];
  uint uVar1;
  
  (*((uint16_t *)(stack_record_c + 2))) = 0xffff;
  stack_record_c[0] = 0xff;
  stack_record_c[1] = 0xff;
  uVar1 = nvm_get_attempt_snapshot_and_flags_769a6(((uint16_t *)((stack_record_c + 2))),((uint8_t *)(stack_record_c)),((uint8_t *)((stack_record_c + 1))));
  if ((uVar1 & 1) != 0) {
    set_nvm_category_state_two_72108(4);
  }
  if ((uVar1 >> 2 & 1) != 0) {
    set_nvm_category_state_two_72108(5);
  }
  return;
}

ushort nvm_finish_pending_write_73e8a(void)

{
  ushort uVar1;
  ushort uVar2;
  uchar uVar3;
  int iVar4;
  
  uVar1 = nvm_pending_operation.logical_handle;
  ((void)(nvm_pending_operation.logical_handle), nvm_publish_write_attempt_flags_73e54());
  uVar2 = nvm_operation_phase;
  iVar4 = ((void)(uVar1), thunk_nvm_get_physical_result_state_766c6());
  uVar3 = '\0';
  if (iVar4 != 0) {
    if (iVar4 != 1) {
      return uVar2;
    }
    set_nvm_category_state_two_72108(0);
    set_nvm_category_state_two_72108(4);
    uVar3 = '\x01';
  }
  nvm_operation_state = uVar3;
  nvm_operation_step = 0xffff;
  return 1;
}

void nvm_poll_selected_service_73eda(void)

{
  (*(int (*)())camry_indirect((uint32_t)(nvm_selected_service_poll)))();
  return;
}

void nvm_set_service_poll(uchar full_service)

{
  nvm_selected_service_poll = full_service == '\0' ? 0x766f4u : 0x767eau;
  return;
}

void nvm_initialize_logical_module(void)

{
  clear_shared_countdown_if_configured_7477a();
  nvm_initialize_logical_cells();
  return_only_stub_745bc();
  return_only_stub_745be();
  nvm_clear_buffer_overrides_745c8();
  set_nvm_diagnostic_state_f0_71d7c();
  nvm_initialize_operation();
  thunk_reset_nvm_scheduler_state_7217e();
  nvm_initialize_queues();
  return_only_stub_72e2c();
  return_only_stub_741ea();
  invoke_noop_halfword_hook_79462(0x14);
  return;
}

undefined4 nvm_set_logical_write_inhibit_checked_73f4e(undefined2 param_1,char param_2)

{
  undefined1 uVar1;
  int iVar2;
  undefined4 uVar3;
  
  uVar3 = 1;
  iVar2 = nvm_validate_write_inhibit_update_742a2((uint)(ushort)param_1, (uint)(byte)param_2);
  if (iVar2 == 0) {
    if (param_2 == '\x01') {
      uVar1 = 1;
    }
    else {
      uVar1 = 2;
    }
    set_nvm_logical_write_inhibit_71ce2(param_1,uVar1);
    uVar3 = 0;
  }
  return uVar3;
}

uint nvm_get_logical_result_checked_73f78(ushort param_1,uchar *param_2)

{
  int iVar1;
  uint uVar2;
  
  uVar2 = 1;
  iVar1 = nvm_validate_logical_result_output_7430c((uint)(ushort)param_1, camry_host_addr(param_2));
  if (iVar1 == 0) {
    uVar2 = nvm_read_logical_result(param_1,param_2);
  }
  return uVar2;
}

int nvm_copy_four_configuration_halfwords_checked_73f9c(undefined2 *param_1)

{
  undefined2 uVar1;
  uint32_t puVar2;
  int iVar3;
  undefined2 *puVar4;
  uint32_t puVar5;
  
  puVar2 = 0x23dfcu;
  iVar3 = nvm_validate_configuration_output_pointer_7435a((undefined4)param_1);
  if (iVar3 == 0) {
    puVar5 = ((uint32_t)(puVar2 + 0x37e0));
    puVar4 = ((undefined2 *)camry_host_ptr((uint32_t)(puVar2 + 0x37d8)));
    do {
      uVar1 = *puVar4;
      puVar4 = puVar4 + 1;
      *param_1 = uVar1;
      param_1 = param_1 + 1;
    } while (puVar5 !=camry_host_addr(puVar4));
  }
  return iVar3;
}

undefined4 nvm_remove_queued_logical_operation_checked_73fc8(undefined2 param_1)

{
  int iVar1;
  undefined4 uVar2;
  
  uVar2 = 1;
  iVar1 = nvm_validate_queue_removal_handle_7436e((uint)(ushort)param_1);
  if (iVar1 == 0) {
    uVar2 = remove_unscheduled_nvm_handle_and_publish_six_72f44(param_1);
  }
  return uVar2;
}
