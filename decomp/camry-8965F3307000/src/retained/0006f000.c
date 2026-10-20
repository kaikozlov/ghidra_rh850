#include "common.h"

short dispatch_threshold_counters_with_timed_failure_recovery_6f32e(uint *param_1,ushort *param_2,undefined4 *param_3)

{
  uint8_t stack_record_3c[60];
  ushort uVar1;
  ushort uVar2;
  short sVar3;
  uint uVar4;
  int iVar5;
  undefined4 uVar6;
  ushort uVar7;
  uint uVar8;
  uint32_t pcVar9;
  
  sVar3 = 0x11;
  if (((((camry_host_addr(param_1)==camry_host_addr((uint *)0x0)) || (camry_host_addr(param_2)==camry_host_addr((ushort *)0x0))) || (camry_host_addr(param_3)==camry_host_addr((undefined4 *)0x0)))
      || ((pcVar9 = (uint32_t)((uint32_t)(*param_3)),(uint32_t)(pcVar9) == 0u||
          ((uint32_t)(param_3[1] )==0x0u)))) || ((uint32_t)(param_3[2] )==0x0u)) {
    return 0x22;
  }
  (*((uint16_t *)(stack_record_3c + 12))) = (ushort)param_1[2];
  ((uint16_t *)((stack_record_3c + 6)))[0] = (ushort)param_1[1];
  (*((uint16_t *)(stack_record_3c + 10))) = (*((ushort *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 6))));
  (*((uint16_t *)(stack_record_3c + 18))) = (ushort)param_1[3];
  (*((uint16_t *)(stack_record_3c + 16))) = (*((undefined2 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 10))));
  (*((uint16_t *)(stack_record_3c + 22))) = (*((ushort *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 0xe))));
  (*((uint16_t *)(stack_record_3c + 20))) = (undefined2)param_1[4];
  (*((uint16_t *)(stack_record_3c + 2))) = param_2[3];
  (*((uint16_t *)(stack_record_3c + 0))) = param_2[2];
  uVar1 = *param_2;
  uVar2 = param_2[1];
  (*((uint16_t *)(stack_record_3c + 4))) = param_2[4];
  if ((*((uint16_t *)(stack_record_3c + 10))) == 0) {
    if (uVar1 < ((uint16_t *)((stack_record_3c + 6)))[0]) {
      sVar3 = 0x2200;
    }
    else {
      sVar3 = 0;
      if (((uint16_t *)((stack_record_3c + 6)))[0] != 0) {
        sVar3 = 0x1100;
      }
    }
  }
  else if (uVar2 < (*((uint16_t *)(stack_record_3c + 10)))) {
    if (((*((uint16_t *)(stack_record_3c + 4))) < (*((uint16_t *)(stack_record_3c + 22)))) || ((*((uint16_t *)(stack_record_3c + 2))) < (*((uint16_t *)(stack_record_3c + 18))))) {
      sVar3 = 0x44;
    }
    else {
      sVar3 = 0x22;
    }
  }
  if (sVar3 == 0) {
    iVar5 = (*(int (*)())camry_indirect((uint32_t)(pcVar9)))(camry_host_addr(param_1), camry_host_addr(param_2), camry_host_addr(param_3));
    if (iVar5 == 0x11) {
      if ((uVar1 < ((uint16_t *)((stack_record_3c + 6)))[0]) ||
         (uVar2 = ((uint16_t *)((stack_record_3c + 6)))[0] + 1, uVar7 = ((uint16_t *)((stack_record_3c + 6)))[0] + 1, ((uint16_t *)((stack_record_3c + 6)))[0] = uVar2, uVar1 < uVar7
         )) {
        uVar8 = 0x2200;
      }
      else {
        uVar8 = 0x11001100;
      }
      (*((uint16_t *)(stack_record_3c + 10))) = 0;
    }
    else if (iVar5 == 0x22) {
      ((uint16_t *)((stack_record_3c + 6)))[0] = 0;
      if ((*((uint16_t *)(stack_record_3c + 10))) <= uVar2) {
        (*((uint16_t *)(stack_record_3c + 10))) = (*((uint16_t *)(stack_record_3c + 10))) + 1;
      }
      if ((*((uint16_t *)(stack_record_3c + 12))) < (*((uint16_t *)(stack_record_3c + 10)))) {
        (*((uint16_t *)(stack_record_3c + 12))) = (*((uint16_t *)(stack_record_3c + 10)));
      }
      uVar8 = 0x22;
      if ((*((uint16_t *)(stack_record_3c + 10))) <= uVar2) {
        uVar8 = 0x110011;
      }
    }
    else if ((iVar5 == 0x33) || (iVar5 == 0x44)) {
      (*((uint16_t *)(stack_record_3c + 10))) = 0;
      ((uint16_t *)((stack_record_3c + 6)))[0] = 0;
      uVar8 = 0;
    }
    else {
      uVar8 = 0xffff;
    }
    uVar4 = uVar8 & 0xffff;
    if (uVar4 != 0) {
      if (uVar4 == 0x11) {
        if ((uint32_t)(param_3[7] )!=0x0u) {
          (*(int (*)())camry_indirect((uint32_t)(param_3[7])))();
        }
        pcVar9 = (uint32_t)((uint32_t)(param_3[0xe]));
      }
      else if (uVar4 == 0x22) {
        if ((uint32_t)(param_3[7] )!=0x0u) {
          (*(int (*)())camry_indirect((uint32_t)(param_3[7])))();
        }
        if ((uint32_t)(param_3[9] )!=0x0u) {
          (*(int (*)())camry_indirect((uint32_t)(param_3[9])))();
        }
        pcVar9 = (uint32_t)((uint32_t)(param_3[0xf]));
      }
      else if (uVar4 == 0x1100) {
        if ((uint32_t)(param_3[3] )!=0x0u) {
          (*(int (*)())camry_indirect((uint32_t)(param_3[3])))();
        }
        pcVar9 = (uint32_t)((uint32_t)(param_3[0xc]));
      }
      else {
        if (uVar4 != 0x2200) {
          uVar8 = 0;
          goto LAB_0006f8dc;
        }
        if ((uint32_t)(param_3[3] )!=0x0u) {
          (*(int (*)())camry_indirect((uint32_t)(param_3[3])))();
        }
        if ((uint32_t)(param_3[5] )!=0x0u) {
          (*(int (*)())camry_indirect((uint32_t)(param_3[5])))();
        }
        pcVar9 = (uint32_t)((uint32_t)(param_3[0xd]));
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
      if ((uVar1 < ((uint16_t *)((stack_record_3c + 6)))[0]) ||
         (uVar2 = ((uint16_t *)((stack_record_3c + 6)))[0] + 1, uVar7 = ((uint16_t *)((stack_record_3c + 6)))[0] + 1, ((uint16_t *)((stack_record_3c + 6)))[0] = uVar2, uVar1 < uVar7
         )) {
        uVar8 = 0x2200;
      }
      else {
        uVar8 = 0x11001100;
      }
      (*((uint16_t *)(stack_record_3c + 10))) = 0;
    }
    else if (iVar5 == 0x22) {
      ((uint16_t *)((stack_record_3c + 6)))[0] = 0;
      if ((*((uint16_t *)(stack_record_3c + 10))) <= uVar2) {
        (*((uint16_t *)(stack_record_3c + 10))) = (*((uint16_t *)(stack_record_3c + 10))) + 1;
      }
      if ((*((uint16_t *)(stack_record_3c + 12))) < (*((uint16_t *)(stack_record_3c + 10)))) {
        (*((uint16_t *)(stack_record_3c + 12))) = (*((uint16_t *)(stack_record_3c + 10)));
      }
      uVar8 = 0x22;
      if ((*((uint16_t *)(stack_record_3c + 10))) <= uVar2) {
        uVar8 = 0x110011;
      }
    }
    else if ((iVar5 == 0x33) || (iVar5 == 0x44)) {
      (*((uint16_t *)(stack_record_3c + 10))) = 0;
      ((uint16_t *)((stack_record_3c + 6)))[0] = 0;
      uVar8 = 0;
    }
    else {
      uVar8 = 0xffff;
    }
    uVar4 = uVar8 & 0xffff;
    if (uVar4 == 0) {
      if ((uint32_t)(param_3[8] )!=0x0u) {
        (*(int (*)())camry_indirect((uint32_t)(param_3[8])))(camry_host_addr(param_1), camry_host_addr(param_2), camry_host_addr(param_3));
      }
    }
    else {
      if (uVar4 == 0x11) {
        pcVar9 = (uint32_t)((uint32_t)(param_3[0xe]));
      }
      else if (uVar4 == 0x22) {
        if ((uint32_t)(param_3[9] )!=0x0u) {
          (*(int (*)())camry_indirect((uint32_t)(param_3[9])))();
        }
        pcVar9 = (uint32_t)((uint32_t)(param_3[0xf]));
      }
      else if (uVar4 == 0x1100) {
        if ((uint32_t)(param_3[8] )!=0x0u) {
          (*(int (*)())camry_indirect((uint32_t)(param_3[8])))();
        }
        if ((uint32_t)(param_3[3] )!=0x0u) {
          (*(int (*)())camry_indirect((uint32_t)(param_3[3])))();
        }
        pcVar9 = (uint32_t)((uint32_t)(param_3[0xc]));
      }
      else {
        if (uVar4 != 0x2200) {
          if ((uint32_t)(param_3[0xe] )!=0x0u) {
            (*(int (*)())camry_indirect((uint32_t)(param_3[0xe])))();
          }
          uVar8 = 0x11;
          goto LAB_0006f8dc;
        }
        if ((uint32_t)(param_3[8] )!=0x0u) {
          (*(int (*)())camry_indirect((uint32_t)(param_3[8])))();
        }
        if ((uint32_t)(param_3[3] )!=0x0u) {
          (*(int (*)())camry_indirect((uint32_t)(param_3[3])))();
        }
        if ((uint32_t)(param_3[5] )!=0x0u) {
          (*(int (*)())camry_indirect((uint32_t)(param_3[5])))();
        }
        pcVar9 = (uint32_t)((uint32_t)(param_3[0xd]));
      }
      if ((uint32_t)(pcVar9) != 0u) {
        (*(int (*)())camry_indirect((uint32_t)(pcVar9)))();
      }
    }
    goto LAB_0006f8dc;
  }
  if (sVar3 == 0x22) {
    uVar6 = (*(int (*)())camry_indirect((uint32_t)(param_3[2])))();
    uVar8 = update_total_and_consecutive_event_counters_with_peak_71194(uVar6,((uint16_t *)((stack_record_3c + 6))),((uint16_t *)(stack_record_3c)));
    uVar4 = uVar8 & 0xffff;
    if (uVar4 == 0) {
      pcVar9 = (uint32_t)((uint32_t)(param_3[10]));
    }
    else if (uVar4 == 0x22) {
      pcVar9 = (uint32_t)((uint32_t)(param_3[0xf]));
    }
    else {
      if (uVar4 != 0x44) {
        if ((uint32_t)(param_3[0xf] )!=0x0u) {
          (*(int (*)())camry_indirect((uint32_t)(param_3[0xf])))(camry_host_addr(param_1), camry_host_addr(param_2), camry_host_addr(param_3));
        }
        uVar8 = 0x22;
        goto LAB_0006f8dc;
      }
      if ((uint32_t)(param_3[0xb] )!=0x0u) {
        (*(int (*)())camry_indirect((uint32_t)(param_3[0xb])))();
      }
      pcVar9 = (uint32_t)((uint32_t)(param_3[0x10]));
    }
    if ((uint32_t)(pcVar9) != 0u) {
      (*(int (*)())camry_indirect((uint32_t)(pcVar9)))();
    }
    goto LAB_0006f8dc;
  }
  if (sVar3 == 0x1100) {
    iVar5 = (*(int (*)())camry_indirect((uint32_t)(pcVar9)))();
    if (iVar5 == 0x11) {
      if ((uVar1 < ((uint16_t *)((stack_record_3c + 6)))[0]) ||
         (uVar2 = ((uint16_t *)((stack_record_3c + 6)))[0] + 1, uVar7 = ((uint16_t *)((stack_record_3c + 6)))[0] + 1, ((uint16_t *)((stack_record_3c + 6)))[0] = uVar2, uVar1 < uVar7
         )) {
        uVar8 = 0x2200;
      }
      else {
        uVar8 = 0x11001100;
      }
      (*((uint16_t *)(stack_record_3c + 10))) = 0;
    }
    else if (iVar5 == 0x22) {
      ((uint16_t *)((stack_record_3c + 6)))[0] = 0;
      if ((*((uint16_t *)(stack_record_3c + 10))) <= uVar2) {
        (*((uint16_t *)(stack_record_3c + 10))) = (*((uint16_t *)(stack_record_3c + 10))) + 1;
      }
      if ((*((uint16_t *)(stack_record_3c + 12))) < (*((uint16_t *)(stack_record_3c + 10)))) {
        (*((uint16_t *)(stack_record_3c + 12))) = (*((uint16_t *)(stack_record_3c + 10)));
      }
      uVar8 = 0x22;
      if ((*((uint16_t *)(stack_record_3c + 10))) <= uVar2) {
        uVar8 = 0x110011;
      }
    }
    else if ((iVar5 == 0x33) || (iVar5 == 0x44)) {
      (*((uint16_t *)(stack_record_3c + 10))) = 0;
      ((uint16_t *)((stack_record_3c + 6)))[0] = 0;
      uVar8 = 0;
    }
    else {
      uVar8 = 0xffff;
    }
    uVar4 = uVar8 & 0xffff;
    if (uVar4 == 0) {
      if ((uint32_t)(param_3[4] )!=0x0u) {
        (*(int (*)())camry_indirect((uint32_t)(param_3[4])))();
      }
    }
    else {
      if (uVar4 == 0x11) {
        if ((uint32_t)(param_3[4] )!=0x0u) {
          (*(int (*)())camry_indirect((uint32_t)(param_3[4])))();
        }
        if ((uint32_t)(param_3[7] )!=0x0u) {
          (*(int (*)())camry_indirect((uint32_t)(param_3[7])))();
        }
        pcVar9 = (uint32_t)((uint32_t)(param_3[0xe]));
      }
      else if (uVar4 == 0x22) {
        if ((uint32_t)(param_3[4] )!=0x0u) {
          (*(int (*)())camry_indirect((uint32_t)(param_3[4])))();
        }
        if ((uint32_t)(param_3[7] )!=0x0u) {
          (*(int (*)())camry_indirect((uint32_t)(param_3[7])))(camry_host_addr(param_1), camry_host_addr(param_2), camry_host_addr(param_3));
        }
        if ((uint32_t)(param_3[9] )!=0x0u) {
          (*(int (*)())camry_indirect((uint32_t)(param_3[9])))();
        }
        pcVar9 = (uint32_t)((uint32_t)(param_3[0xf]));
      }
      else if (uVar4 == 0x1100) {
        pcVar9 = (uint32_t)((uint32_t)(param_3[0xc]));
      }
      else {
        if (uVar4 != 0x2200) {
          if ((uint32_t)(param_3[0xc] )!=0x0u) {
            (*(int (*)())camry_indirect((uint32_t)(param_3[0xc])))();
          }
          uVar8 = 0x1100;
          goto LAB_0006f8dc;
        }
        if ((uint32_t)(param_3[5] )!=0x0u) {
          (*(int (*)())camry_indirect((uint32_t)(param_3[5])))();
        }
        pcVar9 = (uint32_t)((uint32_t)(param_3[0xd]));
      }
      if ((uint32_t)(pcVar9) != 0u) {
        (*(int (*)())camry_indirect((uint32_t)(pcVar9)))();
      }
    }
    goto LAB_0006f8dc;
  }
  if (sVar3 != 0x2200) {
    if ((uint32_t)(param_3[0x10] )!=0x0u) {
      (*(int (*)())camry_indirect((uint32_t)(param_3[0x10])))();
    }
    uVar8 = 0x44;
    goto LAB_0006f8dc;
  }
  iVar5 = (*(int (*)())camry_indirect((uint32_t)(pcVar9)))();
  if (iVar5 == 0x11) {
LAB_0006f448:
    (*((uint16_t *)(stack_record_3c + 10))) = 0;
LAB_0006f44c:
    uVar8 = 0x2200;
  }
  else {
    if (iVar5 != 0x22) {
      if ((iVar5 == 0x33) || (iVar5 == 0x44)) goto LAB_0006f448;
      goto LAB_0006f44c;
    }
    ((uint16_t *)((stack_record_3c + 6)))[0] = 0;
    if ((*((uint16_t *)(stack_record_3c + 10))) <= uVar2) {
      (*((uint16_t *)(stack_record_3c + 10))) = (*((uint16_t *)(stack_record_3c + 10))) + 1;
    }
    if ((*((uint16_t *)(stack_record_3c + 12))) < (*((uint16_t *)(stack_record_3c + 10)))) {
      (*((uint16_t *)(stack_record_3c + 12))) = (*((uint16_t *)(stack_record_3c + 10)));
    }
    uVar8 = 0x22;
    if ((*((uint16_t *)(stack_record_3c + 10))) <= uVar2) {
      uVar8 = 0x110011;
    }
  }
  uVar4 = uVar8 & 0xffff;
  if (uVar4 == 0) {
    if ((uint32_t)(param_3[6] )!=0x0u) {
      (*(int (*)())camry_indirect((uint32_t)(param_3[6])))();
    }
  }
  else {
    if (uVar4 == 0x11) {
      if ((uint32_t)(param_3[6] )!=0x0u) {
        (*(int (*)())camry_indirect((uint32_t)(param_3[6])))();
      }
      if ((uint32_t)(param_3[7] )!=0x0u) {
        (*(int (*)())camry_indirect((uint32_t)(param_3[7])))();
      }
      pcVar9 = (uint32_t)((uint32_t)(param_3[0xe]));
    }
    else if (uVar4 == 0x22) {
      if ((uint32_t)(param_3[6] )!=0x0u) {
        (*(int (*)())camry_indirect((uint32_t)(param_3[6])))(camry_host_addr(param_1), camry_host_addr(param_2), camry_host_addr(param_3));
      }
      if ((uint32_t)(param_3[7] )!=0x0u) {
        (*(int (*)())camry_indirect((uint32_t)(param_3[7])))();
      }
      if ((uint32_t)(param_3[9] )!=0x0u) {
        (*(int (*)())camry_indirect((uint32_t)(param_3[9])))();
      }
      pcVar9 = (uint32_t)((uint32_t)(param_3[0xf]));
    }
    else {
      pcVar9 = (uint32_t)((uint32_t)(param_3[0xd]));
      if (uVar4 != 0x2200) {
        if ((uint32_t)(pcVar9) != 0u) {
          (*(int (*)())camry_indirect((uint32_t)(pcVar9)))();
        }
        uVar8 = 0x2200;
        goto LAB_0006f8dc;
      }
    }
    if ((uint32_t)(pcVar9) != 0u) {
      (*(int (*)())camry_indirect((uint32_t)(pcVar9)))(camry_host_addr(param_1), camry_host_addr(param_2), camry_host_addr(param_3));
    }
  }
LAB_0006f8dc:
  *param_1 = uVar8;
  *(ushort *)(param_1 + 1) = ((uint16_t *)((stack_record_3c + 6)))[0];
  (*((ushort *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 6)))) = (*((uint16_t *)(stack_record_3c + 10)));
  *(ushort *)(param_1 + 2) = (*((uint16_t *)(stack_record_3c + 12)));
  (*((undefined2 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 10)))) = (*((uint16_t *)(stack_record_3c + 16)));
  *(ushort *)(param_1 + 3) = (*((uint16_t *)(stack_record_3c + 18)));
  (*((ushort *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 0xe)))) = (*((uint16_t *)(stack_record_3c + 22)));
  *(undefined2 *)(param_1 + 4) = (*((uint16_t *)(stack_record_3c + 20)));
  return 0x11;
}

undefined4 dispatch_windowed_thresholds_with_timed_consecutive_recovery_6f910(uint *param_1,ushort *param_2,undefined4 *param_3)

{
  uint8_t stack_record_44[68];
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
  uint32_t pcVar11;
  
  uVar10 = 0x11;
  if (((((camry_host_addr(param_1)==camry_host_addr((uint *)0x0)) || (camry_host_addr(param_2)==camry_host_addr((ushort *)0x0))) || (camry_host_addr(param_3)==camry_host_addr((undefined4 *)0x0)))
      || ((pcVar11 = (uint32_t)((uint32_t)(*param_3)),(uint32_t)(pcVar11) == 0u||
          ((uint32_t)(param_3[1] )==0x0u)))) || ((uint32_t)(param_3[2] )==0x0u)) {
    return 0x22;
  }
  (*((uint16_t *)(stack_record_44 + 14))) = (*((ushort *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 10))));
  (*((uint16_t *)(stack_record_44 + 8))) = (*((ushort *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 6))));
  (*((uint16_t *)(stack_record_44 + 6))) = (ushort)param_1[1];
  (*((uint16_t *)(stack_record_44 + 22))) = (ushort)param_1[4];
  (*((uint16_t *)(stack_record_44 + 12))) = (ushort)param_1[3];
  (*((uint16_t *)(stack_record_44 + 10))) = (ushort)param_1[2];
  (*((uint16_t *)(stack_record_44 + 16))) = (*((undefined2 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 0xe))));
  uVar2 = *param_2;
  (*((uint16_t *)(stack_record_44 + 0))) = param_2[4];
  uVar3 = param_2[1];
  uVar5 = param_2[2];
  uVar4 = param_2[3];
  (*((uint16_t *)(stack_record_44 + 2))) = param_2[5];
  if ((*((uint16_t *)(stack_record_44 + 10))) == 0) {
    if (uVar2 < (*((uint16_t *)(stack_record_44 + 6)))) {
      uVar6 = 0x2200;
    }
    else {
      uVar6 = 0;
      if ((*((uint16_t *)(stack_record_44 + 6))) != 0) {
        uVar6 = 0x1100;
      }
    }
  }
  else {
    uVar6 = uVar10;
    if ((uVar5 < (*((uint16_t *)(stack_record_44 + 10)))) && (uVar6 = 0x44, (*((uint16_t *)(stack_record_44 + 22))) <= (*((uint16_t *)(stack_record_44 + 2))))) {
      uVar6 = 0x22;
    }
  }
  if (uVar6 == 0) {
    iVar8 = (*(int (*)())camry_indirect((uint32_t)(pcVar11)))(camry_host_addr(param_1), camry_host_addr(param_2), camry_host_addr(param_3));
    if (iVar8 == 0x11) {
      if ((uVar3 < (*((uint16_t *)(stack_record_44 + 8)))) || (uVar3 < (ushort)((*((uint16_t *)(stack_record_44 + 8))) + 1))) {
        (*((uint16_t *)(stack_record_44 + 8))) = 0;
        (*((uint16_t *)(stack_record_44 + 6))) = 0;
        uVar10 = 0;
      }
      else if ((uVar2 < (*((uint16_t *)(stack_record_44 + 6)))) ||
              (uVar3 = (*((uint16_t *)(stack_record_44 + 6))) + 1, uVar5 = (*((uint16_t *)(stack_record_44 + 6))) + 1, (*((uint16_t *)(stack_record_44 + 6))) = uVar3, uVar2 < uVar5)) {
        uVar10 = 0x2200;
        (*((uint16_t *)(stack_record_44 + 8))) = (*((uint16_t *)(stack_record_44 + 8))) + 1;
      }
      else {
        uVar10 = 0x11001100;
        (*((uint16_t *)(stack_record_44 + 8))) = (*((uint16_t *)(stack_record_44 + 8))) + 1;
      }
LAB_0006fcfe:
      (*((uint16_t *)(stack_record_44 + 14))) = 0;
      (*((uint16_t *)(stack_record_44 + 10))) = 0;
    }
    else if (iVar8 == 0x22) {
      (*((uint16_t *)(stack_record_44 + 6))) = 0;
      (*((uint16_t *)(stack_record_44 + 8))) = 0;
      if ((uVar4 < (*((uint16_t *)(stack_record_44 + 14)))) || (uVar2 = (*((uint16_t *)(stack_record_44 + 14))) + 1, uVar4 < (ushort)((*((uint16_t *)(stack_record_44 + 14))) + 1))) {
        uVar10 = 0;
        goto LAB_0006fcfe;
      }
      if ((*((uint16_t *)(stack_record_44 + 10))) <= uVar5) {
        (*((uint16_t *)(stack_record_44 + 10))) = (*((uint16_t *)(stack_record_44 + 10))) + 1;
      }
      if ((*((uint16_t *)(stack_record_44 + 12))) < (*((uint16_t *)(stack_record_44 + 10)))) {
        (*((uint16_t *)(stack_record_44 + 12))) = (*((uint16_t *)(stack_record_44 + 10)));
      }
      uVar10 = 0x22;
      (*((uint16_t *)(stack_record_44 + 14))) = uVar2;
      if ((*((uint16_t *)(stack_record_44 + 10))) <= uVar5) {
        uVar10 = 0x110011;
      }
    }
    else {
      if ((iVar8 == 0x33) || (iVar8 == 0x44)) {
        (*((uint16_t *)(stack_record_44 + 8))) = 0;
        (*((uint16_t *)(stack_record_44 + 6))) = 0;
        uVar10 = 0;
        goto LAB_0006fcfe;
      }
      uVar10 = 0;
    }
    uVar6 = uVar10 & 0xffff;
    if (uVar6 != 0) {
      if (uVar6 == 0x11) {
        if ((uint32_t)(param_3[7] )!=0x0u) {
          (*(int (*)())camry_indirect((uint32_t)(param_3[7])))();
        }
        pcVar11 = (uint32_t)((uint32_t)(param_3[0xe]));
      }
      else if (uVar6 == 0x22) {
        if ((uint32_t)(param_3[7] )!=0x0u) {
          (*(int (*)())camry_indirect((uint32_t)(param_3[7])))();
        }
        if ((uint32_t)(param_3[9] )!=0x0u) {
          (*(int (*)())camry_indirect((uint32_t)(param_3[9])))();
        }
        pcVar11 = (uint32_t)((uint32_t)(param_3[0xf]));
      }
      else if (uVar6 == 0x1100) {
        if ((uint32_t)(param_3[3] )!=0x0u) {
          (*(int (*)())camry_indirect((uint32_t)(param_3[3])))();
        }
        pcVar11 = (uint32_t)((uint32_t)(param_3[0xc]));
      }
      else {
        if (uVar6 != 0x2200) {
          uVar10 = 0;
          goto LAB_0006fee8;
        }
        if ((uint32_t)(param_3[3] )!=0x0u) {
          (*(int (*)())camry_indirect((uint32_t)(param_3[3])))();
        }
        if ((uint32_t)(param_3[5] )!=0x0u) {
          (*(int (*)())camry_indirect((uint32_t)(param_3[5])))();
        }
        pcVar11 = (uint32_t)((uint32_t)(param_3[0xd]));
      }
      if ((uint32_t)(pcVar11) != 0u) {
        (*(int (*)())camry_indirect((uint32_t)(pcVar11)))();
      }
    }
    goto LAB_0006fee8;
  }
  if (uVar6 == 0x11) {
    iVar8 = (*(int (*)())camry_indirect((uint32_t)(param_3[1])))();
    if ((uVar4 < (*((uint16_t *)(stack_record_44 + 14)))) || (uVar2 = (*((uint16_t *)(stack_record_44 + 14))) + 1, uVar4 < (ushort)((*((uint16_t *)(stack_record_44 + 14))) + 1))) {
LAB_0006fe08:
      (*((uint16_t *)(stack_record_44 + 14))) = 0;
      (*((uint16_t *)(stack_record_44 + 10))) = 0;
      (*((uint16_t *)(stack_record_44 + 8))) = 0;
      (*((uint16_t *)(stack_record_44 + 6))) = 0;
      uVar6 = 0;
    }
    else {
      uVar6 = uVar10;
      (*((uint16_t *)(stack_record_44 + 14))) = uVar2;
      if (iVar8 == 0x11) {
LAB_0006fdd2:
        (*((uint16_t *)(stack_record_44 + 6))) = 0;
        (*((uint16_t *)(stack_record_44 + 8))) = 0;
      }
      else if (iVar8 == 0x22) {
        (*((uint16_t *)(stack_record_44 + 6))) = 0;
        (*((uint16_t *)(stack_record_44 + 8))) = 0;
        if ((*((uint16_t *)(stack_record_44 + 10))) <= uVar5) {
          (*((uint16_t *)(stack_record_44 + 10))) = (*((uint16_t *)(stack_record_44 + 10))) + 1;
        }
        if ((*((uint16_t *)(stack_record_44 + 12))) < (*((uint16_t *)(stack_record_44 + 10)))) {
          (*((uint16_t *)(stack_record_44 + 12))) = (*((uint16_t *)(stack_record_44 + 10)));
        }
        uVar6 = 0x22;
        if ((*((uint16_t *)(stack_record_44 + 10))) <= uVar5) {
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
      if ((uint32_t)(param_3[8] )!=0x0u) {
        (*(int (*)())camry_indirect((uint32_t)(param_3[8])))(camry_host_addr(param_1), camry_host_addr(param_2), camry_host_addr(param_3));
      }
    }
    else {
      if (uVar7 == 0x11) {
        pcVar11 = (uint32_t)((uint32_t)(param_3[0xe]));
      }
      else {
        if (uVar7 != 0x22) {
          if ((uint32_t)(param_3[0xe] )!=0x0u) {
            (*(int (*)())camry_indirect((uint32_t)(param_3[0xe])))();
          }
          goto LAB_0006fee8;
        }
        if ((uint32_t)(param_3[9] )!=0x0u) {
          (*(int (*)())camry_indirect((uint32_t)(param_3[9])))();
        }
        pcVar11 = (uint32_t)((uint32_t)(param_3[0xf]));
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
    uVar10 = update_total_and_event11_counters_reset_on_event22_70fa4(uVar9,((uint16_t *)((stack_record_44 + 6))),((uint16_t *)(stack_record_44)));
    uVar6 = uVar10 & 0xffff;
    if (uVar6 == 0) {
      pcVar11 = (uint32_t)((uint32_t)(param_3[10]));
    }
    else if (uVar6 == 0x22) {
      pcVar11 = (uint32_t)((uint32_t)(param_3[0xf]));
    }
    else {
      if (uVar6 != 0x44) {
        if ((uint32_t)(param_3[0xf] )!=0x0u) {
          (*(int (*)())camry_indirect((uint32_t)(param_3[0xf])))();
        }
        uVar10 = 0x22;
        goto LAB_0006fee8;
      }
      if ((uint32_t)(param_3[0xb] )!=0x0u) {
        (*(int (*)())camry_indirect((uint32_t)(param_3[0xb])))();
      }
      pcVar11 = (uint32_t)((uint32_t)(param_3[0x10]));
    }
    if ((uint32_t)(pcVar11) != 0u) {
      (*(int (*)())camry_indirect((uint32_t)(pcVar11)))();
    }
    goto LAB_0006fee8;
  }
  if (uVar6 != 0x1100) {
    if (uVar6 != 0x2200) {
      if ((uint32_t)(param_3[0x10] )!=0x0u) {
        (*(int (*)())camry_indirect((uint32_t)(param_3[0x10])))();
      }
      uVar10 = 0x44;
      goto LAB_0006fee8;
    }
    iVar8 = (*(int (*)())camry_indirect((uint32_t)(pcVar11)))();
    if (iVar8 == 0x11) {
LAB_0006fa42:
      (*((uint16_t *)(stack_record_44 + 10))) = 0;
      (*((uint16_t *)(stack_record_44 + 14))) = 0;
LAB_0006fa48:
      uVar10 = 0x2200;
    }
    else {
      if (iVar8 != 0x22) {
        if ((iVar8 == 0x33) || (iVar8 == 0x44)) goto LAB_0006fa42;
        goto LAB_0006fa48;
      }
      (*((uint16_t *)(stack_record_44 + 6))) = 0;
      (*((uint16_t *)(stack_record_44 + 8))) = 0;
      if ((uVar4 < (*((uint16_t *)(stack_record_44 + 14)))) || (uVar2 = (*((uint16_t *)(stack_record_44 + 14))) + 1, uVar4 < (ushort)((*((uint16_t *)(stack_record_44 + 14))) + 1))) {
        (*((uint16_t *)(stack_record_44 + 10))) = 0;
        uVar10 = 0;
        (*((uint16_t *)(stack_record_44 + 14))) = 0;
      }
      else {
        if ((*((uint16_t *)(stack_record_44 + 10))) <= uVar5) {
          (*((uint16_t *)(stack_record_44 + 10))) = (*((uint16_t *)(stack_record_44 + 10))) + 1;
        }
        if ((*((uint16_t *)(stack_record_44 + 12))) < (*((uint16_t *)(stack_record_44 + 10)))) {
          (*((uint16_t *)(stack_record_44 + 12))) = (*((uint16_t *)(stack_record_44 + 10)));
        }
        uVar10 = 0x22;
        (*((uint16_t *)(stack_record_44 + 14))) = uVar2;
        if ((*((uint16_t *)(stack_record_44 + 10))) <= uVar5) {
          uVar10 = 0x110011;
        }
      }
    }
    uVar6 = uVar10 & 0xffff;
    if (uVar6 == 0) {
      if ((uint32_t)(param_3[6] )!=0x0u) {
        (*(int (*)())camry_indirect((uint32_t)(param_3[6])))(camry_host_addr(param_1), camry_host_addr(param_2), camry_host_addr(param_3));
      }
    }
    else {
      if (uVar6 == 0x11) {
        if ((uint32_t)(param_3[6] )!=0x0u) {
          (*(int (*)())camry_indirect((uint32_t)(param_3[6])))();
        }
        if ((uint32_t)(param_3[7] )!=0x0u) {
          (*(int (*)())camry_indirect((uint32_t)(param_3[7])))();
        }
        pcVar11 = (uint32_t)((uint32_t)(param_3[0xe]));
      }
      else if (uVar6 == 0x22) {
        if ((uint32_t)(param_3[6] )!=0x0u) {
          (*(int (*)())camry_indirect((uint32_t)(param_3[6])))();
        }
        if ((uint32_t)(param_3[7] )!=0x0u) {
          (*(int (*)())camry_indirect((uint32_t)(param_3[7])))();
        }
        if ((uint32_t)(param_3[9] )!=0x0u) {
          (*(int (*)())camry_indirect((uint32_t)(param_3[9])))();
        }
        pcVar11 = (uint32_t)((uint32_t)(param_3[0xf]));
      }
      else {
        pcVar11 = (uint32_t)((uint32_t)(param_3[0xd]));
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
  iVar8 = (*(int (*)())camry_indirect((uint32_t)(pcVar11)))(camry_host_addr(param_1), camry_host_addr(param_2), camry_host_addr(param_3));
  if ((uVar3 < (*((uint16_t *)(stack_record_44 + 8)))) || (uVar1 = (*((uint16_t *)(stack_record_44 + 8))) + 1, uVar3 < (ushort)((*((uint16_t *)(stack_record_44 + 8))) + 1))) {
LAB_0006fb8c:
    (*((uint16_t *)(stack_record_44 + 8))) = 0;
    (*((uint16_t *)(stack_record_44 + 6))) = 0;
    uVar10 = 0;
LAB_0006fb94:
    (*((uint16_t *)(stack_record_44 + 14))) = 0;
    (*((uint16_t *)(stack_record_44 + 10))) = 0;
  }
  else {
    (*((uint16_t *)(stack_record_44 + 8))) = uVar1;
    if (iVar8 == 0x11) {
      if ((uVar2 < (*((uint16_t *)(stack_record_44 + 6)))) ||
         (uVar3 = (*((uint16_t *)(stack_record_44 + 6))) + 1, uVar5 = (*((uint16_t *)(stack_record_44 + 6))) + 1, (*((uint16_t *)(stack_record_44 + 6))) = uVar3, uVar2 < uVar5)) {
        uVar10 = 0x2200;
      }
      else {
        uVar10 = 0x11001100;
      }
      goto LAB_0006fb94;
    }
    if (iVar8 == 0x22) {
      (*((uint16_t *)(stack_record_44 + 6))) = 0;
      (*((uint16_t *)(stack_record_44 + 8))) = 0;
      if ((uVar4 < (*((uint16_t *)(stack_record_44 + 14)))) || (uVar2 = (*((uint16_t *)(stack_record_44 + 14))) + 1, uVar4 < (ushort)((*((uint16_t *)(stack_record_44 + 14))) + 1))) {
        uVar10 = 0;
        goto LAB_0006fb94;
      }
      if ((*((uint16_t *)(stack_record_44 + 10))) <= uVar5) {
        (*((uint16_t *)(stack_record_44 + 10))) = (*((uint16_t *)(stack_record_44 + 10))) + 1;
      }
      if ((*((uint16_t *)(stack_record_44 + 12))) < (*((uint16_t *)(stack_record_44 + 10)))) {
        (*((uint16_t *)(stack_record_44 + 12))) = (*((uint16_t *)(stack_record_44 + 10)));
      }
      uVar10 = 0x22;
      (*((uint16_t *)(stack_record_44 + 14))) = uVar2;
      if ((*((uint16_t *)(stack_record_44 + 10))) <= uVar5) {
        uVar10 = 0x110011;
      }
    }
    else {
      if (iVar8 == 0x33) {
        (*((uint16_t *)(stack_record_44 + 10))) = 0;
        (*((uint16_t *)(stack_record_44 + 14))) = 0;
      }
      else if (iVar8 == 0x44) goto LAB_0006fb8c;
      uVar10 = 0x1100;
    }
  }
  uVar6 = uVar10 & 0xffff;
  if (uVar6 == 0) {
    if ((uint32_t)(param_3[4] )!=0x0u) {
      (*(int (*)())camry_indirect((uint32_t)(param_3[4])))();
    }
  }
  else {
    if (uVar6 == 0x11) {
      if ((uint32_t)(param_3[4] )!=0x0u) {
        (*(int (*)())camry_indirect((uint32_t)(param_3[4])))();
      }
      if ((uint32_t)(param_3[7] )!=0x0u) {
        (*(int (*)())camry_indirect((uint32_t)(param_3[7])))();
      }
      pcVar11 = (uint32_t)((uint32_t)(param_3[0xe]));
    }
    else if (uVar6 == 0x22) {
      if ((uint32_t)(param_3[4] )!=0x0u) {
        (*(int (*)())camry_indirect((uint32_t)(param_3[4])))();
      }
      if ((uint32_t)(param_3[7] )!=0x0u) {
        (*(int (*)())camry_indirect((uint32_t)(param_3[7])))(camry_host_addr(param_1), camry_host_addr(param_2), camry_host_addr(param_3));
      }
      if ((uint32_t)(param_3[9] )!=0x0u) {
        (*(int (*)())camry_indirect((uint32_t)(param_3[9])))();
      }
      pcVar11 = (uint32_t)((uint32_t)(param_3[0xf]));
    }
    else if (uVar6 == 0x1100) {
      pcVar11 = (uint32_t)((uint32_t)(param_3[0xc]));
    }
    else {
      if (uVar6 != 0x2200) {
        if ((uint32_t)(param_3[0xc] )!=0x0u) {
          (*(int (*)())camry_indirect((uint32_t)(param_3[0xc])))();
        }
        uVar10 = 0x1100;
        goto LAB_0006fee8;
      }
      if ((uint32_t)(param_3[5] )!=0x0u) {
        (*(int (*)())camry_indirect((uint32_t)(param_3[5])))();
      }
      pcVar11 = (uint32_t)((uint32_t)(param_3[0xd]));
    }
    if ((uint32_t)(pcVar11) != 0u) {
      (*(int (*)())camry_indirect((uint32_t)(pcVar11)))(camry_host_addr(param_1), camry_host_addr(param_2), camry_host_addr(param_3));
    }
  }
LAB_0006fee8:
  *param_1 = uVar10;
  *(ushort *)(param_1 + 1) = (*((uint16_t *)(stack_record_44 + 6)));
  (*((ushort *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 6)))) = (*((uint16_t *)(stack_record_44 + 8)));
  *(ushort *)(param_1 + 2) = (*((uint16_t *)(stack_record_44 + 10)));
  (*((ushort *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 10)))) = (*((uint16_t *)(stack_record_44 + 14)));
  *(ushort *)(param_1 + 3) = (*((uint16_t *)(stack_record_44 + 12)));
  (*((undefined2 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 0xe)))) = (*((uint16_t *)(stack_record_44 + 16)));
  *(ushort *)(param_1 + 4) = (*((uint16_t *)(stack_record_44 + 22)));
  return 0x11;
}

void force_monitor_escalation
               (F33EscalatingMonitorState *state,ushort *calibration,uint *callbacks)

{
  short sVar1;
  uint32_t pcVar2;
  
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
      (*(int (*)())camry_indirect((uint32_t)(callbacks[7])))(camry_host_addr(state), camry_host_addr(calibration), camry_host_addr(callbacks));
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
        pcVar2 = (uint32_t)(callbacks[4]);
      }
      else {
        if (sVar1 != 0x2200) goto LAB_0006ffa2;
        pcVar2 = (uint32_t)(callbacks[6]);
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

void force_state44_with_two_thresholds_exceeded_6ffc2(short *param_1,int param_2,int param_3)

{
  short sVar1;
  uint32_t pcVar2;
  
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
      (*(int (*)())camry_indirect((uint32_t)(((((code *)(uintptr_t)((uint32_t)((uintptr_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(param_3 + 0x1c))))))))))))(camry_host_addr(param_1), param_2, param_3);
    }
LAB_00070024:
    if ((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(param_3 + 0x24))))) != 0u) {
      (*(int (*)())camry_indirect((uint32_t)(((((code *)(uintptr_t)((uint32_t)((uintptr_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(param_3 + 0x24))))))))))))();
    }
  }
  else {
    if (sVar1 == 0x11) goto LAB_00070024;
    if (sVar1 != 0x22) {
      if (sVar1 == 0x1100) {
        pcVar2 = (uint32_t)((uintptr_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(param_3 + 0x10)))));
      }
      else {
        if (sVar1 != 0x2200) goto LAB_00070048;
        pcVar2 = (uint32_t)((uintptr_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(param_3 + 0x18)))));
      }
      if ((uint32_t)(pcVar2) != 0u) {
        (*(int (*)())camry_indirect((uint32_t)(pcVar2)))();
      }
      goto LAB_00070018;
    }
  }
  if ((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(param_3 + 0x2c))))) != 0u) {
    (*(int (*)())camry_indirect((uint32_t)(((((code *)(uintptr_t)((uint32_t)((uintptr_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(param_3 + 0x2c))))))))))))();
  }
  if ((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(param_3 + 0x40))))) != 0u) {
    (*(int (*)())camry_indirect((uint32_t)(((((code *)(uintptr_t)((uint32_t)((uintptr_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(param_3 + 0x40))))))))))))();
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
