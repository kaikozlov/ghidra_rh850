#include "common.h"

void smooth_c722_limit_across_adc2_transitions_cb0fc(void)

{
  bool bVar1;
  char cVar2;
  uint32_t puVar3;
  short sVar4;
  short sVar5;
  char cVar7;
  int iVar8;
  int iVar9;
  short sVar10;
  int iVar11;
  int iVar12;
  int iVar6;
  
  sVar10 = ((int)(int16_t)DAT_febec722);
  cVar7 = DAT_febec702;
  sVar5 = ((int)(int16_t)DAT_febec6ec);
  iVar9 = DAT_febec6d0;
  cVar2 = DAT_febeadc2;
  puVar3 = 0xfebeb800u;
  iVar8 = (int)((int)(int16_t)DAT_febec6ec);
  iVar12 = (int)((int)(int16_t)DAT_febec722);
  iVar11 = (int)((int)(int16_t)DAT_febec6ee);
  bVar1 = DAT_febeadc2 != DAT_febec703;
  if (DAT_febeadc2 == '\x02') {
    puVar3 = 0xfebeb800u;
    sVar4 = abs_s16_wrapping(((int)(int16_t)DAT_febec6ec));
    iVar6 = (int)sVar4;
    iVar12 = (int)(*((short *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xb145cu + (uint32_t)((byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0xbc4))))) & 1) * 4u)))) + 0x18))));
    if (iVar6 - iVar12 < 0 == (iVar6 < 0 != iVar12 < 0 && iVar12 < 0 == iVar6 - iVar12 < 0) &&
        iVar6 != iVar12) {
      if (bVar1) {
        sVar5 = abs_s16_wrapping(sVar10);
        iVar11 = (int)sVar5;
        iVar9 = iVar11 << 10;
        cVar7 = '\x01';
      }
      iVar9 = iVar9 + ((*((short *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xb145cu + (uint32_t)((byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0xbc4))))) & 1) * 4u)))) + 0x18)))) - iVar11) *
                      (uint)(*((ushort *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xb145cu + (uint32_t)((byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0xbc4))))) & 1) * 4u)))) + 0x1a))));
      sVar10 = (short)(iVar9 / 0x400);
      sVar5 = sVar10;
      if (iVar8 < 0) {
        sVar5 = -sVar10;
      }
    }
    else {
      iVar9 = iVar12 << 10;
      cVar7 = '\0';
      sVar10 = (*((short *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xb145cu + (uint32_t)((byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0xbc4))))) & 1) * 4u)))) + 0x18))));
    }
  }
  else {
    sVar4 = (*((short *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xb145cu + (uint32_t)(DAT_febeac3c & 1) * 4u)))) + 0x1c))));
    sVar10 = ((int)(int16_t)DAT_febec6ee);
    if (DAT_febec702 == '\x01') {
      if ((iVar12 < 1) ||
         (iVar11 = sVar4 + iVar12,
         iVar8 - iVar11 < 0 != (iVar8 < 0 != iVar11 < 0 && iVar11 < 0 == iVar8 - iVar11 < 0) ||
         iVar8 == iVar11)) {
        if ((iVar12 < 0) &&
           (iVar12 = iVar12 - sVar4,
           iVar8 - iVar12 < 0 != (iVar8 < 0 != iVar12 < 0 && iVar12 < 0 == iVar8 - iVar12 < 0))) {
          sVar5 = (short)iVar12;
        }
        else {
          cVar7 = '\0';
        }
      }
      else {
        sVar5 = ((int)(int16_t)DAT_febec722) + sVar4;
      }
    }
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(0xf03))))) = cVar2;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(0xf04))))) = bVar1;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(0xf02))))) = cVar7;
  (*((short *)camry_host_ptr((uint32_t)(puVar3 + 0xf22)))) = sVar5;
  (*((short *)camry_host_ptr((uint32_t)(puVar3 + 0xeee)))) = sVar10;
  (*((int *)camry_host_ptr((uint32_t)(puVar3 + 0xed0)))) = iVar9;
  return;
}

void reset_c728_monitors_and_seed_twenty_samples_cb1e8(void)

{
  int iVar1;
  undefined4 uVar2;
  uint uVar3;
  
  uVar2 = DAT_febeaee8;
  DAT_febec79b = 0;
  DAT_febec79a = 0;
  DAT_febec734 = 0;
  DAT_febec730 = 0;
  DAT_febec72c = 0;
  DAT_febec728 = 0;
  DAT_febec799 = 0;
  DAT_febec740 = 0;
  DAT_febec798 = 0;
  DAT_febec73e = 0;
  DAT_febec797 = 0;
  DAT_febec73c = 0;
  DAT_febec796 = 0;
  DAT_febec73a = 0;
  DAT_febec795 = 0;
  DAT_febec794 = 0;
  DAT_febec738 = 0;
  uVar3 = 0;
  do {
    iVar1 = uVar3 * 4;
    uVar3 = uVar3 + 1;
    *(undefined4 *)(((undefined *)camry_host_ptr((uint32_t)(0xfebec744u + (uint32_t)(iVar1) * 1u)))) = uVar2;
  } while (uVar3 < 0x14);
  return;
}

void debounce_c81c_c81d_into_c794_cb246(void)

{
  ushort uVar1;
  ushort uVar2;
  
  if (DAT_febec794 == '\0') {
    if ((DAT_febec7bf != '\x01') || ((DAT_febec81c != '\x01' && (DAT_febec81d != '\x01')))) {
      DAT_febec738 = 0;
      return;
    }
    if ((DAT_febec738 < DAT_000b04b0) &&
       (uVar1 = DAT_febec738 + 1, uVar2 = DAT_febec738 + 1, DAT_febec738 = uVar1,
       DAT_000b04b0 <= uVar2)) {
      DAT_febec794 = DAT_febec7bf;
      return;
    }
  }
  else if (DAT_febec7bf == '\0') {
    DAT_febec738 = 0;
    DAT_febec794 = '\0';
  }
  return;
}

void derive_c795_c79a_c79b_group_status_gates_cb2a2(void)

{
  bool bVar1;
  bool bVar2;
  bool bVar3;
  uint32_t puVar4;
  byte bVar5;
  byte bVar6;
  
  puVar4 = 0xfebeb800u;
  bVar5 = get_application_grouped_status(0x1a);
  bVar6 = get_application_grouped_status(0x17);
  if ((bVar5 | bVar6) == 0x5a) {
    bVar1 = false;
    bVar3 = false;
  }
  else {
    bVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0xa47))))) == '\0';
    bVar2 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0xb34))))) == '\0';
    bVar3 = bVar2;
    if (bVar1) goto LAB_000cb2e8;
  }
  bVar2 = bVar1;
LAB_000cb2e8:
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(0xf95))))) = bVar2;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(0xf9a))))) = bVar1;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(0xf9b))))) = bVar3;
  return;
}

void debounce_c80e_sign_relations_into_c796_cb2f8(void)

{
  ushort uVar1;
  ushort uVar2;
  
  if ((DAT_febec7bf == '\x01') &&
     ((((((0 < ((int)(int16_t)DAT_febec80e) && (((int)(int16_t)DAT_febec812) < 0)) || ((((int)(int16_t)DAT_febec80e) < 0 && (0 < ((int)(int16_t)DAT_febec812))))) ||
        (((0 < ((int)(int16_t)DAT_febec80e) && (0 < ((int)(int16_t)DAT_febec810))) &&
         (((int)(int32_t)DAT_febec800) - ((int)(int32_t)DAT_febec804) < 0 !=
          (((int)(int32_t)DAT_febec800) < 0 != ((int)(int32_t)DAT_febec804) < 0 &&
          ((int)(int32_t)DAT_febec804) < 0 == ((int)(int32_t)DAT_febec800) - ((int)(int32_t)DAT_febec804) < 0))))) ||
       ((((((int)(int16_t)DAT_febec80e) < 0 && (((int)(int16_t)DAT_febec810) < 0)) &&
         (((int)(int32_t)DAT_febec800) - ((int)(int32_t)DAT_febec804) < 0 ==
          (((int)(int32_t)DAT_febec800) < 0 != ((int)(int32_t)DAT_febec804) < 0 &&
          ((int)(int32_t)DAT_febec804) < 0 == ((int)(int32_t)DAT_febec800) - ((int)(int32_t)DAT_febec804) < 0) && ((int)(int32_t)DAT_febec800) != ((int)(int32_t)DAT_febec804))) ||
        ((((0 < ((int)(int16_t)DAT_febec816) && (0 < ((int)(int16_t)DAT_febec818))) || ((((int)(int16_t)DAT_febec816) < 0 && (((int)(int16_t)DAT_febec818) < 0))))
         || ((0 < ((int)(int16_t)DAT_febec808) && (((int)(int16_t)DAT_febec814) < 0)))))))) ||
      ((((int)(int16_t)DAT_febec808) < 0 && (0 < ((int)(int16_t)DAT_febec814))))))) {
    if ((DAT_febec73a <= DAT_000b04b2) &&
       (uVar1 = DAT_febec73a + 1, uVar2 = DAT_febec73a + 1, DAT_febec73a = uVar1,
       DAT_000b04b2 < uVar2)) {
      DAT_febec796 = DAT_febec7bf;
      return;
    }
  }
  else {
    DAT_febec73a = 0;
  }
  return;
}

short debounce_cc6c_inactive_magnitude_into_c797_cb396(void)

{
  int iVar1;
  ushort uVar2;
  ushort uVar3;
  short sVar4;
  uint32_t puVar5;
  short sVar6;
  uint uVar7;
  
  sVar4 = DAT_000b04d4;
  puVar5 = 0xfebeb800u;
  sVar6 = abs_s16_wrapping(((int)(int16_t)DAT_febecc6c));
  uVar3 = DAT_000b04b6;
  uVar7 = (uint)sVar6;
  if ((((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(0xfbf))))) == '\x01') || ((*((short *)camry_host_ptr((uint32_t)(puVar5 + 0xfbc)))) != sVar4)) ||
     (iVar1 = uVar7 - DAT_000b04b4,
     iVar1 < 0 != ((int)uVar7 < 0 && -1 < iVar1) || uVar7 == DAT_000b04b4)) {
    (*((undefined2 *)camry_host_ptr((uint32_t)(puVar5 + 0xf3c)))) = 0;
  }
  else {
    uVar2 = (*((ushort *)camry_host_ptr((uint32_t)(puVar5 + 0xf3c))));
    if ((uVar2 <= DAT_000b04b6) &&
       ((*((ushort *)camry_host_ptr((uint32_t)(puVar5 + 0xf3c)))) = uVar2 + 1, uVar3 < (ushort)(uVar2 + 1))) {
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(0xf97))))) = 1;
    }
  }
  return sVar6;
}

uint debounce_c80a_c80c_difference_into_c798_cb3f4(void)

{
  ushort uVar1;
  ushort uVar2;
  uint32_t puVar3;
  uint uVar4;
  
  puVar3 = 0xfebeb800u;
  uVar4 = abs_s32_wrapping((int)((int)(int16_t)DAT_febec80a) - (int)((int)(int16_t)DAT_febec80c));
  uVar2 = DAT_000b04ba;
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(0xf98))))) == '\0') {
    if (((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(0xfbf))))) == '\x01') && (DAT_000b04b8 < uVar4)) {
      uVar1 = (*((ushort *)camry_host_ptr((uint32_t)(puVar3 + 0xf3e))));
      if ((uVar1 < DAT_000b04ba) &&
         ((*((ushort *)camry_host_ptr((uint32_t)(puVar3 + 0xf3e)))) = uVar1 + 1, uVar2 <= (ushort)(uVar1 + 1))) {
        (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(0xf98))))) = 1;
      }
    }
    else {
      (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + 0xf3e)))) = 0;
    }
  }
  else if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(0xfbf))))) == '\0') {
    (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + 0xf3e)))) = 0;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(0xf98))))) = 0;
  }
  return uVar4;
}

void monitor_wrapped_aee8_delta_c744_ring_cb45e(void)

{
  ushort uVar1;
  ushort uVar2;
  int iVar3;
  uint uVar4;
  uint32_t puVar5;
  uint uVar6;
  char cVar7;
  int value;
  uint uVar8;
  
  iVar3 = DAT_febeaee8;
  uVar2 = DAT_febeae38;
  puVar5 = 0xfebeb800u;
  if (DAT_febec740 < 0x13) {
    uVar8 = (uint)(ushort)(DAT_febec740 + 1);
  }
  else {
    uVar8 = 0;
  }
  uVar4 = uVar8;
  if (uVar8 < DAT_000b04bc) {
    uVar4 = uVar8 + 0x14;
  }
  DAT_febec728 = *(int *)(((undefined *)camry_host_ptr((uint32_t)(0xfebec744u + (uint32_t)((uVar4 - DAT_000b04bc & 0xffff) * 4) * 1u))));
  cVar7 = DAT_febec799;
  if (DAT_febec799 == '\0') {
    if (DAT_febec7bf == '\x01') {
      value = DAT_febeaee8 - DAT_febec728;
      if (value + 0x3330000 < 0 == (-1 < value && value + 0x3330000 < 0)) {
        if (value + -0x3330000 < 0 == (value < 0 && -1 < value + -0x3330000)) {
          value = value + -0x6660000;
        }
      }
      else {
        value = value + 0x6660000;
      }
      puVar5 = 0xfebeb800u;
      uVar6 = abs_s32_wrapping(value);
      (*((int *)camry_host_ptr((uint32_t)(puVar5 + 0xf2c)))) = value;
      uVar1 = DAT_000b04be;
      (*((uint *)camry_host_ptr((uint32_t)(puVar5 + 0xf30)))) = uVar6;
      uVar4 = (uint)uVar1 * (uint)uVar2 >> 10;
      (*((uint *)camry_host_ptr((uint32_t)(puVar5 + 0xf34)))) = uVar4;
      cVar7 = uVar4 <= uVar6;
    }
  }
  else if (DAT_febec7bf == '\0') {
    cVar7 = '\0';
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(0xf99))))) = cVar7;
  (*((int *)camry_host_ptr((uint32_t)(puVar5 + uVar8 * 4 + 0xf44)))) = iVar3;
  (*((short *)camry_host_ptr((uint32_t)(puVar5 + 0xf40)))) = (short)uVar8;
  return;
}

undefined4 store_c7a0_c7bc_with_ones_complements_cb516(short param_1,short param_2)

{
  uint32_t puVar1;
  undefined4 uVar2;
  
  puVar1 = 0xfebeb800u;
  uVar2 = raise_priority_mask_and_return_previous_d1da0(0xffc0);
  (*((short *)camry_host_ptr((uint32_t)(puVar1 + 4000)))) = param_2;
  (*((short *)camry_host_ptr((uint32_t)(puVar1 + 0xfbc)))) = param_1;
  (*((short *)camry_host_ptr((uint32_t)(puVar1 + 0xfac)))) = -1 - param_1;
  (*((short *)camry_host_ptr((uint32_t)(puVar1 + 0xfaa)))) = -1 - param_2;
  restore_priority_mask_preserving_interrupt_enable_d1dc6(uVar2);
  return uVar2;
}

void initialize_c79c_transition_filter_state_cb548(void)

{
  short sVar1;
  byte bVar2;
  uint32_t puVar3;
  puVar3 = 0xfebeb800u;
  DAT_febec79c = 0;
  DAT_febec7be = 0;
  DAT_febec7a2 = DAT_000b04c4 * (ushort)DAT_000b04cd;
  DAT_febec7b4 = 0;
  DAT_febec7b5 = 0;
  DAT_febec7bf = 0;
  DAT_febec7a4 = DAT_000b04d4 * (ushort)DAT_000b04d0;
  DAT_febec7c0 = 0;
  DAT_febec7b3 = 0;
  DAT_febec79e = 0;
  store_c7a0_c7bc_with_ones_complements_cb516((*((volatile uint16_t *)camry_host_ptr(0xb04d4u))), (*((volatile uint16_t *)camry_host_ptr(0xb04c4u))));
  sVar1 = DAT_000b04c4;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(0xfb9))))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(0xfb2))))) = 0;
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + 0xfae)))) = 0;
  (*((short *)camry_host_ptr((uint32_t)(puVar3 + 0xfa6)))) = sVar1;
  bVar2 = DAT_000b04cd;
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + 0xfb0)))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(0xfb6))))) = bVar2;
  (*((short *)camry_host_ptr((uint32_t)(puVar3 + 0xfa8)))) = DAT_000b04d4;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(0xfb7))))) = DAT_000b04d0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(0xfba))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(0xfb5)))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(0xfb8))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(0xfb5)))));
  return;
}

void debounce_abs_adf2_c7be_banked_hysteresis_cb5e4(void)

{
  ushort uVar1;
  uint32_t puVar2;
  ushort uVar3;
  ushort *puVar4;
  
  puVar2 = 0xfebeb800u;
  uVar3 = abs_s16_wrapping(((int)(int16_t)DAT_febeadf2));
  puVar4 = ((ushort *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xb1464u + (uint32_t)((byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0xbc4))))) & 1) * 4u))))));
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(0xfbe))))) == '\0') {
    if (*puVar4 <= uVar3) {
      uVar1 = (*((ushort *)camry_host_ptr((uint32_t)(puVar2 + 0xf9c))));
      uVar3 = puVar4[2];
      if (uVar3 <= uVar1) {
        return;
      }
      (*((ushort *)camry_host_ptr((uint32_t)(puVar2 + 0xf9c)))) = uVar1 + 1;
      if ((ushort)(uVar1 + 1) < uVar3) {
        return;
      }
      (*((undefined2 *)camry_host_ptr((uint32_t)(puVar2 + 0xf9c)))) = 0;
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(0xfbe))))) = 1;
      return;
    }
  }
  else if (uVar3 < puVar4[1]) {
    uVar1 = (*((ushort *)camry_host_ptr((uint32_t)(puVar2 + 0xf9c))));
    uVar3 = puVar4[3];
    if (uVar3 <= uVar1) {
      return;
    }
    (*((ushort *)camry_host_ptr((uint32_t)(puVar2 + 0xf9c)))) = uVar1 + 1;
    if ((ushort)(uVar1 + 1) < uVar3) {
      return;
    }
    (*((undefined2 *)camry_host_ptr((uint32_t)(puVar2 + 0xf9c)))) = 0;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(0xfbe))))) = 0;
    return;
  }
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar2 + 0xf9c)))) = 0;
  return;
}

void latch_c7b4_with_fault_and_accd_timeout_gates_cb664(void)

{
  if (((((((DAT_febec7b4 == '\0') && (DAT_febeadbf < 2)) && (DAT_febeadc0 == '\0')) &&
        ((DAT_febec796 == '\0' && (DAT_febec797 == '\0')))) &&
       ((DAT_febec79a == '\x01' && ((DAT_febeaddd == '\0' && (DAT_febec79b == '\x01')))))) &&
      (DAT_febeaccd == '\0')) &&
     (DAT_febeae02 <= (*((ushort *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xb1464u + (uint32_t)(DAT_febeac3c & 1) * 4u)))) + 0x26)))))) {
    DAT_febec7b4 = DAT_febec79b;
    DAT_febec7b2 = '\0';
  }
  if ((DAT_febec7b4 == '\x01') && (DAT_febeaccd != '\0')) {
    DAT_febec7b2 = DAT_febec7b2 + 1;
  }
  else {
    DAT_febec7b2 = 0;
    if (DAT_febec7b4 != '\x01') {
      DAT_febec7b2 = 0;
      return;
    }
  }
  if (((((1 < DAT_febeadbf) || (DAT_febeadc0 != '\0')) || (DAT_febec796 != '\0')) ||
      (((DAT_febec797 != '\0' || ((DAT_febeadb9 >> 1 & 1) != 0)) ||
       ((DAT_febeaddd != '\0' || (((DAT_febeaccc >> 1 & 1) != 0 || (DAT_000b04d2 < DAT_febec7b2)))))
       ))) || ((DAT_febeaccd == '\0' &&
               ((*((ushort *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xb1464u + (uint32_t)(DAT_febeac3c & 1) * 4u)))) + 0x26)))) < DAT_febeae02)))) {
    DAT_febec7b4 = '\0';
    DAT_febec7b2 = 0;
  }
  return;
}

void step_c7bf_activation_and_exit_reason_cb73a(void)

{
  char cVar1;
  uint32_t puVar2;
  cVar1 = DAT_febeadb0;
  puVar2 = 0xfebeb800u;
  DAT_febec7c0 = DAT_febec7bf;
  if (DAT_febec7bf == '\0') {
    if (DAT_febec79e < DAT_000b04c0) {
      DAT_febec79e = DAT_febec79e + 1;
    }
    else if (((DAT_febec7b4 == '\x01') && (DAT_febec7be == '\0')) &&
            ((DAT_febec795 == '\x01' &&
             (((DAT_febec7b3 == '\0' && (DAT_febeadb0 == '1')) &&
              (DAT_febeae02 < (*((ushort *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xb1464u + (uint32_t)(DAT_febeac3c & 1) * 4u)))) + 0x24)))))))))) {
      DAT_febec7bf = '\x01';
      DAT_febec7b5 = 1;
      DAT_febec79e = 0;
      puVar2 = 0xfebeb800u;
      initialize_c7c4_fixed_point_control_state_cba80();
      reset_c728_monitors_and_seed_twenty_samples_cb1e8();
    }
  }
  else {
    if ((((DAT_febec7b4 == '\0') || (DAT_febec795 == '\0')) || (DAT_febec794 == '\x01')) ||
       ((DAT_febec798 == '\x01' || (DAT_febec799 == '\x01')))) {
      DAT_febec7b5 = 3;
    }
    else {
      if ((DAT_febeadb0 == '1') && (DAT_febec7be != '\x01')) goto LAB_000cb80c;
      DAT_febec7b5 = 2;
    }
    DAT_febec7bf = '\0';
  }
LAB_000cb80c:
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(0xfb3))))) = cVar1;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(0xfb9))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(0xf99)))));
  return;
}

void update_c7b4_and_c7bf_gates_cb81c(void)

{
  latch_c7b4_with_fault_and_accd_timeout_gates_cb664();
  step_c7bf_activation_and_exit_reason_cb73a();
  return;
}

undefined4 filter_two_c7bf_transition_targets_cb82c(void)

{
  int iVar1;
  byte bVar2;
  ushort uVar3;
  uint uVar4;
  uint uVar5;
  uint camry_first_quotient;
  byte *pbVar6;
  
  if ((DAT_febec7ba == '\x01') || (DAT_febec7b5 != '\x01')) {
    if ((DAT_febec7ba == '\x02') || (DAT_febec7b5 != '\x02')) {
      if ((DAT_febec7ba == '\x03') || (DAT_febec7b5 != '\x03')) goto LAB_000cb8e0;
      pbVar6 = ((undefined *)camry_host_ptr(0xb04d1u));
      DAT_febec7b6 = DAT_000b04ce;
    }
    else {
      pbVar6 = ((undefined *)camry_host_ptr(0xb04d0u));
      DAT_febec7b6 = DAT_000b04cd;
    }
    bVar2 = *pbVar6;
    DAT_febec7b7 = *pbVar6;
  }
  else {
    DAT_febec7b6 = DAT_000b04cc;
    DAT_febec7b7 = DAT_000b04cf;
    bVar2 = DAT_000b04cf;
  }
  DAT_febec7a4 = DAT_febec7bc * (ushort)bVar2;
  DAT_febec7a2 = DAT_febec7a0 * (ushort)DAT_febec7b6;
LAB_000cb8e0:
  DAT_febec7a8 = DAT_000b04d4;
  DAT_febec7a6 = DAT_000b04c4;
  if (DAT_febec7bf == '\x01') {
    DAT_febec7a8 = DAT_000b04c6;
    DAT_febec7a6 = DAT_000b04c2;
  }
  uVar5 = (uint)DAT_febec7b6;
  DAT_febec7a2 = (DAT_febec7a2 + DAT_febec7a6) - DAT_febec7a0;
  uVar4 = (uint)DAT_febec7a2;
  if (uVar5 != 0) {
    if (uVar4 == 0x80000000 && uVar5 == 0xffffffff) {
      uVar4 = 0;
    }
    else {
      uVar4 = (int)uVar4 / (int)uVar5;
    }
  }
  iVar1 = DAT_000b04c4 - 5;
  uVar3 = DAT_000b04c4;
  if (((int)(uVar4 - iVar1) < 0 == (iVar1 < 0 && iVar1 < 0 == (int)(uVar4 - iVar1) < 0)) ||
     (uVar3 = DAT_000b04c2, (int)(uVar4 - (DAT_000b04c2 + 5)) < 0 || uVar4 == DAT_000b04c2 + 5)) {
    uVar4 = uVar3;
    DAT_febec7a2 = uVar3 * DAT_febec7b6;
  }
  camry_first_quotient = uVar4;
  uVar5 = (uint)DAT_febec7b7;
  DAT_febec7a4 = (DAT_febec7a4 + DAT_febec7a8) - DAT_febec7bc;
  uVar4 = (uint)DAT_febec7a4;
  if (uVar5 != 0) {
    if (uVar4 == 0x80000000 && uVar5 == 0xffffffff) {
      uVar4 = 0;
    }
    else {
      uVar4 = (int)uVar4 / (int)uVar5;
    }
  }
  iVar1 = DAT_000b04c6 - 5;
  uVar3 = DAT_000b04c6;
  if (((int)(uVar4 - iVar1) < 0 == (iVar1 < 0 && iVar1 < 0 == (int)(uVar4 - iVar1) < 0)) ||
     (uVar3 = DAT_000b04d4, (int)(uVar4 - (DAT_000b04d4 + 5)) < 0 || uVar4 == DAT_000b04d4 + 5)) {
    uVar4 = uVar3;
    DAT_febec7a4 = uVar3 * DAT_febec7b7;
  }
  DAT_febec7b8 = DAT_febec7ba;
  DAT_febec7ba = DAT_febec7b5;
  return store_c7a0_c7bc_with_ones_complements_cb516(uVar4,camry_first_quotient);
}

uint get_c7bc_or_default_on_complement_failure_cb9ae(void)

{
  uint uVar1;
  
  uVar1 = (uint)DAT_febec7bc;
  if (DAT_febec7ac + uVar1 != 0xffff) {
    uVar1 = (uint)DAT_000b04d4;
  }
  return uVar1;
}

uint get_c7a0_or_default_on_complement_failure_cb9c8(void)

{
  uint uVar1;
  
  uVar1 = (uint)DAT_febec7a0;
  if (DAT_febec7aa + uVar1 != 0xffff) {
    uVar1 = (uint)DAT_000b04c4;
  }
  return uVar1;
}

void repair_c7a2_c7a4_filter_residuals_cb9e2(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  uint32_t puVar4;
  ushort uVar5;
  
  puVar4 = 0xfebeb800u;
  uVar5 = 0;
  iVar1 = (uint)DAT_febec7a2 - (uint)DAT_febec7a0 * (uint)DAT_febec7b6;
  iVar2 = (uint)DAT_febec7b6 * (uint)DAT_000b04c8;
  iVar3 = -iVar2;
  if ((iVar1 + iVar2 < 0 != (iVar1 < 0 != iVar3 < 0 && iVar3 < 0 == iVar1 + iVar2 < 0) ||
       iVar1 == iVar3) || (iVar1 - iVar2 < 0 == (iVar1 < 0 && -1 < iVar1 - iVar2))) {
    uVar5 = 1;
    DAT_febec7a2 = DAT_febec7a6 * (ushort)DAT_febec7b6;
  }
  iVar1 = (uint)DAT_febec7a4 - (uint)DAT_febec7bc * (uint)DAT_febec7b7;
  iVar2 = (uint)DAT_febec7b7 * (uint)DAT_000b04ca;
  iVar3 = -iVar2;
  if ((iVar1 + iVar2 < 0 != (iVar1 < 0 != iVar3 < 0 && iVar3 < 0 == iVar1 + iVar2 < 0) ||
       iVar1 == iVar3) || (iVar1 - iVar2 < 0 == (iVar1 < 0 && -1 < iVar1 - iVar2))) {
    uVar5 = uVar5 | 2;
    DAT_febec7a4 = DAT_febec7a8 * (ushort)DAT_febec7b7;
  }
  if (uVar5 != 0) {
    puVar4 = 0xfebeb800u;
    store_c7a0_c7bc_with_ones_complements_cb516((uVar5 & 2) ? DAT_febec7a8 : DAT_febec7bc,(uVar5 & 1) ? DAT_febec7a6 : DAT_febec7a0);
  }
  (*((ushort *)camry_host_ptr((uint32_t)(puVar4 + 0xfae)))) = uVar5;
  (*((ushort *)camry_host_ptr((uint32_t)(puVar4 + 0xfb0)))) = (*((ushort *)camry_host_ptr((uint32_t)(puVar4 + 0xfb0)))) | uVar5;
  return;
}

undefined4 initialize_c7c4_fixed_point_control_state_cba80(void)

{
  uint32_t puVar1;
  undefined4 uVar2;
  uint32_t puVar3;
  
  puVar1 = 0xfebeb800u;
  DAT_febec7de = 0;
  DAT_febec81c = 0;
  DAT_febec81d = 0;
  DAT_febec7fc = 0;
  DAT_febec7e6 = 0;
  DAT_febec80a = 0;
  DAT_febec7fd = 1;
  DAT_febec7e8 = 0;
  DAT_febec80c = 0;
  DAT_febec7dc = (undefined2)((((int)(int16_t)DAT_febeae90) * 0x27) / 0x400);
  DAT_febec7ec = 0;
  DAT_febec7cc = 0;
  DAT_febec80e = 0;
  DAT_febec7d4 = 0;
  DAT_febec810 = 0;
  DAT_febec7ee = 0;
  puVar3 = ((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xb1464u + (uint32_t)(DAT_febeac3c & 1) * 4u))))));
  DAT_febec7d0 = 0;
  DAT_febec800 = 0;
  DAT_febec7ff = 0;
  DAT_febec7f4 = (*((volatile uint16_t *)camry_host_ptr((uint32_t)(puVar3 + 0x14))));
  DAT_febec812 = 0;
  DAT_febec814 = 0;
  DAT_febec804 = 0;
  DAT_febec7d8 = (*((volatile uint32_t *)camry_host_ptr((uint32_t)(puVar3 + 0x18))));
  DAT_febec7f0 = 0;
  DAT_febec7f2 = 0;
  DAT_febec7c8 = 0;
  DAT_febec7f6 = (*((volatile uint16_t *)camry_host_ptr((uint32_t)(puVar3 + 8))));
  DAT_febec7f8 = (*((volatile uint16_t *)camry_host_ptr((uint32_t)(puVar3 + 0xc))));
  DAT_febec7fa = (*((volatile uint16_t *)camry_host_ptr((uint32_t)(puVar3 + 0x10))));
  DAT_febec7e0 = DAT_febec7dc;
  DAT_febec7e2 = DAT_febec7dc;
  DAT_febec7e4 = DAT_febec7dc;
  DAT_febec808 = DAT_febec7dc;
  uVar2 = raise_priority_mask_and_return_previous_d1da0(0xffc0);
  (*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + 0xfc4)))) = 0;
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + 0xfea)))) = 0;
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + 0x1016)))) = 0;
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + 0x1018)))) = 0;
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + 0x101a)))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0xffe))))) = 0;
  restore_priority_mask_preserving_interrupt_enable_d1dc6(uVar2);
  return uVar2;
}

void slew_c7dc_and_interpolate_c808_history_cbb66(void)

{
  int iVar1;
  short sVar2;
  int iVar3;
  short sVar4;
  int iVar5;
  short sVar6;
  ushort uVar7;
  uint uVar9;
  undefined *puVar10;
  int iVar8;
  
  sVar2 = ((int)(int16_t)DAT_febec7dc);
  puVar10 = ((void *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xb1464u + (uint32_t)(DAT_febeac3c & 1) * 4u)))))));
  iVar3 = (int)((int)(int16_t)DAT_febec7dc);
  sVar4 = (short)((((int)(int16_t)DAT_febeae90) * 0x27) / 0x400);
  DAT_febec7e0 = ((int)(int16_t)DAT_febec7dc);
  iVar5 = (int)(short)(sVar4 - ((int)(int16_t)DAT_febec7e2));
  DAT_febec7de = sVar4 - ((int)(int16_t)DAT_febec7e2);
  if ((iVar5 == 0) && (DAT_febec7fc < DAT_000b04e4)) {
    DAT_febec7fc = DAT_febec7fc + 1;
    iVar5 = iVar3;
    goto LAB_000cbc28;
  }
  DAT_febec7fc = '\0';
  sVar6 = (short)((((short)(ushort)DAT_000b04e4 * 5 + 5) * (int)*(short *)(puVar10 + 0x22)) / 1000);
  iVar8 = (int)sVar6;
  if (iVar5 - iVar8 < 0 == (iVar5 < 0 != iVar8 < 0 && iVar8 < 0 == iVar5 - iVar8 < 0) &&
      iVar5 != iVar8) {
LAB_000cbbe6:
    DAT_febec81d = 1;
    DAT_febec7dc = ((int)(int16_t)DAT_febec7dc) + sVar6;
  }
  else {
    if (iVar5 + iVar8 < 0 != (iVar5 < 0 != -iVar8 < 0 && -iVar8 < 0 == iVar5 + iVar8 < 0)) {
      sVar6 = -sVar6;
      goto LAB_000cbbe6;
    }
    DAT_febec81d = 0;
    DAT_febec7dc = sVar4;
  }
  iVar5 = (int)((int)(int16_t)DAT_febec7dc);
  iVar8 = (int)*(short *)(puVar10 + 0x20);
  sVar6 = *(short *)(puVar10 + 0x20);
  if (iVar5 - iVar8 < 0 != (iVar5 < 0 != iVar8 < 0 && iVar8 < 0 == iVar5 - iVar8 < 0) ||
      iVar5 == iVar8) {
    iVar1 = -iVar8;
    if (iVar5 + iVar8 < 0 == (iVar5 < 0 != iVar1 < 0 && iVar1 < 0 == iVar5 + iVar8 < 0)) {
      DAT_febec81c = 0;
      goto LAB_000cbc28;
    }
    iVar8 = (int)(short)iVar1;
    sVar6 = (short)iVar1;
  }
  DAT_febec7dc = sVar6;
  DAT_febec81c = 1;
  iVar5 = iVar8;
LAB_000cbc28:
  if ((iVar5 == iVar3) && (DAT_febec7fd < (byte)puVar10[0x28])) {
    uVar7 = (ushort)(byte)(DAT_febec7fd + 1);
  }
  else {
    DAT_febec7e6 = (short)iVar5 - sVar2;
    uVar7 = 1;
    DAT_febec7e4 = sVar2;
  }
  DAT_febec7fd = (char)uVar7;
  if ((byte)puVar10[0x29] < uVar7) {
    DAT_febec808 = (short)iVar5 * 0xf;
  }
  else {
    iVar3 = (int)(short)uVar7 * (int)(short)(((int)(int16_t)DAT_febec7e6) * 0xf);
    uVar9 = (uint)(byte)puVar10[0x2a];
    if (uVar9 != 0) {
      if (iVar3 == -0x80000000 && uVar9 == 0xffffffff) {
        iVar3 = 0;
      }
      else {
        iVar3 = iVar3 / (int)uVar9;
      }
    }
    DAT_febec808 = (short)iVar3 + ((int)(int16_t)DAT_febec7e4) * 0xf;
  }
  DAT_febec7e2 = sVar4;
  return;
}

void capture_ac88_baseline_and_clamp_c7c4_delta_cbc80(void)

{
  int iVar1;
  int iVar2;
  
  iVar2 = DAT_febec7c8;
  if ((DAT_febec7bf == '\x01') && (iVar2 = DAT_febeac88, DAT_febec7c0 != '\0')) {
    iVar2 = DAT_febec7c8;
  }
  iVar1 = DAT_febeac88 - iVar2;
  DAT_febec7c4 = 0x7d000000;
  if ((iVar1 + -0x7d000000 < 0 != (iVar1 < 0 && -1 < iVar1 + -0x7d000000) || iVar1 == 0x7d000000) &&
     (DAT_febec7c4 = iVar1,
     iVar1 + 0x7d000000 < 0 != (-1 < iVar1 && iVar1 + 0x7d000000 < 0) || iVar1 == -0x7d000000)) {
    DAT_febec7c4 = -0x7d000000;
  }
  DAT_febec7c8 = iVar2;
  return;
}

void normalize_c7c4_and_compose_c80c_cbcb8(void)

{
  int iVar1;
  int iVar2;
  uint uVar3;
  
  uVar3 = (uint)(DAT_febeae38 >> 6);
  if (uVar3 != 0) {
    iVar2 = ( (int)(DAT_febec7c4) / (int)0x100) * 0xe1;
    if (uVar3 != 0) {
      if (iVar2 == -0x80000000 && uVar3 == 0xffffffff) {
        iVar2 = -0x80000000;
      }
      else {
        iVar2 = iVar2 / (int)uVar3;
      }
    }
    DAT_febec7ea = 0x7fff;
    iVar1 = -iVar2;
    if (iVar1 + -0x7fff < 0 != (iVar1 < 0 && -1 < iVar1 + -0x7fff) || iVar2 == -0x7fff) {
      if (iVar1 + 0x7fff < 0 == (-1 < iVar1 && iVar1 + 0x7fff < 0) && iVar2 != 0x7fff) {
        DAT_febec7ea = (short)iVar1;
      }
      else {
        DAT_febec7ea = -0x7fff;
      }
    }
  }
  if ((int)DAT_febeaf20 + -0x7fff < 0 == ((int)DAT_febeaf20 < 0 && -1 < (int)DAT_febeaf20 + -0x7fff) &&
      ((int)(int32_t)DAT_febeaf20) != 0x7fff) {
    iVar2 = 0x7fff;
  }
  else {
    iVar2 = ((int)(int32_t)DAT_febeaf20);
    if ((int)DAT_febeaf20 + 0x7fff < 0 != (-1 < (int)DAT_febeaf20 && (int)DAT_febeaf20 + 0x7fff < 0)) {
      iVar2 = -0x7fff;
    }
  }
  DAT_febec80c = (short)iVar2;
  DAT_febec80a = DAT_febec80c;
  if ((DAT_febec7bf == '\x01') && (DAT_febec7c0 == '\0')) {
    DAT_febec7e8 = DAT_febec80c;
  }
  if ((DAT_febec7bf != '\0') || (DAT_febec7bc != DAT_000b04d4)) {
    iVar2 = (int)((int)(int16_t)DAT_febec7e8) + (int)((int)(int16_t)DAT_febec7ea);
    if (iVar2 + -0x7fff < 0 == (iVar2 < 0 && -1 < iVar2 + -0x7fff) && iVar2 != 0x7fff) {
      iVar2 = 0x7fff;
    }
    else if (iVar2 + 0x7fff < 0 != (-1 < iVar2 && iVar2 + 0x7fff < 0)) {
      iVar2 = -0x7fff;
    }
    DAT_febec80c = (short)iVar2;
  }
  return;
}

void debounce_ae02_and_select_c7f4_coefficients_cbd64(void)

{
  uint32_t puVar1;
  
  if (DAT_febeae02 < DAT_000b04d6) {
    if (DAT_febec7f0 <= DAT_000b04d8) {
      DAT_febec7f0 = DAT_febec7f0 + 1;
    }
    if (DAT_000b04d8 < DAT_febec7f0) {
      puVar1 = ((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xb1464u + (uint32_t)(DAT_febeac3c & 1) * 4u))))));
      DAT_febec7f4 = (*((volatile uint16_t *)camry_host_ptr((uint32_t)(puVar1 + 0x14))));
      DAT_febec7d8 = (*((volatile uint32_t *)camry_host_ptr((uint32_t)(puVar1 + 0x18))));
      DAT_febec7f6 = (*((volatile uint16_t *)camry_host_ptr((uint32_t)(puVar1 + 8))));
      DAT_febec7f8 = (*((volatile uint16_t *)camry_host_ptr((uint32_t)(puVar1 + 0xc))));
      DAT_febec7fa = (*((volatile uint16_t *)camry_host_ptr((uint32_t)(puVar1 + 0x10))));
    }
  }
  else {
    DAT_febec7f0 = 0;
  }
  if (DAT_febeae02 < DAT_000b04d6) {
    DAT_febec7f2 = 0;
  }
  else {
    if (DAT_febec7f2 <= DAT_000b04d8) {
      DAT_febec7f2 = DAT_febec7f2 + 1;
    }
    if (DAT_000b04d8 < DAT_febec7f2) {
      puVar1 = ((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xb1464u + (uint32_t)(DAT_febeac3c & 1) * 4u))))));
      DAT_febec7f4 = (*((volatile uint16_t *)camry_host_ptr((uint32_t)(puVar1 + 0x16))));
      DAT_febec7d8 = (*((volatile uint32_t *)camry_host_ptr((uint32_t)(puVar1 + 0x1c))));
      DAT_febec7f6 = (*((volatile uint16_t *)camry_host_ptr((uint32_t)(puVar1 + 10))));
      DAT_febec7f8 = (*((volatile uint16_t *)camry_host_ptr((uint32_t)(puVar1 + 0xe))));
      DAT_febec7fa = (*((volatile uint16_t *)camry_host_ptr((uint32_t)(puVar1 + 0x12))));
      return;
    }
  }
  return;
}

void step_c808_c80c_error_filter_and_integrator_cbe28(void)

{
  undefined1 uVar1;
  int iVar2;
  uint32_t puVar3;
  short sVar4;
  int iVar6;
  short sVar7;
  int iVar8;
  undefined2 uVar9;
  int iVar10;
  int iVar5;
  
  puVar3 = 0xfebeb800u;
  sVar4 = abs_s16_wrapping(((int)(int16_t)DAT_febec7dc));
  iVar5 = (int)sVar4;
  sVar4 = abs_s16_wrapping((*((short *)camry_host_ptr((uint32_t)(puVar3 + 0xfe0)))));
  iVar6 = (int)sVar4;
  iVar8 = (int)DAT_000b04da;
  iVar2 = (int)(*((short *)camry_host_ptr((uint32_t)(puVar3 + 0x1008)))) - (int)(*((short *)camry_host_ptr((uint32_t)(puVar3 + 0x100c))));
  iVar10 = iVar8;
  if ((iVar2 - iVar8 < 0 != (iVar2 < 0 != iVar8 < 0 && iVar8 < 0 == iVar2 - iVar8 < 0) ||
       iVar2 == iVar8) &&
     (iVar10 = -iVar8,
     iVar2 + iVar8 < 0 == (iVar2 < 0 != iVar10 < 0 && iVar10 < 0 == iVar2 + iVar8 < 0) &&
     iVar2 != iVar10)) {
    iVar10 = iVar2;
  }
  sVar4 = (*((short *)camry_host_ptr((uint32_t)(puVar3 + 0x100e))));
  (*((short *)camry_host_ptr((uint32_t)(puVar3 + 0xfec)))) = (short)iVar10;
  (*((short *)camry_host_ptr((uint32_t)(puVar3 + 0x1010)))) = sVar4;
  iVar2 = (*((int *)camry_host_ptr((uint32_t)(puVar3 + 0xfcc)))) + ((int)(short)iVar10 - (*((int *)camry_host_ptr((uint32_t)(puVar3 + 0xfd4)))));
  (*((int *)camry_host_ptr((uint32_t)(puVar3 + 0xfcc)))) = iVar2;
  iVar10 = (int)DAT_000b04dc;
  if (iVar10 != 0) {
    if (iVar2 == -0x80000000 && iVar10 == -1) {
      iVar2 = -0x80000000;
    }
    else {
      iVar2 = (int)iVar2 / (int)iVar10;
    }
  }
  (*((int *)camry_host_ptr((uint32_t)(puVar3 + 0xfd4)))) = iVar2;
  if (iVar2 + -0x7fff < 0 == (iVar2 < 0 && -1 < iVar2 + -0x7fff) && iVar2 != 0x7fff) {
    iVar10 = 0x7fff;
  }
  else {
    iVar10 = -0x7fff;
    if (iVar2 + 0x7fff < 0 == (-1 < iVar2 && iVar2 + 0x7fff < 0)) {
      iVar10 = (int)(short)iVar2;
    }
  }
  sVar7 = (short)iVar10;
  (*((short *)camry_host_ptr((uint32_t)(puVar3 + 0x100e)))) = sVar7;
  iVar2 = (int)(((sVar4 + iVar10) * (int)(*((short *)camry_host_ptr((uint32_t)(puVar3 + 0xff4)))))) / (int)0x80;
  if (iVar2 + -0x7fff < 0 == (iVar2 < 0 && -1 < iVar2 + -0x7fff) && iVar2 != 0x7fff) {
    iVar10 = 0x7fff;
  }
  else {
    iVar10 = (int)(short)iVar2;
    if (iVar2 + 0x7fff < 0 != (-1 < iVar2 && iVar2 + 0x7fff < 0)) {
      iVar10 = -0x7fff;
    }
  }
  (*((short *)camry_host_ptr((uint32_t)(puVar3 + 0xfee)))) = (short)iVar10;
  if ((((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(0xffe))))) != '\x02') || (iVar10 < 0)) && (((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(0xffe))))) != '\x01' || (-1 < iVar10)))) {
    (*((int *)camry_host_ptr((uint32_t)(puVar3 + 0xfd0)))) = (*((int *)camry_host_ptr((uint32_t)(puVar3 + 0xfd0)))) + iVar10;
  }
  iVar8 = (*((int *)camry_host_ptr((uint32_t)(puVar3 + 0xfd0))));
  iVar10 = (*((int *)camry_host_ptr((uint32_t)(puVar3 + 0xfd8))));
  iVar2 = iVar10;
  if ((iVar8 - iVar10 < 0 != (iVar8 < 0 != iVar10 < 0 && iVar10 < 0 == iVar8 - iVar10 < 0) ||
       iVar8 == iVar10) &&
     (iVar2 = -iVar10,
     iVar8 + iVar10 < 0 == (iVar8 < 0 != iVar2 < 0 && iVar2 < 0 == iVar8 + iVar10 < 0) &&
     iVar8 != iVar2)) {
    iVar2 = iVar8;
  }
  (*((int *)camry_host_ptr((uint32_t)(puVar3 + 0xfd0)))) = iVar2;
  iVar10 = (*((int *)camry_host_ptr((uint32_t)(puVar3 + 0x1000))));
  (*((int *)camry_host_ptr((uint32_t)(puVar3 + 0x1000)))) = iVar2;
  uVar1 = 0;
  (*((int *)camry_host_ptr((uint32_t)(puVar3 + 0x1004)))) = iVar10;
  if ((iVar5 - iVar6 < 0 == (iVar5 < 0 != iVar6 < 0 && iVar6 < 0 == iVar5 - iVar6 < 0) &&
       iVar5 != iVar6) ||
     (uVar1 = 1, iVar5 - iVar6 < 0 != (iVar5 < 0 != iVar6 < 0 && iVar6 < 0 == iVar5 - iVar6 < 0))) {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(0xfff))))) = uVar1;
  }
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(0xfff))))) == '\0') {
    iVar2 = (int)(*((short *)camry_host_ptr((uint32_t)(puVar3 + 0xff6)))) * (int)sVar7;
    if (iVar2 + -0x7fff < 0 != (iVar2 < 0 && -1 < iVar2 + -0x7fff) || iVar2 == 0x7fff) {
LAB_000cbf5a:
      if (iVar2 + 0x7fff < 0 == (-1 < iVar2 && iVar2 + 0x7fff < 0)) {
        uVar9 = (undefined2)iVar2;
      }
      else {
        uVar9 = 0x8001;
      }
      goto LAB_000cbf66;
    }
  }
  else {
    iVar2 = (int)(*((short *)camry_host_ptr((uint32_t)(puVar3 + 0xff8)))) * (int)sVar7;
    if (iVar2 + -0x7fff < 0 != (iVar2 < 0 && -1 < iVar2 + -0x7fff) || iVar2 == 0x7fff)
    goto LAB_000cbf5a;
  }
  uVar9 = 0x7fff;
LAB_000cbf66:
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + 0x1012)))) = uVar9;
  iVar2 = (int)(((int)DAT_000b04de * (int)(*((short *)camry_host_ptr((uint32_t)(puVar3 + 0x1008)))))) / (int)0x80;
  if (iVar2 + -0x7fff < 0 == (iVar2 < 0 && -1 < iVar2 + -0x7fff) && iVar2 != 0x7fff) {
    uVar9 = 0x7fff;
  }
  else if (iVar2 + 0x7fff < 0 == (-1 < iVar2 && iVar2 + 0x7fff < 0)) {
    uVar9 = (undefined2)iVar2;
  }
  else {
    uVar9 = 0x8001;
  }
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + 0x1014)))) = uVar9;
  return;
}

void sum_c814_c818_c800_c812_with_limit_status_cbf9e(void)

{
  bool bVar1;
  short sVar2;
  int iVar4;
  int iVar5;
  int iVar3;
  
  iVar5 = (int)DAT_000b04e2;
  sVar2 = (short)((((int)(int16_t)DAT_febec172) * 10) / 8);
  iVar3 = (int)sVar2;
  DAT_febec816 = DAT_000b04e2;
  if ((iVar3 - iVar5 < 0 != (iVar3 < 0 != iVar5 < 0 && iVar5 < 0 == iVar3 - iVar5 < 0) ||
       iVar3 == iVar5) &&
     (iVar4 = -iVar5, DAT_febec816 = sVar2,
     iVar3 + iVar5 < 0 != (iVar3 < 0 != iVar4 < 0 && iVar4 < 0 == iVar3 + iVar5 < 0) ||
     iVar3 == iVar4)) {
    DAT_febec816 = (short)iVar4;
  }
  iVar3 = -((int)(int16_t)DAT_febec7fa * (int)(int16_t)DAT_febec816) / 0x40;
  iVar5 = 0x7fff;
  if ((iVar3 + -0x7fff < 0 != (iVar3 < 0 && -1 < iVar3 + -0x7fff) || iVar3 == 0x7fff) &&
     (iVar5 = iVar3, iVar3 + 0x7fff < 0 != (-1 < iVar3 && iVar3 + 0x7fff < 0) || iVar3 == -0x7fff))
  {
    iVar5 = -0x7fff;
  }
  DAT_febec818 = (short)iVar5;
  iVar4 = (int)DAT_000b04e0;
  iVar3 = (int)((int)(int16_t)DAT_febec814) + (int)(short)iVar5 + DAT_febec800 + ((int)(int16_t)DAT_febec812);
  if (iVar3 - iVar4 < 0 == (iVar3 < 0 != iVar4 < 0 && iVar4 < 0 == iVar3 - iVar4 < 0) &&
      iVar3 != iVar4) {
    DAT_febec7fe = 2;
    DAT_febec81a = DAT_000b04e0;
  }
  else {
    iVar5 = iVar3 + DAT_000b04e0;
    bVar1 = -(int)DAT_000b04e0 < 0;
    if (iVar5 < 0 == (iVar3 < 0 != bVar1 && bVar1 == iVar5 < 0)) {
      DAT_febec81a = (short)iVar3;
      DAT_febec7fe = 0;
    }
    else {
      DAT_febec7fe = 1;
      DAT_febec81a = -DAT_000b04e0;
    }
  }
  return;
}
