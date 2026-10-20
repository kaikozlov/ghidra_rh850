#include "common.h"

void end_execution_profile_slot3(void)

{
  uint *puVar1;
  uint uVar2;
  uint32_t puVar3;
  uint32_t puVar4;
  uint saved_mask;
  uint uVar5;
  int iVar6;
  
  puVar3 = 0xfebeb800u;
  saved_mask = priority_mask_enter(0xffc0);
  uVar5 = end_execution_profile('\x03',2,0x75);
  uVar2 = uVar5 - (*((int *)camry_host_ptr((uint32_t)(puVar3 + -0x2a98))));
  puVar4 = ((uint32_t)(puVar3));
  priority_mask_restore(saved_mask);
  if ((byte)(*((volatile undefined *)camry_host_ptr((uint32_t)(0xfebeb800u + (uint32_t)(-0x2a5a) * 1u)))) < 9) {
    iVar6 = (byte)(*((volatile undefined *)camry_host_ptr((uint32_t)(0xfebeb800u + (uint32_t)(-0x2a5a) * 1u)))) + 1;
  }
  else {
    iVar6 = 0;
  }
  (*((volatile undefined *)camry_host_ptr((uint32_t)(0xfebeb800u + (uint32_t)(-0x2a5a) * 1u)))) = (char)iVar6;
  puVar1 = ((uint *)camry_host_ptr((uint32_t)(puVar3 + iVar6 * 4 + -0x2ba0)));
  if (execution_profile_peak_hold == 'Z') {
    if (uVar2 < *puVar1) {
      uVar2 = *puVar1;
    }
    *puVar1 = uVar2;
    if (uVar5 < puVar1[0x1b]) {
      uVar5 = puVar1[0x1b];
    }
  }
  else {
    *puVar1 = uVar2;
  }
  (*((uint *)camry_host_ptr((uint32_t)(puVar3 + iVar6 * 4 + -0x2b34)))) = uVar5;
  return;
}

void end_execution_profile_slot4(void)

{
  uint uVar1;
  uint32_t puVar2;
  uint saved_mask;
  uint uVar3;
  
  puVar2 = 0xfebeb800u;
  saved_mask = priority_mask_enter(0xffc0);
  uVar3 = end_execution_profile('\x04',0x40,0x9a);
  uVar1 = uVar3 - (*((int *)camry_host_ptr((uint32_t)(puVar2 + -0x2a94))));
  priority_mask_restore(saved_mask);
  if (execution_profile_peak_hold == 'Z') {
    if (uVar1 < (*((uint *)camry_host_ptr((uint32_t)(puVar2 + -0x2b78))))) {
      uVar1 = (*((uint *)camry_host_ptr((uint32_t)(puVar2 + -0x2b78))));
    }
    (*((uint *)camry_host_ptr((uint32_t)(puVar2 + -0x2b78)))) = uVar1;
    if (uVar3 < (*((uint *)camry_host_ptr((uint32_t)(puVar2 + -0x2b0c))))) {
      uVar3 = (*((uint *)camry_host_ptr((uint32_t)(puVar2 + -0x2b0c))));
    }
  }
  else {
    (*((uint *)camry_host_ptr((uint32_t)(puVar2 + -0x2b78)))) = uVar1;
  }
  (*((uint *)camry_host_ptr((uint32_t)(puVar2 + -0x2b0c)))) = uVar3;
  return;
}

void end_execution_profile_slot5(void)

{
  int iVar1;
  uint uVar2;
  uint32_t puVar3;
  uint32_t puVar4;
  uint uVar5;
  uint uVar6;
  
  puVar3 = 0xfebeb800u;
  uVar5 = priority_mask_enter(0xffc0);
  uVar6 = end_execution_profile('\x05',0x44,0x76);
  uVar2 = uVar6 - (*((int *)camry_host_ptr((uint32_t)(puVar3 + -0x2a90))));
  puVar4 = ((uint32_t)(puVar3));
  priority_mask_restore(uVar5);
  uVar5 = (byte)(*((volatile undefined *)camry_host_ptr((uint32_t)(0xfebeb800u + (uint32_t)(-0x2a59) * 1u)))) + 1 & 0xf;
  (*((volatile undefined *)camry_host_ptr((uint32_t)(0xfebeb800u + (uint32_t)(-0x2a59) * 1u)))) = (byte)uVar5;
  iVar1 = uVar5 * 4;
  if (execution_profile_peak_hold == 'Z') {
    if (uVar2 < (*((uint *)camry_host_ptr((uint32_t)(puVar3 + iVar1 + -0x2b74))))) {
      uVar2 = (*((uint *)camry_host_ptr((uint32_t)(puVar3 + iVar1 + -0x2b74))));
    }
    (*((uint *)camry_host_ptr((uint32_t)(puVar3 + iVar1 + -0x2b74)))) = uVar2;
    if (uVar6 < (*((uint *)camry_host_ptr((uint32_t)(puVar3 + iVar1 + -0x2b08))))) {
      uVar6 = (*((uint *)camry_host_ptr((uint32_t)(puVar3 + iVar1 + -0x2b08))));
    }
  }
  else {
    (*((uint *)camry_host_ptr((uint32_t)(puVar3 + iVar1 + -0x2b74)))) = uVar2;
  }
  (*((uint *)camry_host_ptr((uint32_t)(puVar3 + iVar1 + -0x2b08)))) = uVar6;
  return;
}

uint read_adjusted_profile_elapsed(uchar slot,int exit_adjust)

{
  uint uVar1;
  
  uVar1 = DAT_ffe51010;
  return (~uVar1 - exit_adjust) - execution_profiles.start[slot];
}

uint read_execution_profile_slot0(void)

{
  uint uVar1;
  
  uVar1 = read_adjusted_profile_elapsed('\0',-0x13);
  return uVar1;
}

uint read_execution_profile_slot2(void)

{
  uint32_t puVar1;
  uint saved_mask;
  uint uVar2;
  int iVar3;
  
  puVar1 = 0xfebeb800u;
  saved_mask = priority_mask_enter(0xffc0);
  uVar2 = read_adjusted_profile_elapsed('\x02',4);
  iVar3 = (*((int *)camry_host_ptr((uint32_t)(puVar1 + -0x2a9c))));
  priority_mask_restore(saved_mask);
  return uVar2 - iVar3;
}

uint read_execution_profile_slot3(void)

{
  uint32_t puVar1;
  uint saved_mask;
  uint uVar2;
  int iVar3;
  
  puVar1 = 0xfebeb800u;
  saved_mask = priority_mask_enter(0xffc0);
  uVar2 = read_adjusted_profile_elapsed('\x03',2);
  iVar3 = (*((int *)camry_host_ptr((uint32_t)(puVar1 + -0x2a98))));
  priority_mask_restore(saved_mask);
  return uVar2 - iVar3;
}

uint read_execution_profile_slot4(void)

{
  uint32_t puVar1;
  uint saved_mask;
  uint uVar2;
  int iVar3;
  
  puVar1 = 0xfebeb800u;
  saved_mask = priority_mask_enter(0xffc0);
  uVar2 = read_adjusted_profile_elapsed('\x04',0x40);
  iVar3 = (*((int *)camry_host_ptr((uint32_t)(puVar1 + -0x2a94))));
  priority_mask_restore(saved_mask);
  return uVar2 - iVar3;
}

uint read_execution_profile_slot5(void)

{
  uint32_t puVar1;
  uint saved_mask;
  uint uVar2;
  int iVar3;
  
  puVar1 = 0xfebeb800u;
  saved_mask = priority_mask_enter(0xffc0);
  uVar2 = read_adjusted_profile_elapsed('\x05',0x44);
  iVar3 = (*((int *)camry_host_ptr((uint32_t)(puVar1 + -0x2a90))));
  priority_mask_restore(saved_mask);
  return uVar2 - iVar3;
}

void reset_task_rate_window(F33TaskRateWindow *state)

{
  state->phase = '\0';
  state->count = '\0';
  state->maximum = '\0';
  state->minimum = 0xff;
  return;
}

void initialize_task_progress_supervision(void)

{
  undefined1 *puVar1;
  int iVar2;
  uint uVar3;
  uint32_t puVar4;
  puVar4 = 0xfebeb800u;
  reset_task_rate_window(task_rate_windows);
  reset_task_rate_window(((F33TaskRateWindow *)camry_host_ptr((uint32_t)(puVar4 + -0x2a4c))));
  reset_task_rate_window(((F33TaskRateWindow *)camry_host_ptr((uint32_t)(puVar4 + -0x2a48))));
  reset_task_rate_window(((F33TaskRateWindow *)camry_host_ptr((uint32_t)(puVar4 + -0x2a44))));
  uVar3 = 0;
  do {
    iVar2 = uVar3 * 8;
    uVar3 = uVar3 + 1;
    puVar1 = ((undefined *)camry_host_ptr((uint32_t)(puVar4 + iVar2 + -0x2a40)));
    *puVar1 = 0;
    *(undefined2 *)(puVar1 + 2) = 0;
    *(undefined2 *)(puVar1 + 4) = 0;
    *(undefined2 *)(puVar1 + 6) = 0xffff;
  } while (uVar3 < 4);
  return;
}

void record_supervised_task_dispatch(F33TaskRateWindow *state,F33TaskRatePolicy *policy)

{
  camry_write32((camry_sp - 4u) & ~3u, camry_gpr[27]);
  camry_write32((camry_sp - 8u) & ~3u, camry_gpr[28]);
  camry_write32((camry_sp - 12u) & ~3u, camry_gpr[29]);
  camry_write32((camry_sp - 16u) & ~3u, camry_gpr[31]);
  camry_sp -= 16u;
  camry_gpr[3] = camry_sp;

  uint saved_mask;
  byte bVar1;
  
  saved_mask = (camry_gpr[28] = camry_host_addr(state), camry_gpr[27] = camry_host_addr(policy), camry_gpr[6] = 0xffc0u, camry_gpr[31] = 0x652bau, priority_mask_enter)(0xffc0);
  bVar1 = state->count;
  if (bVar1 != 0xff) {
    bVar1 = bVar1 + 1;
  }
  state->count = bVar1;
  (camry_gpr[29] = bVar1, camry_gpr[10] = saved_mask, camry_gpr[6] = saved_mask, camry_gpr[31] = 0x652d2u, priority_mask_restore)(saved_mask);
  if (policy->maximum < bVar1) {
                    /* WARNING: Subroutine does not return */
    (camry_gpr[31] = 0x652deu, enter_terminal_hardware_sequence)();
  }
  { if (!camry_halted) { camry_gpr[27] = camry_read32((camry_sp + 12u) & ~3u); camry_gpr[28] = camry_read32((camry_sp + 8u) & ~3u); camry_gpr[29] = camry_read32((camry_sp + 4u) & ~3u); camry_gpr[31] = camry_read32((camry_sp + 0u) & ~3u); camry_sp += 16u; camry_gpr[3] = camry_sp; } return; }
}

void record_ch0_dispatch(void)

{
  camry_write32((camry_sp - 4u) & ~3u, camry_gpr[31]);
  camry_sp -= 4u;
  camry_gpr[3] = camry_sp;

  (camry_gpr[6] = camry_gp - 0x2a50u, camry_r7 = camry_gpr[7] = 0x30dc0u, camry_gpr[31] = 0x652f4u, record_supervised_task_dispatch)(task_rate_windows,task_rate_policies);
  { if (!camry_halted) { camry_gpr[31] = camry_read32((camry_sp + 0u) & ~3u); camry_sp += 4u; camry_gpr[3] = camry_sp; } return; }
}

void record_auxiliary_dispatch(void)

{
  record_supervised_task_dispatch(((volatile F33TaskRateWindow *)camry_host_ptr((uint32_t)(0xfebe8db0u + (uint32_t)(1) * (uint32_t)sizeof(F33TaskRateWindow)))),task_rate_policies);
  return;
}

void record_ch1_dispatch(void)

{
  record_supervised_task_dispatch(((volatile F33TaskRateWindow *)camry_host_ptr((uint32_t)(0xfebe8db0u + (uint32_t)(2) * (uint32_t)sizeof(F33TaskRateWindow)))),((volatile F33TaskRatePolicy *)camry_host_ptr((uint32_t)(0x30dc0u + (uint32_t)(1) * (uint32_t)sizeof(F33TaskRatePolicy)))));
  return;
}

void check_dma_progress_windows(void)

{
  int iVar1;
  byte bVar2;
  undefined8 uVar3;
  uint uVar4;
  uint uVar5;
  undefined2 uVar6;
  uint uVar7;
  
  uVar3 = 0xfebeb800;
  uVar5 = 0;
  do {
    uVar4 = read_dma_progress_delta((*((volatile uint8_t *)camry_host_ptr((uint32_t)((uint32_t)(0x30dccu + (uint32_t)(uVar5) * (uint32_t)sizeof(F33DmaProgressPolicy)) + (uint32_t)(0) * (uint32_t)sizeof(F33DmaProgressPolicy) + (uint32_t)offsetof(F33DmaProgressPolicy, channel))))));
    iVar1 = uVar5 * 8 + (int)uVar3;
    uVar4 = uVar4 + (*((ushort *)camry_host_ptr((uint32_t)(iVar1 + -0x2a3e))));
    uVar7 = uVar4 & 0xffff;
    if (0xfffe < uVar4) {
      uVar7 = 0xffff;
    }
    uVar6 = (undefined2)uVar7;
    bVar2 = (*((byte *)camry_host_ptr((uint32_t)(iVar1 + -0x2a40)))) + 1;
    if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)((uint32_t)(0x30dccu + (uint32_t)(uVar5) * (uint32_t)sizeof(F33DmaProgressPolicy)) + (uint32_t)(0) * (uint32_t)sizeof(F33DmaProgressPolicy) + (uint32_t)offsetof(F33DmaProgressPolicy, window))))) <= bVar2) {
      if ((uVar7 < (*((volatile uint16_t *)camry_host_ptr((uint32_t)((uint32_t)(0x30dccu + (uint32_t)(uVar5) * (uint32_t)sizeof(F33DmaProgressPolicy)) + (uint32_t)(0) * (uint32_t)sizeof(F33DmaProgressPolicy) + (uint32_t)offsetof(F33DmaProgressPolicy, minimum)))))) ||
         ((*((volatile uint16_t *)camry_host_ptr((uint32_t)((uint32_t)(0x30dccu + (uint32_t)(uVar5) * (uint32_t)sizeof(F33DmaProgressPolicy)) + (uint32_t)(0) * (uint32_t)sizeof(F33DmaProgressPolicy) + (uint32_t)offsetof(F33DmaProgressPolicy, maximum))))) < uVar7)) {
                    /* WARNING: Subroutine does not return */
        enter_terminal_hardware_sequence();
      }
      if ((*((ushort *)camry_host_ptr((uint32_t)(iVar1 + -0x2a3c)))) < uVar7) {
        (*((undefined2 *)camry_host_ptr((uint32_t)(iVar1 + -0x2a3c)))) = uVar6;
      }
      if (uVar7 < (*((ushort *)camry_host_ptr((uint32_t)(iVar1 + -0x2a3a))))) {
        (*((undefined2 *)camry_host_ptr((uint32_t)(iVar1 + -0x2a3a)))) = uVar6;
      }
      bVar2 = 0;
      uVar6 = 0;
    }
    (*((undefined2 *)camry_host_ptr((uint32_t)(iVar1 + -0x2a3e)))) = uVar6;
    (*((byte *)camry_host_ptr((uint32_t)(iVar1 + -0x2a40)))) = bVar2;
    uVar5 = uVar5 + 1;
    if (3 < uVar5) {
      return;
    }
  } while( true );
}

void check_task_rate_window(F33TaskRateWindow *state,F33TaskRatePolicy *policy)

{
  byte bVar1;
  byte bVar2;
  byte bVar3;
  uint saved_mask;
  uint uVar4;
  
  bVar3 = state->phase;
  if (bVar3 != 0xff) {
    bVar3 = bVar3 + 1;
  }
  if (policy->window <= bVar3) {
    saved_mask = priority_mask_enter(0xffc0);
    bVar3 = state->count;
    uVar4 = (uint)bVar3;
    state->count = '\0';
    priority_mask_restore(saved_mask);
    if ((uVar4 < policy->minimum) || (policy->maximum < uVar4)) {
                    /* WARNING: Subroutine does not return */
      enter_terminal_hardware_sequence();
    }
    bVar1 = state->maximum;
    bVar2 = bVar3;
    if (-1 < (int)(bVar1 - uVar4) && bVar1 != uVar4) {
      bVar2 = bVar1;
    }
    state->maximum = bVar2;
    if ((int)(state->minimum - uVar4) < 0) {
      bVar3 = state->minimum;
    }
    state->minimum = bVar3;
    bVar3 = 0;
  }
  state->phase = bVar3;
  return;
}

void supervise_scheduled_progress(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  check_dma_progress_windows();
  check_task_rate_window(((F33TaskRateWindow *)camry_host_ptr((uint32_t)(puVar1 + -0x2a50))),task_rate_policies);
  check_task_rate_window(((F33TaskRateWindow *)camry_host_ptr((uint32_t)(puVar1 + -0x2a48))),((volatile F33TaskRatePolicy *)camry_host_ptr((uint32_t)(0x30dc0u + (uint32_t)(1) * (uint32_t)sizeof(F33TaskRatePolicy)))));
  check_task_rate_window(((F33TaskRateWindow *)camry_host_ptr((uint32_t)(puVar1 + -0x2a44))),((volatile F33TaskRatePolicy *)camry_host_ptr((uint32_t)(0x30dc0u + (uint32_t)(2) * (uint32_t)sizeof(F33TaskRatePolicy)))));
  return;
}

void record_foreground_dispatch(void)

{
  record_supervised_task_dispatch(((volatile F33TaskRateWindow *)camry_host_ptr((uint32_t)(0xfebe8db0u + (uint32_t)(3) * (uint32_t)sizeof(F33TaskRateWindow)))),((volatile F33TaskRatePolicy *)camry_host_ptr((uint32_t)(0x30dc0u + (uint32_t)(2) * (uint32_t)sizeof(F33TaskRatePolicy)))));
  return;
}

void initialize_fffee680_eight_register_groups_65458(void)

{
  Ramfffee680 = 0xfff000;
  Ramfffee688 = 4;
  Ramfffee684 = 0xfe000017;
  Ramfffee690 = 0xfff000;
  Ramfffee698 = 0x38;
  Ramfffee694 = 0xfe000013;
  Ramfffee6a0 = 0;
  Ramfffee6a8 = 0;
  Ramfffee6a4 = 0x16;
  Ramfffee6b0 = 0;
  Ramfffee6b8 = 0;
  Ramfffee6b4 = 0x16;
  Ramfffee6c0 = 0;
  Ramfffee6c8 = 0;
  Ramfffee6c4 = 0x16;
  Ramfffee6d0 = 0;
  Ramfffee6d8 = 0;
  Ramfffee6d4 = 0x16;
  Ramfffee6e0 = 0;
  Ramfffee6e8 = 0;
  Ramfffee6e4 = 0x16;
  Ramfffee6f0 = 0;
  Ramfffee6f8 = 0;
  Ramfffee6f4 = 0x16;
  return;
}

void initialize_fixed_register_access_patterns_654aa(void)

{
  Ramffddd114 = 0xffffffff;
  Ramffddd110 = 0x8625fe1b;
  Ramffddd11c = 0x24;
  Ramffddd118 = 0x8625fe17;
  Ramffddd124 = 0xffffffff;
  Ramffddd120 = 0x8625fe1b;
  Ramffddd12c = 0x24;
  Ramffddd128 = 0x8625fe17;
  Ramffddd204 = 0xffffffff;
  Ramffddd200 = 0x8625fe1b;
  Ramffddd20c = 0x14;
  Ramffddd208 = 0x8625fe17;
  Ramffddd214 = 0xffffffff;
  Ramffddd210 = 0x8625fe1b;
  Ramffddd21c = 0x14;
  Ramffddd218 = 0x8625fe17;
  Ramffddd224 = 0xffffffff;
  Ramffddd220 = 0x8625fe1b;
  Ramffddd22c = 0x14;
  Ramffddd228 = 0x8625fe17;
  Ramffddd234 = 0xffffffff;
  Ramffddd230 = 0x8625fe1b;
  Ramffddd23c = 0x14;
  Ramffddd238 = 0x8625fe17;
  Ramffddd244 = 0xffffffff;
  Ramffddd240 = 0x8625fe1b;
  Ramffddd24c = 0x14;
  Ramffddd248 = 0x8625fe17;
  Ramffddd254 = 0xffffffff;
  Ramffddd250 = 0x8625fe1b;
  Ramffddd25c = 0x14;
  Ramffddd258 = 0x8625fe17;
  Ramffc4c004 = 0xffffffff;
  Ramffc4c000 = 0x862dfe1b;
  Ramffc4c00c = 4;
  Ramffc4c008 = 0x860dfe17;
  Ramffc4c014 = 0xffffffff;
  Ramffc4c010 = 0x862dfe1b;
  Ramffc4c01c = 4;
  Ramffc4c018 = 0x860dfe17;
  Ramffc4c024 = 0xffffffff;
  Ramffc4c020 = 0x862dfe1b;
  Ramffc4c02c = 4;
  Ramffc4c028 = 0x860dfe17;
  Ramffc4c044 = 0xffffffff;
  Ramffc4c040 = 0x866dfe1b;
  Ramffc4c04c = 4;
  Ramffc4c048 = 0x864dfe17;
  Ramffc4c054 = 0xffffffff;
  Ramffc4c050 = 0x862dfe1b;
  Ramffc4c05c = 4;
  Ramffc4c058 = 0x860dfe17;
  Ramffc4c074 = 0xffffffff;
  Ramffc4c070 = 0x862dfe1b;
  Ramffc4c07c = 4;
  Ramffc4c078 = 0x860dfe17;
  Ramffc5a004 = 0xffffffff;
  Ramffc5a000 = 0x8625fe1b;
  Ramffc5a00c = 4;
  Ramffc5a008 = 0x8605fe17;
  Ramffc5a024 = 0xffffffff;
  Ramffc5a020 = 0x8625fe1b;
  Ramffc5a02c = 4;
  Ramffc5a028 = 0x8605fe17;
  Ramffc5a034 = 0xffffffff;
  Ramffc5a030 = 0x8625fe1b;
  Ramffc5a03c = 4;
  Ramffc5a038 = 0x8605fe17;
  Ramffc5a044 = 4;
  Ramffc5a040 = 0x8605fe1b;
  Ramffc5a04c = 4;
  Ramffc5a048 = 0x8605fe17;
  Ramffc5a054 = 0xffffffff;
  Ramffc5a050 = 0x8625fe1b;
  Ramffc5a05c = 4;
  Ramffc5a058 = 0x8605fe17;
  Ramffddd004 = 0xffffffff;
  Ramffddd000 = 0x8625fe1b;
  Ramffddd00c = 4;
  Ramffddd008 = 0x8605fe17;
  Ramffddd014 = 0xffffffff;
  Ramffddd010 = 0x8625fe1b;
  Ramffddd01c = 4;
  Ramffddd018 = 0x8605fe17;
  Ramffddd024 = 0xffffffff;
  Ramffddd020 = 0x8625fe1b;
  Ramffddd02c = 4;
  Ramffddd028 = 0x8605fe17;
  Ramffddd034 = 0xffffffff;
  Ramffddd030 = 0x8625fe1b;
  Ramffddd03c = 4;
  Ramffddd038 = 0x8605fe17;
  Ramffddd044 = 0xffffffff;
  Ramffddd040 = 0x8625fe1b;
  Ramffddd04c = 4;
  Ramffddd048 = 0x8605fe17;
  Ramffddd054 = 0xffffffff;
  Ramffddd050 = 0x8625fe1b;
  Ramffddd05c = 4;
  Ramffddd058 = 0x8605fe17;
  Ramffddd064 = 0xffffffff;
  Ramffddd060 = 0x8625fe1b;
  Ramffddd06c = 4;
  Ramffddd068 = 0x8605fe17;
  Ramffddd074 = 0xffffffff;
  Ramffddd070 = 0x8625fe1b;
  Ramffddd07c = 4;
  Ramffddd078 = 0x8605fe17;
  Ramffddd084 = 0xffffffff;
  Ramffddd080 = 0x8625fe1b;
  Ramffddd08c = 4;
  Ramffddd088 = 0x8605fe17;
  Ramffddd094 = 0xffffffff;
  Ramffddd090 = 0x8625fe1b;
  Ramffddd09c = 4;
  Ramffddd098 = 0x8605fe17;
  Ramffddd0a4 = 0xffffffff;
  Ramffddd0a0 = 0x8625fe1b;
  Ramffddd0ac = 4;
  Ramffddd0a8 = 0x8605fe17;
  Ramffddd0b4 = 0xffffffff;
  Ramffddd0b0 = 0x8625fe1b;
  Ramffddd0bc = 4;
  Ramffddd0b8 = 0x8605fe17;
  Ramffddd0c4 = 0xffffffff;
  Ramffddd0c0 = 0x8625fe1b;
  Ramffddd0cc = 4;
  Ramffddd0c8 = 0x8605fe17;
  Ramffddd0d4 = 0xffffffff;
  Ramffddd0d0 = 0x8625fe1b;
  Ramffddd0dc = 4;
  Ramffddd0d8 = 0x8605fe17;
  Ramffddd0e4 = 0xffffffff;
  Ramffddd0e0 = 0x8625fe1b;
  Ramffddd0ec = 4;
  Ramffddd0e8 = 0x8605fe17;
  Ramffddd0f4 = 0xffffffff;
  Ramffddd0f0 = 0x8625fe1b;
  Ramffddd0fc = 4;
  Ramffddd0f8 = 0x8605fe17;
  Ramffddd104 = 0xffffffff;
  Ramffddd100 = 0x8625fe1b;
  Ramffddd10c = 4;
  Ramffddd108 = 0x8605fe17;
  Ramffddd134 = 0xffffffff;
  Ramffddd130 = 0x8625fe1b;
  Ramffddd13c = 4;
  Ramffddd138 = 0x8605fe17;
  Ramffddd144 = 0xffffffff;
  Ramffddd140 = 0x8625fe1b;
  Ramffddd14c = 4;
  Ramffddd148 = 0x8605fe17;
  Ramffddd154 = 0xffffffff;
  Ramffddd150 = 0x8625fe1b;
  Ramffddd15c = 4;
  Ramffddd158 = 0x8605fe17;
  Ramffddd164 = 0xffffffff;
  Ramffddd160 = 0x8625fe1b;
  Ramffddd16c = 4;
  Ramffddd168 = 0x8605fe17;
  Ramffddd174 = 0xffffffff;
  Ramffddd170 = 0x8625fe1b;
  Ramffddd17c = 4;
  Ramffddd178 = 0x8605fe17;
  Ramffddd184 = 0xffffffff;
  Ramffddd180 = 0x8625fe1b;
  Ramffddd18c = 4;
  Ramffddd188 = 0x8605fe17;
  Ramffddd194 = 0xffffffff;
  Ramffddd190 = 0x8625fe1b;
  Ramffddd19c = 4;
  Ramffddd198 = 0x8605fe17;
  Ramffddd1a4 = 0xffffffff;
  Ramffddd1a0 = 0x8625fe1b;
  Ramffddd1ac = 4;
  Ramffddd1a8 = 0x8605fe17;
  Ramffddd1b4 = 0xffffffff;
  Ramffddd1b0 = 0x8625fe1b;
  Ramffddd1bc = 4;
  Ramffddd1b8 = 0x8605fe17;
  Ramffddd1c4 = 0xffffffff;
  Ramffddd1c0 = 0x8625fe1b;
  Ramffddd1cc = 4;
  Ramffddd1c8 = 0x8605fe17;
  Ramffddd1d4 = 0xffffffff;
  Ramffddd1d0 = 0x8625fe1b;
  Ramffddd1dc = 4;
  Ramffddd1d8 = 0x8605fe17;
  Ramffddd1e4 = 0xffffffff;
  Ramffddd1e0 = 0x8625fe1b;
  Ramffddd1ec = 4;
  Ramffddd1e8 = 0x8605fe17;
  Ramffddd1f4 = 0xffffffff;
  Ramffddd1f0 = 0x8625fe1b;
  Ramffddd1fc = 4;
  Ramffddd1f8 = 0x8605fe17;
  Ramffddd264 = 0xffffffff;
  Ramffddd260 = 0x8625fe1b;
  Ramffddd26c = 4;
  Ramffddd268 = 0x8605fe17;
  Ramffddd274 = 0xffffffff;
  Ramffddd270 = 0x8625fe1b;
  Ramffddd27c = 4;
  Ramffddd278 = 0x8605fe17;
  Ramfff94004 = 0xffffffff;
  Ramfff94000 = 0x8625fe1b;
  Ramfff9400c = 4;
  Ramfff94008 = 0x8605fe17;
  Ramfff94014 = 0xffffffff;
  Ramfff94010 = 0x8625fe1b;
  Ramfff9401c = 4;
  Ramfff94018 = 0x8605fe17;
  Ramfff94024 = 0xffffffff;
  Ramfff94020 = 0x8625fe1b;
  Ramfff9402c = 4;
  Ramfff94028 = 0x8605fe17;
  Ramfff94034 = 0xffffffff;
  Ramfff94030 = 0x8625fe1b;
  Ramfff9403c = 4;
  Ramfff94038 = 0x8605fe17;
  Ramfff94044 = 0xffffffff;
  Ramfff94040 = 0x8625fe1b;
  Ramfff9404c = 4;
  Ramfff94048 = 0x8605fe17;
  Ramfff94054 = 0xffffffff;
  Ramfff94050 = 0x8625fe1b;
  Ramfff9405c = 4;
  Ramfff94058 = 0x8605fe17;
  Ramfff94064 = 0xffffffff;
  Ramfff94060 = 0x8625fe1b;
  Ramfff9406c = 4;
  Ramfff94068 = 0x8605fe17;
  Ramfff94074 = 0xffffffff;
  Ramfff94070 = 0x8625fe1b;
  Ramfff9407c = 4;
  Ramfff94078 = 0x8605fe17;
  Ramfff94084 = 0xffffffff;
  Ramfff94080 = 0x8625fe1b;
  Ramfff9408c = 4;
  Ramfff94088 = 0x8605fe17;
  Ramfff94094 = 0xffffffff;
  Ramfff94090 = 0x8625fe1b;
  Ramfff9409c = 4;
  Ramfff94098 = 0x8605fe17;
  Ramfff940a4 = 0xffffffff;
  Ramfff940a0 = 0x8625fe1b;
  Ramfff940ac = 4;
  Ramfff940a8 = 0x8605fe17;
  Ramfff940b4 = 0xffffffff;
  Ramfff940b0 = 0x8625fe1b;
  Ramfff940bc = 0x44;
  Ramfff940b8 = 0x8625fe17;
  Ramfff940c4 = 0xffffffff;
  Ramfff940c0 = 0x8625fe1b;
  Ramfff940cc = 0x44;
  Ramfff940c8 = 0x8625fe17;
  Ramfff940d4 = 0xffffffff;
  Ramfff940d0 = 0x8625fe1b;
  Ramfff940dc = 4;
  Ramfff940d8 = 0x8605fe17;
  Ramfff940e4 = 0xffffffff;
  Ramfff940e0 = 0x8625fe1b;
  Ramfff940ec = 4;
  Ramfff940e8 = 0x8605fe17;
  Ramfff94104 = 0xffffffff;
  Ramfff94100 = 0x8625fe1b;
  Ramfff9410c = 4;
  Ramfff94108 = 0x8605fe17;
  Ramfff94114 = 0xffffffff;
  Ramfff94110 = 0x8625fe1b;
  Ramfff9411c = 4;
  Ramfff94118 = 0x8605fe17;
  Ramfff94124 = 0xffffffff;
  Ramfff94120 = 0x8625fe1b;
  Ramfff9412c = 4;
  Ramfff94128 = 0x8605fe17;
  Ramfff94134 = 0xffffffff;
  Ramfff94130 = 0x8625fe1b;
  Ramfff9413c = 4;
  Ramfff94138 = 0x8605fe17;
  Ramfff94144 = 0xffffffff;
  Ramfff94140 = 0x8625fe1b;
  Ramfff9414c = 4;
  Ramfff94148 = 0x8605fe17;
  Ramfff94154 = 0xffffffff;
  Ramfff94150 = 0x8625fe1b;
  Ramfff9415c = 4;
  Ramfff94158 = 0x8605fe17;
  Ramffc40004 = 0xffffffff;
  Ramffc40000 = 0x8625fe1b;
  Ramffc4000c = 4;
  Ramffc40008 = 0x8605fe17;
  Ramffc40014 = 0xffffffff;
  Ramffc40010 = 0x8625fe1b;
  Ramffc4001c = 4;
  Ramffc40018 = 0x8605fe17;
  Ramffc40024 = 0xffffffff;
  Ramffc40020 = 0x8625fe1b;
  Ramffc4002c = 4;
  Ramffc40028 = 0x8605fe17;
  Ramffc40034 = 0xffffffff;
  Ramffc40030 = 0x8625fe1b;
  Ramffc4003c = 4;
  Ramffc40038 = 0x8605fe17;
  Ramffc40044 = 0xffffffff;
  Ramffc40040 = 0x8625fe1b;
  Ramffc4004c = 4;
  Ramffc40048 = 0x8605fe17;
  Ramffc40054 = 0xffffffff;
  Ramffc40050 = 0x8625fe1b;
  Ramffc4005c = 4;
  Ramffc40058 = 0x8605fe17;
  Ramffc40064 = 0xffffffff;
  Ramffc40060 = 0x8625fe1b;
  Ramffc4006c = 4;
  Ramffc40068 = 0x8605fe17;
  Ramffc40074 = 0xffffffff;
  Ramffc40070 = 0x8625fe1b;
  Ramffc4007c = 4;
  Ramffc40078 = 0x8605fe17;
  Ramffc40084 = 0xffffffff;
  Ramffc40080 = 0x8625fe1b;
  Ramffc4008c = 4;
  Ramffc40088 = 0x8605fe17;
  Ramffc40094 = 0xffffffff;
  Ramffc40090 = 0x8625fe1b;
  Ramffc4009c = 4;
  Ramffc40098 = 0x8605fe17;
  Ramffc400b4 = 0xffffffff;
  Ramffc400b0 = 0x8625fe1b;
  Ramffc400bc = 4;
  Ramffc400b8 = 0x8605fe17;
  Ramffc400c4 = 0xffffffff;
  Ramffc400c0 = 0x8625fe1b;
  Ramffc400cc = 4;
  Ramffc400c8 = 0x8605fe17;
  Ramffc400d4 = 0xffffffff;
  Ramffc400d0 = 0x8625fe1b;
  Ramffc400dc = 4;
  Ramffc400d8 = 0x8605fe17;
  Ramffc400e4 = 0xffffffff;
  Ramffc400e0 = 0x8625fe1b;
  Ramffc400ec = 4;
  Ramffc400e8 = 0x8605fe17;
  Ramffc400f4 = 0xffffffff;
  Ramffc400f0 = 0x8625fe1b;
  Ramffc400fc = 4;
  Ramffc400f8 = 0x8605fe17;
  Ramffc40104 = 0xffffffff;
  Ramffc40100 = 0x8625fe1b;
  Ramffc4010c = 4;
  Ramffc40108 = 0x8605fe17;
  Ramffc40114 = 0xffffffff;
  Ramffc40110 = 0x8625fe1b;
  Ramffc4011c = 4;
  Ramffc40118 = 0x8605fe17;
  Ramffc40124 = 0xffffffff;
  Ramffc40120 = 0x8625fe1b;
  Ramffc4012c = 4;
  Ramffc40128 = 0x8605fe17;
  return;
}

void initialize_ffc49000_eight_register_groups_657fa(void)

{
  Ramffc49004 = 0xc;
  Ramffc49008 = 0;
  Ramffc4900c = 0x100000;
  Ramffc49000 = 0xc7fffe10;
  Ramffc49014 = 0;
  Ramffc49018 = 0;
  Ramffc4901c = 0;
  Ramffc49010 = 0x87fffe10;
  Ramffc49024 = 0;
  Ramffc49028 = 0;
  Ramffc4902c = 0;
  Ramffc49020 = 0x87fffe10;
  Ramffc49034 = 0;
  Ramffc49038 = 0;
  Ramffc4903c = 0;
  Ramffc49030 = 0x87fffe10;
  Ramffc49044 = 0;
  Ramffc49048 = 0;
  Ramffc4904c = 0;
  Ramffc49040 = 0x87fffe10;
  Ramffc49054 = 0;
  Ramffc49058 = 0;
  Ramffc4905c = 0;
  Ramffc49050 = 0x87fffe10;
  Ramffc49064 = 0;
  Ramffc49068 = 0;
  Ramffc4906c = 0;
  Ramffc49060 = 0x87fffe10;
  Ramffc49074 = 0;
  Ramffc49078 = 0;
  Ramffc4907c = 0;
  Ramffc49070 = 0x87fffe10;
  return;
}

void initialize_fffa0000_register_pair_65852(void)

{
  Ramfffa0004 = 0;
  Ramfffa0000 = 0x8601fe1b;
  Ramfffa000c = 0;
  Ramfffa0008 = 0x8601fe17;
  return;
}

undefined4 load_mpu_region_bounds_and_enable_profile_6586a(void)

{
  __synchronize();
  __synchronize();
  apply_mpu_attribute_profile(DAT_00031683);
  __synchronize();
  __synchronize();
  return 3;
}

void clear_febf3400_with_mpu_write_window_6595e(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  set_selected_mpu_region_attributes_659f8(0x40, 0xb8);
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x7c00))))) = 0;
  set_selected_mpu_region_attributes_659f8(0x40, 0xa8);
  return;
}

void apply_mpu_attribute_profile(uchar selector)
{
  camry_gpr[6] = selector;
  camry_gpr[30] = 0x31708u + ((uint32_t)selector << 6);
  camry_gpr[10] = camry_read32(camry_gpr[30] + 0u);
  camry_SR[6][2] = camry_gpr[10];
  camry_gpr[10] = camry_read32(camry_gpr[30] + 4u);
  camry_SR[6][6] = camry_gpr[10];
  camry_gpr[10] = camry_read32(camry_gpr[30] + 8u);
  camry_SR[6][10] = camry_gpr[10];
  camry_gpr[10] = camry_read32(camry_gpr[30] + 12u);
  camry_SR[6][14] = camry_gpr[10];
  camry_gpr[10] = camry_read32(camry_gpr[30] + 16u);
  camry_SR[6][18] = camry_gpr[10];
  camry_gpr[10] = camry_read32(camry_gpr[30] + 20u);
  camry_SR[6][22] = camry_gpr[10];
  camry_gpr[10] = camry_read32(camry_gpr[30] + 24u);
  camry_SR[6][26] = camry_gpr[10];
  camry_gpr[10] = camry_read32(camry_gpr[30] + 28u);
  camry_SR[6][30] = camry_gpr[10];
  camry_gpr[10] = camry_read32(camry_gpr[30] + 32u);
  camry_SR[7][2] = camry_gpr[10];
  camry_gpr[10] = camry_read32(camry_gpr[30] + 36u);
  camry_SR[7][6] = camry_gpr[10];
  camry_gpr[10] = camry_read32(camry_gpr[30] + 40u);
  camry_SR[7][10] = camry_gpr[10];
  camry_gpr[10] = camry_read32(camry_gpr[30] + 44u);
  camry_SR[7][14] = camry_gpr[10];
  camry_gpr[10] = camry_read32(camry_gpr[30] + 48u);
  camry_SR[7][18] = camry_gpr[10];
  camry_gpr[10] = camry_read32(camry_gpr[30] + 52u);
  camry_SR[7][22] = camry_gpr[10];
  camry_gpr[10] = camry_read32(camry_gpr[30] + 56u);
  camry_SR[7][26] = camry_gpr[10];
  camry_gpr[10] = camry_read32(camry_gpr[30] + 60u);
  camry_SR[7][30] = camry_gpr[10];
  __synchronize();
  return;
}

void set_selected_mpu_region_attributes_659f8(uint32_t mask, uint32_t attributes)
{
  camry_gpr[6] = mask;
  camry_r7 = camry_gpr[7] = attributes;
  camry_gpr[10] = mask;
  camry_gpr[11] = attributes;
  camry_gpr[12] = camry_gpr[10] & 1u;
  if (camry_gpr[12]) camry_SR[6][2] = attributes;
  camry_gpr[10] >>= 1;
  camry_gpr[12] = camry_gpr[10] & 1u;
  if (camry_gpr[12]) camry_SR[6][6] = attributes;
  camry_gpr[10] >>= 1;
  camry_gpr[12] = camry_gpr[10] & 1u;
  if (camry_gpr[12]) camry_SR[6][10] = attributes;
  camry_gpr[10] >>= 1;
  camry_gpr[12] = camry_gpr[10] & 1u;
  if (camry_gpr[12]) camry_SR[6][14] = attributes;
  camry_gpr[10] >>= 1;
  camry_gpr[12] = camry_gpr[10] & 1u;
  if (camry_gpr[12]) camry_SR[6][18] = attributes;
  camry_gpr[10] >>= 1;
  camry_gpr[12] = camry_gpr[10] & 1u;
  if (camry_gpr[12]) camry_SR[6][22] = attributes;
  camry_gpr[10] >>= 1;
  camry_gpr[12] = camry_gpr[10] & 1u;
  if (camry_gpr[12]) camry_SR[6][26] = attributes;
  camry_gpr[10] >>= 1;
  camry_gpr[12] = camry_gpr[10] & 1u;
  if (camry_gpr[12]) camry_SR[6][30] = attributes;
  camry_gpr[10] >>= 1;
  camry_gpr[12] = camry_gpr[10] & 1u;
  if (camry_gpr[12]) camry_SR[7][2] = attributes;
  camry_gpr[10] >>= 1;
  camry_gpr[12] = camry_gpr[10] & 1u;
  if (camry_gpr[12]) camry_SR[7][6] = attributes;
  camry_gpr[10] >>= 1;
  camry_gpr[12] = camry_gpr[10] & 1u;
  if (camry_gpr[12]) camry_SR[7][10] = attributes;
  camry_gpr[10] >>= 1;
  camry_gpr[12] = camry_gpr[10] & 1u;
  if (camry_gpr[12]) camry_SR[7][14] = attributes;
  camry_gpr[10] >>= 1;
  camry_gpr[12] = camry_gpr[10] & 1u;
  if (camry_gpr[12]) camry_SR[7][18] = attributes;
  camry_gpr[10] >>= 1;
  camry_gpr[12] = camry_gpr[10] & 1u;
  if (camry_gpr[12]) camry_SR[7][22] = attributes;
  camry_gpr[10] >>= 1;
  camry_gpr[12] = camry_gpr[10] & 1u;
  if (camry_gpr[12]) camry_SR[7][26] = attributes;
  camry_gpr[10] >>= 1;
  camry_gpr[12] = camry_gpr[10] & 1u;
  if (camry_gpr[12]) camry_SR[7][30] = attributes;
  __synchronize();
  return;
}

uint32_t push_sixteen_mpu_attributes_65ac0(void)
{
  uint32_t value;
  camry_sp -= 64u;
  value = camry_SR[6][2];
  camry_write32(camry_sp + 60u, value);
  value = camry_SR[6][6];
  camry_write32(camry_sp + 56u, value);
  value = camry_SR[6][10];
  camry_write32(camry_sp + 52u, value);
  value = camry_SR[6][14];
  camry_write32(camry_sp + 48u, value);
  value = camry_SR[6][18];
  camry_write32(camry_sp + 44u, value);
  value = camry_SR[6][22];
  camry_write32(camry_sp + 40u, value);
  value = camry_SR[6][26];
  camry_write32(camry_sp + 36u, value);
  value = camry_SR[6][30];
  camry_write32(camry_sp + 32u, value);
  value = camry_SR[7][2];
  camry_write32(camry_sp + 28u, value);
  value = camry_SR[7][6];
  camry_write32(camry_sp + 24u, value);
  value = camry_SR[7][10];
  camry_write32(camry_sp + 20u, value);
  value = camry_SR[7][14];
  camry_write32(camry_sp + 16u, value);
  value = camry_SR[7][18];
  camry_write32(camry_sp + 12u, value);
  value = camry_SR[7][22];
  camry_write32(camry_sp + 8u, value);
  value = camry_SR[7][26];
  camry_write32(camry_sp + 4u, value);
  value = camry_SR[7][30];
  camry_write32(camry_sp + 0u, value);
  __synchronize();
  return value;
}

uint32_t pop_sixteen_mpu_attributes_65b4a(void)
{
  uint32_t value;
  value = camry_read32(camry_sp + 60u);
  camry_SR[6][2] = value;
  value = camry_read32(camry_sp + 56u);
  camry_SR[6][6] = value;
  value = camry_read32(camry_sp + 52u);
  camry_SR[6][10] = value;
  value = camry_read32(camry_sp + 48u);
  camry_SR[6][14] = value;
  value = camry_read32(camry_sp + 44u);
  camry_SR[6][18] = value;
  value = camry_read32(camry_sp + 40u);
  camry_SR[6][22] = value;
  value = camry_read32(camry_sp + 36u);
  camry_SR[6][26] = value;
  value = camry_read32(camry_sp + 32u);
  camry_SR[6][30] = value;
  value = camry_read32(camry_sp + 28u);
  camry_SR[7][2] = value;
  value = camry_read32(camry_sp + 24u);
  camry_SR[7][6] = value;
  value = camry_read32(camry_sp + 20u);
  camry_SR[7][10] = value;
  value = camry_read32(camry_sp + 16u);
  camry_SR[7][14] = value;
  value = camry_read32(camry_sp + 12u);
  camry_SR[7][18] = value;
  value = camry_read32(camry_sp + 8u);
  camry_SR[7][22] = value;
  value = camry_read32(camry_sp + 4u);
  camry_SR[7][26] = value;
  value = camry_read32(camry_sp + 0u);
  camry_SR[7][30] = value;
  __synchronize();
  camry_sp += 64u;
  return value;
}

void increment_saturating_exception_counter_and_feret_65bd4(void)
{
  uint32_t saved_mpat6 = camry_SR[6][26];
  camry_SR[6][26] = 0xb8u;
  __synchronize();
  uint32_t count = camry_read8(0xfebf3400u);
  if (count != 0xffu) camry_write8(0xfebf3400u, count + 1u);
  camry_SR[6][26] = saved_mpat6;
  __synchronize();
  camry_SR[0][2] += 4u;
  camry_gpr[3] = camry_sp;
  camry_gpr_export_aliases();
  if (!(camry_psw & 0x40u) && !(camry_SR[2][13] & 1u))
    camry_SR[2][10] &= camry_SR[2][10] - 1u;
  camry_psw = camry_SR[0][3];
  camry_gpr_import_aliases();
  camry_SR[2][12] &= ~2u;
  if ((camry_SR[0][11] & 1u) != 0) {
    uint32_t priority = camry_SR[1][7] & 31u;
    if (priority > 16u) priority = 16u;
    unsigned mask_priority = priority > 15u ? 15u : priority;
    uint32_t masked = (camry_pmr >> mask_priority) & 1u;
    camry_SR[2][12] |= masked << 1;
    if (!masked && !(camry_SR[2][10] & ((1u << (priority + 1u)) - 1u) & 0xffffu)
        && !(camry_psw & 0xa0u)) {
      uint32_t vector = (camry_SR[1][(camry_psw & 0x8000u) ? 3 : 2] & 0xfffffe00u) + 0x70u;
      camry_SR[0][11] = 0;
      camry_SR[0][0] = camry_SR[0][2];
      camry_SR[0][1] = camry_psw;
      camry_SR[0][13] = 0x72u;
      camry_psw = (camry_psw & 0xbfffffffu) | 0x60u;
      camry_gpr_export_aliases();
      camry_gpr[10] = ((uint32_t (*)(uint32_t, uint32_t, uint32_t, uint32_t))camry_indirect(vector))
          (camry_gpr[6], camry_gpr[7], camry_gpr[8], camry_gpr[9]);
      camry_gpr_import_aliases();
    }
  }
  camry_gpr_import_aliases();
  return;
}

void clear_febf3402_with_mpu_write_window_65c64(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  set_selected_mpu_region_attributes_659f8(0x40, 0xb8);
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x7c02))))) = 0;
  set_selected_mpu_region_attributes_659f8(0x40, 0xa8);
  return;
}

void clear_ffc654_status_and_ecm_bit16_65c88(void)

{
  undefined4 uVar1;
  uchar uVar2;
  byte bVar3;
  
  Ramffc65408 = 0xffffffff;
  Ramffc6540c = 0xf;
  uVar1 = Ramffc6540c;
  bVar3 = 0;
  __synchronize();
  do {
    ECMPCMD1 = 0xa5;
    ECMESSTC0 = 0x10000;
    ECMESSTC0 = 0xfffeffff;
    ECMESSTC0 = 0x10000;
    uVar2 = ECMPS;
    __synchronize();
    if (uVar2 == '\0') {
      return;
    }
    bVar3 = bVar3 + 1;
  } while (bVar3 < 3);
                    /* WARNING: Subroutine does not return */
  enter_terminal_hardware_sequence();
}

void count_ffc654_fault_and_clear_or_terminate_65cda(void)

{
  uint32_t puVar1;
  byte bVar2;
  
  puVar1 = 0xfebeb800u;
  bVar2 = DAT_febf3402;
  if (DAT_febf3402 != 0xff) {
    bVar2 = DAT_febf3402 + 1;
  }
  if (DAT_00030dec <= bVar2) {
    store_three_pattern_encoded_control_words_62b90((int)0xd6d6d6d6);
                    /* WARNING: Subroutine does not return */
    enter_terminal_hardware_sequence();
  }
  clear_ffc654_status_and_ecm_bit16_65c88();
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x7c02))))) = bVar2;
  return;
}

void spin_thirty_two_iterations_65d14(void)

{
  uint uVar1;
  
  for (uVar1 = 0; uVar1 < 0x20; uVar1 = uVar1 + 1) {
  }
  return;
}

void delay_if_febe39d9_bit0_set_65d38(void)

{
  if ((DAT_febe39d9 & 1) != 0) {
    spin_thirty_two_iterations_65d14();
  }
  return;
}

void clear_febf3403_with_mpu_write_window_65d4a(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  set_selected_mpu_region_attributes_659f8(0x40, 0xb8);
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x7c03))))) = 0;
  set_selected_mpu_region_attributes_659f8(0x40, 0xa8);
  return;
}

void clear_ecm_bit19_and_ucf_error_status_65d6e(void)

{
  uint uVar1;
  uint uVar2;
  uchar uVar3;
  byte bVar4;
  
  bVar4 = 0;
  do {
    ECMPCMD1 = 0xa5;
    ECMESSTC0 = 0x80000;
    ECMESSTC0 = 0xfff7ffff;
    ECMESSTC0 = 0x80000;
    uVar3 = ECMPS;
    __synchronize();
    if (uVar3 == '\0') {
      uVar1 = UCFDERSTR;
      uVar2 = UCFDEDADR;
      if (((uVar1 & 1) != 0) || ((uVar1 >> 2 & 1) != 0)) {
        camry_write32(0xffc62008u, 1);
        uVar1 = camry_read32(0xffc62008u);
        __synchronize();
        configure_debug_cache_and_invalidate_instruction_cache_71c48();
      }
      return;
    }
    bVar4 = bVar4 + 1;
  } while (bVar4 < 3);
                    /* WARNING: Subroutine does not return */
  enter_terminal_hardware_sequence();
}

void handle_ucf_error_address_or_count_fault_65dd6(void)

{
  uint uVar1;
  uchar uVar2;
  
  uVar1 = UCFDEDADR;
  if (uVar1 + 0xfeff6000 < 0x2000) {
    ECMPCMD1 = 0xa5;
    ECMESSTC0 = 0x80000;
    ECMESSTC0 = 0xfff7ffff;
    ECMESSTC0 = 0x80000;
    uVar2 = ECMPS;
    __synchronize();
    camry_write32(0xffc62008u, 1);
    uVar1 = camry_read32(0xffc62008u);
    __synchronize();
  }
  else {
    if (DAT_febf3403 != 0xff) {
      DAT_febf3403 = DAT_febf3403 + 1;
    }
    if (DAT_00030ded <= DAT_febf3403) {
      store_three_pattern_encoded_control_words_62b90((int)0xc7c7c7c7);
                    /* WARNING: Subroutine does not return */
      enter_terminal_hardware_sequence();
    }
    clear_ecm_bit19_and_ucf_error_status_65d6e();
  }
  return;
}

void clear_febf3404_with_mpu_write_window_65e58(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  set_selected_mpu_region_attributes_659f8(0x40, 0xb8);
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x7c04))))) = 0;
  set_selected_mpu_region_attributes_659f8(0x40, 0xa8);
  return;
}

void clear_multiple_register_statuses_and_ecm_bit28_65e7c(void)

{
  undefined4 uVar1;
  uchar uVar2;
  byte bVar3;
  
  bVar3 = 0;
  Ramffc62c08 = 1;
  Ramffc63408 = 1;
  Ramffc66008 = 1;
  Ramffc66408 = 1;
  Ramffc67008 = 1;
  Ramffc67408 = 1;
  Ramffc67808 = 1;
  Ramffc68408 = 1;
  Ramffc6a008 = 1;
  Ramffc6c008 = 1;
  uVar1 = Ramffc6c008;
  __synchronize();
  Ramffddd808 = 1;
  uVar1 = Ramffddd808;
  __synchronize();
  Ramfff94808 = 1;
  uVar1 = Ramfff94808;
  __synchronize();
  Ramffc40808 = 1;
  uVar1 = Ramffc40808;
  __synchronize();
  do {
    ECMPCMD1 = 0xa5;
    ECMESSTC0 = 0x10000000;
    ECMESSTC0 = 0xefffffff;
    ECMESSTC0 = 0x10000000;
    uVar2 = ECMPS;
    __synchronize();
    if (uVar2 == '\0') {
      return;
    }
    bVar3 = bVar3 + 1;
  } while (bVar3 < 3);
                    /* WARNING: Subroutine does not return */
  enter_terminal_hardware_sequence();
}

void count_register_fault_and_clear_or_terminate_65f24(void)

{
  uint32_t puVar1;
  byte bVar2;
  
  puVar1 = 0xfebeb800u;
  bVar2 = DAT_febf3404;
  if (DAT_febf3404 != 0xff) {
    bVar2 = DAT_febf3404 + 1;
  }
  if (DAT_00030dee <= bVar2) {
    store_three_pattern_encoded_control_words_62b90((int)0xe3e3e3e3);
                    /* WARNING: Subroutine does not return */
    enter_terminal_hardware_sequence();
  }
  clear_multiple_register_statuses_and_ecm_bit28_65e7c();
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x7c04))))) = bVar2;
  return;
}

void disable_ffc0a000_block_and_transfer_to_boot_65f5e(void)

{
  undefined4 uVar1;
  
  priority_mask_enter(0xffff);
  Ramffc0a000 = 0;
  Ramffc0a004 = 0;
  Ramffc0a008 = 0;
  Ramffc0a00c = 0;
  uVar1 = Ramffc0a00c;
  __synchronize();
  application_transfer_to_boot_context(&boot_application_handoff_record.tag);
  enter_terminal_hardware_sequence();
  return;
}

void initialize_supervision_and_clear_four_state_bytes_65f8e(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  initialize_task_progress_supervision();
  initialize_execution_profiles();
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x7e28))))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x7e27))))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x7e26))))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x7e25))))) = 0;
  return;
}

void run_ch0_application_task(void)

{
  camry_write32((camry_sp - 4u) & ~3u, camry_gpr[29]);
  camry_write32((camry_sp - 8u) & ~3u, camry_gpr[31]);
  camry_sp -= 8u;
  camry_gpr[3] = camry_sp;

  uint32_t puVar1;
  int iVar2;
  
  puVar1 = 0xfebeb800u;
  iVar2 = 0;
  if (execution_profiling_enabled == 'Z') {
    puVar1 = 0xfebeb800u;
    (camry_gpr[31] = 0x65fc6u, begin_execution_profile_slot0)();
    iVar2 = 0x5a;
  }
  (camry_gpr[29] = iVar2, camry_gpr[31] = 0x65fceu, record_ch0_dispatch)();
  (camry_gpr[29] = iVar2, camry_gpr[31] = 0x65fd2u, fast_control_cycle)();
  if (iVar2 == 0x5a) {
    (camry_gpr[29] = iVar2, camry_gpr[31] = 0x65fdcu, end_execution_profile_slot0)();
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x7e28))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x7e28))))) + '\x01';
  { if (!camry_halted) { camry_gpr[29] = camry_read32((camry_sp + 4u) & ~3u); camry_gpr[31] = camry_read32((camry_sp + 0u) & ~3u); camry_sp += 8u; camry_gpr[3] = camry_sp; } return; }
}

void run_ch1_application_task(void)

{
  uint32_t puVar1;
  int iVar2;
  
  puVar1 = 0xfebeb800u;
  iVar2 = 0;
  if (execution_profiling_enabled == 'Z') {
    puVar1 = 0xfebeb800u;
    begin_execution_profile_slot2();
    iVar2 = 0x5a;
  }
  record_ch1_dispatch();
  run_init_chain_6679e();
  if (iVar2 == 0x5a) {
    end_execution_profile_slot2();
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x7e27))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x7e27))))) + '\x01';
  return;
}
