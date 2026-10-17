#include "common.h"


void FUN_00070110(short param_1,short param_2,short param_3,short *param_4)

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



void FUN_0007012a(int param_1,int param_2,int param_3,int *param_4)

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



void FUN_0007013e(uint param_1,uint param_2,uint param_3,uint *param_4)

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



void FUN_00070152(int param_1,int param_2,int *param_3)

{
  if (param_2 - param_1 < 0 == (param_2 < 0 != param_1 < 0 && param_1 < 0 == param_2 - param_1 < 0)
      && param_2 != param_1) {
    param_1 = param_2;
  }
  *param_3 = param_1;
  return;
}



void FUN_00070160(int param_1,int param_2,int *param_3)

{
  if (param_2 - param_1 < 0 != (param_2 < 0 != param_1 < 0 && param_1 < 0 == param_2 - param_1 < 0))
  {
    param_1 = param_2;
  }
  *param_3 = param_1;
  return;
}



void FUN_0007016e(byte param_1,byte param_2,byte *param_3)

{
  if (param_2 < param_1) {
    param_1 = param_2;
  }
  *param_3 = param_1;
  return;
}



void FUN_00070180(ushort param_1,ushort param_2,ushort *param_3)

{
  if (param_2 < param_1) {
    param_1 = param_2;
  }
  *param_3 = param_1;
  return;
}



void FUN_00070192(uint param_1,uint param_2,uint *param_3)

{
  if (param_2 < param_1) {
    param_1 = param_2;
  }
  *param_3 = param_1;
  return;
}



void FUN_00070208(short *param_1,short param_2,short *param_3)

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



void FUN_0007025c(short *param_1,short param_2,short *param_3)

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
            iVar2 = iVar2 / iVar3;
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



void FUN_000702b0(ushort *param_1,uint param_2,ushort *param_3)

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



void FUN_00070304(ushort *param_1,uint param_2,ushort *param_3)

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



void FUN_00070674(int param_1,int param_2,int *param_3)

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



void FUN_000706ae(int param_1,int param_2,uint *param_3)

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



void FUN_00070706(short param_1,short param_2,undefined2 *param_3)

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



/* Reject any NULL pointer or output==raw with -1 and no write. Read three bytes under the FFC0
   priority-mask pair, then normalize the encoded copies with55/AA. All agree: return0 and raw. Raw
   agrees with either encoded copy: return-11 and raw. Only encoded copies agree: return-12 and that
   value. All differ: return-13 but still write raw. Output may alias either encoded input; no input
   repair. Reject any NULL or output==raw with-1 and no output write. Snapshot raw and55/AA-encoded
   bytes under PMRFFC0; normalize. All agree:0/raw; raw agrees with either copy:-11/raw; encoded
   pair agrees:-12/pair; all differ:-13/raw, still writing output. only the output cell is written.
   All single-bit faults in each lane exercised for six base values. */

int f33_vote_redundant_u8(uchar *raw,uchar *xor55,uchar *xorAA,uchar *output)

{
  byte bVar1;
  int iVar2;
  uint saved_mask;
  byte bVar3;
  byte bVar4;
  
  if ((((raw == (uchar *)0x0) || (xor55 == (uchar *)0x0)) || (xorAA == (uchar *)0x0)) ||
     ((output == (uchar *)0x0 || (raw == output)))) {
    iVar2 = -1;
  }
  else {
    saved_mask = f33_priority_mask_enter(0xffc0);
    bVar1 = *raw;
    bVar4 = *xor55;
    bVar3 = *xorAA;
    f33_priority_mask_restore(saved_mask);
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



undefined4 FUN_000707ac(ushort *param_1,ushort *param_2,ushort *param_3,ushort *param_4)

{
  ushort uVar1;
  undefined4 uVar2;
  uint saved_mask;
  ushort uVar3;
  ushort uVar4;
  
  if ((((param_1 == (ushort *)0x0) || (param_2 == (ushort *)0x0)) || (param_3 == (ushort *)0x0)) ||
     ((param_4 == (ushort *)0x0 || (param_1 == param_4)))) {
    uVar2 = 0xffffffff;
  }
  else {
    saved_mask = f33_priority_mask_enter(0xffc0);
    uVar1 = *param_1;
    uVar4 = *param_2;
    uVar3 = *param_3;
    f33_priority_mask_restore(saved_mask);
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



undefined4 FUN_00070822(uint *param_1,uint *param_2,uint *param_3,uint *param_4)

{
  undefined4 uVar1;
  uint saved_mask;
  uint uVar2;
  uint uVar3;
  uint uVar4;
  
  if ((((param_1 == (uint *)0x0) || (param_2 == (uint *)0x0)) || (param_3 == (uint *)0x0)) ||
     ((param_4 == (uint *)0x0 || (param_1 == param_4)))) {
    uVar1 = 0xffffffff;
  }
  else {
    saved_mask = f33_priority_mask_enter(0xffc0);
    uVar4 = *param_1;
    uVar3 = *param_2;
    uVar2 = *param_3;
    f33_priority_mask_restore(saved_mask);
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



undefined4 FUN_000708a0(byte *param_1,byte *param_2,byte *param_3,byte *param_4)

{
  byte bVar1;
  undefined4 uVar2;
  uint saved_mask;
  byte bVar3;
  byte bVar4;
  
  if ((((param_1 == (byte *)0x0) || (param_2 == (byte *)0x0)) || (param_3 == (byte *)0x0)) ||
     ((param_4 == (byte *)0x0 || (param_1 == param_4)))) {
    uVar2 = 0xffffffff;
  }
  else {
    saved_mask = f33_priority_mask_enter(0xffc0);
    bVar1 = *param_1;
    bVar4 = *param_2;
    bVar3 = *param_3;
    f33_priority_mask_restore(saved_mask);
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



undefined4 FUN_00070916(ushort *param_1,ushort *param_2,ushort *param_3,ushort *param_4)

{
  ushort uVar1;
  undefined4 uVar2;
  uint saved_mask;
  ushort uVar3;
  ushort uVar4;
  
  if ((((param_1 == (ushort *)0x0) || (param_2 == (ushort *)0x0)) || (param_3 == (ushort *)0x0)) ||
     ((param_4 == (ushort *)0x0 || (param_1 == param_4)))) {
    uVar2 = 0xffffffff;
  }
  else {
    saved_mask = f33_priority_mask_enter(0xffc0);
    uVar1 = *param_1;
    uVar4 = *param_2;
    uVar3 = *param_3;
    f33_priority_mask_restore(saved_mask);
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



undefined4 FUN_0007098c(uint *param_1,uint *param_2,uint *param_3,uint *param_4)

{
  undefined4 uVar1;
  uint saved_mask;
  uint uVar2;
  uint uVar3;
  uint uVar4;
  
  if ((((param_1 == (uint *)0x0) || (param_2 == (uint *)0x0)) || (param_3 == (uint *)0x0)) ||
     ((param_4 == (uint *)0x0 || (param_1 == param_4)))) {
    uVar1 = 0xffffffff;
  }
  else {
    saved_mask = f33_priority_mask_enter(0xffc0);
    uVar4 = *param_1;
    uVar3 = *param_2;
    uVar2 = *param_3;
    f33_priority_mask_restore(saved_mask);
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



/* Any NULL destination returns-1 before all stores. Otherwise publish low8(value), value^55,
   value^AA in that order under the FFC0 priority-mask pair and return0. No alias rejection; the
   three stores are not asserted atomic against every interrupt source. Otherwise write low8(value),
   value^55 and value^AA in that order under the real PMRFFC0 enter/restore pair, then return0.
   Upper value bits discarded; no alias rejection. Sweep covers each NULL position and both ID
   states; not globally atomic storage. */

int f33_publish_redundant_u8(uchar value,uchar *raw,uchar *xor55,uchar *xorAA)

{
  int iVar1;
  uint saved_mask;
  
  if (((raw == (uchar *)0x0) || (xor55 == (uchar *)0x0)) || (xorAA == (uchar *)0x0)) {
    iVar1 = -1;
  }
  else {
    saved_mask = f33_priority_mask_enter(0xffc0);
    *raw = value;
    *xor55 = value ^ 0x55;
    *xorAA = value ^ 0xaa;
    f33_priority_mask_restore(saved_mask);
    iVar1 = 0;
  }
  return iVar1;
}



/* Any NULL destination returns-1 without partial stores. Otherwise publish low16(value),
   value^5555, value^AAAA in that order under the FFC0 priority-mask pair and return0. No alias
   rejection or local alignment validation; no claim of global interrupt exclusion. Otherwise write
   low16(value), value^5555 and value^AAAA in that order under the real PMRFFC0 pair, then return0.
   No alias rejection or local alignment check. Executed narrowing, both ID states and each NULL
   position; no hardware-interleaving proof. */

int f33_publish_redundant_u16(ushort value,ushort *raw,ushort *xor5555,ushort *xorAAAA)

{
  int iVar1;
  uint saved_mask;
  
  if (((raw == (ushort *)0x0) || (xor5555 == (ushort *)0x0)) || (xorAAAA == (ushort *)0x0)) {
    iVar1 = -1;
  }
  else {
    saved_mask = f33_priority_mask_enter(0xffc0);
    *raw = value;
    *xor5555 = value ^ 0x5555;
    *xorAAAA = value ^ 0xaaaa;
    f33_priority_mask_restore(saved_mask);
    iVar1 = 0;
  }
  return iVar1;
}



undefined4 FUN_00070a92(uint param_1,uint *param_2,uint *param_3,uint *param_4)

{
  undefined4 uVar1;
  uint saved_mask;
  
  if (((param_2 == (uint *)0x0) || (param_3 == (uint *)0x0)) || (param_4 == (uint *)0x0)) {
    uVar1 = 0xffffffff;
  }
  else {
    saved_mask = f33_priority_mask_enter(0xffc0);
    *param_2 = param_1;
    *param_3 = param_1 ^ 0x55555555;
    *param_4 = param_1 ^ 0xaaaaaaaa;
    f33_priority_mask_restore(saved_mask);
    uVar1 = 0;
  }
  return uVar1;
}



undefined4 FUN_00070ade(byte param_1,byte *param_2,byte *param_3,byte *param_4)

{
  undefined4 uVar1;
  uint saved_mask;
  
  if (((param_2 == (byte *)0x0) || (param_3 == (byte *)0x0)) || (param_4 == (byte *)0x0)) {
    uVar1 = 0xffffffff;
  }
  else {
    saved_mask = f33_priority_mask_enter(0xffc0);
    *param_2 = param_1;
    *param_3 = param_1 ^ 0x55;
    *param_4 = param_1 ^ 0xaa;
    f33_priority_mask_restore(saved_mask);
    uVar1 = 0;
  }
  return uVar1;
}



undefined4 FUN_00070b22(ushort param_1,ushort *param_2,ushort *param_3,ushort *param_4)

{
  undefined4 uVar1;
  uint saved_mask;
  
  if (((param_2 == (ushort *)0x0) || (param_3 == (ushort *)0x0)) || (param_4 == (ushort *)0x0)) {
    uVar1 = 0xffffffff;
  }
  else {
    saved_mask = f33_priority_mask_enter(0xffc0);
    *param_2 = param_1;
    *param_3 = param_1 ^ 0x5555;
    *param_4 = param_1 ^ 0xaaaa;
    f33_priority_mask_restore(saved_mask);
    uVar1 = 0;
  }
  return uVar1;
}



undefined4 FUN_00070b66(uint param_1,uint *param_2,uint *param_3,uint *param_4)

{
  undefined4 uVar1;
  uint saved_mask;
  
  if (((param_2 == (uint *)0x0) || (param_3 == (uint *)0x0)) || (param_4 == (uint *)0x0)) {
    uVar1 = 0xffffffff;
  }
  else {
    saved_mask = f33_priority_mask_enter(0xffc0);
    *param_2 = param_1;
    *param_3 = param_1 ^ 0x55555555;
    *param_4 = param_1 ^ 0xaaaaaaaa;
    f33_priority_mask_restore(saved_mask);
    uVar1 = 0;
  }
  return uVar1;
}



/* WARNING: Removing unreachable block (ram,0x00070bd8) */

uint FUN_00070bb2(uint param_1,int param_2)

{
  ushort *puVar1;
  
  puVar1 = ((ushort *)camry_host_ptr((uint32_t)(((int)(param_1 & 0xffff) >> 8) * 2 + param_2)));
  return (int)((param_1 & 0xff) * (uint)puVar1[1] + (0x100 - (param_1 & 0xff)) * (uint)*puVar1) /
         0x100 & 0xffff;
}



/* Truncate classification to8 bits.11 increments scratch recovery_count at+10 while<=limit; strict
   crossing clears halfwords0/2/4/8/10/12/16 and returns0,else44000022.22/44 clear recovery_count
   and return22; other classifications return22 preserving it. Scratch+6 high-water survives.
   This18-byte transient layout is not the persistent monitor record. */

uint f33_step_monitor_recovery_scratch
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



undefined4 FUN_00070fa4(char param_1,undefined2 *param_2,ushort *param_3)

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



undefined4 FUN_00071014(char param_1,undefined2 *param_2,ushort *param_3)

{
  ushort uVar1;
  ushort uVar2;
  
  if ((param_2 == (undefined2 *)0x0) || (param_3 == (ushort *)0x0)) {
    return 0xffff;
  }
  if (param_1 == 'D') {
    param_2[5] = 0;
    param_2[8] = 0;
  }
  else {
    uVar1 = param_2[8];
    uVar2 = param_3[1];
    if ((uVar2 < uVar1) || (param_2[8] = uVar1 + 1, uVar2 < (ushort)(uVar1 + 1))) {
      return 0x44;
    }
    if (param_1 == '\x11') {
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
  }
  return 0x22;
}



undefined4 FUN_00071086(char param_1,undefined2 *param_2,ushort *param_3)

{
  short sVar1;
  ushort uVar2;
  ushort uVar3;
  
  if ((param_2 == (undefined2 *)0x0) || (param_3 == (ushort *)0x0)) {
    return 0xffff;
  }
  if (param_1 != '\x11') {
    if (param_1 != '\"') {
      if (param_1 != 'D') {
        return 0x22;
      }
      param_2[5] = 0;
      param_2[6] = 0;
      return 0x22;
    }
    uVar3 = param_2[6];
    uVar2 = param_3[1];
    if (uVar3 <= uVar2) {
      sVar1 = uVar3 + 1;
      uVar3 = uVar3 + 1;
      param_2[6] = sVar1;
    }
    if ((ushort)param_2[7] < uVar3) {
      param_2[7] = uVar3;
    }
    if (uVar2 < uVar3) {
      return 0x44;
    }
    return 0x220022;
  }
  uVar3 = param_2[5];
  uVar2 = *param_3;
  if ((uVar3 <= uVar2) && (param_2[5] = uVar3 + 1, (ushort)(uVar3 + 1) <= uVar2)) {
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



undefined4 FUN_0007110c(char param_1,undefined2 *param_2,ushort *param_3)

{
  short sVar1;
  ushort uVar2;
  ushort uVar3;
  
  if ((param_2 == (undefined2 *)0x0) || (param_3 == (ushort *)0x0)) {
    return 0xffff;
  }
  if (param_1 != '\x11') {
    if (param_1 != '\"') {
      if (param_1 != 'D') {
        return 0x22;
      }
      param_2[5] = 0;
      param_2[6] = 0;
      return 0x22;
    }
    param_2[5] = 0;
    uVar3 = param_2[6];
    uVar2 = param_3[1];
    if (uVar3 <= uVar2) {
      sVar1 = uVar3 + 1;
      uVar3 = uVar3 + 1;
      param_2[6] = sVar1;
    }
    if ((ushort)param_2[7] < uVar3) {
      param_2[7] = uVar3;
    }
    if (uVar2 < uVar3) {
      return 0x44;
    }
    return 0x220022;
  }
  uVar3 = param_2[5];
  uVar2 = *param_3;
  if ((uVar3 <= uVar2) && (param_2[5] = uVar3 + 1, (ushort)(uVar3 + 1) <= uVar2)) {
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



undefined4 FUN_00071194(char param_1,undefined2 *param_2,ushort *param_3)

{
  short sVar1;
  ushort uVar2;
  ushort uVar3;
  
  if ((param_2 == (undefined2 *)0x0) || (param_3 == (ushort *)0x0)) {
    return 0xffff;
  }
  if (param_1 == 'D') {
    param_2[5] = 0;
    param_2[8] = 0;
    param_2[6] = 0;
    return 0x22;
  }
  uVar3 = param_2[8];
  uVar2 = param_3[2];
  if ((uVar3 <= uVar2) && (param_2[8] = uVar3 + 1, (ushort)(uVar3 + 1) <= uVar2)) {
    if (param_1 == '\x11') {
      uVar3 = param_2[5];
      uVar2 = *param_3;
      if ((uVar3 <= uVar2) && (param_2[5] = uVar3 + 1, (ushort)(uVar3 + 1) <= uVar2)) {
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
    if (param_1 != '\"') {
      return 0x22;
    }
    param_2[5] = 0;
    uVar3 = param_2[6];
    uVar2 = param_3[1];
    if (uVar3 <= uVar2) {
      sVar1 = uVar3 + 1;
      uVar3 = uVar3 + 1;
      param_2[6] = sVar1;
    }
    if ((ushort)param_2[7] < uVar3) {
      param_2[7] = uVar3;
    }
    if (uVar3 <= uVar2) {
      return 0x220022;
    }
  }
  return 0x44;
}



undefined4 FUN_00071232(char param_1,undefined2 *param_2,ushort *param_3)

{
  short sVar1;
  ushort uVar2;
  ushort uVar3;
  
  if ((param_2 == (undefined2 *)0x0) || (param_3 == (ushort *)0x0)) {
    return 0xffff;
  }
  if (param_1 != '\x11') {
    if (param_1 != '\"') {
      if (param_1 != 'D') {
        return 0x22;
      }
      param_2[5] = 0;
      param_2[6] = 0;
      return 0x22;
    }
    uVar3 = param_2[6];
    uVar2 = param_3[1];
    if (uVar3 <= uVar2) {
      sVar1 = uVar3 + 1;
      uVar3 = uVar3 + 1;
      param_2[6] = sVar1;
    }
    if ((ushort)param_2[7] < uVar3) {
      param_2[7] = uVar3;
    }
    if (uVar2 < uVar3) {
      return 0x44;
    }
    return 0x220022;
  }
  param_2[6] = 0;
  uVar3 = param_2[5];
  uVar2 = *param_3;
  if ((uVar3 <= uVar2) && (param_2[5] = uVar3 + 1, (ushort)(uVar3 + 1) <= uVar2)) {
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



/* WARNING: This function may have set the stack pointer */
/* NONORDINARY PAIRED ABI: PUSHSP r1..ep saves120 bytes on original stack; r2 retains saved-frame
   SP, SP becomes FEBE2800, r20 preserves continuation, profile selectorROM31684=1 goes to65984. No
   PSW save or independent interrupt disable. Pair with71398; do not model as an ordinary leaf
   wrapper. */

void FUN_00071378(void)

{
  f33_apply_mpu_attribute_profile(DAT_00031684);
  return;
}



/* Exact F33 context loader: INTBP=20200 EBASE=20000 GP=FEBEB800 TP=23DFC SP=FEBE2000 */

void f33_application_context_init(void)

{
  return;
}



void FUN_00071610(void)

{
  __synchronize();
  __synchronize();
  DAT_febf3401 = 0;
  __synchronize();
  __synchronize();
  return;
}



/* Full32-bit nonzero outer count; each iteration decrements an inner counter from155 to zero. Zero
   bypasses both loops. Exact execution takes4 instructions for zero,313*n+5 for positive tested
   n=1,2,3400. These are instruction counts, not clock-cycle or wall-time calibration. No ordinary
   return value. Two-level spin loop: full32-bit outer count fromr6; inner counter155; zero skips
   loops. Native n=0/1/2/3400 executes4/318/631/1064205 instructions and returns with the expected
   counter state. No clock-cycle or wall-time inference. Constant3400 at30D8C loaded63ABC is a
   scalar iteration count, not code pointerD48. Throwaway execution plus exact22-byte body; no
   redundant permanent loop-counter fixture. */

void f33_spin_wait(uint outer_iterations)

{
  bool bVar1;
  int iVar2;
  
  if (outer_iterations != 0) {
    do {
      iVar2 = 0x9b;
      do {
        bVar1 = iVar2 != 1;
        iVar2 = iVar2 + -1;
      } while (bVar1);
      bVar1 = outer_iterations != 1;
      outer_iterations = outer_iterations - 1;
    } while (bVar1);
  }
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_71ce0(void)

{
  return;
}



/* Constant source: return 1; shape-classified from the canonical corpus. Callers receive this
   literal directly; its meaning is not recovered. */

undefined4 f33_return_const_1_71cf4(void)

{
  return 1;
}



/* Single constant publisher: DAT_febf6102 = 0xf0; Shape-classified from the canonical corpus; the
   target cell is not yet named, so the written state's meaning is unknown. */

void FUN_00071d7c(void)

{
  DAT_febf6102 = 0xf0;
  return;
}



/* Constant source: return 0; shape-classified from the canonical corpus. Callers receive this
   literal directly; its meaning is not recovered. */

undefined4 f33_return_const_0_71d88(void)

{
  return 0;
}



/* Low16 handle0 calls the two-argument zero-handle notifier; otherwise preserve all three arguments
   for the logical notifier. Low16 logical0 routes operation/low8 result to71D8C; nonzero preserves
   logical/operation/result for71DBA. Both routes execute with nonzero upper input bits. No
   independent result or admission policy. */

void f33_nvm_route_logical_result(ushort logical_handle,uint operation,uchar result)

{
  if (logical_handle == 0) {
    f33_nvm_notify_zero_handle_result(operation,result);
  }
  else {
    f33_nvm_notify_logical_result(logical_handle,operation,result);
  }
  return;
}



void FUN_00071e26(short param_1,uint param_2)

{
  uint uVar1;
  
  uVar1 = f33_lookup_u32_value_by_key(param_2,0xff,(0x275ccu));
  uVar1 = uVar1 & 0xff;
  if (param_1 == 0) {
    FUN_00079be8(uVar1);
  }
  else {
    FUN_00079bc0(param_1,uVar1);
    if ((uVar1 == 6) || (uVar1 == 0x16)) {
      DAT_febf60fa = 4;
      DAT_febf60fb = 4;
      DAT_febf60fe = 4;
      DAT_febf6101 = 4;
      DAT_febf60fc = 4;
    }
    else if ((uVar1 == 7) || (uVar1 == 0x17)) {
      DAT_febf60fa = 4;
      DAT_febf60fe = 4;
      DAT_febf60ff = 4;
    }
  }
  return;
}



void FUN_00071e88(uint param_1)

{
  undefined4 uVar1;
  
  uVar1 = 0;
  if (((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebf60fau + (uint32_t)(param_1 & 0xff) * 1u)))) == '\x01') ||
     (uVar1 = 1, (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebf60fau + (uint32_t)(param_1 & 0xff) * 1u)))) == '\x02')) {
    ((void)((*((undefined2 *)camry_host_ptr((uint32_t)((int)&PTR_DAT_000273cc + (param_1 & 0xff) * 2))))), (void)(uVar1), f33_return_only_stub_747de())
    ;
  }
  return;
}



void FUN_00071eb4(short param_1,uint param_2)

{
  undefined4 uVar1;
  uint uVar2;
  
  uVar2 = f33_lookup_u32_value_by_key(param_2,0xff,(0x275ccu));
  uVar2 = uVar2 & 0xff;
  if (param_1 == 0) {
    FUN_00079c2a(uVar2);
  }
  else {
    FUN_00079bfe(param_1,uVar2);
    if ((uVar2 == 6) || (uVar2 == 0x16)) {
      FUN_00071e88(0);
      FUN_00071e88(1);
      FUN_00071e88(4);
      FUN_00071e88(7);
      uVar1 = 2;
    }
    else {
      if ((uVar2 != 7) && (uVar2 != 0x17)) {
        return;
      }
      FUN_00071e88(0);
      FUN_00071e88(4);
      uVar1 = 5;
    }
    FUN_00071e88(uVar1);
  }
  return;
}



void FUN_00071f28(undefined2 param_1,uint param_2)

{
  uint uVar1;
  int iVar2;
  
  uVar1 = f33_lookup_u32_value_by_key(param_2,0xff,(0x275ccu));
  if ((uVar1 & 0xff) == 0xc) {
    FUN_00079bc0(param_1,0xc);
    DAT_febf60fb = 4;
    iVar2 = 2;
    DAT_febf6101 = 4;
  }
  else {
    if ((uVar1 & 0xff) != 0xd) {
      return;
    }
    FUN_00079bc0(param_1,0xd);
    iVar2 = 5;
  }
  DAT_febf60fa = 4;
  DAT_febf60fe = 4;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebf60fau + (uint32_t)(iVar2) * 1u)))) = 4;
  return;
}



void FUN_00071f82(undefined2 param_1,uint param_2)

{
  undefined4 uVar1;
  uint uVar2;
  
  uVar2 = f33_lookup_u32_value_by_key(param_2,0xff,(0x275ccu));
  if ((uVar2 & 0xff) == 0xc) {
    FUN_00079bfe(param_1,0xc);
    FUN_00071e88(0);
    FUN_00071e88(1);
    FUN_00071e88(4);
    FUN_00071e88(7);
    uVar1 = 2;
  }
  else {
    if ((uVar2 & 0xff) != 0xd) {
      return;
    }
    FUN_00079bfe(param_1,0xd);
    FUN_00071e88(0);
    FUN_00071e88(4);
    uVar1 = 5;
  }
  FUN_00071e88(uVar1);
  return;
}



void FUN_00071fe4(ushort param_1,void *param_2)

{
  f33_nvm_set_read_buffer(param_1, camry_host_addr(param_2));
  return;
}



void FUN_00071ff2(undefined2 param_1)

{
  int iVar1;
  
  iVar1 = FUN_0007475a();
  if (iVar1 == 0) {
    ((void)(param_1), (void)(0x70), f33_return_only_stub_71ce0());
  }
  return;
}



void FUN_00072010(undefined2 param_1)

{
  int iVar1;
  
  iVar1 = FUN_0007475a();
  if (iVar1 == 0) {
    ((void)(param_1), (void)(0), f33_return_only_stub_71ce0());
  }
  return;
}



void FUN_0007202c(ushort param_1,void *param_2)

{
  f33_nvm_set_write_buffer(param_1, camry_host_addr(param_2));
  return;
}



void FUN_0007203a(undefined2 param_1)

{
  int iVar1;
  
  iVar1 = FUN_0007476a();
  if (iVar1 == 0) {
    ((void)(param_1), (void)(0x70), f33_return_only_stub_71ce0());
  }
  return;
}



void FUN_00072058(undefined2 param_1)

{
  int iVar1;
  
  iVar1 = FUN_0007476a();
  if (iVar1 == 0) {
    ((void)(param_1), (void)(0), f33_return_only_stub_71ce0());
  }
  return;
}



void FUN_00072074(ushort param_1,void *param_2)

{
  f33_nvm_set_read_buffer(param_1, camry_host_addr(param_2));
  return;
}



void FUN_00072082(undefined2 param_1)

{
  int iVar1;
  
  iVar1 = FUN_0007475a();
  if (iVar1 == 0) {
    ((void)(param_1), (void)(0x77), f33_return_only_stub_71ce0());
  }
  return;
}



void FUN_000720a0(undefined2 param_1)

{
  int iVar1;
  
  iVar1 = FUN_0007475a();
  if (iVar1 == 0) {
    ((void)(param_1), (void)(0), f33_return_only_stub_71ce0());
  }
  return;
}



/* Single constant publisher: DAT_febf6100 = 1; Shape-classified from the canonical corpus; the
   target cell is not yet named, so the written state's meaning is unknown. */

void FUN_000720bc(void)

{
  DAT_febf6100 = 1;
  return;
}



void FUN_000720c8(void)

{
  FUN_00071e88(6);
  return;
}



/* Single constant publisher: DAT_febf60fd = 1; Shape-classified from the canonical corpus; the
   target cell is not yet named, so the written state's meaning is unknown. */

void FUN_000720d6(void)

{
  DAT_febf60fd = 1;
  return;
}



void FUN_000720e2(void)

{
  FUN_00071e88(3);
  return;
}



void FUN_000720f0(uint param_1)

{
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebf60fau + (uint32_t)(param_1 & 0xff) * 1u)))) == '\x04') {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebf60fau + (uint32_t)(param_1 & 0xff) * 1u)))) = '\x01';
  }
  return;
}



void FUN_00072108(uint param_1)

{
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebf60fau + (uint32_t)(param_1 & 0xff) * 1u)))) = 2;
  return;
}



void FUN_0007211a(uint param_1)

{
  f33_nvm_accumulate_diagnostic_mask((uint)(&PTR_DAT_000273dc)[param_1 & 0xff]);
  return;
}



void FUN_00072130(void)

{
  FUN_000796be(2);
  DAT_febf6102 = 0xf;
  return;
}



/* Return full32 boolean(6102!=F0). Native service-state0 rejects scheduler progress; queue
   admission itself is a different contract. Exact LDBU6102 and SETFNE againstF0 produce full32
   boolean. Native service-state0 prevents scheduler progress despite valid prepared queues; queue
   admission is a different contract. */

uint f33_nvm_service_uninitialized(void)

{
  return (uint)(((int8_t)DAT_febf6102) != -0x10);
}



/* Far-call trampoline: prepare {lp},0 / jarl 0x7217E / dispose 0,{lp},lp; byte-verified against the
   exact image. Forwards with registers and stack unchanged; marked as a thunk. Forwarding shape
   machine-verified; target semantics not recovered. */

void thunk_FUN_0007217e(void)

{
  FUN_0007217e();
  return;
}



uint FUN_000722d4(short param_1,uint param_2)

{
  undefined *puVar1;
  int iVar2;
  uint uVar3;
  code *pcVar4;
  
  puVar1 = ((undefined *)camry_host_ptr(0x23dfcu));
  param_2 = param_2 & 0xff;
  iVar2 = FUN_00073c76();
  if (iVar2 == 1) {
    iVar2 = param_1 * 0x18;
    if (param_2 == 4) {
      uVar3 = FUN_00073a5c(DAT_febf6114, 0xff, ((uint *)camry_host_ptr((uint32_t)(0x3614u + (int)camry_host_addr(puVar1)))));
      if ((byte)puVar1[iVar2 + 0x36d4] <= uVar3) {
        return 4;
      }
      pcVar4 = *(code **)(uVar3 * 4 + *(int *)(puVar1 + iVar2 + 0x36d8));
    }
    else {
      puVar1 = puVar1 + iVar2;
      if (param_2 == 8) {
        pcVar4 = *(code **)(((undefined *)camry_host_ptr(0x36dcu)) + (int)camry_host_addr(puVar1));
      }
      else if (param_2 == 0x20) {
        pcVar4 = *(code **)(puVar1 + 0x36e4);
      }
      else {
        pcVar4 = *(code **)(0x36deu + (int)camry_host_addr((puVar1 + 2)));
      }
    }
    param_2 = (*(int (*)())pcVar4)();
  }
  return param_2;
}



bool FUN_00072418(void)

{
  int iVar1;
  
  iVar1 = FUN_00079420();
  if (iVar1 != 0) {
    FUN_0007305e(0);
  }
  else {
    FUN_0007305e(1);
  }
  return iVar1 != 0;
}



void FUN_00072632(void)

{
  FUN_0007252c(DAT_febf6125);
  return;
}



/* Far-call trampoline: prepare {lp},0 / jarl 0x72646 / dispose 0,{lp},lp; byte-verified against the
   exact image. Forwards with registers and stack unchanged; marked as a thunk. Forwarding shape
   machine-verified; target semantics not recovered. */

void thunk_FUN_00072646(void)

{
  FUN_00072646();
  return;
}



/* Far-call trampoline: prepare {lp},0 / jarl 0x7275E / dispose 0,{lp},lp; byte-verified against the
   exact image. Forwards with registers and stack unchanged; marked as a thunk. Forwarding shape
   machine-verified; target semantics not recovered. */

void thunk_FUN_0007275e(void)

{
  FUN_0007275e();
  return;
}



undefined4 FUN_0007285c(undefined2 param_1)

{
  int iVar1;
  undefined4 uVar2;
  char cStack_9;
  
  uVar2 = 0;
  iVar1 = ((void)(param_1), (void)(&cStack_9), f33_return_const_1_71cf4());
  if ((iVar1 == 0) && (cStack_9 == 'w')) {
    FUN_0007211a(5);
    uVar2 = 1;
  }
  return uVar2;
}



void FUN_00072888(char param_1)

{
  if ((param_1 != '\0') && (param_1 != '\x04')) {
    DAT_febf6120 = 1;
  }
  return;
}



undefined4 FUN_000729c2(void)

{
  int iVar1;
  undefined4 uVar2;
  
  iVar1 = FUN_00072418();
  if (iVar1 == 0) {
    uVar2 = FUN_00072958();
  }
  else {
    uVar2 = 2;
    DAT_febf6114 = 0x3f721401;
  }
  return uVar2;
}



/* Far-call trampoline: prepare {lp},0 / jarl 0x729C2 / dispose 0,{lp},lp; byte-verified against the
   exact image. Forwards with registers and stack unchanged; marked as a thunk. Forwarding shape
   machine-verified; target semantics not recovered. */

void thunk_FUN_000729c2(void)

{
  FUN_000729c2();
  return;
}



void FUN_00072b76(void)

{
  FUN_00072a76(DAT_febf6122,DAT_febf6125);
  return;
}



void FUN_00072c2c(void)

{
  FUN_00072bae(0x16,8);
  return;
}



void FUN_00072c3e(void)

{
  FUN_00072bae(0x26,0);
  return;
}



void FUN_00072c50(void)

{
  FUN_00072bae(0x36,6);
  return;
}



void FUN_00072c62(uint param_1,ushort param_2,uint param_3,uchar param_4,undefined1 param_5)

{
  ushort uVar1;
  undefined8 uVar2;
  uint uVar3;
  
  uVar2 = 0x23dfc00000000;
  uVar1 = f33_nvm_logical_descriptor_count - 1;
  while( true ) {
    uVar3 = param_1 & 0xffff;
    if (uVar1 < uVar3) break;
    if (param_2 == ((*((ushort *)camry_host_ptr((uint32_t)(uVar3 * 0x10 + (int)((ulonglong)uVar2 >> 0x20) + 0x2e1a)))) & param_2))
    {
      FUN_00071f28(uVar3,param_3);
      FUN_0007211a(param_5);
      f33_nvm_publish_logical_result((ushort)param_1,param_3,param_4);
      FUN_00071f82(uVar3,param_3);
    }
    param_1 = uVar3 + 1;
  }
  return;
}



void FUN_00072cba(undefined2 param_1,uint param_2,undefined1 param_3,uchar param_4,
                 undefined1 param_5,char param_6)

{
  ushort logical_handle;
  
  logical_handle = DAT_febf6122;
  ((void)(0), f33_return_only_stub_73c86());
  FUN_0007211a(param_5);
  if (param_2 == 0x2ece2284) {
    FUN_00072010(logical_handle);
  }
  else if (param_2 == 0xea907101) {
    FUN_00072058(logical_handle);
  }
  if (param_6 == '\x01') {
    f33_nvm_publish_logical_result(logical_handle,param_2,param_4);
  }
  FUN_00071f82(logical_handle,param_2);
  if (param_6 == '\x01') {
    FUN_00072c62(logical_handle + 1,param_1,param_2,param_4,param_5);
  }
  FUN_0007289e(param_3);
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_72e2c(void)

{
  return;
}



bool FUN_00072eac(uint *param_1)

{
  int iVar1;
  uint uVar2;
  bool bVar3;
  undefined1 auStack_1c [16];
  
  bVar3 = false;
  iVar1 = FUN_00073516(auStack_1c);
  if (iVar1 == 0) {
    uVar2 = f33_nvm_uses_reserved_queue((ushort)param_1[1],*param_1);
    bVar3 = uVar2 != 1;
  }
  return bVar3;
}



/* Snapshot via721C6. Idle:73C76==1 calls72E70, otherwise abort72130 (lower operation state2).
   Active status1 calls72ED4; status2 skips it. Always finish723D6. Native quiet scans,
   ascending-header admission bounded before726C4, phase08 queue retention and explicit10/20
   terminal dequeue/recycle/result1/6. These terminal inputs do not prove physical programming
   reached those phases. Snapshot721C6. Idle calls72E70 only when73C76 returns1, otherwise
   abort72130; active status1 calls72ED4, status2 skips it; always723D6. Native quiet scan/wrap,
   ascending header selection bounded before726C4, and explicit08/10/20 terminal
   retention/dequeue/recycle/result1/6. Terminal-state fixtures are not evidence of physical
   programming progress. */

void f33_nvm_service_scheduler(void)

{
  uint uVar1;
  int iVar2;
  F33NvmOperation FStack_14;
  
  uVar1 = f33_nvm_snapshot_scheduler_operation(&FStack_14);
  if (uVar1 == 0) {
    iVar2 = FUN_00073c76();
    if (iVar2 == 1) {
      FUN_00072e70();
    }
    else {
      FUN_00072130();
    }
  }
  else if (uVar1 != 2) {
    ((void)(&FStack_14), FUN_00072ed4());
  }
  FUN_000723d6();
  return;
}



bool FUN_00072f1e(ushort param_1)

{
  uint uVar1;
  F33NvmOperation FStack_1c;
  
  uVar1 = f33_nvm_snapshot_scheduler_operation(&FStack_1c);
  return (uVar1 == 1 || uVar1 == 2) && FStack_1c.logical_handle == param_1;
}



void FUN_00072f76(undefined1 param_1)

{
  FUN_00072248(param_1);
  return;
}



char FUN_00072fc8(char param_1)

{
  if (param_1 != '&') {
    if (param_1 == '6') {
      param_1 = '\x06';
    }
    return param_1;
  }
  return '\x01';
}



void FUN_00073024(uint param_1,char param_2)

{
  uchar result;
  
  if (param_2 != '\x16') {
    FUN_000739e8();
    f33_return_only_stub_73a06();
    result = FUN_00072fc8(param_2);
    f33_nvm_publish_logical_result(0,param_1,result);
    FUN_00071eb4(0,param_1);
  }
  ((void)(0), FUN_000747d2());
  return;
}



void FUN_0007305e(char param_1)

{
  undefined *puVar1;
  
  puVar1 = ((undefined *)camry_host_ptr((uint32_t)(0x5)));
  if (param_1 == '\x01') {
    puVar1 = ((undefined *)camry_host_ptr(0xfde8u));
  }
  FUN_000747c8(0, camry_host_addr(puVar1));
  return;
}



/* Publish logical result6 unless low16 handle equalsFEBF6126. Result6 is not event6. Publish
   result6 unless logical equals6126 exclusion halfword. Preserve operation marker for event lookup.
   Result6 is not event6 or normal success. */

void f33_nvm_notify_reset_result(ushort logical_handle,uint operation)

{
  if (f33_nvm_reset_notification_exclusion != logical_handle) {
    f33_nvm_publish_logical_result(logical_handle,operation,'\x06');
  }
  return;
}



void FUN_00073094(void)

{
  FUN_00072f76(1);
  return;
}



/* Set head/tailFFFF in all127 headers; do not inspect slots. Clear all127 head/tail pairs toFFFF
   without touching slots. Exact header extent and adjacent records checked through cold
   initializer. */

void f33_nvm_clear_queue_headers(void)

{
  uint uVar1;
  uint uVar2;
  
  uVar2 = 0;
  do {
    uVar1 = uVar2 + 1;
    f33_nvm_queue_headers[uVar2].head = 0xffff;
    f33_nvm_queue_headers[uVar2].tail = 0xffff;
    uVar2 = uVar1;
  } while (uVar1 < 0x7f);
  return;
}



/* Return low16(base+offset), zero-extended. No queue bounds check. Return zero-extended
   low16(base+offset); no local queue bound. Actual final normal queue126 exercised through
   logical123. */

uint f33_nvm_queue_index(uint base,uint offset)

{
  return offset + base & 0xffff;
}



/* Relink inclusive range. For nonfree old markers, logical2..123 calls 73078 before clearing;
   invalid logical calls72130 then still clears. Final nextFFFF. No queue/range validation; not
   proof of a warm-boot entry. Relink inclusive slot range. Nonfree old marker with logical2..123
   invokes73078; invalid logical invokes72130 then still clears. Reset markers/buffers/handles and
   final nextFFFF. No local range validation; not a warm-boot claim. */

void f33_nvm_reset_slot_range_notifying(ushort queue,ushort first,ushort last)

{
  ushort uVar1;
  ushort logical_handle;
  uint operation;
  uint uVar2;
  
  uVar1 = f33_nvm_logical_descriptor_count - 1;
  f33_nvm_queue_headers[queue].head = first;
  f33_nvm_queue_headers[queue].tail = last;
  for (uVar2 = (uint)first; uVar2 <= last; uVar2 = uVar2 + 1 & 0xffff) {
    operation = f33_nvm_queue_slots[uVar2].operation;
    if (operation != 0x9da70ae7) {
      logical_handle = f33_nvm_queue_slots[uVar2].logical_handle;
      if ((uVar1 < logical_handle) || (logical_handle < 2)) {
        FUN_00072130();
      }
      else {
        f33_nvm_notify_reset_result(logical_handle,operation);
      }
    }
    f33_nvm_queue_slots[uVar2].operation = 0x9da70ae7;
    f33_nvm_queue_slots[uVar2].logical_handle = 0xffff;
    f33_nvm_queue_slots[uVar2].read_buffer = 0;
    f33_nvm_queue_slots[uVar2].write_buffer = 0;
    f33_nvm_queue_slots[uVar2].next = (short)uVar2 + 1;
  }
  f33_nvm_queue_slots[last].next = 0xffff;
  return;
}



/* WARNING: This is an inlined function */
/* Set header and inclusive unsigned16 range to free marker, NULL buffers, logicalFFFF, ascending
   next; last.nextFFFF. Preserve r10:7319A carries pool1 across this call. Inline actual p-code, not
   an invented return value. No range validation; lastFFFF wraps the loop. Reset inclusive
   unsigned16 slot range without old-operation notifications; Preserve r10 carrying pool1
   through7319A. Actual p-code inlined, no fabricated return. No bounds validation; lastFFFF would
   wrap. */

void f33_nvm_reset_slot_range(ushort queue,ushort first,ushort last)

{
  uint uVar1;
  
  f33_nvm_queue_headers[queue].head = first;
  f33_nvm_queue_headers[queue].tail = last;
  for (uVar1 = (uint)first; uVar1 <= last; uVar1 = uVar1 + 1 & 0xffff) {
    f33_nvm_queue_slots[uVar1].operation = 0x9da70ae7;
    f33_nvm_queue_slots[uVar1].read_buffer = 0;
    f33_nvm_queue_slots[uVar1].write_buffer = 0;
    f33_nvm_queue_slots[uVar1].logical_handle = 0xffff;
    f33_nvm_queue_slots[uVar1].next = (short)uVar1 + 1;
  }
  f33_nvm_queue_slots[last].next = 0xffff;
  return;
}



/* WARNING: Inlined function: f33_nvm_reset_slot_range */
/* Clear127 headers; reset pool0 slot122 and pool1 slots0..121. Exactly notify==1 selects
   old-operation notifications. Set free counts1/122 and used counts0/0. Does not initialize the
   notification-exclusion handle. Initialize pool0 slot122 and pool1 slots0..121, free counts1/122
   and used0/0. Exactly mode1 selects notifying reset; other modes select plain reset. Both paths
   executed. */

void f33_nvm_reset_pooled_queues(uchar notify)

{
  uint uVar1;
  uint uVar2;
  uint uVar3;
  
  f33_nvm_clear_queue_headers();
  uVar2 = f33_nvm_queue_index(0,0);
  uVar3 = f33_nvm_queue_index(1,0);
  uVar1 = 0x7a;
  if (notify == '\x01') {
    f33_nvm_reset_slot_range_notifying((ushort)uVar2,0x7a,0x7a);
    f33_nvm_reset_slot_range_notifying((ushort)uVar3,0,0x79);
  }
  else {
    f33_nvm_queue_headers[uVar2 & 0xffff].head = 0x7a;
    f33_nvm_queue_headers[uVar2 & 0xffff].tail = 0x7a;
    for (; uVar1 < 0x7b; uVar1 = uVar1 + 1 & 0xffff) {
      f33_nvm_queue_slots[uVar1].operation = 0x9da70ae7;
      f33_nvm_queue_slots[uVar1].read_buffer = 0;
      f33_nvm_queue_slots[uVar1].write_buffer = 0;
      f33_nvm_queue_slots[uVar1].logical_handle = 0xffff;
      f33_nvm_queue_slots[uVar1].next = (short)uVar1 + 1;
    }
    f33_nvm_queue_slots[0x7a].next = 0xffff;
                    /* WARNING: Could not inline here */
    f33_nvm_reset_slot_range((ushort)uVar3,0,0x79);
  }
  f33_nvm_reserved_free_count = 1;
  f33_nvm_normal_free_count = 0x7a;
  f33_nvm_reserved_used_count = 0;
  f33_nvm_normal_used_count = 0;
  return;
}



bool FUN_00073274(void)

{
  bool bVar1;
  
  bVar1 = false;
  if (((ushort)(f33_nvm_reserved_free_count + f33_nvm_reserved_used_count) == 1) &&
     ((ushort)(f33_nvm_normal_free_count + f33_nvm_normal_used_count) == 0x7a)) {
    bVar1 = (ushort)(f33_nvm_normal_used_count + f33_nvm_reserved_used_count) != 0;
  }
  else {
    FUN_00072130();
  }
  return bVar1;
}



/* Both sentinels:empty1/return0; neither:empty0/return0. Exactly one sentinel calls72130, returns1
   and leaves output unchanged. Both sentinel fields mean empty; neither means nonempty. Exactly
   oneFFFF invokes72130 and returns1 without assigning empty output. Not a slot-chain traversal. */

uint f33_nvm_check_queue_empty(F33NvmQueueHeader *header,uchar *empty)

{
  if (header->head == 0xffff) {
    if (header->tail == 0xffff) {
      *empty = '\x01';
      return 0;
    }
  }
  else if (header->tail != 0xffff) {
    *empty = '\0';
    return 0;
  }
  FUN_00072130();
  return 1;
}



/* Queues0/2 accept only122; all other queue values accept0..121. Invalid slot calls72130 and
   returns1, else0. Does not bound queue itself. Queues0/2 require slot122; all other queue values
   require0..121. Invalid index invokes72130 then returns1; valid returns0. No queue-id bound. */

uint f33_nvm_check_slot_partition(ushort index,ushort queue)

{
  ushort uVar1;
  uint uVar2;
  ushort uVar3;
  
  uVar2 = 0;
  if ((queue == 0) || (queue == 2)) {
    uVar1 = 0x7a;
    uVar3 = uVar1;
  }
  else {
    uVar1 = 0;
    uVar3 = 0x79;
  }
  if ((uVar3 < index) || (index < uVar1)) {
    FUN_00072130();
    uVar2 = 1;
  }
  return uVar2;
}



bool FUN_00073334(uint param_1,short param_2)

{
  ushort logical_handle;
  uint uVar1;
  uint uVar2;
  bool bVar3;
  
  logical_handle = f33_nvm_queue_slots[param_1 & 0xffff].logical_handle;
  bVar3 = true;
  if ((logical_handle <= (ushort)(f33_nvm_logical_descriptor_count - 1)) && (1 < logical_handle)) {
    uVar2 = f33_nvm_queue_key(logical_handle);
    uVar1 = 0;
    if (param_2 != 2) {
      uVar1 = (uint)(ushort)(param_2 - 3);
    }
    bVar3 = uVar2 != uVar1;
    if (uVar2 == uVar1) {
      return false;
    }
  }
  FUN_00072130();
  return bVar3;
}



undefined4 FUN_00073380(ushort param_1,ushort *param_2)

{
  ushort index;
  uint uVar1;
  int iVar2;
  undefined4 uVar3;
  uchar uStack_15;
  
  uVar3 = 1;
  uStack_15 = '\0';
  uVar1 = f33_nvm_check_queue_empty(f33_nvm_queue_headers + param_1,&uStack_15);
  if ((uVar1 == 0) && (uStack_15 == '\0')) {
    index = f33_nvm_queue_headers[param_1].head;
    uVar1 = f33_nvm_check_slot_partition(index,param_1);
    if ((uVar1 == 0) && (iVar2 = FUN_00073334(index,(uint)param_1), iVar2 == 0)) {
      *param_2 = index;
      uVar3 = 0;
    }
  }
  return uVar3;
}



undefined4 FUN_000733da(ushort param_1,short param_2,undefined2 *param_3)

{
  ushort uVar1;
  int iVar2;
  uint uVar3;
  undefined2 uStack_16;
  
  uVar1 = param_2 + param_1;
  uStack_16 = 0xffff;
  while( true ) {
    if (uVar1 <= param_1) {
      return 1;
    }
    iVar2 = FUN_00073380(param_1,&uStack_16);
    if (iVar2 == 0) break;
    param_1 = param_1 + 1;
  }
  uVar3 = f33_nvm_service_uninitialized();
  if (uVar3 != 0) {
    return 1;
  }
  *param_3 = uStack_16;
  return 0;
}



void FUN_00073424(undefined4 *param_1,undefined4 *param_2)

{
  *param_1 = *param_2;
  *(undefined2 *)(param_1 + 1) = *(undefined2 *)(param_2 + 3);
  param_1[2] = param_2[1];
  param_1[3] = param_2[2];
  return;
}



/* Empty tail sets head; otherwise validate old tail partition and link its next. Set tail=index and
   new nextFFFF. Return0 or1 on old-tail failure. Does not validate new index or head/tail
   consistency. TailFFFF sets head; otherwise validate old tail partition and link old tail.next.
   Set tail and new nextFFFF. Reject bad old tail before append; no new-index validation or header
   consistency check. */

uint f33_nvm_append_queue_slot(ushort queue,ushort index)

{
  ushort index_00;
  uint uVar1;
  
  index_00 = f33_nvm_queue_headers[queue].tail;
  if (index_00 == 0xffff) {
    f33_nvm_queue_headers[queue].head = index;
  }
  else {
    uVar1 = f33_nvm_check_slot_partition(index_00,queue);
    if (uVar1 != 0) {
      return 1;
    }
    f33_nvm_queue_slots[index_00].next = index;
  }
  f33_nvm_queue_headers[queue].tail = index;
  f33_nvm_queue_slots[index].next = 0xffff;
  return 0;
}



/* WARNING: This is an inlined function */
/* Copy operation+0/+4/+8/+C into slot+0/+C/+4/+8; preserve slot.next. Preserve r10, carrying append
   success through7365C; inline actual p-code. Convert operation fields+0/+4/+8/+C to
   slot+0/+C/+4/+8, preserving next. Preserves r10 append status through7365C; inline real p-code.
    */

void f33_nvm_copy_operation_to_slot(F33NvmQueueSlot *slot,F33NvmOperation *operation)

{
  slot->operation = operation->operation;
  slot->logical_handle = operation->logical_handle;
  slot->read_buffer = operation->buffer_08;
  slot->write_buffer = operation->buffer_0c;
  return;
}



/* WARNING: Inlined function: f33_nvm_copy_operation_to_slot */
/* Append index, then copy operation only on success. Return append status. Append slot then copy
   operation only on successful append. Return append status surviving actual73640; no payload read.
    */

uint f33_nvm_append_operation(ushort queue,ushort index,F33NvmOperation *operation)

{
  uint uVar1;
  
  uVar1 = f33_nvm_append_queue_slot(queue,index);
  if (uVar1 == 0) {
    f33_nvm_queue_slots[index].operation = operation->operation;
    f33_nvm_queue_slots[index].logical_handle = operation->logical_handle;
    f33_nvm_queue_slots[index].read_buffer = operation->buffer_08;
    f33_nvm_queue_slots[index].write_buffer = operation->buffer_0c;
  }
  return uVar1;
}



undefined4 FUN_00073828(ushort *param_1,ushort param_2,ushort *param_3,undefined2 *param_4)

{
  ushort uVar1;
  uint uVar2;
  uint uVar3;
  int iVar4;
  
  uVar1 = *param_1;
  iVar4 = 0x7b;
  uVar3 = 0xffffffff;
  do {
    uVar2 = (uint)uVar1;
    if (uVar2 == 0xffff) {
      return 1;
    }
    if (0x7a < uVar2) {
      FUN_00072130();
      return 1;
    }
    if (param_2 == f33_nvm_queue_slots[uVar2].logical_handle) {
      *param_3 = uVar1;
      *param_4 = (short)uVar3;
      return 0;
    }
    uVar1 = f33_nvm_queue_slots[uVar2].next;
    iVar4 = iVar4 + -1;
    uVar3 = uVar2;
  } while (iVar4 != 0);
  return 1;
}



/* WARNING: Inlined function: f33_nvm_unlink_queue_slot */

int FUN_00073878(undefined2 param_1,uint param_2,ushort *param_3)

{
  F33NvmQueueHeader *header;
  ushort uVar1;
  uint uVar2;
  int iVar3;
  uchar uStack_19;
  ushort uStack_18;
  ushort uStack_16;
  
  uStack_18 = 0xffff;
  uStack_16 = 0xffff;
  iVar3 = 1;
  uStack_19 = '\0';
  header = f33_nvm_queue_headers + (param_2 & 0xffff);
  uVar2 = f33_nvm_check_queue_empty(header,&uStack_19);
  if (((uVar2 == 0) && (uStack_19 == '\0')) &&
     (iVar3 = FUN_00073828(header,param_1,&uStack_18,&uStack_16), iVar3 == 0)) {
    uVar1 = f33_nvm_queue_slots[uStack_18].next;
    if (uStack_16 == 0xffff) {
      header->head = uVar1;
      uStack_16 = uVar1;
    }
    else {
      f33_nvm_queue_slots[uStack_16].next = uVar1;
      uVar1 = f33_nvm_queue_slots[uStack_18].next;
    }
    if (uVar1 == 0xffff) {
      f33_nvm_queue_headers[param_2 & 0xffff].tail = uStack_16;
    }
    *param_3 = uStack_18;
  }
  return iVar3;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_73a06(void)

{
  return;
}



undefined4 FUN_00073a5c(int param_1,undefined4 param_2,uint *param_3)

{
  uint uVar1;
  
  uVar1 = 0;
  while( true ) {
    if (*param_3 <= uVar1) {
      return param_2;
    }
    if (*(int *)(param_3[1] + uVar1 * 8) == param_1) break;
    uVar1 = uVar1 + 1;
  }
  return *(undefined4 *)(param_3[1] + uVar1 * 8 + 4);
}



/* Copy only fields+0,+4,+8,+C intoFEBF6AEC. Do not copy the two padding bytes or adjacent dispatch
   state. Copy request fields+0/+4/+8/+C intoFEBF6AEC; leave padding+6/+7 untouched. Executed as the
   real callee of73AFC with distinct input/global padding. No whole-structure memcpy or validation.
    */

void f33_nvm_copy_operation(F33NvmOperation *request)

{
  f33_nvm_pending_operation.operation = request->operation;
  f33_nvm_pending_operation.logical_handle = request->logical_handle;
  f33_nvm_pending_operation.buffer_08 = request->buffer_08;
  f33_nvm_pending_operation.buffer_0c = request->buffer_0c;
  return;
}



/* Zero-extend low8 and call73EEE. Initialized74164 selects the nonzero branch. Zero-extend low8
   argument and call73EEE; no independent policy or pointer invocation. Real initialized service
   chooses nonzero poll selector; behavior established with callee bytes and composed execution. */

void f33_nvm_select_service_poll(uchar full_service)

{
  f33_nvm_set_service_poll(full_service);
  return;
}



/* Far-call trampoline: prepare {lp},0 / jarl 0x766C6 / dispose 0,{lp},lp; byte-verified against the
   exact image. Forwards with registers and stack unchanged; marked as a thunk. Forwarding shape
   machine-verified; target semantics not recovered. */

void thunk_FUN_000766c6(void)

{
  FUN_000766c6();
  return;
}



void FUN_00073c14(void)

{
  uint uVar1;
  
  if (f33_nvm_operation_state == '\x02') {
    uVar1 = FUN_00073a5c(f33_nvm_pending_operation.operation,0xffffffff,((undefined *)camry_host_ptr(0x2758cu)));
    if (uVar1 < 2) {
      FUN_00073ba0(uVar1);
    }
    else {
      FUN_00072130();
    }
  }
  return;
}



/* Call physical cancellation7664E first; then if6B00==2 set6AFC=8. 72248 calls this before
   inspecting its own module marker. Native classifier mode exit exercises the active and inactive
   logical-operation cases. Physical cancellation7664E first; if logical state6B00==2 set
   phase6AFC=8. Runs before72248 module-marker test. Native exact active-phase transition and
   inactive logical-context preservation. */

void f33_nvm_cancel_logical_operation(void)

{
  f33_nvm_cancel_physical_operation();
  if (f33_nvm_operation_state == '\x02') {
    f33_nvm_operation_phase = 8;
  }
  return;
}



uchar FUN_00073c6c(void)

{
  return f33_nvm_operation_state;
}



undefined1 FUN_00073c76(void)

{
  undefined1 uVar1;
  
  if (f33_nvm_operation_state == '\x02') {
    uVar1 = 2;
  }
  else {
    uVar1 = 1;
  }
  return uVar1;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_73c86(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_73ca0(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_73ca2(void)

{
  return;
}



void FUN_00073cb0(ushort param_1,undefined4 param_2,undefined2 param_3,undefined4 param_4,
                 undefined2 param_5)

{
  uint uVar1;
  
  uVar1 = f33_nvm_storage_handle(param_1);
  FUN_000720f0(4);
  ((void)(param_5), FUN_00076572(uVar1, param_3, param_4));
  return;
}



void FUN_00073cdc(ushort param_1,undefined4 param_2,undefined4 param_3)

{
  uint uVar1;
  
  uVar1 = f33_nvm_storage_handle(param_1);
  FUN_000720f0(4);
  FUN_000765fc(uVar1,param_3);
  return;
}



void FUN_00073d5a(void)

{
  uint uVar1;
  undefined1 local_c;
  char cStack_b;
  undefined2 uStack_a;
  
  uStack_a = 0xffff;
  local_c = 0xff;
  cStack_b = -1;
  uVar1 = FUN_000769a6(&uStack_a,&local_c,&cStack_b);
  if ((uVar1 & 1) != 0) {
    FUN_00072108(4);
  }
  if ((uVar1 >> 1 & 1) != 0) {
    FUN_00072108(7);
  }
  if ((cStack_b == '\x01') && (FUN_000720f0(2), (uVar1 >> 3 & 1) != 0)) {
    FUN_00072108(2);
  }
  return;
}



void FUN_00073e54(void)

{
  uint uVar1;
  undefined1 local_c;
  undefined1 uStack_b;
  undefined2 uStack_a;
  
  uStack_a = 0xffff;
  local_c = 0xff;
  uStack_b = 0xff;
  uVar1 = FUN_000769a6(&uStack_a,&local_c,&uStack_b);
  if ((uVar1 & 1) != 0) {
    FUN_00072108(4);
  }
  if ((uVar1 >> 2 & 1) != 0) {
    FUN_00072108(5);
  }
  return;
}



void FUN_00073eda(void)

{
  (*(int (*)())f33_nvm_selected_service_poll)();
  return;
}



/* Actual full initializer executes5772 instructions under explicit RAM preconditions. Initialize
   logical cells, buffer overrides, abortF0, pending/active records and queues. Preserve
   service-state bytes,6126,6B14 and padding.7477A clears the same6B18 word once in this target. No
   implied blanket zeroing or reset-path completion. Full logical initializer5772 native
   instructions. Exact6000..6B1F comparison includes initialized records/pools/counters and
   preserved service bytes,6126,6B14,padding. Does not stand in for reset-to-application execution.
    */

void f33_nvm_initialize_logical_module(void)

{
  FUN_0007477a();
  f33_nvm_initialize_logical_cells();
  f33_return_only_stub_745bc();
  f33_return_only_stub_745be();
  FUN_000745c8();
  FUN_00071d7c();
  f33_nvm_initialize_operation();
  thunk_FUN_0007217e();
  f33_nvm_initialize_queues();
  f33_return_only_stub_72e2c();
  f33_return_only_stub_741ea();
  FUN_00079462(0x14);
  return;
}


