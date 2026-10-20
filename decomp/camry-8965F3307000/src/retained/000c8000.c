#include "common.h"

void initialize_directional_rate_compensation(void)

{
  DAT_febec460 = 0;
  DAT_febec462 = 0;
  DAT_febec470 = 0;
  DAT_febec464 = 0;
  DAT_febec466 = 0;
  DAT_febec468 = 0;
  DAT_febec46a = 0;
  DAT_febec46c = 0;
  DAT_febec46e = 0;
  DAT_febec472 = 0;
  DAT_febec45c = 0;
  return;
}

void qualify_opposed_rate_direction(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  int iVar6;
  int iVar7;
  
  iVar4 = (int)((int)(int16_t)DAT_febeadf2);
  iVar3 = (int)DAT_000affdc;
  iVar2 = (int)DAT_000affde;
  iVar1 = (int)((int)(int16_t)DAT_febec460);
  iVar7 = (int)((int)(int16_t)DAT_febec462);
  iVar5 = (int)DAT_000affe0;
  iVar6 = (int)((int)(int16_t)DAT_febec18a);
  if ((iVar4 - iVar3 < 0 == (iVar4 < 0 != iVar3 < 0 && iVar3 < 0 == iVar4 - iVar3 < 0) &&
       iVar4 != iVar3) &&
     (iVar6 + iVar2 < 0 != (iVar6 < 0 != -iVar2 < 0 && -iVar2 < 0 == iVar6 + iVar2 < 0))) {
    if (iVar1 - iVar5 < 0 != (iVar1 < 0 != iVar5 < 0 && iVar5 < 0 == iVar1 - iVar5 < 0) ||
        iVar1 == iVar5) {
      DAT_febec460 = ((int)(int16_t)DAT_febec460) + 1;
      iVar1 = (int)((int)(int16_t)DAT_febec460);
      if (iVar1 - iVar5 < 0 == (iVar1 < 0 != iVar5 < 0 && iVar5 < 0 == iVar1 - iVar5 < 0) &&
          iVar1 != iVar5) {
        DAT_febec470 = '\x01';
      }
    }
    DAT_febec462 = 0;
  }
  else if ((iVar4 + iVar3 < 0 == (iVar4 < 0 != -iVar3 < 0 && -iVar3 < 0 == iVar4 + iVar3 < 0)) ||
          (iVar6 - iVar2 < 0 != (iVar6 < 0 != iVar2 < 0 && iVar2 < 0 == iVar6 - iVar2 < 0) ||
           iVar6 == iVar2)) {
    DAT_febec460 = 0;
    DAT_febec462 = 0;
  }
  else {
    if (iVar7 - iVar5 < 0 != (iVar7 < 0 != iVar5 < 0 && iVar5 < 0 == iVar7 - iVar5 < 0) ||
        iVar7 == iVar5) {
      DAT_febec462 = ((int)(int16_t)DAT_febec462) + 1;
      iVar1 = (int)((int)(int16_t)DAT_febec462);
      if (iVar1 - iVar5 < 0 == (iVar1 < 0 != iVar5 < 0 && iVar5 < 0 == iVar1 - iVar5 < 0) &&
          iVar1 != iVar5) {
        DAT_febec470 = '\x02';
      }
    }
    DAT_febec460 = 0;
  }
  if (DAT_febec470 == '\x01') {
    DAT_febec470 = iVar6 < 0;
    if (!(bool)DAT_febec470) {
      DAT_febec460 = 0;
    }
  }
  else if (DAT_febec470 == '\x02') {
    if (iVar6 < 1) {
      DAT_febec470 = 0;
      DAT_febec462 = 0;
    }
    else {
      DAT_febec470 = 2;
    }
  }
  else {
    DAT_febec470 = 0;
  }
  return;
}

void update_directional_rate_speed_gain(void)

{
  uint32_t puVar1;
  int iVar2;
  
  puVar1 = 0xfebeb800u;
  iVar2 = interpolate_unsigned_axis_sentinel_curve((ushort *)((undefined *)camry_host_ptr(0xafffeu)),DAT_febeadf6);
  (*((short *)camry_host_ptr((uint32_t)(puVar1 + 0xc6e)))) = (short)iVar2;
  return;
}

void filter_directional_rate_compensation(void)

{
  int iVar1;
  uint32_t puVar2;
  short input;
  short sVar3;
  short sVar4;
  int iVar5;
  int iVar7;
  ushort uVar8;
  int iVar6;
  
  sVar3 = ((int)(int16_t)DAT_febec18a);
  sVar4 = ((int)(int16_t)DAT_febeae4a);
  puVar2 = 0xfebeb800u;
  iVar7 = (int)((int)(int16_t)DAT_febec46c);
  input = abs_s16_wrapping(((int)(int16_t)DAT_febec18a));
  (*((short *)camry_host_ptr((uint32_t)(puVar2 + 0xc64)))) = input;
  iVar5 = interpolate_signed_sentinel_curve((short *)((undefined *)camry_host_ptr(0xaffe6u)),input);
  uVar8 = (ushort)(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(0xc70)))));
  if (((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(0xc70))))) != 0) &&
     (uVar8 = (ushort)( (int)(((int)(*((short *)camry_host_ptr((uint32_t)(puVar2 + 0xc6e)))) * (int)(short)iVar5 + 0x200)) / (int)0x400),
     sVar3 < 0)) {
    uVar8 = -uVar8;
  }
  sVar4 = (short)(((int)sVar4 * (int)(short)uVar8) / 0x400);
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(0xdf4))))) == '\x01') {
    sVar3 = abs_s16_wrapping((*((short *)camry_host_ptr((uint32_t)(puVar2 + 0xdec)))));
    iVar6 = (int)sVar3;
    iVar1 = (int)DAT_000affe4;
    if (iVar6 - iVar1 < 0 == (iVar6 < 0 != iVar1 < 0 && iVar1 < 0 == iVar6 - iVar1 < 0) &&
        iVar6 != iVar1) {
      sVar4 = 0;
    }
  }
  sVar4 = scale_rate_assist_term(sVar4);
  iVar1 = directional_rate_filter_denominator;
  (*((short *)camry_host_ptr((uint32_t)(puVar2 + 0xc66)))) = (short)iVar5;
  (*((ushort *)camry_host_ptr((uint32_t)(puVar2 + 0xc68)))) = uVar8;
  (*((short *)camry_host_ptr((uint32_t)(puVar2 + 0xc6a)))) = sVar4;
  iVar7 = ((*((int *)camry_host_ptr((uint32_t)(puVar2 + 0xc5c)))) + (int)sVar4) - iVar7;
  (*((int *)camry_host_ptr((uint32_t)(puVar2 + 0xc5c)))) = iVar7;
  iVar7 = iVar7 * 0x400;
  if (iVar1 != 0) {
    if (iVar7 == -0x80000000 && iVar1 == -1) {
      iVar7 = 0;
    }
    else {
      iVar7 = (int)iVar7 / (int)iVar1;
    }
  }
  (*((short *)camry_host_ptr((uint32_t)(puVar2 + 0xc6c)))) = (short)iVar7;
  return;
}

void publish_directional_rate_compensation(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  
  iVar3 = (int)((int)(int16_t)DAT_febec46c);
  iVar2 = (int)DAT_000affe2;
  DAT_febec472 = DAT_000affe2;
  if ((iVar3 - iVar2 < 0 != (iVar3 < 0 != iVar2 < 0 && iVar2 < 0 == iVar3 - iVar2 < 0) ||
       iVar3 == iVar2) &&
     (iVar1 = -iVar2, DAT_febec472 = ((int)(int16_t)DAT_febec46c),
     iVar3 + iVar2 < 0 != (iVar3 < 0 != iVar1 < 0 && iVar1 < 0 == iVar3 + iVar2 < 0) ||
     iVar3 == iVar1)) {
    DAT_febec472 = (short)iVar1;
  }
  return;
}

void clear_c474_c476_curve_outputs_c81ee(void)

{
  DAT_febec474 = 0;
  DAT_febec476 = 0;
  return;
}

void interpolate_two_signed_ae4a_curves_into_c474_c476_c81f8(void)

{
  short input;
  uint32_t puVar1;
  int iVar2;
  
  input = ((int)(int16_t)DAT_febeae4a);
  puVar1 = 0xfebeb800u;
  iVar2 = interpolate_signed_sentinel_curve((short *)((undefined *)camry_host_ptr(0xb001au)),((int)(int16_t)DAT_febeae4a));
  (*((short *)camry_host_ptr((uint32_t)(puVar1 + 0xc74)))) = (short)iVar2;
  iVar2 = interpolate_signed_sentinel_curve((short *)((undefined *)camry_host_ptr(0xb003eu)),input);
  (*((short *)camry_host_ptr((uint32_t)(puVar1 + 0xc76)))) = (short)iVar2;
  return;
}

void reset_c478_filter_and_abb8_scaled_output_state_c8224(void)

{
  DAT_febeabbc = 0;
  DAT_febec49d = 0x5a;
  DAT_febec4a0 = 0;
  DAT_febeabc2 = 0;
  DAT_febec48c = 0;
  DAT_febec480 = PTR_DAT_000b0068;
  DAT_febec48e = 0;
  DAT_febeabc4 = 0x400;
  DAT_febeabc6 = 0x400;
  DAT_febec490 = 0;
  DAT_febec492 = 0;
  DAT_febec498 = DAT_000b0084;
  DAT_febec494 = 0;
  DAT_febeabb8 = 0;
  DAT_febeabbe = 0;
  DAT_febeabc0 = 0;
  DAT_febec478 = 0;
  DAT_febec47c = 0;
  DAT_febec49c = 0;
  DAT_febec488 = 0;
  DAT_febec48a = 0;
  DAT_febec49e = 0;
  DAT_febec496 = 0;
  DAT_febec49a = DAT_000b0084;
  DAT_febec484 = (uint)DAT_000b0084;
  return;
}

void interpolate_unsigned_b00ae_curve_into_abbc_c82a8(void)

{
  uint32_t puVar1;
  undefined2 uVar2;
  
  puVar1 = 0xfebeb800u;
  uVar2 = interpolate_unsigned16_axis_and_values_d0896(((undefined *)camry_host_ptr(0xb00aeu)),DAT_febeadf6);
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0xc44)))) = uVar2;
  return;
}

void lookup_signed_magnitude_scale_by_ae4a_and_filter_abbe_c82c2(ushort param_1,short param_2)

{
  int iVar1;
  short sVar2;
  uint32_t puVar3;
  int iVar4;
  short sVar5;
  short sVar6;
  int iVar7;
  
  sVar2 = ((int)(int16_t)DAT_febeae4a);
  puVar3 = 0xfebeb800u;
  iVar4 = interpolate_unsigned_axis_sentinel_curve((ushort *)((undefined *)camry_host_ptr(0xb0086u)),param_1);
  sVar6 = (short)iVar4;
  if (param_2 < 0) {
    iVar4 = (int)-sVar6;
  }
  (*((short *)camry_host_ptr((uint32_t)(puVar3 + 0xc8e)))) = (short)iVar4;
  (*((short *)camry_host_ptr((uint32_t)(puVar3 + 0xc8c)))) = sVar6;
  sVar5 = (short)((int)(iVar4 * (uint)(*((ushort *)camry_host_ptr((uint32_t)(puVar3 + -0xc44))))) / 0x400);
  (*((short *)camry_host_ptr((uint32_t)(puVar3 + 0xc90)))) = sVar5;
  sVar6 = DAT_000b0070;
  iVar7 = (int)DAT_000b0070;
  sVar2 = (short)(((int)sVar2 * (int)sVar5) / 0x400);
  iVar4 = (int)sVar2;
  (*((short *)camry_host_ptr((uint32_t)(puVar3 + 0xc92)))) = sVar2;
  if ((iVar4 - iVar7 < 0 != (iVar4 < 0 != iVar7 < 0 && iVar7 < 0 == iVar4 - iVar7 < 0) ||
       iVar4 == iVar7) &&
     (iVar1 = -iVar7, sVar6 = sVar2,
     iVar4 + iVar7 < 0 != (iVar4 < 0 != iVar1 < 0 && iVar1 < 0 == iVar4 + iVar7 < 0) ||
     iVar4 == iVar1)) {
    sVar6 = (short)iVar1;
  }
  (*((short *)camry_host_ptr((uint32_t)(puVar3 + 0xc94)))) = sVar6;
  iVar4 = ((*((int *)camry_host_ptr((uint32_t)(puVar3 + -0xc48)))) + (int)sVar6) - (int)(*((short *)camry_host_ptr((uint32_t)(puVar3 + -0xc42))));
  (*((int *)camry_host_ptr((uint32_t)(puVar3 + -0xc48)))) = iVar4;
  iVar4 = iVar4 * 0x400;
  if (DAT_000b0064 != 0) {
    if (iVar4 == -0x80000000 && DAT_000b0064 == -1) {
      iVar4 = 0;
    }
    else {
      iVar4 = (int)iVar4 / (int)DAT_000b0064;
    }
  }
  (*((short *)camry_host_ptr((uint32_t)(puVar3 + -0xc42)))) = (short)iVar4;
  return;
}

void step_unsigned_abc0_enable_envelope_with_latch_c8350(ushort param_1,char param_2)

{
  uint uVar1;
  
  uVar1 = (uint)DAT_febeabc0;
  if (((param_2 == '\0') || (DAT_febead18 != '\x11')) || (DAT_febead41 == 'Z')) {
    DAT_febec478 = DAT_febec47c * (int)PTR_DAT_000b0068;
    DAT_febec49c = 'Z';
    if (DAT_febec480 != 0) {
      DAT_febec478 = DAT_febec478 / (uint)DAT_febec480;
    }
    DAT_febec47c = DAT_febec478 - uVar1;
    uVar1 = DAT_febec47c * 0x400;
    if (PTR_DAT_000b0068 != 0) {
      uVar1 = uVar1 / (uint)PTR_DAT_000b0068;
    }
    uVar1 = uVar1 & 0xffff;
    DAT_febec480 = PTR_DAT_000b0068;
  }
  else {
    if (DAT_febec49c == '\0') {
      if (param_1 <= DAT_000b0074) {
        DAT_febec478 = DAT_febec47c * (int)PTR_DAT_000b006c;
        if (DAT_febec480 != 0) {
          DAT_febec478 = DAT_febec478 / (uint)DAT_febec480;
        }
        DAT_febec47c = (DAT_febec478 + 0x100) - uVar1;
        uVar1 = DAT_febec47c * 0x400;
        if (PTR_DAT_000b006c != 0) {
          uVar1 = uVar1 / (uint)PTR_DAT_000b006c;
        }
        uVar1 = uVar1 & 0xffff;
        DAT_febec480 = PTR_DAT_000b006c;
      }
    }
    else {
      DAT_febec478 = DAT_febec47c * (int)PTR_DAT_000b0068;
      if (DAT_febec480 != 0) {
        DAT_febec478 = DAT_febec478 / (uint)DAT_febec480;
      }
      DAT_febec47c = DAT_febec478 - uVar1;
      uVar1 = DAT_febec47c * 0x400;
      if (PTR_DAT_000b0068 != 0) {
        uVar1 = uVar1 / (uint)PTR_DAT_000b0068;
      }
      uVar1 = uVar1 & 0xffff;
      DAT_febec480 = PTR_DAT_000b0068;
    }
    if (DAT_febec49c != 'Z') {
      if (uVar1 < DAT_000b0078) {
        DAT_febeabc0 = (short)uVar1;
        return;
      }
      DAT_febec478 = ((uint)PTR_DAT_000b006c & 0xffffff) >> 2;
      DAT_febeabc0 = 0x100;
      DAT_febec47c = DAT_febec478;
      return;
    }
  }
  DAT_febeabc0 = (ushort)uVar1;
  if (uVar1 <= DAT_000b0076) {
    DAT_febec49c = '\0';
    DAT_febeabc0 = 0;
    DAT_febec47c = 0;
    DAT_febec478 = DAT_febec47c;
  }
  return;
}

undefined2 apply_abc0_envelope_and_abc4_c438_gains_c843a(char param_1)

{
  int iVar1;
  uint32_t puVar2;
  int iVar3;
  undefined2 uVar4;
  char cVar5;
  
  puVar2 = 0xfebeb800u;
  iVar1 = (int)((int)((int)(int16_t)DAT_febeabbe) * (uint)DAT_febeabc0) / 0x100;
  if (iVar1 + -0x7fff < 0 == (iVar1 < 0 && -1 < iVar1 + -0x7fff) && iVar1 != 0x7fff) {
    iVar3 = 0x7fff;
  }
  else {
    iVar3 = (int)(short)iVar1;
    if (iVar1 + 0x7fff < 0 != (-1 < iVar1 && iVar1 + 0x7fff < 0)) {
      iVar3 = -0x7fff;
    }
  }
  DAT_febec488 = (undefined2)iVar3;
  if (param_1 == '\0') {
    cVar5 = 'Z';
  }
  else {
    if (DAT_febec49c == '\0') {
      cVar5 = '\0';
      goto LAB_000c8496;
    }
    cVar5 = DAT_febec49d;
    if (DAT_febec49d != 'Z') goto LAB_000c8496;
  }
  iVar3 = 0;
LAB_000c8496:
  DAT_febec48a = (undefined2)iVar3;
  uVar4 = scale_signed_sample_by_c438_store_and_return_c43a_c7e1c((int)(short)((int)(iVar3 * (uint)DAT_febeabc4) / 0x400));
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar2 + -0xc3e)))) = uVar4;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(0xc9d))))) = cVar5;
  return uVar4;
}

void bound_abc2_by_b0072_into_c4a0_c84bc(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  
  iVar3 = (int)((int)(int16_t)DAT_febeabc2);
  iVar2 = (int)DAT_000b0072;
  DAT_febec4a0 = DAT_000b0072;
  if ((iVar3 - iVar2 < 0 != (iVar3 < 0 != iVar2 < 0 && iVar2 < 0 == iVar3 - iVar2 < 0) ||
       iVar3 == iVar2) &&
     (iVar1 = -iVar2, DAT_febec4a0 = ((int)(int16_t)DAT_febeabc2),
     iVar3 + iVar2 < 0 != (iVar3 < 0 != iVar1 < 0 && iVar1 < 0 == iVar3 + iVar2 < 0) ||
     iVar3 == iVar1)) {
    DAT_febec4a0 = (short)iVar1;
  }
  return;
}

void update_abc0_envelope_scaled_output_and_bound_c84dc(undefined2 param_1,undefined1 param_2)

{
  step_unsigned_abc0_enable_envelope_with_latch_c8350(param_1, (uint)(byte)param_2);
  apply_abc0_envelope_and_abc4_c438_gains_c843a(param_2);
  bound_abc2_by_b0072_into_c4a0_c84bc();
  return;
}

void snapshot_c084_and_run_abb8_curve_curve_filter_c84f8(void)

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
  sVar3 = abs_s16_wrapping((short)iVar5);
  lookup_signed_magnitude_scale_by_ae4a_and_filter_abbe_c82c2(sVar3,iVar5);
  update_abc0_envelope_scaled_output_and_bound_c84dc(sVar3,uVar1);
  return;
}

void debounce_c5ec_status_and_filter_unsigned_abc4_gain_c854a(void)

{
  ushort uVar1;
  ushort uVar2;
  ushort uVar3;
  char cVar4;
  int iVar5;
  uint32_t puVar6;
  short sVar7;
  char cVar8;
  int iVar9;
  int iVar10;
  uint uVar11;
  uint uVar12;
  ushort *puVar13;
  
  cVar4 = DAT_febec5f4;
  uVar3 = DAT_febeadf6;
  uVar2 = DAT_000b0080;
  uVar1 = DAT_000b007a;
  puVar6 = 0xfebeb800u;
  iVar10 = (int)DAT_000b007c;
  iVar9 = (int)DAT_000b007e;
  sVar7 = abs_s16_wrapping(((int)(int16_t)DAT_febec5ec));
  iVar5 = (int)sVar7;
  cVar8 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(0xc9e)))));
  if (cVar8 == '\0') {
    if (((cVar4 != '\x01') ||
        (iVar5 - iVar10 < 0 != (iVar5 < 0 != iVar10 < 0 && iVar10 < 0 == iVar5 - iVar10 < 0) ||
         iVar5 == iVar10)) || (uVar3 <= uVar1)) goto LAB_000c85d2;
    cVar8 = 'Z';
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(0xc9e))))) = 0x5a;
  }
  else if (((cVar4 == '\0') ||
           (iVar5 - iVar9 < 0 != (iVar5 < 0 != iVar9 < 0 && iVar9 < 0 == iVar5 - iVar9 < 0) ||
            iVar5 == iVar9)) || (uVar3 <= uVar1)) {
    uVar1 = (*((ushort *)camry_host_ptr((uint32_t)(puVar6 + 0xc96))));
    if ((uVar2 < uVar1) || ((*((ushort *)camry_host_ptr((uint32_t)(puVar6 + 0xc96)))) = uVar1 + 1, uVar2 < (ushort)(uVar1 + 1))) {
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(0xc9e))))) = 0;
      cVar8 = '\0';
    }
    goto LAB_000c85d2;
  }
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar6 + 0xc96)))) = 0;
LAB_000c85d2:
  if (cVar8 == 'Z') {
    puVar13 = ((undefined *)camry_host_ptr(0xb0082u));
    iVar5 = 0;
  }
  else {
    puVar13 = ((undefined *)camry_host_ptr(0xb0084u));
    iVar5 = 0x400;
  }
  uVar1 = *puVar13;
  uVar12 = (*((int *)camry_host_ptr((uint32_t)(puVar6 + 0xc84)))) * (uint)*puVar13;
  (*((ushort *)camry_host_ptr((uint32_t)(puVar6 + 0xc98)))) = uVar1;
  uVar2 = *puVar13;
  (*((short *)camry_host_ptr((uint32_t)(puVar6 + -0xc3a)))) = (short)iVar5;
  if ((*((ushort *)camry_host_ptr((uint32_t)(puVar6 + 0xc9a)))) != 0) {
    uVar12 = uVar12 / (*((ushort *)camry_host_ptr((uint32_t)(puVar6 + 0xc9a))));
  }
  (*((ushort *)camry_host_ptr((uint32_t)(puVar6 + 0xc9a)))) = uVar2;
  uVar12 = (uVar12 + iVar5) - (uint)(*((ushort *)camry_host_ptr((uint32_t)(puVar6 + -0xc3c))));
  uVar11 = uVar12 * 0x400;
  if (uVar1 != 0) {
    uVar11 = uVar11 / uVar1;
  }
  uVar11 = uVar11 & 0xffff;
  iVar5 = abs_s32_wrapping(uVar11 - iVar5);
  if (iVar5 + -0x14 < 0 != (iVar5 < 0 && -1 < iVar5 + -0x14) || iVar5 == 0x14) {
    uVar11 = (uint)(*((ushort *)camry_host_ptr((uint32_t)(puVar6 + -0xc3a))));
    uVar12 = uVar11 * (*((ushort *)camry_host_ptr((uint32_t)(puVar6 + 0xc98)))) >> 10;
  }
  (*((uint *)camry_host_ptr((uint32_t)(puVar6 + 0xc84)))) = uVar12;
  (*((short *)camry_host_ptr((uint32_t)(puVar6 + -0xc3c)))) = (short)uVar11;
  return;
}

void reset_c4a4_state_and_select_two_fixed_tables_c8642(void)

{
  DAT_febec4ac = ((uint32_t)(0xb1248u));
  DAT_febec4b4 = 0;
  DAT_febec4b6 = 0;
  DAT_febec4c0 = 0;
  DAT_febec4a4 = 0;
  DAT_febec4a8 = 0;
  DAT_febec4b8 = 0;
  DAT_febec4ba = 0;
  DAT_febec4bc = 0;
  DAT_febec4b0 = ((uint32_t)(0xb121cu));
  return;
}

void update_torque_rate_assist_compensation(void)

{
  uint uVar1;
  uint32_t puVar2;
  short sVar3;
  int iVar4;
  int iVar5;
  short sVar6;
  int iVar7;
  short *points;
  short *points_00;
  
  sVar6 = ((int)(int16_t)DAT_febec266);
  puVar2 = 0xfebeb800u;
  uVar1 = (uint)DAT_febec156;
  iVar7 = (int)((int)(int16_t)DAT_febec1aa);
  iVar4 = (int)((int)(int16_t)DAT_febec1a8) + (uVar1 & 3) * 2;
  points_00 = ((short *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd3670u + (uint32_t)(iVar4) * 4u))))));
  points = ((short *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd3674u + (uint32_t)(iVar4) * 4u))))));
  DAT_febec4ac = camry_host_addr(points_00);
  DAT_febec4b0 = camry_host_addr(points);
  sVar3 = abs_s16_wrapping(((int)(int16_t)DAT_febec266));
  iVar4 = interpolate_signed_sentinel_curve(((short *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd3630u + (uint32_t)(uVar1 & 3) * 4u)))))),sVar3);
  sVar3 = (short)iVar4;
  if (sVar6 < 0) {
    sVar3 = -sVar3;
  }
  sVar6 = (*((short *)camry_host_ptr((uint32_t)(puVar2 + 0x740))));
  (*((short *)camry_host_ptr((uint32_t)(puVar2 + 0xcb4)))) = sVar3;
  (*((short *)camry_host_ptr((uint32_t)(puVar2 + 0xcbc)))) = sVar6;
  iVar4 = interpolate_signed_sentinel_curve(points_00,sVar6);
  iVar5 = interpolate_signed_sentinel_curve(points,sVar6);
  (*((short *)camry_host_ptr((uint32_t)(puVar2 + 0xcb8)))) = (short)iVar4;
  (*((short *)camry_host_ptr((uint32_t)(puVar2 + 0xcba)))) = (short)iVar5;
  sVar6 = (short)(((iVar5 - iVar4) * iVar7) / 0x400) + (short)iVar4;
  (*((short *)camry_host_ptr((uint32_t)(puVar2 + 0xcb6)))) = sVar6;
  iVar4 = (int)(((int)sVar6 * (int)(*((short *)camry_host_ptr((uint32_t)(puVar2 + 0xcb4)))))) / (int)0x400;
  (*((int *)camry_host_ptr((uint32_t)(puVar2 + 0xca8)))) = iVar4;
  iVar5 = DAT_000b1204;
  iVar4 = (iVar4 << 10) / 0x400;
  (*((int *)camry_host_ptr((uint32_t)(puVar2 + 0xca4)))) = iVar4;
  iVar7 = iVar5;
  if ((iVar4 - iVar5 < 0 != (iVar4 < 0 != iVar5 < 0 && iVar5 < 0 == iVar4 - iVar5 < 0) ||
       iVar4 == iVar5) &&
     (iVar7 = -iVar5,
     iVar4 + iVar5 < 0 == (iVar4 < 0 != iVar7 < 0 && iVar7 < 0 == iVar4 + iVar5 < 0) &&
     iVar4 != iVar7)) {
    iVar7 = iVar4;
  }
  (*((int *)camry_host_ptr((uint32_t)(puVar2 + 0xcc0)))) = iVar7;
  return;
}

void reset_c4c4_envelope_and_unity_gain_state_c873e(void)

{
  DAT_febec4e0 = 0;
  DAT_febec4c8 = 0;
  DAT_febec4ce = DAT_000b12ba;
  DAT_febec4ca = 0x400;
  DAT_febec4cc = 0x400;
  DAT_febec4d0 = DAT_000b12ba;
  DAT_febec4c4 = (uint)DAT_000b12ba;
  DAT_febec4d2 = 0;
  DAT_febec4d4 = 0x400;
  DAT_febec4d6 = 0x400;
  DAT_febec4d8 = 0x400;
  DAT_febec4da = 0x400;
  DAT_febec4dc = 0x400;
  DAT_febec4de = 0;
  return;
}

void debounce_c5ec_status_and_filter_unsigned_c4ca_gain_c878a(void)

{
  char cVar1;
  ushort uVar2;
  uint uVar3;
  int iVar4;
  uint32_t puVar5;
  short sVar6;
  int iVar7;
  int iVar8;
  char cVar9;
  uint uVar10;
  ushort *puVar11;
  
  cVar1 = DAT_febec5f4;
  uVar2 = DAT_febeadf6;
  puVar5 = 0xfebeb800u;
  sVar6 = abs_s16_wrapping(((int)(int16_t)DAT_febec5ec));
  iVar4 = (int)sVar6;
  cVar9 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(0xce0)))));
  iVar8 = (int)DAT_000b12b2;
  iVar7 = (int)DAT_000b12b4;
  uVar10 = (*((uint *)camry_host_ptr((uint32_t)(puVar5 + 0xcc4))));
  if (cVar9 == '\0') {
    if (((cVar1 != '\x01') ||
        (iVar4 - iVar8 < 0 != (iVar4 < 0 != iVar8 < 0 && iVar8 < 0 == iVar4 - iVar8 < 0) ||
         iVar4 == iVar8)) || (uVar2 <= DAT_000b12b0)) goto LAB_000c8812;
    cVar9 = 'Z';
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(0xce0))))) = 0x5a;
  }
  else if (((cVar1 == '\0') ||
           (iVar4 - iVar7 < 0 != (iVar4 < 0 != iVar7 < 0 && iVar7 < 0 == iVar4 - iVar7 < 0) ||
            iVar4 == iVar7)) || (uVar2 <= DAT_000b12b0)) {
    uVar2 = (*((ushort *)camry_host_ptr((uint32_t)(puVar5 + 0xcc8))));
    if (uVar2 <= DAT_000b12b6) {
      sVar6 = uVar2 + 1;
      uVar2 = uVar2 + 1;
      (*((short *)camry_host_ptr((uint32_t)(puVar5 + 0xcc8)))) = sVar6;
    }
    if (DAT_000b12b6 < uVar2) {
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(0xce0))))) = 0;
      cVar9 = '\0';
    }
    goto LAB_000c8812;
  }
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar5 + 0xcc8)))) = 0;
LAB_000c8812:
  uVar3 = (uint)(*((ushort *)camry_host_ptr((uint32_t)(puVar5 + 0xcd0))));
  if (cVar9 == 'Z') {
    puVar11 = ((undefined *)camry_host_ptr(0xb12b8u));
    if ((uVar3 != 0) && (uVar10 = uVar10 * DAT_000b12b8, uVar3 != 0)) {
      uVar10 = uVar10 / uVar3;
    }
    iVar4 = 0;
  }
  else {
    puVar11 = ((undefined *)camry_host_ptr(0xb12bau));
    if ((uVar3 != 0) && (uVar10 = uVar10 * DAT_000b12ba, uVar3 != 0)) {
      uVar10 = uVar10 / uVar3;
    }
    iVar4 = 0x400;
  }
  uVar2 = *puVar11;
  uVar10 = (uVar10 + iVar4) - (uint)(*((ushort *)camry_host_ptr((uint32_t)(puVar5 + 0xcca))));
  uVar3 = uVar10 * 0x400;
  if (uVar2 != 0) {
    uVar3 = uVar3 / uVar2;
  }
  (*((ushort *)camry_host_ptr((uint32_t)(puVar5 + 0xcce)))) = uVar2;
  uVar2 = *puVar11;
  (*((short *)camry_host_ptr((uint32_t)(puVar5 + 0xccc)))) = (short)iVar4;
  uVar3 = uVar3 & 0xffff;
  (*((ushort *)camry_host_ptr((uint32_t)(puVar5 + 0xcd0)))) = uVar2;
  iVar4 = abs_s32_wrapping(uVar3 - iVar4);
  if (iVar4 + -0x14 < 0 != (iVar4 < 0 && -1 < iVar4 + -0x14) || iVar4 == 0x14) {
    uVar3 = (uint)(*((ushort *)camry_host_ptr((uint32_t)(puVar5 + 0xccc))));
    uVar10 = uVar3 * (*((ushort *)camry_host_ptr((uint32_t)(puVar5 + 0xcce)))) >> 10;
  }
  (*((uint *)camry_host_ptr((uint32_t)(puVar5 + 0xcc4)))) = uVar10;
  (*((short *)camry_host_ptr((uint32_t)(puVar5 + 0xcca)))) = (short)uVar3;
  return;
}

uint scale_signed_sample_by_c4ca_store_and_return_c4d2_c8894(short param_1)

{
  DAT_febec4d2 = (short)((int)((int)param_1 * (uint)DAT_febec4ca) / 0x400);
  return DAT_febec4d2;
}

void prepare_gain_parameters_c4dc(F33GainSlewState *state,uint mode)

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
    uVar2 = *(ushort *)(((undefined *)camry_host_ptr((uint32_t)(0xd36f8u + (uint32_t)(iVar1 * 0x10) * 1u))));
    uVar6 = (*((ushort *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd36f4u + (uint32_t)(iVar1 * 4) * 4u)))))));
    uVar5 = (*((volatile ushort *)camry_host_ptr((*((volatile uint32_t *)(((undefined *)camry_host_ptr((uint32_t)(0xd36fcu + (uint32_t)(iVar1 * 0x10) * 1u)))))))));
    uVar4 = (*((ushort *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd36f0u + (uint32_t)(iVar1 * 4) * 4u)))))));
  }
  else {
    uVar3 = '\x01';
    uVar2 = DAT_febec4d4;
    uVar6 = DAT_febec4d8;
    uVar5 = DAT_febec4da;
    uVar4 = DAT_febec4d6;
  }
  state->down_step = uVar6;
  state->up_step = uVar5;
  state->down_target = uVar4;
  state->up_target = uVar2;
  state->direction = uVar3;
  return;
}

void prepare_and_step_unsigned_gain_c4dc_c890e(void)

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
  local_10.current = DAT_febec4dc;
  if (uVar3 < 7) {
    local_10.direction = '\x02';
    iVar1 = (short)(DAT_febeac3c & 1) * 7 + uVar3;
    local_10.up_target = *(ushort *)(((undefined *)camry_host_ptr((uint32_t)(0xd36f8u + (uint32_t)(iVar1 * 0x10) * 1u))));
    local_10.down_step = (*((ushort *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd36f4u + (uint32_t)(iVar1 * 4) * 4u)))))));
    local_10.up_step = (*((volatile ushort *)camry_host_ptr((*((volatile uint32_t *)(((undefined *)camry_host_ptr((uint32_t)(0xd36fcu + (uint32_t)(iVar1 * 0x10) * 1u)))))))));
    local_10.down_target = (*((ushort *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd36f0u + (uint32_t)(iVar1 * 4) * 4u)))))));
  }
  else {
    local_10.direction = '\x01';
    local_10.up_target = DAT_febec4d4;
    local_10.down_step = DAT_febec4d8;
    local_10.up_step = DAT_febec4da;
    local_10.down_target = DAT_febec4d6;
  }
  step_retained_unsigned_gain(&local_10);
  (*((ushort *)camry_host_ptr((uint32_t)(puVar2 + 0xcd8)))) = local_10.down_step;
  (*((ushort *)camry_host_ptr((uint32_t)(puVar2 + 0xcda)))) = local_10.up_step;
  (*((ushort *)camry_host_ptr((uint32_t)(puVar2 + 0xcd6)))) = local_10.down_target;
  (*((ushort *)camry_host_ptr((uint32_t)(puVar2 + 0xcd4)))) = local_10.up_target;
  (*((ushort *)camry_host_ptr((uint32_t)(puVar2 + 0xcdc)))) = local_10.current;
  return;
}

uint scale_signed_sample_by_c4dc_store_and_return_c4de_c8956(short param_1)

{
  DAT_febec4de = (short)((int)((uint)DAT_febec4dc * (int)param_1) / 0x400);
  return DAT_febec4de;
}

void fill_constant_block_c8970(void)

{
  DAT_febec4e4 = 0;
  DAT_febec520 = 0;
  DAT_febec508 = 0;
  DAT_febeabce = 0;
  DAT_febec50a = 0;
  DAT_febec50c = 0;
  DAT_febec4e8 = 0;
  DAT_febec4ec = 0;
  DAT_febec50e = 0;
  DAT_febec510 = 0;
  DAT_febec512 = 0;
  DAT_febec514 = 0;
  DAT_febec524 = 0;
  DAT_febec4f0 = 0;
  DAT_febeabc8 = 0;
  DAT_febec4f4 = 0;
  DAT_febec4f8 = 0;
  DAT_febec521 = 0;
  DAT_febec522 = 0x5a;
  DAT_febec516 = 0;
  DAT_febec4fc = 0;
  DAT_febec518 = 0;
  DAT_febec500 = 0;
  DAT_febec51a = 0;
  DAT_febec51c = 0;
  DAT_febec51e = 0;
  DAT_febeabcc = 0;
  DAT_febec504 = 0;
  return;
}

void blend_signed_c0cc_curve_pair_into_abcc_c89e6(void)

{
  int value;
  uint uVar1;
  uchar *puVar2;
  uint32_t puVar3;
  short sVar4;
  uint uVar5;
  int iVar6;
  int iVar7;
  int iVar8;
  ushort input;
  
  value = DAT_febec0cc;
  puVar3 = 0xfebeb800u;
  uVar1 = (uint)DAT_febec156;
  input = 0xffff;
  iVar8 = (int)((int)(int16_t)DAT_febec1ac);
  iVar7 = (int)((int)(int16_t)DAT_febec1ae);
  uVar5 = abs_s32_wrapping(DAT_febec0cc);
  if (uVar5 < 0x10000) {
    iVar6 = abs_s32_wrapping(value);
    input = (ushort)iVar6;
  }
  puVar2 = ((void *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xb144cu + (uint32_t)((byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0xbc4))))) & 1) * 4u)))))));
  iVar6 = interpolate_unsigned_axis_sentinel_curve
                    ((ushort *)(puVar2 + (iVar8 + (uVar1 & 3) * 8) * 0x24 + 0x1bbc),input);
  (*((short *)camry_host_ptr((uint32_t)(puVar3 + 0xd1c)))) = (short)iVar6;
  iVar8 = interpolate_unsigned_axis_sentinel_curve
                    (((ushort *)camry_host_ptr((uint32_t)((int)camry_host_addr((puVar2 + (iVar8 + (uVar1 & 3) * 8) * 0x24 + 0x1bbc)) + 0x24))),
                     input);
  (*((short *)camry_host_ptr((uint32_t)(puVar3 + 0xd1e)))) = (short)iVar8;
  sVar4 = (short)( (int)(((iVar8 - (*((short *)camry_host_ptr((uint32_t)(puVar3 + 0xd1c))))) * iVar7)) / (int)0x400) +
          (*((short *)camry_host_ptr((uint32_t)(puVar3 + 0xd1c))));
  if (value < 0) {
    sVar4 = -sVar4;
  }
  (*((short *)camry_host_ptr((uint32_t)(puVar3 + -0xc34)))) = sVar4;
  return;
}

void interpolate_banked_1a4c_curve_into_c508_c8a78(void)

{
  uint32_t puVar1;
  int iVar2;
  
  puVar1 = 0xfebeb800u;
  iVar2 = interpolate_unsigned_axis_sentinel_curve
                    (((ushort *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xb144cu + (uint32_t)(DAT_febeac3c & 1) * 4u)))) +
                     (DAT_febec156 & 3) * 0x24 + 0x1a4c))),DAT_febeadf6);
  (*((short *)camry_host_ptr((uint32_t)(puVar1 + 0xd08)))) = (short)iVar2;
  return;
}

void interpolate_abs_c29a_curve_into_abce_c8ab2(void)

{
  uint32_t puVar1;
  short input;
  int iVar2;
  
  puVar1 = 0xfebeb800u;
  input = abs_s16_wrapping(((int)(int16_t)DAT_febec29a));
  iVar2 = interpolate_signed_sentinel_curve
                    (((short *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xb144cu + (uint32_t)((byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0xbc4))))) & 1) * 4u)))) +
                              ((*((volatile ushort *)camry_host_ptr((uint32_t)(0xfebeb800u + (uint32_t)(0x956) * 1u)))) & 3) * 0x14 + 0x1b6c))),input);
  (*((short *)camry_host_ptr((uint32_t)(puVar1 + -0xc32)))) = (short)iVar2;
  return;
}

undefined4 filter_signed_abcc_minus_c1a2_curve_and_snapshot_c8af2(void)

{
  uint uVar1;
  uint32_t puVar2;
  ushort input;
  uint uVar3;
  int iVar4;
  undefined4 uVar5;
  short sVar6;
  short sVar7;
  
  puVar2 = 0xfebeb800u;
  uVar1 = (uint)DAT_febec156;
  DAT_febec504 = (int)((int)(int16_t)DAT_febeabcc) - (int)((int)(int16_t)DAT_febec1a2);
  uVar3 = abs_s32_wrapping(DAT_febec504);
  input = (ushort)uVar3;
  if (0xffff < uVar3) {
    input = 0xffff;
  }
  iVar4 = interpolate_unsigned_axis_sentinel_curve
                    (((ushort *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xb144cu + (uint32_t)((byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0xbc4))))) & 1) * 4u)))) +
                     (uVar1 & 3) * 0x24 + 0x1adc))),input);
  sVar7 = (short)iVar4;
  if ((*((int *)camry_host_ptr((uint32_t)(puVar2 + 0xd04)))) < 0) {
    sVar7 = -sVar7;
  }
  sVar6 = (short)( (int)(((int)(*((short *)camry_host_ptr((uint32_t)(puVar2 + 0xd08)))) * (int)sVar7)) / (int)0x400);
  (*((short *)camry_host_ptr((uint32_t)(puVar2 + 0xd0c)))) = sVar6;
  iVar4 = ((int)sVar6 - (*((int *)camry_host_ptr((uint32_t)(puVar2 + 0xcf8))))) * (uint)DAT_000b12c4 + (*((int *)camry_host_ptr((uint32_t)(puVar2 + 0xcf4))));
  (*((int *)camry_host_ptr((uint32_t)(puVar2 + 0xcf0)))) = iVar4;
  (*((int *)camry_host_ptr((uint32_t)(puVar2 + 0xcf4)))) = iVar4;
  (*((int *)camry_host_ptr((uint32_t)(puVar2 + -0xc38)))) = iVar4 / 0x4000;
  (*((int *)camry_host_ptr((uint32_t)(puVar2 + 0xcf8)))) = iVar4 / 0x4000;
  uVar5 = raise_priority_mask_and_return_previous_d1da0(0xffc0);
  (*((short *)camry_host_ptr((uint32_t)(puVar2 + 0xd0a)))) = sVar7;
  (*((undefined4 *)camry_host_ptr((uint32_t)(puVar2 + 0xce4)))) = (*((undefined4 *)camry_host_ptr((uint32_t)(puVar2 + 0x8cc))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(0xd20))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(0x8d0)))));
  (*((undefined4 *)camry_host_ptr((uint32_t)(puVar2 + 0xce8)))) = (*((undefined4 *)camry_host_ptr((uint32_t)(puVar2 + -0xc38))));
  restore_priority_mask_preserving_interrupt_enable_d1dc6(uVar5);
  return uVar5;
}

void scale_c4e8_by_abce_with_sign_bypass_and_bound_c8bc6(void)

{
  uint32_t puVar1;
  int iVar2;
  short input;
  int iVar3;
  int iVar4;
  
  puVar1 = 0xfebeb800u;
  iVar2 = (int)(int16_t)DAT_febeac44;
  iVar4 = (int)(short)DAT_000b12d2;
  iVar3 = (int)DAT_febec4e8;
  if (DAT_000b12d4 == '\x01' && ((iVar2 > iVar4 && iVar3 > 0) || (iVar2 < iVar4 && iVar3 < 0))) {
    iVar2 = iVar3;
  }
  else {
    iVar2 = (iVar3 * (int)(int16_t)DAT_febeabce) / 0x400;
  }
  DAT_febec4ec = (uint)iVar2;
  iVar3 = (int)(short)DAT_000b12c2;
  if (iVar2 > iVar3) {
    DAT_febec510 = (short)iVar3;
  }
  else if (iVar2 <= -iVar3) {
    DAT_febec510 = (short)(-iVar3);
  }
  else {
    DAT_febec510 = (short)iVar2;
  }
  input = abs_s16_wrapping(((int)(int16_t)DAT_febeac44));
  iVar2 = interpolate_signed_sentinel_curve((short *)((undefined *)camry_host_ptr(0xb12d6u)),input);
  (*((short *)camry_host_ptr((uint32_t)(puVar1 + 0xd1a)))) = (short)iVar2;
  (*((short *)camry_host_ptr((uint32_t)(puVar1 + 0xd0e)))) =
       (short)( (int)(((int)(short)iVar2 * (int)(*((short *)camry_host_ptr((uint32_t)(puVar1 + 0xd10)))))) / (int)0x400);
  return;
}

int return_c512_unless_enable_zero_latch_active_c8c58(void)

{
  if (DAT_febec520 == '\0') {
    DAT_febec522 = 'Z';
  }
  else {
    if (DAT_febec521 == '\0') {
      DAT_febec522 = 0;
      return (int)((int)(int16_t)DAT_febec512);
    }
    if (DAT_febec522 != 'Z') {
      return (int)((int)(int16_t)DAT_febec512);
    }
  }
  return 0;
}

void step_c516_envelope_apply_two_gains_and_bound_c524_c8c88(void)

{
  int iVar1;
  uint32_t puVar2;
  short sVar3;
  int iVar5;
  undefined2 uVar6;
  int iVar7;
  undefined4 uVar8;
  int iVar9;
  int iVar10;
  char cVar11;
  int iVar4;
  
  cVar11 = DAT_febec521;
  iVar7 = DAT_febec4e4;
  iVar1 = DAT_000b12bc;
  puVar2 = 0xfebeb800u;
  iVar10 = (int)DAT_000b12c6;
  iVar9 = (int)DAT_000b12c8;
  if (((DAT_febec520 == '\0') || (DAT_febeac30 != '\x11')) || (DAT_febeac2e == 'Z')) {
    cVar11 = '\x01';
LAB_000c8d10:
    iVar1 = -(int)((int)(int16_t)DAT_febec518);
    sVar3 = DAT_000b12cc;
LAB_000c8d18:
    iVar1 = iVar1 * sVar3 + (*((int *)camry_host_ptr((uint32_t)(puVar2 + 0xd00))));
    (*((int *)camry_host_ptr((uint32_t)(puVar2 + 0xcfc)))) = iVar1;
    (*((short *)camry_host_ptr((uint32_t)(puVar2 + 0xd16)))) = (short)(iVar1 / 0x4000);
  }
  else {
    if (DAT_febec521 != '\0') goto LAB_000c8d10;
    puVar2 = 0xfebeb800u;
    sVar3 = abs_s16_wrapping(((int)(int16_t)DAT_febec50e));
    iVar4 = (int)sVar3;
    iVar7 = abs_s32_wrapping(iVar7);
    sVar3 = abs_s16_wrapping((*((short *)camry_host_ptr((uint32_t)(puVar2 + 0xd0a)))));
    iVar5 = (int)sVar3;
    if (((iVar4 - iVar10 < 0 != (iVar4 < 0 != iVar10 < 0 && iVar10 < 0 == iVar4 - iVar10 < 0) ||
          iVar4 == iVar10) &&
        (iVar7 - iVar1 < 0 != (iVar7 < 0 != iVar1 < 0 && iVar1 < 0 == iVar7 - iVar1 < 0) ||
         iVar7 == iVar1)) &&
       (iVar5 - iVar9 < 0 != (iVar5 < 0 != iVar9 < 0 && iVar9 < 0 == iVar5 - iVar9 < 0) ||
        iVar5 == iVar9)) {
      iVar1 = 0x400 - (*((short *)camry_host_ptr((uint32_t)(puVar2 + 0xd18))));
      sVar3 = DAT_000b12ca;
      goto LAB_000c8d18;
    }
  }
  sVar3 = (*((short *)camry_host_ptr((uint32_t)(puVar2 + 0xd16))));
  iVar1 = (int)sVar3;
  if (cVar11 == '\x01') {
    iVar7 = (int)DAT_000b12d0;
    if (iVar1 - iVar7 < 0 == (iVar1 < 0 != iVar7 < 0 && iVar7 < 0 == iVar1 - iVar7 < 0) &&
        iVar1 != iVar7) goto LAB_000c8d6e;
    cVar11 = '\0';
    sVar3 = 0;
    (*((undefined2 *)camry_host_ptr((uint32_t)(puVar2 + 0xd16)))) = 0;
    uVar8 = 0;
  }
  else {
    iVar7 = (int)DAT_000b12ce;
    if (iVar1 - iVar7 < 0 != (iVar1 < 0 != iVar7 < 0 && iVar7 < 0 == iVar1 - iVar7 < 0))
    goto LAB_000c8d6e;
    sVar3 = 0x400;
    uVar8 = 0x1000000;
    (*((undefined2 *)camry_host_ptr((uint32_t)(puVar2 + 0xd16)))) = 0x400;
  }
  (*((undefined4 *)camry_host_ptr((uint32_t)(puVar2 + 0xcfc)))) = uVar8;
LAB_000c8d6e:
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(0xd21))))) = cVar11;
  uVar6 = 0;
  if (DAT_000b1370 != '\x01') {
    uVar6 = (undefined2)( (int)(((int)sVar3 * (int)(*((short *)camry_host_ptr((uint32_t)(puVar2 + 0xd0e)))))) / (int)0x400);
  }
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar2 + 0xd12)))) = uVar6;
  uVar8 = return_c512_unless_enable_zero_latch_active_c8c58();
  (*((short *)camry_host_ptr((uint32_t)(puVar2 + 0xd14)))) = (short)uVar8;
  uVar8 = scale_signed_sample_by_c4ca_store_and_return_c4d2_c8894(uVar8);
  iVar7 = scale_signed_sample_by_c4dc_store_and_return_c4de_c8956(uVar8);
  iVar1 = (int)DAT_000b12c0;
  sVar3 = DAT_000b12c0;
  if (iVar7 - iVar1 < 0 != (iVar7 < 0 != iVar1 < 0 && iVar1 < 0 == iVar7 - iVar1 < 0) ||
      iVar7 == iVar1) {
    iVar9 = -iVar1;
    if (iVar7 + iVar1 < 0 == (iVar7 < 0 != iVar9 < 0 && iVar9 < 0 == iVar7 + iVar1 < 0) &&
        iVar7 != iVar9) {
      sVar3 = (short)iVar7;
    }
    else {
      sVar3 = (short)iVar9;
    }
  }
  (*((short *)camry_host_ptr((uint32_t)(puVar2 + 0xd24)))) = sVar3;
  (*((undefined4 *)camry_host_ptr((uint32_t)(puVar2 + 0xd00)))) = (*((undefined4 *)camry_host_ptr((uint32_t)(puVar2 + 0xcfc))));
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar2 + 0xd18)))) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar2 + 0xd16))));
  return;
}

void update_abce_scaling_and_c516_enveloped_output_c8dd2(void)

{
  interpolate_abs_c29a_curve_into_abce_c8ab2();
  scale_c4e8_by_abce_with_sign_bypass_and_bound_c8bc6();
  step_c516_envelope_apply_two_gains_and_bound_c524_c8c88();
  return;
}

undefined4 update_abcc_curve_and_filtered_difference_c8de6(void)

{
  blend_signed_c0cc_curve_pair_into_abcc_c89e6();
  return filter_signed_abcc_minus_c1a2_curve_and_snapshot_c8af2();
}

void fill_constant_block_c8df6(void)

{
  DAT_febec536 = 0;
  DAT_febec537 = 0;
  DAT_febec538 = 0;
  DAT_febec528 = 0;
  DAT_febec530 = 0;
  DAT_febec532 = 0;
  DAT_febec53a = 0;
  DAT_febec534 = 0;
  DAT_febec52c = 0;
  return;
}

void debounce_opposed_adf2_c18a_sign_thresholds_c8e1c(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  
  iVar3 = (int)((int)(int16_t)DAT_febeadf2);
  iVar2 = (int)DAT_000b0160;
  iVar1 = (int)DAT_000b0162;
  iVar4 = (int)((int)(int16_t)DAT_febec18a);
  if ((iVar3 - iVar2 < 0 == (iVar3 < 0 != iVar2 < 0 && iVar2 < 0 == iVar3 - iVar2 < 0) &&
       iVar3 != iVar2) &&
     (iVar4 + iVar1 < 0 != (iVar4 < 0 != -iVar1 < 0 && -iVar1 < 0 == iVar4 + iVar1 < 0))) {
    iVar2 = (int)((int)(int8_t)DAT_febec538);
    iVar1 = (int)DAT_000b0168;
    if (iVar2 - iVar1 < 0 != (iVar2 < 0 != iVar1 < 0 && iVar1 < 0 == iVar2 - iVar1 < 0) ||
        iVar2 == iVar1) {
      iVar1 = (int)DAT_000b0168;
      DAT_febec538 = ((int)(int8_t)DAT_febec538) + '\x01';
      iVar2 = (int)((int)(int8_t)DAT_febec538);
      if (iVar2 - iVar1 < 0 == (iVar2 < 0 != iVar1 < 0 && iVar1 < 0 == iVar2 - iVar1 < 0) &&
          iVar2 != iVar1) {
        DAT_febec536 = '\x01';
      }
    }
  }
  else {
    if ((iVar3 + iVar2 < 0 != (iVar3 < 0 != -iVar2 < 0 && -iVar2 < 0 == iVar3 + iVar2 < 0)) &&
       (iVar4 - iVar1 < 0 == (iVar4 < 0 != iVar1 < 0 && iVar1 < 0 == iVar4 - iVar1 < 0) &&
        iVar4 != iVar1)) {
      iVar2 = (int)((int)(int8_t)DAT_febec537);
      iVar1 = (int)DAT_000b0168;
      if (iVar2 - iVar1 < 0 != (iVar2 < 0 != iVar1 < 0 && iVar1 < 0 == iVar2 - iVar1 < 0) ||
          iVar2 == iVar1) {
        iVar1 = (int)DAT_000b0168;
        DAT_febec537 = ((int)(int8_t)DAT_febec537) + '\x01';
        iVar2 = (int)((int)(int8_t)DAT_febec537);
        if (iVar2 - iVar1 < 0 == (iVar2 < 0 != iVar1 < 0 && iVar1 < 0 == iVar2 - iVar1 < 0) &&
            iVar2 != iVar1) {
          DAT_febec536 = '\x02';
        }
      }
      DAT_febec538 = '\0';
      goto LAB_000c8e98;
    }
    DAT_febec538 = '\0';
  }
  DAT_febec537 = '\0';
LAB_000c8e98:
  if (DAT_febec536 == '\x01') {
    iVar1 = (int)DAT_000b0164;
    if (iVar4 - iVar1 < 0 == (iVar4 < 0 != iVar1 < 0 && iVar1 < 0 == iVar4 - iVar1 < 0)) {
      DAT_febec538 = '\0';
      DAT_febec536 = '\0';
    }
  }
  else if (DAT_febec536 == '\x02') {
    iVar2 = -(int)DAT_000b0164;
    iVar1 = iVar4 + DAT_000b0164;
    if (iVar1 < 0 != (iVar4 < 0 != iVar2 < 0 && iVar2 < 0 == iVar1 < 0) || iVar4 == iVar2) {
      DAT_febec537 = '\0';
      DAT_febec536 = '\0';
    }
  }
  else {
    DAT_febec536 = '\0';
  }
  return;
}

uint32_t interpolate_mode_selected_d3810_curve_into_c530_c8ecc(void)

{
  uint32_t camry_r10_result;
  uint32_t puVar1;
  int iVar2;
  
  puVar1 = 0xfebeb800u;
  iVar2 = (camry_r10_result = interpolate_unsigned_axis_sentinel_curve
                    (((ushort *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)((((undefined *)camry_host_ptr((uint32_t)(0xd3810u + (uint32_t)((DAT_febec156 & 3) * 4) * 1u)))))))))),DAT_febeadf6));
  (*((short *)camry_host_ptr((uint32_t)(puVar1 + 0xd30)))) = (short)iVar2;
  return camry_r10_result;
}

void lookup_signed_c18a_curve_gate_scale_and_filter_c534_c8ef4(void)

{
  uint uVar1;
  uint32_t puVar2;
  short input;
  short sVar3;
  int iVar4;
  int iVar6;
  int iVar5;
  
  sVar3 = ((int)(int16_t)DAT_febec18a);
  puVar2 = 0xfebeb800u;
  uVar1 = (uint)DAT_febec156;
  input = abs_s16_wrapping(((int)(int16_t)DAT_febec18a));
  iVar4 = interpolate_signed_sentinel_curve(((short *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd37d0u + (uint32_t)(uVar1 & 3) * 4u)))))),input);
  if (sVar3 < 0) {
    iVar4 = -iVar4;
  }
  (*((int *)camry_host_ptr((uint32_t)(puVar2 + 0xd28)))) = iVar4;
  iVar6 = 0;
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(0xd36))))) != '\0') {
    iVar6 = (int)(short)( (int)((iVar4 * (*((short *)camry_host_ptr((uint32_t)(puVar2 + 0xd30)))) + 0x200)) / (int)0x400);
  }
  (*((short *)camry_host_ptr((uint32_t)(puVar2 + 0xd32)))) = (short)iVar6;
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(0xdf4))))) == '\x01') {
    sVar3 = abs_s16_wrapping((*((short *)camry_host_ptr((uint32_t)(puVar2 + 0xdec)))));
    iVar5 = (int)sVar3;
    iVar4 = (int)DAT_000b0166;
    if (iVar5 - iVar4 < 0 == (iVar5 < 0 != iVar4 < 0 && iVar4 < 0 == iVar5 - iVar4 < 0) &&
        iVar5 != iVar4) {
      iVar6 = 0;
    }
  }
  iVar4 = (*((int *)camry_host_ptr((uint32_t)(puVar2 + 0xd2c)))) + (iVar6 - (*((short *)camry_host_ptr((uint32_t)(puVar2 + 0xd34)))));
  (*((int *)camry_host_ptr((uint32_t)(puVar2 + 0xd2c)))) = iVar4;
  iVar4 = iVar4 * 0x400;
  if (PTR_LAB_000b015c != 0) {
    if (iVar4 == -0x80000000 && PTR_LAB_000b015c == 0xffffffffu) {
      iVar4 = 0;
    }
    else {
      iVar4 = iVar4 / (int)PTR_LAB_000b015c;
    }
  }
  (*((short *)camry_host_ptr((uint32_t)(puVar2 + 0xd34)))) = (short)iVar4;
  return;
}

void bound_c534_by_b1274_into_c53a_c8f90(void)

{
  bool bVar1;
  int iVar2;
  int iVar3;
  
  iVar3 = (int)((int)(int16_t)DAT_febec534);
  iVar2 = (int)DAT_000b1274;
  DAT_febec53a = DAT_000b1274;
  if ((iVar3 - iVar2 < 0 != (iVar3 < 0 != iVar2 < 0 && iVar2 < 0 == iVar3 - iVar2 < 0) ||
       iVar3 == iVar2) &&
     (iVar2 = iVar3 + DAT_000b1274, bVar1 = -(int)DAT_000b1274 < 0, DAT_febec53a = ((int)(int16_t)DAT_febec534),
     iVar2 < 0 != (iVar3 < 0 != bVar1 && bVar1 == iVar2 < 0))) {
    DAT_febec53a = -DAT_000b1274;
  }
  return;
}

void initialize_seven_c54c_gain_slots_to_unity_c8fb6(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  
  DAT_febec546 = 0;
  DAT_febec53c = 0x400;
  DAT_febec53e = 0x400;
  DAT_febec540 = 0x400;
  DAT_febec542 = 0x400;
  DAT_febec544 = 0x400;
  iVar3 = 0;
  do {
    *(undefined2 *)(((undefined *)camry_host_ptr((uint32_t)(0xfebec554u + (uint32_t)(iVar3 * 2) * 1u)))) = 0x400;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebec54cu + (uint32_t)(iVar3) * 1u)))) = 0;
    iVar2 = iVar3 + 1;
    iVar1 = iVar3 + -6;
    iVar3 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  DAT_febec548 = 0x400;
  DAT_febec54a = 0;
  return;
}

void prepare_gain_parameters_c544(F33GainSlewState *state,uint mode)

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
    uVar2 = *(ushort *)(((undefined *)camry_host_ptr((uint32_t)(0xd3858u + (uint32_t)(iVar1 * 0x10) * 1u))));
    uVar6 = (*((ushort *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd3854u + (uint32_t)(iVar1 * 4) * 4u)))))));
    uVar5 = (*((ushort *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd385cu + (uint32_t)(iVar1 * 4) * 4u)))))));
    uVar4 = (*((ushort *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd3850u + (uint32_t)(iVar1 * 4) * 4u)))))));
  }
  else {
    uVar3 = '\x01';
    uVar2 = DAT_febec53c;
    uVar6 = DAT_febec540;
    uVar5 = DAT_febec542;
    uVar4 = DAT_febec53e;
  }
  state->down_step = uVar6;
  state->up_step = uVar5;
  state->down_target = uVar4;
  state->up_target = uVar2;
  state->direction = uVar3;
  return;
}
