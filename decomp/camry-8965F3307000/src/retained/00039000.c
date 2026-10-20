#include "common.h"

void refresh_current_reference_envelope_qualification(void)

{
  uint32_t puVar1;
  int signed_product;
  uint uVar2;
  
  puVar1 = 0xfebeb800u;
  if (DAT_febe8a20 == '\x01') {
    signed_product = current_reference_envelope_signed_product();
    uVar2 = qualify_additional_current_reference_envelope(signed_product);
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffb6a8u + (uint32_t)((int)puVar1) * 1u)))) = (char)uVar2;
  }
  return;
}

void return_only_stub_39058(void)

{
  return;
}

int clear_6eac_if_588b6_returns_zero_3905a(void)

{
  uint32_t puVar1;
  int iVar2;
  
  puVar1 = 0xfebeb800u;
  iVar2 = test_redundant_status_a5_or_vote_error13_588b6();
  if (iVar2 == 0) {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffb6acu + (uint32_t)((int)puVar1) * 1u)))) = 0;
  }
  return iVar2;
}

uint should_zero_ecu_source5_thermal_seed(ushort record_marker)

{
  int iVar1;
  int threshold;
  uint uVar2;
  
  if ((DAT_febe7bf8 & 0xff) == 0) {
    if ((DAT_febe7bf8 & 0xff00) != 0) {
      DAT_febe6ed8 = (int)((int)(int16_t)DAT_febe7dd0) - (int)((int)(int16_t)DAT_febe7dce);
      iVar1 = (int)DAT_febe6ed8;
      goto LAB_000390b6;
    }
  }
  else if ((DAT_febe7bf8 & 0xff00) == 0) {
    DAT_febe6edc = (int)((int)(int16_t)DAT_febe7dd8) - (int)((int)(int16_t)DAT_febe7dd6);
    iVar1 = (int)DAT_febe6edc;
    goto LAB_000390b6;
  }
  DAT_febe6ed8 = (int)((int)(int16_t)DAT_febe7dd0) - (int)((int)(int16_t)DAT_febe7dce);
  DAT_febe6edc = (int)((int)(int16_t)DAT_febe7dd8) - (int)((int)(int16_t)DAT_febe7dd6);
  iVar1 = (int)DAT_febe6ed8;
  if ((int)DAT_febe6edc - iVar1 < 0 !=
      ((int)DAT_febe6edc < 0 != iVar1 < 0 && iVar1 < 0 == (int)DAT_febe6edc - iVar1 < 0))
  {
    iVar1 = (int)DAT_febe6edc;
  }
LAB_000390b6:
  threshold = (int)DAT_0002b2b4;
  if ((iVar1 - threshold < 0 ==
       (iVar1 < 0 != threshold < 0 && threshold < 0 == iVar1 - threshold < 0) &&
       iVar1 != threshold) && (record_marker == 0)) {
    uVar2 = 0x5a;
  }
  else {
    uVar2 = 0;
  }
  return uVar2;
}

undefined4 compute_signed_ratio_q19_saturating_390d4(short param_1,short param_2)

{
  int iVar1;
  int iVar2;
  undefined4 local_8;
  
  iVar2 = (int)param_2;
  if (iVar2 == 0) {
    local_8 = 0;
  }
  else {
    iVar1 = (int)param_1 << 0xc;
    if (iVar2 != 0) {
      if (iVar1 == -0x80000000 && iVar2 == -1) {
        iVar1 = -0x80000000;
      }
      else {
        iVar1 = (int)iVar1 / (int)iVar2;
      }
    }
    store_symmetric_saturating_s32_product_706ae(iVar1,0x80,&local_8);
  }
  return local_8;
}

uint32_t restore_ecu_source5_thermal_model(void)

{
  uint32_t camry_r10_result;
  uint8_t stack_record_58[88];
  uint *puVar1;
  uint32_t puVar2;
  int iVar3;
  uint uVar4;
  undefined4 uVar5;
  undefined4 uVar6;
  undefined4 uVar7;
  undefined4 uVar8;
  undefined4 uVar9;
  undefined4 uVar10;
  int iVar11;
  int iVar12;
  int iVar13;
  int iVar14;
  int iVar15;
  undefined4 *puVar16;
  
  puVar2 = 0xfebeb800u;
  puVar1 = ((uint32_t *)(stack_record_58));
  puVar16 = ((undefined *)camry_host_ptr(0x21108u));
  do {
    uVar10 = *puVar16;
    puVar16 = puVar16 + 1;
    *puVar1 = uVar10;
    puVar1 = puVar1 + 1;
  } while (camry_host_addr(puVar16)!=((uint32_t)(0x21140u)));
  uVar4 = (camry_r10_result = nvm_get_record(6, camry_host_addr(((uint32_t *)(stack_record_58)))));
  if ((uVar4 == 0x10) && ((*((uint16_t *)(stack_record_58 + 50))) != 0xa55a)) {
    if ((((((*((ushort *)camry_host_ptr((uint32_t)(puVar2 + -0x3c08)))) & 0xff) == 0) ||
         (((*((ushort *)camry_host_ptr((uint32_t)(puVar2 + -0x3c08)))) & 0xff00) == 0)) && ((*((uint16_t *)(stack_record_58 + 50))) != 0x5aa5)) &&
       (uVar4 = (camry_r10_result = should_zero_ecu_source5_thermal_seed((*((uint16_t *)(stack_record_58 + 50))))), uVar4 == 0x5a)) {
      iVar3 = 0;
      iVar15 = 0;
      iVar14 = 0;
      iVar13 = 0;
      iVar12 = 0;
      iVar11 = 0;
    }
    else {
      iVar3 = (int)(*((int16_t *)(stack_record_58 + 24)));
      iVar15 = (int)(*((int16_t *)(stack_record_58 + 26)));
      iVar14 = (int)(*((int16_t *)(stack_record_58 + 28)));
      iVar13 = (int)(*((int16_t *)(stack_record_58 + 30)));
      iVar12 = (int)(*((int16_t *)(stack_record_58 + 32)));
      iVar11 = (int)(*((int16_t *)(stack_record_58 + 34)));
    }
  }
  else {
    iVar3 = (int)DAT_0002b2a6;
    iVar15 = (int)DAT_0002b2a8;
    iVar14 = (int)DAT_0002b2aa;
    iVar13 = (int)DAT_0002b2ac;
    iVar12 = (int)DAT_0002b2ae;
    iVar11 = (int)DAT_0002b2b0;
  }
  uVar10 = (camry_r10_result = compute_signed_ratio_q19_saturating_390d4(iVar3,(int)DAT_0002b28c));
  uVar5 = (camry_r10_result = compute_signed_ratio_q19_saturating_390d4(iVar15,(int)DAT_0002b28e));
  uVar6 = (camry_r10_result = compute_signed_ratio_q19_saturating_390d4(iVar14,(int)DAT_0002b290));
  uVar7 = (camry_r10_result = compute_signed_ratio_q19_saturating_390d4(iVar13,(int)DAT_0002b292));
  uVar8 = (camry_r10_result = compute_signed_ratio_q19_saturating_390d4(iVar12,(int)DAT_0002b294));
  uVar9 = (camry_r10_result = compute_signed_ratio_q19_saturating_390d4(iVar11,(int)DAT_0002b296));
  (*((undefined4 *)camry_host_ptr((uint32_t)((0xffffb6c0u + (uint32_t)((int)puVar2)))))) = uVar10;
  (*((undefined4 *)camry_host_ptr((uint32_t)((0xffffb6c4u + (uint32_t)((int)puVar2)))))) = uVar5;
  (*((undefined4 *)camry_host_ptr((uint32_t)((0xffffb6c8u + (uint32_t)((int)puVar2)))))) = uVar6;
  (*((undefined4 *)camry_host_ptr((uint32_t)((0xffffb6ccu + (uint32_t)((int)puVar2)))))) = uVar7;
  (*((undefined4 *)camry_host_ptr((uint32_t)((0xffffb6d0u + (uint32_t)((int)puVar2)))))) = uVar8;
  (*((undefined4 *)camry_host_ptr((uint32_t)((0xffffb6d4u + (uint32_t)((int)puVar2)))))) = uVar9;
  (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffb6aeu + (uint32_t)((int)puVar2)))))) = 0x3480;
  return camry_r10_result;
}

int calculate_ecu_source5_thermal_estimate(void)

{
  uint8_t stack_record_3c[60];
  short upper;
  short lower;
  uint32_t puVar1;
  int state;
  int iVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  int iVar6;
  int iVar7;
  int iVar8;
  int iVar9;
  int iVar10;
  
  iVar8 = DAT_febe70b0;
  iVar7 = DAT_febe6ef0;
  iVar6 = DAT_febe6ed4;
  iVar5 = DAT_febe6ed0;
  iVar4 = DAT_febe6ecc;
  iVar3 = DAT_febe6ec8;
  iVar2 = DAT_febe6ec4;
  puVar1 = 0xfebeb800u;
  (*((int16_t *)(stack_record_3c + 14))) = ((int)(int16_t)DAT_febe6eae);
  state = update_nonnegative_thermal_pole(DAT_febe6ec0,DAT_febe6ef0,(uint)DAT_0002b29a);
  iVar2 = update_nonnegative_thermal_pole(iVar2,iVar7,(uint)DAT_0002b29c);
  iVar3 = update_nonnegative_thermal_pole(iVar3,iVar7,(uint)DAT_0002b29e);
  iVar4 = update_nonnegative_thermal_pole(iVar4,iVar8,(uint)DAT_0002b2a0);
  iVar5 = update_nonnegative_thermal_pole(iVar5,iVar8,(uint)DAT_0002b2a2);
  iVar6 = update_nonnegative_thermal_pole(iVar6,iVar8,(uint)DAT_0002b2a4);
  lower = DAT_0002b28a;
  upper = DAT_0002b288;
  iVar9 = (int)(int16_t)DAT_0002b288;
  iVar10 = (int)(int16_t)DAT_0002b28a;
  iVar7 = scale_thermal_contribution(state,DAT_0002b28c,DAT_0002b288,DAT_0002b28a);
  iVar8 = scale_thermal_contribution(iVar2,DAT_0002b28e,upper,lower);
  (*((int16_t *)(stack_record_3c + 4))) = (short)iVar8;
  iVar8 = scale_thermal_contribution(iVar3,DAT_0002b290,upper,lower);
  (*((int16_t *)(stack_record_3c + 6))) = (short)iVar8;
  iVar8 = scale_thermal_contribution(iVar4,DAT_0002b292,upper,lower);
  (*((int16_t *)(stack_record_3c + 8))) = (short)iVar8;
  iVar8 = scale_thermal_contribution(iVar5,DAT_0002b294,upper,lower);
  (*((int16_t *)(stack_record_3c + 10))) = (short)iVar8;
  iVar8 = scale_thermal_contribution(iVar6,DAT_0002b296,upper,lower);
  (*((uint16_t *)(stack_record_3c + 12))) = (undefined2)iVar8;
  (*((int32_t *)(stack_record_3c + 0))) = (int)DAT_0002b298 +
             (int)(*((int16_t *)(stack_record_3c + 8))) + (int)(*((int16_t *)(stack_record_3c + 6))) + (*((int16_t *)(stack_record_3c + 4))) + iVar7 + (int)(*((int16_t *)(stack_record_3c + 10))) + iVar8;
  store_s32_max_third_min_first_two_7012a((*((int32_t *)(stack_record_3c + 0))),iVar9,iVar10,((int32_t *)(stack_record_3c)));
  iVar8 = apply_thermal_offset_and_following(3,(short)(*((int32_t *)(stack_record_3c + 0))),(*((int16_t *)(stack_record_3c + 14))));
  (*((int *)camry_host_ptr((uint32_t)((0xffffb6c0u + (uint32_t)((int)puVar1)))))) = state;
  (*((int *)camry_host_ptr((uint32_t)((0xffffb6c4u + (uint32_t)((int)puVar1)))))) = iVar2;
  (*((short *)camry_host_ptr((uint32_t)((0xffffb6b0u + (uint32_t)((int)puVar1)))))) = (short)(*((int32_t *)(stack_record_3c + 0)));
  (*((int *)camry_host_ptr((uint32_t)((0xffffb6c8u + (uint32_t)((int)puVar1)))))) = iVar3;
  (*((int *)camry_host_ptr((uint32_t)((0xffffb6ccu + (uint32_t)((int)puVar1)))))) = iVar4;
  (*((int *)camry_host_ptr((uint32_t)((0xffffb6d0u + (uint32_t)((int)puVar1)))))) = iVar5;
  (*((int *)camry_host_ptr((uint32_t)((0xffffb6d4u + (uint32_t)((int)puVar1)))))) = iVar6;
  (*((short *)camry_host_ptr((uint32_t)((0xffffb6b2u + (uint32_t)((int)puVar1)))))) = (short)iVar7;
  (*((short *)camry_host_ptr((uint32_t)((0xffffb6b4u + (uint32_t)((int)puVar1)))))) = (*((int16_t *)(stack_record_3c + 4)));
  (*((short *)camry_host_ptr((uint32_t)((0xffffb6b6u + (uint32_t)((int)puVar1)))))) = (*((int16_t *)(stack_record_3c + 6)));
  (*((short *)camry_host_ptr((uint32_t)((0xffffb6b8u + (uint32_t)((int)puVar1)))))) = (*((int16_t *)(stack_record_3c + 8)));
  (*((short *)camry_host_ptr((uint32_t)((0xffffb6bau + (uint32_t)((int)puVar1)))))) = (*((int16_t *)(stack_record_3c + 10)));
  (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffb6bcu + (uint32_t)((int)puVar1)))))) = (*((uint16_t *)(stack_record_3c + 12)));
  return iVar8;
}

void update_ecu_source5_thermal_estimate(void)

{
  uint32_t puVar1;
  undefined *puVar2;
  int iVar4;
  char cVar5;
  uint32_t puVar3;
  puVar3 = 0xfebeb800u;
  puVar2 = ((undefined *)camry_host_ptr(0xfebeb800u));
  cVar5 = DAT_febe6eac;
  puVar1 = (0xfebeb800u);
  if (DAT_febe6eac == '\0') {
    if ((DAT_febe7dcc != 'Z') || (DAT_febe7bf6 != 'Z')) goto LAB_0003936a;
    restore_ecu_source5_thermal_model();
    cVar5 = 'Z';
    puVar1 = ((uint32_t)(puVar3));
  }
  puVar2 = ((void *)camry_host_ptr((uint32_t)(puVar1)));
  iVar4 = calculate_ecu_source5_thermal_estimate();
  *(short *)camry_host_ptr((uint32_t)(0xffffb6aeu + (uint32_t)camry_host_addr(puVar2))) = (short)iVar4;
LAB_0003936a:
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffb6acu + (uint32_t)((int)camry_host_addr(puVar2)) * 1u)))) = cVar5;
  return;
}

void fill_constant_block_39372(void)

{
  DAT_febe6eb2 = 0;
  DAT_febe6eb4 = 0;
  DAT_febe6eb6 = 0;
  DAT_febe6eb8 = 0;
  DAT_febe6eba = 0;
  DAT_febe6ebc = 0;
  DAT_febe6ec0 = 0;
  DAT_febe6ec4 = 0;
  DAT_febe6ec8 = 0;
  DAT_febe6ecc = 0;
  DAT_febe6ed0 = 0;
  DAT_febe6ed4 = 0;
  return;
}

void return_only_stub_39390(void)

{
  return;
}

void initialize_6ee0_half_ratio_constants_39392(void)

{
  DAT_febe6ee0 = 0x569a;
  DAT_febe6ee2 = 0x2b4d;
  return;
}

void publish_ecu_source5_thermal_limit_maps(void)

{
  uint8_t stack_record_c[12];
  uint32_t puVar1;
  int iVar2;
  
  puVar1 = 0xfebeb800u;
  iVar2 = (int)((int)(int16_t)DAT_febe6eae);
  interpolate_s16_axis_u16_values_7025c(ecu_source5_current_curve_bank0,iVar2,((uint16_t *)(stack_record_c)));
  interpolate_s16_axis_u16_values_7025c(ecu_source5_current_curve_bank1,iVar2,((uint16_t *)((stack_record_c + 2))));
  (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffb6e0u + (uint32_t)((int)puVar1)))))) = (*((uint16_t *)(stack_record_c + 0)));
  (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffb6e2u + (uint32_t)((int)puVar1)))))) = (*((uint16_t *)(stack_record_c + 2)));
  return;
}

void return_only_stub_393dc(void)

{
  return;
}

void snapshot_6f06_and_6f08_halfwords_393de(void)

{
  DAT_febe6ee6 = ((int)(int16_t)DAT_febe6f06);
  DAT_febe6ee8 = ((int)(int16_t)DAT_febe6f08);
  return;
}

void poll_thermal_history_record_status(void)

{
  uint32_t puVar1;
  uint uVar2;
  char cVar3;
  
  cVar3 = DAT_febe6ee4;
  puVar1 = 0xfebeb800u;
  if (DAT_febe6ee4 == '\x01') {
    puVar1 = 0xfebeb800u;
    uVar2 = nvm_get_record_status(6);
    if (uVar2 == 0x10) {
      cVar3 = -1;
    }
    else if ((uVar2 & 0xf0) == 0x30) {
      cVar3 = -2;
    }
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffb6e4u + (uint32_t)((int)puVar1) * 1u)))) = cVar3;
  return;
}

uint scale_thermal_divisor(uint base,uint scale)

{
  uint uVar1;
  uint uVar2;
  
  uVar1 = (base & 0xffff) * (scale & 0xffff) >> 10;
  uVar2 = uVar1 & 0xffff;
  if (0xffff < uVar1) {
    uVar2 = 0xffff;
  }
  return uVar2;
}

int update_nonnegative_thermal_pole(int previous,int drive,uint divisor)

{
  uint8_t stack_record_c[12];
  int iVar1;
  uint uVar2;
  
  uVar2 = divisor & 0xffff;
  if (drive < 0) {
    if ((-1 < previous) &&
       (iVar1 = (drive + 0x7fffffff) - previous,
       iVar1 < 0 != (drive + 0x7fffffff < 0 != previous < 0 && previous < 0 == iVar1 < 0))) {
      (*((int32_t *)(stack_record_c + 0))) = -0x7fffffff;
      goto LAB_00039472;
    }
  }
  else if ((previous < 0) &&
          (iVar1 = -(0x7fffffff - drive),
          iVar1 - previous < 0 ==
          (iVar1 < 0 != previous < 0 && previous < 0 == iVar1 - previous < 0) && iVar1 != previous))
  {
    (*((int32_t *)(stack_record_c + 0))) = 0x7fffffff;
    goto LAB_00039472;
  }
  (*((int32_t *)(stack_record_c + 0))) = drive - previous;
LAB_00039472:
  if ((uVar2 != 0) && (uVar2 != 0)) {
    if ((*((int32_t *)(stack_record_c + 0))) == -0x80000000 && uVar2 == 0xffffffff) {
      (*((int32_t *)(stack_record_c + 0))) = -0x80000000;
    }
    else {
      (*((int32_t *)(stack_record_c + 0))) = (*((int32_t *)(stack_record_c + 0))) / (int)uVar2;
    }
  }
  store_symmetric_saturating_s32_sum_70674(previous,(*((int32_t *)(stack_record_c + 0))),((int32_t *)(stack_record_c)));
  store_maximum_s32_70152((*((int32_t *)(stack_record_c + 0))),0,((int32_t *)((stack_record_c + 4))));
  return (*((int32_t *)(stack_record_c + 4)));
}

int scale_thermal_contribution(int state,short gain,short upper,short lower)

{
  int iVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  uint uVar6;
  
  iVar3 = (int)gain;
  iVar4 = (int)upper;
  iVar5 = (int)lower;
  iVar2 = state / 0x80;
  if ((iVar2 == 0) || (iVar3 == 0)) {
    uVar6 = 0;
    goto LAB_000394fa;
  }
  if (iVar2 < 0) {
    if (-1 < iVar3) goto LAB_000394dc;
  }
  else if (iVar3 < 0) {
LAB_000394dc:
    iVar1 = (int)((ulonglong)((longlong)iVar3 * (longlong)iVar2) >> 0x20) + 1;
    if ((iVar1 < 0 != (-1 < (longlong)iVar3 * (longlong)iVar2 && iVar1 < 0)) ||
       (uVar6 = iVar2 * iVar3, uVar6 < 0x80000001)) {
      uVar6 = 0x80000001;
    }
    goto LAB_000394fa;
  }
  if ((-1 < (longlong)iVar3 * (longlong)iVar2 &&
       (int)((ulonglong)((longlong)iVar3 * (longlong)iVar2) >> 0x20) != 0) ||
     (uVar6 = iVar2 * iVar3, 0x7fffffff < (uint)(iVar2 * iVar3))) {
    uVar6 = 0x7fffffff;
  }
LAB_000394fa:
  iVar2 = (int)uVar6 / 0x1000;
  if (iVar2 - iVar4 < 0 != (iVar2 < 0 != iVar4 < 0 && iVar4 < 0 == iVar2 - iVar4 < 0) ||
      iVar2 == iVar4) {
    iVar4 = iVar2;
  }
  if (iVar4 - iVar5 < 0 == (iVar4 < 0 != iVar5 < 0 && iVar5 < 0 == iVar4 - iVar5 < 0)) {
    lower = (short)iVar4;
  }
  return (int)lower;
}

void reset_thermal_models_and_history_record(void)

{
  uint8_t stack_record_40[64];
  uint32_t puVar1;
  
  puVar1 = 0xfebeb800u;
  clear_6f90_and_6f98_states_3a84e();
  clear_6f8e_and_6f94_states_3a844();
  clear_6fa0_and_6fa8_states_3a990();
  clear_6f9e_and_6fa4_states_3a986();
  clear_6f16_pair_and_6f20_ratio_states_39ba2();
  clear_6f56_pair_and_6f60_ratio_states_3a25c();
  clear_6f42_pair_and_6f4c_ratio_states_39ffa();
  clear_707a_pair_and_thermal_offset_poles_3ba84();
  fill_constant_block_39372();
  clear_6ff0_pair_and_6ff4_ratio_states_3afc0();
  clear_7000_pair_and_7004_ratio_states_3b0d8();
  (*((uint32_t *)(stack_record_40 + 44))) = 0;
  (*((uint16_t *)(stack_record_40 + 50))) = 0;
  (*((uint16_t *)(stack_record_40 + 48))) = 0x7f80;
  (*((uint16_t *)(stack_record_40 + 22))) = 0;
  (*((uint16_t *)(stack_record_40 + 20))) = 0;
  (*((uint16_t *)(stack_record_40 + 42))) = 0;
  (*((uint16_t *)(stack_record_40 + 40))) = 0;
  (*((uint16_t *)(stack_record_40 + 38))) = 0;
  (*((uint16_t *)(stack_record_40 + 36))) = 0;
  (*((uint16_t *)(stack_record_40 + 34))) = 0;
  (*((uint16_t *)(stack_record_40 + 32))) = 0;
  (*((uint16_t *)(stack_record_40 + 30))) = 0;
  (*((uint16_t *)(stack_record_40 + 28))) = 0;
  (*((uint16_t *)(stack_record_40 + 26))) = 0;
  (*((uint16_t *)(stack_record_40 + 24))) = 0;
  (*((uint16_t *)(stack_record_40 + 18))) = 0;
  (*((uint16_t *)(stack_record_40 + 16))) = 0;
  (*((uint16_t *)(stack_record_40 + 14))) = 0;
  (*((uint16_t *)(stack_record_40 + 12))) = 0;
  (*((uint16_t *)(stack_record_40 + 10))) = 0;
  (*((uint16_t *)(stack_record_40 + 8))) = 0;
  (*((uint16_t *)(stack_record_40 + 6))) = 0;
  (*((uint16_t *)(stack_record_40 + 4))) = 0;
  (*((uint16_t *)(stack_record_40 + 2))) = 0;
  (*((uint16_t *)(stack_record_40 + 0))) = 0;
  fill_constant_block_398fa();
  (*((uint16_t *)(stack_record_40 + 54))) = 0;
  (*((uint16_t *)(stack_record_40 + 52))) = 0;
  (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffb6e8u + (uint32_t)((int)puVar1)))))) = 0;
  (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffb6e6u + (uint32_t)((int)puVar1)))))) = 0;
  nvm_set_record(6,(uint *)stack_record_40);
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffb6e4u + (uint32_t)((int)puVar1) * 1u)))) = 1;
  return;
}

void return_only_stub_39756(void)

{
  return;
}

void return_only_stub_39758(void)

{
  return;
}

int multiply_signed_halfwords_divide_12288_3975a(short param_1,short param_2)

{
  return ((int)param_2 * (int)param_1) / 0x3000;
}

int sum_two_pairs_of_scaled_products_with_clamps_39768(void)

{
  uint8_t stack_record_28[40];
  uint32_t puVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  int iVar6;
  int iVar7;
  int iVar8;
  
  puVar1 = 0xfebeb800u;
  iVar8 = (int)((int)(int16_t)DAT_febe65b2);
  iVar7 = (int)((int)(int16_t)DAT_febe65b4);
  iVar6 = (int)((int)(int16_t)DAT_febe65b6);
  iVar5 = (int)((int)(int16_t)DAT_febe66e8);
  iVar4 = (int)((int)(int16_t)DAT_febe66ea);
  iVar3 = (int)((int)(int16_t)DAT_febe66ec);
  iVar2 = multiply_signed_halfwords_divide_12288_3975a((int)((int)(int16_t)DAT_febe65b0),(int)((int)(int16_t)DAT_febe66e6));
  iVar5 = multiply_signed_halfwords_divide_12288_3975a(iVar8,iVar5);
  store_s32_max_third_min_first_two_7012a(iVar5 + iVar2,0x4000,(int)0xffffc000,((int32_t *)(stack_record_28)));
  iVar2 = multiply_signed_halfwords_divide_12288_3975a(iVar7,iVar4);
  iVar5 = multiply_signed_halfwords_divide_12288_3975a(iVar6,iVar3);
  store_s32_max_third_min_first_two_7012a(iVar5 + iVar2,0x4000,(int)0xffffc000,((int32_t *)((stack_record_28 + 4))));
  (*((short *)camry_host_ptr((uint32_t)((0xffffb6eeu + (uint32_t)((int)puVar1)))))) = (short)(*((int32_t *)(stack_record_28 + 4)));
  (*((short *)camry_host_ptr((uint32_t)((0xffffb6ecu + (uint32_t)((int)puVar1)))))) = (short)(*((int32_t *)(stack_record_28 + 0)));
  (*((int *)camry_host_ptr((uint32_t)((0xffffb6fcu + (uint32_t)((int)puVar1)))))) = (*((int32_t *)(stack_record_28 + 4))) + (*((int32_t *)(stack_record_28 + 0)));
  return iVar2;
}

void stage_ecu_thermal_squared_inputs(void)

{
  uint8_t stack_record_1c[28];
  uint32_t puVar1;
  int iVar2;
  int iVar3;
  
  puVar1 = 0xfebeb800u;
  iVar2 = (int)((int)(int16_t)DAT_febe6eee);
  iVar3 = (int)((int)(int16_t)DAT_febe6eec);
  store_s32_max_third_min_first_two_7012a(DAT_febe6efc * DAT_febe6efc,DAT_0002b2f0,DAT_0002b2f4,((uint32_t *)(stack_record_1c)));
  store_s32_max_third_min_first_two_7012a(iVar3 * iVar3,DAT_0002b2f8,DAT_0002b2fc,((uint32_t *)((stack_record_1c + 4))));
  store_s32_max_third_min_first_two_7012a(iVar2 * iVar2,DAT_0002b300,DAT_0002b304,((uint32_t *)((stack_record_1c + 8))));
  (*((undefined4 *)camry_host_ptr((uint32_t)((0xffffb6f0u + (uint32_t)((int)puVar1)))))) = (*((uint32_t *)(stack_record_1c + 0)));
  (*((undefined4 *)camry_host_ptr((uint32_t)((0xffffb6f4u + (uint32_t)((int)puVar1)))))) = (*((uint32_t *)(stack_record_1c + 4)));
  (*((undefined4 *)camry_host_ptr((uint32_t)((0xffffb6f8u + (uint32_t)((int)puVar1)))))) = (*((uint32_t *)(stack_record_1c + 8)));
  return;
}

void update_scaled_pair_sums_and_thermal_squared_inputs_3984a(void)

{
  sum_two_pairs_of_scaled_products_with_clamps_39768();
  stage_ecu_thermal_squared_inputs();
  return;
}

void return_only_stub_3985a(void)

{
  return;
}

uint32_t restore_thermal_drive_epoch_maxima(void)

{
  uint32_t camry_r10_result;
  uint8_t stack_record_3c[60];
  uint *puVar1;
  uint32_t puVar2;
  uint uVar3;
  undefined4 uVar4;
  undefined4 *puVar5;
  
  puVar2 = 0xfebeb800u;
  puVar1 = ((uint32_t *)(stack_record_3c));
  puVar5 = ((undefined *)camry_host_ptr(0x21140u));
  do {
    uVar4 = *puVar5;
    puVar5 = puVar5 + 1;
    *puVar1 = uVar4;
    puVar1 = puVar1 + 1;
  } while (camry_host_addr(puVar5)!=((uint32_t)(0x21178u)));
  uVar3 = (camry_r10_result = nvm_get_record(6, camry_host_addr(((uint32_t *)(stack_record_3c)))));
  if (uVar3 == 0x10) {
    (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffb706u + (uint32_t)((int)puVar2)))))) = (*((uint16_t *)(stack_record_3c + 52)));
  }
  else {
    (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffb706u + (uint32_t)((int)puVar2)))))) = 0;
    (*((uint16_t *)(stack_record_3c + 54))) = 0;
  }
  (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffb708u + (uint32_t)((int)puVar2)))))) = (*((uint16_t *)(stack_record_3c + 54)));
  return camry_r10_result;
}

void update_thermal_drive_epoch_maxima(void)

{
  bool bVar1;
  bool bVar2;
  short sVar3;
  short sVar4;
  uint32_t puVar5;
  int state;
  int iVar6;
  int iVar7;
  int iVar8;
  short sVar9;
  int iVar10;
  
  sVar3 = ((int)(int16_t)DAT_febe6f08);
  sVar4 = ((int)(int16_t)DAT_febe6f06);
  sVar9 = DAT_0002b30a;
  puVar5 = 0xfebeb800u;
  iVar8 = (int)((int)(int16_t)DAT_febe6f06);
  iVar7 = (int)((int)(int16_t)DAT_febe6f08);
  iVar10 = (int)((int)(int16_t)DAT_febe6f04);
  state = update_nonnegative_thermal_pole(DAT_febe6f0c,DAT_febe70b0,(uint)DAT_0002b308);
  iVar6 = scale_thermal_contribution(state,sVar9,0x7fff,0);
  if (iVar10 - iVar6 < 0 == (iVar10 < 0 != iVar6 < 0 && iVar6 < 0 == iVar10 - iVar6 < 0) &&
      iVar10 != iVar6) {
    iVar6 = iVar10;
  }
  sVar9 = (short)iVar6;
  if ((iVar6 - iVar8 < 0 != (iVar6 < 0 != iVar8 < 0 && iVar8 < 0 == iVar6 - iVar8 < 0) ||
       iVar6 == iVar8) &&
     (iVar10 = iVar6 - iVar7, bVar2 = iVar6 < 0, bVar1 = iVar6 != iVar7, iVar6 = iVar8,
     sVar4 = sVar3, iVar10 < 0 == (bVar2 != iVar7 < 0 && iVar7 < 0 == iVar10 < 0) && bVar1)) {
    sVar4 = sVar9;
  }
  (*((int *)camry_host_ptr((uint32_t)((0xffffb70cu + (uint32_t)((int)puVar5)))))) = state;
  (*((short *)camry_host_ptr((uint32_t)((0xffffb700u + (uint32_t)((int)puVar5)))))) = (short)iVar6;
  (*((short *)camry_host_ptr((uint32_t)((0xffffb702u + (uint32_t)((int)puVar5)))))) = sVar4;
  (*((short *)camry_host_ptr((uint32_t)((0xffffb704u + (uint32_t)((int)puVar5)))))) = sVar9;
  return;
}

void fill_constant_block_398fa(void)

{
  DAT_febe6f06 = 0;
  DAT_febe6f08 = 0;
  DAT_febe6f0c = 0;
  DAT_febe6f00 = 0;
  DAT_febe6f02 = 0;
  DAT_febe6f04 = 0;
  return;
}

void clear_6f00_6f02_6f06_6f08_halfwords_3990c(void)

{
  DAT_febe6f06 = 0;
  DAT_febe6f08 = 0;
  DAT_febe6f00 = 0;
  DAT_febe6f02 = 0;
  return;
}

void return_only_stub_3991a(void)

{
  return;
}

int clear_6f10_if_588b6_returns_zero_3991c(void)

{
  uint32_t puVar1;
  int iVar2;
  
  puVar1 = 0xfebeb800u;
  iVar2 = test_redundant_status_a5_or_vote_error13_588b6();
  if (iVar2 == 0) {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffb710u + (uint32_t)((int)puVar1) * 1u)))) = 0;
  }
  return iVar2;
}

uint should_zero_ecu_source4_thermal_seed(ushort record_marker)

{
  int iVar1;
  int threshold;
  uint uVar2;
  
  if ((DAT_febe7bf8 & 0xff) == 0) {
    if ((DAT_febe7bf8 & 0xff00) != 0) {
      DAT_febe6f28 = (int)((int)(int16_t)DAT_febe7dd0) - (int)((int)(int16_t)DAT_febe7dce);
      iVar1 = (int)DAT_febe6f28;
      goto LAB_00039978;
    }
  }
  else if ((DAT_febe7bf8 & 0xff00) == 0) {
    DAT_febe6f2c = (int)((int)(int16_t)DAT_febe7dd8) - (int)((int)(int16_t)DAT_febe7dd6);
    iVar1 = (int)DAT_febe6f2c;
    goto LAB_00039978;
  }
  DAT_febe6f28 = (int)((int)(int16_t)DAT_febe7dd0) - (int)((int)(int16_t)DAT_febe7dce);
  DAT_febe6f2c = (int)((int)(int16_t)DAT_febe7dd8) - (int)((int)(int16_t)DAT_febe7dd6);
  iVar1 = (int)DAT_febe6f28;
  if ((int)DAT_febe6f2c - iVar1 < 0 !=
      ((int)DAT_febe6f2c < 0 != iVar1 < 0 && iVar1 < 0 == (int)DAT_febe6f2c - iVar1 < 0))
  {
    iVar1 = (int)DAT_febe6f2c;
  }
LAB_00039978:
  threshold = (int)DAT_0002b328;
  if ((iVar1 - threshold < 0 ==
       (iVar1 < 0 != threshold < 0 && threshold < 0 == iVar1 - threshold < 0) &&
       iVar1 != threshold) && (record_marker == 0)) {
    uVar2 = 0x5a;
  }
  else {
    uVar2 = 0;
  }
  return uVar2;
}

int compute_signed_ratio_q19_saturating_39996(short param_1,short param_2)

{
  int iVar1;
  int iVar2;
  
  iVar2 = (int)param_2;
  if (iVar2 == 0) {
    return 0;
  }
  iVar1 = (int)param_1 << 0xc;
  if (iVar2 != 0) {
    if (iVar1 == -0x80000000 && iVar2 == -1) {
      iVar1 = -0x80000000;
    }
    else {
      iVar1 = (int)iVar1 / (int)iVar2;
    }
  }
  if (iVar1 < 0) {
    iVar2 = (int)((ulonglong)((longlong)iVar1 * 0x80) >> 0x20) + 1;
    if ((iVar2 < 0 != (-1 < (longlong)iVar1 * 0x80 && iVar2 < 0)) ||
       ((uint)(iVar1 * 0x80) < 0x80000001)) {
      return -0x7fffffff;
    }
  }
  else {
    if (iVar1 == 0) {
      return 0;
    }
    if ((-1 < (longlong)iVar1 * 0x80 && (int)((ulonglong)((longlong)iVar1 * 0x80) >> 0x20) != 0) ||
       (0x7fffffff < (uint)(iVar1 * 0x80))) {
      return 0x7fffffff;
    }
  }
  return iVar1 * 0x80;
}

void initialize_6f20_pair_of_calibrated_ratios_399e6(short param_1,short param_2)

{
  uint32_t puVar1;
  undefined4 uVar2;
  undefined4 uVar3;
  
  puVar1 = 0xfebeb800u;
  uVar2 = compute_signed_ratio_q19_saturating_39996((int)param_1,(int)DAT_0002b310);
  uVar3 = compute_signed_ratio_q19_saturating_39996((int)param_2,(int)DAT_0002b312);
  (*((undefined4 *)camry_host_ptr((uint32_t)((0xffffb720u + (uint32_t)((int)puVar1)))))) = uVar2;
  (*((undefined4 *)camry_host_ptr((uint32_t)((0xffffb724u + (uint32_t)((int)puVar1)))))) = uVar3;
  (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffb712u + (uint32_t)((int)puVar1)))))) = 0x3480;
  return;
}

void restore_ecu_source4_thermal_model(void)

{
  uint8_t stack_record_3c[60];
  uint *puVar1;
  uint32_t puVar2;
  int iVar3;
  int iVar4;
  uint uVar5;
  undefined4 uVar6;
  undefined4 *puVar7;
  
  puVar2 = 0xfebeb800u;
  puVar1 = ((uint32_t *)(stack_record_3c));
  puVar7 = ((undefined *)camry_host_ptr(0x21178u));
  do {
    uVar6 = *puVar7;
    puVar7 = puVar7 + 1;
    *puVar1 = uVar6;
    puVar1 = puVar1 + 1;
  } while (camry_host_addr(puVar7)!=((uint32_t)(0x211b0u)));
  uVar5 = nvm_get_record(6, camry_host_addr(((uint32_t *)(stack_record_3c))));
  if ((uVar5 == 0x10) && ((*((uint16_t *)(stack_record_3c + 50))) != 0xa55a)) {
    if ((((((*((ushort *)camry_host_ptr((uint32_t)(puVar2 + -0x3c08)))) & 0xff) == 0) ||
         (((*((ushort *)camry_host_ptr((uint32_t)(puVar2 + -0x3c08)))) & 0xff00) == 0)) && ((*((uint16_t *)(stack_record_3c + 50))) != 0x5aa5)) &&
       (uVar5 = should_zero_ecu_source4_thermal_seed((*((uint16_t *)(stack_record_3c + 50)))), uVar5 == 0x5a)) {
      iVar3 = 0;
      iVar4 = 0;
    }
    else {
      iVar3 = (int)(*((int16_t *)(stack_record_3c + 16)));
      iVar4 = (int)(*((int16_t *)(stack_record_3c + 18)));
    }
  }
  else {
    iVar3 = (int)DAT_0002b31e;
    iVar4 = (int)DAT_0002b320;
  }
  initialize_6f20_pair_of_calibrated_ratios_399e6(iVar3,iVar4);
  return;
}

int calculate_ecu_source4_thermal_estimate(void)

{
  short upper;
  short lower;
  short previous;
  int iVar1;
  uint32_t puVar2;
  uint divisor;
  int iVar3;
  int iVar4;
  int iVar5;
  int iVar6;
  uint uVar7;
  int iVar8;
  int iVar9;
  
  iVar9 = ((int)(int32_t)DAT_febe70b0);
  iVar8 = DAT_febe6f24;
  iVar5 = DAT_febe6f20;
  previous = ((int)(int16_t)DAT_febe6f12);
  puVar2 = 0xfebeb800u;
  iVar1 = (int)((int)(int16_t)DAT_febe64e2);
  iVar6 = (int)DAT_0002b31c;
  if (iVar1 + 0x7fff < 0 == (-1 < iVar1 && iVar1 + 0x7fff < 0) && iVar1 != -0x7fff) {
    if (iVar1 < 0) {
      iVar1 = (int)-((int)(int16_t)DAT_febe64e2);
    }
  }
  else {
    iVar1 = 0x7fff;
  }
  if ((iVar1 - iVar6 < 0 == (iVar1 < 0 != iVar6 < 0 && iVar6 < 0 == iVar1 - iVar6 < 0) &&
       iVar1 != iVar6) &&
     (((int)(int32_t)DAT_febe70b0) - DAT_0002b324 < 0 ==
      (((int)(int32_t)DAT_febe70b0) < 0 != DAT_0002b324 < 0 && DAT_0002b324 < 0 == ((int)(int32_t)DAT_febe70b0) - DAT_0002b324 < 0)
      && ((int)(int32_t)DAT_febe70b0) != DAT_0002b324)) {
    uVar7 = (uint)DAT_0002b31a;
    puVar2 = 0xfebeb800u;
    divisor = scale_thermal_divisor((uint)DAT_0002b316,uVar7);
    uVar7 = scale_thermal_divisor((uint)DAT_0002b318,uVar7);
  }
  else {
    divisor = (uint)DAT_0002b316;
    uVar7 = (uint)DAT_0002b318;
  }
  iVar1 = update_nonnegative_thermal_pole(iVar5,iVar9,divisor);
  iVar6 = update_nonnegative_thermal_pole(iVar8,iVar9,uVar7);
  lower = DAT_0002b30e;
  upper = DAT_0002b30c;
  iVar9 = (int)(int16_t)DAT_0002b30c;
  iVar8 = (int)(int16_t)DAT_0002b30e;
  iVar3 = scale_thermal_contribution(iVar1,DAT_0002b310,DAT_0002b30c,DAT_0002b30e);
  iVar4 = scale_thermal_contribution(iVar6,DAT_0002b312,upper,lower);
  iVar5 = (int)DAT_0002b314 + iVar3 + iVar4;
  if (iVar5 - iVar9 < 0 != (iVar5 < 0 != iVar9 < 0 && iVar9 < 0 == iVar5 - iVar9 < 0) ||
      iVar5 == iVar9) {
    iVar9 = iVar5;
  }
  if (iVar9 - iVar8 < 0 == (iVar9 < 0 != iVar8 < 0 && iVar8 < 0 == iVar9 - iVar8 < 0)) {
    iVar8 = iVar9;
  }
  iVar5 = apply_thermal_offset_and_following(2,(short)iVar8,previous);
  (*((short *)camry_host_ptr((uint32_t)((0xffffb714u + (uint32_t)((int)puVar2)))))) = (short)iVar8;
  (*((int *)camry_host_ptr((uint32_t)((0xffffb724u + (uint32_t)((int)puVar2)))))) = iVar6;
  (*((int *)camry_host_ptr((uint32_t)((0xffffb720u + (uint32_t)((int)puVar2)))))) = iVar1;
  (*((short *)camry_host_ptr((uint32_t)((0xffffb71au + (uint32_t)((int)puVar2)))))) = (short)divisor;
  (*((short *)camry_host_ptr((uint32_t)((0xffffb71cu + (uint32_t)((int)puVar2)))))) = (short)uVar7;
  (*((short *)camry_host_ptr((uint32_t)((0xffffb716u + (uint32_t)((int)puVar2)))))) = (short)iVar3;
  (*((short *)camry_host_ptr((uint32_t)((0xffffb718u + (uint32_t)((int)puVar2)))))) = (short)iVar4;
  return iVar5;
}

void update_ecu_source4_thermal_estimate(void)

{
  uint32_t puVar1;
  undefined *puVar2;
  int iVar4;
  char cVar5;
  uint32_t puVar3;
  puVar3 = 0xfebeb800u;
  puVar2 = ((undefined *)camry_host_ptr(0xfebeb800u));
  cVar5 = DAT_febe6f10;
  puVar1 = (0xfebeb800u);
  if (DAT_febe6f10 == '\0') {
    if ((DAT_febe7dcc != 'Z') || (DAT_febe7bf6 != 'Z')) goto LAB_00039b9a;
    restore_ecu_source4_thermal_model();
    cVar5 = 'Z';
    puVar1 = ((uint32_t)(puVar3));
  }
  puVar2 = ((void *)camry_host_ptr((uint32_t)(puVar1)));
  iVar4 = calculate_ecu_source4_thermal_estimate();
  *(short *)camry_host_ptr((uint32_t)(0xffffb712u + (uint32_t)camry_host_addr(puVar2))) = (short)iVar4;
LAB_00039b9a:
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffb710u + (uint32_t)((int)camry_host_addr(puVar2)) * 1u)))) = cVar5;
  return;
}

void clear_6f16_pair_and_6f20_ratio_states_39ba2(void)

{
  DAT_febe6f16 = 0;
  DAT_febe6f18 = 0;
  DAT_febe6f20 = 0;
  DAT_febe6f24 = 0;
  return;
}

void return_only_stub_39bb0(void)

{
  return;
}

void initialize_6f30_half_ratio_constants_39bb2(void)

{
  DAT_febe6f30 = 0x569a;
  DAT_febe6f32 = 0x2b4d;
  return;
}

void publish_ecu_source4_thermal_limit_maps(void)

{
  uint8_t stack_record_c[12];
  uint32_t puVar1;
  int iVar2;
  
  puVar1 = 0xfebeb800u;
  iVar2 = (int)((int)(int16_t)DAT_febe6f12);
  interpolate_s16_axis_u16_values_7025c(ecu_source4_current_curve_bank0,iVar2,((uint16_t *)(stack_record_c)));
  interpolate_s16_axis_u16_values_7025c(ecu_source4_current_curve_bank1,iVar2,((uint16_t *)((stack_record_c + 2))));
  (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffb730u + (uint32_t)((int)puVar1)))))) = (*((uint16_t *)(stack_record_c + 0)));
  (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffb732u + (uint32_t)((int)puVar1)))))) = (*((uint16_t *)(stack_record_c + 2)));
  return;
}

void return_only_stub_39bfc(void)

{
  return;
}

int clear_6f34_if_588b6_returns_zero_39bfe(void)

{
  uint32_t puVar1;
  int iVar2;
  
  puVar1 = 0xfebeb800u;
  iVar2 = test_redundant_status_a5_or_vote_error13_588b6();
  if (iVar2 == 0) {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffb734u + (uint32_t)((int)puVar1) * 1u)))) = 0;
  }
  return iVar2;
}

uint should_zero_ecu_source2_thermal_seed(ushort record_marker)

{
  int iVar1;
  int threshold;
  uint uVar2;
  
  if ((DAT_febe7bf8 & 0xff) == 0) {
    if ((DAT_febe7bf8 & 0xff00) != 0) {
      DAT_febe6f38 = (int)((int)(int16_t)DAT_febe7dd0) - (int)((int)(int16_t)DAT_febe7dce);
      iVar1 = (int)DAT_febe6f38;
      goto LAB_00039c5a;
    }
  }
  else if ((DAT_febe7bf8 & 0xff00) == 0) {
    DAT_febe6f3c = (int)((int)(int16_t)DAT_febe7dd8) - (int)((int)(int16_t)DAT_febe7dd6);
    iVar1 = (int)DAT_febe6f3c;
    goto LAB_00039c5a;
  }
  DAT_febe6f38 = (int)((int)(int16_t)DAT_febe7dd0) - (int)((int)(int16_t)DAT_febe7dce);
  DAT_febe6f3c = (int)((int)(int16_t)DAT_febe7dd8) - (int)((int)(int16_t)DAT_febe7dd6);
  iVar1 = (int)DAT_febe6f38;
  if ((int)DAT_febe6f3c - iVar1 < 0 !=
      ((int)DAT_febe6f3c < 0 != iVar1 < 0 && iVar1 < 0 == (int)DAT_febe6f3c - iVar1 < 0))
  {
    iVar1 = (int)DAT_febe6f3c;
  }
LAB_00039c5a:
  threshold = (int)DAT_0002b368;
  if ((iVar1 - threshold < 0 ==
       (iVar1 < 0 != threshold < 0 && threshold < 0 == iVar1 - threshold < 0) &&
       iVar1 != threshold) && (record_marker == 0)) {
    uVar2 = 0x5a;
  }
  else {
    uVar2 = 0;
  }
  return uVar2;
}

void restore_ecu_source2_thermal_model(void)

{
  uint8_t stack_record_4c[76];
  ushort uVar1;
  uint *puVar2;
  uint32_t puVar3;
  int iVar4;
  int iVar5;
  uint uVar6;
  undefined4 uVar7;
  int iVar8;
  int iVar9;
  undefined1 uVar10;
  undefined4 *puVar11;
  
  uVar1 = DAT_febe6764;
  puVar3 = 0xfebeb800u;
  puVar2 = ((uint32_t *)(stack_record_4c));
  puVar11 = ((undefined *)camry_host_ptr(0x211b0u));
  do {
    uVar7 = *puVar11;
    puVar11 = puVar11 + 1;
    *puVar2 = uVar7;
    puVar2 = puVar2 + 1;
  } while (camry_host_addr(puVar11)!=((uint32_t)(0x211e8u)));
  uVar6 = nvm_get_record(6, camry_host_addr(((uint32_t *)(stack_record_4c))));
  if ((uVar6 == 0x10) && ((*((uint16_t *)(stack_record_4c + 50))) != 0xa55a)) {
    if ((((((*((ushort *)camry_host_ptr((uint32_t)(puVar3 + -0x3c08)))) & 0xff) == 0) ||
         (((*((ushort *)camry_host_ptr((uint32_t)(puVar3 + -0x3c08)))) & 0xff00) == 0)) && ((*((uint16_t *)(stack_record_4c + 50))) != 0x5aa5)) &&
       (uVar6 = should_zero_ecu_source2_thermal_seed((*((uint16_t *)(stack_record_4c + 50)))), uVar6 == 0x5a)) {
      iVar4 = 0;
      iVar9 = 0;
      iVar5 = 0;
      iVar8 = 0;
    }
    else {
      iVar4 = (int)(*((int16_t *)(stack_record_4c + 8)));
      iVar9 = (int)(*((int16_t *)(stack_record_4c + 12)));
      iVar5 = (int)(*((int16_t *)(stack_record_4c + 10)));
      iVar8 = (int)(*((int16_t *)(stack_record_4c + 14)));
    }
  }
  else {
    iVar4 = (int)DAT_0002b39e;
    iVar9 = (int)DAT_0002b3ba;
    iVar5 = (int)DAT_0002b3a0;
    iVar8 = (int)DAT_0002b3bc;
  }
  uVar10 = 0;
  if ((uVar1 & 3) != 0) {
    uVar10 = 0x5a;
  }
  initialize_6f4c_mode_selected_ratio_pair_39efe(iVar4,iVar5,uVar10);
  initialize_6f60_mode_selected_ratio_pair_3a160(iVar9,iVar8,uVar10);
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffb735u + (uint32_t)((int)puVar3) * 1u)))) = uVar10;
  return;
}

void update_ecu_source2_thermal_estimate(void)

{
  short upper;
  short lower;
  ushort uVar1;
  undefined2 uVar2;
  uint32_t puVar3;
  int iVar4;
  int iVar5;
  char cVar6;
  uchar alternate_gains;
  
  uVar1 = DAT_febe6764;
  puVar3 = 0xfebeb800u;
  cVar6 = DAT_febe6f34;
  if (((DAT_febe7dcc == 'Z') && (DAT_febe7bf6 == 'Z')) && (DAT_febe6f34 == '\0')) {
    puVar3 = 0xfebeb800u;
    restore_ecu_source2_thermal_model();
    cVar6 = 'Z';
  }
  alternate_gains = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffb735u + (uint32_t)((int)puVar3) * 1u))));
  if (cVar6 != '\0') {
    if (((uVar1 & 3) != 0) && (alternate_gains == '\0')) {
      rebase_ecu_source2_thermal_branch0();
      rebase_ecu_source2_thermal_branch1();
      alternate_gains = 'Z';
    }
    lower = DAT_0002b366;
    upper = DAT_0002b364;
    iVar4 = update_ecu_source2_thermal_branch0(DAT_0002b364,DAT_0002b366,alternate_gains);
    iVar5 = update_ecu_source2_thermal_branch1(upper,lower,alternate_gains);
    if (iVar5 - iVar4 < 0 == (iVar5 < 0 != iVar4 < 0 && iVar4 < 0 == iVar5 - iVar4 < 0) &&
        iVar5 != iVar4) {
      uVar2 = (undefined2)iVar5;
    }
    else {
      uVar2 = (undefined2)iVar4;
    }
    (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffb736u + (uint32_t)((int)puVar3)))))) = uVar2;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffb734u + (uint32_t)((int)puVar3) * 1u)))) = cVar6;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffb735u + (uint32_t)((int)puVar3) * 1u)))) = alternate_gains;
  return;
}

void return_only_stub_39da6(void)

{
  return;
}

int update_ecu_source2_thermal_branch0(short upper,short lower,uchar alternate_gains)

{
  uint8_t stack_record_30[48];
  short gain;
  int iVar1;
  uint32_t puVar2;
  uint divisor;
  uint divisor_00;
  int iVar3;
  int iVar4;
  int iVar5;
  int iVar6;
  int iVar7;
  int iVar8;
  short gain_00;
  
  iVar4 = DAT_febe70b4;
  iVar3 = DAT_febe6f50;
  iVar5 = DAT_febe6f4c;
  puVar2 = 0xfebeb800u;
  iVar7 = (int)lower;
  iVar8 = (int)upper;
  iVar1 = (int)((int)(int16_t)DAT_febe64e2);
  (*((int16_t *)(stack_record_30 + 2))) = ((int)(int16_t)DAT_febe6f40);
  gain = DAT_0002b38e;
  gain_00 = DAT_0002b38c;
  if (alternate_gains != '\0') {
    gain = DAT_0002b392;
    gain_00 = DAT_0002b390;
  }
  if (iVar1 + 0x7fff < 0 == (-1 < iVar1 && iVar1 + 0x7fff < 0) && iVar1 != -0x7fff) {
    if (iVar1 < 0) {
      iVar1 = (int)-((int)(int16_t)DAT_febe64e2);
    }
  }
  else {
    iVar1 = 0x7fff;
  }
  iVar6 = (int)DAT_0002b39c;
  if (iVar1 > iVar6 && (int)DAT_febe70b4 > (int)DAT_0002b3a4) {
    (*((uint16_t *)(stack_record_30 + 0))) = DAT_0002b39a;
  }
  else {
    puVar2 = 0xfebeb800u;
    interpolate_u16_axis_u16_values_70304(((undefined *)camry_host_ptr(0x2b36cu)),((int)(int16_t)DAT_febe668a) & 0x7fff,stack_record_30);
  }
  divisor = scale_thermal_divisor((uint)DAT_0002b396,(uint)(*((uint16_t *)(stack_record_30 + 0))));
  divisor_00 = scale_thermal_divisor((uint)DAT_0002b398,(uint)(*((uint16_t *)(stack_record_30 + 0))));
  iVar1 = update_nonnegative_thermal_pole(iVar5,iVar4,divisor);
  iVar3 = update_nonnegative_thermal_pole(iVar3,iVar4,divisor_00);
  iVar4 = scale_thermal_contribution(iVar1,gain_00,upper,lower);
  iVar6 = scale_thermal_contribution(iVar3,gain,upper,lower);
  iVar5 = (int)DAT_0002b394 + iVar4 + iVar6;
  if (iVar5 - iVar8 < 0 != (iVar5 < 0 != iVar8 < 0 && iVar8 < 0 == iVar5 - iVar8 < 0) ||
      iVar5 == iVar8) {
    iVar8 = iVar5;
  }
  if (iVar8 - iVar7 < 0 == (iVar8 < 0 != iVar7 < 0 && iVar7 < 0 == iVar8 - iVar7 < 0)) {
    iVar7 = iVar8;
  }
  iVar5 = apply_thermal_offset_and_following(0,(short)iVar7,(*((int16_t *)(stack_record_30 + 2))));
  (*((short *)camry_host_ptr((uint32_t)((0xffffb74au + (uint32_t)((int)puVar2)))))) = (short)iVar7;
  (*((short *)camry_host_ptr((uint32_t)((0xffffb740u + (uint32_t)((int)puVar2)))))) = (short)iVar5;
  (*((int *)camry_host_ptr((uint32_t)((0xffffb74cu + (uint32_t)((int)puVar2)))))) = iVar1;
  (*((int *)camry_host_ptr((uint32_t)((0xffffb750u + (uint32_t)((int)puVar2)))))) = iVar3;
  (*((short *)camry_host_ptr((uint32_t)((0xffffb746u + (uint32_t)((int)puVar2)))))) = (short)divisor;
  (*((short *)camry_host_ptr((uint32_t)((0xffffb748u + (uint32_t)((int)puVar2)))))) = (short)divisor_00;
  (*((short *)camry_host_ptr((uint32_t)((0xffffb742u + (uint32_t)((int)puVar2)))))) = (short)iVar4;
  (*((short *)camry_host_ptr((uint32_t)((0xffffb744u + (uint32_t)((int)puVar2)))))) = (short)iVar6;
  return iVar5;
}

int compute_signed_ratio_q19_saturating_39eae(short param_1,short param_2)

{
  int iVar1;
  int iVar2;
  
  iVar2 = (int)param_2;
  if (iVar2 == 0) {
    return 0;
  }
  iVar1 = (int)param_1 << 0xc;
  if (iVar2 != 0) {
    if (iVar1 == -0x80000000 && iVar2 == -1) {
      iVar1 = -0x80000000;
    }
    else {
      iVar1 = (int)iVar1 / (int)iVar2;
    }
  }
  if (iVar1 < 0) {
    iVar2 = (int)((ulonglong)((longlong)iVar1 * 0x80) >> 0x20) + 1;
    if ((iVar2 < 0 != (-1 < (longlong)iVar1 * 0x80 && iVar2 < 0)) ||
       ((uint)(iVar1 * 0x80) < 0x80000001)) {
      return -0x7fffffff;
    }
  }
  else {
    if (iVar1 == 0) {
      return 0;
    }
    if ((-1 < (longlong)iVar1 * 0x80 && (int)((ulonglong)((longlong)iVar1 * 0x80) >> 0x20) != 0) ||
       (0x7fffffff < (uint)(iVar1 * 0x80))) {
      return 0x7fffffff;
    }
  }
  return iVar1 * 0x80;
}

void initialize_6f4c_mode_selected_ratio_pair_39efe(short param_1,short param_2,char param_3)

{
  short sVar1;
  uint32_t puVar3;
  undefined4 uVar4;
  undefined4 uVar5;
  short sVar2;
  
  puVar3 = 0xfebeb800u;
  sVar1 = DAT_0002b38c;
  sVar2 = DAT_0002b38e;
  if (param_3 != '\0') {
    sVar1 = DAT_0002b390;
    sVar2 = DAT_0002b392;
  }
  uVar4 = compute_signed_ratio_q19_saturating_39eae((int)param_1,(int)sVar1);
  uVar5 = compute_signed_ratio_q19_saturating_39eae((int)param_2,(int)sVar2);
  (*((undefined4 *)camry_host_ptr((uint32_t)((0xffffb74cu + (uint32_t)((int)puVar3)))))) = uVar4;
  (*((undefined4 *)camry_host_ptr((uint32_t)((0xffffb750u + (uint32_t)((int)puVar3)))))) = uVar5;
  (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffb740u + (uint32_t)((int)puVar3)))))) = 0x3480;
  return;
}

void rebase_ecu_source2_thermal_branch0(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  
  iVar2 = 0x7fffffff;
  iVar4 = (int)DAT_0002b390;
  iVar3 = (int)DAT_0002b392;
  if (iVar4 == 0) {
LAB_00039f72:
    iVar2 = 0;
  }
  else {
    iVar1 = ((int)DAT_febe6f4c / 0x800) * (int)DAT_0002b38c;
    if (iVar4 != 0) {
      if (iVar1 == -0x80000000 && iVar4 == -1) {
        iVar1 = -0x80000000;
      }
      else {
        iVar1 = (int)iVar1 / (int)iVar4;
      }
    }
    if (iVar1 < 0) {
      iVar2 = (int)((ulonglong)((longlong)iVar1 * 0x800) >> 0x20) + 1;
      if ((iVar2 < 0 != (-1 < (longlong)iVar1 * 0x800 && iVar2 < 0)) ||
         ((uint)(iVar1 * 0x800) < 0x80000001)) {
        iVar2 = -0x7fffffff;
        goto LAB_00039fa2;
      }
    }
    else {
      if (iVar1 == 0) goto LAB_00039f72;
      if ((-1 < (longlong)iVar1 * 0x800 && (int)((ulonglong)((longlong)iVar1 * 0x800) >> 0x20) != 0)
         || (0x7fffffff < (uint)(iVar1 * 0x800))) goto LAB_00039fa2;
    }
    iVar2 = iVar1 * 0x800;
  }
LAB_00039fa2:
  if (iVar3 != 0) {
    iVar4 = ((int)DAT_febe6f50 / 0x800) * (int)DAT_0002b38e;
    if (iVar3 != 0) {
      if (iVar4 == -0x80000000 && iVar3 == -1) {
        iVar4 = -0x80000000;
      }
      else {
        iVar4 = (int)iVar4 / (int)iVar3;
      }
    }
    if (iVar4 < 0) {
      iVar3 = (int)((ulonglong)((longlong)iVar4 * 0x800) >> 0x20) + 1;
      if ((iVar3 < 0 == (-1 < (longlong)iVar4 * 0x800 && iVar3 < 0)) &&
         (0x80000000 < (uint)(iVar4 * 0x800))) {
        DAT_febe6f4c = iVar2;
        DAT_febe6f50 = iVar4 * 0x800;
        return;
      }
      DAT_febe6f4c = iVar2;
      DAT_febe6f50 = 0x80000001;
      return;
    }
    if (iVar4 != 0) {
      if (((longlong)iVar4 * 0x800 < 0 || (int)((ulonglong)((longlong)iVar4 * 0x800) >> 0x20) == 0)
         && ((uint)(iVar4 * 0x800) < 0x80000000)) {
        DAT_febe6f4c = iVar2;
        DAT_febe6f50 = iVar4 * 0x800;
        return;
      }
      DAT_febe6f4c = iVar2;
      DAT_febe6f50 = 0x7fffffff;
      return;
    }
  }
  DAT_febe6f4c = iVar2;
  DAT_febe6f50 = 0;
  return;
}

void clear_6f42_pair_and_6f4c_ratio_states_39ffa(void)

{
  DAT_febe6f42 = 0;
  DAT_febe6f44 = 0;
  DAT_febe6f4c = 0;
  DAT_febe6f50 = 0;
  return;
}
