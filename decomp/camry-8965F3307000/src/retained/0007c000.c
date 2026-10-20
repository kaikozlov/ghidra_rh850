#include "common.h"

void publish_network_policy_bit_zero_boolean_7c010(ushort param_1)

{
  uint32_t puVar1;
  uint uVar2;
  int iVar3;
  ushort uVar4;
  uint32_t pcVar5;
  
  puVar1 = (0x23dfcu);
  param_1 = param_1 & 0xff;
  uVar4 = (ushort)DAT_0002183d;
  iVar3 = 0;
  if (((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe3de5u + (uint32_t)((short)param_1 * 6) * 1u)))) != '\x0f') &&
     (puVar1 = (0x23dfcu), uVar2 = dispatch_record_callback_slot_thirty_two_7f3a6(param_1), (uVar2 & 1) != 0)) {
    iVar3 = 0xff;
  }
  forward_network_ff_equality_boolean_7a0ba(uVar4 + param_1 & 0xff,iVar3);
  if (iVar3 == 0xff) {
    pcVar5 = (uint32_t)((uintptr_t)(*((volatile uint32_t *)(((undefined *)camry_host_ptr((uint32_t)(0x23dfcu + (uint32_t)(-0x25c8) * 1u)))))));
  }
  else {
    pcVar5 = (uint32_t)((uintptr_t)(*((volatile uint32_t *)(((undefined *)camry_host_ptr((uint32_t)(0x23dfcu + (uint32_t)(-0x25c4) * 1u)))))));
  }
  (*(int (*)())camry_indirect((uint32_t)(pcVar5)))(param_1);
  return;
}

void refresh_network_policy_and_boolean_indication_7c060(undefined1 param_1)

{
  uint uVar1;
  
  uVar1 = dispatch_record_callback_slot_thirty_two_7f3a6((uint)(byte)param_1);
  reconcile_and_apply_swapped_network_policy_bits_7bf10(param_1,(uVar1 >> 1 & 1) != 0);
  publish_network_policy_bit_zero_boolean_7c010(param_1);
  return;
}

void set_network_software_policy_0f_and_refresh_7c082(ushort param_1)

{
  ushort uVar1;
  
  param_1 = param_1 & 0xff;
  uVar1 = (ushort)DAT_0002183d;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe3de5u + (uint32_t)((short)param_1 * 6) * 1u)))) = 0xf;
  reconcile_and_apply_swapped_network_policy_bits_7bf10(param_1,0);
  publish_network_policy_bit_zero_boolean_7c010(param_1);
  forward_network_group_command_c0_and_notify_7a02c(uVar1 + param_1 & 0xff);
  return;
}

void set_network_software_policy_1e_and_refresh_7c0b4(ushort param_1)

{
  ushort uVar1;
  
  param_1 = param_1 & 0xff;
  uVar1 = (ushort)DAT_0002183d;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe3de5u + (uint32_t)((short)param_1 * 6) * 1u)))) = 0x1e;
  forward_network_group_command_c0_and_notify_7a050(uVar1 + param_1 & 0xff);
  reconcile_and_apply_swapped_network_policy_bits_7bf10(param_1,0);
  publish_network_policy_bit_zero_boolean_7c010(param_1);
  return;
}

void reset_requested_normal_network_policy_records_7c0e8(void)

{
  uint uVar1;
  uint uVar2;
  
  uVar2 = (uint)DAT_0002183c;
  for (uVar1 = 0; uVar1 < uVar2; uVar1 = uVar1 + 1 & 0xff) {
    (*((volatile uint16_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe3de0u + (uint32_t)(uVar1) * (uint32_t)sizeof(F33RequestedNormalNetworkPolicy)) + (uint32_t)(0) * (uint32_t)sizeof(F33RequestedNormalNetworkPolicy) + (uint32_t)offsetof(F33RequestedNormalNetworkPolicy, remaining_delay))))) = 0;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe3de0u + (uint32_t)(uVar1) * (uint32_t)sizeof(F33RequestedNormalNetworkPolicy)) + (uint32_t)(0) * (uint32_t)sizeof(F33RequestedNormalNetworkPolicy) + (uint32_t)offsetof(F33RequestedNormalNetworkPolicy, requested_policy))))) = '\x1e';
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe3de0u + (uint32_t)(uVar1) * (uint32_t)sizeof(F33RequestedNormalNetworkPolicy)) + (uint32_t)(0) * (uint32_t)sizeof(F33RequestedNormalNetworkPolicy) + (uint32_t)offsetof(F33RequestedNormalNetworkPolicy, reconciled_software_policy))))) = '\x0f';
  }
  return;
}

uint request_normal_network_policy_disable(uchar network)

{
  bool bVar1;
  uchar uVar2;
  uint uVar3;
  
  uVar3 = 0x12;
  uVar2 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe3de0u + (uint32_t)((uint)network - (uint)DAT_0002183d & 0xff) * (uint32_t)sizeof(F33RequestedNormalNetworkPolicy)) + (uint32_t)(0) * (uint32_t)sizeof(F33RequestedNormalNetworkPolicy) + (uint32_t)offsetof(F33RequestedNormalNetworkPolicy, requested_policy)))));
  bVar1 = uVar2 == '\x1e';
  if (bVar1) {
    uVar2 = '\x0f';
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe3de0u + (uint32_t)((uint)network - (uint)DAT_0002183d & 0xff) * (uint32_t)sizeof(F33RequestedNormalNetworkPolicy)) + (uint32_t)(0) * (uint32_t)sizeof(F33RequestedNormalNetworkPolicy) + (uint32_t)offsetof(F33RequestedNormalNetworkPolicy, requested_policy)))))
       = uVar2;
  if (bVar1) {
    uVar3 = 0;
  }
  return uVar3;
}

uint request_normal_network_policy_enable(uchar network)

{
  uint uVar1;
  ushort uVar2;
  int iVar3;
  uint uVar4;
  
  uVar1 = 0x13;
  uVar4 = (uint)network - (uint)DAT_0002183d & 0xff;
  uVar2 = (*((volatile uint16_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe3de0u + (uint32_t)(uVar4) * (uint32_t)sizeof(F33RequestedNormalNetworkPolicy)) + (uint32_t)(0) * (uint32_t)sizeof(F33RequestedNormalNetworkPolicy) + (uint32_t)offsetof(F33RequestedNormalNetworkPolicy, remaining_delay)))));
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe3de0u + (uint32_t)(uVar4) * (uint32_t)sizeof(F33RequestedNormalNetworkPolicy)) + (uint32_t)(0) * (uint32_t)sizeof(F33RequestedNormalNetworkPolicy) + (uint32_t)offsetof(F33RequestedNormalNetworkPolicy, requested_policy))))) != '\x1e') {
    iVar3 = scale_network_zero_stub_value_by_config_period_7bcbe((uint)(byte)network);
    if (iVar3 != 0) {
      iVar3 = iVar3 + 1;
    }
    uVar2 = (ushort)iVar3;
    uVar1 = 0;
  }
  (*((volatile uint16_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe3de0u + (uint32_t)(uVar4) * (uint32_t)sizeof(F33RequestedNormalNetworkPolicy)) + (uint32_t)(0) * (uint32_t)sizeof(F33RequestedNormalNetworkPolicy) + (uint32_t)offsetof(F33RequestedNormalNetworkPolicy, remaining_delay))))) = uVar2;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe3de0u + (uint32_t)(uVar4) * (uint32_t)sizeof(F33RequestedNormalNetworkPolicy)) + (uint32_t)(0) * (uint32_t)sizeof(F33RequestedNormalNetworkPolicy) + (uint32_t)offsetof(F33RequestedNormalNetworkPolicy, requested_policy))))) = '\x1e';
  return uVar1;
}

uint get_swapped_network_policy_without_configured_bits_7c178(char param_1)

{
  uint32_t puVar1;
  uint uVar2;
  uint uVar3;
  uint uVar4;
  
  puVar1 = 0x23dfcu;
  uVar2 = dispatch_record_callback_slot_thirty_two_7f3a6((uint)(byte)param_1);
  uVar3 = get_bounded_network_configuration_flags_7bcde((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x25bf))))) + param_1);
  uVar4 = 0;
  if ((uVar3 & 1) == 0) {
    if ((uVar2 & 1) == 0) {
      uVar4 = 0;
    }
    else {
      uVar4 = 2;
    }
  }
  if (((uVar3 >> 1 & 1) == 0) && ((uVar2 >> 1 & 1) != 0)) {
    uVar4 = uVar4 | 1;
  }
  return uVar4;
}

uint get_swapped_network_policy_low_two_bits_7c1b4(undefined1 param_1)

{
  uint uVar1;
  uint uVar2;
  
  uVar1 = dispatch_record_callback_slot_thirty_two_7f3a6(param_1);
  if ((uVar1 & 1) == 0) {
    uVar2 = 0;
  }
  else {
    uVar2 = 2;
  }
  if ((uVar1 >> 1 & 1) != 0) {
    uVar2 = uVar2 | 1;
  }
  return uVar2;
}

uint reconcile_requested_normal_network_policy(uchar param_1,uchar clear_request)

{
  char cVar1;
  uint32_t puVar2;
  uint uVar3;
  undefined4 uVar4;
  uint uVar5;
  uint uVar6;
  uint uVar7;
  char cVar8;
  
  puVar2 = 0xfebeb800u;
  uVar6 = (uint)param_1;
  uVar7 = DAT_0002183d + uVar6 & 0xff;
  uVar5 = 0;
  uVar3 = get_bounded_network_configuration_flags_7bcde(uVar7);
  if (uVar3 == 0) {
    return 0;
  }
  cVar8 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(uVar6 * 4 + -0x7a1f)))));
  cVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(uVar6 * 4 + -0x7a20)))));
  if (cVar8 == '\x0f') {
    uVar5 = (uint)(cVar1 == '\x0f');
    if (cVar1 != '\x0f') goto LAB_0007c2cc;
LAB_0007c290:
    cVar8 = '\x1e';
    uVar4 = get_swapped_network_policy_without_configured_bits_7c178(uVar6);
    if ((uVar3 & 3) == 3) {
      map_channel_mode_to_c0_80_40_callback_83204(uVar7,3);
    }
    if ((uVar3 >> 2 & 1) != 0) {
      mark_bounded_network_group_request_one_7bcf4(uVar7);
      cVar8 = '\x1e';
      goto LAB_0007c2be;
    }
  }
  else {
    uVar4 = 0;
    if (cVar8 == '\x1e') {
      uVar5 = 1;
      if (cVar1 == '\x0f') {
        uVar4 = get_swapped_network_policy_without_configured_bits_7c178(uVar6);
      }
      else {
        map_channel_mode_to_c0_80_40_callback_83204(uVar7, (char)(uVar3 & 3));
        if ((*((short *)camry_host_ptr((uint32_t)(puVar2 + uVar6 * 4 + -0x7a1e)))) == 0) {
          cVar8 = '\x0f';
          uVar4 = get_swapped_network_policy_low_two_bits_7c1b4(uVar6);
          if ((uVar3 & 2) != 0) {
            clear_request = '\x01';
          }
        }
        else {
          cVar8 = '-';
        }
        if ((uVar3 >> 2 & 1) != 0) {
          mark_bounded_network_group_request_two_and_schedule_pdus_7bd0a(uVar7);
        }
LAB_0007c2be:
        if (uVar5 != 1) goto LAB_0007c2cc;
      }
    }
    else {
      if (cVar8 != '-') {
        if (cVar1 == '\x0f') goto LAB_0007c2cc;
        cVar8 = '\x0f';
        goto LAB_0007c2be;
      }
      uVar5 = 1;
      if (cVar1 != '\x1e') {
        (*((undefined2 *)camry_host_ptr((uint32_t)(puVar2 + uVar6 * 4 + -0x7a1e)))) = 0;
        goto LAB_0007c290;
      }
      if ((*((short *)camry_host_ptr((uint32_t)(puVar2 + uVar6 * 4 + -0x7a1e)))) == 0) {
        cVar8 = '\x0f';
        uVar4 = get_swapped_network_policy_low_two_bits_7c1b4(uVar6);
        clear_request = '\x01';
      }
    }
  }
  apply_offset_network_policy_with_optional_zero_reset_7bed0(uVar6,uVar4,clear_request);
LAB_0007c2cc:
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(uVar6 * 4 + -0x7a1f))))) = cVar8;
  return uVar5;
}

void decrement_requested_network_policy_delay_if_nonzero_7c2d6(uint param_1)

{
  ushort uVar1;
  
  uVar1 = (*((volatile uint16_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe3de0u + (uint32_t)(param_1 & 0xff) * (uint32_t)sizeof(F33RequestedNormalNetworkPolicy)) + (uint32_t)(0) * (uint32_t)sizeof(F33RequestedNormalNetworkPolicy) + (uint32_t)offsetof(F33RequestedNormalNetworkPolicy, remaining_delay)))));
  if (uVar1 != 0) {
    uVar1 = uVar1 - 1;
  }
  (*((volatile uint16_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe3de0u + (uint32_t)(param_1 & 0xff) * (uint32_t)sizeof(F33RequestedNormalNetworkPolicy)) + (uint32_t)(0) * (uint32_t)sizeof(F33RequestedNormalNetworkPolicy) + (uint32_t)offsetof(F33RequestedNormalNetworkPolicy, remaining_delay))))) = uVar1;
  return;
}

void initialize_normal_network_channel_state_and_hooks_7c2ee(void)

{
  ushort uVar1;
  uint32_t puVar2;
  ushort uVar3;
  undefined1 uVar4;
  int iVar5;
  
  puVar2 = 0x23dfcu;
  uVar4 = 0x2d;
  if (((int8_t)DAT_0002183e) == -1) {
    uVar4 = 0x1e;
  }
  uVar3 = (ushort)DAT_0002183c;
  for (uVar1 = 0; uVar1 < uVar3; uVar1 = uVar1 + 1 & 0xff) {
    iVar5 = (short)uVar1 * 6;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe3de9u + (uint32_t)(iVar5) * 1u)))) = 0;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe3de4u + (uint32_t)(iVar5) * 1u)))) = 0x1e;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe3de5u + (uint32_t)(iVar5) * 1u)))) = 0x1e;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe3de6u + (uint32_t)(iVar5) * 1u)))) = uVar4;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe3de7u + (uint32_t)(iVar5) * 1u)))) = 0;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe3de8u + (uint32_t)(iVar5) * 1u)))) = 0xff;
  }
  DAT_febe4fb0 = 0x2d;
  (*(int (*)())camry_indirect((uint32_t)(PTR_FUN_0002181c)))();
  (*(int (*)())camry_indirect((uint32_t)(((((code *)(uintptr_t)((uint32_t)((uintptr_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(puVar2 + -0x25d4))))))))))))();
  (*(int (*)())camry_indirect((uint32_t)(((((code *)(uintptr_t)((uint32_t)((uintptr_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(puVar2 + -0x25d0))))))))))))();
  return;
}

undefined4 advance_normal_channel_setup_and_publish_fault_class_7c352(void)

{
  char cVar1;
  undefined1 uVar2;
  undefined *puVar3;
  undefined *puVar4;
  uint32_t puVar5;
  undefined4 uVar6;
  int iVar7;
  ushort uVar8;
  undefined4 uVar9;
  ushort uVar10;
  ushort uVar11;
  
  puVar3 = ((undefined *)camry_host_ptr(0xfebeb800u));
  puVar5 = 0x23dfcu;
  uVar8 = (ushort)DAT_0002183c;
  uVar9 = 0;
  uVar11 = 0;
  do {
    if (uVar8 <= uVar11) {
      return uVar9;
    }
    cVar1 = puVar3[(short)uVar11 * 6 + -0x7a1a];
    if (cVar1 != 'K') {
      puVar4 = puVar3;
      if (cVar1 == '\x1e') {
        uVar6 = 0;
LAB_0007c39e:
        iVar7 = request_network_setup_and_capture_nonbusy_fault_cause_7c96c(uVar11,uVar6);
        if (iVar7 != 2) {
          uVar10 = (byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x25bf))))) + uVar11 & 0xff;
          set_record_492c_boolean_token_7ead0(uVar10,1);
          puVar3[(short)uVar11 * 6 + -0x7a1a] = 0x4b;
          iVar7 = get_single_selected_network_cause_08_10_or_40_7cd7c(uVar11);
          if (iVar7 == 0x40) {
            puVar3[(short)uVar11 * 6 + -0x7a19] = 1;
            puVar3[(short)uVar11 * 6 + -0x7a18] = 0xfe;
            call_stub_83594_for_matching_channels_8132e(uVar11);
            call_stub_83596_for_matching_channels_812be(uVar11);
            uVar6 = 1;
          }
          else if (iVar7 == 8) {
            puVar3[(short)uVar11 * 6 + -0x7a19] = 2;
            puVar3[(short)uVar11 * 6 + -0x7a18] = 0xfd;
            call_stub_83594_for_matching_channels_8132e(uVar11);
            call_stub_83596_for_matching_channels_812be(uVar11);
            uVar6 = 2;
          }
          else if (iVar7 == 0x10) {
            uVar6 = 3;
            puVar3[(short)uVar11 * 6 + -0x7a19] = 3;
            puVar3[(short)uVar11 * 6 + -0x7a18] = 0xfc;
          }
          else {
            puVar3[(short)uVar11 * 6 + -0x7a19] = 0;
            puVar3[(short)uVar11 * 6 + -0x7a18] = 0xff;
            puVar3 = puVar4;
            if (iVar7 != 0) goto LAB_0007c42e;
            uVar6 = 0;
          }
          ((void)(uVar10), (void)(uVar6), return_only_stub_83280());
          puVar3 = puVar4;
          goto LAB_0007c42e;
        }
      }
      else {
        if (cVar1 == '-') {
          uVar6 = 1;
          goto LAB_0007c39e;
        }
        uVar2 = 0x2d;
        if (((int8_t)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x25be)))))) == -1) {
          uVar2 = 0x1e;
        }
        puVar3[(short)uVar11 * 6 + -0x7a1a] = uVar2;
      }
      uVar9 = 1;
      puVar3 = puVar4;
    }
LAB_0007c42e:
    uVar11 = uVar11 + 1 & 0xff;
  } while( true );
}

void advance_aggregate_normal_channel_setup_state_7c43c(void)

{
  uint32_t puVar1;
  int iVar2;
  char cVar3;
  
  puVar1 = 0xfebeb800u;
  if (DAT_febe4fb0 == 'K') {
    return;
  }
  cVar3 = DAT_febe4fb0;
  if (DAT_febe4fb0 == '\x1e') {
LAB_0007c45a:
    puVar1 = 0xfebeb800u;
    iVar2 = is_state_3df4_equal_0f_83172();
    if (iVar2 == 0) goto LAB_0007c470;
    cVar3 = cVar3 + '\x0f';
  }
  else if (DAT_febe4fb0 != '-') {
    cVar3 = '\x1e';
    goto LAB_0007c45a;
  }
  iVar2 = advance_normal_channel_setup_and_publish_fault_class_7c352();
  if (iVar2 == 0) {
    cVar3 = 'K';
  }
LAB_0007c470:
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6850))))) = cVar3;
  return;
}

void walk_all_normal_channels_through_three_notification_hooks_7c478(void)

{
  byte bVar1;
  byte bVar2;
  
  bVar1 = DAT_0002183c;
  for (bVar2 = 0; bVar2 < bVar1; bVar2 = bVar2 + 1) {
    call_stub_83590_for_matching_channels_81290(bVar2);
    call_stub_83594_for_matching_channels_8132e(bVar2);
    call_stub_83596_for_matching_channels_812be(bVar2);
  }
  return;
}

void walk_all_normal_channels_through_two_notification_hooks_7c4a2(void)

{
  byte bVar1;
  byte bVar2;
  
  bVar1 = DAT_0002183c;
  for (bVar2 = 0; bVar2 < bVar1; bVar2 = bVar2 + 1) {
    call_stub_83594_for_matching_channels_8132e(bVar2);
    call_stub_83596_for_matching_channels_812be(bVar2);
  }
  return;
}

void reset_normal_network_policy_bytes_and_run_hooks_7c4c6(void)

{
  ushort uVar1;
  uint32_t puVar2;
  ushort uVar3;
  int iVar4;
  
  puVar2 = 0x23dfcu;
  uVar3 = (ushort)DAT_0002183c;
  for (uVar1 = 0; uVar1 < uVar3; uVar1 = uVar1 + 1 & 0xff) {
    iVar4 = (short)uVar1 * 6;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe3de9u + (uint32_t)(iVar4) * 1u)))) = 0;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe3de4u + (uint32_t)(iVar4) * 1u)))) = 0x1e;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe3de5u + (uint32_t)(iVar4) * 1u)))) = 0x1e;
  }
  (*(int (*)())camry_indirect((uint32_t)(PTR_FUN_0002181c)))();
  (*(int (*)())camry_indirect((uint32_t)(((((code *)(uintptr_t)((uint32_t)((uintptr_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(puVar2 + -0x25d4))))))))))))();
  (*(int (*)())camry_indirect((uint32_t)(((((code *)(uintptr_t)((uint32_t)((uintptr_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(puVar2 + -0x25d0))))))))))))();
  return;
}

void restart_channel_setup_preserving_valid_zero_fault_classes_7c50a(void)

{
  char cVar1;
  ushort uVar2;
  ushort uVar3;
  undefined1 uVar4;
  int iVar5;
  
  cVar1 = DAT_0002183e;
  uVar3 = (ushort)DAT_0002183c;
  if (((DAT_febe4fb0 == '\x1e') || (DAT_febe4fb0 == '-')) || (DAT_febe4fb0 == 'K')) {
    for (uVar2 = 0; uVar2 < uVar3; uVar2 = uVar2 + 1 & 0xff) {
      iVar5 = (short)uVar2 * 6;
      if (((int8_t)cVar1) == -1) {
LAB_0007c550:
        uVar4 = 0x1e;
      }
      else {
        uVar4 = 0x2d;
        if ((((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe3de8u + (uint32_t)(iVar5) * 1u)))) ^ (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe3de7u + (uint32_t)(iVar5) * 1u))))) == 0xff) &&
           ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe3de7u + (uint32_t)(iVar5) * 1u)))) == 0)) goto LAB_0007c550;
      }
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe3de6u + (uint32_t)(iVar5) * 1u)))) = uVar4;
    }
  }
  else {
    uVar4 = 0x2d;
    if (((int8_t)DAT_0002183e) == -1) {
      uVar4 = 0x1e;
    }
    for (uVar2 = 0; uVar2 < uVar3; uVar2 = uVar2 + 1 & 0xff) {
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe3de6u + (uint32_t)((short)uVar2 * 6) * 1u)))) = uVar4;
    }
  }
  DAT_febe4fb0 = 0x2d;
  return;
}

int check_normal_network_transition_or_mode_activity_7c58c(void)

{
  uchar network;
  byte bVar1;
  char cVar2;
  int iVar3;
  int iVar4;
  uint uVar5;
  int iVar6;
  byte bVar7;
  uchar uStack_1d;
  
  cVar2 = DAT_0002183d;
  bVar1 = DAT_0002183c;
  iVar6 = 0;
  if (DAT_febe4fb0 == '-') {
LAB_0007c59c:
    iVar6 = 0xff;
  }
  else {
    for (bVar7 = 0; bVar7 < bVar1; bVar7 = bVar7 + 1) {
      network = cVar2 + bVar7;
      iVar3 = get_record_byte_mask_or_zero_7eb4c(network);
      iVar4 = get_record_u16_mask_low_byte_or_zero_7eb62(network);
      if ((iVar3 != iVar4) && (iVar6 = dispatch_record_callback_slot_twelve_21b70_7f366(bVar7), iVar6 != 0)) {
        return iVar6;
      }
      uVar5 = get_selected_network_software_mode(network,&uStack_1d);
      if (((uVar5 == 0) && (uStack_1d != '\0')) || (iVar3 = test_matching_channel_stub_returns_zero_7f6a4(bVar7), iVar3 == 1))
      goto LAB_0007c59c;
    }
  }
  return iVar6;
}

void return_only_stub_7c600(void)

{
  return;
}

void return_only_stub_7c602(void)

{
  return;
}

undefined1 return_low_byte_second_argument_7c604(undefined4 param_1,undefined1 param_2)

{
  return param_2;
}

void return_only_stub_7c60a(void)

{
  return;
}

void return_only_stub_7c60c(void)

{
  return;
}

uint retain_network_fault_bits_3a7_7c60e(uint param_1)

{
  uint uVar1;
  
  uVar1 = (uint)((param_1 & 1) != 0);
  if ((param_1 >> 1 & 1) != 0) {
    uVar1 = uVar1 | 2;
  }
  if ((param_1 >> 2 & 1) != 0) {
    uVar1 = uVar1 | 4;
  }
  if ((param_1 >> 5 & 1) != 0) {
    uVar1 = uVar1 | 0x20;
  }
  if ((param_1 >> 7 & 1) != 0) {
    uVar1 = uVar1 | 0x80;
  }
  if ((param_1 >> 8 & 1) != 0) {
    uVar1 = uVar1 | 0x100;
  }
  if ((param_1 >> 9 & 1) != 0) {
    uVar1 = uVar1 | 0x200;
  }
  return uVar1;
}

undefined4 get_normal_network_fault_mask_with_complement_validation_7c652(short param_1,ushort *param_2)

{
  byte bVar1;
  ushort uVar2;
  ushort uVar3;
  int iVar4;
  
  uVar3 = param_1 - (ushort)DAT_0002183d & 0xff;
  if (DAT_0002183c <= uVar3) {
    return 1;
  }
  iVar4 = (short)uVar3 * 6;
  uVar3 = 0;
  bVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe3de7u + (uint32_t)(iVar4) * 1u))));
  if (((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe3de8u + (uint32_t)(iVar4) * 1u)))) ^ bVar1) == 0xff) {
    if (bVar1 == 0) goto LAB_0007c6a2;
    if (bVar1 != 1) {
      if (bVar1 == 2) {
        uVar3 = 8;
      }
      else {
        uVar3 = 0;
        if (bVar1 == 3) {
          uVar3 = 0x10;
        }
      }
      goto LAB_0007c6a2;
    }
  }
  uVar3 = 0x40;
LAB_0007c6a2:
  if (((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe3de6u + (uint32_t)(iVar4) * 1u)))) == 'K') && (iVar4 = compose_selected_network_fault_mask_and_class_bits_7cfe2((uint)(iVar4 / 6)), iVar4 != 0)) {
    uVar2 = retain_network_fault_bits_3a7_7c60e(iVar4);
    uVar3 = uVar3 | uVar2;
  }
  *param_2 = uVar3;
  return 0;
}

uint map_first_encoded_pdu_table_to_global_network_7c6c4(undefined2 param_1)

{
  uint32_t puVar1;
  uint uVar2;
  uint uVar3;
  uint uVar4;
  
  puVar1 = 0x23dfcu;
  uVar3 = (uint)DAT_0002183c;
  uVar4 = 0xff;
  uVar2 = lookup_base_bank_controller_byte_or_ff_8144e(param_1);
  if (uVar2 < uVar3) {
    uVar4 = (byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x25bf))))) + uVar2 & 0xff;
  }
  return uVar4;
}

uint map_second_encoded_pdu_table_to_global_network_7c6e8(undefined2 param_1)

{
  uint32_t puVar1;
  uint uVar2;
  
  puVar1 = 0x23dfcu;
  uVar2 = lookup_extended_bank_record_byte_or_ff_813e4(param_1);
  if (uVar2 < (byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x25c0)))))) {
    uVar2 = (byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x25bf))))) + uVar2 & 0xff;
  }
  else {
    uVar2 = 0xff;
  }
  return uVar2;
}

void return_only_stub_7c70e(void)

{
  return;
}

void initialize_selected_network_modes_and_recovery_7c710(void)

{
  uint uVar1;
  uint32_t puVar2;
  uint uVar3;
  
  puVar2 = 0x23dfcu;
  uVar3 = (uint)DAT_00021ba8;
  for (uVar1 = 0; uVar1 < uVar3; uVar1 = uVar1 + 1 & 0xff) {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe4924u + (uint32_t)(uVar1) * (uint32_t)sizeof(F33SelectedNetworkModeState)) + (uint32_t)(0) * (uint32_t)sizeof(F33SelectedNetworkModeState) + (uint32_t)offsetof(F33SelectedNetworkModeState, remaining_delay))))) = '\0';
    (*((volatile uint16_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe4924u + (uint32_t)(uVar1) * (uint32_t)sizeof(F33SelectedNetworkModeState)) + (uint32_t)(0) * (uint32_t)sizeof(F33SelectedNetworkModeState) + (uint32_t)offsetof(F33SelectedNetworkModeState, mode_state))))) = 0xff;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe4924u + (uint32_t)(uVar1) * (uint32_t)sizeof(F33SelectedNetworkModeState)) + (uint32_t)(0) * (uint32_t)sizeof(F33SelectedNetworkModeState) + (uint32_t)offsetof(F33SelectedNetworkModeState, uninterpreted))))) = '\0';
  }
  reset_selected_network_recovery_records_7cd12();
  (*(int (*)())camry_indirect((uint32_t)(((((code *)(uintptr_t)((uint32_t)((uintptr_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(puVar2 + -0x2260))))))))))))();
  return;
}

void set_selected_network_modes_07f8_and_clear_fault_causes_7c748(void)

{
  uint uVar1;
  uint32_t puVar2;
  uint uVar3;
  
  puVar2 = 0x23dfcu;
  uVar3 = (uint)DAT_00021ba8;
  for (uVar1 = 0; uVar1 < uVar3; uVar1 = uVar1 + 1 & 0xff) {
    (*((volatile uint16_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe4924u + (uint32_t)(uVar1) * (uint32_t)sizeof(F33SelectedNetworkModeState)) + (uint32_t)(0) * (uint32_t)sizeof(F33SelectedNetworkModeState) + (uint32_t)offsetof(F33SelectedNetworkModeState, mode_state))))) = 0x7f8;
  }
  clear_selected_network_recovery_causes_and_fault_classes_7cd3e();
  (*(int (*)())camry_indirect((uint32_t)(((((code *)(uintptr_t)((uint32_t)((uintptr_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(puVar2 + -0x2260))))))))))))();
  return;
}

void decrement_and_clamp_selected_network_mode_delay_7c77a(uint param_1)

{
  byte bVar1;
  byte bVar2;
  
  bVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe4924u + (uint32_t)(param_1 & 0xff) * (uint32_t)sizeof(F33SelectedNetworkModeState)) + (uint32_t)(0) * (uint32_t)sizeof(F33SelectedNetworkModeState) + (uint32_t)offsetof(F33SelectedNetworkModeState, remaining_delay)))));
  bVar2 = bVar1;
  if ((bVar1 != 0) && (bVar2 = DAT_00021bab, (byte)(bVar1 - 1) <= DAT_00021bab)) {
    bVar2 = bVar1 - 1;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe4924u + (uint32_t)(param_1 & 0xff) * (uint32_t)sizeof(F33SelectedNetworkModeState)) + (uint32_t)(0) * (uint32_t)sizeof(F33SelectedNetworkModeState) + (uint32_t)offsetof(F33SelectedNetworkModeState, remaining_delay))))) = bVar2;
  return;
}

void advance_selected_mode_zero_transition_after_delay_7c79e(uint param_1)

{
  uchar uVar1;
  ushort uVar2;
  uint32_t puVar3;
  int iVar4;
  
  puVar3 = 0x23dfcu;
  param_1 = param_1 & 0xff;
  uVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe4924u + (uint32_t)(param_1) * (uint32_t)sizeof(F33SelectedNetworkModeState)) + (uint32_t)(0) * (uint32_t)sizeof(F33SelectedNetworkModeState) + (uint32_t)offsetof(F33SelectedNetworkModeState, remaining_delay)))));
  iVar4 = test_cached_controller_matching_channel_status_7f56a((uint)(byte)param_1);
  if (iVar4 != 0) {
    if (uVar1 != '\0') {
      return;
    }
    set_controller_cache_6b94_and_clear_channels_7fafa(param_1);
  }
  check_controller_request_mode_and_release_7f4fe(param_1,2);
  uVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(param_1 - 0x2252)))));
  if (uVar1 == '\0') {
    dispatch_record_three_way_operation_7eaf2((byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x2253))))) + param_1 & 0xff,0);
    uVar2 = 0xff;
  }
  else {
    uVar2 = 0x4fb;
  }
  (*((volatile uint16_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe4924u + (uint32_t)(param_1) * (uint32_t)sizeof(F33SelectedNetworkModeState)) + (uint32_t)(0) * (uint32_t)sizeof(F33SelectedNetworkModeState) + (uint32_t)offsetof(F33SelectedNetworkModeState, mode_state))))) = uVar2;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe4924u + (uint32_t)(param_1) * (uint32_t)sizeof(F33SelectedNetworkModeState)) + (uint32_t)(0) * (uint32_t)sizeof(F33SelectedNetworkModeState) + (uint32_t)offsetof(F33SelectedNetworkModeState, remaining_delay))))) = uVar1;
  return;
}

void finish_selected_mode_zero_when_delay_expires_7c7fc(uint param_1)

{
  param_1 = param_1 & 0xff;
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe4924u + (uint32_t)(param_1) * (uint32_t)sizeof(F33SelectedNetworkModeState)) + (uint32_t)(0) * (uint32_t)sizeof(F33SelectedNetworkModeState) + (uint32_t)offsetof(F33SelectedNetworkModeState, remaining_delay))))) == '\0') {
    dispatch_record_three_way_operation_7eaf2(DAT_00021ba9 + param_1 & 0xff,0);
    (*((volatile uint16_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe4924u + (uint32_t)(param_1) * (uint32_t)sizeof(F33SelectedNetworkModeState)) + (uint32_t)(0) * (uint32_t)sizeof(F33SelectedNetworkModeState) + (uint32_t)offsetof(F33SelectedNetworkModeState, mode_state))))) = 0xff;
  }
  return;
}

void request_controller_run_and_publish_selected_mode_one_7c830(uchar param_1)

{
  char cVar1;
  
  cVar1 = DAT_00021ba9 + param_1;
  request_logical_controller_run_stop(param_1,'\x02');
  dispatch_record_three_way_operation_7eaf2(cVar1,1);
  call_21840_with_two_bytes_832da(cVar1,1);
  return;
}

void finish_selected_mode_one_when_delay_expires_7c858(uint param_1)

{
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe4924u + (uint32_t)(param_1 & 0xff) * (uint32_t)sizeof(F33SelectedNetworkModeState)) + (uint32_t)(0) * (uint32_t)sizeof(F33SelectedNetworkModeState) + (uint32_t)offsetof(F33SelectedNetworkModeState, remaining_delay))))) == '\0') {
    request_controller_run_and_publish_selected_mode_one_7c830((uint)(byte)param_1);
    (*((volatile uint16_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe4924u + (uint32_t)(param_1 & 0xff) * (uint32_t)sizeof(F33SelectedNetworkModeState)) + (uint32_t)(0) * (uint32_t)sizeof(F33SelectedNetworkModeState) + (uint32_t)offsetof(F33SelectedNetworkModeState, mode_state))))) = 0x1fe;
  }
  return;
}

void publish_selected_mode_two_and_controller_policy_three_7c880(char param_1)

{
  char cVar1;
  
  cVar1 = DAT_00021ba9 + param_1;
  set_controller_request_byte_from_mode_80f6c(param_1,3);
  dispatch_record_three_way_operation_7eaf2(cVar1,2);
  call_21840_with_two_bytes_832da(cVar1,2);
  return;
}

void finish_selected_mode_two_when_delay_expires_7c8a8(byte param_1)

{
  uint32_t puVar1;
  uint32_t puVar2;
  uint uVar3;
  
  puVar1 = 0xfebeb800u;
  puVar2 = 0x23dfcu;
  uVar3 = (uint)param_1;
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe4924u + (uint32_t)(uVar3) * (uint32_t)sizeof(F33SelectedNetworkModeState)) + (uint32_t)(0) * (uint32_t)sizeof(F33SelectedNetworkModeState) + (uint32_t)offsetof(F33SelectedNetworkModeState, remaining_delay))))) == '\0') {
    request_logical_controller_run_stop(param_1,'\x02');
    if ((*((short *)camry_host_ptr((uint32_t)(puVar1 + uVar3 * 8 + -0x6ee4)))) == 0xff) {
      publish_selected_mode_two_and_controller_policy_three_7c880(uVar3);
    }
    else {
      dispatch_record_three_way_operation_7eaf2((byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x2253))))) + uVar3 & 0xff,1);
    }
    (*((volatile uint16_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe4924u + (uint32_t)(uVar3) * (uint32_t)sizeof(F33SelectedNetworkModeState)) + (uint32_t)(0) * (uint32_t)sizeof(F33SelectedNetworkModeState) + (uint32_t)offsetof(F33SelectedNetworkModeState, mode_state))))) = 0x2fd;
  }
  return;
}

void dispatch_selected_network_pending_mode_transition_7c8fc(uint param_1)

{
  ushort uVar1;
  
  uVar1 = (*((volatile uint16_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe4924u + (uint32_t)(param_1 & 0xff) * (uint32_t)sizeof(F33SelectedNetworkModeState)) + (uint32_t)(0) * (uint32_t)sizeof(F33SelectedNetworkModeState) + (uint32_t)offsetof(F33SelectedNetworkModeState, mode_state)))));
  if (uVar1 == 0x3fc) {
    advance_selected_mode_zero_transition_after_delay_7c79e((uint)(byte)param_1);
  }
  else if (uVar1 == 0x4fb) {
    finish_selected_mode_zero_when_delay_expires_7c7fc((uint)(byte)param_1);
  }
  else if (uVar1 == 0x5fa) {
    finish_selected_mode_one_when_delay_expires_7c858((uint)(byte)param_1);
  }
  else if (uVar1 == 0x8f7) {
    finish_selected_mode_two_when_delay_expires_7c8a8((uint)(byte)param_1);
  }
  return;
}

void service_selected_network_recovery_and_mode_delays_7c93e(void)

{
  byte bVar1;
  undefined8 uVar2;
  byte bVar3;
  
  uVar2 = 0x23dfc00000000;
  service_all_selected_network_fault_recovery_records_7cf44();
  bVar1 = (*((byte *)camry_host_ptr((uint32_t)((int)((ulonglong)uVar2 >> 0x20) + -0x2254))));
  for (bVar3 = 0; bVar3 < bVar1; bVar3 = bVar3 + 1) {
    decrement_and_clamp_selected_network_mode_delay_7c77a(bVar3);
    dispatch_selected_network_pending_mode_transition_7c8fc(bVar3);
  }
  (*(int (*)())camry_indirect((uint32_t)(((((code *)(uintptr_t)((uint32_t)((uintptr_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)((int)((ulonglong)uVar2 >> 0x20) + -0x225c)))))))))))))();
  return;
}

int request_network_setup_and_capture_nonbusy_fault_cause_7c96c(undefined1 param_1,undefined1 param_2)

{
  int iVar1;
  
  iVar1 = advance_controller_cache_from_6d92_7fa3a(param_1,param_2);
  if (iVar1 != 2) {
    capture_selected_network_fault_cause_bits_58_7cd60(param_1);
  }
  return iVar1;
}

undefined4 request_selected_network_mode_zero_7c98c(char param_1)

{
  byte logical_controller;
  uint32_t puVar1;
  int iVar2;
  ushort uVar3;
  undefined4 uVar4;
  uchar uVar5;
  uint uVar6;
  
  puVar1 = 0x23dfcu;
  uVar4 = 0;
  logical_controller = param_1 - DAT_00021ba9;
  uVar6 = (uint)logical_controller;
  uVar3 = (*((volatile uint16_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe4924u + (uint32_t)(uVar6) * (uint32_t)sizeof(F33SelectedNetworkModeState)) + (uint32_t)(0) * (uint32_t)sizeof(F33SelectedNetworkModeState) + (uint32_t)offsetof(F33SelectedNetworkModeState, mode_state)))));
  uVar5 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe4924u + (uint32_t)(uVar6) * (uint32_t)sizeof(F33SelectedNetworkModeState)) + (uint32_t)(0) * (uint32_t)sizeof(F33SelectedNetworkModeState) + (uint32_t)offsetof(F33SelectedNetworkModeState, remaining_delay)))));
  if (uVar3 == 0xff) goto LAB_0007ca32;
  if ((uVar3 == 0x1fe) || (uVar3 == 0x2fd)) {
    call_21840_with_two_bytes_832da(param_1,0);
    request_logical_controller_run_stop(logical_controller,'\x03');
    iVar2 = test_cached_controller_matching_channel_status_7f56a(uVar6);
    if (iVar2 != 0) {
      uVar5 = '\x03';
      uVar3 = 0x3fc;
      goto LAB_0007ca32;
    }
    check_controller_request_mode_and_release_7f4fe(uVar6,2);
    uVar5 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(uVar6 - 0x2252)))));
    if (uVar5 == '\0') {
      dispatch_record_three_way_operation_7eaf2(param_1,0);
      uVar3 = 0xff;
      goto LAB_0007ca32;
    }
  }
  else {
    if ((uVar3 == 0x3fc) || (uVar3 == 0x4fb)) goto LAB_0007ca32;
    if ((uVar3 != 0x5fa) && (uVar3 != 0x8f7)) {
      uVar4 = 1;
      goto LAB_0007ca32;
    }
    check_controller_request_mode_and_release_7f4fe(uVar6,2);
    uVar5 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(uVar6 - 0x2252)))));
  }
  uVar3 = 0x4fb;
LAB_0007ca32:
  (*((volatile uint16_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe4924u + (uint32_t)(uVar6) * (uint32_t)sizeof(F33SelectedNetworkModeState)) + (uint32_t)(0) * (uint32_t)sizeof(F33SelectedNetworkModeState) + (uint32_t)offsetof(F33SelectedNetworkModeState, mode_state))))) = uVar3;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe4924u + (uint32_t)(uVar6) * (uint32_t)sizeof(F33SelectedNetworkModeState)) + (uint32_t)(0) * (uint32_t)sizeof(F33SelectedNetworkModeState) + (uint32_t)offsetof(F33SelectedNetworkModeState, remaining_delay))))) = uVar5;
  return uVar4;
}

undefined4 request_selected_network_mode_one_7ca3e(char param_1)

{
  uint32_t puVar1;
  ushort uVar2;
  undefined4 uVar3;
  uchar uVar4;
  uint uVar5;
  
  puVar1 = 0x23dfcu;
  uVar3 = 0;
  uVar5 = (uint)(byte)(param_1 - DAT_00021ba9);
  uVar2 = (*((volatile uint16_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe4924u + (uint32_t)(uVar5) * (uint32_t)sizeof(F33SelectedNetworkModeState)) + (uint32_t)(0) * (uint32_t)sizeof(F33SelectedNetworkModeState) + (uint32_t)offsetof(F33SelectedNetworkModeState, mode_state)))));
  uVar4 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe4924u + (uint32_t)(uVar5) * (uint32_t)sizeof(F33SelectedNetworkModeState)) + (uint32_t)(0) * (uint32_t)sizeof(F33SelectedNetworkModeState) + (uint32_t)offsetof(F33SelectedNetworkModeState, remaining_delay)))));
  if (uVar2 == 0xff) {
LAB_0007caaa:
    check_controller_request_mode_and_release_7f4fe(uVar5,0);
    uVar4 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(uVar5 - 0x2252)))));
    if (uVar4 == '\0') {
LAB_0007cabe:
      request_controller_run_and_publish_selected_mode_one_7c830(uVar5);
LAB_0007cac4:
      uVar2 = 0x1fe;
      goto LAB_0007cace;
    }
  }
  else {
    if (uVar2 == 0x1fe) goto LAB_0007cace;
    if (uVar2 == 0x2fd) {
      call_21840_with_two_bytes_832da(param_1,1);
      set_controller_request_byte_from_mode_80f6c(uVar5,1);
      dispatch_record_three_way_operation_7eaf2(param_1,1);
      goto LAB_0007cac4;
    }
    if (uVar2 == 0x3fc) goto LAB_0007cabe;
    if (uVar2 == 0x4fb) goto LAB_0007caaa;
    if (uVar2 == 0x5fa) goto LAB_0007cace;
    if (uVar2 != 0x8f7) {
      uVar3 = 1;
      goto LAB_0007cace;
    }
  }
  uVar2 = 0x5fa;
LAB_0007cace:
  (*((volatile uint16_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe4924u + (uint32_t)(uVar5) * (uint32_t)sizeof(F33SelectedNetworkModeState)) + (uint32_t)(0) * (uint32_t)sizeof(F33SelectedNetworkModeState) + (uint32_t)offsetof(F33SelectedNetworkModeState, mode_state))))) = uVar2;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe4924u + (uint32_t)(uVar5) * (uint32_t)sizeof(F33SelectedNetworkModeState)) + (uint32_t)(0) * (uint32_t)sizeof(F33SelectedNetworkModeState) + (uint32_t)offsetof(F33SelectedNetworkModeState, remaining_delay))))) = uVar4;
  return uVar3;
}

undefined4 request_selected_network_mode_two_7cada(char param_1)

{
  byte logical_controller;
  ushort uVar1;
  uint32_t puVar2;
  ushort uVar3;
  undefined4 uVar4;
  uchar uVar5;
  uint uVar6;
  
  puVar2 = 0x23dfcu;
  uVar4 = 0;
  logical_controller = param_1 - DAT_00021ba9;
  uVar6 = (uint)logical_controller;
  uVar1 = (*((volatile uint16_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe491cu + (uint32_t)(uVar6) * (uint32_t)sizeof(F33SelectedNetworkRecoveryState)) + (uint32_t)(0) * (uint32_t)sizeof(F33SelectedNetworkRecoveryState) + (uint32_t)offsetof(F33SelectedNetworkRecoveryState, recovery_state)))));
  uVar3 = (*((volatile uint16_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe4924u + (uint32_t)(uVar6) * (uint32_t)sizeof(F33SelectedNetworkModeState)) + (uint32_t)(0) * (uint32_t)sizeof(F33SelectedNetworkModeState) + (uint32_t)offsetof(F33SelectedNetworkModeState, mode_state)))));
  uVar5 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe4924u + (uint32_t)(uVar6) * (uint32_t)sizeof(F33SelectedNetworkModeState)) + (uint32_t)(0) * (uint32_t)sizeof(F33SelectedNetworkModeState) + (uint32_t)offsetof(F33SelectedNetworkModeState, remaining_delay)))));
  if (uVar3 == 0xff) {
LAB_0007cb36:
    check_controller_request_mode_and_release_7f4fe(uVar6,0);
    uVar5 = '\0';
    if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(uVar6 - 0x2252))))) != '\0') {
      uVar3 = 0x8f7;
      uVar5 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(uVar6 - 0x2252))))) + '\x01';
      goto LAB_0007cb80;
    }
LAB_0007cb52:
    request_logical_controller_run_stop(logical_controller,'\x02');
    if (uVar1 == 0xff) {
LAB_0007cb70:
      publish_selected_mode_two_and_controller_policy_three_7c880(uVar6);
    }
    else {
      dispatch_record_three_way_operation_7eaf2(param_1,1);
    }
  }
  else {
    if (uVar3 != 0x1fe) {
      if (uVar3 == 0x2fd) goto LAB_0007cb80;
      if (uVar3 != 0x3fc) {
        if (uVar3 != 0x4fb) {
          if (uVar3 == 0x5fa) {
            uVar3 = 0x8f7;
          }
          else if (uVar3 != 0x8f7) {
            uVar4 = 1;
          }
          goto LAB_0007cb80;
        }
        goto LAB_0007cb36;
      }
      goto LAB_0007cb52;
    }
    if (uVar1 == 0xff) goto LAB_0007cb70;
  }
  uVar3 = 0x2fd;
LAB_0007cb80:
  (*((volatile uint16_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe4924u + (uint32_t)(uVar6) * (uint32_t)sizeof(F33SelectedNetworkModeState)) + (uint32_t)(0) * (uint32_t)sizeof(F33SelectedNetworkModeState) + (uint32_t)offsetof(F33SelectedNetworkModeState, mode_state))))) = uVar3;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe4924u + (uint32_t)(uVar6) * (uint32_t)sizeof(F33SelectedNetworkModeState)) + (uint32_t)(0) * (uint32_t)sizeof(F33SelectedNetworkModeState) + (uint32_t)offsetof(F33SelectedNetworkModeState, remaining_delay))))) = uVar5;
  return uVar4;
}

undefined4 dispatch_selected_network_mode_request_zero_one_two_7cb8c(undefined1 param_1,char param_2)

{
  undefined4 uVar1;
  
  uVar1 = 1;
  if (param_2 == '\0') {
    uVar1 = request_selected_network_mode_zero_7c98c(param_1);
  }
  else if (param_2 == '\x01') {
    uVar1 = request_selected_network_mode_one_7ca3e((uint)(byte)param_1);
  }
  else if (param_2 == '\x02') {
    uVar1 = request_selected_network_mode_two_7cada((uint)(byte)param_1);
  }
  return uVar1;
}

uint get_selected_network_software_mode(uchar network,uchar *mode)

{
  ushort uVar1;
  uchar uVar2;
  uint uVar3;
  
  uVar3 = (uint)network - (uint)DAT_00021ba9 & 0xff;
  if (DAT_00021ba8 <= uVar3) {
    return 1;
  }
  uVar1 = (*((volatile uint16_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe4924u + (uint32_t)(uVar3) * (uint32_t)sizeof(F33SelectedNetworkModeState)) + (uint32_t)(0) * (uint32_t)sizeof(F33SelectedNetworkModeState) + (uint32_t)offsetof(F33SelectedNetworkModeState, mode_state)))));
  if (uVar1 == 0xff) {
    uVar2 = '\0';
  }
  else {
    if (uVar1 != 0x1fe) {
      if (uVar1 == 0x2fd) {
        *mode = '\x02';
        if ((*((volatile uint16_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe491cu + (uint32_t)(uVar3) * (uint32_t)sizeof(F33SelectedNetworkRecoveryState)) + (uint32_t)(0) * (uint32_t)sizeof(F33SelectedNetworkRecoveryState) + (uint32_t)offsetof(F33SelectedNetworkRecoveryState, recovery_state))))) != 0x1fe) {
          return 0;
        }
      }
      else if ((((uVar1 != 0x3fc) && (uVar1 != 0x4fb)) && (uVar1 != 0x5fa)) && (uVar1 != 0x8f7)) {
        return 1;
      }
    }
    uVar2 = '\x01';
  }
  *mode = uVar2;
  return 0;
}

void restore_selected_mode_two_and_normal_software_policy_7cc1e(uint param_1)

{
  uint uVar1;
  
  param_1 = param_1 & 0xff;
  if ((*((volatile uint16_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe4924u + (uint32_t)(param_1) * (uint32_t)sizeof(F33SelectedNetworkModeState)) + (uint32_t)(0) * (uint32_t)sizeof(F33SelectedNetworkModeState) + (uint32_t)offsetof(F33SelectedNetworkModeState, mode_state))))) == 0x2fd) {
    uVar1 = DAT_00021ba9 + param_1 & 0xff;
    set_controller_request_byte_from_mode_80f6c(param_1,3);
    dispatch_record_three_way_operation_7eaf2(uVar1,2);
    call_21840_with_two_bytes_832da(uVar1,2);
  }
  set_network_software_policy_1e_and_refresh_7c0b4(param_1);
  return;
}

void stop_selected_controller_and_publish_recovery_notification_7cc60(byte param_1,char param_2)

{
  uint32_t puVar1;
  uint32_t puVar2;
  uint uVar3;
  undefined4 uVar4;
  uint uVar5;
  
  puVar1 = 0xfebeb800u;
  puVar2 = 0x23dfcu;
  uVar3 = (uint)param_1;
  request_logical_controller_run_stop(param_1,'\x03');
  set_network_software_policy_0f_and_refresh_7c082(uVar3);
  set_controller_cache_6b94_and_clear_channels_7fafa(uVar3);
  if ((*((short *)camry_host_ptr((uint32_t)(puVar1 + uVar3 * 4 + -0x6edc)))) == 0x2fd) {
    uVar5 = (byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x2253))))) + uVar3 & 0xff;
    if (param_2 == '\x01') {
      uVar4 = 3;
    }
    else {
      uVar4 = 5;
    }
    call_21840_with_two_bytes_832da(uVar5,uVar4);
    if ((*((short *)camry_host_ptr((uint32_t)(puVar1 + uVar3 * 8 + -0x6ee4)))) == 0xff) {
      dispatch_record_three_way_operation_7eaf2(uVar5,1);
    }
  }
  return;
}

void reassert_controller_run_for_active_selected_modes_7ccbe(byte param_1)

{
  if (((*((volatile uint16_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe4924u + (uint32_t)(param_1) * (uint32_t)sizeof(F33SelectedNetworkModeState)) + (uint32_t)(0) * (uint32_t)sizeof(F33SelectedNetworkModeState) + (uint32_t)offsetof(F33SelectedNetworkModeState, mode_state))))) == 0x2fd) ||
     ((*((volatile uint16_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe4924u + (uint32_t)(param_1) * (uint32_t)sizeof(F33SelectedNetworkModeState)) + (uint32_t)(0) * (uint32_t)sizeof(F33SelectedNetworkModeState) + (uint32_t)offsetof(F33SelectedNetworkModeState, mode_state))))) == 0x1fe)) {
    request_logical_controller_run_stop(param_1,'\x02');
  }
  return;
}

void latch_fault_0100_and_dispatch_network_cause_hooks_7cce4(char param_1,undefined2 param_2)

{
  char cVar1;
  
  cVar1 = DAT_00021ba9 + param_1;
  reset_valid_encoded_tx_queue_notify_80066(param_1,0x100);
  set_controller_status_byte_4911_55_8156c(param_1);
  dispatch_selected_network_fault_bits_to_stub_hooks_7cdda(cVar1,param_2);
  return;
}

void reset_selected_network_recovery_records_7cd12(void)

{
  uint uVar1;
  uint uVar2;
  
  uVar2 = (uint)DAT_00021ba8;
  for (uVar1 = 0; uVar1 < uVar2; uVar1 = uVar1 + 1 & 0xff) {
    (*((volatile int16_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe491cu + (uint32_t)(uVar1) * (uint32_t)sizeof(F33SelectedNetworkRecoveryState)) + (uint32_t)(0) * (uint32_t)sizeof(F33SelectedNetworkRecoveryState) + (uint32_t)offsetof(F33SelectedNetworkRecoveryState, remaining_hold))))) = 0;
    (*((volatile uint16_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe491cu + (uint32_t)(uVar1) * (uint32_t)sizeof(F33SelectedNetworkRecoveryState)) + (uint32_t)(0) * (uint32_t)sizeof(F33SelectedNetworkRecoveryState) + (uint32_t)offsetof(F33SelectedNetworkRecoveryState, recovery_state))))) = 0xff;
    (*((volatile uint16_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe491cu + (uint32_t)(uVar1) * (uint32_t)sizeof(F33SelectedNetworkRecoveryState)) + (uint32_t)(0) * (uint32_t)sizeof(F33SelectedNetworkRecoveryState) + (uint32_t)offsetof(F33SelectedNetworkRecoveryState, aggregated_cause))))) = 0;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe491cu + (uint32_t)(uVar1) * (uint32_t)sizeof(F33SelectedNetworkRecoveryState)) + (uint32_t)(0) * (uint32_t)sizeof(F33SelectedNetworkRecoveryState) + (uint32_t)offsetof(F33SelectedNetworkRecoveryState, reported_fault_class))))) = '\x03';
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe491cu + (uint32_t)(uVar1) * (uint32_t)sizeof(F33SelectedNetworkRecoveryState)) + (uint32_t)(0) * (uint32_t)sizeof(F33SelectedNetworkRecoveryState) + (uint32_t)offsetof(F33SelectedNetworkRecoveryState, uninterpreted))))) = '\0';
  }
  return;
}

void clear_selected_network_recovery_causes_and_fault_classes_7cd3e(void)

{
  uint uVar1;
  uint uVar2;
  
  uVar2 = (uint)DAT_00021ba8;
  for (uVar1 = 0; uVar1 < uVar2; uVar1 = uVar1 + 1 & 0xff) {
    (*((volatile uint16_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe491cu + (uint32_t)(uVar1) * (uint32_t)sizeof(F33SelectedNetworkRecoveryState)) + (uint32_t)(0) * (uint32_t)sizeof(F33SelectedNetworkRecoveryState) + (uint32_t)offsetof(F33SelectedNetworkRecoveryState, aggregated_cause))))) = 0;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe491cu + (uint32_t)(uVar1) * (uint32_t)sizeof(F33SelectedNetworkRecoveryState)) + (uint32_t)(0) * (uint32_t)sizeof(F33SelectedNetworkRecoveryState) + (uint32_t)offsetof(F33SelectedNetworkRecoveryState, reported_fault_class))))) = '\x03';
  }
  return;
}

ushort capture_selected_network_fault_cause_bits_58_7cd60(uint param_1)

{
  uint32_t puVar1;
  ushort uVar2;
  
  puVar1 = 0xfebeb800u;
  uVar2 = compose_controller_status_error_mask_80dc0((uint)(byte)param_1);
  (*((ushort *)camry_host_ptr((uint32_t)(puVar1 + (param_1 & 0xff) * 8 + -0x6ee0)))) = uVar2 & 0x58;
  return uVar2;
}

ushort get_single_selected_network_cause_08_10_or_40_7cd7c(uint param_1)

{
  ushort uVar1;
  ushort uVar2;
  
  uVar1 = (*((volatile uint16_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe491cu + (uint32_t)(param_1 & 0xff) * (uint32_t)sizeof(F33SelectedNetworkRecoveryState)) + (uint32_t)(0) * (uint32_t)sizeof(F33SelectedNetworkRecoveryState) + (uint32_t)offsetof(F33SelectedNetworkRecoveryState, aggregated_cause))))) & 0x58;
  if (((uVar1 == 8) || (uVar1 == 0x10)) || (uVar2 = 0, uVar1 == 0x40)) {
    uVar2 = uVar1;
  }
  return uVar2;
}

undefined4 map_network_zero_stub_result_to_fault_bit_80_7cda0(char param_1)

{
  undefined4 uVar1;
  int iVar2;
  
  iVar2 = ((void)(DAT_00021ba9 + param_1), return_const_0_7cf74());
  uVar1 = 0;
  if (iVar2 != 0) {
    uVar1 = 0x80;
  }
  return uVar1;
}

void decrement_positive_selected_recovery_hold_7cdc2(uint param_1)

{
  short sVar1;
  
  sVar1 = (*((volatile int16_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe491cu + (uint32_t)(param_1 & 0xff) * (uint32_t)sizeof(F33SelectedNetworkRecoveryState)) + (uint32_t)(0) * (uint32_t)sizeof(F33SelectedNetworkRecoveryState) + (uint32_t)offsetof(F33SelectedNetworkRecoveryState, remaining_hold)))));
  if (0 < sVar1) {
    sVar1 = sVar1 + -1;
  }
  (*((volatile int16_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe491cu + (uint32_t)(param_1 & 0xff) * (uint32_t)sizeof(F33SelectedNetworkRecoveryState)) + (uint32_t)(0) * (uint32_t)sizeof(F33SelectedNetworkRecoveryState) + (uint32_t)offsetof(F33SelectedNetworkRecoveryState, remaining_hold))))) = sVar1;
  return;
}

void dispatch_selected_network_fault_bits_to_stub_hooks_7cdda(undefined1 param_1,uint param_2)

{
  if ((param_2 & 1) != 0) {
    ((void)(param_1), return_only_stub_7cf6c());
  }
  if ((param_2 >> 1 & 1) != 0) {
    ((void)(param_1), return_only_stub_7cf72());
  }
  if ((param_2 >> 2 & 1) != 0) {
    ((void)(param_1), return_only_stub_7cf70());
  }
  if ((param_2 >> 5 & 1) != 0) {
    ((void)(param_1), return_only_stub_7cf6e());
  }
  if ((param_2 & 0x300) != 0) {
    ((void)(param_1), return_only_stub_7d014());
  }
  return;
}

void update_selected_network_fault_recovery(uchar selected_network)

{
  int iVar1;
  undefined2 *puVar2;
  uint32_t puVar3;
  uint32_t puVar4;
  uint uVar5;
  undefined1 uVar6;
  undefined2 uVar7;
  short sVar8;
  int iVar9;
  uint uVar10;
  uint uVar11;
  uint uVar12;
  
  puVar3 = 0xfebeb800u;
  puVar4 = 0x23dfcu;
  uVar5 = (uint)selected_network;
  iVar9 = get_controller_cache_compact_state_7fbb0((uint)(byte)selected_network);
  if (iVar9 != 2 && iVar9 != 3) {
    return;
  }
  puVar2 = ((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + uVar5 * 8 + -0x6ee4)));
  uVar10 = compose_controller_status_error_mask_80dc0(uVar5);
  if ((uVar10 & 0x48) != 0) {
    uVar6 = 3;
    uVar10 = uVar10 & 0x48;
    goto LAB_0007cf08;
  }
  uVar6 = (*(int (*)())camry_indirect((uint32_t)(*((code * *)camry_host_ptr((uint32_t)(puVar4 + uVar5 * 4 + -0x2264))))))(uVar5,uVar10);
  if ((uVar10 & 0x3a7) == 0) goto LAB_0007cf08;
  if ((uVar10 & 0x3a7) == 0x200) {
    (*(int (*)())camry_indirect((uint32_t)(*((code * *)camry_host_ptr((uint32_t)(puVar4 + -0x2268))))))(uVar5,uVar10);
    goto LAB_0007cf08;
  }
  uVar11 = uVar10 & 1;
  uVar12 = (byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x2253))))) + uVar5 & 0xff;
  if (uVar11 != 0) {
    ((void)(0), dispatch_record_callback_slot_thirty_six_7f386(uVar5));
  }
  stop_selected_controller_and_publish_recovery_notification_7cc60(uVar5,uVar11 != 0);
  dispatch_selected_network_fault_bits_to_stub_hooks_7cdda(uVar12,uVar10);
  reassert_controller_run_for_active_selected_modes_7ccbe(uVar5);
  if (uVar11 == 0) {
    if ((uVar10 >> 1 & 1) != 0) {
      sVar8 = (*((short *)camry_host_ptr((uint32_t)(puVar4 + uVar5 * 2 + -0x2256))));
      goto LAB_0007ced6;
    }
    iVar9 = 0;
    if ((uVar10 >> 7 & 1) != 0) {
      uVar7 = ((void)(uVar12), return_const_0_7cf7e());
      goto LAB_0007cecc;
    }
  }
  else {
    uVar7 = return_sign_extended_second_halfword_7cf78(uVar12,(int)(*((short *)camry_host_ptr((uint32_t)(puVar4 + uVar5 * 2 + -0x2258)))));
LAB_0007cecc:
    sVar8 = convert_u16_units_to_ceiling_configured_ticks_7bde2(uVar7);
LAB_0007ced6:
    iVar9 = (int)sVar8;
    if (0 < iVar9) {
      iVar9 = (int)(short)(sVar8 + 1);
    }
  }
  iVar1 = (short)puVar2[1] - iVar9;
  if (iVar1 < 0 != ((short)puVar2[1] < 0 != iVar9 < 0 && iVar9 < 0 == iVar1 < 0)) {
    puVar2[1] = (short)iVar9;
  }
  *puVar2 = 0x1fe;
LAB_0007cf08:
  *(undefined1 *)(puVar2 + 3) = uVar6;
  puVar2[2] = (short)uVar10;
  return;
}

void finish_selected_recovery_when_signed_hold_expires_7cf12(uint param_1)

{
  param_1 = param_1 & 0xff;
  if (((*((volatile uint16_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe491cu + (uint32_t)(param_1) * (uint32_t)sizeof(F33SelectedNetworkRecoveryState)) + (uint32_t)(0) * (uint32_t)sizeof(F33SelectedNetworkRecoveryState) + (uint32_t)offsetof(F33SelectedNetworkRecoveryState, recovery_state))))) == 0x1fe) &&
     ((*((volatile int16_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe491cu + (uint32_t)(param_1) * (uint32_t)sizeof(F33SelectedNetworkRecoveryState)) + (uint32_t)(0) * (uint32_t)sizeof(F33SelectedNetworkRecoveryState) + (uint32_t)offsetof(F33SelectedNetworkRecoveryState, remaining_hold))))) < 1)) {
    restore_selected_mode_two_and_normal_software_policy_7cc1e((uint)(byte)param_1);
    (*((volatile uint16_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe491cu + (uint32_t)(param_1) * (uint32_t)sizeof(F33SelectedNetworkRecoveryState)) + (uint32_t)(0) * (uint32_t)sizeof(F33SelectedNetworkRecoveryState) + (uint32_t)offsetof(F33SelectedNetworkRecoveryState, recovery_state))))) = 0xff;
  }
  return;
}

void service_all_selected_network_fault_recovery_records_7cf44(void)

{
  byte bVar1;
  uchar selected_network;
  byte bVar2;
  
  bVar1 = DAT_00021ba8;
  for (bVar2 = 0; bVar2 < bVar1; bVar2 = bVar2 + 1) {
    decrement_positive_selected_recovery_hold_7cdc2(bVar2);
    update_selected_network_fault_recovery(selected_network);
    finish_selected_recovery_when_signed_hold_expires_7cf12(bVar2);
  }
  return;
}

void return_only_stub_7cf6c(void)

{
  return;
}

void return_only_stub_7cf6e(void)

{
  return;
}

void return_only_stub_7cf70(void)

{
  return;
}

void return_only_stub_7cf72(void)

{
  return;
}

undefined4 return_const_0_7cf74(void)

{
  return 0;
}

int return_sign_extended_second_halfword_7cf78(undefined4 param_1,short param_2)

{
  return (int)param_2;
}

undefined4 return_const_0_7cf7e(void)

{
  return 0;
}

uint normalize_fault_bits_with_08_10_40_priority_7cf86(uint param_1)

{
  uint uVar1;
  
  uVar1 = (uint)((param_1 & 1) != 0);
  if ((param_1 >> 1 & 1) != 0) {
    uVar1 = uVar1 | 2;
  }
  if ((param_1 >> 2 & 1) != 0) {
    uVar1 = uVar1 | 4;
  }
  if ((param_1 >> 5 & 1) != 0) {
    uVar1 = uVar1 | 0x20;
  }
  if ((param_1 >> 7 & 1) != 0) {
    uVar1 = uVar1 | 0x80;
  }
  if ((param_1 & 0x300) != 0) {
    uVar1 = uVar1 | 0x200;
  }
  if ((param_1 >> 3 & 1) == 0) {
    if ((param_1 >> 4 & 1) == 0) {
      if ((param_1 >> 6 & 1) != 0) {
        uVar1 = uVar1 | 0x40;
      }
      return uVar1;
    }
    return uVar1 | 0x10;
  }
  return uVar1 | 8;
}

uint compose_selected_network_fault_mask_and_class_bits_7cfe2(uint param_1)

{
  uchar uVar1;
  uint uVar2;
  
  uVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe491cu + (uint32_t)(param_1 & 0xff) * (uint32_t)sizeof(F33SelectedNetworkRecoveryState)) + (uint32_t)(0) * (uint32_t)sizeof(F33SelectedNetworkRecoveryState) + (uint32_t)offsetof(F33SelectedNetworkRecoveryState, reported_fault_class)))));
  uVar2 = 0;
  if ((*((volatile uint16_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe491cu + (uint32_t)(param_1 & 0xff) * (uint32_t)sizeof(F33SelectedNetworkRecoveryState)) + (uint32_t)(0) * (uint32_t)sizeof(F33SelectedNetworkRecoveryState) + (uint32_t)offsetof(F33SelectedNetworkRecoveryState, aggregated_cause))))) != 0) {
    uVar2 = normalize_fault_bits_with_08_10_40_priority_7cf86((*((volatile uint16_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe491cu + (uint32_t)(param_1 & 0xff) * (uint32_t)sizeof(F33SelectedNetworkRecoveryState)) + (uint32_t)(0) * (uint32_t)sizeof(F33SelectedNetworkRecoveryState) + (uint32_t)offsetof(F33SelectedNetworkRecoveryState, aggregated_cause))))));
  }
  if (uVar1 == '\x02') {
    uVar2 = uVar2 | 1;
  }
  else if (uVar1 == '\x01') {
    uVar2 = uVar2 | 0x100;
  }
  return uVar2;
}
