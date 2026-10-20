#include "common.h"

undefined4 thunk_classify_secoc_transmit_state_8fa86(void)

{
  return classify_secoc_transmit_state_8fa86();
}

int thunk_classify_three_secoc_receive_states_8f2fc(void)

{
  return classify_three_secoc_receive_states_8f2fc();
}

undefined4 get_aggregate_secoc_activity_status_8f05e(undefined1 *param_1)

{
  undefined1 uVar1;
  int iVar2;
  int iVar3;
  undefined4 uVar4;
  
  uVar4 = 1;
  if (camry_host_addr((param_1))!= 0) {
    uVar4 = 0;
    if (((int16_t)DAT_febe54f4) == -0x1ff) {
      iVar2 = thunk_classify_secoc_transmit_state_8fa86();
      iVar3 = thunk_classify_three_secoc_receive_states_8f2fc();
      if ((iVar2 == 2) || (iVar3 == 2)) {
        uVar1 = 2;
      }
      else if ((iVar2 == 3) || (iVar3 == 3)) {
        uVar1 = 3;
      }
      else {
        uVar1 = 1;
      }
    }
    else {
      uVar1 = 0;
    }
    *param_1 = uVar1;
  }
  return uVar4;
}

undefined4 reset_matching_secoc_freshness_and_age_8f0a8(short param_1)

{
  undefined4 uVar1;
  
  uVar1 = 1;
  if ((((int16_t)DAT_febe54f4) == -0x1ff) && (param_1 == DAT_0002583c)) {
    ((void)(0), clear_secoc_receive_age_8f3ec());
    uVar1 = reset_freshness_for_primary_configured_id_90482(param_1);
  }
  return uVar1;
}

undefined4 reset_matching_secoc_age_8f0d4(short param_1)

{
  undefined4 uVar1;
  
  uVar1 = 1;
  if ((((int16_t)DAT_febe54f4) == -0x1ff) && (param_1 == DAT_0002583c)) {
    ((void)(0), clear_secoc_receive_age_8f3ec());
    uVar1 = 0;
  }
  return uVar1;
}

void thunk_initialize_secoc_context_and_publish_ready_8ed14(void)

{
  initialize_secoc_context_and_publish_ready_8ed14();
  return;
}

void return_only_stub_8f106(void)

{
  return;
}

void return_only_stub_8f108(void)

{
  return;
}

undefined4 return_const_1_8f10e(void)

{
  return 1;
}

undefined4 return_const_1_8f112(void)

{
  return 1;
}

undefined4 return_const_1_8f116(void)

{
  return 1;
}

void initialize_secoc_key_descriptor_and_mirrors_8f11a(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  memzero(((undefined *)camry_host_ptr(0xfebe5504u)),0x14);
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x6300)))) = 0;
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x6302)))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x62fe))))) = 0xe1;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6303))))) = 0xff;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6304))))) = 0xff;
  return;
}

undefined4 store_secoc_key_descriptor_with_byte_complements_8f148(short param_1,int *param_2)

{
  uint32_t puVar1;
  undefined4 uVar2;
  
  puVar1 = 0xfebeb800u;
  uVar2 = 1;
  if ((param_1 == 0) && (*param_2 - 1U < 0x10)) {
    thunk_push_priority_mask_and_raise_to_ff00_6a45e();
    (*((int *)camry_host_ptr((uint32_t)(puVar1 + -0x62fc)))) = *param_2;
    memcpy_forward(((undefined *)camry_host_ptr((uint32_t)(puVar1 + -0x62f8))), param_2 + 1, 0x10);
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6304))))) = ~(byte)*param_2;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6303))))) = ~*(byte *)(param_2 + 1);
    thunk_pop_and_restore_priority_mask_stack_6a4c4();
    uVar2 = 0;
  }
  return uVar2;
}

bool load_secoc_key_descriptor_8f19a(short param_1,undefined4 *param_2)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  if (param_1 == 0) {
    thunk_push_priority_mask_and_raise_to_ff00_6a45e();
    *param_2 = (*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + -0x62fc))));
    memcpy_forward(param_2 + 1, ((undefined *)camry_host_ptr((uint32_t)(puVar1 + -0x62f8))), 0x10);
    thunk_pop_and_restore_priority_mask_stack_6a4c4();
  }
  return param_1 != 0;
}

uint secoc_publish_crypto_qualification(uchar qualified)

{
  undefined1 uVar1;
  uint32_t puVar2;
  uint uVar3;
  
  puVar2 = 0xfebeb800u;
  uVar3 = 0;
  thunk_push_priority_mask_and_raise_to_ff00_6a45e();
  if (qualified == '\x01') {
    uVar1 = 0xd2;
  }
  else {
    if (qualified != '\0') {
      uVar3 = 1;
      goto LAB_0008f1f8;
    }
    uVar1 = 0xe1;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x62fe))))) = uVar1;
LAB_0008f1f8:
  thunk_pop_and_restore_priority_mask_stack_6a4c4();
  return uVar3;
}

uint secoc_crypto_qualification_reported(void)

{
  return (uint)(secoc_crypto_qualification == 0xd2);
}

int validate_secoc_key_byte_complements_8f210(void)

{
  uint32_t puVar1;
  int iVar2;
  
  puVar1 = 0xfebeb800u;
  iVar2 = 2;
  thunk_push_priority_mask_and_raise_to_ff00_6a45e();
  if (((*((uint *)camry_host_ptr((uint32_t)(puVar1 + -0x62fc)))) < 0x11) &&
     ((*((uint *)camry_host_ptr((uint32_t)(puVar1 + -0x62fc)))) == (uint)(byte)~(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6304))))))) {
    if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x62f8))))) == (undefined)~(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6303)))))) {
      iVar2 = 0;
    }
    else {
      iVar2 = 2;
    }
  }
  thunk_pop_and_restore_priority_mask_stack_6a4c4();
  if (iVar2 != 0) {
    (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x6300)))) = 1;
  }
  if ((*((short *)camry_host_ptr((uint32_t)(puVar1 + -0x6300)))) != 0) {
    iVar2 = 2;
    (*((short *)camry_host_ptr((uint32_t)(puVar1 + -0x6300)))) = (*((short *)camry_host_ptr((uint32_t)(puVar1 + -0x6300)))) + -1;
  }
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x6302)))) = 1;
  return iVar2;
}

void initialize_three_secoc_receive_slots_8f26c(void)

{
  uint uVar1;
  uint uVar2;
  uint32_t puVar3;
  puVar3 = 0xfebeb800u;
  memzero(((undefined *)camry_host_ptr(0xfebe5518u)),4);
  memzero(((undefined *)camry_host_ptr((uint32_t)(puVar3 + -0x62e4))), 4);
  memzero(((undefined *)camry_host_ptr((uint32_t)(puVar3 + -0x62d8))), 0x40);
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x62e0)))) = 0;
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x62de)))) = 0;
  uVar2 = 0;
  do {
    uVar1 = uVar2 + 1;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(uVar2 - 0x62dc))))) = 0xe1;
    uVar2 = uVar1;
  } while (uVar1 < 3);
  return;
}

undefined4 find_secoc_receive_slot_by_pdu_id_8f2b0(short param_1,char param_2,ushort *param_3)

{
  ushort uVar1;
  
  if (camry_host_addr((param_3))!= 0) {
    uVar1 = 0;
    if (param_2 == '\0') {
      while (param_1 != (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0x2587cu + (uint32_t)((short)uVar1 * 0x28) * 2u))))) {
        uVar1 = uVar1 + 1;
        if (2 < uVar1) {
          return 1;
        }
      }
LAB_0008f2ec:
      *param_3 = uVar1;
      return 0;
    }
    if (param_2 == '\x01') {
      uVar1 = 0;
      do {
        if (param_1 == (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0x2587eu + (uint32_t)((short)uVar1 * 0x28) * 2u))))) goto LAB_0008f2ec;
        uVar1 = uVar1 + 1;
      } while (uVar1 < 3);
    }
  }
  return 1;
}

int classify_three_secoc_receive_states_8f2fc(void)

{
  char cVar1;
  int iVar2;
  int iVar3;
  uint uVar4;
  
  iVar3 = 0;
  iVar2 = 1;
  uVar4 = 0;
  do {
    cVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe5524u + (uint32_t)(uVar4) * 1u))));
    if (((int8_t)cVar1) != -0x1f) {
      if ((((((int8_t)cVar1) == -0x6a) || (((int8_t)cVar1) == -0x5b)) || (((int8_t)cVar1) == -0x4c)) ||
         ((((int8_t)cVar1) == -0x3d || (((int8_t)cVar1) == -0x2e)))) {
        iVar2 = 2;
      }
      else {
        iVar3 = 0xff;
      }
    }
    uVar4 = uVar4 + 1;
  } while (uVar4 < 3);
  if ((iVar3 == 0xff) && (iVar2 == 1)) {
    iVar2 = 3;
  }
  return iVar2;
}

void queue_or_update_secoc_receive_buffer_8f34a(ushort param_1,undefined4 *param_2)

{
  uint8_t stack_record_14[20];
  uint32_t puVar1;
  int iVar2;
  uint uVar3;
  
  puVar1 = 0xfebeb800u;
  uVar3 = (uint)param_1;
  (*((uint32_t *)(stack_record_14 + 0))) = *param_2;
  (*((uint16_t *)(stack_record_14 + 4))) = *(ushort *)(param_2 + 1);
  if ((*(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x2586cu + (uint32_t)((short)param_1 * 0x50) * 1u)))) & 0xffff) < (uint)(*((uint16_t *)(stack_record_14 + 4)))) {
    (*((uint16_t *)(stack_record_14 + 4))) = (ushort)*(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x2586cu + (uint32_t)((short)param_1 * 0x50) * 1u))));
  }
  thunk_push_priority_mask_and_raise_to_ff00_6a45e();
  if (((int8_t)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(uVar3 - 0x62dc)))))) == -0x1f) {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(uVar3 - 0x62dc))))) = 0xd2;
    thunk_pop_and_restore_priority_mask_stack_6a4c4();
    iVar2 = copy_payload_and_append_queue_slot_8e9c6(1,uVar3,((uint32_t *)(stack_record_14)));
    if (iVar2 != 0) {
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(uVar3 - 0x62dc))))) = 0xe1;
    }
  }
  else {
    if (((int8_t)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(uVar3 - 0x62dc)))))) == -0x2e) {
      copy_payload_at_slot_offset_and_return_view_8eaa0(1,uVar3,0,((uint32_t *)(stack_record_14)));
    }
    thunk_pop_and_restore_priority_mask_stack_6a4c4();
  }
  return;
}

void increment_secoc_receive_age_to_configured_limit_8f3ca(void)

{
  uint32_t puVar1;
  uint32_t puVar2;
  puVar1 = 0xfebeb800u;
  puVar2 = 0x23dfcu;
  thunk_push_priority_mask_and_raise_to_ff00_6a45e();
  if ((*((uint *)camry_host_ptr((uint32_t)(puVar1 + -0x62e4)))) < (uint)(*((ushort *)camry_host_ptr((uint32_t)(puVar2 + 0x1a46))))) {
    (*((uint *)camry_host_ptr((uint32_t)(puVar1 + -0x62e4)))) = (*((uint *)camry_host_ptr((uint32_t)(puVar1 + -0x62e4)))) + 1;
  }
  thunk_pop_and_restore_priority_mask_stack_6a4c4();
  return;
}

void clear_secoc_receive_age_8f3ec(void)

{
  DAT_febe551c = 0;
  return;
}

void begin_secoc_receive_attempt_8f3f2(uint param_1)

{
  char cVar1;
  char cVar2;
  uint32_t puVar3;
  puVar3 = 0xfebeb800u;
  thunk_push_priority_mask_and_raise_to_ff00_6a45e();
  cVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)((param_1 & 0xffff) - 0x62dc)))));
  if ((((int8_t)cVar1) == -0x2e) || (((int8_t)cVar1) == -0x4c)) {
    cVar2 = -0x3d;
  }
  else {
    cVar2 = -0x6a;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)((param_1 & 0xffff) - 0x62dc))))) = cVar2;
  thunk_pop_and_restore_priority_mask_stack_6a4c4();
  if (((int8_t)cVar1) == -0x2e) {
    (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x62e8)))) = 0;
    (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x62e6)))) = 0;
  }
  return;
}

void extract_receive_freshness_and_shift_authenticator_bits_8f434(short param_1,int *param_2,void *param_3)

{
  char *pcVar1;
  byte bVar2;
  uint32_t puVar3;
  uint uVar4;
  uint uVar5;
  int iVar6;
  uint byte_count;
  byte local_30 [16];
  
  puVar3 = 0xfebeb800u;
  iVar6 = param_1 * 0x50;
  if (*(ushort *)(((undefined *)camry_host_ptr((uint32_t)(0x2584eu + (uint32_t)(iVar6) * 1u)))) <= *(ushort *)(param_2 + 1)) {
    bVar2 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x2585du + (uint32_t)(iVar6) * 1u))));
    uVar4 = (uint)(ushort)(*(ushort *)(param_2 + 1) - *(ushort *)(((undefined *)camry_host_ptr((uint32_t)(0x2584eu + (uint32_t)(iVar6) * 1u)))));
    memcpy_forward(param_3,((void *)camry_host_ptr((uint32_t)(*param_2 + uVar4))),bVar2 + 7 >> 3);
    uVar5 = bVar2 & 7;
    byte_count = *(ushort *)(((undefined *)camry_host_ptr((uint32_t)(0x2584au + (uint32_t)(iVar6) * 1u)))) + 7 >> 3;
    memcpy_forward(local_30,((void *)camry_host_ptr((uint32_t)(*param_2 + (bVar2 >> 3) + uVar4))),byte_count);
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x62ac))))) = local_30[0] << uVar5;
    for (uVar4 = 1; uVar4 < byte_count; uVar4 = uVar4 + 1 & 0xffff) {
      bVar2 = local_30[uVar4];
      pcVar1 = ((undefined *)camry_host_ptr((uint32_t)(puVar3 + (uVar4 - 0x62ac))));
      pcVar1[-1] = pcVar1[-1] | (byte)((int)(uint)bVar2 >> (8 - uVar5 & 0x1f));
      *pcVar1 = bVar2 << uVar5;
    }
  }
  return;
}

void notify_configured_receive_profile_status_8f4d0(short param_1,short param_2)

{
  if ((((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x25867u + (uint32_t)(param_1 * 0x50) * 1u)))) == '\0') ||
      (((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x25867u + (uint32_t)(param_1 * 0x50) * 1u)))) == '\x01' && (param_2 != 0)))) &&
     (PTR_crypto_bank_record_profile_status_00025818 != 0)) {
    (*(void (*)(uint))camry_indirect((uint32_t)(PTR_crypto_bank_record_profile_status_00025818)))(
        (uint)(*((volatile uint16_t *)camry_host_ptr((uint32_t)(0x2585au + (uint32_t)(param_1 * 0x50))))) |
        ((uint)(ushort)param_2 << 16));
  }
  return;
}

void invoke_slot_receive_result_callback_8f506(short param_1)

{
  if ((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x25894u + (uint32_t)(param_1 * 0x14) * 4u)))) !=0x0u) {
    (*(int (*)())camry_indirect((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x25894u + (uint32_t)(param_1 * 0x14) * 4u))))))();
  }
  return;
}

void notify_receive_data_id_callback_8f528(short param_1)

{
  if (PTR_FUN_00025820 != 0) {
    (*(int (*)())camry_indirect((uint32_t)(PTR_FUN_00025820)))(*(undefined2 *)(((undefined *)camry_host_ptr((uint32_t)(0x25852u + (uint32_t)(param_1 * 0x50) * 1u)))));
  }
  return;
}

undefined2 deliver_secoc_receive_payload_8f546(ushort param_1,undefined2 param_2)

{
  uint8_t stack_record_20[32];
  camry_fill_bytes(stack_record_20, sizeof stack_record_20);
  uint32_t puVar1;
  int iVar2;
  
  puVar1 = 0xfebeb800u;
  iVar2 = get_queue_slot_payload_view_clamped_8eb1c(1,(uint)param_1,((uint32_t *)(stack_record_20)));
  if (iVar2 == 0) {
    (*((uint32_t *)(stack_record_20 + 8))) = (*((uint32_t *)(stack_record_20 + 0)));
    (*((uint16_t *)(stack_record_20 + 12))) = (*((uint16_t *)(stack_record_20 + 4)));
    ((void)(((uint32_t *)((stack_record_20 + 8)))), dispatch_mapped_callback8_by_packed_route_id_90204((*((volatile uint16_t *)camry_host_ptr((uint32_t)(0x2587eu + (uint32_t)((short)param_1 * 0x28) * 2u))))));
  }
  else {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(param_1 - 0x62dc))))) = 0x96;
    param_2 = 0x103;
  }
  return param_2;
}

uint32_t notify_receive_failure_and_conditionally_deliver_8f596(ushort param_1)

{
  uint32_t camry_r10_result;
  uint32_t puVar1;
  uint32_t puVar2;
  uint uVar3;
  uint uVar4;
  undefined4 uVar5;
  
  puVar1 = 0xfebeb800u;
  puVar2 = 0x23dfcu;
  uVar3 = (uint)param_1;
  if (((int8_t)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe5524u + (uint32_t)(uVar3) * 1u))))) == -0x5b) {
    uVar5 = 2;
  }
  else {
    uVar5 = 1;
  }
  notify_configured_receive_profile_status_8f4d0(uVar3,uVar5);
  ((void)(uVar5), invoke_slot_receive_result_callback_8f506(uVar3));
  notify_receive_data_id_callback_8f528(uVar3);
  uVar4 = (camry_r10_result = secoc_crypto_qualification_reported());
  if ((uVar4 == 1) ||
     (((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x25851u + (uint32_t)((short)param_1 * 0x50) * 1u)))) != '\x01' &&
      ((*((uint *)camry_host_ptr((uint32_t)(puVar1 + -0x62e4)))) < (uint)(*((ushort *)camry_host_ptr((uint32_t)(puVar2 + 0x1a46)))))))) {
    (camry_r10_result = deliver_secoc_receive_payload_8f546(uVar3,0x103));
  }
  return camry_r10_result;
}

void invoke_freshness_exhaustion_callback_8f5f8(undefined2 param_1)

{
  if (PTR_FUN_0002581c != 0) {
    (*(int (*)())camry_indirect((uint32_t)(PTR_FUN_0002581c)))(param_1);
  }
  return;
}

short retry_receive_freshness_or_report_failure_8f60e(ushort param_1,short param_2)

{
  uint uVar1;
  undefined4 uVar2;
  short sVar3;
  
  uVar1 = (uint)param_1;
  if (DAT_febe551a < *(ushort *)(((undefined *)camry_host_ptr((uint32_t)(0x25858u + (uint32_t)((short)param_1 * 0x50) * 1u))))) {
    sVar3 = 0x103;
    if (((int8_t)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe5524u + (uint32_t)(uVar1) * 1u))))) == -0x3d) {
      DAT_febe551a = DAT_febe551a + 1;
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe5524u + (uint32_t)(uVar1) * 1u)))) = -0x4c;
      DAT_febe5518 = 0;
      sVar3 = param_2;
    }
    if (param_2 == 0x201) {
      uVar2 = 2;
    }
    else {
      uVar2 = 1;
    }
    notify_configured_receive_profile_status_8f4d0(uVar1,uVar2);
  }
  else {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe5524u + (uint32_t)(uVar1) * 1u)))) = 0x96;
    notify_receive_failure_and_conditionally_deliver_8f596((uint)(ushort)param_1);
    sVar3 = 0x102;
  }
  return sVar3;
}

int verify_receive_authenticator_with_staged_key_8f676(undefined2 param_1, undefined4 param_2)

{
  uint32_t puVar1;
  int iVar2;
  
  puVar1 = 0xfebeb800u;
  iVar2 = set_word13b0_when_status_one_89c5a((uint)(ushort)param_1, param_2);
  if ((iVar2 == 0) &&
     (iVar2 = set_words13b4_and13b8_89c8c(param_1, ((uint32_t)((uint32_t)(puVar1 + -0x62d4))),  (*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + -0x62d8))))), iVar2 == 0))
  {
    iVar2 = submit_89646_and_poll_completion13be_89c98(param_1, ((uint32_t)((uint32_t)(puVar1 + -0x62ac))),  (*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + -0x62b0)))), ((uint32_t)((uint32_t)(puVar1 + -0x629c))));
  }
  return iVar2;
}

undefined2 retry_receive_crypto_or_report_failure_8f6b2(ushort param_1,undefined2 param_2)

{
  uint uVar1;
  undefined2 uVar2;
  
  uVar1 = (uint)param_1;
  if (DAT_febe5518 < *(ushort *)(((undefined *)camry_host_ptr((uint32_t)(0x25876u + (uint32_t)((short)param_1 * 0x50) * 1u))))) {
    uVar2 = 0x103;
    if (((int8_t)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe5524u + (uint32_t)(uVar1) * 1u))))) == -0x3d) {
      DAT_febe5518 = DAT_febe5518 + 1;
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe5524u + (uint32_t)(uVar1) * 1u)))) = -0x4c;
      uVar2 = param_2;
    }
    notify_configured_receive_profile_status_8f4d0(uVar1,1);
  }
  else {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe5524u + (uint32_t)(uVar1) * 1u)))) = 0x96;
    notify_receive_failure_and_conditionally_deliver_8f596((uint)(ushort)param_1);
    uVar2 = 0x102;
  }
  return uVar2;
}

uint32_t release_secoc_receive_slot_and_clear_work_8f70e(uint param_1)

{
  uint32_t camry_r10_result;
  uint32_t puVar1;
  int iVar2;
  
  puVar1 = 0xfebeb800u;
  iVar2 = (camry_r10_result = unlink_queue_slot_and_clear_payload_8eb7e(1,param_1 & 0xffff));
  if (iVar2 == 0) {
    memzero(((undefined *)camry_host_ptr((uint32_t)(puVar1 + -0x62e8))), 4);
    memzero(((undefined *)camry_host_ptr((uint32_t)(puVar1 + -0x62d8))), 0x40);
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)((param_1 & 0xffff) - 0x62dc))))) = 0xe1;
  }
  return camry_r10_result;
}

undefined4 prepare_and_verify_secoc_receive_authentication_8f746(ushort param_1)

{
  uint8_t stack_record_58[88];
  uint8_t stack_record_5c[92];
  uint32_t puVar1;
  uint uVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  undefined4 uVar6;
  char *pcVar7;
  int iVar8;
  int iVar9;
  
  puVar1 = 0xfebeb800u;
  uVar2 = (uint)param_1;
  iVar5 = (int)(short)param_1;
  iVar9 = iVar5 * 0x50;
  (*((uint32_t *)(stack_record_5c + 0))) = (uint)(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x2585cu + (uint32_t)(iVar9) * 1u))));
  begin_secoc_receive_attempt_8f3f2((uint)(ushort)param_1);
  pcVar7 = ((undefined *)camry_host_ptr((uint32_t)(puVar1 + (uVar2 - 0x62dc))));
  if (((int8_t)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(uVar2 - 0x62dc)))))) == -0x3d) {
    iVar8 = 1;
    uVar6 = 0;
    iVar3 = get_queue_slot_payload_view_clamped_8eb1c(1,uVar2,(stack_record_5c + 40));
    iVar4 = load_secoc_key_descriptor_8f19a(*(undefined2 *)(((undefined *)camry_host_ptr((uint32_t)(0x2585eu + (uint32_t)(iVar9) * 1u)))),((uint8_t *)((stack_record_58 + 16))));
    if ((iVar3 == 0) && (iVar4 == 0)) {
      if ((*((uint16_t *)(stack_record_5c + 44))) < *(ushort *)(((undefined *)camry_host_ptr((uint32_t)(0x2584eu + (uint32_t)(iVar9) * 1u))))) {
LAB_0008f7ee:
        uVar6 = 0x100;
        *pcVar7 = -0x5b;
        notify_receive_failure_and_conditionally_deliver_8f596(uVar2);
        goto LAB_0008f836;
      }
      extract_receive_freshness_and_shift_authenticator_bits_8f434(uVar2,(stack_record_5c + 40),((uint8_t *)((stack_record_58 + 8))));
      if (*(short *)(((undefined *)camry_host_ptr((uint32_t)(0x25874u + (uint32_t)(iVar9) * 1u)))) == 2) {
        if ((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x25890u + (uint32_t)(iVar5 * 0x14) * 4u)))) != 0x0u) {
          iVar8 = (*(int (*)())camry_indirect((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x25890u + (uint32_t)(iVar5 * 0x14) * 4u))))))((*((volatile uint16_t *)camry_host_ptr((uint32_t)(0x2585au + (uint32_t)(iVar5 * 0x28) * 2u)))),camry_host_addr(((uint8_t *)((stack_record_58 + 8)))),(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x2585du + (uint32_t)(iVar9) * 1u)))),
                             (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x62e6)))),camry_host_addr(((uint8_t *)(stack_record_58))),camry_host_addr(stack_record_5c));
        }
        if (iVar8 == 0x22) goto LAB_0008f7ee;
        if (iVar8 == 0x24) {
          invoke_freshness_exhaustion_callback_8f5f8((*((volatile uint16_t *)camry_host_ptr((uint32_t)(0x2585au + (uint32_t)(iVar5 * 0x28) * 2u)))));
          goto LAB_0008f836;
        }
        if (iVar8 == 0x23) {
          uVar6 = retry_receive_freshness_or_report_failure_8f60e(uVar2,0x201);
          goto LAB_0008f836;
        }
        if (iVar8 == 0) goto LAB_0008f836;
      }
    }
    *pcVar7 = -0x6a;
  }
  uVar6 = 0x103;
LAB_0008f836:
  if (*pcVar7 == -0x3d) {
    (*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + -0x62d8)))) = 0x24;
    (*((uint *)camry_host_ptr((uint32_t)(puVar1 + -0x62b0)))) = (uint)*(ushort *)(((undefined *)camry_host_ptr((uint32_t)(0x2584au + (uint32_t)(iVar9) * 1u))));
    (*((uint16_t *)(stack_record_5c + 56))) = *(undefined2 *)(((undefined *)camry_host_ptr((uint32_t)(0x25852u + (uint32_t)(iVar9) * 1u))));
    (*((uint32_t *)(stack_record_5c + 48))) = (*((uint32_t *)(stack_record_5c + 40)));
    (*((int16_t *)(stack_record_5c + 58))) = (*((uint16_t *)(stack_record_5c + 44))) - *(short *)(((undefined *)camry_host_ptr((uint32_t)(0x2584eu + (uint32_t)(iVar9) * 1u))));
    (*((uint32_t *)(stack_record_58 + 48))) = camry_host_addr(((uint8_t *)(stack_record_58)));
    (*((uint16_t *)(stack_record_5c + 60))) = (undefined2)((*((uint32_t *)(stack_record_5c + 0))) + 7 >> 3);
    serialize_be16_header_and_two_buffers_8ecb2((stack_record_5c + 48),  ((undefined *)camry_host_ptr((uint32_t)(puVar1 + -0x62d4))), ((uint *)camry_host_ptr((uint32_t)((int)0xfebe5528))));
    iVar5 = verify_receive_authenticator_with_staged_key_8f676(*(undefined2 *)(((undefined *)camry_host_ptr((uint32_t)(0x25868u + (uint32_t)(iVar9) * 1u)))), camry_host_addr(((uint8_t *)((stack_record_58 + 16)))));
    if (iVar5 != 0) {
      if (iVar5 == 2) {
        uVar6 = retry_receive_crypto_or_report_failure_8f6b2(uVar2,0x202);
      }
      else {
        uVar6 = 0x101;
        *pcVar7 = -0x6a;
        notify_receive_failure_and_conditionally_deliver_8f596(uVar2);
      }
    }
  }
  if ((*pcVar7 != -0x3d) && (*pcVar7 != -0x4c)) {
    release_secoc_receive_slot_and_clear_work_8f70e(uVar2);
  }
  return uVar6;
}

void notify_receive_freshness_verification_result_8f8d2(short param_1,char param_2)

{
  int iVar1;
  uint uVar2;
  
  iVar1 = (int)param_1;
  if (*(short *)(((undefined *)camry_host_ptr((uint32_t)(0x25874u + (uint32_t)(iVar1 * 0x50) * 1u)))) == 2) {
    uVar2 = (ushort)(*((volatile uint16_t *)camry_host_ptr((uint32_t)(0x2585au + (uint32_t)(iVar1 * 0x28) * 2u)))) | 0x10000;
    if (param_2 == '\0') {
      uVar2 = (uint)(ushort)(*((volatile uint16_t *)camry_host_ptr((uint32_t)(0x2585au + (uint32_t)(iVar1 * 0x28) * 2u))));
    }
    if ((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x25878u + (uint32_t)(iVar1 * 0x14) * 4u)))) != 0u) {
      (*(int (*)())camry_indirect((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x25878u + (uint32_t)(iVar1 * 0x14) * 4u))))))(uVar2, (uint)(byte)param_2);
    }
  }
  return;
}

undefined4 finish_secoc_receive_verification_8f906(ushort param_1)

{
  bool bVar1;
  bool bVar2;
  uint uVar3;
  undefined4 uVar4;
  uint uVar5;
  
  uVar5 = (uint)param_1;
  if (((int8_t)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe5524u + (uint32_t)(uVar5) * 1u))))) == -0x3d) {
    bVar1 = DAT_febe5564 != '\0';
    uVar3 = secoc_crypto_qualification_reported();
    bVar2 = bVar1;
    if ((uVar3 == 1) && ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x25851u + (uint32_t)((short)param_1 * 0x50) * 1u)))) == '\x01')) {
      bVar2 = false;
    }
    notify_receive_freshness_verification_result_8f8d2(uVar5,bVar2);
    if (bVar1) {
      uVar4 = retry_receive_freshness_or_report_failure_8f60e(uVar5,0x200);
    }
    else {
      notify_configured_receive_profile_status_8f4d0(uVar5,0);
      uVar4 = deliver_secoc_receive_payload_8f546(uVar5,0);
    }
  }
  else {
    uVar4 = 0x103;
  }
  if (((int8_t)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe5524u + (uint32_t)(uVar5) * 1u))))) != -0x4c) {
    release_secoc_receive_slot_and_clear_work_8f70e(uVar5);
  }
  return uVar4;
}

int process_next_secoc_receive_slot_8f98c(void)

{
  int iVar1;
  int iVar2;
  undefined2 uStack_a;
  
  iVar2 = 0x300;
  uStack_a = 0;
  iVar1 = get_queue_slot_by_link_position_8e8a0(1,0,&uStack_a);
  if ((iVar1 == 0) && (iVar2 = prepare_and_verify_secoc_receive_authentication_8f746(uStack_a), iVar2 == 0)) {
    iVar2 = finish_secoc_receive_verification_8f906(uStack_a);
  }
  return iVar2;
}

undefined4 check_rotating_secoc_receive_state_8f9c6(void)

{
  char cVar1;
  undefined4 uVar2;
  uint uVar3;
  
  uVar3 = (uint)DAT_febe5520;
  uVar2 = 2;
  if (2 < uVar3) {
    uVar3 = 0;
  }
  cVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe5524u + (uint32_t)(uVar3) * 1u))));
  if ((((((int8_t)cVar1) == -0x6a) || (((int8_t)cVar1) == -0x5b)) || (((int8_t)cVar1) == -0x4c)) ||
     (((((int8_t)cVar1) == -0x3d || (((int8_t)cVar1) == -0x2e)) || (((int8_t)cVar1) == -0x1f)))) {
    uVar2 = 0;
  }
  else {
    DAT_febe5522 = 3;
  }
  if (DAT_febe5522 != 0) {
    DAT_febe5522 = DAT_febe5522 + -1;
    uVar2 = 2;
  }
  DAT_febe5520 = (short)uVar3 + 1;
  return uVar2;
}

void initialize_secoc_transmit_context_8fa20(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  memzero(((undefined *)camry_host_ptr(0xfebe5570u)),0xc);
  memzero(((undefined *)camry_host_ptr((uint32_t)(puVar1 + -0x6284))), 0x3c);
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x6292)))) = 0;
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x6294)))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6298))))) = 0xe1;
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x6296)))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6297))))) = 0x5a;
  return;
}

undefined4 find_single_secoc_transmit_slot_by_pdu_id_8fa5a(short param_1,char param_2,undefined2 *param_3)

{
  short sVar1;
  undefined4 uVar2;
  
  uVar2 = 1;
  if (camry_host_addr((param_3))!= 0) {
    sVar1 = DAT_00025964;
    if (((param_2 != '\0') && (sVar1 = DAT_00025966, param_2 != '\x01')) || (param_1 != sVar1)) {
      return uVar2;
    }
    *param_3 = 0;
    uVar2 = 0;
  }
  return uVar2;
}

undefined4 classify_secoc_transmit_state_8fa86(void)

{
  if (((int8_t)DAT_febe5568) == -0x1f) {
    return 1;
  }
  if ((((((int8_t)DAT_febe5568) != -0x6a) && (((int8_t)DAT_febe5568) != -0x5b)) && (((int8_t)DAT_febe5568) != -0x4c)) &&
     ((((int8_t)DAT_febe5568) != -0x3d && (((int8_t)DAT_febe5568) != -0x2e)))) {
    return 3;
  }
  return 2;
}

uint claim_secoc_tx_snapshot(ushort profile,F33PduInfo *info)

{
  uint8_t stack_record_18[24];
  uint32_t puVar1;
  uint32_t puVar2;
  uint uVar3;
  
  puVar1 = 0xfebeb800u;
  puVar2 = 0x23dfcu;
  uVar3 = 0;
  thunk_push_priority_mask_and_raise_to_ff00_6a45e();
  if ((((int8_t)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6298)))))) == -0x1f) && ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6297))))) == 'Z')) {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6298))))) = 0xd2;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6297))))) = 0xa5;
    (*((short *)camry_host_ptr((uint32_t)(puVar1 + -0x6296)))) = (*((short *)camry_host_ptr((uint32_t)(puVar1 + -0x6296)))) + 1;
  }
  else {
    uVar3 = 0x21;
  }
  thunk_pop_and_restore_priority_mask_stack_6a4c4();
  if (uVar3 == 0) {
    (*((uint32_t *)(stack_record_18 + 0))) = ((uint32_t)(info->data));
    (*((int16_t *)(stack_record_18 + 4))) = info->length - (*((short *)camry_host_ptr((uint32_t)(puVar2 + 0x1b42))));
    uVar3 = copy_payload_and_append_queue_slot_8e9c6(0,profile,((uint32_t *)(stack_record_18)));
    if (uVar3 != 0) {
      thunk_push_priority_mask_and_raise_to_ff00_6a45e();
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6298))))) = 0xe1;
      (*((short *)camry_host_ptr((uint32_t)(puVar1 + -0x6296)))) = (*((short *)camry_host_ptr((uint32_t)(puVar1 + -0x6296)))) + -1;
      thunk_pop_and_restore_priority_mask_stack_6a4c4();
    }
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6297))))) = 0x5a;
  }
  return uVar3;
}

int cancel_secoc_transmit_state_and_release_buffer_8fb52(undefined2 param_1)

{
  char cVar1;
  uint32_t puVar2;
  uint32_t puVar3;
  char cVar4;
  int iVar5;
  
  puVar2 = 0xfebeb800u;
  puVar3 = 0x23dfcu;
  cVar4 = 'Z';
  thunk_push_priority_mask_and_raise_to_ff00_6a45e();
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x6297))))) == 'Z') {
    cVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x6298)))));
    iVar5 = 0;
    if (((int8_t)cVar1) == -0x5b) {
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x6297))))) = 0xa5;
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x6298))))) = 0xe1;
      cVar4 = -0x5b;
    }
    else if (((int8_t)cVar1) == -0x3d) {
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x6298))))) = 0x96;
    }
    else if (((int8_t)cVar1) != -0x6a) {
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x6297))))) = 0xa5;
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x6298))))) = 0xe1;
      if ((((int8_t)cVar1) == -0x2e) || (((int8_t)cVar1) == -0x4c)) {
        (*((short *)camry_host_ptr((uint32_t)(puVar2 + -0x6296)))) = (*((short *)camry_host_ptr((uint32_t)(puVar2 + -0x6296)))) + -1;
      }
    }
  }
  else {
    iVar5 = 1;
  }
  thunk_pop_and_restore_priority_mask_stack_6a4c4();
  if (iVar5 == 0) {
    if (((int8_t)cVar4) == -0x5b) {
      dispatch_group_callback4_by_packed_route_id_901e8((*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + 0x1b68)))));
    }
    if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x6297))))) != 'Z') {
      iVar5 = unlink_queue_slot_and_clear_payload_8eb7e(0,param_1);
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x6297))))) = 0x5a;
    }
  }
  return iVar5;
}

void confirm_secoc_transmit_and_notify_upper_8fc00(undefined2 param_1)

{
  undefined2 uVar1;
  uint32_t puVar2;
  uint32_t puVar3;
  char cVar4;
  
  puVar2 = 0xfebeb800u;
  puVar3 = 0x23dfcu;
  cVar4 = 'Z';
  thunk_push_priority_mask_and_raise_to_ff00_6a45e();
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x6297))))) == 'Z') {
    if (((int8_t)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x6298)))))) == -0x5b) {
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x6297))))) = 0xa5;
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x6298))))) = 0xe1;
      cVar4 = -0x5b;
    }
  }
  thunk_pop_and_restore_priority_mask_stack_6a4c4();
  if (cVar4 != 'Z') {
    unlink_queue_slot_and_clear_payload_8eb7e(0,param_1);
    uVar1 = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + 0x1b6a))));
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x6297))))) = 0x5a;
    dispatch_mapped_callback4_by_packed_route_id_901f6(uVar1);
  }
  return;
}

ushort get_bounded_secoc_pending_transmit_count_8fc58(void)

{
  ushort uVar1;
  
  uVar1 = DAT_00025826;
  if (DAT_febe556a < DAT_00025826) {
    uVar1 = DAT_febe556a;
  }
  return uVar1;
}

void begin_secoc_transmit_attempt_8fc68(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  thunk_push_priority_mask_and_raise_to_ff00_6a45e();
  if (((int8_t)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6298)))))) == -0x2e) {
    (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x6288)))) = 0;
  }
  else {
    if (((int8_t)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6298)))))) != -0x4c) {
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6298))))) = 0x96;
      goto LAB_0008fcac;
    }
    (*((short *)camry_host_ptr((uint32_t)(puVar1 + -0x6288)))) = (*((short *)camry_host_ptr((uint32_t)(puVar1 + -0x6288)))) + 1;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6298))))) = 0xc3;
  (*((short *)camry_host_ptr((uint32_t)(puVar1 + -0x6296)))) = (*((short *)camry_host_ptr((uint32_t)(puVar1 + -0x6296)))) + -1;
LAB_0008fcac:
  thunk_pop_and_restore_priority_mask_stack_6a4c4();
  return;
}

void invoke_transmit_freshness_exhaustion_callback_8fcb4(undefined2 param_1)

{
  if (PTR_FUN_0002581c != 0) {
    (*(int (*)())camry_indirect((uint32_t)(PTR_FUN_0002581c)))(param_1);
  }
  return;
}

int generate_transmit_authenticator_with_staged_key_8fcca(undefined2 param_1, undefined4 param_2)

{
  uint32_t puVar1;
  int iVar2;
  
  puVar1 = 0xfebeb800u;
  iVar2 = set_word13a0_when_status_one_89b84((uint)(ushort)param_1, param_2);
  if ((iVar2 == 0) &&
     (iVar2 = set_words13a4_and13a8_89bb6(param_1, ((uint32_t)((uint32_t)(puVar1 + -0x6280))),  (*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + -0x6284))))), iVar2 == 0))
  {
    iVar2 = submit_89440_and_poll_completion13bc_89bc2(param_1, ((uint32_t)((uint32_t)(puVar1 + -0x6258))),  ((undefined *)camry_host_ptr((uint32_t)(puVar1 + -0x625c))),  0);
  }
  return iVar2;
}

undefined2 retry_secoc_transmit_with_counter_limit_8fd04(undefined4 param_1,undefined2 param_2)

{
  uint32_t puVar1;
  undefined2 uVar2;
  
  puVar1 = 0xfebeb800u;
  if (DAT_febe5578 < DAT_00025942) {
    thunk_push_priority_mask_and_raise_to_ff00_6a45e();
    if ((((int8_t)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6298)))))) == -0x3d) || (uVar2 = 0x104, ((int8_t)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6298)))))) == -0x5b)) {
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6298))))) = 0xb4;
      (*((short *)camry_host_ptr((uint32_t)(puVar1 + -0x6296)))) = (*((short *)camry_host_ptr((uint32_t)(puVar1 + -0x6296)))) + 1;
      uVar2 = param_2;
    }
    thunk_pop_and_restore_priority_mask_stack_6a4c4();
  }
  else {
    uVar2 = 0x103;
    DAT_febe5568 = 0x96;
  }
  return uVar2;
}

int release_secoc_transmit_and_clear_work_8fd5c(undefined2 param_1)

{
  uint32_t puVar1;
  int iVar2;
  
  puVar1 = 0xfebeb800u;
  iVar2 = unlink_queue_slot_and_clear_payload_8eb7e(0,param_1);
  if (iVar2 == 0) {
    memzero(((undefined *)camry_host_ptr((uint32_t)(puVar1 + -0x6290))), 0xc);
    memzero(((undefined *)camry_host_ptr((uint32_t)(puVar1 + -0x6284))), 0x3c);
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6298))))) = 0xe1;
  }
  return iVar2;
}

undefined4 prepare_secoc_transmit_authentication_8fd90(short param_1)

{
  uint8_t stack_record_4c[76];
  uint8_t stack_record_50[80];
  undefined2 uVar1;
  uint32_t puVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  uint32_t pcVar6;
  undefined4 uVar7;
  int iVar8;
  
  puVar2 = 0xfebeb800u;
  iVar5 = (int)param_1;
  iVar8 = iVar5 * 0x44;
  (*((uint32_t *)(stack_record_50 + 0))) = (uint)(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x2594cu + (uint32_t)(iVar8) * 1u))));
  begin_secoc_transmit_attempt_8fc68();
  if (((int8_t)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x6298)))))) == -0x3d) {
    uVar7 = 0;
    iVar3 = get_queue_slot_payload_view_clamped_8eb1c(0,param_1,(stack_record_50 + 32));
    iVar4 = load_secoc_key_descriptor_8f19a(*(undefined2 *)(((undefined *)camry_host_ptr((uint32_t)(0x2594eu + (uint32_t)(iVar8) * 1u)))),((uint8_t *)((stack_record_4c + 8))));
    if ((iVar3 == 0) && (iVar4 == 0)) {
      if ((*(short *)(((undefined *)camry_host_ptr((uint32_t)(0x2595eu + (uint32_t)(iVar8) * 1u)))) == 2) &&
         (pcVar6 = (uint32_t)((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x25978u + (uint32_t)(iVar5 * 0x11) * 4u))))),(uint32_t)(pcVar6) != 0u)) {
        uVar1 = (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0x25946u + (uint32_t)(iVar5 * 0x22) * 2u))));
        (*((uint *)camry_host_ptr((uint32_t)(puVar2 + -0x6290)))) = (uint)(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x2594du + (uint32_t)(iVar8) * 1u))));
        iVar5 = (*(int (*)())camry_indirect((uint32_t)(pcVar6)))(uVar1,camry_host_addr(((uint8_t *)(stack_record_4c))),camry_host_addr(stack_record_50),puVar2 + -0x628c,puVar2 + -0x6290);
        if (iVar5 == 0) goto LAB_0008fe3e;
        if (iVar5 == 0x24) {
          invoke_transmit_freshness_exhaustion_callback_8fcb4(uVar1);
          goto LAB_0008fe3e;
        }
      }
      uVar7 = 0x100;
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x6298))))) = 0x96;
      goto LAB_0008fe3e;
    }
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x6298))))) = 0x96;
  }
  uVar7 = 0x104;
LAB_0008fe3e:
  if (((int8_t)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x6298)))))) == -0x3d) {
    (*((undefined4 *)camry_host_ptr((uint32_t)(puVar2 + -0x6284)))) = 0x24;
    (*((undefined4 *)camry_host_ptr((uint32_t)(puVar2 + -0x625c)))) = 0x10;
    (*((uint16_t *)(stack_record_50 + 48))) = *(undefined2 *)(((undefined *)camry_host_ptr((uint32_t)(0x25944u + (uint32_t)(iVar8) * 1u))));
    (*((uint32_t *)(stack_record_50 + 40))) = (*((uint32_t *)(stack_record_50 + 32)));
    (*((uint16_t *)(stack_record_50 + 50))) = (*((uint16_t *)(stack_record_50 + 36)));
    (*((uint32_t *)(stack_record_4c + 40))) = camry_host_addr(((uint8_t *)(stack_record_4c)));
    (*((uint16_t *)(stack_record_50 + 52))) = (undefined2)((*((uint32_t *)(stack_record_50 + 0))) + 7 >> 3);
    serialize_be16_header_and_two_buffers_8ecb2((stack_record_50 + 40),  ((undefined *)camry_host_ptr((uint32_t)(puVar2 + -0x6280))), ((uint *)camry_host_ptr((uint32_t)((int)0xfebe557c))));
    iVar5 = generate_transmit_authenticator_with_staged_key_8fcca(*(undefined2 *)(((undefined *)camry_host_ptr((uint32_t)(0x25950u + (uint32_t)(iVar8) * 1u)))), camry_host_addr(((uint8_t *)((stack_record_4c + 8)))));
    if (iVar5 != 0) {
      if (iVar5 == 2) {
        uVar7 = retry_secoc_transmit_with_counter_limit_8fd04(param_1,0x202);
      }
      else {
        uVar7 = 0x101;
        (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x6298))))) = 0x96;
      }
    }
  }
  if ((((int8_t)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x6298)))))) != -0x3d) && (((int8_t)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x6298)))))) != -0x4c)) {
    release_secoc_transmit_and_clear_work_8fd5c(param_1);
  }
  return uVar7;
}

void pack_secoc_transmit_freshness_and_authenticator_bits_8fed0(short param_1,int param_2,uint *param_3)

{
  undefined1 *puVar1;
  byte bVar2;
  uint uVar3;
  uint uVar4;
  uint uVar5;
  uint uVar6;
  uint uVar7;
  uint uVar8;
  byte *pbVar9;
  
  uVar3 = (uint)(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x2594du + (uint32_t)(param_1 * 0x44) * 1u))));
  if (DAT_febe5570 <= uVar3) {
    uVar3 = DAT_febe5570;
  }
  for (uVar4 = 0; uVar4 < (uVar3 + 7 >> 3 & 0xffff); uVar4 = uVar4 + 1 & 0xffff) {
    (*((undefined1 *)camry_host_ptr((uint32_t)(uVar4 + param_2)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe5574u + (uint32_t)(uVar4) * 1u))));
  }
  uVar7 = uVar3 & 7;
  uVar5 = (uint)*(ushort *)(((undefined *)camry_host_ptr((uint32_t)(0x2593au + (uint32_t)(param_1 * 0x44) * 1u))));
  if ((uint)(DAT_febe55a4 * 8) <= uVar5) {
    uVar5 = DAT_febe55a4 * 8;
  }
  uVar8 = uVar5 >> 3 & 0xffff;
  uVar6 = 0;
  if (uVar7 == 0) {
    for (; uVar6 < uVar8; uVar6 = uVar6 + 1 & 0xffff) {
      puVar1 = ((undefined1 *)camry_host_ptr((uint32_t)(uVar4 + param_2)));
      uVar4 = uVar4 + 1 & 0xffff;
      *puVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe55a8u + (uint32_t)(uVar6) * 1u))));
    }
    if ((uVar5 & 7) == 0) goto LAB_0008ffce;
    uVar7 = 8 - (uVar5 & 7);
    pbVar9 = ((byte *)camry_host_ptr((uint32_t)(uVar4 + param_2)));
    bVar2 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe55a8u + (uint32_t)(uVar6) * 1u)))) & (byte)((0xff >> (uVar7 & 0x1f)) << (uVar7 & 0x1f));
  }
  else {
    uVar4 = uVar4 - 1 & 0xffff;
    for (; uVar6 < uVar8; uVar6 = uVar6 + 1 & 0xffff) {
      pbVar9 = ((byte *)camry_host_ptr((uint32_t)(uVar4 + param_2)));
      uVar4 = uVar4 + 1 & 0xffff;
      *pbVar9 = *pbVar9 | (byte)((int)(uint)(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe55a8u + (uint32_t)(uVar6) * 1u)))) >> uVar7);
      (*((undefined1 *)camry_host_ptr((uint32_t)(uVar4 + param_2)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe55a8u + (uint32_t)(uVar6) * 1u)))) << (8 - uVar7 & 0x1f);
    }
    if ((uVar5 & 7) == 0) goto LAB_0008ffce;
    uVar8 = 8 - (uVar5 & 7);
    pbVar9 = ((byte *)camry_host_ptr((uint32_t)(uVar4 + param_2)));
    bVar2 = *pbVar9 | (byte)((int)((uint)(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe55a8u + (uint32_t)(uVar6) * 1u)))) &
                                  (0xff >> (uVar8 & 0x1f)) << (uVar8 & 0x1f)) >> uVar7);
  }
  *pbVar9 = bVar2;
LAB_0008ffce:
  *param_3 = uVar3 + uVar5 + 7 >> 3;
  return;
}

undefined4 append_secoc_authentication_and_transmit_lower_pdu_8ffda(short param_1)

{
  uint8_t stack_record_34[52];
  undefined4 camry_r10_0;

  uint8_t stack_record_40[64];
  int iVar1;
  ushort pdu;
  ushort uVar2;
  uint32_t puVar3;
  undefined4 extraout_r6;
  uint32_t extraout_r7;
  int iVar4;
  undefined4 uVar5;
  uint uVar6;
  undefined4 uVar7;
  F33PduInfo FStack_3c;
  
  puVar3 = 0xfebeb800u;
  iVar1 = (int)param_1;
  (*((uint32_t *)(stack_record_40 + 0))) = 0x14;
  if (((int8_t)DAT_febe5568) == -0x3d) {
    uVar7 = 0;
    uVar6 = 1;
    puVar3 = 0xfebeb800u;
    iVar4 = (camry_r10_0 = get_queue_slot_payload_view_clamped_8eb1c(0,param_1,((int32_t *)((stack_record_34 + 20)))));
    uVar2 = (*((uint16_t *)(stack_record_40 + 36)));
    if (iVar4 == 0) {
      uVar5 = (pack_secoc_transmit_freshness_and_authenticator_bits_8fed0(param_1, camry_host_addr(((uint8_t *)(stack_record_34))), stack_record_40), (undefined4)(uintptr_t)camry_r10_0);
      (*((uint16_t *)(stack_record_40 + 36))) = (ushort)(*((uint32_t *)(stack_record_40 + 0)));
      (*((int32_t *)(stack_record_34 + 20))) = ((uint32_t)(extraout_r7));
      iVar4 = copy_payload_at_slot_offset_and_return_view_8eaa0(uVar5,((undefined4)((uint)(ushort)param_1)),uVar2,((int32_t *)((stack_record_34 + 20))));
      if (iVar4 == 0) {
        FStack_3c.data = ((*((int32_t *)(stack_record_34 + 20))));
        FStack_3c.length = (*((uint16_t *)(stack_record_40 + 36)));
        thunk_push_priority_mask_and_raise_to_ff00_6a45e();
        if (((int8_t)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6298)))))) == -0x3d) {
          pdu = (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0x25966u + (uint32_t)(iVar1 * 0x22) * 2u))));
          (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6298))))) = 0xa5;
          uVar6 = secoc_lower_tx(pdu,&FStack_3c);
        }
        thunk_pop_and_restore_priority_mask_stack_6a4c4();
        if (uVar6 == 0) {
          if ((*(short *)(((undefined *)camry_host_ptr((uint32_t)(0x2595eu + (uint32_t)(iVar1 * 0x44) * 1u)))) == 2) &&
             ((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x25960u + (uint32_t)(iVar1 * 0x11) * 4u)))) !=0x0u)) {
            (*(int (*)())camry_indirect((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x25960u + (uint32_t)(iVar1 * 0x11) * 4u))))))((*((volatile uint16_t *)camry_host_ptr((uint32_t)(0x25946u + (uint32_t)(iVar1 * 0x22) * 2u)))));
          }
        }
        else if (uVar6 == 0x20) {
          (*((uint16_t *)(stack_record_40 + 36))) = 0;
          copy_payload_at_slot_offset_and_return_view_8eaa0(0,param_1,uVar2,((int32_t *)((stack_record_34 + 20))));
          uVar7 = retry_secoc_transmit_with_counter_limit_8fd04(param_1,0x203);
        }
        else {
          uVar7 = 0x102;
          (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6298))))) = 0x96;
        }
        goto LAB_000900ce;
      }
    }
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6298))))) = 0x96;
  }
  uVar7 = 0x104;
LAB_000900ce:
  if ((((int8_t)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6298)))))) != -0x4c) && (((int8_t)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6298)))))) != -0x5b)) {
    release_secoc_transmit_and_clear_work_8fd5c(param_1);
  }
  return uVar7;
}
