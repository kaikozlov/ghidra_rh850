#include "common.h"


void FUN_00094008(ushort param_1)

{
  f33_dcm_pending_dispatch_receive_slot = param_1;
  return;
}



ushort FUN_0009400e(void)

{
  return f33_dcm_pending_dispatch_receive_slot;
}



bool FUN_00094014(undefined2 param_1)

{
  int extraout_r8;
  short local_14;
  short sStack_12;
  short sStack_10;
  short sStack_e;
  
  local_14 = 0;
  sStack_12 = 0;
  sStack_10 = 0;
  sStack_e = 0;
  FUN_00093cce(f33_dcm_pending_dispatch_receive_slot,&local_14,&sStack_12);
  FUN_00093cce(param_1, &sStack_10, ((ushort *)camry_host_ptr((uint32_t)(extraout_r8 + 4))));
  return local_14 == sStack_10 && sStack_12 == sStack_e;
}



void FUN_0009405c(undefined2 param_1)

{
  uint uVar1;
  
  uVar1 = DAT_febe59e6 + 1;
  *(undefined2 *)(((undefined *)camry_host_ptr(0xfebe59dcu)) + (uint)DAT_febe59e6 * 2) = param_1;
  DAT_febe59e6 = (ushort)uVar1;
  if (1 < (uVar1 & 0xffff)) {
    DAT_febe59e6 = 0;
  }
  return;
}



undefined2 FUN_0009407c(void)

{
  uint uVar1;
  uint uVar2;
  uint uVar3;
  
  uVar2 = (uint)DAT_febe59e4;
  uVar1 = uVar2 + 1;
  uVar3 = uVar1 & 0xffff;
  DAT_febe59e4 = (ushort)uVar1;
  if (1 < uVar3) {
    DAT_febe59e4 = 0;
    uVar3 = 0;
  }
  if (uVar3 == DAT_febe59e6) {
    DAT_febe59e4 = 0;
    DAT_febe59e6 = 0;
  }
  return *(undefined2 *)(((undefined *)camry_host_ptr(0xfebe59dcu)) + uVar2 * 2);
}



ushort FUN_000940ae(uint param_1)

{
  return f33_dcm_receive_buffer_state[param_1 & 0xffff].remaining_capacity;
}



void FUN_000940ba(void)

{
  uint32_t puVar1;
  undefined2 uVar2;
  
  puVar1 = 0xfebeb800u;
  uVar2 = FUN_00093e82();
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x5e18)))) = uVar2;
  return;
}



ushort FUN_000940ca(void)

{
  return f33_dcm_displaced_transmit_id;
}



void FUN_000940d0(uchar param_1,char param_2)

{
  if (param_2 == '\0') {
    f33_dcm_zero_p2_deadline = param_1;
    return;
  }
  if (param_2 == '\x01') {
    f33_dcm_zero_overall_timeout = param_1;
  }
  return;
}



uchar FUN_000940e6(char param_1)

{
  uchar uVar1;
  
  if (param_1 == '\0') {
    return f33_dcm_zero_p2_deadline;
  }
  uVar1 = '\0';
  if (param_1 == '\x01') {
    uVar1 = f33_dcm_zero_overall_timeout;
  }
  return uVar1;
}



void FUN_000940fe(ushort param_1,ushort *param_2,uint param_3,undefined1 *param_4)

{
  uint uVar1;
  uint uVar2;
  ushort uVar3;
  
  uVar2 = param_3 & 0xffff;
  do {
    uVar3 = *param_2;
    if (uVar2 <= uVar3) {
      return;
    }
    uVar1 = (int)(uVar3 + uVar2) >> 1;
    if (f33_dcm_did_class[(short)uVar1].last_did < param_1) {
      uVar3 = (short)uVar1 + 1;
      *param_2 = uVar3;
      uVar1 = uVar2;
    }
    uVar2 = uVar1;
  } while ((param_1 < f33_dcm_did_class[(short)uVar3].first_did) ||
          (f33_dcm_did_class[(short)uVar3].last_did < param_1));
  *param_4 = 1;
  return;
}



undefined4 FUN_00094148(ushort param_1,ushort *param_2,byte *param_3)

{
  undefined *puVar1;
  undefined4 uVar2;
  char cStack_13;
  ushort uStack_12;
  
  puVar1 = ((undefined *)camry_host_ptr(0x23dfcu));
  cStack_13 = '\0';
  uVar2 = 1;
  if (DAT_00026016 != 0) {
    uStack_12 = 0;
    if (f33_dcm_did_class[0].first_did <= param_1) {
      if (f33_dcm_did_class[0].last_did < param_1) {
        if (param_1 <= f33_dcm_did_class[(short)(DAT_00026016 + -1)].last_did) {
          puVar1 = ((undefined *)camry_host_ptr(0x23dfcu));
          FUN_000940fe(param_1,&uStack_12,DAT_00026016 + -1,&cStack_13);
        }
      }
      else {
        cStack_13 = '\x01';
      }
    }
    if ((cStack_13 == '\x01') && (uStack_12 < 6)) {
      *param_2 = uStack_12;
      puVar1 = puVar1 + (short)uStack_12 * 0x1c;
      if ((puVar1[0x2258] == '\x01') && (*(int *)(puVar1 + 0x2240) == 0)) {
        uVar2 = 2;
      }
      else {
        if ((*((int *)camry_host_ptr((uint32_t)(*(int *)(0x2250u + (int)camry_host_addr(puVar1)) + 4)))) != 0) {
          *param_3 = 2;
        }
        if ((*((int *)camry_host_ptr((uint32_t)(*(int *)(0x2250u + (int)camry_host_addr(puVar1)) + 8)))) != 0) {
          *param_3 = *param_3 | 4;
        }
        uVar2 = 0;
      }
    }
  }
  return uVar2;
}



/* Writes capability0 then invokes94148 forkind1 or941EC; actual resolver r10 is consumed9586C.
   Existing void prototype is wrong. */

uint f33_dcm_resolve_did_group(ushort did,uchar table_kind,ushort *group,uchar *capabilities)

{
  uint uVar1;
  
  *capabilities = '\0';
  if (table_kind == '\x01') {
    uVar1 = FUN_00094148((uint)(ushort)did, group, capabilities);
  }
  else {
    uVar1 = FUN_000941ec(did,group,capabilities);
  }
  return uVar1;
}



undefined4 FUN_000942ac(char param_1,char param_2,int *param_3)

{
  byte bVar1;
  uint uVar2;
  uint uVar3;
  int iVar4;
  
  if ((uintptr_t)(param_3)==(uintptr_t)((int *)0x0)) {
    return 1;
  }
  if (param_1 == '\x01' || param_1 == '\x02') {
    if (*param_3 == 0) {
      return 1;
    }
    if (param_1 != '\x01') {
      uVar2 = (uint)(*((byte *)camry_host_ptr((uint32_t)(*param_3 + 8))));
      iVar4 = *(int *)*param_3;
      goto LAB_0009432c;
    }
    uVar2 = (uint)(*((byte *)camry_host_ptr((uint32_t)(*param_3 + 9))));
    iVar4 = *param_3;
  }
  else if (param_1 == '\x11' || param_1 == '\x12') {
    if (param_3[1] == 0) {
      return 1;
    }
    if (param_1 == '\x11') {
      bVar1 = *(byte *)(param_3[1] + 0xd);
      iVar4 = param_3[1];
LAB_00094320:
      uVar2 = (uint)bVar1;
      iVar4 = (*((int *)camry_host_ptr((uint32_t)(iVar4 + 8))));
      goto LAB_0009432c;
    }
    uVar2 = (uint)*(byte *)(param_3[1] + 0xc);
    iVar4 = param_3[1];
  }
  else {
    if (param_1 != '!' && param_1 != '\"') {
      return 1;
    }
    if (param_3[2] == 0) {
      return 1;
    }
    if (param_1 == '!') {
      bVar1 = *(byte *)(param_3[2] + 0xd);
      iVar4 = param_3[2];
      goto LAB_00094320;
    }
    uVar2 = (uint)*(byte *)(param_3[2] + 0xc);
    iVar4 = param_3[2];
  }
  iVar4 = (*((int *)camry_host_ptr((uint32_t)(iVar4 + 4))));
LAB_0009432c:
  if (uVar2 != 0) {
    if (iVar4 == 0) {
      return 1;
    }
    uVar3 = 0;
    while( true ) {
      if (uVar2 <= uVar3) {
        return 1;
      }
      if ((*((char *)camry_host_ptr((uint32_t)(uVar3 + iVar4)))) == param_2) break;
      uVar3 = uVar3 + 1 & 0xff;
    }
  }
  return 0;
}



undefined4 FUN_00094350(undefined2 param_1,undefined1 param_2,undefined1 param_3)

{
  undefined8 uVar1;
  int iVar2;
  uint uVar3;
  undefined4 uVar4;
  byte bVar5;
  byte local_20;
  uchar uStack_1f;
  ushort uStack_1e;
  ushort auStack_1c [2];
  
  uVar1 = 0x23dfc00000000;
  uVar4 = 0;
  iVar2 = FUN_00095514(param_1,&local_20);
  if ((iVar2 == 0) && (local_20 != 0)) {
    for (bVar5 = 0; bVar5 < local_20; bVar5 = bVar5 + 1) {
      iVar2 = ((void)(auStack_1c), FUN_0009552a(param_1, bVar5));
      if (((iVar2 != 0) ||
          (uVar3 = f33_dcm_resolve_did_group(auStack_1c[0],'\x01',&uStack_1e,&uStack_1f), uVar3 != 0
          )) || (iVar2 = FUN_000942ac(param_2, param_3, ((int *)camry_host_ptr((uint32_t)((*((undefined4 *)camry_host_ptr((uint32_t)(0x2250u +
                                       (short)uStack_1e * 0x1c + (int)((ulonglong)uVar1 >> 0x20))))))))),
                iVar2 != 0)) goto LAB_000943c6;
    }
  }
  else {
LAB_000943c6:
    uVar4 = 1;
  }
  return uVar4;
}



undefined4 FUN_000943ce(ushort param_1,char param_2,undefined1 param_3,undefined1 param_4)

{
  char cVar1;
  uint32_t puVar2;
  void *pvVar3;
  undefined4 uVar4;
  uint uVar5;
  int iVar6;
  uchar uStack_17;
  ushort uStack_16;
  
  cVar1 = DAT_00026019;
  puVar2 = 0x23dfcu;
  if (param_2 == '\0') {
    pvVar3 = ((void *)camry_host_ptr((uint32_t)(DAT_0002601c)));
    if (param_1 != 0) {
      return 1;
    }
  }
  else {
    if (param_2 != '\x01') {
      if (param_1 != 0) {
        return 1;
      }
      uVar5 = f33_dcm_resolve_did_group(DAT_00025fec,'\0',&uStack_16,&uStack_17);
      if ((uVar5 == 0) &&
         (iVar6 = FUN_000942ac(param_3, param_4, ((int *)camry_host_ptr((uint32_t)((*((undefined4 *)camry_host_ptr((uint32_t)(puVar2 + 0x2220)))))))), iVar6 == 0)) {
        if (cVar1 != '\x01') {
          return 0;
        }
        uVar4 = FUN_00094350(0,param_3,param_4);
        return uVar4;
      }
      return 1;
    }
    if (5 < param_1) {
      return 1;
    }
    pvVar3 = ((void *)camry_host_ptr((uint32_t)(f33_dcm_did_class[(short)param_1].policy)));
  }
  uVar4 = FUN_000942ac(param_3,param_4,pvVar3);
  return uVar4;
}



uint FUN_0009445a(ushort param_1,ushort param_2,uchar param_3,uchar *param_4)

{
  uint uVar1;
  
  uVar1 = 0;
  *param_4 = '\x01';
  if (param_1 < 6) {
    if (f33_dcm_did_class[(short)param_1].probe_presence == '\x01') {
      if (f33_dcm_did_class[(short)param_1].presence != 0x0u) {
        uVar1 = (*(int (*)())camry_indirect((uint32_t)(f33_dcm_did_class[(short)param_1].presence)))(param_2,param_3,param_4);
      }
    }
    else {
      *param_4 = '\0';
    }
  }
  return uVar1;
}



uint FUN_0009449e(ushort param_1,ushort param_2,uchar param_3,ushort *param_4)

{
  uint uVar1;
  
  *param_4 = 0;
  if (param_1 < 6) {
    uVar1 = (*(int (*)())camry_indirect((uint32_t)(f33_dcm_did_class[(short)param_1].length)))(param_2,param_3,param_4);
  }
  else {
    uVar1 = 1;
  }
  return uVar1;
}



undefined4 FUN_000944cc(undefined2 param_1,short *param_2)

{
  int iVar1;
  undefined4 uVar2;
  byte bVar3;
  byte bStack_19;
  undefined1 auStack_18 [3];
  byte bStack_15;
  
  *param_2 = 0;
  uVar2 = 0;
  iVar1 = FUN_00095514(param_1,&bStack_19);
  if ((iVar1 == 0) && (bStack_19 != 0)) {
    for (bVar3 = 0; bVar3 < bStack_19; bVar3 = bVar3 + 1) {
      iVar1 = ((void)(auStack_18), FUN_0009552a(param_1, bVar3));
      if (iVar1 != 0) goto LAB_0009451e;
      *param_2 = *param_2 + (ushort)bStack_15;
    }
  }
  else {
LAB_0009451e:
    uVar2 = 1;
  }
  return uVar2;
}



uint FUN_00094526(ushort param_1,ushort param_2,uchar *param_3,uchar param_4,ushort *param_5,
                 uchar *param_6)

{
  uint uVar1;
  
  uVar1 = 1;
  *param_5 = 0;
  *param_6 = '\0';
  if ((param_1 < 6) && (f33_dcm_did_class[(short)param_1].read != 0x0u)) {
    uVar1 = (*(int (*)())camry_indirect((uint32_t)(f33_dcm_did_class[(short)param_1].read)))(param_2,param_3,param_4,param_5,param_6);
  }
  return uVar1;
}



undefined4 FUN_0009456e(byte param_1,uint param_2,short param_3,undefined1 *param_4)

{
  int iVar1;
  undefined4 uVar2;
  
  iVar1 = (param_2 & 0xff) - 1;
  uVar2 = 0;
  if (((int)((uint)param_1 - iVar1) < 0 !=
       (iVar1 < 0 && iVar1 < 0 == (int)((uint)param_1 - iVar1) < 0)) && (param_3 == 0)) {
    DAT_febe5d20 = param_1 + 1;
    uVar2 = 10;
    *param_4 = 1;
  }
  return uVar2;
}



int FUN_00094590(undefined2 param_1,byte param_2,int param_3,ushort *param_4,undefined1 *param_5,
                short *param_6)

{
  int iVar1;
  uint uVar2;
  uint32_t puVar3;
  uint32_t puVar4;
  int iVar5;
  uint uVar6;
  undefined *puVar7;
  bool bVar8;
  byte bVar9;
  uchar uStack_2f;
  char cStack_2e;
  undefined1 uStack_2d;
  ushort uStack_2c;
  undefined1 auStack_2a [2];
  ushort uStack_28;
  byte bStack_26;
  byte bStack_25;
  
  puVar3 = 0xfebeb800u;
  puVar4 = 0x23dfcu;
  iVar5 = 1;
  *param_5 = 0;
  uStack_2d = 0;
  cStack_2e = '\0';
  bVar8 = DAT_febe5d21 != '\0';
  bVar9 = DAT_febe5d20;
  do {
    if (param_2 <= bVar9) {
      return iVar5;
    }
    iVar5 = ((void)(&uStack_28), FUN_0009552a(param_1, bVar9));
    if (((iVar5 == 0) &&
        (uVar6 = f33_dcm_resolve_did_group(uStack_28,'\x01',&uStack_2c,&uStack_2f), uVar6 == 0)) &&
       ((*((int *)camry_host_ptr((uint32_t)(puVar4 + (short)uStack_2c * 0x1c + 0x2248)))) != 0)) {
      puVar7 = ((void *)camry_host_ptr((uint32_t)(puVar3 + -0x5ade)));
      iVar5 = (*(int (*)())camry_indirect((uint32_t)(((code *)(uintptr_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(puVar4 + (short)uStack_2c * 0x1c + 0x2248))))))))(uStack_28,puVar7,bVar8,auStack_2a,&uStack_2d);
      if (iVar5 == 0) {
        (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x5adf))))) = 0;
        uVar6 = (uint)bStack_26;
        *param_6 = *param_6 + -1;
        bVar8 = false;
        if (uVar6 != 0) {
          uVar2 = 2 - bStack_25;
          if ((int)(uVar6 - uVar2) < 0 !=
              ((int)uVar2 < 0 && (int)uVar2 < 0 == (int)(uVar6 - uVar2) < 0) || uVar6 == uVar2) {
            uVar2 = 0;
            while( true ) {
              if (bStack_25 <= uVar2) break;
              iVar5 = *param_4 + uVar2;
              iVar1 = uVar6 + uVar2;
              uVar2 = uVar2 + 1 & 0xff;
              (*((undefined *)camry_host_ptr((uint32_t)(iVar5 + param_3)))) = puVar7[iVar1 + -1];
            }
            *param_4 = *param_4 + (ushort)bStack_25;
            iVar5 = FUN_0009456e(bVar9,param_2,*param_6,&cStack_2e);
            goto LAB_000946b2;
          }
        }
        goto LAB_000946ac;
      }
      if (iVar5 == 1) {
        (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x5adf))))) = 0;
        *param_5 = uStack_2d;
        goto LAB_000946ae;
      }
      cStack_2e = '\x01';
      if (iVar5 == 10) {
        (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x5adf))))) = 1;
        (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x5ae0))))) = bVar9;
      }
      else {
        (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x5adf))))) = 0;
        iVar5 = 1;
      }
    }
    else {
LAB_000946ac:
      iVar5 = 1;
LAB_000946ae:
      cStack_2e = (char)iVar5;
    }
LAB_000946b2:
    if (cStack_2e == '\x01') {
      return iVar5;
    }
    bVar9 = bVar9 + 1;
  } while( true );
}



int FUN_000946c6(undefined2 param_1,undefined4 param_2,char param_3,undefined2 *param_4,
                undefined1 *param_5,undefined4 param_6)

{
  uint32_t puVar1;
  uint32_t puVar2;
  int iVar3;
  uint uVar4;
  int iVar5;
  undefined1 uStack_1f;
  char cStack_1e;
  uchar uStack_1d;
  ushort auStack_1c [3];
  ushort uStack_16;
  
  puVar1 = 0xfebeb800u;
  puVar2 = 0x23dfcu;
  iVar5 = 1;
  *param_5 = 0;
  uStack_1f = 0;
  *param_4 = 0;
  if (param_3 == '\x02') {
    if (DAT_febe5d21 == '\x01') {
      puVar1 = 0xfebeb800u;
      iVar3 = ((void)(auStack_1c), FUN_0009552a(param_1, DAT_febe5d20));
      if (((iVar3 == 0) &&
          (uVar4 = f33_dcm_resolve_did_group(auStack_1c[0],'\x01',&uStack_16,&uStack_1d), uVar4 == 0
          )) && ((*((int *)camry_host_ptr((uint32_t)(puVar2 + (short)uStack_16 * 0x1c + 0x2248)))) != 0)) {
        iVar5 = (*(int (*)())camry_indirect((uint32_t)(((code *)(uintptr_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(puVar2 + (short)uStack_16 * 0x1c + 0x2248))))))))(auStack_1c[0],param_2,2,param_4,&uStack_1f);
      }
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x5adf))))) = 0;
    }
  }
  else {
    puVar1 = 0xfebeb800u;
    iVar3 = FUN_00095514(param_1,&cStack_1e);
    if (((iVar3 == 0) && (cStack_1e != '\0')) &&
       (iVar5 = FUN_00094590(param_1, cStack_1e, param_2, param_4, param_5, ((short *)camry_host_ptr((uint32_t)(param_6)))), iVar5 == 10)) {
      return 10;
    }
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x5ae0))))) = 0;
  return iVar5;
}



uint FUN_00094786(ushort param_1,ushort param_2,uchar *param_3,uchar param_4,ushort param_5,
                 uchar *param_6)

{
  uint uVar1;
  
  uVar1 = 1;
  *param_6 = '\0';
  if ((param_1 < 6) && (f33_dcm_did_class[(short)param_1].write != 0x0u)) {
    uVar1 = (*(int (*)())camry_indirect((uint32_t)(f33_dcm_did_class[(short)param_1].write)))(param_2,param_3,param_4,param_5,param_6);
  }
  return uVar1;
}



uint FUN_0009487e(short param_1,int param_2,uint param_3)

{
  uint uVar1;
  
  if (param_3 == 0 && param_2 == 0) {
    uVar1 = param_3 & 0xff;
  }
  else {
    uVar1 = 1;
    if ((param_1 == 0) && (DAT_00026024 != 0x0u)) {
      uVar1 = (*(int (*)())DAT_00026024)(param_2,param_3);
    }
  }
  return uVar1;
}



uint FUN_000948ae(short param_1,uint param_2,undefined1 *param_3)

{
  int iVar1;
  uint uVar2;
  uint uVar3;
  undefined1 uStack_11;
  
  *param_3 = 0;
  uVar3 = 1;
  if ((param_1 == 0) && ((param_2 & 0xff) < (uint)DAT_0002602a)) {
    iVar1 = (param_2 & 0xff) * 8;
    uVar2 = (uint)(*((byte *)camry_host_ptr((uint32_t)(*(int *)(DAT_00026020 + iVar1) + 0xf))));
    if (((uVar2 - 1 < 4) || (uVar2 == 6 || uVar2 == 7)) &&
       (uVar2 = (*(int (*)())**(undefined4 **)(DAT_00026020 + iVar1))(&uStack_11), uVar2 < 2)) {
      *param_3 = uStack_11;
      uVar3 = uVar2;
    }
  }
  return uVar3;
}



uint FUN_00094906(short param_1,uint param_2,undefined1 param_3,undefined1 *param_4)

{
  int iVar1;
  short sVar2;
  uint uVar3;
  undefined1 uStack_11;
  
  *param_4 = 0;
  uVar3 = 1;
  if ((param_1 == 0) && ((param_2 & 0xff) < (uint)DAT_0002602a)) {
    iVar1 = (param_2 & 0xff) * 8;
    sVar2 = (*((short *)camry_host_ptr((uint32_t)(*(int *)(DAT_00026020 + iVar1) + 4))));
    uVar3 = (uint)(*((byte *)camry_host_ptr((uint32_t)(*(int *)(iVar1 + DAT_00026020) + 0xf))));
    if (uVar3 - 1 < 4) {
      if (sVar2 != 0) {
        return 1;
      }
      if (DAT_00026008 == 0x0u) {
        return 1;
      }
      uVar3 = (*(int (*)())DAT_00026008)(param_3,&uStack_11);
      if (((uVar3 != 0) && (uVar3 != 1)) && (uVar3 != 10)) {
        return 1;
      }
    }
    else {
      if (uVar3 != 6 && uVar3 != 7) {
        return 1;
      }
      if (sVar2 != 0) {
        return 1;
      }
      if (DAT_00026004 == 0x0u) {
        return 1;
      }
      uVar3 = (*(int (*)())DAT_00026004)(&uStack_11);
      if (1 < uVar3) {
        return 1;
      }
    }
    *param_4 = uStack_11;
  }
  return uVar3;
}



uint FUN_0009499a(short param_1,uint param_2,undefined1 param_3,undefined1 *param_4)

{
  int iVar1;
  short sVar2;
  uint uVar3;
  undefined1 uStack_11;
  
  *param_4 = 0;
  uVar3 = 1;
  if ((param_1 == 0) && ((param_2 & 0xff) < (uint)DAT_0002602a)) {
    iVar1 = (param_2 & 0xff) * 8;
    sVar2 = (*((short *)camry_host_ptr((uint32_t)(*(int *)(DAT_00026020 + iVar1) + 6))));
    uVar3 = (uint)(*((byte *)camry_host_ptr((uint32_t)(*(int *)(iVar1 + DAT_00026020) + 0xf))));
    if (uVar3 - 1 < 4) {
      if (sVar2 != 0) {
        return 1;
      }
      if (DAT_00025ff4 == 0x0u) {
        return 1;
      }
      uVar3 = (*(int (*)())DAT_00025ff4)(param_3,&uStack_11);
      if (((uVar3 != 0) && (uVar3 != 1)) && (uVar3 != 10)) {
        return 1;
      }
    }
    else {
      if (uVar3 != 6 && uVar3 != 7) {
        return 1;
      }
      if (sVar2 != 0) {
        return 1;
      }
      if (DAT_00025ff0 == 0x0u) {
        return 1;
      }
      uVar3 = (*(int (*)())DAT_00025ff0)(&uStack_11);
      if (1 < uVar3) {
        return 1;
      }
    }
    *param_4 = uStack_11;
  }
  return uVar3;
}



uint FUN_00094a2e(short param_1,uint param_2,int param_3,undefined1 param_4,undefined1 *param_5)

{
  int iVar1;
  short sVar2;
  int iVar3;
  uint uVar4;
  undefined1 uStack_d;
  
  uVar4 = 1;
  *param_5 = 0;
  if ((param_1 == 0) && ((param_2 & 0xff) < (uint)DAT_0002602a)) {
    iVar1 = (param_2 & 0xff) * 8;
    iVar3 = 0;
    if ((*((char *)camry_host_ptr((uint32_t)(*(int *)(DAT_00026020 + iVar1) + 0xe)))) != '\0') {
      iVar3 = (int)(uint)(*((ushort *)camry_host_ptr((uint32_t)(DAT_00026020 + iVar1 + 4)))) >> 3;
    }
    sVar2 = (*((short *)camry_host_ptr((uint32_t)(*(int *)(DAT_00026020 + iVar1) + 8))));
    uVar4 = (uint)(*((byte *)camry_host_ptr((uint32_t)(*(int *)(DAT_00026020 + iVar1) + 0xf))));
    if (uVar4 - 1 < 4) {
      if (sVar2 != 0) {
        return 1;
      }
      if (DAT_00026010 == 0x0u) {
        return 1;
      }
      uVar4 = (*(int (*)())camry_indirect((uint32_t)(DAT_00026010)))(iVar3 + param_3,param_4,&uStack_d);
      if (((uVar4 != 0) && (uVar4 != 1)) && (uVar4 != 10)) {
        return 1;
      }
    }
    else {
      if (uVar4 != 6 && uVar4 != 7) {
        return 1;
      }
      if (sVar2 != 0) {
        return 1;
      }
      if (DAT_0002600c == 0x0u) {
        return 1;
      }
      uVar4 = (*(int (*)())camry_indirect((uint32_t)(DAT_0002600c)))(iVar3 + param_3,&uStack_d);
      if (1 < uVar4) {
        return 1;
      }
    }
    *param_5 = uStack_d;
  }
  return uVar4;
}



int FUN_00094ae0(short param_1,uint param_2,undefined1 param_3,int param_4,undefined1 *param_5)

{
  byte bVar1;
  short sVar2;
  int iVar3;
  int iVar4;
  bool bVar5;
  undefined1 uStack_d;
  
  *param_5 = 0;
  if (param_1 != 0) {
    return 1;
  }
  if ((uint)DAT_0002602a <= (param_2 & 0xff)) {
    return 1;
  }
  iVar4 = (param_2 & 0xff) * 8;
  iVar3 = 0;
  if ((*((char *)camry_host_ptr((uint32_t)(*(int *)(DAT_00026020 + iVar4) + 0xe)))) != '\0') {
    iVar3 = (int)(uint)(*((ushort *)camry_host_ptr((uint32_t)(DAT_00026020 + iVar4 + 4)))) >> 3;
  }
  sVar2 = (*((short *)camry_host_ptr((uint32_t)(*(int *)(DAT_00026020 + iVar4) + 10))));
  bVar1 = (*((byte *)camry_host_ptr((uint32_t)(*(int *)(DAT_00026020 + iVar4) + 0xf))));
  if (bVar1 == 0) {
    return 1;
  }
  if (bVar1 != 1) {
    if (bVar1 < 3) {
LAB_00094b76:
      if (sVar2 != 0) {
        return 1;
      }
      iVar4 = (*(int (*)())camry_indirect((uint32_t)(DAT_00026000)))(param_3,iVar3 + param_4,&uStack_d);
      if (((iVar4 != 0) && (iVar4 != 1)) && (iVar4 != 10)) {
        return 1;
      }
      *param_5 = uStack_d;
      return iVar4;
    }
    if (bVar1 != 3) {
      if (bVar1 == 4) goto LAB_00094b76;
      if (bVar1 != 6 && bVar1 != 7) {
        return 1;
      }
      if (sVar2 != 0) {
        return 1;
      }
      iVar4 = (*(int (*)())camry_indirect((uint32_t)(DAT_00025ff8)))(iVar3 + param_4);
      bVar5 = iVar4 == 0;
      goto LAB_00094b70;
    }
  }
  if (sVar2 != 0) {
    return 1;
  }
  iVar4 = (*(int (*)())camry_indirect((uint32_t)(DAT_00025ffc)))(param_3,iVar3 + param_4);
  if (iVar4 == 0) {
    return 0;
  }
  bVar5 = iVar4 == 10;
LAB_00094b70:
  if (bVar5) {
    return iVar4;
  }
  return 1;
}



undefined4 FUN_00094d9c(ushort param_1,undefined2 *param_2)

{
  uint uVar1;
  undefined4 uVar2;
  uint uVar3;
  uint uVar4;
  
  uVar2 = 1;
  if (DAT_00026018 != '\0') {
    uVar4 = 0;
    if (param_1 < DAT_00025fec) {
      return uVar2;
    }
    if (DAT_00025fec != param_1) {
      uVar3 = (uint)(byte)(DAT_00026018 - 1);
      if (DAT_00025fec < param_1) {
        return uVar2;
      }
      do {
        if (uVar3 <= uVar4) {
          return uVar2;
        }
        uVar1 = (int)(uVar4 + uVar3) >> 1;
        if (DAT_00025fec < param_1) {
          uVar4 = uVar1 + 1 & 0xff;
          uVar1 = uVar3;
        }
        uVar3 = uVar1;
      } while (DAT_00025fec != param_1);
    }
    *param_2 = (short)uVar4;
    uVar2 = 0;
  }
  return uVar2;
}



undefined4 FUN_00094df6(short param_1,int param_2,int param_3)

{
  uint32_t puVar1;
  int extraout_r7;
  int iVar2;
  uint uVar3;
  byte bVar4;
  byte bStack_1b;
  undefined2 uStack_1a;
  undefined1 auStack_18 [3];
  byte bStack_15;
  
  puVar1 = 0x23dfcu;
  uVar3 = 0;
  if ((((param_1 == 0) && (iVar2 = FUN_00094d9c(DAT_00026028,&uStack_1a), iVar2 == 0)) &&
      (iVar2 = FUN_00095514(uStack_1a, ((undefined1 *)camry_host_ptr((uint32_t)(extraout_r7 + -1)))), iVar2 == 0)) &&
     ((uint)bStack_1b + param_2 <= (uint)(*((byte *)camry_host_ptr((uint32_t)(*(int *)(puVar1 + 0x2220) + 0xc)))))) {
    for (bVar4 = 0; bVar4 < bStack_1b; bVar4 = bVar4 + 1) {
      iVar2 = ((void)(auStack_18), FUN_0009552a(uStack_1a, bVar4));
      if (iVar2 != 0) {
        return 1;
      }
      uVar3 = uVar3 + bStack_15 & 0xffff;
    }
    if (uVar3 + param_3 == 0) {
      return 0;
    }
  }
  return 1;
}



undefined4 FUN_00094e6a(undefined2 param_1,int param_2,uint param_3)

{
  int iVar1;
  undefined4 uVar2;
  uint uVar3;
  byte bStack_19;
  undefined2 uStack_18;
  undefined1 uStack_16;
  undefined1 uStack_15;
  
  iVar1 = FUN_00095514(param_1,&bStack_19);
  uVar3 = 0;
  if (iVar1 == 0) {
    for (; uVar3 < (param_3 & 0xff); uVar3 = uVar3 + 1 & 0xff) {
      iVar1 = uVar3 * 4;
      uStack_18 = CONCAT11((*((undefined1 *)camry_host_ptr((uint32_t)(iVar1 + 2 + param_2)))),(*((undefined1 *)camry_host_ptr((uint32_t)(iVar1 + 3 + param_2))))
                          );
      uStack_16 = (*((undefined1 *)camry_host_ptr((uint32_t)(iVar1 + param_2 + 4))));
      uStack_15 = (*((undefined1 *)camry_host_ptr((uint32_t)(iVar1 + param_2 + 5))));
      iVar1 = ((void)(&uStack_18), FUN_00095474(param_1, bStack_19 + uVar3 & 0xff));
      if (iVar1 != 0) goto LAB_00094e86;
    }
    uVar2 = FUN_000954dc(param_1,(param_3 & 0xff) + (uint)bStack_19 & 0xff);
  }
  else {
LAB_00094e86:
    uVar2 = 1;
  }
  return uVar2;
}



undefined4 FUN_00094ee6(char param_1,undefined1 *param_2,char param_3)

{
  uint32_t puVar1;
  int iVar2;
  undefined4 uVar3;
  short sStack_e;
  
  puVar1 = 0x23dfcu;
  if (param_1 == '\x01') {
    if ((((param_3 == '\0') || ((uintptr_t)(param_2)==(uintptr_t)((undefined1 *)0x0))) ||
        (iVar2 = FUN_00094d9c(CONCAT11(*param_2,param_2[1]),&sStack_e), iVar2 != 0)) ||
       ((sStack_e != 0 || ((*((int *)camry_host_ptr((uint32_t)(puVar1 + 0x21ec)))) == 0)))) {
      uVar3 = 1;
    }
    else {
      uVar3 = FUN_00094e6a(0, camry_host_addr(param_2), param_3);
    }
  }
  else {
    uVar3 = 0;
  }
  return uVar3;
}



undefined4 FUN_00094f3a(undefined2 param_1)

{
  int iVar1;
  undefined4 uVar2;
  undefined2 uStack_a;
  
  uVar2 = 1;
  iVar1 = FUN_00094d9c(param_1,&uStack_a);
  if (iVar1 == 0) {
    uVar2 = FUN_000954ee(uStack_a);
  }
  return uVar2;
}



/* Far-call trampoline: prepare {lp},0 / jarl 0x95500 / dispose 0,{lp},lp; byte-verified against the
   exact image. Forwards with registers and stack unchanged; marked as a thunk. Forwarding shape
   machine-verified; target semantics not recovered. */

undefined4 thunk_FUN_00095500(void)

{
  return FUN_00095500();
}



undefined4 FUN_00094f6a(undefined2 param_1,undefined1 *param_2,undefined4 param_3)

{
  undefined2 *extraout_r8;
  int iVar1;
  undefined4 uVar2;
  
  *param_2 = 0;
  uVar2 = 1;
  iVar1 = FUN_00094d9c(param_1, ((undefined2 *)camry_host_ptr((uint32_t)(param_3))));
  if (iVar1 == 0) {
    uVar2 = FUN_00095514(*extraout_r8,param_2);
  }
  return uVar2;
}



undefined4 FUN_00094f94(char param_1,int *param_2,undefined2 param_3,undefined1 *param_4)

{
  int iVar1;
  undefined4 uVar2;
  
  *param_4 = 0;
  if ((uintptr_t)(param_2)==(uintptr_t)((int *)0x0)) {
    return 1;
  }
  if (param_1 == '\0') {
    iVar1 = *param_2;
  }
  else {
    if (param_1 == '\x10') {
      if (param_2[1] == 0) {
        return 1;
      }
      if (*(int *)param_2[1] == 0) {
        return 0;
      }
      uVar2 = (*(int (*)())*(code **)param_2[1])(param_3,param_4);
      return uVar2;
    }
    if (param_1 != ' ') {
      return 1;
    }
    iVar1 = param_2[2];
  }
  if (iVar1 != 0) {
    return 0;
  }
  return 1;
}



undefined4 FUN_00094fea(ushort param_1,char param_2,undefined2 param_3,undefined1 *param_4)

{
  void *pvVar1;
  undefined4 uVar2;
  
  *param_4 = 0;
  if ((param_2 == '\x10') || (param_2 == ' ')) {
    if (5 < param_1) {
      return 1;
    }
    pvVar1 = ((void *)camry_host_ptr((uint32_t)(f33_dcm_did_class[(short)param_1].policy)));
  }
  else {
    pvVar1 = ((void *)camry_host_ptr((uint32_t)(DAT_0002601c)));
    if (param_1 != 0) {
      return 1;
    }
  }
  uVar2 = FUN_00094f94(param_2,pvVar1,param_3, param_4);
  return uVar2;
}



int FUN_0009502a(undefined2 param_1,undefined1 param_2,undefined1 *param_3)

{
  undefined8 uVar1;
  int iVar2;
  uint uVar3;
  byte bVar4;
  byte bStack_1d;
  uchar uStack_1c;
  undefined1 uStack_1b;
  ushort uStack_1a;
  ushort auStack_18 [2];
  
  uVar1 = 0x23dfc00000000;
  *param_3 = 0;
  uStack_1b = 0;
  iVar2 = FUN_00095514(param_1,&bStack_1d);
  if ((iVar2 == 0) && (bStack_1d != 0)) {
    for (bVar4 = 0; iVar2 = 0, bVar4 < bStack_1d; bVar4 = bVar4 + 1) {
      iVar2 = ((void)(auStack_18), FUN_0009552a(param_1, bVar4));
      if ((iVar2 != 0) ||
         (uVar3 = f33_dcm_resolve_did_group(auStack_18[0],'\x01',&uStack_1a,&uStack_1c), uVar3 != 0)
         ) goto LAB_000950ba;
      iVar2 = FUN_00094f94(param_2, ((int *)camry_host_ptr((uint32_t)((*((undefined4 *)camry_host_ptr((uint32_t)(0x2250u +
                                    (short)uStack_1a * 0x1c + (int)((ulonglong)uVar1 >> 0x20)))))))), 
                           auStack_18[0], &uStack_1b);
      if (iVar2 != 0) {
        if (iVar2 != 1) {
          return iVar2;
        }
        *param_3 = uStack_1b;
        return 1;
      }
    }
  }
  else {
LAB_000950ba:
    iVar2 = 1;
  }
  return iVar2;
}



int FUN_000950c0(short param_1,undefined1 param_2,undefined1 *param_3)

{
  ushort uVar1;
  char cVar2;
  uint32_t puVar3;
  uint uVar4;
  int iVar5;
  uchar uStack_1c;
  undefined1 uStack_1b;
  ushort uStack_1a;
  
  puVar3 = 0x23dfcu;
  *param_3 = 0;
  cVar2 = DAT_00026019;
  uVar1 = DAT_00025fec;
  if ((param_1 != 0) ||
     (uVar4 = f33_dcm_resolve_did_group(DAT_00025fec,'\0',&uStack_1a,&uStack_1c), uVar4 != 0)) {
    return 1;
  }
  iVar5 = FUN_00094f94(param_2, ((int *)camry_host_ptr((uint32_t)((*((undefined4 *)camry_host_ptr((uint32_t)(puVar3 + 0x2220))))))), uVar1, &uStack_1b);
  if (iVar5 != 0) {
    if (iVar5 != 1) {
      return iVar5;
    }
    *param_3 = uStack_1b;
    return 1;
  }
  if (cVar2 != '\x01') {
    return 0;
  }
  iVar5 = FUN_0009502a(0,param_2,param_3);
  return iVar5;
}



undefined4 FUN_0009512c(void)

{
  DAT_febe5d20 = 0;
  DAT_febe5d21 = 0;
  return FUN_00095500();
}



undefined4 FUN_000951b8(ushort param_1,byte param_2,undefined4 param_3)

{
  uint uVar1;
  
  if (param_2 < 2) {
    uVar1 = f33_dcm_probe_did_metadata(param_1);
    (*((bool *)camry_host_ptr((uint32_t)(param_3)))) = uVar1 != 0;
  }
  return 0;
}



undefined4 FUN_000951da(ushort param_1,byte param_2,undefined4 param_3)

{
  uint uVar1;
  
  if (param_2 < 2) {
    uVar1 = f33_dcm_probe_did_metadata(param_1);
    (*((bool *)camry_host_ptr((uint32_t)(param_3)))) = uVar1 != 0;
  }
  return 0;
}



undefined4 FUN_000951fc(ushort param_1,byte param_2,undefined4 param_3)

{
  uint uVar1;
  
  if (param_2 < 2) {
    uVar1 = f33_dcm_probe_did_metadata(param_1);
    (*((bool *)camry_host_ptr((uint32_t)(param_3)))) = uVar1 != 0;
  }
  return 0;
}



undefined4 FUN_0009521e(ushort param_1,byte param_2,undefined4 param_3)

{
  uint uVar1;
  
  if (param_2 < 2) {
    uVar1 = f33_dcm_probe_did_metadata(param_1);
    (*((bool *)camry_host_ptr((uint32_t)(param_3)))) = uVar1 != 0;
  }
  return 0;
}



undefined4 FUN_00095240(ushort param_1,byte param_2,undefined4 param_3)

{
  uint uVar1;
  
  if (param_2 < 2) {
    uVar1 = f33_dcm_probe_did_metadata(param_1);
    (*((bool *)camry_host_ptr((uint32_t)(param_3)))) = uVar1 != 0;
  }
  return 0;
}



undefined4 FUN_00095262(undefined4 param_1,byte param_2,ushort *param_3)

{
  if (param_2 < 2) {
    f33_dcm_selected_did_payload_length(param_3);
  }
  return 0;
}



undefined4 FUN_00095278(undefined4 param_1,byte param_2,ushort *param_3)

{
  if (param_2 < 2) {
    f33_dcm_selected_did_payload_length(param_3);
  }
  return 0;
}



undefined4 FUN_0009528e(undefined4 param_1,byte param_2,ushort *param_3)

{
  if (param_2 < 2) {
    f33_dcm_selected_did_payload_length(param_3);
  }
  return 0;
}



undefined4 FUN_000952a4(undefined4 param_1,byte param_2,ushort *param_3)

{
  if (param_2 < 2) {
    f33_dcm_selected_did_payload_length(param_3);
  }
  return 0;
}



undefined4 FUN_000952ba(undefined4 param_1,byte param_2,ushort *param_3)

{
  if (param_2 < 2) {
    f33_dcm_selected_did_payload_length(param_3);
  }
  return 0;
}



uint FUN_000952d0(ushort param_1,uchar *param_2,byte param_3,ushort *param_4,uchar *param_5)

{
  uint uVar1;
  
  if (param_3 < 2) {
    uVar1 = f33_did_read_application_adapter(param_2,param_4,param_5,param_1);
  }
  else {
    uVar1 = 0;
    if (param_3 == 2) {
      thunk_FUN_0008b3d4();
    }
  }
  return uVar1;
}



uint FUN_00095300(ushort param_1,uchar *param_2,byte param_3,ushort *param_4,uchar *param_5)

{
  uint uVar1;
  
  if (param_3 < 2) {
    uVar1 = f33_did_read_application_adapter(param_2,param_4,param_5,param_1);
  }
  else {
    uVar1 = 0;
    if (param_3 == 2) {
      thunk_FUN_0008b3d4();
    }
  }
  return uVar1;
}



uint FUN_00095330(ushort param_1,uchar *param_2,byte param_3,ushort *param_4,uchar *param_5)

{
  uint uVar1;
  
  if (param_3 < 2) {
    uVar1 = f33_did_read_application_adapter(param_2,param_4,param_5,param_1);
  }
  else {
    uVar1 = 0;
    if (param_3 == 2) {
      thunk_FUN_0008b3d4();
    }
  }
  return uVar1;
}



uint FUN_00095360(ushort param_1,uchar *param_2,byte param_3,ushort *param_4,uchar *param_5)

{
  uint uVar1;
  
  if (param_3 < 2) {
    uVar1 = f33_did_read_application_adapter(param_2,param_4,param_5,param_1);
  }
  else {
    uVar1 = 0;
    if (param_3 == 2) {
      thunk_FUN_0008b3d4();
    }
  }
  return uVar1;
}



uint FUN_00095390(ushort param_1,uchar *param_2,byte param_3,ushort *param_4,uchar *param_5)

{
  uint uVar1;
  
  if (param_3 < 2) {
    uVar1 = f33_did_read_application_adapter(param_2,param_4,param_5,param_1);
  }
  else {
    uVar1 = 0;
    if (param_3 == 2) {
      thunk_FUN_0008b3d4();
    }
  }
  return uVar1;
}



uint FUN_000953c0(ushort param_1,uchar *param_2,byte param_3,ushort param_4,uchar *param_5)

{
  uint uVar1;
  
  if (param_3 < 2) {
    uVar1 = f33_write_did_request_adapter(param_1,param_2,param_4,param_5);
  }
  else {
    uVar1 = 0;
    if (param_3 == 2) {
      FUN_0008b3e8();
    }
  }
  return uVar1;
}



uint FUN_000953ec(ushort param_1,uchar *param_2,byte param_3,ushort param_4,uchar *param_5)

{
  uint uVar1;
  
  if (param_3 < 2) {
    uVar1 = f33_write_did_request_adapter(param_1,param_2,param_4,param_5);
  }
  else {
    uVar1 = 0;
    if (param_3 == 2) {
      FUN_0008b3e8();
    }
  }
  return uVar1;
}



undefined4 FUN_00095418(ushort param_1,undefined2 *param_2)

{
  uint uVar1;
  undefined4 uVar2;
  uint uVar3;
  uint uVar4;
  
  uVar2 = 1;
  if (DAT_00026014 != 0) {
    uVar4 = 0;
    if (param_1 < DAT_00026028) {
      return uVar2;
    }
    if (DAT_00026028 != param_1) {
      uVar3 = (uint)(ushort)(DAT_00026014 - 1);
      if (DAT_00026028 < param_1) {
        return uVar2;
      }
      do {
        if (uVar3 <= uVar4) {
          return uVar2;
        }
        uVar1 = (int)(uVar4 + uVar3) >> 1;
        if (DAT_00026028 < param_1) {
          uVar4 = uVar1 + 1 & 0xffff;
          uVar1 = uVar3;
        }
        uVar3 = uVar1;
      } while (DAT_00026028 != param_1);
    }
    *param_2 = (short)uVar4;
    uVar2 = 0;
  }
  return uVar2;
}



undefined4 FUN_00095474(short param_1,uint param_2)

{
  uint32_t puVar1;
  undefined2 *extraout_r8;
  int iVar2;
  undefined4 uVar3;
  short asStack_12 [3];
  
  puVar1 = 0x23dfcu;
  uVar3 = 1;
  if ((((param_1 == 0) && (DAT_00025fe8 != 0)) &&
      (iVar2 = FUN_00095418(DAT_00025fec,asStack_12), iVar2 == 0)) &&
     ((asStack_12[0] == 0 && ((param_2 & 0xff) < (uint)(*((byte *)camry_host_ptr((uint32_t)(*(int *)(puVar1 + 0x2220) + 0xc)))))))
     ) {
    iVar2 = (param_2 & 0xff) * 4;
    (*((undefined2 *)camry_host_ptr((uint32_t)(*(int *)(puVar1 + 0x21ec) + iVar2)))) = *extraout_r8;
    (*((undefined1 *)camry_host_ptr((uint32_t)(*(int *)(puVar1 + 0x21ec) + iVar2 + 2)))) = *(undefined1 *)(extraout_r8 + 1);
    (*((undefined1 *)camry_host_ptr((uint32_t)(iVar2 + *(int *)(puVar1 + 0x21ec) + 3)))) = (*((undefined1 *)camry_host_ptr((uint32_t)((int)camry_host_addr(extraout_r8) + 3))));
    uVar3 = 0;
  }
  return uVar3;
}



bool FUN_000954dc(short param_1,undefined1 param_2)

{
  if (param_1 == 0) {
    DAT_febe5d23 = param_2;
  }
  return param_1 != 0;
}



bool FUN_000954ee(short param_1)

{
  if (param_1 == 0) {
    DAT_febe5d23 = 0;
  }
  return param_1 != 0;
}



undefined4 FUN_00095500(void)

{
  uint uVar1;
  
  for (uVar1 = (uint)DAT_00026018; uVar1 != 0; uVar1 = uVar1 - 1) {
    DAT_febe5d23 = 0;
  }
  return 0;
}



bool FUN_00095514(short param_1,undefined1 *param_2)

{
  if (param_1 == 0) {
    *param_2 = DAT_febe5d23;
  }
  return param_1 != 0;
}



undefined4 FUN_0009552a(short param_1,uint param_2)

{
  uint32_t puVar1;
  undefined2 *extraout_r8;
  int iVar2;
  undefined4 uVar3;
  int iVar4;
  short asStack_12 [3];
  
  puVar1 = 0x23dfcu;
  uVar3 = 1;
  if ((((param_1 == 0) && (DAT_00025fe8 != 0)) &&
      (iVar2 = FUN_00095418(DAT_00025fec,asStack_12), iVar2 == 0)) &&
     ((asStack_12[0] == 0 && ((param_2 & 0xff) < (uint)(*((byte *)camry_host_ptr((uint32_t)(*(int *)(puVar1 + 0x2220) + 0xc)))))))
     ) {
    iVar2 = (param_2 & 0xff) * 4;
    iVar4 = (*((int *)camry_host_ptr((uint32_t)(puVar1 + 0x21ec))));
    *extraout_r8 = (*((undefined2 *)camry_host_ptr((uint32_t)(*(int *)(puVar1 + 0x21ec) + iVar2))));
    *(undefined1 *)(extraout_r8 + 1) = (*((undefined1 *)camry_host_ptr((uint32_t)(iVar4 + iVar2 + 2))));
    (*((undefined1 *)camry_host_ptr((uint32_t)((int)camry_host_addr(extraout_r8) + 3)))) = (*((undefined1 *)camry_host_ptr((uint32_t)(iVar2 + *(int *)(puVar1 + 0x21ec) + 3))));
    uVar3 = 0;
  }
  return uVar3;
}



void FUN_00095590(void)

{
  int iVar1;
  int iVar2;
  uint32_t puVar3;
  int iVar4;
  
  puVar3 = 0x23dfcu;
  f33_app_dcm_callback_pending = '\0';
  DAT_febe5d24 = 0;
  iVar4 = 0;
  do {
    (*(int (*)())camry_indirect((uint32_t)(((code *)(uintptr_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(puVar3 + iVar4 * 4 + 0x2300))))))))();
    iVar2 = iVar4 + 1;
    iVar1 = iVar4 + -3;
    iVar4 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  return;
}



void FUN_000955b6(uchar param_1)

{
  f33_app_dcm_callback_pending = param_1;
  return;
}



uchar FUN_000955bc(void)

{
  return f33_app_dcm_callback_pending;
}



void FUN_000955c2(char param_1,undefined1 param_2)

{
  if ((param_1 != '\0') && (param_1 == DAT_000260ec)) {
    (*(int (*)())camry_indirect((uint32_t)(PTR_FUN_000260f0)))(param_2);
  }
  return;
}



int FUN_000955e4(void)

{
  int iVar1;
  
  if (DAT_febe5d24 == -0x5a5a5a5b) {
    iVar1 = 0;
  }
  else {
    iVar1 = (*(int (*)())camry_indirect((uint32_t)(PTR_f33_return_const_1_968de_000260e4)))();
    if (iVar1 == 1) {
      iVar1 = f33_return_const_1_95622();
    }
  }
  return iVar1;
}



void FUN_0009560e(char param_1)

{
  if (param_1 == '\x01') {
    DAT_febe5d24 = 0;
  }
  else {
    DAT_febe5d24 = 0xa5a5a5a5;
  }
  return;
}



/* Constant source: return 1; shape-classified from the canonical corpus. Callers receive this
   literal directly; its meaning is not recovered. */

undefined4 f33_return_const_1_95622(void)

{
  return 1;
}



/* Stage NRC;78 leaves service pending and does not finalize message. Other NRCs complete
   through9126A/disposition queue. */

void f33_dcm_report_negative_or_pending(F33DcmMessageContext *message,uchar nrc)

{
  f33_dcm_stage_negative_response(message,nrc);
  if (nrc != 'x') {
    f33_dcm_complete_service_response(message);
  }
  return;
}



/* Forward handler-retained body length/routing through9126A. This is response readiness, not
   delivery. */

void f33_dcm_report_positive_response(F33DcmMessageContext *message)

{
  f33_dcm_complete_service_response(message);
  return;
}



void FUN_00095650(char param_1,undefined2 param_2,undefined1 param_3)

{
  if (param_1 == DAT_00026114) {
    (*(int (*)())camry_indirect((uint32_t)(PTR_FUN_00026110)))(param_1,param_2,param_3);
  }
  FUN_0009560e(1);
  return;
}



undefined4 FUN_00095674(undefined1 param_1)

{
  int iVar1;
  uint32_t puVar2;
  uint32_t puVar3;
  int iVar4;
  undefined4 uVar5;
  uchar uStack_11;
  
  puVar2 = 0xfebeb800u;
  puVar3 = 0x23dfcu;
  uVar5 = 0;
  iVar1 = DAT_febe5d30 + 2;
  iVar4 = FUN_00094786(DAT_febe5d2c, DAT_febe5d2e, ((uchar *)camry_host_ptr((uint32_t)(iVar1))), param_1, DAT_febe5d34 - 2U & 0xffff, &uStack_11
                      );
  if (iVar4 == 0) {
    FUN_000955b6(0);
    if (((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(0x2cf5))))) == '\x01') && ((*((short *)camry_host_ptr((uint32_t)(puVar3 + 0x2cf6)))) == (*((short *)camry_host_ptr((uint32_t)(puVar2 + -0x5ad2))))))
    {
      ((void)(iVar1), f33_return_only_stub_98900());
    }
    if (1 < (*((uint *)camry_host_ptr((uint32_t)(puVar2 + -0x5abc))))) {
      **(undefined1 **)(puVar2 + -0x5ac8) = **(undefined1 **)(puVar2 + -0x5ad0);
      (*((undefined1 *)camry_host_ptr((uint32_t)(*(int *)(puVar2 + -0x5ac8) + 1)))) =
           (*((undefined1 *)camry_host_ptr((uint32_t)(*(int *)(puVar2 + -0x5ad0) + 1))));
      (*((undefined4 *)camry_host_ptr((uint32_t)(puVar2 + -0x5ac4)))) = 2;
      f33_dcm_report_positive_response(((F33DcmMessageContext *)camry_host_ptr((uint32_t)(puVar2 + -0x5ad0))));
    }
  }
  else if (iVar4 == 10) {
    FUN_000955b6(1);
    f33_dcm_enqueue_event('\x13');
    uVar5 = 10;
  }
  else {
    FUN_000955b6(0);
    if ((iVar4 == 1) && (uStack_11 != '\0')) {
      f33_dcm_report_negative_or_pending(((F33DcmMessageContext *)camry_host_ptr((uint32_t)(puVar2 + -0x5ad0))),uStack_11);
    }
  }
  return uVar5;
}



undefined4 FUN_00095734(undefined1 param_1)

{
  uint32_t puVar1;
  uchar nrc;
  int iVar2;
  undefined4 uVar3;
  uchar uStack_b;
  ushort uStack_a;
  
  puVar1 = 0xfebeb800u;
  uVar3 = 0;
  iVar2 = FUN_0009449e(DAT_febe5d2c,DAT_febe5d2e,param_1,&uStack_a);
  if (iVar2 == 0) {
    FUN_000955b6(0);
    if ((uint)uStack_a == (*((int *)camry_host_ptr((uint32_t)(puVar1 + -0x5acc)))) - 2U) {
      f33_dcm_get_security_level(&uStack_b);
      iVar2 = FUN_000943ce((*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x5ad4)))),1,0x22,uStack_b);
      if (iVar2 == 0) {
        uVar3 = FUN_00095674(0);
        return uVar3;
      }
      nrc = '3';
    }
    else {
      nrc = '\x13';
    }
    f33_dcm_report_negative_or_pending(((F33DcmMessageContext *)camry_host_ptr((uint32_t)(puVar1 + -0x5ad0))),nrc);
  }
  else if (iVar2 == 10) {
    FUN_000955b6(1);
    f33_dcm_enqueue_event('\x12');
    uVar3 = 10;
  }
  else {
    FUN_000955b6(0);
  }
  return uVar3;
}



undefined4 FUN_000957c8(void)

{
  uint32_t puVar1;
  int iVar2;
  undefined4 uVar3;
  uchar uStack_9;
  
  puVar1 = 0xfebeb800u;
  f33_dcm_get_session(&uStack_9);
  iVar2 = FUN_000943ce((*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x5ad4)))),1,0x21,uStack_9);
  if (iVar2 == 0) {
    uVar3 = FUN_00095734(0);
  }
  else {
    uVar3 = 0;
    f33_dcm_report_negative_or_pending(((F33DcmMessageContext *)camry_host_ptr((uint32_t)(puVar1 + -0x5ad0))),'1');
  }
  return uVar3;
}



undefined4 FUN_00095808(undefined1 param_1)

{
  uint32_t puVar1;
  int iVar2;
  undefined4 uVar3;
  char cStack_9;
  
  puVar1 = 0xfebeb800u;
  uVar3 = 0;
  iVar2 = FUN_0009445a(DAT_febe5d2c,DAT_febe5d2e,param_1,&cStack_9);
  if (iVar2 == 0) {
    FUN_000955b6(0);
    if (cStack_9 == '\0') {
      uVar3 = FUN_000957c8();
    }
    else {
      f33_dcm_report_negative_or_pending(((F33DcmMessageContext *)camry_host_ptr((uint32_t)(puVar1 + -0x5ad0))),'1');
    }
  }
  else if (iVar2 == 10) {
    FUN_000955b6(1);
    f33_dcm_enqueue_event('\x11');
    uVar3 = 10;
  }
  else {
    FUN_000955b6(0);
  }
  return uVar3;
}



undefined4 FUN_0009586c(undefined4 *param_1)

{
  undefined4 *puVar1;
  uint32_t puVar2;
  ushort did;
  uchar nrc;
  uint uVar3;
  undefined4 uVar4;
  undefined4 *puVar5;
  byte bStack_d;
  
  puVar2 = 0xfebeb800u;
  FUN_0009560e(0);
  puVar1 = ((undefined4 *)camry_host_ptr((uint32_t)(puVar2 + -0x5ad0)));
  puVar5 = param_1 + 7;
  do {
    uVar4 = *param_1;
    param_1 = param_1 + 1;
    *puVar1 = uVar4;
    puVar1 = puVar1 + 1;
  } while ((uintptr_t)(puVar5)!=(uintptr_t)(param_1));
  FUN_000955b6(0);
  if ((*((uint *)camry_host_ptr((uint32_t)(puVar2 + -0x5acc)))) < 3) {
    nrc = '\x13';
  }
  else {
    did = CONCAT11(**(undefined1 **)(puVar2 + -0x5ad0),(*(undefined1 **)(puVar2 + -0x5ad0))[1]);
    (*((ushort *)camry_host_ptr((uint32_t)(puVar2 + -0x5ad2)))) = did;
    uVar3 = f33_dcm_resolve_did_group(did,'\x01',((ushort *)camry_host_ptr((uint32_t)(puVar2 + -0x5ad4))),&bStack_d);
    if (uVar3 == 0) {
      if ((bStack_d >> 2 & 1) != 0) {
        uVar4 = FUN_00095808(0);
        return uVar4;
      }
    }
    else if (uVar3 != 1) {
      return 0;
    }
    nrc = '1';
  }
  f33_dcm_report_negative_or_pending(((F33DcmMessageContext *)camry_host_ptr((uint32_t)(puVar2 + -0x5ad0))),nrc);
  return 0;
}



/* 0 starts9586C,2 cancels958F4; all paths meaningful r10. */

uint f33_dcm_write_did_service(uchar operation,F33DcmMessageContext *message)

{
  uint uVar1;
  
  if (operation == '\0') {
    uVar1 = FUN_0009586c(message);
  }
  else {
    uVar1 = 0;
    if (operation == '\x02') {
      uVar1 = FUN_000958f4(((undefined *)camry_host_ptr(0xfebe5d30u)));
    }
  }
  return uVar1;
}



undefined4 FUN_0009599c(void)

{
  return FUN_00095808(1);
}



undefined4 FUN_000959aa(void)

{
  return FUN_00095734(1);
}



undefined4 FUN_000959b8(void)

{
  return FUN_00095674(1);
}



void FUN_00095a06(void)

{
  FUN_0009560e(1);
  return;
}



uint FUN_00095a14(char param_1,F33DcmMessageContext *param_2)

{
  uint uVar1;
  
  if (param_1 == '\0') {
    uVar1 = f33_dcm_tester_present_request(param_2);
  }
  else {
    uVar1 = 0;
    if (param_1 == '\x02') {
      FUN_00095a06();
    }
  }
  return uVar1;
}



/* For selected non-immediate row and state1/2 clear localstate/reset8B134 through95D4E(0).
   Invalidate event0E and release5D24. Does not revoke request9, clear81AE, publishdefault, or prove
   cancellation of already admitted mode/hardware action. */

void f33_dcm_session_cancel(void)

{
  if (((f33_app_dcm_session_row_index < 4) &&
      (f33_app_session_timing_rows[(short)(ushort)f33_app_dcm_session_row_index].transition_kind !=
       '\0')) &&
     (f33_app_dcm_session_deferred_state == '\x01' || f33_app_dcm_session_deferred_state == '\x02'))
  {
    f33_app_dcm_session_deferred_state = '\0';
    FUN_00095d4e(0);
  }
  f33_dcm_invalidate_queued_event('\x0e','\0');
  FUN_0009560e(1);
  return;
}



/* Only state1 constructs eight-byte record5D4C using current logical transport config and
   target/suppression.8B334 returns10 on successful mode9 request; state2/event0E/78 retained.
   State3\u21924 calls95D4E(6), an exact no-op. No app session2 store or successful handoff follows
   this callback. State3→4 calls95D4E(6), an exact no-op. */

uint f33_dcm_programming_pending_response_join(uchar target)

{
  ushort uVar1;
  undefined2 uVar2;
  undefined1 uVar3;
  undefined *puVar4;
  uint32_t puVar5;
  uint32_t puVar6;
  uint uVar7;
  int iVar8;
  uint uVar9;
  uchar nrc;
  
  puVar4 = ((undefined *)camry_host_ptr(0xfebeb800u));
  puVar5 = 0xfebeb800u;
  puVar6 = 0x23dfcu;
  uVar9 = 0;
  if (f33_app_dcm_session_deferred_state == '\x01') {
    uVar7 = thunk_FUN_00093c60();
    if (2 < uVar7) {
      return 0;
    }
    uVar1 = (*((ushort *)camry_host_ptr((uint32_t)(puVar6 + (short)uVar7 * 0xc + 0x20ec))));
    if (1 < uVar1) {
      return 0;
    }
    uVar2 = **(undefined2 **)
              ((uint)(*((ushort *)camry_host_ptr((uint32_t)((int)(puVar6 + (short)uVar7 * 0xc + 0x20ec) + 2)))) * 4 +
              (*((int *)camry_host_ptr((uint32_t)(puVar6 + (short)uVar1 * 0x14 + 0x20c4)))));
    uVar3 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)((short)uVar1 * 0x14 + 0x20d4)))));
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x5ab0))))) = target;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x5aae))))) = 0;
    (*((undefined2 *)camry_host_ptr((uint32_t)(puVar5 + -0x5ab4)))) = uVar2;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x5ab2))))) = uVar3;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x5ab1))))) = 0x10;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x5aaf))))) = target == '\x02';
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x5aad))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x5a97))))) != '\x01';
    iVar8 = ((void)(((undefined *)camry_host_ptr((uint32_t)(puVar5 + -0x5ab4)))), FUN_00095cf2());
    puVar4 = ((undefined *)camry_host_ptr((uint32_t)(puVar5)));
    if (iVar8 == 0) {
LAB_00095c40:
      puVar4[-0x5aab] = 4;
      FUN_00095d4e(6);
      return 0;
    }
    if (iVar8 == 1) {
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x5aab))))) = 0;
      FUN_00095d4e(0);
      nrc = '\"';
      puVar4 = ((undefined *)camry_host_ptr((uint32_t)(puVar5)));
    }
    else {
      if (iVar8 != 10) {
        return 0;
      }
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x5aab))))) = 2;
      nrc = 'x';
      f33_dcm_enqueue_event('\x0e');
      uVar9 = 10;
      puVar4 = ((undefined *)camry_host_ptr((uint32_t)(puVar5)));
    }
  }
  else {
    if (f33_app_dcm_session_deferred_state != '\x02') {
      if (f33_app_dcm_session_deferred_state != '\x03') {
        return 0;
      }
      goto LAB_00095c40;
    }
    nrc = 'x';
  }
  f33_dcm_report_negative_or_pending((F33DcmMessageContext *)(puVar4 + -0x5aa8),nrc);
  return uVar9;
}



/* Operation0\u219295A3E admission;2\u219295B48 cancellation;3\u219295B88 pending-response
   notification. Other operations no action. Operation0→95A3E admission;2→95B48
   cancellation;3→95B88 pending-response notification. */

uint f33_dcm_session_operation(uchar operation,F33DcmMessageContext *message,uchar target)

{
  uint uVar1;
  
  if (operation == '\0') {
    uVar1 = f33_dcm_session_request(message,target);
  }
  else {
    uVar1 = 0;
    if (operation == '\x02') {
      f33_dcm_session_cancel();
    }
    else if (operation == '\x03') {
      uVar1 = f33_dcm_programming_pending_response_join(target);
    }
  }
  return uVar1;
}



void FUN_00095c86(undefined4 param_1,undefined4 param_2,char param_3)

{
  if (((param_3 == '\0') && (DAT_00026120 == '\x01')) && (f33_app_dcm_session_row_index < 4)) {
    FUN_00091f9c(f33_app_session_timing_rows[(short)(ushort)f33_app_dcm_session_row_index].session);
  }
  return;
}



/* Event0E re-enters8B334 with5D4C. Generic0/1/10 outcomes mapstate3/state0+22/requeue0E. Exact
   wrapper latches pending10 after accepted software request; no timer/transport receipt alone
   proves handoff. */

void f33_dcm_programming_deferred_event(void)

{
  uint32_t puVar1;
  int iVar2;
  
  puVar1 = 0xfebeb800u;
  iVar2 = ((void)((0xfebe5d4cu)), FUN_00095cf2());
  if (iVar2 == 0) {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x5aab))))) = 3;
  }
  else if (iVar2 == 1) {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x5aab))))) = 0;
    FUN_00095d4e(0);
    f33_dcm_report_negative_or_pending(((F33DcmMessageContext *)camry_host_ptr((uint32_t)(puVar1 + -0x5aa8))),'\"');
  }
  else if (iVar2 == 10) {
    f33_dcm_enqueue_event('\x0e');
  }
  return;
}



uint FUN_00095cf2(void)

{
  return f33_app_programming_handoff_pending_join();
}



uint FUN_00095cfe(undefined1 param_1, undefined4 param_2)

{
  return FUN_0008b36e(param_1, ((uchar *)camry_host_ptr((uint32_t)(param_2))));
}



/* Configured SID10 operation callback for target0x01; forwards operation/message plus fixed target
   inr8 to95C52. Callback return is ignored by existing F33DcmServiceCallback dispatcher. No direct
   hardware transition. */

uint f33_dcm_session_1_callback(uchar operation,F33DcmMessageContext *message)

{
  uint uVar1;
  
  uVar1 = f33_dcm_session_operation(operation,message,'\x01');
  return uVar1;
}



/* Configured SID10 operation callback for target0x02; forwards operation/message plus fixed target
   inr8 to95C52. Callback return is ignored by existing F33DcmServiceCallback dispatcher. No direct
   hardware transition. */

uint f33_dcm_session_2_callback(uchar operation,F33DcmMessageContext *message)

{
  uint uVar1;
  
  uVar1 = f33_dcm_session_operation(operation,message,'\x02');
  return uVar1;
}



/* Configured SID10 operation callback for target0x03; forwards operation/message plus fixed target
   inr8 to95C52. Callback return is ignored by existing F33DcmServiceCallback dispatcher. No direct
   hardware transition. */

uint f33_dcm_session_3_callback(uchar operation,F33DcmMessageContext *message)

{
  uint uVar1;
  
  uVar1 = f33_dcm_session_operation(operation,message,'\x03');
  return uVar1;
}



/* Configured SID10 operation callback for target0x40; forwards operation/message plus fixed target
   inr8 to95C52. Callback return is ignored by existing F33DcmServiceCallback dispatcher. No direct
   hardware transition. */

uint f33_dcm_session_64_callback(uchar operation,F33DcmMessageContext *message)

{
  uint uVar1;
  
  uVar1 = f33_dcm_session_operation(operation,message,'@');
  return uVar1;
}



undefined4 FUN_00095d4e(char param_1)

{
  if (param_1 == '\0') {
    thunk_FUN_0008b134();
  }
  return 0;
}



int FUN_00095d60(undefined1 param_1)

{
  uint32_t puVar1;
  int iVar2;
  ushort uStack_a;
  
  puVar1 = 0xfebeb800u;
  if (f33_dcm_read_route_kind == '\x01') {
    iVar2 = FUN_0009449e(f33_dcm_read_selected_class,f33_dcm_read_current_did,param_1,&uStack_a);
  }
  else {
    iVar2 = FUN_000944cc(f33_dcm_read_selected_class,&uStack_a);
  }
  if (iVar2 == 0) {
    FUN_000955b6(0);
    (*((uint *)camry_host_ptr((uint32_t)(puVar1 + -0x5a8c)))) = (*((int *)camry_host_ptr((uint32_t)(puVar1 + -0x5a8c)))) + uStack_a + 2;
  }
  else if ((iVar2 == 1) || (iVar2 != 10)) {
    FUN_000955b6(0);
  }
  else {
    FUN_000955b6(1);
    f33_dcm_enqueue_event('\x1f');
  }
  return iVar2;
}



/* Read current session/security snapshots, apply class policy, then fixed local callback and length
   callback. Session rejection31 and security33 are distinct from metadata absence31 and whole-body
   capacity14. */

uint f33_dcm_check_read_did_policy_and_length(void)

{
  ushort uVar1;
  uint32_t puVar2;
  F33DcmMessageContext *message;
  uchar uVar3;
  int iVar4;
  uint uVar5;
  uchar uStack_13;
  uchar uStack_12;
  uchar uStack_11;
  
  uVar3 = f33_dcm_read_route_kind;
  uVar1 = f33_dcm_read_selected_class;
  puVar2 = 0xfebeb800u;
  uStack_11 = '\0';
  uStack_12 = '\0';
  uStack_13 = '\x01';
  f33_dcm_get_session(&uStack_13);
  iVar4 = FUN_000943ce(uVar1,uVar3,0x11,uStack_13);
  if (iVar4 == 0) {
    f33_dcm_get_security_level(&uStack_12);
    iVar4 = FUN_000943ce(uVar1,uVar3,0x12,uStack_12);
    if (iVar4 == 0) {
      if (uVar3 == '\x01') {
        iVar4 = FUN_00094fea(uVar1,0x10,(*((undefined2 *)camry_host_ptr((uint32_t)(puVar2 + -0x5a84)))),&uStack_11);
      }
      else {
        iVar4 = FUN_000950c0(uVar1,0x10,&uStack_11);
      }
      if (iVar4 == 0) {
        uVar5 = FUN_00095d60(0);
        return uVar5;
      }
      if (iVar4 != 1) {
        return 1;
      }
      if (uStack_11 == '\0') {
        return 1;
      }
      message = ((F33DcmMessageContext *)camry_host_ptr((uint32_t)(puVar2 + -0x5a7c)));
      uVar3 = uStack_11;
    }
    else {
      message = ((F33DcmMessageContext *)camry_host_ptr((uint32_t)(puVar2 + -0x5a7c)));
      uVar3 = '3';
    }
  }
  else {
    message = ((F33DcmMessageContext *)camry_host_ptr((uint32_t)(puVar2 + -0x5a7c)));
    uVar3 = '1';
  }
  f33_dcm_report_negative_or_pending(message,uVar3);
  return 1;
}



uint FUN_00095e76(undefined1 param_1)

{
  uint32_t puVar1;
  int iVar2;
  uint uVar3;
  char cStack_9;
  
  puVar1 = 0xfebeb800u;
  uVar3 = 1;
  cStack_9 = '\x01';
  iVar2 = FUN_0009445a(f33_dcm_read_selected_class,f33_dcm_read_current_did,param_1,&cStack_9);
  if (iVar2 == 0) {
    FUN_000955b6(0);
    if (cStack_9 == '\0') {
      uVar3 = f33_dcm_check_read_did_policy_and_length();
    }
    else {
      f33_dcm_report_negative_or_pending(((F33DcmMessageContext *)camry_host_ptr((uint32_t)(puVar1 + -0x5a7c))),'1');
    }
  }
  else if (iVar2 == 10) {
    FUN_000955b6(1);
    f33_dcm_enqueue_event('\x04');
    uVar3 = 10;
  }
  else {
    FUN_000955b6(0);
  }
  return uVar3;
}



/* Dynamic DID bank count0 selects static class ranges. Require read capability; retain class
   index5D78 and route kind5D7A. Class membership alone does not prove available metadata. */

uint f33_dcm_resolve_read_did_route(void)

{
  ushort did;
  uint32_t puVar1;
  uint uVar2;
  int iVar3;
  byte bStack_15;
  byte bStack_14;
  char cStack_13;
  ushort uStack_12;
  ushort uStack_10;
  ushort uStack_e;
  
  did = f33_dcm_read_current_did;
  puVar1 = 0xfebeb800u;
  uStack_e = 0;
  cStack_13 = '\0';
  bStack_14 = 0;
  uStack_10 = 0;
  bStack_15 = 0;
  uStack_12 = 0;
  uVar2 = f33_dcm_resolve_did_group(f33_dcm_read_current_did,'\0',&uStack_12,&bStack_15);
  if ((((uVar2 == 0) && ((bStack_15 & 10) == 10)) &&
      (iVar3 = FUN_00094f6a(did, &cStack_13, camry_host_addr(&uStack_e)), iVar3 == 0)) && (cStack_13 != '\0')) {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x5a86))))) = 2;
  }
  else {
    uVar2 = f33_dcm_resolve_did_group(did,'\x01',&uStack_10,&bStack_14);
    if (uVar2 != 0) {
      if (uVar2 == 1) {
        return 1;
      }
      return 2;
    }
    if ((bStack_14 & 2) != 2) {
      return 1;
    }
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x5a86))))) = 1;
    uStack_e = uStack_10;
  }
  (*((ushort *)camry_host_ptr((uint32_t)(puVar1 + -0x5a88)))) = uStack_e;
  return 0;
}



uint FUN_00095f78(void)

{
  uint32_t puVar1;
  uint uVar2;
  uint uVar3;
  
  puVar1 = 0xfebeb800u;
  uVar2 = f33_dcm_resolve_read_did_route();
  if (uVar2 == 0) {
    if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x5a86))))) == '\x02') {
      uVar3 = f33_dcm_check_read_did_policy_and_length();
    }
    else {
      uVar3 = FUN_00095e76(0);
    }
  }
  else {
    uVar3 = 1;
    if (uVar2 == 1) {
      f33_dcm_report_negative_or_pending(((F33DcmMessageContext *)camry_host_ptr((uint32_t)(puVar1 + -0x5a7c))),'1');
    }
  }
  return uVar3;
}



/* Echo admitted DID then invoke fixed class reader into retained response. Advance body by reported
   u16 length, enforce post-read cap and submit only at completed cursor. Pending/iteration events
   are generic machinery, not configured multi-DID support. */

uint f33_dcm_serialize_read_did_body(uchar operation)

{
  undefined *puVar1;
  ushort uVar2;
  undefined2 uVar3;
  ushort uVar4;
  int iVar5;
  int iVar6;
  undefined8 uVar7;
  uchar event_id;
  uint uVar8;
  undefined *puVar9;
  uint uVar10;
  ushort uVar11;
  uchar uStack_25;
  short sStack_24;
  ushort auStack_22 [3];
  
  uVar4 = f33_dcm_read_did_count;
  uVar7 = 0xfebeb800;
  uStack_25 = '\0';
  sStack_24 = 1;
  uVar10 = 0;
  uVar11 = f33_dcm_read_did_cursor;
LAB_00096124:
  iVar6 = (int)uVar7;
  if (uVar11 < uVar4) {
    uVar2 = uVar11 * 2;
    uVar3 = CONCAT11((*((undefined1 *)camry_host_ptr((uint32_t)((uint)uVar2 + *(int *)(iVar6 + -0x5a7c))))),
                     (*((undefined1 *)camry_host_ptr((uint32_t)((uint)(ushort)(uVar2 + 1) + *(int *)(iVar6 + -0x5a7c))))));
    (*((undefined2 *)camry_host_ptr((uint32_t)(iVar6 + -0x5a84)))) = uVar3;
    uVar8 = f33_dcm_resolve_read_did_route();
    iVar6 = (int)uVar7;
    if (uVar8 == 0) {
      if (operation == '\0') {
        iVar5 = (*((int *)camry_host_ptr((uint32_t)(iVar6 + -0x5a70))));
        (*((undefined1 *)camry_host_ptr((uint32_t)(*(int *)(iVar6 + -0x5a74) + iVar5)))) =
             (*((undefined1 *)camry_host_ptr((uint32_t)(*(int *)(iVar6 + -0x5a7c) + (uint)uVar2))));
        (*((undefined1 *)camry_host_ptr((uint32_t)(iVar5 + *(int *)(iVar6 + -0x5a74) + 1)))) =
             (*((undefined1 *)camry_host_ptr((uint32_t)(*(int *)(iVar6 + -0x5a7c) + (uint)uVar2 + 1))));
        (*((int *)camry_host_ptr((uint32_t)(iVar6 + -0x5a70)))) = (*((int *)camry_host_ptr((uint32_t)(iVar6 + -0x5a70)))) + 2;
      }
      auStack_22[0] = 0;
      iVar5 = (*((int *)camry_host_ptr((uint32_t)(iVar6 + -0x5a70)))) + (*((int *)camry_host_ptr((uint32_t)(iVar6 + -0x5a74))));
      if ((*((char *)camry_host_ptr((uint32_t)(iVar6 + -0x5a86)))) == '\x01') {
        iVar5 = FUN_00094526((*((undefined2 *)camry_host_ptr((uint32_t)(iVar6 + -0x5a88)))), uVar3, ((uchar *)camry_host_ptr((uint32_t)(iVar5))), operation, auStack_22, 
                             &uStack_25);
        sStack_24 = sStack_24 + -1;
      }
      else {
        iVar5 = FUN_000946c6((*((undefined2 *)camry_host_ptr((uint32_t)(iVar6 + -0x5a88)))), iVar5, operation, auStack_22, &uStack_25, camry_host_addr(&sStack_24));
      }
      iVar6 = (int)uVar7;
      if (iVar5 == 0) {
        FUN_000955b6(0);
        iVar6 = (int)uVar7;
        puVar1 = ((undefined *)camry_host_ptr((uint32_t)(*(int *)(iVar6 + -0x5a70) + (uint)auStack_22[0])));
        puVar9 = *(undefined **)(iVar6 + -0x5a68);
        *(undefined **)(iVar6 + -0x5a70) = puVar1;
        if ((uintptr_t)(((undefined *)camry_host_ptr(0xfffdu)))<(uintptr_t)(puVar9)) {
          puVar9 = ((undefined *)camry_host_ptr((uint32_t)(0xfffe)));
        }
        if ((uintptr_t)(puVar1)<=(uintptr_t)(puVar9)) goto code_r0x000960ac;
      }
      else if (iVar5 == 1) {
        FUN_000955b6(0);
        if (uStack_25 != '\0') {
          f33_dcm_report_negative_or_pending(((F33DcmMessageContext *)camry_host_ptr((uint32_t)(iVar6 + -0x5a7c))),uStack_25);
        }
      }
      else if (iVar5 == 10) {
        FUN_000955b6(1);
        puVar1 = ((undefined *)camry_host_ptr((uint32_t)(*(int *)(iVar6 + -0x5a70) + (uint)auStack_22[0])));
        puVar9 = *(undefined **)(iVar6 + -0x5a68);
        *(undefined **)(iVar6 + -0x5a70) = puVar1;
        if ((uintptr_t)(((undefined *)camry_host_ptr(0xfffdu)))<(uintptr_t)(puVar9)) {
          puVar9 = ((undefined *)camry_host_ptr((uint32_t)(0xfffe)));
        }
        if ((uintptr_t)(puVar1)<=(uintptr_t)(puVar9)) {
          (*((ushort *)camry_host_ptr((uint32_t)(iVar6 + -0x5a82)))) = uVar11;
          event_id = '\x05';
          goto LAB_00096114;
        }
      }
      else {
        FUN_000955b6(0);
      }
    }
  }
  goto LAB_0009612a;
code_r0x000960ac:
  uVar11 = uVar11 + 1;
  if (uVar11 < uVar4) {
    if (sStack_24 == 0) {
      (*((ushort *)camry_host_ptr((uint32_t)(iVar6 + -0x5a82)))) = uVar11;
      event_id = '$';
LAB_00096114:
      f33_dcm_enqueue_event(event_id);
      uVar10 = 10;
LAB_0009612a:
      if (uVar11 == uVar4) {
        f33_dcm_report_positive_response(((F33DcmMessageContext *)camry_host_ptr((uint32_t)(iVar6 + -0x5a7c))));
      }
      return uVar10;
    }
    operation = '\0';
  }
  goto LAB_00096124;
}



undefined4 FUN_00096244(void)

{
  undefined2 uVar1;
  ushort uVar2;
  uchar *puVar3;
  uint32_t puVar4;
  int iVar5;
  undefined1 uStack_16;
  undefined1 uStack_15;
  undefined2 uStack_14;
  undefined2 uStack_12;
  
  puVar3 = ((void *)camry_host_ptr((uint32_t)(f33_dcm_read_message.response)));
  uVar2 = f33_dcm_read_current_did;
  puVar4 = 0xfebeb800u;
  uStack_12 = 0;
  uStack_15 = 0;
  uStack_14 = 0;
  uStack_16 = 1;
  iVar5 = FUN_000955bc();
  if (iVar5 == 1) {
    uVar1 = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar4 + -0x5a88))));
    if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x5a86))))) == '\x01') {
      FUN_0009445a(uVar1,uVar2,2,&uStack_16);
      FUN_0009449e(uVar1,uVar2,2,&uStack_14);
      FUN_00094526(uVar1,uVar2,puVar3,2,&uStack_14,&uStack_15);
      f33_dcm_invalidate_queued_event('\x04','\0');
      f33_dcm_invalidate_queued_event('\x1f','\0');
    }
    else {
      FUN_000946c6(uVar1, camry_host_addr(puVar3), 2, &uStack_14, &uStack_15, camry_host_addr(&uStack_12));
    }
    f33_dcm_invalidate_queued_event('\x05','\0');
    FUN_000955b6(0);
  }
  f33_dcm_invalidate_queued_event('$','\0');
  FUN_0009560e(1);
  return 0;
}



/* Operation0 admits configured SID22;2 cancels retained read continuation. Other operations
   return0. Message snapshot, read preparation and serialization are separate from response
   delivery. */

uint f33_dcm_read_did_service(uchar operation,F33DcmMessageContext *message)

{
  uint uVar1;
  
  if (operation == '\0') {
    uVar1 = f33_dcm_begin_read_did_request(message);
  }
  else {
    uVar1 = 0;
    if (operation == '\x02') {
      uVar1 = FUN_00096244();
    }
  }
  return uVar1;
}



uint FUN_00096312(void)

{
  return f33_dcm_preflight_read_did_body('\x01');
}



uint FUN_00096320(char param_1)

{
  return f33_dcm_serialize_read_did_body(param_1 != '$');
}



uint FUN_00096336(void)

{
  return f33_dcm_preflight_read_did_body('\x02');
}



bool FUN_00096344(uint param_1,uint param_2)

{
  uint uVar1;
  
  for (uVar1 = 0; uVar1 < (param_2 & 0xff); uVar1 = uVar1 + 1 & 0xff) {
    DAT_febe5da4 = (uint)(*((byte *)camry_host_ptr((uint32_t)(uVar1 + (param_1 & 0xff) + DAT_febe5dac + 1)))) +
                   DAT_febe5da4 * 0x100;
  }
  return DAT_febe5da4 == 0 || (uint)(DAT_febe5dc0 - DAT_febe5db8) < DAT_febe5da4;
}



undefined4 FUN_00096388(uint param_1)

{
  uint uVar1;
  uint32_t puVar2;
  undefined4 uVar3;
  int iVar4;
  undefined4 uVar5;
  
  puVar2 = 0xfebeb800u;
  uVar5 = 1;
  if (DAT_00026154 == '\x01') {
    uVar3 = 0;
    DAT_febe5da8 = (*((undefined1 *)camry_host_ptr((uint32_t)(DAT_febe5dac + 1))));
    uVar1 = 1;
  }
  else {
    uVar1 = 0;
    uVar3 = 1;
  }
  for (; uVar1 < (param_1 & 0xff); uVar1 = uVar1 + 1 & 0xff) {
    DAT_febe5da0 = (uint)(*((byte *)camry_host_ptr((uint32_t)(DAT_febe5dac + uVar1 + 1)))) + DAT_febe5da0 * 0x100;
  }
  iVar4 = FUN_00094be2(0,DAT_febe5da0,uVar3,DAT_febe5da8,((undefined *)camry_host_ptr(0xfebe5da9u)),((undefined *)camry_host_ptr(0xfebe5daau)));
  if (iVar4 == 0) {
    iVar4 = FUN_00094cc4(0,(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x5a57))))),(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x5a56))))),(*((undefined4 *)camry_host_ptr((uint32_t)(puVar2 + -0x5a60)))),
                         (*((undefined4 *)camry_host_ptr((uint32_t)(puVar2 + -0x5a5c)))));
    if (iVar4 == 0) {
      uVar5 = 0;
    }
    else {
      uVar5 = 1;
    }
  }
  return uVar5;
}



undefined4 FUN_00096410(byte param_1)

{
  uint32_t puVar1;
  undefined4 uVar2;
  uchar nrc;
  uchar uStack_d;
  
  puVar1 = 0xfebeb800u;
  uStack_d = '\0';
  if ((1 < param_1) && (param_1 != 3)) {
    return 0;
  }
  uVar2 = FUN_000965fc(param_1, DAT_febe5da8, DAT_febe5da0, DAT_febe5da4, DAT_febe5db8 + DAT_febe5db4, camry_host_addr(&uStack_d));
  nrc = uStack_d;
  switch(uVar2) {
  case 0:
    (*((int *)camry_host_ptr((uint32_t)(puVar1 + -0x5a48)))) = (*((int *)camry_host_ptr((uint32_t)(puVar1 + -0x5a48)))) + (*((int *)camry_host_ptr((uint32_t)(puVar1 + -0x5a5c))));
    f33_dcm_report_positive_response(((F33DcmMessageContext *)camry_host_ptr((uint32_t)(puVar1 + -0x5a54))));
  default:
    FUN_000955b6(0);
    return 0;
  case 1:
    f33_dcm_enqueue_event('#');
    FUN_000955b6(1);
    return 10;
  case 2:
    FUN_000955b6(0);
    if (nrc == '\0') {
      return 0;
    }
    break;
  case 3:
    nrc = 'x';
    FUN_000955b6(1);
  }
  f33_dcm_report_negative_or_pending(((F33DcmMessageContext *)camry_host_ptr((uint32_t)(puVar1 + -0x5a54))),nrc);
  return 0;
}



undefined4 FUN_000964b0(undefined4 *param_1)

{
  undefined4 *puVar1;
  uint32_t puVar2;
  uchar nrc;
  int iVar3;
  undefined4 uVar4;
  uint uVar5;
  undefined4 *puVar6;
  uchar uStack_11;
  
  puVar2 = 0xfebeb800u;
  uStack_11 = '\0';
  FUN_0009560e(0x0);
  puVar1 = ((undefined4 *)camry_host_ptr((uint32_t)(puVar2 + -0x5a54)));
  puVar6 = param_1;
  do {
    uVar4 = *puVar6;
    puVar6 = puVar6 + 1;
    *puVar1 = uVar4;
    puVar1 = puVar1 + 1;
  } while ((uintptr_t)(param_1 + 7)!=(uintptr_t)(puVar6));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x5a58))))) = 0;
  (*((undefined4 *)camry_host_ptr((uint32_t)(puVar2 + -0x5a60)))) = 0;
  (*((undefined4 *)camry_host_ptr((uint32_t)(puVar2 + -0x5a5c)))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x5a57))))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x5a56))))) = 0;
  FUN_000955b6(0);
  if ((uint)param_1[1] < 3) {
LAB_00096570:
    nrc = '\x13';
  }
  else {
    iVar3 = FUN_00094ba8(**(undefined1 **)(puVar2 + -0x5a54));
    if (iVar3 == 0) {
      uVar5 = *(byte *)*param_1 & 0xf;
      iVar3 = (int)(uint)*(byte *)*param_1 >> 4;
      if (param_1[1] != iVar3 + uVar5 + 1) goto LAB_00096570;
      iVar3 = FUN_00096344(uVar5,iVar3);
      if ((iVar3 == 0) && (iVar3 = FUN_00096388(uVar5), iVar3 == 0)) {
        f33_dcm_get_security_level(&uStack_11);
        iVar3 = FUN_00094d04(0,(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x5a57))))),(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x5a56))))),uStack_11);
        if (iVar3 == 0) {
          iVar3 = FUN_00096410(0);
          if (iVar3 == 0) {
            return 0;
          }
          return 10;
        }
        nrc = '3';
        goto LAB_00096574;
      }
    }
    nrc = '1';
  }
LAB_00096574:
  f33_dcm_report_negative_or_pending(((F33DcmMessageContext *)camry_host_ptr((uint32_t)(puVar2 + -0x5a54))),nrc);
  return 0;
}



void FUN_00096582(void)

{
  uint32_t puVar1;
  int iVar2;
  
  puVar1 = 0xfebeb800u;
  iVar2 = FUN_000955bc();
  if (iVar2 == 1) {
    FUN_000965fc(2,(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x5a58))))),(*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + -0x5a60)))),
                 (*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + -0x5a5c)))),0,0);
    FUN_000955b6(0);
  }
  f33_dcm_invalidate_queued_event('#','\0');
  FUN_0009560e(1);
  return;
}



/* Operation0 validates configured ALFID15 and bounded memory family;2 cancels adapter state;3
   enters configured continuation path. No memory write or indirect executable dispatch. */

uint f33_dcm_read_memory_service(uchar operation,F33DcmMessageContext *message)

{
  uint uVar1;
  
  if (operation == '\0') {
    uVar1 = FUN_000964b0(message);
  }
  else {
    uVar1 = 0;
    if (operation == '\x02') {
      FUN_00096582();
    }
    else if (operation == '\x03') {
      uVar1 = FUN_00096410((uint)(byte)operation);
    }
  }
  return uVar1;
}



undefined4 FUN_000965ee(void)

{
  return FUN_00096410(1);
}



undefined4
FUN_000965fc(char param_1,undefined1 param_2,undefined4 param_3,undefined4 param_4,
            undefined4 param_5,undefined4 param_6)

{
  undefined4 uVar1;
  
  if (param_1 == '\x02') {
    thunk_FUN_0008d4ae();
    uVar1 = 0;
  }
  else {
    uVar1 = FUN_0008d546(param_1, param_2, param_3, param_4, ((uchar *)camry_host_ptr((uint32_t)(param_5))), ((undefined1 *)camry_host_ptr((uint32_t)(param_6))));
  }
  return uVar1;
}



void FUN_00096622(uint param_1,char param_2)

{
  uint uVar1;
  
  if ((param_1 & 0xff) < 2) {
    uVar1 = 1 << (param_1 & 0x1f);
    if (param_2 == '\x01') {
      f33_app_security_delay_bits = f33_app_security_delay_bits | uVar1;
    }
    else {
      f33_app_security_delay_bits = f33_app_security_delay_bits & ~uVar1;
    }
  }
  return;
}



/* Cold module initializer clearsdelaymask andboth failures, arms configured initial10000 delays on
   timers7/8 and setsbits, then token/issuedflag0. Actual95590 init table26104 selects it. Does not
   itself clear application crypto buffers8D66A. */

void f33_dcm_security_initialize_delays(void)

{
  uint32_t puVar1;
  uint32_t puVar2;
  uint uVar3;
  int iVar4;
  
  puVar1 = 0xfebeb800u;
  puVar2 = 0x23dfcu;
  f33_app_security_delay_bits = 0;
  uVar3 = 0;
  do {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(uVar3 - 0x5a31))))) = 0;
    iVar4 = (short)uVar3 * 0x18;
    if ((*((int *)camry_host_ptr((uint32_t)(puVar2 + iVar4 + 0x2370)))) != 0) {
      f33_dcm_arm_software_timer((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(uVar3 * 2 + 0x235d))))),(*((uint *)camry_host_ptr((uint32_t)(puVar2 + iVar4 + 0x2370)))));
      FUN_00096622(uVar3,1);
    }
    uVar3 = uVar3 + 1;
  } while (uVar3 < 2);
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x5a33))))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x5a32))))) = 0;
  return;
}



/* Calls96B98(level,retainedrequest,op,response,&NRC) before delay/current-security tests. Return0
   sets5DCE=1; delay mask then clears token/NRC37. Otherwise already-unlocked samelevel zeroes16
   response and token0, else tokenlevel. Stages16-byte response. Return1 clears token and uses
   callbackNRC;10 supportsgeneric pending but actual callbacks never10. */

uint f33_dcm_security_seed_callback_join(uchar level,uchar operation)

{
  uint uVar1;
  uint32_t puVar2;
  uint32_t puVar3;
  uchar uVar4;
  int iVar5;
  uint uVar6;
  uchar uStack_12;
  uchar uStack_11;
  
  uVar4 = f33_app_security_selected_row;
  puVar2 = 0xfebeb800u;
  puVar3 = 0x23dfcu;
  uVar6 = (uint)f33_app_security_selected_row;
  uStack_12 = '\0';
  if (uVar6 < 2) {
    uStack_11 = '\0';
    iVar5 = FUN_00096b98(level, f33_app_dcm_security_message.request, operation, 
                         f33_app_dcm_security_message.response, camry_host_addr(&uStack_11));
    if (iVar5 == 0) {
      FUN_000955b6(0);
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x5a32))))) = 1;
      if (((*((uint *)camry_host_ptr((uint32_t)(puVar2 + -0x5a38)))) & 1 << (uVar6 & 0x1f)) == 0) {
        f33_dcm_get_security_level(&uStack_12);
        uVar6 = (*((uint *)camry_host_ptr((uint32_t)(puVar3 + (short)(ushort)uVar4 * 0x18 + 0x2378))));
        if (level == uStack_12) {
          for (uVar1 = 0; uVar1 < uVar6; uVar1 = uVar1 + 1) {
            (*((undefined1 *)camry_host_ptr((uint32_t)(*(int *)(puVar2 + -0x5a24) + uVar1)))) = 0;
          }
          level = '\0';
        }
        (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x5a33))))) = level;
        (*((uint *)camry_host_ptr((uint32_t)(puVar2 + -0x5a20)))) = uVar6;
        f33_dcm_report_positive_response(((F33DcmMessageContext *)camry_host_ptr((uint32_t)(puVar2 + -0x5a2c))));
        return 0;
      }
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x5a33))))) = 0;
      uVar4 = '7';
    }
    else {
      if (iVar5 != 1) {
        if (iVar5 != 10) {
          FUN_000955b6(0);
          (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x5a33))))) = 0;
          return 0;
        }
        FUN_000955b6(1);
        f33_dcm_enqueue_event('\x0f');
        return 10;
      }
      FUN_000955b6(0);
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x5a33))))) = 0;
      uVar4 = uStack_11;
    }
    f33_dcm_report_negative_or_pending(((F33DcmMessageContext *)camry_host_ptr((uint32_t)(puVar2 + -0x5a2c))),uVar4);
  }
  return 0;
}



void FUN_00096768(void)

{
  if (f33_app_security_selected_row < 2) {
    f33_dcm_security_seed_callback_join
              (f33_app_security_level_rows[(short)(ushort)f33_app_security_selected_row].
               security_level,'\x01');
  }
  return;
}



/* Application0 clears selected failures, publishes security via91E12, clears token, stageszero-body
   response BEFORE95644. ApplicationB saturating increments; belowthreshold2 NRC35 else armraw10000
   timer7/8, setdelaybit andNRC36. Failures/challenge retained. Callback1 usesNRC;10genericpending
   only, actualcallbacks never10. */

uint f33_dcm_security_key_callback_join(uchar level,uchar operation)

{
  byte bVar1;
  byte bVar2;
  uint32_t puVar3;
  uint32_t puVar4;
  F33DcmMessageContext *message;
  uchar uVar5;
  int iVar6;
  uint uVar7;
  uchar uStack_11;
  
  uVar5 = f33_app_security_selected_row;
  puVar3 = 0xfebeb800u;
  puVar4 = 0x23dfcu;
  uVar7 = (uint)f33_app_security_selected_row;
  if (uVar7 < 2) {
    uStack_11 = '\0';
    iVar6 = FUN_00096bce(level, f33_app_dcm_security_message.request, operation, camry_host_addr(&uStack_11));
    if (iVar6 == 0) {
      FUN_000955b6(0);
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(uVar7 - 0x5a31))))) = 0;
      FUN_00091e12(level);
      (*((undefined4 *)camry_host_ptr((uint32_t)(puVar3 + -0x5a20)))) = 0;
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x5a33))))) = 0;
      f33_dcm_report_positive_response(((F33DcmMessageContext *)camry_host_ptr((uint32_t)(puVar3 + -0x5a2c))));
    }
    else {
      if (iVar6 == 1) {
        FUN_000955b6(0);
        (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x5a33))))) = 0;
        message = ((F33DcmMessageContext *)camry_host_ptr((uint32_t)(puVar3 + -0x5a2c)));
        uVar5 = uStack_11;
      }
      else {
        if (iVar6 == 10) {
          FUN_000955b6(1);
          f33_dcm_enqueue_event('\x10');
          return 10;
        }
        if (iVar6 != 0xb) {
          FUN_000955b6(0);
          (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x5a33))))) = 0;
          return 0;
        }
        FUN_000955b6(0);
        bVar2 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(uVar7 - 0x5a31)))));
        if (bVar2 != 0xff) {
          bVar1 = bVar2 + 1;
          bVar2 = bVar2 + 1;
          (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(uVar7 - 0x5a31))))) = bVar1;
        }
        if (bVar2 < (byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)((short)(ushort)uVar5 * 0x18 + 0x237d)))))) {
          (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x5a33))))) = 0;
          message = ((F33DcmMessageContext *)camry_host_ptr((uint32_t)(puVar3 + -0x5a2c)));
          uVar5 = '5';
        }
        else {
          if ((*((int *)camry_host_ptr((uint32_t)(puVar4 + (short)(ushort)uVar5 * 0x18 + 0x236c)))) != 0) {
            f33_dcm_arm_software_timer
                      ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(uVar7 * 2 + 0x235d))))),
                       (*((uint *)camry_host_ptr((uint32_t)(puVar4 + (short)(ushort)uVar5 * 0x18 + 0x236c)))));
            FUN_00096622(uVar7,1);
          }
          (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x5a33))))) = 0;
          message = ((F33DcmMessageContext *)camry_host_ptr((uint32_t)(puVar3 + -0x5a2c)));
          uVar5 = '6';
        }
      }
      f33_dcm_report_negative_or_pending(message,uVar5);
    }
  }
  return 0;
}



void FUN_0009687c(void)

{
  if (f33_app_security_selected_row < 2) {
    f33_dcm_security_key_callback_join
              (f33_app_security_level_rows[(short)(ushort)f33_app_security_selected_row].
               security_level,'\x01');
  }
  return;
}



/* Timer callback7/8 matches26159/2615B and clears respective5DC8 bit only;
   attempts/challenge/client/security/token unchanged. */

void f33_dcm_security_delay_expired(uchar timer_slot)

{
  uint uVar1;
  
  uVar1 = 0;
  do {
    if (timer_slot == (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x26159u + (uint32_t)(uVar1 * 2) * 1u))))) {
      FUN_00096622(uVar1,0);
      return;
    }
    uVar1 = uVar1 + 1;
  } while (uVar1 < 2);
  return;
}



void FUN_000968c6(void)

{
  f33_app_security_issued_level = '\0';
  return;
}



/* ROM25F48-selected application session callback. Exact instructions ignore both args: if5DCE==1
   clear5DCD and5DCE; otherwise retain token. No delay/failure reset and no challenge clear
   here;4D582 later owns application crypto reset. */

void f33_dcm_security_session_notification(uchar old_session,uchar new_session)

{
  if (f33_app_security_seed_callback_succeeded == '\x01') {
    f33_app_security_issued_level = '\0';
    f33_app_security_seed_callback_succeeded = '\0';
  }
  return;
}



/* Constant source: return 1; shape-classified from the canonical corpus. Callers receive this
   literal directly; its meaning is not recovered. */

undefined4 f33_return_const_1_968de(void)

{
  return 1;
}



/* Invalidate event0F, and only if5D28==1 call application seed-cancel wrapper, then clearasyncflag.
   Always clear generic token and release5D24. Retains issuedflag/delay/failures/challenge for
   actual synchronous path. Exact application wrapper ignoresoperation and is not a hardware
   cancellation guarantee. */

uint f33_dcm_security_cancel_seed(uchar subfunction,uchar operation)

{
  uint32_t puVar1;
  int iVar2;
  undefined1 uStack_f;
  undefined1 uStack_e;
  undefined1 uStack_d;
  
  puVar1 = 0xfebeb800u;
  uStack_d = 0;
  uStack_f = 0;
  f33_dcm_invalidate_queued_event('\x0f','\0');
  iVar2 = FUN_000955bc();
  if (iVar2 == 1) {
    FUN_00096b98((int)(subfunction + 1) >> 1, camry_host_addr(&uStack_f), operation, camry_host_addr(&uStack_e), camry_host_addr(&uStack_d));
    FUN_000955b6(0);
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x5a33))))) = 0;
  FUN_0009560e(1);
  return 0;
}



/* Operation0\u2192968E2 seed admission,2\u219296990 cancellation; others return0. Actual third
   argument retained inr8 and consumed by968E2. Operation0→968E2 seed admission,2→96990
   cancellation; */

uint f33_dcm_security_seed_operation
               (uchar subfunction,uchar operation,F33DcmMessageContext *message)

{
  uint uVar1;
  
  if (operation == '\0') {
    uVar1 = f33_dcm_security_seed_request(subfunction,'\0',message);
  }
  else {
    uVar1 = 0;
    if (operation == '\x02') {
      uVar1 = f33_dcm_security_cancel_seed(subfunction,'\x02');
    }
  }
  return uVar1;
}



/* Invalidate event10; only5D28==1 invokes key callback withcancel operation; always
   cleartoken/release5D24. Exact key callback ignoresoperation; reachable synchronous implementation
   neverreturns10 and doesnotown asynchronous operation to cancel. */

uint f33_dcm_security_cancel_key(uchar subfunction,uchar operation)

{
  uint32_t puVar1;
  int iVar2;
  undefined1 uStack_e;
  undefined1 uStack_d;
  
  puVar1 = 0xfebeb800u;
  uStack_d = 0;
  uStack_e = 0;
  f33_dcm_invalidate_queued_event('\x10','\0');
  iVar2 = FUN_000955bc();
  if (iVar2 == 1) {
    FUN_00096bce((int)(subfunction + 1) >> 1, camry_host_addr(&uStack_e), operation, camry_host_addr(&uStack_d));
    FUN_000955b6(0);
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x5a33))))) = 0;
  FUN_0009560e(1);
  return 0;
}



/* Operation0\u219296A04 key admission,2\u219296AB6 cancellation; others return0. Actual third
   argument retained inr8. Operation0→96A04 key admission,2→96AB6 cancellation; */

uint f33_dcm_security_key_operation(uchar subfunction,uchar operation,F33DcmMessageContext *message)

{
  uint uVar1;
  
  if (operation == '\0') {
    uVar1 = f33_dcm_security_key_request(subfunction,'\0',message);
  }
  else {
    uVar1 = 0;
    if (operation == '\x02') {
      uVar1 = f33_dcm_security_cancel_key(subfunction,'\x02');
    }
  }
  return uVar1;
}



/* Constant source: return 1; shape-classified from the canonical corpus. Callers receive this
   literal directly; its meaning is not recovered. */

undefined4 f33_return_const_1_96b24(void)

{
  return 1;
}



uint FUN_00096b28(uchar *param_1,undefined4 param_2,uchar *param_3,uchar *param_4)

{
  return f33_app_security_prepare_seed(param_1,param_3,param_4);
}



/* Constant source: return 1; shape-classified from the canonical corpus. Callers receive this
   literal directly; its meaning is not recovered. */

undefined4 f33_return_const_1_96b38(void)

{
  return 1;
}



uint FUN_00096b3c(uchar *param_1)

{
  return f33_app_security_compare_key(param_1);
}



/* Configured SID27 sub1; wrapper preserves message inr8, moves operation tor7 and fixedsubfunction
   tor6. Level=(sub+1)>>1. Odd seed dispatch969E4, even key96B04; r8 carries the consumed message
   pointer. r8 message is real despite missing corpus parameters. */

uint f33_dcm_security_sub1_callback(uchar operation,F33DcmMessageContext *message)

{
  uint uVar1;
  
  uVar1 = f33_dcm_security_seed_operation('\x01',operation,message);
  return uVar1;
}



/* Configured SID27 sub2; wrapper preserves message inr8, moves operation tor7 and fixedsubfunction
   tor6. Level=(sub+1)>>1. Odd seed dispatch969E4, even key96B04; r8 carries the consumed message
   pointer. r8 message is real despite missing corpus parameters. */

uint f33_dcm_security_sub2_callback(uchar operation,F33DcmMessageContext *message)

{
  uint uVar1;
  
  uVar1 = f33_dcm_security_key_operation('\x02',operation,message);
  return uVar1;
}



/* Configured SID27 sub3; wrapper preserves message inr8, moves operation tor7 and fixedsubfunction
   tor6. Level=(sub+1)>>1. Odd seed dispatch969E4, even key96B04; r8 carries the consumed message
   pointer. r8 message is real despite missing corpus parameters. */

uint f33_dcm_security_sub3_callback(uchar operation,F33DcmMessageContext *message)

{
  uint uVar1;
  
  uVar1 = f33_dcm_security_seed_operation('\x03',operation,message);
  return uVar1;
}



/* Configured SID27 sub4; wrapper preserves message inr8, moves operation tor7 and fixedsubfunction
   tor6. Level=(sub+1)>>1. Odd seed dispatch969E4, even key96B04; r8 carries the consumed message
   pointer. r8 message is real despite missing corpus parameters. */

uint f33_dcm_security_sub4_callback(uchar operation,F33DcmMessageContext *message)

{
  uint uVar1;
  
  uVar1 = f33_dcm_security_key_operation('\x04',operation,message);
  return uVar1;
}



undefined4
FUN_00096b98(char param_1,undefined4 param_2,undefined1 param_3,undefined4 param_4,
            undefined4 param_5)

{
  undefined4 uVar1;
  
  if (param_1 == '\x01') {
    uVar1 = ((void)(param_2), (void)(param_3), (void)(param_4), (void)(param_5), f33_return_const_1_96b24());
  }
  else {
    uVar1 = 0;
    if (param_1 == '\x02') {
      uVar1 = FUN_00096b28(((uchar *)camry_host_ptr((uint32_t)(param_2))), param_3, ((uchar *)camry_host_ptr((uint32_t)(param_4))), ((uchar *)camry_host_ptr((uint32_t)(param_5))));
    }
  }
  return uVar1;
}



undefined4 FUN_00096bce(char param_1,undefined4 param_2,undefined1 param_3,undefined4 param_4)

{
  undefined4 uVar1;
  
  if (param_1 == '\x01') {
    uVar1 = ((void)(param_2), (void)(param_3), (void)(param_4), f33_return_const_1_96b38());
  }
  else {
    uVar1 = 0;
    if (param_1 == '\x02') {
      uVar1 = ((void)(param_3), (void)(param_4), FUN_00096b3c(((uchar *)camry_host_ptr((uint32_t)(param_2)))));
    }
  }
  return uVar1;
}



/* Exactconfiguration admitslow1/high0 only; optional4/5nodepaths are unconfigured. */

uint f33_dcm_validate_configured_communication_selection
               (uchar subfunction,uchar communication_class,uchar subnet,ushort node)

{
  uchar uVar1;
  ushort uVar2;
  uint uVar3;
  uint uVar4;
  
  uVar4 = 1;
  uVar1 = f33_dcm_communication_configuration.normal_enabled;
  if ((((communication_class == '\x01') ||
       (uVar1 = f33_dcm_communication_configuration.nm_enabled, communication_class == '\x02')) ||
      ((communication_class == '\x03' &&
       (f33_dcm_communication_configuration.normal_enabled == '\x01')))) && (uVar1 == '\x01')) {
    if (subnet != '\0') {
      if (subnet == '\x0f') {
        if (f33_dcm_communication_configuration.current_network_enabled != '\x01') {
          return uVar4;
        }
      }
      else {
        uVar2 = 0;
        while( true ) {
          if (f33_dcm_communication_configuration.subnet_count <= uVar2) {
            return uVar4;
          }
          if (((*((uchar *)camry_host_ptr((uint32_t)((int)f33_dcm_communication_configuration.subnets + (short)uVar2 * 3 + 1))))
               == subnet) &&
             ((*((char *)camry_host_ptr((uint32_t)((int)f33_dcm_communication_configuration.subnets + (short)uVar2 * 3)))) ==
              '\x01')) break;
          uVar2 = uVar2 + 1 & 0xff;
        }
      }
    }
    if (subfunction == '\x04' || subfunction == '\x05') {
      uVar3 = 0;
      while( true ) {
        if ((ushort)(*((volatile uint16_t *)camry_host_ptr(0x261cau))) <= uVar3) {
          return uVar4;
        }
        if (((*((ushort *)camry_host_ptr((uint32_t)((int)f33_dcm_communication_configuration.nodes + uVar3 * 4 + 2)))) == node) &&
           ((*((char *)camry_host_ptr((uint32_t)((int)f33_dcm_communication_configuration.nodes + uVar3 * 4)))) == '\x01')) break;
        uVar3 = uVar3 + 1 & 0xffff;
      }
    }
    return 0;
  }
  return uVar4;
}



void FUN_00096ca4(char param_1,short param_2,char param_3,undefined1 param_4)

{
  int iVar1;
  uint uVar2;
  
  if (param_1 == '\x04' || param_1 == '\x05') {
    for (uVar2 = 0; uVar2 < (ushort)(*((volatile uint16_t *)camry_host_ptr(0x261cau)));
        uVar2 = uVar2 + 1 & 0xffff) {
      iVar1 = uVar2 * 4;
      if ((((*((short *)camry_host_ptr((uint32_t)((int)f33_dcm_communication_configuration.nodes + iVar1 + 2)))) == param_2) &&
          ((*((char *)camry_host_ptr((uint32_t)((int)f33_dcm_communication_configuration.nodes + iVar1)))) == '\x01')) &&
         ((*((char *)camry_host_ptr((uint32_t)((int)f33_dcm_communication_configuration.nodes + iVar1 + 1)))) == param_3))
      goto LAB_00096cf6;
    }
  }
  else {
LAB_00096cf6:
    ((void)(param_3), (void)(param_4), f33_return_const_0_9713a());
    ((void)(param_3), (void)(param_4), f33_return_only_stub_97138());
  }
  return;
}



undefined4 FUN_00096d0a(char param_1,short param_2,char param_3,undefined1 param_4)

{
  uint uVar1;
  int iVar2;
  
  if (param_1 == '\x04' || param_1 == '\x05') {
    for (uVar1 = 0; uVar1 < (ushort)(*((volatile uint16_t *)camry_host_ptr(0x261cau)));
        uVar1 = uVar1 + 1 & 0xffff) {
      iVar2 = uVar1 * 4;
      if ((((*((short *)camry_host_ptr((uint32_t)((int)f33_dcm_communication_configuration.nodes + iVar2 + 2)))) == param_2) &&
          ((*((char *)camry_host_ptr((uint32_t)((int)f33_dcm_communication_configuration.nodes + iVar2)))) == '\x01')) &&
         ((*((char *)camry_host_ptr((uint32_t)((int)f33_dcm_communication_configuration.nodes + iVar2 + 1)))) == param_3))
      goto LAB_00096d5a;
    }
  }
  else {
LAB_00096d5a:
    iVar2 = FUN_00097128(param_3,param_4);
    if (iVar2 != 0) {
      if (iVar2 == 10) {
        return 10;
      }
      return 1;
    }
  }
  return 0;
}



/* Iterateactiveconfiguredchannels;action0positivecompletes,1returns,10savestherowcursorandqueues26h.
   Stackargumentfromrealcallsite,notafifthGPR. */

void f33_dcm_complete_or_queue_communication_request
               (uchar subnet,uchar subfunction,ushort node,uchar mapped_mode,uchar start_index)

{
  ushort uVar1;
  uint32_t puVar2;
  uint32_t puVar3;
  int iVar4;
  uint uVar5;
  
  puVar2 = 0xfebeb800u;
  puVar3 = 0x23dfcu;
  if (subnet == '\0') {
    for (uVar5 = (uint)start_index; uVar5 < (byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(0x23cc))))); uVar5 = uVar5 + 1 & 0xff) {
      if (((*((char *)camry_host_ptr((uint32_t)(*(int *)(puVar3 + 0x23d0) + uVar5 * 2)))) == '\x01') &&
         (iVar4 = FUN_00096d0a(subfunction,node,
                               (*((undefined1 *)camry_host_ptr((uint32_t)(*(int *)(puVar3 + 0x23d0) + uVar5 * 2 + 1)))),
                               mapped_mode), iVar4 != 0)) goto LAB_00096dc0;
    }
  }
  else if (subnet == '\x0f') {
    uVar5 = thunk_FUN_00093c60();
    if (2 < uVar5) {
      return;
    }
    uVar1 = (*((ushort *)camry_host_ptr((uint32_t)(puVar3 + (short)uVar5 * 0xc + 0x20ec))));
    if (1 < uVar1) {
      return;
    }
    iVar4 = FUN_00096d0a(subfunction,node,
                         (*((undefined1 *)camry_host_ptr((uint32_t)(*(int *)((uint)*(ushort *)
                                           ((int)(puVar3 + (short)uVar5 * 0xc + 0x20ec) + 2) * 4 +
                                   *(int *)(puVar3 + (short)uVar1 * 0x14 + 0x20c4)) + 2)))),mapped_mode
                        );
    if (iVar4 != 0) {
      if (iVar4 == 1) {
        return;
      }
      goto LAB_00096dc8;
    }
  }
  else {
    for (uVar5 = (uint)start_index; uVar5 < (byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(0x23cd))))); uVar5 = uVar5 + 1 & 0xff) {
      iVar4 = (short)uVar5 * 3;
      if ((((*((uchar *)camry_host_ptr((uint32_t)(*(int *)(puVar3 + 0x23d4) + iVar4 + 1)))) == subnet) &&
          ((*((char *)camry_host_ptr((uint32_t)(*(int *)(puVar3 + 0x23d4) + iVar4)))) == '\x01')) &&
         (iVar4 = FUN_00096d0a(subfunction,node,
                               (*((undefined1 *)camry_host_ptr((uint32_t)(*(int *)(puVar3 + 0x23d4) + iVar4 + 2)))),mapped_mode),
         iVar4 != 0)) goto LAB_00096dc0;
    }
  }
  f33_dcm_report_positive_response(((F33DcmMessageContext *)camry_host_ptr((uint32_t)(puVar2 + -0x5a08))));
  return;
LAB_00096dc0:
  if (iVar4 == 1) {
    return;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x5a0d))))) = (char)uVar5;
LAB_00096dc8:
  f33_dcm_enqueue_event('&');
  return;
}



/* Invalidateallqueued26hentriesandclear5D24sentinel;no8196rollbackorcontrollerstop/start. */

void f33_dcm_cancel_communication_continuation(void)

{
  f33_dcm_invalidate_queued_event('&','\0');
  FUN_0009560e(1);
  return;
}



/* Operation0 starts96E6A;2 removes queued26h continuation and clears diagnostic sentinel, not
   retained policy; otheroperationsreturn0. */

uint f33_dcm_dispatch_communication_control_lifetime
               (uchar operation,F33DcmMessageContext *message,uchar subfunction)

{
  uint uVar1;
  
  if (operation == '\0') {
    uVar1 = f33_dcm_begin_configured_communication_request(message,subfunction);
  }
  else {
    uVar1 = 0;
    if (operation == '\x02') {
      f33_dcm_cancel_communication_continuation();
    }
  }
  return uVar1;
}



/* Exact261C4=0 disablesrestorebody. Latentnew1/retainedSID28invalidrestore8targetsarealsoempty.
   KeepR8new_sessionforwardingto916EC;thisdoesnotclear8196. */

void f33_dcm_notify_communication_session_change(uchar old_session,uchar new_session)

{
  undefined1 uVar1;
  undefined8 uVar2;
  int iVar3;
  uint uVar4;
  
  uVar2 = 0x23dfcfebeb800;
  if ((f33_dcm_communication_configuration.restore_enabled == '\x01') &&
     ((new_session == '\x01' ||
      ((f33_dcm_communication_lifetime.accepted_active == '\x01' &&
       (iVar3 = FUN_000916ec(0x28,f33_dcm_communication_lifetime.protocol_selector, (uint)(byte)new_session), iVar3 != 0)))))
     ) {
    for (uVar4 = 0; iVar3 = (int)((ulonglong)uVar2 >> 0x20), uVar4 < (*((byte *)camry_host_ptr((uint32_t)(iVar3 + 0x23cc))));
        uVar4 = uVar4 + 1 & 0xff) {
      if ((*((char *)camry_host_ptr((uint32_t)(*(int *)(iVar3 + 0x23d0) + uVar4 * 2)))) == '\x01') {
        uVar1 = (*((undefined1 *)camry_host_ptr((uint32_t)(*(int *)(iVar3 + 0x23d0) + uVar4 * 2 + 1))));
        iVar3 = ((void)(uVar1), f33_return_const_b_9713e());
        if (iVar3 != 8) {
          ((void)(uVar1), (void)(8), f33_return_const_0_9713a());
          ((void)(uVar1), (void)(8), f33_return_only_stub_97138());
        }
      }
    }
  }
  return;
}



/* Forward the fourth R9 NRC pointer to8DA10 and return its meaningful R10 admission result.
   Preserve fourth R9argumentandmeaningfulreturn from8DA10;currentvoid/3args hides NRCwrite. */

uint f33_dcm_check_communication_application_admission
               (uchar subfunction,uchar communication_type,ushort node,uchar *nrc)

{
  uint uVar1;
  
  uVar1 = f33_admit_application_communication_request(subfunction,communication_type,node,nrc);
  return uVar1;
}



uint FUN_00097128(uchar param_1,uchar param_2)

{
  return f33_apply_and_complete_communication_policy_request(param_1,param_2);
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_97138(void)

{
  return;
}



/* Constant source: return 0; shape-classified from the canonical corpus. Callers receive this
   literal directly; its meaning is not recovered. */

undefined4 f33_return_const_0_9713a(void)

{
  return 0;
}



/* Constant source: return 0xb; shape-classified from the canonical corpus. Callers receive this
   literal directly; its meaning is not recovered. */

undefined4 f33_return_const_b_9713e(void)

{
  return 0xb;
}



/* ConfiguredSID28sub0/session3 wrapper; shared9701C lifetime, only communicationByte01 admitted by
   image. */

uint f33_dcm_communication_enable_rx_tx(uchar operation,F33DcmMessageContext *message)

{
  uint uVar1;
  
  uVar1 = f33_dcm_dispatch_communication_control_lifetime(operation,message,'\0');
  return uVar1;
}



/* ConfiguredSID28sub1/session3; application effect is retained8196Tx-policy request, not controller
   confirmation or7F97. */

uint f33_dcm_communication_enable_rx_disable_tx(uchar operation,F33DcmMessageContext *message)

{
  uint uVar1;
  
  uVar1 = f33_dcm_dispatch_communication_control_lifetime(operation,message,'\x01');
  return uVar1;
}



/* Configuredsub3 name describes request only; actual local actionusesmappedmodebit0 and does not
   independently implement Rxdisable. */

uint f33_dcm_communication_disable_rx_tx_request(uchar operation,F33DcmMessageContext *message)

{
  uint uVar1;
  
  uVar1 = f33_dcm_dispatch_communication_control_lifetime(operation,message,'\x03');
  return uVar1;
}



bool FUN_00097172(ushort param_1,undefined2 *param_2)

{
  ushort uVar1;
  uint uVar2;
  uint uVar3;
  uint uVar4;
  
  if (DAT_00026492 != 0) {
    uVar4 = 0;
    uVar3 = (uint)(ushort)(DAT_00026492 - 1);
    if ((DAT_00026918 <= param_1) && (uVar1 = DAT_00026918, param_1 <= (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0x26918u + (uint32_t)(uVar3 * 4) * 2u))))))
    {
      while( true ) {
        if (uVar1 == param_1) {
          *param_2 = (short)uVar4;
          return (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x2691bu + (uint32_t)(uVar4 * 8) * 1u)))) != '\x01';
        }
        if (uVar3 <= uVar4) break;
        uVar2 = uVar3 + uVar4 >> 1;
        if ((*((volatile uint16_t *)camry_host_ptr((uint32_t)(0x26918u + (uint32_t)(uVar2 * 4) * 2u)))) < param_1) {
          uVar4 = uVar2 + 1 & 0xffff;
          uVar2 = uVar3;
        }
        uVar3 = uVar2;
        uVar1 = (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0x26918u + (uint32_t)(uVar4 * 4) * 2u))));
      }
    }
  }
  return true;
}



undefined4 FUN_000971e8(ushort param_1)

{
  int iVar1;
  uint uVar2;
  uint32_t puVar3;
  uint uVar4;
  uchar uStack_11;
  
  puVar3 = 0x23dfcu;
  uVar4 = (uint)param_1;
  if (DAT_00026492 <= uVar4) {
    return 1;
  }
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x269b9u + (uint32_t)((short)param_1 * 0xf) * 1u)))) != '\0') {
    if (1 < *(ushort *)(((undefined *)camry_host_ptr(0x264bcu)) + uVar4 * 2)) {
      return 1;
    }
    iVar1 = (uint)*(ushort *)(((undefined *)camry_host_ptr(0x264bcu)) + uVar4 * 2) * 2;
    if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x2624du + (uint32_t)(iVar1) * 1u)))) != '\0') {
      uStack_11 = '\0';
      f33_dcm_get_session(&uStack_11);
      uVar2 = 0;
      while( true ) {
        if ((byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x2624du + (uint32_t)(iVar1) * 1u)))) <= uVar2) {
          return 1;
        }
        if ((*((uchar *)camry_host_ptr((uint32_t)(*(int *)(uVar2 * 4 + *(int *)(*(int *)(puVar3 + uVar4 * 8 + 0x2b20) + 4)) + 1
                      )))) == uStack_11) break;
        uVar2 = uVar2 + 1 & 0xffff;
      }
    }
  }
  return 0;
}



undefined4 FUN_0009726c(ushort param_1)

{
  int iVar1;
  uint uVar2;
  uint32_t puVar3;
  uint uVar4;
  uchar uStack_11;
  
  puVar3 = 0x23dfcu;
  uVar4 = (uint)param_1;
  if (DAT_00026492 <= uVar4) {
    return 1;
  }
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x269b9u + (uint32_t)((short)param_1 * 0xf) * 1u)))) != '\0') {
    if (1 < *(ushort *)(((undefined *)camry_host_ptr(0x264bcu)) + uVar4 * 2)) {
      return 1;
    }
    iVar1 = (uint)*(ushort *)(((undefined *)camry_host_ptr(0x264bcu)) + uVar4 * 2) * 2;
    if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x2624cu + (uint32_t)(iVar1) * 1u)))) != '\0') {
      uStack_11 = '\0';
      f33_dcm_get_security_level(&uStack_11);
      uVar2 = 0;
      while( true ) {
        if ((byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x2624cu + (uint32_t)(iVar1) * 1u)))) <= uVar2) {
          return 1;
        }
        if ((*((uchar *)camry_host_ptr((uint32_t)(*(int *)(uVar2 * 4 + **(int **)(puVar3 + uVar4 * 8 + 0x2b20)) + 0x14)))) ==
            uStack_11) break;
        uVar2 = uVar2 + 1 & 0xffff;
      }
    }
  }
  return 0;
}



/* 269B9+15*index offsets4/9/1 forcontrols1/2/3;0supported,1rejected;indexbound26492. */

uint f33_diag_routine_control_type_supported(ushort configured_index,uchar control_type)

{
  char cVar1;
  uint uVar2;
  
  uVar2 = 1;
  if (configured_index < DAT_00026492) {
    if (control_type == '\x01') {
      cVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x269bdu + (uint32_t)((short)configured_index * 0xf) * 1u))));
    }
    else if (control_type == '\x02') {
      cVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x269c2u + (uint32_t)((short)configured_index * 0xf) * 1u))));
    }
    else {
      if (control_type != '\x03') {
        return uVar2;
      }
      cVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x269bau + (uint32_t)((short)configured_index * 0xf) * 1u))));
    }
    if (cVar1 == '\0') {
      return uVar2;
    }
    uVar2 = 0;
  }
  return uVar2;
}



bool FUN_0009733a(int param_1,ushort param_2,char param_3)

{
  undefined **ppuVar1;
  uint uVar2;
  int iVar3;
  int iVar4;
  uint uVar5;
  undefined *puVar6;
  undefined *puVar7;
  
  uVar5 = (uint)param_2;
  if (DAT_00026492 <= uVar5) {
    return true;
  }
  uVar2 = 0;
  if (param_3 == '\x01') {
    if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x269bfu + (uint32_t)((short)param_2 * 0xf) * 1u)))) == 0) goto LAB_000973ce;
    ppuVar1 = &PTR_DAT_00026698 + uVar5;
    iVar3 = (short)(ushort)(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x269bfu + (uint32_t)((short)param_2 * 0xf) * 1u)))) * 6;
    iVar4 = iVar3 + -6;
    puVar6 = *ppuVar1;
    puVar7 = *ppuVar1;
    if ((*ppuVar1)[iVar3 + -5] == '\a') goto LAB_000973be;
LAB_000973b0:
    puVar6 = puVar6 + iVar4;
    uVar5 = (uint)(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x261d8u + (uint32_t)((byte)puVar7[iVar4 + 1]) * 1u))));
  }
  else {
    if ((param_3 != '\x02') || ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x269c4u + (uint32_t)((short)param_2 * 0xf) * 1u)))) == 0)) goto LAB_000973ce;
    ppuVar1 = &PTR_DAT_000267d8 + uVar5;
    iVar3 = (short)(ushort)(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x269c4u + (uint32_t)((short)param_2 * 0xf) * 1u)))) * 6;
    iVar4 = iVar3 + -6;
    puVar6 = *ppuVar1;
    puVar7 = *ppuVar1;
    if ((*ppuVar1)[iVar3 + -5] != '\a') goto LAB_000973b0;
LAB_000973be:
    puVar6 = puVar6 + iVar4;
    uVar5 = (uint)*(ushort *)(puVar7 + iVar4 + 2);
  }
  uVar2 = uVar5 + *(ushort *)(puVar6 + 4) + 7 >> 3;
LAB_000973ce:
  return uVar2 + 3 != (*((int *)camry_host_ptr((uint32_t)(param_1 + 4))));
}



bool FUN_000973dc(int param_1,ushort param_2,char param_3)

{
  undefined **ppuVar1;
  char cVar2;
  uint uVar3;
  int iVar4;
  uint uVar5;
  undefined *puVar6;
  undefined *puVar7;
  
  uVar5 = (uint)param_2;
  if (DAT_00026492 <= uVar5) {
    return true;
  }
  uVar3 = 0;
  if (param_3 == '\x01') {
    if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x269c1u + (uint32_t)((short)param_2 * 0xf) * 1u)))) == 0) goto LAB_000974a2;
    ppuVar1 = &PTR_DAT_000266e8 + uVar5;
    iVar4 = (short)(ushort)(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x269c1u + (uint32_t)((short)param_2 * 0xf) * 1u)))) * 6;
    cVar2 = (*ppuVar1)[iVar4 + -5];
    puVar6 = *ppuVar1;
    puVar7 = *ppuVar1;
  }
  else if (param_3 == '\x02') {
    if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x269c6u + (uint32_t)((short)param_2 * 0xf) * 1u)))) == 0) goto LAB_000974a2;
    ppuVar1 = &PTR_DAT_00026828 + uVar5;
    iVar4 = (short)(ushort)(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x269c6u + (uint32_t)((short)param_2 * 0xf) * 1u)))) * 6;
    cVar2 = (*ppuVar1)[iVar4 + -5];
    puVar6 = *ppuVar1;
    puVar7 = *ppuVar1;
  }
  else {
    if ((param_3 != '\x03') || ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x269bcu + (uint32_t)((short)param_2 * 0xf) * 1u)))) == 0)) goto LAB_000974a2;
    ppuVar1 = &PTR_DAT_000265f8 + uVar5;
    iVar4 = (short)(ushort)(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x269bcu + (uint32_t)((short)param_2 * 0xf) * 1u)))) * 6;
    cVar2 = (*ppuVar1)[iVar4 + -5];
    puVar6 = *ppuVar1;
    puVar7 = *ppuVar1;
  }
  if (cVar2 == '\a') {
    uVar5 = (uint)*(ushort *)(puVar7 + iVar4 + -4);
  }
  else {
    uVar5 = (uint)(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x261d8u + (uint32_t)((byte)puVar7[iVar4 + -5]) * 1u))));
  }
  uVar3 = uVar5 + *(ushort *)(puVar6 + iVar4 + -2) + 7 >> 3;
LAB_000974a2:
  return (*((uint *)camry_host_ptr((uint32_t)(param_1 + 0x14)))) < uVar3 + 3;
}



void FUN_0009767c(ushort param_1,char param_2,int param_3)

{
  char *pcVar1;
  undefined2 uVar2;
  undefined **ppuVar3;
  uint uVar4;
  undefined *puVar5;
  undefined *puVar6;
  char cVar7;
  short sVar8;
  uint uVar9;
  undefined1 uVar10;
  uint uVar11;
  undefined1 uVar12;
  undefined **ppuVar13;
  int iVar14;
  
  uVar4 = (uint)param_1;
  if (uVar4 < DAT_00026492) {
    iVar14 = (short)param_1 * 0xf;
    if (param_2 == '\x01') {
      uVar9 = (uint)(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x269c1u + (uint32_t)(iVar14) * 1u))));
      ppuVar3 = &PTR_DAT_000266e8;
      ppuVar13 = &PTR_DAT_00026788;
    }
    else if (param_2 == '\x02') {
      uVar9 = (uint)(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x269c6u + (uint32_t)(iVar14) * 1u))));
      ppuVar3 = &PTR_DAT_00026828;
      ppuVar13 = &PTR_DAT_000268c8;
    }
    else {
      uVar9 = (uint)(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x269bcu + (uint32_t)(iVar14) * 1u))));
      ppuVar3 = &PTR_DAT_000265f8;
      ppuVar13 = &PTR_DAT_00026648;
    }
    puVar6 = ppuVar3[uVar4];
    puVar5 = ppuVar13[uVar4];
    for (uVar4 = 0; uVar4 < uVar9; uVar4 = uVar4 + 1 & 0xff) {
      pcVar1 = puVar6 + (short)uVar4 * 6;
      iVar14 = ((int)(uint)*(ushort *)(pcVar1 + 4) >> 3) + 3;
      if (pcVar1[1] != '\a') {
        if (pcVar1[1] == '\0') {
          (*((byte *)camry_host_ptr((uint32_t)(DAT_febe5e20 + iVar14)))) =
               (*((byte *)camry_host_ptr((uint32_t)(DAT_febe5e20 + iVar14)))) |
               (byte)((*((int *)camry_host_ptr((uint32_t)(uVar4 * 4 + param_3)))) << (*(ushort *)(pcVar1 + 4) & 7));
        }
        else if ((pcVar1[1] == '\x06') || (pcVar1[1] == '\x03')) {
          (*((char *)camry_host_ptr((uint32_t)(DAT_febe5e20 + iVar14)))) = (char)(*((undefined4 *)camry_host_ptr((uint32_t)(uVar4 * 4 + param_3))));
        }
        else {
          if ((puVar5[uVar4 * 2] == '\0') || (*pcVar1 == '\x02')) {
            cVar7 = '\x01';
          }
          else {
            cVar7 = *pcVar1;
          }
          if ((pcVar1[1] == '\x04') || (pcVar1[1] == '\x01')) {
            uVar2 = (*((undefined2 *)camry_host_ptr((uint32_t)(uVar4 * 4 + param_3))));
            uVar12 = (undefined1)((ushort)uVar2 >> 8);
            uVar10 = (undefined1)uVar2;
            if (cVar7 == '\x01') {
              (*((undefined1 *)camry_host_ptr((uint32_t)(DAT_febe5e20 + iVar14)))) = uVar10;
              (*((undefined1 *)camry_host_ptr((uint32_t)(DAT_febe5e20 + iVar14 + 1)))) = uVar12;
            }
            else {
              (*((undefined1 *)camry_host_ptr((uint32_t)(DAT_febe5e20 + iVar14)))) = uVar12;
              (*((undefined1 *)camry_host_ptr((uint32_t)(DAT_febe5e20 + iVar14 + 1)))) = uVar10;
            }
          }
          else {
            uVar11 = (*((uint *)camry_host_ptr((uint32_t)(uVar4 * 4 + param_3))));
            uVar10 = (undefined1)(uVar11 >> 0x10);
            uVar12 = (undefined1)(uVar11 >> 8);
            if (cVar7 == '\x01') {
              (*((undefined1 *)camry_host_ptr((uint32_t)(DAT_febe5e20 + iVar14)))) = (char)uVar11;
              uVar11 = uVar11 >> 0x18;
              (*((undefined1 *)camry_host_ptr((uint32_t)(DAT_febe5e20 + iVar14 + 1)))) = uVar12;
              (*((undefined1 *)camry_host_ptr((uint32_t)(DAT_febe5e20 + iVar14 + 2)))) = uVar10;
            }
            else {
              (*((undefined1 *)camry_host_ptr((uint32_t)(DAT_febe5e20 + iVar14)))) = (char)(uVar11 >> 0x18);
              (*((undefined1 *)camry_host_ptr((uint32_t)(DAT_febe5e20 + iVar14 + 1)))) = uVar10;
              (*((undefined1 *)camry_host_ptr((uint32_t)(DAT_febe5e20 + iVar14 + 2)))) = uVar12;
            }
            (*((char *)camry_host_ptr((uint32_t)(DAT_febe5e20 + iVar14 + 3)))) = (char)uVar11;
          }
        }
      }
    }
    if (uVar9 != 0) {
      sVar8 = (short)uVar9;
      if (puVar6[sVar8 * 6 + -5] == '\a') {
        uVar4 = (uint)*(ushort *)(puVar6 + sVar8 * 6 + -4);
      }
      else {
        uVar4 = (uint)(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x261d8u + (uint32_t)((byte)puVar6[sVar8 * 6 + -5]) * 1u))));
      }
      DAT_febe5e24 = DAT_febe5e24 + (uVar4 + *(ushort *)(puVar6 + sVar8 * 6 + -2) + 7 >> 3);
    }
  }
  return;
}



undefined4 FUN_00097822(char param_1,undefined4 param_2,ushort param_3,char param_4)

{
  uint uVar1;
  uint uVar2;
  uint32_t puVar3;
  int iVar4;
  undefined4 uVar5;
  uchar uStack_31;
  undefined4 auStack_30 [4];
  undefined4 uStack_20;
  undefined4 uStack_1c;
  undefined2 uStack_18;
  byte bStack_16;
  undefined1 uStack_15;
  
  puVar3 = 0xfebeb800u;
  uVar5 = 0;
  if (param_3 < DAT_00026492) {
    uStack_31 = '\0';
    uVar2 = 0;
    do {
      uVar1 = uVar2 + 1;
      auStack_30[uVar2] = 0;
      uVar2 = uVar1;
    } while (uVar1 < 4);
    bStack_16 = 0;
    uStack_15 = 0;
    uStack_20 = 0;
    uStack_1c = 0;
    uStack_18 = 0;
    if (param_1 != '\x02') {
      puVar3 = 0xfebeb800u;
      FUN_000974b0(((int *)camry_host_ptr((uint32_t)(param_2))), param_3, param_4, camry_host_addr(auStack_30));
    }
    if (param_4 == '\x01') {
      iVar4 = FUN_0009847a((uint)(ushort)param_3,  auStack_30,  (uint)(byte)param_1, camry_host_addr(&uStack_31));
    }
    else if (param_4 == '\x02') {
      iVar4 = FUN_00098590((uint)(ushort)param_3, camry_host_addr(auStack_30),  (uint)(byte)param_1, camry_host_addr(&uStack_31));
    }
    else {
      iVar4 = FUN_000982e4(param_3, auStack_30, param_1, camry_host_addr(&uStack_31));
    }
    if (param_1 != '\x02') {
      if (iVar4 == 0) {
        FUN_000955b6(0);
        FUN_0009767c(param_3, param_4, camry_host_addr(auStack_30 + bStack_16));
        f33_dcm_report_positive_response(((F33DcmMessageContext *)camry_host_ptr((uint32_t)(puVar3 + -0x59e8))));
      }
      else if (iVar4 == 1) {
        FUN_000955b6(0);
        f33_dcm_report_negative_or_pending(((F33DcmMessageContext *)camry_host_ptr((uint32_t)(puVar3 + -0x59e8))),uStack_31);
      }
      else if (iVar4 == 10) {
        FUN_000955b6(1);
        f33_dcm_enqueue_event('\x06');
        uVar5 = 10;
      }
      else if (iVar4 == 0xc) {
        FUN_000955b6(1);
        f33_dcm_report_negative_or_pending(((F33DcmMessageContext *)camry_host_ptr((uint32_t)(puVar3 + -0x59e8))),'x');
        uVar5 = 0xc;
      }
      else {
        FUN_000955b6(0);
      }
    }
  }
  return uVar5;
}



undefined4 FUN_000979a2(undefined4 *param_1)

{
  byte bVar1;
  undefined4 *puVar2;
  uint32_t puVar3;
  int iVar4;
  uint uVar5;
  undefined4 uVar6;
  undefined4 uVar7;
  undefined4 *puVar8;
  byte *pbVar9;
  char local_14;
  uchar uStack_13;
  ushort uStack_12;
  
  puVar3 = 0xfebeb800u;
  uStack_12 = 0;
  uStack_13 = '\0';
  uVar7 = 0;
  local_14 = '\0';
  FUN_0009560e(0);
  puVar2 = ((undefined4 *)camry_host_ptr((uint32_t)(puVar3 + -0x59e8)));
  puVar8 = param_1;
  do {
    uVar6 = *puVar8;
    puVar8 = puVar8 + 1;
    *puVar2 = uVar6;
    puVar2 = puVar2 + 1;
  } while ((uintptr_t)(param_1 + 7)!=(uintptr_t)(puVar8));
  FUN_000955b6(0);
  if ((uint)param_1[1] < 3) {
    uStack_13 = '\x13';
  }
  else {
    pbVar9 = (byte *)*param_1;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-22999))))) = *pbVar9 >> 7;
    iVar4 = FUN_00097172(CONCAT11(pbVar9[1],pbVar9[2]),&uStack_12);
    if ((iVar4 == 0) && (iVar4 = FUN_000971e8(uStack_12), iVar4 == 0)) {
      iVar4 = FUN_0009726c(uStack_12);
      if (iVar4 == 0) {
        bVar1 = *(byte *)*param_1;
        uVar5 = f33_diag_routine_control_type_supported(uStack_12,bVar1 & 0x7f);
        if (uVar5 == 0) {
          (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x59ea))))) = bVar1 & 0x7f;
          (*((ushort *)camry_host_ptr((uint32_t)(puVar3 + -0x59ec)))) = uStack_12;
          uVar7 = FUN_00097912(camry_host_addr(param_1), &uStack_13, &local_14);
          goto LAB_00097a7a;
        }
        uStack_13 = '\x12';
      }
      else {
        uStack_13 = '3';
      }
    }
    else {
      uStack_13 = '1';
    }
  }
  local_14 = '\x01';
LAB_00097a7a:
  if (local_14 != '\0') {
    f33_dcm_report_negative_or_pending(((F33DcmMessageContext *)camry_host_ptr((uint32_t)(puVar3 + -0x59e8))),uStack_13);
  }
  return uVar7;
}



void FUN_00097a94(void)

{
  uint32_t puVar1;
  int iVar2;
  
  puVar1 = 0xfebeb800u;
  iVar2 = FUN_000955bc();
  if (iVar2 == 1) {
    FUN_00097822(2, camry_host_addr(((undefined *)camry_host_ptr((uint32_t)(puVar1 + -0x59e8)))),  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x59ec)))),  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x59ea))))));
    FUN_000955b6(0);
  }
  f33_dcm_invalidate_queued_event('\x06','\0');
  FUN_0009560e(1);
  return;
}



undefined4 FUN_00097aca(void)

{
  return FUN_00097822(3, camry_host_addr(((undefined *)camry_host_ptr(0xfebe5e18u))), DAT_febe5e14, DAT_febe5e16);
}



undefined4 FUN_00097ae4(char param_1,undefined4 param_2)

{
  undefined4 uVar1;
  
  if (param_1 == '\0') {
    uVar1 = FUN_000979a2(((undefined4 *)camry_host_ptr((uint32_t)(param_2))));
  }
  else {
    uVar1 = 0;
    if (param_1 == '\x02') {
      FUN_00097a94();
    }
    else if (param_1 == '\x03') {
      uVar1 = FUN_00097aca();
    }
  }
  return uVar1;
}



undefined4 FUN_00097b12(void)

{
  return FUN_00097822(1, camry_host_addr(((undefined *)camry_host_ptr(0xfebe5e18u))), DAT_febe5e14, DAT_febe5e16);
}



/* UDS routine wrapper: guards on the two valid routine-control subfunctions, delegates to the
   application-class routine helper with a fixed class literal, and diverts other subfunctions to
   the negative-response path (8B83C). Shape-verified. */

uint f33_diag_routine_class03_97b2c(byte param_1,uchar *param_2,uchar *param_3)

{
  uint uVar1;
  ushort uStack_a;
  
  uStack_a = 0;
  if (param_1 < 2) {
    uVar1 = f33_diag_routine_application_class('\x03',0,0,param_2,&uStack_a,param_3);
  }
  else {
    uVar1 = 0;
    FUN_0008b83c();
  }
  return uVar1;
}



/* UDS routine wrapper: guards on the two valid routine-control subfunctions, delegates to the
   application-class routine helper with a fixed class literal, and diverts other subfunctions to
   the negative-response path (8B83C). Shape-verified. */

uint f33_diag_routine_class03_97b60(byte param_1,uchar *param_2,uchar *param_3)

{
  uint uVar1;
  ushort uStack_a;
  
  uStack_a = 0;
  if (param_1 < 2) {
    uVar1 = f33_diag_routine_application_class('\x03',1,0,param_2,&uStack_a,param_3);
  }
  else {
    uVar1 = 0;
    FUN_0008b83c();
  }
  return uVar1;
}



/* UDS routine wrapper: guards on the two valid routine-control subfunctions, delegates to the
   application-class routine helper with a fixed class literal, and diverts other subfunctions to
   the negative-response path (8B83C). Shape-verified. */

uint f33_diag_routine_class03_97b94(byte param_1,uchar *param_2,uchar *param_3)

{
  uint uVar1;
  ushort uStack_a;
  
  uStack_a = 0;
  if (param_1 < 2) {
    uVar1 = f33_diag_routine_application_class('\x03',2,0,param_2,&uStack_a,param_3);
  }
  else {
    uVar1 = 0;
    FUN_0008b83c();
  }
  return uVar1;
}



/* UDS routine wrapper: guards on the two valid routine-control subfunctions, delegates to the
   application-class routine helper with a fixed class literal, and diverts other subfunctions to
   the negative-response path (8B83C). Shape-verified. */

uint f33_diag_routine_class03_97bc8(byte param_1,uchar *param_2,uchar *param_3)

{
  uint uVar1;
  ushort uStack_a;
  
  uStack_a = 0;
  if (param_1 < 2) {
    uVar1 = f33_diag_routine_application_class('\x03',3,0,param_2,&uStack_a,param_3);
  }
  else {
    uVar1 = 0;
    FUN_0008b83c();
  }
  return uVar1;
}



/* UDS routine wrapper: guards on the two valid routine-control subfunctions, delegates to the
   application-class routine helper with a fixed class literal, and diverts other subfunctions to
   the negative-response path (8B83C). Shape-verified. */

uint f33_diag_routine_class03_97bfc(byte param_1,uchar *param_2,uchar *param_3)

{
  uint uVar1;
  ushort uStack_a;
  
  uStack_a = 0;
  if (param_1 < 2) {
    uVar1 = f33_diag_routine_application_class('\x03',4,0,param_2,&uStack_a,param_3);
  }
  else {
    uVar1 = 0;
    FUN_0008b83c();
  }
  return uVar1;
}



/* UDS routine wrapper: guards on the two valid routine-control subfunctions, delegates to the
   application-class routine helper with a fixed class literal, and diverts other subfunctions to
   the negative-response path (8B83C). Shape-verified. */

uint f33_diag_routine_class03_97c30(byte param_1,uchar *param_2,uchar *param_3)

{
  uint uVar1;
  ushort uStack_a;
  
  uStack_a = 0;
  if (param_1 < 2) {
    uVar1 = f33_diag_routine_application_class('\x03',5,0,param_2,&uStack_a,param_3);
  }
  else {
    uVar1 = 0;
    FUN_0008b83c();
  }
  return uVar1;
}



/* UDS routine wrapper: guards on the two valid routine-control subfunctions, delegates to the
   application-class routine helper with a fixed class literal, and diverts other subfunctions to
   the negative-response path (8B83C). Shape-verified. */

uint f33_diag_routine_class03_97c64(byte param_1,uchar *param_2,uchar *param_3)

{
  uint uVar1;
  ushort uStack_a;
  
  uStack_a = 0;
  if (param_1 < 2) {
    uVar1 = f33_diag_routine_application_class('\x03',6,0,param_2,&uStack_a,param_3);
  }
  else {
    uVar1 = 0;
    FUN_0008b83c();
  }
  return uVar1;
}



undefined4 FUN_00097c98(char param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  undefined4 uVar1;
  
  if (param_1 == '\0') {
    uVar1 = FUN_0008ba2c(param_2, 0x31, ((uchar *)camry_host_ptr((uint32_t)(param_4))));
  }
  else {
    uVar1 = 0;
    FUN_0008b83c();
  }
  return uVar1;
}



/* UDS routine wrapper: guards on the two valid routine-control subfunctions, delegates to the
   application-class routine helper with a fixed class literal, and diverts other subfunctions to
   the negative-response path (8B83C). Shape-verified. */

uint f33_diag_routine_class03_97cbc(byte param_1,uchar *param_2,uchar *param_3)

{
  uint uVar1;
  ushort uStack_a;
  
  uStack_a = 0;
  if (param_1 < 2) {
    uVar1 = f33_diag_routine_application_class('\x03',10,0,param_2,&uStack_a,param_3);
  }
  else {
    uVar1 = 0;
    FUN_0008b83c();
  }
  return uVar1;
}



/* UDS routine wrapper: guards on the two valid routine-control subfunctions, delegates to the
   application-class routine helper with a fixed class literal, and diverts other subfunctions to
   the negative-response path (8B83C). Shape-verified. */

uint f33_diag_routine_class03_97cf0(byte param_1,uchar *param_2,uchar *param_3)

{
  uint uVar1;
  ushort uStack_a;
  
  uStack_a = 0;
  if (param_1 < 2) {
    uVar1 = f33_diag_routine_application_class('\x03',0xb,0,param_2,&uStack_a,param_3);
  }
  else {
    uVar1 = 0;
    FUN_0008b83c();
  }
  return uVar1;
}



/* UDS routine wrapper: guards on the two valid routine-control subfunctions, delegates to the
   application-class routine helper with a fixed class literal, and diverts other subfunctions to
   the negative-response path (8B83C). Shape-verified. */

uint f33_diag_routine_class03_97d24(byte param_1,uchar *param_2,uchar *param_3)

{
  uint uVar1;
  ushort uStack_a;
  
  uStack_a = 0;
  if (param_1 < 2) {
    uVar1 = f33_diag_routine_application_class('\x03',0xc,0,param_2,&uStack_a,param_3);
  }
  else {
    uVar1 = 0;
    FUN_0008b83c();
  }
  return uVar1;
}



/* UDS routine wrapper: guards on the two valid routine-control subfunctions, delegates to the
   application-class routine helper with a fixed class literal, and diverts other subfunctions to
   the negative-response path (8B83C). Shape-verified. */

uint f33_diag_routine_class03_97d58(byte param_1,uchar *param_2,uchar *param_3)

{
  uint uVar1;
  ushort uStack_a;
  
  uStack_a = 0;
  if (param_1 < 2) {
    uVar1 = f33_diag_routine_application_class('\x03',0xd,0,param_2,&uStack_a,param_3);
  }
  else {
    uVar1 = 0;
    FUN_0008b83c();
  }
  return uVar1;
}



/* UDS routine wrapper: guards on the two valid routine-control subfunctions, delegates to the
   application-class routine helper with a fixed class literal, and diverts other subfunctions to
   the negative-response path (8B83C). Shape-verified. */

uint f33_diag_routine_class03_97d8c(byte param_1,uchar *param_2,uchar *param_3)

{
  uint uVar1;
  ushort uStack_a;
  
  uStack_a = 0;
  if (param_1 < 2) {
    uVar1 = f33_diag_routine_application_class('\x03',0xe,0,param_2,&uStack_a,param_3);
  }
  else {
    uVar1 = 0;
    FUN_0008b83c();
  }
  return uVar1;
}



/* UDS routine wrapper: guards on the two valid routine-control subfunctions, delegates to the
   application-class routine helper with a fixed class literal, and diverts other subfunctions to
   the negative-response path (8B83C). Shape-verified. */

uint f33_diag_routine_class03_97dc0(byte param_1,uchar *param_2,uchar *param_3)

{
  uint uVar1;
  ushort uStack_a;
  
  uStack_a = 0;
  if (param_1 < 2) {
    uVar1 = f33_diag_routine_application_class('\x03',0xf,0,param_2,&uStack_a,param_3);
  }
  else {
    uVar1 = 0;
    FUN_0008b83c();
  }
  return uVar1;
}



/* UDS routine wrapper: guards on the two valid routine-control subfunctions, delegates to the
   application-class routine helper with a fixed class literal, and diverts other subfunctions to
   the negative-response path (8B83C). Shape-verified. */

uint f33_diag_routine_class03_97df4(byte param_1,uchar *param_2,uchar *param_3)

{
  uint uVar1;
  ushort uStack_a;
  
  uStack_a = 0;
  if (param_1 < 2) {
    uVar1 = f33_diag_routine_application_class('\x03',0x10,0,param_2,&uStack_a,param_3);
  }
  else {
    uVar1 = 0;
    FUN_0008b83c();
  }
  return uVar1;
}



/* UDS routine wrapper: guards on the two valid routine-control subfunctions, delegates to the
   application-class routine helper with a fixed class literal, and diverts other subfunctions to
   the negative-response path (8B83C). Shape-verified. */

uint f33_diag_routine_class03_97e2a(byte param_1,uchar *param_2,uchar *param_3)

{
  uint uVar1;
  ushort uStack_a;
  
  uStack_a = 0;
  if (param_1 < 2) {
    uVar1 = f33_diag_routine_application_class('\x03',0x11,0,param_2,&uStack_a,param_3);
  }
  else {
    uVar1 = 0;
    FUN_0008b83c();
  }
  return uVar1;
}



/* UDS routine wrapper: guards on the two valid routine-control subfunctions, delegates to the
   application-class routine helper with a fixed class literal, and diverts other subfunctions to
   the negative-response path (8B83C). Shape-verified. */

uint f33_diag_routine_class03_97e60(byte param_1,uchar *param_2,uchar *param_3)

{
  uint uVar1;
  ushort uStack_a;
  
  uStack_a = 0;
  if (param_1 < 2) {
    uVar1 = f33_diag_routine_application_class('\x03',0x12,0,param_2,&uStack_a,param_3);
  }
  else {
    uVar1 = 0;
    FUN_0008b83c();
  }
  return uVar1;
}



/* UDS routine wrapper: guards on the two valid routine-control subfunctions, delegates to the
   application-class routine helper with a fixed class literal, and diverts other subfunctions to
   the negative-response path (8B83C). Shape-verified. */

uint f33_diag_routine_class01_97e96(byte param_1,uchar *param_2,ushort *param_3,uchar *param_4)

{
  uint uVar1;
  
  if (param_1 < 2) {
    uVar1 = f33_diag_routine_application_class('\x01',0,0,param_2,param_3,param_4);
  }
  else {
    uVar1 = 0;
    FUN_0008b83c();
  }
  return uVar1;
}



/* UDS routine wrapper: guards on the two valid routine-control subfunctions, delegates to the
   application-class routine helper with a fixed class literal, and diverts other subfunctions to
   the negative-response path (8B83C). Shape-verified. */

uint f33_diag_routine_class01_97ec2(byte param_1,uchar *param_2,ushort *param_3,uchar *param_4)

{
  uint uVar1;
  
  if (param_1 < 2) {
    uVar1 = f33_diag_routine_application_class('\x01',1,0,param_2,param_3,param_4);
  }
  else {
    uVar1 = 0;
    FUN_0008b83c();
  }
  return uVar1;
}



/* UDS routine wrapper: guards on the two valid routine-control subfunctions, delegates to the
   application-class routine helper with a fixed class literal, and diverts other subfunctions to
   the negative-response path (8B83C). Shape-verified. */

uint f33_diag_routine_class01_97eee(byte param_1,uchar *param_2)

{
  uint uVar1;
  uchar uStack_b;
  ushort uStack_a;
  
  uStack_b = '\0';
  uStack_a = 0;
  if (param_1 < 2) {
    uVar1 = f33_diag_routine_application_class('\x01',2,0,&uStack_b,&uStack_a,param_2);
  }
  else {
    uVar1 = 0;
    FUN_0008b83c();
  }
  return uVar1;
}



uint FUN_00097f24(uint param_1,byte param_2,uchar *param_3)

{
  uint uVar1;
  uchar uStack_b;
  ushort uStack_a;
  
  uStack_b = '\0';
  uStack_a = 0;
  if (param_2 < 2) {
    uVar1 = f33_diag_routine_application_class
                      ('\x01',3,param_1 & 0xffff,&uStack_b,&uStack_a,param_3);
  }
  else {
    uVar1 = 0;
    FUN_0008b83c();
  }
  return uVar1;
}



/* UDS routine wrapper: guards on the two valid routine-control subfunctions, delegates to the
   application-class routine helper with a fixed class literal, and diverts other subfunctions to
   the negative-response path (8B83C). Shape-verified. */

uint f33_diag_routine_class01_97f5c(byte param_1,uchar *param_2)

{
  uint uVar1;
  uchar uStack_b;
  ushort uStack_a;
  
  uStack_b = '\0';
  uStack_a = 0;
  if (param_1 < 2) {
    uVar1 = f33_diag_routine_application_class('\x01',4,0,&uStack_b,&uStack_a,param_2);
  }
  else {
    uVar1 = 0;
    FUN_0008b83c();
  }
  return uVar1;
}



/* UDS routine wrapper: guards on the two valid routine-control subfunctions, delegates to the
   application-class routine helper with a fixed class literal, and diverts other subfunctions to
   the negative-response path (8B83C). Shape-verified. */

uint f33_diag_routine_class01_97f92(byte param_1,uchar *param_2)

{
  uint uVar1;
  uchar uStack_b;
  ushort uStack_a;
  
  uStack_b = '\0';
  uStack_a = 0;
  if (param_1 < 2) {
    uVar1 = f33_diag_routine_application_class('\x01',5,0,&uStack_b,&uStack_a,param_2);
  }
  else {
    uVar1 = 0;
    FUN_0008b83c();
  }
  return uVar1;
}



/* UDS routine wrapper: guards on the two valid routine-control subfunctions, delegates to the
   application-class routine helper with a fixed class literal, and diverts other subfunctions to
   the negative-response path (8B83C). Shape-verified. */

uint f33_diag_routine_class01_97fc8(byte param_1,uchar *param_2)

{
  uint uVar1;
  uchar uStack_b;
  ushort uStack_a;
  
  uStack_b = '\0';
  uStack_a = 0;
  if (param_1 < 2) {
    uVar1 = f33_diag_routine_application_class('\x01',6,0,&uStack_b,&uStack_a,param_2);
  }
  else {
    uVar1 = 0;
    FUN_0008b83c();
  }
  return uVar1;
}



/* UDS routine wrapper: guards on the two valid routine-control subfunctions, delegates to the
   application-class routine helper with a fixed class literal, and diverts other subfunctions to
   the negative-response path (8B83C). Shape-verified. */

uint f33_diag_routine_class01_97ffe(byte param_1,uchar *param_2)

{
  uint uVar1;
  uchar uStack_b;
  ushort uStack_a;
  
  uStack_b = '\0';
  uStack_a = 0;
  if (param_1 < 2) {
    uVar1 = f33_diag_routine_application_class('\x01',7,0,&uStack_b,&uStack_a,param_2);
  }
  else {
    uVar1 = 0;
    FUN_0008b83c();
  }
  return uVar1;
}



bool FUN_00094cc4(char param_1,uint param_2,uint param_3,int param_4,int param_5)

{
  int iVar1;
  bool bVar2;
  
  bVar2 = true;
  if (PTR_PTR_00026034 != 0) {
    iVar1 = (param_2 & 0xff) * 0xc;
    if (param_1 == '\0') {
      iVar1 = (*((int *)camry_host_ptr((uint32_t)(PTR_PTR_00026034 + iVar1))));
    }
    else {
      iVar1 = (*((int *)camry_host_ptr((uint32_t)(PTR_PTR_00026034 + iVar1 + 4))));
    }
    bVar2 = (uint)((*((int *)camry_host_ptr((uint32_t)((param_3 & 0xff) * 0x10 + iVar1 + 4)))) - param_4) < param_5 - 1U;
  }
  return bVar2;
}

undefined4 FUN_00094d04(char param_1,ushort param_2,uint param_3,char param_4)

{
  int iVar1;
  uint uVar2;
  undefined4 uVar3;
  int iVar4;
  
  uVar3 = 1;
  if (PTR_PTR_00026034 == 0) {
    return uVar3;
  }
  iVar4 = (short)(param_2 & 0xff) * 0xc;
  iVar1 = (param_3 & 0xff) * 0x10;
  if (param_1 == '\0') {
    uVar2 = 0;
    if ((*((char *)camry_host_ptr((uint32_t)(*(int *)(PTR_PTR_00026034 + iVar4) + iVar1 + 0xc)))) != '\0') {
      while( true ) {
        if ((*((byte *)camry_host_ptr((uint32_t)(*(int *)(PTR_PTR_00026034 + iVar4) + iVar1 + 0xc)))) <= uVar2) {
          return uVar3;
        }
        if (param_4 == (*((char *)camry_host_ptr((uint32_t)(*(int *)(*(int *)(PTR_PTR_00026034 + iVar4) + iVar1) + uVar2)))))
        break;
        uVar2 = uVar2 + 1 & 0xff;
      }
    }
  }
  else if ((*((char *)camry_host_ptr((uint32_t)(*(int *)(PTR_PTR_00026034 + iVar4 + 4) + iVar1 + 0xc)))) != '\0') {
    uVar2 = 0;
    while( true ) {
      if ((*((byte *)camry_host_ptr((uint32_t)(*(int *)(PTR_PTR_00026034 + iVar4 + 4) + iVar1 + 0xc)))) <= uVar2) {
        return uVar3;
      }
      if (param_4 == (*((char *)camry_host_ptr((uint32_t)(*(int *)(*(int *)(PTR_PTR_00026034 + iVar4 + 4) + iVar1) + uVar2)))))
      break;
      uVar2 = uVar2 + 1 & 0xff;
    }
    return 0;
  }
  return 0;
}
