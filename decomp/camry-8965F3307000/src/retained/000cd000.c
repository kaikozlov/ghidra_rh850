#include "common.h"

void update_selected_angle_target(void)

{
  load_mode_c9fe_ca00_or_7ffe_limits_ccecc();
  interpolate_selected_angle_target();
  bound_selected_angle_target();
  return;
}

void filter_ae24_with_previous_sample_q14_cd046(void)

{
  int iVar1;
  
  iVar1 = (int)((int)(int16_t)DAT_febeca0c);
  DAT_febeca0c = ((int)(int16_t)DAT_febeae24);
  DAT_febeca0a = (short)((((0x4000 - (*((short *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xb146cu + (uint32_t)(DAT_febeac3c & 1) * 4u)))) + 0x42))))) / 2)
                         * (iVar1 + ((int)(int16_t)DAT_febeae24))) / 0x4000) +
                 (short)(((int)((int)(int16_t)DAT_febeca0a) *
                         (int)(*((short *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xb146cu + (uint32_t)(DAT_febeac3c & 1) * 4u)))) + 0x42))))) / 0x4000);
  return;
}

void filter_angle_controller_measured_rate(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  
  iVar3 = (int)((int)(int16_t)DAT_febeca36);
  iVar4 = (int)((int)(int16_t)DAT_febec172);
  iVar2 = (int)((int)(int16_t)DAT_febeca82);
  DAT_febec984 = (uint)(*((ushort *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd3ce4u + (uint32_t)((short)((DAT_febecb00 & 7) + (DAT_febeac3c & 1) * 8) * 0x57) * 4u)))))));
  if (((iVar3 == iVar2) || (iVar3 == ((int)(int16_t)DAT_febeca90))) || (iVar2 != ((int)(int16_t)DAT_febeca90))) {
    iVar2 = iVar3;
  }
  iVar3 = (int)DAT_000b05b8;
  DAT_febeca14 = DAT_000b05b8;
  if ((iVar4 - iVar3 < 0 != (iVar4 < 0 != iVar3 < 0 && iVar3 < 0 == iVar4 - iVar3 < 0) ||
       iVar4 == iVar3) &&
     (iVar1 = -iVar3, DAT_febeca14 = ((int)(int16_t)DAT_febec172),
     iVar4 + iVar3 < 0 != (iVar4 < 0 != iVar1 < 0 && iVar1 < 0 == iVar4 + iVar3 < 0) ||
     iVar4 == iVar1)) {
    DAT_febeca14 = (short)iVar1;
  }
  DAT_febeca0e = (short)iVar2;
  DAT_febeca36 = (short)( (int)((iVar2 * (0x100 - (int)DAT_febec984) +
                          (int)(int16_t)DAT_febeca14 * (int)DAT_febec984)) / (int)0x100);
  DAT_febeca82 = ((int)(int16_t)DAT_febeca36);
  DAT_febeca90 = ((int)(int16_t)DAT_febeca36);
  return;
}

void update_angle_error_and_derivative(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  
  if (((DAT_febec8b8 == DAT_febec9a0) || (DAT_febec8b8 == DAT_febec9cc)) ||
     (iVar1 = DAT_febec9a0, DAT_febec9a0 != DAT_febec9cc)) {
    iVar1 = DAT_febec8b8;
  }
  iVar4 = (int)((int)(int16_t)DAT_febecad2);
  iVar2 = (int)((int)(int16_t)DAT_febecad4);
  if (((iVar4 == iVar2) || (iVar4 == ((int)(int16_t)DAT_febecad6))) || (iVar2 != ((int)(int16_t)DAT_febecad6))) {
    iVar2 = iVar4;
  }
  iVar4 = (int)(short)((DAT_febecb00 & 7) + (DAT_febeac3c & 1) * 8);
  iVar1 = (iVar1 * 0xb76) / 0x400;
  DAT_febec8dc = (iVar2 * 0xb76) / 0x400;
  DAT_febec988 = (uint)(*((ushort *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd3ce0u + (uint32_t)(iVar4 * 0x57) * 4u)))))));
  DAT_febec98c = (uint)(*((ushort *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd3ce8u + (uint32_t)(iVar4 * 0x57) * 4u)))))));
  DAT_febec8e0 = iVar1 - DAT_febec8dc;
  iVar3 = (int)DAT_febec8e0;
  iVar4 = (int)DAT_000b05a8;
  if (iVar3 > iVar4) {
    iVar3 = iVar4;
  }
  else if (iVar3 <= -iVar4) {
    iVar3 = -iVar4;
  }
  DAT_febec8e4 = (uint)iVar3;
  DAT_febec90c = (int)((int)(int16_t)DAT_febeca32);
  iVar2 = (int)(DAT_febec90c * (0x100 - DAT_febec988) + DAT_febec8e4 * DAT_febec988) / 0x100;
  if (((DAT_febec910 == DAT_febec9a8) || (DAT_febec910 == DAT_febec9d4)) ||
     (DAT_febec914 = DAT_febec9a8, DAT_febec9a8 != DAT_febec9d4)) {
    DAT_febec914 = DAT_febec910;
  }
  iVar3 = (int)(int16_t)DAT_000b05b6;
  DAT_febec910 = (int)(DAT_febec914 * (0x100 - DAT_febec98c) + DAT_febec8e4 * DAT_febec98c) / 0x100;
  DAT_febec8e8 = (int)(((DAT_febec910 - DAT_febec914) * 0x100)) / (int)0x10;
  iVar4 = (int)DAT_febec8e8;
  if (iVar4 > iVar3) {
    iVar4 = iVar3;
  }
  else if (iVar4 <= -iVar3) {
    iVar4 = -iVar3;
  }
  DAT_febec8d8 = DAT_febec8d4;
  DAT_febec8d4 = iVar1;
  DAT_febeca12 = (undefined2)iVar4;
  DAT_febeca84 = DAT_febeca12;
  DAT_febeca92 = DAT_febeca12;
  if (iVar2 + -0x7fff < 0 == (iVar2 < 0 && -1 < iVar2 + -0x7fff) && iVar2 != 0x7fff) {
    DAT_febeca32 = 0x7fff;
  }
  else {
    DAT_febeca32 = (short)iVar2;
    if (iVar2 + 0x7fff < 0 != (-1 < iVar2 && iVar2 + 0x7fff < 0)) {
      DAT_febeca32 = 0x8001;
    }
  }
  DAT_febec9a8 = DAT_febec910;
  DAT_febec9d4 = DAT_febec910;
  return;
}

int update_angle_target_rate_feedforward(void)

{
  uint uVar1;
  int iVar2;
  int iVar3;
  uint32_t puVar4;
  int iVar5;
  uint uVar6;
  uint uVar7;
  uint uVar8;
  int iVar9;
  
  iVar2 = DAT_febec958;
  iVar9 = DAT_febec950;
  puVar4 = 0xfebeb800u;
  if (((DAT_febec8b8 == DAT_febec9a0) || (DAT_febec8b8 == DAT_febec9cc)) ||
     (iVar3 = DAT_febec9a0, DAT_febec9a0 != DAT_febec9cc)) {
    iVar3 = DAT_febec8b8;
  }
  iVar5 = interpolate_unsigned16_axis_and_values_d0896(((ushort *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd3d04u + (uint32_t)((short)((DAT_febecb00 & 7) + (DAT_febeac3c & 1) * 8) * 0x57) * 4u))))))), DAT_febeae02);
  uVar6 = iVar5 * 10;
  iVar3 = iVar3 * 10;
  uVar1 = iVar3 - iVar9;
  uVar7 = (uint)(*((ushort *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xb1484u + (uint32_t)((byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0xbc4))))) & 1) * 4u)))))));
  if (uVar7 != 0) {
    if (uVar6 == 0x80000000 && uVar7 == 0xffffffff) {
      uVar6 = 0;
    }
    else {
      uVar6 = (int)uVar6 / (int)uVar7;
    }
  }
  uVar8 = uVar6 & 0xffff;
  if ((int)(uVar1 - uVar8) < 0 == ((int)uVar1 < 0 && -1 < (int)(uVar1 - uVar8)) && uVar1 != uVar8) {
    iVar9 = iVar3 - uVar8;
  }
  else if ((int)(uVar1 + uVar8) < 0 !=
           ((int)uVar1 < 0 != (int)-uVar8 < 0 && (int)-uVar8 < 0 == (int)(uVar1 + uVar8) < 0)) {
    iVar9 = uVar8 + iVar3;
  }
  uVar8 = (uint)(*((ushort *)camry_host_ptr((uint32_t)((int)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xb1484u + (uint32_t)((byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0xbc4))))) & 1) * 4u)))) + 2))));
  (*((int *)camry_host_ptr((uint32_t)(puVar4 + 0x1150)))) = iVar9;
  (*((short *)camry_host_ptr((uint32_t)(puVar4 + 0x1248)))) = (short)iVar5;
  iVar9 = (int)((iVar3 - iVar9) * uVar7) / 10;
  (*((uint *)camry_host_ptr((uint32_t)(puVar4 + 0x114c)))) = uVar1;
  (*((short *)camry_host_ptr((uint32_t)(puVar4 + 0x124a)))) = (short)uVar6;
  (*((int *)camry_host_ptr((uint32_t)(puVar4 + 0x1154)))) = iVar9;
  iVar9 = (int)(iVar2 * (0x100 - uVar8)) / 0x100 + iVar9 * uVar8 * 2;
  (*((int *)camry_host_ptr((uint32_t)(puVar4 + 0x1158)))) = iVar9;
  return iVar9;
}

int map_angle_target_feedforward(void)

{
  uint8_t stack_record_18[24];
  undefined2 uVar1;
  int iVar2;
  uint32_t puVar3;
  int iVar4;
  int iVar5;
  int iVar6;
  
  iVar2 = DAT_febec8d4;
  uVar1 = DAT_febeadf6;
  puVar3 = 0xfebeb800u;
  (*((int16_t *)(stack_record_18 + 0))) = 0;
  (*((int16_t *)(stack_record_18 + 2))) = 0;
  iVar4 = abs_s32_wrapping(DAT_febec8d4);
  iVar6 = (int)(short)(((byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(0x1300))))) & 7) + ((byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0xbc4))))) & 1) * 8);
  locate_unsigned16_axis_interval_and_q10_fraction_d097a(((ushort *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd3d34u + (uint32_t)(iVar6 * 0x57) * 4u))))))), uVar1, ((int16_t *)(stack_record_18)), ((int16_t *)((stack_record_18 + 2))));
  iVar5 = interpolate_unsigned32_pairs_with_wide_difference_product_d08e8(((uint *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd3cacu + (uint32_t)(iVar6 * 0x57 + (*((int16_t *)(stack_record_18 + 0))) + 0x18) * 4u))))))), iVar4);
  iVar4 = interpolate_unsigned32_pairs_with_wide_difference_product_d08e8(((uint *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd3cacu + (uint32_t)(iVar6 * 0x57 + (*((int16_t *)(stack_record_18 + 0))) + 0x19) * 4u))))))), iVar4);
  iVar6 = ((iVar4 - iVar5) * (int)(*((int16_t *)(stack_record_18 + 2)))) / 0x400 + iVar5;
  if (iVar2 < 0) {
    iVar6 = -iVar6;
  }
  (*((int *)camry_host_ptr((uint32_t)(0x115au + (int)(puVar3 + 6))))) = iVar6;
  (*((short *)camry_host_ptr((uint32_t)(puVar3 + 0x1268)))) = (*((int16_t *)(stack_record_18 + 2)));
  (*((int *)camry_host_ptr((uint32_t)(puVar3 + 0x1164)))) = iVar5;
  (*((short *)camry_host_ptr((uint32_t)(puVar3 + 0x1266)))) = (*((int16_t *)(stack_record_18 + 0)));
  (*((int *)camry_host_ptr((uint32_t)(puVar3 + 0x1168)))) = iVar4;
  return iVar6;
}

void interpolate_ae02_into_ca10_gain_cd426(void)

{
  uint32_t puVar1;
  int iVar2;
  
  puVar1 = 0xfebeb800u;
  iVar2 = interpolate_unsigned_axis_sentinel_curve
                    (((ushort *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd3d08u + (uint32_t)((short)((DAT_febecb00 & 7) + (DAT_febeac3c & 1) * 8) * 0x57) * 4u)))))),DAT_febeae02);
  (*((short *)camry_host_ptr((uint32_t)(puVar1 + 0x1210)))) = (short)iVar2;
  return;
}

int calculate_angle_target_feedforward(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  uint32_t puVar4;
  uint uVar5;
  uint32_t puVar6;
  
  if (((DAT_febec8b8 == DAT_febec9a0) || (DAT_febec8b8 == DAT_febec9cc)) ||
     (iVar2 = DAT_febec9a0, DAT_febec9a0 != DAT_febec9cc)) {
    iVar2 = DAT_febec8b8;
  }
  iVar1 = (int)((uint)DAT_febeae02 * (int)DAT_000b05b4) / 0x400;
  iVar1 = (iVar1 * iVar1) / 0x80;
  puVar6 = (uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xb146cu + (uint32_t)(DAT_febeac3c & 1) * 4u)))));
  iVar3 = iVar1 << 10;
  iVar1 = (int)(((int)(*((volatile int16_t *)camry_host_ptr((uint32_t)(puVar6 + 0x46)))) * ( (int)(((*((volatile int16_t *)camry_host_ptr((uint32_t)(puVar6 + 0x48)))) * iVar1)) / (int)0x1000 + 0x400))) / (int)0x400;
  if (iVar1 != 0) {
    if (iVar3 == -0x80000000 && iVar1 == -1) {
      iVar3 = 0;
    }
    else {
      iVar3 = (int)iVar3 / (int)iVar1;
    }
  }
  uVar5 = (uint)(*((volatile uint16_t *)camry_host_ptr((uint32_t)(puVar6 + 0x4a))));
  iVar3 = iVar3 << 10;
  if (uVar5 != 0) {
    if (iVar3 == -0x80000000 && uVar5 == 0xffffffff) {
      iVar3 = -0x80000000;
    }
    else {
      iVar3 = iVar3 / (int)uVar5;
    }
  }
  puVar6 = (uint32_t)( (int)(((int)(*((volatile int16_t *)camry_host_ptr((uint32_t)(puVar6 + 0x44)))) * ((iVar3 * iVar2) / 2000))) / (int)0x40);
  puVar4 = (uint32_t)(PTR_DAT_000b05ac);
  if (((int)(puVar6) - (int)PTR_DAT_000b05ac < 0 !=
       ((int)(puVar6) < 0 != (int)PTR_DAT_000b05ac < 0 &&
       (int)PTR_DAT_000b05ac < 0 == (int)(puVar6) - (int)PTR_DAT_000b05ac < 0) ||(puVar6)== PTR_DAT_000b05ac) &&
     (puVar4 = -(int)PTR_DAT_000b05ac,
     (int)((uint32_t)(puVar6 + (int)PTR_DAT_000b05ac)) < 0 ==
     ((int)(puVar6) < 0 != (int)(puVar4) < 0 &&
     (int)(puVar4) < 0 == (int)((uint32_t)(puVar6 + (int)PTR_DAT_000b05ac)) < 0) &&(uintptr_t)(puVar6)!=(uintptr_t)(puVar4))) {
    puVar4 = puVar6;
  }
  puVar6 = (uint32_t)((int)((int)(puVar4) * (uint)DAT_febeca10) / 0x100);
  DAT_febec95c = PTR_DAT_000b05ac;
  if (((int)(puVar6) - (int)PTR_DAT_000b05ac < 0 !=
       ((int)(puVar6) < 0 != (int)PTR_DAT_000b05ac < 0 &&
       (int)PTR_DAT_000b05ac < 0 == (int)(puVar6) - (int)PTR_DAT_000b05ac < 0) ||(puVar6)== PTR_DAT_000b05ac) &&
     (DAT_febec95c = ((uint32_t)(-(int)PTR_DAT_000b05ac)),
     (int)((uint32_t)(puVar6 + (int)PTR_DAT_000b05ac)) < 0 ==
     ((int)(puVar6) < 0 != (int)DAT_febec95c < 0 &&
     (int)DAT_febec95c < 0 == (int)((uint32_t)(puVar6 + (int)PTR_DAT_000b05ac)) < 0) &&(puVar6)!= ((int)(int32_t)DAT_febec95c)))
  {
    DAT_febec95c = (puVar6);
  }
  return (int)DAT_febec95c;
}

uint32_t compose_rate_feedforward_and_mode_curve_term_cd538(void)

{
  uint32_t camry_r10_result;
  char cVar1;
  uint32_t puVar2;
  int iVar3;
  int iVar4;
  
  puVar2 = 0xfebeb800u;
  cVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd3cecu + (uint32_t)((short)((DAT_febecb00 & 7) + (DAT_febeac3c & 1) * 8) * 0x57) * 4u))))))));
  iVar3 = (camry_r10_result = update_angle_target_rate_feedforward());
  if (cVar1 == 'Z') {
    iVar4 = (camry_r10_result = map_angle_target_feedforward());
  }
  else {
    interpolate_ae02_into_ca10_gain_cd426();
    iVar4 = (camry_r10_result = calculate_angle_target_feedforward());
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(0x12a0))))) = cVar1;
  (*((int *)camry_host_ptr((uint32_t)(puVar2 + 0x112c)))) = iVar3 / 0x200 + iVar4;
  return camry_r10_result;
}

void interpolate_ae02_into_ca16_ca30_ca1c_cd590(void)

{
  ushort input;
  uint32_t puVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  
  input = DAT_febeae02;
  puVar1 = 0xfebeb800u;
  iVar4 = (int)(short)((DAT_febecb00 & 7) + (DAT_febeac3c & 1) * 8);
  iVar2 = interpolate_unsigned_axis_sentinel_curve
                    (((ushort *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd3d38u + (uint32_t)(iVar4 * 0x57) * 4u)))))),DAT_febeae02);
  iVar3 = interpolate_unsigned_axis_sentinel_curve
                    (((ushort *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd3d44u + (uint32_t)(iVar4 * 0x57) * 4u)))))),input);
  iVar4 = interpolate_unsigned_axis_sentinel_curve
                    (((ushort *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd3d48u + (uint32_t)(iVar4 * 0x57) * 4u)))))),input);
  (*((short *)camry_host_ptr((uint32_t)(puVar1 + 0x1216)))) = (short)iVar2;
  (*((short *)camry_host_ptr((uint32_t)(puVar1 + 0x1230)))) = (short)iVar3;
  (*((short *)camry_host_ptr((uint32_t)(0x121au + (int)(puVar1 + 2))))) = (short)iVar4;
  return;
}

undefined2 map_abs_ca32_bf40_and_load_ca18_ca1a_cd5ea(void)

{
  int iVar1;
  undefined2 uVar2;
  undefined2 uVar3;
  uint32_t puVar4;
  short sVar5;
  undefined2 uVar6;
  undefined2 uVar7;
  uint uVar8;
  
  puVar4 = 0xfebeb800u;
  iVar1 = (int)(short)((DAT_febecb00 & 7) + (DAT_febeac3c & 1) * 8);
  uVar8 = abs_s32_wrapping((int)((int)(int16_t)DAT_febeca32));
  if ((int)(uVar8 - 0xffff) < 0 == ((int)uVar8 < 0 && -1 < (int)(uVar8 - 0xffff))) {
    uVar8 = 0xffff;
  }
  sVar5 = abs_s16_wrapping((*((short *)camry_host_ptr((uint32_t)(puVar4 + 0x740)))));
  uVar6 = interpolate_unsigned16_axis_and_values_d0896(((ushort *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd3d3cu + (uint32_t)(iVar1 * 0x57) * 4u))))))), uVar8 & 0xffff);
  uVar7 = interpolate_signed16_axis_unsigned16_values_d07f2(((short *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd3d40u + (uint32_t)(iVar1 * 0x57) * 4u))))))), (int)sVar5);
  uVar2 = (*((undefined2 *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd3cd0u + (uint32_t)(iVar1 * 0x57) * 4u)))))));
  uVar3 = (*((undefined2 *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd3cd4u + (uint32_t)(iVar1 * 0x57) * 4u)))))));
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar4 + 0x1204)))) = uVar6;
  (*((undefined2 *)camry_host_ptr((uint32_t)(0x1206u + (int)puVar4)))) = uVar7;
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar4 + 0x1218)))) = uVar2;
  (*((undefined2 *)camry_host_ptr((uint32_t)(0x121au + (int)puVar4)))) = uVar3;
  return uVar7;
}

void interpolate_ca32_magnitude_across_adf6_curves_cd662(void)

{
  uint8_t stack_record_20[32];
  undefined1 uVar1;
  ushort uVar2;
  undefined2 uVar3;
  int iVar4;
  uint32_t puVar5;
  uint uVar6;
  int iVar7;
  int iVar8;
  int value;
  
  uVar3 = DAT_febeadf6;
  puVar5 = 0xfebeb800u;
  value = (int)((int)(int16_t)DAT_febeca32);
  (*((int16_t *)(stack_record_20 + 0))) = 0;
  (*((int16_t *)(stack_record_20 + 2))) = 0;
  iVar4 = (int)(short)((DAT_febecb00 & 7) + (DAT_febeac3c & 1) * 8);
  uVar6 = abs_s32_wrapping(value);
  if ((int)(uVar6 - 0xffff) < 0 == ((int)uVar6 < 0 && -1 < (int)(uVar6 - 0xffff))) {
    uVar6 = 0xffff;
  }
  uVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd3cf0u + (uint32_t)(iVar4 * 0x57) * 4u))))))));
  uVar2 = (*((ushort *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd3cf4u + (uint32_t)(iVar4 * 0x57) * 4u)))))));
  locate_unsigned16_axis_interval_and_q10_fraction_d097a(((ushort *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd3d74u + (uint32_t)(iVar4 * 0x57) * 4u))))))), uVar3, ((int16_t *)(stack_record_20)), ((int16_t *)((stack_record_20 + 2))));
  iVar7 = interpolate_unsigned16_axis_and_values_d0896(((ushort *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd3cacu + (uint32_t)(iVar4 * 0x57 + (*((int16_t *)(stack_record_20 + 0))) + 0x28) * 4u))))))), uVar6 & 0xffff);
  iVar8 = interpolate_unsigned16_axis_and_values_d0896(((ushort *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd3cacu + (uint32_t)(iVar4 * 0x57 + (*((int16_t *)(stack_record_20 + 0))) + 0x29) * 4u))))))), uVar6 & 0xffff);
  iVar4 = ((iVar8 - iVar7) * (int)(*((int16_t *)(stack_record_20 + 2)))) / 0x400 + iVar7;
  if (value < 0) {
    iVar4 = -iVar4;
  }
  (*((int *)camry_host_ptr((uint32_t)(puVar5 + 0x1170)))) = iVar4;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(0x12a1))))) = uVar1;
  (*((uint *)camry_host_ptr((uint32_t)(puVar5 + 0x116c)))) = (uint)uVar2;
  (*((short *)camry_host_ptr((uint32_t)(puVar5 + 0x126c)))) = (*((int16_t *)(stack_record_20 + 2)));
  (*((short *)camry_host_ptr((uint32_t)(puVar5 + 0x126a)))) = (*((int16_t *)(stack_record_20 + 0)));
  (*((short *)camry_host_ptr((uint32_t)(puVar5 + 0x126e)))) = (short)iVar7;
  (*((short *)camry_host_ptr((uint32_t)(puVar5 + 0x1270)))) = (short)iVar8;
  return;
}

void blend_ca12_c8bc_then_interpolate_adf6_surface_cd724(void)

{
  uint8_t stack_record_28[40];
  undefined1 uVar1;
  ushort uVar2;
  undefined2 uVar3;
  int iVar4;
  int iVar5;
  uint32_t puVar6;
  uint uVar7;
  int iVar8;
  int iVar9;
  int iVar10;
  uint uVar11;
  
  uVar3 = DAT_febeadf6;
  puVar6 = 0xfebeb800u;
  (*((int16_t *)(stack_record_28 + 0))) = 0;
  (*((int16_t *)(stack_record_28 + 2))) = 0;
  iVar5 = (int)(short)((DAT_febecb00 & 7) + (DAT_febeac3c & 1) * 8);
  iVar10 = (int)((int)(int16_t)DAT_febeca12);
  iVar4 = (int)((int)(int16_t)DAT_febeca84);
  if (((iVar10 == iVar4) || (iVar10 == ((int)(int16_t)DAT_febeca92))) || (iVar4 != ((int)(int16_t)DAT_febeca92))) {
    iVar4 = iVar10;
  }
  if (((DAT_febec8bc == DAT_febec9a4) || (DAT_febec8bc == DAT_febec9d0)) ||
     (iVar10 = DAT_febec9a4, DAT_febec9a4 != DAT_febec9d0)) {
    iVar10 = DAT_febec8bc;
  }
  uVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd3cf8u + (uint32_t)(iVar5 * 0x57) * 4u))))))));
  uVar11 = (uint)(*((ushort *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd3cccu + (uint32_t)(iVar5 * 0x57) * 4u)))))));
  uVar2 = (*((ushort *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd3cfcu + (uint32_t)(iVar5 * 0x57) * 4u)))))));
  iVar4 = (int)(iVar10 * (0x100 - uVar11) + iVar4 * uVar11) / 0x100;
  uVar7 = abs_s32_wrapping(iVar4);
  if ((int)(uVar7 - 0xffff) < 0 == ((int)uVar7 < 0 && -1 < (int)(uVar7 - 0xffff))) {
    uVar7 = 0xffff;
  }
  locate_unsigned16_axis_interval_and_q10_fraction_d097a(((ushort *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd3da0u + (uint32_t)(iVar5 * 0x57) * 4u))))))), uVar3, ((int16_t *)(stack_record_28)), ((int16_t *)((stack_record_28 + 2))));
  iVar8 = interpolate_unsigned16_axis_and_values_d0896(((ushort *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd3cacu + (uint32_t)(iVar5 * 0x57 + (*((int16_t *)(stack_record_28 + 0))) + 0x33) * 4u))))))), uVar7 & 0xffff);
  iVar9 = interpolate_unsigned16_axis_and_values_d0896(((ushort *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd3cacu + (uint32_t)(iVar5 * 0x57 + (*((int16_t *)(stack_record_28 + 0))) + 0x34) * 4u))))))), uVar7 & 0xffff);
  iVar5 = ((iVar9 - iVar8) * (int)(*((int16_t *)(stack_record_28 + 2)))) / 0x400 + iVar8;
  if (iVar4 < 0) {
    iVar5 = -iVar5;
  }
  (*((int *)camry_host_ptr((uint32_t)(puVar6 + 0x117c)))) = iVar5;
  (*((int *)camry_host_ptr((uint32_t)(puVar6 + 0x10bc)))) = iVar4;
  (*((int *)camry_host_ptr((uint32_t)(0x119eu + (int)(puVar6 + 6))))) = iVar4;
  (*((int *)camry_host_ptr((uint32_t)(puVar6 + 0x11d0)))) = iVar4;
  (*((int *)camry_host_ptr((uint32_t)(puVar6 + 0x10c0)))) = iVar10;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(0x12a2))))) = uVar1;
  (*((uint *)camry_host_ptr((uint32_t)(puVar6 + 0x1174)))) = uVar11;
  (*((uint *)camry_host_ptr((uint32_t)(puVar6 + 0x1178)))) = (uint)uVar2;
  (*((short *)camry_host_ptr((uint32_t)(puVar6 + 0x1272)))) = (*((int16_t *)(stack_record_28 + 0)));
  (*((short *)camry_host_ptr((uint32_t)(puVar6 + 0x1274)))) = (*((int16_t *)(stack_record_28 + 2)));
  (*((short *)camry_host_ptr((uint32_t)(puVar6 + 0x1276)))) = (short)iVar8;
  (*((short *)camry_host_ptr((uint32_t)(puVar6 + 0x1278)))) = (short)iVar9;
  return;
}

void load_mode_gain_into_c980_cd84e(void)

{
  DAT_febec980 = (uint)(*((ushort *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd3d00u + (uint32_t)((short)((DAT_febecb00 & 7) + (DAT_febeac3c & 1) * 8) * 0x57) * 4u)))))));
  return;
}

void update_two_adf6_surfaces_and_c980_gain_cd878(void)

{
  interpolate_ca32_magnitude_across_adf6_curves_cd662();
  blend_ca12_c8bc_then_interpolate_adf6_surface_cd724();
  load_mode_gain_into_c980_cd84e();
  return;
}

void vote_and_blend_c8f0_toward_c970_q8_cd88c(void)

{
  if (((DAT_febec8f0 == DAT_febec9ac) || (DAT_febec8f0 == DAT_febec9d8)) ||
     (DAT_febec9ac != DAT_febec9d8)) {
    DAT_febec9ac = DAT_febec8f0;
  }
  DAT_febec8f4 = DAT_febec970;
  DAT_febec8f8 = DAT_febec9ac;
  DAT_febec8f0 = (uint)((int)(DAT_febec9ac * (0x100 - DAT_febec96c) + DAT_febec970 * DAT_febec96c) / 0x100);
  DAT_febec9ac = DAT_febec8f0;
  DAT_febec9d8 = DAT_febec8f0;
  return;
}

int select_ca18_ca1a_gain_by_magnitude_trend_cd8e0(void)

{
  int iVar1;
  uint32_t puVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  int iVar6;
  
  puVar2 = 0xfebeb800u;
  iVar4 = (int)((int)(int16_t)DAT_febeca1e);
  iVar1 = (int)((int)(int16_t)DAT_febeca86);
  iVar6 = (int)((int)(int16_t)DAT_febeca18);
  iVar5 = (int)((int)(int16_t)DAT_febeca1a);
  if (((iVar4 == iVar1) || (iVar4 == ((int)(int16_t)DAT_febeca94))) || (iVar1 != ((int)(int16_t)DAT_febeca94))) {
    iVar1 = iVar4;
  }
  iVar4 = abs_s32_wrapping(DAT_febec8d4);
  iVar3 = abs_s32_wrapping((*((int *)camry_host_ptr((uint32_t)(puVar2 + 0x10d8)))));
  if ((iVar4 - iVar3 < 0 || iVar4 == iVar3) && (iVar6 = iVar1, iVar4 - iVar3 < 0)) {
    iVar6 = iVar5;
  }
  (*((short *)camry_host_ptr((uint32_t)(0x1206u + (int)(puVar2 + 2))))) = (short)iVar1;
  return iVar6;
}

int compose_ca32_gain_term_and_blend_c8f0_cd932(void)

{
  int iVar1;
  byte bVar2;
  byte bVar3;
  int iVar4;
  ushort uVar5;
  ushort uVar6;
  int iVar7;
  uint32_t puVar8;
  undefined2 uVar9;
  int iVar10;
  int iVar11;
  int iVar12;
  uint uVar13;
  byte bVar14;
  
  uVar6 = DAT_febeca06;
  uVar5 = DAT_febeca04;
  iVar4 = DAT_febec96c;
  iVar11 = DAT_febec8e4;
  puVar8 = 0xfebeb800u;
  uVar13 = (uint)DAT_febeca16;
  bVar2 = DAT_febecb00 & 7;
  bVar3 = DAT_febecb00 & 7;
  bVar14 = DAT_febecb00 & 7;
  iVar12 = (int)((int)(int16_t)DAT_febeca32);
  if (((DAT_febec8f0 == DAT_febec9ac) || (DAT_febec8f0 == DAT_febec9d8)) ||
     (iVar7 = DAT_febec9ac, DAT_febec9ac != DAT_febec9d8)) {
    iVar7 = DAT_febec8f0;
  }
  iVar10 = select_ca18_ca1a_gain_by_magnitude_trend_cd8e0();
  iVar1 = iVar10 + uVar13;
  if (bVar2 == 0) {
    iVar11 = iVar11 * iVar1;
  }
  else {
    uVar13 = (uint)uVar5 * (uint)uVar6 >> 10;
    if (0x27ff < uVar13) {
      uVar13 = 0x2800;
    }
    uVar13 = uVar13 * iVar1 >> 10;
    if (0x8f5b < uVar13) {
      uVar13 = 0x8f5c;
    }
    iVar11 = uVar13 * iVar12;
  }
  iVar11 = iVar11 / 0x200;
  iVar12 = iVar11;
  if ((bVar3 != 0) && (iVar12 = iVar7, bVar14 != 7)) {
    iVar12 = (iVar7 * (0x100 - iVar4) + iVar11 * iVar4) / 0x100;
  }
  uVar9 = (undefined2)iVar10;
  (*((undefined2 *)camry_host_ptr((uint32_t)(0x121au + (int)(puVar8 + 4))))) = uVar9;
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar8 + 0x1286)))) = uVar9;
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar8 + 0x1294)))) = uVar9;
  (*((int *)camry_host_ptr((uint32_t)(puVar8 + 0x10ec)))) = iVar1;
  (*((int *)camry_host_ptr((uint32_t)(puVar8 + 0x10f0)))) = iVar12;
  (*((int *)camry_host_ptr((uint32_t)(puVar8 + 0x11ac)))) = iVar12;
  (*((int *)camry_host_ptr((uint32_t)(puVar8 + 0x11d8)))) = iVar12;
  (*((int *)camry_host_ptr((uint32_t)(puVar8 + 0x10f4)))) = iVar11;
  (*((int *)camry_host_ptr((uint32_t)(puVar8 + 0x10f8)))) = iVar7;
  return iVar10;
}

void dispatch_c8f0_curve_or_gain_composition_cda04(void)

{
  if (DAT_febecaa1 == 'Z') {
    vote_and_blend_c8f0_toward_c970_q8_cd88c();
  }
  else {
    compose_ca32_gain_term_and_blend_c8f0_cd932();
  }
  return;
}

void update_angle_error_integral(void)

{
  uint uVar1;
  uint32_t puVar2;
  int iVar3;
  int iVar4;
  int local_c;
  
  puVar2 = 0xfebeb800u;
  local_c = DAT_febec91c;
  uVar1 = DAT_febecb00 & 7;
  if (((DAT_febec924 == DAT_febec9b0) || (DAT_febec924 == DAT_febec9dc)) ||
     (DAT_febec918 = DAT_febec9b0, DAT_febec9b0 != DAT_febec9dc)) {
    DAT_febec918 = DAT_febec924;
  }
  if ((DAT_febecb00 & 7) == 0) {
    local_c = 0;
  }
  else if (uVar1 == 7) {
    local_c = 0;
    uVar1 = 0;
  }
  else {
    uVar1 = (int)((int)((int)(int16_t)DAT_febeca32) * (uint)DAT_febeca30) / 0x10;
    if (((DAT_febeadbb != '\x01') && ((DAT_febeca9b != '\x02' || ((int)uVar1 < 0)))) &&
       ((DAT_febeca9b != '\x01' || (-1 < (int)uVar1)))) {
      puVar2 = 0xfebeb800u;
      store_symmetric_saturated_signed32_sum_d0a06(DAT_febec918,uVar1,&local_c);
    }
  }
  iVar3 = (*((int *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xb146cu + (uint32_t)((byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0xbc4))))) & 1) * 4u)))) + 0xac))));
  iVar4 = iVar3;
  if ((local_c - iVar3 < 0 != (local_c < 0 != iVar3 < 0 && iVar3 < 0 == local_c - iVar3 < 0) ||
       local_c == iVar3) &&
     (iVar4 = -iVar3,
     local_c + iVar3 < 0 == (local_c < 0 != iVar4 < 0 && iVar4 < 0 == local_c + iVar3 < 0) &&
     local_c != iVar4)) {
    iVar4 = local_c;
  }
  (*((uint *)camry_host_ptr((uint32_t)(puVar2 + 0x1120)))) = uVar1;
  (*((int *)camry_host_ptr((uint32_t)(puVar2 + 0x111c)))) = local_c;
  (*((int *)camry_host_ptr((uint32_t)(puVar2 + 0x1124)))) = iVar4;
  (*((int *)camry_host_ptr((uint32_t)(puVar2 + 0x11b0)))) = iVar4;
  (*((int *)camry_host_ptr((uint32_t)(puVar2 + 0x11dc)))) = iVar4;
  return;
}

void vote_and_blend_c8fc_toward_c97c_by_mode_cdae0(void)

{
  undefined1 uVar1;
  undefined1 uVar2;
  
  if (((DAT_febec8fc == DAT_febec9b4) || (DAT_febec8fc == DAT_febec9e0)) ||
     (DAT_febec9b4 != DAT_febec9e0)) {
    DAT_febec9b4 = DAT_febec8fc;
  }
  if ((DAT_febecb00 & 7) == 0) {
    uVar2 = 1;
    uVar1 = 1;
    if (DAT_febeca98 != '\x01') {
      DAT_febec8c4 = 0;
      goto LAB_000cdb26;
    }
  }
  else {
    uVar2 = 0;
    DAT_febec8c4 = DAT_febec9b4;
    uVar1 = 0;
    if ((DAT_febecb00 & 7) == 7) goto LAB_000cdb26;
  }
  uVar2 = uVar1;
  DAT_febec8c4 = DAT_febec97c;
LAB_000cdb26:
  DAT_febeca98 = uVar2;
  DAT_febec8c8 = DAT_febec9b4;
  DAT_febec8fc = (uint)((int)(DAT_febec9b4 * (0x100 - DAT_febec978) + DAT_febec8c4 * DAT_febec978) / 0x100);
  DAT_febec9b4 = DAT_febec8fc;
  DAT_febec9e0 = DAT_febec8fc;
  return;
}

void compose_ca1c_scaled_triplicate_c8fc_cdb5c(void)

{
  uint uVar1;
  int iVar2;
  int iVar3;
  
  iVar2 = (int)((int)(int16_t)DAT_febeca12);
  iVar3 = (int)((int)(int16_t)DAT_febeca84);
  uVar1 = DAT_febecb00 & 7;
  if (((iVar2 == iVar3) || (iVar2 == ((int)(int16_t)DAT_febeca92))) || (iVar3 != ((int)(int16_t)DAT_febeca92))) {
    iVar3 = iVar2;
  }
  if (((DAT_febec8fc == DAT_febec9b4) || (DAT_febec8fc == DAT_febec9e0)) ||
     (DAT_febec9b4 != DAT_febec9e0)) {
    DAT_febec9b4 = DAT_febec8fc;
  }
  if (((DAT_febec8bc == DAT_febec9a4) || (DAT_febec8bc == DAT_febec9d0)) ||
     (iVar2 = DAT_febec9a4, DAT_febec9a4 != DAT_febec9d0)) {
    iVar2 = DAT_febec8bc;
  }
  if ((DAT_febecb00 & 7) == 0) {
    if (DAT_febeca98 != '\x01') {
      DAT_febec8c8 = DAT_febec9b4;
      DAT_febec8fc = uVar1;
      DAT_febec9b4 = uVar1;
      DAT_febec9e0 = uVar1;
      DAT_febeca98 = 1;
      return;
    }
    iVar2 = 0x40;
    DAT_febec8fc = (uint)DAT_febeca1c * iVar3;
    DAT_febeca98 = 1;
  }
  else {
    DAT_febeca98 = 0;
    DAT_febec8c4 = DAT_febec9b4;
    if (uVar1 != 7) {
      DAT_febec8c4 = (int)((uint)DAT_febeca1c * iVar2) / 0x40;
    }
    DAT_febec8fc = DAT_febec9b4 * (0x100 - DAT_febec978) + DAT_febec8c4 * DAT_febec978;
    iVar2 = 0x100;
  }
  if (iVar2 != 0) {
    if (DAT_febec8fc == -0x80000000 && iVar2 == -1) {
      DAT_febec8fc = -0x80000000;
    }
    else {
      DAT_febec8fc = (int)DAT_febec8fc / iVar2;
    }
  }
  DAT_febec8c8 = DAT_febec9b4;
  DAT_febec9b4 = DAT_febec8fc;
  DAT_febec9e0 = DAT_febec8fc;
  return;
}

void dispatch_c8fc_curve_or_gain_composition_cdc2c(void)

{
  if (DAT_febecaa2 == 'Z') {
    vote_and_blend_c8fc_toward_c97c_by_mode_cdae0();
  }
  else {
    compose_ca1c_scaled_triplicate_c8fc_cdb5c();
  }
  return;
}

void compose_filtered_angle_error_feedback(void)

{
  uint32_t puVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  
  if (((DAT_febec924 == DAT_febec9b0) || (DAT_febec924 == DAT_febec9dc)) ||
     (iVar2 = DAT_febec9b0, DAT_febec9b0 != DAT_febec9dc)) {
    iVar2 = DAT_febec924;
  }
  if (((DAT_febec900 == DAT_febec990) || (DAT_febec900 == DAT_febec9bc)) ||
     (DAT_febec8d0 = DAT_febec990, DAT_febec990 != DAT_febec9bc)) {
    DAT_febec8d0 = DAT_febec900;
  }
  if (((DAT_febec8f0 == DAT_febec9ac) || (DAT_febec8f0 == DAT_febec9d8)) ||
     (iVar3 = DAT_febec9ac, DAT_febec9ac != DAT_febec9d8)) {
    iVar3 = DAT_febec8f0;
  }
  if (((DAT_febec8fc == DAT_febec9b4) || (DAT_febec8fc == DAT_febec9e0)) ||
     (iVar4 = DAT_febec9b4, DAT_febec9b4 != DAT_febec9e0)) {
    iVar4 = DAT_febec8fc;
  }
  puVar1 = (iVar4 + iVar2 / 0x200 + iVar3);
  DAT_febec8cc = PTR_DAT_000b05ac;
  if (((int)puVar1 - (int)PTR_DAT_000b05ac < 0 !=
       ((int)puVar1 < 0 != (int)PTR_DAT_000b05ac < 0 &&
       (int)PTR_DAT_000b05ac < 0 == (int)puVar1 - (int)PTR_DAT_000b05ac < 0) ||
       puVar1 == PTR_DAT_000b05ac) &&
     (DAT_febec8cc = ((uint32_t)(-(int)PTR_DAT_000b05ac)),
     (int)(puVar1 + (int)PTR_DAT_000b05ac) < 0 ==
     ((int)puVar1 < 0 != (int)DAT_febec8cc < 0 &&
     (int)DAT_febec8cc < 0 == (int)(puVar1 + (int)PTR_DAT_000b05ac) < 0) && puVar1 != ((int)(int32_t)DAT_febec8cc)))
  {
    DAT_febec8cc = puVar1;
  }
  DAT_febec900 = DAT_febec8d0;
  if ((DAT_febecb00 & 7) != 7) {
    DAT_febec900 = (int)((DAT_febec8d0 * (0x100 - DAT_febec980) + (int)DAT_febec8cc * DAT_febec980)) / (int)0x100;
  }
  DAT_febec990 = DAT_febec900;
  DAT_febec9bc = DAT_febec900;
  return;
}

void run_init_chain_cdd1e(void)

{
  interpolate_ae02_into_ca16_ca30_ca1c_cd590();
  map_abs_ca32_bf40_and_load_ca18_ca1a_cd5ea();
  update_two_adf6_surfaces_and_c980_gain_cd878();
  dispatch_c8f0_curve_or_gain_composition_cda04();
  update_angle_error_integral();
  dispatch_c8fc_curve_or_gain_composition_cdc2c();
  compose_filtered_angle_error_feedback();
  return;
}

void debounce_ca0a_negative_hysteresis_into_ca99_cdd42(void)

{
  int iVar1;
  bool bVar2;
  int iVar3;
  int iVar4;
  
  iVar4 = (int)((int)(int16_t)DAT_febeca0a);
  if (DAT_febeca99 == '\0') {
    iVar1 = iVar4 + DAT_000b05ba;
    bVar2 = -(int)DAT_000b05ba < 0;
    if (iVar1 < 0 == (iVar4 < 0 != bVar2 && bVar2 == iVar1 < 0)) {
      DAT_febeca20 = 0;
    }
    else {
      DAT_febeca20 = DAT_febeca20 + 1;
      DAT_febeca99 = DAT_000b05bc <= DAT_febeca20;
      if ((bool)DAT_febeca99) {
        DAT_febeca20 = 0;
      }
    }
  }
  else {
    iVar3 = -(int)DAT_000b05be;
    iVar1 = iVar4 + DAT_000b05be;
    if (iVar1 < 0 == (iVar4 < 0 != iVar3 < 0 && iVar3 < 0 == iVar1 < 0) && iVar4 != iVar3) {
      DAT_febeca22 = DAT_febeca22 + 1;
      if (DAT_000b05c0 <= DAT_febeca22) {
        DAT_febeca99 = '\0';
        DAT_febeca22 = 0;
      }
    }
    else {
      DAT_febeca22 = 0;
    }
  }
  return;
}

void debounce_ca0a_positive_hysteresis_into_ca9a_cddb6(void)

{
  int iVar1;
  int iVar2;
  
  iVar2 = (int)((int)(int16_t)DAT_febeca0a);
  if (DAT_febeca9a == '\0') {
    iVar1 = (int)DAT_000b05ba;
    if (iVar2 - iVar1 < 0 == (iVar2 < 0 != iVar1 < 0 && iVar1 < 0 == iVar2 - iVar1 < 0) &&
        iVar2 != iVar1) {
      DAT_febeca24 = DAT_febeca24 + 1;
      DAT_febeca9a = DAT_000b05bc <= DAT_febeca24;
      if ((bool)DAT_febeca9a) {
        DAT_febeca24 = 0;
      }
    }
    else {
      DAT_febeca24 = 0;
    }
  }
  else {
    iVar1 = (int)DAT_000b05be;
    if (iVar2 - iVar1 < 0 == (iVar2 < 0 != iVar1 < 0 && iVar1 < 0 == iVar2 - iVar1 < 0)) {
      DAT_febeca26 = 0;
    }
    else {
      DAT_febeca26 = DAT_febeca26 + 1;
      if (DAT_000b05c0 <= DAT_febeca26) {
        DAT_febeca9a = '\0';
        DAT_febeca26 = 0;
      }
    }
  }
  return;
}

void update_ca54_ca0a_deadband_by_curve_product_cde26(void)

{
  undefined2 uVar1;
  short sVar2;
  short sVar3;
  uint32_t puVar4;
  short sVar5;
  int iVar6;
  int iVar7;
  int iVar8;
  short sVar9;
  int iVar10;
  
  sVar2 = ((int)(int16_t)DAT_febeca0a);
  puVar4 = 0xfebeb800u;
  sVar5 = abs_s16_wrapping(((int)(int16_t)DAT_febeca0a));
  uVar1 = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar4 + -0x9fe))));
  sVar3 = (*((short *)camry_host_ptr((uint32_t)(puVar4 + 0x1254))));
  iVar7 = (int)(short)(((byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(0x1300))))) & 7) + ((byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0xbc4))))) & 1) * 8);
  iVar6 = interpolate_unsigned16_axis_and_values_d0896(((ushort *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd3da4u + (uint32_t)(iVar7 * 0x57) * 4u))))))), sVar5);
  iVar7 = interpolate_unsigned16_axis_and_values_d0896(((ushort *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd3da8u + (uint32_t)(iVar7 * 0x57) * 4u))))))), uVar1);
  sVar9 = sVar2 - sVar3;
  iVar10 = (int)sVar9;
  sVar5 = (short)((iVar6 * iVar7) / 0x100);
  iVar8 = (int)sVar5;
  if (iVar10 - iVar8 < 0 == (iVar10 < 0 != iVar8 < 0 && iVar8 < 0 == iVar10 - iVar8 < 0) &&
      iVar10 != iVar8) {
    sVar3 = sVar2 - sVar5;
  }
  else if (iVar10 + iVar8 < 0 != (iVar10 < 0 != -iVar8 < 0 && -iVar8 < 0 == iVar10 + iVar8 < 0)) {
    sVar3 = sVar5 + sVar2;
  }
  (*((short *)camry_host_ptr((uint32_t)(puVar4 + 0x1254)))) = sVar3;
  (*((short *)camry_host_ptr((uint32_t)(puVar4 + 0x1252)))) = sVar9;
  (*((short *)camry_host_ptr((uint32_t)(puVar4 + 0x1250)))) = sVar5;
  (*((short *)camry_host_ptr((uint32_t)(puVar4 + 0x124c)))) = (short)iVar6;
  (*((short *)camry_host_ptr((uint32_t)(puVar4 + 0x124e)))) = (short)iVar7;
  return;
}

int attenuate_and_clamp_voted_c900_term_cdebc(void)

{
  byte bVar1;
  char cVar2;
  char cVar3;
  int iVar4;
  uint32_t puVar5;
  short input;
  int iVar6;
  int iVar7;
  int iVar8;
  int iVar9;
  int iVar10;
  int iVar11;
  uint uVar12;
  
  cVar3 = DAT_febeca9a;
  cVar2 = DAT_febeca99;
  puVar5 = 0xfebeb800u;
  bVar1 = DAT_febecb00 & 7;
  iVar7 = (int)(short)((DAT_febecb00 & 7) + (DAT_febeac3c & 1) * 8);
  if (((DAT_febec900 == DAT_febec990) || (DAT_febec900 == DAT_febec9bc)) ||
     (iVar4 = DAT_febec990, DAT_febec990 != DAT_febec9bc)) {
    iVar4 = DAT_febec900;
  }
  uVar12 = (uint)DAT_febeca58;
  input = abs_s16_wrapping(((int)(int16_t)DAT_febeca54));
  iVar6 = interpolate_signed_sentinel_curve(((short *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd3dacu + (uint32_t)(iVar7 * 0x57) * 4u)))))),input);
  iVar7 = interpolate_signed_sentinel_curve(((short *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd3db0u + (uint32_t)(iVar7 * 0x57) * 4u)))))),input);
  if (bVar1 == 0) {
    iVar10 = 0x4000;
    iVar11 = iVar10;
  }
  else {
    iVar10 = iVar6;
    if (((cVar2 != '\x01') || (-1 < iVar4)) && ((cVar3 != '\x01' || (iVar4 < 1)))) {
      iVar10 = iVar7;
    }
    iVar11 = (int)((0x100 - (uint)(*((ushort *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xb1484u + (uint32_t)((byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0xbc4))))) & 1) * 4u)))) + 0x68)))))
                   * uVar12 +
                  iVar10 * (uint)(*((ushort *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xb1484u + (uint32_t)((byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0xbc4))))) & 1) * 4u)))) + 0x68)))))
             / 0x100;
    iVar4 = (iVar11 * iVar4) / 0x4000;
  }
  iVar8 = (*((int *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd3cd8u + (uint32_t)((short)(((byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(0x1300))))) & 7) + ((byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0xbc4))))) & 1) * 8) * 0x57) * 4u)))))));
  iVar9 = iVar8;
  if ((iVar4 - iVar8 < 0 != (iVar4 < 0 != iVar8 < 0 && iVar8 < 0 == iVar4 - iVar8 < 0) ||
       iVar4 == iVar8) &&
     (iVar9 = -iVar8,
     iVar4 + iVar8 < 0 == (iVar4 < 0 != iVar9 < 0 && iVar9 < 0 == iVar4 + iVar8 < 0) &&
     iVar4 != iVar9)) {
    iVar9 = iVar4;
  }
  (*((short *)camry_host_ptr((uint32_t)(0x1228u + (int)puVar5)))) = (short)iVar6;
  (*((short *)camry_host_ptr((uint32_t)(puVar5 + 0x122a)))) = (short)iVar7;
  (*((int *)camry_host_ptr((uint32_t)(puVar5 + 0x1104)))) = iVar8;
  (*((int *)camry_host_ptr((uint32_t)(puVar5 + 0x1108)))) = iVar4;
  (*((int *)camry_host_ptr((uint32_t)(puVar5 + 0x1130)))) = iVar9;
  (*((short *)camry_host_ptr((uint32_t)(puVar5 + 0x1256)))) = (short)iVar10;
  (*((short *)camry_host_ptr((uint32_t)(puVar5 + 0x1258)))) = (short)iVar11;
  return iVar6;
}

int compose_angle_controller_terms(void)

{
  update_angle_error_and_derivative();
  compose_rate_feedforward_and_mode_curve_term_cd538();
  run_init_chain_cdd1e();
  debounce_ca0a_negative_hysteresis_into_ca99_cdd42();
  debounce_ca0a_positive_hysteresis_into_ca9a_cddb6();
  update_ca54_ca0a_deadband_by_curve_product_cde26();
  return attenuate_and_clamp_voted_c900_term_cdebc();
}

int map_signed_ca36_ae02_and_scale_adbe_cdff8(void)

{
  int iVar1;
  ushort input;
  int iVar2;
  uint32_t puVar3;
  short sVar4;
  int iVar5;
  int iVar6;
  int iVar7;
  short sVar8;
  uint uVar9;
  
  input = DAT_febeae02;
  puVar3 = 0xfebeb800u;
  uVar9 = (uint)DAT_febeadbe;
  iVar7 = (int)(short)((DAT_febecb00 & 7) + (DAT_febeac3c & 1) * 8);
  if (((((int)(int16_t)DAT_febeca36) == ((int)(int16_t)DAT_febeca82)) || (((int)(int16_t)DAT_febeca36) == ((int)(int16_t)DAT_febeca90))) ||
     (sVar8 = ((int)(int16_t)DAT_febeca82), ((int)(int16_t)DAT_febeca82) != ((int)(int16_t)DAT_febeca90))) {
    sVar8 = ((int)(int16_t)DAT_febeca36);
  }
  sVar4 = abs_s16_wrapping(sVar8);
  iVar5 = interpolate_signed_sentinel_curve(((short *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd3db4u + (uint32_t)(iVar7 * 0x57) * 4u)))))),sVar4);
  iVar6 = interpolate_unsigned_axis_sentinel_curve
                    (((ushort *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd3db8u + (uint32_t)(iVar7 * 0x57) * 4u)))))),input);
  iVar2 = ((int)(short)iVar6 * (int)(short)iVar5) / 0x100;
  sVar4 = (*((short *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd3cdcu + (uint32_t)(iVar7 * 0x57) * 4u)))))));
  iVar7 = (int)sVar4;
  if (sVar8 < 1) {
    iVar2 = -iVar2;
  }
  iVar2 = (int)(iVar2 * uVar9) / 100;
  sVar8 = sVar4;
  if (iVar2 - iVar7 < 0 != (iVar2 < 0 != iVar7 < 0 && iVar7 < 0 == iVar2 - iVar7 < 0) ||
      iVar2 == iVar7) {
    iVar1 = -iVar7;
    if (iVar2 + iVar7 < 0 == (iVar2 < 0 != iVar1 < 0 && iVar1 < 0 == iVar2 + iVar7 < 0) &&
        iVar2 != iVar1) {
      sVar8 = (short)iVar2;
    }
    else {
      sVar8 = (short)iVar1;
    }
  }
  (*((short *)camry_host_ptr((uint32_t)(puVar3 + 0x1238)))) = (short)iVar5;
  (*((short *)camry_host_ptr((uint32_t)(puVar3 + 0x123a)))) = (short)iVar6;
  (*((short *)camry_host_ptr((uint32_t)(puVar3 + 0x123c)))) = sVar4;
  (*((int *)camry_host_ptr((uint32_t)(puVar3 + 0x1128)))) = iVar2;
  (*((short *)camry_host_ptr((uint32_t)(puVar3 + 0x123e)))) = sVar8;
  (*((short *)camry_host_ptr((uint32_t)(puVar3 + 0x127a)))) = sVar8;
  (*((short *)camry_host_ptr((uint32_t)(puVar3 + 0x1288)))) = sVar8;
  return iVar6;
}
