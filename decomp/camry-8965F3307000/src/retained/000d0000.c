#include "common.h"

void update_bounded_error_integrator_and_windowed_output_d0030(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  
  iVar2 = -DAT_febeac24;
  DAT_febecc22 = (short)(*((int *)camry_host_ptr((uint32_t)((int)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xb148cu + (uint32_t)(DAT_febeac3c & 1) * 4u)))) + 8))));
  iVar1 = (int)DAT_febecc22;
  if (DAT_febecc20 == '\0') {
    DAT_febecc20 = '\x01';
    DAT_febecc08 = iVar2;
  }
  iVar3 = (int)((int)(int16_t)DAT_febecc1c);
  DAT_febecc00 = ((int)((int)(int16_t)DAT_febecc1a) * (int)((int)(int16_t)DAT_febecc18)) / 0x400;
  if (iVar3 == 0) {
    DAT_febecc04 = 0;
    DAT_febecc00 = 0;
  }
  else {
    DAT_febecc04 = (uint)((int)(DAT_febecc00 << 0x12) / 0x168);
    if (iVar3 != 0) {
      if (((int)(int32_t)DAT_febecc04) == -0x80000000 && iVar3 == -1) {
        DAT_febecc04 = -0x80000000;
      }
      else {
        DAT_febecc04 = (uint)((int)DAT_febecc04 / iVar3);
      }
    }
  }
  DAT_febecc0c = DAT_febecc08 + DAT_febeac24;
  if (((int)(int32_t)DAT_febecc0c) - ((int)(int32_t)DAT_febecc04) < 0 ==
      (((int)(int32_t)DAT_febecc0c) < 0 != ((int)(int32_t)DAT_febecc04) < 0 && ((int)(int32_t)DAT_febecc04) < 0 == ((int)(int32_t)DAT_febecc0c) - ((int)(int32_t)DAT_febecc04) < 0)
      && ((int)(int32_t)DAT_febecc0c) != ((int)(int32_t)DAT_febecc04)) {
    DAT_febecc08 = ((int)(int32_t)DAT_febecc04) + iVar2;
    DAT_febecc10 = DAT_febecc00;
  }
  else if (((int)(int32_t)DAT_febecc0c) + ((int)(int32_t)DAT_febecc04) < 0 ==
           (((int)(int32_t)DAT_febecc0c) < 0 != -((int)(int32_t)DAT_febecc04) < 0 &&
           -((int)(int32_t)DAT_febecc04) < 0 == ((int)(int32_t)DAT_febecc0c) + ((int)(int32_t)DAT_febecc04) < 0)) {
    DAT_febecc10 = (int)((((int)(int32_t)DAT_febecc0c) * iVar3 * 0x168)) / (int)0x40000;
  }
  else {
    DAT_febecc08 = iVar2 - ((int)(int32_t)DAT_febecc04);
    DAT_febecc10 = -DAT_febecc00;
  }
  DAT_febecc14 = (DAT_febecc14 + DAT_febecc10) - (int)((int)(int16_t)DAT_febecc1e);
  iVar3 = (*((int *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xb148cu + (uint32_t)(DAT_febeac3c & 1) * 4u)))))));
  iVar2 = DAT_febecc14 * 0x400;
  if (iVar3 != 0) {
    if (iVar2 == -0x80000000 && iVar3 == -1) {
      iVar2 = 0;
    }
    else {
      iVar2 = (int)iVar2 / (int)iVar3;
    }
  }
  iVar3 = (int)(short)iVar2;
  DAT_febecc1e = (short)iVar2;
  if (DAT_febecbec == '\x01') {
    if (iVar3 - iVar1 < 0 != (iVar3 < 0 != iVar1 < 0 && iVar1 < 0 == iVar3 - iVar1 < 0) ||
        iVar3 == iVar1) {
      iVar2 = -iVar1;
      if (iVar3 + iVar1 < 0 == (iVar3 < 0 != iVar2 < 0 && iVar2 < 0 == iVar3 + iVar1 < 0) &&
          iVar3 != iVar2) {
        iVar2 = iVar3;
      }
      DAT_febecc22 = (short)iVar2;
    }
  }
  else {
    DAT_febecc22 = 0;
  }
  return;
}

void update_absolute_curve_and_bounded_error_integrator_d0120(void)

{
  map_absolute_input_to_waveform_gain_curve_cfffc();
  update_bounded_error_integrator_and_windowed_output_d0030();
  return;
}

void clear_three_command_work_words_d0130(void)

{
  DAT_febecc2c = 0;
  DAT_febecc24 = 0;
  DAT_febecc28 = 0;
  return;
}

void load_nonpositive_command_calibration_bound_d013e(void)

{
  int value;

  value = (int)DAT_000b1328;
  if (value >= 0) {
    value = 0;
  }
  DAT_febecc24 = (uint)value;
  return;
}

void aggregate_internal_assist_terms(void)

{
  int iVar1;
  int iVar2;
  uint32_t puVar3;
  int iVar4;
  int iVar5;
  int iVar6;
  int iVar7;
  
  iVar1 = DAT_febec39c;
  puVar3 = 0xfebeb800u;
  iVar7 = (int)((int)(int16_t)DAT_febec53a);
  iVar5 = (int)((int)(int16_t)DAT_febec5a8);
  iVar6 = (int)((int)(int16_t)DAT_febec41e);
  iVar4 = (int)((int)(int16_t)DAT_febec3a0);
  load_nonpositive_command_calibration_bound_d013e();
  iVar2 = nested_assist_sum_limit;
  iVar1 = (*((int *)camry_host_ptr((uint32_t)(puVar3 + 0x1424)))) + iVar4 + iVar1 + iVar6 + iVar5 + iVar7;
  (*((int *)camry_host_ptr((uint32_t)(puVar3 + 0x1428)))) = iVar1;
  iVar4 = nested_assist_sum_limit;
  if ((iVar1 - iVar2 < 0 != (iVar1 < 0 != iVar2 < 0 && iVar2 < 0 == iVar1 - iVar2 < 0) ||
       iVar1 == iVar2) &&
     (iVar4 = iVar1,
     iVar1 + nested_assist_sum_limit < 0 !=
     (iVar1 < 0 != -nested_assist_sum_limit < 0 &&
     -nested_assist_sum_limit < 0 == iVar1 + nested_assist_sum_limit < 0))) {
    iVar4 = -nested_assist_sum_limit;
  }
  (*((int *)camry_host_ptr((uint32_t)(puVar3 + 0x142c)))) = iVar4;
  return;
}

void fill_constant_block_d01b4(void)

{
  DAT_febecc4c = 0;
  DAT_febecc30 = 0;
  DAT_febecc34 = 0;
  DAT_febecc38 = 0;
  DAT_febecc3c = 0;
  DAT_febecc4e = 0;
  DAT_febecc60 = 0;
  DAT_febecc50 = 0;
  DAT_febecc62 = 0;
  DAT_febecc52 = 0;
  DAT_febecc54 = 0;
  DAT_febecc66 = 0;
  DAT_febecc64 = 0;
  DAT_febecc68 = 0;
  DAT_febecc6a = 0;
  DAT_febecc5c = 0;
  DAT_febecc56 = 0;
  DAT_febecc58 = 0;
  DAT_febecc5a = 0;
  DAT_febecc5e = 0;
  DAT_febecc5f = 0;
  DAT_febecc40 = 0;
  DAT_febecc44 = 0;
  DAT_febecc48 = 0;
  DAT_febecc6c = 0;
  return;
}

void aggregate_assist_command(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  
  iVar1 = DAT_febec4c0;
  if (DAT_febeac2b == 'Z') {
    iVar3 = ((int)(int16_t)DAT_febec3ba) + DAT_febebf3c;
  }
  else {
    iVar3 = DAT_febebf3c;
    if (DAT_febec7bf != '\x01') {
      iVar1 = (int)((int)(int16_t)DAT_febecb38) + (int)((int)(int16_t)DAT_febec5ee);
      iVar3 = DAT_000b132c / 2;
      iVar2 = iVar3;
      if ((iVar1 - iVar3 < 0 != (iVar1 < 0 != iVar3 < 0 && iVar3 < 0 == iVar1 - iVar3 < 0) ||
           iVar1 == iVar3) &&
         (iVar2 = -iVar3,
         iVar1 + iVar3 < 0 == (iVar1 < 0 != iVar2 < 0 && iVar2 < 0 == iVar1 + iVar3 < 0) &&
         iVar1 != iVar2)) {
        iVar2 = iVar1;
      }
      iVar3 = (int)((int)(int16_t)DAT_febecbe8);
      iVar1 = (int)((int)(int16_t)DAT_febec43c) + DAT_febec4c0 + (int)((int)(int16_t)DAT_febec3ba) + DAT_febecc2c + DAT_febebf3c +
              iVar2;
    }
  }
  DAT_febecc48 = iVar1 + iVar3;
  return;
}

void clamp_scale_and_limit_command_work_value_d0284(void)

{
  int iVar1;
  int iVar2;
  
  iVar2 = command_sum_margin + (int)DAT_000b132c;
  iVar1 = (int)DAT_febecc48;
  if (iVar1 > iVar2) {
    iVar1 = iVar2;
  }
  else if (iVar1 <= -iVar2) {
    iVar1 = -iVar2;
  }
  iVar2 = (int)(int16_t)DAT_000b1334;
  DAT_febecc44 = (uint)((int)((long long)iVar1 * (int)DAT_febeac64) / 0x8000);
  iVar1 = (int)DAT_febecc44;
  if (iVar1 > iVar2) {
    iVar1 = iVar2;
  }
  else if (iVar1 <= -iVar2) {
    iVar1 = -iVar2;
  }
  DAT_febecc4c = (short)iVar1;
  return;
}

void filter_command_slew(void)

{
  int iVar1;
  bool bVar2;
  int iVar3;
  uint uVar4;
  
  DAT_febecc4e = ((int)(int16_t)DAT_febecc4c);
  if (DAT_000b1338 != '\x01') goto LAB_000d0378;
  iVar3 = (int)((int)(int16_t)DAT_febecc4c);
  iVar1 = ((int)(int32_t)DAT_febecc3c);
  if (iVar3 == ((int)(int32_t)DAT_febecc3c)) goto LAB_000d0318;
  if (iVar3 == DAT_febecc30) {
    iVar1 = ((int)(int32_t)DAT_febecc34);
    if (iVar3 - ((int)(int32_t)DAT_febecc3c) < 0) {
      if (-1 < (int)DAT_febecc38) goto LAB_000d030e;
    }
    else if ((int)DAT_febecc38 < 0) goto LAB_000d030e;
  }
  else {
LAB_000d030e:
    DAT_febecc3c = ((int)(int32_t)DAT_febecc3c) + ((int)(int32_t)DAT_febecc38);
    iVar1 = ((int)(int32_t)DAT_febecc3c);
  }
LAB_000d0318:
  DAT_febecc34 = iVar1;
  iVar1 = iVar3 - ((int)(int32_t)DAT_febecc34);
  bVar2 = iVar3 < 0 != ((int)(int32_t)DAT_febecc34) < 0 && ((int)(int32_t)DAT_febecc34) < 0 == iVar1 < 0;
  if (iVar1 < 0 == bVar2) {
    if (iVar1 < 0 == bVar2 && iVar3 != ((int)(int32_t)DAT_febecc34)) {
      DAT_febecc38 = (uint)(iVar3 - ((int)(int32_t)DAT_febecc34)) >> (DAT_febecc9e & 0x1f);
      if (((int)(int32_t)DAT_febecc38) == 0) {
        DAT_febecc38 = 1;
      }
    }
    else {
      DAT_febecc38 = 0;
    }
  }
  else {
    uVar4 = (uint)(((int)(int32_t)DAT_febecc34) - iVar3) >> (DAT_febecc9e & 0x1f);
    DAT_febecc38 = -uVar4;
    if (uVar4 == 0) {
      DAT_febecc38 = 0xffffffff;
    }
  }
  DAT_febecc30 = iVar3;
  if (((int)(int16_t)DAT_febecc9c) != 0) {
    iVar1 = ((int)(int32_t)DAT_febecc38) + ((int)(int32_t)DAT_febecc3c);
    iVar3 = 0x7fff;
    if ((iVar1 + -0x7fff < 0 != (iVar1 < 0 && -1 < iVar1 + -0x7fff) || iVar1 == 0x7fff) &&
       (iVar3 = iVar1, iVar1 + 0x7fff < 0 != (-1 < iVar1 && iVar1 + 0x7fff < 0) || iVar1 == -0x7fff)
       ) {
      iVar3 = -0x7fff;
    }
    DAT_febecc4e = (short)iVar3;
  }
LAB_000d0378:
  DAT_febecc3c = (int)DAT_febecc4e;
  return;
}

void clamp_command_slew_to_signed_input_limit_d0382(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  
  iVar3 = (int)((int)(int16_t)DAT_febecc4e);
  iVar2 = (int)((int)(int16_t)DAT_febeac52);
  DAT_febecc60 = ((int)(int16_t)DAT_febeac52);
  if ((iVar3 - iVar2 < 0 != (iVar3 < 0 != iVar2 < 0 && iVar2 < 0 == iVar3 - iVar2 < 0) ||
       iVar3 == iVar2) &&
     (iVar1 = -iVar2, DAT_febecc60 = ((int)(int16_t)DAT_febecc4e),
     iVar3 + iVar2 < 0 != (iVar3 < 0 != iVar1 < 0 && iVar1 < 0 == iVar3 + iVar2 < 0) ||
     iVar3 == iVar1)) {
    DAT_febecc60 = (short)iVar1;
  }
  return;
}

void compose_command_sources(void)

{
  int iVar1;
  char cVar2;
  uint32_t puVar3;
  short sVar4;
  int iVar5;
  int iVar6;
  short sVar7;
  
  cVar2 = DAT_febec797;
  puVar3 = 0xfebeb800u;
  iVar5 = get_c7a0_or_default_on_complement_failure_cb9c8();
  iVar6 = get_c7bc_or_default_on_complement_failure_cb9ae();
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0xbd8))))) == '\x01') {
    sVar7 = (*((short *)camry_host_ptr((uint32_t)(puVar3 + 0x145a))));
  }
  else {
    sVar7 = (*((short *)camry_host_ptr((uint32_t)(puVar3 + 0x1460))));
  }
  (*((short *)camry_host_ptr((uint32_t)(puVar3 + 0x1452)))) = sVar7;
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + 0x146a)))) = 0;
  sVar4 = (short)( (int)((iVar6 * (*((short *)camry_host_ptr((uint32_t)(puVar3 + 0x101a)))))) / (int)0x100);
  sVar7 = (short)(((short)(((int)sVar7 << 8) / 0x100) * iVar5) / 0x100);
  iVar5 = (int)sVar7;
  if (cVar2 == '\0') {
    iVar5 = iVar5 + sVar4;
  }
  (*((short *)camry_host_ptr((uint32_t)(puVar3 + 0x145c)))) = sVar7;
  sVar7 = DAT_000b1334;
  iVar6 = (int)DAT_000b1334;
  (*((short *)camry_host_ptr((uint32_t)(puVar3 + 0x146c)))) = sVar4;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(0x145f))))) = 0;
  (*((int *)camry_host_ptr((uint32_t)(puVar3 + 0x1440)))) = iVar5;
  if (iVar5 - iVar6 < 0 != (iVar5 < 0 != iVar6 < 0 && iVar6 < 0 == iVar5 - iVar6 < 0) ||
      iVar5 == iVar6) {
    iVar1 = -iVar6;
    if (iVar5 + iVar6 < 0 == (iVar5 < 0 != iVar1 < 0 && iVar1 < 0 == iVar5 + iVar6 < 0) &&
        iVar5 != iVar1) {
      sVar7 = (short)iVar5;
    }
    else {
      sVar7 = (short)iVar1;
    }
  }
  (*((short *)camry_host_ptr((uint32_t)(puVar3 + 0x1450)))) = sVar7;
  return;
}

void scale_clamp_gate_command(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  
  iVar3 = (int)((int)(int16_t)DAT_febeac4c);
  DAT_febecc62 = (short)((int)((int)((int)(int16_t)DAT_febecc50) * (uint)DAT_febeac5a) / 0x400);
  iVar2 = (int)DAT_febecc62;
  DAT_febecc66 = ((int)(int16_t)DAT_febeac4c);
  if ((iVar2 - iVar3 < 0 != (iVar2 < 0 != iVar3 < 0 && iVar3 < 0 == iVar2 - iVar3 < 0) ||
       iVar2 == iVar3) &&
     (iVar1 = -iVar3, DAT_febecc66 = DAT_febecc62,
     iVar2 + iVar3 < 0 != (iVar2 < 0 != iVar1 < 0 && iVar1 < 0 == iVar2 + iVar3 < 0) ||
     iVar2 == iVar1)) {
    DAT_febecc66 = (short)iVar1;
  }
  DAT_febecc54 = DAT_febecc66;
  if ((DAT_febeac29 == '\0') || (DAT_febeac2a != '\0')) {
    DAT_febecc66 = 0;
  }
  DAT_febecc68 = ((int)(int16_t)DAT_febeac4c);
  return;
}

void select_final_command(void)

{
  int iVar1;
  
  DAT_febecc64 = ((int)(int16_t)DAT_febecc66);
  if (DAT_febecc98 != '\0') {
    iVar1 = (int)DAT_febecc94;
    if (iVar1 > 0x569a) {
      iVar1 = 0x569a;
    }
    else if (iVar1 <= -0x569a) {
      iVar1 = -0x569a;
    }
    DAT_febecc64 = (short)iVar1;
  }
  return;
}

void capture_three_sample_signed_input_history_d04ac(void)

{
  if (DAT_febeac04 == '\x01') {
    DAT_febecc5e = '\x01';
  }
  else if (DAT_febeac06 == 'Z') {
    if (DAT_febecc5e == '\x01') {
      DAT_febecc5a = ((int)(int16_t)DAT_febeac10);
      DAT_febecc58 = ((int)(int16_t)DAT_febeac10);
    }
    else {
      DAT_febecc5a = ((int)(int16_t)DAT_febecc58);
      DAT_febecc58 = ((int)(int16_t)DAT_febecc56);
    }
    DAT_febecc56 = ((int)(int16_t)DAT_febeac10);
    DAT_febecc5e = '\0';
  }
  return;
}

void fill_constant_block_d04f0(void)

{
  DAT_febecc70 = 0;
  DAT_febecc74 = 0;
  DAT_febecc88 = 0;
  DAT_febecc78 = 0;
  DAT_febecc8a = 0;
  DAT_febecc7c = 0;
  DAT_febecc98 = 0;
  DAT_febecc90 = 1;
  DAT_febecc80 = 0;
  DAT_febecc8c = 0;
  DAT_febecc84 = 0;
  DAT_febecc8e = 0;
  DAT_febecc91 = 0;
  return;
}

void latch_direction_from_five_signed_threshold_tests_d0528(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  int iVar6;
  undefined1 uVar7;
  int iVar8;
  int iVar9;
  int iVar10;
  
  iVar5 = (int)DAT_000b1346;
  iVar9 = (int)DAT_000b1344;
  iVar8 = (int)DAT_000b134a;
  iVar6 = (int)((int)(int16_t)DAT_febecc8c);
  iVar4 = (int)DAT_000b134c;
  iVar10 = (int)-((int)(int16_t)DAT_febeac42);
  iVar3 = (int)DAT_000b134e;
  iVar2 = (int)-((int)(int16_t)DAT_febeac44);
  if (((((((int)(int32_t)DAT_febecc7c) - iVar8 < 0 ==
          (((int)(int32_t)DAT_febecc7c) < 0 != iVar8 < 0 && iVar8 < 0 == ((int)(int32_t)DAT_febecc7c) - iVar8 < 0)) &&
        (((int)(int32_t)DAT_febecc84) - iVar9 < 0 ==
         (((int)(int32_t)DAT_febecc84) < 0 != iVar9 < 0 && iVar9 < 0 == ((int)(int32_t)DAT_febecc84) - iVar9 < 0) &&
         ((int)(int32_t)DAT_febecc84) != iVar9)) &&
       (iVar6 + iVar5 < 0 != (iVar6 < 0 != -iVar5 < 0 && -iVar5 < 0 == iVar6 + iVar5 < 0))) &&
      ((iVar2 - iVar4 < 0 == (iVar2 < 0 != iVar4 < 0 && iVar4 < 0 == iVar2 - iVar4 < 0) &&
        iVar2 != iVar4 &&
       (uVar7 = 1,
       iVar10 - iVar3 < 0 == (iVar10 < 0 != iVar3 < 0 && iVar3 < 0 == iVar10 - iVar3 < 0) &&
       iVar10 != iVar3)))) ||
     ((((iVar1 = -iVar8,
        ((int)(int32_t)DAT_febecc7c) + iVar8 < 0 !=
        (((int)(int32_t)DAT_febecc7c) < 0 != iVar1 < 0 && iVar1 < 0 == ((int)(int32_t)DAT_febecc7c) + iVar8 < 0) ||
        ((int)(int32_t)DAT_febecc7c) == iVar1 &&
        ((((int)(int32_t)DAT_febecc84) + iVar9 < 0 !=
          (((int)(int32_t)DAT_febecc84) < 0 != -iVar9 < 0 && -iVar9 < 0 == ((int)(int32_t)DAT_febecc84) + iVar9 < 0) &&
         (iVar6 - iVar5 < 0 == (iVar6 < 0 != iVar5 < 0 && iVar5 < 0 == iVar6 - iVar5 < 0) &&
          iVar6 != iVar5)))) &&
       (iVar2 + iVar4 < 0 != (iVar2 < 0 != -iVar4 < 0 && -iVar4 < 0 == iVar2 + iVar4 < 0))) &&
      (uVar7 = 2,
      iVar10 + iVar3 < 0 != (iVar10 < 0 != -iVar3 < 0 && -iVar3 < 0 == iVar10 + iVar3 < 0))))) {
    DAT_febecc91 = 1;
    DAT_febecc98 = uVar7;
  }
  return;
}

void filter_two_signed_inputs_and_detect_direction_change_d05b4(void)

{
  int iVar1;
  
  DAT_febecc70 = (DAT_febecc70 + ((int)(int16_t)DAT_febeac48)) - (int)((int)(int16_t)DAT_febecc88);
  iVar1 = DAT_febecc70 * 0x400;
  if (DAT_000b133c != 0) {
    if (iVar1 == -0x80000000 && DAT_000b133c == -1) {
      iVar1 = 0;
    }
    else {
      iVar1 = iVar1 / (int)DAT_000b133c;
    }
  }
  DAT_febecc88 = (short)iVar1;
  DAT_febecc74 = (DAT_febecc74 + ((int)(int16_t)DAT_febeac46)) - DAT_febecc78;
  DAT_febecc78 = DAT_febecc74 * 0x400;
  if (DAT_000b1340 != 0) {
    if (DAT_febecc78 == -0x80000000 && DAT_000b1340 == -1) {
      DAT_febecc78 = -0x80000000;
    }
    else {
      DAT_febecc78 = (uint)((int)DAT_febecc78 / (int)DAT_000b1340);
    }
  }
  if (DAT_febecc90 == '\x01') {
    DAT_febecc90 = '\0';
    DAT_febecc8a = ((int)(int16_t)DAT_febecc88);
  }
  else {
    DAT_febecc84 = DAT_febecc78 - DAT_febecc7c;
    DAT_febecc8c = ((int)(int16_t)DAT_febecc88) - ((int)(int16_t)DAT_febecc8a);
    DAT_febecc8a = ((int)(int16_t)DAT_febecc88);
    if ((DAT_febeac4a <= DAT_000b1348) && (DAT_febecc98 == '\0')) {
      latch_direction_from_five_signed_threshold_tests_d0528();
    }
  }
  return;
}

void expire_direction_latch_after_counter_limit_d064c(void)

{
  if (DAT_febecc91 == '\x01') {
    if (DAT_febecc8e < DAT_000b1350) {
      DAT_febecc8e = DAT_febecc8e + 1;
    }
    else {
      DAT_febecc91 = '\0';
      DAT_febecc8e = 0;
    }
  }
  return;
}

void hold_directional_reference_and_publish_negated_value_d0674(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  
  iVar3 = (int)DAT_000b134a;
  iVar1 = -(int)((int)(int16_t)DAT_febecc66);
  DAT_febecc80 = ((int)(int32_t)DAT_febecc7c);
  if (DAT_febecc98 == '\x01') {
    if (((iVar1 - ((int)(int32_t)DAT_febecc7c) < 0 ==
          (iVar1 < 0 != ((int)(int32_t)DAT_febecc7c) < 0 && ((int)(int32_t)DAT_febecc7c) < 0 == iVar1 - ((int)(int32_t)DAT_febecc7c) < 0)) ||
        (DAT_febecc91 == '\x01')) &&
       (((int)(int32_t)DAT_febecc7c) - iVar3 < 0 ==
        (((int)(int32_t)DAT_febecc7c) < 0 != iVar3 < 0 && iVar3 < 0 == ((int)(int32_t)DAT_febecc7c) - iVar3 < 0)))
    goto LAB_000d06ca;
LAB_000d069e:
    DAT_febecc98 = '\0';
  }
  else if (DAT_febecc98 == '\x02') {
    if (((iVar1 - ((int)(int32_t)DAT_febecc7c) < 0 !=
          (iVar1 < 0 != ((int)(int32_t)DAT_febecc7c) < 0 && ((int)(int32_t)DAT_febecc7c) < 0 == iVar1 - ((int)(int32_t)DAT_febecc7c) < 0) ||
          iVar1 == ((int)(int32_t)DAT_febecc7c)) || (DAT_febecc91 == '\x01')) &&
       (iVar2 = -iVar3,
       ((int)(int32_t)DAT_febecc7c) + iVar3 < 0 !=
       (((int)(int32_t)DAT_febecc7c) < 0 != iVar2 < 0 && iVar2 < 0 == ((int)(int32_t)DAT_febecc7c) + iVar3 < 0) ||
       ((int)(int32_t)DAT_febecc7c) == iVar2)) goto LAB_000d06ca;
    goto LAB_000d069e;
  }
  DAT_febecc7c = DAT_febecc78;
  DAT_febecc80 = iVar1;
LAB_000d06ca:
  DAT_febecc94 = -DAT_febecc80;
  return;
}

void run_direction_filter_timer_and_reference_selection_d06d6(void)

{
  filter_two_signed_inputs_and_detect_direction_change_d05b4();
  expire_direction_latch_after_counter_limit_d064c();
  hold_directional_reference_and_publish_negated_value_d0674();
  return;
}

void initialize_threshold_gain_and_lookup_result_d06ea(void)

{
  DAT_febecc9a = 0;
  DAT_febecc9c = 0;
  DAT_febecc9e = 1;
  return;
}

void select_q14_gain_below_unsigned_input_threshold_d06fa(void)

{
  DAT_febecc9a = 0;
  if (DAT_febeadf6 < DAT_000b1352) {
    DAT_febecc9a = 0x4000;
  }
  return;
}

undefined4 gate_gain_by_absolute_input_and_publish_step_lookup_d0716(void)

{
  int iVar1;
  int iVar2;
  uint32_t puVar3;
  short sVar4;
  undefined2 uVar5;
  undefined4 uVar6;
  int iVar7;
  
  puVar3 = 0xfebeb800u;
  iVar7 = 0;
  sVar4 = abs_s16_wrapping(((int)(int16_t)DAT_febeae3e));
  iVar2 = (int)DAT_000b1354;
  iVar1 = sVar4 - iVar2;
  if (iVar1 < 0 != (sVar4 < 0 != iVar2 < 0 && iVar2 < 0 == iVar1 < 0)) {
    iVar7 = (int)(short)( (int)(((int)(*((short *)camry_host_ptr((uint32_t)(puVar3 + 0x149a)))) << 0xe)) / (int)0x4000);
  }
  uVar5 = lookup_signed16_step_table_with_7fff_sentinel_d07ba(((undefined *)camry_host_ptr(0xb1356u)),iVar7);
  uVar6 = raise_priority_mask_and_return_previous_d1da0(0xffc0);
  (*((short *)camry_host_ptr((uint32_t)(puVar3 + 0x149c)))) = (short)iVar7;
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + 0x149e)))) = uVar5;
  restore_priority_mask_preserving_interrupt_enable_d1dc6(uVar6);
  return uVar6;
}

int interpolate_signed_sentinel_curve(short *points,short input)

{
  short *psVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  
  iVar4 = (int)input;
  iVar2 = (int)*points;
  if ((iVar2 != 0x7fff) &&
     (iVar2 - iVar4 < 0 != (iVar2 < 0 != iVar4 < 0 && iVar4 < 0 == iVar2 - iVar4 < 0))) {
    iVar2 = 0;
    while( true ) {
      psVar1 = points + iVar2 * 2;
      iVar3 = (int)*psVar1;
      if (iVar3 == 0x7fff) {
        return (int)psVar1[-1];
      }
      if (iVar3 - iVar4 < 0 == (iVar3 < 0 != iVar4 < 0 && iVar4 < 0 == iVar3 - iVar4 < 0)) break;
      iVar2 = iVar2 + 1;
    }
    iVar3 = iVar3 - psVar1[-2];
    iVar2 = (iVar4 - psVar1[-2]) * ((int)psVar1[1] - (int)psVar1[-1]);
    if (iVar3 != 0) {
      if (iVar2 == -0x80000000 && iVar3 == -1) {
        iVar2 = 0;
      }
      else {
        iVar2 = (int)iVar2 / (int)iVar3;
      }
    }
    return (int)(short)(psVar1[-1] + (short)iVar2);
  }
  return (int)points[1];
}

int lookup_signed16_step_table_with_7fff_sentinel_d07ba(short *param_1,short param_2)

{
  int iVar1;
  int iVar2;
  int iVar3;
  
  iVar2 = (int)param_2;
  iVar1 = (int)*param_1;
  if ((iVar1 != 0x7fff) &&
     (iVar1 - iVar2 < 0 != (iVar1 < 0 != iVar2 < 0 && iVar2 < 0 == iVar1 - iVar2 < 0))) {
    iVar1 = 0;
    while( true ) {
      iVar3 = (int)param_1[iVar1 * 2 + 2];
      if ((iVar3 - iVar2 < 0 == (iVar3 < 0 != iVar2 < 0 && iVar2 < 0 == iVar3 - iVar2 < 0) &&
           iVar3 != iVar2) || (iVar3 + -0x7fff < 0 == (iVar3 < 0 && -1 < iVar3 + -0x7fff))) break;
      iVar1 = iVar1 + 1;
    }
    return (int)(param_1 + iVar1 * 2 + 2)[-1];
  }
  return (int)param_1[1];
}

uint interpolate_signed16_axis_unsigned16_values_d07f2(short *param_1,short param_2)

{
  short *psVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  
  iVar4 = (int)param_2;
  iVar2 = (int)*param_1;
  if ((iVar2 != 0x7fff) &&
     (iVar2 - iVar4 < 0 != (iVar2 < 0 != iVar4 < 0 && iVar4 < 0 == iVar2 - iVar4 < 0))) {
    iVar2 = 0;
    while( true ) {
      psVar1 = param_1 + iVar2 * 2;
      iVar3 = (int)*psVar1;
      if (iVar3 == 0x7fff) {
        return (uint)(ushort)psVar1[-1];
      }
      if (iVar3 - iVar4 < 0 == (iVar3 < 0 != iVar4 < 0 && iVar4 < 0 == iVar3 - iVar4 < 0)) break;
      iVar2 = iVar2 + 1;
    }
    iVar3 = iVar3 - psVar1[-2];
    iVar2 = (iVar4 - psVar1[-2]) * ((uint)(ushort)psVar1[1] - (uint)(ushort)psVar1[-1]);
    if (iVar3 != 0) {
      if (iVar2 == -0x80000000 && iVar3 == -1) {
        iVar2 = 0;
      }
      else {
        iVar2 = (int)iVar2 / (int)iVar3;
      }
    }
    return (uint)(ushort)psVar1[-1] + iVar2 & 0xffff;
  }
  return (uint)(ushort)param_1[1];
}

int interpolate_unsigned_axis_sentinel_curve(ushort *points,ushort input)

{
  ushort *puVar1;
  int iVar2;
  uint uVar3;
  int iVar4;
  uint uVar5;
  
  uVar3 = (uint)input;
  if ((*points != 0xffff) && (*points < uVar3)) {
    iVar2 = 0;
    while( true ) {
      puVar1 = points + iVar2 * 2;
      uVar5 = (uint)*puVar1;
      if (uVar5 == 0xffff) {
        return (int)(short)puVar1[-1];
      }
      if (uVar3 <= uVar5) break;
      iVar2 = iVar2 + 1;
    }
    iVar2 = uVar5 - puVar1[-2];
    iVar4 = (uVar3 - puVar1[-2]) * ((int)(short)puVar1[1] - (int)(short)puVar1[-1]);
    if (iVar2 != 0) {
      if (iVar4 == -0x80000000 && iVar2 == -1) {
        iVar4 = 0;
      }
      else {
        iVar4 = (int)iVar4 / (int)iVar2;
      }
    }
    return (int)(short)(puVar1[-1] + (short)iVar4);
  }
  return (int)(short)points[1];
}

uint interpolate_unsigned32_pairs_with_wide_difference_product_d08e8(uint *param_1,uint param_2)

{
  uint uVar1;
  uint uVar2;
  undefined8 uVar3;
  uint uVar4;
  uint uVar5;
  int iVar6;
  
  iVar6 = 0;
  if ((*param_1 == 0xffffffff) || (param_2 <= *param_1)) {
    uVar2 = param_1[1];
  }
  else {
    uVar1 = 0;
    while( true ) {
      uVar4 = param_1[uVar1 * 2];
      if ((param_2 < uVar4) || (uVar4 == 0xffffffff)) break;
      uVar1 = uVar1 + 1;
    }
    if (1 < uVar1) {
      iVar6 = uVar1 - 1;
    }
    uVar2 = (param_1 + iVar6 * 2)[1];
    if (uVar4 != 0xffffffff) {
      uVar5 = param_1[iVar6 * 2];
      uVar1 = (param_1 + uVar1 * 2)[1];
      uVar3 = multiply_two_word_integers_modulo_64_bits_d2834(param_2 - uVar5,-(uint)(param_2 < uVar5),uVar1 - uVar2,
                           -(uint)(uVar1 < uVar2));
      iVar6 = divide_signed_two_word_integers_d28ea((int)uVar3,(int)((ulonglong)uVar3 >> 0x20),uVar4 - uVar5,
                           -(uint)(uVar4 < uVar5));
      uVar2 = iVar6 + uVar2;
    }
  }
  return uVar2;
}

short abs_s16_wrapping(short value)

{
  if (0 < value) {
    return value;
  }
  return -value;
}

void locate_unsigned16_axis_interval_and_q10_fraction_d097a(ushort *param_1,uint param_2,undefined2 *param_3,undefined2 *param_4)

{
  int iVar1;
  ushort *puVar2;
  int iVar3;
  int iVar4;
  
  param_2 = param_2 & 0xffff;
  iVar3 = 0;
  if (*param_1 < param_2) {
    for (; (puVar2 = param_1 + iVar3, puVar2[1] < param_2 && (puVar2[1] != 0xffff));
        iVar3 = (int)(short)((short)iVar3 + 1)) {
    }
    iVar4 = 0x400;
    if (puVar2[1] == 0xffff) {
      iVar3 = iVar3 + -1;
    }
    else if (puVar2[1] != *puVar2) {
      iVar4 = (param_2 - *puVar2) * 0x400;
      iVar1 = (uint)puVar2[1] - (uint)*puVar2;
      if (iVar1 != 0) {
        if (iVar4 == -0x80000000 && iVar1 == -1) {
          iVar4 = 0;
        }
        else {
          iVar4 = (int)iVar4 / (int)iVar1;
        }
      }
    }
  }
  else {
    iVar4 = 0;
  }
  *param_3 = (short)iVar3;
  *param_4 = (short)iVar4;
  return;
}

void store_symmetric_saturated_signed32_sum_d0a06(int param_1,int param_2,int *param_3)

{
  int iVar1;
  
  if (param_1 < 1) {
    if ((param_2 < 1) &&
       (iVar1 = -0x7fffffff - param_1,
       iVar1 - param_2 < 0 == (iVar1 < 0 != param_2 < 0 && param_2 < 0 == iVar1 - param_2 < 0) &&
       iVar1 != param_2)) {
      param_2 = -0x7fffffff;
      goto LAB_000d0a3a;
    }
  }
  else if ((0 < param_2) &&
          (iVar1 = (0x7fffffff - param_1) - param_2,
          iVar1 < 0 != (0x7fffffff - param_1 < 0 != param_2 < 0 && param_2 < 0 == iVar1 < 0))) {
    param_2 = 0x7fffffff;
    goto LAB_000d0a3a;
  }
  param_2 = param_2 + param_1;
LAB_000d0a3a:
  *param_3 = param_2;
  return;
}

void publish_command_snapshot(void)

{
  DAT_febeac39 = 0;
  DAT_febeac54 = ((int)(int16_t)DAT_febecc64);
  DAT_febeac76 = ((int)(int16_t)DAT_febecc66);
  DAT_febeac56 = ((int)(int16_t)DAT_febecc62);
  DAT_febeac58 = ((int)(int16_t)DAT_febec128);
  DAT_febeac68 = ((int)(int16_t)DAT_febecc60);
  DAT_febeac7e = ((int)(int16_t)DAT_febecc68);
  DAT_febeac2d = 0;
  if (DAT_febecc98 != '\0') {
    DAT_febeac2d = 0x5a;
  }
  DAT_febeac3e = 0;
  DAT_febeac70 = ((int)(int16_t)DAT_febec172);
  DAT_febeac3f = 0x5a;
  return;
}

void run_assist_command_slice(void)

{
  char cVar1;
  
  cVar1 = DAT_febeac31;
  update_retained_assist_surface_source();
  publish_assist_surface_selector();
  interpolate_abs_ac42_and_scale_c5f0_c9bce();
  if (cVar1 == 'Z') {
    compute_saturated_ac88_delta_after_first_sample_c55b4();
    update_torque_memory_correction();
    step_banked_second_order_recurrence_and_c204_delta_c5a84();
    step_fixed_second_order_recurrence_and_c206_delta_c5c44();
  }
  filter_ac88_delta_twice_scale_clamp_and_negate_c55ee();
  reconcile_both_two_stage_filter_state_pairs_c6128();
  filter_c204_through_two_stages_and_bound_c23c_c5e24();
  filter_c206_through_two_stages_and_bound_c23e_c5eae();
  publish_bounded_assist_torque_input();
  if (cVar1 == 'Z') {
    update_torque_conditioner_slope_blend();
    compose_c88a_from_c172_ac44_curve_products_cc8d6();
    clamp_c882_c88a_sum_into_c894_cc984();
    initialize_and_step_four_stage_ac44_filter_c65c8();
    update_abce_scaling_and_c516_enveloped_output_c8dd2();
    compose_observer_dependent_assist();
    limit_ac90_offset_with_curve_bound_and_filter_c418_c7b44();
    bound_c418_by_b1200_into_c41e_c7c58();
    update_torque_conditioner_reseed_selector();
  }
  repair_assist_torque_conditioner_state();
  condition_assist_torque();
  update_signed_speed_torque_assist();
  update_nonlinear_torque_compensation();
  if (cVar1 == 'Z') {
    update_assist_torque_input_delta();
    update_nonlinear_torque_slope();
    publish_combined_assist_slope();
  }
  sum_nonlinear_and_moving_assist();
  bound_nonlinear_and_moving_assist();
  aggregate_internal_assist_terms();
  repair_torque_rate_filter_state();
  filter_torque_rate_compensation_input();
  if (cVar1 == 'Z') {
    map_first_model_derivative_compensation();
    map_second_model_derivative_compensation();
    publish_model_derivative_compensation();
    update_torque_rate_assist_compensation();
    sum_c814_c818_c800_c812_with_limit_status_cbf9e();
  }
  bound_three_term_compensation();
  aggregate_assist_command();
  clamp_scale_and_limit_command_work_value_d0284();
  filter_command_slew();
  clamp_command_slew_to_signed_input_limit_d0382();
  compose_command_sources();
  scale_clamp_gate_command();
  run_direction_filter_timer_and_reference_selection_d06d6();
  select_final_command();
  publish_command_snapshot();
  return;
}

void initialize_observer_and_waveform_state_chains_d0bda(void)

{
  DAT_febecca0 = 1;
  DAT_febecca1 = 9;
  reset_ac14_delta_filter_c174_and_seed_gain_c5686();
  reset_ac14_delta_filter_c18c_and_seed_gain_c5792();
  reset_rate_observer();
  initialize_retained_estimator_qualification();
  fill_constant_block_c4a06();
  initialize_seven_c54c_gain_slots_to_unity_c8fb6();
  fill_constant_block_cff78();
  fill_constant_block_cfe8e();
  clear_waveform_previous_mode_and_active_history_cfd0a();
  fill_constant_block_cf684();
  return;
}

undefined4 publish_rate_observer_interface(void)

{
  uint32_t puVar1;
  undefined4 uVar2;
  
  puVar1 = 0xfebeb800u;
  DAT_febeac08 = DAT_febebfc5;
  uVar2 = raise_priority_mask_and_return_previous_d1da0(0xffc0);
  (*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + -0xbe4)))) = (*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + 0x884))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0xbf7))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x88e)))));
  restore_priority_mask_preserving_interrupt_enable_d1dc6(uVar2);
  return uVar2;
}

void run_observer_publication_slice(void)

{
  char cVar1;
  char cVar2;
  uint32_t puVar3;
  char cVar4;
  byte bVar5;
  
  cVar2 = DAT_febecca1;
  cVar1 = DAT_febecca0;
  puVar3 = 0xfebeb800u;
  if (DAT_febecca0 == '\x01') {
    puVar3 = 0xfebeb800u;
    compute_saturated_ac14_delta_into_c198_c57cc();
    filter_c198_delta_twice_scale_clamp_and_negate_c5806();
    compute_saturated_ac14_delta_into_c180_c56c0();
  }
  filter_c180_delta_twice_scale_clamp_and_negate_c56fa();
  if (cVar1 == '\x01') {
    qualify_rate_observer_acquisition();
  }
  commit_rate_observer();
  update_rate_observer_deadband();
  if (cVar1 == '\x01') {
    update_abcc_curve_and_filtered_difference_c8de6();
    differentiate_ac0e_and_scale_by_500_over_16_c709e();
    filter_c318_twice_and_bound_c370_c70d6();
    blend_signed_curve_pair_for_c1a2_into_c362_c6e7e();
    step_c36a_enable_envelope_and_bound_c0cc_c6fde();
    map_observer_rate_to_assist_bound();
    update_observer_dependent_assist_bound();
    compute_bounded_two_product_sum_and_c386_complement_c731c();
    scale_c362_by_c386_c376_and_internal_attenuation_c6f1e();
  }
  if (cVar2 == '\t') {
    differentiate_bf9a_and_saturate_s16_c9524();
  }
  if (cVar1 == '\x01') {
    combine_scaled_outputs_with_abs_ac0e_curve_c94b8();
    publish_directional_rate_compensation();
    bound_c534_by_b1274_into_c53a_c8f90();
  }
  capture_three_sample_signed_input_history_d04ac();
  advance_mode_delay_and_commit_outside_active_window_cff04();
  update_windowed_excitation();
  cVar4 = cVar2 + '\x01';
  bVar5 = cVar1 + 1;
  if (1 < bVar5) {
    bVar5 = 0;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(0x14a0))))) = bVar5;
  if (9 < (byte)(cVar2 + 1U)) {
    cVar4 = '\0';
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(0x14a1))))) = cVar4;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0xbfb))))) = bVar5;
  publish_rate_observer_interface();
  return;
}

void publish_retained_cell_and_event_channel_snapshots_d0d6c(void)

{
  store_c60c_record_to_ae10_acf0_acef_c9f1e();
  copy_cell_block_cf5ee();
  return;
}

void publish_scaled_control_terms_and_clear_unused_fields_d0d7c(void)

{
  uint uVar1;
  int iVar2;
  int iVar3;
  
  uVar1 = (uint)DAT_febeae3c;
  iVar3 = (int)((int)((int)(int16_t)DAT_febec5ee) * uVar1) / 0x8000;
  if (iVar3 + -0x569a < 0 == (iVar3 < 0 && -1 < iVar3 + -0x569a) && iVar3 != 0x569a) {
    iVar3 = 0x569a;
  }
  else if (iVar3 + 0x569a < 0 != (-1 < iVar3 && iVar3 + 0x569a < 0)) {
    iVar3 = -0x569a;
  }
  iVar2 = (int)((int)((int)(int16_t)DAT_febec85e) * uVar1) / 0x8000;
  if (iVar2 + -0x569a < 0 == (iVar2 < 0 && -1 < iVar2 + -0x569a) && iVar2 != 0x569a) {
    iVar2 = 0x569a;
  }
  else if (iVar2 + 0x569a < 0 != (-1 < iVar2 && iVar2 + 0x569a < 0)) {
    iVar2 = -0x569a;
  }
  DAT_febeae12 = (undefined2)iVar3;
  DAT_febeae16 = (undefined2)iVar2;
  DAT_febead0a = 0;
  DAT_febeacf1 = DAT_febec5f4;
  DAT_febead09 = 0;
  DAT_febead0b = 0;
  DAT_febead15 = 0;
  DAT_febeacf5 = DAT_febec862;
  DAT_febead16 = 0;
  DAT_febead17 = 0;
  DAT_febeaed2 = 0;
  DAT_febeacf6 = DAT_febec835;
  DAT_febeaed4 = 0;
  DAT_febead33 = 0;
  DAT_febead39 = 0;
  DAT_febeacf7 = DAT_febec863;
  DAT_febeae58 = 0;
  DAT_febeacf8 = DAT_febec865;
  DAT_febead14 = DAT_febec861;
  DAT_febeae36 = ((int)(int16_t)DAT_febecc6a);
  iVar3 = (int)((int)((int)(int16_t)DAT_febecb38) * uVar1) / 0x8000;
  if (iVar3 + -0x569a < 0 == (iVar3 < 0 && -1 < iVar3 + -0x569a) && iVar3 != 0x569a) {
    iVar3 = 0x569a;
  }
  else if (iVar3 + 0x569a < 0 != (-1 < iVar3 && iVar3 + 0x569a < 0)) {
    iVar3 = -0x569a;
  }
  DAT_febeae6e = (undefined2)iVar3;
  DAT_febead45 = 0;
  DAT_febead46 = 0;
  DAT_febead60 = DAT_febecb57;
  DAT_febead49 = 0;
  DAT_febead8f = 0;
  DAT_febead90 = 0;
  DAT_febead67 = DAT_febecb58;
  DAT_febead9f = 0;
  DAT_febeada0 = 0;
  DAT_febeada1 = 0;
  DAT_febead42 = DAT_febecafc;
  DAT_febead91 = 0;
  DAT_febead92 = 0;
  DAT_febead93 = 0;
  DAT_febead43 = DAT_febecab6;
  DAT_febead94 = 0;
  DAT_febead95 = 0;
  DAT_febead96 = 0;
  DAT_febead44 = DAT_febecab7;
  DAT_febeada9 = 0;
  DAT_febead97 = 0;
  DAT_febeaf10 = 0;
  DAT_febead47 = DAT_febecaac;
  DAT_febeaf14 = 0;
  DAT_febeaf2c = 0;
  DAT_febead48 = DAT_febecaad;
  DAT_febead4a = DAT_febecad8;
  DAT_febead4b = DAT_febecad9;
  DAT_febeae82 = 0;
  DAT_febeae80 = 0;
  DAT_febeae84 = 0;
  DAT_febeae5c = ((int)(int16_t)DAT_febecad2) / 2;
  DAT_febeae86 = 0;
  DAT_febead9e = 0;
  DAT_febeadab = 0;
  DAT_febeaddf = DAT_febec7bf;
  DAT_febeadde = DAT_febec7be;
  publish_retained_cell_and_event_channel_snapshots_d0d6c();
  return;
}

void run_cadence_gated_control_updates_and_publication_d0eec(void)

{
  byte bVar1;
  
  bVar1 = DAT_febeacbc;
  qualify_assist_surface_transition();
  refresh_c16e_gain_from_ae3a_c566c();
  refresh_c186_gain_from_ae3a_c5778();
  refresh_c19e_gain_from_ae3a_c5884();
  classify_accc_ad6f_nonzero_and_bit1_c956a();
  if ((bVar1 & 8) != 0) {
    lookup_c1a4_axis_index_and_fraction_from_bank_c58b8();
    lookup_c1a8_axis_index_and_fraction_from_pointer_table_c5910();
    lookup_c1ac_axis_index_and_fraction_from_bank_c5956();
    interpolate_af83c_curve_into_c20c_c5f38();
    interpolate_banked_coefficient_and_14cc_curve_pair_c74e2();
    interpolate_adf6_into_c5d8_gain_c9ba6();
    interpolate_adf6_into_c87c_c886_gains_cc66e();
    interpolate_banked_169c_curve_into_c3cc_c7966();
    interpolate_mode_selected_d3810_curve_into_c530_c8ecc();
    interpolate_banked_1a4c_curve_into_c508_c8a78();
    lookup_c364_axis_index_and_fraction_from_bank_c6f86();
    interpolate_three_banked_curves_into_c372_c374_c376_c713c();
    update_nonlinear_torque_speed_gain();
    update_angle_rate_compensation_speed_gain();
    update_directional_rate_speed_gain();
    interpolate_unsigned_b00ae_curve_into_abbc_c82a8();
    interpolate_adf6_into_abf8_gain_c9a5c();
    interpolate_adf6_abde_and_c594_curves_c9258();
    interpolate_adf6_c590_and_abdc_bounds_c91f2();
    update_torque_memory_speed_gain();
    select_q14_gain_below_unsigned_input_threshold_d06fa();
  }
  if ((bVar1 >> 4 & 1) != 0) {
    interpolate_two_signed_ae4a_curves_into_c474_c476_c81f8();
  }
  if ((bVar1 & 4) != 0) {
    gate_gain_by_absolute_input_and_publish_step_lookup_d0716();
  }
  if ((bVar1 & 2) != 0) {
    interpolate_b0102_curve_into_c37a_c71b6();
    snapshot_bf44_status_class_and_boolean_inputs_c2cc0();
    run_raw_estimator_cycle();
  }
  update_angle_rate_compensation();
  debounce_c5f2_and_latch_c5f3_enable_c9650();
  clamp_ae06_and_report_event_c8_once_c9caa();
  clamp_ae04_to_byte_and_report_event_c9_once_c9d18();
  combine_five_signed_curve_terms_saturating_c98ae();
  filter_signed_c5fc_curve_with_adf6_gate_c9812();
  filter_c5b8_between_c5f4_selected_targets_c973a();
  clamp_and_blend_c5ec_abfa_by_c5b8_c9a84();
  rearm_c608_after_two_magnitude_timeouts_c9e44();
  record_c5f3_activation_with_a5_marker_c9eea();
  debounce_c5ee_magnitude_and_report_event_ca_c9d86();
  debounce_c5ec_status_and_filter_unsigned_abc4_gain_c854a();
  step_c5e7_magnitude_hysteresis_and_holdoff_c9b04();
  debounce_c5ec_status_and_filter_c2d6_gain_c6af6();
  debounce_c5ec_status_and_filter_unsigned_c4ca_gain_c878a();
  thunk_derive_caff_cafe_group_status_gates_cefa4();
  call_select_angle_controller_mode_cf04a();
  set_c865_from_acbe_and_adfc_low9_cc514();
  step_c858_enable_latch_and_c863_holdoff_cc1b6();
  filter_c846_toward_q8_unity_by_c85a_cc32a();
  map_signed_ae20_gain_into_c83c_cc3be();
  slew_c856_and_classify_c840_limit_crossing_cc43a();
  update_acfe_mod64_delta_and_reset_c828_flags_cc07a();
  clear_c826_and_return_abs_ae24_cc114();
  or_c82e_c834_into_c835_cc130();
  derive_c795_c79a_c79b_group_status_gates_cb2a2();
  debounce_abs_adf2_c7be_banked_hysteresis_cb5e4();
  monitor_wrapped_aee8_delta_c744_ring_cb45e();
  update_c7b4_and_c7bf_gates_cb81c();
  repair_c7a2_c7a4_filter_residuals_cb9e2();
  filter_two_c7bf_transition_targets_cb82c();
  slew_c7dc_and_interpolate_c808_history_cbb66();
  capture_ac88_baseline_and_clamp_c7c4_delta_cbc80();
  normalize_c7c4_and_compose_c80c_cbcb8();
  debounce_ae02_and_select_c7f4_coefficients_cbd64();
  step_c808_c80c_error_filter_and_integrator_cbe28();
  debounce_c81c_c81d_into_c794_cb246();
  debounce_c80e_sign_relations_into_c796_cb2f8();
  debounce_cc6c_inactive_magnitude_into_c797_cb396();
  debounce_c80a_c80c_difference_into_c798_cb3f4();
  update_angle_feedback_offset_and_publication();
  debounce_voted_cad2_cab8_difference_into_cad9_ceb92();
  update_triplicate_enable_and_cab7_transition_ce8ca();
  run_init_chain_cef0e();
  latch_cafd_after_ae24_threshold_duration_cef26();
  or_cafb_cafd_into_cafc_cec72();
  update_selected_angle_target();
  run_angle_control_filters_compose_and_limit_ce6cc();
  shape_angle_controller_target();
  publish_angle_controller_target_triplicate();
  update_angle_controller_output_envelope();
  derive_event_enables_and_update_channel_markers_cf5de();
  update_torque_memory_gain();
  prepare_and_step_unsigned_gain_c3f4_c7a18();
  update_c544_slew_and_c548_gain_product_c9124();
  update_c2f4_slew_and_seven_curve_gain_product_c6d4e();
  prepare_and_step_unsigned_gain_c4dc_c890e();
  prepare_and_step_unsigned_gain_c2a4_c666c();
  prepare_and_step_unsigned_gain_c42c_c7d14();
  prepare_and_step_unsigned_gain_c438_c7dd4();
  capture_request_when_group26_status_allows_cfda0();
  publish_request_mode_and_enable_under_priority_mask_cfe64();
  if ((bVar1 & 8) != 0) {
    refresh_c412_c414_c416_terms_from_adf6_c7b34();
    interpolate_two_input_curves_and_scale_second_gain_cffa2();
  }
  if ((bVar1 & 2) != 0) {
    map_signed_bf9a_half_and_c5a2_curves_c92b2();
    step_two_clamped_second_order_recurrences_c9314();
    scale_and_clamp_abe4_abe6_outputs_c945e();
    snapshot_c0d0_c08f_c0cc_into_c88e_c868_cc5ac();
    classify_c890_magic_and_status_gates_cc5da();
    compose_c868_magic_selected_curve_filter_cc6ba();
    debounce_abs_c882_c88a_sum_into_c892_cc878();
    snapshot_c084_and_run_abb8_curve_curve_filter_c84f8();
    snapshot_c084_and_run_c2a8_curve_curve_filter_c6aa4();
    snapshot_c084_and_run_c3bc_curve_curve_filter_c7912();
  }
  if ((bVar1 & 4) != 0) {
    qualify_opposed_rate_direction();
    filter_directional_rate_compensation();
    debounce_opposed_adf2_c18a_sign_thresholds_c8e1c();
    lookup_signed_c18a_curve_gate_scale_and_filter_c534_c8ef4();
  }
  publish_scaled_control_terms_and_clear_unused_fields_d0d7c();
  return;
}
