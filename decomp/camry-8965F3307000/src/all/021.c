#include "common.h"


/* Poll3BC4/3EC1/3DC2andcommitstateonlyonzeroresult;nocreatedphysicalsuccess. Calledby79F16. */

void f33_driver_poll_pending_channel_modes(void)

{
  short sVar1;
  uint32_t puVar2;
  uint32_t puVar3;
  undefined4 uVar4;
  int iVar5;
  uint uVar6;
  undefined2 *puVar7;
  uint uVar8;
  
  puVar2 = 0xfebeb800u;
  puVar3 = 0x23dfcu;
  uVar6 = (uint)DAT_00022e41;
  uVar8 = 0;
  do {
    if (uVar6 <= uVar8) {
      return;
    }
    sVar1 = (*((short *)camry_host_ptr((uint32_t)(puVar2 + uVar8 * 2 + -0x67e0))));
    puVar7 = ((undefined2 *)camry_host_ptr((uint32_t)(puVar2 + uVar8 * 2 + -0x67e0)));
    if (sVar1 == 0x3bc4) {
      iVar5 = FUN_00084e8c(uVar8);
      if (iVar5 == 0) {
        *puVar7 = 0x57a8;
        uVar4 = 2;
LAB_0008412a:
        ((void)(uVar8), (void)(uVar4), f33_return_only_stub_7fb5c());
      }
    }
    else if (sVar1 == 0x3ec1) {
      if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(uVar8 * 4 + -0xf9d))))) == '\0') {
        f33_driver_observe_and_clear_bus_off_entry((uchar)uVar8);
      }
      iVar5 = FUN_00084ec0(uVar8);
      if (iVar5 == 0) {
        *puVar7 = 0x6b94;
        uVar4 = 3;
        goto LAB_0008412a;
      }
    }
    else if ((sVar1 == 0x3dc2) && (iVar5 = FUN_00084f06(uVar8), iVar5 == 0)) {
      FUN_000835c6(uVar8);
      ((void)(uVar8), FUN_00084fea());
      *puVar7 = 0x6b94;
    }
    uVar8 = uVar8 + 1 & 0xff;
  } while( true );
}



void FUN_00084160(void)

{
  byte bVar1;
  uint32_t puVar2;
  uint32_t puVar3;
  undefined4 uVar4;
  uint uVar5;
  
  puVar2 = 0xfebeb800u;
  puVar3 = 0x23dfcu;
  uVar4 = FUN_0007a2da();
  bVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0xfbb)))));
  for (uVar5 = 0; uVar5 < bVar1; uVar5 = uVar5 + 1 & 0xff) {
    (*((undefined2 *)camry_host_ptr((uint32_t)(puVar2 + uVar5 * 2 + -0x67e0)))) = 0x6e91;
  }
  ((void)(uVar4), thunk_FUN_0006a4c4());
  FUN_00084f90();
  for (uVar5 = 0; uVar5 < bVar1; uVar5 = uVar5 + 1 & 0xff) {
    FUN_000835c6(uVar5);
  }
  return;
}



int FUN_000841a6(uint param_1)

{
  int iVar1;
  
  param_1 = param_1 & 0xff;
  f33_driver_channel_software_states[param_1] = recovery_pending;
  FUN_000850e0((uint)(byte)param_1);
  iVar1 = FUN_00084e44(param_1);
  if (iVar1 == 0) {
    ((void)(param_1), FUN_00084fea());
    f33_driver_channel_software_states[param_1] = stopped_software_state;
  }
  FUN_000835c6(param_1);
  return iVar1;
}



bool FUN_000841e6(undefined1 param_1,undefined2 param_2)

{
  int iVar1;
  
  iVar1 = FUN_00085012(param_1,param_2);
  return iVar1 != 0;
}



bool FUN_000841fc(uint param_1)

{
  if (f33_driver_channel_software_states[param_1 & 0xff] != initialized) {
    return f33_driver_channel_software_states[param_1 & 0xff] != stopped_software_state;
  }
  return false;
}



int FUN_00084274(uint param_1)

{
  int iVar1;
  
  f33_driver_channel_software_states[param_1 & 0xff] = stop_pending;
  iVar1 = FUN_00084b74((uint)(byte)param_1);
  if (iVar1 == 0) {
    f33_driver_channel_software_states[param_1 & 0xff] = stopped_software_state;
  }
  return iVar1;
}



void FUN_000842a0(uint param_1)

{
  F33DriverChannelSoftwareState FVar1;
  
  FVar1 = f33_driver_channel_software_states[param_1 & 0xff];
  if ((((FVar1 == start_pending) || (FVar1 == recovery_pending)) || (FVar1 == stop_pending)) ||
     (FVar1 == running_software_state)) {
    f33_driver_channel_software_states[param_1 & 0xff] = stopped_software_state;
  }
  return;
}



void FUN_000842ce(undefined1 param_1)

{
  ((void)(param_1), f33_return_only_stub_6a434());
  return;
}



void FUN_000842dc(void)

{
  uint uVar1;
  uint uVar2;
  
  uVar2 = (uint)DAT_00022ea4;
  for (uVar1 = 0; uVar1 < uVar2; uVar1 = uVar1 + 1 & 0xff) {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe5026u + (uint32_t)(uVar1) * 1u)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x22eabu + (uint32_t)(uVar1) * 1u))));
  }
  return;
}



undefined4 FUN_000842fe(void)

{
  ushort uVar1;
  ushort uVar2;
  uint32_t puVar3;
  undefined4 uVar4;
  uint uVar5;
  
  uVar1 = DAT_00022e8e;
  puVar3 = 0x23dfcu;
  uVar4 = FUN_0007a2da();
  **(undefined4 **)(puVar3 + -0xdbc) = 0x10001;
  uVar2 = 0;
  uVar5 = 0xfffffffe;
  while ((uVar2 < uVar1 && ((uVar5 & 0xf) != 1))) {
    uVar2 = uVar2 + 1;
    uVar5 = **(uint **)(puVar3 + -0xdb8);
  }
  ((void)(uVar4), thunk_FUN_0006a4c4());
  return uVar4;
}



void FUN_0008433c(void)

{
  int iVar1;
  ushort uVar2;
  uint uVar3;
  uint uVar4;
  ushort uVar5;
  uint uVar6;
  
  (*((undefined4 *)camry_host_ptr((uint32_t)(PTR_DAT_00023038)))) = 1;
  (*((undefined4 *)camry_host_ptr((uint32_t)(PTR_GCTR_00023040)))) = 0x10001;
  (*((undefined4 *)camry_host_ptr((uint32_t)(PTR_DAT_00023090)))) = 0;
  (*((undefined4 *)camry_host_ptr((uint32_t)(PTR_DAT_00023094)))) = 0;
  (*((undefined4 *)camry_host_ptr((uint32_t)(PTR_DAT_00023054)))) = 0;
  uVar3 = (uint)DAT_00022ea5;
  for (uVar6 = 0; uVar6 < uVar3; uVar6 = uVar6 + 1 & 0xff) {
    (*((uint *)camry_host_ptr((uint32_t)(PTR_DAT_00023050)))) = uVar6 | 0x100;
    uVar4 = 0;
    do {
      iVar1 = uVar4 * 0x10;
      uVar4 = uVar4 + 1;
      (*((undefined4 *)camry_host_ptr((uint32_t)(PTR_DAT_000230a4 + iVar1)))) = 0xffffffff;
      (*((undefined4 *)camry_host_ptr((uint32_t)(PTR_DAT_000230a4 + iVar1 + 4)))) = 0xdfffffff;
      (*((undefined4 *)camry_host_ptr((uint32_t)(PTR_DAT_000230a4 + iVar1 + 8)))) = 0;
      (*((undefined4 *)camry_host_ptr((uint32_t)(PTR_DAT_000230a4 + iVar1 + 0xc)))) = 0;
    } while (uVar4 < 0x10);
  }
  (*((undefined4 *)camry_host_ptr((uint32_t)(PTR_DAT_00023050)))) = 0;
  uVar3 = 0;
  (*((undefined4 *)camry_host_ptr((uint32_t)(PTR_GCFG_0002303c)))) = 0;
  (*((undefined4 *)camry_host_ptr((uint32_t)(PTR_DAT_00023058)))) = 0;
  do {
    iVar1 = uVar3 * 4;
    uVar3 = uVar3 + 1;
    (*((undefined4 *)camry_host_ptr((uint32_t)(PTR_DAT_00023060 + iVar1)))) = 0;
  } while (uVar3 < 8);
  uVar5 = (ushort)DAT_00022ea4;
  for (uVar2 = 0; uVar2 < uVar5; uVar2 = uVar2 + 1 & 0xff) {
    if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x22ecbu + (uint32_t)((short)uVar2 * 6) * 1u)))) == '\0') {
      iVar1 = (int)(short)uVar2;
      (*((undefined4 *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x22f34u + (uint32_t)(iVar1 * 0x1d) * 4u))))))) = 0;
      (*((undefined4 *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x22f34u + (uint32_t)(iVar1 * 0x1d) * 4u)))) + 4)))) = 0;
      (*((undefined4 *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x22f34u + (uint32_t)(iVar1 * 0x1d) * 4u)))) + 8)))) = 0;
    }
  }
  return;
}



undefined4 FUN_00084420(ushort param_1)

{
  int iVar1;
  ushort uVar2;
  ushort uVar3;
  undefined4 uVar4;
  uint uVar5;
  
  uVar2 = DAT_00022e8c;
  iVar1 = (int)(short)(param_1 & 0xff);
  uVar4 = FUN_0007a2da();
  (*((uint *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x22ef4u + (uint32_t)(iVar1 * 0x1d) * 4u))))))) =
       (*((uint *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x22ef4u + (uint32_t)(iVar1 * 0x1d) * 4u))))))) & 0xfffffff8 | 1;
  uVar3 = 0;
  uVar5 = 0xfffffffe;
  while ((uVar3 < uVar2 && ((uVar5 & 7) != 1))) {
    uVar3 = uVar3 + 1;
    uVar5 = (*((uint *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x22ef8u + (uint32_t)(iVar1 * 0x1d) * 4u)))))));
  }
  ((void)(uVar4), thunk_FUN_0006a4c4());
  return uVar4;
}



void FUN_00084474(ushort param_1)

{
  int iVar1;
  int iVar2;
  uint uVar3;
  int iVar4;
  uint uVar5;
  int iVar6;
  
  iVar1 = (int)(short)(param_1 & 0xff);
  iVar6 = iVar1 * 0x74;
  (*((undefined4 *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x22ef0u + (uint32_t)(iVar1 * 0x1d) * 4u))))))) = 0;
  (*((undefined4 *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x22ef4u + (uint32_t)(iVar1 * 0x1d) * 4u))))))) = 1;
  (*((undefined4 *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x22f00u + (uint32_t)(iVar1 * 0x1d) * 4u))))))) = 0;
  (*((undefined4 *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x22f04u + (uint32_t)(iVar1 * 0x1d) * 4u))))))) = 0x8000000;
  uVar3 = 0;
  do {
    iVar4 = (short)uVar3 * 0x60;
    (*((undefined4 *)camry_host_ptr((uint32_t)(*(int *)(((undefined *)camry_host_ptr(0x22f48u)) + iVar6) + iVar4)))) = 0x9fffffff;
    (*((undefined4 *)camry_host_ptr((uint32_t)(*(int *)(((undefined *)camry_host_ptr(0x22f48u)) + iVar6) + iVar4 + 4)))) = 0;
    (*((undefined4 *)camry_host_ptr((uint32_t)(*(int *)(((undefined *)camry_host_ptr(0x22f48u)) + iVar6) + iVar4 + 8)))) = 0;
    uVar5 = 0;
    do {
      iVar2 = uVar5 * 4;
      uVar5 = uVar5 + 1;
      (*((undefined4 *)camry_host_ptr((uint32_t)(iVar2 + *(int *)(((undefined *)camry_host_ptr(0x22f48u)) + iVar6) + iVar4 + 0xc)))) = 0;
    } while (uVar5 < 0x10);
    uVar3 = uVar3 + 1;
  } while (uVar3 < 2);
  uVar3 = 6;
  do {
    iVar6 = uVar3 * 0x20;
    (*((undefined4 *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x22f44u + (uint32_t)(iVar1 * 0x1d) * 4u)))) + iVar6)))) = 0x9fffffff;
    (*((undefined4 *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x22f44u + (uint32_t)(iVar1 * 0x1d) * 4u)))) + iVar6 + 4)))) = 0;
    (*((undefined4 *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x22f44u + (uint32_t)(iVar1 * 0x1d) * 4u)))) + iVar6 + 8)))) = 0;
    uVar5 = 0;
    do {
      iVar4 = uVar5 * 4;
      uVar5 = uVar5 + 1;
      (*((undefined4 *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x22f44u + (uint32_t)(iVar1 * 0x1d) * 4u)))) + iVar4 + iVar6 + 0xc)))) = 0;
    } while (uVar5 < 5);
    uVar3 = uVar3 + 1;
  } while (uVar3 < 0x10);
  (*((undefined2 *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x22edcu + (uint32_t)(iVar1 * 0x1d) * 4u))))))) = 0;
  (*((undefined4 *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x22f14u + (uint32_t)(iVar1 * 0x1d) * 4u))))))) = 0;
  (*((undefined4 *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x22f20u + (uint32_t)(iVar1 * 0x1d) * 4u))))))) = 0;
  return;
}



void FUN_00084534(ushort param_1)

{
  ushort uVar1;
  uint uVar2;
  
  param_1 = param_1 & 0xff;
  uVar2 = 1;
  (*((uint *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x22ef4u + (uint32_t)((short)param_1 * 0x1d) * 4u))))))) =
       *(uint *)(((undefined *)camry_host_ptr(0x233c8u)) + (short)param_1 * 0x34) | 5;
  uVar1 = 0;
  do {
    if ((uVar2 & 7) == 5) {
      return;
    }
    uVar1 = uVar1 + 1;
    uVar2 = (*((uint *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x22ef8u + (uint32_t)((short)param_1 * 0x1d) * 4u)))))));
  } while (uVar1 < 3);
  return;
}



void FUN_00084570(void)

{
  int iVar1;
  int iVar2;
  short sVar3;
  uint uVar4;
  uint uVar5;
  
  (*((undefined4 *)camry_host_ptr((uint32_t)(PTR_DAT_00023038)))) = 1;
  (*((undefined4 *)camry_host_ptr((uint32_t)(PTR_DAT_00023094)))) = 0;
  (*((undefined4 *)camry_host_ptr((uint32_t)(PTR_DAT_00023090)))) = DAT_00022e84;
  (*((undefined4 *)camry_host_ptr((uint32_t)(PTR_GCFG_0002303c)))) = DAT_00022e80;
  (*((undefined4 *)camry_host_ptr((uint32_t)(PTR_GCTR_00023040)))) = 0x10001;
  uVar5 = (uint)DAT_00022ea4;
  for (uVar4 = 0; uVar4 < uVar5; uVar4 = uVar4 + 1 & 0xff) {
    sVar3 = (short)uVar4;
    if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x22ecbu + (uint32_t)(sVar3 * 6) * 1u)))) == '\0') {
      iVar1 = (int)sVar3;
      iVar2 = (int)sVar3;
      (*((uint *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x22f34u + (uint32_t)(iVar1 * 0x1d) * 4u))))))) =
           (uint)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x233b8u + (uint32_t)(iVar2 * 0xd) * 4u)))) & 0xfffffff8;
      (*((uint *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x22f34u + (uint32_t)(iVar1 * 0x1d) * 4u)))) + 4)))) =
           (uint)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x233bcu + (uint32_t)(iVar2 * 0xd) * 4u)))) & 0xfffffff8;
      (*((uint *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x22f34u + (uint32_t)(iVar1 * 0x1d) * 4u)))) + 8)))) = (*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x233c0u + (uint32_t)(iVar2 * 0xd) * 4u)))) & 0xfffffff8;
    }
  }
  for (uVar4 = 0; uVar4 < uVar5; uVar4 = uVar4 + 1 & 0xff) {
    (*((uint *)camry_host_ptr((uint32_t)(PTR_DAT_00023060 + uVar4 * 4)))) = (*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x233d8u + (uint32_t)((short)uVar4 * 0xd) * 4u)))) & 0xfffffffc;
  }
  for (; uVar5 < 8; uVar5 = uVar5 + 1) {
    (*((undefined4 *)camry_host_ptr((uint32_t)(PTR_DAT_00023060 + uVar5 * 4)))) = 0;
  }
  (*((undefined4 *)camry_host_ptr((uint32_t)(PTR_DAT_00023058)))) = 0;
  return;
}



undefined4 FUN_00084652(void)

{
  byte bVar1;
  uint uVar2;
  undefined8 uVar3;
  int iVar4;
  uint uVar5;
  ushort uVar6;
  undefined4 uVar7;
  
  uVar3 = 0x23dfc00000000;
  uVar7 = 2;
  FUN_00083c72();
  FUN_000842dc();
  iVar4 = (int)((ulonglong)uVar3 >> 0x20);
  uVar5 = 0;
  uVar2 = 0xffffffff;
  while ((uVar5 < (*((uint *)camry_host_ptr((uint32_t)(iVar4 + -0xf84)))) && ((uVar2 >> 3 & 1) != 0))) {
    uVar5 = uVar5 + 1;
    uVar2 = **(uint **)(iVar4 + -0xdb8);
  }
  if (((uVar2 >> 3 & 1) == 0) &&
     (FUN_000842fe(), (**(uint **)((int)((ulonglong)uVar3 >> 0x20) + -0xdb8) & 0xf) == 1)) {
    FUN_0008433c();
    bVar1 = (*((byte *)camry_host_ptr((uint32_t)((int)((ulonglong)uVar3 >> 0x20) + -0xf58))));
    for (uVar6 = 0; uVar6 < bVar1; uVar6 = uVar6 + 1 & 0xff) {
      iVar4 = (short)uVar6 * 6 + (int)((ulonglong)uVar3 >> 0x20);
      if ((*((char *)camry_host_ptr((uint32_t)(iVar4 + -0xf31)))) == '\0') {
        FUN_00084420(uVar6);
        if ((**(uint **)((short)uVar6 * 0x74 + (int)((ulonglong)uVar3 >> 0x20) + -0xf04) & 7) == 1)
        {
          FUN_00084474(uVar6);
        }
        if ((*((char *)camry_host_ptr((uint32_t)(iVar4 + -0xf30)))) != '\0') {
          FUN_00084534(uVar6);
        }
      }
    }
    FUN_00084570();
    uVar7 = 0;
  }
  return uVar7;
}



void FUN_000846f2(ushort param_1)

{
  int iVar1;
  int iVar2;
  
  if (((*((uint *)camry_host_ptr((uint32_t)(PTR_GSTS_00023044)))) & 0xf) == 1) {
    (*((undefined4 *)camry_host_ptr((uint32_t)(PTR_GCFG_0002303c)))) = DAT_00022e80;
  }
  iVar1 = (int)(short)(param_1 & 0xff);
  iVar2 = (short)(param_1 & 0xff) * 0x34;
  (*((uint *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x22ef4u + (uint32_t)(iVar1 * 0x1d) * 4u))))))) = *(uint *)(((undefined *)camry_host_ptr(0x233c8u)) + iVar2) | 1;
  (*((undefined2 *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x22edcu + (uint32_t)(iVar1 * 0x1d) * 4u))))))) = 0;
  (*((undefined4 *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x22f14u + (uint32_t)(iVar1 * 0x1d) * 4u))))))) = 0;
  (*((undefined4 *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x22f20u + (uint32_t)(iVar1 * 0x1d) * 4u))))))) = 0;
  (*((undefined4 *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x22ef0u + (uint32_t)(iVar1 * 0x1d) * 4u))))))) = *(undefined4 *)(((undefined *)camry_host_ptr(0x233c4u)) + iVar2);
  (*((undefined4 *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x22f00u + (uint32_t)(iVar1 * 0x1d) * 4u))))))) = *(undefined4 *)(((undefined *)camry_host_ptr(0x233dcu)) + iVar2);
  (*((undefined4 *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x22f04u + (uint32_t)(iVar1 * 0x1d) * 4u))))))) = *(undefined4 *)(((undefined *)camry_host_ptr(0x233e0u)) + iVar2);
  (*((undefined4 *)camry_host_ptr((uint32_t)(PTR_DAT_00023048)))) = 0;
  return;
}



undefined4 FUN_00084760(uint param_1)

{
  undefined4 uVar1;
  
  param_1 = param_1 & 0xff;
  uVar1 = 2;
  if ((((*((uint *)camry_host_ptr((uint32_t)(PTR_GSTS_00023044)))) & 0xf) < 2) &&
     (((*((uint *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x22ef8u + (uint32_t)((short)param_1 * 0x1d) * 4u))))))) & 7) == 1)) {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe5026u + (uint32_t)(param_1) * 1u)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x22eabu + (uint32_t)(param_1) * 1u))));
    FUN_000846f2((uint)(byte)param_1);
    uVar1 = 0;
  }
  return uVar1;
}



void FUN_000847a4(void)

{
  int iVar1;
  int iVar2;
  uint uVar3;
  uint uVar4;
  undefined4 uVar5;
  
  (*((undefined4 *)camry_host_ptr((uint32_t)(PTR_DAT_00023054)))) = DAT_00022e7c;
  uVar4 = (uint)DAT_00022e90;
  for (uVar3 = 0; uVar3 < uVar4; uVar3 = uVar3 + 1 & 0xffff) {
    (*((uint *)camry_host_ptr((uint32_t)(PTR_DAT_00023050)))) = uVar3 >> 4 & 0x1f | 0x100;
    iVar1 = uVar3 * 0x10;
    uVar5 = *(undefined4 *)(((undefined *)camry_host_ptr(0x22e68u)) + (uint)(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x230c4u + (uint32_t)(iVar1) * 1u)))) * 4);
    iVar2 = (uVar3 & 0xf) * 0x10;
    (*((undefined4 *)camry_host_ptr((uint32_t)(PTR_DAT_000230a4 + iVar2)))) = *(undefined4 *)(((undefined *)camry_host_ptr(0x230b8u)) + iVar1);
    (*((undefined4 *)camry_host_ptr((uint32_t)(PTR_DAT_000230a4 + iVar2 + 4)))) = uVar5;
    (*((undefined4 *)camry_host_ptr((uint32_t)(PTR_DAT_000230a4 + iVar2 + 8)))) = *(undefined4 *)(((undefined *)camry_host_ptr(0x230bcu)) + iVar1);
    (*((undefined4 *)camry_host_ptr((uint32_t)(PTR_DAT_000230a4 + iVar2 + 0xc)))) = *(undefined4 *)(((undefined *)camry_host_ptr(0x230c0u)) + iVar1);
  }
  (*((undefined4 *)camry_host_ptr((uint32_t)(PTR_DAT_00023050)))) = 0;
  return;
}



void FUN_0008481c(void)

{
  ushort uVar1;
  uint uVar2;
  
  uVar2 = 1;
  (*((undefined4 *)camry_host_ptr((uint32_t)(PTR_GCTR_00023040)))) = 0x10000;
  uVar1 = 0;
  do {
    if ((uVar2 & 0xf) == 0) {
      return;
    }
    uVar1 = uVar1 + 1;
    uVar2 = (*((uint *)camry_host_ptr((uint32_t)(PTR_GSTS_00023044))));
  } while (uVar1 < 10);
  return;
}



void FUN_0008483e(void)

{
  FUN_00084570();
  FUN_000847a4();
  FUN_0008481c();
  return;
}



void FUN_00084852(ushort param_1)

{
  ushort uVar1;
  uint uVar2;
  
  param_1 = param_1 & 0xff;
  (*((undefined4 *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x22ef4u + (uint32_t)((short)param_1 * 0x1d) * 4u))))))) =
       *(undefined4 *)(((undefined *)camry_host_ptr(0x233c8u)) + (short)param_1 * 0x34);
  uVar1 = 0;
  uVar2 = 1;
  while ((uVar1 < DAT_00022e8a && ((uVar2 & 7) != 0))) {
    uVar1 = uVar1 + 1;
    uVar2 = (*((uint *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x22ef8u + (uint32_t)((short)param_1 * 0x1d) * 4u)))))));
  }
  return;
}



undefined4 FUN_0008488c(uint param_1)

{
  int iVar1;
  int iVar2;
  int iVar3;
  byte bVar4;
  byte bVar5;
  uint uVar6;
  uint32_t puVar7;
  int iVar8;
  uint uVar9;
  undefined4 uVar10;
  int iVar11;
  
  puVar7 = 0x23dfcu;
  param_1 = param_1 & 0xff;
  iVar1 = (int)(short)param_1;
  iVar2 = (int)(short)param_1;
  iVar11 = iVar2 * 0x74;
  uVar10 = 2;
  if (((((*((ushort *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x22ee0u + (uint32_t)(iVar2 * 0x1d) * 4u))))))) &
        (*(ushort *)(((undefined *)camry_host_ptr(0x22ebeu)) + param_1 * 4) | *(ushort *)(((undefined *)camry_host_ptr(0x22ebcu)) + param_1 * 4))) == 0)
      && (((*((uint *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x22f2cu + (uint32_t)(iVar2 * 0x1d) * 4u))))))) & 1) != 0)) &&
     (((*((uint *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x22f2cu + (uint32_t)(iVar2 * 0x1d) * 4u)))) + 4)))) & 1) != 0)) {
    puVar7 = 0x23dfcu;
    FUN_00084420(param_1);
  }
  if (((*((uint *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x22ef8u + (uint32_t)(iVar2 * 0x1d) * 4u))))))) & 7) == 1) {
    (*((uint *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x22ef4u + (uint32_t)(iVar2 * 0x1d) * 4u))))))) = *(uint *)(((undefined *)camry_host_ptr(0x233c8u)) + iVar1 * 0x34) | 1;
    **(undefined4 **)(puVar7 + -0xd60) = 0;
    (*((undefined4 *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x22f2cu + (uint32_t)(iVar2 * 0x1d) * 4u))))))) = 1;
    (*((undefined4 *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x22f2cu + (uint32_t)(iVar2 * 0x1d) * 4u)))) + 4)))) = 1;
    (*((undefined4 *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x22f2cu + (uint32_t)(iVar2 * 0x1d) * 4u)))) + 8)))) = 1;
    (*((uint *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x22f34u + (uint32_t)(iVar2 * 0x1d) * 4u)))) + 8)))) = (*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x233c0u + (uint32_t)(iVar1 * 0xd) * 4u)))) & 0xfffffffe;
    (*((undefined4 *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x22f34u + (uint32_t)(iVar2 * 0x1d) * 4u)))) + 8)))) = (*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x233c0u + (uint32_t)(iVar1 * 0xd) * 4u))));
    iVar8 = param_1 * 4;
    (*((undefined4 *)camry_host_ptr((uint32_t)(*(int *)(puVar7 + -0xd98) + iVar8)))) = 1;
    (*((uint *)camry_host_ptr((uint32_t)(*(int *)(puVar7 + -0xd9c) + iVar8)))) = (*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x233d8u + (uint32_t)(iVar1 * 0xd) * 4u)))) & 0xfffffffe;
    (*((undefined4 *)camry_host_ptr((uint32_t)(iVar8 + *(int *)(puVar7 + -0xd9c))))) = (*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x233d8u + (uint32_t)(iVar1 * 0xd) * 4u))));
    uVar6 = 0;
    do {
      iVar8 = (short)uVar6 * 0x60;
      (*((undefined4 *)camry_host_ptr((uint32_t)(*(int *)(((undefined *)camry_host_ptr(0x22f48u)) + iVar11) + iVar8)))) = 0x9fffffff;
      uVar9 = 0;
      (*((undefined4 *)camry_host_ptr((uint32_t)(*(int *)(((undefined *)camry_host_ptr(0x22f48u)) + iVar11) + iVar8 + 4)))) = 0;
      (*((undefined4 *)camry_host_ptr((uint32_t)(*(int *)(((undefined *)camry_host_ptr(0x22f48u)) + iVar11) + iVar8 + 8)))) = 0;
      do {
        iVar3 = uVar9 * 4;
        uVar9 = uVar9 + 1;
        (*((undefined4 *)camry_host_ptr((uint32_t)(iVar3 + *(int *)(((undefined *)camry_host_ptr(0x22f48u)) + iVar11) + iVar8 + 0xc)))) = 0;
      } while (uVar9 < 0x10);
      uVar6 = uVar6 + 1;
    } while (uVar6 < 2);
    bVar4 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar7 + (uint32_t)(param_1 - 0xf4e)))));
    uVar6 = 6;
    bVar5 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar7 + (uint32_t)(param_1 - 0xf4b)))));
    do {
      if ((bVar4 != uVar6) && (bVar5 != uVar6)) {
        iVar11 = uVar6 * 0x20;
        (*((undefined4 *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x22f44u + (uint32_t)(iVar2 * 0x1d) * 4u)))) + iVar11)))) = 0x9fffffff;
        uVar9 = 0;
        (*((undefined4 *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x22f44u + (uint32_t)(iVar2 * 0x1d) * 4u)))) + iVar11 + 4)))) = 0;
        (*((undefined4 *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x22f44u + (uint32_t)(iVar2 * 0x1d) * 4u)))) + iVar11 + 8)))) = 0;
        do {
          iVar8 = uVar9 * 4;
          uVar9 = uVar9 + 1;
          (*((undefined4 *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x22f44u + (uint32_t)(iVar2 * 0x1d) * 4u)))) + iVar8 + iVar11 + 0xc)))) = 0;
        } while (uVar9 < 5);
      }
      uVar6 = uVar6 + 1;
    } while (uVar6 < 0x10);
    (*((ushort *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x22edcu + (uint32_t)(iVar2 * 0x1d) * 4u))))))) =
         *(ushort *)(((undefined *)camry_host_ptr(0x22ebcu)) + param_1 * 4) & (*((ushort *)camry_host_ptr((uint32_t)(puVar7 + param_1 * 2 + -0xf68))));
    (*((undefined4 *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x22f14u + (uint32_t)(iVar2 * 0x1d) * 4u))))))) = 0;
    (*((undefined4 *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x22f20u + (uint32_t)(iVar2 * 0x1d) * 4u))))))) = 0;
    FUN_000842ce(param_1);
    FUN_00084852(param_1);
    if (((*((uint *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x22ef8u + (uint32_t)(iVar2 * 0x1d) * 4u))))))) & 7) == 0) {
      uVar10 = 0;
      (*((uint *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x22f34u + (uint32_t)(iVar2 * 0x1d) * 4u))))))) =
           (uint)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x233b8u + (uint32_t)(iVar1 * 0xd) * 4u)))) & 0xfffffffe;
      (*((uint *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x22f34u + (uint32_t)(iVar2 * 0x1d) * 4u)))) + 4)))) =
           (uint)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x233bcu + (uint32_t)(iVar1 * 0xd) * 4u)))) & 0xfffffffe;
      *(undefined **)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x22f34u + (uint32_t)(iVar2 * 0x1d) * 4u)))) = ((void *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x233b8u + (uint32_t)(iVar1 * 0xd) * 4u)))))));
      *(undefined **)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x22f34u + (uint32_t)(iVar2 * 0x1d) * 4u)))) + 4) = ((void *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x233bcu + (uint32_t)(iVar1 * 0xd) * 4u)))))));
    }
  }
  return uVar10;
}



undefined4 FUN_00084a5e(undefined1 param_1)

{
  uint32_t puVar1;
  undefined4 uVar2;
  
  puVar1 = 0x23dfcu;
  uVar2 = 2;
  if (((*((uint *)camry_host_ptr((uint32_t)(PTR_GSTS_00023044)))) & 0xf) == 1) {
    FUN_0008483e();
  }
  if ((**(uint **)(puVar1 + -0xdb8) & 0xf) == 0) {
    uVar2 = FUN_0008488c(param_1);
  }
  return uVar2;
}



undefined4 FUN_00084a92(uint param_1)

{
  int iVar1;
  int iVar2;
  int iVar3;
  short sVar4;
  undefined4 uVar5;
  
  sVar4 = (short)(param_1 & 0xff);
  iVar1 = (int)sVar4;
  iVar2 = (int)sVar4;
  (*((uint *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x22f34u + (uint32_t)(iVar1 * 0x1d) * 4u))))))) = (uint)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x233b8u + (uint32_t)(iVar2 * 0xd) * 4u)))) & 0xfffffffe;
  (*((uint *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x22f34u + (uint32_t)(iVar1 * 0x1d) * 4u)))) + 4)))) =
       (uint)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x233bcu + (uint32_t)(iVar2 * 0xd) * 4u)))) & 0xfffffffe;
  (*((uint *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x22f34u + (uint32_t)(iVar1 * 0x1d) * 4u)))) + 8)))) = (*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x233c0u + (uint32_t)(iVar2 * 0xd) * 4u)))) & 0xfffffffe;
  (*((uint *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x22f34u + (uint32_t)(iVar1 * 0x1d) * 4u))))))) = (uint)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x233b8u + (uint32_t)(iVar2 * 0xd) * 4u)))) & 0xfffffff8;
  (*((uint *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x22f34u + (uint32_t)(iVar1 * 0x1d) * 4u)))) + 4)))) =
       (uint)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x233bcu + (uint32_t)(iVar2 * 0xd) * 4u)))) & 0xfffffff8;
  (*((uint *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x22f34u + (uint32_t)(iVar1 * 0x1d) * 4u)))) + 8)))) = (*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x233c0u + (uint32_t)(iVar2 * 0xd) * 4u)))) & 0xfffffff8;
  (*((undefined4 *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x22f2cu + (uint32_t)(iVar1 * 0x1d) * 4u))))))) = 1;
  (*((undefined4 *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x22f2cu + (uint32_t)(iVar1 * 0x1d) * 4u)))) + 4)))) = 1;
  (*((undefined4 *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x22f2cu + (uint32_t)(iVar1 * 0x1d) * 4u)))) + 8)))) = 1;
  iVar3 = (param_1 & 0xff) * 4;
  (*((uint *)camry_host_ptr((uint32_t)(PTR_DAT_00023060 + iVar3)))) = (*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x233d8u + (uint32_t)(iVar2 * 0xd) * 4u)))) & 0xfffffffe;
  (*((uint *)camry_host_ptr((uint32_t)(PTR_DAT_00023060 + iVar3)))) = (*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x233d8u + (uint32_t)(iVar2 * 0xd) * 4u)))) & 0xfffffffc;
  (*((undefined4 *)camry_host_ptr((uint32_t)(PTR_DAT_00023064 + iVar3)))) = 1;
  uVar5 = 2;
  FUN_00084420((uint)(byte)param_1);
  if (((*((uint *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x22ef8u + (uint32_t)(iVar1 * 0x1d) * 4u))))))) & 7) == 1) {
    uVar5 = 0;
    (*((undefined2 *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x22edcu + (uint32_t)(iVar1 * 0x1d) * 4u))))))) = 0;
    (*((undefined4 *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x22f14u + (uint32_t)(iVar1 * 0x1d) * 4u))))))) = 0;
    (*((undefined4 *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x22f20u + (uint32_t)(iVar1 * 0x1d) * 4u))))))) = 0;
  }
  return uVar5;
}



undefined4 FUN_00084b74(uint param_1)

{
  int iVar1;
  uint32_t puVar2;
  undefined4 uVar3;
  short sVar4;
  
  puVar2 = 0x23dfcu;
  param_1 = param_1 & 0xff;
  sVar4 = (short)param_1;
  iVar1 = (int)sVar4;
  if (((*((uint *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x22ef8u + (uint32_t)(iVar1 * 0x1d) * 4u))))))) & 7) == 0) {
    FUN_0008569a(param_1);
    if ((((((*((ushort *)camry_host_ptr((uint32_t)(puVar2 + param_1 * 4 + -0xf3e)))) | (*((ushort *)camry_host_ptr((uint32_t)(puVar2 + param_1 * 4 + -0xf40)))))
          & (*((ushort *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x22ee0u + (uint32_t)(iVar1 * 0x1d) * 4u)))))))) != 0) ||
        (((*((uint *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x22f2cu + (uint32_t)(iVar1 * 0x1d) * 4u))))))) & 1) == 0)) ||
       (((*((uint *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x22f2cu + (uint32_t)(iVar1 * 0x1d) * 4u)))) + 4)))) & 1) == 0)) {
      (*((uint *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x22f34u + (uint32_t)(iVar1 * 0x1d) * 4u)))) + 8)))) =
           (*((uint *)camry_host_ptr((uint32_t)(puVar2 + sVar4 * 0x34 + -0xa3c)))) & 0xfffffffe;
      (*((uint *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x22f34u + (uint32_t)(iVar1 * 0x1d) * 4u)))) + 8)))) =
           (*((uint *)camry_host_ptr((uint32_t)(puVar2 + sVar4 * 0x34 + -0xa3c)))) & 0xfffffffc;
      (*((undefined4 *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x22f2cu + (uint32_t)(iVar1 * 0x1d) * 4u)))) + 8)))) = 1;
      iVar1 = param_1 * 4;
      (*((uint *)camry_host_ptr((uint32_t)(*(int *)(puVar2 + -0xd9c) + iVar1)))) =
           (*((uint *)camry_host_ptr((uint32_t)(puVar2 + sVar4 * 0x34 + -0xa24)))) & 0xfffffffe;
      (*((uint *)camry_host_ptr((uint32_t)(*(int *)(puVar2 + -0xd9c) + iVar1)))) =
           (*((uint *)camry_host_ptr((uint32_t)(puVar2 + sVar4 * 0x34 + -0xa24)))) & 0xfffffffc;
      (*((undefined4 *)camry_host_ptr((uint32_t)(iVar1 + *(int *)(puVar2 + -0xd98))))) = 1;
      return 2;
    }
  }
  uVar3 = FUN_00084a92(param_1);
  return uVar3;
}



bool FUN_00084c2c(ushort param_1)

{
  int iVar1;
  int iVar2;
  byte bVar3;
  ushort uVar4;
  uint uVar5;
  bool bVar6;
  uint uVar7;
  short sVar8;
  
  param_1 = param_1 & 0xff;
  iVar1 = (int)(short)param_1;
  iVar2 = (int)(short)param_1;
  bVar6 = false;
  if ((((((((*((uint *)camry_host_ptr((uint32_t)(PTR_DAT_00023038)))) & 1) != 0) &&
         (((DAT_00022e80 ^ (*((uint *)camry_host_ptr((uint32_t)(PTR_GCFG_0002303c))))) & 0x3f) == 0)) &&
        (((*((uint *)camry_host_ptr((uint32_t)(PTR_GCTR_00023040)))) & 0xf07) == 0)) &&
       (((((*((uint *)camry_host_ptr((uint32_t)(PTR_DAT_00023058)))) & 0x3ff) == 0 && (((*((uint *)camry_host_ptr((uint32_t)(PTR_DAT_00023050)))) >> 8 & 1) == 0))
        && (((((uint)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x233b8u + (uint32_t)(iVar2 * 0xd) * 4u)))) ^ (*((uint *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x22f34u + (uint32_t)(iVar1 * 0x1d) * 4u))))))))
             & 0xf3f770) == 0 &&
            (((((uint)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x233bcu + (uint32_t)(iVar2 * 0xd) * 4u)))) ^
               (*((uint *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x22f34u + (uint32_t)(iVar1 * 0x1d) * 4u)))) + 4))))) & 0xf3f770) == 0 &&
             ((((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x233c0u + (uint32_t)(iVar2 * 0xd) * 4u)))) ^ (*((uint *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x22f34u + (uint32_t)(iVar1 * 0x1d) * 4u)))) + 8))))) &
              0xf3f770) == 0)))))))) && (((*((uint *)camry_host_ptr((uint32_t)(PTR_DAT_00023088)))) & 0xff) == 0)) &&
     ((((((*((uint *)camry_host_ptr((uint32_t)(PTR_DAT_0002308c)))) & 5) == 0 &&
        (((DAT_00022e84 ^ (*((uint *)camry_host_ptr((uint32_t)(PTR_DAT_00023090))))) & 1) == 0)) &&
       (((*((uint *)camry_host_ptr((uint32_t)(PTR_DAT_00023094)))) & 1) == 0)) && (((*((uint *)camry_host_ptr((uint32_t)(PTR_DAT_0002309c)))) & 0xffff) == 0)))) {
    uVar7 = (uint)DAT_00022ea4;
    uVar5 = 0;
    while ((uVar5 < uVar7 && (bVar6 == false))) {
      sVar8 = (short)uVar5;
      iVar1 = uVar5 * 4;
      uVar5 = uVar5 + 1 & 0xff;
      bVar6 = (((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x233d8u + (uint32_t)(sVar8 * 0xd) * 4u)))) ^ (*((uint *)camry_host_ptr((uint32_t)(PTR_DAT_00023060 + iVar1))))) & 0xf770) != 0;
    }
    while( true ) {
      if (bVar6 != false) {
        return bVar6;
      }
      if (7 < uVar7) break;
      bVar6 = (*((int *)camry_host_ptr((uint32_t)(PTR_DAT_00023060 + uVar7 * 4)))) != 0;
      uVar7 = uVar7 + 1 & 0xff;
    }
    bVar6 = (*((int *)camry_host_ptr((uint32_t)(PTR_DAT_00023054)))) != DAT_00022e7c;
    bVar3 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x22ecau + (uint32_t)((short)param_1 * 6) * 1u))));
    uVar4 = *(ushort *)(((undefined *)camry_host_ptr(0x22ec8u)) + (short)param_1 * 6);
    uVar5 = (uint)*(ushort *)(((undefined *)camry_host_ptr(0x22ec8u)) + (short)param_1 * 6);
    while ((uVar5 < (ushort)(bVar3 + uVar4) && (bVar6 == false))) {
      (*((uint *)camry_host_ptr((uint32_t)(PTR_DAT_00023050)))) = uVar5 >> 4 & 0x1f;
      iVar1 = uVar5 * 0x10;
      iVar2 = (uVar5 & 0xf) * 0x10;
      if (((*((int *)camry_host_ptr((uint32_t)(PTR_DAT_000230a4 + iVar2)))) != *(int *)(((undefined *)camry_host_ptr(0x230b8u)) + iVar1)) ||
         ((((*((int *)camry_host_ptr((uint32_t)(PTR_DAT_000230a4 + iVar2 + 4)))) !=
            *(int *)(((undefined *)camry_host_ptr(0x22e68u)) + (uint)(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x230c4u + (uint32_t)(iVar1) * 1u)))) * 4) ||
           ((*((int *)camry_host_ptr((uint32_t)(PTR_DAT_000230a4 + iVar2 + 8)))) != *(int *)(((undefined *)camry_host_ptr(0x230bcu)) + iVar1))) ||
          ((*((int *)camry_host_ptr((uint32_t)(PTR_DAT_000230a4 + iVar2 + 0xc)))) != *(int *)(((undefined *)camry_host_ptr(0x230c0u)) + iVar1))))) {
        bVar6 = true;
      }
      uVar5 = uVar5 + 1 & 0xffff;
    }
    return bVar6;
  }
  return true;
}



undefined4 FUN_00084e16(void)

{
  uint32_t puVar1;
  undefined4 uVar2;
  
  puVar1 = 0x23dfcu;
  uVar2 = 2;
  (*((undefined4 *)camry_host_ptr((uint32_t)(PTR_DAT_0002309c)))) = 0;
  FUN_000842fe();
  if ((**(uint **)(puVar1 + -0xdb8) & 0xf) == 1) {
    FUN_00084570();
    FUN_000847a4();
    uVar2 = 0;
  }
  return uVar2;
}



undefined4 FUN_00084e44(byte param_1)

{
  byte bVar1;
  uint32_t puVar2;
  int iVar3;
  undefined4 uVar4;
  byte bVar5;
  
  puVar2 = 0x23dfcu;
  iVar3 = FUN_00084c2c((uint)(byte)param_1);
  if (iVar3 != 0) {
    bVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0xf58)))));
    for (bVar5 = 0; bVar5 < bVar1; bVar5 = bVar5 + 1) {
      if (bVar5 != param_1) {
        FUN_000842a0(bVar5);
        FUN_00083cd6(bVar5);
      }
    }
    iVar3 = FUN_00084e16();
    if (iVar3 != 0) {
      return 2;
    }
  }
  uVar4 = FUN_00084de6(param_1);
  return uVar4;
}



undefined4 FUN_00084e8c(undefined1 param_1)

{
  uint32_t puVar1;
  undefined4 uVar2;
  
  puVar1 = 0x23dfcu;
  uVar2 = 2;
  if (((*((uint *)camry_host_ptr((uint32_t)(PTR_GSTS_00023044)))) & 0xf) == 1) {
    FUN_0008483e();
  }
  if ((**(uint **)(puVar1 + -0xdb8) & 0xf) == 0) {
    uVar2 = FUN_0008488c(param_1);
  }
  return uVar2;
}



undefined4 FUN_00084ec0(uint param_1)

{
  int iVar1;
  int iVar2;
  undefined4 uVar3;
  
  iVar2 = (param_1 & 0xff) * 4;
  uVar3 = 2;
  iVar1 = (int)(short)(param_1 & 0xff);
  if (((((*((ushort *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x22ee0u + (uint32_t)(iVar1 * 0x1d) * 4u))))))) &
        (*(ushort *)(((undefined *)camry_host_ptr(0x22ebeu)) + iVar2) | *(ushort *)(((undefined *)camry_host_ptr(0x22ebcu)) + iVar2))) == 0) &&
      (((*((uint *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x22f2cu + (uint32_t)(iVar1 * 0x1d) * 4u))))))) & 1) != 0)) &&
     (((*((uint *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x22f2cu + (uint32_t)(iVar1 * 0x1d) * 4u)))) + 4)))) & 1) != 0)) {
    uVar3 = FUN_00084a92((uint)(byte)param_1);
  }
  return uVar3;
}



undefined4 FUN_00084f06(byte param_1)

{
  byte bVar1;
  int iVar2;
  undefined4 uVar3;
  byte bVar4;
  
  bVar1 = DAT_00022ea4;
  uVar3 = 2;
  for (bVar4 = 0; bVar4 < bVar1; bVar4 = bVar4 + 1) {
    if (bVar4 != param_1) {
      FUN_000842a0(bVar4);
      FUN_00083cd6(bVar4);
    }
  }
  iVar2 = FUN_00084e16();
  if (iVar2 == 0) {
    uVar3 = FUN_00084de6(param_1);
  }
  return uVar3;
}



void FUN_00084f46(void)

{
  int iVar1;
  uint uVar2;
  
  (*((undefined4 *)camry_host_ptr((uint32_t)(PTR_GCTR_00023040)))) = 0x10001;
  uVar2 = 0;
  do {
    iVar1 = uVar2 * 4;
    uVar2 = uVar2 + 1;
    (*((undefined4 *)camry_host_ptr((uint32_t)(PTR_DAT_00023060 + iVar1)))) = 0;
  } while (uVar2 < 8);
  return;
}



void FUN_00084f68(void)

{
  ushort uVar1;
  uint uVar2;
  
  uVar2 = 1;
  *(undefined **)PTR_GCTR_00023040 = ((undefined *)camry_host_ptr(0x10005u));
  uVar1 = 0;
  do {
    if ((uVar2 & 0xf) == 5) {
      return;
    }
    uVar1 = uVar1 + 1;
    uVar2 = (*((uint *)camry_host_ptr((uint32_t)(PTR_GSTS_00023044))));
  } while (uVar1 < 3);
  return;
}



void FUN_00084f90(void)

{
  byte bVar1;
  undefined8 uVar2;
  ushort uVar3;
  
  uVar2 = 0x23dfc00000000;
  if (((((*((uint *)camry_host_ptr((uint32_t)(PTR_GSTS_00023044)))) >> 3 & 1) == 0) && (((*((uint *)camry_host_ptr((uint32_t)(PTR_GSTS_00023044)))) & 0xf) != 5)) &&
     (FUN_000842fe(), (**(uint **)((int)((ulonglong)uVar2 >> 0x20) + -0xdb8) & 0xf) == 1)) {
    FUN_00084f46();
    bVar1 = (*((byte *)camry_host_ptr((uint32_t)((int)((ulonglong)uVar2 >> 0x20) + -0xf58))));
    for (uVar3 = 0; uVar3 < bVar1; uVar3 = uVar3 + 1 & 0xff) {
      if ((*((char *)camry_host_ptr((uint32_t)((short)uVar3 * 6 + (int)((ulonglong)uVar2 >> 0x20) + -0xf31)))) == '\0') {
        FUN_00084a92(uVar3);
      }
    }
    FUN_00084f68();
  }
  return;
}



void FUN_00084fea(void)

{
  if ((((*((uint *)camry_host_ptr((uint32_t)(PTR_GSTS_00023044)))) & 0xf) == 1) && ((*((int *)camry_host_ptr((uint32_t)(PTR_DAT_00023054)))) != DAT_00022e7c)) {
    FUN_000847a4();
  }
  return;
}


undefined4 FUN_00085012(uint param_1,uint param_2)

{
  undefined4 *puVar1;
  int iVar2;
  uint uVar3;
  short sVar4;
  undefined1 uVar5;
  int iVar6;
  uint *puVar7;
  
  if ((param_2 & 0xffff) < (uint)(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(PTR_DAT_00022e74))))) {
    sVar4 = (short)(param_1 & 0xff);
    iVar2 = (int)sVar4;
    puVar1 = ((undefined4 *)camry_host_ptr((uint32_t)(PTR_DAT_00022e70 + (param_2 & 0xffff) * 0x14)));
    (*((undefined4 *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x22ef0u + (uint32_t)(iVar2 * 0x1d) * 4u))))))) = *puVar1;
    (*((undefined4 *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x22f00u + (uint32_t)(iVar2 * 0x1d) * 4u))))))) = puVar1[1];
    iVar6 = sVar4 * 0x34;
    if (puVar1[3] == 0) {
      puVar7 = ((uint *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x22f04u + (uint32_t)(iVar2 * 0x1d) * 4u))))));
      uVar3 = puVar1[2] & 0x7f0000 | *(uint *)(((undefined *)camry_host_ptr(0x233e0u)) + iVar6) & 0xff80fdff | 0x200;
      uVar5 = 0x3c;
    }
    else {
      puVar7 = ((uint *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x22f04u + (uint32_t)(iVar2 * 0x1d) * 4u))))));
      uVar5 = 0x5a;
      uVar3 = *(uint *)(((undefined *)camry_host_ptr(0x233e0u)) + iVar6) & 0xff80fdff;
    }
    *puVar7 = uVar3;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe5026u + (uint32_t)(param_1 & 0xff) * 1u)))) = uVar5;
    return 0;
  }
  return 2;
}





void FUN_0008509a(void)

{
  ushort uVar1;
  uint uVar2;
  
  uVar2 = 1;
  (*((undefined4 *)camry_host_ptr((uint32_t)(PTR_GCTR_00023040)))) = 0x10002;
  uVar1 = 0;
  do {
    if ((uVar2 & 0xf) == 2) {
      return;
    }
    uVar1 = uVar1 + 1;
    uVar2 = (*((uint *)camry_host_ptr((uint32_t)(PTR_GSTS_00023044))));
  } while (uVar1 < 10);
  return;
}



void FUN_000850c2(void)

{
  uint uVar1;
  uint uVar2;
  
  uVar2 = (uint)DAT_00022e3e;
  for (uVar1 = 0; uVar1 < uVar2; uVar1 = uVar1 + 1 & 0xffff) {
    *(undefined2 *)(((undefined *)camry_host_ptr(0xfebe502au)) + uVar1 * 2) = 0xffff;
  }
  return;
}



void FUN_000850e0(uint param_1)

{
  uint uVar1;
  int iVar2;
  uint uVar3;
  
  iVar2 = (param_1 & 0xff) * 8;
  uVar3 = (uint)*(ushort *)(((undefined *)camry_host_ptr(0x22e44u)) + iVar2) - (uint)DAT_00022e3c & 0xffff;
  uVar1 = (byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x22e48u + (uint32_t)(iVar2) * 1u)))) + uVar3;
  for (; uVar3 < (uVar1 & 0xffff); uVar3 = uVar3 + 1 & 0xffff) {
    *(undefined2 *)(((undefined *)camry_host_ptr(0xfebe502au)) + uVar3 * 2) = 0xffff;
  }
  return;
}



/* Require physical-channel initialization sentinel; choose classic853AA or FD8549E by raw-ID bit30.
   Subsequent CFDTMC request store is not proof of bus delivery. */

uint f33_driver_admit_can_tx(ushort driver_handle,F33CanDriverPdu *pdu)

{
  byte *pbVar1;
  undefined8 uVar2;
  undefined4 uVar3;
  uint uVar4;
  uint uVar5;
  uchar *local_28;
  uint uStack_24;
  byte bStack_20;
  
  uVar2 = 0x23dfcfebeb800;
  uVar4 = 1;
  pbVar1 = ((void *)camry_host_ptr((uint32_t)(PTR_DAT_00022e38 + (uint)driver_handle * 2)));
  uVar5 = (uint)*pbVar1;
  if (f33_driver_channel_software_states[uVar5] == running_software_state) {
    uVar3 = FUN_0007a2da();
    local_28 = ((void *)camry_host_ptr((uint32_t)(pdu->data)));
    uStack_24 = pdu->raw_id;
    bStack_20 = pdu->length;
    if ((uStack_24 >> 0x1e & 1) == 0) {
      if (0xf < bStack_20) {
        bStack_20 = 0xf;
      }
      uVar4 = FUN_000853aa(uVar5,pbVar1[1],&local_28);
    }
    else {
      if (0x40 < bStack_20) {
        bStack_20 = 0x40;
      }
      uVar4 = FUN_0008549e(uVar5,pbVar1[1],&local_28);
    }
    if (uVar4 == 0) {
      (*((ushort *)camry_host_ptr((uint32_t)(((uint)driver_handle - (uint)*(ushort *)((int)((ulonglong)uVar2 >> 0x20) + -0xfc0) & 0xffff)
        * 2 + (int)uVar2 + -0x67d6)))) = pdu->confirmation_handle;
    }
    else if (uVar4 != 2) {
      uVar4 = 1;
    }
    ((void)(uVar3), thunk_FUN_0006a4c4());
  }
  return uVar4;
}



void FUN_000851b8(void)

{
  undefined8 uVar1;
  uint uVar2;
  uint uVar3;
  
  uVar1 = 0x23dfcfebeb800;
  uVar2 = (uint)DAT_00022e41;
  for (uVar3 = 0; uVar3 < uVar2; uVar3 = uVar3 + 1 & 0xff) {
    if ((*((short *)camry_host_ptr((uint32_t)(uVar3 * 2 + (int)uVar1 + -0x67e0)))) == 0x57a8) {
      FUN_00085714(uVar3,1);
      FUN_0008584c(uVar3);
    }
  }
  return;
}



void FUN_00085240(uint param_1,ushort param_2)

{
  int iVar1;
  ushort controller_route;
  ushort uVar2;
  
  param_2 = param_2 & 0xff;
  iVar1 = (param_1 & 0xff) * 8;
  uVar2 = (ushort)(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x22e4au + (uint32_t)(iVar1) * 1u))));
  if ((uVar2 <= param_2) && (param_2 < ((byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x22e48u + (uint32_t)(iVar1) * 1u)))) + uVar2 & 0xff))) {
    controller_route =
         *(ushort *)
          (((undefined *)camry_host_ptr(0xfebe502au)) +
          (uint)(ushort)((*(short *)(((undefined *)camry_host_ptr(0x22e44u)) + iVar1) + (param_2 - uVar2)) - DAT_00022e3c) * 2
          );
    *(ushort *)
     (((undefined *)camry_host_ptr(0xfebe502au)) +
     (uint)(ushort)((*(short *)(((undefined *)camry_host_ptr(0x22e44u)) + iVar1) + (param_2 - uVar2)) - DAT_00022e3c) * 2) =
         0xffff;
    f33_complete_queued_can_tx(controller_route);
  }
  return;
}



undefined4 FUN_00085286(uint param_1,uint param_2,uint param_3,int *param_4)

{
  int *piVar1;
  int iVar2;
  uint uVar3;
  
  param_2 = param_2 & 0xff;
  iVar2 = (int)(short)(param_1 & 0xff);
  if ((param_3 & 0xff) <= (uint)(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x22e9cu + (uint32_t)(param_2 + (param_1 & 0xff) * 2) * 1u))))) {
    piVar1 = ((int *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x22f40u + (uint32_t)(iVar2 * 0x1d) * 4u)))) + param_2 * 0x80)));
    *piVar1 = param_4[1];
    piVar1[1] = (uint)*(byte *)(param_4 + 3) << 0x1c;
    piVar1[2] = param_4[2];
    for (uVar3 = 0; uVar3 < (param_3 & 0xff); uVar3 = uVar3 + 1 & 0xff) {
      piVar1[uVar3 + 3] = (*((int *)camry_host_ptr((uint32_t)(uVar3 * 4 + *param_4))));
    }
    (*((undefined4 *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x22f38u + (uint32_t)(iVar2 * 0x1d) * 4u)))) + param_2 * 4)))) = 0xff;
    return 0;
  }
  return 1;
}



void FUN_00085800(ushort param_1)

{
  int iVar1;
  
  param_1 = param_1 & 0xff;
  if (((*((uint *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x22ef8u + (uint32_t)((short)param_1 * 0x1d) * 4u))))))) & 7) == 0) {
    iVar1 = FUN_00085714(param_1,0);
    if (iVar1 != 0) {
      FUN_00083b14(param_1);
    }
  }
  else {
    FUN_00083a34((uint)(byte)param_1);
  }
  FUN_00085938();
  return;
}



void FUN_0008583e(void)

{
  FUN_00085800(1);
  return;
}



void FUN_00085938(void)

{
  __synchronize();
  return;
}



undefined4 FUN_00085940(undefined4 param_1,char param_2,undefined4 param_3)

{
  undefined4 uVar1;
  
  if (param_2 == '\x10') {
    uVar1 = FUN_00087b74(param_1,0x10,((undefined *)camry_host_ptr(0x234dcu)),0x10,param_3);
  }
  else {
    uVar1 = 0xff;
  }
  return uVar1;
}



undefined4 FUN_00085964(undefined4 param_1,undefined4 param_2)

{
  return FUN_00087c40(((undefined *)camry_host_ptr(0x234dcu)), ((uint *)camry_host_ptr((uint32_t)(param_1))), 0x10, param_2);
}



undefined4 FUN_0008597c(undefined4 param_1,char param_2,int param_3)

{
  undefined4 uVar1;
  
  uVar1 = 0xff;
  if (((*((char *)camry_host_ptr((uint32_t)(param_3 + 0xc0)))) == '\x01') && (param_2 == '\x10')) {
    uVar1 = FUN_00087b74(param_1, 0x10, ((undefined4 *)camry_host_ptr((uint32_t)(param_3 + 0xd4))), 0x10, param_3);
  }
  return uVar1;
}



void FUN_000859a8(undefined4 *param_1)

{
  int iVar1;
  undefined4 *puVar2;
  
  *param_1 = 0;
  param_1[1] = 0;
  param_1[2] = 0;
  param_1[3] = 0;
  param_1[4] = 0;
  param_1[5] = 0;
  param_1[6] = 0;
  param_1[7] = 0;
  param_1[8] = 0;
  param_1[9] = 0;
  param_1[10] = 0;
  param_1[0xb] = 0;
  param_1[0xc] = 0;
  param_1[0xd] = 0;
  param_1[0xe] = 0;
  param_1[0xf] = 0;
  param_1[0x10] = 0;
  param_1[0x11] = 0;
  param_1[0x12] = 0;
  param_1[0x13] = 0;
  param_1[0x14] = 0;
  param_1[0x15] = 0;
  param_1[0x16] = 0;
  param_1[0x17] = 0;
  param_1[0x18] = 0;
  param_1[0x19] = 0;
  param_1[0x1a] = 0;
  param_1[0x1b] = 0;
  param_1[0x1c] = 0;
  param_1[0x1d] = 0;
  param_1[0x1e] = 0;
  param_1[0x1f] = 0;
  param_1[0x20] = 0;
  param_1[0x21] = 0;
  param_1[0x22] = 0;
  param_1[0x23] = 0;
  param_1[0x24] = 0;
  param_1[0x25] = 0;
  param_1[0x26] = 0;
  param_1[0x27] = 0;
  param_1[0x28] = 0;
  param_1[0x29] = 0;
  param_1[0x2a] = 0;
  param_1[0x2b] = 0;
  param_1[0x2c] = 0;
  param_1[0x2d] = 0;
  param_1[0x2e] = 0;
  param_1[0x2f] = 0;
  puVar2 = param_1 + 0x30;
  for (iVar1 = 0x24; iVar1 + -0x20 < 0 == (iVar1 < 0 && -1 < iVar1 + -0x20); iVar1 = iVar1 + -0x20)
  {
    *puVar2 = 0;
    puVar2[1] = 0;
    puVar2[2] = 0;
    puVar2[3] = 0;
    puVar2[4] = 0;
    puVar2[5] = 0;
    puVar2[6] = 0;
    puVar2[7] = 0;
    puVar2 = puVar2 + 8;
  }
  for (; iVar1 + -0x10 < 0 == (iVar1 < 0 && -1 < iVar1 + -0x10); iVar1 = iVar1 + -0x10) {
    *puVar2 = 0;
    puVar2[1] = 0;
    puVar2[2] = 0;
    puVar2[3] = 0;
    puVar2 = puVar2 + 4;
  }
  for (; 0 < iVar1; iVar1 = iVar1 + -4) {
    *puVar2 = 0;
    puVar2 = puVar2 + 1;
  }
  *(undefined1 *)(param_1 + 0x30) = 0;
  return;
}



void FUN_00085a5c(uint *param_1)

{
  uint uVar1;
  uint uVar2;
  uint uVar3;
  uint uVar4;
  uint uVar5;
  uint uVar6;
  uint uVar7;
  uint uVar8;
  
  uVar1 = param_1[0x2c];
  uVar7 = param_1[0x2d];
  uVar4 = param_1[0x2e];
  uVar3 = param_1[0x2f];
  param_1[0x2d] = uVar7 ^ param_1[1];
  param_1[0x2c] = uVar1 ^ *param_1;
  param_1[0x2e] = uVar4 ^ param_1[2];
  param_1[0x2f] = uVar3 ^ param_1[3];
  uVar2 = param_1[4] ^
          *(uint *)(((undefined *)camry_host_ptr(0x24100u)) + (uint)(*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 0xbf)))) * 4) ^
          *(uint *)(((undefined *)camry_host_ptr(0x23d00u)) + (uint)(*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 0xba)))) * 4) ^
          *(uint *)(((undefined *)camry_host_ptr(0x23900u)) + (uint)(*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 0xb5)))) * 4) ^
          *(uint *)(((undefined *)camry_host_ptr(0x23500u)) + ((uVar1 ^ *param_1) & 0xff) * 4);
  uVar1 = param_1[5] ^
          *(uint *)(((undefined *)camry_host_ptr(0x24100u)) + (uint)(*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 0xb3)))) * 4) ^
          *(uint *)(((undefined *)camry_host_ptr(0x23d00u)) + (uint)(*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 0xbe)))) * 4) ^
          *(uint *)(((undefined *)camry_host_ptr(0x23900u)) + (uint)(*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 0xb9)))) * 4) ^
          *(uint *)(((undefined *)camry_host_ptr(0x23500u)) + ((uVar7 ^ param_1[1]) & 0xff) * 4);
  uVar5 = param_1[6] ^
          *(uint *)(((undefined *)camry_host_ptr(0x24100u)) + (uint)(*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 0xb7)))) * 4) ^
          *(uint *)(((undefined *)camry_host_ptr(0x23d00u)) + (uint)(*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 0xb2)))) * 4) ^
          *(uint *)(((undefined *)camry_host_ptr(0x23900u)) + (uint)(*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 0xbd)))) * 4) ^
          *(uint *)(((undefined *)camry_host_ptr(0x23500u)) + ((uVar4 ^ param_1[2]) & 0xff) * 4);
  uVar7 = param_1[7] ^
          *(uint *)(((undefined *)camry_host_ptr(0x24100u)) + (uint)(*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 0xbb)))) * 4) ^
          *(uint *)(((undefined *)camry_host_ptr(0x23d00u)) + (uint)(*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 0xb6)))) * 4) ^
          *(uint *)(((undefined *)camry_host_ptr(0x23900u)) + (uint)(*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 0xb1)))) * 4) ^
          *(uint *)(((undefined *)camry_host_ptr(0x23500u)) + ((uVar3 ^ param_1[3]) & 0xff) * 4);
  uVar4 = param_1[8] ^
          *(uint *)(((undefined *)camry_host_ptr(0x24100u)) + (uVar7 >> 0x18) * 4) ^
          *(uint *)(((undefined *)camry_host_ptr(0x23d00u)) + (uVar5 >> 0x10 & 0xff) * 4) ^
          *(uint *)(((undefined *)camry_host_ptr(0x23900u)) + (uVar1 >> 8 & 0xff) * 4) ^
          *(uint *)(((undefined *)camry_host_ptr(0x23500u)) + (uVar2 & 0xff) * 4);
  param_1[0x2c] = uVar4;
  uVar3 = param_1[9] ^
          *(uint *)(((undefined *)camry_host_ptr(0x24100u)) + (uVar2 >> 0x18) * 4) ^
          *(uint *)(((undefined *)camry_host_ptr(0x23d00u)) + (uVar7 >> 0x10 & 0xff) * 4) ^
          *(uint *)(((undefined *)camry_host_ptr(0x23900u)) + (uVar5 >> 8 & 0xff) * 4) ^
          *(uint *)(((undefined *)camry_host_ptr(0x23500u)) + (uVar1 & 0xff) * 4);
  param_1[0x2d] = uVar3;
  uVar6 = param_1[10] ^
          *(uint *)(((undefined *)camry_host_ptr(0x24100u)) + (uVar1 >> 0x18) * 4) ^
          *(uint *)(((undefined *)camry_host_ptr(0x23d00u)) + (uVar2 >> 0x10 & 0xff) * 4) ^
          *(uint *)(((undefined *)camry_host_ptr(0x23900u)) + (uVar7 >> 8 & 0xff) * 4) ^
          *(uint *)(((undefined *)camry_host_ptr(0x23500u)) + (uVar5 & 0xff) * 4);
  param_1[0x2e] = uVar6;
  uVar7 = param_1[0xb] ^
          *(uint *)(((undefined *)camry_host_ptr(0x24100u)) + (uVar5 >> 0x18) * 4) ^
          *(uint *)(((undefined *)camry_host_ptr(0x23d00u)) + (uVar1 >> 0x10 & 0xff) * 4) ^
          *(uint *)(((undefined *)camry_host_ptr(0x23900u)) + (uVar2 >> 8 & 0xff) * 4) ^
          *(uint *)(((undefined *)camry_host_ptr(0x23500u)) + (uVar7 & 0xff) * 4);
  param_1[0x2f] = uVar7;
  uVar2 = param_1[0xc] ^
          *(uint *)(((undefined *)camry_host_ptr(0x24100u)) + (uint)(*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 0xbf)))) * 4) ^
          *(uint *)(((undefined *)camry_host_ptr(0x23d00u)) + (uint)(*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 0xba)))) * 4) ^
          *(uint *)(((undefined *)camry_host_ptr(0x23900u)) + (uint)(*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 0xb5)))) * 4) ^
          *(uint *)(((undefined *)camry_host_ptr(0x23500u)) + (uVar4 & 0xff) * 4);
  uVar1 = param_1[0xd] ^
          *(uint *)(((undefined *)camry_host_ptr(0x24100u)) + (uint)(*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 0xb3)))) * 4) ^
          *(uint *)(((undefined *)camry_host_ptr(0x23d00u)) + (uint)(*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 0xbe)))) * 4) ^
          *(uint *)(((undefined *)camry_host_ptr(0x23900u)) + (uint)(*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 0xb9)))) * 4) ^
          *(uint *)(((undefined *)camry_host_ptr(0x23500u)) + (uVar3 & 0xff) * 4);
  uVar5 = param_1[0xe] ^
          *(uint *)(((undefined *)camry_host_ptr(0x24100u)) + (uint)(*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 0xb7)))) * 4) ^
          *(uint *)(((undefined *)camry_host_ptr(0x23d00u)) + (uint)(*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 0xb2)))) * 4) ^
          *(uint *)(((undefined *)camry_host_ptr(0x23900u)) + (uint)(*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 0xbd)))) * 4) ^
          *(uint *)(((undefined *)camry_host_ptr(0x23500u)) + (uVar6 & 0xff) * 4);
  uVar7 = param_1[0xf] ^
          *(uint *)(((undefined *)camry_host_ptr(0x24100u)) + (uint)(*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 0xbb)))) * 4) ^
          *(uint *)(((undefined *)camry_host_ptr(0x23d00u)) + (uint)(*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 0xb6)))) * 4) ^
          *(uint *)(((undefined *)camry_host_ptr(0x23900u)) + (uint)(*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 0xb1)))) * 4) ^
          *(uint *)(((undefined *)camry_host_ptr(0x23500u)) + (uVar7 & 0xff) * 4);
  uVar4 = param_1[0x10] ^
          *(uint *)(((undefined *)camry_host_ptr(0x24100u)) + (uVar7 >> 0x18) * 4) ^
          *(uint *)(((undefined *)camry_host_ptr(0x23d00u)) + (uVar5 >> 0x10 & 0xff) * 4) ^
          *(uint *)(((undefined *)camry_host_ptr(0x23900u)) + (uVar1 >> 8 & 0xff) * 4) ^
          *(uint *)(((undefined *)camry_host_ptr(0x23500u)) + (uVar2 & 0xff) * 4);
  param_1[0x2c] = uVar4;
  uVar3 = param_1[0x11] ^
          *(uint *)(((undefined *)camry_host_ptr(0x24100u)) + (uVar2 >> 0x18) * 4) ^
          *(uint *)(((undefined *)camry_host_ptr(0x23d00u)) + (uVar7 >> 0x10 & 0xff) * 4) ^
          *(uint *)(((undefined *)camry_host_ptr(0x23900u)) + (uVar5 >> 8 & 0xff) * 4) ^
          *(uint *)(((undefined *)camry_host_ptr(0x23500u)) + (uVar1 & 0xff) * 4);
  param_1[0x2d] = uVar3;
  uVar6 = param_1[0x12] ^
          *(uint *)(((undefined *)camry_host_ptr(0x24100u)) + (uVar1 >> 0x18) * 4) ^
          *(uint *)(((undefined *)camry_host_ptr(0x23d00u)) + (uVar2 >> 0x10 & 0xff) * 4) ^
          *(uint *)(((undefined *)camry_host_ptr(0x23900u)) + (uVar7 >> 8 & 0xff) * 4) ^
          *(uint *)(((undefined *)camry_host_ptr(0x23500u)) + (uVar5 & 0xff) * 4);
  param_1[0x2e] = uVar6;
  uVar7 = param_1[0x13] ^
          *(uint *)(((undefined *)camry_host_ptr(0x24100u)) + (uVar5 >> 0x18) * 4) ^
          *(uint *)(((undefined *)camry_host_ptr(0x23d00u)) + (uVar1 >> 0x10 & 0xff) * 4) ^
          *(uint *)(((undefined *)camry_host_ptr(0x23900u)) + (uVar2 >> 8 & 0xff) * 4) ^
          *(uint *)(((undefined *)camry_host_ptr(0x23500u)) + (uVar7 & 0xff) * 4);
  param_1[0x2f] = uVar7;
  uVar2 = param_1[0x14] ^
          *(uint *)(((undefined *)camry_host_ptr(0x24100u)) + (uint)(*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 0xbf)))) * 4) ^
          *(uint *)(((undefined *)camry_host_ptr(0x23d00u)) + (uint)(*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 0xba)))) * 4) ^
          *(uint *)(((undefined *)camry_host_ptr(0x23900u)) + (uint)(*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 0xb5)))) * 4) ^
          *(uint *)(((undefined *)camry_host_ptr(0x23500u)) + (uVar4 & 0xff) * 4);
  uVar1 = param_1[0x15] ^
          *(uint *)(((undefined *)camry_host_ptr(0x24100u)) + (uint)(*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 0xb3)))) * 4) ^
          *(uint *)(((undefined *)camry_host_ptr(0x23d00u)) + (uint)(*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 0xbe)))) * 4) ^
          *(uint *)(((undefined *)camry_host_ptr(0x23900u)) + (uint)(*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 0xb9)))) * 4) ^
          *(uint *)(((undefined *)camry_host_ptr(0x23500u)) + (uVar3 & 0xff) * 4);
  uVar5 = param_1[0x16] ^
          *(uint *)(((undefined *)camry_host_ptr(0x24100u)) + (uint)(*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 0xb7)))) * 4) ^
          *(uint *)(((undefined *)camry_host_ptr(0x23d00u)) + (uint)(*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 0xb2)))) * 4) ^
          *(uint *)(((undefined *)camry_host_ptr(0x23900u)) + (uint)(*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 0xbd)))) * 4) ^
          *(uint *)(((undefined *)camry_host_ptr(0x23500u)) + (uVar6 & 0xff) * 4);
  uVar7 = param_1[0x17] ^
          *(uint *)(((undefined *)camry_host_ptr(0x24100u)) + (uint)(*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 0xbb)))) * 4) ^
          *(uint *)(((undefined *)camry_host_ptr(0x23d00u)) + (uint)(*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 0xb6)))) * 4) ^
          *(uint *)(((undefined *)camry_host_ptr(0x23900u)) + (uint)(*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 0xb1)))) * 4) ^
          *(uint *)(((undefined *)camry_host_ptr(0x23500u)) + (uVar7 & 0xff) * 4);
  uVar4 = param_1[0x18] ^
          *(uint *)(((undefined *)camry_host_ptr(0x24100u)) + (uVar7 >> 0x18) * 4) ^
          *(uint *)(((undefined *)camry_host_ptr(0x23d00u)) + (uVar5 >> 0x10 & 0xff) * 4) ^
          *(uint *)(((undefined *)camry_host_ptr(0x23900u)) + (uVar1 >> 8 & 0xff) * 4) ^
          *(uint *)(((undefined *)camry_host_ptr(0x23500u)) + (uVar2 & 0xff) * 4);
  param_1[0x2c] = uVar4;
  uVar3 = param_1[0x19] ^
          *(uint *)(((undefined *)camry_host_ptr(0x24100u)) + (uVar2 >> 0x18) * 4) ^
          *(uint *)(((undefined *)camry_host_ptr(0x23d00u)) + (uVar7 >> 0x10 & 0xff) * 4) ^
          *(uint *)(((undefined *)camry_host_ptr(0x23900u)) + (uVar5 >> 8 & 0xff) * 4) ^
          *(uint *)(((undefined *)camry_host_ptr(0x23500u)) + (uVar1 & 0xff) * 4);
  param_1[0x2d] = uVar3;
  uVar6 = param_1[0x1a] ^
          *(uint *)(((undefined *)camry_host_ptr(0x24100u)) + (uVar1 >> 0x18) * 4) ^
          *(uint *)(((undefined *)camry_host_ptr(0x23d00u)) + (uVar2 >> 0x10 & 0xff) * 4) ^
          *(uint *)(((undefined *)camry_host_ptr(0x23900u)) + (uVar7 >> 8 & 0xff) * 4) ^
          *(uint *)(((undefined *)camry_host_ptr(0x23500u)) + (uVar5 & 0xff) * 4);
  param_1[0x2e] = uVar6;
  uVar7 = param_1[0x1b] ^
          *(uint *)(((undefined *)camry_host_ptr(0x24100u)) + (uVar5 >> 0x18) * 4) ^
          *(uint *)(((undefined *)camry_host_ptr(0x23d00u)) + (uVar1 >> 0x10 & 0xff) * 4) ^
          *(uint *)(((undefined *)camry_host_ptr(0x23900u)) + (uVar2 >> 8 & 0xff) * 4) ^
          *(uint *)(((undefined *)camry_host_ptr(0x23500u)) + (uVar7 & 0xff) * 4);
  param_1[0x2f] = uVar7;
  uVar2 = param_1[0x1c] ^
          *(uint *)(((undefined *)camry_host_ptr(0x24100u)) + (uint)(*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 0xbf)))) * 4) ^
          *(uint *)(((undefined *)camry_host_ptr(0x23d00u)) + (uint)(*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 0xba)))) * 4) ^
          *(uint *)(((undefined *)camry_host_ptr(0x23900u)) + (uint)(*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 0xb5)))) * 4) ^
          *(uint *)(((undefined *)camry_host_ptr(0x23500u)) + (uVar4 & 0xff) * 4);
  uVar1 = param_1[0x1d] ^
          *(uint *)(((undefined *)camry_host_ptr(0x24100u)) + (uint)(*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 0xb3)))) * 4) ^
          *(uint *)(((undefined *)camry_host_ptr(0x23d00u)) + (uint)(*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 0xbe)))) * 4) ^
          *(uint *)(((undefined *)camry_host_ptr(0x23900u)) + (uint)(*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 0xb9)))) * 4) ^
          *(uint *)(((undefined *)camry_host_ptr(0x23500u)) + (uVar3 & 0xff) * 4);
  uVar5 = param_1[0x1e] ^
          *(uint *)(((undefined *)camry_host_ptr(0x24100u)) + (uint)(*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 0xb7)))) * 4) ^
          *(uint *)(((undefined *)camry_host_ptr(0x23d00u)) + (uint)(*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 0xb2)))) * 4) ^
          *(uint *)(((undefined *)camry_host_ptr(0x23900u)) + (uint)(*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 0xbd)))) * 4) ^
          *(uint *)(((undefined *)camry_host_ptr(0x23500u)) + (uVar6 & 0xff) * 4);
  uVar7 = param_1[0x1f] ^
          *(uint *)(((undefined *)camry_host_ptr(0x24100u)) + (uint)(*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 0xbb)))) * 4) ^
          *(uint *)(((undefined *)camry_host_ptr(0x23d00u)) + (uint)(*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 0xb6)))) * 4) ^
          *(uint *)(((undefined *)camry_host_ptr(0x23900u)) + (uint)(*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 0xb1)))) * 4) ^
          *(uint *)(((undefined *)camry_host_ptr(0x23500u)) + (uVar7 & 0xff) * 4);
  uVar4 = param_1[0x20] ^
          *(uint *)(((undefined *)camry_host_ptr(0x24100u)) + (uVar7 >> 0x18) * 4) ^
          *(uint *)(((undefined *)camry_host_ptr(0x23d00u)) + (uVar5 >> 0x10 & 0xff) * 4) ^
          *(uint *)(((undefined *)camry_host_ptr(0x23900u)) + (uVar1 >> 8 & 0xff) * 4) ^
          *(uint *)(((undefined *)camry_host_ptr(0x23500u)) + (uVar2 & 0xff) * 4);
  param_1[0x2c] = uVar4;
  uVar3 = param_1[0x21] ^
          *(uint *)(((undefined *)camry_host_ptr(0x24100u)) + (uVar2 >> 0x18) * 4) ^
          *(uint *)(((undefined *)camry_host_ptr(0x23d00u)) + (uVar7 >> 0x10 & 0xff) * 4) ^
          *(uint *)(((undefined *)camry_host_ptr(0x23900u)) + (uVar5 >> 8 & 0xff) * 4) ^
          *(uint *)(((undefined *)camry_host_ptr(0x23500u)) + (uVar1 & 0xff) * 4);
  param_1[0x2d] = uVar3;
  uVar6 = param_1[0x22] ^
          *(uint *)(((undefined *)camry_host_ptr(0x24100u)) + (uVar1 >> 0x18) * 4) ^
          *(uint *)(((undefined *)camry_host_ptr(0x23d00u)) + (uVar2 >> 0x10 & 0xff) * 4) ^
          *(uint *)(((undefined *)camry_host_ptr(0x23900u)) + (uVar7 >> 8 & 0xff) * 4) ^
          *(uint *)(((undefined *)camry_host_ptr(0x23500u)) + (uVar5 & 0xff) * 4);
  param_1[0x2e] = uVar6;
  uVar7 = param_1[0x23] ^
          *(uint *)(((undefined *)camry_host_ptr(0x24100u)) + (uVar5 >> 0x18) * 4) ^
          *(uint *)(((undefined *)camry_host_ptr(0x23d00u)) + (uVar1 >> 0x10 & 0xff) * 4) ^
          *(uint *)(((undefined *)camry_host_ptr(0x23900u)) + (uVar2 >> 8 & 0xff) * 4) ^
          *(uint *)(((undefined *)camry_host_ptr(0x23500u)) + (uVar7 & 0xff) * 4);
  param_1[0x2f] = uVar7;
  uVar2 = param_1[0x24] ^
          *(uint *)(((undefined *)camry_host_ptr(0x24100u)) + (uint)(*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 0xbf)))) * 4) ^
          *(uint *)(((undefined *)camry_host_ptr(0x23d00u)) + (uint)(*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 0xba)))) * 4) ^
          *(uint *)(((undefined *)camry_host_ptr(0x23900u)) + (uint)(*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 0xb5)))) * 4) ^
          *(uint *)(((undefined *)camry_host_ptr(0x23500u)) + (uVar4 & 0xff) * 4);
  uVar1 = param_1[0x25] ^
          *(uint *)(((undefined *)camry_host_ptr(0x24100u)) + (uint)(*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 0xb3)))) * 4) ^
          *(uint *)(((undefined *)camry_host_ptr(0x23d00u)) + (uint)(*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 0xbe)))) * 4) ^
          *(uint *)(((undefined *)camry_host_ptr(0x23900u)) + (uint)(*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 0xb9)))) * 4) ^
          *(uint *)(((undefined *)camry_host_ptr(0x23500u)) + (uVar3 & 0xff) * 4);
  uVar8 = *(uint *)(((undefined *)camry_host_ptr(0x23900u)) + (uint)(*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 0xb1)))) * 4);
  uVar7 = *(uint *)(((undefined *)camry_host_ptr(0x23500u)) + (uVar7 & 0xff) * 4);
  uVar5 = *(uint *)(((undefined *)camry_host_ptr(0x23d00u)) + (uint)(*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 0xb6)))) * 4);
  uVar4 = *(uint *)(((undefined *)camry_host_ptr(0x24100u)) + (uint)(*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 0xbb)))) * 4);
  uVar3 = param_1[0x26] ^
          *(uint *)(((undefined *)camry_host_ptr(0x24100u)) + (uint)(*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 0xb7)))) * 4) ^
          *(uint *)(((undefined *)camry_host_ptr(0x23d00u)) + (uint)(*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 0xb2)))) * 4) ^
          *(uint *)(((undefined *)camry_host_ptr(0x23900u)) + (uint)(*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 0xbd)))) * 4) ^
          *(uint *)(((undefined *)camry_host_ptr(0x23500u)) + (uVar6 & 0xff) * 4);
  *(undefined *)(param_1 + 0x2c) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x23d00u + (uint32_t)((uVar2 & 0xff) * 4) * 1u))));
  uVar4 = param_1[0x27] ^ uVar4 ^ uVar5 ^ uVar8 ^ uVar7;
  (*((undefined *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 0xb1)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x23d00u + (uint32_t)((uVar1 >> 8 & 0xff) * 4) * 1u))));
  (*((undefined *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 0xb2)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x23d00u + (uint32_t)((uVar3 >> 0x10 & 0xff) * 4) * 1u))));
  (*((undefined *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 0xb3)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x23d00u + (uint32_t)((uVar4 >> 0x18) * 4) * 1u))));
  *(undefined *)(param_1 + 0x2d) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x23d00u + (uint32_t)((uVar1 & 0xff) * 4) * 1u))));
  (*((undefined *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 0xb5)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x23d00u + (uint32_t)((uVar3 >> 8 & 0xff) * 4) * 1u))));
  (*((undefined *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 0xb6)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x23d00u + (uint32_t)((uVar4 >> 0x10 & 0xff) * 4) * 1u))));
  (*((undefined *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 0xb7)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x23d00u + (uint32_t)((uVar2 >> 0x18) * 4) * 1u))));
  *(undefined *)(param_1 + 0x2e) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x23d00u + (uint32_t)((uVar3 & 0xff) * 4) * 1u))));
  (*((undefined *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 0xb9)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x23d00u + (uint32_t)((uVar4 >> 8 & 0xff) * 4) * 1u))));
  (*((undefined *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 0xba)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x23d00u + (uint32_t)((uVar2 >> 0x10 & 0xff) * 4) * 1u))));
  (*((undefined *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 0xbb)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x23d00u + (uint32_t)((uVar1 >> 0x18) * 4) * 1u))));
  *(undefined *)(param_1 + 0x2f) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x23d00u + (uint32_t)((uVar4 & 0xff) * 4) * 1u))));
  (*((undefined *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 0xbd)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x23d00u + (uint32_t)((uVar2 >> 8 & 0xff) * 4) * 1u))));
  (*((undefined *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 0xbe)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x23d00u + (uint32_t)((uVar1 >> 0x10 & 0xff) * 4) * 1u))));
  (*((undefined *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 0xbf)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x23d00u + (uint32_t)((uVar3 >> 0x18) * 4) * 1u))));
  param_1[0x2c] = param_1[0x2c] ^ param_1[0x28];
  param_1[0x2d] = param_1[0x2d] ^ param_1[0x29];
  param_1[0x2e] = param_1[0x2e] ^ param_1[0x2a];
  param_1[0x2f] = param_1[0x2f] ^ param_1[0x2b];
  return;
}



undefined4 FUN_000863a0(undefined4 *param_1,undefined4 *param_2,char param_3,int param_4)

{
  undefined4 uVar1;
  undefined4 *puVar2;
  
  uVar1 = 0xff;
  if ((param_3 == '\x10') && ((*((char *)camry_host_ptr((uint32_t)(param_4 + 0xc0)))) == '\x01')) {
    puVar2 = ((undefined4 *)camry_host_ptr((uint32_t)(param_4 + 0xb0)));
    if ((((uint)camry_host_addr(puVar2) & 3) == 0) && (((uint)camry_host_addr(param_1) & 3) == 0)) {
      *puVar2 = *param_1;
      (*((undefined4 *)camry_host_ptr((uint32_t)(param_4 + 0xb4)))) = param_1[1];
      (*((undefined4 *)camry_host_ptr((uint32_t)(param_4 + 0xb8)))) = param_1[2];
      (*((undefined4 *)camry_host_ptr((uint32_t)(param_4 + 0xbc)))) = param_1[3];
    }
    else {
      *(undefined1 *)puVar2 = *(undefined1 *)param_1;
      (*((undefined1 *)camry_host_ptr((uint32_t)(param_4 + 0xb1)))) = (*((undefined1 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 1))));
      (*((undefined1 *)camry_host_ptr((uint32_t)(param_4 + 0xb2)))) = (*((undefined1 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 2))));
      (*((undefined1 *)camry_host_ptr((uint32_t)(param_4 + 0xb3)))) = (*((undefined1 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 3))));
      (*((undefined1 *)camry_host_ptr((uint32_t)(param_4 + 0xb4)))) = *(undefined1 *)(param_1 + 1);
      (*((undefined1 *)camry_host_ptr((uint32_t)(param_4 + 0xb5)))) = (*((undefined1 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 5))));
      (*((undefined1 *)camry_host_ptr((uint32_t)(param_4 + 0xb6)))) = (*((undefined1 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 6))));
      (*((undefined1 *)camry_host_ptr((uint32_t)(param_4 + 0xb7)))) = (*((undefined1 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 7))));
      (*((undefined1 *)camry_host_ptr((uint32_t)(param_4 + 0xb8)))) = *(undefined1 *)(param_1 + 2);
      (*((undefined1 *)camry_host_ptr((uint32_t)(param_4 + 0xb9)))) = (*((undefined1 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 9))));
      (*((undefined1 *)camry_host_ptr((uint32_t)(param_4 + 0xba)))) = (*((undefined1 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 10))));
      (*((undefined1 *)camry_host_ptr((uint32_t)(param_4 + 0xbb)))) = (*((undefined1 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 0xb))));
      (*((undefined1 *)camry_host_ptr((uint32_t)(param_4 + 0xbc)))) = *(undefined1 *)(param_1 + 3);
      (*((undefined1 *)camry_host_ptr((uint32_t)(param_4 + 0xbd)))) = (*((undefined1 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 0xd))));
      (*((undefined1 *)camry_host_ptr((uint32_t)(param_4 + 0xbe)))) = (*((undefined1 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 0xe))));
      (*((undefined1 *)camry_host_ptr((uint32_t)(param_4 + 0xbf)))) = (*((undefined1 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 0xf))));
    }
    FUN_00085a5c(((uint *)camry_host_ptr((uint32_t)(param_4))));
    if ((((uint)camry_host_addr(param_2) & 3) == 0) && (((uint)camry_host_addr(puVar2) & 3) == 0)) {
      *param_2 = *puVar2;
      param_2[1] = (*((undefined4 *)camry_host_ptr((uint32_t)(param_4 + 0xb4))));
      param_2[2] = (*((undefined4 *)camry_host_ptr((uint32_t)(param_4 + 0xb8))));
      param_2[3] = (*((undefined4 *)camry_host_ptr((uint32_t)(param_4 + 0xbc))));
    }
    else {
      *(undefined1 *)param_2 = *(undefined1 *)puVar2;
      (*((undefined1 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_2) + 1)))) = (*((undefined1 *)camry_host_ptr((uint32_t)(param_4 + 0xb1))));
      (*((undefined1 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_2) + 2)))) = (*((undefined1 *)camry_host_ptr((uint32_t)(param_4 + 0xb2))));
      (*((undefined1 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_2) + 3)))) = (*((undefined1 *)camry_host_ptr((uint32_t)(param_4 + 0xb3))));
      *(undefined1 *)(param_2 + 1) = (*((undefined1 *)camry_host_ptr((uint32_t)(param_4 + 0xb4))));
      (*((undefined1 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_2) + 5)))) = (*((undefined1 *)camry_host_ptr((uint32_t)(param_4 + 0xb5))));
      (*((undefined1 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_2) + 6)))) = (*((undefined1 *)camry_host_ptr((uint32_t)(param_4 + 0xb6))));
      (*((undefined1 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_2) + 7)))) = (*((undefined1 *)camry_host_ptr((uint32_t)(param_4 + 0xb7))));
      *(undefined1 *)(param_2 + 2) = (*((undefined1 *)camry_host_ptr((uint32_t)(param_4 + 0xb8))));
      (*((undefined1 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_2) + 9)))) = (*((undefined1 *)camry_host_ptr((uint32_t)(param_4 + 0xb9))));
      (*((undefined1 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_2) + 10)))) = (*((undefined1 *)camry_host_ptr((uint32_t)(param_4 + 0xba))));
      (*((undefined1 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_2) + 0xb)))) = (*((undefined1 *)camry_host_ptr((uint32_t)(param_4 + 0xbb))));
      *(undefined1 *)(param_2 + 3) = (*((undefined1 *)camry_host_ptr((uint32_t)(param_4 + 0xbc))));
      (*((undefined1 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_2) + 0xd)))) = (*((undefined1 *)camry_host_ptr((uint32_t)(param_4 + 0xbd))));
      (*((undefined1 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_2) + 0xe)))) = (*((undefined1 *)camry_host_ptr((uint32_t)(param_4 + 0xbe))));
      (*((undefined1 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_2) + 0xf)))) = (*((undefined1 *)camry_host_ptr((uint32_t)(param_4 + 0xbf))));
    }
    uVar1 = 0;
  }
  return uVar1;
}



undefined4 FUN_000876c4(uint *param_1,char param_2,uint *param_3)

{
  uint uVar1;
  uint uVar2;
  uint uVar3;
  uint uVar4;
  uint uVar5;
  
  if (param_2 == '\x10') {
    param_3[0x2c] = 0;
    param_3[0x2d] = 0;
    param_3[0x2e] = 0;
    param_3[0x2f] = 0;
    if ((((uint)camry_host_addr(param_3) & 3) == 0) && (((uint)camry_host_addr(param_1) & 3) == 0)) {
      *param_3 = *param_1;
      param_3[1] = param_1[1];
      param_3[2] = param_1[2];
      param_3[3] = param_1[3];
    }
    else {
      *(char *)param_3 = (char)*param_1;
      (*((undefined1 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_3) + 1)))) = (*((undefined1 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 1))));
      (*((undefined1 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_3) + 2)))) = (*((undefined1 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 2))));
      (*((undefined1 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_3) + 3)))) = (*((undefined1 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 3))));
      *(char *)(param_3 + 1) = (char)param_1[1];
      (*((undefined1 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_3) + 5)))) = (*((undefined1 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 5))));
      (*((undefined1 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_3) + 6)))) = (*((undefined1 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 6))));
      (*((undefined1 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_3) + 7)))) = (*((undefined1 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 7))));
      *(char *)(param_3 + 2) = (char)param_1[2];
      (*((undefined1 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_3) + 9)))) = (*((undefined1 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 9))));
      (*((undefined1 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_3) + 10)))) = (*((undefined1 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 10))));
      (*((undefined1 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_3) + 0xb)))) = (*((undefined1 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 0xb))));
      *(char *)(param_3 + 3) = (char)param_1[3];
      (*((undefined1 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_3) + 0xd)))) = (*((undefined1 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 0xd))));
      (*((undefined1 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_3) + 0xe)))) = (*((undefined1 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 0xe))));
      (*((undefined1 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_3) + 0xf)))) = (*((undefined1 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 0xf))));
    }
    (*((undefined *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_3) + 0x13)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x23d00u + (uint32_t)((uint)(byte)param_3[3] * 4) * 1u))));
    (*((undefined *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_3) + 0x12)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x23d00u + (uint32_t)((uint)(*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_3) + 0xf)))) * 4) * 1u))));
    (*((undefined *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_3) + 0x11)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x23d00u + (uint32_t)((uint)(*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_3) + 0xe)))) * 4) * 1u))));
    *(byte *)(param_3 + 4) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x23d00u + (uint32_t)((uint)(*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_3) + 0xd)))) * 4) * 1u)))) ^ DAT_000234ed
    ;
    uVar5 = param_3[4] ^ *param_3;
    uVar3 = param_3[1] ^ uVar5;
    param_3[4] = uVar5;
    uVar4 = param_3[2] ^ uVar3;
    param_3[5] = uVar3;
    uVar2 = param_3[3] ^ uVar4;
    param_3[6] = uVar4;
    param_3[7] = uVar2;
    (*((undefined *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_3) + 0x23)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x23d00u + (uint32_t)((uVar2 & 0xff) * 4) * 1u))));
    (*((undefined *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_3) + 0x22)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x23d00u + (uint32_t)((uint)(*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_3) + 0x1f)))) * 4) * 1u))));
    (*((undefined *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_3) + 0x21)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x23d00u + (uint32_t)((uint)(*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_3) + 0x1e)))) * 4) * 1u))));
    *(byte *)(param_3 + 8) =
         (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x23d00u + (uint32_t)((uint)(*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_3) + 0x1d)))) * 4) * 1u)))) ^ DAT_000234ee;
    uVar5 = param_3[8] ^ uVar5;
    uVar3 = uVar5 ^ uVar3;
    param_3[8] = uVar5;
    param_3[9] = uVar3;
    uVar4 = uVar3 ^ uVar4;
    uVar2 = uVar4 ^ uVar2;
    param_3[10] = uVar4;
    param_3[0xb] = uVar2;
    (*((undefined *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_3) + 0x33)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x23d00u + (uint32_t)((uVar2 & 0xff) * 4) * 1u))));
    (*((undefined *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_3) + 0x32)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x23d00u + (uint32_t)((uint)(*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_3) + 0x2f)))) * 4) * 1u))));
    (*((undefined *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_3) + 0x31)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x23d00u + (uint32_t)((uint)(*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_3) + 0x2e)))) * 4) * 1u))));
    *(byte *)(param_3 + 0xc) =
         (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x23d00u + (uint32_t)((uint)(*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_3) + 0x2d)))) * 4) * 1u)))) ^ DAT_000234ef;
    uVar5 = param_3[0xc] ^ uVar5;
    uVar3 = uVar5 ^ uVar3;
    param_3[0xc] = uVar5;
    param_3[0xd] = uVar3;
    uVar4 = uVar3 ^ uVar4;
    uVar2 = uVar4 ^ uVar2;
    param_3[0xe] = uVar4;
    param_3[0xf] = uVar2;
    (*((undefined *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_3) + 0x43)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x23d00u + (uint32_t)((uVar2 & 0xff) * 4) * 1u))));
    (*((undefined *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_3) + 0x42)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x23d00u + (uint32_t)((uint)(*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_3) + 0x3f)))) * 4) * 1u))));
    (*((undefined *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_3) + 0x41)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x23d00u + (uint32_t)((uint)(*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_3) + 0x3e)))) * 4) * 1u))));
    *(byte *)(param_3 + 0x10) =
         (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x23d00u + (uint32_t)((uint)(*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_3) + 0x3d)))) * 4) * 1u)))) ^ DAT_000234f0;
    uVar5 = param_3[0x10] ^ uVar5;
    param_3[0x10] = uVar5;
    uVar3 = uVar5 ^ uVar3;
    param_3[0x11] = uVar3;
    uVar4 = uVar3 ^ uVar4;
    uVar2 = uVar4 ^ uVar2;
    param_3[0x12] = uVar4;
    param_3[0x13] = uVar2;
    (*((undefined *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_3) + 0x53)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x23d00u + (uint32_t)((uVar2 & 0xff) * 4) * 1u))));
    (*((undefined *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_3) + 0x52)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x23d00u + (uint32_t)((uint)(*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_3) + 0x4f)))) * 4) * 1u))));
    (*((undefined *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_3) + 0x51)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x23d00u + (uint32_t)((uint)(*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_3) + 0x4e)))) * 4) * 1u))));
    *(byte *)(param_3 + 0x14) =
         (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x23d00u + (uint32_t)((uint)(*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_3) + 0x4d)))) * 4) * 1u)))) ^ DAT_000234f1;
    uVar5 = param_3[0x14] ^ uVar5;
    param_3[0x14] = uVar5;
    uVar3 = uVar5 ^ uVar3;
    param_3[0x15] = uVar3;
    uVar4 = uVar3 ^ uVar4;
    uVar2 = uVar4 ^ uVar2;
    param_3[0x16] = uVar4;
    param_3[0x17] = uVar2;
    (*((undefined *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_3) + 99)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x23d00u + (uint32_t)((uVar2 & 0xff) * 4) * 1u))));
    (*((undefined *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_3) + 0x62)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x23d00u + (uint32_t)((uint)(*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_3) + 0x5f)))) * 4) * 1u))));
    (*((undefined *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_3) + 0x61)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x23d00u + (uint32_t)((uint)(*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_3) + 0x5e)))) * 4) * 1u))));
    *(byte *)(param_3 + 0x18) =
         (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x23d00u + (uint32_t)((uint)(*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_3) + 0x5d)))) * 4) * 1u)))) ^ DAT_000234f2;
    uVar5 = param_3[0x18] ^ uVar5;
    param_3[0x18] = uVar5;
    uVar3 = uVar5 ^ uVar3;
    param_3[0x19] = uVar3;
    uVar4 = uVar3 ^ uVar4;
    uVar2 = uVar4 ^ uVar2;
    param_3[0x1a] = uVar4;
    param_3[0x1b] = uVar2;
    (*((undefined *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_3) + 0x73)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x23d00u + (uint32_t)((uVar2 & 0xff) * 4) * 1u))));
    (*((undefined *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_3) + 0x72)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x23d00u + (uint32_t)((uint)(*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_3) + 0x6f)))) * 4) * 1u))));
    (*((undefined *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_3) + 0x71)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x23d00u + (uint32_t)((uint)(*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_3) + 0x6e)))) * 4) * 1u))));
    *(byte *)(param_3 + 0x1c) =
         (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x23d00u + (uint32_t)((uint)(*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_3) + 0x6d)))) * 4) * 1u)))) ^ DAT_000234f3;
    uVar5 = param_3[0x1c] ^ uVar5;
    param_3[0x1c] = uVar5;
    uVar3 = uVar5 ^ uVar3;
    param_3[0x1d] = uVar3;
    uVar4 = uVar3 ^ uVar4;
    uVar2 = uVar4 ^ uVar2;
    param_3[0x1e] = uVar4;
    param_3[0x1f] = uVar2;
    (*((undefined *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_3) + 0x83)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x23d00u + (uint32_t)((uVar2 & 0xff) * 4) * 1u))));
    (*((undefined *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_3) + 0x82)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x23d00u + (uint32_t)((uint)(*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_3) + 0x7f)))) * 4) * 1u))));
    (*((undefined *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_3) + 0x81)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x23d00u + (uint32_t)((uint)(*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_3) + 0x7e)))) * 4) * 1u))));
    *(byte *)(param_3 + 0x20) =
         (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x23d00u + (uint32_t)((uint)(*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_3) + 0x7d)))) * 4) * 1u)))) ^ DAT_000234f4;
    uVar5 = param_3[0x20] ^ uVar5;
    uVar3 = uVar5 ^ uVar3;
    param_3[0x20] = uVar5;
    param_3[0x21] = uVar3;
    uVar4 = uVar3 ^ uVar4;
    uVar2 = uVar4 ^ uVar2;
    param_3[0x22] = uVar4;
    param_3[0x23] = uVar2;
    (*((undefined *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_3) + 0x93)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x23d00u + (uint32_t)((uVar2 & 0xff) * 4) * 1u))));
    (*((undefined *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_3) + 0x92)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x23d00u + (uint32_t)((uint)(*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_3) + 0x8f)))) * 4) * 1u))));
    (*((undefined *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_3) + 0x91)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x23d00u + (uint32_t)((uint)(*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_3) + 0x8e)))) * 4) * 1u))));
    *(byte *)(param_3 + 0x24) =
         (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x23d00u + (uint32_t)((uint)(*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_3) + 0x8d)))) * 4) * 1u)))) ^ DAT_000234f5;
    uVar5 = param_3[0x24] ^ uVar5;
    uVar3 = uVar5 ^ uVar3;
    param_3[0x24] = uVar5;
    param_3[0x25] = uVar3;
    uVar4 = uVar3 ^ uVar4;
    uVar2 = uVar4 ^ uVar2;
    param_3[0x26] = uVar4;
    param_3[0x27] = uVar2;
    (*((undefined *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_3) + 0xa3)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x23d00u + (uint32_t)((uVar2 & 0xff) * 4) * 1u))));
    (*((undefined *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_3) + 0xa2)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x23d00u + (uint32_t)((uint)(*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_3) + 0x9f)))) * 4) * 1u))));
    (*((undefined *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_3) + 0xa1)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x23d00u + (uint32_t)((uint)(*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_3) + 0x9e)))) * 4) * 1u))));
    *(byte *)(param_3 + 0x28) =
         (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x23d00u + (uint32_t)((uint)(*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_3) + 0x9d)))) * 4) * 1u)))) ^ DAT_000234f6;
    uVar1 = param_3[0x28];
    param_3[0x28] = uVar1 ^ uVar5;
    uVar3 = uVar1 ^ uVar5 ^ uVar3;
    param_3[0x29] = uVar3;
    uVar3 = uVar3 ^ uVar4;
    param_3[0x2a] = uVar3;
    param_3[0x2b] = uVar3 ^ uVar2;
    *(undefined1 *)(param_3 + 0x30) = 1;
    return 0;
  }
  return 0xff;
}



void FUN_00087ac2(undefined4 *param_1)

{
  int iVar1;
  undefined4 *puVar2;
  
  *param_1 = 0;
  param_1[1] = 0;
  param_1[2] = 0;
  param_1[3] = 0;
  param_1[4] = 0;
  param_1[5] = 0;
  param_1[6] = 0;
  param_1[7] = 0;
  param_1[8] = 0;
  param_1[9] = 0;
  param_1[10] = 0;
  param_1[0xb] = 0;
  param_1[0xc] = 0;
  param_1[0xd] = 0;
  param_1[0xe] = 0;
  param_1[0xf] = 0;
  param_1[0x10] = 0;
  param_1[0x11] = 0;
  param_1[0x12] = 0;
  param_1[0x13] = 0;
  param_1[0x14] = 0;
  param_1[0x15] = 0;
  param_1[0x16] = 0;
  param_1[0x17] = 0;
  param_1[0x18] = 0;
  param_1[0x19] = 0;
  param_1[0x1a] = 0;
  param_1[0x1b] = 0;
  param_1[0x1c] = 0;
  param_1[0x1d] = 0;
  param_1[0x1e] = 0;
  param_1[0x1f] = 0;
  param_1[0x20] = 0;
  param_1[0x21] = 0;
  param_1[0x22] = 0;
  param_1[0x23] = 0;
  param_1[0x24] = 0;
  param_1[0x25] = 0;
  param_1[0x26] = 0;
  param_1[0x27] = 0;
  param_1[0x28] = 0;
  param_1[0x29] = 0;
  param_1[0x2a] = 0;
  param_1[0x2b] = 0;
  param_1[0x2c] = 0;
  param_1[0x2d] = 0;
  param_1[0x2e] = 0;
  param_1[0x2f] = 0;
  puVar2 = param_1 + 0x30;
  for (iVar1 = 4; iVar1 + -0x20 < 0 == (iVar1 < 0 && -1 < iVar1 + -0x20); iVar1 = iVar1 + -0x20) {
    *puVar2 = 0;
    puVar2[1] = 0;
    puVar2[2] = 0;
    puVar2[3] = 0;
    puVar2[4] = 0;
    puVar2[5] = 0;
    puVar2[6] = 0;
    puVar2[7] = 0;
    puVar2 = puVar2 + 8;
  }
  for (; iVar1 + -0x10 < 0 == (iVar1 < 0 && -1 < iVar1 + -0x10); iVar1 = iVar1 + -0x10) {
    *puVar2 = 0;
    puVar2[1] = 0;
    puVar2[2] = 0;
    puVar2[3] = 0;
    puVar2 = puVar2 + 4;
  }
  for (; 0 < iVar1; iVar1 = iVar1 + -4) {
    *puVar2 = 0;
    puVar2 = puVar2 + 1;
  }
  *(undefined1 *)(param_1 + 0x30) = 0;
  return;
}



int FUN_00087b74(undefined4 param_1,undefined1 param_2,undefined4 *param_3,char param_4,uint param_5
                )

{
  int iVar1;
  bool bVar2;
  
  if (param_4 == '\x10') {
    (*((undefined4 *)camry_host_ptr((uint32_t)(param_5 + 0xc4)))) = 0;
    (*((undefined4 *)camry_host_ptr((uint32_t)(param_5 + 200)))) = 0;
    (*((undefined4 *)camry_host_ptr((uint32_t)(param_5 + 0xcc)))) = 0;
    (*((undefined4 *)camry_host_ptr((uint32_t)(param_5 + 0xd0)))) = 0;
    if (((param_5 & 3) == 0) && (((uint)camry_host_addr(param_3) & 3) == 0)) {
      (*((undefined4 *)camry_host_ptr((uint32_t)(param_5 + 0xd4)))) = *param_3;
      (*((undefined4 *)camry_host_ptr((uint32_t)(param_5 + 0xd8)))) = param_3[1];
      (*((undefined4 *)camry_host_ptr((uint32_t)(param_5 + 0xdc)))) = param_3[2];
      (*((undefined4 *)camry_host_ptr((uint32_t)(param_5 + 0xe0)))) = param_3[3];
    }
    else {
      (*((undefined1 *)camry_host_ptr((uint32_t)(param_5 + 0xd4)))) = *(undefined1 *)param_3;
      (*((undefined1 *)camry_host_ptr((uint32_t)(param_5 + 0xd5)))) = (*((undefined1 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_3) + 1))));
      (*((undefined1 *)camry_host_ptr((uint32_t)(param_5 + 0xd6)))) = (*((undefined1 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_3) + 2))));
      (*((undefined1 *)camry_host_ptr((uint32_t)(param_5 + 0xd7)))) = (*((undefined1 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_3) + 3))));
      (*((undefined1 *)camry_host_ptr((uint32_t)(param_5 + 0xd8)))) = *(undefined1 *)(param_3 + 1);
      (*((undefined1 *)camry_host_ptr((uint32_t)(param_5 + 0xd9)))) = (*((undefined1 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_3) + 5))));
      (*((undefined1 *)camry_host_ptr((uint32_t)(param_5 + 0xda)))) = (*((undefined1 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_3) + 6))));
      (*((undefined1 *)camry_host_ptr((uint32_t)(param_5 + 0xdb)))) = (*((undefined1 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_3) + 7))));
      (*((undefined1 *)camry_host_ptr((uint32_t)(param_5 + 0xdc)))) = *(undefined1 *)(param_3 + 2);
      (*((undefined1 *)camry_host_ptr((uint32_t)(param_5 + 0xdd)))) = (*((undefined1 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_3) + 9))));
      (*((undefined1 *)camry_host_ptr((uint32_t)(param_5 + 0xde)))) = (*((undefined1 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_3) + 10))));
      (*((undefined1 *)camry_host_ptr((uint32_t)(param_5 + 0xdf)))) = (*((undefined1 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_3) + 0xb))));
      (*((undefined1 *)camry_host_ptr((uint32_t)(param_5 + 0xe0)))) = *(undefined1 *)(param_3 + 3);
      (*((undefined1 *)camry_host_ptr((uint32_t)(param_5 + 0xe1)))) = (*((undefined1 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_3) + 0xd))));
      (*((undefined1 *)camry_host_ptr((uint32_t)(param_5 + 0xe2)))) = (*((undefined1 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_3) + 0xe))));
      (*((undefined1 *)camry_host_ptr((uint32_t)(param_5 + 0xe3)))) = (*((undefined1 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_3) + 0xf))));
    }
    iVar1 = FUN_000876c4(((uint *)camry_host_ptr((uint32_t)(param_1))), param_2, ((uint *)camry_host_ptr((uint32_t)(param_5))));
    bVar2 = iVar1 == 0;
  }
  else {
    bVar2 = false;
    iVar1 = 0xff;
  }
  (*((bool *)camry_host_ptr((uint32_t)(param_5 + 0xc0)))) = bVar2;
  return iVar1;
}



undefined4 FUN_00087c40(uint *param_1,uint *param_2,undefined1 param_3,int param_4)

{
  int iVar1;
  char cVar2;
  int iVar3;
  undefined4 uVar4;
  char *pcVar5;
  undefined4 local_20;
  undefined4 uStack_1c;
  undefined4 uStack_18;
  undefined4 uStack_14;
  
  if ((((((*((int *)camry_host_ptr((uint32_t)(param_4 + 0xd4)))) == -1) && ((*((int *)camry_host_ptr((uint32_t)(param_4 + 0xd8)))) == -1)) &&
       ((*((int *)camry_host_ptr((uint32_t)(param_4 + 0xdc)))) == -1)) && ((*((int *)camry_host_ptr((uint32_t)(param_4 + 0xe0)))) == -1)) ||
     (iVar3 = FUN_000863a0(((undefined4 *)camry_host_ptr((uint32_t)(param_4 + 0xd4))), &local_20, param_3,  param_4), iVar3 != 0)) {
    uVar4 = 0xff;
  }
  else {
    if ((((uint)camry_host_addr(param_2) & 3) == 0) && (((uint)camry_host_addr(param_1) & 3) == 0)) {
      *param_2 = *param_1 ^ local_20;
      param_2[1] = param_1[1] ^ uStack_1c;
      param_2[2] = param_1[2] ^ uStack_18;
      param_2[3] = param_1[3] ^ uStack_14;
    }
    else {
      *(byte *)param_2 = (byte)*param_1 ^ (byte)local_20;
      (*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_2) + 1)))) = (*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 1)))) ^ (*((uint8_t *)((uint8_t *)&local_20 + 1u)));
      (*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_2) + 2)))) = (*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 2)))) ^ (*((uint8_t *)((uint8_t *)&local_20 + 2u)));
      (*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_2) + 3)))) = (*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 3)))) ^ (*((uint8_t *)((uint8_t *)&local_20 + 3u)));
      *(byte *)(param_2 + 1) = (byte)param_1[1] ^ (byte)uStack_1c;
      (*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_2) + 5)))) = (*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 5)))) ^ (*((uint8_t *)((uint8_t *)&uStack_1c + 1u)));
      (*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_2) + 6)))) = (*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 6)))) ^ (*((uint8_t *)((uint8_t *)&uStack_1c + 2u)));
      (*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_2) + 7)))) = (*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 7)))) ^ (*((uint8_t *)((uint8_t *)&uStack_1c + 3u)));
      *(byte *)(param_2 + 2) = (byte)param_1[2] ^ (byte)uStack_18;
      (*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_2) + 9)))) = (*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 9)))) ^ (*((uint8_t *)((uint8_t *)&uStack_18 + 1u)));
      (*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_2) + 10)))) = (*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 10)))) ^ (*((uint8_t *)((uint8_t *)&uStack_18 + 2u)));
      (*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_2) + 0xb)))) = (*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 0xb)))) ^ (*((uint8_t *)((uint8_t *)&uStack_18 + 3u)));
      *(byte *)(param_2 + 3) = (byte)param_1[3] ^ (byte)uStack_14;
      (*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_2) + 0xd)))) = (*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 0xd)))) ^ (*((uint8_t *)((uint8_t *)&uStack_14 + 1u)));
      (*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_2) + 0xe)))) = (*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 0xe)))) ^ (*((uint8_t *)((uint8_t *)&uStack_14 + 2u)));
      (*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_2) + 0xf)))) = (*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 0xf)))) ^ (*((uint8_t *)((uint8_t *)&uStack_14 + 3u)));
    }
    iVar3 = 3;
    do {
      iVar1 = iVar3 * 4 + param_4;
      pcVar5 = ((char *)camry_host_ptr((uint32_t)(iVar1 + 0xd7)));
      cVar2 = *pcVar5 + '\x01';
      *pcVar5 = cVar2;
      if ((cVar2 == '\0') &&
         (pcVar5 = ((char *)camry_host_ptr((uint32_t)(iVar1 + 0xd6))), cVar2 = *pcVar5 + '\x01', *pcVar5 = cVar2, cVar2 == '\0')
         ) {
        iVar1 = iVar3 * 4 + param_4;
        cVar2 = (*((char *)camry_host_ptr((uint32_t)(iVar1 + 0xd5)))) + '\x01';
        (*((char *)camry_host_ptr((uint32_t)(iVar1 + 0xd5)))) = cVar2;
        if (cVar2 == '\0') {
          (*((char *)camry_host_ptr((uint32_t)(iVar1 + 0xd4)))) = (*((char *)camry_host_ptr((uint32_t)(iVar1 + 0xd4)))) + '\x01';
        }
      }
    } while (((*((int *)camry_host_ptr((uint32_t)(iVar3 * 4 + param_4 + 0xd4)))) == 0) &&
            (iVar1 = iVar3 + -1, iVar3 = iVar3 + -1, -1 < iVar1));
    uVar4 = 0;
  }
  return uVar4;
}



/* Far-call trampoline: prepare {lp},0 / jarl 0x8844E / dispose 0,{lp},lp; byte-verified against the
   exact image. Forwards with registers and stack unchanged; marked as a thunk. Forwarding shape
   machine-verified; target semantics not recovered. */

undefined4 thunk_FUN_0008844e(void)

{
  return FUN_0008844e();
}



/* Far-call trampoline: prepare {lp},0 / jarl 0x884EA / dispose 0,{lp},lp; byte-verified against the
   exact image. Forwards with registers and stack unchanged; marked as a thunk. Forwarding shape
   machine-verified; target semantics not recovered. */

undefined4 thunk_FUN_000884ea(void)

{
  return FUN_000884ea();
}



/* Far-call trampoline: prepare {lp},0 / jarl 0x886E0 / dispose 0,{lp},lp; byte-verified against the
   exact image. Forwards with registers and stack unchanged; marked as a thunk. Forwarding shape
   machine-verified; target semantics not recovered. */

undefined4 thunk_FUN_000886e0(void)

{
  return FUN_000886e0();
}



/* Far-call trampoline: prepare {lp},0 / jarl 0x7995C / dispose 0,{lp},lp; byte-verified against the
   exact image. Forwards with registers and stack unchanged; marked as a thunk. Forwarding shape
   machine-verified; target semantics not recovered. */

void thunk_FUN_0007995c(void)

{
  FUN_0007995c();
  return;
}



void FUN_00087edc(undefined1 param_1)

{
  FUN_0008aa1c(((undefined *)camry_host_ptr(0xfebf10d0u)));
  ((void)(param_1), thunk_FUN_000799b0());
  return;
}



void FUN_00087ef6(char param_1)

{
  undefined1 uVar1;
  
  if (param_1 == '\0') {
    DAT_febf10d0 = 0;
    DAT_febf10d4 = 0;
    FUN_0008aa04(((undefined *)camry_host_ptr(0xfebf10d0u)));
    uVar1 = 0;
  }
  else {
    uVar1 = 1;
    if (param_1 != '\x01') {
      uVar1 = 0xff;
    }
  }
  FUN_000885b2(uVar1);
  return;
}



void FUN_00087f22(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  f33_memzero(((undefined *)camry_host_ptr(0xfebf10f4u)),0x78);
  f33_memzero(((undefined *)camry_host_ptr((uint32_t)(puVar1 + 0x58d8))), 8);
  (*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + 0x58e4)))) = 0xffffffff;
  (*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + 0x58e0)))) = 0xffffffff;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x58f0))))) = 0xd2;
  return;
}



undefined4 FUN_00087f52(void *param_1,int param_2,undefined4 param_3,uint param_4,uint *param_5)

{
  undefined4 uVar1;
  
  if (((((uintptr_t)(param_1)==(uintptr_t)((void *)0x0)) || (param_4 == 0)) || ((uintptr_t)(param_5)==(uintptr_t)((uint *)0x0))) ||
     (param_2 != 0x40)) {
    uVar1 = 1;
  }
  else if (*param_5 < 0x30) {
    uVar1 = 3;
  }
  else {
    uVar1 = 0;
    DAT_febf10d8 = camry_host_addr(param_5);
    DAT_febf10e0 = ~(uint)camry_host_addr(param_5);
    DAT_febf10e4 = ~param_4;
    DAT_febf10f4 = camry_host_addr(((undefined *)camry_host_ptr(0xfebf10fcu)));
    DAT_febf10f8 = camry_host_addr(((undefined *)camry_host_ptr(0xfebf113cu)));
    DAT_febf10dc = param_4;
    f33_memcpy_forward(((undefined *)camry_host_ptr(0xfebf10fcu)),param_1,0x10);
    f33_memcpy_forward(((undefined *)camry_host_ptr(0xfebf110cu)),((void *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 0x10))),0x20);
    f33_memcpy_forward(((undefined *)camry_host_ptr(0xfebf112cu)),((void *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 0x30))),0x10);
  }
  return uVar1;
}



undefined4 FUN_000852fe(ushort param_1,uint param_2,uint param_3,int *param_4)

{
  int *piVar1;
  int iVar2;
  uint uVar3;
  
  param_2 = param_2 & 0xff;
  param_3 = param_3 & 0xff;
  iVar2 = (int)(short)(param_1 & 0xff);
  if (param_2 < 6) {
    piVar1 = ((int *)camry_host_ptr((uint32_t)((short)(ushort)(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x23454u + (uint32_t)(param_2) * 1u)))) * 0x60 +
                    *(int *)(((undefined *)camry_host_ptr(0x22f48u)) + iVar2 * 0x74))));
    *piVar1 = param_4[1];
    piVar1[1] = (uint)*(byte *)(param_4 + 3) << 0x1c;
    piVar1[2] = param_4[2];
    for (uVar3 = 0; uVar3 < param_3; uVar3 = uVar3 + 1 & 0xff) {
      piVar1[uVar3 + 3] = (*((int *)camry_host_ptr((uint32_t)(uVar3 * 4 + *param_4))));
    }
  }
  else {
    if (5 < param_3) {
      return 1;
    }
    piVar1 = ((int *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x22f44u + (uint32_t)(iVar2 * 0x1d) * 4u)))) + param_2 * 0x20)));
    *piVar1 = param_4[1];
    piVar1[1] = (uint)*(byte *)(param_4 + 3) << 0x1c;
    piVar1[2] = param_4[2];
    for (uVar3 = 0; uVar3 < param_3; uVar3 = uVar3 + 1 & 0xff) {
      piVar1[uVar3 + 3] = (*((int *)camry_host_ptr((uint32_t)(uVar3 * 4 + *param_4))));
    }
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x22f3cu + (uint32_t)(iVar2 * 0x1d) * 4u)))) + (uint32_t)(param_2))))) = 1;
  return 0;
}

undefined4 FUN_000853aa(uint param_1,uint param_2,int *param_3)

{
  undefined1 *puVar1;
  undefined1 *puVar2;
  int iVar3;
  int iVar4;
  uint uVar5;
  undefined1 local_54 [64];
  undefined1 *puStack_14;
  uint uStack_10;
  undefined4 uStack_c;
  undefined1 uStack_8;
  
  puStack_14 = local_54;
  param_1 = param_1 & 0xff;
  param_2 = param_2 & 0xff;
  iVar3 = (int)(short)param_1;
  iVar4 = 0;
  if ((param_2 == (byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x22eaeu + (uint32_t)(param_1) * 1u))))) ||
     (iVar4 = 1, param_2 == (byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x22eb1u + (uint32_t)(param_1) * 1u)))))) {
    if (((*((uint *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x22f34u + (uint32_t)(iVar3 * 0x1d) * 4u)))) + iVar4 * 4)))) & 1) == 0) {
      return 2;
    }
    if (((*((uint *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x22f2cu + (uint32_t)(iVar3 * 0x1d) * 4u)))) + iVar4 * 4)))) & 0x11) != 1) {
      return 2;
    }
    uStack_10 = param_3[1];
    if ((uStack_10 & 0x80000000) == 0) {
      uStack_10 = uStack_10 & 0x7ff;
    }
    else {
      uStack_10 = uStack_10 & 0x9fffffff;
    }
    uVar5 = 0;
    do {
      puVar1 = local_54 + uVar5;
      puVar2 = ((undefined1 *)camry_host_ptr((uint32_t)(*param_3 + uVar5)));
      uVar5 = uVar5 + 1;
      *puVar1 = *puVar2;
    } while (uVar5 < 8);
    uStack_8 = (undefined1)param_3[2];
    uStack_c = 0;
    puStack_14 = local_54;
    FUN_00085286(param_1,iVar4,2,&puStack_14);
  }
  else {
    if (((*((volatile uint8_t *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x22f30u + (uint32_t)(iVar3 * 0x1d) * 4u)))) + (uint32_t)(param_2))))) & 0x1e) != 0) {
      return 2;
    }
    uStack_10 = param_3[1];
    if ((uStack_10 & 0x80000000) == 0) {
      uStack_10 = uStack_10 & 0x7ff;
    }
    else {
      uStack_10 = uStack_10 & 0x9fffffff;
    }
    uVar5 = 0;
    do {
      puVar1 = local_54 + uVar5;
      puVar2 = ((undefined1 *)camry_host_ptr((uint32_t)(*param_3 + uVar5)));
      uVar5 = uVar5 + 1;
      *puVar1 = *puVar2;
    } while (uVar5 < 8);
    uStack_8 = (undefined1)param_3[2];
    uStack_c = 0;
    FUN_000852fe(param_1,param_2,2,&puStack_14);
  }
  return 0;
}

undefined4 FUN_0008549e(uint param_1,uint param_2,int *param_3)

{
  int iVar1;
  undefined1 uVar2;
  byte bVar3;
  int iVar4;
  uint uVar5;
  short sVar6;
  undefined4 uVar7;
  uint uVar8;
  uint uVar9;
  undefined1 local_54 [64];
  undefined1 *puStack_14;
  uint uStack_10;
  uint uStack_c;
  undefined1 uStack_8;
  
  param_1 = param_1 & 0xff;
  param_2 = param_2 & 0xff;
  sVar6 = (short)param_1;
  iVar1 = (int)sVar6;
  uVar7 = 1;
  uVar8 = (uint)(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe5026u + (uint32_t)(param_1) * 1u))));
  if (((int)uVar8 >> 4) + (uVar8 & 0xf) == 0xf) {
    uVar7 = 2;
    iVar4 = 0;
    if ((param_2 == (byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x22eaeu + (uint32_t)(param_1) * 1u))))) ||
       (iVar4 = 1, param_2 == (byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x22eb1u + (uint32_t)(param_1) * 1u)))))) {
      if ((((*((uint *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x22f34u + (uint32_t)(iVar1 * 0x1d) * 4u)))) + iVar4 * 4)))) & 1) != 0) &&
         (((*((uint *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x22f2cu + (uint32_t)(iVar1 * 0x1d) * 4u)))) + iVar4 * 4)))) & 0x11) == 1)) {
        uVar9 = param_3[1];
        if ((uVar9 & 0x80000000) == 0) {
          uVar9 = uVar9 & 0x7ff;
        }
        else {
          uVar9 = uVar9 & 0x9fffffff;
        }
        uVar2 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x2345au + (uint32_t)(*(byte *)(param_3 + 2)) * 1u))));
        bVar3 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x2349bu + (uint32_t)(*(byte *)(param_3 + 2)) * 1u))));
        for (uVar5 = 0; uVar5 < bVar3; uVar5 = uVar5 + 1 & 0xff) {
          local_54[uVar5] = (*((undefined1 *)camry_host_ptr((uint32_t)(*param_3 + uVar5))));
        }
        if (uVar8 == 0x3c) {
          uStack_c = 6;
        }
        else {
          uStack_c = 4;
        }
        uStack_c = *(uint *)(((undefined *)camry_host_ptr(0x233e8u)) + sVar6 * 0x34) | uStack_c;
        puStack_14 = local_54;
        uStack_10 = uVar9;
        uStack_8 = uVar2;
        uVar7 = FUN_00085286(param_1,iVar4,(int)(uint)bVar3 >> 2,&puStack_14);
      }
    }
    else if (((*((volatile uint8_t *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x22f30u + (uint32_t)(iVar1 * 0x1d) * 4u)))) + (uint32_t)(param_2))))) & 0x1e) == 0) {
      uVar9 = param_3[1];
      if ((uVar9 & 0x80000000) == 0) {
        uVar9 = uVar9 & 0x7ff;
      }
      else {
        uVar9 = uVar9 & 0x9fffffff;
      }
      uVar2 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x2345au + (uint32_t)(*(byte *)(param_3 + 2)) * 1u))));
      bVar3 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x2349bu + (uint32_t)(*(byte *)(param_3 + 2)) * 1u))));
      for (uVar5 = 0; uVar5 < bVar3; uVar5 = uVar5 + 1 & 0xff) {
        local_54[uVar5] = (*((undefined1 *)camry_host_ptr((uint32_t)(*param_3 + uVar5))));
      }
      if (uVar8 == 0x3c) {
        uStack_c = 6;
      }
      else {
        uStack_c = 4;
      }
      uStack_c = *(uint *)(((undefined *)camry_host_ptr(0x233e4u)) + sVar6 * 0x34) | uStack_c;
      puStack_14 = local_54;
      uStack_10 = uVar9;
      uStack_8 = uVar2;
      uVar7 = FUN_000852fe(param_1,param_2,(int)(uint)bVar3 >> 2,&puStack_14);
    }
  }
  return uVar7;
}

undefined4 FUN_000855f4(uint param_1,uint param_2)

{
  int iVar1;
  short sVar2;
  
  param_1 = param_1 & 0xff;
  param_2 = param_2 & 0xff;
  sVar2 = (short)param_1;
  iVar1 = (int)sVar2;
  if (param_2 == (byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x22eaeu + (uint32_t)(param_1) * 1u))))) {
    (*((uint *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x22f34u + (uint32_t)(iVar1 * 0x1d) * 4u))))))) = (uint)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x233b8u + (uint32_t)(sVar2 * 0xd) * 4u)))) & 0xfffffffe
    ;
    if (((*((uint *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x22f2cu + (uint32_t)(iVar1 * 0x1d) * 4u))))))) & 0x11) != 1) {
      return 2;
    }
    *(undefined **)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x22f34u + (uint32_t)(iVar1 * 0x1d) * 4u)))) = ((void *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x233b8u + (uint32_t)(sVar2 * 0xd) * 4u)))))));
  }
  else if (param_2 == (byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x22eb1u + (uint32_t)(param_1) * 1u))))) {
    (*((uint *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x22f34u + (uint32_t)(iVar1 * 0x1d) * 4u)))) + 4)))) =
         (uint)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x233bcu + (uint32_t)(sVar2 * 0xd) * 4u)))) & 0xfffffffe;
    if (((*((uint *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x22f2cu + (uint32_t)(iVar1 * 0x1d) * 4u)))) + 4)))) & 0x11) != 1) {
      return 2;
    }
    *(undefined **)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x22f34u + (uint32_t)(iVar1 * 0x1d) * 4u)))) + 4) = ((void *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x233bcu + (uint32_t)(sVar2 * 0xd) * 4u)))))));
  }
  else {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x22f3cu + (uint32_t)(iVar1 * 0x1d) * 4u)))) + (uint32_t)(param_2))))) = 2;
    if (((*((volatile uint8_t *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x22f30u + (uint32_t)(iVar1 * 0x1d) * 4u)))) + (uint32_t)(param_2))))) & 0x1e) != 2) {
      return 2;
    }
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x22f30u + (uint32_t)(iVar1 * 0x1d) * 4u)))) + (uint32_t)(param_2))))) = 0;
  }
  return 0;
}

void FUN_0008569a(uint param_1)

{
  int iVar1;
  ushort uVar2;
  ushort uVar3;
  byte bVar4;
  ushort uVar5;
  short sVar6;
  uint uVar7;
  
  param_1 = param_1 & 0xff;
  sVar6 = (short)param_1;
  iVar1 = (int)sVar6;
  uVar2 = *(ushort *)(((undefined *)camry_host_ptr(0x22ebeu)) + param_1 * 4);
  uVar3 = *(ushort *)(((undefined *)camry_host_ptr(0x22ebcu)) + param_1 * 4);
  (*((uint *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x22f34u + (uint32_t)(iVar1 * 0x1d) * 4u))))))) = (uint)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x233b8u + (uint32_t)(sVar6 * 0xd) * 4u)))) & 0xfffffffe;
  (*((uint *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x22f34u + (uint32_t)(iVar1 * 0x1d) * 4u)))) + 4)))) =
       (uint)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x233bcu + (uint32_t)(sVar6 * 0xd) * 4u)))) & 0xfffffffe;
  uVar5 = *(ushort *)(((undefined *)camry_host_ptr(0x22e94u)) + param_1 * 2);
  bVar4 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x22ea8u + (uint32_t)(param_1) * 1u))));
  for (uVar7 = 0; uVar7 < bVar4; uVar7 = uVar7 + 1 & 0xff) {
    if ((1 << (uVar7 & 0xf) & 0xffffU & (uint)((uVar2 | uVar3) & uVar5)) != 0) {
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x22f3cu + (uint32_t)(iVar1 * 0x1d) * 4u)))) + (uint32_t)(uVar7))))) = 2;
    }
  }
  return;
}


void FUN_00087fd8(uchar param_1)

{
  uint *puVar1;
  void *pvVar2;
  uint32_t puVar3;
  undefined *puVar4;
  
  pvVar2 = ((void *)camry_host_ptr((uint32_t)(DAT_febf10dc)));
  puVar1 = ((void *)camry_host_ptr((uint32_t)(DAT_febf10d8)));
  puVar3 = 0xfebeb800u;
  puVar4 = ((undefined *)camry_host_ptr(0xfebeb800u));
  if ((DAT_febf10dc == 0) || (DAT_febf10d8 == 0)) {
    param_1 = '\x01';
  }
  else if ((~(uint)DAT_febf10dc == DAT_febf10e4) && (~(uint)DAT_febf10d8 == DAT_febf10e0)) {
    if (param_1 == '\0') {
      puVar3 = 0xfebeb800u;
      f33_memcpy_forward(((void *)camry_host_ptr((uint32_t)(DAT_febf10dc))), ((undefined *)camry_host_ptr(0xfebf113cu)), 0x20);
      f33_memcpy_forward(((void *)camry_host_ptr((uint32_t)((int)camry_host_addr(pvVar2) + 0x20))),((undefined *)camry_host_ptr(0xfebf115cu)),0x10);
      *puVar1 = 0x30;
    }
    else {
      f33_memzero(((void *)camry_host_ptr((uint32_t)(DAT_febf10dc))), (*((volatile uint32_t *)camry_host_ptr((uint32_t)(DAT_febf10d8)))));
    }
    puVar4 = ((undefined *)camry_host_ptr((uint32_t)(puVar3)));
    f33_memzero(((undefined *)camry_host_ptr((uint32_t)(puVar3 + 0x58fc))), 0x40);
    f33_memzero(((undefined *)camry_host_ptr((uint32_t)(0x5936u + (int)(puVar3 + 6)))), 0x30);
  }
  else {
    param_1 = '\x01';
    DAT_febf1191 = 1;
  }
  f33_crypto_key_job_deliver_completion(param_1);
  if (((int8_t)puVar4[0x5990]) == -0x3d) {
    FUN_00087edc(0);
    puVar4[0x5990] = 0xe1;
  }
  return;
}


