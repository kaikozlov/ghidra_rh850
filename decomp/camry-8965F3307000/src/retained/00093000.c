#include "common.h"

void dcm_advance_response_after_transport_notification_93052(void)

{
  uchar camry_r10_0;

  uint32_t puVar1;
  ushort uVar2;
  int iVar3;
  undefined4 uVar4;
  F33PduInfo *response;
  uint duration;
  uchar uStack_19;
  
  puVar1 = 0xfebeb800u;
  iVar3 = dcm_get_response_state_locked_92b34();
  uVar4 = dcm_get_current_transmit_id_93e82();
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x5e9b))))) == '\0') {
    if (iVar3 == 0x20) {
      dcm_set_response_state_locked_92a86(0x30);
      dcm_try_pending_response
                ((ushort)uVar4,(F33PduInfo *)&dcm_response_queue.copy_cursor,'\0');
    }
    else if (iVar3 == 0x21) {
      uStack_19 = 0xff;
      response = ((F33PduInfo *)camry_host_ptr((uint32_t)(dcm_prepare_head_response_pdu_and_disposition_92d38(&uStack_19))));
      if (camry_host_addr((response))!= 0) {
        dcm_set_response_state_locked_92a86(0x40);
        dcm_try_final_response((ushort)uVar4,response,uStack_19);
      }
    }
  }
  else {
    duration = dcm_get_pending_spacing_raw_93c5a();
    uVar2 = dcm_select_response_deadline('\x01','\x01');
    if (iVar3 == 0x20) {
      dcm_arm_software_timer('\x03',duration);
      dcm_arm_software_timer('\x04',(uint)uVar2);
      run_init_chain_92bfe();
      (camry_r10_0 = dcm_get_explicit_pending_notification_92f6a());
      iVar3 = (dcm_set_explicit_pending_notification_92f70(0), (int)(uintptr_t)camry_r10_0);
      if (iVar3 == 1) {
        deliver_dcm_response_notification_91c82(3,1);
      }
      dcm_set_response_state_locked_92a86(0x11);
    }
    else if (iVar3 == 0x21) {
      dcm_cancel_software_timer('\x03');
      dcm_cancel_software_timer('\x04');
      dcm_cancel_software_timer('\x02');
      uVar4 = dcm_map_head_response_delivery_result_92c1e(1);
      dcm_discard_staged_session_and_finish_response_92de8(uVar4);
    }
    else if (iVar3 == 0x22) {
      dcm_cancel_software_timer('\x03');
      dcm_cancel_software_timer('\x04');
      dcm_set_response_state_locked_92a86(0x40);
      dcm_submit_response_11_and_handle_session_result_92eae(uVar4, ((F33PduInfo *)camry_host_ptr((uint32_t)((int)0xfebe5978))));
    }
  }
  return;
}

void format_three_byte_negative_response_93154(undefined1 *param_1,undefined1 param_2,undefined1 param_3)

{
  param_1[1] = param_2;
  *param_1 = 0x7f;
  param_1[2] = param_3;
  return;
}

void dcm_format_final_negative_response_93162(undefined1 param_1,undefined1 param_2)

{
  format_three_byte_negative_response_93154(dcm_final_negative_response,param_1,param_2);
  return;
}

F33DcmResponseNode * dcm_get_response_node_by_byte_index_9317a(uint param_1)

{
  return ((volatile F33DcmResponseNode *)camry_host_ptr((uint32_t)(0xfebe5984u + (uint32_t)((param_1 & 0xff)) * (uint32_t)sizeof(F33DcmResponseNode))));
}

void dcm_append_response_node(F33DcmResponseQueue *queue,F33DcmResponseNode *node)

{
  ((F33DcmResponseNode *)camry_host_ptr((uint32_t)(queue->tail)))->next = camry_host_addr(node);
  queue->tail = camry_host_addr(node);
  node->next = 0;
  return;
}

F33PduInfo * dcm_enqueue_pending_response(uchar service_id)

{
  F33DcmResponseNode * camry_r10_0;

  uint32_t puVar1;
  int iVar2;
  F33DcmResponseNode *node;
  
  puVar1 = 0xfebeb800u;
  iVar2 = camry_host_addr((camry_r10_0 = ((void)(service_id), dcm_get_response_node_by_byte_index_9317a(4))));
  node = (F33DcmResponseNode *)(format_three_byte_negative_response_93154(((undefined *)camry_host_ptr((uint32_t)(puVar1 + -0x5e96))),  (uint)(byte)service_id,  0x78), camry_r10_0);
  dcm_append_response_node(((F33DcmResponseQueue *)camry_host_ptr((uint32_t)((0xfebe5970u)))), node);
  dcm_refresh_response_copy_cursor_from_head_92bd8((0xfebe5970u));
  return ((F33PduInfo *)camry_host_ptr((uint32_t)(iVar2 + 4)));
}

void dcm_p2_response_deadline(uchar service_id)

{
  uint32_t puVar1;
  ushort transmit_id;
  int iVar2;
  undefined4 uVar3;
  F33PduInfo *response;
  
  puVar1 = 0xfebeb800u;
  iVar2 = dcm_get_response_state_locked_92b34();
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x5e9b))))) = 1;
  if (iVar2 != 0x10) {
    if (iVar2 == 0x23) {
      cancel_dcm_active_service_91e6e();
    }
    else {
      if (iVar2 != 0x24) {
        return;
      }
      cancel_dcm_active_service_91e6e();
      uVar3 = dcm_get_displaced_transmit_id_940ca();
      dcm_cancel_timer_one_and_optional_transmit_callback_92a1e(uVar3);
    }
  }
  thunk_push_priority_mask_and_raise_to_ff00_6a45e();
  response = dcm_enqueue_pending_response(service_id);
  thunk_pop_and_restore_priority_mask_stack_6a4c4();
  dcm_set_response_state_locked_92a86(0x30);
  transmit_id = dcm_get_current_transmit_id_93e82();
  dcm_try_pending_response(transmit_id,response,'\0');
  return;
}

void dcm_send_pending_response_or_leave_wait_state_93230(void)

{
  ushort transmit_id;
  int iVar1;
  
  iVar1 = dcm_get_response_state_locked_92b34();
  if (iVar1 == 0x11) {
    dcm_set_response_state_locked_92a86(0x10);
  }
  else if (iVar1 == 0x20) {
    dcm_cancel_software_timer('\x04');
    dcm_set_response_state_locked_92a86(0x30);
    transmit_id = dcm_get_current_transmit_id_93e82();
    dcm_try_pending_response(transmit_id,(F33PduInfo *)&dcm_response_queue.copy_cursor,'\0')
    ;
  }
  return;
}

uint32_t dcm_replace_response_queue_head_93276(undefined4 param_1, undefined4 param_2)

{
  uint32_t camry_r10_result;
  
  (camry_r10_result = camry_host_addr(dcm_pop_response_queue_node_92b98(((undefined4 *)camry_host_ptr((uint32_t)(param_1))))));
  dcm_append_response_node(((F33DcmResponseQueue *)camry_host_ptr((uint32_t)(param_1))), ((F33DcmResponseNode *)camry_host_ptr((uint32_t)(param_2))));
  return camry_r10_result;
}

void dcm_enqueue_general_reject(uchar service_id)

{
  F33DcmResponseNode * camry_arg_result_0;

  uint32_t puVar1;
  F33DcmResponseQueue *queue;
  F33DcmResponseQueue *queue_00;
  F33DcmResponseNode *node;
  F33DcmResponseNode *node_00;
  F33DcmResponseQueue *queue_01;
  int iVar2;
  undefined4 uVar3;
  
  puVar1 = 0xfebeb800u;
  node_00 = (F33DcmResponseNode *)((void)(service_id), (camry_arg_result_0 = dcm_get_response_node_by_byte_index_9317a(2)));
  queue_01 = ((F33DcmResponseQueue *)camry_host_ptr((uint32_t)(puVar1 + -0x5e90)));
  format_three_byte_negative_response_93154(((undefined *)camry_host_ptr((uint32_t)(puVar1 + -0x5e99))),  (uint)(byte)service_id,  0x10);
  iVar2 = dcm_get_response_state_locked_92b34();
  if (((iVar2 == 0x10) || (iVar2 == 0x11)) || (iVar2 == 0x20)) {
    dcm_cancel_software_timer('\x03');
    dcm_cancel_software_timer('\x04');
    dcm_set_pending_transport_accepted_93c94(0);
    thunk_push_priority_mask_and_raise_to_ff00_6a45e();
    if (iVar2 == 0x20) {
      dcm_replace_response_queue_head_93276(camry_host_addr(&dcm_response_queue), camry_host_addr(camry_arg_result_0));
    }
    else {
      dcm_append_response_node(queue_01,node_00);
    }
    dcm_refresh_response_copy_cursor_from_head_92bd8(camry_host_addr(&dcm_response_queue));
    thunk_pop_and_restore_priority_mask_stack_6a4c4();
    dcm_set_response_state_locked_92a86(0x40);
    dcm_invalidate_queued_event(')','\x01');
    uVar3 = dcm_get_current_transmit_id_93e82();
    dcm_submit_response_11_and_handle_session_result_92eae(uVar3,&node_00->data);
  }
  else {
    if (iVar2 == 0x21) {
      commit_or_discard_dcm_staged_session_91f64(0);
      thunk_push_priority_mask_and_raise_to_ff00_6a45e();
      ((void)(queue_01), (void)(node_00), dcm_replace_response_queue_head_93276(camry_host_addr(&dcm_response_queue), camry_host_addr(camry_arg_result_0)));
      dcm_refresh_response_copy_cursor_from_head_92bd8(camry_host_addr(&dcm_response_queue));
      thunk_pop_and_restore_priority_mask_stack_6a4c4();
      uVar3 = 0x22;
    }
    else {
      if (iVar2 == 0x30) {
        dcm_set_pending_transport_accepted_93c94(0);
        thunk_push_priority_mask_and_raise_to_ff00_6a45e();
        dcm_append_response_node(queue_01,node_00);
        dcm_refresh_response_copy_cursor_from_head_92bd8(camry_host_addr(&dcm_response_queue));
      }
      else {
        if (iVar2 != 0x31) {
          return;
        }
        commit_or_discard_dcm_staged_session_91f64(0);
        thunk_push_priority_mask_and_raise_to_ff00_6a45e();
        dcm_pop_response_queue_node_92b98(queue_01);
        dcm_pop_response_queue_node_92b98(queue_01);
        dcm_append_response_node(queue_01,node);
        dcm_append_response_node(queue_01,node_00);
      }
      thunk_pop_and_restore_priority_mask_stack_6a4c4();
      uVar3 = 0x32;
    }
    dcm_set_response_state_locked_92a86(uVar3);
  }
  return;
}

void dcm_finish_stop_event_by_response_state_9338e(void)

{
  undefined4 uVar1;
  int iVar2;
  
  uVar1 = dcm_get_displaced_transmit_id_940ca();
  dcm_set_pending_transport_accepted_93c94(0);
  iVar2 = dcm_get_response_state_locked_92b34();
  if (iVar2 == 0x25) {
    dcm_finish_staged_session_notifications_wrapper_91f90();
    dcm_clear_response_notification_and_state_92a9c();
  }
  else {
    if (((iVar2 == 0x10 || iVar2 == 0x11) || (iVar2 == 0x23)) || (iVar2 == 0x30)) {
      dcm_set_response_state_locked_92a86(0x10);
      commit_or_discard_dcm_staged_session_91f64(0);
    }
    else {
      if (iVar2 != 0x24) {
        return;
      }
      dcm_set_response_state_locked_92a86(0x10);
      commit_or_discard_dcm_staged_session_91f64(0);
      dcm_cancel_timer_one_and_optional_transmit_callback_92a1e(uVar1);
    }
    dcm_reset_response_queue();
  }
  return;
}

void dcm_enqueue_final_disposition(F33PduInfo *response,uchar disposition)

{
  undefined4 uVar1;
  ushort transmit_id;
  F33DcmResponseNode *node;
  int iVar2;
  uint uVar3;
  
  if (disposition == '\0') {
    node = (F33DcmResponseNode *)dcm_get_response_node_by_byte_index_9317a(1);
    node->data = response->data;
    node->length = response->length;
  }
  else if (disposition == '\x01') {
    node = (F33DcmResponseNode *)dcm_get_response_node_by_byte_index_9317a(2);
  }
  else {
    node = (F33DcmResponseNode *)dcm_get_response_node_by_byte_index_9317a(3);
    node->disposition = disposition;
  }
  iVar2 = dcm_get_response_state_locked_92b34();
  if (iVar2 == 0x30) {
    thunk_push_priority_mask_and_raise_to_ff00_6a45e();
    dcm_append_response_node(((F33DcmResponseQueue *)camry_host_ptr((uint32_t)((0xfebe5970u)))), node);
    thunk_pop_and_restore_priority_mask_stack_6a4c4();
    uVar1 = 0x31;
  }
  else {
    if (iVar2 != 0x23) {
      if (iVar2 == 0x24) {
        commit_or_discard_dcm_staged_session_91f64(0);
        dcm_reset_current_receive_slot_and_shared_response_91faa();
        uVar3 = dcm_map_response_delivery_result(disposition,'\x01');
        deliver_dcm_response_notification_91c82(uVar3,0);
        dcm_invalidate_queued_event('(','\x01');
        dcm_finish_stop_event_by_response_state_9338e();
        return;
      }
      if (iVar2 == 0x25) {
        dcm_finish_staged_session_notifications_wrapper_91f90();
        uVar3 = dcm_map_response_delivery_result(disposition,'\x01');
        deliver_dcm_response_notification_91c82(uVar3,0);
        dcm_reset_response_queue();
        dcm_clear_response_notification_and_state_92a9c();
        return;
      }
      if (((iVar2 != 0x10) && (iVar2 != 0x11)) && (iVar2 != 0x20)) {
        return;
      }
      thunk_push_priority_mask_and_raise_to_ff00_6a45e();
      if (iVar2 == 0x20) {
        dcm_replace_response_queue_head_93276(camry_host_addr(&dcm_response_queue), camry_host_addr(node));
      }
      else {
        dcm_append_response_node(((F33DcmResponseQueue *)camry_host_ptr((uint32_t)((0xfebe5970u)))), node);
      }
      dcm_refresh_response_copy_cursor_from_head_92bd8(camry_host_addr(&dcm_response_queue));
      thunk_pop_and_restore_priority_mask_stack_6a4c4();
      dcm_set_response_state_locked_92a86(0x40);
      transmit_id = dcm_get_current_transmit_id_93e82();
      dcm_try_final_response
                (transmit_id,(F33PduInfo *)&dcm_response_queue.copy_cursor,disposition);
      return;
    }
    commit_or_discard_dcm_staged_session_91f64(0);
    dcm_reset_current_receive_slot_and_shared_response_91faa();
    uVar3 = dcm_map_response_delivery_result(disposition,'\x01');
    deliver_dcm_response_notification_91c82(uVar3,0);
    dcm_reset_response_queue();
    dcm_invalidate_queued_event('(','\x01');
    uVar1 = 0x10;
  }
  dcm_set_response_state_locked_92a86(uVar1);
  return;
}

void dcm_request_explicit_pending_response(uchar service_id)

{
  uint32_t puVar1;
  undefined1 extraout_r6;
  ushort transmit_id;
  int iVar2;
  F33PduInfo *response;
  
  puVar1 = 0xfebeb800u;
  iVar2 = dcm_get_response_state_locked_92b34();
  if (iVar2 == 0x10) {
    dcm_cancel_software_timer('\x04');
    dcm_set_explicit_pending_notification_92f70((extraout_r6 = 1));
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x5e9b))))) = ((undefined1)(0x1));
    thunk_push_priority_mask_and_raise_to_ff00_6a45e();
    response = dcm_enqueue_pending_response(service_id);
    thunk_pop_and_restore_priority_mask_stack_6a4c4();
    dcm_set_response_state_locked_92a86(0x30);
    transmit_id = dcm_get_current_transmit_id_93e82();
    dcm_try_pending_response(transmit_id,response,'\x01');
  }
  else if (iVar2 == 0x11) {
    dcm_set_explicit_pending_notification_92f70(1);
    thunk_push_priority_mask_and_raise_to_ff00_6a45e();
    dcm_enqueue_pending_response(service_id);
    thunk_pop_and_restore_priority_mask_stack_6a4c4();
    dcm_set_response_state_locked_92a86(0x20);
  }
  else if (iVar2 == 0x30) {
    dcm_set_explicit_pending_notification_92f70(1);
  }
  return;
}

void dcm_request_response_stop_and_save_displaced_id_935b6(void)

{
  undefined4 uVar1;
  int iVar2;
  uint uVar3;
  
  iVar2 = dcm_get_response_state_locked_92b34();
  if (2 < iVar2 - 0x23U) {
    dcm_cancel_software_timer('\x03');
    dcm_cancel_software_timer('\x04');
    dcm_cancel_software_timer('\x02');
    dcm_set_explicit_pending_notification_92f70(0);
    dcm_set_pending_transport_accepted_93c94(0x0);
    dcm_save_current_transmit_id_as_displaced_940ba();
    dcm_invalidate_queued_event(')','\x01');
    uVar3 = dcm_enqueue_event('(');
    if (uVar3 == 0) {
      if ((iVar2 == 0x10 || iVar2 == 0x11) || (iVar2 - 0x20U < 3)) {
        uVar1 = 0x23;
      }
      else {
        uVar1 = 0x24;
      }
      dcm_set_response_state_locked_92a86(uVar1);
    }
    else {
      uVar1 = dcm_map_head_response_delivery_result_92c1e(1);
      dcm_discard_staged_session_and_finish_response_92de8(uVar1);
    }
  }
  return;
}

void dcm_restart_inactivity_release_connection_and_reset_queue_9362c(void)

{
  undefined4 uVar1;
  
  uVar1 = dcm_get_current_dispatch_receive_slot_93c60();
  dcm_restart_inactivity_after_request();
  update_dcm_connection_activity_requests_91938(uVar1,1);
  dcm_reset_response_queue();
  return;
}

void dcm_resolve_session_after_response_and_reset_queue_9364a(char param_1)

{
  undefined4 uVar1;
  int iVar2;
  
  if (param_1 != '\0') {
    iVar2 = dcm_get_current_connection_transmit_flag_92b66();
    if (iVar2 != 0) {
      uVar1 = 0;
      goto LAB_0009366a;
    }
    stage_or_publish_dcm_session_91b08(1,1);
  }
  uVar1 = 1;
LAB_0009366a:
  commit_or_discard_dcm_staged_session_91f64(uVar1);
  dcm_restart_inactivity_release_connection_and_reset_queue_9362c();
  return;
}

void dcm_publish_default_session_and_reset_response_context_93676(void)

{
  stage_or_publish_dcm_session_91b08(1,1);
  commit_or_discard_dcm_staged_session_91f64(1);
  dcm_restart_inactivity_release_connection_and_reset_queue_9362c();
  return;
}

undefined4 return_const_febe5978_93690(void)

{
  return 0xfebe5978;
}

int dcm_pop_response_pdu_and_refresh_next_cursor_93696(undefined1 *param_1)

{
  int iVar1;
  int iVar2;
  
  iVar1 = camry_host_addr(dcm_pop_response_queue_node_92b98(((undefined4 *)camry_host_ptr((uint32_t)((0xfebe5970u))))));
  if (iVar1 == 0) {
    *param_1 = 0xff;
    iVar2 = 0;
  }
  else {
    iVar2 = iVar1 + 4;
    *param_1 = (*((undefined1 *)camry_host_ptr((uint32_t)(iVar1 + 0xc))));
    dcm_refresh_response_copy_cursor_from_head_92bd8((0xfebe5970u));
  }
  return iVar2;
}

void dcm_snapshot_response_notification(uchar *result,uchar *pending_notification)

{
  *result = dcm_response_queue.notification_result;
  *pending_notification = dcm_response_queue.pending_notification;
  return;
}

uint dcm_compare_protocol_priority(ushort candidate_slot,ushort owner_slot)

{
  byte bVar1;
  byte bVar2;
  
  bVar1 = ((F33DcmConnection *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(((*((volatile uint32_t *)camry_host_ptr((uint32_t)((uint32_t)(0x25ec0u + (uint32_t)((short)(*((volatile uint16_t *)camry_host_ptr((uint32_t)((uint32_t)(0x25ee8u + (uint32_t)((short)candidate_slot) * (uint32_t)sizeof(F33DcmReceiveRoute)) + (uint32_t)(0) * (uint32_t)sizeof(F33DcmReceiveRoute) + (uint32_t)offsetof(F33DcmReceiveRoute, protocol_index)))))) * (uint32_t)sizeof(F33DcmProtocolConfiguration)) + (uint32_t)(0) * (uint32_t)sizeof(F33DcmProtocolConfiguration) + (uint32_t)offsetof(F33DcmProtocolConfiguration, connections)))))) + (uint32_t)((*((volatile uint16_t *)camry_host_ptr((uint32_t)((uint32_t)(0x25ee8u + (uint32_t)((short)candidate_slot) * (uint32_t)sizeof(F33DcmReceiveRoute)) + (uint32_t)(0) * (uint32_t)sizeof(F33DcmReceiveRoute) + (uint32_t)offsetof(F33DcmReceiveRoute, connection_index)))))) * 4u)))))))->priority;
  bVar2 = ((F33DcmConnection *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(((*((volatile uint32_t *)camry_host_ptr((uint32_t)((uint32_t)(0x25ec0u + (uint32_t)((short)(*((volatile uint16_t *)camry_host_ptr((uint32_t)((uint32_t)(0x25ee8u + (uint32_t)((short)owner_slot) * (uint32_t)sizeof(F33DcmReceiveRoute)) + (uint32_t)(0) * (uint32_t)sizeof(F33DcmReceiveRoute) + (uint32_t)offsetof(F33DcmReceiveRoute, protocol_index)))))) * (uint32_t)sizeof(F33DcmProtocolConfiguration)) + (uint32_t)(0) * (uint32_t)sizeof(F33DcmProtocolConfiguration) + (uint32_t)offsetof(F33DcmProtocolConfiguration, connections)))))) + (uint32_t)((*((volatile uint16_t *)camry_host_ptr((uint32_t)((uint32_t)(0x25ee8u + (uint32_t)((short)owner_slot) * (uint32_t)sizeof(F33DcmReceiveRoute)) + (uint32_t)(0) * (uint32_t)sizeof(F33DcmReceiveRoute) + (uint32_t)offsetof(F33DcmReceiveRoute, connection_index)))))) * 4u)))))))->priority;
  if (bVar2 <= bVar1) {
    return (uint)(bVar1 == bVar2);
  }
  return 2;
}

uint dcm_claim_receive_slot(ushort receive_slot)

{
  ushort owner_slot;
  int iVar1;
  uint uVar2;
  
  iVar1 = dcm_get_request_phase_92624();
  if (iVar1 == 0) {
LAB_0009378e:
    iVar1 = dcm_get_slot_receiving_flag_93e32(receive_slot);
    if (iVar1 != 1) goto LAB_000937a2;
  }
  else {
    if (iVar1 != 1) {
      iVar1 = dcm_slot_matches_pending_protocol_and_connection_94014(receive_slot);
      if (iVar1 == 1) {
        return 0;
      }
      goto LAB_0009378e;
    }
    iVar1 = dcm_get_slot_receiving_flag_93e32((uint)(ushort)receive_slot);
    if (iVar1 != 1) {
      iVar1 = dcm_slot_matches_pending_protocol_and_connection_94014(receive_slot);
      if (iVar1 != 1) {
        owner_slot = dcm_get_pending_dispatch_receive_slot_9400e();
        uVar2 = dcm_compare_protocol_priority(receive_slot,owner_slot);
        if (uVar2 != 2) goto LAB_000937a2;
      }
      dcm_cancel_software_timer('\x05');
      dcm_set_slot_inactivity_participant_93f4e(receive_slot,1);
      goto LAB_000937a2;
    }
  }
  dcm_reset_receive_slot_and_optionally_shared_response_93c9a(receive_slot,1);
LAB_000937a2:
  dcm_set_slot_receiving_and_rewind_on_one_93e5c(receive_slot,1);
  return 1;
}

int dcm_classify_receive_slot_and_collect_displacements_937b0(ushort param_1,ushort param_2,int param_3,byte *param_4)

{
  uint32_t puVar1;
  uint32_t puVar2;
  undefined2 uVar3;
  undefined2 extraout_r7;
  undefined4 extraout_r7_00;
  int iVar4;
  int iVar5;
  uint uVar6;
  int iVar7;
  short sVar8;
  short *psVar9;
  
  puVar1 = 0xfebeb800u;
  puVar2 = 0x23dfcu;
  *param_4 = 0;
  iVar4 = dcm_get_request_phase_92624();
  if (iVar4 == 0) {
    iVar5 = dcm_get_paired_slot_receiving_flag_93f30((uint)(ushort)param_1);
    iVar4 = 0x10;
    if (iVar5 == 1) {
      (*((undefined2 *)camry_host_ptr((uint32_t)((uint)*param_4 * 4 + param_3)))) =
           (*((undefined2 *)camry_host_ptr((uint32_t)(puVar2 + (short)param_1 * 0xc + 0x20f4))));
      (*((undefined1 *)camry_host_ptr((uint32_t)((uint)*param_4 * 4 + param_3 + 2)))) = 0;
      *param_4 = 1;
    }
    goto LAB_00093902;
  }
  if (iVar4 == 1) {
    iVar4 = dcm_slot_matches_pending_protocol_and_connection_94014((uint)(ushort)param_1);
    if (iVar4 == 1) {
      iVar4 = dcm_get_paired_slot_receiving_flag_93f30((uint)(ushort)param_1);
      if (iVar4 == 1) {
        (*((undefined2 *)camry_host_ptr((uint32_t)((uint)*param_4 * 4 + param_3)))) =
             (*((undefined2 *)camry_host_ptr((uint32_t)(puVar2 + (short)param_1 * 0xc + 0x20f4))));
        (*((undefined1 *)camry_host_ptr((uint32_t)((uint)*param_4 * 4 + param_3 + 2)))) = 0;
        *param_4 = 1;
      }
      iVar4 = 0x12;
      if (param_1 == param_2) {
        iVar4 = 0x11;
      }
      goto LAB_00093902;
    }
    uVar6 = dcm_compare_protocol_priority(param_1,param_2);
    if (uVar6 == 2) {
      iVar4 = 0x13;
      iVar5 = dcm_get_slot_receiving_flag_93e32((uint)(ushort)param_2);
      iVar7 = dcm_get_paired_slot_receiving_flag_93f30(param_1);
      if (iVar5 == 1) {
        (*((ushort *)camry_host_ptr((uint32_t)((uint)*param_4 * 4 + param_3)))) = param_2;
        (*((undefined1 *)camry_host_ptr((uint32_t)((uint)*param_4 * 4 + param_3 + 2)))) = 0;
        *param_4 = 1;
      }
      if (iVar7 == 1) {
        (*((undefined2 *)camry_host_ptr((uint32_t)((uint)*param_4 * 4 + param_3)))) =
             (*((undefined2 *)camry_host_ptr((uint32_t)(puVar2 + (short)param_1 * 0xc + 0x20f4))));
        (*((undefined1 *)camry_host_ptr((uint32_t)((uint)*param_4 * 4 + param_3 + 2)))) = 0;
        *param_4 = *param_4 + 1;
      }
      goto LAB_00093902;
    }
  }
  else {
    uVar6 = dcm_compare_protocol_priority(param_1,param_2);
    if (uVar6 == 2) {
      iVar4 = 0x13;
      (*((undefined2 *)camry_host_ptr((uint32_t)((uint)*param_4 * 4 + param_3)))) = (uint)(ushort)param_2;
      (*((undefined1 *)camry_host_ptr((uint32_t)((uint)*param_4 * 4 + param_3 + 2)))) = 1;
      *param_4 = 1;
      iVar5 = dcm_get_paired_slot_receiving_flag_93f30((uint)(ushort)param_1);
      if (iVar5 == 1) {
        (*((undefined2 *)camry_host_ptr((uint32_t)((uint)*param_4 * 4 + param_3)))) =
             (*((undefined2 *)camry_host_ptr((uint32_t)(puVar2 + (short)param_1 * 0xc + 0x20f4))));
        (*((undefined1 *)camry_host_ptr((uint32_t)((uint)*param_4 * 4 + param_3 + 2)))) = 0;
        *param_4 = 2;
      }
      goto LAB_00093902;
    }
  }
  iVar4 = 0;
LAB_00093902:
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(0x2090))))) == '\x01') {
    if ((iVar4 != 0x10) && (iVar4 != 0x12 && iVar4 != 0x13)) {
      return iVar4;
    }
    uVar3 = 0xffff;
    psVar9 = ((short *)camry_host_ptr((uint32_t)(puVar2 + (short)param_1 * 0xc + 0x20ec)));
    if (iVar4 != 0x10) {
      uVar3 = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar2 + (short)param_2 * 0xc + 0x20f6))));
    }
    iVar5 = ((void)(uVar3), (void)((*((undefined2 *)camry_host_ptr((uint32_t)(puVar2 + (short)param_1 * 0xc + 0x20f6))))), return_const_0_92040());
    if (iVar5 != 0) {
      return 0;
    }
    sVar8 = *psVar9;
    thunk_push_priority_mask_and_raise_to_ff00_6a45e();
  }
  else {
    thunk_push_priority_mask_and_raise_to_ff00_6a45e();
    sVar8 = (*((short *)camry_host_ptr((uint32_t)(puVar2 + (short)param_1 * 0xc + 0x20ec))));
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x5e2c))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(sVar8 * 0x14 + 0x20d4)))));
  thunk_pop_and_restore_priority_mask_stack_6a4c4();
  return iVar4;
}

uint dcm_arbitrate_completed_receive(ushort receive_slot)

{
  uint8_t stack_record_19[28];
  short *psVar1;
  int iVar2;
  undefined8 uVar3;
  undefined4 uVar4;
  int iVar5;
  uint uVar6;
  
  uVar3 = 0x23dfc00000000;
  ((int8_t *)((stack_record_19 + 3)))[0] = '\0';
  (*((int16_t *)(stack_record_19 + 1))) = 0;
  stack_record_19[0] = '\0';
  iVar5 = check_buffered_functional_suppressed_tester_present_91b84((uint)(ushort)receive_slot);
  if (iVar5 == 1) {
    iVar5 = dcm_get_request_phase_92624();
    uVar6 = 0;
    if (iVar5 == 1) {
      uVar6 = 0x20;
    }
  }
  else {
    uVar4 = dcm_get_pending_dispatch_receive_slot_9400e();
    uVar6 = dcm_classify_receive_slot_and_collect_displacements_937b0(receive_slot, uVar4, camry_host_addr(((int16_t *)((stack_record_19 + 1)))), ((int8_t *)(stack_record_19)));
  }
  if (uVar6 == 0x20) {
    dcm_reset_receive_slot_and_optionally_shared_response_93c9a(receive_slot,1);
    uVar4 = 1;
  }
  else {
    if (uVar6 != 0) {
      for (iVar5 = 0; iVar2 = (int)stack_record_19[0],
          iVar5 - iVar2 < 0 != (iVar5 < 0 != iVar2 < 0 && iVar2 < 0 == iVar5 - iVar2 < 0);
          iVar5 = (int)(char)((char)iVar5 + '\x01')) {
        psVar1 = (short *)(((int8_t *)((stack_record_19 + 3))) + iVar5 * 4 + -2);
        if (((int8_t *)((stack_record_19 + 3)))[iVar5 * 4] == '\0') {
          iVar2 = (int)((ulonglong)uVar3 >> 0x20);
          if ((*((char *)camry_host_ptr((uint32_t)((*((volatile int16_t *)camry_host_ptr((uint32_t)(*psVar1 * 0xc + iVar2 + 0x20ec)))) * 0x14 + iVar2 + 0x20d5)))) ==
              '\x01') {
            dcm_enqueue_event('\'');
            dcm_enqueue_receive_slot_in_two_entry_ring_9405c(*psVar1);
            dcm_set_receive_slot_abort_pending_93ef6(*psVar1,1);
          }
        }
        else {
          thunk_dcm_request_response_stop_and_save_displaced_id_935b6();
        }
        dcm_reset_receive_slot_and_optionally_shared_response_93c9a(*psVar1,1);
      }
      if (uVar6 != 0x13) {
        return uVar6;
      }
      dcm_invalidate_queued_event('*','\0');
      dcm_enqueue_event('*');
      clear_all_dcm_connection_activity_requests_91a24();
      return 0x13;
    }
    uVar4 = dcm_get_slot_inactivity_participant_93f5a(receive_slot);
    dcm_reset_receive_slot_and_optionally_shared_response_93c9a(receive_slot,1);
  }
  arm_dcm_inactivity_timer_if_no_other_participant_91f26(receive_slot,uVar4);
  return uVar6;
}

undefined4 dcm_get_cached_protocol_byte_93a70(undefined1 *param_1)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  thunk_push_priority_mask_and_raise_to_ff00_6a45e();
  *param_1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x5e2c)))));
  thunk_pop_and_restore_priority_mask_stack_6a4c4();
  return 0;
}

undefined4 dcm_receiving_slot_count_exceeds_phase_allowance_93a8c(void)

{
  ushort uVar1;
  int iVar2;
  
  iVar2 = dcm_get_request_phase_92624();
  uVar1 = dcm_count_receiving_slots();
  if (iVar2 == 2) {
    if (uVar1 < 2) {
      return 0;
    }
  }
  else if (uVar1 == 0) {
    return 0;
  }
  return 1;
}

void dcm_invalidate_cached_protocol_byte_93ab2(void)

{
  DAT_febe59d4 = 0xff;
  return;
}

void dcm_initialize_receive_buffers_and_transport_state_93aba(void)

{
  uint uVar1;
  uint uVar2;
  uchar *puVar3;
  uint uVar4;
  
  dcm_pending_transport_accepted = '\0';
  ((volatile uint8_t *)camry_host_ptr(0xfebe5a20u))[0] = '\0';
  dcm_pending_dispatch_receive_slot = 0;
  dcm_current_dispatch_receive_slot = 0;
  dcm_retained_p2_star_raw = 0;
  dcm_pending_spacing_raw = 0;
  DAT_febe59e4 = 0;
  DAT_febe59e6 = 0;
  dcm_displaced_transmit_id = 0;
  dcm_zero_p2_deadline = '\0';
  dcm_zero_overall_timeout = '\0';
  uVar4 = 0;
  do {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe59f0u + (uint32_t)(uVar4) * (uint32_t)sizeof(F33DcmReceiveBufferState)) + (uint32_t)(0) * (uint32_t)sizeof(F33DcmReceiveBufferState) + (uint32_t)offsetof(F33DcmReceiveBufferState, receiving))))) = '\0';
    puVar3 = ((void *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)((uint32_t)(0x25e90u + (uint32_t)(uVar4) * (uint32_t)sizeof(F33DcmReceiveBufferConfiguration)) + (uint32_t)(0) * (uint32_t)sizeof(F33DcmReceiveBufferConfiguration) + (uint32_t)offsetof(F33DcmReceiveBufferConfiguration, base))))))));
    uVar1 = uVar4 + 1;
    (*((volatile uint32_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe59f0u + (uint32_t)(uVar4) * (uint32_t)sizeof(F33DcmReceiveBufferState)) + (uint32_t)(0) * (uint32_t)sizeof(F33DcmReceiveBufferState) + (uint32_t)offsetof(F33DcmReceiveBufferState, write_cursor))))) = camry_host_addr(puVar3);
    *puVar3 = '\0';
    uVar2 = (*((volatile uint32_t *)camry_host_ptr((uint32_t)((uint32_t)(0x25e90u + (uint32_t)(uVar4) * (uint32_t)sizeof(F33DcmReceiveBufferConfiguration)) + (uint32_t)(0) * (uint32_t)sizeof(F33DcmReceiveBufferConfiguration) + (uint32_t)offsetof(F33DcmReceiveBufferConfiguration, capacity)))));
    (*((volatile uint16_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe59f0u + (uint32_t)(uVar4) * (uint32_t)sizeof(F33DcmReceiveBufferState)) + (uint32_t)(0) * (uint32_t)sizeof(F33DcmReceiveBufferState) + (uint32_t)offsetof(F33DcmReceiveBufferState, received_length))))) = 0;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe59f0u + (uint32_t)(uVar4) * (uint32_t)sizeof(F33DcmReceiveBufferState)) + (uint32_t)(0) * (uint32_t)sizeof(F33DcmReceiveBufferState) + (uint32_t)offsetof(F33DcmReceiveBufferState, abort_pending))))) = '\0';
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe59f0u + (uint32_t)(uVar4) * (uint32_t)sizeof(F33DcmReceiveBufferState)) + (uint32_t)(0) * (uint32_t)sizeof(F33DcmReceiveBufferState) + (uint32_t)offsetof(F33DcmReceiveBufferState, inactivity_participant))))) = '\0';
    (*((volatile uint16_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe59f0u + (uint32_t)(uVar4) * (uint32_t)sizeof(F33DcmReceiveBufferState)) + (uint32_t)(0) * (uint32_t)sizeof(F33DcmReceiveBufferState) + (uint32_t)offsetof(F33DcmReceiveBufferState, remaining_capacity))))) = (ushort)uVar2;
    uVar4 = uVar1;
  } while (uVar1 < 3);
  return;
}

ushort dcm_get_current_protocol_inactivity_timeout_93b18(void)

{
  int slot;
  int protocol;

  slot = (int)(int16_t)dcm_current_dispatch_receive_slot;
  protocol = (int)(int16_t)*(volatile uint16_t *)camry_host_ptr((uint32_t)(0x25ee8 + slot * 12));
  return *(volatile uint16_t *)camry_host_ptr((uint32_t)(0x25ec8 + protocol * 20));
}

void dcm_get_receive_route_indices_93b32(short param_1,ushort *param_2,ushort *param_3,ushort *param_4)

{
  *param_2 = (*((volatile uint16_t *)camry_host_ptr((uint32_t)((uint32_t)(0x25ee8u + (int32_t)(int16_t)param_1 * (uint32_t)sizeof(F33DcmReceiveRoute)) + (uint32_t)(0) * (uint32_t)sizeof(F33DcmReceiveRoute) + (uint32_t)offsetof(F33DcmReceiveRoute, protocol_index)))));
  *param_3 = (*((volatile uint16_t *)camry_host_ptr((uint32_t)((uint32_t)(0x25ee8u + (int32_t)(int16_t)param_1 * (uint32_t)sizeof(F33DcmReceiveRoute)) + (uint32_t)(0) * (uint32_t)sizeof(F33DcmReceiveRoute) + (uint32_t)offsetof(F33DcmReceiveRoute, connection_index)))));
  *param_4 = (*((volatile uint16_t *)camry_host_ptr((uint32_t)((uint32_t)(0x25ee8u + (int32_t)(int16_t)param_1 * (uint32_t)sizeof(F33DcmReceiveRoute)) + (uint32_t)(0) * (uint32_t)sizeof(F33DcmReceiveRoute) + (uint32_t)offsetof(F33DcmReceiveRoute, receive_descriptor_index)))));
  return;
}

uint dcm_get_overall_request_timeout(void)

{
  uint8_t stack_record_a[10];
  int *piVar1;
  int iVar2;
  int iVar3;
  uint32_t puVar4;
  uint32_t puVar5;
  uint uVar6;
  
  puVar4 = 0xfebeb800u;
  puVar5 = 0x23dfcu;
  (*((int16_t *)(stack_record_a + 0))) = 0;
  (*((uint16_t *)(stack_record_a + 2))) = 0;
  (*((uint16_t *)(stack_record_a + 4))) = 0;
  dcm_get_receive_route_indices_93b32(dcm_pending_dispatch_receive_slot,stack_record_a,(stack_record_a + 2),(stack_record_a + 4));
  iVar3 = (uint)(*((uint16_t *)(stack_record_a + 2))) * 4;
  piVar1 = ((int *)camry_host_ptr((uint32_t)(puVar5 + (*((int16_t *)(stack_record_a + 0))) * 0x14 + 0x20c4)));
  iVar2 = (uint)(*((uint16_t *)(stack_record_a + 4))) * 0xc;
  if (((*((char *)camry_host_ptr((uint32_t)((*((volatile int32_t *)camry_host_ptr((uint32_t)((*((volatile int32_t *)camry_host_ptr((uint32_t)(*piVar1 + iVar3)))) + 4)))) + iVar2 + 9)))) == '\x01') &&
     ((*((char *)camry_host_ptr((uint32_t)((*((volatile int32_t *)camry_host_ptr((uint32_t)((*((volatile int32_t *)camry_host_ptr((uint32_t)(*piVar1 + iVar3)))) + 4)))) + iVar2 + 8)))) == '\x01')) {
    uVar6 = (*((uint *)camry_host_ptr((uint32_t)((*((volatile int32_t *)camry_host_ptr((uint32_t)((*((volatile int32_t *)camry_host_ptr((uint32_t)(*piVar1 + iVar3)))) + 4)))) + iVar2))));
  }
  else {
    uVar6 = piVar1[1];
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x5e14))))) = uVar6 == 0;
  return uVar6;
}

ushort dcm_select_response_deadline(uchar use_retained,uchar use_current_session)

{
  uint8_t stack_record_b[11];
  ushort uVar1;
  ushort uVar2;
  uint32_t puVar3;
  uint32_t puVar4;
  short sVar5;
  int iVar6;
  
  puVar3 = 0xfebeb800u;
  puVar4 = 0x23dfcu;
  uVar1 = (*((volatile uint16_t *)camry_host_ptr((uint32_t)((uint32_t)(0x25ee8u + (uint32_t)((short)dcm_pending_dispatch_receive_slot) * (uint32_t)sizeof(F33DcmReceiveRoute)) + (uint32_t)(0) * (uint32_t)sizeof(F33DcmReceiveRoute) + (uint32_t)offsetof(F33DcmReceiveRoute, protocol_index)))));
  stack_record_b[0] = '\x01';
  (*((uint16_t *)(stack_record_b + 1))) = 0;
  uVar2 = dcm_retained_p2_star_raw;
  if (use_retained != '\x01') {
    if (use_current_session == '\x01') {
      dcm_get_session(((uint8_t *)(stack_record_b)));
    }
    lookup_session_three_timing_values_92064(stack_record_b[0], ((uint16_t *)((stack_record_b + 1))), ((undefined *)camry_host_ptr((uint32_t)(puVar3 + -0x5e28))), ((undefined *)camry_host_ptr((uint32_t)(puVar3 + -0x5e26))));
    iVar6 = (short)uVar1 * 0x14;
    uVar2 = (*((uint16_t *)(stack_record_b + 1)));
    if ((*((ushort *)camry_host_ptr((uint32_t)(puVar4 + iVar6 + 0x20d0)))) <= (*((uint16_t *)(stack_record_b + 1)))) {
      uVar2 = (*((uint16_t *)(stack_record_b + 1))) - (*((short *)camry_host_ptr((uint32_t)(puVar4 + iVar6 + 0x20d0))));
    }
    sVar5 = 0;
    if ((*((ushort *)camry_host_ptr((uint32_t)(puVar4 + iVar6 + 0x20d2)))) <= (*((ushort *)camry_host_ptr((uint32_t)(puVar3 + -0x5e28))))) {
      sVar5 = (*((ushort *)camry_host_ptr((uint32_t)(puVar3 + -0x5e28)))) - (*((short *)camry_host_ptr((uint32_t)(puVar4 + iVar6 + 0x20d2))));
    }
    (*((short *)camry_host_ptr((uint32_t)(puVar3 + -0x5e28)))) = sVar5;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x5e15))))) = uVar2 == 0;
  }
  return uVar2;
}

ushort dcm_get_pending_spacing_raw_93c5a(void)

{
  return dcm_pending_spacing_raw;
}

ushort dcm_get_current_dispatch_receive_slot_93c60(void)

{
  return dcm_current_dispatch_receive_slot;
}

void dcm_set_current_dispatch_receive_slot_93c66(ushort param_1)

{
  dcm_current_dispatch_receive_slot = param_1;
  return;
}

void dcm_rewind_receive_cursor_and_get_received_pdu_93c6c(uint param_1,undefined4 *param_2)

{
  uint32_t puVar1;
  
  param_1 = param_1 & 0xffff;
  puVar1 = ((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)((uint32_t)(0x25e90u + (uint32_t)(param_1) * (uint32_t)sizeof(F33DcmReceiveBufferConfiguration)) + (uint32_t)(0) * (uint32_t)sizeof(F33DcmReceiveBufferConfiguration) + (uint32_t)offsetof(F33DcmReceiveBufferConfiguration, base)))))));
  (*((volatile uint32_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe59f0u + (uint32_t)(param_1) * (uint32_t)sizeof(F33DcmReceiveBufferState)) + (uint32_t)(0) * (uint32_t)sizeof(F33DcmReceiveBufferState) + (uint32_t)offsetof(F33DcmReceiveBufferState, write_cursor))))) = (puVar1);
  *param_2 = (puVar1);
  *(ushort *)(param_2 + 1) = (*((volatile uint16_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe59f0u + (uint32_t)(param_1) * (uint32_t)sizeof(F33DcmReceiveBufferState)) + (uint32_t)(0) * (uint32_t)sizeof(F33DcmReceiveBufferState) + (uint32_t)offsetof(F33DcmReceiveBufferState, received_length)))));
  return;
}

uchar dcm_get_pending_transport_accepted_93c8e(void)

{
  return dcm_pending_transport_accepted;
}

void dcm_set_pending_transport_accepted_93c94(uchar param_1)

{
  dcm_pending_transport_accepted = param_1;
  return;
}

void dcm_reset_receive_slot_and_optionally_shared_response_93c9a(uint param_1,char param_2)

{
  uchar *puVar1;
  uint uVar2;
  
  param_1 = param_1 & 0xffff;
  if (param_2 == '\0') {
    ((volatile uint8_t *)camry_host_ptr(0xfebe5a20u))[0] = '\0';
    dcm_pending_transport_accepted = '\0';
  }
  puVar1 = ((void *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)((uint32_t)(0x25e90u + (uint32_t)(param_1) * (uint32_t)sizeof(F33DcmReceiveBufferConfiguration)) + (uint32_t)(0) * (uint32_t)sizeof(F33DcmReceiveBufferConfiguration) + (uint32_t)offsetof(F33DcmReceiveBufferConfiguration, base))))))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe59f0u + (uint32_t)(param_1) * (uint32_t)sizeof(F33DcmReceiveBufferState)) + (uint32_t)(0) * (uint32_t)sizeof(F33DcmReceiveBufferState) + (uint32_t)offsetof(F33DcmReceiveBufferState, receiving))))) = '\0';
  (*((volatile uint32_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe59f0u + (uint32_t)(param_1) * (uint32_t)sizeof(F33DcmReceiveBufferState)) + (uint32_t)(0) * (uint32_t)sizeof(F33DcmReceiveBufferState) + (uint32_t)offsetof(F33DcmReceiveBufferState, write_cursor))))) = camry_host_addr(puVar1);
  *puVar1 = '\0';
  uVar2 = (*((volatile uint32_t *)camry_host_ptr((uint32_t)((uint32_t)(0x25e90u + (uint32_t)(param_1) * (uint32_t)sizeof(F33DcmReceiveBufferConfiguration)) + (uint32_t)(0) * (uint32_t)sizeof(F33DcmReceiveBufferConfiguration) + (uint32_t)offsetof(F33DcmReceiveBufferConfiguration, capacity)))));
  (*((volatile uint16_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe59f0u + (uint32_t)(param_1) * (uint32_t)sizeof(F33DcmReceiveBufferState)) + (uint32_t)(0) * (uint32_t)sizeof(F33DcmReceiveBufferState) + (uint32_t)offsetof(F33DcmReceiveBufferState, received_length))))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe59f0u + (uint32_t)(param_1) * (uint32_t)sizeof(F33DcmReceiveBufferState)) + (uint32_t)(0) * (uint32_t)sizeof(F33DcmReceiveBufferState) + (uint32_t)offsetof(F33DcmReceiveBufferState, inactivity_participant))))) = '\0';
  (*((volatile uint16_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe59f0u + (uint32_t)(param_1) * (uint32_t)sizeof(F33DcmReceiveBufferState)) + (uint32_t)(0) * (uint32_t)sizeof(F33DcmReceiveBufferState) + (uint32_t)offsetof(F33DcmReceiveBufferState, remaining_capacity))))) = (ushort)uVar2;
  return;
}

void dcm_get_route_protocol_and_connection_indices_93cce(ushort param_1,ushort *param_2,ushort *param_3)

{
  *param_2 = (*((volatile uint16_t *)camry_host_ptr((uint32_t)((uint32_t)(0x25ee8u + (int32_t)(int16_t)param_1 * (uint32_t)sizeof(F33DcmReceiveRoute)) + (uint32_t)(0) * (uint32_t)sizeof(F33DcmReceiveRoute) + (uint32_t)offsetof(F33DcmReceiveRoute, protocol_index)))));
  *param_3 = (*((volatile uint16_t *)camry_host_ptr((uint32_t)((uint32_t)(0x25ee8u + (int32_t)(int16_t)param_1 * (uint32_t)sizeof(F33DcmReceiveRoute)) + (uint32_t)(0) * (uint32_t)sizeof(F33DcmReceiveRoute) + (uint32_t)offsetof(F33DcmReceiveRoute, connection_index)))));
  return;
}

void dcm_get_shared_response_buffer_and_connection_limit_93ce6(undefined4 *param_1)

{
  uint8_t stack_record_c[12];
  uint32_t puVar1;
  uint32_t puVar2;
  puVar1 = 0xfebeb800u;
  puVar2 = 0x23dfcu;
  (*((int16_t *)(stack_record_c + 0))) = 0;
  (*((uint16_t *)(stack_record_c + 2))) = 0;
  dcm_get_route_protocol_and_connection_indices_93cce(dcm_current_dispatch_receive_slot,((int16_t *)(stack_record_c)),((uint16_t *)((stack_record_c + 2))));
  *param_1 = puVar1 + -0x5de0;
  *(short *)(param_1 + 1) =
       (short)*(((undefined4 *)camry_host_ptr((*((volatile uint32_t *)camry_host_ptr((uint32_t)((*((volatile int32_t *)camry_host_ptr((uint32_t)((uint)(*((uint16_t *)(stack_record_c + 2))) * 4 + (*((volatile int32_t *)camry_host_ptr((uint32_t)(puVar2 + (*((int16_t *)(stack_record_c + 0))) * 0x14 + 0x20c4)))))))) + 8)))))));
  return;
}

undefined1 dcm_current_receive_descriptor_flags_eight_and_nine_set_93d2e(void)

{
  uint8_t stack_record_e[14];
  uint32_t puVar1;
  undefined1 uVar2;
  
  puVar1 = 0x23dfcu;
  (*((int16_t *)(stack_record_e + 0))) = 0;
  uVar2 = 0;
  (*((uint16_t *)(stack_record_e + 2))) = 0;
  (*((uint16_t *)(stack_record_e + 4))) = 0;
  dcm_get_receive_route_indices_93b32(dcm_current_dispatch_receive_slot,stack_record_e,(stack_record_e + 2),(stack_record_e + 4));
  if ((*((char *)camry_host_ptr((uint32_t)((*((volatile int32_t *)camry_host_ptr((uint32_t)((*((volatile int32_t *)camry_host_ptr((uint32_t)((*((volatile int32_t *)camry_host_ptr((uint32_t)(puVar1 + (*((int16_t *)(stack_record_e + 0))) * 0x14 + 0x20c4)))) + (uint)(*((uint16_t *)(stack_record_e + 2))) * 4))))
                        + 4)))) + (uint)(*((uint16_t *)(stack_record_e + 4))) * 0xc + 9)))) == '\x01') {
    if ((*((char *)camry_host_ptr((uint32_t)((*((volatile int32_t *)camry_host_ptr((uint32_t)((*((volatile int32_t *)camry_host_ptr((uint32_t)((*((volatile int32_t *)camry_host_ptr((uint32_t)(puVar1 + (*((int16_t *)(stack_record_e + 0))) * 0x14 + 0x20c4)))) + (uint)(*((uint16_t *)(stack_record_e + 2))) * 4)))) + 4)))) + (uint)(*((uint16_t *)(stack_record_e + 4))) * 0xc + 8)))) == '\x01') {
      uVar2 = 1;
    }
    else {
      uVar2 = 0;
    }
  }
  return uVar2;
}

undefined1 dcm_get_current_receive_descriptor_flag_nine_93d9a(void)

{
  uint8_t stack_record_a[10];
  uint32_t puVar1;
  puVar1 = 0x23dfcu;
  (*((int16_t *)(stack_record_a + 0))) = 0;
  (*((uint16_t *)(stack_record_a + 2))) = 0;
  (*((uint16_t *)(stack_record_a + 4))) = 0;
  dcm_get_receive_route_indices_93b32(dcm_current_dispatch_receive_slot,stack_record_a,(stack_record_a + 2),(stack_record_a + 4));
  return (*((undefined1 *)camry_host_ptr((uint32_t)((uint)(*((uint16_t *)(stack_record_a + 4))) * 0xc +
           (*((volatile int32_t *)camry_host_ptr((uint32_t)((*((volatile int32_t *)camry_host_ptr((uint32_t)((uint)(*((uint16_t *)(stack_record_a + 2))) * 4 + (*((volatile int32_t *)camry_host_ptr((uint32_t)(puVar1 + (*((int16_t *)(stack_record_a + 0))) * 0x14 + 0x20c4)))))))) + 4))))
          + 9))));
}

uint dcm_append_receive_chunk(ushort receive_slot,F33PduInfo *chunk,ushort *available)

{
  F33DcmReceiveBufferState *pFVar1;
  uchar uVar2;
  ushort uVar3;
  uchar *puVar4;
  
  puVar4 = ((void *)camry_host_ptr((uint32_t)(chunk->data)));
  uVar3 = 0;
  while( true ) {
    pFVar1 = ((volatile F33DcmReceiveBufferState *)camry_host_ptr((uint32_t)(0xfebe59f0u + (uint32_t)(receive_slot) * (uint32_t)sizeof(F33DcmReceiveBufferState))));
    if (chunk->length <= uVar3) break;
    uVar3 = uVar3 + 1;
    uVar2 = *puVar4;
    puVar4 = puVar4 + 1;
    *((uint8_t *)camry_host_ptr((uint32_t)(pFVar1->write_cursor))) = uVar2;
    pFVar1->write_cursor = pFVar1->write_cursor + 1;
  }
  (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe59f0u + (uint32_t)(receive_slot) * (uint32_t)sizeof(F33DcmReceiveBufferState) + (uint32_t)offsetof(F33DcmReceiveBufferState, received_length))))) =
       (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe59f0u + (uint32_t)(receive_slot) * (uint32_t)sizeof(F33DcmReceiveBufferState) + (uint32_t)offsetof(F33DcmReceiveBufferState, received_length))))) + chunk->length;
  uVar3 = (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe59f0u + (uint32_t)(receive_slot) * (uint32_t)sizeof(F33DcmReceiveBufferState) + (uint32_t)offsetof(F33DcmReceiveBufferState, remaining_capacity))))) - chunk->length;
  (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe59f0u + (uint32_t)(receive_slot) * (uint32_t)sizeof(F33DcmReceiveBufferState) + (uint32_t)offsetof(F33DcmReceiveBufferState, remaining_capacity))))) = uVar3;
  *available = uVar3;
  return 0;
}

uchar dcm_get_slot_receiving_flag_93e32(uint param_1)

{
  return (*((volatile uint8_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe59f0u + (uint32_t)(param_1 & 0xffff) * (uint32_t)sizeof(F33DcmReceiveBufferState)) + (uint32_t)(0) * (uint32_t)sizeof(F33DcmReceiveBufferState) + (uint32_t)offsetof(F33DcmReceiveBufferState, receiving)))));
}

ushort dcm_count_receiving_slots(void)

{
  uint uVar1;
  ushort uVar2;
  
  uVar2 = 0;
  uVar1 = 0;
  do {
    if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe59f0u + (uint32_t)(uVar1) * (uint32_t)sizeof(F33DcmReceiveBufferState)) + (uint32_t)(0) * (uint32_t)sizeof(F33DcmReceiveBufferState) + (uint32_t)offsetof(F33DcmReceiveBufferState, receiving))))) == '\x01') {
      uVar2 = uVar2 + 1;
    }
    uVar1 = uVar1 + 1;
  } while (uVar1 < 3);
  return uVar2;
}

void dcm_set_slot_receiving_and_rewind_on_one_93e5c(uint param_1,uchar param_2)

{
  param_1 = param_1 & 0xffff;
  if (param_2 == '\x01') {
    (*((volatile uint32_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe59f0u + (uint32_t)(param_1) * (uint32_t)sizeof(F33DcmReceiveBufferState)) + (uint32_t)(0) * (uint32_t)sizeof(F33DcmReceiveBufferState) + (uint32_t)offsetof(F33DcmReceiveBufferState, write_cursor))))) =
         (*((volatile uint32_t *)camry_host_ptr((uint32_t)((uint32_t)(0x25e90u + (uint32_t)(param_1) * (uint32_t)sizeof(F33DcmReceiveBufferConfiguration)) + (uint32_t)(0) * (uint32_t)sizeof(F33DcmReceiveBufferConfiguration) + (uint32_t)offsetof(F33DcmReceiveBufferConfiguration, base)))));
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe59f0u + (uint32_t)(param_1) * (uint32_t)sizeof(F33DcmReceiveBufferState)) + (uint32_t)(0) * (uint32_t)sizeof(F33DcmReceiveBufferState) + (uint32_t)offsetof(F33DcmReceiveBufferState, receiving))))) = param_2;
  return;
}

undefined2 dcm_get_current_transmit_id_93e82(void)

{
  uint8_t stack_record_8[8];
  uint32_t puVar1;
  puVar1 = 0x23dfcu;
  (*((int16_t *)(stack_record_8 + 0))) = 0;
  (*((uint16_t *)(stack_record_8 + 2))) = 0;
  dcm_get_route_protocol_and_connection_indices_93cce(dcm_current_dispatch_receive_slot,((int16_t *)(stack_record_8)),((uint16_t *)((stack_record_8 + 2))));
  return (*((undefined2 *)camry_host_ptr((uint32_t)((*((volatile int32_t *)camry_host_ptr((uint32_t)((*((volatile int32_t *)camry_host_ptr((uint32_t)((uint)(*((uint16_t *)(stack_record_8 + 2))) * 4 + (*((volatile int32_t *)camry_host_ptr((uint32_t)(puVar1 + (*((int16_t *)(stack_record_8 + 0))) * 0x14 + 0x20c4)))))))) + 8)))) +
          6))));
}

undefined2 dcm_get_current_confirmation_id_93ebc(void)

{
  uint8_t stack_record_8[8];
  uint32_t puVar1;
  puVar1 = 0x23dfcu;
  (*((int16_t *)(stack_record_8 + 0))) = 0;
  (*((uint16_t *)(stack_record_8 + 2))) = 0;
  dcm_get_route_protocol_and_connection_indices_93cce(dcm_current_dispatch_receive_slot,((int16_t *)(stack_record_8)),((uint16_t *)((stack_record_8 + 2))));
  return (*((undefined2 *)camry_host_ptr((uint32_t)((*((volatile int32_t *)camry_host_ptr((uint32_t)((*((volatile int32_t *)camry_host_ptr((uint32_t)((uint)(*((uint16_t *)(stack_record_8 + 2))) * 4 + (*((volatile int32_t *)camry_host_ptr((uint32_t)(puVar1 + (*((int16_t *)(stack_record_8 + 0))) * 0x14 + 0x20c4)))))))) + 8)))) +
          4))));
}

void dcm_set_receive_slot_abort_pending_93ef6(uint param_1,uchar param_2)

{
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe59f0u + (uint32_t)(param_1 & 0xffff) * (uint32_t)sizeof(F33DcmReceiveBufferState)) + (uint32_t)(0) * (uint32_t)sizeof(F33DcmReceiveBufferState) + (uint32_t)offsetof(F33DcmReceiveBufferState, abort_pending))))) = param_2;
  return;
}

uchar dcm_get_receive_slot_abort_pending_93f02(uint param_1)

{
  return (*((volatile uint8_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe59f0u + (uint32_t)(param_1 & 0xffff) * (uint32_t)sizeof(F33DcmReceiveBufferState)) + (uint32_t)(0) * (uint32_t)sizeof(F33DcmReceiveBufferState) + (uint32_t)offsetof(F33DcmReceiveBufferState, abort_pending)))));
}

uint dcm_find_receive_slot_by_receive_id_93f0e(ushort param_1)

{
  uint uVar1;
  
  uVar1 = 0;
  do {
    if (param_1 == (*((volatile uint16_t *)camry_host_ptr((uint32_t)((uint32_t)(0x25ee8u + (uint32_t)((short)uVar1) * (uint32_t)sizeof(F33DcmReceiveRoute)) + (uint32_t)(0) * (uint32_t)sizeof(F33DcmReceiveRoute) + (uint32_t)offsetof(F33DcmReceiveRoute, receive_id)))))) {
      return uVar1;
    }
    uVar1 = uVar1 + 1;
  } while (uVar1 < 3);
  return 0xffff;
}

uchar dcm_get_paired_slot_receiving_flag_93f30(short param_1)

{
  if ((*((volatile uint16_t *)camry_host_ptr((uint32_t)((uint32_t)(0x25ee8u + (int32_t)(int16_t)param_1 * (uint32_t)sizeof(F33DcmReceiveRoute)) + (uint32_t)(0) * (uint32_t)sizeof(F33DcmReceiveRoute) + (uint32_t)offsetof(F33DcmReceiveRoute, paired_receive_slot_or_ffff))))) != 0xffff) {
    return (*((volatile uint8_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe59f0u + (uint32_t)((*((volatile uint16_t *)camry_host_ptr((uint32_t)((uint32_t)(0x25ee8u + (int32_t)(int16_t)param_1 * (uint32_t)sizeof(F33DcmReceiveRoute)) + (uint32_t)(0) * (uint32_t)sizeof(F33DcmReceiveRoute) + (uint32_t)offsetof(F33DcmReceiveRoute, paired_receive_slot_or_ffff)))))) * (uint32_t)sizeof(F33DcmReceiveBufferState)) + (uint32_t)(0) * (uint32_t)sizeof(F33DcmReceiveBufferState) + (uint32_t)offsetof(F33DcmReceiveBufferState, receiving)))));
  }
  return '\0';
}

void dcm_set_slot_inactivity_participant_93f4e(uint param_1,uchar param_2)

{
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe59f0u + (uint32_t)(param_1 & 0xffff) * (uint32_t)sizeof(F33DcmReceiveBufferState)) + (uint32_t)(0) * (uint32_t)sizeof(F33DcmReceiveBufferState) + (uint32_t)offsetof(F33DcmReceiveBufferState, inactivity_participant))))) = param_2;
  return;
}

uchar dcm_get_slot_inactivity_participant_93f5a(uint param_1)

{
  return (*((volatile uint8_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe59f0u + (uint32_t)(param_1 & 0xffff) * (uint32_t)sizeof(F33DcmReceiveBufferState)) + (uint32_t)(0) * (uint32_t)sizeof(F33DcmReceiveBufferState) + (uint32_t)offsetof(F33DcmReceiveBufferState, inactivity_participant)))));
}

void dcm_collect_receiving_slots_and_mark_abort_pending_93f66(int param_1,ushort *param_2,char param_3)

{
  uint8_t stack_record_1e[32];
  undefined *puVar1;
  undefined *puVar2;
  uint32_t puVar3;
  uint uVar4;
  
  puVar3 = 0x23dfcu;
  (*((int16_t *)(stack_record_1e + 0))) = 0;
  (*((uint16_t *)(stack_record_1e + 2))) = 0;
  uVar4 = 0;
  (*((uint16_t *)(stack_record_1e + 4))) = 0;
  *param_2 = 0;
  puVar1 = ((undefined *)camry_host_ptr(0xfebeb800u));
  do {
    puVar2 = puVar1;
    if ((puVar1[uVar4 * 0x10 + -0x5e06] == '\x01') &&
       ((param_3 != '\x02' || (uVar4 != *(ushort *)(puVar1 + -0x5e1e))))) {
      dcm_get_receive_route_indices_93b32(uVar4,((int16_t *)(stack_record_1e)),((uint16_t *)((stack_record_1e + 2))),((uint16_t *)((stack_record_1e + 4))));
      (*((undefined2 *)camry_host_ptr((uint32_t)((uint)*param_2 * 4 + param_1)))) =
           (*((undefined2 *)camry_host_ptr((uint32_t)((uint)(*((uint16_t *)(stack_record_1e + 4))) * 0xc +
             (*((volatile int32_t *)camry_host_ptr((uint32_t)((*((volatile int32_t *)camry_host_ptr((uint32_t)((uint)(*((uint16_t *)(stack_record_1e + 2))) * 4 + (*((volatile int32_t *)camry_host_ptr((uint32_t)(puVar3 + (*((int16_t *)(stack_record_1e + 0))) * 0x14 + 0x20c4)))))))) +
                     4)))) + 6))));
      (*((short *)camry_host_ptr((uint32_t)((uint)*param_2 * 4 + param_1 + 2)))) = (short)uVar4;
      *param_2 = *param_2 + 1;
      puVar1[uVar4 * 0x10 + -0x5e05] = 1;
    }
    uVar4 = uVar4 + 1;
    puVar1 = puVar2;
  } while (uVar4 < 3);
  return;
}
