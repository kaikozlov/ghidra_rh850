#include "common.h"

void match_masked_message_id_and_dispatch_81072(uint param_1,uint *param_2,uint param_3)

{
  uint8_t stack_record_10[16];
  ushort *puVar1;
  uint uVar2;
  int *piVar3;
  
  param_3 = param_3 & 0xff;
  piVar3 = ((int *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x21a0cu + (uint32_t)(param_3) * 4u))))));
  puVar1 = ((ushort *)camry_host_ptr((uint32_t)((param_1 & 0xff) * 2 + piVar3[3])));
  uVar2 = (uint)*puVar1;
  while( true ) {
    if (puVar1[1] <= uVar2) {
      return;
    }
    if (((*((uint *)camry_host_ptr((uint32_t)((param_1 & 0xff) * 4 + piVar3[2])))) & *param_2) == (*((uint *)camry_host_ptr((uint32_t)(uVar2 * 8 + *piVar3)))))
    break;
    uVar2 = uVar2 + 1 & 0xffff;
  }
  (*((uint32_t *)(stack_record_10 + 0))) = param_2[2];
  (*((uint16_t *)(stack_record_10 + 4))) = (ushort)(*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_2) + 7))));
  (*(int (*)())camry_indirect((uint32_t)(piVar3[1])))((ushort)(*((volatile uint16_t *)camry_host_ptr((uint32_t)(0x21a48u + (uint32_t)(param_3) * 2u)))) + uVar2 & 0xffff |
             (uint)*(ushort *)(((undefined *)camry_host_ptr((uint32_t)(0x22d94u + (uint32_t)(param_3 * 2) * 1u)))),camry_host_addr(((uint32_t *)(stack_record_10))),((uint32_t)((uint32_t)(0x21a48u + (uint32_t)(param_3) * 1u))));
  return;
}

void filter_matched_message_and_dispatch_pdu_810f2(uint param_1,uint *param_2)

{
  uint8_t stack_record_28[40];
  byte bVar1;
  bool bVar2;
  uint32_t puVar3;
  int iVar4;
  uint uVar5;
  uint uVar6;
  
  puVar3 = (0x23dfcu);
  param_1 = param_1 & 0xff;
  uVar5 = (uint)*(ushort *)(((undefined *)camry_host_ptr((uint32_t)(0x21908u + (uint32_t)(param_1 * 2) * 1u))));
  while( true ) {
    if (*(ushort *)(((undefined *)camry_host_ptr((uint32_t)(0x2190au + (uint32_t)(param_1 * 2) * 1u)))) <= uVar5) {
      return;
    }
    if (((*((uint *)camry_host_ptr((uint32_t)(PTR_DAT_00021a70 + param_1 * 4)))) & *param_2) ==
        (*((uint *)camry_host_ptr((uint32_t)(PTR_DAT_00021a68 + uVar5 * 8))))) break;
    uVar5 = uVar5 + 1 & 0xffff;
  }
  bVar2 = false;
  uVar6 = DAT_00021a48 + uVar5 & 0xffff;
  bVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x21fb8u + (uint32_t)(uVar6) * 1u))));
  if (((bVar1 & 1) != 0) &&
     (puVar3 = (0x23dfcu), iVar4 = (*(int (*)())camry_indirect((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x21950u + (uint32_t)(param_1) * 4u))))))(uVar5, camry_host_addr(param_2)), iVar4 != 0)) {
    bVar2 = true;
    increment_tracking_counter5398_8e7ba(uVar6);
  }
  iVar4 = (*(int (*)())camry_indirect((uint32_t)(((((code *)(uintptr_t)((uint32_t)((uintptr_t)(*((volatile uint32_t *)(((undefined *)camry_host_ptr((uint32_t)(0x23dfcu + (uint32_t)(param_1 * 4 + -0x24a8) * 1u))))))))))))))(0,uVar5,camry_host_addr(param_2));
  if (iVar4 != 0) {
    ((void)(uVar6), return_only_stub_8135c());
    return;
  }
  if (bVar2) {
    return;
  }
  if (((bVar1 >> 4 & 1) != 0) && (iVar4 = conditionally_run_descriptor_checksum_check_6a3be(uVar6, camry_host_addr(param_2)), iVar4 != 0)) {
    return;
  }
  ((void)(uVar6), return_only_stub_8135e());
  (*((uint32_t *)(stack_record_28 + 0))) = param_2[2];
  (*((uint16_t *)(stack_record_28 + 4))) = (ushort)(*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_2) + 7))));
  ((void)(((uint32_t *)(stack_record_28))), call_21ce4_with_masked_u16_81d16(uVar6));
  return;
}

int dispatch_message_hook_unless_flag_filter_rejects_811be(uint param_1,int param_2)

{
  byte bVar1;
  uint32_t puVar2;
  int iVar3;
  
  puVar2 = (0x23dfcu);
  iVar3 = 0;
  bVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x21fb8u + (uint32_t)((*((ushort *)camry_host_ptr((uint32_t)(param_2 + 4)))) & 0x7ff) * 1u))));
  if ((((bVar1 >> 4 & 1) == 0) || (puVar2 = (0x23dfcu), iVar3 = return_zero_or_invoke_zero_hook_6a3f4((*((volatile uint16_t *)(((uint8_t *)camry_host_ptr((uint32_t)((uint32_t)(param_2) + (uint32_t)((4)) * 1u))))))), iVar3 == 0)) &&
     ((bVar1 & 1) != 0)) {
    (*(int (*)())camry_indirect((uint32_t)(((((code *)(uintptr_t)((uint32_t)((uintptr_t)(*((volatile uint32_t *)(((undefined *)camry_host_ptr((uint32_t)(0x23dfcu + (uint32_t)((param_1 & 0xff) * 4 + -0x24b0) * 1u))))))))))))))(param_2, param_2);
  }
  return iVar3;
}

void match_masked_message_and_dispatch_id_800_81200(uint param_1,uint *param_2,uint param_3)

{
  uint8_t stack_record_18[24];
  ushort uVar1;
  uint32_t puVar2;
  uint uVar3;
  int iVar4;
  
  puVar2 = 0x23dfcu;
  param_1 = param_1 & 0xff;
  uVar3 = (uint)*(ushort *)(((undefined *)camry_host_ptr((uint32_t)(0x21910u + (uint32_t)(param_1 * 2) * 1u))));
  while( true ) {
    if (*(ushort *)(((undefined *)camry_host_ptr((uint32_t)(0x21912u + (uint32_t)(param_1 * 2) * 1u)))) <= uVar3) {
      return;
    }
    if (((*((uint *)camry_host_ptr((uint32_t)(PTR_DAT_00021a98 + param_1 * 4)))) & *param_2) ==
        (*((uint *)camry_host_ptr((uint32_t)(PTR_DAT_00021a90 + uVar3 * 8))))) break;
    uVar3 = uVar3 + 1 & 0xffff;
  }
  uVar1 = (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0x21a48u + (uint32_t)(param_3 & 0xff) * 2u))));
  iVar4 = (*(int (*)())camry_indirect((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x21958u + (uint32_t)(param_1) * 4u))))))(2,uVar3,camry_host_addr(param_2));
  if (iVar4 != 0) {
    return_only_stub_81360();
    return;
  }
  (*((uint32_t *)(stack_record_18 + 0))) = param_2[2];
  (*((uint16_t *)(stack_record_18 + 4))) = (ushort)(*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_2) + 7))));
  (*(int (*)())camry_indirect((uint32_t)(((((code *)(uintptr_t)((uint32_t)((uintptr_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(puVar2 + -0x2368))))))))))))(uVar1 + uVar3 & 0xffff | 0x800,camry_host_addr(((uint32_t *)(stack_record_18))));
  return;
}

void call_stub_83590_for_matching_channels_81290(char param_1)

{
  undefined8 uVar1;
  uint uVar2;
  uint uVar3;
  
  uVar1 = 0x23dfc00000000;
  uVar2 = (uint)DAT_00021971;
  for (uVar3 = 0; uVar3 < uVar2; uVar3 = uVar3 + 1 & 0xff) {
    if (param_1 == (*((char *)camry_host_ptr((uint32_t)(uVar3 + (int)((ulonglong)uVar1 >> 0x20) + -0x2484))))) {
      ((void)(uVar3), return_only_stub_83590());
    }
  }
  return;
}

void call_stub_83596_for_matching_channels_812be(char param_1)

{
  undefined8 uVar1;
  uint uVar2;
  uint uVar3;
  
  uVar1 = 0x23dfc00000000;
  uVar2 = (uint)DAT_00021971;
  for (uVar3 = 0; uVar3 < uVar2; uVar3 = uVar3 + 1 & 0xff) {
    if (param_1 == (*((char *)camry_host_ptr((uint32_t)(uVar3 + (int)((ulonglong)uVar1 >> 0x20) + -0x2484))))) {
      ((void)(uVar3), return_only_stub_83596());
    }
  }
  return;
}

void call_stub_83592_for_terminal_controller_tokens_812ec(uint param_1)

{
  uint32_t puVar1;
  uint uVar2;
  uint uVar3;
  
  puVar1 = 0x23dfcu;
  if (((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe4912u + (uint32_t)(param_1 & 0xff) * 1u)))) == 'K') || (((int8_t)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe4912u + (uint32_t)(param_1 & 0xff) * 1u))))) == -0x5b)) {
    uVar2 = (uint)DAT_00021971;
    for (uVar3 = 0; uVar3 < uVar2; uVar3 = uVar3 + 1 & 0xff) {
      if ((param_1 & 0xff) == (uint)(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(uVar3 - 0x2484)))))) {
        ((void)(uVar3), return_only_stub_83592());
      }
    }
  }
  return;
}

void call_stub_83594_for_matching_channels_8132e(char param_1)

{
  undefined8 uVar1;
  uint uVar2;
  uint uVar3;
  
  uVar1 = 0x23dfc00000000;
  uVar2 = (uint)DAT_00021971;
  for (uVar3 = 0; uVar3 < uVar2; uVar3 = uVar3 + 1 & 0xff) {
    if (param_1 == (*((char *)camry_host_ptr((uint32_t)(uVar3 + (int)((ulonglong)uVar1 >> 0x20) + -0x2484))))) {
      ((void)(uVar3), return_only_stub_83594());
    }
  }
  return;
}

void return_only_stub_8135c(void)

{
  return;
}

void return_only_stub_8135e(void)

{
  return;
}

void return_only_stub_81360(void)

{
  return;
}

void dispatch_six_bank_message_with_global_payload_81362(uint param_1,int param_2)

{
  ushort uVar1;
  ushort uVar2;
  uint32_t puVar3;
  int iVar4;
  
  puVar3 = 0xfebeb800u;
  if (DAT_00021974 == '\x01') {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe490eu + (uint32_t)(param_1 & 0xff) * 1u)))) = 1;
    uVar1 = (*((ushort *)camry_host_ptr((uint32_t)(param_2 + 4))));
    uVar2 = uVar1 & 0xf800;
    iVar4 = 0;
    if ((((((uVar1 & 0xf800) == 0) || (iVar4 = 1, uVar2 == 0x6000)) || (iVar4 = 2, uVar2 == 0x800))
        || (((iVar4 = 3, uVar2 == 0xb800 || (iVar4 = 4, uVar2 == 0xc000)) ||
            (iVar4 = 5, uVar2 == 0xf800)))) && ((uVar1 & 0x7ff) < (ushort)(*((volatile uint16_t *)camry_host_ptr((uint32_t)(0x21a48u + (uint32_t)(iVar4) * 2u)))))) {
      DAT_febe4ff8 = (*((undefined4 *)camry_host_ptr((uint32_t)(param_2 + 8))));
      DAT_febe4ffc = (ushort)(*((byte *)camry_host_ptr((uint32_t)(param_2 + 7))));
      (*(int (*)())camry_indirect((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x2197cu + (uint32_t)(iVar4) * 4u))))))();
      (*((undefined4 *)camry_host_ptr((uint32_t)(puVar3 + -0x6808)))) = 0;
      (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x6804)))) = 0;
    }
  }
  return;
}

undefined1 lookup_extended_bank_record_byte_or_ff_813e4(uint param_1)

{
  uint32_t puVar1;
  uint uVar2;
  undefined1 uVar3;
  int iVar4;
  
  puVar1 = ((uint32_t)(param_1 & 0xf800));
  param_1 = param_1 & 0x7ff;
  uVar3 = 0xff;
  iVar4 = 0;
  if ((((((uintptr_t)(puVar1)== 0) || (iVar4 = 1,(puVar1)==((uint32_t)((uint32_t)(0x6000))))) ||
       (iVar4 = 2,(puVar1)==((uint32_t)((uint32_t)(0x800))))) ||
      ((iVar4 = 3,(puVar1)==((uint32_t)(0xb800u))|| (iVar4 = 4,(puVar1)==((uint32_t)((uint32_t)(0xc000))))))) ||
     (iVar4 = 5,(puVar1)==((uint32_t)((uint32_t)(0xf800))))) {
    uVar2 = (uint)(ushort)(*((volatile uint16_t *)camry_host_ptr((uint32_t)(0x21a48u + (uint32_t)(iVar4) * 2u))));
    if ((uVar2 <= param_1) &&
       ((int)(param_1 - ((*((ushort *)camry_host_ptr((uint32_t)((int)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x21a0cu + (uint32_t)(iVar4) * 4u)))) + 0x10)))) + uVar2)) < 0)) {
      uVar3 = (*((undefined1 *)camry_host_ptr((uint32_t)((param_1 - uVar2 & 0xffff) * 8 + (*((volatile int32_t *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x21a0cu + (uint32_t)(iVar4) * 4u))))))) + 5))));
    }
  }
  return uVar3;
}

undefined1 lookup_base_bank_controller_byte_or_ff_8144e(uint param_1)

{
  uint base;
  undefined1 uVar2;
  int iVar3;
 
  base = param_1 & 0xf800u;
  uVar2 = 0xff;
  iVar3 = 0;
  if ((((((base == 0) || (iVar3 = 1, base == 0x6000)) || (iVar3 = 2, base == 0x800)) ||
       (((iVar3 = 3, base == 0xb800) || (iVar3 = 4, base == 0xc000)) || (iVar3 = 5, base == 0xf800)))
      ) && ((param_1 & 0x7ff) < (uint)(ushort)(*((volatile uint16_t *)camry_host_ptr((uint32_t)(0x21a48u + (uint32_t)(iVar3) * 2u)))))) {
    uVar2 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x21994u + (uint32_t)(iVar3) * 4u)))) + (uint32_t)((param_1 & 0x7ff) * 8 + 4)))));
  }
  return uVar2;
}

void return_only_stub_814aa(void)

{
  return;
}

undefined4 return_const_0_814ae(void)

{
  return 0;
}

void return_only_stub_8152e(void)

{
  return;
}

void set_controller_status_byte_or_pair_failure_81530(uint param_1,char param_2)

{
  uint32_t puVar1;
  undefined4 uVar2;
  
  puVar1 = 0xfebeb800u;
  if (param_2 == '\x01') {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe4911u + (uint32_t)(param_1 & 0xff) * 1u)))) = 0xaa;
  }
  else {
    uVar2 = call_interrupt_guard_and_return_zero_7a2da();
    (*((ushort *)camry_host_ptr((uint32_t)(puVar1 + (param_1 & 0xff) * 2 + -0x6f02)))) =
         (*((ushort *)camry_host_ptr((uint32_t)(puVar1 + (param_1 & 0xff) * 2 + -0x6f02)))) & 0xfcff | 0x200;
    ((void)(uVar2), thunk_pop_and_restore_priority_mask_stack_6a4c4());
  }
  return;
}

void set_controller_status_byte_4911_55_8156c(uint param_1)

{
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe4911u + (uint32_t)(param_1 & 0xff) * 1u)))) = 0x55;
  return;
}

undefined1 poll_driver_channel_retry_status_wrapper_8157a(undefined1 param_1)

{
  return step_channel_bank_test_attempts_8367c(param_1);
}

void return_only_stub_81588(void)

{
  return;
}

undefined4 return_const_1_8158a(void)

{
  return 1;
}

void return_only_stub_8158e(void)

{
  return;
}

void return_only_stub_81590(void)

{
  return;
}

void return_only_stub_81592(void)

{
  return;
}

uint route_secured_lower_tx(ushort pdu,F33PduInfo *info)

{
  uint uVar1;
  uint uVar2;
  uint uVar3;
  uint32_t pcVar4;
  
  uVar2 = (uint)pdu;
  uVar1 = (int)uVar2 >> 0xb;
  uVar3 = 1;
  if ((uVar1 < 0xc) && ((uVar2 & 0x7ff) < (uint)*(ushort *)(((undefined *)camry_host_ptr((uint32_t)(0x21d28u + (uint32_t)(uVar1 * 2) * 1u)))))) {
    if ((DAT_00021d25 != '\0') ||
       ((((uVar2 & 0xf800) != 0x2000 && ((uVar2 & 0xf800) != 0x2800)) ||
        (uVar3 = (uint)(*((ushort *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x21da0u + (uint32_t)(uVar1) * 4u)))) + (uVar2 & 0x7ff) * 2)))),
        pcVar4 = (uint32_t)((uint32_t)(PTR_return_const_1_816b0_00021e60)), uVar3 == 0xffff)))) {
      uVar3 = uVar2;
      pcVar4 = (uint32_t)((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x21dd0u + (uint32_t)(uVar1) * 4u))))))))));
    }
    uVar3 = (*(int (*)())camry_indirect((uint32_t)(pcVar4)))(uVar3, camry_host_addr(info));
  }
  return uVar3;
}

undefined4 dispatch_valid_twelve_bank_callback_slot_four_8160c(ushort param_1)

{
  uint uVar1;
  undefined4 uVar2;
  
  uVar1 = (int)(uint)param_1 >> 0xb;
  uVar2 = 1;
  if ((uVar1 < 0xc) && ((param_1 & 0x7ff) < *(ushort *)(((undefined *)camry_host_ptr((uint32_t)(0x21d28u + (uint32_t)(uVar1 * 2) * 1u)))))) {
    uVar2 = (*(int (*)())camry_indirect((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x21dd0u + (uint32_t)(uVar1) * 4u)))) + 4))))))))((uint)(ushort)param_1);
  }
  return uVar2;
}

void dispatch_packed_id_primary_slot4_81640(uint param_1)

{
  uint uVar1;
  uint uVar2;
  uint uVar3;
  uint32_t pcVar4;
  
  uVar1 = param_1 & 0x7ff;
  uVar2 = (int)(param_1 & 0xffff) >> 0xb;
  if ((uVar2 < 0xc) && (uVar1 < *(ushort *)(((undefined *)camry_host_ptr((uint32_t)(0x21d28u + (uint32_t)(uVar2 * 2) * 1u)))))) {
    if ((DAT_00021d24 != '\0') ||
       (uVar3 = (uint)(*((ushort *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x21d70u + (uint32_t)(uVar2) * 4u)))) + uVar1 * 2)))),
       pcVar4 = (uint32_t)((uint32_t)(PTR_return_only_stub_8176c_00021f20)), uVar3 == 0xffff)) {
      uVar3 = (*((ushort *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x21d40u + (uint32_t)(uVar2) * 4u)))) + uVar1 * 4)))) & 0x7ff;
      pcVar4 = (uint32_t)((uintptr_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x21ee4u + (uint32_t)((int)(uint)(*((ushort *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x21d40u + (uint32_t)(uVar2) * 4u)))) + uVar1 * 4)))) >> 0xb) * 4u)))) +
                         4)))));
    }
    (*(int (*)())camry_indirect((uint32_t)(pcVar4)))(uVar3);
  }
  return;
}

undefined4 return_const_1_816b0(void)

{
  return 1;
}

undefined4 return_const_1_816b4(void)

{
  return 1;
}

undefined4 return_const_1_816b8(void)

{
  return 1;
}

undefined4 query_packed_id_resolved_slot0_816bc(uint param_1)

{
  uint uVar1;
  uint uVar2;
  undefined4 uVar3;
  uint uVar4;
  uint32_t pcVar5;
  undefined4 *puVar6;
  
  uVar4 = param_1 & 0x7ff;
  uVar1 = (int)(param_1 & 0xffff) >> 0xb;
  if (0xb < uVar1) {
    return 1;
  }
  if (*(ushort *)(((undefined *)camry_host_ptr((uint32_t)(0x21d28u + (uint32_t)(uVar1 * 2) * 1u)))) <= uVar4) {
    return 1;
  }
  if (((DAT_00021d25 != '\0') || ((param_1 & 0xf800) != 0x2000)) ||
     (uVar2 = (uint)(*((ushort *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x21da0u + (uint32_t)(uVar1) * 4u)))) + uVar4 * 2)))),
     pcVar5 = (uint32_t)((uint32_t)(PTR_return_const_1_816b8_00021e64)), uVar2 == 0xffff)) {
    uVar2 = (uint)(*((ushort *)camry_host_ptr((uint32_t)((int)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x21d40u + (uint32_t)(uVar1) * 4u)))) + uVar4 * 4) + 2))));
    puVar6 = ((undefined4 *)camry_host_ptr((uint32_t)(PTR_PTR_00021cbc)));
    if (uVar2 == 0xffff) {
      if ((DAT_00021d24 == '\0') &&
         (uVar2 = (uint)(*((ushort *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x21d70u + (uint32_t)(uVar1) * 4u)))) + uVar4 * 2)))),
         pcVar5 = (uint32_t)((uint32_t)(PTR_return_const_1_816b8_00021f1c)), uVar2 != 0xffff))
      goto LAB_0008175c;
      uVar1 = (uint)(*((ushort *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x21d40u + (uint32_t)(uVar1) * 4u)))) + uVar4 * 4))));
      uVar2 = uVar1 & 0x7ff;
      puVar6 = ((undefined4 *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x21ee4u + (uint32_t)((int)uVar1 >> 0xb) * 4u))))));
    }
    pcVar5 = (uint32_t)(*puVar6);
  }
LAB_0008175c:
  uVar3 = (*(int (*)())camry_indirect((uint32_t)(pcVar5)))(uVar2);
  return uVar3;
}

void return_only_stub_8176c(void)

{
  return;
}

void return_only_stub_8176e(void)

{
  return;
}

void dispatch_packed_id_resolved_slot4_with_value_81770(uint param_1,undefined4 param_2)

{
  uint uVar1;
  uint uVar2;
  uint uVar3;
  uint32_t pcVar4;
  uint32_t puVar5;
  
  uVar3 = param_1 & 0x7ff;
  uVar1 = (int)(param_1 & 0xffff) >> 0xb;
  if (0xb < uVar1) {
    return;
  }
  if (*(ushort *)(((undefined *)camry_host_ptr((uint32_t)(0x21d28u + (uint32_t)(uVar1 * 2) * 1u)))) <= uVar3) {
    return;
  }
  if (((DAT_00021d25 == '\0') && ((param_1 & 0xf800) == 0x2000)) &&
     (uVar2 = (uint)(*((ushort *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x21da0u + (uint32_t)(uVar1) * 4u)))) + uVar3 * 2)))), uVar2 != 0xffff)) {
    param_2 = 0;
    pcVar4 = (uint32_t)((uint32_t)(PTR_return_only_stub_8176e_00021e68));
  }
  else {
    uVar2 = (uint)(*((ushort *)camry_host_ptr((uint32_t)((int)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x21d40u + (uint32_t)(uVar1) * 4u)))) + uVar3 * 4) + 2))));
    puVar5 = PTR_PTR_00021cbc;
    if (uVar2 == 0xffff) {
      if ((DAT_00021d24 == '\0') &&
         (uVar2 = (uint)(*((ushort *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x21d70u + (uint32_t)(uVar1) * 4u)))) + uVar3 * 2)))),
         pcVar4 = (uint32_t)((uint32_t)(PTR_return_only_stub_8176c_00021f20)), uVar2 != 0xffff))
      goto LAB_00081816;
      uVar1 = (uint)(*((ushort *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x21d40u + (uint32_t)(uVar1) * 4u)))) + uVar3 * 4))));
      uVar2 = uVar1 & 0x7ff;
      puVar5 = (*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x21ee4u + (uint32_t)((int)uVar1 >> 0xb) * 4u))));
    }
    pcVar4 = (uint32_t)(camry_host_addr(*((code * *)camry_host_ptr((uint32_t)(puVar5 + 4)))));
  }
LAB_00081816:
  (*(int (*)())camry_indirect((uint32_t)(pcVar4)))(uVar2,param_2);
  return;
}

void dispatch_packed_id_slot24_with_byte_8182e(uint param_1,undefined1 param_2)

{
  uint uVar1;
  uint uVar2;
  undefined *puVar3;
  
  uVar1 = (int)(param_1 & 0xffff) >> 0xb;
  if ((uVar1 < 0xc) && ((param_1 & 0x7ff) < (uint)*(ushort *)(((undefined *)camry_host_ptr((uint32_t)(0x21d28u + (uint32_t)(uVar1 * 2) * 1u)))))) {
    uVar2 = (uint)(*((ushort *)camry_host_ptr((uint32_t)((int)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x21d40u + (uint32_t)(uVar1) * 4u)))) + (param_1 & 0x7ff) * 4) + 2))));
    puVar3 = ((void *)camry_host_ptr((uint32_t)(PTR_PTR_00021cbc)));
    if (uVar2 == 0xffff) {
      uVar1 = (uint)(*((ushort *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x21d40u + (uint32_t)(uVar1) * 4u)))) + (param_1 & 0x7ff) * 4))));
      uVar2 = uVar1 & 0x7ff;
      puVar3 = ((void *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x21ee4u + (uint32_t)((int)uVar1 >> 0xb) * 4u)))))));
    }
    (*(int (*)())camry_indirect((uint32_t)(((((code *)(uintptr_t)((uint32_t)((uintptr_t)(*((volatile uint32_t *)(puVar3 + 0x18)))))))))))(uVar2,param_2);
  }
  return;
}

undefined4 query_packed_id_slot12_with_buffer_and_u16_81886(uint param_1,undefined4 param_2,undefined2 param_3, undefined4 param_4)

{
  uint uVar1;
  uint uVar2;
  undefined4 uVar3;
  undefined *puVar4;
  
  uVar3 = 1;
  uVar1 = (int)(param_1 & 0xffff) >> 0xb;
  if ((uVar1 < 0xc) && ((param_1 & 0x7ff) < (uint)*(ushort *)(((undefined *)camry_host_ptr((uint32_t)(0x21d28u + (uint32_t)(uVar1 * 2) * 1u)))))) {
    uVar2 = (uint)(*((ushort *)camry_host_ptr((uint32_t)((int)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x21d40u + (uint32_t)(uVar1) * 4u)))) + (param_1 & 0x7ff) * 4) + 2))));
    puVar4 = ((void *)camry_host_ptr((uint32_t)(PTR_PTR_00021cbc)));
    if (uVar2 == 0xffff) {
      uVar1 = (uint)(*((ushort *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x21d40u + (uint32_t)(uVar1) * 4u)))) + (param_1 & 0x7ff) * 4))));
      uVar2 = uVar1 & 0x7ff;
      puVar4 = ((void *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x21ee4u + (uint32_t)((int)uVar1 >> 0xb) * 4u)))))));
    }
    uVar3 = (*(int (*)())camry_indirect((uint32_t)(((((code *)(uintptr_t)((uint32_t)((uintptr_t)(*((volatile uint32_t *)(puVar4 + 0xc)))))))))))(uVar2,param_2,param_3, param_4);
  }
  return uVar3;
}

undefined4 query_packed_id_slot16_818e0(uint param_1, undefined4 param_2, undefined4 param_3)

{
  uint uVar1;
  uint uVar2;
  undefined4 uVar3;
  undefined *puVar4;
  
  uVar3 = 1;
  uVar1 = (int)(param_1 & 0xffff) >> 0xb;
  if ((uVar1 < 0xc) && ((param_1 & 0x7ff) < (uint)*(ushort *)(((undefined *)camry_host_ptr((uint32_t)(0x21d28u + (uint32_t)(uVar1 * 2) * 1u)))))) {
    uVar2 = (uint)(*((ushort *)camry_host_ptr((uint32_t)((int)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x21d40u + (uint32_t)(uVar1) * 4u)))) + (param_1 & 0x7ff) * 4) + 2))));
    puVar4 = ((void *)camry_host_ptr((uint32_t)(PTR_PTR_00021cbc)));
    if (uVar2 == 0xffff) {
      uVar1 = (uint)(*((ushort *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x21d40u + (uint32_t)(uVar1) * 4u)))) + (param_1 & 0x7ff) * 4))));
      uVar2 = uVar1 & 0x7ff;
      puVar4 = ((void *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x21ee4u + (uint32_t)((int)uVar1 >> 0xb) * 4u)))))));
    }
    uVar3 = (*(int (*)())camry_indirect((uint32_t)(((((code *)(uintptr_t)((uint32_t)((uintptr_t)(*((volatile uint32_t *)(puVar4 + 0x10)))))))))))(uVar2, param_2, param_3);
  }
  return uVar3;
}

void dispatch_packed_id_slot28_with_byte_81938(uint param_1,undefined1 param_2)

{
  uint uVar1;
  uint uVar2;
  undefined *puVar3;
  
  uVar1 = (int)(param_1 & 0xffff) >> 0xb;
  if ((uVar1 < 0xc) && ((param_1 & 0x7ff) < (uint)*(ushort *)(((undefined *)camry_host_ptr((uint32_t)(0x21d28u + (uint32_t)(uVar1 * 2) * 1u)))))) {
    uVar2 = (uint)(*((ushort *)camry_host_ptr((uint32_t)((int)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x21d40u + (uint32_t)(uVar1) * 4u)))) + (param_1 & 0x7ff) * 4) + 2))));
    puVar3 = ((void *)camry_host_ptr((uint32_t)(PTR_PTR_00021cbc)));
    if (uVar2 == 0xffff) {
      uVar1 = (uint)(*((ushort *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x21d40u + (uint32_t)(uVar1) * 4u)))) + (param_1 & 0x7ff) * 4))));
      uVar2 = uVar1 & 0x7ff;
      puVar3 = ((void *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x21ee4u + (uint32_t)((int)uVar1 >> 0xb) * 4u)))))));
    }
    (*(int (*)())camry_indirect((uint32_t)(((((code *)(uintptr_t)((uint32_t)((uintptr_t)(*((volatile uint32_t *)(puVar3 + 0x1c)))))))))))(uVar2,param_2);
  }
  return;
}

undefined4 query_packed_id_slot20_81990(uint param_1, undefined4 param_2, undefined4 param_3, undefined4 param_4)

{
  uint uVar1;
  uint uVar2;
  undefined4 uVar3;
  undefined *puVar4;
  
  uVar3 = 1;
  uVar1 = (int)(param_1 & 0xffff) >> 0xb;
  if ((uVar1 < 0xc) && ((param_1 & 0x7ff) < (uint)*(ushort *)(((undefined *)camry_host_ptr((uint32_t)(0x21d28u + (uint32_t)(uVar1 * 2) * 1u)))))) {
    uVar2 = (uint)(*((ushort *)camry_host_ptr((uint32_t)((int)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x21d40u + (uint32_t)(uVar1) * 4u)))) + (param_1 & 0x7ff) * 4) + 2))));
    puVar4 = ((void *)camry_host_ptr((uint32_t)(PTR_PTR_00021cbc)));
    if (uVar2 == 0xffff) {
      uVar1 = (uint)(*((ushort *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x21d40u + (uint32_t)(uVar1) * 4u)))) + (param_1 & 0x7ff) * 4))));
      uVar2 = uVar1 & 0x7ff;
      puVar4 = ((void *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x21ee4u + (uint32_t)((int)uVar1 >> 0xb) * 4u)))))));
    }
    uVar3 = (*(int (*)())camry_indirect((uint32_t)(((((code *)(uintptr_t)((uint32_t)((uintptr_t)(*((volatile uint32_t *)(puVar4 + 0x14)))))))))))(uVar2, param_2, param_3, param_4);
  }
  return uVar3;
}

void call_21ce0_with_masked_u16_819e8(ushort param_1)

{
  (*(int (*)())camry_indirect((uint32_t)(PTR_FUN_00021ce0)))(DAT_00021d1e & param_1);
  return;
}

void call_21cf4_with_masked_u16_and_byte_81a00(ushort param_1,undefined1 param_2)

{
  (*(int (*)())camry_indirect((uint32_t)(PTR_FUN_00021cf4)))(DAT_00021d1e & param_1,param_2);
  return;
}

int call_21ce8_with_masked_u16_and_two_values_81a1a(ushort param_1,undefined4 param_2,undefined2 param_3, undefined4 param_4)

{
  return (*(int (*)())camry_indirect((uint32_t)(PTR_FUN_00021ce8)))(DAT_00021d1e & param_1,param_2,param_3, param_4);
}

int call_21cec_with_masked_u16_81a34(ushort param_1, undefined4 param_2, undefined4 param_3)

{
  return (*(int (*)())camry_indirect((uint32_t)(PTR_FUN_00021cec)))(DAT_00021d1e & param_1, param_2, param_3);
}

void call_21cf8_with_masked_u16_and_byte_81a4c(ushort param_1,undefined1 param_2)

{
  (*(int (*)())camry_indirect((uint32_t)(PTR_FUN_00021cf8)))(DAT_00021d1e & param_1,param_2);
  return;
}

int call_21cf0_with_masked_u16_81a66(ushort param_1, undefined4 param_2, undefined4 param_3, undefined4 param_4)

{
  return (*(int (*)())camry_indirect((uint32_t)(PTR_FUN_00021cf0)))(DAT_00021d1e & param_1, param_2, param_3, param_4);
}

uint route_com_tx(ushort pdu,F33PduInfo *info)

{
  uint uVar1;
  
  uVar1 = (*(int (*)())camry_indirect((uint32_t)(PTR_dispatch_upper_tx_route_00021cc4)))(DAT_00021d20 | pdu, camry_host_addr(info));
  return uVar1;
}

undefined4 call_21cc8_with_prefixed_u16_81a98(ushort param_1)

{
  return (*(int (*)())camry_indirect((uint32_t)(PTR_FUN_00021cc8)))(DAT_00021d20 | param_1);
}

uint dispatch_upper_tx_route(ushort pdu,F33PduInfo *info)

{
  uint uVar1;
  uint uVar2;
  uint32_t pcVar3;
  undefined4 *puVar4;
  
  uVar1 = (uint)pdu;
  if (uVar1 < DAT_00021d0c) {
    if ((DAT_00021d24 != '\0') ||
       (uVar2 = (uint)*(ushort *)(((undefined *)camry_host_ptr((uint32_t)(0x21d16u + (uint32_t)(uVar1 * 2) * 1u)))),
       pcVar3 = (uint32_t)((uint32_t)(PTR_return_const_1_816b0_00021f14)), uVar2 == 0xffff)) {
      uVar1 = (uint)(*((ushort *)((uint8_t *)&PTR_DAT_0002296e + (uVar1 * 2))));
      uVar2 = (uint)(*((ushort *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x21d40u + (uint32_t)((int)uVar1 >> 0xb) * 4u)))) + (uVar1 & 0x7ff) * 4 + 2))));
      puVar4 = ((undefined4 *)camry_host_ptr((uint32_t)(PTR_PTR_00021cb8)));
      if (uVar2 == 0xffff) {
        uVar2 = uVar1;
        puVar4 = ((undefined4 *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x21dd0u + (uint32_t)((int)uVar1 >> 0xb) * 4u))))));
      }
      pcVar3 = (uint32_t)(*puVar4);
    }
    uVar1 = (*(int (*)())camry_indirect((uint32_t)(pcVar3)))(uVar2, camry_host_addr(info));
  }
  else {
    uVar1 = 1;
  }
  return uVar1;
}

undefined4 query_2296e_mapped_id_slot4_81b22(uint param_1)

{
  uint uVar1;
  undefined4 uVar2;
  uint uVar3;
  uint32_t pcVar4;
  undefined *puVar5;
  
  param_1 = param_1 & 0xffff;
  if (param_1 < DAT_00021d0c) {
    if ((DAT_00021d24 != '\0') ||
       (uVar3 = (uint)*(ushort *)(((undefined *)camry_host_ptr((uint32_t)(0x21d16u + (uint32_t)(param_1 * 2) * 1u)))),
       pcVar4 = (uint32_t)((uint32_t)(PTR_return_const_1_816b4_00021f18)), uVar3 == 0xffff)) {
      uVar1 = (uint)(*((ushort *)((uint8_t *)&PTR_DAT_0002296e + (param_1 * 2))));
      uVar3 = (uint)(*((ushort *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x21d40u + (uint32_t)((int)uVar1 >> 0xb) * 4u)))) + (uVar1 & 0x7ff) * 4 + 2))));
      puVar5 = ((void *)camry_host_ptr((uint32_t)(PTR_PTR_00021cb8)));
      if (uVar3 == 0xffff) {
        uVar3 = uVar1;
        puVar5 = ((void *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x21dd0u + (uint32_t)((int)uVar1 >> 0xb) * 4u)))))));
      }
      pcVar4 = (uint32_t)((uintptr_t)(*((volatile uint32_t *)(puVar5 + 4))));
    }
    uVar2 = (*(int (*)())camry_indirect((uint32_t)(pcVar4)))(uVar3);
  }
  else {
    uVar2 = 1;
  }
  return uVar2;
}

undefined4 call_21ccc_with_prefixed_u16_81b92(ushort param_1, undefined4 param_2)

{
  return (*(int (*)())camry_indirect((uint32_t)(PTR_FUN_00021ccc)))(DAT_00021d22 | param_1, param_2);
}

undefined4 call_21cd0_with_prefixed_u16_81bac(ushort param_1)

{
  return (*(int (*)())camry_indirect((uint32_t)(PTR_FUN_00021cd0)))(DAT_00021d22 | param_1);
}

undefined4 query_22962_mapped_id_slot0_81bc6(uint param_1, undefined4 param_2)

{
  uint uVar1;
  undefined4 uVar2;
  uint uVar3;
  uint32_t pcVar4;
  undefined4 *puVar5;
  
  param_1 = param_1 & 0xffff;
  if (param_1 < DAT_00021d0e) {
    if ((DAT_00021d24 != '\0') ||
       (uVar3 = (uint)*(ushort *)(((undefined *)camry_host_ptr((uint32_t)(0x21d18u + (uint32_t)(param_1 * 2) * 1u)))),
       pcVar4 = (uint32_t)((uint32_t)(PTR_return_const_1_816b0_00021f14)), uVar3 == 0xffff)) {
      uVar1 = (uint)*(ushort *)(((undefined *)camry_host_ptr((uint32_t)(0x22962u + (uint32_t)(param_1 * 2) * 1u))));
      uVar3 = (uint)(*((ushort *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x21d40u + (uint32_t)((int)uVar1 >> 0xb) * 4u)))) + (uVar1 & 0x7ff) * 4 + 2))));
      puVar5 = ((undefined4 *)camry_host_ptr((uint32_t)(PTR_PTR_00021cb8)));
      if (uVar3 == 0xffff) {
        uVar3 = uVar1;
        puVar5 = ((undefined4 *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x21dd0u + (uint32_t)((int)uVar1 >> 0xb) * 4u))))));
      }
      pcVar4 = (uint32_t)(*puVar5);
    }
    uVar2 = (*(int (*)())camry_indirect((uint32_t)(pcVar4)))(uVar3, param_2);
  }
  else {
    uVar2 = 1;
  }
  return uVar2;
}

undefined4 query_22962_mapped_id_slot4_81c36(uint param_1)

{
  uint uVar1;
  undefined4 uVar2;
  uint uVar3;
  uint32_t pcVar4;
  undefined *puVar5;
  
  param_1 = param_1 & 0xffff;
  if (param_1 < DAT_00021d0e) {
    if ((DAT_00021d24 != '\0') ||
       (uVar3 = (uint)*(ushort *)(((undefined *)camry_host_ptr((uint32_t)(0x21d18u + (uint32_t)(param_1 * 2) * 1u)))),
       pcVar4 = (uint32_t)((uint32_t)(PTR_return_const_1_816b4_00021f18)), uVar3 == 0xffff)) {
      uVar1 = (uint)*(ushort *)(((undefined *)camry_host_ptr((uint32_t)(0x22962u + (uint32_t)(param_1 * 2) * 1u))));
      uVar3 = (uint)(*((ushort *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x21d40u + (uint32_t)((int)uVar1 >> 0xb) * 4u)))) + (uVar1 & 0x7ff) * 4 + 2))));
      puVar5 = ((void *)camry_host_ptr((uint32_t)(PTR_PTR_00021cb8)));
      if (uVar3 == 0xffff) {
        uVar3 = uVar1;
        puVar5 = ((void *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x21dd0u + (uint32_t)((int)uVar1 >> 0xb) * 4u)))))));
      }
      pcVar4 = (uint32_t)((uintptr_t)(*((volatile uint32_t *)(puVar5 + 4))));
    }
    uVar2 = (*(int (*)())camry_indirect((uint32_t)(pcVar4)))(uVar3);
  }
  else {
    uVar2 = 1;
  }
  return uVar2;
}

void dispatch_packed_id_primary_slot8_81ca6(uint param_1)

{
  uint uVar1;
  uint uVar2;
  uint uVar3;
  uint32_t pcVar4;
  
  uVar1 = param_1 & 0x7ff;
  uVar2 = (int)(param_1 & 0xffff) >> 0xb;
  if ((uVar2 < 0xc) && (uVar1 < *(ushort *)(((undefined *)camry_host_ptr((uint32_t)(0x21d28u + (uint32_t)(uVar2 * 2) * 1u)))))) {
    if ((DAT_00021d24 != '\0') ||
       (uVar3 = (uint)(*((ushort *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x21d70u + (uint32_t)(uVar2) * 4u)))) + uVar1 * 2)))),
       pcVar4 = (uint32_t)((uint32_t)(PTR_return_only_stub_81d2e_00021f24)), uVar3 == 0xffff)) {
      uVar3 = (*((ushort *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x21d40u + (uint32_t)(uVar2) * 4u)))) + uVar1 * 4)))) & 0x7ff;
      pcVar4 = (uint32_t)((uintptr_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x21ee4u + (uint32_t)((int)(uint)(*((ushort *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x21d40u + (uint32_t)(uVar2) * 4u)))) + uVar1 * 4)))) >> 0xb) * 4u)))) +
                         8)))));
    }
    (*(int (*)())camry_indirect((uint32_t)(pcVar4)))(uVar3);
  }
  return;
}

void call_21ce4_with_masked_u16_81d16(ushort param_1)

{
  (*(int (*)())camry_indirect((uint32_t)(PTR_FUN_00021ce4)))(DAT_00021d1e & param_1);
  return;
}

void return_only_stub_81d2e(void)

{
  return;
}

void dispatch_packed_id_resolved_slot8_81d30(uint param_1)

{
  uint uVar1;
  uint uVar2;
  uint uVar3;
  uint32_t pcVar4;
  uint32_t puVar5;
  
  uVar3 = param_1 & 0x7ff;
  uVar1 = (int)(param_1 & 0xffff) >> 0xb;
  if (0xb < uVar1) {
    return;
  }
  if (*(ushort *)(((undefined *)camry_host_ptr((uint32_t)(0x21d28u + (uint32_t)(uVar1 * 2) * 1u)))) <= uVar3) {
    return;
  }
  if (((DAT_00021d25 != '\0') || ((param_1 & 0xf800) != 0x2000)) ||
     (uVar2 = (uint)(*((ushort *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x21da0u + (uint32_t)(uVar1) * 4u)))) + uVar3 * 2)))),
     pcVar4 = (uint32_t)((uint32_t)(PTR_return_only_stub_81d2e_00021e6c)), uVar2 == 0xffff)) {
    uVar2 = (uint)(*((ushort *)camry_host_ptr((uint32_t)((int)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x21d40u + (uint32_t)(uVar1) * 4u)))) + uVar3 * 4) + 2))));
    puVar5 = PTR_PTR_00021cbc;
    if (uVar2 == 0xffff) {
      if ((DAT_00021d24 == '\0') &&
         (uVar2 = (uint)(*((ushort *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x21d70u + (uint32_t)(uVar1) * 4u)))) + uVar3 * 2)))),
         pcVar4 = (uint32_t)((uint32_t)(PTR_return_only_stub_81d2e_00021f24)), uVar2 != 0xffff))
      goto LAB_00081dd4;
      uVar1 = (uint)(*((ushort *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x21d40u + (uint32_t)(uVar1) * 4u)))) + uVar3 * 4))));
      uVar2 = uVar1 & 0x7ff;
      puVar5 = (*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x21ee4u + (uint32_t)((int)uVar1 >> 0xb) * 4u))));
    }
    pcVar4 = (uint32_t)(camry_host_addr(*((code * *)camry_host_ptr((uint32_t)(puVar5 + 8)))));
  }
LAB_00081dd4:
  (*(int (*)())camry_indirect((uint32_t)(pcVar4)))(uVar2);
  return;
}

undefined4 query_2296e_group_slot16_81ddc(uint param_1)

{
  undefined4 uVar1;
  
  if ((param_1 & 0xffff) < (uint)DAT_00021d0c) {
    uVar1 = (*(int (*)())camry_indirect((uint32_t)(((((code *)(uintptr_t)((uint32_t)((uintptr_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x21dd0u + (uint32_t)((int)(uint)(*((ushort *)((uint8_t *)&PTR_DAT_0002296e + ((param_1 & 0xffff) * 2)))) >>
                          0xb) * 4u)))) + 0x10))))))))))))();
  }
  else {
    uVar1 = 0xffffffff;
  }
  return uVar1;
}

undefined4 query_2296e_group_slot20_81e0c(uint param_1)

{
  undefined4 uVar1;
  
  if ((param_1 & 0xffff) < (uint)DAT_00021d0c) {
    uVar1 = (*(int (*)())camry_indirect((uint32_t)(((((code *)(uintptr_t)((uint32_t)((uintptr_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x21dd0u + (uint32_t)((int)(uint)(*((ushort *)((uint8_t *)&PTR_DAT_0002296e + ((param_1 & 0xffff) * 2)))) >>
                          0xb) * 4u)))) + 0x14))))))))))))();
  }
  else {
    uVar1 = 0xffffffff;
  }
  return uVar1;
}

undefined4 call_21cd4_with_prefixed_u16_byte_u16_81e72(ushort param_1,undefined1 param_2,undefined2 param_3)

{
  return (*(int (*)())camry_indirect((uint32_t)(PTR_FUN_00021cd4)))(DAT_00021d22 | param_1,param_2,param_3);
}

undefined4 call_21cd8_with_prefixed_u16_81e90(ushort param_1)

{
  return (*(int (*)())camry_indirect((uint32_t)(PTR_FUN_00021cd8)))(DAT_00021d22 | param_1);
}

undefined4 query_22962_group_slot8_with_byte_u16_81eb2(uint param_1,undefined1 param_2,undefined2 param_3)

{
  undefined4 uVar1;
  
  if ((param_1 & 0xffff) < (uint)DAT_00021d0e) {
    uVar1 = (*(int (*)())camry_indirect((uint32_t)(((((code *)(uintptr_t)((uint32_t)((uintptr_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x21dd0u + (uint32_t)((int)(uint)*(ushort *)(((undefined *)camry_host_ptr((uint32_t)(0x22962u + (uint32_t)((param_1 & 0xffff) * 2) * 1u)))) >> 0xb) * 4u)))) + 8
                        ))))))))))))((uint)*(ushort *)(((undefined *)camry_host_ptr((uint32_t)(0x22962u + (uint32_t)((param_1 & 0xffff) * 2) * 1u)))),param_2,param_3
                          );
  }
  else {
    uVar1 = 1;
  }
  return uVar1;
}

undefined4 query_22962_group_slot12_81ee6(uint param_1)

{
  undefined4 uVar1;
  
  if ((param_1 & 0xffff) < (uint)DAT_00021d0e) {
    uVar1 = (*(int (*)())camry_indirect((uint32_t)(((((code *)(uintptr_t)((uint32_t)((uintptr_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x21dd0u + (uint32_t)((int)(uint)*(ushort *)(((undefined *)camry_host_ptr((uint32_t)(0x22962u + (uint32_t)((param_1 & 0xffff) * 2) * 1u)))) >> 0xb) * 4u)))) +
                        0xc))))))))))))();
  }
  else {
    uVar1 = 1;
  }
  return uVar1;
}

undefined4 query_group_callback_with_masked_u16_81f30(uint param_1,ushort param_2)

{
  undefined4 uVar1;
  uint uVar2;
  
  uVar2 = (int)(param_1 & 0xffff) >> 0xb;
  if (uVar2 < 5) {
    uVar1 = (*(int (*)())camry_indirect((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x21f28u + (uint32_t)(uVar2) * 4u))))))(DAT_00021d1e & param_2, (uint)(ushort)param_2);
  }
  else {
    uVar1 = 0xffff;
  }
  return uVar1;
}

undefined4 return_const_0_81f62(void)

{
  return 0;
}

undefined4
change_cantp_receive_connection_if_not_current_81f66(F33CanTpConfiguration *param_1,ushort param_2,char param_3,undefined2 param_4)

{
  uint32_t puVar1;
  F33CanTpRxConnection *pFVar2;
  undefined4 uVar3;
  
  puVar1 = 0xfebeb800u;
  uVar3 = 1;
  pFVar2 = cantp_find_receive_connection(param_1,param_2);
  if (param_2 != (*((ushort *)camry_host_ptr((uint32_t)(puVar1 + (uint)pFVar2->channel_state_index * 0x20 + -0x68ac))))) {
    if (param_3 == '\x01') {
      store_cantp_first_flow_byte_with_complement_7a84c(pFVar2, (uint)(ushort)param_4);
    }
    else {
      store_cantp_second_flow_byte_with_complement_7a89a(pFVar2,param_4);
    }
    uVar3 = 0;
  }
  return uVar3;
}

undefined4 validate_and_change_cantp_receive_connection_81fa6(uint param_1,byte param_2,ushort param_3)

{
  int iVar1;
  undefined4 uVar2;
  
  param_1 = param_1 & 0xffff;
  uVar2 = 1;
  if ((((((int8_t)DAT_febe4f3d) == -0x56) && (iVar1 = camry_host_addr(get_cantp_configuration_pointer_7a32e()), iVar1 != 0)) &&
      ((*((ushort *)camry_host_ptr((uint32_t)(iVar1 + 4)))) <= param_1)) &&
     ((((int)(param_1 - ((uint)(*((byte *)camry_host_ptr((uint32_t)(iVar1 + 0xd)))) + (uint)(*((ushort *)camry_host_ptr((uint32_t)(iVar1 + 4)))))) < 0 &&
       (param_2 < 2)) && (param_3 < 0x100)))) {
    uVar2 = change_cantp_receive_connection_if_not_current_81f66(((F33CanTpConfiguration *)camry_host_ptr((uint32_t)(iVar1))), param_1, param_2, param_3);
  }
  return uVar2;
}

undefined4 return_const_0_81ffa(void)

{
  return 0;
}

undefined4 command_write_bytes_at_memory_cursor_81ffe(int param_1,ushort *param_2)

{
  ushort uVar1;
  undefined1 uVar2;
  uint uVar3;
  uint uVar4;
  uint32_t puVar5;
  int iVar6;
  undefined4 uVar7;
  uint uVar8;
  uint uVar9;
  
  puVar5 = 0x23dfcu;
  uVar3 = (uint)DAT_00022aec;
  uVar1 = *param_2;
  *param_2 = 2;
  if (uVar3 <= uVar1) {
    uVar9 = (uint)(*((byte *)camry_host_ptr((uint32_t)(param_1 + 1))));
    uVar3 = (uint)DAT_00022ac0;
    if ((uVar9 == 0) ||
       (uVar8 = uVar3 - 2,
       (int)(uVar9 - uVar8) < 0 == ((int)uVar8 < 0 && (int)uVar8 < 0 == (int)(uVar9 - uVar8) < 0) &&
       uVar9 != uVar8)) {
      uVar2 = 0x22;
      goto LAB_000820ba;
    }
    if (DAT_00022af5 == '\x01') {
      uVar3 = uVar9 + 2 & 0xff;
    }
    if (uVar1 == uVar3) {
      uVar8 = get_memory_cursor_u32_8228e();
      uVar3 = uVar9 - 1 & 0xff;
      if (uVar3 <= ~uVar8) {
        uVar3 = uVar3 + uVar8;
        iVar6 = wrapper_memory_range_outside_write_window_83098(uVar8,uVar9);
        if ((((*((uint *)camry_host_ptr((uint32_t)(puVar5 + -0x1350)))) <= uVar8) && (uVar3 <= (*((uint *)camry_host_ptr((uint32_t)(puVar5 + -0x1354)))))) &&
           (iVar6 == 0)) {
          uVar7 = call_interrupt_guard_and_return_zero_7a2da();
          for (uVar4 = 0; uVar4 < uVar9; uVar4 = uVar4 + 1 & 0xff) {
            (*((undefined1 *)camry_host_ptr((uint32_t)(uVar4 + uVar8)))) = (*((undefined1 *)camry_host_ptr((uint32_t)(uVar4 + param_1 + 2))));
          }
          ((void)(uVar7), thunk_pop_and_restore_priority_mask_stack_6a4c4());
          set_memory_cursor_u32_82288(uVar3 + 1);
          *param_2 = 1;
          return 0;
        }
      }
      (*((undefined1 *)camry_host_ptr((uint32_t)(param_1 + 1)))) = 0x24;
      return 1;
    }
  }
  uVar2 = 0x21;
LAB_000820ba:
  (*((undefined1 *)camry_host_ptr((uint32_t)(param_1 + 1)))) = uVar2;
  return 1;
}
