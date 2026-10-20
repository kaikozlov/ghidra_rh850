#include "common.h"

void force_windowed_state44_with_thresholds_exceeded_70068(short *param_1,int param_2,int param_3)

{
  short sVar1;
  uint32_t pcVar2;
  
  if (0xfffe < (*((ushort *)camry_host_ptr((uint32_t)(param_2 + 4))))) {
    return;
  }
  if (0xfffe < (*((ushort *)camry_host_ptr((uint32_t)(param_2 + 10))))) {
    return;
  }
  sVar1 = *param_1;
  if (sVar1 == 0) {
LAB_000700be:
    if ((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(param_3 + 0x1c))))) != 0u) {
      (*(int (*)())camry_indirect((uint32_t)(((((code *)(uintptr_t)((uint32_t)((uintptr_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(param_3 + 0x1c))))))))))))(camry_host_addr(param_1), param_2, param_3);
    }
LAB_000700ca:
    if ((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(param_3 + 0x24))))) != 0u) {
      (*(int (*)())camry_indirect((uint32_t)(((((code *)(uintptr_t)((uint32_t)((uintptr_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(param_3 + 0x24))))))))))))();
    }
  }
  else {
    if (sVar1 == 0x11) goto LAB_000700ca;
    if (sVar1 != 0x22) {
      if (sVar1 == 0x1100) {
        pcVar2 = (uint32_t)((uintptr_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(param_3 + 0x10)))));
      }
      else {
        if (sVar1 != 0x2200) goto LAB_000700ee;
        pcVar2 = (uint32_t)((uintptr_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(param_3 + 0x18)))));
      }
      if ((uint32_t)(pcVar2) != 0u) {
        (*(int (*)())camry_indirect((uint32_t)(pcVar2)))();
      }
      goto LAB_000700be;
    }
  }
  if ((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(param_3 + 0x2c))))) != 0u) {
    (*(int (*)())camry_indirect((uint32_t)(((((code *)(uintptr_t)((uint32_t)((uintptr_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(param_3 + 0x2c))))))))))))();
  }
  if ((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(param_3 + 0x40))))) != 0u) {
    (*(int (*)())camry_indirect((uint32_t)(((((code *)(uintptr_t)((uint32_t)((uintptr_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(param_3 + 0x40))))))))))))();
  }
LAB_000700ee:
  param_1[7] = 0;
  param_1[3] = 0;
  param_1[2] = 0;
  param_1[0] = 0x44;
  param_1[1] = 0;
  param_1[4] = (*((short *)camry_host_ptr((uint32_t)(param_2 + 4)))) + 1;
  param_1[8] = (*((short *)camry_host_ptr((uint32_t)(param_2 + 10)))) + 1;
  return;
}

void store_s16_max_third_min_first_two_70110(short param_1,short param_2,short param_3,short *param_4)

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

void store_s32_max_third_min_first_two_7012a(int param_1,int param_2,int param_3,int *param_4)

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

void store_u32_max_third_min_first_two_7013e(uint param_1,uint param_2,uint param_3,uint *param_4)

{
  if (param_2 < param_1) {
    param_1 = param_2;
  }
  if (param_1 < param_3) {
    param_1 = param_3;
  }
  *param_4 = param_1;
  return;
}

void store_maximum_s32_70152(int param_1,int param_2,int *param_3)

{
  if (param_2 - param_1 < 0 == (param_2 < 0 != param_1 < 0 && param_1 < 0 == param_2 - param_1 < 0)
      && param_2 != param_1) {
    param_1 = param_2;
  }
  *param_3 = param_1;
  return;
}

void store_minimum_s32_70160(int param_1,int param_2,int *param_3)

{
  if (param_2 - param_1 < 0 != (param_2 < 0 != param_1 < 0 && param_1 < 0 == param_2 - param_1 < 0))
  {
    param_1 = param_2;
  }
  *param_3 = param_1;
  return;
}

void store_minimum_u8_7016e(byte param_1,byte param_2,byte *param_3)

{
  if (param_2 < param_1) {
    param_1 = param_2;
  }
  *param_3 = param_1;
  return;
}

void store_min_u16_70180(ushort param_1,ushort param_2,ushort *param_3)

{
  if (param_2 < param_1) {
    param_1 = param_2;
  }
  *param_3 = param_1;
  return;
}

void store_min_u32_70192(uint param_1,uint param_2,uint *param_3)

{
  if (param_2 < param_1) {
    param_1 = param_2;
  }
  *param_3 = param_1;
  return;
}

undefined4 read_priority_mask_701a0(void)

{
  undefined4 uVar1;
  
  uVar1 = PMR;
  return uVar1;
}

void write_priority_mask_preserving_irq_disable_701a6(undefined4 param_1)

{
  uint uVar1;
  uint uVar2;
  undefined4 uVar3;
  uint uVar4;
  uint in_FPEC = 0;
  uint in_RBASE = 0;
  uint in_EBASE = 0;
  uint in_FPIPR = 0;
  uint in_ISPR = 0;
  
  if ((camry_psw >> 5 & 1) == 0) {
    __disable_irq();
    PMR = param_1;
    if ((in_FPEC & 1) != 0) {
      uVar3 = PMR;
    }
    if ((in_FPEC & 1) != 0) {
      uVar1 = in_FPIPR & 0x1f;
      if (0xf < uVar1) {
        uVar1 = 0x10;
      }
      uVar2 = uVar1;
      if (0xf < uVar1) {
        uVar2 = 0xf;
      }
      uVar4 = PMR;
      if ((((uVar4 & 1 << uVar2) == 0) && ((in_ISPR & (1 << uVar1 + 1) - 1U & 0xffff) == 0)) &&
         ((camry_psw & 0x80) == 0)) {
        if (((camry_psw & 0xbfffffd0) >> 0xf & 1) == 0) {
          in_EBASE = in_RBASE;
        }
        (*(int (*)())camry_indirect((uint32_t)((in_EBASE & 0xfffffe00) + 0x70)))();
      }
    }
    __enable_irq();
  }
  else {
    PMR = param_1;
    if ((in_FPEC & 1) != 0) {
      uVar1 = in_FPIPR & 0x1f;
      if (0xf < uVar1) {
        uVar1 = 0x10;
      }
      uVar2 = uVar1;
      if (0xf < uVar1) {
        uVar2 = 0xf;
      }
      uVar4 = PMR;
      if ((((uVar4 & 1 << uVar2) == 0) && ((in_ISPR & (1 << uVar1 + 1) - 1U & 0xffff) == 0)) &&
         ((camry_psw & 0xa0) == 0)) {
        if (((camry_psw & 0xbfffffb0) >> 0xf & 1) == 0) {
          in_EBASE = in_RBASE;
        }
        (*(int (*)())camry_indirect((uint32_t)((in_EBASE & 0xfffffe00) + 0x70)))();
      }
    }
  }
  __synchronize();
  return;
}

void interpolate_s16_axis_s16_values_70208(short *param_1,short param_2,short *param_3)

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
            iVar2 = (int)iVar2 / (int)iVar3;
          }
        }
        sVar5 = psVar1[-1] + (short)iVar2;
        goto LAB_00070256;
      }
      iVar2 = iVar2 + 1;
    }
    sVar5 = psVar1[-1];
  }
LAB_00070256:
  *param_3 = sVar5;
  return;
}

void interpolate_s16_axis_u16_values_7025c(short *param_1,short param_2,short *param_3)

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
        iVar2 = (iVar4 - psVar1[-2]) * ((uint)(ushort)psVar1[1] - (uint)(ushort)psVar1[-1]);
        if (iVar3 != 0) {
          if (iVar2 == -0x80000000 && iVar3 == -1) {
            iVar2 = 0;
          }
          else {
            iVar2 = (int)iVar2 / (int)iVar3;
          }
        }
        sVar5 = psVar1[-1] + (short)iVar2;
        goto LAB_000702aa;
      }
      iVar2 = iVar2 + 1;
    }
    sVar5 = psVar1[-1];
  }
LAB_000702aa:
  *param_3 = sVar5;
  return;
}

void interpolate_u16_axis_s16_values_702b0(ushort *param_1,uint param_2,ushort *param_3)

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
            iVar4 = (int)iVar4 / (int)iVar3;
          }
        }
        uVar2 = puVar1[-1] + (short)iVar4;
        goto LAB_000702fe;
      }
      iVar3 = iVar3 + 1;
    }
    uVar2 = puVar1[-1];
  }
LAB_000702fe:
  *param_3 = uVar2;
  return;
}

void interpolate_u16_axis_u16_values_70304(ushort *param_1,uint param_2,ushort *param_3)

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
            iVar4 = (int)iVar4 / (int)iVar3;
          }
        }
        uVar2 = puVar1[-1] + (short)iVar4;
        goto LAB_00070352;
      }
      iVar3 = iVar3 + 1;
    }
    uVar2 = puVar1[-1];
  }
LAB_00070352:
  *param_3 = uVar2;
  return;
}

void store_symmetric_saturating_s32_sum_70674(int param_1,int param_2,int *param_3)

{
  int iVar1;
  
  if (param_1 < 1) {
    if ((param_2 < 1) &&
       (iVar1 = -0x7fffffff - param_1,
       iVar1 - param_2 < 0 == (iVar1 < 0 != param_2 < 0 && param_2 < 0 == iVar1 - param_2 < 0) &&
       iVar1 != param_2)) {
      param_2 = -0x7fffffff;
      goto LAB_000706a8;
    }
  }
  else if ((0 < param_2) &&
          (iVar1 = (0x7fffffff - param_1) - param_2,
          iVar1 < 0 != (0x7fffffff - param_1 < 0 != param_2 < 0 && param_2 < 0 == iVar1 < 0))) {
    param_2 = 0x7fffffff;
    goto LAB_000706a8;
  }
  param_2 = param_2 + param_1;
LAB_000706a8:
  *param_3 = param_2;
  return;
}

void store_symmetric_saturating_s32_product_706ae(int param_1,int param_2,uint *param_3)

{
  int iVar1;
  uint uVar2;
  
  if ((param_1 == 0) || (param_2 == 0)) {
    uVar2 = 0;
    goto LAB_00070700;
  }
  if (param_1 < 0) {
    if (-1 < param_2) goto LAB_000706e4;
  }
  else if (param_2 < 0) {
LAB_000706e4:
    iVar1 = (int)((ulonglong)((longlong)param_2 * (longlong)param_1) >> 0x20) + 1;
    if ((iVar1 < 0 != (-1 < (longlong)param_2 * (longlong)param_1 && iVar1 < 0)) ||
       (uVar2 = param_1 * param_2, uVar2 < 0x80000001)) {
      uVar2 = 0x80000001;
    }
    goto LAB_00070700;
  }
  if ((-1 < (longlong)param_2 * (longlong)param_1 &&
       (int)((ulonglong)((longlong)param_2 * (longlong)param_1) >> 0x20) != 0) ||
     (uVar2 = param_1 * param_2, 0x7fffffff < (uint)(param_1 * param_2))) {
    uVar2 = 0x7fffffff;
  }
LAB_00070700:
  *param_3 = uVar2;
  return;
}

void store_symmetric_saturating_s16_difference_70706(short param_1,short param_2,undefined2 *param_3)

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

int vote_redundant_u8(uchar *raw,uchar *xor55,uchar *xorAA,uchar *output)

{
  byte bVar1;
  int iVar2;
  uint saved_mask;
  byte bVar3;
  byte bVar4;
  
  if ((((camry_host_addr(raw)==camry_host_addr((uchar *)0x0)) || (camry_host_addr(xor55)==camry_host_addr((uchar *)0x0))) || (camry_host_addr(xorAA)==camry_host_addr((uchar *)0x0))) ||
     ((camry_host_addr(output)==camry_host_addr((uchar *)0x0)|| (camry_host_addr(raw)==camry_host_addr(output))))) {
    iVar2 = -1;
  }
  else {
    saved_mask = priority_mask_enter(0xffc0);
    bVar1 = *raw;
    bVar4 = *xor55;
    bVar3 = *xorAA;
    priority_mask_restore(saved_mask);
    bVar4 = bVar4 ^ 0x55;
    bVar3 = bVar3 ^ 0xaa;
    if (bVar1 == bVar4) {
      if (bVar1 == bVar3) {
        *output = bVar1;
        return 0;
      }
    }
    else if (bVar1 != bVar3) {
      if (bVar4 == bVar3) {
        iVar2 = -0xc;
        bVar1 = bVar4;
      }
      else {
        iVar2 = -0xd;
      }
      *output = bVar1;
      return iVar2;
    }
    *output = bVar1;
    iVar2 = -0xb;
  }
  return iVar2;
}

undefined4 read_xor_redundant_u16_with_vote_status_707ac(ushort *param_1,ushort *param_2,ushort *param_3,ushort *param_4)

{
  ushort uVar1;
  undefined4 uVar2;
  uint saved_mask;
  ushort uVar3;
  ushort uVar4;
  
  if ((((camry_host_addr((param_1))== 0) || (camry_host_addr((param_2))== 0)) || (camry_host_addr((param_3))== 0)) ||
     ((camry_host_addr((param_4))== 0|| (camry_host_addr(param_1)==camry_host_addr(param_4))))) {
    uVar2 = 0xffffffff;
  }
  else {
    saved_mask = priority_mask_enter(0xffc0);
    uVar1 = *param_1;
    uVar4 = *param_2;
    uVar3 = *param_3;
    priority_mask_restore(saved_mask);
    uVar4 = uVar4 ^ 0x5555;
    uVar3 = uVar3 ^ 0xaaaa;
    if (uVar1 == uVar4) {
      if (uVar1 == uVar3) {
        *param_4 = uVar1;
        return 0;
      }
    }
    else if (uVar1 != uVar3) {
      if (uVar4 == uVar3) {
        uVar2 = 0xfffffff4;
        uVar1 = uVar4;
      }
      else {
        uVar2 = 0xfffffff3;
      }
      *param_4 = uVar1;
      return uVar2;
    }
    *param_4 = uVar1;
    uVar2 = 0xfffffff5;
  }
  return uVar2;
}

undefined4 read_xor_redundant_u32_with_vote_status_70822(uint *param_1,uint *param_2,uint *param_3,uint *param_4)

{
  undefined4 uVar1;
  uint saved_mask;
  uint uVar2;
  uint uVar3;
  uint uVar4;
  
  if ((((camry_host_addr((param_1))== 0) || (camry_host_addr((param_2))== 0)) || (camry_host_addr((param_3))== 0)) ||
     ((camry_host_addr((param_4))== 0|| (camry_host_addr(param_1)==camry_host_addr(param_4))))) {
    uVar1 = 0xffffffff;
  }
  else {
    saved_mask = priority_mask_enter(0xffc0);
    uVar4 = *param_1;
    uVar3 = *param_2;
    uVar2 = *param_3;
    priority_mask_restore(saved_mask);
    uVar3 = uVar3 ^ 0x55555555;
    uVar2 = uVar2 ^ 0xaaaaaaaa;
    if (uVar4 == uVar3) {
      if (uVar4 == uVar2) {
        *param_4 = uVar4;
        return 0;
      }
    }
    else if (uVar4 != uVar2) {
      if (uVar3 == uVar2) {
        uVar1 = 0xfffffff4;
        uVar4 = uVar3;
      }
      else {
        uVar1 = 0xfffffff3;
      }
      *param_4 = uVar4;
      return uVar1;
    }
    *param_4 = uVar4;
    uVar1 = 0xfffffff5;
  }
  return uVar1;
}

undefined4 read_xor_redundant_u8_with_vote_status_708a0(byte *param_1,byte *param_2,byte *param_3,byte *param_4)

{
  byte bVar1;
  undefined4 uVar2;
  uint saved_mask;
  byte bVar3;
  byte bVar4;
  
  if ((((camry_host_addr((param_1))== 0) || (camry_host_addr((param_2))== 0)) || (camry_host_addr((param_3))== 0)) ||
     ((camry_host_addr((param_4))== 0|| (camry_host_addr(param_1)==camry_host_addr(param_4))))) {
    uVar2 = 0xffffffff;
  }
  else {
    saved_mask = priority_mask_enter(0xffc0);
    bVar1 = *param_1;
    bVar4 = *param_2;
    bVar3 = *param_3;
    priority_mask_restore(saved_mask);
    bVar4 = bVar4 ^ 0x55;
    bVar3 = bVar3 ^ 0xaa;
    if (bVar1 == bVar4) {
      if (bVar1 == bVar3) {
        *param_4 = bVar1;
        return 0;
      }
    }
    else if (bVar1 != bVar3) {
      if (bVar4 == bVar3) {
        uVar2 = 0xfffffff4;
        bVar1 = bVar4;
      }
      else {
        uVar2 = 0xfffffff3;
      }
      *param_4 = bVar1;
      return uVar2;
    }
    *param_4 = bVar1;
    uVar2 = 0xfffffff5;
  }
  return uVar2;
}

undefined4 read_xor_redundant_u16_with_vote_status_70916(ushort *param_1,ushort *param_2,ushort *param_3,ushort *param_4)

{
  ushort uVar1;
  undefined4 uVar2;
  uint saved_mask;
  ushort uVar3;
  ushort uVar4;
  
  if ((((camry_host_addr((param_1))== 0) || (camry_host_addr((param_2))== 0)) || (camry_host_addr((param_3))== 0)) ||
     ((camry_host_addr((param_4))== 0|| (camry_host_addr(param_1)==camry_host_addr(param_4))))) {
    uVar2 = 0xffffffff;
  }
  else {
    saved_mask = priority_mask_enter(0xffc0);
    uVar1 = *param_1;
    uVar4 = *param_2;
    uVar3 = *param_3;
    priority_mask_restore(saved_mask);
    uVar4 = uVar4 ^ 0x5555;
    uVar3 = uVar3 ^ 0xaaaa;
    if (uVar1 == uVar4) {
      if (uVar1 == uVar3) {
        *param_4 = uVar1;
        return 0;
      }
    }
    else if (uVar1 != uVar3) {
      if (uVar4 == uVar3) {
        uVar2 = 0xfffffff4;
        uVar1 = uVar4;
      }
      else {
        uVar2 = 0xfffffff3;
      }
      *param_4 = uVar1;
      return uVar2;
    }
    *param_4 = uVar1;
    uVar2 = 0xfffffff5;
  }
  return uVar2;
}

undefined4 read_xor_redundant_u32_with_vote_status_7098c(uint *param_1,uint *param_2,uint *param_3,uint *param_4)

{
  undefined4 uVar1;
  uint saved_mask;
  uint uVar2;
  uint uVar3;
  uint uVar4;
  
  if ((((camry_host_addr((param_1))== 0) || (camry_host_addr((param_2))== 0)) || (camry_host_addr((param_3))== 0)) ||
     ((camry_host_addr((param_4))== 0|| (camry_host_addr(param_1)==camry_host_addr(param_4))))) {
    uVar1 = 0xffffffff;
  }
  else {
    saved_mask = priority_mask_enter(0xffc0);
    uVar4 = *param_1;
    uVar3 = *param_2;
    uVar2 = *param_3;
    priority_mask_restore(saved_mask);
    uVar3 = uVar3 ^ 0x55555555;
    uVar2 = uVar2 ^ 0xaaaaaaaa;
    if (uVar4 == uVar3) {
      if (uVar4 == uVar2) {
        *param_4 = uVar4;
        return 0;
      }
    }
    else if (uVar4 != uVar2) {
      if (uVar3 == uVar2) {
        uVar1 = 0xfffffff4;
        uVar4 = uVar3;
      }
      else {
        uVar1 = 0xfffffff3;
      }
      *param_4 = uVar4;
      return uVar1;
    }
    *param_4 = uVar4;
    uVar1 = 0xfffffff5;
  }
  return uVar1;
}

int publish_redundant_u16(ushort value,ushort *raw,ushort *xor5555,ushort *xorAAAA)

{
  int iVar1;
  uint saved_mask;
  
  if (((camry_host_addr(raw)==camry_host_addr((ushort *)0x0)) || (camry_host_addr(xor5555)==camry_host_addr((ushort *)0x0))) || (camry_host_addr(xorAAAA)==camry_host_addr((ushort *)0x0))) {
    iVar1 = -1;
  }
  else {
    saved_mask = priority_mask_enter(0xffc0);
    *raw = value;
    *xor5555 = value ^ 0x5555;
    *xorAAAA = value ^ 0xaaaa;
    priority_mask_restore(saved_mask);
    iVar1 = 0;
  }
  return iVar1;
}

undefined4 write_xor_redundant_u32_70a92(uint param_1,uint *param_2,uint *param_3,uint *param_4)

{
  undefined4 uVar1;
  uint saved_mask;
  
  if (((camry_host_addr((param_2))== 0) || (camry_host_addr((param_3))== 0)) || (camry_host_addr((param_4))== 0)) {
    uVar1 = 0xffffffff;
  }
  else {
    saved_mask = priority_mask_enter(0xffc0);
    *param_2 = param_1;
    *param_3 = param_1 ^ 0x55555555;
    *param_4 = param_1 ^ 0xaaaaaaaa;
    priority_mask_restore(saved_mask);
    uVar1 = 0;
  }
  return uVar1;
}

undefined4 write_xor_redundant_u8_70ade(byte param_1,byte *param_2,byte *param_3,byte *param_4)

{
  undefined4 uVar1;
  uint saved_mask;
  
  if (((camry_host_addr((param_2))== 0) || (camry_host_addr((param_3))== 0)) || (camry_host_addr((param_4))== 0)) {
    uVar1 = 0xffffffff;
  }
  else {
    saved_mask = priority_mask_enter(0xffc0);
    *param_2 = param_1;
    *param_3 = param_1 ^ 0x55;
    *param_4 = param_1 ^ 0xaa;
    priority_mask_restore(saved_mask);
    uVar1 = 0;
  }
  return uVar1;
}

undefined4 write_xor_redundant_u16_70b22(ushort param_1,ushort *param_2,ushort *param_3,ushort *param_4)

{
  undefined4 uVar1;
  uint saved_mask;
  
  if (((camry_host_addr((param_2))== 0) || (camry_host_addr((param_3))== 0)) || (camry_host_addr((param_4))== 0)) {
    uVar1 = 0xffffffff;
  }
  else {
    saved_mask = priority_mask_enter(0xffc0);
    *param_2 = param_1;
    *param_3 = param_1 ^ 0x5555;
    *param_4 = param_1 ^ 0xaaaa;
    priority_mask_restore(saved_mask);
    uVar1 = 0;
  }
  return uVar1;
}

undefined4 write_xor_redundant_u32_70b66(uint param_1,uint *param_2,uint *param_3,uint *param_4)

{
  undefined4 uVar1;
  uint saved_mask;
  
  if (((camry_host_addr((param_2))== 0) || (camry_host_addr((param_3))== 0)) || (camry_host_addr((param_4))== 0)) {
    uVar1 = 0xffffffff;
  }
  else {
    saved_mask = priority_mask_enter(0xffc0);
    *param_2 = param_1;
    *param_3 = param_1 ^ 0x55555555;
    *param_4 = param_1 ^ 0xaaaaaaaa;
    priority_mask_restore(saved_mask);
    uVar1 = 0;
  }
  return uVar1;
}

uint interpolate_u16_table_with_u8_fraction_70bb2(uint param_1,int param_2)

{
  ushort *puVar1;
  
  puVar1 = ((ushort *)camry_host_ptr((uint32_t)(((int)(param_1 & 0xffff) >> 8) * 2 + param_2)));
  return (int)((param_1 & 0xff) * (uint)puVar1[1] + (0x100 - (param_1 & 0xff)) * (uint)*puVar1) /
         0x100 & 0xffff;
}

undefined4 compute_s16_atan2_turn_angle_70be0(short param_1,short param_2,short *param_3)

{
  int iVar1;
  bool bVar2;
  short sVar3;
  uint uVar4;
  uint uVar5;
  uint uVar6;
  short *extraout_r8;
  short *extraout_r8_00;
  short sVar7;
  uint uVar8;
  
  uVar5 = (uint)param_1;
  uVar8 = (uint)param_2;
  uVar6 = uVar5;
  if ((int)uVar5 < 0) {
    uVar6 = -uVar5;
  }
  uVar4 = uVar8;
  if ((int)uVar8 < 0) {
    uVar4 = -uVar8;
  }
  iVar1 = uVar6 - uVar4;
  bVar2 = (int)uVar6 < 0 != (int)uVar4 < 0 && (int)uVar4 < 0 == iVar1 < 0;
  if (iVar1 < 0 == bVar2) {
    if (iVar1 < 0 != bVar2 || uVar6 == uVar4) {
      if ((int)uVar8 < 0) {
        sVar7 = -0x6000;
        if (-1 < (int)uVar5) {
          sVar7 = 0x6000;
        }
      }
      else {
        sVar7 = -0x2000;
        if (-1 < (int)uVar5) {
          sVar7 = 0x2000;
        }
      }
      goto LAB_00070c7c;
    }
    uVar4 = uVar4 << 0x10;
    if (uVar6 != 0) {
      uVar4 = uVar4 / uVar6;
    }
    sVar7 = interpolate_u16_table_with_u8_fraction_70bb2(uVar4 & 0xffff, ((uint32_t)(0x21618u)));
    param_3 = ((short *)(param_3));
    if ((int)uVar5 < 0) {
      if (-1 < (int)uVar8) {
        sVar7 = sVar7 + -0x4000;
        goto LAB_00070c7c;
      }
      sVar3 = -0x4000;
    }
    else {
      if ((int)uVar8 < 0) {
        sVar7 = sVar7 + 0x4000;
        goto LAB_00070c7c;
      }
      sVar3 = 0x4000;
    }
  }
  else {
    uVar6 = uVar6 << 0x10;
    if (uVar4 != 0) {
      uVar6 = uVar6 / uVar4;
    }
    sVar7 = interpolate_u16_table_with_u8_fraction_70bb2(uVar6 & 0xffff, ((uint32_t)(0x21618u)));
    param_3 = ((short *)(param_3));
    if ((int)uVar8 < 0) {
      sVar3 = -0x8000;
      if ((int)uVar5 < 0) {
        sVar7 = sVar7 + -0x8000;
        goto LAB_00070c7c;
      }
    }
    else {
      if (-1 < (int)uVar5) goto LAB_00070c7c;
      sVar3 = 0;
    }
  }
  sVar7 = sVar3 - sVar7;
LAB_00070c7c:
  *param_3 = sVar7;
  return 0;
}

void compute_q15_sine_cosine_turn_angle_70e32(uint param_1,ushort *param_2,ushort *param_3)

{
  ushort uVar1;
  ushort uVar2;
  int iVar3;
  uint pFVar4;
  uint uVar5;
  uint pFVar6;
  uint uVar7;
  ushort uVar8;
  uint uVar9;
  ushort uVar10;
  uint uVar11;
  uint uVar12;
  
  pFVar6 = (uint )(param_1 & 0xffff);
  if (pFVar6 < (uint )0x8000) {
    if (pFVar6 < (uint )0x4000) {
      pFVar4 = pFVar6;
      if ((uint )0x1fff < pFVar6) {
        iVar3 = 0x4000;
LAB_00070e96:
        pFVar4 = (uint )(iVar3 - (int)pFVar6);
      }
    }
    else {
      if ((uint )0x5fff < pFVar6) {
        iVar3 = 0x8000;
        goto LAB_00070e96;
      }
      pFVar4 = (uint )(pFVar6 - 0x4000);
    }
  }
  else if (0xbfffu < pFVar6) {
    if (0xdfffu < pFVar6) {
      iVar3 = 0x10000;
      goto LAB_00070e96;
    }
    pFVar4 = (uint )((pFVar6 - 0xc000));
  }
  else {
    if (0x9fffu < pFVar6) {
      iVar3 = 0xc000;
      goto LAB_00070e96;
    }
    pFVar4 = (uint )((pFVar6 - 0x8000));
  }
  uVar9 = (uint)((int)pFVar4 * 0x6487f) >> 0x10;
  uVar11 = uVar9 * uVar9 >> 0x11;
  uVar7 = uVar11 * 0x5555 >> 0x10;
  uVar5 = uVar11 * uVar7 >> 0x11;
  uVar12 = uVar5 * 0x3333 >> 0x10;
  uVar5 = ((uVar5 - uVar11) + 0x10000) - (uVar7 * uVar12 >> 0x10);
  uVar1 = (ushort)(((uVar12 - uVar7) + 0x10000) * uVar9 >> 0x10);
  uVar8 = uVar1 >> 1;
  uVar10 = (short)(uVar5 >> 1) - (short)(uVar5 >> 0x10);
  if (pFVar6 < (uint )0x8000) {
    uVar2 = uVar10;
    if (pFVar6 < (uint )0x4000) {
      uVar8 = uVar1 >> 1;
      if (pFVar6 < (uint )0x2000) {
        uVar2 = uVar1 >> 1;
        uVar8 = uVar10;
      }
      goto LAB_00070f4e;
    }
    if ((uint )0x5fff < pFVar6) {
LAB_00070f2a:
      uVar2 = uVar8;
      uVar8 = -uVar10;
      goto LAB_00070f4e;
    }
  }
  else {
    if (0xbfffu < pFVar6) {
      if (0xdfffu < pFVar6) {
        uVar2 = -(uVar1 >> 1);
        uVar8 = uVar10;
      }
      else {
        uVar2 = -uVar10;
      }
      goto LAB_00070f4e;
    }
    if (pFVar6 < 0xa000u) {
      uVar8 = -(uVar1 >> 1);
      goto LAB_00070f2a;
    }
    uVar2 = -uVar10;
  }
  uVar8 = -(uVar1 >> 1);
LAB_00070f4e:
  *param_2 = uVar2;
  *param_3 = uVar8;
  return;
}

uint step_monitor_recovery_scratch
               (uchar classification,F33MonitorRecoveryScratch *scratch,ushort *limit)

{
  ushort uVar1;
  ushort uVar2;
  
  if (classification != '\x11') {
    if ((classification == '\"') || (classification == 'D')) {
      scratch->recovery_count = 0;
    }
    return 0x22;
  }
  uVar1 = scratch->recovery_count;
  uVar2 = *limit;
  if ((uVar1 <= uVar2) && (scratch->recovery_count = uVar1 + 1, (ushort)(uVar1 + 1) <= uVar2)) {
    return 0x44000022;
  }
  scratch->passing_count = 0;
  scratch->opaque_02 = 0;
  scratch->failing_count = 0;
  scratch->opaque_08 = 0;
  scratch->recovery_count = 0;
  scratch->opaque_0c = 0;
  scratch->opaque_10 = 0;
  return 0;
}

undefined4 update_total_and_event11_counters_reset_on_event22_70fa4(char param_1,undefined2 *param_2,ushort *param_3)

{
  ushort uVar1;
  ushort uVar2;
  
  if (param_1 == 'D') {
    param_2[5] = 0;
    param_2[8] = 0;
    return 0x22;
  }
  uVar1 = param_2[8];
  uVar2 = param_3[1];
  if ((uVar2 < uVar1) || (param_2[8] = uVar1 + 1, uVar2 < (ushort)(uVar1 + 1))) {
    return 0x44;
  }
  if (param_1 != '\x11') {
    if (param_1 == '\"') {
      param_2[5] = 0;
    }
    return 0x22;
  }
  uVar1 = param_2[5];
  uVar2 = *param_3;
  if ((uVar1 <= uVar2) && (param_2[5] = uVar1 + 1, (ushort)(uVar1 + 1) <= uVar2)) {
    return 0x44000022;
  }
  *param_2 = 0;
  param_2[1] = 0;
  param_2[2] = 0;
  param_2[4] = 0;
  param_2[5] = 0;
  param_2[6] = 0;
  param_2[8] = 0;
  return 0;
}
