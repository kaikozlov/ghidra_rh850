#include "common.h"

void step_signed_constant_fit_sweep(short angle)

{
  longlong lVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  uint32_t puVar5;
  uint uVar6;
  uint uVar7;
  uint uVar8;
  uint uVar9;
  uint uVar10;
  uint uVar11;
  int iVar12;
  int iVar13;
  int iVar14;
  int iVar15;
  int iVar16;
  int iVar17;
  int iVar18;
  int iVar19;
  int iVar20;
  short sVar21;
  short sVar22;
  short sVar23;
  short sVar24;
  short sVar25;
  short sVar26;
  uchar uStack_52;
  uchar uStack_51;
  int iStack_50;
  int iStack_4c;
  int iStack_48;
  short sStack_44;
  short sStack_42;
  short sStack_40;
  short sStack_3e;
  short sStack_3c;
  short sStack_3a;
  short sStack_38;
  short sStack_36;
  short sStack_34;
  short sStack_32;
  short sStack_30;
  short sStack_2e;
  
  puVar5 = 0xfebeb800u;
  iVar2 = (int)((int)(int16_t)DAT_febe5f36);
  uStack_52 = six_channel_fit_work.signed_initialized;
  uStack_51 = six_channel_fit_work.state;
  sStack_44 = six_channel_fit_work.signed_max[0];
  sStack_38 = six_channel_fit_work.signed_min[0];
  sStack_36 = six_channel_fit_work.signed_min[1];
  sStack_34 = six_channel_fit_work.signed_min[2];
  sStack_32 = six_channel_fit_work.signed_min[3];
  sStack_30 = six_channel_fit_work.signed_min[4];
  sStack_2e = six_channel_fit_work.signed_min[5];
  sStack_40 = six_channel_fit_work.signed_max[2];
  sStack_3e = six_channel_fit_work.signed_max[3];
  sStack_3c = six_channel_fit_work.signed_max[4];
  sStack_3a = six_channel_fit_work.signed_max[5];
  iStack_50 = six_channel_fit_work.signed_q16[3];
  iStack_4c = six_channel_fit_work.signed_q16[4];
  iStack_48 = six_channel_fit_work.signed_q16[5];
  sStack_42 = six_channel_fit_work.signed_max[1];
  uVar11 = (uint)six_channel_fit_work.first_gain[0];
  uVar10 = (uint)six_channel_fit_work.first_gain[1];
  uVar9 = (uint)six_channel_fit_work.first_gain[2];
  uVar8 = (uint)six_channel_fit_work.first_gain[3];
  uVar7 = (uint)six_channel_fit_work.first_gain[4];
  uVar6 = (uint)six_channel_fit_work.first_gain[5];
  if (iVar2 + 0x7fff < 0 == (-1 < iVar2 && iVar2 + 0x7fff < 0) && iVar2 != -0x7fff) {
    if (iVar2 < 0) {
      iVar2 = (int)-((int)(int16_t)DAT_febe5f36);
    }
  }
  else {
    iVar2 = 0x7fff;
  }
  if (((DAT_febe7db0 < fit_parameters.qualifier_lower) ||
      (fit_parameters.qualifier_upper < DAT_febe7db0)) ||
     (iVar17 = (int)fit_parameters.magnitude_upper,
     iVar2 - iVar17 < 0 == (iVar2 < 0 != iVar17 < 0 && iVar17 < 0 == iVar2 - iVar17 < 0) &&
     iVar2 != iVar17)) {
    uStack_52 = '\0';
    goto LAB_00033638;
  }
  iVar2 = (int)(0x8000 - (uint)six_channel_fit_work.first_center[0]) / 4;
  iVar17 = (int)(0x8000 - (uint)six_channel_fit_work.first_center[1]) / 4;
  iVar15 = (int)(0x8000 - (uint)six_channel_fit_work.first_center[2]) / 4;
  iVar14 = (int)(0x8000 - (uint)six_channel_fit_work.first_center[3]) / 4;
  iVar3 = (int)(0x8000 - (uint)six_channel_fit_work.first_center[4]) / 4;
  iVar12 = (int)(0x8000 - (uint)six_channel_fit_work.first_center[5]) / 4;
  if ((uVar11 == 0) || (iVar2 == 0)) {
    iVar2 = 0;
  }
  else {
    lVar1 = (longlong)iVar2 * (longlong)(int)uVar11;
    iVar4 = (int)((ulonglong)lVar1 >> 0x20);
    if (iVar2 < 0) {
      iVar4 = iVar4 + 1;
      if ((iVar4 < 0 == (-1 < lVar1 && iVar4 < 0)) && (0x80000000 < uVar11 * iVar2))
      goto LAB_000331fe;
      iVar2 = -0x7fffffff;
    }
    else if ((lVar1 < 0 || iVar4 == 0) && (uVar11 * iVar2 < 0x80000000)) {
LAB_000331fe:
      iVar2 = uVar11 * iVar2;
    }
    else {
      iVar2 = 0x7fffffff;
    }
  }
  if ((uVar10 == 0) || (iVar17 == 0)) {
    iVar17 = 0;
  }
  else {
    lVar1 = (longlong)iVar17 * (longlong)(int)uVar10;
    iVar4 = (int)((ulonglong)lVar1 >> 0x20);
    if (iVar17 < 0) {
      iVar4 = iVar4 + 1;
      if ((iVar4 < 0 == (-1 < lVar1 && iVar4 < 0)) && (0x80000000 < uVar10 * iVar17))
      goto LAB_0003323e;
      iVar17 = -0x7fffffff;
    }
    else if ((lVar1 < 0 || iVar4 == 0) && (uVar10 * iVar17 < 0x80000000)) {
LAB_0003323e:
      iVar17 = uVar10 * iVar17;
    }
    else {
      iVar17 = 0x7fffffff;
    }
  }
  if ((uVar9 == 0) || (iVar15 == 0)) {
    iVar15 = 0;
  }
  else {
    lVar1 = (longlong)iVar15 * (longlong)(int)uVar9;
    iVar4 = (int)((ulonglong)lVar1 >> 0x20);
    if (iVar15 < 0) {
      iVar4 = iVar4 + 1;
      if ((iVar4 < 0 == (-1 < lVar1 && iVar4 < 0)) && (0x80000000 < uVar9 * iVar15))
      goto LAB_0003327e;
      iVar15 = -0x7fffffff;
    }
    else if ((lVar1 < 0 || iVar4 == 0) && (uVar9 * iVar15 < 0x80000000)) {
LAB_0003327e:
      iVar15 = uVar9 * iVar15;
    }
    else {
      iVar15 = 0x7fffffff;
    }
  }
  if ((uVar8 == 0) || (iVar14 == 0)) {
    iVar14 = 0;
  }
  else {
    lVar1 = (longlong)iVar14 * (longlong)(int)uVar8;
    iVar4 = (int)((ulonglong)lVar1 >> 0x20);
    if (iVar14 < 0) {
      iVar4 = iVar4 + 1;
      if ((iVar4 < 0 == (-1 < lVar1 && iVar4 < 0)) && (0x80000000 < uVar8 * iVar14))
      goto LAB_000332be;
      iVar14 = -0x7fffffff;
    }
    else if ((lVar1 < 0 || iVar4 == 0) && (uVar8 * iVar14 < 0x80000000)) {
LAB_000332be:
      iVar14 = uVar8 * iVar14;
    }
    else {
      iVar14 = 0x7fffffff;
    }
  }
  if ((uVar7 == 0) || (iVar3 == 0)) {
    iVar3 = 0;
  }
  else {
    lVar1 = (longlong)iVar3 * (longlong)(int)uVar7;
    iVar4 = (int)((ulonglong)lVar1 >> 0x20);
    if (iVar3 < 0) {
      iVar4 = iVar4 + 1;
      if ((iVar4 < 0 == (-1 < lVar1 && iVar4 < 0)) && (0x80000000 < uVar7 * iVar3))
      goto LAB_000332fe;
      iVar3 = -0x7fffffff;
    }
    else if ((lVar1 < 0 || iVar4 == 0) && (uVar7 * iVar3 < 0x80000000)) {
LAB_000332fe:
      iVar3 = uVar7 * iVar3;
    }
    else {
      iVar3 = 0x7fffffff;
    }
  }
  if ((uVar6 == 0) || (iVar12 == 0)) {
    uVar6 = 0;
  }
  else {
    lVar1 = (longlong)iVar12 * (longlong)(int)uVar6;
    iVar4 = (int)((ulonglong)lVar1 >> 0x20);
    if (iVar12 < 0) {
      iVar4 = iVar4 + 1;
      if ((iVar4 < 0 != (-1 < lVar1 && iVar4 < 0)) || (uVar6 = uVar6 * iVar12, uVar6 < 0x80000001))
      {
        uVar6 = 0x80000001;
      }
    }
    else if ((-1 < lVar1 && iVar4 != 0) || (uVar6 = (int)uVar6 * iVar12, 0x7fffffff < (int)uVar6)) {
      uVar6 = 0x7fffffff;
    }
  }
  iVar4 = iVar3 / 0x8000 + iVar2 / 0x8000;
  iVar20 = (int)uVar6 / 0x8000 + iVar17 / 0x8000;
  iVar12 = iVar4 - iVar20;
  iVar20 = iVar20 + iVar4;
  iVar3 = iVar3 / 0x8000 + iVar15 / 0x8000;
  iVar15 = iVar15 / 0x8000 + iVar2 / 0x8000;
  iVar4 = iVar14 / 0x8000 + iVar17 / 0x8000;
  iVar14 = (int)uVar6 / 0x8000 + iVar14 / 0x8000;
  iVar2 = iVar15 - iVar4;
  iVar17 = iVar3 - iVar14;
  iVar4 = iVar4 + iVar15;
  iVar14 = iVar14 + iVar3;
  if (iVar12 + 0x7fff < 0 == (-1 < iVar12 && iVar12 + 0x7fff < 0) && iVar12 != -0x7fff) {
    if (iVar12 + -0x7fff < 0 == (iVar12 < 0 && -1 < iVar12 + -0x7fff) && iVar12 != 0x7fff) {
      iVar15 = 0x7fff;
    }
    else {
      iVar15 = (int)(short)iVar12;
    }
  }
  else {
    iVar15 = -0x7fff;
  }
  if (iVar20 + 0x7fff < 0 == (-1 < iVar20 && iVar20 + 0x7fff < 0) && iVar20 != -0x7fff) {
    if (iVar20 + -0x7fff < 0 == (iVar20 < 0 && -1 < iVar20 + -0x7fff) && iVar20 != 0x7fff) {
      iVar3 = 0x7fff;
    }
    else {
      iVar3 = (int)(short)iVar20;
    }
  }
  else {
    iVar3 = -0x7fff;
  }
  if (iVar2 + 0x7fff < 0 == (-1 < iVar2 && iVar2 + 0x7fff < 0) && iVar2 != -0x7fff) {
    if (iVar2 + -0x7fff < 0 == (iVar2 < 0 && -1 < iVar2 + -0x7fff) && iVar2 != 0x7fff) {
      iVar2 = 0x7fff;
    }
    else {
      iVar2 = (int)(short)iVar2;
    }
  }
  else {
    iVar2 = -0x7fff;
  }
  if (iVar4 + 0x7fff < 0 == (-1 < iVar4 && iVar4 + 0x7fff < 0) && iVar4 != -0x7fff) {
    if (iVar4 + -0x7fff < 0 == (iVar4 < 0 && -1 < iVar4 + -0x7fff) && iVar4 != 0x7fff) {
      iVar12 = 0x7fff;
    }
    else {
      iVar12 = (int)(short)iVar4;
    }
  }
  else {
    iVar12 = -0x7fff;
  }
  if (iVar17 + 0x7fff < 0 == (-1 < iVar17 && iVar17 + 0x7fff < 0) && iVar17 != -0x7fff) {
    iVar4 = (int)(short)iVar17;
    if (iVar17 + -0x7fff < 0 == (iVar17 < 0 && -1 < iVar17 + -0x7fff) && iVar17 != 0x7fff) {
      iVar4 = 0x7fff;
    }
  }
  else {
    iVar4 = -0x7fff;
  }
  if (iVar14 + 0x7fff < 0 == (-1 < iVar14 && iVar14 + 0x7fff < 0) && iVar14 != -0x7fff) {
    iVar17 = (int)(short)iVar14;
    if (iVar14 + -0x7fff < 0 == (iVar14 < 0 && -1 < iVar14 + -0x7fff) && iVar14 != 0x7fff) {
      iVar17 = 0x7fff;
    }
  }
  else {
    iVar17 = -0x7fff;
  }
  if (six_channel_fit_work.signed_initialized == '\0') {
    sStack_3a = (short)iVar17;
    sStack_3c = (short)iVar4;
    sStack_3e = (short)iVar12;
    sStack_40 = (short)iVar2;
    sStack_42 = (short)iVar3;
    sStack_44 = (short)iVar15;
    iStack_50 = iVar12 << 0x10;
    iVar18 = iVar2 << 0x10;
    iVar19 = iVar3 << 0x10;
    iVar20 = iVar15 << 0x10;
    iStack_4c = iVar4 << 0x10;
    iStack_48 = iVar17 << 0x10;
    six_channel_fit_work.coverage_max = 0;
    six_channel_fit_work.coverage_min = 0;
    six_channel_fit_work.coverage_sum = 0;
    six_channel_fit_work.coverage_count = '\0';
    uStack_52 = 'Z';
    sStack_38 = sStack_44;
    sStack_36 = sStack_42;
    sStack_34 = sStack_40;
    sStack_32 = sStack_3e;
    sStack_30 = sStack_3c;
    sStack_2e = sStack_3a;
  }
  else {
    iVar14 = (uint)fit_parameters.signed_filter_half_gain * 2;
    uVar6 = iVar14 - 1;
    if (uVar6 < 0xffff) {
      iVar20 = six_channel_fit_work.signed_previous[0] * iVar14;
      iVar15 = iVar15 * iVar14;
    }
    else {
      iVar20 = (int)six_channel_fit_work.signed_previous[0] << 0x10;
      iVar15 = iVar15 << 0x10;
    }
    iVar20 = iVar15 + (six_channel_fit_work.signed_q16[0] - iVar20);
    sVar26 = (short)(iVar20 / 0x10000);
    iVar15 = (int)sVar26;
    if (uVar6 < 0xffff) {
      iVar19 = six_channel_fit_work.signed_previous[1] * iVar14;
      iVar3 = iVar3 * iVar14;
    }
    else {
      iVar19 = (int)six_channel_fit_work.signed_previous[1] << 0x10;
      iVar3 = iVar3 << 0x10;
    }
    iVar19 = iVar3 + (six_channel_fit_work.signed_q16[1] - iVar19);
    sVar25 = (short)(iVar19 / 0x10000);
    iVar3 = (int)sVar25;
    if (uVar6 < 0xffff) {
      iVar18 = six_channel_fit_work.signed_previous[2] * iVar14;
      iVar2 = iVar2 * iVar14;
    }
    else {
      iVar18 = (int)six_channel_fit_work.signed_previous[2] << 0x10;
      iVar2 = iVar2 << 0x10;
    }
    iVar18 = iVar2 + (six_channel_fit_work.signed_q16[2] - iVar18);
    sVar24 = (short)(iVar18 / 0x10000);
    iVar2 = (int)sVar24;
    if (uVar6 < 0xffff) {
      iVar16 = six_channel_fit_work.signed_previous[3] * iVar14;
      iVar12 = iVar12 * iVar14;
    }
    else {
      iVar16 = (int)six_channel_fit_work.signed_previous[3] << 0x10;
      iVar12 = iVar12 << 0x10;
    }
    iStack_50 = iVar12 + (six_channel_fit_work.signed_q16[3] - iVar16);
    sVar23 = (short)(iStack_50 / 0x10000);
    iVar12 = (int)sVar23;
    if (uVar6 < 0xffff) {
      iVar16 = six_channel_fit_work.signed_previous[4] * iVar14;
      iVar4 = iVar4 * iVar14;
    }
    else {
      iVar16 = (int)six_channel_fit_work.signed_previous[4] << 0x10;
      iVar4 = iVar4 << 0x10;
    }
    iStack_4c = iVar4 + (six_channel_fit_work.signed_q16[4] - iVar16);
    sVar22 = (short)(iStack_4c / 0x10000);
    iVar4 = (int)sVar22;
    if (uVar6 < 0xffff) {
      iVar16 = six_channel_fit_work.signed_previous[5] * iVar14;
      iVar17 = iVar17 * iVar14;
    }
    else {
      iVar16 = (int)six_channel_fit_work.signed_previous[5] << 0x10;
      iVar17 = iVar17 << 0x10;
    }
    iVar14 = (int)six_channel_fit_work.signed_max[0];
    iVar13 = (int)six_channel_fit_work.signed_max[1];
    iStack_48 = iVar17 + (six_channel_fit_work.signed_q16[5] - iVar16);
    iVar16 = (int)six_channel_fit_work.signed_max[2];
    if (iVar15 - iVar14 < 0 == (iVar15 < 0 != iVar14 < 0 && iVar14 < 0 == iVar15 - iVar14 < 0) &&
        iVar15 != iVar14) {
      sStack_44 = sVar26;
    }
    sVar21 = (short)(iStack_48 / 0x10000);
    iVar17 = (int)sVar21;
    iVar14 = (int)six_channel_fit_work.signed_max[3];
    if (iVar3 - iVar13 < 0 == (iVar3 < 0 != iVar13 < 0 && iVar13 < 0 == iVar3 - iVar13 < 0) &&
        iVar3 != iVar13) {
      sStack_42 = sVar25;
    }
    iVar13 = (int)six_channel_fit_work.signed_max[4];
    if (iVar2 - iVar16 < 0 == (iVar2 < 0 != iVar16 < 0 && iVar16 < 0 == iVar2 - iVar16 < 0) &&
        iVar2 != iVar16) {
      sStack_40 = sVar24;
    }
    iVar16 = (int)six_channel_fit_work.signed_max[5];
    if (iVar12 - iVar14 < 0 == (iVar12 < 0 != iVar14 < 0 && iVar14 < 0 == iVar12 - iVar14 < 0) &&
        iVar12 != iVar14) {
      sStack_3e = sVar23;
    }
    iVar14 = (int)six_channel_fit_work.signed_min[0];
    if (iVar4 - iVar13 < 0 == (iVar4 < 0 != iVar13 < 0 && iVar13 < 0 == iVar4 - iVar13 < 0) &&
        iVar4 != iVar13) {
      sStack_3c = sVar22;
    }
    iVar13 = (int)six_channel_fit_work.signed_min[1];
    if (iVar17 - iVar16 < 0 == (iVar17 < 0 != iVar16 < 0 && iVar16 < 0 == iVar17 - iVar16 < 0) &&
        iVar17 != iVar16) {
      sStack_3a = sVar21;
    }
    iVar16 = (int)six_channel_fit_work.signed_min[2];
    if (iVar15 - iVar14 < 0 != (iVar15 < 0 != iVar14 < 0 && iVar14 < 0 == iVar15 - iVar14 < 0)) {
      sStack_38 = sVar26;
    }
    iVar14 = (int)six_channel_fit_work.signed_min[3];
    if (iVar3 - iVar13 < 0 != (iVar3 < 0 != iVar13 < 0 && iVar13 < 0 == iVar3 - iVar13 < 0)) {
      sStack_36 = sVar25;
    }
    iVar13 = (int)six_channel_fit_work.signed_min[4];
    if (iVar2 - iVar16 < 0 != (iVar2 < 0 != iVar16 < 0 && iVar16 < 0 == iVar2 - iVar16 < 0)) {
      sStack_34 = sVar24;
    }
    iVar16 = (int)six_channel_fit_work.signed_min[5];
    if (iVar12 - iVar14 < 0 != (iVar12 < 0 != iVar14 < 0 && iVar14 < 0 == iVar12 - iVar14 < 0)) {
      sStack_32 = sVar23;
    }
    if (iVar4 - iVar13 < 0 != (iVar4 < 0 != iVar13 < 0 && iVar13 < 0 == iVar4 - iVar13 < 0)) {
      sStack_30 = sVar22;
    }
    if (iVar17 - iVar16 < 0 != (iVar17 < 0 != iVar16 < 0 && iVar16 < 0 == iVar17 - iVar16 < 0)) {
      sStack_2e = sVar21;
    }
  }
  puVar5 = 0xfebeb800u;
  uVar6 = track_fit_angular_coverage(angle,fit_parameters.signed_coverage_spans);
  six_channel_fit_work.signed_q16[2] = iVar18;
  six_channel_fit_work.signed_q16[1] = iVar19;
  six_channel_fit_work.signed_q16[0] = iVar20;
  six_channel_fit_work.signed_previous[0] = (short)iVar15;
  six_channel_fit_work.signed_previous[1] = (short)iVar3;
  six_channel_fit_work.signed_previous[2] = (short)iVar2;
  six_channel_fit_work.signed_previous[3] = (short)iVar12;
  six_channel_fit_work.signed_previous[4] = (short)iVar4;
  six_channel_fit_work.signed_previous[5] = (short)iVar17;
  if (uVar6 == 0xa5) {
    uStack_51 = 'D';
  }
LAB_00033638:
  (*((uchar *)camry_host_ptr((uint32_t)((int)0xffffb162u + (int)(puVar5 + 1))))) = uStack_52;
  (*((uchar *)camry_host_ptr((uint32_t)((int)(0xffffb160u + (uint32_t)((int)puVar5)))))) = uStack_51;
  six_channel_fit_work.signed_max[0] = sStack_44;
  six_channel_fit_work.signed_max[1] = sStack_42;
  six_channel_fit_work.signed_max[2] = sStack_40;
  six_channel_fit_work.signed_max[3] = sStack_3e;
  six_channel_fit_work.signed_max[4] = sStack_3c;
  six_channel_fit_work.signed_max[5] = sStack_3a;
  six_channel_fit_work.signed_min[0] = sStack_38;
  six_channel_fit_work.signed_min[1] = sStack_36;
  six_channel_fit_work.signed_min[2] = sStack_34;
  six_channel_fit_work.signed_min[3] = sStack_32;
  six_channel_fit_work.signed_min[4] = sStack_30;
  six_channel_fit_work.signed_min[5] = sStack_2e;
  six_channel_fit_work.signed_q16[3] = iStack_50;
  six_channel_fit_work.signed_q16[4] = iStack_4c;
  six_channel_fit_work.signed_q16[5] = iStack_48;
  return;
}

void step_six_channel_fit(void)

{
  uint8_t stack_record_44[68];
  camry_fill_bytes(stack_record_44, sizeof stack_record_44);
  short sVar1;
  uint uVar2;
  uint uVar3;
  uint32_t puVar4;
  uint32_t puVar5;
  int iVar6;
  int iVar7;
  int iVar8;
  int iVar9;
  uint uVar10;
  uint uVar11;
  uint uVar12;
  int iVar13;
  uint uVar14;
  int iVar15;
  int iVar16;
  uint uVar17;
  uint uVar18;
  uint uVar19;
  uchar uVar20;
  int iVar21;
  int iVar22;
  int iVar23;
  int iVar24;
  int iVar25;
  
  sVar1 = (short)DAT_febe7d94;
  uVar20 = six_channel_fit_work.active;
  puVar5 = 0xfebeb800u;
  puVar4 = (uint32_t)(0xfebeb800u);
  if (six_channel_fit_work.active == 'Z') {
    if (six_channel_fit_work.state == '\0') {
      six_channel_fit_work.unsigned_initialized = '\0';
      six_channel_fit_work.state = '\x11';
      six_channel_fit_work.signed_initialized = '\0';
      six_channel_fit_work.coverage_count = '\0';
      six_channel_fit_work.coverage_sum = 0;
      six_channel_fit_work.coverage_min = 0;
      six_channel_fit_work.coverage_max = 0;
    }
    else if (six_channel_fit_work.state == '\x11') {
      puVar4 = (uint32_t)(0xfebeb800u);
      step_unsigned_literal_fit_sweep((short)DAT_febe7d94);
    }
    else if (six_channel_fit_work.state == '\"') {
      iVar6 = (uint)six_channel_fit_work.unsigned_max[0] -
              (uint)six_channel_fit_work.unsigned_min[0];
      (*((uint16_t *)(stack_record_44 + 12))) = six_channel_fit_work.first_gain[0];
      (*((uint16_t *)(stack_record_44 + 14))) = six_channel_fit_work.first_gain[1];
      (*((uint16_t *)(stack_record_44 + 16))) = six_channel_fit_work.first_gain[2];
      (*((uint16_t *)(stack_record_44 + 18))) = six_channel_fit_work.first_gain[3];
      iVar7 = (uint)six_channel_fit_work.unsigned_max[1] -
              (uint)six_channel_fit_work.unsigned_min[1];
      (*((uint16_t *)(stack_record_44 + 20))) = six_channel_fit_work.first_gain[4];
      iVar8 = (uint)six_channel_fit_work.unsigned_max[2] -
              (uint)six_channel_fit_work.unsigned_min[2];
      (*((uint16_t *)(stack_record_44 + 22))) = six_channel_fit_work.first_gain[5];
      iVar9 = (uint)six_channel_fit_work.unsigned_max[3] -
              (uint)six_channel_fit_work.unsigned_min[3];
      iVar13 = (uint)six_channel_fit_work.unsigned_max[4] -
               (uint)six_channel_fit_work.unsigned_min[4];
      iVar15 = (uint)six_channel_fit_work.unsigned_max[5] -
               (uint)six_channel_fit_work.unsigned_min[5];
      if ((((iVar6 < 1) || (iVar7 < 1)) || (iVar8 < 1)) ||
         (((iVar9 < 1 || (iVar13 < 1)) || (iVar15 < 1)))) {
        six_channel_fit_work.state = 'f';
      }
      else {
        uVar18 = (uint)fit_parameters.first_gain_numerator;
        uVar17 = uVar18 << 0xf;
        uVar11 = uVar17;
        if (iVar8 != 0) {
          if (uVar18 == 0x10000 && iVar8 == -1) {
            uVar11 = 0x80000000;
          }
          else {
            uVar11 = (int)uVar17 / iVar8;
          }
        }
        uVar3 = uVar17;
        if (iVar9 != 0) {
          if (uVar18 == 0x10000 && iVar9 == -1) {
            uVar3 = 0x80000000;
          }
          else {
            uVar3 = (int)uVar17 / iVar9;
          }
        }
        uVar19 = uVar17;
        if (iVar6 != 0) {
          if (uVar18 == 0x10000 && iVar6 == -1) {
            uVar19 = 0x80000000;
          }
          else {
            uVar19 = (int)uVar17 / iVar6;
          }
        }
        uVar2 = (uint)fit_parameters.gain_upper;
        uVar14 = uVar17;
        if (iVar7 != 0) {
          if (uVar18 == 0x10000 && iVar7 == -1) {
            uVar14 = 0x80000000;
          }
          else {
            uVar14 = (int)uVar17 / iVar7;
          }
        }
        uVar10 = uVar17;
        if (iVar13 != 0) {
          if (uVar18 == 0x10000 && iVar13 == -1) {
            uVar10 = 0x80000000;
          }
          else {
            uVar10 = (int)uVar17 / iVar13;
          }
        }
        if (iVar15 != 0) {
          if (uVar18 == 0x10000 && iVar15 == -1) {
            uVar17 = 0x80000000;
          }
          else {
            uVar17 = (int)uVar17 / iVar15;
          }
        }
        uVar18 = (uint)fit_parameters.gain_lower;
        if ((int)(uVar2 - uVar19) < 0 !=
            ((int)uVar19 < 0 && (int)uVar19 < 0 == (int)(uVar2 - uVar19) < 0)) {
          uVar19 = uVar2;
        }
        uVar12 = uVar18;
        if ((int)(uVar19 - uVar18) < 0 == ((int)uVar19 < 0 && -1 < (int)(uVar19 - uVar18))) {
          uVar12 = uVar19;
        }
        (*((uint16_t *)(stack_record_44 + 12))) = (ushort)uVar12;
        if ((int)(uVar2 - uVar14) < 0 !=
            ((int)uVar14 < 0 && (int)uVar14 < 0 == (int)(uVar2 - uVar14) < 0)) {
          uVar14 = uVar2;
        }
        uVar19 = uVar18;
        if ((int)(uVar14 - uVar18) < 0 == ((int)uVar14 < 0 && -1 < (int)(uVar14 - uVar18))) {
          uVar19 = uVar14;
        }
        (*((uint16_t *)(stack_record_44 + 14))) = (ushort)uVar19;
        if ((int)(uVar2 - uVar11) < 0 !=
            ((int)uVar11 < 0 && (int)uVar11 < 0 == (int)(uVar2 - uVar11) < 0)) {
          uVar11 = uVar2;
        }
        uVar19 = uVar18;
        if ((int)(uVar11 - uVar18) < 0 == ((int)uVar11 < 0 && -1 < (int)(uVar11 - uVar18))) {
          uVar19 = uVar11;
        }
        (*((uint16_t *)(stack_record_44 + 16))) = (ushort)uVar19;
        if ((int)(uVar2 - uVar3) < 0 !=
            ((int)uVar3 < 0 && (int)uVar3 < 0 == (int)(uVar2 - uVar3) < 0)) {
          uVar3 = uVar2;
        }
        uVar11 = uVar18;
        if ((int)(uVar3 - uVar18) < 0 == ((int)uVar3 < 0 && -1 < (int)(uVar3 - uVar18))) {
          uVar11 = uVar3;
        }
        (*((uint16_t *)(stack_record_44 + 18))) = (ushort)uVar11;
        if ((int)(uVar2 - uVar10) < 0 !=
            ((int)uVar10 < 0 && (int)uVar10 < 0 == (int)(uVar2 - uVar10) < 0)) {
          uVar10 = uVar2;
        }
        uVar11 = uVar18;
        if ((int)(uVar10 - uVar18) < 0 == ((int)uVar10 < 0 && -1 < (int)(uVar10 - uVar18))) {
          uVar11 = uVar10;
        }
        (*((uint16_t *)(stack_record_44 + 20))) = (ushort)uVar11;
        if ((int)(uVar2 - uVar17) < 0 !=
            ((int)uVar17 < 0 && (int)uVar17 < 0 == (int)(uVar2 - uVar17) < 0)) {
          uVar17 = uVar2;
        }
        if ((int)(uVar17 - uVar18) < 0 == ((int)uVar17 < 0 && -1 < (int)(uVar17 - uVar18))) {
          uVar18 = uVar17;
        }
        (*((uint16_t *)(stack_record_44 + 22))) = (ushort)uVar18;
        six_channel_fit_work.first_center[0] =
             (ushort)((uint)six_channel_fit_work.unsigned_min[0] +
                      (uint)six_channel_fit_work.unsigned_max[0] >> 1);
        six_channel_fit_work.first_center[1] =
             (ushort)((uint)six_channel_fit_work.unsigned_min[1] +
                      (uint)six_channel_fit_work.unsigned_max[1] >> 1);
        six_channel_fit_work.first_center[2] =
             (ushort)((uint)six_channel_fit_work.unsigned_min[2] +
                      (uint)six_channel_fit_work.unsigned_max[2] >> 1);
        six_channel_fit_work.first_center[3] =
             (ushort)((uint)six_channel_fit_work.unsigned_min[3] +
                      (uint)six_channel_fit_work.unsigned_max[3] >> 1);
        six_channel_fit_work.first_center[4] =
             (ushort)((uint)six_channel_fit_work.unsigned_min[4] +
                      (uint)six_channel_fit_work.unsigned_max[4] >> 1);
        six_channel_fit_work.first_center[5] =
             (ushort)((uint)six_channel_fit_work.unsigned_min[5] +
                      (uint)six_channel_fit_work.unsigned_max[5] >> 1);
        six_channel_fit_work.state = '3';
      }
      six_channel_fit_work.first_gain[0] = (*((uint16_t *)(stack_record_44 + 12)));
      six_channel_fit_work.first_gain[3] = (*((uint16_t *)(stack_record_44 + 18)));
      six_channel_fit_work.first_gain[4] = (*((uint16_t *)(stack_record_44 + 20)));
      six_channel_fit_work.first_gain[1] = (*((uint16_t *)(stack_record_44 + 14)));
      six_channel_fit_work.first_gain[2] = (*((uint16_t *)(stack_record_44 + 16)));
      six_channel_fit_work.first_gain[5] = (*((uint16_t *)(stack_record_44 + 22)));
    }
    else if (six_channel_fit_work.state == '3') {
      puVar4 = (uint32_t)(0xfebeb800u);
      step_signed_constant_fit_sweep((short)DAT_febe7d94);
    }
    else if (six_channel_fit_work.state == 'D') {
      iVar8 = (int)six_channel_fit_work.signed_max[0];
      iVar6 = (int)six_channel_fit_work.signed_max[1];
      iVar24 = (int)six_channel_fit_work.signed_max[2];
      iVar16 = (int)six_channel_fit_work.signed_min[0];
      iVar15 = (int)six_channel_fit_work.signed_min[1];
      iVar13 = (int)six_channel_fit_work.signed_min[2];
      (*((uint16_t *)(stack_record_44 + 0))) = six_channel_fit_work.component_angle[0];
      (*((uint16_t *)(stack_record_44 + 2))) = six_channel_fit_work.component_angle[1];
      (*((uint16_t *)(stack_record_44 + 14))) = six_channel_fit_work.second_gain[1];
      (*((uint16_t *)(stack_record_44 + 4))) = six_channel_fit_work.component_angle[2];
      (*((uint16_t *)(stack_record_44 + 20))) = six_channel_fit_work.second_gain[4];
      (*((uint16_t *)(stack_record_44 + 22))) = six_channel_fit_work.second_gain[5];
      (*((uint16_t *)(stack_record_44 + 16))) = six_channel_fit_work.second_gain[2];
      (*((uint16_t *)(stack_record_44 + 18))) = six_channel_fit_work.second_gain[3];
      (*((int16_t *)(stack_record_44 + 6))) = (short)(((int)six_channel_fit_work.signed_min[3] +
                          (int)six_channel_fit_work.signed_max[3]) / 2);
      (*((uint16_t *)(stack_record_44 + 12))) = six_channel_fit_work.second_gain[0];
      (*((int16_t *)(stack_record_44 + 10))) = (short)(((int)six_channel_fit_work.signed_min[5] +
                          (int)six_channel_fit_work.signed_max[5]) / 2);
      iVar9 = (int)(short)((iVar8 - iVar16) / 2);
      (*((int16_t *)(stack_record_44 + 8))) = (short)(((int)six_channel_fit_work.signed_min[4] +
                          (int)six_channel_fit_work.signed_max[4]) / 2);
      iVar7 = (int)(short)((iVar6 - iVar15) / 2);
      iVar25 = (int)(short)((iVar24 - iVar13) / 2);
      iVar23 = (int)(short)(((int)six_channel_fit_work.signed_max[3] -
                            (int)six_channel_fit_work.signed_min[3]) / 2);
      iVar22 = (int)(short)(((int)six_channel_fit_work.signed_max[4] -
                            (int)six_channel_fit_work.signed_min[4]) / 2);
      iVar21 = (int)(short)(((int)six_channel_fit_work.signed_max[5] -
                            (int)six_channel_fit_work.signed_min[5]) / 2);
      if (((iVar9 < 1) || (iVar7 < 1)) ||
         ((iVar25 < 1 || (((iVar23 < 1 || (iVar22 < 1)) || (iVar21 < 1)))))) {
        six_channel_fit_work.state = 'f';
        puVar4 = (uint32_t)(0xfebeb800u);
      }
      else {
        uVar3 = (uint)fit_parameters.gain_upper;
        uVar19 = (uint)fit_parameters.gain_lower;
        uVar18 = (uint)fit_parameters.second_gain_numerator;
        uVar17 = uVar18 << 0xf;
        uVar11 = uVar17;
        if (iVar9 != 0) {
          if (uVar18 == 0x10000 && iVar9 == -1) {
            uVar11 = 0x80000000;
          }
          else {
            uVar11 = (int)uVar17 / iVar9;
          }
        }
        uVar14 = uVar17;
        if (iVar7 != 0) {
          if (uVar18 == 0x10000 && iVar7 == -1) {
            uVar14 = 0x80000000;
          }
          else {
            uVar14 = (int)uVar17 / iVar7;
          }
        }
        uVar2 = uVar17;
        if (iVar25 != 0) {
          if (uVar18 == 0x10000 && iVar25 == -1) {
            uVar2 = 0x80000000;
          }
          else {
            uVar2 = (int)uVar17 / iVar25;
          }
        }
        uVar10 = uVar17;
        if (iVar23 != 0) {
          if (uVar18 == 0x10000 && iVar23 == -1) {
            uVar10 = 0x80000000;
          }
          else {
            uVar10 = (int)uVar17 / iVar23;
          }
        }
        uVar12 = uVar17;
        if (iVar22 != 0) {
          if (uVar18 == 0x10000 && iVar22 == -1) {
            uVar12 = 0x80000000;
          }
          else {
            uVar12 = (int)uVar17 / iVar22;
          }
        }
        if (iVar21 != 0) {
          if (uVar18 == 0x10000 && iVar21 == -1) {
            uVar17 = 0x80000000;
          }
          else {
            uVar17 = (int)uVar17 / iVar21;
          }
        }
        if ((int)(uVar3 - uVar11) < 0 !=
            ((int)uVar11 < 0 && (int)uVar11 < 0 == (int)(uVar3 - uVar11) < 0)) {
          uVar11 = uVar3;
        }
        uVar18 = uVar19;
        if ((int)(uVar11 - uVar19) < 0 == ((int)uVar11 < 0 && -1 < (int)(uVar11 - uVar19))) {
          uVar18 = uVar11;
        }
        (*((uint16_t *)(stack_record_44 + 12))) = (ushort)uVar18;
        if ((int)(uVar3 - uVar14) < 0 !=
            ((int)uVar14 < 0 && (int)uVar14 < 0 == (int)(uVar3 - uVar14) < 0)) {
          uVar14 = uVar3;
        }
        uVar18 = uVar19;
        if ((int)(uVar14 - uVar19) < 0 == ((int)uVar14 < 0 && -1 < (int)(uVar14 - uVar19))) {
          uVar18 = uVar14;
        }
        (*((uint16_t *)(stack_record_44 + 14))) = (ushort)uVar18;
        if ((int)(uVar3 - uVar2) < 0 !=
            ((int)uVar2 < 0 && (int)uVar2 < 0 == (int)(uVar3 - uVar2) < 0)) {
          uVar2 = uVar3;
        }
        uVar18 = uVar19;
        if ((int)(uVar2 - uVar19) < 0 == ((int)uVar2 < 0 && -1 < (int)(uVar2 - uVar19))) {
          uVar18 = uVar2;
        }
        (*((uint16_t *)(stack_record_44 + 16))) = (ushort)uVar18;
        if ((int)(uVar3 - uVar10) < 0 !=
            ((int)uVar10 < 0 && (int)uVar10 < 0 == (int)(uVar3 - uVar10) < 0)) {
          uVar10 = uVar3;
        }
        uVar18 = uVar19;
        if ((int)(uVar10 - uVar19) < 0 == ((int)uVar10 < 0 && -1 < (int)(uVar10 - uVar19))) {
          uVar18 = uVar10;
        }
        (*((uint16_t *)(stack_record_44 + 18))) = (ushort)uVar18;
        if ((int)(uVar3 - uVar12) < 0 !=
            ((int)uVar12 < 0 && (int)uVar12 < 0 == (int)(uVar3 - uVar12) < 0)) {
          uVar12 = uVar3;
        }
        uVar18 = uVar19;
        if ((int)(uVar12 - uVar19) < 0 == ((int)uVar12 < 0 && -1 < (int)(uVar12 - uVar19))) {
          uVar18 = uVar12;
        }
        (*((uint16_t *)(stack_record_44 + 20))) = (ushort)uVar18;
        if ((int)(uVar3 - uVar17) < 0 !=
            ((int)uVar17 < 0 && (int)uVar17 < 0 == (int)(uVar3 - uVar17) < 0)) {
          uVar17 = uVar3;
        }
        (*((uint16_t *)(stack_record_44 + 22))) = fit_parameters.gain_lower;
        if ((int)(uVar17 - uVar19) < 0 == ((int)uVar17 < 0 && -1 < (int)(uVar17 - uVar19))) {
          (*((uint16_t *)(stack_record_44 + 22))) = (ushort)uVar17;
        }
        compute_s16_atan2_turn_angle_70be0(iVar7,iVar9,((uint16_t *)(stack_record_44)));
        compute_s16_atan2_turn_angle_70be0(iVar23,iVar25,((uint16_t *)((stack_record_44 + 2))));
        compute_s16_atan2_turn_angle_70be0(iVar21,iVar22,((uint16_t *)((stack_record_44 + 4))));
        six_channel_fit_work.state = 'U';
        puVar4 = (uint32_t)((uint32_t)(puVar5));
      }
      six_channel_fit_work.second_gain[5] = (*((uint16_t *)(stack_record_44 + 22)));
      six_channel_fit_work.second_center[0] = (short)((iVar16 + iVar8) / 2);
      six_channel_fit_work.second_center[1] = (short)((iVar15 + iVar6) / 2);
      six_channel_fit_work.second_center[2] = (short)((iVar13 + iVar24) / 2);
      six_channel_fit_work.second_gain[0] = (*((uint16_t *)(stack_record_44 + 12)));
      six_channel_fit_work.second_gain[1] = (*((uint16_t *)(stack_record_44 + 14)));
      six_channel_fit_work.second_center[3] = (*((int16_t *)(stack_record_44 + 6)));
      six_channel_fit_work.second_gain[2] = (*((uint16_t *)(stack_record_44 + 16)));
      six_channel_fit_work.second_gain[3] = (*((uint16_t *)(stack_record_44 + 18)));
      six_channel_fit_work.second_gain[4] = (*((uint16_t *)(stack_record_44 + 20)));
      six_channel_fit_work.second_center[4] = (*((int16_t *)(stack_record_44 + 8)));
      six_channel_fit_work.component_angle[0] = (*((uint16_t *)(stack_record_44 + 0)));
      six_channel_fit_work.second_center[5] = (*((int16_t *)(stack_record_44 + 10)));
      six_channel_fit_work.component_angle[1] = (*((uint16_t *)(stack_record_44 + 2)));
      six_channel_fit_work.component_angle[2] = (*((uint16_t *)(stack_record_44 + 4)));
    }
    else if ((six_channel_fit_work.state == 'U') || (six_channel_fit_work.state == 'f')) {
      uVar20 = '\0';
    }
    else {
      six_channel_fit_work.state = 'f';
    }
  }
  (*((short *)camry_host_ptr((uint32_t)((int)0xffffb166u + (int)puVar4)))) = sVar1;
  (*((uchar *)camry_host_ptr((uint32_t)((int)0xffffb160u + (int)((uint32_t)((uint32_t)(0xfebeb800u + (uint32_t)(1) * 1u))))))) = uVar20;
  return;
}

void begin_six_channel_fit(void)

{
  six_channel_fit_work.state = '\0';
  six_channel_fit_work.active = 'Z';
  return;
}

void return_only_stub_33ab2(void)

{
  return;
}

void return_only_stub_33ab4(void)

{
  return;
}

uint compare_retained_fit_coefficients(void)

{
  uint uVar1;
  
  if (((((((published_fit_coefficients.first_center[0] ==
            retained_fit_coefficients.first_center[0]) &&
          (published_fit_coefficients.first_center[1] ==
           retained_fit_coefficients.first_center[1])) &&
         (published_fit_coefficients.first_center[2] ==
          retained_fit_coefficients.first_center[2])) &&
        ((published_fit_coefficients.first_center[3] ==
          retained_fit_coefficients.first_center[3] &&
         (published_fit_coefficients.first_center[4] ==
          retained_fit_coefficients.first_center[4])))) &&
       (published_fit_coefficients.first_center[5] ==
        retained_fit_coefficients.first_center[5])) &&
      (((((published_fit_coefficients.first_gain[0] ==
           retained_fit_coefficients.first_gain[0] &&
          (published_fit_coefficients.first_gain[1] ==
           retained_fit_coefficients.first_gain[1])) &&
         ((published_fit_coefficients.first_gain[2] ==
           retained_fit_coefficients.first_gain[2] &&
          (((published_fit_coefficients.first_gain[3] ==
             retained_fit_coefficients.first_gain[3] &&
            (published_fit_coefficients.first_gain[4] ==
             retained_fit_coefficients.first_gain[4])) &&
           (published_fit_coefficients.first_gain[5] ==
            retained_fit_coefficients.first_gain[5])))))) &&
        (((published_fit_coefficients.second_center[0] ==
           retained_fit_coefficients.second_center[0] &&
          (published_fit_coefficients.second_center[1] ==
           retained_fit_coefficients.second_center[1])) &&
         ((published_fit_coefficients.second_center[2] ==
           retained_fit_coefficients.second_center[2] &&
          ((((published_fit_coefficients.second_center[3] ==
              retained_fit_coefficients.second_center[3] &&
             (published_fit_coefficients.second_center[4] ==
              retained_fit_coefficients.second_center[4])) &&
            ((published_fit_coefficients.second_center[5] ==
              retained_fit_coefficients.second_center[5] &&
             (((published_fit_coefficients.second_gain[0] ==
                retained_fit_coefficients.second_gain[0] &&
               (published_fit_coefficients.second_gain[1] ==
                retained_fit_coefficients.second_gain[1])) &&
              (published_fit_coefficients.second_gain[2] ==
               retained_fit_coefficients.second_gain[2])))))) &&
           ((published_fit_coefficients.second_gain[3] ==
             retained_fit_coefficients.second_gain[3] &&
            (published_fit_coefficients.second_gain[4] ==
             retained_fit_coefficients.second_gain[4])))))))))) &&
       (published_fit_coefficients.second_gain[5] ==
        retained_fit_coefficients.second_gain[5])))) &&
     (((published_fit_coefficients.component_angle[0] ==
        retained_fit_coefficients.component_angle[0] &&
       (published_fit_coefficients.component_angle[1] ==
        retained_fit_coefficients.component_angle[1])) &&
      (published_fit_coefficients.component_angle[2] ==
       retained_fit_coefficients.component_angle[2])))) {
    uVar1 = 0;
  }
  else {
    uVar1 = 0x5a;
  }
  return uVar1;
}

void copy_retained_fit_coefficients(void)

{
  published_fit_coefficients.first_center[0] = retained_fit_coefficients.first_center[0];
  published_fit_coefficients.first_center[1] = retained_fit_coefficients.first_center[1];
  published_fit_coefficients.first_center[2] = retained_fit_coefficients.first_center[2];
  published_fit_coefficients.first_center[3] = retained_fit_coefficients.first_center[3];
  published_fit_coefficients.first_center[4] = retained_fit_coefficients.first_center[4];
  published_fit_coefficients.first_center[5] = retained_fit_coefficients.first_center[5];
  published_fit_coefficients.first_gain[0] = retained_fit_coefficients.first_gain[0];
  published_fit_coefficients.first_gain[1] = retained_fit_coefficients.first_gain[1];
  published_fit_coefficients.first_gain[2] = retained_fit_coefficients.first_gain[2];
  published_fit_coefficients.first_gain[3] = retained_fit_coefficients.first_gain[3];
  published_fit_coefficients.first_gain[4] = retained_fit_coefficients.first_gain[4];
  published_fit_coefficients.first_gain[5] = retained_fit_coefficients.first_gain[5];
  published_fit_coefficients.second_center[0] = retained_fit_coefficients.second_center[0];
  published_fit_coefficients.second_center[1] = retained_fit_coefficients.second_center[1];
  published_fit_coefficients.second_center[2] = retained_fit_coefficients.second_center[2];
  published_fit_coefficients.second_center[3] = retained_fit_coefficients.second_center[3];
  published_fit_coefficients.second_center[4] = retained_fit_coefficients.second_center[4];
  published_fit_coefficients.second_center[5] = retained_fit_coefficients.second_center[5];
  published_fit_coefficients.second_gain[0] = retained_fit_coefficients.second_gain[0];
  published_fit_coefficients.second_gain[1] = retained_fit_coefficients.second_gain[1];
  published_fit_coefficients.second_gain[2] = retained_fit_coefficients.second_gain[2];
  published_fit_coefficients.second_gain[3] = retained_fit_coefficients.second_gain[3];
  published_fit_coefficients.second_gain[4] = retained_fit_coefficients.second_gain[4];
  published_fit_coefficients.second_gain[5] = retained_fit_coefficients.second_gain[5];
  published_fit_coefficients.component_angle[0] =
       retained_fit_coefficients.component_angle[0];
  published_fit_coefficients.component_angle[1] =
       retained_fit_coefficients.component_angle[1];
  published_fit_coefficients.component_angle[2] =
       retained_fit_coefficients.component_angle[2];
  return;
}

void reset_published_fit_coefficients(void)

{
  published_fit_coefficients.first_center[0] = 0x8000;
  published_fit_coefficients.first_center[1] = 0x8000;
  published_fit_coefficients.first_center[2] = 0x8000;
  published_fit_coefficients.first_center[3] = 0x8000;
  published_fit_coefficients.first_center[4] = 0x8000;
  published_fit_coefficients.first_center[5] = 0x8000;
  published_fit_coefficients.first_gain[0] = 0x8000;
  published_fit_coefficients.first_gain[1] = 0x8000;
  published_fit_coefficients.first_gain[2] = 0x8000;
  published_fit_coefficients.first_gain[3] = 0x8000;
  published_fit_coefficients.first_gain[4] = 0x8000;
  published_fit_coefficients.first_gain[5] = 0x8000;
  published_fit_coefficients.second_gain[0] = 0x8000;
  published_fit_coefficients.second_gain[1] = 0x8000;
  published_fit_coefficients.second_gain[2] = 0x8000;
  published_fit_coefficients.second_gain[3] = 0x8000;
  published_fit_coefficients.second_gain[4] = 0x8000;
  published_fit_coefficients.second_gain[5] = 0x8000;
  published_fit_coefficients.second_center[0] = 0;
  published_fit_coefficients.second_center[1] = 0;
  published_fit_coefficients.second_center[2] = 0;
  published_fit_coefficients.second_center[3] = 0;
  published_fit_coefficients.second_center[4] = 0;
  published_fit_coefficients.second_center[5] = 0;
  published_fit_coefficients.component_angle[0] = 0x2000;
  published_fit_coefficients.component_angle[1] = 0x2000;
  published_fit_coefficients.component_angle[2] = 0x2000;
  return;
}

void step_retained_fit_coherence(void)

{
  uint32_t puVar1;
  uint uVar2;
  uint uVar3;
  
  puVar1 = 0xfebeb800u;
  if (DAT_febe8a18 != 'Z') {
    return;
  }
  uVar3 = (uint)DAT_febe6a24;
  uVar2 = (uint)DAT_febe6a25;
  if (DAT_febe6abc == -0x5aa5a55b) {
    puVar1 = 0xfebeb800u;
    uVar3 = compare_retained_fit_coefficients();
    if (uVar3 != 0x5a) {
      uVar2 = 0;
      goto LAB_00033d24;
    }
    uVar2 = check_fit_record_admission();
    if (uVar2 == 0) {
      copy_retained_fit_coefficients();
      goto LAB_00033d24;
    }
  }
  reset_published_fit_coefficients();
LAB_00033d24:
  (*((char *)camry_host_ptr((uint32_t)((int)(0xffffb224u + (uint32_t)((int)puVar1)))))) = (char)uVar3;
  (*((char *)camry_host_ptr((uint32_t)((int)0xffffb224u + (int)(puVar1 + 1))))) = (char)uVar2;
  return;
}

void return_only_stub_33d30(void)

{
  return;
}

void clear_state_byte_pair_6a5c_33d32(void)

{
  DAT_febe6a5c = 0;
  DAT_febe6a5d = 0;
  return;
}

uint check_foreground_fit_bounds(void)

{
  uint uVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  int iVar6;
  
  uVar1 = 0;
  iVar6 = (int)((int)(int16_t)DAT_febe6566);
  iVar5 = (int)((int)(int16_t)DAT_febe6568);
  iVar4 = (int)((int)(int16_t)DAT_febe656a);
  iVar3 = (int)(short)fit_parameters.candidate_bound_words[7];
  iVar2 = (int)(short)fit_parameters.candidate_bound_words[6];
  if (((((((((fit_parameters.candidate_bound_words[1] <= DAT_febe6542) &&
            (DAT_febe6542 <= fit_parameters.candidate_bound_words[0])) &&
           (fit_parameters.candidate_bound_words[1] <= DAT_febe6544)) &&
          ((DAT_febe6544 <= fit_parameters.candidate_bound_words[0] &&
           (fit_parameters.candidate_bound_words[1] <= DAT_febe6546)))) &&
         (DAT_febe6546 <= fit_parameters.candidate_bound_words[0])) &&
        (((fit_parameters.candidate_bound_words[1] <= DAT_febe6548 &&
          (DAT_febe6548 <= fit_parameters.candidate_bound_words[0])) &&
         ((fit_parameters.candidate_bound_words[1] <= DAT_febe654a &&
          (((DAT_febe654a <= fit_parameters.candidate_bound_words[0] &&
            (fit_parameters.candidate_bound_words[1] <= DAT_febe654c)) &&
           (DAT_febe654c <= fit_parameters.candidate_bound_words[0])))))))) &&
       (((((fit_parameters.candidate_bound_words[3] <= DAT_febe654e &&
           (DAT_febe654e <= fit_parameters.candidate_bound_words[2])) &&
          ((fit_parameters.candidate_bound_words[3] <= DAT_febe6550 &&
           (((DAT_febe6550 <= fit_parameters.candidate_bound_words[2] &&
             (fit_parameters.candidate_bound_words[3] <= DAT_febe6552)) &&
            ((DAT_febe6552 <= fit_parameters.candidate_bound_words[2] &&
             (((fit_parameters.candidate_bound_words[3] <= DAT_febe6554 &&
               (DAT_febe6554 <= fit_parameters.candidate_bound_words[2])) &&
              (fit_parameters.candidate_bound_words[3] <= DAT_febe6556)))))))))) &&
         ((DAT_febe6556 <= fit_parameters.candidate_bound_words[2] &&
          (fit_parameters.candidate_bound_words[3] <= DAT_febe6558)))) &&
        (DAT_febe6558 <= fit_parameters.candidate_bound_words[2])))) &&
      (((((fit_parameters.candidate_bound_words[5] <= DAT_febe655a &&
          (DAT_febe655a <= fit_parameters.candidate_bound_words[4])) &&
         ((fit_parameters.candidate_bound_words[5] <= DAT_febe655c &&
          ((((DAT_febe655c <= fit_parameters.candidate_bound_words[4] &&
             (fit_parameters.candidate_bound_words[5] <= DAT_febe655e)) &&
            (DAT_febe655e <= fit_parameters.candidate_bound_words[4])) &&
           ((fit_parameters.candidate_bound_words[5] <= DAT_febe6560 &&
            (DAT_febe6560 <= fit_parameters.candidate_bound_words[4])))))))) &&
        (fit_parameters.candidate_bound_words[5] <= DAT_febe6562)) &&
       (((DAT_febe6562 <= fit_parameters.candidate_bound_words[4] &&
         (fit_parameters.candidate_bound_words[5] <= DAT_febe6564)) &&
        ((DAT_febe6564 <= fit_parameters.candidate_bound_words[4] &&
         (((iVar6 - iVar3 < 0 == (iVar6 < 0 != iVar3 < 0 && iVar3 < 0 == iVar6 - iVar3 < 0) &&
           (iVar6 - iVar2 < 0 != (iVar6 < 0 != iVar2 < 0 && iVar2 < 0 == iVar6 - iVar2 < 0) ||
            iVar6 == iVar2)) &&
          (iVar5 - iVar3 < 0 == (iVar5 < 0 != iVar3 < 0 && iVar3 < 0 == iVar5 - iVar3 < 0)))))))))))
     && ((((iVar5 - iVar2 < 0 != (iVar5 < 0 != iVar2 < 0 && iVar2 < 0 == iVar5 - iVar2 < 0) ||
            iVar5 == iVar2 &&
           (iVar4 - iVar3 < 0 == (iVar4 < 0 != iVar3 < 0 && iVar3 < 0 == iVar4 - iVar3 < 0))) &&
          (iVar4 - iVar2 < 0 != (iVar4 < 0 != iVar2 < 0 && iVar2 < 0 == iVar4 - iVar2 < 0) ||
           iVar4 == iVar2)) &&
         ((((iVar4 = (int)((int)(int16_t)DAT_febe656c),
            iVar4 - iVar3 < 0 == (iVar4 < 0 != iVar3 < 0 && iVar3 < 0 == iVar4 - iVar3 < 0) &&
            (iVar4 - iVar2 < 0 != (iVar4 < 0 != iVar2 < 0 && iVar2 < 0 == iVar4 - iVar2 < 0) ||
             iVar4 == iVar2)) &&
           ((((iVar4 = (int)((int)(int16_t)DAT_febe656e),
              iVar4 - iVar3 < 0 == (iVar4 < 0 != iVar3 < 0 && iVar3 < 0 == iVar4 - iVar3 < 0) &&
              (((iVar4 - iVar2 < 0 != (iVar4 < 0 != iVar2 < 0 && iVar2 < 0 == iVar4 - iVar2 < 0) ||
                 iVar4 == iVar2 &&
                (iVar4 = (int)((int)(int16_t)DAT_febe6570),
                iVar4 - iVar3 < 0 == (iVar4 < 0 != iVar3 < 0 && iVar3 < 0 == iVar4 - iVar3 < 0))) &&
               (iVar4 - iVar2 < 0 != (iVar4 < 0 != iVar2 < 0 && iVar2 < 0 == iVar4 - iVar2 < 0) ||
                iVar4 == iVar2)))) &&
             ((fit_parameters.candidate_bound_words[9] <= DAT_febe6572 &&
              (DAT_febe6572 <= fit_parameters.candidate_bound_words[8])))) &&
            (fit_parameters.candidate_bound_words[9] <= DAT_febe6574)))) &&
          (((DAT_febe6574 <= fit_parameters.candidate_bound_words[8] &&
            (fit_parameters.candidate_bound_words[9] <= DAT_febe6576)) &&
           (DAT_febe6576 <= fit_parameters.candidate_bound_words[8])))))))) {
    uVar1 = 0x5a;
  }
  return uVar1;
}

void publish_application_record_path_fault(void)

{
  report_diagnostic_event_failure(0x52,0x32);
  retain_and_clear_fault_record(0x11);
  encode_fault_action_kind('\x11','\x01');
  select_current_fault_record(0x11);
  return;
}

void step_fit_completion(void)

{
  undefined *puVar1;
  undefined *puVar2;
  uint uVar3;
  char cVar4;
  char cVar5;
  
  cVar4 = DAT_febe6a5d;
  cVar5 = DAT_febe6a5c;
  puVar2 = ((undefined *)camry_host_ptr(0xfebeb800u));
  if (DAT_febe6a5c == 'Z') {
    if (DAT_febe6a5d == '\0') {
      puVar2 = ((undefined *)camry_host_ptr(0xfebeb800u));
      begin_six_channel_fit();
      cVar4 = '\x11';
    }
    else if (DAT_febe6a5d == '\x11') {
      if (DAT_febe6528 == 'U') {
        puVar2 = ((undefined *)camry_host_ptr(0xfebeb800u));
        uVar3 = check_foreground_fit_bounds();
        puVar1 = puVar2;
        if (uVar3 == 0x5a) {
          publish_fit_candidate_record();
          cVar4 = '\"';
          goto LAB_00033f90;
        }
      }
      else {
        puVar1 = ((undefined *)camry_host_ptr(0xfebeb800u));
        if (DAT_febe6528 != 'f') goto LAB_00033f90;
      }
      puVar2 = puVar1;
      publish_application_record_path_fault();
      cVar4 = 'D';
    }
    else if (DAT_febe6a5d == '\"') {
      puVar2 = ((undefined *)camry_host_ptr(0xfebeb800u));
      submit_up_to_eight_response_bytes_or_error_34ea4(0,0);
      cVar5 = '\0';
    }
    else {
      cVar5 = '\0';
      puVar2 = ((undefined *)camry_host_ptr(0xfebeb800u));
      if (DAT_febe6a5d != 'D') {
        puVar2 = ((undefined *)camry_host_ptr(0xfebeb800u));
        publish_application_record_path_fault();
      }
      submit_up_to_eight_response_bytes_or_error_34ea4(0,(int)0xfffffff7);
    }
  }
LAB_00033f90:
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffb25cu + (uint32_t)((int)camry_host_addr(puVar2)) * 1u)))) = cVar5;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffb25du + (uint32_t)((int)camry_host_addr(puVar2)) * 1u)))) = cVar4;
  return;
}

uint request_six_channel_fit(void)

{
  DAT_febe6a5c = 0x5a;
  return 0;
}

void return_only_stub_33fa8(void)

{
  return;
}

void initialize_mode600_stimulus_fit(void)

{
  mode600_stimulus_fit_work.state = '\x10';
  mode600_stimulus_fit_work.stimulus_valid = '\0';
  mode600_stimulus_fit_work.positive_mean = 0;
  mode600_stimulus_fit_work.negative_mean = 0;
  mode600_stimulus_fit_work.stimulus = 0;
  mode600_stimulus_fit_work.hold_count = 0;
  mode600_stimulus_fit_work.sample_count = 0;
  mode600_stimulus_fit_work.folded_angle_sum = 0;
  mode600_stimulus_fit_work.signed_component_sum = 0;
  return;
}

void abort_mode600_stimulus_fit
               (uchar *active,uchar *request_valid,short *stimulus,ushort *hold_count,
               short *positive_mean,short *negative_mean,uchar *state)

{
  short *psVar1;
  uint uVar2;
  short asStack_8 [2];
  
  *stimulus = 0;
  *hold_count = 0;
  *active = '\0';
  *request_valid = '\0';
  *positive_mean = 0;
  *negative_mean = 0;
  *state = '\x10';
  uVar2 = 0;
  do {
    psVar1 = asStack_8 + uVar2;
    uVar2 = uVar2 + 1;
    *psVar1 = 0;
  } while (uVar2 < 2);
  stage_pair_correction('\0',asStack_8);
  submit_up_to_eight_response_bytes_or_error_34ea4(0,(int)0xfffffffa);
  cancel_mode600_stimulus_fit();
  return;
}
