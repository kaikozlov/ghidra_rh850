#include "common.h"


/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_34406(void)

{
  return;
}



/* Under existing FFC0 priority mask, default retained first centers/gains and second gains8000,
   second centers0 and angles2000; does not imply accepted physical calibration. */

void f33_reset_retained_fit_coefficients(void)

{
  uint32_t puVar1;
  uint saved_mask;
  
  puVar1 = 0xfebeb800u;
  saved_mask = f33_priority_mask_enter(0xffc0);
  (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffb284u + (uint32_t)((int)puVar1)))))) = 0x8000;
  (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffb286u + (uint32_t)((int)puVar1)))))) = 0x8000;
  (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffb290u + (uint32_t)((int)puVar1)))))) = 0x8000;
  (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffb292u + (uint32_t)((int)puVar1)))))) = 0x8000;
  (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffb288u + (uint32_t)((int)puVar1)))))) = 0x8000;
  (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffb28au + (uint32_t)((int)puVar1)))))) = 0x8000;
  (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffb294u + (uint32_t)((int)puVar1)))))) = 0x8000;
  (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffb296u + (uint32_t)((int)puVar1)))))) = 0x8000;
  (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffb28cu + (uint32_t)((int)puVar1)))))) = 0x8000;
  (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffb28eu + (uint32_t)((int)puVar1)))))) = 0x8000;
  (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffb298u + (uint32_t)((int)puVar1)))))) = 0x8000;
  (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffb29au + (uint32_t)((int)puVar1)))))) = 0x8000;
  (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffb29cu + (uint32_t)((int)puVar1)))))) = 0;
  (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffb29eu + (uint32_t)((int)puVar1)))))) = 0;
  (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffb2a8u + (uint32_t)((int)puVar1)))))) = 0x8000;
  (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffb2aau + (uint32_t)((int)puVar1)))))) = 0x8000;
  (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffb2b4u + (uint32_t)((int)puVar1)))))) = 0x2000;
  (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffb2a0u + (uint32_t)((int)puVar1)))))) = 0;
  (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffb2a2u + (uint32_t)((int)puVar1)))))) = 0;
  (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffb2acu + (uint32_t)((int)puVar1)))))) = 0x8000;
  (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffb2aeu + (uint32_t)((int)puVar1)))))) = 0x8000;
  (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffb2b6u + (uint32_t)((int)puVar1)))))) = 0x2000;
  (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffb2a4u + (uint32_t)((int)puVar1)))))) = 0;
  (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffb2a6u + (uint32_t)((int)puVar1)))))) = 0;
  (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffb2b0u + (uint32_t)((int)puVar1)))))) = 0x8000;
  (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffb2b2u + (uint32_t)((int)puVar1)))))) = 0x8000;
  (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffb2b8u + (uint32_t)((int)puVar1)))))) = 0x2000;
  f33_priority_mask_restore(saved_mask);
  return;
}



/* Return344F4 status;5A first defaults retained values via3465A. Existing346F0 marker/diagnostic
   owner remains separate from candidate publication. */

uint f33_validate_or_default_retained_fit(void)

{
  uint uVar1;
  
  uVar1 = f33_check_retained_fit_bounds();
  if (uVar1 == 0x5a) {
    f33_reset_retained_fit_coefficients();
  }
  return uVar1;
}



void FUN_000346cc(void)

{
  DAT_febe6a7f = 0x44;
  DAT_febe6ac4 = 0xa55a5aa5;
  DAT_febe6a7e = 0;
  f33_report_diagnostic_healthy_observed(0x127);
  return;
}



void FUN_000346f0(void)

{
  undefined2 uVar1;
  uint32_t puVar2;
  uint uVar3;
  int iVar4;
  undefined4 uVar5;
  undefined1 uVar6;
  undefined4 uVar7;
  undefined1 uVar8;
  uint local_54 [16];
  
  puVar2 = 0xfebeb800u;
  uVar3 = f33_nvm_get_record(0x202, camry_host_addr(local_54));
  uVar5 = 0xa55a5aa5;
  if ((uVar3 == 0x10) && (local_54[0] == 0xa55a5aa5)) {
    f33_restore_fit_coefficients();
    uVar3 = f33_validate_or_default_retained_fit();
    if (uVar3 == 0) {
      uVar7 = 0xa55a5aa5;
      uVar8 = 0x44;
      f33_report_diagnostic_healthy_observed(0x125);
      goto LAB_00034744;
    }
  }
  uVar7 = 0x5aa5a55a;
  uVar8 = 0x22;
  f33_report_diagnostic_event_failure(0x125,0x32);
LAB_00034744:
  uVar3 = f33_nvm_get_record_status(0x205);
  iVar4 = camry_host_addr(FUN_000567be());
  if ((uVar3 == 0x10) && ((*((int *)camry_host_ptr((uint32_t)(iVar4 + 0xb8)))) == -0x5aa5a55b)) {
    uVar6 = 0x44;
    f33_report_diagnostic_healthy_observed(0x126);
  }
  else {
    uVar5 = 0x5aa5a55a;
    uVar6 = 0x22;
    f33_report_diagnostic_event_failure(0x126,0x32);
  }
  FUN_000346cc();
  uVar1 = DAT_00030ef2;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffb279u + (uint32_t)((int)puVar2) * 1u)))) = uVar8;
  (*((undefined4 *)camry_host_ptr((uint32_t)((0xffffb2bcu + (uint32_t)((int)puVar2)))))) = uVar7;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffb27cu + (uint32_t)((int)puVar2) * 1u)))) = uVar6;
  (*((undefined4 *)camry_host_ptr((uint32_t)((0xffffb2c0u + (uint32_t)((int)puVar2)))))) = uVar5;
  (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffb282u + (uint32_t)((int)puVar2)))))) = uVar1;
  return;
}



undefined4 FUN_000347a2(void)

{
  uint uVar1;
  uint local_44 [16];
  
  uVar1 = f33_nvm_get_record(0x202, camry_host_addr(local_44));
  if ((uVar1 == 0x10) && (local_44[0] == 0xa55a5aa5)) {
    f33_restore_fit_coefficients();
    uVar1 = f33_validate_or_default_retained_fit();
    if (uVar1 == 0) {
      return 0xa55a5aa5;
    }
  }
  return 0x5aa5a55a;
}



void FUN_000347e2(void)

{
  char cVar1;
  undefined4 uVar2;
  undefined *puVar3;
  int iVar4;
  undefined1 uVar5;
  short sVar6;
  
  uVar2 = DAT_febe6ac0;
  cVar1 = DAT_febe6a7c;
  puVar3 = ((undefined *)camry_host_ptr(0xfebeb800u));
  sVar6 = DAT_febe6a82;
  if (DAT_febe6a82 != 0) {
    sVar6 = DAT_febe6a82 + -1;
  }
  iVar4 = DAT_febe6abc;
  if (((DAT_febe6579 == 'Z') && (DAT_febe6abc == -0x5aa5a55b)) &&
     (puVar3 = ((undefined *)camry_host_ptr(0xfebeb800u)), iVar4 = FUN_000347a2(), iVar4 != -0x5aa5a55b)) {
    f33_report_diagnostic_event_failure(0x125,0x32);
  }
  uVar5 = 0;
  if (cVar1 == 'D') {
    uVar5 = 0x5a;
  }
  if (DAT_00030ef0 == 'Z') {
    uVar5 = 0;
  }
  FUN_000346cc();
  *(int *)(((undefined *)camry_host_ptr(0xffffb2bcu)) + (int)camry_host_addr(puVar3)) = iVar4;
  *(undefined4 *)(((undefined *)camry_host_ptr(0xffffb2c0u)) + (int)camry_host_addr(puVar3)) = uVar2;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffb27bu + (uint32_t)((int)camry_host_addr(puVar3)) * 1u)))) = uVar5;
  *(short *)(((undefined *)camry_host_ptr(0xffffb282u)) + (int)camry_host_addr(puVar3)) = sVar6;
  return;
}



void FUN_00034858(void)

{
  uint32_t puVar1;
  uint uVar2;
  int iVar3;
  undefined4 uVar4;
  undefined1 uVar5;
  
  puVar1 = 0xfebeb800u;
  uVar2 = f33_nvm_get_record_status(0x206);
  iVar3 = camry_host_addr(FUN_000567be());
  if ((uVar2 == 0x10) && ((*((int *)camry_host_ptr((uint32_t)(iVar3 + 0x4c8)))) == -0x5aa5a55b)) {
    uVar5 = 0x44;
    f33_report_diagnostic_healthy_observed(0x127);
    uVar4 = 0xa55a5aa5;
  }
  else {
    uVar4 = 0x5aa5a55a;
    uVar5 = 0x22;
    f33_report_diagnostic_event_failure(0x127,0x32);
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffb27fu + (uint32_t)((int)puVar1) * 1u)))) = uVar5;
  (*((undefined4 *)camry_host_ptr((uint32_t)((0xffffb2c4u + (uint32_t)((int)puVar1)))))) = uVar4;
  return;
}



void FUN_00034bce(void)

{
  uint32_t puVar1;
  uint local_44 [16];
  
  puVar1 = 0xfebeb800u;
  f33_nvm_get_record(0x202, camry_host_addr(local_44));
  local_44[0] = 0;
  f33_nvm_set_record(0x202,local_44);
  (*((undefined4 *)camry_host_ptr((uint32_t)((0xffffb2bcu + (uint32_t)((int)puVar1)))))) = 0x5aa5a55a;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffb278u + (uint32_t)((int)puVar1) * 1u)))) = 0x44;
  return;
}



bool FUN_00034c00(void)

{
  ushort uVar1;
  int iVar2;
  char cVar3;
  bool bVar4;
  uint uVar5;
  
  cVar3 = DAT_febee81a;
  iVar2 = DAT_febe6abc;
  uVar1 = DAT_febe66b8;
  uVar5 = f33_get_diagnostic_event_state(0x52);
  if (((cVar3 == '\x01') && (DAT_00030ef4 <= uVar1)) && (iVar2 == 0)) {
    bVar4 = (uVar5 >> 1 & 1) == 0;
  }
  else {
    bVar4 = false;
  }
  return bVar4;
}



/* Preserve344F4 full R10 result across PREPARE/DISPOSE.33CDC consumes0 for admissible changed
   record and5A for invalid. Replace existing void prototype; no unrelated register clobber/inline
   fiction. */

uint f33_check_fit_record_admission(void)

{
  uint uVar1;
  
  uVar1 = f33_check_retained_fit_bounds();
  return uVar1;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_34c46(void)

{
  return;
}



void FUN_00034c48(void)

{
  DAT_febe6acc = 0;
  DAT_febe6ac8 = 0;
  DAT_febe6ac9 = 0;
  DAT_febe6aca = 0;
  return;
}



/* Prioritize cached6210/6212 from34028 over6959/695C request, else signed torque map. Publish
   source ID and negated selected request. No inferred physical current actuation, freshness or
   actual output consumer. */

void f33_select_mode600_stimulus_request(void)

{
  uint32_t puVar1;
  undefined1 uVar2;
  undefined1 uVar3;
  short sStack_e;
  
  puVar1 = 0xfebeb800u;
  if (DAT_febe6210 == 'Z') {
    uVar3 = 1;
    sStack_e = DAT_febe6212;
    uVar2 = 0x5a;
  }
  else if (DAT_febe6959 == 'Z') {
    uVar3 = 2;
    sStack_e = DAT_febe695c;
    uVar2 = 0x5a;
  }
  else {
    uVar3 = 0;
    uVar2 = 0;
    puVar1 = 0xfebeb800u;
    if (DAT_febe7e0c < 0) {
      FUN_00070208(((undefined *)camry_host_ptr(0x30f0cu)),(int)-DAT_febe7e0c,&sStack_e);
      sStack_e = -sStack_e;
    }
    else {
      FUN_00070208(((undefined *)camry_host_ptr(0x30f0cu)),(int)DAT_febe7e0c,&sStack_e);
    }
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffb2c9u + (uint32_t)((int)puVar1) * 1u)))) = uVar3;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffb2c8u + (uint32_t)((int)puVar1) * 1u)))) = uVar2;
  (*((short *)camry_host_ptr((uint32_t)((0xffffb2ccu + (uint32_t)((int)puVar1)))))) = -sStack_e;
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_34cce(void)

{
  return;
}



/* Get record105 marker and record18 count. Exact10/A55A5AA5 establishes5A; invalid status or
   count>30 clears gate and count. Valid count0 preserves marker-derived gate. RAM publication, not
   a physical flash read. */

void f33_reload_ba_admission_records(void)

{
  uint32_t puVar1;
  uint uVar2;
  undefined1 uVar3;
  byte local_18 [8];
  uint auStack_10 [2];
  
  puVar1 = 0xfebeb800u;
  uVar2 = f33_nvm_get_record(0x105, camry_host_addr(auStack_10));
  if ((uVar2 == 0x10) && (auStack_10[0] == 0xa55a5aa5)) {
    uVar3 = 0x5a;
  }
  else {
    uVar3 = 0;
  }
  uVar2 = f33_nvm_get_record(0x18, camry_host_addr(((uint *)camry_host_ptr((uint32_t)(local_18)))));
  if ((uVar2 != 0x10) || (f33_ba_retained_admission_count_limit < local_18[0])) {
    local_18[0] = 0;
    uVar3 = 0;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x58b0))))) = local_18[0];
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x58b1))))) = uVar3;
  return;
}



/* Compare zero-extended low8 length bytes exactly; return1 on equality,0 on first mismatch. No
   independent source-size validation. */

uint f33_compare_ba_token_bytes(uchar *left,uchar *right,uchar length)

{
  uint uVar1;
  
  uVar1 = 0;
  while( true ) {
    if (length <= uVar1) {
      return 1;
    }
    if (left[uVar1] != right[uVar1]) break;
    uVar1 = uVar1 + 1 & 0xff;
  }
  return 0;
}



/* Return5A only for F7,length6 and five exact BAENA bytes. Token comparison runs before
   selector/length conjunction; this is not a general input-bounds guard. */

uint f33_ba_enable_closed_gate_exception(uchar operation,uchar request_length,uchar *payload)

{
  uint uVar1;
  uint uVar2;
  
  uVar2 = 0;
  uVar1 = f33_compare_ba_token_bytes
                    (payload,(uchar *)"BAENAJTEKMTMPCLJTRM1JTRM2BADISBAENATZCLRJTRM3VSPDASINC",
                     '\x05');
  if (((operation == 0xf7) && (request_length == '\x06')) && (uVar1 == 1)) {
    uVar2 = 0x5a;
  }
  return uVar2;
}



void FUN_00034ea4(int param_1,int param_2)

{
  uint uVar1;
  undefined4 uVar2;
  byte bStack_15;
  undefined1 auStack_14 [8];
  
  uVar1 = 0;
  do {
    auStack_14[uVar1] = 0;
    uVar1 = uVar1 + 1;
  } while (uVar1 < 8);
  FUN_0006a624(param_2,&bStack_15);
  if ((param_2 < 0) || (8 < bStack_15)) {
    uVar2 = 0xfffffffa;
  }
  else {
    uVar2 = 0;
    for (uVar1 = 0; uVar1 < bStack_15; uVar1 = uVar1 + 1 & 0xff) {
      auStack_14[uVar1] = (*((undefined1 *)camry_host_ptr((uint32_t)(uVar1 + param_1))));
    }
  }
  ((void)(auStack_14), FUN_0004d4ca(uVar2, bStack_15));
  return;
}



int FUN_00035004(byte *param_1)

{
  return (uint)param_1[1] + (uint)*param_1 * 0x100;
}



int FUN_00035010(byte *param_1)

{
  return (uint)param_1[3] +
         (uint)param_1[2] * 0x100 + (uint)param_1[1] * 0x10000 + (uint)*param_1 * 0x1000000;
}



/* Exact JTEKM requests internal selector3 admission in modes0400/0500/0700..0702/0800; no latch
   mutation at start. */

int f33_ba_f1_validate_jtekm(uchar configured_index,uchar *payload,uchar *response)

{
  int iVar1;
  uint uVar2;
  
  uVar2 = f33_compare_ba_token_bytes
                    (payload,"JTEKMTMPCLJTRM1JTRM2BADISBAENATZCLRJTRM3VSPDASINC",'\x05');
  iVar1 = -6;
  if (uVar2 == 1) {
    iVar1 = f33_admit_internal_ba_selector(3,0);
  }
  return iVar1;
}



/* Return real B338C(3) R10=0; setB112=5A,B113=11. Persistent software selector, not a physical
   completion. */

int f33_ba_f1_latch_selector3(void)

{
  int iVar1;
  
  iVar1 = f33_latch_internal_ba_selector(3);
  return iVar1;
}



/* Exact JTRM1 requests internal selector5 admission in allowed modes; start does not setB112. */

int f33_ba_f4_validate_jtrm1(uchar configured_index,uchar *payload,uchar *response)

{
  int iVar1;
  uint uVar2;
  
  uVar2 = f33_compare_ba_token_bytes(payload,"JTRM1JTRM2BADISBAENATZCLRJTRM3VSPDASINC",'\x05');
  iVar1 = -6;
  if (uVar2 == 1) {
    iVar1 = f33_admit_internal_ba_selector(5,0);
  }
  return iVar1;
}



/* Return real B338C(5) R10=0; setB112=5A,B113=22. */

int f33_ba_f4_latch_selector5(void)

{
  int iVar1;
  
  iVar1 = f33_latch_internal_ba_selector(5);
  return iVar1;
}



/* Exact JTRM2 requests internal selector6 admission in allowed modes; start does not setB112. */

int f33_ba_f5_validate_jtrm2(uchar configured_index,uchar *payload,uchar *response)

{
  int iVar1;
  uint uVar2;
  
  uVar2 = f33_compare_ba_token_bytes(payload,"JTRM2BADISBAENATZCLRJTRM3VSPDASINC",'\x05');
  iVar1 = -6;
  if (uVar2 == 1) {
    iVar1 = f33_admit_internal_ba_selector(6,0);
  }
  return iVar1;
}



/* Return real B338C(6) R10=0; setB112=5A,B113=44. */

int f33_ba_f5_latch_selector6(void)

{
  int iVar1;
  
  iVar1 = f33_latch_internal_ba_selector(6);
  return iVar1;
}



/* Both cached statuses10 clear5F4F/50 and return0; either20/21 waits-1;otherwise-9. Does not prove
   either setter was admitted. */

int f33_ba_f6_finish_disable(void)

{
  uint32_t puVar1;
  uint uVar2;
  uint uVar3;
  int iVar4;
  
  puVar1 = 0xfebeb800u;
  uVar2 = f33_nvm_get_record_status(0x105);
  uVar3 = f33_nvm_get_record_status(0x18);
  if ((uVar2 == 0x10) && (uVar3 == 0x10)) {
    iVar4 = 0;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x58b0))))) = 0;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x58b1))))) = 0;
  }
  else if ((uVar2 == 0x20 || uVar2 == 0x21) || (uVar3 == 0x20 || uVar3 == 0x21)) {
    iVar4 = -1;
  }
  else {
    iVar4 = -9;
  }
  return iVar4;
}



/* Read numerical published DCM security level and return5A if its bit1 is set, else0. This is not a
   greater-than-or-equal security-level comparison. */

uint f33_ba_security_level_bit1_enabled(void)

{
  uint uVar1;
  uint uVar2;
  
  uVar2 = FUN_0008d9b6();
  uVar1 = 0x5a;
  if ((uVar2 & 2) == 0) {
    uVar1 = 0;
  }
  return uVar1;
}



/* Require numerical security-level bit1 at every invocation. Phase0 exact BAENA requests
   record18=count30 and105=markerA55A5AA5, ignoring admission returns. Phase5A joins cached statuses
   and publishes gate/count on exact10. */

int f33_ba_f7_request_enable(uchar configured_index,uchar *payload,uchar *response)

{
  uint32_t puVar1;
  uint32_t puVar2;
  uint uVar3;
  uint uVar4;
  int iVar5;
  uchar local_1c [8];
  uint auStack_14 [2];
  
  puVar1 = 0xfebeb800u;
  puVar2 = 0x23dfcu;
  uVar3 = f33_ba_security_level_bit1_enabled();
  if (uVar3 == 0x5a) {
    if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x58b4))))) == '\0') {
      uVar3 = f33_compare_ba_token_bytes(payload, ((undefined *)camry_host_ptr((uint32_t)(puVar2 + -0x2d46))), '\x05');
      if (uVar3 == 1) {
        iVar5 = 0;
        local_1c[1] = 0;
        local_1c[2] = '\0';
        local_1c[3] = '\0';
        local_1c[4] = '\0';
        local_1c[5] = '\0';
        local_1c[6] = '\0';
        local_1c[7] = '\0';
        local_1c[0] = f33_ba_retained_admission_count_limit;
        f33_nvm_set_record(0x18,((uint *)camry_host_ptr((uint32_t)(local_1c))));
        auStack_14[0] = 0xa55a5aa5;
        auStack_14[1] = 0;
        f33_nvm_set_record(0x105,auStack_14);
      }
      else {
        iVar5 = -6;
      }
    }
    else {
      if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x58b4))))) == 'Z') {
        uVar3 = f33_nvm_get_record_status(0x105);
        uVar4 = f33_nvm_get_record_status(0x18);
        if ((uVar3 == 0x10) && (uVar4 == 0x10)) {
          (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x58b0))))) = f33_ba_retained_admission_count_limit;
          (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x58b1))))) = 0x5a;
          return 0;
        }
        if ((uVar3 == 0x20 || uVar3 == 0x21) || (uVar4 == 0x20 || uVar4 == 0x21)) {
          return -1;
        }
      }
      iVar5 = -9;
    }
  }
  else {
    iVar5 = -0xe;
  }
  return iVar5;
}



/* Both cached statuses10 publish count30/gate5A and return0; either20/21 waits-1,otherwise-9. No
   token/security recheck or marker re-read; old success can satisfy rejected requests. */

int f33_ba_f7_finish_enable(void)

{
  uint32_t puVar1;
  uint uVar2;
  uint uVar3;
  int iVar4;
  
  puVar1 = 0xfebeb800u;
  uVar2 = f33_nvm_get_record_status(0x105);
  uVar3 = f33_nvm_get_record_status(0x18);
  if ((uVar2 == 0x10) && (uVar3 == 0x10)) {
    iVar4 = 0;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x58b0))))) = f33_ba_retained_admission_count_limit;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x58b1))))) = 0x5a;
  }
  else if ((uVar2 == 0x20 || uVar2 == 0x21) || (uVar3 == 0x20 || uVar3 == 0x21)) {
    iVar4 = -1;
  }
  else {
    iVar4 = -9;
  }
  return iVar4;
}



/* Require TZCLR,byteE81F==0,unsigned halfwordE892<=384,bytesE884/E88A!=5A. Return0 or-6; no reset
   mutation at start. */

int f33_ba_f8_validate_tzclr(uchar configured_index,uchar *payload,uchar *response)

{
  char cVar1;
  char cVar2;
  char cVar3;
  ushort uVar4;
  uint uVar5;
  
  uVar4 = DAT_febee892;
  cVar3 = DAT_febee88a;
  cVar2 = DAT_febee884;
  cVar1 = DAT_febee81f;
  uVar5 = f33_compare_ba_token_bytes(payload,"TZCLRJTRM3VSPDASINC",'\x05');
  if ((((uVar5 != 1) || (cVar1 != '\0')) || (f33_ba_tzclr_raw_input_limit < uVar4)) ||
     ((cVar2 == 'Z' || (uVar5 = (uint)(cVar3 == 'Z'), cVar3 == 'Z')))) {
    uVar5 = 0xfffffffa;
  }
  return uVar5;
}



/* Exact JTRM3 requests internal selector7 admission in allowed modes; start does not setB112. */

int f33_ba_f9_validate_jtrm3(uchar configured_index,uchar *payload,uchar *response)

{
  int iVar1;
  uint uVar2;
  
  uVar2 = f33_compare_ba_token_bytes(payload,"JTRM3VSPDASINC",'\x05');
  iVar1 = -6;
  if (uVar2 == 1) {
    iVar1 = f33_admit_internal_ba_selector(7,0);
  }
  return iVar1;
}



/* Return real B338C(7) R10=0; setB112=5A,B113=88. */

int f33_ba_f9_latch_selector7(void)

{
  int iVar1;
  
  iVar1 = f33_latch_internal_ba_selector(7);
  return iVar1;
}



/* Compare payload[1..4] with VSPD; require receive-status80A5!=0, then copy payload[0] unchanged
   to5F52. No numeric clamp, physical speed or persistence assertion. */

int f33_ba_fa_stage_unsigned_override(uchar configured_index,uchar *payload,uchar *response)

{
  char cVar1;
  uint32_t puVar2;
  uint uVar3;
  int iVar4;
  
  cVar1 = DAT_febe80a5;
  puVar2 = 0xfebeb800u;
  uVar3 = f33_compare_ba_token_bytes(payload + 1,"VSPDASINC",'\x04');
  if ((uVar3 == 1) && (cVar1 != '\0')) {
    iVar4 = 0;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x58ae))))) = *payload;
  }
  else {
    iVar4 = -6;
  }
  return iVar4;
}



/* Exact ASINC returns0,otherwise-6. No mutation in start. */

int f33_ba_fb_validate_asinc(uchar configured_index,uchar *payload,uchar *response)

{
  uint uVar1;
  int iVar2;
  
  uVar1 = f33_compare_ba_token_bytes(payload,"ASINC",'\x05');
  if (uVar1 == 1) {
    iVar2 = 0;
  }
  else {
    iVar2 = -6;
  }
  return iVar2;
}



/* Return real B33CC R10=0; setB118=5A. Later owner5 rising-limit release selects fast coefficient;
   this does not directly set the limit or physical output. */

int f33_ba_fb_latch_owner5_fast_release(void)

{
  int iVar1;
  
  iVar1 = f33_latch_ba_owner5_fast_release();
  return iVar1;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_3552e(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_35530(void)

{
  return;
}



undefined4 FUN_00035532(void)

{
  if ((((DAT_febe6ad2 == f33_learned_quad[0]) && (DAT_febe6ad4 == f33_learned_quad[1])) &&
      (DAT_febe6ad6 == f33_learned_quad[2])) && (DAT_febe6ad8 == f33_learned_quad[3])) {
    return 0;
  }
  return 0x5a;
}



void FUN_00035568(void)

{
  DAT_febe6ad2 = f33_learned_quad[0];
  DAT_febe6ad4 = f33_learned_quad[1];
  DAT_febe6ad6 = f33_learned_quad[2];
  DAT_febe6ad8 = f33_learned_quad[3];
  return;
}



void FUN_00035586(void)

{
  DAT_febe6ad2 = 0x800;
  DAT_febe6ad4 = 0x800;
  DAT_febe6ad6 = 0x800;
  DAT_febe6ad8 = 0x800;
  return;
}



void FUN_00035598(void)

{
  uint32_t puVar1;
  uint uVar2;
  uint uVar3;
  
  puVar1 = 0xfebeb800u;
  if (DAT_febe8a18 != 'Z') {
    return;
  }
  uVar3 = (uint)DAT_febe6ad0;
  uVar2 = (uint)DAT_febe6ad1;
  if ((DAT_febe6af0 == -0x5aa5a55b) && (DAT_febe6ae1 == '\0')) {
    puVar1 = 0xfebeb800u;
    uVar3 = FUN_00035532();
    if (uVar3 != 0x5a) {
      uVar2 = 0;
      goto LAB_000355e8;
    }
    uVar2 = f33_check_learned_quad_bounds();
    if (uVar2 == 0) {
      FUN_00035568();
      goto LAB_000355e8;
    }
  }
  FUN_00035586();
LAB_000355e8:
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffb2d0u + (uint32_t)((int)puVar1) * 1u)))) = (char)uVar3;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffb2d1u + (uint32_t)((int)puVar1) * 1u)))) = (char)uVar2;
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_355f4(void)

{
  return;
}



void FUN_00035772(ushort param_1,ushort param_2,ushort param_3,ushort param_4)

{
  f33_learned_quad[0] = param_1;
  f33_learned_quad[1] = param_2;
  f33_learned_quad[2] = param_3;
  f33_learned_quad[3] = param_4;
  return;
}



void FUN_00035780(void)

{
  uint32_t puVar1;
  uint local_14;
  ushort uStack_10;
  ushort uStack_e;
  ushort uStack_c;
  ushort uStack_a;
  undefined4 uStack_8;
  
  puVar1 = 0xfebeb800u;
  uStack_10 = f33_learned_quad[0];
  uStack_e = f33_learned_quad[1];
  uStack_c = f33_learned_quad[2];
  uStack_8 = 0;
  uStack_a = f33_learned_quad[3];
  local_14 = 0xa55a5aa5;
  f33_nvm_set_record(0x100,&local_14);
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffb2ddu + (uint32_t)((int)puVar1) * 1u)))) = 0x11;
  return;
}



void FUN_000357c0(void)

{
  char cVar1;
  undefined *puVar2;
  int iVar3;
  
  puVar2 = ((undefined *)camry_host_ptr(0xfebeb800u));
  if ((((DAT_febe6ae2 == '\x11') && (((int8_t)DAT_febe6add) != -0x78)) && (DAT_febe6add != '\x11')) &&
     (((DAT_febee8cc & 0xff00) != 0x500 || (DAT_febe6af0 != -0x5aa5a55b)))) {
    puVar2 = ((undefined *)camry_host_ptr(0xfebeb800u));
    if ((DAT_febe6add == '\"') ||
       (puVar2 = ((undefined *)camry_host_ptr(0xfebeb800u)), iVar3 = f33_queue_application_service('\x01'), iVar3 != -1)) {
      FUN_0004d0a4(8,0x20);
    }
    else {
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffb2ddu + (uint32_t)((int)camry_host_addr(puVar2)) * 1u)))) = 0x88;
    }
  }
  else {
    cVar1 = DAT_febe6ae2;
    if ((DAT_febe6ae2 != '\"') || (0x3fe < (DAT_febee8cc & 0xff00) - 0x201)) goto LAB_00035842;
    puVar2 = ((undefined *)camry_host_ptr(0xfebeb800u));
    FUN_00035772(0x800,0x800,0x800,0x800);
    FUN_00035780();
  }
  cVar1 = '\0';
LAB_00035842:
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffb2e2u + (uint32_t)((int)camry_host_addr(puVar2)) * 1u)))) = cVar1;
  return;
}



/* After357C0, decrement nonzero6AE4. Valid source66D5=5A and marker6AF0=A55A5AA5 invoke
   learned-quad restoration; failed restoration reports128 and sets6AE1=5A. Pending
   write/reset6ADD/6ADC poll record100: exact10 succeeds,high-nibble20 waits,other status reports130
   and publishes slot17/kind1. Write success restores valid marker and passes0E; reset success
   clears marker and reports0E through51D38. Publication and physical persistence remain distinct.
    */

void f33_step_learned_quad_record_completion(void)

{
  uint32_t puVar1;
  uint uVar2;
  undefined1 uVar3;
  char cVar4;
  char cVar5;
  uint uVar6;
  short sVar7;
  
  puVar1 = 0xfebeb800u;
  FUN_000357c0();
  sVar7 = (*((short *)camry_host_ptr((uint32_t)((0xffffb2e4u + (uint32_t)((int)puVar1))))));
  uVar6 = (*((uint *)camry_host_ptr((uint32_t)((0xffffb2f0u + (uint32_t)((int)puVar1))))));
  cVar5 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffb2ddu + (uint32_t)((int)puVar1) * 1u))));
  cVar4 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffb2dcu + (uint32_t)((int)puVar1) * 1u))));
  if (sVar7 != 0) {
    sVar7 = sVar7 + -1;
  }
  uVar3 = 0;
  if (((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x512b))))) == 'Z') && (uVar6 == 0xa55a5aa5)) {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffb2e1u + (uint32_t)((int)puVar1) * 1u)))) = 0x5a;
    uVar6 = f33_restore_learned_quad();
    if (uVar6 == 0xa55a5aa5) {
      uVar3 = 0;
    }
    else {
      f33_report_diagnostic_event_failure(0x128,0x32);
      uVar3 = 0x5a;
    }
  }
  if (cVar5 == '\x11') {
    uVar2 = f33_nvm_get_record_status(0x100);
    if (uVar2 == 0x10) {
      uVar6 = 0xa55a5aa5;
      cVar5 = 'D';
      f33_report_diagnostic_event_pass(0xe);
    }
    else if ((uVar2 & 0xf0) != 0x20) {
      cVar5 = '\"';
      f33_report_diagnostic_event_failure(0x130,0x32);
      f33_retain_and_clear_fault_record(0x11);
      f33_encode_fault_action_kind('\x11','\x01');
      f33_select_current_fault_record(0x11);
    }
  }
  if (cVar4 == '\x11') {
    uVar2 = f33_nvm_get_record_status(0x100);
    if (uVar2 == 0x10) {
      uVar6 = 0;
      cVar4 = 'D';
      FUN_00051d38(0xe,10,0x32);
    }
    else if ((uVar2 & 0xf0) != 0x20) {
      cVar4 = '\"';
      f33_report_diagnostic_event_failure(0x130,0x32);
      f33_retain_and_clear_fault_record(0x11);
      f33_encode_fault_action_kind('\x11','\x01');
      f33_select_current_fault_record(0x11);
    }
  }
  (*((uint *)camry_host_ptr((uint32_t)((0xffffb2f0u + (uint32_t)((int)puVar1)))))) = uVar6;
  (*((short *)camry_host_ptr((uint32_t)((0xffffb2e4u + (uint32_t)((int)puVar1)))))) = sVar7;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffb2ddu + (uint32_t)((int)puVar1) * 1u)))) = cVar5;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffb2dcu + (uint32_t)((int)puVar1) * 1u)))) = cVar4;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffb2e1u + (uint32_t)((int)puVar1) * 1u)))) = uVar3;
  return;
}



void FUN_0003599e(void)

{
  uint32_t puVar1;
  undefined1 uVar2;
  uint local_18;
  undefined2 uStack_14;
  undefined2 uStack_12;
  undefined2 uStack_10;
  undefined2 uStack_e;
  undefined4 uStack_c;
  
  puVar1 = 0xfebeb800u;
  uVar2 = 0x44;
  if (DAT_febe6af0 != 0) {
    local_18 = 0;
    uStack_c = 0;
    uStack_e = 0x800;
    uStack_10 = 0x800;
    uStack_12 = 0x800;
    uStack_14 = 0x800;
    uVar2 = 0x11;
    puVar1 = 0xfebeb800u;
    f33_nvm_set_record(0x100,&local_18);
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffb2dcu + (uint32_t)((int)puVar1) * 1u)))) = uVar2;
  return;
}



bool FUN_00035a06(void)

{
  int iVar1;
  ushort uVar2;
  ushort uVar3;
  char cVar4;
  char cVar5;
  char cVar6;
  ushort uVar7;
  bool bVar8;
  short sStack_1e;
  
  uVar7 = DAT_febee892;
  cVar6 = DAT_febee81a;
  cVar5 = DAT_febe80a5;
  cVar4 = DAT_febe80a0;
  uVar3 = DAT_febe66b8;
  uVar2 = DAT_febe6764 & 0x81ff;
  FUN_0006a522((int)DAT_febe66a8,&sStack_1e);
  if ((((cVar6 == '\x01') && (DAT_00030e32 <= uVar3)) && (uVar7 <= DAT_00030e34)) &&
     (((cVar5 == '\0' && (cVar4 == '\0')) &&
      (iVar1 = sStack_1e + -0x200, ((iVar1 < 0) || (sStack_1e < 0)))))) {
    bVar8 = uVar2 == 0;
  }
  else {
    bVar8 = false;
  }
  return bVar8;
}



void FUN_00035a68(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  FUN_00035a06();
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffb2dfu + (uint32_t)((int)puVar1) * 1u)))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffb2deu + (uint32_t)((int)puVar1) * 1u)))) = 0;
  return;
}



void FUN_00035a7c(void)

{
  if (DAT_febe6af0 == 0) {
    f33_report_diagnostic_event_failure(0xe,0x32);
  }
  return;
}



undefined4 FUN_00035a96(void)

{
  DAT_febe6ae2 = 0x11;
  return 2;
}



void FUN_00035aa2(void)

{
  if ((((DAT_febe6af0 != -1) && (DAT_febe6af0 != -0x5aa5a55b)) && (((int8_t)DAT_febe6add) != -0x78)) &&
     ((DAT_febe6add != '\x11' && (DAT_febe6ae2 != '\x11')))) {
    DAT_febe6ae2 = '\"';
  }
  return;
}



void FUN_00035ad6(void)

{
  if (((int8_t)DAT_febe6add) == -0x78) {
    DAT_febe6add = '\0';
  }
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_35ae8(void)

{
  return;
}



/* Constant-block fill: 10 literal assignments into one contiguous cell block; shape-verified.
   Literals are default/reset values; cell meanings are not recovered. */

void f33_fill_constant_block_35aea(void)

{
  DAT_febe5f58 = 0;
  DAT_febe5f59 = 0;
  DAT_febe5f5a = 0;
  DAT_febe5f5e = DAT_0002bd02;
  DAT_febe5f60 = DAT_0002bd02;
  DAT_febe5f5b = 0;
  DAT_febe5f5c = 0;
  DAT_febe5f5d = 0;
  DAT_febe5f62 = DAT_0002bd06;
  DAT_febe5f64 = DAT_0002bd06;
  return;
}



undefined4 FUN_00035b12(undefined4 param_1,undefined4 param_2,uint param_3)

{
  undefined2 uVar1;
  byte bVar2;
  undefined4 uVar3;
  
  uVar1 = DAT_0002bd02;
  bVar2 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe5f58u + (uint32_t)(param_3 & 0xff) * 1u))));
  uVar3 = 0;
  if (DAT_0002bd00 <= bVar2) {
    uVar3 = 0x5a;
    bVar2 = 0;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe5f58u + (uint32_t)(param_3 & 0xff) * 1u)))) = bVar2;
  (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe5f5eu + (uint32_t)(param_3 & 0xff) * 2u)))) = uVar1;
  return uVar3;
}



undefined4 FUN_00035b44(undefined4 param_1,undefined4 param_2,uint param_3)

{
  undefined2 uVar1;
  byte bVar2;
  undefined4 uVar3;
  
  uVar1 = DAT_0002bd06;
  param_3 = param_3 & 0xff;
  bVar2 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe5f5au + (uint32_t)(param_3) * 1u))));
  uVar3 = 0;
  if (DAT_0002bd01 <= bVar2) {
    uVar3 = 0x5a;
    bVar2 = 0;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe5f5au + (uint32_t)(param_3) * 1u)))) = bVar2;
  (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe5f62u + (uint32_t)(param_3) * 2u)))) = uVar1;
  return uVar3;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_35c00(void)

{
  return;
}



void FUN_00035c02(void)

{
  DAT_febe5f6c = 0;
  DAT_febe5f68 = 0;
  DAT_febe5f6a = 0;
  DAT_febe5f69 = 0;
  return;
}



void FUN_00035c10(void)

{
  if ((DAT_0002bd08 <= DAT_febe5f6a) ||
     (DAT_febe5f6a = DAT_febe5f6a + 1, DAT_0002bd08 <= DAT_febe5f6a)) {
    DAT_febe5f69 = 0;
  }
  DAT_febe5f68 = 0;
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_35c36(void)

{
  return;
}



void FUN_00035c38(void)

{
  FUN_00035c10();
  f33_return_only_stub_35c36();
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_35c48(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_35c4a(void)

{
  return;
}



/* Normally publish diagnostic6AF6=EE40A, pre-override6AF8=EE410 and motor6AF4=-EE40C. In mode
   family0500, E780==5A selects clamped EB10 first; otherwise EE406==5A selects clamped EE416. Exact
   ROM30F1C/31914 are zero, so their forced branch is inactive. Command publication and current
   conversion use separate interrupt contexts. Motor sample normally negates EE40C; family0500
   permits two explicitly prioritized bounded service substitutions. Diagnostic mirror EE40A is a
   separate sample. Static instructions/dataflow; no new vehicle behavior. */

void f33_sample_motor_command(void)

{
  short sVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  
  iVar5 = (int)DAT_febee782;
  iVar4 = (int)DAT_febeeb10;
  iVar2 = (int)DAT_febee416;
  iVar3 = (int)DAT_febee418;
  if ((DAT_00030f1c == 'Z') && (DAT_00031914 == 'Z')) {
    DAT_febe6af4 = DAT_00031916;
    DAT_febe6af6 = DAT_00031916;
    DAT_febe6af8 = DAT_00031916;
    DAT_febe6afa = DAT_febee782;
    return;
  }
  DAT_febe6af6 = DAT_febee40a;
  DAT_febe6af8 = DAT_febee410;
  sVar1 = DAT_febee40c;
  if ((DAT_febeeb1e & 0xff00) == 0x500) {
    if (DAT_febee780 == 'Z') {
      if (iVar5 - iVar4 < 0 != (iVar5 < 0 != iVar4 < 0 && iVar4 < 0 == iVar5 - iVar4 < 0)) {
        iVar4 = iVar5;
      }
      iVar3 = -iVar5;
      if (iVar4 + iVar5 < 0 == (iVar4 < 0 != iVar3 < 0 && iVar3 < 0 == iVar4 + iVar5 < 0)) {
        iVar3 = iVar4;
      }
      DAT_febe6af8 = (short)iVar3;
      DAT_febe6af6 = DAT_febeeb10;
      sVar1 = DAT_febe6af8;
    }
    else if (DAT_febee406 == 'Z') {
      iVar4 = (int)-DAT_febee418;
      if (iVar2 - iVar3 < 0 != (iVar2 < 0 != iVar3 < 0 && iVar3 < 0 == iVar2 - iVar3 < 0)) {
        iVar3 = iVar2;
      }
      if (iVar3 - iVar4 < 0 == (iVar3 < 0 != iVar4 < 0 && iVar4 < 0 == iVar3 - iVar4 < 0)) {
        iVar4 = iVar3;
      }
      DAT_febe6af8 = (short)iVar4;
      DAT_febe6af6 = DAT_febee416;
      sVar1 = DAT_febe6af8;
    }
  }
  DAT_febe6af4 = -sVar1;
  DAT_febe6afa = DAT_febee782;
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_35ce8(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_35cea(void)

{
  return;
}



/* 71ECbit0 disables branch; otherwise selectedconstant minus62BC*62D4,dividebyabs62D6
   orboundonzero,clamp\u00b126604 into6AFC. No physicalunitsassigned. otherwise selectedconstant
   minus62BC*62D4,dividebyabs62D6 orboundonzero,clamp±26604 into6AFC. */

void f33_update_limit_budget_branch0(void)

{
  int iVar1;
  int iVar2;
  
  if ((DAT_febe71ec & 1) != 0) {
    DAT_febe6afc = 0;
    DAT_febe6b00 = 0;
    DAT_febe6b04 = 0;
    return;
  }
  iVar1 = DAT_00031938;
  if ((DAT_febe71ec >> 1 & 1) != 0) {
    iVar1 = DAT_0003193c;
  }
  iVar2 = (int)DAT_febe62d6;
  DAT_febe6b04 = iVar1 - (int)DAT_febe62bc * (int)DAT_febe62d4;
  if (iVar2 < 0) {
    iVar2 = -iVar2;
  }
  else {
    iVar1 = DAT_0003191c;
    if (iVar2 == 0) goto LAB_00035d38;
  }
  iVar1 = DAT_febe6b04;
  if (iVar2 != 0) {
    if (DAT_febe6b04 == -0x80000000 && iVar2 == -1) {
      iVar1 = -0x80000000;
    }
    else {
      iVar1 = DAT_febe6b04 / iVar2;
    }
  }
LAB_00035d38:
  iVar2 = DAT_0003191c;
  if (iVar1 - DAT_0003191c < 0 !=
      (iVar1 < 0 != DAT_0003191c < 0 && DAT_0003191c < 0 == iVar1 - DAT_0003191c < 0)) {
    iVar2 = iVar1;
  }
  DAT_febe6afc = -DAT_0003191c;
  if (iVar2 + DAT_0003191c < 0 ==
      (iVar2 < 0 != DAT_febe6afc < 0 && DAT_febe6afc < 0 == iVar2 + DAT_0003191c < 0)) {
    DAT_febe6afc = iVar2;
  }
  DAT_febe6b00 = (int)DAT_febe62bc * (int)DAT_febe62d4;
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_35d54(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_35d56(void)

{
  return;
}



/* Companionbranch using71ECbit1,62C0*62D8 andabs62DA,clamp\u00b126604
   into6B08;otherchannelbitselectsalternateconstant. Companionbranch using71ECbit1,62C0*62D8
   andabs62DA,clamp±26604 into6B08;otherchannelbitselectsalternateconstant. */

void f33_update_limit_budget_branch1(void)

{
  int iVar1;
  int iVar2;
  
  if ((DAT_febe71ec & 2) != 0) {
    DAT_febe6b08 = 0;
    DAT_febe6b0c = 0;
    DAT_febe6b10 = 0;
    return;
  }
  iVar1 = DAT_00031938;
  if ((DAT_febe71ec & 1) != 0) {
    iVar1 = DAT_0003193c;
  }
  iVar2 = (int)DAT_febe62da;
  DAT_febe6b10 = iVar1 - (int)DAT_febe62c0 * (int)DAT_febe62d8;
  if (iVar2 < 0) {
    iVar2 = -iVar2;
  }
  else {
    iVar1 = DAT_00031920;
    if (iVar2 == 0) goto LAB_00035da4;
  }
  iVar1 = DAT_febe6b10;
  if (iVar2 != 0) {
    if (DAT_febe6b10 == -0x80000000 && iVar2 == -1) {
      iVar1 = -0x80000000;
    }
    else {
      iVar1 = DAT_febe6b10 / iVar2;
    }
  }
LAB_00035da4:
  iVar2 = DAT_00031920;
  if (iVar1 - DAT_00031920 < 0 !=
      (iVar1 < 0 != DAT_00031920 < 0 && DAT_00031920 < 0 == iVar1 - DAT_00031920 < 0)) {
    iVar2 = iVar1;
  }
  DAT_febe6b08 = -DAT_00031920;
  if (iVar2 + DAT_00031920 < 0 ==
      (iVar2 < 0 != DAT_febe6b08 < 0 && DAT_febe6b08 < 0 == iVar2 + DAT_00031920 < 0)) {
    DAT_febe6b08 = iVar2;
  }
  DAT_febe6b0c = (int)DAT_febe62c0 * (int)DAT_febe62d8;
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_35dc0(void)

{
  return;
}



/* Seedfilteredbudget,maprequest/finalrequest26604, bothaccumulators26604<<16;
   clearnegativequalificationandreleasemarkers/counts. */

void f33_reset_owner9_budget_limit_state(void)

{
  DAT_febe6b14 = 0;
  DAT_febe6b15 = 0;
  DAT_febe6b1e = 0;
  DAT_febe6b18 = DAT_0003192a;
  DAT_febe6b24 = (uint)DAT_0003192a << 0x10;
  DAT_febe6b1a = DAT_0003192a;
  DAT_febe6b16 = DAT_0003192a;
  DAT_febe6b28 = (uint)DAT_0003192a << 0x10;
  DAT_febe6b1c = 0;
  return;
}



/* Zeroextend low16budget; map38678 withsigned6422 selector, signedcap22170 andzeroextendresult. */

uint f33_map_owner9_budget_limit(uint budget)

{
  uint uVar1;
  
  uVar1 = f33_lookup_signed_five_map_signal(budget & 0xffff,DAT_febe6422);
  if ((int)(uVar1 - 0x569a) < 0 == ((int)uVar1 < 0 && -1 < (int)(uVar1 - 0x569a))) {
    uVar1 = 0x569a;
  }
  return uVar1 & 0xffff;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_35fac(void)

{
  return;
}



/* Clear active6B2C,phase6B2D,reserved6B2E and invocation counter6B30. Does not itself release slot1
   or request word7. */

void f33_initialize_terminal_output_ramp(void)

{
  DAT_febe6b2c = 0;
  DAT_febe6b2d = 0;
  DAT_febe6b2e = 0;
  DAT_febe6b30 = 0;
  return;
}



/* Only active6B2C==5A publishes slot1 in both banks. Entry count<60000 requests owner7 mask40004,
   advances by200 only when6798==1 otherwise1, interpolates exact30E60, and sets phase1. Map is0
   through59950 then rises to8000 at60000. Already-terminal count requests70017001, codes8000 and
   phase2 without advancing. Inactive clears request7/count/phase and releases slot1, retaining its
   triplets. No wall-time or electrical-duty claim; later aggregate neutral slot3 can outrank slot1.
    */

void f33_step_terminal_output_ramp(void)

{
  short sVar1;
  uint32_t puVar2;
  undefined1 uVar3;
  ushort uVar4;
  ushort uStack_1a;
  ushort uStack_18;
  ushort uStack_16;
  ushort uStack_14;
  ushort uStack_12;
  ushort uStack_10;
  ushort uStack_e;
  
  uVar4 = DAT_febe6b30;
  puVar2 = 0xfebeb800u;
  if (DAT_febe6b2c == 'Z') {
    if (DAT_febe6b30 < DAT_00030e5a) {
      puVar2 = 0xfebeb800u;
      f33_set_output_request_word('\a',0x40004);
      sVar1 = DAT_00030e5c;
      if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x5068))))) != '\x01') {
        sVar1 = 1;
      }
      uVar4 = uVar4 + sVar1;
      FUN_00070304(((undefined *)camry_host_ptr(0x30e60u)),uVar4,&uStack_1a);
      uVar3 = 1;
    }
    else {
      puVar2 = 0xfebeb800u;
      f33_set_output_request_word('\a',0x70017001);
      uStack_1a = 0x8000;
      uVar3 = 2;
    }
    uStack_18 = uStack_1a;
    uStack_16 = uStack_1a;
    uStack_14 = uStack_1a;
    uStack_12 = uStack_1a;
    uStack_10 = uStack_1a;
    uStack_e = uStack_1a;
    f33_write_phase_output_slot_pair(2,'\x01',&uStack_12,&uStack_18);
    f33_activate_phase_output_slot_pair('\x01');
  }
  else {
    f33_set_output_request_word('\a',0);
    uVar4 = 0;
    uVar3 = 0;
    f33_release_phase_output_slot_pair('\x01');
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffb32du + (uint32_t)((int)puVar2) * 1u)))) = uVar3;
  (*((ushort *)camry_host_ptr((uint32_t)((0xffffb330u + (uint32_t)((int)puVar2)))))) = uVar4;
  return;
}



undefined1 FUN_00036066(byte param_1,short param_2)

{
  int iVar1;
  undefined1 uVar2;
  int iVar3;
  
  if ((param_1 & 3) == 0) {
    uVar2 = 1;
  }
  else {
    iVar1 = (int)param_2;
    if (DAT_febe6b2e == 0) {
      if (iVar1 + 0x7fff < 0 == (-1 < iVar1 && iVar1 + 0x7fff < 0) && iVar1 != -0x7fff) {
        if (iVar1 < 0) {
          iVar1 = (int)-param_2;
        }
      }
      else {
        iVar1 = 0x7fff;
      }
      iVar3 = (int)DAT_00030e58;
      uVar2 = iVar1 - iVar3 < 0 == (iVar1 < 0 != iVar3 < 0 && iVar3 < 0 == iVar1 - iVar3 < 0) &&
              iVar1 != iVar3;
    }
    else {
      uVar2 = 2;
    }
    DAT_febe6b2e = DAT_febe6b2e | param_1;
  }
  return uVar2;
}



/* Set active6B2C=5A only; do not reset retained ramp count. Fault output router3C470 is the
   recovered requester. */

void f33_request_terminal_output_ramp(void)

{
  DAT_febe6b2c = 0x5a;
  return;
}



/* Clear active6B2C only. Subsequent35FBC invocation clears request7/count/phase and releases slot1;
   this setter is not immediate output retirement. */

void f33_cancel_terminal_output_ramp(void)

{
  DAT_febe6b2c = 0;
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_360cc(void)

{
  return;
}



void FUN_000360ce(void)

{
  DAT_febe6798 = 0;
  DAT_febe6799 = DAT_00030e70;
  return;
}



void FUN_000360e0(void)

{
  int iVar1;
  bool bVar2;
  char cVar3;
  int iVar4;
  int iVar5;
  int iVar6;
  int iVar7;
  
  iVar5 = -(int)DAT_febe64e2;
  cVar3 = DAT_00030e70;
  if ((DAT_febe64cc & 0x40004) == 0) {
    DAT_febe6798 = 0;
  }
  else {
    iVar6 = (int)DAT_febe6770;
    iVar7 = (int)DAT_00030e72;
    if (((iVar6 - iVar7 < 0 == (iVar6 < 0 != iVar7 < 0 && iVar7 < 0 == iVar6 - iVar7 < 0) &&
          iVar6 != iVar7) &&
        (iVar4 = (int)DAT_00030e74, iVar1 = iVar5 + -iVar4,
        iVar1 < 0 == (iVar5 < 0 != iVar4 < 0 && iVar4 < 0 == iVar1 < 0) &&
        -iVar4 != (int)DAT_febe64e2)) ||
       ((iVar6 + iVar7 < 0 != (iVar6 < 0 != -iVar7 < 0 && -iVar7 < 0 == iVar6 + iVar7 < 0) &&
        (iVar6 = iVar5 + DAT_00030e74, bVar2 = -(int)DAT_00030e74 < 0,
        iVar6 < 0 != (iVar5 < 0 != bVar2 && bVar2 == iVar6 < 0))))) {
      if (DAT_febe6799 == '\0') {
        DAT_febe6798 = 1;
        cVar3 = '\0';
      }
      else {
        cVar3 = DAT_febe6799 + -1;
      }
    }
  }
  DAT_febe6799 = cVar3;
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_36140(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_36142(void)

{
  return;
}



/* WARNING: Removing unreachable block (ram,0x00036250) */
/* WARNING: Removing unreachable block (ram,0x0003624a) */
/* WARNING: Removing unreachable block (ram,0x00036230) */
/* WARNING: Removing unreachable block (ram,0x00036222) */
/* WARNING: Removing unreachable block (ram,0x0003621e) */
/* WARNING: Removing unreachable block (ram,0x0003621a) */
/* WARNING: Removing unreachable block (ram,0x000361a8) */
/* WARNING: Removing unreachable block (ram,0x000361a2) */
/* WARNING: Removing unreachable block (ram,0x00036188) */
/* WARNING: Removing unreachable block (ram,0x0003617a) */
/* WARNING: Removing unreachable block (ram,0x00036176) */
/* WARNING: Removing unreachable block (ram,0x00036172) */
/* Transform two conditioned phase-current banks using measured-frame coefficient pairs7D4E/50
   and7D5A/5C. Keep32-bit results6B3C/40/44/48 plus saturated halfword mirrors6B34..3A. ADC/DMA
   freshness and physical phase identity are separate dependencies. Dual-bank measured
   phase-to-rotating-frame transform preserves32-bit outputs and separate saturated halfword
   mirrors. Measured-frame coefficients differ from output-frame coefficients. ADC freshness and
   rotor/sample alignment not established. */

void f33_transform_measured_phase_currents(void)

{
  int iVar1;
  int iVar2;
  
  iVar2 = (((DAT_febe7e46 * 2 - (int)DAT_febe7e48) - (int)DAT_febe7e4a) * 0x3441) / 0x8000;
  iVar1 = (((int)DAT_febe7e48 - (int)DAT_febe7e4a) * 0x5a82) / 0x8000;
  DAT_febe6b3c = (iVar1 * (DAT_febe7d4e / 4) + iVar2 * (DAT_febe7d50 / 4)) / 0x2000;
  DAT_febe6b40 = (iVar1 * (DAT_febe7d50 / 4) - iVar2 * (DAT_febe7d4e / 4)) / 0x2000;
  if (DAT_febe6b3c + 0x7fff < 0 == (-1 < DAT_febe6b3c && DAT_febe6b3c + 0x7fff < 0) &&
      DAT_febe6b3c != -0x7fff) {
    iVar2 = DAT_febe6b3c;
    if (DAT_febe6b3c + -0x7fff < 0 == (DAT_febe6b3c < 0 && -1 < DAT_febe6b3c + -0x7fff) &&
        DAT_febe6b3c != 0x7fff) {
      iVar2 = 0x7fff;
    }
  }
  else {
    iVar2 = -0x7fff;
  }
  DAT_febe6b34 = (short)iVar2;
  if (DAT_febe6b40 + 0x7fff < 0 == (-1 < DAT_febe6b40 && DAT_febe6b40 + 0x7fff < 0) &&
      DAT_febe6b40 != -0x7fff) {
    iVar2 = DAT_febe6b40;
    if (DAT_febe6b40 + -0x7fff < 0 == (DAT_febe6b40 < 0 && -1 < DAT_febe6b40 + -0x7fff) &&
        DAT_febe6b40 != 0x7fff) {
      iVar2 = 0x7fff;
    }
  }
  else {
    iVar2 = -0x7fff;
  }
  DAT_febe6b36 = (short)iVar2;
  iVar2 = (((DAT_febe7e4c * 2 - (int)DAT_febe7e4e) - (int)DAT_febe7e50) * 0x3441) / 0x8000;
  iVar1 = (((int)DAT_febe7e4e - (int)DAT_febe7e50) * 0x5a82) / 0x8000;
  DAT_febe6b44 = (iVar1 * (DAT_febe7d5a / 4) + iVar2 * (DAT_febe7d5c / 4)) / 0x2000;
  DAT_febe6b48 = (iVar1 * (DAT_febe7d5c / 4) - iVar2 * (DAT_febe7d5a / 4)) / 0x2000;
  if (DAT_febe6b44 + 0x7fff < 0 == (-1 < DAT_febe6b44 && DAT_febe6b44 + 0x7fff < 0) &&
      DAT_febe6b44 != -0x7fff) {
    iVar2 = DAT_febe6b44;
    if (DAT_febe6b44 + -0x7fff < 0 == (DAT_febe6b44 < 0 && -1 < DAT_febe6b44 + -0x7fff) &&
        DAT_febe6b44 != 0x7fff) {
      iVar2 = 0x7fff;
    }
  }
  else {
    iVar2 = -0x7fff;
  }
  DAT_febe6b38 = (short)iVar2;
  if (DAT_febe6b48 + 0x7fff < 0 == (-1 < DAT_febe6b48 && DAT_febe6b48 + 0x7fff < 0) &&
      DAT_febe6b48 != -0x7fff) {
    iVar2 = DAT_febe6b48;
    if (DAT_febe6b48 + -0x7fff < 0 == (DAT_febe6b48 < 0 && -1 < DAT_febe6b48 + -0x7fff) &&
        DAT_febe6b48 != 0x7fff) {
      iVar2 = 0x7fff;
    }
  }
  else {
    iVar2 = -0x7fff;
  }
  DAT_febe6b3a = (short)iVar2;
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_36296(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_36298(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_36344(void)

{
  return;
}



/* Mode-entry initializer forwards to bank0 feedback reset; no enable test or acquisition. */

void f33_initialize_bank0_current_reference_feedback(void)

{
  f33_reset_bank0_current_reference_feedback();
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_364dc(void)

{
  return;
}



/* Mode-entry initializer forwards to bank1 feedback reset; no enable test or acquisition. */

void f33_initialize_bank1_current_reference_feedback(void)

{
  f33_reset_bank1_current_reference_feedback();
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_36674(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_36676(void)

{
  return;
}



/* WARNING: Removing unreachable block (ram,0x00036742) */
/* WARNING: Removing unreachable block (ram,0x000366c6) */
/* WARNING: Removing unreachable block (ram,0x000366a6) */
/* Only8A14==1 recomputes32-bit6B98; otherwise retain it. Exact calibrated7DB2 base curve collapses
   to100. WhenEAC6<512, abs(7EA8)>683 reduces the base toward0 at3413, and above3413 selects0. Scale
   by6BE4/1024. No recovered physical units; native composition exercises retained amplitude, not
   this entire recomputation surface. Native nonzero tail from5E280 and full
   staging-only5E202(2,0101) verify scoped transform, retention and arbitration effects. No fresh
   acquisition, upstream nonzero regulation or physical PWM claim. */

void f33_refresh_phase_compensation_amplitude(void)

{
  int iVar1;
  int iVar2;
  uint uVar3;
  uint uVar4;
  uint uVar5;
  uint uVar6;
  uint uVar7;
  
  if (DAT_febe8a14 != '\x01') {
    return;
  }
  uVar6 = (uint)DAT_febe7db2;
  if ((DAT_000319aa < uVar6) || (uVar6 < DAT_000319ac)) {
    uVar3 = (uint)DAT_000319ba;
    uVar7 = uVar3;
  }
  else {
    uVar4 = (uint)DAT_000319b6;
    uVar3 = (uint)DAT_000319b8;
    uVar7 = (int)DAT_000319b2 + (int)(uVar6 * (int)DAT_000319ae) / 0x100;
    uVar5 = uVar4;
    if ((int)(uVar7 - uVar4) < 0 != ((int)uVar7 < 0 && -1 < (int)(uVar7 - uVar4))) {
      uVar5 = uVar7;
    }
    uVar7 = uVar3;
    if ((int)(uVar5 - uVar3) < 0 == ((int)uVar5 < 0 && -1 < (int)(uVar5 - uVar3))) {
      uVar7 = uVar5;
    }
    uVar6 = (int)DAT_000319b4 + (int)(uVar6 * (int)DAT_000319b0) / 0x100;
    if ((int)(uVar6 - uVar4) < 0 != ((int)uVar6 < 0 && -1 < (int)(uVar6 - uVar4))) {
      uVar4 = uVar6;
    }
    if ((int)(uVar4 - uVar3) < 0 == ((int)uVar4 < 0 && -1 < (int)(uVar4 - uVar3))) {
      uVar3 = uVar4;
    }
    uVar3 = uVar3 & 0xffff;
  }
  uVar6 = (uint)DAT_febe7ea8;
  if ((int)(uVar6 + 0x7fff) < 0 == (-1 < (int)uVar6 && (int)(uVar6 + 0x7fff) < 0) &&
      uVar6 != 0xffff8001) {
    if ((int)uVar6 < 0) {
      uVar6 = (uint)-DAT_febe7ea8;
    }
  }
  else {
    uVar6 = 0x7fff;
  }
  uVar4 = (uint)DAT_000319bc;
  uVar5 = (uint)DAT_000319be;
  if (DAT_febeeac6 < DAT_000319a8) {
    if ((int)(uVar6 - uVar4) < 0 == ((int)uVar6 < 0 && -1 < (int)(uVar6 - uVar4)) && uVar6 != uVar4)
    {
      uVar3 = (uint)DAT_000319c0;
      if ((int)(uVar6 - uVar5) < 0 == ((int)uVar6 < 0 && -1 < (int)(uVar6 - uVar5)) &&
          uVar6 != uVar5) goto LAB_00036736;
      iVar1 = uVar5 - uVar4;
      iVar2 = (uVar7 - DAT_000319c0) * (uVar6 - uVar4);
      if (iVar1 != 0) {
        if (iVar2 == -0x80000000 && iVar1 == -1) {
          iVar2 = 0;
        }
        else {
          iVar2 = iVar2 / iVar1;
        }
      }
      uVar7 = uVar7 - iVar2;
    }
    uVar3 = uVar7 & 0xffff;
  }
LAB_00036736:
  DAT_febe6b98 = (int)(uVar3 * DAT_febe6be4) / 0x400;
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_3674c(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_3674e(void)

{
  return;
}



/* Retain raw regulated triplet in6BB4/B8/BC. Reference6E58/5A/5C selects signed compensation
   bounded by +/-6B98, linear within +/-96. Always calculate6BA8/AC/B0; modeA5 suppresses ADDITION,
   not calculation. Publish adjusted32-bit triplet6B9C/BA0/BA4. Native nonzero tail from5E280 and
   full staging-only5E202(2,0101) verify scoped transform, retention and arbitration effects. No
   fresh acquisition, upstream nonzero regulation or physical PWM claim. */

void f33_compensate_first_regulated_phases(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  
  DAT_febe6ba4 = (int)DAT_febe6e6c;
  DAT_febe6ba0 = (int)DAT_febe6e6a;
  iVar4 = (int)DAT_000319c6;
  DAT_febe6b9c = (int)DAT_febe6e68;
  DAT_febe6bbc = DAT_febe6ba4;
  DAT_febe6bb8 = DAT_febe6ba0;
  iVar2 = (int)DAT_febe6e58;
  DAT_febe6bb4 = DAT_febe6b9c;
  iVar3 = (int)DAT_febe6e5c;
  iVar5 = (int)DAT_febe6e5a;
  iVar1 = -iVar4;
  if (iVar2 + iVar4 < 0 == (iVar2 < 0 != iVar1 < 0 && iVar1 < 0 == iVar2 + iVar4 < 0) &&
      iVar2 != iVar1) {
    DAT_febe6ba8 = DAT_febe6b98;
    if ((iVar2 - iVar4 < 0 != (iVar2 < 0 != iVar4 < 0 && iVar4 < 0 == iVar2 - iVar4 < 0)) &&
       (DAT_febe6ba8 = iVar2 * DAT_febe6b98, iVar4 != 0)) {
      if (DAT_febe6ba8 == -0x80000000 && iVar4 == -1) {
        DAT_febe6ba8 = -0x80000000;
      }
      else {
        DAT_febe6ba8 = DAT_febe6ba8 / iVar4;
      }
    }
  }
  else {
    DAT_febe6ba8 = -DAT_febe6b98;
  }
  if (iVar5 + iVar4 < 0 == (iVar5 < 0 != iVar1 < 0 && iVar1 < 0 == iVar5 + iVar4 < 0) &&
      iVar5 != iVar1) {
    DAT_febe6bac = DAT_febe6b98;
    if ((iVar5 - iVar4 < 0 != (iVar5 < 0 != iVar4 < 0 && iVar4 < 0 == iVar5 - iVar4 < 0)) &&
       (DAT_febe6bac = iVar5 * DAT_febe6b98, iVar4 != 0)) {
      if (DAT_febe6bac == -0x80000000 && iVar4 == -1) {
        DAT_febe6bac = -0x80000000;
      }
      else {
        DAT_febe6bac = DAT_febe6bac / iVar4;
      }
    }
  }
  else {
    DAT_febe6bac = -DAT_febe6b98;
  }
  if (iVar3 + iVar4 < 0 == (iVar3 < 0 != iVar1 < 0 && iVar1 < 0 == iVar3 + iVar4 < 0) &&
      iVar3 != iVar1) {
    DAT_febe6bb0 = DAT_febe6b98;
    if ((iVar3 - iVar4 < 0 != (iVar3 < 0 != iVar4 < 0 && iVar4 < 0 == iVar3 - iVar4 < 0)) &&
       (DAT_febe6bb0 = iVar3 * DAT_febe6b98, iVar4 != 0)) {
      if (DAT_febe6bb0 == -0x80000000 && iVar4 == -1) {
        DAT_febe6bb0 = -0x80000000;
      }
      else {
        DAT_febe6bb0 = DAT_febe6bb0 / iVar4;
      }
    }
  }
  else {
    DAT_febe6bb0 = -DAT_febe6b98;
  }
  if (((int8_t)DAT_febe6d5c) != -0x5b) {
    DAT_febe6b9c = DAT_febe6ba8 + DAT_febe6b9c;
    DAT_febe6ba0 = DAT_febe6bac + DAT_febe6ba0;
    DAT_febe6ba4 = DAT_febe6bb0 + DAT_febe6ba4;
  }
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_367fa(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_367fc(void)

{
  return;
}



/* Second bank: reference6E60/62/64 and regulated6E70/72/74; raw backup6BD8/DC/E0, computed
   deltas6BCC/D0/D4, adjusted6BC0/C4/C8. ModeA5 retains raw output despite nonzero computed deltas.
   Signed divisions truncate toward zero. Native nonzero tail from5E280 and full
   staging-only5E202(2,0101) verify scoped transform, retention and arbitration effects. No fresh
   acquisition, upstream nonzero regulation or physical PWM claim. */

void f33_compensate_second_regulated_phases(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  
  DAT_febe6bc8 = (int)DAT_febe6e74;
  DAT_febe6bc4 = (int)DAT_febe6e72;
  iVar4 = (int)DAT_000319ca;
  DAT_febe6bc0 = (int)DAT_febe6e70;
  DAT_febe6be0 = DAT_febe6bc8;
  DAT_febe6bdc = DAT_febe6bc4;
  iVar2 = (int)DAT_febe6e60;
  DAT_febe6bd8 = DAT_febe6bc0;
  iVar3 = (int)DAT_febe6e64;
  iVar5 = (int)DAT_febe6e62;
  iVar1 = -iVar4;
  if (iVar2 + iVar4 < 0 == (iVar2 < 0 != iVar1 < 0 && iVar1 < 0 == iVar2 + iVar4 < 0) &&
      iVar2 != iVar1) {
    DAT_febe6bcc = DAT_febe6b98;
    if ((iVar2 - iVar4 < 0 != (iVar2 < 0 != iVar4 < 0 && iVar4 < 0 == iVar2 - iVar4 < 0)) &&
       (DAT_febe6bcc = iVar2 * DAT_febe6b98, iVar4 != 0)) {
      if (DAT_febe6bcc == -0x80000000 && iVar4 == -1) {
        DAT_febe6bcc = -0x80000000;
      }
      else {
        DAT_febe6bcc = DAT_febe6bcc / iVar4;
      }
    }
  }
  else {
    DAT_febe6bcc = -DAT_febe6b98;
  }
  if (iVar5 + iVar4 < 0 == (iVar5 < 0 != iVar1 < 0 && iVar1 < 0 == iVar5 + iVar4 < 0) &&
      iVar5 != iVar1) {
    DAT_febe6bd0 = DAT_febe6b98;
    if ((iVar5 - iVar4 < 0 != (iVar5 < 0 != iVar4 < 0 && iVar4 < 0 == iVar5 - iVar4 < 0)) &&
       (DAT_febe6bd0 = iVar5 * DAT_febe6b98, iVar4 != 0)) {
      if (DAT_febe6bd0 == -0x80000000 && iVar4 == -1) {
        DAT_febe6bd0 = -0x80000000;
      }
      else {
        DAT_febe6bd0 = DAT_febe6bd0 / iVar4;
      }
    }
  }
  else {
    DAT_febe6bd0 = -DAT_febe6b98;
  }
  if (iVar3 + iVar4 < 0 == (iVar3 < 0 != iVar1 < 0 && iVar1 < 0 == iVar3 + iVar4 < 0) &&
      iVar3 != iVar1) {
    DAT_febe6bd4 = DAT_febe6b98;
    if ((iVar3 - iVar4 < 0 != (iVar3 < 0 != iVar4 < 0 && iVar4 < 0 == iVar3 - iVar4 < 0)) &&
       (DAT_febe6bd4 = iVar3 * DAT_febe6b98, iVar4 != 0)) {
      if (DAT_febe6bd4 == -0x80000000 && iVar4 == -1) {
        DAT_febe6bd4 = -0x80000000;
      }
      else {
        DAT_febe6bd4 = DAT_febe6bd4 / iVar4;
      }
    }
  }
  else {
    DAT_febe6bd4 = -DAT_febe6b98;
  }
  if (((int8_t)DAT_febe6d5d) != -0x5b) {
    DAT_febe6bc0 = DAT_febe6bcc + DAT_febe6bc0;
    DAT_febe6bc4 = DAT_febe6bd0 + DAT_febe6bc4;
    DAT_febe6bc8 = DAT_febe6bd4 + DAT_febe6bc8;
  }
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_368a8(void)

{
  return;
}



/* Single constant publisher: DAT_febe6be4 = 0; Shape-classified from the canonical corpus; the
   target cell is not yet named, so the written state's meaning is unknown. */

void FUN_000368aa(void)

{
  DAT_febe6be4 = 0;
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_3690e(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_36c1a(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_36f22(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_36f24(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_370d4(void)

{
  return;
}



/* Constant-block fill: 5 literal assignments into one contiguous cell block; shape-verified.
   Literals are default/reset values; cell meanings are not recovered. */

void f33_fill_constant_block_370d6(void)

{
  DAT_febe6c70 = 0;
  DAT_febe6c72 = 0;
  DAT_febe6c74 = 0;
  DAT_febe6c76 = 0;
  DAT_febe6c78 = 0;
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_37216(void)

{
  return;
}



/* Constant-block fill: 5 literal assignments into one contiguous cell block; shape-verified.
   Literals are default/reset values; cell meanings are not recovered. */

void f33_fill_constant_block_37218(void)

{
  DAT_febe6c7c = 0;
  DAT_febe6c7e = 0;
  DAT_febe6c80 = 0;
  DAT_febe6c82 = 0;
  DAT_febe6c8c = 0;
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_373bc(void)

{
  return;
}



/* Constant-block fill: 13 literal assignments into one contiguous cell block; shape-verified.
   Literals are default/reset values; cell meanings are not recovered. */

void f33_fill_constant_block_373be(void)

{
  DAT_febe6c90 = 0;
  DAT_febe6c92 = 0;
  DAT_febe6c94 = 0;
  DAT_febe6c9c = DAT_febe6d14;
  DAT_febe6c96 = 0;
  DAT_febe6ca0 = 0;
  DAT_febe6cb4 = 0;
  DAT_febe6c98 = 0;
  DAT_febe6c9a = 0;
  DAT_febe6ca8 = 0;
  DAT_febe6cb0 = 0;
  DAT_febe6cac = 0;
  DAT_febe6ca4 = DAT_febe6d54;
  return;
}



int FUN_000373e6(void)

{
  int iVar1;
  int iVar2;
  
  iVar1 = (int)DAT_febe6d7e - (int)DAT_febe6d76;
  if (iVar1 + 0x7fff < 0 == (-1 < iVar1 && iVar1 + 0x7fff < 0) && iVar1 != -0x7fff) {
    if (iVar1 + -0x7fff < 0 == (iVar1 < 0 && -1 < iVar1 + -0x7fff) && iVar1 != 0x7fff) {
      iVar2 = 0x7fff;
    }
    else {
      iVar2 = -0x8000;
      if (iVar1 + 0x8000 < 0 == (-1 < iVar1 && iVar1 + 0x8000 < 0)) {
        iVar2 = (int)(short)iVar1;
      }
    }
    return iVar2;
  }
  return -0x7fff;
}



/* WARNING: Removing unreachable block (ram,0x000374d0) */

void FUN_00037460(short param_1,char param_2)

{
  int iVar1;
  uint uVar2;
  uint uVar3;
  int iVar4;
  int iVar5;
  uint uVar6;
  
  DAT_febe6ca4 = DAT_febe6d54;
  DAT_febe6c9c = DAT_febe6d14;
  uVar2 = (uint)DAT_00031a4c;
  iVar5 = (int)param_1;
  if (param_2 == '\x01') {
    iVar5 = 0;
  }
  if (DAT_febe6d14 < uVar2) {
    uVar2 = (uint)DAT_febe6d14;
  }
  uVar3 = (uint)DAT_00031a4e;
  if (uVar3 <= uVar2) {
    uVar3 = uVar2;
  }
  uVar2 = DAT_00031a50;
  if (DAT_febe6d54 < DAT_00031a50) {
    uVar2 = DAT_febe6d54;
  }
  uVar6 = DAT_00031a54;
  if (DAT_00031a54 <= uVar2) {
    uVar6 = uVar2;
  }
  iVar4 = DAT_00031a58;
  if (DAT_febe6ca0 - DAT_00031a58 < 0 !=
      (DAT_febe6ca0 < 0 != DAT_00031a58 < 0 && DAT_00031a58 < 0 == DAT_febe6ca0 - DAT_00031a58 < 0))
  {
    iVar4 = DAT_febe6ca0;
  }
  DAT_febe6ca0 = -DAT_00031a58;
  DAT_febe6ca8 = DAT_febe6ca0;
  if (iVar4 + DAT_00031a58 < 0 ==
      (iVar4 < 0 != DAT_febe6ca0 < 0 && DAT_febe6ca0 < 0 == iVar4 + DAT_00031a58 < 0)) {
    DAT_febe6ca8 = iVar4;
  }
  DAT_febe6cac = (uVar6 >> 9) * (DAT_febe6c94 + iVar5);
  DAT_febe6cb0 = uVar3 * ((int)param_1 - (int)DAT_febe6c92);
  iVar4 = DAT_febe6cac / 0x40 + DAT_febe6cb0;
  if (iVar4 < 1) {
    if ((DAT_febe6ca8 < 1) &&
       (iVar1 = -0x7fffffff - iVar4,
       iVar1 - DAT_febe6ca8 < 0 ==
       (iVar1 < 0 != DAT_febe6ca8 < 0 && DAT_febe6ca8 < 0 == iVar1 - DAT_febe6ca8 < 0) &&
       iVar1 != DAT_febe6ca8)) {
      DAT_febe6cb4 = -0x7fffffff;
      goto LAB_00037512;
    }
  }
  else if ((0 < DAT_febe6ca8) &&
          (iVar1 = (0x7fffffff - iVar4) - DAT_febe6ca8,
          iVar1 < 0 != (0x7fffffff - iVar4 < 0 != DAT_febe6ca8 < 0 && DAT_febe6ca8 < 0 == iVar1 < 0)
          )) {
    DAT_febe6cb4 = 0x7fffffff;
    goto LAB_00037512;
  }
  DAT_febe6cb4 = DAT_febe6ca8 + iVar4;
LAB_00037512:
  DAT_febe6c98 = DAT_febe6c92;
  iVar4 = DAT_00031a58;
  if (DAT_febe6cb4 - DAT_00031a58 < 0 !=
      (DAT_febe6cb4 < 0 != DAT_00031a58 < 0 && DAT_00031a58 < 0 == DAT_febe6cb4 - DAT_00031a58 < 0))
  {
    iVar4 = DAT_febe6cb4;
  }
  DAT_febe6c9a = DAT_febe6c94;
  DAT_febe6c92 = param_1;
  if (iVar4 + DAT_00031a58 < 0 ==
      (iVar4 < 0 != DAT_febe6ca0 < 0 && DAT_febe6ca0 < 0 == iVar4 + DAT_00031a58 < 0)) {
    DAT_febe6ca0 = iVar4;
  }
  DAT_febe6c94 = (short)iVar5;
  DAT_febe6c96 = param_1;
  return;
}



/* Differential second-axis regulator aggregate373E6/37418/37460: error=sat(6D7E-6D76),
   accumulator6CA0, directional anti-windup and additional clamp31A58. Reset follows selected
   arbitration indices and acquisition status, not a generic diagnostic inhibit. */

void FUN_00037538(void)

{
  undefined4 uVar1;
  undefined4 uVar2;
  
  if (((DAT_febe8bae == '\0') || (DAT_febe8baf == '\0')) &&
     ((f33_output_request_status & 0x40004) == 0)) {
    uVar1 = FUN_000373e6();
    uVar2 = FUN_00037418(uVar1);
    FUN_00037460(uVar1,uVar2);
  }
  else {
    DAT_febe6c90 = 0;
    DAT_febe6c92 = 0;
    DAT_febe6c94 = 0;
    DAT_febe6c9c = DAT_febe6d14;
    DAT_febe6c96 = 0;
    DAT_febe6ca0 = 0;
    DAT_febe6cb4 = 0;
    DAT_febe6c98 = 0;
    DAT_febe6c9a = 0;
    DAT_febe6ca8 = 0;
    DAT_febe6cb0 = 0;
    DAT_febe6cac = 0;
    DAT_febe6ca4 = DAT_febe6d54;
  }
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_3759a(void)

{
  return;
}



/* Constant-block fill: 12 literal assignments into one contiguous cell block; shape-verified.
   Literals are default/reset values; cell meanings are not recovered. */

void f33_fill_constant_block_3759c(void)

{
  DAT_febe6cb8 = 0;
  DAT_febe6cba = 0;
  DAT_febe6cbc = 0;
  DAT_febe6cc4 = DAT_febe6d04;
  DAT_febe6cbe = 0;
  DAT_febe6ccc = 0;
  DAT_febe6cc0 = 0;
  DAT_febe6cc2 = 0;
  DAT_febe6cd4 = 0;
  DAT_febe6cdc = 0;
  DAT_febe6cd8 = 0;
  DAT_febe6cd0 = DAT_febe6d3c;
  return;
}



int FUN_000375c2(void)

{
  int iVar1;
  
  iVar1 = DAT_febe6d7c - DAT_febe6d78;
  if (iVar1 + -0x7fff < 0 == (iVar1 < 0 && -1 < iVar1 + -0x7fff)) {
    iVar1 = 0x7fff;
  }
  if (iVar1 + 0x7fff < 0 != (-1 < iVar1 && iVar1 + 0x7fff < 0)) {
    iVar1 = -0x7fff;
  }
  return (int)(short)iVar1;
}



/* WARNING: Removing unreachable block (ram,0x00037728) */
/* WARNING: Removing unreachable block (ram,0x0003770a) */

void FUN_0003762e(short param_1,char param_2)

{
  uint uVar1;
  uint uVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  uint uVar6;
  
  iVar5 = (int)param_1;
  if (param_2 == '\x01') {
    iVar5 = 0;
  }
  DAT_febe6cc4 = DAT_febe6d04;
  DAT_febe6cd0 = DAT_febe6d3c;
  uVar1 = (uint)DAT_00031a5c;
  if (DAT_febe6d04 < uVar1) {
    uVar1 = (uint)DAT_febe6d04;
  }
  uVar2 = (uint)DAT_00031a5e;
  if (uVar2 <= uVar1) {
    uVar2 = uVar1;
  }
  uVar1 = DAT_00031a60;
  if (DAT_febe6d3c < DAT_00031a60) {
    uVar1 = DAT_febe6d3c;
  }
  uVar6 = DAT_00031a64;
  if (DAT_00031a64 <= uVar1) {
    uVar6 = uVar1;
  }
  iVar4 = DAT_00031a68;
  if (DAT_febe6ccc - DAT_00031a68 < 0 !=
      (DAT_febe6ccc < 0 != DAT_00031a68 < 0 && DAT_00031a68 < 0 == DAT_febe6ccc - DAT_00031a68 < 0))
  {
    iVar4 = DAT_febe6ccc;
  }
  DAT_febe6ccc = -DAT_00031a68;
  DAT_febe6cc8 = DAT_febe6ccc;
  if (iVar4 + DAT_00031a68 < 0 ==
      (iVar4 < 0 != DAT_febe6ccc < 0 && DAT_febe6ccc < 0 == iVar4 + DAT_00031a68 < 0)) {
    DAT_febe6cc8 = iVar4;
  }
  iVar4 = 0x7fffffff;
  if (((DAT_febe71ec & 1) == 0) || (DAT_febe6cc6 != 0)) {
    if (((DAT_febe71ec >> 1 & 1) != 0) && (DAT_febe6cc6 == 0)) {
      if (DAT_febe6cc8 < 1) {
        if ((0 < DAT_febe6ca0) ||
           (iVar4 = -0x7fffffff - DAT_febe6cc8,
           iVar4 - DAT_febe6ca0 < 0 !=
           (iVar4 < 0 != DAT_febe6ca0 < 0 && DAT_febe6ca0 < 0 == iVar4 - DAT_febe6ca0 < 0) ||
           iVar4 == DAT_febe6ca0)) goto LAB_00037704;
        iVar4 = -0x7fffffff;
      }
      else if ((DAT_febe6ca0 < 1) ||
              (iVar3 = (0x7fffffff - DAT_febe6cc8) - DAT_febe6ca0,
              iVar3 < 0 ==
              (0x7fffffff - DAT_febe6cc8 < 0 != DAT_febe6ca0 < 0 && DAT_febe6ca0 < 0 == iVar3 < 0)))
      {
LAB_00037704:
        iVar4 = DAT_febe6ca0 + DAT_febe6cc8;
      }
      goto LAB_00037708;
    }
  }
  else {
    if (DAT_febe6cc8 < 0) {
      if ((DAT_febe6ca0 < 0) ||
         (iVar4 = (DAT_febe6cc8 + 0x7fffffff) - DAT_febe6ca0,
         iVar4 < 0 ==
         (DAT_febe6cc8 + 0x7fffffff < 0 != DAT_febe6ca0 < 0 && DAT_febe6ca0 < 0 == iVar4 < 0)))
      goto LAB_000376d2;
      iVar4 = -0x7fffffff;
    }
    else if ((-1 < DAT_febe6ca0) ||
            (iVar3 = -(0x7fffffff - DAT_febe6cc8),
            iVar3 - DAT_febe6ca0 < 0 !=
            (iVar3 < 0 != DAT_febe6ca0 < 0 && DAT_febe6ca0 < 0 == iVar3 - DAT_febe6ca0 < 0) ||
            iVar3 == DAT_febe6ca0)) {
LAB_000376d2:
      iVar4 = DAT_febe6cc8 - DAT_febe6ca0;
    }
LAB_00037708:
    DAT_febe6cc8 = iVar4 / 2;
  }
  DAT_febe6cd8 = (uVar6 >> 9) * (DAT_febe6cbc + iVar5);
  DAT_febe6cc6 = DAT_febe71ec;
  DAT_febe6cdc = uVar2 * ((int)param_1 - (int)DAT_febe6cba);
  iVar4 = DAT_febe6cd8 / 0x40 + DAT_febe6cdc;
  if (iVar4 < 1) {
    if ((DAT_febe6cc8 < 1) &&
       (iVar3 = -0x7fffffff - iVar4,
       iVar3 - DAT_febe6cc8 < 0 ==
       (iVar3 < 0 != DAT_febe6cc8 < 0 && DAT_febe6cc8 < 0 == iVar3 - DAT_febe6cc8 < 0) &&
       iVar3 != DAT_febe6cc8)) {
      iVar4 = -0x7fffffff;
      goto LAB_0003775e;
    }
  }
  else if ((0 < DAT_febe6cc8) &&
          (iVar3 = (0x7fffffff - iVar4) - DAT_febe6cc8,
          iVar3 < 0 != (0x7fffffff - iVar4 < 0 != DAT_febe6cc8 < 0 && DAT_febe6cc8 < 0 == iVar3 < 0)
          )) {
    iVar4 = 0x7fffffff;
    goto LAB_0003775e;
  }
  iVar4 = DAT_febe6cc8 + iVar4;
LAB_0003775e:
  DAT_febe6cd4 = DAT_febe6cc8;
  DAT_febe6cc0 = DAT_febe6cba;
  iVar3 = DAT_00031a68;
  if (iVar4 - DAT_00031a68 < 0 !=
      (iVar4 < 0 != DAT_00031a68 < 0 && DAT_00031a68 < 0 == iVar4 - DAT_00031a68 < 0)) {
    iVar3 = iVar4;
  }
  DAT_febe6cc2 = DAT_febe6cbc;
  DAT_febe6cba = param_1;
  if (iVar3 + DAT_00031a68 < 0 ==
      (iVar3 < 0 != DAT_febe6ccc < 0 && DAT_febe6ccc < 0 == iVar3 + DAT_00031a68 < 0)) {
    DAT_febe6ccc = iVar3;
  }
  DAT_febe6cbc = (short)iVar5;
  DAT_febe6cbe = param_1;
  return;
}



/* Common second-axis regulator aggregate375C2/375E6/3762E: error uses unsaturated32-bit
   feedback6D78, not halfword6D72. Persistent accumulator6CCC, directional anti-windup and first
   channel-invalid transition adjustment; additional clamp31A68. */

void FUN_0003777e(void)

{
  undefined4 uVar1;
  undefined4 uVar2;
  
  if (((DAT_febe8bae == '\0') || (DAT_febe8baf == '\0')) &&
     ((f33_output_request_status & 0x40004) == 0)) {
    uVar1 = FUN_000375c2();
    uVar2 = FUN_000375e6(uVar1);
    FUN_0003762e(uVar1,uVar2);
  }
  else {
    DAT_febe6cb8 = 0;
    DAT_febe6cba = 0;
    DAT_febe6cbc = 0;
    DAT_febe6cc4 = DAT_febe6d04;
    DAT_febe6cbe = 0;
    DAT_febe6ccc = 0;
    DAT_febe6cc0 = 0;
    DAT_febe6cc2 = 0;
    DAT_febe6cd4 = 0;
    DAT_febe6cdc = 0;
    DAT_febe6cd8 = 0;
    DAT_febe6cd0 = DAT_febe6d3c;
  }
  return;
}



/* Set retained6CE4 to exact317AC=20480 only; no fresh input or qualification. */

void f33_initialize_shared_second_axis_envelope(void)

{
  f33_shared_second_axis_envelope = DAT_000317ac;
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_377ec(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_378d0(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_378d2(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_3791e(void)

{
  return;
}



/* Single constant publisher: DAT_febe6cf0 = 0x400; Shape-classified from the canonical corpus; the
   target cell is not yet named, so the written state's meaning is unknown. */

void FUN_00037920(void)

{
  DAT_febe6cf0 = 0x400;
  return;
}



void FUN_0003792a(void)

{
  int iVar1;
  uint uVar2;
  
  uVar2 = (uint)DAT_febe7da6;
  DAT_febe6cf0 = 0x400;
  if (uVar2 != 0) {
    iVar1 = (DAT_00031a6e - uVar2) * (uint)DAT_00031a6c;
    if (uVar2 != 0) {
      if (iVar1 == -0x80000000 && uVar2 == 0xffffffff) {
        iVar1 = -0x80000000;
      }
      else {
        iVar1 = iVar1 / (int)uVar2;
      }
    }
    DAT_febe6cf0 = iVar1 + 0x400;
  }
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_37954(void)

{
  return;
}



/* Single constant publisher: DAT_febe6cf4 = 0x400; Shape-classified from the canonical corpus; the
   target cell is not yet named, so the written state's meaning is unknown. */

void FUN_00037956(void)

{
  DAT_febe6cf4 = 0x400;
  return;
}



void FUN_00037960(void)

{
  int iVar1;
  uint uVar2;
  
  uVar2 = (uint)DAT_febe7da8;
  DAT_febe6cf4 = 0x400;
  if (uVar2 != 0) {
    iVar1 = (DAT_00031a72 - uVar2) * (uint)DAT_00031a70;
    if (uVar2 != 0) {
      if (iVar1 == -0x80000000 && uVar2 == 0xffffffff) {
        iVar1 = -0x80000000;
      }
      else {
        iVar1 = iVar1 / (int)uVar2;
      }
    }
    DAT_febe6cf4 = iVar1 + 0x400;
  }
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_3798a(void)

{
  return;
}



void FUN_0003798c(void)

{
  DAT_febe6cfa = 0;
  DAT_febe6cf8 = 0;
  DAT_febe6d08 = DAT_00031a78;
  DAT_febe6d34 = (uint)DAT_00031a78 << 0x10;
  DAT_febe6d00 = DAT_00031a7a;
  DAT_febe6d2c = (uint)DAT_00031a7a << 0x10;
  DAT_febe6d0a = DAT_00031a80;
  DAT_febe6d38 = (uint)DAT_00031a80 << 0x10;
  DAT_febe6d02 = DAT_00031a82;
  DAT_febe6d30 = (uint)DAT_00031a82 << 0x10;
  DAT_febe6d18 = DAT_00031a7c;
  DAT_febe6d4c = (uint)DAT_00031a7c << 0x10;
  DAT_febe6d10 = DAT_00031a7e;
  DAT_febe6d44 = (uint)DAT_00031a7e << 0x10;
  DAT_febe6d1a = DAT_00031a84;
  DAT_febe6d50 = (uint)DAT_00031a84 << 0x10;
  DAT_febe6d12 = DAT_00031a86;
  DAT_febe6d48 = (uint)DAT_00031a86 << 0x10;
  return;
}



undefined4 FUN_000379fc(void)

{
  if (((uint)((int)DAT_febe6e12 * (int)DAT_febe6e12 + (int)DAT_febe6e14 * (int)DAT_febe6e14) <
       DAT_00031ae0) &&
     ((uint)((int)DAT_febe6e16 * (int)DAT_febe6e16 + (int)DAT_febe6e18 * (int)DAT_febe6e18) <
      DAT_00031ae0)) {
    if ((DAT_febe6cf8 != 0) && (DAT_febe6cf8 < DAT_00031a9a)) goto LAB_00037a50;
    if ((DAT_febe7826 != 'Z') && (DAT_febe7936 != 'Z')) {
      DAT_febe6cf8 = 0;
      return 0;
    }
  }
  if (DAT_00031a9a <= DAT_febe6cf8) {
    return 0x5a;
  }
LAB_00037a50:
  DAT_febe6cf8 = DAT_febe6cf8 + 2;
  return 0x5a;
}



undefined4 FUN_00037a62(void)

{
  if (DAT_febee5c0 == '\0') {
    DAT_febe6cfa = 0;
    return 0;
  }
  if (DAT_febe6cfa < DAT_00031a98) {
    DAT_febe6cfa = DAT_febe6cfa + 2;
    return 0x5a;
  }
  return 0;
}



void FUN_00037a92(void)

{
  ushort uVar1;
  ushort uVar5;
  int iVar6;
  int iVar7;
  uint uVar8;
  uint32_t puVar9;
  int iVar10;
  undefined2 uVar11;
  undefined2 uVar12;
  undefined2 uVar13;
  undefined2 uVar14;
  int iVar15;
  uint uVar16;
  uint uVar17;
  uint uVar18;
  undefined2 *puVar19;
  ushort uVar2;
  ushort uVar3;
  ushort uVar4;
  
  uVar5 = DAT_febe71ec;
  puVar9 = 0xfebeb800u;
  if (DAT_febe8a14 != '\x01') {
    return;
  }
  DAT_febe6d20 = DAT_00031a78;
  DAT_febe6d1c = DAT_00031a7a;
  DAT_febe6d22 = DAT_00031a80;
  DAT_febe6d1e = DAT_00031a82;
  iVar6 = (int)DAT_febe5f36;
  if (iVar6 + 0x7fff < 0 == (-1 < iVar6 && iVar6 + 0x7fff < 0) && iVar6 != -0x7fff) {
    if (iVar6 < 0) {
      iVar6 = (int)-DAT_febe5f36;
    }
  }
  else {
    iVar6 = 0x7fff;
  }
  iVar10 = DAT_00031a76 - iVar6;
  uVar1 = DAT_00031a8c;
  uVar2 = DAT_00031a96;
  uVar3 = DAT_00031a94;
  uVar4 = DAT_00031a8e;
  if (iVar10 < 0 == (DAT_00031a76 < 0 != iVar6 < 0 && iVar6 < 0 == iVar10 < 0)) {
    uVar1 = DAT_00031a7c;
    uVar2 = DAT_00031a86;
    uVar3 = DAT_00031a84;
    uVar4 = DAT_00031a7e;
  }
  iVar6 = (uint)DAT_00031abc * 4;
  iVar10 = (uint)DAT_00031abe * 4;
  if (iVar6 - 1U < 0xffff) {
    iVar15 = (uint)DAT_febe6d18 * iVar6;
    iVar7 = (uint)uVar1 * iVar6;
  }
  else {
    iVar15 = (uint)DAT_febe6d18 << 0x10;
    iVar7 = (uint)uVar1 << 0x10;
  }
  DAT_febe6d4c = iVar7 + (DAT_febe6d4c - iVar15);
  DAT_febe6d18 = (ushort)((uint)DAT_febe6d4c >> 0x10);
  if (iVar10 - 1U < 0xffff) {
    iVar15 = (uint)DAT_febe6d10 * iVar10;
    iVar7 = (uint)uVar4 * iVar10;
  }
  else {
    iVar15 = (uint)DAT_febe6d10 << 0x10;
    iVar7 = (uint)uVar4 << 0x10;
  }
  DAT_febe6d44 = iVar7 + (DAT_febe6d44 - iVar15);
  DAT_febe6d10 = (ushort)((uint)DAT_febe6d44 >> 0x10);
  if (iVar6 - 1U < 0xffff) {
    iVar15 = (uint)DAT_febe6d1a * iVar6;
    iVar6 = (uint)uVar3 * iVar6;
  }
  else {
    iVar15 = (uint)DAT_febe6d1a << 0x10;
    iVar6 = (uint)uVar3 << 0x10;
  }
  DAT_febe6d50 = iVar6 + (DAT_febe6d50 - iVar15);
  DAT_febe6d1a = (ushort)((uint)DAT_febe6d50 >> 0x10);
  if (iVar10 - 1U < 0xffff) {
    iVar6 = (uint)DAT_febe6d12 * iVar10;
    iVar10 = (uint)uVar2 * iVar10;
  }
  else {
    iVar6 = (uint)DAT_febe6d12 << 0x10;
    iVar10 = (uint)uVar2 << 0x10;
  }
  DAT_febe6d48 = iVar10 + (DAT_febe6d48 - iVar6);
  DAT_febe6d12 = (ushort)((uint)DAT_febe6d48 >> 0x10);
  DAT_febe6d24 = DAT_febe6d10;
  DAT_febe6d26 = DAT_febe6d12;
  DAT_febe6d28 = DAT_febe6d18;
  DAT_febe6d2a = DAT_febe6d1a;
  iVar6 = FUN_000379fc();
  iVar10 = FUN_00037a62();
  if ((uVar5 & 3) == 0) {
    if (iVar6 == 0x5a) {
      puVar19 = ((undefined *)camry_host_ptr(0x31aacu));
    }
    else {
      if (iVar10 != 0x5a) {
        uVar14 = (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffb520u + (uint32_t)((int)puVar9))))));
        uVar8 = (uint)(*((ushort *)camry_host_ptr((uint32_t)((0xffffb51cu + (uint32_t)((int)puVar9))))));
        uVar13 = (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffb522u + (uint32_t)((int)puVar9))))));
        uVar18 = (uint)(*((ushort *)camry_host_ptr((uint32_t)((0xffffb51eu + (uint32_t)((int)puVar9))))));
        uVar12 = (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffb528u + (uint32_t)((int)puVar9))))));
        uVar17 = (uint)(*((ushort *)camry_host_ptr((uint32_t)((0xffffb524u + (uint32_t)((int)puVar9))))));
        uVar11 = (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffb52au + (uint32_t)((int)puVar9))))));
        uVar16 = (uint)(*((ushort *)camry_host_ptr((uint32_t)((0xffffb526u + (uint32_t)((int)puVar9))))));
        goto LAB_00037c18;
      }
      puVar19 = ((undefined *)camry_host_ptr(0x31a9cu));
    }
    uVar14 = *puVar19;
    uVar8 = (uint)(ushort)puVar19[1];
    uVar13 = puVar19[4];
    uVar18 = (uint)(ushort)puVar19[5];
    uVar12 = puVar19[2];
    uVar17 = (uint)(ushort)puVar19[3];
    uVar11 = puVar19[6];
    uVar16 = (uint)(ushort)puVar19[7];
  }
  else {
    uVar12 = 0;
    uVar11 = 0;
    uVar8 = (uint)DAT_00031ac2;
    uVar17 = 0;
    uVar16 = 0;
    uVar18 = (uint)DAT_00031ac6;
    uVar14 = DAT_00031ac0;
    uVar13 = DAT_00031ac4;
  }
LAB_00037c18:
  (*((short *)camry_host_ptr((uint32_t)((0xffffb4fcu + (uint32_t)((int)puVar9)))))) = (short)uVar8;
  (*((short *)camry_host_ptr((uint32_t)((0xffffb4feu + (uint32_t)((int)puVar9)))))) = (short)uVar18;
  (*((short *)camry_host_ptr((uint32_t)((0xffffb50cu + (uint32_t)((int)puVar9)))))) = (short)uVar17;
  (*((short *)camry_host_ptr((uint32_t)((0xffffb50eu + (uint32_t)((int)puVar9)))))) = (short)uVar16;
  (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffb504u + (uint32_t)((int)puVar9)))))) = uVar14;
  (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffb506u + (uint32_t)((int)puVar9)))))) = uVar13;
  (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffb514u + (uint32_t)((int)puVar9)))))) = uVar12;
  (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffb516u + (uint32_t)((int)puVar9)))))) = uVar11;
  (*((uint *)camry_host_ptr((uint32_t)((0xffffb53cu + (uint32_t)((int)puVar9)))))) = uVar8 * 0x69;
  (*((uint *)camry_host_ptr((uint32_t)((0xffffb540u + (uint32_t)((int)puVar9)))))) = uVar18 * 0x69;
  (*((uint *)camry_host_ptr((uint32_t)((0xffffb554u + (uint32_t)((int)puVar9)))))) = uVar17 * 0x69;
  (*((uint *)camry_host_ptr((uint32_t)((0xffffb558u + (uint32_t)((int)puVar9)))))) = uVar16 * 0x69;
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_37c48(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_37c4a(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_37de2(void)

{
  return;
}



/* Set selector6D6C=5A, adjacent byte6D6D=0 and counter6D6E=0. This initializes software offset
   alternation, not a PWM period or electrical phase. */

void f33_initialize_phase_offset_selector(void)

{
  DAT_febe6d6d = 0;
  f33_phase_offset_selector_counter = 0;
  f33_phase_offset_selector = 'Z';
  return;
}



/* Increment low16 counter; entry>=125 or increment reaching125 resets counter and toggles5A toA5,
   any other selector to5A. ROM31B18 then overrides to5A for33 orA5 for22; exact value11 leaves
   alternation enabled. No physical cadence inferred. */

void f33_advance_phase_offset_selector(void)

{
  uchar uVar1;
  
  if ((f33_phase_offset_selector_period <= f33_phase_offset_selector_counter) ||
     (f33_phase_offset_selector_counter = f33_phase_offset_selector_counter + 1,
     uVar1 = f33_phase_offset_selector,
     f33_phase_offset_selector_period <= f33_phase_offset_selector_counter)) {
    f33_phase_offset_selector_counter = 0;
    uVar1 = 'Z';
    if (f33_phase_offset_selector == 'Z') {
      uVar1 = 0xa5;
    }
  }
  if (f33_phase_offset_selector_override == '3') {
    uVar1 = 'Z';
  }
  else if (f33_phase_offset_selector_override == '\"') {
    uVar1 = 0xa5;
  }
  f33_phase_offset_selector = uVar1;
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_37e44(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_37e46(void)

{
  return;
}



/* Exclude bank0 for71EC.bit0 and bank1 forbit1, then form common/difference feedback. Preserve
   unsaturated32-bit second-axis sum6D78 separately from saturated6D72; the common regulator
   consumes6D78. Acquisition-status8B28&40004 takes the reset branch. Validity-masked
   common/difference feedback, including unsaturated32-bit second-axis sum6D78 and separate
   saturated mirror6D72. Reset follows8B28&40004; exact software dataflow, not acquisition validity.
    */

void f33_compose_current_feedback(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  
  if ((f33_output_request_status & 0x40004) != 0) {
    DAT_febe6d70 = 0;
    DAT_febe6d72 = 0;
    DAT_febe6d78 = 0;
    return;
  }
  iVar4 = DAT_febe6e2c;
  iVar1 = DAT_febe6e28;
  if ((DAT_febe71ec & 1) != 0) {
    iVar4 = 0;
    iVar1 = 0;
  }
  iVar2 = DAT_febe6e34;
  iVar5 = DAT_febe6e30;
  if ((DAT_febe71ec >> 1 & 1) != 0) {
    iVar2 = 0;
    iVar5 = 0;
  }
  iVar3 = iVar5 + iVar1;
  DAT_febe6d78 = iVar2 + iVar4;
  iVar1 = iVar1 - iVar5;
  iVar4 = iVar4 - iVar2;
  if (iVar3 + 0x7fff < 0 == (-1 < iVar3 && iVar3 + 0x7fff < 0) && iVar3 != -0x7fff) {
    if (iVar3 + -0x7fff < 0 == (iVar3 < 0 && -1 < iVar3 + -0x7fff) && iVar3 != 0x7fff) {
      iVar3 = 0x7fff;
    }
    DAT_febe6d70 = (undefined2)iVar3;
  }
  else {
    DAT_febe6d70 = 0x8001;
  }
  if (DAT_febe6d78 + 0x7fff < 0 == (-1 < DAT_febe6d78 && DAT_febe6d78 + 0x7fff < 0) &&
      DAT_febe6d78 != -0x7fff) {
    iVar5 = DAT_febe6d78;
    if (DAT_febe6d78 + -0x7fff < 0 == (DAT_febe6d78 < 0 && -1 < DAT_febe6d78 + -0x7fff) &&
        DAT_febe6d78 != 0x7fff) {
      iVar5 = 0x7fff;
    }
  }
  else {
    iVar5 = -0x7fff;
  }
  DAT_febe6d72 = (short)iVar5;
  if (iVar1 + 0x7fff < 0 == (-1 < iVar1 && iVar1 + 0x7fff < 0) && iVar1 != -0x7fff) {
    if (iVar1 + -0x7fff < 0 == (iVar1 < 0 && -1 < iVar1 + -0x7fff) && iVar1 != 0x7fff) {
      DAT_febe6d74 = 0x7fff;
    }
    else {
      DAT_febe6d74 = (undefined2)iVar1;
    }
  }
  else {
    DAT_febe6d74 = 0x8001;
  }
  if (iVar4 + 0x7fff < 0 == (-1 < iVar4 && iVar4 + 0x7fff < 0) && iVar4 != -0x7fff) {
    if (iVar4 + -0x7fff < 0 == (iVar4 < 0 && -1 < iVar4 + -0x7fff) && iVar4 != 0x7fff) {
      DAT_febe6d76 = 0x7fff;
    }
    else {
      DAT_febe6d76 = (undefined2)iVar4;
    }
  }
  else {
    DAT_febe6d76 = 0x8001;
  }
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_37f12(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_37f14(void)

{
  return;
}



/* Mirror actual main second/first commands6DD6/6DC8 to6D84/86. Add main corrections6DA8/6DA6 with
   symmetric signed16 saturation into common references6D7C/80. Differential references6D7E/82 add
   retained correction and ROM baseline without the same saturation. Feedback baseline6DCA is not
   the published first-axis command. */

void f33_publish_corrected_current_reference_pairs(void)

{
  int iVar1;
  int iVar2;
  
  DAT_febe6d84 = DAT_febe6dd6;
  DAT_febe6d86 = f33_actual_first_current_command;
  iVar2 = (int)DAT_febe6da6 + (int)f33_actual_first_current_command;
  iVar1 = (int)DAT_febe6da8 + (int)DAT_febe6dd6;
  if (iVar2 + 0x7fff < 0 == (-1 < iVar2 && iVar2 + 0x7fff < 0) && iVar2 != -0x7fff) {
    if (iVar2 + -0x7fff < 0 == (iVar2 < 0 && -1 < iVar2 + -0x7fff) && iVar2 != 0x7fff) {
      iVar2 = 0x7fff;
    }
    DAT_febe6d80 = (undefined2)iVar2;
  }
  else {
    DAT_febe6d80 = 0x8001;
  }
  if (iVar1 + 0x7fff < 0 == (-1 < iVar1 && iVar1 + 0x7fff < 0) && iVar1 != -0x7fff) {
    if (iVar1 + -0x7fff < 0 == (iVar1 < 0 && -1 < iVar1 + -0x7fff) && iVar1 != 0x7fff) {
      DAT_febe6d7c = 0x7fff;
    }
    else {
      DAT_febe6d7c = (undefined2)iVar1;
    }
  }
  else {
    DAT_febe6d7c = 0x8001;
  }
  DAT_febe6d82 = DAT_00031b2a + DAT_febe6daa;
  DAT_febe6d7e = DAT_00031b28 + DAT_febe6dac;
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_37f8e(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_37f90(void)

{
  return;
}



/* Read signed second-axis feedback mirror6D72; double when71EC&3, clamp to +/-32767, then return
   saturated absolute magnitude. This is measured-feedback-derived map input, not the sampled torque
   command. */

uint f33_current_reference_curve_feedback_magnitude(void)

{
  int iVar1;
  uint uVar2;
  
  iVar1 = (int)DAT_febe6d72;
  if ((DAT_febe71ec & 3) != 0) {
    iVar1 = iVar1 << 1;
  }
  if (iVar1 + -0x7fff < 0 == (iVar1 < 0 && -1 < iVar1 + -0x7fff)) {
    iVar1 = 0x7fff;
  }
  if (iVar1 + 0x7fff < 0 != (-1 < iVar1 && iVar1 + 0x7fff < 0)) {
    iVar1 = -0x7fff;
  }
  uVar2 = (uint)(short)iVar1;
  if ((int)(uVar2 + 0x7fff) < 0 == (-1 < (int)uVar2 && (int)(uVar2 + 0x7fff) < 0) &&
      uVar2 != 0xffff8001) {
    if ((int)uVar2 < 0) {
      return (int)(short)-(short)iVar1;
    }
    return uVar2;
  }
  return 0x7fff;
}


