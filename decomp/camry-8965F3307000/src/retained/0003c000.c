#include "common.h"

void aggregate_fault_actions(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  uint32_t puVar4;
  ushort uVar5;
  uint actions;
  uint actions_00;
  uint actions_01;
  uint actions_02;
  undefined2 *puVar6;
  ushort local_28[5];
  
  puVar4 = 0xfebeb800u;
  actions_02 = 0;
  actions_01 = 0;
  actions_00 = 0;
  actions = 0;
  uVar5 = 0;
  iVar3 = 0;
  do {
    if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe71ccu + (uint32_t)(iVar3) * 1u)))) == 'Z') {
      puVar6 = (undefined2 *)camry_host_ptr(0xfebe7200u + (uint32_t)iVar3 * 12u);
      if ((~(uint)(ushort)(*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe7200u + (uint32_t)(iVar3 * 6) * 2u)))) & 0xffff) ==
          (uint)*(ushort *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe713cu + (uint32_t)(iVar3 * 2) * 1u))))) {
        actions_02 = actions_02 | (ushort)(*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe7200u + (uint32_t)(iVar3 * 6) * 2u))));
      }
      if ((ushort)~(*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe7208u + (uint32_t)(iVar3 * 6) * 2u)))) == *(ushort *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe719cu + (uint32_t)(iVar3 * 2) * 1u))))) {
        uVar5 = uVar5 | (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe7208u + (uint32_t)(iVar3 * 6) * 2u))));
      }
LAB_0003c0a0:
      actions_01 = actions_01 | (ushort)puVar6[1];
      actions_00 = actions_00 | (ushort)puVar6[2];
      actions = actions | (ushort)puVar6[3];
    }
    else if (((int8_t)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe71ccu + (uint32_t)(iVar3) * 1u))))) == -0x5b) {
      puVar6 = (undefined2 *)camry_host_ptr(0xfebe7320u + (uint32_t)iVar3 * 12u);
      if ((~(uint)(ushort)(*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe7320u + (uint32_t)(iVar3 * 6) * 2u)))) & 0xffff) ==
          (uint)*(ushort *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe710cu + (uint32_t)(iVar3 * 2) * 1u))))) {
        actions_02 = actions_02 | (ushort)(*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe7320u + (uint32_t)(iVar3 * 6) * 2u))));
      }
      if ((ushort)~(*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe7328u + (uint32_t)(iVar3 * 6) * 2u)))) == *(ushort *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe716cu + (uint32_t)(iVar3 * 2) * 1u))))) {
        uVar5 = uVar5 | (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe7328u + (uint32_t)(iVar3 * 6) * 2u))));
      }
      goto LAB_0003c0a0;
    }
    iVar2 = iVar3 + 1;
    iVar1 = iVar3 + -0x17;
    iVar3 = iVar2;
    if (iVar1 < 0 == (iVar2 < 0 && -1 < iVar1)) {
      local_28[0] = (ushort)actions_02;
      local_28[1] = (ushort)actions_01;
      local_28[2] = (ushort)actions_00;
      local_28[3] = (ushort)actions;
      local_28[4] = uVar5;
      qualify_fault_action_aggregate(local_28);
      if (((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffb9edu + (uint32_t)((int)puVar4) * 1u)))) & 0x80) != 0) {
        actions_02 = actions_02 | DAT_febe7440;
        actions_01 = actions_01 | DAT_febe7442;
        actions_00 = actions_00 | DAT_febe7444;
        actions = actions | DAT_febe7446;
      }
      route_fault_action_mode_request(actions_02);
      route_fault_status_actions(actions_01);
      route_fault_output_actions(actions_00);
      route_fault_ancillary_actions(actions);
      DAT_febe71f4 = (short)actions_02;
      DAT_febe71f6 = (short)actions_01;
      DAT_febe71f8 = (short)actions_00;
      DAT_febe71fa = (short)actions;
      DAT_febe71fc = uVar5;
      return;
    }
  } while( true );
}

void select_retained_fault_record(uint slot)

{
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe71ccu + (uint32_t)(slot & 0xff) * 1u)))) = 0xa5;
  return;
}

void merge_fault_action_record(ushort *actions,uint slot)

{
  int iVar1;
  ushort uVar2;
  uint uVar3;
  
  uVar3 = slot & 0xff;
  if (uVar3 < 0x18) {
    iVar1 = (int)(short)uVar3;
    uVar2 = actions[4];
    if ((DAT_febe71ec & uVar2) != 0) {
      *actions = *actions & 0xffed;
      actions[1] = actions[1] & 0xff8f;
      (*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(actions) + 5)))) = (*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(actions) + 5)))) & 0xf7;
      (*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(actions) + 5)))) = (*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(actions) + 5)))) & 0xfb;
    }
    (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe7200u + (uint32_t)(iVar1 * 6) * 2u)))) = (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe7200u + (uint32_t)(iVar1 * 6) * 2u)))) | *actions;
    (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe7202u + (uint32_t)(iVar1 * 6) * 2u)))) = (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe7202u + (uint32_t)(iVar1 * 6) * 2u)))) | actions[1];
    (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe7204u + (uint32_t)(iVar1 * 6) * 2u)))) = (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe7204u + (uint32_t)(iVar1 * 6) * 2u)))) | actions[2];
    (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe7206u + (uint32_t)(iVar1 * 6) * 2u)))) = (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe7206u + (uint32_t)(iVar1 * 6) * 2u)))) | actions[3];
    (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe7208u + (uint32_t)(iVar1 * 6) * 2u)))) = (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe7208u + (uint32_t)(iVar1 * 6) * 2u)))) | uVar2;
    *(ushort *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe713cu + (uint32_t)(uVar3 * 2) * 1u)))) = *(ushort *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe713cu + (uint32_t)(uVar3 * 2) * 1u)))) & ~*actions;
    *(ushort *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe719cu + (uint32_t)(uVar3 * 2) * 1u)))) = *(ushort *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe719cu + (uint32_t)(uVar3 * 2) * 1u)))) & ~actions[4];
  }
  return;
}

void route_fault_action_mode_request(uint actions)

{
  char cVar1;
  char cVar2;
  short sVar3;
  ushort uVar4;
  bool bVar5;
  
  sVar3 = DAT_febeeb9a;
  cVar2 = DAT_febe8acb;
  cVar1 = DAT_febe8ac8;
  uVar4 = DAT_febe71ec & 0x8000;
  if (((actions & 1) == 0) && (((DAT_febe71ec & 0x8000) == 0 || ((actions >> 1 & 1) == 0)))) {
    if (((actions >> 3 & 1) == 0) &&
       (((DAT_febe71ec & 0x8000) == 0 || (uVar4 = 0, (actions & 0x10) == 0)))) {
      thunk_clear_indexed_request_and_set_complement_b14d2(uVar4);
      return;
    }
    latch_health_command_completion();
    if (cVar1 != '\0') {
      return;
    }
    bVar5 = cVar2 == '\0';
  }
  else {
    latch_health_command_completion();
    bVar5 = sVar3 == 0;
  }
  if (bVar5) {
    thunk_set_indexed_request_and_clear_complement_b15ac(0);
  }
  return;
}

void route_fault_status_actions(uint actions)

{
  ushort uVar1;
  uint32_t puVar2;
  uint mode;
  ushort uVar3;
  
  uVar1 = DAT_febeeb9a;
  uVar3 = DAT_febe71f0;
  puVar2 = 0xfebeb800u;
  if (((actions >> 2 & 1) == 0) && (((DAT_febe71ec & 0x8000) == 0 || ((actions >> 6 & 1) == 0)))) {
    if (((actions >> 1 & 1) == 0) && (((DAT_febe71ec & 0x8000) == 0 || ((actions >> 5 & 1) == 0))))
    {
      if (((actions & 1) == 0) && (((DAT_febe71ec & 0x8000) == 0 || ((actions >> 4 & 1) == 0)))) {
        set_owner4_limit_mode((uint)(DAT_febe71f0 <= DAT_000317de));
        if (0x5699 < uVar1) {
          uVar3 = 0;
        }
        goto LAB_0003c308;
      }
      mode = 2;
    }
    else {
      mode = 3;
    }
  }
  else {
    mode = 4;
  }
  set_owner4_limit_mode(mode);
  if (uVar3 <= DAT_000317de) {
    uVar3 = uVar3 + 1;
  }
LAB_0003c308:
  (*((ushort *)camry_host_ptr((uint32_t)((0xffffb9f0u + (uint32_t)((int)puVar2)))))) = uVar3;
  return;
}

void delay_then_request_both_channel_terminal_outputs_3c310(void)

{
  uchar uVar1;
  uchar uVar2;
  uint uVar3;
  uint32_t puVar4;
  byte bVar5;
  byte bVar6;
  
  uVar3 = output_request_status;
  uVar2 = channel_request_state.channel1_state;
  uVar1 = channel_request_state.channel0_state;
  bVar5 = DAT_febe71e8;
  bVar6 = DAT_febe71e5;
  puVar4 = 0xfebeb800u;
  set_channel_owner_request('\x02',0x20002);
  if ((uVar1 == '\0') && (uVar2 == '\0')) {
    if (bVar6 < DAT_000317d5) {
      bVar6 = bVar6 + 1;
    }
    else {
      cancel_terminal_output_ramp();
      set_output_request_word('\x02',0x70017001);
      if ((uVar3 & 0x70017001) == 0x70017001) {
        if (bVar5 < DAT_000317d6) {
          bVar5 = bVar5 + 1;
        }
        else {
          set_secondary_channel_request_bounded5_56e66(2, ((uint32_t)(0x20002u)));
        }
      }
    }
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffb9e5u + (uint32_t)((int)puVar4) * 1u)))) = bVar6;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffb9e8u + (uint32_t)((int)puVar4) * 1u)))) = bVar5;
  return;
}

void clear_both_channel_terminal_output_request_3c386(void)

{
  DAT_febe71e5 = 0;
  DAT_febe71e8 = 0;
  set_output_request_word('\x02',0);
  cancel_terminal_output_ramp();
  set_channel_owner_request('\x02',0);
  set_secondary_channel_request_bounded5_56e66(2,0);
  return;
}

void delay_then_request_channel_zero_terminal_output_3c3b2(void)

{
  uchar uVar1;
  uint32_t puVar2;
  byte bVar3;
  
  uVar1 = channel_request_state.channel0_state;
  bVar3 = DAT_febe71e6;
  puVar2 = 0xfebeb800u;
  set_channel_owner_request('\x03',2);
  if (uVar1 == '\0') {
    if (bVar3 < DAT_000317d5) {
      bVar3 = bVar3 + 1;
    }
    else {
      set_output_request_word('\x05',0x7001);
    }
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffb9e6u + (uint32_t)((int)puVar2) * 1u)))) = bVar3;
  return;
}

void clear_channel_zero_terminal_output_request_3c3ec(void)

{
  DAT_febe71e6 = 0;
  set_output_request_word('\x05',0);
  set_channel_owner_request('\x03',0);
  set_secondary_channel_request_bounded5_56e66(3,0);
  return;
}

void delay_then_request_channel_one_terminal_output_3c410(void)

{
  uchar uVar1;
  uint32_t puVar2;
  byte bVar3;
  
  uVar1 = channel_request_state.channel1_state;
  bVar3 = DAT_febe71e7;
  puVar2 = 0xfebeb800u;
  set_channel_owner_request('\x04',0x20000);
  if (uVar1 == '\0') {
    if (bVar3 < DAT_000317d5) {
      bVar3 = bVar3 + 1;
    }
    else {
      set_output_request_word('\x06',0x70010000);
    }
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffb9e7u + (uint32_t)((int)puVar2) * 1u)))) = bVar3;
  return;
}

void clear_channel_one_terminal_output_request_3c44c(void)

{
  DAT_febe71e7 = 0;
  set_output_request_word('\x06',0);
  set_channel_owner_request('\x04',0);
  set_secondary_channel_request_bounded5_56e66(4,0);
  return;
}

void route_fault_output_actions(uint actions)

{
  ushort uVar1;
  ushort uVar2;
  uint32_t puVar3;
  undefined4 uVar4;
  uint uVar5;
  ushort uVar6;
  
  uVar2 = DAT_febeeb9c;
  uVar1 = DAT_febe71ec & 0x8000;
  uVar6 = DAT_febe71ec & 3;
  if ((actions >> 0xe & 1) == 0) {
    if (((actions & 0x120) == 0x120) ||
       (((DAT_febe71ec & 0x8000) != 0 && ((actions >> 0xb & 1) != 0)))) {
      delay_then_request_both_channel_terminal_outputs_3c310();
    }
    else {
      if ((((actions & 0xc) == 0xc) ||
          (((DAT_febe71ec & 0x8000) != 0 && ((actions >> 10 & 1) != 0)))) && (DAT_febeeb9a == 0)) {
        set_output_request_word('\x02',0x70017001);
        cancel_terminal_output_ramp();
        puVar3 = (0x20002u);
      }
      else {
        if (((actions & 0x8080) != 0x8080) || (DAT_febeeb9a != 0)) {
          if ((actions >> 4 & 1) == 0) {
            clear_both_channel_terminal_output_request_3c386();
          }
          else {
            set_output_request_word('\x02',0);
            set_channel_owner_request('\x02',0x20002);
            set_secondary_channel_request_bounded5_56e66(2,0);
            request_terminal_output_ramp();
          }
          goto LAB_0003c53c;
        }
        set_output_request_word('\x02',0x70017001);
        cancel_terminal_output_ramp();
        puVar3 = (0x0);
      }
      set_secondary_channel_request_bounded5_56e66(2, (puVar3));
    }
  }
  else {
    set_output_request_word('\x02',0x70017001);
    cancel_terminal_output_ramp();
  }
LAB_0003c53c:
  if (uVar1 != 0) {
    return;
  }
  if (((actions & 0x20) == 0) || ((actions >> 8 & 1) != 0)) {
    if ((actions & 4) == 0) {
LAB_0003c596:
      if ((((actions >> 0xc & 1) == 0) || ((actions & 1) == 0)) ||
         (((actions >> 0xd & 1) != 0 || ((actions >> 1 & 1) != 0)))) {
        if ((((actions & 4) == 0) || ((actions >> 3 & 1) != 0)) || (0x2b4d < uVar2)) {
          if (uVar6 != 1) {
            clear_channel_zero_terminal_output_request_3c3ec();
          }
          goto LAB_0003c5f2;
        }
        set_output_request_word('\x05',0x7001);
        uVar5 = 0;
      }
      else {
LAB_0003c5ae:
        set_output_request_word('\x05',0x7001);
        uVar5 = 2;
      }
      set_channel_owner_request('\x03',uVar5);
      uVar4 = 0;
    }
    else {
      if ((((actions >> 6 & 1) == 0) || ((actions >> 3 & 1) != 0)) || ((actions >> 9 & 1) != 0)) {
        if ((((actions & 1) == 0) || ((actions >> 3 & 1) != 0)) || ((actions >> 1 & 1) != 0))
        goto LAB_0003c596;
        goto LAB_0003c5ae;
      }
      set_output_request_word('\x05',0x7001);
      set_channel_owner_request('\x03',2);
      uVar4 = 2;
    }
    set_secondary_channel_request_bounded5_56e66(3,uVar4);
  }
  else {
    delay_then_request_channel_zero_terminal_output_3c3b2();
  }
LAB_0003c5f2:
  if (((actions >> 8 & 1) != 0) && ((actions & 0x20) == 0)) {
    delay_then_request_channel_one_terminal_output_3c410();
    return;
  }
  if ((actions & 8) == 0) {
LAB_0003c648:
    if ((((actions >> 0xd & 1) != 0) && ((actions >> 1 & 1) != 0)) &&
       (((actions >> 0xc & 1) == 0 && ((actions & 1) == 0)))) goto LAB_0003c660;
    if ((((actions & 8) == 0) || ((actions >> 2 & 1) != 0)) || (0x2b4d < uVar2)) {
      if (uVar6 == 2) {
        return;
      }
      clear_channel_one_terminal_output_request_3c44c();
      return;
    }
    set_output_request_word('\x06',0x70010000);
    uVar5 = 0;
  }
  else {
    if ((((actions >> 9 & 1) != 0) && ((actions >> 2 & 1) == 0)) && ((actions >> 6 & 1) == 0)) {
      set_output_request_word('\x06',0x70010000);
      set_channel_owner_request('\x04',0x20000);
      uVar4 = 0x20000;
      goto LAB_0003c696;
    }
    if ((((actions >> 1 & 1) == 0) || ((actions >> 2 & 1) != 0)) || ((actions & 1) != 0))
    goto LAB_0003c648;
LAB_0003c660:
    set_output_request_word('\x06',0x70010000);
    uVar5 = 0x20000;
  }
  set_channel_owner_request('\x04',uVar5);
  uVar4 = 0;
LAB_0003c696:
  set_secondary_channel_request_bounded5_56e66(4,uVar4);
  return;
}

void route_fault_ancillary_actions(uint actions)

{
  bool bVar1;
  ushort uVar2;
  uint uVar3;
  ushort limit;
  ushort limit_00;
  undefined4 uVar4;
  ushort uVar5;
  
  uVar2 = DAT_00031802;
  limit_00 = DAT_00031800;
  uVar5 = DAT_febe71ec & 0x8000;
  if ((actions >> 0xc & 1) == 0) {
    thunk_clear_indexed_request_and_set_complement_b14d2(0xf);
  }
  else {
    thunk_set_indexed_request_and_clear_complement_b15ac(0xf);
  }
  bVar1 = (actions & 2) == 0;
  if (bVar1) {
    set_owner2_entry_inhibit(0);
    set_owner3_entry_inhibit(0);
  }
  else {
    set_owner2_entry_inhibit(1);
    set_owner3_entry_inhibit(1);
  }
  thunk_set_byte_febebdee_bc93a(!bVar1);
  limit = limit_00;
  if (((actions >> 2 & 1) == 0) && (limit = uVar2, (actions >> 3 & 1) == 0)) {
    release_output_code_limit_bank0('\x01');
  }
  else {
    set_output_code_limit_bank0('\x01',limit);
  }
  if (((actions >> 4 & 1) == 0) && (limit_00 = uVar2, (actions >> 5 & 1) == 0)) {
    release_output_code_limit_bank1('\x01');
  }
  else {
    set_output_code_limit_bank1('\x01',limit_00);
  }
  uVar3 = actions & 0x40;
  if (((uVar3 == 0) || ((actions >> 7 & 1) != 0)) || (uVar5 == 0x8000)) {
    if ((actions >> 7 & 1) != 0) {
      if ((uVar3 != 0) || (uVar5 == 0x8000)) goto LAB_0003c76a;
      uVar4 = 2;
      goto LAB_0003c76c;
    }
    if ((uVar5 == 0x8000) && (uVar3 != 0)) {
LAB_0003c76a:
      uVar4 = 3;
      goto LAB_0003c76c;
    }
  }
  else {
    uVar4 = 1;
LAB_0003c76c:
    set_request_word_8a48_bounded2_5693e(1,uVar4);
  }
  if ((((actions & 0x100) == 0) || ((actions >> 9 & 1) != 0)) || (uVar5 == 0x8000)) {
    if ((actions >> 9 & 1) == 0) {
      if (uVar5 != 0x8000) goto LAB_0003c7aa;
    }
    else if (((actions & 0x100) == 0) && (uVar5 != 0x8000)) {
      uVar4 = 2;
      goto LAB_0003c7a4;
    }
    uVar4 = 3;
  }
  else {
    uVar4 = 1;
  }
LAB_0003c7a4:
  set_combined_channel_request_bounded2_5719c(1,uVar4);
LAB_0003c7aa:
  uVar4 = 0x5a;
  if ((actions >> 10 & 1) != 0) {
    uVar4 = 0;
  }
  set_first_owner_gate_bounded3_570f4(2,uVar4);
  uVar4 = 0x5a;
  if ((actions >> 0xb & 1) != 0) {
    uVar4 = 0;
  }
  set_second_owner_gate_bounded3_57106(2,uVar4);
  if ((actions >> 0xd & 1) != 0) {
    set_request_word_8aa8_bounded6_56cda(2,4);
  }
  if ((actions >> 0xe & 1) != 0) {
    set_request_word_8aa8_bounded6_56cda(3,0x40000);
  }
  uVar4 = 0;
  if ((actions & 0x8000) != 0) {
    uVar4 = 0x5a;
  }
  set_byte_febe8143_4c5e8(uVar4);
  return;
}

void clear_six_receive_fault_tracking_pairs_3cb32(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  
  iVar3 = 0;
  do {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe744cu + (uint32_t)(iVar3) * 1u)))) = 0;
    iVar2 = iVar3 + 1;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe7452u + (uint32_t)(iVar3) * 1u)))) = 0;
    iVar1 = iVar3 + -5;
    iVar3 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  return;
}

void clear_receive_fault_tracking_and_auxiliary_flags_3cb48(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  
  DAT_febe7458 = 0;
  iVar3 = 0;
  do {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe7459u + (uint32_t)(iVar3) * 1u)))) = 0;
    iVar2 = iVar3 + 1;
    iVar1 = iVar3 + -1;
    iVar3 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  iVar3 = 0;
  do {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe745du + (uint32_t)(iVar3) * 1u)))) = 0;
    iVar2 = iVar3 + 1;
    iVar1 = iVar3 + -1;
    iVar3 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  iVar3 = 0;
  do {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe744cu + (uint32_t)(iVar3) * 1u)))) = 0;
    iVar2 = iVar3 + 1;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe7452u + (uint32_t)(iVar3) * 1u)))) = 0;
    iVar1 = iVar3 + -5;
    iVar3 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  DAT_febe745b = 0;
  DAT_febe745c = 0;
  return;
}

void publish_indexed_receive_fault_healthy_transition_3cb88(uint param_1)

{
  char cVar1;
  uint event;
  
  param_1 = param_1 & 0xff;
  if (param_1 < 6) {
    cVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe7452u + (uint32_t)(param_1) * 1u))));
    event = (uint)*(ushort *)(((undefined *)camry_host_ptr((uint32_t)(0x280a6u + (uint32_t)(param_1 * 8) * 1u))));
    if (((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe744cu + (uint32_t)(param_1) * 1u)))) != 'Z') && (event != 0)) {
      report_diagnostic_healthy_observed(event);
    }
    if (cVar1 == 'Z') {
      if (event != 0) {
        report_diagnostic_event_pass(event);
      }
      cVar1 = '\0';
    }
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe7452u + (uint32_t)(param_1) * 1u)))) = cVar1;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe744cu + (uint32_t)(param_1) * 1u)))) = 0x5a;
  }
  return;
}

void latch_and_report_indexed_receive_fault_failure_3cbe8(uint param_1)

{
  char cVar1;
  
  param_1 = param_1 & 0xff;
  if (param_1 < 6) {
    cVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x280a4u + (uint32_t)(param_1 * 8) * 1u))));
    if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe7452u + (uint32_t)(param_1) * 1u)))) != 'Z') {
      if (*(ushort *)(((undefined *)camry_host_ptr((uint32_t)(0x280a6u + (uint32_t)(param_1 * 8) * 1u)))) != 0) {
        report_diagnostic_event_failure((uint)*(ushort *)(((undefined *)camry_host_ptr((uint32_t)(0x280a6u + (uint32_t)(param_1 * 8) * 1u)))),0x32);
      }
      if (cVar1 != '\0') {
        increment_indexed_u16_counter_once_until_rearmed_545de(cVar1);
      }
    }
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe7452u + (uint32_t)(param_1) * 1u)))) = 0x5a;
  }
  return;
}

void publish_receive_fault_bank(uchar bank,uchar status)

{
  uchar status_00;
  
  if (status == '\0') {
    publish_indexed_receive_fault_healthy_transition_3cb88(bank);
    status_00 = '\0';
  }
  else if ((status >> 1 & 1) == 0) {
    status_00 = '\"';
  }
  else {
    latch_and_report_indexed_receive_fault_failure_3cbe8(bank);
    status_00 = 'D';
  }
  if (bank < 6) {
    set_communication_monitor_status((uint)(byte)(bank + 0x12),status_00);
  }
  return;
}

void publish_receive_fault_bank_and_clear_linked_failure_3cc74(byte param_1,uchar param_2)

{
  uint32_t puVar1;
  uint uVar2;
  
  puVar1 = 0xfebeb800u;
  if (param_1 < 6) {
    publish_receive_fault_bank(param_1,param_2);
    uVar2 = (uint)(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x280abu + (uint32_t)((uint)param_1 * 8) * 1u))));
    if ((uVar2 < 6) && ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbc52u + (uint32_t)((int)(puVar1 + uVar2)) * 1u)))) == 'Z')) {
      report_diagnostic_event_pass((uint)*(ushort *)(((undefined *)camry_host_ptr((uint32_t)(0x280a6u + (uint32_t)(uVar2 * 8) * 1u)))));
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbc52u + (uint32_t)((int)(puVar1 + uVar2)) * 1u)))) = 0;
    }
  }
  return;
}

void update_configured_receive_fault_banks(void)

{
  int iVar1;
  uchar bank;
  char cVar2;
  char cVar3;
  uchar status;
  uint uVar4;
  
  cVar3 = DAT_febee806;
  uVar4 = 0;
  do {
    iVar1 = uVar4 * 8;
    bank = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x280a8u + (uint32_t)(iVar1) * 1u))));
    status = get_application_receive_status((uint)(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x280a9u + (uint32_t)(iVar1) * 1u)))));
    cVar2 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x280aau + (uint32_t)(iVar1) * 1u))));
    if ((((int8_t)cVar2) == -0x5b) || ((cVar2 == '\0' && (cVar3 == '\0')))) {
      publish_receive_fault_bank(bank,status);
    }
    else if ((cVar2 == 'Z') && (cVar3 == 'Z')) {
      publish_receive_fault_bank_and_clear_linked_failure_3cc74(bank, status);
    }
    uVar4 = uVar4 + 1;
  } while (uVar4 < 6);
  return;
}

void report_event_76_on_7f3a_bit4_transition_3cd16(void)

{
  byte bVar1;
  uint32_t puVar2;
  int iVar3;
  
  puVar2 = 0xfebeb800u;
  bVar1 = (byte)DAT_febe7f3a & 0x10;
  if (((byte)DAT_febe7f3a & 0x10) == 0) {
    iVar3 = 0x5a;
  }
  else {
    puVar2 = 0xfebeb800u;
    if (DAT_febe7459 == '\0') {
      puVar2 = 0xfebeb800u;
      report_diagnostic_event_failure(0x76,0x32);
    }
    bVar1 = 0x5a;
    iVar3 = 0;
  }
  DAT_febe7459 = bVar1;
  if (iVar3 == 0x5a) {
    if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbc58u + (uint32_t)((int)puVar2) * 1u)))) != 'Z') {
      report_diagnostic_healthy_observed(0x76);
    }
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbc58u + (uint32_t)((int)puVar2) * 1u)))) = 0x5a;
  }
  return;
}

void report_event_a8_on_7f3a_bit5_transition_3cd72(void)

{
  byte bVar1;
  
  bVar1 = (byte)DAT_febe7f3a & 0x20;
  if (((byte)DAT_febe7f3a & 0x20) != 0) {
    if (DAT_febe745d == '\0') {
      report_diagnostic_event_failure(0xa8,0x32);
    }
    bVar1 = 0x5a;
  }
  DAT_febe745d = bVar1;
  return;
}

undefined1 report_a9_b4_b9_flags_below_e8cc_limit_3cda8(void)

{
  uchar uVar1;
  char cVar2;
  char cVar3;
  ushort uVar4;
  uint32_t puVar5;
  undefined *puVar6;
  undefined1 uVar8;
  char cVar9;
  uint32_t puVar7;
  uVar4 = DAT_febee8cc;
  cVar3 = DAT_febe7f6b;
  cVar2 = DAT_febe7f6a;
  uVar1 = internal_source_admission_state;
  uVar8 = DAT_febe745c;
  puVar7 = 0xfebeb800u;
  puVar6 = ((undefined *)camry_host_ptr(0xfebeb800u));
  cVar9 = DAT_febe745b;
  puVar5 = (0xfebeb800u);
  if (DAT_febe7f69 == 'Z') {
    if (DAT_febe745b == 'Z') goto LAB_0003cdf8;
    if (0x6ff < DAT_febee8cc) goto LAB_0003ce22;
    puVar6 = ((undefined *)camry_host_ptr(0xfebeb800u));
    report_diagnostic_event_failure(0xa9,0x32);
    cVar9 = 'Z';
  }
  else {
    if (DAT_febe745b == 'Z') {
      report_diagnostic_event_pass(0xa9);
      cVar9 = '\0';
      puVar5 = ((uint32_t)(puVar7));
    }
LAB_0003cdf8:
    puVar6 = ((void *)camry_host_ptr((uint32_t)(puVar5)));
    if (0x6ff < uVar4) goto LAB_0003ce22;
  }
  if (cVar2 == 'Z') {
    report_diagnostic_event_failure(0xb4,0x32);
  }
  if (cVar3 == 'Z') {
    report_diagnostic_event_failure(0xb9,0x32);
  }
LAB_0003ce22:
  if (uVar1 == '\x03') {
    uVar8 = 0x44;
  }
  else if (uVar1 == '\0') {
    uVar8 = 0;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbc5bu + (uint32_t)((int)camry_host_addr(puVar6)) * 1u)))) = cVar9;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbc5cu + (uint32_t)((int)camry_host_addr(puVar6)) * 1u)))) = uVar8;
  return uVar8;
}

uchar update_communication_qualification_monitors(void)

{
  uchar status;
  
  update_configured_receive_fault_banks();
  report_event_76_on_7f3a_bit4_transition_3cd16();
  report_event_a8_on_7f3a_bit5_transition_3cd72();
  status = report_a9_b4_b9_flags_below_e8cc_limit_3cda8();
  set_communication_monitor_status(0,status);
  return status;
}

void return_only_stub_3ce60(void)

{
  return;
}

void return_only_stub_3ce62(void)

{
  return;
}

void publish_af_103_healthy_from_e91c_signature_3ce64(void)

{
  uchar uVar1;
  uint32_t puVar2;
  char cVar3;
  char cVar4;
  
  uVar1 = route30_receive_status;
  cVar3 = DAT_febe7465;
  cVar4 = DAT_febe7464;
  puVar2 = 0xfebeb800u;
  if (DAT_febee91c == 0x55aaaa55) {
    puVar2 = 0xfebeb800u;
    report_diagnostic_healthy_observed(0x103);
    cVar3 = 'Z';
    if ((uVar1 == '\0') && (cVar4 != 'Z')) {
      report_diagnostic_healthy_observed(0xaf);
      cVar4 = cVar3;
    }
  }
  else if (DAT_febee91c == -0x55aaaa56) {
    puVar2 = 0xfebeb800u;
    report_diagnostic_healthy_observed(0xaf);
    cVar4 = 'Z';
    if ((uVar1 == '\0') && (cVar3 != 'Z')) {
      report_diagnostic_healthy_observed(0x103);
      cVar3 = cVar4;
    }
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbc64u + (uint32_t)((int)puVar2) * 1u)))) = cVar4;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbc65u + (uint32_t)((int)puVar2) * 1u)))) = cVar3;
  return;
}

void publish_selected_source_fault_edges(void)

{
  char cVar1;
  char cVar2;
  char cVar3;
  char cVar4;
  uint32_t puVar5;
  uchar status;
  uchar status_00;
  uchar status_01;
  uchar status_02;
  int iVar6;
  char cVar7;
  char cVar8;
  char cVar9;
  char cVar10;
  char cVar11;
  
  cVar4 = DAT_febe7fa5;
  cVar3 = DAT_febe7fa4;
  cVar2 = DAT_febe7fa3;
  cVar1 = DAT_febe7fa2;
  cVar8 = DAT_febe7463;
  cVar10 = DAT_febe7462;
  cVar9 = DAT_febe7461;
  cVar11 = DAT_febe7460;
  puVar5 = 0xfebeb800u;
  cVar7 = '\0';
  iVar6 = 0;
  publish_af_103_healthy_from_e91c_signature_3ce64();
  if (cVar1 == 'Z') {
    if (cVar11 != 'Z') {
      report_diagnostic_event_failure(0xab,0x32);
      cVar11 = 'Z';
      cVar7 = 'Z';
    }
    status_02 = '\"';
  }
  else {
    if (cVar11 == 'Z') {
      report_diagnostic_event_pass(0xab);
      cVar11 = '\0';
      iVar6 = 0x5a;
    }
    status_02 = '\0';
  }
  if (cVar3 == 'Z') {
    if (cVar10 != 'Z') {
      report_diagnostic_event_failure(0x102,0x32);
      cVar10 = 'Z';
      cVar7 = 'Z';
    }
    status_01 = '\"';
  }
  else {
    if (cVar10 == 'Z') {
      report_diagnostic_event_pass(0x102);
      cVar10 = '\0';
      iVar6 = 0x5a;
    }
    status_01 = '\0';
  }
  if (cVar2 == 'Z') {
    if (cVar9 != 'Z') {
      report_diagnostic_event_failure(0xaf,0x32);
      cVar9 = 'Z';
      cVar7 = 'Z';
    }
    status_00 = '\"';
  }
  else {
    if (cVar9 == 'Z') {
      report_diagnostic_event_pass(0xaf);
      cVar9 = '\0';
      iVar6 = 0x5a;
    }
    status_00 = '\0';
  }
  if (cVar4 == 'Z') {
    if (cVar8 != 'Z') {
      report_diagnostic_event_failure(0x103,0x32);
      cVar8 = 'Z';
      cVar7 = 'Z';
    }
    status = '\"';
  }
  else {
    if (cVar8 == 'Z') {
      report_diagnostic_event_pass(0x103);
      cVar8 = '\0';
      iVar6 = 0x5a;
    }
    status = '\0';
  }
  if (iVar6 == 0x5a) {
    clear_indexed_counter_rearm_byte_54724(5);
  }
  if (cVar7 == 'Z') {
    increment_indexed_u16_counter_once_until_rearmed_545de(5);
  }
  set_communication_monitor_status(2,status_02);
  set_communication_monitor_status(4,status_01);
  set_communication_monitor_status(3,status_00);
  set_communication_monitor_status(5,status);
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbc60u + (uint32_t)((int)puVar5) * 1u)))) = cVar11;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbc62u + (uint32_t)((int)puVar5) * 1u)))) = cVar10;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbc61u + (uint32_t)((int)puVar5) * 1u)))) = cVar9;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbc63u + (uint32_t)((int)puVar5) * 1u)))) = cVar8;
  return;
}
