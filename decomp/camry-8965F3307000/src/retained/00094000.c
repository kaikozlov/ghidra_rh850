#include "common.h"

void dcm_set_pending_dispatch_receive_slot_94008(ushort param_1)

{
  dcm_pending_dispatch_receive_slot = param_1;
  return;
}

ushort dcm_get_pending_dispatch_receive_slot_9400e(void)

{
  return dcm_pending_dispatch_receive_slot;
}

bool dcm_slot_matches_pending_protocol_and_connection_94014(undefined2 param_1)

{
  uint8_t stack_record_14[20];
  int extraout_r8;
  
  (*((int16_t *)(stack_record_14 + 0))) = 0;
  (*((int16_t *)(stack_record_14 + 2))) = 0;
  (*((int16_t *)(stack_record_14 + 4))) = 0;
  (*((int16_t *)(stack_record_14 + 6))) = 0;
  dcm_get_route_protocol_and_connection_indices_93cce(dcm_pending_dispatch_receive_slot,stack_record_14,(stack_record_14 + 2));
  dcm_get_route_protocol_and_connection_indices_93cce(param_1, (stack_record_14 + 4), ((ushort *)camry_host_ptr((uint32_t)(extraout_r8 + 4))));
  return (*((int16_t *)(stack_record_14 + 0))) == (*((int16_t *)(stack_record_14 + 4))) && (*((int16_t *)(stack_record_14 + 2))) == (*((int16_t *)(stack_record_14 + 6)));
}

void dcm_enqueue_receive_slot_in_two_entry_ring_9405c(undefined2 param_1)

{
  uint uVar1;
  
  uVar1 = DAT_febe59e6 + 1;
  *(undefined2 *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe59dcu + (uint32_t)((uint)DAT_febe59e6 * 2) * 1u)))) = param_1;
  DAT_febe59e6 = (ushort)uVar1;
  if (1 < (uVar1 & 0xffff)) {
    DAT_febe59e6 = 0;
  }
  return;
}

undefined2 dcm_dequeue_receive_slot_from_two_entry_ring_9407c(void)

{
  uint uVar1;
  uint uVar2;
  uint uVar3;
  
  uVar2 = (uint)DAT_febe59e4;
  uVar1 = uVar2 + 1;
  uVar3 = uVar1 & 0xffff;
  DAT_febe59e4 = (ushort)uVar1;
  if (1 < uVar3) {
    DAT_febe59e4 = 0;
    uVar3 = 0;
  }
  if (uVar3 == DAT_febe59e6) {
    DAT_febe59e4 = 0;
    DAT_febe59e6 = 0;
  }
  return *(undefined2 *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe59dcu + (uint32_t)(uVar2 * 2) * 1u))));
}

ushort dcm_get_receive_slot_remaining_capacity_940ae(uint param_1)

{
  return (*((volatile uint16_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe59f0u + (uint32_t)(param_1 & 0xffff) * (uint32_t)sizeof(F33DcmReceiveBufferState)) + (uint32_t)(0) * (uint32_t)sizeof(F33DcmReceiveBufferState) + (uint32_t)offsetof(F33DcmReceiveBufferState, remaining_capacity)))));
}

uint32_t dcm_save_current_transmit_id_as_displaced_940ba(void)

{
  uint32_t camry_r10_result;
  uint32_t puVar1;
  undefined2 uVar2;
  
  puVar1 = 0xfebeb800u;
  uVar2 = (camry_r10_result = dcm_get_current_transmit_id_93e82());
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x5e18)))) = uVar2;
  return camry_r10_result;
}

ushort dcm_get_displaced_transmit_id_940ca(void)

{
  return dcm_displaced_transmit_id;
}

void dcm_set_selected_zero_timeout_flag_940d0(uchar param_1,char param_2)

{
  if (param_2 == '\0') {
    dcm_zero_p2_deadline = param_1;
    return;
  }
  if (param_2 == '\x01') {
    dcm_zero_overall_timeout = param_1;
  }
  return;
}

uchar dcm_get_selected_zero_timeout_flag_940e6(char param_1)

{
  uchar uVar1;
  
  if (param_1 == '\0') {
    return dcm_zero_p2_deadline;
  }
  uVar1 = '\0';
  if (param_1 == '\x01') {
    uVar1 = dcm_zero_overall_timeout;
  }
  return uVar1;
}

void dcm_binary_search_did_class_range_940fe(ushort param_1,ushort *param_2,uint param_3,undefined1 *param_4)

{
  uint uVar1;
  uint uVar2;
  ushort uVar3;
  
  uVar2 = param_3 & 0xffff;
  do {
    uVar3 = *param_2;
    if (uVar2 <= uVar3) {
      return;
    }
    uVar1 = (int)(uVar3 + uVar2) >> 1;
    if ((*((volatile uint16_t *)camry_host_ptr((uint32_t)((uint32_t)(0x2603cu + (uint32_t)((short)uVar1) * (uint32_t)sizeof(F33DcmDidClass)) + (uint32_t)(0) * (uint32_t)sizeof(F33DcmDidClass) + (uint32_t)offsetof(F33DcmDidClass, last_did))))) < param_1) {
      uVar3 = (short)uVar1 + 1;
      *param_2 = uVar3;
      uVar1 = uVar2;
    }
    uVar2 = uVar1;
  } while ((param_1 < (*((volatile uint16_t *)camry_host_ptr((uint32_t)((uint32_t)(0x2603cu + (uint32_t)((short)uVar3) * (uint32_t)sizeof(F33DcmDidClass)) + (uint32_t)(0) * (uint32_t)sizeof(F33DcmDidClass) + (uint32_t)offsetof(F33DcmDidClass, first_did)))))) ||
          ((*((volatile uint16_t *)camry_host_ptr((uint32_t)((uint32_t)(0x2603cu + (uint32_t)((short)uVar3) * (uint32_t)sizeof(F33DcmDidClass)) + (uint32_t)(0) * (uint32_t)sizeof(F33DcmDidClass) + (uint32_t)offsetof(F33DcmDidClass, last_did))))) < param_1));
  *param_4 = 1;
  return;
}

undefined4 dcm_resolve_did_class_and_access_mask_94148(ushort param_1,ushort *param_2,byte *param_3)

{
  uint8_t stack_record_13[19];
  undefined *puVar1;
  undefined4 uVar2;
  
  puVar1 = ((undefined *)camry_host_ptr(0x23dfcu));
  stack_record_13[0] = '\0';
  uVar2 = 1;
  if (DAT_00026016 != 0) {
    (*((uint16_t *)(stack_record_13 + 1))) = 0;
    if ((*((volatile uint16_t *)camry_host_ptr((uint32_t)(0x2603cu + (uint32_t)(0) * (uint32_t)sizeof(F33DcmDidClass) + (uint32_t)offsetof(F33DcmDidClass, first_did))))) <= param_1) {
      if ((*((volatile uint16_t *)camry_host_ptr((uint32_t)(0x2603cu + (uint32_t)(0) * (uint32_t)sizeof(F33DcmDidClass) + (uint32_t)offsetof(F33DcmDidClass, last_did))))) < param_1) {
        if (param_1 <= (*((volatile uint16_t *)camry_host_ptr((uint32_t)((uint32_t)(0x2603cu + (uint32_t)((short)(DAT_00026016 + -1)) * (uint32_t)sizeof(F33DcmDidClass)) + (uint32_t)(0) * (uint32_t)sizeof(F33DcmDidClass) + (uint32_t)offsetof(F33DcmDidClass, last_did)))))) {
          puVar1 = ((undefined *)camry_host_ptr(0x23dfcu));
          dcm_binary_search_did_class_range_940fe(param_1,((uint16_t *)((stack_record_13 + 1))),DAT_00026016 + -1,((int8_t *)(stack_record_13)));
        }
      }
      else {
        stack_record_13[0] = '\x01';
      }
    }
    if ((stack_record_13[0] == '\x01') && ((*((uint16_t *)(stack_record_13 + 1))) < 6)) {
      *param_2 = (*((uint16_t *)(stack_record_13 + 1)));
      puVar1 = puVar1 + (short)(*((uint16_t *)(stack_record_13 + 1))) * 0x1c;
      if ((puVar1[0x2258] == '\x01') && (*(int *)(puVar1 + 0x2240) == 0)) {
        uVar2 = 2;
      }
      else {
        if ((*((int *)camry_host_ptr((uint32_t)((*((volatile int32_t *)camry_host_ptr((uint32_t)(0x2250u + (int)camry_host_addr(puVar1))))) + 4)))) != 0) {
          *param_3 = 2;
        }
        if ((*((int *)camry_host_ptr((uint32_t)((*((volatile int32_t *)camry_host_ptr((uint32_t)(0x2250u + (int)camry_host_addr(puVar1))))) + 8)))) != 0) {
          *param_3 = *param_3 | 4;
        }
        uVar2 = 0;
      }
    }
  }
  return uVar2;
}

undefined4 dcm_resolve_configured_did_and_access_mask_941ec(ushort param_1,undefined2 *param_2,byte *param_3)

{
  uint uVar1;
  undefined4 uVar2;
  uint uVar3;
  uint uVar4;
  
  uVar2 = 1;
  if (DAT_00026014 == 0) {
    return 1;
  }
  uVar4 = 0;
  if (DAT_00026028 <= param_1) {
    if (DAT_00026028 != param_1) {
      uVar3 = (uint)(ushort)(DAT_00026014 - 1);
      if (DAT_00026028 < param_1) {
        return uVar2;
      }
      do {
        if (uVar3 <= uVar4) {
          return uVar2;
        }
        uVar1 = (int)(uVar4 + uVar3) >> 1;
        if (DAT_00026028 < param_1) {
          uVar4 = uVar1 + 1 & 0xffff;
          uVar1 = uVar3;
        }
        uVar3 = uVar1;
      } while (DAT_00026028 != param_1);
    }
    if (DAT_0002602c == '\x01') {
      *param_2 = (short)uVar4;
      if ((*((volatile uint32_t *)camry_host_ptr((uint32_t)(DAT_0002601c)))) != 0) {
        *param_3 = 1;
      }
      if ((*((volatile uint32_t *)camry_host_ptr((uint32_t)((DAT_0002601c) + (uint32_t)(1) * 4u)))) != 0) {
        *param_3 = *param_3 | 2;
      }
      if ((*((volatile uint32_t *)camry_host_ptr((uint32_t)((DAT_0002601c) + (uint32_t)(2) * 4u)))) != 0) {
        *param_3 = *param_3 | 4;
      }
      if ((*((char *)camry_host_ptr((uint32_t)((int)DAT_0002601c + 0xd)))) == '\x01') {
        *param_3 = *param_3 | 8;
      }
      return 0;
    }
  }
  return uVar2;
}

uint dcm_resolve_did_group(ushort did,uchar table_kind,ushort *group,uchar *capabilities)

{
  uint uVar1;
  
  *capabilities = '\0';
  if (table_kind == '\x01') {
    uVar1 = dcm_resolve_did_class_and_access_mask_94148((uint)(ushort)did, group, capabilities);
  }
  else {
    uVar1 = dcm_resolve_configured_did_and_access_mask_941ec(did,group,capabilities);
  }
  return uVar1;
}

undefined4 dcm_check_selected_policy_byte_allowlist_942ac(char param_1,char param_2,int *param_3)

{
  byte bVar1;
  uint uVar2;
  uint uVar3;
  int iVar4;
  
  if (camry_host_addr((param_3))== 0) {
    return 1;
  }
  if (param_1 == '\x01' || param_1 == '\x02') {
    if (*param_3 == 0) {
      return 1;
    }
    if (param_1 != '\x01') {
      uVar2 = (uint)(*((byte *)camry_host_ptr((uint32_t)(*param_3 + 8))));
      iVar4 = (*((int *)camry_host_ptr((uint32_t)(*param_3))));
      goto LAB_0009432c;
    }
    uVar2 = (uint)(*((byte *)camry_host_ptr((uint32_t)(*param_3 + 9))));
    iVar4 = *param_3;
  }
  else if (param_1 == '\x11' || param_1 == '\x12') {
    if (param_3[1] == 0) {
      return 1;
    }
    if (param_1 == '\x11') {
      bVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(param_3[1] + 0xd))));
      iVar4 = param_3[1];
LAB_00094320:
      uVar2 = (uint)bVar1;
      iVar4 = (*((int *)camry_host_ptr((uint32_t)(iVar4 + 8))));
      goto LAB_0009432c;
    }
    uVar2 = (uint)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(param_3[1] + 0xc))));
    iVar4 = param_3[1];
  }
  else {
    if (param_1 != '!' && param_1 != '\"') {
      return 1;
    }
    if (param_3[2] == 0) {
      return 1;
    }
    if (param_1 == '!') {
      bVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(param_3[2] + 0xd))));
      iVar4 = param_3[2];
      goto LAB_00094320;
    }
    uVar2 = (uint)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(param_3[2] + 0xc))));
    iVar4 = param_3[2];
  }
  iVar4 = (*((int *)camry_host_ptr((uint32_t)(iVar4 + 4))));
LAB_0009432c:
  if (uVar2 != 0) {
    if (iVar4 == 0) {
      return 1;
    }
    uVar3 = 0;
    while( true ) {
      if (uVar2 <= uVar3) {
        return 1;
      }
      if ((*((char *)camry_host_ptr((uint32_t)(uVar3 + iVar4)))) == param_2) break;
      uVar3 = uVar3 + 1 & 0xff;
    }
  }
  return 0;
}

undefined4 dcm_check_all_dynamic_did_source_allowlists_94350(undefined2 param_1,undefined1 param_2,undefined1 param_3)

{
  uint8_t stack_record_20[32];
  undefined8 uVar1;
  int iVar2;
  uint uVar3;
  undefined4 uVar4;
  byte bVar5;
  
  uVar1 = 0x23dfc00000000;
  uVar4 = 0;
  iVar2 = get_record_flag_for_selector_zero_95514(param_1,((uint8_t *)(stack_record_20)));
  if ((iVar2 == 0) && (stack_record_20[0] != 0)) {
    for (bVar5 = 0; bVar5 < stack_record_20[0]; bVar5 = bVar5 + 1) {
      iVar2 = ((void)(((uint16_t *)((stack_record_20 + 4)))), load_indexed_four_byte_record_9552a(param_1, bVar5));
      if (((iVar2 != 0) ||
          (uVar3 = dcm_resolve_did_group(((uint16_t *)((stack_record_20 + 4)))[0],'\x01',((uint16_t *)((stack_record_20 + 2))),((uint8_t *)((stack_record_20 + 1)))), uVar3 != 0
          )) || (iVar2 = dcm_check_selected_policy_byte_allowlist_942ac(param_2, param_3, ((int *)camry_host_ptr((uint32_t)((*((undefined4 *)camry_host_ptr((uint32_t)(0x2250u +
                                       (short)(*((uint16_t *)(stack_record_20 + 2))) * 0x1c + (int)((ulonglong)uVar1 >> 0x20))))))))),
                iVar2 != 0)) goto LAB_000943c6;
    }
  }
  else {
LAB_000943c6:
    uVar4 = 1;
  }
  return uVar4;
}

undefined4 dcm_check_did_policy_byte_allowlist_943ce(ushort param_1,char param_2,undefined1 param_3,undefined1 param_4)

{
  uint8_t stack_record_17[23];
  char cVar1;
  uint32_t puVar2;
  void *pvVar3;
  undefined4 uVar4;
  uint uVar5;
  int iVar6;
  
  cVar1 = DAT_00026019;
  puVar2 = 0x23dfcu;
  if (param_2 == '\0') {
    pvVar3 = ((void *)camry_host_ptr((uint32_t)(DAT_0002601c)));
    if (param_1 != 0) {
      return 1;
    }
  }
  else {
    if (param_2 != '\x01') {
      if (param_1 != 0) {
        return 1;
      }
      uVar5 = dcm_resolve_did_group(DAT_00025fec,'\0',((uint16_t *)((stack_record_17 + 1))),((uint8_t *)(stack_record_17)));
      if ((uVar5 == 0) &&
         (iVar6 = dcm_check_selected_policy_byte_allowlist_942ac(param_3, param_4, ((int *)camry_host_ptr((uint32_t)((*((undefined4 *)camry_host_ptr((uint32_t)(puVar2 + 0x2220)))))))), iVar6 == 0)) {
        if (cVar1 != '\x01') {
          return 0;
        }
        uVar4 = dcm_check_all_dynamic_did_source_allowlists_94350(0,param_3,param_4);
        return uVar4;
      }
      return 1;
    }
    if (5 < param_1) {
      return 1;
    }
    pvVar3 = ((void *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)((uint32_t)(0x2603cu + (uint32_t)((short)param_1) * (uint32_t)sizeof(F33DcmDidClass)) + (uint32_t)(0) * (uint32_t)sizeof(F33DcmDidClass) + (uint32_t)offsetof(F33DcmDidClass, policy))))))));
  }
  uVar4 = dcm_check_selected_policy_byte_allowlist_942ac(param_3,param_4,pvVar3);
  return uVar4;
}

uint dcm_dispatch_did_presence_probe_9445a(ushort param_1,ushort param_2,uchar param_3,uchar *param_4)

{
  uint uVar1;
  
  uVar1 = 0;
  *param_4 = '\x01';
  if (param_1 < 6) {
    if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)((uint32_t)(0x2603cu + (uint32_t)((short)param_1) * (uint32_t)sizeof(F33DcmDidClass)) + (uint32_t)(0) * (uint32_t)sizeof(F33DcmDidClass) + (uint32_t)offsetof(F33DcmDidClass, probe_presence))))) == '\x01') {
      if ((*((volatile uint32_t *)camry_host_ptr((uint32_t)((uint32_t)(0x2603cu + (uint32_t)((short)param_1) * (uint32_t)sizeof(F33DcmDidClass)) + (uint32_t)(0) * (uint32_t)sizeof(F33DcmDidClass) + (uint32_t)offsetof(F33DcmDidClass, presence))))) != 0x0u) {
        uVar1 = (*(int (*)())camry_indirect((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)((uint32_t)(0x2603cu + (uint32_t)((short)param_1) * (uint32_t)sizeof(F33DcmDidClass)) + (uint32_t)(0) * (uint32_t)sizeof(F33DcmDidClass) + (uint32_t)offsetof(F33DcmDidClass, presence))))))))(param_2,param_3,camry_host_addr(param_4), camry_host_addr(param_4));
      }
    }
    else {
      *param_4 = '\0';
    }
  }
  return uVar1;
}

uint dcm_dispatch_did_length_callback_9449e(ushort param_1,ushort param_2,uchar param_3,ushort *param_4)

{
  uint uVar1;
  
  *param_4 = 0;
  if (param_1 < 6) {
    uVar1 = (*(int (*)())camry_indirect((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)((uint32_t)(0x2603cu + (uint32_t)((short)param_1) * (uint32_t)sizeof(F33DcmDidClass)) + (uint32_t)(0) * (uint32_t)sizeof(F33DcmDidClass) + (uint32_t)offsetof(F33DcmDidClass, length))))))))(param_2,param_3,camry_host_addr(param_4), camry_host_addr(param_4));
  }
  else {
    uVar1 = 1;
  }
  return uVar1;
}

undefined4 dcm_sum_dynamic_did_entry_lengths_944cc(undefined2 param_1,short *param_2)

{
  uint8_t stack_record_19[25];
  int iVar1;
  undefined4 uVar2;
  byte bVar3;
  
  *param_2 = 0;
  uVar2 = 0;
  iVar1 = get_record_flag_for_selector_zero_95514(param_1,((uint8_t *)(stack_record_19)));
  if ((iVar1 == 0) && (stack_record_19[0] != 0)) {
    for (bVar3 = 0; bVar3 < stack_record_19[0]; bVar3 = bVar3 + 1) {
      iVar1 = ((void)(((uint8_t *)((stack_record_19 + 1)))), load_indexed_four_byte_record_9552a(param_1, bVar3));
      if (iVar1 != 0) goto LAB_0009451e;
      *param_2 = *param_2 + (ushort)stack_record_19[4];
    }
  }
  else {
LAB_0009451e:
    uVar2 = 1;
  }
  return uVar2;
}

uint dcm_dispatch_did_read_callback_94526(ushort param_1,ushort param_2,uchar *param_3,uchar param_4,ushort *param_5,
                 uchar *param_6)

{
  uint uVar1;
  
  uVar1 = 1;
  *param_5 = 0;
  *param_6 = '\0';
  if ((param_1 < 6) && ((*((volatile uint32_t *)camry_host_ptr((uint32_t)((uint32_t)(0x2603cu + (uint32_t)((short)param_1) * (uint32_t)sizeof(F33DcmDidClass)) + (uint32_t)(0) * (uint32_t)sizeof(F33DcmDidClass) + (uint32_t)offsetof(F33DcmDidClass, read))))) !=0x0u)) {
    uVar1 = (*(int (*)())camry_indirect((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)((uint32_t)(0x2603cu + (uint32_t)((short)param_1) * (uint32_t)sizeof(F33DcmDidClass)) + (uint32_t)(0) * (uint32_t)sizeof(F33DcmDidClass) + (uint32_t)offsetof(F33DcmDidClass, read))))))))(param_2,camry_host_addr(param_3),param_4,camry_host_addr(param_5),camry_host_addr(param_6));
  }
  return uVar1;
}

undefined4 dcm_pause_dynamic_read_at_exhausted_budget_9456e(byte param_1,uint param_2,short param_3,undefined1 *param_4)

{
  int iVar1;
  undefined4 uVar2;
  
  iVar1 = (param_2 & 0xff) - 1;
  uVar2 = 0;
  if (((int)((uint)param_1 - iVar1) < 0 !=
       (iVar1 < 0 && iVar1 < 0 == (int)((uint)param_1 - iVar1) < 0)) && (param_3 == 0)) {
    DAT_febe5d20 = param_1 + 1;
    uVar2 = 10;
    *param_4 = 1;
  }
  return uVar2;
}

int dcm_read_and_slice_dynamic_did_sources_94590(undefined2 param_1,byte param_2,int param_3,ushort *param_4,undefined1 *param_5,
                short *param_6)

{
  uint8_t stack_record_2f[47];
  int iVar1;
  uint uVar2;
  uint32_t puVar3;
  uint32_t puVar4;
  int iVar5;
  uint uVar6;
  undefined *puVar7;
  bool bVar8;
  byte bVar9;
  undefined1 auStack_2a [2];
  
  puVar3 = 0xfebeb800u;
  puVar4 = 0x23dfcu;
  iVar5 = 1;
  *param_5 = 0;
  stack_record_2f[2] = 0;
  stack_record_2f[1] = '\0';
  bVar8 = DAT_febe5d21 != '\0';
  bVar9 = DAT_febe5d20;
  do {
    if (param_2 <= bVar9) {
      return iVar5;
    }
    iVar5 = ((void)((stack_record_2f + 7)), load_indexed_four_byte_record_9552a(param_1, bVar9));
    if (((iVar5 == 0) &&
        (uVar6 = dcm_resolve_did_group((*((uint16_t *)(stack_record_2f + 7))),'\x01',(stack_record_2f + 3),stack_record_2f), uVar6 == 0)) &&
       ((*((int *)camry_host_ptr((uint32_t)(puVar4 + (short)(*((uint16_t *)(stack_record_2f + 3))) * 0x1c + 0x2248)))) != 0)) {
      puVar7 = ((void *)camry_host_ptr((uint32_t)(puVar3 + -0x5ade)));
      iVar5 = (*(int (*)())camry_indirect((uint32_t)(((((code *)(uintptr_t)((uint32_t)((uintptr_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(puVar4 + (short)(*((uint16_t *)(stack_record_2f + 3))) * 0x1c + 0x2248))))))))))))((*((uint16_t *)(stack_record_2f + 7))),camry_host_addr(puVar7),bVar8,camry_host_addr(auStack_2a),camry_host_addr((stack_record_2f + 2)));
      if (iVar5 == 0) {
        (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x5adf))))) = 0;
        uVar6 = (uint)stack_record_2f[9];
        *param_6 = *param_6 + -1;
        bVar8 = false;
        if (uVar6 != 0) {
          uVar2 = 2 - stack_record_2f[10];
          if ((int)(uVar6 - uVar2) < 0 !=
              ((int)uVar2 < 0 && (int)uVar2 < 0 == (int)(uVar6 - uVar2) < 0) || uVar6 == uVar2) {
            uVar2 = 0;
            while( true ) {
              if (stack_record_2f[10] <= uVar2) break;
              iVar5 = *param_4 + uVar2;
              iVar1 = uVar6 + uVar2;
              uVar2 = uVar2 + 1 & 0xff;
              (*((undefined *)camry_host_ptr((uint32_t)(iVar5 + param_3)))) = puVar7[iVar1 + -1];
            }
            *param_4 = *param_4 + (ushort)stack_record_2f[10];
            iVar5 = dcm_pause_dynamic_read_at_exhausted_budget_9456e(bVar9,param_2,*param_6,(stack_record_2f + 1));
            goto LAB_000946b2;
          }
        }
        goto LAB_000946ac;
      }
      if (iVar5 == 1) {
        (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x5adf))))) = 0;
        *param_5 = stack_record_2f[2];
        goto LAB_000946ae;
      }
      stack_record_2f[1] = '\x01';
      if (iVar5 == 10) {
        (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x5adf))))) = 1;
        (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x5ae0))))) = bVar9;
      }
      else {
        (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x5adf))))) = 0;
        iVar5 = 1;
      }
    }
    else {
LAB_000946ac:
      iVar5 = 1;
LAB_000946ae:
      stack_record_2f[1] = (char)iVar5;
    }
LAB_000946b2:
    if (stack_record_2f[1] == '\x01') {
      return iVar5;
    }
    bVar9 = bVar9 + 1;
  } while( true );
}

int dcm_read_dynamic_did_with_pending_cancellation_946c6(undefined2 param_1,undefined4 param_2,char param_3,undefined2 *param_4,
                undefined1 *param_5,undefined4 param_6)

{
  uint8_t stack_record_1f[31];
  uint32_t puVar1;
  uint32_t puVar2;
  int iVar3;
  uint uVar4;
  int iVar5;
  ushort auStack_1c [3];
  
  puVar1 = 0xfebeb800u;
  puVar2 = 0x23dfcu;
  iVar5 = 1;
  *param_5 = 0;
  stack_record_1f[0] = 0;
  *param_4 = 0;
  if (param_3 == '\x02') {
    if (DAT_febe5d21 == '\x01') {
      puVar1 = 0xfebeb800u;
      iVar3 = ((void)(auStack_1c), load_indexed_four_byte_record_9552a(param_1, DAT_febe5d20));
      if (((iVar3 == 0) &&
          (uVar4 = dcm_resolve_did_group(auStack_1c[0],'\x01',(stack_record_1f + 9),(stack_record_1f + 2)), uVar4 == 0
          )) && ((*((int *)camry_host_ptr((uint32_t)(puVar2 + (short)(*((uint16_t *)(stack_record_1f + 9))) * 0x1c + 0x2248)))) != 0)) {
        iVar5 = (*(int (*)())camry_indirect((uint32_t)(((((code *)(uintptr_t)((uint32_t)((uintptr_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(puVar2 + (short)(*((uint16_t *)(stack_record_1f + 9))) * 0x1c + 0x2248))))))))))))(auStack_1c[0],param_2,2,camry_host_addr(param_4),camry_host_addr(stack_record_1f));
      }
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x5adf))))) = 0;
    }
  }
  else {
    puVar1 = 0xfebeb800u;
    iVar3 = get_record_flag_for_selector_zero_95514(param_1,(stack_record_1f + 1));
    if (((iVar3 == 0) && (stack_record_1f[1] != '\0')) &&
       (iVar5 = dcm_read_and_slice_dynamic_did_sources_94590(param_1, stack_record_1f[1], param_2, param_4, param_5, ((short *)camry_host_ptr((uint32_t)(param_6)))), iVar5 == 10)) {
      return 10;
    }
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x5ae0))))) = 0;
  return iVar5;
}

uint dcm_dispatch_did_write_callback_94786(ushort param_1,ushort param_2,uchar *param_3,uchar param_4,ushort param_5,
                 uchar *param_6)

{
  uint uVar1;
  
  uVar1 = 1;
  *param_6 = '\0';
  if ((param_1 < 6) && ((*((volatile uint32_t *)camry_host_ptr((uint32_t)((uint32_t)(0x2603cu + (uint32_t)((short)param_1) * (uint32_t)sizeof(F33DcmDidClass)) + (uint32_t)(0) * (uint32_t)sizeof(F33DcmDidClass) + (uint32_t)offsetof(F33DcmDidClass, write))))) != 0x0u)) {
    uVar1 = (*(int (*)())camry_indirect((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)((uint32_t)(0x2603cu + (uint32_t)((short)param_1) * (uint32_t)sizeof(F33DcmDidClass)) + (uint32_t)(0) * (uint32_t)sizeof(F33DcmDidClass) + (uint32_t)offsetof(F33DcmDidClass, write))))))))(param_2,camry_host_addr(param_3),param_4,param_5,camry_host_addr(param_6));
  }
  return uVar1;
}

uint invoke_configured_two_argument_callback_for_group_zero_9487e(short param_1,int param_2,uint param_3)

{
  uint uVar1;
  
  if (param_3 == 0 && param_2 == 0) {
    uVar1 = param_3 & 0xff;
  }
  else {
    uVar1 = 1;
    if ((param_1 == 0) && (DAT_00026024 != 0x0u)) {
      uVar1 = (*(int (*)())camry_indirect((uint32_t)(DAT_00026024)))(param_2,param_3);
    }
  }
  return uVar1;
}

uint probe_configured_element_status_by_type_948ae(short param_1,uint param_2,undefined1 *param_3)

{
  int iVar1;
  uint uVar2;
  uint uVar3;
  undefined1 uStack_11;
  
  *param_3 = 0;
  uVar3 = 1;
  if ((param_1 == 0) && ((param_2 & 0xff) < (uint)DAT_0002602a)) {
    iVar1 = (param_2 & 0xff) * 8;
    uVar2 = (uint)(*((byte *)camry_host_ptr((uint32_t)((*((volatile int32_t *)camry_host_ptr((uint32_t)(DAT_00026020 + iVar1)))) + 0xf))));
    if (((uVar2 - 1 < 4) || (uVar2 == 6 || uVar2 == 7)) &&
       (uVar2 = (*(int (*)())camry_indirect((uint32_t)((*((volatile undefined4 *)camry_host_ptr((*((volatile uint32_t *)camry_host_ptr((uint32_t)(DAT_00026020 + iVar1))))))))))(camry_host_addr(&uStack_11)), uVar2 < 2)) {
      *param_3 = uStack_11;
      uVar3 = uVar2;
    }
  }
  return uVar3;
}

uint dispatch_element_gate_four_callback_by_type_94906(short param_1,uint param_2,undefined1 param_3,undefined1 *param_4)

{
  int iVar1;
  short sVar2;
  uint uVar3;
  undefined1 uStack_11;
  
  *param_4 = 0;
  uVar3 = 1;
  if ((param_1 == 0) && ((param_2 & 0xff) < (uint)DAT_0002602a)) {
    iVar1 = (param_2 & 0xff) * 8;
    sVar2 = (*((short *)camry_host_ptr((uint32_t)((*((volatile int32_t *)camry_host_ptr((uint32_t)(DAT_00026020 + iVar1)))) + 4))));
    uVar3 = (uint)(*((byte *)camry_host_ptr((uint32_t)((*((volatile int32_t *)camry_host_ptr((uint32_t)(iVar1 + DAT_00026020)))) + 0xf))));
    if (uVar3 - 1 < 4) {
      if (sVar2 != 0) {
        return 1;
      }
      if (DAT_00026008 == 0x0u) {
        return 1;
      }
      uVar3 = (*(int (*)())camry_indirect((uint32_t)(DAT_00026008)))(param_3,camry_host_addr(&uStack_11));
      if (((uVar3 != 0) && (uVar3 != 1)) && (uVar3 != 10)) {
        return 1;
      }
    }
    else {
      if (uVar3 != 6 && uVar3 != 7) {
        return 1;
      }
      if (sVar2 != 0) {
        return 1;
      }
      if (DAT_00026004 == 0x0u) {
        return 1;
      }
      uVar3 = (*(int (*)())camry_indirect((uint32_t)(DAT_00026004)))(camry_host_addr(&uStack_11));
      if (1 < uVar3) {
        return 1;
      }
    }
    *param_4 = uStack_11;
  }
  return uVar3;
}

uint dispatch_element_gate_six_callback_by_type_9499a(short param_1,uint param_2,undefined1 param_3,undefined1 *param_4)

{
  int iVar1;
  short sVar2;
  uint uVar3;
  undefined1 uStack_11;
  
  *param_4 = 0;
  uVar3 = 1;
  if ((param_1 == 0) && ((param_2 & 0xff) < (uint)DAT_0002602a)) {
    iVar1 = (param_2 & 0xff) * 8;
    sVar2 = (*((short *)camry_host_ptr((uint32_t)((*((volatile int32_t *)camry_host_ptr((uint32_t)(DAT_00026020 + iVar1)))) + 6))));
    uVar3 = (uint)(*((byte *)camry_host_ptr((uint32_t)((*((volatile int32_t *)camry_host_ptr((uint32_t)(iVar1 + DAT_00026020)))) + 0xf))));
    if (uVar3 - 1 < 4) {
      if (sVar2 != 0) {
        return 1;
      }
      if (DAT_00025ff4 == 0x0u) {
        return 1;
      }
      uVar3 = (*(int (*)())camry_indirect((uint32_t)(DAT_00025ff4)))(param_3,camry_host_addr(&uStack_11));
      if (((uVar3 != 0) && (uVar3 != 1)) && (uVar3 != 10)) {
        return 1;
      }
    }
    else {
      if (uVar3 != 6 && uVar3 != 7) {
        return 1;
      }
      if (sVar2 != 0) {
        return 1;
      }
      if (DAT_00025ff0 == 0x0u) {
        return 1;
      }
      uVar3 = (*(int (*)())camry_indirect((uint32_t)(DAT_00025ff0)))(camry_host_addr(&uStack_11));
      if (1 < uVar3) {
        return 1;
      }
    }
    *param_4 = uStack_11;
  }
  return uVar3;
}

uint dispatch_element_gate_eight_callback_with_data_offset_94a2e(short param_1,uint param_2,int param_3,undefined1 param_4,undefined1 *param_5)

{
  int iVar1;
  short sVar2;
  int iVar3;
  uint uVar4;
  undefined1 uStack_d;
  
  uVar4 = 1;
  *param_5 = 0;
  if ((param_1 == 0) && ((param_2 & 0xff) < (uint)DAT_0002602a)) {
    iVar1 = (param_2 & 0xff) * 8;
    iVar3 = 0;
    if ((*((char *)camry_host_ptr((uint32_t)((*((volatile int32_t *)camry_host_ptr((uint32_t)(DAT_00026020 + iVar1)))) + 0xe)))) != '\0') {
      iVar3 = (int)(uint)(*((ushort *)camry_host_ptr((uint32_t)(DAT_00026020 + iVar1 + 4)))) >> 3;
    }
    sVar2 = (*((short *)camry_host_ptr((uint32_t)((*((volatile int32_t *)camry_host_ptr((uint32_t)(DAT_00026020 + iVar1)))) + 8))));
    uVar4 = (uint)(*((byte *)camry_host_ptr((uint32_t)((*((volatile int32_t *)camry_host_ptr((uint32_t)(DAT_00026020 + iVar1)))) + 0xf))));
    if (uVar4 - 1 < 4) {
      if (sVar2 != 0) {
        return 1;
      }
      if (DAT_00026010 == 0x0u) {
        return 1;
      }
      uVar4 = (*(int (*)())camry_indirect((uint32_t)(DAT_00026010)))(iVar3 + param_3,param_4,camry_host_addr(&uStack_d));
      if (((uVar4 != 0) && (uVar4 != 1)) && (uVar4 != 10)) {
        return 1;
      }
    }
    else {
      if (uVar4 != 6 && uVar4 != 7) {
        return 1;
      }
      if (sVar2 != 0) {
        return 1;
      }
      if (DAT_0002600c == 0x0u) {
        return 1;
      }
      uVar4 = (*(int (*)())camry_indirect((uint32_t)(DAT_0002600c)))(iVar3 + param_3,camry_host_addr(&uStack_d));
      if (1 < uVar4) {
        return 1;
      }
    }
    *param_5 = uStack_d;
  }
  return uVar4;
}

int dispatch_element_gate_ten_callback_with_data_offset_94ae0(short param_1,uint param_2,undefined1 param_3,int param_4,undefined1 *param_5)

{
  byte bVar1;
  short sVar2;
  int iVar3;
  int iVar4;
  bool bVar5;
  undefined1 uStack_d;
  
  *param_5 = 0;
  if (param_1 != 0) {
    return 1;
  }
  if ((uint)DAT_0002602a <= (param_2 & 0xff)) {
    return 1;
  }
  iVar4 = (param_2 & 0xff) * 8;
  iVar3 = 0;
  if ((*((char *)camry_host_ptr((uint32_t)((*((volatile int32_t *)camry_host_ptr((uint32_t)(DAT_00026020 + iVar4)))) + 0xe)))) != '\0') {
    iVar3 = (int)(uint)(*((ushort *)camry_host_ptr((uint32_t)(DAT_00026020 + iVar4 + 4)))) >> 3;
  }
  sVar2 = (*((short *)camry_host_ptr((uint32_t)((*((volatile int32_t *)camry_host_ptr((uint32_t)(DAT_00026020 + iVar4)))) + 10))));
  bVar1 = (*((byte *)camry_host_ptr((uint32_t)((*((volatile int32_t *)camry_host_ptr((uint32_t)(DAT_00026020 + iVar4)))) + 0xf))));
  if (bVar1 == 0) {
    return 1;
  }
  if (bVar1 != 1) {
    if (bVar1 < 3) {
LAB_00094b76:
      if (sVar2 != 0) {
        return 1;
      }
      iVar4 = (*(int (*)())camry_indirect((uint32_t)(DAT_00026000)))(param_3,iVar3 + param_4,camry_host_addr(&uStack_d));
      if (((iVar4 != 0) && (iVar4 != 1)) && (iVar4 != 10)) {
        return 1;
      }
      *param_5 = uStack_d;
      return iVar4;
    }
    if (bVar1 != 3) {
      if (bVar1 == 4) goto LAB_00094b76;
      if (bVar1 != 6 && bVar1 != 7) {
        return 1;
      }
      if (sVar2 != 0) {
        return 1;
      }
      iVar4 = (*(int (*)())camry_indirect((uint32_t)(DAT_00025ff8)))(iVar3 + param_4);
      bVar5 = iVar4 == 0;
      goto LAB_00094b70;
    }
  }
  if (sVar2 != 0) {
    return 1;
  }
  iVar4 = (*(int (*)())camry_indirect((uint32_t)(DAT_00025ffc)))(param_3,iVar3 + param_4);
  if (iVar4 == 0) {
    return 0;
  }
  bVar5 = iVar4 == 10;
LAB_00094b70:
  if (bVar5) {
    return iVar4;
  }
  return 1;
}

undefined4 check_configured_range_byte_allowlist_94ba8(char param_1)

{
  uint uVar1;
  
  if (PTR_PTR_00026034 != 0) {
    uVar1 = 0;
    if (PTR_PTR_00026030 == 0) {
      return 1;
    }
    for (; uVar1 < (byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)((PTR_PTR_00026030) + (uint32_t)(4) * 1u)))); uVar1 = uVar1 + 1 & 0xff) {
      if (param_1 == (*((char *)camry_host_ptr((uint32_t)((*((volatile int32_t *)camry_host_ptr((uint32_t)(PTR_PTR_00026030)))) + uVar1))))) {
        return 0;
      }
    }
  }
  return 1;
}

undefined4
resolve_configured_address_range_by_mode_and_identifier_94be2(char param_1,uint param_2,char param_3,char param_4,undefined1 *param_5,
            undefined1 *param_6)

{
  ushort uVar1;
  uint uVar2;
  undefined4 uVar3;
  int iVar4;
  
  uVar1 = 0;
  uVar3 = 1;
  if (PTR_PTR_00026034 != 0) {
    if (param_3 == '\0') {
      while( true ) {
        if (DAT_00026038 <= uVar1) {
          return uVar3;
        }
        if (((*((volatile uint8_t *)camry_host_ptr((uint32_t)((PTR_PTR_00026034) + (uint32_t)((short)uVar1 * 0xc + 0xb) * 1u)))) == '\x01') &&
           (param_4 == (*((volatile uint8_t *)camry_host_ptr((uint32_t)((PTR_PTR_00026034) + (uint32_t)((short)uVar1 * 0xc + 10) * 1u)))))) break;
        uVar1 = uVar1 + 1 & 0xff;
      }
    }
    iVar4 = (short)uVar1 * 0xc;
    *param_5 = (char)uVar1;
    if (param_1 == '\0') {
      uVar2 = 0;
      if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)((PTR_PTR_00026034) + (uint32_t)(iVar4 + 8) * 1u)))) == '\0') {
        return uVar3;
      }
      while( true ) {
        if ((byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)((PTR_PTR_00026034) + (uint32_t)(iVar4 + 8) * 1u)))) <= uVar2) {
          return uVar3;
        }
        if (((*((uint *)camry_host_ptr((uint32_t)((*((volatile int32_t *)camry_host_ptr((uint32_t)((PTR_PTR_00026034) + (uint32_t)(iVar4))))) + uVar2 * 0x10 + 8)))) <= param_2) &&
           (param_2 <= (*((uint *)camry_host_ptr((uint32_t)((*((volatile int32_t *)camry_host_ptr((uint32_t)((PTR_PTR_00026034) + (uint32_t)(iVar4))))) + uVar2 * 0x10 + 4)))))) break;
        uVar2 = uVar2 + 1 & 0xff;
      }
LAB_00094ca8:
      *param_6 = (char)uVar2;
      return 0;
    }
    uVar2 = 0;
    if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)((PTR_PTR_00026034) + (uint32_t)(iVar4 + 9) * 1u)))) == '\0') {
      return uVar3;
    }
    for (; uVar2 < (byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)((PTR_PTR_00026034) + (uint32_t)(iVar4 + 9) * 1u)))); uVar2 = uVar2 + 1 & 0xff) {
      if (((*((uint *)camry_host_ptr((uint32_t)((*((volatile int32_t *)camry_host_ptr((uint32_t)((PTR_PTR_00026034) + (uint32_t)(iVar4 + 4))))) + uVar2 * 0x10 + 8)))) <= param_2) &&
         (param_2 <= (*((uint *)camry_host_ptr((uint32_t)((*((volatile int32_t *)camry_host_ptr((uint32_t)((PTR_PTR_00026034) + (uint32_t)(iVar4 + 4))))) + uVar2 * 0x10 + 4))))))
      goto LAB_00094ca8;
    }
  }
  return uVar3;
}

bool is_requested_range_past_configured_end_94cc4(char param_1,uint param_2,uint param_3,int param_4,int param_5)

{
  int iVar1;
  bool bVar2;
  
  bVar2 = true;
  if (PTR_PTR_00026034 != 0) {
    iVar1 = (param_2 & 0xff) * 0xc;
    if (param_1 == '\0') {
      iVar1 = (*((int *)camry_host_ptr((uint32_t)(PTR_PTR_00026034 + iVar1))));
    }
    else {
      iVar1 = (*((int *)camry_host_ptr((uint32_t)(PTR_PTR_00026034 + iVar1 + 4))));
    }
    bVar2 = (uint)((*((int *)camry_host_ptr((uint32_t)((param_3 & 0xff) * 0x10 + iVar1 + 4)))) - param_4) < param_5 - 1U;
  }
  return bVar2;
}

undefined4 check_selected_range_byte_allowlist_94d04(char param_1,ushort param_2,uint param_3,char param_4)

{
  int iVar1;
  uint uVar2;
  undefined4 uVar3;
  int iVar4;
  
  uVar3 = 1;
  if (PTR_PTR_00026034 == 0) {
    return uVar3;
  }
  iVar4 = (short)(param_2 & 0xff) * 0xc;
  iVar1 = (param_3 & 0xff) * 0x10;
  if (param_1 == '\0') {
    uVar2 = 0;
    if ((*((char *)camry_host_ptr((uint32_t)((*((volatile int32_t *)camry_host_ptr((uint32_t)(PTR_PTR_00026034 + iVar4)))) + iVar1 + 0xc)))) != '\0') {
      while( true ) {
        if ((*((byte *)camry_host_ptr((uint32_t)((*((volatile int32_t *)camry_host_ptr((uint32_t)(PTR_PTR_00026034 + iVar4)))) + iVar1 + 0xc)))) <= uVar2) {
          return uVar3;
        }
        if (param_4 == (*((char *)camry_host_ptr((uint32_t)((*((volatile int32_t *)camry_host_ptr((uint32_t)((*((volatile int32_t *)camry_host_ptr((uint32_t)(PTR_PTR_00026034 + iVar4)))) + iVar1)))) + uVar2)))))
        break;
        uVar2 = uVar2 + 1 & 0xff;
      }
    }
  }
  else if ((*((char *)camry_host_ptr((uint32_t)((*((volatile int32_t *)camry_host_ptr((uint32_t)(PTR_PTR_00026034 + iVar4 + 4)))) + iVar1 + 0xc)))) != '\0') {
    uVar2 = 0;
    while( true ) {
      if ((*((byte *)camry_host_ptr((uint32_t)((*((volatile int32_t *)camry_host_ptr((uint32_t)(PTR_PTR_00026034 + iVar4 + 4)))) + iVar1 + 0xc)))) <= uVar2) {
        return uVar3;
      }
      if (param_4 == (*((char *)camry_host_ptr((uint32_t)((*((volatile int32_t *)camry_host_ptr((uint32_t)((*((volatile int32_t *)camry_host_ptr((uint32_t)(PTR_PTR_00026034 + iVar4 + 4)))) + iVar1)))) + uVar2)))))
      break;
      uVar2 = uVar2 + 1 & 0xff;
    }
    return 0;
  }
  return 0;
}

undefined4 lookup_configured_dynamic_did_index_94d9c(ushort param_1,undefined2 *param_2)

{
  uint uVar1;
  undefined4 uVar2;
  uint uVar3;
  uint uVar4;
  
  uVar2 = 1;
  if (DAT_00026018 != '\0') {
    uVar4 = 0;
    if (param_1 < DAT_00025fec) {
      return uVar2;
    }
    if (DAT_00025fec != param_1) {
      uVar3 = (uint)(byte)(DAT_00026018 - 1);
      if (DAT_00025fec < param_1) {
        return uVar2;
      }
      do {
        if (uVar3 <= uVar4) {
          return uVar2;
        }
        uVar1 = (int)(uVar4 + uVar3) >> 1;
        if (DAT_00025fec < param_1) {
          uVar4 = uVar1 + 1 & 0xff;
          uVar1 = uVar3;
        }
        uVar3 = uVar1;
      } while (DAT_00025fec != param_1);
    }
    *param_2 = (short)uVar4;
    uVar2 = 0;
  }
  return uVar2;
}

undefined4 check_dynamic_did_capacity_and_zero_length_sum_94df6(short param_1,int param_2,int param_3)

{
  uint8_t stack_record_1a[26];
  uint32_t puVar1;
  int extraout_r7;
  int iVar2;
  uint uVar3;
  byte bVar4;
  byte bStack_1b;
  
  puVar1 = 0x23dfcu;
  uVar3 = 0;
  if ((((param_1 == 0) && (iVar2 = lookup_configured_dynamic_did_index_94d9c(DAT_00026028,((uint16_t *)(stack_record_1a))), iVar2 == 0)) &&
      (iVar2 = get_record_flag_for_selector_zero_95514((*((uint16_t *)(stack_record_1a + 0))), ((undefined1 *)camry_host_ptr((uint32_t)(extraout_r7 + -1)))), iVar2 == 0)) &&
     ((uint)bStack_1b + param_2 <= (uint)(*((byte *)camry_host_ptr((uint32_t)((*((volatile int32_t *)camry_host_ptr((uint32_t)(puVar1 + 0x2220)))) + 0xc)))))) {
    for (bVar4 = 0; bVar4 < bStack_1b; bVar4 = bVar4 + 1) {
      iVar2 = ((void)(((uint8_t *)((stack_record_1a + 2)))), load_indexed_four_byte_record_9552a((*((uint16_t *)(stack_record_1a + 0))), bVar4));
      if (iVar2 != 0) {
        return 1;
      }
      uVar3 = uVar3 + stack_record_1a[5] & 0xffff;
    }
    if (uVar3 + param_3 == 0) {
      return 0;
    }
  }
  return 1;
}

undefined4 append_big_endian_dynamic_did_source_records_94e6a(undefined2 param_1,int param_2,uint param_3)

{
  uint8_t stack_record_19[25];
  int iVar1;
  undefined4 uVar2;
  uint uVar3;
  
  iVar1 = get_record_flag_for_selector_zero_95514(param_1,((uint8_t *)(stack_record_19)));
  uVar3 = 0;
  if (iVar1 == 0) {
    for (; uVar3 < (param_3 & 0xff); uVar3 = uVar3 + 1 & 0xff) {
      iVar1 = uVar3 * 4;
      (*((uint16_t *)(stack_record_19 + 1))) = CONCAT11((*((undefined1 *)camry_host_ptr((uint32_t)(iVar1 + 2 + param_2)))),(*((undefined1 *)camry_host_ptr((uint32_t)(iVar1 + 3 + param_2))))
                          );
      stack_record_19[3] = (*((undefined1 *)camry_host_ptr((uint32_t)(iVar1 + param_2 + 4))));
      stack_record_19[4] = (*((undefined1 *)camry_host_ptr((uint32_t)(iVar1 + param_2 + 5))));
      iVar1 = ((void)(((uint16_t *)((stack_record_19 + 1)))), store_indexed_four_byte_record_95474(param_1, stack_record_19[0] + uVar3 & 0xff));
      if (iVar1 != 0) goto LAB_00094e86;
    }
    uVar2 = set_record_flag_for_selector_zero_954dc(param_1,(param_3 & 0xff) + (uint)stack_record_19[0] & 0xff);
  }
  else {
LAB_00094e86:
    uVar2 = 1;
  }
  return uVar2;
}

undefined4 append_dynamic_did_sources_for_define_mode_one_94ee6(char param_1,undefined1 *param_2,char param_3)

{
  uint32_t puVar1;
  int iVar2;
  undefined4 uVar3;
  short sStack_e;
  
  puVar1 = 0x23dfcu;
  if (param_1 == '\x01') {
    if ((((param_3 == '\0') || (camry_host_addr((param_2))== 0)) ||
        (iVar2 = lookup_configured_dynamic_did_index_94d9c(CONCAT11(*param_2,param_2[1]),&sStack_e), iVar2 != 0)) ||
       ((sStack_e != 0 || ((*((int *)camry_host_ptr((uint32_t)(puVar1 + 0x21ec)))) == 0)))) {
      uVar3 = 1;
    }
    else {
      uVar3 = append_big_endian_dynamic_did_source_records_94e6a(0, camry_host_addr(param_2), param_3);
    }
  }
  else {
    uVar3 = 0;
  }
  return uVar3;
}

undefined4 clear_dynamic_did_entries_by_identifier_94f3a(undefined2 param_1)

{
  int iVar1;
  undefined4 uVar2;
  undefined2 uStack_a;
  
  uVar2 = 1;
  iVar1 = lookup_configured_dynamic_did_index_94d9c(param_1,&uStack_a);
  if (iVar1 == 0) {
    uVar2 = clear_record_flag_for_selector_zero_954ee(uStack_a);
  }
  return uVar2;
}

undefined4 thunk_clear_record_flag_for_configured_count_95500(void)

{
  return clear_record_flag_for_configured_count_95500();
}

undefined4 get_dynamic_did_index_and_entry_count_94f6a(undefined2 param_1,undefined1 *param_2,undefined4 param_3)

{
  undefined2 *extraout_r8;
  int iVar1;
  undefined4 uVar2;
  
  *param_2 = 0;
  uVar2 = 1;
  iVar1 = lookup_configured_dynamic_did_index_94d9c(param_1, ((undefined2 *)camry_host_ptr((uint32_t)(param_3))));
  if (iVar1 == 0) {
    uVar2 = get_record_flag_for_selector_zero_95514((*((volatile uint16_t *)camry_host_ptr((uint32_t)(param_3)))),param_2);
  }
  return uVar2;
}

undefined4 check_policy_operation_availability_and_condition_94f94(char param_1,int *param_2,undefined2 param_3,undefined1 *param_4)

{
  int iVar1;
  undefined4 uVar2;
  
  *param_4 = 0;
  if (camry_host_addr((param_2))== 0) {
    return 1;
  }
  if (param_1 == '\0') {
    iVar1 = *param_2;
  }
  else {
    if (param_1 == '\x10') {
      if (param_2[1] == 0) {
        return 1;
      }
      if ((*((int *)camry_host_ptr((uint32_t)(param_2[1] ))))== 0) {
        return 0;
      }
      uVar2 = (*(int (*)())camry_indirect((uint32_t)((*((code * *)camry_host_ptr((uint32_t)(param_2[1])))))))(param_3,camry_host_addr(param_4), (uint)(ushort)param_3, camry_host_addr(param_4));
      return uVar2;
    }
    if (param_1 != ' ') {
      return 1;
    }
    iVar1 = param_2[2];
  }
  if (iVar1 != 0) {
    return 0;
  }
  return 1;
}

undefined4 check_selected_did_policy_operation_condition_94fea(ushort param_1,char param_2,undefined2 param_3,undefined1 *param_4)

{
  uint32_t addr;
  undefined4 uVar2;
  
  *param_4 = 0;
  if ((param_2 == '\x10') || (param_2 == ' ')) {
    if (5 < param_1) {
      return 1;
    }
    addr = (*((volatile uint32_t *)camry_host_ptr((uint32_t)((uint32_t)(0x2603cu + (uint32_t)((short)param_1) * (uint32_t)sizeof(F33DcmDidClass)) + (uint32_t)(0) * (uint32_t)sizeof(F33DcmDidClass) + (uint32_t)offsetof(F33DcmDidClass, policy)))));
  }
  else {
    if (param_1 != 0) {
      return 1;
    }
    addr = DAT_0002601c;
  }
  if (addr == 0) {
    return 1;
  }
  uVar2 = check_policy_operation_availability_and_condition_94f94(param_2,((int *)camry_host_ptr(addr)),param_3,param_4);
  return uVar2;
}
