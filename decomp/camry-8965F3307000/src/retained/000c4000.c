#include "common.h"

void run_init_chain_c4046(void)

{
  apply_estimator_center_reseed();
  apply_estimator_acquisition_reset();
  run_init_chain_c3292();
  update_secondary_estimator_stability();
  return;
}

void refresh_estimator_tracking_qualifiers(void)

{
  refresh_estimator_qualifier_thresholds();
  qualify_estimator_source_stability();
  qualify_estimator_paired_sources();
  qualify_estimator_source_constraints();
  return;
}

uint predict_estimator_source_sample(ushort *warmup,uchar *accepted,int *projection)

{
  int iVar1;
  int iVar2;
  ushort uVar3;
  int iVar4;
  short sVar5;
  short sVar6;
  ushort uVar7;
  int iVar8;
  char cVar9;
  char cVar10;
  char cVar11;
  char cVar12;
  char cVar13;
  uint32_t puVar14;
  short sVar15;
  short sVar16;
  uint uVar17;
  int iVar18;
  uchar uVar19;
  int iVar20;
  ushort uVar21;
  
  cVar13 = DAT_febebff0;
  cVar12 = DAT_febebfc5;
  cVar11 = DAT_febebfc4;
  cVar10 = DAT_febebfb7;
  cVar9 = DAT_febebfaf;
  sVar16 = ((int)(int16_t)DAT_febebf98);
  iVar2 = DAT_febebf7c;
  iVar8 = DAT_febebf70;
  uVar21 = DAT_febeae38;
  sVar6 = DAT_000af776;
  sVar5 = DAT_000af774;
  puVar14 = 0xfebeb800u;
  iVar20 = *projection;
  uVar19 = *accepted;
  uVar3 = *warmup;
  sVar15 = abs_s16_wrapping(((int)(int16_t)DAT_febebf9c));
  sVar16 = abs_s16_wrapping(sVar16);
  iVar1 = iVar2 - iVar8;
  uVar17 = abs_s32_wrapping(iVar1);
  iVar4 = DAT_000af768;
  (*((int *)camry_host_ptr((uint32_t)(puVar14 + 0x858)))) = iVar1;
  uVar7 = DAT_000af778;
  if (((((cVar12 == '\0') && (cVar11 == '\0')) && (cVar9 == 'Z')) &&
      ((cVar13 == 'Z' &&
       (iVar18 = (int)sVar5, iVar1 = sVar15 - iVar18,
       iVar1 < 0 != (sVar15 < 0 != iVar18 < 0 && iVar18 < 0 == iVar1 < 0))))) &&
     ((iVar18 = (int)sVar6, iVar1 = sVar16 - iVar18,
      iVar1 < 0 != (sVar16 < 0 != iVar18 < 0 && iVar18 < 0 == iVar1 < 0) &&
      ((cVar10 == 'Z' && (uVar17 < iVar4 * (uint)uVar21 >> 10)))))) {
    uVar21 = uVar3 + 1;
    if ((DAT_000af778 < (ushort)(uVar3 + 1)) && (uVar21 = uVar7, (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar14 + (uint32_t)(0x8de))))) == 'Z')) {
      iVar2 = iVar2 - (((*((int *)camry_host_ptr((uint32_t)(puVar14 + 0x778)))) - (*((int *)camry_host_ptr((uint32_t)(puVar14 + 0x7d4))))) - iVar8);
      (*((int *)camry_host_ptr((uint32_t)(puVar14 + 0x7d8)))) = iVar2;
      iVar20 = (*((int *)camry_host_ptr((uint32_t)(puVar14 + 0x880)))) + iVar2;
      uVar19 = 'Z';
    }
  }
  else {
    uVar21 = 0;
  }
  *warmup = uVar21;
  *accepted = uVar19;
  *projection = iVar20;
  return uVar17;
}

void update_estimator_source_projection(void)

{
  uint8_t stack_record_b[11];
  uint32_t puVar1;
  
  puVar1 = 0xfebeb800u;
  (*((uint16_t *)(stack_record_b + 1))) = DAT_febec068;
  stack_record_b[0] = DAT_febebff1;
  (*((int32_t *)(stack_record_b + 3))) = DAT_febec07c;
  if (((DAT_febead3c == '\0') || (DAT_febead3c == '\x03')) ||
     ((DAT_febead3c == '\x02' &&
      (((DAT_febead3e == '\x01' && (DAT_febead25 == '\0')) && (DAT_febead27 == '\x01')))))) {
    stack_record_b[0] = '\0';
    (*((uint16_t *)(stack_record_b + 1))) = 0;
    DAT_febebffa = 0;
  }
  else if (DAT_febebff1 == 'Z') {
    (*((int32_t *)(stack_record_b + 3))) = DAT_febec080 + DAT_febebfd8;
  }
  else {
    puVar1 = 0xfebeb800u;
    predict_estimator_source_sample((stack_record_b + 1),stack_record_b,(stack_record_b + 3));
  }
  (*((ushort *)camry_host_ptr((uint32_t)(puVar1 + 0x868)))) = (*((uint16_t *)(stack_record_b + 1)));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x7f1))))) = stack_record_b[0];
  (*((int *)camry_host_ptr((uint32_t)(puVar1 + 0x87c)))) = (*((int32_t *)(stack_record_b + 3)));
  return;
}

void run_estimator_acquisition_or_tracking(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  refresh_estimator_tracking_qualifiers();
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x7f0))))) == 'Z') {
    track_established_estimator_difference();
  }
  else {
    select_estimator_acquisition_source();
  }
  update_estimator_source_projection();
  return;
}

void classify_estimator_source_band(void)

{
  DAT_febec08a = DAT_febec08e;
  if ((DAT_febead3c != '\0') && (DAT_febead3c != '\x03')) {
    DAT_febec088 = estimator_lower_band_default;
    DAT_febec06a = estimator_upper_band_default;
    if (DAT_febead3c == '\x02') {
      DAT_febec088 = estimator_lower_band_mode2;
      DAT_febec06a = estimator_upper_band_mode2;
    }
    if (DAT_febec088 <= DAT_febebfec) {
      if (DAT_febebfec < DAT_febec06a) {
        DAT_febec06e = 0x11;
        return;
      }
      DAT_febec06e = 0x22;
      return;
    }
  }
  DAT_febec06e = 0;
  return;
}

void follow_estimator_center(void)

{
  int value;
  int iVar1;
  undefined1 uVar2;
  uint32_t puVar3;
  int iVar5;
  int iVar6;
  undefined1 uVar7;
  char cVar8;
  uint32_t puVar4;
  uVar7 = DAT_febec08b;
  iVar6 = DAT_febec080;
  cVar8 = DAT_febec06f;
  uVar2 = DAT_febec06e;
  puVar4 = 0xfebeb800u;
  puVar3 = (0xfebeb800u);
  if ((DAT_febebfc5 == '\0') && (DAT_febebff0 == 'Z')) {
    value = (DAT_febebf78 - DAT_febebfd4) - DAT_febec080;
    if (DAT_febec06f == '\0') {
      cVar8 = 'Z';
      uVar7 = uVar2;
      puVar3 = (0xfebeb800u);
    }
    else {
      iVar5 = abs_s32_wrapping(value);
      iVar1 = (int)(estimator_center_adoption_scale * (uint)(*((ushort *)camry_host_ptr((uint32_t)(puVar4 + -0x9c8))))) /
              0x400;
      puVar3 = ((uint32_t)(puVar4));
      if (iVar5 - iVar1 < 0 != (iVar5 < 0 != iVar1 < 0 && iVar1 < 0 == iVar5 - iVar1 < 0) ||
          iVar5 == iVar1) {
        iVar6 = (*((int *)camry_host_ptr((uint32_t)(puVar4 + 0x84c))));
        uVar7 = uVar2;
      }
    }
    *(int *)(((undefined *)camry_host_ptr((uint32_t)(0xfebeb800u + (uint32_t)(0x85c) * 1u)))) = value;
    (*((volatile undefined *)camry_host_ptr((uint32_t)(0xfebeb800u + (uint32_t)(0x88b) * 1u)))) = uVar7;
    (*((volatile undefined *)camry_host_ptr((uint32_t)(0xfebeb800u + (uint32_t)(0x86f) * 1u)))) = cVar8;
  }
  else {
    iVar6 = 0;
  }
  *(int *)(((undefined *)camry_host_ptr((uint32_t)(0xfebeb800u + (uint32_t)(0x880) * 1u)))) = iVar6;
  return;
}

void run_raw_estimator_cycle(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  run_init_chain_c4046();
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0xaed))))) == 'Z') {
    if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x870))))) == '\0') {
      (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + 0x7f8)))) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x9f2))));
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x7fa))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0xacf)))));
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x870))))) = 0x5a;
    }
    run_estimator_acquisition_or_tracking();
    classify_estimator_source_band();
    follow_estimator_center();
    publish_raw_estimator_state();
  }
  else {
    clear_published_estimator_state();
  }
  return;
}

void sample_rate_observer(F33RateObserverSample *sample)

{
  uint uVar1;
  int iVar2;
  int iVar3;
  uchar uVar4;
  uchar uVar5;
  
  if ((DAT_febead3c != '\0') && (DAT_febead3c != '\x03')) {
    DAT_febec06c = estimator_lower_band_default;
    if (DAT_febead3c == '\x02') {
      DAT_febec06c = estimator_lower_band_mode2;
    }
    if (((DAT_febebfb9 == 'Z') && (DAT_febebfc5 == '\0')) && (DAT_febec06c <= DAT_febec0b4)) {
      iVar2 = DAT_febeaba4 + DAT_febeaba0 * -0x80 + DAT_febeaba8 * -0x80;
      uVar5 = DAT_febec0b7;
      uVar4 = DAT_febec0b6;
      goto LAB_000c4598;
    }
  }
  iVar2 = 0;
  uVar5 = DAT_febec08e;
  uVar4 = DAT_febec08f;
LAB_000c4598:
  uVar1 = ((uint)DAT_febeac12 << 4) / 0x400;
  iVar3 = DAT_febec084;
  if ((uVar1 != 0) && (iVar3 = iVar2 / 8, uVar1 != 0)) {
    if (iVar3 == -0x80000000 && uVar1 == 0xffffffff) {
      iVar3 = -0x80000000;
    }
    else {
      iVar3 = iVar3 / (int)uVar1;
    }
  }
  sample->rate = iVar3;
  sample->qualification = uVar4;
  sample->state = uVar5;
  return;
}

void commit_rate_observer(void)

{
  uint32_t puVar1;
  undefined4 uVar2;
  F33RateObserverSample local_c;
  
  puVar1 = 0xfebeb800u;
  refresh_observer_source_and_debounce_ac01_c330c();
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0xbf9))))) == 'Z') {
    sample_rate_observer(&local_c);
    uVar2 = raise_priority_mask_and_return_previous_d1da0(0xffc0);
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x88f))))) = local_c.qualification;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x88e))))) = local_c.state;
    (*((int *)camry_host_ptr((uint32_t)(puVar1 + 0x884)))) = local_c.rate;
    restore_priority_mask_preserving_interrupt_enable_d1dc6(uVar2);
  }
  return;
}

void initialize_retained_estimator_qualification(void)

{
  DAT_febec094 = 0;
  DAT_febec098 = 0;
  DAT_febec09c = 0;
  DAT_febec0a0 = 0;
  DAT_febec0ac = 0;
  DAT_febec0ad = 0;
  DAT_febec0a4 = 0;
  DAT_febec0a6 = 0;
  DAT_febec0a8 = 0;
  DAT_febec0aa = 0;
  DAT_febec0b0 = 0;
  DAT_febeaba8 = 0;
  DAT_febec0ae = 0;
  DAT_febec0b6 = 0;
  DAT_febec0b7 = 0;
  DAT_febec0b4 = 0;
  return;
}

void check_retained_estimator_consistency(uchar *snapshot)

{
  uchar uVar1;
  undefined1 uVar2;
  uint32_t puVar3;
  int iVar4;
  int iVar5;
  undefined1 uVar6;
  int iVar7;
  int iVar8;
  
  puVar3 = 0xfebeb800u;
  uVar1 = snapshot[6];
  if (((uVar1 != '\0') && (uVar1 != '\x03')) &&
     ((snapshot[10] != '\x02' || (snapshot[0xb] != '\0')))) {
    iVar7 = DAT_000af7e0;
    iVar8 = DAT_000af7dc;
    if (uVar1 == '\x02') {
      iVar7 = DAT_000af7d8;
      iVar8 = DAT_000af7d4;
    }
    iVar8 = (int)(iVar8 * (uint)DAT_febeac12) / 0x400;
    iVar7 = (int)(iVar7 * (uint)DAT_febeac12) / 0x400;
    DAT_febec09c = iVar8;
    DAT_febec0a0 = iVar7;
    if ((((snapshot[5] == 'Z') && (snapshot[0x34] == 'Z')) &&
        (*(ushort *)(snapshot + 0x20) <= DAT_febec0b4)) && (snapshot[3] == 'Z')) {
      iVar5 = (*(int *)(snapshot + 0x2c) + *(int *)(snapshot + 0x24)) - *(int *)(snapshot + 0x30);
      DAT_febec094 = (*(int *)(snapshot + 0x28) + *(int *)(snapshot + 0x24)) -
                     *(int *)(snapshot + 0x30);
      puVar3 = 0xfebeb800u;
      DAT_febec098 = iVar5;
      iVar4 = abs_s32_wrapping(DAT_febec094);
      iVar5 = abs_s32_wrapping(iVar5);
      if ((iVar4 - iVar8 < 0 == (iVar4 < 0 != iVar8 < 0 && iVar8 < 0 == iVar4 - iVar8 < 0)) ||
         (iVar5 - iVar7 < 0 == (iVar5 < 0 != iVar7 < 0 && iVar7 < 0 == iVar5 - iVar7 < 0))) {
        uVar2 = 0;
      }
      else {
        uVar2 = 0x5a;
      }
      uVar6 = 0x5a;
      goto LAB_000c4708;
    }
  }
  uVar6 = 0;
  uVar2 = DAT_febec0ac;
LAB_000c4708:
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(0x8ac))))) = uVar2;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(0x8ad))))) = uVar6;
  return;
}

void clear_retained_estimator_and_request_reset(void)

{
  DAT_febec0b4 = 0;
  DAT_febec0b7 = 0;
  DAT_febec08e = 0;
  DAT_febec08f = 0;
  DAT_febec0b6 = 0;
  DAT_febeaba8 = 0;
  DAT_febec0b0 = 0;
  DAT_febec0ac = 0;
  DAT_febec0ad = 0;
  DAT_febebfb9 = 0;
  DAT_febebfbb = 0;
  DAT_febebfbd = 0;
  DAT_febebfbe = 0;
  DAT_febebfaa = 0;
  DAT_febebfac = 0;
  DAT_febec090 = 0x5a;
  return;
}

void count_retained_estimator_failure(void)

{
  ushort uVar1;
  uint32_t puVar2;
  ushort uVar3;
  
  uVar1 = DAT_000af7ec;
  puVar2 = 0xfebeb800u;
  DAT_febec0a4 = 0;
  DAT_febec0a6 = 0;
  DAT_febec0aa = 0;
  uVar3 = DAT_febec0a8 + 1U;
  if (DAT_000af7ec <= (ushort)(DAT_febec0a8 + 1U)) {
    puVar2 = 0xfebeb800u;
    clear_retained_estimator_and_request_reset();
    uVar3 = uVar1;
  }
  (*((ushort *)camry_host_ptr((uint32_t)(puVar2 + 0x8a8)))) = uVar3;
  return;
}

void accept_consistent_estimator_center(uchar *snapshot)

{
  ushort uVar1;
  
  DAT_febec0a6 = 0;
  DAT_febec0a8 = 0;
  DAT_febec0aa = 0;
  uVar1 = DAT_febec0a4 + 1;
  if (DAT_000af7e8 <= (ushort)(DAT_febec0a4 + 1)) {
    DAT_febec0b6 = 0x5a;
    DAT_febec0b7 = snapshot[8];
    DAT_febec0b4 = *(undefined2 *)(snapshot + 0x10);
    DAT_febeaba8 = *(undefined4 *)(snapshot + 0x2c);
    uVar1 = DAT_000af7e8;
    DAT_febec0b0 = DAT_febeaba8;
  }
  DAT_febec0a4 = uVar1;
  return;
}

void request_secondary_estimator_reseed(uchar *snapshot)

{
  ushort uVar1;
  
  DAT_febec0a4 = 0;
  DAT_febec0a8 = 0;
  DAT_febec0aa = 0;
  uVar1 = DAT_febec0a6 + 1;
  if (DAT_000af7ea <= (ushort)(DAT_febec0a6 + 1)) {
    DAT_febec0b7 = snapshot[9];
    DAT_febec0b4 = *(undefined2 *)(snapshot + 0x12);
    DAT_febec091 = 0x5a;
    uVar1 = DAT_000af7ea;
  }
  DAT_febec0a6 = uVar1;
  return;
}

void accept_unqualified_estimator_center(uchar *snapshot)

{
  ushort uVar1;
  
  DAT_febec0a4 = 0;
  DAT_febec0a6 = 0;
  DAT_febec0a8 = 0;
  uVar1 = DAT_febec0aa + 1;
  if (DAT_000af7ee <= (ushort)(DAT_febec0aa + 1)) {
    DAT_febec0b7 = snapshot[8];
    DAT_febec0b6 = 0;
    DAT_febeaba8 = *(undefined4 *)(snapshot + 0x2c);
    DAT_febec0b4 = *(undefined2 *)(snapshot + 0x10);
    uVar1 = DAT_000af7ee;
  }
  DAT_febec0aa = uVar1;
  return;
}

void route_retained_estimator_qualification(uchar *snapshot)

{
  if (DAT_febec0ad == 'Z') {
    if (DAT_febec0ac == 'Z') {
      accept_consistent_estimator_center(snapshot);
      return;
    }
    if (DAT_febec0b6 != 'Z') {
      count_retained_estimator_failure();
      return;
    }
  }
  else if (DAT_febec0b6 != 'Z') {
    accept_unqualified_estimator_center(snapshot);
    return;
  }
  request_secondary_estimator_reseed(snapshot);
  return;
}

void validate_and_route_retained_estimator(uchar *snapshot)

{
  uint32_t puVar1;
  int iVar2;
  char cVar3;
  
  cVar3 = DAT_febec0ae;
  puVar1 = 0xfebeb800u;
  if (((*snapshot != 'Z') &&
      ((((snapshot[0xb] != '\x01' || (snapshot[10] != '\x02')) || (snapshot[0x35] != '\0')) ||
       (1 < snapshot[4])))) &&
     ((((snapshot[1] != 'Z' && (snapshot[2] != 'Z')) &&
       (*(uint *)(snapshot + 0x14) == ~*(uint *)(snapshot + 0x18))) &&
      (snapshot[0x1c] == (uchar)~snapshot[0x1d])))) {
    puVar1 = 0xfebeb800u;
    iVar2 = abs_s32_wrapping((int)*(short *)(snapshot + 0xe));
    if ((iVar2 - DAT_000af7e4 < 0 !=
         (iVar2 < 0 != DAT_000af7e4 < 0 && DAT_000af7e4 < 0 == iVar2 - DAT_000af7e4 < 0)) &&
       (cVar3 == '\0')) {
      route_retained_estimator_qualification(snapshot);
      goto LAB_000c4924;
    }
    cVar3 = 'Z';
  }
  count_retained_estimator_failure();
LAB_000c4924:
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x8ae))))) = cVar3;
  return;
}

void qualify_rate_observer_acquisition(void)

{
  uint8_t snapshot[56];
  ushort band;
  
  snapshot[8] = DAT_febebfbd;
  snapshot[0] = DAT_febebfc5;
  snapshot[9] = DAT_febebfbe;
  snapshot[1] = DAT_febead3d;
  snapshot[10] = DAT_febebfbf;
  snapshot[2] = DAT_febead40;
  snapshot[11] = DAT_febebfc0;
  *(uint16_t *)(snapshot + 14) = (uint16_t)((int)(int16_t)DAT_febec172);
  *(uint16_t *)(snapshot + 16) = (uint16_t)DAT_febebfaa;
  snapshot[3] = DAT_febebfba;
  *(uint16_t *)(snapshot + 18) = (uint16_t)DAT_febebfac;
  snapshot[4] = DAT_febebfc2;
  *(uint32_t *)(snapshot + 20) = DAT_febebfd4;
  snapshot[5] = DAT_febebfbb;
  *(uint32_t *)(snapshot + 24) = DAT_febebfe4;
  snapshot[6] = DAT_febebfbc;
  snapshot[28] = DAT_febebff0;
  snapshot[29] = DAT_febebff2;
  band = estimator_lower_band_default;
  if (DAT_febebfbc == '\x02') {
    band = estimator_lower_band_mode2;
  }
  *(uint16_t *)(snapshot + 32) = band;
  *(uint32_t *)(snapshot + 36) = DAT_febebf88;
  *(uint32_t *)(snapshot + 40) = DAT_febebf8c;
  *(uint32_t *)(snapshot + 44) = DAT_febebf90;
  *(uint32_t *)(snapshot + 48) = DAT_febebf94;
  snapshot[52] = DAT_febebfc1;
  snapshot[53] = DAT_febebfc3;
  if (DAT_febec08d == 'Z') {
    DAT_febec091 = 0;
  }
  if (DAT_febec08c == 'Z') {
    DAT_febec090 = 0;
  }
  check_retained_estimator_consistency((uchar *)snapshot);
  validate_and_route_retained_estimator((uchar *)snapshot);
  return;
}

void fill_constant_block_c4a06(void)

{
  DAT_febec0cc = 0;
  DAT_febec0d0 = 0;
  DAT_febec0b8 = 0;
  DAT_febec0c0 = DAT_000af7f8;
  DAT_febec0bc = 0;
  DAT_febec0c8 = 0;
  DAT_febec0ca = 0;
  DAT_febec0c4 = DAT_000af7f8;
  return;
}

void seed_c0c0_c0c4_thresholds_by_c08e_mode_c4a32(void)

{
  undefined4 *puVar1;
  
  if (DAT_febec08e == '\"') {
    puVar1 = ((undefined *)camry_host_ptr(0xaf7f0u));
  }
  else {
    if (DAT_febec08e != '\x11') {
      puVar1 = ((undefined *)camry_host_ptr(0xaf7f8u));
      goto LAB_000c4a5e;
    }
    puVar1 = ((undefined *)camry_host_ptr(0xaf7f4u));
  }
  DAT_febec0ca = 1;
LAB_000c4a5e:
  DAT_febec0c0 = *puVar1;
  DAT_febec0c4 = *puVar1;
  return;
}

void select_c0bc_threshold_by_c08e_mode_c4a70(void)

{
  DAT_febec0bc = DAT_000af7f0;
  if ((DAT_febec08e != '\"') && (DAT_febec0bc = DAT_000af7f8, DAT_febec08e == '\x11')) {
    DAT_febec0bc = DAT_000af7f4;
  }
  return;
}

int replace_second_with_first_minus_threshold_if_far_c4aa2(int param_1,int param_2)

{
  int gap;
  
  gap = abs_s32_wrapping(param_1 - param_2);
  if (gap >= (int)DAT_000af7fc) {
    return param_1 - (int)DAT_000af7fc;
  }
  return param_2;
}

int replace_second_with_first_plus_threshold_if_far_c4acc(int param_1,int param_2)

{
  int gap;
  
  gap = abs_s32_wrapping(param_1 - param_2);
  if (gap >= (int)DAT_000af7fc) {
    return (int)DAT_000af7fc + param_1;
  }
  return param_2;
}

void step_c0c0_toward_c0bc_on_counter_expiry_c4af6(void)

{
  int iVar1;
  bool bVar2;
  uint32_t puVar3;
  int iVar4;
  ushort uVar5;
  
  puVar3 = 0xfebeb800u;
  uVar5 = DAT_febec0c8 + 1;
  iVar1 = ((int)(int32_t)DAT_febec0c0) - ((int)(int32_t)DAT_febec0bc);
  bVar2 = ((int)(int32_t)DAT_febec0c0) < 0 != ((int)(int32_t)DAT_febec0bc) < 0 && ((int)(int32_t)DAT_febec0bc) < 0 == iVar1 < 0;
  iVar4 = ((int)(int32_t)DAT_febec0c0);
  if (iVar1 < 0 == bVar2) {
    if (iVar1 < 0 != bVar2 || ((int)(int32_t)DAT_febec0c0) == ((int)(int32_t)DAT_febec0bc)) {
      uVar5 = 0;
      goto LAB_000c4b42;
    }
    if ((uVar5 < DAT_000af800) ||
       (uVar5 = 0,
       ((int)(int32_t)DAT_febec0c0) - ((int)(int32_t)DAT_febec0c4) < 0 !=
       (((int)(int32_t)DAT_febec0c0) < 0 != ((int)(int32_t)DAT_febec0c4) < 0 && ((int)(int32_t)DAT_febec0c4) < 0 == ((int)(int32_t)DAT_febec0c0) - ((int)(int32_t)DAT_febec0c4) < 0)
       )) goto LAB_000c4b42;
    puVar3 = 0xfebeb800u;
    iVar4 = replace_second_with_first_minus_threshold_if_far_c4aa2((int)DAT_febec0c0,(int)DAT_febec0bc);
  }
  else {
    if ((uVar5 < DAT_000af800) ||
       (uVar5 = 0,
       ((int)(int32_t)DAT_febec0c0) - ((int)(int32_t)DAT_febec0c4) < 0 ==
       (((int)(int32_t)DAT_febec0c0) < 0 != ((int)(int32_t)DAT_febec0c4) < 0 && ((int)(int32_t)DAT_febec0c4) < 0 == ((int)(int32_t)DAT_febec0c0) - ((int)(int32_t)DAT_febec0c4) < 0)
       && ((int)(int32_t)DAT_febec0c0) != ((int)(int32_t)DAT_febec0c4))) goto LAB_000c4b42;
    puVar3 = 0xfebeb800u;
    iVar4 = replace_second_with_first_plus_threshold_if_far_c4acc((int)DAT_febec0c0,(int)DAT_febec0bc);
  }
  uVar5 = 0;
LAB_000c4b42:
  (*((int *)camry_host_ptr((uint32_t)(puVar3 + 0x8c0)))) = iVar4;
  (*((ushort *)camry_host_ptr((uint32_t)(puVar3 + 0x8c8)))) = uVar5;
  return;
}

void update_c0c4_reference_on_signed_input_crossing_c4b4e(void)

{
  if (((int)(int32_t)DAT_febec0b8) < 0) {
    if (((int)(int32_t)DAT_febec084) + ((int)(int32_t)DAT_febec0c4) < 0 !=
        (((int)(int32_t)DAT_febec084) < 0 != -((int)(int32_t)DAT_febec0c4) < 0 &&
        -((int)(int32_t)DAT_febec0c4) < 0 == ((int)(int32_t)DAT_febec084) + ((int)(int32_t)DAT_febec0c4) < 0)) {
      DAT_febec0b8 = ((int)(int32_t)DAT_febec084);
      return;
    }
    if (((int)(int32_t)DAT_febec084) + ((int)(int32_t)DAT_febec0bc) < 0 !=
        (((int)(int32_t)DAT_febec084) < 0 != -((int)(int32_t)DAT_febec0bc) < 0 &&
        -((int)(int32_t)DAT_febec0bc) < 0 == ((int)(int32_t)DAT_febec084) + ((int)(int32_t)DAT_febec0bc) < 0)) {
      DAT_febec0b8 = ((int)(int32_t)DAT_febec084);
      return;
    }
  }
  else if (((int)(int32_t)DAT_febec0b8) != 0) {
    if (((int)(int32_t)DAT_febec084) - ((int)(int32_t)DAT_febec0c4) < 0 ==
        (((int)(int32_t)DAT_febec084) < 0 != ((int)(int32_t)DAT_febec0c4) < 0 && ((int)(int32_t)DAT_febec0c4) < 0 == ((int)(int32_t)DAT_febec084) - ((int)(int32_t)DAT_febec0c4) < 0
        ) && ((int)(int32_t)DAT_febec084) != ((int)(int32_t)DAT_febec0c4)) {
      DAT_febec0b8 = ((int)(int32_t)DAT_febec084);
      return;
    }
    if (((int)(int32_t)DAT_febec084) - ((int)(int32_t)DAT_febec0bc) < 0 ==
        (((int)(int32_t)DAT_febec084) < 0 != ((int)(int32_t)DAT_febec0bc) < 0 && ((int)(int32_t)DAT_febec0bc) < 0 == ((int)(int32_t)DAT_febec084) - ((int)(int32_t)DAT_febec0bc) < 0
        ) && ((int)(int32_t)DAT_febec084) != ((int)(int32_t)DAT_febec0bc)) {
      DAT_febec0b8 = ((int)(int32_t)DAT_febec084);
      return;
    }
  }
  DAT_febec0c4 = DAT_febec0c0;
  DAT_febec0b8 = ((int)(int32_t)DAT_febec084);
  return;
}

undefined4 publish_c084_symmetric_deadband_residual_c4b8c(void)

{
  uint32_t puVar1;
  undefined4 uVar2;
  int value;
  int other;
  int iVar3;
  
  puVar1 = 0xfebeb800u;
  value = (int)DAT_febec084;
  other = (int)DAT_febec0c4;
  if (value > other) {
    iVar3 = value - other;
  }
  else {
    iVar3 = 0;
    if (value < -other) {
      iVar3 = other + value;
    }
  }
  uVar2 = raise_priority_mask_and_return_previous_d1da0(0xffc0);
  (*((int *)camry_host_ptr((uint32_t)(puVar1 + 0x8cc)))) = iVar3;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x8d0))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x88e)))));
  restore_priority_mask_preserving_interrupt_enable_d1dc6(uVar2);
  return uVar2;
}

void update_rate_observer_deadband(void)

{
  if (DAT_febec0ca == '\0') {
    seed_c0c0_c0c4_thresholds_by_c08e_mode_c4a32();
  }
  select_c0bc_threshold_by_c08e_mode_c4a70();
  step_c0c0_toward_c0bc_on_counter_expiry_c4af6();
  update_c0c4_reference_on_signed_input_crossing_c4b4e();
  publish_c084_symmetric_deadband_residual_c4b8c();
  return;
}

void initialize_secondary_estimator_stability(void)

{
  DAT_febec0de = 0;
  DAT_febec0dd = 0;
  DAT_febec0d4 = 0;
  DAT_febec0dc = DAT_febead5b;
  DAT_febec0d8 = 0;
  return;
}

void qualify_secondary_estimator_change(int change,uchar *count,uchar *qualified)

{
  int iVar1;
  byte bVar2;
  uchar uVar3;
  
  iVar1 = (int)(DAT_000af804 * (uint)DAT_febeae38) / 0x400;
  if (change - iVar1 < 0 == (change < 0 != iVar1 < 0 && iVar1 < 0 == change - iVar1 < 0)) {
    uVar3 = '\0';
    bVar2 = 0;
  }
  else {
    bVar2 = *count;
    uVar3 = *qualified;
    if ((DAT_000af808 <= bVar2) || (bVar2 = bVar2 + 1, DAT_000af808 <= bVar2)) {
      uVar3 = 'Z';
    }
  }
  *qualified = uVar3;
  *count = bVar2;
  return;
}

void update_secondary_estimator_stability(void)

{
  uint8_t stack_record_e[14];
  char cVar1;
  int iVar2;
  uint32_t puVar3;
  int iVar4;
  
  cVar1 = DAT_febead5b;
  puVar3 = 0xfebeb800u;
  stack_record_e[0] = DAT_febec0de;
  stack_record_e[1] = DAT_febec0dd;
  iVar4 = DAT_febec0d4;
  if ((((DAT_febebfb6 == 'Z') && (DAT_febeac02 == '\0')) && (DAT_febebfaf == 'Z')) &&
     (DAT_febebfb7 == 'Z')) {
    iVar2 = DAT_febec0d8;
    if (DAT_febead5b != DAT_febec0dc) {
      iVar2 = (DAT_febebf84 + DAT_febebf7c) - DAT_febebf70;
      puVar3 = 0xfebeb800u;
      iVar4 = abs_s32_wrapping(iVar2 - DAT_febec0d8);
      qualify_secondary_estimator_change(iVar4,((uint8_t *)((stack_record_e + 1))),((uint8_t *)(stack_record_e)));
      iVar4 = iVar2;
    }
  }
  else {
    stack_record_e[0] = '\0';
    iVar2 = 0;
    stack_record_e[1] = '\0';
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(0x8dc))))) = cVar1;
  (*((int *)camry_host_ptr((uint32_t)(puVar3 + 0x8d4)))) = iVar4;
  (*((int *)camry_host_ptr((uint32_t)(puVar3 + 0x8d8)))) = iVar2;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(0x8de))))) = stack_record_e[0];
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(0x8dd))))) = stack_record_e[1];
  return;
}

void initialize_assist_torque_conditioner(void)

{
  DAT_febec114 = 0;
  DAT_febec0f0 = 0;
  DAT_febec110 = 0;
  DAT_febec0fc = DAT_000afb34;
  DAT_febec124 = 0;
  DAT_febec0f8 = 0;
  DAT_febec0f4 = 0;
  DAT_febec112 = 0;
  DAT_febec0e4 = DAT_000af80c;
  DAT_febec128 = 0;
  DAT_febec116 = 0;
  DAT_febec118 = 0;
  DAT_febec11a = 0;
  DAT_febec108 = 0;
  DAT_febec11c = 0;
  DAT_febec100 = 0;
  DAT_febec104 = 0;
  DAT_febec10c = 0;
  DAT_febec0e0 = 0;
  DAT_febec0e8 = 0;
  DAT_febec10e = 0;
  DAT_febec0ec = DAT_000afb34;
  DAT_febec12a = 0;
  DAT_febec11e = 0;
  DAT_febec120 = 0;
  return;
}

void update_retained_assist_torque_output(void)

{
  int iVar1;
  int iVar2;
  
  if (DAT_febec12a == '\x01') {
    iVar2 = 0x400;
  }
  else {
    iVar2 = DAT_000afb38;
    if (DAT_febeac4a <= DAT_000af810) {
      iVar2 = DAT_000afb34;
    }
  }
  DAT_febec10e = ((int)(int16_t)DAT_febec128);
  DAT_febec100 = iVar2 << 10;
  if (DAT_febec0fc != 0) {
    if (DAT_febec100 == -0x80000000 && DAT_febec0fc == -1) {
      DAT_febec100 = -0x80000000;
    }
    else {
      DAT_febec100 = (int)DAT_febec100 / (int)DAT_febec0fc;
    }
  }
  DAT_febec0e8 = DAT_febec0f4;
  DAT_febec0ec = DAT_febec0fc;
  DAT_febec0fc = iVar2;
  DAT_febec104 = (int)((DAT_febec0f4 * DAT_febec100)) / (int)0x400;
  DAT_febec0f4 = (DAT_febec108 + DAT_febec104) - (int)((int)(int16_t)DAT_febec112);
  iVar1 = DAT_febec0f4 * 0x400;
  if (iVar2 != 0) {
    if (iVar1 == -0x80000000 && iVar2 == -1) {
      iVar1 = 0;
    }
    else {
      iVar1 = (int)iVar1 / (int)iVar2;
    }
  }
  DAT_febec112 = (short)iVar1;
  DAT_febec128 = (short)iVar1;
  return;
}

void condition_assist_torque(void)

{
  int iVar1;
  short sVar2;
  int iVar3;
  int iVar4;
  
  iVar4 = (int)((int)(int16_t)DAT_febec150);
  iVar3 = (int)DAT_000afae4;
  sVar2 = DAT_000afae4;
  if ((iVar4 - iVar3 < 0 != (iVar4 < 0 != iVar3 < 0 && iVar3 < 0 == iVar4 - iVar3 < 0) ||
       iVar4 == iVar3) &&
     (iVar1 = -iVar3, sVar2 = ((int)(int16_t)DAT_febec150),
     iVar4 + iVar3 < 0 != (iVar4 < 0 != iVar1 < 0 && iVar1 < 0 == iVar4 + iVar3 < 0) ||
     iVar4 == iVar1)) {
    sVar2 = (short)iVar1;
  }
  iVar3 = (int)sVar2;
  DAT_febec10c = ((int)(int16_t)DAT_febec110);
  DAT_febec0e0 = DAT_febec0f0;
  DAT_febec0e4 = DAT_000af80c;
  DAT_febec0f8 = DAT_febec124;
  if (DAT_febec12a == '\x01') {
    iVar4 = 0x400;
    DAT_febec0f0 = (iVar3 * DAT_000af80c) / 0x400;
    DAT_febec124 = iVar3;
  }
  else {
    iVar4 = (int)((int)(int16_t)DAT_febec114);
    DAT_febec0f0 = (int)((int)(int16_t)DAT_febec110) + iVar3 + DAT_febec0f0 + DAT_febec124 * -2;
    DAT_febec124 = DAT_febec0f0 * 0x400;
    if (DAT_000af80c != 0) {
      if (DAT_febec124 == -0x80000000 && DAT_000af80c == -1) {
        DAT_febec124 = -0x80000000;
      }
      else {
        DAT_febec124 = (int)DAT_febec124 / (int)DAT_000af80c;
      }
    }
  }
  DAT_febec11c = (undefined2)iVar4;
  DAT_febec108 = DAT_febec124 + (int)((iVar4 * (iVar3 - DAT_febec124))) / (int)0x400;
  DAT_febec110 = sVar2;
  update_retained_assist_torque_output();
  return;
}

void update_torque_conditioner_slope_blend(void)

{
  short sVar1;
  uint32_t puVar2;
  short sVar3;
  int iVar4;
  short *points;
  int iVar5;
  
  sVar1 = ((int)(int16_t)DAT_febebf40);
  puVar2 = 0xfebeb800u;
  iVar5 = (int)((int)(int16_t)DAT_febec1aa);
  iVar4 = (int)((int)(int16_t)DAT_febec1a8) + (DAT_febec156 & 3) * 2;
  points = ((short *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd2f3cu + (uint32_t)(iVar4) * 4u))))));
  iVar4 = interpolate_signed_sentinel_curve(((short *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd2f38u + (uint32_t)(iVar4) * 4u)))))),((int)(int16_t)DAT_febebf40));
  (*((short *)camry_host_ptr((uint32_t)(puVar2 + 0x91a)))) = (short)iVar4;
  iVar4 = interpolate_signed_sentinel_curve(points,sVar1);
  (*((short *)camry_host_ptr((uint32_t)(puVar2 + 0x918)))) = (short)iVar4;
  sVar3 = (short)( (int)(((iVar4 - (*((short *)camry_host_ptr((uint32_t)(puVar2 + 0x91a))))) * iVar5)) / (int)0x400) +
          (*((short *)camry_host_ptr((uint32_t)(puVar2 + 0x91a))));
  iVar4 = (int)sVar3;
  (*((short *)camry_host_ptr((uint32_t)(puVar2 + 0x916)))) = sVar3;
  sVar1 = 0x400;
  if ((iVar4 + -0x400 < 0 != (iVar4 < 0 && -1 < iVar4 + -0x400) || iVar4 == 0x400) &&
     (sVar1 = sVar3, iVar4 < 1)) {
    sVar1 = 0;
  }
  (*((short *)camry_host_ptr((uint32_t)(puVar2 + 0x914)))) = sVar1;
  return;
}

void update_torque_conditioner_reseed_selector(void)

{
  ushort uVar1;
  char cVar2;
  uint32_t puVar3;
  int iVar4;
  int iVar5;
  int iVar6;
  int iVar7;
  int iVar8;
  int iVar9;
  uint uVar10;
  bool bVar11;
  
  cVar2 = DAT_febec12a;
  uVar1 = DAT_febeac50;
  puVar3 = 0xfebeb800u;
  iVar8 = (int)((int)(int16_t)DAT_febecc62);
  if (((DAT_febeadfa & 0xff00) == 0x500) && (DAT_febeac41 == 'Z')) {
    uVar10 = (uint)DAT_febeac84;
  }
  else {
    uVar10 = (uint)((int)(int16_t)DAT_febeac4c);
  }
  iVar9 = (int)((int)(int16_t)DAT_febec150);
  iVar7 = (int)((int)(int16_t)DAT_febec128);
  iVar5 = DAT_febebf3c * (uint)DAT_febeac64;
  iVar6 = DAT_febec4c0 * (uint)DAT_febeac64;
  iVar4 = abs_s32_wrapping(iVar8);
  iVar5 = abs_s32_wrapping(iVar5 / 0x8000);
  iVar9 = abs_s32_wrapping(iVar9);
  iVar7 = abs_s32_wrapping(iVar7);
  iVar6 = abs_s32_wrapping(iVar8 - iVar6 / 0x8000);
  iVar8 = (iVar4 - uVar10) - DAT_000afb3c;
  if (((iVar8 < 0 ==
        ((int)(iVar4 - uVar10) < 0 != DAT_000afb3c < 0 && DAT_000afb3c < 0 == iVar8 < 0)) &&
      (iVar8 = (iVar5 - uVar10) - DAT_000afb40,
      iVar8 < 0 == ((int)(iVar5 - uVar10) < 0 != DAT_000afb40 < 0 && DAT_000afb40 < 0 == iVar8 < 0))
      ) && ((uVar1 & 0x1ff) == 0)) {
    if (cVar2 != '\0') {
      bVar11 = true;
      goto LAB_000c4fd2;
    }
    iVar8 = (iVar9 - iVar7) - DAT_000afb44;
    if (iVar8 < 0 == (iVar9 - iVar7 < 0 != DAT_000afb44 < 0 && DAT_000afb44 < 0 == iVar8 < 0)) {
      iVar8 = (iVar6 - uVar10) - DAT_000afb48;
      bVar11 = iVar8 < 0 ==
               ((int)(iVar6 - uVar10) < 0 != DAT_000afb48 < 0 && DAT_000afb48 < 0 == iVar8 < 0);
      goto LAB_000c4fd2;
    }
  }
  bVar11 = false;
LAB_000c4fd2:
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(0x92a))))) = bVar11;
  return;
}

void repair_assist_torque_conditioner_state(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  
  DAT_febec11e = 0;
  if (DAT_febec0e4 != 0) {
    iVar1 = (int)(DAT_febec0f0 << 10);
    if ((int)DAT_febec0e4 != 0) {
      if (iVar1 == -0x80000000 && (int)DAT_febec0e4 == -1) {
        iVar1 = -0x80000000;
      }
      else {
        iVar1 = iVar1 / (int)DAT_febec0e4;
      }
    }
    iVar3 = (int)DAT_febec108 -
            ((int)DAT_febec124 + (int)(((int)(int16_t)DAT_febec11c * ((int)(int16_t)DAT_febec110 - (int)DAT_febec124))) / (int)0x400);
    iVar2 = (int)DAT_000afad4;
    if (-iVar2 < iVar3 && iVar3 < iVar2) {
      iVar3 = (int)DAT_febec124 - iVar1;
      iVar2 = (int)DAT_000afad8;
      if (iVar3 <= -iVar2 || iVar3 >= iVar2) {
        DAT_febec0f0 = (uint)( (int)(((int)DAT_febec124 * (int)DAT_febec0e4)) / (int)0x400);
        DAT_febec11e = 1;
      }
    }
    else {
      DAT_febec11e = 2;
      DAT_febec124 = (uint)iVar1;
    }
  }
  if (DAT_febec0fc == 0) {
    DAT_febec11e = DAT_febec11e | 0x10;
    DAT_febec0fc = 0x400;
    DAT_febec0f4 = (int)(int16_t)DAT_febec112;
  }
  else {
    iVar1 = (int)(DAT_febec0f4 << 10);
    if ((int)DAT_febec0fc != 0) {
      if (iVar1 == -0x80000000 && (int)DAT_febec0fc == -1) {
        iVar1 = -0x80000000;
      }
      else {
        iVar1 = iVar1 / (int)DAT_febec0fc;
      }
    }
    iVar2 = (int)(short)((int)(int16_t)DAT_febec128 - (int)(int16_t)DAT_febec112);
    iVar3 = (int)DAT_000afadc;
    if (-iVar3 < iVar2 && iVar2 < iVar3) {
      iVar2 = (int)(short)((int)(int16_t)DAT_febec112 - (short)iVar1);
      iVar3 = (int)DAT_000afae0;
      if (iVar2 <= -iVar3 || iVar2 >= iVar3) {
        DAT_febec0f4 = (uint)( (int)(((int)(int16_t)DAT_febec112 * (int)DAT_febec0fc)) / (int)0x400);
        DAT_febec11e = DAT_febec11e | 4;
      }
    }
    else {
      DAT_febec11e = DAT_febec11e | 8;
      DAT_febec112 = (short)iVar1;
    }
  }
  DAT_febec120 = DAT_febec120 | DAT_febec11e;
  return;
}
