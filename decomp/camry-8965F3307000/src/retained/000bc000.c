#include "common.h"

void return_only_stub_bc0f6(void)

{
  return;
}

void reset_owner3_signal_qualification(void)

{
  DAT_febebda8 = 0;
  DAT_febebda9 = 0;
  DAT_febebdac = DAT_000af110;
  DAT_febebdae = DAT_000af112;
  return;
}

void qualify_owner3_shutdown_signal(void)

{
  if ((DAT_febeb1a7 == 'Z') &&
     (((DAT_febeb20e == '\0' || (DAT_febeb20e == '3')) && (DAT_febeb1bc == '\0')))) {
    DAT_febebda9 = 1;
    if (DAT_febebda8 < 2) {
      if (DAT_febebda8 == 0) {
        if ((DAT_febeb084 < DAT_000af114) && (DAT_febebdaa == '\0')) {
          if (DAT_febebdac == 0) {
            DAT_febebda8 = 1;
            DAT_febebda9 = 1;
            DAT_febebdae = DAT_000af112;
            return;
          }
          DAT_febebda9 = 1;
          DAT_febebdac = DAT_febebdac + -1;
          return;
        }
      }
      else {
        if (DAT_febeb084 <= DAT_000af116) {
          DAT_febebda9 = 1;
          DAT_febebdae = DAT_000af112;
          return;
        }
        if (DAT_febebdae != 0) {
          DAT_febebda9 = 1;
          DAT_febebdae = DAT_febebdae + -1;
          return;
        }
      }
      DAT_febebda8 = 0;
      DAT_febebdac = DAT_000af110;
    }
  }
  else {
    DAT_febebda8 = 0;
    DAT_febebda9 = 0;
    DAT_febebdac = DAT_000af110;
    DAT_febebdae = DAT_000af112;
  }
  return;
}

void return_only_stub_bc19c(void)

{
  return;
}

void reset_owner2_deficit_request(void)

{
  DAT_febebdb0 = 0;
  DAT_febebdb1 = 0;
  DAT_febebdb4 = 0x569a;
  DAT_febebdb6 = 0;
  DAT_febebdb8 = 0;
  DAT_febebdba = 0;
  DAT_febebdbc = 0x569a;
  DAT_febebdbe = DAT_000af144;
  DAT_febebdc0 = DAT_000af13e;
  DAT_febebdc2 = DAT_000af140;
  DAT_febebdc8 = 0x569a;
  DAT_febebdd0 = 0;
  DAT_febebdc4 = DAT_000af142;
  DAT_febebdcc = 0x569a0000;
  DAT_febebdd4 = 0;
  DAT_febebdd8 = 0;
  return;
}

void publish_owner2_deficit_limit_request(void)

{
  uint8_t stack_record_5e[94];
  char cVar1;
  char cVar2;
  char cVar3;
  short sVar4;
  uint32_t puVar5;
  uint uVar6;
  int iVar7;
  short sVar8;
  int iVar9;
  short sVar10;
  short sVar11;
  int iVar12;
  short sVar13;
  short sVar14;
  int iVar15;
  int iVar16;
  char cStack_61;
  char cStack_60;
  
  iVar16 = DAT_febebdcc;
  sVar11 = DAT_febebdbe;
  cVar3 = DAT_febebdb0;
  cVar2 = DAT_febeb1d1;
  cVar1 = DAT_febeb1a7;
  puVar5 = 0xfebeb800u;
  (*((int16_t *)(stack_record_5e + 40))) = DAT_000af134;
  (*((int16_t *)(stack_record_5e + 46))) = ((int)(int16_t)DAT_febeaf80);
  (*((int16_t *)(stack_record_5e + 48))) = ((int)(int16_t)DAT_febeaf82);
  (*((int16_t *)(stack_record_5e + 14))) = ((int)(int16_t)DAT_febeafa4);
  cStack_61 = DAT_febebdb1;
  (*((int16_t *)(stack_record_5e + 38))) = DAT_000af132;
  iVar15 = (int)((int)(int16_t)DAT_febebdbc);
  (*((int32_t *)(stack_record_5e + 26))) = DAT_febebdd8;
  uVar6 = (uint)DAT_febeee20;
  iVar9 = (int)((int)(int16_t)DAT_febebdba);
  (*((int32_t *)(stack_record_5e + 34))) = DAT_febebdc8;
  iVar12 = (int)((int)(int16_t)DAT_febebdb4);
  cStack_60 = DAT_febebdb0;
  (*((int16_t *)(stack_record_5e + 16))) = DAT_febebdc4;
  sVar13 = DAT_000af13e;
  sVar14 = DAT_000af140;
  if ((DAT_febeb1a7 == 'Z') && (DAT_febebcaa != 'Z')) {
    if ((uVar6 < DAT_000af11a) && (DAT_febebdb2 == '\0')) {
      if (DAT_febebdc0 == 0) {
        cStack_61 = '\x01';
        sVar13 = 0;
      }
      else {
        sVar13 = DAT_febebdc0 + -1;
      }
    }
    else if ((DAT_febebdb1 == '\x01') && (DAT_000af11c < uVar6)) {
      if (DAT_febebdc2 == 0) {
        cStack_61 = '\0';
        sVar14 = 0;
      }
      else {
        sVar14 = DAT_febebdc2 + -1;
      }
    }
    iVar7 = DAT_000af118 - uVar6;
    if (iVar7 + 0x7fff < 0 == (-1 < iVar7 && iVar7 + 0x7fff < 0) && iVar7 != -0x7fff) {
      if (iVar7 + -0x7fff < 0 == (iVar7 < 0 && -1 < iVar7 + -0x7fff) && iVar7 != 0x7fff) {
        iVar7 = 0x7fff;
      }
      (*((int16_t *)(stack_record_5e + 32))) = (short)iVar7;
    }
    else {
      (*((int16_t *)(stack_record_5e + 32))) = -0x7fff;
    }
    (*((int32_t *)(stack_record_5e + 18))) = (uint)DAT_000af138 * 10;
    if ((*((int32_t *)(stack_record_5e + 18))) - 1U < 0xffff) {
      iVar7 = ((int)(int16_t)DAT_febebdb6) * (*((int32_t *)(stack_record_5e + 18)));
      (*((int32_t *)(stack_record_5e + 18))) = (*((int16_t *)(stack_record_5e + 32))) * (*((int32_t *)(stack_record_5e + 18)));
    }
    else {
      iVar7 = (int)((int)(int16_t)DAT_febebdb6) << 0x10;
      (*((int32_t *)(stack_record_5e + 18))) = (int)(*((int16_t *)(stack_record_5e + 32))) << 0x10;
    }
    (*((int32_t *)(stack_record_5e + 18))) = (DAT_febebdd0 - iVar7) + (*((int32_t *)(stack_record_5e + 18)));
    (*((int32_t *)(stack_record_5e + 10))) = (uint)DAT_000af13a * 10;
    sVar10 = (short)((*((int32_t *)(stack_record_5e + 18))) / 0x10000);
    (*((uint32_t *)(stack_record_5e + 42))) = (*((int32_t *)(stack_record_5e + 10))) - 1;
    if ((*((uint32_t *)(stack_record_5e + 42))) < 0xffff) {
      iVar7 = ((int)(int16_t)DAT_febebdb8) * (*((int32_t *)(stack_record_5e + 10)));
      (*((int32_t *)(stack_record_5e + 22))) = (*((int16_t *)(stack_record_5e + 32))) * (*((int32_t *)(stack_record_5e + 10)));
    }
    else {
      iVar7 = (int)((int)(int16_t)DAT_febebdb8) << 0x10;
      (*((int32_t *)(stack_record_5e + 22))) = (int)(*((int16_t *)(stack_record_5e + 32))) << 0x10;
    }
    (*((int32_t *)(stack_record_5e + 22))) = (DAT_febebdd4 - iVar7) + (*((int32_t *)(stack_record_5e + 22)));
    (*((int16_t *)(stack_record_5e + 30))) = (short)((*((int32_t *)(stack_record_5e + 22))) / 0x10000);
    puVar5 = 0xfebeb800u;
    store_symmetric_saturated_signed16_difference_d2388((int)(*((int16_t *)(stack_record_5e + 32))),(int)(*((int16_t *)(stack_record_5e + 30))),((int16_t *)(stack_record_5e)));
    if ((*((uint32_t *)(stack_record_5e + 42))) < 0xffff) {
      iVar9 = iVar9 * (*((int32_t *)(stack_record_5e + 10)));
      iVar7 = (*((int16_t *)(stack_record_5e + 0))) * (*((int32_t *)(stack_record_5e + 10)));
    }
    else {
      iVar9 = iVar9 << 0x10;
      iVar7 = (int)(*((int16_t *)(stack_record_5e + 0))) << 0x10;
    }
    (*((int32_t *)(stack_record_5e + 26))) = ((*((int32_t *)(stack_record_5e + 26))) - iVar9) + iVar7;
    sVar8 = (short)((*((int32_t *)(stack_record_5e + 26))) / 0x10000);
    iVar9 = (int)sVar8;
    if (cStack_61 == '\x01') {
      if (cVar3 == '\0') {
        store_saturated_signed16_absolute_d1178((int)(*((int16_t *)(stack_record_5e + 48))),((int16_t *)((stack_record_5e + 6))));
        store_saturated_signed16_absolute_d1178((int)(*((int16_t *)(stack_record_5e + 46))),((int16_t *)((stack_record_5e + 8))));
        iVar16 = (int)(*((int16_t *)(stack_record_5e + 8)));
        iVar15 = (int)(*((int16_t *)(stack_record_5e + 6)));
        cStack_60 = '\x01';
        if (iVar16 - iVar15 < 0 != (iVar16 < 0 != iVar15 < 0 && iVar15 < 0 == iVar16 - iVar15 < 0))
        {
          iVar15 = iVar16;
        }
        iVar16 = iVar15 << 0x10;
      }
      sVar11 = DAT_000af120;
      if (cVar2 != 'Z') {
        sVar11 = DAT_000af11e;
      }
      iVar12 = (int)sVar11;
      if (iVar15 - iVar12 < 0 == (iVar15 < 0 != iVar12 < 0 && iVar12 < 0 == iVar15 - iVar12 < 0) &&
          iVar15 != iVar12) {
        iVar7 = (uint)DAT_000af13c * 10;
        if (iVar7 - 1U < 0xffff) {
          iVar15 = iVar15 * iVar7;
          iVar12 = iVar12 * iVar7;
        }
        else {
          iVar15 = iVar15 << 0x10;
          iVar12 = iVar12 << 0x10;
        }
        iVar16 = (iVar16 - iVar15) + iVar12;
        iVar15 = (int)(short)(iVar16 / 0x10000);
      }
      iVar12 = 0;
      if (-1 < sVar10) {
        iVar12 = ((int)DAT_000af122 * (int)sVar10) / 8;
      }
      iVar7 = iVar15 - iVar12;
      if (iVar15 - iVar12 < 0) {
        iVar7 = 0;
      }
      if (iVar7 - (*((int32_t *)(stack_record_5e + 34))) < 0 !=
          (iVar7 < 0 != (*((int32_t *)(stack_record_5e + 34))) < 0 && (*((int32_t *)(stack_record_5e + 34))) < 0 == iVar7 - (*((int32_t *)(stack_record_5e + 34))) < 0)) {
        (*((int32_t *)(stack_record_5e + 34))) = iVar7;
      }
      if ((*((int16_t *)(stack_record_5e + 32))) < 0) {
        if (cVar2 == 'Z') {
          iVar12 = (int)DAT_000af12a;
        }
        else {
          iVar12 = (int)DAT_000af128;
        }
      }
      else if (cVar2 == 'Z') {
        iVar12 = (int)DAT_000af126;
      }
      else {
        iVar12 = (int)DAT_000af124;
      }
      iVar12 = ((*((int16_t *)(stack_record_5e + 32))) * iVar12) / 8;
      iVar7 = (int)DAT_000af12c;
      if (iVar9 - iVar7 < 0 == (iVar9 < 0 != iVar7 < 0 && iVar7 < 0 == iVar9 - iVar7 < 0)) {
        sVar11 = DAT_000af130;
        if (cVar2 != 'Z') {
          sVar11 = DAT_000af12e;
        }
        iVar9 = (iVar9 * sVar11) / 8;
      }
      else {
        iVar9 = 0;
      }
      iVar7 = (*((int32_t *)(stack_record_5e + 34))) - iVar12;
      if ((*((int32_t *)(stack_record_5e + 34))) - iVar12 < 0) {
        if ((iVar9 < 0) ||
           (iVar12 = (iVar7 + 0x7fffffff) - iVar9,
           iVar12 < 0 == (iVar7 + 0x7fffffff < 0 != iVar9 < 0 && iVar9 < 0 == iVar12 < 0)))
        goto LAB_000bc4da;
        iVar7 = -0x7fffffff;
      }
      else if ((iVar9 < 0) &&
              (iVar12 = -(0x7fffffff - iVar7),
              iVar12 - iVar9 < 0 == (iVar12 < 0 != iVar9 < 0 && iVar9 < 0 == iVar12 - iVar9 < 0) &&
              iVar12 != iVar9)) {
        iVar7 = 0x7fffffff;
      }
      else {
LAB_000bc4da:
        iVar7 = iVar7 - iVar9;
      }
      store_signed32_clamped_between_upper_and_lower_d1cf6(iVar7,(int)(*((int16_t *)(stack_record_5e + 38))),(int)(*((int16_t *)(stack_record_5e + 40))),((int16_t *)((stack_record_5e + 2))));
      iVar9 = (int)((int16_t *)((stack_record_5e + 2)))[0];
      sVar11 = DAT_000af144;
      goto LAB_000bc552;
    }
    iVar9 = (int)(*((int16_t *)(stack_record_5e + 38)));
    if (iVar12 - iVar9 < 0 != (iVar12 < 0 != iVar9 < 0 && iVar9 < 0 == iVar12 - iVar9 < 0)) {
      if (sVar11 == 0) {
        store_signed32_clamped_between_upper_and_lower_d1cf6(DAT_000af136 + iVar12,(int)(*((int16_t *)(stack_record_5e + 38))),(int)(*((int16_t *)(stack_record_5e + 40))),((int16_t *)((stack_record_5e + 2))));
        iVar9 = (int)((int16_t *)((stack_record_5e + 2)))[0];
        sVar11 = DAT_000af144;
      }
      else {
        sVar11 = sVar11 + -1;
        iVar9 = iVar12;
      }
    }
    (*((int32_t *)(stack_record_5e + 34))) = (int)(*((int16_t *)(stack_record_5e + 38)));
    iVar16 = (*((int32_t *)(stack_record_5e + 34))) << 0x10;
  }
  else {
    (*((int32_t *)(stack_record_5e + 26))) = 0;
    (*((int32_t *)(stack_record_5e + 22))) = 0;
    (*((int32_t *)(stack_record_5e + 18))) = 0;
    (*((int16_t *)(stack_record_5e + 30))) = 0;
    iVar16 = 0x569a0000;
    sVar10 = 0;
    iVar9 = 0x569a;
    cStack_61 = '\0';
    (*((int32_t *)(stack_record_5e + 34))) = 0x569a;
    sVar8 = 0;
    sVar11 = DAT_000af144;
  }
  cStack_60 = '\0';
  iVar15 = (*((int32_t *)(stack_record_5e + 34)));
LAB_000bc552:
  store_saturated_signed16_absolute_d1178((int)(*((int16_t *)(stack_record_5e + 14))),((int16_t *)((stack_record_5e + 14))));
  iVar7 = (int)DAT_000af146;
  iVar12 = (*((int16_t *)(stack_record_5e + 14))) - iVar9;
  sVar4 = DAT_000af142;
  if ((iVar7 - iVar12 < 0 != (iVar7 < 0 != iVar12 < 0 && iVar12 < 0 == iVar7 - iVar12 < 0) ||
       iVar7 == iVar12) && (sVar4 = DAT_000af142, cVar1 == 'Z')) {
    if ((*((int16_t *)(stack_record_5e + 16))) == 0) {
      thunk_increment_indexed_u16_counter_once_until_rearmed_545de(9);
      thunk_gate_indexed_event_payload_during_diagnostic_clears_51cf6(3,10);
      sVar4 = (*((int16_t *)(stack_record_5e + 16)));
    }
    else {
      sVar4 = (*((int16_t *)(stack_record_5e + 16))) + -1;
    }
  }
  (*((int16_t *)(stack_record_5e + 16))) = sVar4;
  set_current_limit_request(2,(ushort)iVar9);
  (*((short *)camry_host_ptr((uint32_t)(puVar5 + 0x5ba)))) = sVar8;
  (*((short *)camry_host_ptr((uint32_t)(puVar5 + 0x5c0)))) = sVar13;
  (*((short *)camry_host_ptr((uint32_t)(puVar5 + 0x5c2)))) = sVar14;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(0x5b1))))) = cStack_61;
  (*((short *)camry_host_ptr((uint32_t)(puVar5 + 0x5bc)))) = (short)iVar15;
  (*((int *)camry_host_ptr((uint32_t)(puVar5 + 0x5cc)))) = iVar16;
  (*((short *)camry_host_ptr((uint32_t)(puVar5 + 0x5b6)))) = sVar10;
  (*((short *)camry_host_ptr((uint32_t)(puVar5 + 0x5b8)))) = (*((int16_t *)(stack_record_5e + 30)));
  (*((int *)camry_host_ptr((uint32_t)(puVar5 + 0x5d0)))) = (*((int32_t *)(stack_record_5e + 18)));
  (*((int *)camry_host_ptr((uint32_t)(puVar5 + 0x5d4)))) = (*((int32_t *)(stack_record_5e + 22)));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(0x5b0))))) = cStack_60;
  (*((int *)camry_host_ptr((uint32_t)(puVar5 + 0x5d8)))) = (*((int32_t *)(stack_record_5e + 26)));
  (*((int *)camry_host_ptr((uint32_t)(puVar5 + 0x5c8)))) = (*((int32_t *)(stack_record_5e + 34)));
  (*((ushort *)camry_host_ptr((uint32_t)(puVar5 + 0x5b4)))) = (ushort)iVar9;
  (*((short *)camry_host_ptr((uint32_t)(puVar5 + 0x5be)))) = sVar11;
  (*((short *)camry_host_ptr((uint32_t)(puVar5 + 0x5c4)))) = (*((int16_t *)(stack_record_5e + 16)));
  return;
}

void return_only_stub_bc5fa(void)

{
  return;
}

void return_only_stub_bc5fc(void)

{
  return;
}

void latch_bddc_after_any_selected_failure_flag_bc5fe(void)

{
  char cVar1;
  uint32_t puVar2;
  puVar2 = 0xfebeb800u;
  cVar1 = DAT_febebddc;
  if ((DAT_febebddc == '\0') &&
     ((((DAT_febebd9c == '\x01' || (DAT_febef38b == 'Z')) || (DAT_febebded == '\x01')) ||
      (DAT_febebde4 == '\x01')))) {
    puVar2 = 0xfebeb800u;
    thunk_increment_indexed_u16_counter_once_until_rearmed_545de(0);
    thunk_gate_indexed_event_payload_during_diagnostic_clears_51cf6(5,10);
    cVar1 = 'Z';
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(0x5dc))))) = cVar1;
  return;
}

void return_only_stub_bc646(void)

{
  return;
}

void fill_constant_block_bc648(void)

{
  DAT_febebde0 = 0;
  DAT_febebde1 = 0;
  DAT_febebde2 = 0;
  DAT_febebde3 = 0;
  DAT_febebde4 = 0;
  DAT_febebde6 = 0;
  DAT_febebde8 = 0;
  DAT_febebdea = 0;
  return;
}

void debounce_b084_threshold_window_and_toggle_request_14_bc65e(void)

{
  ushort uVar1;
  bool bVar2;
  uint32_t puVar3;
  uint32_t puVar4;
  char cVar5;
  char cVar6;
  char cVar7;
  ushort uVar8;
  ushort uVar9;
  ushort uVar10;
  char cVar11;
  
  puVar4 = 0xfebeb800u;
  puVar3 = (0xfebeb800u);
  if ((((((DAT_febeb065 != '\0') || (DAT_febef0b2 != '\0')) || (DAT_febeb1a7 != 'Z')) ||
       ((DAT_febeb20e != '\0' && (DAT_febeb20e != '3')))) ||
      ((DAT_febeb1bc == 'Z' || ((DAT_febeb084 < DAT_000af14a || (DAT_000af148 < DAT_febeb084))))))
     || (DAT_febeb30c == 0)) {
    cVar7 = '\0';
    cVar6 = '\0';
    cVar5 = '\0';
    bVar2 = false;
    cVar11 = '\0';
    uVar10 = 0;
    uVar9 = 0;
    uVar8 = 0;
    goto LAB_000bc7a4;
  }
  uVar10 = DAT_000af152;
  uVar1 = DAT_000af14e;
  if (DAT_febeb30c == -0x55aaaa56) {
    uVar10 = DAT_000af150;
    uVar1 = DAT_000af14c;
  }
  if (DAT_febebde3 == 'Z') {
    uVar9 = DAT_febebde8;
    if (DAT_febebde8 < DAT_000af156) {
      uVar9 = DAT_febebde8 + 1;
      goto LAB_000bc6ee;
    }
LAB_000bc6f4:
    cVar5 = 'Z';
  }
  else {
    uVar9 = 0;
LAB_000bc6ee:
    if (DAT_000af156 <= uVar9) goto LAB_000bc6f4;
    cVar5 = '\0';
  }
  cVar11 = '\0';
  uVar8 = DAT_febebdea;
  cVar7 = DAT_febebde0;
  cVar6 = cVar11;
  if (uVar1 < DAT_febeb084) {
    if ((uVar10 <= DAT_febeb084) || (cVar5 == 'Z')) {
      uVar8 = 0;
      cVar7 = cVar11;
    }
LAB_000bc724:
    if ((DAT_febebde1 != 'Z') || (cVar7 != '\0')) goto LAB_000bc712;
    uVar10 = DAT_febebde6;
    if (DAT_febebde6 <= DAT_000af154) {
      uVar10 = DAT_febebde6 + 1;
      goto LAB_000bc738;
    }
  }
  else {
    if ((DAT_febebdea < DAT_000af158) && (uVar8 = DAT_febebdea + 1, uVar8 < DAT_000af158))
    goto LAB_000bc724;
    cVar7 = 'Z';
LAB_000bc712:
    uVar10 = 0;
LAB_000bc738:
    if ((uVar10 <= DAT_000af154) && (cVar5 != 'Z')) {
      if (cVar7 == 'Z') {
        cVar6 = 'Z';
      }
      else {
        cVar6 = DAT_febebde1;
        if (DAT_febebde1 != 'Z') goto LAB_000bc762;
      }
      if (cVar5 == '\0') {
        cVar11 = cVar6;
      }
    }
  }
LAB_000bc762:
  puVar3 = (0xfebeb800u);
  if (DAT_febebde3 == '\0') {
    if (cVar11 == 'Z') {
      thunk_increment_indexed_u16_counter_once_until_rearmed_545de(0xe);
      thunk_gate_indexed_event_payload_during_diagnostic_clears_51cf6(4,0x32);
      puVar3 = ((uint32_t)(puVar4));
    }
  }
  else if (cVar11 != 'Z') {
    puVar3 = (0xfebeb800u);
    thunk_clear_indexed_counter_rearm_byte_54724(0xe);
  }
  bVar2 = cVar11 == 'Z';
LAB_000bc7a4:
  (*((volatile undefined *)camry_host_ptr((uint32_t)(0xfebeb800u + (uint32_t)(0x5e0) * 1u)))) = cVar7;
  (*((volatile undefined *)camry_host_ptr((uint32_t)(0xfebeb800u + (uint32_t)(0x5e1) * 1u)))) = cVar6;
  (*((volatile undefined *)camry_host_ptr((uint32_t)(0xfebeb800u + (uint32_t)(0x5e2) * 1u)))) = cVar5;
  (*((volatile undefined *)camry_host_ptr((uint32_t)(0xfebeb800u + (uint32_t)(0x5e3) * 1u)))) = cVar11;
  *(ushort *)(((undefined *)camry_host_ptr((uint32_t)(0xfebeb800u + (uint32_t)(0x5e6) * 1u)))) = uVar10;
  *(ushort *)(((undefined *)camry_host_ptr((uint32_t)(0xfebeb800u + (uint32_t)(0x5e8) * 1u)))) = uVar9;
  *(ushort *)(((undefined *)camry_host_ptr((uint32_t)(0xfebeb800u + (uint32_t)(0x5ea) * 1u)))) = uVar8;
  (*((volatile undefined *)camry_host_ptr((uint32_t)(0xfebeb800u + (uint32_t)(0x5e4) * 1u)))) = bVar2;
  return;
}

void return_only_stub_bc7bc(void)

{
  return;
}

void fill_constant_block_bc7be(void)

{
  DAT_febebdec = 0;
  DAT_febebded = 0;
  DAT_febebdf0 = 0;
  DAT_febebdf2 = 0;
  DAT_febebdf4 = 0;
  return;
}

void debounce_event_9a_failure_and_recovery_bc7ce(void)

{
  uint8_t stack_record_2c[44];
  ushort uVar1;
  char cVar2;
  int iVar3;
  uint32_t puVar4;
  uint32_t puVar5;
  int iVar6;
  undefined1 uVar7;
  int iVar8;
  char cVar9;
  ushort uVar10;
  ushort uVar11;
  ushort uVar12;
  
  uVar12 = DAT_febebdf4;
  uVar10 = DAT_febebdf2;
  cVar2 = DAT_febebdee;
  uVar1 = DAT_febeb084;
  puVar4 = 0xfebeb800u;
  puVar5 = (0xfebeb800u);
  iVar8 = (int)((int)(int16_t)DAT_febeb00a);
  uVar11 = DAT_febebdf0;
  cVar9 = DAT_febebded;
  if ((DAT_febeb1a7 == 'Z') && ((DAT_febeb20e == '\0' || (DAT_febeb20e == '3')))) {
    if (DAT_febeb1bc != 'Z') {
      iVar3 = (int)DAT_000af164;
      uVar7 = 1;
      puVar5 = (0xfebeb800u);
      if ((iVar8 - iVar3 < 0 == (iVar8 < 0 != iVar3 < 0 && iVar3 < 0 == iVar8 - iVar3 < 0)) ||
         (DAT_febebee2 < DAT_000af15c)) {
        uVar11 = 0;
      }
      else if (DAT_febebded == '\0') {
        if (DAT_febebdf0 < DAT_000af15e) {
          uVar11 = DAT_febebdf0 + 1;
        }
        else {
          report_diagnostic_event_failure(0x9a,100);
          thunk_increment_indexed_u16_counter_once_until_rearmed_545de(0xd);
          uVar11 = 0;
          puVar5 = ((uint32_t)(puVar4));
          cVar9 = '\x01';
        }
      }
      store_saturated_signed16_absolute_d1178((int)*(short *)(((undefined *)camry_host_ptr((uint32_t)(0xfebeb800u + (uint32_t)(-0x820) * 1u)))),((int16_t *)(stack_record_2c)));
      store_saturated_signed16_absolute_d1178((int)*(short *)(((undefined *)camry_host_ptr((uint32_t)(0xfebeb800u + (uint32_t)(-0x824) * 1u)))),((int16_t *)((stack_record_2c + 2))));
      if (uVar1 < DAT_000af16a) {
        iVar3 = (int)DAT_000af166;
        iVar6 = (int)(*((int16_t *)(stack_record_2c + 0)));
        if (iVar6 - iVar3 < 0 == (iVar6 < 0 != iVar3 < 0 && iVar3 < 0 == iVar6 - iVar3 < 0) &&
            iVar6 != iVar3) goto LAB_000bc8b2;
        iVar3 = (int)DAT_000af16e;
        iVar6 = (int)(*((int16_t *)(stack_record_2c + 2)));
        if ((iVar6 - iVar3 < 0 == (iVar6 < 0 != iVar3 < 0 && iVar3 < 0 == iVar6 - iVar3 < 0) &&
             iVar6 != iVar3) || (cVar2 != '\0')) goto LAB_000bc8b2;
        if (cVar9 == '\0') {
          if (uVar10 < DAT_000af160) {
            uVar10 = uVar10 + 1;
          }
          else {
            report_diagnostic_event_failure(0x9a,100);
            cVar9 = '\x01';
            thunk_increment_indexed_u16_counter_once_until_rearmed_545de(0xd);
            uVar10 = 0;
          }
        }
      }
      else {
LAB_000bc8b2:
        uVar10 = 0;
      }
      if ((DAT_000af16c < uVar1) &&
         (iVar3 = (int)DAT_000af168,
         iVar8 - iVar3 < 0 == (iVar8 < 0 != iVar3 < 0 && iVar3 < 0 == iVar8 - iVar3 < 0))) {
        if (uVar12 < DAT_000af162) {
          uVar12 = uVar12 + 1;
        }
        else {
          report_diagnostic_event_pass(0x9a);
          cVar9 = '\0';
        }
      }
      else {
        uVar12 = 0;
      }
      goto LAB_000bc928;
    }
LAB_000bc8e6:
    if ((DAT_000af16c < DAT_febeb084) &&
       (iVar3 = (int)DAT_000af168,
       iVar8 - iVar3 < 0 == (iVar8 < 0 != iVar3 < 0 && iVar3 < 0 == iVar8 - iVar3 < 0))) {
      if (DAT_000af162 <= DAT_febebdf4) {
        puVar5 = (0xfebeb800u);
        report_diagnostic_event_pass(0x9a);
        goto LAB_000bc924;
      }
      uVar12 = DAT_febebdf4 + 1;
    }
    else {
      uVar12 = 0;
    }
  }
  else {
    if (DAT_febeb1bc == 'Z') goto LAB_000bc8e6;
    puVar5 = (0xfebeb800u);
    report_diagnostic_event_pass(0x9a);
LAB_000bc924:
    uVar12 = 0;
    uVar11 = 0;
    uVar10 = 0;
    cVar9 = '\0';
  }
  uVar7 = 0;
LAB_000bc928:
  (*((volatile undefined *)camry_host_ptr((uint32_t)(0xfebeb800u + (uint32_t)(0x5ec) * 1u)))) = uVar7;
  (*((volatile undefined *)camry_host_ptr((uint32_t)(0xfebeb800u + (uint32_t)(0x5ed) * 1u)))) = cVar9;
  *(ushort *)(((undefined *)camry_host_ptr((uint32_t)(0xfebeb800u + (uint32_t)(0x5f0) * 1u)))) = uVar11;
  *(ushort *)(((undefined *)camry_host_ptr((uint32_t)(0xfebeb800u + (uint32_t)(0x5f2) * 1u)))) = uVar10;
  *(ushort *)(((undefined *)camry_host_ptr((uint32_t)(0xfebeb800u + (uint32_t)(0x5f4) * 1u)))) = uVar12;
  return;
}

void set_byte_febebdee_bc93a(undefined1 param_1)

{
  DAT_febebdee = param_1;
  return;
}

void publish_ee14_nonzero_as_ac01_5a_bc958(void)

{
  DAT_febeac01 = 0;
  if (DAT_febeee14 != '\0') {
    DAT_febeac01 = 0x5a;
  }
  return;
}

void publish_ee03_group_inhibit_and_ee02_ready_bc96a(void)

{
  if (((((((DAT_febeee03 == '\0') && (DAT_febeee04 == '\0')) && (DAT_febeee05 == '\0')) &&
        ((DAT_febeee06 == '\0' && (DAT_febeee07 == '\0')))) &&
       (((DAT_febeee08 == '\0' && ((DAT_febeee09 == '\0' && (DAT_febeee0a == '\0')))) &&
        (DAT_febeee0b == '\0')))) &&
      (((DAT_febeee0c == '\0' && (DAT_febeee0d == '\0')) &&
       ((DAT_febeb358 == '\0' || (DAT_febeb358 == '\x02')))))) && (DAT_febef394 == -0x5aa5a55b)) {
    DAT_febeac02 = 0;
  }
  else {
    DAT_febeac02 = 0x5a;
  }
  DAT_febeac04 = DAT_febeee02 == 'Z';
  return;
}

void scale_observer_source_term(void)

{
  uint32_t puVar1;
  undefined4 local_8;
  
  puVar1 = 0xfebeb800u;
  scale_signed32_ratio_with_overflow_order_fallback_d1272(DAT_febeaf8c,0x2d,4,&local_8);
  (*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + -0xbe8)))) = local_8;
  return;
}

void copy_selected_inputs_to_ac00_snapshot_bca08(void)

{
  DAT_febeac14 = DAT_febeaf88;
  DAT_febeac00 = DAT_febeb20e;
  DAT_febeac0c = DAT_febeee1e;
  DAT_febeac03 = DAT_febeb1a7;
  DAT_febeac0e = ((int)(int16_t)DAT_febeafbc);
  DAT_febeac06 = DAT_febeee12;
  DAT_febeac10 = ((int)(int16_t)DAT_febeafa8);
  DAT_febeac07 = record8_confirmation_complete;
  DAT_febeac12 = DAT_febeb138;
  DAT_febeac20 = DAT_febebed4;
  DAT_febeac0a = DAT_febeb1ce;
  DAT_febeac0b = DAT_febeee14;
  DAT_febeac24 = DAT_febeaf8c;
  return;
}

void run_init_chain_bca62(void)

{
  publish_ee14_nonzero_as_ac01_5a_bc958();
  publish_ee03_group_inhibit_and_ee02_ready_bc96a();
  scale_observer_source_term();
  copy_selected_inputs_to_ac00_snapshot_bca08();
  call_observer_and_waveform_publication_slice_d1118();
  return;
}

void call_ff100_with_second_argument_ten_bca7e(undefined1 param_1)

{
  thunk_gate_indexed_event_payload_during_diagnostic_clears_51cf6(param_1,10);
  return;
}

void derive_scaled_and_masked_ac28_snapshot_fields_bcaa6(void)

{
  uint8_t stack_record_34[52];
  char cVar1;
  undefined1 uVar2;
  ushort uVar3;
  char cVar4;
  char cVar5;
  char cVar6;
  uint uVar7;
  uint32_t puVar8;
  undefined1 uVar9;
  undefined1 uVar10;
  undefined1 uVar11;
  undefined2 uVar12;
  
  cVar5 = DAT_febebe20;
  cVar4 = DAT_febebe1c;
  puVar8 = 0xfebeb800u;
  scale_signed16_by_unsigned_ratio_with_symmetric_saturation_d1232((int)((int)(int16_t)DAT_febeaf56),0x168,0x80,((uint16_t *)(stack_record_34)));
  uVar7 = (*((uint *)camry_host_ptr((uint32_t)(puVar8 + 0x3790))));
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar8 + (uint32_t)(0x3500))))) == 'Z') {
    uVar9 = 0x5a;
  }
  else {
    uVar9 = 0;
  }
  cVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar8 + (uint32_t)(0x3781)))));
  uVar2 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar8 + (uint32_t)(0x3b02)))));
  cVar6 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar8 + (uint32_t)(0x3b00)))));
  if ((cVar6 != '\0') && (cVar6 != '\x02')) {
    if (cVar6 == '\x03') {
      cVar6 = '\x04';
    }
    else {
      cVar6 = '\x01';
    }
  }
  uVar3 = (*((ushort *)camry_host_ptr((uint32_t)(puVar8 + 0x3788))));
  if ((uVar3 & 3) == 0) {
    uVar12 = (undefined2)( (int)(((int)(*((short *)camry_host_ptr((uint32_t)(puVar8 + -0x8b0)))) + (int)(*((short *)camry_host_ptr((uint32_t)(puVar8 + -0x8ae)))))) / (int)2)
    ;
  }
  else if ((uVar3 & 1) == 0) {
    uVar12 = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar8 + -0x8b0))));
  }
  else {
    uVar12 = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar8 + -0x8ae))));
  }
  if (((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar8 + (uint32_t)(-0x8b3))))) == 'Z') || ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar8 + (uint32_t)(-0x8b2))))) == 'Z')) {
    uVar11 = 0x5a;
  }
  else {
    uVar11 = 0;
  }
  scale_signed16_by_unsigned_ratio_with_symmetric_saturation_d1232((int)(*((short *)camry_host_ptr((uint32_t)(puVar8 + 0x3b06)))),0x100,100,((uint16_t *)((stack_record_34 + 2))));
  if ((cVar5 == 'Z') || (cVar4 == 'Z')) {
    uVar10 = 0x5a;
  }
  else {
    uVar10 = 0;
  }
  scale_signed32_ratio_with_overflow_order_fallback_d1272((*((undefined4 *)camry_host_ptr((uint32_t)(puVar8 + -0x8a0)))),0x2d,0x200,((uint32_t *)((stack_record_34 + 4))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar8 + (uint32_t)(-0xbca))))) = uVar10;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar8 + (uint32_t)(-0xbd7))))) = (uVar7 & 0x70017001) != 0x70017001;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar8 + (uint32_t)(-0xbd6))))) = (uVar7 & 0x40004) != 0;
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar8 + -0xbbe)))) = (*((uint16_t *)(stack_record_34 + 0)));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar8 + (uint32_t)(-0xbcf))))) = uVar9;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar8 + (uint32_t)(-0xbd8))))) = cVar1 == 'Z';
  (*((ushort *)camry_host_ptr((uint32_t)(puVar8 + -0xbb0)))) = uVar3;
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar8 + -3000)))) = uVar12;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar8 + (uint32_t)(-0xbcc))))) = uVar2;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar8 + (uint32_t)(-0xbcd))))) = cVar6;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar8 + (uint32_t)(-0xbcb))))) = uVar11;
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar8 + -0xb84)))) = (*((uint16_t *)(stack_record_34 + 2)));
  (*((undefined4 *)camry_host_ptr((uint32_t)(puVar8 + -0xb48)))) = (*((uint32_t *)(stack_record_34 + 4)));
  return;
}

void copy_selected_inputs_to_ac28_extended_snapshot_bcbd8(void)

{
  DAT_febeac88 = DAT_febeaf60;
  DAT_febeac8c = DAT_febeaf6c;
  DAT_febeacac = DAT_febeaf68;
  DAT_febeac44 = ((int)(int16_t)DAT_febeed04);
  DAT_febeac4a = DAT_febebee2;
  DAT_febeac46 = ((int)(int16_t)DAT_febeaf58);
  DAT_febeac4c = ((int)(int16_t)DAT_febeaf40);
  DAT_febeac4e = (ushort)DAT_febeb24d;
  DAT_febeac66 = (ushort)DAT_febeb24e;
  DAT_febeac2b = DAT_febeb112;
  DAT_febeac2c = DAT_febeb113;
  DAT_febeac40 = DAT_febeb116;
  DAT_febeac90 = DAT_febeaf64;
  DAT_febeac2e = DAT_febeb1ce;
  DAT_febeac5a = DAT_febeb1f8;
  DAT_febeac94 = DAT_febef30c;
  DAT_febeac98 = DAT_febef308;
  DAT_febeac9c = DAT_febef314;
  DAT_febeaca0 = DAT_febef318;
  DAT_febeaca4 = DAT_febef310;
  DAT_febeaca8 = DAT_febef31c;
  DAT_febeac2f = DAT_febeb121;
  DAT_febeac30 = DAT_febebef0;
  DAT_febeac5c = DAT_febeb138;
  DAT_febeac5e = DAT_febeb13a;
  DAT_febeac60 = DAT_febeb13c;
  DAT_febeac62 = DAT_febeb13e;
  DAT_febeac64 = DAT_febeb140;
  DAT_febeac6a = ((int)(int16_t)DAT_febebcf0);
  DAT_febeacb0 = DAT_febebed4;
  DAT_febeac72 = DAT_febebede;
  DAT_febeac32 = DAT_febef301;
  DAT_febeac74 = DAT_febef304;
  DAT_febeac52 = DAT_febeef8e;
  DAT_febeac3b = DAT_febebe23;
  DAT_febeac6e = ((int)(int16_t)DAT_febebd80);
  DAT_febeac6c = DAT_febebd82;
  DAT_febeacb4 = DAT_febeaf70;
  DAT_febeac3a = DAT_febebe22;
  DAT_febeac37 = DAT_febeef80;
  DAT_febeac3c = DAT_febeb354;
  DAT_febeac3d = DAT_febeac02;
  DAT_febeac80 = ((int)(int16_t)DAT_febeed12);
  DAT_febeac82 = ((int)(int16_t)DAT_febeaf42);
  DAT_febeac41 = DAT_febeb3fd;
  DAT_febeac84 = DAT_febeb400;
  return;
}

void refresh_derived_and_copied_ac_snapshot_then_d1100_bcd02(void)

{
  derive_scaled_and_masked_ac28_snapshot_fields_bcaa6();
  copy_selected_inputs_to_ac28_extended_snapshot_bcbd8();
  call_assist_command_update_slice_d1100();
  return;
}

void snapshot_f06a_and_run_d1124_chain_bcd22(void)

{
  DAT_febead5b = DAT_febef06a;
  run_init_chain_d0ce8();
  return;
}

void clear_record8_pending_on_terminal_status_nibble_bcd36(void)

{
  uint32_t puVar1;
  uint uVar2;
  
  puVar1 = 0xfebeb800u;
  if (DAT_febeaceb == 'Z') {
    uVar2 = call_nvm_record_status_with_u16_selector_ff0c4(8);
    if (((uVar2 & 0xf0) == 0x30) || ((uVar2 & 0xf0) == 0x10)) {
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0xb15))))) = 0;
    }
  }
  return;
}

void refresh_foreground_control_projection(void)

{
  uint8_t stack_record_4c[76];
  char cVar1;
  char cVar2;
  char cVar3;
  undefined1 uVar4;
  undefined1 uVar5;
  undefined1 uVar6;
  undefined1 uVar7;
  char cVar8;
  undefined1 uVar9;
  undefined1 uVar10;
  char cVar11;
  undefined1 uVar12;
  undefined1 uVar13;
  char cVar14;
  undefined1 uVar15;
  undefined1 uVar16;
  undefined1 uVar17;
  char cVar18;
  char cVar19;
  char cVar20;
  undefined1 uVar21;
  char cVar22;
  undefined1 uVar23;
  undefined1 uVar24;
  undefined1 uVar25;
  char cVar26;
  undefined1 uVar27;
  undefined1 uVar28;
  undefined1 uVar29;
  char cVar30;
  undefined1 uVar31;
  undefined1 uVar32;
  code cVar33;
  undefined1 uVar34;
  char cVar35;
  short sVar36;
  short sVar37;
  int iVar38;
  uint32_t puVar39;
  uchar uVar40;
  undefined1 uVar41;
  undefined1 uVar42;
  undefined1 uVar43;
  undefined1 uVar44;
  char cVar45;
  
  puVar39 = 0xfebeb800u;
  scale_signed32_ratio_with_overflow_order_fallback_d1272(DAT_febeafec,0x2d,0x200,((uint32_t *)(stack_record_4c)));
  sVar37 = (*((short *)camry_host_ptr((uint32_t)(puVar39 + -0x822))));
  scale_signed16_by_unsigned_ratio_with_symmetric_saturation_d1232((int)sVar37,0x168,0x80,((uint16_t *)((stack_record_4c + 6))));
  scale_signed32_ratio_with_overflow_order_fallback_d1272((int)(*((short *)camry_host_ptr((uint32_t)(puVar39 + 0x39ac)))),0x80,100,((uint32_t *)((stack_record_4c + 8))));
  scale_signed32_ratio_with_overflow_order_fallback_d1272((int)(*((short *)camry_host_ptr((uint32_t)(puVar39 + 0x39aa)))),0x80,100,((uint32_t *)((stack_record_4c + 12))));
  scale_signed32_ratio_with_overflow_order_fallback_d1272((int)(*((short *)camry_host_ptr((uint32_t)(puVar39 + 0x39b0)))),0x80,100,((uint32_t *)((stack_record_4c + 16))));
  scale_signed32_ratio_with_overflow_order_fallback_d1272((int)(*((short *)camry_host_ptr((uint32_t)(puVar39 + 0x39ae)))),0x80,100,((uint32_t *)((stack_record_4c + 20))));
  scale_signed16_by_unsigned_ratio_with_symmetric_saturation_d1232((int)(*((short *)camry_host_ptr((uint32_t)(puVar39 + 0x3984)))),0x100,100,((uint16_t *)((stack_record_4c + 24))));
  scale_signed16_by_unsigned_ratio_with_symmetric_saturation_d1232((int)(*((short *)camry_host_ptr((uint32_t)(0x3998u + (int)puVar39)))),0x100,100,((uint16_t *)((stack_record_4c + 26))));
  scale_signed16_by_unsigned_ratio_with_symmetric_saturation_d1232((int)(char)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(0x3880))))),1000,0x32,((uint16_t *)((stack_record_4c + 28))));
  scale_signed16_by_unsigned_ratio_with_symmetric_saturation_d1232((int)(char)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(0x3881))))),1000,0x32,((uint16_t *)((stack_record_4c + 30))));
  cVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(0x3800)))));
  cVar45 = cVar1;
  if ((cVar1 != '\0') && (cVar1 != '\x02')) {
    if (cVar1 == '\x03') {
      cVar45 = '\x04';
    }
    else {
      cVar45 = '\x01';
    }
  }
  cVar2 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(-0x65c)))));
  if (((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(-0x82b))))) == 'Z') || ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(-0x82a))))) == 'Z')) {
    uVar42 = 0x5a;
  }
  else {
    uVar42 = 0;
  }
  cVar3 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(0x6fa)))));
  uVar4 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(0x3869)))));
  uVar5 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(0x382e)))));
  uVar6 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(0x3870)))));
  uVar7 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(0x3890)))));
  cVar8 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(0x6fb)))));
  uVar9 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(0x388a)))));
  uVar10 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(0x3893)))));
  cVar11 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(0x6f8)))));
  uVar12 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(0x3887)))));
  uVar13 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(0x38a9)))));
  cVar14 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(0x6f9)))));
  uVar15 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(0x38a8)))));
  uVar16 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(0x38a3)))));
  uVar17 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(0x3849)))));
  cVar18 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(0x6fc)))));
  cVar19 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(0x692)))));
  cVar20 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(0x693)))));
  uVar21 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(0x387a)))));
  cVar22 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(0x690)))));
  uVar23 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(0x389f)))));
  uVar24 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(0x3882)))));
  uVar25 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(0x383a)))));
  cVar26 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(0x691)))));
  uVar27 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(0x38fa)))));
  uVar28 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(0x3846)))));
  uVar29 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(0x388b)))));
  cVar30 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(0x694)))));
  uVar31 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(0x3859)))));
  uVar32 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(0x38f0)))));
  cVar33 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x3824u + (uint32_t)((int)(puVar39 + 4))))));
  uVar34 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(0x3860)))));
  cVar35 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(0x389b)))));
  uVar40 = get_grouped_status_byte(0x16);
  sVar36 = (*((short *)camry_host_ptr((uint32_t)(puVar39 + -0x6e6))));
  uVar44 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(-0xb40)))));
  if (((sVar36 == 0x400) && (uVar40 != 'Z')) && (uVar44 = 0, cVar35 == '\0')) {
    uVar44 = cVar1 == '\0';
  }
  if (((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(-0x7b4))))) == 'Z') || ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(0x61c))))) == 'Z')) {
    uVar43 = 0x5a;
  }
  else {
    uVar43 = 0;
  }
  uVar41 = thunk_get_state_byte_8c19_58c84();
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(-0xb44))))) = uVar41;
  (*((short *)camry_host_ptr((uint32_t)(puVar39 + -0xa06)))) = sVar36;
  (*((short *)camry_host_ptr((uint32_t)(puVar39 + -0x9c2)))) = sVar37;
  (*((undefined4 *)camry_host_ptr((uint32_t)(puVar39 + -0x914)))) = (*((uint32_t *)(stack_record_4c + 0)));
  (*((undefined4 *)camry_host_ptr((uint32_t)(puVar39 + -0x918)))) = (*((undefined4 *)camry_host_ptr((uint32_t)(puVar39 + -0x814))));
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar39 + -0xa10)))) = (*((uint16_t *)(stack_record_4c + 6)));
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar39 + -0xa0e)))) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar39 + -0x7ac))));
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar39 + -0xa0c)))) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar39 + 0x6e4))));
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar39 + -0xa0a)))) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar39 + 0x6e2))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(-0xb43))))) = cVar45;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(-0xb42))))) = cVar2 == '\x11';
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(-0xb40))))) = uVar44;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(-0xae7))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(0x3814)))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(-0xb06))))) = uVar42;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(-0xaa1))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(-0x6df)))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(-0xae8))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(0x6f0)))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(-0xace))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(0x3813)))));
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar39 + -0xa08)))) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar39 + -0x780))));
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar39 + -0xa04)))) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar39 + -0x77e))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(-0xb41))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(-0x6ee)))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(-0xb07))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(0x699)))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(-0xb05))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(-0x659)))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(-0xb04))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(0x5ed)))));
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar39 + -0x9dc)))) = (*((uint16_t *)(stack_record_4c + 26)));
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar39 + -0x9da)))) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar39 + -0x830))));
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar39 + -0x9e8)))) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar39 + 0x4b0))));
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar39 + -0x9e6)))) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar39 + 0x4c2))));
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar39 + -0x9e4)))) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar39 + 0x59e))));
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar39 + -0x9e2)))) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar39 + -0x7f6))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(-0xaee))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(0x69a)))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(-0xaf8))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(0x385d)))));
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar39 + -0x9d2)))) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar39 + 0x3974))));
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar39 + -0x9d0)))) = (*((undefined2 *)camry_host_ptr((uint32_t)(0x396cu + (int)puVar39))));
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar39 + -0x9ce)))) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar39 + 0x396e))));
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar39 + -0x9cc)))) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar39 + 0x3970))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(-0xaed))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(0x704)))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(-0xacf))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(0x705)))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(-0xac5))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(0x385c)))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(-0xac6))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(-0x8bc)))));
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar39 + -0x9a6)))) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar39 + -0x6c2))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(-0xabf))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(-0x632)))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(-0xa68))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(0x6b8)))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(-0xa41))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x3942u + (uint32_t)((int)(puVar39 + 3))))));
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar39 + -0x962)))) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar39 + 0x39fe))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(-0xa40))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(0x3946)))));
  (*((undefined4 *)camry_host_ptr((uint32_t)(puVar39 + -0x8e0)))) = (*((undefined4 *)camry_host_ptr((uint32_t)(puVar39 + 0x3a2c))));
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar39 + -0x9b6)))) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar39 + 0x580))));
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar39 + -0x9a2)))) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar39 + 0x4a6))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(-0xab4))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(0x4a4)))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(-0xaa3))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(0x69f)))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(-0xaa2))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(0x6a0)))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(-0xab3))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(-0x79c)))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(-0xb03))))) = cVar33;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(-0xb02))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(0x3829)))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(-0xb01))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(0x382a)))));
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar39 + -0x9e0)))) = (*((uint16_t *)(stack_record_4c + 24)));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(-0xa28))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(0x394c)))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(-0xae6))))) = uVar5;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(-0xae5))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(0x3833)))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(-0xae4))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(0x3832)))));
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar39 + -0x9c0)))) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar39 + 0x3988))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(-0xae3))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(0x3835)))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(-0xae2))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(0x3831)))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(-0xae1))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(0x3830)))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(-0xae0))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(0x3834)))));
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar39 + -0x9be)))) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar39 + 0x3986))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(-0xadf))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(0x3836)))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(-0xade))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(0x3837)))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(-0xab2))))) = uVar25;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(-0xab1))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(0x3841)))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(-0xab0))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(0x3844)))));
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar39 + -0x9a0)))) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar39 + 0x398c))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(-0xaaf))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(0x3843)))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(-0xaae))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(0x3840)))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(-0xaad))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(0x383b)))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(-0xaac))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(0x383f)))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(-0xaab))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(0x383c)))));
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar39 + -0x99e)))) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar39 + 0x656))));
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar39 + -0x99c)))) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar39 + 0x654))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(-0xa64))))) = uVar27;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(-0xaaa))))) = uVar28;
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar39 + -0x99a)))) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar39 + 0x398e))));
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar39 + -0x998)))) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar39 + 0x3990))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(-0xaa9))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(0x3848)))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(-0xaa8))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(0x3847)))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(-0xafd))))) = uVar34;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(-0xafc))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(0x3861)))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(-0xafb))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(0x3862)))));
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar39 + -0x9d8)))) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar39 + 0x399c))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(-0xafa))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(0x3864)))));
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar39 + -0x9d6)))) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar39 + 0x399a))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(-0xaf9))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(0x3863)))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(-0xb3f))))) = uVar4;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(-0xb3e))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(0x386d)))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(-0xb3d))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(0x3868)))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(-0xb3c))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(0x386b)))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(-0xb3a))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x386cu + (uint32_t)((int)puVar39)))));
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar39 + -0xa02)))) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar39 + 0x39a0))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(-0xb3b))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(0x386f)))));
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar39 + -0xa00)))) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar39 + 0x39a2))));
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar39 + -0x9de)))) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar39 + 0x399e))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(-0xaa5))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(0x386a)))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(-0xadd))))) = uVar6;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(-0xadc))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(0x3872)))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(-0xadb))))) = uVar21;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(-0xada))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(0x387f)))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(-0xad8))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(0x3875)))));
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar39 + -0x9bc)))) = (*((undefined2 *)camry_host_ptr((uint32_t)(0x39a6u + (int)puVar39))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(-0xad7))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(0x387d)))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(-0xad6))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(0x387e)))));
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar39 + -0x9ba)))) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar39 + 0x39a8))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(-0xad5))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(0x3878)))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(-0xad4))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(0x3877)))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(-0xad3))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(0x3879)))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(-0xad2))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(0x3873)))));
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar39 + -0x9b8)))) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar39 + 0x39a4))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(-0xad1))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(0x387c)))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(-0xad0))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(0x3874)))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(-0xad9))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(0x3876)))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(-0xb39))))) = uVar12;
  (*((undefined4 *)camry_host_ptr((uint32_t)(puVar39 + -0x910)))) = (*((uint32_t *)(stack_record_4c + 8)));
  (*((undefined4 *)camry_host_ptr((uint32_t)(puVar39 + -0x90c)))) = (*((uint32_t *)(stack_record_4c + 12)));
  (*((undefined4 *)camry_host_ptr((uint32_t)(puVar39 + -0x908)))) = (*((uint32_t *)(stack_record_4c + 16)));
  (*((undefined4 *)camry_host_ptr((uint32_t)(puVar39 + -0x904)))) = (*((uint32_t *)(stack_record_4c + 20)));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(-0xb38))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(0x3884)))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(-0xb37))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(0x3883)))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(-0xb36))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(0x3886)))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(-0xb35))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(0x3885)))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(-0xb34))))) = uVar10;
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar39 + -0x9fe)))) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar39 + 0x6de))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(-0xb33))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(0x3894)))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(-0xa1f))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(0x3895)))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(-0xa1e))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(0x3896)))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(-0xb32))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(0x3897)))));
  sVar37 = (*((short *)camry_host_ptr((uint32_t)(puVar39 + 0x39bc))));
  iVar38 = (int)sVar37;
  if (iVar38 + 0x7fff < 0 != (-1 < iVar38 && iVar38 + 0x7fff < 0) || iVar38 == -0x7fff) {
    sVar37 = -0x7fff;
  }
  (*((short *)camry_host_ptr((uint32_t)(puVar39 + -0x9fc)))) = sVar37;
  sVar37 = (*((short *)camry_host_ptr((uint32_t)(puVar39 + 0x39be))));
  iVar38 = (int)sVar37;
  if (iVar38 + 0x7fff < 0 != (-1 < iVar38 && iVar38 + 0x7fff < 0) || iVar38 == -0x7fff) {
    sVar37 = -0x7fff;
  }
  (*((short *)camry_host_ptr((uint32_t)(puVar39 + -0x9fa)))) = sVar37;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(-0xb2c))))) = uVar7;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(-0xb2b))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(0x3892)))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(-0xb2a))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(0x3891)))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(-0xb29))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(0x388e)))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(-0xb28))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(0x388f)))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(-0xb1b))))) = uVar31;
  sVar37 = (*((short *)camry_host_ptr((uint32_t)(puVar39 + 0x3996))));
  iVar38 = (int)sVar37;
  if (iVar38 + 0x7fff < 0 != (-1 < iVar38 && iVar38 + 0x7fff < 0) || iVar38 == -0x7fff) {
    sVar37 = -0x7fff;
  }
  (*((short *)camry_host_ptr((uint32_t)(puVar39 + -0x9f8)))) = sVar37;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(-0xb1a))))) = uVar32;
  sVar37 = (*((short *)camry_host_ptr((uint32_t)(puVar39 + 0x3992))));
  iVar38 = (int)sVar37;
  if (iVar38 + 0x7fff < 0 != (-1 < iVar38 && iVar38 + 0x7fff < 0) || iVar38 == -0x7fff) {
    sVar37 = -0x7fff;
  }
  (*((short *)camry_host_ptr((uint32_t)(puVar39 + -0x9f6)))) = sVar37;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(-0xb27))))) = cVar35;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(-0xb26))))) = uVar13;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(-0xb22))))) = cVar8 == 'Z';
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(-0xb24))))) = cVar3 == 'Z';
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(-0xb23))))) = cVar18 == 'Z';
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(-0xb25))))) = uVar15;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(-0xb21))))) = cVar19 == 'Z';
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(-0xb20))))) = cVar20 == 'Z';
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(-0xb1f))))) = cVar30 == 'Z';
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(-0xa8f))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(0x38a6)))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(-0xa8e))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(0x38a7)))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(-0xb31))))) = uVar16;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(-0xb30))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(0x38a2)))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(-0xb2f))))) = uVar17;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(-0xb2d))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(0x384a)))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(-0xb2e))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(0x384b)))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(-0xb19))))) = cVar22 == 'Z';
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(-0xb18))))) = cVar26 == 'Z';
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar39 + -0x9f4)))) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar39 + 0x696))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(-0xb1e))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(0x389a)))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(-0xb17))))) = cVar11 == 'Z';
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(-0xb16))))) = cVar14 == 'Z';
  (*((undefined4 *)camry_host_ptr((uint32_t)(puVar39 + -0x900)))) = (*((undefined4 *)camry_host_ptr((uint32_t)(puVar39 + 0x700))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(-0xb1d))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(0x389d)))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(-0xb1c))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(0x389e)))));
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar39 + -0x9c8)))) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar39 + -0x6c8))));
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar39 + -0x9c6)))) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar39 + -0x6c6))));
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar39 + -0x9c4)))) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar39 + -0x6c0))));
  (*((undefined4 *)camry_host_ptr((uint32_t)(puVar39 + -0x8f4)))) = (*((undefined4 *)camry_host_ptr((uint32_t)(puVar39 + -0x4f4))));
  (*((undefined4 *)camry_host_ptr((uint32_t)(puVar39 + -0x8f8)))) = (*((undefined4 *)camry_host_ptr((uint32_t)(puVar39 + 0x6d4))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(-0xacc))))) = uVar9;
  sVar37 = (*((short *)camry_host_ptr((uint32_t)(puVar39 + 0x39b2))));
  iVar38 = (int)sVar37;
  if (iVar38 + 0x7fff < 0 != (-1 < iVar38 && iVar38 + 0x7fff < 0) || iVar38 == -0x7fff) {
    sVar37 = -0x7fff;
  }
  (*((short *)camry_host_ptr((uint32_t)(puVar39 + -0x9b4)))) = sVar37;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(-0xac9))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(0x3888)))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(-0xac8))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(0x3889)))));
  sVar37 = (*((short *)camry_host_ptr((uint32_t)(puVar39 + 0x39b4))));
  iVar38 = (int)sVar37;
  if (iVar38 + 0x7fff < 0 != (-1 < iVar38 && iVar38 + 0x7fff < 0) || iVar38 == -0x7fff) {
    sVar37 = -0x7fff;
  }
  (*((short *)camry_host_ptr((uint32_t)(puVar39 + -0x9b2)))) = sVar37;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(-0xacb))))) = uVar23;
  sVar37 = (*((short *)camry_host_ptr((uint32_t)(0x39c0u + (int)(puVar39 + 2)))));
  iVar38 = (int)sVar37;
  if (iVar38 + 0x7fff < 0 != (-1 < iVar38 && iVar38 + 0x7fff < 0) || iVar38 == -0x7fff) {
    sVar37 = -0x7fff;
  }
  (*((short *)camry_host_ptr((uint32_t)(puVar39 + -0x9b0)))) = sVar37;
  sVar37 = (*((short *)camry_host_ptr((uint32_t)(puVar39 + 0x39c4))));
  iVar38 = (int)sVar37;
  if (iVar38 + 0x7fff < 0 != (-1 < iVar38 && iVar38 + 0x7fff < 0) || iVar38 == -0x7fff) {
    sVar37 = -0x7fff;
  }
  (*((short *)camry_host_ptr((uint32_t)(puVar39 + -0x9ae)))) = sVar37;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(-0xaca))))) = uVar24;
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar39 + -0x9ac)))) = (*((uint16_t *)(stack_record_4c + 28)));
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar39 + -0x9aa)))) = (*((uint16_t *)(stack_record_4c + 30)));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(-0xaa7))))) = uVar29;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(-0xaa6))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(0x388d)))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(-0xac4))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(-0x3ba)))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(-0xac2))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(-0x3b8)))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(-0xac3))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(-0x3b9)))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(-0xac1))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(-0x3b4)))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(-0xaa4))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(-0x3b2)))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(-0xac0))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(-0x3b3)))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(-0xa92))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(0x38c0)))));
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar39 + -0x930)))) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar39 + 0x3a00))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(-0xa24))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(0x3954)))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(-0xa91))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(0x38c1)))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(-0xa90))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(0x38c2)))));
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar39 + -0x990)))) = (*((undefined2 *)camry_host_ptr((uint32_t)(0x39d6u + (int)puVar39))));
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar39 + -0x98e)))) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar39 + 0x39d8))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(-0xa8d))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(0x38d6)))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(-0xa8c))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(0x38d7)))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(-0xa8b))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(0x38d8)))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(-0xa8a))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(0x38d9)))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(-0xa89))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(0x38dc)))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(-0xa88))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(0x38dd)))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(-0xa87))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(0x38de)))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(-0xa86))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(0x38df)))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(-0xa85))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(0x38e0)))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(-0xa84))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(0x38e2)))));
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar39 + -0x98c)))) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar39 + 0x39da))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(-0xa83))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(0x38e4)))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(-0xa58))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(0x38e5)))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(-0xa59))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(0x38e1)))));
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar39 + -0x98a)))) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar39 + 0x39dc))));
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar39 + -0x974)))) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar39 + 0x39de))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(-0xa82))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(0x38e8)))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(-0xa81))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(0x38ea)))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(-0xa80))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(0x38ed)))));
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar39 + -0x988)))) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar39 + 0x39cc))));
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar39 + -0x986)))) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar39 + 0x39ce))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(-0xa7f))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(0x38c6)))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(-0xa7e))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(0x38c4)))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(-0xa7d))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(0x38c9)))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(-0xa7c))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(0x38c8)))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(-0xa7b))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(0x38c5)))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(-0xa7a))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(0x38c7)))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(-0xa79))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(0x38cd)))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(-0xa78))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(0x38ca)))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(-0xa77))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(0x38cc)))));
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar39 + -0x984)))) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar39 + 0x39d0))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(-0xa76))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(0x38c3)))));
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar39 + -0x982)))) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar39 + 0x39d2))));
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar39 + -0x976)))) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar39 + 0x39d4))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(-0xa75))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(0x38ce)))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(-0xa74))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(0x38d0)))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(-0xa73))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(0x38d1)))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(-0xa5a))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(0x38d2)))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(-0xa5b))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(0x38cb)))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(-0xa72))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(0x38d3)))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(-0xa47))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(0x393e)))));
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar39 + -0x970)))) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar39 + 0x39fa))));
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar39 + -0x926)))) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar39 + 0x39fc))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(-0xa23))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(0x3955)))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(-0xa51))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(0x393b)))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(-0xa1b))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(0x393c)))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(-0xa50))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(0x3930)))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(-0xa1d))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(0x3931)))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(-0xa4f))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(0x3932)))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(-0xa1c))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(0x3933)))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(-0xa45))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(0x3934)))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(-0xa44))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(0x3937)))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(-0xa43))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(0x3938)))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(-0xa42))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(0x3939)))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(-0xa3f))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(0x393a)))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(-0xa3e))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(0x3936)))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(-0xa27))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(0x394d)))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(-0xa20))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(0x3958)))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(-0xa46))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x3918u + (uint32_t)((int)(puVar39 + 3))))));
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar39 + -0x92a)))) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar39 + 0x39b8))));
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar39 + -0x928)))) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar39 + 0x39ba))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(-0xa26))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(0x394e)))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(-0xa1a))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(0x394f)))));
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar39 + -0x96e)))) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar39 + 0x39f2))));
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar39 + -0x91c)))) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar39 + 0x39f4))));
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar39 + -0x96c)))) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar39 + 0x39f6))));
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar39 + -0x91a)))) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar39 + 0x39f8))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(-0xa4e))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(0x392a)))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(-0xa13))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(0x392b)))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(-0xa4d))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(0x392c)))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(-0xa12))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(0x392d)))));
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar39 + -0x96a)))) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar39 + 0x39e6))));
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar39 + -0x922)))) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar39 + 0x39e8))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(-0xa4c))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(0x391e)))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(-0xa18))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(0x391f)))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(-0xa4b))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(0x3921)))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(-0xa17))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(0x3920)))));
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar39 + -0x968)))) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar39 + 0x39e2))));
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar39 + -0x924)))) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar39 + 0x39e4))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(-0xa4a))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(0x391c)))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(-0xa19))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(0x391d)))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(-0xa25))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(0x3950)))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(-0xa16))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(0x3951)))));
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar39 + -0x966)))) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar39 + 0x39ea))));
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar39 + -0x920)))) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar39 + 0x39ec))));
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar39 + -0x964)))) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar39 + 0x39ee))));
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar39 + -0x91e)))) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar39 + 0x39f0))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(-0xa49))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(0x3924)))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(-0xa15))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(0x3925)))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(-0xa48))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(0x3926)))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(-0xa14))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(0x3927)))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(-0xa66))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(-0x82c)))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(-0xa65))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(-0x786)))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(-0xa63))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(-0x788)))));
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar39 + -0x978)))) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar39 + -0x77c))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(-0xa5e))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(-0x7b3)))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(-0xa5d))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(0x602)))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(-0xa5c))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(0x603)))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(-0xa54))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(0x604)))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(-0xa56))))) = uVar43;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(-0xa53))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(0x605)))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(-0xa52))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x3908u + (uint32_t)((int)(puVar39 + 4))))));
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar39 + -0x960)))) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar39 + 0x396a))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(-0xa3d))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(-0x7c0)))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(-0xa3c))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(-0x7bf)))));
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar39 + -0x95e)))) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar39 + -0x81c))));
  (*((undefined4 *)camry_host_ptr((uint32_t)(puVar39 + -0x8dc)))) = (*((undefined4 *)camry_host_ptr((uint32_t)(puVar39 + -0x818))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(-0xa2c))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar39 + (uint32_t)(0x3947)))));
  thunk_run_cadence_gated_control_updates_and_publication_d0eec();
  clear_record8_pending_on_terminal_status_nibble_bcd36();
  return;
}
