#include "common.h"

undefined4 command_modify_aligned_cursor_word_820c4(int param_1,short *param_2)

{
  short sVar1;
  ushort uVar2;
  ushort uVar3;
  short sVar4;
  undefined1 uVar5;
  uint32_t puVar6;
  uint *puVar7;
  int iVar8;
  undefined4 uVar9;
  uint uVar10;
  
  sVar4 = DAT_00022aee;
  puVar6 = 0x23dfcu;
  sVar1 = *param_2;
  *param_2 = 2;
  if (sVar1 == sVar4) {
    uVar10 = (uint)(*((byte *)camry_host_ptr((uint32_t)(param_1 + 1))));
    if (uVar10 < 0x20) {
      puVar7 = ((uint *)camry_host_ptr((uint32_t)(get_memory_cursor_u32_8228e())));
      if (((uint)camry_host_addr(puVar7) & 3) == 0) {
        iVar8 = wrapper_memory_range_outside_write_window_83098(camry_host_addr(puVar7), 4);
        if (((((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x23dfcu + (uint32_t)(-0x1350) * 1u)))))<=camry_host_addr(puVar7)) &&
            ((int)camry_host_addr(puVar7) + 3U <= (*((uint *)camry_host_ptr((uint32_t)(puVar6 + -0x1354)))))) && (iVar8 == 0)) {
          uVar2 = (*((ushort *)camry_host_ptr((uint32_t)(param_1 + 2))));
          uVar3 = (*((ushort *)camry_host_ptr((uint32_t)(param_1 + 4))));
          uVar9 = call_interrupt_guard_and_return_zero_7a2da();
          *puVar7 = (uint)uVar3 << (uVar10 & 0x1f) ^
                    ~((uVar2 ^ 0xffff) << (uVar10 & 0x1f)) & *puVar7;
          ((void)(uVar9), thunk_pop_and_restore_priority_mask_stack_6a4c4());
          *param_2 = 1;
          return 0;
        }
      }
      (*((undefined1 *)camry_host_ptr((uint32_t)(param_1 + 1)))) = 0x24;
      return 1;
    }
    uVar5 = 0x22;
  }
  else {
    uVar5 = 0x21;
  }
  (*((undefined1 *)camry_host_ptr((uint32_t)(param_1 + 1)))) = uVar5;
  return 1;
}

void reset_session_and_memory_cursor_82166(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  DAT_febe5004 = 0;
  DAT_febe5005 = 0;
  (*(int (*)())camry_indirect((uint32_t)(PTR_FUN_00022af8)))();
  (*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + -0x6800)))) = 0;
  return;
}

void deactivate_session_and_call_22afc_82182(void)

{
  DAT_febe5005 = 0;
  (*(int (*)())camry_indirect((uint32_t)(PTR_FUN_00022afc)))();
  return;
}

void call_callback_22b00_82196(void)

{
  (*(int (*)())camry_indirect((uint32_t)(PTR_FUN_00022b00)))();
  return;
}

void set_active_session_id_821a6(undefined1 param_1)

{
  DAT_febe5004 = param_1;
  DAT_febe5005 = 1;
  return;
}

void close_session_and_clear_queue_indices_821b2(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  (*(int (*)())camry_indirect((uint32_t)(PTR_FUN_00022afc)))();
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x67fb))))) = 0;
  clear_packet_queue_indices_82ed6();
  return;
}

undefined1 get_session_active_flag_821ca(void)

{
  return DAT_febe5005;
}

undefined1 get_session_id_821d0(void)

{
  return DAT_febe5004;
}

void dispatch_session_command_and_send_response_821d6(char param_1,byte *param_2,ushort param_3)

{
  byte bVar1;
  uint uVar2;
  uint32_t puVar3;
  uint32_t puVar4;
  int iVar5;
  ushort uStack_12;
  
  puVar3 = 0xfebeb800u;
  puVar4 = 0x23dfcu;
  iVar5 = wrapper_predispatch_session_command_hook_830c0((uint)(byte)param_1, camry_host_addr(param_2),  (uint)(ushort)param_3);
  if (iVar5 == 0) {
    uStack_12 = param_3;
    if (*param_2 == 0xff) {
      iVar5 = command_connect_session_and_report_limits_82bd2(param_1, camry_host_addr(param_2), &uStack_12);
    }
    else {
      if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x67fc))))) != param_1) {
        return;
      }
      if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x67fb))))) != '\x01') {
        return;
      }
      uVar2 = *param_2 ^ 0xff;
      if (uVar2 < (byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x130b)))))) {
        iVar5 = (*(int (*)())camry_indirect((uint32_t)(*((code * *)camry_host_ptr((uint32_t)(puVar4 + (uint)(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(uVar2 - 0x12d8))))) * 4 + -0x12ac))))))(camry_host_addr(param_2), camry_host_addr(&uStack_12));
      }
      else {
        iVar5 = command_return_unsupported_error20_82a5c(camry_host_addr(param_2), &uStack_12);
      }
    }
    if (iVar5 != 0xff) {
      if (iVar5 == 0) {
        bVar1 = 0xff;
      }
      else {
        bVar1 = 0xfe;
      }
      *param_2 = bVar1;
      if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x1308))))) == '\0') {
        bVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x133c)))));
        for (uVar2 = (uint)(byte)uStack_12; uVar2 < bVar1; uVar2 = uVar2 + 1 & 0xff) {
          param_2[uVar2] = 0;
        }
        uStack_12 = (ushort)bVar1;
      }
      try_packet_callback_then_enqueue_if_busy_82fc0(param_1, camry_host_addr(param_2), uStack_12);
    }
  }
  return;
}

void set_memory_cursor_u32_82288(undefined4 param_1)

{
  DAT_febe5000 = param_1;
  return;
}

undefined4 get_memory_cursor_u32_8228e(void)

{
  return DAT_febe5000;
}

void initialize_sample_lists_and_pointer_slots_82294(void)

{
  int iVar1;
  uint uVar2;
  uint uVar3;
  
  uVar3 = (uint)DAT_00022ae6;
  DAT_febe5006 = 0x69;
  DAT_febe500a = 0;
  for (uVar2 = 0; uVar2 < uVar3; uVar2 = uVar2 + 1 & 0xff) {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe4ebcu + (uint32_t)(uVar2) * 1u)))) = 0;
  }
  uVar3 = (uint)DAT_00022ae7;
  for (uVar2 = 0; uVar2 < uVar3; uVar2 = uVar2 + 1 & 0xff) {
    iVar1 = uVar2 * 8;
    *(undefined2 *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe4cdcu + (uint32_t)(iVar1) * 1u)))) = 0;
    *(undefined2 *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe4cdeu + (uint32_t)(iVar1) * 1u)))) = 0;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe4ce0u + (uint32_t)(iVar1) * 1u)))) = 0;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe4ce2u + (uint32_t)(iVar1) * 1u)))) = 0xff;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe4ce1u + (uint32_t)(iVar1) * 1u)))) = 0;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe4ce3u + (uint32_t)(iVar1) * 1u)))) = 0;
  }
  uVar3 = (uint)DAT_00022ae4;
  DAT_febe500b = 0;
  for (uVar2 = 0; uVar2 < uVar3; uVar2 = uVar2 + 1 & 0xffff) {
    *(volatile uint32_t *)((uint8_t *)camry_host_ptr(0xfebe4cfcu) + uVar2 * 4) = 0xfebe500bu;
  }
  for (uVar2 = 0; uVar2 < DAT_00022abf; uVar2 = uVar2 + 1 & 0xff) {
    *(undefined4 *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe4cd4u + (uint32_t)(uVar2 * 8) * 1u)))) = 0;
    *(undefined4 *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe4cd8u + (uint32_t)(uVar2 * 8) * 1u)))) = 0;
  }
  DAT_febe5007 = 0xff;
  DAT_febe5008 = 0xff;
  DAT_febe5009 = 0xff;
  return;
}

undefined4 stop_all_sample_lists_82330(void)

{
  byte bVar1;
  uint uVar2;
  uint32_t puVar3;
  uint32_t puVar4;
  undefined4 uVar5;
  
  puVar3 = 0xfebeb800u;
  puVar4 = 0x23dfcu;
  uVar5 = call_interrupt_guard_and_return_zero_7a2da();
  bVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x1315)))));
  for (uVar2 = 0; uVar2 < bVar1; uVar2 = uVar2 + 1 & 0xff) {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(uVar2 * 8 + -0x6b1f))))) = 0;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x67f6))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x67f6))))) & 0x7f;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x67fa))))) = 0x69;
  ((void)(uVar5), thunk_pop_and_restore_priority_mask_stack_6a4c4());
  return uVar5;
}

void queue_pointer_sample_packets_82368(ushort param_1,byte param_2)

{
  int iVar1;
  int iVar2;
  byte bVar3;
  ushort uVar4;
  uint uVar5;
  uint32_t puVar6;
  uint32_t puVar7;
  undefined4 uVar8;
  uint uVar9;
  byte bVar10;
  
  puVar6 = 0xfebeb800u;
  puVar7 = 0x23dfcu;
  param_1 = param_1 & 0xff;
  if (param_2 < DAT_00022ae8) {
    uVar9 = 0;
    uVar4 = (ushort)DAT_00022ae9;
    iVar1 = (int)(short)param_1;
    for (bVar10 = 0; bVar10 <= param_2; bVar10 = bVar10 + 1) {
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(-0x6b2c))))) = (char)param_1;
      param_1 = param_1 + 1;
      uVar8 = call_interrupt_guard_and_return_zero_7a2da();
      bVar3 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar7 + (uint32_t)(-0x133b)))));
      for (uVar5 = 1; uVar5 < bVar3; uVar5 = uVar5 + 1 & 0xff) {
        iVar2 = uVar9 * 4;
        uVar9 = uVar9 + 1 & 0xff;
        (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(uVar5 - 0x6b2c))))) = (*((volatile undefined1 *)camry_host_ptr((*((volatile uint32_t *)((undefined *)camry_host_ptr((uint32_t)(0xfebe4cfcu + (uint32_t)(iVar2 + (short)uVar4 * iVar1 * 4) * 1u))))))))
        ;
      }
      ((void)(uVar8), thunk_pop_and_restore_priority_mask_stack_6a4c4());
      enqueue_fixed_packet_overwriting_oldest_82f44((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(-0x67fc))))), ((uint32_t)((uint32_t)(puVar6 + -0x6b2c))),  (uint)bVar3);
    }
  }
  return;
}

void tick_sample_lists_for_event_823e2(char param_1)

{
  undefined *puVar1;
  undefined *puVar2;
  uint32_t puVar3;
  uint uVar4;
  uint uVar5;
  
  puVar1 = ((undefined *)camry_host_ptr(0xfebeb800u));
  puVar3 = 0x23dfcu;
  if ((DAT_febe500a & 0x80) != 0) {
    uVar4 = (uint)DAT_00022ae7;
    for (uVar5 = 0; uVar5 < uVar4; uVar5 = uVar5 + 1 & 0xff) {
      if (((puVar1[uVar5 * 8 + -0x6b1f] & 1) != 0) && (puVar1[uVar5 * 8 + -0x6b20] == param_1)) {
        puVar2 = puVar1;
        if (*(short *)(puVar1 + uVar5 * 8 + -0x6b22) == 0) {
          *(undefined2 *)(puVar1 + uVar5 * 8 + -0x6b22) =
               *(undefined2 *)(puVar1 + uVar5 * 8 + -0x6b24);
          queue_pointer_sample_packets_82368((int)(short)(ushort)(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x1314))))) * (int)(short)uVar5 & 0xff,
                       puVar1[uVar5 * 8 + -0x6b1e]);
        }
        *(short *)(puVar1 + uVar5 * 8 + -0x6b22) = *(short *)(puVar1 + uVar5 * 8 + -0x6b22) + -1;
        puVar1 = puVar2;
      }
    }
  }
  return;
}

void tick_sample_event_prescalers_82444(void)

{
  undefined1 uVar1;
  uint32_t puVar2;
  uint32_t puVar3;
  uint uVar4;
  char *pcVar5;
  uint uVar6;
  
  puVar2 = 0xfebeb800u;
  puVar3 = 0x23dfcu;
  if (DAT_febe5006 == 'Z') {
    uVar4 = (uint)DAT_00022ae6;
    for (uVar6 = 0; uVar6 < uVar4; uVar6 = uVar6 + 1 & 0xff) {
      pcVar5 = ((void *)camry_host_ptr((uint32_t)(puVar2 + (uVar6 - 0x6944))));
      if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(uVar6 - 0x6944))))) == '\0') {
        uVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)((short)uVar6 * 3 + -0x1369)))));
        *pcVar5 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)((short)uVar6 * 3 + -0x136a)))));
        tick_sample_lists_for_event_823e2(uVar1);
      }
      *pcVar5 = *pcVar5 + -1;
    }
  }
  return;
}

undefined4 any_sample_list_enabled_82494(void)

{
  uint uVar1;
  
  uVar1 = 0;
  while( true ) {
    if (DAT_00022ae7 <= uVar1) {
      return 0;
    }
    if (((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe4ce1u + (uint32_t)(uVar1 * 8) * 1u)))) & 1) != 0) break;
    uVar1 = uVar1 + 1 & 0xff;
  }
  return 1;
}

undefined4 command_set_selected_sample_pointer_82510(int param_1,short *param_2)

{
  bool bVar1;
  short sVar2;
  byte bVar3;
  short sVar4;
  undefined1 uVar5;
  uint uVar6;
  uint32_t puVar7;
  uint32_t puVar8;
  int iVar9;
  byte bVar10;
  uint uVar11;
  byte bVar12;
  uint uVar13;
  uint uVar14;
  
  sVar4 = DAT_00022ad4;
  puVar7 = 0xfebeb800u;
  puVar8 = 0x23dfcu;
  sVar2 = *param_2;
  *param_2 = 2;
  if (sVar2 == sVar4) {
    if (((((int8_t)(*((char *)camry_host_ptr((uint32_t)(param_1 + 1))))) == -1) && ((*((char *)camry_host_ptr((uint32_t)(param_1 + 2)))) == '\x01')) &&
       ((*((char *)camry_host_ptr((uint32_t)(param_1 + 3)))) == '\0')) {
      uVar14 = (*((uint *)camry_host_ptr((uint32_t)(param_1 + 4))));
      iVar9 = wrapper_memory_range_overlaps_configured_regions_830a6(uVar14,1);
      if (((uVar14 < (*((uint *)camry_host_ptr((uint32_t)(puVar8 + -0x1358))))) || ((*((uint *)camry_host_ptr((uint32_t)(puVar8 + -0x135c)))) < uVar14)) ||
         (iVar9 != 0)) {
        uVar5 = 0x24;
      }
      else {
        bVar12 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar7 + (uint32_t)(-0x67f9)))));
        uVar13 = (uint)bVar12;
        bVar10 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar7 + (uint32_t)(-0x67f8)))));
        uVar11 = (uint)bVar10;
        uVar6 = (uint)(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar7 + (uint32_t)(-0x67f7)))));
        if (((uVar13 < (byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar8 + (uint32_t)(-0x1315)))))) && (uVar11 < (byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar8 + (uint32_t)(-0x1314))))))) &&
           (uVar6 < (byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar8 + (uint32_t)(-0x1313))))))) {
          if (((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar7 + (uint32_t)(uVar13 * 8 + -0x6b1f))))) & 1) == 0) {
            bVar3 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar7 + (uint32_t)(uVar13 * 8 + -0x6b1e)))));
            (*((uint *)camry_host_ptr((uint32_t)(puVar7 + (uVar6 + ((int)(short)(ushort)bVar12 *
                                         (int)(short)(ushort)(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar8 + (uint32_t)(-0x1314))))) + uVar11) *
                                        (uint)(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar8 + (uint32_t)(-0x1313))))) & 0xffff) * 4 + -0x6b04)))) =
                 uVar14;
            if ((bVar3 == 0xff) || (bVar3 < uVar11)) {
              (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar7 + (uint32_t)(uVar13 * 8 + -0x6b1e))))) = bVar10;
            }
            bVar1 = (uint)(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar8 + (uint32_t)(-0x1313))))) <= (uVar6 + 1 & 0xff);
            if (bVar1) {
              uVar5 = 0xff;
            }
            else {
              uVar5 = (undefined1)(uVar6 + 1);
            }
            (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar7 + (uint32_t)(-0x67f7))))) = uVar5;
            if (bVar1) {
              bVar12 = 0xff;
            }
            (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar7 + (uint32_t)(-0x67f9))))) = bVar12;
            if (bVar1) {
              bVar10 = 0xff;
            }
            (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar7 + (uint32_t)(-0x67f8))))) = bVar10;
            *param_2 = 1;
            return 0;
          }
          uVar5 = 0x11;
        }
        else {
          uVar5 = 0x23;
        }
      }
      (*((undefined1 *)camry_host_ptr((uint32_t)(param_1 + 1)))) = uVar5;
      return 1;
    }
  }
  (*((undefined1 *)camry_host_ptr((uint32_t)(param_1 + 1)))) = 0x21;
  return 1;
}

undefined4 enable_sample_scheduler_8268c(void)

{
  byte bVar1;
  uint uVar2;
  uint32_t puVar3;
  uint32_t puVar4;
  undefined4 uVar5;
  
  puVar3 = 0xfebeb800u;
  puVar4 = 0x23dfcu;
  uVar5 = call_interrupt_guard_and_return_zero_7a2da();
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x67f6))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x67f6))))) | 0x80;
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x67fa))))) != 'Z') {
    bVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x1316)))));
    for (uVar2 = 0; uVar2 < bVar1; uVar2 = uVar2 + 1 & 0xff) {
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(uVar2 - 0x6944))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)((short)uVar2 * 3 + -0x1368)))));
    }
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x67fa))))) = 0x5a;
  }
  ((void)(uVar5), thunk_pop_and_restore_priority_mask_stack_6a4c4());
  return uVar5;
}

undefined4 command_control_sample_list_826d6(int param_1,short *param_2)

{
  short sVar1;
  char cVar2;
  ushort uVar3;
  short sVar4;
  undefined1 uVar5;
  uint32_t puVar6;
  uint32_t puVar7;
  int iVar8;
  
  sVar4 = DAT_00022ad8;
  puVar6 = 0xfebeb800u;
  puVar7 = 0x23dfcu;
  sVar1 = *param_2;
  *param_2 = 2;
  if (sVar1 == sVar4) {
    uVar3 = (*((ushort *)camry_host_ptr((uint32_t)(param_1 + 2))));
    if ((uint)uVar3 < (uint)DAT_00022ae7) {
      iVar8 = (uVar3 & 0xff) * 8;
      cVar2 = (*((char *)camry_host_ptr((uint32_t)(param_1 + 1))));
      if (cVar2 == '\0') {
        (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe4ce1u + (uint32_t)(iVar8) * 1u)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe4ce1u + (uint32_t)(iVar8) * 1u)))) & 0xfe;
        iVar8 = any_sample_list_enabled_82494();
        if (iVar8 == 0) {
          (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(-0x67f6))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(-0x67f6))))) & 0x7f;
        }
LAB_0008271a:
        (*((char *)camry_host_ptr((uint32_t)(param_1 + 1)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar7 + (uint32_t)(-0x1314))))) * (char)uVar3;
        *param_2 = 2;
        return 0;
      }
      if (cVar2 == '\x01') {
        if ((*(short *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe4cdcu + (uint32_t)(iVar8) * 1u)))) != 0) &&
           ((byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe4ce2u + (uint32_t)(iVar8) * 1u)))) < DAT_00022ae8)) {
          *(undefined2 *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe4cdeu + (uint32_t)(iVar8) * 1u)))) = 0;
          (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe4ce1u + (uint32_t)(iVar8) * 1u)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe4ce1u + (uint32_t)(iVar8) * 1u)))) | 1;
          enable_sample_scheduler_8268c();
          goto LAB_0008271a;
        }
        uVar5 = 0x2a;
      }
      else {
        if (cVar2 == '\x02') {
          (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe4ce1u + (uint32_t)(iVar8) * 1u)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe4ce1u + (uint32_t)(iVar8) * 1u)))) | 4;
          goto LAB_0008271a;
        }
        uVar5 = 0x27;
      }
    }
    else {
      uVar5 = 0x22;
    }
  }
  else {
    uVar5 = 0x21;
  }
  (*((undefined1 *)camry_host_ptr((uint32_t)(param_1 + 1)))) = uVar5;
  return 1;
}

undefined4 selected_sample_lists_are_configured_8277a(void)

{
  int iVar1;
  uint uVar2;
  undefined4 uVar3;
  
  uVar3 = 0;
  uVar2 = 0;
  while( true ) {
    if (DAT_00022ae7 <= uVar2) {
      return uVar3;
    }
    iVar1 = uVar2 * 8;
    if ((((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe4ce1u + (uint32_t)(iVar1) * 1u)))) & 4) != 0) &&
       ((uVar3 = 1, *(short *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe4cdcu + (uint32_t)(iVar1) * 1u)))) == 0 ||
        (DAT_00022ae8 <= (byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe4ce2u + (uint32_t)(iVar1) * 1u)))))))) break;
    uVar2 = uVar2 + 1 & 0xff;
  }
  return 0;
}

undefined4 command_control_selected_sample_lists_827b4(int param_1,short *param_2)

{
  short sVar1;
  char cVar2;
  bool bVar3;
  short sVar4;
  undefined1 uVar5;
  uint uVar6;
  uint32_t puVar7;
  int extraout_r6;
  int iVar8;
  bool bVar9;
  uint uVar10;
  
  sVar4 = DAT_00022ada;
  puVar7 = 0xfebeb800u;
  sVar1 = *param_2;
  *param_2 = 2;
  if (sVar1 == sVar4) {
    cVar2 = (*((char *)camry_host_ptr((uint32_t)(param_1 + 1))));
    uVar10 = (uint)DAT_00022ae7;
    if (cVar2 == '\0') {
      stop_all_sample_lists_82330();
LAB_00082820:
      *param_2 = 1;
      return 0;
    }
    if (cVar2 == '\x01') {
      iVar8 = selected_sample_lists_are_configured_8277a();
      param_1 = ((int)(param_1));
      if (iVar8 == 1) {
        for (uVar6 = 0; uVar6 < uVar10; uVar6 = uVar6 + 1 & 0xff) {
          iVar8 = uVar6 * 8;
          if (((byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar7 + (uint32_t)(iVar8 + -0x6b1f))))) >> 2 & 1) != 0) {
            (*((undefined2 *)camry_host_ptr((uint32_t)(puVar7 + iVar8 + -0x6b22)))) = 0;
            (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar7 + (uint32_t)(iVar8 + -0x6b1f))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar7 + (uint32_t)(iVar8 + -0x6b1f))))) & 0xfb | 1;
          }
        }
        enable_sample_scheduler_8268c();
        goto LAB_00082820;
      }
    }
    else {
      if (cVar2 != '\x02') {
        uVar5 = 0x27;
        goto LAB_00082876;
      }
      bVar3 = false;
      bVar9 = false;
      for (uVar6 = 0; uVar6 < uVar10; uVar6 = uVar6 + 1 & 0xff) {
        if (((byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe4ce1u + (uint32_t)(uVar6 * 8) * 1u)))) >> 2 & 1) == 0) {
          if (((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe4ce1u + (uint32_t)(uVar6 * 8) * 1u)))) & 1) != 0) {
            bVar3 = true;
          }
        }
        else {
          (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe4ce1u + (uint32_t)(uVar6 * 8) * 1u)))) = 0;
          bVar9 = true;
        }
      }
      if (bVar9) {
        if (!bVar3) {
          DAT_febe500a = DAT_febe500a & 0x7f;
        }
        *param_2 = 1;
        return 0;
      }
    }
    uVar5 = 0x2a;
  }
  else {
    uVar5 = 0x21;
  }
LAB_00082876:
  (*((undefined1 *)camry_host_ptr((uint32_t)(param_1 + 1)))) = uVar5;
  return 1;
}

undefined4 command_clear_sample_list_configuration_82880(int param_1,short *param_2)

{
  ushort uVar1;
  short sVar2;
  short sVar3;
  undefined1 uVar4;
  uint uVar5;
  uint32_t puVar6;
  undefined2 *extraout_r7;
  int iVar7;
  
  sVar3 = DAT_00022ad0;
  puVar6 = 0xfebeb800u;
  sVar2 = *param_2;
  *param_2 = 2;
  if (sVar2 == sVar3) {
    uVar1 = (*((ushort *)camry_host_ptr((uint32_t)(param_1 + 2))));
    if ((uint)uVar1 < (uint)DAT_00022ae7) {
      iVar7 = (uVar1 & 0xff) * 8;
      DAT_febe500b = 0;
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe4ce1u + (uint32_t)(iVar7) * 1u)))) = 0;
      *(undefined2 *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe4cdcu + (uint32_t)(iVar7) * 1u)))) = 0;
      *(undefined2 *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe4cdeu + (uint32_t)(iVar7) * 1u)))) = 0;
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe4ce0u + (uint32_t)(iVar7) * 1u)))) = 0;
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe4ce2u + (uint32_t)(iVar7) * 1u)))) = 0xff;
      iVar7 = (int)(short)(ushort)DAT_00022ae8 * (int)(short)(ushort)DAT_00022ae9;
      uVar5 = (int)(short)iVar7 * (int)(short)uVar1;
      for (; iVar7 != 0; iVar7 = iVar7 + -1) {
        (*((volatile uint32_t *)((((undefined *)camry_host_ptr((uint32_t)(0xfebe4cfcu + (uint32_t)((uVar5 & 0xffff) * 4) * 1u))))))) = ((uint32_t)(0xfebe500bu));
        uVar5 = (uVar5 & 0xffff) + 1;
      }
      iVar7 = any_sample_list_enabled_82494();
      if (iVar7 == 0) {
        (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(-0x67f6))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(-0x67f6))))) & 0x7f;
      }
      *((undefined2 *)(param_2)) = 1;
      return 0;
    }
    uVar4 = 0x22;
  }
  else {
    uVar4 = 0x21;
  }
  (*((undefined1 *)camry_host_ptr((uint32_t)(param_1 + 1)))) = uVar4;
  return 1;
}

undefined4 command_get_sample_event_capabilities_829ce(int param_1,short *param_2)

{
  short sVar1;
  short sVar2;
  undefined1 uVar3;
  uint32_t puVar4;
  undefined2 uVar5;
  
  sVar2 = DAT_00022ae2;
  puVar4 = 0x23dfcu;
  sVar1 = *param_2;
  *param_2 = 2;
  if (sVar1 == sVar2) {
    if ((uint)(*((ushort *)camry_host_ptr((uint32_t)(param_1 + 2)))) < (uint)DAT_00022ae6) {
      uVar5 = (*(int (*)())camry_indirect((uint32_t)(PTR_FUN_00022ab4)))((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x22a92u + (uint32_t)((uint)(*((ushort *)camry_host_ptr((uint32_t)(param_1 + 2)))) * 3) * 1u)))));
      (*((undefined1 *)camry_host_ptr((uint32_t)(param_1 + 1)))) = 4;
      uVar3 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x1315)))));
      (*((undefined1 *)camry_host_ptr((uint32_t)(param_1 + 3)))) = 0;
      (*((char *)camry_host_ptr((uint32_t)(param_1 + 4)))) = (char)uVar5;
      (*((undefined1 *)camry_host_ptr((uint32_t)(param_1 + 6)))) = 0;
      (*((undefined1 *)camry_host_ptr((uint32_t)(param_1 + 2)))) = uVar3;
      (*((byte *)camry_host_ptr((uint32_t)(param_1 + 5)))) = (byte)((ushort)uVar5 >> 8) & 0xf;
      *param_2 = 7;
      return 0;
    }
    uVar3 = 0x22;
  }
  else {
    uVar3 = 0x21;
  }
  (*((undefined1 *)camry_host_ptr((uint32_t)(param_1 + 1)))) = uVar3;
  return 1;
}

uint encode_byte_as_scaled_tagged_value_82a3c(uint param_1)

{
  param_1 = param_1 & 0xff;
  if (0x33 < param_1) {
    return (int)(param_1 + 1) >> 1 | 0x700;
  }
  return (short)param_1 * 5 | 0x600;
}

undefined4 command_return_unsupported_error20_82a5c(int param_1,undefined2 *param_2)

{
  (*((undefined1 *)camry_host_ptr((uint32_t)(param_1 + 1)))) = 0x20;
  *param_2 = 2;
  return 1;
}

bool command_disconnect_active_session_82a6e(int param_1,short *param_2)

{
  short sVar1;
  short sVar2;
  
  sVar2 = DAT_00022ac6;
  sVar1 = *param_2;
  *param_2 = 2;
  if (sVar1 != sVar2) {
    (*((undefined1 *)camry_host_ptr((uint32_t)(param_1 + 1)))) = 0x21;
  }
  else {
    close_session_and_clear_queue_indices_821b2();
    *param_2 = 1;
  }
  return sVar1 != sVar2;
}

undefined4 command_clear_queue_and_return_status_error_82aa2(int param_1,short *param_2)

{
  short sVar1;
  short sVar2;
  undefined1 uVar3;
  
  sVar2 = DAT_00022aca;
  sVar1 = *param_2;
  *param_2 = 2;
  if (sVar1 == sVar2) {
    clear_packet_queue_indices_82ed6();
    uVar3 = 0;
  }
  else {
    uVar3 = 0x21;
  }
  (*((undefined1 *)camry_host_ptr((uint32_t)(param_1 + 1)))) = uVar3;
  return 1;
}

undefined4 command_get_callback_status_bit6_82ace(int param_1,short *param_2)

{
  short sVar1;
  short sVar2;
  int iVar3;
  undefined4 uVar4;
  undefined1 uVar5;
  
  sVar2 = DAT_00022ac8;
  sVar1 = *param_2;
  *param_2 = 2;
  if (sVar1 == sVar2) {
    uVar5 = 0;
    iVar3 = (*(int (*)())camry_indirect((uint32_t)(PTR_FUN_00022b04)))();
    if (iVar3 == 1) {
      uVar5 = 0x40;
    }
    (*((undefined1 *)camry_host_ptr((uint32_t)(param_1 + 1)))) = uVar5;
    (*((undefined1 *)camry_host_ptr((uint32_t)(param_1 + 2)))) = 0;
    (*((undefined1 *)camry_host_ptr((uint32_t)(param_1 + 3)))) = 0;
    uVar4 = 0;
    (*((undefined2 *)camry_host_ptr((uint32_t)(param_1 + 4)))) = 0;
    *param_2 = 6;
  }
  else {
    uVar4 = 1;
    (*((undefined1 *)camry_host_ptr((uint32_t)(param_1 + 1)))) = 0x21;
  }
  return uVar4;
}

undefined4 command_read_bytes_from_explicit_address_82b1a(int param_1,short *param_2)

{
  short sVar1;
  byte bVar2;
  short sVar3;
  undefined1 uVar4;
  uint uVar5;
  uint32_t puVar6;
  int iVar7;
  undefined4 uVar8;
  uint uVar9;
  uint uVar10;
  uint uVar11;
  
  sVar3 = DAT_00022ace;
  puVar6 = 0x23dfcu;
  sVar1 = *param_2;
  *param_2 = 2;
  if ((sVar1 == sVar3) && ((*((char *)camry_host_ptr((uint32_t)(param_1 + 3)))) == '\0')) {
    bVar2 = (*((byte *)camry_host_ptr((uint32_t)(param_1 + 1))));
    uVar11 = (uint)bVar2;
    if ((uVar11 != 0) &&
       (uVar9 = DAT_00022ac0 - 1,
       (int)(uVar11 - uVar9) < 0 != ((int)uVar9 < 0 && (int)uVar9 < 0 == (int)(uVar11 - uVar9) < 0)
       || uVar11 == uVar9)) {
      uVar10 = (*((uint *)camry_host_ptr((uint32_t)(param_1 + 4))));
      uVar9 = uVar11 - 1 & 0xff;
      if (uVar9 <= ~uVar10) {
        uVar9 = uVar9 + uVar10;
        iVar7 = wrapper_memory_range_overlaps_configured_regions_830a6(uVar10,uVar11);
        if ((((*((uint *)camry_host_ptr((uint32_t)(puVar6 + -0x1358)))) <= uVar10) && (uVar9 <= (*((uint *)camry_host_ptr((uint32_t)(puVar6 + -0x135c)))))) &&
           (iVar7 == 0)) {
          uVar8 = call_interrupt_guard_and_return_zero_7a2da();
          for (uVar5 = 0; uVar5 < uVar11; uVar5 = uVar5 + 1 & 0xff) {
            (*((undefined1 *)camry_host_ptr((uint32_t)(uVar5 + param_1 + 1)))) = (*((undefined1 *)camry_host_ptr((uint32_t)(uVar5 + uVar10))));
          }
          ((void)(uVar8), thunk_pop_and_restore_priority_mask_stack_6a4c4());
          set_memory_cursor_u32_82288(uVar9 + 1);
          *param_2 = bVar2 + 1;
          return 0;
        }
      }
      (*((undefined1 *)camry_host_ptr((uint32_t)(param_1 + 1)))) = 0x24;
      return 1;
    }
    uVar4 = 0x22;
  }
  else {
    uVar4 = 0x21;
  }
  (*((undefined1 *)camry_host_ptr((uint32_t)(param_1 + 1)))) = uVar4;
  return 1;
}

undefined4 command_connect_session_and_report_limits_82bd2(char param_1,int param_2,short *param_3)

{
  short sVar1;
  short sVar2;
  uint32_t puVar3;
  uint32_t puVar4;
  byte bVar5;
  undefined4 uVar6;
  
  sVar2 = DAT_00022ac4;
  puVar3 = 0xfebeb800u;
  puVar4 = 0x23dfcu;
  sVar1 = *param_3;
  uVar6 = 1;
  *param_3 = 2;
  if ((sVar1 == sVar2) && ((*((char *)camry_host_ptr((uint32_t)(param_2 + 1)))) == '\0')) {
    bVar5 = return_const_5_98eee();
    (*((byte *)camry_host_ptr((uint32_t)(param_2 + 1)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x130a))))) | bVar5;
    (*((undefined *)camry_host_ptr((uint32_t)(param_2 + 2)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x1309)))));
    (*((undefined *)camry_host_ptr((uint32_t)(param_2 + 3)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x133c)))));
    (*((ushort *)camry_host_ptr((uint32_t)(param_2 + 4)))) = (ushort)(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x133b)))));
    (*((undefined1 *)camry_host_ptr((uint32_t)(param_2 + 6)))) = 1;
    (*((undefined1 *)camry_host_ptr((uint32_t)(param_2 + 7)))) = 1;
    if (((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x67fc))))) != param_1) && ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x67fb))))) == '\x01')) {
      close_session_and_clear_queue_indices_821b2();
    }
    set_active_session_id_821a6(param_1);
    uVar6 = 0;
    *param_3 = 8;
  }
  else {
    (*((undefined1 *)camry_host_ptr((uint32_t)(param_2 + 1)))) = 0x21;
    if ((DAT_febe5004 != param_1) || (DAT_febe5005 != '\x01')) {
      uVar6 = 0xff;
    }
  }
  return uVar6;
}

undefined4 command_set_memory_cursor_82c62(int param_1,short *param_2)

{
  short sVar1;
  short sVar2;
  undefined4 uVar3;
  
  sVar2 = DAT_00022acc;
  sVar1 = *param_2;
  *param_2 = 2;
  uVar3 = 1;
  if ((sVar1 == sVar2) && ((*((char *)camry_host_ptr((uint32_t)(param_1 + 3)))) == '\0')) {
    set_memory_cursor_u32_82288((*((undefined4 *)camry_host_ptr((uint32_t)(param_1 + 4)))));
    uVar3 = 0;
    *param_2 = 1;
  }
  else {
    (*((undefined1 *)camry_host_ptr((uint32_t)(param_1 + 1)))) = 0x21;
  }
  return uVar3;
}

void initialize_packet_queue_and_channel_gates_82c9e(void)

{
  int iVar1;
  byte bVar2;
  uint uVar3;
  uint uVar4;
  uint32_t puVar5;
  uint32_t puVar6;
  uint uVar7;
  uint uVar8;
  uint uVar9;
  uint uVar10;
  
  puVar5 = 0xfebeb800u;
  puVar6 = 0x23dfcu;
  DAT_febe500c = 0;
  uVar9 = 0;
  DAT_febe500d = 0;
  DAT_febe500e = 0x69;
  uVar7 = (uint)DAT_00022abe;
  uVar8 = (uint)DAT_00022abf;
  for (uVar4 = 0; uVar10 = 0, uVar3 = uVar8, uVar4 < uVar7; uVar4 = uVar4 + 1 & 0xff) {
    for (; uVar3 != 0; uVar3 = uVar3 - 1) {
      iVar1 = uVar9 * 8;
      uVar9 = uVar9 + 1 & 0xffff;
      *(undefined4 *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe4c3cu + (uint32_t)(iVar1) * 1u)))) = 0;
      *(undefined4 *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe4c40u + (uint32_t)(iVar1) * 1u)))) = 0;
    }
    *(undefined2 *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe4ec0u + (uint32_t)(uVar4 * 2) * 1u)))) = 0;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe4ee7u + (uint32_t)(uVar4) * 1u)))) = 0;
  }
  for (; uVar10 < uVar8; uVar10 = uVar10 + 1 & 0xff) {
    *(undefined4 *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe4c34u + (uint32_t)(uVar10 * 8) * 1u)))) = 0;
    *(undefined4 *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe4c38u + (uint32_t)(uVar10 * 8) * 1u)))) = 0;
  }
  (*(int (*)())camry_indirect((uint32_t)(PTR_FUN_00022b08)))();
  bVar2 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(-0x1340)))));
  for (uVar9 = 0; uVar9 < bVar2; uVar9 = uVar9 + 1 & 0xff) {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(uVar9 - 0x691a))))) = 0x69;
  }
  return;
}

void disable_packet_channels_and_reset_queue_82d38(void)

{
  uint uVar1;
  uint32_t puVar2;
  uint uVar3;
  
  puVar2 = 0xfebeb800u;
  uVar3 = (uint)DAT_00022abc;
  for (uVar1 = 0; uVar1 < uVar3; uVar1 = uVar1 + 1 & 0xff) {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe4ee6u + (uint32_t)(uVar1) * 1u)))) = 0x69;
  }
  (*(int (*)())camry_indirect((uint32_t)(PTR_FUN_00022b0c)))();
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x67f4))))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x67f3))))) = 0;
  return;
}

undefined4 try_channel_packet_callback_82d6c(uint param_1,undefined4 param_2,undefined2 param_3)

{
  undefined4 uVar1;
  
  param_1 = param_1 & 0xff;
  uVar1 = 0;
  if ((param_1 < DAT_00022abc) && ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe4ee6u + (uint32_t)(param_1) * 1u)))) == 'Z')) {
    uVar1 = (*(int (*)())camry_indirect((uint32_t)(PTR_FUN_00022ab0)))(param_1,param_2,param_3);
  }
  return uVar1;
}

void drain_packet_queue_until_callback_busy_82d98(void)

{
  uint32_t puVar1;
  uint32_t puVar2;
  uint uVar3;
  uint uVar4;
  uint uVar5;
  uint uVar6;
  uint uVar7;
  
  puVar1 = 0xfebeb800u;
  puVar2 = 0x23dfcu;
  uVar5 = (uint)DAT_00022abe;
  uVar4 = (uint)DAT_febe500c;
  uVar6 = (uint)DAT_febe500d;
  if ((uVar4 < uVar5) && (uVar6 < uVar5)) {
    uVar3 = 0;
    do {
      if (uVar4 == uVar6) {
        return;
      }
      if ((((ushort)(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x133f))))) < (*((ushort *)camry_host_ptr((uint32_t)(puVar1 + uVar6 * 2 + -0x6940))))) ||
          (uVar3 = try_channel_packet_callback_82d6c((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(uVar6 - 0x6919))))),
                                puVar1 + (int)(short)(ushort)(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x133d))))) *
                                         (int)(short)uVar6 * 8 + -0x6bc4, (*((ushort *)camry_host_ptr((uint32_t)(puVar1 + uVar6 * 2 - 0x6940))))), uVar3 == 0)) &&
         (uVar7 = uVar6 + 1 & 0xff, uVar6 = uVar3, uVar7 < uVar5)) {
        uVar6 = uVar7;
      }
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x67f3))))) = (char)uVar6;
    } while (uVar3 == 0);
  }
  return;
}

undefined4 mark_packet_queue_idle_if_empty_82dfe(void)

{
  uint32_t puVar1;
  uint32_t puVar2;
  undefined4 uVar3;
  int iVar4;
  
  puVar1 = 0xfebeb800u;
  puVar2 = 0x23dfcu;
  uVar3 = call_interrupt_guard_and_return_zero_7a2da();
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x67f4))))) == (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x67f3)))))) {
    iVar4 = (*(int (*)())camry_indirect((uint32_t)(((((code *)(uintptr_t)((uint32_t)((uintptr_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(puVar2 + -0x12e0))))))))))))();
    uVar3 = iVar4;
    if (iVar4 == 0) {
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x67f2))))) = 0x69;
    }
  }
  thunk_pop_and_restore_priority_mask_stack_6a4c4();
  return uVar3;
}

void service_active_packet_queue_82e32(void)

{
  if (DAT_febe500e == 'Z') {
    (*(int (*)())camry_indirect((uint32_t)(PTR_FUN_00022b10)))();
    drain_packet_queue_until_callback_busy_82d98();
    mark_packet_queue_idle_if_empty_82dfe();
  }
  return;
}

uint find_packet_channel_by_configured_id_82e54(char param_1)

{
  uint uVar1;
  
  for (uVar1 = 0; (uVar1 < DAT_00022abc && ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x22a8eu + (uint32_t)(uVar1) * 1u)))) != param_1));
      uVar1 = uVar1 + 1 & 0xff) {
  }
  return uVar1;
}

void call_22b18_if_channel_matches_current_82e74(uint param_1)

{
  uint32_t puVar1;
  uint uVar2;
  
  puVar1 = 0x23dfcu;
  uVar2 = (*(int (*)())camry_indirect((uint32_t)(PTR_FUN_00022b20)))();
  if ((param_1 & 0xff) == uVar2) {
    (*(int (*)())camry_indirect((uint32_t)(((((code *)(uintptr_t)((uint32_t)((uintptr_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(puVar1 + -0x12e4))))))))))))();
  }
  return;
}

uint notify_current_packet_channel_by_id_82e94(undefined1 param_1)

{
  uint32_t puVar1;
  uint uVar2;
  
  puVar1 = 0x23dfcu;
  uVar2 = find_packet_channel_by_configured_id_82e54(param_1);
  if (uVar2 < (byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x1340)))))) {
    call_22b18_if_channel_matches_current_82e74(uVar2);
  }
  return uVar2;
}

void disable_packet_channel_and_notify_if_current_82eb0(undefined1 param_1)

{
  uint32_t puVar1;
  uint32_t puVar2;
  uint uVar3;
  
  puVar1 = 0xfebeb800u;
  puVar2 = 0x23dfcu;
  uVar3 = find_packet_channel_by_configured_id_82e54(param_1);
  if (uVar3 < (byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x1340)))))) {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(uVar3 - 0x691a))))) = 0x69;
    call_22b18_if_channel_matches_current_82e74(uVar3);
  }
  return;
}

undefined4 clear_packet_queue_indices_82ed6(void)

{
  uint32_t puVar1;
  undefined4 uVar2;
  
  puVar1 = 0xfebeb800u;
  uVar2 = call_interrupt_guard_and_return_zero_7a2da();
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x67f4))))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x67f3))))) = 0;
  ((void)(uVar2), thunk_pop_and_restore_priority_mask_stack_6a4c4());
  return uVar2;
}

void clear_queue_if_mapped_channel_is_current_82ef0(undefined1 param_1)

{
  uint32_t puVar1;
  uint uVar2;
  uint uVar3;
  
  puVar1 = 0x23dfcu;
  uVar2 = find_packet_channel_by_configured_id_82e54(param_1);
  if ((uVar2 < (byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x1340)))))) && (uVar3 = (*(int (*)())camry_indirect((uint32_t)(((((code *)(uintptr_t)((uint32_t)((uintptr_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(puVar1 + -0x12dc))))))))))))(), uVar2 == uVar3)
     ) {
    clear_packet_queue_indices_82ed6();
  }
  return;
}

uint set_packet_channel_gate_from_boolean_82f18(undefined1 param_1,char param_2)

{
  undefined1 uVar1;
  uint32_t puVar2;
  uint32_t puVar3;
  uint uVar4;
  
  puVar2 = 0xfebeb800u;
  puVar3 = 0x23dfcu;
  uVar4 = find_packet_channel_by_configured_id_82e54(param_1);
  if (uVar4 < (byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x1340)))))) {
    uVar1 = 0x69;
    if (param_2 == '\x01') {
      uVar1 = 0x5a;
    }
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(uVar4 - 0x691a))))) = uVar1;
  }
  return uVar4;
}

void enqueue_fixed_packet_overwriting_oldest_82f44(undefined1 param_1,int param_2,undefined2 param_3)

{
  undefined4 *puVar1;
  int iVar2;
  uint uVar3;
  ushort uVar4;
  uint uVar5;
  uint uVar6;
  uint uVar7;
  uint uVar8;
  
  uVar6 = (uint)DAT_00022abe;
  uVar3 = (uint)DAT_febe500c;
  uVar8 = (uint)DAT_febe500d;
  if ((uVar3 < uVar6) && (uVar8 < uVar6)) {
    uVar5 = (uint)DAT_00022abf;
    uVar4 = (ushort)DAT_00022abf;
    for (uVar7 = 0; uVar7 < uVar5; uVar7 = uVar7 + 1 & 0xff) {
      puVar1 = ((undefined4 *)camry_host_ptr((uint32_t)(uVar7 * 8 + param_2)));
      iVar2 = (uVar7 + (int)(short)uVar4 * (int)(short)(ushort)DAT_febe500c) * 8;
      *(undefined4 *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe4c3cu + (uint32_t)(iVar2) * 1u)))) = *puVar1;
      *(undefined4 *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe4c40u + (uint32_t)(iVar2) * 1u)))) = puVar1[1];
    }
    *(undefined2 *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe4ec0u + (uint32_t)(uVar3 * 2) * 1u)))) = param_3;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe4ee7u + (uint32_t)(uVar3) * 1u)))) = param_1;
    uVar3 = uVar3 + 1 & 0xff;
    if (uVar6 <= uVar3) {
      uVar3 = 0;
    }
    if ((uVar3 == uVar8) && (DAT_febe500d = (byte)(uVar8 + 1), uVar6 <= (uVar8 + 1 & 0xff))) {
      DAT_febe500d = 0;
    }
    DAT_febe500c = (byte)uVar3;
  }
  return;
}

int try_packet_callback_then_enqueue_if_busy_82fc0(undefined1 param_1,undefined4 param_2,undefined2 param_3)

{
  uint32_t puVar1;
  int iVar2;
  
  puVar1 = 0xfebeb800u;
  iVar2 = try_channel_packet_callback_82d6c((uint)(byte)param_1, param_2, (uint)(ushort)param_3);
  if (iVar2 != 0) {
    enqueue_fixed_packet_overwriting_oldest_82f44(param_1,param_2,param_3);
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x67f2))))) = 0x5a;
  return iVar2;
}

void dispatch_packet_for_enabled_channel_82fec(uint param_1,undefined4 param_2,undefined2 param_3)

{
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe4ee6u + (uint32_t)(param_1 & 0xff) * 1u)))) == 'Z') {
    (*(int (*)())camry_indirect((uint32_t)(PTR_FUN_00022b14)))(param_1 & 0xff,param_2,param_3);
  }
  return;
}
