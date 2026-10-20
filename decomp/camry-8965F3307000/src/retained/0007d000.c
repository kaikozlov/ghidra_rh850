#include "common.h"

void return_only_stub_7d014(void)

{
  return;
}

void return_only_stub_7d016(void)

{
  return;
}

void return_only_stub_7d018(void)

{
  return;
}

void copy_two_network_group_request_vectors_7d01a(int param_1)

{
  int iVar1;
  undefined1 uVar2;
  undefined1 uVar3;
  undefined8 uVar4;
  undefined4 uVar5;
  uint uVar6;
  uint uVar7;
  uint uVar8;
  
  uVar4 = 0x23dfcfebeb800;
  uVar6 = (uint)DAT_00021c6e;
  uVar7 = uVar6;
  for (uVar8 = 0; uVar8 < uVar6; uVar8 = uVar8 + 1 & 0xff) {
    uVar2 = (*((undefined1 *)camry_host_ptr((uint32_t)(uVar8 + param_1))));
    uVar3 = (*((undefined1 *)camry_host_ptr((uint32_t)(uVar7 + param_1))));
    uVar5 = call_interrupt_guard_and_return_zero_7a2da();
    iVar1 = uVar8 + (int)uVar4;
    (*((undefined1 *)camry_host_ptr((uint32_t)(iVar1 + -0x6dc5)))) = uVar2;
    (*((undefined1 *)camry_host_ptr((uint32_t)(iVar1 + -0x6dbf)))) = uVar3;
    ((void)(uVar5), thunk_pop_and_restore_priority_mask_stack_6a4c4());
    uVar7 = uVar7 + 1 & 0xff;
  }
  return;
}

undefined4 copy_com_pdu_buffer_and_return_availability_7d05c(uint param_1,int param_2)

{
  char cVar1;
  ushort uVar2;
  ushort uVar3;
  uint uVar4;
  uint32_t puVar5;
  undefined4 uVar6;
  
  puVar5 = 0xfebeb800u;
  param_1 = param_1 & 0xffff;
  uVar2 = *(ushort *)(((undefined *)camry_host_ptr((uint32_t)(0x226c4u + (uint32_t)(param_1 * 8) * 1u))));
  uVar3 = *(ushort *)(((undefined *)camry_host_ptr((uint32_t)(0x22840u + (uint32_t)(param_1 * 2) * 1u))));
  uVar6 = thunk_call_interrupt_guard_and_return_zero_7a2da();
  for (uVar4 = 0; uVar4 < uVar2; uVar4 = uVar4 + 1 & 0xffff) {
    (*((undefined1 *)camry_host_ptr((uint32_t)(uVar4 + param_2)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe4a48u + (uint32_t)(uVar4 + uVar3) * 1u))));
  }
  cVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(param_1 - 0x6ec2)))));
  ((void)(uVar6), thunk_pop_and_restore_priority_mask_stack_6a4c4());
  uVar6 = 0x20;
  if (cVar1 < '\0') {
    uVar6 = 0;
  }
  return uVar6;
}

byte get_mapped_com_pdu_status_bits_23_7d0b8(uint param_1)

{
  ushort uVar1;
  byte bVar2;
  uint32_t puVar3;
  undefined4 uVar4;
  uint uVar5;
  
  puVar3 = 0xfebeb800u;
  uVar1 = *(ushort *)(((undefined *)camry_host_ptr((uint32_t)(0x22488u + (uint32_t)((param_1 & 0xffff) * 2) * 1u))));
  uVar5 = (uint)DAT_00021c54;
  uVar4 = call_interrupt_guard_and_return_zero_7a2da();
  bVar2 = 1;
  if (uVar1 < uVar5) {
    bVar2 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(uVar1 - 0x6ec2)))));
  }
  ((void)(uVar4), thunk_pop_and_restore_priority_mask_stack_6a4c4());
  return bVar2 & 0x23;
}

byte get_com_pdu_status_with_group_enable_bit_7d0ea(uint param_1)

{
  uchar *puVar1;
  byte bVar2;
  
  param_1 = param_1 & 0xffff;
  bVar2 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe493eu + (uint32_t)(param_1) * 1u)))) & 0x33;
  if (param_1 < DAT_00021c56) {
    puVar1 = ((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe4a39u + (uint32_t)(3) * 1u)));
  }
  else {
    puVar1 = ((undefined *)camry_host_ptr(0xfebe4a42u));
  }
  if (((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x22148u + (uint32_t)(param_1) * 1u)))) & puVar1[(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x226c2u + (uint32_t)(param_1 * 8) * 1u))))]) != 0) {
    bVar2 = bVar2 | 0x80;
  }
  return bVar2;
}

undefined4
extract_com_big_endian_bitfield_with_optional_sign_extension_7d12a(uint param_1,uint param_2,uint param_3,int param_4,char param_5,uint *param_6)

{
  byte *pbVar1;
  uint uVar2;
  byte bVar3;
  byte bVar4;
  byte bVar5;
  byte bVar6;
  char cVar7;
  ushort uVar8;
  uint32_t puVar9;
  undefined4 uVar10;
  uint uVar11;
  uint uVar12;
  
  puVar9 = 0xfebeb800u;
  uVar12 = param_3 & 0xff;
  uVar8 = *(ushort *)(((undefined *)camry_host_ptr((uint32_t)(0x22488u + (uint32_t)((param_1 & 0xffff) * 2) * 1u))));
  uVar10 = call_interrupt_guard_and_return_zero_7a2da();
  cVar7 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar9 + (uint32_t)(uVar8 - 0x6ec2)))));
  pbVar1 = ((undefined *)camry_host_ptr((uint32_t)(puVar9 + ((param_2 & 0xffff) - 0x6db8))));
  bVar3 = pbVar1[3];
  bVar4 = pbVar1[2];
  bVar5 = pbVar1[1];
  bVar6 = *pbVar1;
  ((void)(uVar10), thunk_pop_and_restore_priority_mask_stack_6a4c4());
  uVar10 = 0x20;
  if (cVar7 < '\0') {
    uVar10 = 0;
  }
  uVar11 = 0xffffffff;
  if (uVar12 < 0x20) {
    uVar11 = (1 << (param_3 & 0x1f)) - 1;
  }
  uVar11 = ((uint)bVar3 | (uint)bVar4 << 8 | (uint)bVar5 << 0x10 | (uint)bVar6 << 0x18) >>
           ((param_4 - (param_4 + uVar12 + 7 & 0xf8)) + 0x20 & 0x1f) & uVar11;
  if ((param_5 == '\x01') && (uVar2 = 1 << (uVar12 - 1 & 0x1f), (uVar2 & uVar11) != 0)) {
    uVar11 = uVar11 | ~(uVar2 - 1);
  }
  if (uVar12 < 9) {
    *(char *)param_6 = (char)uVar11;
  }
  else if (uVar12 < 0x11) {
    *(short *)param_6 = (short)uVar11;
  }
  else {
    *param_6 = uVar11;
  }
  return uVar10;
}

undefined4 insert_com_big_endian_signal_and_apply_trigger_policy_7d1dc(uint param_1,uint param_2,uint param_3,uint param_4,uint *param_5)

{
  byte *pbVar1;
  char cVar2;
  ushort uVar3;
  uint uVar4;
  uint32_t puVar5;
  undefined4 uVar6;
  char cVar7;
  uint uVar8;
  uint uVar9;
  uint uVar10;
  
  puVar5 = 0xfebeb800u;
  uVar8 = param_3 & 0xff;
  uVar9 = 0xffffffff;
  uVar3 = *(ushort *)(((undefined *)camry_host_ptr((uint32_t)(0x22488u + (uint32_t)((param_1 & 0xffff) * 2) * 1u))));
  cVar2 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x2236cu + (uint32_t)(param_1 & 0xffff) * 1u))));
  if (uVar8 < 0x20) {
    uVar9 = (1 << (param_3 & 0x1f)) - 1;
  }
  if (uVar8 < 9) {
    uVar10 = (uint)(byte)*param_5;
  }
  else if (uVar8 < 0x11) {
    uVar10 = (uint)(ushort)*param_5;
  }
  else {
    uVar10 = *param_5;
  }
  uVar6 = call_interrupt_guard_and_return_zero_7a2da();
  if (uVar8 == 1) {
    uVar8 = (uint)(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)((param_2 & 0xffff) - 0x6db8)))));
    uVar9 = (uVar9 & 0xff) << (param_4 & 0x1f) & 0xff;
    if ((*param_5 & 1) == 0) {
      cVar7 = '\x02';
      uVar9 = (uVar9 ^ 0xff) & uVar8;
    }
    else {
      uVar9 = uVar9 | uVar8;
      cVar7 = '\x01';
    }
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)((param_2 & 0xffff) - 0x6db8))))) = (byte)uVar9;
    if ((cVar2 != '\x04') && ((uVar8 == uVar9 || ((cVar2 != cVar7 && (cVar2 != '\x03'))))))
    goto LAB_0007d304;
  }
  else {
    uVar4 = ((param_4 & 0xff) - ((param_4 & 0xff) + uVar8 + 7 & 0xf8)) + 0x20;
    uVar8 = uVar9 << (uVar4 & 0x1f);
    uVar9 = (uVar10 & uVar9) << (uVar4 & 0x1f);
    uVar10 = ~uVar8;
    pbVar1 = ((undefined *)camry_host_ptr((uint32_t)(puVar5 + ((param_2 & 0xffff) - 0x6db8))));
    if ((cVar2 == '\x03') &&
       ((uVar8 & ((uint)pbVar1[3] |
                 (uint)pbVar1[2] << 8 | (uint)pbVar1[1] << 0x10 | (uint)*pbVar1 << 0x18)) == uVar9))
    goto LAB_0007d304;
    *pbVar1 = *pbVar1 & (byte)(uVar10 >> 0x18) | (byte)(uVar9 >> 0x18);
    pbVar1[1] = pbVar1[1] & (byte)(uVar10 >> 0x10) | (byte)(uVar9 >> 0x10);
    pbVar1[2] = pbVar1[2] & (byte)(uVar10 >> 8) | (byte)(uVar9 >> 8);
    pbVar1[3] = pbVar1[3] & (byte)uVar10 | (byte)uVar9;
  }
  request_tx_by_group_and_mode_7e196((uint)uVar3,0x80);
LAB_0007d304:
  cVar2 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(uVar3 - 0x6ec2)))));
  ((void)(uVar6), thunk_pop_and_restore_priority_mask_stack_6a4c4());
  uVar6 = 0x20;
  if (cVar2 < '\0') {
    uVar6 = 0;
  }
  return uVar6;
}

undefined4 insert_com_big_endian_signal_without_trigger_7d31e(uint param_1,uint param_2,uint param_3,int param_4,uint *param_5)

{
  byte *pbVar1;
  int iVar2;
  char cVar3;
  uint uVar4;
  uint32_t puVar5;
  uint32_t puVar6;
  uint uVar7;
  undefined4 uVar8;
  uint uVar9;
  
  puVar5 = 0xfebeb800u;
  puVar6 = 0x23dfcu;
  uVar7 = param_3 & 0xff;
  uVar4 = 0xffffffff;
  if (uVar7 < 0x20) {
    uVar4 = (1 << (param_3 & 0x1f)) - 1;
  }
  if (uVar7 < 9) {
    uVar9 = (uint)(byte)*param_5;
  }
  else if (uVar7 < 0x11) {
    uVar9 = (uint)(ushort)*param_5;
  }
  else {
    uVar9 = *param_5;
  }
  uVar7 = (param_4 - (param_4 + uVar7 + 7 & 0xf8)) + 0x20;
  iVar2 = (uVar9 & uVar4) << (uVar7 & 0x1f);
  uVar4 = ~(uVar4 << (uVar7 & 0x1f));
  uVar8 = call_interrupt_guard_and_return_zero_7a2da();
  pbVar1 = ((undefined *)camry_host_ptr((uint32_t)(puVar5 + ((param_2 & 0xffff) - 0x6db8))));
  *pbVar1 = *pbVar1 & (byte)(uVar4 >> 0x18) | (byte)((uint)iVar2 >> 0x18);
  pbVar1[1] = pbVar1[1] & (byte)(uVar4 >> 0x10) | (byte)((uint)iVar2 >> 0x10);
  pbVar1[2] = pbVar1[2] & (byte)(uVar4 >> 8) | (byte)((uint)iVar2 >> 8);
  pbVar1[3] = pbVar1[3] & (byte)uVar4 | (byte)iVar2;
  cVar3 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)((*((ushort *)camry_host_ptr((uint32_t)(puVar6 + (param_1 & 0xffff) * 2 + -0x1974)))) - 0x6ec2)))));
  ((void)(uVar8), thunk_pop_and_restore_priority_mask_stack_6a4c4());
  uVar8 = 0x20;
  if (cVar3 < '\0') {
    uVar8 = 0;
  }
  return uVar8;
}

void reconcile_com_group_masks_and_pdu_availability_timers_7d3f0(uint param_1)

{
  ushort uVar1;
  uint uVar2;
  undefined1 uVar3;
  byte bVar4;
  byte bVar5;
  byte bVar6;
  byte bVar7;
  byte bVar8;
  short sVar9;
  byte bVar10;
  ushort uVar11;
  uint32_t puVar12;
  uint32_t puVar13;
  undefined4 uVar14;
  uint uVar15;
  uint uVar16;
  
  uVar11 = DAT_00021c56;
  puVar12 = 0xfebeb800u;
  puVar13 = 0x23dfcu;
  param_1 = param_1 & 0xff;
  uVar3 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe4a43u + (uint32_t)(param_1) * 1u))));
  bVar4 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe4a42u + (uint32_t)(param_1) * 1u))));
  bVar5 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe4a41u + (uint32_t)(param_1) * 1u))));
  bVar6 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe4a46u + (uint32_t)(param_1) * 1u))));
  bVar7 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe4a45u + (uint32_t)(param_1) * 1u))));
  if ((bVar4 != bVar5) || (bVar6 != bVar7)) {
    uVar16 = (uint)*(ushort *)(((undefined *)camry_host_ptr((uint32_t)(0x22144u + (uint32_t)(param_1 * 4) * 1u))));
    uVar2 = *(ushort *)(((undefined *)camry_host_ptr((uint32_t)(0x22146u + (uint32_t)(param_1 * 4) * 1u)))) + uVar16;
    for (; uVar16 < (uVar2 & 0xffff); uVar16 = uVar16 + 1 & 0xffff) {
      bVar8 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar13 + (uint32_t)(uVar16 - 0x1cb4)))));
      sVar9 = (*((short *)camry_host_ptr((uint32_t)(puVar13 + uVar16 * 8 + -0x173c))));
      uVar15 = uVar16 - uVar11 & 0xffff;
      if (((bVar7 & bVar8) != 0) && ((bVar6 & bVar8) == 0)) {
        uVar14 = call_interrupt_guard_and_return_zero_7a2da();
        if (sVar9 != 0) {
          uVar1 = sVar9 + (*((short *)camry_host_ptr((uint32_t)(puVar13 + uVar15 * 2 + -0x1504)))) + 1;
          if ((*((ushort *)camry_host_ptr((uint32_t)(puVar12 + uVar15 * 2 + -0x6e22)))) < uVar1) {
            (*((ushort *)camry_host_ptr((uint32_t)(puVar12 + uVar15 * 2 + -0x6e22)))) = uVar1;
          }
        }
        ((void)(uVar14), thunk_pop_and_restore_priority_mask_stack_6a4c4());
      }
      bVar10 = bVar4 & bVar8;
      if ((bVar5 & bVar8) == 0) {
        if (bVar10 != 0) {
          uVar14 = call_interrupt_guard_and_return_zero_7a2da();
          (*((undefined2 *)camry_host_ptr((uint32_t)(puVar12 + uVar15 * 2 + -0x6e22)))) = 0;
          (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar12 + (uint32_t)(uVar16 - 0x6ec2))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar12 + (uint32_t)(uVar16 - 0x6ec2))))) & 0x7f;
          ((void)(uVar14), thunk_pop_and_restore_priority_mask_stack_6a4c4());
          ((void)(uVar16), return_only_stub_832f2());
        }
      }
      else if (bVar10 == 0) {
        uVar14 = call_interrupt_guard_and_return_zero_7a2da();
        (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar12 + (uint32_t)(uVar16 - 0x6ec2))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar12 + (uint32_t)(uVar16 - 0x6ec2))))) | 0x80;
        if (sVar9 != 0) {
          (*((short *)camry_host_ptr((uint32_t)(puVar12 + uVar15 * 2 + -0x6e22)))) =
               (*((short *)camry_host_ptr((uint32_t)(puVar13 + uVar15 * 2 + -0x155c)))) + sVar9 + 1;
        }
        ((void)(uVar14), thunk_pop_and_restore_priority_mask_stack_6a4c4());
        ((void)(uVar16), return_only_stub_832f0());
      }
    }
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe4a46u + (uint32_t)(param_1) * 1u)))) = bVar7;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe4a42u + (uint32_t)(param_1) * 1u)))) = bVar5;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar12 + (uint32_t)(param_1 - 0x6dbc))))) = uVar3;
  return;
}

void tick_com_group_pdu_timers_and_report_expirations_7d52c(void)

{
  uint uVar1;
  byte bVar2;
  ushort uVar3;
  uint32_t puVar4;
  uint32_t puVar5;
  undefined4 uVar6;
  uint uVar7;
  uint uVar8;
  short *psVar9;
  uint uVar10;
  short sVar11;
  uint uVar12;
  uint uVar13;
  
  puVar4 = 0xfebeb800u;
  puVar5 = 0x23dfcu;
  uVar7 = (uint)DAT_00021c6e;
  uVar10 = 0;
  uVar12 = 0;
  do {
    if (uVar7 <= uVar12) {
      if (uVar10 != 0) {
        for (uVar7 = 0; uVar7 < uVar10; uVar7 = uVar7 + 1 & 0xffff) {
          set_tracking_flag_to_5a_8e790((*((undefined2 *)camry_host_ptr((uint32_t)(puVar4 + uVar7 * 2 + -0x6e78)))));
        }
      }
      return;
    }
    reconcile_com_group_masks_and_pdu_availability_timers_7d3f0(uVar12);
    bVar2 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(uVar12 - 0x6dbc)))));
    uVar13 = (uint)(*((ushort *)camry_host_ptr((uint32_t)(puVar5 + uVar12 * 4 + -0x1cb8))));
    uVar3 = (*((ushort *)camry_host_ptr((uint32_t)(puVar5 + -0x21a6))));
    uVar1 = (*((ushort *)camry_host_ptr((uint32_t)(puVar5 + uVar12 * 4 + -0x1cb6)))) + uVar13;
    for (; uVar13 < (uVar1 & 0xffff); uVar13 = uVar13 + 1 & 0xffff) {
      uVar8 = uVar13 - uVar3 & 0xffff;
      psVar9 = ((short *)camry_host_ptr((uint32_t)(puVar4 + uVar8 * 2 + -0x6e22)));
      if ((*((short *)camry_host_ptr((uint32_t)(puVar4 + uVar8 * 2 + -0x6e22)))) == 0) {
        if (((((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(uVar13 - 0x1cb4))))) & bVar2) != 0) &&
            (((byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(uVar13 - 0x6ec2))))) >> 1 & 1) == 0)) &&
           (sVar11 = (*((short *)camry_host_ptr((uint32_t)(puVar5 + uVar13 * 8 + -0x173c)))), sVar11 != 0)) goto LAB_0007d5d2;
      }
      else {
        sVar11 = (*((short *)camry_host_ptr((uint32_t)(puVar4 + uVar8 * 2 + -0x6e22)))) + -1;
        if ((sVar11 == 0) && (((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(uVar13 - 0x1cb4))))) & bVar2) != 0)) {
          uVar6 = call_interrupt_guard_and_return_zero_7a2da();
          (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(uVar13 - 0x6ec2))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(uVar13 - 0x6ec2))))) | 2;
          ((void)(uVar6), thunk_pop_and_restore_priority_mask_stack_6a4c4());
          (*((short *)camry_host_ptr((uint32_t)(puVar4 + uVar10 * 2 + -0x6e78)))) = (short)uVar13;
          uVar10 = uVar10 + 1 & 0xffff;
        }
LAB_0007d5d2:
        *psVar9 = sVar11;
      }
    }
    uVar12 = uVar12 + 1 & 0xff;
  } while( true );
}

void clear_com_group_pdu_timer_and_expiry_slots_7d608(uint param_1)

{
  ushort uVar1;
  int iVar2;
  short sVar3;
  ushort uVar4;
  
  sVar3 = DAT_00021c56;
  iVar2 = (param_1 & 0xff) * 4;
  uVar4 = *(ushort *)(((undefined *)camry_host_ptr((uint32_t)(0x22144u + (uint32_t)(iVar2) * 1u))));
  uVar1 = *(short *)(((undefined *)camry_host_ptr((uint32_t)(0x22146u + (uint32_t)(iVar2) * 1u)))) + uVar4;
  for (; uVar4 < uVar1; uVar4 = uVar4 + 1) {
    iVar2 = (uint)(ushort)(uVar4 - sVar3) * 2;
    *(undefined2 *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe49deu + (uint32_t)(iVar2) * 1u)))) = 0;
    *(undefined2 *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe4988u + (uint32_t)(iVar2) * 1u)))) = 0;
  }
  return;
}

void initialize_com_group_masks_from_second_input_vector_7d646(int param_1)

{
  undefined1 uVar1;
  uint uVar2;
  uint uVar3;
  
  uVar3 = (uint)DAT_00021c6e;
  for (uVar2 = 0; uVar2 < uVar3; uVar2 = uVar2 + 1 & 0xff) {
    uVar1 = (*((undefined1 *)camry_host_ptr((uint32_t)(uVar2 + uVar3 + param_1))));
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe4a43u + (uint32_t)(uVar2) * 1u)))) = 0;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe4a44u + (uint32_t)(uVar2) * 1u)))) = 0;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe4a41u + (uint32_t)(uVar2) * 1u)))) = uVar1;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe4a42u + (uint32_t)(uVar2) * 1u)))) = uVar1;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe4a45u + (uint32_t)(uVar2) * 1u)))) = 0;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe4a46u + (uint32_t)(uVar2) * 1u)))) = 0;
  }
  return;
}

void clear_committed_com_group_mask_arrays_7d67c(void)

{
  uint uVar1;
  uint uVar2;
  
  uVar2 = (uint)DAT_00021c6e;
  for (uVar1 = 0; uVar1 < uVar2; uVar1 = uVar1 + 1 & 0xff) {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe4a42u + (uint32_t)(uVar1) * 1u)))) = 0;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe4a44u + (uint32_t)(uVar1) * 1u)))) = 0;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe4a46u + (uint32_t)(uVar1) * 1u)))) = 0;
  }
  return;
}

void copy_second_group_vector_to_active_timer_masks_7d69e(int param_1)

{
  uint uVar1;
  uint uVar2;
  
  uVar2 = (uint)DAT_00021c6e;
  for (uVar1 = 0; uVar1 < uVar2; uVar1 = uVar1 + 1 & 0xff) {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe4a43u + (uint32_t)(uVar1) * 1u)))) = (*((undefined1 *)camry_host_ptr((uint32_t)(uVar2 + uVar1 + param_1))));
  }
  return;
}

void copy_second_group_vector_to_timer_transition_requests_7d6c2(int param_1)

{
  uint uVar1;
  uint uVar2;
  
  uVar2 = (uint)DAT_00021c6e;
  for (uVar1 = 0; uVar1 < uVar2; uVar1 = uVar1 + 1 & 0xff) {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe4a45u + (uint32_t)(uVar1) * 1u)))) = (*((undefined1 *)camry_host_ptr((uint32_t)(uVar2 + uVar1 + param_1))));
  }
  return;
}

undefined4 extend_com_pdu_timer_by_configured_period_plus_delta_7d6e6(uint param_1,ushort param_2)

{
  ushort uVar1;
  uint32_t puVar2;
  uint32_t puVar3;
  undefined4 uVar4;
  
  puVar2 = 0xfebeb800u;
  puVar3 = 0x23dfcu;
  uVar4 = call_interrupt_guard_and_return_zero_7a2da();
  uVar1 = *(short *)(((undefined *)camry_host_ptr((uint32_t)(0x226c0u + (uint32_t)((param_1 & 0xffff) * 8) * 1u)))) + param_2;
  if ((param_2 < uVar1) &&
     ((*((ushort *)camry_host_ptr((uint32_t)(puVar2 + ((param_1 & 0xffff) - (uint)(*((volatile ushort *)camry_host_ptr((uint32_t)(0x23dfcu + (uint32_t)(-0x21a6) * 1u)))) & 0xffff) * 2 + -0x6e22))))
      < uVar1)) {
    (*((ushort *)camry_host_ptr((uint32_t)(puVar2 + ((param_1 & 0xffff) - (uint)(*((volatile ushort *)camry_host_ptr((uint32_t)(0x23dfcu + (uint32_t)(-0x21a6) * 1u)))) & 0xffff) * 2 + -0x6e22)))) =
         uVar1;
  }
  ((void)(uVar4), thunk_pop_and_restore_priority_mask_stack_6a4c4());
  return 0;
}

void copy_received_com_pdu_and_refresh_status_timer_7d72c(uint param_1,int *param_2)

{
  uint8_t stack_record_1e[30];
  byte *pbVar1;
  byte bVar2;
  ushort uVar3;
  uint uVar4;
  uint uVar5;
  int iVar6;
  undefined8 uVar7;
  undefined4 uVar8;
  int iVar9;
  int iVar10;
  undefined4 uVar11;
  
  uVar7 = 0x23dfcfebeb800;
  param_1 = param_1 & 0xffff;
  bVar2 = (*((byte *)camry_host_ptr((uint32_t)(&PTR_DAT_000226c7 + param_1 * 2))));
  if ((bVar2 >> 4 & 1) != 0) {
    uVar8 = (*(int (*)())camry_indirect((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x21c4cu + (uint32_t)((byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x226c2u + (uint32_t)(param_1 * 8) * 1u))))) * 4u))))))(param_1,camry_host_addr(param_2),camry_host_addr(stack_record_1e),camry_host_addr((stack_record_1e + 1)));
    iVar9 = ((void)(param_1), (void)(uVar8), (void)(stack_record_1e[0]), (void)(stack_record_1e[1]), return_const_1_833e0());
    if (iVar9 != 1) {
      return;
    }
  }
  iVar9 = *param_2;
  if (((bVar2 >> 3 & 1) == 0) || (iVar10 = ((void)(param_1), (void)(param_2), return_const_1_7d800()), iVar10 == 1))
  {
    iVar10 = (int)uVar7;
    uVar3 = (*((ushort *)camry_host_ptr((uint32_t)(param_1 * 2 + (int)((ulonglong)uVar7 >> 0x20) + -0x15bc))));
    uVar4 = (uint)*(ushort *)(((undefined *)camry_host_ptr((uint32_t)(0x226c4u + (uint32_t)(param_1 * 8) * 1u))));
    if (*(ushort *)(param_2 + 1) <= uVar4) {
      uVar4 = (uint)*(ushort *)(param_2 + 1);
    }
    uVar8 = thunk_call_interrupt_guard_and_return_zero_7a2da();
    iVar6 = (int)uVar7;
    for (uVar5 = 0; uVar5 < uVar4; uVar5 = uVar5 + 1 & 0xffff) {
      (*((undefined1 *)camry_host_ptr((uint32_t)(uVar5 + (uint)uVar3 + iVar10 + -0x6db8)))) = (*((undefined1 *)camry_host_ptr((uint32_t)(uVar5 + iVar9))));
    }
    uVar11 = call_interrupt_guard_and_return_zero_7a2da();
    extend_com_pdu_timer_by_configured_period_plus_delta_7d6e6(param_1,1);
    pbVar1 = ((byte *)camry_host_ptr((uint32_t)(iVar6 + -0x6ec2 + param_1)));
    *pbVar1 = *pbVar1 & 0xdc;
    ((void)(uVar11), thunk_pop_and_restore_priority_mask_stack_6a4c4());
    ((void)(uVar8), thunk_pop_and_restore_priority_mask_stack_6a4c4());
    if ((bVar2 >> 2 & 1) != 0) {
      clear_tracking_flag_and_increment_counter_8e772(param_1);
    }
  }
  return;
}

undefined4 return_const_1_7d800(void)

{
  return 1;
}

void initialize_com_group_state_buffers_and_callbacks_7d804(short param_1)

{
  byte bVar1;
  uint uVar2;
  undefined8 uVar3;
  int iVar4;
  byte bVar5;
  undefined1 local_2c [32];
  
  bVar1 = DAT_00021c6e;
  uVar3 = 0x23dfc00000000;
  uVar2 = 0;
  do {
    local_2c[uVar2] = 0;
    uVar2 = uVar2 + 1;
  } while (uVar2 < 0x20);
  if (param_1 == 4) {
    initialize_paired_inverted_channel_masks_8317e(camry_host_addr(local_2c));
  }
  initialize_tx_groups_from_mask_bytes_7e380(camry_host_addr(local_2c));
  initialize_com_group_masks_from_second_input_vector_7d646(camry_host_addr(local_2c));
  initialize_com_tx_pdu_flags_by_mode_832f4(param_1);
  set_com_state_4a47_a5_833cc();
  initialize_tx_inhibit_and_pending_pairs_7e312();
  for (bVar5 = 0; iVar4 = (int)((ulonglong)uVar3 >> 0x20), bVar5 < bVar1; bVar5 = bVar5 + 1) {
    zero_group_tx_period_countdowns_7e2ea(bVar5);
    clear_com_group_pdu_timer_and_expiry_slots_7d608(bVar5);
  }
  zero_all_tx_minimum_delay_countdowns_7e364();
  (*(int (*)())camry_indirect((uint32_t)(((((code *)(uintptr_t)((uint32_t)((uintptr_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(iVar4 + -0x21fc))))))))))))();
  (*(int (*)())camry_indirect((uint32_t)(((((code *)(uintptr_t)((uint32_t)((uintptr_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(iVar4 + -0x21f8))))))))))))();
  (*(int (*)())camry_indirect((uint32_t)(((((code *)(uintptr_t)((uint32_t)((uintptr_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(iVar4 + -0x2200))))))))))))();
  set_tx_group_modes_two_7e33e();
  return;
}

void initialize_com_state_with_mode_one_7d880(void)

{
  initialize_com_group_state_buffers_and_callbacks_7d804(1);
  return;
}

void reset_com_group_modes_and_committed_masks_7d88e(void)

{
  reset_tx_group_modes_and_pending_masks_7e3bc();
  clear_committed_com_group_mask_arrays_7d67c();
  return;
}

void initialize_com_state_with_mode_20_7d89e(void)

{
  initialize_com_group_state_buffers_and_callbacks_7d804(0x20);
  return;
}

void apply_com_tx_group_transition(uchar group)

{
  uint uVar1;
  int iVar2;
  byte bVar3;
  byte bVar4;
  char cVar5;
  byte bVar6;
  short sVar7;
  short sVar8;
  short sVar9;
  byte bVar10;
  byte bVar11;
  uint32_t puVar12;
  uint32_t puVar13;
  uint uVar14;
  undefined4 uVar15;
  short *psVar16;
  uint uVar17;
  uint uVar18;
  
  puVar12 = 0xfebeb800u;
  puVar13 = 0x23dfcu;
  uVar14 = (uint)group;
  iVar2 = uVar14 * 2;
  bVar3 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe4a39u + (uint32_t)(uVar14 + 3) * 1u))));
  bVar4 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe4a39u + (uint32_t)(uVar14 + 2) * 1u))));
  sVar7 = *(short *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe4986u + (uint32_t)(iVar2) * 1u))));
  cVar5 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe4a3fu + (uint32_t)(uVar14) * 1u))));
  if ((bVar3 != bVar4) || (cVar5 == '\x01')) {
    uVar18 = (uint)*(ushort *)(((undefined *)camry_host_ptr((uint32_t)(0x22140u + (uint32_t)(uVar14 * 4) * 1u))));
    uVar1 = *(ushort *)(((undefined *)camry_host_ptr((uint32_t)(0x22142u + (uint32_t)(uVar14 * 4) * 1u)))) + uVar18;
    sVar8 = *(short *)(((undefined *)camry_host_ptr((uint32_t)(0x21c5cu + (uint32_t)(iVar2) * 1u))));
    for (; uVar18 < (uVar1 & 0xffff); uVar18 = uVar18 + 1 & 0xffff) {
      bVar6 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar13 + (uint32_t)(uVar18 * 8 + -0x1736)))));
      psVar16 = ((short *)camry_host_ptr((uint32_t)(puVar13 + uVar18 * 8 + -0x173c)));
      bVar10 = bVar4 & (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar13 + (uint32_t)(uVar18 - 0x1cb4)))));
      bVar11 = bVar3 & (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar13 + (uint32_t)(uVar18 - 0x1cb4)))));
      if (bVar10 == 0) {
        if (bVar11 != 0) {
          (*(int (*)())camry_indirect((uint32_t)(((((code *)(uintptr_t)((uint32_t)((uintptr_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(puVar13 + -0x21f0))))))))))))(uVar18);
          uVar17 = uVar18 >> 3 & 0xff;
          bVar11 = (byte)(1 << (uVar18 & 7)) ^ 0xff;
          uVar15 = call_interrupt_guard_and_return_zero_7a2da();
          (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar12 + (uint32_t)(uVar17 - 0x6dc7))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar12 + (uint32_t)(uVar17 - 0x6dc7))))) & bVar11;
          (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar12 + (uint32_t)(uVar17 - 0x6dc6))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar12 + (uint32_t)(uVar17 - 0x6dc6))))) & bVar11;
          (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar12 + (uint32_t)(uVar18 - 0x6ec2))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar12 + (uint32_t)(uVar18 - 0x6ec2))))) & 0x3b;
          (*((undefined2 *)camry_host_ptr((uint32_t)(puVar12 + uVar18 * 2 + -0x6e92)))) = 0;
          (*((undefined2 *)camry_host_ptr((uint32_t)(puVar12 + uVar18 * 2 + -0x6e88)))) = 0;
          if ((bVar6 >> 3 & 1) != 0) {
            (*(int (*)())camry_indirect((uint32_t)(((((code *)(uintptr_t)((uint32_t)((uintptr_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(puVar13 + -0x21cc))))))))))))(uVar18);
          }
          ((void)(uVar15), thunk_pop_and_restore_priority_mask_stack_6a4c4());
          ((void)(uVar18), return_only_stub_832f2());
        }
      }
      else if (bVar11 == 0) {
        uVar17 = uVar18 >> 3 & 0xff;
        bVar11 = (byte)(1 << (uVar18 & 7)) ^ 0xff;
        uVar15 = call_interrupt_guard_and_return_zero_7a2da();
        (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar12 + (uint32_t)(uVar17 - 0x6dc7))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar12 + (uint32_t)(uVar17 - 0x6dc7))))) & bVar11;
        sVar9 = *psVar16;
        (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar12 + (uint32_t)(uVar17 - 0x6dc6))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar12 + (uint32_t)(uVar17 - 0x6dc6))))) & bVar11;
        (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar12 + (uint32_t)(uVar18 - 0x6ec2))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar12 + (uint32_t)(uVar18 - 0x6ec2))))) | 0x84;
        if (sVar9 != 0) {
          (*((short *)camry_host_ptr((uint32_t)(puVar12 + uVar18 * 2 + -0x6e92)))) =
               (*((short *)camry_host_ptr((uint32_t)(puVar13 + uVar18 * 2 + -0x1c84)))) + sVar8 + 1;
        }
        (*((short *)camry_host_ptr((uint32_t)(puVar12 + uVar18 * 2 + -0x6e88)))) = sVar8 + 1;
        if ((bVar6 >> 3 & 1) != 0) {
          (*(int (*)())camry_indirect((uint32_t)(((((code *)(uintptr_t)((uint32_t)((uintptr_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(puVar13 + -0x21cc))))))))))))(uVar18);
        }
        ((void)(uVar15), thunk_pop_and_restore_priority_mask_stack_6a4c4());
        ((void)(uVar18), return_only_stub_832f0());
      }
      if ((cVar5 == '\x01') && (bVar10 != 0)) {
        sVar9 = *psVar16;
        uVar15 = call_interrupt_guard_and_return_zero_7a2da();
        bVar6 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar12 + (uint32_t)(uVar18 - 0x6ec2)))));
        if ((sVar9 != 0) && ((bVar6 >> 2 & 1) == 0)) {
          (*((short *)camry_host_ptr((uint32_t)(puVar12 + uVar18 * 2 + -0x6e92)))) =
               (*((short *)camry_host_ptr((uint32_t)(puVar13 + uVar18 * 2 + -0x1c84)))) + sVar7 + 1;
          (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar12 + (uint32_t)(uVar18 - 0x6ec2))))) = bVar6 | 0x40;
        }
        ((void)(uVar15), thunk_pop_and_restore_priority_mask_stack_6a4c4());
      }
    }
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe4a39u + (uint32_t)(uVar14 + 3) * 1u)))) = bVar4;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe4a3fu + (uint32_t)(uVar14) * 1u)))) = 0;
  *(undefined2 *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe4986u + (uint32_t)(iVar2) * 1u)))) = 0;
  return;
}

undefined4 set_com_pending_bitmap_bit_by_boolean_bank_7dab6(uint param_1,char param_2)

{
  uchar *puVar1;
  
  if (param_2 == '\0') {
    puVar1 = ((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe4a39u + (uint32_t)(1) * 1u)));
  }
  else {
    puVar1 = com_tx_pending_and_group_state;
  }
  puVar1[param_1 >> 3 & 0xff] = puVar1[param_1 >> 3 & 0xff] | (byte)(1 << (param_1 & 7));
  return 0;
}

uint return_u16_pdu_length_through_optional_group_gate_7dae0(uint param_1,uint param_2,uint param_3)

{
  param_3 = param_3 & 0xffff;
  if ((((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x226c6u + (uint32_t)((param_2 & 0xffff) * 8) * 1u)))) & 4) != 0) &&
     ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe4a39u + (uint32_t)((param_1 & 0xff) + 5) * 1u)))) == '\x01')) {
    param_3 = return_third_argument_u16_7e4e0((uint)(byte)param_1, (uint)(ushort)param_2, (uint)(ushort)param_3);
  }
  return param_3;
}

void service_com_tx_countdowns(void)

{
  uint uVar1;
  byte bVar2;
  char cVar3;
  char cVar4;
  byte bVar5;
  uint32_t puVar6;
  uint32_t puVar7;
  short sVar8;
  undefined4 uVar9;
  uint uVar10;
  int iVar11;
  int iVar12;
  short *psVar13;
  short *psVar14;
  uint uVar15;
  uint uVar16;
  bool bVar17;
  
  cVar4 = DAT_00021c6f;
  puVar6 = 0xfebeb800u;
  puVar7 = 0x23dfcu;
  uVar10 = (uint)DAT_00021c6e;
  uVar15 = 0;
  do {
    if (uVar10 <= uVar15) {
      (*(int (*)())camry_indirect((uint32_t)(((((code *)(uintptr_t)((uint32_t)((uintptr_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(puVar7 + -0x21e0))))))))))))();
      (*(int (*)())camry_indirect((uint32_t)(((((code *)(uintptr_t)((uint32_t)((uintptr_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(puVar7 + -0x21c8))))))))))))();
      return;
    }
    uVar16 = (uint)(*((ushort *)camry_host_ptr((uint32_t)(puVar7 + uVar15 * 4 + -0x1cbc))));
    uVar1 = (*((ushort *)camry_host_ptr((uint32_t)(puVar7 + uVar15 * 4 + -0x1cba)))) + uVar16;
    bVar2 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(uVar15 - 0x6dc4)))));
    cVar3 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(uVar15 - 0x6dc2)))));
    for (; uVar16 < (uVar1 & 0xffff); uVar16 = uVar16 + 1 & 0xffff) {
      iVar12 = uVar16 * 2;
      psVar13 = ((short *)camry_host_ptr((uint32_t)(puVar6 + iVar12 + -0x6e88)));
      if ((*((short *)camry_host_ptr((uint32_t)(puVar6 + iVar12 + -0x6e88)))) != 0) {
        sVar8 = (*((short *)camry_host_ptr((uint32_t)(puVar6 + iVar12 + -0x6e88)))) + -1;
        if (sVar8 == 0) {
          uVar9 = call_interrupt_guard_and_return_zero_7a2da();
          bVar5 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(uVar16 - 0x6ec2)))));
          if ((bVar5 >> 2 & 1) != 0) {
            bVar5 = bVar5 & 0xfb;
            if ((*((short *)camry_host_ptr((uint32_t)(puVar7 + uVar16 * 8 + -0x173c)))) != 0) {
              bVar5 = bVar5 | 0x40;
              (*((short *)camry_host_ptr((uint32_t)(puVar6 + iVar12 + -0x6e92)))) = (*((short *)camry_host_ptr((uint32_t)(puVar7 + iVar12 + -0x1c84)))) + 1;
            }
            (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(uVar16 - 0x6ec2))))) = bVar5;
          }
          ((void)(uVar9), thunk_pop_and_restore_priority_mask_stack_6a4c4());
          sVar8 = (*(int (*)())camry_indirect((uint32_t)(((((code *)(uintptr_t)((uint32_t)((uintptr_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(puVar7 + -0x21e4))))))))))))(uVar16);
        }
        *psVar13 = sVar8;
      }
      sVar8 = (*((short *)camry_host_ptr((uint32_t)(puVar6 + iVar12 + -0x6e92))));
      psVar13 = ((short *)camry_host_ptr((uint32_t)(puVar6 + iVar12 + -0x6e92)));
      if (sVar8 != 0) {
        if (sVar8 == 1) {
          sVar8 = 0;
          if (((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar7 + (uint32_t)(uVar16 - 0x1cb4))))) & bVar2) != 0) {
            iVar12 = -0xd;
            psVar14 = ((short *)camry_host_ptr((uint32_t)(puVar7 + uVar16 * 8 + -0x173c)));
            if (((byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar7 + (uint32_t)(uVar16 * 8 + -0x1736))))) >> 4 & 1) != 0) {
              iVar12 = (*(int (*)())camry_indirect((uint32_t)(((((code *)(uintptr_t)((uint32_t)((uintptr_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(puVar7 + -0x21bc))))))))))))(uVar16);
            }
            sVar8 = *psVar14;
            uVar9 = call_interrupt_guard_and_return_zero_7a2da();
            bVar5 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(uVar16 - 0x6ec2)))));
            if ((bVar5 >> 6 & 1) == 0) {
              if ((bVar5 >> 2 & 1) == 0) {
                bVar17 = cVar3 == '\x01';
                goto LAB_0007dc2c;
              }
            }
            else {
              iVar11 = -0x15;
              if (cVar3 == '\x01') {
                iVar11 = 0;
              }
              (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(uVar16 - 0x6ec2))))) = bVar5 & 0xbf;
              bVar17 = iVar11 == 0;
LAB_0007dc2c:
              if ((bVar17) && (iVar12 == -0xd)) {
                set_com_pending_bitmap_bit_by_boolean_bank_7dab6(uVar16,1);
              }
            }
            ((void)(uVar9), thunk_pop_and_restore_priority_mask_stack_6a4c4());
            if ((cVar4 == '\0') && ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(uVar15 - 0x6dc9))))) == '\x01')) {
              sVar8 = (*((short *)camry_host_ptr((uint32_t)(puVar7 + uVar15 * 2 + -0x21a4))));
            }
            if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar7 + (uint32_t)(uVar15 - 0x2186))))) == '\x03') {
              sVar8 = return_u16_pdu_length_through_optional_group_gate_7dae0(uVar15,uVar16,sVar8);
            }
          }
        }
        else {
          sVar8 = sVar8 + -1;
        }
        *psVar13 = sVar8;
      }
    }
    uVar15 = uVar15 + 1 & 0xff;
  } while( true );
}

int select_admissible_com_tx(uchar group,ushort *selected_pdu)

{
  short sVar1;
  ushort uVar2;
  byte bVar3;
  uchar uVar4;
  uchar uVar5;
  uint32_t puVar6;
  uint32_t puVar7;
  uint uVar8;
  int iVar9;
  uint uVar10;
  undefined1 uVar11;
  uint uVar12;
  
  puVar6 = 0xfebeb800u;
  puVar7 = 0x23dfcu;
  uVar8 = (uint)group;
  iVar9 = -0x14;
  uVar11 = 0;
  uVar12 = (uint)*(ushort *)(((undefined *)camry_host_ptr((uint32_t)(0x22140u + (uint32_t)(uVar8 * 4) * 1u))));
  sVar1 = *(short *)(((undefined *)camry_host_ptr((uint32_t)(0x22142u + (uint32_t)(uVar8 * 4) * 1u))));
  uVar2 = *(ushort *)(((undefined *)camry_host_ptr((uint32_t)(0x22140u + (uint32_t)(uVar8 * 4) * 1u))));
  bVar3 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe4a39u + (uint32_t)(uVar8 + 3) * 1u))));
  uVar4 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe4a39u + (uint32_t)(uVar8 + 4) * 1u))));
  uVar5 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe4a39u + (uint32_t)(uVar8 + 5) * 1u))));
  do {
    if ((ushort)(sVar1 + uVar2) <= uVar12) {
      return iVar9;
    }
    uVar8 = uVar12 >> 3 & 0xff;
    uVar10 = 1 << (uVar12 & 7) & 0xff;
    if ((uVar5 == '\x01') && (((byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(uVar8 - 0x6dc7))))) & uVar10) != 0)) {
      uVar11 = 0x40;
      iVar9 = 1;
    }
    if ((uVar4 == '\x01') && (((byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(uVar8 - 0x6dc6))))) & uVar10) != 0)) {
      uVar11 = 0x80;
      iVar9 = 2;
LAB_0007dd18:
      if (((*((short *)camry_host_ptr((uint32_t)(puVar6 + uVar12 * 2 + -0x6e88)))) == 0) &&
         (((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar7 + (uint32_t)(uVar12 - 0x1cb4))))) & bVar3) != 0)) {
        if (((byte)((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(uVar8 - 0x6dcb))))) ^ (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(uVar8 - 0x6dcc)))))) & uVar10) == 0) {
          set_com_state_4a47_5a_833d6();
        }
        else if ((uVar10 & (byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(uVar8 - 0x6dcc)))))) == 0) {
          *selected_pdu = (ushort)uVar12;
          (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(-0x684f))))) = uVar11;
          return iVar9;
        }
      }
      iVar9 = -0x14;
    }
    else if (iVar9 != -0x14) goto LAB_0007dd18;
    uVar12 = uVar12 + 1 & 0xffff;
  } while( true );
}

void reload_tx_minimum_delay_if_configured_7dd64(uint param_1,char param_2)

{
  ushort uVar1;
  
  param_1 = param_1 & 0xffff;
  uVar1 = 0;
  if ((DAT_00021c74 != '\0') || (uVar1 = *(ushort *)(((undefined *)camry_host_ptr((uint32_t)(0x21c64u + (uint32_t)(param_1 * 2) * 1u)))), uVar1 == 0)) {
    if (((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x226c6u + (uint32_t)(param_1 * 8) * 1u)))) & 1) == 0) {
      return;
    }
    if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x21c77u + (uint32_t)((byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x226c2u + (uint32_t)(param_1 * 8) * 1u))))) * 1u)))) != '\x01') {
      return;
    }
    if (((param_2 == -0x80) || ((param_2 == '@' && (DAT_00021c71 == '\0')))) &&
       (uVar1 = DAT_00021c5a, DAT_00021c72 != '\x01')) {
      uVar1 = *(ushort *)(((undefined *)camry_host_ptr((uint32_t)(0x21c60u + (uint32_t)(param_1 * 2) * 1u))));
    }
    if (uVar1 == 0) {
      return;
    }
  }
  (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe4978u + (uint32_t)(param_1) * 2u)))) = uVar1;
  return;
}

undefined4 reload_tx_period_with_offset_7ddd8(uint param_1,short param_2,char param_3)

{
  char cVar1;
  uint32_t puVar2;
  uint32_t puVar3;
  short sVar4;
  undefined4 uVar5;
  uint uVar6;
  
  cVar1 = DAT_00021c6f;
  puVar2 = 0xfebeb800u;
  puVar3 = 0x23dfcu;
  param_1 = param_1 & 0xffff;
  uVar6 = (uint)(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x226c2u + (uint32_t)(param_1 * 8) * 1u))));
  uVar5 = call_interrupt_guard_and_return_zero_7a2da();
  sVar4 = *(short *)(((undefined *)camry_host_ptr((uint32_t)(0x226c0u + (uint32_t)(param_1 * 8) * 1u))));
  if (sVar4 != 0) {
    if ((cVar1 == '\0') && ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(uVar6 - 0x6dc9))))) == '\x01')) {
      sVar4 = (*((short *)camry_host_ptr((uint32_t)(puVar3 + uVar6 * 2 + -0x21a4))));
    }
    if (param_3 == '\x01') {
      sVar4 = return_u16_pdu_length_through_optional_group_gate_7dae0(uVar6,param_1,(uint)(ushort)sVar4);
    }
    (*((short *)camry_host_ptr((uint32_t)(puVar2 + param_1 * 2 + -0x6e92)))) = param_2 + sVar4;
    if (((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(param_1 - 0x6ec2))))) & 0x40) != 0) {
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(param_1 - 0x6ec2))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(param_1 - 0x6ec2))))) & 0xbf;
    }
  }
  ((void)(uVar5), thunk_pop_and_restore_priority_mask_stack_6a4c4());
  return 0;
}

void reload_tx_period_by_group_mode_7de52(uint param_1,char param_2)

{
  char cVar1;
  short sVar2;
  
  param_1 = param_1 & 0xffff;
  sVar2 = 0;
  if (param_2 == '@') {
    cVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x21c76u + (uint32_t)((byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x226c2u + (uint32_t)(param_1 * 8) * 1u))))) * 1u))));
  }
  else {
    cVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x21c78u + (uint32_t)((byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x226c2u + (uint32_t)(param_1 * 8) * 1u))))) * 1u))));
  }
  if (cVar1 != '\x01') {
    if (cVar1 != '\x02') {
      return;
    }
    sVar2 = *(short *)(((undefined *)camry_host_ptr((uint32_t)(0x21c64u + (uint32_t)(param_1 * 2) * 1u))));
  }
  reload_tx_period_with_offset_7ddd8(param_1,sVar2,sVar2 == 0);
  return;
}

void reload_tx_delays_and_notify_flags_7de9e(uint param_1,undefined1 param_2)

{
  byte bVar1;
  uint32_t puVar2;
  puVar2 = 0x23dfcu;
  param_1 = param_1 & 0xffff;
  reload_tx_minimum_delay_if_configured_7dd64((uint)(ushort)param_1, (uint)(byte)param_2);
  reload_tx_period_by_group_mode_7de52(param_1,param_2);
  bVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(param_1 * 8 + -0x1736)))));
  if ((bVar1 >> 3 & 1) != 0) {
    (*(int (*)())camry_indirect((uint32_t)(((((code *)(uintptr_t)((uint32_t)((uintptr_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(puVar2 + -0x21d8))))))))))))(param_1,param_2);
  }
  if ((bVar1 >> 4 & 1) != 0) {
    (*(int (*)())camry_indirect((uint32_t)(((((code *)(uintptr_t)((uint32_t)((uintptr_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(puVar2 + -0x21c4))))))))))))(param_1,param_2);
  }
  return;
}

void clear_tx_pending_bit_pair_7dee6(uint param_1)

{
  byte bVar1;
  uint uVar2;
  
  uVar2 = param_1 >> 3 & 0xff;
  bVar1 = (byte)(1 << (param_1 & 7)) ^ 0xff;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe4a39u + (uint32_t)(uVar2) * 1u)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe4a39u + (uint32_t)(uVar2) * 1u)))) & bVar1;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe4a39u + (uint32_t)(uVar2 + 1) * 1u)))) =
       (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe4a39u + (uint32_t)(uVar2 + 1) * 1u)))) & bVar1;
  return;
}

int dispatch_one_com_tx(uchar group)

{
  uchar *puVar1;
  byte bVar2;
  uint uVar3;
  uint32_t puVar4;
  uint32_t puVar5;
  uint32_t puVar6;
  uint uVar7;
  undefined4 uVar8;
  int iVar9;
  int iVar10;
  uint uVar11;
  uint uVar12;
  ushort uStack_26;
  F33PduInfo FStack_24;
  
  uVar7 = (uint)group;
  puVar4 = 0xfebeb800u;
  puVar5 = 0x23dfcu;
  uVar8 = call_interrupt_guard_and_return_zero_7a2da();
  iVar9 = select_admissible_com_tx(group,&uStack_26);
  ((void)(uVar8), thunk_pop_and_restore_priority_mask_stack_6a4c4());
  if (iVar9 == -0x14) {
    return -0x14;
  }
  uVar12 = (uint)uStack_26;
  FStack_24.length = (*((ushort *)camry_host_ptr((uint32_t)(puVar5 + uVar12 * 8 + -0x1738))));
  uVar11 = (uint)FStack_24.length;
  bVar2 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(uVar12 * 8 + -0x1735)))));
  puVar1 = ((undefined *)camry_host_ptr((uint32_t)(puVar4 + ((*((ushort *)camry_host_ptr((uint32_t)(puVar5 + uVar12 * 2 + -0x15bc)))) - 0x6db8))));
  puVar6 = ((uint32_t)(puVar5));
  FStack_24.data = camry_host_addr(puVar1);
  if ((bVar2 >> 5 & 1) == 0) {
LAB_0007dfa8:
    uVar11 = route_com_tx(uStack_26,&FStack_24);
    if (uVar11 == 2) {
      iVar9 = -0x13;
      goto LAB_0007e03c;
    }
  }
  else {
    uVar8 = thunk_call_interrupt_guard_and_return_zero_7a2da();
    for (uVar3 = 0; uVar3 < uVar11; uVar3 = uVar3 + 1 & 0xffff) {
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(uVar3 - 0x6dc0))))) = puVar1[uVar3];
    }
    ((void)(uVar8), thunk_pop_and_restore_priority_mask_stack_6a4c4());
    FStack_24.data = puVar4 + -0x6dc0;
    iVar10 = ((void)(uStack_26), (void)(&FStack_24), return_const_1_7e77e());
    if (iVar10 == 1) goto LAB_0007dfa8;
    uVar11 = 1;
  }
  iVar10 = 0x40;
  if (iVar9 == 2) {
    iVar10 = 0x80;
  }
  if (uVar11 == 0) {
    if ((bVar2 >> 4 & 1) != 0) {
      (*(int (*)())camry_indirect((uint32_t)(((((code *)(uintptr_t)((uint32_t)((uintptr_t)(*((volatile uint32_t *)(((undefined *)camry_host_ptr((uint32_t)(0x23dfcu + (uint32_t)(uVar7 * 4 + -0x21f4) * 1u))))))))))))))(uStack_26,camry_host_addr(&FStack_24));
    }
    reload_tx_delays_and_notify_flags_7de9e(uStack_26,iVar10);
    if ((iVar10 == 0x80) && (((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(uVar12 * 8 + -0x1736))))) & 2) != 0)) {
      (*(int (*)())camry_indirect((uint32_t)(((((code *)(uintptr_t)((uint32_t)((uintptr_t)(*((volatile uint32_t *)(((undefined *)camry_host_ptr((uint32_t)(0x23dfcu + (uint32_t)(-0x21b8) * 1u))))))))))))))(uVar7);
    }
    (*(int (*)())camry_indirect((uint32_t)(((((code *)(uintptr_t)((uint32_t)((uintptr_t)(*((volatile uint32_t *)(((undefined *)camry_host_ptr((uint32_t)(0x23dfcu + (uint32_t)(-0x21ec) * 1u))))))))))))))(uStack_26,iVar10);
  }
  uVar8 = call_interrupt_guard_and_return_zero_7a2da();
  clear_tx_pending_bit_pair_7dee6(uStack_26);
  ((void)(uVar8), thunk_pop_and_restore_priority_mask_stack_6a4c4());
  if ((bVar2 & 1) != 0) {
    ((void)(uVar7), (void)(uStack_26), (void)(iVar10), return_only_stub_7e4e6());
  }
LAB_0007e03c:
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x684f))))) = 0;
  return iVar9;
}
