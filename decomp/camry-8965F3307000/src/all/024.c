#include "common.h"


int FUN_000900ea(void)

{
  undefined8 uVar1;
  int iVar2;
  char cVar3;
  short sVar4;
  undefined2 uStack_16;
  
  uVar1 = 0xfebeb800;
  uStack_16 = 0;
  sVar4 = 0;
  cVar3 = -0x1f;
  while( true ) {
    thunk_FUN_0006a45e();
    iVar2 = FUN_0008e8a0(0,sVar4,&uStack_16);
    if (iVar2 == 0) {
      cVar3 = (*((char *)camry_host_ptr((uint32_t)((int)uVar1 + -0x6298))));
    }
    thunk_FUN_0006a4c4();
    sVar4 = sVar4 + 1;
    if (iVar2 != 0) break;
    if (cVar3 != -0x5b) {
      iVar2 = FUN_0008fd90(uStack_16);
      if (iVar2 == 0) {
        iVar2 = FUN_0008ffda(uStack_16);
      }
      return iVar2;
    }
  }
  return 0x300;
}



undefined4 FUN_00090146(void)

{
  char cVar1;
  uint32_t puVar2;
  undefined2 uVar3;
  undefined4 uVar4;
  
  puVar2 = 0xfebeb800u;
  uVar4 = 2;
  if (DAT_febe556c != 0) {
    uVar3 = 0;
    puVar2 = 0xfebeb800u;
    thunk_FUN_0006a45e();
    if ((((int8_t)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x6298)))))) == -0x2e) || (((int8_t)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x6298)))))) == -0x4c)) {
      uVar3 = 1;
    }
    (*((undefined2 *)camry_host_ptr((uint32_t)(puVar2 + -0x6296)))) = uVar3;
    thunk_FUN_0006a4c4();
  }
  cVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x6298)))));
  if ((((((cVar1 == -0x6a) || (cVar1 == -0x5b)) || (cVar1 == -0x4c)) ||
       ((cVar1 == -0x3d || (cVar1 == -0x2e)))) || (cVar1 == -0x1f)) &&
     (((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x6297))))) == 'Z' || (((int8_t)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x6297)))))) == -0x5b)))) {
    uVar4 = 0;
  }
  else {
    (*((undefined2 *)camry_host_ptr((uint32_t)(puVar2 + -0x6292)))) = 1;
  }
  if ((*((short *)camry_host_ptr((uint32_t)(puVar2 + -0x6292)))) != 0) {
    uVar4 = 2;
    (*((short *)camry_host_ptr((uint32_t)(puVar2 + -0x6292)))) = (*((short *)camry_host_ptr((uint32_t)(puVar2 + -0x6292)))) + -1;
  }
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar2 + -0x6294)))) = 1;
  return uVar4;
}



/* Protected lower-route forwarding preserves R7 descriptor; application snapshot admission remains
   distinct from MAC/lower transmission completion. */

uint f33_secoc_lower_tx(ushort pdu,F33PduInfo *info)

{
  uint uVar1;
  
  uVar1 = f33_route_secured_lower_tx(pdu,info);
  if (uVar1 == 2) {
    uVar1 = 0x20;
  }
  return uVar1;
}



void FUN_000901e8(undefined2 param_1)

{
  FUN_0008160c(param_1);
  return;
}



void FUN_000901f6(undefined2 param_1)

{
  FUN_00081640(param_1);
  return;
}



void FUN_00090204(undefined2 param_1)

{
  FUN_00081ca6(param_1);
  return;
}



void FUN_00090212(void)

{
  DAT_febe55b8 = 0;
  DAT_febe55ba = 0;
  DAT_febe55bc = 0;
  FUN_00090502();
  return;
}



undefined4 FUN_0009022a(short param_1,undefined2 *param_2)

{
  undefined4 uVar1;
  
  uVar1 = 0;
  if ((DAT_0002583e == 0) && (param_1 == DAT_0002583c)) {
    *param_2 = 0;
    uVar1 = 1;
    param_2[1] = 0;
  }
  return uVar1;
}



void FUN_00090248(short param_1,undefined2 *param_2)

{
  bool bVar1;
  int iVar2;
  short sVar3;
  undefined8 uVar4;
  int iVar5;
  int iVar6;
  uint uVar7;
  short sVar8;
  undefined1 auStack_1c [2];
  undefined2 uStack_1a;
  
  uVar4 = 0x23dfc00000000;
  iVar6 = 0;
  sVar8 = 0;
  uVar7 = 0;
  do {
    iVar5 = (int)((ulonglong)uVar4 >> 0x20);
    if ((*((short *)camry_host_ptr((uint32_t)(iVar5 + 0x1a42)))) == 0) {
      iVar2 = (short)uVar7 * 0x50 + iVar5;
      if (param_1 == (*((short *)camry_host_ptr((uint32_t)(iVar2 + 0x1a5e))))) {
        FUN_0009022a((*((undefined2 *)camry_host_ptr((uint32_t)(iVar5 + 0x1a40)))),auStack_1c);
        *param_2 = uStack_1a;
        bVar1 = (*((char *)camry_host_ptr((uint32_t)(iVar2 + 0x1a55)))) == '\x01';
        sVar3 = sVar8;
        if (bVar1) {
          sVar3 = 0;
        }
        param_2[1] = sVar3;
        if (bVar1) {
          iVar6 = 3;
        }
        else {
          iVar6 = 1;
        }
      }
      if ((*((char *)camry_host_ptr((uint32_t)(iVar2 + 0x1a55)))) != '\x01') {
        sVar8 = sVar8 + 1;
      }
      if (iVar6 != 0) {
        return;
      }
    }
    uVar7 = uVar7 + 1;
    if (2 < uVar7) {
      return;
    }
  } while( true );
}



undefined4 FUN_000902b0(short param_1,undefined2 *param_2)

{
  undefined4 uVar1;
  undefined1 auStack_c [2];
  undefined2 uStack_a;
  
  uVar1 = 0;
  if ((DAT_0002583e == 0) && (param_1 == DAT_00025946)) {
    FUN_0009022a(DAT_0002583c,auStack_c);
    param_2[1] = 0;
    uVar1 = 1;
    *param_2 = uStack_a;
  }
  return uVar1;
}



undefined4
FUN_000903f6(undefined2 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4,
            undefined4 param_5)

{
  int iVar1;
  undefined4 uVar2;
  undefined1 auStack_1c [4];
  undefined4 uStack_18;
  undefined4 uStack_14;
  undefined4 uStack_10;
  undefined4 uStack_c;
  
  uVar2 = 1;
  uStack_14 = param_5;
  uStack_18 = param_4;
  uStack_10 = param_2;
  uStack_c = param_3;
  iVar1 = FUN_000902b0(param_1,auStack_1c);
  if (iVar1 == 1) {
    uVar2 = FUN_000908ba(auStack_1c,&uStack_10,&uStack_18);
  }
  return uVar2;
}



void FUN_0009042a(undefined2 param_1)

{
  int iVar1;
  undefined1 auStack_8 [2];
  undefined2 uStack_6;
  
  iVar1 = FUN_000902b0(param_1,auStack_8);
  if (iVar1 == 1) {
    FUN_00090d42(uStack_6,1);
  }
  return;
}



bool FUN_00090482(undefined2 param_1)

{
  int iVar1;
  undefined2 local_c;
  undefined2 uStack_a;
  
  iVar1 = FUN_0009022a(param_1,&local_c);
  if (iVar1 == 1) {
    FUN_00090e6e(local_c,uStack_a);
  }
  return iVar1 != 1;
}



undefined4 FUN_000904a6(void)

{
  undefined4 uVar1;
  
  if (DAT_febe55b8 == 0) {
    uVar1 = ((void)(0), FUN_00090eac());
  }
  else {
    uVar1 = 0;
  }
  return uVar1;
}



uint FUN_000904c0(void)

{
  uint32_t puVar1;
  uint uVar2;
  
  puVar1 = 0xfebeb800u;
  if (DAT_febe55b8 != 0) {
    DAT_febe55b8 = 0;
  }
  uVar2 = FUN_000904a6();
  if (uVar2 != 0) {
    (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x6246)))) = 1;
    (*((short *)camry_host_ptr((uint32_t)(puVar1 + -0x6244)))) = (short)uVar2;
  }
  if ((*((short *)camry_host_ptr((uint32_t)(puVar1 + -0x6246)))) != 0) {
    uVar2 = (uint)(*((ushort *)camry_host_ptr((uint32_t)(puVar1 + -0x6244))));
    (*((short *)camry_host_ptr((uint32_t)(puVar1 + -0x6246)))) = (*((short *)camry_host_ptr((uint32_t)(puVar1 + -0x6246)))) + -1;
  }
  (*((short *)camry_host_ptr((uint32_t)(puVar1 + -0x6248)))) = (*((short *)camry_host_ptr((uint32_t)(puVar1 + -0x6248)))) + 1;
  return uVar2;
}



void FUN_00090502(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  f33_memzero(((undefined *)camry_host_ptr(0xfebe55c0u)),8);
  f33_memzero(((undefined *)camry_host_ptr((uint32_t)(puVar1 + -0x6238))), 8);
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x6228)))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6226))))) = 0;
  (*((uint *)camry_host_ptr((uint32_t)(puVar1 + -0x6230)))) = ~(*((uint *)camry_host_ptr((uint32_t)(puVar1 + -0x6240))));
  (*((uint *)camry_host_ptr((uint32_t)(puVar1 + -0x622c)))) = ~(*((uint *)camry_host_ptr((uint32_t)(puVar1 + -0x623c))));
  f33_memzero(((undefined *)camry_host_ptr((uint32_t)(puVar1 + -0x61f4))), 0xc);
  f33_memzero(((undefined *)camry_host_ptr((uint32_t)(puVar1 + -0x61e8))), 0xc);
  f33_memzero(((undefined *)camry_host_ptr((uint32_t)(puVar1 + -0x6224))), 0x18);
  f33_memzero(((undefined *)camry_host_ptr((uint32_t)(puVar1 + -0x620c))), 0x18);
  return;
}



undefined4 FUN_000905de(short param_1,uchar *param_2,uint *param_3)

{
  uint32_t puVar1;
  undefined4 uVar2;
  F33FreshnessWire local_18;
  
  puVar1 = 0xfebeb800u;
  uVar2 = 1;
  if ((((param_1 == 0) && ((uintptr_t)(param_2)!=(uintptr_t)((uchar *)0x0))) && ((uintptr_t)(param_3)!=(uintptr_t)((uint *)0x0))) &&
     (0x2d < *param_3)) {
    thunk_FUN_0006a45e();
    local_18.trip = (*((uint *)camry_host_ptr((uint32_t)(puVar1 + -0x61f4))));
    local_18.reset = (*((uint *)camry_host_ptr((uint32_t)(puVar1 + -0x61f0))));
    local_18.message = (*((ushort *)camry_host_ptr((uint32_t)(puVar1 + -0x61ec))));
    thunk_FUN_0006a4c4();
    local_18.reset_low2 = (byte)local_18.reset & 3;
    local_18.bit_length = '.';
    f33_freshness_encode_wire(camry_host_addr(&local_18), camry_host_addr(param_2), camry_host_addr(param_3));
    uVar2 = 0;
  }
  return uVar2;
}



undefined4 FUN_0009063c(ushort param_1,uchar *param_2,uint *param_3)

{
  uint *puVar1;
  uint32_t puVar2;
  undefined4 uVar3;
  F33FreshnessWire local_1c;
  
  puVar2 = 0xfebeb800u;
  uVar3 = 1;
  if ((((param_1 < 2) && ((uintptr_t)(param_2)!=(uintptr_t)((uchar *)0x0))) && ((uintptr_t)(param_3)!=(uintptr_t)((uint *)0x0))) &&
     (0x2d < *param_3)) {
    thunk_FUN_0006a45e();
    puVar1 = ((uint *)camry_host_ptr((uint32_t)(puVar2 + (short)param_1 * 0xc + -0x6224)));
    local_1c.trip = *puVar1;
    local_1c.reset = puVar1[1];
    local_1c.message = (ushort)puVar1[2];
    thunk_FUN_0006a4c4();
    local_1c.reset_low2 = (byte)local_1c.reset & 3;
    local_1c.bit_length = '.';
    f33_freshness_encode_wire(camry_host_addr(&local_1c), camry_host_addr(param_2), camry_host_addr(param_3));
    uVar3 = 0;
  }
  return uVar3;
}



void FUN_000906a4(undefined4 *param_1,undefined1 *param_2,uint *param_3)

{
  uint uVar1;
  
  if ((byte)*param_3 < (*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 0xb))))) {
    uVar1 = 0;
  }
  else {
    *param_2 = (char)((uint)*param_1 >> 8);
    param_2[1] = (char)*param_1;
    param_2[2] = (char)((uint)param_1[1] >> 0xc);
    param_2[3] = (char)((uint)param_1[1] >> 4);
    param_2[4] = (char)(param_1[1] << 4);
    uVar1 = (uint)(*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 0xb))));
  }
  *param_3 = uVar1;
  return;
}



undefined4 FUN_000906e2(short param_1,int param_2,uint *param_3)

{
  uint32_t puVar1;
  undefined4 uVar2;
  undefined4 local_18;
  undefined4 uStack_14;
  undefined2 uStack_10;
  undefined1 uStack_e;
  undefined1 uStack_d;
  
  puVar1 = 0xfebeb800u;
  uVar2 = 1;
  if ((((param_1 == 0) && (param_2 != 0)) && ((uintptr_t)(param_3)!=(uintptr_t)((uint *)0x0))) && (0x23 < *param_3)) {
    thunk_FUN_0006a45e();
    local_18 = (*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + -0x6240))));
    uStack_14 = (*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + -0x623c))));
    thunk_FUN_0006a4c4();
    uStack_10 = 0;
    uStack_e = 0;
    uStack_d = 0x24;
    FUN_000906a4(&local_18, ((undefined1 *)camry_host_ptr((uint32_t)(param_2))), param_3);
    uVar2 = 0;
  }
  return uVar2;
}



undefined4 FUN_000907aa(short param_1,uchar *param_2,int param_3)

{
  uint32_t puVar1;
  undefined4 uVar2;
  F33FreshnessWire local_10;
  
  puVar1 = 0xfebeb800u;
  uVar2 = 1;
  if (((param_1 == 0) && ((uintptr_t)(param_2)!=(uintptr_t)((uchar *)0x0))) && (param_3 == 0x2e)) {
    f33_freshness_decode_wire(camry_host_addr(param_2), 0x2e, camry_host_addr(&local_10));
    thunk_FUN_0006a45e();
    (*((uint *)camry_host_ptr((uint32_t)(puVar1 + -0x61f4)))) = local_10.trip;
    (*((uint *)camry_host_ptr((uint32_t)(puVar1 + -0x61f0)))) = local_10.reset;
    (*((ushort *)camry_host_ptr((uint32_t)(puVar1 + -0x61ec)))) = local_10.message;
    thunk_FUN_0006a4c4();
    uVar2 = 0;
  }
  return uVar2;
}



undefined4 FUN_000907ea(ushort param_1,uchar *param_2,int param_3)

{
  uint *puVar1;
  uint32_t puVar2;
  undefined4 uVar3;
  F33FreshnessWire local_14;
  
  puVar2 = 0xfebeb800u;
  uVar3 = 1;
  if (((param_1 < 2) && ((uintptr_t)(param_2)!=(uintptr_t)((uchar *)0x0))) && (param_3 == 0x2e)) {
    f33_freshness_decode_wire(camry_host_addr(param_2), 0x2e, camry_host_addr(&local_14));
    thunk_FUN_0006a45e();
    puVar1 = ((uint *)camry_host_ptr((uint32_t)(puVar2 + (short)param_1 * 0xc + -0x6224)));
    *puVar1 = local_14.trip;
    puVar1[1] = local_14.reset;
    *(ushort *)(puVar1 + 2) = local_14.message;
    thunk_FUN_0006a4c4();
    uVar3 = 0;
  }
  return uVar3;
}



void FUN_00090836(undefined1 *param_1,int param_2,uint *param_3)

{
  undefined1 uVar1;
  uint uVar2;
  
  if (param_2 == 0x24) {
    *param_3 = (uint)CONCAT11(*param_1,param_1[1]);
    uVar2 = (uint)((byte)param_1[4] >> 4) |
            (uint)(byte)param_1[3] << 4 | (uint)(byte)param_1[2] << 0xc;
    uVar1 = 0x24;
  }
  else {
    *param_3 = 0;
    uVar2 = 0;
    uVar1 = 0;
  }
  param_3[1] = uVar2;
  *(undefined2 *)(param_3 + 2) = 0;
  (*((undefined1 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_3) + 10)))) = 0;
  (*((undefined1 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_3) + 0xb)))) = uVar1;
  return;
}



undefined4 FUN_00090874(short param_1,int param_2,int param_3)

{
  uint32_t puVar1;
  undefined4 uVar2;
  uint local_10;
  uint uStack_c;
  
  puVar1 = 0xfebeb800u;
  uVar2 = 1;
  if (((param_1 == 0) && (param_2 != 0)) && (param_3 == 0x24)) {
    FUN_00090836(((undefined1 *)camry_host_ptr((uint32_t)(param_2))), 0x24, &local_10);
    thunk_FUN_0006a45e();
    (*((uint *)camry_host_ptr((uint32_t)(puVar1 + -0x6240)))) = local_10;
    (*((uint *)camry_host_ptr((uint32_t)(puVar1 + -0x623c)))) = uStack_c;
    (*((uint *)camry_host_ptr((uint32_t)(puVar1 + -0x6230)))) = ~local_10;
    (*((uint *)camry_host_ptr((uint32_t)(puVar1 + -0x622c)))) = ~uStack_c;
    thunk_FUN_0006a4c4();
    uVar2 = 0;
  }
  return uVar2;
}



void FUN_00090d42(short param_1,char param_2)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  if ((param_1 == 0) && (param_2 == '\x01')) {
    thunk_FUN_0006a45e();
    f33_memcpy_forward(((undefined *)camry_host_ptr((uint32_t)(puVar1 + -0x61f4))), ((undefined *)camry_host_ptr((uint32_t)(puVar1 + -0x61e8))), 0xc);
    thunk_FUN_0006a4c4();
  }
  return;
}



void FUN_00090d9e(short param_1)

{
  short sVar1;
  uint32_t puVar2;
  uint32_t puVar3;
  uint uVar4;
  short sVar5;
  int iVar6;
  
  puVar2 = 0xfebeb800u;
  puVar3 = 0x23dfcu;
  sVar5 = 0;
  uVar4 = 0;
  do {
    sVar1 = (*((short *)camry_host_ptr((uint32_t)(puVar3 + 0x1a42))));
    if ((sVar1 == 0) && (iVar6 = (short)uVar4 * 0x50, (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(iVar6 + 0x1a55))))) != '\x01')) {
      if ((*((short *)camry_host_ptr((uint32_t)(puVar3 + iVar6 + 0x1a50)))) == param_1) {
        thunk_FUN_0006a45e();
        f33_memzero(((undefined *)camry_host_ptr((uint32_t)(puVar2 + sVar5 * 0xc + -0x6224))), 0xc);
        f33_memzero(((undefined *)camry_host_ptr((uint32_t)(puVar2 + sVar5 * 0xc + -0x620c))), 0xc);
        thunk_FUN_0006a4c4();
      }
      sVar5 = sVar5 + 1;
    }
    uVar4 = uVar4 + 1;
  } while (uVar4 < 3);
  if ((sVar1 == 0) && ((*((short *)camry_host_ptr((uint32_t)(puVar3 + 0x1b40)))) == param_1)) {
    thunk_FUN_0006a45e();
    f33_memzero(((undefined *)camry_host_ptr((uint32_t)(puVar2 + -0x61f4))), 0xc);
    f33_memzero(((undefined *)camry_host_ptr((uint32_t)(puVar2 + -0x61e8))), 0xc);
    thunk_FUN_0006a4c4();
  }
  return;
}



void FUN_00090e20(short param_1,char param_2)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  if (param_1 == 0) {
    if (param_2 == '\x01') {
      puVar1 = 0xfebeb800u;
      thunk_FUN_0006a45e();
      f33_memcpy_forward(((undefined *)camry_host_ptr((uint32_t)(puVar1 + -0x6240))), ((undefined *)camry_host_ptr((uint32_t)(puVar1 + -0x6238))), 8);
      (*((uint *)camry_host_ptr((uint32_t)(puVar1 + -0x6230)))) = ~(*((uint *)camry_host_ptr((uint32_t)(puVar1 + -0x6240))));
      (*((uint *)camry_host_ptr((uint32_t)(puVar1 + -0x622c)))) = ~(*((uint *)camry_host_ptr((uint32_t)(puVar1 + -0x623c))));
      thunk_FUN_0006a4c4();
      if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6226))))) == '\x01') {
        FUN_00090d9e(0);
      }
    }
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6226))))) = 0;
  }
  return;
}



void FUN_00090e6e(short param_1,short param_2)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  if ((param_1 == 0) && (param_2 == 0)) {
    thunk_FUN_0006a45e();
    (*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + -0x6240)))) = 0;
    (*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + -0x623c)))) = 0;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6226))))) = 0;
    (*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + -0x6238)))) = 0;
    (*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + -0x6234)))) = 0;
    (*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + -0x6230)))) = 0xffffffff;
    (*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + -0x622c)))) = 0xffffffff;
    thunk_FUN_0006a4c4();
    FUN_00090d9e(0);
  }
  return;
}



undefined4 FUN_00090eac(void)

{
  uint32_t puVar1;
  undefined4 uVar2;
  uint uVar3;
  uint uVar4;
  uint uVar5;
  uint uVar6;
  
  puVar1 = 0xfebeb800u;
  thunk_FUN_0006a45e();
  uVar5 = (*((uint *)camry_host_ptr((uint32_t)(puVar1 + -0x6240))));
  uVar4 = (*((uint *)camry_host_ptr((uint32_t)(puVar1 + -0x623c))));
  uVar6 = (*((uint *)camry_host_ptr((uint32_t)(puVar1 + -0x6230))));
  uVar3 = (*((uint *)camry_host_ptr((uint32_t)(puVar1 + -0x622c))));
  thunk_FUN_0006a4c4();
  if ((uVar6 == ~uVar5) && (uVar3 == ~uVar4)) {
    (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x6228)))) = 0;
    uVar2 = 0;
  }
  else {
    uVar2 = 2;
    (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x6228)))) = 2;
  }
  return uVar2;
}



void FUN_00090ee6(void)

{
  FUN_000913b6();
  FUN_000912b2();
  return;
}



/* Configured second policy hook uses fourth argument R9 only; map nonzero8B0FC result to8,
   otherwise0. Return8 selects silent-drop disposition, not a fabricated NRC. */

uint f33_dcm_application_policy_hook
               (uchar service_id,uchar *request,ushort request_length,uchar addressing_flags,
               ushort service_list_selector,uchar *negative_response)

{
  uint uVar1;
  
  uVar1 = f33_check_diagnostic_addressing_admission(addressing_flags);
  if (uVar1 == 0) {
    uVar1 = 0;
  }
  else {
    uVar1 = 8;
  }
  return uVar1;
}



/* Null list allows; nonnull list requires current595C session in count bytes. Nonnull zero-count
   rejects. Return0 allowed,1 rejected. */

uint f33_dcm_check_session_list(uchar *allowed,uchar count)

{
  uint uVar1;
  uint uVar2;
  uchar uStack_11;
  
  uVar2 = 1;
  uStack_11 = '\x01';
  if ((uintptr_t)(allowed)==(uintptr_t)((uchar *)0x0)) {
LAB_00090f50:
    uVar2 = 0;
  }
  else {
    f33_dcm_get_session(&uStack_11);
    for (uVar1 = 0; uVar1 < count; uVar1 = uVar1 + 1 & 0xff) {
      if (uStack_11 == allowed[uVar1]) goto LAB_00090f50;
    }
  }
  return uVar2;
}



/* Null list allows; otherwise match current security getter result against count bytes. Nonnull
   zero-count rejects. Separate from application/group admission. */

uint f33_dcm_check_security_list(uchar *allowed,uchar count)

{
  uint uVar1;
  uint uVar2;
  uchar uStack_11;
  
  uStack_11 = '\0';
  uVar2 = 1;
  if ((uintptr_t)(allowed)==(uintptr_t)((uchar *)0x0)) {
LAB_00090f90:
    uVar2 = 0;
  }
  else {
    f33_dcm_get_security_level(&uStack_11);
    for (uVar1 = 0; uVar1 < count; uVar1 = uVar1 + 1 & 0xff) {
      if (uStack_11 == allowed[uVar1]) goto LAB_00090f90;
    }
  }
  return uVar2;
}



/* Stage bit1 selects hook family; bit0 selects post-SID request and adds address flag10. Clamp byte
   extent toFFFF. Exact first hook disabled, second enabled. Preserve nonzero callback result; only
   result1 is an NRC path in the service entry. */

uint f33_dcm_invoke_request_policy
               (uchar service_id,F33DcmMessageContext *message,uint stage,uchar *negative_response)

{
  char cVar1;
  undefined4 *puVar2;
  uint uVar3;
  uchar *puVar4;
  byte bVar5;
  uint uVar6;
  uchar uStack_2e;
  uchar uStack_2d;
  
  *negative_response = '\0';
  uVar3 = 0;
  cVar1 = DAT_00025bf8;
  if ((stage & 2) != 0) {
    cVar1 = DAT_00025bf9;
  }
  if (cVar1 == '\x01') {
    puVar2 = ((undefined4 *)camry_host_ptr((uint32_t)(PTR_PTR_00025bfc)));
    if ((stage & 2) != 0) {
      puVar2 = ((undefined4 *)camry_host_ptr((uint32_t)(PTR_PTR_00025c04)));
    }
    if ((uintptr_t)(puVar2)!=(uintptr_t)((undefined4 *)0x0)) {
      bVar5 = message->addressing_kind;
      puVar4 = ((void *)camry_host_ptr((uint32_t)(message->request)));
      uVar6 = message->request_length;
      if ((stage & 1) == 0) {
        puVar4 = puVar4 + 1;
        uVar6 = uVar6 - 1;
      }
      else {
        bVar5 = bVar5 | 0x10;
      }
      if (0xffff < uVar6) {
        uVar6 = 0xffff;
      }
      uStack_2e = '\0';
      uStack_2d = service_id;
      uVar6 = (*(int (*)())*puVar2)(service_id,puVar4,uVar6 & 0xffff,bVar5,
                                 message->service_list_selector,&uStack_2e);
      if (uVar6 != 0) {
        uVar3 = uVar6;
        if (uVar6 == 1) {
          *negative_response = uStack_2e;
        }
        else {
          *negative_response = uStack_2e;
        }
      }
    }
  }
  return uVar3;
}



/* Copy remaining request length/routing to main5630, add retained prefix count to body length, then
   select and stage final disposition. Does not itself mean transport confirmation. */

void f33_dcm_complete_service_response(F33DcmMessageContext *message)

{
  uchar uVar1;
  F33DcmMessageContext *message_00;
  int iVar2;
  
  message_00 = f33_dcm_get_message_context();
  message_00->request_length = message->request_length;
  iVar2 = FUN_000916a6();
  message_00->response_length = message->response_length + iVar2;
  uVar1 = message->suppress_positive;
  message_00->addressing_kind = message->addressing_kind;
  message_00->suppress_positive = uVar1;
  message_00->service_id = message->service_id;
  message_00->service_list_selector = message->service_list_selector;
  f33_dcm_select_response_disposition(message_00);
  return;
}



void FUN_000912b2(void)

{
  f33_dcm_final_nrc = '\0';
  return;
}



void FUN_000912b8(void)

{
  f33_dcm_final_nrc = '\0';
  return;
}



/* Nonzero pending flag invokes operation3 without clearing active state. Final notification runs
   service/generic observers, then clears active context and NRC; it does not invoke operation3. */

uint f33_dcm_deliver_response_notification(uchar result,uchar pending_notification)

{
  uint32_t puVar1;
  F33DcmMessageContext *pFVar2;
  int iVar3;
  undefined4 uVar4;
  
  puVar1 = 0x23dfcu;
  if (pending_notification == '\0') {
    pFVar2 = f33_dcm_get_message_context();
    iVar3 = FUN_0009169a();
    if (iVar3 == 1) {
      FUN_00095650(pFVar2->service_id,pFVar2->service_list_selector,result);
    }
    uVar4 = FUN_0009168e();
    if (((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x1dfc))))) == '\x01') && ((*((int *)camry_host_ptr((uint32_t)(0x1e04u + (int)puVar1)))) != 0)) {
      (*(int (*)())**(undefined4 **)(0x1e04u + (int)puVar1))(uVar4,pFVar2->addressing_kind,pFVar2->service_list_selector,result);
    }
    if (((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x1dfd))))) == '\x01') && ((*((int *)camry_host_ptr((uint32_t)(puVar1 + 0x1e0c)))) != 0)) {
      (*(int (*)())**(undefined4 **)(puVar1 + 0x1e0c))(uVar4,pFVar2->addressing_kind,pFVar2->service_list_selector,result);
    }
    f33_dcm_clear_active_service();
    FUN_000912b8();
  }
  else {
    f33_dcm_notify_active_service_operation_three();
  }
  return 0;
}



void FUN_0009136c(F33DcmMessageContext *param_1)

{
  f33_dcm_stage_final_response(param_1,'\x03');
  return;
}



/* Zero main message pointers, lengths, addressing, suppression, capacity, SID and selector; opaque
   padding is untouched. Cancellation invokes this before operation2. */

void f33_dcm_reset_message_context(void)

{
  f33_dcm_message_context.request = 0;
  f33_dcm_message_context.request_length = 0;
  f33_dcm_message_context.response = 0;
  f33_dcm_message_context.response_length = 0;
  f33_dcm_message_context.addressing_kind = '\0';
  f33_dcm_message_context.suppress_positive = '\0';
  f33_dcm_message_context.response_capacity = 0;
  f33_dcm_message_context.service_id = '\0';
  f33_dcm_message_context.service_list_selector = 0;
  return;
}



/* Clear retained SID562C, callback5628 and prefix count562D, then reset message5630; this is not
   the NRC5624 reset. */

void f33_dcm_clear_active_service(void)

{
  DAT_febe562c = 0;
  f33_dcm_active_service_callback = camry_host_addr(f33_reset_vector);
  DAT_febe562d = 0;
  f33_dcm_reset_message_context();
  return;
}



void FUN_000913b6(void)

{
  f33_dcm_clear_active_service();
  return;
}



/* Initialize28-byte5630 context from two eight-byte PduInfo descriptors. Request and response
   extents read as unsigned16; response length and suppression reset. */

void f33_dcm_initialize_message_context
               (ushort service_list_selector,uchar addressing_kind,F33PduInfo *request,
               F33PduInfo *response)

{
  f33_dcm_message_context.request = camry_host_addr(((void *)camry_host_ptr((uint32_t)(request->data))));
  f33_dcm_message_context.response_length = 0;
  f33_dcm_message_context.addressing_kind = addressing_kind;
  f33_dcm_message_context.request_length = (uint)request->length;
  f33_dcm_message_context.suppress_positive = '\0';
  f33_dcm_message_context.service_id = '\0';
  f33_dcm_message_context.response = camry_host_addr(((void *)camry_host_ptr((uint32_t)(response->data))));
  f33_dcm_message_context.service_list_selector = service_list_selector;
  f33_dcm_message_context.response_capacity = (uint)response->length;
  return;
}



void FUN_000913ea(undefined1 param_1)

{
  DAT_febe562c = param_1;
  return;
}



/* Exact selectors2/3/4 select rows0/1/2 at25C0C. Unknown selector falls back to row0; not a CAN-bus
   identity claim. */

uint f33_dcm_select_service_list(ushort selector)

{
  uint uVar1;
  
  uVar1 = 0;
  do {
    if (f33_dcm_service_lists[uVar1].selector == selector) {
      return uVar1;
    }
    uVar1 = uVar1 + 1;
  } while (uVar1 < 3);
  return 0;
}



/* Initialize context; run first policy, service/session/security resolution, then second policy
   before direct/subfunction dispatch. Result1 stages NRC; other nonzero policy results choose
   silent disposition3. Session denial precedes application addressing publication. Native
   service-entry compositions verify extended-session DID2013 writes1234 while COM7F96 remains
   inhibited, default-session NRC7F before addressing publication, and application-gate silent drop
   that still publishes addressing kind. Stop before91CE2 transport publication; no external wire
   reachability claim. */

void f33_dcm_begin_service_request
               (F33DcmRequestRoute *route,F33PduInfo *request,F33PduInfo *response)

{
  uint32_t puVar1;
  uint32_t puVar2;
  undefined1 uVar3;
  uint uVar4;
  F33DcmMessageContext *message;
  uchar uStack_16;
  uchar uStack_15;
  F33DcmServiceSelection FStack_14;
  
  puVar1 = 0xfebeb800u;
  puVar2 = 0x23dfcu;
  uStack_15 = '\0';
  uStack_16 = '\0';
  f33_dcm_initialize_message_context
            (route->service_list_selector,route->addressing_kind,request,response);
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x61b8))))) = **(undefined1 **)(puVar1 + -0x61d0);
  FUN_000913ea(**(undefined1 **)(puVar1 + -0x61d0));
  message = ((F33DcmMessageContext *)camry_host_ptr((uint32_t)(puVar1 + -0x61d0)));
  uVar4 = f33_dcm_invoke_request_policy(**(uchar **)(puVar1 + -0x61d0),message,0,&uStack_15);
  if (uVar4 == 0) {
    uVar4 = f33_dcm_select_service_list(route->service_list_selector);
    FStack_14.list = camry_host_addr(((F33DcmServiceList *)camry_host_ptr((uint32_t)(0x1e10u + (int)(puVar2 + uVar4 * 8)))));
    FStack_14.service = 0;
    uStack_15 = '\0';
    uVar4 = f33_dcm_resolve_service(message,&FStack_14,&uStack_16,&uStack_15);
    if (uVar4 != 0) {
      uVar3 = 0;
      if (uStack_15 != '\x11') {
        uVar3 = **(undefined1 **)(puVar1 + -0x61d0);
      }
      goto LAB_0009162a;
    }
    uStack_15 = '\0';
    uVar4 = f33_dcm_invoke_request_policy(**(uchar **)(puVar1 + -0x61d0),message,2,&uStack_15);
    if (uVar4 == 0) {
      if (uStack_16 == '\0') {
        f33_dcm_dispatch_direct_service(message, ((F33DcmService *)camry_host_ptr((uint32_t)(FStack_14.service))));
        return;
      }
      f33_dcm_dispatch_subfunction_service(message, ((F33DcmService *)camry_host_ptr((uint32_t)(FStack_14.service))));
      return;
    }
    uVar3 = **(undefined1 **)(puVar1 + -0x61d0);
  }
  else {
    uVar3 = 0;
  }
  if (uVar4 != 1) {
    FUN_000955c2(uVar3,0);
    FUN_0009136c(message);
    return;
  }
LAB_0009162a:
  FUN_000955c2(uVar3,uStack_15);
  f33_dcm_stage_negative_response(message,uStack_15);
  f33_dcm_complete_service_response(message);
  return;
}



/* Return the retained28-byte message context5630; not an opaque scalar. */

F33DcmMessageContext * f33_dcm_get_message_context(void)

{
  return ((undefined *)camry_host_ptr(0xfebe5630u));
}



undefined1 FUN_0009168e(void)

{
  return DAT_febe562c;
}



undefined1 FUN_00091694(undefined1 *param_1)

{
  return *param_1;
}



undefined1 FUN_000916a6(void)

{
  return DAT_febe562d;
}



bool FUN_000916c6(char param_1,undefined4 *param_2)

{
  bool bVar1;
  
  bVar1 = false;
  if (((param_1 == '\x01') && (*(short *)(param_2 + 1) == 2)) && (*(char *)*param_2 == '>')) {
    bVar1 = ((char *)*param_2)[1] == -0x80;
  }
  return bVar1;
}



undefined4 FUN_000916ec(char param_1,ushort param_2,char param_3)

{
  short *psVar1;
  uint uVar2;
  uint32_t puVar3;
  uint uVar4;
  
  puVar3 = 0x23dfcu;
  uVar4 = f33_dcm_select_service_list(param_2);
  uVar2 = 0;
  while( true ) {
    if ((byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x1e10u + (uint32_t)((int)(puVar3 + uVar4 * 8 + 2)))))) <= uVar2) {
      return 1;
    }
    psVar1 = ((short *)camry_host_ptr((uint32_t)(uVar2 * 2 + *(int *)(puVar3 + uVar4 * 8 + 0x1e14))));
    if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(*psVar1 * 0x18 + 0x1e68))))) == param_1) break;
    uVar2 = uVar2 + 1 & 0xff;
  }
  uVar2 = 0;
  if ((*((int *)camry_host_ptr((uint32_t)(puVar3 + *psVar1 * 0x18 + 0x1e60)))) != 0) {
    while( true ) {
      if ((byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(*psVar1 * 0x18 + 0x1e6b))))) <= uVar2) {
        return 1;
      }
      if ((*((char *)camry_host_ptr((uint32_t)(*(int *)(puVar3 + *psVar1 * 0x18 + 0x1e60) + uVar2)))) == param_3) break;
      uVar2 = uVar2 + 1 & 0xff;
    }
  }
  return 0;
}



void FUN_00091788(undefined1 param_1)

{
  FUN_00092094(param_1);
  return;
}



void FUN_00091796(undefined1 param_1)

{
  FUN_000920a2(param_1);
  return;
}



void FUN_000917a4(undefined1 param_1)

{
  FUN_000920b0(param_1);
  return;
}



void FUN_000917b2(void)

{
  int iVar1;
  uint uVar2;
  
  uVar2 = 0;
  do {
    iVar1 = uVar2 * 2;
    uVar2 = uVar2 + 1;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe564cu + (uint32_t)(iVar1) * 1u)))) = 0;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe564du + (uint32_t)(iVar1) * 1u)))) = 0;
  } while (uVar2 < 2);
  DAT_febe5650 = 1;
  return;
}



void FUN_000917d0(char param_1,undefined1 param_2)

{
  uint32_t puVar1;
  undefined *puVar2;
  undefined *puVar3;
  short sVar4;
  uint uVar5;
  
  puVar1 = 0xfebeb800u;
  puVar2 = ((undefined *)camry_host_ptr(0x23dfcu));
  uVar5 = 0;
  do {
    sVar4 = (short)uVar5;
    if (param_1 ==
        (*((char *)camry_host_ptr((uint32_t)(*(int *)((uint)*(ushort *)(puVar2 + sVar4 * 0xc + 0x20ee) * 4 +
                          *(int *)(puVar2 + *(short *)(puVar2 + sVar4 * 0xc + 0x20ec) * 0x14 +
                                            0x20c4)) + 2))))) {
      puVar3 = puVar2;
      thunk_FUN_0006a45e();
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)((uint)*(ushort *)(puVar2 + sVar4 * 0xc + 0x20f2) * 2 + -0x61b4))))) = param_2;
      thunk_FUN_0006a4c4();
      puVar2 = puVar3;
    }
    uVar5 = uVar5 + 1;
  } while (uVar5 < 3);
  return;
}



undefined4 FUN_00091826(undefined1 param_1)

{
  FUN_000917d0(param_1,0);
  return 0;
}



undefined4 FUN_00091838(undefined1 param_1)

{
  FUN_000917d0(param_1,1);
  return 0;
}



undefined4 FUN_0009184a(undefined1 param_1)

{
  FUN_000917d0(param_1,2);
  return 0;
}



undefined4 FUN_0009185c(short param_1,char param_2)

{
  ushort uVar1;
  uint32_t puVar2;
  undefined4 uVar3;
  
  puVar2 = 0xfebeb800u;
  uVar3 = 0;
  uVar1 = f33_dcm_receive_route[param_1].communication_slot;
  thunk_FUN_0006a45e();
  if (((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)((uint)uVar1 * 2 + -0x61b4))))) == '\x02') ||
     ((param_2 == '\x01' && ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)((uint)uVar1 * 2 + -0x61b4))))) == '\x01')))) {
    uVar3 = 1;
  }
  thunk_FUN_0006a4c4();
  return uVar3;
}



undefined4 FUN_00091894(char param_1)

{
  short *psVar1;
  undefined8 uVar2;
  int iVar3;
  uint uVar4;
  char *pcVar5;
  
  uVar2 = 0x23dfcfebeb800;
  thunk_FUN_0006a45e();
  pcVar5 = ((char *)camry_host_ptr((uint32_t)((int)uVar2 + -0x61b0)));
  *pcVar5 = param_1 == '\x01';
  uVar4 = 0;
  if (*pcVar5 == '\x01') {
    do {
      iVar3 = (int)((ulonglong)uVar2 >> 0x20);
      psVar1 = ((short *)camry_host_ptr((uint32_t)((short)uVar4 * 0xc + iVar3 + 0x20ec)));
      if ((*((char *)camry_host_ptr((uint32_t)((uint)(ushort)psVar1[3] * 2 + (int)uVar2 + -0x61b3)))) == '\x01') {
        FUN_00091ac2((*((undefined1 *)camry_host_ptr((uint32_t)(*(int *)((uint)(ushort)psVar1[1] * 4 +
                               *(int *)(*psVar1 * 0x14 + iVar3 + 0x20c4)) + 2)))));
      }
      uVar4 = uVar4 + 1;
    } while (uVar4 < 3);
  }
  else {
    do {
      iVar3 = (int)((ulonglong)uVar2 >> 0x20);
      psVar1 = ((short *)camry_host_ptr((uint32_t)((short)uVar4 * 0xc + iVar3 + 0x20ec)));
      if ((*((char *)camry_host_ptr((uint32_t)((uint)(ushort)psVar1[3] * 2 + (int)uVar2 + -0x61b3)))) == '\x01') {
        FUN_00091ad0((*((undefined1 *)camry_host_ptr((uint32_t)(*(int *)((uint)(ushort)psVar1[1] * 4 +
                               *(int *)(*psVar1 * 0x14 + iVar3 + 0x20c4)) + 2)))));
      }
      uVar4 = uVar4 + 1;
    } while (uVar4 < 3);
  }
  thunk_FUN_0006a4c4();
  return 0;
}



void FUN_00091938(short param_1,char param_2)

{
  short *psVar1;
  char cVar2;
  uint32_t puVar3;
  undefined *puVar4;
  undefined *puVar5;
  short sVar6;
  uint uVar7;
  uchar uStack_d;
  
  puVar3 = 0xfebeb800u;
  puVar4 = ((undefined *)camry_host_ptr(0x23dfcu));
  uStack_d = '\0';
  thunk_FUN_0006a45e();
  cVar2 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x61b0)))));
  if (param_2 == '\0') {
    if (cVar2 == '\x01') {
      psVar1 = (short *)(puVar4 + param_1 * 0xc + 0x20ec);
      if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)((uint)(ushort)psVar1[3] * 2 + -0x61b3))))) != '\0') goto LAB_00091a1c;
      FUN_00091ac2((*((undefined1 *)camry_host_ptr((uint32_t)(*(int *)((uint)(ushort)psVar1[1] * 4 +
                             *(int *)(puVar4 + *psVar1 * 0x14 + 0x20c4)) + 2)))));
    }
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)((uint)*(ushort *)(puVar4 + param_1 * 0xc + 0x20f2) * 2 + -0x61b3))))) = 1;
  }
  else {
    f33_dcm_get_session(&uStack_d);
    if (uStack_d == '\x01') {
      uVar7 = 0;
      if (cVar2 == '\x01') {
        do {
          sVar6 = (short)uVar7;
          if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)((uint)*(ushort *)(puVar4 + sVar6 * 0xc + 0x20f2) * 2 + -0x61b3))))) == '\x01') {
            puVar5 = puVar4;
            FUN_00091ad0((*((undefined1 *)camry_host_ptr((uint32_t)(*(int *)((uint)*(ushort *)(puVar4 + sVar6 * 0xc + 0x20ee) * 4 +
                                   *(int *)(puVar4 + *(short *)(puVar4 + sVar6 * 0xc + 0x20ec) *
                                                     0x14 + 0x20c4)) + 2)))));
            (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)((uint)*(ushort *)(puVar4 + sVar6 * 0xc + 0x20f2) * 2 + -0x61b3))))) = 0;
            puVar4 = puVar5;
          }
          uVar7 = uVar7 + 1;
        } while (uVar7 < 3);
      }
      else {
        do {
          sVar6 = (short)uVar7;
          uVar7 = uVar7 + 1;
          (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)((uint)*(ushort *)(puVar4 + sVar6 * 0xc + 0x20f2) * 2 + -0x61b3))))) = 0;
        } while (uVar7 < 3);
      }
    }
  }
LAB_00091a1c:
  thunk_FUN_0006a4c4();
  return;
}



void FUN_00091a24(void)

{
  uint32_t puVar1;
  undefined *puVar2;
  undefined *puVar3;
  short sVar4;
  uint uVar5;
  
  puVar1 = 0xfebeb800u;
  puVar2 = ((undefined *)camry_host_ptr(0x23dfcu));
  thunk_FUN_0006a45e();
  uVar5 = 0;
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x61b0))))) == '\x01') {
    do {
      sVar4 = (short)uVar5;
      if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)((uint)*(ushort *)(puVar2 + sVar4 * 0xc + 0x20f2) * 2 + -0x61b3))))) == '\x01') {
        puVar3 = puVar2;
        FUN_00091ad0((*((undefined1 *)camry_host_ptr((uint32_t)(*(int *)((uint)*(ushort *)(puVar2 + sVar4 * 0xc + 0x20ee) * 4 +
                               *(int *)(puVar2 + *(short *)(puVar2 + sVar4 * 0xc + 0x20ec) * 0x14 +
                                                 0x20c4)) + 2)))));
        (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)((uint)*(ushort *)(puVar2 + sVar4 * 0xc + 0x20f2) * 2 + -0x61b3))))) = 0;
        puVar2 = puVar3;
      }
      uVar5 = uVar5 + 1;
    } while (uVar5 < 3);
  }
  else {
    do {
      if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)((uint)*(ushort *)(puVar2 + (short)uVar5 * 0xc + 0x20f2) * 2 + -0x61b3))))) == '\x01') {
        (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)((uint)*(ushort *)(puVar2 + (short)uVar5 * 0xc + 0x20f2) * 2 + -0x61b3))))) = 0;
      }
      uVar5 = uVar5 + 1;
    } while (uVar5 < 3);
  }
  thunk_FUN_0006a4c4();
  return;
}



void FUN_00091ab8(void)

{
  return;
}



void FUN_00091ac2(undefined1 param_1)

{
  FUN_0007ed16(param_1);
  return;
}



void FUN_00091ad0(undefined1 param_1)

{
  FUN_0007ed2e(param_1);
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_91ade(void)

{
  return;
}



/* Null output returns0 without a read; otherwise return9240E status and its byte output. */

uint f33_dcm_get_security_level(uchar *level)

{
  uint uVar1;
  
  if ((uintptr_t)(level)==(uintptr_t)((uchar *)0x0)) {
    uVar1 = 0;
  }
  else {
    uVar1 = f33_dcm_read_security_bitmap_level(level);
  }
  return uVar1;
}



/* Null output returns0 without a read; otherwise return924FC status and its byte output. */

uint f33_dcm_get_session(uchar *session)

{
  uint uVar1;
  
  if ((uintptr_t)(session)==(uintptr_t)((uchar *)0x0)) {
    uVar1 = 0;
  }
  else {
    uVar1 = f33_dcm_read_session_snapshot(session);
  }
  return uVar1;
}



void FUN_00091b08(uchar param_1,uchar param_2)

{
  f33_dcm_stage_or_publish_session(param_1,param_2);
  return;
}



/* Publishdefault1 immediately (relocks and notifies), clear three receive-active slots, set
   diagnostic transportstate0, run91A24 and no-op925A0. Timer5 callback91B78 reaches this path. No
   physical reset or ECU power action. */

void f33_dcm_restore_default_session(void)

{
  uint uVar1;
  
  FUN_00091b08(1,0);
  thunk_FUN_0006a45e();
  uVar1 = 0;
  do {
    FUN_00093f4e(uVar1,0);
    uVar1 = uVar1 + 1;
  } while (uVar1 < 3);
  FUN_00092610(0);
  thunk_FUN_0006a4c4();
  FUN_00091a24();
  FUN_000925a0(1);
  return;
}



undefined4 FUN_00091b50(void)

{
  ushort uVar1;
  uint uVar2;
  undefined4 uVar3;
  
  uVar3 = 1;
  uVar2 = FUN_00092624();
  if ((uVar2 < 2) && (uVar1 = f33_dcm_count_receiving_slots(), uVar1 == 0)) {
    f33_dcm_cancel_software_timer('\x05');
    f33_dcm_restore_default_session();
    uVar3 = 0;
  }
  return uVar3;
}



void FUN_00091b78(void)

{
  f33_dcm_restore_default_session();
  return;
}



/* Far-call trampoline: prepare {lp},0 / jarl 0x93C60 / dispose 0,{lp},lp; byte-verified against the
   exact image. Forwards with registers and stack unchanged; marked as a thunk. Forwarding shape
   machine-verified; target semantics not recovered. */

void thunk_FUN_00093c60(void)

{
  FUN_00093c60();
  return;
}



undefined4 FUN_00091bf2(void)

{
  undefined4 uVar1;
  
  thunk_FUN_0006a45e();
  uVar1 = FUN_00093c8e();
  thunk_FUN_0006a4c4();
  return uVar1;
}



void FUN_00091c82(uchar param_1,uchar param_2)

{
  f33_dcm_deliver_response_notification(param_1,param_2);
  return;
}



/* Consume latched queue result/pending flag. Final notification resets queue transport state and
   finishes staged-session notifications before observers; pending flag preserves callback and
   invokes operation3. */

void f33_dcm_run_queued_response_notification(void)

{
  int iVar1;
  uchar uStack_6;
  uchar uStack_5;
  
  uStack_6 = '\0';
  uStack_5 = '\0';
  f33_dcm_snapshot_response_notification(&uStack_6,&uStack_5);
  if (uStack_5 != '\x01') {
    FUN_00092a9c();
    iVar1 = FUN_00092624();
    if (iVar1 == 2) {
      FUN_00092b4a();
    }
  }
  f33_dcm_finish_staged_session_notifications();
  f33_dcm_deliver_response_notification(uStack_6,uStack_5);
  return;
}



void FUN_00091cd2(undefined1 param_1,undefined1 param_2)

{
  FUN_00093162(param_1,param_2);
  return;
}



/* Only overall phase5960==2 stages a response. Use shared root5A20 and truncate total message
   response length to16-bit PduInfo before933F8. */

void f33_dcm_stage_final_response(F33DcmMessageContext *message,uchar disposition)

{
  int iVar1;
  F33PduInfo local_14;
  
  local_14.data = 0;
  local_14.length = 0;
  iVar1 = FUN_00092624();
  if (iVar1 == 2) {
    FUN_00093ce6(&local_14);
    local_14.length = (ushort)message->response_length;
    f33_dcm_enqueue_final_disposition(&local_14,disposition);
  }
  return;
}



/* Far-call trampoline: prepare {lp},0 / jarl 0x935B6 / dispose 0,{lp},lp; byte-verified against the
   exact image. Forwards with registers and stack unchanged; marked as a thunk. Forwarding shape
   machine-verified; target semantics not recovered. */

void thunk_FUN_000935b6(void)

{
  FUN_000935b6();
  return;
}



void FUN_00091d20(void)

{
  uchar service_id;
  int iVar1;
  undefined4 uVar2;
  undefined4 local_10;
  undefined2 uStack_c;
  
  local_10 = 0;
  uStack_c = 0;
  iVar1 = FUN_00092624();
  if (iVar1 == 2) {
    thunk_FUN_0006a45e();
    iVar1 = FUN_000940e6(1);
    if (iVar1 == 1) {
      uVar2 = FUN_0009400e();
      FUN_00093c6c(uVar2,&local_10);
      service_id = FUN_00091694(((undefined1 *)camry_host_ptr((uint32_t)(local_10))));
      FUN_000940d0(0,1);
    }
    else {
      service_id = FUN_0009168e();
    }
    iVar1 = FUN_00092d72();
    if (iVar1 != 1) {
      f33_dcm_cancel_active_service();
    }
    thunk_FUN_0006a4c4();
    f33_dcm_enqueue_general_reject(service_id);
  }
  return;
}



void FUN_00091d80(void)

{
  uchar service_id;
  int iVar1;
  undefined4 uVar2;
  undefined4 local_14;
  undefined2 uStack_10;
  
  local_14 = 0;
  uStack_10 = 0;
  iVar1 = FUN_00092624();
  if (iVar1 == 2) {
    thunk_FUN_0006a45e();
    iVar1 = FUN_00093c8e();
    if ((iVar1 == 0) && (iVar1 = FUN_000940e6(0), iVar1 == 1)) {
      uVar2 = FUN_0009400e();
      FUN_00093c6c(uVar2,&local_14);
      service_id = FUN_00091694(((undefined1 *)camry_host_ptr((uint32_t)(local_14))));
      FUN_00093c66(uVar2);
      FUN_000940d0(0,0);
    }
    else {
      service_id = FUN_0009168e();
    }
    thunk_FUN_0006a4c4();
    f33_dcm_p2_response_deadline(service_id);
  }
  return;
}



void FUN_00091de4(void)

{
  int iVar1;
  
  iVar1 = FUN_00092624();
  if (iVar1 == 2) {
    FUN_00093230();
  }
  return;
}



void FUN_00091df8(uchar param_1)

{
  int iVar1;
  
  iVar1 = FUN_00092624();
  if (iVar1 == 2) {
    f33_dcm_request_explicit_pending_response(param_1);
  }
  return;
}



void FUN_00091e12(uchar param_1)

{
  f33_dcm_publish_security_level(param_1);
  return;
}



/* Far-call trampoline: prepare {lp},0 / jarl 0x93D9A / dispose 0,{lp},lp; byte-verified against the
   exact image. Forwards with registers and stack unchanged; marked as a thunk. Forwarding shape
   machine-verified; target semantics not recovered. */

void thunk_FUN_00093d9a(void)

{
  FUN_00093d9a();
  return;
}



bool FUN_00091e2c(void)

{
  ushort uVar1;
  int iVar2;
  bool bVar3;
  
  thunk_FUN_0006a45e();
  bVar3 = false;
  iVar2 = FUN_00092624();
  if (iVar2 == 0) {
    uVar1 = f33_dcm_count_receiving_slots();
    bVar3 = uVar1 == 0;
  }
  thunk_FUN_0006a4c4();
  return bVar3;
}



bool FUN_00091e52(void)

{
  int iVar1;
  
  thunk_FUN_0006a45e();
  iVar1 = FUN_00092624();
  thunk_FUN_0006a4c4();
  return iVar1 == 0;
}



void FUN_00091e6e(void)

{
  f33_dcm_cancel_active_service();
  return;
}



void FUN_00091e7a(void)

{
  uint uVar1;
  
  FUN_00091b08(1,0);
  thunk_FUN_0006a45e();
  uVar1 = 0;
  do {
    FUN_00093f4e(uVar1,0);
    uVar1 = uVar1 + 1;
  } while (uVar1 < 3);
  thunk_FUN_0006a4c4();
  FUN_000925a0(1);
  return;
}



/* Read current session snapshot. Nondefault arms timer5 with protocol-selected raw S3 value
   from25EC8 and sets5960=1; default sets5960=0 without explicitly cancelling an already armed slot.
   Clear receive-active slots. Called from response/release joins and TesterPresent special case. */

void f33_dcm_restart_inactivity_after_request(void)

{
  bool bVar1;
  undefined4 uVar2;
  uint uVar3;
  uchar uStack_9;
  
  uStack_9 = '\x01';
  uVar2 = FUN_00093c60();
  f33_dcm_read_session_snapshot(&uStack_9);
  bVar1 = uStack_9 != '\x01';
  if (bVar1) {
    uVar3 = FUN_00093b18();
    f33_dcm_arm_software_timer('\x05',uVar3);
    thunk_FUN_0006a45e();
  }
  else {
    thunk_FUN_0006a45e();
  }
  FUN_00092610(bVar1);
  thunk_FUN_0006a4c4();
  thunk_FUN_0006a45e();
  FUN_00093c9a(uVar2,0);
  uVar3 = 0;
  do {
    FUN_00093f4e(uVar3,0);
    uVar3 = uVar3 + 1;
  } while (uVar3 < 3);
  thunk_FUN_0006a4c4();
  return;
}



void FUN_00091f0e(void)

{
  int iVar1;
  
  iVar1 = FUN_00092d72();
  if (iVar1 != 1) {
    f33_dcm_cancel_active_service();
  }
  FUN_0009338e();
  return;
}



void FUN_00091f26(uint param_1,char param_2)

{
  int iVar1;
  uint uVar2;
  
  iVar1 = FUN_00092624();
  if (iVar1 == 1) {
    uVar2 = 0;
    do {
      iVar1 = FUN_00093f5a(uVar2);
      if ((iVar1 == 1) && (uVar2 != (param_1 & 0xffff))) {
        return;
      }
      uVar2 = uVar2 + 1;
    } while (uVar2 < 3);
    if (param_2 == '\x01') {
      uVar2 = FUN_00093b18();
      f33_dcm_arm_software_timer('\x05',uVar2);
    }
  }
  return;
}



void FUN_00091f64(uchar param_1)

{
  f33_dcm_commit_or_discard_staged_session(param_1);
  return;
}



void FUN_00091f72(undefined1 param_1)

{
  uint uVar1;
  
  uVar1 = FUN_00092624();
  if (uVar1 < 2) {
    FUN_00092610(param_1);
    FUN_00092b4a();
  }
  return;
}



void FUN_00091f90(void)

{
  f33_dcm_finish_staged_session_notifications();
  return;
}



void FUN_00091f9c(undefined1 param_1)

{
  FUN_000925a0(param_1);
  return;
}



void FUN_00091faa(void)

{
  undefined4 uVar1;
  
  uVar1 = FUN_00093c60();
  FUN_00093c9a(uVar1,0);
  return;
}



void FUN_00091fbe(void)

{
  undefined4 uVar1;
  undefined4 uVar2;
  undefined4 uVar3;
  
  thunk_FUN_0006a45e();
  uVar1 = FUN_00092624();
  uVar2 = FUN_00093c60();
  uVar3 = FUN_0009400e();
  FUN_00092610(uVar1);
  FUN_00093c66(uVar2);
  FUN_00094008(uVar3);
  FUN_00092602();
  FUN_00091ab8();
  thunk_FUN_0006a4c4();
  return;
}



/* Sequential initializer chain: 10 unconditional calls and no other statements; shape-verified. The
   called sequence is the function's entire behavior; chain family members differ in callee sets. */

void f33_run_init_chain_91ffa(void)

{
  f33_return_only_stub_9262a();
  f33_return_only_stub_922e8();
  FUN_000917b2();
  FUN_000924e8();
  FUN_000923ec();
  FUN_00092616();
  FUN_00092b24();
  FUN_00093ab2();
  FUN_00093aba();
  f33_return_only_stub_91ade();
  return;
}



undefined4 FUN_0009202a(undefined1 param_1,undefined1 param_2)

{
  FUN_0008b0de(param_1,param_2);
  return 0;
}



/* Constant source: return 0; shape-classified from the canonical corpus. Callers receive this
   literal directly; its meaning is not recovered. */

undefined4 f33_return_const_0_9203c(void)

{
  return 0;
}



/* Constant source: return 0; shape-classified from the canonical corpus. Callers receive this
   literal directly; its meaning is not recovered. */

undefined4 f33_return_const_0_92040(void)

{
  return 0;
}



void FUN_00092044(undefined1 param_1,undefined1 param_2)

{
  FUN_0009202a(param_1,param_2);
  return;
}



void FUN_00092054(undefined1 param_1,undefined1 param_2)

{
  ((void)(param_1), (void)(param_2), f33_return_const_0_9203c());
  return;
}



void FUN_00092064(uchar param_1,ushort *param_2,ushort *param_3,ushort *param_4)

{
  int iVar1;
  int iVar2;
  short sVar3;
  int iVar4;
  
  iVar4 = 0;
  do {
    sVar3 = (short)iVar4;
    if (f33_app_session_timing_rows[sVar3].session == param_1) {
      *param_2 = f33_app_session_timing_rows[sVar3].response_timing_a_raw;
      *param_3 = f33_app_session_timing_rows[sVar3].transport_timing_b_raw;
      *param_4 = f33_app_session_timing_rows[sVar3].transport_timing_c_raw;
      return;
    }
    iVar2 = iVar4 + 1;
    iVar1 = iVar4 + -3;
    iVar4 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  return;
}



void FUN_00092094(undefined1 param_1)

{
  FUN_00091826(param_1);
  return;
}



void FUN_000920a2(undefined1 param_1)

{
  FUN_00091838(param_1);
  return;
}



void FUN_000920b0(undefined1 param_1)

{
  FUN_0009184a(param_1);
  return;
}



/* Map receive IDs2/3/4 to slots0/1/2; check communication permission and pending abort. Zero total
   length queries configured capacity only. Nonzero <=256 claims receive slot and arms watchdog0;
   larger returns3. Initial data pointer is not copied here. */

uint f33_dcm_start_of_reception
               (ushort receive_id,F33PduInfo *first_frame,ushort total_length,ushort *available)

{
  uint32_t puVar1;
  int iVar2;
  undefined4 *puVar3;
  uint uVar4;
  
  puVar1 = 0x23dfcu;
  uVar4 = 0;
  while (receive_id != f33_dcm_receive_route[(short)(ushort)uVar4].receive_id) {
    uVar4 = uVar4 + 1;
    if (2 < uVar4) {
      return 1;
    }
  }
  iVar2 = FUN_0009185c(uVar4,1);
  if (iVar2 != 1) {
    return 1;
  }
  iVar2 = FUN_00093f02(uVar4);
  if (iVar2 != 0) {
    return 1;
  }
  if (total_length == 0) {
    if ((uintptr_t)(available)!=(uintptr_t)((ushort *)0x0)) {
      *available = (ushort)(*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + uVar4 * 8 + 0x2094))));
    }
    return 0;
  }
  if ((uint)total_length <= ((*((uint *)camry_host_ptr((uint32_t)(puVar1 + uVar4 * 8 + 0x2094)))) & 0xffff)) {
    puVar3 = ((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + uVar4 * 8 + 0x2094)));
    uVar4 = f33_dcm_claim_receive_slot((ushort)uVar4);
    if (uVar4 != 1) {
      return 1;
    }
    if ((uintptr_t)(available)!=(uintptr_t)((ushort *)0x0)) {
      *available = (ushort)*puVar3;
    }
    f33_dcm_arm_software_timer('\0',(*((uint *)camry_host_ptr((uint32_t)(puVar1 + 0x2088)))));
    return 0;
  }
  return 3;
}



/* Require mapped active slot, communication admission and chunk length <=remaining capacity; copy
   into retained receive cursor and update16-bit received/remaining lengths. Rejection
   releases/reset slot and may restart inactivity. */

uint f33_dcm_copy_receive_data(ushort receive_id,F33PduInfo *chunk,ushort *available)

{
  uint32_t puVar1;
  int iVar2;
  int iVar3;
  uint uVar4;
  undefined4 uVar5;
  uint uVar6;
  
  puVar1 = 0x23dfcu;
  uVar6 = 1;
  iVar2 = FUN_00093f0e(receive_id);
  if ((iVar2 != 0xffff) && (iVar3 = FUN_00093e32(iVar2), iVar3 == 1)) {
    f33_dcm_cancel_software_timer('\0');
    iVar3 = FUN_0009185c(iVar2,1);
    if ((iVar3 == 1) && (uVar4 = FUN_000940ae(iVar2), chunk->length <= uVar4)) {
      uVar6 = f33_dcm_append_receive_chunk((ushort)iVar2,chunk,available);
    }
    else {
      uVar5 = FUN_00093f5a(iVar2);
      FUN_00093c9a(iVar2,1);
      FUN_00091f26(iVar2,uVar5);
      iVar2 = FUN_00093a8c();
      if (iVar2 != 1) {
        return 1;
      }
    }
    f33_dcm_arm_software_timer('\0',(*((uint *)camry_host_ptr((uint32_t)(puVar1 + 0x2088)))));
  }
  return uVar6;
}



/* Only active mapped slots participate. Success with permission arbitrates ownership; selected
   codes10..13 claim pending-dispatch slot, phase2, P2/overall timers and deferred event0 scheduling
   via timer6. Failure releases slot and considers S3 restart. */

void f33_dcm_receive_indication(ushort receive_id,uchar result)

{
  uint32_t puVar1;
  uchar timer_slot;
  ushort uVar2;
  int iVar3;
  int iVar4;
  uint uVar5;
  undefined4 uVar6;
  
  puVar1 = 0x23dfcu;
  iVar3 = FUN_00093f0e(receive_id);
  if (iVar3 == 0xffff) {
    return;
  }
  iVar4 = FUN_00093e32(iVar3);
  if (iVar4 != 1) {
    return;
  }
  f33_dcm_cancel_software_timer('\0');
  iVar4 = FUN_0009185c(iVar3,1);
  if ((iVar4 == 1) && (result == '\0')) {
    uVar5 = f33_dcm_arbitrate_completed_receive((ushort)iVar3);
    if (uVar5 - 0x10 < 4) {
      FUN_00091938(iVar3,0);
      FUN_00094008(iVar3);
      FUN_00091f72(2);
      FUN_00093c94(0);
      uVar2 = f33_dcm_select_response_deadline('\0',uVar5 != 0x13);
      f33_dcm_arm_software_timer('\x04',(uint)uVar2);
      uVar5 = f33_dcm_get_overall_request_timeout();
      f33_dcm_arm_software_timer('\x02',uVar5);
      iVar4 = FUN_00093a8c();
      if (iVar4 == 1) {
        f33_dcm_arm_software_timer('\0',(*((uint *)camry_host_ptr((uint32_t)(puVar1 + 0x2088)))));
      }
      timer_slot = '\x06';
      uVar5 = (uint)(*((ushort *)camry_host_ptr((uint32_t)(puVar1 + *(short *)(puVar1 + (short)(ushort)iVar3 * 0xc + 0x20ec) * 0x14 +
                               0x20ce))));
      goto LAB_000922a2;
    }
  }
  else {
    uVar6 = FUN_00093f5a(iVar3);
    FUN_00093c9a(iVar3,1);
    FUN_00091f26(iVar3,uVar6);
  }
  iVar3 = FUN_00093a8c();
  if (iVar3 != 1) {
    return;
  }
  uVar5 = (*((uint *)camry_host_ptr((uint32_t)(puVar1 + 0x2088))));
  timer_slot = '\0';
LAB_000922a2:
  f33_dcm_arm_software_timer(timer_slot,uVar5);
  return;
}



/* Event0 snapshots pending-dispatch slot and overall phase; phase2 installs current-dispatch slot
   and admits service, otherwise resets pending receive buffer. */

void f33_dcm_run_scheduled_request(void)

{
  undefined4 uVar1;
  int iVar2;
  
  thunk_FUN_0006a45e();
  uVar1 = FUN_0009400e();
  iVar2 = FUN_00092624();
  thunk_FUN_0006a4c4();
  if (iVar2 == 2) {
    FUN_00093c66(uVar1);
    f33_dcm_dispatch_retained_receive((ushort)uVar1);
  }
  else {
    thunk_FUN_0006a45e();
    FUN_00093c9a(uVar1,1);
    thunk_FUN_0006a4c4();
  }
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_922e8(void)

{
  return;
}



/* Timer6 callback tombstones all pending event0 slots then appends one fresh event0. Occupancy is
   not compacted and both statuses are discarded, so a full ring can reject the fresh append. */

void f33_dcm_post_receive_dispatch_after_delay(void)

{
  f33_dcm_invalidate_queued_event('\0','\0');
  f33_dcm_enqueue_event('\0');
  return;
}



/* WARNING: Type propagation algorithm not settling */

void FUN_00092300(void)

{
  undefined8 uVar1;
  int iVar2;
  undefined4 uVar3;
  int iVar4;
  ushort auStack_1e [7];
  
  uVar1 = 0x23dfc00000000;
  auStack_1e[0] = 0;
  auStack_1e[2] = 0;
  auStack_1e[1] = 0;
  thunk_FUN_0006a45e();
  uVar3 = FUN_00092624();
  FUN_00093f66(camry_host_addr(auStack_1e + 1), auStack_1e, uVar3);
  thunk_FUN_0006a4c4();
  for (iVar4 = 0;
      (int)(iVar4 - (uint)auStack_1e[0]) < 0 !=
      (iVar4 < 0 && -1 < (int)(iVar4 - (uint)auStack_1e[0])); iVar4 = iVar4 + 1) {
    iVar2 = (int)((ulonglong)uVar1 >> 0x20);
    if ((*((char *)camry_host_ptr((uint32_t)(*(short *)((short)auStack_1e[iVar4 * 2U + 2] * 0xc + iVar2 + 0x20ec) * 0x14 +
                  iVar2 + 0x20d5)))) == '\x01') {
      FUN_000923de(auStack_1e[iVar4 * 2U + 1]);
    }
    uVar3 = FUN_00093f5a(auStack_1e[iVar4 * 2U + 2]);
    FUN_00093c9a(auStack_1e[iVar4 * 2U + 2],1);
    FUN_00091f26(auStack_1e[iVar4 * 2U + 2],uVar3);
    FUN_00093ef6(auStack_1e[iVar4 * 2U + 2],0);
  }
  return;
}



void FUN_0009238c(void)

{
  short *psVar1;
  uint32_t puVar2;
  undefined4 uVar3;
  
  puVar2 = 0x23dfcu;
  thunk_FUN_0006a45e();
  uVar3 = FUN_0009407c();
  thunk_FUN_0006a4c4();
  psVar1 = ((short *)camry_host_ptr((uint32_t)(puVar2 + (short)uVar3 * 0xc + 0x20ec)));
  FUN_000923de((*((undefined2 *)camry_host_ptr((uint32_t)((uint)(ushort)psVar1[2] * 0xc +
                 *(int *)(*(int *)((uint)(ushort)psVar1[1] * 4 +
                                  *(int *)(puVar2 + *psVar1 * 0x14 + 0x20c4)) + 4) + 6)))));
  FUN_00093ef6(uVar3,0);
  return;
}



void FUN_000923de(undefined2 param_1)

{
  FUN_00081e90(param_1);
  return;
}



void FUN_000923ec(void)

{
  int iVar1;
  uint uVar2;
  uint32_t puVar3;
  puVar3 = 0xfebeb800u;
  thunk_FUN_0006a45e();
  uVar2 = 0;
  do {
    iVar1 = uVar2 * 4;
    uVar2 = uVar2 + 1;
    (*((undefined4 *)camry_host_ptr((uint32_t)(puVar3 + iVar1 + -0x5eac)))) = 0;
  } while (uVar2 < 2);
  thunk_FUN_0006a4c4();
  return;
}



/* Return0 after snapshot of5954[2] undercritical. Output0 for locked; scan first set bit perword,
   later nonzero second word can replace first-word level.92470 maintains one-hot level1..63 or
   allzero. Caller91AE0 supplies the output pointer. Fix lost pointer ABI causing91AE0 corpus
   no-argument call. */

uint f33_dcm_read_security_bitmap_level(uchar *level)

{
  uint *puVar1;
  int iVar2;
  uint uVar3;
  uint32_t puVar4;
  uint uVar5;
  uint auStack_10 [2];
  
  puVar4 = 0xfebeb800u;
  *level = '\0';
  thunk_FUN_0006a45e();
  uVar3 = 0;
  do {
    iVar2 = uVar3 * 4;
    puVar1 = auStack_10 + uVar3;
    uVar3 = uVar3 + 1;
    *puVar1 = (*((uint *)camry_host_ptr((uint32_t)(puVar4 + iVar2 + -0x5eac))));
  } while (uVar3 < 2);
  thunk_FUN_0006a4c4();
  uVar3 = 0;
  do {
    uVar5 = 0;
    do {
      puVar1 = auStack_10 + uVar3;
      if ((*puVar1 & 1) != 0) {
        *level = (char)uVar5 + (char)uVar3 * ' ' + '\x01';
        break;
      }
      uVar5 = uVar5 + 1;
      *puVar1 = *puVar1 >> 1;
    } while (uVar5 < 0x20);
    uVar3 = uVar3 + 1;
    if (1 < uVar3) {
      return 0;
    }
  } while( true );
}



/* For level<64 store two-word one-hot bitmap5954, or zero for level0, then no-op92054 notification.
   Called on keyaccept BEFORE response and on session publication BEFORE session callbacks. */

void f33_dcm_publish_security_level(uchar level)

{
  uint uVar1;
  uint uVar2;
  uint32_t puVar3;
  uint uVar4;
  uchar uStack_11;
  int aiStack_10 [2];
  
  puVar3 = 0xfebeb800u;
  uVar4 = (uint)level;
  uStack_11 = '\0';
  f33_dcm_read_security_bitmap_level(&uStack_11);
  uVar2 = 0;
  do {
    uVar1 = uVar2 + 1;
    aiStack_10[uVar2] = 0;
    uVar2 = uVar1;
  } while (uVar1 < 2);
  if (uVar4 < 0x40) {
    if (uVar4 != 0) {
      aiStack_10[(int)(uVar4 - 1 & 0xff) >> 5] = 1 << (uVar4 - 1 & 0x1f);
    }
    thunk_FUN_0006a45e();
    uVar2 = 0;
    do {
      uVar1 = uVar2 + 1;
      (*((int *)camry_host_ptr((uint32_t)(puVar3 + uVar2 * 4 + -0x5eac)))) = aiStack_10[uVar2];
      uVar2 = uVar1;
    } while (uVar1 < 2);
    thunk_FUN_0006a4c4();
    FUN_00092054(uStack_11,uVar4);
  }
  return;
}



void FUN_000924e8(void)

{
  f33_app_dcm_session_snapshot.current = '\x01';
  f33_app_dcm_session_snapshot.previous = '\x01';
  f33_app_dcm_session_snapshot.target = '\x01';
  f33_app_dcm_session_snapshot.pending_publication = '\0';
  return;
}



/* Copy current595C under the recovered critical section and return0; session membership is checked
   by callers. */

uint f33_dcm_read_session_snapshot(uchar *session)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  thunk_FUN_0006a45e();
  *session = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x5ea4)))));
  thunk_FUN_0006a4c4();
  return 0;
}



/* Invoke ROM25F48 callbacks968CC and9704E in order, then92044\u21928B0DE\u21924D582/6A156. Network
   restore effects owned by network slice. Security bits already cleared by publication callers;
   challenge/client reset occurs later4D582. Invoke ROM25F48 callbacks968CC and9704E in order,
   then92044→8B0DE→4D582/6A156. */

void f33_dcm_notify_session_publication(uchar old_session,uchar new_session)

{
  int iVar1;
  int iVar2;
  undefined8 uVar3;
  int iVar4;
  
  uVar3 = 0x23dfc00000000;
  iVar4 = 0;
  do {
    (*(int (*)())*(code **)(iVar4 * 4 + (int)((ulonglong)uVar3 >> 0x20) + 0x214c))(old_session,new_session);
    iVar2 = iVar4 + 1;
    iVar1 = iVar4 + -1;
    iVar4 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  FUN_00092044(old_session,new_session);
  return;
}



/* Under98CDA/98CE6 store target595E and previous595D. defer==1 sets pending595F only; otherwise
   storecurrent595C, clearpending, then security0 and92518 callbacks outside critical section. Even
   same-session publication runs notifications. */

void f33_dcm_stage_or_publish_session(uchar target,uchar defer)

{
  uchar uVar1;
  uint32_t puVar2;
  puVar2 = 0xfebeb800u;
  thunk_FUN_0006a45e();
  if (defer == '\x01') {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x5ea2))))) = target;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x5ea1))))) = 1;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x5ea3))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x5ea4)))));
    thunk_FUN_0006a4c4();
  }
  else {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x5ea2))))) = target;
    uVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x5ea4)))));
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x5ea4))))) = target;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x5ea1))))) = 0;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x5ea3))))) = uVar1;
    thunk_FUN_0006a4c4();
    FUN_00091e12(0);
    f33_dcm_notify_session_publication((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x5ea3))))),target);
  }
  return;
}



void FUN_000925a0(undefined1 param_1)

{
  ((void)(param_1), f33_return_const_0_9260c());
  return;
}



/* commit1 publishes595E to595C only if595F==1, retaining pending for925DC notification; other
   values clearpending without rolling current session back. Distinct from925DC security/application
   notifications. */

void f33_dcm_commit_or_discard_staged_session(uchar commit)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  thunk_FUN_0006a45e();
  if (commit == '\x01') {
    if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x5ea1))))) == '\x01') {
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x5ea4))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x5ea2)))));
    }
  }
  else {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x5ea1))))) = 0;
  }
  thunk_FUN_0006a4c4();
  return;
}



/* When595F==1, clear published security, invoke92518(old595D,target595E), then clearpending. Does
   not itself storecurrent session. Called at completed-response joins, independently of SID10 exact
   immediate policy. */

void f33_dcm_finish_staged_session_notifications(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  if (f33_app_dcm_session_snapshot.pending_publication == '\x01') {
    FUN_00091e12(0);
    f33_dcm_notify_session_publication((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x5ea3))))),(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x5ea2))))));
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x5ea1))))) = 0;
  }
  return;
}



void FUN_00092602(void)

{
  return;
}



/* Constant source: return 0; shape-classified from the canonical corpus. Callers receive this
   literal directly; its meaning is not recovered. */

undefined4 f33_return_const_0_9260c(void)

{
  return 0;
}



void FUN_00092610(uchar param_1)

{
  f33_dcm_request_phase = param_1;
  return;
}



void FUN_00092616(void)

{
  FUN_00092610(0);
  return;
}



uchar FUN_00092624(void)

{
  return f33_dcm_request_phase;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_9262a(void)

{
  return;
}



undefined4 FUN_0009262c(int *param_1,char *param_2,int *param_3)

{
  ushort uVar1;
  uint uVar2;
  
  uVar1 = *(ushort *)(param_2 + 2);
  uVar2 = (uint)uVar1 + (uint)*(ushort *)(param_3 + 1);
  if (-1 < (int)(*(ushort *)(param_1 + 1) - uVar2) && *(ushort *)(param_1 + 1) != uVar2) {
    return 2;
  }
  uVar2 = 0;
  if (*param_2 == '\0') {
    for (; uVar2 < *(ushort *)(param_1 + 1); uVar2 = uVar2 + 1 & 0xffff) {
      (*((undefined1 *)camry_host_ptr((uint32_t)(*param_1 + uVar2)))) = (*((undefined1 *)camry_host_ptr((uint32_t)(*param_3 + uVar2))));
    }
  }
  else {
    uVar2 = 0;
    if (*param_2 != '\x01') {
      for (; uVar2 < *(ushort *)(param_1 + 1); uVar2 = uVar2 + 1 & 0xffff) {
        (*((undefined1 *)camry_host_ptr((uint32_t)(*param_1 + uVar2)))) = (*((undefined1 *)camry_host_ptr((uint32_t)(*param_3 + uVar2))));
      }
      return 0;
    }
    *(ushort *)(param_3 + 1) = uVar1 + *(ushort *)(param_3 + 1);
    *param_3 = *param_3 - (uint)uVar1;
    for (; uVar2 < *(ushort *)(param_1 + 1); uVar2 = uVar2 + 1 & 0xffff) {
      (*((undefined1 *)camry_host_ptr((uint32_t)(*param_1 + uVar2)))) = (*((undefined1 *)camry_host_ptr((uint32_t)(*param_3 + uVar2))));
    }
  }
  *(short *)(param_3 + 1) = (short)param_3[1] - (short)uVar2;
  *param_3 = *param_3 + uVar2;
  return 0;
}



/* Require matching configured confirmation ID and state30/31/32/40. Copy response cursor bytes into
   lower buffer, advance pointer/decrement16-bit length; retry descriptors may rewind. Rearm
   watchdog1. This copy is not final confirmation. */

uint f33_dcm_copy_transmit_data
               (ushort transmit_id,F33PduInfo *chunk,F33DcmRetryInfo *retry,ushort *available)

{
  uint32_t puVar1;
  int *piVar2;
  uint uVar3;
  undefined4 uVar4;
  int iVar5;
  uint uVar6;
  
  puVar1 = 0x23dfcu;
  uVar6 = 0;
  piVar2 = (int *)f33_return_const_febe5978_93690();
  uVar3 = FUN_00093ebc();
  if ((uVar3 == transmit_id) && ((uintptr_t)(chunk)!=(uintptr_t)((F33PduInfo *)0x0))) {
    uVar4 = FUN_00092b34();
    iVar5 = FUN_00092c46(uVar4);
    if (iVar5 == 1) {
      f33_dcm_cancel_software_timer('\x01');
      if (chunk->length == 0) {
        if ((uintptr_t)(available)==(uintptr_t)((ushort *)0x0)) {
          uVar6 = 1;
        }
        else {
          *available = *(ushort *)(piVar2 + 1);
          if (((uintptr_t)(retry)!=(uintptr_t)((F33DcmRetryInfo *)0x0)) && (retry->retry_kind == '\0')) {
            *(undefined2 *)(piVar2 + 1) = 0;
            *available = 0;
          }
        }
      }
      else {
        if ((uintptr_t)(retry)==(uintptr_t)((F33DcmRetryInfo *)0x0)) {
          if (*(ushort *)(piVar2 + 1) < chunk->length) {
            uVar6 = 2;
          }
          else {
            for (uVar3 = 0; uVar3 < chunk->length; uVar3 = uVar3 + 1 & 0xffff) {
              ((uint8_t *)camry_host_ptr((uint32_t)(chunk->data)))[uVar3] = (*((uchar *)camry_host_ptr((uint32_t)(*piVar2 + uVar3))));
            }
            *(short *)(piVar2 + 1) = (short)piVar2[1] - (short)uVar3;
            *piVar2 = *piVar2 + uVar3;
          }
        }
        else {
          uVar6 = FUN_0009262c(chunk,retry,piVar2);
        }
        if ((uintptr_t)(available)!=(uintptr_t)((ushort *)0x0)) {
          *available = *(ushort *)(piVar2 + 1);
        }
      }
      f33_dcm_arm_software_timer('\x01',(*((uint *)camry_host_ptr((uint32_t)(puVar1 + 0x2088)))));
      return uVar6;
    }
  }
  return 1;
}



/* Positive0 maps success/failure0/1; negative1 maps2/3; suppressed positive2 always0; other
   dispositions including silent3 and pending10 map2. Return is four-valued, not bool. */

uint f33_dcm_map_response_delivery_result(uchar disposition,uchar transport_result)

{
  if (disposition == '\0') {
    return (uint)(transport_result != '\0');
  }
  if (disposition == '\x01') {
    if (transport_result != '\0') {
      return 3;
    }
  }
  else if (disposition == '\x02') {
    return 0;
  }
  return 2;
}



undefined4 FUN_000927cc(char param_1,char param_2)

{
  undefined4 uVar1;
  int iVar2;
  uint uVar3;
  
  if (param_2 == '\0') {
    return 0;
  }
  iVar2 = FUN_00092b66();
  if (iVar2 != 0) {
    return 0;
  }
  f33_dcm_cancel_software_timer('\x03');
  f33_dcm_cancel_software_timer('\x04');
  f33_dcm_cancel_software_timer('\x02');
  FUN_00093676();
  if (param_1 == '0') {
    uVar3 = f33_dcm_enqueue_event('(');
    if (uVar3 != 0) {
LAB_00092828:
      f33_dcm_arm_software_timer('\x01',0);
      return 0;
    }
    uVar1 = 0x25;
  }
  else {
    uVar3 = f33_dcm_enqueue_event(')');
    if (uVar3 != 0) goto LAB_00092828;
    uVar1 = 0x50;
  }
  FUN_00092a86(uVar1);
  return 1;
}



/* Matching configured ID pops queue head, latches mapped result and explicit-pending flag.
   Pending30..32 restarts pending timers and may queue29/1; final40 finalizes session/receive
   ownership and queues29. Actual callback notification occurs later. */

void f33_dcm_transmit_confirmation(ushort transmit_id,uchar result)

{
  undefined4 uVar1;
  ushort uVar2;
  uint uVar3;
  int iVar4;
  int iVar5;
  uchar uStack_19;
  
  uVar3 = FUN_00093ebc();
  uStack_19 = 0xff;
  if (uVar3 == transmit_id) {
    thunk_FUN_0006a45e();
    FUN_00093696(&uStack_19);
    thunk_FUN_0006a4c4();
    if (uStack_19 != 0xff) {
      iVar4 = FUN_00092b34();
      uVar3 = f33_dcm_map_response_delivery_result(uStack_19,result);
      iVar5 = FUN_00092f6a();
      FUN_00092a74(uVar3,iVar5);
      if (iVar4 - 0x30U < 3) {
        uVar3 = FUN_00093c5a();
        uVar2 = f33_dcm_select_response_deadline('\x01','\x01');
        f33_dcm_cancel_software_timer('\x01');
        f33_dcm_arm_software_timer('\x03',uVar3);
        f33_dcm_arm_software_timer('\x04',(uint)uVar2);
        if (iVar4 == 0x30) {
          FUN_00092a86(0x11);
          iVar4 = FUN_000927cc(0x30,result);
          if ((iVar4 == 0) && (iVar5 == 1)) {
            f33_dcm_enqueue_event(')');
          }
        }
        else {
          iVar5 = FUN_000927cc(iVar4,result);
          if ((iVar5 == 0) && (uVar3 = f33_dcm_enqueue_event('\x01'), uVar3 == 0)) {
            if (iVar4 == 0x31) {
              uVar1 = 0x21;
            }
            else {
              uVar1 = 0x22;
            }
            FUN_00092a86(uVar1);
          }
        }
        FUN_00092f70(0);
      }
      else if (iVar4 == 0x40) {
        f33_dcm_cancel_software_timer('\x01');
        FUN_0009364a(result);
        uVar3 = f33_dcm_enqueue_event(')');
        if (uVar3 == 0) {
          FUN_00092a86(0x50);
        }
        else {
          f33_dcm_arm_software_timer('\x01',0);
        }
      }
    }
  }
  return;
}



void FUN_00092946(uint param_1)

{
  uint uVar1;
  
  uVar1 = FUN_00093ebc();
  if (uVar1 == (param_1 & 0xffff)) {
    FUN_00092a74(0,0);
    f33_dcm_enqueue_event(')');
  }
  return;
}



void FUN_00092a1e(undefined2 param_1)

{
  uint32_t puVar1;
  short sVar2;
  
  puVar1 = 0x23dfcu;
  sVar2 = FUN_00093c60();
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)((*((short *)camry_host_ptr((uint32_t)(puVar1 + sVar2 * 0xc + 0x20ec)))) * 0x14 + 0x20d5))))) == '\x01') {
    FUN_00092a60(param_1);
  }
  f33_dcm_cancel_software_timer('\x01');
  return;
}



void FUN_00092a52(undefined2 param_1)

{
  FUN_00081b92(param_1);
  return;
}



void FUN_00092a60(undefined2 param_1)

{
  FUN_00081bac(param_1);
  return;
}



/* WARNING: This is an inlined function */
/* Return5970 inR10 while preserving incomingR6/R7. Inline exact leaf p-code where callers forward
   pointer arguments through this getter. */

F33DcmResponseQueue * f33_dcm_get_response_queue(void)

{
  return ((undefined *)camry_host_ptr(0xfebe5970u));
}



/* WARNING: Inlined function: f33_dcm_get_response_queue */

void FUN_00092a74(uchar param_1,uchar param_2)

{
  f33_dcm_response_queue.notification_result = param_1;
  f33_dcm_response_queue.pending_notification = param_2;
  return;
}



void FUN_00092a86(undefined1 param_1)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  thunk_FUN_0006a45e();
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x5e9c))))) = param_1;
  thunk_FUN_0006a4c4();
  return;
}



/* Initialize shared response cursor/capacity and fixed sentinel plus four response nodes:
   positive0,negative1,silent3,pending10. Reset forced/explicit pending flags5965/5966; do not erase
   handler-retained request copies. */

void f33_dcm_reset_response_queue(void)

{
  undefined4 *puVar1;
  uint32_t puVar2;
  puVar2 = 0xfebeb800u;
  f33_dcm_pending_negative_response[0] = '\0';
  f33_dcm_final_negative_response[0] = '\0';
  f33_dcm_response_queue.remaining_length = 0;
  f33_dcm_response_queue.copy_cursor = 0;
  FUN_00093ce6(((undefined4 *)camry_host_ptr((uint32_t)(0xfebe5978))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x5e9a))))) = 0;
  (*((undefined4 *)camry_host_ptr((uint32_t)(puVar2 + -0x5e68)))) = (*((undefined4 *)camry_host_ptr((uint32_t)(puVar2 + -0x5e88))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x5e9b))))) = 0;
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar2 + -0x5e44)))) = 0;
  (*((undefined4 *)camry_host_ptr((uint32_t)(puVar2 + -0x5e48)))) = 0;
  *(uchar **)(puVar2 + -0x5e38) = f33_dcm_pending_negative_response;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x5e50))))) = 1;
  *(uchar **)(puVar2 + -0x5e58) = f33_dcm_final_negative_response;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x5e60))))) = 0;
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar2 + -0x5e64)))) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar2 + -0x5e84))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x5e40))))) = 3;
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar2 + -0x5e34)))) = 3;
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar2 + -0x5e54)))) = 3;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x5e30))))) = 0x10;
  puVar1 = ((undefined4 *)camry_host_ptr((uint32_t)(puVar2 + -0x5e7c)));
  *(undefined4 **)(puVar2 + -0x5e90) = puVar1;
  *(undefined4 **)(puVar2 + -0x5e8c) = puVar1;
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar2 + -0x5e74)))) = 0;
  (*((undefined4 *)camry_host_ptr((uint32_t)(puVar2 + -0x5e78)))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x5e70))))) = 0;
  *puVar1 = 0;
  return;
}



void FUN_00092b24(void)

{
  FUN_00092a9c();
  f33_dcm_reset_response_queue();
  return;
}



undefined1 FUN_00092b34(void)

{
  undefined1 uVar1;
  uint32_t puVar2;
  puVar2 = 0xfebeb800u;
  thunk_FUN_0006a45e();
  uVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x5e9c)))));
  thunk_FUN_0006a4c4();
  return uVar1;
}



void FUN_00092b4a(void)

{
  int iVar1;
  
  iVar1 = FUN_00092b34();
  if (iVar1 == 0) {
    f33_dcm_reset_response_queue();
    FUN_00092a86(0x10);
  }
  return;
}



undefined1 FUN_00092b66(void)

{
  uint32_t puVar1;
  short sVar2;
  
  puVar1 = 0x23dfcu;
  sVar2 = FUN_00093c60();
  return (*((undefined1 *)camry_host_ptr((uint32_t)(*(int *)(*(int *)((uint)*(ushort *)(puVar1 + sVar2 * 0xc + 0x20ee) * 4 +
                            *(int *)(puVar1 + *(short *)(puVar1 + sVar2 * 0xc + 0x20ec) * 0x14 +
                                              0x20c4)) + 8) + 8))));
}



int * FUN_00092b98(undefined4 *param_1)

{
  int *piVar1;
  int iVar2;
  int *piVar3;
  int *piVar4;
  
  piVar3 = (int *)0x0;
  if (((((uintptr_t)(param_1)!=(uintptr_t)((undefined4 *)0x0)) && (piVar4 = (int *)*param_1,(uintptr_t)(piVar4)!=(uintptr_t)((int *)0x0))) &&
      (piVar1 = (int *)*piVar4,(uintptr_t)(piVar1)!=(uintptr_t)((int *)0x0))) &&
     (iVar2 = *piVar1, *piVar4 = iVar2, piVar3 = piVar1, iVar2 == 0)) {
    param_1[1] = camry_host_addr(f33_dcm_response_node);
  }
  return piVar3;
}



undefined4 FUN_00092bc2(undefined4 *param_1)

{
  undefined4 uVar1;
  
  uVar1 = 0;
  if (((uintptr_t)(param_1)!=(uintptr_t)((undefined4 *)0x0)) && ((uintptr_t)((undefined4 *)*param_1)!=(uintptr_t)((undefined4 *)0x0))) {
    uVar1 = *(undefined4 *)*param_1;
  }
  return uVar1;
}



/* WARNING: Inlined function: f33_dcm_get_response_queue */
/* Sequential initializer chain: 4 unconditional calls and no other statements; shape-verified. The
   called sequence is the function's entire behavior; chain family members differ in callee sets. */

void f33_run_init_chain_92bfe(void)

{
  thunk_FUN_0006a45e();
  FUN_00092b98(((undefined4 *)camry_host_ptr((uint32_t)((0xfebe5970u)))));
  FUN_00092bd8();
  thunk_FUN_0006a4c4();
  return;
}



/* WARNING: Inlined function: f33_dcm_get_response_queue */

void FUN_00092c1e(uchar param_1)

{
  uchar disposition;
  int iVar1;
  
  iVar1 = FUN_00092bc2(((undefined4 *)camry_host_ptr((uint32_t)((0xfebe5970u)))));
  disposition = 0xff;
  if (iVar1 != 0) {
    disposition = (*((uchar *)camry_host_ptr((uint32_t)(iVar1 + 0xc))));
  }
  f33_dcm_map_response_delivery_result(disposition,param_1);
  return;
}



undefined4 FUN_00092c46(uint param_1)

{
  uint uVar1;
  undefined4 uVar2;
  
  uVar1 = (param_1 & 0xff) - 0x30;
  uVar2 = 0;
  if ((uVar1 < 3) || (uVar1 == 0x10)) {
    uVar2 = 1;
  }
  return uVar2;
}



/* WARNING: Inlined function: f33_dcm_get_response_queue */

undefined4 FUN_00092d38(undefined1 *param_1)

{
  undefined1 uVar1;
  int iVar2;
  undefined4 uVar3;
  
  iVar2 = FUN_00092bc2(((undefined4 *)camry_host_ptr((uint32_t)((0xfebe5970u)))));
  if (iVar2 == 0) {
    uVar1 = 0xff;
    uVar3 = 0;
  }
  else {
    f33_dcm_response_queue.copy_cursor = camry_host_addr(*(uchar **)(iVar2 + 4));
    uVar3 = 0xfebe5978;
    f33_dcm_response_queue.remaining_length = (*((ushort *)camry_host_ptr((uint32_t)(iVar2 + 8))));
    uVar1 = (*((undefined1 *)camry_host_ptr((uint32_t)(iVar2 + 0xc))));
  }
  *param_1 = uVar1;
  return uVar3;
}



undefined4 FUN_00092d72(void)

{
  int iVar1;
  undefined4 uVar2;
  
  uVar2 = 0;
  iVar1 = FUN_00092b34();
  if ((((iVar1 == 0) || (iVar1 == 0x21 || iVar1 == 0x22)) || (iVar1 == 0x31 || iVar1 == 0x32)) ||
     ((iVar1 == 0x40 || (iVar1 == 0x50)))) {
    uVar2 = 1;
  }
  return uVar2;
}



void FUN_00092da0(undefined1 param_1)

{
  int iVar1;
  undefined4 uVar2;
  
  iVar1 = FUN_00092d72();
  if (iVar1 == 1) {
    f33_dcm_restart_inactivity_after_request();
    FUN_00091c82(param_1,0);
  }
  else {
    FUN_00091e6e();
  }
  uVar2 = FUN_00093c60();
  FUN_00091938(uVar2,1);
  return;
}



void FUN_00092dd2(undefined1 param_1)

{
  FUN_00092da0(param_1);
  f33_dcm_reset_response_queue();
  FUN_00092a9c();
  return;
}



void FUN_00092de8(undefined1 param_1)

{
  FUN_00091f64(0);
  FUN_00092dd2(param_1);
  return;
}



void FUN_00092eae(ushort param_1,F33PduInfo *param_2)

{
  int iVar1;
  uint uVar2;
  
  iVar1 = FUN_00092b66();
  uVar2 = f33_dcm_submit_transport_response(param_1,param_2,'\x11');
  if (uVar2 == 0) {
    if (iVar1 == 0) {
      FUN_00091b08(1,1);
    }
    else {
      FUN_00091f64(0);
    }
  }
  else {
    if ((uVar2 == 0x83) || (iVar1 != 0)) {
      FUN_00091f64(0);
    }
    else {
      FUN_00091b08(1,0);
    }
    FUN_00092dd2(3);
  }
  return;
}



void FUN_00092f08(void)

{
  undefined4 uVar1;
  F33PduInfo *response;
  int iVar2;
  uchar uStack_d;
  
  uStack_d = '\0';
  uVar1 = FUN_00093e82();
  response = (F33PduInfo *)FUN_00092d38(&uStack_d);
  if ((uintptr_t)(response)!=(uintptr_t)((F33PduInfo *)0x0)) {
    iVar2 = FUN_00092b34();
    if (iVar2 == 0x21) {
      FUN_00092a86(0x40);
      f33_dcm_try_final_response((ushort)uVar1,response,uStack_d);
    }
    else if (iVar2 == 0x22) {
      f33_dcm_cancel_software_timer('\x03');
      f33_dcm_cancel_software_timer('\x04');
      FUN_00092a86(0x40);
      FUN_00092eae(uVar1,response);
    }
  }
  return;
}



uchar FUN_00092f6a(void)

{
  return f33_dcm_explicit_pending_notification;
}



void FUN_00092f70(uchar param_1)

{
  f33_dcm_explicit_pending_notification = param_1;
  return;
}



void FUN_00093154(undefined1 *param_1,undefined1 param_2,undefined1 param_3)

{
  param_1[1] = param_2;
  *param_1 = 0x7f;
  param_1[2] = param_3;
  return;
}



void FUN_00093162(undefined1 param_1,undefined1 param_2)

{
  FUN_00093154(f33_dcm_final_negative_response,param_1,param_2);
  return;
}



F33DcmResponseNode * FUN_0009317a(uint param_1)

{
  return f33_dcm_response_node + (param_1 & 0xff);
}



/* Automatic deadline sets5965=1 and sends NRC78 from state10; states23/24 first cancel old service
   and may cancel lower Tx. Explicit-pending callback latch5966 is not set here. */

void f33_dcm_p2_response_deadline(uchar service_id)

{
  uint32_t puVar1;
  ushort transmit_id;
  int iVar2;
  undefined4 uVar3;
  F33PduInfo *response;
  
  puVar1 = 0xfebeb800u;
  iVar2 = FUN_00092b34();
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x5e9b))))) = 1;
  if (iVar2 != 0x10) {
    if (iVar2 == 0x23) {
      FUN_00091e6e();
    }
    else {
      if (iVar2 != 0x24) {
        return;
      }
      FUN_00091e6e();
      uVar3 = FUN_000940ca();
      FUN_00092a1e(uVar3);
    }
  }
  thunk_FUN_0006a45e();
  response = f33_dcm_enqueue_pending_response(service_id);
  thunk_FUN_0006a4c4();
  FUN_00092a86(0x30);
  transmit_id = FUN_00093e82();
  f33_dcm_try_pending_response(transmit_id,response,'\0');
  return;
}



void FUN_0009338e(void)

{
  undefined4 uVar1;
  int iVar2;
  
  uVar1 = FUN_000940ca();
  FUN_00093c94(0);
  iVar2 = FUN_00092b34();
  if (iVar2 == 0x25) {
    FUN_00091f90();
    FUN_00092a9c();
  }
  else {
    if (((iVar2 == 0x10 || iVar2 == 0x11) || (iVar2 == 0x23)) || (iVar2 == 0x30)) {
      FUN_00092a86(0x10);
      FUN_00091f64(0);
    }
    else {
      if (iVar2 != 0x24) {
        return;
      }
      FUN_00092a86(0x10);
      FUN_00091f64(0);
      FUN_00092a1e(uVar1);
    }
    f33_dcm_reset_response_queue();
  }
  return;
}



/* Explicit NRC78 in state10 cancels timer4, sets5965/5966 and submits pending30; state11 queues
   pending20 until timer3; state30 coalesces by setting notification latch only. */

void f33_dcm_request_explicit_pending_response(uchar service_id)

{
  uint32_t puVar1;
  undefined1 extraout_r6;
  ushort transmit_id;
  int iVar2;
  F33PduInfo *response;
  
  puVar1 = 0xfebeb800u;
  iVar2 = FUN_00092b34();
  if (iVar2 == 0x10) {
    f33_dcm_cancel_software_timer('\x04');
    FUN_00092f70(1);
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x5e9b))))) = extraout_r6;
    thunk_FUN_0006a45e();
    response = f33_dcm_enqueue_pending_response(service_id);
    thunk_FUN_0006a4c4();
    FUN_00092a86(0x30);
    transmit_id = FUN_00093e82();
    f33_dcm_try_pending_response(transmit_id,response,'\x01');
  }
  else if (iVar2 == 0x11) {
    FUN_00092f70(1);
    thunk_FUN_0006a45e();
    f33_dcm_enqueue_pending_response(service_id);
    thunk_FUN_0006a4c4();
    FUN_00092a86(0x20);
  }
  else if (iVar2 == 0x30) {
    FUN_00092f70(1);
  }
  return;
}



void FUN_0009362c(void)

{
  undefined4 uVar1;
  
  uVar1 = FUN_00093c60();
  f33_dcm_restart_inactivity_after_request();
  FUN_00091938(uVar1,1);
  f33_dcm_reset_response_queue();
  return;
}



void FUN_0009364a(char param_1)

{
  undefined4 uVar1;
  int iVar2;
  
  if (param_1 != '\0') {
    iVar2 = FUN_00092b66();
    if (iVar2 != 0) {
      uVar1 = 0;
      goto LAB_0009366a;
    }
    FUN_00091b08(1,1);
  }
  uVar1 = 1;
LAB_0009366a:
  FUN_00091f64(uVar1);
  FUN_0009362c();
  return;
}



void FUN_00093676(void)

{
  FUN_00091b08(1,1);
  FUN_00091f64(1);
  FUN_0009362c();
  return;
}



/* Constant source: return 0xfebe5978; shape-classified from the canonical corpus. Callers receive
   this literal directly; its meaning is not recovered. */

undefined4 f33_return_const_febe5978_93690(void)

{
  return 0xfebe5978;
}



/* WARNING: Inlined function: f33_dcm_get_response_queue */

int FUN_00093696(undefined1 *param_1)

{
  int iVar1;
  int iVar2;
  
  iVar1 = camry_host_addr(FUN_00092b98(((undefined4 *)camry_host_ptr((uint32_t)((0xfebe5970u))))));
  if (iVar1 == 0) {
    *param_1 = 0xff;
    iVar2 = 0;
  }
  else {
    iVar2 = iVar1 + 4;
    *param_1 = (*((undefined1 *)camry_host_ptr((uint32_t)(iVar1 + 0xc))));
    FUN_00092bd8();
  }
  return iVar2;
}



/* WARNING: Inlined function: f33_dcm_get_response_queue */
/* Read current response-queue root+10/+11 and store through preserved incomingR6/R7 pointers. Does
   not clear the latch. Caller91C92 selects final notification versus operation3 from this snapshot.
    */

void f33_dcm_snapshot_response_notification(uchar *result,uchar *pending_notification)

{
  *result = f33_dcm_response_queue.notification_result;
  *pending_notification = f33_dcm_response_queue.pending_notification;
  return;
}



undefined4 FUN_00093a70(undefined1 *param_1)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  thunk_FUN_0006a45e();
  *param_1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x5e2c)))));
  thunk_FUN_0006a4c4();
  return 0;
}



undefined4 FUN_00093a8c(void)

{
  ushort uVar1;
  int iVar2;
  
  iVar2 = FUN_00092624();
  uVar1 = f33_dcm_count_receiving_slots();
  if (iVar2 == 2) {
    if (uVar1 < 2) {
      return 0;
    }
  }
  else if (uVar1 == 0) {
    return 0;
  }
  return 1;
}



/* Single constant publisher: DAT_febe59d4 = 0xff; Shape-classified from the canonical corpus; the
   target cell is not yet named, so the written state's meaning is unknown. */

void FUN_00093ab2(void)

{
  DAT_febe59d4 = 0xff;
  return;
}



void FUN_00093aba(void)

{
  uint uVar1;
  uint uVar2;
  uchar *puVar3;
  uint uVar4;
  
  f33_dcm_pending_transport_accepted = '\0';
  f33_dcm_shared_response_buffer[0] = '\0';
  f33_dcm_pending_dispatch_receive_slot = 0;
  f33_dcm_current_dispatch_receive_slot = 0;
  f33_dcm_retained_p2_star_raw = 0;
  f33_dcm_pending_spacing_raw = 0;
  DAT_febe59e4 = 0;
  DAT_febe59e6 = 0;
  f33_dcm_displaced_transmit_id = 0;
  f33_dcm_zero_p2_deadline = '\0';
  f33_dcm_zero_overall_timeout = '\0';
  uVar4 = 0;
  do {
    f33_dcm_receive_buffer_state[uVar4].receiving = '\0';
    puVar3 = ((void *)camry_host_ptr((uint32_t)(f33_dcm_receive_buffer_configuration[uVar4].base)));
    uVar1 = uVar4 + 1;
    f33_dcm_receive_buffer_state[uVar4].write_cursor = camry_host_addr(puVar3);
    *puVar3 = '\0';
    uVar2 = f33_dcm_receive_buffer_configuration[uVar4].capacity;
    f33_dcm_receive_buffer_state[uVar4].received_length = 0;
    f33_dcm_receive_buffer_state[uVar4].abort_pending = '\0';
    f33_dcm_receive_buffer_state[uVar4].inactivity_participant = '\0';
    f33_dcm_receive_buffer_state[uVar4].remaining_capacity = (ushort)uVar2;
    uVar4 = uVar1;
  } while (uVar1 < 3);
  return;
}



ushort FUN_00093b18(void)

{
  return f33_dcm_protocol_configuration
         [(short)f33_dcm_receive_route[(short)f33_dcm_current_dispatch_receive_slot].protocol_index]
         .inactivity_timeout_raw;
}



void FUN_00093b32(short param_1,ushort *param_2,ushort *param_3,ushort *param_4)

{
  *param_2 = f33_dcm_receive_route[param_1].protocol_index;
  *param_3 = f33_dcm_receive_route[param_1].connection_index;
  *param_4 = f33_dcm_receive_route[param_1].receive_descriptor_index;
  return;
}



/* Return configured protocol timeout or selected functional override, and publish zero-time
   flag59EC. Real R10 return is used by timer2 admission; not void. */

uint f33_dcm_get_overall_request_timeout(void)

{
  int *piVar1;
  int iVar2;
  int iVar3;
  uint32_t puVar4;
  uint32_t puVar5;
  uint uVar6;
  short sStack_a;
  ushort uStack_8;
  ushort uStack_6;
  
  puVar4 = 0xfebeb800u;
  puVar5 = 0x23dfcu;
  sStack_a = 0;
  uStack_8 = 0;
  uStack_6 = 0;
  FUN_00093b32(f33_dcm_pending_dispatch_receive_slot,&sStack_a,&uStack_8,&uStack_6);
  iVar3 = (uint)uStack_8 * 4;
  piVar1 = ((int *)camry_host_ptr((uint32_t)(puVar5 + sStack_a * 0x14 + 0x20c4)));
  iVar2 = (uint)uStack_6 * 0xc;
  if (((*((char *)camry_host_ptr((uint32_t)(*(int *)(*(int *)(*piVar1 + iVar3) + 4) + iVar2 + 9)))) == '\x01') &&
     ((*((char *)camry_host_ptr((uint32_t)(*(int *)(*(int *)(*piVar1 + iVar3) + 4) + iVar2 + 8)))) == '\x01')) {
    uVar6 = (*((uint *)camry_host_ptr((uint32_t)(*(int *)(*(int *)(*piVar1 + iVar3) + 4) + iVar2))));
  }
  else {
    uVar6 = piVar1[1];
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x5e14))))) = uVar6 == 0;
  return uVar6;
}



/* Fresh selection reads session raw timings and subtracts protocol margins with floor0; retains
   P2star at59D8 and pending spacing at59DA. Return initial raw P2 or retained P2star. */

ushort f33_dcm_select_response_deadline(uchar use_retained,uchar use_current_session)

{
  ushort uVar1;
  ushort uVar2;
  uint32_t puVar3;
  uint32_t puVar4;
  short sVar5;
  int iVar6;
  uchar uStack_b;
  ushort uStack_a;
  
  puVar3 = 0xfebeb800u;
  puVar4 = 0x23dfcu;
  uVar1 = f33_dcm_receive_route[(short)f33_dcm_pending_dispatch_receive_slot].protocol_index;
  uStack_b = '\x01';
  uStack_a = 0;
  uVar2 = f33_dcm_retained_p2_star_raw;
  if (use_retained != '\x01') {
    if (use_current_session == '\x01') {
      f33_dcm_get_session(&uStack_b);
    }
    FUN_00092064(uStack_b, &uStack_a, ((undefined *)camry_host_ptr((uint32_t)(puVar3 + -0x5e28))), ((undefined *)camry_host_ptr((uint32_t)(puVar3 + -0x5e26))));
    iVar6 = (short)uVar1 * 0x14;
    uVar2 = uStack_a;
    if ((*((ushort *)camry_host_ptr((uint32_t)(puVar4 + iVar6 + 0x20d0)))) <= uStack_a) {
      uVar2 = uStack_a - (*((short *)camry_host_ptr((uint32_t)(puVar4 + iVar6 + 0x20d0))));
    }
    sVar5 = 0;
    if ((*((ushort *)camry_host_ptr((uint32_t)(puVar4 + iVar6 + 0x20d2)))) <= (*((ushort *)camry_host_ptr((uint32_t)(puVar3 + -0x5e28))))) {
      sVar5 = (*((ushort *)camry_host_ptr((uint32_t)(puVar3 + -0x5e28)))) - (*((short *)camry_host_ptr((uint32_t)(puVar4 + iVar6 + 0x20d2))));
    }
    (*((short *)camry_host_ptr((uint32_t)(puVar3 + -0x5e28)))) = sVar5;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x5e15))))) = uVar2 == 0;
  }
  return uVar2;
}



ushort FUN_00093c5a(void)

{
  return f33_dcm_pending_spacing_raw;
}



ushort FUN_00093c60(void)

{
  return f33_dcm_current_dispatch_receive_slot;
}



void FUN_00093c66(ushort param_1)

{
  f33_dcm_current_dispatch_receive_slot = param_1;
  return;
}



void FUN_00093c6c(uint param_1,undefined4 *param_2)

{
  uchar *puVar1;
  
  param_1 = param_1 & 0xffff;
  puVar1 = ((void *)camry_host_ptr((uint32_t)(f33_dcm_receive_buffer_configuration[param_1].base)));
  f33_dcm_receive_buffer_state[param_1].write_cursor = camry_host_addr(puVar1);
  *param_2 = camry_host_addr(puVar1);
  *(ushort *)(param_2 + 1) = f33_dcm_receive_buffer_state[param_1].received_length;
  return;
}



uchar FUN_00093c8e(void)

{
  return f33_dcm_pending_transport_accepted;
}



void FUN_00093c94(uchar param_1)

{
  f33_dcm_pending_transport_accepted = param_1;
  return;
}



void FUN_00093c9a(uint param_1,char param_2)

{
  uchar *puVar1;
  uint uVar2;
  
  param_1 = param_1 & 0xffff;
  if (param_2 == '\0') {
    f33_dcm_shared_response_buffer[0] = '\0';
    f33_dcm_pending_transport_accepted = '\0';
  }
  puVar1 = ((void *)camry_host_ptr((uint32_t)(f33_dcm_receive_buffer_configuration[param_1].base)));
  f33_dcm_receive_buffer_state[param_1].receiving = '\0';
  f33_dcm_receive_buffer_state[param_1].write_cursor = camry_host_addr(puVar1);
  *puVar1 = '\0';
  uVar2 = f33_dcm_receive_buffer_configuration[param_1].capacity;
  f33_dcm_receive_buffer_state[param_1].received_length = 0;
  f33_dcm_receive_buffer_state[param_1].inactivity_participant = '\0';
  f33_dcm_receive_buffer_state[param_1].remaining_capacity = (ushort)uVar2;
  return;
}



void FUN_00093cce(short param_1,ushort *param_2,ushort *param_3)

{
  *param_2 = f33_dcm_receive_route[param_1].protocol_index;
  *param_3 = f33_dcm_receive_route[param_1].connection_index;
  return;
}



void FUN_00093ce6(undefined4 *param_1)

{
  uint32_t puVar1;
  uint32_t puVar2;
  short local_c;
  ushort uStack_a;
  
  puVar1 = 0xfebeb800u;
  puVar2 = 0x23dfcu;
  local_c = 0;
  uStack_a = 0;
  FUN_00093cce(f33_dcm_current_dispatch_receive_slot,&local_c,&uStack_a);
  *param_1 = puVar1 + -0x5de0;
  *(short *)(param_1 + 1) =
       (short)**(undefined4 **)
                ((*((int *)camry_host_ptr((uint32_t)((uint)uStack_a * 4 + *(int *)(puVar2 + local_c * 0x14 + 0x20c4))))) + 8);
  return;
}



undefined1 FUN_00093d2e(void)

{
  uint32_t puVar1;
  undefined1 uVar2;
  short sStack_e;
  ushort uStack_c;
  ushort uStack_a;
  
  puVar1 = 0x23dfcu;
  sStack_e = 0;
  uVar2 = 0;
  uStack_c = 0;
  uStack_a = 0;
  FUN_00093b32(f33_dcm_current_dispatch_receive_slot,&sStack_e,&uStack_c,&uStack_a);
  if ((*((char *)camry_host_ptr((uint32_t)(*(int *)(*(int *)(*(int *)(puVar1 + sStack_e * 0x14 + 0x20c4) + (uint)uStack_c * 4)
                        + 4) + (uint)uStack_a * 0xc + 9)))) == '\x01') {
    if ((*((char *)camry_host_ptr((uint32_t)(*(int *)(*(int *)(*(int *)(puVar1 + sStack_e * 0x14 + 0x20c4) + (uint)uStack_c * 4
                                   ) + 4) + (uint)uStack_a * 0xc + 8)))) == '\x01') {
      uVar2 = 1;
    }
    else {
      uVar2 = 0;
    }
  }
  return uVar2;
}



undefined1 FUN_00093d9a(void)

{
  uint32_t puVar1;
  short sStack_a;
  ushort uStack_8;
  ushort uStack_6;
  
  puVar1 = 0x23dfcu;
  sStack_a = 0;
  uStack_8 = 0;
  uStack_6 = 0;
  FUN_00093b32(f33_dcm_current_dispatch_receive_slot,&sStack_a,&uStack_8,&uStack_6);
  return (*((undefined1 *)camry_host_ptr((uint32_t)((uint)uStack_6 * 0xc +
           *(int *)(*(int *)((uint)uStack_8 * 4 + *(int *)(puVar1 + sStack_a * 0x14 + 0x20c4)) + 4)
          + 9))));
}



/* Copy exactly16-bit chunk length into slot cursor, add received and subtract remaining16-bit
   lengths. Caller92152 owns capacity check. */

uint f33_dcm_append_receive_chunk(ushort receive_slot,F33PduInfo *chunk,ushort *available)

{
  F33DcmReceiveBufferState *pFVar1;
  uchar uVar2;
  ushort uVar3;
  uchar *puVar4;
  
  puVar4 = ((void *)camry_host_ptr((uint32_t)(chunk->data)));
  uVar3 = 0;
  while( true ) {
    pFVar1 = f33_dcm_receive_buffer_state + receive_slot;
    if (chunk->length <= uVar3) break;
    uVar3 = uVar3 + 1;
    uVar2 = *puVar4;
    puVar4 = puVar4 + 1;
    *((uint8_t *)camry_host_ptr((uint32_t)(pFVar1->write_cursor))) = uVar2;
    pFVar1->write_cursor = pFVar1->write_cursor + 1;
  }
  f33_dcm_receive_buffer_state[receive_slot].received_length =
       f33_dcm_receive_buffer_state[receive_slot].received_length + chunk->length;
  uVar3 = f33_dcm_receive_buffer_state[receive_slot].remaining_capacity - chunk->length;
  f33_dcm_receive_buffer_state[receive_slot].remaining_capacity = uVar3;
  *available = uVar3;
  return 0;
}



uchar FUN_00093e32(uint param_1)

{
  return f33_dcm_receive_buffer_state[param_1 & 0xffff].receiving;
}



/* Count three59F0-stride10 slot receive-active bytes equal1. Real R10 result is consumed by release
   and inactivity decisions; not void. */

ushort f33_dcm_count_receiving_slots(void)

{
  uint uVar1;
  ushort uVar2;
  
  uVar2 = 0;
  uVar1 = 0;
  do {
    if (f33_dcm_receive_buffer_state[uVar1].receiving == '\x01') {
      uVar2 = uVar2 + 1;
    }
    uVar1 = uVar1 + 1;
  } while (uVar1 < 3);
  return uVar2;
}



void FUN_00093e5c(uint param_1,uchar param_2)

{
  param_1 = param_1 & 0xffff;
  if (param_2 == '\x01') {
    f33_dcm_receive_buffer_state[param_1].write_cursor =
         f33_dcm_receive_buffer_configuration[param_1].base;
  }
  f33_dcm_receive_buffer_state[param_1].receiving = param_2;
  return;
}



undefined2 FUN_00093e82(void)

{
  uint32_t puVar1;
  short local_8;
  ushort uStack_6;
  
  puVar1 = 0x23dfcu;
  local_8 = 0;
  uStack_6 = 0;
  FUN_00093cce(f33_dcm_current_dispatch_receive_slot,&local_8,&uStack_6);
  return (*((undefined2 *)camry_host_ptr((uint32_t)(*(int *)(*(int *)((uint)uStack_6 * 4 + *(int *)(puVar1 + local_8 * 0x14 + 0x20c4)) + 8) +
          6))));
}



undefined2 FUN_00093ebc(void)

{
  uint32_t puVar1;
  short local_8;
  ushort uStack_6;
  
  puVar1 = 0x23dfcu;
  local_8 = 0;
  uStack_6 = 0;
  FUN_00093cce(f33_dcm_current_dispatch_receive_slot,&local_8,&uStack_6);
  return (*((undefined2 *)camry_host_ptr((uint32_t)(*(int *)(*(int *)((uint)uStack_6 * 4 + *(int *)(puVar1 + local_8 * 0x14 + 0x20c4)) + 8) +
          4))));
}



void FUN_00093ef6(uint param_1,uchar param_2)

{
  f33_dcm_receive_buffer_state[param_1 & 0xffff].abort_pending = param_2;
  return;
}



uchar FUN_00093f02(uint param_1)

{
  return f33_dcm_receive_buffer_state[param_1 & 0xffff].abort_pending;
}



uint FUN_00093f0e(ushort param_1)

{
  uint uVar1;
  
  uVar1 = 0;
  do {
    if (param_1 == f33_dcm_receive_route[(short)uVar1].receive_id) {
      return uVar1;
    }
    uVar1 = uVar1 + 1;
  } while (uVar1 < 3);
  return 0xffff;
}



uchar FUN_00093f30(short param_1)

{
  if (f33_dcm_receive_route[param_1].paired_receive_slot_or_ffff != 0xffff) {
    return f33_dcm_receive_buffer_state[f33_dcm_receive_route[param_1].paired_receive_slot_or_ffff].
           receiving;
  }
  return '\0';
}



void FUN_00093f4e(uint param_1,uchar param_2)

{
  f33_dcm_receive_buffer_state[param_1 & 0xffff].inactivity_participant = param_2;
  return;
}



uchar FUN_00093f5a(uint param_1)

{
  return f33_dcm_receive_buffer_state[param_1 & 0xffff].inactivity_participant;
}



void FUN_00093f66(int param_1,ushort *param_2,char param_3)

{
  undefined *puVar1;
  undefined *puVar2;
  uint32_t puVar3;
  uint uVar4;
  short sStack_1e;
  ushort uStack_1c;
  ushort uStack_1a;
  
  puVar3 = 0x23dfcu;
  sStack_1e = 0;
  uStack_1c = 0;
  uVar4 = 0;
  uStack_1a = 0;
  *param_2 = 0;
  puVar1 = ((undefined *)camry_host_ptr(0xfebeb800u));
  do {
    puVar2 = puVar1;
    if ((puVar1[uVar4 * 0x10 + -0x5e06] == '\x01') &&
       ((param_3 != '\x02' || (uVar4 != *(ushort *)(puVar1 + -0x5e1e))))) {
      FUN_00093b32(uVar4,&sStack_1e,&uStack_1c,&uStack_1a);
      (*((undefined2 *)camry_host_ptr((uint32_t)((uint)*param_2 * 4 + param_1)))) =
           (*((undefined2 *)camry_host_ptr((uint32_t)((uint)uStack_1a * 0xc +
             *(int *)(*(int *)((uint)uStack_1c * 4 + *(int *)(puVar3 + sStack_1e * 0x14 + 0x20c4)) +
                     4) + 6))));
      (*((short *)camry_host_ptr((uint32_t)((uint)*param_2 * 4 + param_1 + 2)))) = (short)uVar4;
      *param_2 = *param_2 + 1;
      puVar1[uVar4 * 0x10 + -0x5e05] = 1;
    }
    uVar4 = uVar4 + 1;
    puVar1 = puVar2;
  } while (uVar4 < 3);
  return;
}


