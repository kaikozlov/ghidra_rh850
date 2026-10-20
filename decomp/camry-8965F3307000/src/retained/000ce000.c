#include "common.h"

int update_ca62_ca0a_deadband_and_return_ce0ae(void)

{
  int iVar1;
  undefined2 uVar2;
  short sVar3;
  uint32_t puVar4;
  short sVar5;
  short sVar6;
  int iVar7;
  int iVar8;
  int iVar9;
  
  sVar3 = ((int)(int16_t)DAT_febeca0a);
  puVar4 = 0xfebeb800u;
  iVar9 = (int)((int)(int16_t)DAT_febeca0a);
  sVar5 = abs_s16_wrapping(((int)(int16_t)DAT_febeca0a));
  uVar2 = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar4 + -0x9fe))));
  sVar6 = (*((short *)camry_host_ptr((uint32_t)(puVar4 + 0x1262))));
  iVar1 = (int)(short)(((byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(0x1300))))) & 7) + ((byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0xbc4))))) & 1) * 8);
  iVar7 = interpolate_unsigned16_axis_and_values_d0896(((ushort *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd3dbcu + (uint32_t)(iVar1 * 0x57) * 4u))))))), sVar5);
  iVar8 = interpolate_unsigned16_axis_and_values_d0896(((ushort *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd3dc0u + (uint32_t)(iVar1 * 0x57) * 4u))))))), uVar2);
  iVar1 = (iVar7 * iVar8) / 0x100;
  iVar9 = iVar9 - sVar6;
  sVar5 = (short)iVar1;
  if (iVar9 - iVar1 < 0 == (iVar9 < 0 != iVar1 < 0 && iVar1 < 0 == iVar9 - iVar1 < 0) &&
      iVar9 != iVar1) {
    sVar6 = sVar3 - sVar5;
  }
  else if (iVar9 + iVar1 < 0 != (iVar9 < 0 != -iVar1 < 0 && -iVar1 < 0 == iVar9 + iVar1 < 0)) {
    sVar6 = sVar5 + sVar3;
  }
  (*((short *)camry_host_ptr((uint32_t)(puVar4 + 0x1262)))) = sVar6;
  (*((short *)camry_host_ptr((uint32_t)(puVar4 + 0x1260)))) = (short)iVar9;
  (*((short *)camry_host_ptr((uint32_t)(puVar4 + 0x125e)))) = sVar5;
  (*((short *)camry_host_ptr((uint32_t)(puVar4 + 0x125a)))) = (short)iVar7;
  (*((short *)camry_host_ptr((uint32_t)(puVar4 + 0x125c)))) = (short)iVar8;
  return (int)sVar6;
}

int compose_angle_controller_prelimit_output(void)

{
  byte bVar1;
  undefined1 uVar2;
  ushort uVar3;
  ushort uVar4;
  int iVar5;
  int iVar6;
  ushort uVar7;
  int iVar8;
  uint32_t puVar9;
  short sVar10;
  int iVar11;
  undefined1 uVar12;
  undefined1 uVar13;
  int iVar14;
  int iVar15;
  int iVar16;
  ushort uVar17;
  uint uVar18;
  
  uVar2 = DAT_febeca9b;
  iVar16 = DAT_febec944;
  iVar6 = DAT_febec930;
  iVar5 = DAT_febec92c;
  uVar4 = DAT_febeae02;
  uVar3 = DAT_000b060c;
  puVar9 = 0xfebeb800u;
  bVar1 = DAT_febecb00 & 7;
  uVar17 = DAT_febecb00 & 7;
  uVar7 = (ushort)DAT_febeac3c;
  iVar14 = (int)((int)(int16_t)DAT_febeca3e);
  iVar8 = (int)((int)(int16_t)DAT_febeca7a);
  if (((iVar14 == iVar8) || (iVar14 == ((int)(int16_t)DAT_febeca88))) || (iVar8 != ((int)(int16_t)DAT_febeca88))) {
    iVar8 = iVar14;
  }
  iVar15 = (int)((int)(int16_t)DAT_febeca40);
  iVar14 = (int)((int)(int16_t)DAT_febeca7e);
  if (((iVar15 == iVar14) || (iVar15 == ((int)(int16_t)DAT_febeca8c))) || (iVar14 != ((int)(int16_t)DAT_febeca8c))) {
    iVar14 = iVar15;
  }
  uVar18 = (uint)DAT_febeca64;
  sVar10 = update_ca62_ca0a_deadband_and_return_ce0ae();
  sVar10 = abs_s16_wrapping(sVar10);
  iVar11 = interpolate_signed16_axis_unsigned16_values_d07f2(((short *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd3dc4u + (uint32_t)((short)(uVar17 + (uVar7 & 1) * 8) * 0x57) * 4u))))))), (int)sVar10);
  iVar15 = (int)(uVar18 * (0x100 - (uint)(*((ushort *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xb1484u + (uint32_t)((byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar9 + (uint32_t)(-0xbc4))))) & 1) * 4u)))) + 0x6a))))) +
                iVar11 * (uint)(*((ushort *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xb1484u + (uint32_t)((byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar9 + (uint32_t)(-0xbc4))))) & 1) * 4u)))) + 0x6a))))) /
           0x100;
  iVar8 = iVar8 + ((iVar6 + iVar5) * iVar15) / 0x400;
  if (bVar1 == 0) {
    uVar12 = (undefined1)uVar17;
    iVar16 = iVar8;
    uVar13 = uVar12;
    uVar2 = uVar12;
  }
  else {
    uVar12 = 1;
    uVar13 = uVar12;
    if ((uVar17 != 7) && (uVar4 < uVar3)) {
      iVar16 = iVar14;
      uVar13 = 0;
    }
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar9 + (uint32_t)(0x129c))))) = uVar12;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar9 + (uint32_t)(0x129d))))) = uVar13;
  (*((int *)camry_host_ptr((uint32_t)(puVar9 + 0x1134)))) = iVar8;
  (*((int *)camry_host_ptr((uint32_t)(puVar9 + 0x1194)))) = iVar8;
  (*((int *)camry_host_ptr((uint32_t)(puVar9 + 0x11c0)))) = iVar8;
  (*((int *)camry_host_ptr((uint32_t)(puVar9 + 0x1144)))) = iVar16;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar9 + (uint32_t)(0x129b))))) = uVar2;
  (*((short *)camry_host_ptr((uint32_t)(puVar9 + 0x1234)))) = (short)iVar11;
  (*((short *)camry_host_ptr((uint32_t)(puVar9 + 0x1264)))) = (short)iVar15;
  return iVar11;
}

void reset_angle_controller_control_state(void)

{
  int iVar1;
  
  DAT_febeca9d = 1;
  DAT_febec92c = 0;
  DAT_febec8f0 = 0;
  DAT_febec9ac = 0;
  DAT_febec9d8 = 0;
  DAT_febec8f4 = 0;
  DAT_febec8f8 = 0;
  DAT_febec920 = 0;
  DAT_febec91c = 0;
  DAT_febec918 = 0;
  DAT_febec924 = 0;
  DAT_febec9b0 = 0;
  DAT_febec9dc = 0;
  DAT_febec8fc = 0;
  DAT_febec9b4 = 0;
  DAT_febec9e0 = 0;
  DAT_febec8c4 = 0;
  DAT_febec8c8 = 0;
  DAT_febec900 = 0;
  DAT_febec990 = 0;
  DAT_febec9bc = 0;
  DAT_febec908 = 0;
  DAT_febec930 = 0;
  DAT_febec928 = 0;
  DAT_febeca3e = 0;
  DAT_febeca7a = 0;
  DAT_febeca88 = 0;
  DAT_febec934 = 0;
  DAT_febec994 = 0;
  DAT_febec9c0 = 0;
  DAT_febeca9c = 0;
  DAT_febeca32 = 0;
  DAT_febec90c = 0;
  DAT_febeca36 = 0;
  DAT_febeca82 = 0;
  DAT_febeca90 = 0;
  DAT_febeca0e = 0;
  DAT_febec910 = 0;
  DAT_febec9a8 = 0;
  DAT_febec9d4 = 0;
  DAT_febec914 = 0;
  DAT_febec8d8 = 0;
  DAT_febeca1e = 0;
  DAT_febeca86 = 0;
  DAT_febeca94 = 0;
  DAT_febeca02 = 0;
  DAT_febeca08 = 0;
  DAT_febec8cc = 0;
  DAT_febec8d0 = 0;
  DAT_febec8bc = 0;
  DAT_febec9a4 = 0;
  DAT_febec9d0 = 0;
  DAT_febec8c0 = 0;
  if (((DAT_febec8b8 == DAT_febec9a0) || (DAT_febec8b8 == DAT_febec9cc)) ||
     (iVar1 = DAT_febec9a0, DAT_febec9a0 != DAT_febec9cc)) {
    iVar1 = DAT_febec8b8;
  }
  DAT_febec958 = 0;
  DAT_febeca54 = 0;
  DAT_febeca62 = 0;
  DAT_febec950 = iVar1 * 10;
  DAT_febeca58 = 0x4000;
  DAT_febeca64 = 0x400;
  return;
}

void compose_or_reset_angle_control_by_mode7_ce384(void)

{
  if ((DAT_febecb00 & 7) == 7) {
    reset_angle_controller_control_state();
  }
  else {
    compose_angle_controller_terms();
    map_signed_ca36_ae02_and_scale_adbe_cdff8();
    compose_angle_controller_prelimit_output();
  }
  return;
}

void scale_voted_c934_by_adbd_or_subtract_offset_ce3aa(void)

{
  int iVar1;
  uint uVar2;
  uint uVar3;
  
  if (((DAT_febec934 == DAT_febec994) || (DAT_febec934 == DAT_febec9c0)) ||
     (iVar1 = DAT_febec994, DAT_febec994 != DAT_febec9c0)) {
    iVar1 = DAT_febec934;
  }
  uVar2 = (uint)DAT_febeadbd;
  uVar3 = uVar2;
  if (DAT_000b05c2 < uVar2) {
    uVar3 = (uint)DAT_000b05c2;
  }
  if (uVar2 == 0xc9) {
    uVar3 = (uint)(*((ushort *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xb146cu + (uint32_t)(DAT_febeac3c & 1) * 4u)))) + 0x8e))));
  }
  else if (uVar2 == 0xca) {
    uVar3 = (uint)(*((ushort *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xb146cu + (uint32_t)(DAT_febeac3c & 1) * 4u)))) + 0x90))));
  }
  else {
    if (uVar2 != 0xcb) {
      DAT_febec940 = (int)(iVar1 * uVar3) / 100;
      DAT_febec998 = DAT_febec940;
      DAT_febec9c4 = DAT_febec940;
      return;
    }
    uVar3 = (uint)(*((ushort *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xb146cu + (uint32_t)(DAT_febeac3c & 1) * 4u)))) + 0x92))));
  }
  DAT_febec940 = iVar1 - (int)((uVar3 * 0xa4)) / (int)0x3200;
  DAT_febec998 = DAT_febec940;
  DAT_febec9c4 = DAT_febec940;
  return;
}

uint interpolate_current_mode_d3dc8_curve_ce454(undefined2 param_1)

{
  return interpolate_unsigned16_axis_and_values_d0896(((ushort *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd3dc8u + (uint32_t)((short)((DAT_febecb00 & 7) + (DAT_febeac3c & 1) * 8) * 0x57) * 4u))))))), 
               param_1);
}

uint interpolate_previous_mode_d3dcc_curve_ce486(undefined2 param_1)

{
  return interpolate_unsigned16_axis_and_values_d0896(((ushort *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd3dccu + (uint32_t)((short)((DAT_febeca9f & 7) + (DAT_febeac3c & 1) * 8) * 0x57) * 4u))))))), 
               param_1);
}

uint select_current_or_previous_mode_limit_curve_ce4b8(undefined2 param_1)

{
  if ((uint)((DAT_febecb00 & 7) - 1) < 5) {
    return interpolate_current_mode_d3dc8_curve_ce454((uint)(ushort)param_1);
  }
  return interpolate_previous_mode_d3dcc_curve_ce486(param_1);
}

void interpolate_selected_limit_curve_into_ca42_ce4da(char param_1,undefined2 param_2)

{
  uint32_t puVar1;
  undefined2 uVar2;
  
  puVar1 = 0xfebeb800u;
  if (param_1 == '\x01') {
    uVar2 = select_current_or_previous_mode_limit_curve_ce4b8(param_2);
  }
  else {
    uVar2 = interpolate_unsigned16_axis_and_values_d0896(((ushort *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd3dd0u + (uint32_t)((short)((DAT_febecb00 & 7) + (DAT_febeac3c & 1) * 8) * 0x57) * 4u))))))),  (uint)(ushort)param_2);
  }
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + 0x1242)))) = uVar2;
  return;
}

void update_ca42_ca44_transition_limit_parameters_ce51c(void)

{
  byte bVar1;
  byte bVar2;
  ushort input;
  char cVar3;
  ushort uVar4;
  uint32_t puVar5;
  int iVar6;
  ushort uVar7;
  bool bVar8;
  
  bVar2 = DAT_febecaac;
  cVar3 = DAT_febeca9e;
  input = DAT_febeae02;
  puVar5 = 0xfebeb800u;
  if (DAT_febeca9d == '\x01') {
    uVar7 = DAT_febecb00 & 7;
    uVar4 = (ushort)DAT_febeca9f;
    bVar1 = DAT_febeca9f & 7;
    scale_voted_c934_by_adbd_or_subtract_offset_ce3aa();
    if ((cVar3 != '\0') ||
       ((bVar8 = false, uVar7 != (uVar4 & 7) && (bVar8 = true, bVar2 = bVar1, uVar7 == 7)))) {
      bVar8 = bVar2 != 0;
    }
    interpolate_selected_limit_curve_into_ca42_ce4da(bVar8,input);
    iVar6 = interpolate_unsigned_axis_sentinel_curve
                      (((ushort *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd3dd4u + (uint32_t)((short)(uVar7 + ((byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0xbc4))))) & 1) * 8) * 0x57) * 4u)))))),
                       input);
    (*((short *)camry_host_ptr((uint32_t)(puVar5 + 0x1244)))) = (short)iVar6;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(0x129e))))) = bVar8;
  }
  return;
}

void limit_angle_controller_output(void)

{
  bool bVar1;
  bool bVar2;
  undefined2 uVar3;
  int iVar4;
  int iVar5;
  uint32_t puVar6;
  uint uVar7;
  undefined1 uVar8;
  bool bVar9;
  int iVar10;
  undefined1 uVar11;
  uint uVar12;
  
  uVar11 = DAT_febeca9b;
  puVar6 = 0xfebeb800u;
  if (DAT_febeca9d == '\x01') {
    if (((DAT_febec940 == DAT_febec998) || (DAT_febec940 == DAT_febec9c4)) ||
       (iVar5 = DAT_febec998, DAT_febec998 != DAT_febec9c4)) {
      iVar5 = DAT_febec940;
    }
    iVar10 = (int)((int)(int16_t)DAT_febeca40);
    iVar4 = (int)((int)(int16_t)DAT_febeca7e);
    if (((iVar10 == iVar4) || (iVar10 == ((int)(int16_t)DAT_febeca8c))) || (iVar4 != ((int)(int16_t)DAT_febeca8c))) {
      iVar4 = iVar10;
    }
    iVar10 = iVar5 - iVar4;
    uVar12 = (uint)DAT_febeca42;
    puVar6 = 0xfebeb800u;
    uVar7 = abs_s32_wrapping(iVar10);
    (*((int *)camry_host_ptr((uint32_t)(puVar6 + 0x1138)))) = iVar10;
    uVar12 = (int)((uVar12 * 0xa4)) / (int)0x8000;
    (*((uint *)camry_host_ptr((uint32_t)(puVar6 + 0x1148)))) = uVar12;
    bVar1 = uVar7 != uVar12;
    bVar2 = (int)(uVar7 - uVar12) < 0 == ((int)uVar7 < 0 && -1 < (int)(uVar7 - uVar12));
    bVar9 = bVar2 && bVar1;
    if (bVar2 && bVar1) {
      if (iVar10 < 1) {
        iVar5 = iVar4 - uVar12;
        if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xb146cu + (uint32_t)((byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(-0xbc4))))) & 1) * 4u)))) + (uint32_t)(1))))) == '\x01') {
          uVar11 = 1;
        }
      }
      else {
        iVar5 = uVar12 + iVar4;
        if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xb146cu + (uint32_t)((byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(-0xbc4))))) & 1) * 4u)))) + (uint32_t)(1))))) == '\x01') {
          uVar11 = 2;
        }
      }
    }
    iVar4 = (int)(*((short *)camry_host_ptr((uint32_t)(puVar6 + 0x1244))));
    if (iVar5 - iVar4 < 0 == (iVar5 < 0 != iVar4 < 0 && iVar4 < 0 == iVar5 - iVar4 < 0) &&
        iVar5 != iVar4) {
      uVar11 = 2;
      uVar8 = 1;
      iVar10 = iVar4;
    }
    else {
      iVar10 = -iVar4;
      if (iVar5 + iVar4 < 0 == (iVar5 < 0 != iVar10 < 0 && iVar10 < 0 == iVar5 + iVar4 < 0)) {
        uVar8 = 0;
        iVar10 = iVar5;
        if (((*((volatile uint8_t *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xb146cu + (uint32_t)((byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(-0xbc4))))) & 1) * 4u)))) + (uint32_t)(1))))) != '\x01') || (!bVar2 || !bVar1)) {
          uVar11 = 0;
        }
      }
      else {
        uVar8 = 1;
        uVar11 = 1;
      }
    }
    uVar3 = (undefined2)iVar10;
    (*((int *)camry_host_ptr((uint32_t)(puVar6 + 0x113c)))) = iVar5;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(0x129b))))) = uVar11;
  }
  else {
    iVar5 = 0x7fff;
    if (((int)DAT_febec944 + -0x7fff < 0 != ((int)DAT_febec944 < 0 && -1 < (int)DAT_febec944 + -0x7fff) ||
         ((int)(int32_t)DAT_febec944) == 0x7fff) &&
       (iVar5 = ((int)(int32_t)DAT_febec944),
       (int)DAT_febec944 + 0x7fff < 0 != (-1 < (int)DAT_febec944 && (int)DAT_febec944 + 0x7fff < 0) ||
       ((int)(int32_t)DAT_febec944) == -0x7fff)) {
      iVar5 = -0x7fff;
    }
    uVar3 = (undefined2)iVar5;
    bVar9 = false;
    uVar8 = 0;
  }
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar6 + 0x1246)))) = uVar3;
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar6 + 0x127c)))) = uVar3;
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar6 + 0x128a)))) = uVar3;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(0x12ac))))) = bVar9;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(0x12ad))))) = uVar8;
  if (((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(0x1300))))) & 7) == 0) {
    uVar3 = 0;
  }
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar6 + 0x1240)))) = uVar3;
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar6 + 0x127e)))) = uVar3;
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar6 + 0x128c)))) = uVar3;
  return;
}

void run_angle_control_filters_compose_and_limit_ce6cc(void)

{
  uint32_t puVar1;
  byte bVar2;
  
  puVar1 = 0xfebeb800u;
  bVar2 = DAT_febecb00 & 7;
  filter_ae24_with_previous_sample_q14_cd046();
  filter_angle_controller_measured_rate();
  compose_or_reset_angle_control_by_mode7_ce384();
  update_ca42_ca44_transition_limit_parameters_ce51c();
  limit_angle_controller_output();
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x129f))))) = bVar2;
  return;
}

int shape_angle_controller_target(void)

{
  short value;
  uint32_t puVar1;
  short *points;
  short input;
  int iVar2;
  undefined2 uVar3;
  
  puVar1 = 0xfebeb800u;
  if (((((int)(int16_t)DAT_febeca46) == ((int)(int16_t)DAT_febeca7c)) || (((int)(int16_t)DAT_febeca46) == ((int)(int16_t)DAT_febeca8a))) ||
     (value = ((int)(int16_t)DAT_febeca7c), ((int)(int16_t)DAT_febeca7c) != ((int)(int16_t)DAT_febeca8a))) {
    value = ((int)(int16_t)DAT_febeca46);
  }
  input = abs_s16_wrapping(value);
  if (value < 0) {
    points = (short *)((undefined *)camry_host_ptr(0xb05e8u));
  }
  else {
    points = (short *)((undefined *)camry_host_ptr(0xb05c4u));
  }
  iVar2 = interpolate_signed_sentinel_curve(points,input);
  (*((short *)camry_host_ptr((uint32_t)(0x1228u + (int)(puVar1 + 4))))) = (short)iVar2;
  uVar3 = (undefined2)(((int)(short)iVar2 * (int)value) / 0x400);
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + 0x122e)))) = uVar3;
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + 0x1280)))) = uVar3;
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + 0x128e)))) = uVar3;
  return iVar2;
}

void fill_constant_block_ce750(void)

{
  DAT_febecaae = 0;
  DAT_febecab2 = 0;
  DAT_febecab3 = 0;
  DAT_febecab4 = 0;
  DAT_febecab0 = 0;
  DAT_febecab5 = 0;
  DAT_febecab6 = 0;
  DAT_febecab7 = 0;
  return;
}

char enable_if_clear_accc_accd_adbf_cafc_cad9_ce772(char param_1)

{
  if ((((param_1 == '\0') && (DAT_febeaccc == '\0')) && (DAT_febeaccd == '\0')) &&
     (((DAT_febeadbf < 2 && (DAT_febecafc == '\0')) && (DAT_febecad9 == '\0')))) {
    param_1 = '\x01';
  }
  return param_1;
}

char clear_enable_on_fault_or_accd_timeout_ce7a6(char param_1)

{
  if ((param_1 == '\x01') && (DAT_febeaccd != '\0')) {
    DAT_febecaae = DAT_febecaae + 1;
  }
  else {
    DAT_febecaae = 0;
    if (param_1 != '\x01') {
      DAT_febecaae = 0;
      return param_1;
    }
  }
  if ((((DAT_febeaccc != '\0') || (DAT_000b060e < DAT_febecaae)) ||
      (DAT_febeadbf == '\x02' || DAT_febeadbf == '\x03')) ||
     ((DAT_febecafc == '\x01' || (DAT_febecad9 == '\x01')))) {
    param_1 = '\0';
    DAT_febecaae = 0;
  }
  return param_1;
}

void vote_update_and_triplicate_cab2_enable_ce7fe(void)

{
  uint32_t puVar1;
  char cVar2;
  undefined1 uVar3;
  undefined4 uVar4;
  
  puVar1 = 0xfebeb800u;
  if (((DAT_febecab2 == DAT_febecab3) || (DAT_febecab2 == DAT_febecab4)) ||
     (cVar2 = DAT_febecab3, DAT_febecab3 != DAT_febecab4)) {
    cVar2 = DAT_febecab2;
  }
  uVar4 = enable_if_clear_accc_accd_adbf_cafc_cad9_ce772(cVar2);
  uVar3 = clear_enable_on_fault_or_accd_timeout_ce7a6(uVar4);
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x12b2))))) = uVar3;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x12b3))))) = uVar3;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x12b4))))) = uVar3;
  return;
}

void step_cab7_enable_reasons_and_cab6_holdoff_ce836(void)

{
  char cVar1;
  
  if (((DAT_febecab2 == DAT_febecab3) || (DAT_febecab2 == DAT_febecab4)) ||
     (cVar1 = DAT_febecab3, DAT_febecab3 != DAT_febecab4)) {
    cVar1 = DAT_febecab2;
  }
  if (DAT_febecab7 == '\0') {
    if (((cVar1 == '\x01') && ((DAT_febecb00 & 7) != 7)) && (DAT_febecab6 == '\0')) {
      DAT_febecab5 = 0x11;
      DAT_febecab7 = 1;
      return;
    }
  }
  else {
    if (cVar1 == '\0') {
      DAT_febecab5 = 0x44;
      DAT_febecab7 = '\0';
      goto LAB_000ce8a6;
    }
    if ((DAT_febecb00 & 7) == 7) {
      DAT_febecab7 = '\0';
      DAT_febecab5 = 0x22;
    }
  }
  if (DAT_febecab6 != '\x01') {
    return;
  }
LAB_000ce8a6:
  DAT_febecab6 = true;
  if (DAT_febecab0 <= DAT_000b0610) {
    DAT_febecab0 = DAT_febecab0 + 1;
    DAT_febecab6 = DAT_febecab0 <= DAT_000b0610;
    if (DAT_000b0610 < DAT_febecab0) {
      DAT_febecab0 = 0;
    }
  }
  return;
}

void update_triplicate_enable_and_cab7_transition_ce8ca(void)

{
  vote_update_and_triplicate_cab2_enable_ce7fe();
  step_cab7_enable_reasons_and_cab6_holdoff_ce836();
  return;
}

void step_retained_unsigned_gain(F33GainSlewState *state)

{
  int iVar1;
  ushort uVar2;
  ushort uVar3;
  ushort uVar4;
  uint uVar5;
  
  uVar2 = state->current;
  uVar5 = (uint)uVar2;
  uVar4 = state->down_target;
  if ((uVar5 < uVar4) || (state->direction != '\x02')) {
    uVar4 = state->up_target;
    uVar3 = state->up_step;
    uVar5 = uVar4 - uVar5;
    iVar1 = uVar5 - uVar3;
    if (iVar1 < 0 == ((int)uVar5 < 0 && -1 < iVar1) && uVar5 != uVar3) {
      uVar4 = uVar2 + uVar3;
    }
  }
  else {
    uVar3 = state->down_step;
    uVar5 = uVar5 - uVar4;
    iVar1 = uVar5 - uVar3;
    if (iVar1 < 0 == ((int)uVar5 < 0 && -1 < iVar1) && uVar5 != uVar3) {
      uVar4 = uVar2 - uVar3;
    }
  }
  state->current = uVar4;
  return;
}

void update_retained_mode_gain_below_magnitude_threshold_ce912(char *param_1)

{
  bool bVar1;
  int iVar2;
  uint32_t puVar3;
  short sVar4;
  undefined2 uVar5;
  int iVar6;
  
  puVar3 = 0xfebeb800u;
  sVar4 = abs_s16_wrapping(*(short *)(param_1 + 0x10));
  iVar6 = (int)sVar4;
  iVar2 = (int)(*((volatile short *)camry_host_ptr((*((volatile uint32_t *)(param_1 + 4))))));
  if (iVar6 - iVar2 < 0 != (iVar6 < 0 != iVar2 < 0 && iVar2 < 0 == iVar6 - iVar2 < 0)) {
    bVar1 = false;
    if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(0x12b7))))) == '\x01') {
      bVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(0x1300))))) == *param_1;
    }
    param_1[0xc] = bVar1;
  }
  uVar5 = 0x400;
  if (param_1[0xc] == '\x01') {
    uVar5 = interpolate_signed16_axis_unsigned16_values_d07f2(((short *)camry_host_ptr((uint32_t)(*(undefined4 *)(param_1 + 8)))), iVar6);
  }
  *(undefined2 *)(param_1 + 0xe) = uVar5;
  return;
}

void fill_constant_block_ce964(void)

{
  DAT_febecabc = 0;
  DAT_febecac0 = 0;
  DAT_febecac4 = 0;
  DAT_febecab8 = 0;
  DAT_febecaca = 0;
  DAT_febecacc = 0;
  DAT_febecacb = 0;
  DAT_febecace = 0;
  DAT_febecad0 = 0;
  DAT_febecad8 = 0;
  DAT_febecacd = 0;
  DAT_febecacf = 0;
  DAT_febecad2 = 0;
  DAT_febecad4 = 0;
  DAT_febecad6 = 0;
  DAT_febecac8 = 0;
  DAT_febecad9 = 1;
  return;
}

void set_caca_from_acc4_cafe_and_acbd_ce9ac(void)

{
  if ((DAT_febeacc4 == '\0') && (DAT_febecafe == '\x01')) {
    DAT_febecaca = DAT_febeacbd == '\0';
  }
  else {
    DAT_febecaca = false;
  }
  return;
}

void set_cacc_from_caff_and_acbd_ce9d0(void)

{
  DAT_febecacc = DAT_febecaff == '\x01' && DAT_febeacbd == '\0';
  return;
}

void capture_triplicate_ae5e_offset_under_quiet_gates_ce9ea(void)

{
  int value;
  int iVar1;
  char cVar2;
  char cVar3;
  short value_00;
  short value_01;
  char cVar4;
  uint32_t puVar5;
  uint32_t puVar6;
  ushort uVar7;
  ushort uVar8;
  uint uVar9;
  int iVar10;
  int iVar11;
  char cVar12;
  
  cVar4 = DAT_febecaca;
  value_01 = ((int)(int16_t)DAT_febeae24);
  value_00 = ((int)(int16_t)DAT_febeae22);
  cVar3 = DAT_febead4d;
  cVar2 = DAT_febead4c;
  puVar6 = 0xfebeb800u;
  if (((DAT_febecacb == DAT_febecace) || (DAT_febecacb == DAT_febecad0)) ||
     (cVar12 = DAT_febecace, DAT_febecace != DAT_febecad0)) {
    cVar12 = DAT_febecacb;
  }
  if (((DAT_febecabc == DAT_febecac0) || (DAT_febecabc == DAT_febecac4)) ||
     (iVar11 = DAT_febecac0, DAT_febecac0 != DAT_febecac4)) {
    iVar11 = DAT_febecabc;
  }
  iVar10 = (int)((int)(int16_t)DAT_febeae5e);
  value = (int)((int)(int8_t)DAT_febeacc5) + ((int)(int16_t)DAT_febeadfe) * 0xf;
  iVar1 = (value * 0x6fb) / 0x200;
  uVar9 = abs_s32_wrapping(value);
  uVar7 = abs_s16_wrapping(value_00);
  uVar8 = abs_s16_wrapping(value_01);
  if (((cVar3 == 'Z') && (cVar2 == '\0')) && (cVar4 == '\x01')) {
    if ((((cVar12 == '\0') &&
         (puVar5 = ((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xb146cu + (uint32_t)((byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(-0xbc4))))) & 1) * 4u)))))), uVar9 < (*((volatile uint16_t *)camry_host_ptr((uint32_t)(puVar5 + 0x2c))))
         )) && (uVar7 < (*((volatile uint16_t *)camry_host_ptr((uint32_t)(puVar5 + 0x2e)))))) && (uVar8 < (*((volatile uint16_t *)camry_host_ptr((uint32_t)(puVar5 + 0x30)))))) {
      iVar11 = iVar10 * 2 - iVar1;
      cVar12 = '\x01';
    }
  }
  else {
    cVar12 = '\0';
  }
  (*((int *)camry_host_ptr((uint32_t)(puVar6 + 0x12b8)))) = iVar1;
  (*((int *)camry_host_ptr((uint32_t)(puVar6 + 0x12bc)))) = iVar11;
  (*((int *)camry_host_ptr((uint32_t)(puVar6 + 0x12c0)))) = iVar11;
  (*((int *)camry_host_ptr((uint32_t)(puVar6 + 0x12c4)))) = iVar11;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(0x12cb))))) = cVar12;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(0x12ce))))) = cVar12;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(0x12d0))))) = cVar12;
  return;
}

void publish_offset_corrected_angle_feedback(void)

{
  char cVar1;
  int iVar2;
  
  if (((DAT_febecacb == DAT_febecace) || (DAT_febecacb == DAT_febecad0)) ||
     (cVar1 = DAT_febecace, DAT_febecace != DAT_febecad0)) {
    cVar1 = DAT_febecacb;
  }
  if (((DAT_febecabc == DAT_febecac0) || (DAT_febecabc == DAT_febecac4)) ||
     (iVar2 = DAT_febecac0, DAT_febecac0 != DAT_febecac4)) {
    iVar2 = DAT_febecabc;
  }
  if (((DAT_febecad8 == DAT_febecacd) || (DAT_febecad8 == DAT_febecacf)) ||
     (DAT_febecacd != DAT_febecacf)) {
    DAT_febecacd = DAT_febecad8;
  }
  if ((DAT_febead4c == '\0') && (cVar1 == '\x01')) {
    if (DAT_febecacd == '\0') {
      DAT_febecacd = '\x01';
    }
    iVar2 = ((int)(int16_t)DAT_febeae5e) * 2 - iVar2;
    if (iVar2 + -0x7fff < 0 == (iVar2 < 0 && -1 < iVar2 + -0x7fff) && iVar2 != 0x7fff) {
      DAT_febecad2 = 0x7fff;
      DAT_febecad4 = DAT_febecad2;
      DAT_febecad6 = DAT_febecad2;
    }
    else if (iVar2 + 0x8000 < 0 == (-1 < iVar2 && iVar2 + 0x8000 < 0)) {
      DAT_febecad2 = (undefined2)iVar2;
      DAT_febecad4 = DAT_febecad2;
      DAT_febecad6 = DAT_febecad2;
    }
    else {
      DAT_febecad2 = 0x8000;
      DAT_febecad4 = DAT_febecad2;
      DAT_febecad6 = DAT_febecad2;
    }
  }
  else {
    DAT_febecacd = '\0';
  }
  DAT_febecad8 = DAT_febecacd;
  DAT_febecacf = DAT_febecacd;
  return;
}

void update_angle_feedback_offset_and_publication(void)

{
  set_caca_from_acc4_cafe_and_acbd_ce9ac();
  set_cacc_from_caff_and_acbd_ce9d0();
  capture_triplicate_ae5e_offset_under_quiet_gates_ce9ea();
  publish_offset_corrected_angle_feedback();
  return;
}

void debounce_voted_cad2_cab8_difference_into_cad9_ceb92(void)

{
  int iVar1;
  bool bVar2;
  int iVar3;
  uint32_t puVar4;
  int iVar5;
  undefined1 uVar6;
  ushort uVar7;
  
  uVar6 = DAT_febecad9;
  uVar7 = DAT_febecac8;
  iVar1 = DAT_000b0614;
  puVar4 = 0xfebeb800u;
  iVar5 = (int)((int)(int16_t)DAT_febecad2);
  iVar3 = (int)((int)(int16_t)DAT_febecad4);
  if (((iVar5 == iVar3) || (iVar5 == ((int)(int16_t)DAT_febecad6))) || (iVar3 != ((int)(int16_t)DAT_febecad6))) {
    iVar3 = iVar5;
  }
  iVar5 = DAT_000b0614 * 2;
  if ((DAT_febead4c == '\0') && (DAT_febecaca == '\x01')) {
    puVar4 = 0xfebeb800u;
    iVar3 = abs_s32_wrapping(iVar3 - DAT_febecab8);
    iVar1 = iVar3 + iVar1 * -2;
    bVar2 = iVar5 < 0;
    if (iVar1 < 0 == (iVar3 < 0 != bVar2 && bVar2 == iVar1 < 0)) {
      if (uVar7 < DAT_000b0618) {
        uVar7 = uVar7 + 1;
      }
      else {
        uVar6 = 1;
      }
    }
    else {
      uVar6 = 0;
      uVar7 = 0;
    }
  }
  else {
    uVar6 = 1;
    uVar7 = 0;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(0x12d9))))) = uVar6;
  (*((ushort *)camry_host_ptr((uint32_t)(puVar4 + 0x12c8)))) = uVar7;
  return;
}

void fill_constant_block_cec0c(void)

{
  DAT_febecafc = 0;
  DAT_febecada = 0;
  DAT_febecadc = 0;
  DAT_febecade = 0;
  DAT_febecaf4 = 0;
  DAT_febecae0 = 0;
  DAT_febecae2 = 0;
  DAT_febecae4 = 0;
  DAT_febecaf5 = 0;
  DAT_febecaf6 = 0;
  DAT_febecaf7 = 0;
  DAT_febecaf8 = 0;
  DAT_febecaf9 = 0;
  DAT_febecae6 = 0;
  DAT_febecae8 = 0;
  DAT_febecafa = 0;
  DAT_febecafb = 0;
  DAT_febecaea = 0;
  DAT_febecaec = 0;
  DAT_febecaee = 0;
  DAT_febecaf0 = 0;
  DAT_febecaf2 = 0;
  DAT_febecafd = 0;
  DAT_febecafe = 0;
  DAT_febecaff = 0;
  return;
}

void or_cafb_cafd_into_cafc_cec72(void)

{
  DAT_febecafc = DAT_febecafb == '\x01' || DAT_febecafd == '\x01';
  return;
}

void update_adbc_wrapped_delta_and_bound_cade_cec8a(void)

{
  int iVar1;
  int iVar2;
  
  iVar1 = (int)(short)DAT_febecada;
  if ((int)((uint)DAT_febeadbc - iVar1) < 0 ==
      (iVar1 < 0 && iVar1 < 0 == (int)((uint)DAT_febeadbc - iVar1) < 0)) {
    DAT_febecadc = DAT_febeadbc - ((int)(int16_t)DAT_febecada);
  }
  else {
    DAT_febecadc = DAT_000b0620 + (DAT_febeadbc - ((int)(int16_t)DAT_febecada)) + 1;
  }
  DAT_febecada = (ushort)DAT_febeadbc;
  iVar1 = (int)DAT_febecadc;
  if (iVar1 + -1 < 0 == (iVar1 < 0 && -1 < iVar1 + -1) && iVar1 != 1) {
    iVar2 = (int)DAT_000b0622;
    DAT_febecade = DAT_febecadc;
    if (iVar1 - iVar2 < 0 == (iVar1 < 0 != iVar2 < 0 && iVar2 < 0 == iVar1 - iVar2 < 0)) {
      DAT_febecade = DAT_000b0622;
    }
  }
  else {
    DAT_febecade = 1;
  }
  return;
}

void debounce_acd6_non_mode7_into_caf5_cecd6(void)

{
  if (((DAT_febecb00 & 7) == 7) || (DAT_febeacd6 != '\x01')) {
    DAT_febecaf4 = 0;
    DAT_febecaf5 = false;
    DAT_febecae0 = 0;
  }
  else {
    if (DAT_febecae0 < (*((ushort *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xb146cu + (uint32_t)(DAT_febeac3c & 1) * 4u)))) + 2))))) {
      DAT_febecae0 = DAT_febecae0 + 1;
    }
    DAT_febecaf5 = (*((ushort *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xb146cu + (uint32_t)(DAT_febeac3c & 1) * 4u)))) + 2)))) <= DAT_febecae0;
    DAT_febecaf4 = 1;
  }
  return;
}

short debounce_abs_ae22_above_mode_limit_into_caf7_ced28(void)

{
  undefined1 uVar1;
  ushort uVar2;
  uint32_t puVar3;
  short sVar4;
  int iVar6;
  bool bVar7;
  ushort uVar8;
  int iVar5;
  
  uVar8 = DAT_febecae2;
  puVar3 = 0xfebeb800u;
  uVar2 = (ushort)DAT_febecb00;
  sVar4 = abs_s16_wrapping(((int)(int16_t)DAT_febeae22));
  iVar5 = (int)sVar4;
  iVar6 = (int)(*((short *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd3dd8u + (uint32_t)((short)((uVar2 & 7) + (short)(((byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0xbc4))))) & 1) << 3)) * 0x57) * 4u)))))));
  if (((uVar2 & 7) == 7) ||
     (iVar5 - iVar6 < 0 != (iVar5 < 0 != iVar6 < 0 && iVar6 < 0 == iVar5 - iVar6 < 0) ||
      iVar5 == iVar6)) {
    uVar1 = 0;
    bVar7 = false;
    uVar8 = 0;
  }
  else {
    uVar1 = 1;
    if (uVar8 < (*((ushort *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xb146cu + (uint32_t)((byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0xbc4))))) & 1) * 4u)))) + 8))))) {
      uVar8 = uVar8 + 1;
    }
    bVar7 = (*((ushort *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xb146cu + (uint32_t)((byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0xbc4))))) & 1) * 4u)))) + 8)))) <= uVar8;
  }
  (*((short *)camry_host_ptr((uint32_t)(puVar3 + 0x12e4)))) =
       (*((short *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd3dd8u + (uint32_t)((short)((uVar2 & 7) + (short)(((byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0xbc4))))) & 1) << 3)) * 0x57) * 4u)))))));
  (*((ushort *)camry_host_ptr((uint32_t)(puVar3 + 0x12e2)))) = uVar8;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(0x12f6))))) = uVar1;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(0x12f7))))) = bVar7;
  return sVar4;
}

short debounce_abs_ae24_below_mode_limit_into_caf9_ceda4(void)

{
  int iVar1;
  short sVar2;
  undefined1 uVar3;
  ushort uVar4;
  uint32_t puVar5;
  short sVar6;
  int iVar7;
  bool bVar8;
  ushort uVar9;
  
  uVar9 = DAT_febecae6;
  puVar5 = 0xfebeb800u;
  uVar4 = (ushort)DAT_febecb00;
  sVar6 = abs_s16_wrapping(((int)(int16_t)DAT_febeae24));
  sVar2 = (*((short *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd3ddcu + (uint32_t)((short)((uVar4 & 7) + (short)(((byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0xbc4))))) & 1) << 3)) * 0x57) * 4u)))))));
  iVar7 = (int)sVar2;
  if (((uVar4 & 7) == 7) ||
     (iVar1 = sVar6 - iVar7, iVar1 < 0 == (sVar6 < 0 != iVar7 < 0 && iVar7 < 0 == iVar1 < 0))) {
    uVar3 = 0;
    bVar8 = false;
    uVar9 = 0;
  }
  else {
    uVar3 = 1;
    if (uVar9 < (*((ushort *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xb146cu + (uint32_t)((byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0xbc4))))) & 1) * 4u)))) + 0xe))))) {
      uVar9 = uVar9 + 1;
    }
    bVar8 = (*((ushort *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xb146cu + (uint32_t)((byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0xbc4))))) & 1) * 4u)))) + 0xe)))) <= uVar9;
  }
  (*((short *)camry_host_ptr((uint32_t)(puVar5 + 0x12e8)))) = sVar2;
  (*((ushort *)camry_host_ptr((uint32_t)(puVar5 + 0x12e6)))) = uVar9;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(0x12f8))))) = uVar3;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(0x12f9))))) = bVar8;
  return sVar6;
}

void update_ae22_ae24_debounces_and_cafa_cee20(void)

{
  undefined1 uVar1;
  uint32_t puVar2;
  puVar2 = 0xfebeb800u;
  debounce_abs_ae22_above_mode_limit_into_caf7_ced28();
  debounce_abs_ae24_below_mode_limit_into_caf9_ceda4();
  if (((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(0x12f7))))) != '\x01') || (uVar1 = 1, (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(0x12f9))))) != '\x01')) {
    uVar1 = 0;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(0x12fa))))) = uVar1;
  return;
}

void load_mode_caea_caec_threshold_pair_cee46(void)

{
  int iVar1;
  
  iVar1 = (int)(short)((DAT_febecb00 & 7) + (DAT_febeac3c & 1) * 8);
  DAT_febecaea = (*((undefined2 *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd3de0u + (uint32_t)(iVar1 * 0x57) * 4u)))))));
  DAT_febecaec = (*((undefined2 *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd3de4u + (uint32_t)(iVar1 * 0x57) * 4u)))))));
  return;
}

void update_cafb_from_ae90_tracking_thresholds_cee7c(void)

{
  int iVar1;
  int iVar2;
  short sVar3;
  short sVar4;
  short sVar5;
  char cVar6;
  char cVar7;
  char cVar8;
  ushort uVar9;
  ushort uVar10;
  uint uVar11;
  uint32_t puVar12;
  uint uVar13;
  int iVar14;
  byte bVar15;
  undefined1 uVar16;
  
  puVar12 = 0xfebeb800u;
  bVar15 = DAT_febecb00 & 7;
  load_mode_caea_caec_threshold_pair_cee46();
  uVar11 = DAT_000b061c;
  sVar3 = (*((short *)camry_host_ptr((uint32_t)(puVar12 + 0x12de))));
  sVar4 = (*((short *)camry_host_ptr((uint32_t)(puVar12 + -0x970))));
  sVar5 = (*((short *)camry_host_ptr((uint32_t)(puVar12 + 0x12a4))));
  cVar6 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar12 + (uint32_t)(0x12b6)))));
  cVar7 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar12 + (uint32_t)(0x12fa)))));
  cVar8 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar12 + (uint32_t)(0x12f5)))));
  uVar16 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar12 + (uint32_t)(0x12fb)))));
  uVar9 = (*((ushort *)camry_host_ptr((uint32_t)(puVar12 + 0x12ea))));
  uVar10 = (*((ushort *)camry_host_ptr((uint32_t)(puVar12 + 0x12ec))));
  uVar13 = abs_s32_wrapping((int)sVar4);
  iVar14 = abs_s32_wrapping((int)sVar4 - (int)sVar5 / 2);
  iVar2 = (int)sVar3 * (uint)uVar10;
  if (bVar15 != 7) {
    if (cVar6 != '\0') goto LAB_000cef06;
    if (((cVar7 == '\x01') || (cVar8 == '\x01')) ||
       (iVar1 = uVar13 - uVar9, iVar1 < 0 == ((int)uVar13 < 0 && -1 < iVar1) && uVar13 != uVar9)) {
      uVar16 = 1;
      goto LAB_000cef06;
    }
    if ((int)(uVar13 - uVar11) < 0 ==
        ((int)uVar13 < 0 != (int)uVar11 < 0 && (int)uVar11 < 0 == (int)(uVar13 - uVar11) < 0) &&
        uVar13 != uVar11) {
      uVar16 = iVar14 - iVar2 < 0 == (iVar14 < 0 != iVar2 < 0 && iVar2 < 0 == iVar14 - iVar2 < 0) &&
               iVar14 != iVar2;
      goto LAB_000cef06;
    }
  }
  uVar16 = 0;
LAB_000cef06:
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar12 + (uint32_t)(0x12fb))))) = uVar16;
  return;
}

void run_init_chain_cef0e(void)

{
  update_adbc_wrapped_delta_and_bound_cade_cec8a();
  debounce_acd6_non_mode7_into_caf5_cecd6();
  update_ae22_ae24_debounces_and_cafa_cee20();
  update_cafb_from_ae90_tracking_thresholds_cee7c();
  return;
}

void latch_cafd_after_ae24_threshold_duration_cef26(void)

{
  int iVar1;
  ushort uVar2;
  ushort uVar3;
  char cVar4;
  short sVar5;
  ushort uVar6;
  uint32_t puVar7;
  ushort uVar8;
  char cVar9;
  
  cVar9 = DAT_febecafd;
  sVar5 = DAT_febecaf2;
  cVar4 = DAT_febecab6;
  puVar7 = 0xfebeb800u;
  uVar6 = (ushort)DAT_febecb00;
  uVar8 = abs_s16_wrapping(((int)(int16_t)DAT_febeae24));
  iVar1 = (int)(short)((uVar6 & 7) + ((byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar7 + (uint32_t)(-0xbc4))))) & 1) * 8);
  uVar2 = (*((ushort *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd3de8u + (uint32_t)(iVar1 * 0x57) * 4u)))))));
  uVar3 = (*((ushort *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd3decu + (uint32_t)(iVar1 * 0x57) * 4u)))))));
  if (((((uVar6 & 7) == 7) || (cVar4 != '\0')) || (cVar9 == '\x01')) || (uVar8 < uVar2)) {
    uVar6 = 0;
  }
  else {
    uVar6 = sVar5 + 1;
    if (uVar3 <= uVar6) {
      uVar6 = 0;
      cVar9 = '\x01';
    }
  }
  (*((ushort *)camry_host_ptr((uint32_t)(puVar7 + 0x12f2)))) = uVar6;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar7 + (uint32_t)(0x12fd))))) = cVar9;
  (*((ushort *)camry_host_ptr((uint32_t)(puVar7 + 0x12ee)))) = uVar2;
  (*((ushort *)camry_host_ptr((uint32_t)(puVar7 + 0x12f0)))) = uVar3;
  return;
}

void derive_caff_cafe_group_status_gates_cefa4(void)

{
  bool bVar1;
  uint32_t puVar2;
  byte bVar3;
  byte bVar4;
  
  puVar2 = 0xfebeb800u;
  bVar3 = get_application_grouped_status(0x11);
  bVar4 = get_application_grouped_status(0x1a);
  bVar1 = (bVar3 | bVar4) != 0x5a;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(0x12ff))))) = bVar1 && (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0xa47))))) == '\0';
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(0x12fe))))) = bVar1 && (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0xb3f))))) == '\0';
  return;
}

void thunk_derive_caff_cafe_group_status_gates_cefa4(void)

{
  derive_caff_cafe_group_status_gates_cefa4();
  return;
}

void set_angle_controller_mode_seven_ceff4(void)

{
  DAT_febecb00 = 7;
  return;
}

void select_angle_controller_mode(void)

{
  DAT_febecb00 = 7;
  if ((DAT_febeacbd == '\0') && (DAT_febecaff == '\x01')) {
    if (DAT_febeadb0 == '\x01') {
      DAT_febecb00 = 0;
    }
    else if (DAT_febeadb0 == '\x04') {
      DAT_febecb00 = 1;
    }
    else if (DAT_febeadb0 == '\n') {
      DAT_febecb00 = 3;
    }
    else if (DAT_febeadb0 == '\v') {
      DAT_febecb00 = 2;
    }
    else if (DAT_febeadb0 == '\x12') {
      DAT_febecb00 = 5;
    }
    else if (DAT_febeadb0 == '\x13') {
      DAT_febecb00 = 4;
    }
  }
  return;
}
