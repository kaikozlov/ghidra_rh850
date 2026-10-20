#include "common.h"

undefined4 send_bounded_zero_padded_packet_8300e(byte param_1,int param_2,uint param_3)

{
  uint uVar1;
  undefined4 uVar2;
  uint uVar3;
  
  if ((param_1 < DAT_00022abc) && ((param_3 & 0xffff) <= (uint)DAT_00022abd)) {
    uVar3 = (uint)DAT_00022abf;
    for (uVar1 = 0; uVar1 < uVar3; uVar1 = uVar1 + 1 & 0xff) {
      *(undefined4 *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe4c34u + (uint32_t)(uVar1 * 8) * 1u)))) = 0;
      *(undefined4 *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe4c38u + (uint32_t)(uVar1 * 8) * 1u)))) = 0;
    }
    for (uVar1 = 0; uVar1 < (param_3 & 0xffff); uVar1 = uVar1 + 1 & 0xffff) {
      (*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xfebe4c34u + (uint32_t)(uVar1) * 4u)))) = (*((undefined1 *)camry_host_ptr((uint32_t)(uVar1 + param_2))));
    }
    try_packet_callback_then_enqueue_if_busy_82fc0(param_1, (int)((uint32_t)(0xfebe4c34u)),  (uint)(ushort)param_3);
    uVar2 = 0;
  }
  else {
    uVar2 = 1;
  }
  return uVar2;
}

bool wrapper_session_id_not_active_83072(undefined1 param_1)

{
  return session_id_not_active_83570(param_1);
}

void thunk_set_memory_cursor_u32_82288(undefined4 param_1)

{
  set_memory_cursor_u32_82288(param_1);
  return;
}

undefined4 thunk_get_memory_cursor_u32_8228e(void)

{
  return get_memory_cursor_u32_8228e();
}

bool wrapper_memory_range_outside_write_window_83098(undefined4 param_1,undefined1 param_2)

{
  return reject_memory_span_outside_configured_window_98f2c(((undefined *)camry_host_ptr((uint32_t)(param_1))), param_2);
}

undefined4 wrapper_memory_range_overlaps_configured_regions_830a6(undefined4 param_1,undefined1 param_2)

{
  return test_memory_span_overlap_with_configured_ranges_98ef2(((undefined *)camry_host_ptr((uint32_t)(param_1))), param_2);
}

undefined1 wrapper_predispatch_session_command_hook_830c0(undefined1 param_1,undefined4 param_2,undefined2 param_3)

{
  return dispatch_eight_byte_command_reply_98e80(param_1, ((char *)camry_host_ptr((uint32_t)(param_2))), param_3);
}

void dispatch_bounded_pdu_copy_for_enabled_channel_830d0(undefined1 param_1,int *param_2)

{
  uint uVar1;
  uint uVar2;
  uint uVar3;
  
  uVar2 = (uint)*(ushort *)(param_2 + 1);
  if ((uVar2 != 0) && (uVar2 <= DAT_00022abd)) {
    uVar3 = (uint)DAT_00022abf;
    for (uVar1 = 0; uVar1 < uVar3; uVar1 = uVar1 + 1 & 0xff) {
      *(undefined4 *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe4c34u + (uint32_t)(uVar1 * 8) * 1u)))) = 0;
      *(undefined4 *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe4c38u + (uint32_t)(uVar1 * 8) * 1u)))) = 0;
    }
    for (uVar1 = 0; uVar1 < uVar2; uVar1 = uVar1 + 1 & 0xffff) {
      (*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xfebe4c34u + (uint32_t)(uVar1) * 4u)))) = (*((undefined1 *)camry_host_ptr((uint32_t)(*param_2 + uVar1))));
    }
    dispatch_packet_for_enabled_channel_82fec(param_1, (int)((uint32_t)(0xfebe4c34u)),  (*((volatile uint16_t *)((uint8_t *)(param_2) + (4)))));
  }
  return;
}

void dispatch_second_bank_pdu_to_packet_channel_8312e(uint param_1, undefined4 param_2)

{
  uint uVar1;
  
  uVar1 = (uint)DAT_00022abc;
  param_1 = param_1 & 0x7ff;
  if ((uVar1 <= param_1) && (param_1 < (uVar1 * 2 & 0xff))) {
    dispatch_bounded_pdu_copy_for_enabled_channel_830d0(param_1 - uVar1 & 0xff, ((int *)camry_host_ptr((uint32_t)(param_2))));
  }
  return;
}

void return_only_stub_83156(void)

{
  return;
}

uint transmit_canif_pdu_with_f800_prefix_83158(ushort param_1,uchar *param_2,ushort param_3)

{
  F33PduInfo local_c;
  
  local_c.data = camry_host_addr(param_2);
  local_c.length = param_3;
  return canif_transmit(param_1 & 0xff | 0xf800,&local_c);
}

bool is_state_3df4_equal_0f_83172(void)

{
  return DAT_febe3df4 == '\x0f';
}

void initialize_paired_inverted_channel_masks_8317e(int param_1)

{
  byte bVar1;
  byte bVar2;
  uint uVar3;
  uint uVar4;
  
  bVar1 = DAT_febe4fae;
  uVar3 = (uint)DAT_00021865;
  for (uVar4 = 0; uVar4 < uVar3; uVar4 = uVar4 + 1 & 0xff) {
    bVar2 = get_record_u16_mask_low_byte_or_zero_7eb62(uVar4);
    bVar2 = (bVar2 ^ 0xff) & bVar1;
    (*((byte *)camry_host_ptr((uint32_t)(uVar4 + param_1)))) = bVar2;
    (*((byte *)camry_host_ptr((uint32_t)(uVar4 + uVar3 + param_1)))) = bVar2;
    set_paired_channel_bytes_831be(uVar4,bVar2,bVar2);
  }
  return;
}

void set_paired_channel_bytes_831be(uint param_1,undefined1 param_2,undefined1 param_3)

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

void set_second_bank_3dec_channel_byte_831dc(uint param_1,undefined1 param_2)

{
  if ((param_1 & 0xff) < (uint)DAT_00021865) {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe3decu + (uint32_t)((param_1 & 0xff) + (uint)DAT_00021865) * 1u)))) = param_2;
  }
  return;
}

void set_second_bank_3dee_channel_byte_831f0(uint param_1,undefined1 param_2)

{
  if ((param_1 & 0xff) < (uint)DAT_00021865) {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe3deeu + (uint32_t)((param_1 & 0xff) + (uint)DAT_00021865) * 1u)))) = param_2;
  }
  return;
}

void map_channel_mode_to_c0_80_40_callback_83204(byte param_1,char param_2)

{
  undefined4 uVar1;
  
  if ((param_1 < DAT_00021865) &&
     (((uVar1 = 0xc0, param_2 == '\x03' || (uVar1 = 0x80, param_2 == '\x01')) ||
      (uVar1 = 0x40, param_2 == '\x02')))) {
    clear_group_pending_and_reset_pdus_7e29c(param_1,uVar1);
  }
  return;
}

void call_218a4_with_two_bytes_83236(undefined1 param_1,undefined1 param_2)

{
  (*(int (*)())camry_indirect((uint32_t)(PTR_return_only_stub_7be56_000218a4)))(param_1,param_2);
  return;
}

void call_218b0_with_byte_8324a(undefined1 param_1)

{
  (*(int (*)())camry_indirect((uint32_t)(PTR_FUN_000218b0)))(param_1);
  return;
}

void call_218b4_with_byte_8325c(undefined1 param_1)

{
  (*(int (*)())camry_indirect((uint32_t)(PTR_FUN_000218b4)))(param_1);
  return;
}

void call_218b8_with_byte_8326e(undefined1 param_1)

{
  (*(int (*)())camry_indirect((uint32_t)(PTR_FUN_000218b8)))(param_1);
  return;
}

void return_only_stub_83280(void)

{
  return;
}

void set_offset_network_indication_one_83282(char param_1)

{
  set_upper_network_indication_one_79f9a(DAT_0002183d + param_1);
  return;
}

void set_offset_network_indication_three_83298(char param_1)

{
  set_upper_network_indication_three_79fba(DAT_0002183d + param_1);
  return;
}

void clear_offset_network_indication_and_disable_packets_832ae(char param_1)

{
  clear_upper_network_indication_and_notify_79fda(DAT_0002183d + param_1);
  return;
}

void set_offset_network_indication_one_and_notify_832c4(char param_1)

{
  set_upper_network_indication_one_and_notify_7a002(DAT_0002183d + param_1);
  return;
}

void call_21840_with_two_bytes_832da(undefined1 param_1,undefined1 param_2)

{
  (*(int (*)())camry_indirect((uint32_t)(PTR_return_only_stub_7c70e_00021840)))(param_1,param_2);
  return;
}

void return_only_stub_832ee(void)

{
  return;
}

void return_only_stub_832f0(void)

{
  return;
}

void return_only_stub_832f2(void)

{
  return;
}

void initialize_com_tx_pdu_flags_by_mode_832f4(short param_1)

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
      uVar5 = (uint)*(ushort *)(((undefined *)camry_host_ptr((uint32_t)(0x22140u + (uint32_t)(iVar2) * 1u))));
      uVar1 = *(ushort *)(((undefined *)camry_host_ptr((uint32_t)(0x22142u + (uint32_t)(iVar2) * 1u)))) + uVar5;
      bVar3 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe4a39u + (uint32_t)(uVar7 + 3) * 1u))));
      for (; uVar5 < (uVar1 & 0xffff); uVar5 = uVar5 + 1 & 0xffff) {
        uVar6 = '\x01';
        if (((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x22148u + (uint32_t)(uVar5) * 1u)))) & bVar3) != 0) {
          uVar6 = 0x81;
        }
        (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe493eu + (uint32_t)(uVar5) * 1u)))) = uVar6;
      }
      uVar5 = (uint)*(ushort *)(((undefined *)camry_host_ptr((uint32_t)(0x22144u + (uint32_t)(iVar2) * 1u))));
      uVar1 = *(ushort *)(((undefined *)camry_host_ptr((uint32_t)(0x22146u + (uint32_t)(iVar2) * 1u)))) + uVar5;
      bVar3 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe4a42u + (uint32_t)(uVar7) * 1u))));
      for (; uVar5 < (uVar1 & 0xffff); uVar5 = uVar5 + 1 & 0xffff) {
        uVar6 = '\x01';
        if (((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x22148u + (uint32_t)(uVar5) * 1u)))) & bVar3) != 0) {
          uVar6 = 0x81;
        }
        (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe493eu + (uint32_t)(uVar5) * 1u)))) = uVar6;
      }
    }
  }
  else {
    for (; uVar4 < uVar7; uVar4 = uVar4 + 1 & 0xffff) {
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe493eu + (uint32_t)(uVar4) * 1u)))) = '\x01';
    }
  }
  return;
}

void set_com_state_4a47_a5_833cc(void)

{
  DAT_febe4a47 = 0xa5;
  return;
}

void set_com_state_4a47_5a_833d6(void)

{
  DAT_febe4a47 = 0x5a;
  return;
}

undefined4 return_const_1_833e0(void)

{
  return 1;
}

void reset_channel_mode_to_00ff_833e4(uint param_1)

{
  int iVar1;
  short sVar2;
  
  param_1 = param_1 & 0xff;
  iVar1 = param_1 * 0x10;
  sVar2 = *(short *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe492au + (uint32_t)(iVar1) * 1u))));
  if ((((sVar2 == 0x1fe) || (sVar2 == 0x2fd)) || (sVar2 == 0x3fc)) || (sVar2 == 0x5fa)) {
    (*(int (*)())camry_indirect((uint32_t)(((((code *)(uintptr_t)((uint32_t)((uintptr_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x21be4u + (uint32_t)((byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x21be0u + (uint32_t)(param_1) * 1u))))) * 4u)))))))))))))))(param_1,0);
    if (((sVar2 == 0x1fe) || (sVar2 == 0x2fd)) || (sVar2 == 0x5fa)) {
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe4937u + (uint32_t)(iVar1) * 1u)))) = 0x1e;
    }
    *(undefined2 *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe492au + (uint32_t)(iVar1) * 1u)))) = 0xff;
  }
  return;
}

void set_channel_marker_4935_e1_8344e(uint param_1)

{
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe4935u + (uint32_t)((param_1 & 0xff) * 0x10) * 1u)))) = 0xe1;
  return;
}

void transition_channel_mode_03fc_to_02fd_8345e(uint param_1)

{
  int iVar1;
  
  param_1 = param_1 & 0xff;
  iVar1 = param_1 * 0x10;
  if (*(short *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe492au + (uint32_t)(iVar1) * 1u)))) == 0x3fc) {
    (*(int (*)())camry_indirect((uint32_t)(((((code *)(uintptr_t)((uint32_t)((uintptr_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x21be4u + (uint32_t)((byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x21be0u + (uint32_t)(param_1) * 1u))))) * 4u)))))))))))))))(param_1,2);
    *(undefined2 *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe492au + (uint32_t)(iVar1) * 1u)))) = 0x2fd;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe4937u + (uint32_t)(iVar1) * 1u)))) = 0x1e;
  }
  return;
}

void transition_channel_mode_to_03fc_834a2(uint param_1)

{
  int iVar1;
  short sVar2;
  
  param_1 = param_1 & 0xff;
  iVar1 = param_1 * 0x10;
  sVar2 = *(short *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe492au + (uint32_t)(iVar1) * 1u))));
  if (((sVar2 == 0x1fe) || (sVar2 == 0x2fd)) || (sVar2 == 0x5fa)) {
    (*(int (*)())camry_indirect((uint32_t)(((((code *)(uintptr_t)((uint32_t)((uintptr_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x21be4u + (uint32_t)((byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x21be0u + (uint32_t)(param_1) * 1u))))) * 4u)))))))))))))))(param_1,1);
    *(undefined2 *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe492au + (uint32_t)(iVar1) * 1u)))) = 0x3fc;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe4937u + (uint32_t)(iVar1) * 1u)))) = 0x1e;
  }
  return;
}

void request_channel_mode_03fc_when_queries_allow_834f2(uint param_1)

{
  uint32_t puVar1;
  int iVar2;
  uint uVar3;
  
  puVar1 = 0x23dfcu;
  param_1 = param_1 & 0xff;
  iVar2 = test_enabled_record_492c_is_1fe_7eb7c((uint)(byte)param_1);
  if ((iVar2 == 1) && (uVar3 = get_record_compact_state_or_five_7e998(param_1), uVar3 < 2)) {
    (*(int (*)())camry_indirect((uint32_t)(*(((undefined4 *)camry_host_ptr((*((volatile uint32_t *)camry_host_ptr((uint32_t)(puVar1 + (uint)(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(param_1 - 0x221c))))) * 4 + -0x2218))))))))))(param_1,1);
    *(undefined2 *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe492au + (uint32_t)(param_1 * 0x10) * 1u)))) = 0x3fc;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe4934u + (uint32_t)(param_1 * 0x10) * 1u)))) = 0x1e;
  }
  return;
}

void clear_channel_markers_4936_and_call_21bd4_83542(void)

{
  uint uVar1;
  uint uVar2;
  
  uVar2 = (uint)DAT_00021be1;
  for (uVar1 = 0; uVar1 < uVar2; uVar1 = uVar1 + 1 & 0xff) {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe4936u + (uint32_t)(uVar1 * 0x10) * 1u)))) = 0;
  }
  (*(int (*)())camry_indirect((uint32_t)(PTR_return_only_stub_7ed7a_00021bd4)))();
  return;
}

void return_only_stub_8356c(void)

{
  return;
}

void return_only_stub_8356e(void)

{
  return;
}

bool session_id_not_active_83570(char param_1)

{
  if (DAT_febe5005 == '\x01') {
    return DAT_febe5004 != param_1;
  }
  return true;
}

void return_only_stub_83590(void)

{
  return;
}

void return_only_stub_83592(void)

{
  return;
}

void return_only_stub_83594(void)

{
  return;
}

void return_only_stub_83596(void)

{
  return;
}

undefined4 return_const_1_83598(void)

{
  return 1;
}

void initialize_driver_busoff_and_test_flags_8359c(void)

{
  uint uVar1;
  uint uVar2;
  
  uVar2 = (uint)DAT_00022e41;
  for (uVar1 = 0; uVar1 < uVar2; uVar1 = uVar1 + 1 & 0xff) {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe5010u + (uint32_t)(uVar1) * 1u)))) = '<';
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe5013u + (uint32_t)(uVar1) * 1u)))) = 0;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe5016u + (uint32_t)(uVar1) * 1u)))) = 0x5a;
  }
  return;
}

void clear_driver_busoff_observation_latch_835c6(uint param_1)

{
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe5010u + (uint32_t)(param_1 & 0xff) * 1u)))) = '<';
  return;
}

void service_driver_busoff_observation_latches_835d4(void)

{
  char *pcVar1;
  short sVar2;
  uint32_t puVar3;
  uint32_t puVar4;
  uint uVar5;
  uint uVar6;
  
  puVar3 = 0xfebeb800u;
  puVar4 = 0x23dfcu;
  uVar5 = (uint)DAT_00022e41;
  for (uVar6 = 0; uVar6 < uVar5; uVar6 = uVar6 + 1 & 0xff) {
    pcVar1 = ((void *)camry_host_ptr((uint32_t)(puVar4 + uVar6 * 4 + -4000)));
    if ((*pcVar1 == '\0') && (pcVar1[1] == '\0')) {
      if (pcVar1[3] == '\0') {
        if ((pcVar1[2] == '\x01') &&
           (((sVar2 = (*((short *)camry_host_ptr((uint32_t)(puVar3 + uVar6 * 2 + -0x67e0)))), sVar2 == 0x57a8 || (sVar2 == 0x3bc4)
             ) || (sVar2 == 0x3ec1)))) {
          driver_observe_and_clear_bus_off_entry((uchar)uVar6);
        }
        if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(uVar6 - 0x67f0))))) != '<') {
          (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(uVar6 - 0x67f0))))) = '<';
          request_channel_quiesce_and_update_state_84274(uVar6);
          publish_mapped_controller_bus_off_event((uchar)uVar6);
        }
      }
      else if (((*((short *)camry_host_ptr((uint32_t)(puVar3 + uVar6 * 2 + -0x67e0)))) == 0x57a8) ||
              ((*((short *)camry_host_ptr((uint32_t)(puVar3 + uVar6 * 2 + -0x67e0)))) == 0x3bc4)) {
        ((void)(uVar6), return_only_stub_83806());
      }
    }
  }
  return;
}

void set_driver_busoff_observation_latch_8366e(uint param_1)

{
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe5010u + (uint32_t)(param_1 & 0xff) * 1u)))) = 'Z';
  return;
}

undefined1 step_channel_bank_test_attempts_8367c(uint param_1)

{
  byte bVar1;
  byte bVar2;
  int iVar3;
  undefined1 uVar4;
  
  bVar2 = DAT_00022e40;
  param_1 = param_1 & 0xff;
  uVar4 = 1;
  if (((volatile F33DriverChannelSoftwareState *)camry_host_ptr((uint32_t)(0xfebe5020u + (uint32_t)(param_1) * (uint32_t)sizeof(F33DriverChannelSoftwareState))))[0] == stopped_software_state) {
    if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe5016u + (uint32_t)(param_1) * 1u)))) == 'Z') {
      bVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe5013u + (uint32_t)(param_1) * 1u))));
      if (bVar1 < DAT_00022e40) {
        iVar3 = step_shared_bank_test_state_83956(param_1,bVar1);
        if (iVar3 == 1) {
          (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe5016u + (uint32_t)(param_1) * 1u)))) = 0x3c;
        }
        else {
          (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe5013u + (uint32_t)(param_1) * 1u)))) = bVar1 + 1;
          if ((byte)(bVar1 + 1) < bVar2) {
            uVar4 = 2;
          }
          else {
            ((void)(param_1), reload_acceptance_filters_when_count_differs_in_mode_one_84fea());
            uVar4 = 0;
            (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe5016u + (uint32_t)(param_1) * 1u)))) = 0x96;
          }
        }
      }
    }
    else {
      uVar4 = ((int8_t)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe5016u + (uint32_t)(param_1) * 1u))))) != -0x6a;
    }
  }
  return uVar4;
}

void wrapper_return_only_6a420_with_byte_83702(undefined1 param_1)

{
  ((void)(param_1), return_only_stub_6a420());
  return;
}

bool u16_bytes_not_complementary_83710(uint param_1)

{
  return (param_1 & 0xff) + ((int)(param_1 & 0xffff) >> 8) != 0xff;
}

void check_channel_state_integrity_and_dispatch_first_failure_83724(void)

{
  uint32_t puVar1;
  uint32_t puVar2;
  int iVar3;
  int iVar4;
  uint uVar5;
  uint uVar6;
  
  puVar1 = 0xfebeb800u;
  puVar2 = 0x23dfcu;
  uVar5 = (uint)DAT_00022e41;
  uVar6 = 0;
  do {
    if (uVar5 <= uVar6) {
      return;
    }
    if (((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(uVar6 * 4 + -4000))))) == '\0') && ((*((volatile uint8_t *)camry_host_ptr((uint32_t)((puVar2 + uVar6 * 4 + -4000) + (uint32_t)(1))))) == '\0')) {
      iVar3 = u16_bytes_not_complementary_83710((*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + uVar6 * 2 + -0x67e0)))));
      iVar4 = check_and_latch_channel_nibble_integrity_83a04(uVar6);
      if ((iVar3 != 0) || (iVar4 != 1)) {
        request_channel_quiesce_and_update_state_84274(uVar6);
        mark_status_for_mapped_valid_driver_channel_80d54(uVar6);
        return;
      }
    }
    uVar6 = uVar6 + 1 & 0xff;
  } while( true );
}

undefined4 query_channel_status_code_when_state_57a8_8377e(uint param_1)

{
  undefined4 uVar1;
  
  uVar1 = 1;
  if (((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x22e5fu + (uint32_t)((param_1 & 0xff) * 4) * 1u)))) == '\x01') &&
     (((volatile F33DriverChannelSoftwareState *)camry_host_ptr((uint32_t)(0xfebe5020u + (uint32_t)(param_1 & 0xff) * (uint32_t)sizeof(F33DriverChannelSoftwareState))))[0] == running_software_state)) {
    uVar1 = decode_channel_status_bits_18_to_2_4_8_83c50((uint)(byte)param_1);
  }
  return uVar1;
}

void restart_channel_bank_test_unless_terminal_837ac(uint param_1)

{
  if (((int8_t)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe5016u + (uint32_t)(param_1 & 0xff) * 1u))))) != -0x6a) {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe5016u + (uint32_t)(param_1 & 0xff) * 1u)))) = 'Z';
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe5013u + (uint32_t)(param_1 & 0xff) * 1u)))) = 0;
  }
  select_channel_bank_test_state_83c9c((uint)(byte)param_1);
  return;
}

uint driver_observe_and_clear_bus_off_entry(uchar driver_index)

{
  bool bVar1;
  
  bVar1 = ((*((uint *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x22efcu + (uint32_t)((short)(ushort)driver_index * 0x1d) * 4u))))))) >> 3 & 1) == 0;
  if (!bVar1) {
    (*((undefined4 *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x22efcu + (uint32_t)((short)(ushort)driver_index * 0x1d) * 4u))))))) = 0x7ff7;
    set_driver_busoff_observation_latch_8366e((uint)(byte)driver_index);
  }
  return (uint)bVar1;
}

void return_only_stub_83806(void)

{
  return;
}

int enter_keyed_register_test_mode_83808(void)

{
  byte bVar1;
  uint32_t puVar2;
  int iVar3;
  
  puVar2 = 0x23dfcu;
  iVar3 = 1;
  request_global_mode_one_and_poll_bounded_842fe();
  request_global_mode_two_and_poll_ten_times_8509a();
  if (((*((volatile uint *)camry_host_ptr((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x23dfcu + (uint32_t)(-0xdb8) * 1u))))))) & 0xf) == 2) {
    bVar1 = 0;
    do {
      (*((volatile undefined4 *)camry_host_ptr((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x23dfcu + (uint32_t)(-0xd64) * 1u))))))) = 0x7575;
      (*((volatile undefined4 *)camry_host_ptr((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x23dfcu + (uint32_t)(-0xd64) * 1u))))))) = ((uint32_t)(0x8a8au));
      (*((volatile undefined4 *)camry_host_ptr((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x23dfcu + (uint32_t)(-0xd70) * 1u))))))) = 4;
      if (((*((volatile uint *)camry_host_ptr((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x23dfcu + (uint32_t)(-0xd70) * 1u))))))) >> 2 & 1) != 0) {
        iVar3 = 0;
      }
      bVar1 = bVar1 + 1;
    } while ((bVar1 < 0x1a) && (iVar3 != 0));
  }
  return iVar3;
}

int test_indexed_word_bank_alternating_patterns_83862(uint param_1,uint param_2)

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
  return iVar3;
}

bool exit_register_test_mode_and_check_status_838ba(void)

{
  uint32_t puVar1;
  puVar1 = 0x23dfcu;
  (*((undefined4 *)camry_host_ptr((uint32_t)(PTR_DAT_0002308c)))) = 0;
  request_global_mode_one_and_poll_bounded_842fe();
  return ((*((volatile uint *)camry_host_ptr((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x23dfcu + (uint32_t)(-0xdb8) * 1u))))))) & 0xf) != 1;
}

int run_configured_word_bank_pattern_tests_838dc(void)

{
  char cVar1;
  byte bVar2;
  undefined8 uVar3;
  int iVar4;
  int iVar5;
  byte bVar6;
  
  uVar3 = 0x23dfc00000000;
  iVar4 = enter_keyed_register_test_mode_83808();
  if (iVar4 == 0) {
    iVar5 = (int)((ulonglong)uVar3 >> 0x20);
    iVar4 = 0x5a;
    cVar1 = (*((char *)camry_host_ptr((uint32_t)(iVar5 + -0xf74))));
    bVar2 = (*((byte *)camry_host_ptr((uint32_t)(iVar5 + -0xf73))));
    bVar6 = 0;
    while ((bVar6 < bVar2 && (iVar4 == 0x5a))) {
      iVar4 = test_indexed_word_bank_alternating_patterns_83862(bVar6 + cVar1,0x40);
      bVar6 = bVar6 + 1;
    }
    iVar5 = (int)((ulonglong)uVar3 >> 0x20);
    cVar1 = bVar2 + cVar1;
    if (((cVar1 == (*((char *)camry_host_ptr((uint32_t)(iVar5 + -0xf56))))) && (iVar4 == 0x5a)) &&
       (iVar4 = test_indexed_word_bank_alternating_patterns_83862(cVar1,(*((undefined1 *)camry_host_ptr((uint32_t)(iVar5 + -0xf55))))), iVar4 == 0x5a)) {
      iVar4 = 0x96;
    }
  }
  else {
    iVar4 = 0xa5;
  }
  iVar5 = exit_register_test_mode_and_check_status_838ba();
  if (iVar5 != 0) {
    iVar4 = 0xa5;
  }
  return iVar4;
}

undefined4 step_shared_bank_test_state_83956(uint param_1,undefined1 param_2)

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
    iVar4 = ((void)(param_2), run_configured_word_bank_pattern_tests_838dc());
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
  else if ((cVar1 != 'i') && (((int8_t)cVar1) != -0x5b)) {
    uVar5 = (uint)DAT_00022ea4;
    for (uVar2 = 0; uVar2 < uVar5; uVar2 = uVar2 + 1 & 0xff) {
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe5019u + (uint32_t)(uVar2) * 1u)))) = 0x96;
    }
    return 1;
  }
  return 0;
}

bool check_and_latch_channel_nibble_integrity_83a04(uint param_1)

{
  bool bVar1;
  
  bVar1 = ((int8_t)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe501cu + (uint32_t)(param_1 & 0xff) * 1u))))) == -0x5b;
  if (!bVar1) {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe501cu + (uint32_t)(param_1 & 0xff) * 1u)))) = -0x5b;
  }
  return ((int)(uint)(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe5026u + (uint32_t)(param_1 & 0xff) * 1u)))) >> 4) +
         ((byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe5026u + (uint32_t)(param_1 & 0xff) * 1u)))) & 0xf) == 0xf && bVar1;
}

void clear_channel_tx_fifo_status_and_control_83a34(uint param_1)

{
  int iVar1;
  uint uVar2;
  undefined4 *puVar3;
  
  iVar1 = (int)(short)(param_1 & 0xff);
  uVar2 = 0;
  do {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x22f30u + (uint32_t)(iVar1 * 0x1d) * 4u)))) + (uint32_t)(uVar2))))) = 0;
    uVar2 = uVar2 + 1;
  } while (uVar2 < 0x10);
  (*((undefined4 *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x22f2cu + (uint32_t)(iVar1 * 0x1d) * 4u))))))) = 1;
  (*((undefined4 *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x22f2cu + (uint32_t)(iVar1 * 0x1d) * 4u)))) + 4)))) = 1;
  (*((undefined4 *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x22f2cu + (uint32_t)(iVar1 * 0x1d) * 4u)))) + 8)))) = 1;
  (*((undefined4 *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x22f18u + (uint32_t)(iVar1 * 0x1d) * 4u))))))) = 1;
  (*((undefined4 *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x22f24u + (uint32_t)(iVar1 * 0x1d) * 4u))))))) = 1;
  (*((undefined4 *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x22efcu + (uint32_t)(iVar1 * 0x1d) * 4u))))))) = 0;
  puVar3 = ((undefined4 *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x22f0cu + (uint32_t)(iVar1 * 0x1d) * 4u))))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe501cu + (uint32_t)(param_1 & 0xff) * 1u)))) = 0x5a;
  *puVar3 = 0;
  return;
}

void clear_channel_status_and_synchronize_83a88(undefined1 param_1)

{
  clear_channel_tx_fifo_status_and_control_83a34(param_1);
  synchronize_memory_accesses_85938();
  return;
}

void clear_channel_zero_status_and_synchronize_83aa0(void)

{
  clear_channel_status_and_synchronize_83a88(0);
  return;
}

void clear_channel_one_status_and_synchronize_83aae(void)

{
  clear_channel_status_and_synchronize_83a88(1);
  return;
}

void clear_channel_two_status_and_synchronize_83abc(void)

{
  clear_channel_status_and_synchronize_83a88(2);
  return;
}

void clear_global_fifo_status_and_channel_latches_83aca(void)

{
  uint32_t puVar1;
  uint uVar2;
  uint uVar3;
  
  puVar1 = ((uint32_t)(PTR_DAT_00023064));
  uVar2 = 0;
  do {
    (*((volatile uint32_t *)camry_host_ptr((uint32_t)(puVar1 + uVar2 * 4)))) = 1;
    uVar2 = uVar2 + 1;
  } while (uVar2 < 8);
  (*((undefined4 *)camry_host_ptr((uint32_t)(PTR_DAT_00023048)))) = 0;
  uVar3 = (uint)DAT_00022ea4;
  for (uVar2 = 0; uVar2 < uVar3; uVar2 = uVar2 + 1 & 0xff) {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe501cu + (uint32_t)(uVar2) * 1u)))) = 0x5a;
  }
  synchronize_memory_accesses_85938();
  return;
}

void restore_fifo_status_and_check_channel_registers_83b14(uint param_1)

{
  int iVar1;
  int iVar2;
  int iVar3;
  ushort uVar4;
  ushort uVar5;
  uint uVar6;
  int iVar7;
  undefined4 *puVar8;
  
  param_1 = param_1 & 0xff;
  iVar1 = (int)(short)param_1;
  iVar2 = (int)(short)param_1;
  iVar7 = iVar2 * 0x34;
  iVar3 = param_1 * 4;
  uVar4 = *(ushort *)(((undefined *)camry_host_ptr((uint32_t)(0x22ebeu + (uint32_t)(iVar3) * 1u))));
  uVar5 = *(ushort *)(((undefined *)camry_host_ptr((uint32_t)(0x22ebcu + (uint32_t)(iVar3) * 1u))));
  uVar6 = 0;
  do {
    if ((1 << (uVar6 & 0x1f) & 0xffffU & (uint)(uVar4 | uVar5)) == 0) {
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x22f30u + (uint32_t)(iVar1 * 0x1d) * 4u)))) + (uint32_t)(uVar6))))) = 0;
    }
    uVar6 = uVar6 + 1;
  } while (uVar6 < 0x10);
  (*((undefined4 *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x22f2cu + (uint32_t)(iVar1 * 0x1d) * 4u))))))) = *(undefined4 *)(((undefined *)camry_host_ptr((uint32_t)(0x233ccu + (uint32_t)(iVar7) * 1u))));
  (*((undefined4 *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x22f2cu + (uint32_t)(iVar1 * 0x1d) * 4u)))) + 4)))) = *(undefined4 *)(((undefined *)camry_host_ptr((uint32_t)(0x233d0u + (uint32_t)(iVar7) * 1u))));
  (*((undefined4 *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x22f2cu + (uint32_t)(iVar1 * 0x1d) * 4u)))) + 8)))) = *(undefined4 *)(((undefined *)camry_host_ptr((uint32_t)(0x233d4u + (uint32_t)(iVar7) * 1u))));
  (*((undefined4 *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x22f18u + (uint32_t)(iVar1 * 0x1d) * 4u))))))) = 1;
  (*((undefined4 *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x22f24u + (uint32_t)(iVar1 * 0x1d) * 4u))))))) = 1;
  (*((undefined4 *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x22efcu + (uint32_t)(iVar1 * 0x1d) * 4u))))))) = 8;
  (*((undefined4 *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x22f0cu + (uint32_t)(iVar1 * 0x1d) * 4u))))))) = 0;
  if (((((*((ushort *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x22edcu + (uint32_t)(iVar1 * 0x1d) * 4u))))))) !=
         (*(ushort *)(((undefined *)camry_host_ptr((uint32_t)(0x22ebcu + (uint32_t)(iVar3) * 1u)))) & *(ushort *)(((undefined *)camry_host_ptr((uint32_t)(0x22e94u + (uint32_t)(param_1 * 2) * 1u)))))) ||
       (((*((uint *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x22ef4u + (uint32_t)(iVar1 * 0x1d) * 4u))))))) & 0xc7efff0f) !=
        *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0x233c8u + (uint32_t)(iVar7) * 1u)))))) ||
      ((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x22f34u + (uint32_t)(iVar1 * 0x1d) * 4u))))))) & 0xfffff777) !=
       (*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x233b8u + (uint32_t)(iVar2 * 0xd) * 4u)))))) ||
     ((((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x22f34u + (uint32_t)(iVar1 * 0x1d) * 4u)))) + 4)))) & 0xfffff777) !=
        (*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x233bcu + (uint32_t)(iVar2 * 0xd) * 4u)))) ||
       (((*((uint *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x22f34u + (uint32_t)(iVar1 * 0x1d) * 4u)))) + 8)))) & 0xfffff777) !=
        (*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x233c0u + (uint32_t)(iVar2 * 0xd) * 4u)))))) ||
      ((((*((uint *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x22f14u + (uint32_t)(iVar1 * 0x1d) * 4u))))))) & 0x3f01) != 0 ||
       (((*((uint *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x22f20u + (uint32_t)(iVar1 * 0x1d) * 4u))))))) & 0x701) != 0)))))) {
    uVar6 = 0;
    do {
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x22f30u + (uint32_t)(iVar1 * 0x1d) * 4u)))) + (uint32_t)(uVar6))))) = 0;
      uVar6 = uVar6 + 1;
    } while (uVar6 < 0x10);
    (*((undefined4 *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x22f2cu + (uint32_t)(iVar1 * 0x1d) * 4u))))))) = 1;
    (*((undefined4 *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x22f2cu + (uint32_t)(iVar1 * 0x1d) * 4u)))) + 4)))) = 1;
    (*((undefined4 *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x22f2cu + (uint32_t)(iVar1 * 0x1d) * 4u)))) + 8)))) = 1;
    puVar8 = ((undefined4 *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x22efcu + (uint32_t)(iVar1 * 0x1d) * 4u))))));
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe501cu + (uint32_t)(param_1) * 1u)))) = 0x5a;
    *puVar8 = 0;
  }
  return;
}

undefined4 decode_channel_status_bits_18_to_2_4_8_83c50(ushort param_1)

{
  undefined4 uVar1;
  
  if (((*((uint *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x22ef8u + (uint32_t)((short)(param_1 & 0xff) * 0x1d) * 4u))))))) & 0x18) == 0) {
    return 2;
  }
  if (((*((uint *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x22ef8u + (uint32_t)((short)(param_1 & 0xff) * 0x1d) * 4u))))))) & 0x18) == 8) {
    uVar1 = 4;
  }
  else {
    uVar1 = 8;
  }
  return uVar1;
}

void initialize_bank_test_and_integrity_latches_83c72(void)

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

undefined4 return_const_1_83c98(void)

{
  return 1;
}

void select_channel_bank_test_state_83c9c(uint param_1)

{
  char cVar1;
  uint uVar2;
  uint uVar3;
  
  cVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe5019u + (uint32_t)(param_1 & 0xff) * 1u))));
  if ((cVar1 == 'Z') || (((int8_t)cVar1) == -0x6a)) {
    uVar3 = (uint)DAT_00022ea4;
    for (uVar2 = 0; uVar2 < uVar3; uVar2 = uVar2 + 1 & 0xff) {
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe5019u + (uint32_t)(uVar2) * 1u)))) = 0x69;
    }
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe5019u + (uint32_t)(param_1 & 0xff) * 1u)))) = 'Z';
  }
  return;
}

void invalidate_channel_integrity_latch_83cd6(uint param_1)

{
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe501cu + (uint32_t)(param_1 & 0xff) * 1u)))) = 0x5a;
  return;
}

void service_receive_path_one_for_state_57a8_channels_83ce4(void)

{
  undefined8 uVar1;
  uint uVar2;
  uint uVar3;
  
  uVar1 = 0x23dfcfebeb800;
  uVar2 = (uint)DAT_00022e41;
  for (uVar3 = 0; uVar3 < uVar2; uVar3 = uVar3 + 1 & 0xff) {
    if ((*((short *)camry_host_ptr((uint32_t)(uVar3 * 2 + (int)uVar1 + -0x67e0)))) == 0x57a8) {
      dispatch_receive_fifo_by_selector_83eda(uVar3,1);
    }
  }
  return;
}

void forward_received_frame_with_mapped_handle_83d14(uint param_1,ushort param_2,undefined4 *param_3)

{
  int iVar1;
  
  iVar1 = (param_1 & 0xff) * 8;
  enqueue_mapped_message_when_controller_ready_80b42(*(short *)(((undefined *)camry_host_ptr((uint32_t)(0x22e46u + (uint32_t)(iVar1) * 1u)))) +
               ((param_2 & 0xff) - (ushort)(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x22e4bu + (uint32_t)(iVar1) * 1u))))),param_3[1],
               *(undefined1 *)(param_3 + 2),*param_3);
  return;
}

undefined4 drain_channel_receive_fifo_two_classic_or_fd_83d40(uint param_1)

{
  uint8_t stack_record_60[96];
  int iVar1;
  byte bVar2;
  uint uVar3;
  undefined8 uVar4;
  int iVar5;
  uint uVar6;
  undefined4 uVar7;
  uint uVar8;
  uint uVar9;
  undefined *puVar10;
  uint32_t puStack_20;
  
  uVar4 = 0x23dfc00000000;
  puStack_20 = ((uint32_t)(((uint32_t *)(stack_record_60))));
  param_1 = param_1 & 0xff;
  iVar1 = (int)(short)param_1;
  uVar7 = 1;
  (*((undefined4 *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x22f2cu + (uint32_t)(iVar1 * 0x1d) * 4u)))) + 8)))) = 0x15;
  puVar10 = ((void *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x22f40u + (uint32_t)(iVar1 * 0x1d) * 4u)))))));
  for (uVar9 = ((*((uint *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x22f2cu + (uint32_t)(iVar1 * 0x1d) * 4u)))) + 8)))) & 0xff00) >> 8; uVar9 != 0;
      uVar9 = uVar9 - 1) {
    uVar8 = *(uint *)(puVar10 + 0x100);
    uVar6 = *(uint *)(puVar10 + 0x104);
    if ((*(uint *)(puVar10 + 0x108) >> 2 & 1) == 0) {
      ((uint32_t *)(stack_record_60))[0] = *(uint *)(puVar10 + 0x10c);
      stack_record_60[72] = (byte)(uVar6 >> 0x1c);
      ((uint32_t *)(stack_record_60))[1] = *(uint *)(puVar10 + 0x110);
      (*((undefined4 *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x22f38u + (uint32_t)(iVar1 * 0x1d) * 4u)))) + 8)))) = 0xff;
      (*((uint32_t *)(stack_record_60 + 68))) = uVar8 & 0x9fffffff;
    }
    else {
      iVar5 = (int)((ulonglong)uVar4 >> 0x20);
      bVar2 = (*((byte *)camry_host_ptr((uint32_t)(param_1 + iVar5 + -0xf45))));
      for (uVar3 = 0; uVar3 < bVar2; uVar3 = uVar3 + 1 & 0xff) {
        ((uint32_t *)(stack_record_60))[uVar3] = (*((uint *)camry_host_ptr((uint32_t)((int)camry_host_addr((puVar10 + 0x100)) + (uVar3 + 3) * 4))));
      }
      (*((undefined4 *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x22f38u + (uint32_t)(iVar1 * 0x1d) * 4u)))) + 8)))) = 0xff;
      (*((uint32_t *)(stack_record_60 + 68))) = uVar8 & 0x9fffffff | 0x40000000;
      stack_record_60[72] = (*((byte *)camry_host_ptr((uint32_t)((uVar6 >> 0x1c) + iVar5 + -0xfd4))));
    }
    forward_received_frame_with_mapped_handle_83d14(param_1,uVar6 >> 0x10 & 0xff,&puStack_20);
    uVar7 = 0;
  }
  return uVar7;
}

undefined4 drain_global_receive_fifo_frames_83e0c(uint param_1)

{
  uint8_t stack_record_60[96];
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
  uint32_t puStack_20;
  
  uVar5 = 0x23dfc00000000;
  puStack_20 = ((uint32_t)(((uint32_t *)(stack_record_60))));
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
      ((uint32_t *)(stack_record_60))[0] = puVar1[3];
      stack_record_60[72] = (byte)(uVar7 >> 0x1c);
      ((uint32_t *)(stack_record_60))[1] = puVar1[4];
      (*((undefined4 *)camry_host_ptr((uint32_t)((*((volatile int32_t *)camry_host_ptr((uint32_t)(iVar6 + -0xd94)))) + iVar2)))) = 0xff;
      (*((uint32_t *)(stack_record_60 + 68))) = uVar9 & 0x9fffffff;
    }
    else {
      bVar3 = (*((byte *)camry_host_ptr((uint32_t)(param_1 + iVar6 + -0xf48))));
      for (uVar4 = 0; uVar4 < bVar3; uVar4 = uVar4 + 1 & 0xff) {
        ((uint32_t *)(stack_record_60))[uVar4] = puVar1[uVar4 + 3];
      }
      (*((undefined4 *)camry_host_ptr((uint32_t)((*((volatile int32_t *)camry_host_ptr((uint32_t)(iVar6 + -0xd94)))) + iVar2)))) = 0xff;
      (*((uint32_t *)(stack_record_60 + 68))) = uVar9 & 0x9fffffff | 0x40000000;
      stack_record_60[72] = (*((byte *)camry_host_ptr((uint32_t)((uVar7 >> 0x1c) + iVar6 + -0xfd4))));
    }
    forward_received_frame_with_mapped_handle_83d14(param_1,uVar7 >> 0x10 & 0xff,&puStack_20);
    uVar8 = 0;
  }
  return uVar8;
}

undefined4 dispatch_receive_fifo_by_selector_83eda(undefined1 param_1,char param_2)

{
  if (param_2 == '\0') {
    return drain_channel_receive_fifo_two_classic_or_fd_83d40((uint)(byte)param_1);
  }
  return drain_global_receive_fifo_frames_83e0c(param_1);
}

void service_channel_receive_or_status_and_sync_83ef2(ushort param_1)

{
  int iVar1;
  
  param_1 = param_1 & 0xff;
  if (((*((uint *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x22ef8u + (uint32_t)((short)param_1 * 0x1d) * 4u))))))) & 7) == 0) {
    iVar1 = dispatch_receive_fifo_by_selector_83eda(param_1,0);
    if (iVar1 != 0) {
      restore_fifo_status_and_check_channel_registers_83b14(param_1);
    }
  }
  else {
    clear_channel_tx_fifo_status_and_control_83a34((uint)(byte)param_1);
  }
  synchronize_memory_accesses_85938();
  return;
}

void service_channel_one_receive_and_sync_83f30(void)

{
  service_channel_receive_or_status_and_sync_83ef2(1);
  return;
}

void initialize_driver_channels_and_registers_83f3e(void)

{
  uint32_t puVar1;
  uint32_t puVar2;
  uint uVar3;
  int iVar4;
  uint uVar5;
  
  puVar1 = 0xfebeb800u;
  puVar2 = 0x23dfcu;
  uVar5 = (uint)DAT_00022e41;
  for (uVar3 = 0; uVar3 < uVar5; uVar3 = uVar3 + 1 & 0xff) {
    ((volatile F33DriverChannelSoftwareState *)camry_host_ptr((uint32_t)(0xfebe5020u + (uint32_t)(uVar3) * (uint32_t)sizeof(F33DriverChannelSoftwareState))))[0] = uninitialized;
  }
  invalidate_all_can_transmit_route_slots_850c2();
  initialize_driver_busoff_and_test_flags_8359c();
  iVar4 = initialize_can_registers_after_global_status_bit3_clears_84652();
  uVar3 = 0;
  if (iVar4 == 0) {
    for (; uVar3 < uVar5; uVar3 = uVar3 + 1 & 0xff) {
      if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(uVar3 * 4 + -4000))))) == '\0') {
        (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + uVar3 * 2 + -0x67e0)))) = 0x6d92;
      }
    }
  }
  return;
}

undefined4 configure_channel_and_advance_state_to_6b94_83f9a(uint param_1)

{
  int iVar1;
  
  param_1 = param_1 & 0xff;
  if (((volatile F33DriverChannelSoftwareState *)camry_host_ptr((uint32_t)(0xfebe5020u + (uint32_t)(param_1) * (uint32_t)sizeof(F33DriverChannelSoftwareState))))[0] == initialized) {
    iVar1 = configure_channel_only_in_global_and_channel_reset_modes_84760(param_1);
    if (iVar1 != 0) {
      return 2;
    }
    iVar1 = ((void)(param_1), return_const_1_83c98());
    if (iVar1 != 1) {
      return 1;
    }
    clear_driver_busoff_observation_latch_835c6(param_1);
    ((void)(param_1), reload_acceptance_filters_when_count_differs_in_mode_one_84fea());
    ((volatile F33DriverChannelSoftwareState *)camry_host_ptr((uint32_t)(0xfebe5020u + (uint32_t)(param_1) * (uint32_t)sizeof(F33DriverChannelSoftwareState))))[0] = stopped_software_state;
  }
  else {
    if (((volatile F33DriverChannelSoftwareState *)camry_host_ptr((uint32_t)(0xfebe5020u + (uint32_t)(param_1) * (uint32_t)sizeof(F33DriverChannelSoftwareState))))[0] != stopped_software_state) {
      return 1;
    }
    restart_channel_bank_test_unless_terminal_837ac(param_1);
  }
  return 0;
}

uint driver_request_channel_start_stop(uchar driver_index,uchar request)

{
  camry_write32((camry_sp - 4u) & ~3u, camry_gpr[28]);
  camry_write32((camry_sp - 8u) & ~3u, camry_gpr[29]);
  camry_write32((camry_sp - 12u) & ~3u, camry_gpr[31]);
  camry_sp -= 12u;
  camry_gpr[3] = camry_sp;

  F33DriverChannelSoftwareState FVar1;
  undefined4 uVar2;
  int iVar3;
  uint uVar4;
  F33DriverChannelSoftwareState *pFVar5;
  
  uVar4 = (uint)driver_index;
  if (request == '\0') {
    FVar1 = ((volatile F33DriverChannelSoftwareState *)camry_host_ptr((uint32_t)(0xfebe5020u + (uint32_t)(uVar4) * (uint32_t)sizeof(F33DriverChannelSoftwareState))))[0];
    pFVar5 = ((volatile F33DriverChannelSoftwareState *)camry_host_ptr((uint32_t)(0xfebe5020u + (uint32_t)(uVar4) * (uint32_t)sizeof(F33DriverChannelSoftwareState))));
    if (((FVar1 != stopped_software_state) && (FVar1 != stop_pending)) &&
       (FVar1 != recovery_pending)) {
      { uint32_t camry_return_value = (1); if (camry_halted) return 0; camry_gpr[28] = camry_read32((camry_sp + 8u) & ~3u); camry_gpr[29] = camry_read32((camry_sp + 4u) & ~3u); camry_gpr[31] = camry_read32((camry_sp + 0u) & ~3u); camry_sp += 12u; camry_gpr[3] = camry_sp; return camry_return_value; }
    }
    *pFVar5 = start_pending;
    (camry_gpr[28] = uVar4, camry_gpr[29] = camry_host_addr(pFVar5), camry_gpr[6] = uVar4, camry_gpr[31] = 0x84038u, clear_driver_busoff_observation_latch_835c6)(uVar4);
    iVar3 = (camry_gpr[28] = uVar4, camry_gpr[29] = camry_host_addr(pFVar5), camry_gpr[6] = uVar4, camry_gpr[31] = 0x8403eu, enter_channel_mode_zero_after_global_activation_84a5e)(uVar4);
    if (iVar3 != 0) {
      { uint32_t camry_return_value = (0); if (camry_halted) return 0; camry_gpr[28] = camry_read32((camry_sp + 8u) & ~3u); camry_gpr[29] = camry_read32((camry_sp + 4u) & ~3u); camry_gpr[31] = camry_read32((camry_sp + 0u) & ~3u); camry_sp += 12u; camry_gpr[3] = camry_sp; return camry_return_value; }
    }
    FVar1 = running_software_state;
    uVar2 = 2;
  }
  else {
    if (request != '\x01') {
      { uint32_t camry_return_value = (1); if (camry_halted) return 0; camry_gpr[28] = camry_read32((camry_sp + 8u) & ~3u); camry_gpr[29] = camry_read32((camry_sp + 4u) & ~3u); camry_gpr[31] = camry_read32((camry_sp + 0u) & ~3u); camry_sp += 12u; camry_gpr[3] = camry_sp; return camry_return_value; }
    }
    FVar1 = ((volatile F33DriverChannelSoftwareState *)camry_host_ptr((uint32_t)(0xfebe5020u + (uint32_t)(uVar4) * (uint32_t)sizeof(F33DriverChannelSoftwareState))))[0];
    pFVar5 = ((volatile F33DriverChannelSoftwareState *)camry_host_ptr((uint32_t)(0xfebe5020u + (uint32_t)(uVar4) * (uint32_t)sizeof(F33DriverChannelSoftwareState))));
    if ((FVar1 != start_pending) && (FVar1 != running_software_state)) {
      if (FVar1 == stopped_software_state) {
        { uint32_t camry_return_value = (0); if (camry_halted) return 0; camry_gpr[28] = camry_read32((camry_sp + 8u) & ~3u); camry_gpr[29] = camry_read32((camry_sp + 4u) & ~3u); camry_gpr[31] = camry_read32((camry_sp + 0u) & ~3u); camry_sp += 12u; camry_gpr[3] = camry_sp; return camry_return_value; }
      }
      if (FVar1 == stop_pending) {
        { uint32_t camry_return_value = (0); if (camry_halted) return 0; camry_gpr[28] = camry_read32((camry_sp + 8u) & ~3u); camry_gpr[29] = camry_read32((camry_sp + 4u) & ~3u); camry_gpr[31] = camry_read32((camry_sp + 0u) & ~3u); camry_sp += 12u; camry_gpr[3] = camry_sp; return camry_return_value; }
      }
      if (FVar1 == recovery_pending) {
        { uint32_t camry_return_value = (0); if (camry_halted) return 0; camry_gpr[28] = camry_read32((camry_sp + 8u) & ~3u); camry_gpr[29] = camry_read32((camry_sp + 4u) & ~3u); camry_gpr[31] = camry_read32((camry_sp + 0u) & ~3u); camry_sp += 12u; camry_gpr[3] = camry_sp; return camry_return_value; }
      }
      { uint32_t camry_return_value = (1); if (camry_halted) return 0; camry_gpr[28] = camry_read32((camry_sp + 8u) & ~3u); camry_gpr[29] = camry_read32((camry_sp + 4u) & ~3u); camry_gpr[31] = camry_read32((camry_sp + 0u) & ~3u); camry_sp += 12u; camry_gpr[3] = camry_sp; return camry_return_value; }
    }
    *pFVar5 = stop_pending;
    if (((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x22e5fu + (uint32_t)(uVar4 * 4) * 1u)))) == '\0') && ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x22e5eu + (uint32_t)(uVar4 * 4) * 1u)))) == '\x01')) {
      (camry_gpr[28] = uVar4, camry_gpr[29] = camry_host_addr(pFVar5), camry_gpr[6] = uVar4, camry_gpr[31] = 0x8408cu, driver_observe_and_clear_bus_off_entry)(driver_index);
    }
    iVar3 = (camry_gpr[28] = uVar4, camry_gpr[29] = camry_host_addr(pFVar5), camry_gpr[6] = uVar4, camry_gpr[31] = 0x84092u, cancel_pending_channel_transmits_before_mode_one_84b74)(uVar4);
    if (iVar3 != 0) {
      { uint32_t camry_return_value = (0); if (camry_halted) return 0; camry_gpr[28] = camry_read32((camry_sp + 8u) & ~3u); camry_gpr[29] = camry_read32((camry_sp + 4u) & ~3u); camry_gpr[31] = camry_read32((camry_sp + 0u) & ~3u); camry_sp += 12u; camry_gpr[3] = camry_sp; return camry_return_value; }
    }
    FVar1 = stopped_software_state;
    uVar2 = 3;
  }
  *pFVar5 = FVar1;
  ((void)(uVar4), (void)(uVar2), return_only_stub_7fb5c());
  { uint32_t camry_return_value = (0); if (camry_halted) return 0; camry_gpr[28] = camry_read32((camry_sp + 8u) & ~3u); camry_gpr[29] = camry_read32((camry_sp + 4u) & ~3u); camry_gpr[31] = camry_read32((camry_sp + 0u) & ~3u); camry_sp += 12u; camry_gpr[3] = camry_sp; return camry_return_value; }
}
