#include "common.h"

uint step_windowed_monitor
               (F33WindowedMonitorState *state,F33WindowedMonitorLimits *limits,
               F33TwoSidedMonitorCallbacks *callbacks)

{
  ushort uVar1;
  ushort uVar2;
  ushort uVar3;
  ushort uVar4;
  short sVar5;
  uint uVar6;
  uint uVar7;
  ushort uVar8;
  ushort uVar9;
  ushort uVar10;
  ushort uVar11;
  ushort uVar12;
  uint32_t pFVar13;
  
  uVar10 = state->passing_count;
  uVar9 = state->passing_window;
  uVar12 = state->failing_count;
  uVar11 = state->failing_window;
  uVar8 = state->failing_high_water;
  uVar1 = limits->passing_window_limit;
  uVar2 = limits->passing_limit;
  uVar3 = limits->failing_limit;
  uVar4 = limits->failing_window_limit;
  if (uVar12 == 0) {
    if (uVar2 < uVar10) {
      sVar5 = 0x2200;
    }
    else {
      sVar5 = 0;
      if (uVar10 != 0) {
        sVar5 = 0x1100;
      }
    }
  }
  else {
    sVar5 = 0x22;
    if (uVar12 <= uVar3) {
      sVar5 = 0x11;
    }
  }
  if (sVar5 == 0) {
    uVar7 = (*(int (*)())camry_indirect((uint32_t)(callbacks->classify_normal)))(camry_host_addr(state), camry_host_addr(limits), camry_host_addr(callbacks));
    if (uVar7 == 0x11) {
      if ((uVar1 < uVar9) || (uVar9 = uVar9 + 1, uVar1 < uVar9)) {
        uVar10 = 0;
        uVar9 = 0;
        uVar7 = 0;
      }
      else if ((uVar2 < uVar10) || (uVar10 = uVar10 + 1, uVar2 < uVar10)) {
        uVar7 = 0x2200;
      }
      else {
        uVar7 = 0x11001100;
      }
      uVar12 = 0;
      uVar11 = 0;
    }
    else if (uVar7 == 0x22) {
      uVar10 = 0;
      uVar9 = 0;
      if ((uVar4 < uVar11) || (uVar11 = uVar11 + 1, uVar4 < uVar11)) goto LAB_0006b648;
      if (uVar12 <= uVar3) {
        uVar12 = uVar12 + 1;
      }
      uVar1 = uVar12;
      if (uVar12 <= uVar8) {
        uVar1 = uVar8;
      }
      uVar8 = uVar1;
      uVar7 = 0x22;
      if (uVar12 <= uVar3) {
        uVar7 = 0x110011;
      }
    }
    else if ((uVar7 == 0x33) || (uVar7 == 0x44)) {
LAB_0006b648:
      uVar10 = 0;
      uVar9 = 0;
      uVar11 = 0;
      uVar7 = 0;
      uVar12 = uVar9;
    }
    else {
      uVar7 = 0;
    }
    uVar6 = uVar7 & 0xffff;
    if (uVar6 != 0) {
      if (uVar6 == 0x11) {
        if (callbacks->enter_failing !=0x0u) {
          (*(int (*)())camry_indirect((uint32_t)(callbacks->enter_failing)))();
        }
        pFVar13 = (uint32_t)((uint32_t)(callbacks->repeat_pending_failing));
      }
      else if (uVar6 == 0x22) {
        if (callbacks->enter_failing !=0x0u) {
          (*(int (*)())camry_indirect((uint32_t)(callbacks->enter_failing)))();
        }
        if (callbacks->confirm_failing !=0x0u) {
          (*(int (*)())camry_indirect((uint32_t)(callbacks->confirm_failing)))();
        }
        pFVar13 = (uint32_t)((uint32_t)(callbacks->repeat_confirmed_failing));
      }
      else if (uVar6 == 0x1100) {
        if (callbacks->enter_passing !=0x0u) {
          (*(int (*)())camry_indirect((uint32_t)(callbacks->enter_passing)))();
        }
        pFVar13 = (uint32_t)((uint32_t)(callbacks->repeat_pending_passing));
      }
      else {
        if (uVar6 != 0x2200) {
          uVar7 = 0;
          goto LAB_0006b7bc;
        }
        if (callbacks->enter_passing !=0x0u) {
          (*(int (*)())camry_indirect((uint32_t)(callbacks->enter_passing)))();
        }
        if (callbacks->confirm_passing !=0x0u) {
          (*(int (*)())camry_indirect((uint32_t)(callbacks->confirm_passing)))();
        }
        pFVar13 = (uint32_t)((uint32_t)(callbacks->repeat_confirmed_passing));
      }
      if ((uint32_t)(pFVar13) != 0u) {
        (*(int (*)())camry_indirect((uint32_t)(pFVar13)))();
      }
    }
    goto LAB_0006b7bc;
  }
  if (sVar5 == 0x11) {
    uVar7 = (*(int (*)())camry_indirect((uint32_t)(callbacks->classify_failing)))();
    if ((uVar4 < uVar11) || (uVar11 = uVar11 + 1, uVar4 < uVar11)) {
LAB_0006b744:
      uVar10 = 0;
      uVar9 = 0;
      uVar12 = 0;
      uVar11 = 0;
      uVar7 = 0;
    }
    else {
      if (uVar7 == 0x11) {
LAB_0006b73e:
        uVar10 = 0;
        uVar9 = uVar10;
      }
      else {
        if (uVar7 == 0x22) {
          uVar10 = 0;
          uVar9 = 0;
          if (uVar12 <= uVar3) {
            uVar12 = uVar12 + 1;
          }
          uVar1 = uVar12;
          if (uVar12 <= uVar8) {
            uVar1 = uVar8;
          }
          uVar8 = uVar1;
          uVar7 = 0x22;
          if (uVar12 <= uVar3) {
            uVar7 = 0x110011;
          }
          goto LAB_0006b74e;
        }
        if (uVar7 == 0x33) goto LAB_0006b73e;
        if (uVar7 == 0x44) goto LAB_0006b744;
      }
      uVar7 = 0x11;
    }
LAB_0006b74e:
    uVar6 = uVar7 & 0xffff;
    if (uVar6 == 0) {
      if (callbacks->leave_pending_failing !=0x0u) {
        (*(int (*)())camry_indirect((uint32_t)(callbacks->leave_pending_failing)))(camry_host_addr(state), camry_host_addr(limits), camry_host_addr(callbacks));
      }
    }
    else {
      if (uVar6 == 0x11) {
        pFVar13 = (uint32_t)((uint32_t)(callbacks->repeat_pending_failing));
      }
      else {
        if (uVar6 != 0x22) {
          if (callbacks->repeat_pending_failing !=0x0u) {
            (*(int (*)())camry_indirect((uint32_t)(callbacks->repeat_pending_failing)))();
          }
          uVar7 = 0x11;
          goto LAB_0006b7bc;
        }
        if (callbacks->confirm_failing !=0x0u) {
          (*(int (*)())camry_indirect((uint32_t)(callbacks->confirm_failing)))();
        }
        pFVar13 = (uint32_t)((uint32_t)(callbacks->repeat_confirmed_failing));
      }
      if ((uint32_t)(pFVar13) != 0u) {
        (*(int (*)())camry_indirect((uint32_t)(pFVar13)))();
      }
    }
    goto LAB_0006b7bc;
  }
  if (sVar5 == 0x1100) {
    uVar7 = (*(int (*)())camry_indirect((uint32_t)(callbacks->classify_normal)))();
    if ((uVar1 < uVar9) || (uVar9 = uVar9 + 1, uVar1 < uVar9)) {
LAB_0006b502:
      uVar10 = 0;
      uVar9 = 0;
      uVar11 = 0;
      uVar7 = 0;
      uVar12 = uVar9;
    }
    else if (uVar7 == 0x11) {
      if ((uVar2 < uVar10) || (uVar10 = uVar10 + 1, uVar2 < uVar10)) {
        uVar7 = 0x2200;
      }
      else {
        uVar7 = 0x11001100;
      }
      uVar12 = 0;
      uVar11 = 0;
    }
    else if (uVar7 == 0x22) {
      uVar10 = 0;
      uVar9 = 0;
      if ((uVar4 < uVar11) || (uVar11 = uVar11 + 1, uVar4 < uVar11)) goto LAB_0006b502;
      if (uVar12 <= uVar3) {
        uVar12 = uVar12 + 1;
      }
      uVar1 = uVar12;
      if (uVar12 <= uVar8) {
        uVar1 = uVar8;
      }
      uVar8 = uVar1;
      uVar7 = 0x22;
      if (uVar12 <= uVar3) {
        uVar7 = 0x110011;
      }
    }
    else {
      if (uVar7 == 0x33) {
        uVar12 = 0;
        uVar11 = uVar12;
      }
      else if (uVar7 == 0x44) goto LAB_0006b502;
      uVar7 = 0x1100;
    }
    uVar6 = uVar7 & 0xffff;
    if (uVar6 == 0) {
      if (callbacks->leave_pending_passing !=0x0u) {
        (*(int (*)())camry_indirect((uint32_t)(callbacks->leave_pending_passing)))();
      }
    }
    else {
      if (uVar6 == 0x11) {
        if (callbacks->leave_pending_passing !=0x0u) {
          (*(int (*)())camry_indirect((uint32_t)(callbacks->leave_pending_passing)))();
        }
        if (callbacks->enter_failing !=0x0u) {
          (*(int (*)())camry_indirect((uint32_t)(callbacks->enter_failing)))();
        }
        pFVar13 = (uint32_t)((uint32_t)(callbacks->repeat_pending_failing));
      }
      else if (uVar6 == 0x22) {
        if (callbacks->leave_pending_passing !=0x0u) {
          (*(int (*)())camry_indirect((uint32_t)(callbacks->leave_pending_passing)))();
        }
        if (callbacks->enter_failing !=0x0u) {
          (*(int (*)())camry_indirect((uint32_t)(callbacks->enter_failing)))();
        }
        if (callbacks->confirm_failing !=0x0u) {
          (*(int (*)())camry_indirect((uint32_t)(callbacks->confirm_failing)))(camry_host_addr(state), camry_host_addr(limits), camry_host_addr(callbacks));
        }
        pFVar13 = (uint32_t)((uint32_t)(callbacks->repeat_confirmed_failing));
      }
      else if (uVar6 == 0x1100) {
        pFVar13 = (uint32_t)((uint32_t)(callbacks->repeat_pending_passing));
      }
      else {
        if (uVar6 != 0x2200) {
          if (callbacks->repeat_pending_passing !=0x0u) {
            (*(int (*)())camry_indirect((uint32_t)(callbacks->repeat_pending_passing)))();
          }
          uVar7 = 0x1100;
          goto LAB_0006b7bc;
        }
        if (callbacks->confirm_passing !=0x0u) {
          (*(int (*)())camry_indirect((uint32_t)(callbacks->confirm_passing)))();
        }
        pFVar13 = (uint32_t)((uint32_t)(callbacks->repeat_confirmed_passing));
      }
      if ((uint32_t)(pFVar13) != 0u) {
        (*(int (*)())camry_indirect((uint32_t)(pFVar13)))();
      }
    }
    goto LAB_0006b7bc;
  }
  if (sVar5 != 0x2200) {
    if (callbacks->repeat_confirmed_failing !=0x0u) {
      (*(int (*)())camry_indirect((uint32_t)(callbacks->repeat_confirmed_failing)))();
    }
    uVar7 = 0x22;
    goto LAB_0006b7bc;
  }
  uVar7 = (*(int (*)())camry_indirect((uint32_t)(callbacks->classify_normal)))();
  if (uVar7 == 0x11) {
LAB_0006b3d6:
    uVar12 = 0;
    uVar11 = 0;
LAB_0006b3da:
    uVar7 = 0x2200;
  }
  else {
    if (uVar7 != 0x22) {
      if ((uVar7 == 0x33) || (uVar7 == 0x44)) goto LAB_0006b3d6;
      goto LAB_0006b3da;
    }
    uVar10 = 0;
    uVar9 = 0;
    if ((uVar4 < uVar11) || (uVar11 = uVar11 + 1, uVar4 < uVar11)) {
      uVar12 = 0;
      uVar11 = 0;
      uVar7 = 0;
    }
    else {
      if (uVar12 <= uVar3) {
        uVar12 = uVar12 + 1;
      }
      uVar1 = uVar12;
      if (uVar12 <= uVar8) {
        uVar1 = uVar8;
      }
      uVar8 = uVar1;
      uVar7 = 0x22;
      if (uVar12 <= uVar3) {
        uVar7 = 0x110011;
      }
    }
  }
  uVar6 = uVar7 & 0xffff;
  if (uVar6 == 0) {
    if (callbacks->leave_confirmed_passing !=0x0u) {
      (*(int (*)())camry_indirect((uint32_t)(callbacks->leave_confirmed_passing)))();
    }
  }
  else {
    if (uVar6 == 0x11) {
      if (callbacks->leave_confirmed_passing !=0x0u) {
        (*(int (*)())camry_indirect((uint32_t)(callbacks->leave_confirmed_passing)))();
      }
      if (callbacks->enter_failing !=0x0u) {
        (*(int (*)())camry_indirect((uint32_t)(callbacks->enter_failing)))(camry_host_addr(state), camry_host_addr(limits), camry_host_addr(callbacks));
      }
      pFVar13 = (uint32_t)((uint32_t)(callbacks->repeat_pending_failing));
    }
    else if (uVar6 == 0x22) {
      if (callbacks->leave_confirmed_passing !=0x0u) {
        (*(int (*)())camry_indirect((uint32_t)(callbacks->leave_confirmed_passing)))();
      }
      if (callbacks->enter_failing !=0x0u) {
        (*(int (*)())camry_indirect((uint32_t)(callbacks->enter_failing)))();
      }
      if (callbacks->confirm_failing !=0x0u) {
        (*(int (*)())camry_indirect((uint32_t)(callbacks->confirm_failing)))();
      }
      pFVar13 = (uint32_t)((uint32_t)(callbacks->repeat_confirmed_failing));
    }
    else {
      pFVar13 = (uint32_t)((uint32_t)(callbacks->repeat_confirmed_passing));
      if (uVar6 != 0x2200) {
        if ((uint32_t)(pFVar13) != 0u) {
          (*(int (*)())camry_indirect((uint32_t)(pFVar13)))();
        }
        uVar7 = 0x2200;
        goto LAB_0006b7bc;
      }
    }
    if ((uint32_t)(pFVar13) != 0u) {
      (*(int (*)())camry_indirect((uint32_t)(pFVar13)))(camry_host_addr(state), camry_host_addr(limits), camry_host_addr(callbacks));
    }
  }
LAB_0006b7bc:
  state->packed_status = uVar7;
  state->passing_count = uVar10;
  state->passing_window = uVar9;
  state->failing_count = uVar12;
  state->failing_window = uVar11;
  state->failing_high_water = uVar8;
  return 0x11;
}

void clear_byte_state_and_three_halfword_counters_6b7d2(undefined1 *param_1)

{
  *param_1 = 0;
  *(undefined2 *)(param_1 + 2) = 0;
  *(undefined2 *)(param_1 + 4) = 0;
  *(undefined2 *)(param_1 + 6) = 0;
  return;
}

undefined1 advance_four_phase_threshold_callback_state_6b7f0(char *param_1,ushort *param_2,undefined4 *param_3)

{
  int iVar1;
  uint uVar2;
  uint uVar3;
  uint uVar4;
  uint uVar5;
  ushort uVar6;
  uint uVar7;
  char cVar8;
  uint32_t pcVar9;
  ushort uVar10;
  uint uVar11;
  ushort uVar12;
  uint uVar13;
  undefined1 uStack_31;
  
  cVar8 = *param_1;
  uVar10 = *(ushort *)(param_1 + 6);
  uVar11 = (uint)uVar10;
  uVar12 = *(ushort *)(param_1 + 2);
  uVar13 = (uint)uVar12;
  uVar6 = *(ushort *)(param_1 + 4);
  uVar7 = (uint)uVar6;
  uStack_31 = 0x11;
  uVar5 = (uint)param_2[2];
  uVar3 = (uint)param_2[3];
  uVar4 = (uint)*param_2;
  uVar2 = (uint)param_2[1];
  iVar1 = (*(int (*)())camry_indirect((uint32_t)(*param_3)))(camry_host_addr(param_1), camry_host_addr(param_2), camry_host_addr(param_3));
  if (cVar8 == '\0') {
    if (iVar1 != 0x22) {
      if ((iVar1 == 0x11) || (iVar1 == 0x44)) {
        uVar12 = 0;
      }
      goto LAB_0006b978;
    }
    if ((int)(uVar13 - uVar4) < 0 || uVar13 == uVar4) {
      uVar13 = uVar13 + 1;
    }
    uVar2 = uVar13;
    if (-1 < (int)(uVar7 - uVar13)) {
      uVar2 = uVar7;
    }
    uVar6 = (ushort)uVar2;
    cVar8 = '\x11';
    if ((uint32_t)(param_3[1] )!=0x0u) {
      (*(int (*)())camry_indirect((uint32_t)(param_3[1])))();
    }
LAB_0006b8cc:
    uVar12 = (ushort)uVar13;
    uVar10 = (ushort)uVar11;
    pcVar9 = (uint32_t)((uint32_t)(param_3[7]));
  }
  else {
    if (cVar8 == '\x11') {
      if (iVar1 == 0x11) {
        if ((-1 < (int)(uVar11 - uVar5) && uVar11 != uVar5) ||
           (uVar11 = uVar11 + 1, -1 < (int)(uVar11 - uVar5) && uVar11 != uVar5)) {
          pcVar9 = (uint32_t)((uint32_t)(param_3[2]));
          uVar10 = 0;
          uVar12 = 0;
          cVar8 = '\0';
          goto joined_r0x0006b8d2;
        }
      }
      else if (iVar1 == 0x22) {
        uVar11 = 0;
        if ((int)(uVar13 - uVar4) < 0 || uVar13 == uVar4) {
          uVar13 = uVar13 + 1;
        }
        uVar2 = uVar13;
        if (-1 < (int)(uVar7 - uVar13)) {
          uVar2 = uVar7;
        }
        uVar6 = (ushort)uVar2;
        if (-1 < (int)(uVar13 - uVar4) && uVar13 != uVar4) {
          if ((uint32_t)(param_3[3] )!=0x0u) {
            (*(int (*)())camry_indirect((uint32_t)(param_3[3])))();
          }
          goto LAB_0006b92c;
        }
      }
      else if (iVar1 == 0x44) {
        uVar11 = 0;
        uVar13 = 0;
      }
      goto LAB_0006b8cc;
    }
    if (cVar8 == '\"') {
      if (iVar1 == 0x11) {
        if ((-1 < (int)(uVar11 - uVar5) && uVar11 != uVar5) ||
           (uVar11 = uVar11 + 1, -1 < (int)(uVar11 - uVar5) && uVar11 != uVar5)) {
          pcVar9 = (uint32_t)((uint32_t)(param_3[4]));
          uVar10 = 0;
          uVar12 = 0;
          cVar8 = '\0';
          goto joined_r0x0006b8d2;
        }
      }
      else if (iVar1 == 0x22) {
        uVar11 = 0;
        if ((int)(uVar13 - uVar2) < 0 || uVar13 == uVar2) {
          uVar13 = uVar13 + 1;
        }
        uVar3 = uVar13;
        if (-1 < (int)(uVar7 - uVar13)) {
          uVar3 = uVar7;
        }
        uVar6 = (ushort)uVar3;
        if (-1 < (int)(uVar13 - uVar2) && uVar13 != uVar2) {
          cVar8 = 'D';
          if ((uint32_t)(param_3[5] )!=0x0u) {
            (*(int (*)())camry_indirect((uint32_t)(param_3[5])))();
          }
          goto LAB_0006b96c;
        }
      }
      else if (iVar1 == 0x44) {
        uVar11 = 0;
        uVar13 = 0;
      }
LAB_0006b92c:
      uVar12 = (ushort)uVar13;
      cVar8 = '\"';
      uVar10 = (ushort)uVar11;
      pcVar9 = (uint32_t)((uint32_t)(param_3[8]));
    }
    else {
      if (cVar8 != 'D') {
        uStack_31 = 0x33;
        goto LAB_0006b978;
      }
      if (iVar1 == 0x11) {
        if ((-1 < (int)(uVar11 - uVar3) && uVar11 != uVar3) ||
           (uVar11 = uVar11 + 1, -1 < (int)(uVar11 - uVar3) && uVar11 != uVar3)) {
          pcVar9 = (uint32_t)((uint32_t)(param_3[6]));
          uVar10 = 0;
          uVar12 = 0;
          cVar8 = '\0';
          goto joined_r0x0006b8d2;
        }
      }
      else if (iVar1 == 0x22) {
        uVar11 = 0;
      }
      else if (iVar1 == 0x44) {
        uVar11 = 0;
        uVar13 = 0;
      }
LAB_0006b96c:
      uVar12 = (ushort)uVar13;
      uVar10 = (ushort)uVar11;
      pcVar9 = (uint32_t)((uint32_t)(param_3[9]));
    }
  }
joined_r0x0006b8d2:
  if ((uint32_t)(pcVar9) != 0u) {
    (*(int (*)())camry_indirect((uint32_t)(pcVar9)))();
  }
LAB_0006b978:
  *(ushort *)(param_1 + 4) = uVar6;
  *(ushort *)(param_1 + 2) = uVar12;
  *(ushort *)(param_1 + 6) = uVar10;
  *param_1 = cVar8;
  return uStack_31;
}

void clear_word_state_and_five_halfword_counters_6b98a(undefined4 *param_1)

{
  *param_1 = 0;
  *(undefined2 *)(param_1 + 1) = 0;
  (*((undefined2 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 6)))) = 0;
  *(undefined2 *)(param_1 + 2) = 0;
  (*((undefined2 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 10)))) = 0;
  *(undefined2 *)(param_1 + 3) = 0;
  return;
}

void retain_disabled_escalating_monitor(F33EscalatingMonitorState *state,ushort *calibration)

{
  uint uVar1;
  
  if ((uintptr_t)(((calibration[7])))<(uintptr_t)(((state->elapsed_count)))) {
    uVar1 = 0x44;
  }
  else if ((state->elapsed_count == 0) && ((uintptr_t)(((state->failing_count)))<=(uintptr_t)(((calibration[5]))))) {
    if ((state->failing_count == 0) && ((uintptr_t)(((calibration[2])))<(uintptr_t)(((state->passing_count))))) {
      uVar1 = 0x2200;
    }
    else {
      state->passing_count = 0;
      uVar1 = 0;
    }
    state->failing_count = 0;
    state->recovery_count = 0;
    state->elapsed_count = 0;
  }
  else {
    uVar1 = 0x22;
  }
  state->packed_status = uVar1;
  return;
}

uint step_escalating_monitor
               (F33EscalatingMonitorState *state,ushort *calibration,uint *callbacks)

{
  uint8_t stack_record_3c[60];
  int iVar1;
  ushort uVar2;
  ushort uVar3;
  int iVar4;
  undefined4 uVar5;
  uint uVar6;
  uint uVar7;
  uint uVar8;
  uint uVar9;
  uint32_t pcVar10;
  
  (*((uint16_t *)(stack_record_3c + 12))) = state->failing_high_water;
  ((uint16_t *)((stack_record_3c + 6)))[0] = state->passing_count;
  (*((uint16_t *)(stack_record_3c + 10))) = state->failing_count;
  (*((uint16_t *)(stack_record_3c + 22))) = state->elapsed_count;
  (*((uint16_t *)(stack_record_3c + 16))) = state->recovery_count;
  (*((uint16_t *)(stack_record_3c + 0))) = calibration[6];
  uVar7 = (uint)*calibration;
  uVar2 = calibration[1];
  uVar6 = (uint)calibration[2];
  (*((uint16_t *)(stack_record_3c + 2))) = calibration[7];
  uVar9 = (uint)calibration[3];
  uVar3 = calibration[4];
  uVar8 = (uint)calibration[5];
  if ((*((uint16_t *)(stack_record_3c + 10))) == 0) {
    if (uVar6 < ((uint16_t *)((stack_record_3c + 6)))[0]) {
      iVar4 = 0x2200;
    }
    else {
      iVar4 = 0;
      if (((uint16_t *)((stack_record_3c + 6)))[0] != 0) {
        iVar4 = 0x1100;
      }
    }
  }
  else if (uVar8 < (*((uint16_t *)(stack_record_3c + 10)))) {
    iVar4 = 0x44;
    if ((*((uint16_t *)(stack_record_3c + 22))) <= (*((uint16_t *)(stack_record_3c + 2)))) {
      iVar4 = 0x22;
    }
  }
  else {
    iVar4 = 0x11;
  }
  if (iVar4 == 0) {
    iVar4 = (*(int (*)())camry_indirect((uint32_t)(*callbacks)))(camry_host_addr(state), camry_host_addr(calibration), camry_host_addr(callbacks));
    if (iVar4 == 0x11) {
      iVar1 = 0xffff - uVar7;
      iVar4 = (uint)((uint16_t *)((stack_record_3c + 6)))[0] - iVar1;
      if (iVar4 < 0 == (iVar1 < 0 && iVar1 < 0 == iVar4 < 0)) {
        uVar8 = 0xffff;
      }
      else {
        uVar8 = ((uint16_t *)((stack_record_3c + 6)))[0] + uVar7 & 0xffff;
      }
      ((uint16_t *)((stack_record_3c + 6)))[0] = (ushort)uVar8;
      uVar7 = 0x2200;
      if (uVar8 <= uVar6) {
        uVar7 = 0x11001100;
      }
      (*((uint16_t *)(stack_record_3c + 10))) = 0;
    }
    else if (iVar4 == 0x22) {
      ((uint16_t *)((stack_record_3c + 6)))[0] = 0;
      iVar1 = 0xffff - uVar9;
      iVar4 = (uint)(*((uint16_t *)(stack_record_3c + 10))) - iVar1;
      if (iVar4 < 0 == (iVar1 < 0 && iVar1 < 0 == iVar4 < 0)) {
        uVar6 = 0xffff;
      }
      else {
        uVar6 = (*((uint16_t *)(stack_record_3c + 10))) + uVar9 & 0xffff;
      }
      (*((uint16_t *)(stack_record_3c + 10))) = (ushort)uVar6;
      if ((*((uint16_t *)(stack_record_3c + 12))) < uVar6) {
        (*((uint16_t *)(stack_record_3c + 12))) = (*((uint16_t *)(stack_record_3c + 10)));
      }
      uVar7 = 0x22;
      if (uVar6 <= uVar8) {
        uVar7 = 0x110011;
      }
    }
    else if ((iVar4 == 0x33) || (iVar4 == 0x44)) {
      (*((uint16_t *)(stack_record_3c + 10))) = 0;
      ((uint16_t *)((stack_record_3c + 6)))[0] = 0;
      uVar7 = 0;
    }
    else {
      uVar7 = 0;
    }
    uVar6 = uVar7 & 0xffff;
    if (uVar6 != 0) {
      if (uVar6 == 0x11) {
        if ((uint32_t)(callbacks[7] )!=0x0u) {
          (*(int (*)())camry_indirect((uint32_t)(callbacks[7])))();
        }
        pcVar10 = (uint32_t)((uint32_t)(callbacks[0xe]));
      }
      else if (uVar6 == 0x22) {
        if ((uint32_t)(callbacks[7] )!=0x0u) {
          (*(int (*)())camry_indirect((uint32_t)(callbacks[7])))();
        }
        if ((uint32_t)(callbacks[9] )!=0x0u) {
          (*(int (*)())camry_indirect((uint32_t)(callbacks[9])))();
        }
        pcVar10 = (uint32_t)((uint32_t)(callbacks[0xf]));
      }
      else if (uVar6 == 0x1100) {
        if ((uint32_t)(callbacks[3] )!=0x0u) {
          (*(int (*)())camry_indirect((uint32_t)(callbacks[3])))();
        }
        pcVar10 = (uint32_t)((uint32_t)(callbacks[0xc]));
      }
      else {
        if (uVar6 != 0x2200) {
          uVar7 = 0;
          goto LAB_0006c32e;
        }
        if ((uint32_t)(callbacks[3] )!=0x0u) {
          (*(int (*)())camry_indirect((uint32_t)(callbacks[3])))();
        }
        if ((uint32_t)(callbacks[5] )!=0x0u) {
          (*(int (*)())camry_indirect((uint32_t)(callbacks[5])))();
        }
        pcVar10 = (uint32_t)((uint32_t)(callbacks[0xd]));
      }
      if ((uint32_t)(pcVar10) != 0u) {
        (*(int (*)())camry_indirect((uint32_t)(pcVar10)))();
      }
    }
    goto LAB_0006c32e;
  }
  if (iVar4 == 0x11) {
    iVar4 = (*(int (*)())camry_indirect((uint32_t)(callbacks[1])))();
    if (iVar4 == 0x11) {
LAB_0006c238:
      ((uint16_t *)((stack_record_3c + 6)))[0] = 0;
      if (uVar3 < (*((uint16_t *)(stack_record_3c + 10)))) {
        (*((uint16_t *)(stack_record_3c + 10))) = (*((uint16_t *)(stack_record_3c + 10))) - uVar3;
LAB_0006c1fc:
        uVar7 = 0x11;
      }
      else {
LAB_0006c252:
        ((uint16_t *)((stack_record_3c + 6)))[0] = 0;
        uVar7 = 0;
        (*((uint16_t *)(stack_record_3c + 10))) = 0;
      }
    }
    else {
      if (iVar4 != 0x22) {
        if (iVar4 == 0x33) goto LAB_0006c238;
        if (iVar4 == 0x44) goto LAB_0006c252;
        goto LAB_0006c1fc;
      }
      ((uint16_t *)((stack_record_3c + 6)))[0] = 0;
      iVar1 = 0xffff - uVar9;
      iVar4 = (uint)(*((uint16_t *)(stack_record_3c + 10))) - iVar1;
      if (iVar4 < 0 == (iVar1 < 0 && iVar1 < 0 == iVar4 < 0)) {
        uVar6 = 0xffff;
      }
      else {
        uVar6 = (*((uint16_t *)(stack_record_3c + 10))) + uVar9 & 0xffff;
      }
      (*((uint16_t *)(stack_record_3c + 10))) = (ushort)uVar6;
      if ((*((uint16_t *)(stack_record_3c + 12))) < uVar6) {
        (*((uint16_t *)(stack_record_3c + 12))) = (*((uint16_t *)(stack_record_3c + 10)));
      }
      uVar7 = 0x22;
      if (uVar6 <= uVar8) {
        uVar7 = 0x110011;
      }
    }
    uVar6 = uVar7 & 0xffff;
    if (uVar6 == 0) {
      if ((uint32_t)(callbacks[8] )!=0x0u) {
        (*(int (*)())camry_indirect((uint32_t)(callbacks[8])))(camry_host_addr(state), camry_host_addr(calibration), camry_host_addr(callbacks));
      }
    }
    else {
      if (uVar6 == 0x11) {
        pcVar10 = (uint32_t)((uint32_t)(callbacks[0xe]));
      }
      else {
        if (uVar6 != 0x22) {
          if ((uint32_t)(callbacks[0xe] )!=0x0u) {
            (*(int (*)())camry_indirect((uint32_t)(callbacks[0xe])))();
          }
          uVar7 = 0x11;
          goto LAB_0006c32e;
        }
        if ((uint32_t)(callbacks[9] )!=0x0u) {
          (*(int (*)())camry_indirect((uint32_t)(callbacks[9])))();
        }
        pcVar10 = (uint32_t)((uint32_t)(callbacks[0xf]));
      }
      if ((uint32_t)(pcVar10) != 0u) {
        (*(int (*)())camry_indirect((uint32_t)(pcVar10)))();
      }
    }
    goto LAB_0006c32e;
  }
  if (iVar4 == 0x22) {
    uVar5 = (*(int (*)())camry_indirect((uint32_t)(callbacks[2])))();
    uVar7 = update_total_and_event11_counters_reset_on_event22_70fa4(uVar5,((uint16_t *)((stack_record_3c + 6))),((uint16_t *)(stack_record_3c)));
    uVar6 = uVar7 & 0xffff;
    if (uVar6 == 0) {
      pcVar10 = (uint32_t)((uint32_t)(callbacks[10]));
    }
    else if (uVar6 == 0x22) {
      pcVar10 = (uint32_t)((uint32_t)(callbacks[0xf]));
    }
    else {
      if (uVar6 != 0x44) {
        if ((uint32_t)(callbacks[0xf] )!=0x0u) {
          (*(int (*)())camry_indirect((uint32_t)(callbacks[0xf])))();
        }
        uVar7 = 0x22;
        goto LAB_0006c32e;
      }
      if ((uint32_t)(callbacks[0xb] )!=0x0u) {
        (*(int (*)())camry_indirect((uint32_t)(callbacks[0xb])))();
      }
      pcVar10 = (uint32_t)((uint32_t)(callbacks[0x10]));
    }
    if ((uint32_t)(pcVar10) != 0u) {
      (*(int (*)())camry_indirect((uint32_t)(pcVar10)))();
    }
    goto LAB_0006c32e;
  }
  if (iVar4 == 0x1100) {
    iVar4 = (*(int (*)())camry_indirect((uint32_t)(*callbacks)))();
    if (iVar4 == 0x11) {
      iVar1 = 0xffff - uVar7;
      iVar4 = (uint)((uint16_t *)((stack_record_3c + 6)))[0] - iVar1;
      if (iVar4 < 0 == (iVar1 < 0 && iVar1 < 0 == iVar4 < 0)) {
        uVar8 = 0xffff;
      }
      else {
        uVar8 = ((uint16_t *)((stack_record_3c + 6)))[0] + uVar7 & 0xffff;
      }
      ((uint16_t *)((stack_record_3c + 6)))[0] = (ushort)uVar8;
      uVar7 = 0x2200;
      if (uVar8 <= uVar6) {
        uVar7 = 0x11001100;
      }
LAB_0006bfe6:
      (*((uint16_t *)(stack_record_3c + 10))) = 0;
    }
    else if (iVar4 == 0x22) {
      ((uint16_t *)((stack_record_3c + 6)))[0] = 0;
      iVar1 = 0xffff - uVar9;
      iVar4 = (uint)(*((uint16_t *)(stack_record_3c + 10))) - iVar1;
      if (iVar4 < 0 == (iVar1 < 0 && iVar1 < 0 == iVar4 < 0)) {
        uVar6 = 0xffff;
      }
      else {
        uVar6 = (*((uint16_t *)(stack_record_3c + 10))) + uVar9 & 0xffff;
      }
      (*((uint16_t *)(stack_record_3c + 10))) = (ushort)uVar6;
      if ((*((uint16_t *)(stack_record_3c + 12))) < uVar6) {
        (*((uint16_t *)(stack_record_3c + 12))) = (*((uint16_t *)(stack_record_3c + 10)));
      }
      uVar7 = 0x22;
      if (uVar6 <= uVar8) {
        uVar7 = 0x110011;
      }
    }
    else {
      if (iVar4 == 0x33) {
        if (uVar2 < ((uint16_t *)((stack_record_3c + 6)))[0]) {
          ((uint16_t *)((stack_record_3c + 6)))[0] = ((uint16_t *)((stack_record_3c + 6)))[0] - uVar2;
          uVar7 = 0x1100;
        }
        else {
          ((uint16_t *)((stack_record_3c + 6)))[0] = 0;
          uVar7 = 0;
        }
        goto LAB_0006bfe6;
      }
      if (iVar4 == 0x44) {
        (*((uint16_t *)(stack_record_3c + 10))) = 0;
        ((uint16_t *)((stack_record_3c + 6)))[0] = 0;
        uVar7 = 0;
      }
      else {
        uVar7 = 0x1100;
      }
    }
    uVar6 = uVar7 & 0xffff;
    if (uVar6 == 0) {
      if ((uint32_t)(callbacks[4] )!=0x0u) {
        (*(int (*)())camry_indirect((uint32_t)(callbacks[4])))();
      }
    }
    else {
      if (uVar6 == 0x11) {
        if ((uint32_t)(callbacks[4] )!=0x0u) {
          (*(int (*)())camry_indirect((uint32_t)(callbacks[4])))(camry_host_addr(state), camry_host_addr(calibration), camry_host_addr(callbacks));
        }
        if ((uint32_t)(callbacks[7] )!=0x0u) {
          (*(int (*)())camry_indirect((uint32_t)(callbacks[7])))();
        }
        pcVar10 = (uint32_t)((uint32_t)(callbacks[0xe]));
      }
      else if (uVar6 == 0x22) {
        if ((uint32_t)(callbacks[4] )!=0x0u) {
          (*(int (*)())camry_indirect((uint32_t)(callbacks[4])))();
        }
        if ((uint32_t)(callbacks[7] )!=0x0u) {
          (*(int (*)())camry_indirect((uint32_t)(callbacks[7])))();
        }
        if ((uint32_t)(callbacks[9] )!=0x0u) {
          (*(int (*)())camry_indirect((uint32_t)(callbacks[9])))();
        }
        pcVar10 = (uint32_t)((uint32_t)(callbacks[0xf]));
      }
      else if (uVar6 == 0x1100) {
        pcVar10 = (uint32_t)((uint32_t)(callbacks[0xc]));
      }
      else {
        if (uVar6 != 0x2200) {
          if ((uint32_t)(callbacks[0xc] )!=0x0u) {
            (*(int (*)())camry_indirect((uint32_t)(callbacks[0xc])))();
          }
          uVar7 = 0x1100;
          goto LAB_0006c32e;
        }
        if ((uint32_t)(callbacks[5] )!=0x0u) {
          (*(int (*)())camry_indirect((uint32_t)(callbacks[5])))();
        }
        pcVar10 = (uint32_t)((uint32_t)(callbacks[0xd]));
      }
      if ((uint32_t)(pcVar10) != 0u) {
        (*(int (*)())camry_indirect((uint32_t)(pcVar10)))();
      }
    }
    goto LAB_0006c32e;
  }
  if (iVar4 != 0x2200) {
    if ((uint32_t)(callbacks[0x10] )!=0x0u) {
      (*(int (*)())camry_indirect((uint32_t)(callbacks[0x10])))(camry_host_addr(state), camry_host_addr(calibration), camry_host_addr(callbacks));
    }
    uVar7 = 0x44;
    goto LAB_0006c32e;
  }
  iVar4 = (*(int (*)())camry_indirect((uint32_t)(*callbacks)))();
  if (iVar4 == 0x11) {
LAB_0006bea2:
    (*((uint16_t *)(stack_record_3c + 10))) = 0;
LAB_0006bea6:
    uVar7 = 0x2200;
  }
  else {
    if (iVar4 != 0x22) {
      if ((iVar4 == 0x33) || (iVar4 == 0x44)) goto LAB_0006bea2;
      goto LAB_0006bea6;
    }
    ((uint16_t *)((stack_record_3c + 6)))[0] = 0;
    iVar1 = 0xffff - uVar9;
    iVar4 = (uint)(*((uint16_t *)(stack_record_3c + 10))) - iVar1;
    if (iVar4 < 0 == (iVar1 < 0 && iVar1 < 0 == iVar4 < 0)) {
      uVar6 = 0xffff;
    }
    else {
      uVar6 = (*((uint16_t *)(stack_record_3c + 10))) + uVar9 & 0xffff;
    }
    (*((uint16_t *)(stack_record_3c + 10))) = (ushort)uVar6;
    if ((*((uint16_t *)(stack_record_3c + 12))) < uVar6) {
      (*((uint16_t *)(stack_record_3c + 12))) = (*((uint16_t *)(stack_record_3c + 10)));
    }
    uVar7 = 0x22;
    if (uVar6 <= uVar8) {
      uVar7 = 0x110011;
    }
  }
  uVar6 = uVar7 & 0xffff;
  if (uVar6 == 0) {
    if ((uint32_t)(callbacks[6] )!=0x0u) {
      (*(int (*)())camry_indirect((uint32_t)(callbacks[6])))();
    }
  }
  else {
    if (uVar6 == 0x11) {
      if ((uint32_t)(callbacks[6] )!=0x0u) {
        (*(int (*)())camry_indirect((uint32_t)(callbacks[6])))();
      }
      if ((uint32_t)(callbacks[7] )!=0x0u) {
        (*(int (*)())camry_indirect((uint32_t)(callbacks[7])))();
      }
      pcVar10 = (uint32_t)((uint32_t)(callbacks[0xe]));
    }
    else if (uVar6 == 0x22) {
      if ((uint32_t)(callbacks[6] )!=0x0u) {
        (*(int (*)())camry_indirect((uint32_t)(callbacks[6])))(camry_host_addr(state), camry_host_addr(calibration), camry_host_addr(callbacks));
      }
      if ((uint32_t)(callbacks[7] )!=0x0u) {
        (*(int (*)())camry_indirect((uint32_t)(callbacks[7])))();
      }
      if ((uint32_t)(callbacks[9] )!=0x0u) {
        (*(int (*)())camry_indirect((uint32_t)(callbacks[9])))();
      }
      pcVar10 = (uint32_t)((uint32_t)(callbacks[0xf]));
    }
    else {
      pcVar10 = (uint32_t)((uint32_t)(callbacks[0xd]));
      if (uVar6 != 0x2200) {
        if ((uint32_t)(pcVar10) != 0u) {
          (*(int (*)())camry_indirect((uint32_t)(pcVar10)))();
        }
        uVar7 = 0x2200;
        goto LAB_0006c32e;
      }
    }
    if ((uint32_t)(pcVar10) != 0u) {
      (*(int (*)())camry_indirect((uint32_t)(pcVar10)))(camry_host_addr(state), camry_host_addr(calibration), camry_host_addr(callbacks));
    }
  }
LAB_0006c32e:
  state->packed_status = uVar7;
  state->passing_count = ((uint16_t *)((stack_record_3c + 6)))[0];
  state->failing_count = (*((uint16_t *)(stack_record_3c + 10)));
  state->failing_high_water = (*((uint16_t *)(stack_record_3c + 12)));
  state->recovery_count = (*((uint16_t *)(stack_record_3c + 16)));
  state->elapsed_count = (*((uint16_t *)(stack_record_3c + 22)));
  return 0x11;
}
