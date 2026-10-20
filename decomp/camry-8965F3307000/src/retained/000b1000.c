#include "common.h"

void fill_inverse_request_bitmap_with_ones_b149c(void)

{
  uint uVar1;
  
  uVar1 = 0;
  do {
    *(undefined4 *)(((undefined *)camry_host_ptr((uint32_t)(0xfebeb090u + (uint32_t)(uVar1 * 4) * 1u)))) = 0xffffffff;
    uVar1 = uVar1 + 1;
  } while (uVar1 < 2);
  return;
}

void initialize_complementary_request_bitmaps_b14b2(void)

{
  int iVar1;
  uint uVar2;
  
  uVar2 = 0;
  do {
    iVar1 = uVar2 * 4;
    *(undefined4 *)(((undefined *)camry_host_ptr((uint32_t)(0xfebeb098u + (uint32_t)(iVar1) * 1u)))) = 0;
    uVar2 = uVar2 + 1;
    *(undefined4 *)(((undefined *)camry_host_ptr((uint32_t)(0xfebeb090u + (uint32_t)(iVar1) * 1u)))) = 0xffffffff;
  } while (uVar2 < 2);
  return;
}

undefined4 clear_indexed_request_and_set_complement_b14d2(uint param_1)

{
  uint *puVar1;
  int iVar2;
  uint32_t puVar3;
  undefined4 uVar4;
  uint uVar5;
  
  puVar3 = 0xfebeb800u;
  uVar5 = param_1 & 0xff;
  if (uVar5 < 0x32) {
    iVar2 = (uVar5 >> 5) * 4;
    puVar1 = (uint *)(((undefined *)camry_host_ptr((uint32_t)(0xfebeb098u + (uint32_t)(iVar2) * 1u))));
    param_1 = param_1 & 0x1f;
    if (((*puVar1 >> param_1 & 1) != 0) || ((*(uint *)(((undefined *)camry_host_ptr((uint32_t)(0xfebeb090u + (uint32_t)(iVar2) * 1u)))) >> param_1 & 1) == 0))
    {
      uVar4 = raise_priority_mask_and_return_previous_d1da0(0xffc0);
      *puVar1 = *puVar1 & ~(1 << param_1);
      (*((uint *)camry_host_ptr((uint32_t)(puVar3 + iVar2 + -0x770)))) = (*((uint *)camry_host_ptr((uint32_t)(puVar3 + iVar2 + -0x770)))) | 1 << param_1;
      restore_priority_mask_preserving_interrupt_enable_d1dc6(uVar4);
    }
    uVar4 = get_indexed_request_status_u16_b1c34(uVar5);
  }
  else {
    uVar4 = 0xffff;
  }
  return uVar4;
}

void reconcile_mode_requests(void)

{
  int iVar1;
  undefined8 uVar2;
  uint uVar3;
  uint request_id;
  
  uVar2 = 0xfebeb800;
  request_id = 0;
  do {
    iVar1 = (request_id >> 5) * 4;
    uVar3 = request_id & 0x1f;
    if ((*(uint *)(((undefined *)camry_host_ptr((uint32_t)(0xfebeb098u + (uint32_t)(iVar1) * 1u)))) >> uVar3 & 1) == 0) {
      if (((*((uint *)camry_host_ptr((uint32_t)(iVar1 + (int)uVar2 + -0x770)))) >> uVar3 & 1) != 0) {
        clear_acknowledged_mode_request(request_id);
      }
    }
    else if ((((*((uint *)camry_host_ptr((uint32_t)(iVar1 + (int)uVar2 + -0x770)))) >> uVar3 & 1) == 0) &&
            (uVar3 = materialize_mode_request(request_id), uVar3 == 0x5aa5)) {
      clear_indexed_request_and_set_complement_b14d2(request_id);
    }
    request_id = request_id + 1;
  } while (request_id < 0x32);
  return;
}

undefined4 set_indexed_request_and_clear_complement_b15ac(uint param_1)

{
  uint *puVar1;
  int iVar2;
  uint32_t puVar3;
  undefined4 uVar4;
  uint uVar5;
  
  puVar3 = 0xfebeb800u;
  uVar5 = param_1 & 0xff;
  if (uVar5 < 0x32) {
    iVar2 = (uVar5 >> 5) * 4;
    puVar1 = (uint *)(((undefined *)camry_host_ptr((uint32_t)(0xfebeb098u + (uint32_t)(iVar2) * 1u))));
    param_1 = param_1 & 0x1f;
    if (((*puVar1 >> param_1 & 1) == 0) || ((*(uint *)(((undefined *)camry_host_ptr((uint32_t)(0xfebeb090u + (uint32_t)(iVar2) * 1u)))) >> param_1 & 1) != 0))
    {
      uVar4 = raise_priority_mask_and_return_previous_d1da0(0xffc0);
      *puVar1 = *puVar1 | 1 << param_1;
      (*((uint *)camry_host_ptr((uint32_t)(puVar3 + iVar2 + -0x770)))) = (*((uint *)camry_host_ptr((uint32_t)(puVar3 + iVar2 + -0x770)))) & ~(1 << param_1);
      restore_priority_mask_preserving_interrupt_enable_d1dc6(uVar4);
    }
    uVar4 = get_indexed_request_status_u16_b1c34(uVar5);
  }
  else {
    uVar4 = 0xffff;
  }
  return uVar4;
}

undefined4 publish_live_application_mode(ushort mode)

{
  return write_xor_encoded_u16_triplicate_d26d0(mode,((undefined *)camry_host_ptr(0xfebeb11au)),((undefined *)camry_host_ptr(0xfebeb0a0u)),((undefined *)camry_host_ptr(0xfebeb0a4u)));
}

undefined4 initialize_fifty_request_status_entries_and_publish_mode_b163a(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  
  iVar3 = 0;
  do {
    iVar2 = iVar3 + 1;
    *(undefined2 *)(((undefined *)camry_host_ptr((uint32_t)(0xfebeb0a8u + (uint32_t)(iVar3 * 2) * 1u)))) = 0;
    iVar1 = iVar3 + -0x31;
    iVar3 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  DAT_febeb10c = 0;
  DAT_febeb0a6 = 0xff;
  DAT_febeb11c = 0;
  DAT_febeb0a2 = 0xffff;
  return publish_live_application_mode(DAT_febeb11a);
}

void reset_mode_readiness_counter(void)

{
  DAT_febeb114 = 0;
  return_only_stub_b1d9e();
  return;
}

void repair_live_application_mode(void)

{
  int iVar1;
  undefined2 uStack_12;
  
  iVar1 = read_vote_xor_encoded_u16_triplicate_d242e(((undefined *)camry_host_ptr(0xfebeb11au)),((undefined *)camry_host_ptr(0xfebeb0a0u)),((undefined *)camry_host_ptr(0xfebeb0a4u)),&uStack_12);
  if ((iVar1 != 0) && (iVar1 == -0xc || iVar1 == -0xb)) {
    write_xor_encoded_u16_triplicate_d26d0(uStack_12,((undefined *)camry_host_ptr(0xfebeb11au)),((undefined *)camry_host_ptr(0xfebeb0a0u)),((undefined *)camry_host_ptr(0xfebeb0a4u)));
  }
  return;
}

uint probe_pending_mode_request(uchar request_id)

{
  uint uVar1;
  
  if (*(short *)(((undefined *)camry_host_ptr((uint32_t)(0xfebeb0a8u + (uint32_t)((uint)request_id * 2) * 1u)))) == -0x5aa6) {
    uVar1 = 1;
    if (request_id < 0x10) {
      DAT_febeb0a6 = ~request_id;
      DAT_febeb10c = request_id;
      DAT_febeb11c = DAT_febeb11a;
      DAT_febeb0a2 = ~DAT_febeb11a;
      return uVar1;
    }
  }
  else {
    uVar1 = 0;
  }
  return uVar1;
}

void transition_application_mode(ushort new_mode)

{
  if ((DAT_febeb11a < 0xa00) && (new_mode < 0xa00)) {
    (*(int (*)())camry_indirect((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)((uint32_t)(0xaeb00u + (uint32_t)(DAT_febeb11a >> 8) * (uint32_t)sizeof(F33ModeFamilyHooks)) + (uint32_t)(0) * (uint32_t)sizeof(F33ModeFamilyHooks) + (uint32_t)offsetof(F33ModeFamilyHooks, exit))))))))(new_mode);
    (*(int (*)())camry_indirect((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)((uint32_t)(0xaeb00u + (uint32_t)(new_mode >> 8) * (uint32_t)sizeof(F33ModeFamilyHooks)) + (uint32_t)(0) * (uint32_t)sizeof(F33ModeFamilyHooks) + (uint32_t)offsetof(F33ModeFamilyHooks, entry))))))))();
    publish_live_application_mode(new_mode);
  }
  return;
}

void acknowledge_selected_mode_request(uchar request_id)

{
  uint uVar1;
  
  uVar1 = (uint)request_id;
  if ((((uVar1 == DAT_febeb10c) && ((~uVar1 & 0xff) == (uint)DAT_febeb0a6)) || (0x10 < uVar1)) &&
     (*(short *)(((undefined *)camry_host_ptr((uint32_t)(0xfebeb0a8u + (uint32_t)(uVar1 * 2) * 1u)))) == -0x5aa6)) {
    *(short *)(((undefined *)camry_host_ptr((uint32_t)(0xfebeb0a8u + (uint32_t)(uVar1 * 2) * 1u)))) = 0x5aa5;
  }
  return;
}

uint qualify_mode_restart_readiness(void)

{
  char cVar1;
  char cVar2;
  char cVar3;
  char cVar4;
  uint32_t puVar5;
  uint uVar6;
  byte bVar7;
  
  bVar7 = DAT_febeb114;
  cVar4 = DAT_febeb075;
  cVar3 = DAT_febeb074;
  cVar2 = DAT_febeb073;
  cVar1 = DAT_febeb072;
  puVar5 = 0xfebeb800u;
  uVar6 = query_application_nvm_readiness();
  if (uVar6 == 1) {
    if (((((cVar1 == '\0') && (cVar3 == '\0')) && (cVar2 == '\0')) && (cVar4 == '\0')) ||
       (DAT_000af3dc <= bVar7)) {
      bVar7 = 0;
      uVar6 = 0x5a;
      goto LAB_000b17e6;
    }
    set_channel_owner_request('\0',0x20002);
    set_channel_owner_request('\x01',0x20002);
    thunk_set_secondary_channel_request_bounded5_56e66(0, ((uint32_t)(0x20002u)));
    thunk_set_secondary_channel_request_bounded5_56e66(1, ((uint32_t)(0x20002u)));
    bVar7 = bVar7 + 1;
  }
  uVar6 = 0;
LAB_000b17e6:
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x6ec))))) = bVar7;
  return uVar6;
}

int request_foreground_restart_from_mode(void)

{
  thunk_clear_redundant_flag_febf0671_66f84();
  thunk_clear_redundant_flag_febf0672_66fba();
  transition_application_mode(0);
  return thunk_publish_redundant_mode_marker_a55a_5889a();
}

void advance_application_mode(void)

{
  uint32_t puVar1;
  uchar uVar2;
  ushort uVar3;
  uint uVar4;
  uint uVar5;
  uint uVar6;
  
  puVar1 = 0xfebeb800u;
  repair_live_application_mode();
  uVar3 = (*((ushort *)camry_host_ptr((uint32_t)(puVar1 + -0x6e6)))) & 0xff00;
  if (uVar3 == 0x100) {
    clear_direct_output_enables();
    advance_mode100_substate();
    uVar6 = probe_pending_mode_request('\0');
    if (uVar6 == 1) {
      uVar3 = 0x700;
LAB_000b1894:
      transition_application_mode(uVar3);
    }
    else {
      uVar6 = probe_pending_mode_request('\t');
      if (uVar6 == 1) {
        uVar3 = 0x900;
        goto LAB_000b1894;
      }
      uVar6 = probe_pending_mode_request('\x05');
      if (uVar6 == 1) {
        uVar3 = 0x200;
        goto LAB_000b1894;
      }
    }
    acknowledge_selected_mode_request('\0');
    uVar2 = '\x05';
  }
  else {
    if (uVar3 == 0x200) {
      advance_mode200_output_sequence();
      uVar6 = probe_pending_mode_request('\0');
      if ((uVar6 == 1) || (uVar6 = probe_pending_mode_request('\x01'), uVar6 == 1)) {
        uVar3 = 0x700;
LAB_000b18e0:
        transition_application_mode(uVar3);
      }
      else {
        uVar6 = probe_pending_mode_request('\t');
        if (uVar6 == 1) {
          uVar3 = 0x900;
          goto LAB_000b18e0;
        }
        uVar6 = probe_pending_mode_request('\x03');
        if (uVar6 == 1) {
          uVar3 = 0x300;
          goto LAB_000b18e0;
        }
      }
      acknowledge_selected_mode_request('\0');
      acknowledge_selected_mode_request('\x01');
      acknowledge_selected_mode_request('\t');
      uVar2 = '\x03';
      goto LAB_000b1bf6;
    }
    if (uVar3 == 0x300) {
      clear_direct_output_enables();
      advance_mode300_substate();
      uVar6 = probe_pending_mode_request('\0');
      if ((uVar6 == 1) || (uVar6 = probe_pending_mode_request('\x01'), uVar6 == 1)) {
        uVar3 = 0x700;
LAB_000b194c:
        transition_application_mode(uVar3);
      }
      else {
        uVar6 = probe_pending_mode_request('\t');
        if (uVar6 == 1) {
          uVar3 = 0x900;
          goto LAB_000b194c;
        }
        uVar6 = probe_pending_mode_request('\x06');
        if (uVar6 == 1) {
          uVar3 = 0x500;
          goto LAB_000b194c;
        }
        uVar6 = probe_pending_mode_request('\f');
        if (uVar6 == 1) {
          uVar3 = 0x400;
          goto LAB_000b194c;
        }
      }
      acknowledge_selected_mode_request('\0');
      acknowledge_selected_mode_request('\x01');
      acknowledge_selected_mode_request('\t');
      acknowledge_selected_mode_request('\f');
      uVar2 = '\x06';
      goto LAB_000b1bf6;
    }
    if (uVar3 == 0x400) {
      clear_direct_output_enables();
      apply_mode400_output_requests();
      uVar6 = probe_pending_mode_request('\0');
      if ((uVar6 == 1) || (uVar6 = probe_pending_mode_request('\x01'), uVar6 == 1)) {
LAB_000b19b4:
        uVar3 = 0x700;
LAB_000b19c8:
        transition_application_mode(uVar3);
      }
      else {
        uVar6 = probe_pending_mode_request('\t');
        if (uVar6 == 1) {
          uVar3 = 0x900;
          goto LAB_000b19c8;
        }
        uVar6 = probe_pending_mode_request('\x06');
        if (uVar6 == 1) {
          uVar3 = 0x500;
          goto LAB_000b19c8;
        }
        uVar6 = probe_pending_mode_request('\v');
        if (uVar6 == 1) goto LAB_000b19b4;
        uVar6 = probe_pending_mode_request('\a');
        if (uVar6 == 1) {
          uVar3 = 0x600;
          goto LAB_000b19c8;
        }
      }
      acknowledge_selected_mode_request('\0');
      acknowledge_selected_mode_request('\x01');
      acknowledge_selected_mode_request('\t');
      acknowledge_selected_mode_request('\x06');
      uVar2 = '\v';
LAB_000b19e6:
      acknowledge_selected_mode_request(uVar2);
      uVar2 = '\a';
      goto LAB_000b1bf6;
    }
    if (uVar3 == 0x500) {
      clear_direct_output_enables();
      advance_service_family();
      uVar6 = probe_pending_mode_request('\0');
      if ((uVar6 == 1) || (uVar6 = probe_pending_mode_request('\x01'), uVar6 == 1)) {
        uVar3 = 0x700;
LAB_000b1b5a:
        transition_application_mode(uVar3);
      }
      else {
        uVar6 = probe_pending_mode_request('\t');
        if (uVar6 == 1) {
          uVar3 = 0x900;
          goto LAB_000b1b5a;
        }
        uVar6 = probe_pending_mode_request('\x04');
        if (uVar6 == 1) {
          uVar3 = 0x300;
          if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x65c))))) != '\0') {
            uVar3 = 0x400;
          }
          goto LAB_000b1b5a;
        }
        uVar6 = probe_pending_mode_request('\a');
        if (uVar6 == 1) {
          uVar3 = 0x600;
          goto LAB_000b1b5a;
        }
      }
      acknowledge_selected_mode_request('\0');
      acknowledge_selected_mode_request('\x01');
      acknowledge_selected_mode_request('\t');
      uVar2 = '\x04';
      goto LAB_000b19e6;
    }
    if (uVar3 != 0x600) {
      if (uVar3 == 0x700) {
        clear_direct_output_enables();
        uVar6 = advance_mode700_substate();
        uVar4 = probe_pending_mode_request('\x02');
        uVar5 = probe_pending_mode_request('\0');
        if (uVar5 == 1) {
LAB_000b1a64:
          uVar3 = 0x800;
LAB_000b1a78:
          transition_application_mode(uVar3);
        }
        else {
          uVar5 = probe_pending_mode_request('\t');
          if (uVar5 == 1) {
            uVar3 = 0x900;
            goto LAB_000b1a78;
          }
          if ((uVar6 == 0) && (uVar4 == 1)) {
            if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6eb))))) != 'Z') {
              thunk_reset_classifier_counts_and_rearm_status_flags_515e6();
              (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6eb))))) = 0x5a;
            }
            uVar6 = qualify_mode_restart_readiness();
            if (uVar6 == 0x5a) {
              uVar6 = get_mode_restart_hardware_selector();
              if (uVar6 == 0x5a) goto LAB_000b1a64;
              request_foreground_restart_from_mode();
              acknowledge_selected_mode_request('\x02');
            }
          }
          else {
            uVar6 = probe_pending_mode_request('\n');
            if (uVar6 == 1) goto LAB_000b1a64;
            uVar6 = probe_pending_mode_request('\a');
            if (uVar6 == 1) {
              uVar3 = 0x600;
              goto LAB_000b1a78;
            }
          }
        }
        acknowledge_selected_mode_request('\0');
        acknowledge_selected_mode_request('\t');
        acknowledge_selected_mode_request('\a');
        uVar2 = '\n';
        goto LAB_000b1bf6;
      }
      if (uVar3 != 0x800) {
        if (uVar3 != 0x900) {
          return;
        }
        clear_direct_output_enables();
        return_only_stub_b33d8();
        uVar6 = probe_pending_mode_request('\x0e');
        if (uVar6 == 1) {
          transition_application_mode(0x800);
        }
        uVar2 = '\x0e';
        goto LAB_000b1bf6;
      }
      clear_direct_output_enables();
      apply_mode800_ready_output_requests();
      uVar6 = probe_pending_mode_request('\x0f');
      if (uVar6 == 1) {
        call_terminal_masked_hardware_sequence_ff0d8();
      }
      else {
        uVar6 = probe_pending_mode_request('\t');
        if (uVar6 == 1) {
          uVar3 = 0x900;
LAB_000b1aee:
          transition_application_mode(uVar3);
        }
        else {
          uVar6 = probe_pending_mode_request('\x02');
          if (uVar6 == 1) {
            thunk_set_two_classifier_flags_and_clear_two_counts_515d4();
            uVar6 = qualify_mode_restart_readiness();
            if (uVar6 == 0x5a) {
              thunk_set_redundant_terminal_sequence_request_6163e();
              acknowledge_selected_mode_request('\x02');
            }
          }
          else {
            uVar6 = probe_pending_mode_request('\a');
            if (uVar6 == 1) {
              uVar3 = 0x600;
              goto LAB_000b1aee;
            }
          }
        }
      }
      acknowledge_selected_mode_request('\x0f');
      uVar2 = '\t';
      goto LAB_000b19e6;
    }
    clear_direct_output_enables();
    return_only_stub_b32f2();
    uVar6 = probe_pending_mode_request('\0');
    if (uVar6 == 1) {
LAB_000b1bc4:
      uVar3 = 0x700;
LAB_000b1bd8:
      transition_application_mode(uVar3);
    }
    else {
      uVar6 = probe_pending_mode_request('\r');
      if (uVar6 == 1) {
LAB_000b1bd4:
        uVar3 = 0x900;
        goto LAB_000b1bd8;
      }
      uVar6 = probe_pending_mode_request('\b');
      if ((uVar6 == 1) || (uVar6 = probe_pending_mode_request('\x01'), uVar6 == 1))
      goto LAB_000b1bc4;
      uVar6 = probe_pending_mode_request('\t');
      if (uVar6 == 1) goto LAB_000b1bd4;
    }
    acknowledge_selected_mode_request('\0');
    acknowledge_selected_mode_request('\b');
    acknowledge_selected_mode_request('\x01');
    uVar2 = '\r';
  }
  acknowledge_selected_mode_request(uVar2);
  uVar2 = '\t';
LAB_000b1bf6:
  acknowledge_selected_mode_request(uVar2);
  return;
}

uint materialize_mode_request(uint request_id)

{
  uint32_t puVar1;
  
  puVar1 = ((uint32_t)((uint)*(ushort *)(((undefined *)camry_host_ptr((uint32_t)(0xfebeb0a8u + (uint32_t)((request_id & 0xff) * 2) * 1u))))));
  if ((puVar1)!=((uint32_t)((uint32_t)(0x5aa5)))) {
    puVar1 = (0xa55au);
    *(ushort *)(((undefined *)camry_host_ptr((uint32_t)(0xfebeb0a8u + (uint32_t)((request_id & 0xff) * 2) * 1u)))) = 0xa55a;
  }
  return (uint)(puVar1);
}

void clear_acknowledged_mode_request(uint request_id)

{
  if (*(short *)(((undefined *)camry_host_ptr((uint32_t)(0xfebeb0a8u + (uint32_t)((request_id & 0xff) * 2) * 1u)))) == 0x5aa5) {
    *(short *)(((undefined *)camry_host_ptr((uint32_t)(0xfebeb0a8u + (uint32_t)((request_id & 0xff) * 2) * 1u)))) = 0;
  }
  return;
}

void mode_hook_b1c32(void)

{
  return;
}

undefined2 get_indexed_request_status_u16_b1c34(uint param_1)

{
  return *(undefined2 *)(((undefined *)camry_host_ptr((uint32_t)(0xfebeb0a8u + (uint32_t)((param_1 & 0xff) * 2) * 1u))));
}

bool check_status_byte_complement_pair_b1c40(void)

{
  return DAT_febeb0a6 == (byte)~DAT_febeb10c;
}

void start_mode100_after_foreground_restart(void)

{
  transition_application_mode(0x100);
  return;
}

undefined2 vote_redundant_application_mode_u16_b1c64(void)

{
  undefined2 uStack_6;
  
  read_vote_xor_encoded_u16_triplicate_d242e(((undefined *)camry_host_ptr(0xfebeb11au)),((undefined *)camry_host_ptr(0xfebeb0a0u)),((undefined *)camry_host_ptr(0xfebeb0a4u)),&uStack_6);
  return uStack_6;
}

undefined4 set_request_index_17_b1c84(void)

{
  return set_indexed_request_and_clear_complement_b15ac(0x11);
}

int release_nvm_hold_and_conditionally_restart_acquisition_b1c96(void)

{
  int iVar1;
  
  thunk_clear_nvm_work_hold_66fd4();
  iVar1 = thunk_test_redundant_status_a5_or_vote_error13_588b6();
  if (iVar1 != 0) {
    thunk_restart_nvm_acquisition_with_reset_scan_cursors_66ef4();
  }
  return iVar1;
}

int restore_nvm_records_c_9_and_8_b1cae(void)

{
  thunk_load_record_twelve_samples_and_arm_capture_45d98();
  load_or_clear_record9_configuration_fields_bd9da();
  return load_record8_fields_and_mark_initialized_bd81e();
}

undefined4 set_request_index_19_b1cc2(void)

{
  return set_indexed_request_and_clear_complement_b15ac(0x13);
}

undefined4 set_request_index_20_b1ce0(void)

{
  return set_indexed_request_and_clear_complement_b15ac(0x14);
}

undefined4 set_request_index_5_b1cf2(void)

{
  return set_indexed_request_and_clear_complement_b15ac(5);
}

void advance_mode100_substate(void)

{
  uchar request_id;
  uint uVar1;
  
  switch(DAT_febeb11a) {
  case 0x100:
    set_request_index_17_b1c84();
    uVar1 = probe_pending_mode_request('\x11');
    if (uVar1 == 1) {
      release_nvm_hold_and_conditionally_restart_acquisition_b1c96();
      publish_live_application_mode(0x101);
    }
    request_id = '\x11';
    break;
  case 0x101:
    uVar1 = probe_pending_mode_request('\x12');
    if (uVar1 == 1) {
      restore_nvm_records_c_9_and_8_b1cae();
      set_request_index_19_b1cc2();
      publish_live_application_mode(0x102);
    }
    request_id = '\x12';
    break;
  case 0x102:
    uVar1 = probe_pending_mode_request('\x13');
    if (uVar1 == 1) {
      thunk_restore_and_age_retained_cell_and_event_channels_d10d4();
      publish_live_application_mode(0x103);
    }
    request_id = '\x13';
    break;
  case 0x103:
    set_request_index_20_b1ce0();
    uVar1 = probe_pending_mode_request('\x14');
    if (uVar1 == 1) {
      set_request_index_5_b1cf2();
    }
    request_id = '\x14';
    break;
  default:
    goto switchD_000b1d10_default;
  }
  acknowledge_selected_mode_request(request_id);
switchD_000b1d10_default:
  return;
}

void return_only_stub_b1d9e(void)

{
  return;
}

void mode_hook_b1da0(void)

{
  return;
}

void apply_mode0201_entry_requests(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  if ((DAT_febeb082 & 1) == 0) {
    puVar1 = 0xfebeb800u;
    set_output_request_word((byte)DAT_febeb082 & 1,0x7001);
    clear_direct_output_bank0();
    set_channel_owner_request('\0',2);
    thunk_set_priority_mask_8a9c_bounded2_56c26(0,4);
    thunk_set_secondary_channel_request_bounded5_56e66(0,2);
    thunk_set_secondary_priority_mask_bounded2_56f14(0,4);
    thunk_set_request_word_8a50_bounded5_569ac(0,0);
    thunk_set_request_word_8a2c_bounded5_568dc(0,0x20);
    thunk_set_indexed_status_mask_word_if_below_five_50c82(0,0);
    thunk_set_request_word_8aa8_bounded6_56cda(0,0xc);
  }
  if (((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x77e))))) & 2) == 0) {
    set_output_request_word('\x01',0x70010000);
    clear_direct_output_bank1();
    set_channel_owner_request('\x01',0x20000);
    thunk_set_priority_mask_8a9c_bounded2_56c26(1,0x40000);
    thunk_set_secondary_channel_request_bounded5_56e66(1,0x20000);
    thunk_set_secondary_priority_mask_bounded2_56f14(1,0x40000);
    thunk_set_request_word_8a50_bounded5_569ac(1,0);
    thunk_set_request_word_8a2c_bounded5_568dc(1,0x200000);
    thunk_set_indexed_status_mask_word_if_below_five_50c82(1,0);
    thunk_set_request_word_8aa8_bounded6_56cda(1,0xc0000);
  }
  thunk_set_request_word_8a48_bounded2_5693e(0,3);
  return;
}

void apply_mode0202_entry_requests(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  if ((DAT_febeb082 & 1) == 0) {
    puVar1 = 0xfebeb800u;
    set_output_request_word((byte)DAT_febeb082 & 1,0x7001);
    clear_direct_output_bank0();
    set_channel_owner_request('\0',2);
    thunk_set_priority_mask_8a9c_bounded2_56c26(0,4);
    thunk_set_secondary_channel_request_bounded5_56e66(0,2);
    thunk_set_secondary_priority_mask_bounded2_56f14(0,4);
    thunk_set_request_word_8a50_bounded5_569ac(0,0);
    thunk_set_request_word_8a2c_bounded5_568dc(0,2);
    thunk_set_indexed_status_mask_word_if_below_five_50c82(0,0);
    thunk_set_request_word_8aa8_bounded6_56cda(0,0xc);
  }
  if (((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x77e))))) & 2) == 0) {
    set_output_request_word('\x01',0x70010000);
    clear_direct_output_bank1();
    set_channel_owner_request('\x01',0x20000);
    thunk_set_priority_mask_8a9c_bounded2_56c26(1,0x40000);
    thunk_set_secondary_channel_request_bounded5_56e66(1,0x20000);
    thunk_set_secondary_priority_mask_bounded2_56f14(1,0x40000);
    thunk_set_request_word_8a50_bounded5_569ac(1,0);
    thunk_set_request_word_8a2c_bounded5_568dc(1,0x20000);
    thunk_set_indexed_status_mask_word_if_below_five_50c82(1,0);
    thunk_set_request_word_8aa8_bounded6_56cda(1,0xc0000);
  }
  thunk_set_request_word_8a48_bounded2_5693e(0,0);
  return;
}

void apply_mode0203_entry_requests(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  if ((DAT_febeb082 & 1) == 0) {
    puVar1 = 0xfebeb800u;
    set_output_request_word((byte)DAT_febeb082 & 1,0x7001);
    clear_direct_output_bank0();
    set_channel_owner_request('\0',2);
    thunk_set_priority_mask_8a9c_bounded2_56c26(0,4);
    thunk_set_secondary_channel_request_bounded5_56e66(0,2);
    thunk_set_secondary_priority_mask_bounded2_56f14(0,4);
    thunk_set_request_word_8a50_bounded5_569ac(0,0);
    thunk_set_request_word_8a2c_bounded5_568dc(0,2);
    thunk_set_indexed_status_mask_word_if_below_five_50c82(0,1);
    thunk_set_request_word_8aa8_bounded6_56cda(0,0xc);
  }
  if (((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x77e))))) & 2) == 0) {
    set_output_request_word('\x01',0x70010000);
    clear_direct_output_bank1();
    set_channel_owner_request('\x01',0x20000);
    thunk_set_priority_mask_8a9c_bounded2_56c26(1,0x40000);
    thunk_set_secondary_channel_request_bounded5_56e66(1,0x20000);
    thunk_set_secondary_priority_mask_bounded2_56f14(1,0x40000);
    thunk_set_request_word_8a50_bounded5_569ac(1,0);
    thunk_set_request_word_8a2c_bounded5_568dc(1,0x20000);
    thunk_set_indexed_status_mask_word_if_below_five_50c82(1,1);
    thunk_set_request_word_8aa8_bounded6_56cda(1,0xc0000);
  }
  thunk_set_request_word_8a48_bounded2_5693e(0,0);
  return;
}
