#include "common.h"


/* Sequential initializer chain: 4 unconditional calls and no other statements; shape-verified. The
   called sequence is the function's entire behavior; chain family members differ in callee sets. */

void f33_run_init_chain_c4046(void)

{
  f33_apply_estimator_center_reseed();
  f33_apply_estimator_acquisition_reset();
  f33_run_init_chain_c3292();
  f33_update_secondary_estimator_stability();
  return;
}



/* Refresh threshold maps, source stabilityC042, paired-source qualificationC044, then
   compositeC045. C43E0 consumes these newly produced bytes before acquisition/tracking. Compose
   threshold refresh then independent source-stability, paired-source and composite constraints
   before the same caller selects acquisition or tracking. */

void f33_refresh_estimator_tracking_qualifiers(void)

{
  f33_refresh_estimator_qualifier_thresholds();
  f33_qualify_estimator_source_stability();
  f33_qualify_estimator_paired_sources();
  f33_qualify_estimator_source_constraints();
  return;
}



/* WARNING: Removing unreachable block (ram,0x000c412c) */
/* WARNING: Removing unreachable block (ram,0x000c4118) */
/* WARNING: Removing unreachable block (ram,0x000c40a2) */
/* WARNING: Removing unreachable block (ram,0x000c409e) */
/* WARNING: Removing unreachable block (ram,0x000c40f8) */
/* Clip difference around C080 by AE38/1024. StateC08E selects curveAF77E/AF792/AF7A6 atADF6;
   gain=8192/curve, or8192 when zero. Clamp low32 error*low16(gain) to +/-8*AE38; add signed
   increment/4 to GLOBAL C078, publish accumulator/2048 through output pointer. Arithmetic is low32,
   not a saturating integral; third pointer is output-only. Clip around center; curve-derived low16
   gain and bounded low32 step feed global accumulatorC078. Third pointer is output-only. Signed
   divisions by4 and2048 remain separate. */

void f33_filter_established_estimator_difference
               (int difference,int *filtered_difference,int *new_accumulator)

{
  int iVar1;
  int iVar2;
  uint32_t puVar3;
  undefined1 *puVar4;
  int iVar5;
  uint uVar6;
  int iVar7;
  int iVar8;
  
  puVar3 = 0xfebeb800u;
  iVar7 = (int)(f33_estimator_tracking_band_scale * (uint)DAT_febeae38) / 0x400;
  iVar2 = (int)(f33_estimator_tracking_step_scale * (uint)DAT_febeae38) / 0x400;
  iVar5 = DAT_febec080 - iVar7;
  iVar7 = iVar7 + DAT_febec080;
  if ((difference - iVar7 < 0 !=
       (difference < 0 != iVar7 < 0 && iVar7 < 0 == difference - iVar7 < 0) || difference == iVar7)
     && (iVar7 = iVar5,
        difference - iVar5 < 0 ==
        (difference < 0 != iVar5 < 0 && iVar5 < 0 == difference - iVar5 < 0) && difference != iVar5)
     ) {
    iVar7 = difference;
  }
  if (DAT_febec08e == '\"') {
    puVar4 = ((undefined *)camry_host_ptr(0xaf7a6u));
  }
  else if (DAT_febec08e == '\x11') {
    puVar4 = ((undefined *)camry_host_ptr(0xaf792u));
  }
  else {
    puVar4 = ((undefined *)camry_host_ptr(0xaf77eu));
  }
  DAT_febec048 = iVar7;
  iVar5 = FUN_000d0896(puVar4,DAT_febeadf6);
  uVar6 = 0x2000;
  if (iVar5 != 0) {
    uVar6 = 0x2000 / iVar5;
  }
  iVar1 = (iVar7 - *filtered_difference) * (uVar6 & 0xffff);
  iVar7 = iVar1 - iVar2;
  iVar8 = iVar2;
  if (iVar7 < 0 != (iVar1 < 0 != iVar2 < 0 && iVar2 < 0 == iVar7 < 0) || iVar7 == 0) {
    iVar8 = -iVar2;
    iVar2 = iVar1 + iVar2;
    if (iVar2 < 0 == (iVar1 < 0 != iVar8 < 0 && iVar8 < 0 == iVar2 < 0) && iVar2 != 0) {
      iVar8 = iVar1;
    }
  }
  (*((short *)camry_host_ptr((uint32_t)(puVar3 + 0x860)))) = (short)iVar5;
  (*((short *)camry_host_ptr((uint32_t)(puVar3 + 0x862)))) = (short)uVar6;
  iVar2 = (*((int *)camry_host_ptr((uint32_t)(puVar3 + 0x878)))) + iVar8 / 4;
  *filtered_difference = iVar2 / 0x800;
  *new_accumulator = iVar2;
  (*((int *)camry_host_ptr((uint32_t)(puVar3 + 0x850)))) = iVar1;
  (*((int *)camry_host_ptr((uint32_t)(puVar3 + 0x854)))) = iVar8;
  return;
}



/* WARNING: Removing unreachable block (ram,0x000c417e) */
/* Start from C0B4, not oldBFEC. Below curve ceiling60000, increment if candidate changed or wrapped
   abs32(candidate-C080)<AE38/1024. Otherwise retain the input count, even above the ceiling.
   Publish BFEC and diagnostic ceilingC066. Count starts fromC0B4 rather thanBFEC. Below flat60000
   ceiling increment for changed candidate or strict center band; ceiling gates increment rather
   than clamping. */

void f33_advance_estimator_source_count(int candidate,int previous)

{
  int iVar1;
  uint32_t puVar2;
  uint uVar3;
  int iVar4;
  ushort uVar5;
  uint uVar6;
  
  uVar5 = DAT_febec0b4;
  puVar2 = 0xfebeb800u;
  uVar6 = (uint)DAT_febec0b4;
  uVar3 = FUN_000d0896(((undefined *)camry_host_ptr(0xaf7bau)),DAT_febeadf4);
  iVar4 = f33_abs_s32_wrapping(camry_host_addr(((undefined *)camry_host_ptr((uint32_t)(candidate - (*((int *)camry_host_ptr((uint32_t)(puVar2 + 0x880)))))))));
  iVar1 = (int)(f33_estimator_tracking_band_scale * (uint)(*((ushort *)camry_host_ptr((uint32_t)(puVar2 + -0x9c8))))) / 0x400;
  if ((uVar6 < uVar3) &&
     ((iVar4 - iVar1 < 0 != (iVar4 < 0 != iVar1 < 0 && iVar1 < 0 == iVar4 - iVar1 < 0) ||
      (candidate != previous)))) {
    uVar5 = uVar5 + 1;
  }
  (*((ushort *)camry_host_ptr((uint32_t)(puVar2 + 0x7ec)))) = uVar5;
  (*((short *)camry_host_ptr((uint32_t)(puVar2 + 0x866)))) = (short)uVar3;
  return;
}



/* With BFC5==0, first copyC0B4->BFEE. QualifiersC045/C044/C042=5A, AD18=11 and unsignedADF4>=3840
   publishC074=low32(BF78-BFD4) and increment u16C064. Only count>100 runs bounded
   filter/source-count update, then pins100. Failed qualification resets warmup but holds
   C04C/C078/C074; BFC5!=0 instead clears filter/accumulator and warmup. Established tracking
   publishes difference before consecutive warmup exceeds100. Qualifier interruption resets warmup
   but holds filter/difference; BFEE refresh precedes admission. BFC5 instead clears
   filter/accumulator. */

void f33_track_established_estimator_difference(void)

{
  ushort uVar1;
  int previous;
  uint32_t puVar2;
  ushort uVar3;
  int local_14;
  int iStack_10;
  
  previous = DAT_febec04c;
  uVar1 = f33_estimator_tracking_warmup;
  puVar2 = 0xfebeb800u;
  if (DAT_febebfc5 == '\0') {
    DAT_febebfee = DAT_febec0b4;
    local_14 = DAT_febec078;
    iStack_10 = DAT_febec04c;
    if ((((DAT_febec045 == 'Z') && (DAT_febec044 == 'Z')) && (DAT_febec042 == 'Z')) &&
       ((DAT_febead18 == '\x11' && (DAT_000af770 <= DAT_febeadf4)))) {
      DAT_febec074 = DAT_febebf78 - DAT_febebfd4;
      uVar3 = DAT_febec064 + 1U;
      if (f33_estimator_tracking_warmup < (ushort)(DAT_febec064 + 1U)) {
        puVar2 = 0xfebeb800u;
        f33_filter_established_estimator_difference(DAT_febec074,&iStack_10,&local_14);
        f33_advance_estimator_source_count(iStack_10,previous);
        uVar3 = uVar1;
      }
      goto LAB_000c4236;
    }
  }
  else {
    iStack_10 = 0;
    local_14 = 0;
  }
  uVar3 = 0;
LAB_000c4236:
  (*((ushort *)camry_host_ptr((uint32_t)(puVar2 + 0x864)))) = uVar3;
  (*((int *)camry_host_ptr((uint32_t)(puVar2 + 0x84c)))) = iStack_10;
  (*((int *)camry_host_ptr((uint32_t)(puVar2 + 0x878)))) = local_14;
  return;
}



/* Source markers, wrapped abs16 amplitudes<160/512 and unsigned abs32 difference
   <low32(24000*AE38)>>10 admit warmup. Incremented u16 count>10 pins10; C0DE5A additionally commits
   BFD8=BF7C-(BF78-BFD4-BF70), projection=C080+BFD8 and acceptance5A. Rejection clears warmup but
   holds acceptance/output. Source/amplitude gates plus unsigned normalized difference bound admit
   strict warmup>10. AdditionalC0DE commits predicted sample and center projection; failure holds
   acceptance/output while clearing warmup. */

void f33_predict_estimator_source_sample(ushort *warmup,uchar *accepted,int *projection)

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
  sVar16 = DAT_febebf98;
  iVar2 = DAT_febebf7c;
  iVar8 = DAT_febebf70;
  uVar21 = DAT_febeae38;
  sVar6 = DAT_000af776;
  sVar5 = DAT_000af774;
  puVar14 = 0xfebeb800u;
  iVar20 = *projection;
  uVar19 = *accepted;
  uVar3 = *warmup;
  sVar15 = f33_abs_s16_wrapping(DAT_febebf9c);
  sVar16 = f33_abs_s16_wrapping(sVar16);
  iVar1 = iVar2 - iVar8;
  uVar17 = f33_abs_s32_wrapping(iVar1);
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
  return;
}



/* AD3C==0/3 or mode2+AD3E1+AD250+AD271 clearsBFF1/C068/BFFA but retainsC07C. Otherwise
   acceptedBFF1==5A projectsC07C=low32(C080+BFD8); absent acceptance invokes C424C prediction.
   Projection usesBFD8, notBFD4. Accepted projection adds C080+BFD8, not referenceBFD4. Disabled
   modes clear markers/warmup but retainC07C; no acceptance selects prediction pathC424C. */

void f33_update_estimator_source_projection(void)

{
  uint32_t puVar1;
  uchar uStack_b;
  ushort uStack_a;
  int iStack_8;
  
  puVar1 = 0xfebeb800u;
  uStack_a = DAT_febec068;
  uStack_b = DAT_febebff1;
  iStack_8 = DAT_febec07c;
  if (((DAT_febead3c == '\0') || (DAT_febead3c == '\x03')) ||
     ((DAT_febead3c == '\x02' &&
      (((DAT_febead3e == '\x01' && (DAT_febead25 == '\0')) && (DAT_febead27 == '\x01')))))) {
    uStack_b = '\0';
    uStack_a = 0;
    DAT_febebffa = 0;
  }
  else if (DAT_febebff1 == 'Z') {
    iStack_8 = DAT_febec080 + DAT_febebfd8;
  }
  else {
    puVar1 = 0xfebeb800u;
    f33_predict_estimator_source_sample(&uStack_a,&uStack_b,&iStack_8);
  }
  (*((ushort *)camry_host_ptr((uint32_t)(puVar1 + 0x868)))) = uStack_a;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x7f1))))) = uStack_b;
  (*((int *)camry_host_ptr((uint32_t)(puVar1 + 0x87c)))) = iStack_8;
  return;
}



/* Refresh qualifiers; BFF0==5A selects established-reference difference trackingC419C, otherwise
   source acquisitionC3740. Then update external-source projectionC4358. Reference acquisition is
   not repeated on every established tracking pass. Real threshold/group-release/stability producers
   refresh qualifiers before BFF05A selects established tracking. Native invocation matures all
   three qualifiers and advances bounded tracking, stopping before4358 projection; other branch
   selects acquisition. */

void f33_run_estimator_acquisition_or_tracking(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  f33_refresh_estimator_tracking_qualifiers();
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x7f0))))) == 'Z') {
    f33_track_established_estimator_difference();
  }
  else {
    f33_select_estimator_acquisition_source();
  }
  f33_update_estimator_source_projection();
  return;
}



/* Always snapshotC08E->C08A. Modes0/3 selectC06E0. Other mode bytes classify unsignedBFEC with
   exact lower1 and upper10880: below lower0, below upper11, otherwise22. Mode2 has separate
   calibration cells but the same exact thresholds. Modes0/3 force class0; others classify
   unsignedBFEC against1/10880 as0/11/22. Always snapshot retained class; closed mode retains
   threshold cells. */

void f33_classify_estimator_source_band(void)

{
  DAT_febec08a = DAT_febec08e;
  if ((DAT_febead3c != '\0') && (DAT_febead3c != '\x03')) {
    DAT_febec088 = f33_estimator_lower_band_default;
    DAT_febec06a = f33_estimator_upper_band_default;
    if (DAT_febead3c == '\x02') {
      DAT_febec088 = f33_estimator_lower_band_mode2;
      DAT_febec06a = f33_estimator_upper_band_mode2;
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



/* WARNING: Removing unreachable block (ram,0x000c44b4) */
/* BFC5==0 andBFF0==5A compute low32 residualBF78-BFD4-C080. First C06F0 call latches C06E->C08B
   andC06F5A without adopting the filter. Later calls adoptC04C and current band only when wrapped
   abs32(residual)<=480*AE38/1024. Closed gate clears center only, retaining C06F/C08B/C05C. This is
   separate from AD13's outer publication gate. First admitted call latches initialization/class
   without center adoption. Later inclusive residual band adopts filter; closed source gate clears
   only center. Distinct from outer publication gate. */

void f33_follow_estimator_center(void)

{
  int value;
  int iVar1;
  undefined1 uVar2;
  undefined *puVar3;
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
  puVar3 = ((undefined *)camry_host_ptr(0xfebeb800u));
  if ((DAT_febebfc5 == '\0') && (DAT_febebff0 == 'Z')) {
    value = (DAT_febebf78 - DAT_febebfd4) - DAT_febec080;
    if (DAT_febec06f == '\0') {
      cVar8 = 'Z';
      uVar7 = uVar2;
      puVar3 = ((undefined *)camry_host_ptr(0xfebeb800u));
    }
    else {
      iVar5 = f33_abs_s32_wrapping(value);
      iVar1 = (int)(f33_estimator_center_adoption_scale * (uint)(*((ushort *)camry_host_ptr((uint32_t)(puVar4 + -0x9c8))))) /
              0x400;
      puVar3 = ((undefined *)camry_host_ptr((uint32_t)(puVar4)));
      if (iVar5 - iVar1 < 0 != (iVar5 < 0 != iVar1 < 0 && iVar1 < 0 == iVar5 - iVar1 < 0) ||
          iVar5 == iVar1) {
        iVar6 = (*((int *)camry_host_ptr((uint32_t)(puVar4 + 0x84c))));
        uVar7 = uVar2;
      }
    }
    *(int *)(puVar3 + 0x85c) = value;
    puVar3[0x88b] = uVar7;
    puVar3[0x86f] = cVar8;
  }
  else {
    iVar6 = 0;
  }
  *(int *)(puVar3 + 0x880) = iVar6;
  return;
}



/* Always apply reseed/reset and source/secondary-tracker preworkC4046. AD13==5A seeds BFF8/BFFA
   fromAE0E/AD31 once whileC070==0, then acquisition/tracking, source-band selection, center
   following and publication. Otherwise clear only published copiesC33E6. Always run reset/reseed
   and source prework. AD135A initializes external count/marker once, then acquisition/tracking,
   bands, center and publication; closed gate clears published copies only. */

void f33_run_raw_estimator_cycle(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  f33_run_init_chain_c4046();
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0xaed))))) == 'Z') {
    if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x870))))) == '\0') {
      (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + 0x7f8)))) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x9f2))));
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x7fa))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0xacf)))));
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x870))))) = 0x5a;
    }
    f33_run_estimator_acquisition_or_tracking();
    f33_classify_estimator_source_band();
    f33_follow_estimator_center();
    f33_publish_raw_estimator_state();
  }
  else {
    f33_clear_published_estimator_state();
  }
  return;
}



/* WARNING: Removing unreachable block (ram,0x000c45aa) */
/* WARNING: Removing unreachable block (ram,0x000c45a2) */
/* Require AD3C!=0/3,BFB9==5A,BFC5==0 and C0B4>=selected threshold1. Delta is low32
   ABA4-(ABA0<<7)-(ABA8<<7); rate=(delta/8)/((u16AC12<<4)/1024). Failed gate zeroes delta but
   RETAINS state/qualification. A zero divisor alone holds oldC084. Output layout is8 bytes.
   Eight-byte state/qualification/rate result. Native qualified versus failed gate yields31 versus0
   while failed gate retains state/qualification. Static gates require AD3C!=0/3 and BFC5==0; zero
   divisor alone holds prior rate. */

void f33_sample_rate_observer(F33RateObserverSample *sample)

{
  uint uVar1;
  int iVar2;
  int iVar3;
  uchar uVar4;
  uchar uVar5;
  
  if ((DAT_febead3c != '\0') && (DAT_febead3c != '\x03')) {
    DAT_febec06c = f33_estimator_lower_band_default;
    if (DAT_febead3c == '\x02') {
      DAT_febec06c = f33_estimator_lower_band_mode2;
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



/* Always run C330C source snapshot/qualification prework. Only AC07==5A samples and commits
   C08F,then C08E,then C084 under PMRFFC0. Closed outer gate holds publication. Composed native
   prework clears the separate AC01 qualifier at its threshold then commits qualification/state/rate
   under PMRFFC0. Closed AC07 outer gate holds publication but still runs source prework. */

void f33_commit_rate_observer(void)

{
  uint32_t puVar1;
  undefined4 uVar2;
  F33RateObserverSample local_c;
  
  puVar1 = 0xfebeb800u;
  FUN_000c330c();
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0xbf9))))) == 'Z') {
    f33_sample_rate_observer(&local_c);
    uVar2 = FUN_000d1da0(0xffc0);
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x88f))))) = local_c.qualification;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x88e))))) = local_c.state;
    (*((int *)camry_host_ptr((uint32_t)(puVar1 + 0x884)))) = local_c.rate;
    FUN_000d1dc6(uVar2);
  }
  return;
}



/* Full initialization clears residuals/bounds/counters, correctionABA8, reseed centerC0B0 and
   sticky plausibilityC0AE. Ordinary failure resetC4714 does not clear that latch. Full
   retained-estimator initialization clears sticky plausibilityC0AE; ordinary failure reset does
   not. */

void f33_initialize_retained_estimator_qualification(void)

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



/* WARNING: Removing unreachable block (ram,0x000c46a0) */
/* WARNING: Removing unreachable block (ram,0x000c469c) */
/* Separate evaluation admissionC0AD and passC0AC. Inadmission clearsAD but holdsAC. Admitted
   residuals are sample+difference-feedforward and sample+center-feedforward; wrapped abs32 must be
   strictly below signed low32(480/160*AC12)/1024. Bounds refresh after outer mode admission;
   residuals only after all source/count gates. AdmissionC0AD and passC0AC have distinct retention.
   Strict wrapped-absolute residual bands480/160 scaled byAC12; inadmission holds pass and only
   outer mode admission refreshes bounds. */

void f33_check_retained_estimator_consistency(uchar *snapshot)

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
      iVar4 = f33_abs_s32_wrapping(DAT_febec094);
      iVar5 = f33_abs_s32_wrapping(iVar5);
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



/* Clear candidate/publication qualification, counters, correctionABA8 and centerC0B0; assertC090.
   Do not execute raw-estimator reset, clear stickyC0AE or overwrite rateC084. Clear retained
   candidate/publication context and correction then request raw reset; preserve sticky plausibility
   latch and published rate. Request is not execution of its consumer. */

void f33_clear_retained_estimator_and_request_reset(void)

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



/* Exclusive u16C0A8 failure counter reaches2 inclusively then callsC4714. Narrow increment before
   comparison; pre-existingFFFF wraps rather than saturating. Exclusive narrowed u16 failure counter
   reaches2 inclusively before clear/reset request; pre-existingFFFF wraps. */

void f33_count_retained_estimator_failure(void)

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
    f33_clear_retained_estimator_and_request_reset();
    uVar3 = uVar1;
  }
  (*((ushort *)camry_host_ptr((uint32_t)(puVar2 + 0x8a8)))) = uVar3;
  return;
}



/* ExclusiveC0A4 reaches3 inclusively: qualifyC0B6, adopt primary class/count, and copy published
   centerBF90 to BOTH correctionABA8 and reseed centerC0B0. Primary consistency count reaches3
   inclusively; adopt primary class/count and copy center to both rate correction and reseed center.
    */

void f33_accept_consistent_estimator_center(uchar *snapshot)

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



/* ExclusiveC0A6 reaches3 inclusively: adopt secondary class/count and assertC091. Hold
   correctionABA8, reseed centerC0B0 and retained qualificationC0B6. Secondary count reaches3
   inclusively; adopt secondary class/count and assert reseed while retaining correction and reseed
   center. */

void f33_request_secondary_estimator_reseed(uchar *snapshot)

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



/* ExclusiveC0AA reaches3 inclusively: adopt primary class/count, clear qualification and copyBF90
   toABA8 only; retain reseed centerC0B0. Unqualified primary count reaches3 inclusively; clear
   qualification and refresh correction only, retaining reseed center. */

void f33_accept_unqualified_estimator_center(uchar *snapshot)

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



/* Admission/pass both5A select primary consistency; else retained qualification5A selects secondary
   reseed; else inadmission selects unqualified primary; otherwise failure. Exactly one branch runs
   and clears the other three consecutive counters. Fresh admission/pass and retained qualification
   select exactly one of four consecutive-counter branches with different center lifetimes. */

void f33_route_retained_estimator_qualification(uchar *snapshot)

{
  if (DAT_febec0ad == 'Z') {
    if (DAT_febec0ac == 'Z') {
      f33_accept_consistent_estimator_center(snapshot);
      return;
    }
    if (DAT_febec0b6 != 'Z') {
      f33_count_retained_estimator_failure();
      return;
    }
  }
  else if (DAT_febec0b6 != 'Z') {
    f33_accept_unqualified_estimator_center(snapshot);
    return;
  }
  f33_request_secondary_estimator_reseed(snapshot);
  return;
}



/* Suppression/mode predicates and bitwise reference/marker complements precede widened
   abs(s16C172)<12000 and stickyC0AE==0. Structural rejection preserves latch; plausibility/latch
   failure sets5A. Rejection counts failure, not immediate raw reset. Structural
   suppression/complement gates precede widened signed16 magnitude<12000 and stickyC0AE. Structural
   rejection retains latch; plausibility failure asserts it. */

void f33_validate_and_route_retained_estimator(uchar *snapshot)

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
    iVar2 = f33_abs_s32_wrapping((int)*(short *)(snapshot + 0xe));
    if ((iVar2 - DAT_000af7e4 < 0 !=
         (iVar2 < 0 != DAT_000af7e4 < 0 && DAT_000af7e4 < 0 == iVar2 - DAT_000af7e4 < 0)) &&
       (cVar3 == '\0')) {
      f33_route_retained_estimator_qualification(snapshot);
      goto LAB_000c4924;
    }
    cVar3 = 'Z';
  }
  f33_count_retained_estimator_failure();
LAB_000c4924:
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x8ae))))) = cVar3;
  return;
}



/* Build56-byte published-source/reference snapshot; acknowledgementsC08D/C08C clear
   requestsC091/C090 but themselves hold. ConsistencyC4640 then routingC489C may reassert a request
   in the same invocation. Distinct from C45C0 rate sampling and physical freshness. Consume prior
   acknowledgements before consistency/routing. Native scheduler composition rejects residual-bound
   equality, matures retained secondary qualification, reasserts reseed and publishes rate31 with
   held correction/center. No physical freshness or later reseed-consumer claim. */

void f33_qualify_rate_observer_acquisition(void)

{
  uchar local_3c;
  undefined1 uStack_3b;
  undefined1 uStack_3a;
  undefined1 uStack_39;
  undefined1 uStack_38;
  undefined1 uStack_37;
  char cStack_36;
  undefined1 uStack_34;
  undefined1 uStack_33;
  undefined1 uStack_32;
  undefined1 uStack_31;
  undefined2 uStack_2e;
  undefined2 uStack_2c;
  undefined2 uStack_2a;
  undefined4 uStack_28;
  undefined4 uStack_24;
  undefined1 uStack_20;
  undefined1 uStack_1f;
  ushort uStack_1c;
  undefined4 uStack_18;
  undefined4 uStack_14;
  undefined4 uStack_10;
  undefined4 uStack_c;
  undefined1 uStack_8;
  undefined1 uStack_7;
  
  uStack_34 = DAT_febebfbd;
  local_3c = DAT_febebfc5;
  uStack_33 = DAT_febebfbe;
  uStack_3b = DAT_febead3d;
  uStack_32 = DAT_febebfbf;
  uStack_3a = DAT_febead40;
  uStack_31 = DAT_febebfc0;
  uStack_2e = DAT_febec172;
  uStack_2c = DAT_febebfaa;
  uStack_39 = DAT_febebfba;
  uStack_2a = DAT_febebfac;
  uStack_38 = DAT_febebfc2;
  uStack_28 = DAT_febebfd4;
  uStack_37 = DAT_febebfbb;
  uStack_24 = DAT_febebfe4;
  cStack_36 = DAT_febebfbc;
  uStack_20 = DAT_febebff0;
  uStack_1f = DAT_febebff2;
  uStack_1c = f33_estimator_lower_band_default;
  if (DAT_febebfbc == '\x02') {
    uStack_1c = f33_estimator_lower_band_mode2;
  }
  uStack_18 = DAT_febebf88;
  uStack_14 = DAT_febebf8c;
  uStack_10 = DAT_febebf90;
  uStack_c = DAT_febebf94;
  uStack_8 = DAT_febebfc1;
  uStack_7 = DAT_febebfc3;
  if (DAT_febec08d == 'Z') {
    DAT_febec091 = 0;
  }
  if (DAT_febec08c == 'Z') {
    DAT_febec090 = 0;
  }
  f33_check_retained_estimator_consistency(&local_3c);
  f33_validate_and_route_retained_estimator(&local_3c);
  return;
}



/* Constant-block fill: 8 literal assignments into one contiguous cell block; shape-verified.
   Literals are default/reset values; cell meanings are not recovered. */

void f33_fill_constant_block_c4a06(void)

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



void FUN_000c4a32(void)

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



void FUN_000c4a70(void)

{
  DAT_febec0bc = DAT_000af7f0;
  if ((DAT_febec08e != '\"') && (DAT_febec0bc = DAT_000af7f8, DAT_febec08e == '\x11')) {
    DAT_febec0bc = DAT_000af7f4;
  }
  return;
}



int FUN_000c4aa2(int param_1,int param_2)

{
  int iVar1;
  
  iVar1 = f33_abs_s32_wrapping(param_1 - param_2);
  if (iVar1 - DAT_000af7fc < 0 ==
      (iVar1 < 0 != DAT_000af7fc < 0 && DAT_000af7fc < 0 == iVar1 - DAT_000af7fc < 0)) {
    param_2 = param_1 - DAT_000af7fc;
  }
  return param_2;
}



int FUN_000c4acc(int param_1,int param_2)

{
  int iVar1;
  
  iVar1 = f33_abs_s32_wrapping(param_1 - param_2);
  if (iVar1 - DAT_000af7fc < 0 ==
      (iVar1 < 0 != DAT_000af7fc < 0 && DAT_000af7fc < 0 == iVar1 - DAT_000af7fc < 0)) {
    param_2 = DAT_000af7fc + param_1;
  }
  return param_2;
}



void FUN_000c4b4e(void)

{
  if (DAT_febec0b8 < 0) {
    if (DAT_febec084 + DAT_febec0c4 < 0 !=
        (DAT_febec084 < 0 != -DAT_febec0c4 < 0 &&
        -DAT_febec0c4 < 0 == DAT_febec084 + DAT_febec0c4 < 0)) {
      DAT_febec0b8 = DAT_febec084;
      return;
    }
    if (DAT_febec084 + DAT_febec0bc < 0 !=
        (DAT_febec084 < 0 != -DAT_febec0bc < 0 &&
        -DAT_febec0bc < 0 == DAT_febec084 + DAT_febec0bc < 0)) {
      DAT_febec0b8 = DAT_febec084;
      return;
    }
  }
  else if (DAT_febec0b8 != 0) {
    if (DAT_febec084 - DAT_febec0c4 < 0 ==
        (DAT_febec084 < 0 != DAT_febec0c4 < 0 && DAT_febec0c4 < 0 == DAT_febec084 - DAT_febec0c4 < 0
        ) && DAT_febec084 != DAT_febec0c4) {
      DAT_febec0b8 = DAT_febec084;
      return;
    }
    if (DAT_febec084 - DAT_febec0bc < 0 ==
        (DAT_febec084 < 0 != DAT_febec0bc < 0 && DAT_febec0bc < 0 == DAT_febec084 - DAT_febec0bc < 0
        ) && DAT_febec084 != DAT_febec0bc) {
      DAT_febec0b8 = DAT_febec084;
      return;
    }
  }
  DAT_febec0c4 = DAT_febec0c0;
  DAT_febec0b8 = DAT_febec084;
  return;
}



void FUN_000c4b8c(void)

{
  uint32_t puVar1;
  undefined4 uVar2;
  int iVar3;
  
  puVar1 = 0xfebeb800u;
  if (DAT_febec084 - DAT_febec0c4 < 0 ==
      (DAT_febec084 < 0 != DAT_febec0c4 < 0 && DAT_febec0c4 < 0 == DAT_febec084 - DAT_febec0c4 < 0)
      && DAT_febec084 != DAT_febec0c4) {
    iVar3 = DAT_febec084 - DAT_febec0c4;
  }
  else {
    iVar3 = 0;
    if (DAT_febec084 + DAT_febec0c4 < 0 !=
        (DAT_febec084 < 0 != -DAT_febec0c4 < 0 &&
        -DAT_febec0c4 < 0 == DAT_febec084 + DAT_febec0c4 < 0)) {
      iVar3 = DAT_febec0c4 + DAT_febec084;
    }
  }
  uVar2 = FUN_000d1da0(0xffc0);
  (*((int *)camry_host_ptr((uint32_t)(puVar1 + 0x8cc)))) = iVar3;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x8d0))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x88e)))));
  FUN_000d1dc6(uVar2);
  return;
}



/* Initialize band until state11/22 latches initialization; select32 for11/other,0 for22, adapt one
   count per invocation, retain direction-dependent active band, then publish deadband excessC0CC
   and stateC0D0 under PMR. Invalid state reinitializes on each call. Compose state-selected band,
   one-count target chase, directional active-band retention and protected signed-excess
   publication. Native positive rate31/state22 requests zero width but retained active32 still
   yields zero excess; failed sample retains state11. */

void f33_update_rate_observer_deadband(void)

{
  if (DAT_febec0ca == '\0') {
    FUN_000c4a32();
  }
  FUN_000c4a70();
  FUN_000c4af6();
  FUN_000c4b4e();
  FUN_000c4b8c();
  return;
}



/* Clear observationsC0D4/C0D8, counterC0DD and markerC0DE; seed tokenC0DC fromAD5B. Initialize
   secondary observations/count/marker and snapshot currentAD5B token; no hardware freshness
   assertion. */

void f33_initialize_secondary_estimator_stability(void)

{
  DAT_febec0de = 0;
  DAT_febec0dd = 0;
  DAT_febec0d4 = 0;
  DAT_febec0dc = DAT_febead5b;
  DAT_febec0d8 = 0;
  return;
}



/* WARNING: Removing unreachable block (ram,0x000c4c2a) */
/* Require signed change<signed low32(43*AE38)/1024. Increment below2 and assert5A on reaching2;
   equality/large change clears count/status. Invocation count, not elapsed time. Strict signed
   change<low32(43*AE38)/1024 and inclusive count2 qualify secondary stability; equal/large changes
   reset count and marker. */

void f33_qualify_secondary_estimator_change(int change,uchar *count,uchar *qualified)

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



/* Admitted source with changedAD5B token evaluates BF84+BF7C-BF70 versusC0D8. Changed token updates
   both observations even on rejection; unchanged token holds. Closed admission
   clearsC0D8/count/marker but retainsC0D4. Always retain current token. Changed token updates
   BF84+BF7C-BF70 observations even on rejection; unchanged admitted token holds. Closed admission
   clears comparison history/count/marker but retains latest observation; token always refreshes. */

void f33_update_secondary_estimator_stability(void)

{
  char cVar1;
  int iVar2;
  uint32_t puVar3;
  int iVar4;
  uchar uStack_e;
  uchar uStack_d;
  
  cVar1 = DAT_febead5b;
  puVar3 = 0xfebeb800u;
  uStack_e = DAT_febec0de;
  uStack_d = DAT_febec0dd;
  iVar4 = DAT_febec0d4;
  if ((((DAT_febebfb6 == 'Z') && (DAT_febeac02 == '\0')) && (DAT_febebfaf == 'Z')) &&
     (DAT_febebfb7 == 'Z')) {
    iVar2 = DAT_febec0d8;
    if (DAT_febead5b != DAT_febec0dc) {
      iVar2 = (DAT_febebf84 + DAT_febebf7c) - DAT_febebf70;
      puVar3 = 0xfebeb800u;
      iVar4 = f33_abs_s32_wrapping(iVar2 - DAT_febec0d8);
      f33_qualify_secondary_estimator_change(iVar4,&uStack_d,&uStack_e);
      iVar4 = iVar2;
    }
  }
  else {
    uStack_e = '\0';
    iVar2 = 0;
    uStack_d = '\0';
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(0x8dc))))) = cVar1;
  (*((int *)camry_host_ptr((uint32_t)(puVar3 + 0x8d4)))) = iVar4;
  (*((int *)camry_host_ptr((uint32_t)(puVar3 + 0x8d8)))) = iVar2;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(0x8de))))) = uStack_e;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(0x8dd))))) = uStack_d;
  return;
}



/* Initialize both retained recurrences, denominators408474/6347, outputs/history and
   selector/repair latches. This reset is distinct from a later C12A reseed. Initialize both torque
   recurrences and denominators408474/6347 plus outputs/history/repair latches; full reset is
   distinct from later C12A reseeding. */

void f33_initialize_assist_torque_conditioner(void)

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



/* WARNING: Removing unreachable block (ram,0x000c4dce) */
/* Denominator1024 for C12A==1, otherwise6347 when unsigned AC4A<=512 or4607. Rescale old
   accumulator using low32(newD<<10)/oldD, then add C108-oldC112. Narrow
   low32(newAccumulator<<10)/newD into C112/C128; history is not independently cleared. Select
   denominator1024/6347/4607 then rescale retained accumulator with low32 arithmetic before output
   recurrence. C12A does not independently erase old stage2 history. */

void f33_update_retained_assist_torque_output(void)

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
  DAT_febec10e = DAT_febec128;
  DAT_febec100 = iVar2 << 10;
  if (DAT_febec0fc != 0) {
    if (DAT_febec100 == -0x80000000 && DAT_febec0fc == -1) {
      DAT_febec100 = -0x80000000;
    }
    else {
      DAT_febec100 = DAT_febec100 / DAT_febec0fc;
    }
  }
  DAT_febec0e8 = DAT_febec0f4;
  DAT_febec0ec = DAT_febec0fc;
  DAT_febec0fc = iVar2;
  DAT_febec104 = (DAT_febec0f4 * DAT_febec100) / 0x400;
  DAT_febec0f4 = (DAT_febec108 + DAT_febec104) - (int)DAT_febec112;
  iVar1 = DAT_febec0f4 * 0x400;
  if (iVar2 != 0) {
    if (iVar1 == -0x80000000 && iVar2 == -1) {
      iVar1 = 0;
    }
    else {
      iVar1 = iVar1 / iVar2;
    }
  }
  DAT_febec112 = (short)iVar1;
  DAT_febec128 = (short)iVar1;
  return;
}



/* WARNING: Removing unreachable block (ram,0x000c4e82) */
/* WARNING: Removing unreachable block (ram,0x000c4e54) */
/* Clamp C150 to+/-2109, then advance retained two-stage recurrence. C12A==1 seeds stage1 with
   low32(input*408474)/1024 and blend1024, but does not clear stage2 history. Ordinary stage1
   preserves low32 accumulator/shift arithmetic before signed division408474. Actual scheduler
   composition admits reseed at equality and advances both retained stages into signed base
   assistance. Preserve low32 products/shifts and signed division; reseed does not independently
   clear second-stage history. Physical scaling remains unassigned. */

void f33_condition_assist_torque(void)

{
  int iVar1;
  short sVar2;
  int iVar3;
  int iVar4;
  
  iVar4 = (int)DAT_febec150;
  iVar3 = (int)DAT_000afae4;
  sVar2 = DAT_000afae4;
  if ((iVar4 - iVar3 < 0 != (iVar4 < 0 != iVar3 < 0 && iVar3 < 0 == iVar4 - iVar3 < 0) ||
       iVar4 == iVar3) &&
     (iVar1 = -iVar3, sVar2 = DAT_febec150,
     iVar4 + iVar3 < 0 != (iVar4 < 0 != iVar1 < 0 && iVar1 < 0 == iVar4 + iVar3 < 0) ||
     iVar4 == iVar1)) {
    sVar2 = (short)iVar1;
  }
  iVar3 = (int)sVar2;
  DAT_febec10c = DAT_febec110;
  DAT_febec0e0 = DAT_febec0f0;
  DAT_febec0e4 = DAT_000af80c;
  DAT_febec0f8 = DAT_febec124;
  if (DAT_febec12a == '\x01') {
    iVar4 = 0x400;
    DAT_febec0f0 = (iVar3 * DAT_000af80c) / 0x400;
    DAT_febec124 = iVar3;
  }
  else {
    iVar4 = (int)DAT_febec114;
    DAT_febec0f0 = (int)DAT_febec110 + iVar3 + DAT_febec0f0 + DAT_febec124 * -2;
    DAT_febec124 = DAT_febec0f0 * 0x400;
    if (DAT_000af80c != 0) {
      if (DAT_febec124 == -0x80000000 && DAT_000af80c == -1) {
        DAT_febec124 = -0x80000000;
      }
      else {
        DAT_febec124 = DAT_febec124 / DAT_000af80c;
      }
    }
  }
  DAT_febec11c = (undefined2)iVar4;
  DAT_febec108 = DAT_febec124 + (iVar4 * (iVar3 - DAT_febec124)) / 0x400;
  DAT_febec110 = sVar2;
  f33_update_retained_assist_torque_output();
  return;
}



/* WARNING: Removing unreachable block (ram,0x000c4ee2) */
/* Produce C114 from previous BF40 before current base surface/slope publication. Caller AC31
   admission can retain this coefficient while torque recurrences advance. Conditioner blend C114
   consumes previous BF40; caller generation admission can hold it while input recurrences and base
   assistance advance. */

void f33_update_torque_conditioner_slope_blend(void)

{
  short sVar1;
  uint32_t puVar2;
  short sVar3;
  int iVar4;
  short *points;
  int iVar5;
  
  sVar1 = DAT_febebf40;
  puVar2 = 0xfebeb800u;
  iVar5 = (int)DAT_febec1aa;
  iVar4 = (int)DAT_febec1a8 + (DAT_febec156 & 3) * 2;
  points = ((short *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd2f3cu + (uint32_t)(iVar4) * 4u))))));
  iVar4 = f33_interpolate_signed_sentinel_curve(((short *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd2f38u + (uint32_t)(iVar4) * 4u)))))),DAT_febebf40);
  (*((short *)camry_host_ptr((uint32_t)(puVar2 + 0x91a)))) = (short)iVar4;
  iVar4 = f33_interpolate_signed_sentinel_curve(points,sVar1);
  (*((short *)camry_host_ptr((uint32_t)(puVar2 + 0x918)))) = (short)iVar4;
  sVar3 = (short)(((iVar4 - (*((short *)camry_host_ptr((uint32_t)(puVar2 + 0x91a))))) * iVar5) / 0x400) +
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



/* WARNING: Removing unreachable block (ram,0x000c4f5c) */
/* WARNING: Removing unreachable block (ram,0x000c4f58) */
/* Threshold is unsigned AC84 only for ADFA.high0500 and AC41==5A, otherwise signed AC4C. Previous
   command/base-assist magnitudes and low-nine AC50 bits gate entry/retention. Entry also tests
   input/output magnitude difference and command-rate residual. All four exact margins0 admit
   equality; common failure clears retained C12A. Ordinary threshold is signed AC4C versus special
   unsigned AC84. All exact margins0 admit equality; common gates retain or clear C12A while entry
   adds two residual gates. Native interval reaches signed base assistance. */

void f33_update_torque_conditioner_reseed_selector(void)

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
  iVar8 = (int)DAT_febecc62;
  if (((DAT_febeadfa & 0xff00) == 0x500) && (DAT_febeac41 == 'Z')) {
    uVar10 = (uint)DAT_febeac84;
  }
  else {
    uVar10 = (uint)DAT_febeac4c;
  }
  iVar9 = (int)DAT_febec150;
  iVar7 = (int)DAT_febec128;
  iVar5 = DAT_febebf3c * (uint)DAT_febeac64;
  iVar6 = DAT_febec4c0 * (uint)DAT_febeac64;
  iVar4 = f33_abs_s32_wrapping(iVar8);
  iVar5 = f33_abs_s32_wrapping(iVar5 / 0x8000);
  iVar9 = f33_abs_s32_wrapping(iVar9);
  iVar7 = f33_abs_s32_wrapping(iVar7);
  iVar6 = f33_abs_s32_wrapping(iVar8 - iVar6 / 0x8000);
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



/* WARNING: Removing unreachable block (ram,0x000c50ac) */
/* WARNING: Removing unreachable block (ram,0x000c5046) */
/* WARNING: Removing unreachable block (ram,0x000c500c) */
/* Strict consistency band(-384,384); equality repairs. Indications1/2 repair first
   accumulator/model,4/8 repair second accumulator/output,10 initializes zero second denominator.
   Second-stage differences SXH before comparison. Publish C11E and OR into sticky C120; do not
   write C128. Consistency bands are strict(-384,384); Stage2 differences narrow before comparison;
   zero denominator seeds1024. Repair indications latch but do not directly replace C128. */

void f33_repair_assist_torque_conditioner_state(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  
  DAT_febec11e = 0;
  if (DAT_febec0e4 != 0) {
    iVar1 = DAT_febec0f0 << 10;
    if (DAT_febec0e4 != 0) {
      if (iVar1 == -0x80000000 && DAT_febec0e4 == -1) {
        iVar1 = -0x80000000;
      }
      else {
        iVar1 = iVar1 / DAT_febec0e4;
      }
    }
    iVar3 = DAT_febec108 -
            (DAT_febec124 + ((int)DAT_febec11c * (DAT_febec110 - DAT_febec124)) / 0x400);
    iVar2 = -DAT_000afad4;
    if ((iVar3 + DAT_000afad4 < 0 ==
         (iVar3 < 0 != iVar2 < 0 && iVar2 < 0 == iVar3 + DAT_000afad4 < 0) && iVar3 != iVar2) &&
       (iVar3 - DAT_000afad4 < 0 !=
        (iVar3 < 0 != DAT_000afad4 < 0 && DAT_000afad4 < 0 == iVar3 - DAT_000afad4 < 0))) {
      iVar1 = DAT_febec124 - iVar1;
      iVar3 = -DAT_000afad8;
      if ((iVar1 + DAT_000afad8 < 0 !=
           (iVar1 < 0 != iVar3 < 0 && iVar3 < 0 == iVar1 + DAT_000afad8 < 0) || iVar1 == iVar3) ||
         (iVar1 - DAT_000afad8 < 0 ==
          (iVar1 < 0 != DAT_000afad8 < 0 && DAT_000afad8 < 0 == iVar1 - DAT_000afad8 < 0))) {
        DAT_febec0f0 = (DAT_febec124 * DAT_febec0e4) / 0x400;
        DAT_febec11e = 1;
      }
    }
    else {
      DAT_febec11e = 2;
      DAT_febec124 = iVar1;
    }
  }
  if (DAT_febec0fc == 0) {
    DAT_febec11e = DAT_febec11e | 0x10;
    DAT_febec0fc = 0x400;
    DAT_febec0f4 = (int)DAT_febec112;
  }
  else {
    iVar1 = DAT_febec0f4 << 10;
    if (DAT_febec0fc != 0) {
      if (iVar1 == -0x80000000 && DAT_febec0fc == -1) {
        iVar1 = 0;
      }
      else {
        iVar1 = iVar1 / DAT_febec0fc;
      }
    }
    iVar2 = (int)(short)(DAT_febec128 - DAT_febec112);
    iVar3 = -DAT_000afadc;
    if ((iVar2 + DAT_000afadc < 0 ==
         (iVar2 < 0 != iVar3 < 0 && iVar3 < 0 == iVar2 + DAT_000afadc < 0) && iVar2 != iVar3) &&
       (iVar2 - DAT_000afadc < 0 !=
        (iVar2 < 0 != DAT_000afadc < 0 && DAT_000afadc < 0 == iVar2 - DAT_000afadc < 0))) {
      iVar3 = (int)(short)(DAT_febec112 - (short)iVar1);
      iVar1 = -DAT_000afae0;
      if ((iVar3 + DAT_000afae0 < 0 !=
           (iVar3 < 0 != iVar1 < 0 && iVar1 < 0 == iVar3 + DAT_000afae0 < 0) || iVar3 == iVar1) ||
         (iVar3 - DAT_000afae0 < 0 ==
          (iVar3 < 0 != DAT_000afae0 < 0 && DAT_000afae0 < 0 == iVar3 - DAT_000afae0 < 0))) {
        DAT_febec0f4 = (DAT_febec112 * DAT_febec0fc) / 0x400;
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



/* Initialize C12C/C12E/C130/C132/C134 to1024. Combined with all exact D2FB8 rows, this makes C134
   invariant1024 from initialized state. Initialize retained correction gain and tuple to1024; exact
   calibration rows preserve initialized C134 at1024. */

void f33_initialize_torque_memory_gain(void)

{
  DAT_febec136 = 0;
  DAT_febec12c = 0x400;
  DAT_febec12e = 0x400;
  DAT_febec130 = 0x400;
  DAT_febec132 = 0x400;
  DAT_febec134 = 0x400;
  return;
}



/* WARNING: This is an inlined function */
/* Low8 mode<7 selects16-byte D2FB8 row in bankAC3C&1: three dereferenced halfword pointers plus
   inline up_target. Otherwise retain parameters and select direction1. Real leaf preserves R6 for
   following CE8DA; inline its actual p-code, not an invented return. Prepare12-byte gain state from
   low8 mode and banked16-byte rows containing three pointers plus inline target. Preserve R6 into
   CE8DA; default mode retains parameters. */

void f33_prepare_torque_memory_gain_parameters(F33GainSlewState *state,uint mode)

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
    uVar2 = f33_torque_memory_gain_calibrations[iVar1].up_target;
    uVar6 = *((uint16_t *)camry_host_ptr((uint32_t)(f33_torque_memory_gain_calibrations[iVar1].down_step)));
    uVar5 = *((uint16_t *)camry_host_ptr((uint32_t)(f33_torque_memory_gain_calibrations[iVar1].up_step)));
    uVar4 = *((uint16_t *)camry_host_ptr((uint32_t)(f33_torque_memory_gain_calibrations[iVar1].down_target)));
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



/* WARNING: Inlined function: f33_prepare_torque_memory_gain_parameters */
/* ModeCB00 only when CAB7==1, otherwise7. Prepare stack state, run real CE8DA with preserved R6,
   then publish parameter tuple and C134. Not evidence of varying initialized gain. CAB7==1 selects
   CB00 mode otherwise7; prepare and step real stack state then publish tuple/current gain. Both
   exact banks preserve C1341024 from initialization. */

void f33_update_torque_memory_gain(void)

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
    local_10.up_target = f33_torque_memory_gain_calibrations[iVar1].up_target;
    local_10.down_step = *((uint16_t *)camry_host_ptr((uint32_t)(f33_torque_memory_gain_calibrations[iVar1].down_step)));
    local_10.up_step = *((uint16_t *)camry_host_ptr((uint32_t)(f33_torque_memory_gain_calibrations[iVar1].up_step)));
    local_10.down_target = *((uint16_t *)camry_host_ptr((uint32_t)(f33_torque_memory_gain_calibrations[iVar1].down_target)));
  }
  else {
    local_10.direction = '\x01';
    local_10.up_target = DAT_febec12c;
    local_10.down_step = DAT_febec130;
    local_10.up_step = DAT_febec132;
    local_10.down_target = DAT_febec12e;
  }
  f33_step_retained_unsigned_gain(&local_10);
  (*((ushort *)camry_host_ptr((uint32_t)(puVar2 + 0x930)))) = local_10.down_step;
  (*((ushort *)camry_host_ptr((uint32_t)(puVar2 + 0x932)))) = local_10.up_step;
  (*((ushort *)camry_host_ptr((uint32_t)(puVar2 + 0x92e)))) = local_10.down_target;
  (*((ushort *)camry_host_ptr((uint32_t)(puVar2 + 0x92c)))) = local_10.up_target;
  (*((ushort *)camry_host_ptr((uint32_t)(puVar2 + 0x934)))) = local_10.current;
  return;
}



/* WARNING: Removing unreachable block (ram,0x000c51ba) */
/* Unsigned C134 gain times signed16 R6, signed division1024, then SXH R10. Return and store the
   same narrowed result in C136; not void. Signed16 R6 scaled by unsigned C134; signed division1024
   then SXH R10. Same narrowed result is stored at C136 and returned. Correct nonvoid contract
   preserves caller arithmetic. */

short f33_scale_torque_memory_correction(short value)

{
  DAT_febec136 = (short)((int)((uint)DAT_febec134 * (int)value) / 0x400);
  return DAT_febec136;
}



/* Reset bounded-memory correction state separately from torque recurrence initialization. Reset
   bounded-memory correction separately from torque recurrence and gain initialization. */

void f33_initialize_torque_memory_correction(void)

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



/* Selector-strided torque-magnitude curve supplies C14A; diagnostic AC2B==5A requests zero band.
   Selector-strided torque magnitude curve supplies correction-band amplitude; diagnostic admission
   requests zero amplitude. */

void f33_update_torque_memory_band_amplitude(void)

{
  uint uVar1;
  uint32_t puVar2;
  short input;
  undefined2 uVar3;
  int iVar4;
  
  puVar2 = 0xfebeb800u;
  uVar1 = (uint)DAT_febec156;
  input = f33_abs_s16_wrapping(DAT_febeac44);
  uVar3 = 0;
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0xbd5))))) != 'Z') {
    iVar4 = f33_interpolate_signed_sentinel_curve
                      (((short *)camry_host_ptr((uint32_t)(f33_calibration_bank_bases[(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0xbc4))))) & 1] +
                                (uVar1 & 3) * 0x1c + 0x954))),input);
    uVar3 = (undefined2)iVar4;
  }
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar2 + 0x94a)))) = uVar3;
  return;
}



/* WARNING: Removing unreachable block (ram,0x000c52d6) */
/* WARNING: Removing unreachable block (ram,0x000c52c2) */
/* WARNING: Removing unreachable block (ram,0x000c5282) */
/* First use seeds signed32 offset=-AC90; in-band motion retains it and excursions move the band
   boundary. Scalar low32(1440*u16(AC5E))/262144; zero scalar gives zero raw correction. Speed gain
   then SXH, retained gain then SXH, and final+/-256 clamp publish C146. First use offsets AC90 to
   zero residual; in-band motion retains memory and excursions move the band. Zero scalar gives zero
   raw correction; speed and retained gains each narrow before final +/-256 clamp. */

void f33_update_torque_memory_correction(void)

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
  f33_update_torque_memory_band_amplitude();
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
        iVar3 = iVar3 / iVar2;
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
  sVar5 = f33_scale_torque_memory_correction((short)((iVar7 * (*((short *)camry_host_ptr((uint32_t)(puVar4 + 0x948))))) / 0x400));
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
  return;
}



/* SXH(AC44+C146) BEFORE +/-2109 clamp into C150; not wide saturating addition. Signed16 narrowing
   of AC44+C146 precedes +/-2109 clamp; input publication continues even when selected correction
   producers hold. */

void f33_publish_bounded_assist_torque_input(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  
  iVar3 = (int)DAT_000af818;
  DAT_febec14c = DAT_febeac44 + DAT_febec146;
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



/* Unsigned ADF6 selects selector-strided speed curve into C148. Separate slow-domain caller
   requires captured ACBC&8; base assist may consume retained gain. Unsigned ADF6 selects
   selector-strided speed gain C148 in separate ACBC&8 update domain. */

void f33_update_torque_memory_speed_gain(void)

{
  uint32_t puVar1;
  int iVar2;
  
  puVar1 = 0xfebeb800u;
  iVar2 = f33_interpolate_unsigned_axis_sentinel_curve
                    (((ushort *)camry_host_ptr((uint32_t)(f33_calibration_bank_bases[DAT_febeac3c & 1] +
                     (DAT_febec156 & 3) * 0x24 + 0x8c4))),DAT_febeadf6);
  (*((short *)camry_host_ptr((uint32_t)(puVar1 + 0x948)))) = (short)iVar2;
  return;
}



/* Initialize retained source-transition qualification and source/selector publications. Initialize
   source-transition qualification and source/selector publications independently of torque input
   production. */

void f33_initialize_assist_surface_selection(void)

{
  DAT_febec154 = 0;
  DAT_febec152 = 0;
  DAT_febec158 = 0;
  DAT_febec156 = 0;
  return;
}



/* Separate AD18/AD5F source snapshots and six signed wrapped-magnitude gates qualify source
   mismatch. Exact B1172=0 makes every admitted invocation immediately set C154=5A and clear C152;
   no nonzero debounce. Rejection clears both. Signed-minimum wrap is not saturation. Separate
   request snapshots plus six signed wrapped-magnitude gates qualify mismatch. Exact B1172zero
   immediately asserts C154 and clears count; no nonzero debounce is established. */

void f33_qualify_assist_surface_transition(void)

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
  
  value_01 = DAT_febec266;
  value_00 = DAT_febec23c;
  value = DAT_febec1a2;
  cVar8 = DAT_febec158;
  uVar20 = DAT_febec154;
  uVar7 = DAT_febec152;
  sVar11 = DAT_febec150;
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
  sVar10 = f33_abs_s16_wrapping(DAT_febeadf2);
  iVar12 = (int)sVar10;
  iVar13 = f33_abs_s32_wrapping(iVar13);
  sVar11 = f33_abs_s16_wrapping(sVar11);
  iVar14 = (int)sVar11;
  sVar11 = f33_abs_s16_wrapping(value_00);
  iVar15 = (int)sVar11;
  sVar11 = f33_abs_s16_wrapping(value_01);
  iVar16 = (int)sVar11;
  sVar11 = f33_abs_s16_wrapping(value);
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
  return;
}



/* Priority diagnostic66, AC94 magic override11, then five complement markers/AC50 admission.
   Admitted but unqualified holds C158; qualified selects55 or77/44/88/0. Failed marker/status
   admission clears source without waiting. Diagnostic and magic-word overrides precede
   five-marker/status admission. Admitted unqualified source holds; qualified requests
   select55/77/44/88/0; failed admission clears. */

void f33_update_retained_assist_surface_source(void)

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



/* Regenerate C156 from C158:77->1,44->2,88->3,otherwise0. Calibration source, not a command.
   Regenerate calibration selector1/2/3 from source77/44/88; other states map0. Not an external
   torque command. */

void f33_publish_assist_surface_selector(void)

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



void FUN_000c557a(void)

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



void FUN_000c55b4(void)

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



/* WARNING: Removing unreachable block (ram,0x000c564a) */

void FUN_000c55ee(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  
  DAT_febec15c = (DAT_febec15c + DAT_febec168) - (int)DAT_febec16a;
  iVar2 = DAT_febec15c * 0x400;
  if (DAT_000afab0 != 0) {
    if (iVar2 == -0x80000000 && DAT_000afab0 == -1) {
      iVar2 = 0;
    }
    else {
      iVar2 = iVar2 / DAT_000afab0;
    }
  }
  DAT_febec16a = (short)iVar2;
  DAT_febec160 = (DAT_febec160 + (short)iVar2) - (int)DAT_febec16c;
  iVar2 = DAT_febec160 * 0x400;
  if (DAT_000afab4 != 0) {
    if (iVar2 == -0x80000000 && DAT_000afab4 == -1) {
      iVar2 = 0;
    }
    else {
      iVar2 = iVar2 / DAT_000afab4;
    }
  }
  DAT_febec16c = (short)iVar2;
  iVar2 = ((int)DAT_febec16e * (int)(short)iVar2) / 0x1000;
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



void FUN_000c566c(void)

{
  DAT_febec16e = (short)((uint)DAT_febeae3a * 0xdbba + 0x8000 >> 0x10);
  return;
}



void FUN_000c5686(void)

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



void FUN_000c56c0(void)

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



/* WARNING: Removing unreachable block (ram,0x000c5756) */

void FUN_000c56fa(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  
  DAT_febec174 = (DAT_febec174 + DAT_febec180) - (int)DAT_febec182;
  iVar2 = DAT_febec174 * 0x400;
  if (DAT_000afabc != 0) {
    if (iVar2 == -0x80000000 && DAT_000afabc == -1) {
      iVar2 = 0;
    }
    else {
      iVar2 = iVar2 / DAT_000afabc;
    }
  }
  DAT_febec182 = (short)iVar2;
  DAT_febec178 = (DAT_febec178 + (short)iVar2) - (int)DAT_febec184;
  iVar2 = DAT_febec178 * 0x400;
  if (DAT_000afac0 != 0) {
    if (iVar2 == -0x80000000 && DAT_000afac0 == -1) {
      iVar2 = 0;
    }
    else {
      iVar2 = iVar2 / DAT_000afac0;
    }
  }
  DAT_febec184 = (short)iVar2;
  iVar2 = ((int)DAT_febec186 * (int)(short)iVar2) / 0x1000;
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



void FUN_000c5778(void)

{
  DAT_febec186 = (ushort)((uint)DAT_febeae3a * 90000 + 0x20000 >> 0x12);
  return;
}



void FUN_000c5792(void)

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



void FUN_000c57cc(void)

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



/* WARNING: Removing unreachable block (ram,0x000c5862) */

void FUN_000c5806(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  
  DAT_febec18c = (DAT_febec18c + DAT_febec198) - (int)DAT_febec19a;
  iVar2 = DAT_febec18c * 0x400;
  if (DAT_000afac8 != 0) {
    if (iVar2 == -0x80000000 && DAT_000afac8 == -1) {
      iVar2 = 0;
    }
    else {
      iVar2 = iVar2 / DAT_000afac8;
    }
  }
  DAT_febec19a = (short)iVar2;
  DAT_febec190 = (DAT_febec190 + (short)iVar2) - (int)DAT_febec19c;
  iVar2 = DAT_febec190 * 0x400;
  if (DAT_000afacc != 0) {
    if (iVar2 == -0x80000000 && DAT_000afacc == -1) {
      iVar2 = 0;
    }
    else {
      iVar2 = iVar2 / DAT_000afacc;
    }
  }
  DAT_febec19c = (short)iVar2;
  iVar2 = ((int)DAT_febec19e * (int)(short)iVar2) / 0x1000;
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



void FUN_000c5884(void)

{
  DAT_febec19e = (ushort)((uint)DAT_febeae3a * 90000 + 0x20000 >> 0x12);
  return;
}



/* Constant-block fill: 6 literal assignments into one contiguous cell block; shape-verified.
   Literals are default/reset values; cell meanings are not recovered. */

void f33_fill_constant_block_c589e(void)

{
  DAT_febec1a4 = 0;
  DAT_febec1a6 = 0;
  DAT_febec1a8 = 0;
  DAT_febec1aa = 0;
  DAT_febec1ac = 0;
  DAT_febec1ae = 0;
  return;
}



void FUN_000c5910(void)

{
  uint32_t puVar1;
  undefined4 uVar2;
  undefined2 local_8;
  undefined2 uStack_6;
  
  puVar1 = 0xfebeb800u;
  FUN_000d097a(((ushort *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd30e8u + (uint32_t)(DAT_febec156 & 3) * 4u))))))), DAT_febeadf6, &local_8, &uStack_6);
  uVar2 = FUN_000d1da0(0xffc0);
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + 0x9a8)))) = local_8;
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + 0x9aa)))) = uStack_6;
  FUN_000d1dc6(uVar2);
  return;
}



/* Constant-block fill: 53 literal assignments into one contiguous cell block; shape-verified.
   Literals are default/reset values; cell meanings are not recovered. */

void f33_fill_constant_block_c59ae(void)

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



/* WARNING: Removing unreachable block (ram,0x000c5c0a) */
/* WARNING: Removing unreachable block (ram,0x000c5bd0) */
/* WARNING: Removing unreachable block (ram,0x000c5bba) */
/* WARNING: Removing unreachable block (ram,0x000c5bac) */
/* WARNING: Removing unreachable block (ram,0x000c5b98) */
/* WARNING: Removing unreachable block (ram,0x000c5b94) */
/* WARNING: Removing unreachable block (ram,0x000c5b90) */
/* WARNING: Removing unreachable block (ram,0x000c5b4a) */
/* WARNING: Removing unreachable block (ram,0x000c5b40) */
/* WARNING: Removing unreachable block (ram,0x000c5b32) */
/* WARNING: Removing unreachable block (ram,0x000c5b24) */
/* WARNING: Removing unreachable block (ram,0x000c5b16) */

void FUN_000c5a84(void)

{
  bool bVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  short sVar6;
  int iVar7;
  int *piVar8;
  
  iVar5 = (int)DAT_febec22c;
  iVar7 = (int)DAT_000afb20;
  DAT_febec1d4 = DAT_febec1c8;
  DAT_febec1d8 = DAT_febec1cc;
  DAT_febec234 = 0;
  sVar6 = DAT_000afb20;
  if ((iVar5 - iVar7 < 0 != (iVar5 < 0 != iVar7 < 0 && iVar7 < 0 == iVar5 - iVar7 < 0) ||
       iVar5 == iVar7) &&
     (iVar7 = iVar5 + DAT_000afb20, bVar1 = -(int)DAT_000afb20 < 0, sVar6 = DAT_febec22c,
     iVar7 < 0 != (iVar5 < 0 != bVar1 && bVar1 == iVar7 < 0))) {
    sVar6 = -DAT_000afb20;
  }
  piVar8 = ((int *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xb1454u + (uint32_t)(DAT_febeac3c & 1) * 4u))))));
  iVar4 = *piVar8;
  iVar5 = DAT_febec1c0 - (iVar4 * DAT_febec22a - piVar8[1] * (int)DAT_febec22e) / 2;
  iVar7 = DAT_febec1c8 -
          ((DAT_febec1d0 * (*((short *)camry_host_ptr((uint32_t)((int)camry_host_addr(piVar8) + 10))))) / 2 +
          ((short)piVar8[2] * DAT_febec1cc) / 2 + DAT_febec1c0) / 0x800;
  iVar2 = (int)DAT_febec20a - (int)(short)(DAT_febec1c8 / 0x40);
  iVar3 = -DAT_000afb08;
  if ((((iVar5 + DAT_000afb08 < 0 ==
         (iVar5 < 0 != iVar3 < 0 && iVar3 < 0 == iVar5 + DAT_000afb08 < 0) && iVar5 != iVar3) &&
       (iVar5 - DAT_000afb08 < 0 !=
        (iVar5 < 0 != DAT_000afb08 < 0 && DAT_000afb08 < 0 == iVar5 - DAT_000afb08 < 0))) &&
      (iVar5 = -DAT_000afb0c,
      iVar7 + DAT_000afb0c < 0 == (iVar7 < 0 != iVar5 < 0 && iVar5 < 0 == iVar7 + DAT_000afb0c < 0)
      && iVar7 != iVar5)) &&
     (((iVar7 - DAT_000afb0c < 0 !=
        (iVar7 < 0 != DAT_000afb0c < 0 && DAT_000afb0c < 0 == iVar7 - DAT_000afb0c < 0) &&
       (iVar5 = -DAT_000afb18,
       iVar2 + DAT_000afb18 < 0 == (iVar2 < 0 != iVar5 < 0 && iVar5 < 0 == iVar2 + DAT_000afb18 < 0)
       && iVar2 != iVar5)) &&
      (iVar2 - DAT_000afb18 < 0 !=
       (iVar2 < 0 != DAT_000afb18 < 0 && DAT_000afb18 < 0 == iVar2 - DAT_000afb18 < 0))))) {
    DAT_febec1c0 = (iVar4 * DAT_febeac44 - piVar8[1] * (int)sVar6) / 2;
    iVar5 = ((*((short *)camry_host_ptr((uint32_t)((int)camry_host_addr(piVar8) + 10)))) * DAT_febec1cc) / 2 +
            ((short)piVar8[2] * DAT_febec1c8) / 2 + DAT_febec1c0;
  }
  else {
    DAT_febec234 = 1;
    DAT_febec1c0 = (iVar4 * DAT_febeac44) / 2;
    iVar5 = DAT_febec1c0;
  }
  DAT_febec1c4 = iVar5 / 0x800;
  DAT_febec1d0 = DAT_febec1cc;
  DAT_febec1cc = DAT_febec1c8;
  DAT_febec1c8 = DAT_febec1c4;
  DAT_febec208 = DAT_febec200;
  DAT_febec20a = (short)(DAT_febec1c4 / 0x40);
  DAT_febec23a = DAT_febec238;
  if (DAT_febec238 == '\0') {
    DAT_febec238 = '\x01';
    DAT_febec1b8 = 0;
  }
  else {
    DAT_febec1b8 = (int)DAT_febec20a - (int)DAT_febec200;
  }
  DAT_febec1b0 = (DAT_febec1b8 * 0x4e2) / 0x10;
  if (DAT_febec1b0 + -0x7fff < 0 == (DAT_febec1b0 < 0 && -1 < DAT_febec1b0 + -0x7fff) &&
      DAT_febec1b0 != 0x7fff) {
    DAT_febec204 = 0x7fff;
  }
  else {
    DAT_febec204 = (undefined2)DAT_febec1b0;
    if (DAT_febec1b0 + 0x7fff < 0 != (-1 < DAT_febec1b0 && DAT_febec1b0 + 0x7fff < 0)) {
      DAT_febec204 = 0x8001;
    }
  }
  DAT_febec200 = DAT_febec20a;
  DAT_febec236 = DAT_febec236 | DAT_febec234;
  return;
}



/* WARNING: Removing unreachable block (ram,0x000c5de4) */
/* WARNING: Removing unreachable block (ram,0x000c5db6) */
/* WARNING: Removing unreachable block (ram,0x000c5d94) */
/* WARNING: Removing unreachable block (ram,0x000c5d7e) */
/* WARNING: Removing unreachable block (ram,0x000c5d70) */
/* WARNING: Removing unreachable block (ram,0x000c5d5c) */
/* WARNING: Removing unreachable block (ram,0x000c5d58) */
/* WARNING: Removing unreachable block (ram,0x000c5d54) */
/* WARNING: Removing unreachable block (ram,0x000c5d06) */
/* WARNING: Removing unreachable block (ram,0x000c5cfc) */
/* WARNING: Removing unreachable block (ram,0x000c5cee) */
/* WARNING: Removing unreachable block (ram,0x000c5ce0) */
/* WARNING: Removing unreachable block (ram,0x000c5ccc) */

void FUN_000c5c44(void)

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
  
  sVar5 = DAT_febec22a;
  iVar4 = DAT_febec1e4;
  iVar7 = (int)DAT_febec22c;
  iVar9 = (int)DAT_000afb20;
  uVar6 = 0;
  sVar8 = DAT_000afb20;
  if ((iVar7 - iVar9 < 0 != (iVar7 < 0 != iVar9 < 0 && iVar9 < 0 == iVar7 - iVar9 < 0) ||
       iVar7 == iVar9) &&
     (iVar9 = iVar7 + DAT_000afb20, bVar1 = -(int)DAT_000afb20 < 0, sVar8 = DAT_febec22c,
     iVar9 < 0 != (iVar7 < 0 != bVar1 && bVar1 == iVar9 < 0))) {
    sVar8 = -DAT_000afb20;
  }
  iVar7 = DAT_febec1dc -
          ((int)PTR_DAT_000af824 * (int)DAT_febec22a - (int)PTR_DAT_000af828 * (int)DAT_febec22e) /
          2;
  iVar9 = DAT_febec1e4 -
          ((DAT_febec1ec * DAT_000af838) / 2 + (DAT_000af836 * DAT_febec1e8) / 2 + DAT_febec1dc) /
          0x800;
  iVar2 = (int)DAT_febec20e - (int)(short)(DAT_febec1e4 / 0x40);
  iVar3 = -DAT_000afb10;
  if ((((iVar7 + DAT_000afb10 < 0 ==
         (iVar7 < 0 != iVar3 < 0 && iVar3 < 0 == iVar7 + DAT_000afb10 < 0) && iVar7 != iVar3) &&
       (iVar7 - DAT_000afb10 < 0 !=
        (iVar7 < 0 != DAT_000afb10 < 0 && DAT_000afb10 < 0 == iVar7 - DAT_000afb10 < 0))) &&
      (iVar7 = -DAT_000afb14,
      iVar9 + DAT_000afb14 < 0 == (iVar9 < 0 != iVar7 < 0 && iVar7 < 0 == iVar9 + DAT_000afb14 < 0)
      && iVar9 != iVar7)) &&
     (((iVar9 - DAT_000afb14 < 0 !=
        (iVar9 < 0 != DAT_000afb14 < 0 && DAT_000afb14 < 0 == iVar9 - DAT_000afb14 < 0) &&
       (iVar7 = -DAT_000afb1c,
       iVar2 + DAT_000afb1c < 0 == (iVar2 < 0 != iVar7 < 0 && iVar7 < 0 == iVar2 + DAT_000afb1c < 0)
       && iVar2 != iVar7)) &&
      (iVar2 - DAT_000afb1c < 0 !=
       (iVar2 < 0 != DAT_000afb1c < 0 && DAT_000afb1c < 0 == iVar2 - DAT_000afb1c < 0))))) {
    DAT_febec1dc = ((int)PTR_DAT_000af824 * (int)DAT_febeac44 - (int)PTR_DAT_000af828 * (int)sVar8)
                   / 2;
    iVar7 = (DAT_000af838 * DAT_febec1e8) / 2 + (DAT_000af836 * DAT_febec1e4) / 2 + DAT_febec1dc;
  }
  else {
    uVar6 = 2;
    DAT_febec1dc = ((int)PTR_DAT_000af824 * (int)DAT_febeac44) / 2;
    iVar7 = DAT_febec1dc;
  }
  DAT_febec1e0 = iVar7 / 0x800;
  DAT_febec22a = DAT_febeac44;
  DAT_febec1ec = DAT_febec1e8;
  DAT_febec1e4 = DAT_febec1e0;
  DAT_febec1e8 = iVar4;
  DAT_febec20e = (short)(DAT_febec1e0 / 0x40);
  DAT_febec22e = DAT_febec22c;
  DAT_febec22c = sVar5;
  DAT_febec218 = DAT_febeac44 - (short)(((int)DAT_febec20c * (int)DAT_febec20e) / 0x400);
  if (DAT_febec239 == '\0') {
    DAT_febec239 = '\x01';
    DAT_febec1bc = 0;
  }
  else {
    DAT_febec1bc = (int)DAT_febec218 - (int)DAT_febec202;
  }
  DAT_febec1b4 = (DAT_febec1bc * 0x4e2) / 0x10;
  if (DAT_febec1b4 + -0x7fff < 0 == (DAT_febec1b4 < 0 && -1 < DAT_febec1b4 + -0x7fff) &&
      DAT_febec1b4 != 0x7fff) {
    DAT_febec206 = 0x7fff;
  }
  else {
    DAT_febec206 = (undefined2)DAT_febec1b4;
    if (DAT_febec1b4 + 0x7fff < 0 != (-1 < DAT_febec1b4 && DAT_febec1b4 + 0x7fff < 0)) {
      DAT_febec206 = 0x8001;
    }
  }
  DAT_febec202 = DAT_febec218;
  DAT_febec234 = DAT_febec234 | uVar6;
  DAT_febec236 = DAT_febec236 | uVar6;
  return;
}



void FUN_000c5e24(void)

{
  bool bVar1;
  int iVar2;
  int iVar3;
  
  DAT_febec21c = DAT_febec216;
  DAT_febec1f0 = (DAT_febec204 + DAT_febec1f0) - (int)DAT_febec212;
  iVar3 = DAT_febec1f0 * 0x400;
  if (DAT_000af81c != 0) {
    if (iVar3 == -0x80000000 && DAT_000af81c == -1) {
      iVar3 = 0;
    }
    else {
      iVar3 = iVar3 / DAT_000af81c;
    }
  }
  iVar2 = (int)DAT_000af834;
  DAT_febec212 = (short)iVar3;
  DAT_febec21a = DAT_febec210;
  DAT_febec1f4 = (DAT_febec1f4 + DAT_febec212) - (int)DAT_febec214;
  iVar3 = DAT_febec1f4 * 0x400;
  if (DAT_000af820 != 0) {
    if (iVar3 == -0x80000000 && DAT_000af820 == -1) {
      iVar3 = 0;
    }
    else {
      iVar3 = iVar3 / DAT_000af820;
    }
  }
  DAT_febec214 = (short)iVar3;
  iVar3 = (int)DAT_febec214;
  DAT_febec23c = DAT_000af834;
  if ((iVar3 - iVar2 < 0 != (iVar3 < 0 != iVar2 < 0 && iVar2 < 0 == iVar3 - iVar2 < 0) ||
       iVar3 == iVar2) &&
     (iVar2 = iVar3 + DAT_000af834, bVar1 = -(int)DAT_000af834 < 0, DAT_febec23c = DAT_febec214,
     iVar2 < 0 != (iVar3 < 0 != bVar1 && bVar1 == iVar2 < 0))) {
    DAT_febec23c = -DAT_000af834;
  }
  DAT_febec210 = DAT_febec212;
  DAT_febec216 = DAT_febec214;
  return;
}



void FUN_000c5eae(void)

{
  bool bVar1;
  int iVar2;
  int iVar3;
  
  DAT_febec228 = DAT_febec226;
  DAT_febec1f8 = (DAT_febec206 + DAT_febec1f8) - (int)DAT_febec220;
  iVar3 = DAT_febec1f8 * 0x400;
  if (DAT_000af82c != 0) {
    if (iVar3 == -0x80000000 && DAT_000af82c == -1) {
      iVar3 = 0;
    }
    else {
      iVar3 = iVar3 / DAT_000af82c;
    }
  }
  iVar2 = (int)DAT_000af83a;
  DAT_febec220 = (short)iVar3;
  DAT_febec222 = DAT_febec21e;
  DAT_febec1fc = (DAT_febec1fc + DAT_febec220) - (int)DAT_febec224;
  iVar3 = DAT_febec1fc * 0x400;
  if (DAT_000af830 != 0) {
    if (iVar3 == -0x80000000 && DAT_000af830 == -1) {
      iVar3 = 0;
    }
    else {
      iVar3 = iVar3 / DAT_000af830;
    }
  }
  DAT_febec224 = (short)iVar3;
  iVar3 = (int)DAT_febec224;
  DAT_febec23e = DAT_000af83a;
  if ((iVar3 - iVar2 < 0 != (iVar3 < 0 != iVar2 < 0 && iVar2 < 0 == iVar3 - iVar2 < 0) ||
       iVar3 == iVar2) &&
     (iVar2 = iVar3 + DAT_000af83a, bVar1 = -(int)DAT_000af83a < 0, DAT_febec23e = DAT_febec224,
     iVar2 < 0 != (iVar3 < 0 != bVar1 && bVar1 == iVar2 < 0))) {
    DAT_febec23e = -DAT_000af83a;
  }
  DAT_febec21e = DAT_febec220;
  DAT_febec226 = DAT_febec224;
  return;
}



void FUN_000c5f38(void)

{
  uint32_t puVar1;
  int iVar2;
  
  puVar1 = 0xfebeb800u;
  iVar2 = f33_interpolate_unsigned_axis_sentinel_curve((ushort *)((undefined *)camry_host_ptr(0xaf83cu)),DAT_febeadf6);
  (*((short *)camry_host_ptr((uint32_t)(puVar1 + 0xa0c)))) = (short)iVar2;
  return;
}



/* WARNING: Removing unreachable block (ram,0x000c600e) */
/* WARNING: Removing unreachable block (ram,0x000c5fa6) */

void FUN_000c5f52(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  
  DAT_febec230 = 0;
  iVar1 = (int)DAT_febec210 - (int)DAT_febec212;
  iVar4 = DAT_febec1f0 * 0x400;
  iVar2 = -DAT_000afae8;
  if ((iVar1 + DAT_000afae8 < 0 == (iVar1 < 0 != iVar2 < 0 && iVar2 < 0 == iVar1 + DAT_000afae8 < 0)
       && iVar1 != iVar2) &&
     (iVar1 - DAT_000afae8 < 0 !=
      (iVar1 < 0 != DAT_000afae8 < 0 && DAT_000afae8 < 0 == iVar1 - DAT_000afae8 < 0))) {
    iVar4 = DAT_febec212 * DAT_000af81c;
    iVar1 = iVar4 + DAT_febec1f0 * -0x400;
    iVar2 = DAT_000afaec * DAT_000af81c;
    iVar3 = -iVar2;
    if ((iVar1 + iVar2 < 0 != (iVar1 < 0 != iVar3 < 0 && iVar3 < 0 == iVar1 + iVar2 < 0) ||
         iVar1 == iVar3) ||
       (iVar1 - iVar2 < 0 == (iVar1 < 0 != iVar2 < 0 && iVar2 < 0 == iVar1 - iVar2 < 0))) {
      DAT_febec1f0 = iVar4 / 0x400;
      DAT_febec230 = 1;
    }
  }
  else {
    if (DAT_000af81c != 0) {
      if (iVar4 == -0x80000000 && DAT_000af81c == -1) {
        iVar4 = 0;
      }
      else {
        iVar4 = iVar4 / DAT_000af81c;
      }
    }
    DAT_febec230 = 2;
    DAT_febec212 = (short)iVar4;
  }
  iVar1 = (int)DAT_febec216 - (int)DAT_febec214;
  iVar4 = DAT_febec1f4 * 0x400;
  iVar2 = -DAT_000afaf0;
  if ((iVar1 + DAT_000afaf0 < 0 == (iVar1 < 0 != iVar2 < 0 && iVar2 < 0 == iVar1 + DAT_000afaf0 < 0)
       && iVar1 != iVar2) &&
     (iVar1 - DAT_000afaf0 < 0 !=
      (iVar1 < 0 != DAT_000afaf0 < 0 && DAT_000afaf0 < 0 == iVar1 - DAT_000afaf0 < 0))) {
    iVar4 = DAT_febec214 * DAT_000af820;
    iVar1 = iVar4 + DAT_febec1f4 * -0x400;
    iVar2 = DAT_000afaf4 * DAT_000af820;
    iVar3 = -iVar2;
    if ((iVar1 + iVar2 < 0 != (iVar1 < 0 != iVar3 < 0 && iVar3 < 0 == iVar1 + iVar2 < 0) ||
         iVar1 == iVar3) ||
       (iVar1 - iVar2 < 0 == (iVar1 < 0 != iVar2 < 0 && iVar2 < 0 == iVar1 - iVar2 < 0))) {
      DAT_febec1f4 = iVar4 / 0x400;
      DAT_febec230 = DAT_febec230 | 4;
    }
  }
  else {
    if (DAT_000af820 != 0) {
      if (iVar4 == -0x80000000 && DAT_000af820 == -1) {
        iVar4 = 0;
      }
      else {
        iVar4 = iVar4 / DAT_000af820;
      }
    }
    DAT_febec230 = DAT_febec230 | 8;
    DAT_febec214 = (short)iVar4;
  }
  DAT_febec232 = DAT_febec232 | DAT_febec230;
  return;
}



/* WARNING: Removing unreachable block (ram,0x000c60f8) */
/* WARNING: Removing unreachable block (ram,0x000c608c) */

void FUN_000c6038(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  ushort uVar4;
  int iVar5;
  
  uVar4 = 0;
  iVar1 = (int)DAT_febec21e - (int)DAT_febec220;
  iVar5 = DAT_febec1f8 * 0x400;
  iVar2 = -DAT_000afaf8;
  if ((iVar1 + DAT_000afaf8 < 0 == (iVar1 < 0 != iVar2 < 0 && iVar2 < 0 == iVar1 + DAT_000afaf8 < 0)
       && iVar1 != iVar2) &&
     (iVar1 - DAT_000afaf8 < 0 !=
      (iVar1 < 0 != DAT_000afaf8 < 0 && DAT_000afaf8 < 0 == iVar1 - DAT_000afaf8 < 0))) {
    iVar5 = DAT_febec220 * DAT_000af82c;
    iVar1 = iVar5 + DAT_febec1f8 * -0x400;
    iVar2 = DAT_000afafc * DAT_000af82c;
    iVar3 = -iVar2;
    if ((iVar1 + iVar2 < 0 != (iVar1 < 0 != iVar3 < 0 && iVar3 < 0 == iVar1 + iVar2 < 0) ||
         iVar1 == iVar3) ||
       (iVar1 - iVar2 < 0 == (iVar1 < 0 != iVar2 < 0 && iVar2 < 0 == iVar1 - iVar2 < 0))) {
      DAT_febec1f8 = iVar5 / 0x400;
      uVar4 = 0x10;
    }
  }
  else {
    if (DAT_000af82c != 0) {
      if (iVar5 == -0x80000000 && DAT_000af82c == -1) {
        iVar5 = 0;
      }
      else {
        iVar5 = iVar5 / DAT_000af82c;
      }
    }
    uVar4 = 0x20;
    DAT_febec220 = (short)iVar5;
  }
  iVar1 = (int)DAT_febec226 - (int)DAT_febec224;
  iVar5 = DAT_febec1fc * 0x400;
  iVar2 = -DAT_000afb00;
  if ((iVar1 + DAT_000afb00 < 0 == (iVar1 < 0 != iVar2 < 0 && iVar2 < 0 == iVar1 + DAT_000afb00 < 0)
       && iVar1 != iVar2) &&
     (iVar1 - DAT_000afb00 < 0 !=
      (iVar1 < 0 != DAT_000afb00 < 0 && DAT_000afb00 < 0 == iVar1 - DAT_000afb00 < 0))) {
    iVar5 = DAT_febec224 * DAT_000af830;
    iVar1 = iVar5 + DAT_febec1fc * -0x400;
    iVar2 = DAT_000afb04 * DAT_000af830;
    iVar3 = -iVar2;
    if ((iVar1 + iVar2 < 0 != (iVar1 < 0 != iVar3 < 0 && iVar3 < 0 == iVar1 + iVar2 < 0) ||
         iVar1 == iVar3) ||
       (iVar1 - iVar2 < 0 == (iVar1 < 0 != iVar2 < 0 && iVar2 < 0 == iVar1 - iVar2 < 0))) {
      DAT_febec1fc = iVar5 / 0x400;
      uVar4 = uVar4 | 0x40;
    }
  }
  else {
    if (DAT_000af830 != 0) {
      if (iVar5 == -0x80000000 && DAT_000af830 == -1) {
        iVar5 = 0;
      }
      else {
        iVar5 = iVar5 / DAT_000af830;
      }
    }
    uVar4 = uVar4 | 0x80;
    DAT_febec224 = (short)iVar5;
  }
  DAT_febec230 = DAT_febec230 | uVar4;
  DAT_febec232 = DAT_febec232 | uVar4;
  return;
}



void FUN_000c6128(void)

{
  FUN_000c5f52();
  FUN_000c6038();
  return;
}



/* Constant-block fill: 18 literal assignments into one contiguous cell block; shape-verified.
   Literals are default/reset values; cell meanings are not recovered. */

void f33_fill_constant_block_c6138(void)

{
  DAT_febec24c = 0;
  DAT_febec24e = 0;
  DAT_febec240 = 0;
  DAT_febec254 = 0;
  DAT_febec266 = 0;
  DAT_febec258 = 0;
  DAT_febec244 = 0;
  DAT_febec248 = 0;
  DAT_febec256 = 0;
  DAT_febec25a = 0;
  DAT_febec264 = 0;
  DAT_febec250 = 0;
  DAT_febec252 = 0;
  DAT_febec25c = 0;
  DAT_febec25e = 0;
  DAT_febec265 = 0;
  DAT_febec260 = 0;
  DAT_febec262 = 0;
  return;
}



/* WARNING: Removing unreachable block (ram,0x000c61c0) */
/* First use or C12A==1 suppresses delta but still updates previous C150. Otherwise use full
   signed32 difference, low32 multiply1250/div16 and saturation+/-32767; separately stored C250 is
   narrowed. Caller can retain this state on non5A generation. First-use/reseed suppresses delta but
   updates previous input. Otherwise full signed32 difference is scaled1250/16 and saturated; stored
   C250 is separately narrowed. */

void f33_update_assist_torque_input_delta(void)

{
  int iVar1;
  
  iVar1 = 0;
  DAT_febec265 = DAT_febec264;
  DAT_febec252 = DAT_febec24c;
  if (DAT_febec264 == '\0') {
    DAT_febec264 = '\x01';
  }
  else if (DAT_febec12a != '\x01') {
    iVar1 = (int)DAT_febec150 - (int)DAT_febec24c;
  }
  DAT_febec250 = (short)iVar1;
  DAT_febec240 = (iVar1 * 0x4e2) / 0x10;
  if (DAT_febec240 + -0x7fff < 0 == (DAT_febec240 < 0 && -1 < DAT_febec240 + -0x7fff) &&
      DAT_febec240 != 0x7fff) {
    DAT_febec24e = 0x7fff;
  }
  else {
    DAT_febec24e = (undefined2)DAT_febec240;
    if (DAT_febec240 + 0x7fff < 0 != (-1 < DAT_febec240 && DAT_febec240 + 0x7fff < 0)) {
      DAT_febec24e = 0x8001;
    }
  }
  DAT_febec24c = DAT_febec150;
  return;
}



/* Cascade retained accumulators with AF860/AF864, preserving low32 shifts and signed division.
   Publish mirrors and bound second output by AF868 into C266. */

void f33_filter_torque_rate_compensation_input(void)

{
  bool bVar1;
  int iVar2;
  int iVar3;
  
  DAT_febec25e = DAT_febec258;
  DAT_febec244 = (DAT_febec24e + DAT_febec244) - (int)DAT_febec256;
  iVar3 = DAT_febec244 * 0x400;
  if (DAT_000af860 != 0) {
    if (iVar3 == -0x80000000 && DAT_000af860 == -1) {
      iVar3 = 0;
    }
    else {
      iVar3 = iVar3 / DAT_000af860;
    }
  }
  iVar2 = (int)DAT_000af868;
  DAT_febec256 = (short)iVar3;
  DAT_febec25c = DAT_febec254;
  DAT_febec248 = (DAT_febec248 + DAT_febec256) - (int)DAT_febec25a;
  iVar3 = DAT_febec248 * 0x400;
  if (DAT_000af864 != 0) {
    if (iVar3 == -0x80000000 && DAT_000af864 == -1) {
      iVar3 = 0;
    }
    else {
      iVar3 = iVar3 / DAT_000af864;
    }
  }
  DAT_febec25a = (short)iVar3;
  iVar3 = (int)DAT_febec25a;
  DAT_febec266 = DAT_000af868;
  if ((iVar3 - iVar2 < 0 != (iVar3 < 0 != iVar2 < 0 && iVar2 < 0 == iVar3 - iVar2 < 0) ||
       iVar3 == iVar2) &&
     (iVar2 = iVar3 + DAT_000af868, bVar1 = -(int)DAT_000af868 < 0, DAT_febec266 = DAT_febec25a,
     iVar2 < 0 != (iVar3 < 0 != bVar1 && bVar1 == iVar2 < 0))) {
    DAT_febec266 = -DAT_000af868;
  }
  DAT_febec254 = DAT_febec256;
  DAT_febec258 = DAT_febec25a;
  return;
}



/* WARNING: Removing unreachable block (ram,0x000c6330) */
/* WARNING: Removing unreachable block (ram,0x000c62c8) */
/* Two stages independently compare current/mirror outputs and accumulator residuals. Strict mirror
   windows; residual equality repairs accumulator. Publish per-cycle and latched repair bits before
   filtering. */

void f33_repair_torque_rate_filter_state(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  
  DAT_febec260 = 0;
  iVar1 = (int)DAT_febec254 - (int)DAT_febec256;
  iVar4 = DAT_febec244 * 0x400;
  iVar2 = -DAT_000afb24;
  if ((iVar1 + DAT_000afb24 < 0 == (iVar1 < 0 != iVar2 < 0 && iVar2 < 0 == iVar1 + DAT_000afb24 < 0)
       && iVar1 != iVar2) &&
     (iVar1 - DAT_000afb24 < 0 !=
      (iVar1 < 0 != DAT_000afb24 < 0 && DAT_000afb24 < 0 == iVar1 - DAT_000afb24 < 0))) {
    iVar4 = DAT_febec256 * DAT_000af860;
    iVar1 = iVar4 + DAT_febec244 * -0x400;
    iVar2 = DAT_000afb28 * DAT_000af860;
    iVar3 = -iVar2;
    if ((iVar1 + iVar2 < 0 != (iVar1 < 0 != iVar3 < 0 && iVar3 < 0 == iVar1 + iVar2 < 0) ||
         iVar1 == iVar3) ||
       (iVar1 - iVar2 < 0 == (iVar1 < 0 != iVar2 < 0 && iVar2 < 0 == iVar1 - iVar2 < 0))) {
      DAT_febec244 = iVar4 / 0x400;
      DAT_febec260 = 1;
    }
  }
  else {
    if (DAT_000af860 != 0) {
      if (iVar4 == -0x80000000 && DAT_000af860 == -1) {
        iVar4 = 0;
      }
      else {
        iVar4 = iVar4 / DAT_000af860;
      }
    }
    DAT_febec260 = 2;
    DAT_febec256 = (short)iVar4;
  }
  iVar1 = (int)DAT_febec258 - (int)DAT_febec25a;
  iVar4 = DAT_febec248 * 0x400;
  iVar2 = -DAT_000afb2c;
  if ((iVar1 + DAT_000afb2c < 0 == (iVar1 < 0 != iVar2 < 0 && iVar2 < 0 == iVar1 + DAT_000afb2c < 0)
       && iVar1 != iVar2) &&
     (iVar1 - DAT_000afb2c < 0 !=
      (iVar1 < 0 != DAT_000afb2c < 0 && DAT_000afb2c < 0 == iVar1 - DAT_000afb2c < 0))) {
    iVar4 = DAT_febec25a * DAT_000af864;
    iVar1 = iVar4 + DAT_febec248 * -0x400;
    iVar2 = DAT_000afb30 * DAT_000af864;
    iVar3 = -iVar2;
    if ((iVar1 + iVar2 < 0 != (iVar1 < 0 != iVar3 < 0 && iVar3 < 0 == iVar1 + iVar2 < 0) ||
         iVar1 == iVar3) ||
       (iVar1 - iVar2 < 0 == (iVar1 < 0 != iVar2 < 0 && iVar2 < 0 == iVar1 - iVar2 < 0))) {
      DAT_febec248 = iVar4 / 0x400;
      DAT_febec260 = DAT_febec260 | 4;
    }
  }
  else {
    if (DAT_000af864 != 0) {
      if (iVar4 == -0x80000000 && DAT_000af864 == -1) {
        iVar4 = 0;
      }
      else {
        iVar4 = iVar4 / DAT_000af864;
      }
    }
    DAT_febec260 = DAT_febec260 | 8;
    DAT_febec25a = (short)iVar4;
  }
  DAT_febec262 = DAT_febec262 | DAT_febec260;
  return;
}



/* Constant-block fill: 20 literal assignments into one contiguous cell block; shape-verified.
   Literals are default/reset values; cell meanings are not recovered. */

void f33_fill_constant_block_c635a(void)

{
  DAT_febec280 = 0;
  DAT_febec268 = 0;
  DAT_febec282 = 0;
  DAT_febec26c = 0;
  DAT_febec284 = 0;
  DAT_febec270 = 0;
  DAT_febec286 = 0;
  DAT_febec288 = 0;
  DAT_febec28a = 0;
  DAT_febec274 = 0;
  DAT_febec28c = 0;
  DAT_febec278 = 0;
  DAT_febec28e = 0;
  DAT_febec27c = 0;
  DAT_febec290 = 0;
  DAT_febec292 = 0;
  DAT_febec294 = 0;
  DAT_febec296 = 0;
  DAT_febec298 = 0;
  DAT_febec29a = 0;
  return;
}



/* WARNING: Removing unreachable block (ram,0x000c6422) */
/* WARNING: Removing unreachable block (ram,0x000c6414) */
/* WARNING: Removing unreachable block (ram,0x000c63fe) */
/* WARNING: Removing unreachable block (ram,0x000c63d8) */

void FUN_000c63ac(void)

{
  int iVar1;
  
  iVar1 = (int)DAT_febeac44;
  DAT_febec280 = DAT_febeac44;
  DAT_febec282 = DAT_febeac44;
  DAT_febec286 = DAT_febeac44;
  DAT_febec288 = DAT_febeac44;
  DAT_febec28a = DAT_febeac44;
  DAT_febec28c = DAT_febeac44;
  DAT_febec290 = DAT_febeac44;
  DAT_febec268 = (DAT_000af86c * iVar1) / 0x400;
  DAT_febec292 = DAT_febeac44;
  DAT_febec270 = (iVar1 * DAT_000af874) / 0x400;
  DAT_febec274 = (iVar1 * (int)PTR_DAT_000af878) / 0x400;
  DAT_febec27c = (iVar1 * DAT_000af880) / 0x400;
  return;
}



/* WARNING: Removing unreachable block (ram,0x000c6474) */

void FUN_000c642c(void)

{
  int iVar1;
  int iVar2;
  
  iVar1 = (int)DAT_febec280;
  DAT_febec280 = DAT_febeac44;
  DAT_febec268 = iVar1 + DAT_febec268 + DAT_febeac44 + DAT_febec282 * -2;
  iVar1 = DAT_febec268 * 0x400;
  if (DAT_000af86c != 0) {
    if (iVar1 == -0x80000000 && DAT_000af86c == -1) {
      iVar1 = 0;
    }
    else {
      iVar1 = iVar1 / DAT_000af86c;
    }
  }
  DAT_febec282 = (short)iVar1;
  DAT_febec26c = (int)DAT_febec282 +
                 (DAT_000af870 * ((int)DAT_febeac44 - (int)DAT_febec282)) / 0x400;
  if (DAT_febec26c + -0x7fff < 0 == (DAT_febec26c < 0 && -1 < DAT_febec26c + -0x7fff) &&
      DAT_febec26c != 0x7fff) {
    iVar1 = 0x7fff;
  }
  else {
    iVar1 = -0x7fff;
    if (DAT_febec26c + 0x7fff < 0 == (-1 < DAT_febec26c && DAT_febec26c + 0x7fff < 0)) {
      iVar1 = (int)(short)DAT_febec26c;
    }
  }
  iVar2 = (int)DAT_febec286;
  DAT_febec284 = (short)iVar1;
  DAT_febec286 = (short)iVar1;
  DAT_febec270 = iVar2 + DAT_febec270 + iVar1 + DAT_febec288 * -2;
  iVar1 = DAT_febec270 * 0x400;
  if (DAT_000af874 != 0) {
    if (iVar1 == -0x80000000 && DAT_000af874 == -1) {
      iVar1 = 0;
    }
    else {
      iVar1 = iVar1 / DAT_000af874;
    }
  }
  DAT_febec288 = (short)iVar1;
  return;
}



void FUN_000c656c(void)

{
  bool bVar1;
  int iVar2;
  short sVar3;
  int iVar4;
  int iVar5;
  
  iVar5 = (int)DAT_000af884;
  iVar4 = (int)(short)(DAT_febec292 - DAT_febec29a);
  DAT_febec294 = DAT_febec292 - DAT_febec29a;
  sVar3 = DAT_000af884;
  if (iVar4 - iVar5 < 0 != (iVar4 < 0 != iVar5 < 0 && iVar5 < 0 == iVar4 - iVar5 < 0)) {
    iVar2 = -(int)DAT_000af884;
    iVar5 = iVar4 + DAT_000af884;
    DAT_febec296 = DAT_febec292;
    if (iVar5 < 0 == (iVar4 < 0 != iVar2 < 0 && iVar2 < 0 == iVar5 < 0) && iVar4 != iVar2)
    goto LAB_000c65a2;
    sVar3 = -DAT_000af884;
  }
  DAT_febec296 = sVar3 + DAT_febec29a;
LAB_000c65a2:
  iVar4 = (int)DAT_febec296;
  iVar5 = (int)DAT_000af886;
  DAT_febec29a = DAT_000af886;
  if ((iVar4 - iVar5 < 0 != (iVar4 < 0 != iVar5 < 0 && iVar5 < 0 == iVar4 - iVar5 < 0) ||
       iVar4 == iVar5) &&
     (iVar5 = iVar4 + DAT_000af886, bVar1 = -(int)DAT_000af886 < 0, DAT_febec29a = DAT_febec296,
     iVar5 < 0 != (iVar4 < 0 != bVar1 && bVar1 == iVar5 < 0))) {
    DAT_febec29a = -DAT_000af886;
  }
  return;
}



void FUN_000c65c8(void)

{
  uint32_t puVar1;
  char cVar2;
  
  puVar1 = 0xfebeb800u;
  cVar2 = DAT_febec298;
  if (DAT_febec298 == '\0') {
    puVar1 = 0xfebeb800u;
    FUN_000c63ac();
    cVar2 = 'Z';
  }
  FUN_000c642c();
  FUN_000c64cc();
  FUN_000c656c();
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0xa98))))) = cVar2;
  return;
}



/* Constant-block fill: 6 literal assignments into one contiguous cell block; shape-verified.
   Literals are default/reset values; cell meanings are not recovered. */

void f33_fill_constant_block_c65f0(void)

{
  DAT_febec2a6 = 0;
  DAT_febec29c = 0x400;
  DAT_febec29e = 0x400;
  DAT_febec2a0 = 0x400;
  DAT_febec2a2 = 0x400;
  DAT_febec2a4 = 0x400;
  return;
}



/* WARNING: This is an inlined function */
/* Same12-byte state and preserved R6 as C5106, feeding CE8DA. Exact94-byte body differs only in ROM
   pointer/global displacements; calibration values remain producer-local. Inline real p-code so the
   shared helper's typed argument remains connected in every caller. Prepare common gain state for
   retained C2A4; exact body matches C5106 outside ROM/global displacement fields and preserves R6
   into shared step. Local calibration meaning remains separate. */

void f33_prepare_gain_parameters_c2a4(F33GainSlewState *state,uint mode)

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
    uVar2 = *(ushort *)(((undefined *)camry_host_ptr(0xd3130u)) + iVar1 * 0x10);
    uVar6 = (*((ushort *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd312cu + (uint32_t)(iVar1 * 4) * 4u)))))));
    uVar5 = (*((ushort *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd3134u + (uint32_t)(iVar1 * 4) * 4u)))))));
    uVar4 = (*((ushort *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd3128u + (uint32_t)(iVar1 * 4) * 4u)))))));
  }
  else {
    uVar3 = '\x01';
    uVar2 = DAT_febec29c;
    uVar6 = DAT_febec2a0;
    uVar5 = DAT_febec2a2;
    uVar4 = DAT_febec29e;
  }
  state->down_step = uVar6;
  state->up_step = uVar5;
  state->down_target = uVar4;
  state->up_target = uVar2;
  state->direction = uVar3;
  return;
}



/* WARNING: Inlined function: f33_prepare_gain_parameters_c2a4 */

void FUN_000c666c(void)

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
  local_10.current = DAT_febec2a4;
  if (uVar3 < 7) {
    local_10.direction = '\x02';
    iVar1 = (short)(DAT_febeac3c & 1) * 7 + uVar3;
    local_10.up_target = *(ushort *)(((undefined *)camry_host_ptr(0xd3130u)) + iVar1 * 0x10);
    local_10.down_step = (*((ushort *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd312cu + (uint32_t)(iVar1 * 4) * 4u)))))));
    local_10.up_step = (*((ushort *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd3134u + (uint32_t)(iVar1 * 4) * 4u)))))));
    local_10.down_target = (*((ushort *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd3128u + (uint32_t)(iVar1 * 4) * 4u)))))));
  }
  else {
    local_10.direction = '\x01';
    local_10.up_target = DAT_febec29c;
    local_10.down_step = DAT_febec2a0;
    local_10.up_step = DAT_febec2a2;
    local_10.down_target = DAT_febec29e;
  }
  f33_step_retained_unsigned_gain(&local_10);
  (*((ushort *)camry_host_ptr((uint32_t)(puVar2 + 0xaa0)))) = local_10.down_step;
  (*((ushort *)camry_host_ptr((uint32_t)(puVar2 + 0xaa2)))) = local_10.up_step;
  (*((ushort *)camry_host_ptr((uint32_t)(puVar2 + 0xa9e)))) = local_10.down_target;
  (*((ushort *)camry_host_ptr((uint32_t)(puVar2 + 0xa9c)))) = local_10.up_target;
  (*((ushort *)camry_host_ptr((uint32_t)(puVar2 + 0xaa4)))) = local_10.current;
  return;
}



/* WARNING: Removing unreachable block (ram,0x000c66c2) */

void FUN_000c66b4(short param_1)

{
  DAT_febec2a6 = (short)((int)((uint)DAT_febec2a4 * (int)param_1) / 0x400);
  return;
}



/* WARNING: Removing unreachable block (ram,0x000c6746) */

void FUN_000c66ce(void)

{
  DAT_febec2d4 = 0;
  DAT_febec2e0 = 0;
  DAT_febeabac = 0;
  DAT_febec2bc = 0;
  DAT_febec2de = 0;
  DAT_febec2b0 = 0;
  DAT_febec2ac = 0;
  DAT_febec2d0 = 0;
  DAT_febec2d2 = 0;
  DAT_febec2a8 = 0;
  DAT_febec2ce = 0;
  DAT_febec2cc = 0;
  DAT_febec2ca = 0;
  DAT_febec2df = 0x5a;
  DAT_febec2c8 = 0;
  DAT_febec2c6 = 0;
  DAT_febec2c4 = 0;
  DAT_febec2c2 = 0;
  DAT_febec2b4 = PTR_DAT_000b1180;
  DAT_febec2c0 = 0;
  DAT_febec2be = 0;
  DAT_febec2e2 = 0;
  DAT_febec2da = DAT_000b11a8;
  DAT_febec2d8 = 0x400;
  DAT_febec2d6 = 0x400;
  DAT_febec2dc = DAT_000b11a8;
  DAT_febec2b8 = ((int)DAT_000b11a8 << 10) / 0x400;
  return;
}



/* WARNING: Removing unreachable block (ram,0x000c68a6) */
/* WARNING: Removing unreachable block (ram,0x000c67de) */

void FUN_000c675c(ushort param_1,short param_2,char param_3)

{
  char cVar1;
  short sVar2;
  uint32_t puVar3;
  short sVar4;
  short sVar5;
  int iVar6;
  int iVar7;
  int iVar8;
  int iVar9;
  int iVar10;
  ushort uVar11;
  short sVar12;
  
  puVar3 = 0xfebeb800u;
  iVar10 = (int)param_2;
  iVar8 = (int)DAT_febec1a6;
  iVar7 = (int)DAT_febec1a4 + (DAT_febec156 & 3) * 8;
  iVar9 = (int)DAT_000b118e;
  iVar6 = f33_interpolate_unsigned_axis_sentinel_curve
                    (((ushort *)camry_host_ptr((uint32_t)(f33_calibration_bank_bases[DAT_febeac3c & 1] + iVar7 * 0x28 + 0xa54)))
                     ,param_1);
  iVar7 = f33_interpolate_unsigned_axis_sentinel_curve
                    (((ushort *)camry_host_ptr((uint32_t)(f33_calibration_bank_bases[(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0xbc4))))) & 1] + iVar7 * 0x28 + 0xa7c))),
                     param_1);
  sVar2 = (short)(((iVar7 - iVar6) * iVar8) / 0x400) + (short)iVar6;
  if (iVar10 < 0) {
    sVar2 = -sVar2;
  }
  (*((short *)camry_host_ptr((uint32_t)(puVar3 + 0xac0)))) = (short)iVar6;
  cVar1 = DAT_000b11aa;
  (*((short *)camry_host_ptr((uint32_t)(puVar3 + 0xac2)))) = (short)iVar7;
  (*((short *)camry_host_ptr((uint32_t)(puVar3 + 0xac4)))) = sVar2;
  if (param_3 == cVar1) {
    iVar7 = (int)DAT_000b1188;
  }
  else if (param_3 == DAT_000b11ab) {
    iVar7 = (int)DAT_000b118a;
  }
  else {
    iVar7 = (int)DAT_000b118c;
  }
  sVar5 = (*((short *)camry_host_ptr((uint32_t)(puVar3 + 0xace))));
  iVar6 = (int)sVar5;
  sVar12 = (short)iVar7;
  (*((short *)camry_host_ptr((uint32_t)(puVar3 + 0xacc)))) = sVar12;
  if ((iVar10 - iVar9 < 0 == (iVar10 < 0 != iVar9 < 0 && iVar9 < 0 == iVar10 - iVar9 < 0)) ||
     (iVar8 = -iVar9,
     iVar10 + iVar9 < 0 != (iVar10 < 0 != iVar8 < 0 && iVar8 < 0 == iVar10 + iVar9 < 0) ||
     iVar10 == iVar8)) {
    uVar11 = 0;
  }
  else {
    uVar11 = (*((short *)camry_host_ptr((uint32_t)(puVar3 + 0xaca)))) + 1;
    if (DAT_000b1190 <= uVar11) {
      uVar11 = 0;
      iVar8 = iVar6;
      if ((iVar6 - iVar7 < 0 == (iVar6 < 0 != iVar7 < 0 && iVar7 < 0 == iVar6 - iVar7 < 0) &&
           iVar6 != iVar7) &&
         (sVar4 = f33_abs_s16_wrapping(sVar5 - sVar12), iVar9 = (int)DAT_000b1192,
         iVar6 = sVar4 - iVar9, iVar8 = iVar7,
         iVar6 < 0 == (sVar4 < 0 != iVar9 < 0 && iVar9 < 0 == iVar6 < 0))) {
        iVar8 = (int)(short)(sVar5 - DAT_000b1192);
      }
      iVar6 = iVar8;
      if ((iVar8 - iVar7 < 0 != (iVar8 < 0 != iVar7 < 0 && iVar7 < 0 == iVar8 - iVar7 < 0)) &&
         (sVar5 = f33_abs_s16_wrapping((short)iVar8 - sVar12), iVar10 = (int)DAT_000b1192,
         iVar9 = sVar5 - iVar10, iVar6 = iVar7,
         iVar9 < 0 == (sVar5 < 0 != iVar10 < 0 && iVar10 < 0 == iVar9 < 0))) {
        iVar6 = iVar8 + DAT_000b1192;
      }
    }
  }
  sVar5 = DAT_000b1194;
  iVar8 = (int)DAT_000b1194;
  (*((short *)camry_host_ptr((uint32_t)(puVar3 + 0xace)))) = (short)iVar6;
  (*((ushort *)camry_host_ptr((uint32_t)(puVar3 + 0xaca)))) = uVar11;
  sVar2 = (short)(((int)(short)iVar6 * (int)sVar2) / 0x400);
  iVar7 = (int)sVar2;
  (*((short *)camry_host_ptr((uint32_t)(puVar3 + 0xac6)))) = sVar2;
  if ((iVar7 - iVar8 < 0 != (iVar7 < 0 != iVar8 < 0 && iVar8 < 0 == iVar7 - iVar8 < 0) ||
       iVar7 == iVar8) &&
     (iVar6 = -iVar8, sVar5 = sVar2,
     iVar7 + iVar8 < 0 != (iVar7 < 0 != iVar6 < 0 && iVar6 < 0 == iVar7 + iVar8 < 0) ||
     iVar7 == iVar6)) {
    sVar5 = (short)iVar6;
  }
  (*((short *)camry_host_ptr((uint32_t)(puVar3 + 0xac8)))) = sVar5;
  iVar7 = ((*((int *)camry_host_ptr((uint32_t)(puVar3 + 0xaa8)))) + (int)sVar5) - (int)(*((short *)camry_host_ptr((uint32_t)(puVar3 + 0xad2))));
  (*((int *)camry_host_ptr((uint32_t)(puVar3 + 0xaa8)))) = iVar7;
  iVar7 = iVar7 * 0x400;
  if (DAT_000b117c != 0) {
    if (iVar7 == -0x80000000 && DAT_000b117c == -1) {
      iVar7 = 0;
    }
    else {
      iVar7 = iVar7 / DAT_000b117c;
    }
  }
  (*((short *)camry_host_ptr((uint32_t)(puVar3 + 0xad2)))) = (short)iVar7;
  return;
}



void FUN_000c6a68(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  
  iVar3 = (int)DAT_febec2be;
  iVar2 = (int)DAT_000b1196;
  DAT_febec2e2 = DAT_000b1196;
  if ((iVar3 - iVar2 < 0 != (iVar3 < 0 != iVar2 < 0 && iVar2 < 0 == iVar3 - iVar2 < 0) ||
       iVar3 == iVar2) &&
     (iVar1 = -iVar2, DAT_febec2e2 = DAT_febec2be,
     iVar3 + iVar2 < 0 != (iVar3 < 0 != iVar1 < 0 && iVar1 < 0 == iVar3 + iVar2 < 0) ||
     iVar3 == iVar1)) {
    DAT_febec2e2 = (short)iVar1;
  }
  return;
}



void FUN_000c6a88(short param_1,undefined1 param_2)

{
  FUN_000c68fa((int)param_1, (uint)(byte)param_2);
  FUN_000c69ec(param_2);
  FUN_000c6a68();
  return;
}



void FUN_000c6aa4(void)

{
  undefined1 uVar1;
  uint32_t puVar2;
  short sVar3;
  undefined4 uVar4;
  int iVar5;
  int iVar6;
  
  puVar2 = 0xfebeb800u;
  uVar4 = FUN_000d1da0(0xffc0);
  uVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(0x88e)))));
  iVar6 = (*((int *)camry_host_ptr((uint32_t)(puVar2 + 0x884))));
  FUN_000d1dc6(uVar4);
  if (iVar6 + -0x7fff < 0 == (iVar6 < 0 && -1 < iVar6 + -0x7fff) && iVar6 != 0x7fff) {
    iVar5 = 0x7fff;
  }
  else {
    iVar5 = (int)(short)iVar6;
    if (iVar6 + 0x7fff < 0 != (-1 < iVar6 && iVar6 + 0x7fff < 0)) {
      iVar5 = -0x7fff;
    }
  }
  sVar3 = f33_abs_s16_wrapping((short)iVar5);
  FUN_000c675c((int)sVar3,iVar5,uVar1);
  FUN_000c6a88((int)sVar3,uVar1);
  return;
}



void FUN_000c6af6(void)

{
  char cVar1;
  ushort uVar2;
  uint32_t puVar3;
  short sVar4;
  int iVar5;
  int iVar6;
  int iVar7;
  char cVar8;
  int iVar9;
  short *psVar10;
  
  cVar1 = DAT_febec5f4;
  uVar2 = DAT_febeadf6;
  puVar3 = 0xfebeb800u;
  sVar4 = f33_abs_s16_wrapping(DAT_febec5ec);
  iVar5 = (int)sVar4;
  cVar8 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(0xae0)))));
  iVar9 = (int)DAT_000b11a0;
  iVar6 = (int)DAT_000b11a2;
  if (cVar8 == '\0') {
    if (((cVar1 != '\x01') ||
        (iVar5 - iVar9 < 0 != (iVar5 < 0 != iVar9 < 0 && iVar9 < 0 == iVar5 - iVar9 < 0) ||
         iVar5 == iVar9)) || (uVar2 <= DAT_000b119e)) goto LAB_000c6b74;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(0xae0))))) = 1;
    cVar8 = '\x01';
  }
  else if (((cVar1 == '\0') ||
           (iVar5 - iVar6 < 0 != (iVar5 < 0 != iVar6 < 0 && iVar6 < 0 == iVar5 - iVar6 < 0) ||
            iVar5 == iVar6)) || (uVar2 <= DAT_000b119e)) {
    uVar2 = (*((ushort *)camry_host_ptr((uint32_t)(puVar3 + 0xad4))));
    if (uVar2 <= DAT_000b11a4) {
      sVar4 = uVar2 + 1;
      uVar2 = uVar2 + 1;
      (*((short *)camry_host_ptr((uint32_t)(puVar3 + 0xad4)))) = sVar4;
    }
    if (DAT_000b11a4 < uVar2) {
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(0xae0))))) = 0;
      cVar8 = '\0';
    }
    goto LAB_000c6b74;
  }
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + 0xad4)))) = 0;
LAB_000c6b74:
  iVar5 = (int)(*((short *)camry_host_ptr((uint32_t)(puVar3 + 0xadc))));
  if (cVar8 == '\x01') {
    psVar10 = ((undefined *)camry_host_ptr(0xb11a6u));
    iVar6 = 0;
  }
  else {
    psVar10 = ((undefined *)camry_host_ptr(0xb11a8u));
    iVar6 = 0x400;
  }
  iVar7 = (int)*psVar10;
  iVar9 = (*((int *)camry_host_ptr((uint32_t)(puVar3 + 0xab8)))) * (int)*psVar10;
  (*((short *)camry_host_ptr((uint32_t)(puVar3 + 0xada)))) = *psVar10;
  sVar4 = *psVar10;
  (*((short *)camry_host_ptr((uint32_t)(puVar3 + 0xad8)))) = (short)iVar6;
  if (iVar5 != 0) {
    if (iVar9 == -0x80000000 && iVar5 == -1) {
      iVar9 = -0x80000000;
    }
    else {
      iVar9 = iVar9 / iVar5;
    }
  }
  (*((short *)camry_host_ptr((uint32_t)(puVar3 + 0xadc)))) = sVar4;
  iVar5 = (iVar6 + iVar9) - (int)(*((short *)camry_host_ptr((uint32_t)(puVar3 + 0xad6))));
  (*((int *)camry_host_ptr((uint32_t)(puVar3 + 0xab8)))) = iVar5;
  iVar5 = iVar5 * 0x400;
  if (iVar7 != 0) {
    if (iVar5 == -0x80000000 && iVar7 == -1) {
      iVar5 = 0;
    }
    else {
      iVar5 = iVar5 / iVar7;
    }
  }
  (*((short *)camry_host_ptr((uint32_t)(puVar3 + 0xad6)))) = (short)iVar5;
  sVar4 = f33_abs_s16_wrapping((short)iVar5 - (short)iVar6);
  iVar5 = (int)sVar4;
  if (iVar5 + -0x14 < 0 != (iVar5 < 0 && -1 < iVar5 + -0x14) || iVar5 == 0x14) {
    (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + 0xad6)))) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + 0xad8))));
  }
  return;
}



void FUN_000c6be0(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  
  DAT_febec2e4 = 0;
  DAT_febec2ee = 0x400;
  DAT_febec2ec = 0x400;
  DAT_febec2f0 = 0x400;
  DAT_febec2f2 = 0x400;
  DAT_febec2f4 = 0x400;
  iVar3 = 0;
  do {
    *(undefined2 *)(((undefined *)camry_host_ptr(0xfebec300u)) + iVar3 * 2) = 0x400;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebec2f8u + (uint32_t)(iVar3) * 1u)))) = 0;
    iVar2 = iVar3 + 1;
    iVar1 = iVar3 + -6;
    iVar3 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  DAT_febec2f6 = 0x400;
  DAT_febec2e8 = 0;
  return;
}



/* WARNING: This is an inlined function */
/* Same12-byte state and preserved R6 as C5106, feeding CE8DA. Exact94-byte body differs only in ROM
   pointer/global displacements; calibration values remain producer-local. Inline real p-code so the
   shared helper's typed argument remains connected in every caller. Prepare common gain state for
   C2F4 with retained/default mode path and preserved R6; target values remain producer-local. */

void f33_prepare_gain_parameters_c2f4(F33GainSlewState *state,uint mode)

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
    uVar2 = *(ushort *)(((undefined *)camry_host_ptr(0xd3210u)) + iVar1 * 0x10);
    uVar6 = (*((ushort *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd320cu + (uint32_t)(iVar1 * 4) * 4u)))))));
    uVar5 = (*((ushort *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd3214u + (uint32_t)(iVar1 * 4) * 4u)))))));
    uVar4 = (*((ushort *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd3208u + (uint32_t)(iVar1 * 4) * 4u)))))));
  }
  else {
    uVar3 = '\x01';
    uVar2 = DAT_febec2ec;
    uVar6 = DAT_febec2f0;
    uVar5 = DAT_febec2f2;
    uVar4 = DAT_febec2ee;
  }
  state->down_step = uVar6;
  state->up_step = uVar5;
  state->down_target = uVar4;
  state->up_target = uVar2;
  state->direction = uVar3;
  return;
}



/* WARNING: Inlined function: f33_prepare_gain_parameters_c2f4 */

void FUN_000c6c82(void)

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
  local_10.current = DAT_febec2f4;
  if (uVar3 < 7) {
    local_10.direction = '\x02';
    iVar1 = (short)(DAT_febeac3c & 1) * 7 + uVar3;
    local_10.up_target = *(ushort *)(((undefined *)camry_host_ptr(0xd3210u)) + iVar1 * 0x10);
    local_10.down_step = (*((ushort *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd320cu + (uint32_t)(iVar1 * 4) * 4u)))))));
    local_10.up_step = (*((ushort *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd3214u + (uint32_t)(iVar1 * 4) * 4u)))))));
    local_10.down_target = (*((ushort *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd3208u + (uint32_t)(iVar1 * 4) * 4u)))))));
  }
  else {
    local_10.direction = '\x01';
    local_10.up_target = DAT_febec2ec;
    local_10.down_step = DAT_febec2f0;
    local_10.up_step = DAT_febec2f2;
    local_10.down_target = DAT_febec2ee;
  }
  f33_step_retained_unsigned_gain(&local_10);
  (*((ushort *)camry_host_ptr((uint32_t)(puVar2 + 0xaf0)))) = local_10.down_step;
  (*((ushort *)camry_host_ptr((uint32_t)(puVar2 + 0xaf2)))) = local_10.up_step;
  (*((ushort *)camry_host_ptr((uint32_t)(puVar2 + 0xaee)))) = local_10.down_target;
  (*((ushort *)camry_host_ptr((uint32_t)(puVar2 + 0xaec)))) = local_10.up_target;
  (*((ushort *)camry_host_ptr((uint32_t)(puVar2 + 0xaf4)))) = local_10.current;
  return;
}



void FUN_000c6cca(void)

{
  char *pcVar1;
  int iVar2;
  int iVar3;
  ushort uVar4;
  undefined8 uVar5;
  uint uVar6;
  int iVar7;
  char local_2c [4];
  undefined4 uStack_28;
  undefined4 uStack_24;
  undefined1 uStack_20;
  ushort uStack_1e;
  undefined2 uStack_1c;
  
  uVar5 = 0xfebeb800;
  uVar6 = 0x400;
  uStack_1c = DAT_febec1a2;
  uVar4 = (ushort)DAT_febeac3c;
  iVar7 = 0;
  do {
    pcVar1 = ((undefined *)camry_host_ptr(0xd32e8u)) + iVar7 * 0xc + (short)(uVar4 & 1) * 0x54;
    local_2c[0] = *pcVar1;
    if (local_2c[0] != '\a') {
      uStack_28 = *(undefined4 *)(pcVar1 + 4);
      iVar2 = iVar7 + (int)uVar5;
      iVar3 = iVar7 * 2 + (int)uVar5;
      uStack_24 = *(undefined4 *)(pcVar1 + 8);
      uStack_20 = (*((undefined1 *)camry_host_ptr((uint32_t)(iVar2 + 0xaf8))));
      uStack_1e = (*((ushort *)camry_host_ptr((uint32_t)(iVar3 + 0xb00))));
      FUN_000ce912(local_2c);
      (*((ushort *)camry_host_ptr((uint32_t)(iVar3 + 0xb00)))) = uStack_1e;
      (*((undefined1 *)camry_host_ptr((uint32_t)(iVar2 + 0xaf8)))) = uStack_20;
      uVar6 = uVar6 * uStack_1e >> 10 & 0xffff;
    }
    iVar3 = iVar7 + 1;
    iVar2 = iVar7 + -6;
    iVar7 = iVar3;
  } while (((iVar2 < 0) || (iVar3 < 0)));
  (*((short *)camry_host_ptr((uint32_t)((int)uVar5 + 0xaf6)))) = (short)uVar6;
  return;
}



void FUN_000c6d4e(void)

{
  FUN_000c6c82();
  FUN_000c6cca();
  return;
}



/* WARNING: Removing unreachable block (ram,0x000c6d7a) */
/* WARNING: Removing unreachable block (ram,0x000c6d6e) */
/* Apply C2F4 then C2F6 through separate low32 products and signed divisions1024. Publish C2E4/C2E8
   and return the second signed32 result in R10. Two separate low32 products and signed
   divisions1024 apply C2F4/C2F6 attenuation. Publish C2E4/C2E8 and return the second signed32 value
   in R10. */

int f33_apply_internal_assist_attenuation(int value)

{
  DAT_febec2e4 = (int)((uint)DAT_febec2f4 * value) / 0x400;
  DAT_febec2e8 = (int)((uint)DAT_febec2f6 * DAT_febec2e4) / 0x400;
  return DAT_febec2e8;
}



void FUN_000c6d84(void)

{
  DAT_febec35c = 0;
  DAT_febec386 = 0x400;
  DAT_febec35e = 0;
  DAT_febec360 = 0;
  DAT_febec362 = 0;
  DAT_febec364 = 0;
  DAT_febec366 = 0;
  DAT_febec368 = 0;
  DAT_febec310 = 0;
  DAT_febec36a = 0;
  DAT_febec398 = 0;
  DAT_febec399 = 0;
  DAT_febec34c = f33_calibration_bank_bases[DAT_febeac3c & 1] + 0xf54;
  DAT_febec36c = 0;
  DAT_febec36e = 0;
  DAT_febec314 = 0;
  DAT_febec318 = 0;
  DAT_febec31c = 0;
  DAT_febec320 = 0;
  DAT_febec324 = 0;
  DAT_febec328 = 0;
  DAT_febec370 = 0;
  DAT_febec372 = 0;
  DAT_febec374 = 0;
  DAT_febec376 = 0;
  DAT_febec378 = 0;
  DAT_febec37a = 0;
  DAT_febec39a = 0;
  DAT_febec32c = 0;
  DAT_febec37c = 0;
  DAT_febec37e = 0;
  DAT_febec380 = 0;
  DAT_febec330 = 0;
  DAT_febec334 = 0;
  DAT_febec382 = 0;
  DAT_febec338 = 0;
  DAT_febec33c = 0;
  DAT_febec340 = 0;
  DAT_febec384 = 0;
  DAT_febec344 = 0;
  DAT_febec348 = 0;
  DAT_febec3a0 = 0;
  DAT_febec39c = 0;
  DAT_febec388 = 0;
  DAT_febec38a = 0;
  DAT_febec38c = 0;
  DAT_febec38e = 0;
  DAT_febec390 = 0;
  DAT_febec350 = f33_calibration_bank_bases[DAT_febeac3c & 1] + 0xf70;
  DAT_febec354 = 0;
  DAT_febec358 = 0;
  DAT_febec392 = 0;
  DAT_febec394 = 0;
  DAT_febec396 = 0;
  return;
}



/* WARNING: Removing unreachable block (ram,0x000c6f04) */

void FUN_000c6e7e(void)

{
  short *points;
  short sVar1;
  short sVar2;
  uint uVar3;
  uint32_t puVar4;
  short sVar5;
  int iVar6;
  int iVar7;
  
  sVar2 = DAT_febec1a2;
  puVar4 = 0xfebeb800u;
  uVar3 = (uint)DAT_febec156;
  sVar5 = f33_abs_s16_wrapping(DAT_febec1a2);
  sVar1 = (*((short *)camry_host_ptr((uint32_t)(puVar4 + 0xb66))));
  (*((short *)camry_host_ptr((uint32_t)(puVar4 + 0xb8c)))) = (short)(uVar3 & 3);
  (*((short *)camry_host_ptr((uint32_t)(puVar4 + 0xb92)))) = (*((short *)camry_host_ptr((uint32_t)(puVar4 + 0xb64))));
  points = ((short *)camry_host_ptr((uint32_t)(f33_calibration_bank_bases[(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0xbc4))))) & 1] +
                    ((int)*(short *)(puVar4 + 0xb64) + (uVar3 & 3) * 8) * 0x1c + 0xf54)));
  iVar6 = f33_interpolate_signed_sentinel_curve(points,sVar5);
  (*((short *)camry_host_ptr((uint32_t)(puVar4 + 0xb5c)))) = (short)iVar6;
  iVar7 = f33_interpolate_signed_sentinel_curve(points + 0xe,sVar5);
  (*((short *)camry_host_ptr((uint32_t)(puVar4 + 0xb5e)))) = (short)iVar7;
  (*((short *)camry_host_ptr((uint32_t)(puVar4 + 0xb90)))) = sVar5;
  (*((short *)camry_host_ptr((uint32_t)(puVar4 + 0xb88)))) = sVar2;
  *(short **)(puVar4 + 0xb4c) = points;
  *(short **)(puVar4 + 0xb50) = points + 0xe;
  sVar1 = (short)(((iVar7 - iVar6) * (int)sVar1) / 0x400) + (short)iVar6;
  sVar5 = sVar1;
  if (sVar2 < 0) {
    sVar5 = -sVar1;
  }
  (*((short *)camry_host_ptr((uint32_t)(puVar4 + 0xb60)))) = sVar1;
  (*((short *)camry_host_ptr((uint32_t)(puVar4 + 0xb62)))) = sVar5;
  return;
}



/* WARNING: Removing unreachable block (ram,0x000c6f40) */
/* WARNING: Removing unreachable block (ram,0x000c6f34) */

void FUN_000c6f1e(void)

{
  uint32_t puVar1;
  int iVar2;
  
  puVar1 = 0xfebeb800u;
  DAT_febec344 = ((int)DAT_febec386 * (int)DAT_febec362) / 0x400;
  iVar2 = f33_apply_internal_assist_attenuation((DAT_febec344 * DAT_febec376) / 0x400);
  (*((int *)camry_host_ptr((uint32_t)(puVar1 + 0xb48)))) = iVar2;
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + 0xb96)))) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + 0xb76))));
  return;
}



/* Publish C358=C348+C5F0 with machine signed32 arithmetic. */

void f33_sum_nonlinear_and_moving_assist(void)

{
  DAT_febec358 = DAT_febec348 + DAT_febec5f0;
  return;
}



/* Bound C358 to exact B00E8=5120 and publish signed32 C39C for the nested assist aggregate. */

void f33_bound_nonlinear_and_moving_assist(void)

{
  DAT_febec39c = f33_nonlinear_moving_assist_limit;
  if ((DAT_febec358 - f33_nonlinear_moving_assist_limit < 0 !=
       (DAT_febec358 < 0 != f33_nonlinear_moving_assist_limit < 0 &&
       f33_nonlinear_moving_assist_limit < 0 == DAT_febec358 - f33_nonlinear_moving_assist_limit < 0
       ) || DAT_febec358 == f33_nonlinear_moving_assist_limit) &&
     (DAT_febec39c = -f33_nonlinear_moving_assist_limit,
     DAT_febec358 + f33_nonlinear_moving_assist_limit < 0 ==
     (DAT_febec358 < 0 != DAT_febec39c < 0 &&
     DAT_febec39c < 0 == DAT_febec358 + f33_nonlinear_moving_assist_limit < 0) &&
     DAT_febec358 != DAT_febec39c)) {
    DAT_febec39c = DAT_febec358;
  }
  return;
}



/* WARNING: Removing unreachable block (ram,0x000c7080) */
/* WARNING: Removing unreachable block (ram,0x000c702c) */

void FUN_000c6fde(void)

{
  bool bVar1;
  short sVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  
  if ((DAT_febec0d0 == '\0') || (DAT_febeac0a == 'Z')) {
    DAT_febec398 = '\x01';
  }
  else if (DAT_febec398 == '\0') {
    iVar3 = 0x400 - DAT_febec36a;
    sVar2 = DAT_000b00f4;
    goto LAB_000c7020;
  }
  iVar3 = -(int)DAT_febec36a;
  sVar2 = DAT_000b00f6;
LAB_000c7020:
  DAT_febec310 = iVar3 * sVar2 + DAT_febec310;
  DAT_febec36a = (short)(DAT_febec310 / 0x4000);
  iVar3 = (int)DAT_febec36a;
  if (DAT_febec398 == '\x01') {
    iVar4 = (int)DAT_000b00d6;
    iVar5 = iVar3 - iVar4;
    bVar1 = iVar3 < 0 != iVar4 < 0 && iVar4 < 0 == iVar5 < 0;
    DAT_febec398 = iVar5 < 0 == bVar1 && iVar3 != iVar4;
    if (iVar5 < 0 != bVar1 || iVar3 == iVar4) {
      DAT_febec36a = 0;
      DAT_febec310 = 0;
    }
  }
  else {
    iVar5 = (int)DAT_000b00d4;
    if (iVar3 - iVar5 < 0 == (iVar3 < 0 != iVar5 < 0 && iVar5 < 0 == iVar3 - iVar5 < 0)) {
      DAT_febec36a = 0x400;
      DAT_febec310 = 0x1000000;
    }
  }
  DAT_febec36c = (short)(((int)DAT_febec36a * (int)DAT_000b00f0) / 0x400);
  iVar3 = (int)DAT_febec36c;
  DAT_febec368 = DAT_febec36c;
  if (DAT_febec0cc - iVar3 < 0 !=
      (DAT_febec0cc < 0 != iVar3 < 0 && iVar3 < 0 == DAT_febec0cc - iVar3 < 0) ||
      DAT_febec0cc == iVar3) {
    iVar5 = -iVar3;
    if (DAT_febec0cc + iVar3 < 0 ==
        (DAT_febec0cc < 0 != iVar5 < 0 && iVar5 < 0 == DAT_febec0cc + iVar3 < 0) &&
        DAT_febec0cc != iVar5) {
      DAT_febec36c = (short)DAT_febec0cc;
    }
    else {
      DAT_febec36c = (short)iVar5;
    }
  }
  return;
}



/* WARNING: Removing unreachable block (ram,0x000c70cc) */

void FUN_000c709e(void)

{
  if (DAT_febec399 == '\0') {
    DAT_febec399 = '\x01';
    DAT_febec314 = 0;
  }
  else {
    DAT_febec314 = (int)DAT_febeac0e - (int)DAT_febec36e;
  }
  DAT_febec36e = DAT_febeac0e;
  DAT_febec318 = (DAT_febec314 * 500) / 0x10;
  return;
}



void FUN_000c70d6(void)

{
  int iVar1;
  int iVar2;
  
  DAT_febec31c = (DAT_febec318 + DAT_febec31c) - DAT_febec324;
  DAT_febec324 = DAT_febec31c * 0x400;
  if (DAT_000b00e0 != 0) {
    if (DAT_febec324 == -0x80000000 && DAT_000b00e0 == -1) {
      DAT_febec324 = -0x80000000;
    }
    else {
      DAT_febec324 = DAT_febec324 / DAT_000b00e0;
    }
  }
  DAT_febec320 = (DAT_febec320 + DAT_febec324) - DAT_febec328;
  DAT_febec328 = DAT_febec320 * 0x400;
  iVar2 = (int)DAT_000b00f8;
  if (DAT_000b00e4 != 0) {
    if (DAT_febec328 == -0x80000000 && DAT_000b00e4 == -1) {
      DAT_febec328 = -0x80000000;
    }
    else {
      DAT_febec328 = DAT_febec328 / DAT_000b00e4;
    }
  }
  DAT_febec370 = DAT_000b00f8;
  if (DAT_febec328 - iVar2 < 0 !=
      (DAT_febec328 < 0 != iVar2 < 0 && iVar2 < 0 == DAT_febec328 - iVar2 < 0) ||
      DAT_febec328 == iVar2) {
    iVar1 = -iVar2;
    if (DAT_febec328 + iVar2 < 0 ==
        (DAT_febec328 < 0 != iVar1 < 0 && iVar1 < 0 == DAT_febec328 + iVar2 < 0) &&
        DAT_febec328 != iVar1) {
      DAT_febec370 = (short)DAT_febec328;
    }
    else {
      DAT_febec370 = (short)iVar1;
    }
  }
  return;
}



void FUN_000c71b6(void)

{
  uint32_t puVar1;
  int iVar2;
  
  puVar1 = 0xfebeb800u;
  iVar2 = f33_interpolate_unsigned_axis_sentinel_curve((ushort *)((undefined *)camry_host_ptr(0xb0102u)),DAT_febeadf6);
  (*((short *)camry_host_ptr((uint32_t)(puVar1 + 0xb7a)))) = (short)iVar2;
  return;
}



/* WARNING: Removing unreachable block (ram,0x000c727a) */
/* WARNING: Removing unreachable block (ram,0x000c7232) */
/* C08F==0 targets gain0 with coefficient16384; otherwise target1024 with286 unless the completion
   latch still requires clearing. Retained accumulator divisor16384. C37E=1792+3328*C37C/1024:
   qualification loss reduces the bound, NOT to zero. Qualification-dependent retained gain
   targets0/1024 with coefficients16384/286 and divisor16384. C37E=1792+3328*gain/1024; cleared gain
   gives1792 not zero or7. Not a steering veto. */

void f33_update_observer_dependent_assist_bound(void)

{
  bool bVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  
  iVar4 = (int)DAT_000b00da;
  iVar2 = (int)DAT_000b00fe;
  if (DAT_febec08f == '\0') {
    DAT_febec39a = '\x01';
    iVar2 = (int)DAT_000b0100;
    iVar5 = iVar4;
  }
  else {
    iVar5 = (int)DAT_000b00d8;
    if (DAT_febec39a != '\0') {
      iVar2 = (int)DAT_000b0100;
      iVar5 = iVar4;
    }
  }
  DAT_febec32c = (iVar5 - DAT_febec37c) * iVar2 + DAT_febec32c;
  iVar2 = (int)(short)(DAT_febec32c / 0x4000);
  if (DAT_febec39a == '\x01') {
    iVar3 = (int)DAT_000b00dc;
    iVar5 = iVar2 - iVar3;
    bVar1 = iVar2 < 0 != iVar3 < 0 && iVar3 < 0 == iVar5 < 0;
    DAT_febec39a = iVar5 < 0 == bVar1 && iVar2 != iVar3;
    if (iVar5 < 0 == bVar1 && iVar2 != iVar3) goto LAB_000c7264;
  }
  else {
    iVar5 = (int)DAT_000b00de;
    iVar4 = (int)DAT_000b00d8;
    if (iVar2 - iVar5 < 0 != (iVar2 < 0 != iVar5 < 0 && iVar5 < 0 == iVar2 - iVar5 < 0))
    goto LAB_000c7264;
  }
  iVar2 = iVar4;
  DAT_febec32c = iVar2 << 0xe;
LAB_000c7264:
  DAT_febec37c = (short)iVar2;
  DAT_febec37e = (short)((((int)DAT_000b00fc - (int)DAT_000b00fa) * iVar2) / 0x400) + DAT_000b00fa;
  return;
}



/* Clamp C084 symmetrically to+/-32767, map its magnitude through B0126 and publish C378. This is an
   assist amplitude bound, not a phase counter or sample-age flag. Clamp observer rate to+-32767;
   map its magnitude through B0126 into C378. This bound joins the observer-dependent assist
   aggregate. */

void f33_map_observer_rate_to_assist_bound(void)

{
  uint32_t puVar1;
  short sVar2;
  int iVar3;
  
  puVar1 = 0xfebeb800u;
  if (DAT_febec084 + -0x7fff < 0 == (DAT_febec084 < 0 && -1 < DAT_febec084 + -0x7fff) &&
      DAT_febec084 != 0x7fff) {
    sVar2 = 0x7fff;
  }
  else {
    sVar2 = (short)DAT_febec084;
    if (DAT_febec084 + 0x7fff < 0 != (-1 < DAT_febec084 && DAT_febec084 + 0x7fff < 0)) {
      sVar2 = -0x7fff;
    }
  }
  sVar2 = f33_abs_s16_wrapping(sVar2);
  iVar3 = f33_interpolate_signed_sentinel_curve((short *)((undefined *)camry_host_ptr(0xb0126u)),sVar2);
  (*((short *)camry_host_ptr((uint32_t)(puVar1 + 0xb78)))) = (short)iVar3;
  return;
}



/* Sum signed16 C894,C4A0,C3EA,C524,C2E2 into s32C330; clamp toC378 intoC334, then to
   min(C37E,C37A), narrow intoC3A0. D0162 consumes this term intoCC2C: no direct C084 read in the
   command slice does NOT mean independence from the observer. Sum C894+C4A0+C3EA+C524+C2E2 into
   signed32 C330; clamp by C378 then min(C37E,C37A); narrow C3A0. D0162 carries the result into CC2C
   and D0218, so absent direct observer reads do not imply independence. */

void f33_compose_observer_dependent_assist(void)

{
  int iVar1;
  int iVar2;
  
  iVar2 = (int)DAT_febec378;
  DAT_febec330 = (int)DAT_febec894 +
                 (int)DAT_febec4a0 + (int)DAT_febec3ea + (int)DAT_febec524 + (int)DAT_febec2e2;
  DAT_febec334 = iVar2;
  if ((DAT_febec330 - iVar2 < 0 !=
       (DAT_febec330 < 0 != iVar2 < 0 && iVar2 < 0 == DAT_febec330 - iVar2 < 0) ||
       DAT_febec330 == iVar2) &&
     (DAT_febec334 = -iVar2,
     DAT_febec330 + iVar2 < 0 ==
     (DAT_febec330 < 0 != DAT_febec334 < 0 && DAT_febec334 < 0 == DAT_febec330 + iVar2 < 0) &&
     DAT_febec330 != DAT_febec334)) {
    DAT_febec334 = DAT_febec330;
  }
  iVar1 = (int)DAT_febec37e;
  iVar2 = (int)DAT_febec37a;
  if (iVar1 - iVar2 < 0 != (iVar1 < 0 != iVar2 < 0 && iVar2 < 0 == iVar1 - iVar2 < 0)) {
    iVar2 = iVar1;
  }
  DAT_febec380 = (short)iVar2;
  iVar1 = iVar2;
  if ((DAT_febec334 - iVar2 < 0 !=
       (DAT_febec334 < 0 != iVar2 < 0 && iVar2 < 0 == DAT_febec334 - iVar2 < 0) ||
       DAT_febec334 == iVar2) &&
     (iVar1 = -iVar2,
     DAT_febec334 + iVar2 < 0 ==
     (DAT_febec334 < 0 != iVar1 < 0 && iVar1 < 0 == DAT_febec334 + iVar2 < 0) &&
     DAT_febec334 != iVar1)) {
    iVar1 = DAT_febec334;
  }
  DAT_febec3a0 = (short)iVar1;
  return;
}



/* WARNING: Removing unreachable block (ram,0x000c738c) */
/* WARNING: Removing unreachable block (ram,0x000c737c) */
/* WARNING: Removing unreachable block (ram,0x000c736c) */
/* WARNING: Removing unreachable block (ram,0x000c7352) */

void FUN_000c731c(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  
  iVar3 = (int)DAT_febec1a2;
  iVar2 = (int)DAT_000b00f2;
  DAT_febec382 = DAT_000b00f2;
  if ((iVar3 - iVar2 < 0 != (iVar3 < 0 != iVar2 < 0 && iVar2 < 0 == iVar3 - iVar2 < 0) ||
       iVar3 == iVar2) &&
     (iVar1 = -iVar2, DAT_febec382 = DAT_febec1a2,
     iVar3 + iVar2 < 0 != (iVar3 < 0 != iVar1 < 0 && iVar1 < 0 == iVar3 + iVar2 < 0) ||
     iVar3 == iVar1)) {
    DAT_febec382 = (short)iVar1;
  }
  DAT_febec38e = DAT_febeac0e;
  DAT_febec354 = ((int)DAT_febec382 * (int)DAT_febeac0e) / 0x40;
  DAT_febec394 = DAT_febec372;
  DAT_febec338 = (DAT_febec372 * DAT_febec354) / 0x200;
  DAT_febec33c = ((int)DAT_febec374 * (((int)DAT_febec36c * (int)DAT_febec370) / 4)) / 0x400;
  DAT_febec340 = DAT_febec33c + DAT_febec338;
  iVar2 = (int)DAT_000b00ec;
  iVar3 = (int)DAT_000b00ee;
  if ((DAT_febec340 - iVar2 < 0 !=
       (DAT_febec340 < 0 != iVar2 < 0 && iVar2 < 0 == DAT_febec340 - iVar2 < 0) ||
       DAT_febec340 == iVar2) &&
     (iVar2 = iVar3,
     DAT_febec340 - iVar3 < 0 ==
     (DAT_febec340 < 0 != iVar3 < 0 && iVar3 < 0 == DAT_febec340 - iVar3 < 0) &&
     DAT_febec340 != iVar3)) {
    iVar2 = DAT_febec340;
  }
  DAT_febec384 = (short)iVar2;
  DAT_febec386 = 0x400 - (short)iVar2;
  return;
}



/* Constant-block fill: 10 literal assignments into one contiguous cell block; shape-verified.
   Literals are default/reset values; cell meanings are not recovered. */

void f33_fill_constant_block_c73c4(void)

{
  DAT_febec3ba = 0;
  DAT_febec3b0 = 0;
  DAT_febec3a4 = 0;
  DAT_febec3b2 = 0;
  DAT_febec3b4 = 0;
  DAT_febec3b6 = 0;
  DAT_febeabb0 = 0;
  DAT_febec3a8 = 0;
  DAT_febec3ac = 0;
  DAT_febec3b8 = 0;
  return;
}



/* WARNING: Removing unreachable block (ram,0x000c7444) */
/* WARNING: Removing unreachable block (ram,0x000c743c) */
/* Signed C23C lookup at B11D2 times bank-specific combined-slope map and retained C3B0 gain;
   publish signed32 C3A4. */

void f33_map_first_model_derivative_compensation(void)

{
  short input;
  short sVar1;
  uint32_t puVar2;
  short sVar3;
  int iVar4;
  
  sVar1 = DAT_febec23c;
  puVar2 = 0xfebeb800u;
  sVar3 = f33_abs_s16_wrapping(DAT_febec23c);
  input = (*((short *)camry_host_ptr((uint32_t)(puVar2 + 0x740))));
  iVar4 = f33_interpolate_signed_sentinel_curve((short *)((undefined *)camry_host_ptr(0xb11d2u)),sVar3);
  sVar3 = (short)iVar4;
  if (sVar1 < 0) {
    sVar3 = -sVar3;
  }
  iVar4 = f33_interpolate_signed_sentinel_curve
                    (((short *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xb1454u + (uint32_t)((byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0xbc4))))) & 1) * 4u)))) + 0xc))),input);
  (*((int *)camry_host_ptr((uint32_t)(puVar2 + 0xba4)))) =
       ((((int)(short)iVar4 * (int)sVar3) / 0x400) * (int)(*((short *)camry_host_ptr((uint32_t)(puVar2 + 0xbb0))))) / 0x400;
  return;
}



/* WARNING: Removing unreachable block (ram,0x000c74a0) */
/* WARNING: Removing unreachable block (ram,0x000c749a) */
/* Signed C23E lookup at B11E6, narrow its C3B2-scaled product before B11AE slope scaling; publish
   signed32 ABB0. */

void f33_map_second_model_derivative_compensation(void)

{
  short input;
  short sVar1;
  uint32_t puVar2;
  short sVar3;
  int iVar4;
  
  sVar1 = DAT_febec23e;
  puVar2 = 0xfebeb800u;
  sVar3 = f33_abs_s16_wrapping(DAT_febec23e);
  input = (*((short *)camry_host_ptr((uint32_t)(puVar2 + 0x740))));
  iVar4 = f33_interpolate_signed_sentinel_curve((short *)((undefined *)camry_host_ptr(0xb11e6u)),sVar3);
  sVar3 = (short)iVar4;
  if (sVar1 < 0) {
    sVar3 = -sVar3;
  }
  (*((short *)camry_host_ptr((uint32_t)(puVar2 + 0xbb4)))) = sVar3;
  (*((short *)camry_host_ptr((uint32_t)(puVar2 + 3000)))) = sVar1;
  iVar4 = f33_interpolate_signed_sentinel_curve((short *)((undefined *)camry_host_ptr(0xb11aeu)),input);
  (*((short *)camry_host_ptr((uint32_t)(puVar2 + 0xbb6)))) = (short)iVar4;
  (*((int *)camry_host_ptr((uint32_t)(puVar2 + -0xc50)))) =
       ((int)(short)iVar4 * (int)(short)(((int)sVar3 * (int)(*((short *)camry_host_ptr((uint32_t)(puVar2 + 0xbb2))))) / 0x400)) /
       0x400;
  return;
}



/* WARNING: Removing unreachable block (ram,0x000c74c0) */
/* Add ABB0+C3A4, retain C3AC, then real low32 shift10/signed division1024 into C3A8 before B11AC
   bound into C3BA. Shift/division cannot be cancelled under wrap. */

void f33_publish_model_derivative_compensation(void)

{
  int iVar1;
  int iVar2;
  
  DAT_febec3ac = DAT_febeabb0 + DAT_febec3a4;
  DAT_febec3a8 = ((DAT_febeabb0 + DAT_febec3a4) * 0x400) / 0x400;
  iVar2 = (int)DAT_000b11ac;
  DAT_febec3ba = DAT_000b11ac;
  if (DAT_febec3a8 - iVar2 < 0 !=
      (DAT_febec3a8 < 0 != iVar2 < 0 && iVar2 < 0 == DAT_febec3a8 - iVar2 < 0) ||
      DAT_febec3a8 == iVar2) {
    iVar1 = -iVar2;
    if (DAT_febec3a8 + iVar2 < 0 ==
        (DAT_febec3a8 < 0 != iVar1 < 0 && iVar1 < 0 == DAT_febec3a8 + iVar2 < 0) &&
        DAT_febec3a8 != iVar1) {
      DAT_febec3ba = (short)DAT_febec3a8;
    }
    else {
      DAT_febec3ba = (short)iVar1;
    }
  }
  return;
}



void FUN_000c7540(void)

{
  DAT_febec3e2 = 0;
  DAT_febec3e8 = 0;
  DAT_febec3e7 = 0;
  DAT_febec3de = 0;
  DAT_febec3e6 = 0;
  DAT_febec3e4 = 0;
  DAT_febec3c4 = 0;
  DAT_febec3c0 = 0;
  DAT_febec3dc = 0;
  DAT_febec3e0 = 0;
  DAT_febec3bc = 0;
  DAT_febec3cc = 0;
  DAT_febec3da = 0;
  DAT_febec3d8 = 0;
  DAT_febec3d6 = 0;
  DAT_febec3d4 = 0;
  DAT_febec3d2 = 0;
  DAT_febec3d0 = 0;
  DAT_febeabb4 = 0;
  DAT_febec3ce = 0;
  DAT_febec3ea = 0;
  DAT_febec3e9 = 0x5a;
  DAT_febec3e5 = 0x5a;
  DAT_febec3c8 = PTR_DAT_000b0140;
  return;
}



void FUN_000c75ae(void)

{
  if ((DAT_febeacd4 == '\0') && (DAT_febeacbd == '\0')) {
    if (DAT_febeacd8 == '\x01') {
      DAT_febec3de = 0;
      DAT_febec3e6 = DAT_febeacd8;
      DAT_febec3e7 = 0;
      DAT_febec3e8 = 1;
      return;
    }
    if ((DAT_febec3e6 != '\x01') && (DAT_febec3e7 != '\x01')) {
      DAT_febec3e6 = DAT_febeacd8;
      return;
    }
    if (DAT_febec3de < DAT_000b014c) {
      DAT_febec3de = DAT_febec3de + 1;
      DAT_febec3e6 = DAT_febeacd8;
      DAT_febec3e7 = 1;
      return;
    }
  }
  DAT_febec3e8 = 0;
  DAT_febec3e7 = 0;
  DAT_febec3de = 0;
  DAT_febec3e6 = DAT_febeacd8;
  return;
}



/* WARNING: Removing unreachable block (ram,0x000c76d6) */
/* WARNING: Removing unreachable block (ram,0x000c76c0) */

void FUN_000c7612(ushort param_1,short param_2)

{
  bool bVar1;
  short sVar2;
  int iVar3;
  uint32_t puVar4;
  short sVar5;
  int iVar6;
  int iVar7;
  short sVar9;
  int iVar10;
  short value;
  int iVar8;
  
  sVar2 = DAT_febec3da;
  puVar4 = 0xfebeb800u;
  iVar7 = (DAT_febec156 & 3) * 0x28;
  iVar6 = f33_interpolate_unsigned_axis_sentinel_curve
                    (((ushort *)camry_host_ptr((uint32_t)(f33_calibration_bank_bases[DAT_febeac3c & 1] + iVar7 + 0x15fc))),
                     param_1);
  iVar7 = f33_interpolate_unsigned_axis_sentinel_curve
                    ((ushort *)
                     (((undefined *)camry_host_ptr(0x155cu)) +
                     (int)(f33_calibration_bank_bases[(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0xbc4))))) & 1] + iVar7)),param_1);
  iVar10 = 0;
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(0xbe8))))) == '\x01') {
    iVar10 = 0x400;
  }
  sVar9 = (short)iVar10;
  value = sVar9 - sVar2;
  sVar5 = f33_abs_s16_wrapping(value);
  iVar8 = (int)sVar5;
  iVar3 = (int)DAT_000b014e;
  if (iVar8 - iVar3 < 0 == (iVar8 < 0 != iVar3 < 0 && iVar3 < 0 == iVar8 - iVar3 < 0) &&
      iVar8 != iVar3) {
    sVar5 = DAT_000b014e;
    if (value < 1) {
      sVar5 = -DAT_000b014e;
    }
    iVar10 = (int)(short)(sVar5 + sVar2);
  }
  (*((short *)camry_host_ptr((uint32_t)(puVar4 + 0xbda)))) = (short)iVar10;
  (*((short *)camry_host_ptr((uint32_t)(puVar4 + 0xbd2)))) = (short)iVar6;
  (*((short *)camry_host_ptr((uint32_t)(puVar4 + 0xbd4)))) = (short)iVar7;
  (*((short *)camry_host_ptr((uint32_t)(puVar4 + 0xbd8)))) = sVar9;
  sVar2 = (short)(((iVar6 - iVar7) * iVar10) / 0x400) + (short)iVar7;
  (*((short *)camry_host_ptr((uint32_t)(puVar4 + 0xbd6)))) = sVar2;
  sVar2 = (short)(((int)(*((short *)camry_host_ptr((uint32_t)(puVar4 + 0xbcc)))) * (int)sVar2) / 0x400);
  if (param_2 < 0) {
    sVar2 = -sVar2;
  }
  iVar7 = (int)DAT_000b0148;
  iVar6 = (int)sVar2;
  (*((short *)camry_host_ptr((uint32_t)(puVar4 + 0xbd0)))) = sVar2;
  sVar9 = DAT_000b0148;
  if ((iVar6 - iVar7 < 0 != (iVar6 < 0 != iVar7 < 0 && iVar7 < 0 == iVar6 - iVar7 < 0) ||
       iVar6 == iVar7) &&
     (iVar7 = iVar6 + DAT_000b0148, bVar1 = -(int)DAT_000b0148 < 0, sVar9 = sVar2,
     iVar7 < 0 != (iVar6 < 0 != bVar1 && bVar1 == iVar7 < 0))) {
    sVar9 = -DAT_000b0148;
  }
  iVar7 = ((*((int *)camry_host_ptr((uint32_t)(puVar4 + 0xbbc)))) + (int)sVar9) - (int)(*((short *)camry_host_ptr((uint32_t)(puVar4 + 0xbe0))));
  (*((int *)camry_host_ptr((uint32_t)(puVar4 + 0xbbc)))) = iVar7;
  iVar7 = iVar7 * 0x400;
  if (DAT_000b013c != 0) {
    if (iVar7 == -0x80000000 && DAT_000b013c == -1) {
      iVar7 = 0;
    }
    else {
      iVar7 = iVar7 / DAT_000b013c;
    }
  }
  (*((short *)camry_host_ptr((uint32_t)(puVar4 + 0xbe0)))) = (short)iVar7;
  return;
}



void FUN_000c772a(void)

{
  if ((DAT_febead18 == '\x11') && (DAT_febeadf6 <= DAT_000b0156)) {
    if (DAT_000b0158 <= DAT_febec3e2) {
      DAT_febec3e9 = 0x5a;
      return;
    }
    DAT_febec3e2 = DAT_febec3e2 + 1;
    return;
  }
  DAT_febec3e2 = 0;
  DAT_febec3e9 = 0;
  return;
}



/* WARNING: Removing unreachable block (ram,0x000c7880) */

void FUN_000c786c(char param_1)

{
  int iVar1;
  
  iVar1 = ((int)DAT_febec3dc * (int)DAT_febec3e0) / 0x100;
  if (iVar1 + -0x7fff < 0 == (iVar1 < 0 && -1 < iVar1 + -0x7fff) && iVar1 != 0x7fff) {
    iVar1 = 0x7fff;
  }
  else if (iVar1 + 0x7fff < 0 != (-1 < iVar1 && iVar1 + 0x7fff < 0)) {
    iVar1 = -0x7fff;
  }
  DAT_febeabb4 = (undefined2)iVar1;
  if (param_1 == '\0') {
    DAT_febec3e5 = 'Z';
  }
  else {
    if (DAT_febec3e4 == '\0') {
      DAT_febec3ce = DAT_febeabb4;
      DAT_febec3e5 = 0;
      return;
    }
    if (DAT_febec3e5 != 'Z') {
      DAT_febec3ce = DAT_febeabb4;
      return;
    }
  }
  DAT_febec3ce = DAT_febeabb4;
  DAT_febeabb4 = 0;
  return;
}



void FUN_000c78cc(void)

{
  bool bVar1;
  int iVar2;
  int iVar3;
  
  iVar3 = (int)DAT_febeabb4;
  iVar2 = (int)DAT_000b014a;
  DAT_febec3ea = DAT_000b014a;
  if ((iVar3 - iVar2 < 0 != (iVar3 < 0 != iVar2 < 0 && iVar2 < 0 == iVar3 - iVar2 < 0) ||
       iVar3 == iVar2) &&
     (iVar2 = iVar3 + DAT_000b014a, bVar1 = -(int)DAT_000b014a < 0, DAT_febec3ea = DAT_febeabb4,
     iVar2 < 0 != (iVar3 < 0 != bVar1 && bVar1 == iVar2 < 0))) {
    DAT_febec3ea = -DAT_000b014a;
  }
  return;
}



void FUN_000c7912(void)

{
  undefined1 uVar1;
  uint32_t puVar2;
  short sVar3;
  undefined4 uVar4;
  int iVar5;
  int iVar6;
  
  puVar2 = 0xfebeb800u;
  uVar4 = FUN_000d1da0(0xffc0);
  uVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(0x88e)))));
  iVar6 = (*((int *)camry_host_ptr((uint32_t)(puVar2 + 0x884))));
  FUN_000d1dc6(uVar4);
  if (iVar6 + -0x7fff < 0 == (iVar6 < 0 && -1 < iVar6 + -0x7fff) && iVar6 != 0x7fff) {
    iVar5 = 0x7fff;
  }
  else {
    iVar5 = (int)(short)iVar6;
    if (iVar6 + 0x7fff < 0 != (-1 < iVar6 && iVar6 + 0x7fff < 0)) {
      iVar5 = -0x7fff;
    }
  }
  FUN_000c75ae();
  sVar3 = f33_abs_s16_wrapping((short)iVar5);
  FUN_000c7612((int)sVar3,iVar5);
  FUN_000c78f2((int)sVar3,uVar1);
  return;
}



void FUN_000c7966(void)

{
  uint32_t puVar1;
  int iVar2;
  
  puVar1 = 0xfebeb800u;
  iVar2 = f33_interpolate_unsigned_axis_sentinel_curve
                    (((ushort *)camry_host_ptr((uint32_t)(0x169cu +
                     (int)(f33_calibration_bank_bases[DAT_febeac3c & 1] + (DAT_febec156 & 3) * 0x24)
                     ))),DAT_febeadf6);
  (*((short *)camry_host_ptr((uint32_t)(puVar1 + 0xbcc)))) = (short)iVar2;
  return;
}



/* Constant-block fill: 5 literal assignments into one contiguous cell block; shape-verified.
   Literals are default/reset values; cell meanings are not recovered. */

void f33_fill_constant_block_c79a0(void)

{
  DAT_febec3ec = 0x400;
  DAT_febec3ee = 0x400;
  DAT_febec3f0 = 0x400;
  DAT_febec3f2 = 0x400;
  DAT_febec3f4 = 0x400;
  return;
}



/* WARNING: This is an inlined function */
/* Same12-byte state and preserved R6 as C5106, feeding CE8DA. Exact94-byte body differs only in ROM
   pointer/global displacements; calibration values remain producer-local. Inline real p-code so the
   shared helper's typed argument remains connected in every caller. Prepare common gain state for
   C3F4; pointer/inline-field loads and preserved R6 are instruction-equivalent to C5106 outside
   known displacements. */

void f33_prepare_gain_parameters_c3f4(F33GainSlewState *state,uint mode)

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
    uVar2 = *(ushort *)(((undefined *)camry_host_ptr(0xd3398u)) + iVar1 * 0x10);
    uVar6 = (*((ushort *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd3394u + (uint32_t)(iVar1 * 4) * 4u)))))));
    uVar5 = **(ushort **)(((undefined *)camry_host_ptr(0xd339cu)) + iVar1 * 0x10);
    uVar4 = (*((ushort *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd3390u + (uint32_t)(iVar1 * 4) * 4u)))))));
  }
  else {
    uVar3 = '\x01';
    uVar2 = DAT_febec3ec;
    uVar6 = DAT_febec3f0;
    uVar5 = DAT_febec3f2;
    uVar4 = DAT_febec3ee;
  }
  state->down_step = uVar6;
  state->up_step = uVar5;
  state->down_target = uVar4;
  state->up_target = uVar2;
  state->direction = uVar3;
  return;
}



/* WARNING: Inlined function: f33_prepare_gain_parameters_c3f4 */

void FUN_000c7a18(void)

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
  local_10.current = DAT_febec3f4;
  if (uVar3 < 7) {
    local_10.direction = '\x02';
    iVar1 = (short)(DAT_febeac3c & 1) * 7 + uVar3;
    local_10.up_target = *(ushort *)(((undefined *)camry_host_ptr(0xd3398u)) + iVar1 * 0x10);
    local_10.down_step = (*((ushort *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd3394u + (uint32_t)(iVar1 * 4) * 4u)))))));
    local_10.up_step = **(ushort **)(((undefined *)camry_host_ptr(0xd339cu)) + iVar1 * 0x10);
    local_10.down_target = (*((ushort *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd3390u + (uint32_t)(iVar1 * 4) * 4u)))))));
  }
  else {
    local_10.direction = '\x01';
    local_10.up_target = DAT_febec3ec;
    local_10.down_step = DAT_febec3f0;
    local_10.up_step = DAT_febec3f2;
    local_10.down_target = DAT_febec3ee;
  }
  f33_step_retained_unsigned_gain(&local_10);
  (*((ushort *)camry_host_ptr((uint32_t)(puVar2 + 0xbf0)))) = local_10.down_step;
  (*((ushort *)camry_host_ptr((uint32_t)(puVar2 + 0xbf2)))) = local_10.up_step;
  (*((ushort *)camry_host_ptr((uint32_t)(puVar2 + 0xbee)))) = local_10.down_target;
  (*((ushort *)camry_host_ptr((uint32_t)(puVar2 + 0xbec)))) = local_10.up_target;
  (*((ushort *)camry_host_ptr((uint32_t)(puVar2 + 0xbf4)))) = local_10.current;
  return;
}



/* WARNING: Removing unreachable block (ram,0x000c7a6e) */

int FUN_000c7a60(short param_1)

{
  return (int)(short)((int)((uint)DAT_febec3f4 * (int)param_1) / 0x400);
}



/* Constant-block fill: 14 literal assignments into one contiguous cell block; shape-verified.
   Literals are default/reset values; cell meanings are not recovered. */

void f33_fill_constant_block_c7a76(void)

{
  DAT_febec41c = 0;
  DAT_febec410 = 0;
  DAT_febec412 = 0;
  DAT_febec414 = 0;
  DAT_febec416 = 0;
  DAT_febec3f8 = 0;
  DAT_febec3fc = 0;
  DAT_febec400 = 0;
  DAT_febec404 = 0;
  DAT_febec408 = 0;
  DAT_febec418 = 0;
  DAT_febec41a = 0;
  DAT_febec40c = 0;
  DAT_febec41e = 0;
  return;
}



/* WARNING: Removing unreachable block (ram,0x000c7b28) */
/* WARNING: Removing unreachable block (ram,0x000c7af2) */

void FUN_000c7ab0(ushort param_1)

{
  short sVar1;
  uint32_t puVar2;
  undefined2 uVar3;
  int iVar4;
  int iVar5;
  
  sVar1 = DAT_febec474;
  puVar2 = 0xfebeb800u;
  iVar5 = (DAT_febec156 & 3) * 0x24;
  iVar4 = f33_interpolate_unsigned_axis_sentinel_curve
                    (((ushort *)camry_host_ptr((uint32_t)(f33_calibration_bank_bases[DAT_febeac3c & 1] + iVar5 + 0x172c))),
                     param_1);
  (*((short *)camry_host_ptr((uint32_t)(puVar2 + 0xc12)))) = (short)iVar4;
  uVar3 = FUN_000c7a60((int)(short)(((int)sVar1 * (int)(short)iVar4) / 0x400));
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar2 + 0xc14)))) = uVar3;
  iVar5 = f33_interpolate_unsigned_axis_sentinel_curve
                    (((ushort *)camry_host_ptr((uint32_t)(f33_calibration_bank_bases[(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0xbc4))))) & 1] + iVar5 + 0x17bc))),param_1
                    );
  (*((short *)camry_host_ptr((uint32_t)(puVar2 + 0xc16)))) = (short)((int)(iVar5 * (uint)(*((ushort *)camry_host_ptr((uint32_t)(puVar2 + -0x9c6))))) / 0x40000);
  return;
}



void FUN_000c7b34(void)

{
  FUN_000c7ab0(DAT_febeadf6);
  return;
}



/* WARNING: Removing unreachable block (ram,0x000c7c16) */
/* WARNING: Removing unreachable block (ram,0x000c7bd2) */
/* WARNING: Removing unreachable block (ram,0x000c7bb0) */

void FUN_000c7b44(void)

{
  int iVar1;
  short sVar2;
  uint uVar3;
  int iVar4;
  uint32_t puVar6;
  ushort input;
  int iVar7;
  int iVar8;
  short sVar9;
  int iVar10;
  int iVar5;
  
  iVar5 = DAT_febeac90;
  sVar9 = DAT_000b1200;
  puVar6 = 0xfebeb800u;
  uVar3 = (uint)DAT_febec156;
  iVar10 = (int)DAT_000b1200;
  iVar1 = -DAT_febeac90;
  if (DAT_febec41c == '\0') {
    DAT_febec41c = '\x01';
    DAT_febec400 = iVar1;
  }
  input = f33_abs_s16_wrapping(DAT_febeac44);
  iVar7 = f33_interpolate_unsigned_axis_sentinel_curve
                    (((ushort *)camry_host_ptr((uint32_t)(f33_calibration_bank_bases[(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(-0xbc4))))) & 1] +
                     (uVar3 & 3) * 0x1c + 0x184c))),input);
  (*((short *)camry_host_ptr((uint32_t)(puVar6 + 0xc10)))) = (short)iVar7;
  iVar8 = (int)(*((short *)camry_host_ptr((uint32_t)(puVar6 + 0xc16))));
  iVar7 = ((int)(*((short *)camry_host_ptr((uint32_t)(puVar6 + 0xc14)))) * (int)(short)iVar7) / 0x400;
  (*((int *)camry_host_ptr((uint32_t)(puVar6 + 0xbf8)))) = iVar7;
  if (iVar8 == 0) {
    (*((undefined4 *)camry_host_ptr((uint32_t)(puVar6 + 0xbfc)))) = 0;
    (*((undefined4 *)camry_host_ptr((uint32_t)(puVar6 + 0xbf8)))) = 0;
    iVar4 = 0;
    iVar7 = 0;
  }
  else {
    iVar4 = (iVar7 << 0x12) / 0x168;
    if (iVar8 != 0) {
      if (iVar4 == -0x80000000 && iVar8 == -1) {
        iVar4 = -0x80000000;
      }
      else {
        iVar4 = iVar4 / iVar8;
      }
    }
    (*((int *)camry_host_ptr((uint32_t)(puVar6 + 0xbfc)))) = iVar4;
  }
  iVar5 = (*((int *)camry_host_ptr((uint32_t)(puVar6 + 0xc00)))) + iVar5;
  (*((int *)camry_host_ptr((uint32_t)(puVar6 + 0xc04)))) = iVar5;
  if (iVar5 - iVar4 < 0 == (iVar5 < 0 != iVar4 < 0 && iVar4 < 0 == iVar5 - iVar4 < 0) &&
      iVar5 != iVar4) {
    (*((int *)camry_host_ptr((uint32_t)(puVar6 + 0xc00)))) = iVar4 + iVar1;
  }
  else if (iVar5 + iVar4 < 0 == (iVar5 < 0 != -iVar4 < 0 && -iVar4 < 0 == iVar5 + iVar4 < 0)) {
    iVar7 = (iVar5 * iVar8 * 0x168) / 0x40000;
  }
  else {
    iVar7 = -iVar7;
    (*((int *)camry_host_ptr((uint32_t)(puVar6 + 0xc00)))) = iVar1 - iVar4;
  }
  (*((int *)camry_host_ptr((uint32_t)(puVar6 + 0xc08)))) = iVar7;
  iVar5 = ((*((int *)camry_host_ptr((uint32_t)(puVar6 + 0xc0c)))) + iVar7) - (int)(*((short *)camry_host_ptr((uint32_t)(puVar6 + 0xc1a))));
  (*((int *)camry_host_ptr((uint32_t)(puVar6 + 0xc0c)))) = iVar5;
  iVar5 = iVar5 * 0x400;
  if (DAT_000b11fc != 0) {
    if (iVar5 == -0x80000000 && DAT_000b11fc == -1) {
      iVar5 = 0;
    }
    else {
      iVar5 = iVar5 / DAT_000b11fc;
    }
  }
  sVar2 = (short)iVar5;
  iVar5 = (int)sVar2;
  (*((short *)camry_host_ptr((uint32_t)(puVar6 + 0xc1a)))) = sVar2;
  if ((iVar5 - iVar10 < 0 != (iVar5 < 0 != iVar10 < 0 && iVar10 < 0 == iVar5 - iVar10 < 0) ||
       iVar5 == iVar10) &&
     (iVar1 = -iVar10, sVar9 = sVar2,
     iVar5 + iVar10 < 0 != (iVar5 < 0 != iVar1 < 0 && iVar1 < 0 == iVar5 + iVar10 < 0) ||
     iVar5 == iVar1)) {
    sVar9 = (short)iVar1;
  }
  (*((short *)camry_host_ptr((uint32_t)(puVar6 + 0xc18)))) = sVar9;
  return;
}



void FUN_000c7c58(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  
  iVar3 = (int)DAT_febec418;
  iVar2 = (int)DAT_000b1200;
  DAT_febec41e = DAT_000b1200;
  if ((iVar3 - iVar2 < 0 != (iVar3 < 0 != iVar2 < 0 && iVar2 < 0 == iVar3 - iVar2 < 0) ||
       iVar3 == iVar2) &&
     (iVar1 = -iVar2, DAT_febec41e = DAT_febec418,
     iVar3 + iVar2 < 0 != (iVar3 < 0 != iVar1 < 0 && iVar1 < 0 == iVar3 + iVar2 < 0) ||
     iVar3 == iVar1)) {
    DAT_febec41e = (short)iVar1;
  }
  return;
}



/* Clear C420/C43C and initialize both retained gain families to1024. */

void f33_initialize_three_term_compensation(void)

{
  DAT_febec420 = 0;
  DAT_febec43c = 0;
  DAT_febec424 = 0x400;
  DAT_febec426 = 0x400;
  DAT_febec428 = 0x400;
  DAT_febec42a = 0x400;
  DAT_febec42c = 0x400;
  DAT_febec42e = 0;
  DAT_febec430 = 0x400;
  DAT_febec432 = 0x400;
  DAT_febec434 = 0x400;
  DAT_febec436 = 0x400;
  DAT_febec438 = 0x400;
  DAT_febec43a = 0;
  return;
}



/* WARNING: This is an inlined function */
/* Same12-byte state and preserved R6 as C5106, feeding CE8DA. Exact94-byte body differs only in ROM
   pointer/global displacements; calibration values remain producer-local. Inline real p-code so the
   shared helper's typed argument remains connected in every caller. Prepare common gain state for
   C42C; preserve actual stack-state pointer across preparation into shared unsigned step. */

void f33_prepare_gain_parameters_c42c(F33GainSlewState *state,uint mode)

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
    uVar2 = *(ushort *)(((undefined *)camry_host_ptr(0xd3478u)) + iVar1 * 0x10);
    uVar6 = (*((ushort *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd3474u + (uint32_t)(iVar1 * 4) * 4u)))))));
    uVar5 = **(ushort **)(((undefined *)camry_host_ptr(0xd347cu)) + iVar1 * 0x10);
    uVar4 = (*((ushort *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd3470u + (uint32_t)(iVar1 * 4) * 4u)))))));
  }
  else {
    uVar3 = '\x01';
    uVar2 = DAT_febec424;
    uVar6 = DAT_febec428;
    uVar5 = DAT_febec42a;
    uVar4 = DAT_febec426;
  }
  state->down_step = uVar6;
  state->up_step = uVar5;
  state->down_target = uVar4;
  state->up_target = uVar2;
  state->direction = uVar3;
  return;
}



/* WARNING: Inlined function: f33_prepare_gain_parameters_c42c */

void FUN_000c7d14(void)

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
  local_10.current = DAT_febec42c;
  if (uVar3 < 7) {
    local_10.direction = '\x02';
    iVar1 = (short)(DAT_febeac3c & 1) * 7 + uVar3;
    local_10.up_target = *(ushort *)(((undefined *)camry_host_ptr(0xd3478u)) + iVar1 * 0x10);
    local_10.down_step = (*((ushort *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd3474u + (uint32_t)(iVar1 * 4) * 4u)))))));
    local_10.up_step = **(ushort **)(((undefined *)camry_host_ptr(0xd347cu)) + iVar1 * 0x10);
    local_10.down_target = (*((ushort *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd3470u + (uint32_t)(iVar1 * 4) * 4u)))))));
  }
  else {
    local_10.direction = '\x01';
    local_10.up_target = DAT_febec424;
    local_10.down_step = DAT_febec428;
    local_10.up_step = DAT_febec42a;
    local_10.down_target = DAT_febec426;
  }
  f33_step_retained_unsigned_gain(&local_10);
  (*((ushort *)camry_host_ptr((uint32_t)(puVar2 + 0xc28)))) = local_10.down_step;
  (*((ushort *)camry_host_ptr((uint32_t)(puVar2 + 0xc2a)))) = local_10.up_step;
  (*((ushort *)camry_host_ptr((uint32_t)(puVar2 + 0xc26)))) = local_10.down_target;
  (*((ushort *)camry_host_ptr((uint32_t)(puVar2 + 0xc24)))) = local_10.up_target;
  (*((ushort *)camry_host_ptr((uint32_t)(puVar2 + 0xc2c)))) = local_10.current;
  return;
}



/* WARNING: Removing unreachable block (ram,0x000c7d6a) */
/* Unsigned C42C gain times signed16 R6, divide1024, SXH R10, store C42E and return it. Signed16 R6
   scaled by unsigned C42C then division1024 and SXH. Store C42E and return the same signed16 value;
   exact register/dataflow contract. */

short f33_scale_rate_assist_term(short value)

{
  DAT_febec42e = (short)((int)((uint)DAT_febec42c * (int)value) / 0x400);
  return DAT_febec42e;
}



/* WARNING: This is an inlined function */
/* Same12-byte state and preserved R6 as C5106, feeding CE8DA. Exact94-byte body differs only in ROM
   pointer/global displacements; calibration values remain producer-local. Inline real p-code so the
   shared helper's typed argument remains connected in every caller. Prepare common gain state for
   C438 with separate calibration/global tuple and unchanged R6 calling contract. */

void f33_prepare_gain_parameters_c438(F33GainSlewState *state,uint mode)

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
    uVar2 = *(ushort *)(((undefined *)camry_host_ptr(0xd3558u)) + iVar1 * 0x10);
    uVar6 = (*((ushort *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd3554u + (uint32_t)(iVar1 * 4) * 4u)))))));
    uVar5 = **(ushort **)(((undefined *)camry_host_ptr(0xd355cu)) + iVar1 * 0x10);
    uVar4 = (*((ushort *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd3550u + (uint32_t)(iVar1 * 4) * 4u)))))));
  }
  else {
    uVar3 = '\x01';
    uVar2 = DAT_febec430;
    uVar6 = DAT_febec434;
    uVar5 = DAT_febec436;
    uVar4 = DAT_febec432;
  }
  state->down_step = uVar6;
  state->up_step = uVar5;
  state->down_target = uVar4;
  state->up_target = uVar2;
  state->direction = uVar3;
  return;
}



/* WARNING: Inlined function: f33_prepare_gain_parameters_c438 */

void FUN_000c7dd4(void)

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
  local_10.current = DAT_febec438;
  if (uVar3 < 7) {
    local_10.direction = '\x02';
    iVar1 = (short)(DAT_febeac3c & 1) * 7 + uVar3;
    local_10.up_target = *(ushort *)(((undefined *)camry_host_ptr(0xd3558u)) + iVar1 * 0x10);
    local_10.down_step = (*((ushort *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd3554u + (uint32_t)(iVar1 * 4) * 4u)))))));
    local_10.up_step = **(ushort **)(((undefined *)camry_host_ptr(0xd355cu)) + iVar1 * 0x10);
    local_10.down_target = (*((ushort *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd3550u + (uint32_t)(iVar1 * 4) * 4u)))))));
  }
  else {
    local_10.direction = '\x01';
    local_10.up_target = DAT_febec430;
    local_10.down_step = DAT_febec434;
    local_10.up_step = DAT_febec436;
    local_10.down_target = DAT_febec432;
  }
  f33_step_retained_unsigned_gain(&local_10);
  (*((ushort *)camry_host_ptr((uint32_t)(puVar2 + 0xc34)))) = local_10.down_step;
  (*((ushort *)camry_host_ptr((uint32_t)(puVar2 + 0xc36)))) = local_10.up_step;
  (*((ushort *)camry_host_ptr((uint32_t)(puVar2 + 0xc32)))) = local_10.down_target;
  (*((ushort *)camry_host_ptr((uint32_t)(puVar2 + 0xc30)))) = local_10.up_target;
  (*((ushort *)camry_host_ptr((uint32_t)(puVar2 + 0xc38)))) = local_10.current;
  return;
}



/* WARNING: Removing unreachable block (ram,0x000c7e2a) */

void FUN_000c7e1c(short param_1)

{
  DAT_febec43a = (short)((int)((uint)DAT_febec438 * (int)param_1) / 0x400);
  return;
}



/* Sum fresh nonlinear torqueC44C with separately published C45A/C472; retain raw signed32 C420,
   bound by unsigned AC6C and publish signed16 C43C. Native compositions join fresh nonlinear torque
   with older foreground rate, clamp5260 to2048, and retain negative430 before ordinary command
   aggregation. Cross-task atomicity and physical reachability are not asserted. */

void f33_bound_three_term_compensation(void)

{
  uint uVar1;
  uint uVar2;
  
  uVar2 = (uint)DAT_febeac6c;
  DAT_febec420 = (int)DAT_febec472 + (int)DAT_febec45a + (int)DAT_febec44c;
  DAT_febec43c = DAT_febeac6c;
  if ((int)(DAT_febec420 - uVar2) < 0 != ((int)DAT_febec420 < 0 && -1 < (int)(DAT_febec420 - uVar2))
      || DAT_febec420 == uVar2) {
    uVar1 = -uVar2;
    if ((int)(DAT_febec420 + uVar2) < 0 ==
        ((int)DAT_febec420 < 0 != (int)uVar1 < 0 &&
        (int)uVar1 < 0 == (int)(DAT_febec420 + uVar2) < 0) && DAT_febec420 != uVar1) {
      DAT_febec43c = (ushort)DAT_febec420;
    }
    else {
      DAT_febec43c = (ushort)uVar1;
    }
  }
  return;
}



/* Clear speed gain, curve products, bounded term and separate slope contribution. */

void f33_initialize_nonlinear_torque_compensation(void)

{
  DAT_febec43e = 0;
  DAT_febec440 = 0;
  DAT_febec442 = 0;
  DAT_febec444 = 0;
  DAT_febec446 = 0;
  DAT_febec44c = 0;
  DAT_febec448 = 0;
  DAT_febec44a = 0;
  DAT_febec44e = 0;
  return;
}



/* Unsigned ADF6 through AFB8E: gain1024 through7680, interpolate to614 at12800, then retain614. */

void f33_update_nonlinear_torque_speed_gain(void)

{
  uint32_t puVar1;
  int iVar2;
  
  puVar1 = 0xfebeb800u;
  iVar2 = f33_interpolate_unsigned_axis_sentinel_curve((ushort *)((undefined *)camry_host_ptr(0xafb8eu)),DAT_febeadf6);
  (*((short *)camry_host_ptr((uint32_t)(puVar1 + 0xc3e)))) = (short)iVar2;
  return;
}



/* WARNING: Removing unreachable block (ram,0x000c7f1c) */
/* WARNING: Removing unreachable block (ram,0x000c7f14) */
/* WARNING: Removing unreachable block (ram,0x000c7ef2) */
/* Unsigned wrapping magnitude of C128 selects32-wide interpolation below index127; otherwise4876.
   Restore sign, narrow after C43E/1024 and AC6E/1024 products, bound10240 into C44C. Native
   scheduler compositions verify high-magnitude4876 publication and negative112 interpolation
   through retained speed gain614 to-46. Other inputs remain statically reconstructed. */

void f33_update_nonlinear_torque_compensation(void)

{
  int iVar1;
  short sVar2;
  short sVar3;
  uint32_t puVar4;
  ushort uVar5;
  short sVar6;
  short sVar7;
  short sVar9;
  int iVar10;
  uint uVar11;
  int iVar8;
  
  sVar2 = DAT_febec43e;
  sVar6 = DAT_febec128;
  sVar7 = DAT_febeac6e;
  sVar9 = DAT_000afb8c;
  puVar4 = 0xfebeb800u;
  iVar10 = (int)DAT_000afb8c;
  uVar5 = f33_abs_s16_wrapping(DAT_febec128);
  uVar11 = (uint)(uVar5 >> 5);
  if (uVar11 < 0x7f) {
    sVar3 = *(short *)(((undefined *)camry_host_ptr(0xafba4u)) + uVar11 * 4) +
            (short)((int)(((int)(short)uVar5 & 0x1fU) *
                         ((int)*(short *)(((undefined *)camry_host_ptr(0xafba4u)) + (uVar11 + 1) * 4) -
                         (int)*(short *)(((undefined *)camry_host_ptr(0xafba4u)) + uVar11 * 4))) / 0x20);
  }
  else {
    sVar3 = 0x130c;
  }
  (*((short *)camry_host_ptr((uint32_t)(puVar4 + 0xc40)))) = sVar3;
  if (sVar6 < 0) {
    sVar3 = -sVar3;
  }
  sVar6 = (short)(((int)sVar2 * (int)sVar3) / 0x400);
  sVar7 = (short)(((int)sVar7 * (int)sVar6) / 0x400);
  iVar8 = (int)sVar7;
  if ((iVar8 - iVar10 < 0 != (iVar8 < 0 != iVar10 < 0 && iVar10 < 0 == iVar8 - iVar10 < 0) ||
       iVar8 == iVar10) &&
     (iVar1 = -iVar10, sVar9 = sVar7,
     iVar8 + iVar10 < 0 != (iVar8 < 0 != iVar1 < 0 && iVar1 < 0 == iVar8 + iVar10 < 0) ||
     iVar8 == iVar1)) {
    sVar9 = (short)iVar1;
  }
  (*((short *)camry_host_ptr((uint32_t)(puVar4 + 0xc42)))) = sVar3;
  (*((short *)camry_host_ptr((uint32_t)(puVar4 + 0xc44)))) = sVar6;
  (*((short *)camry_host_ptr((uint32_t)(puVar4 + 0xc46)))) = sVar7;
  (*((short *)camry_host_ptr((uint32_t)(puVar4 + 0xc4c)))) = sVar9;
  return;
}



/* WARNING: Removing unreachable block (ram,0x000c7f8c) */
/* WARNING: Removing unreachable block (ram,0x000c7f82) */
/* Use AFDA8 indexed by abs(C128)>>5, else2713. Narrow speed-scaled slope; AC2B5A publishes C44E
   zero, otherwise scale by AC6E/1024. */

void f33_update_nonlinear_torque_slope(void)

{
  char cVar1;
  short sVar2;
  short sVar3;
  short sVar4;
  undefined2 uVar5;
  uint32_t puVar6;
  ushort uVar7;
  
  sVar3 = DAT_febec43e;
  sVar2 = DAT_febeac6e;
  cVar1 = DAT_febeac2b;
  puVar6 = 0xfebeb800u;
  uVar7 = f33_abs_s16_wrapping(DAT_febec128);
  sVar4 = 0xa99;
  if (uVar7 >> 5 < 0x7f) {
    sVar4 = *(short *)(((undefined *)camry_host_ptr(0xafda8u)) + (uint)(uVar7 >> 5) * 4);
  }
  (*((short *)camry_host_ptr((uint32_t)(puVar6 + 0xc48)))) = sVar4;
  sVar4 = (short)(((int)sVar3 * (int)sVar4) / 0x400);
  (*((short *)camry_host_ptr((uint32_t)(puVar6 + 0xc4a)))) = sVar4;
  if (cVar1 == 'Z') {
    uVar5 = 0;
  }
  else {
    uVar5 = (undefined2)(((int)sVar2 * (int)sVar4) / 0x400);
  }
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar6 + 0xc4e)))) = uVar5;
  return;
}



/* Clear C450..C45A angle-rate compensation publications. */

void f33_initialize_angle_rate_compensation(void)

{
  DAT_febec450 = 0;
  DAT_febec452 = 0;
  DAT_febec454 = 0;
  DAT_febec456 = 0;
  DAT_febec458 = 0;
  DAT_febec45a = 0;
  return;
}



/* Unsigned ADF6 through AFFC4: gain1024 through7680, interpolate tozero at12800, then zero. */

void f33_update_angle_rate_compensation_speed_gain(void)

{
  uint32_t puVar1;
  int iVar2;
  
  puVar1 = 0xfebeb800u;
  iVar2 = f33_interpolate_unsigned_axis_sentinel_curve((ushort *)((undefined *)camry_host_ptr(0xaffc4u)),DAT_febeadf6);
  (*((short *)camry_host_ptr((uint32_t)(puVar1 + 0xc50)))) = (short)iVar2;
  return;
}



/* WARNING: Removing unreachable block (ram,0x000c801a) */
/* WARNING: Removing unreachable block (ram,0x000c8012) */
/* Signed sentinel lookup of wrapping abs(C172): zero through480, rise to384 at1280. Restore sign;
   narrow C450/1024 and AE4A/1024 products; bound768 into C45A. */

void f33_update_angle_rate_compensation(void)

{
  int iVar1;
  short sVar2;
  short sVar3;
  short sVar4;
  uint32_t puVar5;
  short sVar6;
  int iVar7;
  short sVar8;
  int iVar9;
  
  sVar2 = DAT_febec450;
  sVar3 = DAT_febec172;
  sVar4 = DAT_febeae4a;
  sVar8 = DAT_000affaa;
  puVar5 = 0xfebeb800u;
  iVar9 = (int)DAT_000affaa;
  sVar6 = f33_abs_s16_wrapping(DAT_febec172);
  iVar7 = f33_interpolate_signed_sentinel_curve((short *)((undefined *)camry_host_ptr(0xaffacu)),sVar6);
  sVar6 = (short)iVar7;
  (*((short *)camry_host_ptr((uint32_t)(puVar5 + 0xc52)))) = sVar6;
  if (sVar3 < 0) {
    sVar6 = -sVar6;
  }
  sVar3 = (short)(((int)sVar2 * (int)sVar6) / 0x400);
  sVar4 = (short)(((int)sVar4 * (int)sVar3) / 0x400);
  iVar7 = (int)sVar4;
  if ((iVar7 - iVar9 < 0 != (iVar7 < 0 != iVar9 < 0 && iVar9 < 0 == iVar7 - iVar9 < 0) ||
       iVar7 == iVar9) &&
     (iVar1 = -iVar9, sVar8 = sVar4,
     iVar7 + iVar9 < 0 != (iVar7 < 0 != iVar1 < 0 && iVar1 < 0 == iVar7 + iVar9 < 0) ||
     iVar7 == iVar1)) {
    sVar8 = (short)iVar1;
  }
  (*((short *)camry_host_ptr((uint32_t)(puVar5 + 0xc54)))) = sVar6;
  (*((short *)camry_host_ptr((uint32_t)(puVar5 + 0xc56)))) = sVar3;
  (*((short *)camry_host_ptr((uint32_t)(puVar5 + 0xc58)))) = sVar4;
  (*((short *)camry_host_ptr((uint32_t)(puVar5 + 0xc5a)))) = sVar8;
  return;
}


