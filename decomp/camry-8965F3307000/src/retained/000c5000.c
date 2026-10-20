#include "common.h"

void initialize_torque_memory_gain(void)

{
  DAT_febec136 = 0;
  DAT_febec12c = 0x400;
  DAT_febec12e = 0x400;
  DAT_febec130 = 0x400;
  DAT_febec132 = 0x400;
  DAT_febec134 = 0x400;
  return;
}

void prepare_torque_memory_gain_parameters(F33GainSlewState *state,uint mode)

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
    uVar2 = (*((volatile uint16_t *)camry_host_ptr((uint32_t)((uint32_t)(0xd2fb8u + (uint32_t)(iVar1) * (uint32_t)sizeof(F33GainSlewCalibration)) + (uint32_t)(0) * (uint32_t)sizeof(F33GainSlewCalibration) + (uint32_t)offsetof(F33GainSlewCalibration, up_target)))));
    uVar6 = *((uint16_t *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)((uint32_t)(0xd2fb8u + (uint32_t)(iVar1) * (uint32_t)sizeof(F33GainSlewCalibration)) + (uint32_t)(0) * (uint32_t)sizeof(F33GainSlewCalibration) + (uint32_t)offsetof(F33GainSlewCalibration, down_step))))))));
    uVar5 = *((uint16_t *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)((uint32_t)(0xd2fb8u + (uint32_t)(iVar1) * (uint32_t)sizeof(F33GainSlewCalibration)) + (uint32_t)(0) * (uint32_t)sizeof(F33GainSlewCalibration) + (uint32_t)offsetof(F33GainSlewCalibration, up_step))))))));
    uVar4 = *((uint16_t *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)((uint32_t)(0xd2fb8u + (uint32_t)(iVar1) * (uint32_t)sizeof(F33GainSlewCalibration)) + (uint32_t)(0) * (uint32_t)sizeof(F33GainSlewCalibration) + (uint32_t)offsetof(F33GainSlewCalibration, down_target))))))));
  }
  else {
    uVar3 = '\x01';
    uVar2 = DAT_febec12c;
    uVar6 = DAT_febec130;
    uVar5 = DAT_febec132;
    uVar4 = DAT_febec12e;
  }
  state->down_step = uVar6;
  state->up_step = uVar5;
  state->down_target = uVar4;
  state->up_target = uVar2;
  state->direction = uVar3;
  return;
}

void update_torque_memory_gain(void)

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
  local_10.current = DAT_febec134;
  if (uVar3 < 7) {
    local_10.direction = '\x02';
    iVar1 = (short)(DAT_febeac3c & 1) * 7 + uVar3;
    local_10.up_target = (*((volatile uint16_t *)camry_host_ptr((uint32_t)((uint32_t)(0xd2fb8u + (uint32_t)(iVar1) * (uint32_t)sizeof(F33GainSlewCalibration)) + (uint32_t)(0) * (uint32_t)sizeof(F33GainSlewCalibration) + (uint32_t)offsetof(F33GainSlewCalibration, up_target)))));
    local_10.down_step = *((uint16_t *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)((uint32_t)(0xd2fb8u + (uint32_t)(iVar1) * (uint32_t)sizeof(F33GainSlewCalibration)) + (uint32_t)(0) * (uint32_t)sizeof(F33GainSlewCalibration) + (uint32_t)offsetof(F33GainSlewCalibration, down_step))))))));
    local_10.up_step = *((uint16_t *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)((uint32_t)(0xd2fb8u + (uint32_t)(iVar1) * (uint32_t)sizeof(F33GainSlewCalibration)) + (uint32_t)(0) * (uint32_t)sizeof(F33GainSlewCalibration) + (uint32_t)offsetof(F33GainSlewCalibration, up_step))))))));
    local_10.down_target = *((uint16_t *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)((uint32_t)(0xd2fb8u + (uint32_t)(iVar1) * (uint32_t)sizeof(F33GainSlewCalibration)) + (uint32_t)(0) * (uint32_t)sizeof(F33GainSlewCalibration) + (uint32_t)offsetof(F33GainSlewCalibration, down_target))))))));
  }
  else {
    local_10.direction = '\x01';
    local_10.up_target = DAT_febec12c;
    local_10.down_step = DAT_febec130;
    local_10.up_step = DAT_febec132;
    local_10.down_target = DAT_febec12e;
  }
  step_retained_unsigned_gain(&local_10);
  (*((ushort *)camry_host_ptr((uint32_t)(puVar2 + 0x930)))) = local_10.down_step;
  (*((ushort *)camry_host_ptr((uint32_t)(puVar2 + 0x932)))) = local_10.up_step;
  (*((ushort *)camry_host_ptr((uint32_t)(puVar2 + 0x92e)))) = local_10.down_target;
  (*((ushort *)camry_host_ptr((uint32_t)(puVar2 + 0x92c)))) = local_10.up_target;
  (*((ushort *)camry_host_ptr((uint32_t)(puVar2 + 0x934)))) = local_10.current;
  return;
}

short scale_torque_memory_correction(short value)

{
  DAT_febec136 = (short)((int)((uint)DAT_febec134 * (int)value) / 0x400);
  return DAT_febec136;
}

void initialize_torque_memory_correction(void)

{
  DAT_febec14e = 0;
  DAT_febec138 = 0;
  DAT_febec13c = 0;
  DAT_febec140 = 0;
  DAT_febec144 = 0;
  DAT_febec146 = 0;
  DAT_febec150 = 0;
  DAT_febec148 = 0;
  DAT_febec14a = 0;
  DAT_febec14c = 0;
  return;
}

void update_torque_memory_band_amplitude(void)

{
  uint uVar1;
  uint32_t puVar2;
  short input;
  undefined2 uVar3;
  int iVar4;
  
  puVar2 = 0xfebeb800u;
  uVar1 = (uint)DAT_febec156;
  input = abs_s16_wrapping(((int)(int16_t)DAT_febeac44));
  uVar3 = 0;
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0xbd5))))) != 'Z') {
    iVar4 = interpolate_signed_sentinel_curve
                      (((short *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xb144cu + (uint32_t)((byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0xbc4))))) & 1) * 4u)))) +
                                (uVar1 & 3) * 0x1c + 0x954))),input);
    uVar3 = (undefined2)iVar4;
  }
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar2 + 0x94a)))) = uVar3;
  return;
}

short update_torque_memory_correction(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  uint32_t puVar4;
  short sVar5;
  int iVar7;
  short sVar8;
  int iVar9;
  int iVar6;
  
  puVar4 = 0xfebeb800u;
  update_torque_memory_band_amplitude();
  sVar8 = DAT_000af81a;
  iVar9 = (int)DAT_000af81a;
  iVar6 = -(*((int *)camry_host_ptr((uint32_t)(puVar4 + -0xb70))));
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(0x94e))))) == '\0') {
    (*((int *)camry_host_ptr((uint32_t)(puVar4 + 0x93c)))) = iVar6;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(0x94e))))) = 1;
  }
  iVar2 = DAT_000af814 * (uint)(*((ushort *)camry_host_ptr((uint32_t)(puVar4 + -0xba2))));
  iVar1 = (*((int *)camry_host_ptr((uint32_t)(puVar4 + 0x93c)))) + (*((int *)camry_host_ptr((uint32_t)(puVar4 + -0xb70))));
  (*((int *)camry_host_ptr((uint32_t)(puVar4 + 0x938)))) = iVar1;
  iVar2 = iVar2 / 0x40000;
  if (iVar2 == 0) {
    iVar7 = 0;
  }
  else {
    iVar7 = (int)(*((short *)camry_host_ptr((uint32_t)(puVar4 + 0x94a))));
    iVar3 = iVar7 << 10;
    if (iVar2 != 0) {
      if (iVar3 == -0x80000000 && iVar2 == -1) {
        iVar3 = -0x80000000;
      }
      else {
        iVar3 = (int)iVar3 / (int)iVar2;
      }
    }
    if (iVar1 - iVar3 < 0 == (iVar1 < 0 != iVar3 < 0 && iVar3 < 0 == iVar1 - iVar3 < 0) &&
        iVar1 != iVar3) {
      (*((int *)camry_host_ptr((uint32_t)(puVar4 + 0x93c)))) = iVar3 + iVar6;
    }
    else if (iVar1 + iVar3 < 0 == (iVar1 < 0 != -iVar3 < 0 && -iVar3 < 0 == iVar1 + iVar3 < 0)) {
      iVar7 = (iVar1 * iVar2) / 0x400;
    }
    else {
      (*((int *)camry_host_ptr((uint32_t)(puVar4 + 0x93c)))) = iVar6 - iVar3;
      iVar7 = -iVar7;
    }
  }
  (*((int *)camry_host_ptr((uint32_t)(puVar4 + 0x940)))) = iVar7;
  sVar5 = scale_torque_memory_correction((short)( (int)((iVar7 * (*((short *)camry_host_ptr((uint32_t)(puVar4 + 0x948)))))) / (int)0x400));
  iVar6 = (int)sVar5;
  (*((short *)camry_host_ptr((uint32_t)(puVar4 + 0x944)))) = sVar5;
  if ((iVar6 - iVar9 < 0 != (iVar6 < 0 != iVar9 < 0 && iVar9 < 0 == iVar6 - iVar9 < 0) ||
       iVar6 == iVar9) &&
     (iVar1 = -iVar9, sVar8 = sVar5,
     iVar6 + iVar9 < 0 != (iVar6 < 0 != iVar1 < 0 && iVar1 < 0 == iVar6 + iVar9 < 0) ||
     iVar6 == iVar1)) {
    sVar8 = (short)iVar1;
  }
  (*((short *)camry_host_ptr((uint32_t)(puVar4 + 0x946)))) = sVar8;
  return sVar5;
}

void publish_bounded_assist_torque_input(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  
  iVar3 = (int)DAT_000af818;
  DAT_febec14c = ((int)(int16_t)DAT_febeac44) + ((int)(int16_t)DAT_febec146);
  iVar2 = (int)DAT_febec14c;
  DAT_febec150 = DAT_000af818;
  if ((iVar2 - iVar3 < 0 != (iVar2 < 0 != iVar3 < 0 && iVar3 < 0 == iVar2 - iVar3 < 0) ||
       iVar2 == iVar3) &&
     (iVar1 = -iVar3, DAT_febec150 = DAT_febec14c,
     iVar2 + iVar3 < 0 != (iVar2 < 0 != iVar1 < 0 && iVar1 < 0 == iVar2 + iVar3 < 0) ||
     iVar2 == iVar1)) {
    DAT_febec150 = (short)iVar1;
  }
  return;
}

void update_torque_memory_speed_gain(void)

{
  uint32_t puVar1;
  int iVar2;
  
  puVar1 = 0xfebeb800u;
  iVar2 = interpolate_unsigned_axis_sentinel_curve
                    (((ushort *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xb144cu + (uint32_t)(DAT_febeac3c & 1) * 4u)))) +
                     (DAT_febec156 & 3) * 0x24 + 0x8c4))),DAT_febeadf6);
  (*((short *)camry_host_ptr((uint32_t)(puVar1 + 0x948)))) = (short)iVar2;
  return;
}

void initialize_assist_surface_selection(void)

{
  DAT_febec154 = 0;
  DAT_febec152 = 0;
  DAT_febec158 = 0;
  DAT_febec156 = 0;
  return;
}

short qualify_assist_surface_transition(void)

{
  short sVar1;
  short sVar2;
  short sVar3;
  short sVar4;
  char cVar5;
  char cVar6;
  ushort uVar7;
  char cVar8;
  short value;
  short value_00;
  short value_01;
  uint32_t puVar9;
  short sVar10;
  short sVar11;
  int iVar13;
  int iVar15;
  int iVar16;
  int iVar17;
  int iVar18;
  int iVar19;
  undefined1 uVar20;
  short sVar21;
  int iVar12;
  int iVar14;
  
  value_01 = ((int)(int16_t)DAT_febec266);
  value_00 = ((int)(int16_t)DAT_febec23c);
  value = ((int)(int16_t)DAT_febec1a2);
  cVar8 = DAT_febec158;
  uVar20 = DAT_febec154;
  uVar7 = DAT_febec152;
  sVar11 = ((int)(int16_t)DAT_febec150);
  iVar13 = DAT_febec124;
  cVar6 = DAT_febead5f;
  cVar5 = DAT_febead18;
  sVar4 = DAT_000b1170;
  sVar3 = DAT_000b116e;
  sVar2 = DAT_000b116c;
  sVar1 = DAT_000b116a;
  sVar21 = DAT_000b1168;
  iVar19 = DAT_000b1164;
  puVar9 = 0xfebeb800u;
  sVar10 = abs_s16_wrapping(((int)(int16_t)DAT_febeadf2));
  iVar12 = (int)sVar10;
  iVar13 = abs_s32_wrapping(iVar13);
  sVar11 = abs_s16_wrapping(sVar11);
  iVar14 = (int)sVar11;
  sVar11 = abs_s16_wrapping(value_00);
  iVar15 = (int)sVar11;
  sVar11 = abs_s16_wrapping(value_01);
  iVar16 = (int)sVar11;
  sVar11 = abs_s16_wrapping(value);
  iVar17 = (int)sVar11;
  if ((((((cVar5 == 'D') && (cVar8 != 'U')) || ((cVar6 == '\x11' && (cVar8 != 'w')))) ||
       (((cVar6 == '\"' && (cVar8 != 'D')) || ((cVar6 == '3' && (((int8_t)cVar8) != -0x78)))))) ||
      ((cVar6 == '\0' && (cVar8 != '\0')))) &&
     (iVar18 = (int)sVar21,
     iVar12 - iVar18 < 0 != (iVar12 < 0 != iVar18 < 0 && iVar18 < 0 == iVar12 - iVar18 < 0) ||
     iVar12 == iVar18)) {
    if ((((iVar13 - iVar19 < 0 != (iVar13 < 0 != iVar19 < 0 && iVar19 < 0 == iVar13 - iVar19 < 0) ||
           iVar13 == iVar19) &&
         (iVar19 = (int)sVar1,
         iVar14 - iVar19 < 0 != (iVar14 < 0 != iVar19 < 0 && iVar19 < 0 == iVar14 - iVar19 < 0) ||
         iVar14 == iVar19)) &&
        (iVar19 = (int)sVar3,
        iVar15 - iVar19 < 0 != (iVar15 < 0 != iVar19 < 0 && iVar19 < 0 == iVar15 - iVar19 < 0) ||
        iVar15 == iVar19)) &&
       ((iVar19 = (int)sVar2,
        iVar16 - iVar19 < 0 != (iVar16 < 0 != iVar19 < 0 && iVar19 < 0 == iVar16 - iVar19 < 0) ||
        iVar16 == iVar19 &&
        (iVar19 = (int)sVar4,
        iVar17 - iVar19 < 0 != (iVar17 < 0 != iVar19 < 0 && iVar19 < 0 == iVar17 - iVar19 < 0) ||
        iVar17 == iVar19)))) {
      if (uVar7 < DAT_000b1172) {
        sVar21 = uVar7 + 1;
      }
      else {
        sVar21 = 0;
        uVar20 = 0x5a;
      }
      goto LAB_000c5496;
    }
  }
  sVar21 = 0;
  uVar20 = 0;
LAB_000c5496:
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar9 + (uint32_t)(0x954))))) = uVar20;
  (*((short *)camry_host_ptr((uint32_t)(puVar9 + 0x952)))) = sVar21;
  return sVar10;
}

void update_retained_assist_surface_source(void)

{
  if (DAT_febeac2b == 'Z') {
    DAT_febec158 = 0x66;
  }
  else if (DAT_febeac94 == 0x5aa5a55a) {
    DAT_febec158 = 0x11;
  }
  else {
    if (((((DAT_febeac9c == -0x5aa5a55b) && (DAT_febeac98 == -0x5aa5a55b)) &&
         (DAT_febeaca8 == -0x5aa5a55b)) &&
        ((DAT_febeaca4 == -0x5aa5a55b && (DAT_febeaca0 == -0x5aa5a55b)))) &&
       (((DAT_febeac50 & 0x19c) == 0 && (((DAT_febeac50 & 0x60) == 0 && ((DAT_febeac50 & 3) == 0))))
       )) {
      if (DAT_febec154 != 'Z') {
        return;
      }
      if ((DAT_febeac30 == 'D') && (DAT_febeac40 != 'Z')) {
        DAT_febec158 = 0x55;
        return;
      }
      if (DAT_febeac2f == '\x11') {
        DAT_febec158 = 0x77;
        return;
      }
      if (DAT_febeac2f == '\"') {
        DAT_febec158 = 0x44;
        return;
      }
      if (DAT_febeac2f == '3') {
        DAT_febec158 = 0x88;
        return;
      }
    }
    DAT_febec158 = 0;
  }
  return;
}

void publish_assist_surface_selector(void)

{
  undefined2 uVar1;
  
  DAT_febec156 = 0;
  uVar1 = 1;
  if (((DAT_febec158 == 'w') || (uVar1 = 2, DAT_febec158 == 'D')) ||
     (uVar1 = 3, ((int8_t)DAT_febec158) == -0x78)) {
    DAT_febec156 = uVar1;
  }
  return;
}

void reset_ac88_delta_filter_and_seed_gain_c557a(void)

{
  DAT_febec168 = 0;
  DAT_febec16a = 0;
  DAT_febec16c = 0;
  DAT_febec15c = 0;
  DAT_febec160 = 0;
  DAT_febec164 = 0;
  DAT_febec172 = 0;
  DAT_febec170 = 0;
  DAT_febec16e = (short)((uint)DAT_febeae3a * 0xdbba + 0x8000 >> 0x10);
  return;
}

void compute_saturated_ac88_delta_after_first_sample_c55b4(void)

{
  int iVar1;
  
  if (DAT_febec170 == '\0') {
    DAT_febec170 = '\x01';
    iVar1 = 0;
  }
  else {
    iVar1 = DAT_febeac88 - DAT_febec164;
    if (iVar1 + -0x7fff < 0 == (iVar1 < 0 && -1 < iVar1 + -0x7fff) && iVar1 != 0x7fff) {
      iVar1 = 0x7fff;
    }
    else if (iVar1 + 0x7fff < 0 != (-1 < iVar1 && iVar1 + 0x7fff < 0)) {
      iVar1 = -0x7fff;
    }
  }
  DAT_febec168 = (short)iVar1;
  DAT_febec164 = DAT_febeac88;
  return;
}

void filter_ac88_delta_twice_scale_clamp_and_negate_c55ee(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  
  DAT_febec15c = (DAT_febec15c + ((int)(int16_t)DAT_febec168)) - (int)((int)(int16_t)DAT_febec16a);
  iVar2 = DAT_febec15c * 0x400;
  if (DAT_000afab0 != 0) {
    if (iVar2 == -0x80000000 && DAT_000afab0 == -1) {
      iVar2 = 0;
    }
    else {
      iVar2 = iVar2 / (int)DAT_000afab0;
    }
  }
  DAT_febec16a = (short)iVar2;
  DAT_febec160 = (DAT_febec160 + (short)iVar2) - (int)((int)(int16_t)DAT_febec16c);
  iVar2 = DAT_febec160 * 0x400;
  if (DAT_000afab4 != 0) {
    if (iVar2 == -0x80000000 && DAT_000afab4 == -1) {
      iVar2 = 0;
    }
    else {
      iVar2 = iVar2 / (int)DAT_000afab4;
    }
  }
  DAT_febec16c = (short)iVar2;
  iVar2 = ((int)((int)(int16_t)DAT_febec16e) * (int)(short)iVar2) / 0x1000;
  iVar3 = (int)DAT_000afab8;
  iVar4 = (int)DAT_000afab8;
  if ((iVar2 - iVar3 < 0 != (iVar2 < 0 != iVar3 < 0 && iVar3 < 0 == iVar2 - iVar3 < 0) ||
       iVar2 == iVar3) &&
     (iVar1 = -iVar4, iVar3 = iVar2 + iVar4, iVar4 = iVar2,
     iVar3 < 0 != (iVar2 < 0 != iVar1 < 0 && iVar1 < 0 == iVar3 < 0))) {
    iVar4 = -(int)DAT_000afab8;
  }
  DAT_febec172 = -(short)iVar4;
  return;
}

void refresh_c16e_gain_from_ae3a_c566c(void)

{
  DAT_febec16e = (short)((uint)DAT_febeae3a * 0xdbba + 0x8000 >> 0x10);
  return;
}

void reset_ac14_delta_filter_c174_and_seed_gain_c5686(void)

{
  DAT_febec180 = 0;
  DAT_febec182 = 0;
  DAT_febec184 = 0;
  DAT_febec174 = 0;
  DAT_febec178 = 0;
  DAT_febec17c = 0;
  DAT_febec18a = 0;
  DAT_febec186 = (ushort)((uint)DAT_febeae3a * 90000 + 0x20000 >> 0x12);
  DAT_febec188 = 0;
  return;
}

void compute_saturated_ac14_delta_into_c180_c56c0(void)

{
  int iVar1;
  
  if (DAT_febec188 == '\0') {
    DAT_febec188 = '\x01';
    iVar1 = 0;
  }
  else {
    iVar1 = DAT_febeac14 - DAT_febec17c;
    if (iVar1 + -0x7fff < 0 == (iVar1 < 0 && -1 < iVar1 + -0x7fff) && iVar1 != 0x7fff) {
      iVar1 = 0x7fff;
    }
    else if (iVar1 + 0x7fff < 0 != (-1 < iVar1 && iVar1 + 0x7fff < 0)) {
      iVar1 = -0x7fff;
    }
  }
  DAT_febec180 = (short)iVar1;
  DAT_febec17c = DAT_febeac14;
  return;
}

void filter_c180_delta_twice_scale_clamp_and_negate_c56fa(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  
  DAT_febec174 = (DAT_febec174 + ((int)(int16_t)DAT_febec180)) - (int)((int)(int16_t)DAT_febec182);
  iVar2 = DAT_febec174 * 0x400;
  if (DAT_000afabc != 0) {
    if (iVar2 == -0x80000000 && DAT_000afabc == -1) {
      iVar2 = 0;
    }
    else {
      iVar2 = iVar2 / (int)DAT_000afabc;
    }
  }
  DAT_febec182 = (short)iVar2;
  DAT_febec178 = (DAT_febec178 + (short)iVar2) - (int)((int)(int16_t)DAT_febec184);
  iVar2 = DAT_febec178 * 0x400;
  if (DAT_000afac0 != 0) {
    if (iVar2 == -0x80000000 && DAT_000afac0 == -1) {
      iVar2 = 0;
    }
    else {
      iVar2 = iVar2 / (int)DAT_000afac0;
    }
  }
  DAT_febec184 = (short)iVar2;
  iVar2 = ((int)((int)(int16_t)DAT_febec186) * (int)(short)iVar2) / 0x1000;
  iVar3 = (int)DAT_000afac4;
  iVar4 = (int)DAT_000afac4;
  if ((iVar2 - iVar3 < 0 != (iVar2 < 0 != iVar3 < 0 && iVar3 < 0 == iVar2 - iVar3 < 0) ||
       iVar2 == iVar3) &&
     (iVar1 = -iVar4, iVar3 = iVar2 + iVar4, iVar4 = iVar2,
     iVar3 < 0 != (iVar2 < 0 != iVar1 < 0 && iVar1 < 0 == iVar3 < 0))) {
    iVar4 = -(int)DAT_000afac4;
  }
  DAT_febec18a = -(short)iVar4;
  return;
}

void refresh_c186_gain_from_ae3a_c5778(void)

{
  DAT_febec186 = (ushort)((uint)DAT_febeae3a * 90000 + 0x20000 >> 0x12);
  return;
}

void reset_ac14_delta_filter_c18c_and_seed_gain_c5792(void)

{
  DAT_febec198 = 0;
  DAT_febec19a = 0;
  DAT_febec19c = 0;
  DAT_febec18c = 0;
  DAT_febec190 = 0;
  DAT_febec194 = 0;
  DAT_febec1a2 = 0;
  DAT_febec19e = (ushort)((uint)DAT_febeae3a * 90000 + 0x20000 >> 0x12);
  DAT_febec1a0 = 0;
  return;
}

void compute_saturated_ac14_delta_into_c198_c57cc(void)

{
  int iVar1;
  
  if (DAT_febec1a0 == '\0') {
    DAT_febec1a0 = '\x01';
    iVar1 = 0;
  }
  else {
    iVar1 = DAT_febeac14 - DAT_febec194;
    if (iVar1 + -0x7fff < 0 == (iVar1 < 0 && -1 < iVar1 + -0x7fff) && iVar1 != 0x7fff) {
      iVar1 = 0x7fff;
    }
    else if (iVar1 + 0x7fff < 0 != (-1 < iVar1 && iVar1 + 0x7fff < 0)) {
      iVar1 = -0x7fff;
    }
  }
  DAT_febec198 = (short)iVar1;
  DAT_febec194 = DAT_febeac14;
  return;
}

void filter_c198_delta_twice_scale_clamp_and_negate_c5806(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  
  DAT_febec18c = (DAT_febec18c + ((int)(int16_t)DAT_febec198)) - (int)((int)(int16_t)DAT_febec19a);
  iVar2 = DAT_febec18c * 0x400;
  if (DAT_000afac8 != 0) {
    if (iVar2 == -0x80000000 && DAT_000afac8 == -1) {
      iVar2 = 0;
    }
    else {
      iVar2 = iVar2 / (int)DAT_000afac8;
    }
  }
  DAT_febec19a = (short)iVar2;
  DAT_febec190 = (DAT_febec190 + (short)iVar2) - (int)((int)(int16_t)DAT_febec19c);
  iVar2 = DAT_febec190 * 0x400;
  if (DAT_000afacc != 0) {
    if (iVar2 == -0x80000000 && DAT_000afacc == -1) {
      iVar2 = 0;
    }
    else {
      iVar2 = iVar2 / (int)DAT_000afacc;
    }
  }
  DAT_febec19c = (short)iVar2;
  iVar2 = ((int)((int)(int16_t)DAT_febec19e) * (int)(short)iVar2) / 0x1000;
  iVar3 = (int)DAT_000afad0;
  iVar4 = (int)DAT_000afad0;
  if ((iVar2 - iVar3 < 0 != (iVar2 < 0 != iVar3 < 0 && iVar3 < 0 == iVar2 - iVar3 < 0) ||
       iVar2 == iVar3) &&
     (iVar1 = -iVar4, iVar3 = iVar2 + iVar4, iVar4 = iVar2,
     iVar3 < 0 != (iVar2 < 0 != iVar1 < 0 && iVar1 < 0 == iVar3 < 0))) {
    iVar4 = -(int)DAT_000afad0;
  }
  DAT_febec1a2 = -(short)iVar4;
  return;
}

void refresh_c19e_gain_from_ae3a_c5884(void)

{
  DAT_febec19e = (ushort)((uint)DAT_febeae3a * 90000 + 0x20000 >> 0x12);
  return;
}

void fill_constant_block_c589e(void)

{
  DAT_febec1a4 = 0;
  DAT_febec1a6 = 0;
  DAT_febec1a8 = 0;
  DAT_febec1aa = 0;
  DAT_febec1ac = 0;
  DAT_febec1ae = 0;
  return;
}

undefined4 lookup_c1a4_axis_index_and_fraction_from_bank_c58b8(void)

{
  uint8_t stack_record_8[8];
  uint32_t puVar1;
  undefined4 uVar2;
  
  puVar1 = 0xfebeb800u;
  locate_unsigned16_axis_interval_and_q10_fraction_d097a(((ushort *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xb144cu + (uint32_t)(DAT_febeac3c & 1) * 4u)))) + (DAT_febec156 & 3) * 0x12 + 0x9c4))), 
               DAT_febeadf6, ((uint16_t *)(stack_record_8)), ((uint16_t *)((stack_record_8 + 2))));
  uVar2 = raise_priority_mask_and_return_previous_d1da0(0xffc0);
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + 0x9a4)))) = (*((uint16_t *)(stack_record_8 + 0)));
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + 0x9a6)))) = (*((uint16_t *)(stack_record_8 + 2)));
  restore_priority_mask_preserving_interrupt_enable_d1dc6(uVar2);
  return uVar2;
}

undefined4 lookup_c1a8_axis_index_and_fraction_from_pointer_table_c5910(void)

{
  uint8_t stack_record_8[8];
  uint32_t puVar1;
  undefined4 uVar2;
  
  puVar1 = 0xfebeb800u;
  locate_unsigned16_axis_interval_and_q10_fraction_d097a(((ushort *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd30e8u + (uint32_t)(DAT_febec156 & 3) * 4u))))))), DAT_febeadf6, ((uint16_t *)(stack_record_8)), ((uint16_t *)((stack_record_8 + 2))));
  uVar2 = raise_priority_mask_and_return_previous_d1da0(0xffc0);
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + 0x9a8)))) = (*((uint16_t *)(stack_record_8 + 0)));
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + 0x9aa)))) = (*((uint16_t *)(stack_record_8 + 2)));
  restore_priority_mask_preserving_interrupt_enable_d1dc6(uVar2);
  return uVar2;
}

undefined4 lookup_c1ac_axis_index_and_fraction_from_bank_c5956(void)

{
  uint8_t stack_record_8[8];
  uint32_t puVar1;
  undefined4 uVar2;
  
  puVar1 = 0xfebeb800u;
  locate_unsigned16_axis_interval_and_q10_fraction_d097a(((ushort *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xb144cu + (uint32_t)(DAT_febeac3c & 1) * 4u)))) + (DAT_febec156 & 3) * 0x12 + 0xa0c))), 
               DAT_febeadf6, ((uint16_t *)(stack_record_8)), ((uint16_t *)((stack_record_8 + 2))));
  uVar2 = raise_priority_mask_and_return_previous_d1da0(0xffc0);
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + 0x9ac)))) = (*((uint16_t *)(stack_record_8 + 0)));
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + 0x9ae)))) = (*((uint16_t *)(stack_record_8 + 2)));
  restore_priority_mask_preserving_interrupt_enable_d1dc6(uVar2);
  return uVar2;
}

void fill_constant_block_c59ae(void)

{
  DAT_febec200 = 0;
  DAT_febec202 = 0;
  DAT_febec204 = 0;
  DAT_febec206 = 0;
  DAT_febec1b0 = 0;
  DAT_febec1b4 = 0;
  DAT_febec20a = 0;
  DAT_febec1c0 = 0;
  DAT_febec1c4 = 0;
  DAT_febec1c8 = 0;
  DAT_febec1cc = 0;
  DAT_febec1d0 = 0;
  DAT_febec1d4 = 0;
  DAT_febec1d8 = 0;
  DAT_febec20e = 0;
  DAT_febec1dc = 0;
  DAT_febec1e0 = 0;
  DAT_febec1e4 = 0;
  DAT_febec1e8 = 0;
  DAT_febec1ec = 0;
  DAT_febec20c = 0;
  DAT_febec210 = 0;
  DAT_febec23c = 0;
  DAT_febec212 = 0;
  DAT_febec214 = 0;
  DAT_febec216 = 0;
  DAT_febec218 = 0;
  DAT_febec1f0 = 0;
  DAT_febec1f4 = 0;
  DAT_febec21e = 0;
  DAT_febec23e = 0;
  DAT_febec220 = 0;
  DAT_febec224 = 0;
  DAT_febec226 = 0;
  DAT_febec1f8 = 0;
  DAT_febec1fc = 0;
  DAT_febec238 = 0;
  DAT_febec239 = 0;
  DAT_febec208 = 0;
  DAT_febec1b8 = 0;
  DAT_febec1bc = 0;
  DAT_febec21a = 0;
  DAT_febec222 = 0;
  DAT_febec21c = 0;
  DAT_febec228 = 0;
  DAT_febec23a = 0;
  DAT_febec22a = 0;
  DAT_febec22c = 0;
  DAT_febec22e = 0;
  DAT_febec230 = 0;
  DAT_febec232 = 0;
  DAT_febec234 = 0;
  DAT_febec236 = 0;
  return;
}

void step_banked_second_order_recurrence_and_c204_delta_c5a84(void)

{
  bool bVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  short sVar6;
  int iVar7;
  int *piVar8;
  
  iVar5 = (int)((int)(int16_t)DAT_febec22c);
  iVar7 = (int)DAT_000afb20;
  DAT_febec1d4 = DAT_febec1c8;
  DAT_febec1d8 = DAT_febec1cc;
  DAT_febec234 = 0;
  sVar6 = DAT_000afb20;
  if ((iVar5 - iVar7 < 0 != (iVar5 < 0 != iVar7 < 0 && iVar7 < 0 == iVar5 - iVar7 < 0) ||
       iVar5 == iVar7) &&
     (iVar7 = iVar5 + DAT_000afb20, bVar1 = -(int)DAT_000afb20 < 0, sVar6 = ((int)(int16_t)DAT_febec22c),
     iVar7 < 0 != (iVar5 < 0 != bVar1 && bVar1 == iVar7 < 0))) {
    sVar6 = -DAT_000afb20;
  }
  piVar8 = ((int *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xb1454u + (uint32_t)(DAT_febeac3c & 1) * 4u))))));
  iVar4 = *piVar8;
  iVar5 = DAT_febec1c0 - (iVar4 * ((int)(int16_t)DAT_febec22a) - piVar8[1] * (int)((int)(int16_t)DAT_febec22e)) / 2;
  iVar7 = DAT_febec1c8 - (int)(( (int)((DAT_febec1d0 * (*((short *)camry_host_ptr((uint32_t)((int)camry_host_addr(piVar8) + 10)))))) / (int)2 + (int)(((short)piVar8[2] * DAT_febec1cc)) / (int)2 + DAT_febec1c0)) / (int)0x800;
  iVar2 = (int)((int)(int16_t)DAT_febec20a) - (int)(short)( (int)(DAT_febec1c8) / (int)0x40);
  iVar3 = -DAT_000afb08;
  if (-(int)DAT_000afb08 < iVar5 && iVar5 < (int)DAT_000afb08 &&
      -(int)DAT_000afb0c < iVar7 && iVar7 < (int)DAT_000afb0c &&
      -(int)DAT_000afb18 < iVar2 && iVar2 < (int)DAT_000afb18) {
    DAT_febec1c0 = (iVar4 * ((int)(int16_t)DAT_febeac44) - piVar8[1] * (int)sVar6) / 2;
    iVar5 = (int)(((*((short *)camry_host_ptr((uint32_t)((int)camry_host_addr(piVar8) + 10)))) * DAT_febec1cc)) / (int)2 + (int)(((short)piVar8[2] * DAT_febec1c8)) / (int)2 + DAT_febec1c0;
  }
  else {
    DAT_febec234 = 1;
    DAT_febec1c0 = (iVar4 * ((int)(int16_t)DAT_febeac44)) / 2;
    iVar5 = DAT_febec1c0;
  }
  DAT_febec1c4 = iVar5 / 0x800;
  DAT_febec1d0 = DAT_febec1cc;
  DAT_febec1cc = DAT_febec1c8;
  DAT_febec1c8 = DAT_febec1c4;
  DAT_febec208 = ((int)(int16_t)DAT_febec200);
  DAT_febec20a = (short)((int)DAT_febec1c4 / 0x40);
  DAT_febec23a = DAT_febec238;
  if (DAT_febec238 == '\0') {
    DAT_febec238 = '\x01';
    DAT_febec1b8 = 0;
  }
  else {
    DAT_febec1b8 = (int)((int)(int16_t)DAT_febec20a) - (int)((int)(int16_t)DAT_febec200);
  }
  DAT_febec1b0 = (int)((DAT_febec1b8 * 0x4e2)) / (int)0x10;
  if ((int)DAT_febec1b0 + -0x7fff < 0 == ((int)DAT_febec1b0 < 0 && -1 < (int)DAT_febec1b0 + -0x7fff) &&
      ((int)(int32_t)DAT_febec1b0) != 0x7fff) {
    DAT_febec204 = 0x7fff;
  }
  else {
    DAT_febec204 = (undefined2)((int)(int32_t)DAT_febec1b0);
    if ((int)DAT_febec1b0 + 0x7fff < 0 != (-1 < (int)DAT_febec1b0 && (int)DAT_febec1b0 + 0x7fff < 0)) {
      DAT_febec204 = 0x8001;
    }
  }
  DAT_febec200 = ((int)(int16_t)DAT_febec20a);
  DAT_febec236 = DAT_febec236 | DAT_febec234;
  return;
}

void step_fixed_second_order_recurrence_and_c206_delta_c5c44(void)

{
  bool bVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  short sVar5;
  ushort uVar6;
  int iVar7;
  short sVar8;
  int iVar9;
  
  sVar5 = ((int)(int16_t)DAT_febec22a);
  iVar4 = DAT_febec1e4;
  iVar7 = (int)((int)(int16_t)DAT_febec22c);
  iVar9 = (int)DAT_000afb20;
  uVar6 = 0;
  sVar8 = DAT_000afb20;
  if ((iVar7 - iVar9 < 0 != (iVar7 < 0 != iVar9 < 0 && iVar9 < 0 == iVar7 - iVar9 < 0) ||
       iVar7 == iVar9) &&
     (iVar9 = iVar7 + DAT_000afb20, bVar1 = -(int)DAT_000afb20 < 0, sVar8 = ((int)(int16_t)DAT_febec22c),
     iVar9 < 0 != (iVar7 < 0 != bVar1 && bVar1 == iVar9 < 0))) {
    sVar8 = -DAT_000afb20;
  }
  iVar7 = DAT_febec1dc -
          ((int)PTR_DAT_000af824 * (int)((int)(int16_t)DAT_febec22a) - (int)PTR_DAT_000af828 * (int)((int)(int16_t)DAT_febec22e)) /
          2;
  iVar9 = DAT_febec1e4 - (int)(( (int)((DAT_febec1ec * DAT_000af838)) / (int)2 + (int)((DAT_000af836 * DAT_febec1e8)) / (int)2 + DAT_febec1dc)) / (int)0x800;
  iVar2 = (int)((int)(int16_t)DAT_febec20e) - (int)(short)( (int)(DAT_febec1e4) / (int)0x40);
  iVar3 = -DAT_000afb10;
  if (-(int)DAT_000afb10 < iVar7 && iVar7 < (int)DAT_000afb10 &&
      -(int)DAT_000afb14 < iVar9 && iVar9 < (int)DAT_000afb14 &&
      -(int)DAT_000afb1c < iVar2 && iVar2 < (int)DAT_000afb1c) {
    DAT_febec1dc = ((int)PTR_DAT_000af824 * (int)((int)(int16_t)DAT_febeac44) - (int)PTR_DAT_000af828 * (int)sVar8)
                   / 2;
    iVar7 = (int)((DAT_000af838 * DAT_febec1e8)) / (int)2 + (int)((DAT_000af836 * DAT_febec1e4)) / (int)2 + DAT_febec1dc;
  }
  else {
    uVar6 = 2;
    DAT_febec1dc = ((int)PTR_DAT_000af824 * (int)((int)(int16_t)DAT_febeac44)) / 2;
    iVar7 = DAT_febec1dc;
  }
  DAT_febec1e0 = iVar7 / 0x800;
  DAT_febec22a = ((int)(int16_t)DAT_febeac44);
  DAT_febec1ec = DAT_febec1e8;
  DAT_febec1e4 = DAT_febec1e0;
  DAT_febec1e8 = iVar4;
  DAT_febec20e = (short)( (int)(DAT_febec1e0) / (int)0x40);
  DAT_febec22e = ((int)(int16_t)DAT_febec22c);
  DAT_febec22c = sVar5;
  DAT_febec218 = ((int)(int16_t)DAT_febeac44) - (short)(((int)((int)(int16_t)DAT_febec20c) * (int)((int)(int16_t)DAT_febec20e)) / 0x400);
  if (DAT_febec239 == '\0') {
    DAT_febec239 = '\x01';
    DAT_febec1bc = 0;
  }
  else {
    DAT_febec1bc = (int)DAT_febec218 - (int)((int)(int16_t)DAT_febec202);
  }
  DAT_febec1b4 = (int)((DAT_febec1bc * 0x4e2)) / (int)0x10;
  if ((int)DAT_febec1b4 + -0x7fff < 0 == ((int)DAT_febec1b4 < 0 && -1 < (int)DAT_febec1b4 + -0x7fff) &&
      ((int)(int32_t)DAT_febec1b4) != 0x7fff) {
    DAT_febec206 = 0x7fff;
  }
  else {
    DAT_febec206 = (undefined2)((int)(int32_t)DAT_febec1b4);
    if ((int)DAT_febec1b4 + 0x7fff < 0 != (-1 < (int)DAT_febec1b4 && (int)DAT_febec1b4 + 0x7fff < 0)) {
      DAT_febec206 = 0x8001;
    }
  }
  DAT_febec202 = DAT_febec218;
  DAT_febec234 = DAT_febec234 | uVar6;
  DAT_febec236 = DAT_febec236 | uVar6;
  return;
}

void filter_c204_through_two_stages_and_bound_c23c_c5e24(void)

{
  bool bVar1;
  int iVar2;
  int iVar3;
  
  DAT_febec21c = ((int)(int16_t)DAT_febec216);
  DAT_febec1f0 = (((int)(int16_t)DAT_febec204) + DAT_febec1f0) - (int)((int)(int16_t)DAT_febec212);
  iVar3 = DAT_febec1f0 * 0x400;
  if (DAT_000af81c != 0) {
    if (iVar3 == -0x80000000 && DAT_000af81c == -1) {
      iVar3 = 0;
    }
    else {
      iVar3 = iVar3 / (int)DAT_000af81c;
    }
  }
  iVar2 = (int)DAT_000af834;
  DAT_febec212 = (short)iVar3;
  DAT_febec21a = ((int)(int16_t)DAT_febec210);
  DAT_febec1f4 = (DAT_febec1f4 + ((int)(int16_t)DAT_febec212)) - (int)((int)(int16_t)DAT_febec214);
  iVar3 = DAT_febec1f4 * 0x400;
  if (DAT_000af820 != 0) {
    if (iVar3 == -0x80000000 && DAT_000af820 == -1) {
      iVar3 = 0;
    }
    else {
      iVar3 = iVar3 / (int)DAT_000af820;
    }
  }
  DAT_febec214 = (short)iVar3;
  iVar3 = (int)((int)(int16_t)DAT_febec214);
  DAT_febec23c = DAT_000af834;
  if ((iVar3 - iVar2 < 0 != (iVar3 < 0 != iVar2 < 0 && iVar2 < 0 == iVar3 - iVar2 < 0) ||
       iVar3 == iVar2) &&
     (iVar2 = iVar3 + DAT_000af834, bVar1 = -(int)DAT_000af834 < 0, DAT_febec23c = ((int)(int16_t)DAT_febec214),
     iVar2 < 0 != (iVar3 < 0 != bVar1 && bVar1 == iVar2 < 0))) {
    DAT_febec23c = -DAT_000af834;
  }
  DAT_febec210 = ((int)(int16_t)DAT_febec212);
  DAT_febec216 = ((int)(int16_t)DAT_febec214);
  return;
}

void filter_c206_through_two_stages_and_bound_c23e_c5eae(void)

{
  bool bVar1;
  int iVar2;
  int iVar3;
  
  DAT_febec228 = ((int)(int16_t)DAT_febec226);
  DAT_febec1f8 = (((int)(int16_t)DAT_febec206) + DAT_febec1f8) - (int)((int)(int16_t)DAT_febec220);
  iVar3 = DAT_febec1f8 * 0x400;
  if (DAT_000af82c != 0) {
    if (iVar3 == -0x80000000 && DAT_000af82c == -1) {
      iVar3 = 0;
    }
    else {
      iVar3 = iVar3 / (int)DAT_000af82c;
    }
  }
  iVar2 = (int)DAT_000af83a;
  DAT_febec220 = (short)iVar3;
  DAT_febec222 = ((int)(int16_t)DAT_febec21e);
  DAT_febec1fc = (DAT_febec1fc + ((int)(int16_t)DAT_febec220)) - (int)((int)(int16_t)DAT_febec224);
  iVar3 = DAT_febec1fc * 0x400;
  if (DAT_000af830 != 0) {
    if (iVar3 == -0x80000000 && DAT_000af830 == -1) {
      iVar3 = 0;
    }
    else {
      iVar3 = iVar3 / (int)DAT_000af830;
    }
  }
  DAT_febec224 = (short)iVar3;
  iVar3 = (int)((int)(int16_t)DAT_febec224);
  DAT_febec23e = DAT_000af83a;
  if ((iVar3 - iVar2 < 0 != (iVar3 < 0 != iVar2 < 0 && iVar2 < 0 == iVar3 - iVar2 < 0) ||
       iVar3 == iVar2) &&
     (iVar2 = iVar3 + DAT_000af83a, bVar1 = -(int)DAT_000af83a < 0, DAT_febec23e = ((int)(int16_t)DAT_febec224),
     iVar2 < 0 != (iVar3 < 0 != bVar1 && bVar1 == iVar2 < 0))) {
    DAT_febec23e = -DAT_000af83a;
  }
  DAT_febec21e = ((int)(int16_t)DAT_febec220);
  DAT_febec226 = ((int)(int16_t)DAT_febec224);
  return;
}

void interpolate_af83c_curve_into_c20c_c5f38(void)

{
  uint32_t puVar1;
  int iVar2;
  
  puVar1 = 0xfebeb800u;
  iVar2 = interpolate_unsigned_axis_sentinel_curve((ushort *)((undefined *)camry_host_ptr(0xaf83cu)),DAT_febeadf6);
  (*((short *)camry_host_ptr((uint32_t)(puVar1 + 0xa0c)))) = (short)iVar2;
  return;
}

void reconcile_c1f0_c1f4_filter_states_and_latch_flags_c5f52(void)

{
  int delta;
  int scaled;
  int product;
  int bound;
  ushort flags;
  
  flags = 0;
  delta = (int)(short)DAT_febec210 - (int)(short)DAT_febec212;
  scaled = (int)(DAT_febec1f0 << 10);
  if (delta > -(int)DAT_000afae8 && delta < (int)DAT_000afae8) {
    product = (int)(short)DAT_febec212 * (int)DAT_000af81c;
    bound = (int)DAT_000afaec * (int)DAT_000af81c;
    delta = product - scaled;
    if (delta <= -bound || delta >= bound) {
      DAT_febec1f0 = (uint)(product / 0x400);
      flags = 1;
    }
  }
  else {
    if ((int)DAT_000af81c != 0) {
      if (scaled == (int)0x80000000 && (int)DAT_000af81c == -1) {
        scaled = 0;
      }
      else {
        scaled = scaled / (int)DAT_000af81c;
      }
    }
    flags = 2;
    DAT_febec212 = (short)scaled;
  }
  delta = (int)(short)DAT_febec216 - (int)(short)DAT_febec214;
  scaled = (int)(DAT_febec1f4 << 10);
  if (delta > -(int)DAT_000afaf0 && delta < (int)DAT_000afaf0) {
    product = (int)(short)DAT_febec214 * (int)DAT_000af820;
    bound = (int)DAT_000afaf4 * (int)DAT_000af820;
    delta = product - scaled;
    if (delta <= -bound || delta >= bound) {
      DAT_febec1f4 = (uint)(product / 0x400);
      flags = flags | 4;
    }
  }
  else {
    if ((int)DAT_000af820 != 0) {
      if (scaled == (int)0x80000000 && (int)DAT_000af820 == -1) {
        scaled = 0;
      }
      else {
        scaled = scaled / (int)DAT_000af820;
      }
    }
    flags = flags | 8;
    DAT_febec214 = (short)scaled;
  }
  DAT_febec230 = flags;
  DAT_febec232 = DAT_febec232 | flags;
  return;
}
