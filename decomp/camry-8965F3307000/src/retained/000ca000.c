#include "common.h"

void debounce_c716_sign_relations_report_10f_ca04e(void)

{
  ushort uVar1;
  ushort uVar2;
  uint32_t puVar3;
  puVar3 = 0xfebeb800u;
  if (DAT_000b0468 != '\x01') {
    if ((DAT_febec6b0 == '\x01') &&
       ((((((0 < ((int)(int16_t)DAT_febec716) && (((int)(int16_t)DAT_febec71a) < 0)) || ((((int)(int16_t)DAT_febec716) < 0 && (0 < ((int)(int16_t)DAT_febec71a)))))
          || (((0 < ((int)(int16_t)DAT_febec716) && (0 < ((int)(int16_t)DAT_febec718))) &&
              (((int)(int32_t)DAT_febec708) - ((int)(int32_t)DAT_febec70c) < 0 !=
               (((int)(int32_t)DAT_febec708) < 0 != ((int)(int32_t)DAT_febec70c) < 0 &&
               ((int)(int32_t)DAT_febec70c) < 0 == ((int)(int32_t)DAT_febec708) - ((int)(int32_t)DAT_febec70c) < 0))))) ||
         ((((((int)(int16_t)DAT_febec716) < 0 && (((int)(int16_t)DAT_febec718) < 0)) &&
           (((int)(int32_t)DAT_febec708) - ((int)(int32_t)DAT_febec70c) < 0 ==
            (((int)(int32_t)DAT_febec708) < 0 != ((int)(int32_t)DAT_febec70c) < 0 &&
            ((int)(int32_t)DAT_febec70c) < 0 == ((int)(int32_t)DAT_febec708) - ((int)(int32_t)DAT_febec70c) < 0) && ((int)(int32_t)DAT_febec708) != ((int)(int32_t)DAT_febec70c)))
          || ((((0 < ((int)(int16_t)DAT_febec71e) && (0 < ((int)(int16_t)DAT_febec720))) ||
               ((((int)(int16_t)DAT_febec71e) < 0 && (((int)(int16_t)DAT_febec720) < 0)))) ||
              ((0 < ((int)(int16_t)DAT_febec710) && (((int)(int16_t)DAT_febec71c) < 0)))))))) ||
        ((((int)(int16_t)DAT_febec710) < 0 && (0 < ((int)(int16_t)DAT_febec71c))))))) {
      if ((DAT_febec622 <= DAT_000b045a) &&
         (uVar1 = DAT_febec622 + 1, uVar2 = DAT_febec622 + 1, DAT_febec622 = uVar1,
         DAT_000b045a < uVar2)) {
        DAT_febec682 = DAT_febec6b0;
      }
    }
    else {
      DAT_febec622 = 0;
    }
    if (((DAT_febec6ae == '\x01') && (DAT_febec682 == '\x01')) && (DAT_febec62b == '\0')) {
      report_diagnostic_event_failure_ffff_32_bdb64(0x10f);
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(0xe2b))))) = 1;
    }
  }
  return;
}

short debounce_cc6a_inactive_magnitude_report_110_ca124(void)

{
  int iVar1;
  ushort uVar2;
  ushort uVar3;
  short sVar4;
  uint32_t puVar5;
  short sVar6;
  uint uVar7;
  
  sVar4 = DAT_000b049a;
  puVar5 = 0xfebeb800u;
  sVar6 = abs_s16_wrapping(((int)(int16_t)DAT_febecc6a));
  uVar3 = DAT_000b045e;
  uVar7 = (uint)sVar6;
  if ((((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(0xeb0))))) == '\x01') || ((*((short *)camry_host_ptr((uint32_t)(puVar5 + 0xea8)))) != sVar4)) ||
     (iVar1 = uVar7 - DAT_000b045c,
     iVar1 < 0 != ((int)uVar7 < 0 && -1 < iVar1) || uVar7 == DAT_000b045c)) {
    (*((undefined2 *)camry_host_ptr((uint32_t)(puVar5 + 0xe24)))) = 0;
  }
  else {
    uVar2 = (*((ushort *)camry_host_ptr((uint32_t)(puVar5 + 0xe24))));
    if ((uVar2 <= DAT_000b045e) &&
       ((*((ushort *)camry_host_ptr((uint32_t)(puVar5 + 0xe24)))) = uVar2 + 1, uVar3 < (ushort)(uVar2 + 1))) {
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(0xe83))))) = 1;
    }
  }
  if ((((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(0xeae))))) == '\x01') && ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(0xe83))))) == '\x01')) && ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(0xe2c))))) == '\0')) {
    report_diagnostic_event_failure_ffff_32_bdb64(0x110);
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(0xe2c))))) = 1;
  }
  return sVar6;
}

void debounce_c712_c714_difference_report_111_ca1a8(void)

{
  ushort uVar1;
  ushort uVar2;
  uint32_t puVar3;
  uint uVar4;
  char cVar5;
  
  puVar3 = 0xfebeb800u;
  if (DAT_000b0469 != '\x01') {
    uVar4 = abs_s32_wrapping((int)((int)(int16_t)DAT_febec712) - (int)((int)(int16_t)DAT_febec714));
    uVar2 = DAT_000b0462;
    cVar5 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(0xe84)))));
    if (cVar5 == '\0') {
      if (((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(0xeb0))))) == '\x01') && (DAT_000b0460 < uVar4)) {
        uVar1 = (*((ushort *)camry_host_ptr((uint32_t)(puVar3 + 0xe26))));
        if ((uVar1 < DAT_000b0462) &&
           ((*((ushort *)camry_host_ptr((uint32_t)(puVar3 + 0xe26)))) = uVar1 + 1, uVar2 <= (ushort)(uVar1 + 1))) {
          cVar5 = '\x01';
          (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(0xe84))))) = 1;
        }
      }
      else {
        (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + 0xe26)))) = 0;
      }
    }
    else if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(0xeb0))))) == '\0') {
      (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + 0xe26)))) = 0;
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(0xe84))))) = 0;
      cVar5 = '\0';
    }
    if ((((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(0xeae))))) == '\x01') && (cVar5 == '\x01')) && ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(0xe2d))))) == '\0')) {
      report_diagnostic_event_failure_ffff_32_bdb64(0x111);
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(0xe2d))))) = 1;
    }
  }
  return;
}

void monitor_wrapped_aee8_delta_c630_ring_ca242(void)

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
  if (DAT_febec628 < 0x13) {
    uVar8 = (uint)(ushort)(DAT_febec628 + 1);
  }
  else {
    uVar8 = 0;
  }
  uVar4 = uVar8;
  if (uVar8 < DAT_000b0464) {
    uVar4 = uVar8 + 0x14;
  }
  DAT_febec610 = *(int *)(((undefined *)camry_host_ptr((uint32_t)(0xfebec630u + (uint32_t)((uVar4 - DAT_000b0464 & 0xffff) * 4) * 1u))));
  cVar7 = DAT_febec685;
  if (DAT_febec685 == '\0') {
    if (DAT_febec6b0 == '\x01') {
      value = DAT_febeaee8 - DAT_febec610;
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
      (*((int *)camry_host_ptr((uint32_t)(puVar5 + 0xe14)))) = value;
      uVar1 = DAT_000b0466;
      (*((uint *)camry_host_ptr((uint32_t)(puVar5 + 0xe18)))) = uVar6;
      uVar4 = (uint)uVar1 * (uint)uVar2 >> 10;
      (*((uint *)camry_host_ptr((uint32_t)(puVar5 + 0xe1c)))) = uVar4;
      cVar7 = uVar4 <= uVar6;
    }
  }
  else if (DAT_febec6b0 == '\0') {
    cVar7 = '\0';
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(0xe85))))) = cVar7;
  (*((int *)camry_host_ptr((uint32_t)(puVar5 + uVar8 * 4 + 0xe30)))) = iVar3;
  (*((short *)camry_host_ptr((uint32_t)(puVar5 + 0xe28)))) = (short)uVar8;
  return;
}

undefined4 store_c68c_c6a8_with_ones_complements_ca312(short param_1,short param_2)

{
  uint32_t puVar1;
  undefined4 uVar2;
  
  puVar1 = 0xfebeb800u;
  uVar2 = raise_priority_mask_and_return_previous_d1da0(0xffc0);
  (*((short *)camry_host_ptr((uint32_t)(puVar1 + 0xe8c)))) = param_2;
  (*((short *)camry_host_ptr((uint32_t)(puVar1 + 0xea8)))) = param_1;
  (*((short *)camry_host_ptr((uint32_t)(puVar1 + 0xe98)))) = -1 - param_1;
  (*((short *)camry_host_ptr((uint32_t)(puVar1 + 0xe96)))) = -1 - param_2;
  restore_priority_mask_preserving_interrupt_enable_d1dc6(uVar2);
  return uVar2;
}

void initialize_c688_transition_filter_state_ca344(void)

{
  byte bVar1;
  uint32_t puVar2;
  puVar2 = 0xfebeb800u;
  DAT_febec68a = 0;
  DAT_febec6a0 = 0;
  DAT_febec6b1 = 0;
  DAT_febec6b0 = 0;
  DAT_febec69f = 0;
  DAT_febec6af = 0;
  DAT_febec6ae = 1;
  DAT_febec6a1 = 0;
  DAT_febec68e = DAT_000b048a * (ushort)DAT_000b0493;
  DAT_febec6ad = 0;
  DAT_febec6ac = 0;
  DAT_febec690 = DAT_000b049a * (ushort)DAT_000b0496;
  DAT_febec6ab = 0;
  DAT_febec6aa = 0;
  DAT_febec688 = 0;
  store_c68c_c6a8_with_ones_complements_ca312((*((volatile uint16_t *)camry_host_ptr(0xb049au))), (*((volatile uint16_t *)camry_host_ptr(0xb048au))));
  (*((short *)camry_host_ptr((uint32_t)(puVar2 + 0xe92)))) = DAT_000b048a;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(0xea2))))) = DAT_000b0493;
  (*((short *)camry_host_ptr((uint32_t)(puVar2 + 0xe94)))) = DAT_000b049a;
  bVar1 = DAT_000b0496;
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar2 + 0xe9c)))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(0xea3))))) = bVar1;
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar2 + 0xe9a)))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(0xe9e))))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(0xea5))))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(0xea4))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(0xeaf)))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(0xea6))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(0xeaf)))));
  return;
}

void debounce_abs_adf2_c6aa_hysteresis_ca3f6(void)

{
  ushort uVar1;
  ushort uVar2;
  uint32_t puVar3;
  ushort uVar4;
  
  puVar3 = 0xfebeb800u;
  uVar4 = abs_s16_wrapping(((int)(int16_t)DAT_febeadf2));
  uVar1 = DAT_000b0474;
  uVar2 = DAT_000b0472;
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(0xeaa))))) == '\0') {
    if (DAT_000b046e <= uVar4) {
      uVar1 = (*((ushort *)camry_host_ptr((uint32_t)(puVar3 + 0xe88))));
      if (DAT_000b0472 <= uVar1) {
        return;
      }
      (*((ushort *)camry_host_ptr((uint32_t)(puVar3 + 0xe88)))) = uVar1 + 1;
      if ((ushort)(uVar1 + 1) < uVar2) {
        return;
      }
      (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + 0xe88)))) = 0;
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(0xeaa))))) = 1;
      return;
    }
  }
  else if (uVar4 < DAT_000b0470) {
    uVar2 = (*((ushort *)camry_host_ptr((uint32_t)(puVar3 + 0xe88))));
    if (DAT_000b0474 <= uVar2) {
      return;
    }
    (*((ushort *)camry_host_ptr((uint32_t)(puVar3 + 0xe88)))) = uVar2 + 1;
    if ((ushort)(uVar2 + 1) < uVar1) {
      return;
    }
    (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + 0xe88)))) = 0;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(0xeaa))))) = 0;
    return;
  }
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + 0xe88)))) = 0;
  return;
}

void set_c6ae_report_gate_one_ca550(void)

{
  DAT_febec6ae = 1;
  return;
}

void latch_c6a1_with_fault_and_accd_timeout_gates_ca558(void)

{
  if (((((((DAT_febec6a1 == '\0') && (DAT_febeadbf == '\0')) && (DAT_febeadc0 == '\0')) &&
        ((DAT_febec682 == '\0' && (DAT_febec683 == '\0')))) &&
       ((DAT_febeadb9 == 0 && ((DAT_febeadc1 == '\0' && (DAT_febeaccc == 0)))))) &&
      (DAT_febeaccd == '\0')) && (DAT_febeae02 <= DAT_000b046a)) {
    DAT_febec6a1 = '\x01';
    DAT_febec69e = '\0';
  }
  if ((DAT_febec6a1 == '\x01') && (DAT_febeaccd != '\0')) {
    DAT_febec69e = DAT_febec69e + 1;
  }
  else {
    DAT_febec69e = 0;
    if (DAT_febec6a1 != '\x01') {
      DAT_febec69e = 0;
      return;
    }
  }
  if (((((DAT_febeadbf != '\0') || (DAT_febeadc0 != '\0')) || (DAT_febec682 != '\0')) ||
      (((DAT_febec683 != '\0' || ((DAT_febeadb9 >> 1 & 1) != 0)) ||
       ((DAT_febeadc1 != '\0' || (((DAT_febeaccc >> 1 & 1) != 0 || (DAT_000b0498 < DAT_febec69e)))))
       ))) || ((DAT_febeaccd == '\0' && (DAT_000b046a < DAT_febeae02)))) {
    DAT_febec6a1 = '\0';
    DAT_febec69e = 0;
  }
  return;
}

void step_c6b0_activation_and_exit_reason_ca614(void)

{
  char cVar1;
  uint32_t puVar2;
  cVar1 = DAT_febeadb0;
  puVar2 = 0xfebeb800u;
  DAT_febec6b1 = DAT_febec6b0;
  if (DAT_febec6b0 != '\0') {
    if ((((DAT_febec6a1 == '\0') || (DAT_febec681 == '\0')) || (DAT_febec680 == '\x01')) ||
       ((DAT_febec684 == '\x01' || (DAT_febec685 == '\x01')))) {
      DAT_febec6af = '\x03';
      DAT_febec6b0 = '\0';
      if ((DAT_febec681 == '\0') && (DAT_febec69f == '\0')) {
        puVar2 = 0xfebeb800u;
        report_diagnostic_event_failure_ffff_32_bdb64(0x10d);
        (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(0xe9f))))) = 1;
      }
    }
    else if (((DAT_febeadb0 != '\x19') && (DAT_febeadb0 != '\x1b')) || (DAT_febec6aa == '\x01')) {
      DAT_febec6b0 = '\0';
      DAT_febec6af = '\x02';
    }
    goto LAB_000ca706;
  }
  if (DAT_febec6a1 == '\x01') {
    if (DAT_000b0486 <= DAT_febec68a) {
      if (((((DAT_febec6aa == '\0') && (DAT_febec681 == '\x01')) && (DAT_febec6a0 == '\0')) &&
          ((DAT_febeadb0 == '\x19' || (DAT_febeadb0 == '\x1b')))) && (DAT_febeae02 < DAT_000b046c))
      {
        DAT_febec6b0 = DAT_febec6a1;
        DAT_febec6af = DAT_febec6a1;
        DAT_febec68a = 0;
        puVar2 = 0xfebeb800u;
        initialize_c6b8_fixed_point_control_state_caaa2();
        reset_c610_monitors_and_seed_twenty_samples_c9f38();
        goto LAB_000ca706;
      }
      goto LAB_000ca68a;
    }
  }
  else {
LAB_000ca68a:
    if (DAT_000b0486 <= DAT_febec68a) goto LAB_000ca706;
  }
  DAT_febec68a = DAT_febec68a + 1;
LAB_000ca706:
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(0xea0))))) = cVar1;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(0xea5))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(0xe85)))));
  return;
}

void update_c6ae_c6a1_and_c6b0_gates_ca716(void)

{
  set_c6ae_report_gate_one_ca550();
  latch_c6a1_with_fault_and_accd_timeout_gates_ca558();
  step_c6b0_activation_and_exit_reason_ca614();
  return;
}

undefined4 filter_two_c6b0_transition_targets_ca72a(void)

{
  int iVar1;
  byte bVar2;
  ushort uVar3;
  uint uVar4;
  uint uVar5;
  uint camry_first_quotient;
  byte *pbVar6;
  
  if ((DAT_febec6a6 == '\x01') || (DAT_febec6af != '\x01')) {
    if ((DAT_febec6a6 == '\x02') || (DAT_febec6af != '\x02')) {
      if ((DAT_febec6a6 == '\x03') || (DAT_febec6af != '\x03')) goto LAB_000ca7de;
      pbVar6 = ((undefined *)camry_host_ptr(0xb0497u));
      DAT_febec6a2 = DAT_000b0494;
    }
    else {
      pbVar6 = ((undefined *)camry_host_ptr(0xb0496u));
      DAT_febec6a2 = DAT_000b0493;
    }
    bVar2 = *pbVar6;
    DAT_febec6a3 = *pbVar6;
  }
  else {
    DAT_febec6a2 = DAT_000b0492;
    DAT_febec6a3 = DAT_000b0495;
    bVar2 = DAT_000b0495;
  }
  DAT_febec690 = DAT_febec6a8 * (ushort)bVar2;
  DAT_febec68e = DAT_febec68c * (ushort)DAT_febec6a2;
LAB_000ca7de:
  DAT_febec694 = DAT_000b049a;
  DAT_febec692 = DAT_000b048a;
  if (DAT_febec6b0 == '\x01') {
    DAT_febec694 = DAT_000b048c;
    DAT_febec692 = DAT_000b0488;
  }
  uVar5 = (uint)DAT_febec6a2;
  DAT_febec68e = (DAT_febec68e + DAT_febec692) - DAT_febec68c;
  uVar4 = (uint)DAT_febec68e;
  if (uVar5 != 0) {
    if (uVar4 == 0x80000000 && uVar5 == 0xffffffff) {
      uVar4 = 0;
    }
    else {
      uVar4 = (int)uVar4 / (int)uVar5;
    }
  }
  iVar1 = DAT_000b048a - 5;
  uVar3 = DAT_000b048a;
  if (((int)(uVar4 - iVar1) < 0 == (iVar1 < 0 && iVar1 < 0 == (int)(uVar4 - iVar1) < 0)) ||
     (uVar3 = DAT_000b0488, (int)(uVar4 - (DAT_000b0488 + 5)) < 0 || uVar4 == DAT_000b0488 + 5)) {
    uVar4 = uVar3;
    DAT_febec68e = uVar3 * DAT_febec6a2;
  }
  camry_first_quotient = uVar4;
  uVar5 = (uint)DAT_febec6a3;
  DAT_febec690 = (DAT_febec690 + DAT_febec694) - DAT_febec6a8;
  uVar4 = (uint)DAT_febec690;
  if (uVar5 != 0) {
    if (uVar4 == 0x80000000 && uVar5 == 0xffffffff) {
      uVar4 = 0;
    }
    else {
      uVar4 = (int)uVar4 / (int)uVar5;
    }
  }
  iVar1 = DAT_000b048c - 5;
  uVar3 = DAT_000b048c;
  if (((int)(uVar4 - iVar1) < 0 == (iVar1 < 0 && iVar1 < 0 == (int)(uVar4 - iVar1) < 0)) ||
     (uVar3 = DAT_000b049a, (int)(uVar4 - (DAT_000b049a + 5)) < 0 || uVar4 == DAT_000b049a + 5)) {
    uVar4 = uVar3;
    DAT_febec690 = uVar3 * DAT_febec6a3;
  }
  DAT_febec6a4 = DAT_febec6a6;
  DAT_febec6a6 = DAT_febec6af;
  return store_c68c_c6a8_with_ones_complements_ca312(uVar4,camry_first_quotient);
}

void repair_c68e_c690_filter_residuals_ca8e0(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  uint32_t puVar4;
  ushort uVar5;
  
  puVar4 = 0xfebeb800u;
  uVar5 = 0;
  iVar1 = (uint)DAT_febec68e - (uint)DAT_febec68c * (uint)DAT_febec6a2;
  iVar2 = (uint)DAT_febec6a2 * (uint)DAT_000b048e;
  iVar3 = -iVar2;
  if ((iVar1 + iVar2 < 0 != (iVar1 < 0 != iVar3 < 0 && iVar3 < 0 == iVar1 + iVar2 < 0) ||
       iVar1 == iVar3) || (iVar1 - iVar2 < 0 == (iVar1 < 0 && -1 < iVar1 - iVar2))) {
    uVar5 = 1;
    DAT_febec68e = DAT_febec692 * (ushort)DAT_febec6a2;
  }
  iVar1 = (uint)DAT_febec690 - (uint)DAT_febec6a8 * (uint)DAT_febec6a3;
  iVar2 = (uint)DAT_febec6a3 * (uint)DAT_000b0490;
  iVar3 = -iVar2;
  if ((iVar1 + iVar2 < 0 != (iVar1 < 0 != iVar3 < 0 && iVar3 < 0 == iVar1 + iVar2 < 0) ||
       iVar1 == iVar3) || (iVar1 - iVar2 < 0 == (iVar1 < 0 && -1 < iVar1 - iVar2))) {
    uVar5 = uVar5 | 2;
    DAT_febec690 = DAT_febec694 * (ushort)DAT_febec6a3;
  }
  if (uVar5 != 0) {
    puVar4 = 0xfebeb800u;
    store_c68c_c6a8_with_ones_complements_ca312((uVar5 & 2) ? DAT_febec694 : DAT_febec6a8,(uVar5 & 1) ? DAT_febec692 : DAT_febec68c);
  }
  (*((ushort *)camry_host_ptr((uint32_t)(puVar4 + 0xe9a)))) = uVar5;
  (*((ushort *)camry_host_ptr((uint32_t)(puVar4 + 0xe9c)))) = (*((ushort *)camry_host_ptr((uint32_t)(puVar4 + 0xe9c)))) | uVar5;
  return;
}

undefined4 initialize_c6b8_fixed_point_control_state_caaa2(void)

{
  uint32_t puVar1;
  undefined4 uVar2;
  uint32_t puVar3;
  
  puVar1 = 0xfebeb800u;
  DAT_febec6da = 0;
  DAT_febec724 = 0;
  DAT_febec725 = 0;
  DAT_febec6fe = 0;
  DAT_febec6e2 = 0;
  DAT_febec712 = 0;
  DAT_febec6ff = 5;
  DAT_febec6e4 = 0;
  DAT_febec714 = 0;
  DAT_febec6d8 = (undefined2)((((int)(int16_t)DAT_febeae90) * 0x27) / 0x400);
  DAT_febec6e8 = 0;
  DAT_febec6c4 = 0;
  DAT_febec716 = 0;
  DAT_febec6cc = 0;
  DAT_febec718 = 0;
  DAT_febec6ea = 0;
  puVar3 = ((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xb145cu + (uint32_t)(DAT_febeac3c & 1) * 4u))))));
  DAT_febec6c8 = 0;
  DAT_febec708 = 0;
  DAT_febec701 = 0;
  DAT_febec6f6 = (*((volatile uint16_t *)camry_host_ptr((uint32_t)(puVar3 + 0x16))));
  DAT_febec71a = 0;
  DAT_febec71c = 0;
  DAT_febec70c = 0;
  DAT_febec6d4 = (*((volatile uint32_t *)camry_host_ptr((uint32_t)(puVar3 + 0x28))));
  DAT_febec6f0 = 0;
  DAT_febec6f2 = 0;
  DAT_febec6f4 = 0;
  DAT_febec6f8 = (*((volatile uint16_t *)camry_host_ptr((uint32_t)(puVar3 + 4))));
  DAT_febec6c0 = 0;
  DAT_febec6fa = (*((volatile uint16_t *)camry_host_ptr((uint32_t)(puVar3 + 10))));
  DAT_febec6fc = (*((volatile uint16_t *)camry_host_ptr((uint32_t)(puVar3 + 0x10))));
  DAT_febec6dc = DAT_febec6d8;
  DAT_febec6de = DAT_febec6d8;
  DAT_febec6e0 = DAT_febec6d8;
  DAT_febec710 = DAT_febec6d8;
  uVar2 = raise_priority_mask_and_return_previous_d1da0(0xffc0);
  (*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + 0xebc)))) = 0;
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + 0xeee)))) = 0x569a;
  (*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + 0xed0)))) = 0x15a6800;
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + 0xee6)))) = 0;
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + 0xf1e)))) = 0;
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + 0xf20)))) = 0;
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + 0xf22)))) = 0;
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + 0xeec)))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0xf03))))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0xf04))))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0xf00))))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0xf02))))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0xf26))))) = (char)(*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + 0xeba))));
  restore_priority_mask_preserving_interrupt_enable_d1dc6(uVar2);
  return uVar2;
}

void step_c710_c714_error_filter_and_integrator_caebc(void)

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
  sVar4 = abs_s16_wrapping(((int)(int16_t)DAT_febec6d8));
  iVar5 = (int)sVar4;
  sVar4 = abs_s16_wrapping((*((short *)camry_host_ptr((uint32_t)(puVar3 + 0xedc)))));
  iVar6 = (int)sVar4;
  iVar8 = (int)DAT_000b04a4;
  iVar2 = (int)(*((short *)camry_host_ptr((uint32_t)(puVar3 + 0xf10)))) - (int)(*((short *)camry_host_ptr((uint32_t)(puVar3 + 0xf14))));
  iVar10 = iVar8;
  if ((iVar2 - iVar8 < 0 != (iVar2 < 0 != iVar8 < 0 && iVar8 < 0 == iVar2 - iVar8 < 0) ||
       iVar2 == iVar8) &&
     (iVar10 = -iVar8,
     iVar2 + iVar8 < 0 == (iVar2 < 0 != iVar10 < 0 && iVar10 < 0 == iVar2 + iVar8 < 0) &&
     iVar2 != iVar10)) {
    iVar10 = iVar2;
  }
  sVar4 = (*((short *)camry_host_ptr((uint32_t)(puVar3 + 0xf16))));
  (*((short *)camry_host_ptr((uint32_t)(puVar3 + 0xee8)))) = (short)iVar10;
  (*((short *)camry_host_ptr((uint32_t)(puVar3 + 0xf18)))) = sVar4;
  iVar2 = (*((int *)camry_host_ptr((uint32_t)(puVar3 + 0xec4)))) + ((int)(short)iVar10 - (*((int *)camry_host_ptr((uint32_t)(puVar3 + 0xecc)))));
  (*((int *)camry_host_ptr((uint32_t)(puVar3 + 0xec4)))) = iVar2;
  iVar10 = (int)DAT_000b04a6;
  if (iVar10 != 0) {
    if (iVar2 == -0x80000000 && iVar10 == -1) {
      iVar2 = -0x80000000;
    }
    else {
      iVar2 = (int)iVar2 / (int)iVar10;
    }
  }
  (*((int *)camry_host_ptr((uint32_t)(puVar3 + 0xecc)))) = iVar2;
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
  (*((short *)camry_host_ptr((uint32_t)(puVar3 + 0xf16)))) = sVar7;
  iVar2 = (int)(((sVar4 + iVar10) * (int)(*((short *)camry_host_ptr((uint32_t)(puVar3 + 0xef6)))))) / (int)0x80;
  if (iVar2 + -0x7fff < 0 == (iVar2 < 0 && -1 < iVar2 + -0x7fff) && iVar2 != 0x7fff) {
    iVar10 = 0x7fff;
  }
  else {
    iVar10 = (int)(short)iVar2;
    if (iVar2 + 0x7fff < 0 != (-1 < iVar2 && iVar2 + 0x7fff < 0)) {
      iVar10 = -0x7fff;
    }
  }
  (*((short *)camry_host_ptr((uint32_t)(puVar3 + 0xeea)))) = (short)iVar10;
  if ((((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(0xf00))))) != '\x02') || (iVar10 < 0)) && (((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(0xf00))))) != '\x01' || (-1 < iVar10)))) {
    (*((int *)camry_host_ptr((uint32_t)(puVar3 + 0xec8)))) = (*((int *)camry_host_ptr((uint32_t)(puVar3 + 0xec8)))) + iVar10;
  }
  iVar8 = (*((int *)camry_host_ptr((uint32_t)(puVar3 + 0xec8))));
  iVar10 = (*((int *)camry_host_ptr((uint32_t)(puVar3 + 0xed4))));
  iVar2 = iVar10;
  if ((iVar8 - iVar10 < 0 != (iVar8 < 0 != iVar10 < 0 && iVar10 < 0 == iVar8 - iVar10 < 0) ||
       iVar8 == iVar10) &&
     (iVar2 = -iVar10,
     iVar8 + iVar10 < 0 == (iVar8 < 0 != iVar2 < 0 && iVar2 < 0 == iVar8 + iVar10 < 0) &&
     iVar8 != iVar2)) {
    iVar2 = iVar8;
  }
  (*((int *)camry_host_ptr((uint32_t)(puVar3 + 0xec8)))) = iVar2;
  iVar10 = (*((int *)camry_host_ptr((uint32_t)(puVar3 + 0xf08))));
  (*((int *)camry_host_ptr((uint32_t)(puVar3 + 0xf08)))) = iVar2;
  uVar1 = 0;
  (*((int *)camry_host_ptr((uint32_t)(puVar3 + 0xf0c)))) = iVar10;
  if ((iVar5 - iVar6 < 0 == (iVar5 < 0 != iVar6 < 0 && iVar6 < 0 == iVar5 - iVar6 < 0) &&
       iVar5 != iVar6) ||
     (uVar1 = 1, iVar5 - iVar6 < 0 != (iVar5 < 0 != iVar6 < 0 && iVar6 < 0 == iVar5 - iVar6 < 0))) {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(0xf01))))) = uVar1;
  }
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(0xf01))))) == '\0') {
    iVar2 = (int)(*((short *)camry_host_ptr((uint32_t)(puVar3 + 0xef8)))) * (int)sVar7;
    if (iVar2 + -0x7fff < 0 != (iVar2 < 0 && -1 < iVar2 + -0x7fff) || iVar2 == 0x7fff) {
LAB_000cafee:
      if (iVar2 + 0x7fff < 0 == (-1 < iVar2 && iVar2 + 0x7fff < 0)) {
        uVar9 = (undefined2)iVar2;
      }
      else {
        uVar9 = 0x8001;
      }
      goto LAB_000caffa;
    }
  }
  else {
    iVar2 = (int)(*((short *)camry_host_ptr((uint32_t)(puVar3 + 0xefa)))) * (int)sVar7;
    if (iVar2 + -0x7fff < 0 != (iVar2 < 0 && -1 < iVar2 + -0x7fff) || iVar2 == 0x7fff)
    goto LAB_000cafee;
  }
  uVar9 = 0x7fff;
LAB_000caffa:
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + 0xf1a)))) = uVar9;
  iVar2 = (int)(((int)DAT_000b04a8 * (int)(*((short *)camry_host_ptr((uint32_t)(puVar3 + 0xf10)))))) / (int)0x80;
  if (iVar2 + -0x7fff < 0 == (iVar2 < 0 && -1 < iVar2 + -0x7fff) && iVar2 != 0x7fff) {
    uVar9 = 0x7fff;
  }
  else if (iVar2 + 0x7fff < 0 == (-1 < iVar2 && iVar2 + 0x7fff < 0)) {
    uVar9 = (undefined2)iVar2;
  }
  else {
    uVar9 = 0x8001;
  }
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + 0xf1c)))) = uVar9;
  return;
}
