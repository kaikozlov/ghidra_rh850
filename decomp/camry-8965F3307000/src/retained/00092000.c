#include "common.h"

undefined4 notify_application_session_change_return_zero_9202a(undefined1 param_1,undefined1 param_2)

{
  notify_application_and_6a156_session_change_8b0de(param_1,param_2);
  return 0;
}

undefined4 return_const_0_9203c(void)

{
  return 0;
}

undefined4 return_const_0_92040(void)

{
  return 0;
}

undefined4 notify_application_session_change_wrapper_92044(undefined1 param_1,undefined1 param_2)

{
  return notify_application_session_change_return_zero_9202a(param_1,param_2);
}

undefined4 return_zero_via_two_byte_hook_92054(undefined1 param_1,undefined1 param_2)

{
  return ((void)(param_1), (void)(param_2), return_const_0_9203c());
}

void lookup_session_three_timing_values_92064(uchar param_1,ushort *param_2,ushort *param_3,ushort *param_4)

{
  int iVar1;
  int iVar2;
  short sVar3;
  int iVar4;
  
  iVar4 = 0;
  do {
    sVar3 = (short)iVar4;
    if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)((uint32_t)(0x26122u + (uint32_t)(sVar3) * (uint32_t)sizeof(F33DcmSessionTimingRow)) + (uint32_t)(0) * (uint32_t)sizeof(F33DcmSessionTimingRow) + (uint32_t)offsetof(F33DcmSessionTimingRow, session))))) == param_1) {
      *param_2 = (*((volatile uint16_t *)camry_host_ptr((uint32_t)((uint32_t)(0x26122u + (uint32_t)(sVar3) * (uint32_t)sizeof(F33DcmSessionTimingRow)) + (uint32_t)(0) * (uint32_t)sizeof(F33DcmSessionTimingRow) + (uint32_t)offsetof(F33DcmSessionTimingRow, response_timing_a_raw)))));
      *param_3 = (*((volatile uint16_t *)camry_host_ptr((uint32_t)((uint32_t)(0x26122u + (uint32_t)(sVar3) * (uint32_t)sizeof(F33DcmSessionTimingRow)) + (uint32_t)(0) * (uint32_t)sizeof(F33DcmSessionTimingRow) + (uint32_t)offsetof(F33DcmSessionTimingRow, transport_timing_b_raw)))));
      *param_4 = (*((volatile uint16_t *)camry_host_ptr((uint32_t)((uint32_t)(0x26122u + (uint32_t)(sVar3) * (uint32_t)sizeof(F33DcmSessionTimingRow)) + (uint32_t)(0) * (uint32_t)sizeof(F33DcmSessionTimingRow) + (uint32_t)offsetof(F33DcmSessionTimingRow, transport_timing_c_raw)))));
      return;
    }
    iVar2 = iVar4 + 1;
    iVar1 = iVar4 + -3;
    iVar4 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  return;
}

undefined4 set_matching_connection_state_zero_92094(undefined1 param_1)

{
  return set_dcm_communication_mode_zero_and_return_success_91826(param_1);
}

undefined4 set_matching_connection_state_one_920a2(undefined1 param_1)

{
  return set_dcm_communication_mode_one_and_return_success_91838(param_1);
}

undefined4 set_matching_connection_state_two_920b0(undefined1 param_1)

{
  return set_dcm_communication_mode_two_and_return_success_9184a(param_1);
}

uint dcm_start_of_reception
               (ushort receive_id,F33PduInfo *first_frame,ushort total_length,ushort *available)

{
  uint32_t puVar1;
  int iVar2;
  undefined4 *puVar3;
  uint uVar4;
  
  puVar1 = 0x23dfcu;
  uVar4 = 0;
  while (receive_id != (*((volatile uint16_t *)camry_host_ptr((uint32_t)((uint32_t)(0x25ee8u + (uint32_t)((short)(ushort)uVar4) * (uint32_t)sizeof(F33DcmReceiveRoute)) + (uint32_t)(0) * (uint32_t)sizeof(F33DcmReceiveRoute) + (uint32_t)offsetof(F33DcmReceiveRoute, receive_id)))))) {
    uVar4 = uVar4 + 1;
    if (2 < uVar4) {
      return 1;
    }
  }
  iVar2 = is_dcm_route_communication_mode_blocked_9185c(uVar4,1);
  if (iVar2 != 1) {
    return 1;
  }
  iVar2 = dcm_get_receive_slot_abort_pending_93f02(uVar4);
  if (iVar2 != 0) {
    return 1;
  }
  if (total_length == 0) {
    if (camry_host_addr((available))!= 0) {
      *available = (ushort)(*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + uVar4 * 8 + 0x2094))));
    }
    return 0;
  }
  if ((uint)total_length <= ((*((uint *)camry_host_ptr((uint32_t)(puVar1 + uVar4 * 8 + 0x2094)))) & 0xffff)) {
    puVar3 = ((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + uVar4 * 8 + 0x2094)));
    uVar4 = dcm_claim_receive_slot((ushort)uVar4);
    if (uVar4 != 1) {
      return 1;
    }
    if (camry_host_addr((available))!= 0) {
      *available = (ushort)*puVar3;
    }
    dcm_arm_software_timer('\0',(*((uint *)camry_host_ptr((uint32_t)(puVar1 + 0x2088)))));
    return 0;
  }
  return 3;
}

uint dcm_copy_receive_data(ushort receive_id,F33PduInfo *chunk,ushort *available)

{
  uint32_t puVar1;
  int iVar2;
  int iVar3;
  uint uVar4;
  undefined4 uVar5;
  uint uVar6;
  
  puVar1 = 0x23dfcu;
  uVar6 = 1;
  iVar2 = dcm_find_receive_slot_by_receive_id_93f0e(receive_id);
  if ((iVar2 != 0xffff) && (iVar3 = dcm_get_slot_receiving_flag_93e32(iVar2), iVar3 == 1)) {
    dcm_cancel_software_timer('\0');
    iVar3 = is_dcm_route_communication_mode_blocked_9185c(iVar2,1);
    if ((iVar3 == 1) && (uVar4 = dcm_get_receive_slot_remaining_capacity_940ae(iVar2), chunk->length <= uVar4)) {
      uVar6 = dcm_append_receive_chunk((ushort)iVar2,chunk,available);
    }
    else {
      uVar5 = dcm_get_slot_inactivity_participant_93f5a(iVar2);
      dcm_reset_receive_slot_and_optionally_shared_response_93c9a(iVar2,1);
      arm_dcm_inactivity_timer_if_no_other_participant_91f26(iVar2,uVar5);
      iVar2 = dcm_receiving_slot_count_exceeds_phase_allowance_93a8c();
      if (iVar2 != 1) {
        return 1;
      }
    }
    dcm_arm_software_timer('\0',(*((uint *)camry_host_ptr((uint32_t)(puVar1 + 0x2088)))));
  }
  return uVar6;
}

uint32_t dcm_receive_indication(ushort receive_id,uchar result)

{
  uint32_t camry_r10_result;
  uint32_t puVar1;
  uchar timer_slot;
  ushort uVar2;
  int iVar3;
  int iVar4;
  uint uVar5;
  undefined4 uVar6;
  
  puVar1 = 0x23dfcu;
  iVar3 = (camry_r10_result = dcm_find_receive_slot_by_receive_id_93f0e(receive_id));
  if (iVar3 == 0xffff) {
    return camry_r10_result;
  }
  iVar4 = (camry_r10_result = dcm_get_slot_receiving_flag_93e32(iVar3));
  if (iVar4 != 1) {
    return camry_r10_result;
  }
  dcm_cancel_software_timer('\0');
  iVar4 = (camry_r10_result = is_dcm_route_communication_mode_blocked_9185c(iVar3,1));
  if ((iVar4 == 1) && (result == '\0')) {
    uVar5 = (camry_r10_result = dcm_arbitrate_completed_receive((ushort)iVar3));
    if (uVar5 - 0x10 < 4) {
      update_dcm_connection_activity_requests_91938(iVar3,0);
      dcm_set_pending_dispatch_receive_slot_94008(iVar3);
      (camry_r10_result = set_dcm_phase_and_prepare_response_queue_when_not_active_91f72(2));
      dcm_set_pending_transport_accepted_93c94(0);
      uVar2 = (camry_r10_result = dcm_select_response_deadline('\0',uVar5 != 0x13));
      dcm_arm_software_timer('\x04',(uint)uVar2);
      uVar5 = (camry_r10_result = dcm_get_overall_request_timeout());
      dcm_arm_software_timer('\x02',uVar5);
      iVar4 = (camry_r10_result = dcm_receiving_slot_count_exceeds_phase_allowance_93a8c());
      if (iVar4 == 1) {
        dcm_arm_software_timer('\0',(*((uint *)camry_host_ptr((uint32_t)(puVar1 + 0x2088)))));
      }
      timer_slot = '\x06';
      uVar5 = (uint)(*((ushort *)camry_host_ptr((uint32_t)(puVar1 + (*((volatile int16_t *)camry_host_ptr((uint32_t)(puVar1 + (short)(ushort)iVar3 * 0xc + 0x20ec)))) * 0x14 +
                               0x20ce))));
      goto LAB_000922a2;
    }
  }
  else {
    uVar6 = (camry_r10_result = dcm_get_slot_inactivity_participant_93f5a(iVar3));
    dcm_reset_receive_slot_and_optionally_shared_response_93c9a(iVar3,1);
    (camry_r10_result = arm_dcm_inactivity_timer_if_no_other_participant_91f26(iVar3,uVar6));
  }
  iVar3 = (camry_r10_result = dcm_receiving_slot_count_exceeds_phase_allowance_93a8c());
  if (iVar3 != 1) {
    return camry_r10_result;
  }
  uVar5 = (*((uint *)camry_host_ptr((uint32_t)(puVar1 + 0x2088))));
  timer_slot = '\0';
LAB_000922a2:
  dcm_arm_software_timer(timer_slot,uVar5);
  return camry_r10_result;
}

void dcm_run_scheduled_request(void)

{
  undefined4 uVar1;
  int iVar2;
  
  thunk_push_priority_mask_and_raise_to_ff00_6a45e();
  uVar1 = dcm_get_pending_dispatch_receive_slot_9400e();
  iVar2 = dcm_get_request_phase_92624();
  thunk_pop_and_restore_priority_mask_stack_6a4c4();
  if (iVar2 == 2) {
    dcm_set_current_dispatch_receive_slot_93c66(uVar1);
    dcm_dispatch_retained_receive((ushort)uVar1);
  }
  else {
    thunk_push_priority_mask_and_raise_to_ff00_6a45e();
    dcm_reset_receive_slot_and_optionally_shared_response_93c9a(uVar1,1);
    thunk_pop_and_restore_priority_mask_stack_6a4c4();
  }
  return;
}

void return_only_stub_922e8(void)

{
  return;
}

uint dcm_post_receive_dispatch_after_delay(void)

{
  dcm_invalidate_queued_event('\0','\0');
  return dcm_enqueue_event('\0');
}

uint32_t dcm_abort_and_reset_selected_receiving_slots_92300(void)

{
  uint32_t camry_r10_result;
  undefined8 uVar1;
  int iVar2;
  undefined4 uVar3;
  int iVar4;
  ushort auStack_1e [7];
  
  uVar1 = 0x23dfc00000000;
  auStack_1e[0] = 0;
  auStack_1e[2] = 0;
  auStack_1e[1] = 0;
  thunk_push_priority_mask_and_raise_to_ff00_6a45e();
  uVar3 = (camry_r10_result = dcm_get_request_phase_92624());
  dcm_collect_receiving_slots_and_mark_abort_pending_93f66(camry_host_addr(auStack_1e + 1), auStack_1e, uVar3);
  thunk_pop_and_restore_priority_mask_stack_6a4c4();
  for (iVar4 = 0;
      (int)(iVar4 - (uint)auStack_1e[0]) < 0 !=
      (iVar4 < 0 && -1 < (int)(iVar4 - (uint)auStack_1e[0])); iVar4 = iVar4 + 1) {
    iVar2 = (int)((ulonglong)uVar1 >> 0x20);
    if ((*((char *)camry_host_ptr((uint32_t)((*((volatile int16_t *)camry_host_ptr((uint32_t)((short)auStack_1e[iVar4 * 2U + 2] * 0xc + iVar2 + 0x20ec)))) * 0x14 +
                  iVar2 + 0x20d5)))) == '\x01') {
      (camry_r10_result = call_configured_receive_abort_callback_923de(auStack_1e[iVar4 * 2U + 1]));
    }
    uVar3 = (camry_r10_result = dcm_get_slot_inactivity_participant_93f5a(auStack_1e[iVar4 * 2U + 2]));
    dcm_reset_receive_slot_and_optionally_shared_response_93c9a(auStack_1e[iVar4 * 2U + 2],1);
    (camry_r10_result = arm_dcm_inactivity_timer_if_no_other_participant_91f26(auStack_1e[iVar4 * 2U + 2],uVar3));
    dcm_set_receive_slot_abort_pending_93ef6(auStack_1e[iVar4 * 2U + 2],0);
  }
  return camry_r10_result;
}

uint32_t dcm_abort_next_queued_receive_slot_9238c(void)

{
  uint32_t camry_r10_result;
  short *psVar1;
  uint32_t puVar2;
  undefined4 uVar3;
  
  puVar2 = 0x23dfcu;
  thunk_push_priority_mask_and_raise_to_ff00_6a45e();
  uVar3 = (camry_r10_result = dcm_dequeue_receive_slot_from_two_entry_ring_9407c());
  thunk_pop_and_restore_priority_mask_stack_6a4c4();
  psVar1 = ((short *)camry_host_ptr((uint32_t)(puVar2 + (short)uVar3 * 0xc + 0x20ec)));
  (camry_r10_result = call_configured_receive_abort_callback_923de((*((undefined2 *)camry_host_ptr((uint32_t)((uint)(ushort)psVar1[2] * 0xc +
                 (*((volatile int32_t *)camry_host_ptr((uint32_t)((*((volatile int32_t *)camry_host_ptr((uint32_t)((uint)(ushort)psVar1[1] * 4 +
                                  (*((volatile int32_t *)camry_host_ptr((uint32_t)(puVar2 + *psVar1 * 0x14 + 0x20c4)))))))) + 4)))) + 6))))));
  dcm_set_receive_slot_abort_pending_93ef6(uVar3,0);
  return camry_r10_result;
}

undefined4 call_configured_receive_abort_callback_923de(undefined2 param_1)

{
  return call_21cd8_with_prefixed_u16_81e90(param_1);
}

void clear_two_locked_state_words_923ec(void)

{
  int iVar1;
  uint uVar2;
  uint32_t puVar3;
  puVar3 = 0xfebeb800u;
  thunk_push_priority_mask_and_raise_to_ff00_6a45e();
  uVar2 = 0;
  do {
    iVar1 = uVar2 * 4;
    uVar2 = uVar2 + 1;
    (*((undefined4 *)camry_host_ptr((uint32_t)(puVar3 + iVar1 + -0x5eac)))) = 0;
  } while (uVar2 < 2);
  thunk_pop_and_restore_priority_mask_stack_6a4c4();
  return;
}

uint dcm_read_security_bitmap_level(uchar *level)

{
  uint *puVar1;
  int iVar2;
  uint uVar3;
  uint32_t puVar4;
  uint uVar5;
  uint auStack_10 [2];
  
  puVar4 = 0xfebeb800u;
  *level = '\0';
  thunk_push_priority_mask_and_raise_to_ff00_6a45e();
  uVar3 = 0;
  do {
    iVar2 = uVar3 * 4;
    puVar1 = auStack_10 + uVar3;
    uVar3 = uVar3 + 1;
    *puVar1 = (*((uint *)camry_host_ptr((uint32_t)(puVar4 + iVar2 + -0x5eac))));
  } while (uVar3 < 2);
  thunk_pop_and_restore_priority_mask_stack_6a4c4();
  uVar3 = 0;
  do {
    uVar5 = 0;
    do {
      puVar1 = auStack_10 + uVar3;
      if ((*puVar1 & 1) != 0) {
        *level = (char)uVar5 + (char)uVar3 * ' ' + '\x01';
        break;
      }
      uVar5 = uVar5 + 1;
      *puVar1 = *puVar1 >> 1;
    } while (uVar5 < 0x20);
    uVar3 = uVar3 + 1;
    if (1 < uVar3) {
      return 0;
    }
  } while( true );
}

void dcm_publish_security_level(uchar level)

{
  uint8_t stack_record_11[17];
  uint uVar1;
  uint uVar2;
  uint32_t puVar3;
  uint uVar4;
  
  puVar3 = 0xfebeb800u;
  uVar4 = (uint)level;
  stack_record_11[0] = '\0';
  dcm_read_security_bitmap_level(((uint8_t *)(stack_record_11)));
  uVar2 = 0;
  do {
    uVar1 = uVar2 + 1;
    ((int32_t *)((stack_record_11 + 1)))[uVar2] = 0;
    uVar2 = uVar1;
  } while (uVar1 < 2);
  if (uVar4 < 0x40) {
    if (uVar4 != 0) {
      ((int32_t *)((stack_record_11 + 1)))[(int)(uVar4 - 1 & 0xff) >> 5] = 1 << (uVar4 - 1 & 0x1f);
    }
    thunk_push_priority_mask_and_raise_to_ff00_6a45e();
    uVar2 = 0;
    do {
      uVar1 = uVar2 + 1;
      (*((int *)camry_host_ptr((uint32_t)(puVar3 + uVar2 * 4 + -0x5eac)))) = ((int32_t *)((stack_record_11 + 1)))[uVar2];
      uVar2 = uVar1;
    } while (uVar1 < 2);
    thunk_pop_and_restore_priority_mask_stack_6a4c4();
    return_zero_via_two_byte_hook_92054(stack_record_11[0],uVar4);
  }
  return;
}

void dcm_initialize_session_snapshot_to_default_924e8(void)

{
  app_dcm_session_snapshot.current = '\x01';
  app_dcm_session_snapshot.previous = '\x01';
  app_dcm_session_snapshot.target = '\x01';
  app_dcm_session_snapshot.pending_publication = '\0';
  return;
}

uint dcm_read_session_snapshot(uchar *session)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  thunk_push_priority_mask_and_raise_to_ff00_6a45e();
  *session = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x5ea4)))));
  thunk_pop_and_restore_priority_mask_stack_6a4c4();
  return 0;
}

undefined4 dcm_notify_session_publication(uchar old_session,uchar new_session)

{
  int iVar1;
  int iVar2;
  undefined8 uVar3;
  int iVar4;
  
  uVar3 = 0x23dfc00000000;
  iVar4 = 0;
  do {
    (*(int (*)())camry_indirect((uint32_t)(((((code *)(uintptr_t)((uint32_t)((uintptr_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(iVar4 * 4 + (int)((ulonglong)uVar3 >> 0x20) + 0x214c))))))))))))(old_session,new_session);
    iVar2 = iVar4 + 1;
    iVar1 = iVar4 + -1;
    iVar4 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  return notify_application_session_change_wrapper_92044(old_session,new_session);
}

void dcm_stage_or_publish_session(uchar target,uchar defer)

{
  uchar uVar1;
  uint32_t puVar2;
  puVar2 = 0xfebeb800u;
  thunk_push_priority_mask_and_raise_to_ff00_6a45e();
  if (defer == '\x01') {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x5ea2))))) = target;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x5ea1))))) = 1;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x5ea3))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x5ea4)))));
    thunk_pop_and_restore_priority_mask_stack_6a4c4();
  }
  else {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x5ea2))))) = target;
    uVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x5ea4)))));
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x5ea4))))) = target;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x5ea1))))) = 0;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x5ea3))))) = uVar1;
    thunk_pop_and_restore_priority_mask_stack_6a4c4();
    publish_dcm_security_level_91e12(0);
    dcm_notify_session_publication((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x5ea3))))),target);
  }
  return;
}

undefined4 return_zero_via_byte_hook_925a0(undefined1 param_1)

{
  return ((void)(param_1), return_const_0_9260c());
}

void dcm_commit_or_discard_staged_session(uchar commit)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  thunk_push_priority_mask_and_raise_to_ff00_6a45e();
  if (commit == '\x01') {
    if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x5ea1))))) == '\x01') {
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x5ea4))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x5ea2)))));
    }
  }
  else {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x5ea1))))) = 0;
  }
  thunk_pop_and_restore_priority_mask_stack_6a4c4();
  return;
}

void dcm_finish_staged_session_notifications(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  if (app_dcm_session_snapshot.pending_publication == '\x01') {
    publish_dcm_security_level_91e12(0);
    dcm_notify_session_publication((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x5ea3))))),(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x5ea2))))));
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x5ea1))))) = 0;
  }
  return;
}

void dcm_rewrite_current_session_byte_92602(void)

{
  return;
}

undefined4 return_const_0_9260c(void)

{
  return 0;
}

void dcm_set_request_phase_92610(uchar param_1)

{
  dcm_request_phase = param_1;
  return;
}

void dcm_clear_request_phase_92616(void)

{
  dcm_set_request_phase_92610(0);
  return;
}

uchar dcm_get_request_phase_92624(void)

{
  return dcm_request_phase;
}

void return_only_stub_9262a(void)

{
  return;
}

undefined4 copy_response_bytes_with_optional_cursor_rewind_9262c(int *param_1,char *param_2,int *param_3)

{
  ushort uVar1;
  uint uVar2;
  
  uVar1 = *(ushort *)(param_2 + 2);
  uVar2 = (uint)uVar1 + (uint)*(ushort *)(param_3 + 1);
  if (-1 < (int)(*(ushort *)(param_1 + 1) - uVar2) && *(ushort *)(param_1 + 1) != uVar2) {
    return 2;
  }
  uVar2 = 0;
  if (*param_2 == '\0') {
    for (; uVar2 < *(ushort *)(param_1 + 1); uVar2 = uVar2 + 1 & 0xffff) {
      (*((undefined1 *)camry_host_ptr((uint32_t)(*param_1 + uVar2)))) = (*((undefined1 *)camry_host_ptr((uint32_t)(*param_3 + uVar2))));
    }
  }
  else {
    uVar2 = 0;
    if (*param_2 != '\x01') {
      for (; uVar2 < *(ushort *)(param_1 + 1); uVar2 = uVar2 + 1 & 0xffff) {
        (*((undefined1 *)camry_host_ptr((uint32_t)(*param_1 + uVar2)))) = (*((undefined1 *)camry_host_ptr((uint32_t)(*param_3 + uVar2))));
      }
      return 0;
    }
    *(ushort *)(param_3 + 1) = uVar1 + *(ushort *)(param_3 + 1);
    *param_3 = *param_3 - (uint)uVar1;
    for (; uVar2 < *(ushort *)(param_1 + 1); uVar2 = uVar2 + 1 & 0xffff) {
      (*((undefined1 *)camry_host_ptr((uint32_t)(*param_1 + uVar2)))) = (*((undefined1 *)camry_host_ptr((uint32_t)(*param_3 + uVar2))));
    }
  }
  *(short *)(param_3 + 1) = (short)param_3[1] - (short)uVar2;
  *param_3 = *param_3 + uVar2;
  return 0;
}

uint dcm_copy_transmit_data
               (ushort transmit_id,F33PduInfo *chunk,F33DcmRetryInfo *retry,ushort *available)

{
  uint32_t puVar1;
  int *piVar2;
  uint uVar3;
  undefined4 uVar4;
  int iVar5;
  uint uVar6;
  
  puVar1 = 0x23dfcu;
  uVar6 = 0;
  piVar2 = ((int *)camry_host_ptr((uint32_t)(return_const_febe5978_93690())));
  uVar3 = dcm_get_current_confirmation_id_93ebc();
  if ((uVar3 == transmit_id) && (camry_host_addr((chunk))!= 0)) {
    uVar4 = dcm_get_response_state_locked_92b34();
    iVar5 = is_response_state_30_31_32_or_40_92c46(uVar4);
    if (iVar5 == 1) {
      dcm_cancel_software_timer('\x01');
      if (chunk->length == 0) {
        if (camry_host_addr((available))== 0) {
          uVar6 = 1;
        }
        else {
          *available = *(ushort *)(piVar2 + 1);
          if ((camry_host_addr((retry))!= 0) && (retry->retry_kind == '\0')) {
            *(undefined2 *)(piVar2 + 1) = 0;
            *available = 0;
          }
        }
      }
      else {
        if (camry_host_addr((retry))== 0) {
          if (*(ushort *)(piVar2 + 1) < chunk->length) {
            uVar6 = 2;
          }
          else {
            for (uVar3 = 0; uVar3 < chunk->length; uVar3 = uVar3 + 1 & 0xffff) {
              (*((volatile uint8_t *)camry_host_ptr((uint32_t)((uint32_t)(chunk->data) + (uint32_t)(uVar3) * 1u)))) = (*((uchar *)camry_host_ptr((uint32_t)(*piVar2 + uVar3))));
            }
            *(short *)(piVar2 + 1) = (short)piVar2[1] - (short)uVar3;
            *piVar2 = *piVar2 + uVar3;
          }
        }
        else {
          uVar6 = copy_response_bytes_with_optional_cursor_rewind_9262c(chunk,retry,piVar2);
        }
        if (camry_host_addr((available))!= 0) {
          *available = *(ushort *)(piVar2 + 1);
        }
      }
      dcm_arm_software_timer('\x01',(*((uint *)camry_host_ptr((uint32_t)(puVar1 + 0x2088)))));
      return uVar6;
    }
  }
  return 1;
}

uint dcm_map_response_delivery_result(uchar disposition,uchar transport_result)

{
  if (disposition == '\0') {
    return (uint)(transport_result != '\0');
  }
  if (disposition == '\x01') {
    if (transport_result != '\0') {
      return 3;
    }
  }
  else if (disposition == '\x02') {
    return 0;
  }
  return 2;
}

undefined4 dcm_queue_response_stop_event_and_cancel_timers_927cc(char param_1,char param_2)

{
  undefined4 uVar1;
  int iVar2;
  uint uVar3;
  
  if (param_2 == '\0') {
    return 0;
  }
  iVar2 = dcm_get_current_connection_transmit_flag_92b66();
  if (iVar2 != 0) {
    return 0;
  }
  dcm_cancel_software_timer('\x03');
  dcm_cancel_software_timer('\x04');
  dcm_cancel_software_timer('\x02');
  dcm_publish_default_session_and_reset_response_context_93676();
  if (param_1 == '0') {
    uVar3 = dcm_enqueue_event('(');
    if (uVar3 != 0) {
LAB_00092828:
      dcm_arm_software_timer('\x01',0);
      return 0;
    }
    uVar1 = 0x25;
  }
  else {
    uVar3 = dcm_enqueue_event(')');
    if (uVar3 != 0) goto LAB_00092828;
    uVar1 = 0x50;
  }
  dcm_set_response_state_locked_92a86(uVar1);
  return 1;
}

void dcm_transmit_confirmation(ushort transmit_id,uchar result)

{
  undefined4 uVar1;
  ushort uVar2;
  uint uVar3;
  int iVar4;
  int iVar5;
  uchar uStack_19;
  camry_fill_bytes(&uStack_19, sizeof uStack_19);
  
  uVar3 = dcm_get_current_confirmation_id_93ebc();
  uStack_19 = 0xff;
  if (uVar3 == transmit_id) {
    thunk_push_priority_mask_and_raise_to_ff00_6a45e();
    dcm_pop_response_pdu_and_refresh_next_cursor_93696(&uStack_19);
    thunk_pop_and_restore_priority_mask_stack_6a4c4();
    if (uStack_19 != 0xff) {
      iVar4 = dcm_get_response_state_locked_92b34();
      uVar3 = dcm_map_response_delivery_result(uStack_19,result);
      iVar5 = dcm_get_explicit_pending_notification_92f6a();
      dcm_set_response_notification_bytes_92a74(uVar3,iVar5);
      if (iVar4 - 0x30U < 3) {
        uVar3 = dcm_get_pending_spacing_raw_93c5a();
        uVar2 = dcm_select_response_deadline('\x01','\x01');
        dcm_cancel_software_timer('\x01');
        dcm_arm_software_timer('\x03',uVar3);
        dcm_arm_software_timer('\x04',(uint)uVar2);
        if (iVar4 == 0x30) {
          dcm_set_response_state_locked_92a86(0x11);
          iVar4 = dcm_queue_response_stop_event_and_cancel_timers_927cc(0x30,result);
          if ((iVar4 == 0) && (iVar5 == 1)) {
            dcm_enqueue_event(')');
          }
        }
        else {
          iVar5 = dcm_queue_response_stop_event_and_cancel_timers_927cc(iVar4,result);
          if ((iVar5 == 0) && (uVar3 = dcm_enqueue_event('\x01'), uVar3 == 0)) {
            if (iVar4 == 0x31) {
              uVar1 = 0x21;
            }
            else {
              uVar1 = 0x22;
            }
            dcm_set_response_state_locked_92a86(uVar1);
          }
        }
        dcm_set_explicit_pending_notification_92f70(0);
      }
      else if (iVar4 == 0x40) {
        dcm_cancel_software_timer('\x01');
        dcm_resolve_session_after_response_and_reset_queue_9364a(result);
        uVar3 = dcm_enqueue_event(')');
        if (uVar3 == 0) {
          dcm_set_response_state_locked_92a86(0x50);
        }
        else {
          dcm_arm_software_timer('\x01',0);
        }
      }
    }
  }
  return;
}

uint32_t dcm_enqueue_completion_for_matching_confirmation_id_92946(uint param_1)

{
  uint32_t camry_r10_result;
  uint uVar1;
  
  uVar1 = (camry_r10_result = dcm_get_current_confirmation_id_93ebc());
  if (uVar1 == (param_1 & 0xffff)) {
    dcm_set_response_notification_bytes_92a74(0,0);
    (camry_r10_result = dcm_enqueue_event(')'));
  }
  return camry_r10_result;
}

uint dcm_submit_transport_response(ushort transmit_id,F33PduInfo *response,uchar disposition)

{
  uint32_t puVar1;
  undefined4 uVar2;
  int iVar3;
  uint uVar4;
  
  puVar1 = 0x23dfcu;
  uVar4 = 0;
  if ((disposition == '\x10') || (disposition == '\x11')) {
    puVar1 = 0x23dfcu;
    iVar3 = dcm_current_receive_descriptor_flags_eight_and_nine_set_93d2e();
    if (iVar3 != 0) {
      return 0x83;
    }
  }
  else if (1 < disposition) {
    dcm_set_pending_transport_accepted_93c94(0);
    dcm_cancel_software_timer('\x03');
    dcm_cancel_software_timer('\x04');
    dcm_cancel_software_timer('\x02');
    return 0x84;
  }
  uVar2 = dcm_get_current_dispatch_receive_slot_93c60();
  iVar3 = is_dcm_route_communication_mode_blocked_9185c(uVar2,0);
  if (iVar3 == 1) {
    if ((disposition != '\x10') && (disposition != '\x11')) {
      dcm_set_pending_transport_accepted_93c94(0);
      dcm_cancel_software_timer('\x03');
      dcm_cancel_software_timer('\x04');
      dcm_cancel_software_timer('\x02');
    }
    iVar3 = invoke_prefixed_id_callback_21ccc_92a52(transmit_id, camry_host_addr(response));
    if (iVar3 == 0) {
      if (disposition == '\x10') {
        dcm_set_pending_transport_accepted_93c94(1);
      }
      dcm_arm_software_timer('\x01',(*((uint *)camry_host_ptr((uint32_t)(puVar1 + 0x2088)))));
    }
    else {
      uVar4 = 0x81;
    }
  }
  else {
    uVar4 = 0x82;
  }
  return uVar4;
}

short dcm_cancel_timer_one_and_optional_transmit_callback_92a1e(undefined2 param_1)

{
  uint32_t puVar1;
  short sVar2;
  
  puVar1 = 0x23dfcu;
  sVar2 = dcm_get_current_dispatch_receive_slot_93c60();
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)((*((short *)camry_host_ptr((uint32_t)(puVar1 + sVar2 * 0xc + 0x20ec)))) * 0x14 + 0x20d5))))) == '\x01') {
    sVar2 = (short)invoke_prefixed_id_callback_21cd0_92a60(param_1);
  }
  dcm_cancel_software_timer('\x01');
  return sVar2;
}

undefined4 invoke_prefixed_id_callback_21ccc_92a52(undefined2 param_1, undefined4 param_2)

{
  return call_21ccc_with_prefixed_u16_81b92(param_1, param_2);
}

undefined4 invoke_prefixed_id_callback_21cd0_92a60(undefined2 param_1)

{
  return call_21cd0_with_prefixed_u16_81bac(param_1);
}

F33DcmResponseQueue * dcm_get_response_queue(void)

{
  return ((undefined *)camry_host_ptr(0xfebe5970u));
}

void dcm_set_response_notification_bytes_92a74(uchar param_1,uchar param_2)

{
  dcm_response_queue.notification_result = param_1;
  dcm_response_queue.pending_notification = param_2;
  return;
}

void dcm_set_response_state_locked_92a86(undefined1 param_1)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  thunk_push_priority_mask_and_raise_to_ff00_6a45e();
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x5e9c))))) = param_1;
  thunk_pop_and_restore_priority_mask_stack_6a4c4();
  return;
}

void dcm_clear_response_notification_and_state_92a9c(void)

{
  dcm_set_response_notification_bytes_92a74(0,0);
  dcm_set_response_state_locked_92a86(0x0);
  return;
}

void dcm_reset_response_queue(void)

{
  undefined4 *puVar1;
  uint32_t puVar2;
  puVar2 = 0xfebeb800u;
  ((volatile uint8_t *)camry_host_ptr(0xfebe596au))[0] = '\0';
  ((volatile uint8_t *)camry_host_ptr(0xfebe5967u))[0] = '\0';
  dcm_response_queue.remaining_length = 0;
  dcm_response_queue.copy_cursor = 0;
  dcm_get_shared_response_buffer_and_connection_limit_93ce6(((undefined4 *)camry_host_ptr((uint32_t)((int)0xfebe5978))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x5e9a))))) = 0;
  (*((undefined4 *)camry_host_ptr((uint32_t)(puVar2 + -0x5e68)))) = (*((undefined4 *)camry_host_ptr((uint32_t)(puVar2 + -0x5e88))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x5e9b))))) = 0;
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar2 + -0x5e44)))) = 0;
  (*((undefined4 *)camry_host_ptr((uint32_t)(puVar2 + -0x5e48)))) = 0;
  (*((volatile uint32_t *)camry_host_ptr((uint32_t)(puVar2 + -0x5e38)))) = camry_host_addr(dcm_pending_negative_response);
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x5e50))))) = 1;
  (*((volatile uint32_t *)camry_host_ptr((uint32_t)(puVar2 + -0x5e58)))) = camry_host_addr(dcm_final_negative_response);
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x5e60))))) = 0;
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar2 + -0x5e64)))) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar2 + -0x5e84))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x5e40))))) = 3;
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar2 + -0x5e34)))) = 3;
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar2 + -0x5e54)))) = 3;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x5e30))))) = 0x10;
  puVar1 = ((undefined4 *)camry_host_ptr((uint32_t)(puVar2 + -0x5e7c)));
  (*((volatile uint32_t *)camry_host_ptr((uint32_t)(puVar2 + -0x5e90)))) = camry_host_addr(puVar1);
  (*((volatile uint32_t *)camry_host_ptr((uint32_t)(puVar2 + -0x5e8c)))) = camry_host_addr(puVar1);
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar2 + -0x5e74)))) = 0;
  (*((undefined4 *)camry_host_ptr((uint32_t)(puVar2 + -0x5e78)))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x5e70))))) = 0;
  *puVar1 = 0;
  return;
}

void dcm_reset_response_state_and_queue_92b24(void)

{
  dcm_clear_response_notification_and_state_92a9c();
  dcm_reset_response_queue();
  return;
}

undefined1 dcm_get_response_state_locked_92b34(void)

{
  undefined1 uVar1;
  uint32_t puVar2;
  puVar2 = 0xfebeb800u;
  thunk_push_priority_mask_and_raise_to_ff00_6a45e();
  uVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x5e9c)))));
  thunk_pop_and_restore_priority_mask_stack_6a4c4();
  return uVar1;
}

uint32_t dcm_activate_idle_response_queue_92b4a(void)

{
  uint32_t camry_r10_result;
  int iVar1;
  
  iVar1 = (camry_r10_result = dcm_get_response_state_locked_92b34());
  if (iVar1 == 0) {
    dcm_reset_response_queue();
    dcm_set_response_state_locked_92a86(0x10);
  }
  return camry_r10_result;
}

undefined1 dcm_get_current_connection_transmit_flag_92b66(void)

{
  uint32_t puVar1;
  short sVar2;
  
  puVar1 = 0x23dfcu;
  sVar2 = dcm_get_current_dispatch_receive_slot_93c60();
  return (*((undefined1 *)camry_host_ptr((uint32_t)((*((volatile int32_t *)camry_host_ptr((uint32_t)((*((volatile int32_t *)camry_host_ptr((uint32_t)((uint)(*((volatile ushort *)camry_host_ptr((uint32_t)(0x23dfcu + (uint32_t)(sVar2 * 0xc + 0x20ee) * 1u)))) * 4 +
                            (*((volatile int32_t *)camry_host_ptr((uint32_t)(puVar1 + (*((volatile short *)camry_host_ptr((uint32_t)(0x23dfcu + (uint32_t)(sVar2 * 0xc + 0x20ec) * 1u)))) * 0x14 +
                                              0x20c4)))))))) + 8)))) + 8))));
}

int * dcm_pop_response_queue_node_92b98(undefined4 *param_1)

{
  int *piVar1;
  int iVar2;
  int *piVar3;
  int *piVar4;
  
  piVar3 = (int *)0x0;
  if ((((camry_host_addr(param_1)!=camry_host_addr((undefined4 *)0x0)) && (piVar4 = ((int *)camry_host_ptr((uint32_t)(*param_1))),camry_host_addr(piVar4)!=camry_host_addr((int *)0x0))) &&
      (piVar1 = ((int *)camry_host_ptr((uint32_t)(*piVar4))),camry_host_addr(piVar1)!=camry_host_addr((int *)0x0))) &&
     (iVar2 = *piVar1, *piVar4 = iVar2, piVar3 = piVar1, iVar2 == 0)) {
    param_1[1] = camry_host_addr(dcm_response_node);
  }
  return piVar3;
}

undefined4 dcm_peek_response_queue_node_92bc2(undefined4 *param_1)

{
  undefined4 uVar1;
  
  uVar1 = 0;
  if ((camry_host_addr((param_1))!= 0) && ((uint32_t)(*param_1 )!= 0)) {
    uVar1 = (*((undefined4 *)camry_host_ptr((uint32_t)(*param_1))));
  }
  return uVar1;
}

uint32_t dcm_refresh_response_copy_cursor_from_head_92bd8(undefined4 param_1)

{
  uint32_t camry_r10_result;
  undefined2 uVar1;
  int iVar2;
  
  iVar2 = (camry_r10_result = dcm_peek_response_queue_node_92bc2(((undefined4 *)camry_host_ptr((uint32_t)(param_1)))));
  if (iVar2 == 0) {
    (*((undefined4 *)camry_host_ptr((uint32_t)(param_1 + 8)))) = 0;
    uVar1 = 0;
  }
  else {
    (*((undefined4 *)camry_host_ptr((uint32_t)(param_1 + 8)))) = (*((undefined4 *)camry_host_ptr((uint32_t)(iVar2 + 4))));
    uVar1 = (*((undefined2 *)camry_host_ptr((uint32_t)(iVar2 + 8))));
  }
  (*((undefined2 *)camry_host_ptr((uint32_t)(param_1 + 0xc)))) = uVar1;
  return camry_r10_result;
}

uint32_t run_init_chain_92bfe(void)

{
  uint32_t camry_r10_result;
  thunk_push_priority_mask_and_raise_to_ff00_6a45e();
  dcm_pop_response_queue_node_92b98(((undefined4 *)camry_host_ptr((uint32_t)((0xfebe5970u)))));
  (camry_r10_result = dcm_refresh_response_copy_cursor_from_head_92bd8((0xfebe5970u)));
  thunk_pop_and_restore_priority_mask_stack_6a4c4();
  return camry_r10_result;
}

uint dcm_map_head_response_delivery_result_92c1e(uchar param_1)

{
  uchar disposition;
  int iVar1;
  
  iVar1 = dcm_peek_response_queue_node_92bc2(((undefined4 *)camry_host_ptr((uint32_t)((0xfebe5970u)))));
  disposition = 0xff;
  if (iVar1 != 0) {
    disposition = (*((uchar *)camry_host_ptr((uint32_t)(iVar1 + 0xc))));
  }
  return dcm_map_response_delivery_result(disposition,param_1);
}

undefined4 is_response_state_30_31_32_or_40_92c46(uint param_1)

{
  uint uVar1;
  undefined4 uVar2;
  
  uVar1 = (param_1 & 0xff) - 0x30;
  uVar2 = 0;
  if ((uVar1 < 3) || (uVar1 == 0x10)) {
    uVar2 = 1;
  }
  return uVar2;
}

void dcm_transport_watchdog_expired(void)

{
  int iVar1;
  int iVar2;
  undefined4 uVar3;
  undefined4 uVar4;
  
  iVar1 = dcm_get_response_state_locked_92b34();
  iVar2 = dcm_get_current_connection_transmit_flag_92b66();
  uVar3 = dcm_get_current_transmit_id_93e82();
  uVar4 = dcm_get_current_dispatch_receive_slot_93c60();
  dcm_cancel_software_timer('\x03');
  dcm_cancel_software_timer('\x04');
  dcm_cancel_software_timer('\x02');
  if (iVar2 == 0) {
    stage_or_publish_dcm_session_91b08(1,0);
  }
  if (((iVar1 == 0x21 || iVar1 == 0x22) || (iVar1 == 0x31 || iVar1 == 0x32)) || (iVar1 == 0x40)) {
    commit_or_discard_dcm_staged_session_91f64(0);
    dcm_restart_inactivity_after_request();
    update_dcm_connection_activity_requests_91938(uVar4,1);
    if (iVar1 == 0x31 || iVar1 == 0x32) {
      run_init_chain_92bfe();
    }
    uVar4 = dcm_map_head_response_delivery_result_92c1e(1);
    deliver_dcm_response_notification_91c82(uVar4,0);
    if ((iVar1 == 0x40) || (iVar1 == 0x31 || iVar1 == 0x32)) {
      dcm_cancel_timer_one_and_optional_transmit_callback_92a1e(uVar3);
    }
  }
  else if (((iVar1 == 0x10 || iVar1 == 0x11) || (iVar1 == 0x20)) ||
          ((iVar1 - 0x23U < 3 || (iVar1 - 0x23U == 0xd)))) {
    cancel_dcm_active_service_91e6e();
    iVar2 = is_response_state_30_31_32_or_40_92c46(iVar1);
    if ((iVar2 == 1) || (iVar1 == 0x24)) {
      dcm_cancel_timer_one_and_optional_transmit_callback_92a1e(uVar3);
    }
    commit_or_discard_dcm_staged_session_91f64(0);
    dcm_restart_inactivity_after_request();
    update_dcm_connection_activity_requests_91938(uVar4,1);
  }
  dcm_reset_response_queue();
  dcm_clear_response_notification_and_state_92a9c();
  return;
}

undefined4 dcm_prepare_head_response_pdu_and_disposition_92d38(undefined1 *param_1)

{
  undefined1 uVar1;
  int iVar2;
  undefined4 uVar3;
  
  iVar2 = dcm_peek_response_queue_node_92bc2(((undefined4 *)camry_host_ptr((uint32_t)((0xfebe5970u)))));
  if (iVar2 == 0) {
    uVar1 = 0xff;
    uVar3 = 0;
  }
  else {
    dcm_response_queue.copy_cursor = ((uint32_t)((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)((iVar2 + 4))))))));
    uVar3 = 0xfebe5978;
    dcm_response_queue.remaining_length = (*((ushort *)camry_host_ptr((uint32_t)(iVar2 + 8))));
    uVar1 = (*((undefined1 *)camry_host_ptr((uint32_t)(iVar2 + 0xc))));
  }
  *param_1 = uVar1;
  return uVar3;
}

undefined4 dcm_response_state_allows_completion_notification_92d72(void)

{
  int iVar1;
  undefined4 uVar2;
  
  uVar2 = 0;
  iVar1 = dcm_get_response_state_locked_92b34();
  if ((((iVar1 == 0) || (iVar1 == 0x21 || iVar1 == 0x22)) || (iVar1 == 0x31 || iVar1 == 0x32)) ||
     ((iVar1 == 0x40 || (iVar1 == 0x50)))) {
    uVar2 = 1;
  }
  return uVar2;
}

void dcm_complete_response_notification_and_connection_release_92da0(undefined1 param_1)

{
  int iVar1;
  undefined4 uVar2;
  
  iVar1 = dcm_response_state_allows_completion_notification_92d72();
  if (iVar1 == 1) {
    dcm_restart_inactivity_after_request();
    deliver_dcm_response_notification_91c82(param_1,0);
  }
  else {
    cancel_dcm_active_service_91e6e();
  }
  uVar2 = dcm_get_current_dispatch_receive_slot_93c60();
  update_dcm_connection_activity_requests_91938(uVar2,1);
  return;
}

void dcm_finish_response_and_clear_queue_state_92dd2(undefined1 param_1)

{
  dcm_complete_response_notification_and_connection_release_92da0(param_1);
  dcm_reset_response_queue();
  dcm_clear_response_notification_and_state_92a9c();
  return;
}

void dcm_discard_staged_session_and_finish_response_92de8(undefined1 param_1)

{
  commit_or_discard_dcm_staged_session_91f64(0);
  dcm_finish_response_and_clear_queue_state_92dd2(param_1);
  return;
}

void dcm_try_final_response(ushort transmit_id,F33PduInfo *response,uchar disposition)

{
  bool bVar1;
  uint32_t puVar2;
  uint uVar3;
  undefined4 uVar4;
  int iVar5;
  undefined4 uVar6;
  
  puVar2 = 0xfebeb800u;
  bVar1 = false;
  uVar6 = 1;
  uVar3 = dcm_submit_transport_response(transmit_id,response,disposition);
  if (uVar3 == 0) {
    return;
  }
  if (uVar3 == 0x82) {
    if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x5e9b))))) == '\x01') {
      commit_or_discard_dcm_staged_session_91f64(0);
      bVar1 = true;
    }
    else {
      uVar3 = dcm_enqueue_event('+');
      if (uVar3 == 0) {
        dcm_set_response_state_locked_92a86(0x21);
        return;
      }
      uVar4 = dcm_map_head_response_delivery_result_92c1e(1);
      dcm_discard_staged_session_and_finish_response_92de8(uVar4);
    }
    dcm_cancel_software_timer('\x03');
    dcm_cancel_software_timer('\x04');
    dcm_cancel_software_timer('\x02');
    if (!bVar1) {
      return;
    }
  }
  else {
    if (uVar3 == 0x84) {
      uVar6 = 0;
      if (disposition == '\x02') {
        commit_or_discard_dcm_staged_session_91f64(1);
        dcm_finish_staged_session_notifications_wrapper_91f90();
        goto LAB_00092e9e;
      }
    }
    else if ((uVar3 == 0x81) && (iVar5 = dcm_get_current_connection_transmit_flag_92b66(), iVar5 == 0)) {
      stage_or_publish_dcm_session_91b08(1,0);
      goto LAB_00092e9e;
    }
    commit_or_discard_dcm_staged_session_91f64(0);
  }
LAB_00092e9e:
  uVar6 = dcm_map_head_response_delivery_result_92c1e(uVar6);
  dcm_finish_response_and_clear_queue_state_92dd2(uVar6);
  return;
}

void dcm_submit_response_11_and_handle_session_result_92eae(ushort param_1,F33PduInfo *param_2)

{
  int iVar1;
  uint uVar2;
  
  iVar1 = dcm_get_current_connection_transmit_flag_92b66();
  uVar2 = dcm_submit_transport_response(param_1,param_2,'\x11');
  if (uVar2 == 0) {
    if (iVar1 == 0) {
      stage_or_publish_dcm_session_91b08(1,1);
    }
    else {
      commit_or_discard_dcm_staged_session_91f64(0);
    }
  }
  else {
    if ((uVar2 == 0x83) || (iVar1 != 0)) {
      commit_or_discard_dcm_staged_session_91f64(0);
    }
    else {
      stage_or_publish_dcm_session_91b08(1,0);
    }
    dcm_finish_response_and_clear_queue_state_92dd2(3);
  }
  return;
}

void dcm_transmit_queued_final_response_by_state_92f08(void)

{
  undefined4 uVar1;
  F33PduInfo *response;
  int iVar2;
  uchar uStack_d;
  
  uStack_d = '\0';
  uVar1 = dcm_get_current_transmit_id_93e82();
  response = ((F33PduInfo *)camry_host_ptr((uint32_t)(dcm_prepare_head_response_pdu_and_disposition_92d38(&uStack_d))));
  if (camry_host_addr((response))!= 0) {
    iVar2 = dcm_get_response_state_locked_92b34();
    if (iVar2 == 0x21) {
      dcm_set_response_state_locked_92a86(0x40);
      dcm_try_final_response((ushort)uVar1,response,uStack_d);
    }
    else if (iVar2 == 0x22) {
      dcm_cancel_software_timer('\x03');
      dcm_cancel_software_timer('\x04');
      dcm_set_response_state_locked_92a86(0x40);
      dcm_submit_response_11_and_handle_session_result_92eae(uVar1,response);
    }
  }
  return;
}

uchar dcm_get_explicit_pending_notification_92f6a(void)

{
  return dcm_explicit_pending_notification;
}

void dcm_set_explicit_pending_notification_92f70(uchar param_1)

{
  dcm_explicit_pending_notification = param_1;
  return;
}

void dcm_try_pending_response(ushort transmit_id,F33PduInfo *response,uchar explicit_pending)

{
  uchar camry_r10_0;

  uint32_t puVar1;
  ushort uVar2;
  uint uVar3;
  int iVar4;
  undefined4 uVar5;
  undefined4 uVar6;
  
  puVar1 = 0xfebeb800u;
  uVar3 = dcm_submit_transport_response(transmit_id,response,'\x10');
  if (uVar3 == 0) {
    if (explicit_pending != '\x01') {
      return;
    }
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x5e9b))))) = 1;
    return;
  }
  uVar6 = 3;
  if (uVar3 == 0x82) {
    if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x5e9b))))) != '\x01') {
      uVar3 = dcm_enqueue_event('+');
      if (uVar3 == 0) {
        dcm_set_response_state_locked_92a86(0x20);
        return;
      }
      dcm_discard_staged_session_and_finish_response_92de8(3);
      return;
    }
    run_init_chain_92bfe();
  }
  else {
    run_init_chain_92bfe();
    if (uVar3 != 0x83) {
      iVar4 = dcm_get_current_connection_transmit_flag_92b66();
      if (iVar4 != 0) {
        uVar5 = 0x11;
      }
      else {
        dcm_cancel_software_timer('\x02');
        cancel_dcm_active_service_91e6e();
        stage_or_publish_dcm_session_91b08(1,0);
        dcm_restart_inactivity_after_request();
        dcm_reset_response_queue();
        uVar5 = 0;
      }
      dcm_set_response_state_locked_92a86(uVar5);
      if (iVar4 == 0) {
        return;
      }
      goto LAB_00093018;
    }
    uVar6 = 2;
  }
  dcm_set_response_state_locked_92a86(0x11);
LAB_00093018:
  uVar3 = dcm_get_pending_spacing_raw_93c5a();
  uVar2 = dcm_select_response_deadline('\x01','\x01');
  dcm_arm_software_timer('\x03',uVar3);
  dcm_arm_software_timer('\x04',(uint)uVar2);
  iVar4 = (camry_r10_0 = dcm_get_explicit_pending_notification_92f6a());
  if (iVar4 == 1) {
    uVar5 = (dcm_set_explicit_pending_notification_92f70(0), (undefined4)(uintptr_t)camry_r10_0);
    deliver_dcm_response_notification_91c82(uVar6,uVar5);
  }
  return;
}
