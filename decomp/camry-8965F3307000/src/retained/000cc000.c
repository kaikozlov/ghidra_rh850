#include "common.h"

void fill_constant_block_cc038(void)

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

int update_acfe_mod64_delta_and_reset_c828_flags_cc07a(void)

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
  
  sVar2 = ((int)(int16_t)DAT_febeae20);
  bVar1 = DAT_febeacfe;
  puVar4 = 0xfebeb800u;
  iVar8 = (int)((int)(int16_t)DAT_febeae20);
  uVar9 = (uint)DAT_febeacfe;
  abs_s16_wrapping(((int)(int16_t)DAT_febeae20));
  abs_s32_wrapping(((uint32_t)((uint32_t)(iVar8 - (*((short *)camry_host_ptr((uint32_t)(puVar4 + 0x1024))))))));
  abs_s16_wrapping((*((short *)camry_host_ptr((uint32_t)(puVar4 + -0x9de)))));
  sVar5 = abs_s16_wrapping((*((short *)camry_host_ptr((uint32_t)(puVar4 + -0x9dc)))));
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

int clear_c826_and_return_abs_ae24_cc114(void)

{
  uint32_t puVar1;
  short sVar2;
  
  puVar1 = 0xfebeb800u;
  sVar2 = abs_s16_wrapping(((int)(int16_t)DAT_febeae24));
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + 0x1026)))) = 0;
  return (int)sVar2;
}

void or_c82e_c834_into_c835_cc130(void)

{
  DAT_febec835 = DAT_febec82e == '\x01' || DAT_febec834 == '\x01';
  return;
}

void fill_constant_block_cc148(void)

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

void step_c858_enable_latch_and_c863_holdoff_cc1b6(void)

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

void filter_c846_toward_q8_unity_by_c85a_cc32a(void)

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
    DAT_febec838 = (int)sVar3 * (int)((int)(int16_t)DAT_febec846);
    DAT_febec84a = sVar3;
  }
  DAT_febec85b = DAT_febec85a;
  DAT_febec848 = 0x100;
  if (uVar1 - 1 < 3) {
    DAT_febec838 = (DAT_febec838 + 0x100) - (int)((int)(int16_t)DAT_febec846);
    iVar5 = (int)((int)(int16_t)DAT_febec84a);
    iVar4 = DAT_febec838;
    if (iVar5 != 0) {
      if (DAT_febec838 == -0x80000000 && iVar5 == -1) {
        iVar4 = 0;
      }
      else {
        iVar4 = (int)DAT_febec838 / (int)iVar5;
      }
    }
    DAT_febec846 = (short)iVar4;
    sVar3 = abs_s16_wrapping(((int)(int16_t)DAT_febec846) + -0x100);
    iVar4 = (int)sVar3;
    if (iVar4 + -5 < 0 != (iVar4 < 0 && -1 < iVar4 + -5) || iVar4 == 5) {
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(0x105a))))) = 0;
      (*((undefined2 *)camry_host_ptr((uint32_t)(puVar2 + 0x1046)))) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar2 + 0x1048))));
    }
  }
  return;
}

uint32_t map_signed_ae20_gain_into_c83c_cc3be(void)

{
  uint32_t camry_r10_result;
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
  sVar5 = (camry_r10_result = abs_s16_wrapping(((int)(int16_t)DAT_febec850)));
  if ((*((short *)camry_host_ptr((uint32_t)(puVar4 + 0x1050)))) < 0) {
    ppuVar3 = &PTR_DAT_000d3c5c;
  }
  else {
    ppuVar3 = &PTR_DAT_000d3c1c;
  }
  iVar6 = (camry_r10_result = interpolate_signed16_axis_unsigned16_values_d07f2(((undefined *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)((uint8_t *)ppuVar3 + (uint32_t)(uVar2 & 3) * 4u)))))),(int)sVar5));
  (*((short *)camry_host_ptr((uint32_t)(puVar4 + 0x1052)))) = (short)iVar6;
  sVar5 = (short)( (int)(((*((short *)camry_host_ptr((uint32_t)(puVar4 + 0x1050)))) * iVar6)) / (int)0x400);
  (*((short *)camry_host_ptr((uint32_t)(puVar4 + 0x1054)))) = sVar5;
  (*((int *)camry_host_ptr((uint32_t)(puVar4 + 0x103c)))) = (int)sVar5 << 5;
  return camry_r10_result;
}

void slew_c856_and_classify_c840_limit_crossing_cc43a(void)

{
  int old_value;
  int scaled;
  int limit;
  int delta;
  int stepped;
  int mode_limit;
  
  old_value = (int)(int16_t)DAT_febec856;
  scaled = (int)(DAT_febec83c << 8) / 0x2000;
  if (scaled > 0x7fff) {
    scaled = 0x7fff;
  }
  else if (scaled <= -0x7fff) {
    scaled = -0x7fff;
  }
  DAT_febec84c = (short)scaled;
  limit = (int)(int16_t)DAT_000b0512;
  delta = scaled - old_value;
  stepped = scaled;
  if (delta > limit) {
    stepped = old_value + limit;
  }
  else if (delta < -limit) {
    stepped = old_value - limit;
  }
  if (stepped > 0x7fff) {
    stepped = 0x7fff;
  }
  else if (stepped < -0x7fff) {
    stepped = -0x7fff;
  }
  DAT_febec856 = (short)stepped;
  DAT_febec840 = (uint)stepped;
  mode_limit = (int)(int16_t)DAT_000b0510;
  if (stepped > mode_limit) {
    if (DAT_febec85c != '\x02') {
      DAT_febec85c = '\x02';
      DAT_febec864 = 1;
    }
    else {
      DAT_febec864 = 0;
    }
  }
  else if (stepped < -mode_limit) {
    if (DAT_febec85c != '\x01') {
      DAT_febec85c = '\x01';
      DAT_febec864 = 1;
    }
    else {
      DAT_febec864 = 0;
    }
  }
  else {
    DAT_febec85c = '\0';
    DAT_febec864 = 0;
  }
  if (stepped > mode_limit) {
    stepped = mode_limit;
  }
  else if (stepped <= -mode_limit) {
    stepped = -mode_limit;
  }
  DAT_febec85e = (short)stepped;
  return;
}

void set_c865_from_acbe_and_adfc_low9_cc514(void)

{
  DAT_febec865 = DAT_febeacbe == '\x01' && (DAT_febeadfc & 0x1ff) == 0;
  return;
}

void initialize_c868_curve_filter_state_cc530(void)

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
  DAT_febec88c = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xb144cu + (uint32_t)(DAT_febeac3c & 1) * 4u))))) + (uint32_t)(0x228c)))));
  DAT_febec88d = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xb144cu + (uint32_t)(DAT_febeac3c & 1) * 4u))))) + (uint32_t)(0x228d)))));
  DAT_febec87e = 0;
  DAT_febec880 = 0;
  DAT_febec86c = 0;
  DAT_febec882 = 0;
  DAT_febec886 = 0;
  return;
}

void fill_constant_block_cc596(void)

{
  DAT_febec884 = 0;
  DAT_febec888 = 0;
  DAT_febec870 = 0;
  DAT_febec88a = 0;
  DAT_febec894 = 0;
  return;
}

undefined4 snapshot_c0d0_c08f_c0cc_into_c88e_c868_cc5ac(void)

{
  uint32_t puVar1;
  undefined4 uVar2;
  
  puVar1 = 0xfebeb800u;
  uVar2 = raise_priority_mask_and_return_previous_d1da0(0xffc0);
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x108e))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x8d0)))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x108f))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x88f)))));
  (*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + 0x1068)))) = (*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + 0x8cc))));
  restore_priority_mask_preserving_interrupt_enable_d1dc6(uVar2);
  return uVar2;
}

void classify_c890_magic_and_status_gates_cc5da(void)

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

void interpolate_adf6_into_c87c_c886_gains_cc66e(void)

{
  ushort input;
  uint32_t puVar1;
  int iVar2;
  int iVar3;
  
  input = DAT_febeadf6;
  puVar1 = 0xfebeb800u;
  iVar2 = interpolate_unsigned_axis_sentinel_curve
                    (((ushort *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xb144cu + (uint32_t)(DAT_febeac3c & 1) * 4u)))) + 0x22f0))),DAT_febeadf6)
  ;
  iVar3 = interpolate_unsigned_axis_sentinel_curve
                    (((ushort *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xb144cu + (uint32_t)((byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0xbc4))))) & 1) * 4u)))) + 0x2348))),input
                    );
  (*((short *)camry_host_ptr((uint32_t)(puVar1 + 0x107c)))) = (short)iVar2;
  (*((short *)camry_host_ptr((uint32_t)(puVar1 + 0x1086)))) = (short)iVar3;
  return;
}

ushort compose_c868_magic_selected_curve_filter_cc6ba(void)

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
  puVar6 = ((void *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xb144cu + (uint32_t)(DAT_febeac3c & 1) * 4u)))))));
  sVar1 = *(short *)(puVar6 + 0x2282);
  sVar2 = (*((short *)camry_host_ptr((uint32_t)(0x2284u + (int)camry_host_addr((puVar6 + 4))))));
  sVar3 = *(short *)(puVar6 + 0x228a);
  if ((int)DAT_febec868 + -0x7fff < 0 != ((int)DAT_febec868 < 0 && -1 < (int)DAT_febec868 + -0x7fff) ||
      ((int)(int32_t)DAT_febec868) == 0x7fff) {
    if ((int)DAT_febec868 + 0x7fff < 0 == (-1 < (int)DAT_febec868 && (int)DAT_febec868 + 0x7fff < 0) &&
        ((int)(int32_t)DAT_febec868) != -0x7fff) {
      sVar8 = (short)((int)(int32_t)DAT_febec868);
    }
    else {
      sVar8 = -0x7fff;
    }
  }
  input = abs_s16_wrapping(sVar8);
  if (cVar4 == '\x01') {
    iVar10 = interpolate_unsigned_axis_sentinel_curve
                       (((ushort *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xb144cu + (uint32_t)((byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar7 + (uint32_t)(-0xbc4))))) & 1) * 4u)))) + 0x2290))),
                        input);
    sVar17 = (short)iVar10;
    if (sVar8 < 0) {
      sVar17 = -sVar17;
    }
    (*((short *)camry_host_ptr((uint32_t)(puVar7 + 0x1076)))) = sVar17;
    sVar18 = (short)(((int)sVar18 * (int)sVar17) / 0x400);
    (*((short *)camry_host_ptr((uint32_t)(puVar7 + 0x1078)))) = sVar18;
    if (iVar13 == 0x55aaaa55) {
      points = ((short *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xb144cu + (uint32_t)((byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar7 + (uint32_t)(-0xbc4))))) & 1) * 4u)))) + 0x22b8)));
      sVar17 = sVar9;
LAB_000cc7b0:
      iVar10 = interpolate_signed_sentinel_curve(points,sVar17);
      sVar17 = (short)iVar10;
    }
    else {
      sVar17 = 0;
      if (iVar13 == -0x55aaaa56) {
        points = ((short *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xb144cu + (uint32_t)((byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar7 + (uint32_t)(-0xbc4))))) & 1) * 4u)))) + 0x22d4)));
        sVar17 = value;
        goto LAB_000cc7b0;
      }
    }
    iVar10 = (int)(short)(((int)sVar17 * (int)sVar18) / 0x400);
  }
  else {
    iVar10 = 0;
  }
  puVar6 = ((void *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xb144cu + (uint32_t)((byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar7 + (uint32_t)(-0xbc4))))) & 1) * 4u)))))));
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
      iVar11 = (int)iVar11 / (int)iVar14;
    }
  }
  sVar18 = (short)iVar15;
  sVar8 = abs_s16_wrapping((short)iVar11 - sVar18);
  iVar14 = (int)sVar8;
  iVar15 = (int)DAT_000b04ec;
  sVar8 = sVar18;
  if (iVar14 - iVar15 < 0 == (iVar14 < 0 != iVar15 < 0 && iVar15 < 0 == iVar14 - iVar15 < 0) &&
      iVar14 != iVar15) {
    sVar8 = (short)iVar11;
  }
  sVar9 = abs_s16_wrapping(sVar9);
  iVar11 = (int)sVar9;
  sVar9 = abs_s16_wrapping(value);
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
  return (ushort)sVar9;
}

void debounce_abs_c882_c88a_sum_into_c892_cc878(void)

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
    sVar2 = abs_s16_wrapping(((int)(int16_t)DAT_febec882) + ((int)(int16_t)DAT_febec88a));
    iVar3 = (int)sVar2;
    iVar4 = (int)(*((short *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xb144cu + (uint32_t)((byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0xbc4))))) & 1) * 4u)))) + 0x2286))));
    if (iVar3 - iVar4 < 0 == (iVar3 < 0 != iVar4 < 0 && iVar4 < 0 == iVar3 - iVar4 < 0) &&
        iVar3 != iVar4) {
      if (uVar6 < (*((ushort *)camry_host_ptr((uint32_t)(0x2284u + (int)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xb144cu + (uint32_t)((byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0xbc4))))) & 1) * 4u))))))))) {
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

void compose_c88a_from_c172_ac44_curve_products_cc8d6(void)

{
  short sVar1;
  uint32_t puVar2;
  short sVar3;
  short sVar4;
  int iVar5;
  int iVar6;
  int iVar7;
  
  sVar1 = ((int)(int16_t)DAT_febec172);
  sVar4 = ((int)(int16_t)DAT_febeac44);
  puVar2 = 0xfebeb800u;
  if (DAT_febec891 == '\x01') {
    iVar7 = (int)((int)(int16_t)DAT_febec886);
    puVar2 = 0xfebeb800u;
    sVar3 = abs_s16_wrapping(((int)(int16_t)DAT_febec172));
    sVar4 = abs_s16_wrapping(sVar4);
    iVar5 = interpolate_signed_sentinel_curve
                      (((short *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xb144cu + (uint32_t)((byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0xbc4))))) & 1) * 4u)))) + 0x2314))),
                       sVar3);
    sVar3 = (short)iVar5;
    if (sVar1 < 0) {
      sVar3 = -sVar3;
    }
    (*((short *)camry_host_ptr((uint32_t)(puVar2 + 0x1084)))) = sVar3;
    iVar5 = interpolate_signed_sentinel_curve
                      (((short *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xb144cu + (uint32_t)((byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0xbc4))))) & 1) * 4u)))) + 0x2330))),
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

void clamp_c882_c88a_sum_into_c894_cc984(void)

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

void initialize_c898_ca78_redundant_control_state_cc9ac(void)

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
  ((volatile int16_t *)camry_host_ptr(0xfebecaa6u))[0] = 0;
  (*((volatile int16_t *)camry_host_ptr((uint32_t)(0xfebecaa6u + (uint32_t)(1) * 2u)))) = 0;
  (*((volatile int16_t *)camry_host_ptr((uint32_t)(0xfebecaa6u + (uint32_t)(2) * 2u)))) = 0;
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

void load_c9ee_c9f4_and_reseed_transition_divisor_cccc6(void)

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
    DAT_febec898 = (int)((int)(int16_t)DAT_febec9ec) * (int)((int)(int16_t)DAT_febec9e8);
  }
  DAT_febeca96 = DAT_febecab5;
  return;
}

void filter_c9e8_between_cab7_selected_q8_targets_ccd50(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  
  iVar3 = (int)DAT_000b05b2;
  iVar4 = (int)DAT_000b05b0;
  iVar2 = (int)((int)(int16_t)DAT_febec9ec);
  iVar5 = iVar4;
  if (DAT_febecab7 == '\x01') {
    iVar5 = iVar3;
  }
  if (((DAT_febecab5 == '\x11') || (DAT_febecab5 == '\"')) || (DAT_febecab5 == 'D')) {
    DAT_febec898 = (DAT_febec898 + iVar5) - (int)((int)(int16_t)DAT_febec9e8);
    iVar1 = DAT_febec898;
    if (iVar2 != 0) {
      if (DAT_febec898 == -0x80000000 && iVar2 == -1) {
        iVar1 = -0x80000000;
      }
      else {
        iVar1 = (int)DAT_febec898 / (int)iVar2;
      }
    }
    if (((iVar5 != iVar3) ||
        (iVar2 = iVar3 - ((int)(int16_t)DAT_febec9f4),
        iVar1 - iVar2 < 0 != (iVar1 < 0 != iVar2 < 0 && iVar2 < 0 == iVar1 - iVar2 < 0))) &&
       ((iVar3 = iVar1, iVar5 == iVar4 &&
        (iVar2 = ((int)(int16_t)DAT_febec9f4) + iVar4, iVar3 = iVar4,
        iVar1 - iVar2 < 0 == (iVar1 < 0 != iVar2 < 0 && iVar2 < 0 == iVar1 - iVar2 < 0) &&
        iVar1 != iVar2)))) {
      iVar3 = iVar1;
    }
    DAT_febec9e8 = (short)iVar3;
  }
  DAT_febec9ea = (short)iVar5;
  return;
}

void load_mode_c9f6_slew_and_c9f8_limit_ccdc4(void)

{
  int iVar1;
  
  iVar1 = (int)(short)((DAT_febecb00 & 7) + (DAT_febeac3c & 1) * 8);
  DAT_febec9f6 = (*((undefined2 *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd3cbcu + (uint32_t)(iVar1 * 0x57) * 4u)))))));
  DAT_febec9f8 = (*((undefined2 *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd3cc0u + (uint32_t)(iVar1 * 0x57) * 4u)))))));
  return;
}

void vote_slew_scale_and_triplicate_c9fa_target_ccdf8(void)

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
  if ((int)(((int)(int32_t)DAT_febec89c) - uVar4) < 0 == ((int)DAT_febec89c < 0 && -1 < (int)(((int)(int32_t)DAT_febec89c) - uVar4))
      && ((int)(int32_t)DAT_febec89c) != uVar4) {
    DAT_febec8a0 = uVar4 + DAT_febec9b8;
  }
  else if ((int)(((int)(int32_t)DAT_febec89c) + uVar4) < 0 !=
           ((int)DAT_febec89c < 0 != (int)-uVar4 < 0 &&
           (int)-uVar4 < 0 == (int)(((int)(int32_t)DAT_febec89c) + uVar4) < 0)) {
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
  DAT_febec8a4 = (uint)( (int)(((int)DAT_febec8a0 * iVar3)) / (int)0x100);
  DAT_febec9fa = DAT_febec9f8;
  if ((int)(((int)(int32_t)DAT_febec8a4) - uVar2) < 0 != ((int)DAT_febec8a4 < 0 && -1 < (int)(((int)(int32_t)DAT_febec8a4) - uVar2))
      || ((int)(int32_t)DAT_febec8a4) == uVar2) {
    uVar4 = -uVar2;
    if ((int)(((int)(int32_t)DAT_febec8a4) + uVar2) < 0 ==
        ((int)DAT_febec8a4 < 0 != (int)uVar4 < 0 &&
        (int)uVar4 < 0 == (int)(((int)(int32_t)DAT_febec8a4) + uVar2) < 0) && ((int)(int32_t)DAT_febec8a4) != uVar4) {
      DAT_febec9fa = (ushort)((int)(int32_t)DAT_febec8a4);
    }
    else {
      DAT_febec9fa = (ushort)uVar4;
    }
  }
  DAT_febec9b8 = DAT_febec8a0;
  DAT_febec9e4 = DAT_febec8a0;
  ((volatile int16_t *)camry_host_ptr(0xfebecaa6u))[0] = DAT_febec9fa;
  (*((volatile int16_t *)camry_host_ptr((uint32_t)(0xfebecaa6u + (uint32_t)(1) * 2u)))) = DAT_febec9fa;
  (*((volatile int16_t *)camry_host_ptr((uint32_t)(0xfebecaa6u + (uint32_t)(2) * 2u)))) = DAT_febec9fa;
  return;
}

void publish_angle_controller_target_triplicate(void)

{
  load_c9ee_c9f4_and_reseed_transition_divisor_cccc6();
  filter_c9e8_between_cab7_selected_q8_targets_ccd50();
  load_mode_c9f6_slew_and_c9f8_limit_ccdc4();
  vote_slew_scale_and_triplicate_c9fa_target_ccdf8();
  return;
}

void load_mode_c9fe_ca00_or_7ffe_limits_ccecc(void)

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

void interpolate_selected_angle_target(void)

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
  DAT_febec8b4 = (int)(int16_t)DAT_febec9fc;
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
      DAT_febec8ac = (uint)((int)DAT_febec8a8 / (int)uVar3);
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

void bound_selected_angle_target(void)

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
  if (((((int)(int32_t)DAT_febec8b8) == DAT_febec9a0) || (((int)(int32_t)DAT_febec8b8) == DAT_febec9cc)) ||
     (DAT_febec9a0 != DAT_febec9cc)) {
    DAT_febec9a0 = ((int)(int32_t)DAT_febec8b8);
  }
  if ((DAT_febecb00 & 7) != 7) {
    uVar2 = ((int)(int32_t)DAT_febec8b0) - DAT_febec9a0;
    if (((int)(uVar2 - uVar4) < 0 != ((int)uVar2 < 0 && -1 < (int)(uVar2 - uVar4)) || uVar2 == uVar4
        ) && (uVar3 = -uVar4, iVar1 = uVar2 + uVar4, uVar4 = uVar3,
             iVar1 < 0 == ((int)uVar2 < 0 != (int)uVar3 < 0 && (int)uVar3 < 0 == iVar1 < 0) &&
             uVar2 != uVar3)) {
      uVar4 = uVar2;
    }
    DAT_febec8b0 = uVar4 + DAT_febec9a0;
  }
  DAT_febec8b8 = uVar5;
  if (((int)(((int)(int32_t)DAT_febec8b0) - uVar5) < 0 !=
       ((int)DAT_febec8b0 < 0 && -1 < (int)(((int)(int32_t)DAT_febec8b0) - uVar5)) || ((int)(int32_t)DAT_febec8b0) == uVar5) &&
     (DAT_febec8b8 = -uVar5,
     (int)(((int)(int32_t)DAT_febec8b0) + uVar5) < 0 ==
     ((int)DAT_febec8b0 < 0 != (int)DAT_febec8b8 < 0 &&
     (int)DAT_febec8b8 < 0 == (int)(((int)(int32_t)DAT_febec8b0) + uVar5) < 0) && ((int)(int32_t)DAT_febec8b0) != ((int)(int32_t)DAT_febec8b8))) {
    DAT_febec8b8 = ((int)(int32_t)DAT_febec8b0);
  }
  DAT_febec9a0 = ((int)(int32_t)DAT_febec8b8);
  DAT_febec9cc = ((int)(int32_t)DAT_febec8b8);
  return;
}
