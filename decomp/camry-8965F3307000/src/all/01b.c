#include "common.h"


/* WARNING: Type propagation algorithm not settling */

short FUN_0006c358(uint *param_1,ushort *param_2,undefined4 *param_3)

{
  ushort uVar1;
  ushort uVar2;
  short sVar3;
  uint uVar4;
  int iVar5;
  undefined4 uVar6;
  ushort uVar7;
  uint uVar8;
  code *pcVar9;
  ushort local_3c;
  ushort uStack_3a;
  ushort auStack_36 [2];
  ushort uStack_32;
  ushort uStack_30;
  undefined2 uStack_2c;
  ushort uStack_2a;
  undefined2 uStack_28;
  
  sVar3 = 0x11;
  if ((((((uintptr_t)(param_1)==(uintptr_t)((uint *)0x0)) || ((uintptr_t)(param_2)==(uintptr_t)((ushort *)0x0))) || ((uintptr_t)(param_3)==(uintptr_t)((undefined4 *)0x0)))
      || ((pcVar9 = (code *)*param_3,(uint32_t)(pcVar9) == 0u||
          ((uint32_t)(param_3[1]) == 0u)))) || ((uint32_t)(param_3[2]) == 0u)) {
    return 0x22;
  }
  uStack_30 = (ushort)param_1[2];
  auStack_36[0] = (ushort)param_1[1];
  uStack_32 = (*((ushort *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 6))));
  uStack_2a = (ushort)param_1[3];
  uStack_2c = (*((undefined2 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 10))));
  uStack_28 = (*((undefined2 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 0xe))));
  uVar1 = *param_2;
  uVar2 = param_2[1];
  local_3c = param_2[2];
  uStack_3a = param_2[3];
  if (uStack_32 == 0) {
    if (uVar1 < auStack_36[0]) {
      sVar3 = 0x2200;
    }
    else {
      sVar3 = 0;
      if (auStack_36[0] != 0) {
        sVar3 = 0x1100;
      }
    }
  }
  else if ((uVar2 < uStack_32) && (sVar3 = 0x44, uStack_2a <= uStack_3a)) {
    sVar3 = 0x22;
  }
  if (sVar3 == 0) {
    iVar5 = (*(int (*)())camry_indirect((uint32_t)(pcVar9)))();
    if (iVar5 == 0x11) {
      if ((uVar1 < auStack_36[0]) ||
         (uVar2 = auStack_36[0] + 1, uVar7 = auStack_36[0] + 1, auStack_36[0] = uVar2, uVar1 < uVar7
         )) {
        uVar8 = 0x2200;
      }
      else {
        uVar8 = 0x11001100;
      }
      uStack_32 = 0;
    }
    else if (iVar5 == 0x22) {
      auStack_36[0] = 0;
      if (uStack_32 <= uVar2) {
        uStack_32 = uStack_32 + 1;
      }
      if (uStack_30 < uStack_32) {
        uStack_30 = uStack_32;
      }
      uVar8 = 0x22;
      if (uStack_32 <= uVar2) {
        uVar8 = 0x110011;
      }
    }
    else if ((iVar5 == 0x33) || (iVar5 == 0x44)) {
      uStack_32 = 0;
      auStack_36[0] = 0;
      uVar8 = 0;
    }
    else {
      uVar8 = 0xffff;
    }
    uVar4 = uVar8 & 0xffff;
    if (uVar4 != 0) {
      if (uVar4 == 0x11) {
        if ((uint32_t)(param_3[7]) != 0u) {
          (*(int (*)())camry_indirect((uint32_t)(param_3[7])))();
        }
        pcVar9 = (code *)param_3[0xe];
      }
      else if (uVar4 == 0x22) {
        if ((uint32_t)(param_3[7]) != 0u) {
          (*(int (*)())camry_indirect((uint32_t)(param_3[7])))();
        }
        if ((uint32_t)(param_3[9]) != 0u) {
          (*(int (*)())camry_indirect((uint32_t)(param_3[9])))();
        }
        pcVar9 = (code *)param_3[0xf];
      }
      else if (uVar4 == 0x1100) {
        if ((uint32_t)(param_3[3]) != 0u) {
          (*(int (*)())camry_indirect((uint32_t)(param_3[3])))();
        }
        pcVar9 = (code *)param_3[0xc];
      }
      else {
        if (uVar4 != 0x2200) {
          uVar8 = 0;
          goto LAB_0006c8f4;
        }
        if ((uint32_t)(param_3[3]) != 0u) {
          (*(int (*)())camry_indirect((uint32_t)(param_3[3])))();
        }
        if ((uint32_t)(param_3[5]) != 0u) {
          (*(int (*)())camry_indirect((uint32_t)(param_3[5])))();
        }
        pcVar9 = (code *)param_3[0xd];
      }
      if ((uint32_t)(pcVar9) != 0u) {
        (*(int (*)())camry_indirect((uint32_t)(pcVar9)))();
      }
    }
    goto LAB_0006c8f4;
  }
  if (sVar3 == 0x11) {
    iVar5 = (*(int (*)())camry_indirect((uint32_t)(param_3[1])))();
    if (iVar5 == 0x11) {
      if ((uVar1 < auStack_36[0]) ||
         (uVar2 = auStack_36[0] + 1, uVar7 = auStack_36[0] + 1, auStack_36[0] = uVar2, uVar1 < uVar7
         )) {
        uVar8 = 0x2200;
      }
      else {
        uVar8 = 0x11001100;
      }
      uStack_32 = 0;
    }
    else if (iVar5 == 0x22) {
      auStack_36[0] = 0;
      if (uStack_32 <= uVar2) {
        uStack_32 = uStack_32 + 1;
      }
      if (uStack_30 < uStack_32) {
        uStack_30 = uStack_32;
      }
      uVar8 = 0x22;
      if (uStack_32 <= uVar2) {
        uVar8 = 0x110011;
      }
    }
    else if ((iVar5 == 0x33) || (iVar5 == 0x44)) {
      uStack_32 = 0;
      auStack_36[0] = 0;
      uVar8 = 0;
    }
    else {
      uVar8 = 0xffff;
    }
    uVar4 = uVar8 & 0xffff;
    if (uVar4 == 0) {
      if ((uint32_t)(param_3[8]) != 0u) {
        (*(int (*)())camry_indirect((uint32_t)(param_3[8])))();
      }
    }
    else {
      if (uVar4 == 0x11) {
        pcVar9 = (code *)param_3[0xe];
      }
      else if (uVar4 == 0x22) {
        if ((uint32_t)(param_3[9]) != 0u) {
          (*(int (*)())camry_indirect((uint32_t)(param_3[9])))();
        }
        pcVar9 = (code *)param_3[0xf];
      }
      else if (uVar4 == 0x1100) {
        if ((uint32_t)(param_3[8]) != 0u) {
          (*(int (*)())camry_indirect((uint32_t)(param_3[8])))();
        }
        if ((uint32_t)(param_3[3]) != 0u) {
          (*(int (*)())camry_indirect((uint32_t)(param_3[3])))();
        }
        pcVar9 = (code *)param_3[0xc];
      }
      else {
        if (uVar4 != 0x2200) {
          if ((uint32_t)(param_3[0xe]) != 0u) {
            (*(int (*)())camry_indirect((uint32_t)(param_3[0xe])))();
          }
          uVar8 = 0x11;
          goto LAB_0006c8f4;
        }
        if ((uint32_t)(param_3[8]) != 0u) {
          (*(int (*)())camry_indirect((uint32_t)(param_3[8])))();
        }
        if ((uint32_t)(param_3[3]) != 0u) {
          (*(int (*)())camry_indirect((uint32_t)(param_3[3])))();
        }
        if ((uint32_t)(param_3[5]) != 0u) {
          (*(int (*)())camry_indirect((uint32_t)(param_3[5])))();
        }
        pcVar9 = (code *)param_3[0xd];
      }
      if ((uint32_t)(pcVar9) != 0u) {
        (*(int (*)())camry_indirect((uint32_t)(pcVar9)))();
      }
    }
    goto LAB_0006c8f4;
  }
  if (sVar3 == 0x22) {
    uVar6 = (*(int (*)())camry_indirect((uint32_t)(param_3[2])))();
    uVar8 = FUN_0007110c(uVar6,auStack_36,&local_3c);
    uVar4 = uVar8 & 0xffff;
    if (uVar4 == 0) {
      pcVar9 = (code *)param_3[10];
    }
    else if (uVar4 == 0x22) {
      pcVar9 = (code *)param_3[0xf];
    }
    else {
      if (uVar4 != 0x44) {
        if ((uint32_t)(param_3[0xf]) != 0u) {
          (*(int (*)())camry_indirect((uint32_t)(param_3[0xf])))();
        }
        uVar8 = 0x22;
        goto LAB_0006c8f4;
      }
      if ((uint32_t)(param_3[0xb]) != 0u) {
        (*(int (*)())camry_indirect((uint32_t)(param_3[0xb])))();
      }
      pcVar9 = (code *)param_3[0x10];
    }
    if ((uint32_t)(pcVar9) != 0u) {
      (*(int (*)())camry_indirect((uint32_t)(pcVar9)))();
    }
    goto LAB_0006c8f4;
  }
  if (sVar3 == 0x1100) {
    iVar5 = (*(int (*)())camry_indirect((uint32_t)(pcVar9)))();
    if (iVar5 == 0x11) {
      if ((uVar1 < auStack_36[0]) ||
         (uVar2 = auStack_36[0] + 1, uVar7 = auStack_36[0] + 1, auStack_36[0] = uVar2, uVar1 < uVar7
         )) {
        uVar8 = 0x2200;
      }
      else {
        uVar8 = 0x11001100;
      }
      uStack_32 = 0;
    }
    else if (iVar5 == 0x22) {
      auStack_36[0] = 0;
      if (uStack_32 <= uVar2) {
        uStack_32 = uStack_32 + 1;
      }
      if (uStack_30 < uStack_32) {
        uStack_30 = uStack_32;
      }
      uVar8 = 0x22;
      if (uStack_32 <= uVar2) {
        uVar8 = 0x110011;
      }
    }
    else if ((iVar5 == 0x33) || (iVar5 == 0x44)) {
      uStack_32 = 0;
      auStack_36[0] = 0;
      uVar8 = 0;
    }
    else {
      uVar8 = 0xffff;
    }
    uVar4 = uVar8 & 0xffff;
    if (uVar4 == 0) {
      if ((uint32_t)(param_3[4]) != 0u) {
        (*(int (*)())camry_indirect((uint32_t)(param_3[4])))();
      }
    }
    else {
      if (uVar4 == 0x11) {
        if ((uint32_t)(param_3[4]) != 0u) {
          (*(int (*)())camry_indirect((uint32_t)(param_3[4])))();
        }
        if ((uint32_t)(param_3[7]) != 0u) {
          (*(int (*)())camry_indirect((uint32_t)(param_3[7])))();
        }
        pcVar9 = (code *)param_3[0xe];
      }
      else if (uVar4 == 0x22) {
        if ((uint32_t)(param_3[4]) != 0u) {
          (*(int (*)())camry_indirect((uint32_t)(param_3[4])))();
        }
        if ((uint32_t)(param_3[7]) != 0u) {
          (*(int (*)())camry_indirect((uint32_t)(param_3[7])))();
        }
        if ((uint32_t)(param_3[9]) != 0u) {
          (*(int (*)())camry_indirect((uint32_t)(param_3[9])))();
        }
        pcVar9 = (code *)param_3[0xf];
      }
      else if (uVar4 == 0x1100) {
        pcVar9 = (code *)param_3[0xc];
      }
      else {
        if (uVar4 != 0x2200) {
          if ((uint32_t)(param_3[0xc]) != 0u) {
            (*(int (*)())camry_indirect((uint32_t)(param_3[0xc])))();
          }
          uVar8 = 0x1100;
          goto LAB_0006c8f4;
        }
        if ((uint32_t)(param_3[5]) != 0u) {
          (*(int (*)())camry_indirect((uint32_t)(param_3[5])))();
        }
        pcVar9 = (code *)param_3[0xd];
      }
      if ((uint32_t)(pcVar9) != 0u) {
        (*(int (*)())camry_indirect((uint32_t)(pcVar9)))();
      }
    }
    goto LAB_0006c8f4;
  }
  if (sVar3 != 0x2200) {
    if ((uint32_t)(param_3[0x10]) != 0u) {
      (*(int (*)())camry_indirect((uint32_t)(param_3[0x10])))();
    }
    uVar8 = 0x44;
    goto LAB_0006c8f4;
  }
  iVar5 = (*(int (*)())camry_indirect((uint32_t)(pcVar9)))();
  if (iVar5 == 0x11) {
LAB_0006c460:
    uStack_32 = 0;
LAB_0006c464:
    uVar8 = 0x2200;
  }
  else {
    if (iVar5 != 0x22) {
      if ((iVar5 == 0x33) || (iVar5 == 0x44)) goto LAB_0006c460;
      goto LAB_0006c464;
    }
    auStack_36[0] = 0;
    if (uStack_32 <= uVar2) {
      uStack_32 = uStack_32 + 1;
    }
    if (uStack_30 < uStack_32) {
      uStack_30 = uStack_32;
    }
    uVar8 = 0x22;
    if (uStack_32 <= uVar2) {
      uVar8 = 0x110011;
    }
  }
  uVar4 = uVar8 & 0xffff;
  if (uVar4 == 0) {
    if ((uint32_t)(param_3[6]) != 0u) {
      (*(int (*)())camry_indirect((uint32_t)(param_3[6])))();
    }
  }
  else {
    if (uVar4 == 0x11) {
      if ((uint32_t)(param_3[6]) != 0u) {
        (*(int (*)())camry_indirect((uint32_t)(param_3[6])))();
      }
      if ((uint32_t)(param_3[7]) != 0u) {
        (*(int (*)())camry_indirect((uint32_t)(param_3[7])))();
      }
      pcVar9 = (code *)param_3[0xe];
    }
    else if (uVar4 == 0x22) {
      if ((uint32_t)(param_3[6]) != 0u) {
        (*(int (*)())camry_indirect((uint32_t)(param_3[6])))();
      }
      if ((uint32_t)(param_3[7]) != 0u) {
        (*(int (*)())camry_indirect((uint32_t)(param_3[7])))();
      }
      if ((uint32_t)(param_3[9]) != 0u) {
        (*(int (*)())camry_indirect((uint32_t)(param_3[9])))();
      }
      pcVar9 = (code *)param_3[0xf];
    }
    else {
      pcVar9 = (code *)param_3[0xd];
      if (uVar4 != 0x2200) {
        if ((uint32_t)(pcVar9) != 0u) {
          (*(int (*)())camry_indirect((uint32_t)(pcVar9)))();
        }
        uVar8 = 0x2200;
        goto LAB_0006c8f4;
      }
    }
    if ((uint32_t)(pcVar9) != 0u) {
      (*(int (*)())camry_indirect((uint32_t)(pcVar9)))();
    }
  }
LAB_0006c8f4:
  *param_1 = uVar8;
  *(ushort *)(param_1 + 1) = auStack_36[0];
  (*((ushort *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 6)))) = uStack_32;
  *(ushort *)(param_1 + 2) = uStack_30;
  (*((undefined2 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 10)))) = uStack_2c;
  *(ushort *)(param_1 + 3) = uStack_2a;
  (*((undefined2 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 0xe)))) = uStack_28;
  return 0x11;
}



/* WARNING: Type propagation algorithm not settling */

short FUN_0006c922(uint *param_1,ushort *param_2,undefined4 *param_3)

{
  ushort uVar1;
  ushort uVar2;
  short sVar3;
  uint uVar4;
  int iVar5;
  undefined4 uVar6;
  ushort uVar7;
  uint uVar8;
  code *pcVar9;
  ushort local_3c;
  ushort uStack_3a;
  ushort auStack_36 [2];
  ushort uStack_32;
  ushort uStack_30;
  undefined2 uStack_2c;
  ushort uStack_26;
  
  sVar3 = 0x11;
  if ((((((uintptr_t)(param_1)==(uintptr_t)((uint *)0x0)) || ((uintptr_t)(param_2)==(uintptr_t)((ushort *)0x0))) || ((uintptr_t)(param_3)==(uintptr_t)((undefined4 *)0x0)))
      || ((pcVar9 = (code *)*param_3,(uint32_t)(pcVar9) == 0u||
          ((uint32_t)(param_3[1]) == 0u)))) || ((uint32_t)(param_3[2]) == 0u)) {
    return 0x22;
  }
  uStack_30 = (ushort)param_1[2];
  auStack_36[0] = (ushort)param_1[1];
  uStack_32 = (*((ushort *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 6))));
  uStack_26 = (ushort)param_1[3];
  uStack_2c = (*((undefined2 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 10))));
  local_3c = param_2[2];
  uVar1 = *param_2;
  uVar2 = param_2[1];
  uStack_3a = param_2[3];
  if (uStack_32 == 0) {
    if (uVar1 < auStack_36[0]) {
      sVar3 = 0x2200;
    }
    else {
      sVar3 = 0;
      if (auStack_36[0] != 0) {
        sVar3 = 0x1100;
      }
    }
  }
  else if ((uVar2 < uStack_32) && (sVar3 = 0x44, uStack_26 <= uStack_3a)) {
    sVar3 = 0x22;
  }
  if (sVar3 == 0) {
    iVar5 = (*(int (*)())camry_indirect((uint32_t)(pcVar9)))();
    if (iVar5 == 0x11) {
      if ((uVar1 < auStack_36[0]) ||
         (uVar2 = auStack_36[0] + 1, uVar7 = auStack_36[0] + 1, auStack_36[0] = uVar2, uVar1 < uVar7
         )) {
        uVar8 = 0x2200;
      }
      else {
        uVar8 = 0x11001100;
      }
      uStack_32 = 0;
    }
    else if (iVar5 == 0x22) {
      auStack_36[0] = 0;
      if (uStack_32 <= uVar2) {
        uStack_32 = uStack_32 + 1;
      }
      if (uStack_30 < uStack_32) {
        uStack_30 = uStack_32;
      }
      uVar8 = 0x22;
      if (uStack_32 <= uVar2) {
        uVar8 = 0x110011;
      }
    }
    else if ((iVar5 == 0x33) || (iVar5 == 0x44)) {
      uStack_32 = 0;
      auStack_36[0] = 0;
      uVar8 = 0;
    }
    else {
      uVar8 = 0xffff;
    }
    uVar4 = uVar8 & 0xffff;
    if (uVar4 != 0) {
      if (uVar4 == 0x11) {
        if ((uint32_t)(param_3[7]) != 0u) {
          (*(int (*)())camry_indirect((uint32_t)(param_3[7])))();
        }
        pcVar9 = (code *)param_3[0xe];
      }
      else if (uVar4 == 0x22) {
        if ((uint32_t)(param_3[7]) != 0u) {
          (*(int (*)())camry_indirect((uint32_t)(param_3[7])))();
        }
        if ((uint32_t)(param_3[9]) != 0u) {
          (*(int (*)())camry_indirect((uint32_t)(param_3[9])))();
        }
        pcVar9 = (code *)param_3[0xf];
      }
      else if (uVar4 == 0x1100) {
        if ((uint32_t)(param_3[3]) != 0u) {
          (*(int (*)())camry_indirect((uint32_t)(param_3[3])))();
        }
        pcVar9 = (code *)param_3[0xc];
      }
      else {
        if (uVar4 != 0x2200) {
          uVar8 = 0;
          goto LAB_0006ceb8;
        }
        if ((uint32_t)(param_3[3]) != 0u) {
          (*(int (*)())camry_indirect((uint32_t)(param_3[3])))();
        }
        if ((uint32_t)(param_3[5]) != 0u) {
          (*(int (*)())camry_indirect((uint32_t)(param_3[5])))();
        }
        pcVar9 = (code *)param_3[0xd];
      }
      if ((uint32_t)(pcVar9) != 0u) {
        (*(int (*)())camry_indirect((uint32_t)(pcVar9)))();
      }
    }
    goto LAB_0006ceb8;
  }
  if (sVar3 == 0x11) {
    iVar5 = (*(int (*)())camry_indirect((uint32_t)(param_3[1])))();
    if (iVar5 == 0x11) {
      if ((uVar1 < auStack_36[0]) ||
         (uVar2 = auStack_36[0] + 1, uVar7 = auStack_36[0] + 1, auStack_36[0] = uVar2, uVar1 < uVar7
         )) {
        uVar8 = 0x2200;
      }
      else {
        uVar8 = 0x11001100;
      }
      uStack_32 = 0;
    }
    else if (iVar5 == 0x22) {
      auStack_36[0] = 0;
      if (uStack_32 <= uVar2) {
        uStack_32 = uStack_32 + 1;
      }
      if (uStack_30 < uStack_32) {
        uStack_30 = uStack_32;
      }
      uVar8 = 0x22;
      if (uStack_32 <= uVar2) {
        uVar8 = 0x110011;
      }
    }
    else if ((iVar5 == 0x33) || (iVar5 == 0x44)) {
      uStack_32 = 0;
      auStack_36[0] = 0;
      uVar8 = 0;
    }
    else {
      uVar8 = 0xffff;
    }
    uVar4 = uVar8 & 0xffff;
    if (uVar4 == 0) {
      if ((uint32_t)(param_3[8]) != 0u) {
        (*(int (*)())camry_indirect((uint32_t)(param_3[8])))();
      }
    }
    else {
      if (uVar4 == 0x11) {
        pcVar9 = (code *)param_3[0xe];
      }
      else if (uVar4 == 0x22) {
        if ((uint32_t)(param_3[9]) != 0u) {
          (*(int (*)())camry_indirect((uint32_t)(param_3[9])))();
        }
        pcVar9 = (code *)param_3[0xf];
      }
      else if (uVar4 == 0x1100) {
        if ((uint32_t)(param_3[8]) != 0u) {
          (*(int (*)())camry_indirect((uint32_t)(param_3[8])))();
        }
        if ((uint32_t)(param_3[3]) != 0u) {
          (*(int (*)())camry_indirect((uint32_t)(param_3[3])))();
        }
        pcVar9 = (code *)param_3[0xc];
      }
      else {
        if (uVar4 != 0x2200) {
          if ((uint32_t)(param_3[0xe]) != 0u) {
            (*(int (*)())camry_indirect((uint32_t)(param_3[0xe])))();
          }
          uVar8 = 0x11;
          goto LAB_0006ceb8;
        }
        if ((uint32_t)(param_3[8]) != 0u) {
          (*(int (*)())camry_indirect((uint32_t)(param_3[8])))();
        }
        if ((uint32_t)(param_3[3]) != 0u) {
          (*(int (*)())camry_indirect((uint32_t)(param_3[3])))();
        }
        if ((uint32_t)(param_3[5]) != 0u) {
          (*(int (*)())camry_indirect((uint32_t)(param_3[5])))();
        }
        pcVar9 = (code *)param_3[0xd];
      }
      if ((uint32_t)(pcVar9) != 0u) {
        (*(int (*)())camry_indirect((uint32_t)(pcVar9)))();
      }
    }
    goto LAB_0006ceb8;
  }
  if (sVar3 == 0x22) {
    uVar6 = (*(int (*)())camry_indirect((uint32_t)(param_3[2])))();
    uVar8 = FUN_00070fa4(uVar6,auStack_36,&local_3c);
    uVar4 = uVar8 & 0xffff;
    if (uVar4 == 0) {
      pcVar9 = (code *)param_3[10];
    }
    else if (uVar4 == 0x22) {
      pcVar9 = (code *)param_3[0xf];
    }
    else {
      if (uVar4 != 0x44) {
        if ((uint32_t)(param_3[0xf]) != 0u) {
          (*(int (*)())camry_indirect((uint32_t)(param_3[0xf])))();
        }
        uVar8 = 0x22;
        goto LAB_0006ceb8;
      }
      if ((uint32_t)(param_3[0xb]) != 0u) {
        (*(int (*)())camry_indirect((uint32_t)(param_3[0xb])))();
      }
      pcVar9 = (code *)param_3[0x10];
    }
    if ((uint32_t)(pcVar9) != 0u) {
      (*(int (*)())camry_indirect((uint32_t)(pcVar9)))();
    }
    goto LAB_0006ceb8;
  }
  if (sVar3 == 0x1100) {
    iVar5 = (*(int (*)())camry_indirect((uint32_t)(pcVar9)))();
    if (iVar5 == 0x11) {
      if ((uVar1 < auStack_36[0]) ||
         (uVar2 = auStack_36[0] + 1, uVar7 = auStack_36[0] + 1, auStack_36[0] = uVar2, uVar1 < uVar7
         )) {
        uVar8 = 0x2200;
      }
      else {
        uVar8 = 0x11001100;
      }
      uStack_32 = 0;
    }
    else if (iVar5 == 0x22) {
      auStack_36[0] = 0;
      if (uStack_32 <= uVar2) {
        uStack_32 = uStack_32 + 1;
      }
      if (uStack_30 < uStack_32) {
        uStack_30 = uStack_32;
      }
      uVar8 = 0x22;
      if (uStack_32 <= uVar2) {
        uVar8 = 0x110011;
      }
    }
    else if ((iVar5 == 0x33) || (iVar5 == 0x44)) {
      uStack_32 = 0;
      auStack_36[0] = 0;
      uVar8 = 0;
    }
    else {
      uVar8 = 0xffff;
    }
    uVar4 = uVar8 & 0xffff;
    if (uVar4 == 0) {
      if ((uint32_t)(param_3[4]) != 0u) {
        (*(int (*)())camry_indirect((uint32_t)(param_3[4])))();
      }
    }
    else {
      if (uVar4 == 0x11) {
        if ((uint32_t)(param_3[4]) != 0u) {
          (*(int (*)())camry_indirect((uint32_t)(param_3[4])))();
        }
        if ((uint32_t)(param_3[7]) != 0u) {
          (*(int (*)())camry_indirect((uint32_t)(param_3[7])))();
        }
        pcVar9 = (code *)param_3[0xe];
      }
      else if (uVar4 == 0x22) {
        if ((uint32_t)(param_3[4]) != 0u) {
          (*(int (*)())camry_indirect((uint32_t)(param_3[4])))();
        }
        if ((uint32_t)(param_3[7]) != 0u) {
          (*(int (*)())camry_indirect((uint32_t)(param_3[7])))();
        }
        if ((uint32_t)(param_3[9]) != 0u) {
          (*(int (*)())camry_indirect((uint32_t)(param_3[9])))();
        }
        pcVar9 = (code *)param_3[0xf];
      }
      else if (uVar4 == 0x1100) {
        pcVar9 = (code *)param_3[0xc];
      }
      else {
        if (uVar4 != 0x2200) {
          if ((uint32_t)(param_3[0xc]) != 0u) {
            (*(int (*)())camry_indirect((uint32_t)(param_3[0xc])))();
          }
          uVar8 = 0x1100;
          goto LAB_0006ceb8;
        }
        if ((uint32_t)(param_3[5]) != 0u) {
          (*(int (*)())camry_indirect((uint32_t)(param_3[5])))();
        }
        pcVar9 = (code *)param_3[0xd];
      }
      if ((uint32_t)(pcVar9) != 0u) {
        (*(int (*)())camry_indirect((uint32_t)(pcVar9)))();
      }
    }
    goto LAB_0006ceb8;
  }
  if (sVar3 != 0x2200) {
    if ((uint32_t)(param_3[0x10]) != 0u) {
      (*(int (*)())camry_indirect((uint32_t)(param_3[0x10])))();
    }
    uVar8 = 0x44;
    goto LAB_0006ceb8;
  }
  iVar5 = (*(int (*)())camry_indirect((uint32_t)(pcVar9)))();
  if (iVar5 == 0x11) {
LAB_0006ca24:
    uStack_32 = 0;
LAB_0006ca28:
    uVar8 = 0x2200;
  }
  else {
    if (iVar5 != 0x22) {
      if ((iVar5 == 0x33) || (iVar5 == 0x44)) goto LAB_0006ca24;
      goto LAB_0006ca28;
    }
    auStack_36[0] = 0;
    if (uStack_32 <= uVar2) {
      uStack_32 = uStack_32 + 1;
    }
    if (uStack_30 < uStack_32) {
      uStack_30 = uStack_32;
    }
    uVar8 = 0x22;
    if (uStack_32 <= uVar2) {
      uVar8 = 0x110011;
    }
  }
  uVar4 = uVar8 & 0xffff;
  if (uVar4 == 0) {
    if ((uint32_t)(param_3[6]) != 0u) {
      (*(int (*)())camry_indirect((uint32_t)(param_3[6])))();
    }
  }
  else {
    if (uVar4 == 0x11) {
      if ((uint32_t)(param_3[6]) != 0u) {
        (*(int (*)())camry_indirect((uint32_t)(param_3[6])))();
      }
      if ((uint32_t)(param_3[7]) != 0u) {
        (*(int (*)())camry_indirect((uint32_t)(param_3[7])))();
      }
      pcVar9 = (code *)param_3[0xe];
    }
    else if (uVar4 == 0x22) {
      if ((uint32_t)(param_3[6]) != 0u) {
        (*(int (*)())camry_indirect((uint32_t)(param_3[6])))();
      }
      if ((uint32_t)(param_3[7]) != 0u) {
        (*(int (*)())camry_indirect((uint32_t)(param_3[7])))();
      }
      if ((uint32_t)(param_3[9]) != 0u) {
        (*(int (*)())camry_indirect((uint32_t)(param_3[9])))();
      }
      pcVar9 = (code *)param_3[0xf];
    }
    else {
      pcVar9 = (code *)param_3[0xd];
      if (uVar4 != 0x2200) {
        if ((uint32_t)(pcVar9) != 0u) {
          (*(int (*)())camry_indirect((uint32_t)(pcVar9)))();
        }
        uVar8 = 0x2200;
        goto LAB_0006ceb8;
      }
    }
    if ((uint32_t)(pcVar9) != 0u) {
      (*(int (*)())camry_indirect((uint32_t)(pcVar9)))();
    }
  }
LAB_0006ceb8:
  *param_1 = uVar8;
  *(ushort *)(param_1 + 1) = auStack_36[0];
  (*((ushort *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 6)))) = uStack_32;
  *(ushort *)(param_1 + 2) = uStack_30;
  (*((undefined2 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 10)))) = uStack_2c;
  *(ushort *)(param_1 + 3) = uStack_26;
  return 0x11;
}



/* WARNING: Type propagation algorithm not settling */

undefined4 FUN_0006cee0(uint *param_1,ushort *param_2,undefined4 *param_3)

{
  ushort uVar1;
  ushort uVar2;
  ushort uVar3;
  ushort uVar4;
  ushort uVar5;
  uint uVar6;
  uint uVar7;
  int iVar8;
  undefined4 uVar9;
  uint uVar10;
  code *pcVar11;
  ushort local_44;
  ushort uStack_42;
  ushort uStack_3e;
  ushort uStack_3c;
  ushort uStack_3a;
  ushort uStack_38;
  ushort uStack_36;
  undefined2 uStack_34;
  ushort uStack_32;
  undefined2 uStack_30;
  
  uVar10 = 0x11;
  if ((((((uintptr_t)(param_1)==(uintptr_t)((uint *)0x0)) || ((uintptr_t)(param_2)==(uintptr_t)((ushort *)0x0))) || ((uintptr_t)(param_3)==(uintptr_t)((undefined4 *)0x0)))
      || ((pcVar11 = (code *)*param_3,(uint32_t)(pcVar11) == 0u||
          ((uint32_t)(param_3[1]) == 0u)))) || ((uint32_t)(param_3[2]) == 0u)) {
    return 0x22;
  }
  uStack_36 = (*((ushort *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 10))));
  uStack_3c = (*((ushort *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 6))));
  uStack_3e = (ushort)param_1[1];
  uStack_32 = (ushort)param_1[4];
  uStack_38 = (ushort)param_1[3];
  uStack_3a = (ushort)param_1[2];
  uStack_34 = (*((undefined2 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 0xe))));
  uStack_30 = (*((undefined2 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 0x12))));
  uVar2 = *param_2;
  uVar3 = param_2[1];
  uVar5 = param_2[2];
  local_44 = param_2[4];
  uVar4 = param_2[3];
  uStack_42 = param_2[5];
  if (uStack_3a == 0) {
    if (uVar2 < uStack_3e) {
      uVar6 = 0x2200;
    }
    else {
      uVar6 = 0;
      if (uStack_3e != 0) {
        uVar6 = 0x1100;
      }
    }
  }
  else {
    uVar6 = uVar10;
    if ((uVar5 < uStack_3a) && (uVar6 = 0x44, uStack_32 <= uStack_42)) {
      uVar6 = 0x22;
    }
  }
  if (uVar6 == 0) {
    iVar8 = (*(int (*)())camry_indirect((uint32_t)(pcVar11)))();
    if (iVar8 == 0x11) {
      if ((uVar3 < uStack_3c) || (uVar3 < (ushort)(uStack_3c + 1))) {
        uStack_3c = 0;
        uStack_3e = 0;
        uVar10 = 0;
      }
      else if ((uVar2 < uStack_3e) ||
              (uVar3 = uStack_3e + 1, uVar5 = uStack_3e + 1, uStack_3e = uVar3, uVar2 < uVar5)) {
        uVar10 = 0x2200;
        uStack_3c = uStack_3c + 1;
      }
      else {
        uVar10 = 0x11001100;
        uStack_3c = uStack_3c + 1;
      }
LAB_0006d2d4:
      uStack_36 = 0;
      uStack_3a = 0;
    }
    else if (iVar8 == 0x22) {
      uStack_3e = 0;
      uStack_3c = 0;
      if ((uVar4 < uStack_36) || (uVar2 = uStack_36 + 1, uVar4 < (ushort)(uStack_36 + 1))) {
        uVar10 = 0;
        goto LAB_0006d2d4;
      }
      if (uStack_3a <= uVar5) {
        uStack_3a = uStack_3a + 1;
      }
      if (uStack_38 < uStack_3a) {
        uStack_38 = uStack_3a;
      }
      uVar10 = 0x22;
      uStack_36 = uVar2;
      if (uStack_3a <= uVar5) {
        uVar10 = 0x110011;
      }
    }
    else {
      if ((iVar8 == 0x33) || (iVar8 == 0x44)) {
        uStack_3c = 0;
        uStack_3e = 0;
        uVar10 = 0;
        goto LAB_0006d2d4;
      }
      uVar10 = 0;
    }
    uVar6 = uVar10 & 0xffff;
    if (uVar6 != 0) {
      if (uVar6 == 0x11) {
        if ((uint32_t)(param_3[7]) != 0u) {
          (*(int (*)())camry_indirect((uint32_t)(param_3[7])))();
        }
        pcVar11 = (code *)param_3[0xe];
      }
      else if (uVar6 == 0x22) {
        if ((uint32_t)(param_3[7]) != 0u) {
          (*(int (*)())camry_indirect((uint32_t)(param_3[7])))();
        }
        if ((uint32_t)(param_3[9]) != 0u) {
          (*(int (*)())camry_indirect((uint32_t)(param_3[9])))();
        }
        pcVar11 = (code *)param_3[0xf];
      }
      else if (uVar6 == 0x1100) {
        if ((uint32_t)(param_3[3]) != 0u) {
          (*(int (*)())camry_indirect((uint32_t)(param_3[3])))();
        }
        pcVar11 = (code *)param_3[0xc];
      }
      else {
        if (uVar6 != 0x2200) {
          uVar10 = 0;
          goto LAB_0006d4be;
        }
        if ((uint32_t)(param_3[3]) != 0u) {
          (*(int (*)())camry_indirect((uint32_t)(param_3[3])))();
        }
        if ((uint32_t)(param_3[5]) != 0u) {
          (*(int (*)())camry_indirect((uint32_t)(param_3[5])))();
        }
        pcVar11 = (code *)param_3[0xd];
      }
      if ((uint32_t)(pcVar11) != 0u) {
        (*(int (*)())camry_indirect((uint32_t)(pcVar11)))();
      }
    }
    goto LAB_0006d4be;
  }
  if (uVar6 == 0x11) {
    iVar8 = (*(int (*)())camry_indirect((uint32_t)(param_3[1])))();
    if ((uVar4 < uStack_36) || (uVar2 = uStack_36 + 1, uVar4 < (ushort)(uStack_36 + 1))) {
LAB_0006d3de:
      uStack_36 = 0;
      uStack_3a = 0;
      uStack_3c = 0;
      uStack_3e = 0;
      uVar6 = 0;
    }
    else {
      uVar6 = uVar10;
      uStack_36 = uVar2;
      if (iVar8 == 0x11) {
LAB_0006d3a8:
        uStack_3e = 0;
        uStack_3c = 0;
      }
      else if (iVar8 == 0x22) {
        uStack_3e = 0;
        uStack_3c = 0;
        if (uStack_3a <= uVar5) {
          uStack_3a = uStack_3a + 1;
        }
        if (uStack_38 < uStack_3a) {
          uStack_38 = uStack_3a;
        }
        uVar6 = 0x22;
        if (uStack_3a <= uVar5) {
          uVar6 = 0x110011;
        }
      }
      else {
        if (iVar8 == 0x33) goto LAB_0006d3a8;
        if (iVar8 == 0x44) goto LAB_0006d3de;
      }
    }
    uVar7 = uVar6 & 0xffff;
    if (uVar7 == 0) {
      uVar10 = uVar6;
      if ((uint32_t)(param_3[8]) != 0u) {
        (*(int (*)())camry_indirect((uint32_t)(param_3[8])))();
      }
    }
    else {
      if (uVar7 == 0x11) {
        pcVar11 = (code *)param_3[0xe];
      }
      else {
        if (uVar7 != 0x22) {
          if ((uint32_t)(param_3[0xe]) != 0u) {
            (*(int (*)())camry_indirect((uint32_t)(param_3[0xe])))();
          }
          goto LAB_0006d4be;
        }
        if ((uint32_t)(param_3[9]) != 0u) {
          (*(int (*)())camry_indirect((uint32_t)(param_3[9])))();
        }
        pcVar11 = (code *)param_3[0xf];
      }
      uVar10 = uVar6;
      if ((uint32_t)(pcVar11) != 0u) {
        (*(int (*)())camry_indirect((uint32_t)(pcVar11)))();
      }
    }
    goto LAB_0006d4be;
  }
  if (uVar6 == 0x22) {
    uVar9 = (*(int (*)())camry_indirect((uint32_t)(param_3[2])))();
    uVar10 = FUN_0007110c(uVar9,&uStack_3e,&local_44);
    uVar6 = uVar10 & 0xffff;
    if (uVar6 == 0) {
      pcVar11 = (code *)param_3[10];
    }
    else if (uVar6 == 0x22) {
      pcVar11 = (code *)param_3[0xf];
    }
    else {
      if (uVar6 != 0x44) {
        if ((uint32_t)(param_3[0xf]) != 0u) {
          (*(int (*)())camry_indirect((uint32_t)(param_3[0xf])))();
        }
        uVar10 = 0x22;
        goto LAB_0006d4be;
      }
      if ((uint32_t)(param_3[0xb]) != 0u) {
        (*(int (*)())camry_indirect((uint32_t)(param_3[0xb])))();
      }
      pcVar11 = (code *)param_3[0x10];
    }
    if ((uint32_t)(pcVar11) != 0u) {
      (*(int (*)())camry_indirect((uint32_t)(pcVar11)))();
    }
    goto LAB_0006d4be;
  }
  if (uVar6 != 0x1100) {
    if (uVar6 != 0x2200) {
      if ((uint32_t)(param_3[0x10]) != 0u) {
        (*(int (*)())camry_indirect((uint32_t)(param_3[0x10])))();
      }
      uVar10 = 0x44;
      goto LAB_0006d4be;
    }
    iVar8 = (*(int (*)())camry_indirect((uint32_t)(pcVar11)))();
    if (iVar8 == 0x11) {
LAB_0006d018:
      uStack_3a = 0;
      uStack_36 = 0;
LAB_0006d01e:
      uVar10 = 0x2200;
    }
    else {
      if (iVar8 != 0x22) {
        if ((iVar8 == 0x33) || (iVar8 == 0x44)) goto LAB_0006d018;
        goto LAB_0006d01e;
      }
      uStack_3e = 0;
      uStack_3c = 0;
      if ((uVar4 < uStack_36) || (uVar2 = uStack_36 + 1, uVar4 < (ushort)(uStack_36 + 1))) {
        uStack_3a = 0;
        uVar10 = 0;
        uStack_36 = 0;
      }
      else {
        if (uStack_3a <= uVar5) {
          uStack_3a = uStack_3a + 1;
        }
        if (uStack_38 < uStack_3a) {
          uStack_38 = uStack_3a;
        }
        uVar10 = 0x22;
        uStack_36 = uVar2;
        if (uStack_3a <= uVar5) {
          uVar10 = 0x110011;
        }
      }
    }
    uVar6 = uVar10 & 0xffff;
    if (uVar6 == 0) {
      if ((uint32_t)(param_3[6]) != 0u) {
        (*(int (*)())camry_indirect((uint32_t)(param_3[6])))();
      }
    }
    else {
      if (uVar6 == 0x11) {
        if ((uint32_t)(param_3[6]) != 0u) {
          (*(int (*)())camry_indirect((uint32_t)(param_3[6])))();
        }
        if ((uint32_t)(param_3[7]) != 0u) {
          (*(int (*)())camry_indirect((uint32_t)(param_3[7])))();
        }
        pcVar11 = (code *)param_3[0xe];
      }
      else if (uVar6 == 0x22) {
        if ((uint32_t)(param_3[6]) != 0u) {
          (*(int (*)())camry_indirect((uint32_t)(param_3[6])))();
        }
        if ((uint32_t)(param_3[7]) != 0u) {
          (*(int (*)())camry_indirect((uint32_t)(param_3[7])))();
        }
        if ((uint32_t)(param_3[9]) != 0u) {
          (*(int (*)())camry_indirect((uint32_t)(param_3[9])))();
        }
        pcVar11 = (code *)param_3[0xf];
      }
      else {
        pcVar11 = (code *)param_3[0xd];
        if (uVar6 != 0x2200) {
          if ((uint32_t)(pcVar11) != 0u) {
            (*(int (*)())camry_indirect((uint32_t)(pcVar11)))();
          }
          uVar10 = 0x2200;
          goto LAB_0006d4be;
        }
      }
      if ((uint32_t)(pcVar11) != 0u) {
        (*(int (*)())camry_indirect((uint32_t)(pcVar11)))();
      }
    }
    goto LAB_0006d4be;
  }
  iVar8 = (*(int (*)())camry_indirect((uint32_t)(pcVar11)))();
  if ((uVar3 < uStack_3c) || (uVar1 = uStack_3c + 1, uVar3 < (ushort)(uStack_3c + 1))) {
LAB_0006d162:
    uStack_3c = 0;
    uStack_3e = 0;
    uVar10 = 0;
LAB_0006d16a:
    uStack_36 = 0;
    uStack_3a = 0;
  }
  else {
    uStack_3c = uVar1;
    if (iVar8 == 0x11) {
      if ((uVar2 < uStack_3e) ||
         (uVar3 = uStack_3e + 1, uVar5 = uStack_3e + 1, uStack_3e = uVar3, uVar2 < uVar5)) {
        uVar10 = 0x2200;
      }
      else {
        uVar10 = 0x11001100;
      }
      goto LAB_0006d16a;
    }
    if (iVar8 == 0x22) {
      uStack_3e = 0;
      uStack_3c = 0;
      if ((uVar4 < uStack_36) || (uVar2 = uStack_36 + 1, uVar4 < (ushort)(uStack_36 + 1))) {
        uVar10 = 0;
        goto LAB_0006d16a;
      }
      if (uStack_3a <= uVar5) {
        uStack_3a = uStack_3a + 1;
      }
      if (uStack_38 < uStack_3a) {
        uStack_38 = uStack_3a;
      }
      uVar10 = 0x22;
      uStack_36 = uVar2;
      if (uStack_3a <= uVar5) {
        uVar10 = 0x110011;
      }
    }
    else {
      if (iVar8 == 0x33) {
        uStack_3a = 0;
        uStack_36 = 0;
      }
      else if (iVar8 == 0x44) goto LAB_0006d162;
      uVar10 = 0x1100;
    }
  }
  uVar6 = uVar10 & 0xffff;
  if (uVar6 == 0) {
    if ((uint32_t)(param_3[4]) != 0u) {
      (*(int (*)())camry_indirect((uint32_t)(param_3[4])))();
    }
  }
  else {
    if (uVar6 == 0x11) {
      if ((uint32_t)(param_3[4]) != 0u) {
        (*(int (*)())camry_indirect((uint32_t)(param_3[4])))();
      }
      if ((uint32_t)(param_3[7]) != 0u) {
        (*(int (*)())camry_indirect((uint32_t)(param_3[7])))();
      }
      pcVar11 = (code *)param_3[0xe];
    }
    else if (uVar6 == 0x22) {
      if ((uint32_t)(param_3[4]) != 0u) {
        (*(int (*)())camry_indirect((uint32_t)(param_3[4])))();
      }
      if ((uint32_t)(param_3[7]) != 0u) {
        (*(int (*)())camry_indirect((uint32_t)(param_3[7])))();
      }
      if ((uint32_t)(param_3[9]) != 0u) {
        (*(int (*)())camry_indirect((uint32_t)(param_3[9])))();
      }
      pcVar11 = (code *)param_3[0xf];
    }
    else if (uVar6 == 0x1100) {
      pcVar11 = (code *)param_3[0xc];
    }
    else {
      if (uVar6 != 0x2200) {
        if ((uint32_t)(param_3[0xc]) != 0u) {
          (*(int (*)())camry_indirect((uint32_t)(param_3[0xc])))();
        }
        uVar10 = 0x1100;
        goto LAB_0006d4be;
      }
      if ((uint32_t)(param_3[5]) != 0u) {
        (*(int (*)())camry_indirect((uint32_t)(param_3[5])))();
      }
      pcVar11 = (code *)param_3[0xd];
    }
    if ((uint32_t)(pcVar11) != 0u) {
      (*(int (*)())camry_indirect((uint32_t)(pcVar11)))();
    }
  }
LAB_0006d4be:
  *param_1 = uVar10;
  *(ushort *)(param_1 + 1) = uStack_3e;
  (*((ushort *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 6)))) = uStack_3c;
  *(ushort *)(param_1 + 2) = uStack_3a;
  (*((ushort *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 10)))) = uStack_36;
  *(ushort *)(param_1 + 3) = uStack_38;
  (*((undefined2 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 0xe)))) = uStack_34;
  *(ushort *)(param_1 + 4) = uStack_32;
  (*((undefined2 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 0x12)))) = uStack_30;
  return 0x11;
}



/* WARNING: Type propagation algorithm not settling */

undefined4 FUN_0006d4f8(uint *param_1,ushort *param_2,undefined4 *param_3)

{
  ushort uVar1;
  ushort uVar2;
  ushort uVar3;
  ushort uVar4;
  ushort uVar5;
  uint uVar6;
  uint uVar7;
  int iVar8;
  undefined4 uVar9;
  uint uVar10;
  code *pcVar11;
  ushort local_44;
  ushort uStack_42;
  ushort uStack_40;
  ushort uStack_3e;
  ushort uStack_3c;
  ushort uStack_3a;
  ushort uStack_38;
  ushort uStack_36;
  undefined2 uStack_34;
  ushort uStack_32;
  undefined2 uStack_30;
  ushort uStack_2e;
  
  uVar10 = 0x11;
  if ((((((uintptr_t)(param_1)==(uintptr_t)((uint *)0x0)) || ((uintptr_t)(param_2)==(uintptr_t)((ushort *)0x0))) || ((uintptr_t)(param_3)==(uintptr_t)((undefined4 *)0x0)))
      || ((pcVar11 = (code *)*param_3,(uint32_t)(pcVar11) == 0u||
          ((uint32_t)(param_3[1]) == 0u)))) || ((uint32_t)(param_3[2]) == 0u)) {
    return 0x22;
  }
  uStack_36 = (*((ushort *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 10))));
  uStack_3c = (*((ushort *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 6))));
  uStack_3e = (ushort)param_1[1];
  uStack_32 = (ushort)param_1[4];
  uStack_38 = (ushort)param_1[3];
  uStack_3a = (ushort)param_1[2];
  uStack_2e = (*((ushort *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 0x12))));
  uStack_34 = (*((undefined2 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 0xe))));
  uStack_30 = (undefined2)param_1[5];
  uStack_42 = param_2[5];
  uVar2 = *param_2;
  local_44 = param_2[4];
  uVar3 = param_2[1];
  uVar5 = param_2[2];
  uVar4 = param_2[3];
  uStack_40 = param_2[6];
  if (uStack_3a == 0) {
    if (uVar2 < uStack_3e) {
      uVar6 = 0x2200;
    }
    else {
      uVar6 = 0;
      if (uStack_3e != 0) {
        uVar6 = 0x1100;
      }
    }
  }
  else {
    uVar6 = uVar10;
    if (uVar5 < uStack_3a) {
      if ((uStack_40 < uStack_2e) || (uStack_42 < uStack_32)) {
        uVar6 = 0x44;
      }
      else {
        uVar6 = 0x22;
      }
    }
  }
  if (uVar6 == 0) {
    iVar8 = (*(int (*)())camry_indirect((uint32_t)(pcVar11)))();
    if (iVar8 == 0x11) {
      if ((uVar3 < uStack_3c) || (uVar3 < (ushort)(uStack_3c + 1))) {
        uStack_3c = 0;
        uStack_3e = 0;
        uVar10 = 0;
      }
      else if ((uVar2 < uStack_3e) ||
              (uVar3 = uStack_3e + 1, uVar5 = uStack_3e + 1, uStack_3e = uVar3, uVar2 < uVar5)) {
        uVar10 = 0x2200;
        uStack_3c = uStack_3c + 1;
      }
      else {
        uVar10 = 0x11001100;
        uStack_3c = uStack_3c + 1;
      }
LAB_0006d8fe:
      uStack_36 = 0;
      uStack_3a = 0;
    }
    else if (iVar8 == 0x22) {
      uStack_3e = 0;
      uStack_3c = 0;
      if ((uVar4 < uStack_36) || (uVar2 = uStack_36 + 1, uVar4 < (ushort)(uStack_36 + 1))) {
        uVar10 = 0;
        goto LAB_0006d8fe;
      }
      if (uStack_3a <= uVar5) {
        uStack_3a = uStack_3a + 1;
      }
      if (uStack_38 < uStack_3a) {
        uStack_38 = uStack_3a;
      }
      uVar10 = 0x22;
      uStack_36 = uVar2;
      if (uStack_3a <= uVar5) {
        uVar10 = 0x110011;
      }
    }
    else {
      if ((iVar8 == 0x33) || (iVar8 == 0x44)) {
        uStack_3c = 0;
        uStack_3e = 0;
        uVar10 = 0;
        goto LAB_0006d8fe;
      }
      uVar10 = 0;
    }
    uVar6 = uVar10 & 0xffff;
    if (uVar6 != 0) {
      if (uVar6 == 0x11) {
        if ((uint32_t)(param_3[7]) != 0u) {
          (*(int (*)())camry_indirect((uint32_t)(param_3[7])))();
        }
        pcVar11 = (code *)param_3[0xe];
      }
      else if (uVar6 == 0x22) {
        if ((uint32_t)(param_3[7]) != 0u) {
          (*(int (*)())camry_indirect((uint32_t)(param_3[7])))();
        }
        if ((uint32_t)(param_3[9]) != 0u) {
          (*(int (*)())camry_indirect((uint32_t)(param_3[9])))();
        }
        pcVar11 = (code *)param_3[0xf];
      }
      else if (uVar6 == 0x1100) {
        if ((uint32_t)(param_3[3]) != 0u) {
          (*(int (*)())camry_indirect((uint32_t)(param_3[3])))();
        }
        pcVar11 = (code *)param_3[0xc];
      }
      else {
        if (uVar6 != 0x2200) {
          uVar10 = 0;
          goto LAB_0006dae8;
        }
        if ((uint32_t)(param_3[3]) != 0u) {
          (*(int (*)())camry_indirect((uint32_t)(param_3[3])))();
        }
        if ((uint32_t)(param_3[5]) != 0u) {
          (*(int (*)())camry_indirect((uint32_t)(param_3[5])))();
        }
        pcVar11 = (code *)param_3[0xd];
      }
      if ((uint32_t)(pcVar11) != 0u) {
        (*(int (*)())camry_indirect((uint32_t)(pcVar11)))();
      }
    }
    goto LAB_0006dae8;
  }
  if (uVar6 == 0x11) {
    iVar8 = (*(int (*)())camry_indirect((uint32_t)(param_3[1])))();
    if ((uVar4 < uStack_36) || (uVar2 = uStack_36 + 1, uVar4 < (ushort)(uStack_36 + 1))) {
LAB_0006da08:
      uStack_36 = 0;
      uStack_3a = 0;
      uStack_3c = 0;
      uStack_3e = 0;
      uVar6 = 0;
    }
    else {
      uVar6 = uVar10;
      uStack_36 = uVar2;
      if (iVar8 == 0x11) {
LAB_0006d9d2:
        uStack_3e = 0;
        uStack_3c = 0;
      }
      else if (iVar8 == 0x22) {
        uStack_3e = 0;
        uStack_3c = 0;
        if (uStack_3a <= uVar5) {
          uStack_3a = uStack_3a + 1;
        }
        if (uStack_38 < uStack_3a) {
          uStack_38 = uStack_3a;
        }
        uVar6 = 0x22;
        if (uStack_3a <= uVar5) {
          uVar6 = 0x110011;
        }
      }
      else {
        if (iVar8 == 0x33) goto LAB_0006d9d2;
        if (iVar8 == 0x44) goto LAB_0006da08;
      }
    }
    uVar7 = uVar6 & 0xffff;
    if (uVar7 == 0) {
      uVar10 = uVar6;
      if ((uint32_t)(param_3[8]) != 0u) {
        (*(int (*)())camry_indirect((uint32_t)(param_3[8])))();
      }
    }
    else {
      if (uVar7 == 0x11) {
        pcVar11 = (code *)param_3[0xe];
      }
      else {
        if (uVar7 != 0x22) {
          if ((uint32_t)(param_3[0xe]) != 0u) {
            (*(int (*)())camry_indirect((uint32_t)(param_3[0xe])))();
          }
          goto LAB_0006dae8;
        }
        if ((uint32_t)(param_3[9]) != 0u) {
          (*(int (*)())camry_indirect((uint32_t)(param_3[9])))();
        }
        pcVar11 = (code *)param_3[0xf];
      }
      uVar10 = uVar6;
      if ((uint32_t)(pcVar11) != 0u) {
        (*(int (*)())camry_indirect((uint32_t)(pcVar11)))();
      }
    }
    goto LAB_0006dae8;
  }
  if (uVar6 == 0x22) {
    uVar9 = (*(int (*)())camry_indirect((uint32_t)(param_3[2])))();
    uVar10 = FUN_00071194(uVar9,&uStack_3e,&local_44);
    uVar6 = uVar10 & 0xffff;
    if (uVar6 == 0) {
      pcVar11 = (code *)param_3[10];
    }
    else if (uVar6 == 0x22) {
      pcVar11 = (code *)param_3[0xf];
    }
    else {
      if (uVar6 != 0x44) {
        if ((uint32_t)(param_3[0xf]) != 0u) {
          (*(int (*)())camry_indirect((uint32_t)(param_3[0xf])))();
        }
        uVar10 = 0x22;
        goto LAB_0006dae8;
      }
      if ((uint32_t)(param_3[0xb]) != 0u) {
        (*(int (*)())camry_indirect((uint32_t)(param_3[0xb])))();
      }
      pcVar11 = (code *)param_3[0x10];
    }
    if ((uint32_t)(pcVar11) != 0u) {
      (*(int (*)())camry_indirect((uint32_t)(pcVar11)))();
    }
    goto LAB_0006dae8;
  }
  if (uVar6 != 0x1100) {
    if (uVar6 != 0x2200) {
      if ((uint32_t)(param_3[0x10]) != 0u) {
        (*(int (*)())camry_indirect((uint32_t)(param_3[0x10])))();
      }
      uVar10 = 0x44;
      goto LAB_0006dae8;
    }
    iVar8 = (*(int (*)())camry_indirect((uint32_t)(pcVar11)))();
    if (iVar8 == 0x11) {
LAB_0006d642:
      uStack_3a = 0;
      uStack_36 = 0;
LAB_0006d648:
      uVar10 = 0x2200;
    }
    else {
      if (iVar8 != 0x22) {
        if ((iVar8 == 0x33) || (iVar8 == 0x44)) goto LAB_0006d642;
        goto LAB_0006d648;
      }
      uStack_3e = 0;
      uStack_3c = 0;
      if ((uVar4 < uStack_36) || (uVar2 = uStack_36 + 1, uVar4 < (ushort)(uStack_36 + 1))) {
        uStack_3a = 0;
        uVar10 = 0;
        uStack_36 = 0;
      }
      else {
        if (uStack_3a <= uVar5) {
          uStack_3a = uStack_3a + 1;
        }
        if (uStack_38 < uStack_3a) {
          uStack_38 = uStack_3a;
        }
        uVar10 = 0x22;
        uStack_36 = uVar2;
        if (uStack_3a <= uVar5) {
          uVar10 = 0x110011;
        }
      }
    }
    uVar6 = uVar10 & 0xffff;
    if (uVar6 == 0) {
      if ((uint32_t)(param_3[6]) != 0u) {
        (*(int (*)())camry_indirect((uint32_t)(param_3[6])))();
      }
    }
    else {
      if (uVar6 == 0x11) {
        if ((uint32_t)(param_3[6]) != 0u) {
          (*(int (*)())camry_indirect((uint32_t)(param_3[6])))();
        }
        if ((uint32_t)(param_3[7]) != 0u) {
          (*(int (*)())camry_indirect((uint32_t)(param_3[7])))();
        }
        pcVar11 = (code *)param_3[0xe];
      }
      else if (uVar6 == 0x22) {
        if ((uint32_t)(param_3[6]) != 0u) {
          (*(int (*)())camry_indirect((uint32_t)(param_3[6])))();
        }
        if ((uint32_t)(param_3[7]) != 0u) {
          (*(int (*)())camry_indirect((uint32_t)(param_3[7])))();
        }
        if ((uint32_t)(param_3[9]) != 0u) {
          (*(int (*)())camry_indirect((uint32_t)(param_3[9])))();
        }
        pcVar11 = (code *)param_3[0xf];
      }
      else {
        pcVar11 = (code *)param_3[0xd];
        if (uVar6 != 0x2200) {
          if ((uint32_t)(pcVar11) != 0u) {
            (*(int (*)())camry_indirect((uint32_t)(pcVar11)))();
          }
          uVar10 = 0x2200;
          goto LAB_0006dae8;
        }
      }
      if ((uint32_t)(pcVar11) != 0u) {
        (*(int (*)())camry_indirect((uint32_t)(pcVar11)))();
      }
    }
    goto LAB_0006dae8;
  }
  iVar8 = (*(int (*)())camry_indirect((uint32_t)(pcVar11)))();
  if ((uVar3 < uStack_3c) || (uVar1 = uStack_3c + 1, uVar3 < (ushort)(uStack_3c + 1))) {
LAB_0006d78c:
    uStack_3c = 0;
    uStack_3e = 0;
    uVar10 = 0;
LAB_0006d794:
    uStack_36 = 0;
    uStack_3a = 0;
  }
  else {
    uStack_3c = uVar1;
    if (iVar8 == 0x11) {
      if ((uVar2 < uStack_3e) ||
         (uVar3 = uStack_3e + 1, uVar5 = uStack_3e + 1, uStack_3e = uVar3, uVar2 < uVar5)) {
        uVar10 = 0x2200;
      }
      else {
        uVar10 = 0x11001100;
      }
      goto LAB_0006d794;
    }
    if (iVar8 == 0x22) {
      uStack_3e = 0;
      uStack_3c = 0;
      if ((uVar4 < uStack_36) || (uVar2 = uStack_36 + 1, uVar4 < (ushort)(uStack_36 + 1))) {
        uVar10 = 0;
        goto LAB_0006d794;
      }
      if (uStack_3a <= uVar5) {
        uStack_3a = uStack_3a + 1;
      }
      if (uStack_38 < uStack_3a) {
        uStack_38 = uStack_3a;
      }
      uVar10 = 0x22;
      uStack_36 = uVar2;
      if (uStack_3a <= uVar5) {
        uVar10 = 0x110011;
      }
    }
    else {
      if (iVar8 == 0x33) {
        uStack_3a = 0;
        uStack_36 = 0;
      }
      else if (iVar8 == 0x44) goto LAB_0006d78c;
      uVar10 = 0x1100;
    }
  }
  uVar6 = uVar10 & 0xffff;
  if (uVar6 == 0) {
    if ((uint32_t)(param_3[4]) != 0u) {
      (*(int (*)())camry_indirect((uint32_t)(param_3[4])))();
    }
  }
  else {
    if (uVar6 == 0x11) {
      if ((uint32_t)(param_3[4]) != 0u) {
        (*(int (*)())camry_indirect((uint32_t)(param_3[4])))();
      }
      if ((uint32_t)(param_3[7]) != 0u) {
        (*(int (*)())camry_indirect((uint32_t)(param_3[7])))();
      }
      pcVar11 = (code *)param_3[0xe];
    }
    else if (uVar6 == 0x22) {
      if ((uint32_t)(param_3[4]) != 0u) {
        (*(int (*)())camry_indirect((uint32_t)(param_3[4])))();
      }
      if ((uint32_t)(param_3[7]) != 0u) {
        (*(int (*)())camry_indirect((uint32_t)(param_3[7])))();
      }
      if ((uint32_t)(param_3[9]) != 0u) {
        (*(int (*)())camry_indirect((uint32_t)(param_3[9])))();
      }
      pcVar11 = (code *)param_3[0xf];
    }
    else if (uVar6 == 0x1100) {
      pcVar11 = (code *)param_3[0xc];
    }
    else {
      if (uVar6 != 0x2200) {
        if ((uint32_t)(param_3[0xc]) != 0u) {
          (*(int (*)())camry_indirect((uint32_t)(param_3[0xc])))();
        }
        uVar10 = 0x1100;
        goto LAB_0006dae8;
      }
      if ((uint32_t)(param_3[5]) != 0u) {
        (*(int (*)())camry_indirect((uint32_t)(param_3[5])))();
      }
      pcVar11 = (code *)param_3[0xd];
    }
    if ((uint32_t)(pcVar11) != 0u) {
      (*(int (*)())camry_indirect((uint32_t)(pcVar11)))();
    }
  }
LAB_0006dae8:
  *param_1 = uVar10;
  *(ushort *)(param_1 + 1) = uStack_3e;
  (*((ushort *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 6)))) = uStack_3c;
  *(ushort *)(param_1 + 2) = uStack_3a;
  (*((ushort *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 10)))) = uStack_36;
  *(ushort *)(param_1 + 3) = uStack_38;
  (*((undefined2 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 0xe)))) = uStack_34;
  *(ushort *)(param_1 + 4) = uStack_32;
  (*((ushort *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 0x12)))) = uStack_2e;
  *(undefined2 *)(param_1 + 5) = uStack_30;
  return 0x11;
}



/* WARNING: Type propagation algorithm not settling */

undefined4 FUN_0006db28(uint *param_1,ushort *param_2,undefined4 *param_3)

{
  ushort uVar1;
  ushort uVar2;
  ushort uVar3;
  ushort uVar4;
  ushort uVar5;
  uint uVar6;
  uint uVar7;
  int iVar8;
  undefined4 uVar9;
  uint uVar10;
  code *pcVar11;
  ushort local_44;
  ushort uStack_42;
  ushort uStack_3e;
  ushort uStack_3c;
  ushort uStack_3a;
  ushort uStack_38;
  ushort uStack_36;
  undefined2 uStack_34;
  ushort uStack_32;
  undefined2 uStack_30;
  
  uVar10 = 0x11;
  if ((((((uintptr_t)(param_1)==(uintptr_t)((uint *)0x0)) || ((uintptr_t)(param_2)==(uintptr_t)((ushort *)0x0))) || ((uintptr_t)(param_3)==(uintptr_t)((undefined4 *)0x0)))
      || ((pcVar11 = (code *)*param_3,(uint32_t)(pcVar11) == 0u||
          ((uint32_t)(param_3[1]) == 0u)))) || ((uint32_t)(param_3[2]) == 0u)) {
    return 0x22;
  }
  uStack_36 = (*((ushort *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 10))));
  uStack_3c = (*((ushort *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 6))));
  uStack_3e = (ushort)param_1[1];
  uStack_32 = (ushort)param_1[4];
  uStack_38 = (ushort)param_1[3];
  uStack_3a = (ushort)param_1[2];
  uStack_34 = (*((undefined2 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 0xe))));
  uStack_30 = (*((undefined2 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 0x12))));
  uVar2 = *param_2;
  uVar3 = param_2[1];
  uVar5 = param_2[2];
  local_44 = param_2[4];
  uVar4 = param_2[3];
  uStack_42 = param_2[5];
  if (uStack_3a == 0) {
    if (uVar2 < uStack_3e) {
      uVar6 = 0x2200;
    }
    else {
      uVar6 = 0;
      if (uStack_3e != 0) {
        uVar6 = 0x1100;
      }
    }
  }
  else {
    uVar6 = uVar10;
    if ((uVar5 < uStack_3a) && (uVar6 = 0x44, uStack_32 <= uStack_42)) {
      uVar6 = 0x22;
    }
  }
  if (uVar6 == 0) {
    iVar8 = (*(int (*)())camry_indirect((uint32_t)(pcVar11)))();
    if (iVar8 == 0x11) {
      if ((uVar3 < uStack_3c) || (uVar3 < (ushort)(uStack_3c + 1))) {
        uStack_3c = 0;
        uStack_3e = 0;
        uVar10 = 0;
      }
      else if ((uVar2 < uStack_3e) ||
              (uVar3 = uStack_3e + 1, uVar5 = uStack_3e + 1, uStack_3e = uVar3, uVar2 < uVar5)) {
        uVar10 = 0x2200;
        uStack_3c = uStack_3c + 1;
      }
      else {
        uVar10 = 0x11001100;
        uStack_3c = uStack_3c + 1;
      }
LAB_0006df1c:
      uStack_36 = 0;
      uStack_3a = 0;
    }
    else if (iVar8 == 0x22) {
      uStack_3e = 0;
      uStack_3c = 0;
      if ((uVar4 < uStack_36) || (uVar2 = uStack_36 + 1, uVar4 < (ushort)(uStack_36 + 1))) {
        uVar10 = 0;
        goto LAB_0006df1c;
      }
      if (uStack_3a <= uVar5) {
        uStack_3a = uStack_3a + 1;
      }
      if (uStack_38 < uStack_3a) {
        uStack_38 = uStack_3a;
      }
      uVar10 = 0x22;
      uStack_36 = uVar2;
      if (uStack_3a <= uVar5) {
        uVar10 = 0x110011;
      }
    }
    else {
      if ((iVar8 == 0x33) || (iVar8 == 0x44)) {
        uStack_3c = 0;
        uStack_3e = 0;
        uVar10 = 0;
        goto LAB_0006df1c;
      }
      uVar10 = 0;
    }
    uVar6 = uVar10 & 0xffff;
    if (uVar6 != 0) {
      if (uVar6 == 0x11) {
        if ((uint32_t)(param_3[7]) != 0u) {
          (*(int (*)())camry_indirect((uint32_t)(param_3[7])))();
        }
        pcVar11 = (code *)param_3[0xe];
      }
      else if (uVar6 == 0x22) {
        if ((uint32_t)(param_3[7]) != 0u) {
          (*(int (*)())camry_indirect((uint32_t)(param_3[7])))();
        }
        if ((uint32_t)(param_3[9]) != 0u) {
          (*(int (*)())camry_indirect((uint32_t)(param_3[9])))();
        }
        pcVar11 = (code *)param_3[0xf];
      }
      else if (uVar6 == 0x1100) {
        if ((uint32_t)(param_3[3]) != 0u) {
          (*(int (*)())camry_indirect((uint32_t)(param_3[3])))();
        }
        pcVar11 = (code *)param_3[0xc];
      }
      else {
        if (uVar6 != 0x2200) {
          uVar10 = 0;
          goto LAB_0006e106;
        }
        if ((uint32_t)(param_3[3]) != 0u) {
          (*(int (*)())camry_indirect((uint32_t)(param_3[3])))();
        }
        if ((uint32_t)(param_3[5]) != 0u) {
          (*(int (*)())camry_indirect((uint32_t)(param_3[5])))();
        }
        pcVar11 = (code *)param_3[0xd];
      }
      if ((uint32_t)(pcVar11) != 0u) {
        (*(int (*)())camry_indirect((uint32_t)(pcVar11)))();
      }
    }
    goto LAB_0006e106;
  }
  if (uVar6 == 0x11) {
    iVar8 = (*(int (*)())camry_indirect((uint32_t)(param_3[1])))();
    if ((uVar4 < uStack_36) || (uVar2 = uStack_36 + 1, uVar4 < (ushort)(uStack_36 + 1))) {
LAB_0006e026:
      uStack_36 = 0;
      uStack_3a = 0;
      uStack_3c = 0;
      uStack_3e = 0;
      uVar6 = 0;
    }
    else {
      uVar6 = uVar10;
      uStack_36 = uVar2;
      if (iVar8 == 0x11) {
LAB_0006dff0:
        uStack_3e = 0;
        uStack_3c = 0;
      }
      else if (iVar8 == 0x22) {
        uStack_3e = 0;
        uStack_3c = 0;
        if (uStack_3a <= uVar5) {
          uStack_3a = uStack_3a + 1;
        }
        if (uStack_38 < uStack_3a) {
          uStack_38 = uStack_3a;
        }
        uVar6 = 0x22;
        if (uStack_3a <= uVar5) {
          uVar6 = 0x110011;
        }
      }
      else {
        if (iVar8 == 0x33) goto LAB_0006dff0;
        if (iVar8 == 0x44) goto LAB_0006e026;
      }
    }
    uVar7 = uVar6 & 0xffff;
    if (uVar7 == 0) {
      uVar10 = uVar6;
      if ((uint32_t)(param_3[8]) != 0u) {
        (*(int (*)())camry_indirect((uint32_t)(param_3[8])))();
      }
    }
    else {
      if (uVar7 == 0x11) {
        pcVar11 = (code *)param_3[0xe];
      }
      else {
        if (uVar7 != 0x22) {
          if ((uint32_t)(param_3[0xe]) != 0u) {
            (*(int (*)())camry_indirect((uint32_t)(param_3[0xe])))();
          }
          goto LAB_0006e106;
        }
        if ((uint32_t)(param_3[9]) != 0u) {
          (*(int (*)())camry_indirect((uint32_t)(param_3[9])))();
        }
        pcVar11 = (code *)param_3[0xf];
      }
      uVar10 = uVar6;
      if ((uint32_t)(pcVar11) != 0u) {
        (*(int (*)())camry_indirect((uint32_t)(pcVar11)))();
      }
    }
    goto LAB_0006e106;
  }
  if (uVar6 == 0x22) {
    uVar9 = (*(int (*)())camry_indirect((uint32_t)(param_3[2])))();
    uVar10 = FUN_00071086(uVar9,&uStack_3e,&local_44);
    uVar6 = uVar10 & 0xffff;
    if (uVar6 == 0) {
      pcVar11 = (code *)param_3[10];
    }
    else if (uVar6 == 0x22) {
      pcVar11 = (code *)param_3[0xf];
    }
    else {
      if (uVar6 != 0x44) {
        if ((uint32_t)(param_3[0xf]) != 0u) {
          (*(int (*)())camry_indirect((uint32_t)(param_3[0xf])))();
        }
        uVar10 = 0x22;
        goto LAB_0006e106;
      }
      if ((uint32_t)(param_3[0xb]) != 0u) {
        (*(int (*)())camry_indirect((uint32_t)(param_3[0xb])))();
      }
      pcVar11 = (code *)param_3[0x10];
    }
    if ((uint32_t)(pcVar11) != 0u) {
      (*(int (*)())camry_indirect((uint32_t)(pcVar11)))();
    }
    goto LAB_0006e106;
  }
  if (uVar6 != 0x1100) {
    if (uVar6 != 0x2200) {
      if ((uint32_t)(param_3[0x10]) != 0u) {
        (*(int (*)())camry_indirect((uint32_t)(param_3[0x10])))();
      }
      uVar10 = 0x44;
      goto LAB_0006e106;
    }
    iVar8 = (*(int (*)())camry_indirect((uint32_t)(pcVar11)))();
    if (iVar8 == 0x11) {
LAB_0006dc60:
      uStack_3a = 0;
      uStack_36 = 0;
LAB_0006dc66:
      uVar10 = 0x2200;
    }
    else {
      if (iVar8 != 0x22) {
        if ((iVar8 == 0x33) || (iVar8 == 0x44)) goto LAB_0006dc60;
        goto LAB_0006dc66;
      }
      uStack_3e = 0;
      uStack_3c = 0;
      if ((uVar4 < uStack_36) || (uVar2 = uStack_36 + 1, uVar4 < (ushort)(uStack_36 + 1))) {
        uStack_3a = 0;
        uVar10 = 0;
        uStack_36 = 0;
      }
      else {
        if (uStack_3a <= uVar5) {
          uStack_3a = uStack_3a + 1;
        }
        if (uStack_38 < uStack_3a) {
          uStack_38 = uStack_3a;
        }
        uVar10 = 0x22;
        uStack_36 = uVar2;
        if (uStack_3a <= uVar5) {
          uVar10 = 0x110011;
        }
      }
    }
    uVar6 = uVar10 & 0xffff;
    if (uVar6 == 0) {
      if ((uint32_t)(param_3[6]) != 0u) {
        (*(int (*)())camry_indirect((uint32_t)(param_3[6])))();
      }
    }
    else {
      if (uVar6 == 0x11) {
        if ((uint32_t)(param_3[6]) != 0u) {
          (*(int (*)())camry_indirect((uint32_t)(param_3[6])))();
        }
        if ((uint32_t)(param_3[7]) != 0u) {
          (*(int (*)())camry_indirect((uint32_t)(param_3[7])))();
        }
        pcVar11 = (code *)param_3[0xe];
      }
      else if (uVar6 == 0x22) {
        if ((uint32_t)(param_3[6]) != 0u) {
          (*(int (*)())camry_indirect((uint32_t)(param_3[6])))();
        }
        if ((uint32_t)(param_3[7]) != 0u) {
          (*(int (*)())camry_indirect((uint32_t)(param_3[7])))();
        }
        if ((uint32_t)(param_3[9]) != 0u) {
          (*(int (*)())camry_indirect((uint32_t)(param_3[9])))();
        }
        pcVar11 = (code *)param_3[0xf];
      }
      else {
        pcVar11 = (code *)param_3[0xd];
        if (uVar6 != 0x2200) {
          if ((uint32_t)(pcVar11) != 0u) {
            (*(int (*)())camry_indirect((uint32_t)(pcVar11)))();
          }
          uVar10 = 0x2200;
          goto LAB_0006e106;
        }
      }
      if ((uint32_t)(pcVar11) != 0u) {
        (*(int (*)())camry_indirect((uint32_t)(pcVar11)))();
      }
    }
    goto LAB_0006e106;
  }
  iVar8 = (*(int (*)())camry_indirect((uint32_t)(pcVar11)))();
  if ((uVar3 < uStack_3c) || (uVar1 = uStack_3c + 1, uVar3 < (ushort)(uStack_3c + 1))) {
LAB_0006ddaa:
    uStack_3c = 0;
    uStack_3e = 0;
    uVar10 = 0;
LAB_0006ddb2:
    uStack_36 = 0;
    uStack_3a = 0;
  }
  else {
    uStack_3c = uVar1;
    if (iVar8 == 0x11) {
      if ((uVar2 < uStack_3e) ||
         (uVar3 = uStack_3e + 1, uVar5 = uStack_3e + 1, uStack_3e = uVar3, uVar2 < uVar5)) {
        uVar10 = 0x2200;
      }
      else {
        uVar10 = 0x11001100;
      }
      goto LAB_0006ddb2;
    }
    if (iVar8 == 0x22) {
      uStack_3e = 0;
      uStack_3c = 0;
      if ((uVar4 < uStack_36) || (uVar2 = uStack_36 + 1, uVar4 < (ushort)(uStack_36 + 1))) {
        uVar10 = 0;
        goto LAB_0006ddb2;
      }
      if (uStack_3a <= uVar5) {
        uStack_3a = uStack_3a + 1;
      }
      if (uStack_38 < uStack_3a) {
        uStack_38 = uStack_3a;
      }
      uVar10 = 0x22;
      uStack_36 = uVar2;
      if (uStack_3a <= uVar5) {
        uVar10 = 0x110011;
      }
    }
    else {
      if (iVar8 == 0x33) {
        uStack_3a = 0;
        uStack_36 = 0;
      }
      else if (iVar8 == 0x44) goto LAB_0006ddaa;
      uVar10 = 0x1100;
    }
  }
  uVar6 = uVar10 & 0xffff;
  if (uVar6 == 0) {
    if ((uint32_t)(param_3[4]) != 0u) {
      (*(int (*)())camry_indirect((uint32_t)(param_3[4])))();
    }
  }
  else {
    if (uVar6 == 0x11) {
      if ((uint32_t)(param_3[4]) != 0u) {
        (*(int (*)())camry_indirect((uint32_t)(param_3[4])))();
      }
      if ((uint32_t)(param_3[7]) != 0u) {
        (*(int (*)())camry_indirect((uint32_t)(param_3[7])))();
      }
      pcVar11 = (code *)param_3[0xe];
    }
    else if (uVar6 == 0x22) {
      if ((uint32_t)(param_3[4]) != 0u) {
        (*(int (*)())camry_indirect((uint32_t)(param_3[4])))();
      }
      if ((uint32_t)(param_3[7]) != 0u) {
        (*(int (*)())camry_indirect((uint32_t)(param_3[7])))();
      }
      if ((uint32_t)(param_3[9]) != 0u) {
        (*(int (*)())camry_indirect((uint32_t)(param_3[9])))();
      }
      pcVar11 = (code *)param_3[0xf];
    }
    else if (uVar6 == 0x1100) {
      pcVar11 = (code *)param_3[0xc];
    }
    else {
      if (uVar6 != 0x2200) {
        if ((uint32_t)(param_3[0xc]) != 0u) {
          (*(int (*)())camry_indirect((uint32_t)(param_3[0xc])))();
        }
        uVar10 = 0x1100;
        goto LAB_0006e106;
      }
      if ((uint32_t)(param_3[5]) != 0u) {
        (*(int (*)())camry_indirect((uint32_t)(param_3[5])))();
      }
      pcVar11 = (code *)param_3[0xd];
    }
    if ((uint32_t)(pcVar11) != 0u) {
      (*(int (*)())camry_indirect((uint32_t)(pcVar11)))();
    }
  }
LAB_0006e106:
  *param_1 = uVar10;
  *(ushort *)(param_1 + 1) = uStack_3e;
  (*((ushort *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 6)))) = uStack_3c;
  *(ushort *)(param_1 + 2) = uStack_3a;
  (*((ushort *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 10)))) = uStack_36;
  *(ushort *)(param_1 + 3) = uStack_38;
  (*((undefined2 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 0xe)))) = uStack_34;
  *(ushort *)(param_1 + 4) = uStack_32;
  (*((undefined2 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 0x12)))) = uStack_30;
  return 0x11;
}



/* WARNING: Type propagation algorithm not settling */

undefined4 FUN_0006e140(uint *param_1,ushort *param_2,undefined4 *param_3)

{
  ushort uVar1;
  ushort uVar2;
  ushort uVar3;
  ushort uVar4;
  ushort uVar5;
  uint uVar6;
  uint uVar7;
  int iVar8;
  undefined4 uVar9;
  uint uVar10;
  code *pcVar11;
  ushort local_44;
  ushort uStack_42;
  ushort uStack_3e;
  ushort uStack_3c;
  ushort uStack_3a;
  ushort uStack_38;
  ushort uStack_36;
  undefined2 uStack_34;
  ushort uStack_2e;
  
  uVar10 = 0x11;
  if ((((((uintptr_t)(param_1)==(uintptr_t)((uint *)0x0)) || ((uintptr_t)(param_2)==(uintptr_t)((ushort *)0x0))) || ((uintptr_t)(param_3)==(uintptr_t)((undefined4 *)0x0)))
      || ((pcVar11 = (code *)*param_3,(uint32_t)(pcVar11) == 0u||
          ((uint32_t)(param_3[1]) == 0u)))) || ((uint32_t)(param_3[2]) == 0u)) {
    return 0x22;
  }
  uStack_36 = (*((ushort *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 10))));
  uStack_3c = (*((ushort *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 6))));
  uStack_3e = (ushort)param_1[1];
  uStack_2e = (ushort)param_1[4];
  uStack_38 = (ushort)param_1[3];
  uStack_3a = (ushort)param_1[2];
  uStack_34 = (*((undefined2 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 0xe))));
  uVar2 = *param_2;
  local_44 = param_2[4];
  uVar3 = param_2[1];
  uVar5 = param_2[2];
  uVar4 = param_2[3];
  uStack_42 = param_2[5];
  if (uStack_3a == 0) {
    if (uVar2 < uStack_3e) {
      uVar6 = 0x2200;
    }
    else {
      uVar6 = 0;
      if (uStack_3e != 0) {
        uVar6 = 0x1100;
      }
    }
  }
  else {
    uVar6 = uVar10;
    if ((uVar5 < uStack_3a) && (uVar6 = 0x44, uStack_2e <= uStack_42)) {
      uVar6 = 0x22;
    }
  }
  if (uVar6 == 0) {
    iVar8 = (*(int (*)())camry_indirect((uint32_t)(pcVar11)))();
    if (iVar8 == 0x11) {
      if ((uVar3 < uStack_3c) || (uVar3 < (ushort)(uStack_3c + 1))) {
        uStack_3c = 0;
        uStack_3e = 0;
        uVar10 = 0;
      }
      else if ((uVar2 < uStack_3e) ||
              (uVar3 = uStack_3e + 1, uVar5 = uStack_3e + 1, uStack_3e = uVar3, uVar2 < uVar5)) {
        uVar10 = 0x2200;
        uStack_3c = uStack_3c + 1;
      }
      else {
        uVar10 = 0x11001100;
        uStack_3c = uStack_3c + 1;
      }
LAB_0006e52e:
      uStack_36 = 0;
      uStack_3a = 0;
    }
    else if (iVar8 == 0x22) {
      uStack_3e = 0;
      uStack_3c = 0;
      if ((uVar4 < uStack_36) || (uVar2 = uStack_36 + 1, uVar4 < (ushort)(uStack_36 + 1))) {
        uVar10 = 0;
        goto LAB_0006e52e;
      }
      if (uStack_3a <= uVar5) {
        uStack_3a = uStack_3a + 1;
      }
      if (uStack_38 < uStack_3a) {
        uStack_38 = uStack_3a;
      }
      uVar10 = 0x22;
      uStack_36 = uVar2;
      if (uStack_3a <= uVar5) {
        uVar10 = 0x110011;
      }
    }
    else {
      if ((iVar8 == 0x33) || (iVar8 == 0x44)) {
        uStack_3c = 0;
        uStack_3e = 0;
        uVar10 = 0;
        goto LAB_0006e52e;
      }
      uVar10 = 0;
    }
    uVar6 = uVar10 & 0xffff;
    if (uVar6 != 0) {
      if (uVar6 == 0x11) {
        if ((uint32_t)(param_3[7]) != 0u) {
          (*(int (*)())camry_indirect((uint32_t)(param_3[7])))();
        }
        pcVar11 = (code *)param_3[0xe];
      }
      else if (uVar6 == 0x22) {
        if ((uint32_t)(param_3[7]) != 0u) {
          (*(int (*)())camry_indirect((uint32_t)(param_3[7])))();
        }
        if ((uint32_t)(param_3[9]) != 0u) {
          (*(int (*)())camry_indirect((uint32_t)(param_3[9])))();
        }
        pcVar11 = (code *)param_3[0xf];
      }
      else if (uVar6 == 0x1100) {
        if ((uint32_t)(param_3[3]) != 0u) {
          (*(int (*)())camry_indirect((uint32_t)(param_3[3])))();
        }
        pcVar11 = (code *)param_3[0xc];
      }
      else {
        if (uVar6 != 0x2200) {
          uVar10 = 0;
          goto LAB_0006e718;
        }
        if ((uint32_t)(param_3[3]) != 0u) {
          (*(int (*)())camry_indirect((uint32_t)(param_3[3])))();
        }
        if ((uint32_t)(param_3[5]) != 0u) {
          (*(int (*)())camry_indirect((uint32_t)(param_3[5])))();
        }
        pcVar11 = (code *)param_3[0xd];
      }
      if ((uint32_t)(pcVar11) != 0u) {
        (*(int (*)())camry_indirect((uint32_t)(pcVar11)))();
      }
    }
    goto LAB_0006e718;
  }
  if (uVar6 == 0x11) {
    iVar8 = (*(int (*)())camry_indirect((uint32_t)(param_3[1])))();
    if ((uVar4 < uStack_36) || (uVar2 = uStack_36 + 1, uVar4 < (ushort)(uStack_36 + 1))) {
LAB_0006e638:
      uStack_36 = 0;
      uStack_3a = 0;
      uStack_3c = 0;
      uStack_3e = 0;
      uVar6 = 0;
    }
    else {
      uVar6 = uVar10;
      uStack_36 = uVar2;
      if (iVar8 == 0x11) {
LAB_0006e602:
        uStack_3e = 0;
        uStack_3c = 0;
      }
      else if (iVar8 == 0x22) {
        uStack_3e = 0;
        uStack_3c = 0;
        if (uStack_3a <= uVar5) {
          uStack_3a = uStack_3a + 1;
        }
        if (uStack_38 < uStack_3a) {
          uStack_38 = uStack_3a;
        }
        uVar6 = 0x22;
        if (uStack_3a <= uVar5) {
          uVar6 = 0x110011;
        }
      }
      else {
        if (iVar8 == 0x33) goto LAB_0006e602;
        if (iVar8 == 0x44) goto LAB_0006e638;
      }
    }
    uVar7 = uVar6 & 0xffff;
    if (uVar7 == 0) {
      uVar10 = uVar6;
      if ((uint32_t)(param_3[8]) != 0u) {
        (*(int (*)())camry_indirect((uint32_t)(param_3[8])))();
      }
    }
    else {
      if (uVar7 == 0x11) {
        pcVar11 = (code *)param_3[0xe];
      }
      else {
        if (uVar7 != 0x22) {
          if ((uint32_t)(param_3[0xe]) != 0u) {
            (*(int (*)())camry_indirect((uint32_t)(param_3[0xe])))();
          }
          goto LAB_0006e718;
        }
        if ((uint32_t)(param_3[9]) != 0u) {
          (*(int (*)())camry_indirect((uint32_t)(param_3[9])))();
        }
        pcVar11 = (code *)param_3[0xf];
      }
      uVar10 = uVar6;
      if ((uint32_t)(pcVar11) != 0u) {
        (*(int (*)())camry_indirect((uint32_t)(pcVar11)))();
      }
    }
    goto LAB_0006e718;
  }
  if (uVar6 == 0x22) {
    uVar9 = (*(int (*)())camry_indirect((uint32_t)(param_3[2])))();
    uVar10 = FUN_00071014(uVar9,&uStack_3e,&local_44);
    uVar6 = uVar10 & 0xffff;
    if (uVar6 == 0) {
      pcVar11 = (code *)param_3[10];
    }
    else if (uVar6 == 0x22) {
      pcVar11 = (code *)param_3[0xf];
    }
    else {
      if (uVar6 != 0x44) {
        if ((uint32_t)(param_3[0xf]) != 0u) {
          (*(int (*)())camry_indirect((uint32_t)(param_3[0xf])))();
        }
        uVar10 = 0x22;
        goto LAB_0006e718;
      }
      if ((uint32_t)(param_3[0xb]) != 0u) {
        (*(int (*)())camry_indirect((uint32_t)(param_3[0xb])))();
      }
      pcVar11 = (code *)param_3[0x10];
    }
    if ((uint32_t)(pcVar11) != 0u) {
      (*(int (*)())camry_indirect((uint32_t)(pcVar11)))();
    }
    goto LAB_0006e718;
  }
  if (uVar6 != 0x1100) {
    if (uVar6 != 0x2200) {
      if ((uint32_t)(param_3[0x10]) != 0u) {
        (*(int (*)())camry_indirect((uint32_t)(param_3[0x10])))();
      }
      uVar10 = 0x44;
      goto LAB_0006e718;
    }
    iVar8 = (*(int (*)())camry_indirect((uint32_t)(pcVar11)))();
    if (iVar8 == 0x11) {
LAB_0006e272:
      uStack_3a = 0;
      uStack_36 = 0;
LAB_0006e278:
      uVar10 = 0x2200;
    }
    else {
      if (iVar8 != 0x22) {
        if ((iVar8 == 0x33) || (iVar8 == 0x44)) goto LAB_0006e272;
        goto LAB_0006e278;
      }
      uStack_3e = 0;
      uStack_3c = 0;
      if ((uVar4 < uStack_36) || (uVar2 = uStack_36 + 1, uVar4 < (ushort)(uStack_36 + 1))) {
        uStack_3a = 0;
        uVar10 = 0;
        uStack_36 = 0;
      }
      else {
        if (uStack_3a <= uVar5) {
          uStack_3a = uStack_3a + 1;
        }
        if (uStack_38 < uStack_3a) {
          uStack_38 = uStack_3a;
        }
        uVar10 = 0x22;
        uStack_36 = uVar2;
        if (uStack_3a <= uVar5) {
          uVar10 = 0x110011;
        }
      }
    }
    uVar6 = uVar10 & 0xffff;
    if (uVar6 == 0) {
      if ((uint32_t)(param_3[6]) != 0u) {
        (*(int (*)())camry_indirect((uint32_t)(param_3[6])))();
      }
    }
    else {
      if (uVar6 == 0x11) {
        if ((uint32_t)(param_3[6]) != 0u) {
          (*(int (*)())camry_indirect((uint32_t)(param_3[6])))();
        }
        if ((uint32_t)(param_3[7]) != 0u) {
          (*(int (*)())camry_indirect((uint32_t)(param_3[7])))();
        }
        pcVar11 = (code *)param_3[0xe];
      }
      else if (uVar6 == 0x22) {
        if ((uint32_t)(param_3[6]) != 0u) {
          (*(int (*)())camry_indirect((uint32_t)(param_3[6])))();
        }
        if ((uint32_t)(param_3[7]) != 0u) {
          (*(int (*)())camry_indirect((uint32_t)(param_3[7])))();
        }
        if ((uint32_t)(param_3[9]) != 0u) {
          (*(int (*)())camry_indirect((uint32_t)(param_3[9])))();
        }
        pcVar11 = (code *)param_3[0xf];
      }
      else {
        pcVar11 = (code *)param_3[0xd];
        if (uVar6 != 0x2200) {
          if ((uint32_t)(pcVar11) != 0u) {
            (*(int (*)())camry_indirect((uint32_t)(pcVar11)))();
          }
          uVar10 = 0x2200;
          goto LAB_0006e718;
        }
      }
      if ((uint32_t)(pcVar11) != 0u) {
        (*(int (*)())camry_indirect((uint32_t)(pcVar11)))();
      }
    }
    goto LAB_0006e718;
  }
  iVar8 = (*(int (*)())camry_indirect((uint32_t)(pcVar11)))();
  if ((uVar3 < uStack_3c) || (uVar1 = uStack_3c + 1, uVar3 < (ushort)(uStack_3c + 1))) {
LAB_0006e3bc:
    uStack_3c = 0;
    uStack_3e = 0;
    uVar10 = 0;
LAB_0006e3c4:
    uStack_36 = 0;
    uStack_3a = 0;
  }
  else {
    uStack_3c = uVar1;
    if (iVar8 == 0x11) {
      if ((uVar2 < uStack_3e) ||
         (uVar3 = uStack_3e + 1, uVar5 = uStack_3e + 1, uStack_3e = uVar3, uVar2 < uVar5)) {
        uVar10 = 0x2200;
      }
      else {
        uVar10 = 0x11001100;
      }
      goto LAB_0006e3c4;
    }
    if (iVar8 == 0x22) {
      uStack_3e = 0;
      uStack_3c = 0;
      if ((uVar4 < uStack_36) || (uVar2 = uStack_36 + 1, uVar4 < (ushort)(uStack_36 + 1))) {
        uVar10 = 0;
        goto LAB_0006e3c4;
      }
      if (uStack_3a <= uVar5) {
        uStack_3a = uStack_3a + 1;
      }
      if (uStack_38 < uStack_3a) {
        uStack_38 = uStack_3a;
      }
      uVar10 = 0x22;
      uStack_36 = uVar2;
      if (uStack_3a <= uVar5) {
        uVar10 = 0x110011;
      }
    }
    else {
      if (iVar8 == 0x33) {
        uStack_3a = 0;
        uStack_36 = 0;
      }
      else if (iVar8 == 0x44) goto LAB_0006e3bc;
      uVar10 = 0x1100;
    }
  }
  uVar6 = uVar10 & 0xffff;
  if (uVar6 == 0) {
    if ((uint32_t)(param_3[4]) != 0u) {
      (*(int (*)())camry_indirect((uint32_t)(param_3[4])))();
    }
  }
  else {
    if (uVar6 == 0x11) {
      if ((uint32_t)(param_3[4]) != 0u) {
        (*(int (*)())camry_indirect((uint32_t)(param_3[4])))();
      }
      if ((uint32_t)(param_3[7]) != 0u) {
        (*(int (*)())camry_indirect((uint32_t)(param_3[7])))();
      }
      pcVar11 = (code *)param_3[0xe];
    }
    else if (uVar6 == 0x22) {
      if ((uint32_t)(param_3[4]) != 0u) {
        (*(int (*)())camry_indirect((uint32_t)(param_3[4])))();
      }
      if ((uint32_t)(param_3[7]) != 0u) {
        (*(int (*)())camry_indirect((uint32_t)(param_3[7])))();
      }
      if ((uint32_t)(param_3[9]) != 0u) {
        (*(int (*)())camry_indirect((uint32_t)(param_3[9])))();
      }
      pcVar11 = (code *)param_3[0xf];
    }
    else if (uVar6 == 0x1100) {
      pcVar11 = (code *)param_3[0xc];
    }
    else {
      if (uVar6 != 0x2200) {
        if ((uint32_t)(param_3[0xc]) != 0u) {
          (*(int (*)())camry_indirect((uint32_t)(param_3[0xc])))();
        }
        uVar10 = 0x1100;
        goto LAB_0006e718;
      }
      if ((uint32_t)(param_3[5]) != 0u) {
        (*(int (*)())camry_indirect((uint32_t)(param_3[5])))();
      }
      pcVar11 = (code *)param_3[0xd];
    }
    if ((uint32_t)(pcVar11) != 0u) {
      (*(int (*)())camry_indirect((uint32_t)(pcVar11)))();
    }
  }
LAB_0006e718:
  *param_1 = uVar10;
  *(ushort *)(param_1 + 1) = uStack_3e;
  (*((ushort *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 6)))) = uStack_3c;
  *(ushort *)(param_1 + 2) = uStack_3a;
  (*((ushort *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 10)))) = uStack_36;
  *(ushort *)(param_1 + 3) = uStack_38;
  (*((undefined2 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 0xe)))) = uStack_34;
  *(ushort *)(param_1 + 4) = uStack_2e;
  return 0x11;
}



/* WARNING: Type propagation algorithm not settling */

undefined4 FUN_0006e74c(uint *param_1,ushort *param_2,undefined4 *param_3)

{
  ushort uVar1;
  ushort uVar2;
  ushort uVar3;
  ushort uVar4;
  ushort uVar5;
  uint uVar6;
  uint uVar7;
  int iVar8;
  undefined4 uVar9;
  uint uVar10;
  code *pcVar11;
  ushort local_44;
  ushort uStack_42;
  ushort uStack_3e;
  ushort uStack_3c;
  ushort uStack_3a;
  ushort uStack_38;
  ushort uStack_36;
  undefined2 uStack_34;
  ushort uStack_32;
  undefined2 uStack_30;
  
  uVar10 = 0x11;
  if ((((((uintptr_t)(param_1)==(uintptr_t)((uint *)0x0)) || ((uintptr_t)(param_2)==(uintptr_t)((ushort *)0x0))) || ((uintptr_t)(param_3)==(uintptr_t)((undefined4 *)0x0)))
      || ((pcVar11 = (code *)*param_3,(uint32_t)(pcVar11) == 0u||
          ((uint32_t)(param_3[1]) == 0u)))) || ((uint32_t)(param_3[2]) == 0u)) {
    return 0x22;
  }
  uStack_36 = (*((ushort *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 10))));
  uStack_3c = (*((ushort *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 6))));
  uStack_3e = (ushort)param_1[1];
  uStack_32 = (ushort)param_1[4];
  uStack_38 = (ushort)param_1[3];
  uStack_3a = (ushort)param_1[2];
  uStack_34 = (*((undefined2 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 0xe))));
  uStack_30 = (*((undefined2 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 0x12))));
  uVar2 = *param_2;
  uVar3 = param_2[1];
  uVar5 = param_2[2];
  local_44 = param_2[4];
  uVar4 = param_2[3];
  uStack_42 = param_2[5];
  if (uStack_3a == 0) {
    if (uVar2 < uStack_3e) {
      uVar6 = 0x2200;
    }
    else {
      uVar6 = 0;
      if (uStack_3e != 0) {
        uVar6 = 0x1100;
      }
    }
  }
  else {
    uVar6 = uVar10;
    if ((uVar5 < uStack_3a) && (uVar6 = 0x44, uStack_32 <= uStack_42)) {
      uVar6 = 0x22;
    }
  }
  if (uVar6 == 0) {
    iVar8 = (*(int (*)())camry_indirect((uint32_t)(pcVar11)))();
    if (iVar8 == 0x11) {
      if ((uVar3 < uStack_3c) || (uVar3 < (ushort)(uStack_3c + 1))) {
        uStack_3c = 0;
        uStack_3e = 0;
        uVar10 = 0;
      }
      else if ((uVar2 < uStack_3e) ||
              (uVar3 = uStack_3e + 1, uVar5 = uStack_3e + 1, uStack_3e = uVar3, uVar2 < uVar5)) {
        uVar10 = 0x2200;
        uStack_3c = uStack_3c + 1;
      }
      else {
        uVar10 = 0x11001100;
        uStack_3c = uStack_3c + 1;
      }
LAB_0006eb40:
      uStack_36 = 0;
      uStack_3a = 0;
    }
    else if (iVar8 == 0x22) {
      uStack_3e = 0;
      uStack_3c = 0;
      if ((uVar4 < uStack_36) || (uVar2 = uStack_36 + 1, uVar4 < (ushort)(uStack_36 + 1))) {
        uVar10 = 0;
        goto LAB_0006eb40;
      }
      if (uStack_3a <= uVar5) {
        uStack_3a = uStack_3a + 1;
      }
      if (uStack_38 < uStack_3a) {
        uStack_38 = uStack_3a;
      }
      uVar10 = 0x22;
      uStack_36 = uVar2;
      if (uStack_3a <= uVar5) {
        uVar10 = 0x110011;
      }
    }
    else {
      if ((iVar8 == 0x33) || (iVar8 == 0x44)) {
        uStack_3c = 0;
        uStack_3e = 0;
        uVar10 = 0;
        goto LAB_0006eb40;
      }
      uVar10 = 0;
    }
    uVar6 = uVar10 & 0xffff;
    if (uVar6 != 0) {
      if (uVar6 == 0x11) {
        if ((uint32_t)(param_3[7]) != 0u) {
          (*(int (*)())camry_indirect((uint32_t)(param_3[7])))();
        }
        pcVar11 = (code *)param_3[0xe];
      }
      else if (uVar6 == 0x22) {
        if ((uint32_t)(param_3[7]) != 0u) {
          (*(int (*)())camry_indirect((uint32_t)(param_3[7])))();
        }
        if ((uint32_t)(param_3[9]) != 0u) {
          (*(int (*)())camry_indirect((uint32_t)(param_3[9])))();
        }
        pcVar11 = (code *)param_3[0xf];
      }
      else if (uVar6 == 0x1100) {
        if ((uint32_t)(param_3[3]) != 0u) {
          (*(int (*)())camry_indirect((uint32_t)(param_3[3])))();
        }
        pcVar11 = (code *)param_3[0xc];
      }
      else {
        if (uVar6 != 0x2200) {
          uVar10 = 0;
          goto LAB_0006ed2a;
        }
        if ((uint32_t)(param_3[3]) != 0u) {
          (*(int (*)())camry_indirect((uint32_t)(param_3[3])))();
        }
        if ((uint32_t)(param_3[5]) != 0u) {
          (*(int (*)())camry_indirect((uint32_t)(param_3[5])))();
        }
        pcVar11 = (code *)param_3[0xd];
      }
      if ((uint32_t)(pcVar11) != 0u) {
        (*(int (*)())camry_indirect((uint32_t)(pcVar11)))();
      }
    }
    goto LAB_0006ed2a;
  }
  if (uVar6 == 0x11) {
    iVar8 = (*(int (*)())camry_indirect((uint32_t)(param_3[1])))();
    if ((uVar4 < uStack_36) || (uVar2 = uStack_36 + 1, uVar4 < (ushort)(uStack_36 + 1))) {
LAB_0006ec4a:
      uStack_36 = 0;
      uStack_3a = 0;
      uStack_3c = 0;
      uStack_3e = 0;
      uVar6 = 0;
    }
    else {
      uVar6 = uVar10;
      uStack_36 = uVar2;
      if (iVar8 == 0x11) {
LAB_0006ec14:
        uStack_3e = 0;
        uStack_3c = 0;
      }
      else if (iVar8 == 0x22) {
        uStack_3e = 0;
        uStack_3c = 0;
        if (uStack_3a <= uVar5) {
          uStack_3a = uStack_3a + 1;
        }
        if (uStack_38 < uStack_3a) {
          uStack_38 = uStack_3a;
        }
        uVar6 = 0x22;
        if (uStack_3a <= uVar5) {
          uVar6 = 0x110011;
        }
      }
      else {
        if (iVar8 == 0x33) goto LAB_0006ec14;
        if (iVar8 == 0x44) goto LAB_0006ec4a;
      }
    }
    uVar7 = uVar6 & 0xffff;
    if (uVar7 == 0) {
      uVar10 = uVar6;
      if ((uint32_t)(param_3[8]) != 0u) {
        (*(int (*)())camry_indirect((uint32_t)(param_3[8])))();
      }
    }
    else {
      if (uVar7 == 0x11) {
        pcVar11 = (code *)param_3[0xe];
      }
      else {
        if (uVar7 != 0x22) {
          if ((uint32_t)(param_3[0xe]) != 0u) {
            (*(int (*)())camry_indirect((uint32_t)(param_3[0xe])))();
          }
          goto LAB_0006ed2a;
        }
        if ((uint32_t)(param_3[9]) != 0u) {
          (*(int (*)())camry_indirect((uint32_t)(param_3[9])))();
        }
        pcVar11 = (code *)param_3[0xf];
      }
      uVar10 = uVar6;
      if ((uint32_t)(pcVar11) != 0u) {
        (*(int (*)())camry_indirect((uint32_t)(pcVar11)))();
      }
    }
    goto LAB_0006ed2a;
  }
  if (uVar6 == 0x22) {
    uVar9 = (*(int (*)())camry_indirect((uint32_t)(param_3[2])))();
    uVar10 = FUN_00071232(uVar9,&uStack_3e,&local_44);
    uVar6 = uVar10 & 0xffff;
    if (uVar6 == 0) {
      pcVar11 = (code *)param_3[10];
    }
    else if (uVar6 == 0x22) {
      pcVar11 = (code *)param_3[0xf];
    }
    else {
      if (uVar6 != 0x44) {
        if ((uint32_t)(param_3[0xf]) != 0u) {
          (*(int (*)())camry_indirect((uint32_t)(param_3[0xf])))();
        }
        uVar10 = 0x22;
        goto LAB_0006ed2a;
      }
      if ((uint32_t)(param_3[0xb]) != 0u) {
        (*(int (*)())camry_indirect((uint32_t)(param_3[0xb])))();
      }
      pcVar11 = (code *)param_3[0x10];
    }
    if ((uint32_t)(pcVar11) != 0u) {
      (*(int (*)())camry_indirect((uint32_t)(pcVar11)))();
    }
    goto LAB_0006ed2a;
  }
  if (uVar6 != 0x1100) {
    if (uVar6 != 0x2200) {
      if ((uint32_t)(param_3[0x10]) != 0u) {
        (*(int (*)())camry_indirect((uint32_t)(param_3[0x10])))();
      }
      uVar10 = 0x44;
      goto LAB_0006ed2a;
    }
    iVar8 = (*(int (*)())camry_indirect((uint32_t)(pcVar11)))();
    if (iVar8 == 0x11) {
LAB_0006e884:
      uStack_3a = 0;
      uStack_36 = 0;
LAB_0006e88a:
      uVar10 = 0x2200;
    }
    else {
      if (iVar8 != 0x22) {
        if ((iVar8 == 0x33) || (iVar8 == 0x44)) goto LAB_0006e884;
        goto LAB_0006e88a;
      }
      uStack_3e = 0;
      uStack_3c = 0;
      if ((uVar4 < uStack_36) || (uVar2 = uStack_36 + 1, uVar4 < (ushort)(uStack_36 + 1))) {
        uStack_3a = 0;
        uVar10 = 0;
        uStack_36 = 0;
      }
      else {
        if (uStack_3a <= uVar5) {
          uStack_3a = uStack_3a + 1;
        }
        if (uStack_38 < uStack_3a) {
          uStack_38 = uStack_3a;
        }
        uVar10 = 0x22;
        uStack_36 = uVar2;
        if (uStack_3a <= uVar5) {
          uVar10 = 0x110011;
        }
      }
    }
    uVar6 = uVar10 & 0xffff;
    if (uVar6 == 0) {
      if ((uint32_t)(param_3[6]) != 0u) {
        (*(int (*)())camry_indirect((uint32_t)(param_3[6])))();
      }
    }
    else {
      if (uVar6 == 0x11) {
        if ((uint32_t)(param_3[6]) != 0u) {
          (*(int (*)())camry_indirect((uint32_t)(param_3[6])))();
        }
        if ((uint32_t)(param_3[7]) != 0u) {
          (*(int (*)())camry_indirect((uint32_t)(param_3[7])))();
        }
        pcVar11 = (code *)param_3[0xe];
      }
      else if (uVar6 == 0x22) {
        if ((uint32_t)(param_3[6]) != 0u) {
          (*(int (*)())camry_indirect((uint32_t)(param_3[6])))();
        }
        if ((uint32_t)(param_3[7]) != 0u) {
          (*(int (*)())camry_indirect((uint32_t)(param_3[7])))();
        }
        if ((uint32_t)(param_3[9]) != 0u) {
          (*(int (*)())camry_indirect((uint32_t)(param_3[9])))();
        }
        pcVar11 = (code *)param_3[0xf];
      }
      else {
        pcVar11 = (code *)param_3[0xd];
        if (uVar6 != 0x2200) {
          if ((uint32_t)(pcVar11) != 0u) {
            (*(int (*)())camry_indirect((uint32_t)(pcVar11)))();
          }
          uVar10 = 0x2200;
          goto LAB_0006ed2a;
        }
      }
      if ((uint32_t)(pcVar11) != 0u) {
        (*(int (*)())camry_indirect((uint32_t)(pcVar11)))();
      }
    }
    goto LAB_0006ed2a;
  }
  iVar8 = (*(int (*)())camry_indirect((uint32_t)(pcVar11)))();
  if ((uVar3 < uStack_3c) || (uVar1 = uStack_3c + 1, uVar3 < (ushort)(uStack_3c + 1))) {
LAB_0006e9ce:
    uStack_3c = 0;
    uStack_3e = 0;
    uVar10 = 0;
LAB_0006e9d6:
    uStack_36 = 0;
    uStack_3a = 0;
  }
  else {
    uStack_3c = uVar1;
    if (iVar8 == 0x11) {
      if ((uVar2 < uStack_3e) ||
         (uVar3 = uStack_3e + 1, uVar5 = uStack_3e + 1, uStack_3e = uVar3, uVar2 < uVar5)) {
        uVar10 = 0x2200;
      }
      else {
        uVar10 = 0x11001100;
      }
      goto LAB_0006e9d6;
    }
    if (iVar8 == 0x22) {
      uStack_3e = 0;
      uStack_3c = 0;
      if ((uVar4 < uStack_36) || (uVar2 = uStack_36 + 1, uVar4 < (ushort)(uStack_36 + 1))) {
        uVar10 = 0;
        goto LAB_0006e9d6;
      }
      if (uStack_3a <= uVar5) {
        uStack_3a = uStack_3a + 1;
      }
      if (uStack_38 < uStack_3a) {
        uStack_38 = uStack_3a;
      }
      uVar10 = 0x22;
      uStack_36 = uVar2;
      if (uStack_3a <= uVar5) {
        uVar10 = 0x110011;
      }
    }
    else {
      if (iVar8 == 0x33) {
        uStack_3a = 0;
        uStack_36 = 0;
      }
      else if (iVar8 == 0x44) goto LAB_0006e9ce;
      uVar10 = 0x1100;
    }
  }
  uVar6 = uVar10 & 0xffff;
  if (uVar6 == 0) {
    if ((uint32_t)(param_3[4]) != 0u) {
      (*(int (*)())camry_indirect((uint32_t)(param_3[4])))();
    }
  }
  else {
    if (uVar6 == 0x11) {
      if ((uint32_t)(param_3[4]) != 0u) {
        (*(int (*)())camry_indirect((uint32_t)(param_3[4])))();
      }
      if ((uint32_t)(param_3[7]) != 0u) {
        (*(int (*)())camry_indirect((uint32_t)(param_3[7])))();
      }
      pcVar11 = (code *)param_3[0xe];
    }
    else if (uVar6 == 0x22) {
      if ((uint32_t)(param_3[4]) != 0u) {
        (*(int (*)())camry_indirect((uint32_t)(param_3[4])))();
      }
      if ((uint32_t)(param_3[7]) != 0u) {
        (*(int (*)())camry_indirect((uint32_t)(param_3[7])))();
      }
      if ((uint32_t)(param_3[9]) != 0u) {
        (*(int (*)())camry_indirect((uint32_t)(param_3[9])))();
      }
      pcVar11 = (code *)param_3[0xf];
    }
    else if (uVar6 == 0x1100) {
      pcVar11 = (code *)param_3[0xc];
    }
    else {
      if (uVar6 != 0x2200) {
        if ((uint32_t)(param_3[0xc]) != 0u) {
          (*(int (*)())camry_indirect((uint32_t)(param_3[0xc])))();
        }
        uVar10 = 0x1100;
        goto LAB_0006ed2a;
      }
      if ((uint32_t)(param_3[5]) != 0u) {
        (*(int (*)())camry_indirect((uint32_t)(param_3[5])))();
      }
      pcVar11 = (code *)param_3[0xd];
    }
    if ((uint32_t)(pcVar11) != 0u) {
      (*(int (*)())camry_indirect((uint32_t)(pcVar11)))();
    }
  }
LAB_0006ed2a:
  *param_1 = uVar10;
  *(ushort *)(param_1 + 1) = uStack_3e;
  (*((ushort *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 6)))) = uStack_3c;
  *(ushort *)(param_1 + 2) = uStack_3a;
  (*((ushort *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 10)))) = uStack_36;
  *(ushort *)(param_1 + 3) = uStack_38;
  (*((undefined2 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 0xe)))) = uStack_34;
  *(ushort *)(param_1 + 4) = uStack_32;
  (*((undefined2 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 0x12)))) = uStack_30;
  return 0x11;
}



/* WARNING: Type propagation algorithm not settling */

short FUN_0006ed64(uint *param_1,ushort *param_2,undefined4 *param_3)

{
  ushort uVar1;
  ushort uVar2;
  short sVar3;
  uint uVar4;
  int iVar5;
  undefined4 uVar6;
  ushort uVar7;
  uint uVar8;
  code *pcVar9;
  ushort local_3c;
  ushort uStack_3a;
  ushort auStack_36 [2];
  ushort uStack_32;
  ushort uStack_30;
  undefined2 uStack_2c;
  ushort uStack_2a;
  undefined2 uStack_28;
  
  sVar3 = 0x11;
  if ((((((uintptr_t)(param_1)==(uintptr_t)((uint *)0x0)) || ((uintptr_t)(param_2)==(uintptr_t)((ushort *)0x0))) || ((uintptr_t)(param_3)==(uintptr_t)((undefined4 *)0x0)))
      || ((pcVar9 = (code *)*param_3,(uint32_t)(pcVar9) == 0u||
          ((uint32_t)(param_3[1]) == 0u)))) || ((uint32_t)(param_3[2]) == 0u)) {
    return 0x22;
  }
  uStack_30 = (ushort)param_1[2];
  auStack_36[0] = (ushort)param_1[1];
  uStack_32 = (*((ushort *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 6))));
  uStack_2a = (ushort)param_1[3];
  uStack_2c = (*((undefined2 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 10))));
  uStack_28 = (*((undefined2 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 0xe))));
  uVar1 = *param_2;
  uVar2 = param_2[1];
  local_3c = param_2[2];
  uStack_3a = param_2[3];
  if (uStack_32 == 0) {
    if (uVar1 < auStack_36[0]) {
      sVar3 = 0x2200;
    }
    else {
      sVar3 = 0;
      if (auStack_36[0] != 0) {
        sVar3 = 0x1100;
      }
    }
  }
  else if ((uVar2 < uStack_32) && (sVar3 = 0x44, uStack_2a <= uStack_3a)) {
    sVar3 = 0x22;
  }
  if (sVar3 == 0) {
    iVar5 = (*(int (*)())camry_indirect((uint32_t)(pcVar9)))();
    if (iVar5 == 0x11) {
      if ((uVar1 < auStack_36[0]) ||
         (uVar2 = auStack_36[0] + 1, uVar7 = auStack_36[0] + 1, auStack_36[0] = uVar2, uVar1 < uVar7
         )) {
        uVar8 = 0x2200;
      }
      else {
        uVar8 = 0x11001100;
      }
      uStack_32 = 0;
    }
    else if (iVar5 == 0x22) {
      auStack_36[0] = 0;
      if (uStack_32 <= uVar2) {
        uStack_32 = uStack_32 + 1;
      }
      if (uStack_30 < uStack_32) {
        uStack_30 = uStack_32;
      }
      uVar8 = 0x22;
      if (uStack_32 <= uVar2) {
        uVar8 = 0x110011;
      }
    }
    else if ((iVar5 == 0x33) || (iVar5 == 0x44)) {
      uStack_32 = 0;
      auStack_36[0] = 0;
      uVar8 = 0;
    }
    else {
      uVar8 = 0xffff;
    }
    uVar4 = uVar8 & 0xffff;
    if (uVar4 != 0) {
      if (uVar4 == 0x11) {
        if ((uint32_t)(param_3[7]) != 0u) {
          (*(int (*)())camry_indirect((uint32_t)(param_3[7])))();
        }
        pcVar9 = (code *)param_3[0xe];
      }
      else if (uVar4 == 0x22) {
        if ((uint32_t)(param_3[7]) != 0u) {
          (*(int (*)())camry_indirect((uint32_t)(param_3[7])))();
        }
        if ((uint32_t)(param_3[9]) != 0u) {
          (*(int (*)())camry_indirect((uint32_t)(param_3[9])))();
        }
        pcVar9 = (code *)param_3[0xf];
      }
      else if (uVar4 == 0x1100) {
        if ((uint32_t)(param_3[3]) != 0u) {
          (*(int (*)())camry_indirect((uint32_t)(param_3[3])))();
        }
        pcVar9 = (code *)param_3[0xc];
      }
      else {
        if (uVar4 != 0x2200) {
          uVar8 = 0;
          goto LAB_0006f300;
        }
        if ((uint32_t)(param_3[3]) != 0u) {
          (*(int (*)())camry_indirect((uint32_t)(param_3[3])))();
        }
        if ((uint32_t)(param_3[5]) != 0u) {
          (*(int (*)())camry_indirect((uint32_t)(param_3[5])))();
        }
        pcVar9 = (code *)param_3[0xd];
      }
      if ((uint32_t)(pcVar9) != 0u) {
        (*(int (*)())camry_indirect((uint32_t)(pcVar9)))();
      }
    }
    goto LAB_0006f300;
  }
  if (sVar3 == 0x11) {
    iVar5 = (*(int (*)())camry_indirect((uint32_t)(param_3[1])))();
    if (iVar5 == 0x11) {
      if ((uVar1 < auStack_36[0]) ||
         (uVar2 = auStack_36[0] + 1, uVar7 = auStack_36[0] + 1, auStack_36[0] = uVar2, uVar1 < uVar7
         )) {
        uVar8 = 0x2200;
      }
      else {
        uVar8 = 0x11001100;
      }
      uStack_32 = 0;
    }
    else if (iVar5 == 0x22) {
      auStack_36[0] = 0;
      if (uStack_32 <= uVar2) {
        uStack_32 = uStack_32 + 1;
      }
      if (uStack_30 < uStack_32) {
        uStack_30 = uStack_32;
      }
      uVar8 = 0x22;
      if (uStack_32 <= uVar2) {
        uVar8 = 0x110011;
      }
    }
    else if ((iVar5 == 0x33) || (iVar5 == 0x44)) {
      uStack_32 = 0;
      auStack_36[0] = 0;
      uVar8 = 0;
    }
    else {
      uVar8 = 0xffff;
    }
    uVar4 = uVar8 & 0xffff;
    if (uVar4 == 0) {
      if ((uint32_t)(param_3[8]) != 0u) {
        (*(int (*)())camry_indirect((uint32_t)(param_3[8])))();
      }
    }
    else {
      if (uVar4 == 0x11) {
        pcVar9 = (code *)param_3[0xe];
      }
      else if (uVar4 == 0x22) {
        if ((uint32_t)(param_3[9]) != 0u) {
          (*(int (*)())camry_indirect((uint32_t)(param_3[9])))();
        }
        pcVar9 = (code *)param_3[0xf];
      }
      else if (uVar4 == 0x1100) {
        if ((uint32_t)(param_3[8]) != 0u) {
          (*(int (*)())camry_indirect((uint32_t)(param_3[8])))();
        }
        if ((uint32_t)(param_3[3]) != 0u) {
          (*(int (*)())camry_indirect((uint32_t)(param_3[3])))();
        }
        pcVar9 = (code *)param_3[0xc];
      }
      else {
        if (uVar4 != 0x2200) {
          if ((uint32_t)(param_3[0xe]) != 0u) {
            (*(int (*)())camry_indirect((uint32_t)(param_3[0xe])))();
          }
          uVar8 = 0x11;
          goto LAB_0006f300;
        }
        if ((uint32_t)(param_3[8]) != 0u) {
          (*(int (*)())camry_indirect((uint32_t)(param_3[8])))();
        }
        if ((uint32_t)(param_3[3]) != 0u) {
          (*(int (*)())camry_indirect((uint32_t)(param_3[3])))();
        }
        if ((uint32_t)(param_3[5]) != 0u) {
          (*(int (*)())camry_indirect((uint32_t)(param_3[5])))();
        }
        pcVar9 = (code *)param_3[0xd];
      }
      if ((uint32_t)(pcVar9) != 0u) {
        (*(int (*)())camry_indirect((uint32_t)(pcVar9)))();
      }
    }
    goto LAB_0006f300;
  }
  if (sVar3 == 0x22) {
    uVar6 = (*(int (*)())camry_indirect((uint32_t)(param_3[2])))();
    uVar8 = FUN_00071086(uVar6,auStack_36,&local_3c);
    uVar4 = uVar8 & 0xffff;
    if (uVar4 == 0) {
      pcVar9 = (code *)param_3[10];
    }
    else if (uVar4 == 0x22) {
      pcVar9 = (code *)param_3[0xf];
    }
    else {
      if (uVar4 != 0x44) {
        if ((uint32_t)(param_3[0xf]) != 0u) {
          (*(int (*)())camry_indirect((uint32_t)(param_3[0xf])))();
        }
        uVar8 = 0x22;
        goto LAB_0006f300;
      }
      if ((uint32_t)(param_3[0xb]) != 0u) {
        (*(int (*)())camry_indirect((uint32_t)(param_3[0xb])))();
      }
      pcVar9 = (code *)param_3[0x10];
    }
    if ((uint32_t)(pcVar9) != 0u) {
      (*(int (*)())camry_indirect((uint32_t)(pcVar9)))();
    }
    goto LAB_0006f300;
  }
  if (sVar3 == 0x1100) {
    iVar5 = (*(int (*)())camry_indirect((uint32_t)(pcVar9)))();
    if (iVar5 == 0x11) {
      if ((uVar1 < auStack_36[0]) ||
         (uVar2 = auStack_36[0] + 1, uVar7 = auStack_36[0] + 1, auStack_36[0] = uVar2, uVar1 < uVar7
         )) {
        uVar8 = 0x2200;
      }
      else {
        uVar8 = 0x11001100;
      }
      uStack_32 = 0;
    }
    else if (iVar5 == 0x22) {
      auStack_36[0] = 0;
      if (uStack_32 <= uVar2) {
        uStack_32 = uStack_32 + 1;
      }
      if (uStack_30 < uStack_32) {
        uStack_30 = uStack_32;
      }
      uVar8 = 0x22;
      if (uStack_32 <= uVar2) {
        uVar8 = 0x110011;
      }
    }
    else if ((iVar5 == 0x33) || (iVar5 == 0x44)) {
      uStack_32 = 0;
      auStack_36[0] = 0;
      uVar8 = 0;
    }
    else {
      uVar8 = 0xffff;
    }
    uVar4 = uVar8 & 0xffff;
    if (uVar4 == 0) {
      if ((uint32_t)(param_3[4]) != 0u) {
        (*(int (*)())camry_indirect((uint32_t)(param_3[4])))();
      }
    }
    else {
      if (uVar4 == 0x11) {
        if ((uint32_t)(param_3[4]) != 0u) {
          (*(int (*)())camry_indirect((uint32_t)(param_3[4])))();
        }
        if ((uint32_t)(param_3[7]) != 0u) {
          (*(int (*)())camry_indirect((uint32_t)(param_3[7])))();
        }
        pcVar9 = (code *)param_3[0xe];
      }
      else if (uVar4 == 0x22) {
        if ((uint32_t)(param_3[4]) != 0u) {
          (*(int (*)())camry_indirect((uint32_t)(param_3[4])))();
        }
        if ((uint32_t)(param_3[7]) != 0u) {
          (*(int (*)())camry_indirect((uint32_t)(param_3[7])))();
        }
        if ((uint32_t)(param_3[9]) != 0u) {
          (*(int (*)())camry_indirect((uint32_t)(param_3[9])))();
        }
        pcVar9 = (code *)param_3[0xf];
      }
      else if (uVar4 == 0x1100) {
        pcVar9 = (code *)param_3[0xc];
      }
      else {
        if (uVar4 != 0x2200) {
          if ((uint32_t)(param_3[0xc]) != 0u) {
            (*(int (*)())camry_indirect((uint32_t)(param_3[0xc])))();
          }
          uVar8 = 0x1100;
          goto LAB_0006f300;
        }
        if ((uint32_t)(param_3[5]) != 0u) {
          (*(int (*)())camry_indirect((uint32_t)(param_3[5])))();
        }
        pcVar9 = (code *)param_3[0xd];
      }
      if ((uint32_t)(pcVar9) != 0u) {
        (*(int (*)())camry_indirect((uint32_t)(pcVar9)))();
      }
    }
    goto LAB_0006f300;
  }
  if (sVar3 != 0x2200) {
    if ((uint32_t)(param_3[0x10]) != 0u) {
      (*(int (*)())camry_indirect((uint32_t)(param_3[0x10])))();
    }
    uVar8 = 0x44;
    goto LAB_0006f300;
  }
  iVar5 = (*(int (*)())camry_indirect((uint32_t)(pcVar9)))();
  if (iVar5 == 0x11) {
LAB_0006ee6c:
    uStack_32 = 0;
LAB_0006ee70:
    uVar8 = 0x2200;
  }
  else {
    if (iVar5 != 0x22) {
      if ((iVar5 == 0x33) || (iVar5 == 0x44)) goto LAB_0006ee6c;
      goto LAB_0006ee70;
    }
    auStack_36[0] = 0;
    if (uStack_32 <= uVar2) {
      uStack_32 = uStack_32 + 1;
    }
    if (uStack_30 < uStack_32) {
      uStack_30 = uStack_32;
    }
    uVar8 = 0x22;
    if (uStack_32 <= uVar2) {
      uVar8 = 0x110011;
    }
  }
  uVar4 = uVar8 & 0xffff;
  if (uVar4 == 0) {
    if ((uint32_t)(param_3[6]) != 0u) {
      (*(int (*)())camry_indirect((uint32_t)(param_3[6])))();
    }
  }
  else {
    if (uVar4 == 0x11) {
      if ((uint32_t)(param_3[6]) != 0u) {
        (*(int (*)())camry_indirect((uint32_t)(param_3[6])))();
      }
      if ((uint32_t)(param_3[7]) != 0u) {
        (*(int (*)())camry_indirect((uint32_t)(param_3[7])))();
      }
      pcVar9 = (code *)param_3[0xe];
    }
    else if (uVar4 == 0x22) {
      if ((uint32_t)(param_3[6]) != 0u) {
        (*(int (*)())camry_indirect((uint32_t)(param_3[6])))();
      }
      if ((uint32_t)(param_3[7]) != 0u) {
        (*(int (*)())camry_indirect((uint32_t)(param_3[7])))();
      }
      if ((uint32_t)(param_3[9]) != 0u) {
        (*(int (*)())camry_indirect((uint32_t)(param_3[9])))();
      }
      pcVar9 = (code *)param_3[0xf];
    }
    else {
      pcVar9 = (code *)param_3[0xd];
      if (uVar4 != 0x2200) {
        if ((uint32_t)(pcVar9) != 0u) {
          (*(int (*)())camry_indirect((uint32_t)(pcVar9)))();
        }
        uVar8 = 0x2200;
        goto LAB_0006f300;
      }
    }
    if ((uint32_t)(pcVar9) != 0u) {
      (*(int (*)())camry_indirect((uint32_t)(pcVar9)))();
    }
  }
LAB_0006f300:
  *param_1 = uVar8;
  *(ushort *)(param_1 + 1) = auStack_36[0];
  (*((ushort *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 6)))) = uStack_32;
  *(ushort *)(param_1 + 2) = uStack_30;
  (*((undefined2 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 10)))) = uStack_2c;
  *(ushort *)(param_1 + 3) = uStack_2a;
  (*((undefined2 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 0xe)))) = uStack_28;
  return 0x11;
}



/* WARNING: Type propagation algorithm not settling */

short FUN_0006f32e(uint *param_1,ushort *param_2,undefined4 *param_3)

{
  ushort uVar1;
  ushort uVar2;
  short sVar3;
  uint uVar4;
  int iVar5;
  undefined4 uVar6;
  ushort uVar7;
  uint uVar8;
  code *pcVar9;
  ushort local_3c;
  ushort uStack_3a;
  ushort uStack_38;
  ushort auStack_36 [2];
  ushort uStack_32;
  ushort uStack_30;
  undefined2 uStack_2c;
  ushort uStack_2a;
  undefined2 uStack_28;
  ushort uStack_26;
  
  sVar3 = 0x11;
  if ((((((uintptr_t)(param_1)==(uintptr_t)((uint *)0x0)) || ((uintptr_t)(param_2)==(uintptr_t)((ushort *)0x0))) || ((uintptr_t)(param_3)==(uintptr_t)((undefined4 *)0x0)))
      || ((pcVar9 = (code *)*param_3,(uint32_t)(pcVar9) == 0u||
          ((uint32_t)(param_3[1]) == 0u)))) || ((uint32_t)(param_3[2]) == 0u)) {
    return 0x22;
  }
  uStack_30 = (ushort)param_1[2];
  auStack_36[0] = (ushort)param_1[1];
  uStack_32 = (*((ushort *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 6))));
  uStack_2a = (ushort)param_1[3];
  uStack_2c = (*((undefined2 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 10))));
  uStack_26 = (*((ushort *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 0xe))));
  uStack_28 = (undefined2)param_1[4];
  uStack_3a = param_2[3];
  local_3c = param_2[2];
  uVar1 = *param_2;
  uVar2 = param_2[1];
  uStack_38 = param_2[4];
  if (uStack_32 == 0) {
    if (uVar1 < auStack_36[0]) {
      sVar3 = 0x2200;
    }
    else {
      sVar3 = 0;
      if (auStack_36[0] != 0) {
        sVar3 = 0x1100;
      }
    }
  }
  else if (uVar2 < uStack_32) {
    if ((uStack_38 < uStack_26) || (uStack_3a < uStack_2a)) {
      sVar3 = 0x44;
    }
    else {
      sVar3 = 0x22;
    }
  }
  if (sVar3 == 0) {
    iVar5 = (*(int (*)())camry_indirect((uint32_t)(pcVar9)))();
    if (iVar5 == 0x11) {
      if ((uVar1 < auStack_36[0]) ||
         (uVar2 = auStack_36[0] + 1, uVar7 = auStack_36[0] + 1, auStack_36[0] = uVar2, uVar1 < uVar7
         )) {
        uVar8 = 0x2200;
      }
      else {
        uVar8 = 0x11001100;
      }
      uStack_32 = 0;
    }
    else if (iVar5 == 0x22) {
      auStack_36[0] = 0;
      if (uStack_32 <= uVar2) {
        uStack_32 = uStack_32 + 1;
      }
      if (uStack_30 < uStack_32) {
        uStack_30 = uStack_32;
      }
      uVar8 = 0x22;
      if (uStack_32 <= uVar2) {
        uVar8 = 0x110011;
      }
    }
    else if ((iVar5 == 0x33) || (iVar5 == 0x44)) {
      uStack_32 = 0;
      auStack_36[0] = 0;
      uVar8 = 0;
    }
    else {
      uVar8 = 0xffff;
    }
    uVar4 = uVar8 & 0xffff;
    if (uVar4 != 0) {
      if (uVar4 == 0x11) {
        if ((uint32_t)(param_3[7]) != 0u) {
          (*(int (*)())camry_indirect((uint32_t)(param_3[7])))();
        }
        pcVar9 = (code *)param_3[0xe];
      }
      else if (uVar4 == 0x22) {
        if ((uint32_t)(param_3[7]) != 0u) {
          (*(int (*)())camry_indirect((uint32_t)(param_3[7])))();
        }
        if ((uint32_t)(param_3[9]) != 0u) {
          (*(int (*)())camry_indirect((uint32_t)(param_3[9])))();
        }
        pcVar9 = (code *)param_3[0xf];
      }
      else if (uVar4 == 0x1100) {
        if ((uint32_t)(param_3[3]) != 0u) {
          (*(int (*)())camry_indirect((uint32_t)(param_3[3])))();
        }
        pcVar9 = (code *)param_3[0xc];
      }
      else {
        if (uVar4 != 0x2200) {
          uVar8 = 0;
          goto LAB_0006f8dc;
        }
        if ((uint32_t)(param_3[3]) != 0u) {
          (*(int (*)())camry_indirect((uint32_t)(param_3[3])))();
        }
        if ((uint32_t)(param_3[5]) != 0u) {
          (*(int (*)())camry_indirect((uint32_t)(param_3[5])))();
        }
        pcVar9 = (code *)param_3[0xd];
      }
      if ((uint32_t)(pcVar9) != 0u) {
        (*(int (*)())camry_indirect((uint32_t)(pcVar9)))();
      }
    }
    goto LAB_0006f8dc;
  }
  if (sVar3 == 0x11) {
    iVar5 = (*(int (*)())camry_indirect((uint32_t)(param_3[1])))();
    if (iVar5 == 0x11) {
      if ((uVar1 < auStack_36[0]) ||
         (uVar2 = auStack_36[0] + 1, uVar7 = auStack_36[0] + 1, auStack_36[0] = uVar2, uVar1 < uVar7
         )) {
        uVar8 = 0x2200;
      }
      else {
        uVar8 = 0x11001100;
      }
      uStack_32 = 0;
    }
    else if (iVar5 == 0x22) {
      auStack_36[0] = 0;
      if (uStack_32 <= uVar2) {
        uStack_32 = uStack_32 + 1;
      }
      if (uStack_30 < uStack_32) {
        uStack_30 = uStack_32;
      }
      uVar8 = 0x22;
      if (uStack_32 <= uVar2) {
        uVar8 = 0x110011;
      }
    }
    else if ((iVar5 == 0x33) || (iVar5 == 0x44)) {
      uStack_32 = 0;
      auStack_36[0] = 0;
      uVar8 = 0;
    }
    else {
      uVar8 = 0xffff;
    }
    uVar4 = uVar8 & 0xffff;
    if (uVar4 == 0) {
      if ((uint32_t)(param_3[8]) != 0u) {
        (*(int (*)())camry_indirect((uint32_t)(param_3[8])))();
      }
    }
    else {
      if (uVar4 == 0x11) {
        pcVar9 = (code *)param_3[0xe];
      }
      else if (uVar4 == 0x22) {
        if ((uint32_t)(param_3[9]) != 0u) {
          (*(int (*)())camry_indirect((uint32_t)(param_3[9])))();
        }
        pcVar9 = (code *)param_3[0xf];
      }
      else if (uVar4 == 0x1100) {
        if ((uint32_t)(param_3[8]) != 0u) {
          (*(int (*)())camry_indirect((uint32_t)(param_3[8])))();
        }
        if ((uint32_t)(param_3[3]) != 0u) {
          (*(int (*)())camry_indirect((uint32_t)(param_3[3])))();
        }
        pcVar9 = (code *)param_3[0xc];
      }
      else {
        if (uVar4 != 0x2200) {
          if ((uint32_t)(param_3[0xe]) != 0u) {
            (*(int (*)())camry_indirect((uint32_t)(param_3[0xe])))();
          }
          uVar8 = 0x11;
          goto LAB_0006f8dc;
        }
        if ((uint32_t)(param_3[8]) != 0u) {
          (*(int (*)())camry_indirect((uint32_t)(param_3[8])))();
        }
        if ((uint32_t)(param_3[3]) != 0u) {
          (*(int (*)())camry_indirect((uint32_t)(param_3[3])))();
        }
        if ((uint32_t)(param_3[5]) != 0u) {
          (*(int (*)())camry_indirect((uint32_t)(param_3[5])))();
        }
        pcVar9 = (code *)param_3[0xd];
      }
      if ((uint32_t)(pcVar9) != 0u) {
        (*(int (*)())camry_indirect((uint32_t)(pcVar9)))();
      }
    }
    goto LAB_0006f8dc;
  }
  if (sVar3 == 0x22) {
    uVar6 = (*(int (*)())camry_indirect((uint32_t)(param_3[2])))();
    uVar8 = FUN_00071194(uVar6,auStack_36,&local_3c);
    uVar4 = uVar8 & 0xffff;
    if (uVar4 == 0) {
      pcVar9 = (code *)param_3[10];
    }
    else if (uVar4 == 0x22) {
      pcVar9 = (code *)param_3[0xf];
    }
    else {
      if (uVar4 != 0x44) {
        if ((uint32_t)(param_3[0xf]) != 0u) {
          (*(int (*)())camry_indirect((uint32_t)(param_3[0xf])))();
        }
        uVar8 = 0x22;
        goto LAB_0006f8dc;
      }
      if ((uint32_t)(param_3[0xb]) != 0u) {
        (*(int (*)())camry_indirect((uint32_t)(param_3[0xb])))();
      }
      pcVar9 = (code *)param_3[0x10];
    }
    if ((uint32_t)(pcVar9) != 0u) {
      (*(int (*)())camry_indirect((uint32_t)(pcVar9)))();
    }
    goto LAB_0006f8dc;
  }
  if (sVar3 == 0x1100) {
    iVar5 = (*(int (*)())camry_indirect((uint32_t)(pcVar9)))();
    if (iVar5 == 0x11) {
      if ((uVar1 < auStack_36[0]) ||
         (uVar2 = auStack_36[0] + 1, uVar7 = auStack_36[0] + 1, auStack_36[0] = uVar2, uVar1 < uVar7
         )) {
        uVar8 = 0x2200;
      }
      else {
        uVar8 = 0x11001100;
      }
      uStack_32 = 0;
    }
    else if (iVar5 == 0x22) {
      auStack_36[0] = 0;
      if (uStack_32 <= uVar2) {
        uStack_32 = uStack_32 + 1;
      }
      if (uStack_30 < uStack_32) {
        uStack_30 = uStack_32;
      }
      uVar8 = 0x22;
      if (uStack_32 <= uVar2) {
        uVar8 = 0x110011;
      }
    }
    else if ((iVar5 == 0x33) || (iVar5 == 0x44)) {
      uStack_32 = 0;
      auStack_36[0] = 0;
      uVar8 = 0;
    }
    else {
      uVar8 = 0xffff;
    }
    uVar4 = uVar8 & 0xffff;
    if (uVar4 == 0) {
      if ((uint32_t)(param_3[4]) != 0u) {
        (*(int (*)())camry_indirect((uint32_t)(param_3[4])))();
      }
    }
    else {
      if (uVar4 == 0x11) {
        if ((uint32_t)(param_3[4]) != 0u) {
          (*(int (*)())camry_indirect((uint32_t)(param_3[4])))();
        }
        if ((uint32_t)(param_3[7]) != 0u) {
          (*(int (*)())camry_indirect((uint32_t)(param_3[7])))();
        }
        pcVar9 = (code *)param_3[0xe];
      }
      else if (uVar4 == 0x22) {
        if ((uint32_t)(param_3[4]) != 0u) {
          (*(int (*)())camry_indirect((uint32_t)(param_3[4])))();
        }
        if ((uint32_t)(param_3[7]) != 0u) {
          (*(int (*)())camry_indirect((uint32_t)(param_3[7])))();
        }
        if ((uint32_t)(param_3[9]) != 0u) {
          (*(int (*)())camry_indirect((uint32_t)(param_3[9])))();
        }
        pcVar9 = (code *)param_3[0xf];
      }
      else if (uVar4 == 0x1100) {
        pcVar9 = (code *)param_3[0xc];
      }
      else {
        if (uVar4 != 0x2200) {
          if ((uint32_t)(param_3[0xc]) != 0u) {
            (*(int (*)())camry_indirect((uint32_t)(param_3[0xc])))();
          }
          uVar8 = 0x1100;
          goto LAB_0006f8dc;
        }
        if ((uint32_t)(param_3[5]) != 0u) {
          (*(int (*)())camry_indirect((uint32_t)(param_3[5])))();
        }
        pcVar9 = (code *)param_3[0xd];
      }
      if ((uint32_t)(pcVar9) != 0u) {
        (*(int (*)())camry_indirect((uint32_t)(pcVar9)))();
      }
    }
    goto LAB_0006f8dc;
  }
  if (sVar3 != 0x2200) {
    if ((uint32_t)(param_3[0x10]) != 0u) {
      (*(int (*)())camry_indirect((uint32_t)(param_3[0x10])))();
    }
    uVar8 = 0x44;
    goto LAB_0006f8dc;
  }
  iVar5 = (*(int (*)())camry_indirect((uint32_t)(pcVar9)))();
  if (iVar5 == 0x11) {
LAB_0006f448:
    uStack_32 = 0;
LAB_0006f44c:
    uVar8 = 0x2200;
  }
  else {
    if (iVar5 != 0x22) {
      if ((iVar5 == 0x33) || (iVar5 == 0x44)) goto LAB_0006f448;
      goto LAB_0006f44c;
    }
    auStack_36[0] = 0;
    if (uStack_32 <= uVar2) {
      uStack_32 = uStack_32 + 1;
    }
    if (uStack_30 < uStack_32) {
      uStack_30 = uStack_32;
    }
    uVar8 = 0x22;
    if (uStack_32 <= uVar2) {
      uVar8 = 0x110011;
    }
  }
  uVar4 = uVar8 & 0xffff;
  if (uVar4 == 0) {
    if ((uint32_t)(param_3[6]) != 0u) {
      (*(int (*)())camry_indirect((uint32_t)(param_3[6])))();
    }
  }
  else {
    if (uVar4 == 0x11) {
      if ((uint32_t)(param_3[6]) != 0u) {
        (*(int (*)())camry_indirect((uint32_t)(param_3[6])))();
      }
      if ((uint32_t)(param_3[7]) != 0u) {
        (*(int (*)())camry_indirect((uint32_t)(param_3[7])))();
      }
      pcVar9 = (code *)param_3[0xe];
    }
    else if (uVar4 == 0x22) {
      if ((uint32_t)(param_3[6]) != 0u) {
        (*(int (*)())camry_indirect((uint32_t)(param_3[6])))();
      }
      if ((uint32_t)(param_3[7]) != 0u) {
        (*(int (*)())camry_indirect((uint32_t)(param_3[7])))();
      }
      if ((uint32_t)(param_3[9]) != 0u) {
        (*(int (*)())camry_indirect((uint32_t)(param_3[9])))();
      }
      pcVar9 = (code *)param_3[0xf];
    }
    else {
      pcVar9 = (code *)param_3[0xd];
      if (uVar4 != 0x2200) {
        if ((uint32_t)(pcVar9) != 0u) {
          (*(int (*)())camry_indirect((uint32_t)(pcVar9)))();
        }
        uVar8 = 0x2200;
        goto LAB_0006f8dc;
      }
    }
    if ((uint32_t)(pcVar9) != 0u) {
      (*(int (*)())camry_indirect((uint32_t)(pcVar9)))();
    }
  }
LAB_0006f8dc:
  *param_1 = uVar8;
  *(ushort *)(param_1 + 1) = auStack_36[0];
  (*((ushort *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 6)))) = uStack_32;
  *(ushort *)(param_1 + 2) = uStack_30;
  (*((undefined2 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 10)))) = uStack_2c;
  *(ushort *)(param_1 + 3) = uStack_2a;
  (*((ushort *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 0xe)))) = uStack_26;
  *(undefined2 *)(param_1 + 4) = uStack_28;
  return 0x11;
}



/* WARNING: Type propagation algorithm not settling */

undefined4 FUN_0006f910(uint *param_1,ushort *param_2,undefined4 *param_3)

{
  ushort uVar1;
  ushort uVar2;
  ushort uVar3;
  ushort uVar4;
  ushort uVar5;
  uint uVar6;
  uint uVar7;
  int iVar8;
  undefined4 uVar9;
  uint uVar10;
  code *pcVar11;
  ushort local_44;
  ushort uStack_42;
  ushort uStack_3e;
  ushort uStack_3c;
  ushort uStack_3a;
  ushort uStack_38;
  ushort uStack_36;
  undefined2 uStack_34;
  ushort uStack_2e;
  
  uVar10 = 0x11;
  if ((((((uintptr_t)(param_1)==(uintptr_t)((uint *)0x0)) || ((uintptr_t)(param_2)==(uintptr_t)((ushort *)0x0))) || ((uintptr_t)(param_3)==(uintptr_t)((undefined4 *)0x0)))
      || ((pcVar11 = (code *)*param_3,(uint32_t)(pcVar11) == 0u||
          ((uint32_t)(param_3[1]) == 0u)))) || ((uint32_t)(param_3[2]) == 0u)) {
    return 0x22;
  }
  uStack_36 = (*((ushort *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 10))));
  uStack_3c = (*((ushort *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 6))));
  uStack_3e = (ushort)param_1[1];
  uStack_2e = (ushort)param_1[4];
  uStack_38 = (ushort)param_1[3];
  uStack_3a = (ushort)param_1[2];
  uStack_34 = (*((undefined2 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 0xe))));
  uVar2 = *param_2;
  local_44 = param_2[4];
  uVar3 = param_2[1];
  uVar5 = param_2[2];
  uVar4 = param_2[3];
  uStack_42 = param_2[5];
  if (uStack_3a == 0) {
    if (uVar2 < uStack_3e) {
      uVar6 = 0x2200;
    }
    else {
      uVar6 = 0;
      if (uStack_3e != 0) {
        uVar6 = 0x1100;
      }
    }
  }
  else {
    uVar6 = uVar10;
    if ((uVar5 < uStack_3a) && (uVar6 = 0x44, uStack_2e <= uStack_42)) {
      uVar6 = 0x22;
    }
  }
  if (uVar6 == 0) {
    iVar8 = (*(int (*)())camry_indirect((uint32_t)(pcVar11)))();
    if (iVar8 == 0x11) {
      if ((uVar3 < uStack_3c) || (uVar3 < (ushort)(uStack_3c + 1))) {
        uStack_3c = 0;
        uStack_3e = 0;
        uVar10 = 0;
      }
      else if ((uVar2 < uStack_3e) ||
              (uVar3 = uStack_3e + 1, uVar5 = uStack_3e + 1, uStack_3e = uVar3, uVar2 < uVar5)) {
        uVar10 = 0x2200;
        uStack_3c = uStack_3c + 1;
      }
      else {
        uVar10 = 0x11001100;
        uStack_3c = uStack_3c + 1;
      }
LAB_0006fcfe:
      uStack_36 = 0;
      uStack_3a = 0;
    }
    else if (iVar8 == 0x22) {
      uStack_3e = 0;
      uStack_3c = 0;
      if ((uVar4 < uStack_36) || (uVar2 = uStack_36 + 1, uVar4 < (ushort)(uStack_36 + 1))) {
        uVar10 = 0;
        goto LAB_0006fcfe;
      }
      if (uStack_3a <= uVar5) {
        uStack_3a = uStack_3a + 1;
      }
      if (uStack_38 < uStack_3a) {
        uStack_38 = uStack_3a;
      }
      uVar10 = 0x22;
      uStack_36 = uVar2;
      if (uStack_3a <= uVar5) {
        uVar10 = 0x110011;
      }
    }
    else {
      if ((iVar8 == 0x33) || (iVar8 == 0x44)) {
        uStack_3c = 0;
        uStack_3e = 0;
        uVar10 = 0;
        goto LAB_0006fcfe;
      }
      uVar10 = 0;
    }
    uVar6 = uVar10 & 0xffff;
    if (uVar6 != 0) {
      if (uVar6 == 0x11) {
        if ((uint32_t)(param_3[7]) != 0u) {
          (*(int (*)())camry_indirect((uint32_t)(param_3[7])))();
        }
        pcVar11 = (code *)param_3[0xe];
      }
      else if (uVar6 == 0x22) {
        if ((uint32_t)(param_3[7]) != 0u) {
          (*(int (*)())camry_indirect((uint32_t)(param_3[7])))();
        }
        if ((uint32_t)(param_3[9]) != 0u) {
          (*(int (*)())camry_indirect((uint32_t)(param_3[9])))();
        }
        pcVar11 = (code *)param_3[0xf];
      }
      else if (uVar6 == 0x1100) {
        if ((uint32_t)(param_3[3]) != 0u) {
          (*(int (*)())camry_indirect((uint32_t)(param_3[3])))();
        }
        pcVar11 = (code *)param_3[0xc];
      }
      else {
        if (uVar6 != 0x2200) {
          uVar10 = 0;
          goto LAB_0006fee8;
        }
        if ((uint32_t)(param_3[3]) != 0u) {
          (*(int (*)())camry_indirect((uint32_t)(param_3[3])))();
        }
        if ((uint32_t)(param_3[5]) != 0u) {
          (*(int (*)())camry_indirect((uint32_t)(param_3[5])))();
        }
        pcVar11 = (code *)param_3[0xd];
      }
      if ((uint32_t)(pcVar11) != 0u) {
        (*(int (*)())camry_indirect((uint32_t)(pcVar11)))();
      }
    }
    goto LAB_0006fee8;
  }
  if (uVar6 == 0x11) {
    iVar8 = (*(int (*)())camry_indirect((uint32_t)(param_3[1])))();
    if ((uVar4 < uStack_36) || (uVar2 = uStack_36 + 1, uVar4 < (ushort)(uStack_36 + 1))) {
LAB_0006fe08:
      uStack_36 = 0;
      uStack_3a = 0;
      uStack_3c = 0;
      uStack_3e = 0;
      uVar6 = 0;
    }
    else {
      uVar6 = uVar10;
      uStack_36 = uVar2;
      if (iVar8 == 0x11) {
LAB_0006fdd2:
        uStack_3e = 0;
        uStack_3c = 0;
      }
      else if (iVar8 == 0x22) {
        uStack_3e = 0;
        uStack_3c = 0;
        if (uStack_3a <= uVar5) {
          uStack_3a = uStack_3a + 1;
        }
        if (uStack_38 < uStack_3a) {
          uStack_38 = uStack_3a;
        }
        uVar6 = 0x22;
        if (uStack_3a <= uVar5) {
          uVar6 = 0x110011;
        }
      }
      else {
        if (iVar8 == 0x33) goto LAB_0006fdd2;
        if (iVar8 == 0x44) goto LAB_0006fe08;
      }
    }
    uVar7 = uVar6 & 0xffff;
    if (uVar7 == 0) {
      uVar10 = uVar6;
      if ((uint32_t)(param_3[8]) != 0u) {
        (*(int (*)())camry_indirect((uint32_t)(param_3[8])))();
      }
    }
    else {
      if (uVar7 == 0x11) {
        pcVar11 = (code *)param_3[0xe];
      }
      else {
        if (uVar7 != 0x22) {
          if ((uint32_t)(param_3[0xe]) != 0u) {
            (*(int (*)())camry_indirect((uint32_t)(param_3[0xe])))();
          }
          goto LAB_0006fee8;
        }
        if ((uint32_t)(param_3[9]) != 0u) {
          (*(int (*)())camry_indirect((uint32_t)(param_3[9])))();
        }
        pcVar11 = (code *)param_3[0xf];
      }
      uVar10 = uVar6;
      if ((uint32_t)(pcVar11) != 0u) {
        (*(int (*)())camry_indirect((uint32_t)(pcVar11)))();
      }
    }
    goto LAB_0006fee8;
  }
  if (uVar6 == 0x22) {
    uVar9 = (*(int (*)())camry_indirect((uint32_t)(param_3[2])))();
    uVar10 = FUN_00070fa4(uVar9,&uStack_3e,&local_44);
    uVar6 = uVar10 & 0xffff;
    if (uVar6 == 0) {
      pcVar11 = (code *)param_3[10];
    }
    else if (uVar6 == 0x22) {
      pcVar11 = (code *)param_3[0xf];
    }
    else {
      if (uVar6 != 0x44) {
        if ((uint32_t)(param_3[0xf]) != 0u) {
          (*(int (*)())camry_indirect((uint32_t)(param_3[0xf])))();
        }
        uVar10 = 0x22;
        goto LAB_0006fee8;
      }
      if ((uint32_t)(param_3[0xb]) != 0u) {
        (*(int (*)())camry_indirect((uint32_t)(param_3[0xb])))();
      }
      pcVar11 = (code *)param_3[0x10];
    }
    if ((uint32_t)(pcVar11) != 0u) {
      (*(int (*)())camry_indirect((uint32_t)(pcVar11)))();
    }
    goto LAB_0006fee8;
  }
  if (uVar6 != 0x1100) {
    if (uVar6 != 0x2200) {
      if ((uint32_t)(param_3[0x10]) != 0u) {
        (*(int (*)())camry_indirect((uint32_t)(param_3[0x10])))();
      }
      uVar10 = 0x44;
      goto LAB_0006fee8;
    }
    iVar8 = (*(int (*)())camry_indirect((uint32_t)(pcVar11)))();
    if (iVar8 == 0x11) {
LAB_0006fa42:
      uStack_3a = 0;
      uStack_36 = 0;
LAB_0006fa48:
      uVar10 = 0x2200;
    }
    else {
      if (iVar8 != 0x22) {
        if ((iVar8 == 0x33) || (iVar8 == 0x44)) goto LAB_0006fa42;
        goto LAB_0006fa48;
      }
      uStack_3e = 0;
      uStack_3c = 0;
      if ((uVar4 < uStack_36) || (uVar2 = uStack_36 + 1, uVar4 < (ushort)(uStack_36 + 1))) {
        uStack_3a = 0;
        uVar10 = 0;
        uStack_36 = 0;
      }
      else {
        if (uStack_3a <= uVar5) {
          uStack_3a = uStack_3a + 1;
        }
        if (uStack_38 < uStack_3a) {
          uStack_38 = uStack_3a;
        }
        uVar10 = 0x22;
        uStack_36 = uVar2;
        if (uStack_3a <= uVar5) {
          uVar10 = 0x110011;
        }
      }
    }
    uVar6 = uVar10 & 0xffff;
    if (uVar6 == 0) {
      if ((uint32_t)(param_3[6]) != 0u) {
        (*(int (*)())camry_indirect((uint32_t)(param_3[6])))();
      }
    }
    else {
      if (uVar6 == 0x11) {
        if ((uint32_t)(param_3[6]) != 0u) {
          (*(int (*)())camry_indirect((uint32_t)(param_3[6])))();
        }
        if ((uint32_t)(param_3[7]) != 0u) {
          (*(int (*)())camry_indirect((uint32_t)(param_3[7])))();
        }
        pcVar11 = (code *)param_3[0xe];
      }
      else if (uVar6 == 0x22) {
        if ((uint32_t)(param_3[6]) != 0u) {
          (*(int (*)())camry_indirect((uint32_t)(param_3[6])))();
        }
        if ((uint32_t)(param_3[7]) != 0u) {
          (*(int (*)())camry_indirect((uint32_t)(param_3[7])))();
        }
        if ((uint32_t)(param_3[9]) != 0u) {
          (*(int (*)())camry_indirect((uint32_t)(param_3[9])))();
        }
        pcVar11 = (code *)param_3[0xf];
      }
      else {
        pcVar11 = (code *)param_3[0xd];
        if (uVar6 != 0x2200) {
          if ((uint32_t)(pcVar11) != 0u) {
            (*(int (*)())camry_indirect((uint32_t)(pcVar11)))();
          }
          uVar10 = 0x2200;
          goto LAB_0006fee8;
        }
      }
      if ((uint32_t)(pcVar11) != 0u) {
        (*(int (*)())camry_indirect((uint32_t)(pcVar11)))();
      }
    }
    goto LAB_0006fee8;
  }
  iVar8 = (*(int (*)())camry_indirect((uint32_t)(pcVar11)))();
  if ((uVar3 < uStack_3c) || (uVar1 = uStack_3c + 1, uVar3 < (ushort)(uStack_3c + 1))) {
LAB_0006fb8c:
    uStack_3c = 0;
    uStack_3e = 0;
    uVar10 = 0;
LAB_0006fb94:
    uStack_36 = 0;
    uStack_3a = 0;
  }
  else {
    uStack_3c = uVar1;
    if (iVar8 == 0x11) {
      if ((uVar2 < uStack_3e) ||
         (uVar3 = uStack_3e + 1, uVar5 = uStack_3e + 1, uStack_3e = uVar3, uVar2 < uVar5)) {
        uVar10 = 0x2200;
      }
      else {
        uVar10 = 0x11001100;
      }
      goto LAB_0006fb94;
    }
    if (iVar8 == 0x22) {
      uStack_3e = 0;
      uStack_3c = 0;
      if ((uVar4 < uStack_36) || (uVar2 = uStack_36 + 1, uVar4 < (ushort)(uStack_36 + 1))) {
        uVar10 = 0;
        goto LAB_0006fb94;
      }
      if (uStack_3a <= uVar5) {
        uStack_3a = uStack_3a + 1;
      }
      if (uStack_38 < uStack_3a) {
        uStack_38 = uStack_3a;
      }
      uVar10 = 0x22;
      uStack_36 = uVar2;
      if (uStack_3a <= uVar5) {
        uVar10 = 0x110011;
      }
    }
    else {
      if (iVar8 == 0x33) {
        uStack_3a = 0;
        uStack_36 = 0;
      }
      else if (iVar8 == 0x44) goto LAB_0006fb8c;
      uVar10 = 0x1100;
    }
  }
  uVar6 = uVar10 & 0xffff;
  if (uVar6 == 0) {
    if ((uint32_t)(param_3[4]) != 0u) {
      (*(int (*)())camry_indirect((uint32_t)(param_3[4])))();
    }
  }
  else {
    if (uVar6 == 0x11) {
      if ((uint32_t)(param_3[4]) != 0u) {
        (*(int (*)())camry_indirect((uint32_t)(param_3[4])))();
      }
      if ((uint32_t)(param_3[7]) != 0u) {
        (*(int (*)())camry_indirect((uint32_t)(param_3[7])))();
      }
      pcVar11 = (code *)param_3[0xe];
    }
    else if (uVar6 == 0x22) {
      if ((uint32_t)(param_3[4]) != 0u) {
        (*(int (*)())camry_indirect((uint32_t)(param_3[4])))();
      }
      if ((uint32_t)(param_3[7]) != 0u) {
        (*(int (*)())camry_indirect((uint32_t)(param_3[7])))();
      }
      if ((uint32_t)(param_3[9]) != 0u) {
        (*(int (*)())camry_indirect((uint32_t)(param_3[9])))();
      }
      pcVar11 = (code *)param_3[0xf];
    }
    else if (uVar6 == 0x1100) {
      pcVar11 = (code *)param_3[0xc];
    }
    else {
      if (uVar6 != 0x2200) {
        if ((uint32_t)(param_3[0xc]) != 0u) {
          (*(int (*)())camry_indirect((uint32_t)(param_3[0xc])))();
        }
        uVar10 = 0x1100;
        goto LAB_0006fee8;
      }
      if ((uint32_t)(param_3[5]) != 0u) {
        (*(int (*)())camry_indirect((uint32_t)(param_3[5])))();
      }
      pcVar11 = (code *)param_3[0xd];
    }
    if ((uint32_t)(pcVar11) != 0u) {
      (*(int (*)())camry_indirect((uint32_t)(pcVar11)))();
    }
  }
LAB_0006fee8:
  *param_1 = uVar10;
  *(ushort *)(param_1 + 1) = uStack_3e;
  (*((ushort *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 6)))) = uStack_3c;
  *(ushort *)(param_1 + 2) = uStack_3a;
  (*((ushort *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 10)))) = uStack_36;
  *(ushort *)(param_1 + 3) = uStack_38;
  (*((undefined2 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 0xe)))) = uStack_34;
  *(ushort *)(param_1 + 4) = uStack_2e;
  return 0x11;
}



/* Require finite fail/elapsed thresholds. Execute transition callbacks, publish44, seed
   failure/elapsed to threshold+1, clear passing/recovery, preserve failure high-water. Finite
   fail/elapsed thresholds permit callback-driven forced44; seed both counts threshold+1, clear
   pass/recovery, preserve high-water. */

void f33_force_monitor_escalation
               (F33EscalatingMonitorState *state,ushort *calibration,uint *callbacks)

{
  short sVar1;
  code *pcVar2;
  
  if (0xfffe < calibration[5]) {
    return;
  }
  if (0xfffe < calibration[7]) {
    return;
  }
  sVar1 = (short)state->packed_status;
  if (sVar1 == 0) {
LAB_0006ff72:
    if ((uint32_t)(callbacks[7]) != 0u) {
      (*(int (*)())camry_indirect((uint32_t)(callbacks[7])))();
    }
LAB_0006ff7e:
    if ((uint32_t)(callbacks[9]) != 0u) {
      (*(int (*)())camry_indirect((uint32_t)(callbacks[9])))();
    }
  }
  else {
    if (sVar1 == 0x11) goto LAB_0006ff7e;
    if (sVar1 != 0x22) {
      if (sVar1 == 0x1100) {
        pcVar2 = (code *)callbacks[4];
      }
      else {
        if (sVar1 != 0x2200) goto LAB_0006ffa2;
        pcVar2 = (code *)callbacks[6];
      }
      if ((uint32_t)(pcVar2) != 0u) {
        (*(int (*)())camry_indirect((uint32_t)(pcVar2)))();
      }
      goto LAB_0006ff72;
    }
  }
  if ((uint32_t)(callbacks[0xb]) != 0u) {
    (*(int (*)())camry_indirect((uint32_t)(callbacks[0xb])))();
  }
  if ((uint32_t)(callbacks[0x10]) != 0u) {
    (*(int (*)())camry_indirect((uint32_t)(callbacks[0x10])))();
  }
LAB_0006ffa2:
  state->recovery_count = 0;
  state->passing_count = 0;
  state->packed_status = 0x44;
  state->failing_count = calibration[5] + 1;
  state->elapsed_count = calibration[7] + 1;
  return;
}



void FUN_0006ffc2(short *param_1,int param_2,int param_3)

{
  short sVar1;
  code *pcVar2;
  
  if (0xfffe < (*((ushort *)camry_host_ptr((uint32_t)(param_2 + 2))))) {
    return;
  }
  if (0xfffe < (*((ushort *)camry_host_ptr((uint32_t)(param_2 + 6))))) {
    return;
  }
  sVar1 = *param_1;
  if (sVar1 == 0) {
LAB_00070018:
    if ((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(param_3 + 0x1c))))) != 0u) {
      (*(int (*)())camry_indirect((uint32_t)(((code *)(uintptr_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(param_3 + 0x1c))))))))();
    }
LAB_00070024:
    if ((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(param_3 + 0x24))))) != 0u) {
      (*(int (*)())camry_indirect((uint32_t)(((code *)(uintptr_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(param_3 + 0x24))))))))();
    }
  }
  else {
    if (sVar1 == 0x11) goto LAB_00070024;
    if (sVar1 != 0x22) {
      if (sVar1 == 0x1100) {
        pcVar2 = ((code *)(uintptr_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(param_3 + 0x10)))));
      }
      else {
        if (sVar1 != 0x2200) goto LAB_00070048;
        pcVar2 = ((code *)(uintptr_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(param_3 + 0x18)))));
      }
      if ((uint32_t)(pcVar2) != 0u) {
        (*(int (*)())camry_indirect((uint32_t)(pcVar2)))();
      }
      goto LAB_00070018;
    }
  }
  if ((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(param_3 + 0x2c))))) != 0u) {
    (*(int (*)())camry_indirect((uint32_t)(((code *)(uintptr_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(param_3 + 0x2c))))))))();
  }
  if ((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(param_3 + 0x40))))) != 0u) {
    (*(int (*)())camry_indirect((uint32_t)(((code *)(uintptr_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(param_3 + 0x40))))))))();
  }
LAB_00070048:
  param_1[5] = 0;
  param_1[2] = 0;
  param_1[0] = 0x44;
  param_1[1] = 0;
  param_1[3] = (*((short *)camry_host_ptr((uint32_t)(param_2 + 2)))) + 1;
  param_1[6] = (*((short *)camry_host_ptr((uint32_t)(param_2 + 6)))) + 1;
  return;
}


