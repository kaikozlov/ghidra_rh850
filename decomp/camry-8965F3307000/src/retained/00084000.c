#include "common.h"

void driver_poll_pending_channel_modes(void)

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
      iVar5 = activate_global_configuration_then_start_channel_84e8c(uVar8);
      if (iVar5 == 0) {
        *puVar7 = 0x57a8;
        uVar4 = 2;
LAB_0008412a:
        ((void)(uVar8), (void)(uVar4), return_only_stub_7fb5c());
      }
    }
    else if (sVar1 == 0x3ec1) {
      if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(uVar8 * 4 + -0xf9d))))) == '\0') {
        driver_observe_and_clear_bus_off_entry((uchar)uVar8);
      }
      iVar5 = enter_channel_mode_one_only_after_transmit_idle_84ec0(uVar8);
      if (iVar5 == 0) {
        *puVar7 = 0x6b94;
        uVar4 = 3;
        goto LAB_0008412a;
      }
    }
    else if ((sVar1 == 0x3dc2) && (iVar5 = reload_global_configuration_and_selected_channel_84f06(uVar8), iVar5 == 0)) {
      clear_driver_busoff_observation_latch_835c6(uVar8);
      ((void)(uVar8), reload_acceptance_filters_when_count_differs_in_mode_one_84fea());
      *puVar7 = 0x6b94;
    }
    uVar8 = uVar8 + 1 & 0xff;
  } while( true );
}

void reset_all_channel_states_and_quiesce_registers_84160(void)

{
  byte bVar1;
  uint32_t puVar2;
  uint32_t puVar3;
  undefined4 uVar4;
  uint uVar5;
  
  puVar2 = 0xfebeb800u;
  puVar3 = 0x23dfcu;
  uVar4 = call_interrupt_guard_and_return_zero_7a2da();
  bVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0xfbb)))));
  for (uVar5 = 0; uVar5 < bVar1; uVar5 = uVar5 + 1 & 0xff) {
    (*((undefined2 *)camry_host_ptr((uint32_t)(puVar2 + uVar5 * 2 + -0x67e0)))) = 0x6e91;
  }
  ((void)(uVar4), thunk_pop_and_restore_priority_mask_stack_6a4c4());
  quiesce_configured_channels_and_enter_global_mode_five_84f90();
  for (uVar5 = 0; uVar5 < bVar1; uVar5 = uVar5 + 1 & 0xff) {
    clear_driver_busoff_observation_latch_835c6(uVar5);
  }
  return;
}

int reconfigure_channel_after_clearing_tx_routes_841a6(uint param_1)

{
  int iVar1;
  
  param_1 = param_1 & 0xff;
  ((volatile F33DriverChannelSoftwareState *)camry_host_ptr((uint32_t)(0xfebe5020u + (uint32_t)(param_1) * (uint32_t)sizeof(F33DriverChannelSoftwareState))))[0] = recovery_pending;
  invalidate_channel_can_transmit_route_slots_850e0((uint)(byte)param_1);
  iVar1 = repair_global_configuration_then_reload_channel_84e44(param_1);
  if (iVar1 == 0) {
    ((void)(param_1), reload_acceptance_filters_when_count_differs_in_mode_one_84fea());
    ((volatile F33DriverChannelSoftwareState *)camry_host_ptr((uint32_t)(0xfebe5020u + (uint32_t)(param_1) * (uint32_t)sizeof(F33DriverChannelSoftwareState))))[0] = stopped_software_state;
  }
  clear_driver_busoff_observation_latch_835c6(param_1);
  return iVar1;
}

bool set_channel_timing_returns_failure_841e6(undefined1 param_1,undefined2 param_2)

{
  int iVar1;
  
  iVar1 = apply_indexed_channel_timing_profile_85012(param_1,param_2);
  return iVar1 != 0;
}

bool is_channel_outside_states_6d92_and_6b94_841fc(uint param_1)

{
  if (((volatile F33DriverChannelSoftwareState *)camry_host_ptr((uint32_t)(0xfebe5020u + (uint32_t)(param_1 & 0xff) * (uint32_t)sizeof(F33DriverChannelSoftwareState))))[0] != initialized) {
    return ((volatile F33DriverChannelSoftwareState *)camry_host_ptr((uint32_t)(0xfebe5020u + (uint32_t)(param_1 & 0xff) * (uint32_t)sizeof(F33DriverChannelSoftwareState))))[0] != stopped_software_state;
  }
  return false;
}

int request_channel_quiesce_and_update_state_84274(uint param_1)

{
  int iVar1;
  
  ((volatile F33DriverChannelSoftwareState *)camry_host_ptr((uint32_t)(0xfebe5020u + (uint32_t)(param_1 & 0xff) * (uint32_t)sizeof(F33DriverChannelSoftwareState))))[0] = stop_pending;
  iVar1 = cancel_pending_channel_transmits_before_mode_one_84b74((uint)(byte)param_1);
  if (iVar1 == 0) {
    ((volatile F33DriverChannelSoftwareState *)camry_host_ptr((uint32_t)(0xfebe5020u + (uint32_t)(param_1 & 0xff) * (uint32_t)sizeof(F33DriverChannelSoftwareState))))[0] = stopped_software_state;
  }
  return iVar1;
}

void normalize_pending_channel_states_to_6b94_842a0(uint param_1)

{
  F33DriverChannelSoftwareState FVar1;
  
  FVar1 = ((volatile F33DriverChannelSoftwareState *)camry_host_ptr((uint32_t)(0xfebe5020u + (uint32_t)(param_1 & 0xff) * (uint32_t)sizeof(F33DriverChannelSoftwareState))))[0];
  if ((((FVar1 == start_pending) || (FVar1 == recovery_pending)) || (FVar1 == stop_pending)) ||
     (FVar1 == running_software_state)) {
    ((volatile F33DriverChannelSoftwareState *)camry_host_ptr((uint32_t)(0xfebe5020u + (uint32_t)(param_1 & 0xff) * (uint32_t)sizeof(F33DriverChannelSoftwareState))))[0] = stopped_software_state;
  }
  return;
}

void call_return_only_channel_hook_842ce(undefined1 param_1)

{
  ((void)(param_1), return_only_stub_6a434());
  return;
}

void copy_configured_channel_mode_bytes_842dc(void)

{
  uint uVar1;
  uint uVar2;
  
  uVar2 = (uint)DAT_00022ea4;
  for (uVar1 = 0; uVar1 < uVar2; uVar1 = uVar1 + 1 & 0xff) {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe5026u + (uint32_t)(uVar1) * 1u)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x22eabu + (uint32_t)(uVar1) * 1u))));
  }
  return;
}

undefined4 request_global_mode_one_and_poll_bounded_842fe(void)

{
  ushort uVar1;
  ushort uVar2;
  uint32_t puVar3;
  undefined4 uVar4;
  uint uVar5;
  
  uVar1 = DAT_00022e8e;
  puVar3 = 0x23dfcu;
  uVar4 = call_interrupt_guard_and_return_zero_7a2da();
  (*((volatile undefined4 *)camry_host_ptr((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x23dfcu + (uint32_t)(-0xdbc) * 1u))))))) = 0x10001;
  uVar2 = 0;
  uVar5 = 0xfffffffe;
  while ((uVar2 < uVar1 && ((uVar5 & 0xf) != 1))) {
    uVar2 = uVar2 + 1;
    uVar5 = (*((volatile uint *)camry_host_ptr((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x23dfcu + (uint32_t)(-0xdb8) * 1u)))))));
  }
  ((void)(uVar4), thunk_pop_and_restore_priority_mask_stack_6a4c4());
  return uVar4;
}

void reset_global_can_configuration_and_buffers_8433c(void)

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

undefined4 request_channel_mode_one_and_poll_bounded_84420(ushort param_1)

{
  int iVar1;
  ushort uVar2;
  ushort uVar3;
  undefined4 uVar4;
  uint uVar5;
  
  uVar2 = DAT_00022e8c;
  iVar1 = (int)(short)(param_1 & 0xff);
  uVar4 = call_interrupt_guard_and_return_zero_7a2da();
  (*((uint *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x22ef4u + (uint32_t)(iVar1 * 0x1d) * 4u))))))) =
       (*((uint *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x22ef4u + (uint32_t)(iVar1 * 0x1d) * 4u))))))) & 0xfffffff8 | 1;
  uVar3 = 0;
  uVar5 = 0xfffffffe;
  while ((uVar3 < uVar2 && ((uVar5 & 7) != 1))) {
    uVar3 = uVar3 + 1;
    uVar5 = (*((uint *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x22ef8u + (uint32_t)(iVar1 * 0x1d) * 4u)))))));
  }
  ((void)(uVar4), thunk_pop_and_restore_priority_mask_stack_6a4c4());
  return uVar4;
}

void reset_channel_registers_and_transmit_buffers_84474(ushort param_1)

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
    (*((undefined4 *)camry_host_ptr((uint32_t)(*(int *)(((undefined *)camry_host_ptr((uint32_t)(0x22f48u + (uint32_t)(iVar6) * 1u)))) + iVar4)))) = 0x9fffffff;
    (*((undefined4 *)camry_host_ptr((uint32_t)(*(int *)(((undefined *)camry_host_ptr((uint32_t)(0x22f48u + (uint32_t)(iVar6) * 1u)))) + iVar4 + 4)))) = 0;
    (*((undefined4 *)camry_host_ptr((uint32_t)(*(int *)(((undefined *)camry_host_ptr((uint32_t)(0x22f48u + (uint32_t)(iVar6) * 1u)))) + iVar4 + 8)))) = 0;
    uVar5 = 0;
    do {
      iVar2 = uVar5 * 4;
      uVar5 = uVar5 + 1;
      (*((undefined4 *)camry_host_ptr((uint32_t)(iVar2 + *(int *)(((undefined *)camry_host_ptr((uint32_t)(0x22f48u + (uint32_t)(iVar6) * 1u)))) + iVar4 + 0xc)))) = 0;
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

void request_channel_mode_five_and_poll_three_times_84534(ushort param_1)

{
  ushort uVar1;
  uint uVar2;
  
  param_1 = param_1 & 0xff;
  uVar2 = 1;
  (*((uint *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x22ef4u + (uint32_t)((short)param_1 * 0x1d) * 4u))))))) =
       *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x233c8u + (uint32_t)((short)param_1 * 0x34) * 1u)))) | 5;
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

void load_global_can_configuration_with_fifos_disabled_84570(void)

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

undefined4 initialize_can_registers_after_global_status_bit3_clears_84652(void)

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
  initialize_bank_test_and_integrity_latches_83c72();
  copy_configured_channel_mode_bytes_842dc();
  iVar4 = (int)((ulonglong)uVar3 >> 0x20);
  uVar5 = 0;
  uVar2 = 0xffffffff;
  while ((uVar5 < (*((uint *)camry_host_ptr((uint32_t)(iVar4 + -0xf84)))) && ((uVar2 >> 3 & 1) != 0))) {
    uVar5 = uVar5 + 1;
    uVar2 = (*((volatile uint *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)((iVar4 + -0xdb8)))))))));
  }
  if (((uVar2 >> 3 & 1) == 0) &&
     (request_global_mode_one_and_poll_bounded_842fe(), ((*((volatile uint *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(((int)((ulonglong)uVar3 >> 0x20) + -0xdb8))))))))) & 0xf) == 1)) {
    reset_global_can_configuration_and_buffers_8433c();
    bVar1 = (*((byte *)camry_host_ptr((uint32_t)((int)((ulonglong)uVar3 >> 0x20) + -0xf58))));
    for (uVar6 = 0; uVar6 < bVar1; uVar6 = uVar6 + 1 & 0xff) {
      iVar4 = (short)uVar6 * 6 + (int)((ulonglong)uVar3 >> 0x20);
      if ((*((char *)camry_host_ptr((uint32_t)(iVar4 + -0xf31)))) == '\0') {
        request_channel_mode_one_and_poll_bounded_84420(uVar6);
        if (((*((volatile uint *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(((short)uVar6 * 0x74 + (int)((ulonglong)uVar3 >> 0x20) + -0xf04))))))))) & 7) == 1)
        {
          reset_channel_registers_and_transmit_buffers_84474(uVar6);
        }
        if ((*((char *)camry_host_ptr((uint32_t)(iVar4 + -0xf30)))) != '\0') {
          request_channel_mode_five_and_poll_three_times_84534(uVar6);
        }
      }
    }
    load_global_can_configuration_with_fifos_disabled_84570();
    uVar7 = 0;
  }
  return uVar7;
}

void load_channel_timing_and_clear_status_registers_846f2(ushort param_1)

{
  int iVar1;
  int iVar2;
  
  if (((*((uint *)camry_host_ptr((uint32_t)(PTR_GSTS_00023044)))) & 0xf) == 1) {
    (*((undefined4 *)camry_host_ptr((uint32_t)(PTR_GCFG_0002303c)))) = DAT_00022e80;
  }
  iVar1 = (int)(short)(param_1 & 0xff);
  iVar2 = (short)(param_1 & 0xff) * 0x34;
  (*((uint *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x22ef4u + (uint32_t)(iVar1 * 0x1d) * 4u))))))) = *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x233c8u + (uint32_t)(iVar2) * 1u)))) | 1;
  (*((undefined2 *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x22edcu + (uint32_t)(iVar1 * 0x1d) * 4u))))))) = 0;
  (*((undefined4 *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x22f14u + (uint32_t)(iVar1 * 0x1d) * 4u))))))) = 0;
  (*((undefined4 *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x22f20u + (uint32_t)(iVar1 * 0x1d) * 4u))))))) = 0;
  (*((undefined4 *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x22ef0u + (uint32_t)(iVar1 * 0x1d) * 4u))))))) = *(undefined4 *)(((undefined *)camry_host_ptr((uint32_t)(0x233c4u + (uint32_t)(iVar2) * 1u))));
  (*((undefined4 *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x22f00u + (uint32_t)(iVar1 * 0x1d) * 4u))))))) = *(undefined4 *)(((undefined *)camry_host_ptr((uint32_t)(0x233dcu + (uint32_t)(iVar2) * 1u))));
  (*((undefined4 *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x22f04u + (uint32_t)(iVar1 * 0x1d) * 4u))))))) = *(undefined4 *)(((undefined *)camry_host_ptr((uint32_t)(0x233e0u + (uint32_t)(iVar2) * 1u))));
  (*((undefined4 *)camry_host_ptr((uint32_t)(PTR_DAT_00023048)))) = 0;
  return;
}

undefined4 configure_channel_only_in_global_and_channel_reset_modes_84760(uint param_1)

{
  undefined4 uVar1;
  
  param_1 = param_1 & 0xff;
  uVar1 = 2;
  if ((((*((uint *)camry_host_ptr((uint32_t)(PTR_GSTS_00023044)))) & 0xf) < 2) &&
     (((*((uint *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x22ef8u + (uint32_t)((short)param_1 * 0x1d) * 4u))))))) & 7) == 1)) {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe5026u + (uint32_t)(param_1) * 1u)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x22eabu + (uint32_t)(param_1) * 1u))));
    load_channel_timing_and_clear_status_registers_846f2((uint)(byte)param_1);
    uVar1 = 0;
  }
  return uVar1;
}

void load_paged_can_acceptance_filter_rules_847a4(void)

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
    uVar5 = *(undefined4 *)(((undefined *)camry_host_ptr((uint32_t)(0x22e68u + (uint32_t)((uint)(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x230c4u + (uint32_t)(iVar1) * 1u)))) * 4) * 1u))));
    iVar2 = (uVar3 & 0xf) * 0x10;
    (*((undefined4 *)camry_host_ptr((uint32_t)(PTR_DAT_000230a4 + iVar2)))) = *(undefined4 *)(((undefined *)camry_host_ptr((uint32_t)(0x230b8u + (uint32_t)(iVar1) * 1u))));
    (*((undefined4 *)camry_host_ptr((uint32_t)(PTR_DAT_000230a4 + iVar2 + 4)))) = uVar5;
    (*((undefined4 *)camry_host_ptr((uint32_t)(PTR_DAT_000230a4 + iVar2 + 8)))) = *(undefined4 *)(((undefined *)camry_host_ptr((uint32_t)(0x230bcu + (uint32_t)(iVar1) * 1u))));
    (*((undefined4 *)camry_host_ptr((uint32_t)(PTR_DAT_000230a4 + iVar2 + 0xc)))) = *(undefined4 *)(((undefined *)camry_host_ptr((uint32_t)(0x230c0u + (uint32_t)(iVar1) * 1u))));
  }
  (*((undefined4 *)camry_host_ptr((uint32_t)(PTR_DAT_00023050)))) = 0;
  return;
}

void request_global_mode_zero_and_poll_ten_times_8481c(void)

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

void load_can_configuration_filters_and_enter_global_mode_zero_8483e(void)

{
  load_global_can_configuration_with_fifos_disabled_84570();
  load_paged_can_acceptance_filter_rules_847a4();
  request_global_mode_zero_and_poll_ten_times_8481c();
  return;
}

void load_channel_control_and_poll_mode_zero_84852(ushort param_1)

{
  ushort uVar1;
  uint uVar2;
  
  param_1 = param_1 & 0xff;
  (*((undefined4 *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x22ef4u + (uint32_t)((short)param_1 * 0x1d) * 4u))))))) =
       *(undefined4 *)(((undefined *)camry_host_ptr((uint32_t)(0x233c8u + (uint32_t)((short)param_1 * 0x34) * 1u))));
  uVar1 = 0;
  uVar2 = 1;
  while ((uVar1 < DAT_00022e8a && ((uVar2 & 7) != 0))) {
    uVar1 = uVar1 + 1;
    uVar2 = (*((uint *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x22ef8u + (uint32_t)((short)param_1 * 0x1d) * 4u)))))));
  }
  return;
}

undefined4 reset_transmit_storage_and_enter_channel_mode_zero_8488c(uint param_1)

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
        (*(ushort *)(((undefined *)camry_host_ptr((uint32_t)(0x22ebeu + (uint32_t)(param_1 * 4) * 1u)))) | *(ushort *)(((undefined *)camry_host_ptr((uint32_t)(0x22ebcu + (uint32_t)(param_1 * 4) * 1u)))))) == 0)
      && (((*((uint *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x22f2cu + (uint32_t)(iVar2 * 0x1d) * 4u))))))) & 1) != 0)) &&
     (((*((uint *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x22f2cu + (uint32_t)(iVar2 * 0x1d) * 4u)))) + 4)))) & 1) != 0)) {
    puVar7 = 0x23dfcu;
    request_channel_mode_one_and_poll_bounded_84420(param_1);
  }
  if (((*((uint *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x22ef8u + (uint32_t)(iVar2 * 0x1d) * 4u))))))) & 7) == 1) {
    (*((uint *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x22ef4u + (uint32_t)(iVar2 * 0x1d) * 4u))))))) = *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x233c8u + (uint32_t)(iVar1 * 0x34) * 1u)))) | 1;
    (*((volatile undefined4 *)camry_host_ptr((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x23dfcu + (uint32_t)(-0xd60) * 1u))))))) = 0;
    (*((undefined4 *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x22f2cu + (uint32_t)(iVar2 * 0x1d) * 4u))))))) = 1;
    (*((undefined4 *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x22f2cu + (uint32_t)(iVar2 * 0x1d) * 4u)))) + 4)))) = 1;
    (*((undefined4 *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x22f2cu + (uint32_t)(iVar2 * 0x1d) * 4u)))) + 8)))) = 1;
    (*((uint *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x22f34u + (uint32_t)(iVar2 * 0x1d) * 4u)))) + 8)))) = (*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x233c0u + (uint32_t)(iVar1 * 0xd) * 4u)))) & 0xfffffffe;
    (*((undefined4 *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x22f34u + (uint32_t)(iVar2 * 0x1d) * 4u)))) + 8)))) = (*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x233c0u + (uint32_t)(iVar1 * 0xd) * 4u))));
    iVar8 = param_1 * 4;
    (*((undefined4 *)camry_host_ptr((uint32_t)((*((volatile int32_t *)camry_host_ptr((uint32_t)(puVar7 + -0xd98)))) + iVar8)))) = 1;
    (*((uint *)camry_host_ptr((uint32_t)((*((volatile int32_t *)camry_host_ptr((uint32_t)(puVar7 + -0xd9c)))) + iVar8)))) = (*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x233d8u + (uint32_t)(iVar1 * 0xd) * 4u)))) & 0xfffffffe;
    (*((undefined4 *)camry_host_ptr((uint32_t)(iVar8 + (*((volatile int32_t *)camry_host_ptr((uint32_t)(puVar7 + -0xd9c)))))))) = (*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x233d8u + (uint32_t)(iVar1 * 0xd) * 4u))));
    uVar6 = 0;
    do {
      iVar8 = (short)uVar6 * 0x60;
      (*((undefined4 *)camry_host_ptr((uint32_t)(*(int *)(((undefined *)camry_host_ptr((uint32_t)(0x22f48u + (uint32_t)(iVar11) * 1u)))) + iVar8)))) = 0x9fffffff;
      uVar9 = 0;
      (*((undefined4 *)camry_host_ptr((uint32_t)(*(int *)(((undefined *)camry_host_ptr((uint32_t)(0x22f48u + (uint32_t)(iVar11) * 1u)))) + iVar8 + 4)))) = 0;
      (*((undefined4 *)camry_host_ptr((uint32_t)(*(int *)(((undefined *)camry_host_ptr((uint32_t)(0x22f48u + (uint32_t)(iVar11) * 1u)))) + iVar8 + 8)))) = 0;
      do {
        iVar3 = uVar9 * 4;
        uVar9 = uVar9 + 1;
        (*((undefined4 *)camry_host_ptr((uint32_t)(iVar3 + *(int *)(((undefined *)camry_host_ptr((uint32_t)(0x22f48u + (uint32_t)(iVar11) * 1u)))) + iVar8 + 0xc)))) = 0;
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
         *(ushort *)(((undefined *)camry_host_ptr((uint32_t)(0x22ebcu + (uint32_t)(param_1 * 4) * 1u)))) & (*((ushort *)camry_host_ptr((uint32_t)(puVar7 + param_1 * 2 + -0xf68))));
    (*((undefined4 *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x22f14u + (uint32_t)(iVar2 * 0x1d) * 4u))))))) = 0;
    (*((undefined4 *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x22f20u + (uint32_t)(iVar2 * 0x1d) * 4u))))))) = 0;
    call_return_only_channel_hook_842ce(param_1);
    load_channel_control_and_poll_mode_zero_84852(param_1);
    if (((*((uint *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x22ef8u + (uint32_t)(iVar2 * 0x1d) * 4u))))))) & 7) == 0) {
      uVar10 = 0;
      (*((uint *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x22f34u + (uint32_t)(iVar2 * 0x1d) * 4u))))))) =
           (uint)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x233b8u + (uint32_t)(iVar1 * 0xd) * 4u)))) & 0xfffffffe;
      (*((uint *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x22f34u + (uint32_t)(iVar2 * 0x1d) * 4u)))) + 4)))) =
           (uint)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x233bcu + (uint32_t)(iVar1 * 0xd) * 4u)))) & 0xfffffffe;
      (*((volatile uint32_t *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x22f34u + (uint32_t)(iVar2 * 0x1d) * 4u)))))))) = ((uint32_t)((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x233b8u + (uint32_t)(iVar1 * 0xd) * 4u)))))));
      (*((volatile uint32_t *)camry_host_ptr((uint32_t)(((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x22f34u + (uint32_t)(iVar2 * 0x1d) * 4u)))) + 4))))) = ((uint32_t)((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x233bcu + (uint32_t)(iVar1 * 0xd) * 4u)))))));
    }
  }
  return uVar10;
}

undefined4 enter_channel_mode_zero_after_global_activation_84a5e(undefined1 param_1)

{
  uint32_t puVar1;
  undefined4 uVar2;
  
  puVar1 = 0x23dfcu;
  uVar2 = 2;
  if (((*((uint *)camry_host_ptr((uint32_t)(PTR_GSTS_00023044)))) & 0xf) == 1) {
    load_can_configuration_filters_and_enter_global_mode_zero_8483e();
  }
  if (((*((volatile uint *)camry_host_ptr((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x23dfcu + (uint32_t)(-0xdb8) * 1u))))))) & 0xf) == 0) {
    uVar2 = reset_transmit_storage_and_enter_channel_mode_zero_8488c(param_1);
  }
  return uVar2;
}

undefined4 disable_channel_fifos_and_enter_mode_one_84a92(uint param_1)

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
  request_channel_mode_one_and_poll_bounded_84420((uint)(byte)param_1);
  if (((*((uint *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x22ef8u + (uint32_t)(iVar1 * 0x1d) * 4u))))))) & 7) == 1) {
    uVar5 = 0;
    (*((undefined2 *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x22edcu + (uint32_t)(iVar1 * 0x1d) * 4u))))))) = 0;
    (*((undefined4 *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x22f14u + (uint32_t)(iVar1 * 0x1d) * 4u))))))) = 0;
    (*((undefined4 *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x22f20u + (uint32_t)(iVar1 * 0x1d) * 4u))))))) = 0;
  }
  return uVar5;
}

undefined4 cancel_pending_channel_transmits_before_mode_one_84b74(uint param_1)

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
    request_cancellation_for_configured_channel_transmits_8569a(param_1);
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
      (*((uint *)camry_host_ptr((uint32_t)((*((volatile int32_t *)camry_host_ptr((uint32_t)(puVar2 + -0xd9c)))) + iVar1)))) =
           (*((uint *)camry_host_ptr((uint32_t)(puVar2 + sVar4 * 0x34 + -0xa24)))) & 0xfffffffe;
      (*((uint *)camry_host_ptr((uint32_t)((*((volatile int32_t *)camry_host_ptr((uint32_t)(puVar2 + -0xd9c)))) + iVar1)))) =
           (*((uint *)camry_host_ptr((uint32_t)(puVar2 + sVar4 * 0x34 + -0xa24)))) & 0xfffffffc;
      (*((undefined4 *)camry_host_ptr((uint32_t)(iVar1 + (*((volatile int *)camry_host_ptr((uint32_t)(0x23dfcu + (uint32_t)(-0xd98) * 1u)))))))) = 1;
      return 2;
    }
  }
  uVar3 = disable_channel_fifos_and_enter_mode_one_84a92(param_1);
  return uVar3;
}

bool detect_can_configuration_or_filter_mismatch_84c2c(ushort param_1)

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
    uVar4 = *(ushort *)(((undefined *)camry_host_ptr((uint32_t)(0x22ec8u + (uint32_t)((short)param_1 * 6) * 1u))));
    uVar5 = (uint)*(ushort *)(((undefined *)camry_host_ptr((uint32_t)(0x22ec8u + (uint32_t)((short)param_1 * 6) * 1u))));
    while ((uVar5 < (ushort)(bVar3 + uVar4) && (bVar6 == false))) {
      (*((uint *)camry_host_ptr((uint32_t)(PTR_DAT_00023050)))) = uVar5 >> 4 & 0x1f;
      iVar1 = uVar5 * 0x10;
      iVar2 = (uVar5 & 0xf) * 0x10;
      if (((*((int *)camry_host_ptr((uint32_t)(PTR_DAT_000230a4 + iVar2)))) != *(int *)(((undefined *)camry_host_ptr((uint32_t)(0x230b8u + (uint32_t)(iVar1) * 1u))))) ||
         ((((*((int *)camry_host_ptr((uint32_t)(PTR_DAT_000230a4 + iVar2 + 4)))) !=
            *(int *)(((undefined *)camry_host_ptr((uint32_t)(0x22e68u + (uint32_t)((uint)(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x230c4u + (uint32_t)(iVar1) * 1u)))) * 4) * 1u)))) ||
           ((*((int *)camry_host_ptr((uint32_t)(PTR_DAT_000230a4 + iVar2 + 8)))) != *(int *)(((undefined *)camry_host_ptr((uint32_t)(0x230bcu + (uint32_t)(iVar1) * 1u)))))) ||
          ((*((int *)camry_host_ptr((uint32_t)(PTR_DAT_000230a4 + iVar2 + 0xc)))) != *(int *)(((undefined *)camry_host_ptr((uint32_t)(0x230c0u + (uint32_t)(iVar1) * 1u)))))))) {
        bVar6 = true;
      }
      uVar5 = uVar5 + 1 & 0xffff;
    }
    return bVar6;
  }
  return true;
}

undefined4 reset_channel_then_reload_timing_configuration_84de6(uint param_1)

{
  uint32_t puVar1;
  uint32_t puVar2;
  int iVar3;
  undefined4 uVar4;
  
  puVar1 = 0xfebeb800u;
  puVar2 = 0x23dfcu;
  param_1 = param_1 & 0xff;
  uVar4 = 2;
  iVar3 = disable_channel_fifos_and_enter_mode_one_84a92((uint)(byte)param_1);
  if (iVar3 == 0) {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(param_1 - 0x67da))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(param_1 - 0xf51)))));
    load_channel_timing_and_clear_status_registers_846f2(param_1);
    uVar4 = 0;
  }
  return uVar4;
}

undefined4 reset_global_status_and_reload_can_filters_84e16(void)

{
  uint32_t puVar1;
  undefined4 uVar2;
  
  puVar1 = 0x23dfcu;
  uVar2 = 2;
  (*((undefined4 *)camry_host_ptr((uint32_t)(PTR_DAT_0002309c)))) = 0;
  request_global_mode_one_and_poll_bounded_842fe();
  if (((*((volatile uint *)camry_host_ptr((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x23dfcu + (uint32_t)(-0xdb8) * 1u))))))) & 0xf) == 1) {
    load_global_can_configuration_with_fifos_disabled_84570();
    load_paged_can_acceptance_filter_rules_847a4();
    uVar2 = 0;
  }
  return uVar2;
}

undefined4 repair_global_configuration_then_reload_channel_84e44(byte param_1)

{
  byte bVar1;
  uint32_t puVar2;
  int iVar3;
  undefined4 uVar4;
  byte bVar5;
  
  puVar2 = 0x23dfcu;
  iVar3 = detect_can_configuration_or_filter_mismatch_84c2c((uint)(byte)param_1);
  if (iVar3 != 0) {
    bVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0xf58)))));
    for (bVar5 = 0; bVar5 < bVar1; bVar5 = bVar5 + 1) {
      if (bVar5 != param_1) {
        normalize_pending_channel_states_to_6b94_842a0(bVar5);
        invalidate_channel_integrity_latch_83cd6(bVar5);
      }
    }
    iVar3 = reset_global_status_and_reload_can_filters_84e16();
    if (iVar3 != 0) {
      return 2;
    }
  }
  uVar4 = reset_channel_then_reload_timing_configuration_84de6(param_1);
  return uVar4;
}

undefined4 activate_global_configuration_then_start_channel_84e8c(undefined1 param_1)

{
  uint32_t puVar1;
  undefined4 uVar2;
  
  puVar1 = 0x23dfcu;
  uVar2 = 2;
  if (((*((uint *)camry_host_ptr((uint32_t)(PTR_GSTS_00023044)))) & 0xf) == 1) {
    load_can_configuration_filters_and_enter_global_mode_zero_8483e();
  }
  if (((*((volatile uint *)camry_host_ptr((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x23dfcu + (uint32_t)(-0xdb8) * 1u))))))) & 0xf) == 0) {
    uVar2 = reset_transmit_storage_and_enter_channel_mode_zero_8488c(param_1);
  }
  return uVar2;
}

undefined4 enter_channel_mode_one_only_after_transmit_idle_84ec0(uint param_1)

{
  int iVar1;
  int iVar2;
  undefined4 uVar3;
  
  iVar2 = (param_1 & 0xff) * 4;
  uVar3 = 2;
  iVar1 = (int)(short)(param_1 & 0xff);
  if (((((*((ushort *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x22ee0u + (uint32_t)(iVar1 * 0x1d) * 4u))))))) &
        (*(ushort *)(((undefined *)camry_host_ptr((uint32_t)(0x22ebeu + (uint32_t)(iVar2) * 1u)))) | *(ushort *)(((undefined *)camry_host_ptr((uint32_t)(0x22ebcu + (uint32_t)(iVar2) * 1u)))))) == 0) &&
      (((*((uint *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x22f2cu + (uint32_t)(iVar1 * 0x1d) * 4u))))))) & 1) != 0)) &&
     (((*((uint *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x22f2cu + (uint32_t)(iVar1 * 0x1d) * 4u)))) + 4)))) & 1) != 0)) {
    uVar3 = disable_channel_fifos_and_enter_mode_one_84a92((uint)(byte)param_1);
  }
  return uVar3;
}

undefined4 reload_global_configuration_and_selected_channel_84f06(byte param_1)

{
  byte bVar1;
  int iVar2;
  undefined4 uVar3;
  byte bVar4;
  
  bVar1 = DAT_00022ea4;
  uVar3 = 2;
  for (bVar4 = 0; bVar4 < bVar1; bVar4 = bVar4 + 1) {
    if (bVar4 != param_1) {
      normalize_pending_channel_states_to_6b94_842a0(bVar4);
      invalidate_channel_integrity_latch_83cd6(bVar4);
    }
  }
  iVar2 = reset_global_status_and_reload_can_filters_84e16();
  if (iVar2 == 0) {
    uVar3 = reset_channel_then_reload_timing_configuration_84de6(param_1);
  }
  return uVar3;
}

void request_global_mode_one_and_clear_eight_fifo_controls_84f46(void)

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

void request_global_mode_five_and_poll_three_times_84f68(void)

{
  ushort uVar1;
  uint uVar2;
  
  uVar2 = 1;
  (*((volatile uint32_t *)camry_host_ptr((uint32_t)(PTR_GCTR_00023040)))) = ((uint32_t)(0x10005u));
  uVar1 = 0;
  do {
    if ((uVar2 & 0xf) == 5) {
      return;
    }
    uVar1 = uVar1 + 1;
    uVar2 = (*((volatile uint32_t *)camry_host_ptr((uint32_t)(PTR_GSTS_00023044))));
  } while (uVar1 < 3);
  return;
}

void quiesce_configured_channels_and_enter_global_mode_five_84f90(void)

{
  byte bVar1;
  undefined8 uVar2;
  ushort uVar3;
  
  uVar2 = 0x23dfc00000000;
  if (((((*((volatile uint32_t *)camry_host_ptr((uint32_t)(PTR_GSTS_00023044)))) >> 3 & 1) == 0) && (((*((volatile uint32_t *)camry_host_ptr((uint32_t)(PTR_GSTS_00023044)))) & 0xf) != 5)) &&
     (request_global_mode_one_and_poll_bounded_842fe(), ((*((volatile uint *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(((int)((ulonglong)uVar2 >> 0x20) + -0xdb8))))))))) & 0xf) == 1)) {
    request_global_mode_one_and_clear_eight_fifo_controls_84f46();
    bVar1 = (*((byte *)camry_host_ptr((uint32_t)((int)((ulonglong)uVar2 >> 0x20) + -0xf58))));
    for (uVar3 = 0; uVar3 < bVar1; uVar3 = uVar3 + 1 & 0xff) {
      if ((*((char *)camry_host_ptr((uint32_t)((short)uVar3 * 6 + (int)((ulonglong)uVar2 >> 0x20) + -0xf31)))) == '\0') {
        disable_channel_fifos_and_enter_mode_one_84a92(uVar3);
      }
    }
    request_global_mode_five_and_poll_three_times_84f68();
  }
  return;
}

void reload_acceptance_filters_when_count_differs_in_mode_one_84fea(void)

{
  if ((((*((uint *)camry_host_ptr((uint32_t)(PTR_GSTS_00023044)))) & 0xf) == 1) && ((*((int *)camry_host_ptr((uint32_t)(PTR_DAT_00023054)))) != DAT_00022e7c)) {
    load_paged_can_acceptance_filter_rules_847a4();
  }
  return;
}
