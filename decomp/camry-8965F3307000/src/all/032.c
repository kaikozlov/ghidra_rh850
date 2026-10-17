#include "common.h"


/* Clear counters/latch, map products, retained accumulatorC45C/filterC46C and independently
   published C472. */

void f33_initialize_directional_rate_compensation(void)

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



/* ADF2>0 and C18A<-80 qualify direction1; ADF2<0 and C18A>80 direction2. Increment while count<=3;
   strict>3 latches. Counts may reset while latch persists until the rate sign releases it. */

void f33_qualify_opposed_rate_direction(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  int iVar6;
  int iVar7;
  
  iVar4 = (int)DAT_febeadf2;
  iVar3 = (int)DAT_000affdc;
  iVar2 = (int)DAT_000affde;
  iVar1 = (int)DAT_febec460;
  iVar7 = (int)DAT_febec462;
  iVar5 = (int)DAT_000affe0;
  iVar6 = (int)DAT_febec18a;
  if ((iVar4 - iVar3 < 0 == (iVar4 < 0 != iVar3 < 0 && iVar3 < 0 == iVar4 - iVar3 < 0) &&
       iVar4 != iVar3) &&
     (iVar6 + iVar2 < 0 != (iVar6 < 0 != -iVar2 < 0 && -iVar2 < 0 == iVar6 + iVar2 < 0))) {
    if (iVar1 - iVar5 < 0 != (iVar1 < 0 != iVar5 < 0 && iVar5 < 0 == iVar1 - iVar5 < 0) ||
        iVar1 == iVar5) {
      DAT_febec460 = DAT_febec460 + 1;
      iVar1 = (int)DAT_febec460;
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
      DAT_febec462 = DAT_febec462 + 1;
      iVar1 = (int)DAT_febec462;
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



/* Unsigned ADF6 lookup at AFFFE. All ordinary ordinates are zero in this exact image. */

void f33_update_directional_rate_speed_gain(void)

{
  uint32_t puVar1;
  int iVar2;
  
  puVar1 = 0xfebeb800u;
  iVar2 = f33_interpolate_unsigned_axis_sentinel_curve((ushort *)((undefined *)camry_host_ptr(0xafffeu)),DAT_febeadf6);
  (*((short *)camry_host_ptr((uint32_t)(puVar1 + 0xc6e)))) = (short)iVar2;
  return;
}



/* WARNING: Removing unreachable block (ram,0x000c8176) */
/* WARNING: Removing unreachable block (ram,0x000c8162) */
/* Gate signed mapped C18A with retained direction and speed gain, AE4A and optional CDF4/CDEC
   suppression, then C42C scaling. Suppression zeros input, not history. Update A=A+input-oldY;
   Y=s16(s32(A<<10)/5100). Exact AFFE6 ordinates are zero. */

void f33_filter_directional_rate_compensation(void)

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
  input = f33_abs_s16_wrapping(((int)(int16_t)DAT_febec18a));
  (*((short *)camry_host_ptr((uint32_t)(puVar2 + 0xc64)))) = input;
  iVar5 = f33_interpolate_signed_sentinel_curve((short *)((undefined *)camry_host_ptr(0xaffe6u)),input);
  uVar8 = (ushort)(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(0xc70)))));
  if (((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(0xc70))))) != 0) &&
     (uVar8 = (ushort)(((int)(*((short *)camry_host_ptr((uint32_t)(puVar2 + 0xc6e)))) * (int)(short)iVar5 + 0x200) / 0x400),
     sVar3 < 0)) {
    uVar8 = -uVar8;
  }
  sVar4 = (short)(((int)sVar4 * (int)(short)uVar8) / 0x400);
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(0xdf4))))) == '\x01') {
    sVar3 = f33_abs_s16_wrapping((*((short *)camry_host_ptr((uint32_t)(puVar2 + 0xdec)))));
    iVar6 = (int)sVar3;
    iVar1 = (int)DAT_000affe4;
    if (iVar6 - iVar1 < 0 == (iVar6 < 0 != iVar1 < 0 && iVar1 < 0 == iVar6 - iVar1 < 0) &&
        iVar6 != iVar1) {
      sVar4 = 0;
    }
  }
  sVar4 = f33_scale_rate_assist_term(sVar4);
  iVar1 = f33_directional_rate_filter_denominator;
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
      iVar7 = iVar7 / iVar1;
    }
  }
  (*((short *)camry_host_ptr((uint32_t)(puVar2 + 0xc6c)))) = (short)iVar7;
  return;
}



/* Bound retained C46C to768 into C472. D0C44 invokes on captured CCA0==1, separately from
   foreground filter updates. */

void f33_publish_directional_rate_compensation(void)

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



/* Paired constant publisher: DAT_febec474 = 0; and DAT_febec476 = 0;; shape-classified from the
   canonical corpus. Target cells not yet named. */

void FUN_000c81ee(void)

{
  DAT_febec474 = 0;
  DAT_febec476 = 0;
  return;
}



void FUN_000c81f8(void)

{
  short input;
  uint32_t puVar1;
  int iVar2;
  
  input = DAT_febeae4a;
  puVar1 = 0xfebeb800u;
  iVar2 = f33_interpolate_signed_sentinel_curve((short *)((undefined *)camry_host_ptr(0xb001au)),DAT_febeae4a);
  (*((short *)camry_host_ptr((uint32_t)(puVar1 + 0xc74)))) = (short)iVar2;
  iVar2 = f33_interpolate_signed_sentinel_curve((short *)((undefined *)camry_host_ptr(0xb003eu)),input);
  (*((short *)camry_host_ptr((uint32_t)(puVar1 + 0xc76)))) = (short)iVar2;
  return;
}



void FUN_000c8224(void)

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



void FUN_000c82a8(void)

{
  uint32_t puVar1;
  undefined2 uVar2;
  
  puVar1 = 0xfebeb800u;
  uVar2 = FUN_000d0896(((undefined *)camry_host_ptr(0xb00aeu)),DAT_febeadf6);
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0xc44)))) = uVar2;
  return;
}



/* WARNING: Removing unreachable block (ram,0x000c830e) */
/* WARNING: Removing unreachable block (ram,0x000c82fa) */

void FUN_000c82c2(ushort param_1,short param_2)

{
  int iVar1;
  short sVar2;
  uint32_t puVar3;
  int iVar4;
  short sVar5;
  short sVar6;
  int iVar7;
  
  sVar2 = DAT_febeae4a;
  puVar3 = 0xfebeb800u;
  iVar4 = f33_interpolate_unsigned_axis_sentinel_curve((ushort *)((undefined *)camry_host_ptr(0xb0086u)),param_1);
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
      iVar4 = iVar4 / DAT_000b0064;
    }
  }
  (*((short *)camry_host_ptr((uint32_t)(puVar3 + -0xc42)))) = (short)iVar4;
  return;
}



/* WARNING: Removing unreachable block (ram,0x000c84a6) */
/* WARNING: Removing unreachable block (ram,0x000c8456) */

undefined2 FUN_000c843a(char param_1)

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
  uVar4 = FUN_000c7e1c((int)(short)((int)(iVar3 * (uint)DAT_febeabc4) / 0x400));
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar2 + -0xc3e)))) = uVar4;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(0xc9d))))) = cVar5;
  return uVar4;
}



void FUN_000c84bc(void)

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



void FUN_000c84dc(undefined2 param_1,undefined1 param_2)

{
  FUN_000c8350(param_1, (uint)(byte)param_2);
  FUN_000c843a(param_2);
  FUN_000c84bc();
  return;
}



void FUN_000c84f8(void)

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
  FUN_000c82c2(sVar3,iVar5);
  FUN_000c84dc(sVar3,uVar1);
  return;
}



void FUN_000c854a(void)

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
  sVar7 = f33_abs_s16_wrapping(DAT_febec5ec);
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
  iVar5 = f33_abs_s32_wrapping(uVar11 - iVar5);
  if (iVar5 + -0x14 < 0 != (iVar5 < 0 && -1 < iVar5 + -0x14) || iVar5 == 0x14) {
    uVar11 = (uint)(*((ushort *)camry_host_ptr((uint32_t)(puVar6 + -0xc3a))));
    uVar12 = uVar11 * (*((ushort *)camry_host_ptr((uint32_t)(puVar6 + 0xc98)))) >> 10;
  }
  (*((uint *)camry_host_ptr((uint32_t)(puVar6 + 0xc84)))) = uVar12;
  (*((short *)camry_host_ptr((uint32_t)(puVar6 + -0xc3c)))) = (short)uVar11;
  return;
}



void FUN_000c8642(void)

{
  DAT_febec4ac = camry_host_addr(((undefined *)camry_host_ptr(0xb1248u)));
  DAT_febec4b4 = 0;
  DAT_febec4b6 = 0;
  DAT_febec4c0 = 0;
  DAT_febec4a4 = 0;
  DAT_febec4a8 = 0;
  DAT_febec4b8 = 0;
  DAT_febec4ba = 0;
  DAT_febec4bc = 0;
  DAT_febec4b0 = camry_host_addr(((undefined *)camry_host_ptr(0xb121cu)));
  return;
}



/* WARNING: Removing unreachable block (ram,0x000c871a) */
/* WARNING: Removing unreachable block (ram,0x000c8710) */
/* WARNING: Removing unreachable block (ram,0x000c8704) */
/* Map signed torque rateC266 and multiply by a narrowed factor from assistance slopeBF40 and
   adjacent speed maps. Publish bounded signed32 C4C0. Preserve low32 products and the real
   left-shift10 followed by signed division1024; these are not algebraic identities under wrap.
   Torque-rate magnitude mapping and sign restoration multiply a narrowed speed/slope-derived factor
   to produce signed32 C4C0. Preserve low32 arithmetic and shift10/divide1024 wrap behavior; not
   another base torque surface. */

void f33_update_torque_rate_assist_compensation(void)

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
  sVar3 = f33_abs_s16_wrapping(((int)(int16_t)DAT_febec266));
  iVar4 = f33_interpolate_signed_sentinel_curve(((short *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd3630u + (uint32_t)(uVar1 & 3) * 4u)))))),sVar3);
  sVar3 = (short)iVar4;
  if (sVar6 < 0) {
    sVar3 = -sVar3;
  }
  sVar6 = (*((short *)camry_host_ptr((uint32_t)(puVar2 + 0x740))));
  (*((short *)camry_host_ptr((uint32_t)(puVar2 + 0xcb4)))) = sVar3;
  (*((short *)camry_host_ptr((uint32_t)(puVar2 + 0xcbc)))) = sVar6;
  iVar4 = f33_interpolate_signed_sentinel_curve(points_00,sVar6);
  iVar5 = f33_interpolate_signed_sentinel_curve(points,sVar6);
  (*((short *)camry_host_ptr((uint32_t)(puVar2 + 0xcb8)))) = (short)iVar4;
  (*((short *)camry_host_ptr((uint32_t)(puVar2 + 0xcba)))) = (short)iVar5;
  sVar6 = (short)(((iVar5 - iVar4) * iVar7) / 0x400) + (short)iVar4;
  (*((short *)camry_host_ptr((uint32_t)(puVar2 + 0xcb6)))) = sVar6;
  iVar4 = ((int)sVar6 * (int)(*((short *)camry_host_ptr((uint32_t)(puVar2 + 0xcb4))))) / 0x400;
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



void FUN_000c873e(void)

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



void FUN_000c878a(void)

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
  sVar6 = f33_abs_s16_wrapping(DAT_febec5ec);
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
  iVar4 = f33_abs_s32_wrapping(uVar3 - iVar4);
  if (iVar4 + -0x14 < 0 != (iVar4 < 0 && -1 < iVar4 + -0x14) || iVar4 == 0x14) {
    uVar3 = (uint)(*((ushort *)camry_host_ptr((uint32_t)(puVar5 + 0xccc))));
    uVar10 = uVar3 * (*((ushort *)camry_host_ptr((uint32_t)(puVar5 + 0xcce)))) >> 10;
  }
  (*((uint *)camry_host_ptr((uint32_t)(puVar5 + 0xcc4)))) = uVar10;
  (*((short *)camry_host_ptr((uint32_t)(puVar5 + 0xcca)))) = (short)uVar3;
  return;
}



/* WARNING: Removing unreachable block (ram,0x000c88a2) */

uint FUN_000c8894(short param_1)

{
  DAT_febec4d2 = (short)((int)((int)param_1 * (uint)DAT_febec4ca) / 0x400);
  return DAT_febec4d2;
}



/* WARNING: This is an inlined function */
/* Same12-byte state and preserved R6 as C5106, feeding CE8DA. Exact94-byte body differs only in ROM
   pointer/global displacements; calibration values remain producer-local. Inline real p-code so the
   shared helper's typed argument remains connected in every caller. Prepare common gain state for
   C4DC; real94-byte leaf preserves R6 and uses the same typed12-byte layout. */

void f33_prepare_gain_parameters_c4dc(F33GainSlewState *state,uint mode)

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
    uVar2 = *(ushort *)(((undefined *)camry_host_ptr(0xd36f8u)) + iVar1 * 0x10);
    uVar6 = (*((ushort *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd36f4u + (uint32_t)(iVar1 * 4) * 4u)))))));
    uVar5 = **(ushort **)(((undefined *)camry_host_ptr(0xd36fcu)) + iVar1 * 0x10);
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



/* WARNING: Inlined function: f33_prepare_gain_parameters_c4dc */

void FUN_000c890e(void)

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
    local_10.up_target = *(ushort *)(((undefined *)camry_host_ptr(0xd36f8u)) + iVar1 * 0x10);
    local_10.down_step = (*((ushort *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd36f4u + (uint32_t)(iVar1 * 4) * 4u)))))));
    local_10.up_step = **(ushort **)(((undefined *)camry_host_ptr(0xd36fcu)) + iVar1 * 0x10);
    local_10.down_target = (*((ushort *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd36f0u + (uint32_t)(iVar1 * 4) * 4u)))))));
  }
  else {
    local_10.direction = '\x01';
    local_10.up_target = DAT_febec4d4;
    local_10.down_step = DAT_febec4d8;
    local_10.up_step = DAT_febec4da;
    local_10.down_target = DAT_febec4d6;
  }
  f33_step_retained_unsigned_gain(&local_10);
  (*((ushort *)camry_host_ptr((uint32_t)(puVar2 + 0xcd8)))) = local_10.down_step;
  (*((ushort *)camry_host_ptr((uint32_t)(puVar2 + 0xcda)))) = local_10.up_step;
  (*((ushort *)camry_host_ptr((uint32_t)(puVar2 + 0xcd6)))) = local_10.down_target;
  (*((ushort *)camry_host_ptr((uint32_t)(puVar2 + 0xcd4)))) = local_10.up_target;
  (*((ushort *)camry_host_ptr((uint32_t)(puVar2 + 0xcdc)))) = local_10.current;
  return;
}



/* WARNING: Removing unreachable block (ram,0x000c8964) */

uint FUN_000c8956(short param_1)

{
  DAT_febec4de = (short)((int)((uint)DAT_febec4dc * (int)param_1) / 0x400);
  return DAT_febec4de;
}



/* Constant-block fill: 28 literal assignments into one contiguous cell block; shape-verified.
   Literals are default/reset values; cell meanings are not recovered. */

void f33_fill_constant_block_c8970(void)

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



void FUN_000c8a78(void)

{
  uint32_t puVar1;
  int iVar2;
  
  puVar1 = 0xfebeb800u;
  iVar2 = f33_interpolate_unsigned_axis_sentinel_curve
                    (((ushort *)camry_host_ptr((uint32_t)(f33_calibration_bank_bases[DAT_febeac3c & 1] +
                     (DAT_febec156 & 3) * 0x24 + 0x1a4c))),DAT_febeadf6);
  (*((short *)camry_host_ptr((uint32_t)(puVar1 + 0xd08)))) = (short)iVar2;
  return;
}



void FUN_000c8ab2(void)

{
  uint32_t puVar1;
  short input;
  int iVar2;
  
  puVar1 = 0xfebeb800u;
  input = f33_abs_s16_wrapping(((int)(int16_t)DAT_febec29a));
  iVar2 = f33_interpolate_signed_sentinel_curve
                    (((short *)camry_host_ptr((uint32_t)(f33_calibration_bank_bases[(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0xbc4))))) & 1] +
                              (*(ushort *)(puVar1 + 0x956) & 3) * 0x14 + 0x1b6c))),input);
  (*((short *)camry_host_ptr((uint32_t)(puVar1 + -0xc32)))) = (short)iVar2;
  return;
}



/* WARNING: Removing unreachable block (ram,0x000c8b8e) */
/* WARNING: Removing unreachable block (ram,0x000c8b66) */

undefined4 FUN_000c8af2(void)

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
  uVar3 = f33_abs_s32_wrapping(DAT_febec504);
  input = (ushort)uVar3;
  if (0xffff < uVar3) {
    input = 0xffff;
  }
  iVar4 = f33_interpolate_unsigned_axis_sentinel_curve
                    (((ushort *)camry_host_ptr((uint32_t)(f33_calibration_bank_bases[(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0xbc4))))) & 1] +
                     (uVar1 & 3) * 0x24 + 0x1adc))),input);
  sVar7 = (short)iVar4;
  if ((*((int *)camry_host_ptr((uint32_t)(puVar2 + 0xd04)))) < 0) {
    sVar7 = -sVar7;
  }
  sVar6 = (short)(((int)(*((short *)camry_host_ptr((uint32_t)(puVar2 + 0xd08)))) * (int)sVar7) / 0x400);
  (*((short *)camry_host_ptr((uint32_t)(puVar2 + 0xd0c)))) = sVar6;
  iVar4 = ((int)sVar6 - (*((int *)camry_host_ptr((uint32_t)(puVar2 + 0xcf8))))) * (uint)DAT_000b12c4 + (*((int *)camry_host_ptr((uint32_t)(puVar2 + 0xcf4))));
  (*((int *)camry_host_ptr((uint32_t)(puVar2 + 0xcf0)))) = iVar4;
  (*((int *)camry_host_ptr((uint32_t)(puVar2 + 0xcf4)))) = iVar4;
  (*((int *)camry_host_ptr((uint32_t)(puVar2 + -0xc38)))) = iVar4 / 0x4000;
  (*((int *)camry_host_ptr((uint32_t)(puVar2 + 0xcf8)))) = iVar4 / 0x4000;
  uVar5 = FUN_000d1da0(0xffc0);
  (*((short *)camry_host_ptr((uint32_t)(puVar2 + 0xd0a)))) = sVar7;
  (*((undefined4 *)camry_host_ptr((uint32_t)(puVar2 + 0xce4)))) = (*((undefined4 *)camry_host_ptr((uint32_t)(puVar2 + 0x8cc))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(0xd20))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(0x8d0)))));
  (*((undefined4 *)camry_host_ptr((uint32_t)(puVar2 + 0xce8)))) = (*((undefined4 *)camry_host_ptr((uint32_t)(puVar2 + -0xc38))));
  FUN_000d1dc6(uVar5);
  return uVar5;
}



/* WARNING: Removing unreachable block (ram,0x000c8c4c) */
/* WARNING: Removing unreachable block (ram,0x000c8c12) */

void FUN_000c8bc6(void)

{
  uint32_t puVar1;
  int iVar2;
  short input;
  int iVar3;
  int iVar4;
  
  puVar1 = 0xfebeb800u;
  iVar3 = (int)DAT_000b12c2;
  iVar4 = (int)DAT_000b12d2;
  iVar2 = (int)((int)(int16_t)DAT_febeac44);
  if ((DAT_000b12d4 != '\x01') ||
     (((DAT_febec4ec = DAT_febec4e8,
       iVar2 - iVar4 < 0 != (iVar2 < 0 != iVar4 < 0 && iVar4 < 0 == iVar2 - iVar4 < 0) ||
       iVar2 == iVar4 || (DAT_febec4e8 < 1)) &&
      ((iVar2 - iVar4 < 0 == (iVar2 < 0 != iVar4 < 0 && iVar4 < 0 == iVar2 - iVar4 < 0) ||
       (-1 < DAT_febec4e8)))))) {
    DAT_febec4ec = (DAT_febec4e8 * ((int)(int16_t)DAT_febeabce)) / 0x400;
  }
  DAT_febec510 = DAT_000b12c2;
  if (DAT_febec4ec - iVar3 < 0 !=
      (DAT_febec4ec < 0 != iVar3 < 0 && iVar3 < 0 == DAT_febec4ec - iVar3 < 0) ||
      DAT_febec4ec == iVar3) {
    iVar2 = -iVar3;
    if (DAT_febec4ec + iVar3 < 0 ==
        (DAT_febec4ec < 0 != iVar2 < 0 && iVar2 < 0 == DAT_febec4ec + iVar3 < 0) &&
        DAT_febec4ec != iVar2) {
      DAT_febec510 = (short)DAT_febec4ec;
    }
    else {
      DAT_febec510 = (short)iVar2;
    }
  }
  input = f33_abs_s16_wrapping(((int)(int16_t)DAT_febeac44));
  iVar2 = f33_interpolate_signed_sentinel_curve((short *)((undefined *)camry_host_ptr(0xb12d6u)),input);
  (*((short *)camry_host_ptr((uint32_t)(puVar1 + 0xd1a)))) = (short)iVar2;
  (*((short *)camry_host_ptr((uint32_t)(puVar1 + 0xd0e)))) =
       (short)(((int)(short)iVar2 * (int)(*((short *)camry_host_ptr((uint32_t)(puVar1 + 0xd10))))) / 0x400);
  return;
}



int FUN_000c8c58(void)

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



/* WARNING: Removing unreachable block (ram,0x000c8d8a) */
/* WARNING: Removing unreachable block (ram,0x000c8d2a) */

void FUN_000c8c88(void)

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
    iVar1 = -(int)DAT_febec518;
    sVar3 = DAT_000b12cc;
LAB_000c8d18:
    iVar1 = iVar1 * sVar3 + (*((int *)camry_host_ptr((uint32_t)(puVar2 + 0xd00))));
    (*((int *)camry_host_ptr((uint32_t)(puVar2 + 0xcfc)))) = iVar1;
    (*((short *)camry_host_ptr((uint32_t)(puVar2 + 0xd16)))) = (short)(iVar1 / 0x4000);
  }
  else {
    if (DAT_febec521 != '\0') goto LAB_000c8d10;
    puVar2 = 0xfebeb800u;
    sVar3 = f33_abs_s16_wrapping(DAT_febec50e);
    iVar4 = (int)sVar3;
    iVar7 = f33_abs_s32_wrapping(iVar7);
    sVar3 = f33_abs_s16_wrapping((*((short *)camry_host_ptr((uint32_t)(puVar2 + 0xd0a)))));
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
    uVar6 = (undefined2)(((int)sVar3 * (int)(*((short *)camry_host_ptr((uint32_t)(puVar2 + 0xd0e))))) / 0x400);
  }
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar2 + 0xd12)))) = uVar6;
  uVar8 = FUN_000c8c58();
  (*((short *)camry_host_ptr((uint32_t)(puVar2 + 0xd14)))) = (short)uVar8;
  uVar8 = FUN_000c8894(uVar8);
  iVar7 = FUN_000c8956(uVar8);
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



void FUN_000c8dd2(void)

{
  FUN_000c8ab2();
  FUN_000c8bc6();
  FUN_000c8c88();
  return;
}



void FUN_000c8de6(void)

{
  FUN_000c89e6();
  FUN_000c8af2();
  return;
}



/* Constant-block fill: 9 literal assignments into one contiguous cell block; shape-verified.
   Literals are default/reset values; cell meanings are not recovered. */

void f33_fill_constant_block_c8df6(void)

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



void FUN_000c8e1c(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  
  iVar3 = (int)DAT_febeadf2;
  iVar2 = (int)DAT_000b0160;
  iVar1 = (int)DAT_000b0162;
  iVar4 = (int)DAT_febec18a;
  if ((iVar3 - iVar2 < 0 == (iVar3 < 0 != iVar2 < 0 && iVar2 < 0 == iVar3 - iVar2 < 0) &&
       iVar3 != iVar2) &&
     (iVar4 + iVar1 < 0 != (iVar4 < 0 != -iVar1 < 0 && -iVar1 < 0 == iVar4 + iVar1 < 0))) {
    iVar2 = (int)DAT_febec538;
    iVar1 = (int)DAT_000b0168;
    if (iVar2 - iVar1 < 0 != (iVar2 < 0 != iVar1 < 0 && iVar1 < 0 == iVar2 - iVar1 < 0) ||
        iVar2 == iVar1) {
      iVar1 = (int)DAT_000b0168;
      DAT_febec538 = DAT_febec538 + '\x01';
      iVar2 = (int)DAT_febec538;
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
      iVar2 = (int)DAT_febec537;
      iVar1 = (int)DAT_000b0168;
      if (iVar2 - iVar1 < 0 != (iVar2 < 0 != iVar1 < 0 && iVar1 < 0 == iVar2 - iVar1 < 0) ||
          iVar2 == iVar1) {
        iVar1 = (int)DAT_000b0168;
        DAT_febec537 = DAT_febec537 + '\x01';
        iVar2 = (int)DAT_febec537;
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



void FUN_000c8ecc(void)

{
  uint32_t puVar1;
  int iVar2;
  
  puVar1 = 0xfebeb800u;
  iVar2 = f33_interpolate_unsigned_axis_sentinel_curve
                    (*(ushort **)(((undefined *)camry_host_ptr(0xd3810u)) + (DAT_febec156 & 3) * 4),DAT_febeadf6);
  (*((short *)camry_host_ptr((uint32_t)(puVar1 + 0xd30)))) = (short)iVar2;
  return;
}



void FUN_000c8f90(void)

{
  bool bVar1;
  int iVar2;
  int iVar3;
  
  iVar3 = (int)DAT_febec534;
  iVar2 = (int)DAT_000b1274;
  DAT_febec53a = DAT_000b1274;
  if ((iVar3 - iVar2 < 0 != (iVar3 < 0 != iVar2 < 0 && iVar2 < 0 == iVar3 - iVar2 < 0) ||
       iVar3 == iVar2) &&
     (iVar2 = iVar3 + DAT_000b1274, bVar1 = -(int)DAT_000b1274 < 0, DAT_febec53a = DAT_febec534,
     iVar2 < 0 != (iVar3 < 0 != bVar1 && bVar1 == iVar2 < 0))) {
    DAT_febec53a = -DAT_000b1274;
  }
  return;
}



void FUN_000c8fb6(void)

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
    *(undefined2 *)(((undefined *)camry_host_ptr(0xfebec554u)) + iVar3 * 2) = 0x400;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebec54cu + (uint32_t)(iVar3) * 1u)))) = 0;
    iVar2 = iVar3 + 1;
    iVar1 = iVar3 + -6;
    iVar3 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  DAT_febec548 = 0x400;
  DAT_febec54a = 0;
  return;
}



/* WARNING: This is an inlined function */
/* Same12-byte state and preserved R6 as C5106, feeding CE8DA. Exact94-byte body differs only in ROM
   pointer/global displacements; calibration values remain producer-local. Inline real p-code so the
   shared helper's typed argument remains connected in every caller. Prepare common gain state for
   C544; actual register preservation connects the final shared-step caller without a fabricated
   return. */

void f33_prepare_gain_parameters_c544(F33GainSlewState *state,uint mode)

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
    uVar2 = *(ushort *)(((undefined *)camry_host_ptr(0xd3858u)) + iVar1 * 0x10);
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



/* WARNING: Inlined function: f33_prepare_gain_parameters_c544 */

void FUN_000c9058(void)

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
  local_10.current = DAT_febec544;
  if (uVar3 < 7) {
    local_10.direction = '\x02';
    iVar1 = (short)(DAT_febeac3c & 1) * 7 + uVar3;
    local_10.up_target = *(ushort *)(((undefined *)camry_host_ptr(0xd3858u)) + iVar1 * 0x10);
    local_10.down_step = (*((ushort *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd3854u + (uint32_t)(iVar1 * 4) * 4u)))))));
    local_10.up_step = (*((ushort *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd385cu + (uint32_t)(iVar1 * 4) * 4u)))))));
    local_10.down_target = (*((ushort *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd3850u + (uint32_t)(iVar1 * 4) * 4u)))))));
  }
  else {
    local_10.direction = '\x01';
    local_10.up_target = DAT_febec53c;
    local_10.down_step = DAT_febec540;
    local_10.up_step = DAT_febec542;
    local_10.down_target = DAT_febec53e;
  }
  f33_step_retained_unsigned_gain(&local_10);
  (*((ushort *)camry_host_ptr((uint32_t)(puVar2 + 0xd40)))) = local_10.down_step;
  (*((ushort *)camry_host_ptr((uint32_t)(puVar2 + 0xd42)))) = local_10.up_step;
  (*((ushort *)camry_host_ptr((uint32_t)(puVar2 + 0xd3e)))) = local_10.down_target;
  (*((ushort *)camry_host_ptr((uint32_t)(puVar2 + 0xd3c)))) = local_10.up_target;
  (*((ushort *)camry_host_ptr((uint32_t)(puVar2 + 0xd44)))) = local_10.current;
  return;
}



void FUN_000c90a0(void)

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
  uStack_1c = ((int)(int16_t)DAT_febec172);
  uVar4 = (ushort)DAT_febeac3c;
  iVar7 = 0;
  do {
    pcVar1 = ((undefined *)camry_host_ptr(0xd3930u)) + iVar7 * 0xc + (short)(uVar4 & 1) * 0x54;
    local_2c[0] = *pcVar1;
    if (local_2c[0] != '\a') {
      uStack_28 = *(undefined4 *)(pcVar1 + 4);
      iVar2 = iVar7 + (int)uVar5;
      iVar3 = iVar7 * 2 + (int)uVar5;
      uStack_24 = *(undefined4 *)(pcVar1 + 8);
      uStack_20 = (*((undefined1 *)camry_host_ptr((uint32_t)(iVar2 + 0xd4c))));
      uStack_1e = (*((ushort *)camry_host_ptr((uint32_t)(iVar3 + 0xd54))));
      FUN_000ce912(local_2c);
      (*((ushort *)camry_host_ptr((uint32_t)(iVar3 + 0xd54)))) = uStack_1e;
      (*((undefined1 *)camry_host_ptr((uint32_t)(iVar2 + 0xd4c)))) = uStack_20;
      uVar6 = uVar6 * uStack_1e >> 10 & 0xffff;
    }
    iVar3 = iVar7 + 1;
    iVar2 = iVar7 + -6;
    iVar7 = iVar3;
  } while (((iVar2 < 0) || (iVar3 < 0)));
  (*((short *)camry_host_ptr((uint32_t)((int)uVar5 + 0xd48)))) = (short)uVar6;
  return;
}



void FUN_000c9124(void)

{
  FUN_000c9058();
  FUN_000c90a0();
  return;
}



/* WARNING: Removing unreachable block (ram,0x000c9154) */
/* WARNING: Removing unreachable block (ram,0x000c9146) */

void FUN_000c9134(short param_1)

{
  DAT_febec546 = (short)((int)((uint)DAT_febec544 * (int)param_1) / 0x400);
  DAT_febec54a = (short)((int)((uint)DAT_febec548 * (int)DAT_febec546) / 0x400);
  return;
}



/* Constant-block fill: 34 literal assignments into one contiguous cell block; shape-verified.
   Literals are default/reset values; cell meanings are not recovered. */

void f33_fill_constant_block_c9160(void)

{
  DAT_febec590 = 5;
  DAT_febeabde = 0;
  DAT_febeabdc = 0x32;
  DAT_febec594 = 0;
  DAT_febec592 = 0x38;
  DAT_febec564 = 0;
  DAT_febec568 = 0;
  DAT_febec56c = 0;
  DAT_febec570 = 0;
  DAT_febec574 = 0;
  DAT_febec578 = 0;
  DAT_febec596 = 0;
  DAT_febeabe0 = 0;
  DAT_febeabe2 = 0;
  DAT_febec598 = 0;
  DAT_febec59a = 0;
  DAT_febec59c = 0;
  DAT_febec57c = 0;
  DAT_febeabd0 = 0;
  DAT_febeabd4 = 0;
  DAT_febec580 = 0;
  DAT_febec584 = 0;
  DAT_febeabd8 = 0;
  DAT_febeabe4 = 0;
  DAT_febeabe6 = 0;
  DAT_febec59e = 0;
  DAT_febec5a0 = 0;
  DAT_febec5a8 = 0;
  DAT_febec588 = 0;
  DAT_febec58c = 0;
  DAT_febec5a2 = 0;
  DAT_febec5a4 = 0;
  DAT_febec5a6 = 0;
  DAT_febeabe8 = 0;
  return;
}



int FUN_000c91f2(void)

{
  ushort input;
  uint32_t puVar1;
  int iVar2;
  int iVar3;
  
  input = DAT_febeadf6;
  puVar1 = 0xfebeb800u;
  iVar3 = (DAT_febec156 & 3) * 0x24;
  iVar2 = f33_interpolate_unsigned_axis_sentinel_curve
                    (((ushort *)camry_host_ptr((uint32_t)(f33_calibration_bank_bases[DAT_febeac3c & 1] + iVar3 + 0x203c))),
                     DAT_febeadf6);
  (*((short *)camry_host_ptr((uint32_t)(puVar1 + 0xd90)))) = (short)iVar2;
  iVar3 = f33_interpolate_unsigned_axis_sentinel_curve
                    (((ushort *)camry_host_ptr((uint32_t)(f33_calibration_bank_bases[(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0xbc4))))) & 1] + iVar3 + 0x20cc))),input);
  (*((short *)camry_host_ptr((uint32_t)(puVar1 + -0xc24)))) = (short)iVar3;
  (*((short *)camry_host_ptr((uint32_t)(puVar1 + 0xd92)))) = (*((short *)camry_host_ptr((uint32_t)(puVar1 + 0xd90)))) + (short)iVar3 + 1;
  return iVar2;
}



void FUN_000c9258(void)

{
  ushort input;
  uint32_t puVar1;
  int iVar2;
  int iVar3;
  
  input = DAT_febeadf6;
  puVar1 = 0xfebeb800u;
  iVar3 = (DAT_febec156 & 3) * 0x24;
  iVar2 = f33_interpolate_unsigned_axis_sentinel_curve
                    (((ushort *)camry_host_ptr((uint32_t)(f33_calibration_bank_bases[DAT_febeac3c & 1] + iVar3 + 0x215c))),
                     DAT_febeadf6);
  (*((short *)camry_host_ptr((uint32_t)(puVar1 + -0xc22)))) = (short)iVar2;
  iVar3 = f33_interpolate_unsigned_axis_sentinel_curve
                    (((ushort *)camry_host_ptr((uint32_t)(f33_calibration_bank_bases[(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0xbc4))))) & 1] + iVar3 + 0x21ec))),input);
  (*((short *)camry_host_ptr((uint32_t)(puVar1 + 0xd94)))) = (short)iVar3;
  return;
}



/* WARNING: Removing unreachable block (ram,0x000c92ce) */

void FUN_000c92b2(void)

{
  short value;
  uint32_t puVar1;
  short sVar2;
  short sVar3;
  undefined4 uVar4;
  int iVar5;
  
  puVar1 = 0xfebeb800u;
  uVar4 = FUN_000d1da0(0xffc0);
  sVar3 = (*((short *)camry_host_ptr((uint32_t)(puVar1 + 0x79a))));
  value = (*((short *)camry_host_ptr((uint32_t)(puVar1 + 0xda2))));
  FUN_000d1dc6(uVar4);
  sVar2 = f33_abs_s16_wrapping(sVar3 / 2);
  iVar5 = f33_interpolate_signed_sentinel_curve((short *)((undefined *)camry_host_ptr(0xb12f0u)),sVar2);
  sVar2 = (short)iVar5;
  if (sVar3 / 2 < 0) {
    sVar2 = -sVar2;
  }
  (*((short *)camry_host_ptr((uint32_t)(puVar1 + 0xd96)))) = sVar2;
  sVar3 = f33_abs_s16_wrapping(value);
  iVar5 = f33_interpolate_signed_sentinel_curve((short *)((undefined *)camry_host_ptr(0xb1304u)),sVar3);
  sVar3 = (short)iVar5;
  if (value < 0) {
    sVar3 = -sVar3;
  }
  (*((short *)camry_host_ptr((uint32_t)(puVar1 + 0xd98)))) = sVar3;
  return;
}



void FUN_000c9314(void)

{
  int iVar1;
  short sVar2;
  int iVar3;
  int iVar4;
  short sVar5;
  short sVar6;
  int iVar7;
  int iVar8;
  uint uVar9;
  int iVar10;
  uint uVar11;
  
  sVar2 = ((int)(int16_t)DAT_febec59a);
  sVar5 = ((int)(int16_t)DAT_febeabe0);
  iVar1 = DAT_febeabd8;
  iVar4 = DAT_febeabd4;
  iVar10 = (int)((int)(int16_t)DAT_febec596);
  uVar9 = (uint)DAT_000b12e8;
  iVar7 = (int)DAT_000b12e4;
  DAT_febec56c = iVar7;
  sVar6 = DAT_000b12e4;
  if ((iVar10 - iVar7 < 0 != (iVar10 < 0 != iVar7 < 0 && iVar7 < 0 == iVar10 - iVar7 < 0) ||
       iVar10 == iVar7) &&
     (DAT_febec56c = -iVar7, sVar6 = ((int)(int16_t)DAT_febec596),
     iVar10 + iVar7 < 0 !=
     (iVar10 < 0 != DAT_febec56c < 0 && DAT_febec56c < 0 == iVar10 + iVar7 < 0) ||
     iVar10 == DAT_febec56c)) {
    sVar6 = (short)DAT_febec56c;
  }
  iVar7 = (int)((int)(int16_t)DAT_febec592);
  DAT_febec568 = DAT_febeabd0 - DAT_febeabd4;
  DAT_febec564 = DAT_febec568;
  if (iVar7 != 0) {
    if (DAT_febec568 == -0x80000000 && iVar7 == -1) {
      DAT_febec568 = -0x80000000;
      DAT_febec56c = 0;
    }
    else {
      DAT_febec56c = DAT_febec568 % iVar7;
      DAT_febec568 = DAT_febec568 / iVar7;
    }
  }
  iVar8 = (int)((int)(int16_t)DAT_febeabdc);
  iVar10 = (((int)(int16_t)DAT_febeabe0) * 2 + (int)sVar6 + (int)((int)(int16_t)DAT_febeabe2)) * uVar9 +
           (DAT_febeabd4 + DAT_febeabd0) * -2;
  iVar3 = DAT_febec56c * iVar8 * 2;
  if (iVar7 != 0) {
    if (iVar3 == -0x80000000 && iVar7 == -1) {
      iVar3 = -0x80000000;
    }
    else {
      iVar3 = iVar3 / iVar7;
    }
  }
  if (iVar7 != 0) {
    if (iVar10 == -0x80000000 && iVar7 == -1) {
      iVar10 = -0x80000000;
    }
    else {
      iVar10 = iVar10 / iVar7;
    }
  }
  DAT_febeabe0 = sVar6;
  DAT_febeabe2 = sVar5;
  DAT_febeabd4 = DAT_febeabd0;
  DAT_febeabd0 = iVar4 + iVar3 + DAT_febec568 * iVar8 * 2 + iVar10;
  uVar11 = (uint)(DAT_000b12e8 >> 1);
  DAT_febec57c = DAT_febeabd0;
  if (DAT_febeabd0 < 0) {
    iVar4 = uVar11 - DAT_febeabd0;
    if (uVar9 != 0) {
      if (iVar4 == -0x80000000 && uVar9 == 0xffffffff) {
        iVar4 = 0;
      }
      else {
        iVar4 = iVar4 / (int)uVar9;
      }
    }
    iVar4 = -iVar4;
  }
  else {
    iVar4 = uVar11 + DAT_febeabd0;
    if (uVar9 != 0) {
      if (iVar4 == -0x80000000 && uVar9 == 0xffffffff) {
        iVar4 = 0;
      }
      else {
        iVar4 = iVar4 / (int)uVar9;
      }
    }
  }
  iVar3 = (int)((int)(int16_t)DAT_febec598);
  iVar10 = (int)DAT_000b12e6;
  DAT_febeabe4 = (short)iVar4;
  DAT_febec578 = iVar10;
  sVar5 = DAT_000b12e6;
  if ((iVar3 - iVar10 < 0 != (iVar3 < 0 != iVar10 < 0 && iVar10 < 0 == iVar3 - iVar10 < 0) ||
       iVar3 == iVar10) &&
     (DAT_febec578 = -iVar10, sVar5 = ((int)(int16_t)DAT_febec598),
     iVar3 + iVar10 < 0 != (iVar3 < 0 != DAT_febec578 < 0 && DAT_febec578 < 0 == iVar3 + iVar10 < 0)
     || iVar3 == DAT_febec578)) {
    sVar5 = (short)DAT_febec578;
  }
  iVar4 = (int)((int)(int16_t)DAT_febec59a);
  iVar10 = (int)((int)(int16_t)DAT_febec59c);
  DAT_febec59a = sVar5;
  DAT_febec574 = DAT_febec584 - DAT_febeabd8;
  DAT_febec570 = DAT_febec574;
  if (iVar7 != 0) {
    if (DAT_febec574 == -0x80000000 && iVar7 == -1) {
      DAT_febec574 = -0x80000000;
      DAT_febec578 = 0;
    }
    else {
      DAT_febec578 = DAT_febec574 % iVar7;
      DAT_febec574 = DAT_febec574 / iVar7;
    }
  }
  DAT_febeabd8 = DAT_febec584;
  DAT_febec59c = sVar2;
  iVar4 = (iVar4 * 2 + (int)sVar5 + iVar10) * uVar9 + (iVar1 + DAT_febec584) * -2;
  if (iVar7 != 0) {
    if (iVar4 == -0x80000000 && iVar7 == -1) {
      iVar4 = -0x80000000;
    }
    else {
      iVar4 = iVar4 / iVar7;
    }
  }
  iVar10 = DAT_febec578 * iVar8 * 2;
  if (iVar7 != 0) {
    if (iVar10 == -0x80000000 && iVar7 == -1) {
      iVar10 = -0x80000000;
    }
    else {
      iVar10 = iVar10 / iVar7;
    }
  }
  iVar4 = iVar10 + DAT_febec574 * iVar8 * 2 + iVar4;
  DAT_febec580 = iVar1 + iVar4;
  DAT_febec584 = DAT_febec580;
  if (iVar1 + iVar4 < 0) {
    iVar4 = uVar11 - DAT_febec580;
    if (uVar9 != 0) {
      if (iVar4 == -0x80000000 && uVar9 == 0xffffffff) {
        iVar4 = 0;
      }
      else {
        iVar4 = iVar4 / (int)uVar9;
      }
    }
    iVar4 = -iVar4;
  }
  else {
    iVar4 = uVar11 + DAT_febec580;
    if (uVar9 != 0) {
      if (iVar4 == -0x80000000 && uVar9 == 0xffffffff) {
        iVar4 = 0;
      }
      else {
        iVar4 = iVar4 / (int)uVar9;
      }
    }
  }
  DAT_febeabe6 = (short)iVar4;
  return;
}



/* WARNING: Removing unreachable block (ram,0x000c94a0) */
/* WARNING: Removing unreachable block (ram,0x000c9474) */

void FUN_000c945e(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  
  iVar2 = (int)DAT_000b12ea;
  iVar1 = ((int)DAT_febeabe4 * (int)DAT_febeabde) / 0x800;
  iVar3 = iVar2;
  if ((iVar1 - iVar2 < 0 != (iVar1 < 0 != iVar2 < 0 && iVar2 < 0 == iVar1 - iVar2 < 0) ||
       iVar1 == iVar2) &&
     (iVar3 = -iVar2,
     iVar1 + iVar2 < 0 == (iVar1 < 0 != iVar3 < 0 && iVar3 < 0 == iVar1 + iVar2 < 0) &&
     iVar1 != iVar3)) {
    iVar3 = iVar1;
  }
  DAT_febec59e = (short)iVar3;
  iVar3 = (int)DAT_000b12ec;
  iVar1 = ((int)DAT_febeabe6 * (int)DAT_febec594) / 0x100;
  DAT_febec5a0 = DAT_000b12ec;
  if (iVar1 - iVar3 < 0 != (iVar1 < 0 != iVar3 < 0 && iVar3 < 0 == iVar1 - iVar3 < 0) ||
      iVar1 == iVar3) {
    iVar2 = -iVar3;
    if (iVar1 + iVar3 < 0 == (iVar1 < 0 != iVar2 < 0 && iVar2 < 0 == iVar1 + iVar3 < 0) &&
        iVar1 != iVar2) {
      DAT_febec5a0 = (short)iVar1;
    }
    else {
      DAT_febec5a0 = (short)iVar2;
    }
  }
  return;
}



/* WARNING: Removing unreachable block (ram,0x000c953a) */

void FUN_000c9524(void)

{
  DAT_febec588 = (int)((int)(int16_t)DAT_febebf9a) - (int)((int)(int16_t)DAT_febec5a4);
  DAT_febec58c = (((int)((int)(int16_t)DAT_febebf9a) - (int)((int)(int16_t)DAT_febec5a4)) * 100) / 0x20;
  DAT_febec5a2 = 0x7fff;
  if ((int)DAT_febec58c + -0x7fff < 0 != ((int)DAT_febec58c < 0 && -1 < (int)DAT_febec58c + -0x7fff) ||
      DAT_febec58c == 0x7fff) {
    if ((int)DAT_febec58c + 0x7fff < 0 == (-1 < (int)DAT_febec58c && (int)DAT_febec58c + 0x7fff < 0) &&
        DAT_febec58c != -0x7fff) {
      DAT_febec5a2 = (undefined2)DAT_febec58c;
    }
    else {
      DAT_febec5a2 = 0x8001;
    }
  }
  DAT_febec5a4 = ((int)(int16_t)DAT_febebf9a);
  return;
}



/* Single constant publisher: DAT_febec5ac = 1; Shape-classified from the canonical corpus; the
   target cell is not yet named, so the written state's meaning is unknown. */

void FUN_000c9562(void)

{
  DAT_febec5ac = 1;
  return;
}



void FUN_000c956a(void)

{
  if ((DAT_febeaccc != 0) || (DAT_febec5ac = 0, DAT_febead6f != 0)) {
    if (((DAT_febeaccc >> 1 & 1) == 0) && ((DAT_febead6f & 2) == 0)) {
      DAT_febec5ac = 1;
    }
    else {
      DAT_febec5ac = 2;
    }
  }
  return;
}



/* Constant-block fill: 36 literal assignments into one contiguous cell block; shape-verified.
   Literals are default/reset values; cell meanings are not recovered. */

void f33_fill_constant_block_c9590(void)

{
  DAT_febec5e5 = 1;
  DAT_febec5f2 = 0;
  DAT_febec5e4 = 0;
  DAT_febec5f3 = 0;
  DAT_febec5bc = DAT_000b0180;
  DAT_febec5e6 = 0;
  DAT_febec5c0 = 0;
  DAT_febec5c2 = 0;
  DAT_febeabec = 0;
  DAT_febec5ec = 0;
  DAT_febeabf0 = 0;
  DAT_febeabf2 = 0;
  DAT_febec5c4 = 0;
  DAT_febec5c6 = 0;
  DAT_febeabf4 = 0;
  DAT_febeabf6 = 0;
  DAT_febec5c8 = 0;
  DAT_febec5ca = 0;
  DAT_febec5cc = 0;
  DAT_febec5ce = 0;
  DAT_febec5d0 = 0;
  DAT_febeabfa = 0;
  DAT_febeabf8 = 0;
  DAT_febec5b8 = 0;
  DAT_febec5b0 = 0;
  DAT_febec5ba = 0;
  DAT_febec5be = DAT_000b0180;
  DAT_febec5f4 = 0;
  DAT_febec5ee = 0;
  DAT_febec5b4 = 0;
  DAT_febec5d2 = 0;
  DAT_febec5e7 = 0;
  DAT_febec5e8 = 0;
  DAT_febec5e9 = 0;
  DAT_febec5d6 = 0;
  DAT_febec5d8 = 0;
  return;
}



/* Constant-block fill: 8 literal assignments into one contiguous cell block; shape-verified.
   Literals are default/reset values; cell meanings are not recovered. */

void f33_fill_constant_block_c962e(void)

{
  DAT_febec5f0 = 0;
  DAT_febec5d4 = 0;
  DAT_febec5ea = 0;
  DAT_febec5de = 0;
  DAT_febec5da = 0;
  DAT_febec5dc = 0;
  DAT_febec5e0 = 0;
  DAT_febec5e2 = 0;
  return;
}



void FUN_000c9650(void)

{
  char cVar1;
  
  cVar1 = DAT_febec5e5;
  if ((((DAT_febec5f2 == '\0') && (DAT_000b0187 == '\x01')) && (DAT_febec5ac == 0)) &&
     ((DAT_febeacce == '\x01' && (DAT_febeaf08 == 0x55aaaa55)))) {
    DAT_febec5e4 = DAT_febec5e4 + 1;
    if (DAT_000b0186 <= DAT_febec5e4) {
      DAT_febec5f2 = DAT_febeacce;
    }
  }
  else {
    DAT_febec5e4 = 0;
  }
  if (((((DAT_febec5f3 == '\0') && (DAT_febec5e5 == '\x01')) &&
       ((DAT_febec5f2 == '\x01' &&
        (((DAT_febeacbd == '\0' && (DAT_febeacce == '\x01')) && (DAT_febec601 == '\0')))))) &&
      ((DAT_febec602 == '\0' && (DAT_febeacbe == '\x01')))) &&
     ((DAT_febec5ac == 0 && ((DAT_febead19 == '\0' && ((DAT_febeadfc & 0x1ff) == 0)))))) {
    DAT_febec5e5 = '\0';
    DAT_febec5f3 = cVar1;
  }
  if ((DAT_febec5f3 == '\x01') &&
     ((((DAT_febec601 == '\x01' || (DAT_febec602 == '\x01')) || (DAT_febeacbe == '\0')) ||
      ((((DAT_febec5ac >> 1 & 1) != 0 || (DAT_febec603 == '\x01')) ||
       ((DAT_febead19 == '\"' || ((DAT_febead19 == 'D' || ((DAT_febeadfc & 0x1ff) != 0)))))))))) {
    DAT_febec5f3 = '\0';
  }
  return;
}



/* Native composed release clears the gain sub-state and advances retained accumulator3072 to2560
   using exact6144 coefficients; gain512 decays to426 rather than clearing immediately. */

short FUN_000c973a(void)

{
  char cVar1;
  uint32_t puVar2;
  short sVar3;
  int iVar4;
  int iVar5;
  int iVar6;
  
  puVar2 = 0xfebeb800u;
  cVar1 = DAT_febec5f4;
  if (DAT_febec5f4 == '\0') {
    if (((DAT_febec5f3 != '\x01') || (DAT_febec5ac != 0)) ||
       ((DAT_febeacce != '\x01' ||
        ((DAT_febeaccd != '\0' || (cVar1 = DAT_febeacbd == '\0', !(bool)cVar1))))))
    goto LAB_000c978e;
  }
  else {
    if ((((DAT_febec5f3 != '\0') && ((DAT_febec5ac & 1) == 0)) && (DAT_febeacce != '\0')) &&
       ((DAT_febeaccd != '\x01' && (DAT_febeacbd == '\0')))) goto LAB_000c978e;
    cVar1 = false;
  }
  DAT_febec5f4 = cVar1;
  cVar1 = DAT_febec5f4;
LAB_000c978e:
  iVar4 = (int)((int)(int16_t)DAT_febec5be);
  DAT_febec5bc = DAT_000b0180;
  DAT_febec5ba = DAT_000b016e;
  if (cVar1 == '\x01') {
    DAT_febec5bc = DAT_000b017e;
    DAT_febec5ba = DAT_000b016c;
  }
  iVar5 = (int)DAT_febec5bc;
  iVar6 = DAT_febec5b0 * DAT_febec5bc;
  if (iVar4 != 0) {
    if (iVar6 == -0x80000000 && iVar4 == -1) {
      iVar6 = -0x80000000;
    }
    else {
      iVar6 = iVar6 / iVar4;
    }
  }
  DAT_febec5b0 = (((int)(int16_t)DAT_febec5ba) + iVar6) - (int)((int)(int16_t)DAT_febec5b8);
  iVar4 = DAT_febec5b0 * 0x400;
  if (iVar5 != 0) {
    if (iVar4 == -0x80000000 && iVar5 == -1) {
      iVar4 = 0;
    }
    else {
      iVar4 = iVar4 / iVar5;
    }
  }
  DAT_febec5b8 = (short)iVar4;
  DAT_febec5be = DAT_febec5bc;
  sVar3 = f33_abs_s16_wrapping(((int)(int16_t)DAT_febec5b8) - ((int)(int16_t)DAT_febec5ba));
  iVar4 = (int)sVar3;
  if (iVar4 + -0x14 < 0 != (iVar4 < 0 && -1 < iVar4 + -0x14) || iVar4 == 0x14) {
    (*((undefined2 *)camry_host_ptr((uint32_t)(puVar2 + 0xdb8)))) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar2 + 0xdba))));
  }
  return sVar3;
}



/* Native foreground subsequence preserves C5EC and its accumulator when admission is inactive.
   Prior nonzero state remains despite zero current source; no claim about retained-drive initial
   state. */

void FUN_000c9812(void)

{
  ushort uVar1;
  undefined1 uVar2;
  uint uVar3;
  uint32_t puVar4;
  short input;
  int iVar5;
  int iVar6;
  
  uVar1 = DAT_febeadf6;
  puVar4 = 0xfebeb800u;
  uVar3 = (uint)DAT_febec156;
  if (DAT_febec5f3 != '\x01') {
    return;
  }
  input = f33_abs_s16_wrapping(DAT_febec5fc);
  iVar5 = f33_interpolate_signed_sentinel_curve(((short *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd39dcu + (uint32_t)(uVar3 & 3) * 4u)))))),input);
  if ((*((short *)camry_host_ptr((uint32_t)(puVar4 + 0xdfc)))) < 0) {
    iVar5 = (int)(short)-(short)iVar5;
  }
  (*((short *)camry_host_ptr((uint32_t)(puVar4 + 0xdc0)))) = (short)iVar5;
  if (uVar1 < DAT_000b0170) {
    if (uVar1 != DAT_000b0172) goto LAB_000c987a;
    uVar2 = 0;
  }
  else {
    uVar2 = 1;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(0xde6))))) = uVar2;
LAB_000c987a:
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(0xde6))))) != '\x01') {
    iVar5 = 0;
  }
  (*((short *)camry_host_ptr((uint32_t)(puVar4 + 0xdc2)))) = (short)iVar5;
  iVar5 = ((*((int *)camry_host_ptr((uint32_t)(puVar4 + -0xc14)))) + iVar5) - (int)(*((short *)camry_host_ptr((uint32_t)(puVar4 + 0xdec))));
  (*((int *)camry_host_ptr((uint32_t)(puVar4 + -0xc14)))) = iVar5;
  iVar6 = (int)DAT_000b0174;
  iVar5 = iVar5 * 0x400;
  if (iVar6 != 0) {
    if (iVar5 == -0x80000000 && iVar6 == -1) {
      iVar5 = 0;
    }
    else {
      iVar5 = iVar5 / iVar6;
    }
  }
  (*((short *)camry_host_ptr((uint32_t)(puVar4 + 0xdec)))) = (short)iVar5;
  return;
}



/* WARNING: Removing unreachable block (ram,0x000c9a50) */
/* WARNING: Removing unreachable block (ram,0x000c99b4) */
/* WARNING: Removing unreachable block (ram,0x000c9964) */
/* WARNING: Removing unreachable block (ram,0x000c993e) */

void FUN_000c98ae(void)

{
  short sVar1;
  uint32_t puVar2;
  short sVar3;
  short sVar4;
  int iVar5;
  int iVar6;
  uint uVar7;
  
  sVar1 = DAT_febec128;
  sVar4 = DAT_febeadf0;
  uVar7 = DAT_febec156 & 3;
  puVar2 = 0xfebeb800u;
  if (DAT_febec5f3 == '\x01') {
    puVar2 = 0xfebeb800u;
    sVar3 = f33_abs_s16_wrapping((short)DAT_febec600);
    iVar5 = f33_interpolate_signed_sentinel_curve(((short *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd3a1cu + (uint32_t)(uVar7) * 4u)))))),sVar3);
    sVar3 = (short)iVar5;
    if ((char)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(0xe00))))) < '\0') {
      sVar3 = -sVar3;
    }
    (*((short *)camry_host_ptr((uint32_t)(puVar2 + -0xc10)))) = sVar3;
    sVar3 = f33_abs_s16_wrapping(sVar4);
    iVar5 = f33_interpolate_signed_sentinel_curve(((short *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd3a5cu + (uint32_t)(uVar7) * 4u)))))),sVar3);
    sVar3 = (short)iVar5;
    if (sVar4 < 0) {
      sVar3 = -sVar3;
    }
    (*((short *)camry_host_ptr((uint32_t)(puVar2 + -0xc0e)))) = sVar3;
    sVar3 = f33_abs_s16_wrapping((short)(char)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(0xe00))))));
    iVar5 = f33_interpolate_signed_sentinel_curve(((short *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd3a9cu + (uint32_t)(uVar7) * 4u)))))),sVar3);
    (*((short *)camry_host_ptr((uint32_t)(puVar2 + 0xdc4)))) = (short)iVar5;
    sVar3 = (short)(((int)(short)iVar5 * (int)(*((short *)camry_host_ptr((uint32_t)(puVar2 + -0xc0e))))) / 0x400);
    (*((short *)camry_host_ptr((uint32_t)(puVar2 + 0xdc6)))) = sVar3;
    if (((0 < sVar1) && (sVar4 < 0)) || ((sVar1 < 0 && (0 < sVar4)))) {
      sVar3 = (short)(((int)DAT_000b0176 * (int)sVar3) / 0x100);
    }
    (*((short *)camry_host_ptr((uint32_t)(puVar2 + -0xc0c)))) = sVar3;
    sVar3 = f33_abs_s16_wrapping((short)(char)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(0xe00))))));
    iVar5 = f33_interpolate_signed_sentinel_curve(((short *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd3adcu + (uint32_t)(uVar7) * 4u)))))),sVar3);
    sVar3 = (short)iVar5;
    if (sVar1 < 0) {
      sVar3 = -sVar3;
    }
    (*((short *)camry_host_ptr((uint32_t)(puVar2 + -0xc0a)))) = sVar3;
    sVar3 = f33_abs_s16_wrapping(sVar4);
    iVar5 = f33_interpolate_signed_sentinel_curve(((short *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd3b1cu + (uint32_t)(uVar7) * 4u)))))),sVar3);
    (*((short *)camry_host_ptr((uint32_t)(puVar2 + 0xdc8)))) = (short)iVar5;
    sVar3 = (short)(((int)(short)iVar5 * (int)(*((short *)camry_host_ptr((uint32_t)(puVar2 + -0xc0a))))) / 0x400);
    iVar5 = (int)sVar3;
    (*((short *)camry_host_ptr((uint32_t)(puVar2 + 0xdca)))) = sVar3;
    if (((0 < sVar1) && (sVar4 < 0)) || ((sVar1 < 0 && (0 < sVar4)))) {
      sVar4 = f33_abs_s16_wrapping((*((short *)camry_host_ptr((uint32_t)(puVar2 + 0xdcc)))));
      iVar6 = (int)sVar4;
      iVar5 = (int)DAT_000b0178;
      if (iVar6 - iVar5 < 0 == (iVar6 < 0 != iVar5 < 0 && iVar5 < 0 == iVar6 - iVar5 < 0) &&
          iVar6 != iVar5) {
        iVar5 = (int)(*((short *)camry_host_ptr((uint32_t)(puVar2 + 0xdcc))));
        iVar6 = (int)DAT_000b017a;
        sVar4 = DAT_000b0178;
        if (iVar5 - iVar6 < 0 == (iVar5 < 0 != iVar6 < 0 && iVar6 < 0 == iVar5 - iVar6 < 0) &&
            iVar5 != iVar6) {
          sVar4 = -DAT_000b0178;
        }
        iVar5 = (int)(short)((*((short *)camry_host_ptr((uint32_t)(puVar2 + 0xdcc)))) + sVar4);
      }
      else {
        iVar5 = 0;
      }
      sVar3 = (short)iVar5;
    }
    (*((short *)camry_host_ptr((uint32_t)(puVar2 + 0xdcc)))) = sVar3;
  }
  else {
    DAT_febeabf0 = 0;
    iVar5 = 0;
    DAT_febeabf4 = 0;
  }
  (*((short *)camry_host_ptr((uint32_t)(puVar2 + 0xdce)))) = (short)iVar5;
  iVar5 = iVar5 + (int)(*((short *)camry_host_ptr((uint32_t)(puVar2 + -0xc0c)))) + (int)(*((short *)camry_host_ptr((uint32_t)(puVar2 + -0xc10))));
  if (iVar5 + -0x7fff < 0 == (iVar5 < 0 && -1 < iVar5 + -0x7fff) && iVar5 != 0x7fff) {
    iVar5 = 0x7fff;
  }
  else if (iVar5 + 0x7fff < 0 != (-1 < iVar5 && iVar5 + 0x7fff < 0)) {
    iVar5 = -0x7fff;
  }
  (*((short *)camry_host_ptr((uint32_t)(puVar2 + 0xdd0)))) = (short)iVar5;
  (*((short *)camry_host_ptr((uint32_t)(puVar2 + -0xc06)))) =
       (short)(((int)(*((short *)camry_host_ptr((uint32_t)(puVar2 + -0xc08)))) * (int)(short)iVar5) / 0x400);
  return;
}



void FUN_000c9a5c(void)

{
  uint32_t puVar1;
  int iVar2;
  
  puVar1 = 0xfebeb800u;
  iVar2 = f33_interpolate_unsigned_axis_sentinel_curve
                    (((ushort *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd3b5cu + (uint32_t)(DAT_febec156 & 3) * 4u)))))),DAT_febeadf6);
  (*((short *)camry_host_ptr((uint32_t)(puVar1 + -0xc08)))) = (short)iVar2;
  return;
}



/* WARNING: Removing unreachable block (ram,0x000c9af8) */
/* Native composed release publishes C5EE=426 from held C5EC=1024 and decayed gain426 while
   admission and current source are zero. Earlier admission and secondary producers remain outside
   this scenario boundary. */

void FUN_000c9a84(void)

{
  int iVar1;
  int iVar2;
  uint32_t puVar3;
  short sVar4;
  int iVar5;
  int iVar6;
  
  puVar3 = 0xfebeb800u;
  iVar5 = (int)((int)(int16_t)DAT_febec5b8);
  iVar1 = (int)DAT_000b016e;
  iVar6 = (int)DAT_000b016c;
  if ((iVar5 - iVar6 < 0 != (iVar5 < 0 != iVar6 < 0 && iVar6 < 0 == iVar5 - iVar6 < 0) ||
       iVar5 == iVar6) &&
     (iVar6 = iVar1,
     iVar5 - iVar1 < 0 == (iVar5 < 0 != iVar1 < 0 && iVar1 < 0 == iVar5 - iVar1 < 0) &&
     iVar5 != iVar1)) {
    iVar6 = iVar5;
  }
  if ((DAT_febec5f3 == '\x01') ||
     (iVar6 - iVar1 < 0 == (iVar6 < 0 != iVar1 < 0 && iVar1 < 0 == iVar6 - iVar1 < 0) &&
      iVar6 != iVar1)) {
    puVar3 = 0xfebeb800u;
    sVar4 = f33_abs_s16_wrapping(((int)(int16_t)DAT_febec5fc));
    if (0 < sVar4) {
      (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0xc06)))) = 0;
    }
    sVar4 = DAT_000b017c;
    iVar5 = (int)DAT_000b017c;
    iVar1 = (int)(*((short *)camry_host_ptr((uint32_t)(puVar3 + 0xdec)))) + (int)(*((short *)camry_host_ptr((uint32_t)(puVar3 + -0xc06))));
    (*((int *)camry_host_ptr((uint32_t)(puVar3 + 0xdb4)))) = iVar1;
    if (iVar1 - iVar5 < 0 != (iVar1 < 0 != iVar5 < 0 && iVar5 < 0 == iVar1 - iVar5 < 0) ||
        iVar1 == iVar5) {
      iVar2 = -iVar5;
      if (iVar1 + iVar5 < 0 == (iVar1 < 0 != iVar2 < 0 && iVar2 < 0 == iVar1 + iVar5 < 0) &&
          iVar1 != iVar2) {
        iVar2 = iVar1;
      }
      sVar4 = (short)iVar2;
    }
  }
  else {
    sVar4 = 0;
  }
  (*((short *)camry_host_ptr((uint32_t)(puVar3 + 0xdd2)))) = sVar4;
  (*((short *)camry_host_ptr((uint32_t)(puVar3 + 0xdee)))) = (short)(((int)(short)iVar6 * (int)sVar4) / 0x400);
  return;
}



void FUN_000c9b04(void)

{
  bool bVar1;
  int iVar2;
  int iVar3;
  undefined1 uVar4;
  int iVar5;
  
  iVar2 = (int)DAT_febec600;
  iVar5 = (int)DAT_000b0188;
  iVar3 = (int)DAT_000b0189;
  if (iVar2 < 0) {
    iVar2 = (int)-DAT_febec600;
  }
  if ((DAT_febec5f4 == '\x01') &&
     (iVar2 - iVar5 < 0 == (iVar2 < 0 != iVar5 < 0 && iVar5 < 0 == iVar2 - iVar5 < 0) &&
      iVar2 != iVar5)) {
    uVar4 = DAT_000b0182 < DAT_febeadf6;
  }
  else {
    uVar4 = false;
  }
  DAT_febec5e8 = (bool)uVar4;
  if (((DAT_febec5f4 == '\0') ||
      (iVar2 - iVar3 < 0 != (iVar2 < 0 != iVar3 < 0 && iVar3 < 0 == iVar2 - iVar3 < 0) ||
       iVar2 == iVar3)) || (DAT_febeadf6 <= DAT_000b0182)) {
    DAT_febec5e9 = 2;
    bVar1 = true;
  }
  else {
    DAT_febec5e9 = 0;
    bVar1 = false;
  }
  if (DAT_febec5e7 == '\0') {
    if (!(bool)uVar4) {
      return;
    }
  }
  else if (DAT_febec5e7 == '\x01') {
    if (!bVar1) {
      return;
    }
    DAT_febec5d6 = 0;
    uVar4 = 2;
  }
  else if (!(bool)uVar4) {
    if (DAT_febec5d6 <= DAT_000b0184) {
      DAT_febec5d6 = DAT_febec5d6 + 1;
    }
    if (DAT_febec5d6 <= DAT_000b0184) {
      return;
    }
    uVar4 = 0;
  }
  DAT_febec5e7 = uVar4;
  return;
}



void FUN_000c9ba6(void)

{
  uint32_t puVar1;
  int iVar2;
  
  puVar1 = 0xfebeb800u;
  iVar2 = f33_interpolate_unsigned_axis_sentinel_curve
                    (((ushort *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd3b9cu + (uint32_t)(DAT_febec156 & 3) * 4u)))))),DAT_febeadf6);
  (*((short *)camry_host_ptr((uint32_t)(puVar1 + 0xdd8)))) = (short)iVar2;
  return;
}



/* WARNING: Removing unreachable block (ram,0x000c9c6c) */
/* WARNING: Removing unreachable block (ram,0x000c9c60) */
/* WARNING: Removing unreachable block (ram,0x000c9c2e) */

ushort FUN_000c9bce(void)

{
  char cVar1;
  undefined2 uVar2;
  short sVar3;
  short sVar4;
  uint uVar5;
  uint uVar6;
  uint32_t puVar7;
  ushort uVar8;
  undefined *puVar9;
  
  cVar1 = DAT_febec5e7;
  sVar4 = DAT_febeac42;
  puVar7 = 0xfebeb800u;
  uVar5 = (uint)DAT_febec156;
  uVar8 = f33_abs_s16_wrapping(DAT_febeac42);
  uVar2 = 0;
  if (cVar1 == '\x01' || cVar1 == '\x02') {
    uVar6 = (uint)(uVar8 >> 8);
    puVar9 = ((void *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd3bdcu + (uint32_t)(uVar5 & 3) * 4u)))))));
    if (uVar6 < 0x7f) {
      sVar3 = (short)((int)((uint)(byte)uVar8 *
                           ((int)*(short *)(puVar9 + (uVar6 + 1) * 4 + 2) -
                           (int)*(short *)(puVar9 + uVar6 * 4 + 2))) / 0x100) +
              *(short *)(puVar9 + uVar6 * 4 + 2);
    }
    else {
      sVar3 = *(short *)(puVar9 + 0x1fe);
    }
    (*((short *)camry_host_ptr((uint32_t)(puVar7 + 0xde2)))) = (short)(uVar5 & 3);
    (*((ushort *)camry_host_ptr((uint32_t)(puVar7 + 0xdda)))) = uVar8;
    if (sVar4 < 0) {
      sVar3 = -sVar3;
    }
    (*((short *)camry_host_ptr((uint32_t)(puVar7 + 0xdd4)))) = sVar3;
    (*((short *)camry_host_ptr((uint32_t)(puVar7 + 0xddc)))) = sVar4;
    (*((short *)camry_host_ptr((uint32_t)(puVar7 + 0xdde)))) = (*((short *)camry_host_ptr((uint32_t)(puVar7 + 0xdd8))));
    sVar4 = (short)(((int)(*((short *)camry_host_ptr((uint32_t)(puVar7 + 0xdd8)))) * (int)sVar3) / 0x400);
    (*((short *)camry_host_ptr((uint32_t)(puVar7 + 0xde0)))) = sVar4;
    uVar2 = (undefined2)(((int)sVar4 << 10) / 0x400);
  }
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar7 + 0xdf0)))) = uVar2;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar7 + (uint32_t)(0xdea))))) = cVar1;
  return uVar8;
}



/* Constant-block fill: 11 literal assignments into one contiguous cell block; shape-verified.
   Literals are default/reset values; cell meanings are not recovered. */

void f33_fill_constant_block_c9c7c(void)

{
  DAT_febec5fc = 0;
  DAT_febec600 = 0;
  DAT_febec5f6 = 0;
  DAT_febec5f7 = 0;
  DAT_febec601 = 0;
  DAT_febec602 = 0;
  DAT_febec5fe = 0;
  DAT_febec603 = 0;
  DAT_febec5fa = 0;
  DAT_febec5f8 = 0;
  DAT_febec5f9 = 0;
  return;
}



void FUN_000c9caa(void)

{
  bool bVar1;
  bool bVar2;
  short sVar3;
  int iVar4;
  int iVar5;
  uint32_t puVar6;
  short sVar7;
  int iVar9;
  int iVar8;
  
  sVar3 = ((int)(int16_t)DAT_febeae06);
  puVar6 = 0xfebeb800u;
  iVar9 = (int)((int)(int16_t)DAT_febeae06);
  sVar7 = f33_abs_s16_wrapping(((int)(int16_t)DAT_febeae06));
  iVar8 = (int)sVar7;
  iVar4 = (int)DAT_000b044a;
  iVar5 = (int)DAT_000b044a;
  bVar2 = iVar8 - iVar4 < 0 == (iVar8 < 0 != iVar4 < 0 && iVar4 < 0 == iVar8 - iVar4 < 0);
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(0xdf6))))) = bVar2 && iVar8 != iVar4;
  sVar7 = DAT_000b044a;
  if ((iVar9 - iVar5 < 0 != (iVar9 < 0 != iVar5 < 0 && iVar5 < 0 == iVar9 - iVar5 < 0) ||
       iVar9 == iVar5) &&
     (iVar5 = iVar9 + DAT_000b044a, bVar1 = -(int)DAT_000b044a < 0, sVar7 = sVar3,
     iVar5 < 0 != (iVar9 < 0 != bVar1 && bVar1 == iVar5 < 0))) {
    sVar7 = -DAT_000b044a;
  }
  (*((short *)camry_host_ptr((uint32_t)(puVar6 + 0xdfc)))) = sVar7;
  if (bVar2 && iVar8 != iVar4) {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(0xe01))))) = 1;
  }
  if ((((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(0xdf2))))) == '\x01') && ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(0xe01))))) == '\x01')) && ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(0xdf8))))) == '\0')) {
    f33_report_diagnostic_event_failure_ffff_32_bdb64(200);
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(0xdf8))))) = 1;
  }
  return;
}



short FUN_000c9d18(void)

{
  bool bVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  uint32_t puVar6;
  short sVar7;
  int iVar9;
  int iVar8;
  
  puVar6 = 0xfebeb800u;
  iVar9 = (int)((int)(int16_t)DAT_febeae04);
  sVar7 = f33_abs_s16_wrapping(((int)(int16_t)DAT_febeae04));
  iVar8 = (int)sVar7;
  iVar2 = (int)DAT_000b044c;
  iVar3 = (int)DAT_000b044c;
  bVar1 = iVar8 - iVar2 < 0 == (iVar8 < 0 != iVar2 < 0 && iVar2 < 0 == iVar8 - iVar2 < 0);
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(0xdf7))))) = bVar1 && iVar8 != iVar2;
  iVar4 = (int)DAT_000b044c;
  iVar5 = iVar4;
  if ((iVar9 - iVar3 < 0 != (iVar9 < 0 != iVar3 < 0 && iVar3 < 0 == iVar9 - iVar3 < 0) ||
       iVar9 == iVar3) &&
     (iVar5 = iVar9,
     iVar9 + iVar4 < 0 != (iVar9 < 0 != -iVar4 < 0 && -iVar4 < 0 == iVar9 + iVar4 < 0))) {
    iVar5 = -(int)DAT_000b044c;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(0xe00))))) = (char)iVar5;
  if (bVar1 && iVar8 != iVar2) {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(0xe02))))) = 1;
  }
  if ((((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(0xdf2))))) == '\x01') && ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(0xe02))))) == '\x01')) && ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(0xdf9))))) == '\0')) {
    f33_report_diagnostic_event_failure_ffff_32_bdb64(0xc9);
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(0xdf9))))) = 1;
  }
  return sVar7;
}



void FUN_000c9d86(void)

{
  ushort uVar1;
  ushort uVar2;
  int iVar3;
  uint32_t puVar4;
  short sVar5;
  int iVar6;
  
  puVar4 = 0xfebeb800u;
  if (DAT_febec5f3 == '\x01') {
    puVar4 = 0xfebeb800u;
    sVar5 = f33_abs_s16_wrapping(DAT_febec5ee);
    uVar2 = DAT_000b0446;
    iVar6 = (int)sVar5;
    iVar3 = (int)DAT_000b0448;
    if (iVar6 - iVar3 < 0 == (iVar6 < 0 != iVar3 < 0 && iVar3 < 0 == iVar6 - iVar3 < 0) &&
        iVar6 != iVar3) {
      uVar1 = (*((ushort *)camry_host_ptr((uint32_t)(puVar4 + 0xdfe))));
      if ((uVar1 <= DAT_000b0446) &&
         ((*((ushort *)camry_host_ptr((uint32_t)(puVar4 + 0xdfe)))) = uVar1 + 1, uVar2 < (ushort)(uVar1 + 1))) {
        (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(0xe03))))) = 1;
      }
      goto LAB_000c9dd0;
    }
  }
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar4 + 0xdfe)))) = 0;
LAB_000c9dd0:
  if (((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(0xe03))))) == '\x01') && ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(0xdfa))))) == '\0')) {
    f33_report_diagnostic_event_failure_ffff_32_bdb64(0xca);
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(0xdfa))))) = 1;
  }
  return;
}



/* Constant-block fill: 5 literal assignments into one contiguous cell block; shape-verified.
   Literals are default/reset values; cell meanings are not recovered. */

void f33_fill_constant_block_c9df2(void)

{
  DAT_febec608 = 1;
  DAT_febec609 = 1;
  DAT_febec60a = 1;
  DAT_febec604 = 0;
  DAT_febec606 = 0;
  return;
}



void FUN_000c9e0a(void)

{
  DAT_febec60c = 0;
  DAT_febec60e = 0;
  DAT_febec60f = 0;
  return;
}



void FUN_000c9e18(void)

{
  DAT_febec60e = DAT_febeacf0;
  DAT_febec60f = DAT_febeacef;
  DAT_febec60c = DAT_febeae10;
  if ((((int8_t)DAT_febeacf0) == -0x5b) && (((int8_t)DAT_febeacef) != -1)) {
    DAT_febec60f = DAT_febeacef + '\x01';
  }
  return;
}



void FUN_000c9e44(void)

{
  int iVar1;
  ushort uVar2;
  ushort uVar3;
  int iVar4;
  uint32_t puVar5;
  short sVar6;
  
  puVar5 = 0xfebeb800u;
  if (DAT_febec5f3 == '\x01') {
    sVar6 = f33_abs_s16_wrapping(DAT_febec5ec);
    uVar3 = DAT_000b0452;
    iVar4 = (int)DAT_000b044e;
    iVar1 = sVar6 - iVar4;
    if (iVar1 < 0 == (sVar6 < 0 != iVar4 < 0 && iVar4 < 0 == iVar1 < 0)) {
      uVar2 = (*((ushort *)camry_host_ptr((uint32_t)(puVar5 + 0xe04))));
      if ((uVar2 < DAT_000b0452) &&
         ((*((ushort *)camry_host_ptr((uint32_t)(puVar5 + 0xe04)))) = uVar2 + 1, uVar3 <= (ushort)(uVar2 + 1))) {
        (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(0xe09))))) = 0;
      }
    }
    else {
      (*((undefined2 *)camry_host_ptr((uint32_t)(puVar5 + 0xe04)))) = 0;
    }
    sVar6 = f33_abs_s16_wrapping((*((short *)camry_host_ptr((uint32_t)(puVar5 + -0xc06)))));
    uVar3 = DAT_000b0454;
    iVar4 = (int)DAT_000b0450;
    iVar1 = sVar6 - iVar4;
    if (iVar1 < 0 == (sVar6 < 0 != iVar4 < 0 && iVar4 < 0 == iVar1 < 0)) {
      uVar2 = (*((ushort *)camry_host_ptr((uint32_t)(puVar5 + 0xe06))));
      if ((uVar2 < DAT_000b0454) &&
         ((*((ushort *)camry_host_ptr((uint32_t)(puVar5 + 0xe06)))) = uVar2 + 1, uVar3 <= (ushort)(uVar2 + 1))) {
        (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(0xe0a))))) = 0;
      }
    }
    else {
      (*((undefined2 *)camry_host_ptr((uint32_t)(puVar5 + 0xe06)))) = 0;
    }
    if (((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(0xe09))))) == '\0') || ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(0xe0a))))) == '\0')) {
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(0xe08))))) = 0;
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(0xe09))))) = 1;
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(0xe0a))))) = 1;
    }
  }
  return;
}



void FUN_000c9eea(void)

{
  if ((DAT_febec5f3 == '\x01') && (DAT_febec608 == '\0')) {
    DAT_febec60e = 0xa5;
    DAT_febec60f = 0;
    if (DAT_febec60c < 0xff) {
      DAT_febec60c = DAT_febec60c + 1;
    }
    DAT_febec608 = '\x01';
  }
  return;
}



void FUN_000c9f1e(void)

{
  DAT_febeae10 = DAT_febec60c;
  DAT_febeacf0 = DAT_febec60e;
  DAT_febeacef = DAT_febec60f;
  return;
}



void FUN_000c9f38(void)

{
  int iVar1;
  undefined4 uVar2;
  uint uVar3;
  
  uVar2 = DAT_febeaee8;
  DAT_febec61c = 0;
  DAT_febec618 = 0;
  DAT_febec614 = 0;
  DAT_febec610 = 0;
  DAT_febec686 = 0;
  DAT_febec685 = 0;
  DAT_febec628 = 0;
  DAT_febec684 = 0;
  DAT_febec626 = 0;
  DAT_febec683 = 0;
  DAT_febec624 = 0;
  DAT_febec682 = 0;
  DAT_febec622 = 0;
  DAT_febec681 = 0;
  DAT_febec680 = 0;
  DAT_febec620 = 0;
  uVar3 = 0;
  do {
    iVar1 = uVar3 * 4;
    uVar3 = uVar3 + 1;
    *(undefined4 *)(((undefined *)camry_host_ptr(0xfebec630u)) + iVar1) = uVar2;
  } while (uVar3 < 0x14);
  DAT_febec62a = 0;
  DAT_febec62b = 0;
  DAT_febec62c = 0;
  DAT_febec62d = 0;
  return;
}



void FUN_000c9fa2(void)

{
  ushort uVar1;
  ushort uVar2;
  uint32_t puVar3;
  char cVar4;
  
  puVar3 = 0xfebeb800u;
  cVar4 = DAT_febec680;
  if (DAT_febec680 == '\0') {
    if ((DAT_febec6b0 == '\x01') && ((DAT_febec724 == '\x01' || (DAT_febec725 == '\x01')))) {
      if ((DAT_febec620 < DAT_000b0458) &&
         (uVar1 = DAT_febec620 + 1, uVar2 = DAT_febec620 + 1, DAT_febec620 = uVar1,
         DAT_000b0458 <= uVar2)) {
        DAT_febec680 = DAT_febec6b0;
        cVar4 = DAT_febec6b0;
      }
    }
    else {
      DAT_febec620 = 0;
    }
  }
  else if (DAT_febec6b0 == '\0') {
    DAT_febec620 = 0;
    DAT_febec680 = '\0';
    cVar4 = DAT_febec6b0;
  }
  if (((DAT_febec6ae == '\x01') && (cVar4 == '\x01')) && (DAT_febec62a == '\0')) {
    f33_report_diagnostic_event_failure_ffff_32_bdb64(0x10e);
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(0xe2a))))) = 1;
  }
  return;
}



void FUN_000ca04e(void)

{
  ushort uVar1;
  ushort uVar2;
  uint32_t puVar3;
  puVar3 = 0xfebeb800u;
  if (DAT_000b0468 != '\x01') {
    if ((DAT_febec6b0 == '\x01') &&
       ((((((0 < DAT_febec716 && (DAT_febec71a < 0)) || ((DAT_febec716 < 0 && (0 < DAT_febec71a))))
          || (((0 < DAT_febec716 && (0 < DAT_febec718)) &&
              (DAT_febec708 - DAT_febec70c < 0 !=
               (DAT_febec708 < 0 != DAT_febec70c < 0 &&
               DAT_febec70c < 0 == DAT_febec708 - DAT_febec70c < 0))))) ||
         ((((DAT_febec716 < 0 && (DAT_febec718 < 0)) &&
           (DAT_febec708 - DAT_febec70c < 0 ==
            (DAT_febec708 < 0 != DAT_febec70c < 0 &&
            DAT_febec70c < 0 == DAT_febec708 - DAT_febec70c < 0) && DAT_febec708 != DAT_febec70c))
          || ((((0 < DAT_febec71e && (0 < DAT_febec720)) ||
               ((DAT_febec71e < 0 && (DAT_febec720 < 0)))) ||
              ((0 < DAT_febec710 && (DAT_febec71c < 0)))))))) ||
        ((DAT_febec710 < 0 && (0 < DAT_febec71c)))))) {
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
      f33_report_diagnostic_event_failure_ffff_32_bdb64(0x10f);
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(0xe2b))))) = 1;
    }
  }
  return;
}



short FUN_000ca124(void)

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
  sVar6 = f33_abs_s16_wrapping(DAT_febecc6a);
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
    f33_report_diagnostic_event_failure_ffff_32_bdb64(0x110);
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(0xe2c))))) = 1;
  }
  return sVar6;
}



void FUN_000ca1a8(void)

{
  ushort uVar1;
  ushort uVar2;
  uint32_t puVar3;
  uint uVar4;
  char cVar5;
  
  puVar3 = 0xfebeb800u;
  if (DAT_000b0469 != '\x01') {
    uVar4 = f33_abs_s32_wrapping((int)DAT_febec712 - (int)DAT_febec714);
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
      f33_report_diagnostic_event_failure_ffff_32_bdb64(0x111);
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(0xe2d))))) = 1;
    }
  }
  return;
}



void FUN_000ca242(void)

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
  DAT_febec610 = *(int *)(((undefined *)camry_host_ptr(0xfebec630u)) + (uVar4 - DAT_000b0464 & 0xffff) * 4);
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
      uVar6 = f33_abs_s32_wrapping(value);
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



undefined4 FUN_000ca312(short param_1,short param_2)

{
  uint32_t puVar1;
  undefined4 uVar2;
  
  puVar1 = 0xfebeb800u;
  uVar2 = FUN_000d1da0(0xffc0);
  (*((short *)camry_host_ptr((uint32_t)(puVar1 + 0xe8c)))) = param_2;
  (*((short *)camry_host_ptr((uint32_t)(puVar1 + 0xea8)))) = param_1;
  (*((short *)camry_host_ptr((uint32_t)(puVar1 + 0xe98)))) = -1 - param_1;
  (*((short *)camry_host_ptr((uint32_t)(puVar1 + 0xe96)))) = -1 - param_2;
  FUN_000d1dc6(uVar2);
  return uVar2;
}



void FUN_000ca344(void)

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
  FUN_000ca312((*((volatile uint16_t *)camry_host_ptr(0xb049au))), (*((volatile uint16_t *)camry_host_ptr(0xb048au))));
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



void FUN_000ca3f6(void)

{
  ushort uVar1;
  ushort uVar2;
  uint32_t puVar3;
  ushort uVar4;
  
  puVar3 = 0xfebeb800u;
  uVar4 = f33_abs_s16_wrapping(((int)(int16_t)DAT_febeadf2));
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



/* Single constant publisher: DAT_febec6ae = 1; Shape-classified from the canonical corpus; the
   target cell is not yet named, so the written state's meaning is unknown. */

void FUN_000ca550(void)

{
  DAT_febec6ae = 1;
  return;
}



void FUN_000ca558(void)

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



void FUN_000ca614(void)

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
        f33_report_diagnostic_event_failure_ffff_32_bdb64(0x10d);
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
        FUN_000caaa2();
        FUN_000c9f38();
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



void FUN_000ca716(void)

{
  FUN_000ca550();
  FUN_000ca558();
  FUN_000ca614();
  return;
}



/* WARNING: Removing unreachable block (ram,0x000caace) */

undefined4 FUN_000caaa2(void)

{
  uint32_t puVar1;
  undefined4 uVar2;
  undefined *puVar3;
  
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
  puVar3 = ((void *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xb145cu + (uint32_t)(DAT_febeac3c & 1) * 4u)))))));
  DAT_febec6c8 = 0;
  DAT_febec708 = 0;
  DAT_febec701 = 0;
  DAT_febec6f6 = *(undefined2 *)(puVar3 + 0x16);
  DAT_febec71a = 0;
  DAT_febec71c = 0;
  DAT_febec70c = 0;
  DAT_febec6d4 = *(undefined4 *)(puVar3 + 0x28);
  DAT_febec6f0 = 0;
  DAT_febec6f2 = 0;
  DAT_febec6f4 = 0;
  DAT_febec6f8 = *(undefined2 *)(puVar3 + 4);
  DAT_febec6c0 = 0;
  DAT_febec6fa = *(undefined2 *)(puVar3 + 10);
  DAT_febec6fc = *(undefined2 *)(puVar3 + 0x10);
  DAT_febec6dc = DAT_febec6d8;
  DAT_febec6de = DAT_febec6d8;
  DAT_febec6e0 = DAT_febec6d8;
  DAT_febec710 = DAT_febec6d8;
  uVar2 = FUN_000d1da0(0xffc0);
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
  FUN_000d1dc6(uVar2);
  return uVar2;
}



/* WARNING: Removing unreachable block (ram,0x000cb00e) */
/* WARNING: Removing unreachable block (ram,0x000caf50) */

void FUN_000caebc(void)

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
  sVar4 = f33_abs_s16_wrapping(DAT_febec6d8);
  iVar5 = (int)sVar4;
  sVar4 = f33_abs_s16_wrapping((*((short *)camry_host_ptr((uint32_t)(puVar3 + 0xedc)))));
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
      iVar2 = iVar2 / iVar10;
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
  iVar2 = ((sVar4 + iVar10) * (int)(*((short *)camry_host_ptr((uint32_t)(puVar3 + 0xef6))))) / 0x80;
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
  iVar2 = ((int)DAT_000b04a8 * (int)(*((short *)camry_host_ptr((uint32_t)(puVar3 + 0xf10))))) / 0x80;
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



/* WARNING: Removing unreachable block (ram,0x000cb182) */

void FUN_000cb0fc(void)

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
  
  sVar10 = DAT_febec722;
  cVar7 = DAT_febec702;
  sVar5 = DAT_febec6ec;
  iVar9 = DAT_febec6d0;
  cVar2 = DAT_febeadc2;
  puVar3 = 0xfebeb800u;
  iVar8 = (int)DAT_febec6ec;
  iVar12 = (int)DAT_febec722;
  iVar11 = (int)DAT_febec6ee;
  bVar1 = DAT_febeadc2 != DAT_febec703;
  if (DAT_febeadc2 == '\x02') {
    puVar3 = 0xfebeb800u;
    sVar4 = f33_abs_s16_wrapping(DAT_febec6ec);
    iVar6 = (int)sVar4;
    iVar12 = (int)(*((short *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xb145cu + (uint32_t)((byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0xbc4))))) & 1) * 4u)))) + 0x18))));
    if (iVar6 - iVar12 < 0 == (iVar6 < 0 != iVar12 < 0 && iVar12 < 0 == iVar6 - iVar12 < 0) &&
        iVar6 != iVar12) {
      if (bVar1) {
        sVar5 = f33_abs_s16_wrapping(sVar10);
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
    sVar10 = DAT_febec6ee;
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
        sVar5 = DAT_febec722 + sVar4;
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



void FUN_000cb1e8(void)

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
    *(undefined4 *)(((undefined *)camry_host_ptr(0xfebec744u)) + iVar1) = uVar2;
  } while (uVar3 < 0x14);
  return;
}



void FUN_000cb246(void)

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



void FUN_000cb2a2(void)

{
  bool bVar1;
  bool bVar2;
  bool bVar3;
  uint32_t puVar4;
  byte bVar5;
  byte bVar6;
  
  puVar4 = 0xfebeb800u;
  bVar5 = f33_get_application_grouped_status(0x1a);
  bVar6 = f33_get_application_grouped_status(0x17);
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



void FUN_000cb2f8(void)

{
  ushort uVar1;
  ushort uVar2;
  
  if ((DAT_febec7bf == '\x01') &&
     ((((((0 < DAT_febec80e && (DAT_febec812 < 0)) || ((DAT_febec80e < 0 && (0 < DAT_febec812)))) ||
        (((0 < DAT_febec80e && (0 < DAT_febec810)) &&
         (DAT_febec800 - DAT_febec804 < 0 !=
          (DAT_febec800 < 0 != DAT_febec804 < 0 &&
          DAT_febec804 < 0 == DAT_febec800 - DAT_febec804 < 0))))) ||
       ((((DAT_febec80e < 0 && (DAT_febec810 < 0)) &&
         (DAT_febec800 - DAT_febec804 < 0 ==
          (DAT_febec800 < 0 != DAT_febec804 < 0 &&
          DAT_febec804 < 0 == DAT_febec800 - DAT_febec804 < 0) && DAT_febec800 != DAT_febec804)) ||
        ((((0 < DAT_febec816 && (0 < DAT_febec818)) || ((DAT_febec816 < 0 && (DAT_febec818 < 0))))
         || ((0 < DAT_febec808 && (DAT_febec814 < 0)))))))) ||
      ((DAT_febec808 < 0 && (0 < DAT_febec814)))))) {
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



short FUN_000cb396(void)

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
  sVar6 = f33_abs_s16_wrapping(DAT_febecc6c);
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



uint FUN_000cb3f4(void)

{
  ushort uVar1;
  ushort uVar2;
  uint32_t puVar3;
  uint uVar4;
  
  puVar3 = 0xfebeb800u;
  uVar4 = f33_abs_s32_wrapping((int)DAT_febec80a - (int)DAT_febec80c);
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



void FUN_000cb45e(void)

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
  DAT_febec728 = *(int *)(((undefined *)camry_host_ptr(0xfebec744u)) + (uVar4 - DAT_000b04bc & 0xffff) * 4);
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
      uVar6 = f33_abs_s32_wrapping(value);
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



undefined4 FUN_000cb516(short param_1,short param_2)

{
  uint32_t puVar1;
  undefined4 uVar2;
  
  puVar1 = 0xfebeb800u;
  uVar2 = FUN_000d1da0(0xffc0);
  (*((short *)camry_host_ptr((uint32_t)(puVar1 + 4000)))) = param_2;
  (*((short *)camry_host_ptr((uint32_t)(puVar1 + 0xfbc)))) = param_1;
  (*((short *)camry_host_ptr((uint32_t)(puVar1 + 0xfac)))) = -1 - param_1;
  (*((short *)camry_host_ptr((uint32_t)(puVar1 + 0xfaa)))) = -1 - param_2;
  FUN_000d1dc6(uVar2);
  return uVar2;
}



void FUN_000cb548(void)

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
  FUN_000cb516((*((volatile uint16_t *)camry_host_ptr(0xb04d4u))), (*((volatile uint16_t *)camry_host_ptr(0xb04c4u))));
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



void FUN_000cb5e4(void)

{
  ushort uVar1;
  uint32_t puVar2;
  ushort uVar3;
  ushort *puVar4;
  
  puVar2 = 0xfebeb800u;
  uVar3 = f33_abs_s16_wrapping(((int)(int16_t)DAT_febeadf2));
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



void FUN_000cb664(void)

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



void FUN_000cb73a(void)

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
      FUN_000cba80();
      FUN_000cb1e8();
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



void FUN_000cb81c(void)

{
  FUN_000cb664();
  FUN_000cb73a();
  return;
}



uint FUN_000cb9ae(void)

{
  uint uVar1;
  
  uVar1 = (uint)DAT_febec7bc;
  if (DAT_febec7ac + uVar1 != 0xffff) {
    uVar1 = (uint)DAT_000b04d4;
  }
  return uVar1;
}



uint FUN_000cb9c8(void)

{
  uint uVar1;
  
  uVar1 = (uint)DAT_febec7a0;
  if (DAT_febec7aa + uVar1 != 0xffff) {
    uVar1 = (uint)DAT_000b04c4;
  }
  return uVar1;
}



/* WARNING: Removing unreachable block (ram,0x000cbaac) */

undefined4 FUN_000cba80(void)

{
  uint32_t puVar1;
  undefined4 uVar2;
  undefined *puVar3;
  
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
  puVar3 = ((void *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xb1464u + (uint32_t)(DAT_febeac3c & 1) * 4u)))))));
  DAT_febec7d0 = 0;
  DAT_febec800 = 0;
  DAT_febec7ff = 0;
  DAT_febec7f4 = *(undefined2 *)(puVar3 + 0x14);
  DAT_febec812 = 0;
  DAT_febec814 = 0;
  DAT_febec804 = 0;
  DAT_febec7d8 = *(undefined4 *)(puVar3 + 0x18);
  DAT_febec7f0 = 0;
  DAT_febec7f2 = 0;
  DAT_febec7c8 = 0;
  DAT_febec7f6 = *(undefined2 *)(puVar3 + 8);
  DAT_febec7f8 = *(undefined2 *)(puVar3 + 0xc);
  DAT_febec7fa = *(undefined2 *)(puVar3 + 0x10);
  DAT_febec7e0 = DAT_febec7dc;
  DAT_febec7e2 = DAT_febec7dc;
  DAT_febec7e4 = DAT_febec7dc;
  DAT_febec808 = DAT_febec7dc;
  uVar2 = FUN_000d1da0(0xffc0);
  (*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + 0xfc4)))) = 0;
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + 0xfea)))) = 0;
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + 0x1016)))) = 0;
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + 0x1018)))) = 0;
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + 0x101a)))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0xffe))))) = 0;
  FUN_000d1dc6(uVar2);
  return uVar2;
}



/* WARNING: Removing unreachable block (ram,0x000cbbce) */
/* WARNING: Removing unreachable block (ram,0x000cbb88) */

void FUN_000cbb66(void)

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



void FUN_000cbc80(void)

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



/* WARNING: Removing unreachable block (ram,0x000cbcd0) */

void FUN_000cbcb8(void)

{
  int iVar1;
  int iVar2;
  uint uVar3;
  
  uVar3 = (uint)(DAT_febeae38 >> 6);
  if (uVar3 != 0) {
    iVar2 = (DAT_febec7c4 / 0x100) * 0xe1;
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
      DAT_febeaf20 != 0x7fff) {
    iVar2 = 0x7fff;
  }
  else {
    iVar2 = DAT_febeaf20;
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



void FUN_000cbd64(void)

{
  undefined *puVar1;
  
  if (DAT_febeae02 < DAT_000b04d6) {
    if (DAT_febec7f0 <= DAT_000b04d8) {
      DAT_febec7f0 = DAT_febec7f0 + 1;
    }
    if (DAT_000b04d8 < DAT_febec7f0) {
      puVar1 = ((void *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xb1464u + (uint32_t)(DAT_febeac3c & 1) * 4u)))))));
      DAT_febec7f4 = *(undefined2 *)(puVar1 + 0x14);
      DAT_febec7d8 = *(undefined4 *)(puVar1 + 0x18);
      DAT_febec7f6 = *(undefined2 *)(puVar1 + 8);
      DAT_febec7f8 = *(undefined2 *)(puVar1 + 0xc);
      DAT_febec7fa = *(undefined2 *)(puVar1 + 0x10);
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
      puVar1 = ((void *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xb1464u + (uint32_t)(DAT_febeac3c & 1) * 4u)))))));
      DAT_febec7f4 = *(undefined2 *)(puVar1 + 0x16);
      DAT_febec7d8 = *(undefined4 *)(puVar1 + 0x1c);
      DAT_febec7f6 = *(undefined2 *)(puVar1 + 10);
      DAT_febec7f8 = *(undefined2 *)(puVar1 + 0xe);
      DAT_febec7fa = *(undefined2 *)(puVar1 + 0x12);
      return;
    }
  }
  return;
}



/* WARNING: Removing unreachable block (ram,0x000cbf7a) */
/* WARNING: Removing unreachable block (ram,0x000cbebc) */

void FUN_000cbe28(void)

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
  sVar4 = f33_abs_s16_wrapping(DAT_febec7dc);
  iVar5 = (int)sVar4;
  sVar4 = f33_abs_s16_wrapping((*((short *)camry_host_ptr((uint32_t)(puVar3 + 0xfe0)))));
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
      iVar2 = iVar2 / iVar10;
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
  iVar2 = ((sVar4 + iVar10) * (int)(*((short *)camry_host_ptr((uint32_t)(puVar3 + 0xff4))))) / 0x80;
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
  iVar2 = ((int)DAT_000b04de * (int)(*((short *)camry_host_ptr((uint32_t)(puVar3 + 0x1008))))) / 0x80;
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



/* WARNING: Removing unreachable block (ram,0x000cbfdc) */
/* WARNING: Removing unreachable block (ram,0x000cbfb0) */

void FUN_000cbf9e(void)

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
  iVar3 = -((int)((int)(int16_t)DAT_febec7fa) * (int)DAT_febec816) / 0x40;
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


