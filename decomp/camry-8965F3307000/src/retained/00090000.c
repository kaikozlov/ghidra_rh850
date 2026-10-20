#include "common.h"

int process_next_eligible_secoc_transmit_900ea(void)

{
  undefined8 uVar1;
  int iVar2;
  char cVar3;
  short sVar4;
  undefined2 uStack_16;
  
  uVar1 = 0xfebeb800;
  uStack_16 = 0;
  sVar4 = 0;
  cVar3 = -0x1f;
  while( true ) {
    thunk_push_priority_mask_and_raise_to_ff00_6a45e();
    iVar2 = get_queue_slot_by_link_position_8e8a0(0,sVar4,&uStack_16);
    if (iVar2 == 0) {
      cVar3 = (*((char *)camry_host_ptr((uint32_t)((int)uVar1 + -0x6298))));
    }
    thunk_pop_and_restore_priority_mask_stack_6a4c4();
    sVar4 = sVar4 + 1;
    if (iVar2 != 0) break;
    if (((int8_t)cVar3) != -0x5b) {
      iVar2 = prepare_secoc_transmit_authentication_8fd90(uStack_16);
      if (iVar2 == 0) {
        iVar2 = append_secoc_authentication_and_transmit_lower_pdu_8ffda(uStack_16);
      }
      return iVar2;
    }
  }
  return 0x300;
}

undefined4 validate_secoc_transmit_state_and_lock_90146(void)

{
  char cVar1;
  uint32_t puVar2;
  undefined2 uVar3;
  undefined4 uVar4;
  
  puVar2 = 0xfebeb800u;
  uVar4 = 2;
  if (DAT_febe556c != 0) {
    uVar3 = 0;
    puVar2 = 0xfebeb800u;
    thunk_push_priority_mask_and_raise_to_ff00_6a45e();
    if ((((int8_t)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x6298)))))) == -0x2e) || (((int8_t)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x6298)))))) == -0x4c)) {
      uVar3 = 1;
    }
    (*((undefined2 *)camry_host_ptr((uint32_t)(puVar2 + -0x6296)))) = uVar3;
    thunk_pop_and_restore_priority_mask_stack_6a4c4();
  }
  cVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x6298)))));
  if ((((((((int8_t)cVar1) == -0x6a) || (((int8_t)cVar1) == -0x5b)) || (((int8_t)cVar1) == -0x4c)) ||
       ((((int8_t)cVar1) == -0x3d || (((int8_t)cVar1) == -0x2e)))) || (((int8_t)cVar1) == -0x1f)) &&
     (((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x6297))))) == 'Z' || (((int8_t)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x6297)))))) == -0x5b)))) {
    uVar4 = 0;
  }
  else {
    (*((undefined2 *)camry_host_ptr((uint32_t)(puVar2 + -0x6292)))) = 1;
  }
  if ((*((short *)camry_host_ptr((uint32_t)(puVar2 + -0x6292)))) != 0) {
    uVar4 = 2;
    (*((short *)camry_host_ptr((uint32_t)(puVar2 + -0x6292)))) = (*((short *)camry_host_ptr((uint32_t)(puVar2 + -0x6292)))) + -1;
  }
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar2 + -0x6294)))) = 1;
  return uVar4;
}

uint secoc_lower_tx(ushort pdu,F33PduInfo *info)

{
  uint uVar1;
  
  uVar1 = route_secured_lower_tx(pdu,info);
  if (uVar1 == 2) {
    uVar1 = 0x20;
  }
  return uVar1;
}

undefined4 dispatch_group_callback4_by_packed_route_id_901e8(undefined2 param_1)

{
  return dispatch_valid_twelve_bank_callback_slot_four_8160c(param_1);
}

void dispatch_mapped_callback4_by_packed_route_id_901f6(undefined2 param_1)

{
  dispatch_packed_id_primary_slot4_81640(param_1);
  return;
}

void dispatch_mapped_callback8_by_packed_route_id_90204(undefined2 param_1)

{
  dispatch_packed_id_primary_slot8_81ca6(param_1);
  return;
}

void initialize_freshness_check_counters_and_state_90212(void)

{
  DAT_febe55b8 = 0;
  DAT_febe55ba = 0;
  DAT_febe55bc = 0;
  initialize_freshness_histories_and_complements_90502();
  return;
}

undefined4 resolve_primary_freshness_selector_zero_9022a(short param_1,undefined2 *param_2)

{
  undefined4 uVar1;
  
  uVar1 = 0;
  if ((DAT_0002583e == 0) && (param_1 == DAT_0002583c)) {
    *param_2 = 0;
    uVar1 = 1;
    param_2[1] = 0;
  }
  return uVar1;
}

int resolve_receive_freshness_selector_and_slot_90248(short param_1,undefined2 *param_2)

{
  bool bVar1;
  int iVar2;
  short sVar3;
  undefined8 uVar4;
  int iVar5;
  int iVar6;
  uint uVar7;
  short sVar8;
  undefined2 local_1c [2];
  
  uVar4 = 0x23dfc00000000;
  iVar6 = 0;
  sVar8 = 0;
  uVar7 = 0;
  do {
    iVar5 = (int)((ulonglong)uVar4 >> 0x20);
    if ((*((short *)camry_host_ptr((uint32_t)(iVar5 + 0x1a42)))) == 0) {
      iVar2 = (short)uVar7 * 0x50 + iVar5;
      if (param_1 == (*((short *)camry_host_ptr((uint32_t)(iVar2 + 0x1a5e))))) {
        resolve_primary_freshness_selector_zero_9022a((*((undefined2 *)camry_host_ptr((uint32_t)(iVar5 + 0x1a40)))),local_1c);
        *param_2 = local_1c[1];
        bVar1 = (*((char *)camry_host_ptr((uint32_t)(iVar2 + 0x1a55)))) == '\x01';
        sVar3 = sVar8;
        if (bVar1) {
          sVar3 = 0;
        }
        param_2[1] = sVar3;
        if (bVar1) {
          iVar6 = 3;
        }
        else {
          iVar6 = 1;
        }
      }
      if ((*((char *)camry_host_ptr((uint32_t)(iVar2 + 0x1a55)))) != '\x01') {
        sVar8 = sVar8 + 1;
      }
      if (iVar6 != 0) {
        return iVar6;
      }
    }
    uVar7 = uVar7 + 1;
    if (2 < uVar7) {
      return iVar6;
    }
  } while( true );
}

undefined4 resolve_transmit_freshness_selector_zero_902b0(short param_1,undefined2 *param_2)

{
  uint8_t stack_record_c[12];
  undefined4 uVar1;
  
  uVar1 = 0;
  if ((DAT_0002583e == 0) && (param_1 == DAT_00025946)) {
    resolve_primary_freshness_selector_zero_9022a(DAT_0002583c,((uint8_t *)(stack_record_c)));
    param_2[1] = 0;
    uVar1 = 1;
    *param_2 = (*((uint16_t *)(stack_record_c + 2)));
  }
  return uVar1;
}

undefined4 dispatch_freshness_export_by_configured_id_902e4(undefined2 param_1,undefined4 param_2, undefined4 param_3)

{
  uint8_t stack_record_1c[28];

  int iVar1;
  undefined4 uVar2;
  
  iVar1 = resolve_receive_freshness_selector_and_slot_90248(param_1,stack_record_1c);
  if (iVar1 == 1) {
    uVar2 = encode_current_receive_freshness_46bit_9063c((*((uint16_t *)(stack_record_1c + 2))), ((uchar *)camry_host_ptr((uint32_t)(param_2))), ((uint *)camry_host_ptr((uint32_t)(param_3))));
  }
  else {
    uVar2 = 1;
    if ((iVar1 != 2) && (iVar1 == 3)) {
      uVar2 = encode_primary_trip_reset_36bit_906e2((*((uint16_t *)(stack_record_1c + 0))), param_2, ((uint *)camry_host_ptr((uint32_t)(param_3))));
    }
    if ((iVar1 == 0) && (iVar1 = resolve_transmit_freshness_selector_zero_902b0(param_1,stack_record_1c), iVar1 == 1)) {
      uVar2 = encode_current_transmit_freshness_46bit_905de((*((uint16_t *)(stack_record_1c + 2))), ((uchar *)camry_host_ptr((uint32_t)(param_2))), ((uint *)camry_host_ptr((uint32_t)(param_3))));
    }
  }
  return uVar2;
}

undefined4 dispatch_freshness_import_by_configured_id_90342(undefined2 param_1,undefined4 param_2, undefined4 param_3)

{
  uint8_t stack_record_1c[28];

  int iVar1;
  undefined4 uVar2;
  
  iVar1 = resolve_receive_freshness_selector_and_slot_90248(param_1,stack_record_1c);
  if (iVar1 == 1) {
    uVar2 = decode_and_store_receive_freshness_46bit_907ea((*((uint16_t *)(stack_record_1c + 2))), ((uchar *)camry_host_ptr((uint32_t)(param_2))), param_3);
  }
  else {
    uVar2 = 1;
    if ((iVar1 != 2) && (iVar1 == 3)) {
      uVar2 = decode_primary_trip_reset_and_refresh_complements_90874((*((uint16_t *)(stack_record_1c + 0))),param_2,param_3);
    }
    if ((iVar1 == 0) && (iVar1 = resolve_transmit_freshness_selector_zero_902b0(param_1,stack_record_1c), iVar1 == 1)) {
      uVar2 = decode_and_store_transmit_freshness_46bit_907aa((*((uint16_t *)(stack_record_1c + 2))), ((uchar *)camry_host_ptr((uint32_t)(param_2))), param_3);
    }
  }
  return uVar2;
}

undefined4
dispatch_receive_freshness_reconstruction_903a0(undefined2 param_1,undefined4 param_2,undefined4 param_3,undefined2 param_4,
            undefined4 param_5,undefined4 param_6)

{
  uint8_t stack_record_20[32];
  int iVar1;
  undefined4 uVar2;
  
  (*((uint32_t *)(stack_record_20 + 4))) = param_5;
  (*((uint32_t *)(stack_record_20 + 8))) = param_6;
  (*((uint32_t *)(stack_record_20 + 12))) = param_2;
  (*((uint32_t *)(stack_record_20 + 16))) = param_3;
  iVar1 = resolve_receive_freshness_selector_and_slot_90248(param_1,((uint8_t *)(stack_record_20)));
  if (iVar1 == 1) {
    uVar2 = reconstruct_stage_and_encode_receive_freshness_90b8a(((uint8_t *)(stack_record_20)),((uint32_t *)((stack_record_20 + 12))),param_4,((uint32_t *)((stack_record_20 + 4))));
  }
  else {
    uVar2 = 1;
    if ((iVar1 != 2) && (iVar1 == 3)) {
      uVar2 = validate_and_stage_primary_freshness_candidate_90c5e(((uint8_t *)(stack_record_20)),((uint32_t *)((stack_record_20 + 12))),param_4,((uint32_t *)((stack_record_20 + 4))));
    }
  }
  return uVar2;
}

undefined4
dispatch_transmit_freshness_generation_903f6(undefined2 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4,
            undefined4 param_5)

{
  uint8_t stack_record_18[24];
  int iVar1;
  undefined4 uVar2;
  undefined1 auStack_1c [4];
  
  uVar2 = 1;
  (*((uint32_t *)(stack_record_18 + 4))) = param_5;
  (*((uint32_t *)(stack_record_18 + 0))) = param_4;
  (*((uint32_t *)(stack_record_18 + 8))) = param_2;
  (*((uint32_t *)(stack_record_18 + 12))) = param_3;
  iVar1 = resolve_transmit_freshness_selector_zero_902b0(param_1,auStack_1c);
  if (iVar1 == 1) {
    uVar2 = generate_and_stage_next_transmit_freshness_908ba(auStack_1c,(stack_record_18 + 8),stack_record_18);
  }
  return uVar2;
}

void commit_transmit_freshness_for_configured_id_9042a(undefined2 param_1)

{
  uint8_t stack_record_8[8];
  int iVar1;
  
  iVar1 = resolve_transmit_freshness_selector_zero_902b0(param_1,((uint8_t *)(stack_record_8)));
  if (iVar1 == 1) {
    commit_pending_transmit_freshness_if_success_90d42((*((uint16_t *)(stack_record_8 + 2))),1);
  }
  return;
}

void commit_receive_freshness_for_verification_result_90448(uint param_1)

{
  uint8_t stack_record_c[12];
  bool verification_result;
  int iVar1;
  
  verification_result = param_1 >> 0x10 == 0;
  iVar1 = resolve_receive_freshness_selector_and_slot_90248(param_1 & 0xffff,((uint16_t *)(stack_record_c)));
  if (iVar1 == 1) {
    freshness_commit_pending((*((uint16_t *)(stack_record_c + 2))),verification_result);
  }
  else if ((iVar1 != 2) && (iVar1 == 3)) {
    commit_primary_freshness_and_handle_trip_wrap_90e20((*((uint16_t *)(stack_record_c + 0))),verification_result);
  }
  return;
}

bool reset_freshness_for_primary_configured_id_90482(undefined2 param_1)

{
  int iVar1;
  undefined2 local_c[2];
  
  iVar1 = resolve_primary_freshness_selector_zero_9022a(param_1,local_c);
  if (iVar1 == 1) {
    reset_primary_freshness_and_dependent_histories_90e6e(local_c[0],local_c[1]);
  }
  return iVar1 != 1;
}

undefined4 check_primary_freshness_once_per_cycle_904a6(void)

{
  undefined4 uVar1;
  
  if (DAT_febe55b8 == 0) {
    uVar1 = ((void)(0), validate_primary_freshness_word_complements_90eac());
  }
  else {
    uVar1 = 0;
  }
  return uVar1;
}

uint run_freshness_check_and_latch_cycle_error_904c0(void)

{
  uint32_t puVar1;
  uint uVar2;
  
  puVar1 = 0xfebeb800u;
  if (DAT_febe55b8 != 0) {
    DAT_febe55b8 = 0;
  }
  uVar2 = check_primary_freshness_once_per_cycle_904a6();
  if (uVar2 != 0) {
    (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x6246)))) = 1;
    (*((short *)camry_host_ptr((uint32_t)(puVar1 + -0x6244)))) = (short)uVar2;
  }
  if ((*((short *)camry_host_ptr((uint32_t)(puVar1 + -0x6246)))) != 0) {
    uVar2 = (uint)(*((ushort *)camry_host_ptr((uint32_t)(puVar1 + -0x6244))));
    (*((short *)camry_host_ptr((uint32_t)(puVar1 + -0x6246)))) = (*((short *)camry_host_ptr((uint32_t)(puVar1 + -0x6246)))) + -1;
  }
  (*((short *)camry_host_ptr((uint32_t)(puVar1 + -0x6248)))) = (*((short *)camry_host_ptr((uint32_t)(puVar1 + -0x6248)))) + 1;
  return uVar2;
}

void initialize_freshness_histories_and_complements_90502(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  memzero(((undefined *)camry_host_ptr(0xfebe55c0u)),8);
  memzero(((undefined *)camry_host_ptr((uint32_t)(puVar1 + -0x6238))), 8);
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x6228)))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6226))))) = 0;
  (*((uint *)camry_host_ptr((uint32_t)(puVar1 + -0x6230)))) = ~(*((uint *)camry_host_ptr((uint32_t)(puVar1 + -0x6240))));
  (*((uint *)camry_host_ptr((uint32_t)(puVar1 + -0x622c)))) = ~(*((uint *)camry_host_ptr((uint32_t)(puVar1 + -0x623c))));
  memzero(((undefined *)camry_host_ptr((uint32_t)(puVar1 + -0x61f4))), 0xc);
  memzero(((undefined *)camry_host_ptr((uint32_t)(puVar1 + -0x61e8))), 0xc);
  memzero(((undefined *)camry_host_ptr((uint32_t)(puVar1 + -0x6224))), 0x18);
  memzero(((undefined *)camry_host_ptr((uint32_t)(puVar1 + -0x620c))), 0x18);
  return;
}

undefined4 encode_current_transmit_freshness_46bit_905de(short param_1,uchar *param_2,uint *param_3)

{
  uint32_t puVar1;
  undefined4 uVar2;
  F33FreshnessWire local_18;
  
  puVar1 = 0xfebeb800u;
  uVar2 = 1;
  if ((((param_1 == 0) && (camry_host_addr((param_2))!= 0)) && (camry_host_addr((param_3))!= 0)) &&
     (0x2d < *param_3)) {
    thunk_push_priority_mask_and_raise_to_ff00_6a45e();
    local_18.trip = (*((uint *)camry_host_ptr((uint32_t)(puVar1 + -0x61f4))));
    local_18.reset = (*((uint *)camry_host_ptr((uint32_t)(puVar1 + -0x61f0))));
    local_18.message = (*((ushort *)camry_host_ptr((uint32_t)(puVar1 + -0x61ec))));
    thunk_pop_and_restore_priority_mask_stack_6a4c4();
    local_18.reset_low2 = (byte)local_18.reset & 3;
    local_18.bit_length = '.';
    freshness_encode_wire(camry_host_addr(&local_18), camry_host_addr(param_2), camry_host_addr(param_3));
    uVar2 = 0;
  }
  return uVar2;
}

undefined4 encode_current_receive_freshness_46bit_9063c(ushort param_1,uchar *param_2,uint *param_3)

{
  uint *puVar1;
  uint32_t puVar2;
  undefined4 uVar3;
  F33FreshnessWire local_1c;
  
  puVar2 = 0xfebeb800u;
  uVar3 = 1;
  if ((((param_1 < 2) && (camry_host_addr((param_2))!= 0)) && (camry_host_addr((param_3))!= 0)) &&
     (0x2d < *param_3)) {
    thunk_push_priority_mask_and_raise_to_ff00_6a45e();
    puVar1 = ((uint *)camry_host_ptr((uint32_t)(puVar2 + (short)param_1 * 0xc + -0x6224)));
    local_1c.trip = *puVar1;
    local_1c.reset = puVar1[1];
    local_1c.message = (ushort)puVar1[2];
    thunk_pop_and_restore_priority_mask_stack_6a4c4();
    local_1c.reset_low2 = (byte)local_1c.reset & 3;
    local_1c.bit_length = '.';
    freshness_encode_wire(camry_host_addr(&local_1c), camry_host_addr(param_2), camry_host_addr(param_3));
    uVar3 = 0;
  }
  return uVar3;
}

void encode_trip16_reset20_big_endian_906a4(undefined4 *param_1,undefined1 *param_2,uint *param_3)

{
  uint uVar1;
  
  if ((byte)*param_3 < (*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 0xb))))) {
    uVar1 = 0;
  }
  else {
    *param_2 = (char)((uint)*param_1 >> 8);
    param_2[1] = (char)*param_1;
    param_2[2] = (char)((uint)param_1[1] >> 0xc);
    param_2[3] = (char)((uint)param_1[1] >> 4);
    param_2[4] = (char)(param_1[1] << 4);
    uVar1 = (uint)(*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 0xb))));
  }
  *param_3 = uVar1;
  return;
}

undefined4 encode_primary_trip_reset_36bit_906e2(short param_1,int param_2,uint *param_3)

{
  uint8_t stack_record_18[24];
  uint32_t puVar1;
  undefined4 uVar2;
  
  puVar1 = 0xfebeb800u;
  uVar2 = 1;
  if ((((param_1 == 0) && (param_2 != 0)) && (camry_host_addr((param_3))!= 0)) && (0x23 < *param_3)) {
    thunk_push_priority_mask_and_raise_to_ff00_6a45e();
    (*((uint32_t *)(stack_record_18 + 0))) = (*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + -0x6240))));
    (*((uint32_t *)(stack_record_18 + 4))) = (*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + -0x623c))));
    thunk_pop_and_restore_priority_mask_stack_6a4c4();
    (*((uint16_t *)(stack_record_18 + 8))) = 0;
    stack_record_18[10] = 0;
    stack_record_18[11] = 0x24;
    encode_trip16_reset20_big_endian_906a4(((uint32_t *)(stack_record_18)), ((undefined1 *)camry_host_ptr((uint32_t)(param_2))), param_3);
    uVar2 = 0;
  }
  return uVar2;
}

undefined4 decode_and_store_transmit_freshness_46bit_907aa(short param_1,uchar *param_2,int param_3)

{
  uint32_t puVar1;
  undefined4 uVar2;
  F33FreshnessWire local_10;
  
  puVar1 = 0xfebeb800u;
  uVar2 = 1;
  if (((param_1 == 0) && (camry_host_addr((param_2))!= 0)) && (param_3 == 0x2e)) {
    freshness_decode_wire(camry_host_addr(param_2), 0x2e, camry_host_addr(&local_10));
    thunk_push_priority_mask_and_raise_to_ff00_6a45e();
    (*((uint *)camry_host_ptr((uint32_t)(puVar1 + -0x61f4)))) = local_10.trip;
    (*((uint *)camry_host_ptr((uint32_t)(puVar1 + -0x61f0)))) = local_10.reset;
    (*((ushort *)camry_host_ptr((uint32_t)(puVar1 + -0x61ec)))) = local_10.message;
    thunk_pop_and_restore_priority_mask_stack_6a4c4();
    uVar2 = 0;
  }
  return uVar2;
}

undefined4 decode_and_store_receive_freshness_46bit_907ea(ushort param_1,uchar *param_2,int param_3)

{
  uint *puVar1;
  uint32_t puVar2;
  undefined4 uVar3;
  F33FreshnessWire local_14;
  
  puVar2 = 0xfebeb800u;
  uVar3 = 1;
  if (((param_1 < 2) && (camry_host_addr((param_2))!= 0)) && (param_3 == 0x2e)) {
    freshness_decode_wire(camry_host_addr(param_2), 0x2e, camry_host_addr(&local_14));
    thunk_push_priority_mask_and_raise_to_ff00_6a45e();
    puVar1 = ((uint *)camry_host_ptr((uint32_t)(puVar2 + (short)param_1 * 0xc + -0x6224)));
    *puVar1 = local_14.trip;
    puVar1[1] = local_14.reset;
    *(ushort *)(puVar1 + 2) = local_14.message;
    thunk_pop_and_restore_priority_mask_stack_6a4c4();
    uVar3 = 0;
  }
  return uVar3;
}

void decode_trip16_reset20_big_endian_90836(undefined1 *param_1,int param_2,uint *param_3)

{
  undefined1 uVar1;
  uint uVar2;
  
  if (param_2 == 0x24) {
    *param_3 = (uint)CONCAT11(*param_1,param_1[1]);
    uVar2 = (uint)((byte)param_1[4] >> 4) |
            (uint)(byte)param_1[3] << 4 | (uint)(byte)param_1[2] << 0xc;
    uVar1 = 0x24;
  }
  else {
    *param_3 = 0;
    uVar2 = 0;
    uVar1 = 0;
  }
  param_3[1] = uVar2;
  *(undefined2 *)(param_3 + 2) = 0;
  (*((undefined1 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_3) + 10)))) = 0;
  (*((undefined1 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_3) + 0xb)))) = uVar1;
  return;
}

undefined4 decode_primary_trip_reset_and_refresh_complements_90874(short param_1,int param_2,int param_3)

{
  uint8_t stack_record_10[16];
  uint32_t puVar1;
  undefined4 uVar2;
  
  puVar1 = 0xfebeb800u;
  uVar2 = 1;
  if (((param_1 == 0) && (param_2 != 0)) && (param_3 == 0x24)) {
    decode_trip16_reset20_big_endian_90836(((undefined1 *)camry_host_ptr((uint32_t)(param_2))), 0x24, ((uint32_t *)(stack_record_10)));
    thunk_push_priority_mask_and_raise_to_ff00_6a45e();
    (*((uint *)camry_host_ptr((uint32_t)(puVar1 + -0x6240)))) = (*((uint32_t *)(stack_record_10 + 0)));
    (*((uint *)camry_host_ptr((uint32_t)(puVar1 + -0x623c)))) = (*((uint32_t *)(stack_record_10 + 4)));
    (*((uint *)camry_host_ptr((uint32_t)(puVar1 + -0x6230)))) = ~(*((uint32_t *)(stack_record_10 + 0)));
    (*((uint *)camry_host_ptr((uint32_t)(puVar1 + -0x622c)))) = ~(*((uint32_t *)(stack_record_10 + 4)));
    thunk_pop_and_restore_priority_mask_stack_6a4c4();
    uVar2 = 0;
  }
  return uVar2;
}

undefined4 generate_and_stage_next_transmit_freshness_908ba(short *param_1,int *param_2,int *param_3)

{
  uint32_t puVar1;
  F33FreshnessWire *freshness;
  uint *puVar2;
  uint uVar3;
  uint uVar4;
  undefined4 uVar5;
  uint uVar6;
  uint uVar7;
  ushort uVar8;
  F33FreshnessWire local_30;
  
  puVar1 = 0xfebeb800u;
  if (*param_1 != 0) {
    return 1;
  }
  if (param_1[1] != 0) {
    return 1;
  }
  if (*param_2 == 0) {
    return 1;
  }
  if (((uint32_t)(param_2[1]))==camry_host_addr((((uint *)0x0)))) {
    return 1;
  }
  if (*param_3 == 0) {
    return 1;
  }
  if (param_3[1] == 0) {
    return 1;
  }
  if ((*((uint *)camry_host_ptr((uint32_t)(param_2[1] ))))< 0x2e) {
    return 1;
  }
  if (DAT_febe55d8 != 0) {
    return 1;
  }
  thunk_push_priority_mask_and_raise_to_ff00_6a45e();
  uVar3 = (*((uint *)camry_host_ptr((uint32_t)(puVar1 + -0x6240))));
  uVar4 = (*((uint *)camry_host_ptr((uint32_t)(puVar1 + -0x623c))));
  uVar6 = (*((uint *)camry_host_ptr((uint32_t)(puVar1 + -0x61f4))));
  uVar7 = (*((uint *)camry_host_ptr((uint32_t)(puVar1 + -0x61f0))));
  uVar8 = (*((ushort *)camry_host_ptr((uint32_t)(puVar1 + -0x61ec))));
  thunk_pop_and_restore_priority_mask_stack_6a4c4();
  uVar5 = 0;
  if ((uVar3 == uVar6) && (uVar4 == uVar7)) {
    uVar3 = uVar6;
    uVar4 = uVar7;
    if (uVar7 < 0xfffff) {
      if (uVar8 < 0xff) {
        uVar8 = uVar8 + 1;
      }
      goto LAB_00090954;
    }
    uVar8 = 0xff;
  }
  else {
    uVar8 = 0xff;
    if (uVar4 < 0xfffff) {
      uVar8 = 1;
    }
LAB_00090954:
    if (uVar8 != 0xff) goto LAB_0009095e;
  }
  uVar5 = 0x24;
LAB_0009095e:
  thunk_push_priority_mask_and_raise_to_ff00_6a45e();
  (*((uint *)camry_host_ptr((uint32_t)(puVar1 + -0x61e8)))) = uVar3;
  (*((uint *)camry_host_ptr((uint32_t)(puVar1 + -0x61e4)))) = uVar4;
  (*((ushort *)camry_host_ptr((uint32_t)(puVar1 + -0x61e0)))) = uVar8;
  thunk_pop_and_restore_priority_mask_stack_6a4c4();
  puVar2 = ((uint *)camry_host_ptr((uint32_t)(param_2[1])));
  local_30.reset_low2 = (byte)uVar4 & 3;
  uVar6 = *puVar2;
  if (0x2e < uVar6) {
    uVar6 = 0x2e;
    *puVar2 = 0x2e;
  }
  local_30.bit_length = (uchar)uVar6;
  local_30.trip = uVar3;
  local_30.reset = uVar4;
  local_30.message = uVar8;
  freshness_encode_wire(camry_host_addr(&local_30), (uint32_t)(*param_2), camry_host_addr(puVar2));
  puVar2 = ((uint *)camry_host_ptr((uint32_t)(param_3[1])));
  uVar3 = *puVar2;
  if (0x2e < uVar3) {
    uVar3 = 0x2e;
    *puVar2 = 0x2e;
  }
  local_30.bit_length = (uchar)uVar3;
  freshness_encode_wire(camry_host_addr(freshness), (uint32_t)(*param_3), camry_host_addr(puVar2));
  return uVar5;
}

uint reconstruct_stage_and_encode_receive_freshness_90b8a(F33FreshnessSlot *param_1,undefined4 *param_2,ushort param_3,int *param_4)

{
  uint uVar1;
  uint32_t puVar2;
  uint *puVar3;
  uint uVar4;
  F33FreshnessHistory local_2c;
  F33FreshnessWire FStack_20;
  
  puVar2 = 0xfebeb800u;
  uVar4 = 1;
  if ((((param_1->selector == 0) && ((ushort)param_1->slot < 2)) &&
      (((uint32_t)(*param_2))!=camry_host_addr((((uchar *)0x0))))) &&
     (((*param_4 != 0 && (((uint32_t)(param_4[1]))!=camry_host_addr((((uint *)0x0))))) && (0x2d < (*((uint *)camry_host_ptr((uint32_t)(param_4[1])))))))) {
    freshness_decode_wire((uint32_t)(*param_2), param_2[1], camry_host_addr(&FStack_20));
    uVar4 = freshness_reconstruct_candidate(camry_host_addr(param_1), camry_host_addr(&FStack_20), param_3, camry_host_addr(&local_2c));
    if (uVar4 == 0) {
      if (local_2c.message == 0xff) {
        uVar4 = 0x24;
      }
      thunk_push_priority_mask_and_raise_to_ff00_6a45e();
      puVar3 = ((uint *)camry_host_ptr((uint32_t)(puVar2 + param_1->slot * 0xc + -0x620c)));
      *puVar3 = local_2c.trip;
      puVar3[1] = local_2c.reset;
      *(ushort *)(puVar3 + 2) = local_2c.message;
      thunk_pop_and_restore_priority_mask_stack_6a4c4();
      puVar3 = ((uint *)camry_host_ptr((uint32_t)(param_4[1])));
      FStack_20.trip = local_2c.trip;
      FStack_20.message = local_2c.message;
      FStack_20.reset = local_2c.reset;
      FStack_20.reset_low2 = (byte)local_2c.reset & 3;
      uVar1 = *puVar3;
      if (0x2e < uVar1) {
        uVar1 = 0x2e;
        *puVar3 = 0x2e;
      }
      FStack_20.bit_length = (uchar)uVar1;
      freshness_encode_wire(camry_host_addr(&FStack_20), (uint32_t)(*param_4), camry_host_addr(puVar3));
    }
  }
  return uVar4;
}

undefined4 validate_and_stage_primary_freshness_candidate_90c5e(short *param_1,int *param_2,short param_3,int *param_4)

{
  uint8_t stack_record_24[36];
  bool bVar1;
  uint32_t puVar2;
  uint32_t puVar3;
  uint uVar4;
  uint uVar5;
  
  puVar2 = 0xfebeb800u;
  puVar3 = 0x23dfcu;
  bVar1 = false;
  if (*param_1 != 0) {
    return 1;
  }
  if (*param_2 == 0) {
    return 1;
  }
  if (*param_4 == 0) {
    return 1;
  }
  if (((uint32_t)(param_4[1]))!=camry_host_addr((((uint *)0x0)))) {
    if ((*((uint *)camry_host_ptr((uint32_t)(param_4[1] ))))< 0x24) {
      return 1;
    }
    if ((param_2[1] == 0x24) && (param_3 == 0)) {
      decode_trip16_reset20_big_endian_90836(((undefined1 *)camry_host_ptr((uint32_t)(*param_2))), 0x24, ((uint32_t *)(stack_record_24)));
      thunk_push_priority_mask_and_raise_to_ff00_6a45e();
      uVar5 = (*((uint *)camry_host_ptr((uint32_t)(puVar2 + -0x6240))));
      uVar4 = (*((uint *)camry_host_ptr((uint32_t)(puVar2 + -0x623c))));
      thunk_pop_and_restore_priority_mask_stack_6a4c4();
      if ((0xffff - (byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(0x1a48))))) <= uVar5) && ((*((uint32_t *)(stack_record_24 + 0))) != 0)) {
        bVar1 = (*((uint32_t *)(stack_record_24 + 0))) <= (byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(0x1a48))))) + 1;
      }
      if ((uVar5 < (*((uint32_t *)(stack_record_24 + 0)))) || (((uVar5 <= (*((uint32_t *)(stack_record_24 + 0))) && (uVar4 < (*((uint32_t *)(stack_record_24 + 4))))) || (bVar1)))) {
        thunk_push_priority_mask_and_raise_to_ff00_6a45e();
        (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x6226))))) = bVar1;
        (*((uint *)camry_host_ptr((uint32_t)(puVar2 + -0x6238)))) = (*((uint32_t *)(stack_record_24 + 0)));
        (*((uint *)camry_host_ptr((uint32_t)(puVar2 + -0x6234)))) = (*((uint32_t *)(stack_record_24 + 4)));
        thunk_pop_and_restore_priority_mask_stack_6a4c4();
        if (0x24 < (*((uint *)camry_host_ptr((uint32_t)(param_4[1]))))) {
          (*((uint *)camry_host_ptr((uint32_t)(param_4[1] ))))= 0x24;
        }
        encode_trip16_reset20_big_endian_906a4(((uint32_t *)(stack_record_24)), ((undefined1 *)camry_host_ptr((uint32_t)(*param_4))), ((uint *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)((uint8_t *)(param_4) + (4))))))));
        return 0;
      }
      if (((*((uint32_t *)(stack_record_24 + 0))) == uVar5) && ((*((uint32_t *)(stack_record_24 + 4))) == uVar4)) {
        return 1;
      }
    }
    return 0x22;
  }
  return 1;
}

void commit_pending_transmit_freshness_if_success_90d42(short param_1,char param_2)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  if ((param_1 == 0) && (param_2 == '\x01')) {
    thunk_push_priority_mask_and_raise_to_ff00_6a45e();
    memcpy_forward(((undefined *)camry_host_ptr((uint32_t)(puVar1 + -0x61f4))), ((undefined *)camry_host_ptr((uint32_t)(puVar1 + -0x61e8))), 0xc);
    thunk_pop_and_restore_priority_mask_stack_6a4c4();
  }
  return;
}

void clear_matching_freshness_histories_90d9e(short param_1)

{
  short sVar1;
  uint32_t puVar2;
  uint32_t puVar3;
  uint uVar4;
  short sVar5;
  int iVar6;
  
  puVar2 = 0xfebeb800u;
  puVar3 = 0x23dfcu;
  sVar5 = 0;
  uVar4 = 0;
  do {
    sVar1 = (*((short *)camry_host_ptr((uint32_t)(puVar3 + 0x1a42))));
    if ((sVar1 == 0) && (iVar6 = (short)uVar4 * 0x50, (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(iVar6 + 0x1a55))))) != '\x01')) {
      if ((*((short *)camry_host_ptr((uint32_t)(puVar3 + iVar6 + 0x1a50)))) == param_1) {
        thunk_push_priority_mask_and_raise_to_ff00_6a45e();
        memzero(((undefined *)camry_host_ptr((uint32_t)(puVar2 + sVar5 * 0xc + -0x6224))), 0xc);
        memzero(((undefined *)camry_host_ptr((uint32_t)(puVar2 + sVar5 * 0xc + -0x620c))), 0xc);
        thunk_pop_and_restore_priority_mask_stack_6a4c4();
      }
      sVar5 = sVar5 + 1;
    }
    uVar4 = uVar4 + 1;
  } while (uVar4 < 3);
  if ((sVar1 == 0) && ((*((short *)camry_host_ptr((uint32_t)(puVar3 + 0x1b40)))) == param_1)) {
    thunk_push_priority_mask_and_raise_to_ff00_6a45e();
    memzero(((undefined *)camry_host_ptr((uint32_t)(puVar2 + -0x61f4))), 0xc);
    memzero(((undefined *)camry_host_ptr((uint32_t)(puVar2 + -0x61e8))), 0xc);
    thunk_pop_and_restore_priority_mask_stack_6a4c4();
  }
  return;
}

void commit_primary_freshness_and_handle_trip_wrap_90e20(short param_1,char param_2)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  if (param_1 == 0) {
    if (param_2 == '\x01') {
      puVar1 = 0xfebeb800u;
      thunk_push_priority_mask_and_raise_to_ff00_6a45e();
      memcpy_forward(((undefined *)camry_host_ptr((uint32_t)(puVar1 + -0x6240))), ((undefined *)camry_host_ptr((uint32_t)(puVar1 + -0x6238))), 8);
      (*((uint *)camry_host_ptr((uint32_t)(puVar1 + -0x6230)))) = ~(*((uint *)camry_host_ptr((uint32_t)(puVar1 + -0x6240))));
      (*((uint *)camry_host_ptr((uint32_t)(puVar1 + -0x622c)))) = ~(*((uint *)camry_host_ptr((uint32_t)(puVar1 + -0x623c))));
      thunk_pop_and_restore_priority_mask_stack_6a4c4();
      if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6226))))) == '\x01') {
        clear_matching_freshness_histories_90d9e(0);
      }
    }
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6226))))) = 0;
  }
  return;
}

void reset_primary_freshness_and_dependent_histories_90e6e(short param_1,short param_2)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  if ((param_1 == 0) && (param_2 == 0)) {
    thunk_push_priority_mask_and_raise_to_ff00_6a45e();
    (*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + -0x6240)))) = 0;
    (*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + -0x623c)))) = 0;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6226))))) = 0;
    (*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + -0x6238)))) = 0;
    (*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + -0x6234)))) = 0;
    (*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + -0x6230)))) = 0xffffffff;
    (*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + -0x622c)))) = 0xffffffff;
    thunk_pop_and_restore_priority_mask_stack_6a4c4();
    clear_matching_freshness_histories_90d9e(0);
  }
  return;
}

undefined4 validate_primary_freshness_word_complements_90eac(void)

{
  uint32_t puVar1;
  undefined4 uVar2;
  uint uVar3;
  uint uVar4;
  uint uVar5;
  uint uVar6;
  
  puVar1 = 0xfebeb800u;
  thunk_push_priority_mask_and_raise_to_ff00_6a45e();
  uVar5 = (*((uint *)camry_host_ptr((uint32_t)(puVar1 + -0x6240))));
  uVar4 = (*((uint *)camry_host_ptr((uint32_t)(puVar1 + -0x623c))));
  uVar6 = (*((uint *)camry_host_ptr((uint32_t)(puVar1 + -0x6230))));
  uVar3 = (*((uint *)camry_host_ptr((uint32_t)(puVar1 + -0x622c))));
  thunk_pop_and_restore_priority_mask_stack_6a4c4();
  if ((uVar6 == ~uVar5) && (uVar3 == ~uVar4)) {
    (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x6228)))) = 0;
    uVar2 = 0;
  }
  else {
    uVar2 = 2;
    (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x6228)))) = 2;
  }
  return uVar2;
}

void reset_dcm_active_service_and_final_nrc_90ee6(void)

{
  clear_dcm_active_service_callback_913b6();
  clear_dcm_final_negative_response_code_912b2();
  return;
}

uint dcm_application_policy_hook
               (uchar service_id,uchar *request,ushort request_length,uchar addressing_flags,
               ushort service_list_selector,uchar *negative_response)

{
  uint uVar1;
  
  uVar1 = check_diagnostic_addressing_admission(addressing_flags);
  if (uVar1 == 0) {
    uVar1 = 0;
  }
  else {
    uVar1 = 8;
  }
  return uVar1;
}

uint dcm_check_session_list(uchar *allowed,uchar count)

{
  uint uVar1;
  uint uVar2;
  uchar uStack_11;
  
  uVar2 = 1;
  uStack_11 = '\x01';
  if (camry_host_addr((allowed))== 0) {
LAB_00090f50:
    uVar2 = 0;
  }
  else {
    dcm_get_session(&uStack_11);
    for (uVar1 = 0; uVar1 < count; uVar1 = uVar1 + 1 & 0xff) {
      if (uStack_11 == allowed[uVar1]) goto LAB_00090f50;
    }
  }
  return uVar2;
}

uint dcm_check_security_list(uchar *allowed,uchar count)

{
  uint uVar1;
  uint uVar2;
  uchar uStack_11;
  
  uStack_11 = '\0';
  uVar2 = 1;
  if (camry_host_addr((allowed))== 0) {
LAB_00090f90:
    uVar2 = 0;
  }
  else {
    dcm_get_security_level(&uStack_11);
    for (uVar1 = 0; uVar1 < count; uVar1 = uVar1 + 1 & 0xff) {
      if (uStack_11 == allowed[uVar1]) goto LAB_00090f90;
    }
  }
  return uVar2;
}

uint dcm_resolve_service
               (F33DcmMessageContext *message,F33DcmServiceSelection *selection,
               uchar *has_subfunction,uchar *negative_response)

{
  uchar uVar1;
  F33DcmService *pFVar2;
  uint uVar3;
  F33DcmServiceList *pFVar4;
  
  *has_subfunction = '\0';
  pFVar2 = (F33DcmService *)0x0;
  *negative_response = '\0';
  selection->service = 0;
  uVar3 = 0;
  do {
    pFVar4 = ((void *)camry_host_ptr((uint32_t)(selection->list)));
    if (pFVar4->count <= uVar3) {
LAB_00090ffa:
      if (camry_host_addr(pFVar2)==camry_host_addr((F33DcmService *)0x0)) {
        *negative_response = '\x11';
      }
      else {
        if ((pFVar2->has_subfunctions == '\x01') && (pFVar2->sid != '1')) {
          *has_subfunction = '\x01';
        }
        uVar3 = dcm_check_session_list
                          (((uint8_t *)camry_host_ptr((uint32_t)(((F33DcmService *)camry_host_ptr((uint32_t)(selection->service)))->sessions))),((F33DcmService *)camry_host_ptr((uint32_t)(selection->service)))->session_count);
        if (uVar3 == 0) {
          uVar3 = dcm_check_security_list
                            (((uint8_t *)camry_host_ptr((uint32_t)(((F33DcmService *)camry_host_ptr((uint32_t)(selection->service)))->security))),((F33DcmService *)camry_host_ptr((uint32_t)(selection->service)))->security_count);
          if (uVar3 == 0) {
            return 0;
          }
          uVar1 = '3';
        }
        else {
          uVar1 = '\x7f';
        }
        *negative_response = uVar1;
      }
      return 1;
    }
    if (*((uint8_t *)camry_host_ptr((uint32_t)(message->request))) == (*((volatile uint8_t *)camry_host_ptr((uint32_t)((uint32_t)(0x25c54u + (uint32_t)((short)(*((volatile uint16_t *)camry_host_ptr((uint32_t)((uint32_t)(pFVar4->indices) + (uint32_t)(uVar3) * 2u))))) * (uint32_t)sizeof(F33DcmService)) + (uint32_t)(0) * (uint32_t)sizeof(F33DcmService) + (uint32_t)offsetof(F33DcmService, sid)))))) {
      pFVar2 = ((volatile F33DcmService *)camry_host_ptr((uint32_t)(0x25c54u + (uint32_t)((short)(*((volatile uint16_t *)camry_host_ptr((uint32_t)((uint32_t)(pFVar4->indices) + (uint32_t)(uVar3) * 2u))))) * (uint32_t)sizeof(F33DcmService))));
      selection->service = camry_host_addr(pFVar2);
      goto LAB_00090ffa;
    }
    uVar3 = uVar3 + 1 & 0xffff;
  } while( true );
}
