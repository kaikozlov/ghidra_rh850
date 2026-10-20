#include "common.h"

void step_c544_mode_selected_gain_slew_c9058(void)

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
  local_10.current = DAT_febec544;
  if (uVar3 < 7) {
    local_10.direction = '\x02';
    iVar1 = (short)(DAT_febeac3c & 1) * 7 + uVar3;
    local_10.up_target = *(ushort *)(((undefined *)camry_host_ptr((uint32_t)(0xd3858u + (uint32_t)(iVar1 * 0x10) * 1u))));
    local_10.down_step = (*((ushort *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd3854u + (uint32_t)(iVar1 * 4) * 4u)))))));
    local_10.up_step = (*((ushort *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd385cu + (uint32_t)(iVar1 * 4) * 4u)))))));
    local_10.down_target = (*((ushort *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd3850u + (uint32_t)(iVar1 * 4) * 4u)))))));
  }
  else {
    local_10.direction = '\x01';
    local_10.up_target = DAT_febec53c;
    local_10.down_step = DAT_febec540;
    local_10.up_step = DAT_febec542;
    local_10.down_target = DAT_febec53e;
  }
  step_retained_unsigned_gain(&local_10);
  (*((ushort *)camry_host_ptr((uint32_t)(puVar2 + 0xd40)))) = local_10.down_step;
  (*((ushort *)camry_host_ptr((uint32_t)(puVar2 + 0xd42)))) = local_10.up_step;
  (*((ushort *)camry_host_ptr((uint32_t)(puVar2 + 0xd3e)))) = local_10.down_target;
  (*((ushort *)camry_host_ptr((uint32_t)(puVar2 + 0xd3c)))) = local_10.up_target;
  (*((ushort *)camry_host_ptr((uint32_t)(puVar2 + 0xd44)))) = local_10.current;
  return;
}

void multiply_seven_c54c_retained_gains_q10_c90a0(void)

{
  uint8_t stack_record_2c[44];
  char *pcVar1;
  int iVar2;
  int iVar3;
  ushort uVar4;
  undefined8 uVar5;
  uint uVar6;
  int iVar7;
  
  uVar5 = 0xfebeb800;
  uVar6 = 0x400;
  (*((uint16_t *)(stack_record_2c + 16))) = ((int)(int16_t)DAT_febec172);
  uVar4 = (ushort)DAT_febeac3c;
  iVar7 = 0;
  do {
    pcVar1 = ((undefined *)camry_host_ptr((uint32_t)(0xd3930u + (uint32_t)(iVar7 * 0xc + (short)(uVar4 & 1) * 0x54) * 1u)));
    ((int8_t *)(stack_record_2c))[0] = *pcVar1;
    if (((int8_t *)(stack_record_2c))[0] != '\a') {
      (*((uint32_t *)(stack_record_2c + 4))) = *(undefined4 *)(pcVar1 + 4);
      iVar2 = iVar7 + (int)uVar5;
      iVar3 = iVar7 * 2 + (int)uVar5;
      (*((uint32_t *)(stack_record_2c + 8))) = *(undefined4 *)(pcVar1 + 8);
      stack_record_2c[12] = (*((undefined1 *)camry_host_ptr((uint32_t)(iVar2 + 0xd4c))));
      (*((uint16_t *)(stack_record_2c + 14))) = (*((ushort *)camry_host_ptr((uint32_t)(iVar3 + 0xd54))));
      update_retained_mode_gain_below_magnitude_threshold_ce912(((int8_t *)(stack_record_2c)));
      (*((ushort *)camry_host_ptr((uint32_t)(iVar3 + 0xd54)))) = (*((uint16_t *)(stack_record_2c + 14)));
      (*((undefined1 *)camry_host_ptr((uint32_t)(iVar2 + 0xd4c)))) = stack_record_2c[12];
      uVar6 = uVar6 * (*((uint16_t *)(stack_record_2c + 14))) >> 10 & 0xffff;
    }
    iVar3 = iVar7 + 1;
    iVar2 = iVar7 + -6;
    iVar7 = iVar3;
  } while (((iVar2 < 0) || (iVar3 < 0)));
  (*((short *)camry_host_ptr((uint32_t)((int)uVar5 + 0xd48)))) = (short)uVar6;
  return;
}

void update_c544_slew_and_c548_gain_product_c9124(void)

{
  step_c544_mode_selected_gain_slew_c9058();
  multiply_seven_c54c_retained_gains_q10_c90a0();
  return;
}

int apply_c544_and_c548_q10_gains_c9134(short param_1)

{
  DAT_febec546 = (short)((int)((uint)DAT_febec544 * (int)param_1) / 0x400);
  DAT_febec54a = (short)((int)((uint)DAT_febec548 * (int)DAT_febec546) / 0x400);
  return (int)(short)DAT_febec54a;
}

void fill_constant_block_c9160(void)

{
  DAT_febec590 = 5;
  DAT_febeabde = 0;
  DAT_febeabdc = 0x32;
  DAT_febec594 = 0;
  DAT_febec592 = 0x38;
  DAT_febec564 = 0;
  DAT_febec568 = 0;
  DAT_febec56c = 0;
  DAT_febec570 = 0;
  DAT_febec574 = 0;
  DAT_febec578 = 0;
  DAT_febec596 = 0;
  DAT_febeabe0 = 0;
  DAT_febeabe2 = 0;
  DAT_febec598 = 0;
  DAT_febec59a = 0;
  DAT_febec59c = 0;
  DAT_febec57c = 0;
  DAT_febeabd0 = 0;
  DAT_febeabd4 = 0;
  DAT_febec580 = 0;
  DAT_febec584 = 0;
  DAT_febeabd8 = 0;
  DAT_febeabe4 = 0;
  DAT_febeabe6 = 0;
  DAT_febec59e = 0;
  DAT_febec5a0 = 0;
  DAT_febec5a8 = 0;
  DAT_febec588 = 0;
  DAT_febec58c = 0;
  DAT_febec5a2 = 0;
  DAT_febec5a4 = 0;
  DAT_febec5a6 = 0;
  DAT_febeabe8 = 0;
  return;
}

int interpolate_adf6_c590_and_abdc_bounds_c91f2(void)

{
  ushort input;
  uint32_t puVar1;
  int iVar2;
  int iVar3;
  
  input = DAT_febeadf6;
  puVar1 = 0xfebeb800u;
  iVar3 = (DAT_febec156 & 3) * 0x24;
  iVar2 = interpolate_unsigned_axis_sentinel_curve
                    (((ushort *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xb144cu + (uint32_t)(DAT_febeac3c & 1) * 4u)))) + iVar3 + 0x203c))),
                     DAT_febeadf6);
  (*((short *)camry_host_ptr((uint32_t)(puVar1 + 0xd90)))) = (short)iVar2;
  iVar3 = interpolate_unsigned_axis_sentinel_curve
                    (((ushort *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xb144cu + (uint32_t)((byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0xbc4))))) & 1) * 4u)))) + iVar3 + 0x20cc))),input);
  (*((short *)camry_host_ptr((uint32_t)(puVar1 + -0xc24)))) = (short)iVar3;
  (*((short *)camry_host_ptr((uint32_t)(puVar1 + 0xd92)))) = (*((short *)camry_host_ptr((uint32_t)(puVar1 + 0xd90)))) + (short)iVar3 + 1;
  return iVar3;
}

void interpolate_adf6_abde_and_c594_curves_c9258(void)

{
  ushort input;
  uint32_t puVar1;
  int iVar2;
  int iVar3;
  
  input = DAT_febeadf6;
  puVar1 = 0xfebeb800u;
  iVar3 = (DAT_febec156 & 3) * 0x24;
  iVar2 = interpolate_unsigned_axis_sentinel_curve
                    (((ushort *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xb144cu + (uint32_t)(DAT_febeac3c & 1) * 4u)))) + iVar3 + 0x215c))),
                     DAT_febeadf6);
  (*((short *)camry_host_ptr((uint32_t)(puVar1 + -0xc22)))) = (short)iVar2;
  iVar3 = interpolate_unsigned_axis_sentinel_curve
                    (((ushort *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xb144cu + (uint32_t)((byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0xbc4))))) & 1) * 4u)))) + iVar3 + 0x21ec))),input);
  (*((short *)camry_host_ptr((uint32_t)(puVar1 + 0xd94)))) = (short)iVar3;
  return;
}

void map_signed_bf9a_half_and_c5a2_curves_c92b2(void)

{
  short value;
  uint32_t puVar1;
  short sVar2;
  short sVar3;
  undefined4 uVar4;
  int iVar5;
  
  puVar1 = 0xfebeb800u;
  uVar4 = raise_priority_mask_and_return_previous_d1da0(0xffc0);
  sVar3 = (*((short *)camry_host_ptr((uint32_t)(puVar1 + 0x79a))));
  value = (*((short *)camry_host_ptr((uint32_t)(puVar1 + 0xda2))));
  restore_priority_mask_preserving_interrupt_enable_d1dc6(uVar4);
  sVar2 = abs_s16_wrapping(sVar3 / 2);
  iVar5 = interpolate_signed_sentinel_curve((short *)((undefined *)camry_host_ptr(0xb12f0u)),sVar2);
  sVar2 = (short)iVar5;
  if (sVar3 / 2 < 0) {
    sVar2 = -sVar2;
  }
  (*((short *)camry_host_ptr((uint32_t)(puVar1 + 0xd96)))) = sVar2;
  sVar3 = abs_s16_wrapping(value);
  iVar5 = interpolate_signed_sentinel_curve((short *)((undefined *)camry_host_ptr(0xb1304u)),sVar3);
  sVar3 = (short)iVar5;
  if (value < 0) {
    sVar3 = -sVar3;
  }
  (*((short *)camry_host_ptr((uint32_t)(puVar1 + 0xd98)))) = sVar3;
  return;
}

void step_two_clamped_second_order_recurrences_c9314(void)

{
  int iVar1;
  short sVar2;
  int iVar3;
  int iVar4;
  short sVar5;
  short sVar6;
  int iVar7;
  int iVar8;
  uint uVar9;
  int iVar10;
  uint uVar11;
  
  sVar2 = ((int)(int16_t)DAT_febec59a);
  sVar5 = ((int)(int16_t)DAT_febeabe0);
  iVar1 = DAT_febeabd8;
  iVar4 = DAT_febeabd4;
  iVar10 = (int)((int)(int16_t)DAT_febec596);
  uVar9 = (uint)DAT_000b12e8;
  iVar7 = (int)DAT_000b12e4;
  DAT_febec56c = iVar7;
  sVar6 = DAT_000b12e4;
  if ((iVar10 - iVar7 < 0 != (iVar10 < 0 != iVar7 < 0 && iVar7 < 0 == iVar10 - iVar7 < 0) ||
       iVar10 == iVar7) &&
     (DAT_febec56c = -iVar7, sVar6 = ((int)(int16_t)DAT_febec596),
     iVar10 + iVar7 < 0 !=
     (iVar10 < 0 != ((int)(int32_t)DAT_febec56c) < 0 && ((int)(int32_t)DAT_febec56c) < 0 == iVar10 + iVar7 < 0) ||
     iVar10 == ((int)(int32_t)DAT_febec56c))) {
    sVar6 = (short)((int)(int32_t)DAT_febec56c);
  }
  iVar7 = (int)((int)(int16_t)DAT_febec592);
  DAT_febec568 = ((int)(int32_t)DAT_febeabd0) - DAT_febeabd4;
  DAT_febec564 = DAT_febec568;
  if (iVar7 != 0) {
    if (DAT_febec568 == -0x80000000 && iVar7 == -1) {
      DAT_febec568 = -0x80000000;
      DAT_febec56c = 0;
    }
    else {
      DAT_febec56c = (int)DAT_febec568 % (int)iVar7;
      DAT_febec568 = (int)DAT_febec568 / (int)iVar7;
    }
  }
  iVar8 = (int)((int)(int16_t)DAT_febeabdc);
  iVar10 = (((int)(int16_t)DAT_febeabe0) * 2 + (int)sVar6 + (int)((int)(int16_t)DAT_febeabe2)) * uVar9 +
           (DAT_febeabd4 + ((int)(int32_t)DAT_febeabd0)) * -2;
  iVar3 = ((int)(int32_t)DAT_febec56c) * iVar8 * 2;
  if (iVar7 != 0) {
    if (iVar3 == -0x80000000 && iVar7 == -1) {
      iVar3 = -0x80000000;
    }
    else {
      iVar3 = (int)iVar3 / (int)iVar7;
    }
  }
  if (iVar7 != 0) {
    if (iVar10 == -0x80000000 && iVar7 == -1) {
      iVar10 = -0x80000000;
    }
    else {
      iVar10 = (int)iVar10 / (int)iVar7;
    }
  }
  DAT_febeabe0 = sVar6;
  DAT_febeabe2 = sVar5;
  DAT_febeabd4 = ((int)(int32_t)DAT_febeabd0);
  DAT_febeabd0 = iVar4 + iVar3 + DAT_febec568 * iVar8 * 2 + iVar10;
  uVar11 = (uint)(DAT_000b12e8 >> 1);
  DAT_febec57c = ((int)(int32_t)DAT_febeabd0);
  if ((int)DAT_febeabd0 < 0) {
    iVar4 = uVar11 - ((int)(int32_t)DAT_febeabd0);
    if (uVar9 != 0) {
      if (iVar4 == -0x80000000 && uVar9 == 0xffffffff) {
        iVar4 = 0;
      }
      else {
        iVar4 = iVar4 / (int)uVar9;
      }
    }
    iVar4 = -iVar4;
  }
  else {
    iVar4 = uVar11 + ((int)(int32_t)DAT_febeabd0);
    if (uVar9 != 0) {
      if (iVar4 == -0x80000000 && uVar9 == 0xffffffff) {
        iVar4 = 0;
      }
      else {
        iVar4 = iVar4 / (int)uVar9;
      }
    }
  }
  iVar3 = (int)((int)(int16_t)DAT_febec598);
  iVar10 = (int)DAT_000b12e6;
  DAT_febeabe4 = (short)iVar4;
  DAT_febec578 = iVar10;
  sVar5 = DAT_000b12e6;
  if ((iVar3 - iVar10 < 0 != (iVar3 < 0 != iVar10 < 0 && iVar10 < 0 == iVar3 - iVar10 < 0) ||
       iVar3 == iVar10) &&
     (DAT_febec578 = -iVar10, sVar5 = ((int)(int16_t)DAT_febec598),
     iVar3 + iVar10 < 0 != (iVar3 < 0 != ((int)(int32_t)DAT_febec578) < 0 && ((int)(int32_t)DAT_febec578) < 0 == iVar3 + iVar10 < 0)
     || iVar3 == ((int)(int32_t)DAT_febec578))) {
    sVar5 = (short)((int)(int32_t)DAT_febec578);
  }
  iVar4 = (int)((int)(int16_t)DAT_febec59a);
  iVar10 = (int)((int)(int16_t)DAT_febec59c);
  DAT_febec59a = sVar5;
  DAT_febec574 = DAT_febec584 - DAT_febeabd8;
  DAT_febec570 = DAT_febec574;
  if (iVar7 != 0) {
    if (DAT_febec574 == -0x80000000 && iVar7 == -1) {
      DAT_febec574 = -0x80000000;
      DAT_febec578 = 0;
    }
    else {
      DAT_febec578 = (int)DAT_febec574 % (int)iVar7;
      DAT_febec574 = (int)DAT_febec574 / (int)iVar7;
    }
  }
  DAT_febeabd8 = DAT_febec584;
  DAT_febec59c = sVar2;
  iVar4 = (iVar4 * 2 + (int)sVar5 + iVar10) * uVar9 + (iVar1 + DAT_febec584) * -2;
  if (iVar7 != 0) {
    if (iVar4 == -0x80000000 && iVar7 == -1) {
      iVar4 = -0x80000000;
    }
    else {
      iVar4 = (int)iVar4 / (int)iVar7;
    }
  }
  iVar10 = ((int)(int32_t)DAT_febec578) * iVar8 * 2;
  if (iVar7 != 0) {
    if (iVar10 == -0x80000000 && iVar7 == -1) {
      iVar10 = -0x80000000;
    }
    else {
      iVar10 = (int)iVar10 / (int)iVar7;
    }
  }
  iVar4 = iVar10 + DAT_febec574 * iVar8 * 2 + iVar4;
  DAT_febec580 = iVar1 + iVar4;
  DAT_febec584 = DAT_febec580;
  if (iVar1 + iVar4 < 0) {
    iVar4 = uVar11 - DAT_febec580;
    if (uVar9 != 0) {
      if (iVar4 == -0x80000000 && uVar9 == 0xffffffff) {
        iVar4 = 0;
      }
      else {
        iVar4 = iVar4 / (int)uVar9;
      }
    }
    iVar4 = -iVar4;
  }
  else {
    iVar4 = uVar11 + DAT_febec580;
    if (uVar9 != 0) {
      if (iVar4 == -0x80000000 && uVar9 == 0xffffffff) {
        iVar4 = 0;
      }
      else {
        iVar4 = iVar4 / (int)uVar9;
      }
    }
  }
  DAT_febeabe6 = (short)iVar4;
  return;
}

void scale_and_clamp_abe4_abe6_outputs_c945e(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  
  iVar2 = (int)DAT_000b12ea;
  iVar1 = ((int)((int)(int16_t)DAT_febeabe4) * (int)((int)(int16_t)DAT_febeabde)) / 0x800;
  iVar3 = iVar2;
  if ((iVar1 - iVar2 < 0 != (iVar1 < 0 != iVar2 < 0 && iVar2 < 0 == iVar1 - iVar2 < 0) ||
       iVar1 == iVar2) &&
     (iVar3 = -iVar2,
     iVar1 + iVar2 < 0 == (iVar1 < 0 != iVar3 < 0 && iVar3 < 0 == iVar1 + iVar2 < 0) &&
     iVar1 != iVar3)) {
    iVar3 = iVar1;
  }
  DAT_febec59e = (short)iVar3;
  iVar3 = (int)DAT_000b12ec;
  iVar1 = ((int)((int)(int16_t)DAT_febeabe6) * (int)((int)(int16_t)DAT_febec594)) / 0x100;
  DAT_febec5a0 = DAT_000b12ec;
  if (iVar1 - iVar3 < 0 != (iVar1 < 0 != iVar3 < 0 && iVar3 < 0 == iVar1 - iVar3 < 0) ||
      iVar1 == iVar3) {
    iVar2 = -iVar3;
    if (iVar1 + iVar3 < 0 == (iVar1 < 0 != iVar2 < 0 && iVar2 < 0 == iVar1 + iVar3 < 0) &&
        iVar1 != iVar2) {
      DAT_febec5a0 = (short)iVar1;
    }
    else {
      DAT_febec5a0 = (short)iVar2;
    }
  }
  return;
}

void combine_scaled_outputs_with_abs_ac0e_curve_c94b8(void)

{
  undefined2 uVar1;
  uint32_t puVar2;
  short input;
  int iVar3;
  int iVar4;
  int iVar5;
  
  puVar2 = 0xfebeb800u;
  if (DAT_000b1371 == '\x01') {
    uVar1 = 0;
  }
  else {
    puVar2 = 0xfebeb800u;
    iVar3 = apply_c544_and_c548_q10_gains_c9134((int)(short)(((int)(int16_t)DAT_febec5a0) + ((int)(int16_t)DAT_febec59e)));
    iVar5 = (int)DAT_000b12ee;
    iVar4 = iVar5;
    if ((iVar3 - iVar5 < 0 != (iVar3 < 0 != iVar5 < 0 && iVar5 < 0 == iVar3 - iVar5 < 0) ||
         iVar3 == iVar5) &&
       (iVar4 = -iVar5,
       iVar3 + iVar5 < 0 == (iVar3 < 0 != iVar4 < 0 && iVar4 < 0 == iVar3 + iVar5 < 0) &&
       iVar3 != iVar4)) {
      iVar4 = iVar3;
    }
    (*((short *)camry_host_ptr((uint32_t)(puVar2 + -0xc18)))) = (short)iVar4;
    input = abs_s16_wrapping((*((short *)camry_host_ptr((uint32_t)(puVar2 + -0xbf2)))));
    iVar4 = interpolate_signed_sentinel_curve((short *)((undefined *)camry_host_ptr(0xb1318u)),input);
    (*((short *)camry_host_ptr((uint32_t)(puVar2 + 0xda6)))) = (short)iVar4;
    uVar1 = (undefined2)( (int)(((int)(short)iVar4 * (int)(*((short *)camry_host_ptr((uint32_t)(puVar2 + -0xc18)))))) / (int)0x400);
  }
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar2 + 0xda8)))) = uVar1;
  return;
}

void differentiate_bf9a_and_saturate_s16_c9524(void)

{
  DAT_febec588 = (int)((int)(int16_t)DAT_febebf9a) - (int)((int)(int16_t)DAT_febec5a4);
  DAT_febec58c = (((int)((int)(int16_t)DAT_febebf9a) - (int)((int)(int16_t)DAT_febec5a4)) * 100) / 0x20;
  DAT_febec5a2 = 0x7fff;
  if ((int)DAT_febec58c + -0x7fff < 0 != ((int)DAT_febec58c < 0 && -1 < (int)DAT_febec58c + -0x7fff) ||
      ((int)(int32_t)DAT_febec58c) == 0x7fff) {
    if ((int)DAT_febec58c + 0x7fff < 0 == (-1 < (int)DAT_febec58c && (int)DAT_febec58c + 0x7fff < 0) &&
        ((int)(int32_t)DAT_febec58c) != -0x7fff) {
      DAT_febec5a2 = (undefined2)((int)(int32_t)DAT_febec58c);
    }
    else {
      DAT_febec5a2 = 0x8001;
    }
  }
  DAT_febec5a4 = ((int)(int16_t)DAT_febebf9a);
  return;
}

void set_c5ac_status_one_c9562(void)

{
  DAT_febec5ac = 1;
  return;
}

void classify_accc_ad6f_nonzero_and_bit1_c956a(void)

{
  if ((DAT_febeaccc != 0) || (DAT_febec5ac = 0, DAT_febead6f != 0)) {
    if (((DAT_febeaccc >> 1 & 1) == 0) && ((DAT_febead6f & 2) == 0)) {
      DAT_febec5ac = 1;
    }
    else {
      DAT_febec5ac = 2;
    }
  }
  return;
}

void fill_constant_block_c9590(void)

{
  DAT_febec5e5 = 1;
  DAT_febec5f2 = 0;
  DAT_febec5e4 = 0;
  DAT_febec5f3 = 0;
  DAT_febec5bc = DAT_000b0180;
  DAT_febec5e6 = 0;
  DAT_febec5c0 = 0;
  DAT_febec5c2 = 0;
  DAT_febeabec = 0;
  DAT_febec5ec = 0;
  DAT_febeabf0 = 0;
  DAT_febeabf2 = 0;
  DAT_febec5c4 = 0;
  DAT_febec5c6 = 0;
  DAT_febeabf4 = 0;
  DAT_febeabf6 = 0;
  DAT_febec5c8 = 0;
  DAT_febec5ca = 0;
  DAT_febec5cc = 0;
  DAT_febec5ce = 0;
  DAT_febec5d0 = 0;
  DAT_febeabfa = 0;
  DAT_febeabf8 = 0;
  DAT_febec5b8 = 0;
  DAT_febec5b0 = 0;
  DAT_febec5ba = 0;
  DAT_febec5be = DAT_000b0180;
  DAT_febec5f4 = 0;
  DAT_febec5ee = 0;
  DAT_febec5b4 = 0;
  DAT_febec5d2 = 0;
  DAT_febec5e7 = 0;
  DAT_febec5e8 = 0;
  DAT_febec5e9 = 0;
  DAT_febec5d6 = 0;
  DAT_febec5d8 = 0;
  return;
}

void fill_constant_block_c962e(void)

{
  DAT_febec5f0 = 0;
  DAT_febec5d4 = 0;
  DAT_febec5ea = 0;
  DAT_febec5de = 0;
  DAT_febec5da = 0;
  DAT_febec5dc = 0;
  DAT_febec5e0 = 0;
  DAT_febec5e2 = 0;
  return;
}

void debounce_c5f2_and_latch_c5f3_enable_c9650(void)

{
  char cVar1;
  
  cVar1 = DAT_febec5e5;
  if ((((DAT_febec5f2 == '\0') && (DAT_000b0187 == '\x01')) && (DAT_febec5ac == 0)) &&
     ((DAT_febeacce == '\x01' && (DAT_febeaf08 == 0x55aaaa55)))) {
    DAT_febec5e4 = DAT_febec5e4 + 1;
    if (DAT_000b0186 <= DAT_febec5e4) {
      DAT_febec5f2 = DAT_febeacce;
    }
  }
  else {
    DAT_febec5e4 = 0;
  }
  if (((((DAT_febec5f3 == '\0') && (DAT_febec5e5 == '\x01')) &&
       ((DAT_febec5f2 == '\x01' &&
        (((DAT_febeacbd == '\0' && (DAT_febeacce == '\x01')) && (DAT_febec601 == '\0')))))) &&
      ((DAT_febec602 == '\0' && (DAT_febeacbe == '\x01')))) &&
     ((DAT_febec5ac == 0 && ((DAT_febead19 == '\0' && ((DAT_febeadfc & 0x1ff) == 0)))))) {
    DAT_febec5e5 = '\0';
    DAT_febec5f3 = cVar1;
  }
  if ((DAT_febec5f3 == '\x01') &&
     ((((DAT_febec601 == '\x01' || (DAT_febec602 == '\x01')) || (DAT_febeacbe == '\0')) ||
      ((((DAT_febec5ac >> 1 & 1) != 0 || (DAT_febec603 == '\x01')) ||
       ((DAT_febead19 == '\"' || ((DAT_febead19 == 'D' || ((DAT_febeadfc & 0x1ff) != 0)))))))))) {
    DAT_febec5f3 = '\0';
  }
  return;
}

short filter_c5b8_between_c5f4_selected_targets_c973a(void)

{
  char cVar1;
  uint32_t puVar2;
  short sVar3;
  int iVar4;
  int iVar5;
  int iVar6;
  
  puVar2 = 0xfebeb800u;
  cVar1 = DAT_febec5f4;
  if (DAT_febec5f4 == '\0') {
    if (((DAT_febec5f3 != '\x01') || (DAT_febec5ac != 0)) ||
       ((DAT_febeacce != '\x01' ||
        ((DAT_febeaccd != '\0' || (cVar1 = DAT_febeacbd == '\0', !(bool)cVar1))))))
    goto LAB_000c978e;
  }
  else {
    if ((((DAT_febec5f3 != '\0') && ((DAT_febec5ac & 1) == 0)) && (DAT_febeacce != '\0')) &&
       ((DAT_febeaccd != '\x01' && (DAT_febeacbd == '\0')))) goto LAB_000c978e;
    cVar1 = false;
  }
  DAT_febec5f4 = cVar1;
  cVar1 = DAT_febec5f4;
LAB_000c978e:
  iVar4 = (int)((int)(int16_t)DAT_febec5be);
  DAT_febec5bc = DAT_000b0180;
  DAT_febec5ba = DAT_000b016e;
  if (cVar1 == '\x01') {
    DAT_febec5bc = DAT_000b017e;
    DAT_febec5ba = DAT_000b016c;
  }
  iVar5 = (int)DAT_febec5bc;
  iVar6 = DAT_febec5b0 * DAT_febec5bc;
  if (iVar4 != 0) {
    if (iVar6 == -0x80000000 && iVar4 == -1) {
      iVar6 = -0x80000000;
    }
    else {
      iVar6 = (int)iVar6 / (int)iVar4;
    }
  }
  DAT_febec5b0 = (((int)(int16_t)DAT_febec5ba) + iVar6) - (int)((int)(int16_t)DAT_febec5b8);
  iVar4 = DAT_febec5b0 * 0x400;
  if (iVar5 != 0) {
    if (iVar4 == -0x80000000 && iVar5 == -1) {
      iVar4 = 0;
    }
    else {
      iVar4 = (int)iVar4 / (int)iVar5;
    }
  }
  DAT_febec5b8 = (short)iVar4;
  DAT_febec5be = DAT_febec5bc;
  sVar3 = abs_s16_wrapping(((int)(int16_t)DAT_febec5b8) - ((int)(int16_t)DAT_febec5ba));
  iVar4 = (int)sVar3;
  if (iVar4 + -0x14 < 0 != (iVar4 < 0 && -1 < iVar4 + -0x14) || iVar4 == 0x14) {
    (*((undefined2 *)camry_host_ptr((uint32_t)(puVar2 + 0xdb8)))) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar2 + 0xdba))));
  }
  return sVar3;
}

void filter_signed_c5fc_curve_with_adf6_gate_c9812(void)

{
  ushort uVar1;
  undefined1 uVar2;
  uint uVar3;
  uint32_t puVar4;
  short input;
  int iVar5;
  int iVar6;
  
  uVar1 = DAT_febeadf6;
  puVar4 = 0xfebeb800u;
  uVar3 = (uint)DAT_febec156;
  if (DAT_febec5f3 != '\x01') {
    return;
  }
  input = abs_s16_wrapping(((int)(int16_t)DAT_febec5fc));
  iVar5 = interpolate_signed_sentinel_curve(((short *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd39dcu + (uint32_t)(uVar3 & 3) * 4u)))))),input);
  if ((*((short *)camry_host_ptr((uint32_t)(puVar4 + 0xdfc)))) < 0) {
    iVar5 = (int)(short)-(short)iVar5;
  }
  (*((short *)camry_host_ptr((uint32_t)(puVar4 + 0xdc0)))) = (short)iVar5;
  if (uVar1 < DAT_000b0170) {
    if (uVar1 != DAT_000b0172) goto LAB_000c987a;
    uVar2 = 0;
  }
  else {
    uVar2 = 1;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(0xde6))))) = uVar2;
LAB_000c987a:
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(0xde6))))) != '\x01') {
    iVar5 = 0;
  }
  (*((short *)camry_host_ptr((uint32_t)(puVar4 + 0xdc2)))) = (short)iVar5;
  iVar5 = ((*((int *)camry_host_ptr((uint32_t)(puVar4 + -0xc14)))) + iVar5) - (int)(*((short *)camry_host_ptr((uint32_t)(puVar4 + 0xdec))));
  (*((int *)camry_host_ptr((uint32_t)(puVar4 + -0xc14)))) = iVar5;
  iVar6 = (int)DAT_000b0174;
  iVar5 = iVar5 * 0x400;
  if (iVar6 != 0) {
    if (iVar5 == -0x80000000 && iVar6 == -1) {
      iVar5 = 0;
    }
    else {
      iVar5 = (int)iVar5 / (int)iVar6;
    }
  }
  (*((short *)camry_host_ptr((uint32_t)(puVar4 + 0xdec)))) = (short)iVar5;
  return;
}

void combine_five_signed_curve_terms_saturating_c98ae(void)

{
  short sVar1;
  uint32_t puVar2;
  short sVar3;
  short sVar4;
  int iVar5;
  int iVar6;
  uint uVar7;
  
  sVar1 = ((int)(int16_t)DAT_febec128);
  sVar4 = ((int)(int16_t)DAT_febeadf0);
  uVar7 = DAT_febec156 & 3;
  puVar2 = 0xfebeb800u;
  if (DAT_febec5f3 == '\x01') {
    puVar2 = 0xfebeb800u;
    sVar3 = abs_s16_wrapping((short)((int)(int8_t)DAT_febec600));
    iVar5 = interpolate_signed_sentinel_curve(((short *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd3a1cu + (uint32_t)(uVar7) * 4u)))))),sVar3);
    sVar3 = (short)iVar5;
    if ((char)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(0xe00))))) < '\0') {
      sVar3 = -sVar3;
    }
    (*((short *)camry_host_ptr((uint32_t)(puVar2 + -0xc10)))) = sVar3;
    sVar3 = abs_s16_wrapping(sVar4);
    iVar5 = interpolate_signed_sentinel_curve(((short *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd3a5cu + (uint32_t)(uVar7) * 4u)))))),sVar3);
    sVar3 = (short)iVar5;
    if (sVar4 < 0) {
      sVar3 = -sVar3;
    }
    (*((short *)camry_host_ptr((uint32_t)(puVar2 + -0xc0e)))) = sVar3;
    sVar3 = abs_s16_wrapping((short)(char)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(0xe00))))));
    iVar5 = interpolate_signed_sentinel_curve(((short *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd3a9cu + (uint32_t)(uVar7) * 4u)))))),sVar3);
    (*((short *)camry_host_ptr((uint32_t)(puVar2 + 0xdc4)))) = (short)iVar5;
    sVar3 = (short)( (int)(((int)(short)iVar5 * (int)(*((short *)camry_host_ptr((uint32_t)(puVar2 + -0xc0e)))))) / (int)0x400);
    (*((short *)camry_host_ptr((uint32_t)(puVar2 + 0xdc6)))) = sVar3;
    if (((0 < sVar1) && (sVar4 < 0)) || ((sVar1 < 0 && (0 < sVar4)))) {
      sVar3 = (short)(((int)DAT_000b0176 * (int)sVar3) / 0x100);
    }
    (*((short *)camry_host_ptr((uint32_t)(puVar2 + -0xc0c)))) = sVar3;
    sVar3 = abs_s16_wrapping((short)(char)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(0xe00))))));
    iVar5 = interpolate_signed_sentinel_curve(((short *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd3adcu + (uint32_t)(uVar7) * 4u)))))),sVar3);
    sVar3 = (short)iVar5;
    if (sVar1 < 0) {
      sVar3 = -sVar3;
    }
    (*((short *)camry_host_ptr((uint32_t)(puVar2 + -0xc0a)))) = sVar3;
    sVar3 = abs_s16_wrapping(sVar4);
    iVar5 = interpolate_signed_sentinel_curve(((short *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd3b1cu + (uint32_t)(uVar7) * 4u)))))),sVar3);
    (*((short *)camry_host_ptr((uint32_t)(puVar2 + 0xdc8)))) = (short)iVar5;
    sVar3 = (short)( (int)(((int)(short)iVar5 * (int)(*((short *)camry_host_ptr((uint32_t)(puVar2 + -0xc0a)))))) / (int)0x400);
    iVar5 = (int)sVar3;
    (*((short *)camry_host_ptr((uint32_t)(puVar2 + 0xdca)))) = sVar3;
    if (((0 < sVar1) && (sVar4 < 0)) || ((sVar1 < 0 && (0 < sVar4)))) {
      sVar4 = abs_s16_wrapping((*((short *)camry_host_ptr((uint32_t)(puVar2 + 0xdcc)))));
      iVar6 = (int)sVar4;
      iVar5 = (int)DAT_000b0178;
      if (iVar6 - iVar5 < 0 == (iVar6 < 0 != iVar5 < 0 && iVar5 < 0 == iVar6 - iVar5 < 0) &&
          iVar6 != iVar5) {
        iVar5 = (int)(*((short *)camry_host_ptr((uint32_t)(puVar2 + 0xdcc))));
        iVar6 = (int)DAT_000b017a;
        sVar4 = DAT_000b0178;
        if (iVar5 - iVar6 < 0 == (iVar5 < 0 != iVar6 < 0 && iVar6 < 0 == iVar5 - iVar6 < 0) &&
            iVar5 != iVar6) {
          sVar4 = -DAT_000b0178;
        }
        iVar5 = (int)(short)((*((short *)camry_host_ptr((uint32_t)(puVar2 + 0xdcc)))) + sVar4);
      }
      else {
        iVar5 = 0;
      }
      sVar3 = (short)iVar5;
    }
    (*((short *)camry_host_ptr((uint32_t)(puVar2 + 0xdcc)))) = sVar3;
  }
  else {
    DAT_febeabf0 = 0;
    iVar5 = 0;
    DAT_febeabf4 = 0;
  }
  (*((short *)camry_host_ptr((uint32_t)(puVar2 + 0xdce)))) = (short)iVar5;
  iVar5 = iVar5 + (int)(*((short *)camry_host_ptr((uint32_t)(puVar2 + -0xc0c)))) + (int)(*((short *)camry_host_ptr((uint32_t)(puVar2 + -0xc10))));
  if (iVar5 + -0x7fff < 0 == (iVar5 < 0 && -1 < iVar5 + -0x7fff) && iVar5 != 0x7fff) {
    iVar5 = 0x7fff;
  }
  else if (iVar5 + 0x7fff < 0 != (-1 < iVar5 && iVar5 + 0x7fff < 0)) {
    iVar5 = -0x7fff;
  }
  (*((short *)camry_host_ptr((uint32_t)(puVar2 + 0xdd0)))) = (short)iVar5;
  (*((short *)camry_host_ptr((uint32_t)(puVar2 + -0xc06)))) =
       (short)( (int)(((int)(*((short *)camry_host_ptr((uint32_t)(puVar2 + -0xc08)))) * (int)(short)iVar5)) / (int)0x400);
  return;
}

void interpolate_adf6_into_abf8_gain_c9a5c(void)

{
  uint32_t puVar1;
  int iVar2;
  
  puVar1 = 0xfebeb800u;
  iVar2 = interpolate_unsigned_axis_sentinel_curve
                    (((ushort *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd3b5cu + (uint32_t)(DAT_febec156 & 3) * 4u)))))),DAT_febeadf6);
  (*((short *)camry_host_ptr((uint32_t)(puVar1 + -0xc08)))) = (short)iVar2;
  return;
}

void clamp_and_blend_c5ec_abfa_by_c5b8_c9a84(void)

{
  int iVar1;
  int iVar2;
  uint32_t puVar3;
  short sVar4;
  int iVar5;
  int iVar6;
  
  puVar3 = 0xfebeb800u;
  iVar5 = (int)((int)(int16_t)DAT_febec5b8);
  iVar1 = (int)DAT_000b016e;
  iVar6 = (int)DAT_000b016c;
  if ((iVar5 - iVar6 < 0 != (iVar5 < 0 != iVar6 < 0 && iVar6 < 0 == iVar5 - iVar6 < 0) ||
       iVar5 == iVar6) &&
     (iVar6 = iVar1,
     iVar5 - iVar1 < 0 == (iVar5 < 0 != iVar1 < 0 && iVar1 < 0 == iVar5 - iVar1 < 0) &&
     iVar5 != iVar1)) {
    iVar6 = iVar5;
  }
  if ((DAT_febec5f3 == '\x01') ||
     (iVar6 - iVar1 < 0 == (iVar6 < 0 != iVar1 < 0 && iVar1 < 0 == iVar6 - iVar1 < 0) &&
      iVar6 != iVar1)) {
    puVar3 = 0xfebeb800u;
    sVar4 = abs_s16_wrapping(((int)(int16_t)DAT_febec5fc));
    if (0 < sVar4) {
      (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0xc06)))) = 0;
    }
    sVar4 = DAT_000b017c;
    iVar5 = (int)DAT_000b017c;
    iVar1 = (int)(*((short *)camry_host_ptr((uint32_t)(puVar3 + 0xdec)))) + (int)(*((short *)camry_host_ptr((uint32_t)(puVar3 + -0xc06))));
    (*((int *)camry_host_ptr((uint32_t)(puVar3 + 0xdb4)))) = iVar1;
    if (iVar1 - iVar5 < 0 != (iVar1 < 0 != iVar5 < 0 && iVar5 < 0 == iVar1 - iVar5 < 0) ||
        iVar1 == iVar5) {
      iVar2 = -iVar5;
      if (iVar1 + iVar5 < 0 == (iVar1 < 0 != iVar2 < 0 && iVar2 < 0 == iVar1 + iVar5 < 0) &&
          iVar1 != iVar2) {
        iVar2 = iVar1;
      }
      sVar4 = (short)iVar2;
    }
  }
  else {
    sVar4 = 0;
  }
  (*((short *)camry_host_ptr((uint32_t)(puVar3 + 0xdd2)))) = sVar4;
  (*((short *)camry_host_ptr((uint32_t)(puVar3 + 0xdee)))) = (short)(((int)(short)iVar6 * (int)sVar4) / 0x400);
  return;
}

void step_c5e7_magnitude_hysteresis_and_holdoff_c9b04(void)

{
  bool bVar1;
  int iVar2;
  int iVar3;
  undefined1 uVar4;
  int iVar5;
  
  iVar2 = (int)((int)(int8_t)DAT_febec600);
  iVar5 = (int)DAT_000b0188;
  iVar3 = (int)DAT_000b0189;
  if (iVar2 < 0) {
    iVar2 = (int)-((int)(int8_t)DAT_febec600);
  }
  if ((DAT_febec5f4 == '\x01') &&
     (iVar2 - iVar5 < 0 == (iVar2 < 0 != iVar5 < 0 && iVar5 < 0 == iVar2 - iVar5 < 0) &&
      iVar2 != iVar5)) {
    uVar4 = DAT_000b0182 < DAT_febeadf6;
  }
  else {
    uVar4 = false;
  }
  DAT_febec5e8 = (bool)uVar4;
  if (((DAT_febec5f4 == '\0') ||
      (iVar2 - iVar3 < 0 != (iVar2 < 0 != iVar3 < 0 && iVar3 < 0 == iVar2 - iVar3 < 0) ||
       iVar2 == iVar3)) || (DAT_febeadf6 <= DAT_000b0182)) {
    DAT_febec5e9 = 2;
    bVar1 = true;
  }
  else {
    DAT_febec5e9 = 0;
    bVar1 = false;
  }
  if (DAT_febec5e7 == '\0') {
    if (!(bool)uVar4) {
      return;
    }
  }
  else if (DAT_febec5e7 == '\x01') {
    if (!bVar1) {
      return;
    }
    DAT_febec5d6 = 0;
    uVar4 = 2;
  }
  else if (!(bool)uVar4) {
    if (DAT_febec5d6 <= DAT_000b0184) {
      DAT_febec5d6 = DAT_febec5d6 + 1;
    }
    if (DAT_febec5d6 <= DAT_000b0184) {
      return;
    }
    uVar4 = 0;
  }
  DAT_febec5e7 = uVar4;
  return;
}

void interpolate_adf6_into_c5d8_gain_c9ba6(void)

{
  uint32_t puVar1;
  int iVar2;
  
  puVar1 = 0xfebeb800u;
  iVar2 = interpolate_unsigned_axis_sentinel_curve
                    (((ushort *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd3b9cu + (uint32_t)(DAT_febec156 & 3) * 4u)))))),DAT_febeadf6);
  (*((short *)camry_host_ptr((uint32_t)(puVar1 + 0xdd8)))) = (short)iVar2;
  return;
}

ushort interpolate_abs_ac42_and_scale_c5f0_c9bce(void)

{
  char cVar1;
  undefined2 uVar2;
  short sVar3;
  short sVar4;
  uint uVar5;
  uint uVar6;
  uint32_t puVar7;
  ushort uVar8;
  uint32_t puVar9;
  
  cVar1 = DAT_febec5e7;
  sVar4 = ((int)(int16_t)DAT_febeac42);
  puVar7 = 0xfebeb800u;
  uVar5 = (uint)DAT_febec156;
  uVar8 = abs_s16_wrapping(((int)(int16_t)DAT_febeac42));
  uVar2 = 0;
  if (cVar1 == '\x01' || cVar1 == '\x02') {
    uVar6 = (uint)(uVar8 >> 8);
    puVar9 = ((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd3bdcu + (uint32_t)(uVar5 & 3) * 4u))))));
    if (uVar6 < 0x7f) {
      sVar3 = (short)((int)((uint)(byte)uVar8 *
                           ((int)(*((volatile int16_t *)camry_host_ptr((uint32_t)(puVar9 + (uVar6 + 1) * 4 + 2)))) -
                           (int)(*((volatile int16_t *)camry_host_ptr((uint32_t)(puVar9 + uVar6 * 4 + 2)))))) / 0x100) +
              (*((volatile int16_t *)camry_host_ptr((uint32_t)(puVar9 + uVar6 * 4 + 2))));
    }
    else {
      sVar3 = (*((volatile int16_t *)camry_host_ptr((uint32_t)(puVar9 + 0x1fe))));
    }
    (*((short *)camry_host_ptr((uint32_t)(puVar7 + 0xde2)))) = (short)(uVar5 & 3);
    (*((ushort *)camry_host_ptr((uint32_t)(puVar7 + 0xdda)))) = uVar8;
    if (sVar4 < 0) {
      sVar3 = -sVar3;
    }
    (*((short *)camry_host_ptr((uint32_t)(puVar7 + 0xdd4)))) = sVar3;
    (*((short *)camry_host_ptr((uint32_t)(puVar7 + 0xddc)))) = sVar4;
    (*((short *)camry_host_ptr((uint32_t)(puVar7 + 0xdde)))) = (*((short *)camry_host_ptr((uint32_t)(puVar7 + 0xdd8))));
    sVar4 = (short)( (int)(((int)(*((short *)camry_host_ptr((uint32_t)(puVar7 + 0xdd8)))) * (int)sVar3)) / (int)0x400);
    (*((short *)camry_host_ptr((uint32_t)(puVar7 + 0xde0)))) = sVar4;
    uVar2 = (undefined2)(((int)sVar4 << 10) / 0x400);
  }
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar7 + 0xdf0)))) = uVar2;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar7 + (uint32_t)(0xdea))))) = cVar1;
  return uVar8;
}

void fill_constant_block_c9c7c(void)

{
  DAT_febec5fc = 0;
  DAT_febec600 = 0;
  DAT_febec5f6 = 0;
  DAT_febec5f7 = 0;
  DAT_febec601 = 0;
  DAT_febec602 = 0;
  DAT_febec5fe = 0;
  DAT_febec603 = 0;
  DAT_febec5fa = 0;
  DAT_febec5f8 = 0;
  DAT_febec5f9 = 0;
  return;
}

void clamp_ae06_and_report_event_c8_once_c9caa(void)

{
  bool bVar1;
  bool bVar2;
  short sVar3;
  int iVar4;
  int iVar5;
  uint32_t puVar6;
  short sVar7;
  int iVar9;
  int iVar8;
  
  sVar3 = ((int)(int16_t)DAT_febeae06);
  puVar6 = 0xfebeb800u;
  iVar9 = (int)((int)(int16_t)DAT_febeae06);
  sVar7 = abs_s16_wrapping(((int)(int16_t)DAT_febeae06));
  iVar8 = (int)sVar7;
  iVar4 = (int)DAT_000b044a;
  iVar5 = (int)DAT_000b044a;
  bVar2 = iVar8 - iVar4 < 0 == (iVar8 < 0 != iVar4 < 0 && iVar4 < 0 == iVar8 - iVar4 < 0);
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(0xdf6))))) = bVar2 && iVar8 != iVar4;
  sVar7 = DAT_000b044a;
  if ((iVar9 - iVar5 < 0 != (iVar9 < 0 != iVar5 < 0 && iVar5 < 0 == iVar9 - iVar5 < 0) ||
       iVar9 == iVar5) &&
     (iVar5 = iVar9 + DAT_000b044a, bVar1 = -(int)DAT_000b044a < 0, sVar7 = sVar3,
     iVar5 < 0 != (iVar9 < 0 != bVar1 && bVar1 == iVar5 < 0))) {
    sVar7 = -DAT_000b044a;
  }
  (*((short *)camry_host_ptr((uint32_t)(puVar6 + 0xdfc)))) = sVar7;
  if (bVar2 && iVar8 != iVar4) {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(0xe01))))) = 1;
  }
  if ((((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(0xdf2))))) == '\x01') && ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(0xe01))))) == '\x01')) && ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(0xdf8))))) == '\0')) {
    report_diagnostic_event_failure_ffff_32_bdb64(200);
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(0xdf8))))) = 1;
  }
  return;
}

short clamp_ae04_to_byte_and_report_event_c9_once_c9d18(void)

{
  bool bVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  uint32_t puVar6;
  short sVar7;
  int iVar9;
  int iVar8;
  
  puVar6 = 0xfebeb800u;
  iVar9 = (int)((int)(int16_t)DAT_febeae04);
  sVar7 = abs_s16_wrapping(((int)(int16_t)DAT_febeae04));
  iVar8 = (int)sVar7;
  iVar2 = (int)DAT_000b044c;
  iVar3 = (int)DAT_000b044c;
  bVar1 = iVar8 - iVar2 < 0 == (iVar8 < 0 != iVar2 < 0 && iVar2 < 0 == iVar8 - iVar2 < 0);
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(0xdf7))))) = bVar1 && iVar8 != iVar2;
  iVar4 = (int)DAT_000b044c;
  iVar5 = iVar4;
  if ((iVar9 - iVar3 < 0 != (iVar9 < 0 != iVar3 < 0 && iVar3 < 0 == iVar9 - iVar3 < 0) ||
       iVar9 == iVar3) &&
     (iVar5 = iVar9,
     iVar9 + iVar4 < 0 != (iVar9 < 0 != -iVar4 < 0 && -iVar4 < 0 == iVar9 + iVar4 < 0))) {
    iVar5 = -(int)DAT_000b044c;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(0xe00))))) = (char)iVar5;
  if (bVar1 && iVar8 != iVar2) {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(0xe02))))) = 1;
  }
  if ((((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(0xdf2))))) == '\x01') && ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(0xe02))))) == '\x01')) && ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(0xdf9))))) == '\0')) {
    report_diagnostic_event_failure_ffff_32_bdb64(0xc9);
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(0xdf9))))) = 1;
  }
  return sVar7;
}

void debounce_c5ee_magnitude_and_report_event_ca_c9d86(void)

{
  ushort uVar1;
  ushort uVar2;
  int iVar3;
  uint32_t puVar4;
  short sVar5;
  int iVar6;
  
  puVar4 = 0xfebeb800u;
  if (DAT_febec5f3 == '\x01') {
    puVar4 = 0xfebeb800u;
    sVar5 = abs_s16_wrapping(((int)(int16_t)DAT_febec5ee));
    uVar2 = DAT_000b0446;
    iVar6 = (int)sVar5;
    iVar3 = (int)DAT_000b0448;
    if (iVar6 - iVar3 < 0 == (iVar6 < 0 != iVar3 < 0 && iVar3 < 0 == iVar6 - iVar3 < 0) &&
        iVar6 != iVar3) {
      uVar1 = (*((ushort *)camry_host_ptr((uint32_t)(puVar4 + 0xdfe))));
      if ((uVar1 <= DAT_000b0446) &&
         ((*((ushort *)camry_host_ptr((uint32_t)(puVar4 + 0xdfe)))) = uVar1 + 1, uVar2 < (ushort)(uVar1 + 1))) {
        (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(0xe03))))) = 1;
      }
      goto LAB_000c9dd0;
    }
  }
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar4 + 0xdfe)))) = 0;
LAB_000c9dd0:
  if (((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(0xe03))))) == '\x01') && ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(0xdfa))))) == '\0')) {
    report_diagnostic_event_failure_ffff_32_bdb64(0xca);
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(0xdfa))))) = 1;
  }
  return;
}

void fill_constant_block_c9df2(void)

{
  DAT_febec608 = 1;
  DAT_febec609 = 1;
  DAT_febec60a = 1;
  DAT_febec604 = 0;
  DAT_febec606 = 0;
  return;
}

void clear_c60c_c60e_c60f_record_c9e0a(void)

{
  DAT_febec60c = 0;
  DAT_febec60e = 0;
  DAT_febec60f = 0;
  return;
}

void load_ae10_acf0_acef_record_increment_a5_c9e18(void)

{
  DAT_febec60e = DAT_febeacf0;
  DAT_febec60f = DAT_febeacef;
  DAT_febec60c = DAT_febeae10;
  if ((((int8_t)DAT_febeacf0) == -0x5b) && (((int8_t)DAT_febeacef) != -1)) {
    DAT_febec60f = DAT_febeacef + '\x01';
  }
  return;
}

void rearm_c608_after_two_magnitude_timeouts_c9e44(void)

{
  int iVar1;
  ushort uVar2;
  ushort uVar3;
  int iVar4;
  uint32_t puVar5;
  short sVar6;
  
  puVar5 = 0xfebeb800u;
  if (DAT_febec5f3 == '\x01') {
    sVar6 = abs_s16_wrapping(((int)(int16_t)DAT_febec5ec));
    uVar3 = DAT_000b0452;
    iVar4 = (int)DAT_000b044e;
    iVar1 = sVar6 - iVar4;
    if (iVar1 < 0 == (sVar6 < 0 != iVar4 < 0 && iVar4 < 0 == iVar1 < 0)) {
      uVar2 = (*((ushort *)camry_host_ptr((uint32_t)(puVar5 + 0xe04))));
      if ((uVar2 < DAT_000b0452) &&
         ((*((ushort *)camry_host_ptr((uint32_t)(puVar5 + 0xe04)))) = uVar2 + 1, uVar3 <= (ushort)(uVar2 + 1))) {
        (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(0xe09))))) = 0;
      }
    }
    else {
      (*((undefined2 *)camry_host_ptr((uint32_t)(puVar5 + 0xe04)))) = 0;
    }
    sVar6 = abs_s16_wrapping((*((short *)camry_host_ptr((uint32_t)(puVar5 + -0xc06)))));
    uVar3 = DAT_000b0454;
    iVar4 = (int)DAT_000b0450;
    iVar1 = sVar6 - iVar4;
    if (iVar1 < 0 == (sVar6 < 0 != iVar4 < 0 && iVar4 < 0 == iVar1 < 0)) {
      uVar2 = (*((ushort *)camry_host_ptr((uint32_t)(puVar5 + 0xe06))));
      if ((uVar2 < DAT_000b0454) &&
         ((*((ushort *)camry_host_ptr((uint32_t)(puVar5 + 0xe06)))) = uVar2 + 1, uVar3 <= (ushort)(uVar2 + 1))) {
        (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(0xe0a))))) = 0;
      }
    }
    else {
      (*((undefined2 *)camry_host_ptr((uint32_t)(puVar5 + 0xe06)))) = 0;
    }
    if (((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(0xe09))))) == '\0') || ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(0xe0a))))) == '\0')) {
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(0xe08))))) = 0;
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(0xe09))))) = 1;
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(0xe0a))))) = 1;
    }
  }
  return;
}

void record_c5f3_activation_with_a5_marker_c9eea(void)

{
  if ((DAT_febec5f3 == '\x01') && (DAT_febec608 == '\0')) {
    DAT_febec60e = 0xa5;
    DAT_febec60f = 0;
    if (DAT_febec60c < 0xff) {
      DAT_febec60c = DAT_febec60c + 1;
    }
    DAT_febec608 = '\x01';
  }
  return;
}

void store_c60c_record_to_ae10_acf0_acef_c9f1e(void)

{
  DAT_febeae10 = DAT_febec60c;
  DAT_febeacf0 = DAT_febec60e;
  DAT_febeacef = DAT_febec60f;
  return;
}

void reset_c610_monitors_and_seed_twenty_samples_c9f38(void)

{
  int iVar1;
  undefined4 uVar2;
  uint uVar3;
  
  uVar2 = DAT_febeaee8;
  DAT_febec61c = 0;
  DAT_febec618 = 0;
  DAT_febec614 = 0;
  DAT_febec610 = 0;
  DAT_febec686 = 0;
  DAT_febec685 = 0;
  DAT_febec628 = 0;
  DAT_febec684 = 0;
  DAT_febec626 = 0;
  DAT_febec683 = 0;
  DAT_febec624 = 0;
  DAT_febec682 = 0;
  DAT_febec622 = 0;
  DAT_febec681 = 0;
  DAT_febec680 = 0;
  DAT_febec620 = 0;
  uVar3 = 0;
  do {
    iVar1 = uVar3 * 4;
    uVar3 = uVar3 + 1;
    *(undefined4 *)(((undefined *)camry_host_ptr((uint32_t)(0xfebec630u + (uint32_t)(iVar1) * 1u)))) = uVar2;
  } while (uVar3 < 0x14);
  DAT_febec62a = 0;
  DAT_febec62b = 0;
  DAT_febec62c = 0;
  DAT_febec62d = 0;
  return;
}

void debounce_c724_c725_and_report_event_10e_c9fa2(void)

{
  ushort uVar1;
  ushort uVar2;
  uint32_t puVar3;
  char cVar4;
  
  puVar3 = 0xfebeb800u;
  cVar4 = DAT_febec680;
  if (DAT_febec680 == '\0') {
    if ((DAT_febec6b0 == '\x01') && ((DAT_febec724 == '\x01' || (DAT_febec725 == '\x01')))) {
      if ((DAT_febec620 < DAT_000b0458) &&
         (uVar1 = DAT_febec620 + 1, uVar2 = DAT_febec620 + 1, DAT_febec620 = uVar1,
         DAT_000b0458 <= uVar2)) {
        DAT_febec680 = DAT_febec6b0;
        cVar4 = DAT_febec6b0;
      }
    }
    else {
      DAT_febec620 = 0;
    }
  }
  else if (DAT_febec6b0 == '\0') {
    DAT_febec620 = 0;
    DAT_febec680 = '\0';
    cVar4 = DAT_febec6b0;
  }
  if (((DAT_febec6ae == '\x01') && (cVar4 == '\x01')) && (DAT_febec62a == '\0')) {
    report_diagnostic_event_failure_ffff_32_bdb64(0x10e);
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(0xe2a))))) = 1;
  }
  return;
}
