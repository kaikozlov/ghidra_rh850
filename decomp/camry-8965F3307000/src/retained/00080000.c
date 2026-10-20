#include "common.h"

undefined4 reset_valid_encoded_tx_queue_notify_80066(byte param_1,undefined2 param_2)

{
  if (param_1 < DAT_00021970) {
    reset_encoded_tx_queue_and_completion_state_7ff98(param_1,param_2,1);
  }
  return 0;
}

undefined4 decode_u16_tx_queue_and_reset_notify_80082(uint param_1)

{
  uint32_t puVar1;
  int iVar2;
  
  puVar1 = ((uint32_t)(param_1 & 0xf800));
  param_1 = param_1 & 0x7ff;
  iVar2 = 0;
  if ((((((uintptr_t)(puVar1)== 0) || (iVar2 = 1,(puVar1)==((uint32_t)((uint32_t)(0x6000))))) ||
       (iVar2 = 2,(puVar1)==((uint32_t)((uint32_t)(0x800))))) ||
      (((iVar2 = 3,(puVar1)==((uint32_t)(0xb800u))|| (iVar2 = 4,(puVar1)==((uint32_t)((uint32_t)(0xc000))))) ||
       (iVar2 = 5,(puVar1)==((uint32_t)((uint32_t)(0xf800))))))) && (param_1 < (ushort)(*((volatile uint16_t *)camry_host_ptr((uint32_t)(0x21a48u + (uint32_t)(iVar2) * 2u))))))
  {
    reset_valid_encoded_tx_queue_notify_80066((*((volatile uint8_t *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x21994u + (uint32_t)(iVar2) * 4u)))) + (uint32_t)(param_1 * 8 + 4))))),
                 (uint)(*((ushort *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x21994u + (uint32_t)(iVar2) * 4u)))) + param_1 * 8 + 6)))) | iVar2 << 8);
  }
  return 0;
}

undefined4 decode_u16_tx_queue_and_reset_silent_800ee(uint param_1)

{
  uint base;
  int iVar2;
  
  base = param_1 & 0xf800;
  param_1 = param_1 & 0x7ff;
  iVar2 = 0;
  if ((((((base == 0) || (iVar2 = 1, base == 0x6000)) || (iVar2 = 2, base == 0x800)) ||
       (((iVar2 = 3, base == 0xb800) || (iVar2 = 4, base == 0xc000)) || (iVar2 = 5, base == 0xf800)))
      ) && (param_1 < (ushort)(*((volatile uint16_t *)camry_host_ptr((uint32_t)(0x21a48u + (uint32_t)(iVar2) * 2u))))))
  {
    reset_encoded_tx_queue_and_completion_state_7ff98((*((volatile uint8_t *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x21994u + (uint32_t)(iVar2) * 4u)))) + (uint32_t)(param_1 * 8 + 4))))),
                 (uint)(*((ushort *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x21994u + (uint32_t)(iVar2) * 4u)))) + param_1 * 8 + 6)))) | iVar2 << 8,2);
  }
  return 0;
}

void attempt_queued_can_tx
               (uchar controller,uchar route_index,F33CanQueueDescriptor *descriptor,ushort *cursors
               )

{
  undefined1 uVar1;
  int iVar2;
  uint32_t puVar3;
  uint uVar4;
  undefined *puVar5;
  undefined *puVar6;
  int iVar7;
  uint uVar8;
  uint uVar9;
  undefined *puVar10;
  uint *puVar11;
  F33CanDriverPdu local_34;
  
  puVar5 = ((undefined *)camry_host_ptr(0xfebeb800u));
  puVar3 = 0x23dfcu;
  uVar9 = (uint)controller;
  puVar6 = ((undefined *)camry_host_ptr((uint32_t)((uint)descriptor->queue_index)));
  puVar10 = ((undefined *)camry_host_ptr((uint32_t)((uint)descriptor->hardware_group)));
  uVar8 = (uint)cursors[1];
  iVar7 = 0x69;
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x218e8u + (uint32_t)(uVar9) * 4u)))) + (uint32_t)((int)camry_host_addr(puVar10)))))) != '<') {
    reload_controller_indexed_u16_counter_7f5ba(uVar9, camry_host_addr(puVar10));
  }
  puVar11 = ((uint *)camry_host_ptr((uint32_t)(uVar8 * 4 + (*((volatile int32_t *)camry_host_ptr((uint32_t)(puVar3 + (int)camry_host_addr(puVar6) * 4 + -0x23a8)))))));
  uVar4 = *puVar11;
  if ((puVar11[1] ^ uVar4) != 0xffffffff) goto LAB_00080250;
  if (uVar4 == 0xffffffff) {
    puVar11 = (((uint *)camry_host_ptr((*((volatile uint32_t *)camry_host_ptr((uint32_t)(puVar3 + (int)camry_host_addr(puVar6) * 4 + -0x23a8)))))));
    uVar8 = 0;
    uVar4 = *puVar11;
    if ((puVar11[1] ^ uVar4) != 0xffffffff) goto LAB_00080250;
  }
  iVar2 = 5;
  if (8 < (uVar4 & 0xff)) {
    iVar2 = ((int)((uVar4 & 0xff) + 7) >> 3) * 2 + 3;
  }
  uVar8 = iVar2 + uVar8 + 2;
  if ((int)(uVar8 - descriptor->capacity_words) < 0 || uVar8 == descriptor->capacity_words) {
    local_34.confirmation_handle = CONCAT11(route_index,controller);
    local_34.raw_id = puVar11[2];
    local_34.data = camry_host_addr((uchar *)(puVar11 + 3));
    local_34.length = (uchar)uVar4;
    uVar8 = driver_admit_can_tx
                      ((*((ushort *)camry_host_ptr((uint32_t)((uint)route_index * 10 + (*((volatile int32_t *)camry_host_ptr((uint32_t)(puVar3 + uVar9 * 4 + -0x2518)))) + 6)))),
                       &local_34);
    if (uVar8 != 0) goto LAB_00080222;
    uVar1 = 0x5a;
    puVar5 = puVar5 + -0x6efc;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x218e8u + (uint32_t)(uVar9) * 4u)))) + (uint32_t)((int)camry_host_addr(puVar10)))))) = 0x5a;
  }
  else {
    iVar7 = 0xc3;
LAB_00080222:
    puVar6 = ((void *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x218e8u + (uint32_t)(uVar9) * 4u)))))));
    uVar1 = 0x3c;
    puVar5 = puVar10;
  }
  puVar6[(int)camry_host_addr(puVar5)] = uVar1;
  if (iVar7 != 0xc3) {
    return;
  }
LAB_00080250:
  set_controller_status_low_pair_two_80d2a(uVar9);
  return;
}

void service_can_tx_queues(uchar controller)

{
  F33CanQueueDescriptor *descriptor;
  byte bVar1;
  byte bVar2;
  uint uVar3;
  uint32_t puVar4;
  undefined *puVar5;
  undefined *puVar6;
  uint uVar7;
  undefined4 uVar8;
  ushort uVar9;
  
  uVar7 = (uint)controller;
  puVar4 = 0xfebeb800u;
  puVar6 = ((undefined *)camry_host_ptr(0x23dfcu));
  bVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x21972u + (uint32_t)(uVar7) * 1u))));
  for (uVar9 = 0; uVar9 < bVar1; uVar9 = uVar9 + 1 & 0xff) {
    descriptor = ((F33CanQueueDescriptor *)camry_host_ptr((uint32_t)((short)uVar9 * 10 + *(int *)(puVar6 + uVar7 * 4 + -0x2518))));
    bVar2 = descriptor->hardware_group;
    puVar5 = puVar6;
    uVar8 = call_interrupt_guard_and_return_zero_7a2da();
    if ((*((char *)camry_host_ptr((uint32_t)(*(int *)(puVar6 + uVar7 * 4 + -0x2514) + (uint)bVar2)))) != 'Z') {
      uVar3 = (uint)descriptor->queue_index;
      if ((((4 < (*((ushort *)camry_host_ptr((uint32_t)(puVar4 + uVar3 * 6 + -0x6f22))))) &&
           ((int)(((*((ushort *)camry_host_ptr((uint32_t)(puVar4 + uVar3 * 6 + -0x6f24)))) + 2) - (uint)descriptor->capacity_words
                 ) < 0 ||
            (*((ushort *)camry_host_ptr((uint32_t)(puVar4 + uVar3 * 6 + -0x6f24)))) + 2 == (uint)descriptor->capacity_words)) &&
          ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(uVar3 - 0x6efc))))) == 'i')) && ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(uVar3 - 0x6ef7))))) == '\0')) {
        attempt_queued_can_tx
                  (controller,(uchar)uVar9,descriptor,((ushort *)camry_host_ptr((uint32_t)(puVar4 + uVar3 * 6 + -0x6f26))));
      }
    }
    puVar6 = puVar5;
    ((void)(uVar8), thunk_pop_and_restore_priority_mask_stack_6a4c4());
  }
  return;
}

void tick_active_tx_queue_delays_and_service_802ee(void)

{
  char cVar1;
  ushort uVar2;
  byte bVar3;
  short sVar4;
  uint32_t puVar5;
  uint32_t puVar6;
  undefined4 uVar7;
  uint uVar8;
  ushort uVar9;
  uint uVar10;
  
  puVar5 = 0xfebeb800u;
  puVar6 = 0x23dfcu;
  uVar8 = (uint)DAT_00021970;
  for (uVar10 = 0; uVar10 < uVar8; uVar10 = uVar10 + 1 & 0xff) {
    bVar3 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(uVar10 - 0x248a)))));
    if (bVar3 != 0) {
      sVar4 = (*((short *)camry_host_ptr((uint32_t)(puVar5 + uVar10 * 2 + -0x6f28))));
      if ((sVar4 == 0x57a8) || (sVar4 == 0x6b94)) {
        for (uVar9 = 0; uVar9 < bVar3; uVar9 = uVar9 + 1 & 0xff) {
          uVar2 = (*((ushort *)camry_host_ptr((uint32_t)((short)uVar9 * 10 + (*((volatile int32_t *)camry_host_ptr((uint32_t)(puVar6 + uVar10 * 4 + -0x2518)))) + 8))));
          uVar7 = call_interrupt_guard_and_return_zero_7a2da();
          cVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(uVar2 - 0x6ef7)))));
          if (cVar1 != '\0') {
            (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(uVar2 - 0x6ef7))))) = cVar1 + -1;
          }
          ((void)(uVar7), thunk_pop_and_restore_priority_mask_stack_6a4c4());
        }
      }
      if ((sVar4 == 0x57a8) && ((*((short *)camry_host_ptr((uint32_t)(puVar5 + uVar10 * 2 + -0x6f02)))) == 0x5555)) {
        service_can_tx_queues((uchar)uVar10);
      }
    }
  }
  return;
}

bool test_tx_queue_controller_unavailable_8037a(uint param_1,byte param_2)

{
  bool bVar1;
  
  param_1 = param_1 & 0xff;
  bVar1 = true;
  if (param_1 < DAT_00021970) {
    if ((param_2 < (byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x21972u + (uint32_t)(param_1) * 1u))))) &&
       ((*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe48d8u + (uint32_t)(param_1) * 2u)))) == 0x57a8)) {
      bVar1 = *(short *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe48feu + (uint32_t)(param_1 * 2) * 1u)))) != 0x5555;
    }
  }
  return bVar1;
}

void attempt_first_eligible_group_can_tx_queue_803b0(byte param_1,uchar param_2)

{
  F33CanQueueDescriptor *descriptor;
  byte bVar1;
  bool bVar2;
  uint uVar3;
  uint32_t puVar4;
  uint32_t puVar5;
  ushort uVar6;
  
  puVar4 = 0xfebeb800u;
  puVar5 = 0x23dfcu;
  bVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x21972u + (uint32_t)(param_1) * 1u))));
  bVar2 = false;
  uVar6 = 0;
  while ((uVar6 < bVar1 && (!bVar2))) {
    descriptor = ((F33CanQueueDescriptor *)camry_host_ptr((uint32_t)((short)uVar6 * 10 + (*((volatile int *)camry_host_ptr((uint32_t)(0x23dfcu + (uint32_t)((uint)param_1 * 4 + -0x2518) * 1u)))))));
    if ((descriptor->completion_policy == '\0') && (param_2 == descriptor->hardware_group)) {
      uVar3 = (uint)descriptor->queue_index;
      if ((((4 < (*((ushort *)camry_host_ptr((uint32_t)(puVar4 + uVar3 * 6 + -0x6f22))))) &&
           ((int)(((*((ushort *)camry_host_ptr((uint32_t)(puVar4 + uVar3 * 6 + -0x6f24)))) + 2) - (uint)descriptor->capacity_words
                 ) < 0 ||
            (*((ushort *)camry_host_ptr((uint32_t)(puVar4 + uVar3 * 6 + -0x6f24)))) + 2 == (uint)descriptor->capacity_words)) &&
          ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(uVar3 - 0x6efc))))) == 'i')) && ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(uVar3 - 0x6ef7))))) == '\0')) {
        bVar2 = true;
        attempt_queued_can_tx
                  (param_1,(uchar)uVar6,descriptor,((ushort *)camry_host_ptr((uint32_t)(puVar4 + uVar3 * 6 + -0x6f26))));
      }
    }
    uVar6 = uVar6 + 1 & 0xff;
  }
  return;
}

void complete_queued_can_tx(ushort controller_route)

{
  uint8_t stack_record_38[56];
  ushort *puVar1;
  uint uVar2;
  undefined *puVar3;
  undefined *puVar4;
  uint32_t puVar5;
  int iVar6;
  undefined4 uVar7;
  int iVar8;
  uint uVar9;
  uint uVar10;
  uint uVar11;
  uint uVar12;
  char *pcVar13;
  char cVar14;
  uint uVar15;
  uint uVar16;
  uint *puVar17;
  uint *puStack_30;
  
  puVar3 = ((undefined *)camry_host_ptr(0xfebeb800u));
  puVar5 = 0x23dfcu;
  uVar15 = (uint)controller_route;
  uVar16 = uVar15 & 0xff;
  if ((uVar15 & 0xf0) == 0xf0) {
    ((void)(uVar15 & 0xf), (void)((int)uVar15 >> 8), return_only_stub_8152e());
    return;
  }
  iVar6 = test_tx_queue_controller_unavailable_8037a(uVar16, (controller_route >> 8));
  if (iVar6 != 0) {
    return;
  }
  puVar1 = ((ushort *)camry_host_ptr((uint32_t)((short)(controller_route >> 8) * 10 + (*((volatile int32_t *)camry_host_ptr((uint32_t)(puVar5 + uVar16 * 4 + -0x2518)))))))
  ;
  uVar12 = (uint)puVar1[4];
  uVar15 = (uint)(byte)puVar1[2];
  uVar7 = call_interrupt_guard_and_return_zero_7a2da();
  cVar14 = puVar3[uVar12 - 0x6efc];
  pcVar13 = puVar3 + (uVar12 - 0x6efc);
  if (cVar14 == 'Z') {
    uVar9 = (uint)*puVar1;
    uVar10 = (uint)*(ushort *)(puVar3 + uVar12 * 6 + -0x6f24);
    if ((*(ushort *)(puVar3 + uVar12 * 6 + -0x6f22) < 5) ||
       (-1 < (int)((uVar10 + 2) - uVar9) && uVar10 + 2 != uVar9)) {
LAB_0008056e:
      *pcVar13 = 'i';
      iVar6 = (*((int *)camry_host_ptr((uint32_t)(puVar5 + uVar16 * 4 + -0x2514))));
      puVar3[uVar12 - 0x6ef7] = (char)puVar1[1];
      (*((undefined1 *)camry_host_ptr((uint32_t)(iVar6 + uVar15)))) = 0x69;
      zero_controller_indexed_u16_counter_7f5da(uVar16,uVar15);
      goto LAB_000805a4;
    }
    iVar6 = 0;
    puVar17 = ((uint *)camry_host_ptr((uint32_t)(uVar10 * 4 + (*((volatile int32_t *)camry_host_ptr((uint32_t)(puVar5 + uVar12 * 4 + -0x23a8)))))));
    uVar2 = *puVar17;
    if ((puVar17[1] ^ uVar2) == 0xffffffff) {
      if (uVar2 == 0xffffffff) {
        puVar17 = (((uint *)camry_host_ptr((*((volatile uint32_t *)camry_host_ptr((uint32_t)(puVar5 + uVar12 * 4 + -0x23a8)))))));
        iVar6 = uVar9 - uVar10;
        uVar10 = 0;
        uVar2 = *puVar17;
        if ((puVar17[1] ^ uVar2) != 0xffffffff) goto LAB_00080562;
      }
      stack_record_38[7] = (undefined1)uVar2;
      stack_record_38[6] = (undefined1)(uVar2 >> 8);
      iVar8 = 5;
      if (8 < (uVar2 & 0xff)) {
        iVar8 = ((uVar2 & 0xff) + 7 >> 3) * 2 + 3;
      }
      uVar11 = (iVar8 + uVar10 & 0xffff) + 2;
      if (((int)(uVar11 - uVar9) < 0 || uVar11 == uVar9) &&
         ((iVar6 + iVar8 & 0xffffU) <= (uint)*(ushort *)(puVar3 + uVar12 * 6 + -0x6f22))) {
        puVar4 = puVar3;
        if ((uVar2 >> 8 & 0xff) != 0) {
          (*((uint32_t *)(stack_record_38 + 0))) = puVar17[2];
          (*((uint16_t *)(stack_record_38 + 4))) = (undefined2)(uVar2 >> 0x10);
          puStack_30 = puVar17 + 3;
          enqueue_message_ring_with_complement_header_80a4a(uVar16,((uint32_t *)(stack_record_38)));
        }
        *(short *)(puVar3 + uVar12 * 6 + -0x6f24) = (short)(iVar8 + uVar10);
        *(short *)(puVar3 + uVar12 * 6 + -0x6f22) =
             *(short *)(puVar3 + uVar12 * 6 + -0x6f22) - (short)(iVar6 + iVar8);
        puVar3 = puVar4;
        goto LAB_0008056e;
      }
    }
LAB_00080562:
    cVar14 = -0x3d;
  }
  else {
    if (cVar14 == '<') goto LAB_0008056e;
    if (((int8_t)cVar14) != -0x3d) goto LAB_000805a4;
  }
  *pcVar13 = cVar14;
  set_controller_status_low_pair_two_80d2a(uVar16);
LAB_000805a4:
  ((void)(uVar7), thunk_pop_and_restore_priority_mask_stack_6a4c4());
  if ((cVar14 == 'Z') && ((*((char *)camry_host_ptr((uint32_t)((int)camry_host_addr(puVar1) + 3)))) == '\0')) {
    attempt_first_eligible_group_can_tx_queue_803b0(uVar16,uVar15);
  }
  return;
}

void initialize_tx_queue_buffers_and_group_counters_805c6(void)

{
  ushort *puVar1;
  undefined2 *puVar2;
  ushort uVar3;
  uint32_t puVar4;
  uint32_t puVar5;
  ushort uVar6;
  uint uVar7;
  int iVar8;
  uint uVar9;
  uint uVar10;
  uint uVar11;
  uint uVar12;
  uint uVar13;
  
  puVar4 = 0xfebeb800u;
  puVar5 = 0x23dfcu;
  uVar10 = (uint)DAT_00021970;
  for (uVar13 = 0; uVar13 < uVar10; uVar13 = uVar13 + 1 & 0xff) {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(uVar13 - 0x6ef2))))) = 0;
    uVar6 = (ushort)(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(uVar13 - 0x248a)))));
    if (uVar6 == 0) {
      uVar6 = 1;
      uVar11 = 1;
    }
    else {
      uVar11 = (uint)(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(uVar13 - 0x2489)))));
    }
    for (uVar3 = 0; uVar3 < uVar6; uVar3 = uVar3 + 1 & 0xff) {
      puVar1 = ((ushort *)camry_host_ptr((uint32_t)((short)uVar3 * 10 + (*((volatile int *)camry_host_ptr((uint32_t)(0x23dfcu + (uint32_t)(uVar13 * 4 + -0x2518) * 1u)))))));
      uVar7 = (uint)puVar1[4];
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(uVar7 - 0x6ef7))))) = 0;
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(uVar7 - 0x6efc))))) = 0x69;
      puVar2 = ((undefined2 *)camry_host_ptr((uint32_t)(puVar4 + uVar7 * 6 + -0x6f26)));
      *puVar2 = 0;
      puVar2[1] = 0;
      puVar2[2] = 0;
      uVar12 = (uint)*puVar1;
      uVar9 = 0;
      if (uVar12 == 0) {
        uVar12 = 1;
      }
      iVar8 = (*((int *)camry_host_ptr((uint32_t)(puVar5 + uVar7 * 4 + -0x23a8))));
      for (; uVar9 < uVar12; uVar9 = uVar9 + 1 & 0xffff) {
        (*((undefined4 *)camry_host_ptr((uint32_t)(uVar9 * 4 + iVar8)))) = 0;
      }
    }
    for (uVar12 = 0; uVar12 < uVar11; uVar12 = uVar12 + 1 & 0xff) {
      (*((undefined1 *)camry_host_ptr((uint32_t)((*((volatile int32_t *)camry_host_ptr((uint32_t)(puVar5 + uVar13 * 4 + -0x2514)))) + uVar12)))) = 0x69;
      zero_controller_indexed_u16_counter_7f5da(uVar13,uVar12);
    }
  }
  uVar10 = 0;
  do {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(uVar10 - 0x684e))))) = 0;
    uVar10 = uVar10 + 1;
  } while (uVar10 < 0x40);
  (*((undefined4 *)camry_host_ptr((uint32_t)(puVar4 + -0x6808)))) = 0;
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar4 + -0x6804)))) = 0;
  return;
}

void reset_controller_tx_queues_and_delays_806a4(uint param_1)

{
  undefined2 *puVar1;
  byte bVar2;
  uint32_t puVar3;
  uint32_t puVar4;
  undefined4 uVar5;
  ushort uVar6;
  uint uVar7;
  
  puVar3 = 0xfebeb800u;
  puVar4 = 0x23dfcu;
  param_1 = param_1 & 0xff;
  bVar2 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x21972u + (uint32_t)(param_1) * 1u))));
  if (bVar2 != 0) {
    for (uVar6 = 0; uVar6 < bVar2; uVar6 = uVar6 + 1 & 0xff) {
      uVar7 = (uint)(*((ushort *)camry_host_ptr((uint32_t)((short)uVar6 * 10 + (*((volatile int32_t *)camry_host_ptr((uint32_t)(puVar4 + param_1 * 4 + -0x2518)))) + 8))));
      uVar5 = call_interrupt_guard_and_return_zero_7a2da();
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(uVar7 - 0x6ef7))))) = 0;
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(uVar7 - 0x6efc))))) = 0x69;
      puVar1 = ((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + uVar7 * 6 + -0x6f26)));
      *puVar1 = 0;
      puVar1[1] = 0;
      puVar1[2] = 0;
      ((void)(uVar5), thunk_pop_and_restore_priority_mask_stack_6a4c4());
    }
    bVar2 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(param_1 - 0x2489)))));
    for (uVar7 = 0; uVar7 < bVar2; uVar7 = uVar7 + 1 & 0xff) {
      uVar5 = call_interrupt_guard_and_return_zero_7a2da();
      (*((undefined1 *)camry_host_ptr((uint32_t)((*((volatile int32_t *)camry_host_ptr((uint32_t)(puVar4 + param_1 * 4 + -0x2514)))) + uVar7)))) = 0x69;
      zero_controller_indexed_u16_counter_7f5da(param_1,uVar7);
      ((void)(uVar5), thunk_pop_and_restore_priority_mask_stack_6a4c4());
    }
  }
  return;
}

void reset_controller_tx_queues_preserve_delays_80740(uint param_1)

{
  undefined2 *puVar1;
  byte bVar2;
  uint32_t puVar3;
  uint32_t puVar4;
  undefined4 uVar5;
  ushort uVar6;
  uint uVar7;
  
  puVar3 = 0xfebeb800u;
  puVar4 = 0x23dfcu;
  param_1 = param_1 & 0xff;
  bVar2 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x21972u + (uint32_t)(param_1) * 1u))));
  if (bVar2 != 0) {
    for (uVar6 = 0; uVar6 < bVar2; uVar6 = uVar6 + 1 & 0xff) {
      uVar7 = (uint)(*((ushort *)camry_host_ptr((uint32_t)((short)uVar6 * 10 + (*((volatile int32_t *)camry_host_ptr((uint32_t)(puVar4 + param_1 * 4 + -0x2518)))) + 8))));
      uVar5 = call_interrupt_guard_and_return_zero_7a2da();
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(uVar7 - 0x6efc))))) = 0x69;
      puVar1 = ((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + uVar7 * 6 + -0x6f26)));
      *puVar1 = 0;
      puVar1[1] = 0;
      puVar1[2] = 0;
      ((void)(uVar5), thunk_pop_and_restore_priority_mask_stack_6a4c4());
    }
    bVar2 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(param_1 - 0x2489)))));
    for (uVar7 = 0; uVar7 < bVar2; uVar7 = uVar7 + 1 & 0xff) {
      uVar5 = call_interrupt_guard_and_return_zero_7a2da();
      (*((undefined1 *)camry_host_ptr((uint32_t)((*((volatile int32_t *)camry_host_ptr((uint32_t)(puVar4 + param_1 * 4 + -0x2514)))) + uVar7)))) = 0x69;
      zero_controller_indexed_u16_counter_7f5da(param_1,uVar7);
      ((void)(uVar5), thunk_pop_and_restore_priority_mask_stack_6a4c4());
    }
  }
  return;
}

void reset_controller_tx_queues_reload_changed_delays_807d8(uint param_1)

{
  int iVar1;
  undefined2 *puVar2;
  byte bVar3;
  uint32_t puVar4;
  uint32_t puVar5;
  undefined4 uVar6;
  ushort uVar7;
  uint uVar8;
  
  puVar4 = 0xfebeb800u;
  puVar5 = 0x23dfcu;
  param_1 = param_1 & 0xff;
  bVar3 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x21972u + (uint32_t)(param_1) * 1u))));
  if (bVar3 != 0) {
    for (uVar7 = 0; uVar7 < bVar3; uVar7 = uVar7 + 1 & 0xff) {
      iVar1 = (short)uVar7 * 10 + (*((int *)camry_host_ptr((uint32_t)(puVar5 + param_1 * 4 + -0x2518))));
      uVar8 = (uint)(*((ushort *)camry_host_ptr((uint32_t)(iVar1 + 8))));
      uVar6 = call_interrupt_guard_and_return_zero_7a2da();
      if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(uVar8 - 0x6efc))))) != 'i') {
        (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(uVar8 - 0x6ef7))))) = (*((undefined1 *)camry_host_ptr((uint32_t)(iVar1 + 2))));
      }
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(uVar8 - 0x6efc))))) = 'i';
      puVar2 = ((undefined2 *)camry_host_ptr((uint32_t)(puVar4 + uVar8 * 6 + -0x6f26)));
      *puVar2 = 0;
      puVar2[1] = 0;
      puVar2[2] = 0;
      ((void)(uVar6), thunk_pop_and_restore_priority_mask_stack_6a4c4());
    }
    bVar3 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(param_1 - 0x2489)))));
    for (uVar8 = 0; uVar8 < bVar3; uVar8 = uVar8 + 1 & 0xff) {
      uVar6 = call_interrupt_guard_and_return_zero_7a2da();
      (*((undefined1 *)camry_host_ptr((uint32_t)((*((volatile int32_t *)camry_host_ptr((uint32_t)(puVar5 + param_1 * 4 + -0x2514)))) + uVar8)))) = 0x69;
      zero_controller_indexed_u16_counter_7f5da(param_1,uVar8);
      ((void)(uVar6), thunk_pop_and_restore_priority_mask_stack_6a4c4());
    }
  }
  return;
}

void dispatch_message_to_six_masked_callbacks_80884(uint param_1,undefined4 *param_2)

{
  byte bVar1;
  uint32_t puVar2;
  uint32_t puVar3;
  uint uVar4;
  byte bVar5;
  
  puVar2 = 0xfebeb800u;
  puVar3 = 0x23dfcu;
  param_1 = param_1 & 0xff;
  bVar5 = 1;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe490fu + (uint32_t)(param_1) * 1u)))) = 1;
  DAT_febe4ff4 = *param_2;
  bVar1 = (*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_2) + 6))));
  uVar4 = 0;
  do {
    if ((bVar5 & bVar1) != 0) {
      (*(int (*)())camry_indirect((uint32_t)(*((code * *)camry_host_ptr((uint32_t)(puVar3 + ((short)param_1 * 6 + uVar4) * 4 + -0x23d8))))))(param_1,camry_host_addr(param_2),uVar4);
    }
    uVar4 = uVar4 + 1;
    bVar5 = bVar5 << 1;
  } while (uVar4 < 6);
  (*((undefined4 *)camry_host_ptr((uint32_t)(puVar2 + -0x680c)))) = 0xffffffff;
  return;
}

void consume_complement_checked_message_ring_808d6(uint param_1)

{
  uint8_t stack_record_38[56];
  int iVar1;
  ushort uVar2;
  bool bVar3;
  uint uVar4;
  undefined8 uVar5;
  undefined4 uVar6;
  int iVar7;
  int iVar8;
  uint uVar9;
  uint uVar10;
  int iVar11;
  uint uVar12;
  uint uVar13;
  uint uVar14;
  uint uVar15;
  uint *puVar16;
  uint *puStack_30;
  
  uVar5 = 0x23dfcfebeb800;
  param_1 = param_1 & 0xff;
  iVar1 = (int)(short)param_1;
  bVar3 = false;
  iVar11 = 0x69;
  uVar10 = (uint)*(ushort *)(((undefined *)camry_host_ptr((uint32_t)(0x21966u + (uint32_t)(param_1 * 2) * 1u))));
  uVar6 = call_interrupt_guard_and_return_zero_7a2da();
  uVar14 = (uint)(ushort)(*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe48fau + (uint32_t)(iVar1 * 3) * 2u))));
  uVar2 = (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe48fcu + (uint32_t)(iVar1 * 3) * 2u))));
  uVar13 = (uint)uVar2;
  ((void)(uVar6), thunk_pop_and_restore_priority_mask_stack_6a4c4());
  uVar12 = 0;
  if (uVar10 < uVar13) {
    return;
  }
  while( true ) {
    do {
      if (-1 < (int)((uVar12 + 5) - (uint)uVar2) && uVar12 + 5 != (uint)uVar2) {
        return;
      }
      if (bVar3) {
        return;
      }
      bVar3 = true;
    } while (-1 < (int)((uVar14 + 2) - uVar10) && uVar14 + 2 != uVar10);
    iVar7 = param_1 * 4 + (int)((ulonglong)uVar5 >> 0x20);
    iVar8 = 0;
    puVar16 = ((uint *)camry_host_ptr((uint32_t)(uVar14 * 4 + (*((volatile int32_t *)camry_host_ptr((uint32_t)(iVar7 + -0x24f8)))))));
    uVar4 = *puVar16;
    uVar15 = uVar14;
    if ((puVar16[1] ^ uVar4) != 0xffffffff) break;
    if (uVar4 == 0xffffffff) {
      puVar16 = ((uint *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)((iVar7 + -0x24f8))))))));
      iVar8 = uVar10 - uVar14;
      uVar15 = 0;
      uVar4 = *puVar16;
      if ((puVar16[1] ^ uVar4) != 0xffffffff) break;
    }
    uVar14 = uVar15;
    if (iVar11 == 0x69) {
      iVar7 = 5;
      if (8 < (uVar4 & 0xff)) {
        iVar7 = ((uVar4 & 0xff) + 7 >> 3) * 2 + 3;
      }
      uVar14 = iVar7 + uVar15 & 0xffff;
      uVar9 = iVar8 + iVar7 & 0xffff;
      if ((-1 < (int)((uVar14 + 2) - uVar10) && uVar14 + 2 != uVar10) || (uVar13 < uVar9)) break;
      stack_record_38[6] = (undefined1)(uVar4 >> 8);
      (*((uint16_t *)(stack_record_38 + 4))) = (undefined2)(uVar4 >> 0x10);
      (*((uint32_t *)(stack_record_38 + 0))) = puVar16[2];
      stack_record_38[7] = (undefined1)uVar4;
      puStack_30 = puVar16 + 3;
      if ((uVar4 >> 0xf & 1) == 0) {
        dispatch_message_to_six_masked_callbacks_80884(param_1,((uint32_t *)(stack_record_38)));
      }
      else {
        dispatch_six_bank_message_with_global_payload_81362((uint)(byte)param_1, camry_host_addr(((uint32_t *)(stack_record_38))));
      }
      uVar6 = call_interrupt_guard_and_return_zero_7a2da();
      (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe48fau + (uint32_t)(iVar1 * 3) * 2u)))) = (short)(iVar7 + uVar15);
      uVar13 = (ushort)(*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe48fcu + (uint32_t)(iVar1 * 3) * 2u)))) - uVar9 & 0xffff;
      (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe48fcu + (uint32_t)(iVar1 * 3) * 2u)))) = (short)((ushort)(*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe48fcu + (uint32_t)(iVar1 * 3) * 2u)))) - uVar9);
      ((void)(uVar6), thunk_pop_and_restore_priority_mask_stack_6a4c4());
      bVar3 = false;
      uVar12 = uVar12 + uVar9 & 0xffff;
    }
    if (iVar11 == 0xc3) {
LAB_000809e4:
      set_controller_status_low_pair_two_80d2a(param_1);
    }
  }
  uVar14 = uVar15;
  iVar11 = 0xc3;
  goto LAB_000809e4;
}

void service_enabled_controller_message_rings_809fe(void)

{
  int iVar1;
  uint32_t puVar2;
  uint32_t puVar3;
  uint uVar4;
  uint uVar5;
  
  puVar2 = 0xfebeb800u;
  puVar3 = 0x23dfcu;
  uVar4 = (uint)DAT_00021970;
  for (uVar5 = 0; uVar5 < uVar4; uVar5 = uVar5 + 1 & 0xff) {
    iVar1 = uVar5 * 2;
    if ((*((short *)camry_host_ptr((uint32_t)(puVar3 + iVar1 + -0x2496)))) != 0) {
      if ((((*((short *)camry_host_ptr((uint32_t)(puVar2 + iVar1 + -0x6f28)))) == 0x57a8) ||
          ((*((short *)camry_host_ptr((uint32_t)(puVar2 + iVar1 + -0x6f28)))) == 0x6b94)) &&
         (((*((ushort *)camry_host_ptr((uint32_t)(puVar2 + iVar1 + -0x6f02)))) & 3) == 1)) {
        consume_complement_checked_message_ring_808d6(uVar5);
      }
    }
  }
  return;
}

undefined4 enqueue_message_ring_with_complement_header_80a4a(uint param_1,uint *param_2)

{
  undefined4 *puVar1;
  uint *puVar2;
  undefined1 *puVar3;
  undefined1 *puVar4;
  int iVar5;
  undefined1 uVar6;
  undefined1 uVar7;
  undefined1 uVar8;
  byte bVar9;
  uint uVar10;
  uint uVar11;
  uint uVar12;
  uint32_t puVar13;
  undefined4 uVar14;
  int iVar15;
  uint uVar16;
  uint uVar17;
  uint uVar18;
  uint uVar19;
  uint uVar20;
  uint uVar21;
  
  puVar13 = 0x23dfcu;
  param_1 = param_1 & 0xff;
  uVar18 = *param_2;
  uVar19 = (uint)(*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_2) + 7))));
  uVar10 = 8;
  if ((uVar18 >> 0x1e & 1) != 0) {
    uVar10 = 0x40;
  }
  iVar5 = (int)(short)param_1;
  if (uVar19 <= uVar10) {
    uVar10 = uVar19;
  }
  uVar20 = (uint)*(ushort *)(((undefined *)camry_host_ptr((uint32_t)(0x21966u + (uint32_t)(param_1 * 2) * 1u))));
  uVar14 = call_interrupt_guard_and_return_zero_7a2da();
  uVar11 = (uint)(ushort)(*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe48f8u + (uint32_t)(iVar5 * 3) * 2u))));
  uVar17 = (uint)(ushort)(*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe48fcu + (uint32_t)(iVar5 * 3) * 2u))));
  if (((int)((uVar11 + 2) - uVar20) < 0 || uVar11 + 2 == uVar20) && (uVar17 <= uVar20)) {
    iVar15 = 5;
    if (8 < uVar19) {
      iVar15 = ((int)(uVar19 + 7) >> 3) * 2 + 3;
    }
    uVar16 = uVar20 - uVar11 & 0xffff;
    uVar12 = uVar11;
    uVar21 = uVar20;
    if (-1 < (int)((iVar15 + 2U) - uVar16) && iVar15 + 2U != uVar16) {
      uVar17 = uVar17 + uVar16;
      uVar12 = 0;
      uVar21 = uVar11;
    }
    if ((iVar15 + uVar17 & 0xffff) <= uVar20) {
      if (uVar21 < uVar20) {
        puVar1 = ((undefined4 *)camry_host_ptr((uint32_t)(uVar21 * 4 + (*((volatile int *)camry_host_ptr((uint32_t)(0x23dfcu + (uint32_t)(param_1 * 4 + -0x24f8) * 1u)))))));
        *puVar1 = 0xffffffff;
        puVar1[1] = 0;
      }
      (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe48f8u + (uint32_t)(iVar5 * 3) * 2u)))) = (short)iVar15 + (short)uVar12;
      (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe48fcu + (uint32_t)(iVar5 * 3) * 2u)))) = (short)(iVar15 + uVar17);
      uVar17 = param_2[1];
      puVar2 = ((uint *)camry_host_ptr((uint32_t)(uVar12 * 4 + (*((volatile int *)camry_host_ptr((uint32_t)(0x23dfcu + (uint32_t)(param_1 * 4 + -0x24f8) * 1u)))))));
      bVar9 = (*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_2) + 6))));
      puVar2[2] = uVar18;
      uVar18 = param_2[2];
      uVar19 = uVar19 + (uint)bVar9 * 0x100 + (uint)(ushort)uVar17 * 0x10000;
      *puVar2 = uVar19;
      puVar2[1] = ~uVar19;
      for (uVar19 = 0; uVar19 < uVar10; uVar19 = uVar19 + 4 & 0xff) {
        puVar3 = ((undefined1 *)camry_host_ptr((uint32_t)(uVar19 + uVar18)));
        uVar6 = puVar3[1];
        uVar7 = puVar3[2];
        uVar8 = puVar3[3];
        puVar4 = ((undefined1 *)camry_host_ptr((uint32_t)((int)camry_host_addr(puVar2) + uVar19 + 0xc)));
        *puVar4 = *puVar3;
        puVar4[1] = uVar6;
        puVar4[2] = uVar7;
        puVar4[3] = uVar8;
      }
    }
  }
  ((void)(uVar14), thunk_pop_and_restore_priority_mask_stack_6a4c4());
  return uVar14;
}

void enqueue_mapped_message_when_controller_ready_80b42(ushort param_1,undefined4 param_2,undefined1 param_3,undefined4 param_4)

{
  uint8_t stack_record_2c[44];
  uint32_t puVar1;
  uint32_t puVar2;
  int iVar3;
  uint uVar4;
  uint uVar5;
  
  puVar1 = 0xfebeb800u;
  puVar2 = 0x23dfcu;
  uVar4 = (uint)param_1;
  if (uVar4 < DAT_00021964) {
    stack_record_2c[18] = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x219acu + (uint32_t)(uVar4) * 1u))));
    uVar5 = (uint)stack_record_2c[18];
    if (uVar5 != 0xff) {
      (*((uint32_t *)(stack_record_2c + 12))) = param_2;
      (*((uint16_t *)(stack_record_2c + 16))) = param_1;
      iVar3 = ((void)(((uint32_t *)((stack_record_2c + 12)))), (void)(param_3), (void)(param_4), return_const_0_814ae());
      if (((iVar3 == 0) && ((*((short *)camry_host_ptr((uint32_t)(puVar1 + uVar5 * 2 + -0x6f28)))) == 0x57a8)) &&
         ((*((short *)camry_host_ptr((uint32_t)(puVar1 + uVar5 * 2 + -0x6f02)))) == 0x5555)) {
        stack_record_2c[6] = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(uVar4 - 0x2420)))));
        (*((uint16_t *)(stack_record_2c + 4))) = 0;
        (*((uint32_t *)(stack_record_2c + 0))) = param_2;
        stack_record_2c[7] = param_3;
        (*((uint32_t *)(stack_record_2c + 8))) = param_4;
        enqueue_message_ring_with_complement_header_80a4a(uVar5,((uint32_t *)(stack_record_2c)));
        (*(int (*)())camry_indirect((uint32_t)(*((code * *)camry_host_ptr((uint32_t)(puVar2 + -0x24bc))))))(uVar5);
      }
    }
  }
  return;
}

void initialize_all_message_ring_storage_80bc2(void)

{
  int iVar1;
  uint uVar2;
  uint32_t puVar3;
  uint uVar4;
  uint uVar5;
  uint uVar6;
  
  uVar4 = (uint)DAT_00021970;
  for (uVar2 = 0; uVar2 < uVar4; uVar2 = uVar2 + 1 & 0xff) {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe490fu + (uint32_t)(uVar2) * 1u)))) = 0;
    iVar1 = (int)(short)uVar2;
    (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe48f8u + (uint32_t)(iVar1 * 3) * 2u)))) = 0;
    (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe48fau + (uint32_t)(iVar1 * 3) * 2u)))) = 0;
    (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe48fcu + (uint32_t)(iVar1 * 3) * 2u)))) = 0;
    uVar6 = 0;
    uVar5 = (uint)*(ushort *)(((undefined *)camry_host_ptr((uint32_t)(0x21966u + (uint32_t)(uVar2 * 2) * 1u))));
    if (uVar5 == 0) {
      uVar5 = 1;
    }
    puVar3 = ((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x21904u + (uint32_t)(uVar2) * 4u))))));
    for (; uVar6 < uVar5; uVar6 = uVar6 + 1 & 0xffff) {
      (*((volatile uint32_t *)camry_host_ptr((uint32_t)(puVar3 + uVar6 * 4)))) = 0;
    }
  }
  DAT_febe4ff4 = 0xffffffff;
  return;
}

void clear_configured_controller_ring_indices_80c20(uint param_1)

{
  undefined2 *puVar1;
  uint32_t puVar2;
  undefined4 uVar3;
  
  puVar2 = 0xfebeb800u;
  if (*(short *)(((undefined *)camry_host_ptr((uint32_t)(0x21966u + (uint32_t)((param_1 & 0xff) * 2) * 1u)))) != 0) {
    uVar3 = call_interrupt_guard_and_return_zero_7a2da();
    puVar1 = ((undefined2 *)camry_host_ptr((uint32_t)(puVar2 + (short)(param_1 & 0xff) * 6 + -0x6f08)));
    *puVar1 = 0;
    puVar1[1] = 0;
    puVar1[2] = 0;
    ((void)(uVar3), thunk_pop_and_restore_priority_mask_stack_6a4c4());
  }
  return;
}

uint32_t set_controller_status_pair_on_80_result_80c54(uint param_1)

{
  uint32_t camry_r10_result;
  uint32_t puVar1;
  int iVar2;
  undefined4 uVar3;
  
  puVar1 = 0xfebeb800u;
  iVar2 = (camry_r10_result = map_network_zero_stub_result_to_fault_bit_80_7cda0((uint)(byte)param_1));
  if (iVar2 == 0x80) {
    uVar3 = (camry_r10_result = call_interrupt_guard_and_return_zero_7a2da());
    (*((ushort *)camry_host_ptr((uint32_t)(puVar1 + (param_1 & 0xff) * 2 + -0x6f02)))) =
         (*((ushort *)camry_host_ptr((uint32_t)(puVar1 + (param_1 & 0xff) * 2 + -0x6f02)))) & 0xffcf | 0x20;
    ((void)(uVar3), thunk_pop_and_restore_priority_mask_stack_6a4c4());
  }
  return camry_r10_result;
}

void poll_cached_controller_hooks_and_status_80c88(void)

{
  uint32_t puVar1;
  uint32_t puVar2;
  uint uVar3;
  uint uVar4;
  
  puVar1 = 0xfebeb800u;
  puVar2 = 0x23dfcu;
  uVar3 = (uint)DAT_00021970;
  uVar4 = 0;
  do {
    if (uVar3 <= uVar4) {
      return;
    }
    if ((*((short *)camry_host_ptr((uint32_t)(puVar1 + uVar4 * 2 + -0x6f28)))) == 0x57a8) {
      (*(int (*)())camry_indirect((uint32_t)(((((code *)(uintptr_t)((uint32_t)((uintptr_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(puVar2 + -0x24b4))))))))))))(uVar4);
      (*(int (*)())camry_indirect((uint32_t)(((((code *)(uintptr_t)((uint32_t)((uintptr_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(puVar2 + -0x24b8))))))))))))(uVar4);
LAB_00080cc0:
      set_controller_status_pair_on_80_result_80c54(uVar4);
    }
    else if ((*((short *)camry_host_ptr((uint32_t)(puVar1 + uVar4 * 2 + -0x6f28)))) == 0x6b94) goto LAB_00080cc0;
    uVar4 = uVar4 + 1 & 0xff;
  } while( true );
}

void publish_mapped_controller_bus_off_event(uchar driver_index)

{
  uint32_t puVar1;
  undefined4 uVar2;
  uint uVar3;
  
  puVar1 = 0xfebeb800u;
  if ((uint)driver_index < (uint)DAT_00021971) {
    uVar3 = (uint)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x21978u + (uint32_t)(driver_index) * 1u))));
    if (uVar3 != 0xff) {
      if (((*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe48d8u + (uint32_t)(uVar3) * 2u)))) == 0x57a8) ||
         ((*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe48d8u + (uint32_t)(uVar3) * 2u)))) == 0x6b94)) {
        uVar2 = call_interrupt_guard_and_return_zero_7a2da();
        (*((ushort *)camry_host_ptr((uint32_t)(puVar1 + uVar3 * 2 + -0x6f02)))) =
             (*((ushort *)camry_host_ptr((uint32_t)(puVar1 + uVar3 * 2 + -0x6f02)))) & 0xff3f | 0x80;
        ((void)(uVar2), thunk_pop_and_restore_priority_mask_stack_6a4c4());
        ((void)(uVar3), return_only_stub_832ee());
      }
    }
  }
  return;
}

undefined4 set_controller_status_low_pair_two_80d2a(uint param_1)

{
  uint32_t puVar1;
  undefined4 uVar2;
  
  puVar1 = 0xfebeb800u;
  uVar2 = call_interrupt_guard_and_return_zero_7a2da();
  (*((ushort *)camry_host_ptr((uint32_t)(puVar1 + (param_1 & 0xff) * 2 + -0x6f02)))) =
       (*((ushort *)camry_host_ptr((uint32_t)(puVar1 + (param_1 & 0xff) * 2 + -0x6f02)))) & 0xfffc | 2;
  ((void)(uVar2), thunk_pop_and_restore_priority_mask_stack_6a4c4());
  return uVar2;
}

void mark_status_for_mapped_valid_driver_channel_80d54(uint param_1)

{
  if (((param_1 & 0xff) < (uint)DAT_00021971) &&
     ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x21978u + (uint32_t)(param_1 & 0xff) * 1u)))) != 0xff)) {
    set_controller_status_low_pair_two_80d2a((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x21978u + (uint32_t)(param_1 & 0xff) * 1u)))));
  }
  return;
}

uint decode_status_pair_failures_to_mask_80d76(uint param_1)

{
  uint uVar1;
  
  uVar1 = (uint)((param_1 & 0xc0) != 0x40);
  if ((param_1 & 0x30) != 0x10) {
    uVar1 = uVar1 | 0x80;
  }
  if ((param_1 & 0xc) != 4) {
    uVar1 = uVar1 | 2;
  }
  if ((param_1 & 3) != 1) {
    uVar1 = uVar1 | 0x20;
  }
  if ((param_1 & 0x300) != 0x100) {
    uVar1 = uVar1 | 0x100;
  }
  if (uVar1 == 0) {
    uVar1 = 0x20;
  }
  return uVar1;
}

uint compose_controller_status_error_mask_80dc0(uint param_1)

{
  char cVar1;
  char cVar2;
  char cVar3;
  short sVar4;
  uint32_t puVar5;
  undefined4 uVar6;
  uint uVar7;
  
  puVar5 = 0xfebeb800u;
  param_1 = param_1 & 0xff;
  uVar6 = call_interrupt_guard_and_return_zero_7a2da();
  cVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(param_1 - 0x6ef0)))));
  cVar2 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(param_1 - 0x6eef)))));
  sVar4 = (*((short *)camry_host_ptr((uint32_t)(puVar5 + param_1 * 2 + -0x6f02))));
  cVar3 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(param_1 - 0x6eee)))));
  ((void)(uVar6), thunk_pop_and_restore_priority_mask_stack_6a4c4());
  uVar7 = 0;
  if (sVar4 != 0x5555) {
    uVar7 = decode_status_pair_failures_to_mask_80d76(sVar4);
  }
  if (cVar1 != 'U') {
    uVar7 = uVar7 | 4;
  }
  if (cVar2 != 'U') {
    uVar7 = uVar7 | 0x200;
  }
  if (((int8_t)cVar3) == -0x5b) {
    uVar7 = uVar7 | 0x10;
  }
  else if (cVar3 == 'Z') {
    uVar7 = uVar7 | 0x40;
  }
  else if (cVar3 != 'K') {
    uVar7 = uVar7 | 8;
  }
  return uVar7;
}

undefined4 initialize_controller_status_by_mode_80e32(uint param_1,char param_2)

{
  uint32_t puVar1;
  undefined4 uVar2;
  ushort uVar3;
  undefined1 uVar4;
  undefined *puVar5;
  
  puVar1 = 0xfebeb800u;
  param_1 = param_1 & 0xff;
  uVar2 = call_interrupt_guard_and_return_zero_7a2da();
  uVar4 = 0x55;
  if (param_2 == '\0') {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(param_1 - 0x6ef0))))) = 0x55;
    puVar5 = ((undefined *)camry_host_ptr((uint32_t)(puVar1 + -0x6eee)));
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(param_1 - 0x6eef))))) = 0x55;
    uVar3 = 0x5555;
    uVar4 = 0x4b;
  }
  else {
    puVar5 = ((undefined *)camry_host_ptr((uint32_t)(puVar1 + -0x6eef)));
    if (param_2 == '\x02') {
      uVar3 = 0x5555;
    }
    else {
      uVar3 = (*((ushort *)camry_host_ptr((uint32_t)(puVar1 + param_1 * 2 + -0x6f02)))) & 3 | 0x5554;
    }
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(param_1 - 0x6ef0))))) = 0x55;
  }
  (*((ushort *)camry_host_ptr((uint32_t)(puVar1 + param_1 * 2 + -0x6f02)))) = uVar3;
  puVar5[param_1] = uVar4;
  ((void)(uVar2), thunk_pop_and_restore_priority_mask_stack_6a4c4());
  return uVar2;
}

undefined4 aggregate_mapped_driver_status_priority_80eb0(char param_1)

{
  char cVar1;
  undefined8 uVar2;
  uint uVar3;
  undefined4 uVar4;
  uint uVar5;
  uint uVar6;
  uint uVar7;
  
  cVar1 = DAT_00021975;
  uVar2 = 0x23dfc00000000;
  uVar7 = 0;
  uVar5 = (uint)DAT_00021971;
  for (uVar6 = 0; uVar6 < uVar5; uVar6 = uVar6 + 1 & 0xff) {
    if (param_1 == (*((char *)camry_host_ptr((uint32_t)(uVar6 + (int)((ulonglong)uVar2 >> 0x20) + -0x2484))))) {
      uVar3 = poll_driver_channel_retry_status_wrapper_8157a(uVar6);
      if ((uVar3 == 4) && (cVar1 == '\0')) {
        uVar3 = 1;
      }
      uVar7 = uVar7 | uVar3;
    }
  }
  if (uVar7 == 0) {
    uVar4 = 0;
  }
  else if ((uVar7 & 1) == 0) {
    if ((uVar7 >> 1 & 1) == 0) {
      if ((uVar7 >> 2 & 1) == 0) {
        uVar4 = 99;
      }
      else {
        uVar4 = 3;
      }
    }
    else {
      uVar4 = 2;
    }
  }
  else {
    uVar4 = 1;
  }
  return uVar4;
}

undefined4 validate_u16_ring_index_triplet_80f16(ushort *param_1,ushort param_2)

{
  ushort uVar1;
  ushort uVar2;
  ushort uVar3;
  ushort uVar4;
  undefined4 uVar5;
  undefined4 uVar6;
  
  uVar6 = 0;
  uVar5 = call_interrupt_guard_and_return_zero_7a2da();
  uVar2 = *param_1;
  uVar3 = param_1[1];
  uVar4 = param_1[2];
  ((void)(uVar5), thunk_pop_and_restore_priority_mask_stack_6a4c4());
  uVar1 = uVar4 + (uVar3 - uVar2);
  if ((((param_2 <= uVar2) || (param_2 <= uVar3)) || (param_2 < uVar4)) ||
     ((uVar1 != 0 && (uVar1 != param_2)))) {
    uVar6 = 1;
  }
  return uVar6;
}

void store_controller_request_result_byte_80f5a(uint param_1,undefined1 param_2)

{
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe4912u + (uint32_t)(param_1 & 0xff) * 1u)))) = param_2;
  return;
}

void return_only_stub_80f64(void)

{
  return;
}

void return_only_stub_80f66(void)

{
  return;
}

void return_only_stub_80f68(void)

{
  return;
}

void return_only_stub_80f6a(void)

{
  return;
}

undefined4 set_controller_request_byte_from_mode_80f6c(uint param_1,byte param_2)

{
  undefined1 uVar1;
  undefined4 uVar2;
  
  uVar2 = 1;
  if (((param_1 & 0xff) < (uint)DAT_00021970) &&
     ((uVar1 = 0x5a, param_2 == 3 || (uVar1 = 0x69, param_2 < 2)))) {
    uVar2 = 0;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe4903u + (uint32_t)(param_1 & 0xff) * 1u)))) = uVar1;
  }
  return uVar2;
}
