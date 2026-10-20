#include "common.h"

undefined4 apply_indexed_channel_timing_profile_85012(uint param_1,uint param_2)

{
  undefined4 *puVar1;
  int iVar2;
  uint uVar3;
  short sVar4;
  undefined1 uVar5;
  int iVar6;
  uint *puVar7;
  
  if ((param_2 & 0xffff) < (uint)(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(PTR_DAT_00022e74))))) {
    sVar4 = (short)(param_1 & 0xff);
    iVar2 = (int)sVar4;
    puVar1 = ((undefined4 *)camry_host_ptr((uint32_t)(PTR_DAT_00022e70 + (param_2 & 0xffff) * 0x14)));
    (*((undefined4 *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x22ef0u + (uint32_t)(iVar2 * 0x1d) * 4u))))))) = *puVar1;
    (*((undefined4 *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x22f00u + (uint32_t)(iVar2 * 0x1d) * 4u))))))) = puVar1[1];
    iVar6 = sVar4 * 0x34;
    if (puVar1[3] == 0) {
      puVar7 = ((uint *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x22f04u + (uint32_t)(iVar2 * 0x1d) * 4u))))));
      uVar3 = puVar1[2] & 0x7f0000 | *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x233e0u + (uint32_t)(iVar6) * 1u)))) & 0xff80fdff | 0x200;
      uVar5 = 0x3c;
    }
    else {
      puVar7 = ((uint *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x22f04u + (uint32_t)(iVar2 * 0x1d) * 4u))))));
      uVar5 = 0x5a;
      uVar3 = *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x233e0u + (uint32_t)(iVar6) * 1u)))) & 0xff80fdff;
    }
    *puVar7 = uVar3;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe5026u + (uint32_t)(param_1 & 0xff) * 1u)))) = uVar5;
    return 0;
  }
  return 2;
}

void request_global_mode_two_and_poll_ten_times_8509a(void)

{
  ushort uVar1;
  uint uVar2;
  
  uVar2 = 1;
  (*((undefined4 *)camry_host_ptr((uint32_t)(PTR_GCTR_00023040)))) = 0x10002;
  uVar1 = 0;
  do {
    if ((uVar2 & 0xf) == 2) {
      return;
    }
    uVar1 = uVar1 + 1;
    uVar2 = (*((uint *)camry_host_ptr((uint32_t)(PTR_GSTS_00023044))));
  } while (uVar1 < 10);
  return;
}

void invalidate_all_can_transmit_route_slots_850c2(void)

{
  uint uVar1;
  uint uVar2;
  
  uVar2 = (uint)DAT_00022e3e;
  for (uVar1 = 0; uVar1 < uVar2; uVar1 = uVar1 + 1 & 0xffff) {
    *(undefined2 *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe502au + (uint32_t)(uVar1 * 2) * 1u)))) = 0xffff;
  }
  return;
}

void invalidate_channel_can_transmit_route_slots_850e0(uint param_1)

{
  uint uVar1;
  int iVar2;
  uint uVar3;
  
  iVar2 = (param_1 & 0xff) * 8;
  uVar3 = (uint)*(ushort *)(((undefined *)camry_host_ptr((uint32_t)(0x22e44u + (uint32_t)(iVar2) * 1u)))) - (uint)DAT_00022e3c & 0xffff;
  uVar1 = (byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x22e48u + (uint32_t)(iVar2) * 1u)))) + uVar3;
  for (; uVar3 < (uVar1 & 0xffff); uVar3 = uVar3 + 1 & 0xffff) {
    *(undefined2 *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe502au + (uint32_t)(uVar3 * 2) * 1u)))) = 0xffff;
  }
  return;
}

uint driver_admit_can_tx(ushort driver_handle,F33CanDriverPdu *pdu)

{
  uint8_t stack_record_28[40];
  byte *pbVar1;
  undefined8 uVar2;
  undefined4 uVar3;
  uint uVar4;
  uint uVar5;
  
  uVar2 = 0x23dfcfebeb800;
  uVar4 = 1;
  pbVar1 = ((void *)camry_host_ptr((uint32_t)(PTR_DAT_00022e38 + (uint)driver_handle * 2)));
  uVar5 = (uint)*pbVar1;
  if (((volatile F33DriverChannelSoftwareState *)camry_host_ptr((uint32_t)(0xfebe5020u + (uint32_t)(uVar5) * (uint32_t)sizeof(F33DriverChannelSoftwareState))))[0] == running_software_state) {
    uVar3 = call_interrupt_guard_and_return_zero_7a2da();
    (*((int32_t *)(stack_record_28 + 0))) = ((uint32_t)(pdu->data));
    (*((uint32_t *)(stack_record_28 + 4))) = pdu->raw_id;
    stack_record_28[8] = pdu->length;
    if (((*((uint32_t *)(stack_record_28 + 4))) >> 0x1e & 1) == 0) {
      if (0xf < stack_record_28[8]) {
        stack_record_28[8] = 0xf;
      }
      uVar4 = submit_classic_can_frame_to_fifo_or_buffer_853aa(uVar5,pbVar1[1],((int32_t *)(stack_record_28)));
    }
    else {
      if (0x40 < stack_record_28[8]) {
        stack_record_28[8] = 0x40;
      }
      uVar4 = submit_can_fd_frame_using_length_tables_8549e(uVar5,pbVar1[1],((int32_t *)(stack_record_28)));
    }
    if (uVar4 == 0) {
      (*((ushort *)camry_host_ptr((uint32_t)(((uint)driver_handle - (uint)(*((volatile uint16_t *)camry_host_ptr((uint32_t)((int)((ulonglong)uVar2 >> 0x20) + -0xfc0)))) & 0xffff)
        * 2 + (int)uVar2 + -0x67d6)))) = pdu->confirmation_handle;
    }
    else if (uVar4 != 2) {
      uVar4 = 1;
    }
    ((void)(uVar3), thunk_pop_and_restore_priority_mask_stack_6a4c4());
  }
  return uVar4;
}

void poll_transmit_completions_for_state_57a8_channels_851b8(void)

{
  undefined8 uVar1;
  uint uVar2;
  uint uVar3;
  
  uVar1 = 0x23dfcfebeb800;
  uVar2 = (uint)DAT_00022e41;
  for (uVar3 = 0; uVar3 < uVar2; uVar3 = uVar3 + 1 & 0xff) {
    if ((*((short *)camry_host_ptr((uint32_t)(uVar3 * 2 + (int)uVar1 + -0x67e0)))) == 0x57a8) {
      process_masked_can_transmit_completions_85714(uVar3,1);
      process_cancelled_can_fifo_and_buffer_routes_8584c(uVar3);
    }
  }
  return;
}

undefined4 cancel_route_transmit_and_complete_saved_can_route_851ee(uint param_1)

{
  ushort controller_route;
  uint32_t puVar1;
  uint32_t puVar2;
  uint uVar3;
  int iVar4;
  undefined4 uVar5;
  
  puVar1 = 0xfebeb800u;
  puVar2 = 0x23dfcu;
  uVar3 = (uint)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(PTR_DAT_00022e38 + (uint32_t)((param_1 & 0xffff) * 2)))));
  if (((volatile F33DriverChannelSoftwareState *)camry_host_ptr((uint32_t)(0xfebe5020u + (uint32_t)(uVar3) * (uint32_t)sizeof(F33DriverChannelSoftwareState))))[0] == running_software_state) {
    iVar4 = cancel_can_fifo_or_buffer_transmit_855f4(uVar3,(*((volatile uint8_t *)camry_host_ptr((uint32_t)((PTR_DAT_00022e38 + (param_1 & 0xffff) * 2) + (uint32_t)(1))))));
    if (iVar4 == 0) {
      controller_route =
           (*((ushort *)camry_host_ptr((uint32_t)(puVar1 + ((param_1 & 0xffff) - (uint)(*((volatile uint16_t *)camry_host_ptr((uint32_t)(puVar2 + -0xfc0)))) & 0xffff) * 2 +
                      -0x67d6))));
      (*((ushort *)camry_host_ptr((uint32_t)(puVar1 + ((param_1 & 0xffff) - (uint)(*((volatile uint16_t *)camry_host_ptr((uint32_t)(puVar2 + -0xfc0)))) & 0xffff) * 2 + -0x67d6)))) =
           0xffff;
      complete_queued_can_tx(controller_route);
    }
    uVar5 = 0;
  }
  else {
    uVar5 = 1;
  }
  return uVar5;
}

void consume_channel_buffer_route_and_complete_can_tx_85240(uint param_1,ushort param_2)

{
  int iVar1;
  ushort controller_route;
  ushort uVar2;
  
  param_2 = param_2 & 0xff;
  iVar1 = (param_1 & 0xff) * 8;
  uVar2 = (ushort)(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x22e4au + (uint32_t)(iVar1) * 1u))));
  if ((uVar2 <= param_2) && (param_2 < ((byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x22e48u + (uint32_t)(iVar1) * 1u)))) + uVar2 & 0xff))) {
    controller_route =
         *(ushort *)
          (((undefined *)camry_host_ptr((uint32_t)(0xfebe502au + (uint32_t)((uint)(ushort)((*(short *)(((undefined *)camry_host_ptr((uint32_t)(0x22e44u + (uint32_t)(iVar1) * 1u)))) + (param_2 - uVar2)) - DAT_00022e3c) * 2) * 1u))));
    *(ushort *)
     (((undefined *)camry_host_ptr((uint32_t)(0xfebe502au + (uint32_t)((uint)(ushort)((*(short *)(((undefined *)camry_host_ptr((uint32_t)(0x22e44u + (uint32_t)(iVar1) * 1u)))) + (param_2 - uVar2)) - DAT_00022e3c) * 2) * 1u)))) =
         0xffff;
    complete_queued_can_tx(controller_route);
  }
  return;
}

undefined4 write_can_fifo_transmit_frame_words_85286(uint param_1,uint param_2,uint param_3,int *param_4)

{
  int *piVar1;
  int iVar2;
  uint uVar3;
  
  param_2 = param_2 & 0xff;
  iVar2 = (int)(short)(param_1 & 0xff);
  if ((param_3 & 0xff) <= (uint)(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x22e9cu + (uint32_t)(param_2 + (param_1 & 0xff) * 2) * 1u))))) {
    piVar1 = ((int *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x22f40u + (uint32_t)(iVar2 * 0x1d) * 4u)))) + param_2 * 0x80)));
    *piVar1 = param_4[1];
    piVar1[1] = (uint)*(byte *)(param_4 + 3) << 0x1c;
    piVar1[2] = param_4[2];
    for (uVar3 = 0; uVar3 < (param_3 & 0xff); uVar3 = uVar3 + 1 & 0xff) {
      piVar1[uVar3 + 3] = (*((int *)camry_host_ptr((uint32_t)(uVar3 * 4 + *param_4))));
    }
    (*((undefined4 *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x22f38u + (uint32_t)(iVar2 * 0x1d) * 4u)))) + param_2 * 4)))) = 0xff;
    return 0;
  }
  return 1;
}

undefined4 write_can_transmit_buffer_and_set_request_852fe(ushort param_1,uint param_2,uint param_3,int *param_4)

{
  int *piVar1;
  int iVar2;
  uint uVar3;
  
  param_2 = param_2 & 0xff;
  param_3 = param_3 & 0xff;
  iVar2 = (int)(short)(param_1 & 0xff);
  if (param_2 < 6) {
    piVar1 = ((int *)camry_host_ptr((uint32_t)((short)(ushort)(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x23454u + (uint32_t)(param_2) * 1u)))) * 0x60 +
                    *(int *)(((undefined *)camry_host_ptr((uint32_t)(0x22f48u + (uint32_t)(iVar2 * 0x74) * 1u)))))));
    *piVar1 = param_4[1];
    piVar1[1] = (uint)*(byte *)(param_4 + 3) << 0x1c;
    piVar1[2] = param_4[2];
    for (uVar3 = 0; uVar3 < param_3; uVar3 = uVar3 + 1 & 0xff) {
      piVar1[uVar3 + 3] = (*((int *)camry_host_ptr((uint32_t)(uVar3 * 4 + *param_4))));
    }
  }
  else {
    if (5 < param_3) {
      return 1;
    }
    piVar1 = ((int *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x22f44u + (uint32_t)(iVar2 * 0x1d) * 4u)))) + param_2 * 0x20)));
    *piVar1 = param_4[1];
    piVar1[1] = (uint)*(byte *)(param_4 + 3) << 0x1c;
    piVar1[2] = param_4[2];
    for (uVar3 = 0; uVar3 < param_3; uVar3 = uVar3 + 1 & 0xff) {
      piVar1[uVar3 + 3] = (*((int *)camry_host_ptr((uint32_t)(uVar3 * 4 + *param_4))));
    }
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x22f3cu + (uint32_t)(iVar2 * 0x1d) * 4u)))) + (uint32_t)(param_2))))) = 1;
  return 0;
}

undefined4 submit_classic_can_frame_to_fifo_or_buffer_853aa(uint param_1,uint param_2,int *param_3)

{
  uint8_t stack_record_54[84];
  undefined1 *puVar1;
  undefined1 *puVar2;
  int iVar3;
  int iVar4;
  uint uVar5;
  undefined1 *puStack_14;
  
  puStack_14 = ((uint8_t *)(stack_record_54));
  param_1 = param_1 & 0xff;
  param_2 = param_2 & 0xff;
  iVar3 = (int)(short)param_1;
  iVar4 = 0;
  if ((param_2 == (byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x22eaeu + (uint32_t)(param_1) * 1u))))) ||
     (iVar4 = 1, param_2 == (byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x22eb1u + (uint32_t)(param_1) * 1u)))))) {
    if (((*((uint *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x22f34u + (uint32_t)(iVar3 * 0x1d) * 4u)))) + iVar4 * 4)))) & 1) == 0) {
      return 2;
    }
    if (((*((uint *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x22f2cu + (uint32_t)(iVar3 * 0x1d) * 4u)))) + iVar4 * 4)))) & 0x11) != 1) {
      return 2;
    }
    (*((uint32_t *)(stack_record_54 + 68))) = param_3[1];
    if (((*((uint32_t *)(stack_record_54 + 68))) & 0x80000000) == 0) {
      (*((uint32_t *)(stack_record_54 + 68))) = (*((uint32_t *)(stack_record_54 + 68))) & 0x7ff;
    }
    else {
      (*((uint32_t *)(stack_record_54 + 68))) = (*((uint32_t *)(stack_record_54 + 68))) & 0x9fffffff;
    }
    uVar5 = 0;
    do {
      puVar1 = ((uint8_t *)(stack_record_54)) + uVar5;
      puVar2 = ((undefined1 *)camry_host_ptr((uint32_t)(*param_3 + uVar5)));
      uVar5 = uVar5 + 1;
      *puVar1 = *puVar2;
    } while (uVar5 < 8);
    stack_record_54[76] = (undefined1)param_3[2];
    (*((uint32_t *)(stack_record_54 + 72))) = 0;
    puStack_14 = ((uint8_t *)(stack_record_54));
    write_can_fifo_transmit_frame_words_85286(param_1,iVar4,2,&puStack_14);
  }
  else {
    if (((*((volatile uint8_t *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x22f30u + (uint32_t)(iVar3 * 0x1d) * 4u)))) + (uint32_t)(param_2))))) & 0x1e) != 0) {
      return 2;
    }
    (*((uint32_t *)(stack_record_54 + 68))) = param_3[1];
    if (((*((uint32_t *)(stack_record_54 + 68))) & 0x80000000) == 0) {
      (*((uint32_t *)(stack_record_54 + 68))) = (*((uint32_t *)(stack_record_54 + 68))) & 0x7ff;
    }
    else {
      (*((uint32_t *)(stack_record_54 + 68))) = (*((uint32_t *)(stack_record_54 + 68))) & 0x9fffffff;
    }
    uVar5 = 0;
    do {
      puVar1 = ((uint8_t *)(stack_record_54)) + uVar5;
      puVar2 = ((undefined1 *)camry_host_ptr((uint32_t)(*param_3 + uVar5)));
      uVar5 = uVar5 + 1;
      *puVar1 = *puVar2;
    } while (uVar5 < 8);
    stack_record_54[76] = (undefined1)param_3[2];
    (*((uint32_t *)(stack_record_54 + 72))) = 0;
    write_can_transmit_buffer_and_set_request_852fe(param_1,param_2,2,&puStack_14);
  }
  return 0;
}

undefined4 submit_can_fd_frame_using_length_tables_8549e(uint param_1,uint param_2,int *param_3)

{
  uint8_t stack_record_54[84];
  int iVar1;
  undefined1 uVar2;
  byte bVar3;
  int iVar4;
  uint uVar5;
  short sVar6;
  undefined4 uVar7;
  uint uVar8;
  uint uVar9;
  undefined1 *puStack_14;
  
  param_1 = param_1 & 0xff;
  param_2 = param_2 & 0xff;
  sVar6 = (short)param_1;
  iVar1 = (int)sVar6;
  uVar7 = 1;
  uVar8 = (uint)(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe5026u + (uint32_t)(param_1) * 1u))));
  if (((int)uVar8 >> 4) + (uVar8 & 0xf) == 0xf) {
    uVar7 = 2;
    iVar4 = 0;
    if ((param_2 == (byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x22eaeu + (uint32_t)(param_1) * 1u))))) ||
       (iVar4 = 1, param_2 == (byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x22eb1u + (uint32_t)(param_1) * 1u)))))) {
      if ((((*((uint *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x22f34u + (uint32_t)(iVar1 * 0x1d) * 4u)))) + iVar4 * 4)))) & 1) != 0) &&
         (((*((uint *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x22f2cu + (uint32_t)(iVar1 * 0x1d) * 4u)))) + iVar4 * 4)))) & 0x11) == 1)) {
        uVar9 = param_3[1];
        if ((uVar9 & 0x80000000) == 0) {
          uVar9 = uVar9 & 0x7ff;
        }
        else {
          uVar9 = uVar9 & 0x9fffffff;
        }
        uVar2 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x2345au + (uint32_t)(*(byte *)(param_3 + 2)) * 1u))));
        bVar3 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x2349bu + (uint32_t)(*(byte *)(param_3 + 2)) * 1u))));
        for (uVar5 = 0; uVar5 < bVar3; uVar5 = uVar5 + 1 & 0xff) {
          ((uint8_t *)(stack_record_54))[uVar5] = (*((undefined1 *)camry_host_ptr((uint32_t)(*param_3 + uVar5))));
        }
        if (uVar8 == 0x3c) {
          (*((uint32_t *)(stack_record_54 + 72))) = 6;
        }
        else {
          (*((uint32_t *)(stack_record_54 + 72))) = 4;
        }
        (*((uint32_t *)(stack_record_54 + 72))) = *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x233e8u + (uint32_t)(sVar6 * 0x34) * 1u)))) | (*((uint32_t *)(stack_record_54 + 72)));
        puStack_14 = ((uint8_t *)(stack_record_54));
        (*((uint32_t *)(stack_record_54 + 68))) = uVar9;
        stack_record_54[76] = uVar2;
        uVar7 = write_can_fifo_transmit_frame_words_85286(param_1,iVar4,(int)(uint)bVar3 >> 2,&puStack_14);
      }
    }
    else if (((*((volatile uint8_t *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x22f30u + (uint32_t)(iVar1 * 0x1d) * 4u)))) + (uint32_t)(param_2))))) & 0x1e) == 0) {
      uVar9 = param_3[1];
      if ((uVar9 & 0x80000000) == 0) {
        uVar9 = uVar9 & 0x7ff;
      }
      else {
        uVar9 = uVar9 & 0x9fffffff;
      }
      uVar2 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x2345au + (uint32_t)(*(byte *)(param_3 + 2)) * 1u))));
      bVar3 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x2349bu + (uint32_t)(*(byte *)(param_3 + 2)) * 1u))));
      for (uVar5 = 0; uVar5 < bVar3; uVar5 = uVar5 + 1 & 0xff) {
        ((uint8_t *)(stack_record_54))[uVar5] = (*((undefined1 *)camry_host_ptr((uint32_t)(*param_3 + uVar5))));
      }
      if (uVar8 == 0x3c) {
        (*((uint32_t *)(stack_record_54 + 72))) = 6;
      }
      else {
        (*((uint32_t *)(stack_record_54 + 72))) = 4;
      }
      (*((uint32_t *)(stack_record_54 + 72))) = *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x233e4u + (uint32_t)(sVar6 * 0x34) * 1u)))) | (*((uint32_t *)(stack_record_54 + 72)));
      puStack_14 = ((uint8_t *)(stack_record_54));
      (*((uint32_t *)(stack_record_54 + 68))) = uVar9;
      stack_record_54[76] = uVar2;
      uVar7 = write_can_transmit_buffer_and_set_request_852fe(param_1,param_2,(int)(uint)bVar3 >> 2,&puStack_14);
    }
  }
  return uVar7;
}

undefined4 cancel_can_fifo_or_buffer_transmit_855f4(uint param_1,uint param_2)

{
  int iVar1;
  short sVar2;
  
  param_1 = param_1 & 0xff;
  param_2 = param_2 & 0xff;
  sVar2 = (short)param_1;
  iVar1 = (int)sVar2;
  if (param_2 == (byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x22eaeu + (uint32_t)(param_1) * 1u))))) {
    (*((uint *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x22f34u + (uint32_t)(iVar1 * 0x1d) * 4u))))))) = (uint)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x233b8u + (uint32_t)(sVar2 * 0xd) * 4u)))) & 0xfffffffe
    ;
    if (((*((uint *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x22f2cu + (uint32_t)(iVar1 * 0x1d) * 4u))))))) & 0x11) != 1) {
      return 2;
    }
    (*((volatile uint32_t *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x22f34u + (uint32_t)(iVar1 * 0x1d) * 4u)))))))) = ((uint32_t)((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x233b8u + (uint32_t)(sVar2 * 0xd) * 4u)))))));
  }
  else if (param_2 == (byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x22eb1u + (uint32_t)(param_1) * 1u))))) {
    (*((uint *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x22f34u + (uint32_t)(iVar1 * 0x1d) * 4u)))) + 4)))) =
         (uint)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x233bcu + (uint32_t)(sVar2 * 0xd) * 4u)))) & 0xfffffffe;
    if (((*((uint *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x22f2cu + (uint32_t)(iVar1 * 0x1d) * 4u)))) + 4)))) & 0x11) != 1) {
      return 2;
    }
    (*((volatile uint32_t *)camry_host_ptr((uint32_t)(((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x22f34u + (uint32_t)(iVar1 * 0x1d) * 4u)))) + 4))))) = ((uint32_t)((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x233bcu + (uint32_t)(sVar2 * 0xd) * 4u)))))));
  }
  else {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x22f3cu + (uint32_t)(iVar1 * 0x1d) * 4u)))) + (uint32_t)(param_2))))) = 2;
    if (((*((volatile uint8_t *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x22f30u + (uint32_t)(iVar1 * 0x1d) * 4u)))) + (uint32_t)(param_2))))) & 0x1e) != 2) {
      return 2;
    }
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x22f30u + (uint32_t)(iVar1 * 0x1d) * 4u)))) + (uint32_t)(param_2))))) = 0;
  }
  return 0;
}

void request_cancellation_for_configured_channel_transmits_8569a(uint param_1)

{
  int iVar1;
  ushort uVar2;
  ushort uVar3;
  byte bVar4;
  ushort uVar5;
  short sVar6;
  uint uVar7;
  
  param_1 = param_1 & 0xff;
  sVar6 = (short)param_1;
  iVar1 = (int)sVar6;
  uVar2 = *(ushort *)(((undefined *)camry_host_ptr((uint32_t)(0x22ebeu + (uint32_t)(param_1 * 4) * 1u))));
  uVar3 = *(ushort *)(((undefined *)camry_host_ptr((uint32_t)(0x22ebcu + (uint32_t)(param_1 * 4) * 1u))));
  (*((uint *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x22f34u + (uint32_t)(iVar1 * 0x1d) * 4u))))))) = (uint)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x233b8u + (uint32_t)(sVar6 * 0xd) * 4u)))) & 0xfffffffe;
  (*((uint *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x22f34u + (uint32_t)(iVar1 * 0x1d) * 4u)))) + 4)))) =
       (uint)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x233bcu + (uint32_t)(sVar6 * 0xd) * 4u)))) & 0xfffffffe;
  uVar5 = *(ushort *)(((undefined *)camry_host_ptr((uint32_t)(0x22e94u + (uint32_t)(param_1 * 2) * 1u))));
  bVar4 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x22ea8u + (uint32_t)(param_1) * 1u))));
  for (uVar7 = 0; uVar7 < bVar4; uVar7 = uVar7 + 1 & 0xff) {
    if ((1 << (uVar7 & 0xf) & 0xffffU & (uint)((uVar2 | uVar3) & uVar5)) != 0) {
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x22f3cu + (uint32_t)(iVar1 * 0x1d) * 4u)))) + (uint32_t)(uVar7))))) = 2;
    }
  }
  return;
}

undefined4 process_masked_can_transmit_completions_85714(uint param_1,char param_2)

{
  int iVar1;
  ushort uVar2;
  ushort uVar3;
  uint32_t puVar4;
  uint uVar5;
  undefined4 uVar6;
  uint uVar7;
  short sVar8;
  
  puVar4 = 0x23dfcu;
  param_1 = param_1 & 0xff;
  sVar8 = (short)param_1;
  iVar1 = (int)sVar8;
  uVar6 = 1;
  if (param_2 == '\0') {
    uVar3 = *(ushort *)(((undefined *)camry_host_ptr((uint32_t)(0x22ebcu + (uint32_t)(param_1 * 4) * 1u))));
  }
  else {
    uVar3 = *(ushort *)(((undefined *)camry_host_ptr((uint32_t)(0x22ebeu + (uint32_t)(param_1 * 4) * 1u))));
  }
  uVar5 = (uint)(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x22ea8u + (uint32_t)(param_1) * 1u))));
  if ((((byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x22eaeu + (uint32_t)(param_1) * 1u)))) < uVar5) &&
      ((1 << ((byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x22eaeu + (uint32_t)(param_1) * 1u)))) & 0x1f) & 0xffffU & (uint)uVar3) != 0)) &&
     (((*((uint *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x22f2cu + (uint32_t)(iVar1 * 0x1d) * 4u))))))) >> 4 & 1) != 0)) {
    uVar6 = 0;
    (*((undefined4 *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x22f2cu + (uint32_t)(iVar1 * 0x1d) * 4u))))))) = 1;
    (*((volatile uint32_t *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x22f34u + (uint32_t)(iVar1 * 0x1d) * 4u)))))))) = (*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x233b8u + (uint32_t)(sVar8 * 0xd) * 4u))));
    puVar4 = 0x23dfcu;
    consume_channel_buffer_route_and_complete_can_tx_85240(param_1,(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x22eaeu + (uint32_t)(param_1) * 1u)))));
  }
  if ((((byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(param_1 - 0xf4b))))) < uVar5) &&
      ((1 << ((byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(param_1 - 0xf4b))))) & 0x1f) & 0xffffU & (uint)uVar3) != 0)) &&
     (((*((uint *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x22f2cu + (uint32_t)(iVar1 * 0x1d) * 4u)))) + 4)))) >> 4 & 1) != 0)) {
    uVar6 = 0;
    (*((undefined4 *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x22f2cu + (uint32_t)(iVar1 * 0x1d) * 4u)))) + 4)))) = 1;
    (*((volatile uint32_t *)camry_host_ptr((uint32_t)(((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x22f34u + (uint32_t)(iVar1 * 0x1d) * 4u)))) + 4))))) = (*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x233bcu + (uint32_t)(sVar8 * 0xd) * 4u))));
    consume_channel_buffer_route_and_complete_can_tx_85240(param_1,(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(param_1 - 0xf4b))))));
  }
  uVar2 = (*((ushort *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x22ee8u + (uint32_t)(iVar1 * 0x1d) * 4u)))))));
  if ((uVar3 & uVar2) != 0) {
    uVar6 = 0;
    for (uVar7 = 0; uVar7 < uVar5; uVar7 = uVar7 + 1 & 0xff) {
      if ((1 << (uVar7 & 0xf) & 0xffffU & (uint)(uVar3 & uVar2)) != 0) {
        (*((volatile uint8_t *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x22f30u + (uint32_t)(iVar1 * 0x1d) * 4u)))) + (uint32_t)(uVar7))))) = 0;
        consume_channel_buffer_route_and_complete_can_tx_85240(param_1,uVar7);
      }
    }
  }
  return uVar6;
}

void service_channel_transmit_completions_and_sync_85800(ushort param_1)

{
  int iVar1;
  
  param_1 = param_1 & 0xff;
  if (((*((uint *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x22ef8u + (uint32_t)((short)param_1 * 0x1d) * 4u))))))) & 7) == 0) {
    iVar1 = process_masked_can_transmit_completions_85714(param_1,0);
    if (iVar1 != 0) {
      restore_fifo_status_and_check_channel_registers_83b14(param_1);
    }
  }
  else {
    clear_channel_tx_fifo_status_and_control_83a34((uint)(byte)param_1);
  }
  synchronize_memory_accesses_85938();
  return;
}

void service_channel_one_transmit_completions_and_sync_8583e(void)

{
  service_channel_transmit_completions_and_sync_85800(1);
  return;
}

void process_cancelled_can_fifo_and_buffer_routes_8584c(uint param_1)

{
  int iVar1;
  ushort uVar2;
  ushort uVar3;
  uint32_t puVar4;
  uint uVar5;
  uint uVar6;
  short sVar7;
  
  puVar4 = 0x23dfcu;
  param_1 = param_1 & 0xff;
  sVar7 = (short)param_1;
  iVar1 = (int)sVar7;
  uVar5 = (uint)(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x22ea8u + (uint32_t)(param_1) * 1u))));
  uVar3 = *(ushort *)(((undefined *)camry_host_ptr((uint32_t)(0x22ebeu + (uint32_t)(param_1 * 4) * 1u)))) | *(ushort *)(((undefined *)camry_host_ptr((uint32_t)(0x22ebcu + (uint32_t)(param_1 * 4) * 1u))));
  if (((((byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x22eaeu + (uint32_t)(param_1) * 1u)))) < uVar5) &&
       ((1 << ((byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x22eaeu + (uint32_t)(param_1) * 1u)))) & 0x1f) & 0xffffU & (uint)uVar3) != 0)) &&
      (((*((uint *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x22f34u + (uint32_t)(iVar1 * 0x1d) * 4u))))))) & 1) == 0)) &&
     (((*((uint *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x22f2cu + (uint32_t)(iVar1 * 0x1d) * 4u))))))) & 0x11) == 1)) {
    (*((volatile uint32_t *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x22f34u + (uint32_t)(iVar1 * 0x1d) * 4u)))))))) = (*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x233b8u + (uint32_t)(sVar7 * 0xd) * 4u))));
    puVar4 = 0x23dfcu;
    consume_channel_buffer_route_and_complete_can_tx_85240(param_1,(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x22eaeu + (uint32_t)(param_1) * 1u)))));
  }
  if ((((byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(param_1 - 0xf4b))))) < uVar5) &&
      ((1 << ((byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(param_1 - 0xf4b))))) & 0x1f) & 0xffffU & (uint)uVar3) != 0)) &&
     ((((*((uint *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x22f34u + (uint32_t)(iVar1 * 0x1d) * 4u)))) + 4)))) & 1) == 0 &&
      (((*((uint *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x22f2cu + (uint32_t)(iVar1 * 0x1d) * 4u)))) + 4)))) & 0x11) == 1)))) {
    (*((volatile uint32_t *)camry_host_ptr((uint32_t)(((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x22f34u + (uint32_t)(iVar1 * 0x1d) * 4u)))) + 4))))) = (*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x233bcu + (uint32_t)(sVar7 * 0xd) * 4u))));
    consume_channel_buffer_route_and_complete_can_tx_85240(param_1,(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(param_1 - 0xf4b))))));
  }
  uVar2 = (*((ushort *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x22eecu + (uint32_t)(iVar1 * 0x1d) * 4u)))))));
  if ((uVar3 & uVar2) != 0) {
    for (uVar6 = 0; uVar6 < uVar5; uVar6 = uVar6 + 1 & 0xff) {
      if ((1 << (uVar6 & 0xf) & 0xffffU & (uint)(uVar3 & uVar2)) != 0) {
        (*((volatile uint8_t *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x22f30u + (uint32_t)(iVar1 * 0x1d) * 4u)))) + (uint32_t)(uVar6))))) = 0;
        consume_channel_buffer_route_and_complete_can_tx_85240(param_1,uVar6);
      }
    }
  }
  return;
}

void synchronize_memory_accesses_85938(void)

{
  __synchronize();
  return;
}

undefined4 initialize_aes128_counter_context_with_fixed_iv_85940(undefined4 param_1,char param_2,undefined4 param_3)

{
  undefined4 uVar1;
  
  if (param_2 == '\x10') {
    uVar1 = initialize_aes128_counter_context_and_iv_87b74(param_1,0x10,((undefined *)camry_host_ptr(0x234dcu)),0x10,param_3);
  }
  else {
    uVar1 = 0xff;
  }
  return uVar1;
}

undefined4 xor_fixed_input_with_aes128_counter_block_85964(undefined4 param_1,undefined4 param_2)

{
  return aes128_counter_xor_block_and_increment_big_endian_counter_87c40(((undefined *)camry_host_ptr(0x234dcu)), ((uint *)camry_host_ptr((uint32_t)(param_1))), 0x10, param_2);
}

undefined4 rekey_initialized_aes128_counter_context_8597c(undefined4 param_1,char param_2,int param_3)

{
  undefined4 uVar1;
  
  uVar1 = 0xff;
  if (((*((char *)camry_host_ptr((uint32_t)(param_3 + 0xc0)))) == '\x01') && (param_2 == '\x10')) {
    uVar1 = initialize_aes128_counter_context_and_iv_87b74(param_1, 0x10, ((undefined4 *)camry_host_ptr((uint32_t)(param_3 + 0xd4))), 0x10, param_3);
  }
  return uVar1;
}

void clear_aes128_counter_context_228_bytes_859a8(undefined4 *param_1)

{
  int iVar1;
  undefined4 *puVar2;
  
  *param_1 = 0;
  param_1[1] = 0;
  param_1[2] = 0;
  param_1[3] = 0;
  param_1[4] = 0;
  param_1[5] = 0;
  param_1[6] = 0;
  param_1[7] = 0;
  param_1[8] = 0;
  param_1[9] = 0;
  param_1[10] = 0;
  param_1[0xb] = 0;
  param_1[0xc] = 0;
  param_1[0xd] = 0;
  param_1[0xe] = 0;
  param_1[0xf] = 0;
  param_1[0x10] = 0;
  param_1[0x11] = 0;
  param_1[0x12] = 0;
  param_1[0x13] = 0;
  param_1[0x14] = 0;
  param_1[0x15] = 0;
  param_1[0x16] = 0;
  param_1[0x17] = 0;
  param_1[0x18] = 0;
  param_1[0x19] = 0;
  param_1[0x1a] = 0;
  param_1[0x1b] = 0;
  param_1[0x1c] = 0;
  param_1[0x1d] = 0;
  param_1[0x1e] = 0;
  param_1[0x1f] = 0;
  param_1[0x20] = 0;
  param_1[0x21] = 0;
  param_1[0x22] = 0;
  param_1[0x23] = 0;
  param_1[0x24] = 0;
  param_1[0x25] = 0;
  param_1[0x26] = 0;
  param_1[0x27] = 0;
  param_1[0x28] = 0;
  param_1[0x29] = 0;
  param_1[0x2a] = 0;
  param_1[0x2b] = 0;
  param_1[0x2c] = 0;
  param_1[0x2d] = 0;
  param_1[0x2e] = 0;
  param_1[0x2f] = 0;
  puVar2 = param_1 + 0x30;
  for (iVar1 = 0x24; iVar1 + -0x20 < 0 == (iVar1 < 0 && -1 < iVar1 + -0x20); iVar1 = iVar1 + -0x20)
  {
    *puVar2 = 0;
    puVar2[1] = 0;
    puVar2[2] = 0;
    puVar2[3] = 0;
    puVar2[4] = 0;
    puVar2[5] = 0;
    puVar2[6] = 0;
    puVar2[7] = 0;
    puVar2 = puVar2 + 8;
  }
  for (; iVar1 + -0x10 < 0 == (iVar1 < 0 && -1 < iVar1 + -0x10); iVar1 = iVar1 + -0x10) {
    *puVar2 = 0;
    puVar2[1] = 0;
    puVar2[2] = 0;
    puVar2[3] = 0;
    puVar2 = puVar2 + 4;
  }
  for (; 0 < iVar1; iVar1 = iVar1 + -4) {
    *puVar2 = 0;
    puVar2 = puVar2 + 1;
  }
  *(undefined1 *)(param_1 + 0x30) = 0;
  return;
}

void aes128_encrypt_context_block_in_place_85a5c(uint *param_1)

{
  uint uVar1;
  uint uVar2;
  uint uVar3;
  uint uVar4;
  uint uVar5;
  uint uVar6;
  uint uVar7;
  uint uVar8;
  
  uVar1 = param_1[0x2c];
  uVar7 = param_1[0x2d];
  uVar4 = param_1[0x2e];
  uVar3 = param_1[0x2f];
  param_1[0x2d] = uVar7 ^ param_1[1];
  param_1[0x2c] = uVar1 ^ *param_1;
  param_1[0x2e] = uVar4 ^ param_1[2];
  param_1[0x2f] = uVar3 ^ param_1[3];
  uVar2 = param_1[4] ^
          *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x24100u + (uint32_t)((uint)(*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 0xbf)))) * 4) * 1u)))) ^
          *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x23d00u + (uint32_t)((uint)(*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 0xba)))) * 4) * 1u)))) ^
          *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x23900u + (uint32_t)((uint)(*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 0xb5)))) * 4) * 1u)))) ^
          *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x23500u + (uint32_t)(((uVar1 ^ *param_1) & 0xff) * 4) * 1u))));
  uVar1 = param_1[5] ^
          *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x24100u + (uint32_t)((uint)(*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 0xb3)))) * 4) * 1u)))) ^
          *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x23d00u + (uint32_t)((uint)(*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 0xbe)))) * 4) * 1u)))) ^
          *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x23900u + (uint32_t)((uint)(*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 0xb9)))) * 4) * 1u)))) ^
          *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x23500u + (uint32_t)(((uVar7 ^ param_1[1]) & 0xff) * 4) * 1u))));
  uVar5 = param_1[6] ^
          *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x24100u + (uint32_t)((uint)(*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 0xb7)))) * 4) * 1u)))) ^
          *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x23d00u + (uint32_t)((uint)(*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 0xb2)))) * 4) * 1u)))) ^
          *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x23900u + (uint32_t)((uint)(*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 0xbd)))) * 4) * 1u)))) ^
          *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x23500u + (uint32_t)(((uVar4 ^ param_1[2]) & 0xff) * 4) * 1u))));
  uVar7 = param_1[7] ^
          *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x24100u + (uint32_t)((uint)(*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 0xbb)))) * 4) * 1u)))) ^
          *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x23d00u + (uint32_t)((uint)(*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 0xb6)))) * 4) * 1u)))) ^
          *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x23900u + (uint32_t)((uint)(*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 0xb1)))) * 4) * 1u)))) ^
          *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x23500u + (uint32_t)(((uVar3 ^ param_1[3]) & 0xff) * 4) * 1u))));
  uVar4 = param_1[8] ^
          *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x24100u + (uint32_t)((uVar7 >> 0x18) * 4) * 1u)))) ^
          *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x23d00u + (uint32_t)((uVar5 >> 0x10 & 0xff) * 4) * 1u)))) ^
          *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x23900u + (uint32_t)((uVar1 >> 8 & 0xff) * 4) * 1u)))) ^
          *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x23500u + (uint32_t)((uVar2 & 0xff) * 4) * 1u))));
  param_1[0x2c] = uVar4;
  uVar3 = param_1[9] ^
          *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x24100u + (uint32_t)((uVar2 >> 0x18) * 4) * 1u)))) ^
          *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x23d00u + (uint32_t)((uVar7 >> 0x10 & 0xff) * 4) * 1u)))) ^
          *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x23900u + (uint32_t)((uVar5 >> 8 & 0xff) * 4) * 1u)))) ^
          *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x23500u + (uint32_t)((uVar1 & 0xff) * 4) * 1u))));
  param_1[0x2d] = uVar3;
  uVar6 = param_1[10] ^
          *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x24100u + (uint32_t)((uVar1 >> 0x18) * 4) * 1u)))) ^
          *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x23d00u + (uint32_t)((uVar2 >> 0x10 & 0xff) * 4) * 1u)))) ^
          *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x23900u + (uint32_t)((uVar7 >> 8 & 0xff) * 4) * 1u)))) ^
          *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x23500u + (uint32_t)((uVar5 & 0xff) * 4) * 1u))));
  param_1[0x2e] = uVar6;
  uVar7 = param_1[0xb] ^
          *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x24100u + (uint32_t)((uVar5 >> 0x18) * 4) * 1u)))) ^
          *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x23d00u + (uint32_t)((uVar1 >> 0x10 & 0xff) * 4) * 1u)))) ^
          *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x23900u + (uint32_t)((uVar2 >> 8 & 0xff) * 4) * 1u)))) ^
          *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x23500u + (uint32_t)((uVar7 & 0xff) * 4) * 1u))));
  param_1[0x2f] = uVar7;
  uVar2 = param_1[0xc] ^
          *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x24100u + (uint32_t)((uint)(*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 0xbf)))) * 4) * 1u)))) ^
          *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x23d00u + (uint32_t)((uint)(*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 0xba)))) * 4) * 1u)))) ^
          *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x23900u + (uint32_t)((uint)(*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 0xb5)))) * 4) * 1u)))) ^
          *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x23500u + (uint32_t)((uVar4 & 0xff) * 4) * 1u))));
  uVar1 = param_1[0xd] ^
          *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x24100u + (uint32_t)((uint)(*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 0xb3)))) * 4) * 1u)))) ^
          *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x23d00u + (uint32_t)((uint)(*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 0xbe)))) * 4) * 1u)))) ^
          *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x23900u + (uint32_t)((uint)(*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 0xb9)))) * 4) * 1u)))) ^
          *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x23500u + (uint32_t)((uVar3 & 0xff) * 4) * 1u))));
  uVar5 = param_1[0xe] ^
          *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x24100u + (uint32_t)((uint)(*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 0xb7)))) * 4) * 1u)))) ^
          *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x23d00u + (uint32_t)((uint)(*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 0xb2)))) * 4) * 1u)))) ^
          *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x23900u + (uint32_t)((uint)(*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 0xbd)))) * 4) * 1u)))) ^
          *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x23500u + (uint32_t)((uVar6 & 0xff) * 4) * 1u))));
  uVar7 = param_1[0xf] ^
          *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x24100u + (uint32_t)((uint)(*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 0xbb)))) * 4) * 1u)))) ^
          *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x23d00u + (uint32_t)((uint)(*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 0xb6)))) * 4) * 1u)))) ^
          *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x23900u + (uint32_t)((uint)(*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 0xb1)))) * 4) * 1u)))) ^
          *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x23500u + (uint32_t)((uVar7 & 0xff) * 4) * 1u))));
  uVar4 = param_1[0x10] ^
          *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x24100u + (uint32_t)((uVar7 >> 0x18) * 4) * 1u)))) ^
          *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x23d00u + (uint32_t)((uVar5 >> 0x10 & 0xff) * 4) * 1u)))) ^
          *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x23900u + (uint32_t)((uVar1 >> 8 & 0xff) * 4) * 1u)))) ^
          *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x23500u + (uint32_t)((uVar2 & 0xff) * 4) * 1u))));
  param_1[0x2c] = uVar4;
  uVar3 = param_1[0x11] ^
          *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x24100u + (uint32_t)((uVar2 >> 0x18) * 4) * 1u)))) ^
          *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x23d00u + (uint32_t)((uVar7 >> 0x10 & 0xff) * 4) * 1u)))) ^
          *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x23900u + (uint32_t)((uVar5 >> 8 & 0xff) * 4) * 1u)))) ^
          *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x23500u + (uint32_t)((uVar1 & 0xff) * 4) * 1u))));
  param_1[0x2d] = uVar3;
  uVar6 = param_1[0x12] ^
          *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x24100u + (uint32_t)((uVar1 >> 0x18) * 4) * 1u)))) ^
          *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x23d00u + (uint32_t)((uVar2 >> 0x10 & 0xff) * 4) * 1u)))) ^
          *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x23900u + (uint32_t)((uVar7 >> 8 & 0xff) * 4) * 1u)))) ^
          *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x23500u + (uint32_t)((uVar5 & 0xff) * 4) * 1u))));
  param_1[0x2e] = uVar6;
  uVar7 = param_1[0x13] ^
          *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x24100u + (uint32_t)((uVar5 >> 0x18) * 4) * 1u)))) ^
          *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x23d00u + (uint32_t)((uVar1 >> 0x10 & 0xff) * 4) * 1u)))) ^
          *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x23900u + (uint32_t)((uVar2 >> 8 & 0xff) * 4) * 1u)))) ^
          *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x23500u + (uint32_t)((uVar7 & 0xff) * 4) * 1u))));
  param_1[0x2f] = uVar7;
  uVar2 = param_1[0x14] ^
          *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x24100u + (uint32_t)((uint)(*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 0xbf)))) * 4) * 1u)))) ^
          *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x23d00u + (uint32_t)((uint)(*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 0xba)))) * 4) * 1u)))) ^
          *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x23900u + (uint32_t)((uint)(*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 0xb5)))) * 4) * 1u)))) ^
          *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x23500u + (uint32_t)((uVar4 & 0xff) * 4) * 1u))));
  uVar1 = param_1[0x15] ^
          *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x24100u + (uint32_t)((uint)(*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 0xb3)))) * 4) * 1u)))) ^
          *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x23d00u + (uint32_t)((uint)(*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 0xbe)))) * 4) * 1u)))) ^
          *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x23900u + (uint32_t)((uint)(*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 0xb9)))) * 4) * 1u)))) ^
          *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x23500u + (uint32_t)((uVar3 & 0xff) * 4) * 1u))));
  uVar5 = param_1[0x16] ^
          *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x24100u + (uint32_t)((uint)(*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 0xb7)))) * 4) * 1u)))) ^
          *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x23d00u + (uint32_t)((uint)(*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 0xb2)))) * 4) * 1u)))) ^
          *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x23900u + (uint32_t)((uint)(*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 0xbd)))) * 4) * 1u)))) ^
          *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x23500u + (uint32_t)((uVar6 & 0xff) * 4) * 1u))));
  uVar7 = param_1[0x17] ^
          *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x24100u + (uint32_t)((uint)(*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 0xbb)))) * 4) * 1u)))) ^
          *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x23d00u + (uint32_t)((uint)(*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 0xb6)))) * 4) * 1u)))) ^
          *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x23900u + (uint32_t)((uint)(*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 0xb1)))) * 4) * 1u)))) ^
          *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x23500u + (uint32_t)((uVar7 & 0xff) * 4) * 1u))));
  uVar4 = param_1[0x18] ^
          *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x24100u + (uint32_t)((uVar7 >> 0x18) * 4) * 1u)))) ^
          *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x23d00u + (uint32_t)((uVar5 >> 0x10 & 0xff) * 4) * 1u)))) ^
          *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x23900u + (uint32_t)((uVar1 >> 8 & 0xff) * 4) * 1u)))) ^
          *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x23500u + (uint32_t)((uVar2 & 0xff) * 4) * 1u))));
  param_1[0x2c] = uVar4;
  uVar3 = param_1[0x19] ^
          *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x24100u + (uint32_t)((uVar2 >> 0x18) * 4) * 1u)))) ^
          *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x23d00u + (uint32_t)((uVar7 >> 0x10 & 0xff) * 4) * 1u)))) ^
          *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x23900u + (uint32_t)((uVar5 >> 8 & 0xff) * 4) * 1u)))) ^
          *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x23500u + (uint32_t)((uVar1 & 0xff) * 4) * 1u))));
  param_1[0x2d] = uVar3;
  uVar6 = param_1[0x1a] ^
          *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x24100u + (uint32_t)((uVar1 >> 0x18) * 4) * 1u)))) ^
          *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x23d00u + (uint32_t)((uVar2 >> 0x10 & 0xff) * 4) * 1u)))) ^
          *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x23900u + (uint32_t)((uVar7 >> 8 & 0xff) * 4) * 1u)))) ^
          *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x23500u + (uint32_t)((uVar5 & 0xff) * 4) * 1u))));
  param_1[0x2e] = uVar6;
  uVar7 = param_1[0x1b] ^
          *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x24100u + (uint32_t)((uVar5 >> 0x18) * 4) * 1u)))) ^
          *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x23d00u + (uint32_t)((uVar1 >> 0x10 & 0xff) * 4) * 1u)))) ^
          *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x23900u + (uint32_t)((uVar2 >> 8 & 0xff) * 4) * 1u)))) ^
          *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x23500u + (uint32_t)((uVar7 & 0xff) * 4) * 1u))));
  param_1[0x2f] = uVar7;
  uVar2 = param_1[0x1c] ^
          *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x24100u + (uint32_t)((uint)(*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 0xbf)))) * 4) * 1u)))) ^
          *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x23d00u + (uint32_t)((uint)(*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 0xba)))) * 4) * 1u)))) ^
          *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x23900u + (uint32_t)((uint)(*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 0xb5)))) * 4) * 1u)))) ^
          *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x23500u + (uint32_t)((uVar4 & 0xff) * 4) * 1u))));
  uVar1 = param_1[0x1d] ^
          *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x24100u + (uint32_t)((uint)(*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 0xb3)))) * 4) * 1u)))) ^
          *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x23d00u + (uint32_t)((uint)(*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 0xbe)))) * 4) * 1u)))) ^
          *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x23900u + (uint32_t)((uint)(*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 0xb9)))) * 4) * 1u)))) ^
          *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x23500u + (uint32_t)((uVar3 & 0xff) * 4) * 1u))));
  uVar5 = param_1[0x1e] ^
          *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x24100u + (uint32_t)((uint)(*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 0xb7)))) * 4) * 1u)))) ^
          *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x23d00u + (uint32_t)((uint)(*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 0xb2)))) * 4) * 1u)))) ^
          *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x23900u + (uint32_t)((uint)(*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 0xbd)))) * 4) * 1u)))) ^
          *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x23500u + (uint32_t)((uVar6 & 0xff) * 4) * 1u))));
  uVar7 = param_1[0x1f] ^
          *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x24100u + (uint32_t)((uint)(*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 0xbb)))) * 4) * 1u)))) ^
          *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x23d00u + (uint32_t)((uint)(*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 0xb6)))) * 4) * 1u)))) ^
          *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x23900u + (uint32_t)((uint)(*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 0xb1)))) * 4) * 1u)))) ^
          *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x23500u + (uint32_t)((uVar7 & 0xff) * 4) * 1u))));
  uVar4 = param_1[0x20] ^
          *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x24100u + (uint32_t)((uVar7 >> 0x18) * 4) * 1u)))) ^
          *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x23d00u + (uint32_t)((uVar5 >> 0x10 & 0xff) * 4) * 1u)))) ^
          *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x23900u + (uint32_t)((uVar1 >> 8 & 0xff) * 4) * 1u)))) ^
          *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x23500u + (uint32_t)((uVar2 & 0xff) * 4) * 1u))));
  param_1[0x2c] = uVar4;
  uVar3 = param_1[0x21] ^
          *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x24100u + (uint32_t)((uVar2 >> 0x18) * 4) * 1u)))) ^
          *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x23d00u + (uint32_t)((uVar7 >> 0x10 & 0xff) * 4) * 1u)))) ^
          *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x23900u + (uint32_t)((uVar5 >> 8 & 0xff) * 4) * 1u)))) ^
          *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x23500u + (uint32_t)((uVar1 & 0xff) * 4) * 1u))));
  param_1[0x2d] = uVar3;
  uVar6 = param_1[0x22] ^
          *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x24100u + (uint32_t)((uVar1 >> 0x18) * 4) * 1u)))) ^
          *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x23d00u + (uint32_t)((uVar2 >> 0x10 & 0xff) * 4) * 1u)))) ^
          *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x23900u + (uint32_t)((uVar7 >> 8 & 0xff) * 4) * 1u)))) ^
          *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x23500u + (uint32_t)((uVar5 & 0xff) * 4) * 1u))));
  param_1[0x2e] = uVar6;
  uVar7 = param_1[0x23] ^
          *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x24100u + (uint32_t)((uVar5 >> 0x18) * 4) * 1u)))) ^
          *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x23d00u + (uint32_t)((uVar1 >> 0x10 & 0xff) * 4) * 1u)))) ^
          *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x23900u + (uint32_t)((uVar2 >> 8 & 0xff) * 4) * 1u)))) ^
          *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x23500u + (uint32_t)((uVar7 & 0xff) * 4) * 1u))));
  param_1[0x2f] = uVar7;
  uVar2 = param_1[0x24] ^
          *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x24100u + (uint32_t)((uint)(*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 0xbf)))) * 4) * 1u)))) ^
          *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x23d00u + (uint32_t)((uint)(*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 0xba)))) * 4) * 1u)))) ^
          *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x23900u + (uint32_t)((uint)(*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 0xb5)))) * 4) * 1u)))) ^
          *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x23500u + (uint32_t)((uVar4 & 0xff) * 4) * 1u))));
  uVar1 = param_1[0x25] ^
          *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x24100u + (uint32_t)((uint)(*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 0xb3)))) * 4) * 1u)))) ^
          *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x23d00u + (uint32_t)((uint)(*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 0xbe)))) * 4) * 1u)))) ^
          *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x23900u + (uint32_t)((uint)(*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 0xb9)))) * 4) * 1u)))) ^
          *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x23500u + (uint32_t)((uVar3 & 0xff) * 4) * 1u))));
  uVar8 = *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x23900u + (uint32_t)((uint)(*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 0xb1)))) * 4) * 1u))));
  uVar7 = *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x23500u + (uint32_t)((uVar7 & 0xff) * 4) * 1u))));
  uVar5 = *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x23d00u + (uint32_t)((uint)(*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 0xb6)))) * 4) * 1u))));
  uVar4 = *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x24100u + (uint32_t)((uint)(*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 0xbb)))) * 4) * 1u))));
  uVar3 = param_1[0x26] ^
          *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x24100u + (uint32_t)((uint)(*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 0xb7)))) * 4) * 1u)))) ^
          *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x23d00u + (uint32_t)((uint)(*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 0xb2)))) * 4) * 1u)))) ^
          *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x23900u + (uint32_t)((uint)(*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 0xbd)))) * 4) * 1u)))) ^
          *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x23500u + (uint32_t)((uVar6 & 0xff) * 4) * 1u))));
  *(undefined *)(param_1 + 0x2c) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x23d00u + (uint32_t)((uVar2 & 0xff) * 4) * 1u))));
  uVar4 = param_1[0x27] ^ uVar4 ^ uVar5 ^ uVar8 ^ uVar7;
  (*((undefined *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 0xb1)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x23d00u + (uint32_t)((uVar1 >> 8 & 0xff) * 4) * 1u))));
  (*((undefined *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 0xb2)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x23d00u + (uint32_t)((uVar3 >> 0x10 & 0xff) * 4) * 1u))));
  (*((undefined *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 0xb3)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x23d00u + (uint32_t)((uVar4 >> 0x18) * 4) * 1u))));
  *(undefined *)(param_1 + 0x2d) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x23d00u + (uint32_t)((uVar1 & 0xff) * 4) * 1u))));
  (*((undefined *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 0xb5)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x23d00u + (uint32_t)((uVar3 >> 8 & 0xff) * 4) * 1u))));
  (*((undefined *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 0xb6)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x23d00u + (uint32_t)((uVar4 >> 0x10 & 0xff) * 4) * 1u))));
  (*((undefined *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 0xb7)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x23d00u + (uint32_t)((uVar2 >> 0x18) * 4) * 1u))));
  *(undefined *)(param_1 + 0x2e) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x23d00u + (uint32_t)((uVar3 & 0xff) * 4) * 1u))));
  (*((undefined *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 0xb9)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x23d00u + (uint32_t)((uVar4 >> 8 & 0xff) * 4) * 1u))));
  (*((undefined *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 0xba)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x23d00u + (uint32_t)((uVar2 >> 0x10 & 0xff) * 4) * 1u))));
  (*((undefined *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 0xbb)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x23d00u + (uint32_t)((uVar1 >> 0x18) * 4) * 1u))));
  *(undefined *)(param_1 + 0x2f) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x23d00u + (uint32_t)((uVar4 & 0xff) * 4) * 1u))));
  (*((undefined *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 0xbd)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x23d00u + (uint32_t)((uVar2 >> 8 & 0xff) * 4) * 1u))));
  (*((undefined *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 0xbe)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x23d00u + (uint32_t)((uVar1 >> 0x10 & 0xff) * 4) * 1u))));
  (*((undefined *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 0xbf)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x23d00u + (uint32_t)((uVar3 >> 0x18) * 4) * 1u))));
  param_1[0x2c] = param_1[0x2c] ^ param_1[0x28];
  param_1[0x2d] = param_1[0x2d] ^ param_1[0x29];
  param_1[0x2e] = param_1[0x2e] ^ param_1[0x2a];
  param_1[0x2f] = param_1[0x2f] ^ param_1[0x2b];
  return;
}
