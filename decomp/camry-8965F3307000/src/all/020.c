#include "common.h"


undefined4 FUN_00080066(byte param_1,undefined2 param_2)

{
  if (param_1 < DAT_00021970) {
    FUN_0007ff98(param_1,param_2,1);
  }
  return 0;
}



void FUN_000802ee(void)

{
  char cVar1;
  ushort uVar2;
  byte bVar3;
  short sVar4;
  uint32_t puVar5;
  uint32_t puVar6;
  undefined4 uVar7;
  uint uVar8;
  ushort uVar9;
  uint uVar10;
  
  puVar5 = 0xfebeb800u;
  puVar6 = 0x23dfcu;
  uVar8 = (uint)DAT_00021970;
  for (uVar10 = 0; uVar10 < uVar8; uVar10 = uVar10 + 1 & 0xff) {
    bVar3 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(uVar10 - 0x248a)))));
    if (bVar3 != 0) {
      sVar4 = (*((short *)camry_host_ptr((uint32_t)(puVar5 + uVar10 * 2 + -0x6f28))));
      if ((sVar4 == 0x57a8) || (sVar4 == 0x6b94)) {
        for (uVar9 = 0; uVar9 < bVar3; uVar9 = uVar9 + 1 & 0xff) {
          uVar2 = (*((ushort *)camry_host_ptr((uint32_t)((short)uVar9 * 10 + *(int *)(puVar6 + uVar10 * 4 + -0x2518) + 8))));
          uVar7 = FUN_0007a2da();
          cVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(uVar2 - 0x6ef7)))));
          if (cVar1 != '\0') {
            (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(uVar2 - 0x6ef7))))) = cVar1 + -1;
          }
          ((void)(uVar7), thunk_FUN_0006a4c4());
        }
      }
      if ((sVar4 == 0x57a8) && ((*((short *)camry_host_ptr((uint32_t)(puVar5 + uVar10 * 2 + -0x6f02)))) == 0x5555)) {
        f33_service_can_tx_queues((uchar)uVar10);
      }
    }
  }
  return;
}



bool FUN_0008037a(uint param_1,byte param_2)

{
  bool bVar1;
  
  param_1 = param_1 & 0xff;
  bVar1 = true;
  if (param_1 < DAT_00021970) {
    if ((param_2 < (byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x21972u + (uint32_t)(param_1) * 1u))))) &&
       (f33_logical_controller_request_cache[param_1] == 0x57a8)) {
      bVar1 = *(short *)(((undefined *)camry_host_ptr(0xfebe48feu)) + param_1 * 2) != 0x5555;
    }
  }
  return bVar1;
}



void FUN_000805c6(void)

{
  ushort *puVar1;
  undefined2 *puVar2;
  ushort uVar3;
  uint32_t puVar4;
  uint32_t puVar5;
  ushort uVar6;
  uint uVar7;
  int iVar8;
  uint uVar9;
  uint uVar10;
  uint uVar11;
  uint uVar12;
  uint uVar13;
  
  puVar4 = 0xfebeb800u;
  puVar5 = 0x23dfcu;
  uVar10 = (uint)DAT_00021970;
  for (uVar13 = 0; uVar13 < uVar10; uVar13 = uVar13 + 1 & 0xff) {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(uVar13 - 0x6ef2))))) = 0;
    uVar6 = (ushort)(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(uVar13 - 0x248a)))));
    if (uVar6 == 0) {
      uVar6 = 1;
      uVar11 = 1;
    }
    else {
      uVar11 = (uint)(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(uVar13 - 0x2489)))));
    }
    for (uVar3 = 0; uVar3 < uVar6; uVar3 = uVar3 + 1 & 0xff) {
      puVar1 = ((ushort *)camry_host_ptr((uint32_t)((short)uVar3 * 10 + *(int *)(puVar5 + uVar13 * 4 + -0x2518))));
      uVar7 = (uint)puVar1[4];
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(uVar7 - 0x6ef7))))) = 0;
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(uVar7 - 0x6efc))))) = 0x69;
      puVar2 = ((undefined2 *)camry_host_ptr((uint32_t)(puVar4 + uVar7 * 6 + -0x6f26)));
      *puVar2 = 0;
      puVar2[1] = 0;
      puVar2[2] = 0;
      uVar12 = (uint)*puVar1;
      uVar9 = 0;
      if (uVar12 == 0) {
        uVar12 = 1;
      }
      iVar8 = (*((int *)camry_host_ptr((uint32_t)(puVar5 + uVar7 * 4 + -0x23a8))));
      for (; uVar9 < uVar12; uVar9 = uVar9 + 1 & 0xffff) {
        (*((undefined4 *)camry_host_ptr((uint32_t)(uVar9 * 4 + iVar8)))) = 0;
      }
    }
    for (uVar12 = 0; uVar12 < uVar11; uVar12 = uVar12 + 1 & 0xff) {
      (*((undefined1 *)camry_host_ptr((uint32_t)(*(int *)(puVar5 + uVar13 * 4 + -0x2514) + uVar12)))) = 0x69;
      FUN_0007f5da(uVar13,uVar12);
    }
  }
  uVar10 = 0;
  do {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(uVar10 - 0x684e))))) = 0;
    uVar10 = uVar10 + 1;
  } while (uVar10 < 0x40);
  (*((undefined4 *)camry_host_ptr((uint32_t)(puVar4 + -0x6808)))) = 0;
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar4 + -0x6804)))) = 0;
  return;
}



void FUN_000806a4(uint param_1)

{
  undefined2 *puVar1;
  byte bVar2;
  uint32_t puVar3;
  uint32_t puVar4;
  undefined4 uVar5;
  ushort uVar6;
  uint uVar7;
  
  puVar3 = 0xfebeb800u;
  puVar4 = 0x23dfcu;
  param_1 = param_1 & 0xff;
  bVar2 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x21972u + (uint32_t)(param_1) * 1u))));
  if (bVar2 != 0) {
    for (uVar6 = 0; uVar6 < bVar2; uVar6 = uVar6 + 1 & 0xff) {
      uVar7 = (uint)(*((ushort *)camry_host_ptr((uint32_t)((short)uVar6 * 10 + *(int *)(puVar4 + param_1 * 4 + -0x2518) + 8))));
      uVar5 = FUN_0007a2da();
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(uVar7 - 0x6ef7))))) = 0;
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(uVar7 - 0x6efc))))) = 0x69;
      puVar1 = ((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + uVar7 * 6 + -0x6f26)));
      *puVar1 = 0;
      puVar1[1] = 0;
      puVar1[2] = 0;
      ((void)(uVar5), thunk_FUN_0006a4c4());
    }
    bVar2 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(param_1 - 0x2489)))));
    for (uVar7 = 0; uVar7 < bVar2; uVar7 = uVar7 + 1 & 0xff) {
      uVar5 = FUN_0007a2da();
      (*((undefined1 *)camry_host_ptr((uint32_t)(*(int *)(puVar4 + param_1 * 4 + -0x2514) + uVar7)))) = 0x69;
      FUN_0007f5da(param_1,uVar7);
      ((void)(uVar5), thunk_FUN_0006a4c4());
    }
  }
  return;
}



void FUN_00080740(uint param_1)

{
  undefined2 *puVar1;
  byte bVar2;
  uint32_t puVar3;
  uint32_t puVar4;
  undefined4 uVar5;
  ushort uVar6;
  uint uVar7;
  
  puVar3 = 0xfebeb800u;
  puVar4 = 0x23dfcu;
  param_1 = param_1 & 0xff;
  bVar2 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x21972u + (uint32_t)(param_1) * 1u))));
  if (bVar2 != 0) {
    for (uVar6 = 0; uVar6 < bVar2; uVar6 = uVar6 + 1 & 0xff) {
      uVar7 = (uint)(*((ushort *)camry_host_ptr((uint32_t)((short)uVar6 * 10 + *(int *)(puVar4 + param_1 * 4 + -0x2518) + 8))));
      uVar5 = FUN_0007a2da();
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(uVar7 - 0x6efc))))) = 0x69;
      puVar1 = ((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + uVar7 * 6 + -0x6f26)));
      *puVar1 = 0;
      puVar1[1] = 0;
      puVar1[2] = 0;
      ((void)(uVar5), thunk_FUN_0006a4c4());
    }
    bVar2 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(param_1 - 0x2489)))));
    for (uVar7 = 0; uVar7 < bVar2; uVar7 = uVar7 + 1 & 0xff) {
      uVar5 = FUN_0007a2da();
      (*((undefined1 *)camry_host_ptr((uint32_t)(*(int *)(puVar4 + param_1 * 4 + -0x2514) + uVar7)))) = 0x69;
      FUN_0007f5da(param_1,uVar7);
      ((void)(uVar5), thunk_FUN_0006a4c4());
    }
  }
  return;
}



void FUN_000807d8(uint param_1)

{
  int iVar1;
  undefined2 *puVar2;
  byte bVar3;
  uint32_t puVar4;
  uint32_t puVar5;
  undefined4 uVar6;
  ushort uVar7;
  uint uVar8;
  
  puVar4 = 0xfebeb800u;
  puVar5 = 0x23dfcu;
  param_1 = param_1 & 0xff;
  bVar3 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x21972u + (uint32_t)(param_1) * 1u))));
  if (bVar3 != 0) {
    for (uVar7 = 0; uVar7 < bVar3; uVar7 = uVar7 + 1 & 0xff) {
      iVar1 = (short)uVar7 * 10 + (*((int *)camry_host_ptr((uint32_t)(puVar5 + param_1 * 4 + -0x2518))));
      uVar8 = (uint)(*((ushort *)camry_host_ptr((uint32_t)(iVar1 + 8))));
      uVar6 = FUN_0007a2da();
      if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(uVar8 - 0x6efc))))) != 'i') {
        (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(uVar8 - 0x6ef7))))) = (*((undefined1 *)camry_host_ptr((uint32_t)(iVar1 + 2))));
      }
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(uVar8 - 0x6efc))))) = 'i';
      puVar2 = ((undefined2 *)camry_host_ptr((uint32_t)(puVar4 + uVar8 * 6 + -0x6f26)));
      *puVar2 = 0;
      puVar2[1] = 0;
      puVar2[2] = 0;
      ((void)(uVar6), thunk_FUN_0006a4c4());
    }
    bVar3 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(param_1 - 0x2489)))));
    for (uVar8 = 0; uVar8 < bVar3; uVar8 = uVar8 + 1 & 0xff) {
      uVar6 = FUN_0007a2da();
      (*((undefined1 *)camry_host_ptr((uint32_t)(*(int *)(puVar5 + param_1 * 4 + -0x2514) + uVar8)))) = 0x69;
      FUN_0007f5da(param_1,uVar8);
      ((void)(uVar6), thunk_FUN_0006a4c4());
    }
  }
  return;
}



void FUN_000809fe(void)

{
  int iVar1;
  uint32_t puVar2;
  uint32_t puVar3;
  uint uVar4;
  uint uVar5;
  
  puVar2 = 0xfebeb800u;
  puVar3 = 0x23dfcu;
  uVar4 = (uint)DAT_00021970;
  for (uVar5 = 0; uVar5 < uVar4; uVar5 = uVar5 + 1 & 0xff) {
    iVar1 = uVar5 * 2;
    if ((*((short *)camry_host_ptr((uint32_t)(puVar3 + iVar1 + -0x2496)))) != 0) {
      if ((((*((short *)camry_host_ptr((uint32_t)(puVar2 + iVar1 + -0x6f28)))) == 0x57a8) ||
          ((*((short *)camry_host_ptr((uint32_t)(puVar2 + iVar1 + -0x6f28)))) == 0x6b94)) &&
         (((*((ushort *)camry_host_ptr((uint32_t)(puVar2 + iVar1 + -0x6f02)))) & 3) == 1)) {
        FUN_000808d6(uVar5);
      }
    }
  }
  return;
}



void FUN_00080a4a(uint param_1,uint *param_2)

{
  undefined4 *puVar1;
  uint *puVar2;
  undefined1 *puVar3;
  undefined1 *puVar4;
  int iVar5;
  undefined1 uVar6;
  undefined1 uVar7;
  undefined1 uVar8;
  byte bVar9;
  uint uVar10;
  uint uVar11;
  uint uVar12;
  uint32_t puVar13;
  undefined4 uVar14;
  int iVar15;
  uint uVar16;
  uint uVar17;
  uint uVar18;
  uint uVar19;
  uint uVar20;
  uint uVar21;
  
  puVar13 = 0x23dfcu;
  param_1 = param_1 & 0xff;
  uVar18 = *param_2;
  uVar19 = (uint)(*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_2) + 7))));
  uVar10 = 8;
  if ((uVar18 >> 0x1e & 1) != 0) {
    uVar10 = 0x40;
  }
  iVar5 = (int)(short)param_1;
  if (uVar19 <= uVar10) {
    uVar10 = uVar19;
  }
  uVar20 = (uint)*(ushort *)(((undefined *)camry_host_ptr(0x21966u)) + param_1 * 2);
  uVar14 = FUN_0007a2da();
  uVar11 = (uint)(ushort)(*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe48f8u + (uint32_t)(iVar5 * 3) * 2u))));
  uVar17 = (uint)(ushort)(*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe48fcu + (uint32_t)(iVar5 * 3) * 2u))));
  if (((int)((uVar11 + 2) - uVar20) < 0 || uVar11 + 2 == uVar20) && (uVar17 <= uVar20)) {
    iVar15 = 5;
    if (8 < uVar19) {
      iVar15 = ((int)(uVar19 + 7) >> 3) * 2 + 3;
    }
    uVar16 = uVar20 - uVar11 & 0xffff;
    uVar12 = uVar11;
    uVar21 = uVar20;
    if (-1 < (int)((iVar15 + 2U) - uVar16) && iVar15 + 2U != uVar16) {
      uVar17 = uVar17 + uVar16;
      uVar12 = 0;
      uVar21 = uVar11;
    }
    if ((iVar15 + uVar17 & 0xffff) <= uVar20) {
      if (uVar21 < uVar20) {
        puVar1 = ((undefined4 *)camry_host_ptr((uint32_t)(uVar21 * 4 + *(int *)(puVar13 + param_1 * 4 + -0x24f8))));
        *puVar1 = 0xffffffff;
        puVar1[1] = 0;
      }
      (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe48f8u + (uint32_t)(iVar5 * 3) * 2u)))) = (short)iVar15 + (short)uVar12;
      (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe48fcu + (uint32_t)(iVar5 * 3) * 2u)))) = (short)(iVar15 + uVar17);
      uVar17 = param_2[1];
      puVar2 = ((uint *)camry_host_ptr((uint32_t)(uVar12 * 4 + *(int *)(puVar13 + param_1 * 4 + -0x24f8))));
      bVar9 = (*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_2) + 6))));
      puVar2[2] = uVar18;
      uVar18 = param_2[2];
      uVar19 = uVar19 + (uint)bVar9 * 0x100 + (uint)(ushort)uVar17 * 0x10000;
      *puVar2 = uVar19;
      puVar2[1] = ~uVar19;
      for (uVar19 = 0; uVar19 < uVar10; uVar19 = uVar19 + 4 & 0xff) {
        puVar3 = ((undefined1 *)camry_host_ptr((uint32_t)(uVar19 + uVar18)));
        uVar6 = puVar3[1];
        uVar7 = puVar3[2];
        uVar8 = puVar3[3];
        puVar4 = ((undefined1 *)camry_host_ptr((uint32_t)((int)camry_host_addr(puVar2) + uVar19 + 0xc)));
        *puVar4 = *puVar3;
        puVar4[1] = uVar6;
        puVar4[2] = uVar7;
        puVar4[3] = uVar8;
      }
    }
  }
  ((void)(uVar14), thunk_FUN_0006a4c4());
  return;
}



void FUN_00080c20(uint param_1)

{
  undefined2 *puVar1;
  uint32_t puVar2;
  undefined4 uVar3;
  
  puVar2 = 0xfebeb800u;
  if (*(short *)(((undefined *)camry_host_ptr(0x21966u)) + (param_1 & 0xff) * 2) != 0) {
    uVar3 = FUN_0007a2da();
    puVar1 = ((undefined2 *)camry_host_ptr((uint32_t)(puVar2 + (short)(param_1 & 0xff) * 6 + -0x6f08)));
    *puVar1 = 0;
    puVar1[1] = 0;
    puVar1[2] = 0;
    ((void)(uVar3), thunk_FUN_0006a4c4());
  }
  return;
}



/* Mapdriver1\u2192logical0using21978;publish48FEbits7:6=10bunderlockonlyforinitializedlogicalstate.
   NotSID28.
   Mapdriver1→logical0using21978;publish48FEbits7:6=10bunderlockonlyforinitializedlogicalstate. */

void f33_publish_mapped_controller_bus_off_event(uchar driver_index)

{
  uint32_t puVar1;
  undefined4 uVar2;
  uint uVar3;
  
  puVar1 = 0xfebeb800u;
  if ((uint)driver_index < (uint)DAT_00021971) {
    uVar3 = (uint)f33_driver_to_logical_controller_map[driver_index];
    if (uVar3 != 0xff) {
      if ((f33_logical_controller_request_cache[uVar3] == 0x57a8) ||
         (f33_logical_controller_request_cache[uVar3] == 0x6b94)) {
        uVar2 = FUN_0007a2da();
        (*((ushort *)camry_host_ptr((uint32_t)(puVar1 + uVar3 * 2 + -0x6f02)))) =
             (*((ushort *)camry_host_ptr((uint32_t)(puVar1 + uVar3 * 2 + -0x6f02)))) & 0xff3f | 0x80;
        ((void)(uVar2), thunk_FUN_0006a4c4());
        ((void)(uVar3), f33_return_only_stub_832ee());
      }
    }
  }
  return;
}



void FUN_00080d2a(uint param_1)

{
  uint32_t puVar1;
  undefined4 uVar2;
  
  puVar1 = 0xfebeb800u;
  uVar2 = FUN_0007a2da();
  (*((ushort *)camry_host_ptr((uint32_t)(puVar1 + (param_1 & 0xff) * 2 + -0x6f02)))) =
       (*((ushort *)camry_host_ptr((uint32_t)(puVar1 + (param_1 & 0xff) * 2 + -0x6f02)))) & 0xfffc | 2;
  ((void)(uVar2), thunk_FUN_0006a4c4());
  return;
}



uint FUN_00080d76(uint param_1)

{
  uint uVar1;
  
  uVar1 = (uint)((param_1 & 0xc0) != 0x40);
  if ((param_1 & 0x30) != 0x10) {
    uVar1 = uVar1 | 0x80;
  }
  if ((param_1 & 0xc) != 4) {
    uVar1 = uVar1 | 2;
  }
  if ((param_1 & 3) != 1) {
    uVar1 = uVar1 | 0x20;
  }
  if ((param_1 & 0x300) != 0x100) {
    uVar1 = uVar1 | 0x100;
  }
  if (uVar1 == 0) {
    uVar1 = 0x20;
  }
  return uVar1;
}



uint FUN_00080dc0(uint param_1)

{
  char cVar1;
  char cVar2;
  char cVar3;
  short sVar4;
  uint32_t puVar5;
  undefined4 uVar6;
  uint uVar7;
  
  puVar5 = 0xfebeb800u;
  param_1 = param_1 & 0xff;
  uVar6 = FUN_0007a2da();
  cVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(param_1 - 0x6ef0)))));
  cVar2 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(param_1 - 0x6eef)))));
  sVar4 = (*((short *)camry_host_ptr((uint32_t)(puVar5 + param_1 * 2 + -0x6f02))));
  cVar3 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(param_1 - 0x6eee)))));
  ((void)(uVar6), thunk_FUN_0006a4c4());
  uVar7 = 0;
  if (sVar4 != 0x5555) {
    uVar7 = FUN_00080d76(sVar4);
  }
  if (cVar1 != 'U') {
    uVar7 = uVar7 | 4;
  }
  if (cVar2 != 'U') {
    uVar7 = uVar7 | 0x200;
  }
  if (cVar3 == -0x5b) {
    uVar7 = uVar7 | 0x10;
  }
  else if (cVar3 == 'Z') {
    uVar7 = uVar7 | 0x40;
  }
  else if (cVar3 != 'K') {
    uVar7 = uVar7 | 8;
  }
  return uVar7;
}



void FUN_00080e32(uint param_1,char param_2)

{
  uint32_t puVar1;
  undefined4 uVar2;
  ushort uVar3;
  undefined1 uVar4;
  undefined *puVar5;
  
  puVar1 = 0xfebeb800u;
  param_1 = param_1 & 0xff;
  uVar2 = FUN_0007a2da();
  uVar4 = 0x55;
  if (param_2 == '\0') {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(param_1 - 0x6ef0))))) = 0x55;
    puVar5 = ((undefined *)camry_host_ptr((uint32_t)(puVar1 + -0x6eee)));
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(param_1 - 0x6eef))))) = 0x55;
    uVar3 = 0x5555;
    uVar4 = 0x4b;
  }
  else {
    puVar5 = ((undefined *)camry_host_ptr((uint32_t)(puVar1 + -0x6eef)));
    if (param_2 == '\x02') {
      uVar3 = 0x5555;
    }
    else {
      uVar3 = (*((ushort *)camry_host_ptr((uint32_t)(puVar1 + param_1 * 2 + -0x6f02)))) & 3 | 0x5554;
    }
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(param_1 - 0x6ef0))))) = 0x55;
  }
  (*((ushort *)camry_host_ptr((uint32_t)(puVar1 + param_1 * 2 + -0x6f02)))) = uVar3;
  puVar5[param_1] = uVar4;
  ((void)(uVar2), thunk_FUN_0006a4c4());
  return;
}



undefined4 FUN_00080f16(ushort *param_1,ushort param_2)

{
  ushort uVar1;
  ushort uVar2;
  ushort uVar3;
  ushort uVar4;
  undefined4 uVar5;
  undefined4 uVar6;
  
  uVar6 = 0;
  uVar5 = FUN_0007a2da();
  uVar2 = *param_1;
  uVar3 = param_1[1];
  uVar4 = param_1[2];
  ((void)(uVar5), thunk_FUN_0006a4c4());
  uVar1 = uVar4 + (uVar3 - uVar2);
  if ((((param_2 <= uVar2) || (param_2 <= uVar3)) || (param_2 < uVar4)) ||
     ((uVar1 != 0 && (uVar1 != param_2)))) {
    uVar6 = 1;
  }
  return uVar6;
}



void FUN_00080f5a(uint param_1,undefined1 param_2)

{
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe4912u + (uint32_t)(param_1 & 0xff) * 1u)))) = param_2;
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_80f64(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_80f66(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_80f68(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_80f6a(void)

{
  return;
}



undefined4 FUN_00080f6c(uint param_1,byte param_2)

{
  undefined1 uVar1;
  undefined4 uVar2;
  
  uVar2 = 1;
  if (((param_1 & 0xff) < (uint)DAT_00021970) &&
     ((uVar1 = 0x5a, param_2 == 3 || (uVar1 = 0x69, param_2 < 2)))) {
    uVar2 = 0;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe4903u + (uint32_t)(param_1 & 0xff) * 1u)))) = uVar1;
  }
  return uVar2;
}



void FUN_00081290(char param_1)

{
  undefined8 uVar1;
  uint uVar2;
  uint uVar3;
  
  uVar1 = 0x23dfc00000000;
  uVar2 = (uint)DAT_00021971;
  for (uVar3 = 0; uVar3 < uVar2; uVar3 = uVar3 + 1 & 0xff) {
    if (param_1 == (*((char *)camry_host_ptr((uint32_t)(uVar3 + (int)((ulonglong)uVar1 >> 0x20) + -0x2484))))) {
      ((void)(uVar3), f33_return_only_stub_83590());
    }
  }
  return;
}



void FUN_000812be(char param_1)

{
  undefined8 uVar1;
  uint uVar2;
  uint uVar3;
  
  uVar1 = 0x23dfc00000000;
  uVar2 = (uint)DAT_00021971;
  for (uVar3 = 0; uVar3 < uVar2; uVar3 = uVar3 + 1 & 0xff) {
    if (param_1 == (*((char *)camry_host_ptr((uint32_t)(uVar3 + (int)((ulonglong)uVar1 >> 0x20) + -0x2484))))) {
      ((void)(uVar3), f33_return_only_stub_83596());
    }
  }
  return;
}



void FUN_000812ec(uint param_1)

{
  uint32_t puVar1;
  uint uVar2;
  uint uVar3;
  
  puVar1 = 0x23dfcu;
  if (((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe4912u + (uint32_t)(param_1 & 0xff) * 1u)))) == 'K') || (((int8_t)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe4912u + (uint32_t)(param_1 & 0xff) * 1u))))) == -0x5b)) {
    uVar2 = (uint)DAT_00021971;
    for (uVar3 = 0; uVar3 < uVar2; uVar3 = uVar3 + 1 & 0xff) {
      if ((param_1 & 0xff) == (uint)(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(uVar3 - 0x2484)))))) {
        ((void)(uVar3), f33_return_only_stub_83592());
      }
    }
  }
  return;
}



void FUN_0008132e(char param_1)

{
  undefined8 uVar1;
  uint uVar2;
  uint uVar3;
  
  uVar1 = 0x23dfc00000000;
  uVar2 = (uint)DAT_00021971;
  for (uVar3 = 0; uVar3 < uVar2; uVar3 = uVar3 + 1 & 0xff) {
    if (param_1 == (*((char *)camry_host_ptr((uint32_t)(uVar3 + (int)((ulonglong)uVar1 >> 0x20) + -0x2484))))) {
      ((void)(uVar3), f33_return_only_stub_83594());
    }
  }
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_8135c(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_8135e(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_81360(void)

{
  return;
}



undefined1 FUN_000813e4(uint param_1)

{
  undefined *puVar1;
  uint uVar2;
  undefined1 uVar3;
  int iVar4;
  
  puVar1 = ((undefined *)camry_host_ptr((uint32_t)(param_1 & 0xf800)));
  param_1 = param_1 & 0x7ff;
  uVar3 = 0xff;
  iVar4 = 0;
  if (((((puVar1 == (undefined *)0x0) || (iVar4 = 1, puVar1 == ((undefined *)camry_host_ptr((uint32_t)(0x6000))))) ||
       (iVar4 = 2, puVar1 == ((undefined *)camry_host_ptr((uint32_t)(0x800))))) ||
      ((iVar4 = 3, puVar1 == ((undefined *)camry_host_ptr(0xb800u)) || (iVar4 = 4, puVar1 == ((undefined *)camry_host_ptr((uint32_t)(0xc000))))))) ||
     (iVar4 = 5, puVar1 == ((undefined *)camry_host_ptr((uint32_t)(0xf800))))) {
    uVar2 = (uint)(ushort)(*((volatile uint16_t *)camry_host_ptr((uint32_t)(0x21a48u + (uint32_t)(iVar4) * 2u))));
    if ((uVar2 <= param_1) &&
       ((int)(param_1 - ((*((ushort *)camry_host_ptr((uint32_t)((int)(&PTR_PTR_00021a0c)[iVar4] + 0x10)))) + uVar2)) < 0)) {
      uVar3 = (*((undefined1 *)camry_host_ptr((uint32_t)((param_1 - uVar2 & 0xffff) * 8 + *(int *)(&PTR_PTR_00021a0c)[iVar4] + 5))));
    }
  }
  return uVar3;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_814aa(void)

{
  return;
}



/* Constant source: return 0; shape-classified from the canonical corpus. Callers receive this
   literal directly; its meaning is not recovered. */

undefined4 f33_return_const_0_814ae(void)

{
  return 0;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_8152e(void)

{
  return;
}



void FUN_00081530(uint param_1,char param_2)

{
  uint32_t puVar1;
  undefined4 uVar2;
  
  puVar1 = 0xfebeb800u;
  if (param_2 == '\x01') {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe4911u + (uint32_t)(param_1 & 0xff) * 1u)))) = 0xaa;
  }
  else {
    uVar2 = FUN_0007a2da();
    (*((ushort *)camry_host_ptr((uint32_t)(puVar1 + (param_1 & 0xff) * 2 + -0x6f02)))) =
         (*((ushort *)camry_host_ptr((uint32_t)(puVar1 + (param_1 & 0xff) * 2 + -0x6f02)))) & 0xfcff | 0x200;
    ((void)(uVar2), thunk_FUN_0006a4c4());
  }
  return;
}



void FUN_0008156c(uint param_1)

{
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe4911u + (uint32_t)(param_1 & 0xff) * 1u)))) = 0x55;
  return;
}



void FUN_0008157a(undefined1 param_1)

{
  FUN_0008367c(param_1);
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_81588(void)

{
  return;
}



/* Constant source: return 1; shape-classified from the canonical corpus. Callers receive this
   literal directly; its meaning is not recovered. */

undefined4 f33_return_const_1_8158a(void)

{
  return 1;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_8158e(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_81590(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_81592(void)

{
  return;
}



/* Constant source: return 1; shape-classified from the canonical corpus. Callers receive this
   literal directly; its meaning is not recovered. */

undefined4 f33_return_const_1_816b0(void)

{
  return 1;
}



/* Constant source: return 1; shape-classified from the canonical corpus. Callers receive this
   literal directly; its meaning is not recovered. */

undefined4 f33_return_const_1_816b4(void)

{
  return 1;
}



/* Constant source: return 1; shape-classified from the canonical corpus. Callers receive this
   literal directly; its meaning is not recovered. */

undefined4 f33_return_const_1_816b8(void)

{
  return 1;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_8176c(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_8176e(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_81d2e(void)

{
  return;
}



/* Constant source: return 0; shape-classified from the canonical corpus. Callers receive this
   literal directly; its meaning is not recovered. */

undefined4 f33_return_const_0_81f62(void)

{
  return 0;
}



undefined4 FUN_00081fa6(uint param_1,byte param_2,ushort param_3)

{
  int iVar1;
  undefined4 uVar2;
  
  param_1 = param_1 & 0xffff;
  uVar2 = 1;
  if ((((((int8_t)DAT_febe4f3d) == -0x56) && (iVar1 = camry_host_addr(FUN_0007a32e()), iVar1 != 0)) &&
      ((*((ushort *)camry_host_ptr((uint32_t)(iVar1 + 4)))) <= param_1)) &&
     ((((int)(param_1 - ((uint)(*((byte *)camry_host_ptr((uint32_t)(iVar1 + 0xd)))) + (uint)(*((ushort *)camry_host_ptr((uint32_t)(iVar1 + 4)))))) < 0 &&
       (param_2 < 2)) && (param_3 < 0x100)))) {
    uVar2 = FUN_00081f66(((F33CanTpConfiguration *)camry_host_ptr((uint32_t)(iVar1))), param_1, param_2, param_3);
  }
  return uVar2;
}



/* Constant source: return 0; shape-classified from the canonical corpus. Callers receive this
   literal directly; its meaning is not recovered. */

undefined4 f33_return_const_0_81ffa(void)

{
  return 0;
}



void FUN_000821a6(undefined1 param_1)

{
  DAT_febe5004 = param_1;
  DAT_febe5005 = 1;
  return;
}



undefined1 FUN_000821ca(void)

{
  return DAT_febe5005;
}



undefined1 FUN_000821d0(void)

{
  return DAT_febe5004;
}



void FUN_00082288(undefined4 param_1)

{
  DAT_febe5000 = param_1;
  return;
}



undefined4 FUN_0008228e(void)

{
  return DAT_febe5000;
}



void FUN_00082294(void)

{
  int iVar1;
  uint uVar2;
  uint uVar3;
  
  uVar3 = (uint)DAT_00022ae6;
  DAT_febe5006 = 0x69;
  DAT_febe500a = 0;
  for (uVar2 = 0; uVar2 < uVar3; uVar2 = uVar2 + 1 & 0xff) {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe4ebcu + (uint32_t)(uVar2) * 1u)))) = 0;
  }
  uVar3 = (uint)DAT_00022ae7;
  for (uVar2 = 0; uVar2 < uVar3; uVar2 = uVar2 + 1 & 0xff) {
    iVar1 = uVar2 * 8;
    *(undefined2 *)(((undefined *)camry_host_ptr(0xfebe4cdcu)) + iVar1) = 0;
    *(undefined2 *)(((undefined *)camry_host_ptr(0xfebe4cdeu)) + iVar1) = 0;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe4ce0u + (uint32_t)(iVar1) * 1u)))) = 0;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe4ce2u + (uint32_t)(iVar1) * 1u)))) = 0xff;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe4ce1u + (uint32_t)(iVar1) * 1u)))) = 0;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe4ce3u + (uint32_t)(iVar1) * 1u)))) = 0;
  }
  uVar3 = (uint)DAT_00022ae4;
  DAT_febe500b = 0;
  for (uVar2 = 0; uVar2 < uVar3; uVar2 = uVar2 + 1 & 0xffff) {
    *(undefined1 **)(((undefined *)camry_host_ptr(0xfebe4cfcu)) + uVar2 * 4) = ((undefined *)camry_host_ptr(0xfebe500bu));
  }
  for (uVar2 = 0; uVar2 < DAT_00022abf; uVar2 = uVar2 + 1 & 0xff) {
    *(undefined4 *)(((undefined *)camry_host_ptr(0xfebe4cd4u)) + uVar2 * 8) = 0;
    *(undefined4 *)(((undefined *)camry_host_ptr(0xfebe4cd8u)) + uVar2 * 8) = 0;
  }
  DAT_febe5007 = 0xff;
  DAT_febe5008 = 0xff;
  DAT_febe5009 = 0xff;
  return;
}



void FUN_00082330(void)

{
  byte bVar1;
  uint uVar2;
  uint32_t puVar3;
  uint32_t puVar4;
  undefined4 uVar5;
  
  puVar3 = 0xfebeb800u;
  puVar4 = 0x23dfcu;
  uVar5 = FUN_0007a2da();
  bVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x1315)))));
  for (uVar2 = 0; uVar2 < bVar1; uVar2 = uVar2 + 1 & 0xff) {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(uVar2 * 8 + -0x6b1f))))) = 0;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x67f6))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x67f6))))) & 0x7f;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x67fa))))) = 0x69;
  ((void)(uVar5), thunk_FUN_0006a4c4());
  return;
}



void FUN_000823e2(char param_1)

{
  undefined *puVar1;
  undefined *puVar2;
  uint32_t puVar3;
  uint uVar4;
  uint uVar5;
  
  puVar1 = ((undefined *)camry_host_ptr(0xfebeb800u));
  puVar3 = 0x23dfcu;
  if ((DAT_febe500a & 0x80) != 0) {
    uVar4 = (uint)DAT_00022ae7;
    for (uVar5 = 0; uVar5 < uVar4; uVar5 = uVar5 + 1 & 0xff) {
      if (((puVar1[uVar5 * 8 + -0x6b1f] & 1) != 0) && (puVar1[uVar5 * 8 + -0x6b20] == param_1)) {
        puVar2 = puVar1;
        if (*(short *)(puVar1 + uVar5 * 8 + -0x6b22) == 0) {
          *(undefined2 *)(puVar1 + uVar5 * 8 + -0x6b22) =
               *(undefined2 *)(puVar1 + uVar5 * 8 + -0x6b24);
          FUN_00082368((int)(short)(ushort)(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x1314))))) * (int)(short)uVar5 & 0xff,
                       puVar1[uVar5 * 8 + -0x6b1e]);
        }
        *(short *)(puVar1 + uVar5 * 8 + -0x6b22) = *(short *)(puVar1 + uVar5 * 8 + -0x6b22) + -1;
        puVar1 = puVar2;
      }
    }
  }
  return;
}



undefined4 FUN_00082494(void)

{
  uint uVar1;
  
  uVar1 = 0;
  while( true ) {
    if (DAT_00022ae7 <= uVar1) {
      return 0;
    }
    if (((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe4ce1u + (uint32_t)(uVar1 * 8) * 1u)))) & 1) != 0) break;
    uVar1 = uVar1 + 1 & 0xff;
  }
  return 1;
}



void FUN_0008268c(void)

{
  byte bVar1;
  uint uVar2;
  uint32_t puVar3;
  uint32_t puVar4;
  undefined4 uVar5;
  
  puVar3 = 0xfebeb800u;
  puVar4 = 0x23dfcu;
  uVar5 = FUN_0007a2da();
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x67f6))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x67f6))))) | 0x80;
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x67fa))))) != 'Z') {
    bVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x1316)))));
    for (uVar2 = 0; uVar2 < bVar1; uVar2 = uVar2 + 1 & 0xff) {
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(uVar2 - 0x6944))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)((short)uVar2 * 3 + -0x1368)))));
    }
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x67fa))))) = 0x5a;
  }
  ((void)(uVar5), thunk_FUN_0006a4c4());
  return;
}



undefined4 FUN_000826d6(int param_1,short *param_2)

{
  short sVar1;
  char cVar2;
  ushort uVar3;
  short sVar4;
  undefined1 uVar5;
  uint32_t puVar6;
  uint32_t puVar7;
  int iVar8;
  
  sVar4 = DAT_00022ad8;
  puVar6 = 0xfebeb800u;
  puVar7 = 0x23dfcu;
  sVar1 = *param_2;
  *param_2 = 2;
  if (sVar1 == sVar4) {
    uVar3 = (*((ushort *)camry_host_ptr((uint32_t)(param_1 + 2))));
    if ((uint)uVar3 < (uint)DAT_00022ae7) {
      iVar8 = (uVar3 & 0xff) * 8;
      cVar2 = (*((char *)camry_host_ptr((uint32_t)(param_1 + 1))));
      if (cVar2 == '\0') {
        (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe4ce1u + (uint32_t)(iVar8) * 1u)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe4ce1u + (uint32_t)(iVar8) * 1u)))) & 0xfe;
        iVar8 = FUN_00082494();
        if (iVar8 == 0) {
          (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(-0x67f6))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(-0x67f6))))) & 0x7f;
        }
LAB_0008271a:
        (*((char *)camry_host_ptr((uint32_t)(param_1 + 1)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar7 + (uint32_t)(-0x1314))))) * (char)uVar3;
        *param_2 = 2;
        return 0;
      }
      if (cVar2 == '\x01') {
        if ((*(short *)(((undefined *)camry_host_ptr(0xfebe4cdcu)) + iVar8) != 0) &&
           ((byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe4ce2u + (uint32_t)(iVar8) * 1u)))) < DAT_00022ae8)) {
          *(undefined2 *)(((undefined *)camry_host_ptr(0xfebe4cdeu)) + iVar8) = 0;
          (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe4ce1u + (uint32_t)(iVar8) * 1u)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe4ce1u + (uint32_t)(iVar8) * 1u)))) | 1;
          FUN_0008268c();
          goto LAB_0008271a;
        }
        uVar5 = 0x2a;
      }
      else {
        if (cVar2 == '\x02') {
          (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe4ce1u + (uint32_t)(iVar8) * 1u)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe4ce1u + (uint32_t)(iVar8) * 1u)))) | 4;
          goto LAB_0008271a;
        }
        uVar5 = 0x27;
      }
    }
    else {
      uVar5 = 0x22;
    }
  }
  else {
    uVar5 = 0x21;
  }
  (*((undefined1 *)camry_host_ptr((uint32_t)(param_1 + 1)))) = uVar5;
  return 1;
}



undefined4 FUN_0008277a(void)

{
  int iVar1;
  uint uVar2;
  undefined4 uVar3;
  
  uVar3 = 0;
  uVar2 = 0;
  while( true ) {
    if (DAT_00022ae7 <= uVar2) {
      return uVar3;
    }
    iVar1 = uVar2 * 8;
    if ((((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe4ce1u + (uint32_t)(iVar1) * 1u)))) & 4) != 0) &&
       ((uVar3 = 1, *(short *)(((undefined *)camry_host_ptr(0xfebe4cdcu)) + iVar1) == 0 ||
        (DAT_00022ae8 <= (byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe4ce2u + (uint32_t)(iVar1) * 1u)))))))) break;
    uVar2 = uVar2 + 1 & 0xff;
  }
  return 0;
}



uint FUN_00082a3c(uint param_1)

{
  param_1 = param_1 & 0xff;
  if (0x33 < param_1) {
    return (int)(param_1 + 1) >> 1 | 0x700;
  }
  return (short)param_1 * 5 | 0x600;
}



undefined4 FUN_00082a5c(int param_1,undefined2 *param_2)

{
  (*((undefined1 *)camry_host_ptr((uint32_t)(param_1 + 1)))) = 0x20;
  *param_2 = 2;
  return 1;
}



bool FUN_00082a6e(int param_1,short *param_2)

{
  short sVar1;
  short sVar2;
  
  sVar2 = DAT_00022ac6;
  sVar1 = *param_2;
  *param_2 = 2;
  if (sVar1 != sVar2) {
    (*((undefined1 *)camry_host_ptr((uint32_t)(param_1 + 1)))) = 0x21;
  }
  else {
    FUN_000821b2();
    *param_2 = 1;
  }
  return sVar1 != sVar2;
}



undefined4 FUN_00082aa2(int param_1,short *param_2)

{
  short sVar1;
  short sVar2;
  undefined1 uVar3;
  
  sVar2 = DAT_00022aca;
  sVar1 = *param_2;
  *param_2 = 2;
  if (sVar1 == sVar2) {
    FUN_00082ed6();
    uVar3 = 0;
  }
  else {
    uVar3 = 0x21;
  }
  (*((undefined1 *)camry_host_ptr((uint32_t)(param_1 + 1)))) = uVar3;
  return 1;
}



undefined4 FUN_00082bd2(char param_1,int param_2,short *param_3)

{
  short sVar1;
  short sVar2;
  uint32_t puVar3;
  uint32_t puVar4;
  byte bVar5;
  undefined4 uVar6;
  
  sVar2 = DAT_00022ac4;
  puVar3 = 0xfebeb800u;
  puVar4 = 0x23dfcu;
  sVar1 = *param_3;
  uVar6 = 1;
  *param_3 = 2;
  if ((sVar1 == sVar2) && ((*((char *)camry_host_ptr((uint32_t)(param_2 + 1)))) == '\0')) {
    bVar5 = f33_return_const_5_98eee();
    (*((byte *)camry_host_ptr((uint32_t)(param_2 + 1)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x130a))))) | bVar5;
    (*((undefined *)camry_host_ptr((uint32_t)(param_2 + 2)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x1309)))));
    (*((undefined *)camry_host_ptr((uint32_t)(param_2 + 3)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x133c)))));
    (*((ushort *)camry_host_ptr((uint32_t)(param_2 + 4)))) = (ushort)(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x133b)))));
    (*((undefined1 *)camry_host_ptr((uint32_t)(param_2 + 6)))) = 1;
    (*((undefined1 *)camry_host_ptr((uint32_t)(param_2 + 7)))) = 1;
    if (((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x67fc))))) != param_1) && ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x67fb))))) == '\x01')) {
      FUN_000821b2();
    }
    FUN_000821a6(param_1);
    uVar6 = 0;
    *param_3 = 8;
  }
  else {
    (*((undefined1 *)camry_host_ptr((uint32_t)(param_2 + 1)))) = 0x21;
    if ((DAT_febe5004 != param_1) || (DAT_febe5005 != '\x01')) {
      uVar6 = 0xff;
    }
  }
  return uVar6;
}



undefined4 FUN_00082c62(int param_1,short *param_2)

{
  short sVar1;
  short sVar2;
  undefined4 uVar3;
  
  sVar2 = DAT_00022acc;
  sVar1 = *param_2;
  *param_2 = 2;
  uVar3 = 1;
  if ((sVar1 == sVar2) && ((*((char *)camry_host_ptr((uint32_t)(param_1 + 3)))) == '\0')) {
    FUN_00082288((*((undefined4 *)camry_host_ptr((uint32_t)(param_1 + 4)))));
    uVar3 = 0;
    *param_2 = 1;
  }
  else {
    (*((undefined1 *)camry_host_ptr((uint32_t)(param_1 + 1)))) = 0x21;
  }
  return uVar3;
}



void FUN_00082e54(char param_1)

{
  uint uVar1;
  
  for (uVar1 = 0; (uVar1 < DAT_00022abc && ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x22a8eu + (uint32_t)(uVar1) * 1u)))) != param_1));
      uVar1 = uVar1 + 1 & 0xff) {
  }
  return;
}



void FUN_00082ed6(void)

{
  uint32_t puVar1;
  undefined4 uVar2;
  
  puVar1 = 0xfebeb800u;
  uVar2 = FUN_0007a2da();
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x67f4))))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x67f3))))) = 0;
  ((void)(uVar2), thunk_FUN_0006a4c4());
  return;
}



void FUN_00082f44(undefined1 param_1,int param_2,undefined2 param_3)

{
  undefined4 *puVar1;
  int iVar2;
  uint uVar3;
  ushort uVar4;
  uint uVar5;
  uint uVar6;
  uint uVar7;
  uint uVar8;
  
  uVar6 = (uint)DAT_00022abe;
  uVar3 = (uint)DAT_febe500c;
  uVar8 = (uint)DAT_febe500d;
  if ((uVar3 < uVar6) && (uVar8 < uVar6)) {
    uVar5 = (uint)DAT_00022abf;
    uVar4 = (ushort)DAT_00022abf;
    for (uVar7 = 0; uVar7 < uVar5; uVar7 = uVar7 + 1 & 0xff) {
      puVar1 = ((undefined4 *)camry_host_ptr((uint32_t)(uVar7 * 8 + param_2)));
      iVar2 = (uVar7 + (int)(short)uVar4 * (int)(short)(ushort)DAT_febe500c) * 8;
      *(undefined4 *)(((undefined *)camry_host_ptr(0xfebe4c3cu)) + iVar2) = *puVar1;
      *(undefined4 *)(((undefined *)camry_host_ptr(0xfebe4c40u)) + iVar2) = puVar1[1];
    }
    *(undefined2 *)(((undefined *)camry_host_ptr(0xfebe4ec0u)) + uVar3 * 2) = param_3;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe4ee7u + (uint32_t)(uVar3) * 1u)))) = param_1;
    uVar3 = uVar3 + 1 & 0xff;
    if (uVar6 <= uVar3) {
      uVar3 = 0;
    }
    if ((uVar3 == uVar8) && (DAT_febe500d = (byte)(uVar8 + 1), uVar6 <= (uVar8 + 1 & 0xff))) {
      DAT_febe500d = 0;
    }
    DAT_febe500c = (byte)uVar3;
  }
  return;
}



void FUN_00083072(undefined1 param_1)

{
  FUN_00083570(param_1);
  return;
}



/* Far-call trampoline: prepare {lp},0 / jarl 0x8228E / dispose 0,{lp},lp; byte-verified against the
   exact image. Forwards with registers and stack unchanged; marked as a thunk. Forwarding shape
   machine-verified; target semantics not recovered. */

void thunk_FUN_0008228e(void)

{
  FUN_0008228e();
  return;
}



void FUN_00083098(undefined4 param_1,undefined1 param_2)

{
  FUN_00098f2c(((undefined *)camry_host_ptr((uint32_t)(param_1))), param_2);
  return;
}



void FUN_000830a6(undefined4 param_1,undefined1 param_2)

{
  FUN_00098ef2(((undefined *)camry_host_ptr((uint32_t)(param_1))), param_2);
  return;
}



void FUN_000830c0(undefined1 param_1,undefined4 param_2,undefined2 param_3)

{
  FUN_00098e80(param_1, ((char *)camry_host_ptr((uint32_t)(param_2))), param_3);
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_83156(void)

{
  return;
}



bool FUN_00083172(void)

{
  return DAT_febe3df4 == '\x0f';
}



void FUN_000831be(uint param_1,undefined1 param_2,undefined1 param_3)

{
  uint uVar1;
  
  param_1 = param_1 & 0xff;
  uVar1 = (uint)DAT_00021865;
  if (param_1 < uVar1) {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe3deau + (uint32_t)(param_1) * 1u)))) = param_2;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe3deau + (uint32_t)(param_1 + uVar1) * 1u)))) = param_3;
  }
  return;
}



void FUN_000831dc(uint param_1,undefined1 param_2)

{
  if ((param_1 & 0xff) < (uint)DAT_00021865) {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe3decu + (uint32_t)((param_1 & 0xff) + (uint)DAT_00021865) * 1u)))) = param_2;
  }
  return;
}



void FUN_000831f0(uint param_1,undefined1 param_2)

{
  if ((param_1 & 0xff) < (uint)DAT_00021865) {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe3deeu + (uint32_t)((param_1 & 0xff) + (uint)DAT_00021865) * 1u)))) = param_2;
  }
  return;
}



void FUN_00083204(byte param_1,char param_2)

{
  undefined4 uVar1;
  
  if ((param_1 < DAT_00021865) &&
     (((uVar1 = 0xc0, param_2 == '\x03' || (uVar1 = 0x80, param_2 == '\x01')) ||
      (uVar1 = 0x40, param_2 == '\x02')))) {
    FUN_0007e29c(param_1,uVar1);
  }
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_83280(void)

{
  return;
}



void FUN_00083282(char param_1)

{
  FUN_00079f9a(DAT_0002183d + param_1);
  return;
}



void FUN_00083298(char param_1)

{
  FUN_00079fba(DAT_0002183d + param_1);
  return;
}



void FUN_000832ae(char param_1)

{
  FUN_00079fda(DAT_0002183d + param_1);
  return;
}



void FUN_000832c4(char param_1)

{
  FUN_0007a002(DAT_0002183d + param_1);
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_832ee(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_832f0(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_832f2(void)

{
  return;
}



void FUN_000832f4(short param_1)

{
  uint uVar1;
  int iVar2;
  byte bVar3;
  uint uVar4;
  uint uVar5;
  uchar uVar6;
  uint uVar7;
  
  if (param_1 == 1) {
    uVar7 = (uint)DAT_00021c68;
    for (uVar4 = 0; uVar4 < uVar7; uVar4 = uVar4 + 1 & 0xffff) {
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe4a48u + (uint32_t)(uVar4) * 1u)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x22184u + (uint32_t)(uVar4) * 1u))));
    }
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe4a48u + (uint32_t)(uVar7) * 1u)))) = 0;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe4a49u + (uint32_t)(uVar7) * 1u)))) = 0;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe4a4au + (uint32_t)(uVar7) * 1u)))) = 0;
  }
  uVar7 = (uint)DAT_00021c54;
  uVar4 = 0;
  if (param_1 == 4) {
    uVar4 = (uint)DAT_00021c6e;
    for (uVar7 = 0; uVar7 < uVar4; uVar7 = uVar7 + 1 & 0xff) {
      iVar2 = uVar7 * 4;
      uVar5 = (uint)*(ushort *)(((undefined *)camry_host_ptr(0x22140u)) + iVar2);
      uVar1 = *(ushort *)(((undefined *)camry_host_ptr(0x22142u)) + iVar2) + uVar5;
      bVar3 = f33_com_tx_pending_and_group_state[uVar7 + 3];
      for (; uVar5 < (uVar1 & 0xffff); uVar5 = uVar5 + 1 & 0xffff) {
        uVar6 = '\x01';
        if (((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x22148u + (uint32_t)(uVar5) * 1u)))) & bVar3) != 0) {
          uVar6 = 0x81;
        }
        f33_com_tx_pdu_flags[uVar5] = uVar6;
      }
      uVar5 = (uint)*(ushort *)(((undefined *)camry_host_ptr(0x22144u)) + iVar2);
      uVar1 = *(ushort *)(((undefined *)camry_host_ptr(0x22146u)) + iVar2) + uVar5;
      bVar3 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe4a42u + (uint32_t)(uVar7) * 1u))));
      for (; uVar5 < (uVar1 & 0xffff); uVar5 = uVar5 + 1 & 0xffff) {
        uVar6 = '\x01';
        if (((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x22148u + (uint32_t)(uVar5) * 1u)))) & bVar3) != 0) {
          uVar6 = 0x81;
        }
        f33_com_tx_pdu_flags[uVar5] = uVar6;
      }
    }
  }
  else {
    for (; uVar4 < uVar7; uVar4 = uVar4 + 1 & 0xffff) {
      f33_com_tx_pdu_flags[uVar4] = '\x01';
    }
  }
  return;
}



/* Single constant publisher: DAT_febe4a47 = 0xa5; Shape-classified from the canonical corpus; the
   target cell is not yet named, so the written state's meaning is unknown. */

void FUN_000833cc(void)

{
  DAT_febe4a47 = 0xa5;
  return;
}



/* Single constant publisher: DAT_febe4a47 = 0x5a; Shape-classified from the canonical corpus; the
   target cell is not yet named, so the written state's meaning is unknown. */

void FUN_000833d6(void)

{
  DAT_febe4a47 = 0x5a;
  return;
}



/* Constant source: return 1; shape-classified from the canonical corpus. Callers receive this
   literal directly; its meaning is not recovered. */

undefined4 f33_return_const_1_833e0(void)

{
  return 1;
}



void FUN_0008344e(uint param_1)

{
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe4935u + (uint32_t)((param_1 & 0xff) * 0x10) * 1u)))) = 0xe1;
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_8356c(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_8356e(void)

{
  return;
}



bool FUN_00083570(char param_1)

{
  if (DAT_febe5005 == '\x01') {
    return DAT_febe5004 != param_1;
  }
  return true;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_83590(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_83592(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_83594(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_83596(void)

{
  return;
}



/* Constant source: return 1; shape-classified from the canonical corpus. Callers receive this
   literal directly; its meaning is not recovered. */

undefined4 f33_return_const_1_83598(void)

{
  return 1;
}



void FUN_0008359c(void)

{
  uint uVar1;
  uint uVar2;
  
  uVar2 = (uint)DAT_00022e41;
  for (uVar1 = 0; uVar1 < uVar2; uVar1 = uVar1 + 1 & 0xff) {
    f33_driver_bus_off_observation_latch[uVar1] = '<';
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe5013u + (uint32_t)(uVar1) * 1u)))) = 0;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe5016u + (uint32_t)(uVar1) * 1u)))) = 0x5a;
  }
  return;
}



void FUN_000835c6(uint param_1)

{
  f33_driver_bus_off_observation_latch[param_1 & 0xff] = '<';
  return;
}



void FUN_0008366e(uint param_1)

{
  f33_driver_bus_off_observation_latch[param_1 & 0xff] = 'Z';
  return;
}



void FUN_00083702(undefined1 param_1)

{
  ((void)(param_1), f33_return_only_stub_6a420());
  return;
}



bool FUN_00083710(uint param_1)

{
  return (param_1 & 0xff) + ((int)(param_1 & 0xffff) >> 8) != 0xff;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_83806(void)

{
  return;
}



void FUN_00083862(uint param_1,uint param_2)

{
  int *piVar1;
  uint uVar2;
  int iVar3;
  
  iVar3 = 0x5a;
  uVar2 = 0;
  (*((uint *)camry_host_ptr((uint32_t)(PTR_DAT_00023088)))) = (param_1 & 0x7f) << 0x10;
  while ((uVar2 < (param_2 & 0xff) && (iVar3 == 0x5a))) {
    piVar1 = ((int *)camry_host_ptr((uint32_t)(PTR_DAT_000230b0 + uVar2 * 4)));
    *piVar1 = -0x55555556;
    if ((*piVar1 == -0x55555556) && (*piVar1 = 0x55555555, *piVar1 == 0x55555555)) {
      *piVar1 = 0;
    }
    else {
      iVar3 = 0xa5;
    }
    uVar2 = uVar2 + 1 & 0xff;
  }
  return;
}



bool FUN_000838ba(void)

{
  uint32_t puVar1;
  puVar1 = 0x23dfcu;
  (*((undefined4 *)camry_host_ptr((uint32_t)(PTR_DAT_0002308c)))) = 0;
  FUN_000842fe();
  return (**(uint **)(puVar1 + -0xdb8) & 0xf) != 1;
}



undefined4 FUN_00083956(uint param_1,undefined1 param_2)

{
  char cVar1;
  uint uVar2;
  uint32_t puVar3;
  int iVar4;
  uint uVar5;
  
  puVar3 = 0xfebeb800u;
  cVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe5019u + (uint32_t)(param_1 & 0xff) * 1u))));
  if (cVar1 == 'Z') {
    uVar5 = (uint)DAT_00022ea4;
    for (uVar2 = 0; uVar2 < uVar5; uVar2 = uVar2 + 1 & 0xff) {
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe5019u + (uint32_t)(uVar2) * 1u)))) = 0x69;
    }
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe5019u + (uint32_t)(param_1 & 0xff) * 1u)))) = 'Z';
    iVar4 = ((void)(param_2), FUN_000838dc());
    if (iVar4 != 0x5a) {
      uVar2 = 0;
      if (iVar4 != 0x96) {
        for (; uVar2 < uVar5; uVar2 = uVar2 + 1 & 0xff) {
          (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(uVar2 - 0x67e7))))) = 0x96;
        }
        return 1;
      }
      for (; uVar2 < uVar5; uVar2 = uVar2 + 1 & 0xff) {
        (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(uVar2 - 0x67e7))))) = 0xa5;
      }
    }
  }
  else if ((cVar1 != 'i') && (cVar1 != -0x5b)) {
    uVar5 = (uint)DAT_00022ea4;
    for (uVar2 = 0; uVar2 < uVar5; uVar2 = uVar2 + 1 & 0xff) {
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe5019u + (uint32_t)(uVar2) * 1u)))) = 0x96;
    }
    return 1;
  }
  return 0;
}



void FUN_00083a88(undefined1 param_1)

{
  FUN_00083a34(param_1);
  FUN_00085938();
  return;
}



void FUN_00083aa0(void)

{
  FUN_00083a88(0);
  return;
}



void FUN_00083aae(void)

{
  FUN_00083a88(1);
  return;
}



void FUN_00083abc(void)

{
  FUN_00083a88(2);
  return;
}



void FUN_00083c72(void)

{
  uint uVar1;
  uint uVar2;
  
  uVar2 = (uint)DAT_00022ea4;
  for (uVar1 = 0; uVar1 < uVar2; uVar1 = uVar1 + 1 & 0xff) {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe5019u + (uint32_t)(uVar1) * 1u)))) = 0x5a;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe501cu + (uint32_t)(uVar1) * 1u)))) = 0xa5;
  }
  return;
}



/* Constant source: return 1; shape-classified from the canonical corpus. Callers receive this
   literal directly; its meaning is not recovered. */

undefined4 f33_return_const_1_83c98(void)

{
  return 1;
}



void FUN_00083c9c(uint param_1)

{
  char cVar1;
  uint uVar2;
  uint uVar3;
  
  cVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe5019u + (uint32_t)(param_1 & 0xff) * 1u))));
  if ((cVar1 == 'Z') || (cVar1 == -0x6a)) {
    uVar3 = (uint)DAT_00022ea4;
    for (uVar2 = 0; uVar2 < uVar3; uVar2 = uVar2 + 1 & 0xff) {
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe5019u + (uint32_t)(uVar2) * 1u)))) = 0x69;
    }
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe5019u + (uint32_t)(param_1 & 0xff) * 1u)))) = 'Z';
  }
  return;
}



void FUN_00083cd6(uint param_1)

{
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe501cu + (uint32_t)(param_1 & 0xff) * 1u)))) = 0x5a;
  return;
}



void FUN_00083ce4(void)

{
  undefined8 uVar1;
  uint uVar2;
  uint uVar3;
  
  uVar1 = 0x23dfcfebeb800;
  uVar2 = (uint)DAT_00022e41;
  for (uVar3 = 0; uVar3 < uVar2; uVar3 = uVar3 + 1 & 0xff) {
    if ((*((short *)camry_host_ptr((uint32_t)(uVar3 * 2 + (int)uVar1 + -0x67e0)))) == 0x57a8) {
      FUN_00083eda(uVar3,1);
    }
  }
  return;
}



void FUN_00083d14(uint param_1,ushort param_2,undefined4 *param_3)

{
  int iVar1;
  
  iVar1 = (param_1 & 0xff) * 8;
  FUN_00080b42(*(short *)(((undefined *)camry_host_ptr(0x22e46u)) + iVar1) +
               ((param_2 & 0xff) - (ushort)(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x22e4bu + (uint32_t)(iVar1) * 1u))))),param_3[1],
               *(undefined1 *)(param_3 + 2),*param_3);
  return;
}



undefined4 FUN_00083e0c(uint param_1)

{
  uint *puVar1;
  int iVar2;
  byte bVar3;
  uint uVar4;
  undefined8 uVar5;
  int iVar6;
  uint uVar7;
  undefined4 uVar8;
  uint uVar9;
  uint uVar10;
  uint local_60 [16];
  undefined1 *puStack_20;
  uint uStack_1c;
  byte bStack_18;
  
  uVar5 = 0x23dfc00000000;
  puStack_20 = ((undefined1 *)camry_host_ptr((uint32_t)(local_60)));
  param_1 = param_1 & 0xff;
  iVar2 = param_1 * 4;
  uVar8 = 1;
  (*((undefined4 *)camry_host_ptr((uint32_t)(PTR_DAT_00023064 + iVar2)))) = 5;
  puVar1 = ((uint *)camry_host_ptr((uint32_t)(PTR_DAT_000230ac + param_1 * 0x80)));
  for (uVar10 = ((*((uint *)camry_host_ptr((uint32_t)(PTR_DAT_00023064 + iVar2)))) & 0xff00) >> 8; uVar10 != 0;
      uVar10 = uVar10 - 1) {
    uVar9 = *puVar1;
    uVar7 = puVar1[1];
    iVar6 = (int)((ulonglong)uVar5 >> 0x20);
    if ((puVar1[2] >> 2 & 1) == 0) {
      local_60[0] = puVar1[3];
      bStack_18 = (byte)(uVar7 >> 0x1c);
      local_60[1] = puVar1[4];
      (*((undefined4 *)camry_host_ptr((uint32_t)(*(int *)(iVar6 + -0xd94) + iVar2)))) = 0xff;
      uStack_1c = uVar9 & 0x9fffffff;
    }
    else {
      bVar3 = (*((byte *)camry_host_ptr((uint32_t)(param_1 + iVar6 + -0xf48))));
      for (uVar4 = 0; uVar4 < bVar3; uVar4 = uVar4 + 1 & 0xff) {
        local_60[uVar4] = puVar1[uVar4 + 3];
      }
      (*((undefined4 *)camry_host_ptr((uint32_t)(*(int *)(iVar6 + -0xd94) + iVar2)))) = 0xff;
      uStack_1c = uVar9 & 0x9fffffff | 0x40000000;
      bStack_18 = (*((byte *)camry_host_ptr((uint32_t)((uVar7 >> 0x1c) + iVar6 + -0xfd4))));
    }
    FUN_00083d14(param_1,uVar7 >> 0x10 & 0xff,&puStack_20);
    uVar8 = 0;
  }
  return uVar8;
}



void FUN_00083f30(void)

{
  FUN_00083ef2(1);
  return;
}


