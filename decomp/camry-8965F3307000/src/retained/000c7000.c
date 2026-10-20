#include "common.h"

void differentiate_ac0e_and_scale_by_500_over_16_c709e(void)

{
  if (DAT_febec399 == '\0') {
    DAT_febec399 = '\x01';
    DAT_febec314 = 0;
  }
  else {
    DAT_febec314 = (int)((int)(int16_t)DAT_febeac0e) - (int)((int)(int16_t)DAT_febec36e);
  }
  DAT_febec36e = ((int)(int16_t)DAT_febeac0e);
  DAT_febec318 = (int)((DAT_febec314 * 500)) / (int)0x10;
  return;
}

void filter_c318_twice_and_bound_c370_c70d6(void)

{
  int iVar1;
  int iVar2;
  
  DAT_febec31c = (DAT_febec318 + DAT_febec31c) - DAT_febec324;
  DAT_febec324 = DAT_febec31c * 0x400;
  if (DAT_000b00e0 != 0) {
    if (DAT_febec324 == -0x80000000 && DAT_000b00e0 == -1) {
      DAT_febec324 = -0x80000000;
    }
    else {
      DAT_febec324 = (uint)((int)DAT_febec324 / (int)DAT_000b00e0);
    }
  }
  DAT_febec320 = (DAT_febec320 + DAT_febec324) - DAT_febec328;
  DAT_febec328 = DAT_febec320 * 0x400;
  iVar2 = (int)DAT_000b00f8;
  if (DAT_000b00e4 != 0) {
    if (DAT_febec328 == -0x80000000 && DAT_000b00e4 == -1) {
      DAT_febec328 = -0x80000000;
    }
    else {
      DAT_febec328 = (uint)((int)DAT_febec328 / (int)DAT_000b00e4);
    }
  }
  iVar1 = (int)DAT_febec328;
  iVar2 = (int)(short)DAT_000b00f8;
  if (iVar1 > iVar2) {
    DAT_febec370 = (short)iVar2;
  }
  else if (iVar1 <= -iVar2) {
    DAT_febec370 = (short)(-iVar2);
  }
  else {
    DAT_febec370 = (short)iVar1;
  }
  return;
}

uint32_t interpolate_three_banked_curves_into_c372_c374_c376_c713c(void)

{
  uint32_t camry_r10_result;
  ushort input;
  uchar *puVar1;
  uint32_t puVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  undefined4 uVar6;
  
  input = DAT_febeadf6;
  puVar2 = 0xfebeb800u;
  iVar5 = (DAT_febec156 & 3) * 0x24;
  DAT_febec38a = (undefined2)(DAT_febec156 & 3);
  puVar1 = ((void *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xb144cu + (uint32_t)(DAT_febeac3c & 1) * 4u)))))));
  iVar3 = (camry_r10_result = interpolate_unsigned_axis_sentinel_curve
                    ((ushort *)(puVar1 + iVar5 + 0x13ac),DAT_febeadf6));
  iVar4 = (camry_r10_result = interpolate_unsigned_axis_sentinel_curve((ushort *)(puVar1 + iVar5 + 0x143c),input));
  iVar5 = (camry_r10_result = interpolate_unsigned_axis_sentinel_curve((ushort *)(puVar1 + iVar5 + 0x131c),input));
  uVar6 = (camry_r10_result = raise_priority_mask_and_return_previous_d1da0(0xffc0));
  (*((short *)camry_host_ptr((uint32_t)(puVar2 + 0xb72)))) = (short)iVar3;
  (*((short *)camry_host_ptr((uint32_t)(puVar2 + 0xb74)))) = (short)iVar4;
  (*((short *)camry_host_ptr((uint32_t)(puVar2 + 0xb76)))) = (short)iVar5;
  restore_priority_mask_preserving_interrupt_enable_d1dc6(uVar6);
  return camry_r10_result;
}

void interpolate_b0102_curve_into_c37a_c71b6(void)

{
  uint32_t puVar1;
  int iVar2;
  
  puVar1 = 0xfebeb800u;
  iVar2 = interpolate_unsigned_axis_sentinel_curve((ushort *)((undefined *)camry_host_ptr(0xb0102u)),DAT_febeadf6);
  (*((short *)camry_host_ptr((uint32_t)(puVar1 + 0xb7a)))) = (short)iVar2;
  return;
}

void update_observer_dependent_assist_bound(void)

{
  bool bVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  
  iVar4 = (int)DAT_000b00da;
  iVar2 = (int)DAT_000b00fe;
  if (DAT_febec08f == '\0') {
    DAT_febec39a = '\x01';
    iVar2 = (int)DAT_000b0100;
    iVar5 = iVar4;
  }
  else {
    iVar5 = (int)DAT_000b00d8;
    if (DAT_febec39a != '\0') {
      iVar2 = (int)DAT_000b0100;
      iVar5 = iVar4;
    }
  }
  DAT_febec32c = (iVar5 - ((int)(int16_t)DAT_febec37c)) * iVar2 + DAT_febec32c;
  iVar2 = (int)(short)((int)DAT_febec32c / 0x4000);
  if (DAT_febec39a == '\x01') {
    iVar3 = (int)DAT_000b00dc;
    iVar5 = iVar2 - iVar3;
    bVar1 = iVar2 < 0 != iVar3 < 0 && iVar3 < 0 == iVar5 < 0;
    DAT_febec39a = iVar5 < 0 == bVar1 && iVar2 != iVar3;
    if (iVar5 < 0 == bVar1 && iVar2 != iVar3) goto LAB_000c7264;
  }
  else {
    iVar5 = (int)DAT_000b00de;
    iVar4 = (int)DAT_000b00d8;
    if (iVar2 - iVar5 < 0 != (iVar2 < 0 != iVar5 < 0 && iVar5 < 0 == iVar2 - iVar5 < 0))
    goto LAB_000c7264;
  }
  iVar2 = iVar4;
  DAT_febec32c = iVar2 << 0xe;
LAB_000c7264:
  DAT_febec37c = (short)iVar2;
  DAT_febec37e = (short)((((int)DAT_000b00fc - (int)DAT_000b00fa) * iVar2) / 0x400) + DAT_000b00fa;
  return;
}

void map_observer_rate_to_assist_bound(void)

{
  uint32_t puVar1;
  short sVar2;
  int iVar3;
  
  puVar1 = 0xfebeb800u;
  if ((int)DAT_febec084 + -0x7fff < 0 == ((int)DAT_febec084 < 0 && -1 < (int)DAT_febec084 + -0x7fff) &&
      ((int)(int32_t)DAT_febec084) != 0x7fff) {
    sVar2 = 0x7fff;
  }
  else {
    sVar2 = (short)((int)(int32_t)DAT_febec084);
    if ((int)DAT_febec084 + 0x7fff < 0 != (-1 < (int)DAT_febec084 && (int)DAT_febec084 + 0x7fff < 0)) {
      sVar2 = -0x7fff;
    }
  }
  sVar2 = abs_s16_wrapping(sVar2);
  iVar3 = interpolate_signed_sentinel_curve((short *)((undefined *)camry_host_ptr(0xb0126u)),sVar2);
  (*((short *)camry_host_ptr((uint32_t)(puVar1 + 0xb78)))) = (short)iVar3;
  return;
}

void compose_observer_dependent_assist(void)

{
  int sum;
  int limit;
  int clamped;
  int bound;
  int narrowed;
  
  sum = (int)(int16_t)DAT_febec894 + (int)(int16_t)DAT_febec4a0 + (int)(int16_t)DAT_febec3ea +
        (int)(int16_t)DAT_febec524 + (int)(int16_t)DAT_febec2e2;
  limit = (int)(int16_t)DAT_febec378;
  if (sum > limit) {
    clamped = limit;
  }
  else if (sum <= -limit) {
    clamped = -limit;
  }
  else {
    clamped = sum;
  }
  bound = (int)(int16_t)DAT_febec37e;
  if (bound >= (int)(int16_t)DAT_febec37a) {
    bound = (int)(int16_t)DAT_febec37a;
  }
  DAT_febec380 = (short)bound;
  if (clamped > bound) {
    narrowed = bound;
  }
  else if (clamped <= -bound) {
    narrowed = -bound;
  }
  else {
    narrowed = clamped;
  }
  DAT_febec330 = (uint)sum;
  DAT_febec334 = (uint)clamped;
  DAT_febec3a0 = (short)narrowed;
  return;
}

void compute_bounded_two_product_sum_and_c386_complement_c731c(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  
  iVar3 = (int)((int)(int16_t)DAT_febec1a2);
  iVar2 = (int)DAT_000b00f2;
  DAT_febec382 = DAT_000b00f2;
  if ((iVar3 - iVar2 < 0 != (iVar3 < 0 != iVar2 < 0 && iVar2 < 0 == iVar3 - iVar2 < 0) ||
       iVar3 == iVar2) &&
     (iVar1 = -iVar2, DAT_febec382 = ((int)(int16_t)DAT_febec1a2),
     iVar3 + iVar2 < 0 != (iVar3 < 0 != iVar1 < 0 && iVar1 < 0 == iVar3 + iVar2 < 0) ||
     iVar3 == iVar1)) {
    DAT_febec382 = (short)iVar1;
  }
  DAT_febec38e = ((int)(int16_t)DAT_febeac0e);
  DAT_febec354 = ((int)(int16_t)DAT_febec382 * (int)(int16_t)DAT_febeac0e) / 0x40;
  DAT_febec394 = ((int)(int16_t)DAT_febec372);
  DAT_febec338 = (int)(((int)(int16_t)DAT_febec372 * (int)DAT_febec354)) / (int)0x200;
  DAT_febec33c = ((int)((int)(int16_t)DAT_febec374) * (((int)((int)(int16_t)DAT_febec36c) * (int)((int)(int16_t)DAT_febec370)) / 4)) / 0x400;
  DAT_febec340 = DAT_febec33c + DAT_febec338;
  iVar2 = (int)DAT_000b00ec;
  iVar3 = (int)DAT_000b00ee;
  if ((((int)(int32_t)DAT_febec340) - iVar2 < 0 !=
       (((int)(int32_t)DAT_febec340) < 0 != iVar2 < 0 && iVar2 < 0 == ((int)(int32_t)DAT_febec340) - iVar2 < 0) ||
       ((int)(int32_t)DAT_febec340) == iVar2) &&
     (iVar2 = iVar3,
     ((int)(int32_t)DAT_febec340) - iVar3 < 0 ==
     (((int)(int32_t)DAT_febec340) < 0 != iVar3 < 0 && iVar3 < 0 == ((int)(int32_t)DAT_febec340) - iVar3 < 0) &&
     ((int)(int32_t)DAT_febec340) != iVar3)) {
    iVar2 = ((int)(int32_t)DAT_febec340);
  }
  DAT_febec384 = (short)iVar2;
  DAT_febec386 = 0x400 - (short)iVar2;
  return;
}

void fill_constant_block_c73c4(void)

{
  DAT_febec3ba = 0;
  DAT_febec3b0 = 0;
  DAT_febec3a4 = 0;
  DAT_febec3b2 = 0;
  DAT_febec3b4 = 0;
  DAT_febec3b6 = 0;
  DAT_febeabb0 = 0;
  DAT_febec3a8 = 0;
  DAT_febec3ac = 0;
  DAT_febec3b8 = 0;
  return;
}

int map_first_model_derivative_compensation(void)

{
  short input;
  short sVar1;
  uint32_t puVar2;
  short sVar3;
  int iVar4;
  
  sVar1 = ((int)(int16_t)DAT_febec23c);
  puVar2 = 0xfebeb800u;
  sVar3 = abs_s16_wrapping(((int)(int16_t)DAT_febec23c));
  input = (*((short *)camry_host_ptr((uint32_t)(puVar2 + 0x740))));
  iVar4 = interpolate_signed_sentinel_curve((short *)((undefined *)camry_host_ptr(0xb11d2u)),sVar3);
  sVar3 = (short)iVar4;
  if (sVar1 < 0) {
    sVar3 = -sVar3;
  }
  iVar4 = interpolate_signed_sentinel_curve
                    (((short *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xb1454u + (uint32_t)((byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0xbc4))))) & 1) * 4u)))) + 0xc))),input);
  (*((int *)camry_host_ptr((uint32_t)(puVar2 + 0xba4)))) = (int)(((((int)(short)iVar4 * (int)sVar3) / 0x400) * (int)(*((short *)camry_host_ptr((uint32_t)(puVar2 + 0xbb0)))))) / (int)0x400;
  return iVar4;
}

int map_second_model_derivative_compensation(void)

{
  short input;
  short sVar1;
  uint32_t puVar2;
  short sVar3;
  int iVar4;
  
  sVar1 = ((int)(int16_t)DAT_febec23e);
  puVar2 = 0xfebeb800u;
  sVar3 = abs_s16_wrapping(((int)(int16_t)DAT_febec23e));
  input = (*((short *)camry_host_ptr((uint32_t)(puVar2 + 0x740))));
  iVar4 = interpolate_signed_sentinel_curve((short *)((undefined *)camry_host_ptr(0xb11e6u)),sVar3);
  sVar3 = (short)iVar4;
  if (sVar1 < 0) {
    sVar3 = -sVar3;
  }
  (*((short *)camry_host_ptr((uint32_t)(puVar2 + 0xbb4)))) = sVar3;
  (*((short *)camry_host_ptr((uint32_t)(puVar2 + 3000)))) = sVar1;
  iVar4 = interpolate_signed_sentinel_curve((short *)((undefined *)camry_host_ptr(0xb11aeu)),input);
  (*((short *)camry_host_ptr((uint32_t)(puVar2 + 0xbb6)))) = (short)iVar4;
  (*((int *)camry_host_ptr((uint32_t)(puVar2 + -0xc50)))) = (int)(((int)(short)iVar4 * (int)(short)( (int)(((int)sVar3 * (int)(*((short *)camry_host_ptr((uint32_t)(puVar2 + 0xbb2)))))) / (int)0x400))) / (int)0x400;
  return iVar4;
}

void publish_model_derivative_compensation(void)

{
  int iVar1;
  int iVar2;
  
  DAT_febec3ac = DAT_febeabb0 + DAT_febec3a4;
  DAT_febec3a8 = (int)(((DAT_febeabb0 + DAT_febec3a4) * 0x400)) / (int)0x400;
  iVar1 = (int)DAT_febec3a8;
  iVar2 = (int)(short)DAT_000b11ac;
  if (iVar1 > iVar2) {
    DAT_febec3ba = (short)iVar2;
  }
  else if (iVar1 <= -iVar2) {
    DAT_febec3ba = (short)(-iVar2);
  }
  else {
    DAT_febec3ba = (short)iVar1;
  }
  return;
}

uint32_t interpolate_banked_coefficient_and_14cc_curve_pair_c74e2(void)

{
  uint32_t camry_r10_result;
  ushort input;
  uint uVar1;
  uchar *puVar2;
  uint32_t puVar3;
  int iVar4;
  
  input = DAT_febeadf6;
  puVar3 = 0xfebeb800u;
  uVar1 = (uint)DAT_febec156;
  iVar4 = (camry_r10_result = interpolate_unsigned_axis_sentinel_curve
                    (((ushort *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xb1454u + (uint32_t)(DAT_febeac3c & 1) * 4u)))) + 0x30))),DAT_febeadf6));
  puVar2 = ((void *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xb144cu + (uint32_t)((byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0xbc4))))) & 1) * 4u)))))));
  (*((short *)camry_host_ptr((uint32_t)(puVar3 + 0xbb0)))) = (short)iVar4;
  iVar4 = (camry_r10_result = interpolate_unsigned_axis_sentinel_curve
                    ((ushort *)(puVar2 + (uVar1 & 3) * 0x24 + 0x14cc),input));
  (*((short *)camry_host_ptr((uint32_t)(puVar3 + 0xbb2)))) = (short)iVar4;
  return camry_r10_result;
}

void reset_c3bc_curve_filter_filter_and_latches_c7540(void)

{
  DAT_febec3e2 = 0;
  DAT_febec3e8 = 0;
  DAT_febec3e7 = 0;
  DAT_febec3de = 0;
  DAT_febec3e6 = 0;
  DAT_febec3e4 = 0;
  DAT_febec3c4 = 0;
  DAT_febec3c0 = 0;
  DAT_febec3dc = 0;
  DAT_febec3e0 = 0;
  DAT_febec3bc = 0;
  DAT_febec3cc = 0;
  DAT_febec3da = 0;
  DAT_febec3d8 = 0;
  DAT_febec3d6 = 0;
  DAT_febec3d4 = 0;
  DAT_febec3d2 = 0;
  DAT_febec3d0 = 0;
  DAT_febeabb4 = 0;
  DAT_febec3ce = 0;
  DAT_febec3ea = 0;
  DAT_febec3e9 = 0x5a;
  DAT_febec3e5 = 0x5a;
  DAT_febec3c8 = PTR_DAT_000b0140;
  return;
}

void retain_acd8_enable_for_calibrated_release_delay_c75ae(void)

{
  if ((DAT_febeacd4 == '\0') && (DAT_febeacbd == '\0')) {
    if (DAT_febeacd8 == '\x01') {
      DAT_febec3de = 0;
      DAT_febec3e6 = DAT_febeacd8;
      DAT_febec3e7 = 0;
      DAT_febec3e8 = 1;
      return;
    }
    if ((DAT_febec3e6 != '\x01') && (DAT_febec3e7 != '\x01')) {
      DAT_febec3e6 = DAT_febeacd8;
      return;
    }
    if (DAT_febec3de < DAT_000b014c) {
      DAT_febec3de = DAT_febec3de + 1;
      DAT_febec3e6 = DAT_febeacd8;
      DAT_febec3e7 = 1;
      return;
    }
  }
  DAT_febec3e8 = 0;
  DAT_febec3e7 = 0;
  DAT_febec3de = 0;
  DAT_febec3e6 = DAT_febeacd8;
  return;
}

void slew_curve_blend_weight_and_filter_signed_c3e0_c7612(ushort param_1,short param_2)

{
  bool bVar1;
  short sVar2;
  int iVar3;
  uint32_t puVar4;
  short sVar5;
  int iVar6;
  int iVar7;
  short sVar9;
  int iVar10;
  short value;
  int iVar8;
  
  sVar2 = ((int)(int16_t)DAT_febec3da);
  puVar4 = 0xfebeb800u;
  iVar7 = (DAT_febec156 & 3) * 0x28;
  iVar6 = interpolate_unsigned_axis_sentinel_curve
                    (((ushort *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xb144cu + (uint32_t)(DAT_febeac3c & 1) * 4u)))) + iVar7 + 0x15fc))),
                     param_1);
  iVar7 = interpolate_unsigned_axis_sentinel_curve
                    ((ushort *)
                     (((undefined *)camry_host_ptr((uint32_t)(0x155cu + (uint32_t)((int)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xb144cu + (uint32_t)((byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0xbc4))))) & 1) * 4u)))) + iVar7)) * 1u)))),param_1);
  iVar10 = 0;
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(0xbe8))))) == '\x01') {
    iVar10 = 0x400;
  }
  sVar9 = (short)iVar10;
  value = sVar9 - sVar2;
  sVar5 = abs_s16_wrapping(value);
  iVar8 = (int)sVar5;
  iVar3 = (int)DAT_000b014e;
  if (iVar8 - iVar3 < 0 == (iVar8 < 0 != iVar3 < 0 && iVar3 < 0 == iVar8 - iVar3 < 0) &&
      iVar8 != iVar3) {
    sVar5 = DAT_000b014e;
    if (value < 1) {
      sVar5 = -DAT_000b014e;
    }
    iVar10 = (int)(short)(sVar5 + sVar2);
  }
  (*((short *)camry_host_ptr((uint32_t)(puVar4 + 0xbda)))) = (short)iVar10;
  (*((short *)camry_host_ptr((uint32_t)(puVar4 + 0xbd2)))) = (short)iVar6;
  (*((short *)camry_host_ptr((uint32_t)(puVar4 + 0xbd4)))) = (short)iVar7;
  (*((short *)camry_host_ptr((uint32_t)(puVar4 + 0xbd8)))) = sVar9;
  sVar2 = (short)(((iVar6 - iVar7) * iVar10) / 0x400) + (short)iVar7;
  (*((short *)camry_host_ptr((uint32_t)(puVar4 + 0xbd6)))) = sVar2;
  sVar2 = (short)( (int)(((int)(*((short *)camry_host_ptr((uint32_t)(puVar4 + 0xbcc)))) * (int)sVar2)) / (int)0x400);
  if (param_2 < 0) {
    sVar2 = -sVar2;
  }
  iVar7 = (int)DAT_000b0148;
  iVar6 = (int)sVar2;
  (*((short *)camry_host_ptr((uint32_t)(puVar4 + 0xbd0)))) = sVar2;
  sVar9 = DAT_000b0148;
  if ((iVar6 - iVar7 < 0 != (iVar6 < 0 != iVar7 < 0 && iVar7 < 0 == iVar6 - iVar7 < 0) ||
       iVar6 == iVar7) &&
     (iVar7 = iVar6 + DAT_000b0148, bVar1 = -(int)DAT_000b0148 < 0, sVar9 = sVar2,
     iVar7 < 0 != (iVar6 < 0 != bVar1 && bVar1 == iVar7 < 0))) {
    sVar9 = -DAT_000b0148;
  }
  iVar7 = ((*((int *)camry_host_ptr((uint32_t)(puVar4 + 0xbbc)))) + (int)sVar9) - (int)(*((short *)camry_host_ptr((uint32_t)(puVar4 + 0xbe0))));
  (*((int *)camry_host_ptr((uint32_t)(puVar4 + 0xbbc)))) = iVar7;
  iVar7 = iVar7 * 0x400;
  if (DAT_000b013c != 0) {
    if (iVar7 == -0x80000000 && DAT_000b013c == -1) {
      iVar7 = 0;
    }
    else {
      iVar7 = iVar7 / (int)DAT_000b013c;
    }
  }
  (*((short *)camry_host_ptr((uint32_t)(puVar4 + 0xbe0)))) = (short)iVar7;
  return;
}

void latch_c3e9_after_low_adf6_duration_c772a(void)

{
  if ((DAT_febead18 == '\x11') && (DAT_febeadf6 <= DAT_000b0156)) {
    if (DAT_000b0158 <= DAT_febec3e2) {
      DAT_febec3e9 = 0x5a;
      return;
    }
    DAT_febec3e2 = DAT_febec3e2 + 1;
    return;
  }
  DAT_febec3e2 = 0;
  DAT_febec3e9 = 0;
  return;
}

void step_c3dc_enable_envelope_with_inhibit_latch_c7770(short param_1,char param_2)

{
  bool bVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  
  iVar2 = (int)param_1;
  iVar4 = (int)((int)(int16_t)DAT_febec3dc);
  iVar3 = (int)DAT_000b0150;
  if ((((param_2 == '\0') || (DAT_febead18 != '\x11')) || (DAT_febec3e9 == 'Z')) ||
     (DAT_febead41 == 'Z')) {
    DAT_febec3c0 = DAT_febec3c4 * (int)PTR_DAT_000b0140;
    if (DAT_febec3c8 != 0) {
      if (DAT_febec3c0 == -0x80000000 && DAT_febec3c8 == 0xffffffffu) {
        DAT_febec3c0 = -0x80000000;
      }
      else {
        DAT_febec3c0 = DAT_febec3c0 / (int)DAT_febec3c8;
      }
    }
    DAT_febec3c4 = DAT_febec3c0 - iVar4;
    iVar2 = DAT_febec3c4 * 0x400;
    if (PTR_DAT_000b0140 != 0) {
      if (iVar2 == -0x80000000 && PTR_DAT_000b0140 == 0xffffffffu) {
        iVar2 = 0;
      }
      else {
        iVar2 = iVar2 / (int)PTR_DAT_000b0140;
      }
    }
    iVar4 = (int)(short)iVar2;
    DAT_febec3c8 = PTR_DAT_000b0140;
  }
  else {
    if (DAT_febec3e4 == '\0') {
      if (iVar2 - iVar3 < 0 != (iVar2 < 0 != iVar3 < 0 && iVar3 < 0 == iVar2 - iVar3 < 0) ||
          iVar2 == iVar3) {
        DAT_febec3c0 = DAT_febec3c4 * (int)PTR_DAT_000b0144;
        if (DAT_febec3c8 != 0) {
          if (DAT_febec3c0 == -0x80000000 && DAT_febec3c8 == 0xffffffffu) {
            DAT_febec3c0 = -0x80000000;
          }
          else {
            DAT_febec3c0 = DAT_febec3c0 / (int)DAT_febec3c8;
          }
        }
        DAT_febec3c4 = (DAT_febec3c0 + 0x100) - iVar4;
        iVar2 = DAT_febec3c4 * 0x400;
        if (PTR_DAT_000b0144 != 0) {
          if (iVar2 == -0x80000000 && PTR_DAT_000b0144 == 0xffffffffu) {
            iVar2 = 0;
          }
          else {
            iVar2 = iVar2 / (int)PTR_DAT_000b0144;
          }
        }
        iVar4 = (int)(short)iVar2;
        DAT_febec3c8 = PTR_DAT_000b0144;
      }
    }
    else {
      DAT_febec3c0 = DAT_febec3c4 * (int)PTR_DAT_000b0140;
      if (DAT_febec3c8 != 0) {
        if (DAT_febec3c0 == -0x80000000 && DAT_febec3c8 == 0xffffffffu) {
          DAT_febec3c0 = -0x80000000;
        }
        else {
          DAT_febec3c0 = DAT_febec3c0 / (int)DAT_febec3c8;
        }
      }
      DAT_febec3c4 = DAT_febec3c0 - iVar4;
      iVar2 = DAT_febec3c4 * 0x400;
      if (PTR_DAT_000b0140 != 0) {
        if (iVar2 == -0x80000000 && PTR_DAT_000b0140 == 0xffffffffu) {
          iVar2 = 0;
        }
        else {
          iVar2 = iVar2 / (int)PTR_DAT_000b0140;
        }
      }
      iVar4 = (int)(short)iVar2;
      DAT_febec3c8 = PTR_DAT_000b0140;
    }
    if (DAT_febec3e4 != '\x01') {
      iVar2 = (int)DAT_000b0154;
      if (iVar4 - iVar2 < 0 == (iVar4 < 0 != iVar2 < 0 && iVar2 < 0 == iVar4 - iVar2 < 0)) {
        iVar4 = 0x100;
        DAT_febec3c4 = ((int)PTR_DAT_000b0144 << 8) / 0x400;
        DAT_febec3c0 = DAT_febec3c4;
      }
      goto LAB_000c7856;
    }
  }
  iVar3 = (int)DAT_000b0152;
  iVar2 = iVar4 - iVar3;
  bVar1 = iVar4 < 0 != iVar3 < 0 && iVar3 < 0 == iVar2 < 0;
  DAT_febec3e4 = iVar2 < 0 == bVar1 && iVar4 != iVar3;
  if (iVar2 < 0 != bVar1 || iVar4 == iVar3) {
    iVar4 = 0;
    DAT_febec3c0 = 0;
    DAT_febec3c4 = 0;
  }
LAB_000c7856:
  DAT_febec3dc = (short)iVar4;
  return;
}

void apply_c3dc_envelope_with_c3e5_zero_latch_c786c(char param_1)

{
  int iVar1;
  
  iVar1 = ((int)(int16_t)DAT_febec3dc * (int)(int16_t)DAT_febec3e0) / 0x100;
  if (iVar1 + -0x7fff < 0 == (iVar1 < 0 && -1 < iVar1 + -0x7fff) && iVar1 != 0x7fff) {
    iVar1 = 0x7fff;
  }
  else if (iVar1 + 0x7fff < 0 != (-1 < iVar1 && iVar1 + 0x7fff < 0)) {
    iVar1 = -0x7fff;
  }
  DAT_febeabb4 = (undefined2)iVar1;
  if (param_1 == '\0') {
    DAT_febec3e5 = 'Z';
  }
  else {
    if (DAT_febec3e4 == '\0') {
      DAT_febec3ce = DAT_febeabb4;
      DAT_febec3e5 = 0;
      return;
    }
    if (DAT_febec3e5 != 'Z') {
      DAT_febec3ce = DAT_febeabb4;
      return;
    }
  }
  DAT_febec3ce = DAT_febeabb4;
  DAT_febeabb4 = 0;
  return;
}

void bound_abb4_by_b014a_into_c3ea_c78cc(void)

{
  bool bVar1;
  int iVar2;
  int iVar3;
  
  iVar3 = (int)((int)(int16_t)DAT_febeabb4);
  iVar2 = (int)DAT_000b014a;
  DAT_febec3ea = DAT_000b014a;
  if ((iVar3 - iVar2 < 0 != (iVar3 < 0 != iVar2 < 0 && iVar2 < 0 == iVar3 - iVar2 < 0) ||
       iVar3 == iVar2) &&
     (iVar2 = iVar3 + DAT_000b014a, bVar1 = -(int)DAT_000b014a < 0, DAT_febec3ea = ((int)(int16_t)DAT_febeabb4),
     iVar2 < 0 != (iVar3 < 0 != bVar1 && bVar1 == iVar2 < 0))) {
    DAT_febec3ea = -DAT_000b014a;
  }
  return;
}

void update_c3e9_inhibit_envelope_output_and_bound_c78f2(short param_1,undefined1 param_2)

{
  latch_c3e9_after_low_adf6_duration_c772a();
  step_c3dc_enable_envelope_with_inhibit_latch_c7770((int)(short)param_1, (uint)(byte)param_2);
  apply_c3dc_envelope_with_c3e5_zero_latch_c786c((uint)(byte)param_2);
  bound_abb4_by_b014a_into_c3ea_c78cc();
  return;
}

void snapshot_c084_and_run_c3bc_curve_curve_filter_c7912(void)

{
  undefined1 uVar1;
  uint32_t puVar2;
  short sVar3;
  undefined4 uVar4;
  int iVar5;
  int iVar6;
  
  puVar2 = 0xfebeb800u;
  uVar4 = raise_priority_mask_and_return_previous_d1da0(0xffc0);
  uVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(0x88e)))));
  iVar6 = (*((int *)camry_host_ptr((uint32_t)(puVar2 + 0x884))));
  restore_priority_mask_preserving_interrupt_enable_d1dc6(uVar4);
  if (iVar6 + -0x7fff < 0 == (iVar6 < 0 && -1 < iVar6 + -0x7fff) && iVar6 != 0x7fff) {
    iVar5 = 0x7fff;
  }
  else {
    iVar5 = (int)(short)iVar6;
    if (iVar6 + 0x7fff < 0 != (-1 < iVar6 && iVar6 + 0x7fff < 0)) {
      iVar5 = -0x7fff;
    }
  }
  retain_acd8_enable_for_calibrated_release_delay_c75ae();
  sVar3 = abs_s16_wrapping((short)iVar5);
  slew_curve_blend_weight_and_filter_signed_c3e0_c7612((int)sVar3,iVar5);
  update_c3e9_inhibit_envelope_output_and_bound_c78f2((int)sVar3,uVar1);
  return;
}

void interpolate_banked_169c_curve_into_c3cc_c7966(void)

{
  uint32_t puVar1;
  int iVar2;
  
  puVar1 = 0xfebeb800u;
  iVar2 = interpolate_unsigned_axis_sentinel_curve
                    (((ushort *)camry_host_ptr((uint32_t)(0x169cu +
                     (int)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xb144cu + (uint32_t)(DAT_febeac3c & 1) * 4u)))) + (DAT_febec156 & 3) * 0x24)
                     ))),DAT_febeadf6);
  (*((short *)camry_host_ptr((uint32_t)(puVar1 + 0xbcc)))) = (short)iVar2;
  return;
}

void fill_constant_block_c79a0(void)

{
  DAT_febec3ec = 0x400;
  DAT_febec3ee = 0x400;
  DAT_febec3f0 = 0x400;
  DAT_febec3f2 = 0x400;
  DAT_febec3f4 = 0x400;
  return;
}

void prepare_gain_parameters_c3f4(F33GainSlewState *state,uint mode)

{
  int iVar1;
  ushort uVar2;
  uchar uVar3;
  ushort uVar4;
  ushort uVar5;
  ushort uVar6;
  
  if ((mode & 0xff) < 7) {
    uVar3 = '\x02';
    iVar1 = (short)(DAT_febeac3c & 1) * 7 + (mode & 0xff);
    uVar2 = *(ushort *)(((undefined *)camry_host_ptr((uint32_t)(0xd3398u + (uint32_t)(iVar1 * 0x10) * 1u))));
    uVar6 = (*((ushort *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd3394u + (uint32_t)(iVar1 * 4) * 4u)))))));
    uVar5 = (*((volatile ushort *)camry_host_ptr((*((volatile uint32_t *)(((undefined *)camry_host_ptr((uint32_t)(0xd339cu + (uint32_t)(iVar1 * 0x10) * 1u)))))))));
    uVar4 = (*((ushort *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd3390u + (uint32_t)(iVar1 * 4) * 4u)))))));
  }
  else {
    uVar3 = '\x01';
    uVar2 = DAT_febec3ec;
    uVar6 = DAT_febec3f0;
    uVar5 = DAT_febec3f2;
    uVar4 = DAT_febec3ee;
  }
  state->down_step = uVar6;
  state->up_step = uVar5;
  state->down_target = uVar4;
  state->up_target = uVar2;
  state->direction = uVar3;
  return;
}

void prepare_and_step_unsigned_gain_c3f4_c7a18(void)

{
  int iVar1;
  uint32_t puVar2;
  uint uVar3;
  F33GainSlewState local_10;
  
  puVar2 = 0xfebeb800u;
  uVar3 = 7;
  if (DAT_febecab7 == '\x01') {
    uVar3 = (uint)DAT_febecb00;
  }
  local_10.current = DAT_febec3f4;
  if (uVar3 < 7) {
    local_10.direction = '\x02';
    iVar1 = (short)(DAT_febeac3c & 1) * 7 + uVar3;
    local_10.up_target = *(ushort *)(((undefined *)camry_host_ptr((uint32_t)(0xd3398u + (uint32_t)(iVar1 * 0x10) * 1u))));
    local_10.down_step = (*((ushort *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd3394u + (uint32_t)(iVar1 * 4) * 4u)))))));
    local_10.up_step = (*((volatile ushort *)camry_host_ptr((*((volatile uint32_t *)(((undefined *)camry_host_ptr((uint32_t)(0xd339cu + (uint32_t)(iVar1 * 0x10) * 1u)))))))));
    local_10.down_target = (*((ushort *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd3390u + (uint32_t)(iVar1 * 4) * 4u)))))));
  }
  else {
    local_10.direction = '\x01';
    local_10.up_target = DAT_febec3ec;
    local_10.down_step = DAT_febec3f0;
    local_10.up_step = DAT_febec3f2;
    local_10.down_target = DAT_febec3ee;
  }
  step_retained_unsigned_gain(&local_10);
  (*((ushort *)camry_host_ptr((uint32_t)(puVar2 + 0xbf0)))) = local_10.down_step;
  (*((ushort *)camry_host_ptr((uint32_t)(puVar2 + 0xbf2)))) = local_10.up_step;
  (*((ushort *)camry_host_ptr((uint32_t)(puVar2 + 0xbee)))) = local_10.down_target;
  (*((ushort *)camry_host_ptr((uint32_t)(puVar2 + 0xbec)))) = local_10.up_target;
  (*((ushort *)camry_host_ptr((uint32_t)(puVar2 + 0xbf4)))) = local_10.current;
  return;
}

int return_signed_sample_scaled_by_c3f4_gain_c7a60(short param_1)

{
  return (int)(short)((int)((uint)DAT_febec3f4 * (int)param_1) / 0x400);
}

void fill_constant_block_c7a76(void)

{
  DAT_febec41c = 0;
  DAT_febec410 = 0;
  DAT_febec412 = 0;
  DAT_febec414 = 0;
  DAT_febec416 = 0;
  DAT_febec3f8 = 0;
  DAT_febec3fc = 0;
  DAT_febec400 = 0;
  DAT_febec404 = 0;
  DAT_febec408 = 0;
  DAT_febec418 = 0;
  DAT_febec41a = 0;
  DAT_febec40c = 0;
  DAT_febec41e = 0;
  return;
}

void interpolate_and_scale_banked_c412_c416_terms_c7ab0(ushort param_1)

{
  short sVar1;
  uint32_t puVar2;
  undefined2 uVar3;
  int iVar4;
  int iVar5;
  
  sVar1 = ((int)(int16_t)DAT_febec474);
  puVar2 = 0xfebeb800u;
  iVar5 = (DAT_febec156 & 3) * 0x24;
  iVar4 = interpolate_unsigned_axis_sentinel_curve
                    (((ushort *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xb144cu + (uint32_t)(DAT_febeac3c & 1) * 4u)))) + iVar5 + 0x172c))),
                     param_1);
  (*((short *)camry_host_ptr((uint32_t)(puVar2 + 0xc12)))) = (short)iVar4;
  uVar3 = return_signed_sample_scaled_by_c3f4_gain_c7a60((int)(short)(((int)sVar1 * (int)(short)iVar4) / 0x400));
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar2 + 0xc14)))) = uVar3;
  iVar5 = interpolate_unsigned_axis_sentinel_curve
                    (((ushort *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xb144cu + (uint32_t)((byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0xbc4))))) & 1) * 4u)))) + iVar5 + 0x17bc))),param_1
                    );
  (*((short *)camry_host_ptr((uint32_t)(puVar2 + 0xc16)))) = (short)((int)(iVar5 * (uint)(*((ushort *)camry_host_ptr((uint32_t)(puVar2 + -0x9c6))))) / 0x40000);
  return;
}

void refresh_c412_c414_c416_terms_from_adf6_c7b34(void)

{
  interpolate_and_scale_banked_c412_c416_terms_c7ab0(DAT_febeadf6);
  return;
}

void limit_ac90_offset_with_curve_bound_and_filter_c418_c7b44(void)

{
  int iVar1;
  short sVar2;
  uint uVar3;
  int iVar4;
  uint32_t puVar6;
  ushort input;
  int iVar7;
  int iVar8;
  short sVar9;
  int iVar10;
  int iVar5;
  
  iVar5 = DAT_febeac90;
  sVar9 = DAT_000b1200;
  puVar6 = 0xfebeb800u;
  uVar3 = (uint)DAT_febec156;
  iVar10 = (int)DAT_000b1200;
  iVar1 = -DAT_febeac90;
  if (DAT_febec41c == '\0') {
    DAT_febec41c = '\x01';
    DAT_febec400 = iVar1;
  }
  input = abs_s16_wrapping(((int)(int16_t)DAT_febeac44));
  iVar7 = interpolate_unsigned_axis_sentinel_curve
                    (((ushort *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xb144cu + (uint32_t)((byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(-0xbc4))))) & 1) * 4u)))) +
                     (uVar3 & 3) * 0x1c + 0x184c))),input);
  (*((short *)camry_host_ptr((uint32_t)(puVar6 + 0xc10)))) = (short)iVar7;
  iVar8 = (int)(*((short *)camry_host_ptr((uint32_t)(puVar6 + 0xc16))));
  iVar7 = (int)(((int)(*((short *)camry_host_ptr((uint32_t)(puVar6 + 0xc14)))) * (int)(short)iVar7)) / (int)0x400;
  (*((int *)camry_host_ptr((uint32_t)(puVar6 + 0xbf8)))) = iVar7;
  if (iVar8 == 0) {
    (*((undefined4 *)camry_host_ptr((uint32_t)(puVar6 + 0xbfc)))) = 0;
    (*((undefined4 *)camry_host_ptr((uint32_t)(puVar6 + 0xbf8)))) = 0;
    iVar4 = 0;
    iVar7 = 0;
  }
  else {
    iVar4 = (iVar7 << 0x12) / 0x168;
    if (iVar8 != 0) {
      if (iVar4 == -0x80000000 && iVar8 == -1) {
        iVar4 = -0x80000000;
      }
      else {
        iVar4 = (int)iVar4 / (int)iVar8;
      }
    }
    (*((int *)camry_host_ptr((uint32_t)(puVar6 + 0xbfc)))) = iVar4;
  }
  iVar5 = (*((int *)camry_host_ptr((uint32_t)(puVar6 + 0xc00)))) + iVar5;
  (*((int *)camry_host_ptr((uint32_t)(puVar6 + 0xc04)))) = iVar5;
  if (iVar5 - iVar4 < 0 == (iVar5 < 0 != iVar4 < 0 && iVar4 < 0 == iVar5 - iVar4 < 0) &&
      iVar5 != iVar4) {
    (*((int *)camry_host_ptr((uint32_t)(puVar6 + 0xc00)))) = iVar4 + iVar1;
  }
  else if (iVar5 + iVar4 < 0 == (iVar5 < 0 != -iVar4 < 0 && -iVar4 < 0 == iVar5 + iVar4 < 0)) {
    iVar7 = (iVar5 * iVar8 * 0x168) / 0x40000;
  }
  else {
    iVar7 = -iVar7;
    (*((int *)camry_host_ptr((uint32_t)(puVar6 + 0xc00)))) = iVar1 - iVar4;
  }
  (*((int *)camry_host_ptr((uint32_t)(puVar6 + 0xc08)))) = iVar7;
  iVar5 = ((*((int *)camry_host_ptr((uint32_t)(puVar6 + 0xc0c)))) + iVar7) - (int)(*((short *)camry_host_ptr((uint32_t)(puVar6 + 0xc1a))));
  (*((int *)camry_host_ptr((uint32_t)(puVar6 + 0xc0c)))) = iVar5;
  iVar5 = iVar5 * 0x400;
  if (DAT_000b11fc != 0) {
    if (iVar5 == -0x80000000 && DAT_000b11fc == -1) {
      iVar5 = 0;
    }
    else {
      iVar5 = (int)iVar5 / (int)DAT_000b11fc;
    }
  }
  sVar2 = (short)iVar5;
  iVar5 = (int)sVar2;
  (*((short *)camry_host_ptr((uint32_t)(puVar6 + 0xc1a)))) = sVar2;
  if ((iVar5 - iVar10 < 0 != (iVar5 < 0 != iVar10 < 0 && iVar10 < 0 == iVar5 - iVar10 < 0) ||
       iVar5 == iVar10) &&
     (iVar1 = -iVar10, sVar9 = sVar2,
     iVar5 + iVar10 < 0 != (iVar5 < 0 != iVar1 < 0 && iVar1 < 0 == iVar5 + iVar10 < 0) ||
     iVar5 == iVar1)) {
    sVar9 = (short)iVar1;
  }
  (*((short *)camry_host_ptr((uint32_t)(puVar6 + 0xc18)))) = sVar9;
  return;
}

void bound_c418_by_b1200_into_c41e_c7c58(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  
  iVar3 = (int)((int)(int16_t)DAT_febec418);
  iVar2 = (int)DAT_000b1200;
  DAT_febec41e = DAT_000b1200;
  if ((iVar3 - iVar2 < 0 != (iVar3 < 0 != iVar2 < 0 && iVar2 < 0 == iVar3 - iVar2 < 0) ||
       iVar3 == iVar2) &&
     (iVar1 = -iVar2, DAT_febec41e = ((int)(int16_t)DAT_febec418),
     iVar3 + iVar2 < 0 != (iVar3 < 0 != iVar1 < 0 && iVar1 < 0 == iVar3 + iVar2 < 0) ||
     iVar3 == iVar1)) {
    DAT_febec41e = (short)iVar1;
  }
  return;
}

void initialize_three_term_compensation(void)

{
  DAT_febec420 = 0;
  DAT_febec43c = 0;
  DAT_febec424 = 0x400;
  DAT_febec426 = 0x400;
  DAT_febec428 = 0x400;
  DAT_febec42a = 0x400;
  DAT_febec42c = 0x400;
  DAT_febec42e = 0;
  DAT_febec430 = 0x400;
  DAT_febec432 = 0x400;
  DAT_febec434 = 0x400;
  DAT_febec436 = 0x400;
  DAT_febec438 = 0x400;
  DAT_febec43a = 0;
  return;
}

void prepare_gain_parameters_c42c(F33GainSlewState *state,uint mode)

{
  int iVar1;
  ushort uVar2;
  uchar uVar3;
  ushort uVar4;
  ushort uVar5;
  ushort uVar6;
  
  if ((mode & 0xff) < 7) {
    uVar3 = '\x02';
    iVar1 = (short)(DAT_febeac3c & 1) * 7 + (mode & 0xff);
    uVar2 = *(ushort *)(((undefined *)camry_host_ptr((uint32_t)(0xd3478u + (uint32_t)(iVar1 * 0x10) * 1u))));
    uVar6 = (*((ushort *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd3474u + (uint32_t)(iVar1 * 4) * 4u)))))));
    uVar5 = (*((volatile ushort *)camry_host_ptr((*((volatile uint32_t *)(((undefined *)camry_host_ptr((uint32_t)(0xd347cu + (uint32_t)(iVar1 * 0x10) * 1u)))))))));
    uVar4 = (*((ushort *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd3470u + (uint32_t)(iVar1 * 4) * 4u)))))));
  }
  else {
    uVar3 = '\x01';
    uVar2 = DAT_febec424;
    uVar6 = DAT_febec428;
    uVar5 = DAT_febec42a;
    uVar4 = DAT_febec426;
  }
  state->down_step = uVar6;
  state->up_step = uVar5;
  state->down_target = uVar4;
  state->up_target = uVar2;
  state->direction = uVar3;
  return;
}

void prepare_and_step_unsigned_gain_c42c_c7d14(void)

{
  int iVar1;
  uint32_t puVar2;
  uint uVar3;
  F33GainSlewState local_10;
  
  puVar2 = 0xfebeb800u;
  uVar3 = 7;
  if (DAT_febecab7 == '\x01') {
    uVar3 = (uint)DAT_febecb00;
  }
  local_10.current = DAT_febec42c;
  if (uVar3 < 7) {
    local_10.direction = '\x02';
    iVar1 = (short)(DAT_febeac3c & 1) * 7 + uVar3;
    local_10.up_target = *(ushort *)(((undefined *)camry_host_ptr((uint32_t)(0xd3478u + (uint32_t)(iVar1 * 0x10) * 1u))));
    local_10.down_step = (*((ushort *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd3474u + (uint32_t)(iVar1 * 4) * 4u)))))));
    local_10.up_step = (*((volatile ushort *)camry_host_ptr((*((volatile uint32_t *)(((undefined *)camry_host_ptr((uint32_t)(0xd347cu + (uint32_t)(iVar1 * 0x10) * 1u)))))))));
    local_10.down_target = (*((ushort *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd3470u + (uint32_t)(iVar1 * 4) * 4u)))))));
  }
  else {
    local_10.direction = '\x01';
    local_10.up_target = DAT_febec424;
    local_10.down_step = DAT_febec428;
    local_10.up_step = DAT_febec42a;
    local_10.down_target = DAT_febec426;
  }
  step_retained_unsigned_gain(&local_10);
  (*((ushort *)camry_host_ptr((uint32_t)(puVar2 + 0xc28)))) = local_10.down_step;
  (*((ushort *)camry_host_ptr((uint32_t)(puVar2 + 0xc2a)))) = local_10.up_step;
  (*((ushort *)camry_host_ptr((uint32_t)(puVar2 + 0xc26)))) = local_10.down_target;
  (*((ushort *)camry_host_ptr((uint32_t)(puVar2 + 0xc24)))) = local_10.up_target;
  (*((ushort *)camry_host_ptr((uint32_t)(puVar2 + 0xc2c)))) = local_10.current;
  return;
}

short scale_rate_assist_term(short value)

{
  DAT_febec42e = (short)((int)((uint)DAT_febec42c * (int)value) / 0x400);
  return DAT_febec42e;
}

void prepare_gain_parameters_c438(F33GainSlewState *state,uint mode)

{
  int iVar1;
  ushort uVar2;
  uchar uVar3;
  ushort uVar4;
  ushort uVar5;
  ushort uVar6;
  
  if ((mode & 0xff) < 7) {
    uVar3 = '\x02';
    iVar1 = (short)(DAT_febeac3c & 1) * 7 + (mode & 0xff);
    uVar2 = *(ushort *)(((undefined *)camry_host_ptr((uint32_t)(0xd3558u + (uint32_t)(iVar1 * 0x10) * 1u))));
    uVar6 = (*((ushort *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd3554u + (uint32_t)(iVar1 * 4) * 4u)))))));
    uVar5 = (*((volatile ushort *)camry_host_ptr((*((volatile uint32_t *)(((undefined *)camry_host_ptr((uint32_t)(0xd355cu + (uint32_t)(iVar1 * 0x10) * 1u)))))))));
    uVar4 = (*((ushort *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd3550u + (uint32_t)(iVar1 * 4) * 4u)))))));
  }
  else {
    uVar3 = '\x01';
    uVar2 = DAT_febec430;
    uVar6 = DAT_febec434;
    uVar5 = DAT_febec436;
    uVar4 = DAT_febec432;
  }
  state->down_step = uVar6;
  state->up_step = uVar5;
  state->down_target = uVar4;
  state->up_target = uVar2;
  state->direction = uVar3;
  return;
}

void prepare_and_step_unsigned_gain_c438_c7dd4(void)

{
  int iVar1;
  uint32_t puVar2;
  uint uVar3;
  F33GainSlewState local_10;
  
  puVar2 = 0xfebeb800u;
  uVar3 = 7;
  if (DAT_febecab7 == '\x01') {
    uVar3 = (uint)DAT_febecb00;
  }
  local_10.current = DAT_febec438;
  if (uVar3 < 7) {
    local_10.direction = '\x02';
    iVar1 = (short)(DAT_febeac3c & 1) * 7 + uVar3;
    local_10.up_target = *(ushort *)(((undefined *)camry_host_ptr((uint32_t)(0xd3558u + (uint32_t)(iVar1 * 0x10) * 1u))));
    local_10.down_step = (*((ushort *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd3554u + (uint32_t)(iVar1 * 4) * 4u)))))));
    local_10.up_step = (*((volatile ushort *)camry_host_ptr((*((volatile uint32_t *)(((undefined *)camry_host_ptr((uint32_t)(0xd355cu + (uint32_t)(iVar1 * 0x10) * 1u)))))))));
    local_10.down_target = (*((ushort *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd3550u + (uint32_t)(iVar1 * 4) * 4u)))))));
  }
  else {
    local_10.direction = '\x01';
    local_10.up_target = DAT_febec430;
    local_10.down_step = DAT_febec434;
    local_10.up_step = DAT_febec436;
    local_10.down_target = DAT_febec432;
  }
  step_retained_unsigned_gain(&local_10);
  (*((ushort *)camry_host_ptr((uint32_t)(puVar2 + 0xc34)))) = local_10.down_step;
  (*((ushort *)camry_host_ptr((uint32_t)(puVar2 + 0xc36)))) = local_10.up_step;
  (*((ushort *)camry_host_ptr((uint32_t)(puVar2 + 0xc32)))) = local_10.down_target;
  (*((ushort *)camry_host_ptr((uint32_t)(puVar2 + 0xc30)))) = local_10.up_target;
  (*((ushort *)camry_host_ptr((uint32_t)(puVar2 + 0xc38)))) = local_10.current;
  return;
}

uint scale_signed_sample_by_c438_store_and_return_c43a_c7e1c(short param_1)

{
  DAT_febec43a = (short)((int)((uint)DAT_febec438 * (int)param_1) / 0x400);
  return DAT_febec43a;
}

void bound_three_term_compensation(void)

{
  uint uVar1;
  uint uVar2;
  
  uVar2 = (uint)DAT_febeac6c;
  DAT_febec420 = (int)((int)(int16_t)DAT_febec472) + (int)((int)(int16_t)DAT_febec45a) + (int)((int)(int16_t)DAT_febec44c);
  DAT_febec43c = DAT_febeac6c;
  if ((int)(((int)(int32_t)DAT_febec420) - uVar2) < 0 != ((int)DAT_febec420 < 0 && -1 < (int)(((int)(int32_t)DAT_febec420) - uVar2))
      || ((int)(int32_t)DAT_febec420) == uVar2) {
    uVar1 = -uVar2;
    if ((int)(((int)(int32_t)DAT_febec420) + uVar2) < 0 ==
        ((int)DAT_febec420 < 0 != (int)uVar1 < 0 &&
        (int)uVar1 < 0 == (int)(((int)(int32_t)DAT_febec420) + uVar2) < 0) && ((int)(int32_t)DAT_febec420) != uVar1) {
      DAT_febec43c = (ushort)((int)(int32_t)DAT_febec420);
    }
    else {
      DAT_febec43c = (ushort)uVar1;
    }
  }
  return;
}

void initialize_nonlinear_torque_compensation(void)

{
  DAT_febec43e = 0;
  DAT_febec440 = 0;
  DAT_febec442 = 0;
  DAT_febec444 = 0;
  DAT_febec446 = 0;
  DAT_febec44c = 0;
  DAT_febec448 = 0;
  DAT_febec44a = 0;
  DAT_febec44e = 0;
  return;
}

void update_nonlinear_torque_speed_gain(void)

{
  uint32_t puVar1;
  int iVar2;
  
  puVar1 = 0xfebeb800u;
  iVar2 = interpolate_unsigned_axis_sentinel_curve((ushort *)((undefined *)camry_host_ptr(0xafb8eu)),DAT_febeadf6);
  (*((short *)camry_host_ptr((uint32_t)(puVar1 + 0xc3e)))) = (short)iVar2;
  return;
}

ushort update_nonlinear_torque_compensation(void)

{
  int iVar1;
  short sVar2;
  short sVar3;
  uint32_t puVar4;
  ushort uVar5;
  short sVar6;
  short sVar7;
  short sVar9;
  int iVar10;
  uint uVar11;
  int iVar8;
  
  sVar2 = ((int)(int16_t)DAT_febec43e);
  sVar6 = ((int)(int16_t)DAT_febec128);
  sVar7 = ((int)(int16_t)DAT_febeac6e);
  sVar9 = DAT_000afb8c;
  puVar4 = 0xfebeb800u;
  iVar10 = (int)DAT_000afb8c;
  uVar5 = abs_s16_wrapping(((int)(int16_t)DAT_febec128));
  uVar11 = (uint)(uVar5 >> 5);
  if (uVar11 < 0x7f) {
    sVar3 = *(short *)(((undefined *)camry_host_ptr((uint32_t)(0xafba4u + (uint32_t)(uVar11 * 4) * 1u)))) +
            (short)((int)(((int)(short)uVar5 & 0x1fU) *
                         ((int)*(short *)(((undefined *)camry_host_ptr((uint32_t)(0xafba4u + (uint32_t)((uVar11 + 1) * 4) * 1u)))) -
                         (int)*(short *)(((undefined *)camry_host_ptr((uint32_t)(0xafba4u + (uint32_t)(uVar11 * 4) * 1u)))))) / 0x20);
  }
  else {
    sVar3 = 0x130c;
  }
  (*((short *)camry_host_ptr((uint32_t)(puVar4 + 0xc40)))) = sVar3;
  if (sVar6 < 0) {
    sVar3 = -sVar3;
  }
  sVar6 = (short)(((int)sVar2 * (int)sVar3) / 0x400);
  sVar7 = (short)(((int)sVar7 * (int)sVar6) / 0x400);
  iVar8 = (int)sVar7;
  if ((iVar8 - iVar10 < 0 != (iVar8 < 0 != iVar10 < 0 && iVar10 < 0 == iVar8 - iVar10 < 0) ||
       iVar8 == iVar10) &&
     (iVar1 = -iVar10, sVar9 = sVar7,
     iVar8 + iVar10 < 0 != (iVar8 < 0 != iVar1 < 0 && iVar1 < 0 == iVar8 + iVar10 < 0) ||
     iVar8 == iVar1)) {
    sVar9 = (short)iVar1;
  }
  (*((short *)camry_host_ptr((uint32_t)(puVar4 + 0xc42)))) = sVar3;
  (*((short *)camry_host_ptr((uint32_t)(puVar4 + 0xc44)))) = sVar6;
  (*((short *)camry_host_ptr((uint32_t)(puVar4 + 0xc46)))) = sVar7;
  (*((short *)camry_host_ptr((uint32_t)(puVar4 + 0xc4c)))) = sVar9;
  return uVar5;
}

ushort update_nonlinear_torque_slope(void)

{
  char cVar1;
  short sVar2;
  short sVar3;
  short sVar4;
  undefined2 uVar5;
  uint32_t puVar6;
  ushort uVar7;
  
  sVar3 = ((int)(int16_t)DAT_febec43e);
  sVar2 = ((int)(int16_t)DAT_febeac6e);
  cVar1 = DAT_febeac2b;
  puVar6 = 0xfebeb800u;
  uVar7 = abs_s16_wrapping(((int)(int16_t)DAT_febec128));
  sVar4 = 0xa99;
  if (uVar7 >> 5 < 0x7f) {
    sVar4 = *(short *)(((undefined *)camry_host_ptr((uint32_t)(0xafda8u + (uint32_t)((uint)(uVar7 >> 5) * 4) * 1u))));
  }
  (*((short *)camry_host_ptr((uint32_t)(puVar6 + 0xc48)))) = sVar4;
  sVar4 = (short)(((int)sVar3 * (int)sVar4) / 0x400);
  (*((short *)camry_host_ptr((uint32_t)(puVar6 + 0xc4a)))) = sVar4;
  if (cVar1 == 'Z') {
    uVar5 = 0;
  }
  else {
    uVar5 = (undefined2)(((int)sVar2 * (int)sVar4) / 0x400);
  }
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar6 + 0xc4e)))) = uVar5;
  return uVar7;
}

void initialize_angle_rate_compensation(void)

{
  DAT_febec450 = 0;
  DAT_febec452 = 0;
  DAT_febec454 = 0;
  DAT_febec456 = 0;
  DAT_febec458 = 0;
  DAT_febec45a = 0;
  return;
}

void update_angle_rate_compensation_speed_gain(void)

{
  uint32_t puVar1;
  int iVar2;
  
  puVar1 = 0xfebeb800u;
  iVar2 = interpolate_unsigned_axis_sentinel_curve((ushort *)((undefined *)camry_host_ptr(0xaffc4u)),DAT_febeadf6);
  (*((short *)camry_host_ptr((uint32_t)(puVar1 + 0xc50)))) = (short)iVar2;
  return;
}

void update_angle_rate_compensation(void)

{
  int iVar1;
  short sVar2;
  short sVar3;
  short sVar4;
  uint32_t puVar5;
  short sVar6;
  int iVar7;
  short sVar8;
  int iVar9;
  
  sVar2 = ((int)(int16_t)DAT_febec450);
  sVar3 = ((int)(int16_t)DAT_febec172);
  sVar4 = ((int)(int16_t)DAT_febeae4a);
  sVar8 = DAT_000affaa;
  puVar5 = 0xfebeb800u;
  iVar9 = (int)DAT_000affaa;
  sVar6 = abs_s16_wrapping(((int)(int16_t)DAT_febec172));
  iVar7 = interpolate_signed_sentinel_curve((short *)((undefined *)camry_host_ptr(0xaffacu)),sVar6);
  sVar6 = (short)iVar7;
  (*((short *)camry_host_ptr((uint32_t)(puVar5 + 0xc52)))) = sVar6;
  if (sVar3 < 0) {
    sVar6 = -sVar6;
  }
  sVar3 = (short)(((int)sVar2 * (int)sVar6) / 0x400);
  sVar4 = (short)(((int)sVar4 * (int)sVar3) / 0x400);
  iVar7 = (int)sVar4;
  if ((iVar7 - iVar9 < 0 != (iVar7 < 0 != iVar9 < 0 && iVar9 < 0 == iVar7 - iVar9 < 0) ||
       iVar7 == iVar9) &&
     (iVar1 = -iVar9, sVar8 = sVar4,
     iVar7 + iVar9 < 0 != (iVar7 < 0 != iVar1 < 0 && iVar1 < 0 == iVar7 + iVar9 < 0) ||
     iVar7 == iVar1)) {
    sVar8 = (short)iVar1;
  }
  (*((short *)camry_host_ptr((uint32_t)(puVar5 + 0xc54)))) = sVar6;
  (*((short *)camry_host_ptr((uint32_t)(puVar5 + 0xc56)))) = sVar3;
  (*((short *)camry_host_ptr((uint32_t)(puVar5 + 0xc58)))) = sVar4;
  (*((short *)camry_host_ptr((uint32_t)(puVar5 + 0xc5a)))) = sVar8;
  return;
}
