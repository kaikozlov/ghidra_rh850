#include "common.h"

void clear_group_tx_pending_bit_ranges_7e046(uint param_1,uint param_2)

{
  uint uVar1;
  int iVar2;
  ushort uVar3;
  char cVar4;
  uint32_t puVar5;
  undefined4 uVar6;
  byte bVar7;
  uint uVar8;
  uint uVar9;
  uint uVar10;
  uint uVar11;
  
  puVar5 = 0xfebeb800u;
  uVar8 = param_2 & 0xff;
  iVar2 = (param_1 & 0xff) * 4;
  uVar3 = *(ushort *)(((undefined *)camry_host_ptr((uint32_t)(0x22140u + (uint32_t)(iVar2) * 1u))));
  uVar10 = (uint)*(ushort *)(((undefined *)camry_host_ptr((uint32_t)(0x22142u + (uint32_t)(iVar2) * 1u))));
  uVar9 = uVar3 & 7;
  uVar11 = uVar3 >> 3 & 0xff;
  if (uVar10 != 0) {
    uVar1 = uVar10 + uVar9;
    uVar6 = call_interrupt_guard_and_return_zero_7a2da();
    if ((uVar3 & 7) != 0) {
      cVar4 = -1;
      if ((uVar1 & 0xffff) < 8) {
        cVar4 = (char)(1 << (uVar1 & 0x1f)) + -1;
      }
      bVar7 = cVar4 - ((char)(1 << uVar9) + -1) ^ 0xff;
      if ((uVar8 >> 6 & 1) != 0) {
        (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(uVar11 - 0x6dc7))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(uVar11 - 0x6dc7))))) & bVar7;
      }
      if (uVar8 >> 7 != 0) {
        (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(uVar11 - 0x6dc6))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(uVar11 - 0x6dc6))))) & bVar7;
      }
      uVar11 = uVar11 + 1 & 0xff;
    }
    uVar10 = uVar10 + uVar3;
    uVar9 = uVar10 - 1 >> 3 & 0xff;
    if (uVar11 <= uVar9) {
      uVar10 = uVar10 & 7;
      bVar7 = 0;
      if (uVar10 != 0) {
        bVar7 = (char)(1 << uVar10) - 1U ^ 0xff;
      }
      if ((param_2 & 0x40) != 0) {
        (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(uVar9 - 0x6dc7))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(uVar9 - 0x6dc7))))) & bVar7;
      }
      if ((param_2 & 0x80) != 0) {
        (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(uVar9 - 0x6dc6))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(uVar9 - 0x6dc6))))) & bVar7;
      }
      for (; uVar11 < uVar9; uVar11 = uVar11 + 1 & 0xff) {
        if ((param_2 & 0x40) != 0) {
          (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(uVar11 - 0x6dc7))))) = 0;
        }
        if ((param_2 & 0x80) != 0) {
          (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(uVar11 - 0x6dc6))))) = 0;
        }
      }
    }
    ((void)(uVar6), thunk_pop_and_restore_priority_mask_stack_6a4c4());
  }
  ((void)(param_1 & 0xff), (void)(uVar8), return_only_stub_7e718());
  return;
}

void service_com_tx_publication(void)

{
  ushort uVar1;
  undefined8 uVar2;
  int iVar3;
  uint uVar4;
  ushort uVar5;
  uint uVar6;
  
  uVar2 = 0x23dfc00000000;
  uVar4 = (uint)DAT_00021c6e;
  for (uVar6 = 0; uVar6 < uVar4; uVar6 = uVar6 + 1 & 0xff) {
    apply_com_tx_group_transition((uchar)uVar6);
  }
  service_com_tx_countdowns();
  uVar6 = 0;
  do {
    if (uVar4 <= uVar6) {
      return;
    }
    uVar5 = 0;
    uVar1 = (*((ushort *)camry_host_ptr((uint32_t)(uVar6 * 2 + (int)((ulonglong)uVar2 >> 0x20) + -0x219e))));
    do {
      if (uVar1 <= uVar5) break;
      iVar3 = dispatch_one_com_tx((uchar)uVar6);
      uVar5 = uVar5 + 1;
    } while (iVar3 != -0x14);
    if (uVar5 == 0) {
      clear_group_tx_pending_bit_ranges_7e046(uVar6,0xc0);
    }
    uVar6 = uVar6 + 1 & 0xff;
  } while( true );
}

undefined4 request_tx_by_group_and_mode_7e196(uint param_1,char param_2)

{
  byte bVar1;
  char cVar2;
  uint32_t puVar3;
  uint32_t puVar4;
  short sVar5;
  int iVar6;
  int iVar7;
  undefined4 uVar8;
  uint uVar9;
  
  cVar2 = DAT_00021c6f;
  puVar3 = 0xfebeb800u;
  puVar4 = 0x23dfcu;
  param_1 = param_1 & 0xffff;
  iVar7 = param_1 * 8;
  uVar9 = (uint)(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x226c2u + (uint32_t)(iVar7) * 1u))));
  uVar8 = 0xfffffffb;
  if (((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe4a39u + (uint32_t)(uVar9 + 3) * 1u)))) & (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x22148u + (uint32_t)(param_1) * 1u))))) == 0) {
    ((void)(param_1), return_only_stub_7e4e8());
  }
  else if (param_2 == -0x80) {
    iVar6 = ((void)(param_1), return_const_1_7e4dc());
    if (iVar6 == 1) {
      bVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x226c6u + (uint32_t)(iVar7) * 1u))));
      if ((bVar1 >> 1 & 1) != 0) {
        (*(int (*)())camry_indirect((uint32_t)(((((code *)(uintptr_t)((uint32_t)((uintptr_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(puVar4 + -0x21b8))))))))))))(uVar9);
      }
      if ((((bVar1 >> 5 & 1) == 0) ||
          (iVar7 = (*(int (*)())camry_indirect((uint32_t)(((((code *)(uintptr_t)((uint32_t)((uintptr_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(puVar4 + -0x21b4))))))))))))(uVar9,param_1), iVar7 == 0)) &&
         (uVar8 = set_com_pending_bitmap_bit_by_boolean_bank_7dab6(param_1,0), (bVar1 >> 3 & 1) != 0)) {
        (*(int (*)())camry_indirect((uint32_t)(((((code *)(uintptr_t)((uint32_t)((uintptr_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(puVar4 + -0x21dc))))))))))))();
      }
    }
  }
  else if ((((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe4a39u + (uint32_t)(uVar9 + 5) * 1u)))) == '\x01') &&
           (((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe493eu + (uint32_t)(param_1) * 1u)))) & 0x44) == 0)) &&
          (iVar6 = (*(int (*)())camry_indirect((uint32_t)(PTR_return_const_fffffff3_7e590_00021c40)))(param_1), iVar6 != -0xc))
  {
    sVar5 = *(short *)(((undefined *)camry_host_ptr((uint32_t)(0x226c0u + (uint32_t)(iVar7) * 1u))));
    if (sVar5 != 0) {
      if ((cVar2 == '\0') && ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(uVar9 - 0x6dc9))))) == '\x01')) {
        sVar5 = (*((short *)camry_host_ptr((uint32_t)(puVar4 + uVar9 * 2 + -0x21a4))));
      }
      if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(uVar9 - 0x2186))))) == '\x03') {
        sVar5 = return_u16_pdu_length_through_optional_group_gate_7dae0(uVar9,param_1,(uint)(ushort)sVar5);
      }
      (*((short *)camry_host_ptr((uint32_t)(puVar3 + param_1 * 2 + -0x6e92)))) = sVar5;
    }
    uVar8 = set_com_pending_bitmap_bit_by_boolean_bank_7dab6(param_1,1);
  }
  return uVar8;
}

void clear_group_pending_and_reset_pdus_7e29c(uint param_1,uint param_2)

{
  ushort uVar1;
  uint32_t puVar2;
  ushort uVar3;
  
  puVar2 = 0x23dfcu;
  param_2 = param_2 & 0xff;
  param_1 = param_1 & 0xff;
  if (param_2 >> 7 != 0) {
    puVar2 = 0x23dfcu;
    (*(int (*)())camry_indirect((uint32_t)(PTR_return_only_stub_7e59c_00021c2c)))(param_1);
  }
  clear_group_tx_pending_bit_ranges_7e046(param_1,param_2);
  if (param_2 == 0xc0) {
    uVar3 = (*((ushort *)camry_host_ptr((uint32_t)(puVar2 + param_1 * 4 + -0x1cbc))));
    uVar1 = (*((short *)camry_host_ptr((uint32_t)(puVar2 + param_1 * 4 + -0x1cba)))) + uVar3;
    for (; uVar3 < uVar1; uVar3 = uVar3 + 1) {
      call_21cc8_with_prefixed_u16_81a98(uVar3);
    }
  }
  return;
}

void zero_group_tx_period_countdowns_7e2ea(uint param_1)

{
  uint uVar1;
  int iVar2;
  uint uVar3;
  
  iVar2 = (param_1 & 0xff) * 4;
  uVar3 = (uint)*(ushort *)(((undefined *)camry_host_ptr((uint32_t)(0x22140u + (uint32_t)(iVar2) * 1u))));
  uVar1 = *(ushort *)(((undefined *)camry_host_ptr((uint32_t)(0x22142u + (uint32_t)(iVar2) * 1u)))) + uVar3;
  for (; uVar3 < (uVar1 & 0xffff); uVar3 = uVar3 + 1 & 0xffff) {
    (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe496eu + (uint32_t)(uVar3) * 2u)))) = 0;
  }
  return;
}

void initialize_tx_inhibit_and_pending_pairs_7e312(void)

{
  uint uVar1;
  uint uVar2;
  
  uVar2 = (uint)DAT_00021c70;
  for (uVar1 = 0; uVar1 < uVar2; uVar1 = uVar1 + 1 & 0xff) {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe4a34u + (uint32_t)(uVar1 + 1) * 1u)))) = 0xff;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe4a34u + (uint32_t)(uVar1) * 1u)))) = '\0';
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe4a39u + (uint32_t)(uVar1 + 1) * 1u)))) = '\0';
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe4a39u + (uint32_t)(uVar1) * 1u)))) = '\0';
  }
  DAT_febe4fb1 = 0;
  return;
}

void set_tx_group_modes_two_7e33e(void)

{
  uint uVar1;
  uint uVar2;
  
  uVar2 = 1;
  if (DAT_00021c6f == '\0') {
    uVar2 = (uint)DAT_00021c6e;
  }
  for (uVar1 = 0; uVar1 < uVar2; uVar1 = uVar1 + 1 & 0xff) {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe4a37u + (uint32_t)(uVar1) * 1u)))) = 2;
  }
  return;
}

void zero_all_tx_minimum_delay_countdowns_7e364(void)

{
  uint uVar1;
  uint uVar2;
  
  uVar2 = (uint)DAT_00021c56;
  for (uVar1 = 0; uVar1 < uVar2; uVar1 = uVar1 + 1 & 0xffff) {
    (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe4978u + (uint32_t)(uVar1) * 2u)))) = 0;
  }
  return;
}

void initialize_tx_groups_from_mask_bytes_7e380(int param_1)

{
  uchar uVar1;
  uint uVar2;
  uint uVar3;
  
  uVar3 = (uint)DAT_00021c6e;
  for (uVar2 = 0; uVar2 < uVar3; uVar2 = uVar2 + 1 & 0xff) {
    uVar1 = (*((uchar *)camry_host_ptr((uint32_t)(uVar2 + param_1))));
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe4a3fu + (uint32_t)(uVar2) * 1u)))) = 0;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe4a39u + (uint32_t)(uVar2 + 2) * 1u)))) = uVar1;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe4a39u + (uint32_t)(uVar2 + 3) * 1u)))) = uVar1;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe4a39u + (uint32_t)(uVar2 + 4) * 1u)))) = '\x02';
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe4a39u + (uint32_t)(uVar2 + 5) * 1u)))) = '\x02';
    *(undefined2 *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe4986u + (uint32_t)(uVar2 * 2) * 1u)))) = 0;
  }
  return;
}

void reset_tx_group_modes_and_pending_masks_7e3bc(void)

{
  uint uVar1;
  uint uVar2;
  
  uVar2 = (uint)DAT_00021c6e;
  for (uVar1 = 0; uVar1 < uVar2; uVar1 = uVar1 + 1 & 0xff) {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe4a39u + (uint32_t)(uVar1 + 5) * 1u)))) = '\x02';
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe4a39u + (uint32_t)(uVar1 + 4) * 1u)))) = '\x02';
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe4a39u + (uint32_t)(uVar1 + 3) * 1u)))) = '\0';
  }
  return;
}

undefined4 set_tx_group_mode_pair_from_bits_7e3e0(uint param_1,uint param_2)

{
  uint32_t puVar1;
  undefined4 uVar2;
  undefined1 uVar3;
  undefined1 uVar4;
  
  puVar1 = 0xfebeb800u;
  if ((param_2 & 1) == 0) {
    uVar3 = 2;
  }
  else {
    uVar3 = 1;
  }
  if ((param_2 >> 1 & 1) == 0) {
    uVar4 = 2;
  }
  else {
    uVar4 = 1;
  }
  uVar2 = call_interrupt_guard_and_return_zero_7a2da();
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)((param_1 & 0xff) - 0x6dc2))))) = uVar3;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)((param_1 & 0xff) - 0x6dc3))))) = uVar4;
  ((void)(uVar2), thunk_pop_and_restore_priority_mask_stack_6a4c4());
  return uVar2;
}

undefined4 set_group_u16_timer_and_active_flag_7e412(uint param_1,undefined2 param_2)

{
  uint32_t puVar1;
  undefined4 uVar2;
  
  puVar1 = 0xfebeb800u;
  uVar2 = call_interrupt_guard_and_return_zero_7a2da();
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)((param_1 & 0xff) - 0x6dc1))))) = 1;
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + (param_1 & 0xff) * 2 + -0x6e7a)))) = param_2;
  ((void)(uVar2), thunk_pop_and_restore_priority_mask_stack_6a4c4());
  return uVar2;
}

void dispatch_pdu_hook_and_optional_8e7a4_7e43c(uint param_1)

{
  byte bVar1;
  
  bVar1 = (*((byte *)camry_host_ptr((uint32_t)(&PTR_DAT_000226c7 + (param_1 & 0xffff) * 2))));
  (*(int (*)())camry_indirect((uint32_t)(PTR_return_only_stub_7e720_00021c14)))();
  if ((bVar1 >> 1 & 1) != 0) {
    increment_tracking_counter5338_8e7a4(param_1 & 0xffff);
  }
  return;
}

void clear_tx_pending_bit_by_mode_7e46a(uint param_1,char param_2)

{
  byte bVar1;
  uint32_t puVar2;
  uint32_t puVar3;
  undefined4 uVar4;
  uint uVar5;
  uint uVar6;
  
  puVar2 = 0xfebeb800u;
  puVar3 = 0x23dfcu;
  uVar6 = param_1 & 0xffff;
  if (uVar6 < DAT_00021c56) {
    uVar5 = uVar6 >> 3 & 0xff;
    bVar1 = (byte)(1 << (param_1 & 7)) ^ 0xff;
    uVar4 = call_interrupt_guard_and_return_zero_7a2da();
    if (param_2 == -0x80) {
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(uVar5 - 0x6dc6))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(uVar5 - 0x6dc6))))) & bVar1;
      if (((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x226c6u + (uint32_t)(uVar6 * 8) * 1u)))) & 8) != 0) {
        (*(int (*)())camry_indirect((uint32_t)(((((code *)(uintptr_t)((uint32_t)((uintptr_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(puVar3 + -0x21cc))))))))))))(uVar6);
      }
    }
    else {
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(uVar5 - 0x6dc7))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(uVar5 - 0x6dc7))))) & bVar1;
    }
    ((void)(uVar4), thunk_pop_and_restore_priority_mask_stack_6a4c4());
  }
  return;
}

undefined4 return_const_1_7e4dc(void)

{
  return 1;
}

undefined2 return_third_argument_u16_7e4e0(undefined4 param_1,undefined4 param_2,undefined2 param_3)

{
  return param_3;
}

void return_only_stub_7e4e6(void)

{
  return;
}

void return_only_stub_7e4e8(void)

{
  return;
}

void set_valid_tx_group_mode_one_7e4ea(uint param_1)

{
  if ((param_1 & 0xff) < (uint)DAT_00021c6e) {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe4a37u + (uint32_t)(param_1 & 0xff) * 1u)))) = 1;
  }
  return;
}

void set_tx_group_mode_two_and_defer_periods_7e4fe(uint param_1)

{
  uint uVar1;
  byte bVar2;
  byte bVar3;
  uint32_t puVar4;
  uint32_t puVar5;
  undefined4 uVar6;
  uint uVar7;
  
  puVar4 = 0xfebeb800u;
  puVar5 = 0x23dfcu;
  param_1 = param_1 & 0xff;
  if (param_1 < DAT_00021c6e) {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe4a37u + (uint32_t)(param_1) * 1u)))) = 2;
    uVar7 = (uint)*(ushort *)(((undefined *)camry_host_ptr((uint32_t)(0x22140u + (uint32_t)(param_1 * 4) * 1u))));
    uVar1 = *(ushort *)(((undefined *)camry_host_ptr((uint32_t)(0x22142u + (uint32_t)(param_1 * 4) * 1u)))) + uVar7;
    bVar3 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe4a39u + (uint32_t)(param_1 + 3) * 1u))));
    for (; uVar7 < (uVar1 & 0xffff); uVar7 = uVar7 + 1 & 0xffff) {
      if (((*((short *)camry_host_ptr((uint32_t)(puVar5 + uVar7 * 8 + -0x173c)))) != 0) && (((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(uVar7 - 0x1cb4))))) & bVar3) != 0)
         ) {
        uVar6 = call_interrupt_guard_and_return_zero_7a2da();
        bVar2 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(uVar7 - 0x6ec2)))));
        if ((bVar2 >> 2 & 1) == 0) {
          (*((short *)camry_host_ptr((uint32_t)(puVar4 + uVar7 * 2 + -0x6e92)))) = (*((short *)camry_host_ptr((uint32_t)(puVar5 + uVar7 * 2 + -0x1c84)))) + 1;
          (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(uVar7 - 0x6ec2))))) = bVar2 | 0x40;
        }
        ((void)(uVar6), thunk_pop_and_restore_priority_mask_stack_6a4c4());
      }
    }
  }
  return;
}

void return_only_stub_7e588(void)

{
  return;
}

void return_only_stub_7e58a(void)

{
  return;
}

void return_only_stub_7e58e(void)

{
  return;
}

undefined4 return_const_fffffff3_7e590(void)

{
  return 0xfffffff3;
}

void return_only_stub_7e594(void)

{
  return;
}

void return_only_stub_7e596(void)

{
  return;
}

void return_only_stub_7e598(void)

{
  return;
}

void return_only_stub_7e59c(void)

{
  return;
}

void return_only_stub_7e59e(void)

{
  return;
}

void return_only_stub_7e5a0(void)

{
  return;
}

void return_only_stub_7e5a2(void)

{
  return;
}

undefined4 copy_enabled_tx_pdu_payload_7e5a4(uint param_1,int *param_2)

{
  ushort uVar1;
  ushort uVar2;
  uint uVar3;
  uint32_t puVar4;
  uint32_t puVar5;
  undefined4 uVar6;
  int iVar7;
  undefined4 uVar8;
  
  puVar4 = 0xfebeb800u;
  puVar5 = 0x23dfcu;
  param_1 = param_1 & 0xffff;
  uVar1 = *(ushort *)(((undefined *)camry_host_ptr((uint32_t)(0x226c4u + (uint32_t)(param_1 * 8) * 1u))));
  uVar2 = *(ushort *)(((undefined *)camry_host_ptr((uint32_t)(0x22840u + (uint32_t)(param_1 * 2) * 1u))));
  uVar8 = 1;
  iVar7 = *param_2;
  uVar6 = thunk_call_interrupt_guard_and_return_zero_7a2da();
  if (((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(param_1 - 0x1cb4))))) & (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)((byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x226c2u + (uint32_t)(param_1 * 8) * 1u)))) - 0x6dc4)))))) != 0) {
    for (uVar3 = 0; uVar3 < uVar1; uVar3 = uVar3 + 1 & 0xffff) {
      (*((undefined1 *)camry_host_ptr((uint32_t)(uVar3 + iVar7)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe4a48u + (uint32_t)(uVar3 + uVar2) * 1u))));
    }
    *(ushort *)(param_2 + 1) = uVar1;
    uVar8 = 0;
  }
  ((void)(uVar6), thunk_pop_and_restore_priority_mask_stack_6a4c4());
  return uVar8;
}

undefined4 set_tx_inhibit_pair_and_flag_7e612(uint param_1)

{
  byte *pbVar1;
  uint uVar2;
  byte bVar3;
  byte bVar4;
  byte bVar5;
  uint32_t puVar6;
  undefined4 uVar7;
  undefined4 uVar8;
  uint uVar9;
  uint uVar10;
  uint uVar11;
  
  puVar6 = 0xfebeb800u;
  uVar10 = param_1 & 0xffff;
  uVar8 = 1;
  if (uVar10 < DAT_00021c56) {
    uVar2 = 1 << (param_1 & 7);
    uVar9 = uVar10 >> 3 & 0xff;
    uVar11 = uVar2 & 0xff;
    uVar7 = call_interrupt_guard_and_return_zero_7a2da();
    pbVar1 = ((undefined *)camry_host_ptr((uint32_t)(puVar6 + (uVar9 - 0x6dcb))));
    bVar3 = *pbVar1;
    bVar4 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(uVar9 - 0x6dcc)))));
    bVar5 = (byte)uVar2;
    if (((bVar3 ^ bVar4) & uVar11) == 0) {
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(uVar9 - 0x6dcc))))) = bVar5 | bVar4;
      *pbVar1 = bVar5 | bVar3;
      set_com_state_4a47_5a_833d6();
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(uVar10 - 0x6ec2))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(uVar10 - 0x6ec2))))) | 0x10;
    }
    else if ((uVar11 & bVar4) == 0) {
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(uVar9 - 0x6dcc))))) = bVar5 | bVar4;
      uVar8 = 0;
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(uVar10 - 0x6ec2))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(uVar10 - 0x6ec2))))) | 0x10;
      *pbVar1 = (bVar5 ^ 0xff) & bVar3;
    }
    ((void)(uVar7), thunk_pop_and_restore_priority_mask_stack_6a4c4());
  }
  return uVar8;
}

undefined4 clear_tx_inhibit_pair_and_flag_7e696(uint param_1)

{
  byte *pbVar1;
  uint uVar2;
  byte bVar3;
  byte bVar4;
  byte bVar5;
  uint32_t puVar6;
  undefined4 uVar7;
  undefined4 uVar8;
  uint uVar9;
  uint uVar10;
  uint uVar11;
  
  puVar6 = 0xfebeb800u;
  uVar10 = param_1 & 0xffff;
  uVar8 = 1;
  if (uVar10 < DAT_00021c56) {
    uVar2 = 1 << (param_1 & 7);
    uVar9 = uVar10 >> 3 & 0xff;
    uVar11 = uVar2 & 0xff;
    uVar7 = call_interrupt_guard_and_return_zero_7a2da();
    pbVar1 = ((undefined *)camry_host_ptr((uint32_t)(puVar6 + (uVar9 - 0x6dcb))));
    bVar3 = *pbVar1;
    bVar4 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(uVar9 - 0x6dcc)))));
    bVar5 = (byte)uVar2;
    if (((bVar3 ^ bVar4) & uVar11) == 0) {
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(uVar9 - 0x6dcc))))) = bVar5 | bVar4;
      *pbVar1 = bVar5 | bVar3;
      set_com_state_4a47_5a_833d6();
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(uVar10 - 0x6ec2))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(uVar10 - 0x6ec2))))) | 0x10;
    }
    else if ((uVar11 & bVar4) != 0) {
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(uVar9 - 0x6dcc))))) = (bVar5 ^ 0xff) & bVar4;
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(uVar10 - 0x6ec2))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(uVar10 - 0x6ec2))))) & 0xef;
      *pbVar1 = bVar5 | bVar3;
      uVar8 = 0;
    }
    ((void)(uVar7), thunk_pop_and_restore_priority_mask_stack_6a4c4());
  }
  return uVar8;
}

void return_only_stub_7e718(void)

{
  return;
}

void return_only_stub_7e71a(void)

{
  return;
}

void return_only_stub_7e71c(void)

{
  return;
}

void return_only_stub_7e71e(void)

{
  return;
}

void return_only_stub_7e720(void)

{
  return;
}

undefined4 return_const_0_7e722(void)

{
  return 0;
}

undefined4 return_const_0_7e726(void)

{
  return 0;
}

undefined4 copy_tx_buffer_range_return_flag_status_7e72a(uint param_1,uint param_2,uint param_3,int param_4)

{
  char cVar1;
  ushort uVar2;
  uint uVar3;
  uint32_t puVar4;
  undefined4 uVar5;
  
  puVar4 = 0xfebeb800u;
  uVar2 = *(ushort *)(((undefined *)camry_host_ptr((uint32_t)(0x22488u + (uint32_t)((param_1 & 0xffff) * 2) * 1u))));
  uVar5 = thunk_call_interrupt_guard_and_return_zero_7a2da();
  for (uVar3 = 0; uVar3 < (param_3 & 0xffff); uVar3 = uVar3 + 1 & 0xffff) {
    (*((undefined1 *)camry_host_ptr((uint32_t)(uVar3 + param_4)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe4a48u + (uint32_t)(uVar3 + (param_2 & 0xffff)) * 1u))));
  }
  cVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(uVar2 - 0x6ec2)))));
  ((void)(uVar5), thunk_pop_and_restore_priority_mask_stack_6a4c4());
  uVar5 = 0x20;
  if (cVar1 < '\0') {
    uVar5 = 0;
  }
  return uVar5;
}

undefined4 return_const_1_7e77e(void)

{
  return 1;
}

void initialize_sixteen_byte_state_records_7e782(void)

{
  int iVar1;
  uint uVar2;
  uint32_t puVar3;
  uint uVar4;
  
  puVar3 = 0xfebeb800u;
  uVar4 = (uint)DAT_00021be1;
  for (uVar2 = 0; uVar2 < uVar4; uVar2 = uVar2 + 1 & 0xff) {
    iVar1 = uVar2 * 0x10;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe4936u + (uint32_t)(iVar1) * 1u)))) = 0;
    *(undefined2 *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe492au + (uint32_t)(iVar1) * 1u)))) = 0xff;
    *(undefined2 *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe492cu + (uint32_t)(iVar1) * 1u)))) = 0xff;
    *(undefined2 *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe492eu + (uint32_t)(iVar1) * 1u)))) = 0xff;
    *(undefined2 *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe4930u + (uint32_t)(iVar1) * 1u)))) = 0xff;
    *(undefined2 *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe4932u + (uint32_t)(iVar1) * 1u)))) = 0xff;
    *(undefined2 *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe4928u + (uint32_t)(iVar1) * 1u)))) = 0;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe4934u + (uint32_t)(iVar1) * 1u)))) = 0x1e;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe4935u + (uint32_t)(iVar1) * 1u)))) = 0x1e;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe4937u + (uint32_t)(iVar1) * 1u)))) = 0x1e;
  }
  DAT_febe493a = 0;
  DAT_febe493c = 0xffff;
  (*(int (*)())camry_indirect((uint32_t)(PTR_return_only_stub_7ed66_00021bbc)))();
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x6ec8)))) = 0x1fe;
  return;
}

void set_global_state_4938_ff_7e7da(void)

{
  DAT_febe4938 = 0xff;
  return;
}

bool test_record_mask_against_global_493a_7e7e4(uint param_1)

{
  if ((param_1 & 0xff) < (uint)DAT_00021be1) {
    return ((byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x21be2u + (uint32_t)(param_1 & 0xff) * 1u)))) & DAT_febe493a) != 0;
  }
  return false;
}

uint compose_record_status_flags_7e804(uint param_1)

{
  int iVar1;
  char cVar2;
  char cVar3;
  uint32_t puVar4;
  uint uVar5;
  
  puVar4 = 0x23dfcu;
  param_1 = param_1 & 0xff;
  iVar1 = param_1 * 0x10;
  if ((*(ushort *)(((undefined *)camry_host_ptr((uint32_t)(0x21bdcu + (uint32_t)(param_1 * 2) * 1u)))) & DAT_febe493a) == 0) {
    uVar5 = (*(int (*)())camry_indirect((uint32_t)(PTR_return_const_0_7ed6c_00021bc8)))(param_1);
    if (uVar5 != 0) goto LAB_0007e87a;
    if (((*(short *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe4930u + (uint32_t)(iVar1) * 1u)))) != 0x1fe) &&
        (*(short *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe4932u + (uint32_t)(iVar1) * 1u)))) != 0x1fe)) &&
       (*(short *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe492eu + (uint32_t)(iVar1) * 1u)))) != 0x1fe)) {
      uVar5 = 8;
      cVar2 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe4934u + (uint32_t)(iVar1) * 1u))));
      cVar3 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe4935u + (uint32_t)(iVar1) * 1u))));
      if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe4936u + (uint32_t)(iVar1) * 1u)))) != '\x01') {
        uVar5 = (*(int (*)())camry_indirect((uint32_t)(((((code *)(uintptr_t)((uint32_t)((uintptr_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(puVar4 + -0x2238))))))))))))(param_1);
      }
      if ((((int8_t)cVar2) == -0x1f) || (((int8_t)cVar3) == -0x1f)) {
        uVar5 = uVar5 | 1;
      }
      goto LAB_0007e87a;
    }
  }
  uVar5 = 4;
LAB_0007e87a:
  if (((int8_t)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe4937u + (uint32_t)(iVar1) * 1u))))) == -0x1f) {
    uVar5 = uVar5 | 2;
  }
  return uVar5;
}

undefined4 read_record_state_as_compact_code_7e88c(uint param_1,undefined1 *param_2)

{
  short sVar1;
  int iVar2;
  undefined1 uVar3;
  
  param_1 = param_1 & 0xff;
  if (DAT_febe4938 != 0x1fe) {
    return 1;
  }
  if (DAT_00021be1 <= param_1) {
    return 1;
  }
  sVar1 = *(short *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe492au + (uint32_t)(param_1 * 0x10) * 1u))));
  if (sVar1 == 0xff) {
    uVar3 = 0;
    iVar2 = test_record_mask_against_global_493a_7e7e4(param_1);
    if ((iVar2 == 1) &&
       ((iVar2 = compose_record_status_flags_7e804(param_1), iVar2 != 0 ||
        (*(short *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe4928u + (uint32_t)(param_1 * 0x10) * 1u)))) != 0)))) {
      uVar3 = 1;
    }
    goto LAB_0007e8d6;
  }
  if (sVar1 != 0x1fe) {
    if (sVar1 == 0x2fd) {
      uVar3 = 3;
      goto LAB_0007e8d6;
    }
    if (sVar1 == 0x3fc) {
      uVar3 = 4;
      goto LAB_0007e8d6;
    }
    if (sVar1 != 0x5fa) {
      return 1;
    }
  }
  uVar3 = 2;
LAB_0007e8d6:
  *param_2 = uVar3;
  return 0;
}

int select_record_status_priority_7e912(uint param_1)

{
  uint32_t puVar1;
  uint32_t puVar2;
  int iVar3;
  
  puVar1 = 0xfebeb800u;
  puVar2 = 0x23dfcu;
  param_1 = param_1 & 0xff;
  if ((*(ushort *)(((undefined *)camry_host_ptr((uint32_t)(0x21bdcu + (uint32_t)(param_1 * 2) * 1u)))) & DAT_febe493a) == 0) {
    iVar3 = (*(int (*)())camry_indirect((uint32_t)(PTR_return_const_0_7ed70_00021bcc)))(param_1);
    if (iVar3 != 0) {
      return iVar3;
    }
    if ((((*((short *)camry_host_ptr((uint32_t)(puVar1 + param_1 * 0x10 + -0x6ed0)))) != 0x1fe) &&
        ((*((short *)camry_host_ptr((uint32_t)(puVar1 + param_1 * 0x10 + -0x6ece)))) != 0x1fe)) &&
       ((*((short *)camry_host_ptr((uint32_t)(puVar1 + param_1 * 0x10 + -0x6ed2)))) != 0x1fe)) {
      if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(param_1 * 0x10 + -0x6eca))))) == '\x01') {
        return 8;
      }
      iVar3 = (*(int (*)())camry_indirect((uint32_t)(((((code *)(uintptr_t)((uint32_t)((uintptr_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(puVar2 + -0x2238))))))))))))(param_1);
      if (iVar3 != 0) {
        return iVar3;
      }
      if (((int8_t)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(param_1 * 0x10 + -0x6ec9)))))) == -0x1f) {
        return 2;
      }
      if (((int8_t)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(param_1 * 0x10 + -0x6ecc)))))) != -0x1f) {
        return 0;
      }
      return 1;
    }
  }
  return 4;
}

undefined4 get_record_compact_state_or_five_7e998(uint param_1)

{
  short sVar1;
  int iVar2;
  undefined4 uVar3;
  
  param_1 = param_1 & 0xff;
  uVar3 = 5;
  if ((DAT_febe4938 == 0x1fe) && (param_1 < DAT_00021be1)) {
    sVar1 = *(short *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe492au + (uint32_t)(param_1 * 0x10) * 1u))));
    if (sVar1 == 0xff) {
      uVar3 = 0;
      iVar2 = test_record_mask_against_global_493a_7e7e4(param_1);
      if ((iVar2 == 1) &&
         ((iVar2 = select_record_status_priority_7e912(param_1), iVar2 != 0 ||
          (*(short *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe4928u + (uint32_t)(param_1 * 0x10) * 1u)))) != 0)))) {
        uVar3 = 1;
      }
    }
    else {
      if (sVar1 != 0x1fe) {
        if (sVar1 == 0x2fd) {
          return 3;
        }
        if (sVar1 == 0x3fc) {
          return 4;
        }
        if (sVar1 != 0x5fa) {
          return 5;
        }
      }
      uVar3 = 2;
    }
  }
  return uVar3;
}

undefined4 update_complemented_global_mask_bit_7ea26(uint param_1,char param_2)

{
  ushort uVar1;
  ushort uVar2;
  uint32_t puVar3;
  undefined4 uVar4;
  undefined4 uVar5;
  
  puVar3 = 0xfebeb800u;
  uVar5 = 1;
  if (DAT_febe4938 == 0x1fe) {
    if ((param_1 & 0xff) < 0x10) {
      uVar4 = call_interrupt_guard_and_return_zero_7a2da();
      uVar2 = (*((ushort *)camry_host_ptr((uint32_t)(puVar3 + -0x6ec6))));
      if (((*((ushort *)camry_host_ptr((uint32_t)(puVar3 + -0x6ec4)))) ^ uVar2) == 0xffff) {
        uVar1 = (ushort)(1 << (param_1 & 0x1f));
        if (param_2 == '\x02') {
          uVar2 = uVar2 | uVar1;
        }
        else {
          uVar2 = uVar2 & (uVar1 ^ 0xffff);
        }
        (*((ushort *)camry_host_ptr((uint32_t)(puVar3 + -0x6ec6)))) = uVar2;
        uVar5 = 0;
        (*((ushort *)camry_host_ptr((uint32_t)(puVar3 + -0x6ec4)))) = uVar2 ^ 0xffff;
      }
      ((void)(uVar4), thunk_pop_and_restore_priority_mask_stack_6a4c4());
    }
    else {
      uVar5 = (*(int (*)())camry_indirect((uint32_t)(PTR_return_const_1_7ed7c_00021bc0)))(param_1 & 0xff,param_2);
    }
  }
  return uVar5;
}

void set_record_492c_boolean_token_7ead0(uint param_1,char param_2)

{
  undefined2 uVar1;
  
  if ((param_1 & 0xff) < (uint)DAT_00021be1) {
    uVar1 = 0x1fe;
    if (param_2 == '\0') {
      uVar1 = 0xff;
    }
    *(undefined2 *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe492cu + (uint32_t)((param_1 & 0xff) * 0x10) * 1u)))) = uVar1;
  }
  return;
}

void dispatch_record_three_way_operation_7eaf2(byte param_1,byte param_2)

{
  if (param_1 < DAT_00021be1) {
    if (param_2 < 3) {
      call_218a4_with_two_bytes_83236(param_1,param_2);
    }
    if (param_2 == 0) {
      call_218b0_with_byte_8324a(param_1);
    }
    else if (param_2 == 1) {
      call_218b4_with_byte_8325c((uint)(byte)param_1);
    }
    else if (param_2 == 2) {
      call_218b8_with_byte_8326e((uint)(byte)param_1);
    }
  }
  return;
}

void call_21bd8_when_global_state_1fe_7eb32(void)

{
  if (DAT_febe4938 == 0x1fe) {
    (*(int (*)())camry_indirect((uint32_t)(PTR_FUN_00021bd8)))();
  }
  return;
}

undefined1 get_record_byte_mask_or_zero_7eb4c(uint param_1)

{
  if ((param_1 & 0xff) < (uint)DAT_00021be1) {
    return (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x21be2u + (uint32_t)(param_1 & 0xff) * 1u))));
  }
  return 0;
}

undefined1 get_record_u16_mask_low_byte_or_zero_7eb62(uint param_1)

{
  if ((param_1 & 0xff) < (uint)DAT_00021be1) {
    return (char)*(undefined2 *)(((undefined *)camry_host_ptr((uint32_t)(0x21bdcu + (uint32_t)((param_1 & 0xff) * 2) * 1u))));
  }
  return 0;
}

bool test_enabled_record_492c_is_1fe_7eb7c(uint param_1)

{
  uint32_t puVar1;
  int iVar2;
  bool bVar3;
  
  puVar1 = 0xfebeb800u;
  param_1 = param_1 & 0xff;
  bVar3 = false;
  if ((param_1 < DAT_00021be1) && (iVar2 = test_record_mask_against_global_493a_7e7e4(param_1), iVar2 == 1)) {
    bVar3 = (*((short *)camry_host_ptr((uint32_t)(puVar1 + param_1 * 0x10 + -0x6ed4)))) == 0x1fe;
  }
  return bVar3;
}

undefined4 transition_ff_record_on_status_7ebae(uint param_1,uint param_2,char param_3)

{
  int iVar1;
  undefined4 uVar2;
  
  param_1 = param_1 & 0xff;
  param_2 = param_2 & 0xff;
  iVar1 = param_1 * 0x10;
  if (*(short *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe4928u + (uint32_t)(iVar1) * 1u)))) == 0) {
    if ((param_2 >> 2 & 1) != 0) {
      *(undefined2 *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe4928u + (uint32_t)(iVar1) * 1u)))) = *(undefined2 *)(((undefined *)camry_host_ptr((uint32_t)(0x21bdeu + (uint32_t)(param_1 * 2) * 1u))));
    }
  }
  else {
    param_2 = param_2 | 4;
  }
  uVar2 = 0xff;
  if (((param_3 == '\x01') && (*(short *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe492cu + (uint32_t)(iVar1) * 1u)))) == 0x1fe)) && (param_2 != 0)) {
    (*(int (*)())camry_indirect((uint32_t)(((((code *)(uintptr_t)((uint32_t)((uintptr_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x21be4u + (uint32_t)((byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x21be0u + (uint32_t)(param_1) * 1u))))) * 4u)))))))))))))))(param_1,2, (uint)(byte)param_3);
    if ((param_2 & 0xc) == 0) {
      dispatch_record_callback_slot_zero_7ee8e(param_1);
      uVar2 = 0x5fa;
    }
    else {
      dispatch_record_callback_slot_four_7eeae((uint)(byte)param_1);
      uVar2 = 0x1fe;
    }
    *(undefined2 *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe4928u + (uint32_t)(iVar1) * 1u)))) = 0;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe4934u + (uint32_t)(iVar1) * 1u)))) = 0x1e;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe4937u + (uint32_t)(iVar1) * 1u)))) = 0x1e;
  }
  return uVar2;
}

undefined4 transition_1fe_record_by_status_7ec40(undefined1 param_1,uint param_2,char param_3)

{
  undefined4 uVar1;
  
  uVar1 = 0x1fe;
  if ((param_3 == '\0') || ((param_2 & 0xc) == 0)) {
    dispatch_record_callback_slot_eight_7eece((uint)(byte)param_1);
    uVar1 = 0x2fd;
  }
  else {
    (*(int (*)())camry_indirect((uint32_t)(PTR_return_only_stub_7ed74_00021bd0)))(param_1);
  }
  return uVar1;
}

undefined4 transition_5fa_record_by_status_7ec70(undefined1 param_1,uint param_2,char param_3)

{
  undefined4 uVar1;
  
  if ((param_3 == '\0') || ((param_2 & 0xc) == 0)) {
    dispatch_record_callback_slot_eight_7eece((uint)(byte)param_1);
    uVar1 = 0x2fd;
  }
  else {
    dispatch_record_callback_slot_four_7eeae(param_1);
    uVar1 = 0x1fe;
  }
  return uVar1;
}

undefined4 transition_2fd_record_if_enabled_status_7ec96(undefined1 param_1,uint param_2,char param_3)

{
  undefined4 uVar1;
  
  uVar1 = 0x2fd;
  if ((param_3 == '\x01') && ((param_2 & 0xc) != 0)) {
    dispatch_record_callback_slot_four_7eeae(param_1);
    uVar1 = 0x1fe;
  }
  return uVar1;
}

undefined4 transition_3fc_record_on_status_7ecb8(uint param_1,uint param_2,char param_3)

{
  uint32_t puVar1;
  undefined4 uVar2;
  
  puVar1 = 0xfebeb800u;
  param_1 = param_1 & 0xff;
  uVar2 = 0x3fc;
  if (((param_2 & 0xe) != 0) && (param_3 == '\x01')) {
    (*(int (*)())camry_indirect((uint32_t)(((((code *)(uintptr_t)((uint32_t)((uintptr_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x21be4u + (uint32_t)((byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x21be0u + (uint32_t)(param_1) * 1u))))) * 4u)))))))))))))))(param_1,2, (uint)(byte)param_3);
    if ((param_2 & 0xc) == 0) {
      dispatch_record_callback_slot_zero_7ee8e(param_1);
      uVar2 = 0x5fa;
    }
    else {
      dispatch_record_callback_slot_four_7eeae((uint)(byte)param_1);
      uVar2 = 0x1fe;
    }
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(param_1 * 0x10 + -0x6ec9))))) = 0x1e;
  }
  return uVar2;
}

void set_record_492e_token_1fe_7ed16(uint param_1)

{
  if ((param_1 & 0xff) < (uint)DAT_00021be1) {
    *(undefined2 *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe492eu + (uint32_t)((param_1 & 0xff) * 0x10) * 1u)))) = 0x1fe;
  }
  return;
}

void set_record_492e_token_ff_7ed2e(uint param_1)

{
  if ((param_1 & 0xff) < (uint)DAT_00021be1) {
    *(undefined2 *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe492eu + (uint32_t)((param_1 & 0xff) * 0x10) * 1u)))) = 0xff;
  }
  return;
}

void set_record_4937_token_e1_7ed4e(uint param_1)

{
  if ((param_1 & 0xff) < (uint)DAT_00021be1) {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe4937u + (uint32_t)((param_1 & 0xff) * 0x10) * 1u)))) = 0xe1;
  }
  return;
}

void return_only_stub_7ed66(void)

{
  return;
}

undefined4 return_const_0_7ed68(void)

{
  return 0;
}

undefined4 return_const_0_7ed6c(void)

{
  return 0;
}

undefined4 return_const_0_7ed70(void)

{
  return 0;
}

void return_only_stub_7ed74(void)

{
  return;
}

void return_only_stub_7ed7a(void)

{
  return;
}

undefined4 return_const_1_7ed7c(void)

{
  return 1;
}

void decrement_record_timers_with_range_reset_7ed80(void)

{
  short sVar1;
  short sVar2;
  uint uVar3;
  uint uVar4;
  
  uVar3 = (uint)DAT_00021be1;
  for (uVar4 = 0; uVar4 < uVar3; uVar4 = uVar4 + 1 & 0xff) {
    sVar1 = *(short *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe4928u + (uint32_t)(uVar4 * 0x10) * 1u))));
    if (sVar1 != 0) {
      sVar2 = sVar1 + -1;
      if (*(ushort *)(((undefined *)camry_host_ptr((uint32_t)(0x21bdeu + (uint32_t)(uVar4 * 2) * 1u)))) < (ushort)(sVar1 - 1U)) {
        sVar2 = 0;
      }
      *(short *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe4928u + (uint32_t)(uVar4 * 0x10) * 1u)))) = sVar2;
    }
  }
  return;
}

void advance_record_token_state_machines_7edb8(void)

{
  int iVar1;
  undefined1 uVar2;
  undefined8 uVar3;
  short sVar4;
  int iVar5;
  undefined4 uVar6;
  uint uVar7;
  uint uVar8;
  
  uVar3 = 0x23dfcfebeb800;
  uVar7 = (uint)DAT_00021be1;
  for (uVar8 = 0; uVar8 < uVar7; uVar8 = uVar8 + 1 & 0xff) {
    iVar1 = uVar8 * 0x10 + (int)uVar3;
    sVar4 = (*((short *)camry_host_ptr((uint32_t)(iVar1 + -0x6ed6))));
    if (((int8_t)(*((char *)camry_host_ptr((uint32_t)(iVar1 + -0x6ecb))))) == -0x1f) {
      uVar2 = 0x1e;
      if (sVar4 == 0xff) {
        uVar2 = 0xe1;
      }
      (*((undefined1 *)camry_host_ptr((uint32_t)(iVar1 + -0x6ecc)))) = uVar2;
      (*((undefined1 *)camry_host_ptr((uint32_t)(iVar1 + -0x6ecb)))) = 0x1e;
    }
    iVar5 = test_record_mask_against_global_493a_7e7e4(uVar8);
    if (iVar5 == 0) {
      (*((undefined1 *)camry_host_ptr((uint32_t)(iVar1 + -0x6ec9)))) = 0x1e;
      (*((undefined1 *)camry_host_ptr((uint32_t)(iVar1 + -0x6ecc)))) = 0x1e;
    }
    uVar6 = select_record_status_priority_7e912(uVar8);
    if (sVar4 == 0xff) {
      sVar4 = transition_ff_record_on_status_7ebae(uVar8,uVar6,iVar5);
    }
    else if (sVar4 == 0x1fe) {
      sVar4 = transition_1fe_record_by_status_7ec40(uVar8,uVar6,iVar5);
    }
    else if (sVar4 == 0x2fd) {
      sVar4 = transition_2fd_record_if_enabled_status_7ec96(uVar8,uVar6,iVar5);
    }
    else if (sVar4 == 0x3fc) {
      sVar4 = transition_3fc_record_on_status_7ecb8(uVar8,uVar6,iVar5);
    }
    else if (sVar4 == 0x5fa) {
      sVar4 = transition_5fa_record_by_status_7ec70(uVar8,uVar6,iVar5);
    }
    (*((short *)camry_host_ptr((uint32_t)(iVar1 + -0x6ed6)))) = sVar4;
  }
  return;
}

void tick_record_timers_and_state_machines_7ee6e(void)

{
  decrement_record_timers_with_range_reset_7ed80();
  advance_record_token_state_machines_7edb8();
  return;
}

void return_only_stub_7ee7e(void)

{
  return;
}

void return_only_stub_7ee80(void)

{
  return;
}

void thunk_clear_record_4936_flags_wrapper_7ef9c(void)

{
  clear_record_4936_flags_wrapper_7ef9c();
  return;
}

void dispatch_record_callback_slot_zero_7ee8e(uint param_1)

{
  (*(int (*)())camry_indirect((uint32_t)(*((code * *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x21ca0u + (uint32_t)((byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x21c7du + (uint32_t)(param_1 & 0xff) * 1u))))) * 4u)))))))))((uint)(byte)param_1);
  return;
}

void dispatch_record_callback_slot_four_7eeae(uint param_1)

{
  (*(int (*)())camry_indirect((uint32_t)(*((code * *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x21ca0u + (uint32_t)((byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x21c7du + (uint32_t)(param_1 & 0xff) * 1u))))) * 4u)))) + 4))))))((uint)(byte)param_1);
  return;
}

void dispatch_record_callback_slot_eight_7eece(uint param_1)

{
  (*(int (*)())camry_indirect((uint32_t)(*((code * *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x21ca0u + (uint32_t)((byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x21c7du + (uint32_t)(param_1 & 0xff) * 1u))))) * 4u)))) + 8))))))((uint)(byte)param_1);
  return;
}

undefined4 dispatch_valid_record_callback_slot_twelve_7eeee(uint param_1)

{
  undefined4 uVar1;
  
  if ((param_1 & 0xff) < (uint)DAT_00021c7c) {
    uVar1 = (*(int (*)())camry_indirect((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x21ca0u + (uint32_t)((byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x21c7du + (uint32_t)(param_1 & 0xff) * 1u))))) * 4u)))) + 0xc))))))))((uint)(byte)param_1);
  }
  else {
    uVar1 = 1;
  }
  return uVar1;
}

void set_valid_record_4935_token_e1_wrapper_7ef1a(byte param_1)

{
  if (param_1 < DAT_00021c7c) {
    set_channel_marker_4935_e1_8344e((uint)(byte)param_1);
  }
  return;
}

void transition_valid_record_3fc_to_2fd_wrapper_7ef30(byte param_1)

{
  if (param_1 < DAT_00021c7c) {
    transition_channel_mode_03fc_to_02fd_8345e((uint)(byte)param_1);
  }
  return;
}

void request_valid_record_state_3fc_when_ready_7ef46(byte param_1)

{
  if (param_1 < DAT_00021c7c) {
    request_channel_mode_03fc_when_queries_allow_834f2((uint)(byte)param_1);
  }
  return;
}

void reset_valid_active_record_state_ff_wrapper_7ef5c(byte param_1)

{
  if (param_1 < DAT_00021c7c) {
    reset_channel_mode_to_00ff_833e4((uint)(byte)param_1);
  }
  return;
}

void transition_valid_active_record_to_3fc_wrapper_7ef72(byte param_1)

{
  if (param_1 < DAT_00021c7c) {
    transition_channel_mode_to_03fc_834a2((uint)(byte)param_1);
  }
  return;
}

void clear_record_4936_flags_wrapper_7ef9c(void)

{
  clear_channel_markers_4936_and_call_21bd4_83542();
  return_only_stub_8356c();
  return;
}

undefined4 thunk_call_interrupt_guard_and_return_zero_7a2da(void)

{
  return call_interrupt_guard_and_return_zero_7a2da();
}

void initialize_eight_byte_record_tokens_7eff2(void)

{
  uint32_t puVar1;
  uint32_t puVar2;
  uint uVar3;
  uint uVar4;
  
  puVar1 = 0xfebeb800u;
  puVar2 = 0x23dfcu;
  uVar3 = (uint)DAT_00021b8e;
  for (uVar4 = 0; uVar4 < uVar3; uVar4 = uVar4 + 1 & 0xff) {
    (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + uVar4 * 8 + -0x6eec)))) = 0xff00;
    if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(uVar4 - 0x226c))))) == '\0') {
      set_offset_network_indication_one_83282(uVar4);
      clear_offset_network_indication_and_disable_packets_832ae(uVar4);
    }
  }
  return;
}
