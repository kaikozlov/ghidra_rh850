#include "common.h"

undefined4 dispatch_windowed_thresholds_with_timed_accumulated_recovery_6e140(uint *param_1,ushort *param_2,undefined4 *param_3)

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
LAB_0006e52e:
      (*((uint16_t *)(stack_record_44 + 14))) = 0;
      (*((uint16_t *)(stack_record_44 + 10))) = 0;
    }
    else if (iVar8 == 0x22) {
      (*((uint16_t *)(stack_record_44 + 6))) = 0;
      (*((uint16_t *)(stack_record_44 + 8))) = 0;
      if ((uVar4 < (*((uint16_t *)(stack_record_44 + 14)))) || (uVar2 = (*((uint16_t *)(stack_record_44 + 14))) + 1, uVar4 < (ushort)((*((uint16_t *)(stack_record_44 + 14))) + 1))) {
        uVar10 = 0;
        goto LAB_0006e52e;
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
        goto LAB_0006e52e;
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
          goto LAB_0006e718;
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
    goto LAB_0006e718;
  }
  if (uVar6 == 0x11) {
    iVar8 = (*(int (*)())camry_indirect((uint32_t)(param_3[1])))();
    if ((uVar4 < (*((uint16_t *)(stack_record_44 + 14)))) || (uVar2 = (*((uint16_t *)(stack_record_44 + 14))) + 1, uVar4 < (ushort)((*((uint16_t *)(stack_record_44 + 14))) + 1))) {
LAB_0006e638:
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
LAB_0006e602:
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
        if (iVar8 == 0x33) goto LAB_0006e602;
        if (iVar8 == 0x44) goto LAB_0006e638;
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
          goto LAB_0006e718;
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
    goto LAB_0006e718;
  }
  if (uVar6 == 0x22) {
    uVar9 = (*(int (*)())camry_indirect((uint32_t)(param_3[2])))();
    uVar10 = update_total_and_event11_counters_checked_71014(uVar9,((uint16_t *)((stack_record_44 + 6))),((uint16_t *)(stack_record_44)));
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
        goto LAB_0006e718;
      }
      if ((uint32_t)(param_3[0xb] )!=0x0u) {
        (*(int (*)())camry_indirect((uint32_t)(param_3[0xb])))();
      }
      pcVar11 = (uint32_t)((uint32_t)(param_3[0x10]));
    }
    if ((uint32_t)(pcVar11) != 0u) {
      (*(int (*)())camry_indirect((uint32_t)(pcVar11)))();
    }
    goto LAB_0006e718;
  }
  if (uVar6 != 0x1100) {
    if (uVar6 != 0x2200) {
      if ((uint32_t)(param_3[0x10] )!=0x0u) {
        (*(int (*)())camry_indirect((uint32_t)(param_3[0x10])))();
      }
      uVar10 = 0x44;
      goto LAB_0006e718;
    }
    iVar8 = (*(int (*)())camry_indirect((uint32_t)(pcVar11)))();
    if (iVar8 == 0x11) {
LAB_0006e272:
      (*((uint16_t *)(stack_record_44 + 10))) = 0;
      (*((uint16_t *)(stack_record_44 + 14))) = 0;
LAB_0006e278:
      uVar10 = 0x2200;
    }
    else {
      if (iVar8 != 0x22) {
        if ((iVar8 == 0x33) || (iVar8 == 0x44)) goto LAB_0006e272;
        goto LAB_0006e278;
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
          goto LAB_0006e718;
        }
      }
      if ((uint32_t)(pcVar11) != 0u) {
        (*(int (*)())camry_indirect((uint32_t)(pcVar11)))();
      }
    }
    goto LAB_0006e718;
  }
  iVar8 = (*(int (*)())camry_indirect((uint32_t)(pcVar11)))(camry_host_addr(param_1), camry_host_addr(param_2), camry_host_addr(param_3));
  if ((uVar3 < (*((uint16_t *)(stack_record_44 + 8)))) || (uVar1 = (*((uint16_t *)(stack_record_44 + 8))) + 1, uVar3 < (ushort)((*((uint16_t *)(stack_record_44 + 8))) + 1))) {
LAB_0006e3bc:
    (*((uint16_t *)(stack_record_44 + 8))) = 0;
    (*((uint16_t *)(stack_record_44 + 6))) = 0;
    uVar10 = 0;
LAB_0006e3c4:
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
      goto LAB_0006e3c4;
    }
    if (iVar8 == 0x22) {
      (*((uint16_t *)(stack_record_44 + 6))) = 0;
      (*((uint16_t *)(stack_record_44 + 8))) = 0;
      if ((uVar4 < (*((uint16_t *)(stack_record_44 + 14)))) || (uVar2 = (*((uint16_t *)(stack_record_44 + 14))) + 1, uVar4 < (ushort)((*((uint16_t *)(stack_record_44 + 14))) + 1))) {
        uVar10 = 0;
        goto LAB_0006e3c4;
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
      else if (iVar8 == 0x44) goto LAB_0006e3bc;
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
        goto LAB_0006e718;
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
LAB_0006e718:
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

undefined4 dispatch_windowed_thresholds_with_consecutive_failure_recovery_6e74c(uint *param_1,ushort *param_2,undefined4 *param_3)

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
  (*((uint16_t *)(stack_record_44 + 18))) = (ushort)param_1[4];
  (*((uint16_t *)(stack_record_44 + 12))) = (ushort)param_1[3];
  (*((uint16_t *)(stack_record_44 + 10))) = (ushort)param_1[2];
  (*((uint16_t *)(stack_record_44 + 16))) = (*((undefined2 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 0xe))));
  (*((uint16_t *)(stack_record_44 + 20))) = (*((undefined2 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 0x12))));
  uVar2 = *param_2;
  uVar3 = param_2[1];
  uVar5 = param_2[2];
  (*((uint16_t *)(stack_record_44 + 0))) = param_2[4];
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
    if ((uVar5 < (*((uint16_t *)(stack_record_44 + 10)))) && (uVar6 = 0x44, (*((uint16_t *)(stack_record_44 + 18))) <= (*((uint16_t *)(stack_record_44 + 2))))) {
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
LAB_0006eb40:
      (*((uint16_t *)(stack_record_44 + 14))) = 0;
      (*((uint16_t *)(stack_record_44 + 10))) = 0;
    }
    else if (iVar8 == 0x22) {
      (*((uint16_t *)(stack_record_44 + 6))) = 0;
      (*((uint16_t *)(stack_record_44 + 8))) = 0;
      if ((uVar4 < (*((uint16_t *)(stack_record_44 + 14)))) || (uVar2 = (*((uint16_t *)(stack_record_44 + 14))) + 1, uVar4 < (ushort)((*((uint16_t *)(stack_record_44 + 14))) + 1))) {
        uVar10 = 0;
        goto LAB_0006eb40;
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
        goto LAB_0006eb40;
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
          goto LAB_0006ed2a;
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
    goto LAB_0006ed2a;
  }
  if (uVar6 == 0x11) {
    iVar8 = (*(int (*)())camry_indirect((uint32_t)(param_3[1])))();
    if ((uVar4 < (*((uint16_t *)(stack_record_44 + 14)))) || (uVar2 = (*((uint16_t *)(stack_record_44 + 14))) + 1, uVar4 < (ushort)((*((uint16_t *)(stack_record_44 + 14))) + 1))) {
LAB_0006ec4a:
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
LAB_0006ec14:
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
        if (iVar8 == 0x33) goto LAB_0006ec14;
        if (iVar8 == 0x44) goto LAB_0006ec4a;
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
          goto LAB_0006ed2a;
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
    goto LAB_0006ed2a;
  }
  if (uVar6 == 0x22) {
    uVar9 = (*(int (*)())camry_indirect((uint32_t)(param_3[2])))();
    uVar10 = update_event_counters_reset_event22_on_event11_71232(uVar9,((uint16_t *)((stack_record_44 + 6))),((uint16_t *)(stack_record_44)));
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
        goto LAB_0006ed2a;
      }
      if ((uint32_t)(param_3[0xb] )!=0x0u) {
        (*(int (*)())camry_indirect((uint32_t)(param_3[0xb])))();
      }
      pcVar11 = (uint32_t)((uint32_t)(param_3[0x10]));
    }
    if ((uint32_t)(pcVar11) != 0u) {
      (*(int (*)())camry_indirect((uint32_t)(pcVar11)))();
    }
    goto LAB_0006ed2a;
  }
  if (uVar6 != 0x1100) {
    if (uVar6 != 0x2200) {
      if ((uint32_t)(param_3[0x10] )!=0x0u) {
        (*(int (*)())camry_indirect((uint32_t)(param_3[0x10])))();
      }
      uVar10 = 0x44;
      goto LAB_0006ed2a;
    }
    iVar8 = (*(int (*)())camry_indirect((uint32_t)(pcVar11)))();
    if (iVar8 == 0x11) {
LAB_0006e884:
      (*((uint16_t *)(stack_record_44 + 10))) = 0;
      (*((uint16_t *)(stack_record_44 + 14))) = 0;
LAB_0006e88a:
      uVar10 = 0x2200;
    }
    else {
      if (iVar8 != 0x22) {
        if ((iVar8 == 0x33) || (iVar8 == 0x44)) goto LAB_0006e884;
        goto LAB_0006e88a;
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
          goto LAB_0006ed2a;
        }
      }
      if ((uint32_t)(pcVar11) != 0u) {
        (*(int (*)())camry_indirect((uint32_t)(pcVar11)))();
      }
    }
    goto LAB_0006ed2a;
  }
  iVar8 = (*(int (*)())camry_indirect((uint32_t)(pcVar11)))(camry_host_addr(param_1), camry_host_addr(param_2), camry_host_addr(param_3));
  if ((uVar3 < (*((uint16_t *)(stack_record_44 + 8)))) || (uVar1 = (*((uint16_t *)(stack_record_44 + 8))) + 1, uVar3 < (ushort)((*((uint16_t *)(stack_record_44 + 8))) + 1))) {
LAB_0006e9ce:
    (*((uint16_t *)(stack_record_44 + 8))) = 0;
    (*((uint16_t *)(stack_record_44 + 6))) = 0;
    uVar10 = 0;
LAB_0006e9d6:
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
      goto LAB_0006e9d6;
    }
    if (iVar8 == 0x22) {
      (*((uint16_t *)(stack_record_44 + 6))) = 0;
      (*((uint16_t *)(stack_record_44 + 8))) = 0;
      if ((uVar4 < (*((uint16_t *)(stack_record_44 + 14)))) || (uVar2 = (*((uint16_t *)(stack_record_44 + 14))) + 1, uVar4 < (ushort)((*((uint16_t *)(stack_record_44 + 14))) + 1))) {
        uVar10 = 0;
        goto LAB_0006e9d6;
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
      else if (iVar8 == 0x44) goto LAB_0006e9ce;
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
        goto LAB_0006ed2a;
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
LAB_0006ed2a:
  *param_1 = uVar10;
  *(ushort *)(param_1 + 1) = (*((uint16_t *)(stack_record_44 + 6)));
  (*((ushort *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 6)))) = (*((uint16_t *)(stack_record_44 + 8)));
  *(ushort *)(param_1 + 2) = (*((uint16_t *)(stack_record_44 + 10)));
  (*((ushort *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 10)))) = (*((uint16_t *)(stack_record_44 + 14)));
  *(ushort *)(param_1 + 3) = (*((uint16_t *)(stack_record_44 + 12)));
  (*((undefined2 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 0xe)))) = (*((uint16_t *)(stack_record_44 + 16)));
  *(ushort *)(param_1 + 4) = (*((uint16_t *)(stack_record_44 + 18)));
  (*((undefined2 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 0x12)))) = (*((uint16_t *)(stack_record_44 + 20)));
  return 0x11;
}

short dispatch_threshold_counters_with_accumulated_recovery_6ed64(uint *param_1,ushort *param_2,undefined4 *param_3)

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
  (*((uint16_t *)(stack_record_3c + 20))) = (*((undefined2 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 0xe))));
  uVar1 = *param_2;
  uVar2 = param_2[1];
  (*((uint16_t *)(stack_record_3c + 0))) = param_2[2];
  (*((uint16_t *)(stack_record_3c + 2))) = param_2[3];
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
  else if ((uVar2 < (*((uint16_t *)(stack_record_3c + 10)))) && (sVar3 = 0x44, (*((uint16_t *)(stack_record_3c + 18))) <= (*((uint16_t *)(stack_record_3c + 2))))) {
    sVar3 = 0x22;
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
          goto LAB_0006f300;
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
    goto LAB_0006f300;
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
          goto LAB_0006f300;
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
    goto LAB_0006f300;
  }
  if (sVar3 == 0x22) {
    uVar6 = (*(int (*)())camry_indirect((uint32_t)(param_3[2])))();
    uVar8 = update_event11_event22_counters_and_peak_71086(uVar6,((uint16_t *)((stack_record_3c + 6))),((uint16_t *)(stack_record_3c)));
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
        goto LAB_0006f300;
      }
      if ((uint32_t)(param_3[0xb] )!=0x0u) {
        (*(int (*)())camry_indirect((uint32_t)(param_3[0xb])))();
      }
      pcVar9 = (uint32_t)((uint32_t)(param_3[0x10]));
    }
    if ((uint32_t)(pcVar9) != 0u) {
      (*(int (*)())camry_indirect((uint32_t)(pcVar9)))();
    }
    goto LAB_0006f300;
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
          goto LAB_0006f300;
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
    goto LAB_0006f300;
  }
  if (sVar3 != 0x2200) {
    if ((uint32_t)(param_3[0x10] )!=0x0u) {
      (*(int (*)())camry_indirect((uint32_t)(param_3[0x10])))();
    }
    uVar8 = 0x44;
    goto LAB_0006f300;
  }
  iVar5 = (*(int (*)())camry_indirect((uint32_t)(pcVar9)))();
  if (iVar5 == 0x11) {
LAB_0006ee6c:
    (*((uint16_t *)(stack_record_3c + 10))) = 0;
LAB_0006ee70:
    uVar8 = 0x2200;
  }
  else {
    if (iVar5 != 0x22) {
      if ((iVar5 == 0x33) || (iVar5 == 0x44)) goto LAB_0006ee6c;
      goto LAB_0006ee70;
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
        goto LAB_0006f300;
      }
    }
    if ((uint32_t)(pcVar9) != 0u) {
      (*(int (*)())camry_indirect((uint32_t)(pcVar9)))(camry_host_addr(param_1), camry_host_addr(param_2), camry_host_addr(param_3));
    }
  }
LAB_0006f300:
  *param_1 = uVar8;
  *(ushort *)(param_1 + 1) = ((uint16_t *)((stack_record_3c + 6)))[0];
  (*((ushort *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 6)))) = (*((uint16_t *)(stack_record_3c + 10)));
  *(ushort *)(param_1 + 2) = (*((uint16_t *)(stack_record_3c + 12)));
  (*((undefined2 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 10)))) = (*((uint16_t *)(stack_record_3c + 16)));
  *(ushort *)(param_1 + 3) = (*((uint16_t *)(stack_record_3c + 18)));
  (*((undefined2 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 0xe)))) = (*((uint16_t *)(stack_record_3c + 20)));
  return 0x11;
}
