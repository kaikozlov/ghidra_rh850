#include "common.h"


/* Constant-block fill: 16 literal assignments into one contiguous cell block; shape-verified.
   Literals are default/reset values; cell meanings are not recovered. */

void f33_fill_constant_block_cc038(void)

{
  DAT_febec81e = 0;
  DAT_febec820 = 0;
  DAT_febec822 = 0;
  DAT_febec824 = 0;
  DAT_febec82e = 0;
  DAT_febec834 = 0;
  DAT_febec826 = 0;
  DAT_febec835 = 0;
  DAT_febec82f = 0;
  DAT_febec828 = 0;
  DAT_febec82a = 0;
  DAT_febec82c = 0;
  DAT_febec830 = 0;
  DAT_febec831 = 0;
  DAT_febec832 = 0;
  DAT_febec833 = 0;
  return;
}



int FUN_000cc07a(void)

{
  byte bVar1;
  short sVar2;
  short sVar3;
  uint32_t puVar4;
  short sVar5;
  int iVar6;
  short sVar7;
  int iVar8;
  uint uVar9;
  
  sVar2 = DAT_febeae20;
  bVar1 = DAT_febeacfe;
  puVar4 = 0xfebeb800u;
  iVar8 = (int)DAT_febeae20;
  uVar9 = (uint)DAT_febeacfe;
  f33_abs_s16_wrapping(DAT_febeae20);
  f33_abs_s32_wrapping(camry_host_addr(((undefined *)camry_host_ptr((uint32_t)(iVar8 - (*((short *)camry_host_ptr((uint32_t)(puVar4 + 0x1024)))))))));
  f33_abs_s16_wrapping((*((short *)camry_host_ptr((uint32_t)(puVar4 + -0x9de)))));
  sVar5 = f33_abs_s16_wrapping((*((short *)camry_host_ptr((uint32_t)(puVar4 + -0x9dc)))));
  sVar3 = (*((short *)camry_host_ptr((uint32_t)(puVar4 + 0x101e))));
  iVar8 = (int)sVar3;
  sVar3 = (ushort)bVar1 - sVar3;
  if ((int)(uVar9 - iVar8) < 0 != (iVar8 < 0 && iVar8 < 0 == (int)(uVar9 - iVar8) < 0)) {
    sVar3 = sVar3 + 0x40;
  }
  (*((ushort *)camry_host_ptr((uint32_t)(puVar4 + 0x101e)))) = (ushort)bVar1;
  iVar8 = (int)sVar3;
  (*((short *)camry_host_ptr((uint32_t)(puVar4 + 0x1020)))) = sVar3;
  sVar7 = DAT_000b04f0;
  if (iVar8 + -1 < 0 == (iVar8 < 0 && -1 < iVar8 + -1) && iVar8 != 1) {
    iVar6 = (int)DAT_000b04f8;
    if (iVar8 - iVar6 < 0 == (iVar8 < 0 != iVar6 < 0 && iVar6 < 0 == iVar8 - iVar6 < 0)) {
      sVar7 = DAT_000b04f8;
      sVar3 = DAT_000b04f0;
    }
    sVar7 = sVar7 * sVar3;
  }
  (*((short *)camry_host_ptr((uint32_t)(puVar4 + 0x1022)))) = sVar7;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(0x102e))))) = 0;
  (*((short *)camry_host_ptr((uint32_t)(puVar4 + 0x1024)))) = sVar2;
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar4 + 0x1028)))) = 0;
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar4 + 0x102a)))) = 0;
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar4 + 0x102c)))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(0x1030))))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(0x1031))))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(0x1032))))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(0x1033))))) = 0;
  return (int)sVar5;
}



int FUN_000cc114(void)

{
  uint32_t puVar1;
  short sVar2;
  
  puVar1 = 0xfebeb800u;
  sVar2 = f33_abs_s16_wrapping(DAT_febeae24);
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + 0x1026)))) = 0;
  return (int)sVar2;
}



void FUN_000cc130(void)

{
  DAT_febec835 = DAT_febec82e == '\x01' || DAT_febec834 == '\x01';
  return;
}



/* Constant-block fill: 25 literal assignments into one contiguous cell block; shape-verified.
   Literals are default/reset values; cell meanings are not recovered. */

void f33_fill_constant_block_cc148(void)

{
  DAT_febec860 = 0;
  DAT_febec846 = 0x100;
  DAT_febec848 = 0x100;
  DAT_febec861 = 0;
  DAT_febec858 = 0;
  DAT_febec862 = 0;
  DAT_febec859 = 0;
  DAT_febec863 = 0;
  DAT_febec844 = 0;
  DAT_febec85a = 0;
  DAT_febec85b = 0;
  DAT_febec84a = 0;
  DAT_febec838 = 0;
  DAT_febec84c = 0;
  DAT_febec85e = 0;
  DAT_febec864 = 0;
  DAT_febec84e = 0;
  DAT_febec850 = 0;
  DAT_febec852 = 0x400;
  DAT_febec854 = 0;
  DAT_febec83c = 0;
  DAT_febec856 = 0;
  DAT_febec85c = 0;
  DAT_febec865 = 0;
  DAT_febec840 = 0;
  return;
}



void FUN_000cc1b6(void)

{
  bool bVar1;
  ushort uVar2;
  ushort uVar3;
  int iVar4;
  int iVar5;
  int iVar6;
  int iVar7;
  
  iVar6 = (int)((int)(int16_t)DAT_febeae1e);
  iVar4 = (int)DAT_000b0506;
  iVar7 = (int)((int)(int16_t)DAT_febeae1c);
  iVar5 = (int)((int)(int16_t)DAT_febeae26);
  if ((DAT_000b0516 == '\x01') || (DAT_febeacf9 != 'Z')) {
    DAT_febec860 = 0;
    bVar1 = false;
    DAT_febec858 = '\0';
  }
  else {
    bVar1 = true;
    DAT_febec860 = 1;
  }
  if (DAT_febeacfd == 0) {
    if ((DAT_febec84e <= DAT_000b0514) &&
       (uVar3 = DAT_febec84e + 1, uVar2 = DAT_febec84e + 1, DAT_febec84e = uVar3,
       DAT_000b0514 < uVar2)) {
      DAT_febec861 = '\0';
    }
  }
  else {
    DAT_febec84e = 0;
    if ((DAT_febeacfd >> 1 & 1) != 0) {
      DAT_febec861 = '\x01';
    }
  }
  if (((((DAT_febec858 == '\0') && (bVar1)) && (DAT_febec865 == '\x01')) &&
      (((DAT_febec861 == '\0' &&
        (iVar5 - iVar4 < 0 == (iVar5 < 0 != iVar4 < 0 && iVar4 < 0 == iVar5 - iVar4 < 0))) &&
       ((DAT_febeacbd == '\0' && ((DAT_febeacfd == 0 && (DAT_febec835 == '\0')))))))) &&
     (((0x5699 < DAT_febeae18 &&
       ((0x5699 < DAT_febeae1a && (iVar7 + -0x569a < 0 == (iVar7 < 0 && -1 < iVar7 + -0x569a))))) &&
      (((iVar6 + -0x569a < 0 == (iVar6 < 0 && -1 < iVar6 + -0x569a) || (DAT_febeacfc != '\x01')) &&
       (DAT_febeacfa == '\0')))))) {
    DAT_febec858 = DAT_febec865;
  }
  if ((DAT_febec858 == '\x01') &&
     ((((((DAT_febec865 == '\0' ||
          (iVar5 - iVar4 < 0 != (iVar5 < 0 != iVar4 < 0 && iVar4 < 0 == iVar5 - iVar4 < 0))) ||
         (DAT_febeacbd != '\0')) ||
        (((DAT_febeacfd != 0 || (DAT_febec835 == '\x01')) ||
         ((DAT_febeae18 < 0x569a ||
          ((DAT_febeae1a < 0x569a || (iVar7 + -0x569a < 0 != (iVar7 < 0 && -1 < iVar7 + -0x569a)))))
         )))) || ((iVar6 + -0x569a < 0 != (iVar6 < 0 && -1 < iVar6 + -0x569a) &&
                  (DAT_febeacfc == '\x01')))) || (DAT_febeacfa != '\0')))) {
    DAT_febec858 = '\0';
  }
  if (DAT_febec862 != '\0') {
    DAT_febec862 = '\0';
    if (DAT_febec858 == '\0') {
      DAT_febec863 = '\x01';
      DAT_febec85a = 3;
    }
    else {
      DAT_febec85a = 2;
    }
  }
  if (((DAT_febec863 == '\x01') && (DAT_febec844 <= DAT_000b0508)) &&
     (uVar3 = DAT_febec844 + 1, DAT_febec844 = DAT_febec844 + 1, DAT_000b0508 < uVar3)) {
    DAT_febec863 = '\0';
    DAT_febec844 = 0;
  }
  DAT_febec859 = 0;
  return;
}



void FUN_000cc32a(void)

{
  uint uVar1;
  uint32_t puVar2;
  short sVar3;
  int iVar5;
  int iVar4;
  
  puVar2 = 0xfebeb800u;
  uVar1 = (uint)DAT_febec85a;
  if (((uVar1 != DAT_febec85b) && (uVar1 != 0)) &&
     ((sVar3 = DAT_000b050a, uVar1 == 1 ||
      ((sVar3 = DAT_000b050c, uVar1 < 3 || (sVar3 = DAT_000b050e, uVar1 == 3)))))) {
    DAT_febec838 = (int)sVar3 * (int)DAT_febec846;
    DAT_febec84a = sVar3;
  }
  DAT_febec85b = DAT_febec85a;
  DAT_febec848 = 0x100;
  if (uVar1 - 1 < 3) {
    DAT_febec838 = (DAT_febec838 + 0x100) - (int)DAT_febec846;
    iVar5 = (int)DAT_febec84a;
    iVar4 = DAT_febec838;
    if (iVar5 != 0) {
      if (DAT_febec838 == -0x80000000 && iVar5 == -1) {
        iVar4 = 0;
      }
      else {
        iVar4 = DAT_febec838 / iVar5;
      }
    }
    DAT_febec846 = (short)iVar4;
    sVar3 = f33_abs_s16_wrapping(DAT_febec846 + -0x100);
    iVar4 = (int)sVar3;
    if (iVar4 + -5 < 0 != (iVar4 < 0 && -1 < iVar4 + -5) || iVar4 == 5) {
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(0x105a))))) = 0;
      (*((undefined2 *)camry_host_ptr((uint32_t)(puVar2 + 0x1046)))) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar2 + 0x1048))));
    }
  }
  return;
}



/* WARNING: Removing unreachable block (ram,0x000cc426) */

void FUN_000cc3be(void)

{
  int iVar1;
  uint uVar2;
  undefined **ppuVar3;
  uint32_t puVar4;
  short sVar5;
  int iVar6;
  int iVar7;
  
  puVar4 = 0xfebeb800u;
  uVar2 = (uint)DAT_febec156;
  iVar7 = (int)((int)(int16_t)DAT_febeae20);
  iVar6 = (int)DAT_000b0504;
  DAT_febec850 = DAT_000b0504;
  if ((iVar7 - iVar6 < 0 != (iVar7 < 0 != iVar6 < 0 && iVar6 < 0 == iVar7 - iVar6 < 0) ||
       iVar7 == iVar6) &&
     (iVar1 = -iVar6, DAT_febec850 = ((int)(int16_t)DAT_febeae20),
     iVar7 + iVar6 < 0 != (iVar7 < 0 != iVar1 < 0 && iVar1 < 0 == iVar7 + iVar6 < 0) ||
     iVar7 == iVar1)) {
    DAT_febec850 = (short)iVar1;
  }
  sVar5 = f33_abs_s16_wrapping(((int)(int16_t)DAT_febec850));
  if ((*((short *)camry_host_ptr((uint32_t)(puVar4 + 0x1050)))) < 0) {
    ppuVar3 = &PTR_DAT_000d3c5c;
  }
  else {
    ppuVar3 = &PTR_DAT_000d3c1c;
  }
  iVar6 = FUN_000d07f2(ppuVar3[uVar2 & 3],(int)sVar5);
  (*((short *)camry_host_ptr((uint32_t)(puVar4 + 0x1052)))) = (short)iVar6;
  sVar5 = (short)(((*((short *)camry_host_ptr((uint32_t)(puVar4 + 0x1050)))) * iVar6) / 0x400);
  (*((short *)camry_host_ptr((uint32_t)(puVar4 + 0x1054)))) = sVar5;
  (*((int *)camry_host_ptr((uint32_t)(puVar4 + 0x103c)))) = (int)sVar5 << 5;
  return;
}



/* WARNING: Removing unreachable block (ram,0x000cc4bc) */
/* WARNING: Removing unreachable block (ram,0x000cc454) */

void FUN_000cc43a(void)

{
  bool bVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  int iVar6;
  
  iVar3 = (int)((int)(int16_t)DAT_febec856);
  iVar2 = (DAT_febec83c << 8) / 0x2000;
  iVar6 = 0x7fff;
  if ((iVar2 + -0x7fff < 0 != (iVar2 < 0 && -1 < iVar2 + -0x7fff) || iVar2 == 0x7fff) &&
     (iVar6 = iVar2, iVar2 + 0x7fff < 0 != (-1 < iVar2 && iVar2 + 0x7fff < 0) || iVar2 == -0x7fff))
  {
    iVar6 = -0x7fff;
  }
  iVar4 = (int)DAT_000b0512;
  DAT_febec84c = (short)iVar6;
  iVar2 = iVar6 - iVar3;
  iVar5 = (int)DAT_000b0512;
  if (iVar2 - iVar4 < 0 == (iVar2 < 0 != iVar4 < 0 && iVar4 < 0 == iVar2 - iVar4 < 0) &&
      iVar2 != iVar4) {
    iVar6 = iVar5 + iVar3;
  }
  else if (iVar2 + iVar5 < 0 != (iVar2 < 0 != -iVar5 < 0 && -iVar5 < 0 == iVar2 + iVar5 < 0)) {
    iVar6 = iVar3 - DAT_000b0512;
  }
  if (iVar6 + -0x7fff < 0 == (iVar6 < 0 && -1 < iVar6 + -0x7fff) && iVar6 != 0x7fff) {
    iVar6 = 0x7fff;
  }
  else if (iVar6 + 0x7fff < 0 != (-1 < iVar6 && iVar6 + 0x7fff < 0)) {
    iVar6 = -0x7fff;
  }
  DAT_febec856 = (short)iVar6;
  DAT_febec840 = ((short)iVar6 * 0x100) / 0x100;
  iVar6 = (int)DAT_000b0510;
  if (DAT_febec840 - iVar6 < 0 ==
      (DAT_febec840 < 0 != iVar6 < 0 && iVar6 < 0 == DAT_febec840 - iVar6 < 0) &&
      DAT_febec840 != iVar6) {
    if (DAT_febec85c != '\x02') {
      DAT_febec85c = '\x02';
      DAT_febec864 = 1;
      goto LAB_000cc4f6;
    }
  }
  else {
    iVar6 = DAT_febec840 + DAT_000b0510;
    bVar1 = -(int)DAT_000b0510 < 0;
    if (iVar6 < 0 == (DAT_febec840 < 0 != bVar1 && bVar1 == iVar6 < 0)) {
      DAT_febec85c = '\0';
    }
    else if (DAT_febec85c != '\x01') {
      DAT_febec864 = 1;
      DAT_febec85c = '\x01';
      goto LAB_000cc4f6;
    }
  }
  DAT_febec864 = 0;
LAB_000cc4f6:
  iVar6 = (int)DAT_000b0510;
  DAT_febec85e = DAT_000b0510;
  if (DAT_febec840 - iVar6 < 0 !=
      (DAT_febec840 < 0 != iVar6 < 0 && iVar6 < 0 == DAT_febec840 - iVar6 < 0) ||
      DAT_febec840 == iVar6) {
    iVar2 = -iVar6;
    if (DAT_febec840 + iVar6 < 0 ==
        (DAT_febec840 < 0 != iVar2 < 0 && iVar2 < 0 == DAT_febec840 + iVar6 < 0) &&
        DAT_febec840 != iVar2) {
      DAT_febec85e = (short)DAT_febec840;
    }
    else {
      DAT_febec85e = (short)iVar2;
    }
  }
  return;
}



void FUN_000cc514(void)

{
  DAT_febec865 = DAT_febeacbe == '\x01' && (DAT_febeadfc & 0x1ff) == 0;
  return;
}

void FUN_000cc530(void)

{
  DAT_febec88e = 0;
  DAT_febec88f = 0;
  DAT_febec868 = 0;
  DAT_febec890 = 0;
  DAT_febec891 = 0;
  DAT_febec874 = 0;
  DAT_febec892 = 0;
  DAT_febec876 = 0;
  DAT_febec878 = 0;
  DAT_febec87a = 0;
  DAT_febec87c = 0;
  DAT_febec88c = (*((volatile uint8_t *)camry_host_ptr((uint32_t)((f33_calibration_bank_bases[DAT_febeac3c & 1]) + (uint32_t)(0x228c)))));
  DAT_febec88d = (*((volatile uint8_t *)camry_host_ptr((uint32_t)((f33_calibration_bank_bases[DAT_febeac3c & 1]) + (uint32_t)(0x228d)))));
  DAT_febec87e = 0;
  DAT_febec880 = 0;
  DAT_febec86c = 0;
  DAT_febec882 = 0;
  DAT_febec886 = 0;
  return;
}




/* Constant-block fill: 5 literal assignments into one contiguous cell block; shape-verified.
   Literals are default/reset values; cell meanings are not recovered. */

void f33_fill_constant_block_cc596(void)

{
  DAT_febec884 = 0;
  DAT_febec888 = 0;
  DAT_febec870 = 0;
  DAT_febec88a = 0;
  DAT_febec894 = 0;
  return;
}



undefined4 FUN_000cc5ac(void)

{
  uint32_t puVar1;
  undefined4 uVar2;
  
  puVar1 = 0xfebeb800u;
  uVar2 = FUN_000d1da0(0xffc0);
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x108e))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x8d0)))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x108f))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x88f)))));
  (*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + 0x1068)))) = (*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + 0x8cc))));
  FUN_000d1dc6(uVar2);
  return uVar2;
}



void FUN_000cc5da(void)

{
  if ((DAT_febec892 == '\0') && (DAT_febec890 != '\x03')) {
    if (((DAT_febeacbe == '\x01') && (DAT_febeacbd == '\0')) &&
       ((((DAT_febeace5 == '\0' && ((DAT_febeaf0c == 0x55aaaa55 && (DAT_febec88c == '\x01')))) ||
         ((DAT_febeace6 == '\0' && ((DAT_febeaf0c == -0x55aaaa56 && (DAT_febec88d == '\x01')))))) &&
        (((DAT_febead41 == '\0' && (DAT_febec88f == 'Z')) &&
         (((DAT_febec88e == '\x11' || (DAT_febec88e == '\"')) && ((DAT_febeadfc & 0x1ff) == 0)))))))
       ) {
      DAT_febec890 = 1;
    }
    else {
      DAT_febec890 = 2;
    }
  }
  else {
    DAT_febec890 = 3;
  }
  return;
}



void FUN_000cc66e(void)

{
  ushort input;
  uint32_t puVar1;
  int iVar2;
  int iVar3;
  
  input = DAT_febeadf6;
  puVar1 = 0xfebeb800u;
  iVar2 = f33_interpolate_unsigned_axis_sentinel_curve
                    (((ushort *)camry_host_ptr((uint32_t)(f33_calibration_bank_bases[DAT_febeac3c & 1] + 0x22f0))),DAT_febeadf6)
  ;
  iVar3 = f33_interpolate_unsigned_axis_sentinel_curve
                    (((ushort *)camry_host_ptr((uint32_t)(f33_calibration_bank_bases[(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0xbc4))))) & 1] + 0x2348))),input
                    );
  (*((short *)camry_host_ptr((uint32_t)(puVar1 + 0x107c)))) = (short)iVar2;
  (*((short *)camry_host_ptr((uint32_t)(puVar1 + 0x1086)))) = (short)iVar3;
  return;
}



void FUN_000cc878(void)

{
  uint32_t puVar1;
  short sVar2;
  int iVar4;
  undefined1 uVar5;
  ushort uVar6;
  int iVar3;
  
  uVar5 = DAT_febec892;
  uVar6 = DAT_febec874;
  puVar1 = 0xfebeb800u;
  if (DAT_febec890 != '\x03') {
    puVar1 = 0xfebeb800u;
    sVar2 = f33_abs_s16_wrapping(DAT_febec882 + DAT_febec88a);
    iVar3 = (int)sVar2;
    iVar4 = (int)(*((short *)camry_host_ptr((uint32_t)(f33_calibration_bank_bases[(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0xbc4))))) & 1] + 0x2286))));
    if (iVar3 - iVar4 < 0 == (iVar3 < 0 != iVar4 < 0 && iVar4 < 0 == iVar3 - iVar4 < 0) &&
        iVar3 != iVar4) {
      if (uVar6 < (*((ushort *)camry_host_ptr((uint32_t)(0x2284u + (int)f33_calibration_bank_bases[(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0xbc4))))) & 1]))))) {
        uVar6 = uVar6 + 1;
      }
      else {
        uVar5 = 1;
      }
      goto LAB_000cc8ca;
    }
  }
  uVar6 = 0;
LAB_000cc8ca:
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x1092))))) = uVar5;
  (*((ushort *)camry_host_ptr((uint32_t)(puVar1 + 0x1074)))) = uVar6;
  return;
}



/* WARNING: Removing unreachable block (ram,0x000cc95e) */
/* WARNING: Removing unreachable block (ram,0x000cc956) */

void FUN_000cc8d6(void)

{
  short sVar1;
  uint32_t puVar2;
  short sVar3;
  short sVar4;
  int iVar5;
  int iVar6;
  int iVar7;
  
  sVar1 = DAT_febec172;
  sVar4 = DAT_febeac44;
  puVar2 = 0xfebeb800u;
  if (DAT_febec891 == '\x01') {
    iVar7 = (int)DAT_febec886;
    puVar2 = 0xfebeb800u;
    sVar3 = f33_abs_s16_wrapping(DAT_febec172);
    sVar4 = f33_abs_s16_wrapping(sVar4);
    iVar5 = f33_interpolate_signed_sentinel_curve
                      (((short *)camry_host_ptr((uint32_t)(f33_calibration_bank_bases[(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0xbc4))))) & 1] + 0x2314))),
                       sVar3);
    sVar3 = (short)iVar5;
    if (sVar1 < 0) {
      sVar3 = -sVar3;
    }
    (*((short *)camry_host_ptr((uint32_t)(puVar2 + 0x1084)))) = sVar3;
    iVar5 = f33_interpolate_signed_sentinel_curve
                      (((short *)camry_host_ptr((uint32_t)(f33_calibration_bank_bases[(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0xbc4))))) & 1] + 0x2330))),
                       sVar4);
    iVar6 = (int)DAT_000b04ea;
    (*((short *)camry_host_ptr((uint32_t)(puVar2 + 0x1088)))) = (short)iVar5;
    sVar4 = DAT_000b04e8;
    iVar5 = ((((int)(short)iVar5 * (int)sVar3) / 0x400) * iVar7) / 0x400;
    iVar7 = (int)DAT_000b04e8;
    (*((int *)camry_host_ptr((uint32_t)(puVar2 + 0x1070)))) = iVar5;
    if (iVar5 - iVar7 < 0 != (iVar5 < 0 != iVar7 < 0 && iVar7 < 0 == iVar5 - iVar7 < 0) ||
        iVar5 == iVar7) {
      if (iVar5 - iVar6 < 0 == (iVar5 < 0 != iVar6 < 0 && iVar6 < 0 == iVar5 - iVar6 < 0) &&
          iVar5 != iVar6) {
        iVar6 = iVar5;
      }
      sVar4 = (short)iVar6;
    }
  }
  else {
    sVar4 = 0;
  }
  (*((short *)camry_host_ptr((uint32_t)(puVar2 + 0x108a)))) = sVar4;
  return;
}



void FUN_000cc984(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  
  iVar3 = (int)DAT_000b04ee;
  iVar1 = (int)((int)(int16_t)DAT_febec88a) + (int)((int)(int16_t)DAT_febec882);
  iVar2 = (int)-DAT_000b04ee;
  DAT_febec894 = DAT_000b04ee;
  if ((iVar1 - iVar3 < 0 != (iVar1 < 0 != iVar3 < 0 && iVar3 < 0 == iVar1 - iVar3 < 0) ||
       iVar1 == iVar3) &&
     (DAT_febec894 = -DAT_000b04ee,
     iVar1 - iVar2 < 0 == (iVar1 < 0 != iVar2 < 0 && iVar2 < 0 == iVar1 - iVar2 < 0) &&
     iVar1 != iVar2)) {
    DAT_febec894 = (short)iVar1;
  }
  return;
}



void FUN_000cc9ac(void)

{
  DAT_febeca96 = 0;
  DAT_febec898 = 0;
  DAT_febec9f4 = 0;
  DAT_febec9e8 = DAT_000b05b0;
  DAT_febec9f6 = 0;
  DAT_febec9f8 = 0;
  DAT_febec89c = 0;
  DAT_febec9ea = DAT_000b05b0;
  DAT_febec9ec = 1;
  DAT_febec9ee = 1;
  DAT_febec9f0 = 1;
  DAT_febec9f2 = 1;
  DAT_febec8a0 = 0;
  DAT_febeca10 = 0x100;
  DAT_febeca3a = 0x100;
  DAT_febeca9d = 1;
  DAT_febec9b8 = 0;
  DAT_febeca2c = 0x400;
  DAT_febeca9f = 7;
  DAT_febec9e4 = 0;
  DAT_febeca56 = 0x4000;
  DAT_febeca58 = 0x4000;
  DAT_febec8a4 = 0;
  DAT_febec9fa = 0;
  DAT_febec9fc = 0;
  DAT_febecaa4 = 0;
  DAT_febec8a8 = 0;
  DAT_febec8ac = 0;
  DAT_febeca97 = 0;
  DAT_febec8b0 = 0;
  DAT_febec8b4 = 0;
  DAT_febec99c = 0;
  DAT_febec9c8 = 0;
  DAT_febec8b8 = 0;
  DAT_febec9a0 = 0;
  DAT_febec9cc = 0;
  DAT_febec9fe = 0;
  DAT_febeca00 = 0;
  DAT_febeca0a = 0;
  DAT_febeca02 = 0;
  DAT_febeca0c = 0;
  DAT_febeca36 = 0;
  DAT_febeca82 = 0;
  DAT_febeca90 = 0;
  DAT_febeca0e = 0;
  DAT_febec92c = 0;
  DAT_febec8d4 = 0;
  DAT_febec8d8 = 0;
  DAT_febec8dc = 0;
  DAT_febec8e0 = 0;
  DAT_febec8e4 = 0;
  DAT_febec8e8 = 0;
  DAT_febeca12 = 0;
  DAT_febeca84 = 0;
  DAT_febeca92 = 0;
  DAT_febeca14 = 0;
  DAT_febeca32 = 0;
  DAT_febec90c = 0;
  DAT_febec910 = 0;
  DAT_febec9a8 = 0;
  DAT_febec9d4 = 0;
  DAT_febec914 = 0;
  DAT_febeca16 = 0;
  DAT_febeca04 = 0;
  DAT_febeca06 = 0;
  DAT_febeca18 = 0;
  DAT_febeca1a = 0;
  DAT_febeca30 = 0;
  DAT_febeca1c = 0;
  DAT_febeca1e = 0;
  DAT_febeca86 = 0;
  DAT_febeca94 = 0;
  DAT_febeca08 = 0;
  DAT_febec8ec = 0;
  DAT_febec8f0 = 0;
  DAT_febec9ac = 0;
  DAT_febec9d8 = 0;
  DAT_febec8f4 = 0;
  DAT_febec8f8 = 0;
  DAT_febec920 = 0;
  DAT_febec918 = 0;
  DAT_febec91c = 0;
  DAT_febec924 = 0;
  DAT_febec9b0 = 0;
  DAT_febec9dc = 0;
  DAT_febec8bc = 0;
  DAT_febec9a4 = 0;
  DAT_febec9d0 = 0;
  DAT_febec8c0 = 0;
  DAT_febec8fc = 0;
  DAT_febec9b4 = 0;
  DAT_febec9e0 = 0;
  DAT_febec8c4 = 0;
  DAT_febec8c8 = 0;
  DAT_febec900 = 0;
  DAT_febec990 = 0;
  DAT_febec9bc = 0;
  DAT_febec8cc = 0;
  DAT_febec8d0 = 0;
  DAT_febeca20 = 0;
  DAT_febeca22 = 0;
  DAT_febeca24 = 0;
  DAT_febeca26 = 0;
  DAT_febeca28 = 0;
  DAT_febeca2a = 0;
  DAT_febec904 = 0;
  DAT_febec908 = 0;
  DAT_febec930 = 0;
  DAT_febeca38 = 0;
  DAT_febeca3c = 0;
  DAT_febec928 = 0;
  DAT_febeca3e = 0;
  DAT_febeca7a = 0;
  DAT_febeca88 = 0;
  DAT_febeca34 = 0;
  DAT_febec934 = 0;
  DAT_febec994 = 0;
  DAT_febec9c0 = 0;
  DAT_febeca46 = 0;
  DAT_febeca7c = 0;
  DAT_febeca8a = 0;
  DAT_febeca44 = 0;
  DAT_febeca42 = 0;
  DAT_febec938 = 0;
  DAT_febec93c = 0;
  DAT_febeca40 = 0;
  DAT_febeca7e = 0;
  DAT_febeca8c = 0;
  DAT_febec940 = 0;
  DAT_febec998 = 0;
  DAT_febec9c4 = 0;
  DAT_febeca98 = 0;
  DAT_febeca99 = 0;
  DAT_febeca9a = 0;
  DAT_febeca9c = 0;
  DAT_febeca9e = 0;
  DAT_febeca9b = 0;
  DAT_febecaac = 0;
  DAT_febecaad = 0;
  DAT_febec944 = 0;
  DAT_febec948 = 0;
  DAT_febeca2e = 0;
  DAT_febeca80 = 0;
  DAT_febeca8e = 0;
  f33_angle_controller_target_triplicate[0] = 0;
  f33_angle_controller_target_triplicate[1] = 0;
  f33_angle_controller_target_triplicate[2] = 0;
  DAT_febeca48 = 0;
  DAT_febec94c = 0;
  DAT_febeca4a = 0;
  DAT_febec950 = 0;
  DAT_febec954 = 0;
  DAT_febec958 = 0;
  DAT_febec95c = 0;
  DAT_febec960 = 0;
  DAT_febeca4c = 0;
  DAT_febeca4e = 0;
  DAT_febeca50 = 0;
  DAT_febeca52 = 0;
  DAT_febeca54 = 0;
  DAT_febeca5a = 0;
  DAT_febeca5c = 0;
  DAT_febeca5e = 0;
  DAT_febeca60 = 0;
  DAT_febeca62 = 0;
  DAT_febeca64 = 0x400;
  DAT_febecaa0 = 0;
  DAT_febeca66 = 0;
  DAT_febeca68 = 0;
  DAT_febec964 = 0;
  DAT_febec968 = 0;
  DAT_febecaa1 = 0;
  DAT_febec96c = 0;
  DAT_febec970 = 0;
  DAT_febeca6a = 0;
  DAT_febeca6c = 0;
  DAT_febeca6e = 0;
  DAT_febeca70 = 0;
  DAT_febecaa2 = 0;
  DAT_febec974 = 0;
  DAT_febec978 = 0;
  DAT_febec97c = 0;
  DAT_febeca72 = 0;
  DAT_febeca74 = 0;
  DAT_febeca76 = 0;
  DAT_febeca78 = 0;
  DAT_febec980 = 0;
  DAT_febec984 = 0;
  DAT_febec988 = 0;
  DAT_febec98c = 0;
  return;
}



void FUN_000cccc6(void)

{
  int iVar1;
  short sVar2;
  
  iVar1 = (int)(short)((DAT_febecb00 & 7) + (DAT_febeac3c & 1) * 8);
  DAT_febec9ee = (*((short *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd3cb0u + (uint32_t)(iVar1 * 0x57) * 4u)))))));
  DAT_febec9f0 = (*((short *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd3cb4u + (uint32_t)(iVar1 * 0x57) * 4u)))))));
  DAT_febec9f2 = (*((short *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd3cb8u + (uint32_t)(iVar1 * 0x57) * 4u)))))));
  DAT_febec9f4 = (*((undefined2 *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd3cacu + (uint32_t)(iVar1 * 0x57) * 4u)))))));
  if ((DAT_febecab5 != DAT_febeca96) &&
     (((sVar2 = (*((short *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd3cb0u + (uint32_t)(iVar1 * 0x57) * 4u))))))), DAT_febecab5 == '\x11' ||
       (sVar2 = (*((short *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd3cb4u + (uint32_t)(iVar1 * 0x57) * 4u))))))), DAT_febecab5 == '\"')) ||
      (sVar2 = (*((short *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd3cb8u + (uint32_t)(iVar1 * 0x57) * 4u))))))), DAT_febecab5 == 'D')))) {
    DAT_febec9ec = sVar2;
    DAT_febec898 = (int)DAT_febec9ec * (int)DAT_febec9e8;
  }
  DAT_febeca96 = DAT_febecab5;
  return;
}



void FUN_000ccd50(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  
  iVar3 = (int)DAT_000b05b2;
  iVar4 = (int)DAT_000b05b0;
  iVar2 = (int)DAT_febec9ec;
  iVar5 = iVar4;
  if (DAT_febecab7 == '\x01') {
    iVar5 = iVar3;
  }
  if (((DAT_febecab5 == '\x11') || (DAT_febecab5 == '\"')) || (DAT_febecab5 == 'D')) {
    DAT_febec898 = (DAT_febec898 + iVar5) - (int)DAT_febec9e8;
    iVar1 = DAT_febec898;
    if (iVar2 != 0) {
      if (DAT_febec898 == -0x80000000 && iVar2 == -1) {
        iVar1 = -0x80000000;
      }
      else {
        iVar1 = DAT_febec898 / iVar2;
      }
    }
    if (((iVar5 != iVar3) ||
        (iVar2 = iVar3 - DAT_febec9f4,
        iVar1 - iVar2 < 0 != (iVar1 < 0 != iVar2 < 0 && iVar2 < 0 == iVar1 - iVar2 < 0))) &&
       ((iVar3 = iVar1, iVar5 == iVar4 &&
        (iVar2 = DAT_febec9f4 + iVar4, iVar3 = iVar4,
        iVar1 - iVar2 < 0 == (iVar1 < 0 != iVar2 < 0 && iVar2 < 0 == iVar1 - iVar2 < 0) &&
        iVar1 != iVar2)))) {
      iVar3 = iVar1;
    }
    DAT_febec9e8 = (short)iVar3;
  }
  DAT_febec9ea = (short)iVar5;
  return;
}



void FUN_000ccdc4(void)

{
  int iVar1;
  
  iVar1 = (int)(short)((DAT_febecb00 & 7) + (DAT_febeac3c & 1) * 8);
  DAT_febec9f6 = (*((undefined2 *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd3cbcu + (uint32_t)(iVar1 * 0x57) * 4u)))))));
  DAT_febec9f8 = (*((undefined2 *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd3cc0u + (uint32_t)(iVar1 * 0x57) * 4u)))))));
  return;
}



/* WARNING: Removing unreachable block (ram,0x000cce7c) */

void FUN_000ccdf8(void)

{
  int iVar1;
  uint uVar2;
  int iVar3;
  uint uVar4;
  int iVar5;
  
  if (((DAT_febec8a0 == DAT_febec9b8) || (DAT_febec8a0 == DAT_febec9e4)) ||
     (DAT_febec9b8 != DAT_febec9e4)) {
    DAT_febec9b8 = DAT_febec8a0;
  }
  iVar3 = (int)((int)(int16_t)DAT_febeca2e);
  DAT_febec8a0 = (int)((int)(int16_t)DAT_febeca80);
  if (((iVar3 == DAT_febec8a0) || (iVar3 == ((int)(int16_t)DAT_febeca8e))) || (DAT_febec8a0 != ((int)(int16_t)DAT_febeca8e))) {
    DAT_febec8a0 = iVar3;
  }
  uVar4 = (uint)DAT_febec9f6;
  iVar3 = (int)DAT_000b05b2;
  uVar2 = (uint)DAT_febec9f8;
  DAT_febec89c = DAT_febec8a0 - DAT_febec9b8;
  iVar1 = (int)DAT_000b05b0;
  if ((int)(DAT_febec89c - uVar4) < 0 == ((int)DAT_febec89c < 0 && -1 < (int)(DAT_febec89c - uVar4))
      && DAT_febec89c != uVar4) {
    DAT_febec8a0 = uVar4 + DAT_febec9b8;
  }
  else if ((int)(DAT_febec89c + uVar4) < 0 !=
           ((int)DAT_febec89c < 0 != (int)-uVar4 < 0 &&
           (int)-uVar4 < 0 == (int)(DAT_febec89c + uVar4) < 0)) {
    DAT_febec8a0 = DAT_febec9b8 - uVar4;
  }
  iVar5 = (int)((int)(int16_t)DAT_febec9e8);
  if ((iVar5 - iVar3 < 0 != (iVar5 < 0 != iVar3 < 0 && iVar3 < 0 == iVar5 - iVar3 < 0) ||
       iVar5 == iVar3) &&
     (iVar3 = iVar1,
     iVar5 - iVar1 < 0 == (iVar5 < 0 != iVar1 < 0 && iVar1 < 0 == iVar5 - iVar1 < 0) &&
     iVar5 != iVar1)) {
    iVar3 = iVar5;
  }
  DAT_febec8a4 = (DAT_febec8a0 * iVar3) / 0x100;
  DAT_febec9fa = DAT_febec9f8;
  if ((int)(DAT_febec8a4 - uVar2) < 0 != ((int)DAT_febec8a4 < 0 && -1 < (int)(DAT_febec8a4 - uVar2))
      || DAT_febec8a4 == uVar2) {
    uVar4 = -uVar2;
    if ((int)(DAT_febec8a4 + uVar2) < 0 ==
        ((int)DAT_febec8a4 < 0 != (int)uVar4 < 0 &&
        (int)uVar4 < 0 == (int)(DAT_febec8a4 + uVar2) < 0) && DAT_febec8a4 != uVar4) {
      DAT_febec9fa = (ushort)DAT_febec8a4;
    }
    else {
      DAT_febec9fa = (ushort)uVar4;
    }
  }
  DAT_febec9b8 = DAT_febec8a0;
  DAT_febec9e4 = DAT_febec8a0;
  f33_angle_controller_target_triplicate[0] = DAT_febec9fa;
  f33_angle_controller_target_triplicate[1] = DAT_febec9fa;
  f33_angle_controller_target_triplicate[2] = DAT_febec9fa;
  return;
}



/* Retained gain, inner slew and magnitude clamp publish one target redundantly toCAA6/8/A, not
   three independent producers. Exact inner limits65280/12800. Inner retained gain/slew/absolute
   limit publishes one calculated target three times, not three independent sources. */

void f33_publish_angle_controller_target_triplicate(void)

{
  FUN_000cccc6();
  FUN_000ccd50();
  FUN_000ccdc4();
  FUN_000ccdf8();
  return;
}



void FUN_000ccecc(void)

{
  int iVar1;
  
  if ((DAT_febecb00 & 7) == 7) {
    DAT_febec9fe = 0x7ffe;
    DAT_febeca00 = 0x7ffe;
  }
  else {
    iVar1 = (int)(short)((DAT_febecb00 & 7) + (DAT_febeac3c & 1) * 8);
    DAT_febec9fe = (*((undefined2 *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd3cc4u + (uint32_t)(iVar1 * 0x57) * 4u)))))));
    DAT_febeca00 = (*((undefined2 *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd3cc8u + (uint32_t)(iVar1 * 0x57) * 4u)))))));
  }
  return;
}



/* Signed32 AE90 doubled/clamped32767, then six-generation retained interpolation; generations1..5
   add delta/6 and generation6 selects complete target. Signed32 AE90 doubles/clamps32767, changed
   target interpolates delta/6 for generations1..5 and completes on6. */

void f33_interpolate_selected_angle_target(void)

{
  int iVar1;
  uint uVar2;
  uint uVar3;
  int iVar4;
  
  iVar1 = ((int)(int16_t)DAT_febeae90) * 2;
  iVar4 = 0x7fff;
  if ((iVar1 + -0x7fff < 0 != (iVar1 < 0 && -1 < iVar1 + -0x7fff) || iVar1 == 0x7fff) &&
     (iVar4 = iVar1, iVar1 + 0x7fff < 0 != (-1 < iVar1 && iVar1 + 0x7fff < 0) || iVar1 == -0x7fff))
  {
    iVar4 = -0x7fff;
  }
  DAT_febec9fc = (short)iVar4;
  DAT_febec8b4 = (int)DAT_febec9fc;
  if (((DAT_febec8b8 == DAT_febec9a0) || (DAT_febec8b8 == DAT_febec9cc)) ||
     (iVar1 = DAT_febec9a0, DAT_febec9a0 != DAT_febec9cc)) {
    iVar1 = DAT_febec8b8;
  }
  if (DAT_febec8b4 == ((int)(int16_t)DAT_febecaa4)) {
    uVar2 = (uint)(byte)(DAT_febeca97 + 1);
  }
  else {
    DAT_febec8a8 = DAT_febec8b4 - iVar1;
    uVar2 = 1;
    DAT_febecaa4 = DAT_febec9fc;
  }
  DAT_febeca97 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xb146cu + (uint32_t)(DAT_febeac3c & 1) * 4u))))))));
  uVar3 = (uint)DAT_febeca97;
  DAT_febec8ac = DAT_febec8a8;
  if (uVar3 != 0) {
    if (DAT_febec8a8 == -0x80000000 && uVar3 == 0xffffffff) {
      DAT_febec8ac = -0x80000000;
    }
    else {
      DAT_febec8ac = DAT_febec8a8 / (int)uVar3;
    }
  }
  if (uVar2 < uVar3) {
    DAT_febec8b4 = DAT_febec8ac + iVar1;
    DAT_febeca97 = (byte)uVar2;
  }
  DAT_febec99c = DAT_febec8b4;
  DAT_febec9c8 = DAT_febec8b4;
  return;
}



/* Bound target around prior selected value and magnitude, publishC8B8/C9A0/C9CC. Ordinary limits
   are bank/mode dependent; mode7 bypasses slew with32766 limits. Publish bounded target
   triplicateC8B8/C9A0/C9CC; mode7 keeps target production with32766 overrides and bypasses ordinary
   slew. */

void f33_bound_selected_angle_target(void)

{
  int iVar1;
  uint uVar2;
  uint uVar3;
  uint uVar4;
  uint uVar5;
  
  uVar5 = (uint)DAT_febec9fe;
  uVar4 = (uint)DAT_febeca00;
  if (((DAT_febec8b4 == DAT_febec99c) || (DAT_febec8b4 == DAT_febec9c8)) ||
     (DAT_febec8b0 = DAT_febec99c, DAT_febec99c != DAT_febec9c8)) {
    DAT_febec8b0 = DAT_febec8b4;
  }
  if (((DAT_febec8b8 == DAT_febec9a0) || (DAT_febec8b8 == DAT_febec9cc)) ||
     (DAT_febec9a0 != DAT_febec9cc)) {
    DAT_febec9a0 = DAT_febec8b8;
  }
  if ((DAT_febecb00 & 7) != 7) {
    uVar2 = DAT_febec8b0 - DAT_febec9a0;
    if (((int)(uVar2 - uVar4) < 0 != ((int)uVar2 < 0 && -1 < (int)(uVar2 - uVar4)) || uVar2 == uVar4
        ) && (uVar3 = -uVar4, iVar1 = uVar2 + uVar4, uVar4 = uVar3,
             iVar1 < 0 == ((int)uVar2 < 0 != (int)uVar3 < 0 && (int)uVar3 < 0 == iVar1 < 0) &&
             uVar2 != uVar3)) {
      uVar4 = uVar2;
    }
    DAT_febec8b0 = uVar4 + DAT_febec9a0;
  }
  DAT_febec8b8 = uVar5;
  if (((int)(DAT_febec8b0 - uVar5) < 0 !=
       ((int)DAT_febec8b0 < 0 && -1 < (int)(DAT_febec8b0 - uVar5)) || DAT_febec8b0 == uVar5) &&
     (DAT_febec8b8 = -uVar5,
     (int)(DAT_febec8b0 + uVar5) < 0 ==
     ((int)DAT_febec8b0 < 0 != (int)DAT_febec8b8 < 0 &&
     (int)DAT_febec8b8 < 0 == (int)(DAT_febec8b0 + uVar5) < 0) && DAT_febec8b0 != DAT_febec8b8)) {
    DAT_febec8b8 = DAT_febec8b0;
  }
  DAT_febec9a0 = DAT_febec8b8;
  DAT_febec9cc = DAT_febec8b8;
  return;
}



/* Compose interpolation and bounds; mode7 still produces target, with32766 limit overrides. Compose
   six-generation target interpolation and independent slew/magnitude bounds even in mode7. */

void f33_update_selected_angle_target(void)

{
  FUN_000ccecc();
  f33_interpolate_selected_angle_target();
  f33_bound_selected_angle_target();
  return;
}



/* WARNING: Removing unreachable block (ram,0x000cd08a) */
/* WARNING: Removing unreachable block (ram,0x000cd07c) */
/* WARNING: Removing unreachable block (ram,0x000cd074) */

void FUN_000cd046(void)

{
  int iVar1;
  
  iVar1 = (int)((int)(int16_t)DAT_febeca0c);
  DAT_febeca0c = ((int)(int16_t)DAT_febeae24);
  DAT_febeca0a = (short)((((0x4000 - (*((short *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xb146cu + (uint32_t)(DAT_febeac3c & 1) * 4u)))) + 0x42))))) / 2)
                         * (iVar1 + ((int)(int16_t)DAT_febeae24))) / 0x4000) +
                 (short)(((int)((int)(int16_t)DAT_febeca0a) *
                         (int)(*((short *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xb146cu + (uint32_t)(DAT_febeac3c & 1) * 4u)))) + 0x42))))) / 0x4000);
  return;
}



/* WARNING: Removing unreachable block (ram,0x000cd116) */
/* ClampC172 to4279 then retained69/256 filter; publishCA36/82/90, save old stateCA0E. Measured
   rateC172 is bounded4279 then filtered69/256 through retained triplicate; invoked before mode7
   reset, not skipped with PID. */

void f33_filter_angle_controller_measured_rate(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  
  iVar3 = (int)((int)(int16_t)DAT_febeca36);
  iVar4 = (int)((int)(int16_t)DAT_febec172);
  iVar2 = (int)((int)(int16_t)DAT_febeca82);
  DAT_febec984 = (uint)(*((ushort *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd3ce4u + (uint32_t)((short)((DAT_febecb00 & 7) + (DAT_febeac3c & 1) * 8) * 0x57) * 4u)))))));
  if (((iVar3 == iVar2) || (iVar3 == ((int)(int16_t)DAT_febeca90))) || (iVar2 != ((int)(int16_t)DAT_febeca90))) {
    iVar2 = iVar3;
  }
  iVar3 = (int)DAT_000b05b8;
  DAT_febeca14 = DAT_000b05b8;
  if ((iVar4 - iVar3 < 0 != (iVar4 < 0 != iVar3 < 0 && iVar3 < 0 == iVar4 - iVar3 < 0) ||
       iVar4 == iVar3) &&
     (iVar1 = -iVar3, DAT_febeca14 = ((int)(int16_t)DAT_febec172),
     iVar4 + iVar3 < 0 != (iVar4 < 0 != iVar1 < 0 && iVar1 < 0 == iVar4 + iVar3 < 0) ||
     iVar4 == iVar1)) {
    DAT_febeca14 = (short)iVar1;
  }
  DAT_febeca0e = (short)iVar2;
  DAT_febeca36 = (short)((int)(iVar2 * (0x100 - DAT_febec984) + (int)DAT_febeca14 * DAT_febec984) /
                        0x100);
  DAT_febeca82 = ((int)(int16_t)DAT_febeca36);
  DAT_febeca90 = ((int)(int16_t)DAT_febeca36);
  return;
}



/* WARNING: Removing unreachable block (ram,0x000cd230) */
/* WARNING: Removing unreachable block (ram,0x000cd226) */
/* WARNING: Removing unreachable block (ram,0x000cd1e8) */
/* WARNING: Removing unreachable block (ram,0x000cd1a6) */
/* WARNING: Removing unreachable block (ram,0x000cd1a2) */
/* Scale voted target/feedback2934/1024; error clamp18000. Separate bounded error filterCA32 and
   retained derivative stateC910; derivative publication capped1600. Target/feedback scale2934/1024
   with error clamp18000; separate error and derivative histories, derivative bounded1600. */

void f33_update_angle_error_and_derivative(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  
  if (((DAT_febec8b8 == DAT_febec9a0) || (DAT_febec8b8 == DAT_febec9cc)) ||
     (iVar1 = DAT_febec9a0, DAT_febec9a0 != DAT_febec9cc)) {
    iVar1 = DAT_febec8b8;
  }
  iVar4 = (int)((int)(int16_t)DAT_febecad2);
  iVar2 = (int)((int)(int16_t)DAT_febecad4);
  if (((iVar4 == iVar2) || (iVar4 == ((int)(int16_t)DAT_febecad6))) || (iVar2 != ((int)(int16_t)DAT_febecad6))) {
    iVar2 = iVar4;
  }
  iVar4 = (int)(short)((DAT_febecb00 & 7) + (DAT_febeac3c & 1) * 8);
  iVar1 = (iVar1 * 0xb76) / 0x400;
  DAT_febec8dc = (iVar2 * 0xb76) / 0x400;
  DAT_febec988 = (uint)(*((ushort *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd3ce0u + (uint32_t)(iVar4 * 0x57) * 4u)))))));
  DAT_febec98c = (uint)(*((ushort *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd3ce8u + (uint32_t)(iVar4 * 0x57) * 4u)))))));
  DAT_febec8e0 = iVar1 - DAT_febec8dc;
  DAT_febec8e4 = DAT_000b05a8;
  if ((DAT_febec8e0 - DAT_000b05a8 < 0 !=
       (DAT_febec8e0 < 0 != DAT_000b05a8 < 0 && DAT_000b05a8 < 0 == DAT_febec8e0 - DAT_000b05a8 < 0)
       || DAT_febec8e0 == DAT_000b05a8) &&
     (DAT_febec8e4 = -DAT_000b05a8,
     DAT_febec8e0 + DAT_000b05a8 < 0 ==
     (DAT_febec8e0 < 0 != DAT_febec8e4 < 0 && DAT_febec8e4 < 0 == DAT_febec8e0 + DAT_000b05a8 < 0)
     && DAT_febec8e0 != DAT_febec8e4)) {
    DAT_febec8e4 = DAT_febec8e0;
  }
  DAT_febec90c = (int)((int)(int16_t)DAT_febeca32);
  iVar2 = (int)(DAT_febec90c * (0x100 - DAT_febec988) + DAT_febec8e4 * DAT_febec988) / 0x100;
  if (((DAT_febec910 == DAT_febec9a8) || (DAT_febec910 == DAT_febec9d4)) ||
     (DAT_febec914 = DAT_febec9a8, DAT_febec9a8 != DAT_febec9d4)) {
    DAT_febec914 = DAT_febec910;
  }
  iVar3 = (int)DAT_000b05b6;
  DAT_febec910 = (int)(DAT_febec914 * (0x100 - DAT_febec98c) + DAT_febec8e4 * DAT_febec98c) / 0x100;
  DAT_febec8e8 = ((DAT_febec910 - DAT_febec914) * 0x100) / 0x10;
  iVar4 = iVar3;
  if ((DAT_febec8e8 - iVar3 < 0 !=
       (DAT_febec8e8 < 0 != iVar3 < 0 && iVar3 < 0 == DAT_febec8e8 - iVar3 < 0) ||
       DAT_febec8e8 == iVar3) &&
     (iVar4 = -iVar3,
     DAT_febec8e8 + iVar3 < 0 ==
     (DAT_febec8e8 < 0 != iVar4 < 0 && iVar4 < 0 == DAT_febec8e8 + iVar3 < 0) &&
     DAT_febec8e8 != iVar4)) {
    iVar4 = DAT_febec8e8;
  }
  DAT_febec8d8 = DAT_febec8d4;
  DAT_febec8d4 = iVar1;
  DAT_febeca12 = (undefined2)iVar4;
  DAT_febeca84 = DAT_febeca12;
  DAT_febeca92 = DAT_febeca12;
  if (iVar2 + -0x7fff < 0 == (iVar2 < 0 && -1 < iVar2 + -0x7fff) && iVar2 != 0x7fff) {
    DAT_febeca32 = 0x7fff;
  }
  else {
    DAT_febeca32 = (short)iVar2;
    if (iVar2 + 0x7fff < 0 != (-1 < iVar2 && iVar2 + 0x7fff < 0)) {
      DAT_febeca32 = 0x8001;
    }
  }
  DAT_febec9a8 = DAT_febec910;
  DAT_febec9d4 = DAT_febec910;
  return;
}



/* WARNING: Removing unreachable block (ram,0x000cd372) */
/* WARNING: Removing unreachable block (ram,0x000cd354) */
/* Bounded-difference target memory and retained rate filter; real R10 return consumed byCD538.
   Target feedforward uses bounded-difference/play-style memory and retained rate filter; */

int f33_update_angle_target_rate_feedforward(void)

{
  uint uVar1;
  int iVar2;
  int iVar3;
  uint32_t puVar4;
  int iVar5;
  uint uVar6;
  uint uVar7;
  uint uVar8;
  int iVar9;
  
  iVar2 = DAT_febec958;
  iVar9 = DAT_febec950;
  puVar4 = 0xfebeb800u;
  if (((DAT_febec8b8 == DAT_febec9a0) || (DAT_febec8b8 == DAT_febec9cc)) ||
     (iVar3 = DAT_febec9a0, DAT_febec9a0 != DAT_febec9cc)) {
    iVar3 = DAT_febec8b8;
  }
  iVar5 = FUN_000d0896(((ushort *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd3d04u + (uint32_t)((short)((DAT_febecb00 & 7) + (DAT_febeac3c & 1) * 8) * 0x57) * 4u))))))), DAT_febeae02);
  uVar6 = iVar5 * 10;
  iVar3 = iVar3 * 10;
  uVar1 = iVar3 - iVar9;
  uVar7 = (uint)(*((ushort *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xb1484u + (uint32_t)((byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0xbc4))))) & 1) * 4u)))))));
  if (uVar7 != 0) {
    if (uVar6 == 0x80000000 && uVar7 == 0xffffffff) {
      uVar6 = 0;
    }
    else {
      uVar6 = (int)uVar6 / (int)uVar7;
    }
  }
  uVar8 = uVar6 & 0xffff;
  if ((int)(uVar1 - uVar8) < 0 == ((int)uVar1 < 0 && -1 < (int)(uVar1 - uVar8)) && uVar1 != uVar8) {
    iVar9 = iVar3 - uVar8;
  }
  else if ((int)(uVar1 + uVar8) < 0 !=
           ((int)uVar1 < 0 != (int)-uVar8 < 0 && (int)-uVar8 < 0 == (int)(uVar1 + uVar8) < 0)) {
    iVar9 = uVar8 + iVar3;
  }
  uVar8 = (uint)(*((ushort *)camry_host_ptr((uint32_t)((int)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xb1484u + (uint32_t)((byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0xbc4))))) & 1) * 4u)))) + 2))));
  (*((int *)camry_host_ptr((uint32_t)(puVar4 + 0x1150)))) = iVar9;
  (*((short *)camry_host_ptr((uint32_t)(puVar4 + 0x1248)))) = (short)iVar5;
  iVar9 = (int)((iVar3 - iVar9) * uVar7) / 10;
  (*((uint *)camry_host_ptr((uint32_t)(puVar4 + 0x114c)))) = uVar1;
  (*((short *)camry_host_ptr((uint32_t)(puVar4 + 0x124a)))) = (short)uVar6;
  (*((int *)camry_host_ptr((uint32_t)(puVar4 + 0x1154)))) = iVar9;
  iVar9 = (int)(iVar2 * (0x100 - uVar8)) / 0x100 + iVar9 * uVar8 * 2;
  (*((int *)camry_host_ptr((uint32_t)(puVar4 + 0x1158)))) = iVar9;
  return iVar9;
}



/* WARNING: Removing unreachable block (ram,0x000cd3fe) */
/* Mapped target shaping with real R10 return, not void despite original auto signature. Mapped
   target feedforward returns real signed R10 contribution despite former void auto signature. */

int f33_map_angle_target_feedforward(void)

{
  undefined2 uVar1;
  int iVar2;
  uint32_t puVar3;
  int iVar4;
  int iVar5;
  int iVar6;
  short local_18;
  short sStack_16;
  
  iVar2 = DAT_febec8d4;
  uVar1 = DAT_febeadf6;
  puVar3 = 0xfebeb800u;
  local_18 = 0;
  sStack_16 = 0;
  iVar4 = f33_abs_s32_wrapping(DAT_febec8d4);
  iVar6 = (int)(short)(((byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(0x1300))))) & 7) + ((byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0xbc4))))) & 1) * 8);
  FUN_000d097a(((ushort *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd3d34u + (uint32_t)(iVar6 * 0x57) * 4u))))))), uVar1, &local_18, &sStack_16);
  iVar5 = FUN_000d08e8(((uint *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd3cacu + (uint32_t)(iVar6 * 0x57 + local_18 + 0x18) * 4u))))))), iVar4);
  iVar4 = FUN_000d08e8(((uint *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd3cacu + (uint32_t)(iVar6 * 0x57 + local_18 + 0x19) * 4u))))))), iVar4);
  iVar6 = ((iVar4 - iVar5) * (int)sStack_16) / 0x400 + iVar5;
  if (iVar2 < 0) {
    iVar6 = -iVar6;
  }
  (*((int *)camry_host_ptr((uint32_t)(0x115au + (int)(puVar3 + 6))))) = iVar6;
  (*((short *)camry_host_ptr((uint32_t)(puVar3 + 0x1268)))) = sStack_16;
  (*((int *)camry_host_ptr((uint32_t)(puVar3 + 0x1164)))) = iVar5;
  (*((short *)camry_host_ptr((uint32_t)(puVar3 + 0x1266)))) = local_18;
  (*((int *)camry_host_ptr((uint32_t)(puVar3 + 0x1168)))) = iVar4;
  return iVar6;
}



void FUN_000cd426(void)

{
  uint32_t puVar1;
  int iVar2;
  
  puVar1 = 0xfebeb800u;
  iVar2 = f33_interpolate_unsigned_axis_sentinel_curve
                    (((ushort *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd3d08u + (uint32_t)((short)((DAT_febecb00 & 7) + (DAT_febeac3c & 1) * 8) * 0x57) * 4u)))))),DAT_febeae02);
  (*((short *)camry_host_ptr((uint32_t)(puVar1 + 0x1210)))) = (short)iVar2;
  return;
}


/* WARNING: Removing unreachable block (ram,0x000cd582) */

int FUN_000cd538(void)

{
  char cVar1;
  uint32_t puVar2;
  int iVar3;
  int iVar4;
  
  puVar2 = 0xfebeb800u;
  cVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd3cecu + (uint32_t)((short)((DAT_febecb00 & 7) + (DAT_febeac3c & 1) * 8) * 0x57) * 4u))))))));
  iVar3 = f33_update_angle_target_rate_feedforward();
  if (cVar1 == 'Z') {
    iVar4 = f33_map_angle_target_feedforward();
  }
  else {
    FUN_000cd426();
    iVar4 = f33_calculate_angle_target_feedforward();
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(0x12a0))))) = cVar1;
  (*((int *)camry_host_ptr((uint32_t)(puVar2 + 0x112c)))) = iVar3 / 0x200 + iVar4;
  return iVar4;
}





void FUN_000cd590(void)

{
  ushort input;
  uint32_t puVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  
  input = DAT_febeae02;
  puVar1 = 0xfebeb800u;
  iVar4 = (int)(short)((DAT_febecb00 & 7) + (DAT_febeac3c & 1) * 8);
  iVar2 = f33_interpolate_unsigned_axis_sentinel_curve
                    (((ushort *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd3d38u + (uint32_t)(iVar4 * 0x57) * 4u)))))),DAT_febeae02);
  iVar3 = f33_interpolate_unsigned_axis_sentinel_curve
                    (((ushort *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd3d44u + (uint32_t)(iVar4 * 0x57) * 4u)))))),input);
  iVar4 = f33_interpolate_unsigned_axis_sentinel_curve
                    (((ushort *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd3d48u + (uint32_t)(iVar4 * 0x57) * 4u)))))),input);
  (*((short *)camry_host_ptr((uint32_t)(puVar1 + 0x1216)))) = (short)iVar2;
  (*((short *)camry_host_ptr((uint32_t)(puVar1 + 0x1230)))) = (short)iVar3;
  (*((short *)camry_host_ptr((uint32_t)(0x121au + (int)(puVar1 + 2))))) = (short)iVar4;
  return;
}



undefined2 FUN_000cd5ea(void)

{
  int iVar1;
  undefined2 uVar2;
  undefined2 uVar3;
  uint32_t puVar4;
  short sVar5;
  undefined2 uVar6;
  undefined2 uVar7;
  uint uVar8;
  
  puVar4 = 0xfebeb800u;
  iVar1 = (int)(short)((DAT_febecb00 & 7) + (DAT_febeac3c & 1) * 8);
  uVar8 = f33_abs_s32_wrapping((int)DAT_febeca32);
  if ((int)(uVar8 - 0xffff) < 0 == ((int)uVar8 < 0 && -1 < (int)(uVar8 - 0xffff))) {
    uVar8 = 0xffff;
  }
  sVar5 = f33_abs_s16_wrapping((*((short *)camry_host_ptr((uint32_t)(puVar4 + 0x740)))));
  uVar6 = FUN_000d0896(((ushort *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd3d3cu + (uint32_t)(iVar1 * 0x57) * 4u))))))), uVar8 & 0xffff);
  uVar7 = FUN_000d07f2(((short *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd3d40u + (uint32_t)(iVar1 * 0x57) * 4u))))))), (int)sVar5);
  uVar2 = (*((undefined2 *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd3cd0u + (uint32_t)(iVar1 * 0x57) * 4u)))))));
  uVar3 = (*((undefined2 *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd3cd4u + (uint32_t)(iVar1 * 0x57) * 4u)))))));
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar4 + 0x1204)))) = uVar6;
  (*((undefined2 *)camry_host_ptr((uint32_t)(0x1206u + (int)puVar4)))) = uVar7;
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar4 + 0x1218)))) = uVar2;
  (*((undefined2 *)camry_host_ptr((uint32_t)(0x121au + (int)puVar4)))) = uVar3;
  return uVar7;
}


/* WARNING: Removing unreachable block (ram,0x000cd6f4) */

void FUN_000cd662(void)

{
  undefined1 uVar1;
  ushort uVar2;
  undefined2 uVar3;
  int iVar4;
  uint32_t puVar5;
  uint uVar6;
  int iVar7;
  int iVar8;
  int value;
  short local_20;
  short sStack_1e;
  
  uVar3 = DAT_febeadf6;
  puVar5 = 0xfebeb800u;
  value = (int)((int)(int16_t)DAT_febeca32);
  local_20 = 0;
  sStack_1e = 0;
  iVar4 = (int)(short)((DAT_febecb00 & 7) + (DAT_febeac3c & 1) * 8);
  uVar6 = f33_abs_s32_wrapping(value);
  if ((int)(uVar6 - 0xffff) < 0 == ((int)uVar6 < 0 && -1 < (int)(uVar6 - 0xffff))) {
    uVar6 = 0xffff;
  }
  uVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd3cf0u + (uint32_t)(iVar4 * 0x57) * 4u))))))));
  uVar2 = (*((ushort *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd3cf4u + (uint32_t)(iVar4 * 0x57) * 4u)))))));
  FUN_000d097a(((ushort *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd3d74u + (uint32_t)(iVar4 * 0x57) * 4u))))))), uVar3, &local_20, &sStack_1e);
  iVar7 = FUN_000d0896(((ushort *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd3cacu + (uint32_t)(iVar4 * 0x57 + local_20 + 0x28) * 4u))))))), uVar6 & 0xffff);
  iVar8 = FUN_000d0896(((ushort *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd3cacu + (uint32_t)(iVar4 * 0x57 + local_20 + 0x29) * 4u))))))), uVar6 & 0xffff);
  iVar4 = ((iVar8 - iVar7) * (int)sStack_1e) / 0x400 + iVar7;
  if (value < 0) {
    iVar4 = -iVar4;
  }
  (*((int *)camry_host_ptr((uint32_t)(puVar5 + 0x1170)))) = iVar4;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(0x12a1))))) = uVar1;
  (*((uint *)camry_host_ptr((uint32_t)(puVar5 + 0x116c)))) = (uint)uVar2;
  (*((short *)camry_host_ptr((uint32_t)(puVar5 + 0x126c)))) = sStack_1e;
  (*((short *)camry_host_ptr((uint32_t)(puVar5 + 0x126a)))) = local_20;
  (*((short *)camry_host_ptr((uint32_t)(puVar5 + 0x126e)))) = (short)iVar7;
  (*((short *)camry_host_ptr((uint32_t)(puVar5 + 0x1270)))) = (short)iVar8;
  return;
}



/* WARNING: Removing unreachable block (ram,0x000cd80a) */
/* WARNING: Removing unreachable block (ram,0x000cd7b2) */

void FUN_000cd724(void)

{
  undefined1 uVar1;
  ushort uVar2;
  undefined2 uVar3;
  int iVar4;
  int iVar5;
  uint32_t puVar6;
  uint uVar7;
  int iVar8;
  int iVar9;
  int iVar10;
  uint uVar11;
  short local_28;
  short sStack_26;
  
  uVar3 = DAT_febeadf6;
  puVar6 = 0xfebeb800u;
  local_28 = 0;
  sStack_26 = 0;
  iVar5 = (int)(short)((DAT_febecb00 & 7) + (DAT_febeac3c & 1) * 8);
  iVar10 = (int)((int)(int16_t)DAT_febeca12);
  iVar4 = (int)((int)(int16_t)DAT_febeca84);
  if (((iVar10 == iVar4) || (iVar10 == ((int)(int16_t)DAT_febeca92))) || (iVar4 != ((int)(int16_t)DAT_febeca92))) {
    iVar4 = iVar10;
  }
  if (((DAT_febec8bc == DAT_febec9a4) || (DAT_febec8bc == DAT_febec9d0)) ||
     (iVar10 = DAT_febec9a4, DAT_febec9a4 != DAT_febec9d0)) {
    iVar10 = DAT_febec8bc;
  }
  uVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd3cf8u + (uint32_t)(iVar5 * 0x57) * 4u))))))));
  uVar11 = (uint)(*((ushort *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd3cccu + (uint32_t)(iVar5 * 0x57) * 4u)))))));
  uVar2 = (*((ushort *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd3cfcu + (uint32_t)(iVar5 * 0x57) * 4u)))))));
  iVar4 = (int)(iVar10 * (0x100 - uVar11) + iVar4 * uVar11) / 0x100;
  uVar7 = f33_abs_s32_wrapping(iVar4);
  if ((int)(uVar7 - 0xffff) < 0 == ((int)uVar7 < 0 && -1 < (int)(uVar7 - 0xffff))) {
    uVar7 = 0xffff;
  }
  FUN_000d097a(((ushort *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd3da0u + (uint32_t)(iVar5 * 0x57) * 4u))))))), uVar3, &local_28, &sStack_26);
  iVar8 = FUN_000d0896(((ushort *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd3cacu + (uint32_t)(iVar5 * 0x57 + local_28 + 0x33) * 4u))))))), uVar7 & 0xffff);
  iVar9 = FUN_000d0896(((ushort *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd3cacu + (uint32_t)(iVar5 * 0x57 + local_28 + 0x34) * 4u))))))), uVar7 & 0xffff);
  iVar5 = ((iVar9 - iVar8) * (int)sStack_26) / 0x400 + iVar8;
  if (iVar4 < 0) {
    iVar5 = -iVar5;
  }
  (*((int *)camry_host_ptr((uint32_t)(puVar6 + 0x117c)))) = iVar5;
  (*((int *)camry_host_ptr((uint32_t)(puVar6 + 0x10bc)))) = iVar4;
  (*((int *)camry_host_ptr((uint32_t)(0x119eu + (int)(puVar6 + 6))))) = iVar4;
  (*((int *)camry_host_ptr((uint32_t)(puVar6 + 0x11d0)))) = iVar4;
  (*((int *)camry_host_ptr((uint32_t)(puVar6 + 0x10c0)))) = iVar10;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(0x12a2))))) = uVar1;
  (*((uint *)camry_host_ptr((uint32_t)(puVar6 + 0x1174)))) = uVar11;
  (*((uint *)camry_host_ptr((uint32_t)(puVar6 + 0x1178)))) = (uint)uVar2;
  (*((short *)camry_host_ptr((uint32_t)(puVar6 + 0x1272)))) = local_28;
  (*((short *)camry_host_ptr((uint32_t)(puVar6 + 0x1274)))) = sStack_26;
  (*((short *)camry_host_ptr((uint32_t)(puVar6 + 0x1276)))) = (short)iVar8;
  (*((short *)camry_host_ptr((uint32_t)(puVar6 + 0x1278)))) = (short)iVar9;
  return;
}





void FUN_000cd84e(void)

{
  DAT_febec980 = (uint)(*((ushort *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd3d00u + (uint32_t)((short)((DAT_febecb00 & 7) + (DAT_febeac3c & 1) * 8) * 0x57) * 4u)))))));
  return;
}



void FUN_000cd878(void)

{
  FUN_000cd662();
  FUN_000cd724();
  FUN_000cd84e();
  return;
}



/* WARNING: Removing unreachable block (ram,0x000cd8ce) */

void FUN_000cd88c(void)

{
  if (((DAT_febec8f0 == DAT_febec9ac) || (DAT_febec8f0 == DAT_febec9d8)) ||
     (DAT_febec9ac != DAT_febec9d8)) {
    DAT_febec9ac = DAT_febec8f0;
  }
  DAT_febec8f4 = DAT_febec970;
  DAT_febec8f8 = DAT_febec9ac;
  DAT_febec8f0 = (DAT_febec9ac * (0x100 - DAT_febec96c) + DAT_febec970 * DAT_febec96c) / 0x100;
  DAT_febec9ac = DAT_febec8f0;
  DAT_febec9d8 = DAT_febec8f0;
  return;
}



int FUN_000cd8e0(void)

{
  int iVar1;
  uint32_t puVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  int iVar6;
  
  puVar2 = 0xfebeb800u;
  iVar4 = (int)((int)(int16_t)DAT_febeca1e);
  iVar1 = (int)((int)(int16_t)DAT_febeca86);
  iVar6 = (int)((int)(int16_t)DAT_febeca18);
  iVar5 = (int)((int)(int16_t)DAT_febeca1a);
  if (((iVar4 == iVar1) || (iVar4 == ((int)(int16_t)DAT_febeca94))) || (iVar1 != ((int)(int16_t)DAT_febeca94))) {
    iVar1 = iVar4;
  }
  iVar4 = f33_abs_s32_wrapping(DAT_febec8d4);
  iVar3 = f33_abs_s32_wrapping((*((int *)camry_host_ptr((uint32_t)(puVar2 + 0x10d8)))));
  if ((iVar4 - iVar3 < 0 || iVar4 == iVar3) && (iVar6 = iVar1, iVar4 - iVar3 < 0)) {
    iVar6 = iVar5;
  }
  (*((short *)camry_host_ptr((uint32_t)(0x1206u + (int)(puVar2 + 2))))) = (short)iVar1;
  return iVar6;
}



/* WARNING: Removing unreachable block (ram,0x000cd9d8) */
/* WARNING: Removing unreachable block (ram,0x000cd9b0) */

int FUN_000cd932(void)

{
  int iVar1;
  byte bVar2;
  byte bVar3;
  int iVar4;
  ushort uVar5;
  ushort uVar6;
  int iVar7;
  uint32_t puVar8;
  undefined2 uVar9;
  int iVar10;
  int iVar11;
  int iVar12;
  uint uVar13;
  byte bVar14;
  
  uVar6 = DAT_febeca06;
  uVar5 = DAT_febeca04;
  iVar4 = DAT_febec96c;
  iVar11 = DAT_febec8e4;
  puVar8 = 0xfebeb800u;
  uVar13 = (uint)DAT_febeca16;
  bVar2 = DAT_febecb00 & 7;
  bVar3 = DAT_febecb00 & 7;
  bVar14 = DAT_febecb00 & 7;
  iVar12 = (int)((int)(int16_t)DAT_febeca32);
  if (((DAT_febec8f0 == DAT_febec9ac) || (DAT_febec8f0 == DAT_febec9d8)) ||
     (iVar7 = DAT_febec9ac, DAT_febec9ac != DAT_febec9d8)) {
    iVar7 = DAT_febec8f0;
  }
  iVar10 = FUN_000cd8e0();
  iVar1 = iVar10 + uVar13;
  if (bVar2 == 0) {
    iVar11 = iVar11 * iVar1;
  }
  else {
    uVar13 = (uint)uVar5 * (uint)uVar6 >> 10;
    if (0x27ff < uVar13) {
      uVar13 = 0x2800;
    }
    uVar13 = uVar13 * iVar1 >> 10;
    if (0x8f5b < uVar13) {
      uVar13 = 0x8f5c;
    }
    iVar11 = uVar13 * iVar12;
  }
  iVar11 = iVar11 / 0x200;
  iVar12 = iVar11;
  if ((bVar3 != 0) && (iVar12 = iVar7, bVar14 != 7)) {
    iVar12 = (iVar7 * (0x100 - iVar4) + iVar11 * iVar4) / 0x100;
  }
  uVar9 = (undefined2)iVar10;
  (*((undefined2 *)camry_host_ptr((uint32_t)(0x121au + (int)(puVar8 + 4))))) = uVar9;
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar8 + 0x1286)))) = uVar9;
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar8 + 0x1294)))) = uVar9;
  (*((int *)camry_host_ptr((uint32_t)(puVar8 + 0x10ec)))) = iVar1;
  (*((int *)camry_host_ptr((uint32_t)(puVar8 + 0x10f0)))) = iVar12;
  (*((int *)camry_host_ptr((uint32_t)(puVar8 + 0x11ac)))) = iVar12;
  (*((int *)camry_host_ptr((uint32_t)(puVar8 + 0x11d8)))) = iVar12;
  (*((int *)camry_host_ptr((uint32_t)(puVar8 + 0x10f4)))) = iVar11;
  (*((int *)camry_host_ptr((uint32_t)(puVar8 + 0x10f8)))) = iVar7;
  return iVar10;
}



void FUN_000cda04(void)

{
  if (DAT_febecaa1 == 'Z') {
    FUN_000cd88c();
  }
  else {
    FUN_000cd932();
  }
  return;
}



/* WARNING: Removing unreachable block (ram,0x000cda7a) */
/* Mode0 clears. Otherwise ADBB1 or previousCA9B direction can block integration; blocked update
   retains rawC91C. Allowed saturated addition uses voted bounded state. Bank0 bound786432, bank1
   bound589824. Integral uses previous directional limit for anti-windup, mode0 clearing, and
   blocked-update raw retention; bank bounds786432/589824. */

void f33_update_angle_error_integral(void)

{
  uint uVar1;
  uint32_t puVar2;
  int iVar3;
  int iVar4;
  int local_c;
  
  puVar2 = 0xfebeb800u;
  local_c = DAT_febec91c;
  uVar1 = DAT_febecb00 & 7;
  if (((DAT_febec924 == DAT_febec9b0) || (DAT_febec924 == DAT_febec9dc)) ||
     (DAT_febec918 = DAT_febec9b0, DAT_febec9b0 != DAT_febec9dc)) {
    DAT_febec918 = DAT_febec924;
  }
  if ((DAT_febecb00 & 7) == 0) {
    local_c = 0;
  }
  else if (uVar1 == 7) {
    local_c = 0;
    uVar1 = 0;
  }
  else {
    uVar1 = (int)((int)((int)(int16_t)DAT_febeca32) * (uint)DAT_febeca30) / 0x10;
    if (((DAT_febeadbb != '\x01') && ((DAT_febeca9b != '\x02' || ((int)uVar1 < 0)))) &&
       ((DAT_febeca9b != '\x01' || (-1 < (int)uVar1)))) {
      puVar2 = 0xfebeb800u;
      FUN_000d0a06(DAT_febec918,uVar1,&local_c);
    }
  }
  iVar3 = (*((int *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xb146cu + (uint32_t)((byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0xbc4))))) & 1) * 4u)))) + 0xac))));
  iVar4 = iVar3;
  if ((local_c - iVar3 < 0 != (local_c < 0 != iVar3 < 0 && iVar3 < 0 == local_c - iVar3 < 0) ||
       local_c == iVar3) &&
     (iVar4 = -iVar3,
     local_c + iVar3 < 0 == (local_c < 0 != iVar4 < 0 && iVar4 < 0 == local_c + iVar3 < 0) &&
     local_c != iVar4)) {
    iVar4 = local_c;
  }
  (*((uint *)camry_host_ptr((uint32_t)(puVar2 + 0x1120)))) = uVar1;
  (*((int *)camry_host_ptr((uint32_t)(puVar2 + 0x111c)))) = local_c;
  (*((int *)camry_host_ptr((uint32_t)(puVar2 + 0x1124)))) = iVar4;
  (*((int *)camry_host_ptr((uint32_t)(puVar2 + 0x11b0)))) = iVar4;
  (*((int *)camry_host_ptr((uint32_t)(puVar2 + 0x11dc)))) = iVar4;
  return;
}



/* WARNING: Removing unreachable block (ram,0x000cdb4a) */

void FUN_000cdae0(void)

{
  undefined1 uVar1;
  undefined1 uVar2;
  
  if (((DAT_febec8fc == DAT_febec9b4) || (DAT_febec8fc == DAT_febec9e0)) ||
     (DAT_febec9b4 != DAT_febec9e0)) {
    DAT_febec9b4 = DAT_febec8fc;
  }
  if ((DAT_febecb00 & 7) == 0) {
    uVar2 = 1;
    uVar1 = 1;
    if (DAT_febeca98 != '\x01') {
      DAT_febec8c4 = 0;
      goto LAB_000cdb26;
    }
  }
  else {
    uVar2 = 0;
    DAT_febec8c4 = DAT_febec9b4;
    uVar1 = 0;
    if ((DAT_febecb00 & 7) == 7) goto LAB_000cdb26;
  }
  uVar2 = uVar1;
  DAT_febec8c4 = DAT_febec97c;
LAB_000cdb26:
  DAT_febeca98 = uVar2;
  DAT_febec8c8 = DAT_febec9b4;
  DAT_febec8fc = (DAT_febec9b4 * (0x100 - DAT_febec978) + DAT_febec8c4 * DAT_febec978) / 0x100;
  DAT_febec9b4 = DAT_febec8fc;
  DAT_febec9e0 = DAT_febec8fc;
  return;
}



/* WARNING: Removing unreachable block (ram,0x000cdbee) */

void FUN_000cdb5c(void)

{
  uint uVar1;
  int iVar2;
  int iVar3;
  
  iVar2 = (int)DAT_febeca12;
  iVar3 = (int)DAT_febeca84;
  uVar1 = DAT_febecb00 & 7;
  if (((iVar2 == iVar3) || (iVar2 == DAT_febeca92)) || (iVar3 != DAT_febeca92)) {
    iVar3 = iVar2;
  }
  if (((DAT_febec8fc == DAT_febec9b4) || (DAT_febec8fc == DAT_febec9e0)) ||
     (DAT_febec9b4 != DAT_febec9e0)) {
    DAT_febec9b4 = DAT_febec8fc;
  }
  if (((DAT_febec8bc == DAT_febec9a4) || (DAT_febec8bc == DAT_febec9d0)) ||
     (iVar2 = DAT_febec9a4, DAT_febec9a4 != DAT_febec9d0)) {
    iVar2 = DAT_febec8bc;
  }
  if ((DAT_febecb00 & 7) == 0) {
    if (DAT_febeca98 != '\x01') {
      DAT_febec8c8 = DAT_febec9b4;
      DAT_febec8fc = uVar1;
      DAT_febec9b4 = uVar1;
      DAT_febec9e0 = uVar1;
      DAT_febeca98 = 1;
      return;
    }
    iVar2 = 0x40;
    DAT_febec8fc = (uint)DAT_febeca1c * iVar3;
    DAT_febeca98 = 1;
  }
  else {
    DAT_febeca98 = 0;
    DAT_febec8c4 = DAT_febec9b4;
    if (uVar1 != 7) {
      DAT_febec8c4 = (int)((uint)DAT_febeca1c * iVar2) / 0x40;
    }
    DAT_febec8fc = DAT_febec9b4 * (0x100 - DAT_febec978) + DAT_febec8c4 * DAT_febec978;
    iVar2 = 0x100;
  }
  if (iVar2 != 0) {
    if (DAT_febec8fc == -0x80000000 && iVar2 == -1) {
      DAT_febec8fc = -0x80000000;
    }
    else {
      DAT_febec8fc = (int)DAT_febec8fc / iVar2;
    }
  }
  DAT_febec8c8 = DAT_febec9b4;
  DAT_febec9b4 = DAT_febec8fc;
  DAT_febec9e0 = DAT_febec8fc;
  return;
}



void FUN_000cdc2c(void)

{
  if (DAT_febecaa2 == 'Z') {
    FUN_000cdae0();
  }
  else {
    FUN_000cdb5c();
  }
  return;
}



/* Sequential initializer chain: 7 unconditional calls and no other statements; shape-verified. The
   called sequence is the function's entire behavior; chain family members differ in callee sets. */

void f33_run_init_chain_cdd1e(void)

{
  FUN_000cd590();
  FUN_000cd5ea();
  FUN_000cd878();
  FUN_000cda04();
  f33_update_angle_error_integral();
  FUN_000cdc2c();
  f33_compose_filtered_angle_error_feedback();
  return;
}



void FUN_000cdd42(void)

{
  int iVar1;
  bool bVar2;
  int iVar3;
  int iVar4;
  
  iVar4 = (int)((int)(int16_t)DAT_febeca0a);
  if (DAT_febeca99 == '\0') {
    iVar1 = iVar4 + DAT_000b05ba;
    bVar2 = -(int)DAT_000b05ba < 0;
    if (iVar1 < 0 == (iVar4 < 0 != bVar2 && bVar2 == iVar1 < 0)) {
      DAT_febeca20 = 0;
    }
    else {
      DAT_febeca20 = DAT_febeca20 + 1;
      DAT_febeca99 = DAT_000b05bc <= DAT_febeca20;
      if ((bool)DAT_febeca99) {
        DAT_febeca20 = 0;
      }
    }
  }
  else {
    iVar3 = -(int)DAT_000b05be;
    iVar1 = iVar4 + DAT_000b05be;
    if (iVar1 < 0 == (iVar4 < 0 != iVar3 < 0 && iVar3 < 0 == iVar1 < 0) && iVar4 != iVar3) {
      DAT_febeca22 = DAT_febeca22 + 1;
      if (DAT_000b05c0 <= DAT_febeca22) {
        DAT_febeca99 = '\0';
        DAT_febeca22 = 0;
      }
    }
    else {
      DAT_febeca22 = 0;
    }
  }
  return;
}



void FUN_000cddb6(void)

{
  int iVar1;
  int iVar2;
  
  iVar2 = (int)((int)(int16_t)DAT_febeca0a);
  if (DAT_febeca9a == '\0') {
    iVar1 = (int)DAT_000b05ba;
    if (iVar2 - iVar1 < 0 == (iVar2 < 0 != iVar1 < 0 && iVar1 < 0 == iVar2 - iVar1 < 0) &&
        iVar2 != iVar1) {
      DAT_febeca24 = DAT_febeca24 + 1;
      DAT_febeca9a = DAT_000b05bc <= DAT_febeca24;
      if ((bool)DAT_febeca9a) {
        DAT_febeca24 = 0;
      }
    }
    else {
      DAT_febeca24 = 0;
    }
  }
  else {
    iVar1 = (int)DAT_000b05be;
    if (iVar2 - iVar1 < 0 == (iVar2 < 0 != iVar1 < 0 && iVar1 < 0 == iVar2 - iVar1 < 0)) {
      DAT_febeca26 = 0;
    }
    else {
      DAT_febeca26 = DAT_febeca26 + 1;
      if (DAT_000b05c0 <= DAT_febeca26) {
        DAT_febeca9a = '\0';
        DAT_febeca26 = 0;
      }
    }
  }
  return;
}



/* WARNING: Removing unreachable block (ram,0x000cde84) */

void FUN_000cde26(void)

{
  undefined2 uVar1;
  short sVar2;
  short sVar3;
  uint32_t puVar4;
  short sVar5;
  int iVar6;
  int iVar7;
  int iVar8;
  short sVar9;
  int iVar10;
  
  sVar2 = DAT_febeca0a;
  puVar4 = 0xfebeb800u;
  sVar5 = f33_abs_s16_wrapping(DAT_febeca0a);
  uVar1 = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar4 + -0x9fe))));
  sVar3 = (*((short *)camry_host_ptr((uint32_t)(puVar4 + 0x1254))));
  iVar7 = (int)(short)(((byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(0x1300))))) & 7) + ((byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0xbc4))))) & 1) * 8);
  iVar6 = FUN_000d0896(((ushort *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd3da4u + (uint32_t)(iVar7 * 0x57) * 4u))))))), sVar5);
  iVar7 = FUN_000d0896(((ushort *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd3da8u + (uint32_t)(iVar7 * 0x57) * 4u))))))), uVar1);
  sVar9 = sVar2 - sVar3;
  iVar10 = (int)sVar9;
  sVar5 = (short)((iVar6 * iVar7) / 0x100);
  iVar8 = (int)sVar5;
  if (iVar10 - iVar8 < 0 == (iVar10 < 0 != iVar8 < 0 && iVar8 < 0 == iVar10 - iVar8 < 0) &&
      iVar10 != iVar8) {
    sVar3 = sVar2 - sVar5;
  }
  else if (iVar10 + iVar8 < 0 != (iVar10 < 0 != -iVar8 < 0 && -iVar8 < 0 == iVar10 + iVar8 < 0)) {
    sVar3 = sVar5 + sVar2;
  }
  (*((short *)camry_host_ptr((uint32_t)(puVar4 + 0x1254)))) = sVar3;
  (*((short *)camry_host_ptr((uint32_t)(puVar4 + 0x1252)))) = sVar9;
  (*((short *)camry_host_ptr((uint32_t)(puVar4 + 0x1250)))) = sVar5;
  (*((short *)camry_host_ptr((uint32_t)(puVar4 + 0x124c)))) = (short)iVar6;
  (*((short *)camry_host_ptr((uint32_t)(puVar4 + 0x124e)))) = (short)iVar7;
  return;
}



/* WARNING: Removing unreachable block (ram,0x000cdf84) */
/* WARNING: Removing unreachable block (ram,0x000cdf76) */

int FUN_000cdebc(void)

{
  byte bVar1;
  char cVar2;
  char cVar3;
  int iVar4;
  uint32_t puVar5;
  short input;
  int iVar6;
  int iVar7;
  int iVar8;
  int iVar9;
  int iVar10;
  int iVar11;
  uint uVar12;
  
  cVar3 = DAT_febeca9a;
  cVar2 = DAT_febeca99;
  puVar5 = 0xfebeb800u;
  bVar1 = DAT_febecb00 & 7;
  iVar7 = (int)(short)((DAT_febecb00 & 7) + (DAT_febeac3c & 1) * 8);
  if (((DAT_febec900 == DAT_febec990) || (DAT_febec900 == DAT_febec9bc)) ||
     (iVar4 = DAT_febec990, DAT_febec990 != DAT_febec9bc)) {
    iVar4 = DAT_febec900;
  }
  uVar12 = (uint)DAT_febeca58;
  input = f33_abs_s16_wrapping(DAT_febeca54);
  iVar6 = f33_interpolate_signed_sentinel_curve(((short *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd3dacu + (uint32_t)(iVar7 * 0x57) * 4u)))))),input);
  iVar7 = f33_interpolate_signed_sentinel_curve(((short *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd3db0u + (uint32_t)(iVar7 * 0x57) * 4u)))))),input);
  if (bVar1 == 0) {
    iVar10 = 0x4000;
    iVar11 = iVar10;
  }
  else {
    iVar10 = iVar6;
    if (((cVar2 != '\x01') || (-1 < iVar4)) && ((cVar3 != '\x01' || (iVar4 < 1)))) {
      iVar10 = iVar7;
    }
    iVar11 = (int)((0x100 - (uint)(*((ushort *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xb1484u + (uint32_t)((byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0xbc4))))) & 1) * 4u)))) + 0x68)))))
                   * uVar12 +
                  iVar10 * (uint)(*((ushort *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xb1484u + (uint32_t)((byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0xbc4))))) & 1) * 4u)))) + 0x68)))))
             / 0x100;
    iVar4 = (iVar11 * iVar4) / 0x4000;
  }
  iVar8 = (*((int *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd3cd8u + (uint32_t)((short)(((byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(0x1300))))) & 7) + ((byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0xbc4))))) & 1) * 8) * 0x57) * 4u)))))));
  iVar9 = iVar8;
  if ((iVar4 - iVar8 < 0 != (iVar4 < 0 != iVar8 < 0 && iVar8 < 0 == iVar4 - iVar8 < 0) ||
       iVar4 == iVar8) &&
     (iVar9 = -iVar8,
     iVar4 + iVar8 < 0 == (iVar4 < 0 != iVar9 < 0 && iVar9 < 0 == iVar4 + iVar8 < 0) &&
     iVar4 != iVar9)) {
    iVar9 = iVar4;
  }
  (*((short *)camry_host_ptr((uint32_t)(0x1228u + (int)puVar5)))) = (short)iVar6;
  (*((short *)camry_host_ptr((uint32_t)(puVar5 + 0x122a)))) = (short)iVar7;
  (*((int *)camry_host_ptr((uint32_t)(puVar5 + 0x1104)))) = iVar8;
  (*((int *)camry_host_ptr((uint32_t)(puVar5 + 0x1108)))) = iVar4;
  (*((int *)camry_host_ptr((uint32_t)(puVar5 + 0x1130)))) = iVar9;
  (*((short *)camry_host_ptr((uint32_t)(puVar5 + 0x1256)))) = (short)iVar10;
  (*((short *)camry_host_ptr((uint32_t)(puVar5 + 0x1258)))) = (short)iVar11;
  return iVar6;
}



/* Target-driven feedforward, error-driven P/I/D feedback, and direction/persistence attenuation.
   Compose target-driven feedforward, error-driven feedback and direction/persistence attenuation;
   numerical map-surface enumeration remains open. */

void f33_compose_angle_controller_terms(void)

{
  f33_update_angle_error_and_derivative();
  FUN_000cd538();
  f33_run_init_chain_cdd1e();
  FUN_000cdd42();
  FUN_000cddb6();
  FUN_000cde26();
  FUN_000cdebc();
  return;
}



/* WARNING: Removing unreachable block (ram,0x000ce07c) */
/* WARNING: Removing unreachable block (ram,0x000ce068) */

int FUN_000cdff8(void)

{
  int iVar1;
  ushort input;
  int iVar2;
  uint32_t puVar3;
  short sVar4;
  int iVar5;
  int iVar6;
  int iVar7;
  short sVar8;
  uint uVar9;
  
  input = DAT_febeae02;
  puVar3 = 0xfebeb800u;
  uVar9 = (uint)DAT_febeadbe;
  iVar7 = (int)(short)((DAT_febecb00 & 7) + (DAT_febeac3c & 1) * 8);
  if (((DAT_febeca36 == DAT_febeca82) || (DAT_febeca36 == DAT_febeca90)) ||
     (sVar8 = DAT_febeca82, DAT_febeca82 != DAT_febeca90)) {
    sVar8 = DAT_febeca36;
  }
  sVar4 = f33_abs_s16_wrapping(sVar8);
  iVar5 = f33_interpolate_signed_sentinel_curve(((short *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd3db4u + (uint32_t)(iVar7 * 0x57) * 4u)))))),sVar4);
  iVar6 = f33_interpolate_unsigned_axis_sentinel_curve
                    (((ushort *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd3db8u + (uint32_t)(iVar7 * 0x57) * 4u)))))),input);
  iVar2 = ((int)(short)iVar6 * (int)(short)iVar5) / 0x100;
  sVar4 = (*((short *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd3cdcu + (uint32_t)(iVar7 * 0x57) * 4u)))))));
  iVar7 = (int)sVar4;
  if (sVar8 < 1) {
    iVar2 = -iVar2;
  }
  iVar2 = (int)(iVar2 * uVar9) / 100;
  sVar8 = sVar4;
  if (iVar2 - iVar7 < 0 != (iVar2 < 0 != iVar7 < 0 && iVar7 < 0 == iVar2 - iVar7 < 0) ||
      iVar2 == iVar7) {
    iVar1 = -iVar7;
    if (iVar2 + iVar7 < 0 == (iVar2 < 0 != iVar1 < 0 && iVar1 < 0 == iVar2 + iVar7 < 0) &&
        iVar2 != iVar1) {
      sVar8 = (short)iVar2;
    }
    else {
      sVar8 = (short)iVar1;
    }
  }
  (*((short *)camry_host_ptr((uint32_t)(puVar3 + 0x1238)))) = (short)iVar5;
  (*((short *)camry_host_ptr((uint32_t)(puVar3 + 0x123a)))) = (short)iVar6;
  (*((short *)camry_host_ptr((uint32_t)(puVar3 + 0x123c)))) = sVar4;
  (*((int *)camry_host_ptr((uint32_t)(puVar3 + 0x1128)))) = iVar2;
  (*((short *)camry_host_ptr((uint32_t)(puVar3 + 0x123e)))) = sVar8;
  (*((short *)camry_host_ptr((uint32_t)(puVar3 + 0x127a)))) = sVar8;
  (*((short *)camry_host_ptr((uint32_t)(puVar3 + 0x1288)))) = sVar8;
  return iVar6;
}



/* WARNING: Removing unreachable block (ram,0x000ce108) */

int FUN_000ce0ae(void)

{
  int iVar1;
  undefined2 uVar2;
  short sVar3;
  uint32_t puVar4;
  short sVar5;
  short sVar6;
  int iVar7;
  int iVar8;
  int iVar9;
  
  sVar3 = DAT_febeca0a;
  puVar4 = 0xfebeb800u;
  iVar9 = (int)DAT_febeca0a;
  sVar5 = f33_abs_s16_wrapping(DAT_febeca0a);
  uVar2 = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar4 + -0x9fe))));
  sVar6 = (*((short *)camry_host_ptr((uint32_t)(puVar4 + 0x1262))));
  iVar1 = (int)(short)(((byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(0x1300))))) & 7) + ((byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0xbc4))))) & 1) * 8);
  iVar7 = FUN_000d0896(((ushort *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd3dbcu + (uint32_t)(iVar1 * 0x57) * 4u))))))), sVar5);
  iVar8 = FUN_000d0896(((ushort *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd3dc0u + (uint32_t)(iVar1 * 0x57) * 4u))))))), uVar2);
  iVar1 = (iVar7 * iVar8) / 0x100;
  iVar9 = iVar9 - sVar6;
  sVar5 = (short)iVar1;
  if (iVar9 - iVar1 < 0 == (iVar9 < 0 != iVar1 < 0 && iVar1 < 0 == iVar9 - iVar1 < 0) &&
      iVar9 != iVar1) {
    sVar6 = sVar3 - sVar5;
  }
  else if (iVar9 + iVar1 < 0 != (iVar9 < 0 != -iVar1 < 0 && -iVar1 < 0 == iVar9 + iVar1 < 0)) {
    sVar6 = sVar5 + sVar3;
  }
  (*((short *)camry_host_ptr((uint32_t)(puVar4 + 0x1262)))) = sVar6;
  (*((short *)camry_host_ptr((uint32_t)(puVar4 + 0x1260)))) = (short)iVar9;
  (*((short *)camry_host_ptr((uint32_t)(puVar4 + 0x125e)))) = sVar5;
  (*((short *)camry_host_ptr((uint32_t)(puVar4 + 0x125a)))) = (short)iVar7;
  (*((short *)camry_host_ptr((uint32_t)(puVar4 + 0x125c)))) = (short)iVar8;
  return (int)sVar6;
}



/* WARNING: Removing unreachable block (ram,0x000ce216) */
/* WARNING: Removing unreachable block (ram,0x000ce20a) */
/* Measured-rate term plus scaled feedforward/feedback. Nonzero active modes retain output and
   suppress following limiting update while unsignedAE02<128. Compose rate/feedforward/feedback;
   active nonzero modes hold output and suppress limiting update for unsignedAE02<128. */

int f33_compose_angle_controller_prelimit_output(void)

{
  byte bVar1;
  undefined1 uVar2;
  ushort uVar3;
  ushort uVar4;
  int iVar5;
  int iVar6;
  ushort uVar7;
  int iVar8;
  uint32_t puVar9;
  short sVar10;
  int iVar11;
  undefined1 uVar12;
  undefined1 uVar13;
  int iVar14;
  int iVar15;
  int iVar16;
  ushort uVar17;
  uint uVar18;
  
  uVar2 = DAT_febeca9b;
  iVar16 = DAT_febec944;
  iVar6 = DAT_febec930;
  iVar5 = DAT_febec92c;
  uVar4 = DAT_febeae02;
  uVar3 = DAT_000b060c;
  puVar9 = 0xfebeb800u;
  bVar1 = DAT_febecb00 & 7;
  uVar17 = DAT_febecb00 & 7;
  uVar7 = (ushort)DAT_febeac3c;
  iVar14 = (int)((int)(int16_t)DAT_febeca3e);
  iVar8 = (int)((int)(int16_t)DAT_febeca7a);
  if (((iVar14 == iVar8) || (iVar14 == ((int)(int16_t)DAT_febeca88))) || (iVar8 != ((int)(int16_t)DAT_febeca88))) {
    iVar8 = iVar14;
  }
  iVar15 = (int)((int)(int16_t)DAT_febeca40);
  iVar14 = (int)((int)(int16_t)DAT_febeca7e);
  if (((iVar15 == iVar14) || (iVar15 == ((int)(int16_t)DAT_febeca8c))) || (iVar14 != ((int)(int16_t)DAT_febeca8c))) {
    iVar14 = iVar15;
  }
  uVar18 = (uint)DAT_febeca64;
  sVar10 = FUN_000ce0ae();
  sVar10 = f33_abs_s16_wrapping(sVar10);
  iVar11 = FUN_000d07f2(((short *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd3dc4u + (uint32_t)((short)(uVar17 + (uVar7 & 1) * 8) * 0x57) * 4u))))))), (int)sVar10);
  iVar15 = (int)(uVar18 * (0x100 - (uint)(*((ushort *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xb1484u + (uint32_t)((byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar9 + (uint32_t)(-0xbc4))))) & 1) * 4u)))) + 0x6a))))) +
                iVar11 * (uint)(*((ushort *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xb1484u + (uint32_t)((byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar9 + (uint32_t)(-0xbc4))))) & 1) * 4u)))) + 0x6a))))) /
           0x100;
  iVar8 = iVar8 + ((iVar6 + iVar5) * iVar15) / 0x400;
  if (bVar1 == 0) {
    uVar12 = (undefined1)uVar17;
    iVar16 = iVar8;
    uVar13 = uVar12;
    uVar2 = uVar12;
  }
  else {
    uVar12 = 1;
    uVar13 = uVar12;
    if ((uVar17 != 7) && (uVar4 < uVar3)) {
      iVar16 = iVar14;
      uVar13 = 0;
    }
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar9 + (uint32_t)(0x129c))))) = uVar12;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar9 + (uint32_t)(0x129d))))) = uVar13;
  (*((int *)camry_host_ptr((uint32_t)(puVar9 + 0x1134)))) = iVar8;
  (*((int *)camry_host_ptr((uint32_t)(puVar9 + 0x1194)))) = iVar8;
  (*((int *)camry_host_ptr((uint32_t)(puVar9 + 0x11c0)))) = iVar8;
  (*((int *)camry_host_ptr((uint32_t)(puVar9 + 0x1144)))) = iVar16;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar9 + (uint32_t)(0x129b))))) = uVar2;
  (*((short *)camry_host_ptr((uint32_t)(puVar9 + 0x1234)))) = (short)iVar11;
  (*((short *)camry_host_ptr((uint32_t)(puVar9 + 0x1264)))) = (short)iVar15;
  return iVar11;
}



/* Mode7 clears controller error/PID/filter/composite states, seedsC950 from10*selected target, but
   does NOT clear finalCB38 slew history or envelope accumulatorCB04. Mode7 resets upstream
   PID/filter/composition and seeds10*selected-target memory, but leaves envelope accumulator and
   final slew history. */

void f33_reset_angle_controller_control_state(void)

{
  int iVar1;
  
  DAT_febeca9d = 1;
  DAT_febec92c = 0;
  DAT_febec8f0 = 0;
  DAT_febec9ac = 0;
  DAT_febec9d8 = 0;
  DAT_febec8f4 = 0;
  DAT_febec8f8 = 0;
  DAT_febec920 = 0;
  DAT_febec91c = 0;
  DAT_febec918 = 0;
  DAT_febec924 = 0;
  DAT_febec9b0 = 0;
  DAT_febec9dc = 0;
  DAT_febec8fc = 0;
  DAT_febec9b4 = 0;
  DAT_febec9e0 = 0;
  DAT_febec8c4 = 0;
  DAT_febec8c8 = 0;
  DAT_febec900 = 0;
  DAT_febec990 = 0;
  DAT_febec9bc = 0;
  DAT_febec908 = 0;
  DAT_febec930 = 0;
  DAT_febec928 = 0;
  DAT_febeca3e = 0;
  DAT_febeca7a = 0;
  DAT_febeca88 = 0;
  DAT_febec934 = 0;
  DAT_febec994 = 0;
  DAT_febec9c0 = 0;
  DAT_febeca9c = 0;
  DAT_febeca32 = 0;
  DAT_febec90c = 0;
  DAT_febeca36 = 0;
  DAT_febeca82 = 0;
  DAT_febeca90 = 0;
  DAT_febeca0e = 0;
  DAT_febec910 = 0;
  DAT_febec9a8 = 0;
  DAT_febec9d4 = 0;
  DAT_febec914 = 0;
  DAT_febec8d8 = 0;
  DAT_febeca1e = 0;
  DAT_febeca86 = 0;
  DAT_febeca94 = 0;
  DAT_febeca02 = 0;
  DAT_febeca08 = 0;
  DAT_febec8cc = 0;
  DAT_febec8d0 = 0;
  DAT_febec8bc = 0;
  DAT_febec9a4 = 0;
  DAT_febec9d0 = 0;
  DAT_febec8c0 = 0;
  if (((DAT_febec8b8 == DAT_febec9a0) || (DAT_febec8b8 == DAT_febec9cc)) ||
     (iVar1 = DAT_febec9a0, DAT_febec9a0 != DAT_febec9cc)) {
    iVar1 = DAT_febec8b8;
  }
  DAT_febec958 = 0;
  DAT_febeca54 = 0;
  DAT_febeca62 = 0;
  DAT_febec950 = iVar1 * 10;
  DAT_febeca58 = 0x4000;
  DAT_febeca64 = 0x400;
  return;
}



void FUN_000ce384(void)

{
  if ((DAT_febecb00 & 7) == 7) {
    f33_reset_angle_controller_control_state();
  }
  else {
    f33_compose_angle_controller_terms();
    FUN_000cdff8();
    f33_compose_angle_controller_prelimit_output();
  }
  return;
}



/* WARNING: Removing unreachable block (ram,0x000ce3fe) */
/* WARNING: Removing unreachable block (ram,0x000ce442) */

void FUN_000ce3aa(void)

{
  int iVar1;
  uint uVar2;
  uint uVar3;
  
  if (((DAT_febec934 == DAT_febec994) || (DAT_febec934 == DAT_febec9c0)) ||
     (iVar1 = DAT_febec994, DAT_febec994 != DAT_febec9c0)) {
    iVar1 = DAT_febec934;
  }
  uVar2 = (uint)DAT_febeadbd;
  uVar3 = uVar2;
  if (DAT_000b05c2 < uVar2) {
    uVar3 = (uint)DAT_000b05c2;
  }
  if (uVar2 == 0xc9) {
    uVar3 = (uint)(*((ushort *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xb146cu + (uint32_t)(DAT_febeac3c & 1) * 4u)))) + 0x8e))));
  }
  else if (uVar2 == 0xca) {
    uVar3 = (uint)(*((ushort *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xb146cu + (uint32_t)(DAT_febeac3c & 1) * 4u)))) + 0x90))));
  }
  else {
    if (uVar2 != 0xcb) {
      DAT_febec940 = (int)(iVar1 * uVar3) / 100;
      DAT_febec998 = DAT_febec940;
      DAT_febec9c4 = DAT_febec940;
      return;
    }
    uVar3 = (uint)(*((ushort *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xb146cu + (uint32_t)(DAT_febeac3c & 1) * 4u)))) + 0x92))));
  }
  DAT_febec940 = iVar1 - (uVar3 * 0xa4) / 0x3200;
  DAT_febec998 = DAT_febec940;
  DAT_febec9c4 = DAT_febec940;
  return;
}



uint FUN_000ce454(undefined2 param_1)

{
  return FUN_000d0896(((ushort *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd3dc8u + (uint32_t)((short)((DAT_febecb00 & 7) + (DAT_febeac3c & 1) * 8) * 0x57) * 4u))))))), 
               param_1);
}



uint FUN_000ce486(undefined2 param_1)

{
  return FUN_000d0896(((ushort *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd3dccu + (uint32_t)((short)((DAT_febeca9f & 7) + (DAT_febeac3c & 1) * 8) * 0x57) * 4u))))))), 
               param_1);
}



void FUN_000ce4b8(undefined2 param_1)

{
  if ((DAT_febecb00 & 7) - 1 < 5) {
    FUN_000ce454((uint)(ushort)param_1);
  }
  else {
    FUN_000ce486(param_1);
  }
  return;
}



void FUN_000ce51c(void)

{
  byte bVar1;
  byte bVar2;
  ushort input;
  char cVar3;
  ushort uVar4;
  uint32_t puVar5;
  int iVar6;
  ushort uVar7;
  bool bVar8;
  
  bVar2 = DAT_febecaac;
  cVar3 = DAT_febeca9e;
  input = DAT_febeae02;
  puVar5 = 0xfebeb800u;
  if (DAT_febeca9d == '\x01') {
    uVar7 = DAT_febecb00 & 7;
    uVar4 = (ushort)DAT_febeca9f;
    bVar1 = DAT_febeca9f & 7;
    FUN_000ce3aa();
    if ((cVar3 != '\0') ||
       ((bVar8 = false, uVar7 != (uVar4 & 7) && (bVar8 = true, bVar2 = bVar1, uVar7 == 7)))) {
      bVar8 = bVar2 != 0;
    }
    FUN_000ce4da(bVar8,input);
    iVar6 = f33_interpolate_unsigned_axis_sentinel_curve
                      (((ushort *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd3dd4u + (uint32_t)((short)(uVar7 + ((byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0xbc4))))) & 1) * 8) * 0x57) * 4u)))))),
                       input);
    (*((short *)camry_host_ptr((uint32_t)(puVar5 + 0x1244)))) = (short)iVar6;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(0x129e))))) = bVar8;
  }
  return;
}



void FUN_000ce6cc(void)

{
  uint32_t puVar1;
  byte bVar2;
  
  puVar1 = 0xfebeb800u;
  bVar2 = DAT_febecb00 & 7;
  FUN_000cd046();
  f33_filter_angle_controller_measured_rate();
  FUN_000ce384();
  FUN_000ce51c();
  f33_limit_angle_controller_output();
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x129f))))) = bVar2;
  return;
}



/* WARNING: Removing unreachable block (ram,0x000ce73c) */
/* VoteCA46/7C/8A and apply sign-selected curve/1024 intoCA2E/80/8E. Vote controller output and
   apply sign-selected curve scaling before target publication; ordinary knot factors1024 are not
   universal curve replacement. */

int f33_shape_angle_controller_target(void)

{
  short value;
  uint32_t puVar1;
  short *points;
  short input;
  int iVar2;
  undefined2 uVar3;
  
  puVar1 = 0xfebeb800u;
  if (((DAT_febeca46 == DAT_febeca7c) || (DAT_febeca46 == DAT_febeca8a)) ||
     (value = DAT_febeca7c, DAT_febeca7c != DAT_febeca8a)) {
    value = DAT_febeca46;
  }
  input = f33_abs_s16_wrapping(value);
  if (value < 0) {
    points = (short *)((undefined *)camry_host_ptr(0xb05e8u));
  }
  else {
    points = (short *)((undefined *)camry_host_ptr(0xb05c4u));
  }
  iVar2 = f33_interpolate_signed_sentinel_curve(points,input);
  (*((short *)camry_host_ptr((uint32_t)(0x1228u + (int)(puVar1 + 4))))) = (short)iVar2;
  uVar3 = (undefined2)(((int)(short)iVar2 * (int)value) / 0x400);
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + 0x122e)))) = uVar3;
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + 0x1280)))) = uVar3;
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + 0x128e)))) = uVar3;
  return iVar2;
}



/* Constant-block fill: 8 literal assignments into one contiguous cell block; shape-verified.
   Literals are default/reset values; cell meanings are not recovered. */

void f33_fill_constant_block_ce750(void)

{
  DAT_febecaae = 0;
  DAT_febecab2 = 0;
  DAT_febecab3 = 0;
  DAT_febecab4 = 0;
  DAT_febecab0 = 0;
  DAT_febecab5 = 0;
  DAT_febecab6 = 0;
  DAT_febecab7 = 0;
  return;
}



char FUN_000ce772(char param_1)

{
  if ((((param_1 == '\0') && (DAT_febeaccc == '\0')) && (DAT_febeaccd == '\0')) &&
     (((DAT_febeadbf < 2 && (DAT_febecafc == '\0')) && (DAT_febecad9 == '\0')))) {
    param_1 = '\x01';
  }
  return param_1;
}



char FUN_000ce7a6(char param_1)

{
  if ((param_1 == '\x01') && (DAT_febeaccd != '\0')) {
    DAT_febecaae = DAT_febecaae + 1;
  }
  else {
    DAT_febecaae = 0;
    if (param_1 != '\x01') {
      DAT_febecaae = 0;
      return param_1;
    }
  }
  if ((((DAT_febeaccc != '\0') || (DAT_000b060e < DAT_febecaae)) ||
      (DAT_febeadbf == '\x02' || DAT_febeadbf == '\x03')) ||
     ((DAT_febecafc == '\x01' || (DAT_febecad9 == '\x01')))) {
    param_1 = '\0';
    DAT_febecaae = 0;
  }
  return param_1;
}



void FUN_000ce7fe(void)

{
  uint32_t puVar1;
  char cVar2;
  undefined1 uVar3;
  undefined4 uVar4;
  
  puVar1 = 0xfebeb800u;
  if (((DAT_febecab2 == DAT_febecab3) || (DAT_febecab2 == DAT_febecab4)) ||
     (cVar2 = DAT_febecab3, DAT_febecab3 != DAT_febecab4)) {
    cVar2 = DAT_febecab2;
  }
  uVar4 = FUN_000ce772(cVar2);
  uVar3 = FUN_000ce7a6(uVar4);
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x12b2))))) = uVar3;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x12b3))))) = uVar3;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x12b4))))) = uVar3;
  return;
}



void FUN_000ce836(void)

{
  char cVar1;
  
  if (((DAT_febecab2 == DAT_febecab3) || (DAT_febecab2 == DAT_febecab4)) ||
     (cVar1 = DAT_febecab3, DAT_febecab3 != DAT_febecab4)) {
    cVar1 = DAT_febecab2;
  }
  if (DAT_febecab7 == '\0') {
    if (((cVar1 == '\x01') && ((DAT_febecb00 & 7) != 7)) && (DAT_febecab6 == '\0')) {
      DAT_febecab5 = 0x11;
      DAT_febecab7 = 1;
      return;
    }
  }
  else {
    if (cVar1 == '\0') {
      DAT_febecab5 = 0x44;
      DAT_febecab7 = '\0';
      goto LAB_000ce8a6;
    }
    if ((DAT_febecb00 & 7) == 7) {
      DAT_febecab7 = '\0';
      DAT_febecab5 = 0x22;
    }
  }
  if (DAT_febecab6 != '\x01') {
    return;
  }
LAB_000ce8a6:
  DAT_febecab6 = true;
  if (DAT_febecab0 <= DAT_000b0610) {
    DAT_febecab0 = DAT_febecab0 + 1;
    DAT_febecab6 = DAT_febecab0 <= DAT_000b0610;
    if (DAT_000b0610 < DAT_febecab0) {
      DAT_febecab0 = 0;
    }
  }
  return;
}



void FUN_000ce8ca(void)

{
  FUN_000ce7fe();
  FUN_000ce836();
  return;
}



/* Generic retained unsigned gain step used by eight producers. Direction2 and current>=down_target
   select bounded subtraction; otherwise step toward up_target. Write only current at+8; not a
   torque-specific policy or elapsed-time controller. Generic unsigned retained gain stepping uses
   direction2/current>=down_target for bounded subtraction and otherwise bounded upward/default
   selection. Eight caller preparation leaves preserve the actual state pointer. */

void f33_step_retained_unsigned_gain(F33GainSlewState *state)

{
  int iVar1;
  ushort uVar2;
  ushort uVar3;
  ushort uVar4;
  uint uVar5;
  
  uVar2 = state->current;
  uVar5 = (uint)uVar2;
  uVar4 = state->down_target;
  if ((uVar5 < uVar4) || (state->direction != '\x02')) {
    uVar4 = state->up_target;
    uVar3 = state->up_step;
    uVar5 = uVar4 - uVar5;
    iVar1 = uVar5 - uVar3;
    if (iVar1 < 0 == ((int)uVar5 < 0 && -1 < iVar1) && uVar5 != uVar3) {
      uVar4 = uVar2 + uVar3;
    }
  }
  else {
    uVar3 = state->down_step;
    uVar5 = uVar5 - uVar4;
    iVar1 = uVar5 - uVar3;
    if (iVar1 < 0 == ((int)uVar5 < 0 && -1 < iVar1) && uVar5 != uVar3) {
      uVar4 = uVar2 - uVar3;
    }
  }
  state->current = uVar4;
  return;
}



void FUN_000ce912(char *param_1)

{
  bool bVar1;
  int iVar2;
  uint32_t puVar3;
  short sVar4;
  undefined2 uVar5;
  int iVar6;
  
  puVar3 = 0xfebeb800u;
  sVar4 = f33_abs_s16_wrapping(*(short *)(param_1 + 0x10));
  iVar6 = (int)sVar4;
  iVar2 = (int)**(short **)(param_1 + 4);
  if (iVar6 - iVar2 < 0 != (iVar6 < 0 != iVar2 < 0 && iVar2 < 0 == iVar6 - iVar2 < 0)) {
    bVar1 = false;
    if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(0x12b7))))) == '\x01') {
      bVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(0x1300))))) == *param_1;
    }
    param_1[0xc] = bVar1;
  }
  uVar5 = 0x400;
  if (param_1[0xc] == '\x01') {
    uVar5 = FUN_000d07f2(((short *)camry_host_ptr((uint32_t)(*(undefined4 *)(param_1 + 8)))), iVar6);
  }
  *(undefined2 *)(param_1 + 0xe) = uVar5;
  return;
}



/* Constant-block fill: 17 literal assignments into one contiguous cell block; shape-verified.
   Literals are default/reset values; cell meanings are not recovered. */

void f33_fill_constant_block_ce964(void)

{
  DAT_febecabc = 0;
  DAT_febecac0 = 0;
  DAT_febecac4 = 0;
  DAT_febecab8 = 0;
  DAT_febecaca = 0;
  DAT_febecacc = 0;
  DAT_febecacb = 0;
  DAT_febecace = 0;
  DAT_febecad0 = 0;
  DAT_febecad8 = 0;
  DAT_febecacd = 0;
  DAT_febecacf = 0;
  DAT_febecad2 = 0;
  DAT_febecad4 = 0;
  DAT_febecad6 = 0;
  DAT_febecac8 = 0;
  DAT_febecad9 = 1;
  return;
}



void FUN_000ce9ac(void)

{
  if ((DAT_febeacc4 == '\0') && (DAT_febecafe == '\x01')) {
    DAT_febecaca = DAT_febeacbd == '\0';
  }
  else {
    DAT_febecaca = false;
  }
  return;
}



void FUN_000ce9d0(void)

{
  DAT_febecacc = DAT_febecaff == '\x01' && DAT_febeacbd == '\0';
  return;
}



/* Saturate2*AE5E-voted(CABC/CAC0/CAC4) to signed16 including-32768; publishCAD2/4/6 when qualified.
   Qualified2*AE5E minus voted offset saturates to signed16 including-32768 and publishesCAD2/4/6.
    */

void f33_publish_offset_corrected_angle_feedback(void)

{
  char cVar1;
  int iVar2;
  
  if (((DAT_febecacb == DAT_febecace) || (DAT_febecacb == DAT_febecad0)) ||
     (cVar1 = DAT_febecace, DAT_febecace != DAT_febecad0)) {
    cVar1 = DAT_febecacb;
  }
  if (((DAT_febecabc == DAT_febecac0) || (DAT_febecabc == DAT_febecac4)) ||
     (iVar2 = DAT_febecac0, DAT_febecac0 != DAT_febecac4)) {
    iVar2 = DAT_febecabc;
  }
  if (((DAT_febecad8 == DAT_febecacd) || (DAT_febecad8 == DAT_febecacf)) ||
     (DAT_febecacd != DAT_febecacf)) {
    DAT_febecacd = DAT_febecad8;
  }
  if ((DAT_febead4c == '\0') && (cVar1 == '\x01')) {
    if (DAT_febecacd == '\0') {
      DAT_febecacd = '\x01';
    }
    iVar2 = DAT_febeae5e * 2 - iVar2;
    if (iVar2 + -0x7fff < 0 == (iVar2 < 0 && -1 < iVar2 + -0x7fff) && iVar2 != 0x7fff) {
      DAT_febecad2 = 0x7fff;
      DAT_febecad4 = DAT_febecad2;
      DAT_febecad6 = DAT_febecad2;
    }
    else if (iVar2 + 0x8000 < 0 == (-1 < iVar2 && iVar2 + 0x8000 < 0)) {
      DAT_febecad2 = (undefined2)iVar2;
      DAT_febecad4 = DAT_febecad2;
      DAT_febecad6 = DAT_febecad2;
    }
    else {
      DAT_febecad2 = 0x8000;
      DAT_febecad4 = DAT_febecad2;
      DAT_febecad6 = DAT_febecad2;
    }
  }
  else {
    DAT_febecacd = '\0';
  }
  DAT_febecad8 = DAT_febecacd;
  DAT_febecacf = DAT_febecacd;
  return;
}



/* Compose qualified offset capture and corrected feedback; lost qualification may hold last
   feedback. Qualified offset acquisition and corrected feedback publication are distinct; loss of
   qualification can hold previous feedback. */

void f33_update_angle_feedback_offset_and_publication(void)

{
  FUN_000ce9ac();
  FUN_000ce9d0();
  FUN_000ce9ea();
  f33_publish_offset_corrected_angle_feedback();
  return;
}



void FUN_000ceb92(void)

{
  int iVar1;
  bool bVar2;
  int iVar3;
  uint32_t puVar4;
  int iVar5;
  undefined1 uVar6;
  ushort uVar7;
  
  uVar6 = DAT_febecad9;
  uVar7 = DAT_febecac8;
  iVar1 = DAT_000b0614;
  puVar4 = 0xfebeb800u;
  iVar5 = (int)DAT_febecad2;
  iVar3 = (int)DAT_febecad4;
  if (((iVar5 == iVar3) || (iVar5 == DAT_febecad6)) || (iVar3 != DAT_febecad6)) {
    iVar3 = iVar5;
  }
  iVar5 = DAT_000b0614 * 2;
  if ((DAT_febead4c == '\0') && (DAT_febecaca == '\x01')) {
    puVar4 = 0xfebeb800u;
    iVar3 = f33_abs_s32_wrapping(iVar3 - DAT_febecab8);
    iVar1 = iVar3 + iVar1 * -2;
    bVar2 = iVar5 < 0;
    if (iVar1 < 0 == (iVar3 < 0 != bVar2 && bVar2 == iVar1 < 0)) {
      if (uVar7 < DAT_000b0618) {
        uVar7 = uVar7 + 1;
      }
      else {
        uVar6 = 1;
      }
    }
    else {
      uVar6 = 0;
      uVar7 = 0;
    }
  }
  else {
    uVar6 = 1;
    uVar7 = 0;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(0x12d9))))) = uVar6;
  (*((ushort *)camry_host_ptr((uint32_t)(puVar4 + 0x12c8)))) = uVar7;
  return;
}



/* Constant-block fill: 25 literal assignments into one contiguous cell block; shape-verified.
   Literals are default/reset values; cell meanings are not recovered. */

void f33_fill_constant_block_cec0c(void)

{
  DAT_febecafc = 0;
  DAT_febecada = 0;
  DAT_febecadc = 0;
  DAT_febecade = 0;
  DAT_febecaf4 = 0;
  DAT_febecae0 = 0;
  DAT_febecae2 = 0;
  DAT_febecae4 = 0;
  DAT_febecaf5 = 0;
  DAT_febecaf6 = 0;
  DAT_febecaf7 = 0;
  DAT_febecaf8 = 0;
  DAT_febecaf9 = 0;
  DAT_febecae6 = 0;
  DAT_febecae8 = 0;
  DAT_febecafa = 0;
  DAT_febecafb = 0;
  DAT_febecaea = 0;
  DAT_febecaec = 0;
  DAT_febecaee = 0;
  DAT_febecaf0 = 0;
  DAT_febecaf2 = 0;
  DAT_febecafd = 0;
  DAT_febecafe = 0;
  DAT_febecaff = 0;
  return;
}



void FUN_000cec72(void)

{
  DAT_febecafc = DAT_febecafb == '\x01' || DAT_febecafd == '\x01';
  return;
}



void FUN_000cec8a(void)

{
  int iVar1;
  int iVar2;
  
  iVar1 = (int)(short)DAT_febecada;
  if ((int)((uint)DAT_febeadbc - iVar1) < 0 ==
      (iVar1 < 0 && iVar1 < 0 == (int)((uint)DAT_febeadbc - iVar1) < 0)) {
    DAT_febecadc = DAT_febeadbc - DAT_febecada;
  }
  else {
    DAT_febecadc = DAT_000b0620 + (DAT_febeadbc - DAT_febecada) + 1;
  }
  DAT_febecada = (ushort)DAT_febeadbc;
  iVar1 = (int)DAT_febecadc;
  if (iVar1 + -1 < 0 == (iVar1 < 0 && -1 < iVar1 + -1) && iVar1 != 1) {
    iVar2 = (int)DAT_000b0622;
    DAT_febecade = DAT_febecadc;
    if (iVar1 - iVar2 < 0 == (iVar1 < 0 != iVar2 < 0 && iVar2 < 0 == iVar1 - iVar2 < 0)) {
      DAT_febecade = DAT_000b0622;
    }
  }
  else {
    DAT_febecade = 1;
  }
  return;
}



void FUN_000cecd6(void)

{
  if (((DAT_febecb00 & 7) == 7) || (DAT_febeacd6 != '\x01')) {
    DAT_febecaf4 = 0;
    DAT_febecaf5 = false;
    DAT_febecae0 = 0;
  }
  else {
    if (DAT_febecae0 < (*((ushort *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xb146cu + (uint32_t)(DAT_febeac3c & 1) * 4u)))) + 2))))) {
      DAT_febecae0 = DAT_febecae0 + 1;
    }
    DAT_febecaf5 = (*((ushort *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xb146cu + (uint32_t)(DAT_febeac3c & 1) * 4u)))) + 2)))) <= DAT_febecae0;
    DAT_febecaf4 = 1;
  }
  return;
}



short FUN_000ced28(void)

{
  undefined1 uVar1;
  ushort uVar2;
  uint32_t puVar3;
  short sVar4;
  int iVar6;
  bool bVar7;
  ushort uVar8;
  int iVar5;
  
  uVar8 = DAT_febecae2;
  puVar3 = 0xfebeb800u;
  uVar2 = (ushort)DAT_febecb00;
  sVar4 = f33_abs_s16_wrapping(DAT_febeae22);
  iVar5 = (int)sVar4;
  iVar6 = (int)(*((short *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd3dd8u + (uint32_t)((short)((uVar2 & 7) + (short)(((byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0xbc4))))) & 1) << 3)) * 0x57) * 4u)))))));
  if (((uVar2 & 7) == 7) ||
     (iVar5 - iVar6 < 0 != (iVar5 < 0 != iVar6 < 0 && iVar6 < 0 == iVar5 - iVar6 < 0) ||
      iVar5 == iVar6)) {
    uVar1 = 0;
    bVar7 = false;
    uVar8 = 0;
  }
  else {
    uVar1 = 1;
    if (uVar8 < (*((ushort *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xb146cu + (uint32_t)((byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0xbc4))))) & 1) * 4u)))) + 8))))) {
      uVar8 = uVar8 + 1;
    }
    bVar7 = (*((ushort *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xb146cu + (uint32_t)((byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0xbc4))))) & 1) * 4u)))) + 8)))) <= uVar8;
  }
  (*((short *)camry_host_ptr((uint32_t)(puVar3 + 0x12e4)))) =
       (*((short *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd3dd8u + (uint32_t)((short)((uVar2 & 7) + (short)(((byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0xbc4))))) & 1) << 3)) * 0x57) * 4u)))))));
  (*((ushort *)camry_host_ptr((uint32_t)(puVar3 + 0x12e2)))) = uVar8;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(0x12f6))))) = uVar1;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(0x12f7))))) = bVar7;
  return sVar4;
}



short FUN_000ceda4(void)

{
  int iVar1;
  short sVar2;
  undefined1 uVar3;
  ushort uVar4;
  uint32_t puVar5;
  short sVar6;
  int iVar7;
  bool bVar8;
  ushort uVar9;
  
  uVar9 = DAT_febecae6;
  puVar5 = 0xfebeb800u;
  uVar4 = (ushort)DAT_febecb00;
  sVar6 = f33_abs_s16_wrapping(DAT_febeae24);
  sVar2 = (*((short *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd3ddcu + (uint32_t)((short)((uVar4 & 7) + (short)(((byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0xbc4))))) & 1) << 3)) * 0x57) * 4u)))))));
  iVar7 = (int)sVar2;
  if (((uVar4 & 7) == 7) ||
     (iVar1 = sVar6 - iVar7, iVar1 < 0 == (sVar6 < 0 != iVar7 < 0 && iVar7 < 0 == iVar1 < 0))) {
    uVar3 = 0;
    bVar8 = false;
    uVar9 = 0;
  }
  else {
    uVar3 = 1;
    if (uVar9 < (*((ushort *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xb146cu + (uint32_t)((byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0xbc4))))) & 1) * 4u)))) + 0xe))))) {
      uVar9 = uVar9 + 1;
    }
    bVar8 = (*((ushort *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xb146cu + (uint32_t)((byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0xbc4))))) & 1) * 4u)))) + 0xe)))) <= uVar9;
  }
  (*((short *)camry_host_ptr((uint32_t)(puVar5 + 0x12e8)))) = sVar2;
  (*((ushort *)camry_host_ptr((uint32_t)(puVar5 + 0x12e6)))) = uVar9;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(0x12f8))))) = uVar3;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(0x12f9))))) = bVar8;
  return sVar6;
}



void FUN_000cee20(void)

{
  undefined1 uVar1;
  uint32_t puVar2;
  puVar2 = 0xfebeb800u;
  FUN_000ced28();
  FUN_000ceda4();
  if (((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(0x12f7))))) != '\x01') || (uVar1 = 1, (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(0x12f9))))) != '\x01')) {
    uVar1 = 0;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(0x12fa))))) = uVar1;
  return;
}



void FUN_000cee46(void)

{
  int iVar1;
  
  iVar1 = (int)(short)((DAT_febecb00 & 7) + (DAT_febeac3c & 1) * 8);
  DAT_febecaea = (*((undefined2 *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd3de0u + (uint32_t)(iVar1 * 0x57) * 4u)))))));
  DAT_febecaec = (*((undefined2 *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd3de4u + (uint32_t)(iVar1 * 0x57) * 4u)))))));
  return;
}



/* WARNING: Removing unreachable block (ram,0x000ceec2) */

void FUN_000cee7c(void)

{
  int iVar1;
  int iVar2;
  short sVar3;
  short sVar4;
  short sVar5;
  char cVar6;
  char cVar7;
  char cVar8;
  ushort uVar9;
  ushort uVar10;
  uint uVar11;
  uint32_t puVar12;
  uint uVar13;
  int iVar14;
  byte bVar15;
  undefined1 uVar16;
  
  puVar12 = 0xfebeb800u;
  bVar15 = DAT_febecb00 & 7;
  FUN_000cee46();
  uVar11 = DAT_000b061c;
  sVar3 = (*((short *)camry_host_ptr((uint32_t)(puVar12 + 0x12de))));
  sVar4 = (*((short *)camry_host_ptr((uint32_t)(puVar12 + -0x970))));
  sVar5 = (*((short *)camry_host_ptr((uint32_t)(puVar12 + 0x12a4))));
  cVar6 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar12 + (uint32_t)(0x12b6)))));
  cVar7 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar12 + (uint32_t)(0x12fa)))));
  cVar8 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar12 + (uint32_t)(0x12f5)))));
  uVar16 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar12 + (uint32_t)(0x12fb)))));
  uVar9 = (*((ushort *)camry_host_ptr((uint32_t)(puVar12 + 0x12ea))));
  uVar10 = (*((ushort *)camry_host_ptr((uint32_t)(puVar12 + 0x12ec))));
  uVar13 = f33_abs_s32_wrapping((int)sVar4);
  iVar14 = f33_abs_s32_wrapping((int)sVar4 - (int)sVar5 / 2);
  iVar2 = (int)sVar3 * (uint)uVar10;
  if (bVar15 != 7) {
    if (cVar6 != '\0') goto LAB_000cef06;
    if (((cVar7 == '\x01') || (cVar8 == '\x01')) ||
       (iVar1 = uVar13 - uVar9, iVar1 < 0 == ((int)uVar13 < 0 && -1 < iVar1) && uVar13 != uVar9)) {
      uVar16 = 1;
      goto LAB_000cef06;
    }
    if ((int)(uVar13 - uVar11) < 0 ==
        ((int)uVar13 < 0 != (int)uVar11 < 0 && (int)uVar11 < 0 == (int)(uVar13 - uVar11) < 0) &&
        uVar13 != uVar11) {
      uVar16 = iVar14 - iVar2 < 0 == (iVar14 < 0 != iVar2 < 0 && iVar2 < 0 == iVar14 - iVar2 < 0) &&
               iVar14 != iVar2;
      goto LAB_000cef06;
    }
  }
  uVar16 = 0;
LAB_000cef06:
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar12 + (uint32_t)(0x12fb))))) = uVar16;
  return;
}



/* Sequential initializer chain: 4 unconditional calls and no other statements; shape-verified. The
   called sequence is the function's entire behavior; chain family members differ in callee sets. */

void f33_run_init_chain_cef0e(void)

{
  FUN_000cec8a();
  FUN_000cecd6();
  FUN_000cee20();
  FUN_000cee7c();
  return;
}



void FUN_000cef26(void)

{
  int iVar1;
  ushort uVar2;
  ushort uVar3;
  char cVar4;
  short sVar5;
  ushort uVar6;
  uint32_t puVar7;
  ushort uVar8;
  char cVar9;
  
  cVar9 = DAT_febecafd;
  sVar5 = DAT_febecaf2;
  cVar4 = DAT_febecab6;
  puVar7 = 0xfebeb800u;
  uVar6 = (ushort)DAT_febecb00;
  uVar8 = f33_abs_s16_wrapping(((int)(int16_t)DAT_febeae24));
  iVar1 = (int)(short)((uVar6 & 7) + ((byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar7 + (uint32_t)(-0xbc4))))) & 1) * 8);
  uVar2 = (*((ushort *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd3de8u + (uint32_t)(iVar1 * 0x57) * 4u)))))));
  uVar3 = (*((ushort *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd3decu + (uint32_t)(iVar1 * 0x57) * 4u)))))));
  if (((((uVar6 & 7) == 7) || (cVar4 != '\0')) || (cVar9 == '\x01')) || (uVar8 < uVar2)) {
    uVar6 = 0;
  }
  else {
    uVar6 = sVar5 + 1;
    if (uVar3 <= uVar6) {
      uVar6 = 0;
      cVar9 = '\x01';
    }
  }
  (*((ushort *)camry_host_ptr((uint32_t)(puVar7 + 0x12f2)))) = uVar6;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar7 + (uint32_t)(0x12fd))))) = cVar9;
  (*((ushort *)camry_host_ptr((uint32_t)(puVar7 + 0x12ee)))) = uVar2;
  (*((ushort *)camry_host_ptr((uint32_t)(puVar7 + 0x12f0)))) = uVar3;
  return;
}



void FUN_000cefa4(void)

{
  bool bVar1;
  uint32_t puVar2;
  byte bVar3;
  byte bVar4;
  
  puVar2 = 0xfebeb800u;
  bVar3 = f33_get_application_grouped_status(0x11);
  bVar4 = f33_get_application_grouped_status(0x1a);
  bVar1 = (bVar3 | bVar4) != 0x5a;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(0x12ff))))) = bVar1 && (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0xa47))))) == '\0';
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(0x12fe))))) = bVar1 && (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0xb3f))))) == '\0';
  return;
}



/* Far-call trampoline: prepare {lp},0 / jarl 0xCEFA4 / dispose 0,{lp},lp; byte-verified against the
   exact image. Forwards with registers and stack unchanged; marked as a thunk. Forwarding shape
   machine-verified; target semantics not recovered. */

void thunk_FUN_000cefa4(void)

{
  FUN_000cefa4();
  return;
}



/* Single constant publisher: DAT_febecb00 = 7; Shape-classified from the canonical corpus; the
   target cell is not yet named, so the written state's meaning is unknown. */

void FUN_000ceff4(void)

{
  DAT_febecb00 = 7;
  return;
}



/* DefaultCB00=7. RequireACBD0/CAFF1; ADB0 values1/4/11/10/19/18 map modes0..5. Effective angle mode
   defaults7; ACBD0/CAFF1 admit ADB0 mapping1/4/11/10/19/18 to0..5. */

void f33_select_angle_controller_mode(void)

{
  DAT_febecb00 = 7;
  if ((DAT_febeacbd == '\0') && (DAT_febecaff == '\x01')) {
    if (DAT_febeadb0 == '\x01') {
      DAT_febecb00 = 0;
    }
    else if (DAT_febeadb0 == '\x04') {
      DAT_febecb00 = 1;
    }
    else if (DAT_febeadb0 == '\n') {
      DAT_febecb00 = 3;
    }
    else if (DAT_febeadb0 == '\v') {
      DAT_febecb00 = 2;
    }
    else if (DAT_febeadb0 == '\x12') {
      DAT_febecb00 = 5;
    }
    else if (DAT_febeadb0 == '\x13') {
      DAT_febecb00 = 4;
    }
  }
  return;
}



void FUN_000cf04a(void)

{
  f33_select_angle_controller_mode();
  return;
}



void FUN_000cf056(void)

{
  f33_angle_controller_envelope_parameters[1] = 1;
  f33_angle_controller_envelope_parameters[2] = 1;
  f33_angle_controller_envelope_parameters[3] = 1;
  f33_angle_controller_envelope_parameters[5] = 1;
  f33_angle_controller_envelope_parameters[0] = 0;
  f33_angle_controller_envelope_parameters[4] = 0;
  f33_angle_controller_envelope_accumulator = 0;
  DAT_febecb08 = 0;
  DAT_febecb0c = 0;
  DAT_febecb10 = 0;
  f33_angle_controller_envelope_parameters[6] = 0;
  f33_angle_controller_envelope_parameters[7] = 0;
  DAT_febecb14 = 0;
  DAT_febecb18 = 0;
  DAT_febecb1c = 0;
  DAT_febecb38 = 0;
  DAT_febecb30 = 0;
  DAT_febecb32 = 0;
  DAT_febecb34 = 0x22;
  DAT_febecb35 = 0x22;
  DAT_febecb36 = 0;
  DAT_febecb3a = 0;
  return;
}



void FUN_000cf0b6(void)

{
  DAT_febecb35 = DAT_febecb34;
  if ((DAT_febecab5 == '\x11') || (DAT_febec862 == '\x01')) {
    DAT_febecb34 = 0x11;
  }
  else {
    DAT_febecb34 = 0x22;
    if (DAT_febecab5 == 'D') {
      DAT_febecb34 = 0x33;
    }
  }
  return;
}



void FUN_000cf0ea(void)

{
  int iVar1;
  
  iVar1 = (int)(short)((DAT_febecb00 & 7) + (DAT_febeac3c & 1) * 8);
  if ((DAT_febecb00 & 7) != 7) {
    f33_angle_controller_envelope_parameters[1] = *(ushort *)(((undefined *)camry_host_ptr(0xd3df4u)) + iVar1 * 0x15c);
    f33_angle_controller_envelope_parameters[2] = (*((ushort *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd3df8u + (uint32_t)(iVar1 * 0x57) * 4u)))))));
    f33_angle_controller_envelope_parameters[3] = (*((ushort *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd3dfcu + (uint32_t)(iVar1 * 0x57) * 4u)))))));
    f33_angle_controller_envelope_parameters[4] = (*((ushort *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd3df0u + (uint32_t)(iVar1 * 0x57) * 4u)))))));
  }
  return;
}



/* Unsigned accumulator rescaled when denominator changes; denominator floor1. Mode11 rises,22/33
   decay. Inclusive snap boundaries256-H/H. Consistent retained state supports0..256; arbitrary
   corrupt accumulator is not universally clamped. Unsigned retained envelope rescales on
   denominator change, then rises/decays with inclusive snap boundaries; valid gain bounds depend on
   consistent retained state. */

void f33_update_angle_controller_retained_envelope(void)

{
  int iVar1;
  uint uVar2;
  uint uVar3;
  uint uVar4;
  uint uVar5;
  uint uVar6;
  uint uVar7;
  
  uVar7 = (uint)f33_angle_controller_envelope_parameters[0];
  uVar2 = (uint)f33_angle_controller_envelope_parameters[4];
  uVar5 = (uint)f33_angle_controller_envelope_parameters[1];
  uVar4 = (uint)f33_angle_controller_envelope_parameters[2];
  uVar3 = (uint)f33_angle_controller_envelope_parameters[3];
  uVar6 = (uint)f33_angle_controller_envelope_parameters[5];
  if (uVar5 < 2) {
    uVar5 = 1;
  }
  if (uVar4 < 2) {
    uVar4 = 1;
  }
  if (uVar3 < 2) {
    uVar3 = 1;
  }
  if (DAT_febecb34 == '\x11') {
    if (uVar5 != uVar6) {
      if (uVar6 == 0) {
        f33_angle_controller_envelope_accumulator = uVar7 * uVar5;
      }
      else {
        f33_angle_controller_envelope_accumulator =
             f33_angle_controller_envelope_accumulator * uVar5;
        if (uVar6 != 0) {
          f33_angle_controller_envelope_accumulator =
               f33_angle_controller_envelope_accumulator / uVar6;
        }
      }
    }
    f33_angle_controller_envelope_accumulator =
         (f33_angle_controller_envelope_accumulator + 0x100) - uVar7;
    iVar1 = 0x100 - uVar2;
    f33_angle_controller_envelope_parameters[5] = (ushort)uVar5;
    uVar7 = f33_angle_controller_envelope_accumulator;
    if (uVar5 != 0) {
      uVar7 = f33_angle_controller_envelope_accumulator / uVar5;
    }
    uVar7 = uVar7 & 0xffff;
    if ((int)(uVar7 - iVar1) < 0 == (iVar1 < 0 && iVar1 < 0 == (int)(uVar7 - iVar1) < 0)) {
      uVar7 = 0x100;
      f33_angle_controller_envelope_accumulator = uVar5 << 8;
    }
    goto LAB_000cf21e;
  }
  if (DAT_febecb34 == '\"') {
    if (uVar4 != uVar6) {
      if (uVar6 == 0) {
        f33_angle_controller_envelope_accumulator = uVar7 * uVar4;
      }
      else {
        f33_angle_controller_envelope_accumulator =
             f33_angle_controller_envelope_accumulator * uVar4;
        if (uVar6 != 0) {
          f33_angle_controller_envelope_accumulator =
               f33_angle_controller_envelope_accumulator / uVar6;
        }
      }
    }
    f33_angle_controller_envelope_accumulator = f33_angle_controller_envelope_accumulator - uVar7;
    f33_angle_controller_envelope_parameters[5] = (ushort)uVar4;
    uVar7 = f33_angle_controller_envelope_accumulator;
    if (uVar4 != 0) {
      uVar7 = f33_angle_controller_envelope_accumulator / uVar4;
    }
    uVar7 = uVar7 & 0xffff;
    if (-1 < (int)(uVar7 - uVar2) && uVar7 != uVar2) goto LAB_000cf21e;
  }
  else {
    if (DAT_febecb34 != '3') goto LAB_000cf21e;
    if (uVar3 != uVar6) {
      if (uVar6 == 0) {
        f33_angle_controller_envelope_accumulator = uVar7 * uVar3;
      }
      else {
        f33_angle_controller_envelope_accumulator =
             f33_angle_controller_envelope_accumulator * uVar3;
        if (uVar6 != 0) {
          f33_angle_controller_envelope_accumulator =
               f33_angle_controller_envelope_accumulator / uVar6;
        }
      }
    }
    f33_angle_controller_envelope_accumulator = f33_angle_controller_envelope_accumulator - uVar7;
    f33_angle_controller_envelope_parameters[5] = (ushort)uVar3;
    uVar7 = f33_angle_controller_envelope_accumulator;
    if (uVar3 != 0) {
      uVar7 = f33_angle_controller_envelope_accumulator / uVar3;
    }
    uVar7 = uVar7 & 0xffff;
    uVar4 = uVar3;
    if (uVar2 < uVar7) goto LAB_000cf21e;
  }
  f33_angle_controller_envelope_parameters[5] = (ushort)uVar4;
  uVar7 = 0;
  f33_angle_controller_envelope_accumulator = 0;
LAB_000cf21e:
  f33_angle_controller_envelope_parameters[0] = (ushort)uVar7;
  return;
}



/* VoteCAA6/8/A. Non7 setsCB36=2; never-active mode7 suppresses target. At gain0 clear activity but
   still admit that invocation's prior-active voted target. Mode7 prior-active latch permits fade;
   zero gain clears latch without suppressing that invocation target, unlike never-active mode7. */

void f33_vote_angle_target_and_update_fade_latch(void)

{
  int iVar1;
  
  iVar1 = (int)f33_angle_controller_target_triplicate[0];
  DAT_febecb08 = (int)f33_angle_controller_target_triplicate[1];
  if (((iVar1 == DAT_febecb08) || (iVar1 == f33_angle_controller_target_triplicate[2])) ||
     (DAT_febecb08 != f33_angle_controller_target_triplicate[2])) {
    DAT_febecb08 = iVar1;
  }
  if ((DAT_febecb00 & 7) == 7) {
    if (DAT_febecb36 == '\0') {
      DAT_febecb08 = 0;
    }
    else if (f33_angle_controller_envelope_parameters[0] == 0) {
      DAT_febecb36 = '\0';
    }
  }
  else {
    DAT_febecb36 = '\x02';
  }
  return;
}



void FUN_000cf276(void)

{
  int iVar1;
  
  iVar1 = (int)(short)((DAT_febecb00 & 7) + (DAT_febeac3c & 1) * 8);
  if ((DAT_febecb00 & 7) != 7) {
    f33_angle_controller_envelope_parameters[6] = (*((ushort *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd3e00u + (uint32_t)(iVar1 * 0x57) * 4u)))))));
    f33_angle_controller_envelope_parameters[7] = **(ushort **)(((undefined *)camry_host_ptr(0xd3e04u)) + iVar1 * 0x15c);
  }
  return;
}



/* WARNING: Removing unreachable block (ram,0x000cf2e6) */
/* Scale target*gain/256, slew from votedCB38/30/32, then absolute clamp and triplicate publication.
   Zero gain/activity does not immediately erase output history. Final target*gain/256 slews
   relative to voted old output then absolute-clamps; zero gain/latch can leave residual output,
   bank1 mode3 clamps1996 after slew. */

void f33_slew_and_clamp_angle_controller_contribution(void)

{
  int iVar1;
  uint uVar2;
  uint uVar3;
  int iVar4;
  
  iVar1 = (int)((int)(int16_t)DAT_febecb38);
  iVar4 = (int)((int)(int16_t)DAT_febecb30);
  uVar2 = (uint)f33_angle_controller_envelope_parameters[6];
  uVar3 = (uint)f33_angle_controller_envelope_parameters[7];
  if (((iVar1 == iVar4) || (iVar1 == ((int)(int16_t)DAT_febecb32))) || (iVar4 != ((int)(int16_t)DAT_febecb32))) {
    iVar4 = iVar1;
  }
  DAT_febecb18 = (int)(DAT_febecb08 * (uint)f33_angle_controller_envelope_parameters[0]) / 0x100;
  DAT_febecb14 = DAT_febecb18 - iVar4;
  if ((int)(DAT_febecb14 - uVar2) < 0 == ((int)DAT_febecb14 < 0 && -1 < (int)(DAT_febecb14 - uVar2))
      && DAT_febecb14 != uVar2) {
    DAT_febecb1c = uVar2 + iVar4;
  }
  else {
    DAT_febecb1c = DAT_febecb18;
    if ((int)(DAT_febecb14 + uVar2) < 0 !=
        ((int)DAT_febecb14 < 0 != (int)-uVar2 < 0 &&
        (int)-uVar2 < 0 == (int)(DAT_febecb14 + uVar2) < 0)) {
      DAT_febecb1c = iVar4 - uVar2;
    }
  }
  if (((int)(DAT_febecb1c - uVar3) < 0 ==
       ((int)DAT_febecb1c < 0 && -1 < (int)(DAT_febecb1c - uVar3)) && DAT_febecb1c != uVar3) ||
     (uVar2 = -uVar3, iVar4 = DAT_febecb1c + uVar3, uVar3 = uVar2,
     iVar4 < 0 != ((int)DAT_febecb1c < 0 != (int)uVar2 < 0 && (int)uVar2 < 0 == iVar4 < 0))) {
    DAT_febecb3a = 1;
  }
  else {
    DAT_febecb3a = 0;
    uVar3 = DAT_febecb1c;
  }
  DAT_febecb38 = (short)uVar3;
  DAT_febecb30 = ((int)(int16_t)DAT_febecb38);
  DAT_febecb32 = ((int)(int16_t)DAT_febecb38);
  return;
}



/* Select envelope mode, evolve retained0..256 gain, vote target and prior output, scale, slew and
   saturate into CB38 plus duplicate publications. Never-active mode7 selects zero; after prior
   activation the envelope may finish fading. Not an always-active ordinary return controller. Voted
   target and prior output feed retained envelope then slew/saturation into CB38 and duplicates.
   after activation retained decay can finish. */

void f33_update_angle_controller_output_envelope(void)

{
  FUN_000cf0b6();
  FUN_000cf0ea();
  f33_update_angle_controller_retained_envelope();
  f33_vote_angle_target_and_update_fade_latch();
  FUN_000cf276();
  f33_slew_and_clamp_angle_controller_contribution();
  return;
}



/* Constant-block fill: 5 literal assignments into one contiguous cell block; shape-verified.
   Literals are default/reset values; cell meanings are not recovered. */

void f33_fill_constant_block_cf35c(void)

{
  DAT_febecb57 = 0;
  DAT_febecb58 = 0;
  DAT_febecb54 = 0;
  DAT_febecb55 = 0;
  DAT_febecb56 = 0;
  return;
}



void FUN_000cf370(void)

{
  uint uVar1;
  int iVar2;
  uint uVar3;
  
  uVar3 = 0;
  do {
    iVar2 = uVar3 * 2;
    uVar1 = uVar3 + 1;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebecb42u + (uint32_t)(iVar2) * 1u)))) = 0;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebecb43u + (uint32_t)(iVar2) * 1u)))) = 0;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebecb48u + (uint32_t)(iVar2) * 1u)))) = 0;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebecb49u + (uint32_t)(iVar2) * 1u)))) = 0;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebecb4eu + (uint32_t)(iVar2) * 1u)))) = 0;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebecb4fu + (uint32_t)(iVar2) * 1u)))) = 0;
    (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebecb3cu + (uint32_t)(uVar3) * 2u)))) = 0;
    uVar3 = uVar1;
  } while (uVar1 < 3);
  return;
}



/* Cell-block copy: 21 whole-cell assignments with a fixed source-to-destination mapping;
   shape-verified. The mapping is per-cell; cell meanings are not recovered. */

void f33_copy_cell_block_cf3a2(void)

{
  DAT_febecb42 = DAT_febead64;
  DAT_febecb43 = DAT_febead61;
  DAT_febecb48 = DAT_febead66;
  DAT_febecb49 = DAT_febead63;
  DAT_febecb4e = DAT_febead65;
  DAT_febecb4f = DAT_febead62;
  DAT_febecb3c = DAT_febeae6a;
  DAT_febecb44 = DAT_febead6b;
  DAT_febecb45 = DAT_febead68;
  DAT_febecb4a = DAT_febead6d;
  DAT_febecb4b = DAT_febead6a;
  DAT_febecb50 = DAT_febead6c;
  DAT_febecb51 = DAT_febead69;
  DAT_febecb3e = DAT_febeae6c;
  DAT_febecb46 = DAT_febead02;
  DAT_febecb47 = DAT_febeacf4;
  DAT_febecb4c = DAT_febead01;
  DAT_febecb4d = DAT_febeacf3;
  DAT_febecb52 = DAT_febead00;
  DAT_febecb53 = DAT_febeacf2;
  DAT_febecb40 = DAT_febeae14;
  return;
}



void FUN_000cf442(void)

{
  char *pcVar1;
  int iVar2;
  uint32_t puVar3;
  uint uVar4;
  
  puVar3 = 0xfebeb800u;
  f33_copy_cell_block_cf3a2();
  uVar4 = 0;
  do {
    iVar2 = uVar4 * 2;
    pcVar1 = ((undefined *)camry_host_ptr((uint32_t)(puVar3 + iVar2 + 0x1342)));
    if ((*pcVar1 == -0x5b) && (((int8_t)pcVar1[1]) != -1)) {
      pcVar1[1] = pcVar1[1] + '\x01';
    }
    pcVar1 = ((undefined *)camry_host_ptr((uint32_t)(puVar3 + iVar2 + 0x1348)));
    if ((*pcVar1 == -0x5b) && (((int8_t)pcVar1[1]) != -1)) {
      pcVar1[1] = pcVar1[1] + '\x01';
    }
    pcVar1 = ((undefined *)camry_host_ptr((uint32_t)(puVar3 + iVar2 + 0x134e)));
    if ((*pcVar1 == -0x5b) && (((int8_t)pcVar1[1]) != -1)) {
      pcVar1[1] = pcVar1[1] + '\x01';
    }
    uVar4 = uVar4 + 1;
  } while (uVar4 < 3);
  return;
}



void FUN_000cf4a8(void)

{
  if ((DAT_febecab7 == '\x01') && ((DAT_febecb00 & 7) == 2)) {
    DAT_febecb57 = 1;
  }
  else {
    DAT_febecb57 = 0;
    if (DAT_febecab7 == '\x01') {
      DAT_febecb57 = 0;
      DAT_febecb58 = (DAT_febecb00 & 7) == 0;
      return;
    }
  }
  DAT_febecb58 = 0;
  return;
}



void FUN_000cf4da(uint param_1,char param_2)

{
  int iVar1;
  
  if ((param_2 == '\x01') && ((param_1 & 0xff) < 3)) {
    iVar1 = (param_1 & 0xff) * 2;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebecb42u + (uint32_t)(iVar1) * 1u)))) = 0xa5;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebecb43u + (uint32_t)(iVar1) * 1u)))) = 0;
  }
  return;
}



void FUN_000cf4f8(uint param_1,char param_2,char param_3)

{
  int iVar1;
  
  if (((param_2 == '\x01') && (param_3 == '\x01')) && ((param_1 & 0xff) < 3)) {
    iVar1 = (param_1 & 0xff) * 2;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebecb48u + (uint32_t)(iVar1) * 1u)))) = 0xa5;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebecb49u + (uint32_t)(iVar1) * 1u)))) = 0;
  }
  return;
}



void FUN_000cf51c(uint param_1,char param_2,char param_3)

{
  ushort uVar1;
  char cVar2;
  
  param_1 = param_1 & 0xff;
  if (((param_2 == '\x01') && (param_3 == '\x01')) && (param_1 < 3)) {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebecb4eu + (uint32_t)(param_1 * 2) * 1u)))) = 0xa5;
    cVar2 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebecb54u + (uint32_t)(param_1) * 1u))));
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebecb4fu + (uint32_t)(param_1 * 2) * 1u)))) = 0;
    if (cVar2 == '\0') {
      uVar1 = (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebecb3cu + (uint32_t)(param_1) * 2u))));
      if (uVar1 < 0xff) {
        (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebecb3cu + (uint32_t)(param_1) * 2u)))) = uVar1 + 1;
        (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebecb54u + (uint32_t)(param_1) * 1u)))) = 0x5a;
      }
    }
  }
  return;
}



void FUN_000cf56a(void)

{
  undefined1 uVar1;
  undefined1 uVar2;
  undefined1 uVar3;
  undefined1 uVar4;
  undefined1 uVar5;
  undefined1 uVar6;
  
  uVar6 = DAT_febecb58;
  uVar5 = DAT_febecb57;
  uVar4 = DAT_febecb3a;
  uVar3 = DAT_febecafd;
  uVar2 = DAT_febec862;
  uVar1 = DAT_febec834;
  FUN_000cf4da(0,DAT_febecb57);
  FUN_000cf4f8(0,uVar5,uVar3);
  FUN_000cf51c(0,uVar5,uVar4);
  FUN_000cf4da(1,uVar6);
  FUN_000cf4f8(1,uVar6,uVar3);
  FUN_000cf51c(1,uVar6,uVar4);
  FUN_000cf4da(2,uVar2);
  FUN_000cf4f8(2,1,uVar1);
  FUN_000cf51c(2,uVar2,uVar4);
  return;
}



void FUN_000cf5de(void)

{
  FUN_000cf4a8();
  FUN_000cf56a();
  return;
}



/* Cell-block copy: 21 whole-cell assignments with a fixed source-to-destination mapping;
   shape-verified. The mapping is per-cell; cell meanings are not recovered. */

void f33_copy_cell_block_cf5ee(void)

{
  DAT_febead64 = DAT_febecb42;
  DAT_febead61 = DAT_febecb43;
  DAT_febead66 = DAT_febecb48;
  DAT_febead63 = DAT_febecb49;
  DAT_febead65 = DAT_febecb4e;
  DAT_febead62 = DAT_febecb4f;
  DAT_febeae6a = DAT_febecb3c;
  DAT_febead6b = DAT_febecb44;
  DAT_febead68 = DAT_febecb45;
  DAT_febead6d = DAT_febecb4a;
  DAT_febead6a = DAT_febecb4b;
  DAT_febead6c = DAT_febecb50;
  DAT_febead69 = DAT_febecb51;
  DAT_febeae6c = DAT_febecb3e;
  DAT_febead02 = DAT_febecb46;
  DAT_febeacf4 = DAT_febecb47;
  DAT_febead01 = DAT_febecb4c;
  DAT_febeacf3 = DAT_febecb4d;
  DAT_febead00 = DAT_febecb52;
  DAT_febeacf2 = DAT_febecb53;
  DAT_febeae14 = DAT_febecb40;
  return;
}



/* Constant-block fill: 52 literal assignments into one contiguous cell block; shape-verified.
   Literals are default/reset values; cell meanings are not recovered. */

void f33_fill_constant_block_cf684(void)

{
  DAT_febecbb8 = 0;
  DAT_febecbb6 = 200;
  DAT_febecbc6 = 200;
  DAT_febecbd6 = 200;
  DAT_febecbc8 = 0;
  DAT_febecbd8 = 0;
  DAT_febecbba = 0;
  DAT_febecbca = 0;
  DAT_febecbda = 0;
  DAT_febecbbc = 0;
  DAT_febecbcc = 0;
  DAT_febecbdc = 0;
  DAT_febecbbe = 1;
  DAT_febecbce = 1;
  DAT_febecbde = 1;
  DAT_febecbc0 = 0;
  DAT_febecbd0 = 0;
  DAT_febecbe0 = 0;
  DAT_febecbc2 = 1;
  DAT_febecbd2 = 1;
  DAT_febecbe2 = 1;
  DAT_febecbec = 0;
  DAT_febecbb4 = 0;
  DAT_febecbd4 = 0;
  DAT_febecbe4 = 0;
  DAT_febecb68 = 0;
  DAT_febecb8c = 0;
  DAT_febecba0 = 0;
  DAT_febecb6c = 0;
  DAT_febecbea = 0;
  DAT_febecbeb = 0;
  DAT_febecb70 = 0;
  DAT_febecb90 = 0;
  DAT_febecba4 = 0;
  DAT_febecb74 = 0;
  DAT_febecb94 = 0;
  DAT_febecba8 = 0;
  DAT_febecb78 = 0;
  DAT_febecb5c = 0;
  DAT_febecb98 = 0;
  DAT_febecbac = 0;
  DAT_febecb7c = 0;
  DAT_febecb9c = 0;
  DAT_febecbb0 = 0;
  DAT_febecb60 = 0;
  DAT_febecb64 = 0;
  DAT_febecbe6 = 1;
  DAT_febecbe8 = 0;
  DAT_febecb84 = 0;
  DAT_febecb88 = 0;
  DAT_febecbc4 = 0;
  DAT_febecb80 = 0;
  return;
}



/* Constant-block fill: 50 literal assignments into one contiguous cell block; shape-verified.
   Literals are default/reset values; cell meanings are not recovered. */

void f33_fill_constant_block_cf75c(void)

{
  DAT_febecbb8 = 0;
  DAT_febecbb6 = 200;
  DAT_febecbc6 = 200;
  DAT_febecbd6 = 200;
  DAT_febecbc8 = 0;
  DAT_febecbd8 = 0;
  DAT_febecbba = 0;
  DAT_febecbca = 0;
  DAT_febecbda = 0;
  DAT_febecbbc = 0;
  DAT_febecbcc = 0;
  DAT_febecbdc = 0;
  DAT_febecbbe = 1;
  DAT_febecbce = 1;
  DAT_febecbde = 1;
  DAT_febecbc0 = 0;
  DAT_febecbd0 = 0;
  DAT_febecbe0 = 0;
  DAT_febecbc2 = 1;
  DAT_febecbd2 = 1;
  DAT_febecbe2 = 1;
  DAT_febecbec = 0;
  DAT_febecbb4 = 0;
  DAT_febecbd4 = 0;
  DAT_febecbe4 = 0;
  DAT_febecb68 = 0;
  DAT_febecb8c = 0;
  DAT_febecba0 = 0;
  DAT_febecb6c = 0;
  DAT_febecb70 = 0;
  DAT_febecb90 = 0;
  DAT_febecba4 = 0;
  DAT_febecb74 = 0;
  DAT_febecb94 = 0;
  DAT_febecba8 = 0;
  DAT_febecb78 = 0;
  DAT_febecb5c = 0;
  DAT_febecb98 = 0;
  DAT_febecbac = 0;
  DAT_febecb7c = 0;
  DAT_febecb9c = 0;
  DAT_febecbb0 = 0;
  DAT_febecb60 = 0;
  DAT_febecb64 = 0;
  DAT_febecbe6 = 1;
  DAT_febecbe8 = 0;
  DAT_febecb84 = 0;
  DAT_febecb88 = 0;
  DAT_febecbc4 = 0;
  DAT_febecb80 = 0;
  return;
}



void FUN_000cf82c(void)

{
  undefined *puVar1;
  
  if (DAT_febecbfe != DAT_febecbed) {
    puVar1 = ((void *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xb148cu + (uint32_t)(DAT_febeac3c & 1) * 4u)))))));
    if (DAT_febecbfe == '\x01') {
      DAT_febecbb6 = *(undefined2 *)(puVar1 + 0xc);
      DAT_febecbb8 = *(undefined2 *)(puVar1 + 0xe);
      DAT_febecbba = *(undefined2 *)(puVar1 + 0x10);
      DAT_febecbbc = *(undefined2 *)(puVar1 + 0x12);
      DAT_febecbbe = *(undefined2 *)(puVar1 + 0x14);
      DAT_febecbc0 = *(undefined2 *)(puVar1 + 0x16);
      DAT_febecbc2 = *(undefined2 *)(puVar1 + 0x18);
      DAT_febecbc6 = DAT_febecbb6;
      DAT_febecbc8 = DAT_febecbb8;
      DAT_febecbca = DAT_febecbba;
      DAT_febecbcc = DAT_febecbbc;
      DAT_febecbce = DAT_febecbbe;
      DAT_febecbd0 = DAT_febecbc0;
      DAT_febecbd2 = DAT_febecbc2;
      DAT_febecbd6 = DAT_febecbb6;
      DAT_febecbd8 = DAT_febecbb8;
      DAT_febecbda = DAT_febecbba;
      DAT_febecbdc = DAT_febecbbc;
      DAT_febecbde = DAT_febecbbe;
      DAT_febecbe0 = DAT_febecbc0;
      DAT_febecbe2 = DAT_febecbc2;
    }
    else if (DAT_febecbfe == '\x02') {
      DAT_febecbb6 = *(undefined2 *)(puVar1 + 0x1a);
      DAT_febecbb8 = *(undefined2 *)(puVar1 + 0x1c);
      DAT_febecbba = *(undefined2 *)(puVar1 + 0x1e);
      DAT_febecbbc = *(undefined2 *)(puVar1 + 0x20);
      DAT_febecbbe = *(undefined2 *)(puVar1 + 0x22);
      DAT_febecbc0 = *(undefined2 *)(puVar1 + 0x24);
      DAT_febecbc2 = *(undefined2 *)(puVar1 + 0x26);
      DAT_febecbc6 = DAT_febecbb6;
      DAT_febecbc8 = DAT_febecbb8;
      DAT_febecbca = DAT_febecbba;
      DAT_febecbcc = DAT_febecbbc;
      DAT_febecbce = DAT_febecbbe;
      DAT_febecbd0 = DAT_febecbc0;
      DAT_febecbd2 = DAT_febecbc2;
      DAT_febecbd6 = DAT_febecbb6;
      DAT_febecbd8 = DAT_febecbb8;
      DAT_febecbda = DAT_febecbba;
      DAT_febecbdc = DAT_febecbbc;
      DAT_febecbde = DAT_febecbbe;
      DAT_febecbe0 = DAT_febecbc0;
      DAT_febecbe2 = DAT_febecbc2;
    }
    else {
      DAT_febecbb6 = *(undefined2 *)(puVar1 + 0x28);
      DAT_febecbb8 = *(undefined2 *)(puVar1 + 0x2a);
      DAT_febecbba = *(undefined2 *)(puVar1 + 0x2c);
      DAT_febecbbc = *(undefined2 *)(puVar1 + 0x2e);
      DAT_febecbbe = *(undefined2 *)(puVar1 + 0x30);
      DAT_febecbc0 = *(undefined2 *)(puVar1 + 0x32);
      DAT_febecbc2 = *(undefined2 *)(puVar1 + 0x34);
      DAT_febecbc6 = DAT_febecbb6;
      DAT_febecbc8 = DAT_febecbb8;
      DAT_febecbca = DAT_febecbba;
      DAT_febecbcc = DAT_febecbbc;
      DAT_febecbce = DAT_febecbbe;
      DAT_febecbd0 = DAT_febecbc0;
      DAT_febecbd2 = DAT_febecbc2;
      DAT_febecbd6 = DAT_febecbb6;
      DAT_febecbd8 = DAT_febecbb8;
      DAT_febecbda = DAT_febecbba;
      DAT_febecbdc = DAT_febecbbc;
      DAT_febecbde = DAT_febecbbe;
      DAT_febecbe0 = DAT_febecbc0;
      DAT_febecbe2 = DAT_febecbc2;
    }
  }
  return;
}



void FUN_000cfa84(void)

{
  uint uVar1;
  
  if (((DAT_febecb70 == DAT_febecb90) || (DAT_febecb70 == DAT_febecba4)) ||
     (uVar1 = DAT_febecb90, DAT_febecb90 != DAT_febecba4)) {
    uVar1 = DAT_febecb70;
  }
  if (DAT_febecbfe != DAT_febecbed) {
    DAT_febecb6c = 0;
  }
  if (DAT_febecb6c < uVar1) {
    DAT_febecb6c = DAT_febecb6c + 1;
  }
  else {
    DAT_febecb6c = 0;
  }
  return;
}



void FUN_000cfac2(void)

{
  uint uVar1;
  uint uVar2;
  uint uVar3;
  uint uVar4;
  
  if (((DAT_febecb5c == DAT_febecb98) || (DAT_febecb5c == DAT_febecbac)) ||
     (uVar1 = DAT_febecb98, DAT_febecb98 != DAT_febecbac)) {
    uVar1 = DAT_febecb5c;
  }
  if (((DAT_febecb70 == DAT_febecb90) || (DAT_febecb70 == DAT_febecba4)) ||
     (uVar2 = DAT_febecb90, DAT_febecb90 != DAT_febecba4)) {
    uVar2 = DAT_febecb70;
  }
  if (((DAT_febecb74 == DAT_febecb94) || (DAT_febecb74 == DAT_febecba8)) ||
     (uVar3 = DAT_febecb94, DAT_febecb94 != DAT_febecba8)) {
    uVar3 = DAT_febecb74;
  }
  if (((DAT_febecb7c == DAT_febecb9c) || (DAT_febecb7c == DAT_febecbb0)) ||
     (uVar4 = DAT_febecb9c, DAT_febecb9c != DAT_febecbb0)) {
    uVar4 = DAT_febecb7c;
  }
  if ((DAT_febecb6c < uVar3) || (uVar2 < DAT_febecb6c)) {
    if (uVar1 == 0) {
      DAT_febecbec = false;
    }
    else {
      if (uVar1 != 0) {
        DAT_febecb78 = DAT_febecb6c % uVar1;
      }
      DAT_febecbec = DAT_febecb78 < uVar4;
    }
  }
  else {
    DAT_febecbec = false;
    DAT_febecb78 = 0;
  }
  return;
}



int FUN_000cfb62(int param_1)

{
  int iVar1;
  
  if (param_1 + -0x168 < 0 == (param_1 < 0 && -1 < param_1 + -0x168)) {
    if (param_1 + -0x2d0 < 0 == (param_1 < 0 && -1 < param_1 + -0x2d0)) {
      iVar1 = -1;
      if (param_1 + -0x438 < 0 == (param_1 < 0 && -1 < param_1 + -0x438)) {
        param_1 = 0x5a0 - param_1;
      }
      else {
        param_1 = param_1 + -0x2d0;
      }
      goto LAB_000cfb90;
    }
    param_1 = 0x2d0 - param_1;
  }
  iVar1 = 1;
LAB_000cfb90:
  if (param_1 + -0x168 < 0 == (param_1 < 0 && -1 < param_1 + -0x168)) {
    param_1 = 0x168;
  }
  else if (param_1 < 0) {
    param_1 = 0;
  }
  return iVar1 * *(short *)(((undefined *)camry_host_ptr(0xd526cu)) + param_1 * 2);
}



/* WARNING: Removing unreachable block (ram,0x000cfc8e) */

void FUN_000cfbb4(void)

{
  uint uVar1;
  uint uVar2;
  int iVar3;
  uint32_t puVar4;
  int iVar5;
  uint uVar6;
  uint uVar7;
  int iVar8;
  int iVar9;
  uint uVar10;
  int iVar11;
  int iVar12;
  
  uVar1 = DAT_febecb78;
  puVar4 = 0xfebeb800u;
  if (((DAT_febecb68 == DAT_febecb8c) || (DAT_febecb68 == DAT_febecba0)) ||
     (iVar3 = DAT_febecb8c, DAT_febecb8c != DAT_febecba0)) {
    iVar3 = DAT_febecb68;
  }
  uVar10 = (uint)DAT_febecbd4;
  uVar2 = (uint)DAT_febecbb4;
  if (((uVar2 == uVar10) || (uVar2 == DAT_febecbe4)) || (uVar10 != DAT_febecbe4)) {
    uVar10 = uVar2;
  }
  uVar6 = (uint)DAT_febecbb8;
  uVar2 = (uint)DAT_febecbc8;
  iVar11 = (int)((int)(int8_t)DAT_febecbe6);
  if (((uVar6 == uVar2) || (uVar6 == DAT_febecbd8)) || (uVar2 != DAT_febecbd8)) {
    uVar2 = uVar6;
  }
  uVar7 = (uint)DAT_febecbba;
  uVar6 = (uint)DAT_febecbca;
  if (((uVar7 == uVar6) || (uVar7 == DAT_febecbda)) || (uVar6 != DAT_febecbda)) {
    uVar6 = uVar7;
  }
  if (DAT_febecbec == '\x01') {
    if (DAT_febecbee == '\0') {
      if (((int)(int16_t)DAT_febec172) < 0) {
        iVar11 = -1;
      }
      else {
        iVar11 = 1;
      }
    }
    DAT_febecb80 = DAT_febecb78;
    if (uVar10 != 0) {
      DAT_febecb80 = DAT_febecb78 % uVar10;
    }
    iVar12 = DAT_febecb80 * 0x5a0;
    if (uVar10 != 0) {
      if (iVar12 == -0x80000000 && uVar10 == 0xffffffff) {
        iVar12 = -0x80000000;
      }
      else {
        iVar12 = iVar12 / (int)uVar10;
      }
    }
    puVar4 = 0xfebeb800u;
    iVar5 = FUN_000cfb62(iVar12);
    if ((uVar10 <= uVar1) && (uVar1 < uVar10 * (iVar3 + -1))) {
      uVar6 = uVar2;
    }
    iVar3 = (int)(iVar5 * iVar11 * uVar6) / 0x1000;
    iVar8 = (*((int *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xb148cu + (uint32_t)((byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0xbc4))))) & 1) * 4u)))) + 4))));
    iVar9 = iVar8;
    if ((iVar3 - iVar8 < 0 != (iVar3 < 0 != iVar8 < 0 && iVar8 < 0 == iVar3 - iVar8 < 0) ||
         iVar3 == iVar8) &&
       (iVar9 = -iVar8,
       iVar3 + iVar8 < 0 == (iVar3 < 0 != iVar9 < 0 && iVar9 < 0 == iVar3 + iVar8 < 0) &&
       iVar3 != iVar9)) {
      iVar9 = iVar3;
    }
  }
  else {
    DAT_febecb80 = 0;
    iVar3 = DAT_febecb88;
    iVar5 = DAT_febecb60;
    iVar9 = 0;
    iVar12 = DAT_febecb84;
  }
  (*((int *)camry_host_ptr((uint32_t)(puVar4 + 0x1360)))) = iVar5;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(0x13e6))))) = (char)iVar11;
  (*((int *)camry_host_ptr((uint32_t)(puVar4 + 0x1364)))) = iVar9;
  (*((int *)camry_host_ptr((uint32_t)(puVar4 + 0x1384)))) = iVar12;
  (*((int *)camry_host_ptr((uint32_t)(puVar4 + 5000)))) = iVar3;
  return;
}



void FUN_000cfcd4(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  
  iVar1 = DAT_febecc22 + DAT_febecb64;
  iVar3 = (int)(*((short *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xb148cu + (uint32_t)(DAT_febeac3c & 1) * 4u)))) + 10))));
  DAT_febecbe8 = (*((short *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xb148cu + (uint32_t)(DAT_febeac3c & 1) * 4u)))) + 10))));
  if ((iVar1 - iVar3 < 0 != (iVar1 < 0 != iVar3 < 0 && iVar3 < 0 == iVar1 - iVar3 < 0) ||
       iVar1 == iVar3) &&
     (iVar2 = -iVar3, DAT_febecbe8 = (short)iVar1,
     iVar1 + iVar3 < 0 != (iVar1 < 0 != iVar2 < 0 && iVar2 < 0 == iVar1 + iVar3 < 0) ||
     iVar1 == iVar2)) {
    DAT_febecbe8 = (short)iVar2;
  }
  DAT_febecbc4 = (short)iVar1;
  return;
}



/* Paired constant publisher: DAT_febecbed = 0; and DAT_febecbee = 0;; shape-classified from the
   canonical corpus. Target cells not yet named. */

void FUN_000cfd0a(void)

{
  DAT_febecbed = 0;
  DAT_febecbee = 0;
  return;
}



void FUN_000cfd14(void)

{
  if (DAT_febecbed == '\0') {
    DAT_febecbe8 = 0;
  }
  else {
    f33_fill_constant_block_cff78();
    f33_fill_constant_block_cf75c();
  }
  return;
}



/* Sequential initializer chain: 7 unconditional calls and no other statements; shape-verified. The
   called sequence is the function's entire behavior; chain family members differ in callee sets. */

void f33_run_init_chain_cfd32(void)

{
  FUN_000cf82c();
  FUN_000cf972();
  FUN_000cfa84();
  FUN_000cfac2();
  FUN_000cfbb4();
  FUN_000d0120();
  FUN_000cfcd4();
  return;
}



/* Run waveform and bounded AC24-memory terms only when CBEB and CBFE are nonzero. Mode transition
   resets phase; window controls publication. Disable after activity resets retained blocks, while
   already-idle disable publishes zero. OEM request identity remains unassigned. CBEB/CBFE gate
   windowed waveform and bounded AC24-memory composition. Activity-to-disabled resets retained
   blocks; idle-disabled publishes zero. Software generator reconstructed; OEM excitation request
   identity remains unresolved. */

void f33_update_windowed_excitation(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  if ((DAT_febecbeb == '\0') || (DAT_febecbfe == '\0')) {
    FUN_000cfd14();
  }
  else {
    f33_run_init_chain_cfd32();
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x13ed))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x13fe)))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x13ee))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x13ec)))));
  return;
}



/* Constant-block fill: 5 literal assignments into one contiguous cell block; shape-verified.
   Literals are default/reset values; cell meanings are not recovered. */

void f33_fill_constant_block_cfd88(void)

{
  DAT_febecbf3 = 0;
  DAT_febecbf4 = 1;
  DAT_febecbf5 = 0;
  DAT_febecbf0 = 0;
  DAT_febecbf2 = 0;
  return;
}



void FUN_000cfda0(void)

{
  uint32_t puVar1;
  uchar uVar2;
  
  puVar1 = 0xfebeb800u;
  uVar2 = f33_get_application_grouped_status(0x1a);
  if ((uVar2 == 'Z') || ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0xa47))))) != '\0')) {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x13f3))))) = 0;
  }
  else {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x13f3))))) = 0x5a;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x13f2))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0xa27)))));
  }
  return;
}



char FUN_000cfdd4(void)

{
  char cVar1;
  
  if (((DAT_febeadbf == '\x02' || DAT_febeadbf == '\x03') || (DAT_febeacbd != '\0')) ||
     (DAT_febecbf3 == '\0')) {
    DAT_febecbf4 = 1;
    cVar1 = DAT_febecbea;
  }
  else {
    DAT_febecbf4 = 0;
    cVar1 = DAT_febecbf2;
    if (((DAT_febecbf2 != '\x01') && (DAT_febecbf2 != '\x02')) && (DAT_febecbf2 != '\x03')) {
      cVar1 = '\0';
    }
  }
  return cVar1;
}



char FUN_000cfe14(void)

{
  char cVar1;
  
  cVar1 = DAT_febecbeb;
  if (((((DAT_febecbeb == '\0') && (DAT_febecbf4 == '\0')) &&
       (cVar1 = DAT_febecbf5 == '\0', (bool)cVar1)) || (cVar1 == '\x01')) &&
     (DAT_febecbf4 == '\x01')) {
    cVar1 = '\0';
  }
  else if (DAT_febecbf5 != '\x01') {
    return cVar1;
  }
  DAT_febecbf5 = DAT_febecbf0 < DAT_000b115c;
  if ((bool)DAT_febecbf5) {
    DAT_febecbf0 = DAT_febecbf0 + 1;
  }
  else {
    DAT_febecbf0 = 0;
  }
  return cVar1;
}



undefined4 FUN_000cfe64(void)

{
  uint32_t puVar1;
  undefined1 uVar2;
  undefined1 uVar3;
  undefined4 uVar4;
  
  puVar1 = 0xfebeb800u;
  uVar2 = FUN_000cfdd4();
  uVar3 = FUN_000cfe14();
  uVar4 = FUN_000d1da0(0xffc0);
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x13ea))))) = uVar2;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x13eb))))) = uVar3;
  FUN_000d1dc6(uVar4);
  return uVar4;
}



/* Constant-block fill: 5 literal assignments into one contiguous cell block; shape-verified.
   Literals are default/reset values; cell meanings are not recovered. */

void f33_fill_constant_block_cfe8e(void)

{
  DAT_febecbfe = 0;
  DAT_febecbf6 = 0;
  DAT_febecbfa = 0;
  DAT_febecbfc = 0;
  DAT_febecbf8 = 0;
  return;
}



void FUN_000cfea4(char param_1,short *param_2)

{
  undefined *puVar1;
  
  if (param_1 != DAT_febecbed) {
    *param_2 = 0;
    if (param_1 == '\0') {
      DAT_febecbf6 = 0;
      DAT_febecbfa = 0;
      DAT_febecbfc = 0;
      return;
    }
    puVar1 = ((void *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xb148cu + (uint32_t)(DAT_febeac3c & 1) * 4u)))))));
    if (param_1 == '\x01') {
      DAT_febecbf6 = *(undefined2 *)(puVar1 + 0x36);
    }
    else if (param_1 == '\x02') {
      DAT_febecbf6 = *(undefined2 *)(puVar1 + 0x38);
    }
    else {
      DAT_febecbf6 = *(undefined2 *)(puVar1 + 0x3a);
    }
    DAT_febecbfa = DAT_febecbf6;
    DAT_febecbfc = DAT_febecbf6;
    *param_2 = *param_2 + 1;
  }
  return;
}



void FUN_000cff04(void)

{
  undefined1 uVar1;
  ushort uVar2;
  uint32_t puVar3;
  undefined1 uVar4;
  ushort uStack_a;
  
  uVar1 = DAT_febecbea;
  puVar3 = 0xfebeb800u;
  uStack_a = DAT_febecbf8;
  if (((DAT_febecbf6 == DAT_febecbfa) || (DAT_febecbf6 == DAT_febecbfc)) ||
     (uVar2 = DAT_febecbfa, DAT_febecbfa != DAT_febecbfc)) {
    uVar2 = DAT_febecbf6;
  }
  if (DAT_febecbeb == '\x01') {
    uVar4 = DAT_febecbfe;
    if (DAT_febecbf8 < uVar2) {
      uStack_a = DAT_febecbf8 + 1;
    }
    else if (DAT_febecbec == '\0') {
      puVar3 = 0xfebeb800u;
      FUN_000cfea4(DAT_febecbea,&uStack_a);
      uVar4 = uVar1;
    }
  }
  else {
    uVar4 = 0;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(0x13fe))))) = uVar4;
  (*((ushort *)camry_host_ptr((uint32_t)(puVar3 + 0x13f8)))) = uStack_a;
  return;
}



/* Paired constant publisher: DAT_febecc1a = 0; and DAT_febecc1c = 0;; shape-classified from the
   canonical corpus. Target cells not yet named. */

void FUN_000cff6e(void)

{
  DAT_febecc1a = 0;
  DAT_febecc1c = 0;
  return;
}



/* Constant-block fill: 10 literal assignments into one contiguous cell block; shape-verified.
   Literals are default/reset values; cell meanings are not recovered. */

void f33_fill_constant_block_cff78(void)

{
  DAT_febecc20 = 0;
  DAT_febecc18 = 0;
  DAT_febecc00 = 0;
  DAT_febecc04 = 0;
  DAT_febecc08 = 0;
  DAT_febecc0c = 0;
  DAT_febecc10 = 0;
  DAT_febecc1e = 0;
  DAT_febecc14 = 0;
  DAT_febecc22 = 0;
  return;
}



/* WARNING: Removing unreachable block (ram,0x000cfff0) */

void FUN_000cffa2(void)

{
  ushort input;
  uint32_t puVar1;
  int iVar2;
  
  input = DAT_febeadf6;
  puVar1 = 0xfebeb800u;
  iVar2 = f33_interpolate_unsigned_axis_sentinel_curve
                    (((ushort *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xb148cu + (uint32_t)(DAT_febeac3c & 1) * 4u)))) + 0x3c))),DAT_febeadf6);
  (*((short *)camry_host_ptr((uint32_t)(puVar1 + 0x141a)))) = (short)iVar2;
  iVar2 = f33_interpolate_unsigned_axis_sentinel_curve
                    (((ushort *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xb148cu + (uint32_t)((byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0xbc4))))) & 1) * 4u)))) + 0x60))),input);
  (*((short *)camry_host_ptr((uint32_t)(puVar1 + 0x141c)))) = (short)((int)(iVar2 * (uint)(*((ushort *)camry_host_ptr((uint32_t)(puVar1 + -0x9c6))))) / 0x40000)
  ;
  return;
}



void FUN_000cfffc(void)

{
  uint32_t puVar1;
  ushort input;
  int iVar2;
  
  puVar1 = 0xfebeb800u;
  input = f33_abs_s16_wrapping(DAT_febeac0e);
  iVar2 = f33_interpolate_unsigned_axis_sentinel_curve
                    (((ushort *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xb148cu + (uint32_t)((byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0xbc4))))) & 1) * 4u)))) + 0x84))),input);
  (*((short *)camry_host_ptr((uint32_t)(puVar1 + 0x1418)))) = (short)iVar2;
  return;
}



/* WARNING: Removing unreachable block (ram,0x000ce5fc) */
/* ADBD scaling or special offsets, previous-output slew then absolute clamp. Equality admitted;
   publishCAAC/CAAD/CA9B and retained center. Mode0 center is zero. Scaled/special-offset
   composition slews from retained center then applies absolute bound; clamp flags exclude equality
   and direction drives later anti-windup. */

void f33_limit_angle_controller_output(void)

{
  bool bVar1;
  bool bVar2;
  undefined2 uVar3;
  int iVar4;
  int iVar5;
  uint32_t puVar6;
  uint uVar7;
  undefined1 uVar8;
  bool bVar9;
  int iVar10;
  undefined1 uVar11;
  uint uVar12;
  
  uVar11 = DAT_febeca9b;
  puVar6 = 0xfebeb800u;
  if (DAT_febeca9d == '\x01') {
    if (((DAT_febec940 == DAT_febec998) || (DAT_febec940 == DAT_febec9c4)) ||
       (iVar5 = DAT_febec998, DAT_febec998 != DAT_febec9c4)) {
      iVar5 = DAT_febec940;
    }
    iVar10 = (int)((int)(int16_t)DAT_febeca40);
    iVar4 = (int)((int)(int16_t)DAT_febeca7e);
    if (((iVar10 == iVar4) || (iVar10 == ((int)(int16_t)DAT_febeca8c))) || (iVar4 != ((int)(int16_t)DAT_febeca8c))) {
      iVar4 = iVar10;
    }
    iVar10 = iVar5 - iVar4;
    uVar12 = (uint)DAT_febeca42;
    puVar6 = 0xfebeb800u;
    uVar7 = f33_abs_s32_wrapping(iVar10);
    (*((int *)camry_host_ptr((uint32_t)(puVar6 + 0x1138)))) = iVar10;
    uVar12 = (uVar12 * 0xa4) / 0x8000;
    (*((uint *)camry_host_ptr((uint32_t)(puVar6 + 0x1148)))) = uVar12;
    bVar1 = uVar7 != uVar12;
    bVar2 = (int)(uVar7 - uVar12) < 0 == ((int)uVar7 < 0 && -1 < (int)(uVar7 - uVar12));
    bVar9 = bVar2 && bVar1;
    if (bVar2 && bVar1) {
      if (iVar10 < 1) {
        iVar5 = iVar4 - uVar12;
        if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xb146cu + (uint32_t)((byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(-0xbc4))))) & 1) * 4u)))) + (uint32_t)(1))))) == '\x01') {
          uVar11 = 1;
        }
      }
      else {
        iVar5 = uVar12 + iVar4;
        if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xb146cu + (uint32_t)((byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(-0xbc4))))) & 1) * 4u)))) + (uint32_t)(1))))) == '\x01') {
          uVar11 = 2;
        }
      }
    }
    iVar4 = (int)(*((short *)camry_host_ptr((uint32_t)(puVar6 + 0x1244))));
    if (iVar5 - iVar4 < 0 == (iVar5 < 0 != iVar4 < 0 && iVar4 < 0 == iVar5 - iVar4 < 0) &&
        iVar5 != iVar4) {
      uVar11 = 2;
      uVar8 = 1;
      iVar10 = iVar4;
    }
    else {
      iVar10 = -iVar4;
      if (iVar5 + iVar4 < 0 == (iVar5 < 0 != iVar10 < 0 && iVar10 < 0 == iVar5 + iVar4 < 0)) {
        uVar8 = 0;
        iVar10 = iVar5;
        if (((*((volatile uint8_t *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xb146cu + (uint32_t)((byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(-0xbc4))))) & 1) * 4u)))) + (uint32_t)(1))))) != '\x01') || (!bVar2 || !bVar1)) {
          uVar11 = 0;
        }
      }
      else {
        uVar8 = 1;
        uVar11 = 1;
      }
    }
    uVar3 = (undefined2)iVar10;
    (*((int *)camry_host_ptr((uint32_t)(puVar6 + 0x113c)))) = iVar5;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(0x129b))))) = uVar11;
  }
  else {
    iVar5 = 0x7fff;
    if (((int)DAT_febec944 + -0x7fff < 0 != ((int)DAT_febec944 < 0 && -1 < (int)DAT_febec944 + -0x7fff) ||
         DAT_febec944 == 0x7fff) &&
       (iVar5 = DAT_febec944,
       (int)DAT_febec944 + 0x7fff < 0 != (-1 < (int)DAT_febec944 && (int)DAT_febec944 + 0x7fff < 0) ||
       DAT_febec944 == -0x7fff)) {
      iVar5 = -0x7fff;
    }
    uVar3 = (undefined2)iVar5;
    bVar9 = false;
    uVar8 = 0;
  }
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar6 + 0x1246)))) = uVar3;
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar6 + 0x127c)))) = uVar3;
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar6 + 0x128a)))) = uVar3;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(0x12ac))))) = bVar9;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(0x12ad))))) = uVar8;
  if (((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(0x1300))))) & 7) == 0) {
    uVar3 = 0;
  }
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar6 + 0x1240)))) = uVar3;
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar6 + 0x127e)))) = uVar3;
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar6 + 0x128c)))) = uVar3;
  return;
}


/* WARNING: Removing unreachable block (ram,0x000cc7bc) */
/* WARNING: Removing unreachable block (ram,0x000cc768) */

ushort FUN_000cc6ba(void)

{
  short sVar1;
  short sVar2;
  short sVar3;
  short value;
  char cVar4;
  bool bVar5;
  uchar *puVar6;
  uint32_t puVar7;
  short *points;
  ushort input;
  short sVar8;
  short sVar9;
  int iVar10;
  int iVar12;
  int iVar13;
  int iVar14;
  int iVar15;
  int iVar16;
  short sVar17;
  short sVar18;
  int iVar11;
  
  cVar4 = DAT_febec890;
  sVar18 = ((int)(int16_t)DAT_febec87c);
  sVar17 = ((int)(int16_t)DAT_febec87a);
  iVar11 = DAT_febec86c;
  iVar13 = DAT_febeaf0c;
  value = ((int)(int16_t)DAT_febeae0a);
  sVar9 = ((int)(int16_t)DAT_febeae08);
  puVar7 = 0xfebeb800u;
  sVar8 = 0x7fff;
  iVar16 = (int)((int)(int16_t)DAT_febec882);
  puVar6 = ((void *)camry_host_ptr((uint32_t)(f33_calibration_bank_bases[DAT_febeac3c & 1])));
  sVar1 = *(short *)(puVar6 + 0x2282);
  sVar2 = (*((short *)camry_host_ptr((uint32_t)(0x2284u + (int)camry_host_addr((puVar6 + 4))))));
  sVar3 = *(short *)(puVar6 + 0x228a);
  if ((int)DAT_febec868 + -0x7fff < 0 != ((int)DAT_febec868 < 0 && -1 < (int)DAT_febec868 + -0x7fff) ||
      DAT_febec868 == 0x7fff) {
    if ((int)DAT_febec868 + 0x7fff < 0 == (-1 < (int)DAT_febec868 && (int)DAT_febec868 + 0x7fff < 0) &&
        DAT_febec868 != -0x7fff) {
      sVar8 = (short)DAT_febec868;
    }
    else {
      sVar8 = -0x7fff;
    }
  }
  input = f33_abs_s16_wrapping(sVar8);
  if (cVar4 == '\x01') {
    iVar10 = f33_interpolate_unsigned_axis_sentinel_curve
                       (((ushort *)camry_host_ptr((uint32_t)(f33_calibration_bank_bases[(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar7 + (uint32_t)(-0xbc4))))) & 1] + 0x2290))),
                        input);
    sVar17 = (short)iVar10;
    if (sVar8 < 0) {
      sVar17 = -sVar17;
    }
    (*((short *)camry_host_ptr((uint32_t)(puVar7 + 0x1076)))) = sVar17;
    sVar18 = (short)(((int)sVar18 * (int)sVar17) / 0x400);
    (*((short *)camry_host_ptr((uint32_t)(puVar7 + 0x1078)))) = sVar18;
    if (iVar13 == 0x55aaaa55) {
      points = ((short *)camry_host_ptr((uint32_t)(f33_calibration_bank_bases[(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar7 + (uint32_t)(-0xbc4))))) & 1] + 0x22b8)));
      sVar17 = sVar9;
LAB_000cc7b0:
      iVar10 = f33_interpolate_signed_sentinel_curve(points,sVar17);
      sVar17 = (short)iVar10;
    }
    else {
      sVar17 = 0;
      if (iVar13 == -0x55aaaa56) {
        points = ((short *)camry_host_ptr((uint32_t)(f33_calibration_bank_bases[(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar7 + (uint32_t)(-0xbc4))))) & 1] + 0x22d4)));
        sVar17 = value;
        goto LAB_000cc7b0;
      }
    }
    iVar10 = (int)(short)(((int)sVar17 * (int)sVar18) / 0x400);
  }
  else {
    iVar10 = 0;
  }
  puVar6 = ((void *)camry_host_ptr((uint32_t)(f33_calibration_bank_bases[(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar7 + (uint32_t)(-0xbc4))))) & 1])));
  iVar15 = (int)*(short *)(puVar6 + 0x227e);
  iVar14 = (int)*(short *)(puVar6 + 0x2280);
  if ((iVar10 - iVar15 < 0 != (iVar10 < 0 != iVar15 < 0 && iVar15 < 0 == iVar10 - iVar15 < 0) ||
       iVar10 == iVar15) &&
     (iVar15 = iVar14,
     iVar10 - iVar14 < 0 == (iVar10 < 0 != iVar14 < 0 && iVar14 < 0 == iVar10 - iVar14 < 0) &&
     iVar10 != iVar14)) {
    iVar15 = iVar10;
  }
  iVar14 = (int)*(short *)(puVar6 + 0x227c);
  iVar16 = (iVar11 + iVar15) - iVar16;
  iVar11 = iVar16 * 0x400;
  if (iVar14 != 0) {
    if (iVar11 == -0x80000000 && iVar14 == -1) {
      iVar11 = 0;
    }
    else {
      iVar11 = iVar11 / iVar14;
    }
  }
  sVar18 = (short)iVar15;
  sVar8 = f33_abs_s16_wrapping((short)iVar11 - sVar18);
  iVar14 = (int)sVar8;
  iVar15 = (int)DAT_000b04ec;
  sVar8 = sVar18;
  if (iVar14 - iVar15 < 0 == (iVar14 < 0 != iVar15 < 0 && iVar15 < 0 == iVar14 - iVar15 < 0) &&
      iVar14 != iVar15) {
    sVar8 = (short)iVar11;
  }
  sVar9 = f33_abs_s16_wrapping(sVar9);
  iVar11 = (int)sVar9;
  sVar9 = f33_abs_s16_wrapping(value);
  iVar15 = (int)sVar9;
  if ((cVar4 == '\x01') &&
     (iVar12 = (int)sVar1, iVar14 = (short)input - iVar12,
     iVar14 < 0 != ((short)input < 0 != iVar12 < 0 && iVar12 < 0 == iVar14 < 0))) {
    if ((iVar13 == 0x55aaaa55) &&
       (iVar14 = (int)sVar2,
       iVar11 - iVar14 < 0 == (iVar11 < 0 != iVar14 < 0 && iVar14 < 0 == iVar11 - iVar14 < 0) &&
       iVar11 != iVar14)) {
      bVar5 = true;
      goto LAB_000cc85c;
    }
    if (iVar13 == -0x55aaaa56) {
      iVar13 = (int)sVar3;
      bVar5 = iVar15 - iVar13 < 0 == (iVar15 < 0 != iVar13 < 0 && iVar13 < 0 == iVar15 - iVar13 < 0)
              && iVar15 != iVar13;
      goto LAB_000cc85c;
    }
  }
  bVar5 = false;
LAB_000cc85c:
  (*((short *)camry_host_ptr((uint32_t)(puVar7 + 0x107a)))) = sVar17;
  (*((short *)camry_host_ptr((uint32_t)(puVar7 + 0x107e)))) = (short)iVar10;
  (*((short *)camry_host_ptr((uint32_t)(puVar7 + 0x1080)))) = sVar18;
  (*((int *)camry_host_ptr((uint32_t)(puVar7 + 0x106c)))) = iVar16;
  (*((short *)camry_host_ptr((uint32_t)(puVar7 + 0x1082)))) = sVar8;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar7 + (uint32_t)(0x1091))))) = bVar5;
  return input;
}


/* WARNING: Removing unreachable block (ram,0x000cea56) */

void FUN_000ce9ea(void)

{
  int value;
  int iVar1;
  char cVar2;
  char cVar3;
  short value_00;
  short value_01;
  char cVar4;
  undefined *puVar5;
  uint32_t puVar6;
  ushort uVar7;
  ushort uVar8;
  uint uVar9;
  int iVar10;
  int iVar11;
  char cVar12;
  
  cVar4 = DAT_febecaca;
  value_01 = ((int)(int16_t)DAT_febeae24);
  value_00 = ((int)(int16_t)DAT_febeae22);
  cVar3 = DAT_febead4d;
  cVar2 = DAT_febead4c;
  puVar6 = 0xfebeb800u;
  if (((DAT_febecacb == DAT_febecace) || (DAT_febecacb == DAT_febecad0)) ||
     (cVar12 = DAT_febecace, DAT_febecace != DAT_febecad0)) {
    cVar12 = DAT_febecacb;
  }
  if (((DAT_febecabc == DAT_febecac0) || (DAT_febecabc == DAT_febecac4)) ||
     (iVar11 = DAT_febecac0, DAT_febecac0 != DAT_febecac4)) {
    iVar11 = DAT_febecabc;
  }
  iVar10 = (int)((int)(int16_t)DAT_febeae5e);
  value = (int)((int)(int8_t)DAT_febeacc5) + ((int)(int16_t)DAT_febeadfe) * 0xf;
  iVar1 = (value * 0x6fb) / 0x200;
  uVar9 = f33_abs_s32_wrapping(value);
  uVar7 = f33_abs_s16_wrapping(value_00);
  uVar8 = f33_abs_s16_wrapping(value_01);
  if (((cVar3 == 'Z') && (cVar2 == '\0')) && (cVar4 == '\x01')) {
    if ((((cVar12 == '\0') &&
         (puVar5 = ((void *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xb146cu + (uint32_t)((byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(-0xbc4))))) & 1) * 4u))))))), uVar9 < *(ushort *)(puVar5 + 0x2c)
         )) && (uVar7 < *(ushort *)(puVar5 + 0x2e))) && (uVar8 < *(ushort *)(puVar5 + 0x30))) {
      iVar11 = iVar10 * 2 - iVar1;
      cVar12 = '\x01';
    }
  }
  else {
    cVar12 = '\0';
  }
  (*((int *)camry_host_ptr((uint32_t)(puVar6 + 0x12b8)))) = iVar1;
  (*((int *)camry_host_ptr((uint32_t)(puVar6 + 0x12bc)))) = iVar11;
  (*((int *)camry_host_ptr((uint32_t)(puVar6 + 0x12c0)))) = iVar11;
  (*((int *)camry_host_ptr((uint32_t)(puVar6 + 0x12c4)))) = iVar11;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(0x12cb))))) = cVar12;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(0x12ce))))) = cVar12;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(0x12d0))))) = cVar12;
  return;
}

