#include "common.h"

void return_only_stub_bb16a(void)

{
  return;
}

void reset_owner1_limit_request(void)

{
  DAT_febebcf0 = 0x569a;
  return;
}

void publish_owner1_limit_request(void)

{
  short sVar1;
  short sVar2;
  uint32_t puVar3;
  short bound;
  int iVar4;
  int iVar5;
  short sStack_a;
  
  puVar3 = 0xfebeb800u;
  iVar4 = (int)((int)(int16_t)DAT_febebcf0);
  iVar5 = (int)((int)(int16_t)DAT_febebce8);
  sStack_a = ((int)(int16_t)DAT_febebcf0);
  sVar1 = DAT_000af0c6;
  if (DAT_febebce0 != '3') {
    if (DAT_febebce0 == '\0') {
      sVar1 = DAT_000af0c4 + ((int)(int16_t)DAT_febebcf0);
    }
    else if (DAT_febebce0 == '\x11') {
      sVar1 = ((int)(int16_t)DAT_febebcf0) - DAT_000af0b8;
    }
    else {
      sVar1 = sStack_a;
      if (DAT_febebce0 == '\"') {
        puVar3 = 0xfebeb800u;
        if (iVar4 - iVar5 < 0 == (iVar4 < 0 != iVar5 < 0 && iVar5 < 0 == iVar4 - iVar5 < 0)) {
          iVar5 = (int)DAT_000af0c0;
          sVar1 = DAT_000af0ba;
          sVar2 = DAT_000af0c0;
          if ((iVar4 - iVar5 < 0 == (iVar4 < 0 != iVar5 < 0 && iVar5 < 0 == iVar4 - iVar5 < 0) &&
               iVar4 != iVar5) ||
             (iVar5 = (int)DAT_000af0c2, sVar1 = DAT_000af0bc, bound = ((int)(int16_t)DAT_febebce8),
             sVar2 = DAT_000af0c2, sStack_a = DAT_000af0be,
             iVar4 - iVar5 < 0 == (iVar4 < 0 != iVar5 < 0 && iVar5 < 0 == iVar4 - iVar5 < 0) &&
             iVar4 != iVar5)) {
            bound = sVar2;
            sStack_a = sVar1;
          }
          sStack_a = ((int)(int16_t)DAT_febebcf0) - sStack_a;
          store_signed_halfword_max(sStack_a,bound,&sStack_a);
          sVar1 = sStack_a;
        }
        else {
          sStack_a = ((int)(int16_t)DAT_febebcf0) + DAT_000af0c4;
          store_signed_halfword_min(sStack_a,((int)(int16_t)DAT_febebce8),&sStack_a);
          sVar1 = sStack_a;
        }
      }
    }
  }
  sStack_a = sVar1;
  iVar4 = (int)sStack_a;
  iVar5 = (int)DAT_000af0c6;
  if (iVar4 - iVar5 < 0 == (iVar4 < 0 != iVar5 < 0 && iVar5 < 0 == iVar4 - iVar5 < 0) &&
      iVar4 != iVar5) {
    sStack_a = DAT_000af0c6;
    iVar4 = iVar5;
  }
  if (iVar4 < 0) {
    sStack_a = 0;
    iVar4 = 0;
  }
  set_current_limit_request(1,(ushort)iVar4);
  (*((short *)camry_host_ptr((uint32_t)(puVar3 + 0x4f0)))) = sStack_a;
  return;
}

void initialize_lifecycle_difference_monitor(void)

{
  reset_application_latched_monitor(((F33LatchedMonitorState *)camry_host_ptr((uint32_t)((0xfebebcf4u)))));
  return;
}

void reset_lifecycle_difference_monitor_entry(void)

{
  reset_application_latched_monitor(((F33LatchedMonitorState *)camry_host_ptr((uint32_t)((0xfebebcf4u)))));
  return;
}

void step_lifecycle_difference_monitor(void)

{
  step_application_latched_monitor
            (((F33LatchedMonitorState *)camry_host_ptr((uint32_t)((0xfebebcf4u)))), ((F33MonitorLimits *)camry_host_ptr((uint32_t)((0xaf050u)))), ((F33TwoSidedMonitorCallbacks *)camry_host_ptr((uint32_t)((0xaeca0u)))));
  return;
}

uint classify_lifecycle_conditioned_sample_difference(void)

{
  int iVar1;
  ushort uVar2;
  char cVar3;
  uint uVar4;
  int iVar5;
  int iVar6;
  short sStack_12;
  
  cVar3 = DAT_febebef0;
  uVar2 = DAT_febebede;
  if (DAT_febeb1a4 == '\x11') {
    iVar6 = (int)((int)(int16_t)DAT_febeb00c);
    store_saturated_signed16_absolute_d1178((int)((int)(int16_t)DAT_febeb02c),&sStack_12);
    iVar5 = (int)DAT_000af0c8;
    iVar1 = (sStack_12 - iVar6) - iVar5;
    if (((iVar1 < 0 == (sStack_12 - iVar6 < 0 != iVar5 < 0 && iVar5 < 0 == iVar1 < 0)) &&
        (DAT_000af0ca < uVar2)) && (cVar3 == '\x11')) {
      uVar4 = 0x22;
    }
    else {
      uVar4 = 0x11;
    }
  }
  else {
    uVar4 = 0x44;
  }
  return uVar4;
}

void confirm_lifecycle_difference_diagnostic(void)

{
  thunk_increment_indexed_u16_counter_once_until_rearmed_545de(10);
  thunk_gate_indexed_event_payload_during_diagnostic_clears_51cf6(8,800);
  return;
}

void return_only_stub_bb2f4(void)

{
  return;
}

void reset_owner6_calibration_envelope(void)

{
  DAT_febebd18 = 0x569a0000;
  DAT_febebd00 = 0;
  DAT_febebd01 = 0;
  DAT_febebd10 = ((int)(int16_t)DAT_febeafdc);
  DAT_febebd02 = 0;
  DAT_febebd2c = (int)((int)(int16_t)DAT_febeafdc) << 0x10;
  DAT_febebd06 = 0x569a;
  DAT_febebd08 = DAT_febeb084;
  DAT_febebd1c = (uint)DAT_febeb084 << 0x10;
  DAT_febebd20 = 0;
  DAT_febebd03 = 0;
  DAT_febebd0a = 0;
  DAT_febebd0e = DAT_febeb084;
  DAT_febebd24 = (uint)DAT_febeb084 << 0x10;
  DAT_febebd04 = 0;
  DAT_febebd0c = 0x569a;
  DAT_febebd28 = 0;
  DAT_febebd12 = 0x569a;
  DAT_febebd14 = 0x569a;
  DAT_febebd30 = 0x569a;
  DAT_febebd16 = 0x569a;
  return;
}

void select_owner6_calibration_family(void)

{
  DAT_febebd20 = DAT_febeb30c;
  if ((DAT_febeb30c != 0x55aaaa55) && (DAT_febeb30c != -0x55aaaa56)) {
    DAT_febebd20 = DAT_000af1b8;
  }
  return;
}

void update_owner6_gate_and_axis_filter(void)

{
  uint8_t stack_record_2c[44];
  int iVar1;
  ushort uVar2;
  int iVar3;
  uint32_t puVar4;
  int iVar5;
  uint uVar6;
  int iVar7;
  int iVar8;
  int iVar9;
  undefined1 uVar10;
  undefined1 uVar11;
  int iVar12;
  byte bVar13;
  
  uVar2 = DAT_febebee2;
  iVar1 = DAT_febebd2c;
  uVar10 = DAT_febebd02;
  puVar4 = 0xfebeb800u;
  iVar7 = (int)((int)(int16_t)DAT_febeafe0);
  iVar3 = (int)DAT_000af178;
  iVar12 = (int)((int)(int16_t)DAT_febeafdc);
  iVar9 = (int)((int)(int16_t)DAT_febeafde);
  iVar8 = (int)((int)(int16_t)DAT_febebd10);
  if (((iVar7 - iVar3 < 0 == (iVar7 < 0 != iVar3 < 0 && iVar3 < 0 == iVar7 - iVar3 < 0) &&
        iVar7 != iVar3) &&
      (iVar5 = (int)DAT_000af17e,
      iVar12 - iVar5 < 0 != (iVar12 < 0 != iVar5 < 0 && iVar5 < 0 == iVar12 - iVar5 < 0))) ||
     ((iVar7 + iVar3 < 0 != (iVar7 < 0 != -iVar3 < 0 && -iVar3 < 0 == iVar7 + iVar3 < 0) &&
      (iVar7 = -(int)DAT_000af17e, iVar3 = iVar12 + DAT_000af17e,
      iVar3 < 0 == (iVar12 < 0 != iVar7 < 0 && iVar7 < 0 == iVar3 < 0) && iVar12 != iVar7)))) {
    uVar11 = 0x5a;
    bVar13 = DAT_febebd01;
    if (DAT_febebd01 < DAT_000af170) {
      uVar11 = 0;
      bVar13 = DAT_febebd01 + 1;
    }
  }
  else {
    uVar11 = 0;
    bVar13 = 0;
  }
  store_saturated_signed16_absolute_d1178((int)((int)(int16_t)DAT_febeb054),((int16_t *)(stack_record_2c)));
  store_saturated_signed16_absolute_d1178(iVar9,((int16_t *)((stack_record_2c + 2))));
  iVar3 = (int)DAT_000af17a;
  iVar7 = (int)(*((int16_t *)(stack_record_2c + 0)));
  if (iVar7 - iVar3 < 0 != (iVar7 < 0 != iVar3 < 0 && iVar3 < 0 == iVar7 - iVar3 < 0) ||
      iVar7 == iVar3) {
    iVar3 = (int)DAT_000af17c;
    iVar7 = (int)(*((int16_t *)(stack_record_2c + 2)));
    if (iVar7 - iVar3 < 0 != (iVar7 < 0 != iVar3 < 0 && iVar3 < 0 == iVar7 - iVar3 < 0) ||
        iVar7 == iVar3) {
      if (DAT_000af174 < uVar2) {
        if (DAT_000af172 < uVar2) {
          uVar10 = 0x5a;
        }
      }
      else {
        uVar10 = 0;
      }
    }
  }
  uVar6 = (uint)DAT_000af196;
  if (uVar6 == 0) {
    iVar8 = iVar8 << 0x10;
    iVar12 = iVar12 << 0x10;
  }
  else {
    iVar8 = iVar8 * uVar6;
    iVar12 = iVar12 * uVar6;
  }
  iVar12 = iVar12 + (iVar1 - iVar8);
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(0x500))))) = uVar11;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(0x501))))) = bVar13;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(0x502))))) = uVar10;
  (*((int *)camry_host_ptr((uint32_t)(puVar4 + 0x52c)))) = iVar12;
  (*((short *)camry_host_ptr((uint32_t)(puVar4 + 0x510)))) = (short)(iVar12 / 0x10000);
  return;
}

void update_owner6_source_transition(void)

{
  uint8_t stack_record_34[52];
  ushort uVar1;
  undefined1 uVar2;
  int iVar3;
  uint32_t puVar4;
  char cVar5;
  uint uVar6;
  ushort uVar7;
  uint uVar8;
  uint uVar9;
  uint uVar10;
  uint uVar11;
  undefined1 uVar12;
  uint uVar13;
  int iVar14;
  
  uVar7 = DAT_000af184;
  puVar4 = 0xfebeb800u;
  uVar9 = (uint)DAT_000af182;
  uVar10 = (uint)DAT_000af184;
  uVar6 = (uint)DAT_000af186;
  (*((int32_t *)(stack_record_34 + 0))) = ((int)(int32_t)DAT_febebd28);
  uVar13 = uVar9;
  if (DAT_febeb084 <= uVar9) {
    uVar13 = (uint)DAT_febeb084;
  }
  uVar8 = uVar10;
  if (uVar10 <= uVar13) {
    uVar8 = uVar13;
  }
  if (uVar6 == 0) {
    iVar3 = (uint)DAT_febebd08 << 0x10;
    iVar14 = uVar8 << 0x10;
  }
  else {
    iVar3 = DAT_febebd08 * uVar6;
    iVar14 = uVar8 * uVar6;
  }
  uVar13 = iVar14 + (DAT_febebd1c - iVar3);
  uVar6 = uVar13 >> 0x10;
  if (DAT_febeb1a9 == 'Z') {
    uVar1 = DAT_000af192;
    if (DAT_febebd20 == 0x55aaaa55) {
      uVar1 = DAT_000af190;
    }
    uVar6 = (uint)uVar1;
    cVar5 = 'Z';
    (*((uint16_t *)(stack_record_34 + 6))) = DAT_000af18c;
  }
  else {
    (*((uint16_t *)(stack_record_34 + 6))) = 0x569a;
    cVar5 = '\0';
  }
  if ((cVar5 == DAT_febebd03) &&
     ((DAT_febebd04 != 'Z' ||
      (((int)(int32_t)DAT_febebd28) - DAT_000af1b4 < 0 !=
       (((int)(int32_t)DAT_febebd28) < 0 != DAT_000af1b4 < 0 && DAT_000af1b4 < 0 == ((int)(int32_t)DAT_febebd28) - DAT_000af1b4 < 0)
      )))) {
    uVar2 = 0;
  }
  else {
    uVar8 = (uint)DAT_000af18e;
    uVar12 = 0x5a;
    if (uVar8 == 0) {
      iVar3 = (uint)DAT_febebd0e << 0x10;
      iVar14 = uVar6 << 0x10;
    }
    else {
      iVar3 = DAT_febebd0e * uVar8;
      iVar14 = uVar6 * uVar8;
    }
    uVar8 = iVar14 + (DAT_febebd24 - iVar3);
    uVar11 = uVar8 >> 0x10;
    puVar4 = 0xfebeb800u;
    store_saturated_signed32_absolute_d1194(uVar6 - uVar11,((int32_t *)(stack_record_34)));
    uVar2 = 0x5a;
    if ((*((int32_t *)(stack_record_34 + 0))) - DAT_000af1b4 < 0 ==
        ((*((int32_t *)(stack_record_34 + 0))) < 0 != DAT_000af1b4 < 0 && DAT_000af1b4 < 0 == (*((int32_t *)(stack_record_34 + 0))) - DAT_000af1b4 < 0))
    goto LAB_000bb51a;
  }
  uVar12 = uVar2;
  uVar8 = uVar6 << 0x10;
  uVar11 = uVar6;
LAB_000bb51a:
  (*((short *)camry_host_ptr((uint32_t)(puVar4 + 0x50e)))) = (short)uVar11;
  if (uVar9 < uVar11) {
    uVar11 = uVar9;
  }
  (*((short *)camry_host_ptr((uint32_t)(puVar4 + 0x508)))) = (short)(uVar13 >> 0x10);
  if (uVar10 <= uVar11) {
    uVar7 = (ushort)uVar11;
  }
  (*((uint *)camry_host_ptr((uint32_t)(puVar4 + 0x51c)))) = uVar13;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(0x503))))) = cVar5;
  (*((ushort *)camry_host_ptr((uint32_t)(puVar4 + 0x50a)))) = uVar7;
  (*((uint *)camry_host_ptr((uint32_t)(puVar4 + 0x524)))) = uVar8;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(0x504))))) = uVar12;
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar4 + 0x50c)))) = (*((uint16_t *)(stack_record_34 + 6)));
  (*((int *)camry_host_ptr((uint32_t)(puVar4 + 0x528)))) = (*((int32_t *)(stack_record_34 + 0)));
  return;
}

void publish_owner6_calibration_envelope(void)

{
  uint8_t stack_record_38[56];
  char cVar1;
  int iVar2;
  int iVar3;
  uint32_t puVar4;
  int iVar5;
  int iVar6;
  undefined *puVar7;
  undefined *puVar8;
  uint uVar9;
  uint uVar10;
  short sVar11;
  uint uVar12;
  int iVar13;
  uint uVar14;
  int iVar15;
  undefined2 *puVar16;
  
  iVar5 = DAT_febebd30;
  iVar15 = DAT_febebd18;
  cVar1 = DAT_febebd00;
  puVar4 = 0xfebeb800u;
  (*((int16_t *)(stack_record_38 + 4))) = DAT_febebd12;
  (*((int16_t *)(stack_record_38 + 10))) = ((int)(int16_t)DAT_febebd06);
  (*((int16_t *)(stack_record_38 + 6))) = ((int)(int16_t)DAT_febebd14);
  uVar14 = (uint)DAT_febebd0a;
  (*((int16_t *)(stack_record_38 + 8))) = ((int)(int16_t)DAT_febebd0c);
  if (DAT_febebd02 == '\0') {
    if (DAT_febebd20 == 0x55aaaa55) {
      puVar16 = ((undefined *)camry_host_ptr(0xaf18au));
      puVar8 = ((undefined *)camry_host_ptr(0xaf244u));
      puVar7 = ((undefined *)camry_host_ptr(0xaf2ccu));
      uVar9 = (uint)DAT_000af18a;
      uVar10 = (uint)DAT_000af198;
      if (uVar14 < DAT_000af19c) {
LAB_000bb5be:
        uVar12 = (uint)(ushort)puVar16[0xd];
      }
      else {
        uVar12 = (uint)DAT_000af1a0;
      }
    }
    else {
      puVar16 = ((undefined *)camry_host_ptr(0xaf188u));
      puVar8 = ((undefined *)camry_host_ptr(0xaf354u));
      puVar7 = ((undefined *)camry_host_ptr(0xaf1bcu));
      uVar9 = (uint)DAT_000af188;
      uVar10 = (uint)DAT_000af19a;
      if (DAT_000af19e <= uVar14) goto LAB_000bb5be;
      uVar12 = (uint)DAT_000af1a6;
    }
  }
  else if (DAT_febebd20 == 0x55aaaa55) {
    puVar8 = ((undefined *)camry_host_ptr(0xaf288u));
    puVar7 = ((undefined *)camry_host_ptr(0xaf310u));
    uVar9 = (uint)DAT_000af18a;
    uVar10 = (uint)DAT_000af198;
    if (uVar14 < DAT_000af1a8) {
      uVar12 = (uint)DAT_000af1b0;
    }
    else {
      uVar12 = (uint)DAT_000af1ac;
    }
  }
  else {
    puVar8 = ((undefined *)camry_host_ptr(0xaf398u));
    puVar7 = ((undefined *)camry_host_ptr(0xaf200u));
    uVar9 = (uint)DAT_000af188;
    uVar10 = (uint)DAT_000af19a;
    if (uVar14 < DAT_000af1aa) {
      uVar12 = (uint)DAT_000af1b2;
    }
    else {
      uVar12 = (uint)DAT_000af1ae;
    }
  }
  store_saturated_signed16_absolute_d1178((int)((int)(int16_t)DAT_febebd10),((int16_t *)((stack_record_38 + 2))));
  if (cVar1 == 'Z') {
    iVar13 = 0x569a;
    goto LAB_000bb6ae;
  }
  interpolate_signed16_pairs_to_output_d1de4(puVar8,(int)(*((int16_t *)(stack_record_38 + 2))),((int16_t *)((stack_record_38 + 4))));
  interpolate_signed16_pairs_to_output_d1de4(puVar7,(int)(*((int16_t *)(stack_record_38 + 2))),((int16_t *)((stack_record_38 + 6))));
  if (uVar14 < uVar10) {
    iVar5 = (int)(uVar12 * (uVar14 - uVar10)) / 0x800;
    iVar13 = (int)(*((int16_t *)(stack_record_38 + 6)));
LAB_000bb696:
    iVar5 = iVar5 + iVar13;
  }
  else {
    if (uVar9 < uVar14) {
      iVar5 = (int)(uVar12 * (uVar14 - uVar9)) / 0x800;
      iVar13 = (int)(*((int16_t *)(stack_record_38 + 4)));
      goto LAB_000bb696;
    }
    iVar5 = (int)(*((int16_t *)(stack_record_38 + 6)));
    if (uVar9 != uVar10) {
      iVar2 = uVar9 - uVar10;
      iVar13 = ((*((int16_t *)(stack_record_38 + 4))) - iVar5) * (uVar14 - uVar10);
      if (iVar2 != 0) {
        if (iVar13 == -0x80000000 && iVar2 == -1) {
          iVar13 = -0x80000000;
        }
        else {
          iVar13 = (int)iVar13 / (int)iVar2;
        }
      }
      goto LAB_000bb696;
    }
  }
  iVar3 = (int)(*((int16_t *)(stack_record_38 + 8)));
  iVar2 = (int)DAT_000af194;
  iVar13 = iVar5;
  if (iVar3 - iVar5 < 0 != (iVar3 < 0 != iVar5 < 0 && iVar5 < 0 == iVar3 - iVar5 < 0)) {
    iVar13 = iVar3;
  }
  sVar11 = DAT_000af194;
  if (iVar13 - iVar2 < 0 == (iVar13 < 0 != iVar2 < 0 && iVar2 < 0 == iVar13 - iVar2 < 0)) {
    sVar11 = (short)iVar13;
  }
  iVar13 = (int)sVar11;
LAB_000bb6ae:
  uVar14 = (uint)DAT_000af176;
  if (uVar14 == 0) {
    iVar3 = (int)(*((int16_t *)(stack_record_38 + 10))) << 0x10;
    iVar2 = iVar13 << 0x10;
  }
  else {
    iVar3 = (int)(*((int16_t *)(stack_record_38 + 10))) * uVar14;
    iVar2 = iVar13 * uVar14;
  }
  iVar2 = (iVar15 - iVar3) + iVar2;
  store_saturated_signed16_absolute_d1178((int)(short)((short)(iVar2 / 0x10000) - (short)iVar13),((int16_t *)(stack_record_38)));
  iVar3 = (int)DAT_000af180;
  iVar6 = (int)(*((int16_t *)(stack_record_38 + 0)));
  iVar15 = iVar2 / 0x10000;
  if (iVar6 - iVar3 < 0 != (iVar6 < 0 != iVar3 < 0 && iVar3 < 0 == iVar6 - iVar3 < 0) ||
      iVar6 == iVar3) {
    iVar2 = iVar13 << 0x10;
    iVar15 = iVar13;
  }
  set_current_limit_request(6,(ushort)iVar15);
  (*((ushort *)camry_host_ptr((uint32_t)(puVar4 + 0x506)))) = (ushort)iVar15;
  (*((int *)camry_host_ptr((uint32_t)(puVar4 + 0x518)))) = iVar2;
  (*((int *)camry_host_ptr((uint32_t)(puVar4 + 0x530)))) = iVar5;
  (*((short *)camry_host_ptr((uint32_t)(puVar4 + 0x512)))) = (*((int16_t *)(stack_record_38 + 4)));
  (*((short *)camry_host_ptr((uint32_t)(puVar4 + 0x516)))) = (short)iVar13;
  (*((short *)camry_host_ptr((uint32_t)(puVar4 + 0x514)))) = (*((int16_t *)(stack_record_38 + 6)));
  return;
}

void update_owner6_calibration_envelope(void)

{
  select_owner6_calibration_family();
  update_owner6_gate_and_axis_filter();
  update_owner6_source_transition();
  publish_owner6_calibration_envelope();
  return;
}

void return_only_stub_bb734(void)

{
  return;
}

uint reduce_thermal_current_requests(void)

{
  int iVar1;
  uint uVar2;
  uint uVar3;
  uint uVar4;
  
  uVar4 = 0x569a;
  uVar3 = 0;
  do {
    if ((((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xaf0ccu + (uint32_t)(uVar3 >> 5) * 4u)))) >> (uVar3 & 0x1f) & 1) != 0) &&
       ((int)((ushort)(*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebebd34u + (uint32_t)(uVar3) * 2u)))) - uVar4) < 0)) {
      uVar4 = (uint)(ushort)(*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebebd34u + (uint32_t)(uVar3) * 2u))));
    }
    uVar2 = uVar3 + 1;
    iVar1 = uVar3 - 9;
    uVar3 = uVar2;
  } while (iVar1 < 0 != ((int)uVar2 < 0 && -1 < iVar1));
  return uVar4;
}

uint reduce_other_current_requests(void)

{
  int iVar1;
  uint uVar2;
  uint uVar3;
  uint uVar4;
  
  uVar4 = 0x569a;
  uVar3 = 0;
  do {
    if ((((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xaf0ccu + (uint32_t)(uVar3 >> 5) * 4u)))) >> (uVar3 & 0x1f) & 1) == 0) &&
       ((int)((ushort)(*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebebd34u + (uint32_t)(uVar3) * 2u)))) - uVar4) < 0)) {
      uVar4 = (uint)(ushort)(*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebebd34u + (uint32_t)(uVar3) * 2u))));
    }
    uVar2 = uVar3 + 1;
    iVar1 = uVar3 - 9;
    uVar3 = uVar2;
  } while (iVar1 < 0 != ((int)uVar2 < 0 && -1 < iVar1));
  return uVar4;
}

uint reduce_service_current_requests(void)

{
  int iVar1;
  uint uVar2;
  uint uVar3;
  uint uVar4;
  
  uVar4 = 0x569a;
  uVar3 = 0;
  do {
    if (((service_current_owner_exclusions >> (uVar3 & 0x1f) & 1) == 0) &&
       ((int)((ushort)(*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebebd34u + (uint32_t)(uVar3) * 2u)))) - uVar4) < 0)) {
      uVar4 = (uint)(ushort)(*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebebd34u + (uint32_t)(uVar3) * 2u))));
    }
    uVar2 = uVar3 + 1;
    iVar1 = uVar3 - 9;
    uVar3 = uVar2;
  } while (iVar1 < 0 != ((int)uVar2 < 0 && -1 < iVar1));
  return uVar4;
}

void return_only_stub_bb7f6(void)

{
  return;
}

void return_only_stub_bb7f8(void)

{
  return;
}

undefined4 publish_other_current_limit(void)

{
  int iVar1;
  char cVar2;
  short sVar3;
  undefined1 uVar4;
  uint32_t puVar5;
  uint uVar6;
  undefined4 uVar7;
  int iVar8;
  undefined1 uVar9;
  short sVar10;
  int iVar11;
  
  sVar3 = ((int)(int16_t)DAT_febebd46);
  sVar10 = ((int)(int16_t)DAT_febebd40);
  cVar2 = DAT_febeb37c;
  puVar5 = 0xfebeb800u;
  iVar11 = (int)((int)(int16_t)DAT_febebd40);
  iVar8 = (int)((int)(int16_t)DAT_febebd46);
  if (((((DAT_febeb11a & 0xff00) == 0x500) && (DAT_febeb37c == 'Z')) && (DAT_febeb20e != '\x11')) &&
     (DAT_febeb20e != '\"')) {
    uVar6 = reduce_service_current_requests();
    uVar9 = 0x11;
  }
  else {
    uVar6 = reduce_other_current_requests();
    uVar9 = 0;
  }
  uVar4 = 3;
  if (uVar6 != 0x569a) {
    uVar4 = uVar6 != 0;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x8c4))))) = uVar4;
  iVar1 = iVar8 - iVar11;
  if (iVar1 < 0 != (iVar8 < 0 != iVar11 < 0 && iVar11 < 0 == iVar1 < 0)) {
    sVar10 = sVar3;
  }
  uVar7 = raise_priority_mask_and_return_previous_d1da0(0xff80);
  (*((short *)camry_host_ptr((uint32_t)(puVar5 + -0x8c0)))) = (short)uVar6;
  (*((short *)camry_host_ptr((uint32_t)(puVar5 + -0x8be)))) = sVar10;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x8c3))))) = cVar2;
  restore_priority_mask_preserving_interrupt_enable_d1dc6(uVar7);
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x8c2))))) = uVar9;
  return uVar7;
}

void return_only_stub_bb878(void)

{
  return;
}

void reset_bd48_flags_and_seed_569a_bounds_bb87a(void)

{
  DAT_febebd48 = 0;
  DAT_febebd4a = 0;
  DAT_febebd4c = 0x569a;
  DAT_febebd4e = 0x569a;
  return;
}

void return_only_stub_bb95c(void)

{
  return;
}

int reset_bd54_bd55_and_bd90_when_query_zero_bb95e(void)

{
  uint32_t puVar1;
  int iVar2;
  
  puVar1 = 0xfebeb800u;
  iVar2 = thunk_test_redundant_status_a5_or_vote_error13_588b6();
  if (iVar2 == 0) {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x554))))) = 0;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x555))))) = 0;
    (*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + 0x590)))) = 0x7fff;
  }
  return iVar2;
}

uint32_t load_nvm_six_validated_bd7e_halfword_bb97c(void)

{
  uint32_t camry_r10_result;
  uint8_t stack_record_3c[60];
  undefined1 uVar1;
  undefined4 *puVar2;
  uint32_t puVar3;
  int iVar4;
  undefined4 uVar5;
  undefined4 *puVar6;
  
  puVar3 = 0xfebeb800u;
  puVar2 = ((uint32_t *)(stack_record_3c));
  puVar6 = ((undefined *)camry_host_ptr(0x1be3cu));
  do {
    uVar5 = *puVar6;
    puVar6 = puVar6 + 1;
    *puVar2 = uVar5;
    puVar2 = puVar2 + 1;
  } while (camry_host_addr(puVar6)!=((uint32_t)(0x1be74u)));
  iVar4 = (camry_r10_result = call_nvm_get_record_with_u16_selector_ff0b0(6,((uint32_t *)(stack_record_3c))));
  if ((iVar4 == 0x10) && ((((*((int16_t *)(stack_record_3c + 50))) == 0 || ((*((int16_t *)(stack_record_3c + 50))) == -1)) && ((*((int16_t *)(stack_record_3c + 48))) != 0x7f80)))) {
    uVar1 = 0x5a;
  }
  else {
    (*((int16_t *)(stack_record_3c + 48))) = 0x7f80;
    uVar1 = 0;
  }
  (*((short *)camry_host_ptr((uint32_t)(puVar3 + 0x57e)))) = (*((int16_t *)(stack_record_3c + 48)));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(0x556))))) = uVar1;
  return camry_r10_result;
}

void initialize_bd54_decay_from_admitted_offset_gap_bb9d8(char *param_1,int *param_2,short *param_3)

{
  char cVar1;
  uint32_t puVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  int iVar6;
  int iVar7;
  short sVar8;
  short sVar9;
  int local_1c;
  
  puVar2 = 0xfebeb800u;
  cVar1 = *param_1;
  iVar7 = *param_2;
  (*((uint16_t *)((uint8_t *)&local_1c + 0u))) = *param_3;
  sVar8 = ((int)(int16_t)DAT_febebd5c);
  if (cVar1 == '\0') {
    iVar5 = (int)((int)(int16_t)DAT_febebd7e);
    iVar6 = (int)conditioned_offset_scalar;
    iVar3 = (int)((int)(int16_t)DAT_febef17c);
    sVar9 = 0;
    if (DAT_febebd58 <= DAT_000aee38) {
      if ((((DAT_febef1e0 != 0) || (1 < published_internal_source_admission_state)) ||
          (DAT_febebe58 != '\0')) ||
         ((iVar4 = (int)(int16_t)DAT_000aee3a,
          iVar6 - iVar4 < 0 == (iVar6 < 0 != iVar4 < 0 && iVar4 < 0 == iVar6 - iVar4 < 0) &&
          iVar6 != iVar4 ||
          (iVar4 = (int)(int16_t)DAT_000aee3c,
          iVar6 - iVar4 < 0 != (iVar6 < 0 != iVar4 < 0 && iVar4 < 0 == iVar6 - iVar4 < 0))))) {
        sVar9 = DAT_febebd58 + 1;
        goto LAB_000bba8c;
      }
      if ((DAT_febebd56 == 'Z') &&
         (iVar3 - iVar5 < 0 == (iVar3 < 0 != iVar5 < 0 && iVar5 < 0 == iVar3 - iVar5 < 0) &&
          iVar3 != iVar5)) {
        iVar4 = (int)(int16_t)DAT_000aee3e;
        iVar6 = iVar3 - iVar6;
        if (iVar6 - iVar4 < 0 == (iVar6 < 0 != iVar4 < 0 && iVar4 < 0 == iVar6 - iVar4 < 0) &&
            iVar6 != iVar4) {
          local_1c = iVar3 - iVar5;
          puVar2 = 0xfebeb800u;
          store_signed32_minimum_d1d4e(local_1c,32000,&local_1c);
          cVar1 = '\x11';
          iVar7 = DAT_000aee50 * (short)local_1c;
          sVar8 = (short)local_1c;
          goto LAB_000bba8c;
        }
      }
    }
    sVar8 = 0;
    cVar1 = 'D';
  }
  else {
    sVar9 = 0;
  }
LAB_000bba8c:
  *param_1 = cVar1;
  *param_3 = (short)local_1c;
  *param_2 = iVar7;
  (*((short *)camry_host_ptr((uint32_t)(puVar2 + 0x558)))) = sVar9;
  (*((short *)camry_host_ptr((uint32_t)(puVar2 + 0x55c)))) = sVar8;
  return;
}

void decrement_decay_accumulator_until_aee40_threshold_bbaa4(char *param_1,int *param_2,short *param_3)

{
  short sVar1;
  int iVar3;
  char cVar4;
  int iVar5;
  int iVar2;
  
  cVar4 = *param_1;
  if (cVar4 == '\x11') {
    iVar5 = *param_2 - (int)*param_3;
    iVar2 = iVar5;
    if (DAT_000aee50 != 0) {
      if (iVar5 == -0x80000000 && DAT_000aee50 == -1) {
        iVar2 = 0;
      }
      else {
        iVar2 = (int)iVar5 / (int)DAT_000aee50;
      }
    }
    iVar3 = (int)DAT_000aee40;
    sVar1 = (short)iVar2;
    iVar2 = (int)sVar1;
    if (iVar2 - iVar3 < 0 != (iVar2 < 0 != iVar3 < 0 && iVar3 < 0 == iVar2 - iVar3 < 0) ||
        iVar2 == iVar3) {
      iVar5 = 0;
      sVar1 = 0;
      cVar4 = '\"';
    }
  }
  else {
    iVar5 = 0;
    sVar1 = 0;
  }
  *param_1 = cVar4;
  *param_2 = iVar5;
  *param_3 = sVar1;
  return;
}

void update_bd54_decay_state_accumulator_and_output_bbaea(void)

{
  uint8_t stack_record_b[11];
  uint32_t puVar1;
  
  puVar1 = 0xfebeb800u;
  stack_record_b[0] = DAT_febebd54;
  (*((uint32_t *)(stack_record_b + 3))) = DAT_febebd88;
  (*((uint16_t *)(stack_record_b + 1))) = ((int)(int16_t)DAT_febebd5e);
  initialize_bd54_decay_from_admitted_offset_gap_bb9d8(((uint8_t *)(stack_record_b)),((uint32_t *)((stack_record_b + 3))),((uint16_t *)((stack_record_b + 1))));
  decrement_decay_accumulator_until_aee40_threshold_bbaa4(((uint8_t *)(stack_record_b)),((uint32_t *)((stack_record_b + 3))),((uint16_t *)((stack_record_b + 1))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x554))))) = stack_record_b[0];
  (*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + 0x588)))) = (*((uint32_t *)(stack_record_b + 3)));
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + 0x55e)))) = (*((uint16_t *)(stack_record_b + 1)));
  return;
}

void advance_bd84_table_and_scale_by_aee34_bbb3c(void)

{
  byte bVar1;
  uint32_t puVar2;
  short sVar3;
  short sStack_a;
  
  puVar2 = 0xfebeb800u;
  if (DAT_febebd84 < 0x927c) {
    sVar3 = DAT_febebd84 + 1;
  }
  else {
    sVar3 = -0x6d84;
  }
  interpolate_unsigned16_axis_signed16_values_to_output_d1e8c(((undefined *)camry_host_ptr(0xaee60u)),sVar3,&sStack_a);
  bVar1 = DAT_000aee34;
  (*((short *)camry_host_ptr((uint32_t)(puVar2 + 0x584)))) = sVar3;
  (*((short *)camry_host_ptr((uint32_t)(puVar2 + 0x560)))) = sStack_a;
  (*((short *)camry_host_ptr((uint32_t)(puVar2 + 0x562)))) = (short)(((int)(short)(ushort)bVar1 * (int)sStack_a) / 0x80);
  return;
}

void compute_f178_f17a_sum_table_residual_bbb88(void)

{
  uint8_t stack_record_12[18];
  int iVar1;
  uint32_t puVar2;
  
  puVar2 = 0xfebeb800u;
  iVar1 = (int)((int)(int16_t)DAT_febef17a) + (int)((int)(int16_t)DAT_febef178);
  store_signed32_clamped_between_upper_and_lower_d1cf6(iVar1,0x7fff,(int)0xffff8001,((int16_t *)((stack_record_12 + 2))));
  interpolate_signed16_pairs_to_output_d1de4(((undefined *)camry_host_ptr(0xaee7cu)),(int)((int16_t *)((stack_record_12 + 2)))[0],((int16_t *)(stack_record_12)));
  (*((int32_t *)(stack_record_12 + 6))) = (int)((iVar1 - (*((int16_t *)(stack_record_12 + 0)))) * (uint)DAT_000aee35) / 0x80;
  store_signed32_clamped_between_upper_and_lower_d1cf6((*((int32_t *)(stack_record_12 + 6))),32000,(int)0xffffe700,((int32_t *)((stack_record_12 + 6))));
  (*((int *)camry_host_ptr((uint32_t)(puVar2 + 0x58c)))) = iVar1;
  (*((short *)camry_host_ptr((uint32_t)(puVar2 + 0x564)))) = (*((int16_t *)(stack_record_12 + 0)));
  (*((short *)camry_host_ptr((uint32_t)(puVar2 + 0x566)))) = (short)(*((int32_t *)(stack_record_12 + 6)));
  return;
}

void update_bd90_filtered_residual_and_bounded_bd7e_bbbfc(void)

{
  uint8_t stack_record_34[52];
  char cVar1;
  int iVar2;
  short sVar3;
  uint32_t puVar4;
  int iVar5;
  int iVar6;
  int iVar7;
  int iVar8;
  int iVar9;
  int iVar10;
  int iVar11;
  
  iVar11 = DAT_febebd90;
  iVar2 = DAT_febebd8c;
  cVar1 = DAT_febebd54;
  puVar4 = 0xfebeb800u;
  (*((int32_t *)(stack_record_34 + 8))) = (int)((int)(int16_t)DAT_febebd5a);
  iVar8 = (int)((int)(int16_t)DAT_febebd5e);
  iVar7 = (int)((int)(int16_t)DAT_febebd62);
  (*((int32_t *)(stack_record_34 + 12))) = (int)((int)(int16_t)DAT_febebd7e);
  iVar6 = (int)((int)(int16_t)DAT_febebd64);
  iVar10 = (int)((int)(int16_t)DAT_febebd6a);
  (*((int32_t *)(stack_record_34 + 0))) = (int)((int)(int16_t)DAT_febef17c) - (int)((int)(int16_t)DAT_febebd66);
  store_signed32_clamped_between_upper_and_lower_d1cf6((*((int32_t *)(stack_record_34 + 0))),32000,(int)0xffffe700,((int32_t *)(stack_record_34)));
  sVar3 = (short)(*((int32_t *)(stack_record_34 + 0)));
  iVar9 = (int)(short)(*((int32_t *)(stack_record_34 + 0)));
  iVar5 = iVar11;
  if (DAT_000aee54 != 0) {
    if (iVar11 == -0x80000000 && DAT_000aee54 == -1) {
      iVar5 = 0;
    }
    else {
      iVar5 = (int)iVar11 / (int)DAT_000aee54;
    }
  }
  if ((short)iVar5 != iVar10) {
    iVar11 = iVar9 * DAT_000aee54;
    iVar10 = iVar9;
  }
  iVar10 = (iVar11 + iVar9) - iVar10;
  iVar11 = iVar10;
  if (DAT_000aee54 != 0) {
    if (iVar10 == -0x80000000 && DAT_000aee54 == -1) {
      iVar11 = 0;
    }
    else {
      iVar11 = (int)iVar10 / (int)DAT_000aee54;
    }
  }
  (*((int32_t *)(stack_record_34 + 4))) = (int)DAT_000aee42 + (((short)iVar11 - iVar7) - iVar8);
  if (cVar1 != '\0') {
    (*((int32_t *)(stack_record_34 + 8))) = (int)((iVar6 + iVar2) * (uint)DAT_000aee36) / 0x80;
    (*((int32_t *)(stack_record_34 + 12))) = (*((int32_t *)(stack_record_34 + 8))) + (*((int32_t *)(stack_record_34 + 4)));
    store_signed32_clamped_between_upper_and_lower_d1cf6((*((int32_t *)(stack_record_34 + 8))),32000,(int)0xffffe700,((int32_t *)((stack_record_34 + 8))));
    store_signed32_clamped_between_upper_and_lower_d1cf6((*((int32_t *)(stack_record_34 + 12))),32000,(int)0xffffe700,((int32_t *)((stack_record_34 + 12))));
  }
  store_signed32_clamped_between_upper_and_lower_d1cf6((*((int32_t *)(stack_record_34 + 4))),32000,(int)0xffffe700,((int32_t *)((stack_record_34 + 4))));
  (*((short *)camry_host_ptr((uint32_t)(puVar4 + 0x568)))) = sVar3;
  (*((int *)camry_host_ptr((uint32_t)(puVar4 + 0x590)))) = iVar10;
  (*((short *)camry_host_ptr((uint32_t)(puVar4 + 0x56a)))) = (short)iVar11;
  (*((short *)camry_host_ptr((uint32_t)(puVar4 + 0x56c)))) = (short)(*((int32_t *)(stack_record_34 + 4)));
  (*((short *)camry_host_ptr((uint32_t)(puVar4 + 0x55a)))) = (short)(*((int32_t *)(stack_record_34 + 8)));
  (*((short *)camry_host_ptr((uint32_t)(puVar4 + 0x57e)))) = (short)(*((int32_t *)(stack_record_34 + 12)));
  return;
}

void run_init_chain_bbcea(void)

{
  update_bd54_decay_state_accumulator_and_output_bbaea();
  advance_bd84_table_and_scale_by_aee34_bbb3c();
  compute_f178_f17a_sum_table_residual_bbb88();
  update_bd90_filtered_residual_and_bounded_bd7e_bbbfc();
  return;
}

void debounce_offset_gap_and_latch_bd51_state_22_bbd02(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  
  iVar1 = (int)((int)(int16_t)DAT_febebd6c);
  iVar4 = (int)conditioned_offset_scalar;
  if (DAT_febebd51 != '\"') {
    if ((((((DAT_febebd54 == '\0') || (DAT_febef1e0 != 0)) ||
          (1 < published_internal_source_admission_state)) ||
         ((DAT_febebe58 != '\0' ||
          (iVar3 = (int)DAT_000aee44,
          iVar4 - iVar3 < 0 == (iVar4 < 0 != iVar3 < 0 && iVar3 < 0 == iVar4 - iVar3 < 0) &&
          iVar4 != iVar3)))) ||
        ((iVar2 = (int)DAT_000aee3c,
         iVar4 - iVar2 < 0 != (iVar4 < 0 != iVar2 < 0 && iVar2 < 0 == iVar4 - iVar2 < 0) ||
         ((iVar1 - iVar3 < 0 == (iVar1 < 0 != iVar3 < 0 && iVar3 < 0 == iVar1 - iVar3 < 0) &&
           iVar1 != iVar3 || (DAT_febebe89 != '\0')))))) ||
       ((1 < DAT_febef053 || ((DAT_febef093 != '\0' || (DAT_febef013 != '\0')))))) {
      DAT_febebd51 = '\0';
    }
    else {
      iVar1 = (int)DAT_000aee46;
      iVar4 = iVar4 - ((int)(int16_t)DAT_febef17c);
      if (iVar4 - iVar1 < 0 == (iVar4 < 0 != iVar1 < 0 && iVar1 < 0 == iVar4 - iVar1 < 0) &&
          iVar4 != iVar1) {
        if (DAT_febebd6e < DAT_000aee48) {
          DAT_febebd6e = DAT_febebd6e + 1;
        }
        else {
          DAT_febebd51 = '\"';
          DAT_febebd6e = 0;
        }
      }
      else {
        DAT_febebd51 = '\x11';
        DAT_febebd6e = 0;
      }
    }
  }
  return;
}

void select_four_tables_and_filter_bd70_into_bd72_bbd9c(void)

{
  int iVar1;
  int iVar2;
  uint32_t puVar3;
  undefined *puVar4;
  int iVar5;
  short sStack_e;
  
  iVar2 = DAT_febebd94;
  puVar3 = 0xfebeb800u;
  iVar5 = (int)((int)(int16_t)DAT_febebd72);
  if (((published_internal_source_admission_state < 2) && (DAT_febebe89 == '\0')) &&
     (DAT_febef053 < 2)) {
    if (DAT_febebe88 == '\0') {
      if (DAT_febef053 == 0) {
        puVar4 = ((undefined *)camry_host_ptr(0xaee90u));
      }
      else {
        puVar4 = ((undefined *)camry_host_ptr(0xaeeacu));
      }
    }
    else if (DAT_febef053 == 0) {
      puVar4 = ((undefined *)camry_host_ptr(0xaeec8u));
    }
    else {
      puVar4 = ((undefined *)camry_host_ptr(0xaeee4u));
    }
    puVar3 = 0xfebeb800u;
    interpolate_unsigned16_axis_signed16_values_to_output_d1e8c(puVar4,DAT_febebee2,&sStack_e);
  }
  else {
    sStack_e = 0;
  }
  iVar1 = DAT_000aee58;
  (*((short *)camry_host_ptr((uint32_t)(puVar3 + 0x570)))) = sStack_e;
  iVar5 = (sStack_e + iVar2) - iVar5;
  (*((int *)camry_host_ptr((uint32_t)(puVar3 + 0x594)))) = iVar5;
  if (iVar1 != 0) {
    if (iVar5 == -0x80000000 && iVar1 == -1) {
      iVar5 = 0;
    }
    else {
      iVar5 = (int)iVar5 / (int)iVar1;
    }
  }
  (*((short *)camry_host_ptr((uint32_t)(puVar3 + 0x572)))) = (short)iVar5;
  return;
}

void detect_b1a7_rise_or_bcb0_resume_pulse_bbe26(void)

{
  if ((DAT_febeb1a7 == DAT_febebd50) || (DAT_febeb1a7 != 'Z')) {
    DAT_febebd52 = '\0';
  }
  else {
    DAT_febebd52 = 'Z';
  }
  if (((DAT_febebcb0 == 0) && (DAT_febeb1bc == 'Z')) && (DAT_febebd53 == '\0')) {
    DAT_febebd53 = 'Z';
  }
  if (DAT_febebd52 != 'Z') {
    if ((DAT_febebcb0 == 0) || (DAT_febebd53 != 'Z')) {
      DAT_febebd52 = '\0';
    }
    else {
      DAT_febebd53 = '\0';
      DAT_febebd52 = 'Z';
    }
  }
  DAT_febebd50 = DAT_febeb1a7;
  return;
}

undefined4 filter_and_slew_limit_offset_table_outputs_bbe7a(void)

{
  uint8_t stack_record_28[40];
  char cVar1;
  char cVar2;
  short sVar3;
  uint32_t puVar4;
  undefined4 uVar5;
  int iVar6;
  int iVar7;
  short sVar8;
  int iVar9;
  int iVar10;
  
  iVar10 = DAT_febebd98;
  cVar2 = DAT_febebd52;
  cVar1 = DAT_febebd51;
  puVar4 = 0xfebeb800u;
  iVar7 = (int)conditioned_offset_scalar;
  (*((int16_t *)(stack_record_28 + 6))) = ((int)(int16_t)DAT_febebd7a);
  iVar9 = (int)((int)(int16_t)DAT_febebd7c);
  (*((int16_t *)(stack_record_28 + 2))) = ((int)(int16_t)DAT_febebd80);
  (*((int32_t *)(stack_record_28 + 8))) = (int)((int)(int16_t)DAT_febebd6c) - (int)((int)(int16_t)DAT_febebd72);
  store_signed32_clamped_between_upper_and_lower_d1cf6((*((int32_t *)(stack_record_28 + 8))),32000,(int)0xffffe700,((int32_t *)((stack_record_28 + 8))));
  sVar3 = (short)(*((int32_t *)(stack_record_28 + 8)));
  iVar6 = (int)(short)(*((int32_t *)(stack_record_28 + 8)));
  if (iVar6 - iVar7 < 0 == (iVar6 < 0 != iVar7 < 0 && iVar7 < 0 == iVar6 - iVar7 < 0) &&
      iVar6 != iVar7) {
    iVar7 = iVar6;
  }
  if (cVar1 == '\x11') {
    interpolate_signed16_pairs_to_output_d1de4(((undefined *)camry_host_ptr(0xaef00u)),iVar7,((int16_t *)(stack_record_28)));
  }
  else {
    (*((int16_t *)(stack_record_28 + 0))) = 0;
  }
  sVar8 = (*((int16_t *)(stack_record_28 + 0)));
  iVar6 = (int)(*((int16_t *)(stack_record_28 + 0)));
  if (cVar2 == 'Z') {
    store_signed16_clamped_between_upper_and_lower_d1cdc(iVar6,(int)DAT_000aee4a,(int)DAT_000aee4c,((int16_t *)((stack_record_28 + 2))));
    iVar9 = (DAT_000aee5c * iVar6) / 0x400;
  }
  else {
    iVar9 = (iVar10 + iVar6) - iVar9;
    iVar10 = iVar9 * 0x400;
    if (DAT_000aee5c != 0) {
      if (iVar10 == -0x80000000 && DAT_000aee5c == -1) {
        iVar10 = 0;
      }
      else {
        iVar10 = iVar10 / (int)DAT_000aee5c;
      }
    }
    sVar8 = (short)iVar10;
    store_signed16_clamped_between_upper_and_lower_d1cdc((int)sVar8,(int)DAT_000aee4a,(int)DAT_000aee4c,((int16_t *)((stack_record_28 + 6))));
    store_signed16_clamped_between_upper_and_lower_d1cdc((int)(*((int16_t *)(stack_record_28 + 6))),(int)(short)(DAT_000aee4e + (*((int16_t *)(stack_record_28 + 2)))),
                 (int)(short)((*((int16_t *)(stack_record_28 + 2))) - DAT_000aee4e),((int16_t *)((stack_record_28 + 2))));
  }
  interpolate_signed16_pairs_to_output_d1de4(((undefined *)camry_host_ptr(0xaef1cu)),iVar7,((uint16_t *)((stack_record_28 + 4))));
  (*((short *)camry_host_ptr((uint32_t)(puVar4 + 0x574)))) = sVar3;
  (*((short *)camry_host_ptr((uint32_t)(puVar4 + 0x576)))) = (short)iVar7;
  (*((short *)camry_host_ptr((uint32_t)(puVar4 + 0x57c)))) = sVar8;
  (*((short *)camry_host_ptr((uint32_t)(puVar4 + 0x57a)))) = (*((int16_t *)(stack_record_28 + 6)));
  (*((int *)camry_host_ptr((uint32_t)(puVar4 + 0x598)))) = iVar9;
  (*((short *)camry_host_ptr((uint32_t)(puVar4 + 0x578)))) = (*((int16_t *)(stack_record_28 + 0)));
  uVar5 = raise_priority_mask_and_return_previous_d1da0(0xffc0);
  (*((short *)camry_host_ptr((uint32_t)(puVar4 + 0x580)))) = (*((int16_t *)(stack_record_28 + 2)));
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar4 + 0x582)))) = (*((uint16_t *)(stack_record_28 + 4)));
  restore_priority_mask_preserving_interrupt_enable_d1dc6(uVar5);
  return uVar5;
}

uint32_t run_bd54_offset_pipeline_with_first_read_bbf8a(void)

{
  uint32_t camry_r10_result;
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  if (DAT_febebd55 == '\0') {
    puVar1 = 0xfebeb800u;
    (camry_r10_result = load_nvm_six_validated_bd7e_halfword_bb97c());
  }
  run_init_chain_bbcea();
  debounce_offset_gap_and_latch_bd51_state_22_bbd02();
  select_four_tables_and_filter_bd70_into_bd72_bbd9c();
  detect_b1a7_rise_or_bcb0_resume_pulse_bbe26();
  (camry_r10_result = filter_and_slew_limit_offset_table_outputs_bbe7a());
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x555))))) = 0x5a;
  return camry_r10_result;
}

void return_only_stub_bbfba(void)

{
  return;
}

void reset_owner3_shutdown_request(void)

{
  DAT_febebd9e = 0x569a;
  DAT_febebd9c = 0;
  DAT_febebd9d = 0;
  DAT_febebda0 = 0;
  DAT_febebda4 = 0x569a0000;
  return;
}

void publish_owner3_shutdown_request(void)

{
  int iVar1;
  ushort uVar2;
  uint32_t puVar3;
  int iVar4;
  undefined1 uVar5;
  ushort uVar6;
  uint uVar7;
  char cVar8;
  int iVar9;
  ushort limit;
  int iVar10;
  int iVar11;
  
  iVar11 = DAT_febebda4;
  uVar2 = DAT_febebda0;
  cVar8 = DAT_febebd9d;
  limit = DAT_000af10c;
  uVar6 = DAT_000af108;
  puVar3 = 0xfebeb800u;
  iVar1 = (int)(DAT_febebda4) / (int)0x10000;
  if (DAT_febebda9 == '\x01') {
    iVar10 = (int)(short)DAT_febebd9e;
    iVar4 = (int)((int)(int16_t)DAT_febebccc);
    if (DAT_febebda8 != '\x01') {
      puVar3 = 0xfebeb800u;
      report_diagnostic_event_pass(0xa1);
      uVar2 = (*((ushort *)camry_host_ptr((uint32_t)(puVar3 + 0x5a0))));
      limit = DAT_000af10c;
      goto LAB_000bc074;
    }
    uVar7 = (uint)DAT_000af108;
    uVar5 = 1;
    iVar9 = DAT_febebda4;
    limit = ((int)(int16_t)DAT_febebd9e);
    if (DAT_febeb084 < DAT_000af114) {
      puVar3 = 0xfebeb800u;
      report_diagnostic_event_failure(0xa1,0x32);
      if ((short)iVar1 != iVar10) {
        iVar11 = iVar4 << 0x10;
        iVar10 = iVar4;
      }
      if ((uVar7 * 0x32 == 0) || (0xffff < uVar7 * 0x32)) {
        iVar10 = iVar10 << 0x10;
        iVar9 = (int)DAT_000af10a << 0x10;
      }
      else {
        iVar10 = iVar10 * uVar7 * 0x32;
        iVar9 = (int)DAT_000af10a * uVar7 * 0x32;
      }
      iVar9 = (iVar11 - iVar10) + iVar9;
      limit = (ushort)(iVar9 / 0x10000);
      iVar11 = (int)(short)limit;
      thunk_increment_indexed_u16_counter_once_until_rearmed_545de(4);
      thunk_gate_indexed_event_payload_during_diagnostic_clears_51cf6(2,0x32);
      iVar1 = DAT_000af10e - iVar11;
      if ((iVar1 < 0 != (DAT_000af10e < 0 != iVar11 < 0 && iVar11 < 0 == iVar1 < 0)) ||
         (cVar8 != '\0')) goto LAB_000bc0ca;
      cVar8 = '\x01';
      iVar9 = 0;
      limit = 0;
LAB_000bc0ce:
      uVar7 = 0x70017001;
      goto LAB_000bc0d4;
    }
LAB_000bc0ca:
    if (cVar8 == '\x01') goto LAB_000bc0ce;
  }
  else {
    puVar3 = 0xfebeb800u;
    report_diagnostic_event_pass(0xa1);
LAB_000bc074:
    uVar5 = 0;
    iVar9 = 0;
    uVar6 = uVar2;
    if (cVar8 == '\x01') {
      cVar8 = '\0';
    }
  }
  uVar7 = 0;
LAB_000bc0d4:
  set_output_request_word('\x03',uVar7);
  set_current_limit_request(3,limit);
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(0x59c))))) = uVar5;
  (*((ushort *)camry_host_ptr((uint32_t)(puVar3 + 0x59e)))) = limit;
  (*((ushort *)camry_host_ptr((uint32_t)(puVar3 + 0x5a0)))) = uVar6;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(0x59d))))) = cVar8;
  (*((int *)camry_host_ptr((uint32_t)(puVar3 + 0x5a4)))) = iVar9;
  return;
}
