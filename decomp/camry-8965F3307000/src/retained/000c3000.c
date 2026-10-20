#include "common.h"

void set_bfb3_from_bf47_or_acd6_c3008(void)

{
  if ((DAT_febebf47 != '\0') || (DAT_febebfb3 = 0, DAT_febeacd6 != '\0')) {
    DAT_febebfb3 = 0x5a;
  }
  return;
}

void combine_accf_acd1_and_bf49_bf4a_into_bfb4_c3022(void)

{
  if ((DAT_febeaccf == '\0') && (DAT_febebf49 == '\0')) {
    if ((DAT_febeacd1 != '\0') || (DAT_febebf4a == '\0')) {
      DAT_febebfb4 = 0;
      return;
    }
  }
  else if ((DAT_febeacd1 == '\0') && ((DAT_febebf4a == '\0' && (DAT_febeaccf != '\0')))) {
    DAT_febebfb4 = 0;
    return;
  }
  DAT_febebfb4 = 0x5a;
  return;
}

void set_bfb5_from_bf47_or_bf48_c305c(void)

{
  if ((DAT_febebf47 != '\0') || (DAT_febebfb5 = 0, DAT_febebf48 != '\0')) {
    DAT_febebfb5 = 0x5a;
  }
  return;
}

void update_bfb3_bfb4_bfb5_boolean_combinations_c3076(void)

{
  set_bfb3_from_bf47_or_acd6_c3008();
  combine_accf_acd1_and_bf49_bf4a_into_bfb4_c3022();
  set_bfb5_from_bf47_or_bf48_c305c();
  return;
}

void classify_bf44_status_by_ad3c_and_gate_bfb6_c308a(void)

{
  byte bVar1;
  
  if ((DAT_febead3c == '\0') || (DAT_febead3c == '\x03')) {
LAB_000c30ca:
    DAT_febebf6c = '\"';
LAB_000c30ce:
    if ((1 < DAT_febeacbd) || (DAT_febebf6c != '\x11')) {
      DAT_febebfb6 = 0;
      return;
    }
  }
  else {
    if (DAT_febead3c == '\x02') {
      if ((DAT_febebf44 == 0) && (DAT_febead25 == 0)) {
LAB_000c30ba:
        DAT_febebf6c = '\x11';
        goto LAB_000c30ce;
      }
      bVar1 = DAT_febead25;
      if ((DAT_febebf44 >> 1 & 1) == 0) goto LAB_000c30c2;
    }
    else {
      bVar1 = DAT_febebf44;
      if (DAT_febebf44 == 0) goto LAB_000c30ba;
LAB_000c30c2:
      if ((bVar1 >> 1 & 1) == 0) goto LAB_000c30ca;
    }
    DAT_febebf6c = 'D';
  }
  DAT_febebfb6 = 0x5a;
  return;
}

void run_init_chain_c30ea(void)

{
  set_bfb0_when_acc0_one_and_nine_flags_clear_c2ed0();
  set_bfb1_when_acc0_one_and_eight_flags_clear_c2f26();
  set_bfae_when_status_class_and_inhibits_clear_c2f78();
  set_bfaf_when_raw_status_and_inhibits_clear_c2fac();
  set_bfb2_when_five_acc7_flags_clear_c2fd8();
  update_bfb3_bfb4_bfb5_boolean_combinations_c3076();
  classify_bf44_status_by_ad3c_and_gate_bfb6_c308a();
  return;
}

void update_six_conditionally_enabled_accumulator_filters_c310e(void)

{
  int iVar1;
  uint uVar2;
  uint uVar3;
  uint uVar4;
  uint uVar5;
  
  if (DAT_febebfb0 == 'Z') {
    DAT_febebf54 = (DAT_febeaf00 + DAT_febebf54) - DAT_febebf80;
    DAT_febebf80 = DAT_febebf54 * 0x400;
    if (DAT_000af560 != 0) {
      if (DAT_febebf80 == -0x80000000 && DAT_000af560 == -1) {
        DAT_febebf80 = -0x80000000;
      }
      else {
        DAT_febebf80 = DAT_febebf80 / DAT_000af560;
      }
    }
  }
  if (DAT_febebfb1 == 'Z') {
    DAT_febebf58 = (DAT_febebf58 + ((int)(int16_t)DAT_febeae0c)) - (int)((int)(int16_t)DAT_febebfa0);
    iVar1 = DAT_febebf58 * 0x400;
    if (DAT_000af564 != 0) {
      if (iVar1 == -0x80000000 && DAT_000af564 == -1) {
        iVar1 = 0;
      }
      else {
        iVar1 = iVar1 / DAT_000af564;
      }
    }
    DAT_febebfa0 = (short)iVar1;
  }
  if (DAT_febebfb2 == 'Z') {
    uVar5 = 0;
    if (-1 < (int)DAT_febeaef0) {
      uVar5 = DAT_febeaef0 & 0xffff;
    }
    uVar4 = 0;
    if (-1 < (int)DAT_febeaef4) {
      uVar4 = DAT_febeaef4 & 0xffff;
    }
    uVar3 = 0;
    if (-1 < (int)DAT_febeaef8) {
      uVar3 = DAT_febeaef8 & 0xffff;
    }
    uVar2 = 0;
    if (-1 < (int)DAT_febeaefc) {
      uVar2 = DAT_febeaefc & 0xffff;
    }
    DAT_febebf5c = (DAT_febebf5c + uVar5) - (uint)DAT_febebfa2;
    uVar5 = DAT_febebf5c * 0x400;
    if (DAT_000af568 != 0) {
      uVar5 = uVar5 / DAT_000af568;
    }
    DAT_febebfa2 = (ushort)uVar5;
    DAT_febebf60 = (DAT_febebf60 + uVar4) - (uint)DAT_febebfa4;
    uVar5 = DAT_febebf60 * 0x400;
    if (DAT_000af568 != 0) {
      uVar5 = uVar5 / DAT_000af568;
    }
    DAT_febebfa4 = (ushort)uVar5;
    DAT_febebf64 = (DAT_febebf64 + uVar3) - (uint)DAT_febebfa6;
    uVar5 = DAT_febebf64 * 0x400;
    if (DAT_000af568 != 0) {
      uVar5 = uVar5 / DAT_000af568;
    }
    DAT_febebfa6 = (ushort)uVar5;
    DAT_febebf68 = (DAT_febebf68 + uVar2) - (uint)DAT_febebfa8;
    uVar5 = DAT_febebf68 * 0x400;
    if (DAT_000af568 != 0) {
      uVar5 = uVar5 / DAT_000af568;
    }
    DAT_febebfa8 = (ushort)uVar5;
  }
  return;
}

void select_bf84_scaled_product_and_mode_flags_c3228(void)

{
  if ((DAT_febead3c == '\0') || (DAT_febead3c == '\x03')) {
    DAT_febebfb7 = 0;
    DAT_febebfb8 = 0;
    DAT_febebf84 = 0;
  }
  else if (DAT_febead3c == '\x02') {
    if (DAT_febead3e == '\x02') {
      DAT_febebf84 = (int)(((((int)(int16_t)DAT_febebf9e) * 0xeaaf) / 0x10000) * (uint)DAT_febeae38) / 0x400;
      DAT_febebfb7 = 0x5a;
    }
    else {
      DAT_febebfb7 = 0;
    }
    DAT_febebfb8 = 1;
  }
  else {
    DAT_febebf84 = 0;
    DAT_febebfb7 = 0x5a;
    DAT_febebfb8 = 0;
  }
  return;
}

void run_init_chain_c3292(void)

{
  compute_bf70_scaled_input_terms_c2e2a();
  run_init_chain_c30ea();
  update_six_conditionally_enabled_accumulator_filters_c310e();
  select_bf84_scaled_product_and_mode_flags_c3228();
  return;
}

void refresh_observer_source_term(void)

{
  DAT_febeaba4 = -DAT_febeac18;
  DAT_febebfc4 = DAT_febeac02;
  return;
}

void debounce_ac01_into_bfc5_with_two_counters_c32be(void)

{
  if (DAT_febeac01 == '\0') {
    if ((DAT_febebf6e < 10) && (DAT_febebf6e = DAT_febebf6e + 1, 9 < DAT_febebf6e)) {
      DAT_febebfc5 = 0;
    }
    DAT_febebf6d = 0;
  }
  else {
    if ((DAT_febebf6d < DAT_000af56c) &&
       (DAT_febebf6d = DAT_febebf6d + 1, DAT_000af56c <= DAT_febebf6d)) {
      DAT_febebfc5 = 0x5a;
    }
    DAT_febebf6e = 0;
  }
  return;
}

void refresh_observer_source_and_debounce_ac01_c330c(void)

{
  refresh_observer_source_term();
  debounce_ac01_into_bfc5_with_two_counters_c32be();
  return;
}

undefined4 publish_raw_estimator_state(void)

{
  undefined1 uVar1;
  undefined1 uVar2;
  undefined1 uVar3;
  undefined1 uVar4;
  undefined1 uVar5;
  undefined4 uVar6;
  undefined1 uVar7;
  undefined1 uVar8;
  undefined4 uVar9;
  undefined4 uVar10;
  undefined2 uVar11;
  undefined2 uVar12;
  undefined1 uVar13;
  undefined1 uVar14;
  undefined4 uVar15;
  undefined4 uVar16;
  undefined1 uVar17;
  undefined1 uVar18;
  uint32_t puVar19;
  undefined4 uVar20;
  
  uVar18 = DAT_febec08b;
  uVar17 = DAT_febec08a;
  uVar16 = DAT_febec080;
  uVar15 = DAT_febec074;
  uVar14 = DAT_febebff1;
  uVar13 = DAT_febebff0;
  uVar12 = DAT_febebfee;
  uVar11 = DAT_febebfec;
  uVar10 = DAT_febebfd8;
  uVar9 = DAT_febebfd4;
  uVar8 = DAT_febebfb6;
  uVar7 = DAT_febebfae;
  uVar6 = DAT_febebf50;
  uVar5 = DAT_febead5c;
  uVar4 = DAT_febead3f;
  uVar3 = DAT_febead3c;
  uVar2 = DAT_febead1a;
  uVar1 = DAT_febeacbd;
  puVar19 = 0xfebeb800u;
  uVar20 = raise_priority_mask_and_return_previous_d1da0(0xffc0);
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar19 + (uint32_t)(0x7bf))))) = uVar4;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar19 + (uint32_t)(0x7c0))))) = uVar5;
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar19 + 0x7aa)))) = uVar11;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar19 + (uint32_t)(0x7c1))))) = uVar8;
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar19 + 0x7ac)))) = uVar12;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar19 + (uint32_t)(0x7c2))))) = uVar1;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar19 + (uint32_t)(0x7b9))))) = uVar13;
  (*((undefined4 *)camry_host_ptr((uint32_t)(puVar19 + -0xc60)))) = uVar9;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar19 + (uint32_t)(0x7ba))))) = uVar7;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar19 + (uint32_t)(0x7bb))))) = uVar14;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar19 + (uint32_t)(0x7bc))))) = uVar3;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar19 + (uint32_t)(0x7bd))))) = uVar18;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar19 + (uint32_t)(0x7be))))) = uVar17;
  (*((undefined4 *)camry_host_ptr((uint32_t)(puVar19 + 0x788)))) = uVar10;
  (*((undefined4 *)camry_host_ptr((uint32_t)(puVar19 + 0x78c)))) = uVar15;
  (*((undefined4 *)camry_host_ptr((uint32_t)(puVar19 + 0x790)))) = uVar16;
  (*((undefined4 *)camry_host_ptr((uint32_t)(puVar19 + 0x794)))) = uVar6;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar19 + (uint32_t)(0x7c3))))) = uVar2;
  restore_priority_mask_preserving_interrupt_enable_d1dc6(uVar20);
  return uVar20;
}

undefined4 clear_published_estimator_state(void)

{
  uint32_t puVar1;
  undefined4 uVar2;
  
  puVar1 = 0xfebeb800u;
  uVar2 = raise_priority_mask_and_return_previous_d1da0(0xffc0);
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x7b9))))) = 0;
  (*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + -0xc60)))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x7ba))))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x7bb))))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x7bc))))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x7bd))))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x7be))))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x7bf))))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x7c0))))) = 0;
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + 0x7aa)))) = 0;
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + 0x7ac)))) = 0;
  (*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + 0x788)))) = 0;
  (*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + 0x78c)))) = 0;
  (*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + 0x790)))) = 0;
  (*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + 0x794)))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x7c1))))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x7c2))))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x7c3))))) = 0;
  restore_priority_mask_preserving_interrupt_enable_d1dc6(uVar2);
  return uVar2;
}

undefined4 reset_bfc8_state_and_protected_bfd4_outputs_c3444(void)

{
  uint32_t puVar1;
  undefined4 uVar2;
  
  puVar1 = 0xfebeb800u;
  DAT_febebfd8 = 0;
  DAT_febebff1 = 0;
  DAT_febebfe8 = 0;
  DAT_febebfc8 = 0;
  DAT_febebfcc = 0;
  DAT_febebfd0 = 0;
  uVar2 = raise_priority_mask_and_return_previous_d1da0(0xffc0);
  (*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + 0x7d4)))) = 0;
  (*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + 0x7e4)))) = 0xffffffff;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x7f0))))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x7f2))))) = 0xff;
  restore_priority_mask_preserving_interrupt_enable_d1dc6(uVar2);
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + 0x7ea)))) = 0;
  (*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + 0x7dc)))) = 0;
  (*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + 0x7e0)))) = 0;
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + 0x7ec)))) = 0;
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + 0x7ee)))) = 0;
  return uVar2;
}

int estimator_reference_correction(void)

{
  int value;
  uint32_t puVar1;
  ushort input;
  uint uVar2;
  int iVar3;
  uint uVar4;
  
  puVar1 = 0xfebeb800u;
  uVar4 = (uint)DAT_febeae38;
  value = DAT_febebf7c - DAT_febebf70;
  DAT_febebfc8 = value;
  iVar3 = abs_s32_wrapping(value);
  if (uVar4 == 0) {
    uVar2 = 0;
  }
  else {
    uVar2 = iVar3 << 10;
    if (uVar4 != 0) {
      uVar2 = uVar2 / uVar4;
    }
    if (0xffff < uVar2) {
      input = 0xffff;
      goto LAB_000c34d0;
    }
  }
  input = (ushort)uVar2;
LAB_000c34d0:
  iVar3 = interpolate_unsigned_axis_sentinel_curve((ushort *)((undefined *)camry_host_ptr(0xaf5ceu)),input);
  iVar3 = (int)(iVar3 * uVar4) / 0x400;
  (*((int *)camry_host_ptr((uint32_t)(puVar1 + 0x7cc)))) = iVar3;
  if (-1 < value) {
    iVar3 = -iVar3;
  }
  (*((int *)camry_host_ptr((uint32_t)(puVar1 + 2000)))) = iVar3;
  return iVar3;
}

void acquire_external_estimator_reference(void)

{
  int iVar1;
  uint uVar2;
  ushort uVar3;
  char cVar4;
  char cVar5;
  char cVar6;
  char cVar7;
  uint32_t puVar8;
  short sVar9;
  short sVar10;
  undefined4 uVar11;
  int iVar12;
  int iVar13;
  ushort uVar14;
  
  cVar7 = DAT_febebff1;
  cVar6 = DAT_febebfc5;
  cVar5 = DAT_febebfc4;
  cVar4 = DAT_febebfb7;
  sVar10 = ((int)(int16_t)DAT_febebf98);
  puVar8 = 0xfebeb800u;
  iVar13 = (int)DAT_000af578;
  iVar12 = (int)DAT_000af57a;
  sVar9 = abs_s16_wrapping(((int)(int16_t)DAT_febebf9c));
  sVar10 = abs_s16_wrapping(sVar10);
  uVar3 = DAT_000af57c;
  if (((((cVar7 == 'Z') && (cVar6 == '\0')) && (cVar5 == '\0')) &&
      ((iVar1 = sVar9 - iVar13, iVar1 < 0 != (sVar9 < 0 != iVar13 < 0 && iVar13 < 0 == iVar1 < 0) &&
       (iVar13 = sVar10 - iVar12,
       iVar13 < 0 != (sVar10 < 0 != iVar12 < 0 && iVar12 < 0 == iVar13 < 0))))) && (cVar4 == 'Z')) {
    uVar14 = (*((short *)camry_host_ptr((uint32_t)(puVar8 + 0x7e8)))) + 1U;
    if ((DAT_000af57c < (ushort)((*((short *)camry_host_ptr((uint32_t)(puVar8 + 0x7e8)))) + 1U)) &&
       (uVar14 = uVar3, (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar8 + (uint32_t)(0x8de))))) == 'Z')) {
      iVar12 = estimator_reference_correction();
      uVar2 = iVar12 + ((*((int *)camry_host_ptr((uint32_t)(puVar8 + 0x778)))) -
                       ((((*((int *)camry_host_ptr((uint32_t)(puVar8 + 0x784)))) + (*((int *)camry_host_ptr((uint32_t)(puVar8 + 0x77c))))) -
                        (*((int *)camry_host_ptr((uint32_t)(puVar8 + 0x7d8))))) - (*((int *)camry_host_ptr((uint32_t)(puVar8 + 0x770))))));
      uVar11 = raise_priority_mask_and_return_previous_d1da0(0xffc0);
      (*((uint *)camry_host_ptr((uint32_t)(puVar8 + 0x7d4)))) = uVar2;
      (*((uint *)camry_host_ptr((uint32_t)(puVar8 + 0x7e4)))) = ~uVar2;
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar8 + (uint32_t)(0x7f0))))) = 0x5a;
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar8 + (uint32_t)(0x7f2))))) = 0xa5;
      restore_priority_mask_preserving_interrupt_enable_d1dc6(uVar11);
    }
  }
  else {
    uVar14 = 0;
  }
  (*((ushort *)camry_host_ptr((uint32_t)(puVar8 + 0x7e8)))) = uVar14;
  return;
}

void select_external_reference_acquisition(void)

{
  DAT_febebfea = 0;
  DAT_febebfdc = 0;
  DAT_febebfe0 = 0;
  acquire_external_estimator_reference();
  return;
}

void accumulate_model_estimator_reference(void)

{
  uint32_t puVar1;
  ushort uVar2;
  uint32_t puVar3;
  uint32_t puVar4;
  undefined4 uVar5;
  int iVar6;
  uint uVar7;
  int iVar8;
  
  puVar4 = 0xfebeb800u;
  puVar3 = (0xfebeb800u);
  puVar1 = (0xfebeb800u);
  if (DAT_febebfc5 == '\0') {
    iVar8 = DAT_febebfdc;
    iVar6 = DAT_febebfe0;
    uVar2 = DAT_febebfea;
    if ((((DAT_febec045 != 'Z') || (DAT_febec044 != 'Z')) || (DAT_febec042 != 'Z')) ||
       ((DAT_febead18 != '\x11' || (DAT_febeadf4 < DAT_000af57e)))) goto LAB_000c367c;
    uVar7 = (uint)estimator_reference_window;
    uVar2 = (ushort)(DAT_febebfea + 1);
    if (uVar7 == 0) {
      iVar6 = 0x11;
      iVar8 = DAT_febebf78;
    }
    else if (DAT_febebf78 == -0x80000000 && uVar7 == 0xffffffff) {
      iVar6 = 0;
      iVar8 = -0x80000000;
    }
    else {
      iVar6 = DAT_febebf78 % (int)uVar7;
      iVar8 = DAT_febebf78 / (int)uVar7;
    }
    iVar8 = DAT_febebfdc + iVar8;
    iVar6 = DAT_febebfe0 + iVar6;
    if ((DAT_febebfea + 1 & 0xffff) < uVar7) goto LAB_000c367c;
    if (uVar7 != 0) {
      if (iVar6 == -0x80000000 && uVar7 == 0xffffffff) {
        iVar6 = -0x80000000;
      }
      else {
        iVar6 = iVar6 / (int)uVar7;
      }
    }
    uVar5 = raise_priority_mask_and_return_previous_d1da0(0xffc0);
    (*((int *)camry_host_ptr((uint32_t)(puVar4 + 0x7d4)))) = iVar6 + iVar8;
    (*((int *)camry_host_ptr((uint32_t)(puVar4 + 0x7e4)))) = ~(iVar6 + iVar8);
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(0x7f0))))) = 0x5a;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(0x7f2))))) = 0xa5;
    restore_priority_mask_preserving_interrupt_enable_d1dc6(uVar5);
    puVar1 = ((uint32_t)(puVar4));
  }
  puVar3 = puVar1;
  iVar8 = 0;
  iVar6 = 0;
  uVar2 = 0;
LAB_000c367c:
  (*((volatile int32_t *)camry_host_ptr((uint32_t)(puVar3 + 0x7dc)))) = iVar8;
  (*((volatile int32_t *)camry_host_ptr((uint32_t)(puVar3 + 0x7e0)))) = iVar6;
  (*((volatile uint16_t *)camry_host_ptr((uint32_t)(puVar3 + 0x7ea)))) = uVar2;
  return;
}

void select_model_reference_acquisition(void)

{
  DAT_febebff1 = 0;
  DAT_febebfe8 = 0;
  DAT_febebffa = 0;
  DAT_febebff8 = 0;
  accumulate_model_estimator_reference();
  return;
}

void latch_estimator_external_sample(void)

{
  DAT_febebfd8 = DAT_febebff4;
  DAT_febebff1 = 0x5a;
  if ((DAT_febead3c == '\x01') || (DAT_febead3e == '\x02')) {
    select_external_reference_acquisition();
  }
  else if (DAT_febead3e == '\x01') {
    select_model_reference_acquisition();
  }
  return;
}

void update_estimator_source_limits(void)

{
  uint32_t puVar1;
  uint32_t puVar2;
  ushort uVar3;
  ushort uVar4;
  
  puVar1 = 0xfebeb800u;
  puVar2 = (0xfebeb800u);
  uVar3 = DAT_febebfec;
  uVar4 = DAT_febebfee;
  if (DAT_febebff0 == 'Z') {
    if (DAT_febebffa == 'Z') {
      uVar3 = interpolate_unsigned16_axis_and_values_d0896(((ushort *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xaf570u + (uint32_t)(DAT_febebfb8) * 4u))))))), DAT_febebff8);
      puVar2 = ((uint32_t)(puVar1));
      uVar4 = uVar3;
    }
    else {
      puVar2 = (0xfebeb800u);
      uVar3 = estimator_source_limit_default;
      uVar4 = estimator_source_limit_default;
      if (DAT_febead3c == '\x02') {
        uVar3 = estimator_source_limit_mode2;
        uVar4 = estimator_source_limit_mode2;
      }
    }
  }
  (*((volatile uint16_t *)camry_host_ptr((uint32_t)(puVar2 + 0x7ec)))) = uVar3;
  (*((volatile uint16_t *)camry_host_ptr((uint32_t)(puVar2 + 0x7ee)))) = uVar4;
  return;
}

void select_estimator_acquisition_source(void)

{
  if (DAT_febebfb6 == 'Z') {
    if ((DAT_febead3c != '\0') && (DAT_febead3c != '\x03')) {
      DAT_febec088 = estimator_lower_band_default;
      if (DAT_febead3c == '\x02') {
        DAT_febec088 = estimator_lower_band_mode2;
      }
      if (((DAT_febebffa == 'Z') && (DAT_febebfaf == 'Z')) && (DAT_febec088 <= DAT_febebff8)) {
        latch_estimator_external_sample();
      }
      else {
        select_model_reference_acquisition();
      }
      update_estimator_source_limits();
    }
  }
  else {
    DAT_febebff1 = 0;
    DAT_febebfe8 = 0;
    DAT_febebfea = 0;
    DAT_febebfdc = 0;
    DAT_febebfe0 = 0;
  }
  return;
}

void return_only_stub_c37b8(void)

{
  return;
}

void snapshot_retained_estimator_projection(void)

{
  DAT_febebff4 = DAT_febeaf04;
  DAT_febebff8 = DAT_febeae0e;
  DAT_febebffa = DAT_febeacec;
  return;
}

undefined4 publish_retained_estimator_projection(void)

{
  char cVar1;
  ushort uVar2;
  undefined1 uVar3;
  uint32_t puVar4;
  undefined4 uVar5;
  
  puVar4 = 0xfebeb800u;
  uVar5 = raise_priority_mask_and_return_previous_d1da0(0xffc0);
  uVar2 = (*((ushort *)camry_host_ptr((uint32_t)(puVar4 + 0x8b4))));
  cVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(0x890)))));
  restore_priority_mask_preserving_interrupt_enable_d1dc6(uVar5);
  if (cVar1 == 'Z') {
    (*((undefined4 *)camry_host_ptr((uint32_t)(puVar4 + 0x87c)))) = 0;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(0x7fa))))) = 0;
  }
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(0x7fa))))) == 'Z') {
    cVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(0x88e)))));
    if ((((cVar1 == '\x11') || (cVar1 == '\"')) && ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(0x7f1))))) == 'Z')) &&
       ((*((ushort *)camry_host_ptr((uint32_t)(puVar4 + 0x7f8)))) <= uVar2)) goto LAB_000c385e;
    if (((cVar1 == '\0') && ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(0x7f1))))) == 'Z')) && ((*((ushort *)camry_host_ptr((uint32_t)(puVar4 + 0x7f8)))) <= uVar2))
    goto LAB_000c3870;
  }
  else {
    if (((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(0x7fa))))) != '\0') ||
       ((((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(0x88e))))) != '\x11' && ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(0x88e))))) != '\"')) || ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(0x7f1))))) != 'Z')))) {
LAB_000c3870:
      uVar3 = 0;
      goto LAB_000c3872;
    }
LAB_000c385e:
    (*((ushort *)camry_host_ptr((uint32_t)(puVar4 + -0x9f2)))) = uVar2;
    (*((undefined4 *)camry_host_ptr((uint32_t)(puVar4 + -0x8fc)))) = (*((undefined4 *)camry_host_ptr((uint32_t)(puVar4 + 0x87c))));
  }
  uVar3 = 0x5a;
LAB_000c3872:
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0xb14))))) = uVar3;
  return uVar5;
}

void fill_constant_block_c387a(void)

{
  DAT_febec00c = 0;
  DAT_febec00e = 0;
  DAT_febec010 = 0;
  DAT_febec012 = 0;
  DAT_febec014 = 0;
  DAT_febec016 = 0;
  DAT_febec018 = 0;
  DAT_febec01a = 0;
  DAT_febec01c = 0;
  DAT_febec01e = 0;
  DAT_febec020 = 0;
  DAT_febec022 = 0;
  DAT_febec024 = 0;
  DAT_febec026 = 0;
  DAT_febec028 = 0;
  DAT_febec02e = 0;
  DAT_febebffc = 0;
  DAT_febec034 = 0;
  DAT_febec038 = 0;
  DAT_febec03c = 0;
  DAT_febec000 = 0;
  DAT_febec004 = 0;
  DAT_febec008 = 0;
  DAT_febec03e = 0;
  DAT_febec042 = 0;
  DAT_febec02f = 0;
  DAT_febec02a = 0;
  DAT_febec02c = 0;
  DAT_febec043 = 0;
  DAT_febec040 = 0;
  DAT_febec044 = 0;
  DAT_febec045 = 0;
  DAT_febec030 = 0;
  DAT_febec031 = 0;
  DAT_febec032 = 0;
  return;
}

void refresh_estimator_qualifier_thresholds(void)

{
  bool bVar1;
  char cVar2;
  char cVar3;
  ushort input;
  undefined2 uVar4;
  uint32_t puVar5;
  ushort uVar6;
  int iVar7;
  int iVar8;
  int iVar9;
  int iVar10;
  int iVar11;
  int iVar12;
  int iVar13;
  int iVar14;
  int iVar15;
  
  uVar4 = DAT_febec0b4;
  input = DAT_febeadf6;
  cVar3 = DAT_febead3f;
  cVar2 = DAT_febead18;
  puVar5 = 0xfebeb800u;
  iVar7 = interpolate_unsigned16_axis_and_values_d0896(((undefined *)camry_host_ptr(0xaf634u)),DAT_febec0b4);
  iVar8 = interpolate_unsigned16_axis_and_values_d0896(((undefined *)camry_host_ptr(0xaf648u)),uVar4);
  iVar9 = interpolate_unsigned16_axis_and_values_d0896(((undefined *)camry_host_ptr(0xaf65cu)),uVar4);
  iVar10 = interpolate_unsigned16_axis_and_values_d0896(((undefined *)camry_host_ptr(0xaf670u)),uVar4);
  uVar6 = interpolate_unsigned16_axis_and_values_d0896(((undefined *)camry_host_ptr(0xaf684u)),uVar4);
  if (cVar2 == '\x11') {
    bVar1 = cVar3 == '\x02';
    iVar11 = interpolate_unsigned16_axis_and_values_d0896(((ushort *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd2f10u + (uint32_t)(bVar1) * 4u))))))), input);
    iVar12 = interpolate_unsigned_axis_sentinel_curve
                       (((ushort *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd2f18u + (uint32_t)(bVar1) * 4u)))))),input);
    iVar13 = interpolate_unsigned16_axis_and_values_d0896(((ushort *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd2f20u + (uint32_t)(bVar1) * 4u))))))), input);
    iVar14 = interpolate_unsigned_axis_sentinel_curve
                       (((ushort *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd2f28u + (uint32_t)(bVar1) * 4u)))))),input);
    iVar15 = interpolate_unsigned16_axis_and_values_d0896(((ushort *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd2f30u + (uint32_t)(bVar1) * 4u))))))), input);
    (*((short *)camry_host_ptr((uint32_t)(puVar5 + 0x81e)))) = (short)iVar15;
    (*((short *)camry_host_ptr((uint32_t)(puVar5 + 0x820)))) = (short)((uint)(iVar11 * iVar7) >> 10);
    (*((short *)camry_host_ptr((uint32_t)(puVar5 + 0x816)))) = (short)iVar11;
    (*((short *)camry_host_ptr((uint32_t)(puVar5 + 0x822)))) = (short)((iVar12 * iVar8) / 0x400);
    (*((short *)camry_host_ptr((uint32_t)(puVar5 + 0x824)))) = (short)((uint)(iVar13 * iVar9) >> 10);
    (*((short *)camry_host_ptr((uint32_t)(puVar5 + 0x818)))) = (short)iVar12;
    (*((short *)camry_host_ptr((uint32_t)(puVar5 + 0x826)))) = (short)((iVar14 * iVar10) / 0x400);
    (*((short *)camry_host_ptr((uint32_t)(puVar5 + 0x828)))) = (short)(iVar15 * (uint)uVar6 >> 10);
    (*((short *)camry_host_ptr((uint32_t)(puVar5 + 0x81a)))) = (short)iVar13;
    (*((short *)camry_host_ptr((uint32_t)(puVar5 + 0x81c)))) = (short)iVar14;
  }
  (*((short *)camry_host_ptr((uint32_t)(puVar5 + 0x80c)))) = (short)iVar7;
  (*((short *)camry_host_ptr((uint32_t)(puVar5 + 0x80e)))) = (short)iVar8;
  (*((short *)camry_host_ptr((uint32_t)(puVar5 + 0x810)))) = (short)iVar9;
  (*((short *)camry_host_ptr((uint32_t)(puVar5 + 0x812)))) = (short)iVar10;
  (*((ushort *)camry_host_ptr((uint32_t)(puVar5 + 0x814)))) = uVar6;
  return;
}

void update_estimator_source_mode_gate(void)

{
  undefined1 uVar1;
  uint32_t puVar2;
  int iVar3;
  
  puVar2 = (0xfebeb800u);
  if ((DAT_febead3f == '\x02') &&
     ((DAT_febead5c != '\x02' ||
      (puVar2 = (0xfebeb800u), iVar3 = abs_s32_wrapping((int)((int)(int16_t)DAT_febeae40)),
      (int)(iVar3 - (uint)*(ushort *)(((undefined *)camry_host_ptr((uint32_t)(0xfebeb800u + (uint32_t)(0x828) * 1u))))) < 0 ==
      (iVar3 < 0 && -1 < (int)(iVar3 - (uint)*(ushort *)(((undefined *)camry_host_ptr((uint32_t)(0xfebeb800u + (uint32_t)(0x828) * 1u)))))))))) {
    uVar1 = 0;
  }
  else {
    uVar1 = 0x5a;
  }
  (*((volatile undefined *)camry_host_ptr((uint32_t)(0xfebeb800u + (uint32_t)(0x82e) * 1u)))) = uVar1;
  return;
}

void advance_estimator_stability_window(ushort *count,uchar *qualified)

{
  int sample;
  int high;
  int low;
  int spread;
  int threshold;
  ushort next;
  uchar flag;
  
  sample = (int)DAT_febebf78;
  high = (int)DAT_febec000;
  low = (int)DAT_febec004;
  if (*count == 0) {
    high = sample;
    low = sample;
  }
  else if (sample > high) {
    high = sample;
  }
  else if (sample < low) {
    low = sample;
  }
  spread = high - low;
  DAT_febec008 = (uint)spread;
  threshold = (int)((long long)estimator_stability_spread_scale * (int)DAT_febeae38) / 0x400;
  if (spread >= threshold) {
    next = 0;
    flag = 0;
  }
  else {
    next = (ushort)(*count + 1);
    flag = DAT_febec042;
    if (next > estimator_stability_window) {
      flag = 'Z';
      next = estimator_stability_window;
    }
  }
  DAT_febec000 = (uint)high;
  DAT_febec004 = (uint)low;
  *count = next;
  *qualified = flag;
  return;
}

void qualify_estimator_source_stability(void)

{
  uint8_t stack_record_17[23];
  char cVar1;
  char cVar2;
  char cVar3;
  uint32_t puVar4;
  short sVar5;
  short sVar6;
  int iVar7;
  int iVar8;
  int iVar9;
  
  cVar3 = DAT_febebfc5;
  cVar2 = DAT_febead3f;
  cVar1 = DAT_febeac02;
  puVar4 = 0xfebeb800u;
  update_estimator_source_mode_gate();
  if ((((cVar2 != '\0') && (cVar2 != '\x03')) && (cVar3 == '\0')) && (cVar1 == '\0')) {
    iVar8 = (*((int *)camry_host_ptr((uint32_t)(puVar4 + 0x774)))) + (int)(*((short *)camry_host_ptr((uint32_t)(puVar4 + 0x798))));
    if (iVar8 + -0x7fff < 0 == (iVar8 < 0 && -1 < iVar8 + -0x7fff) && iVar8 != 0x7fff) {
      iVar7 = 0x7fff;
    }
    else {
      iVar7 = (int)(short)iVar8;
      if (iVar8 + 0x7fff < 0 != (-1 < iVar8 && iVar8 + 0x7fff < 0)) {
        iVar7 = -0x7fff;
      }
    }
    (*((int *)camry_host_ptr((uint32_t)(puVar4 + 0x7fc)))) = iVar8;
    iVar9 = estimator_stability_filter_divisor;
    cVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(0x82e)))));
    iVar8 = ((*((int *)camry_host_ptr((uint32_t)(puVar4 + 0x834)))) + iVar7) - (int)(*((short *)camry_host_ptr((uint32_t)(puVar4 + 0x83c))));
    (*((int *)camry_host_ptr((uint32_t)(puVar4 + 0x834)))) = iVar8;
    (*((uint16_t *)(stack_record_17 + 1))) = (*((ushort *)camry_host_ptr((uint32_t)(puVar4 + 0x83e))));
    iVar8 = iVar8 * 0x400;
    if (iVar9 != 0) {
      if (iVar8 == -0x80000000 && iVar9 == -1) {
        iVar8 = -0x80000000;
      }
      else {
        iVar8 = (int)iVar8 / (int)iVar9;
      }
    }
    sVar6 = (*((short *)camry_host_ptr((uint32_t)(puVar4 + 0x79c))));
    iVar9 = (int)estimator_stability_amplitude_limit;
    (*((int *)camry_host_ptr((uint32_t)(puVar4 + 0x838)))) = iVar8;
    (*((short *)camry_host_ptr((uint32_t)(puVar4 + 0x83c)))) = (short)iVar8;
    sVar5 = abs_s16_wrapping((short)iVar8);
    sVar6 = abs_s16_wrapping(sVar6);
    iVar7 = (int)(*((short *)camry_host_ptr((uint32_t)(puVar4 + 0x826))));
    iVar8 = sVar5 - iVar7;
    if (((iVar8 < 0 != (sVar5 < 0 != iVar7 < 0 && iVar7 < 0 == iVar8 < 0)) &&
        (iVar8 = sVar6 - iVar9, iVar8 < 0 != (sVar6 < 0 != iVar9 < 0 && iVar9 < 0 == iVar8 < 0))) &&
       (cVar1 == 'Z')) {
      advance_estimator_stability_window(((uint16_t *)((stack_record_17 + 1))),((uint8_t *)(stack_record_17)));
      goto LAB_000c3bc2;
    }
  }
  (*((uint16_t *)(stack_record_17 + 1))) = 0;
  stack_record_17[0] = '\0';
LAB_000c3bc2:
  (*((ushort *)camry_host_ptr((uint32_t)(puVar4 + 0x83e)))) = (*((uint16_t *)(stack_record_17 + 1)));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(0x842))))) = stack_record_17[0];
  return;
}

void update_estimator_group_release(void)

{
  ushort uVar1;
  uint32_t puVar2;
  uchar uVar3;
  undefined1 uVar4;
  
  puVar2 = 0xfebeb800u;
  uVar3 = get_application_grouped_status(0x12);
  uVar4 = 0x5a;
  if (uVar3 == '\0') {
    uVar1 = (*((short *)camry_host_ptr((uint32_t)(puVar2 + 0x82a)))) + 1;
    if (estimator_group_release_window <= uVar1) {
      uVar4 = 0;
      uVar1 = estimator_group_release_window;
    }
  }
  else {
    uVar1 = 0;
    uVar4 = 0x5a;
  }
  (*((ushort *)camry_host_ptr((uint32_t)(puVar2 + 0x82a)))) = uVar1;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(0x82f))))) = uVar4;
  return;
}

void advance_estimator_pair_window(ushort *count,uchar *qualified)

{
  short sVar1;
  char cVar2;
  char cVar3;
  uchar uVar4;
  uint32_t puVar5;
  int iVar6;
  int iVar7;
  int iVar8;
  uint uVar9;
  uint uVar10;
  uint uVar11;
  char cVar12;
  uint uVar13;
  uint uVar14;
  ushort uVar15;
  
  puVar5 = 0xfebeb800u;
  uVar10 = (uint)DAT_febebfa4;
  uVar11 = (uint)DAT_febebfa2;
  uVar9 = (uint)DAT_febebfa8;
  uVar15 = *count;
  uVar13 = uVar9 + (uint)DAT_febebfa6 + uVar10 + uVar11 >> 2;
  uVar14 = uVar13 & 0xffff;
  DAT_febec02c = (ushort)uVar13;
  if (uVar14 == 0) {
    uVar4 = '\0';
    cVar12 = '\0';
    uVar15 = DAT_febec02c;
  }
  else {
    puVar5 = 0xfebeb800u;
    iVar6 = abs_s32_wrapping(uVar11 - DAT_febebfa6);
    iVar7 = abs_s32_wrapping(uVar10 - uVar9);
    iVar6 = iVar6 * 100;
    iVar7 = iVar7 * 100;
    if (uVar14 != 0) {
      if (iVar6 == -0x80000000 && uVar14 == 0xffffffff) {
        iVar6 = -0x80000000;
      }
      else {
        iVar6 = iVar6 / (int)uVar14;
      }
    }
    if (uVar14 != 0) {
      if (iVar7 == -0x80000000 && uVar14 == 0xffffffff) {
        iVar7 = -0x80000000;
      }
      else {
        iVar7 = iVar7 / (int)uVar14;
      }
    }
    iVar8 = iVar6 - (uint)estimator_pair_percent_limit;
    if ((iVar8 < 0 == (iVar6 < 0 && -1 < iVar8)) ||
       (iVar6 = iVar7 - (uint)estimator_pair_percent_limit,
       iVar6 < 0 == (iVar7 < 0 && -1 < iVar6))) {
      cVar12 = 'Z';
    }
    else {
      cVar12 = '\0';
    }
    cVar2 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(0x7b0)))));
    cVar3 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(0x7b1)))));
    sVar1 = (*((short *)camry_host_ptr((uint32_t)(puVar5 + 0x7a0))));
    iVar6 = abs_s32_wrapping((*((int *)camry_host_ptr((uint32_t)(puVar5 + 0x780)))));
    iVar7 = abs_s32_wrapping((int)sVar1);
    iVar8 = abs_s32_wrapping(uVar11 - uVar10);
    if (((((int)(iVar8 - (uint)(*((ushort *)camry_host_ptr((uint32_t)(puVar5 + 0x824))))) < 0 ==
           (iVar8 < 0 && -1 < (int)(iVar8 - (uint)(*((ushort *)camry_host_ptr((uint32_t)(puVar5 + 0x824))))))) || (cVar12 != '\0')
         ) || (cVar2 != 'Z')) ||
       ((((int)(iVar6 - (uint)(*((ushort *)camry_host_ptr((uint32_t)(puVar5 + 0x820))))) < 0 ==
          (iVar6 < 0 && -1 < (int)(iVar6 - (uint)(*((ushort *)camry_host_ptr((uint32_t)(puVar5 + 0x820)))))) || (cVar3 != 'Z')) ||
        (iVar6 = (int)(*((short *)camry_host_ptr((uint32_t)(puVar5 + 0x822)))),
        iVar7 - iVar6 < 0 == (iVar7 < 0 != iVar6 < 0 && iVar6 < 0 == iVar7 - iVar6 < 0))))) {
      uVar4 = '\0';
      uVar15 = 0;
    }
    else {
      uVar4 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(0x844)))));
      uVar15 = uVar15 + 1;
      if (estimator_pair_window < uVar15) {
        uVar4 = 'Z';
        uVar15 = estimator_pair_window;
      }
    }
  }
  *count = uVar15;
  *qualified = uVar4;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(0x843))))) = cVar12;
  return;
}

void qualify_estimator_paired_sources(void)

{
  uint8_t stack_record_7[7];
  uint32_t puVar1;
  
  puVar1 = 0xfebeb800u;
  update_estimator_group_release();
  if (((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x7b2))))) == 'Z') && ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x82f))))) == '\0')) {
    (*((uint16_t *)(stack_record_7 + 1))) = (*((ushort *)camry_host_ptr((uint32_t)(puVar1 + 0x840))));
    advance_estimator_pair_window(((uint16_t *)((stack_record_7 + 1))),((uint8_t *)(stack_record_7)));
  }
  else {
    (*((uint16_t *)(stack_record_7 + 1))) = 0;
    stack_record_7[0] = '\0';
  }
  (*((ushort *)camry_host_ptr((uint32_t)(puVar1 + 0x840)))) = (*((uint16_t *)(stack_record_7 + 1)));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x844))))) = stack_record_7[0];
  return;
}

uint estimator_base_source_constraint(void)

{
  char cVar1;
  char cVar2;
  char cVar3;
  short sVar4;
  short sVar5;
  uint uVar8;
  int iVar9;
  int iVar10;
  int iVar6;
  int iVar7;
  
  cVar3 = DAT_febebfb4;
  cVar2 = DAT_febebfb3;
  cVar1 = DAT_febebf46;
  sVar5 = ((int)(int16_t)DAT_febeae04);
  iVar10 = (int)((volatile int16_t *)camry_host_ptr(0xaf626u))[0];
  iVar9 = (int)(*((volatile int16_t *)camry_host_ptr((uint32_t)(0xaf626u + (uint32_t)(1) * 2u))));
  sVar4 = abs_s16_wrapping(((int)(int16_t)DAT_febeae06));
  iVar6 = (int)sVar4;
  sVar5 = abs_s16_wrapping(sVar5);
  iVar7 = (int)sVar5;
  if ((((cVar2 == '\0') && (cVar3 == '\0')) &&
      (iVar6 - iVar10 < 0 != (iVar6 < 0 != iVar10 < 0 && iVar10 < 0 == iVar6 - iVar10 < 0) ||
       iVar6 == iVar10)) &&
     ((iVar7 - iVar9 < 0 != (iVar7 < 0 != iVar9 < 0 && iVar9 < 0 == iVar7 - iVar9 < 0) ||
       iVar7 == iVar9 && (cVar1 == '\0')))) {
    uVar8 = 0x5a;
  }
  else {
    uVar8 = 0;
  }
  return uVar8;
}

uint estimator_mode2_constraint_a(void)

{
  char cVar1;
  char cVar2;
  char cVar3;
  short sVar4;
  short sVar5;
  uint uVar8;
  int iVar9;
  int iVar10;
  int iVar6;
  int iVar7;
  
  sVar5 = ((int)(int16_t)DAT_febeae50);
  cVar3 = DAT_febead3c;
  cVar2 = DAT_febead35;
  cVar1 = DAT_febead34;
  iVar10 = (int)(*((volatile int16_t *)camry_host_ptr((uint32_t)(0xaf626u + (uint32_t)(2) * 2u))));
  iVar9 = (int)(*((volatile int16_t *)camry_host_ptr((uint32_t)(0xaf626u + (uint32_t)(3) * 2u))));
  sVar4 = abs_s16_wrapping(((int)(int16_t)DAT_febeae4c));
  iVar6 = (int)sVar4;
  sVar5 = abs_s16_wrapping(sVar5);
  iVar7 = (int)sVar5;
  if ((cVar3 == '\x02') &&
     ((((iVar6 - iVar10 < 0 == (iVar6 < 0 != iVar10 < 0 && iVar10 < 0 == iVar6 - iVar10 < 0) &&
         iVar6 != iVar10 ||
        (iVar7 - iVar9 < 0 == (iVar7 < 0 != iVar9 < 0 && iVar9 < 0 == iVar7 - iVar9 < 0) &&
         iVar7 != iVar9)) || (cVar1 != '\0')) || (cVar2 != '\0')))) {
    uVar8 = 0;
  }
  else {
    uVar8 = 0x5a;
  }
  return uVar8;
}

uint estimator_mode2_constraint_b(void)

{
  char cVar1;
  char cVar2;
  char cVar3;
  short sVar4;
  short sVar5;
  uint uVar8;
  int iVar9;
  int iVar10;
  int iVar6;
  int iVar7;
  
  sVar5 = ((int)(int16_t)DAT_febeae52);
  cVar3 = DAT_febead3f;
  cVar2 = DAT_febead35;
  cVar1 = DAT_febead34;
  iVar10 = (int)(*((volatile int16_t *)camry_host_ptr((uint32_t)(0xaf626u + (uint32_t)(4) * 2u))));
  iVar9 = (int)(*((volatile int16_t *)camry_host_ptr((uint32_t)(0xaf626u + (uint32_t)(5) * 2u))));
  sVar4 = abs_s16_wrapping(((int)(int16_t)DAT_febeae4e));
  iVar6 = (int)sVar4;
  sVar5 = abs_s16_wrapping(sVar5);
  iVar7 = (int)sVar5;
  if ((cVar3 == '\x02') &&
     ((((iVar6 - iVar10 < 0 == (iVar6 < 0 != iVar10 < 0 && iVar10 < 0 == iVar6 - iVar10 < 0) &&
         iVar6 != iVar10 ||
        (iVar7 - iVar9 < 0 == (iVar7 < 0 != iVar9 < 0 && iVar9 < 0 == iVar7 - iVar9 < 0) &&
         iVar7 != iVar9)) || (cVar1 != '\0')) || (cVar2 != '\0')))) {
    uVar8 = 0;
  }
  else {
    uVar8 = 0x5a;
  }
  return uVar8;
}

void qualify_estimator_source_constraints(void)

{
  char cVar1;
  char cVar2;
  char cVar3;
  undefined1 uVar4;
  uint32_t puVar5;
  uint uVar6;
  uint uVar7;
  uint uVar8;
  int iVar9;
  uint uVar10;
  
  puVar5 = 0xfebeb800u;
  uVar6 = estimator_base_source_constraint();
  uVar7 = estimator_mode2_constraint_a();
  uVar8 = estimator_mode2_constraint_b();
  if (((((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0xac4))))) != '\0') && ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0xac4))))) != '\x03')) && ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0xac1))))) != '\0')) &&
     ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0xac1))))) != '\x03')) {
    cVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0xae8)))));
    cVar2 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(0x7b2)))));
    cVar3 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(0x7b5)))));
    uVar10 = (uint)estimator_pair_axis_margin;
    iVar9 = abs_s32_wrapping
                      (((uint32_t)((uint32_t)(((uint)(*((ushort *)camry_host_ptr((uint32_t)(puVar5 + 0x7a2)))) + (uint)(*((ushort *)camry_host_ptr((uint32_t)(puVar5 + 0x7a4)))) >> 1)
                       - (uint)(*((ushort *)camry_host_ptr((uint32_t)(puVar5 + -0xa0a))))))));
    if (((((cVar2 == 'Z') && (cVar1 == '\x11')) &&
         (((int)(iVar9 - uVar10) < 0 != (iVar9 < 0 && -1 < (int)(iVar9 - uVar10)) &&
          ((cVar3 == '\0' && (uVar6 == 0x5a)))))) && (uVar7 == 0x5a)) && (uVar8 == 0x5a)) {
      uVar4 = 0x5a;
      goto LAB_000c3ec8;
    }
  }
  uVar4 = 0;
LAB_000c3ec8:
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(0x845))))) = uVar4;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(0x830))))) = (char)uVar6;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(0x831))))) = (char)uVar7;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(0x832))))) = (char)uVar8;
  return;
}

void initialize_estimator_helpers_and_c048_state_c3edc(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  fill_constant_block_c2d3e();
  initialize_secondary_estimator_stability();
  fill_constant_block_c387a();
  reset_bfc8_state_and_protected_bfd4_outputs_c3444();
  (*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + 0x874)))) = 0;
  (*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + 0x848)))) = 0;
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + 0x860)))) = 1;
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + 0x862)))) = 1;
  (*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + 0x84c)))) = 0;
  (*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + 0x878)))) = 0;
  (*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + 0x850)))) = 0;
  (*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + 0x854)))) = 0;
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + 0x864)))) = 0;
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + 0x866)))) = 0;
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + 0x868)))) = 0;
  (*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + 0x87c)))) = 0;
  (*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + 0x858)))) = 0;
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + 0x888)))) = 0;
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + 0x86a)))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x86e))))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x88a))))) = 0;
  (*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + 0x85c)))) = 0;
  (*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + 0x880)))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x88b))))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x86f))))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x88c))))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x88d))))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x870))))) = 0;
  return;
}

void reset_rate_observer(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  clear_observer_source_term();
  (*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + 0x884)))) = 0;
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + 0x86c)))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x88e))))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x88f))))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x890))))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x891))))) = 0;
  return;
}

void apply_estimator_center_reseed(void)

{
  if (DAT_febec091 == 'Z') {
    DAT_febec080 = DAT_febec0b0;
    DAT_febec078 = DAT_febec0b0 << 0xb;
    DAT_febec08d = 0x5a;
  }
  else {
    DAT_febec08d = 0;
  }
  return;
}

void apply_estimator_acquisition_reset(void)

{
  undefined1 uVar1;
  uint32_t puVar2;
  undefined4 uVar3;
  
  puVar2 = 0xfebeb800u;
  if (DAT_febec090 == 'Z') {
    puVar2 = 0xfebeb800u;
    uVar3 = raise_priority_mask_and_return_previous_d1da0(0xffc0);
    (*((undefined4 *)camry_host_ptr((uint32_t)(puVar2 + 0x7d4)))) = 0;
    (*((undefined4 *)camry_host_ptr((uint32_t)(puVar2 + 0x7e4)))) = 0xffffffff;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(0x7f0))))) = 0;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(0x7f2))))) = 0xff;
    restore_priority_mask_preserving_interrupt_enable_d1dc6(uVar3);
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(0x7f1))))) = 0;
    uVar1 = 0x5a;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(0x7fa))))) = 0;
    (*((undefined4 *)camry_host_ptr((uint32_t)(puVar2 + 0x784)))) = 0;
    (*((undefined2 *)camry_host_ptr((uint32_t)(puVar2 + 0x7e8)))) = 0;
    (*((undefined2 *)camry_host_ptr((uint32_t)(puVar2 + 0x7ea)))) = 0;
    (*((undefined4 *)camry_host_ptr((uint32_t)(puVar2 + 0x7dc)))) = 0;
    (*((undefined4 *)camry_host_ptr((uint32_t)(puVar2 + 0x7e0)))) = 0;
    (*((undefined2 *)camry_host_ptr((uint32_t)(puVar2 + 0x83e)))) = 0;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(0x842))))) = 0;
    (*((undefined2 *)camry_host_ptr((uint32_t)(puVar2 + 0x840)))) = 0;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(0x844))))) = 0;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(0x843))))) = 0;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(0x845))))) = 0;
    (*((undefined2 *)camry_host_ptr((uint32_t)(puVar2 + 0x864)))) = 0;
    (*((undefined4 *)camry_host_ptr((uint32_t)(puVar2 + 0x84c)))) = 0;
    (*((undefined2 *)camry_host_ptr((uint32_t)(puVar2 + 0x7ec)))) = 0;
    (*((undefined2 *)camry_host_ptr((uint32_t)(puVar2 + 0x7ee)))) = 0;
    (*((undefined2 *)camry_host_ptr((uint32_t)(puVar2 + 0x868)))) = 0;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(0x86e))))) = 0;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(0x88b))))) = 0;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(0x88a))))) = 0;
    (*((undefined4 *)camry_host_ptr((uint32_t)(puVar2 + 0x880)))) = 0;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(0x86f))))) = 0;
    (*((undefined4 *)camry_host_ptr((uint32_t)(puVar2 + 0x834)))) = 0;
    (*((undefined4 *)camry_host_ptr((uint32_t)(puVar2 + 0x838)))) = 0;
    (*((undefined4 *)camry_host_ptr((uint32_t)(puVar2 + 0x878)))) = 0;
  }
  else {
    uVar1 = 0;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(0x88c))))) = uVar1;
  return;
}
