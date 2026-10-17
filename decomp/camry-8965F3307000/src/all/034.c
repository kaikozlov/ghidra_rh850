#include "common.h"


/* WARNING: Removing unreachable block (ram,0x000d00de) */
/* WARNING: Removing unreachable block (ram,0x000d0096) */
/* WARNING: Removing unreachable block (ram,0x000d0074) */

void FUN_000d0030(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  
  iVar2 = -DAT_febeac24;
  DAT_febecc22 = (short)(*((int *)camry_host_ptr((uint32_t)((int)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xb148cu + (uint32_t)(DAT_febeac3c & 1) * 4u)))) + 8))));
  iVar1 = (int)DAT_febecc22;
  if (DAT_febecc20 == '\0') {
    DAT_febecc20 = '\x01';
    DAT_febecc08 = iVar2;
  }
  iVar3 = (int)DAT_febecc1c;
  DAT_febecc00 = ((int)DAT_febecc1a * (int)DAT_febecc18) / 0x400;
  if (iVar3 == 0) {
    DAT_febecc04 = 0;
    DAT_febecc00 = 0;
  }
  else {
    DAT_febecc04 = (DAT_febecc00 << 0x12) / 0x168;
    if (iVar3 != 0) {
      if (DAT_febecc04 == -0x80000000 && iVar3 == -1) {
        DAT_febecc04 = -0x80000000;
      }
      else {
        DAT_febecc04 = DAT_febecc04 / iVar3;
      }
    }
  }
  DAT_febecc0c = DAT_febecc08 + DAT_febeac24;
  if (DAT_febecc0c - DAT_febecc04 < 0 ==
      (DAT_febecc0c < 0 != DAT_febecc04 < 0 && DAT_febecc04 < 0 == DAT_febecc0c - DAT_febecc04 < 0)
      && DAT_febecc0c != DAT_febecc04) {
    DAT_febecc08 = DAT_febecc04 + iVar2;
    DAT_febecc10 = DAT_febecc00;
  }
  else if (DAT_febecc0c + DAT_febecc04 < 0 ==
           (DAT_febecc0c < 0 != -DAT_febecc04 < 0 &&
           -DAT_febecc04 < 0 == DAT_febecc0c + DAT_febecc04 < 0)) {
    DAT_febecc10 = (DAT_febecc0c * iVar3 * 0x168) / 0x40000;
  }
  else {
    DAT_febecc08 = iVar2 - DAT_febecc04;
    DAT_febecc10 = -DAT_febecc00;
  }
  DAT_febecc14 = (DAT_febecc14 + DAT_febecc10) - (int)DAT_febecc1e;
  iVar3 = (*((int *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xb148cu + (uint32_t)(DAT_febeac3c & 1) * 4u)))))));
  iVar2 = DAT_febecc14 * 0x400;
  if (iVar3 != 0) {
    if (iVar2 == -0x80000000 && iVar3 == -1) {
      iVar2 = 0;
    }
    else {
      iVar2 = iVar2 / iVar3;
    }
  }
  iVar3 = (int)(short)iVar2;
  DAT_febecc1e = (short)iVar2;
  if (DAT_febecbec == '\x01') {
    if (iVar3 - iVar1 < 0 != (iVar3 < 0 != iVar1 < 0 && iVar1 < 0 == iVar3 - iVar1 < 0) ||
        iVar3 == iVar1) {
      iVar2 = -iVar1;
      if (iVar3 + iVar1 < 0 == (iVar3 < 0 != iVar2 < 0 && iVar2 < 0 == iVar3 + iVar1 < 0) &&
          iVar3 != iVar2) {
        iVar2 = iVar3;
      }
      DAT_febecc22 = (short)iVar2;
    }
  }
  else {
    DAT_febecc22 = 0;
  }
  return;
}



void FUN_000d0120(void)

{
  FUN_000cfffc();
  FUN_000d0030();
  return;
}



void FUN_000d0130(void)

{
  DAT_febecc2c = 0;
  DAT_febecc24 = 0;
  DAT_febecc28 = 0;
  return;
}



void FUN_000d013e(void)

{
  DAT_febecc24 = DAT_000b1328;
  if ((-1 < DAT_000b1328) && (DAT_febecc24 = 0, 0 < -DAT_000b1328)) {
    DAT_febecc24 = -DAT_000b1328;
  }
  return;
}



/* Sum signed32 CC24/C39C and signed16 C3A0/C41E/C53A/C5A8, clamp to+/-5120, publish CC2C. Nested
   rate, bounded-memory and moving-state terms retain separate attenuation/history. ROM B1328 makes
   CC24 zero; B1371 disables C5A8 in this image. Aggregate six mixed-width published internal terms
   into signed32 CC2C bounded to5120. Exact ROM disables CC24/C5A8 contributions here; this proves
   aggregation rather than complete physical semantics of each producer. */

void f33_aggregate_internal_assist_terms(void)

{
  int iVar1;
  int iVar2;
  uint32_t puVar3;
  int iVar4;
  int iVar5;
  int iVar6;
  int iVar7;
  
  iVar1 = DAT_febec39c;
  puVar3 = 0xfebeb800u;
  iVar7 = (int)DAT_febec53a;
  iVar5 = (int)DAT_febec5a8;
  iVar6 = (int)DAT_febec41e;
  iVar4 = (int)DAT_febec3a0;
  FUN_000d013e();
  iVar2 = f33_nested_assist_sum_limit;
  iVar1 = (*((int *)camry_host_ptr((uint32_t)(puVar3 + 0x1424)))) + iVar4 + iVar1 + iVar6 + iVar5 + iVar7;
  (*((int *)camry_host_ptr((uint32_t)(puVar3 + 0x1428)))) = iVar1;
  iVar4 = f33_nested_assist_sum_limit;
  if ((iVar1 - iVar2 < 0 != (iVar1 < 0 != iVar2 < 0 && iVar2 < 0 == iVar1 - iVar2 < 0) ||
       iVar1 == iVar2) &&
     (iVar4 = iVar1,
     iVar1 + f33_nested_assist_sum_limit < 0 !=
     (iVar1 < 0 != -f33_nested_assist_sum_limit < 0 &&
     -f33_nested_assist_sum_limit < 0 == iVar1 + f33_nested_assist_sum_limit < 0))) {
    iVar4 = -f33_nested_assist_sum_limit;
  }
  (*((int *)camry_host_ptr((uint32_t)(puVar3 + 0x142c)))) = iVar4;
  return;
}



/* Constant-block fill: 25 literal assignments into one contiguous cell block; shape-verified.
   Literals are default/reset values; cell meanings are not recovered. */

void f33_fill_constant_block_d01b4(void)

{
  DAT_febecc4c = 0;
  DAT_febecc30 = 0;
  DAT_febecc34 = 0;
  DAT_febecc38 = 0;
  DAT_febecc3c = 0;
  DAT_febecc4e = 0;
  DAT_febecc60 = 0;
  DAT_febecc50 = 0;
  DAT_febecc62 = 0;
  DAT_febecc52 = 0;
  DAT_febecc54 = 0;
  DAT_febecc66 = 0;
  DAT_febecc64 = 0;
  DAT_febecc68 = 0;
  DAT_febecc6a = 0;
  DAT_febecc5c = 0;
  DAT_febecc56 = 0;
  DAT_febecc58 = 0;
  DAT_febecc5a = 0;
  DAT_febecc5e = 0;
  DAT_febecc5f = 0;
  DAT_febecc40 = 0;
  DAT_febecc44 = 0;
  DAT_febecc48 = 0;
  DAT_febecc6c = 0;
  return;
}



/* WARNING: Removing unreachable block (ram,0x000d025e) */
/* Publish signed32 CC48 without whole-sum saturation. AC2B==5A selects C4C0+C3BA+BF3C; otherwise
   C7BF==1 selects C4C0+BF3C; ordinary branch adds C43C,CC2C,CBE8 and
   clamp(s32(CB38)+s32(C5EE),+/-12002). Selection does not reset skipped producers. Diagnostic AC2B
   selection precedes C7BF. Ordinary branch includes signed32-limited CB38+C5EE pair and other
   mixed-width terms; whole CC48 sum is not clamped here. Contribution selection does not reset
   producer state. */

void f33_aggregate_assist_command(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  
  iVar1 = DAT_febec4c0;
  if (DAT_febeac2b == 'Z') {
    iVar3 = DAT_febec3ba + DAT_febebf3c;
  }
  else {
    iVar3 = DAT_febebf3c;
    if (DAT_febec7bf != '\x01') {
      iVar1 = (int)DAT_febecb38 + (int)DAT_febec5ee;
      iVar3 = DAT_000b132c / 2;
      iVar2 = iVar3;
      if ((iVar1 - iVar3 < 0 != (iVar1 < 0 != iVar3 < 0 && iVar3 < 0 == iVar1 - iVar3 < 0) ||
           iVar1 == iVar3) &&
         (iVar2 = -iVar3,
         iVar1 + iVar3 < 0 == (iVar1 < 0 != iVar2 < 0 && iVar2 < 0 == iVar1 + iVar3 < 0) &&
         iVar1 != iVar2)) {
        iVar2 = iVar1;
      }
      iVar3 = (int)DAT_febecbe8;
      iVar1 = (int)DAT_febec43c + DAT_febec4c0 + (int)DAT_febec3ba + DAT_febecc2c + DAT_febebf3c +
              iVar2;
    }
  }
  DAT_febecc48 = iVar1 + iVar3;
  return;
}



/* WARNING: Removing unreachable block (ram,0x000d02ba) */

void FUN_000d0284(void)

{
  int iVar1;
  int iVar2;
  
  iVar2 = f33_command_sum_margin + DAT_000b132c;
  iVar1 = iVar2;
  if ((DAT_febecc48 - iVar2 < 0 !=
       (DAT_febecc48 < 0 != iVar2 < 0 && iVar2 < 0 == DAT_febecc48 - iVar2 < 0) ||
       DAT_febecc48 == iVar2) &&
     (iVar1 = -iVar2,
     DAT_febecc48 + iVar2 < 0 ==
     (DAT_febecc48 < 0 != iVar1 < 0 && iVar1 < 0 == DAT_febecc48 + iVar2 < 0) &&
     DAT_febecc48 != iVar1)) {
    iVar1 = DAT_febecc48;
  }
  iVar2 = (int)DAT_000b1334;
  DAT_febecc44 = (int)(iVar1 * (uint)DAT_febeac64) / 0x8000;
  DAT_febecc4c = DAT_000b1334;
  if (DAT_febecc44 - iVar2 < 0 !=
      (DAT_febecc44 < 0 != iVar2 < 0 && iVar2 < 0 == DAT_febecc44 - iVar2 < 0) ||
      DAT_febecc44 == iVar2) {
    iVar1 = -iVar2;
    if (DAT_febecc44 + iVar2 < 0 ==
        (DAT_febecc44 < 0 != iVar1 < 0 && iVar1 < 0 == DAT_febecc44 + iVar2 < 0) &&
        DAT_febecc44 != iVar1) {
      DAT_febecc4c = (short)DAT_febecc44;
    }
    else {
      DAT_febecc4c = (short)iVar1;
    }
  }
  return;
}



/* ROM B1338==1 enables retained CC30/34/38/3C recurrence. Nonzero CC9C selects filtered output,
   otherwise CC4C bypasses to CC4E. Difference shift uses low5 CC9E with minimum nonzero step +/-1;
   selected filtered output saturates to +/-32767. Always retain published CC4E in CC3C. Invocation
   recurrence, not a wall-time rate. Retained command slew/filter with conditional bypass and signed
   saturation. Composed native tail exercises filtered1024 publication; remaining branches
   instruction/dataflow checked. No wall-time slew-rate claim. */

void f33_filter_command_slew(void)

{
  int iVar1;
  bool bVar2;
  int iVar3;
  uint uVar4;
  
  DAT_febecc4e = DAT_febecc4c;
  if (DAT_000b1338 != '\x01') goto LAB_000d0378;
  iVar3 = (int)DAT_febecc4c;
  iVar1 = DAT_febecc3c;
  if (iVar3 == DAT_febecc3c) goto LAB_000d0318;
  if (iVar3 == DAT_febecc30) {
    iVar1 = DAT_febecc34;
    if (iVar3 - DAT_febecc3c < 0) {
      if (-1 < (int)DAT_febecc38) goto LAB_000d030e;
    }
    else if ((int)DAT_febecc38 < 0) goto LAB_000d030e;
  }
  else {
LAB_000d030e:
    DAT_febecc3c = DAT_febecc3c + DAT_febecc38;
    iVar1 = DAT_febecc3c;
  }
LAB_000d0318:
  DAT_febecc34 = iVar1;
  iVar1 = iVar3 - DAT_febecc34;
  bVar2 = iVar3 < 0 != DAT_febecc34 < 0 && DAT_febecc34 < 0 == iVar1 < 0;
  if (iVar1 < 0 == bVar2) {
    if (iVar1 < 0 == bVar2 && iVar3 != DAT_febecc34) {
      DAT_febecc38 = (uint)(iVar3 - DAT_febecc34) >> (DAT_febecc9e & 0x1f);
      if (DAT_febecc38 == 0) {
        DAT_febecc38 = 1;
      }
    }
    else {
      DAT_febecc38 = 0;
    }
  }
  else {
    uVar4 = (uint)(DAT_febecc34 - iVar3) >> (DAT_febecc9e & 0x1f);
    DAT_febecc38 = -uVar4;
    if (uVar4 == 0) {
      DAT_febecc38 = 0xffffffff;
    }
  }
  DAT_febecc30 = iVar3;
  if (DAT_febecc9c != 0) {
    iVar1 = DAT_febecc38 + DAT_febecc3c;
    iVar3 = 0x7fff;
    if ((iVar1 + -0x7fff < 0 != (iVar1 < 0 && -1 < iVar1 + -0x7fff) || iVar1 == 0x7fff) &&
       (iVar3 = iVar1, iVar1 + 0x7fff < 0 != (-1 < iVar1 && iVar1 + 0x7fff < 0) || iVar1 == -0x7fff)
       ) {
      iVar3 = -0x7fff;
    }
    DAT_febecc4e = (short)iVar3;
  }
LAB_000d0378:
  DAT_febecc3c = (int)DAT_febecc4e;
  return;
}



void FUN_000d0382(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  
  iVar3 = (int)DAT_febecc4e;
  iVar2 = (int)DAT_febeac52;
  DAT_febecc60 = DAT_febeac52;
  if ((iVar3 - iVar2 < 0 != (iVar3 < 0 != iVar2 < 0 && iVar2 < 0 == iVar3 - iVar2 < 0) ||
       iVar3 == iVar2) &&
     (iVar1 = -iVar2, DAT_febecc60 = DAT_febecc4e,
     iVar3 + iVar2 < 0 != (iVar3 < 0 != iVar1 < 0 && iVar1 < 0 == iVar3 + iVar2 < 0) ||
     iVar3 == iVar1)) {
    DAT_febecc60 = (short)iVar1;
  }
  return;
}



/* WARNING: Removing unreachable block (ram,0x000d03ea) */
/* WARNING: Removing unreachable block (ram,0x000d03e6) */
/* WARNING: Removing unreachable block (ram,0x000d03d0) */
/* Select delayed AC10 history CC5A only when AC28==1, otherwise current CC60. Apply
   complement-checked base and local-addend gains from CB9C8/CB9AE, narrowing each gained term to
   signed16. Add local C81A term only when C797==0; clamp the sum to ROM B1334 and publish CC50.
   Therefore CC62 is not universally before or after the earlier slew path. Select current or
   delayed-history base, apply separately checked gains, optionally add local C81A, then clamp.
   Native composition covers current-base path; alternate branch remains static evidence. */

void f33_compose_command_sources(void)

{
  int iVar1;
  char cVar2;
  uint32_t puVar3;
  short sVar4;
  int iVar5;
  int iVar6;
  short sVar7;
  
  cVar2 = DAT_febec797;
  puVar3 = 0xfebeb800u;
  iVar5 = FUN_000cb9c8();
  iVar6 = FUN_000cb9ae();
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0xbd8))))) == '\x01') {
    sVar7 = (*((short *)camry_host_ptr((uint32_t)(puVar3 + 0x145a))));
  }
  else {
    sVar7 = (*((short *)camry_host_ptr((uint32_t)(puVar3 + 0x1460))));
  }
  (*((short *)camry_host_ptr((uint32_t)(puVar3 + 0x1452)))) = sVar7;
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + 0x146a)))) = 0;
  sVar4 = (short)((iVar6 * (*((short *)camry_host_ptr((uint32_t)(puVar3 + 0x101a))))) / 0x100);
  sVar7 = (short)(((short)(((int)sVar7 << 8) / 0x100) * iVar5) / 0x100);
  iVar5 = (int)sVar7;
  if (cVar2 == '\0') {
    iVar5 = iVar5 + sVar4;
  }
  (*((short *)camry_host_ptr((uint32_t)(puVar3 + 0x145c)))) = sVar7;
  sVar7 = DAT_000b1334;
  iVar6 = (int)DAT_000b1334;
  (*((short *)camry_host_ptr((uint32_t)(puVar3 + 0x146c)))) = sVar4;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(0x145f))))) = 0;
  (*((int *)camry_host_ptr((uint32_t)(puVar3 + 0x1440)))) = iVar5;
  if (iVar5 - iVar6 < 0 != (iVar5 < 0 != iVar6 < 0 && iVar6 < 0 == iVar5 - iVar6 < 0) ||
      iVar5 == iVar6) {
    iVar1 = -iVar6;
    if (iVar5 + iVar6 < 0 == (iVar5 < 0 != iVar1 < 0 && iVar1 < 0 == iVar5 + iVar6 < 0) &&
        iVar5 != iVar1) {
      sVar7 = (short)iVar5;
    }
    else {
      sVar7 = (short)iVar1;
    }
  }
  (*((short *)camry_host_ptr((uint32_t)(puVar3 + 0x1450)))) = sVar7;
  return;
}



/* WARNING: Removing unreachable block (ram,0x000d0440) */
/* Signed16 CC50 times unsigned16 AC5A, signed division by1024, then signed16 narrowing BEFORE
   amplitude clamp. Publish CC62 and reuse the register value, not a RAM reload. Clamp against
   signed AC4C into CC54; publish CC66 only when AC29!=0 and AC2A==0, else zero. Copy AC4C to CC68.
   No history or slew recurrence here. Scale by AC5A/1024, narrow to signed16 BEFORE amplitude
   clamp, then apply AC29/AC2A gate. Native synthetic high-gain case distinguishes pre-clamp -1 from
   gated0; CC62 is not reloaded and this is not the slew limiter. */

void f33_scale_clamp_gate_command(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  
  iVar3 = (int)DAT_febeac4c;
  DAT_febecc62 = (short)((int)((int)DAT_febecc50 * (uint)DAT_febeac5a) / 0x400);
  iVar2 = (int)DAT_febecc62;
  DAT_febecc66 = DAT_febeac4c;
  if ((iVar2 - iVar3 < 0 != (iVar2 < 0 != iVar3 < 0 && iVar3 < 0 == iVar2 - iVar3 < 0) ||
       iVar2 == iVar3) &&
     (iVar1 = -iVar3, DAT_febecc66 = DAT_febecc62,
     iVar2 + iVar3 < 0 != (iVar2 < 0 != iVar1 < 0 && iVar1 < 0 == iVar2 + iVar3 < 0) ||
     iVar2 == iVar1)) {
    DAT_febecc66 = (short)iVar1;
  }
  DAT_febecc54 = DAT_febecc66;
  if ((DAT_febeac29 == '\0') || (DAT_febeac2a != '\0')) {
    DAT_febecc66 = 0;
  }
  DAT_febecc68 = DAT_febeac4c;
  return;
}



/* Normally select CC66. Nonzero CC98 selects signed32 CC94 clamped to +/-22170 instead. Publish
   CC64. Internal override selection can differ from both the diagnostic CC62 and normal gated CC66
   values. Select ordinary CC66 or symmetrically bounded internal CC94 when CC98 is set. Native
   composition covers ordinary selection; override branch instruction/dataflow checked. */

void f33_select_final_command(void)

{
  int iVar1;
  
  DAT_febecc64 = DAT_febecc66;
  if (DAT_febecc98 != '\0') {
    if (DAT_febecc94 + -0x569a < 0 == (DAT_febecc94 < 0 && -1 < DAT_febecc94 + -0x569a) &&
        DAT_febecc94 != 0x569a) {
      DAT_febecc64 = 0x569a;
    }
    else {
      iVar1 = DAT_febecc94;
      if (DAT_febecc94 + 0x569a < 0 != (-1 < DAT_febecc94 && DAT_febecc94 + 0x569a < 0) ||
          DAT_febecc94 == -0x569a) {
        iVar1 = -0x569a;
      }
      DAT_febecc64 = (short)iVar1;
    }
  }
  return;
}



void FUN_000d04ac(void)

{
  if (DAT_febeac04 == '\x01') {
    DAT_febecc5e = '\x01';
  }
  else if (DAT_febeac06 == 'Z') {
    if (DAT_febecc5e == '\x01') {
      DAT_febecc5a = DAT_febeac10;
      DAT_febecc58 = DAT_febeac10;
    }
    else {
      DAT_febecc5a = DAT_febecc58;
      DAT_febecc58 = DAT_febecc56;
    }
    DAT_febecc56 = DAT_febeac10;
    DAT_febecc5e = '\0';
  }
  return;
}



/* Constant-block fill: 13 literal assignments into one contiguous cell block; shape-verified.
   Literals are default/reset values; cell meanings are not recovered. */

void f33_fill_constant_block_d04f0(void)

{
  DAT_febecc70 = 0;
  DAT_febecc74 = 0;
  DAT_febecc88 = 0;
  DAT_febecc78 = 0;
  DAT_febecc8a = 0;
  DAT_febecc7c = 0;
  DAT_febecc98 = 0;
  DAT_febecc90 = 1;
  DAT_febecc80 = 0;
  DAT_febecc8c = 0;
  DAT_febecc84 = 0;
  DAT_febecc8e = 0;
  DAT_febecc91 = 0;
  return;
}



void FUN_000d0528(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  int iVar6;
  undefined1 uVar7;
  int iVar8;
  int iVar9;
  int iVar10;
  
  iVar5 = (int)DAT_000b1346;
  iVar9 = (int)DAT_000b1344;
  iVar8 = (int)DAT_000b134a;
  iVar6 = (int)DAT_febecc8c;
  iVar4 = (int)DAT_000b134c;
  iVar10 = (int)-DAT_febeac42;
  iVar3 = (int)DAT_000b134e;
  iVar2 = (int)-DAT_febeac44;
  if (((((DAT_febecc7c - iVar8 < 0 ==
          (DAT_febecc7c < 0 != iVar8 < 0 && iVar8 < 0 == DAT_febecc7c - iVar8 < 0)) &&
        (DAT_febecc84 - iVar9 < 0 ==
         (DAT_febecc84 < 0 != iVar9 < 0 && iVar9 < 0 == DAT_febecc84 - iVar9 < 0) &&
         DAT_febecc84 != iVar9)) &&
       (iVar6 + iVar5 < 0 != (iVar6 < 0 != -iVar5 < 0 && -iVar5 < 0 == iVar6 + iVar5 < 0))) &&
      ((iVar2 - iVar4 < 0 == (iVar2 < 0 != iVar4 < 0 && iVar4 < 0 == iVar2 - iVar4 < 0) &&
        iVar2 != iVar4 &&
       (uVar7 = 1,
       iVar10 - iVar3 < 0 == (iVar10 < 0 != iVar3 < 0 && iVar3 < 0 == iVar10 - iVar3 < 0) &&
       iVar10 != iVar3)))) ||
     ((((iVar1 = -iVar8,
        DAT_febecc7c + iVar8 < 0 !=
        (DAT_febecc7c < 0 != iVar1 < 0 && iVar1 < 0 == DAT_febecc7c + iVar8 < 0) ||
        DAT_febecc7c == iVar1 &&
        ((DAT_febecc84 + iVar9 < 0 !=
          (DAT_febecc84 < 0 != -iVar9 < 0 && -iVar9 < 0 == DAT_febecc84 + iVar9 < 0) &&
         (iVar6 - iVar5 < 0 == (iVar6 < 0 != iVar5 < 0 && iVar5 < 0 == iVar6 - iVar5 < 0) &&
          iVar6 != iVar5)))) &&
       (iVar2 + iVar4 < 0 != (iVar2 < 0 != -iVar4 < 0 && -iVar4 < 0 == iVar2 + iVar4 < 0))) &&
      (uVar7 = 2,
      iVar10 + iVar3 < 0 != (iVar10 < 0 != -iVar3 < 0 && -iVar3 < 0 == iVar10 + iVar3 < 0))))) {
    DAT_febecc91 = 1;
    DAT_febecc98 = uVar7;
  }
  return;
}



void FUN_000d05b4(void)

{
  int iVar1;
  
  DAT_febecc70 = (DAT_febecc70 + DAT_febeac48) - (int)DAT_febecc88;
  iVar1 = DAT_febecc70 * 0x400;
  if (DAT_000b133c != 0) {
    if (iVar1 == -0x80000000 && DAT_000b133c == -1) {
      iVar1 = 0;
    }
    else {
      iVar1 = iVar1 / DAT_000b133c;
    }
  }
  DAT_febecc88 = (short)iVar1;
  DAT_febecc74 = (DAT_febecc74 + DAT_febeac46) - DAT_febecc78;
  DAT_febecc78 = DAT_febecc74 * 0x400;
  if (DAT_000b1340 != 0) {
    if (DAT_febecc78 == -0x80000000 && DAT_000b1340 == -1) {
      DAT_febecc78 = -0x80000000;
    }
    else {
      DAT_febecc78 = DAT_febecc78 / DAT_000b1340;
    }
  }
  if (DAT_febecc90 == '\x01') {
    DAT_febecc90 = '\0';
    DAT_febecc8a = DAT_febecc88;
  }
  else {
    DAT_febecc84 = DAT_febecc78 - DAT_febecc7c;
    DAT_febecc8c = DAT_febecc88 - DAT_febecc8a;
    DAT_febecc8a = DAT_febecc88;
    if ((DAT_febeac4a <= DAT_000b1348) && (DAT_febecc98 == '\0')) {
      FUN_000d0528();
    }
  }
  return;
}



void FUN_000d064c(void)

{
  if (DAT_febecc91 == '\x01') {
    if (DAT_febecc8e < DAT_000b1350) {
      DAT_febecc8e = DAT_febecc8e + 1;
    }
    else {
      DAT_febecc91 = '\0';
      DAT_febecc8e = 0;
    }
  }
  return;
}



void FUN_000d0674(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  
  iVar3 = (int)DAT_000b134a;
  iVar1 = -(int)DAT_febecc66;
  DAT_febecc80 = DAT_febecc7c;
  if (DAT_febecc98 == '\x01') {
    if (((iVar1 - DAT_febecc7c < 0 ==
          (iVar1 < 0 != DAT_febecc7c < 0 && DAT_febecc7c < 0 == iVar1 - DAT_febecc7c < 0)) ||
        (DAT_febecc91 == '\x01')) &&
       (DAT_febecc7c - iVar3 < 0 ==
        (DAT_febecc7c < 0 != iVar3 < 0 && iVar3 < 0 == DAT_febecc7c - iVar3 < 0)))
    goto LAB_000d06ca;
LAB_000d069e:
    DAT_febecc98 = '\0';
  }
  else if (DAT_febecc98 == '\x02') {
    if (((iVar1 - DAT_febecc7c < 0 !=
          (iVar1 < 0 != DAT_febecc7c < 0 && DAT_febecc7c < 0 == iVar1 - DAT_febecc7c < 0) ||
          iVar1 == DAT_febecc7c) || (DAT_febecc91 == '\x01')) &&
       (iVar2 = -iVar3,
       DAT_febecc7c + iVar3 < 0 !=
       (DAT_febecc7c < 0 != iVar2 < 0 && iVar2 < 0 == DAT_febecc7c + iVar3 < 0) ||
       DAT_febecc7c == iVar2)) goto LAB_000d06ca;
    goto LAB_000d069e;
  }
  DAT_febecc7c = DAT_febecc78;
  DAT_febecc80 = iVar1;
LAB_000d06ca:
  DAT_febecc94 = -DAT_febecc80;
  return;
}



void FUN_000d06d6(void)

{
  FUN_000d05b4();
  FUN_000d064c();
  FUN_000d0674();
  return;
}



void FUN_000d06ea(void)

{
  DAT_febecc9a = 0;
  DAT_febecc9c = 0;
  DAT_febecc9e = 1;
  return;
}



void FUN_000d06fa(void)

{
  DAT_febecc9a = 0;
  if (DAT_febeadf6 < DAT_000b1352) {
    DAT_febecc9a = 0x4000;
  }
  return;
}



/* WARNING: Removing unreachable block (ram,0x000d073a) */

void FUN_000d0716(void)

{
  int iVar1;
  int iVar2;
  uint32_t puVar3;
  short sVar4;
  undefined2 uVar5;
  undefined4 uVar6;
  int iVar7;
  
  puVar3 = 0xfebeb800u;
  iVar7 = 0;
  sVar4 = f33_abs_s16_wrapping(DAT_febeae3e);
  iVar2 = (int)DAT_000b1354;
  iVar1 = sVar4 - iVar2;
  if (iVar1 < 0 != (sVar4 < 0 != iVar2 < 0 && iVar2 < 0 == iVar1 < 0)) {
    iVar7 = (int)(short)(((int)(*((short *)camry_host_ptr((uint32_t)(puVar3 + 0x149a)))) << 0xe) / 0x4000);
  }
  uVar5 = FUN_000d07ba(((undefined *)camry_host_ptr(0xb1356u)),iVar7);
  uVar6 = FUN_000d1da0(0xffc0);
  (*((short *)camry_host_ptr((uint32_t)(puVar3 + 0x149c)))) = (short)iVar7;
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + 0x149e)))) = uVar5;
  FUN_000d1dc6(uVar6);
  return;
}



/* Signed16 axis and ordinate pairs; 7FFF axis sentinel returns previous ordinate. Endpoint hold or
   signed32 linear interpolation with sign-extended16 result; no table-order/extent validation.
   Signed16 axis/ordinate sentinel interpolation. SXH R7 atD0768;7FFF sentinel returns prior
   ordinate; endpoint and signed32 interpolation return signed16 result. Table order and extent
   unchecked. */

int f33_interpolate_signed_sentinel_curve(short *points,short input)

{
  short *psVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  
  iVar4 = (int)input;
  iVar2 = (int)*points;
  if ((iVar2 != 0x7fff) &&
     (iVar2 - iVar4 < 0 != (iVar2 < 0 != iVar4 < 0 && iVar4 < 0 == iVar2 - iVar4 < 0))) {
    iVar2 = 0;
    while( true ) {
      psVar1 = points + iVar2 * 2;
      iVar3 = (int)*psVar1;
      if (iVar3 == 0x7fff) {
        return (int)psVar1[-1];
      }
      if (iVar3 - iVar4 < 0 == (iVar3 < 0 != iVar4 < 0 && iVar4 < 0 == iVar3 - iVar4 < 0)) break;
      iVar2 = iVar2 + 1;
    }
    iVar3 = iVar3 - psVar1[-2];
    iVar2 = (iVar4 - psVar1[-2]) * ((int)psVar1[1] - (int)psVar1[-1]);
    if (iVar3 != 0) {
      if (iVar2 == -0x80000000 && iVar3 == -1) {
        iVar2 = 0;
      }
      else {
        iVar2 = iVar2 / iVar3;
      }
    }
    return (int)(short)(psVar1[-1] + (short)iVar2);
  }
  return (int)points[1];
}



int FUN_000d07ba(short *param_1,short param_2)

{
  int iVar1;
  int iVar2;
  int iVar3;
  
  iVar2 = (int)param_2;
  iVar1 = (int)*param_1;
  if ((iVar1 != 0x7fff) &&
     (iVar1 - iVar2 < 0 != (iVar1 < 0 != iVar2 < 0 && iVar2 < 0 == iVar1 - iVar2 < 0))) {
    iVar1 = 0;
    while( true ) {
      iVar3 = (int)param_1[iVar1 * 2 + 2];
      if ((iVar3 - iVar2 < 0 == (iVar3 < 0 != iVar2 < 0 && iVar2 < 0 == iVar3 - iVar2 < 0) &&
           iVar3 != iVar2) || (iVar3 + -0x7fff < 0 == (iVar3 < 0 && -1 < iVar3 + -0x7fff))) break;
      iVar1 = iVar1 + 1;
    }
    return (int)(param_1 + iVar1 * 2 + 2)[-1];
  }
  return (int)param_1[1];
}



uint FUN_000d07f2(short *param_1,short param_2)

{
  short *psVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  
  iVar4 = (int)param_2;
  iVar2 = (int)*param_1;
  if ((iVar2 != 0x7fff) &&
     (iVar2 - iVar4 < 0 != (iVar2 < 0 != iVar4 < 0 && iVar4 < 0 == iVar2 - iVar4 < 0))) {
    iVar2 = 0;
    while( true ) {
      psVar1 = param_1 + iVar2 * 2;
      iVar3 = (int)*psVar1;
      if (iVar3 == 0x7fff) {
        return (uint)(ushort)psVar1[-1];
      }
      if (iVar3 - iVar4 < 0 == (iVar3 < 0 != iVar4 < 0 && iVar4 < 0 == iVar3 - iVar4 < 0)) break;
      iVar2 = iVar2 + 1;
    }
    iVar3 = iVar3 - psVar1[-2];
    iVar2 = (iVar4 - psVar1[-2]) * ((uint)(ushort)psVar1[1] - (uint)(ushort)psVar1[-1]);
    if (iVar3 != 0) {
      if (iVar2 == -0x80000000 && iVar3 == -1) {
        iVar2 = 0;
      }
      else {
        iVar2 = iVar2 / iVar3;
      }
    }
    return (uint)(ushort)psVar1[-1] + iVar2 & 0xffff;
  }
  return (uint)(ushort)param_1[1];
}



/* Unsigned16 axis, signed16 ordinate pairs; FFFF axis sentinel. Endpoint hold or signed32
   interpolation and sign-extended16 result. SXH and ZXH input contracts differ from D0768.
   Unsigned16 axis and signed16 ordinate sentinel interpolation. ZXH R7 atD0844;FFFF sentinel;
   endpoint and signed32 interpolation return signed16 result. */

int f33_interpolate_unsigned_axis_sentinel_curve(ushort *points,ushort input)

{
  ushort *puVar1;
  int iVar2;
  uint uVar3;
  int iVar4;
  uint uVar5;
  
  uVar3 = (uint)input;
  if ((*points != 0xffff) && (*points < uVar3)) {
    iVar2 = 0;
    while( true ) {
      puVar1 = points + iVar2 * 2;
      uVar5 = (uint)*puVar1;
      if (uVar5 == 0xffff) {
        return (int)(short)puVar1[-1];
      }
      if (uVar3 <= uVar5) break;
      iVar2 = iVar2 + 1;
    }
    iVar2 = uVar5 - puVar1[-2];
    iVar4 = (uVar3 - puVar1[-2]) * ((int)(short)puVar1[1] - (int)(short)puVar1[-1]);
    if (iVar2 != 0) {
      if (iVar4 == -0x80000000 && iVar2 == -1) {
        iVar4 = 0;
      }
      else {
        iVar4 = iVar4 / iVar2;
      }
    }
    return (int)(short)(puVar1[-1] + (short)iVar4);
  }
  return (int)(short)points[1];
}



uint FUN_000d0896(ushort *param_1,uint param_2)

{
  ushort *puVar1;
  int iVar2;
  int iVar3;
  uint uVar4;
  
  param_2 = param_2 & 0xffff;
  if ((*param_1 != 0xffff) && (*param_1 < param_2)) {
    iVar2 = 0;
    while( true ) {
      puVar1 = param_1 + iVar2 * 2;
      uVar4 = (uint)*puVar1;
      if (uVar4 == 0xffff) {
        return (uint)puVar1[-1];
      }
      if (param_2 <= uVar4) break;
      iVar2 = iVar2 + 1;
    }
    iVar2 = uVar4 - puVar1[-2];
    iVar3 = (param_2 - puVar1[-2]) * ((uint)puVar1[1] - (uint)puVar1[-1]);
    if (iVar2 != 0) {
      if (iVar3 == -0x80000000 && iVar2 == -1) {
        iVar3 = 0;
      }
      else {
        iVar3 = iVar3 / iVar2;
      }
    }
    return (uint)puVar1[-1] + iVar3 & 0xffff;
  }
  return (uint)param_1[1];
}



uint FUN_000d08e8(uint *param_1,uint param_2)

{
  uint uVar1;
  uint uVar2;
  undefined8 uVar3;
  uint uVar4;
  uint uVar5;
  int iVar6;
  
  iVar6 = 0;
  if ((*param_1 == 0xffffffff) || (param_2 <= *param_1)) {
    uVar2 = param_1[1];
  }
  else {
    uVar1 = 0;
    while( true ) {
      uVar4 = param_1[uVar1 * 2];
      if ((param_2 < uVar4) || (uVar4 == 0xffffffff)) break;
      uVar1 = uVar1 + 1;
    }
    if (1 < uVar1) {
      iVar6 = uVar1 - 1;
    }
    uVar2 = (param_1 + iVar6 * 2)[1];
    if (uVar4 != 0xffffffff) {
      uVar5 = param_1[iVar6 * 2];
      uVar1 = (param_1 + uVar1 * 2)[1];
      uVar3 = FUN_000d2834(param_2 - uVar5,-(uint)(param_2 < uVar5),uVar1 - uVar2,
                           -(uint)(uVar1 < uVar2));
      iVar6 = FUN_000d28ea((int)uVar3,(int)((ulonglong)uVar3 >> 0x20),uVar4 - uVar5,
                           -(uint)(uVar4 < uVar5));
      uVar2 = iVar6 + uVar2;
    }
  }
  return uVar2;
}



/* SXH input, negate nonpositive input, then SXH R10 again. INT16_MIN remains-32768; the physical
   R10 result is sign-extended32. Signed16 return makes the narrowing explicit in C rather than
   falsely returning+32768. Not a saturating absolute value. Signed16 input and final SXH R10 make
   INT16_MIN remain negative. Formal signed16 return preserves the narrowing; not saturating
   absolute value. */

short f33_abs_s16_wrapping(short value)

{
  if (0 < value) {
    return value;
  }
  return -value;
}



/* Return positive input unchanged, otherwise low32 negation. INT32_MIN remains negative. C
   unary-minus spelling does not establish a nonnegative result over all32-bit inputs. Signed32
   absolute-value negation wraps at INT32_MIN. Tracking predicates must not assume every return is
   nonnegative. */

int f33_abs_s32_wrapping(int value)

{
  if (value < 1) {
    value = -value;
  }
  return value;
}



void FUN_000d097a(ushort *param_1,uint param_2,undefined2 *param_3,undefined2 *param_4)

{
  int iVar1;
  ushort *puVar2;
  int iVar3;
  int iVar4;
  
  param_2 = param_2 & 0xffff;
  iVar3 = 0;
  if (*param_1 < param_2) {
    for (; (puVar2 = param_1 + iVar3, puVar2[1] < param_2 && (puVar2[1] != 0xffff));
        iVar3 = (int)(short)((short)iVar3 + 1)) {
    }
    iVar4 = 0x400;
    if (puVar2[1] == 0xffff) {
      iVar3 = iVar3 + -1;
    }
    else if (puVar2[1] != *puVar2) {
      iVar4 = (param_2 - *puVar2) * 0x400;
      iVar1 = (uint)puVar2[1] - (uint)*puVar2;
      if (iVar1 != 0) {
        if (iVar4 == -0x80000000 && iVar1 == -1) {
          iVar4 = 0;
        }
        else {
          iVar4 = iVar4 / iVar1;
        }
      }
    }
  }
  else {
    iVar4 = 0;
  }
  *param_3 = (short)iVar3;
  *param_4 = (short)iVar4;
  return;
}



void FUN_000d0a06(int param_1,int param_2,int *param_3)

{
  int iVar1;
  
  if (param_1 < 1) {
    if ((param_2 < 1) &&
       (iVar1 = -0x7fffffff - param_1,
       iVar1 - param_2 < 0 == (iVar1 < 0 != param_2 < 0 && param_2 < 0 == iVar1 - param_2 < 0) &&
       iVar1 != param_2)) {
      param_2 = -0x7fffffff;
      goto LAB_000d0a3a;
    }
  }
  else if ((0 < param_2) &&
          (iVar1 = (0x7fffffff - param_1) - param_2,
          iVar1 < 0 != (0x7fffffff - param_1 < 0 != param_2 < 0 && param_2 < 0 == iVar1 < 0))) {
    param_2 = 0x7fffffff;
    goto LAB_000d0a3a;
  }
  param_2 = param_2 + param_1;
LAB_000d0a3a:
  *param_3 = param_2;
  return;
}



/* Sequential initializer chain: 26 unconditional calls and no other statements; shape-verified. The
   called sequence is the function's entire behavior; chain family members differ in callee sets. */

void f33_run_init_chain_d0a3e(void)

{
  f33_initialize_assist_surface_selection();
  f33_initialize_assist_torque_conditioner();
  f33_initialize_torque_memory_correction();
  f33_fill_constant_block_c7a76();
  FUN_000c557a();
  f33_fill_constant_block_c589e();
  f33_fill_constant_block_c59ae();
  f33_fill_constant_block_c6138();
  f33_fill_constant_block_c635a();
  FUN_000c28ae();
  f33_fill_constant_block_c73c4();
  FUN_000c8642();
  f33_fill_constant_block_c8970();
  FUN_000c6d84();
  f33_initialize_nonlinear_torque_compensation();
  f33_initialize_three_term_compensation();
  f33_fill_constant_block_cc596();
  f33_fill_constant_block_c962e();
  FUN_000cba80();
  FUN_000d0130();
  f33_fill_constant_block_d04f0();
  f33_fill_constant_block_d01b4();
  f33_fill_constant_block_c79a0();
  f33_initialize_torque_memory_gain();
  FUN_000c873e();
  FUN_000c6be0();
  return;
}



/* Sequentially publish selected CC64 to AC54, normal gated CC66 to AC76, and pre-final-clamp/gate
   CC62 to AC56. Also copy CC60/CC68 and independent C128/C172 snapshots; publish override
   indication and AC3F=5A. Sequential RAM stores are not an all-reader atomic transaction.
   Sequentially publish selected command, pre-clamp/gate mirror, amplitude limit and independent
   diagnostic snapshots. Native case preserves selected0 versus pre-clamp -1. No atomic cross-reader
   snapshot claim. */

void f33_publish_command_snapshot(void)

{
  DAT_febeac39 = 0;
  DAT_febeac54 = DAT_febecc64;
  DAT_febeac76 = DAT_febecc66;
  DAT_febeac56 = DAT_febecc62;
  DAT_febeac58 = DAT_febec128;
  DAT_febeac68 = DAT_febecc60;
  DAT_febeac7e = DAT_febecc68;
  DAT_febeac2d = 0;
  if (DAT_febecc98 != '\0') {
    DAT_febeac2d = 0x5a;
  }
  DAT_febeac3e = 0;
  DAT_febeac70 = DAT_febec172;
  DAT_febeac3f = 0x5a;
  return;
}



/* Capture AC31 once. Non5A skips selected producers while torque conditioning, base assistance and
   other retained filters still advance. D0162 precedes fresh C266/C3BA/C4C0; D0218 sees those new
   direct terms but the earlier nested aggregate. Finish through command clamp/gate/publication.
   Capture AC31 once; selective producer holds coexist with advancing filters and aggregation.
   Nested D0162 precedes fresh direct dynamic terms. Exact scheduling/dataflow contract; not
   exhaustive native execution of all assist branches. */

void f33_run_assist_command_slice(void)

{
  char cVar1;
  
  cVar1 = DAT_febeac31;
  f33_update_retained_assist_surface_source();
  f33_publish_assist_surface_selector();
  FUN_000c9bce();
  if (cVar1 == 'Z') {
    FUN_000c55b4();
    f33_update_torque_memory_correction();
    FUN_000c5a84();
    FUN_000c5c44();
  }
  FUN_000c55ee();
  FUN_000c6128();
  FUN_000c5e24();
  FUN_000c5eae();
  f33_publish_bounded_assist_torque_input();
  if (cVar1 == 'Z') {
    f33_update_torque_conditioner_slope_blend();
    FUN_000cc8d6();
    FUN_000cc984();
    FUN_000c65c8();
    FUN_000c8dd2();
    f33_compose_observer_dependent_assist();
    FUN_000c7b44();
    FUN_000c7c58();
    f33_update_torque_conditioner_reseed_selector();
  }
  f33_repair_assist_torque_conditioner_state();
  f33_condition_assist_torque();
  f33_update_signed_speed_torque_assist();
  f33_update_nonlinear_torque_compensation();
  if (cVar1 == 'Z') {
    f33_update_assist_torque_input_delta();
    f33_update_nonlinear_torque_slope();
    f33_publish_combined_assist_slope();
  }
  f33_sum_nonlinear_and_moving_assist();
  f33_bound_nonlinear_and_moving_assist();
  f33_aggregate_internal_assist_terms();
  f33_repair_torque_rate_filter_state();
  f33_filter_torque_rate_compensation_input();
  if (cVar1 == 'Z') {
    f33_map_first_model_derivative_compensation();
    f33_map_second_model_derivative_compensation();
    f33_publish_model_derivative_compensation();
    f33_update_torque_rate_assist_compensation();
    FUN_000cbf9e();
  }
  f33_bound_three_term_compensation();
  f33_aggregate_assist_command();
  FUN_000d0284();
  f33_filter_command_slew();
  FUN_000d0382();
  f33_compose_command_sources();
  f33_scale_clamp_gate_command();
  FUN_000d06d6();
  f33_select_final_command();
  f33_publish_command_snapshot();
  return;
}



void FUN_000d0bda(void)

{
  DAT_febecca0 = 1;
  DAT_febecca1 = 9;
  FUN_000c5686();
  FUN_000c5792();
  f33_reset_rate_observer();
  f33_initialize_retained_estimator_qualification();
  f33_fill_constant_block_c4a06();
  FUN_000c8fb6();
  f33_fill_constant_block_cff78();
  f33_fill_constant_block_cfe8e();
  FUN_000cfd0a();
  f33_fill_constant_block_cf684();
  return;
}



/* Copy external-source qualifierBFC5 toAC08; under PMRFFC0 publish C084->AC1C and C08E->AC09. Do
   not conflate this interface snapshot with the direct nested-assist consumers. Publish external
   qualifier BFC5 into AC08 and protected observer rate/state C084/C08E into AC1C/AC09. Separate
   snapshots do not form one atomic whole-control generation. */

void f33_publish_rate_observer_interface(void)

{
  uint32_t puVar1;
  undefined4 uVar2;
  
  puVar1 = 0xfebeb800u;
  DAT_febeac08 = DAT_febebfc5;
  uVar2 = FUN_000d1da0(0xffc0);
  (*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + -0xbe4)))) = (*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + 0x884))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0xbf7))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x88e)))));
  FUN_000d1dc6(uVar2);
  return;
}



/* Capture CCA0/CCA1. Alternate observer acquisition and C472 publication use old CCA0==1; increment
   modulo2/modulo10 afterward. This is software generation ordering, not a clock or jitter
   measurement. */

void f33_run_observer_publication_slice(void)

{
  char cVar1;
  char cVar2;
  uint32_t puVar3;
  char cVar4;
  byte bVar5;
  
  cVar2 = DAT_febecca1;
  cVar1 = DAT_febecca0;
  puVar3 = 0xfebeb800u;
  if (DAT_febecca0 == '\x01') {
    puVar3 = 0xfebeb800u;
    FUN_000c57cc();
    FUN_000c5806();
    FUN_000c56c0();
  }
  FUN_000c56fa();
  if (cVar1 == '\x01') {
    f33_qualify_rate_observer_acquisition();
  }
  f33_commit_rate_observer();
  f33_update_rate_observer_deadband();
  if (cVar1 == '\x01') {
    FUN_000c8de6();
    FUN_000c709e();
    FUN_000c70d6();
    FUN_000c6e7e();
    FUN_000c6fde();
    f33_map_observer_rate_to_assist_bound();
    f33_update_observer_dependent_assist_bound();
    FUN_000c731c();
    FUN_000c6f1e();
  }
  if (cVar2 == '\t') {
    FUN_000c9524();
  }
  if (cVar1 == '\x01') {
    FUN_000c94b8();
    f33_publish_directional_rate_compensation();
    FUN_000c8f90();
  }
  FUN_000d04ac();
  FUN_000cff04();
  f33_update_windowed_excitation();
  cVar4 = cVar2 + '\x01';
  bVar5 = cVar1 + 1;
  if (1 < bVar5) {
    bVar5 = 0;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(0x14a0))))) = bVar5;
  if (9 < (byte)(cVar2 + 1U)) {
    cVar4 = '\0';
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(0x14a1))))) = cVar4;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0xbfb))))) = bVar5;
  f33_publish_rate_observer_interface();
  return;
}



/* Sequential initializer chain: 31 unconditional calls and no other statements; shape-verified. The
   called sequence is the function's entire behavior; chain family members differ in callee sets. */

void f33_run_init_chain_d0ce8(void)

{
  f33_fill_constant_block_c2c78();
  f33_return_only_stub_c37b8();
  FUN_000c3edc();
  FUN_000d06ea();
  FUN_000c66ce();
  FUN_000c7540();
  f33_fill_constant_block_c8df6();
  f33_initialize_angle_rate_compensation();
  f33_initialize_directional_rate_compensation();
  FUN_000c81ee();
  FUN_000c8224();
  f33_fill_constant_block_c9160();
  FUN_000c9562();
  f33_fill_constant_block_c9590();
  f33_fill_constant_block_c9c7c();
  f33_fill_constant_block_c9df2();
  f33_fill_constant_block_cc148();
  f33_fill_constant_block_cc038();
  FUN_000cb548();
  FUN_000cb1e8();
  FUN_000cc530();
  f33_fill_constant_block_c65f0();
  FUN_000ceff4();
  f33_fill_constant_block_ce750();
  f33_fill_constant_block_cec0c();
  f33_fill_constant_block_ce964();
  FUN_000cc9ac();
  FUN_000cf056();
  f33_fill_constant_block_cf35c();
  f33_fill_constant_block_cfd88();
  FUN_000cff6e();
  return;
}



void FUN_000d0d6c(void)

{
  FUN_000c9f1e();
  f33_copy_cell_block_cf5ee();
  return;
}



/* WARNING: Removing unreachable block (ram,0x000d0eca) */
/* WARNING: Removing unreachable block (ram,0x000d0e34) */
/* WARNING: Removing unreachable block (ram,0x000d0db8) */
/* WARNING: Removing unreachable block (ram,0x000d0d90) */

void FUN_000d0d7c(void)

{
  uint uVar1;
  int iVar2;
  int iVar3;
  
  uVar1 = (uint)DAT_febeae3c;
  iVar3 = (int)((int)DAT_febec5ee * uVar1) / 0x8000;
  if (iVar3 + -0x569a < 0 == (iVar3 < 0 && -1 < iVar3 + -0x569a) && iVar3 != 0x569a) {
    iVar3 = 0x569a;
  }
  else if (iVar3 + 0x569a < 0 != (-1 < iVar3 && iVar3 + 0x569a < 0)) {
    iVar3 = -0x569a;
  }
  iVar2 = (int)((int)DAT_febec85e * uVar1) / 0x8000;
  if (iVar2 + -0x569a < 0 == (iVar2 < 0 && -1 < iVar2 + -0x569a) && iVar2 != 0x569a) {
    iVar2 = 0x569a;
  }
  else if (iVar2 + 0x569a < 0 != (-1 < iVar2 && iVar2 + 0x569a < 0)) {
    iVar2 = -0x569a;
  }
  DAT_febeae12 = (undefined2)iVar3;
  DAT_febeae16 = (undefined2)iVar2;
  DAT_febead0a = 0;
  DAT_febeacf1 = DAT_febec5f4;
  DAT_febead09 = 0;
  DAT_febead0b = 0;
  DAT_febead15 = 0;
  DAT_febeacf5 = DAT_febec862;
  DAT_febead16 = 0;
  DAT_febead17 = 0;
  DAT_febeaed2 = 0;
  DAT_febeacf6 = DAT_febec835;
  DAT_febeaed4 = 0;
  DAT_febead33 = 0;
  DAT_febead39 = 0;
  DAT_febeacf7 = DAT_febec863;
  DAT_febeae58 = 0;
  DAT_febeacf8 = DAT_febec865;
  DAT_febead14 = DAT_febec861;
  DAT_febeae36 = DAT_febecc6a;
  iVar3 = (int)((int)DAT_febecb38 * uVar1) / 0x8000;
  if (iVar3 + -0x569a < 0 == (iVar3 < 0 && -1 < iVar3 + -0x569a) && iVar3 != 0x569a) {
    iVar3 = 0x569a;
  }
  else if (iVar3 + 0x569a < 0 != (-1 < iVar3 && iVar3 + 0x569a < 0)) {
    iVar3 = -0x569a;
  }
  DAT_febeae6e = (undefined2)iVar3;
  DAT_febead45 = 0;
  DAT_febead46 = 0;
  DAT_febead60 = DAT_febecb57;
  DAT_febead49 = 0;
  DAT_febead8f = 0;
  DAT_febead90 = 0;
  DAT_febead67 = DAT_febecb58;
  DAT_febead9f = 0;
  DAT_febeada0 = 0;
  DAT_febeada1 = 0;
  DAT_febead42 = DAT_febecafc;
  DAT_febead91 = 0;
  DAT_febead92 = 0;
  DAT_febead93 = 0;
  DAT_febead43 = DAT_febecab6;
  DAT_febead94 = 0;
  DAT_febead95 = 0;
  DAT_febead96 = 0;
  DAT_febead44 = DAT_febecab7;
  DAT_febeada9 = 0;
  DAT_febead97 = 0;
  DAT_febeaf10 = 0;
  DAT_febead47 = DAT_febecaac;
  DAT_febeaf14 = 0;
  DAT_febeaf2c = 0;
  DAT_febead48 = DAT_febecaad;
  DAT_febead4a = DAT_febecad8;
  DAT_febead4b = DAT_febecad9;
  DAT_febeae82 = 0;
  DAT_febeae80 = 0;
  DAT_febeae84 = 0;
  DAT_febeae5c = DAT_febecad2 / 2;
  DAT_febeae86 = 0;
  DAT_febead9e = 0;
  DAT_febeadab = 0;
  DAT_febeaddf = DAT_febec7bf;
  DAT_febeadde = DAT_febec7be;
  FUN_000d0d6c();
  return;
}



void FUN_000d0eec(void)

{
  byte bVar1;
  
  bVar1 = DAT_febeacbc;
  f33_qualify_assist_surface_transition();
  FUN_000c566c();
  FUN_000c5778();
  FUN_000c5884();
  FUN_000c956a();
  if ((bVar1 & 8) != 0) {
    FUN_000c58b8();
    FUN_000c5910();
    FUN_000c5956();
    FUN_000c5f38();
    FUN_000c74e2();
    FUN_000c9ba6();
    FUN_000cc66e();
    FUN_000c7966();
    FUN_000c8ecc();
    FUN_000c8a78();
    FUN_000c6f86();
    FUN_000c713c();
    f33_update_nonlinear_torque_speed_gain();
    f33_update_angle_rate_compensation_speed_gain();
    f33_update_directional_rate_speed_gain();
    FUN_000c82a8();
    FUN_000c9a5c();
    FUN_000c9258();
    FUN_000c91f2();
    f33_update_torque_memory_speed_gain();
    FUN_000d06fa();
  }
  if ((bVar1 >> 4 & 1) != 0) {
    FUN_000c81f8();
  }
  if ((bVar1 & 4) != 0) {
    FUN_000d0716();
  }
  if ((bVar1 & 2) != 0) {
    FUN_000c71b6();
    FUN_000c2cc0();
    f33_run_raw_estimator_cycle();
  }
  f33_update_angle_rate_compensation();
  FUN_000c9650();
  FUN_000c9caa();
  FUN_000c9d18();
  FUN_000c98ae();
  FUN_000c9812();
  FUN_000c973a();
  FUN_000c9a84();
  FUN_000c9e44();
  FUN_000c9eea();
  FUN_000c9d86();
  FUN_000c854a();
  FUN_000c9b04();
  FUN_000c6af6();
  FUN_000c878a();
  thunk_FUN_000cefa4();
  FUN_000cf04a();
  FUN_000cc514();
  FUN_000cc1b6();
  FUN_000cc32a();
  FUN_000cc3be();
  FUN_000cc43a();
  FUN_000cc07a();
  FUN_000cc114();
  FUN_000cc130();
  FUN_000cb2a2();
  FUN_000cb5e4();
  FUN_000cb45e();
  FUN_000cb81c();
  FUN_000cb9e2();
  FUN_000cb82c();
  FUN_000cbb66();
  FUN_000cbc80();
  FUN_000cbcb8();
  FUN_000cbd64();
  FUN_000cbe28();
  FUN_000cb246();
  FUN_000cb2f8();
  FUN_000cb396();
  FUN_000cb3f4();
  f33_update_angle_feedback_offset_and_publication();
  FUN_000ceb92();
  FUN_000ce8ca();
  f33_run_init_chain_cef0e();
  FUN_000cef26();
  FUN_000cec72();
  f33_update_selected_angle_target();
  FUN_000ce6cc();
  f33_shape_angle_controller_target();
  f33_publish_angle_controller_target_triplicate();
  f33_update_angle_controller_output_envelope();
  FUN_000cf5de();
  f33_update_torque_memory_gain();
  FUN_000c7a18();
  FUN_000c9124();
  FUN_000c6d4e();
  FUN_000c890e();
  FUN_000c666c();
  FUN_000c7d14();
  FUN_000c7dd4();
  FUN_000cfda0();
  FUN_000cfe64();
  if ((bVar1 & 8) != 0) {
    FUN_000c7b34();
    FUN_000cffa2();
  }
  if ((bVar1 & 2) != 0) {
    FUN_000c92b2();
    FUN_000c9314();
    FUN_000c945e();
    FUN_000cc5ac();
    FUN_000cc5da();
    FUN_000cc6ba();
    FUN_000cc878();
    FUN_000c84f8();
    FUN_000c6aa4();
    FUN_000c7912();
  }
  if ((bVar1 & 4) != 0) {
    f33_qualify_opposed_rate_direction();
    f33_filter_directional_rate_compensation();
    FUN_000c8e1c();
    FUN_000c8ef4();
  }
  FUN_000d0d7c();
  return;
}



void FUN_000d10d4(void)

{
  FUN_000c9e18();
  FUN_000cf442();
  return;
}



void FUN_000d10e4(void)

{
  FUN_000c9e0a();
  FUN_000cf370();
  return;
}



void FUN_000d1100(void)

{
  f33_run_assist_command_slice();
  return;
}



/* Far-call trampoline: prepare {lp},0 / jarl 0xD0BDA / dispose 0,{lp},lp; byte-verified against the
   exact image. Forwards with registers and stack unchanged; marked as a thunk. Forwarding shape
   machine-verified; target semantics not recovered. */

void thunk_FUN_000d0bda(void)

{
  FUN_000d0bda();
  return;
}



void FUN_000d1118(void)

{
  f33_run_observer_publication_slice();
  return;
}



/* Far-call trampoline: prepare {lp},0 / jarl 0xD0EEC / dispose 0,{lp},lp; byte-verified against the
   exact image. Forwards with registers and stack unchanged; marked as a thunk. Forwarding shape
   machine-verified; target semantics not recovered. */

void thunk_FUN_000d0eec(void)

{
  FUN_000d0eec();
  return;
}



/* Far-call trampoline: prepare {lp},0 / jarl 0xD10E4 / dispose 0,{lp},lp; byte-verified against the
   exact image. Forwards with registers and stack unchanged; marked as a thunk. Forwarding shape
   machine-verified; target semantics not recovered. */

void thunk_FUN_000d10e4(void)

{
  FUN_000d10e4();
  return;
}



/* Far-call trampoline: prepare {lp},0 / jarl 0xD10D4 / dispose 0,{lp},lp; byte-verified against the
   exact image. Forwards with registers and stack unchanged; marked as a thunk. Forwarding shape
   machine-verified; target semantics not recovered. */

void thunk_FUN_000d10d4(void)

{
  FUN_000d10d4();
  return;
}



void FUN_000d1154(void)

{
  f33_publish_retained_estimator_projection();
  return;
}



void FUN_000d1160(void)

{
  f33_snapshot_retained_estimator_projection();
  return;
}



/* Far-call trampoline: prepare {lp},0 / jarl 0xD0D6C / dispose 0,{lp},lp; byte-verified against the
   exact image. Forwards with registers and stack unchanged; marked as a thunk. Forwarding shape
   machine-verified; target semantics not recovered. */

void thunk_FUN_000d0d6c(void)

{
  FUN_000d0d6c();
  return;
}



void FUN_000d1178(short param_1,short *param_2)

{
  int iVar1;
  
  iVar1 = (int)param_1;
  if (iVar1 + 0x7fff < 0 == (-1 < iVar1 && iVar1 + 0x7fff < 0) && iVar1 != -0x7fff) {
    if (iVar1 < 0) {
      param_1 = -param_1;
    }
  }
  else {
    param_1 = 0x7fff;
  }
  *param_2 = param_1;
  return;
}



void FUN_000d1194(int param_1,int *param_2)

{
  if (param_1 + 0x7fffffff < 0 == (-1 < param_1 && param_1 + 0x7fffffff < 0) &&
      param_1 != -0x7fffffff) {
    if (param_1 < 0) {
      param_1 = -param_1;
    }
  }
  else {
    param_1 = 0x7fffffff;
  }
  *param_2 = param_1;
  return;
}



void FUN_000d11d6(undefined4 param_1,undefined4 param_2,undefined1 *param_3)

{
  *param_3 = (char)((uint)param_1 >> 8);
  param_3[1] = (char)param_1;
  param_3[2] = (char)((uint)param_2 >> 8);
  param_3[3] = (char)param_2;
  return;
}



void FUN_000d1222(short param_1,int *param_2)

{
  int iVar1;
  
  iVar1 = (int)param_1;
  if (iVar1 < 1) {
    iVar1 = 0;
  }
  *param_2 = iVar1;
  return;
}



void FUN_000d1232(short param_1,uint param_2,uint param_3,short *param_4)

{
  int iVar1;
  int iVar2;
  
  param_3 = param_3 & 0xffff;
  if (((param_2 & 0xffff) != 0) && (param_3 != 0)) {
    iVar2 = (int)param_1 * (param_2 & 0xffff);
    if (param_3 != 0) {
      if (iVar2 == -0x80000000 && param_3 == 0xffffffff) {
        iVar2 = -0x80000000;
      }
      else {
        iVar2 = iVar2 / (int)param_3;
      }
    }
    if (iVar2 + 0x7fff < 0 == (-1 < iVar2 && iVar2 + 0x7fff < 0) && iVar2 != -0x7fff) {
      iVar1 = 0x7fff;
      if ((iVar2 + -0x7fff < 0 != (iVar2 < 0 && -1 < iVar2 + -0x7fff) || iVar2 == 0x7fff) &&
         (iVar1 = iVar2,
         iVar2 + 0x8000 < 0 != (-1 < iVar2 && iVar2 + 0x8000 < 0) || iVar2 == -0x8000)) {
        iVar1 = -0x8000;
      }
      param_1 = (short)iVar1;
    }
    else {
      param_1 = -0x7fff;
    }
  }
  *param_4 = param_1;
  return;
}



void FUN_000d1272(uint param_1,uint param_2,uint param_3,uint *param_4)

{
  uint uVar1;
  uint local_c;
  
  param_3 = param_3 & 0xffff;
  param_2 = param_2 & 0xffff;
  uVar1 = param_1;
  if ((param_2 == 0) || (uVar1 = param_1, param_3 == 0)) goto LAB_000d12c4;
  if ((int)((ulonglong)((longlong)(int)param_2 * (longlong)(int)param_1) >> 0x20) + 1U < 2) {
    uVar1 = param_1 * param_2;
    if ((int)param_1 < 0) {
      if (uVar1 < 0x80000001) goto LAB_000d12b4;
    }
    else if (0x7fffffff < uVar1) goto LAB_000d12b4;
    if (param_3 != 0) {
      if (uVar1 == 0x80000000 && param_3 == 0xffffffff) {
        uVar1 = 0x80000000;
      }
      else {
        uVar1 = (int)uVar1 / (int)param_3;
      }
    }
  }
  else {
LAB_000d12b4:
    if (param_3 != 0) {
      if (param_1 == 0x80000000 && param_3 == 0xffffffff) {
        param_1 = 0x80000000;
      }
      else {
        param_1 = (int)param_1 / (int)param_3;
      }
    }
    FUN_000d2330(param_1,param_2,&local_c);
    uVar1 = local_c;
  }
LAB_000d12c4:
  local_c = uVar1;
  *param_4 = local_c;
  return;
}



/* 8-bytesample prevU16,targetU16,accU32. Coefficientoutside1..65535 becomes65536. Low32 unsigned
   recurrence,logicalhigh16output andwordaccumulatorthroughr8/r9. Reusehelper,nonewphysicalmodel. */

void f33_filter_unsigned_sample_accumulator
               (ushort *sample,uint coefficient,ushort *output,uint *accumulator)

{
  uint uVar1;
  
  if (0xfffe < coefficient - 1) {
    coefficient = 0x10000;
  }
  uVar1 = sample[1] * coefficient + (*(int *)(sample + 2) - *sample * coefficient);
  *output = (ushort)(uVar1 >> 0x10);
  *accumulator = uVar1;
  return;
}



/* Application copy of ten-byte latched-monitor reset: clear+0word,+4/+6/+8halfwords; preserve
   allocationtail. */

void f33_reset_application_latched_monitor(F33LatchedMonitorState *state)

{
  state->packed_status = 0;
  state->passing_count = 0;
  state->failing_count = 0;
  state->failing_high_water = 0;
  return;
}



undefined4 FUN_000d1824(uint *param_1,ushort *param_2,undefined4 *param_3)

{
  ushort uVar1;
  ushort uVar2;
  ushort uVar3;
  ushort uVar4;
  short sVar5;
  uint uVar6;
  uint uVar7;
  int iVar8;
  ushort uVar9;
  ushort uVar10;
  ushort uVar11;
  ushort uVar12;
  ushort uVar13;
  code *pcVar14;
  
  uVar11 = (ushort)param_1[1];
  uVar10 = (*((ushort *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 6))));
  uVar13 = (ushort)param_1[2];
  uVar12 = (*((ushort *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 10))));
  uVar9 = (ushort)param_1[3];
  uVar1 = param_2[1];
  uVar2 = *param_2;
  uVar3 = param_2[2];
  uVar4 = param_2[3];
  if (uVar13 == 0) {
    if (uVar2 < uVar11) {
      sVar5 = 0x2200;
    }
    else {
      sVar5 = 0;
      if (uVar11 != 0) {
        sVar5 = 0x1100;
      }
    }
  }
  else {
    sVar5 = 0x22;
    if (uVar13 <= uVar3) {
      sVar5 = 0x11;
    }
  }
  if (sVar5 == 0) {
    iVar8 = (*(int (*)())*param_3)();
    if (iVar8 == 0x11) {
      if ((uVar1 < uVar10) || (uVar10 = uVar10 + 1, uVar1 < uVar10)) {
        uVar11 = 0;
        uVar10 = 0;
        uVar6 = 0;
      }
      else if ((uVar2 < uVar11) || (uVar11 = uVar11 + 1, uVar2 < uVar11)) {
        uVar6 = 0x2200;
      }
      else {
        uVar6 = 0x11001100;
      }
      uVar13 = 0;
      uVar12 = 0;
    }
    else if (iVar8 == 0x22) {
      uVar11 = 0;
      uVar10 = 0;
      if ((uVar4 < uVar12) || (uVar12 = uVar12 + 1, uVar4 < uVar12)) goto LAB_000d1b52;
      if (uVar13 <= uVar3) {
        uVar13 = uVar13 + 1;
      }
      uVar1 = uVar13;
      if (uVar13 <= uVar9) {
        uVar1 = uVar9;
      }
      uVar9 = uVar1;
      uVar6 = 0x22;
      if (uVar13 <= uVar3) {
        uVar6 = 0x110011;
      }
    }
    else if ((iVar8 == 0x33) || (iVar8 == 0x44)) {
LAB_000d1b52:
      uVar11 = 0;
      uVar10 = 0;
      uVar12 = 0;
      uVar6 = 0;
      uVar13 = uVar10;
    }
    else {
      uVar6 = 0;
    }
    uVar7 = uVar6 & 0xffff;
    if (uVar7 != 0) {
      if (uVar7 == 0x11) {
        if ((uintptr_t)((code *)param_3[6])!=(uintptr_t)(f33_reset_vector)) {
          (*(int (*)())param_3[6])();
        }
        pcVar14 = (code *)param_3[0xb];
      }
      else if (uVar7 == 0x22) {
        if ((uintptr_t)((code *)param_3[6])!=(uintptr_t)(f33_reset_vector)) {
          (*(int (*)())param_3[6])();
        }
        if ((uintptr_t)((code *)param_3[8])!=(uintptr_t)(f33_reset_vector)) {
          (*(int (*)())param_3[8])();
        }
        pcVar14 = (code *)param_3[0xc];
      }
      else if (uVar7 == 0x1100) {
        if ((uintptr_t)((code *)param_3[2])!=(uintptr_t)(f33_reset_vector)) {
          (*(int (*)())param_3[2])();
        }
        pcVar14 = (code *)param_3[9];
      }
      else {
        if (uVar7 != 0x2200) {
          uVar6 = 0;
          goto LAB_000d1cc6;
        }
        if ((uintptr_t)((code *)param_3[2])!=(uintptr_t)(f33_reset_vector)) {
          (*(int (*)())param_3[2])();
        }
        if ((uintptr_t)((code *)param_3[4])!=(uintptr_t)(f33_reset_vector)) {
          (*(int (*)())param_3[4])();
        }
        pcVar14 = (code *)param_3[10];
      }
      if ((uintptr_t)(pcVar14)!=(uintptr_t)(f33_reset_vector)) {
        (*(int (*)())pcVar14)();
      }
    }
    goto LAB_000d1cc6;
  }
  if (sVar5 == 0x11) {
    iVar8 = (*(int (*)())param_3[1])();
    if ((uVar4 < uVar12) || (uVar12 = uVar12 + 1, uVar4 < uVar12)) {
LAB_000d1c4e:
      uVar11 = 0;
      uVar10 = 0;
      uVar13 = 0;
      uVar12 = 0;
      uVar6 = 0;
    }
    else {
      if (iVar8 == 0x11) {
LAB_000d1c48:
        uVar11 = 0;
        uVar10 = uVar11;
      }
      else {
        if (iVar8 == 0x22) {
          uVar11 = 0;
          uVar10 = 0;
          if (uVar13 <= uVar3) {
            uVar13 = uVar13 + 1;
          }
          uVar1 = uVar13;
          if (uVar13 <= uVar9) {
            uVar1 = uVar9;
          }
          uVar9 = uVar1;
          uVar6 = 0x22;
          if (uVar13 <= uVar3) {
            uVar6 = 0x110011;
          }
          goto LAB_000d1c58;
        }
        if (iVar8 == 0x33) goto LAB_000d1c48;
        if (iVar8 == 0x44) goto LAB_000d1c4e;
      }
      uVar6 = 0x11;
    }
LAB_000d1c58:
    uVar7 = uVar6 & 0xffff;
    if (uVar7 == 0) {
      if ((uintptr_t)((code *)param_3[7])!=(uintptr_t)(f33_reset_vector)) {
        (*(int (*)())param_3[7])();
      }
    }
    else {
      if (uVar7 == 0x11) {
        pcVar14 = (code *)param_3[0xb];
      }
      else {
        if (uVar7 != 0x22) {
          if ((uintptr_t)((code *)param_3[0xb])!=(uintptr_t)(f33_reset_vector)) {
            (*(int (*)())param_3[0xb])();
          }
          uVar6 = 0x11;
          goto LAB_000d1cc6;
        }
        if ((uintptr_t)((code *)param_3[8])!=(uintptr_t)(f33_reset_vector)) {
          (*(int (*)())param_3[8])();
        }
        pcVar14 = (code *)param_3[0xc];
      }
      if ((uintptr_t)(pcVar14)!=(uintptr_t)(f33_reset_vector)) {
        (*(int (*)())pcVar14)();
      }
    }
    goto LAB_000d1cc6;
  }
  if (sVar5 == 0x1100) {
    iVar8 = (*(int (*)())*param_3)();
    if ((uVar1 < uVar10) || (uVar10 = uVar10 + 1, uVar1 < uVar10)) {
LAB_000d1a0c:
      uVar11 = 0;
      uVar10 = 0;
      uVar12 = 0;
      uVar6 = 0;
      uVar13 = uVar10;
    }
    else if (iVar8 == 0x11) {
      if ((uVar2 < uVar11) || (uVar11 = uVar11 + 1, uVar2 < uVar11)) {
        uVar6 = 0x2200;
      }
      else {
        uVar6 = 0x11001100;
      }
      uVar13 = 0;
      uVar12 = 0;
    }
    else if (iVar8 == 0x22) {
      uVar11 = 0;
      uVar10 = 0;
      if ((uVar4 < uVar12) || (uVar12 = uVar12 + 1, uVar4 < uVar12)) goto LAB_000d1a0c;
      if (uVar13 <= uVar3) {
        uVar13 = uVar13 + 1;
      }
      uVar1 = uVar13;
      if (uVar13 <= uVar9) {
        uVar1 = uVar9;
      }
      uVar9 = uVar1;
      uVar6 = 0x22;
      if (uVar13 <= uVar3) {
        uVar6 = 0x110011;
      }
    }
    else {
      if (iVar8 == 0x33) {
        uVar13 = 0;
        uVar12 = uVar13;
      }
      else if (iVar8 == 0x44) goto LAB_000d1a0c;
      uVar6 = 0x1100;
    }
    uVar7 = uVar6 & 0xffff;
    if (uVar7 == 0) {
      if ((uintptr_t)((code *)param_3[3])!=(uintptr_t)(f33_reset_vector)) {
        (*(int (*)())param_3[3])();
      }
    }
    else {
      if (uVar7 == 0x11) {
        if ((uintptr_t)((code *)param_3[3])!=(uintptr_t)(f33_reset_vector)) {
          (*(int (*)())param_3[3])();
        }
        if ((uintptr_t)((code *)param_3[6])!=(uintptr_t)(f33_reset_vector)) {
          (*(int (*)())param_3[6])();
        }
        pcVar14 = (code *)param_3[0xb];
      }
      else if (uVar7 == 0x22) {
        if ((uintptr_t)((code *)param_3[3])!=(uintptr_t)(f33_reset_vector)) {
          (*(int (*)())param_3[3])();
        }
        if ((uintptr_t)((code *)param_3[6])!=(uintptr_t)(f33_reset_vector)) {
          (*(int (*)())param_3[6])();
        }
        if ((uintptr_t)((code *)param_3[8])!=(uintptr_t)(f33_reset_vector)) {
          (*(int (*)())param_3[8])();
        }
        pcVar14 = (code *)param_3[0xc];
      }
      else if (uVar7 == 0x1100) {
        pcVar14 = (code *)param_3[9];
      }
      else {
        if (uVar7 != 0x2200) {
          if ((uintptr_t)((code *)param_3[9])!=(uintptr_t)(f33_reset_vector)) {
            (*(int (*)())param_3[9])();
          }
          uVar6 = 0x1100;
          goto LAB_000d1cc6;
        }
        if ((uintptr_t)((code *)param_3[4])!=(uintptr_t)(f33_reset_vector)) {
          (*(int (*)())param_3[4])();
        }
        pcVar14 = (code *)param_3[10];
      }
      if ((uintptr_t)(pcVar14)!=(uintptr_t)(f33_reset_vector)) {
        (*(int (*)())pcVar14)();
      }
    }
    goto LAB_000d1cc6;
  }
  if (sVar5 != 0x2200) {
    if ((uintptr_t)((code *)param_3[0xc])!=(uintptr_t)(f33_reset_vector)) {
      (*(int (*)())param_3[0xc])();
    }
    uVar6 = 0x22;
    goto LAB_000d1cc6;
  }
  iVar8 = (*(int (*)())*param_3)();
  if (iVar8 == 0x11) {
LAB_000d18e0:
    uVar13 = 0;
    uVar12 = 0;
LAB_000d18e4:
    uVar6 = 0x2200;
  }
  else {
    if (iVar8 != 0x22) {
      if ((iVar8 == 0x33) || (iVar8 == 0x44)) goto LAB_000d18e0;
      goto LAB_000d18e4;
    }
    uVar11 = 0;
    uVar10 = 0;
    if ((uVar4 < uVar12) || (uVar12 = uVar12 + 1, uVar4 < uVar12)) {
      uVar13 = 0;
      uVar12 = 0;
      uVar6 = 0;
    }
    else {
      if (uVar13 <= uVar3) {
        uVar13 = uVar13 + 1;
      }
      uVar1 = uVar13;
      if (uVar13 <= uVar9) {
        uVar1 = uVar9;
      }
      uVar9 = uVar1;
      uVar6 = 0x22;
      if (uVar13 <= uVar3) {
        uVar6 = 0x110011;
      }
    }
  }
  uVar7 = uVar6 & 0xffff;
  if (uVar7 == 0) {
    if ((uintptr_t)((code *)param_3[5])!=(uintptr_t)(f33_reset_vector)) {
      (*(int (*)())param_3[5])();
    }
  }
  else {
    if (uVar7 == 0x11) {
      if ((uintptr_t)((code *)param_3[5])!=(uintptr_t)(f33_reset_vector)) {
        (*(int (*)())param_3[5])();
      }
      if ((uintptr_t)((code *)param_3[6])!=(uintptr_t)(f33_reset_vector)) {
        (*(int (*)())param_3[6])();
      }
      pcVar14 = (code *)param_3[0xb];
    }
    else if (uVar7 == 0x22) {
      if ((uintptr_t)((code *)param_3[5])!=(uintptr_t)(f33_reset_vector)) {
        (*(int (*)())param_3[5])();
      }
      if ((uintptr_t)((code *)param_3[6])!=(uintptr_t)(f33_reset_vector)) {
        (*(int (*)())param_3[6])();
      }
      if ((uintptr_t)((code *)param_3[8])!=(uintptr_t)(f33_reset_vector)) {
        (*(int (*)())param_3[8])();
      }
      pcVar14 = (code *)param_3[0xc];
    }
    else {
      pcVar14 = (code *)param_3[10];
      if (uVar7 != 0x2200) {
        if ((uintptr_t)(pcVar14)!=(uintptr_t)(f33_reset_vector)) {
          (*(int (*)())pcVar14)();
        }
        uVar6 = 0x2200;
        goto LAB_000d1cc6;
      }
    }
    if ((uintptr_t)(pcVar14)!=(uintptr_t)(f33_reset_vector)) {
      (*(int (*)())pcVar14)();
    }
  }
LAB_000d1cc6:
  *param_1 = uVar6;
  *(ushort *)(param_1 + 1) = uVar11;
  (*((ushort *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 6)))) = uVar10;
  *(ushort *)(param_1 + 2) = uVar13;
  (*((ushort *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 10)))) = uVar12;
  *(ushort *)(param_1 + 3) = uVar9;
  return 0x11;
}



void FUN_000d1cdc(short param_1,short param_2,short param_3,short *param_4)

{
  int iVar1;
  int iVar2;
  int iVar3;
  
  iVar1 = (int)param_1;
  iVar2 = (int)param_2;
  iVar3 = (int)param_3;
  if (iVar2 - iVar1 < 0 != (iVar2 < 0 != iVar1 < 0 && iVar1 < 0 == iVar2 - iVar1 < 0)) {
    iVar1 = iVar2;
  }
  if (iVar3 - iVar1 < 0 != (iVar3 < 0 != iVar1 < 0 && iVar1 < 0 == iVar3 - iVar1 < 0) ||
      iVar3 == iVar1) {
    param_3 = (short)iVar1;
  }
  *param_4 = param_3;
  return;
}



void FUN_000d1cf6(int param_1,int param_2,int param_3,int *param_4)

{
  if (param_2 - param_1 < 0 != (param_2 < 0 != param_1 < 0 && param_1 < 0 == param_2 - param_1 < 0))
  {
    param_1 = param_2;
  }
  if (param_3 - param_1 < 0 == (param_3 < 0 != param_1 < 0 && param_1 < 0 == param_3 - param_1 < 0)
      && param_3 != param_1) {
    param_1 = param_3;
  }
  *param_4 = param_1;
  return;
}



/* Sign-extend low16 inputs and store their signed maximum throughR8. R10 is not a defined return;
   the only live caller is owner1 BB176. Explicit output pointer prevents a lost retained-request
   update in decompilation. Native owner1 uses actual R8 output pointer to update retained request;
   only the exercised signed-max branch values are verified. */

void f33_store_signed_halfword_max(short value,short bound,short *output)

{
  int iVar1;
  int iVar2;
  
  iVar1 = (int)value;
  iVar2 = (int)bound;
  if (iVar2 - iVar1 < 0 == (iVar2 < 0 != iVar1 < 0 && iVar1 < 0 == iVar2 - iVar1 < 0) &&
      iVar2 != iVar1) {
    value = bound;
  }
  *output = value;
  return;
}



void FUN_000d1d1c(ushort *param_1,undefined2 *param_2)

{
  uint uVar1;
  uint uVar2;
  uint uVar3;
  
  uVar3 = (uint)*param_1;
  uVar1 = (uint)param_1[1] - (uint)param_1[3];
  uVar2 = (uint)param_1[2] + (uint)param_1[1];
  if (((int)(uVar3 - uVar2) < 0 || uVar3 == uVar2) &&
     (uVar2 = uVar3,
     (int)(uVar1 - uVar3) < 0 == ((int)uVar1 < 0 && -1 < (int)(uVar1 - uVar3)) && uVar1 != uVar3)) {
    uVar2 = uVar1;
  }
  *param_2 = (short)uVar2;
  return;
}



/* Sign-extend low16 inputs and store their signed minimum throughR8. R10 is not a defined return;
   the only live caller is owner1 BB176. Explicit output pointer prevents a lost retained-request
   update in decompilation. */

void f33_store_signed_halfword_min(short value,short bound,short *output)

{
  int iVar1;
  int iVar2;
  
  iVar2 = (int)value;
  iVar1 = bound - iVar2;
  if (iVar1 < 0 != (bound < 0 != iVar2 < 0 && iVar2 < 0 == iVar1 < 0)) {
    value = bound;
  }
  *output = value;
  return;
}



void FUN_000d1d4e(int param_1,int param_2,int *param_3)

{
  if (param_2 - param_1 < 0 != (param_2 < 0 != param_1 < 0 && param_1 < 0 == param_2 - param_1 < 0))
  {
    param_1 = param_2;
  }
  *param_3 = param_1;
  return;
}



void FUN_000d1d5c(ushort param_1,ushort param_2,ushort *param_3)

{
  if (param_2 < param_1) {
    param_1 = param_2;
  }
  *param_3 = param_1;
  return;
}



void FUN_000d1d6e(uint param_1,uint param_2,uint *param_3)

{
  if (param_2 < param_1) {
    param_1 = param_2;
  }
  *param_3 = param_1;
  return;
}



void FUN_000d1de4(short *param_1,short param_2,short *param_3)

{
  short *psVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  short sVar5;
  
  iVar4 = (int)param_2;
  iVar2 = (int)*param_1;
  if ((iVar2 == 0x7fff) ||
     (iVar2 - iVar4 < 0 == (iVar2 < 0 != iVar4 < 0 && iVar4 < 0 == iVar2 - iVar4 < 0))) {
    sVar5 = param_1[1];
  }
  else {
    iVar2 = 0;
    while( true ) {
      psVar1 = param_1 + iVar2 * 2;
      iVar3 = (int)*psVar1;
      if (iVar3 == 0x7fff) break;
      if (iVar3 - iVar4 < 0 == (iVar3 < 0 != iVar4 < 0 && iVar4 < 0 == iVar3 - iVar4 < 0) &&
          iVar3 != iVar4) {
        iVar3 = iVar3 - psVar1[-2];
        iVar2 = (iVar4 - psVar1[-2]) * ((int)psVar1[1] - (int)psVar1[-1]);
        if (iVar3 != 0) {
          if (iVar2 == -0x80000000 && iVar3 == -1) {
            iVar2 = 0;
          }
          else {
            iVar2 = iVar2 / iVar3;
          }
        }
        sVar5 = psVar1[-1] + (short)iVar2;
        goto LAB_000d1e32;
      }
      iVar2 = iVar2 + 1;
    }
    sVar5 = psVar1[-1];
  }
LAB_000d1e32:
  *param_3 = sVar5;
  return;
}



void FUN_000d1e8c(ushort *param_1,uint param_2,ushort *param_3)

{
  ushort *puVar1;
  ushort uVar2;
  int iVar3;
  int iVar4;
  uint uVar5;
  
  param_2 = param_2 & 0xffff;
  if ((*param_1 == 0xffff) || (param_2 <= *param_1)) {
    uVar2 = param_1[1];
  }
  else {
    iVar3 = 0;
    while( true ) {
      puVar1 = param_1 + iVar3 * 2;
      uVar5 = (uint)*puVar1;
      if (uVar5 == 0xffff) break;
      if (param_2 < uVar5) {
        iVar3 = uVar5 - puVar1[-2];
        iVar4 = (param_2 - puVar1[-2]) * ((int)(short)puVar1[1] - (int)(short)puVar1[-1]);
        if (iVar3 != 0) {
          if (iVar4 == -0x80000000 && iVar3 == -1) {
            iVar4 = 0;
          }
          else {
            iVar4 = iVar4 / iVar3;
          }
        }
        uVar2 = puVar1[-1] + (short)iVar4;
        goto LAB_000d1eda;
      }
      iVar3 = iVar3 + 1;
    }
    uVar2 = puVar1[-1];
  }
LAB_000d1eda:
  *param_3 = uVar2;
  return;
}



void FUN_000d1ee0(ushort *param_1,uint param_2,ushort *param_3)

{
  ushort *puVar1;
  ushort uVar2;
  int iVar3;
  int iVar4;
  uint uVar5;
  
  param_2 = param_2 & 0xffff;
  if ((*param_1 == 0xffff) || (param_2 <= *param_1)) {
    uVar2 = param_1[1];
  }
  else {
    iVar3 = 0;
    while( true ) {
      puVar1 = param_1 + iVar3 * 2;
      uVar5 = (uint)*puVar1;
      if (uVar5 == 0xffff) break;
      if (param_2 < uVar5) {
        iVar3 = uVar5 - puVar1[-2];
        iVar4 = (param_2 - puVar1[-2]) * ((uint)puVar1[1] - (uint)puVar1[-1]);
        if (iVar3 != 0) {
          if (iVar4 == -0x80000000 && iVar3 == -1) {
            iVar4 = 0;
          }
          else {
            iVar4 = iVar4 / iVar3;
          }
        }
        uVar2 = puVar1[-1] + (short)iVar4;
        goto LAB_000d1f2e;
      }
      iVar3 = iVar3 + 1;
    }
    uVar2 = puVar1[-1];
  }
LAB_000d1f2e:
  *param_3 = uVar2;
  return;
}



void FUN_000d22c0(ushort *param_1,ushort param_2,ushort *param_3)

{
  ushort uVar1;
  int iVar2;
  
  if ((*param_1 == 0xffff) || (param_2 <= *param_1)) {
    uVar1 = param_1[1];
  }
  else {
    iVar2 = 1;
    while( true ) {
      uVar1 = param_1[iVar2 * 2];
      if ((param_2 < uVar1) || (uVar1 == 0xffff)) break;
      iVar2 = iVar2 + 1;
    }
    uVar1 = (param_1 + iVar2 * 2)[-1];
  }
  *param_3 = uVar1;
  return;
}



void FUN_000d2330(int param_1,int param_2,uint *param_3)

{
  int iVar1;
  uint uVar2;
  
  if ((param_1 == 0) || (param_2 == 0)) {
    uVar2 = 0;
    goto LAB_000d2382;
  }
  if (param_1 < 0) {
    if (-1 < param_2) goto LAB_000d2366;
  }
  else if (param_2 < 0) {
LAB_000d2366:
    iVar1 = (int)((ulonglong)((longlong)param_2 * (longlong)param_1) >> 0x20) + 1;
    if ((iVar1 < 0 != (-1 < (longlong)param_2 * (longlong)param_1 && iVar1 < 0)) ||
       (uVar2 = param_1 * param_2, uVar2 < 0x80000001)) {
      uVar2 = 0x80000001;
    }
    goto LAB_000d2382;
  }
  if ((-1 < (longlong)param_2 * (longlong)param_1 &&
       (int)((ulonglong)((longlong)param_2 * (longlong)param_1) >> 0x20) != 0) ||
     (uVar2 = param_1 * param_2, 0x7fffffff < (uint)(param_1 * param_2))) {
    uVar2 = 0x7fffffff;
  }
LAB_000d2382:
  *param_3 = uVar2;
  return;
}



void FUN_000d2388(short param_1,short param_2,undefined2 *param_3)

{
  undefined2 uVar1;
  int iVar2;
  
  iVar2 = (int)param_1 - (int)param_2;
  if (iVar2 + 0x7fff < 0 == (-1 < iVar2 && iVar2 + 0x7fff < 0) && iVar2 != -0x7fff) {
    if (iVar2 + -0x7fff < 0 == (iVar2 < 0 && -1 < iVar2 + -0x7fff) && iVar2 != 0x7fff) {
      uVar1 = 0x7fff;
    }
    else {
      if (iVar2 + 0x8000 < 0 != (-1 < iVar2 && iVar2 + 0x8000 < 0) || iVar2 == -0x8000) {
        iVar2 = -0x8000;
      }
      uVar1 = (undefined2)iVar2;
    }
  }
  else {
    uVar1 = 0x8001;
  }
  *param_3 = uVar1;
  return;
}



undefined4 FUN_000d268c(byte param_1,byte *param_2,byte *param_3,byte *param_4)

{
  undefined4 uVar1;
  
  if ((((uintptr_t)(param_2)==(uintptr_t)((byte *)0x0)) || ((uintptr_t)(param_3)==(uintptr_t)((byte *)0x0))) || ((uintptr_t)(param_4)==(uintptr_t)((byte *)0x0))) {
    uVar1 = 0xffffffff;
  }
  else {
    uVar1 = FUN_000d1da0(0xffc0);
    *param_2 = param_1;
    *param_3 = param_1 ^ 0x55;
    *param_4 = param_1 ^ 0xaa;
    FUN_000d1dc6(uVar1);
    uVar1 = 0;
  }
  return uVar1;
}



undefined4 FUN_000d26d0(ushort param_1,ushort *param_2,ushort *param_3,ushort *param_4)

{
  undefined4 uVar1;
  
  if ((((uintptr_t)(param_2)==(uintptr_t)((ushort *)0x0)) || ((uintptr_t)(param_3)==(uintptr_t)((ushort *)0x0))) || ((uintptr_t)(param_4)==(uintptr_t)((ushort *)0x0))) {
    uVar1 = 0xffffffff;
  }
  else {
    uVar1 = FUN_000d1da0(0xffc0);
    *param_2 = param_1;
    *param_3 = param_1 ^ 0x5555;
    *param_4 = param_1 ^ 0xaaaa;
    FUN_000d1dc6(uVar1);
    uVar1 = 0;
  }
  return uVar1;
}



undefined4 FUN_000d2714(uint param_1,uint *param_2,uint *param_3,uint *param_4)

{
  undefined4 uVar1;
  
  if ((((uintptr_t)(param_2)==(uintptr_t)((uint *)0x0)) || ((uintptr_t)(param_3)==(uintptr_t)((uint *)0x0))) || ((uintptr_t)(param_4)==(uintptr_t)((uint *)0x0))) {
    uVar1 = 0xffffffff;
  }
  else {
    uVar1 = FUN_000d1da0(0xffc0);
    *param_2 = param_1;
    *param_3 = param_1 ^ 0x55555555;
    *param_4 = param_1 ^ 0xaaaaaaaa;
    FUN_000d1dc6(uVar1);
    uVar1 = 0;
  }
  return uVar1;
}



undefined4 FUN_000d2760(byte param_1,byte *param_2,byte *param_3,byte *param_4)

{
  undefined4 uVar1;
  
  if ((((uintptr_t)(param_2)==(uintptr_t)((byte *)0x0)) || ((uintptr_t)(param_3)==(uintptr_t)((byte *)0x0))) || ((uintptr_t)(param_4)==(uintptr_t)((byte *)0x0))) {
    uVar1 = 0xffffffff;
  }
  else {
    uVar1 = FUN_000d1da0(0xffc0);
    *param_2 = param_1;
    *param_3 = param_1 ^ 0x55;
    *param_4 = param_1 ^ 0xaa;
    FUN_000d1dc6(uVar1);
    uVar1 = 0;
  }
  return uVar1;
}



undefined4 FUN_000d27a4(ushort param_1,ushort *param_2,ushort *param_3,ushort *param_4)

{
  undefined4 uVar1;
  
  if ((((uintptr_t)(param_2)==(uintptr_t)((ushort *)0x0)) || ((uintptr_t)(param_3)==(uintptr_t)((ushort *)0x0))) || ((uintptr_t)(param_4)==(uintptr_t)((ushort *)0x0))) {
    uVar1 = 0xffffffff;
  }
  else {
    uVar1 = FUN_000d1da0(0xffc0);
    *param_2 = param_1;
    *param_3 = param_1 ^ 0x5555;
    *param_4 = param_1 ^ 0xaaaa;
    FUN_000d1dc6(uVar1);
    uVar1 = 0;
  }
  return uVar1;
}



undefined4 FUN_000d27e8(uint param_1,uint *param_2,uint *param_3,uint *param_4)

{
  undefined4 uVar1;
  
  if ((((uintptr_t)(param_2)==(uintptr_t)((uint *)0x0)) || ((uintptr_t)(param_3)==(uintptr_t)((uint *)0x0))) || ((uintptr_t)(param_4)==(uintptr_t)((uint *)0x0))) {
    uVar1 = 0xffffffff;
  }
  else {
    uVar1 = FUN_000d1da0(0xffc0);
    *param_2 = param_1;
    *param_3 = param_1 ^ 0x55555555;
    *param_4 = param_1 ^ 0xaaaaaaaa;
    FUN_000d1dc6(uVar1);
    uVar1 = 0;
  }
  return uVar1;
}



undefined8 FUN_000d2834(uint param_1,uint param_2,uint param_3,uint param_4)

{
  uint uVar1;
  uint uVar2;
  uint uVar3;
  uint uVar4;
  uint uVar5;
  uint uVar6;
  
  uVar6 = param_1 & 0xffff;
  uVar5 = param_3 & 0xffff;
  param_3 = param_3 >> 0x10;
  param_1 = param_1 >> 0x10;
  uVar3 = uVar6 * (param_4 & 0xffff);
  uVar1 = (uVar6 * uVar5 >> 0x10) + (uVar6 * param_3 & 0xffff) + (param_1 * uVar5 & 0xffff);
  uVar4 = (param_2 & 0xffff) * uVar5;
  uVar2 = (uVar6 * param_3 >> 0x10) + (uVar3 & 0xffff) + (param_1 * uVar5 >> 0x10) +
          (param_1 * param_3 & 0xffff) + (uVar4 & 0xffff) + (uVar1 >> 0x10);
  return CONCAT44(((uVar3 >> 0x10) + uVar6 * (param_4 >> 0x10) + (param_1 * param_3 >> 0x10) +
                   param_1 * (param_4 & 0xffff) + (uVar4 >> 0x10) + (param_2 & 0xffff) * param_3 +
                   (param_2 >> 0x10) * uVar5 + (uVar2 >> 0x10)) * 0x10000 | uVar2 & 0xffff,
                  uVar1 * 0x10000 | uVar6 * uVar5 & 0xffff);
}



ulonglong FUN_000d28ea(uint param_1,int param_2,uint param_3,int param_4)

{
  bool bVar1;
  uint uVar2;
  uint uVar3;
  ulonglong uVar4;
  
  if (param_2 != 0 || param_4 != 0) {
    bVar1 = param_2 < 0;
    uVar2 = param_1;
    if (bVar1) {
      uVar2 = -param_1;
      param_2 = -(uint)(param_1 != 0) - param_2;
    }
    uVar3 = param_3;
    if (param_4 < 0) {
      uVar3 = -param_3;
      param_4 = -(uint)(param_3 != 0) - param_4;
      bVar1 = !bVar1;
    }
    uVar4 = FUN_000d2d86(uVar2,param_2,uVar3,param_4);
    if (bVar1) {
      uVar4 = CONCAT44(-(uint)((int)uVar4 != 0) - (int)(uVar4 >> 0x20),-(int)uVar4);
    }
    return uVar4;
  }
  if (param_3 != 0) {
    param_1 = param_1 / param_3;
  }
  return (ulonglong)param_1;
}



uint FUN_000d2942(uint param_1,uint param_2,uint param_3,uint param_4)

{
  bool bVar1;
  uint uVar2;
  uint uVar3;
  uint uVar4;
  uint uVar5;
  int iVar6;
  uint uVar7;
  uint uVar8;
  uint uVar9;
  uint uVar10;
  uint uVar11;
  uint uVar12;
  uint uVar13;
  uint uVar14;
  uint uVar15;
  uint uVar16;
  int iVar17;
  
  if (param_3 != 0 || param_4 != 0) {
    uVar8 = 0;
    uVar13 = param_4;
    do {
      if ((int)uVar13 < 0) {
        iVar6 = uVar8 + 1;
        goto code_r0x000d2952;
      }
      uVar13 = uVar13 << 1;
      uVar8 = uVar8 + 1;
    } while (uVar8 < 0x20);
    iVar6 = 0;
code_r0x000d2952:
    if (iVar6 == 0) {
      uVar8 = 0;
      uVar13 = param_3;
      do {
        if ((int)uVar13 < 0) {
          iVar6 = uVar8 + 1;
          goto code_r0x000d2958;
        }
        uVar13 = uVar13 << 1;
        uVar8 = uVar8 + 1;
      } while (uVar8 < 0x20);
      iVar6 = 0;
code_r0x000d2958:
      iVar6 = iVar6 + 0x20;
    }
    uVar13 = iVar6 - 1;
    if ((param_3 - 1 & param_3) == 0 && (param_4 - (param_3 == 0) & param_4) == 0) {
      uVar13 = FUN_000d2da0(param_1,param_2,0x3f - uVar13);
      return uVar13;
    }
    if (param_2 < param_4 + (param_1 < param_3)) {
      param_1 = 0;
    }
    else if (uVar13 == 0) {
      param_1 = 1;
    }
    else {
      if (iVar6 + -0x21 < 0 == ((int)uVar13 < 0 && -1 < iVar6 + -0x21)) {
        if (param_2 == 0) {
          if (param_3 != 0) {
            param_1 = param_1 / param_3;
          }
          return param_1;
        }
        if (iVar6 + -0x31 < 0 == ((int)uVar13 < 0 && -1 < iVar6 + -0x31)) {
          param_3 = param_3 & 0xffff;
          uVar10 = param_2 >> 0x10;
          uVar8 = param_3 << (0x20 - (-uVar13 + 0x40) & 0x1f);
          if (uVar8 == 0) {
            uVar2 = 1;
          }
          else {
            uVar2 = (int)((ulonglong)
                          (uint)-(int)((ulonglong)uVar8 * (ulonglong)(0x7fffffff - uVar8) >> 0x20) *
                          (ulonglong)(0x7fffffff - uVar8) >> 0x20) << 1;
            uVar2 = (int)((ulonglong)(uint)-(int)((ulonglong)uVar8 * (ulonglong)uVar2 >> 0x20) *
                          (ulonglong)uVar2 >> 0x20) << 1;
            uVar2 = (int)((ulonglong)(uint)-(int)((ulonglong)uVar8 * (ulonglong)uVar2 >> 0x20) *
                          (ulonglong)uVar2 >> 0x20) << 1;
            uVar2 = (int)((ulonglong)(uint)-(int)((ulonglong)uVar8 * (ulonglong)uVar2 >> 0x20) *
                          (ulonglong)uVar2 >> 0x20) * 4 - 3;
            uVar2 = uVar2 - (uVar8 + (int)((ulonglong)uVar8 * (ulonglong)uVar2 >> 0x20));
            uVar2 = uVar2 - (uVar8 + (int)((ulonglong)uVar8 * (ulonglong)uVar2 >> 0x20));
            uVar2 = uVar2 - (uVar8 + (int)((ulonglong)uVar8 * (ulonglong)uVar2 >> 0x20));
          }
          iVar6 = (int)((ulonglong)uVar10 * (ulonglong)uVar2 >> 0x20);
          uVar13 = -uVar13 + 0x3f;
          uVar8 = param_2 & 0xffff |
                  (uVar10 - ((uVar10 - iVar6 >> 1) + iVar6 >> (uVar13 & 0x1f) & 0xffff) * param_3) *
                  0x10000;
          iVar6 = (int)((ulonglong)uVar8 * (ulonglong)uVar2 >> 0x20);
          uVar10 = param_1 >> 0x10 |
                   (uVar8 - ((uVar8 - iVar6 >> 1) + iVar6 >> (uVar13 & 0x1f) & 0xffff) * param_3) *
                   0x10000;
          iVar6 = (int)((ulonglong)uVar10 * (ulonglong)uVar2 >> 0x20);
          uVar8 = (uVar10 - iVar6 >> 1) + iVar6 >> (uVar13 & 0x1f);
          uVar10 = param_1 & 0xffff | (uVar10 - (uVar8 & 0xffff) * param_3) * 0x10000;
          iVar6 = (int)((ulonglong)uVar10 * (ulonglong)uVar2 >> 0x20);
          return (uVar10 - iVar6 >> 1) + iVar6 >> (uVar13 & 0x1f) & 0xffff | uVar8 << 0x10;
        }
      }
      iVar17 = (int)uVar13 >> 4;
      uVar8 = 4 - iVar17;
      if ((uVar13 != 0) && (uVar13 != 0)) {
        if (uVar13 < 0x20) {
          param_4 = param_3 >> (0x20 - uVar13 & 0x1f) | param_4 << (uVar13 & 0x1f);
          param_3 = param_3 << (uVar13 & 0x1f);
        }
        else {
          param_4 = param_3 << (iVar6 - 0x21U & 0x1f);
          param_3 = 0;
        }
      }
      uVar13 = uVar13 & 0xf;
      uVar2 = param_2 >> 0x10;
      uVar10 = (uint)(uVar2 == 0);
      if (uVar2 == 0) {
        if (uVar13 != 0) {
          if (uVar13 < 0x20) {
            param_2 = param_1 >> (0x20 - uVar13 & 0x1f) | param_2 << uVar13;
            param_1 = param_1 << uVar13;
          }
          else {
            param_2 = param_1 << (uVar13 - 0x20 & 0x1f);
            param_1 = 0;
          }
        }
        iVar17 = iVar17 + -1;
        uVar10 = param_2 >> 0x10;
        uVar2 = param_2 & 0xffff;
        uVar7 = 0;
        param_2 = param_1 >> 0x10;
        uVar13 = param_1;
      }
      else {
        if (uVar13 != 0) {
          uVar10 = uVar2 >> (0x10 - uVar13 & 0x1f) & 0xffff;
          if (uVar13 != 0) {
            if (uVar13 < 0x20) {
              param_2 = param_1 >> (0x20 - uVar13 & 0x1f) | param_2 << uVar13;
              param_1 = param_1 << uVar13;
            }
            else {
              param_2 = param_1 << (uVar13 - 0x20 & 0x1f);
              param_1 = 0;
            }
          }
          uVar2 = param_2 >> 0x10;
        }
        uVar13 = param_1 >> 0x10;
        uVar7 = param_1 & 0xffff;
      }
      uVar13 = uVar13 & 0xffff;
      uVar3 = param_4 >> 0x10;
      uVar4 = (uint)((uVar3 - 1 & uVar3) != 0);
      param_4 = param_4 & 0xffff;
      param_1 = 0;
      uVar11 = uVar3 << (0x20 - (uVar4 + 0xf) & 0x1f);
      if (uVar11 == 0) {
        uVar16 = 1;
      }
      else {
        uVar16 = (int)((ulonglong)
                       (uint)-(int)((ulonglong)uVar11 * (ulonglong)(0x7fffffff - uVar11) >> 0x20) *
                       (ulonglong)(0x7fffffff - uVar11) >> 0x20) << 1;
        uVar16 = (int)((ulonglong)(uint)-(int)((ulonglong)uVar11 * (ulonglong)uVar16 >> 0x20) *
                       (ulonglong)uVar16 >> 0x20) << 1;
        uVar16 = (int)((ulonglong)(uint)-(int)((ulonglong)uVar11 * (ulonglong)uVar16 >> 0x20) *
                       (ulonglong)uVar16 >> 0x20) << 1;
        uVar16 = (int)((ulonglong)(uint)-(int)((ulonglong)uVar11 * (ulonglong)uVar16 >> 0x20) *
                       (ulonglong)uVar16 >> 0x20) * 4 - 3;
        uVar16 = uVar16 - (uVar11 + (int)((ulonglong)uVar11 * (ulonglong)uVar16 >> 0x20));
        uVar16 = uVar16 - (uVar11 + (int)((ulonglong)uVar11 * (ulonglong)uVar16 >> 0x20));
        uVar16 = uVar16 - (uVar11 + (int)((ulonglong)uVar11 * (ulonglong)uVar16 >> 0x20));
      }
      uVar15 = uVar8 & 5;
      uVar8 = uVar8 & 4;
      uVar11 = param_2 & 0xffff;
      do {
        if (uVar10 != uVar3) {
          uVar14 = uVar2 | uVar10 << 0x10;
          iVar6 = (int)((ulonglong)uVar14 * (ulonglong)uVar16 >> 0x20);
          uVar12 = (uVar14 - iVar6 >> 1) + iVar6 >> uVar4 + 0xe;
          uVar14 = uVar14 - uVar12 * uVar3;
          goto LAB_000d2c7a;
        }
        uVar12 = 0x10000;
        uVar14 = uVar2;
        do {
          uVar12 = uVar12 - 1;
          uVar14 = uVar14 + uVar3;
          if (0xffff < uVar14) {
            uVar9 = param_4 * uVar12;
            break;
          }
LAB_000d2c7a:
          uVar9 = param_4 * uVar12;
          uVar5 = uVar11 | uVar14 << 0x10;
        } while (uVar5 <= uVar9 && uVar9 - uVar5 != 0);
        uVar14 = 0;
        if (uVar8 != 0) {
          uVar14 = uVar7 - (param_3 & 0xffff) * uVar12;
          uVar7 = uVar14 & 0xffff;
          uVar14 = -(uVar14 >> 0x10) & 0xffff;
        }
        uVar5 = uVar13;
        if (uVar15 != 0) {
          uVar14 = (uVar13 - (param_3 >> 0x10) * uVar12) - uVar14;
          uVar5 = uVar14 & 0xffff;
          uVar14 = -(uVar14 >> 0x10) & 0xffff;
        }
        uVar14 = (uVar11 - uVar9) - uVar14;
        uVar9 = uVar14 & 0xffff;
        uVar13 = (uVar2 - uVar3 * uVar12) - (-(uVar14 >> 0x10) & 0xffff);
        uVar11 = uVar13 & 0xffff;
        uVar2 = uVar10 - (-(uVar13 >> 0x10) & 0xffff);
        uVar13 = uVar7;
        uVar10 = uVar11;
        if ((uVar2 >> 0x10 != 0) && (uVar12 = uVar12 - 1, iVar17 != 0)) {
          if (uVar8 != 0) {
            uVar2 = uVar2 + (param_3 & 0xffff) + uVar7;
            uVar7 = uVar2 & 0xffff;
            uVar2 = uVar2 >> 0x10;
          }
          if (uVar15 != 0) {
            uVar2 = uVar2 + (param_3 >> 0x10) + uVar5;
            uVar5 = uVar2 & 0xffff;
            uVar2 = uVar2 >> 0x10;
          }
          uVar2 = uVar2 + param_4 + uVar9;
          uVar9 = uVar2 & 0xffff;
          uVar10 = (uVar2 >> 0x10) + uVar3 + uVar11 & 0xffff;
          uVar13 = uVar7;
        }
        uVar7 = 0;
        uVar2 = iVar17 * 0x10;
        if (uVar2 != 0) {
          if (uVar2 < 0x20) {
            uVar12 = uVar12 << (uVar2 & 0x1f);
          }
          else {
            uVar12 = 0;
          }
        }
        param_1 = param_1 | uVar12;
        bVar1 = iVar17 != 0;
        uVar11 = uVar5;
        uVar2 = uVar9;
        iVar17 = iVar17 + -1;
      } while (bVar1);
    }
  }
  return param_1;
}



undefined8 FUN_000d2da0(uint param_1,uint param_2,uint param_3)

{
  uint uVar1;
  uint uVar2;
  uint uVar3;
  
  uVar3 = 0;
  uVar2 = 0;
  if (param_3 < 0x40) {
    uVar1 = param_3 - 0x20;
    uVar3 = param_2 >> (uVar1 & 0x1f);
    if ((int)uVar1 < 0) {
      uVar2 = param_2 >> (param_3 & 0x1f);
      uVar3 = (param_2 << (~uVar1 & 0x1f)) << 1 | param_1 >> (param_3 & 0x1f);
    }
  }
  return CONCAT44(uVar2,uVar3);
}


