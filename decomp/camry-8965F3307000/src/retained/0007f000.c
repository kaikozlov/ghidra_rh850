#include "common.h"

undefined4 read_record_4914_output_token_pair_7f052(uint param_1,undefined2 *param_2,undefined1 *param_3)

{
  undefined4 uVar1;
  undefined1 uVar2;
  undefined2 uVar3;
  
  if (*(short *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe4914u + (uint32_t)((param_1 & 0xff) * 8) * 1u)))) == 0x1fe) {
    uVar2 = 0;
    uVar3 = 0x1fe;
  }
  else {
    if (*(short *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe4914u + (uint32_t)((param_1 & 0xff) * 8) * 1u)))) != 0x2fd) {
      return 1;
    }
    uVar3 = 0x4fb;
    uVar2 = 3;
  }
  uVar1 = call_interrupt_guard_and_return_zero_7a2da();
  *param_2 = uVar3;
  *param_3 = uVar2;
  ((void)(uVar1), thunk_pop_and_restore_priority_mask_stack_6a4c4());
  return 0;
}

void decrement_record_4916_timer_clamped_7f098(uint param_1)

{
  int iVar1;
  int iVar2;
  ushort uVar3;
  
  iVar1 = (param_1 & 0xff) * 8;
  uVar3 = *(ushort *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe4916u + (uint32_t)(iVar1) * 1u))));
  if (uVar3 != 0) {
    iVar2 = (param_1 & 0xff) * 2;
    uVar3 = uVar3 - 1;
    if (*(ushort *)(((undefined *)camry_host_ptr((uint32_t)(0x21b8cu + (uint32_t)(iVar2) * 1u)))) < uVar3) {
      uVar3 = *(ushort *)(((undefined *)camry_host_ptr((uint32_t)(0x21b8cu + (uint32_t)(iVar2) * 1u))));
    }
  }
  *(ushort *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe4916u + (uint32_t)(iVar1) * 1u)))) = uVar3;
  return;
}

void expire_record_timer_and_notify_7f0c6(uint param_1)

{
  int iVar1;
  
  param_1 = param_1 & 0xff;
  iVar1 = param_1 * 8;
  if ((*(short *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe4916u + (uint32_t)(iVar1) * 1u)))) == 0) &&
     ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe491bu + (uint32_t)(iVar1) * 1u)))) = 0xe1, ((int8_t)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe4918u + (uint32_t)(iVar1) * 1u))))) != -0x10)) {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe4918u + (uint32_t)(iVar1) * 1u)))) = 0xf0;
    refresh_network_policy_and_boolean_indication_7c060(param_1);
    set_offset_network_indication_three_83298(param_1);
  }
  return;
}

void reset_or_expire_eight_byte_record_7f100(uint param_1)

{
  int iVar1;
  char cVar2;
  uint uVar3;
  
  param_1 = param_1 & 0xff;
  iVar1 = param_1 * 8;
  uVar3 = (uint)DAT_00021b8f;
  if (((int8_t)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe4919u + (uint32_t)(iVar1) * 1u))))) == -0x1f) {
    expire_record_timer_and_notify_7f0c6(param_1);
  }
  else {
    cVar2 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe491bu + (uint32_t)(iVar1) * 1u))));
    *(undefined2 *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe4916u + (uint32_t)(iVar1) * 1u)))) = 0;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe491au + (uint32_t)(iVar1) * 1u)))) = 0xf0;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe4918u + (uint32_t)(iVar1) * 1u)))) = 0xf0;
    *(undefined2 *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe4914u + (uint32_t)(iVar1) * 1u)))) = 0x1fe;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe491bu + (uint32_t)(iVar1) * 1u)))) = 0xf0;
    if (((int8_t)cVar2) != -0x10) {
      refresh_network_policy_and_boolean_indication_7c060(param_1);
      set_offset_network_indication_one_83282(param_1);
    }
    clear_offset_network_indication_and_disable_packets_832ae(param_1);
    reset_valid_active_record_state_ff_wrapper_7ef5c(uVar3 + param_1 & 0xff);
  }
  return;
}

void update_record_enable_timer_and_state_2fd_7f15e(uint param_1)

{
  int iVar1;
  char cVar2;
  undefined2 uVar3;
  uint32_t puVar4;
  int iVar5;
  uint uVar6;
  char cVar7;
  
  puVar4 = 0x23dfcu;
  param_1 = param_1 & 0xff;
  iVar1 = param_1 * 8;
  cVar7 = -0x10;
  cVar2 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe491au + (uint32_t)(iVar1) * 1u))));
  uVar6 = DAT_00021b8f + param_1 & 0xff;
  iVar5 = test_record_mask_against_global_493a_7e7e4(uVar6);
  if (iVar5 == 1) {
    cVar7 = -0x1f;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe491au + (uint32_t)(iVar1) * 1u)))) = cVar7;
  if (cVar2 != cVar7) {
    if (((int8_t)cVar7) == -0x1f) {
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe4918u + (uint32_t)(iVar1) * 1u)))) = 0xe1;
      uVar3 = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar4 + param_1 * 2 + -0x2270))));
    }
    else {
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe4918u + (uint32_t)(iVar1) * 1u)))) = 0xf0;
      uVar3 = 0;
    }
    *(undefined2 *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe4916u + (uint32_t)(iVar1) * 1u)))) = uVar3;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe491bu + (uint32_t)(iVar1) * 1u)))) = 0xf0;
  if (((int8_t)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe4919u + (uint32_t)(iVar1) * 1u))))) == -0x1f) {
    transition_valid_record_3fc_to_2fd_wrapper_7ef30(uVar6);
    set_offset_network_indication_one_and_notify_832c4(param_1);
    expire_record_timer_and_notify_7f0c6(param_1);
    *(undefined2 *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe4914u + (uint32_t)(iVar1) * 1u)))) = 0x2fd;
  }
  return;
}

void dispatch_eight_byte_record_state_7f1e2(uint param_1)

{
  if (*(short *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe4914u + (uint32_t)((param_1 & 0xff) * 8) * 1u)))) == 0x1fe) {
    update_record_enable_timer_and_state_2fd_7f15e((uint)(byte)param_1);
  }
  else if (*(short *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe4914u + (uint32_t)((param_1 & 0xff) * 8) * 1u)))) == 0x2fd) {
    reset_or_expire_eight_byte_record_7f100((uint)(byte)param_1);
  }
  return;
}

void tick_selected_eight_byte_records_7f20c(void)

{
  undefined8 uVar1;
  uint uVar2;
  uint uVar3;
  
  uVar1 = 0x23dfc00000000;
  uVar2 = (uint)DAT_00021b8e;
  for (uVar3 = 0; uVar3 < uVar2; uVar3 = uVar3 + 1 & 0xff) {
    if ((*((char *)camry_host_ptr((uint32_t)(uVar3 + (int)((ulonglong)uVar1 >> 0x20) + -0x226c)))) == '\0') {
      decrement_record_4916_timer_clamped_7f098(uVar3);
      dispatch_eight_byte_record_state_7f1e2(uVar3);
    }
  }
  return;
}

void broadcast_21b70_callback_slot_zero_7f250(undefined4 param_1)

{
  undefined8 uVar1;
  uint uVar2;
  uint uVar3;
  
  uVar1 = 0x23dfc00000000;
  uVar2 = (uint)DAT_00021b09;
  for (uVar3 = 0; uVar3 < uVar2; uVar3 = uVar3 + 1 & 0xff) {
    (*(int (*)())camry_indirect((uint32_t)(*(((undefined4 *)camry_host_ptr((*((volatile uint32_t *)camry_host_ptr((uint32_t)(uVar3 * 4 + (int)((ulonglong)uVar1 >> 0x20) + -0x228c))))))))))(param_1);
  }
  return;
}

void broadcast_21b70_callback_slot_four_7f27c(void)

{
  undefined8 uVar1;
  uint uVar2;
  uint uVar3;
  
  uVar1 = 0x23dfc00000000;
  uVar2 = (uint)DAT_00021b09;
  for (uVar3 = 0; uVar3 < uVar2; uVar3 = uVar3 + 1 & 0xff) {
    (*(int (*)())camry_indirect((uint32_t)(((((code *)(uintptr_t)((uint32_t)((uintptr_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)((*((int *)camry_host_ptr((uint32_t)(uVar3 * 4 + (int)((ulonglong)uVar1 >> 0x20) + -0x228c)))) + 4)))))))))))))();
  }
  return;
}

void dispatch_offset_record_callback_slot_sixteen_7f2a4(int param_1)

{
  (*(int (*)())camry_indirect((uint32_t)(*((code * *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x21b70u + (uint32_t)((byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x21b0bu + (uint32_t)(param_1 - (uint)DAT_00021b08 & 0xff) * 1u))))) * 4u)))) +
              0x10))))))((uint)(byte)param_1);
  return;
}

void dispatch_offset_record_callback_slot_twenty_7f2ca(int param_1)

{
  (*(int (*)())camry_indirect((uint32_t)(*((code * *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x21b70u + (uint32_t)((byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x21b0bu + (uint32_t)(param_1 - (uint)DAT_00021b08 & 0xff) * 1u))))) * 4u)))) +
              0x14))))))((uint)(byte)param_1);
  return;
}

void dispatch_offset_record_callback_slot_twenty_four_7f2f0(int param_1)

{
  (*(int (*)())camry_indirect((uint32_t)(*((code * *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x21b70u + (uint32_t)((byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x21b0bu + (uint32_t)(param_1 - (uint)DAT_00021b08 & 0xff) * 1u))))) * 4u)))) +
              0x18))))))((uint)(byte)param_1);
  return;
}

void dispatch_offset_record_callback_slot_twenty_eight_7f316(int param_1)

{
  (*(int (*)())camry_indirect((uint32_t)(*((code * *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x21b70u + (uint32_t)((byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x21b0bu + (uint32_t)(param_1 - (uint)DAT_00021b08 & 0xff) * 1u))))) * 4u)))) +
              0x1c))))))((uint)(byte)param_1);
  return;
}

void broadcast_21b00_callback_slot_eight_7f33c(void)

{
  undefined8 uVar1;
  uint uVar2;
  uint uVar3;
  
  uVar1 = 0x23dfc00000000;
  uVar2 = (uint)DAT_00021b0a;
  for (uVar3 = 0; uVar3 < uVar2; uVar3 = uVar3 + 1 & 0xff) {
    (*(int (*)())camry_indirect((uint32_t)(((((code *)(uintptr_t)((uint32_t)((uintptr_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)((*((int *)camry_host_ptr((uint32_t)(uVar3 * 4 + (int)((ulonglong)uVar1 >> 0x20) + -0x22fc)))) + 8)))))))))))))();
  }
  return;
}

void return_only_stub_7f364(void)

{
  return;
}

int dispatch_record_callback_slot_twelve_21b70_7f366(uint param_1)

{
  return (*(int (*)())camry_indirect((uint32_t)(((((code *)(uintptr_t)((uint32_t)((uintptr_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x21b70u + (uint32_t)((byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x21b0bu + (uint32_t)(param_1 & 0xff) * 1u))))) * 4u)))) + 0xc))))))))))))((uint)(byte)param_1);
}

void dispatch_record_callback_slot_thirty_six_7f386(uint param_1)

{
  (*(int (*)())camry_indirect((uint32_t)(((((code *)(uintptr_t)((uint32_t)((uintptr_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x21b70u + (uint32_t)((byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x21b0bu + (uint32_t)(param_1 & 0xff) * 1u))))) * 4u)))) + 0x24))))))))))))((uint)(byte)param_1);
  return;
}

int dispatch_record_callback_slot_thirty_two_7f3a6(uint param_1)

{
  return (*(int (*)())camry_indirect((uint32_t)(((((code *)(uintptr_t)((uint32_t)((uintptr_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x21b70u + (uint32_t)((byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x21b0bu + (uint32_t)(param_1 & 0xff) * 1u))))) * 4u)))) + 0x20))))))))))))((uint)(byte)param_1);
}

int dispatch_masked_u16_callback_slot_forty_7f3f8(ushort param_1)

{
  uint32_t puVar1;
  int iVar2;
  
  puVar1 = 0x23dfcu;
  iVar2 = lookup_base_bank_controller_byte_or_ff_8144e((uint)(ushort)param_1);
  (*(int (*)())camry_indirect((uint32_t)(((((code *)(uintptr_t)((uint32_t)((uintptr_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)((*((int *)camry_host_ptr((uint32_t)(puVar1 + (uint)(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(iVar2 + -0x22f1))))) * 4 + -0x228c)))) + 0x28)))))))))))))((param_1 & 0x9fff) - (ushort)(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(iVar2 + -0x22ef))))),iVar2);
  ((void)(param_1), (void)((uint)(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x22f4))))) + iVar2 & 0xff), (void)(0), (void)(1), return_only_stub_8356e());
  return iVar2;
}

void dispatch_u16_callback_slot_forty_four_7f444(undefined2 param_1,undefined4 param_2)

{
  uint32_t puVar1;
  int iVar2;
  
  puVar1 = 0x23dfcu;
  iVar2 = lookup_extended_bank_record_byte_or_ff_813e4((uint)(ushort)param_1);
  (*(int (*)())camry_indirect((uint32_t)(*((code * *)camry_host_ptr((uint32_t)((*((volatile int32_t *)camry_host_ptr((uint32_t)(puVar1 + (uint)(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(iVar2 + -0x22f1))))) * 4 + -0x228c)))) + 0x2c))))))(param_1,iVar2,param_2);
  ((void)(param_1), (void)((uint)(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x22f4))))) + iVar2 & 0xff), (void)(param_2), (void)(2), return_only_stub_8356e());
  return;
}

void change_controller_cache_6b94_to_57a8_7f486(uint param_1)

{
  if ((*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe48d8u + (uint32_t)(param_1 & 0xff) * 2u)))) == 0x6b94) {
    request_stop_on_matching_controller_channels_7fb60((uint)(byte)param_1);
    (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe48d8u + (uint32_t)(param_1 & 0xff) * 2u)))) = 0x57a8;
  }
  return;
}

void set_controller_cache_6b94_and_start_channels_7f4b0(uint param_1)

{
  camry_write32((camry_sp - 4u) & ~3u, camry_gpr[31]);
  camry_sp -= 4u;
  camry_gpr[3] = camry_sp;

  ushort uVar1;
  
  uVar1 = (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe48d8u + (uint32_t)(param_1 & 0xff) * 2u))));
  if ((uVar1 == 0x57a8) || (uVar1 == 0x6b94)) {
    (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe48d8u + (uint32_t)(param_1 & 0xff) * 2u)))) = 0x6b94;
  }
  (camry_gpr[6] = param_1 & 0xffu, camry_gpr[31] = 0x7f4d8u, request_start_on_matching_controller_channels_7f882)((uint)(byte)param_1);
  { if (!camry_halted) { camry_gpr[31] = camry_read32((camry_sp + 0u) & ~3u); camry_sp += 4u; camry_gpr[3] = camry_sp; } return; }
}

uint request_logical_controller_run_stop(uchar logical_controller,uchar requested_mode)

{
  camry_write32((camry_sp - 4u) & ~3u, camry_gpr[31]);
  camry_sp -= 4u;
  camry_gpr[3] = camry_sp;

  if (requested_mode == '\x02') {
    (camry_gpr[6] = logical_controller, camry_r7 = camry_gpr[7] = requested_mode, camry_gpr[31] = 0x7f4ecu, change_controller_cache_6b94_to_57a8_7f486)((uint)(byte)logical_controller);
  }
  else {
    if (requested_mode != '\x03') {
      { uint32_t camry_return_value = (1); if (camry_halted) return 0; camry_gpr[31] = camry_read32((camry_sp + 0u) & ~3u); camry_sp += 4u; camry_gpr[3] = camry_sp; return camry_return_value; }
    }
    (camry_gpr[6] = logical_controller, camry_r7 = camry_gpr[7] = requested_mode, camry_gpr[10] = 1u, camry_gpr[31] = 0x7f4f8u, set_controller_cache_6b94_and_start_channels_7f4b0)(logical_controller);
  }
  { uint32_t camry_return_value = (0); if (camry_halted) return 0; camry_gpr[31] = camry_read32((camry_sp + 0u) & ~3u); camry_sp += 4u; camry_gpr[3] = camry_sp; return camry_return_value; }
}

bool check_controller_request_mode_and_release_7f4fe(uint param_1,char param_2)

{
  ushort uVar1;
  undefined4 uVar2;
  int iVar3;
  int iVar4;
  
  param_1 = param_1 & 0xff;
  iVar4 = 1;
  uVar1 = (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe48d8u + (uint32_t)(param_1) * 2u))));
  if (param_2 == '\0') {
    if (uVar1 == 0x6b94) {
      iVar4 = ((void)(param_1), return_const_1_8158a());
    }
  }
  else if ((param_2 == '\x02') && ((uVar1 == 0x57a8 || (uVar1 == 0x6b94)))) {
    uVar2 = call_interrupt_guard_and_return_zero_duplicate_7a2f4();
    iVar3 = test_matching_channel_stub_returns_zero_7f6a4(param_1);
    iVar4 = ((void)(param_1), (void)(2), return_const_1_8158a());
    if (iVar3 != 1) {
      call_stub_83596_for_matching_channels_812be(param_1);
    }
    ((void)(uVar2), thunk_pop_and_restore_priority_mask_stack_6a4c4());
  }
  return iVar4 != 0;
}

undefined4 test_cached_controller_matching_channel_status_7f56a(uint param_1)

{
  uint32_t puVar1;
  int iVar2;
  uint uVar3;
  uint uVar4;
  
  puVar1 = 0x23dfcu;
  if (((*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe48d8u + (uint32_t)(param_1 & 0xff) * 2u)))) == 0x57a8) ||
     ((*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe48d8u + (uint32_t)(param_1 & 0xff) * 2u)))) == 0x6b94)) {
    uVar3 = (uint)DAT_00021971;
    for (uVar4 = 0; uVar4 < uVar3; uVar4 = uVar4 + 1 & 0xff) {
      if (((param_1 & 0xff) == (uint)(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(uVar4 - 0x2484)))))) &&
         (iVar2 = is_channel_outside_states_6d92_and_6b94_841fc(uVar4), iVar2 != 0)) {
        return 1;
      }
    }
  }
  return 0;
}

void reload_controller_indexed_u16_counter_7f5ba(uint param_1,uint param_2)

{
  (*((undefined2 *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x21934u + (uint32_t)(param_1 & 0xff) * 4u)))) + (param_2 & 0xff) * 2)))) =
       *(undefined2 *)(((undefined *)camry_host_ptr((uint32_t)(0x2196au + (uint32_t)((param_1 & 0xff) * 2) * 1u))));
  return;
}

void zero_controller_indexed_u16_counter_7f5da(uint param_1,uint param_2)

{
  (*((undefined2 *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x21934u + (uint32_t)(param_1 & 0xff) * 4u)))) + (param_2 & 0xff) * 2)))) = 0;
  return;
}

int decrement_controller_counters_until_expiry_7f5f0(uint param_1)

{
  int iVar1;
  byte bVar2;
  short sVar3;
  uint32_t puVar4;
  undefined4 uVar5;
  int iVar6;
  uint uVar7;
  
  puVar4 = 0x23dfcu;
  param_1 = param_1 & 0xff;
  iVar1 = param_1 * 2;
  iVar6 = 0;
  if (((((*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe48d8u + (uint32_t)(param_1) * 2u)))) == 0x57a8) &&
       (*(short *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe48feu + (uint32_t)(iVar1) * 1u)))) == 0x5555)) && ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x21972u + (uint32_t)(param_1) * 1u)))) != '\0')) &&
     (*(short *)(((undefined *)camry_host_ptr((uint32_t)(0x2196au + (uint32_t)(iVar1) * 1u)))) != 0)) {
    bVar2 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x21973u + (uint32_t)(param_1) * 1u))));
    uVar7 = 0;
    while ((uVar7 < bVar2 && (iVar6 == 0))) {
      uVar5 = call_interrupt_guard_and_return_zero_7a2da();
      sVar3 = (*((short *)camry_host_ptr((uint32_t)((*((volatile int32_t *)camry_host_ptr((uint32_t)(puVar4 + param_1 * 4 + -0x24c8)))) + uVar7 * 2))));
      if (sVar3 != 0) {
        sVar3 = sVar3 + -1;
      }
      if (((*((char *)camry_host_ptr((uint32_t)((*((volatile int32_t *)camry_host_ptr((uint32_t)(puVar4 + param_1 * 4 + -0x2514)))) + uVar7)))) != 'i') && (sVar3 == 0)) {
        iVar6 = 1;
        *(ushort *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe48feu + (uint32_t)(iVar1) * 1u)))) = *(ushort *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe48feu + (uint32_t)(iVar1) * 1u)))) & 0xfff3 | 8;
      }
      (*((short *)camry_host_ptr((uint32_t)((*((volatile int32_t *)camry_host_ptr((uint32_t)(puVar4 + param_1 * 4 + -0x24c8)))) + uVar7 * 2)))) = sVar3;
      ((void)(uVar5), thunk_pop_and_restore_priority_mask_stack_6a4c4());
      uVar7 = uVar7 + 1 & 0xff;
    }
  }
  return iVar6;
}

undefined4 test_matching_channel_stub_returns_zero_7f6a4(char param_1)

{
  undefined8 uVar1;
  int iVar2;
  uint uVar3;
  uint uVar4;
  
  uVar1 = 0x23dfc00000000;
  uVar3 = (uint)DAT_00021971;
  uVar4 = 0;
  while( true ) {
    if (uVar3 <= uVar4) {
      return 0;
    }
    if ((param_1 == (*((char *)camry_host_ptr((uint32_t)(uVar4 + (int)((ulonglong)uVar1 >> 0x20) + -0x2484))))) &&
       (iVar2 = ((void)(uVar4), return_const_1_83598()), iVar2 == 0)) break;
    uVar4 = uVar4 + 1 & 0xff;
  }
  return 1;
}

void initialize_controller_request_tokens_and_bytes_7f75a(void)

{
  int iVar1;
  undefined8 uVar2;
  int iVar3;
  uint uVar4;
  uint uVar5;
  
  uVar2 = 0x23dfcfebeb800;
  uVar4 = (uint)DAT_00021970;
  for (uVar5 = 0; uVar5 < uVar4; uVar5 = uVar5 + 1 & 0xff) {
    (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe48d8u + (uint32_t)(uVar5) * 2u)))) = 0x6e91;
  }
  (*(int (*)())camry_indirect((uint32_t)(PTR_FUN_000218f0)))();
  initialize_all_message_ring_storage_80bc2();
  for (uVar5 = 0; uVar5 < uVar4; uVar5 = uVar5 + 1 & 0xff) {
    (*(int (*)())camry_indirect((uint32_t)(((((code *)(uintptr_t)((uint32_t)((uintptr_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)((int)((ulonglong)uVar2 >> 0x20) + -0x24c4)))))))))))))(uVar5);
    initialize_controller_status_by_mode_80e32(uVar5,0);
    iVar1 = uVar5 + (int)uVar2;
    (*((undefined1 *)camry_host_ptr((uint32_t)(iVar1 + -0x6efd)))) = 0x69;
    (*((undefined1 *)camry_host_ptr((uint32_t)(iVar1 + -0x6f00)))) = 0x69;
    iVar3 = (int)((ulonglong)uVar2 >> 0x20);
    (*((undefined1 *)camry_host_ptr((uint32_t)(iVar1 + -0x6eff)))) = (*((undefined1 *)camry_host_ptr((uint32_t)(iVar3 + -0x2485))));
    (*((undefined1 *)camry_host_ptr((uint32_t)(iVar1 + -0x6efe)))) = (*((undefined1 *)camry_host_ptr((uint32_t)(iVar3 + -0x2486))));
  }
  for (uVar5 = 0; uVar5 < uVar4; uVar5 = uVar5 + 1 & 0xff) {
    (*((undefined2 *)camry_host_ptr((uint32_t)(uVar5 * 2 + (int)uVar2 + -0x6f28)))) = 0x6d92;
  }
  return;
}

char resolve_69_token_from_channel_results_7f7e4(char param_1,char param_2)

{
  undefined8 uVar1;
  uint uVar2;
  uint uVar3;
  uint uVar4;
  uint uVar5;
  
  uVar1 = 0x23dfc00000000;
  if (param_2 == 'i') {
    uVar3 = (uint)DAT_00021971;
    uVar4 = 0;
    for (uVar5 = 0; uVar5 < uVar3; uVar5 = uVar5 + 1 & 0xff) {
      if (param_1 == (*((char *)camry_host_ptr((uint32_t)(uVar5 + (int)((ulonglong)uVar1 >> 0x20) + -0x2484))))) {
        uVar2 = ((void)(0), configure_channel_and_advance_state_to_6b94_83f9a(uVar5));
        uVar4 = uVar4 | uVar2;
      }
    }
    if (uVar4 == 0) {
      param_2 = -0x6a;
    }
    else {
      param_2 = -0x3d;
      if (uVar4 == 2) {
        param_2 = 'i';
      }
    }
  }
  return param_2;
}

char map_controller_result_to_request_token_7f838(undefined1 param_1,char param_2)

{
  int iVar1;
  
  if ((param_2 == -0x6a) || (param_2 == 'Z')) {
    iVar1 = aggregate_mapped_driver_status_priority_80eb0(param_1);
    if (iVar1 == 0) {
      param_2 = -0x5b;
    }
    else if (iVar1 == 2) {
      param_2 = 'Z';
    }
    else if (iVar1 == 1) {
      param_2 = '<';
    }
    else {
      param_2 = -0x3d;
      if (iVar1 == 3) {
        param_2 = '\x1e';
      }
    }
  }
  return param_2;
}

void request_start_on_matching_controller_channels_7f882(uint param_1)

{
  camry_write32((camry_sp - 4u) & ~3u, camry_gpr[27]);
  camry_write32((camry_sp - 8u) & ~3u, camry_gpr[28]);
  camry_write32((camry_sp - 12u) & ~3u, camry_gpr[29]);
  camry_write32((camry_sp - 16u) & ~3u, camry_gpr[31]);
  camry_sp -= 16u;
  camry_gpr[3] = camry_sp;

  uint32_t puVar1;
  uint32_t puVar2;
  uint uVar3;
  uint uVar4;
  uint32_t pcVar5;
  
  puVar1 = 0xfebeb800u;
  puVar2 = 0x23dfcu;
  param_1 = param_1 & 0xff;
  uVar3 = (uint)DAT_00021971;
  for (uVar4 = 0; uVar4 < uVar3; uVar4 = uVar4 + 1 & 0xff) {
    if (param_1 == (byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(uVar4 - 0x2484)))))) {
      (camry_gpr[27] = uVar3, camry_gpr[28] = param_1, camry_gpr[29] = uVar4, camry_gpr[6] = uVar4, camry_r7 = camry_gpr[7] = 1u, camry_gpr[31] = 0x7f8a6u, driver_request_channel_start_stop)((uchar)uVar4,'\x01');
    }
  }
  pcVar5 = (uint32_t)(camry_host_addr(*((code * *)camry_host_ptr((uint32_t)(puVar2 + -0x2500)))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(param_1 - 0x6efd))))) = 0x69;
  (*(int (*)())camry_indirect((camry_gpr[29] = (uint32_t)(uintptr_t)pcVar5, camry_gpr[6] = param_1, camry_gpr[31] = 0x7f8c4u, (uint32_t)(pcVar5))))(param_1);
  { if (!camry_halted) { camry_gpr[27] = camry_read32((camry_sp + 12u) & ~3u); camry_gpr[28] = camry_read32((camry_sp + 8u) & ~3u); camry_gpr[29] = camry_read32((camry_sp + 4u) & ~3u); camry_gpr[31] = camry_read32((camry_sp + 0u) & ~3u); camry_sp += 16u; camry_gpr[3] = camry_sp; } return; }
}

undefined4 advance_controller_request_with_retry_bytes_7f8c8(uint param_1,char param_2)

{
  byte *pbVar1;
  byte bVar2;
  byte bVar3;
  char cVar4;
  undefined8 uVar5;
  int iVar6;
  uint32_t pcVar7;
  undefined4 uVar8;
  undefined1 uVar9;
  
  bVar3 = DAT_00021977;
  uVar5 = 0x23dfcfebeb800;
  param_1 = param_1 & 0xff;
  cVar4 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe4912u + (uint32_t)(param_1) * 1u))));
  if ((*(ushort *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe48feu + (uint32_t)(param_1 * 2) * 1u)))) & 3) != 1) {
    store_controller_request_result_byte_80f5a(param_1,0x5a);
    return 1;
  }
  if (((int8_t)cVar4) == -0x4c) {
    return 8;
  }
  if (((int8_t)cVar4) == -0x5b) {
    return 9;
  }
  if (cVar4 == 'Z') {
    return 1;
  }
  iVar6 = resolve_69_token_from_channel_results_7f7e4(param_1,(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe4900u + (uint32_t)(param_1) * 1u)))));
  if (param_2 == '\x01') {
    iVar6 = map_controller_result_to_request_token_7f838(param_1,iVar6);
  }
  else if (iVar6 == 0x5a) {
    iVar6 = 0xa5;
  }
  if ((iVar6 == 0x69) || (iVar6 == 0x5a)) {
    pbVar1 = ((byte *)camry_host_ptr((uint32_t)((int)uVar5 + -0x6eff + param_1)));
    bVar2 = *pbVar1 - 1;
    if ((bVar3 <= bVar2) || (bVar2 == 0)) {
      iVar6 = 0xc3;
    }
    *pbVar1 = bVar2;
LAB_0007f9a4:
    if ((iVar6 != 0x69) && (iVar6 != 0x5a)) {
LAB_0007f9b4:
      if ((iVar6 == 0x96) || (iVar6 == 0xa5)) {
        uVar8 = 0;
      }
      else if (iVar6 == 0x3c) {
        request_start_on_matching_controller_channels_7f882(param_1);
        store_controller_request_result_byte_80f5a(param_1,0xb4);
        uVar8 = 8;
      }
      else if (iVar6 == 0x1e) {
        iVar6 = 0xa5;
        store_controller_request_result_byte_80f5a(param_1,0xa5);
        uVar8 = 9;
      }
      else {
        request_start_on_matching_controller_channels_7f882(param_1);
        store_controller_request_result_byte_80f5a(param_1,0x5a);
        uVar8 = 1;
      }
      uVar9 = (undefined1)iVar6;
      pcVar7 = (uint32_t)((uintptr_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)((int)((ulonglong)uVar5 >> 0x20) + -0x2508))))));
      (*((undefined1 *)camry_host_ptr((uint32_t)(param_1 + (int)uVar5 + -0x6efd)))) = 0x69;
      (*(int (*)())camry_indirect((uint32_t)(pcVar7)))(param_1);
      iVar6 = (int)((ulonglong)uVar5 >> 0x20);
      clear_configured_controller_ring_indices_80c20(param_1);
      (*(int (*)())camry_indirect((uint32_t)(((((code *)(uintptr_t)((uint32_t)((uintptr_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(iVar6 + -0x24c0))))))))))))(param_1);
      initialize_controller_status_by_mode_80e32(param_1,1);
      goto LAB_0007fa30;
    }
  }
  else {
    if (((iVar6 != 0x3c) && (iVar6 != 0x1e)) && (iVar6 != 0xc3)) goto LAB_0007f9b4;
    pbVar1 = ((byte *)camry_host_ptr((uint32_t)((int)uVar5 + -0x6efe + param_1)));
    bVar3 = *pbVar1;
    if (bVar3 < 2) goto LAB_0007f9a4;
    iVar6 = 0x69;
    *pbVar1 = bVar3 - 1;
  }
  uVar9 = (undefined1)iVar6;
  uVar8 = 2;
LAB_0007fa30:
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe4900u + (uint32_t)(param_1) * 1u)))) = uVar9;
  return uVar8;
}

undefined4 advance_controller_cache_from_6d92_7fa3a(uint param_1,undefined1 param_2)

{
  int iVar1;
  undefined4 uVar2;
  
  param_1 = param_1 & 0xff;
  uVar2 = 1;
  if ((*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe48d8u + (uint32_t)(param_1) * 2u)))) == 0x6d92) {
    (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe48d8u + (uint32_t)(param_1) * 2u)))) = 0x6d92;
    iVar1 = advance_controller_request_with_retry_bytes_7f8c8(param_1,param_2);
    if ((iVar1 == 0) || (iVar1 == 9)) {
      uVar2 = 0;
      (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe48d8u + (uint32_t)(param_1) * 2u)))) = 0x6b94;
    }
    else if (iVar1 == 2) {
      uVar2 = 2;
    }
    else {
      uVar2 = 1;
    }
  }
  return uVar2;
}

void reset_all_controller_request_callbacks_7fa80(void)

{
  uint32_t puVar1;
  uint32_t puVar2;
  uint uVar3;
  uint32_t pcVar4;
  uint uVar5;
  
  puVar1 = 0xfebeb800u;
  puVar2 = 0x23dfcu;
  uVar3 = (uint)DAT_00021970;
  for (uVar5 = 0; uVar5 < uVar3; uVar5 = uVar5 + 1 & 0xff) {
    pcVar4 = (uint32_t)((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)((puVar2 + -0x2508)))))));
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(uVar5 - 0x6efd))))) = 0x69;
    (*(int (*)())camry_indirect((uint32_t)(pcVar4)))(uVar5);
    clear_configured_controller_ring_indices_80c20(uVar5);
    (*(int (*)())camry_indirect((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)((puVar2 + -0x24c4))))))))(uVar5);
    initialize_controller_status_by_mode_80e32(uVar5,0);
  }
  return;
}

void set_all_controller_cache_6e91_and_reset_7fac6(void)

{
  uint uVar1;
  uint32_t puVar2;
  undefined4 uVar3;
  uint uVar4;
  
  puVar2 = 0xfebeb800u;
  uVar4 = (uint)DAT_00021970;
  uVar3 = call_interrupt_guard_and_return_zero_7a2da();
  for (uVar1 = 0; uVar1 < uVar4; uVar1 = uVar1 + 1 & 0xff) {
    (*((undefined2 *)camry_host_ptr((uint32_t)(puVar2 + uVar1 * 2 + -0x6f28)))) = 0x6e91;
  }
  ((void)(uVar3), thunk_pop_and_restore_priority_mask_stack_6a4c4());
  reset_all_controller_request_callbacks_7fa80();
  return;
}

undefined4 set_controller_cache_6b94_and_clear_channels_7fafa(uint param_1)

{
  uint32_t puVar1;
  uint32_t puVar2;
  uint uVar3;
  uint uVar4;
  uint32_t pcVar5;
  
  puVar1 = 0xfebeb800u;
  puVar2 = 0x23dfcu;
  param_1 = param_1 & 0xff;
  uVar3 = (uint)DAT_00021971;
  (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe48d8u + (uint32_t)(param_1) * 2u)))) = 0x6b94;
  for (uVar4 = 0; uVar4 < uVar3; uVar4 = uVar4 + 1 & 0xff) {
    if (param_1 == (byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(uVar4 - 0x2484)))))) {
      ((void)(0), reconfigure_channel_after_clearing_tx_routes_841a6(uVar4));
    }
  }
  pcVar5 = (uint32_t)(camry_host_addr(*((code * *)camry_host_ptr((uint32_t)(puVar2 + -0x2500)))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(param_1 - 0x6efd))))) = 0x69;
  (*(int (*)())camry_indirect((uint32_t)(pcVar5)))(param_1);
  clear_configured_controller_ring_indices_80c20(param_1);
  return initialize_controller_status_by_mode_80e32(param_1,2);
}

void return_only_stub_7fb5c(void)

{
  return;
}

uint32_t request_stop_on_matching_controller_channels_7fb60(char param_1)

{
  uint32_t camry_r10_result;
  byte bVar1;
  undefined8 uVar2;
  uint uVar3;
  
  uVar2 = 0x23dfc00000000;
  (*(int (*)())camry_indirect((uint32_t)(PTR_FUN_000218f8)))((uint)(byte)param_1);
  clear_configured_controller_ring_indices_80c20(param_1);
  (*(int (*)())camry_indirect((uint32_t)(*((code * *)camry_host_ptr((uint32_t)((int)((ulonglong)uVar2 >> 0x20) + -0x24bc))))))(param_1);
  (camry_r10_result = initialize_controller_status_by_mode_80e32(param_1,2));
  bVar1 = (*((byte *)camry_host_ptr((uint32_t)((int)((ulonglong)uVar2 >> 0x20) + -0x248b))));
  for (uVar3 = 0; uVar3 < bVar1; uVar3 = uVar3 + 1 & 0xff) {
    if (param_1 == (*((char *)camry_host_ptr((uint32_t)(uVar3 + (int)((ulonglong)uVar2 >> 0x20) + -0x2484))))) {
      (camry_r10_result = driver_request_channel_start_stop((uchar)uVar3,'\0'));
    }
  }
  return camry_r10_result;
}

undefined4 get_controller_cache_compact_state_7fbb0(uint param_1)

{
  ushort uVar1;
  
  uVar1 = (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe48d8u + (uint32_t)(param_1 & 0xff) * 2u))));
  if (uVar1 == 0x57a8) {
    return 3;
  }
  if (uVar1 != 0x6b94) {
    if (uVar1 != 0x6d92) {
      return 0;
    }
    return 1;
  }
  return 2;
}

uint translate_controller_encoded_index_or_ff_7fbdc(uint param_1,uint param_2)

{
  uint uVar1;
  uint uVar2;
  
  uVar2 = 0xff;
  if (((byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x2195cu + (uint32_t)((short)(param_1 & 0xff) * 6 + ((int)(param_2 & 0xffff) >> 8)) * 1u)))) != 0xff)
     && (uVar1 = (param_2 & 0xff) +
                 (uint)(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x2195cu + (uint32_t)((short)(param_1 & 0xff) * 6 + ((int)(param_2 & 0xffff) >> 8)) * 1u)))),
        uVar1 < (byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x21972u + (uint32_t)(param_1 & 0xff) * 1u)))))) {
    uVar2 = uVar1 & 0xff;
  }
  return uVar2;
}

uint enqueue_large_can_tx(F33CanIfTxRecord *record,ushort queue_index,ushort capacity_words)

{
  uint *puVar1;
  uchar *puVar2;
  uchar *puVar3;
  int iVar4;
  byte bVar5;
  uchar uVar6;
  uchar uVar7;
  uchar uVar8;
  ushort uVar9;
  uint uVar10;
  uint uVar11;
  uint uVar12;
  uint uVar13;
  uint uVar14;
  int iVar15;
  uint uVar16;
  undefined *puVar17;
  uchar *puVar18;
  uint uVar19;
  uint uVar20;
  uint uVar21;
  uint uVar22;
  uint uVar23;
  uint uVar24;
  
  uVar10 = (uint)queue_index;
  uVar11 = (uint)capacity_words;
  uVar13 = record->raw_id;
  uVar12 = 1;
  uVar20 = (uint)record->length;
  uVar14 = uVar13 & 0x40000000;
  if (uVar14 == 0) {
    uVar21 = 8;
  }
  else {
    uVar21 = uVar20;
    if (0x40 < uVar20) {
      uVar21 = 0x40;
    }
    uVar20 = (uint)(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x22d84u + (uint32_t)((int)(uVar21 - 1 & 0xff) >> 2) * 1u))));
  }
  uVar22 = (uint)(*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe48dau + (uint32_t)(uVar10 * 3) * 2u))));
  uVar24 = (uint)(*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe48dau + (uint32_t)(uVar10 * 3 + 2) * 2u))));
  if (((int)((uVar22 + 2) - uVar11) < 0 || uVar22 + 2 == uVar11) && (uVar24 <= uVar11)) {
    iVar4 = ((int)(uVar20 + 7) >> 3) * 2;
    iVar15 = iVar4 + 3;
    uVar19 = uVar11 - uVar22 & 0xffff;
    uVar16 = iVar4 + 5;
    uVar12 = uVar11;
    uVar23 = uVar22;
    if (-1 < (int)(uVar16 - uVar19) && uVar16 != uVar19) {
      uVar24 = uVar24 + uVar19;
      uVar23 = 0;
      uVar12 = uVar22;
    }
    uVar24 = iVar15 + uVar24;
    if ((uVar24 & 0xffff) <= uVar11) {
      if (uVar12 < uVar11) {
        puVar17 = ((void *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x21a54u + (uint32_t)(uVar10) * 4u)))))));
        *(undefined4 *)(puVar17 + uVar12 * 4) = 0xffffffff;
        (*((undefined4 *)camry_host_ptr((uint32_t)((int)(puVar17 + uVar12 * 4) + 4)))) = 0;
      }
      puVar17 = ((void *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x21a54u + (uint32_t)(uVar10) * 4u)))))));
      (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe48dau + (uint32_t)(uVar10 * 3) * 2u)))) = (short)iVar15 + (short)uVar23;
      (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe48dau + (uint32_t)(uVar10 * 3 + 2) * 2u)))) = (ushort)uVar24;
      uVar9 = record->source_pdu;
      puVar1 = (uint *)(puVar17 + uVar23 * 4);
      bVar5 = record->class_flags;
      puVar1[2] = uVar13;
      uVar10 = (uint)uVar9 * 0x10000 + (uint)bVar5 * 0x100 + uVar20;
      *puVar1 = uVar10;
      puVar1[1] = ~uVar10;
      uVar10 = DAT_000218ec;
      uVar11 = uVar21 & 0xfc;
      if ((uVar21 != uVar20) && (uVar14 != 0)) {
        for (uVar12 = uVar21 >> 2; uVar12 = uVar12 & 0xff, uVar12 < (uint)((int)uVar20 >> 2);
            uVar12 = uVar12 + 1) {
          puVar1[uVar12 + 3] = uVar10;
        }
      }
      puVar18 = ((void *)camry_host_ptr((uint32_t)(record->data)));
      for (uVar20 = 0; uVar20 < uVar11; uVar20 = uVar20 + 4 & 0xff) {
        puVar2 = puVar18 + uVar20;
        uVar6 = puVar2[1];
        uVar7 = puVar2[2];
        uVar8 = puVar2[3];
        puVar3 = ((uchar *)camry_host_ptr((uint32_t)((int)camry_host_addr(puVar1) + uVar20 + 0xc)));
        *puVar3 = *puVar2;
        puVar3[1] = uVar6;
        puVar3[2] = uVar7;
        puVar3[3] = uVar8;
      }
      for (; uVar11 < uVar21; uVar11 = uVar11 + 1 & 0xff) {
        (*((uchar *)camry_host_ptr((uint32_t)((int)camry_host_addr(puVar1) + uVar11 + 0xc)))) = puVar18[uVar11];
      }
      return 0;
    }
    uVar12 = 2;
  }
  return uVar12;
}

uint snapshot_and_enqueue_can_tx(uchar controller,ushort route,F33CanIfTxRecord *record)

{
  ushort *puVar1;
  undefined4 *puVar2;
  uint *puVar3;
  ushort queue_index;
  ushort capacity_words;
  uchar *puVar4;
  uint uVar5;
  uint32_t puVar6;
  uint32_t puVar7;
  uint uVar8;
  undefined4 uVar9;
  int iVar10;
  uint uVar11;
  uint uVar12;
  uint uVar13;
  uint uVar14;
  uint uVar15;
  uint uVar16;
  uint uVar17;
  F33CanIfTxRecord local_28;
  
  uVar8 = (uint)controller;
  puVar6 = 0xfebeb800u;
  puVar7 = 0x23dfcu;
  uVar14 = 1;
  if (uVar8 < DAT_00021970) {
    local_28.length = record->length;
    uVar16 = (uint)local_28.length;
    uVar15 = record->class_flags | 0x80;
    local_28.raw_id = record->raw_id;
    local_28.class_flags = (uchar)uVar15;
    local_28.source_pdu = record->source_pdu;
    puVar4 = ((void *)camry_host_ptr((uint32_t)(record->data)));
    local_28.data = camry_host_addr(puVar4);
    if (uVar15 == 0x81) {
      if (0x40 < uVar16) {
        uVar16 = 0x40;
      }
      puVar6 = 0xfebeb800u;
      uVar9 = call_interrupt_guard_and_return_zero_7a2da();
      for (uVar5 = 0; uVar5 < uVar16; uVar5 = uVar5 + 1 & 0xff) {
        (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(uVar5 - 0x684e))))) = puVar4[uVar5];
      }
      ((void)(uVar9), thunk_pop_and_restore_priority_mask_stack_6a4c4());
      local_28.data = puVar6 + -0x684e;
      iVar10 = (*(int (*)())camry_indirect((uint32_t)(((((code *)(uintptr_t)((uint32_t)((uintptr_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(puVar7 + uVar8 * 4 + -0x24fc))))))))))))(uVar8,camry_host_addr(&local_28), camry_host_addr(record));
      uVar16 = (uint)local_28.length;
      if (iVar10 != 0) {
        return 1;
      }
    }
    iVar10 = translate_controller_encoded_index_or_ff_7fbdc(uVar8,route);
    uVar9 = call_interrupt_guard_and_return_zero_7a2da();
    if (((((*((short *)camry_host_ptr((uint32_t)(puVar6 + uVar8 * 2 + -0x6f28)))) == 0x57a8) && ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(uVar8 - 0x6efd))))) == 'Z'))
        && ((*((short *)camry_host_ptr((uint32_t)(puVar6 + uVar8 * 2 + -0x6f02)))) == 0x5555)) && (iVar10 != 0xff)) {
      puVar1 = ((ushort *)camry_host_ptr((uint32_t)((short)iVar10 * 10 + (*((volatile int32_t *)camry_host_ptr((uint32_t)(puVar7 + uVar8 * 4 + -0x2518)))))));
      queue_index = puVar1[4];
      uVar5 = (uint)queue_index;
      capacity_words = *puVar1;
      uVar8 = (uint)capacity_words;
      if (uVar16 < 9) {
        uVar13 = (uint)(*((ushort *)camry_host_ptr((uint32_t)(puVar6 + uVar5 * 6 + -0x6f26))));
        uVar12 = (uint)(*((ushort *)camry_host_ptr((uint32_t)(puVar6 + uVar5 * 6 + -0x6f22))));
        if (((int)((uVar13 + 2) - uVar8) < 0 || uVar13 + 2 == uVar8) && (uVar12 <= uVar8)) {
          uVar11 = uVar8 - uVar13 & 0xffff;
          uVar14 = uVar13;
          uVar17 = uVar8;
          if (uVar11 < 7) {
            uVar12 = uVar12 + uVar11;
            uVar14 = 0;
            uVar17 = uVar13;
          }
          if (uVar8 < (uVar12 + 5 & 0xffff)) {
            uVar14 = 2;
          }
          else {
            if (uVar17 < uVar8) {
              puVar2 = ((undefined4 *)camry_host_ptr((uint32_t)(uVar17 * 4 + (*((volatile int32_t *)camry_host_ptr((uint32_t)(puVar7 + uVar5 * 4 + -0x23a8)))))));
              *puVar2 = 0xffffffff;
              puVar2[1] = 0;
            }
            iVar10 = (*((int *)camry_host_ptr((uint32_t)(puVar7 + uVar5 * 4 + -0x23a8))));
            (*((short *)camry_host_ptr((uint32_t)(puVar6 + uVar5 * 6 + -0x6f26)))) = (short)uVar14 + 5;
            (*((short *)camry_host_ptr((uint32_t)(puVar6 + uVar5 * 6 + -0x6f22)))) = (short)(uVar12 + 5);
            puVar3 = ((uint *)camry_host_ptr((uint32_t)(uVar14 * 4 + iVar10)));
            uVar8 = (uint)local_28.source_pdu * 0x10000 + uVar15 * 0x100 + uVar16;
            *puVar3 = uVar8;
            puVar3[1] = ~uVar8;
            puVar3[2] = local_28.raw_id;
            for (uVar8 = 0; uVar8 < uVar16; uVar8 = uVar8 + 1 & 0xff) {
              (*((uchar *)camry_host_ptr((uint32_t)((int)camry_host_addr(puVar3) + uVar8 + 0xc)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)((uint32_t)(local_28.data) + (uint32_t)(uVar8) * 1u))));
            }
            uVar14 = 0;
          }
        }
      }
      else {
        uVar14 = enqueue_large_can_tx(&local_28,queue_index,capacity_words);
      }
    }
    ((void)(uVar9), thunk_pop_and_restore_priority_mask_stack_6a4c4());
  }
  return uVar14;
}

uint canif_transmit(ushort source_pdu,F33PduInfo *info)

{
  uint *puVar1;
  uint uVar2;
  uint uVar3;
  uint32_t puVar4;
  F33CanIfTxRecord local_10;
  
  puVar4 = (source_pdu & 0xf800);
  uVar3 = source_pdu & 0x7ff;
  if ((source_pdu & 0xf800) != 0) {
    if (puVar4 == 0x6000) {
      puVar4 = 0x1;
    }
    else if (puVar4 == 0x800) {
      puVar4 = 0x2;
    }
    else if (puVar4 == 0xb800u) {
      puVar4 = 0x3;
    }
    else if (puVar4 == 0xc000) {
      puVar4 = 0x4;
    }
    else if (puVar4 == 0xf800) {
      puVar4 = 0x5;
    }
    else {
      puVar4 = 0xff;
    }
  }
  uVar2 = 1;
  if ((puVar4 != 0xff) && (uVar3 < (ushort)(*((volatile uint16_t *)camry_host_ptr((uint32_t)(0x21a48u + (uint32_t)((int)puVar4) * 2u)))))) {
    puVar1 = ((uint *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x21994u + (uint32_t)((int)puVar4) * 4u)))) + uVar3 * 8)));
    local_10.raw_id = *puVar1;
    local_10.class_flags = (uchar)(1 << ((uint)puVar4 & 0x1f));
    local_10.length = (uchar)info->length;
    local_10.data = info->data;
    local_10.source_pdu = source_pdu;
    uVar2 = snapshot_and_enqueue_can_tx
                      ((uchar)puVar1[1],(*((ushort *)camry_host_ptr((uint32_t)((int)camry_host_addr(puVar1) + 6)))) | (ushort)((int)puVar4 << 8),
                       &local_10);
  }
  return uVar2;
}

void reset_encoded_tx_queue_and_completion_state_7ff98(uint param_1,undefined2 param_2,char param_3)

{
  short *psVar1;
  undefined2 *puVar2;
  char cVar3;
  ushort uVar4;
  uint32_t puVar5;
  uint32_t puVar6;
  int iVar7;
  undefined4 uVar8;
  
  puVar5 = 0xfebeb800u;
  puVar6 = 0x23dfcu;
  param_1 = param_1 & 0xff;
  if (((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x21972u + (uint32_t)(param_1) * 1u)))) != '\0') && (iVar7 = translate_controller_encoded_index_or_ff_7fbdc(param_1,param_2), iVar7 != 0xff))
  {
    psVar1 = ((short *)camry_host_ptr((uint32_t)((short)iVar7 * 10 + (*((volatile int32_t *)camry_host_ptr((uint32_t)(puVar6 + param_1 * 4 + -0x2518)))))));
    uVar4 = psVar1[4];
    if (*psVar1 != 0) {
      uVar8 = call_interrupt_guard_and_return_zero_7a2da();
      puVar2 = ((undefined2 *)camry_host_ptr((uint32_t)(puVar5 + (uint)uVar4 * 6 + -0x6f26)));
      *puVar2 = 0;
      puVar2[1] = 0;
      puVar2[2] = 0;
      if (((*((short *)camry_host_ptr((uint32_t)(puVar5 + param_1 * 2 + -0x6f28)))) == 0x57a8) &&
         ((*((short *)camry_host_ptr((uint32_t)(puVar5 + param_1 * 2 + -0x6f02)))) == 0x5555)) {
        cVar3 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(uVar4 - 0x6efc)))));
        if (cVar3 == 'Z') {
          (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(uVar4 - 0x6efc))))) = '<';
          if (param_3 == '\x01') {
            cancel_route_transmit_and_complete_saved_can_route_851ee(psVar1[3]);
          }
        }
        else if (cVar3 == 'i') {
          if ((*((char *)camry_host_ptr((uint32_t)((*((volatile int32_t *)camry_host_ptr((uint32_t)(puVar6 + param_1 * 4 + -0x2514)))) + (uint)*(byte *)(psVar1 + 2))))) ==
              '<') {
            (*((undefined1 *)camry_host_ptr((uint32_t)((*((volatile int32_t *)camry_host_ptr((uint32_t)(puVar6 + param_1 * 4 + -0x2514)))) + (uint)*(byte *)(psVar1 + 2)))))
                 = 0x69;
            zero_controller_indexed_u16_counter_7f5da(param_1, *(byte *)(psVar1 + 2));
          }
        }
      }
      ((void)(uVar8), thunk_pop_and_restore_priority_mask_stack_6a4c4());
    }
  }
  return;
}
