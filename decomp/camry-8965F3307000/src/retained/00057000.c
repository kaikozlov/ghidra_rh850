#include "common.h"

void return_only_stub_57000(void)

{
  return;
}

void report_event28_once_for_any_crypto_profile_flag_57002(void)

{
  undefined *puVar1;
  byte bVar3;
  int iVar4;
  int iVar5;
  char cVar6;
  byte bVar7;
  undefined8 uVar2;
  
  cVar6 = DAT_febe8b04;
  uVar2 = 0xfebeb800;
  puVar1 = ((undefined *)camry_host_ptr(0xfebeb800u));
  if (DAT_febe8b04 != 'Z') {
    bVar3 = crypto_config_profile_count;
    if (2 < crypto_config_profile_count) {
      bVar3 = 2;
    }
    iVar5 = 0;
    for (bVar7 = 0; puVar1 = ((undefined *)camry_host_ptr((uint32_t)(uVar2))), bVar7 < bVar3; bVar7 = bVar7 + 1) {
      iVar4 = get_crypto_profile_failure_for_index_below_two_6a180(bVar7);
      if (iVar4 == 0x5a) {
        iVar5 = 0x5a;
      }
    }
    if (iVar5 == 0x5a) {
      gate_indexed_event_payload_during_diagnostic_clears_51cf6(0x28,0x32);
      cVar6 = 'Z';
    }
  }
  puVar1[-0x2cfc] = cVar6;
  return;
}

void reset_event28_profile_report_latch_5704e(void)

{
  DAT_febe8b04 = 0;
  return;
}

void return_only_stub_57054(void)

{
  return;
}

void return_only_stub_57056(void)

{
  return;
}

void consume_5aa5_aa55_status_and_update_count_57058(void)

{
  uint32_t puVar1;
  int iVar2;
  int iVar3;
  undefined1 uVar4;
  short sStack_e;
  
  puVar1 = 0xfebeb800u;
  iVar2 = zero_output_halfword_and_return_success_62d56(&sStack_e);
  return_only_stub_62d54();
  iVar3 = get_indexed_u16_counter_or_zero_546f2(1);
  if ((iVar2 == 0) && ((sStack_e == 0x5aa5 || (sStack_e == -0x55ab)))) {
    iVar3 = iVar3 + 1;
    if (sStack_e == 0x5aa5) {
      uVar4 = 1;
    }
    else {
      uVar4 = 3;
    }
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x2cf8))))) = uVar4;
    increment_indexed_u16_counter_once_until_rearmed_545de(1);
  }
  (*((int *)camry_host_ptr((uint32_t)(puVar1 + -0x2cf4)))) = iVar3;
  return;
}

void return_only_stub_570a6(void)

{
  return;
}

void return_only_stub_570a8(void)

{
  return;
}

void and_three_owner_gates_for_two_status_outputs_570aa(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  
  DAT_febe8b17 = 0x5a;
  iVar3 = 0;
  DAT_febe8b10 = DAT_febe8b17;
  do {
    iVar2 = iVar3 + 1;
    DAT_febe8b10 = DAT_febe8b10 & (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe8b11u + (uint32_t)(iVar3) * 1u))));
    iVar1 = iVar3 + -2;
    iVar3 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  iVar3 = 0;
  do {
    iVar2 = iVar3 + 1;
    DAT_febe8b17 = DAT_febe8b17 & (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe8b14u + (uint32_t)(iVar3) * 1u))));
    iVar1 = iVar3 + -2;
    iVar3 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  if (DAT_febe8b10 == 0x5a) {
    DAT_febe3887 = 0xff;
  }
  else {
    DAT_febe3887 = 0;
  }
  if (DAT_febe8b17 == 0x5a) {
    DAT_febe3886 = 0xff;
  }
  else {
    DAT_febe3886 = 0;
  }
  return;
}

void set_first_owner_gate_bounded3_570f4(uint param_1,undefined1 param_2)

{
  if ((param_1 & 0xff) < 3) {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe8b11u + (uint32_t)(param_1 & 0xff) * 1u)))) = param_2;
  }
  return;
}

void set_second_owner_gate_bounded3_57106(uint param_1,undefined1 param_2)

{
  if ((param_1 & 0xff) < 3) {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe8b14u + (uint32_t)(param_1 & 0xff) * 1u)))) = param_2;
  }
  return;
}

void return_only_stub_57118(void)

{
  return;
}

void clear_two_combined_channel_request_words_5711a(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  
  iVar3 = 0;
  do {
    iVar2 = iVar3 + 1;
    *(undefined4 *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe8b1cu + (uint32_t)(iVar3 * 4) * 1u)))) = 0;
    iVar1 = iVar3 + -1;
    iVar3 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  return;
}

void combine_owner_requests_with_both_channel_masks_57130(void)

{
  int iVar1;
  int iVar2;
  uint uVar3;
  int iVar4;
  
  uVar3 = 0;
  iVar4 = 0;
  do {
    iVar2 = iVar4 + 1;
    uVar3 = uVar3 | *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe8b1cu + (uint32_t)(iVar4 * 4) * 1u))));
    iVar1 = iVar4 + -1;
    iVar4 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  if (((uVar3 >> 0x10 & 1) == 0) &&
     ((((uVar3 & 1) == 0 || ((channel_request_state.observed_mismatch & 2) == 0)) ||
      ((DAT_febe8ae4 & 2) == 0)))) {
    DAT_febe8b18 = 0;
    DAT_febe387b = 0;
  }
  else {
    DAT_febe8b18 = 1;
    DAT_febe387b = 0xff;
  }
  if (((uVar3 & 0x20000) == 0) &&
     ((((uVar3 >> 1 & 1) == 0 || ((channel_request_state.observed_mismatch >> 0x11 & 1) == 0))
      || ((DAT_febe8ae4 >> 0x11 & 1) == 0)))) {
    DAT_febe387a = 0;
  }
  else {
    DAT_febe8b18 = DAT_febe8b18 | 2;
    DAT_febe387a = 0xff;
  }
  return;
}

void set_combined_channel_request_bounded2_5719c(uint param_1,undefined4 param_2)

{
  if ((param_1 & 0xff) < 2) {
    *(undefined4 *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe8b1cu + (uint32_t)((param_1 & 0xff) * 4) * 1u)))) = param_2;
  }
  return;
}

void return_only_stub_571b0(void)

{
  return;
}

void return_only_stub_571b2(void)

{
  return;
}

uint apply_output_request_port_levels(uint request)

{
  bool bVar1;
  uint uVar2;
  
  if (((uint32_t)((uint32_t)(output_request_status & 0x20002)))==((uint32_t)(0x20002u))) {
    if ((request & 0x10001) == 0x10001) {
      write_output_bank0_port_level_b();
      write_output_bank1_port_level_b();
    }
    else if ((request & 0x10001) == 0) {
      write_output_bank0_port_level_a();
      write_output_bank1_port_level_a();
    }
  }
  bVar1 = (request & 1) == 0;
  if (bVar1) {
    write_output_bank0_port_level_a();
  }
  else {
    write_output_bank0_port_level_b();
  }
  uVar2 = (uint)!bVar1;
  if ((request >> 0x10 & 1) == 0) {
    write_output_bank1_port_level_a();
  }
  else {
    write_output_bank1_port_level_b();
    uVar2 = uVar2 | 0x10000;
  }
  return uVar2;
}

uint stage_output_request_phase_masks(uint request)

{
  uint uVar1;
  uint32_t puVar2;
  byte mask;
  byte mask_00;
  uint uVar3;
  
  puVar2 = 0xfebeb800u;
  mask = 0x3f;
  uVar3 = 0;
  mask_00 = mask;
  if ((request >> 2 & 1) != 0) {
    mask_00 = 0x38;
  }
  if ((request >> 0xc & 1) != 0) {
    mask_00 = mask_00 & 0xf6;
    uVar3 = 0x1000;
  }
  if ((request >> 0xd & 1) != 0) {
    uVar3 = uVar3 | 0x2000;
    mask_00 = mask_00 & 0xed;
  }
  if ((request >> 0xe & 1) != 0) {
    mask_00 = mask_00 & 0x1b;
    uVar3 = uVar3 | 0x4000;
  }
  if ((request & 0x7000) == 0x7000) {
    uVar3 = uVar3 | 2;
  }
  else if ((mask_00 & 7) == 0) {
    uVar3 = uVar3 | 4;
  }
  if ((request >> 0x12 & 1) != 0) {
    mask = 0x38;
  }
  if ((request >> 0x1c & 1) != 0) {
    mask = mask & 0xf6;
    uVar3 = uVar3 | 0x10000000;
  }
  if ((request >> 0x1d & 1) != 0) {
    mask = mask & 0xed;
    uVar3 = uVar3 | 0x20000000;
  }
  if ((request >> 0x1e & 1) != 0) {
    mask = mask & 0x1b;
    uVar3 = uVar3 | 0x40000000;
  }
  if ((request & 0x7fffffff) >> 0x1c == 7) {
    uVar1 = 0x20000;
  }
  else {
    if ((mask & 7) != 0) goto LAB_000572cc;
    uVar1 = 0x40000;
  }
  uVar3 = uVar3 | uVar1;
LAB_000572cc:
  stage_output_bank0_phase_mask(mask_00);
  stage_output_bank1_phase_mask(mask);
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x2cdc))))) = mask_00;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x2cdb))))) = mask;
  return uVar3;
}

void publish_aggregate_output_requests(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  uint32_t puVar4;
  uint uVar5;
  uint uVar6;
  ushort codes[3];
  
  puVar4 = 0xfebeb800u;
  uVar6 = 0;
  iVar3 = 0;
  do {
    iVar2 = iVar3 + 1;
    uVar6 = uVar6 | (*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xfebe8b2cu + (uint32_t)(iVar3) * 4u))));
    iVar1 = iVar3 + -7;
    iVar3 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  uVar5 = apply_output_request_port_levels(uVar6);
  uVar6 = stage_output_request_phase_masks(uVar6);
  uVar5 = uVar5 | uVar6;
  if ((uVar5 & 3) == 0) {
    release_phase_output_slot_bank0('\x03');
  }
  else {
    codes[0] = DAT_00031908;
    codes[1] = DAT_00031908;
    codes[2] = DAT_00031908;
    write_phase_output_slot_bank0(10,'\x03',codes);
    activate_phase_output_slot_bank0('\x03');
  }
  if ((uVar5 & 0x30000) == 0) {
    release_phase_output_slot_bank1('\x03');
  }
  else {
    codes[0] = DAT_00031908;
    codes[1] = DAT_00031908;
    codes[2] = DAT_00031908;
    write_phase_output_slot_bank1(10,'\x03',codes);
    activate_phase_output_slot_bank1('\x03');
  }
  (*((uint *)camry_host_ptr((uint32_t)(puVar4 + -0x2cd8)))) = uVar5;
  return;
}

void return_only_stub_5738e(void)

{
  return;
}

void initialize_direct_output_requests(void)

{
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe8b4cu + (uint32_t)(1) * 1u)))) = '\0';
  ((volatile uint8_t *)camry_host_ptr(0xfebe8b4cu))[0] = '\0';
  (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe8b54u + (uint32_t)(2) * 2u)))) = 0x4000;
  (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe8b54u + (uint32_t)(1) * 2u)))) = 0x4000;
  ((volatile uint16_t *)camry_host_ptr(0xfebe8b54u))[0] = 0x4000;
  (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe8b4eu + (uint32_t)(2) * 2u)))) = 0x4000;
  (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe8b4eu + (uint32_t)(1) * 2u)))) = 0x4000;
  ((volatile uint16_t *)camry_host_ptr(0xfebe8b4eu))[0] = 0x4000;
  return;
}

void publish_direct_output_requests(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  if (((volatile uint8_t *)camry_host_ptr(0xfebe8b4cu))[0] == '\0') {
    release_phase_output_slot_bank0('\x04');
  }
  else {
    puVar1 = 0xfebeb800u;
    write_phase_output_slot_bank0(10,'\x04',direct_output_codes_bank0);
    activate_phase_output_slot_bank0('\x04');
  }
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x2cb3))))) == '\0') {
    release_phase_output_slot_bank1('\x04');
  }
  else {
    write_phase_output_slot_bank1(10,'\x04',direct_output_codes_bank1);
    activate_phase_output_slot_bank1('\x04');
  }
  return;
}

void return_only_stub_57458(void)

{
  return;
}

void fill_constant_block_5745a(void)

{
  DAT_febe8b5c = 0;
  DAT_febe8b5d = 0;
  DAT_febe8b5e = 0;
  DAT_febe8b5f = 0;
  DAT_febe8b6c = 0x4000;
  DAT_febe8b6e = 0x4000;
  DAT_febe8b70 = 0x4000;
  DAT_febe8b72 = 0x4000;
  DAT_febe8b74 = 0x4000;
  DAT_febe8b76 = 0x4000;
  DAT_febe8b78 = 0x4000;
  DAT_febe8b7a = 0x4000;
  DAT_febe8b7c = 0x4000;
  DAT_febe8b7e = 0x4000;
  DAT_febe8b80 = 0x4000;
  DAT_febe8b82 = 0x4000;
  return;
}

void stage_phase_output_history(void)

{
  undefined2 uVar1;
  char cVar2;
  ushort uVar3;
  ushort uVar4;
  ushort uVar5;
  uint32_t puVar6;
  ushort uVar7;
  uint uVar8;
  ushort uVar9;
  uint uVar10;
  ushort uVar11;
  uint uVar12;
  uint uVar13;
  undefined1 uVar14;
  
  uVar5 = DAT_febe8bf2;
  uVar4 = DAT_febe8bf0;
  uVar3 = DAT_febe8bee;
  cVar2 = DAT_febe8bae;
  puVar6 = 0xfebeb800u;
  uVar13 = (uint)DAT_0003190e;
  if (((DAT_febe8bae == '\0') && (DAT_febe8b5c == '\0')) && (DAT_0003190c != 'Z')) {
    uVar8 = (uint)DAT_febe8b6c + (uint)DAT_febe8bee >> 1;
    DAT_febe8b60 = (ushort)uVar8;
    uVar10 = (uint)DAT_febe8b6e + (uint)DAT_febe8bf0 >> 1;
    DAT_febe8b62 = (ushort)uVar10;
    uVar12 = (uint)DAT_febe8b70 + (uint)DAT_febe8bf2 >> 1;
    DAT_febe8b64 = (ushort)uVar12;
    if ((((uVar8 < 0x8000) && (uVar13 < uVar8)) || ((uVar10 < 0x8000 && (uVar13 < uVar10)))) ||
       ((uVar12 < 0x8000 && (uVar13 < uVar12)))) goto LAB_000574f2;
    uVar14 = 0x5a;
  }
  else {
LAB_000574f2:
    uVar14 = 0;
    DAT_febe8b60 = DAT_febe8bee;
    DAT_febe8b62 = DAT_febe8bf0;
    DAT_febe8b64 = DAT_febe8bf2;
  }
  stage_channel0_word_pwm_compares_669f6(DAT_febe8b60, DAT_febe8b62, DAT_febe8b64);
  uVar1 = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar6 + -0x2c94))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(-0x2ca4))))) = cVar2;
  cVar2 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(-0x2c51)))));
  (*((ushort *)camry_host_ptr((uint32_t)(puVar6 + -0x2c94)))) = uVar3;
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar6 + -0x2c88)))) = uVar1;
  uVar1 = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar6 + -0x2c92))));
  (*((ushort *)camry_host_ptr((uint32_t)(puVar6 + -0x2c92)))) = uVar4;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(-0x2ca2))))) = uVar14;
  uVar3 = (*((ushort *)camry_host_ptr((uint32_t)(puVar6 + -0x2c0c))));
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar6 + -0x2c86)))) = uVar1;
  uVar1 = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar6 + -0x2c90))));
  (*((ushort *)camry_host_ptr((uint32_t)(puVar6 + -0x2c90)))) = uVar5;
  uVar4 = (*((ushort *)camry_host_ptr((uint32_t)(puVar6 + -0x2c0a))));
  uVar5 = (*((ushort *)camry_host_ptr((uint32_t)(puVar6 + -0x2c08))));
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar6 + -0x2c84)))) = uVar1;
  if (((cVar2 == '\0') && ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(-0x2ca3))))) == '\0')) && (DAT_0003190c != 'Z')) {
    uVar8 = (uint)(*((ushort *)camry_host_ptr((uint32_t)(puVar6 + -0x2c8e)))) + (uint)uVar3 >> 1;
    uVar10 = (uint)(*((ushort *)camry_host_ptr((uint32_t)(puVar6 + -0x2c8c)))) + (uint)uVar4 >> 1;
    uVar12 = (uint)(*((ushort *)camry_host_ptr((uint32_t)(puVar6 + -0x2c8a)))) + (uint)uVar5 >> 1;
    if ((((0x7fff < (int)uVar8) || ((int)uVar8 <= (int)uVar13)) && ((0x7fff < (int)uVar10 || ((int)uVar10 <= (int)uVar13)))) &&
       ((0x7fff < (int)uVar12 || ((int)uVar12 <= (int)uVar13)))) {
      uVar14 = 0x5a;
      uVar7 = (ushort)uVar8;
      uVar9 = (ushort)uVar10;
      uVar11 = (ushort)uVar12;
      goto LAB_00057584;
    }
  }
  uVar14 = 0;
  uVar7 = uVar3;
  uVar9 = uVar4;
  uVar11 = uVar5;
LAB_00057584:
  (*((ushort *)camry_host_ptr((uint32_t)(puVar6 + -0x2c9a)))) = uVar7;
  (*((ushort *)camry_host_ptr((uint32_t)(puVar6 + -0x2c98)))) = uVar9;
  (*((ushort *)camry_host_ptr((uint32_t)(puVar6 + -0x2c96)))) = uVar11;
  stage_channel1_word_pwm_compares_66a5c(uVar7, uVar9, uVar11);
  uVar1 = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar6 + -0x2c8e))));
  (*((ushort *)camry_host_ptr((uint32_t)(puVar6 + -0x2c8e)))) = uVar3;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(-0x2ca3))))) = cVar2;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(-0x2ca1))))) = uVar14;
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar6 + -0x2c82)))) = uVar1;
  uVar1 = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar6 + -0x2c8c))));
  (*((ushort *)camry_host_ptr((uint32_t)(puVar6 + -0x2c8c)))) = uVar4;
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar6 + -0x2c80)))) = uVar1;
  uVar1 = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar6 + -0x2c8a))));
  (*((ushort *)camry_host_ptr((uint32_t)(puVar6 + -0x2c8a)))) = uVar5;
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar6 + -0x2c7e)))) = uVar1;
  return;
}

void initialize_halfword_pair_8b84_to_7fff_575ac(void)

{
  DAT_febe8b84 = 0x7fff;
  DAT_febe8b86 = 0x7fff;
  return;
}

void initialize_output_code_limit_requests(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  
  iVar3 = 0;
  do {
    *(undefined2 *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe8b8au + (uint32_t)(iVar3 * 2) * 1u)))) = 0x8000;
    iVar2 = iVar3 + 1;
    iVar1 = iVar3 + -2;
    iVar3 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  iVar3 = 0;
  do {
    iVar2 = iVar3 + 1;
    *(undefined2 *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe8b94u + (uint32_t)(iVar3 * 2) * 1u)))) = 0x8000;
    iVar1 = iVar3 + -2;
    iVar3 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  DAT_febe8b90 = 0x8000;
  DAT_febe8b9a = 0x8000;
  DAT_febe8b84 = 0x7fff;
  DAT_febe8b86 = 0x7fff;
  return;
}

void reduce_phase_output_code_limits(void)

{
  int iVar1;
  int iVar2;
  uint uVar3;
  int iVar4;
  uint uVar5;
  
  uVar3 = (uint)DAT_febe8b90;
  uVar5 = (uint)DAT_febe8b9a;
  if (uVar3 != (ushort)~DAT_febe8b84) {
    uVar3 = 0x8000;
    iVar4 = 0;
    do {
      if ((int)(*(ushort *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe8b8au + (uint32_t)(iVar4 * 2) * 1u)))) - uVar3) < 0) {
        uVar3 = (uint)*(ushort *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe8b8au + (uint32_t)(iVar4 * 2) * 1u))));
      }
      iVar2 = iVar4 + 1;
      iVar1 = iVar4 + -2;
      iVar4 = iVar2;
    } while (((iVar1 < 0) || (iVar2 < 0)));
    DAT_febe8b90 = (ushort)uVar3;
    DAT_febe8b84 = ~DAT_febe8b90;
  }
  if (uVar5 != (ushort)~DAT_febe8b86) {
    uVar5 = 0x8000;
    iVar4 = 0;
    do {
      if ((int)(*(ushort *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe8b94u + (uint32_t)(iVar4 * 2) * 1u)))) - uVar5) < 0) {
        uVar5 = (uint)*(ushort *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe8b94u + (uint32_t)(iVar4 * 2) * 1u))));
      }
      iVar2 = iVar4 + 1;
      iVar1 = iVar4 + -2;
      iVar4 = iVar2;
    } while (((iVar1 < 0) || (iVar2 < 0)));
    DAT_febe8b9a = (ushort)uVar5;
    DAT_febe8b86 = ~DAT_febe8b9a;
  }
  DAT_febe8b88 = 0;
  if (uVar3 < 0x8000) {
    DAT_febe8b88 = 0x5a;
  }
  DAT_febe8b89 = 0;
  if (uVar5 < 0x8000) {
    DAT_febe8b89 = 0x5a;
  }
  DAT_febe8b92 = (short)uVar3;
  DAT_febe8b9c = (short)uVar5;
  return;
}

void set_output_code_limit_bank0(uchar owner,ushort limit)

{
  int iVar1;
  int iVar2;
  uint uVar3;
  int iVar4;
  
  if (owner < 3) {
    iVar4 = (uint)owner * 2;
    if (*(ushort *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe8b8au + (uint32_t)(iVar4) * 1u)))) == limit) {
      if (DAT_febe8b90 <= limit) {
        return;
      }
      uVar3 = 0x8000;
      iVar4 = 0;
      do {
        if ((int)(*(ushort *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe8b8au + (uint32_t)(iVar4 * 2) * 1u)))) - uVar3) < 0) {
          uVar3 = (uint)*(ushort *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe8b8au + (uint32_t)(iVar4 * 2) * 1u))));
        }
        iVar2 = iVar4 + 1;
        iVar1 = iVar4 + -2;
        iVar4 = iVar2;
      } while (((iVar1 < 0) || (iVar2 < 0)));
      DAT_febe8b90 = (ushort)uVar3;
    }
    else {
      *(ushort *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe8b8au + (uint32_t)(iVar4) * 1u)))) = limit;
      uVar3 = 0x8000;
      iVar4 = 0;
      do {
        if ((int)(*(ushort *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe8b8au + (uint32_t)(iVar4 * 2) * 1u)))) - uVar3) < 0) {
          uVar3 = (uint)*(ushort *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe8b8au + (uint32_t)(iVar4 * 2) * 1u))));
        }
        iVar2 = iVar4 + 1;
        iVar1 = iVar4 + -2;
        iVar4 = iVar2;
      } while (((iVar1 < 0) || (iVar2 < 0)));
      DAT_febe8b90 = (ushort)uVar3;
    }
    DAT_febe8b84 = ~(ushort)uVar3;
  }
  return;
}

void set_output_code_limit_bank1(uchar owner,ushort limit)

{
  int iVar1;
  int iVar2;
  uint uVar3;
  int iVar4;
  
  if (owner < 3) {
    iVar4 = (uint)owner * 2;
    if (*(ushort *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe8b94u + (uint32_t)(iVar4) * 1u)))) == limit) {
      if (DAT_febe8b9a <= limit) {
        return;
      }
      uVar3 = 0x8000;
      iVar4 = 0;
      do {
        if ((int)(*(ushort *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe8b94u + (uint32_t)(iVar4 * 2) * 1u)))) - uVar3) < 0) {
          uVar3 = (uint)*(ushort *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe8b94u + (uint32_t)(iVar4 * 2) * 1u))));
        }
        iVar2 = iVar4 + 1;
        iVar1 = iVar4 + -2;
        iVar4 = iVar2;
      } while (((iVar1 < 0) || (iVar2 < 0)));
      DAT_febe8b9a = (ushort)uVar3;
    }
    else {
      *(ushort *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe8b94u + (uint32_t)(iVar4) * 1u)))) = limit;
      uVar3 = 0x8000;
      iVar4 = 0;
      do {
        if ((int)(*(ushort *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe8b94u + (uint32_t)(iVar4 * 2) * 1u)))) - uVar3) < 0) {
          uVar3 = (uint)*(ushort *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe8b94u + (uint32_t)(iVar4 * 2) * 1u))));
        }
        iVar2 = iVar4 + 1;
        iVar1 = iVar4 + -2;
        iVar4 = iVar2;
      } while (((iVar1 < 0) || (iVar2 < 0)));
      DAT_febe8b9a = (ushort)uVar3;
    }
    DAT_febe8b86 = ~(ushort)uVar3;
  }
  return;
}

void release_output_code_limit_bank0(uchar owner)

{
  int iVar1;
  int iVar2;
  int iVar3;
  uint uVar4;
  
  if (owner < 3) {
    iVar3 = (uint)owner * 2;
    uVar4 = 0x8000;
    if (*(short *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe8b8au + (uint32_t)(iVar3) * 1u)))) == -0x8000) {
      if (DAT_febe8b90 < 0x8001) {
        return;
      }
      iVar3 = 0;
      do {
        if ((int)(*(ushort *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe8b8au + (uint32_t)(iVar3 * 2) * 1u)))) - uVar4) < 0) {
          uVar4 = (uint)*(ushort *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe8b8au + (uint32_t)(iVar3 * 2) * 1u))));
        }
        iVar2 = iVar3 + 1;
        iVar1 = iVar3 + -2;
        iVar3 = iVar2;
      } while (((iVar1 < 0) || (iVar2 < 0)));
      DAT_febe8b90 = (ushort)uVar4;
    }
    else {
      *(undefined2 *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe8b8au + (uint32_t)(iVar3) * 1u)))) = 0x8000;
      uVar4 = 0x8000;
      iVar3 = 0;
      do {
        if ((int)(*(ushort *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe8b8au + (uint32_t)(iVar3 * 2) * 1u)))) - uVar4) < 0) {
          uVar4 = (uint)*(ushort *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe8b8au + (uint32_t)(iVar3 * 2) * 1u))));
        }
        iVar2 = iVar3 + 1;
        iVar1 = iVar3 + -2;
        iVar3 = iVar2;
      } while (((iVar1 < 0) || (iVar2 < 0)));
      DAT_febe8b90 = (ushort)uVar4;
    }
    DAT_febe8b84 = ~(ushort)uVar4;
  }
  return;
}

void release_output_code_limit_bank1(uchar owner)

{
  int iVar1;
  int iVar2;
  int iVar3;
  uint uVar4;
  
  if (owner < 3) {
    iVar3 = (uint)owner * 2;
    uVar4 = 0x8000;
    if (*(short *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe8b94u + (uint32_t)(iVar3) * 1u)))) == -0x8000) {
      if (DAT_febe8b9a < 0x8001) {
        return;
      }
      iVar3 = 0;
      do {
        if ((int)(*(ushort *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe8b94u + (uint32_t)(iVar3 * 2) * 1u)))) - uVar4) < 0) {
          uVar4 = (uint)*(ushort *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe8b94u + (uint32_t)(iVar3 * 2) * 1u))));
        }
        iVar2 = iVar3 + 1;
        iVar1 = iVar3 + -2;
        iVar3 = iVar2;
      } while (((iVar1 < 0) || (iVar2 < 0)));
      DAT_febe8b9a = (ushort)uVar4;
    }
    else {
      *(undefined2 *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe8b94u + (uint32_t)(iVar3) * 1u)))) = 0x8000;
      uVar4 = 0x8000;
      iVar3 = 0;
      do {
        if ((int)(*(ushort *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe8b94u + (uint32_t)(iVar3 * 2) * 1u)))) - uVar4) < 0) {
          uVar4 = (uint)*(ushort *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe8b94u + (uint32_t)(iVar3 * 2) * 1u))));
        }
        iVar2 = iVar3 + 1;
        iVar1 = iVar3 + -2;
        iVar3 = iVar2;
      } while (((iVar1 < 0) || (iVar2 < 0)));
      DAT_febe8b9a = (ushort)uVar4;
    }
    DAT_febe8b86 = ~(ushort)uVar4;
  }
  return;
}

void initialize_byte_pair_8ba0_to_ff_579e8(void)

{
  DAT_febe8ba0 = 0xff;
  DAT_febe8ba1 = 0xff;
  return;
}

void initialize_phase_output_slots(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  
  DAT_febe8ba7 = 0;
  iVar3 = 0;
  do {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe8ba2u + (uint32_t)(iVar3) * 1u)))) = '\0';
    iVar2 = iVar3 + 1;
    iVar1 = iVar3 + -4;
    (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe8bb2u + (uint32_t)(iVar3 * 3) * 2u)))) = 0x4000;
    (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe8bb2u + (uint32_t)(iVar3 * 3 + 1) * 2u)))) = 0x4000;
    (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe8bb2u + (uint32_t)(iVar3 * 3 + 2) * 2u)))) = 0x4000;
    iVar3 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  DAT_febe8bad = 0;
  iVar3 = 0;
  do {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe8ba8u + (uint32_t)(iVar3) * 1u)))) = '\0';
    iVar2 = iVar3 + 1;
    iVar1 = iVar3 + -4;
    (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe8bd0u + (uint32_t)(iVar3 * 3) * 2u)))) = 0x4000;
    (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe8bd0u + (uint32_t)(iVar3 * 3 + 1) * 2u)))) = 0x4000;
    (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe8bd0u + (uint32_t)(iVar3 * 3 + 2) * 2u)))) = 0x4000;
    iVar3 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  DAT_febe8baf = 0;
  DAT_febe8bae = 0;
  DAT_febe8ba1 = 0xff;
  ((volatile uint8_t *)camry_host_ptr(0xfebe8ba8u))[0] = 'Z';
  DAT_febe8ba0 = 0xff;
  ((volatile uint8_t *)camry_host_ptr(0xfebe8ba2u))[0] = 'Z';
  return;
}

void select_phase_output_slots(void)

{
  int iVar1;
  ushort uVar2;
  uint uVar3;
  ushort uVar4;
  ushort uVar5;
  ushort uVar6;
  uint uVar7;
  uint uVar8;
  uint uVar9;
  
  uVar8 = (uint)DAT_febe8bae;
  uVar5 = DAT_febe8b92;
  if (0x7fff < DAT_febe8b92) {
    uVar5 = 0x8000;
  }
  if (uVar5 < 0x4000) {
    uVar5 = 0x4000;
  }
  uVar2 = 0x8000 - uVar5;
  if ((uVar8 != (byte)~DAT_febe8ba0) || (DAT_febe8ba7 != '\0')) {
    DAT_febe8ba7 = '\0';
    uVar7 = 0;
    uVar9 = 0;
    do {
      uVar8 = uVar7;
      if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe8ba2u + (uint32_t)(uVar7) * 1u)))) != 'Z') {
        uVar8 = uVar9;
      }
      uVar3 = uVar7 + 1;
      iVar1 = uVar7 - 4;
      uVar7 = uVar3;
      uVar9 = uVar8;
    } while (iVar1 < 0 != ((int)uVar3 < 0 && -1 < iVar1));
    DAT_febe8bae = (byte)uVar8;
    DAT_febe8ba0 = ~DAT_febe8bae;
  }
  iVar1 = (int)(short)uVar8;
  DAT_febe8bee = (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe8bb2u + (uint32_t)(iVar1 * 3) * 2u))));
  DAT_febe8bf0 = (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe8bb2u + (uint32_t)(iVar1 * 3 + 1) * 2u))));
  uVar6 = (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe8bb2u + (uint32_t)(iVar1 * 3 + 2) * 2u))));
  DAT_febe8bf2 = uVar6;
  if ((*(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x30d6cu + (uint32_t)((uVar8 >> 5) * 4) * 1u)))) >> (uVar8 & 0x1f) & 1) != 0) {
    if (uVar5 < DAT_febe8bee) {
      DAT_febe8bee = uVar5;
    }
    uVar4 = uVar2;
    if (uVar2 <= DAT_febe8bee) {
      uVar4 = DAT_febe8bee;
    }
    DAT_febe8bee = uVar4;
    if (uVar5 < DAT_febe8bf0) {
      DAT_febe8bf0 = uVar5;
    }
    uVar4 = uVar2;
    if (uVar2 <= DAT_febe8bf0) {
      uVar4 = DAT_febe8bf0;
    }
    DAT_febe8bf0 = uVar4;
    if (uVar5 < uVar6) {
      uVar6 = uVar5;
    }
    DAT_febe8bf2 = uVar2;
    if (uVar2 <= uVar6) {
      DAT_febe8bf2 = uVar6;
    }
  }
  DAT_febe8bb0 = DAT_febe8b88;
  uVar8 = (uint)DAT_febe8baf;
  uVar5 = DAT_febe8b9c;
  if (0x7fff < DAT_febe8b9c) {
    uVar5 = 0x8000;
  }
  if (uVar5 < 0x4000) {
    uVar5 = 0x4000;
  }
  uVar2 = 0x8000 - uVar5;
  if ((uVar8 != (byte)~DAT_febe8ba1) || (DAT_febe8bad != '\0')) {
    DAT_febe8bad = '\0';
    uVar7 = 0;
    uVar9 = 0;
    do {
      uVar8 = uVar7;
      if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe8ba8u + (uint32_t)(uVar7) * 1u)))) != 'Z') {
        uVar8 = uVar9;
      }
      uVar3 = uVar7 + 1;
      iVar1 = uVar7 - 4;
      uVar7 = uVar3;
      uVar9 = uVar8;
    } while (iVar1 < 0 != ((int)uVar3 < 0 && -1 < iVar1));
    DAT_febe8baf = (byte)uVar8;
    DAT_febe8ba1 = ~DAT_febe8baf;
  }
  iVar1 = (int)(short)uVar8;
  DAT_febe8bf4 = (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe8bd0u + (uint32_t)(iVar1 * 3) * 2u))));
  DAT_febe8bf6 = (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe8bd0u + (uint32_t)(iVar1 * 3 + 1) * 2u))));
  uVar6 = (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe8bd0u + (uint32_t)(iVar1 * 3 + 2) * 2u))));
  DAT_febe8bf8 = uVar6;
  if ((*(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x30d6cu + (uint32_t)((uVar8 >> 5) * 4) * 1u)))) >> (uVar8 & 0x1f) & 1) != 0) {
    if (uVar5 < DAT_febe8bf4) {
      DAT_febe8bf4 = uVar5;
    }
    uVar4 = uVar2;
    if (uVar2 <= DAT_febe8bf4) {
      uVar4 = DAT_febe8bf4;
    }
    DAT_febe8bf4 = uVar4;
    if (uVar5 < DAT_febe8bf6) {
      DAT_febe8bf6 = uVar5;
    }
    uVar4 = uVar2;
    if (uVar2 <= DAT_febe8bf6) {
      uVar4 = DAT_febe8bf6;
    }
    DAT_febe8bf6 = uVar4;
    if (uVar5 < uVar6) {
      uVar6 = uVar5;
    }
    DAT_febe8bf8 = uVar2;
    if (uVar2 <= uVar6) {
      DAT_febe8bf8 = uVar6;
    }
  }
  DAT_febe8bb1 = DAT_febe8b89;
  return;
}

void write_phase_output_slot_pair(ushort context,uchar slot,ushort *first,ushort *second)

{
  int iVar1;
  uint saved_mask;
  
  if (slot < 5) {
    iVar1 = (int)(short)(ushort)slot;
    if (context < 3) {
      (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe8bb2u + (uint32_t)(iVar1 * 3) * 2u)))) = *first;
      (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe8bb2u + (uint32_t)(iVar1 * 3 + 1) * 2u)))) = first[1];
      (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe8bb2u + (uint32_t)(iVar1 * 3 + 2) * 2u)))) = first[2];
      (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe8bd0u + (uint32_t)(iVar1 * 3) * 2u)))) = *second;
      (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe8bd0u + (uint32_t)(iVar1 * 3 + 1) * 2u)))) = second[1];
      (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe8bd0u + (uint32_t)(iVar1 * 3 + 2) * 2u)))) = second[2];
    }
    else {
      saved_mask = priority_mask_enter(0xffc0);
      (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe8bb2u + (uint32_t)(iVar1 * 3) * 2u)))) = *first;
      (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe8bb2u + (uint32_t)(iVar1 * 3 + 1) * 2u)))) = first[1];
      (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe8bb2u + (uint32_t)(iVar1 * 3 + 2) * 2u)))) = first[2];
      (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe8bd0u + (uint32_t)(iVar1 * 3) * 2u)))) = *second;
      (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe8bd0u + (uint32_t)(iVar1 * 3 + 1) * 2u)))) = second[1];
      (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe8bd0u + (uint32_t)(iVar1 * 3 + 2) * 2u)))) = second[2];
      priority_mask_restore(saved_mask);
    }
  }
  return;
}

void activate_phase_output_slot_pair(uchar slot)

{
  uint uVar1;
  uchar uVar2;
  
  uVar1 = (uint)slot;
  if (uVar1 < 5) {
    uVar2 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe8ba2u + (uint32_t)(uVar1) * 1u))));
    if (uVar2 != 'Z') {
      uVar2 = 'Z';
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe8ba2u + (uint32_t)(uVar1) * 1u)))) = 'Z';
      DAT_febe8ba7 = 0x5a;
    }
    if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe8ba8u + (uint32_t)(uVar1) * 1u)))) != 'Z') {
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe8ba8u + (uint32_t)(uVar1) * 1u)))) = uVar2;
      DAT_febe8bad = uVar2;
    }
  }
  return;
}

void release_phase_output_slot_pair(uchar slot)

{
  uint uVar1;
  
  uVar1 = (uint)slot;
  if (uVar1 < 5) {
    if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe8ba2u + (uint32_t)(uVar1) * 1u)))) != '\0') {
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe8ba2u + (uint32_t)(uVar1) * 1u)))) = '\0';
      DAT_febe8ba7 = 0x5a;
    }
    if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe8ba8u + (uint32_t)(uVar1) * 1u)))) != '\0') {
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe8ba8u + (uint32_t)(uVar1) * 1u)))) = '\0';
      DAT_febe8bad = 0x5a;
    }
  }
  return;
}

void write_phase_output_slot_bank0(ushort context,uchar slot,ushort *codes)

{
  int iVar1;
  uint saved_mask;
  
  if (slot < 5) {
    iVar1 = (int)(short)(ushort)slot;
    if (context < 3) {
      (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe8bb2u + (uint32_t)(iVar1 * 3) * 2u)))) = *codes;
      (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe8bb2u + (uint32_t)(iVar1 * 3 + 1) * 2u)))) = codes[1];
      (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe8bb2u + (uint32_t)(iVar1 * 3 + 2) * 2u)))) = codes[2];
    }
    else {
      saved_mask = priority_mask_enter(0xffc0);
      (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe8bb2u + (uint32_t)(iVar1 * 3) * 2u)))) = *codes;
      (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe8bb2u + (uint32_t)(iVar1 * 3 + 1) * 2u)))) = codes[1];
      (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe8bb2u + (uint32_t)(iVar1 * 3 + 2) * 2u)))) = codes[2];
      priority_mask_restore(saved_mask);
    }
  }
  return;
}

void activate_phase_output_slot_bank0(uchar slot)

{
  if ((slot < 5) && ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe8ba2u + (uint32_t)(slot) * 1u)))) != 'Z')) {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe8ba2u + (uint32_t)(slot) * 1u)))) = 'Z';
    DAT_febe8ba7 = 0x5a;
  }
  return;
}

void release_phase_output_slot_bank0(uchar slot)

{
  if ((slot < 5) && ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe8ba2u + (uint32_t)(slot) * 1u)))) != '\0')) {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe8ba2u + (uint32_t)(slot) * 1u)))) = '\0';
    DAT_febe8ba7 = 0x5a;
  }
  return;
}

void write_phase_output_slot_bank1(ushort context,uchar slot,ushort *codes)

{
  int iVar1;
  uint saved_mask;
  
  if (slot < 5) {
    iVar1 = (int)(short)(ushort)slot;
    if (context < 3) {
      (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe8bd0u + (uint32_t)(iVar1 * 3) * 2u)))) = *codes;
      (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe8bd0u + (uint32_t)(iVar1 * 3 + 1) * 2u)))) = codes[1];
      (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe8bd0u + (uint32_t)(iVar1 * 3 + 2) * 2u)))) = codes[2];
    }
    else {
      saved_mask = priority_mask_enter(0xffc0);
      (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe8bd0u + (uint32_t)(iVar1 * 3) * 2u)))) = *codes;
      (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe8bd0u + (uint32_t)(iVar1 * 3 + 1) * 2u)))) = codes[1];
      (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe8bd0u + (uint32_t)(iVar1 * 3 + 2) * 2u)))) = codes[2];
      priority_mask_restore(saved_mask);
    }
  }
  return;
}

void activate_phase_output_slot_bank1(uchar slot)

{
  uint uVar1;
  
  uVar1 = (uint)slot;
  if ((uVar1 < 5) && ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe8ba8u + (uint32_t)(uVar1) * 1u)))) != 'Z')) {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe8ba8u + (uint32_t)(uVar1) * 1u)))) = 'Z';
    DAT_febe8bad = 0x5a;
  }
  return;
}

void release_phase_output_slot_bank1(uchar slot)

{
  uint uVar1;
  
  uVar1 = (uint)slot;
  if ((uVar1 < 5) && ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe8ba8u + (uint32_t)(uVar1) * 1u)))) != '\0')) {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe8ba8u + (uint32_t)(uVar1) * 1u)))) = '\0';
    DAT_febe8bad = 0x5a;
  }
  return;
}

void return_only_stub_57dec(void)

{
  return;
}

void return_only_stub_57dee(void)

{
  return;
}

void stage_live_phase_halfword_compares(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  stage_channel0_halfword_pwm_compares_669da(DAT_febe8bee,DAT_febe8bf0,DAT_febe8bf2);
  stage_channel1_halfword_pwm_compares_66a40((*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x2c0c)))),(*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x2c0a)))),
               (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x2c08)))));
  return;
}

void return_only_stub_57e14(void)

{
  return;
}

void initialize_mode600_latched_state_57e16(void)

{
  DAT_febe8bfa = 1;
  DAT_febe8bfb = 2;
  DAT_febe8bfc = 0;
  return;
}

void update_mode600_four_state_output_latch_57e26(void)

{
  char cVar1;
  
  cVar1 = DAT_febe8bfc;
  switch(DAT_febe8bfa) {
  case 0:
    if (DAT_febee8cc == 0x600) {
      DAT_febe8bfa = 3;
      DAT_febe8bfb = '\x02';
    }
    else {
      cVar1 = '\0';
    }
    break;
  case 1:
    if (DAT_febee8cc == 0x600) {
      DAT_febe8bfa = 2;
      DAT_febe8bfb = '\x02';
    }
    else {
      cVar1 = '\x01';
    }
    break;
  case 2:
    if (DAT_febee8cc != 0x600) {
      DAT_febe8bfa = 1;
      DAT_febe8bfc = 1;
      return;
    }
    goto LAB_00057e80;
  case 3:
    if (DAT_febee8cc != 0x600) {
      DAT_febe8bfa = 0;
      DAT_febe8bfc = 0;
      return;
    }
LAB_00057e80:
    cVar1 = DAT_febe8bfb;
    if (DAT_febe8bfb == '\x02') {
      cVar1 = DAT_febe8bfc;
    }
    break;
  default:
    DAT_febe8bfa = 1;
  }
  DAT_febe8bfc = cVar1;
  return;
}

void return_only_stub_57eb2(void)

{
  return;
}

void set_range_exclusion_flag_57eb4(void)

{
  DAT_febe5f48 = 1;
  return;
}

void update_three_input_range_exclusion_flag_57ebc(void)

{
  if (((DAT_00030d74 < DAT_febe7da6) || (DAT_febe7da6 < DAT_00030d76)) &&
     ((DAT_00030d74 < DAT_febe7da8 || (DAT_febe7da8 < DAT_00030d76)))) {
    DAT_febe5f48 = true;
    if (DAT_febe7db0 <= DAT_00030d70) {
      DAT_febe5f48 = DAT_febe7db0 < DAT_00030d72;
    }
  }
  else {
    DAT_febe5f48 = false;
  }
  return;
}

void return_only_stub_57efc(void)

{
  return;
}

void publish_application_status_snapshot_at_ee00_57f00(void)

{
  DAT_febeee1c = DAT_febe7db0;
  DAT_febeee00 = DAT_febe7bbc;
  DAT_febeee01 = DAT_febe79e5;
  DAT_febeee02 = DAT_febe686c;
  DAT_febeee1e = DAT_febe71ec;
  DAT_febeee20 = DAT_febe7db2;
  DAT_febeee03 = ((volatile uint8_t *)camry_host_ptr(0xfebe7cacu))[0];
  DAT_febeee04 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe7cacu + (uint32_t)(1) * 1u))));
  DAT_febeee05 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe7cacu + (uint32_t)(2) * 1u))));
  DAT_febeee06 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe7cacu + (uint32_t)(3) * 1u))));
  DAT_febeee07 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe7cacu + (uint32_t)(4) * 1u))));
  DAT_febeee08 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe7cacu + (uint32_t)(5) * 1u))));
  DAT_febeee09 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe7cacu + (uint32_t)(6) * 1u))));
  DAT_febeee0a = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe7cacu + (uint32_t)(7) * 1u))));
  DAT_febeee0b = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe7cacu + (uint32_t)(8) * 1u))));
  DAT_febeee0c = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe7cacu + (uint32_t)(9) * 1u))));
  DAT_febeee0d = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe7cacu + (uint32_t)(10) * 1u))));
  DAT_febeee0e = channel_request_state.channel0_state;
  DAT_febeee0f = DAT_febe8ac8;
  DAT_febeee22 = DAT_febe7da6;
  DAT_febeee10 = channel_request_state.channel1_state;
  DAT_febeee11 = DAT_febe8acb;
  DAT_febeee16 = 0;
  DAT_febeee17 = 0;
  DAT_febeee24 = DAT_febe7da8;
  DAT_febeee18 = 0;
  DAT_febeee19 = 0;
  DAT_febeee1a = 0;
  DAT_febeee28 = output_request_status;
  DAT_febeee12 = DAT_febe8a24;
  DAT_febeee26 = DAT_febe71f2;
  DAT_febeee13 = DAT_febe7569;
  DAT_febeee14 = DAT_febe7567;
  DAT_febeee15 = DAT_febe7568;
  return;
}

void return_only_stub_57fce(void)

{
  return;
}

void publish_current_control_snapshot(void)

{
  DAT_febeec24 = 0;
  DAT_febeec00 = 0;
  DAT_febeec04 = (*((volatile int16_t *)camry_host_ptr((uint32_t)(0xfebe6be8u + (uint32_t)(0) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeState) + (uint32_t)offsetof(F33RegulatorOutputEnvelopeState, second)))));
  DAT_febeec06 = (*((volatile int16_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe6be8u + (uint32_t)(1) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeState)) + (uint32_t)(0) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeState) + (uint32_t)offsetof(F33RegulatorOutputEnvelopeState, second)))));
  DAT_febeec08 = ((int)(int16_t)DAT_febe5f36);
  DAT_febeec0a = ((int)(int16_t)DAT_febe7eaa);
  DAT_febeec0c = ((int)(int16_t)DAT_febe6e00);
  DAT_febeec14 = DAT_febe7d94;
  DAT_febeec18 = DAT_febe7d74;
  DAT_febeec1c = DAT_febe5f40;
  DAT_febeec20 = DAT_febe7d68;
  DAT_febeec0e = ((int)(int16_t)DAT_febe6e0a);
  DAT_febeec01 = DAT_febe8b88;
  DAT_febeec02 = DAT_febe8b89;
  DAT_febeec10 = ((int)(int16_t)DAT_febe7d78);
  return;
}
