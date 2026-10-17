#include "common.h"


uchar FUN_000b8040(uchar phase)

{
  undefined1 uVar1;
  uint32_t puVar2;
  puVar2 = 0xfebeb800u;
  uVar1 = DAT_febeb3d3;
  if (DAT_febeb405 == 'Z') {
    puVar2 = 0xfebeb800u;
    FUN_000b8886();
    f33_fill_constant_block_b7c42();
    f33_fill_constant_block_b7abe();
    uVar1 = 0x5a;
    phase = '\a';
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x42d))))) = uVar1;
  return phase;
}



uchar FUN_000b8070(uchar phase)

{
  if (5 < phase) {
    if (phase == '\x06') {
      f33_fill_constant_block_b7c42();
      f33_fill_constant_block_b7abe();
      phase = '\a';
    }
    else if (phase < 8) {
      phase = FUN_000b7ff4(phase);
    }
    else if (phase == '\b') {
      phase = FUN_000b8040('\b');
    }
  }
  return phase;
}



/* Dispatch the kind1 initial excursion phases and return the selected child phase in R10; not void.
   Phase number alone is not a completion indication. Dispatch low-byte excursion phase and forward
   selected child phase in R10. Nonvoid return is consumed by the engine; separate done/failed flags
   determine completion. */

uchar f33_advance_service_excursion_phase(uchar phase)

{
  uchar uVar1;
  
  switch(phase) {
  case '\x01':
    uVar1 = FUN_000b7dba(phase);
    break;
  case '\x02':
    uVar1 = FUN_000b7e44(phase);
    break;
  case '\x03':
    uVar1 = FUN_000b7eb2(phase);
    break;
  case '\x04':
    uVar1 = FUN_000b7edc(phase);
    break;
  case '\x05':
    uVar1 = FUN_000b7f8a(phase);
    break;
  default:
    uVar1 = FUN_000b8070(phase);
  }
  return uVar1;
}



void FUN_000b80e2(void)

{
  undefined4 uVar1;
  uchar phase;
  uint32_t puVar2;
  uchar uVar3;
  uchar uVar4;
  
  phase = DAT_febeb3cc;
  uVar1 = DAT_febeafe8;
  puVar2 = 0xfebeb800u;
  uVar3 = f33_qualify_service_progress(DAT_febeb3ca,DAT_febeb3dd);
  uVar4 = '\t';
  if (uVar3 != 'Z') {
    uVar4 = f33_advance_service_excursion_phase(phase);
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x434))))) = uVar4;
  (*((undefined4 *)camry_host_ptr((uint32_t)(puVar2 + -0x414)))) = uVar1;
  return;
}



undefined1 FUN_000b8116(undefined1 param_1)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  if (DAT_febeb3d4 == 'Z') {
    puVar1 = 0xfebeb800u;
    f33_fill_constant_block_b7c42();
    f33_fill_constant_block_b7abe();
    param_1 = 10;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x42c))))) = 0x5a;
  return param_1;
}



undefined1 FUN_000b813e(undefined1 param_1)

{
  uint32_t puVar1;
  int iVar2;
  
  puVar1 = 0xfebeb800u;
  iVar2 = FUN_000b7fb8(DAT_000af4b4,DAT_000af4a2);
  if (iVar2 == 0x5a) {
    f33_fill_constant_block_b7ad2();
    f33_fill_constant_block_b7c62();
    FUN_000b7966();
    param_1 = 0xb;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x425))))) = 0x5a;
  }
  return param_1;
}



void FUN_000b8196(void)

{
  undefined1 uVar1;
  uint32_t puVar2;
  uchar uVar3;
  undefined1 uVar4;
  
  uVar1 = DAT_febeb3cc;
  puVar2 = 0xfebeb800u;
  uVar3 = f33_qualify_service_progress(DAT_febeb3db,'\0');
  uVar4 = 0;
  if (uVar3 != 'Z') {
    uVar4 = FUN_000b8176(uVar1);
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x434))))) = uVar4;
  return;
}



undefined1 FUN_000b81c0(void)

{
  byte bVar1;
  byte bVar2;
  int iVar3;
  int iVar4;
  uint32_t puVar5;
  undefined1 uVar6;
  int iVar7;
  char cVar8;
  char cVar9;
  short sStack_1e;
  int iStack_1c;
  
  iVar3 = DAT_febeb3ec;
  bVar2 = DAT_febeb3da;
  bVar1 = DAT_febeb3d9;
  iVar4 = DAT_febeafe8;
  puVar5 = 0xfebeb800u;
  iVar7 = (int)DAT_febeb054;
  FUN_000d1178((int)DAT_febeafdc,&sStack_1e);
  FUN_000d1194(iVar4 - iVar3,&iStack_1c);
  iVar3 = (int)DAT_000af4a0;
  iVar4 = sStack_1e - iVar3;
  if ((iVar4 < 0 != (sStack_1e < 0 != iVar3 < 0 && iVar3 < 0 == iVar4 < 0)) &&
     (iStack_1c - DAT_000af4b0 < 0 !=
      (iStack_1c < 0 != DAT_000af4b0 < 0 && DAT_000af4b0 < 0 == iStack_1c - DAT_000af4b0 < 0))) {
    iVar4 = (int)DAT_000af4a8;
    if (iVar4 - iVar7 < 0 == (iVar4 < 0 != iVar7 < 0 && iVar7 < 0 == iVar4 - iVar7 < 0) &&
        iVar4 != iVar7) {
      cVar8 = '\0';
      uVar6 = DAT_000af496 <= bVar1;
      if ((bool)uVar6) {
        cVar9 = '\0';
      }
      else {
        cVar9 = bVar1 + 1;
      }
      goto LAB_000b8244;
    }
    iVar4 = (int)DAT_000af4a6;
    if (iVar7 - iVar4 < 0 == (iVar7 < 0 != iVar4 < 0 && iVar4 < 0 == iVar7 - iVar4 < 0) &&
        iVar7 != iVar4) {
      cVar9 = '\0';
      if (bVar2 < DAT_000af496) {
        uVar6 = 0;
        cVar8 = bVar2 + 1;
      }
      else {
        cVar8 = '\0';
        uVar6 = 2;
      }
      goto LAB_000b8244;
    }
  }
  cVar9 = '\0';
  cVar8 = '\0';
  uVar6 = 0;
LAB_000b8244:
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x427))))) = cVar9;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x426))))) = cVar8;
  return uVar6;
}



undefined1 FUN_000b8250(undefined1 param_1)

{
  char cVar1;
  char cVar2;
  uint uVar3;
  int iVar4;
  
  cVar2 = DAT_febeb3c9;
  cVar1 = DAT_febeb3c8;
  if ((DAT_febeb3c8 == 'Z') && (DAT_febeb3c9 == 'Z')) {
    uVar3 = f33_queue_service_center_and_check_geometry();
    if (uVar3 == 0x5a) {
      param_1 = 0x10;
    }
    else {
      FUN_000b7966();
      param_1 = 0xf;
    }
  }
  else {
    iVar4 = FUN_000b81c0();
    if ((iVar4 == 1) && (cVar1 != 'Z')) {
      param_1 = 0xd;
    }
    else if ((iVar4 == 2) && (cVar2 != 'Z')) {
      param_1 = 0xe;
    }
  }
  return param_1;
}



undefined1 FUN_000b82a8(undefined1 param_1)

{
  uint32_t puVar1;
  uchar uVar2;
  
  puVar1 = 0xfebeb800u;
  uVar2 = f33_update_service_minimum_excursion(DAT_000af496);
  if (uVar2 == 'Z') {
    param_1 = 0xc;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x428))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x428))))) | 1;
  }
  return param_1;
}



undefined1 FUN_000b82d6(undefined1 param_1)

{
  uint32_t puVar1;
  uchar uVar2;
  
  puVar1 = 0xfebeb800u;
  uVar2 = f33_update_service_maximum_excursion(DAT_000af496);
  if (uVar2 == 'Z') {
    param_1 = 0xc;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x428))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x428))))) | 2;
  }
  return param_1;
}



undefined1 FUN_000b8304(undefined1 param_1)

{
  uint32_t puVar1;
  int iVar2;
  
  puVar1 = 0xfebeb800u;
  iVar2 = FUN_000b7fb8(DAT_000af4bc,DAT_000af4aa);
  if (iVar2 == 0x5a) {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x42a))))) = 0x5a;
    param_1 = 0x10;
  }
  return param_1;
}



void FUN_000b8384(void)

{
  undefined4 uVar1;
  undefined1 uVar2;
  uint32_t puVar3;
  uchar uVar4;
  undefined1 uVar5;
  
  uVar2 = DAT_febeb3cc;
  uVar1 = DAT_febeafe8;
  puVar3 = 0xfebeb800u;
  uVar4 = f33_qualify_service_progress(DAT_febeb3d6,DAT_febeb3dc);
  uVar5 = 0x10;
  if (uVar4 != 'Z') {
    uVar5 = FUN_000b832e(uVar2);
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x434))))) = uVar5;
  (*((undefined4 *)camry_host_ptr((uint32_t)(puVar3 + -0x414)))) = uVar1;
  return;
}



void FUN_000b83ba(void)

{
  if (DAT_febeb3d5 != 0) {
    if (DAT_febeb3d5 == 1) {
      FUN_000b7c82();
      FUN_000b7cd0();
      FUN_000b80e2();
    }
    else if (DAT_febeb3d5 < 3) {
      FUN_000b7c82();
      FUN_000b7cd0();
      FUN_000b8196();
    }
    else if (DAT_febeb3d5 == 3) {
      FUN_000b8384();
    }
  }
  return;
}



void FUN_000b83f2(undefined1 param_1)

{
  DAT_febeb3d1 = param_1;
  return;
}



/* Initialize0520 engine kind1/2/3. Kind2 preserves extrema and selector106. Kinds1/3 reset extrema
   and immediately queue selector106=0. Set phase1, reset qualification and request masks.
   Initialize0520 kind1/2/3. Kind2 retains extrema/selector106; kinds1/3 reset extrema and
   queue106=0 immediately. Engine initialization is not a diagnostic success or physical convergence
   claim. */

void f33_initialize_service_engine(uchar kind)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  DAT_febeb3cc = 1;
  if (kind == '\x02') {
    DAT_febeb3db = 0;
  }
  else {
    DAT_febeb3c9 = 0;
    DAT_febeb3c8 = 0;
    DAT_febeb3e4 = 0x7fffffff;
    DAT_febeb3f0 = 0;
    DAT_febeb3e8 = 0x80000001;
    if (kind == '\x01') {
      DAT_febeb3ca = 0;
      DAT_febeb3db = 0;
    }
    else {
      DAT_febeb3d6 = 0;
      DAT_febeb3d8 = 0;
    }
    puVar1 = 0xfebeb800u;
    FUN_000b865e(0);
    FUN_000b79fa();
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x435))))) = 1;
  (*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + -0x414)))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x433))))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x432))))) = 0;
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x422)))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x431))))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x430))))) = 0;
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x420)))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x42d))))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x42c))))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x427))))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x426))))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x42b))))) = kind;
  FUN_000b42f0();
  f33_set_output_request_word('\0',0);
  f33_set_output_request_word('\x01',0);
  return;
}



undefined4 FUN_000b8474(void)

{
  char cVar1;
  int iVar2;
  undefined4 uVar3;
  int iVar4;
  short sStack_a;
  
  cVar1 = DAT_febeb3d2;
  FUN_000d1178((int)DAT_febeb054,&sStack_a);
  if (cVar1 == '\0') {
    iVar2 = (int)DAT_000af4ac;
    iVar4 = (int)sStack_a;
    if (iVar4 - iVar2 < 0 == (iVar4 < 0 != iVar2 < 0 && iVar2 < 0 == iVar4 - iVar2 < 0) &&
        iVar4 != iVar2) goto LAB_000b849c;
LAB_000b84ac:
    uVar3 = 0x5a;
  }
  else {
LAB_000b849c:
    if (cVar1 == 'Z') {
      iVar2 = (int)DAT_000af4ae;
      iVar4 = (int)sStack_a;
      if (iVar4 - iVar2 < 0 != (iVar4 < 0 != iVar2 < 0 && iVar2 < 0 == iVar4 - iVar2 < 0) ||
          iVar4 == iVar2) goto LAB_000b84ac;
    }
    uVar3 = 0;
  }
  return uVar3;
}



/* Return0/5A from exact raw-unit input/status/mode/limit gates. Kinds1/2 additionally apply B8474
   hysteresis. Diagnostic5062C passes kind1 in retained R6;5070A/507B2 pass2/3. No inferred physical
   stationary condition or engineering-unit interpretation. Raw input/status/mode/limit gates
   return0/5A; kinds1/2 additionally apply hysteresis. Kind1 arrives in retained R6 from
   diagnostic5062C. Internal application queue admission is weaker than this diagnostic
   precondition. */

uint f33_qualify_service_admission(uchar kind)

{
  ushort uVar1;
  char cVar2;
  ushort uVar3;
  short sVar4;
  ushort uVar5;
  char cVar6;
  uint uVar7;
  int iVar8;
  uint32_t puVar9;
  int iVar10;
  ushort uVar11;
  short sStack_26;
  
  cVar6 = DAT_febebef0;
  uVar5 = DAT_febebede;
  sVar4 = DAT_febeb38c;
  uVar3 = DAT_febeb080;
  cVar2 = DAT_febeb079;
  puVar9 = 0xfebeb800u;
  uVar11 = DAT_febeb11a & 0xff00;
  uVar1 = DAT_febeb082 & 0x81ff;
  FUN_000d1178((int)DAT_febeb054,&sStack_26);
  iVar10 = 0;
  uVar7 = 0;
  do {
    if (((*((ushort *)camry_host_ptr((uint32_t)(puVar9 + uVar7 * 2 + -0x7f0)))) < DAT_000af4a4) && (uVar7 != 5)) {
      iVar10 = 0x5a;
    }
    uVar7 = uVar7 + 1;
  } while (uVar7 < 10);
  if ((((((uVar3 < DAT_000af49a) || (DAT_000af49c < uVar5)) || (cVar6 != '\x11')) ||
       ((cVar2 != '\0' || (0x500 < uVar11)))) ||
      ((iVar10 == 0x5a || ((sVar4 != 0 || (uVar1 != 0)))))) ||
     (iVar8 = (int)DAT_000af49e, iVar10 = sStack_26 - iVar8,
     iVar10 < 0 == (sStack_26 < 0 != iVar8 < 0 && iVar8 < 0 == iVar10 < 0))) {
    uVar7 = 0;
  }
  else {
    uVar7 = 0x5a;
  }
  if ((kind == '\x01' || kind == '\x02') && (iVar10 = FUN_000b8474(), iVar10 == 0)) {
    uVar7 = 0;
  }
  return uVar7;
}



void FUN_000b856a(void)

{
  char cVar1;
  
  cVar1 = DAT_febeb1a4;
  DAT_febeb3cc = 0;
  DAT_febeb3d5 = 0;
  FUN_000b87d2();
  if (cVar1 == '\0') {
    f33_set_output_request_word('\0',0x70017001);
    f33_set_output_request_word('\x01',0x70017001);
    FUN_000b42fa();
  }
  return;
}



/* DirectbyteB3D2;B7CD0/B8474thresholdselection. */

void f33_set_service_qualification_mode(uchar mode)

{
  DAT_febeb3d2 = mode;
  return;
}



void FUN_000b85a8(undefined1 param_1)

{
  DAT_febeb3d7 = param_1;
  return;
}



/* Paired constant publisher: DAT_febeb3dc = 0x5a; and DAT_febeb3cb = 0;; shape-classified from the
   canonical corpus. Target cells not yet named. */

void FUN_000b85ae(void)

{
  DAT_febeb3dc = 0x5a;
  DAT_febeb3cb = 0;
  return;
}



/* Paired constant publisher: DAT_febeb3dd = 0x5a; and DAT_febeb3cb = 0;; shape-classified from the
   canonical corpus. Target cells not yet named. */

void FUN_000b85bc(void)

{
  DAT_febeb3dd = 0x5a;
  DAT_febeb3cb = 0;
  return;
}



/* Single constant publisher: DAT_febeb3dc = 0; Shape-classified from the canonical corpus; the
   target cell is not yet named, so the written state's meaning is unknown. */

void FUN_000b85ca(void)

{
  DAT_febeb3dc = 0;
  return;
}



/* Single constant publisher: DAT_febeb3dd = 0; Shape-classified from the canonical corpus; the
   target cell is not yet named, so the written state's meaning is unknown. */

void FUN_000b85d0(void)

{
  DAT_febeb3dd = 0;
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_b85d6(void)

{
  return;
}



void FUN_000b865e(undefined4 param_1)

{
  uint32_t puVar1;
  undefined4 local_c;
  undefined4 uStack_8;
  
  puVar1 = 0xfebeb800u;
  uStack_8 = 0;
  DAT_febeb3f8 = param_1;
  local_c = param_1;
  FUN_000ff09c(0x106,&local_c);
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x40c))))) = 5;
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_b8680(void)

{
  return;
}



void FUN_000b8682(void)

{
  DAT_febeb3fc = 0;
  DAT_febeb3fe = 0;
  DAT_febeb400 = 0;
  DAT_febeb3fd = 0;
  return;
}



/* WARNING: This is an inlined function */
/* Write the phase-selected signed halfword through R6; return0/5A enable in full R10. Real leaf
   preserves caller R19=0, used as the secondary publication flag. Phase-selected kind1 sample is
   written through R6; R10 returns0/5A. Real leaf preserves R19=0 used by caller secondary flag.
   P-code inlining preserves actual effects without a replacement callee. */

uint f33_select_service_kind1_sample(short *sample)

{
  short sVar1;
  uint uVar2;
  
  switch(DAT_febeb3cc) {
  case 2:
  case 4:
    uVar2 = 0x5a;
    sVar1 = DAT_febeb436;
    break;
  case 3:
    uVar2 = 0x5a;
    sVar1 = DAT_000af4c0;
    break;
  case 5:
    uVar2 = 0x5a;
    sVar1 = DAT_000af4c2;
    break;
  default:
    uVar2 = 0;
    sVar1 = 0;
    break;
  case 7:
    uVar2 = 0x5a;
    sVar1 = DAT_febeb3a6;
    break;
  case 8:
    uVar2 = 0x5a;
    sVar1 = DAT_febeb406;
  }
  *sample = sVar1;
  return uVar2;
}



/* WARNING: This is an inlined function */
/* Phase0A selects B3A6 and returns5A; otherwise write zero and return0. R6 is a real output
   pointer. Phase0A writes B3A6 through R6 and returns5A; other phases write zero and return0.
   Preserve real pointer output and caller R19 rather than false no-argument recovery. */

uint f33_select_service_kind2_sample(short *sample)

{
  short sVar1;
  uint uVar2;
  
  if (DAT_febeb3cc == '\n') {
    uVar2 = 0x5a;
    sVar1 = DAT_febeb3a6;
  }
  else {
    uVar2 = 0;
    sVar1 = 0;
  }
  *sample = sVar1;
  return uVar2;
}



/* WARNING: This is an inlined function */
/* Select AC56 or directed ROM samples in phases0C..0F; write through R6 and return0/5A. Kind3
   phases0C/0F select AC56;0D/0E select directed ROM samples. Write signed-halfword bits through R6
   and return0/5A enable. */

uint f33_select_service_kind3_sample(short *sample)

{
  short sVar1;
  uint uVar2;
  
  switch(DAT_febeb3cc) {
  case 0xc:
  case 0xf:
    uVar2 = 0x5a;
    sVar1 = DAT_febeac56;
    break;
  case 0xd:
    uVar2 = 0x5a;
    sVar1 = DAT_000af4c4;
    break;
  case 0xe:
    uVar2 = 0x5a;
    sVar1 = DAT_000af4c6;
    break;
  default:
    uVar2 = 0;
    sVar1 = 0;
  }
  *sample = sVar1;
  return uVar2;
}



uint FUN_000b8742(char param_1)

{
  uint uVar1;
  uint uVar2;
  
  if (param_1 != 'Z') {
    return 0;
  }
  uVar2 = 0x569a;
  uVar1 = 0;
  do {
    if ((int)((ushort)(*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebebd34u + (uint32_t)(uVar1) * 2u)))) - uVar2) < 0) {
      uVar2 = (uint)(ushort)(*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebebd34u + (uint32_t)(uVar1) * 2u))));
    }
    do {
      uVar1 = uVar1 + 1 & 0xff;
      if (9 < uVar1) {
        return uVar2;
      }
    } while (uVar1 == 5);
  } while( true );
}



/* WARNING: Inlined function: f33_select_service_kind3_sample */
/* WARNING: Inlined function: f33_select_service_kind2_sample */
/* WARNING: Inlined function: f33_select_service_kind1_sample */
/* Select sample by engine kind, derive bound, publish B3FC enable/B3FD secondary flag/B3FE
   sample/B400 bound. BF33E snapshots these for family0500 motor substitution. No physical actuation
   claim. Compose selected engine sample, enable and bound into B3FC..B400 for later BF33E snapshot.
   Kinds1/2 preserve zero secondary flag through real leaf effects. Snapshot and motor-family
   qualification are separate stages. */

void f33_publish_service_engine_substitution(void)

{
  uint32_t puVar1;
  undefined2 uVar2;
  undefined1 uVar3;
  char cVar4;
  undefined2 local_e;
  
  puVar1 = 0xfebeb800u;
  if (DAT_febeb3d5 == 0) {
LAB_000b8792:
    local_e = 0;
    cVar4 = '\0';
  }
  else {
    local_e = DAT_febeb3a6;
    if (DAT_febeb3d5 == 1) {
      switch(DAT_febeb3cc) {
      case '\x02':
      case '\x04':
        cVar4 = 'Z';
        local_e = DAT_febeb436;
        break;
      case '\x03':
        cVar4 = 'Z';
        local_e = DAT_000af4c0;
        break;
      case '\x05':
        cVar4 = 'Z';
        local_e = DAT_000af4c2;
        break;
      default:
        cVar4 = '\0';
        local_e = 0;
        break;
      case '\a':
        cVar4 = 'Z';
        break;
      case '\b':
        cVar4 = 'Z';
        local_e = DAT_febeb406;
      }
    }
    else {
      if (2 < DAT_febeb3d5) {
        if (DAT_febeb3d5 == 3) {
          switch(DAT_febeb3cc) {
          case '\f':
          case '\x0f':
            cVar4 = 'Z';
            local_e = DAT_febeac56;
            break;
          case '\r':
            cVar4 = 'Z';
            local_e = DAT_000af4c4;
            break;
          case '\x0e':
            cVar4 = 'Z';
            local_e = DAT_000af4c6;
            break;
          default:
            cVar4 = '\0';
            local_e = 0;
          }
          if (cVar4 == 'Z') {
            uVar3 = 0x5a;
          }
          else {
            uVar3 = 0;
          }
          goto LAB_000b87b8;
        }
        goto LAB_000b8792;
      }
      if (DAT_febeb3cc == '\n') {
        cVar4 = 'Z';
      }
      else {
        cVar4 = '\0';
        local_e = 0;
      }
    }
  }
  uVar3 = 0;
LAB_000b87b8:
  uVar2 = FUN_000b8742(cVar4);
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x400)))) = uVar2;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x404))))) = cVar4;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x403))))) = uVar3;
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x402)))) = local_e;
  return;
}



void FUN_000b87d2(void)

{
  DAT_febeb3fc = 0;
  DAT_febeb3fe = 0;
  DAT_febeb400 = 0;
  DAT_febeb3fd = 0;
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_b87e0(void)

{
  return;
}



/* Constant-block fill: 5 literal assignments into one contiguous cell block; shape-verified.
   Literals are default/reset values; cell meanings are not recovered. */

void f33_fill_constant_block_b87e2(void)

{
  DAT_febeb406 = 0;
  DAT_febeb408 = 0;
  DAT_febeb40a = 0;
  DAT_febeb404 = 0;
  DAT_febeb405 = 0;
  return;
}



/* WARNING: Removing unreachable block (ram,0x000b8828) */

void FUN_000b87f2(void)

{
  int iVar1;
  uint32_t puVar2;
  char cVar3;
  ushort uVar4;
  short sVar5;
  short sStack_12;
  
  uVar4 = DAT_febeb40a;
  sVar5 = DAT_febeb408;
  cVar3 = DAT_febeb405;
  puVar2 = 0xfebeb800u;
  if (DAT_febeb405 == '\0') {
    puVar2 = 0xfebeb800u;
    FUN_000d22c0(((undefined *)camry_host_ptr(0xaf4ccu)),DAT_febeb408,&sStack_12);
    iVar1 = (int)((uint)DAT_000af4ca * (int)sStack_12) / 0x4000;
    if (sVar5 != -1) {
      sVar5 = sVar5 + 1;
    }
    if (iVar1 == 0) {
      if (uVar4 < DAT_000af4c8) {
        uVar4 = uVar4 + 1;
      }
      else {
        cVar3 = 'Z';
      }
    }
  }
  else {
    iVar1 = 0;
  }
  (*((short *)camry_host_ptr((uint32_t)(puVar2 + -0x3fa)))) = (short)iVar1;
  (*((short *)camry_host_ptr((uint32_t)(puVar2 + -0x3f8)))) = sVar5;
  (*((ushort *)camry_host_ptr((uint32_t)(puVar2 + -0x3f6)))) = uVar4;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x3fb))))) = cVar3;
  return;
}



void FUN_000b885c(void)

{
  if (DAT_febeb404 == 'Z') {
    FUN_000b87f2();
  }
  return;
}



/* Constant-block fill: 5 literal assignments into one contiguous cell block; shape-verified.
   Literals are default/reset values; cell meanings are not recovered. */

void f33_fill_constant_block_b8872(void)

{
  DAT_febeb406 = 0;
  DAT_febeb408 = 0;
  DAT_febeb40a = 0;
  DAT_febeb405 = 0;
  DAT_febeb404 = 0x5a;
  return;
}



void FUN_000b8886(void)

{
  DAT_febeb404 = 0;
  DAT_febeb406 = 0;
  DAT_febeb408 = 0;
  DAT_febeb40a = 0;
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_b8894(void)

{
  return;
}



/* Constant-block fill: 11 literal assignments into one contiguous cell block; shape-verified.
   Literals are default/reset values; cell meanings are not recovered. */

void f33_fill_constant_block_b8896(void)

{
  DAT_febeb40c = 0;
  DAT_febeb41c = 0;
  DAT_febeb420 = 0;
  DAT_febeb40e = 0;
  DAT_febeb424 = 0;
  DAT_febeb416 = 0;
  DAT_febeb410 = 0;
  DAT_febeb428 = 0;
  DAT_febeb412 = 0;
  DAT_febeb414 = 0;
  DAT_febeb42c = 0;
  return;
}



/* WARNING: Removing unreachable block (ram,0x000b89c2) */
/* WARNING: Removing unreachable block (ram,0x000b8936) */

int FUN_000b88b2(int param_1,int param_2)

{
  char cVar1;
  short sVar2;
  int iVar3;
  int iVar4;
  uint32_t puVar5;
  int iVar6;
  int iVar7;
  int local_2c;
  int iStack_28;
  int iStack_24;
  int iStack_20;
  int iStack_1c;
  
  sVar2 = DAT_febeb40e;
  puVar5 = 0xfebeb800u;
  iVar4 = -param_2;
  if ((DAT_febeb3cc == '\x02') || (DAT_febeb41c = 0, iVar4 = param_2, DAT_febeb3cc == '\x04')) {
    DAT_febeb41c = iVar4 - param_1;
  }
  iVar6 = (int)DAT_febeb40e;
  iVar4 = (DAT_febeb41c - DAT_febeb424) + DAT_febeb420;
  iVar3 = (int)DAT_000af54c;
  iVar7 = iVar4;
  if (iVar3 != 0) {
    if (iVar4 == -0x80000000 && iVar3 == -1) {
      iVar7 = -0x80000000;
    }
    else {
      iVar7 = iVar4 / iVar3;
    }
  }
  FUN_000d1cf6(iVar7,0x7fff,0xffff8001,&local_2c);
  iStack_24 = (*((int *)camry_host_ptr((uint32_t)(puVar5 + -0x3d8))));
  (*((short *)camry_host_ptr((uint32_t)(puVar5 + -0x3ea)))) = sVar2;
  (*((int *)camry_host_ptr((uint32_t)(puVar5 + -0x3e0)))) = iVar4;
  (*((short *)camry_host_ptr((uint32_t)(puVar5 + -0x3f2)))) = (short)local_2c;
  iVar4 = (int)DAT_000af54e;
  (*((int *)camry_host_ptr((uint32_t)(puVar5 + -0x3dc)))) = iVar7;
  cVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x7fc)))));
  iStack_28 = ((iVar6 + local_2c) * iVar4) / 0x80;
  FUN_000d1cf6(iStack_28,0x7fff,0xffff8001,&iStack_28);
  if (((cVar1 != '\x02') || (iStack_28 < 0)) && ((cVar1 != '\x01' || (-1 < iStack_28)))) {
    iStack_24 = iStack_24 + iStack_28;
  }
  FUN_000d1cf6(iStack_24,PTR_LAB_000af554,-(int)PTR_LAB_000af554,&iStack_24);
  (*((short *)camry_host_ptr((uint32_t)(puVar5 + -0x3f0)))) = (short)iStack_28;
  (*((int *)camry_host_ptr((uint32_t)(puVar5 + -0x3d8)))) = iStack_24;
  iStack_20 = local_2c * DAT_000af550;
  FUN_000d1cf6(iStack_20,0x7fff,0xffff8001,&iStack_20);
  (*((short *)camry_host_ptr((uint32_t)(puVar5 + -0x3ee)))) = (short)iStack_20;
  iStack_1c = (param_2 * DAT_000af552) / 0x80;
  FUN_000d1cf6(iStack_1c,0x7fff,0xffff8001,&iStack_1c);
  (*((short *)camry_host_ptr((uint32_t)(puVar5 + -0x3ec)))) = (short)iStack_1c;
  return iStack_24 + iStack_20 + iStack_1c;
}



/* WARNING: Removing unreachable block (ram,0x000b8a00) */

void FUN_000b89e0(void)

{
  uint32_t puVar1;
  undefined4 uVar2;
  
  puVar1 = 0xfebeb800u;
  if (DAT_febeb40c == 'Z') {
    uVar2 = FUN_000b88b2((DAT_febeb032 * 10) / 8,(uint)DAT_febeb418 * 10);
    (*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + -0x3d4)))) = uVar2;
  }
  return;
}



/* Constant-block fill: 11 literal assignments into one contiguous cell block; shape-verified.
   Literals are default/reset values; cell meanings are not recovered. */

void f33_fill_constant_block_b8a10(void)

{
  DAT_febeb41c = 0;
  DAT_febeb420 = 0;
  DAT_febeb40e = 0;
  DAT_febeb424 = 0;
  DAT_febeb416 = 0;
  DAT_febeb410 = 0;
  DAT_febeb428 = 0;
  DAT_febeb412 = 0;
  DAT_febeb414 = 0;
  DAT_febeb42c = 0;
  DAT_febeb40c = 0x5a;
  return;
}



/* Constant-block fill: 11 literal assignments into one contiguous cell block; shape-verified.
   Literals are default/reset values; cell meanings are not recovered. */

void f33_fill_constant_block_b8a30(void)

{
  DAT_febeb40c = 0;
  DAT_febeb41c = 0;
  DAT_febeb420 = 0;
  DAT_febeb40e = 0;
  DAT_febeb424 = 0;
  DAT_febeb416 = 0;
  DAT_febeb410 = 0;
  DAT_febeb428 = 0;
  DAT_febeb412 = 0;
  DAT_febeb414 = 0;
  DAT_febeb42c = 0;
  return;
}



/* Directu16storeB418,consumedB89E0 onlywhenB40C5A. */

void f33_set_service_numeric_target(ushort target)

{
  DAT_febeb418 = target;
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_b8a52(void)

{
  return;
}



/* Constant-block fill: 5 literal assignments into one contiguous cell block; shape-verified.
   Literals are default/reset values; cell meanings are not recovered. */

void f33_fill_constant_block_b8a54(void)

{
  DAT_febeb431 = 0;
  DAT_febeb432 = 0;
  DAT_febeb434 = 0;
  DAT_febeb436 = 0;
  DAT_febeb430 = 0;
  return;
}



/* WARNING: Removing unreachable block (ram,0x000b8ab4) */
/* WARNING: Removing unreachable block (ram,0x000b8a86) */

void FUN_000b8a64(void)

{
  bool bVar1;
  int iVar2;
  undefined1 uVar3;
  int iVar4;
  uint32_t puVar5;
  short sVar6;
  int local_14;
  int iStack_10;
  int iVar7;
  
  iVar2 = DAT_febeb42c;
  puVar5 = 0xfebeb800u;
  local_14 = (DAT_febeac70 * 10) / 8;
  FUN_000d1cf6(local_14,(int)DAT_000af55c,-(int)DAT_000af55c,&local_14);
  iVar4 = (int)DAT_000af558;
  (*((short *)camry_host_ptr((uint32_t)(puVar5 + -0x3ce)))) = (short)local_14;
  iStack_10 = -(local_14 * iVar4) / 0x40;
  FUN_000d1cf6(iStack_10,0x7fff,0xffff8001,&iStack_10);
  sVar6 = DAT_000af55a;
  iVar4 = (int)DAT_000af55a;
  (*((short *)camry_host_ptr((uint32_t)(puVar5 + -0x3cc)))) = (short)iStack_10;
  iVar2 = iVar2 + iStack_10;
  if (iVar2 - iVar4 < 0 == (iVar2 < 0 != iVar4 < 0 && iVar4 < 0 == iVar2 - iVar4 < 0) &&
      iVar2 != iVar4) {
    uVar3 = 2;
  }
  else {
    iVar7 = -iVar4;
    iVar4 = iVar2 + iVar4;
    bVar1 = iVar2 < 0 != iVar7 < 0 && iVar7 < 0 == iVar4 < 0;
    if (iVar4 < 0 == bVar1) {
      iVar7 = iVar2;
    }
    sVar6 = (short)iVar7;
    uVar3 = iVar4 < 0 != bVar1;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x3d0))))) = uVar3;
  (*((short *)camry_host_ptr((uint32_t)(puVar5 + -0x3ca)))) = sVar6;
  return;
}



void FUN_000b8af0(void)

{
  if ((DAT_febeb431 == 'Z') && (DAT_febeed00 == 'Z')) {
    FUN_000b8a64();
  }
  return;
}



/* Constant-block fill: 5 literal assignments into one contiguous cell block; shape-verified.
   Literals are default/reset values; cell meanings are not recovered. */

void f33_fill_constant_block_b8b10(void)

{
  DAT_febeb432 = 0;
  DAT_febeb434 = 0;
  DAT_febeb436 = 0;
  DAT_febeb430 = 0;
  DAT_febeb431 = 0x5a;
  return;
}



/* Constant-block fill: 5 literal assignments into one contiguous cell block; shape-verified.
   Literals are default/reset values; cell meanings are not recovered. */

void f33_fill_constant_block_b8b24(void)

{
  DAT_febeb431 = 0;
  DAT_febeb432 = 0;
  DAT_febeb434 = 0;
  DAT_febeb436 = 0;
  DAT_febeb430 = 0;
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_b8b34(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_b8b36(void)

{
  return;
}



/* B438=11waitsfive88xxstatuses;all8822success,otherterminalfail;selector4. */

void f33_monitor_routine_1007_lifecycle_group(void)

{
  ushort uVar1;
  
  uVar1 = DAT_febeb440;
  if (DAT_febeb438 == '\x11') {
    if (((((int)(uint)DAT_febeb2d4 >> 8 == 0x88) && ((int)(uint)DAT_febeb26c >> 8 == 0x88)) &&
        ((int)(uint)DAT_febeb324 >> 8 == 0x88)) &&
       (((int)(uint)DAT_febeb490 >> 8 == 0x88 && ((int)(uint)DAT_febeb352 >> 8 == 0x88)))) {
      if (((((DAT_febeb2d4 & 0xff) == 0x22) && ((DAT_febeb26c & 0xff) == 0x22)) &&
          ((DAT_febeb324 & 0xff) == 0x22)) &&
         (((DAT_febeb490 & 0xff) == 0x22 && ((DAT_febeb352 & 0xff) == 0x22)))) {
        ((void)(4), (void)(0), thunk_FUN_0004d0a4());
        DAT_febeb438 = '\"';
        DAT_febeb43c = 0;
      }
      else {
        ((void)(4), (void)(0x20), thunk_FUN_0004d0a4());
        DAT_febeb438 = 'D';
        DAT_febeb43c = 0;
      }
    }
    else if ((DAT_febeb440 < DAT_000aed64) && ((DAT_febeb20e != '\x11' && (DAT_febeb20e != '3')))) {
      uVar1 = DAT_febeb440 + 1;
    }
    else {
      DAT_febeb43c = 0x5a;
      uVar1 = DAT_000aed64;
    }
  }
  else {
    DAT_febeb43c = 0;
  }
  DAT_febeb440 = uVar1;
  return;
}



void FUN_000b8c16(void)

{
  if (DAT_febeb439 == '\x11') {
    if (((((int)(uint)DAT_febeb26c >> 8 == 0x88) && ((int)(uint)DAT_febeb324 >> 8 == 0x88)) &&
        ((int)(uint)DAT_febeb490 >> 8 == 0x88)) && ((int)(uint)DAT_febeb352 >> 8 == 0x88)) {
      DAT_febeb43b = 0;
      DAT_febeb439 = (char)DAT_febeb352;
      if ((((DAT_febeb26c & 0xff) != 0x22) || ((DAT_febeb324 & 0xff) != 0x22)) ||
         (((DAT_febeb490 & 0xff) != 0x22 || ((DAT_febeb352 & 0xff) != 0x22)))) {
        DAT_febeb439 = 'D';
      }
    }
    else if (((DAT_febeb43e < DAT_000aed64) && (DAT_febeb20e != '\x11')) && (DAT_febeb20e != '3')) {
      DAT_febeb43e = DAT_febeb43e + 1;
    }
    else {
      DAT_febeb43b = 0x5a;
      DAT_febeb43e = DAT_000aed64;
    }
  }
  else {
    DAT_febeb43b = 0;
  }
  return;
}



void FUN_000b8cbe(void)

{
  f33_monitor_routine_1007_lifecycle_group();
  FUN_000b8c16();
  return;
}



/* B43A=11waitsfivegroupbytes;all22success,othernon11terminalfail;selector5. */

void f33_monitor_routine_1008_lifecycle_group(void)

{
  ushort uVar1;
  
  uVar1 = DAT_febeb442;
  if (DAT_febeb43a == '\x11') {
    if ((((DAT_febeb2ce == '\x11') || (DAT_febeb25c == '\x11')) || (DAT_febeb302 == '\x11')) ||
       ((DAT_febeb462 == '\x11' || (DAT_febeb334 == '\x11')))) {
      if ((DAT_febeb442 < (ushort)PTR_LAB_000aed66) &&
         ((DAT_febeb20e != '\x11' && (DAT_febeb20e != '3')))) {
        uVar1 = DAT_febeb442 + 1;
      }
      else {
        DAT_febeb43d = 0x5a;
        uVar1 = (ushort)PTR_LAB_000aed66;
      }
    }
    else if ((((DAT_febeb2ce == '\"') && (DAT_febeb25c == '\"')) && (DAT_febeb302 == '\"')) &&
            ((DAT_febeb462 == '\"' && (DAT_febeb334 == '\"')))) {
      ((void)(5), (void)(0), thunk_FUN_0004d0a4());
      DAT_febeb43a = '\"';
      DAT_febeb43d = 0;
    }
    else {
      ((void)(5), (void)(0x20), thunk_FUN_0004d0a4());
      DAT_febeb43a = 'D';
      DAT_febeb43d = 0;
    }
  }
  else {
    DAT_febeb43d = 0;
  }
  DAT_febeb442 = uVar1;
  return;
}



void FUN_000b8d8c(void)

{
  FUN_000b8cbe();
  f33_monitor_routine_1008_lifecycle_group();
  return;
}



undefined4 FUN_000b8d9c(char param_1)

{
  char cVar1;
  char cVar2;
  
  cVar1 = DAT_febeb43a;
  cVar2 = DAT_febeb439;
  if ((((param_1 == '\0') || (cVar2 = DAT_febeb438, param_1 == '\x01')) ||
      (cVar1 = DAT_febeb439, param_1 == '\x02')) && ((cVar2 != '\x11' && (cVar1 != '\x11')))) {
    return 0x5a;
  }
  return 0;
}



void FUN_000b8dda(char param_1)

{
  undefined2 uVar1;
  undefined2 uVar2;
  char cVar3;
  char cVar4;
  
  uVar2 = DAT_febeb440;
  uVar1 = DAT_febeb43e;
  cVar3 = DAT_febeb439;
  cVar4 = DAT_febeb438;
  if (param_1 == '\0') {
    if (DAT_febeb438 != '\x11') {
      FUN_000b6944();
      if (cVar3 != '\x11') {
        FUN_000b5eda();
        FUN_000b726c();
        FUN_000b8fd0();
        f33_fill_constant_block_b7358();
      }
      cVar4 = '\x11';
      uVar2 = 0;
    }
  }
  else if ((param_1 == '\x01') && (DAT_febeb439 != '\x11')) {
    if (DAT_febeb438 != '\x11') {
      FUN_000b5eda();
      FUN_000b726c();
      FUN_000b8fd0();
      f33_fill_constant_block_b7358();
    }
    cVar3 = '\x11';
    uVar1 = 0;
  }
  DAT_febeb438 = cVar4;
  DAT_febeb439 = cVar3;
  DAT_febeb440 = uVar2;
  DAT_febeb43e = uVar1;
  return;
}



void FUN_000b8e52(void)

{
  undefined2 uVar1;
  uint32_t puVar2;
  puVar2 = 0xfebeb800u;
  uVar1 = DAT_febeb442;
  if (DAT_febeb43a != '\x11') {
    puVar2 = 0xfebeb800u;
    FUN_000b69de();
    FUN_000b5f00();
    FUN_000b6be6();
    FUN_000b8ef0();
    FUN_000b72ec();
    uVar1 = 0;
  }
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar2 + -0x3be)))) = uVar1;
  DAT_febeb43a = 0x11;
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_b8e8c(void)

{
  return;
}



/* Paired constant publisher: DAT_febeb446 = 1; and DAT_febeb44c = 1;; shape-classified from the
   canonical corpus. Target cells not yet named. */

void FUN_000b8e8e(void)

{
  DAT_febeb446 = 1;
  DAT_febeb44c = 1;
  return;
}



void FUN_000b8e9a(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  FUN_000b8e8e();
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x3bc))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x387b)))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x3b6))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x382f)))));
  return;
}



/* Far-call trampoline: prepare {lp},0 / jarl 0xB8E8E / dispose 0,{lp},lp; byte-verified against the
   exact image. Forwards with registers and stack unchanged; marked as a thunk. Forwarding shape
   machine-verified; target semantics not recovered. */

void thunk_FUN_000b8e8e(void)

{
  FUN_000b8e8e();
  return;
}



/* Single constant publisher: DAT_febeb462 = 0; Shape-classified from the canonical corpus; the
   target cell is not yet named, so the written state's meaning is unknown. */

void FUN_000b8ec2(void)

{
  DAT_febeb462 = 0;
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_b8ec8(void)

{
  return;
}



/* Constant-block fill: 6 literal assignments into one contiguous cell block; shape-verified.
   Literals are default/reset values; cell meanings are not recovered. */

void f33_fill_constant_block_b8eca(void)

{
  DAT_febeb45f = 0x11;
  DAT_febeb461 = 2;
  DAT_febeb45c = 0;
  DAT_febeb45d = 0;
  DAT_febeb45e = 0;
  DAT_febeb460 = 0;
  return;
}



void FUN_000b8ef0(void)

{
  DAT_febeb461 = 2;
  DAT_febeb45c = 0;
  DAT_febeb462 = 0x22;
  return;
}



/* Constant-block fill: 6 literal assignments into one contiguous cell block; shape-verified.
   Literals are default/reset values; cell meanings are not recovered. */

void f33_fill_constant_block_b8f16(void)

{
  DAT_febeb46c = 0x55aaaa55;
  DAT_febeb467 = 0;
  DAT_febeb464 = 0;
  DAT_febeb465 = 0;
  DAT_febeb466 = 0;
  DAT_febeb468 = 0;
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_b8f3a(void)

{
  return;
}



void FUN_000b8f4a(void)

{
  DAT_febeb474 = 0x55aaaa55;
  DAT_febeb478 = 0x55aaaa55;
  f33_report_diagnostic_healthy_observed(299);
  return;
}



void FUN_000b8f74(void)

{
  FUN_000b8f4a();
  f33_report_diagnostic_event_pass(0x20);
  f33_report_diagnostic_event_pass(0x120);
  return;
}



/* Far-call trampoline: prepare {lp},0 / jarl 0xB8F4A / dispose 0,{lp},lp; byte-verified against the
   exact image. Forwards with registers and stack unchanged; marked as a thunk. Forwarding shape
   machine-verified; target semantics not recovered. */

void thunk_FUN_000b8f4a(void)

{
  FUN_000b8f4a();
  return;
}



/* Single constant publisher: DAT_febeb471 = 0x44; Shape-classified from the canonical corpus; the
   target cell is not yet named, so the written state's meaning is unknown. */

void FUN_000b8fa8(void)

{
  DAT_febeb471 = 0x44;
  return;
}



/* B47244,B480/B484=pair,r10=0. No recoveredreader ofstagedpair;NOTliveB474/B478. */

uint f33_stage_encoded_mode_pair(uint first,uint second)

{
  DAT_febeb472 = 0x44;
  DAT_febeb480 = first;
  DAT_febeb484 = second;
  return 0;
}



/* Single constant publisher: DAT_febeb490 = 0; Shape-classified from the canonical corpus; the
   target cell is not yet named, so the written state's meaning is unknown. */

void FUN_000b8fc6(void)

{
  DAT_febeb490 = 0;
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_b8fcc(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_b8fce(void)

{
  return;
}



void FUN_000b8fd0(void)

{
  DAT_febeb490 = 0x8822;
  DAT_febeb48c = 0;
  DAT_febeb48d = 0;
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_b8fe0(void)

{
  return;
}



void FUN_000b8fe2(void)

{
  DAT_febeb494 = 0;
  DAT_febeb495 = 0;
  DAT_febeb496 = 0;
  return;
}



void FUN_000b8fee(char param_1)

{
  uint32_t puVar1;
  undefined4 uVar2;
  undefined4 uVar3;
  undefined1 uVar4;
  byte bVar5;
  uint uVar6;
  
  bVar5 = DAT_febeb496;
  uVar4 = DAT_febeb495;
  puVar1 = 0xfebeb800u;
  uVar6 = (uint)DAT_febeb496;
  if (param_1 == '\x11') {
    uVar2 = 0;
    uVar3 = 0;
    if (DAT_febeb1a4 == '\0') {
      if (DAT_febef210 == -0x5aa5a55b) {
        puVar1 = 0xfebeb800u;
        FUN_000b15ac(6);
      }
    }
    else {
      puVar1 = 0xfebeb800u;
      FUN_000b15ac(0xb);
      f33_latch_health_command_completion();
    }
  }
  else {
    uVar2 = 0x20;
    uVar3 = 0xfffffff7;
  }
  if ((bVar5 & 1) != 0) {
    ((void)(0xb), (void)(uVar2), thunk_FUN_0004d0a4());
    uVar4 = 0;
    uVar6 = (uint)(bVar5 >> 1) << 1;
  }
  bVar5 = (byte)uVar6;
  if ((uVar6 >> 1 & 1) != 0) {
    ((void)(0), (void)(uVar3), thunk_FUN_00034ea4());
    bVar5 = bVar5 & 0xfd;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x36c))))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x36b))))) = uVar4;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x36a))))) = bVar5;
  return;
}



/* B494/B495requestflags,publishedF011/F00Fstates;callsB8FEE11successor22fail;selectorBrequesterbit1handledthere.
    */

void f33_monitor_pending_learned_record_updates(void)

{
  undefined4 uVar1;
  bool bVar2;
  
  if (DAT_febeb494 == 'Z') {
    if (DAT_febeb495 == 'Z') {
      if ((DAT_febef011 != 'D') || (DAT_febef00f != 'D')) {
        if (DAT_febef011 == '\0') {
          return;
        }
        goto LAB_000b90b8;
      }
    }
    else if (DAT_febef011 != 'D') {
      bVar2 = DAT_febef011 == '\0';
      goto LAB_000b90bc;
    }
  }
  else {
    if (DAT_febeb495 != 'Z') {
      return;
    }
    if (DAT_febef00f != 'D') {
LAB_000b90b8:
      bVar2 = DAT_febef00f == '\x11';
LAB_000b90bc:
      if (bVar2) {
        return;
      }
      uVar1 = 0x22;
      goto LAB_000b90c2;
    }
  }
  uVar1 = 0x11;
LAB_000b90c2:
  FUN_000b8fee(uVar1);
  return;
}



undefined4 FUN_000b90ca(uint param_1,byte param_2)

{
  int iVar1;
  undefined *puVar2;
  int iVar4;
  char cVar5;
  undefined4 uVar6;
  char cVar7;
  byte bVar8;
  uint32_t puVar3;
  iVar1 = DAT_febef208;
  bVar8 = DAT_febeb496;
  cVar7 = DAT_febeb495;
  puVar3 = 0xfebeb800u;
  puVar2 = ((undefined *)camry_host_ptr(0xfebeb800u));
  iVar4 = 0;
  cVar5 = DAT_febeb494;
  if (((DAT_febeb11a & 0xff00) == 0x100) || ((DAT_febeb11a & 0xff00) == 0x900)) {
    uVar6 = 0xfffffffa;
    goto LAB_000b917c;
  }
  if (DAT_febeb495 == 'Z') {
    if (DAT_febef00f == 'D') {
      uVar6 = 0;
      cVar7 = '\0';
      goto LAB_000b917c;
    }
    uVar6 = 0xffffffff;
    if (DAT_febef00f == '\x11') goto LAB_000b917c;
    uVar6 = 0xfffffff7;
    cVar7 = '\0';
    puVar2 = ((undefined *)camry_host_ptr(0xfebeb800u));
LAB_000b916e:
    if (iVar4 != 0x5a) goto LAB_000b917c;
  }
  else {
    uVar6 = 0xffffffff;
    puVar2 = ((undefined *)camry_host_ptr(0xfebeb800u));
    if ((param_1 & 0x11) == 0x11) {
      if (DAT_febef210 == 0) {
        iVar4 = 0x5a;
      }
      else {
        if (DAT_febeb494 == '\0') {
          puVar3 = 0xfebeb800u;
          thunk_FUN_00034bce();
          cVar5 = 'Z';
        }
        iVar4 = 0;
        puVar2 = ((undefined *)camry_host_ptr((uint32_t)(puVar3)));
        bVar8 = bVar8 | param_2;
      }
    }
    if ((param_1 & 0x22) != 0x22) goto LAB_000b916e;
    if (iVar1 != 0) {
      if (cVar7 == '\0') {
        thunk_FUN_0003599e();
        cVar7 = 'Z';
        puVar2[-0x369] = 0x5a;
        puVar2[-0x368] = param_2;
      }
      bVar8 = bVar8 | param_2;
      goto LAB_000b917c;
    }
  }
  if (param_2 == 1 || param_2 == 2) {
    uVar6 = 0;
  }
LAB_000b917c:
  puVar2[-0x36c] = cVar5;
  puVar2[-0x36b] = cVar7;
  puVar2[-0x36a] = bVar8;
  return uVar6;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_b918c(void)

{
  return;
}



void FUN_000b91ee(undefined1 param_1)

{
  uint32_t puVar1;
  undefined1 local_10;
  undefined1 uStack_f;
  undefined2 uStack_e;
  undefined4 uStack_c;
  
  puVar1 = 0xfebeb800u;
  uStack_f = 0;
  uStack_e = 0;
  uStack_c = 0;
  local_10 = DAT_febeaf49;
  FUN_000ff09c(7,&local_10);
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x8b8))))) = param_1;
  return;
}



void FUN_000b92c8(char param_1,char param_2)

{
  undefined4 uVar1;
  
  if (param_1 == '\x03' || param_1 == '\x04') {
    uVar1 = 0x20;
    if (param_2 == '\x10') {
      uVar1 = 0;
    }
    ((void)(0x12), (void)(uVar1), thunk_FUN_0004d0a4());
  }
  return;
}



void FUN_000b9320(undefined1 param_1)

{
  DAT_febeaf47 = param_1;
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_b9326(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_b9328(void)

{
  return;
}



void FUN_000b932a(void)

{
  DAT_febeb49c = 0;
  if (DAT_febeb078 != '\0') {
    DAT_febeb49c = 0x5a;
  }
  return;
}



void FUN_000b933c(void)

{
  if (((((((DAT_febeb067 == '\0') && (DAT_febeb068 == '\0')) && (DAT_febeb069 == '\0')) &&
        ((DAT_febeb06a == '\0' && (DAT_febeb06b == '\0')))) &&
       (((DAT_febeb06c == '\0' && ((DAT_febeb06d == '\0' && (DAT_febeb06e == '\0')))) &&
        (DAT_febeb06f == '\0')))) &&
      (((DAT_febeb070 == '\0' && (DAT_febeb071 == '\0')) &&
       ((DAT_febeb358 == '\0' || (DAT_febeb358 == '\x02')))))) && (DAT_febef208 == -0x5aa5a55b)) {
    DAT_febeb49d = 0;
  }
  else {
    DAT_febeb49d = 0x5a;
  }
  return;
}



/* Set slot qualification from configured magnitude/source/marker gates. Five configured slots use
   AED78..AEDC4. This is a software observation gate, not physical freshness. */

void f33_qualify_control_profile_observation(uchar slot)

{
  uchar uVar1;
  short sVar2;
  short sVar3;
  short sVar4;
  short sVar5;
  int iVar6;
  int iVar7;
  int iVar8;
  
  iVar7 = (int)DAT_febef1ca;
  iVar8 = (int)DAT_febef1c6;
  iVar6 = (int)DAT_febeb054;
  if (iVar6 + 0x7fff < 0 == (-1 < iVar6 && iVar6 + 0x7fff < 0) && iVar6 != -0x7fff) {
    sVar2 = DAT_febeb054;
    if (iVar6 < 0) {
      sVar2 = -DAT_febeb054;
    }
  }
  else {
    sVar2 = 0x7fff;
  }
  if (iVar7 + 0x7fff < 0 == (-1 < iVar7 && iVar7 + 0x7fff < 0) && iVar7 != -0x7fff) {
    sVar3 = DAT_febef1ca;
    if (iVar7 < 0) {
      sVar3 = -DAT_febef1ca;
    }
  }
  else {
    sVar3 = 0x7fff;
  }
  if (iVar8 + 0x7fff < 0 == (-1 < iVar8 && iVar8 + 0x7fff < 0) && iVar8 != -0x7fff) {
    sVar4 = DAT_febef1c6;
    if (iVar8 < 0) {
      sVar4 = -DAT_febef1c6;
    }
  }
  else {
    sVar4 = 0x7fff;
  }
  iVar6 = (int)DAT_febef1c8;
  if (iVar6 + 0x7fff < 0 == (-1 < iVar6 && iVar6 + 0x7fff < 0) && iVar6 != -0x7fff) {
    sVar5 = DAT_febef1c8;
    if (iVar6 < 0) {
      sVar5 = -DAT_febef1c8;
    }
  }
  else {
    sVar5 = 0x7fff;
  }
  iVar7 = (int)f33_profile_config_b054_abs_upper[slot];
  iVar6 = sVar2 - iVar7;
  if (iVar6 < 0 != (sVar2 < 0 != iVar7 < 0 && iVar7 < 0 == iVar6 < 0)) {
    iVar7 = (int)f33_profile_config_f1ca_abs_upper[slot];
    iVar6 = sVar3 - iVar7;
    if (iVar6 < 0 != (sVar3 < 0 != iVar7 < 0 && iVar7 < 0 == iVar6 < 0)) {
      iVar7 = (int)f33_profile_config_f1c6_abs_upper[slot];
      iVar6 = sVar4 - iVar7;
      if (iVar6 < 0 != (sVar4 < 0 != iVar7 < 0 && iVar7 < 0 == iVar6 < 0)) {
        iVar7 = (int)f33_profile_config_f1c8_abs_upper[slot];
        iVar6 = sVar5 - iVar7;
        if (((((((((iVar6 < 0 != (sVar5 < 0 != iVar7 < 0 && iVar7 < 0 == iVar6 < 0)) &&
                  (DAT_febef159 < "ddddd"[slot])) && (f33_profile_config_enable_nonzero[slot] != 0))
                && ((DAT_febef1b6 < f33_profile_config_f1b6_exclusive_upper[slot] &&
                    (f33_profile_config_f1b6_exclusive_lower[slot] < DAT_febef1b6)))) &&
               (DAT_febef091 == '\0')) &&
              (((DAT_febef0a2 == '\0' && (DAT_febef08e == '\0')) &&
               ((DAT_febef084 == '\0' &&
                (((DAT_febef083 == '\0' && (DAT_febef086 == '\0')) && (DAT_febef085 == '\0'))))))))
             && ((DAT_febeb49c == '\0' && (DAT_febeb49d == '\0')))) &&
            (((DAT_febef09e == '\0' &&
              (((DAT_febef0a6 == '\0' && (DAT_febef0a7 == '\0')) &&
               ((DAT_febef094 == '\0' &&
                (((DAT_febef15a == '\0' &&
                  (f33_profile_config_b084_inclusive_lower[slot] <= DAT_febeb084)) &&
                 (DAT_febef161 == '\0')))))))) &&
             (((DAT_febef087 == '\0' && (DAT_febef0c2 == '\0')) && (DAT_febef0a9 == '\0')))))) &&
           ((DAT_febef093 == '\0' && (DAT_febef165 == '\0')))) {
          uVar1 = 'Z';
          goto LAB_000b9570;
        }
      }
    }
  }
  uVar1 = '\0';
LAB_000b9570:
  f33_profile_qualification[slot] = uVar1;
  return;
}



/* While qualificationB49E==5A, add sourceF15B minus previous signed16 byte sample, adding256 when
   narrowed delta is negative; clamp signed32 total to[-32768,32767]. Save previous sample even when
   unqualified. */

void f33_accumulate_profile_counter_first_a(uchar slot)

{
  int iVar1;
  int iVar2;
  int iVar3;
  short sVar4;
  int iVar5;
  int iVar6;
  uint uVar7;
  
  uVar7 = (uint)slot;
  iVar2 = uVar7 * 2;
  iVar3 = uVar7 * 4;
  sVar4 = *(short *)(((undefined *)camry_host_ptr(0xfebeb4b2u)) + iVar2);
  iVar5 = *(int *)(((undefined *)camry_host_ptr(0xfebeb554u)) + iVar3);
  if (f33_profile_qualification[uVar7] == 'Z') {
    iVar1 = (uint)DAT_febef15b - (int)sVar4;
    iVar6 = iVar1 + iVar5;
    if ((short)iVar1 < 0) {
      iVar6 = iVar6 + 0x100;
    }
  }
  else {
    iVar5 = 0;
    iVar6 = 0;
  }
  *(ushort *)(((undefined *)camry_host_ptr(0xfebeb4b2u)) + iVar2) = (ushort)DAT_febef15b;
  if (iVar6 + -0x7fff < 0 == (iVar6 < 0 && -1 < iVar6 + -0x7fff)) {
    iVar6 = 0x7fff;
  }
  if (iVar6 + 0x8000 < 0 != (-1 < iVar6 && iVar6 + 0x8000 < 0)) {
    iVar6 = -0x8000;
  }
  *(short *)(((undefined *)camry_host_ptr(0xfebeb518u)) + iVar2) = sVar4;
  *(int *)(((undefined *)camry_host_ptr(0xfebeb554u)) + iVar3) = iVar6;
  *(int *)(((undefined *)camry_host_ptr(0xfebeb540u)) + iVar3) = iVar5;
  return;
}



/* While qualificationB49E==5A, add sourceF15C minus previous signed16 byte sample, adding256 when
   narrowed delta is negative; clamp signed32 total to[-32768,32767]. Save previous sample even when
   unqualified. */

void f33_accumulate_profile_counter_first_b(uchar slot)

{
  int iVar1;
  int iVar2;
  int iVar3;
  short sVar4;
  int iVar5;
  int iVar6;
  uint uVar7;
  
  uVar7 = (uint)slot;
  iVar2 = uVar7 * 2;
  iVar3 = uVar7 * 4;
  sVar4 = *(short *)(((undefined *)camry_host_ptr(0xfebeb4c6u)) + iVar2);
  iVar5 = *(int *)(((undefined *)camry_host_ptr(0xfebeb57cu)) + iVar3);
  if (f33_profile_qualification[uVar7] == 'Z') {
    iVar1 = (uint)DAT_febef15c - (int)sVar4;
    iVar6 = iVar1 + iVar5;
    if ((short)iVar1 < 0) {
      iVar6 = iVar6 + 0x100;
    }
  }
  else {
    iVar5 = 0;
    iVar6 = 0;
  }
  *(ushort *)(((undefined *)camry_host_ptr(0xfebeb4c6u)) + iVar2) = (ushort)DAT_febef15c;
  if (iVar6 + -0x7fff < 0 == (iVar6 < 0 && -1 < iVar6 + -0x7fff)) {
    iVar6 = 0x7fff;
  }
  if (iVar6 + 0x8000 < 0 != (-1 < iVar6 && iVar6 + 0x8000 < 0)) {
    iVar6 = -0x8000;
  }
  *(short *)(((undefined *)camry_host_ptr(0xfebeb52cu)) + iVar2) = sVar4;
  *(int *)(((undefined *)camry_host_ptr(0xfebeb57cu)) + iVar3) = iVar6;
  *(int *)(((undefined *)camry_host_ptr(0xfebeb568u)) + iVar3) = iVar5;
  return;
}



/* While qualificationB49E==5A, add sourceF15D minus previous signed16 byte sample, adding256 when
   narrowed delta is negative; clamp signed32 total to[-32768,32767]. Save previous sample even when
   unqualified. */

void f33_accumulate_profile_counter_second_a(uchar slot)

{
  int iVar1;
  int iVar2;
  int iVar3;
  short sVar4;
  int iVar5;
  int iVar6;
  uint uVar7;
  
  uVar7 = (uint)slot;
  iVar2 = uVar7 * 2;
  iVar3 = uVar7 * 4;
  sVar4 = *(short *)(((undefined *)camry_host_ptr(0xfebeb4bcu)) + iVar2);
  iVar5 = *(int *)(((undefined *)camry_host_ptr(0xfebeb5a4u)) + iVar3);
  if (f33_profile_qualification[uVar7] == 'Z') {
    iVar1 = (uint)DAT_febef15d - (int)sVar4;
    iVar6 = iVar1 + iVar5;
    if ((short)iVar1 < 0) {
      iVar6 = iVar6 + 0x100;
    }
  }
  else {
    iVar5 = 0;
    iVar6 = 0;
  }
  *(ushort *)(((undefined *)camry_host_ptr(0xfebeb4bcu)) + iVar2) = (ushort)DAT_febef15d;
  if (iVar6 + -0x7fff < 0 == (iVar6 < 0 && -1 < iVar6 + -0x7fff)) {
    iVar6 = 0x7fff;
  }
  if (iVar6 + 0x8000 < 0 != (-1 < iVar6 && iVar6 + 0x8000 < 0)) {
    iVar6 = -0x8000;
  }
  *(short *)(((undefined *)camry_host_ptr(0xfebeb522u)) + iVar2) = sVar4;
  *(int *)(((undefined *)camry_host_ptr(0xfebeb5a4u)) + iVar3) = iVar6;
  *(int *)(((undefined *)camry_host_ptr(0xfebeb590u)) + iVar3) = iVar5;
  return;
}



/* While qualificationB49E==5A, add sourceF15E minus previous signed16 byte sample, adding256 when
   narrowed delta is negative; clamp signed32 total to[-32768,32767]. Save previous sample even when
   unqualified. */

void f33_accumulate_profile_counter_second_b(uchar slot)

{
  int iVar1;
  int iVar2;
  int iVar3;
  short sVar4;
  int iVar5;
  int iVar6;
  uint uVar7;
  
  uVar7 = (uint)slot;
  iVar2 = uVar7 * 2;
  iVar3 = uVar7 * 4;
  sVar4 = *(short *)(((undefined *)camry_host_ptr(0xfebeb4d0u)) + iVar2);
  iVar5 = *(int *)(((undefined *)camry_host_ptr(0xfebeb5ccu)) + iVar3);
  if (f33_profile_qualification[uVar7] == 'Z') {
    iVar1 = (uint)DAT_febef15e - (int)sVar4;
    iVar6 = iVar1 + iVar5;
    if ((short)iVar1 < 0) {
      iVar6 = iVar6 + 0x100;
    }
  }
  else {
    iVar5 = 0;
    iVar6 = 0;
  }
  *(ushort *)(((undefined *)camry_host_ptr(0xfebeb4d0u)) + iVar2) = (ushort)DAT_febef15e;
  if (iVar6 + -0x7fff < 0 == (iVar6 < 0 && -1 < iVar6 + -0x7fff)) {
    iVar6 = 0x7fff;
  }
  if (iVar6 + 0x8000 < 0 != (-1 < iVar6 && iVar6 + 0x8000 < 0)) {
    iVar6 = -0x8000;
  }
  *(int *)(((undefined *)camry_host_ptr(0xfebeb5ccu)) + iVar3) = iVar6;
  *(short *)(((undefined *)camry_host_ptr(0xfebeb536u)) + iVar2) = sVar4;
  *(int *)(((undefined *)camry_host_ptr(0xfebeb5b8u)) + iVar3) = iVar5;
  return;
}



/* Sequential initializer chain: 4 unconditional calls and no other statements; shape-verified. The
   called sequence is the function's entire behavior; chain family members differ in callee sets. */

void f33_run_init_chain_b975a(uchar param_1)

{
  f33_accumulate_profile_counter_first_a(param_1);
  f33_accumulate_profile_counter_first_b(param_1);
  f33_accumulate_profile_counter_second_a(param_1);
  f33_accumulate_profile_counter_second_b(param_1);
  return;
}



/* Require current qualification and saturating-abs differences of both accumulated pairs strictly
   below configured3. Publish the result toB49E and4A3. */

void f33_qualify_control_profile_counter_pairs(uchar slot)

{
  uint uVar1;
  int iVar2;
  uchar uVar3;
  int iVar4;
  int iVar5;
  
  uVar1 = (uint)slot;
  iVar4 = uVar1 * 4;
  iVar5 = *(int *)(((undefined *)camry_host_ptr(0xfebeb554u)) + iVar4) - *(int *)(((undefined *)camry_host_ptr(0xfebeb57cu)) + iVar4);
  iVar4 = *(int *)(((undefined *)camry_host_ptr(0xfebeb5a4u)) + iVar4) - *(int *)(((undefined *)camry_host_ptr(0xfebeb5ccu)) + iVar4);
  if (iVar5 + 0x7fffffff < 0 == (-1 < iVar5 && iVar5 + 0x7fffffff < 0) && iVar5 != -0x7fffffff) {
    if (iVar5 < 0) {
      iVar5 = -iVar5;
    }
  }
  else {
    iVar5 = 0x7fffffff;
  }
  if (iVar4 + 0x7fffffff < 0 == (-1 < iVar4 && iVar4 + 0x7fffffff < 0) && iVar4 != -0x7fffffff) {
    if (iVar4 < 0) {
      iVar4 = -iVar4;
    }
  }
  else {
    iVar4 = 0x7fffffff;
  }
  if (((f33_profile_qualification[uVar1] == 'Z') &&
      (iVar2 = f33_profile_config_first_difference_exclusive_upper[uVar1],
      iVar5 - iVar2 < 0 != (iVar5 < 0 != iVar2 < 0 && iVar2 < 0 == iVar5 - iVar2 < 0))) &&
     (iVar5 = f33_profile_config_second_difference_exclusive_upper[uVar1],
     iVar4 - iVar5 < 0 != (iVar4 < 0 != iVar5 < 0 && iVar5 < 0 == iVar4 - iVar5 < 0))) {
    uVar3 = 'Z';
  }
  else {
    uVar3 = '\0';
  }
  f33_profile_counter_pair_qualification[uVar1] = uVar3;
  f33_profile_qualification[uVar1] = uVar3;
  return;
}



/* While4A3==5A retain the smaller-magnitude signed endpoint in each counter pair, then select the
   smaller-magnitude signed value; otherwise clear the endpoints/output. Do not replace signed
   comparison source with an unsigned magnitude. */

void f33_select_control_profile_counter_floor(uchar slot)

{
  int iVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  int iVar6;
  int iVar7;
  int iVar8;
  int iVar9;
  
  iVar1 = (uint)slot * 4;
  iVar2 = *(int *)(((undefined *)camry_host_ptr(0xfebeb554u)) + iVar1);
  iVar9 = *(int *)(((undefined *)camry_host_ptr(0xfebeb57cu)) + iVar1);
  iVar8 = *(int *)(((undefined *)camry_host_ptr(0xfebeb5a4u)) + iVar1);
  iVar7 = *(int *)(((undefined *)camry_host_ptr(0xfebeb5ccu)) + iVar1);
  if (iVar2 + 0x7fffffff < 0 == (-1 < iVar2 && iVar2 + 0x7fffffff < 0) && iVar2 != -0x7fffffff) {
    iVar3 = iVar2;
    if (iVar2 < 0) {
      iVar3 = -iVar2;
    }
  }
  else {
    iVar3 = 0x7fffffff;
  }
  if (iVar9 + 0x7fffffff < 0 == (-1 < iVar9 && iVar9 + 0x7fffffff < 0) && iVar9 != -0x7fffffff) {
    iVar4 = iVar9;
    if (iVar9 < 0) {
      iVar4 = -iVar9;
    }
  }
  else {
    iVar4 = 0x7fffffff;
  }
  if (iVar8 + 0x7fffffff < 0 == (-1 < iVar8 && iVar8 + 0x7fffffff < 0) && iVar8 != -0x7fffffff) {
    iVar5 = iVar8;
    if (iVar8 < 0) {
      iVar5 = -iVar8;
    }
  }
  else {
    iVar5 = 0x7fffffff;
  }
  if (iVar7 + 0x7fffffff < 0 == (-1 < iVar7 && iVar7 + 0x7fffffff < 0) && iVar7 != -0x7fffffff) {
    iVar6 = iVar7;
    if (iVar7 < 0) {
      iVar6 = -iVar7;
    }
  }
  else {
    iVar6 = 0x7fffffff;
  }
  if (f33_profile_counter_pair_qualification[slot] == 'Z') {
    if (iVar3 - iVar4 < 0 != (iVar3 < 0 != iVar4 < 0 && iVar4 < 0 == iVar3 - iVar4 < 0)) {
      iVar9 = iVar2;
    }
    if (iVar5 - iVar6 < 0 != (iVar5 < 0 != iVar6 < 0 && iVar6 < 0 == iVar5 - iVar6 < 0)) {
      iVar7 = iVar8;
    }
    if (iVar9 + 0x7fffffff < 0 == (-1 < iVar9 && iVar9 + 0x7fffffff < 0) && iVar9 != -0x7fffffff) {
      iVar8 = iVar9;
      if (iVar9 < 0) {
        iVar8 = -iVar9;
      }
    }
    else {
      iVar8 = 0x7fffffff;
    }
    if (iVar7 + 0x7fffffff < 0 == (-1 < iVar7 && iVar7 + 0x7fffffff < 0) && iVar7 != -0x7fffffff) {
      iVar3 = iVar7;
      if (iVar7 < 0) {
        iVar3 = -iVar7;
      }
    }
    else {
      iVar3 = 0x7fffffff;
    }
    iVar2 = iVar7;
    if (iVar8 - iVar3 < 0 != (iVar8 < 0 != iVar3 < 0 && iVar3 < 0 == iVar8 - iVar3 < 0)) {
      iVar2 = iVar9;
    }
  }
  else {
    iVar9 = 0;
    iVar7 = 0;
    iVar2 = 0;
  }
  *(int *)(((undefined *)camry_host_ptr(0xfebeb61cu)) + iVar1) = iVar2;
  *(int *)(((undefined *)camry_host_ptr(0xfebeb608u)) + iVar1) = iVar2;
  *(int *)(((undefined *)camry_host_ptr(0xfebeb5e0u)) + iVar1) = iVar9;
  *(int *)(((undefined *)camry_host_ptr(0xfebeb5f4u)) + iVar1) = iVar7;
  return;
}



/* Track unsigned maximumF1B6 while4A3==5A; unsigned32 interpolation from slot table stores a32-bit
   threshold. Outside qualification clear maximum/intermediate and use configured lower ordinate.
   Subtraction/multiply wrap before division/clipping. */

void f33_update_control_profile_threshold(uchar slot)

{
  uint uVar1;
  uint uVar2;
  uint uVar3;
  uint uVar4;
  uint uVar5;
  uint uVar6;
  
  uVar3 = (uint)slot;
  if (f33_profile_counter_pair_qualification[uVar3] == 'Z') {
    uVar5 = (uint)DAT_febef1b6;
    if (uVar5 <= *(ushort *)(((undefined *)camry_host_ptr(0xfebeb4dau)) + uVar3 * 2)) {
      uVar5 = (uint)*(ushort *)(((undefined *)camry_host_ptr(0xfebeb4dau)) + uVar3 * 2);
    }
    uVar6 = (uint)f33_profile_config_interpolation_lower[uVar3];
    uVar4 = (uint)f33_profile_config_interpolation_upper[uVar3];
    uVar2 = (uVar4 - uVar6) * (uVar5 - f33_profile_config_axis_lower[uVar3]);
    uVar1 = (uint)f33_profile_config_axis_upper[uVar3] - (uint)f33_profile_config_axis_lower[uVar3];
    if (uVar1 != 0) {
      uVar2 = uVar2 / uVar1;
    }
    uVar2 = uVar6 + uVar2;
    if ((uVar2 < uVar4) && (uVar4 = uVar2, uVar2 < uVar6)) {
      uVar4 = uVar6;
    }
  }
  else {
    uVar2 = 0;
    uVar5 = 0;
    uVar4 = (uint)f33_profile_config_interpolation_lower[uVar3];
  }
  *(short *)(((undefined *)camry_host_ptr(0xfebeb4dau)) + uVar3 * 2) = (short)uVar5;
  *(uint *)(((undefined *)camry_host_ptr(0xfebeb630u)) + uVar3 * 4) = uVar2;
  *(uint *)(((undefined *)camry_host_ptr(0xfebeb644u)) + uVar3 * 4) = uVar4;
  return;
}



/* OnlyB4A3==5A recomputesB4A8 as signed selected-counter value>=threshold. Otherwise preserve4A8;
   completion may consume a held result. */

void f33_publish_control_profile_threshold_result(uchar slot)

{
  int iVar1;
  uchar uVar2;
  int iVar3;
  uint uVar4;
  
  uVar4 = (uint)slot;
  iVar3 = *(int *)(((undefined *)camry_host_ptr(0xfebeb644u)) + uVar4 * 4);
  uVar2 = f33_profile_threshold_result[uVar4];
  if (f33_profile_counter_pair_qualification[uVar4] == 'Z') {
    iVar1 = *(int *)(((undefined *)camry_host_ptr(0xfebeb61cu)) + uVar4 * 4) - iVar3;
    if (iVar1 < 0 ==
        (*(int *)(((undefined *)camry_host_ptr(0xfebeb61cu)) + uVar4 * 4) < 0 != iVar3 < 0 && iVar3 < 0 == iVar1 < 0)) {
      uVar2 = 'Z';
    }
    else {
      uVar2 = '\0';
    }
  }
  f33_profile_threshold_result[uVar4] = uVar2;
  return;
}



/* Sequential initializer chain: 4 unconditional calls and no other statements; shape-verified. The
   called sequence is the function's entire behavior; chain family members differ in callee sets. */

void f33_run_init_chain_b997e(uchar param_1)

{
  f33_qualify_control_profile_counter_pairs(param_1);
  f33_select_control_profile_counter_floor(param_1);
  f33_update_control_profile_threshold(param_1);
  f33_publish_control_profile_threshold_result(param_1);
  return;
}



/* WARNING: Removing unreachable block (ram,0x000b99cc) */
/* Signed16 AE5C times37549 uses low32 signed product and truncating signed division65536, then
   narrows signed16. Qualified calls update signed extrema; other calls reseed both from current
   scaled source. */

void f33_track_control_profile_source_extrema(uchar slot)

{
  int iVar1;
  short sVar2;
  int iVar3;
  short sVar4;
  int iVar5;
  int iVar6;
  
  iVar1 = (uint)slot * 2;
  iVar5 = (int)*(short *)(((undefined *)camry_host_ptr(0xfebeb4e6u)) + iVar1);
  sVar2 = *(short *)(((undefined *)camry_host_ptr(0xfebeb4f0u)) + iVar1);
  iVar3 = (int)sVar2;
  DAT_febeb4e4 = (short)((DAT_febeae5c * 0x92ad) / 0x10000);
  iVar6 = (int)DAT_febeb4e4;
  sVar4 = DAT_febeb4e4;
  if (f33_profile_counter_pair_qualification[slot] == 'Z') {
    if (iVar6 - iVar5 < 0 != (iVar6 < 0 != iVar5 < 0 && iVar5 < 0 == iVar6 - iVar5 < 0) ||
        iVar6 == iVar5) {
      sVar4 = *(short *)(((undefined *)camry_host_ptr(0xfebeb4e6u)) + iVar1);
    }
    if (iVar6 - iVar3 < 0 == (iVar6 < 0 != iVar3 < 0 && iVar3 < 0 == iVar6 - iVar3 < 0))
    goto LAB_000b99ec;
  }
  sVar2 = DAT_febeb4e4;
LAB_000b99ec:
  *(short *)(((undefined *)camry_host_ptr(0xfebeb4e6u)) + iVar1) = sVar4;
  *(short *)(((undefined *)camry_host_ptr(0xfebeb4f0u)) + iVar1) = sVar2;
  return;
}



/* Seed both extrema from shared4E4 and clear the eight per-slot counter accumulator/previous-output
   words. Does not clear first/ranked retained banks or their validity. */

void f33_reset_control_profile_interval(uchar slot)

{
  int iVar1;
  undefined2 uVar2;
  
  uVar2 = DAT_febeb4e4;
  iVar1 = (uint)slot * 2;
  *(undefined2 *)(((undefined *)camry_host_ptr(0xfebeb4e6u)) + iVar1) = DAT_febeb4e4;
  *(undefined2 *)(((undefined *)camry_host_ptr(0xfebeb4f0u)) + iVar1) = uVar2;
  iVar1 = (uint)slot * 4;
  *(undefined4 *)(((undefined *)camry_host_ptr(0xfebeb554u)) + iVar1) = 0;
  *(undefined4 *)(((undefined *)camry_host_ptr(0xfebeb57cu)) + iVar1) = 0;
  *(undefined4 *)(((undefined *)camry_host_ptr(0xfebeb5a4u)) + iVar1) = 0;
  *(undefined4 *)(((undefined *)camry_host_ptr(0xfebeb5ccu)) + iVar1) = 0;
  *(undefined4 *)(((undefined *)camry_host_ptr(0xfebeb540u)) + iVar1) = 0;
  *(undefined4 *)(((undefined *)camry_host_ptr(0xfebeb568u)) + iVar1) = 0;
  *(undefined4 *)(((undefined *)camry_host_ptr(0xfebeb590u)) + iVar1) = 0;
  *(undefined4 *)(((undefined *)camry_host_ptr(0xfebeb5b8u)) + iVar1) = 0;
  return;
}



/* Qualified signed extrema span<50 admits count increment capped65536 and saturating signed32 sum;
   signed division truncates toward zero and narrows to16 bits. Rejection clears this interval
   and49E, leaving completion-source4A8 independently held. */

void f33_average_control_profile_source_interval(uchar slot)

{
  int iVar1;
  int iVar2;
  int iVar3;
  uint uVar4;
  undefined2 uVar5;
  int iVar6;
  uint uVar7;
  int iVar8;
  uchar uStack_31;
  
  uVar4 = (uint)slot;
  iVar2 = uVar4 * 4;
  uStack_31 = f33_profile_qualification[uVar4];
  iVar6 = *(int *)(((undefined *)camry_host_ptr(0xfebeb680u)) + iVar2);
  iVar3 = uVar4 * 2;
  iVar8 = (int)DAT_febeb4e4;
  if (f33_profile_counter_pair_qualification[uVar4] == 'Z') {
    iVar1 = ((int)*(short *)(((undefined *)camry_host_ptr(0xfebeb4e6u)) + iVar3) - (int)*(short *)(((undefined *)camry_host_ptr(0xfebeb4f0u)) + iVar3)) -
            (uint)f33_profile_config_b4e6_minus_b4f0_exclusive_upper[uVar4];
    if (iVar1 < 0 !=
        ((int)*(short *)(((undefined *)camry_host_ptr(0xfebeb4e6u)) + iVar3) - (int)*(short *)(((undefined *)camry_host_ptr(0xfebeb4f0u)) + iVar3) < 0 &&
        -1 < iVar1)) {
      uVar7 = *(int *)(((undefined *)camry_host_ptr(0xfebeb658u)) + iVar2) + 1;
      if (0xffff < uVar7) {
        uVar7 = 0x10000;
      }
      if (iVar6 < 0) {
        iVar1 = -0x80000000 - iVar6;
        if (iVar1 - iVar8 < 0 != (iVar1 < 0 != iVar8 < 0 && iVar8 < 0 == iVar1 - iVar8 < 0) ||
            iVar1 == iVar8) goto LAB_000b9ac0;
        iVar8 = -0x80000000;
      }
      else {
        iVar1 = (0x7fffffff - iVar6) - iVar8;
        if (iVar1 < 0 == (0x7fffffff - iVar6 < 0 != iVar8 < 0 && iVar8 < 0 == iVar1 < 0)) {
LAB_000b9ac0:
          iVar8 = iVar8 + iVar6;
        }
        else {
          iVar8 = 0x7fffffff;
        }
      }
      iVar6 = iVar8;
      if (uVar7 != 0) {
        if (iVar8 == -0x80000000 && uVar7 == 0xffffffff) {
          iVar6 = 0;
        }
        else {
          iVar6 = iVar8 / (int)uVar7;
        }
      }
      uVar5 = (undefined2)iVar6;
      goto LAB_000b9ade;
    }
    uStack_31 = '\0';
  }
  iVar8 = 0;
  uVar7 = 0;
  uVar5 = 0;
  f33_reset_control_profile_interval(slot);
LAB_000b9ade:
  *(uint *)(((undefined *)camry_host_ptr(0xfebeb658u)) + iVar2) = uVar7;
  *(uint *)(((undefined *)camry_host_ptr(0xfebeb66cu)) + iVar2) = uVar7;
  *(int *)(((undefined *)camry_host_ptr(0xfebeb680u)) + iVar2) = iVar8;
  *(int *)(((undefined *)camry_host_ptr(0xfebeb694u)) + iVar2) = iVar8;
  *(undefined2 *)(((undefined *)camry_host_ptr(0xfebeb4fau)) + iVar3) = uVar5;
  f33_profile_qualification[uVar4] = uStack_31;
  return;
}



/* ExactB4A8==5A copies interval mean toB504/B50E, resets interval and counter-pair state, and
   publishesB4AD5A. Otherwise retainB50E inB504 and publishB4AD0.B4A8 is not cleared here. */

void f33_publish_control_profile_interval(uchar slot)

{
  int iVar1;
  int iVar2;
  uchar uVar3;
  short sVar4;
  uint uVar5;
  
  uVar5 = (uint)slot;
  iVar1 = uVar5 * 2;
  if (f33_profile_threshold_result[uVar5] == 'Z') {
    sVar4 = *(short *)(((undefined *)camry_host_ptr(0xfebeb4fau)) + iVar1);
    iVar2 = uVar5 * 4;
    *(short *)(((undefined *)camry_host_ptr(0xfebeb50eu)) + iVar1) = sVar4;
    f33_profile_qualification[uVar5] = '\0';
    *(undefined2 *)(((undefined *)camry_host_ptr(0xfebeb4fau)) + iVar1) = 0;
    *(undefined4 *)(((undefined *)camry_host_ptr(0xfebeb694u)) + iVar2) = 0;
    *(undefined4 *)(((undefined *)camry_host_ptr(0xfebeb680u)) + iVar2) = 0;
    *(undefined4 *)(((undefined *)camry_host_ptr(0xfebeb66cu)) + iVar2) = 0;
    *(undefined4 *)(((undefined *)camry_host_ptr(0xfebeb658u)) + iVar2) = 0;
    f33_reset_control_profile_interval(slot);
    uVar3 = 'Z';
  }
  else {
    sVar4 = *(short *)(((undefined *)camry_host_ptr(0xfebeb50eu)) + iVar1);
    uVar3 = '\0';
  }
  f33_profile_published_observation[uVar5] = sVar4;
  f33_profile_observation_published[uVar5] = uVar3;
  return;
}



void FUN_000b9b72(uchar param_1)

{
  f33_track_control_profile_source_extrema(param_1);
  f33_average_control_profile_source_interval(param_1);
  f33_publish_control_profile_interval(param_1);
  return;
}



/* Refresh common control/source gates, then run qualification, counter-pair, threshold,
   extrema/mean and completion for slots0..4. Foreground modes0300..0522 and cadence bit1 own this
   generation. */

void f33_run_control_profile_qualification(void)

{
  uint uVar1;
  
  FUN_000b932a();
  FUN_000b933c();
  uVar1 = 0;
  do {
    f33_qualify_control_profile_observation((uchar)uVar1);
    f33_run_init_chain_b975a(uVar1);
    f33_run_init_chain_b997e(uVar1);
    FUN_000b9b72(uVar1);
    uVar1 = uVar1 + 1;
  } while (uVar1 < 5);
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_b9bbe(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_b9bc0(void)

{
  return;
}



/* WARNING: Removing unreachable block (ram,0x000b9be6) */
/* F0C0==0 andF000<2 refresh sharedBBD8 from low32(F228*9387), signed division65536. Other calls
   hold the value. Source receipt and record retention are separate. */

void f33_refresh_profile_scaled_word(void)

{
  if ((DAT_febef0c0 == '\0') && (f33_published_internal_source_admission_state < 2)) {
    DAT_febebbd8 = (DAT_febef228 * 0x24ab) / 0x10000;
  }
  return;
}



/* F069==0,F000<2,F154==2,F06B==0 refresh signed halfwordB852 from signedF1A0*15 plus signed
   byteF06F; otherwise hold. Store narrows modulo65536. */

void f33_refresh_profile_received_composite(void)

{
  if ((((DAT_febef069 == '\0') && (f33_published_internal_source_admission_state < 2)) &&
      (DAT_febef154 == '\x02')) && (DAT_febef06b == '\0')) {
    DAT_febeb852 = (short)DAT_febef06f + DAT_febef1a0 * 0xf;
  }
  return;
}



/* Qualified4A3 selects retained interval extrema4E6/B4F0. Otherwise use currentB4E4 only after
   first-profile validityB6DF5A; before it select zeros. */

void f33_select_profile_source_extrema(uchar slot)

{
  undefined2 uVar1;
  uint uVar2;
  undefined2 uVar3;
  
  uVar2 = (uint)slot;
  if (f33_profile_counter_pair_qualification[uVar2] == 'Z') {
    uVar1 = *(undefined2 *)(((undefined *)camry_host_ptr(0xfebeb4e6u)) + uVar2 * 2);
    uVar3 = *(undefined2 *)(((undefined *)camry_host_ptr(0xfebeb4f0u)) + uVar2 * 2);
  }
  else {
    uVar1 = DAT_febeb4e4;
    uVar3 = DAT_febeb4e4;
    if (f33_profile_first_validity[uVar2] != 'Z') {
      uVar1 = 0;
      uVar3 = 0;
    }
  }
  *(undefined2 *)(((undefined *)camry_host_ptr(0xfebeb83eu)) + uVar2 * 2) = uVar1;
  *(undefined2 *)(((undefined *)camry_host_ptr(0xfebeb848u)) + uVar2 * 2) = uVar3;
  return;
}



/* Run all five aggregate groups and select source extrema in order for the given low8 slot. Keep
   the realR6 slot argument to first childB9C28. */

void f33_update_control_profile_aggregates(uchar slot)

{
  f33_accumulate_profile_unsigned_source(slot);
  f33_accumulate_profile_signed_source1(slot);
  f33_accumulate_profile_signed_source2(slot);
  f33_accumulate_profile_scaled_feedback(slot);
  f33_accumulate_profile_signed_source3(slot);
  f33_select_profile_source_extrema(slot);
  return;
}



/* F093==0,F000<2,F094==0 and unsignedF1B6>400 latchB7705A. Once latched, advance byte divider and
   halfword counter each ten calls, cap6000; losing source admission does not clear latch or stop
   subsequent call aging. */

void f33_age_control_profile_source_latch(uchar slot)

{
  int iVar1;
  uint uVar2;
  uchar uVar3;
  ushort uVar4;
  byte bVar5;
  byte bVar6;
  ushort uVar7;
  
  uVar2 = (uint)slot;
  iVar1 = uVar2 * 2;
  uVar3 = f33_profile_elapsed_validity[uVar2];
  uVar4 = *(ushort *)(((undefined *)camry_host_ptr(0xfebeb85eu)) + iVar1);
  uVar7 = *(ushort *)(((undefined *)camry_host_ptr(0xfebeb854u)) + iVar1);
  bVar6 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb6adu + (uint32_t)(uVar2) * 1u))));
  if ((((DAT_febef093 == '\0') && (f33_published_internal_source_admission_state < 2)) &&
      (DAT_febef094 == '\0')) && (400 < DAT_febef1b6)) {
    uVar3 = 'Z';
  }
  else if (uVar3 != 'Z') {
    bVar5 = 0;
    goto LAB_000ba03c;
  }
  bVar5 = bVar6 + 1;
  bVar6 = bVar5;
  if (9 < bVar5) {
    uVar7 = uVar4 + 1;
    if (5999 < uVar7) {
      uVar7 = 6000;
    }
    bVar6 = 0;
    uVar4 = uVar7;
  }
LAB_000ba03c:
  f33_profile_elapsed_validity[uVar2] = uVar3;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb6a8u + (uint32_t)(uVar2) * 1u)))) = bVar5;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb6adu + (uint32_t)(uVar2) * 1u)))) = bVar6;
  *(ushort *)(((undefined *)camry_host_ptr(0xfebeb854u)) + iVar1) = uVar7;
  *(ushort *)(((undefined *)camry_host_ptr(0xfebeb85eu)) + iVar1) = uVar4;
  return;
}



/* WARNING: Removing unreachable block (ram,0x000ba0b2) */
/* Same instantaneous source gate asB9FBC, not its sticky latch, adds unsignedF1B6 to wrapped32-bit
   accumulator then caps900000000 and stores quotient/36000 to unsigned16. Ineligible calls retain
   accumulator/value. */

void f33_integrate_control_profile_unsigned_source(uchar slot)

{
  int iVar1;
  int iVar2;
  uint uVar3;
  undefined2 uVar4;
  undefined2 uVar5;
  
  iVar1 = (uint)slot * 2;
  iVar2 = (uint)slot * 4;
  uVar5 = *(undefined2 *)(((undefined *)camry_host_ptr(0xfebeb868u)) + iVar1);
  uVar4 = *(undefined2 *)(((undefined *)camry_host_ptr(0xfebeb872u)) + iVar1);
  uVar3 = *(uint *)(((undefined *)camry_host_ptr(0xfebebbdcu)) + iVar2);
  if ((((DAT_febef093 == '\0') && (f33_published_internal_source_admission_state < 2)) &&
      (DAT_febef094 == '\0')) && (400 < DAT_febef1b6)) {
    uVar3 = uVar3 + DAT_febef1b6;
    if (899999999 < uVar3) {
      uVar3 = 900000000;
    }
    uVar4 = (undefined2)(uVar3 / 36000);
    uVar5 = uVar4;
  }
  *(undefined2 *)(((undefined *)camry_host_ptr(0xfebeb872u)) + iVar1) = uVar4;
  *(undefined2 *)(((undefined *)camry_host_ptr(0xfebeb868u)) + iVar1) = uVar5;
  *(uint *)(((undefined *)camry_host_ptr(0xfebebbdcu)) + iVar2) = uVar3;
  return;
}



/* F0F8==0 andF000<2 copy six already-conditioned packed bytesBE66..6B into this working slot;
   otherwise hold. No additional decoding or fresh-generation check. */

void f33_refresh_control_profile_packed_metadata(uchar slot)

{
  uchar uVar1;
  uchar uVar2;
  uchar uVar3;
  uchar uVar4;
  uchar uVar5;
  uchar uVar6;
  
  uVar6 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb6b2u + (uint32_t)(slot) * 1u))));
  uVar5 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb6b7u + (uint32_t)(slot) * 1u))));
  uVar4 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb6bcu + (uint32_t)(slot) * 1u))));
  uVar3 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb6c1u + (uint32_t)(slot) * 1u))));
  uVar2 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb6c6u + (uint32_t)(slot) * 1u))));
  uVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb6cbu + (uint32_t)(slot) * 1u))));
  if ((DAT_febef0f8 == '\0') && (f33_published_internal_source_admission_state < 2)) {
    uVar6 = f33_received_packed_decimal_fields[0];
    uVar5 = f33_received_packed_decimal_fields[1];
    uVar4 = f33_received_packed_decimal_fields[2];
    uVar3 = f33_received_packed_decimal_fields[3];
    uVar2 = f33_received_packed_decimal_fields[4];
    uVar1 = f33_received_packed_decimal_fields[5];
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb6b2u + (uint32_t)(slot) * 1u)))) = uVar6;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb6b7u + (uint32_t)(slot) * 1u)))) = uVar5;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb6bcu + (uint32_t)(slot) * 1u)))) = uVar4;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb6c1u + (uint32_t)(slot) * 1u)))) = uVar3;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb6c6u + (uint32_t)(slot) * 1u)))) = uVar2;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb6cbu + (uint32_t)(slot) * 1u)))) = uVar1;
  return;
}



/* F065==0 andF000<2 copy typed numericalF218 and raw typeF067 into this working slot; otherwise
   hold. The numerical scalar is not a pointer. */

void f33_refresh_control_profile_scalar_metadata(uchar slot)

{
  undefined1 uVar1;
  uint uVar2;
  uint uVar3;
  
  uVar3 = (uint)slot;
  uVar2 = *(uint *)(((undefined *)camry_host_ptr(0xfebebbf0u)) + uVar3 * 4);
  uVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb6d0u + (uint32_t)(uVar3) * 1u))));
  if ((DAT_febef065 == '\0') && (f33_published_internal_source_admission_state < 2)) {
    uVar2 = f33_published_route31_numeric_scalar;
    uVar1 = DAT_febef067;
  }
  *(uint *)(((undefined *)camry_host_ptr(0xfebebbf0u)) + uVar3 * 4) = uVar2;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb6d0u + (uint32_t)(uVar3) * 1u)))) = uVar1;
  return;
}



/* Copy current aggregates, held shared scalars and metadata into five-slot working
   structure-of-arrays. This does not replace any retained bank. */

void f33_stage_control_profile(uchar slot,short capture_value)

{
  int iVar1;
  int iVar2;
  uint uVar3;
  
  iVar2 = DAT_febebbd8;
  uVar3 = (uint)slot;
  iVar1 = uVar3 * 2;
  f33_profile_working_capture_value[uVar3] = capture_value;
  f33_profile_working_received_composite[uVar3] = DAT_febeb852;
  f33_profile_working_integrated_source[uVar3] = *(ushort *)(((undefined *)camry_host_ptr(0xfebeb868u)) + iVar1);
  f33_profile_working_elapsed_groups[uVar3] = *(ushort *)(((undefined *)camry_host_ptr(0xfebeb854u)) + iVar1);
  f33_profile_working_scaled_f228[uVar3] = iVar2;
  f33_profile_working_source_u16_max[uVar3] = *(ushort *)(((undefined *)camry_host_ptr(0xfebeb78au)) + iVar1);
  f33_profile_working_source_u16_mean[uVar3] = *(ushort *)(((undefined *)camry_host_ptr(0xfebeb780u)) + iVar1);
  f33_profile_working_f1c6_max[uVar3] = *(short *)(((undefined *)camry_host_ptr(0xfebeb7bcu)) + iVar1);
  f33_profile_working_f1c6_mean[uVar3] = *(short *)(((undefined *)camry_host_ptr(0xfebeb7b2u)) + iVar1);
  f33_profile_working_f1c8_max[uVar3] = *(short *)(((undefined *)camry_host_ptr(0xfebeb7e4u)) + iVar1);
  f33_profile_working_f1c8_mean[uVar3] = *(short *)(((undefined *)camry_host_ptr(0xfebeb7dau)) + iVar1);
  f33_profile_working_f1ca_max[uVar3] = *(short *)(((undefined *)camry_host_ptr(0xfebeb80cu)) + iVar1);
  f33_profile_working_f1ca_mean[uVar3] = *(short *)(((undefined *)camry_host_ptr(0xfebeb802u)) + iVar1);
  f33_profile_working_scaled_ae5c_max[uVar3] = *(short *)(((undefined *)camry_host_ptr(0xfebeb83eu)) + iVar1);
  f33_profile_working_scaled_ae5c_min[uVar3] = *(short *)(((undefined *)camry_host_ptr(0xfebeb848u)) + iVar1);
  f33_profile_working_scaled_b054_max[uVar3] = *(short *)(((undefined *)camry_host_ptr(0xfebeb834u)) + iVar1);
  f33_profile_working_scaled_b054_mean[uVar3] = *(short *)(((undefined *)camry_host_ptr(0xfebeb82au)) + iVar1);
  f33_profile_working_route31_scalar[uVar3] = *(uint *)(((undefined *)camry_host_ptr(0xfebebbf0u)) + uVar3 * 4);
  f33_profile_working_metadata_0[uVar3] = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb6d0u + (uint32_t)(uVar3) * 1u))));
  f33_profile_working_metadata_1[uVar3] = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb6b2u + (uint32_t)(uVar3) * 1u))));
  f33_profile_working_metadata_2[uVar3] = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb6b7u + (uint32_t)(uVar3) * 1u))));
  f33_profile_working_metadata_3[uVar3] = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb6bcu + (uint32_t)(uVar3) * 1u))));
  f33_profile_working_metadata_4[uVar3] = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb6c1u + (uint32_t)(uVar3) * 1u))));
  f33_profile_working_metadata_5[uVar3] = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb6c6u + (uint32_t)(uVar3) * 1u))));
  f33_profile_working_metadata_6[uVar3] = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb6cbu + (uint32_t)(uVar3) * 1u))));
  return;
}



/* Stage504 only if6DF==5A orB6DF==0 withB4AD==5A; otherwise stage signed32767 sentinel. CallsBA170
   with realR6 slot andR7 signed value. */

void f33_select_and_stage_control_profile(uchar slot)

{
  short capture_value;
  
  capture_value = f33_profile_published_observation[slot];
  if ((f33_profile_first_validity[slot] != 'Z') &&
     ((f33_profile_first_validity[slot] != '\0' || (f33_profile_observation_published[slot] != 'Z'))
     )) {
    capture_value = 0x7fff;
  }
  f33_stage_control_profile(slot,capture_value);
  return;
}



/* Copy all numerical and seven metadata fields from working slot to first retained bank. Caller
   controls locking; this copy does not store validity or elapsed-source marker. */

void f33_retain_first_control_profile(uchar slot)

{
  f33_profile_retained_capture_value[slot] = f33_profile_working_capture_value[slot];
  f33_profile_retained_received_composite[slot] = f33_profile_working_received_composite[slot];
  f33_profile_retained_integrated_source[slot] = f33_profile_working_integrated_source[slot];
  f33_profile_retained_elapsed_groups[slot] = f33_profile_working_elapsed_groups[slot];
  f33_profile_retained_scaled_f228[slot] = f33_profile_working_scaled_f228[slot];
  f33_profile_retained_source_u16_max[slot] = f33_profile_working_source_u16_max[slot];
  f33_profile_retained_source_u16_mean[slot] = f33_profile_working_source_u16_mean[slot];
  f33_profile_retained_f1c6_max[slot] = f33_profile_working_f1c6_max[slot];
  f33_profile_retained_f1c6_mean[slot] = f33_profile_working_f1c6_mean[slot];
  f33_profile_retained_f1c8_max[slot] = f33_profile_working_f1c8_max[slot];
  f33_profile_retained_f1c8_mean[slot] = f33_profile_working_f1c8_mean[slot];
  f33_profile_retained_f1ca_max[slot] = f33_profile_working_f1ca_max[slot];
  f33_profile_retained_f1ca_mean[slot] = f33_profile_working_f1ca_mean[slot];
  f33_profile_retained_scaled_ae5c_max[slot] = f33_profile_working_scaled_ae5c_max[slot];
  f33_profile_retained_scaled_ae5c_min[slot] = f33_profile_working_scaled_ae5c_min[slot];
  f33_profile_retained_scaled_b054_max[slot] = f33_profile_working_scaled_b054_max[slot];
  f33_profile_retained_scaled_b054_mean[slot] = f33_profile_working_scaled_b054_mean[slot];
  f33_profile_retained_route31_scalar[slot] = f33_profile_working_route31_scalar[slot];
  f33_profile_retained_metadata_0[slot] = f33_profile_working_metadata_0[slot];
  f33_profile_retained_metadata_1[slot] = f33_profile_working_metadata_1[slot];
  f33_profile_retained_metadata_2[slot] = f33_profile_working_metadata_2[slot];
  f33_profile_retained_metadata_3[slot] = f33_profile_working_metadata_3[slot];
  f33_profile_retained_metadata_4[slot] = f33_profile_working_metadata_4[slot];
  f33_profile_retained_metadata_5[slot] = f33_profile_working_metadata_5[slot];
  f33_profile_retained_metadata_6[slot] = f33_profile_working_metadata_6[slot];
  return;
}



/* OnlyB6DF==0 can replace first bank: entry refresh counter>=100 orB4AD5A copies working; reset
   both byte counters and setB6DF toB4AD5A or0. Otherwise advance duplicated byte count. Any
   nonzeroB6DF freezes this bank. */

void f33_update_first_control_profile_retention(uchar slot)

{
  uchar uVar1;
  byte bVar2;
  byte bVar3;
  uchar uVar4;
  
  uVar4 = f33_profile_first_validity[slot];
  uVar1 = f33_profile_observation_published[slot];
  bVar2 = f33_profile_first_refresh_counter[slot];
  bVar3 = f33_profile_first_refresh_counter_copy[slot];
  if (uVar4 == '\0') {
    if ((bVar2 < 100) && (uVar1 != 'Z')) {
      bVar2 = f33_profile_first_refresh_counter_copy[slot] + 1;
      bVar3 = bVar2;
    }
    else {
      f33_retain_first_control_profile(slot);
      if (uVar1 == 'Z') {
        uVar4 = 'Z';
      }
      else {
        uVar4 = '\0';
      }
      bVar2 = 0;
      bVar3 = 0;
    }
  }
  f33_profile_first_refresh_counter[slot] = bVar2;
  f33_profile_first_refresh_counter_copy[slot] = bVar3;
  f33_profile_first_validity[slot] = uVar4;
  return;
}



/* Copy rank1 profile to rank2 before replacing rank1 with working. Applies to sixteen halfword, two
   word and seven byte planes; validity/age markers are not shifted. */

void f33_promote_ranked_control_profile(uchar slot)

{
  uint uVar1;
  
  uVar1 = (uint)slot;
  f33_profile_retained_capture_value[uVar1 + 10] = f33_profile_retained_capture_value[uVar1 + 5];
  f33_profile_retained_received_composite[uVar1 + 10] =
       f33_profile_retained_received_composite[uVar1 + 5];
  f33_profile_retained_integrated_source[uVar1 + 10] =
       f33_profile_retained_integrated_source[uVar1 + 5];
  f33_profile_retained_elapsed_groups[uVar1 + 10] = f33_profile_retained_elapsed_groups[uVar1 + 5];
  f33_profile_retained_scaled_f228[uVar1 + 10] = f33_profile_retained_scaled_f228[uVar1 + 5];
  f33_profile_retained_source_u16_max[uVar1 + 10] = f33_profile_retained_source_u16_max[uVar1 + 5];
  f33_profile_retained_source_u16_mean[uVar1 + 10] = f33_profile_retained_source_u16_mean[uVar1 + 5]
  ;
  f33_profile_retained_f1c6_max[uVar1 + 10] = f33_profile_retained_f1c6_max[uVar1 + 5];
  f33_profile_retained_f1c6_mean[uVar1 + 10] = f33_profile_retained_f1c6_mean[uVar1 + 5];
  f33_profile_retained_f1c8_max[uVar1 + 10] = f33_profile_retained_f1c8_max[uVar1 + 5];
  f33_profile_retained_f1c8_mean[uVar1 + 10] = f33_profile_retained_f1c8_mean[uVar1 + 5];
  f33_profile_retained_f1ca_max[uVar1 + 10] = f33_profile_retained_f1ca_max[uVar1 + 5];
  f33_profile_retained_f1ca_mean[uVar1 + 10] = f33_profile_retained_f1ca_mean[uVar1 + 5];
  f33_profile_retained_scaled_ae5c_max[uVar1 + 10] = f33_profile_retained_scaled_ae5c_max[uVar1 + 5]
  ;
  f33_profile_retained_scaled_ae5c_min[uVar1 + 10] = f33_profile_retained_scaled_ae5c_min[uVar1 + 5]
  ;
  f33_profile_retained_scaled_b054_max[uVar1 + 10] = f33_profile_retained_scaled_b054_max[uVar1 + 5]
  ;
  f33_profile_retained_scaled_b054_mean[uVar1 + 10] =
       f33_profile_retained_scaled_b054_mean[uVar1 + 5];
  f33_profile_retained_route31_scalar[uVar1 + 10] = f33_profile_retained_route31_scalar[uVar1 + 5];
  f33_profile_retained_metadata_0[uVar1 + 10] = f33_profile_retained_metadata_0[uVar1 + 5];
  f33_profile_retained_metadata_1[uVar1 + 10] = f33_profile_retained_metadata_1[uVar1 + 5];
  f33_profile_retained_metadata_2[uVar1 + 10] = f33_profile_retained_metadata_2[uVar1 + 5];
  f33_profile_retained_metadata_3[uVar1 + 10] = f33_profile_retained_metadata_3[uVar1 + 5];
  f33_profile_retained_metadata_4[uVar1 + 10] = f33_profile_retained_metadata_4[uVar1 + 5];
  f33_profile_retained_metadata_5[uVar1 + 10] = f33_profile_retained_metadata_5[uVar1 + 5];
  f33_profile_retained_metadata_6[uVar1 + 10] = f33_profile_retained_metadata_6[uVar1 + 5];
  f33_profile_retained_capture_value[uVar1 + 5] = f33_profile_working_capture_value[uVar1];
  f33_profile_retained_received_composite[uVar1 + 5] = f33_profile_working_received_composite[uVar1]
  ;
  f33_profile_retained_integrated_source[uVar1 + 5] = f33_profile_working_integrated_source[uVar1];
  f33_profile_retained_elapsed_groups[uVar1 + 5] = f33_profile_working_elapsed_groups[uVar1];
  f33_profile_retained_scaled_f228[uVar1 + 5] = f33_profile_working_scaled_f228[uVar1];
  f33_profile_retained_source_u16_max[uVar1 + 5] = f33_profile_working_source_u16_max[uVar1];
  f33_profile_retained_source_u16_mean[uVar1 + 5] = f33_profile_working_source_u16_mean[uVar1];
  f33_profile_retained_f1c6_max[uVar1 + 5] = f33_profile_working_f1c6_max[uVar1];
  f33_profile_retained_f1c6_mean[uVar1 + 5] = f33_profile_working_f1c6_mean[uVar1];
  f33_profile_retained_f1c8_max[uVar1 + 5] = f33_profile_working_f1c8_max[uVar1];
  f33_profile_retained_f1c8_mean[uVar1 + 5] = f33_profile_working_f1c8_mean[uVar1];
  f33_profile_retained_f1ca_max[uVar1 + 5] = f33_profile_working_f1ca_max[uVar1];
  f33_profile_retained_f1ca_mean[uVar1 + 5] = f33_profile_working_f1ca_mean[uVar1];
  f33_profile_retained_scaled_ae5c_max[uVar1 + 5] = f33_profile_working_scaled_ae5c_max[uVar1];
  f33_profile_retained_scaled_ae5c_min[uVar1 + 5] = f33_profile_working_scaled_ae5c_min[uVar1];
  f33_profile_retained_scaled_b054_max[uVar1 + 5] = f33_profile_working_scaled_b054_max[uVar1];
  f33_profile_retained_scaled_b054_mean[uVar1 + 5] = f33_profile_working_scaled_b054_mean[uVar1];
  f33_profile_retained_route31_scalar[uVar1 + 5] = f33_profile_working_route31_scalar[uVar1];
  f33_profile_retained_metadata_0[uVar1 + 5] = f33_profile_working_metadata_0[uVar1];
  f33_profile_retained_metadata_1[uVar1 + 5] = f33_profile_working_metadata_1[uVar1];
  f33_profile_retained_metadata_2[uVar1 + 5] = f33_profile_working_metadata_2[uVar1];
  f33_profile_retained_metadata_3[uVar1 + 5] = f33_profile_working_metadata_3[uVar1];
  f33_profile_retained_metadata_4[uVar1 + 5] = f33_profile_working_metadata_4[uVar1];
  f33_profile_retained_metadata_5[uVar1 + 5] = f33_profile_working_metadata_5[uVar1];
  f33_profile_retained_metadata_6[uVar1 + 5] = f33_profile_working_metadata_6[uVar1];
  return;
}



/* Replace only rank2 with working profile. Does not alter rank1 or first bank; common validity/age
   are not recorded per generation. */

void f33_replace_second_ranked_control_profile(uchar slot)

{
  uint uVar1;
  
  uVar1 = (uint)slot;
  f33_profile_retained_capture_value[uVar1 + 10] = f33_profile_working_capture_value[uVar1];
  f33_profile_retained_received_composite[uVar1 + 10] =
       f33_profile_working_received_composite[uVar1];
  f33_profile_retained_integrated_source[uVar1 + 10] = f33_profile_working_integrated_source[uVar1];
  f33_profile_retained_elapsed_groups[uVar1 + 10] = f33_profile_working_elapsed_groups[uVar1];
  f33_profile_retained_scaled_f228[uVar1 + 10] = f33_profile_working_scaled_f228[uVar1];
  f33_profile_retained_source_u16_max[uVar1 + 10] = f33_profile_working_source_u16_max[uVar1];
  f33_profile_retained_source_u16_mean[uVar1 + 10] = f33_profile_working_source_u16_mean[uVar1];
  f33_profile_retained_f1c6_max[uVar1 + 10] = f33_profile_working_f1c6_max[uVar1];
  f33_profile_retained_f1c6_mean[uVar1 + 10] = f33_profile_working_f1c6_mean[uVar1];
  f33_profile_retained_f1c8_max[uVar1 + 10] = f33_profile_working_f1c8_max[uVar1];
  f33_profile_retained_f1c8_mean[uVar1 + 10] = f33_profile_working_f1c8_mean[uVar1];
  f33_profile_retained_f1ca_max[uVar1 + 10] = f33_profile_working_f1ca_max[uVar1];
  f33_profile_retained_f1ca_mean[uVar1 + 10] = f33_profile_working_f1ca_mean[uVar1];
  f33_profile_retained_scaled_ae5c_max[uVar1 + 10] = f33_profile_working_scaled_ae5c_max[uVar1];
  f33_profile_retained_scaled_ae5c_min[uVar1 + 10] = f33_profile_working_scaled_ae5c_min[uVar1];
  f33_profile_retained_scaled_b054_max[uVar1 + 10] = f33_profile_working_scaled_b054_max[uVar1];
  f33_profile_retained_scaled_b054_mean[uVar1 + 10] = f33_profile_working_scaled_b054_mean[uVar1];
  f33_profile_retained_route31_scalar[uVar1 + 10] = f33_profile_working_route31_scalar[uVar1];
  f33_profile_retained_metadata_0[uVar1 + 10] = f33_profile_working_metadata_0[uVar1];
  f33_profile_retained_metadata_1[uVar1 + 10] = f33_profile_working_metadata_1[uVar1];
  f33_profile_retained_metadata_2[uVar1 + 10] = f33_profile_working_metadata_2[uVar1];
  f33_profile_retained_metadata_3[uVar1 + 10] = f33_profile_working_metadata_3[uVar1];
  f33_profile_retained_metadata_4[uVar1 + 10] = f33_profile_working_metadata_4[uVar1];
  f33_profile_retained_metadata_5[uVar1 + 10] = f33_profile_working_metadata_5[uVar1];
  f33_profile_retained_metadata_6[uVar1 + 10] = f33_profile_working_metadata_6[uVar1];
  return;
}



/* OnlyB4AD5A considers signed504 magnitude with abs(-32768)=32767. Strictly above first rank shifts
   first to second; otherwise strictly above second replaces second. Ties may populate second but do
   not replace an equal-ranked record. */

void f33_rank_control_profile_magnitude(uchar slot)

{
  short sVar1;
  short sVar2;
  short sVar3;
  int iVar4;
  int iVar5;
  short sVar6;
  int iVar7;
  
  sVar2 = f33_profile_published_observation[slot];
  iVar5 = (int)sVar2;
  sVar1 = f33_profile_rank1_comparison_value[slot];
  iVar7 = (int)sVar1;
  sVar3 = f33_profile_rank2_comparison_value[slot];
  iVar4 = (int)sVar3;
  if (iVar5 + 0x7fff < 0 == (-1 < iVar5 && iVar5 + 0x7fff < 0) && iVar5 != -0x7fff) {
    if (iVar5 < 0) {
      iVar5 = (int)-sVar2;
    }
  }
  else {
    iVar5 = 0x7fff;
  }
  if (iVar7 + 0x7fff < 0 == (-1 < iVar7 && iVar7 + 0x7fff < 0) && iVar7 != -0x7fff) {
    if (iVar7 < 0) {
      iVar7 = (int)-sVar1;
    }
  }
  else {
    iVar7 = 0x7fff;
  }
  if (iVar4 + 0x7fff < 0 == (-1 < iVar4 && iVar4 + 0x7fff < 0) && iVar4 != -0x7fff) {
    if (iVar4 < 0) {
      iVar4 = (int)-sVar3;
    }
  }
  else {
    iVar4 = 0x7fff;
  }
  sVar6 = sVar1;
  if (f33_profile_observation_published[slot] == 'Z') {
    if (iVar7 - iVar5 < 0 == (iVar7 < 0 != iVar5 < 0 && iVar5 < 0 == iVar7 - iVar5 < 0)) {
      if (iVar4 - iVar5 < 0 != (iVar4 < 0 != iVar5 < 0 && iVar5 < 0 == iVar4 - iVar5 < 0)) {
        f33_replace_second_ranked_control_profile(slot);
        sVar3 = sVar2;
      }
    }
    else {
      f33_promote_ranked_control_profile(slot);
      sVar6 = sVar2;
      sVar3 = sVar1;
    }
  }
  f33_profile_rank1_comparison_value[slot] = sVar6;
  f33_profile_rank2_comparison_value[slot] = sVar3;
  return;
}



/* Refresh shared scalars once; for slots0..4 update aggregates, build working row, update
   first-profile retention and rank candidate. Foreground captured mode>=0100 and cadence bit1;
   qualification root has a narrower mode gate. */

void f33_run_control_profile_retention(void)

{
  uchar slot;
  uint uVar1;
  
  f33_refresh_profile_scaled_word();
  f33_refresh_profile_received_composite();
  uVar1 = 0;
  do {
    slot = (uchar)uVar1;
    f33_update_control_profile_aggregates(slot);
    f33_refresh_control_profile_working(slot);
    f33_update_first_control_profile_retention(slot);
    f33_rank_control_profile_magnitude(slot);
    uVar1 = uVar1 + 1;
  } while (uVar1 < 5);
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_ba8ac(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_ba8ae(void)

{
  return;
}



/* WARNING: Removing unreachable block (ram,0x000ba900) */
/* WARNING: Removing unreachable block (ram,0x000ba8f0) */

void FUN_000ba8b0(void)

{
  int iVar1;
  uint uVar2;
  
  iVar1 = -DAT_febeafe8;
  uVar2 = (uint)(DAT_febeb138 >> 2);
  if (uVar2 != 0) {
    if (iVar1 + -0x7fffff < 0 == (iVar1 < 0 && -1 < iVar1 + -0x7fffff)) {
      iVar1 = 0x7fffff;
    }
    if (iVar1 + 0x7fffff < 0 != (-1 < iVar1 && iVar1 + 0x7fffff < 0)) {
      iVar1 = -0x7fffff;
    }
    iVar1 = iVar1 << 8;
    if (uVar2 != 0) {
      if (iVar1 == -0x80000000 && uVar2 == 0xffffffff) {
        iVar1 = -0x80000000;
      }
      else {
        iVar1 = iVar1 / (int)uVar2;
      }
    }
    iVar1 = ((iVar1 / 4) * 0x188b) / 0x4000;
    if (iVar1 + -0x7fff < 0 == (iVar1 < 0 && -1 < iVar1 + -0x7fff)) {
      iVar1 = 0x7fff;
    }
    if (iVar1 + 0x8000 < 0 == (-1 < iVar1 && iVar1 + 0x8000 < 0)) {
      DAT_febebca6 = (undefined2)iVar1;
    }
    else {
      DAT_febebca6 = 0x8000;
    }
  }
  if ((DAT_febeb1a4 == '\x11') && (DAT_febeb079 == '\0')) {
    if (((DAT_000aee28 <= DAT_febeb080) && (DAT_febeb080 <= DAT_000aee2a)) ||
       ((DAT_000aee2c <= DAT_febeb086 && (DAT_febeb086 <= DAT_000aee2e)))) {
      DAT_febebca4 = 0;
      return;
    }
    if (DAT_000aee2c <= DAT_febeb088) {
      DAT_febebca4 = DAT_000aee2e < DAT_febeb088;
      return;
    }
  }
  DAT_febebca4 = 1;
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_ba960(void)

{
  return;
}



/* Clear owner5 request/accumulator/release state to0; BCAB=5A. Restrictive entry state, not
   nominal. */

void f33_reset_owner5_release_state(void)

{
  DAT_febebca8 = 0;
  DAT_febebcac = 0;
  DAT_febebcb8 = 0;
  DAT_febebca9 = 0;
  DAT_febebcae = 0;
  DAT_febebcb0 = 0;
  DAT_febebcb4 = 0;
  DAT_febebcaa = 0;
  DAT_febebcab = 0x5a;
  return;
}



/* Seed on first use from BCCC; retain k950 and unsigned16.16 decay toward0; snap<=128. Return full
   unsigned R10. */

uint f33_decay_owner5_limit_request(void)

{
  ushort uVar1;
  char cVar2;
  uint32_t puVar3;
  uint uVar4;
  char cVar5;
  uint coefficient;
  ushort uStack_22;
  uint uStack_20;
  ushort auStack_1c [2];
  int iStack_18;
  
  cVar2 = DAT_febeb20f;
  puVar3 = 0xfebeb800u;
  auStack_1c[0] = DAT_febebcb0;
  auStack_1c[1] = 0;
  iStack_18 = DAT_febebcb4;
  coefficient = DAT_febebcb8;
  cVar5 = DAT_febebca9;
  if (DAT_febebca9 == '\0') {
    uVar1 = DAT_000af030;
    if (DAT_febebee2 <= DAT_000af032) {
      uVar1 = DAT_000af02e;
    }
    uStack_22 = DAT_febebccc;
    auStack_1c[0] = DAT_febebccc;
    cVar5 = 'Z';
    coefficient = (uint)uVar1 * 0x32;
    iStack_18 = (uint)DAT_febebccc << 0x10;
  }
  f33_filter_unsigned_sample_accumulator(auStack_1c,coefficient,&uStack_22,&uStack_20);
  uVar1 = DAT_000af02a;
  if (cVar2 == 'Z') {
    uVar1 = DAT_000af02c;
  }
  uVar4 = (uint)uStack_22;
  if (uVar4 <= uVar1) {
    uStack_20 = 0;
    uVar4 = 0;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(0x4a8))))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(0x4a9))))) = cVar5;
  (*((uint *)camry_host_ptr((uint32_t)(puVar3 + 0x4b8)))) = coefficient;
  (*((uint *)camry_host_ptr((uint32_t)(puVar3 + 0x4b4)))) = uStack_20;
  return uVar4;
}



/* Use low16 target; conditional hold or fast/ordinary quadratic release, mode-change rebase. Reset
   decay-init and reseed decayaccumulator from returned request. */

uint f33_release_owner5_limit_request(uint target)

{
  int iVar1;
  uint uVar2;
  int iVar3;
  uint uVar4;
  uint uVar5;
  uint uVar6;
  char cVar7;
  uint uVar8;
  
  uVar2 = target & 0xffff;
  iVar1 = (int)DAT_febeb054;
  uVar8 = (uint)DAT_febebcb0;
  uVar5 = (uint)DAT_febebcae;
  uVar6 = (uint)DAT_febebcac;
  if (iVar1 + 0x7fff < 0 == (-1 < iVar1 && iVar1 + 0x7fff < 0) && iVar1 != -0x7fff) {
    if (iVar1 < 0) {
      iVar1 = (int)-DAT_febeb054;
    }
  }
  else {
    iVar1 = 0x7fff;
  }
  if (uVar8 < uVar2) {
    iVar3 = (int)DAT_000af026;
    if (((DAT_febebede < DAT_000af028) && (DAT_febebef0 == '\x11')) || (DAT_febeb118 == 'Z')) {
      cVar7 = '\x02';
      uVar4 = f33_owner5_fast_release_coefficient;
    }
    else {
      if ((iVar1 - iVar3 < 0 != (iVar1 < 0 != iVar3 < 0 && iVar3 < 0 == iVar1 - iVar3 < 0) ||
           iVar1 == iVar3) && (uVar8 <= DAT_000af024)) {
        cVar7 = '\0';
        uVar2 = uVar8;
        goto LAB_000baac4;
      }
      cVar7 = '\x01';
      uVar4 = f33_owner5_normal_release_coefficient;
    }
    if (cVar7 != DAT_febebca8) {
      uVar6 = 0;
      uVar5 = uVar8;
    }
    if (uVar6 < 0xffff) {
      uVar6 = uVar6 + 1 & 0xffff;
    }
    if (((int)((ulonglong)uVar4 * (ulonglong)(uVar6 * uVar6) >> 0x20) == 0) &&
       (uVar8 = (uVar6 * uVar6 * uVar4 >> 0x10) + uVar5, (int)(uVar8 - uVar2) < 0 || uVar8 == uVar2)
       ) {
      uVar2 = uVar8 & 0xffff;
    }
  }
  else {
    cVar7 = '\0';
  }
LAB_000baac4:
  DAT_febebca8 = cVar7;
  DAT_febebcac = (short)uVar6;
  DAT_febebcae = (short)uVar5;
  DAT_febebcb4 = uVar2 << 0x10;
  DAT_febebca9 = 0;
  return uVar2;
}



/* Publish owner5 from active decay, conditional release or retained hold. Family0500 with
   alreadyzero skips decay; BCAA active and BCAB report markers remain distinct. */

void f33_publish_owner5_limit_request(void)

{
  undefined *puVar1;
  undefined1 uVar2;
  undefined1 uVar3;
  uint uVar4;
  
  puVar1 = ((undefined *)camry_host_ptr(0xfebeb800u));
  uVar2 = 0;
  uVar4 = (uint)DAT_febebcb0;
  if (((DAT_febeb20e == '\x11') || (DAT_febeb20e == '\"')) || (DAT_febeb1bc == 'Z')) {
    if (((DAT_febeb11a & 0xff00) != 0x500) || (puVar1 = ((undefined *)camry_host_ptr(0xfebeb800u)), uVar4 != 0)) {
      puVar1 = ((undefined *)camry_host_ptr(0xfebeb800u));
      uVar4 = f33_decay_owner5_limit_request();
    }
    uVar2 = 0x5a;
    uVar3 = uVar2;
  }
  else {
    uVar3 = DAT_febebcab;
    if (DAT_febeb1a4 == '\x11') {
      puVar1 = ((undefined *)camry_host_ptr(0xfebeb800u));
      uVar4 = f33_release_owner5_limit_request(0x569a);
      uVar3 = 0xa5;
    }
  }
  if (0x5699 < uVar4) {
    uVar3 = 0;
  }
  f33_set_current_limit_request(5,(ushort)uVar4);
  *(ushort *)(puVar1 + 0x4b0) = (ushort)uVar4;
  puVar1[0x4ab] = uVar3;
  puVar1[0x4aa] = uVar2;
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_bab56(void)

{
  return;
}



/* Set owner4 previous/base22170 and accumulator22170<<16; clear release mode, control mode and
   count. */

void f33_reset_owner4_release_state(void)

{
  DAT_febebcc0 = 0x569a;
  DAT_febebcc2 = 0x569a;
  DAT_febebcbc = 0;
  DAT_febebcbd = 0;
  DAT_febebcbe = 0;
  DAT_febebcc4 = 0x569a0000;
  return;
}



/* Release owner4 toward22170 with conditional hold, k115828/4666 and mode-change quadratic rebase;
   clear its decay accumulator. */

uint f33_release_owner4_limit_request(void)

{
  int iVar1;
  int iVar2;
  uint uVar3;
  uint uVar4;
  uint uVar5;
  char cVar6;
  uint uVar7;
  
  iVar1 = (int)DAT_febeb054;
  uVar7 = (uint)DAT_febebcc2;
  uVar4 = (uint)DAT_febebcc0;
  uVar5 = (uint)DAT_febebcbe;
  if (iVar1 + 0x7fff < 0 == (-1 < iVar1 && iVar1 + 0x7fff < 0) && iVar1 != -0x7fff) {
    if (iVar1 < 0) {
      iVar1 = (int)-DAT_febeb054;
    }
  }
  else {
    iVar1 = 0x7fff;
  }
  if (uVar7 < 0x569a) {
    iVar2 = (int)DAT_000af03e;
    if ((DAT_febebee2 < DAT_000af040) && (DAT_febebef0 == '\x11')) {
      cVar6 = '\x02';
      uVar3 = f33_owner4_fast_release_coefficient;
    }
    else {
      if ((iVar1 - iVar2 < 0 != (iVar1 < 0 != iVar2 < 0 && iVar2 < 0 == iVar1 - iVar2 < 0) ||
           iVar1 == iVar2) && (uVar7 <= DAT_000af03c)) {
        cVar6 = '\0';
        goto LAB_000bac1e;
      }
      cVar6 = '\x01';
      uVar3 = f33_owner4_normal_release_coefficient;
    }
    if (cVar6 != DAT_febebcbc) {
      uVar5 = 0;
      uVar4 = uVar7;
    }
    if (uVar5 < 0xffff) {
      uVar5 = uVar5 + 1 & 0xffff;
    }
    if (((int)((ulonglong)uVar3 * (ulonglong)(uVar5 * uVar5) >> 0x20) == 0) &&
       (uVar7 = (uVar5 * uVar5 * uVar3 >> 0x10) + uVar4,
       (int)(uVar7 - 0x569a) < 0 || uVar7 == 0x569a)) {
      uVar7 = uVar7 & 0xffff;
    }
    else {
      uVar7 = 0x569a;
    }
  }
  else {
    cVar6 = '\0';
    uVar7 = 0x569a;
  }
LAB_000bac1e:
  DAT_febebcc4 = 0;
  DAT_febebcbc = cVar6;
  DAT_febebcbe = (short)uVar5;
  DAT_febebcc0 = (short)uVar4;
  return uVar7;
}



/* Clear release mode and accumulator, return full22170; accumulator is0, not nominal<<16. */

uint f33_force_owner4_nominal_request(void)

{
  DAT_febebcbc = 0;
  DAT_febebcc4 = 0;
  return 0x569a;
}



/* Use low16 coefficient*50; mismatched previous/high16 accumulator reseeds from common BCCC, filter
   toward0 and snap<=128. */

uint f33_decay_owner4_limit_request(uint coefficient)

{
  uint32_t puVar1;
  uint uVar2;
  ushort uStack_12;
  uint uStack_10;
  ushort auStack_c [2];
  uint uStack_8;
  
  puVar1 = 0xfebeb800u;
  auStack_c[1] = 0;
  uStack_8 = DAT_febebcc4;
  auStack_c[0] = DAT_febebcc2;
  if (DAT_febebcc4 >> 0x10 != (uint)DAT_febebcc2) {
    auStack_c[0] = DAT_febebccc;
    uStack_8 = (uint)DAT_febebccc << 0x10;
  }
  f33_filter_unsigned_sample_accumulator
            (auStack_c,(coefficient & 0xffff) * 0x32,&uStack_12,&uStack_10);
  uVar2 = (uint)uStack_12;
  if (uVar2 <= DAT_000af042) {
    uStack_10 = 0;
    uVar2 = 0;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x4bc))))) = 0;
  (*((uint *)camry_host_ptr((uint32_t)(puVar1 + 0x4c4)))) = uStack_10;
  return uVar2;
}



/* Clear release mode and decayaccumulator and return0. */

uint f33_force_owner4_zero_request(void)

{
  DAT_febebcbc = 0;
  DAT_febebcc4 = 0;
  return 0;
}



/* BCBD1 nominal,2 k250 decay,3 k6550 decay,4 zero,others conditional quadratic release; publish
   owner4 and BCC2. */

void f33_publish_owner4_limit_request(void)

{
  uint32_t puVar1;
  ushort uVar2;
  uint uVar3;
  
  puVar1 = 0xfebeb800u;
  if (DAT_febebcbd != '\0') {
    if (DAT_febebcbd == '\x01') {
      uVar3 = f33_force_owner4_nominal_request();
      uVar2 = (ushort)uVar3;
      goto LAB_000bace6;
    }
    uVar2 = DAT_000af044;
    if ((DAT_febebcbd == '\x02') || (uVar2 = DAT_000af046, DAT_febebcbd == '\x03')) {
      uVar3 = f33_decay_owner4_limit_request((uint)uVar2);
      uVar2 = (ushort)uVar3;
      goto LAB_000bace6;
    }
    if (DAT_febebcbd == '\x04') {
      uVar3 = f33_force_owner4_zero_request();
      uVar2 = (ushort)uVar3;
      goto LAB_000bace6;
    }
  }
  uVar3 = f33_release_owner4_limit_request();
  uVar2 = (ushort)uVar3;
LAB_000bace6:
  f33_set_current_limit_request(4,uVar2);
  (*((ushort *)camry_host_ptr((uint32_t)(puVar1 + 0x4c2)))) = uVar2;
  return;
}



/* Store low8 mode toBCBD. Direct reference only from thunkFDFC6; no normal caller inferred. */

void f33_set_owner4_limit_mode(uint mode)

{
  DAT_febebcbd = (char)mode;
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_bacfe(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_bad00(void)

{
  return;
}



/* BCC8=symmetric sat_abs(AFE2), BCCA=sat_abs(AFE0), BCCC=min those two. Distinct owner8 seed versus
   common owner4/5 seed. */

void f33_stage_absolute_limit_seeds(void)

{
  int iVar1;
  int iVar2;
  
  iVar1 = (int)DAT_febeafe2;
  iVar2 = (int)DAT_febeafe0;
  if (iVar1 + 0x7fff < 0 == (-1 < iVar1 && iVar1 + 0x7fff < 0) && iVar1 != -0x7fff) {
    if (iVar1 < 0) {
      iVar1 = (int)-DAT_febeafe2;
    }
  }
  else {
    iVar1 = 0x7fff;
  }
  if (iVar2 + 0x7fff < 0 == (-1 < iVar2 && iVar2 + 0x7fff < 0) && iVar2 != -0x7fff) {
    if (iVar2 < 0) {
      iVar2 = (int)-DAT_febeafe0;
    }
  }
  else {
    iVar2 = 0x7fff;
  }
  DAT_febebccc = (undefined2)iVar1;
  DAT_febebcc8 = DAT_febebccc;
  DAT_febebcca = (short)iVar2;
  if (iVar2 - iVar1 < 0 != (iVar2 < 0 != iVar1 < 0 && iVar1 < 0 == iVar2 - iVar1 < 0)) {
    DAT_febebccc = (short)iVar2;
  }
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_bad44(void)

{
  return;
}



/* Set owner8 request/base22170, accumulatornominal, mode/count0. Does not initialize active
   delayBCD8. */

void f33_reset_owner8_release_state(void)

{
  DAT_febebcd4 = 0x569a;
  DAT_febebcd6 = 0x569a;
  DAT_febebcd0 = 0;
  DAT_febebcd2 = 0;
  DAT_febebcdc = 0x569a0000;
  return;
}



/* After calibrated unsigned delay, filter toward B08A; coherency mismatch seeds BCC8; snap when
   filtered output<target+128. Exact coefficient/delay0 produces B08A immediately. */

uint f33_follow_owner8_qualification_floor(uint coefficient)

{
  uint32_t puVar1;
  uint uVar2;
  uint uVar3;
  ushort uVar4;
  ushort uStack_1e;
  uint uStack_1c;
  ushort uStack_18;
  ushort uStack_16;
  uint uStack_14;
  
  uVar4 = DAT_febebcd8;
  puVar1 = 0xfebeb800u;
  if (DAT_febebcd8 < DAT_000aef9c) {
    uVar2 = (uint)DAT_febebcd6;
    uVar4 = DAT_febebcd8 + 1;
  }
  else {
    uVar3 = (uint)DAT_febeb08a;
    uStack_14 = DAT_febebcdc;
    uStack_16 = DAT_febeb08a;
    uStack_18 = DAT_febebcd6;
    if (DAT_febebcdc >> 0x10 != (uint)DAT_febebcd6) {
      uStack_18 = DAT_febebcc8;
      uStack_14 = (uint)DAT_febebcc8 << 0x10;
    }
    puVar1 = 0xfebeb800u;
    f33_filter_unsigned_sample_accumulator
              (&uStack_18,(coefficient & 0xffff) * 0x32,&uStack_1e,&uStack_1c);
    uVar2 = (uint)uStack_1e;
    if ((uint)uStack_1e < DAT_000aef96 + uVar3) {
      uStack_1c = uVar3 << 0x10;
      uVar2 = uVar3;
    }
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x4d0))))) = 0;
    (*((uint *)camry_host_ptr((uint32_t)(puVar1 + 0x4dc)))) = uStack_1c;
  }
  (*((ushort *)camry_host_ptr((uint32_t)(puVar1 + 0x4d8)))) = uVar4;
  return uVar2;
}



/* When channelsclear, conditionally hold or quadraticrelease toward22170 using k117028/4663; clear
   decayaccumulator anddelay. */

uint f33_release_owner8_limit_request(void)

{
  int iVar1;
  uint uVar2;
  uint uVar3;
  uint uVar4;
  char cVar5;
  int iVar6;
  uint uVar7;
  
  iVar1 = (int)DAT_febeb054;
  uVar7 = (uint)DAT_febebcd6;
  uVar3 = (uint)DAT_febebcd4;
  uVar4 = (uint)DAT_febebcd2;
  if (iVar1 + 0x7fff < 0 == (-1 < iVar1 && iVar1 + 0x7fff < 0) && iVar1 != -0x7fff) {
    if (iVar1 < 0) {
      iVar1 = (int)-DAT_febeb054;
    }
  }
  else {
    iVar1 = 0x7fff;
  }
  if (uVar7 < 0x569a) {
    if ((DAT_febebee2 < DAT_000aef94) && (DAT_febebef0 == '\x11')) {
      cVar5 = '\x02';
      uVar2 = f33_owner8_fast_release_coefficient;
    }
    else {
      iVar6 = (int)DAT_000aef92;
      if ((iVar1 - iVar6 < 0 != (iVar1 < 0 != iVar6 < 0 && iVar6 < 0 == iVar1 - iVar6 < 0) ||
           iVar1 == iVar6) && (uVar7 <= DAT_000aef90)) {
        cVar5 = '\0';
        goto LAB_000bae8e;
      }
      cVar5 = '\x01';
      uVar2 = f33_owner8_normal_release_coefficient;
    }
    if (cVar5 != DAT_febebcd0) {
      uVar4 = 0;
      uVar3 = uVar7;
    }
    if (uVar4 < 0xffff) {
      uVar4 = uVar4 + 1 & 0xffff;
    }
    if (((int)((ulonglong)uVar2 * (ulonglong)(uVar4 * uVar4) >> 0x20) == 0) &&
       (uVar7 = (uVar4 * uVar4 * uVar2 >> 0x10) + uVar3,
       (int)(uVar7 - 0x569a) < 0 || uVar7 == 0x569a)) {
      uVar7 = uVar7 & 0xffff;
    }
    else {
      uVar7 = 0x569a;
    }
  }
  else {
    cVar5 = '\0';
    uVar7 = 0x569a;
  }
LAB_000bae8e:
  DAT_febebcdc = 0;
  DAT_febebcd0 = cVar5;
  DAT_febebcd2 = (short)uVar4;
  DAT_febebcd4 = (short)uVar3;
  DAT_febebcd8 = 0;
  return uVar7;
}



/* B082&3 chooses qualification-floor path; otherwise retained quadraticrelease. Publish owner8
   andBCD6. */

void f33_publish_owner8_limit_request(void)

{
  uint32_t puVar1;
  ushort limit;
  uint uVar2;
  
  puVar1 = 0xfebeb800u;
  if ((DAT_febeb082 & 3) == 0) {
    uVar2 = f33_release_owner8_limit_request();
    limit = (ushort)uVar2;
  }
  else {
    uVar2 = f33_follow_owner8_qualification_floor((uint)DAT_000aef98);
    limit = (ushort)uVar2;
  }
  f33_set_current_limit_request(8,limit);
  (*((ushort *)camry_host_ptr((uint32_t)(puVar1 + 0x4d6)))) = limit;
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_baee4(void)

{
  return;
}



/* Clear qualification/counters/baseline; target22170, persisted-derived admission default5A,
   initmarker0. BCF0 request reset is separateBB16C. */

void f33_reset_owner1_qualification_state(void)

{
  DAT_febebce2 = 0x5a;
  DAT_febebce0 = 0;
  DAT_febebce4 = 0;
  DAT_febebce5 = 0;
  DAT_febebce1 = 0;
  DAT_febebce3 = 0;
  DAT_febebce8 = 0x569a;
  DAT_febebce6 = 0;
  DAT_febebcec = 0;
  return;
}



/* Only F027=5A admits persisted-derived decision; set BCE2=5A iff F1E0==0 and signedF182<0, else0;
   publishBCE3=5A. */

void f33_initialize_owner1_persisted_admission(void)

{
  int iVar1;
  int iVar2;
  
  if (DAT_febef027 == 'Z') {
    if ((DAT_febef1e0 == 0) &&
       (iVar2 = (int)DAT_000af060, iVar1 = DAT_febef182 - iVar2,
       iVar1 < 0 != (DAT_febef182 < 0 != iVar2 < 0 && iVar2 < 0 == iVar1 < 0))) {
      DAT_febebce2 = 0x5a;
    }
    else {
      DAT_febebce2 = 0;
    }
    DAT_febebce3 = 0x5a;
  }
  return;
}



/* WARNING: Removing unreachable block (ram,0x000bb140) */
/* Retained states0/11/22/33 qualify signed snapshot relationships, enter/release counters and
   reversal; state22 maps F174 with AF06C and BEE2 gainAF084 into targetBCE8. Units unassigned. */

void f33_qualify_owner1_limit_state(void)

{
  short sVar1;
  ushort uVar2;
  int iVar3;
  uint32_t puVar4;
  int iVar5;
  int iVar6;
  int iVar7;
  short sVar8;
  int iVar9;
  char cVar10;
  byte bVar11;
  byte bVar12;
  char cVar13;
  short sStack_4a;
  int iStack_48;
  short sStack_44;
  short sStack_42;
  short sStack_40;
  ushort uStack_3e;
  int iStack_3c;
  int iStack_38;
  short sStack_34;
  ushort uStack_32;
  short sStack_30;
  short sStack_2e;
  
  puVar4 = 0xfebeb800u;
  if (DAT_febebce3 == '\0') {
    puVar4 = 0xfebeb800u;
    f33_initialize_owner1_persisted_admission();
  }
  sStack_34 = (*((short *)camry_host_ptr((uint32_t)(puVar4 + 0x3974))));
  iStack_38 = (*((int *)camry_host_ptr((uint32_t)(puVar4 + -0x80c))));
  iVar9 = 0;
  uStack_32 = (*((ushort *)camry_host_ptr((uint32_t)(puVar4 + -0x77e))));
  sStack_30 = (*((short *)camry_host_ptr((uint32_t)(puVar4 + -0x820))));
  sStack_2e = (*((short *)camry_host_ptr((uint32_t)(puVar4 + -0x824))));
  sStack_44 = (*((short *)camry_host_ptr((uint32_t)(puVar4 + 0x4e8))));
  cVar13 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(0x4e0)))));
  bVar12 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(0x4e4)))));
  bVar11 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(0x4e5)))));
  cVar10 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(0x4e1)))));
  uVar2 = (*((ushort *)camry_host_ptr((uint32_t)(puVar4 + 0x6e2))));
  sVar1 = (*((short *)camry_host_ptr((uint32_t)(puVar4 + -0x7ac))));
  iVar3 = (int)(*((short *)camry_host_ptr((uint32_t)(puVar4 + -0x7f4))));
  sVar8 = (*((short *)camry_host_ptr((uint32_t)(puVar4 + 0x4e6))));
  iVar7 = (*((int *)camry_host_ptr((uint32_t)(puVar4 + 0x4ec))));
  if (((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x65c))))) == '\x11') && ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x658))))) == '\0')) {
    if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x6ee))))) == 'Z') {
LAB_000bafde:
      cVar10 = '\0';
      cVar13 = '\0';
      bVar11 = 0;
      bVar12 = 0;
      goto LAB_000baff6;
    }
    if (cVar10 != 'Z') {
      if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(0x4e2))))) != '\0') {
        iVar6 = (int)DAT_000af05a;
        iVar5 = (int)sStack_34;
        if (iVar5 - iVar6 < 0 != (iVar5 < 0 != iVar6 < 0 && iVar6 < 0 == iVar5 - iVar6 < 0) ||
            iVar5 == iVar6) goto LAB_000bafde;
      }
      cVar10 = 'Z';
    }
    if (DAT_000af056 < uVar2) goto LAB_000baff6;
  }
  else {
    cVar10 = '\0';
    cVar13 = '3';
    bVar12 = 0;
    bVar11 = 0;
    iVar3 = 0x569a;
LAB_000baff6:
    iVar5 = (int)DAT_000af0c6;
    if (iVar3 - iVar5 < 0 == (iVar3 < 0 != iVar5 < 0 && iVar5 < 0 == iVar3 - iVar5 < 0)) {
      cVar13 = '3';
      goto LAB_000bb150;
    }
  }
  if ((int)sVar8 * (int)sVar1 < 0) {
    iVar9 = 0x5a;
  }
  iStack_48 = iStack_38 - iVar7;
  FUN_000d1194(iStack_48,&iStack_48);
  FUN_000d1178((int)sVar1,&sStack_4a);
  FUN_000d1178((int)sStack_2e,&sStack_40);
  FUN_000d1178((int)sStack_30,&sStack_42);
  sVar8 = DAT_000af066;
  if ((uStack_32 & 3) == 0) {
    sVar8 = DAT_000af064;
  }
  iVar3 = (int)sVar8;
  if ((cVar13 == '\0') || (cVar13 == '3')) {
    iVar6 = (int)DAT_000af05e;
    iVar5 = sStack_4a - iVar6;
    if (iVar5 < 0 != (sStack_4a < 0 != iVar6 < 0 && iVar6 < 0 == iVar5 < 0)) {
LAB_000bb0ae:
      bVar12 = 0;
      goto LAB_000bb0b0;
    }
    if (bVar12 == 0) {
      bVar12 = 1;
      iVar7 = iStack_38;
      goto LAB_000bb0b0;
    }
    iVar5 = (int)DAT_000af058;
    if ((iStack_48 - iVar5 < 0 == (iStack_48 < 0 != iVar5 < 0 && iVar5 < 0 == iStack_48 - iVar5 < 0)
        ) && ((iVar6 = (int)DAT_000af062, iVar5 = sStack_40 - iVar6,
              iVar5 < 0 == (sStack_40 < 0 != iVar6 < 0 && iVar6 < 0 == iVar5 < 0) ||
              (iVar5 = sStack_42 - iVar3,
              iVar5 < 0 != (sStack_42 < 0 != iVar3 < 0 && iVar3 < 0 == iVar5 < 0)))))
    goto LAB_000bb0ae;
    if (bVar12 < DAT_000af054) {
      bVar12 = bVar12 + 1;
      goto LAB_000bb0b0;
    }
    cVar13 = '\x11';
LAB_000bb0b6:
    if (iStack_48 - DAT_000af068 < 0 ==
        (iStack_48 < 0 != DAT_000af068 < 0 && DAT_000af068 < 0 == iStack_48 - DAT_000af068 < 0)) {
      cVar13 = '\"';
    }
LAB_000bb0ce:
    iVar5 = (int)DAT_000af05c;
    iVar3 = sStack_4a - iVar5;
    if (iVar3 < 0 == (sStack_4a < 0 != iVar5 < 0 && iVar5 < 0 == iVar3 < 0)) {
      bVar11 = 0;
    }
    else if (bVar11 < DAT_000af055) {
      bVar11 = bVar11 + 1;
    }
    else {
      bVar12 = 0;
      bVar11 = 0;
      cVar13 = '\0';
    }
    if (iVar9 == 0x5a) {
      bVar12 = 0;
      bVar11 = 0;
      cVar13 = '\0';
    }
  }
  else {
LAB_000bb0b0:
    if (cVar13 == '\x11') goto LAB_000bb0b6;
    if (cVar13 == '\"') goto LAB_000bb0ce;
  }
  sVar8 = sVar1;
  if (cVar13 == '\"') {
    FUN_000d1de4(((undefined *)camry_host_ptr(0xaf06cu)),(int)sStack_34,&sStack_44);
    FUN_000d1ee0(((undefined *)camry_host_ptr(0xaf084u)),uVar2,&uStack_3e);
    iStack_3c = (int)((int)sStack_44 * (uint)uStack_3e) / 0x400;
    FUN_000d1d4e(iStack_3c,0x569a,&iStack_3c);
    sStack_44 = (short)iStack_3c;
  }
LAB_000bb150:
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(0x4e4))))) = bVar12;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(0x4e5))))) = bVar11;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(0x4e1))))) = cVar10;
  (*((short *)camry_host_ptr((uint32_t)(puVar4 + 0x4e8)))) = sStack_44;
  (*((short *)camry_host_ptr((uint32_t)(puVar4 + 0x4e6)))) = sVar8;
  (*((int *)camry_host_ptr((uint32_t)(puVar4 + 0x4ec)))) = iVar7;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(0x4e0))))) = cVar13;
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_bb16a(void)

{
  return;
}



/* Initialize retained requestBCF0 to22170 only. */

void f33_reset_owner1_limit_request(void)

{
  DAT_febebcf0 = 0x569a;
  return;
}



/* Use retained qualificationstate:0 +28 release,11 -28 decay,22 tiered13/10/4 decay or+28 recovery
   toward target,33 nominal. Narrow arithmetic before final signed clamp[0,22170], publish owner1.
   Native qualified owner1 decrease and release select different winners in real BB7FA reduction;
   independent owner6/9 publication remains distinct. */

void f33_publish_owner1_limit_request(void)

{
  short sVar1;
  short sVar2;
  uint32_t puVar3;
  short bound;
  int iVar4;
  int iVar5;
  short sStack_a;
  
  puVar3 = 0xfebeb800u;
  iVar4 = (int)DAT_febebcf0;
  iVar5 = (int)DAT_febebce8;
  sStack_a = DAT_febebcf0;
  sVar1 = DAT_000af0c6;
  if (DAT_febebce0 != '3') {
    if (DAT_febebce0 == '\0') {
      sVar1 = DAT_000af0c4 + DAT_febebcf0;
    }
    else if (DAT_febebce0 == '\x11') {
      sVar1 = DAT_febebcf0 - DAT_000af0b8;
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
             (iVar5 = (int)DAT_000af0c2, sVar1 = DAT_000af0bc, bound = DAT_febebce8,
             sVar2 = DAT_000af0c2, sStack_a = DAT_000af0be,
             iVar4 - iVar5 < 0 == (iVar4 < 0 != iVar5 < 0 && iVar5 < 0 == iVar4 - iVar5 < 0) &&
             iVar4 != iVar5)) {
            bound = sVar2;
            sStack_a = sVar1;
          }
          sStack_a = DAT_febebcf0 - sStack_a;
          f33_store_signed_halfword_max(sStack_a,bound,&sStack_a);
          sVar1 = sStack_a;
        }
        else {
          sStack_a = DAT_febebcf0 + DAT_000af0c4;
          f33_store_signed_halfword_min(sStack_a,DAT_febebce8,&sStack_a);
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
  f33_set_current_limit_request(1,(ushort)iVar4);
  (*((short *)camry_host_ptr((uint32_t)(puVar3 + 0x4f0)))) = sStack_a;
  return;
}



/* D1306resetofBCF4ten-bytestate. */

void f33_initialize_lifecycle_difference_monitor(void)

{
  f33_reset_application_latched_monitor(((F33LatchedMonitorState *)camry_host_ptr((uint32_t)((0xfebebcf4u)))));
  return;
}



/* SameD1306resetofBCF4; separateentryowner. */

void f33_reset_lifecycle_difference_monitor_entry(void)

{
  f33_reset_application_latched_monitor(((F33LatchedMonitorState *)camry_host_ptr((uint32_t)((0xfebebcf4u)))));
  return;
}



/* D1386(BCF4,AF050,AECA0),limits0/6; scheduledbyexistingmaskbit4. */

void f33_step_lifecycle_difference_monitor(void)

{
  f33_step_application_latched_monitor
            (((F33LatchedMonitorState *)camry_host_ptr((uint32_t)((0xfebebcf4u)))), ((F33MonitorLimits *)camry_host_ptr((uint32_t)((0xaf050u)))), ((F33TwoSidedMonitorCallbacks *)camry_host_ptr((uint32_t)((0xaeca0u)))));
  return;
}



/* B1A4!=11->44. Else signedconvertedB02CminusB00C>=1920,BEDE>1280,BEF0==11->22; otherwise11. No
   physicalunit or OEMmeaning inferred. */

uint f33_classify_lifecycle_conditioned_sample_difference(void)

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
    iVar6 = (int)DAT_febeb00c;
    FUN_000d1178((int)DAT_febeb02c,&sStack_12);
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



/* Latchdiagnosticstatusslot10through545DE, thenconditionallysubmitrecord8/capture800through51CF6.
   No directmoderequest. */

void f33_confirm_lifecycle_difference_diagnostic(void)

{
  ((void)(10), thunk_FUN_000545de());
  ((void)(8), (void)(800), thunk_FUN_00051cf6());
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_bb2f4(void)

{
  return;
}



/* Seed signed AFDC and unsignedB084 retained filters; nominal request/cap/candidates; clear
   markers, transition/family state. */

void f33_reset_owner6_calibration_envelope(void)

{
  DAT_febebd18 = 0x569a0000;
  DAT_febebd00 = 0;
  DAT_febebd01 = 0;
  DAT_febebd10 = DAT_febeafdc;
  DAT_febebd02 = 0;
  DAT_febebd2c = (int)DAT_febeafdc << 0x10;
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



/* Accept B30C55AAAA55 orAA5555AA; otherwise use exactfallbackAF1B8=AA5555AA. */

void f33_select_owner6_calibration_family(void)

{
  DAT_febebd20 = DAT_febeb30c;
  if ((DAT_febeb30c != 0x55aaaa55) && (DAT_febeb30c != -0x55aaaa56)) {
    DAT_febebd20 = DAT_000af1b8;
  }
  return;
}



/* WARNING: Removing unreachable block (ram,0x000bb42a) */
/* Opposite-sign AFDC/AFE0 dwell selects bypass marker; gated BEE2 hysteresis retains bank latch.
   Signed AFDC filter k30573 uses signedDIVQ65536. */

void f33_update_owner6_gate_and_axis_filter(void)

{
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
  short local_2c;
  short sStack_2a;
  
  uVar2 = DAT_febebee2;
  iVar1 = DAT_febebd2c;
  uVar10 = DAT_febebd02;
  puVar4 = 0xfebeb800u;
  iVar7 = (int)DAT_febeafe0;
  iVar3 = (int)DAT_000af178;
  iVar12 = (int)DAT_febeafdc;
  iVar9 = (int)DAT_febeafde;
  iVar8 = (int)DAT_febebd10;
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
  FUN_000d1178((int)DAT_febeb054,&local_2c);
  FUN_000d1178(iVar9,&sStack_2a);
  iVar3 = (int)DAT_000af17a;
  iVar7 = (int)local_2c;
  if (iVar7 - iVar3 < 0 != (iVar7 < 0 != iVar3 < 0 && iVar3 < 0 == iVar7 - iVar3 < 0) ||
      iVar7 == iVar3) {
    iVar3 = (int)DAT_000af17c;
    iVar7 = (int)sStack_2a;
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



/* WARNING: Removing unreachable block (ram,0x000bb6d6) */
/* WARNING: Removing unreachable block (ram,0x000bb656) */
/* WARNING: Removing unreachable block (ram,0x000bb670) */
/* Select real family/bank map pair and extrapolation, recordrawcandidate; signed cap/floor gives
   exactdesired22170. AF1760 immediate output with inclusive3 snap. Publish owner6. */

void f33_publish_owner6_calibration_envelope(void)

{
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
  short local_38;
  short sStack_36;
  short sStack_34;
  short sStack_32;
  short sStack_30;
  short sStack_2e;
  
  iVar5 = DAT_febebd30;
  iVar15 = DAT_febebd18;
  cVar1 = DAT_febebd00;
  puVar4 = 0xfebeb800u;
  sStack_34 = DAT_febebd12;
  sStack_2e = DAT_febebd06;
  sStack_32 = DAT_febebd14;
  uVar14 = (uint)DAT_febebd0a;
  sStack_30 = DAT_febebd0c;
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
  FUN_000d1178((int)DAT_febebd10,&sStack_36);
  if (cVar1 == 'Z') {
    iVar13 = 0x569a;
    goto LAB_000bb6ae;
  }
  FUN_000d1de4(puVar8,(int)sStack_36,&sStack_34);
  FUN_000d1de4(puVar7,(int)sStack_36,&sStack_32);
  if (uVar14 < uVar10) {
    iVar5 = (int)(uVar12 * (uVar14 - uVar10)) / 0x800;
    iVar13 = (int)sStack_32;
LAB_000bb696:
    iVar5 = iVar5 + iVar13;
  }
  else {
    if (uVar9 < uVar14) {
      iVar5 = (int)(uVar12 * (uVar14 - uVar9)) / 0x800;
      iVar13 = (int)sStack_34;
      goto LAB_000bb696;
    }
    iVar5 = (int)sStack_32;
    if (uVar9 != uVar10) {
      iVar2 = uVar9 - uVar10;
      iVar13 = (sStack_34 - iVar5) * (uVar14 - uVar10);
      if (iVar2 != 0) {
        if (iVar13 == -0x80000000 && iVar2 == -1) {
          iVar13 = -0x80000000;
        }
        else {
          iVar13 = iVar13 / iVar2;
        }
      }
      goto LAB_000bb696;
    }
  }
  iVar3 = (int)sStack_30;
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
    iVar3 = (int)sStack_2e << 0x10;
    iVar2 = iVar13 << 0x10;
  }
  else {
    iVar3 = (int)sStack_2e * uVar14;
    iVar2 = iVar13 * uVar14;
  }
  iVar2 = (iVar15 - iVar3) + iVar2;
  FUN_000d1178((int)(short)((short)(iVar2 / 0x10000) - (short)iVar13),&local_38);
  iVar3 = (int)DAT_000af180;
  iVar6 = (int)local_38;
  iVar15 = iVar2 / 0x10000;
  if (iVar6 - iVar3 < 0 != (iVar6 < 0 != iVar3 < 0 && iVar3 < 0 == iVar6 - iVar3 < 0) ||
      iVar6 == iVar3) {
    iVar2 = iVar13 << 0x10;
    iVar15 = iVar13;
  }
  f33_set_current_limit_request(6,(ushort)iVar15);
  (*((ushort *)camry_host_ptr((uint32_t)(puVar4 + 0x506)))) = (ushort)iVar15;
  (*((int *)camry_host_ptr((uint32_t)(puVar4 + 0x518)))) = iVar2;
  (*((int *)camry_host_ptr((uint32_t)(puVar4 + 0x530)))) = iVar5;
  (*((short *)camry_host_ptr((uint32_t)(puVar4 + 0x512)))) = sStack_34;
  (*((short *)camry_host_ptr((uint32_t)(puVar4 + 0x516)))) = (short)iVar13;
  (*((short *)camry_host_ptr((uint32_t)(puVar4 + 0x514)))) = sStack_32;
  return;
}



/* Compose real familyselection,gate/axisfilter,sourcetransition andscalarpublication in order. */

void f33_update_owner6_calibration_envelope(void)

{
  f33_select_owner6_calibration_family();
  f33_update_owner6_gate_and_axis_filter();
  f33_update_owner6_source_transition();
  f33_publish_owner6_calibration_envelope();
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_bb734(void)

{
  return;
}



/* For low8(owner)<10 replace BD34[owner] only. Request publication is distinct from later masked
   reductions and current-control consumption. Low8 owner<10 replaces one unsigned-halfword BD34
   slot; invalid owners do nothing. Request storage is not immediate masked reduction or
   current-control response. */

void f33_set_current_limit_request(uint owner,ushort limit)

{
  if ((owner & 0xff) < 10) {
    (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebebd34u + (uint32_t)(owner & 0xff) * 2u)))) = limit;
  }
  return;
}



/* Return min(22170, BD34 owners whose AECD4 bit is clear). Exact mask21 excludes owners0/5, not the
   retained thermal-release owner7. Return min22170 over owners excluded by neither bit of AECD4=21.
   Owners0/5 are skipped, but retained thermal owner7 is not. */

uint f33_reduce_service_current_requests(void)

{
  int iVar1;
  uint uVar2;
  uint uVar3;
  uint uVar4;
  
  uVar4 = 0x569a;
  uVar3 = 0;
  do {
    if (((f33_service_current_owner_exclusions >> (uVar3 & 0x1f) & 1) == 0) &&
       ((int)((ushort)(*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebebd34u + (uint32_t)(uVar3) * 2u)))) - uVar4) < 0)) {
      uVar4 = (uint)(ushort)(*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebebd34u + (uint32_t)(uVar3) * 2u))));
    }
    uVar2 = uVar3 + 1;
    iVar1 = uVar3 - 9;
    uVar3 = uVar2;
  } while (iVar1 < 0 != ((int)uVar2 < 0 && -1 < iVar1));
  return uVar4;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_bb7f6(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_bb7f8(void)

{
  return;
}



/* Use service reduction only for family0500,B37C==5A,B20E!=11/22; otherwise normal nonthermal
   reduction. AF3C=3 at22170,0 atzero,1 otherwise. Under PMRFF80 publish limitAF40, signed
   min(owner6,owner9) atAF42 and B37C atAF3D; publish route markerAF3E afterward. Special
   family0500+B37C5A+B20E!=11/22 uses the service owner reduction; otherwise ordinary nonthermal
   reduction. Publish bound and signed min(owner6,owner9) under PMRFF80, with distinct status and
   later route marker. */

void f33_publish_other_current_limit(void)

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
  
  sVar3 = DAT_febebd46;
  sVar10 = DAT_febebd40;
  cVar2 = DAT_febeb37c;
  puVar5 = 0xfebeb800u;
  iVar11 = (int)DAT_febebd40;
  iVar8 = (int)DAT_febebd46;
  if (((((DAT_febeb11a & 0xff00) == 0x500) && (DAT_febeb37c == 'Z')) && (DAT_febeb20e != '\x11')) &&
     (DAT_febeb20e != '\"')) {
    uVar6 = f33_reduce_service_current_requests();
    uVar9 = 0x11;
  }
  else {
    uVar6 = f33_reduce_other_current_requests();
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
  uVar7 = FUN_000d1da0(0xff80);
  (*((short *)camry_host_ptr((uint32_t)(puVar5 + -0x8c0)))) = (short)uVar6;
  (*((short *)camry_host_ptr((uint32_t)(puVar5 + -0x8be)))) = sVar10;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x8c3))))) = cVar2;
  FUN_000d1dc6(uVar7);
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x8c2))))) = uVar9;
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_bb878(void)

{
  return;
}



void FUN_000bb87a(void)

{
  DAT_febebd48 = 0;
  DAT_febebd4a = 0;
  DAT_febebd4c = 0x569a;
  DAT_febebd4e = 0x569a;
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_bb95c(void)

{
  return;
}



void FUN_000bb9d8(char *param_1,int *param_2,short *param_3)

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
  sVar8 = DAT_febebd5c;
  if (cVar1 == '\0') {
    iVar5 = (int)DAT_febebd7e;
    iVar6 = (int)f33_conditioned_offset_scalar;
    iVar3 = (int)DAT_febef17c;
    sVar9 = 0;
    if (DAT_febebd58 <= DAT_000aee38) {
      if ((((DAT_febef1e0 != 0) || (1 < f33_published_internal_source_admission_state)) ||
          (DAT_febebe58 != '\0')) ||
         ((iVar4 = (int)DAT_000aee3a,
          iVar6 - iVar4 < 0 == (iVar6 < 0 != iVar4 < 0 && iVar4 < 0 == iVar6 - iVar4 < 0) &&
          iVar6 != iVar4 ||
          (iVar4 = (int)DAT_000aee3c,
          iVar6 - iVar4 < 0 != (iVar6 < 0 != iVar4 < 0 && iVar4 < 0 == iVar6 - iVar4 < 0))))) {
        sVar9 = DAT_febebd58 + 1;
        goto LAB_000bba8c;
      }
      if ((DAT_febebd56 == 'Z') &&
         (iVar3 - iVar5 < 0 == (iVar3 < 0 != iVar5 < 0 && iVar5 < 0 == iVar3 - iVar5 < 0) &&
          iVar3 != iVar5)) {
        iVar4 = (int)DAT_000aee3e;
        iVar6 = iVar3 - iVar6;
        if (iVar6 - iVar4 < 0 == (iVar6 < 0 != iVar4 < 0 && iVar4 < 0 == iVar6 - iVar4 < 0) &&
            iVar6 != iVar4) {
          local_1c = iVar3 - iVar5;
          puVar2 = 0xfebeb800u;
          FUN_000d1d4e(local_1c,32000,&local_1c);
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



void FUN_000bbaa4(char *param_1,int *param_2,short *param_3)

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
        iVar2 = iVar5 / DAT_000aee50;
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



void FUN_000bbaea(void)

{
  uint32_t puVar1;
  undefined1 uStack_b;
  undefined2 uStack_a;
  undefined4 uStack_8;
  
  puVar1 = 0xfebeb800u;
  uStack_b = DAT_febebd54;
  uStack_8 = DAT_febebd88;
  uStack_a = DAT_febebd5e;
  FUN_000bb9d8(&uStack_b,&uStack_8,&uStack_a);
  FUN_000bbaa4(&uStack_b,&uStack_8,&uStack_a);
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x554))))) = uStack_b;
  (*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + 0x588)))) = uStack_8;
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + 0x55e)))) = uStack_a;
  return;
}



/* WARNING: Removing unreachable block (ram,0x000bbb7e) */

void FUN_000bbb3c(void)

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
  FUN_000d1e8c(((undefined *)camry_host_ptr(0xaee60u)),sVar3,&sStack_a);
  bVar1 = DAT_000aee34;
  (*((short *)camry_host_ptr((uint32_t)(puVar2 + 0x584)))) = sVar3;
  (*((short *)camry_host_ptr((uint32_t)(puVar2 + 0x560)))) = sStack_a;
  (*((short *)camry_host_ptr((uint32_t)(puVar2 + 0x562)))) = (short)(((int)(short)(ushort)bVar1 * (int)sStack_a) / 0x80);
  return;
}



/* WARNING: Removing unreachable block (ram,0x000bbbdc) */

void FUN_000bbb88(void)

{
  int iVar1;
  uint32_t puVar2;
  short sStack_12;
  short asStack_10 [2];
  int iStack_c;
  
  puVar2 = 0xfebeb800u;
  iVar1 = (int)DAT_febef17a + (int)DAT_febef178;
  FUN_000d1cf6(iVar1,0x7fff,0xffff8001,asStack_10);
  FUN_000d1de4(((undefined *)camry_host_ptr(0xaee7cu)),(int)asStack_10[0],&sStack_12);
  iStack_c = (int)((iVar1 - sStack_12) * (uint)DAT_000aee35) / 0x80;
  FUN_000d1cf6(iStack_c,32000,0xffffe700,&iStack_c);
  (*((int *)camry_host_ptr((uint32_t)(puVar2 + 0x58c)))) = iVar1;
  (*((short *)camry_host_ptr((uint32_t)(puVar2 + 0x564)))) = sStack_12;
  (*((short *)camry_host_ptr((uint32_t)(puVar2 + 0x566)))) = (short)iStack_c;
  return;
}



/* WARNING: Removing unreachable block (ram,0x000bbc92) */

void FUN_000bbbfc(void)

{
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
  int local_34;
  int iStack_30;
  int iStack_2c;
  int iStack_28;
  
  iVar11 = DAT_febebd90;
  iVar2 = DAT_febebd8c;
  cVar1 = DAT_febebd54;
  puVar4 = 0xfebeb800u;
  iStack_2c = (int)DAT_febebd5a;
  iVar8 = (int)DAT_febebd5e;
  iVar7 = (int)DAT_febebd62;
  iStack_28 = (int)DAT_febebd7e;
  iVar6 = (int)DAT_febebd64;
  iVar10 = (int)DAT_febebd6a;
  local_34 = (int)DAT_febef17c - (int)DAT_febebd66;
  FUN_000d1cf6(local_34,32000,0xffffe700,&local_34);
  sVar3 = (short)local_34;
  iVar9 = (int)(short)local_34;
  iVar5 = iVar11;
  if (DAT_000aee54 != 0) {
    if (iVar11 == -0x80000000 && DAT_000aee54 == -1) {
      iVar5 = 0;
    }
    else {
      iVar5 = iVar11 / DAT_000aee54;
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
      iVar11 = iVar10 / DAT_000aee54;
    }
  }
  iStack_30 = (int)DAT_000aee42 + (((short)iVar11 - iVar7) - iVar8);
  if (cVar1 != '\0') {
    iStack_2c = (int)((iVar6 + iVar2) * (uint)DAT_000aee36) / 0x80;
    iStack_28 = iStack_2c + iStack_30;
    FUN_000d1cf6(iStack_2c,32000,0xffffe700,&iStack_2c);
    FUN_000d1cf6(iStack_28,32000,0xffffe700,&iStack_28);
  }
  FUN_000d1cf6(iStack_30,32000,0xffffe700,&iStack_30);
  (*((short *)camry_host_ptr((uint32_t)(puVar4 + 0x568)))) = sVar3;
  (*((int *)camry_host_ptr((uint32_t)(puVar4 + 0x590)))) = iVar10;
  (*((short *)camry_host_ptr((uint32_t)(puVar4 + 0x56a)))) = (short)iVar11;
  (*((short *)camry_host_ptr((uint32_t)(puVar4 + 0x56c)))) = (short)iStack_30;
  (*((short *)camry_host_ptr((uint32_t)(puVar4 + 0x55a)))) = (short)iStack_2c;
  (*((short *)camry_host_ptr((uint32_t)(puVar4 + 0x57e)))) = (short)iStack_28;
  return;
}



/* Sequential initializer chain: 4 unconditional calls and no other statements; shape-verified. The
   called sequence is the function's entire behavior; chain family members differ in callee sets. */

void f33_run_init_chain_bbcea(void)

{
  FUN_000bbaea();
  FUN_000bbb3c();
  FUN_000bbb88();
  FUN_000bbbfc();
  return;
}



void FUN_000bbd02(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  
  iVar1 = (int)DAT_febebd6c;
  iVar4 = (int)f33_conditioned_offset_scalar;
  if (DAT_febebd51 != '\"') {
    if ((((((DAT_febebd54 == '\0') || (DAT_febef1e0 != 0)) ||
          (1 < f33_published_internal_source_admission_state)) ||
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
      iVar4 = iVar4 - DAT_febef17c;
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



void FUN_000bbd9c(void)

{
  int iVar1;
  int iVar2;
  uint32_t puVar3;
  undefined *puVar4;
  int iVar5;
  short sStack_e;
  
  iVar2 = DAT_febebd94;
  puVar3 = 0xfebeb800u;
  iVar5 = (int)DAT_febebd72;
  if (((f33_published_internal_source_admission_state < 2) && (DAT_febebe89 == '\0')) &&
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
    FUN_000d1e8c(puVar4,DAT_febebee2,&sStack_e);
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
      iVar5 = iVar5 / iVar1;
    }
  }
  (*((short *)camry_host_ptr((uint32_t)(puVar3 + 0x572)))) = (short)iVar5;
  return;
}



void FUN_000bbe26(void)

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



/* WARNING: Removing unreachable block (ram,0x000bbf06) */

void FUN_000bbe7a(void)

{
  char cVar1;
  char cVar2;
  short sVar3;
  uint32_t puVar4;
  undefined4 uVar5;
  int iVar6;
  int iVar7;
  short sVar8;
  int iVar9;
  short local_28;
  short sStack_26;
  undefined2 uStack_24;
  short sStack_22;
  int iStack_20;
  int iVar10;
  
  iVar10 = DAT_febebd98;
  cVar2 = DAT_febebd52;
  cVar1 = DAT_febebd51;
  puVar4 = 0xfebeb800u;
  iVar7 = (int)f33_conditioned_offset_scalar;
  sStack_22 = DAT_febebd7a;
  iVar9 = (int)DAT_febebd7c;
  sStack_26 = DAT_febebd80;
  iStack_20 = (int)DAT_febebd6c - (int)DAT_febebd72;
  FUN_000d1cf6(iStack_20,32000,0xffffe700,&iStack_20);
  sVar3 = (short)iStack_20;
  iVar6 = (int)(short)iStack_20;
  if (iVar6 - iVar7 < 0 == (iVar6 < 0 != iVar7 < 0 && iVar7 < 0 == iVar6 - iVar7 < 0) &&
      iVar6 != iVar7) {
    iVar7 = iVar6;
  }
  if (cVar1 == '\x11') {
    FUN_000d1de4(((undefined *)camry_host_ptr(0xaef00u)),iVar7,&local_28);
  }
  else {
    local_28 = 0;
  }
  sVar8 = local_28;
  iVar6 = (int)local_28;
  if (cVar2 == 'Z') {
    FUN_000d1cdc(iVar6,(int)DAT_000aee4a,(int)DAT_000aee4c,&sStack_26);
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
        iVar10 = iVar10 / DAT_000aee5c;
      }
    }
    sVar8 = (short)iVar10;
    FUN_000d1cdc((int)sVar8,(int)DAT_000aee4a,(int)DAT_000aee4c,&sStack_22);
    FUN_000d1cdc((int)sStack_22,(int)(short)(DAT_000aee4e + sStack_26),
                 (int)(short)(sStack_26 - DAT_000aee4e),&sStack_26);
  }
  FUN_000d1de4(((undefined *)camry_host_ptr(0xaef1cu)),iVar7,&uStack_24);
  (*((short *)camry_host_ptr((uint32_t)(puVar4 + 0x574)))) = sVar3;
  (*((short *)camry_host_ptr((uint32_t)(puVar4 + 0x576)))) = (short)iVar7;
  (*((short *)camry_host_ptr((uint32_t)(puVar4 + 0x57c)))) = sVar8;
  (*((short *)camry_host_ptr((uint32_t)(puVar4 + 0x57a)))) = sStack_22;
  (*((int *)camry_host_ptr((uint32_t)(puVar4 + 0x598)))) = iVar9;
  (*((short *)camry_host_ptr((uint32_t)(puVar4 + 0x578)))) = local_28;
  uVar5 = FUN_000d1da0(0xffc0);
  (*((short *)camry_host_ptr((uint32_t)(puVar4 + 0x580)))) = sStack_26;
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar4 + 0x582)))) = uStack_24;
  FUN_000d1dc6(uVar5);
  return;
}



void FUN_000bbf8a(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  if (DAT_febebd55 == '\0') {
    puVar1 = 0xfebeb800u;
    FUN_000bb97c();
  }
  f33_run_init_chain_bbcea();
  FUN_000bbd02();
  FUN_000bbd9c();
  FUN_000bbe26();
  FUN_000bbe7a();
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x555))))) = 0x5a;
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_bbfba(void)

{
  return;
}



/* Nominal22170 request/accumulator; active and cutoff latch0,cachedcoefficient0. Qualification
   reset isBC0F8. */

void f33_reset_owner3_shutdown_request(void)

{
  DAT_febebd9e = 0x569a;
  DAT_febebd9c = 0;
  DAT_febebd9d = 0;
  DAT_febebda0 = 0;
  DAT_febebda4 = 0x569a0000;
  return;
}



/* WARNING: Removing unreachable block (ram,0x000bc0a2) */
/* WARNING: Removing unreachable block (ram,0x000bbff0) */
/* Active qualificationlow input decayswithk1300, reportsA1failure andactions; inclusive128 cutoff
   latch publishesmask70017001. Holdbandkeepsoutput; inactivepassreleasesnominal andclearsacc/latch.
    */

void f33_publish_owner3_shutdown_request(void)

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
  iVar1 = DAT_febebda4 / 0x10000;
  if (DAT_febebda9 == '\x01') {
    iVar10 = (int)(short)DAT_febebd9e;
    iVar4 = (int)DAT_febebccc;
    if (DAT_febebda8 != '\x01') {
      puVar3 = 0xfebeb800u;
      f33_report_diagnostic_event_pass(0xa1);
      uVar2 = (*((ushort *)camry_host_ptr((uint32_t)(puVar3 + 0x5a0))));
      limit = DAT_000af10c;
      goto LAB_000bc074;
    }
    uVar7 = (uint)DAT_000af108;
    uVar5 = 1;
    iVar9 = DAT_febebda4;
    limit = DAT_febebd9e;
    if (DAT_febeb084 < DAT_000af114) {
      puVar3 = 0xfebeb800u;
      f33_report_diagnostic_event_failure(0xa1,0x32);
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
      ((void)(4), thunk_FUN_000545de());
      ((void)(2), (void)(0x32), thunk_FUN_00051cf6());
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
    f33_report_diagnostic_event_pass(0xa1);
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
  f33_set_output_request_word('\x03',uVar7);
  f33_set_current_limit_request(3,limit);
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(0x59c))))) = uVar5;
  (*((ushort *)camry_host_ptr((uint32_t)(puVar3 + 0x59e)))) = limit;
  (*((ushort *)camry_host_ptr((uint32_t)(puVar3 + 0x5a0)))) = uVar6;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(0x59d))))) = cVar8;
  (*((int *)camry_host_ptr((uint32_t)(puVar3 + 0x5a4)))) = iVar9;
  return;
}


