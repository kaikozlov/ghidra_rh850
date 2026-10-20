#include "common.h"

void set_upper_network_indication_one_and_notify_7a002(uint param_1)

{
  param_1 = param_1 & 0xff;
  if (param_1 < DAT_00021865) {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe3df0u + (uint32_t)(param_1) * 1u)))) = '\x01';
    notify_current_packet_channel_by_id_82e94(param_1);
    ((void)(param_1), return_only_stub_7be46());
  }
  return;
}

void forward_network_group_command_c0_and_notify_7a02c(byte param_1)

{
  if (param_1 < DAT_00021865) {
    clear_group_pending_and_reset_pdus_7e29c(param_1,0xc0);
    clear_queue_if_mapped_channel_is_current_82ef0(param_1);
  }
  return;
}

void forward_network_group_command_c0_and_notify_7a050(byte param_1)

{
  if (param_1 < DAT_00021865) {
    clear_group_pending_and_reset_pdus_7e29c(param_1,0xc0);
    clear_queue_if_mapped_channel_is_current_82ef0(param_1);
  }
  return;
}

void forward_bounded_network_low_two_policy_bits_7a074(byte param_1,uint param_2)

{
  uint uVar1;
  
  if (param_1 < DAT_00021865) {
    if ((param_2 >> 1 & 1) == 0) {
      uVar1 = 0;
    }
    else {
      uVar1 = 2;
    }
    if ((param_2 & 1) != 0) {
      uVar1 = uVar1 | 1;
    }
    set_tx_group_mode_pair_from_bits_7e3e0(param_1,uVar1);
  }
  return;
}

void forward_bounded_network_u16_policy_value_7a09c(byte param_1,undefined2 param_2)

{
  if (param_1 < DAT_00021865) {
    set_group_u16_timer_and_active_flag_7e412(param_1,param_2);
  }
  return;
}

void forward_network_ff_equality_boolean_7a0ba(byte param_1,char param_2)

{
  if (param_1 < DAT_00021865) {
    set_packet_channel_gate_from_boolean_82f18(param_1,param_2 == -1);
  }
  return;
}

void clear_three_network_group_request_arrays_7a0dc(void)

{
  uint uVar1;
  uint uVar2;
  
  uVar2 = (uint)DAT_00021864;
  for (uVar1 = 0; uVar1 < uVar2; uVar1 = uVar1 + 1 & 0xff) {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe3deau + (uint32_t)(uVar1) * 1u)))) = 0;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe3decu + (uint32_t)(uVar1) * 1u)))) = 0;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe3deeu + (uint32_t)(uVar1) * 1u)))) = 0;
  }
  return;
}

void initialize_enabled_network_policy_values_7a0fe(void)

{
  undefined8 uVar1;
  uint uVar2;
  uint uVar3;
  
  uVar1 = 0x23dfc00000000;
  uVar2 = (uint)DAT_00021865;
  for (uVar3 = 0; uVar3 < uVar2; uVar3 = uVar3 + 1 & 0xff) {
    if ((*((char *)camry_host_ptr((uint32_t)(uVar3 + (int)((ulonglong)uVar1 >> 0x20) + -0x2594)))) != '\0') {
      set_group_u16_timer_and_active_flag_7e412(uVar3,0);
      set_tx_group_mode_pair_from_bits_7e3e0(uVar3,3);
    }
  }
  return;
}

void initialize_communication_chain_and_publish_ready_7a132(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  DAT_febe3df2 = 0xfd02;
  clear_three_network_group_request_arrays_7a0dc();
  clear_upper_network_software_indications_79f42();
  initialize_network_enable_mask_complement_pairs_7bb9c();
  run_init_chain_79dfa();
  ((void)(0), initialize_sixteen_byte_state_records_7e782());
  return_only_stub_7be36();
  return_only_stub_7ee7e();
  ((void)(0), initialize_com_state_with_mode_one_7d880());
  initialize_enabled_network_policy_values_7a0fe();
  ((void)(0), initialize_packet_queue_and_channel_gates_82c9e());
  ((void)(0), return_only_stub_81590());
  return_only_stub_7be34();
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x7a0c))))) = 0xf;
  advance_aggregate_normal_channel_setup_state_7c43c();
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x7a0e)))) = 0xfe01;
  return;
}

void mark_not_ready_and_reset_communication_chain_7a18c(void)

{
  DAT_febe3df2 = 0xfd02;
  initialize_network_controllers_and_transport_state_79e2c();
  set_global_state_4938_ff_7e7da();
  reset_com_group_modes_and_committed_masks_7d88e();
  return_only_stub_7ee80();
  disable_packet_channels_and_reset_queue_82d38();
  return_only_stub_81592();
  return;
}

void mark_not_ready_and_reset_alternate_communication_chain_7a1b4(void)

{
  DAT_febe3df2 = 0xfd02;
  run_init_chain_79e60();
  set_global_state_4938_ff_7e7da();
  reset_com_group_modes_and_committed_masks_7d88e();
  return_only_stub_7ee80();
  disable_packet_channels_and_reset_queue_82d38();
  return_only_stub_81592();
  return;
}

void reinitialize_communication_chain_and_publish_ready_7a1dc(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  DAT_febe3df2 = 0xfd02;
  clear_three_network_group_request_arrays_7a0dc();
  clear_upper_network_software_indications_79f42();
  initialize_network_enable_mask_complement_pairs_7bb9c();
  run_init_chain_79e84();
  ((void)(0), initialize_sixteen_byte_state_records_7e782());
  return_only_stub_7be36();
  return_only_stub_7ee7e();
  ((void)(0), initialize_com_state_with_mode_20_7d89e());
  initialize_enabled_network_policy_values_7a0fe();
  ((void)(0), initialize_packet_queue_and_channel_gates_82c9e());
  ((void)(0), return_only_stub_81590());
  return_only_stub_7be34();
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x7a0c))))) = 0xf;
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x7a0e)))) = 0xfe01;
  return;
}

void run_ready_gated_paired_service_calls_7a232(void)

{
  if (((int16_t)DAT_febe3df2) == -0x1ff) {
    return_only_stub_7be4e();
    dispatch_two_active_channel_callback_passes_79eba();
    service_can_transmit_timers_and_queues_wrapper_79eca();
    return_only_stub_7be50();
  }
  return;
}

void service_ready_communication_policy_and_pdu_chains_7a254(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  if (((int16_t)DAT_febe3df2) == -0x1ff) {
    return_only_stub_7be3c();
    publish_changed_network_enable_mask_to_eight_channels_7bbc2();
    advance_aggregate_normal_channel_setup_state_7c43c();
    service_receive_and_mark_eligible_network_states_79ede();
    reconcile_all_network_enable_and_policy_masks_7bf60();
    ((void)(1), copy_two_network_group_request_vectors_7d01a(((uint32_t)((uint32_t)(puVar1 + -0x7a16)))));
    copy_second_group_vector_to_timer_transition_requests_7d6c2(((uint32_t)((uint32_t)(puVar1 + -0x7a12))));
    copy_second_group_vector_to_active_timer_masks_7d69e(((uint32_t)((uint32_t)(puVar1 + -0x7a14))));
    return_only_stub_7be52();
    tick_com_group_pdu_timers_and_report_expirations_7d52c();
    return_only_stub_7be38();
    return_only_stub_7be3a();
    return_only_stub_7be40();
    thunk_clear_record_4936_flags_wrapper_7ef9c();
    call_21bd8_when_global_state_1fe_7eb32();
    run_init_chain_79f16();
    service_com_tx_publication();
    run_guarded_halfword_sequence_then_callback_table_6a410();
    service_active_packet_queue_82e32();
    thunk_cantp_foreground_cycle_wrapper_79d7a();
    return_only_stub_7be3e();
  }
  return;
}

undefined4 call_interrupt_guard_and_return_zero_7a2da(void)

{
  thunk_push_priority_mask_and_raise_to_ff00_6a45e();
  return 0;
}

undefined4 call_interrupt_guard_and_return_zero_duplicate_7a2f4(void)

{
  thunk_push_priority_mask_and_raise_to_ff00_6a45e();
  return 0;
}

void initialize_cantp_flags_and_configuration_state_7a30e(void)

{
  uint32_t puVar1;
  puVar1 = 0x23dfcu;
  mark_cantp_uninitialized_with_clear_fault_status_7b3a6();
  reset_cantp_channels_and_seed_flow_parameters_7b2c4(((undefined *)camry_host_ptr((uint32_t)(puVar1 + -0x118c))));
  return;
}

void thunk_mark_cantp_uninitialized_with_clear_fault_status_7b3a6(void)

{
  mark_cantp_uninitialized_with_clear_fault_status_7b3a6();
  return;
}

F33CanTpConfiguration * get_cantp_configuration_pointer_7a32e(void)

{
  return ((undefined *)camry_host_ptr(0x22c70u));
}

uint request_cantp_transmit_if_initialized_and_in_range_7a334(ushort param_1,uint param_2)

{
  F33CanTpConfiguration *configuration;
  uint uVar1;
  
  uVar1 = 1;
  if ((((((int8_t)DAT_febe4f3d) == -0x56) &&
       (configuration = (F33CanTpConfiguration *)get_cantp_configuration_pointer_7a32e(),camry_host_addr((configuration))!= 0)) &&
      ((uint)configuration->first_transmit_id <= (uint)param_1)) &&
     ((int)((uint)param_1 -
           ((uint)configuration->transmit_count + (uint)configuration->first_transmit_id)) < 0)) {
    uVar1 = cantp_accept_transmit_length(configuration,param_1,param_2);
  }
  return uVar1;
}

uint cantp_transmit_descriptor(ushort transmit_id,F33PduInfo *response)

{
  uint uVar1;
  
  uVar1 = request_cantp_transmit_if_initialized_and_in_range_7a334(transmit_id,response->length);
  return uVar1;
}

uint cancel_cantp_transmit_if_initialized_and_in_range_7a38c(ushort param_1)

{
  F33CanTpConfiguration *configuration;
  uint uVar1;
  
  uVar1 = 1;
  if ((((((int8_t)DAT_febe4f3d) == -0x56) &&
       (configuration = (F33CanTpConfiguration *)get_cantp_configuration_pointer_7a32e(),camry_host_addr(configuration)!=camry_host_addr((F33CanTpConfiguration *)0x0))) &&
      ((uint)configuration->first_transmit_id <= (uint)param_1)) &&
     ((int)((uint)param_1 -
           ((uint)configuration->transmit_count + (uint)configuration->first_transmit_id)) < 0)) {
    uVar1 = cantp_cancel_transmit_owner(configuration,param_1);
  }
  return uVar1;
}

uint cancel_cantp_receive_if_initialized_and_in_range_7a3ca(ushort param_1)

{
  F33CanTpConfiguration *configuration;
  uint uVar1;
  
  uVar1 = 1;
  if ((((((int8_t)DAT_febe4f3d) == -0x56) &&
       (configuration = (F33CanTpConfiguration *)get_cantp_configuration_pointer_7a32e(),camry_host_addr((configuration))!= 0)) &&
      ((uint)configuration->first_receive_id <= (uint)param_1)) &&
     ((int)((uint)param_1 -
           ((uint)configuration->receive_count + (uint)configuration->first_receive_id)) < 0)) {
    uVar1 = cantp_cancel_receive_owner(configuration,param_1);
  }
  return uVar1;
}

void cantp_foreground_cycle(void)

{
  cantp_tick_channel_timeouts();
  cantp_run_receive_channels();
  cantp_run_transmit_channels();
  return;
}

F33CanTpRxConnection *
cantp_find_receive_frame_connection
          (F33CanTpConfiguration *configuration,ushort canif_receive_id,uchar *frame_bytes)

{
  F33CanTpRxConnection *pFVar1;
  uchar uVar2;
  ushort uVar3;
  F33CanTpRxConnection *pFVar4;
  uint uVar5;
  
  pFVar4 = (F33CanTpRxConnection *)0x0;
  uVar3 = 0;
  do {
    if ((configuration->channel_count <= uVar3) || (camry_host_addr((pFVar4))!= 0)) {
      return pFVar4;
    }
    uVar5 = 0;
    while ((uVar5 < (*((volatile uint8_t *)camry_host_ptr((uint32_t)((uint32_t)((uint32_t)(configuration->channel_rows) + (uint32_t)((short)uVar3) * (uint32_t)sizeof(F33CanTpChannelConfiguration)) + (uint32_t)(0) * (uint32_t)sizeof(F33CanTpChannelConfiguration) + (uint32_t)offsetof(F33CanTpChannelConfiguration, receive_count))))) &&
           (camry_host_addr((pFVar4))== 0))) {
      pFVar1 = ((F33CanTpRxConnection *)camry_host_ptr((uint32_t)((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)((uint32_t)((uint32_t)(configuration->channel_rows) + (uint32_t)((short)uVar3) * (uint32_t)sizeof(F33CanTpChannelConfiguration)) + (uint32_t)(0) * (uint32_t)sizeof(F33CanTpChannelConfiguration) + (uint32_t)offsetof(F33CanTpChannelConfiguration, receive_rows)))))) + (uint32_t)(uVar5) * (uint32_t)sizeof(F33CanTpRxConnection))));
      if (canif_receive_id == pFVar1->canif_receive_id) {
        if (1 < pFVar1->addressing_format) {
          if (pFVar1->addressing_format == 4) {
            uVar2 = pFVar1->receive_address_byte;
          }
          else {
            uVar2 = pFVar1->extended_flow_address_byte;
          }
          if (*frame_bytes != uVar2) goto LAB_0007a466;
        }
        pFVar4 = pFVar1;
      }
LAB_0007a466:
      uVar5 = uVar5 + 1 & 0xff;
    }
    uVar3 = uVar3 + 1 & 0xff;
  } while( true );
}

F33CanTpTxConnection *
cantp_find_flow_control_connection
          (F33CanTpConfiguration *configuration,ushort canif_receive_id,uchar *frame_bytes)

{
  F33CanTpTxConnection *pFVar1;
  uchar uVar2;
  ushort uVar3;
  F33CanTpTxConnection *pFVar4;
  uint uVar5;
  
  pFVar4 = (F33CanTpTxConnection *)0x0;
  uVar3 = 0;
  do {
    if ((configuration->channel_count <= uVar3) || (camry_host_addr((pFVar4))!= 0)) {
      return pFVar4;
    }
    uVar5 = 0;
    while ((uVar5 < (*((volatile uint8_t *)camry_host_ptr((uint32_t)((uint32_t)((uint32_t)(configuration->channel_rows) + (uint32_t)((short)uVar3) * (uint32_t)sizeof(F33CanTpChannelConfiguration)) + (uint32_t)(0) * (uint32_t)sizeof(F33CanTpChannelConfiguration) + (uint32_t)offsetof(F33CanTpChannelConfiguration, transmit_count))))) &&
           (camry_host_addr((pFVar4))== 0))) {
      pFVar1 = ((F33CanTpTxConnection *)camry_host_ptr((uint32_t)((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)((uint32_t)((uint32_t)(configuration->channel_rows) + (uint32_t)((short)uVar3) * (uint32_t)sizeof(F33CanTpChannelConfiguration)) + (uint32_t)(0) * (uint32_t)sizeof(F33CanTpChannelConfiguration) + (uint32_t)offsetof(F33CanTpChannelConfiguration, transmit_rows)))))) + (uint32_t)(uVar5) * (uint32_t)sizeof(F33CanTpTxConnection))));
      if (canif_receive_id == pFVar1->flow_control_receive_id) {
        if (1 < pFVar1->addressing_format) {
          if (pFVar1->addressing_format == 4) {
            uVar2 = pFVar1->flow_control_address_byte;
          }
          else {
            uVar2 = pFVar1->extended_transmit_address_byte;
          }
          if (*frame_bytes != uVar2) goto LAB_0007a4ca;
        }
        pFVar4 = pFVar1;
      }
LAB_0007a4ca:
      uVar5 = uVar5 + 1 & 0xff;
    }
    uVar3 = uVar3 + 1 & 0xff;
  } while( true );
}

void dispatch_cantp_received_frame_by_pci_nibble_7a4e4(F33CanTpConfiguration *param_1,F33CanTpFrameInfo *param_2,ushort param_3)

{
  byte bVar1;
  uint32_t puVar2;
  F33CanTpConfiguration *configuration;
  F33CanTpRxConnection *connection;
  F33CanTpTxConnection *connection_00;
  
  puVar2 = 0x23dfcu;
  if (param_2->length < 2) {
    return;
  }
  connection = cantp_find_receive_frame_connection(param_1, param_3, ((uchar *)camry_host_ptr((uint32_t)(param_2->data))));
  if (camry_host_addr(connection)!=camry_host_addr((F33CanTpRxConnection *)0x0)) {
    bVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)((uint32_t)(param_2->data) + (uint32_t)((byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(connection->addressing_format - 0x1264)))))) * 1u)))) & 0xf0;
    if (((*((volatile uint8_t *)camry_host_ptr((uint32_t)((uint32_t)(param_2->data) + (uint32_t)((byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(connection->addressing_format - 0x1264)))))) * 1u)))) & 0xf0) == 0) {
      admit_and_deliver_cantp_single_frame_7adf8(param_1, connection, param_2);
      return;
    }
    if (bVar1 == 0x10) {
      admit_and_begin_cantp_first_frame_7af76(param_1, connection, param_2);
      return;
    }
    if (bVar1 == 0x20) {
      cantp_handle_consecutive_receive(connection,param_2);
      return;
    }
  }
  connection_00 = cantp_find_flow_control_connection(param_1, param_3, ((uchar *)camry_host_ptr((uint32_t)(param_2->data))));
  if ((camry_host_addr(connection_00)!=camry_host_addr((F33CanTpTxConnection *)0x0)) &&
     (((*((volatile uint8_t *)camry_host_ptr((uint32_t)((uint32_t)(param_2->data) + (uint32_t)((byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(connection_00->addressing_format - 0x1264)))))) * 1u)))) & 0xf0) == 0x30)) {
    cantp_handle_flow_control(connection_00,param_2);
  }
  return;
}

void cantp_receive_can_frame(ushort canif_receive_id,F33PduInfo *pdu)

{
  uint8_t stack_record_14[20];
  camry_fill_bytes(stack_record_14, sizeof stack_record_14);
  uint uVar1;
  undefined4 *extraout_r7;
  int iVar2;
  
  uVar1 = (uint)canif_receive_id;
  if ((((((int8_t)DAT_febe4f3d) == -0x56) && (iVar2 = camry_host_addr(get_cantp_configuration_pointer_7a32e()), iVar2 != 0)) &&
      ((*((ushort *)camry_host_ptr((uint32_t)(iVar2 + 8)))) <= uVar1)) &&
     ((int)(uVar1 - ((uint)(*((byte *)camry_host_ptr((uint32_t)(iVar2 + 0xf)))) + (uint)(*((ushort *)camry_host_ptr((uint32_t)(iVar2 + 8)))))) < 0)) {
    (*((uint32_t *)(stack_record_14 + 0))) = *((undefined4 *)(pdu));
    (*((uint32_t *)(stack_record_14 + 4))) = (uint)*(ushort *)(((undefined4 *)(pdu)) + 1);
    dispatch_cantp_received_frame_by_pci_nibble_7a4e4(((F33CanTpConfiguration *)camry_host_ptr((uint32_t)(iVar2))), ((uint32_t *)(stack_record_14)), uVar1);
  }
  return;
}

F33CanTpTxConnection *
cantp_find_active_transmit_confirmation
          (F33CanTpConfiguration *configuration,ushort canif_confirmation_id)

{
  F33CanTpTxConnection *pFVar1;
  F33CanTpTxConnection *pFVar2;
  uint uVar3;
  uint uVar4;
  
  uVar4 = 0;
  pFVar2 = (F33CanTpTxConnection *)0x0;
  while ((uVar4 < configuration->channel_count && (camry_host_addr((pFVar2))== 0))) {
    pFVar1 = pFVar2;
    if ((*((volatile uint16_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe4f40u + (uint32_t)(uVar4 * 2) * (uint32_t)sizeof(F33CanTpTxStatePrefix)) + (uint32_t)(0) * (uint32_t)sizeof(F33CanTpTxStatePrefix) + (uint32_t)offsetof(F33CanTpTxStatePrefix, transmit_id))))) != 0xffff) {
      for (uVar3 = 0;
          (pFVar1 = pFVar2, uVar3 < (*((volatile uint8_t *)camry_host_ptr((uint32_t)((uint32_t)((uint32_t)(configuration->channel_rows) + (uint32_t)((short)uVar4) * (uint32_t)sizeof(F33CanTpChannelConfiguration)) + (uint32_t)(0) * (uint32_t)sizeof(F33CanTpChannelConfiguration) + (uint32_t)offsetof(F33CanTpChannelConfiguration, transmit_count))))) &&
          ((pFVar1 = ((F33CanTpTxConnection *)camry_host_ptr((uint32_t)((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)((uint32_t)((uint32_t)(configuration->channel_rows) + (uint32_t)((short)uVar4) * (uint32_t)sizeof(F33CanTpChannelConfiguration)) + (uint32_t)(0) * (uint32_t)sizeof(F33CanTpChannelConfiguration) + (uint32_t)offsetof(F33CanTpChannelConfiguration, transmit_rows)))))) + (uint32_t)(uVar3) * (uint32_t)sizeof(F33CanTpTxConnection)))),
           canif_confirmation_id != pFVar1->canif_confirmation_id ||
           ((*((volatile uint16_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe4f40u + (uint32_t)(uVar4 * 2) * (uint32_t)sizeof(F33CanTpTxStatePrefix)) + (uint32_t)(0) * (uint32_t)sizeof(F33CanTpTxStatePrefix) + (uint32_t)offsetof(F33CanTpTxStatePrefix, transmit_id))))) != pFVar1->transmit_id))));
          uVar3 = uVar3 + 1 & 0xff) {
      }
    }
    uVar4 = uVar4 + 1 & 0xff;
    pFVar2 = pFVar1;
  }
  return pFVar2;
}

F33CanTpRxConnection *
cantp_find_active_receive_confirmation
          (F33CanTpConfiguration *configuration,ushort canif_confirmation_id)

{
  F33CanTpRxConnection *pFVar1;
  F33CanTpRxConnection *pFVar2;
  uint uVar3;
  uint uVar4;
  
  uVar4 = 0;
  pFVar2 = (F33CanTpRxConnection *)0x0;
  while ((uVar4 < configuration->channel_count && (camry_host_addr((pFVar2))== 0))) {
    pFVar1 = pFVar2;
    if ((*((volatile uint16_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe4f50u + (uint32_t)(uVar4 * 2) * (uint32_t)sizeof(F33CanTpRxState)) + (uint32_t)(0) * (uint32_t)sizeof(F33CanTpRxState) + (uint32_t)offsetof(F33CanTpRxState, receive_id))))) != 0xffff) {
      for (uVar3 = 0;
          (pFVar1 = pFVar2, uVar3 < (*((volatile uint8_t *)camry_host_ptr((uint32_t)((uint32_t)((uint32_t)(configuration->channel_rows) + (uint32_t)((short)uVar4) * (uint32_t)sizeof(F33CanTpChannelConfiguration)) + (uint32_t)(0) * (uint32_t)sizeof(F33CanTpChannelConfiguration) + (uint32_t)offsetof(F33CanTpChannelConfiguration, receive_count))))) &&
          ((pFVar1 = ((F33CanTpRxConnection *)camry_host_ptr((uint32_t)((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)((uint32_t)((uint32_t)(configuration->channel_rows) + (uint32_t)((short)uVar4) * (uint32_t)sizeof(F33CanTpChannelConfiguration)) + (uint32_t)(0) * (uint32_t)sizeof(F33CanTpChannelConfiguration) + (uint32_t)offsetof(F33CanTpChannelConfiguration, receive_rows)))))) + (uint32_t)(uVar3) * (uint32_t)sizeof(F33CanTpRxConnection)))),
           canif_confirmation_id != pFVar1->canif_fc_confirmation_id ||
           ((*((volatile uint16_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe4f50u + (uint32_t)(uVar4 * 2) * (uint32_t)sizeof(F33CanTpRxState)) + (uint32_t)(0) * (uint32_t)sizeof(F33CanTpRxState) + (uint32_t)offsetof(F33CanTpRxState, receive_id))))) != pFVar1->receive_id))));
          uVar3 = uVar3 + 1 & 0xff) {
      }
    }
    uVar4 = uVar4 + 1 & 0xff;
    pFVar2 = pFVar1;
  }
  return pFVar2;
}

void cantp_confirm_can_frame(ushort canif_confirmation_id)

{
  F33CanTpConfiguration *configuration;
  F33CanTpConfiguration *configuration_00;
  F33CanTpTxConnection *connection;
  F33CanTpRxConnection *connection_00;
  
  if ((((((int8_t)DAT_febe4f3d) == -0x56) &&
       (configuration_00 = (F33CanTpConfiguration *)get_cantp_configuration_pointer_7a32e(),camry_host_addr((configuration_00))!= 0)) &&
      ((uint)configuration_00->first_canif_confirmation_id <= (uint)canif_confirmation_id)) &&
     ((int)((uint)canif_confirmation_id -
           ((uint)configuration_00->canif_confirmation_count +
           (uint)configuration_00->first_canif_confirmation_id)) < 0)) {
    connection = cantp_find_active_transmit_confirmation(configuration_00,canif_confirmation_id)
    ;
    if (camry_host_addr((connection))== 0) {
      connection_00 =
           cantp_find_active_receive_confirmation(configuration,canif_confirmation_id);
      if (camry_host_addr((connection_00))!= 0) {
        cantp_confirm_receive_flow_control(connection_00);
      }
    }
    else {
      cantp_handle_frame_confirmation(connection);
    }
  }
  return;
}

F33CanTpRxConnection *
cantp_find_receive_connection(F33CanTpConfiguration *configuration,ushort receive_id)

{
  uint uVar1;
  uint uVar2;
  F33CanTpRxConnection *pFVar3;
  F33CanTpRxConnection *pFVar4;
  ushort uVar5;
  
  uVar2 = (uint)receive_id;
  pFVar3 = (F33CanTpRxConnection *)0x0;
  if ((configuration->first_receive_id <= uVar2) &&
     ((int)(uVar2 - ((uint)configuration->receive_count + (uint)configuration->first_receive_id)) <
      0)) {
    uVar5 = 0;
    while ((uVar5 < configuration->channel_count && (camry_host_addr((pFVar3))== 0))) {
      uVar1 = 0;
      while ((pFVar4 = pFVar3, uVar1 < (*((volatile uint8_t *)camry_host_ptr((uint32_t)((uint32_t)((uint32_t)(configuration->channel_rows) + (uint32_t)((short)uVar5) * (uint32_t)sizeof(F33CanTpChannelConfiguration)) + (uint32_t)(0) * (uint32_t)sizeof(F33CanTpChannelConfiguration) + (uint32_t)offsetof(F33CanTpChannelConfiguration, receive_count))))) &&
             (pFVar4 = ((F33CanTpRxConnection *)camry_host_ptr((uint32_t)((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)((uint32_t)((uint32_t)(configuration->channel_rows) + (uint32_t)((short)uVar5) * (uint32_t)sizeof(F33CanTpChannelConfiguration)) + (uint32_t)(0) * (uint32_t)sizeof(F33CanTpChannelConfiguration) + (uint32_t)offsetof(F33CanTpChannelConfiguration, receive_rows)))))) + (uint32_t)(uVar1) * (uint32_t)sizeof(F33CanTpRxConnection)))),
             uVar2 != pFVar4->receive_id))) {
        uVar1 = uVar1 + 1 & 0xff;
      }
      uVar5 = uVar5 + 1 & 0xff;
      pFVar3 = pFVar4;
    }
  }
  return pFVar3;
}

F33CanTpTxConnection *
cantp_find_transmit_connection(F33CanTpConfiguration *configuration,ushort transmit_id)

{
  uint uVar1;
  uint uVar2;
  F33CanTpTxConnection *pFVar3;
  F33CanTpTxConnection *pFVar4;
  ushort uVar5;
  
  uVar2 = (uint)transmit_id;
  pFVar3 = (F33CanTpTxConnection *)0x0;
  if ((configuration->first_transmit_id <= uVar2) &&
     ((int)(uVar2 - ((uint)configuration->transmit_count + (uint)configuration->first_transmit_id))
      < 0)) {
    uVar5 = 0;
    while ((uVar5 < configuration->channel_count && (camry_host_addr((pFVar3))== 0))) {
      uVar1 = 0;
      while ((pFVar4 = pFVar3, uVar1 < (*((volatile uint8_t *)camry_host_ptr((uint32_t)((uint32_t)((uint32_t)(configuration->channel_rows) + (uint32_t)((short)uVar5) * (uint32_t)sizeof(F33CanTpChannelConfiguration)) + (uint32_t)(0) * (uint32_t)sizeof(F33CanTpChannelConfiguration) + (uint32_t)offsetof(F33CanTpChannelConfiguration, transmit_count))))) &&
             (pFVar4 = ((F33CanTpTxConnection *)camry_host_ptr((uint32_t)((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)((uint32_t)((uint32_t)(configuration->channel_rows) + (uint32_t)((short)uVar5) * (uint32_t)sizeof(F33CanTpChannelConfiguration)) + (uint32_t)(0) * (uint32_t)sizeof(F33CanTpChannelConfiguration) + (uint32_t)offsetof(F33CanTpChannelConfiguration, transmit_rows)))))) + (uint32_t)(uVar1) * (uint32_t)sizeof(F33CanTpTxConnection)))),
             uVar2 != pFVar4->transmit_id))) {
        uVar1 = uVar1 + 1 & 0xff;
      }
      uVar5 = uVar5 + 1 & 0xff;
      pFVar3 = pFVar4;
    }
  }
  return pFVar3;
}

void cantp_reset_receive_owner(F33CanTpRxState *state)

{
  state->receive_id = 0xffff;
  state->remaining_length = 0;
  state->state = 0xe1;
  state->expected_sequence_number = 0xff;
  state->timeout_ticks = 0;
  state->wait_frame_count = 0;
  state->first_frame_dlc = '\0';
  state->block_remaining = '\0';
  state->flow_status_marker = 0xf0;
  return;
}

void forward_cantp_receive_result_to_router_7a79e(undefined2 param_1,undefined1 param_2)

{
  call_21cf4_with_masked_u16_and_byte_81a00(param_1,param_2);
  return;
}

void cantp_finish_receive_aggregate
               (F33CanTpRxConnection *connection,F33CanTpRxState *state,uchar result)

{
  undefined4 extraout_r8;
  
  cantp_reset_receive_owner(state);
  forward_cantp_receive_result_to_router_7a79e(connection->upper_receive_id,((undefined4)((uint)(byte)result)));
  return;
}

uint cantp_cancel_receive_owner(F33CanTpConfiguration *configuration,ushort receive_id)

{
  int iVar1;
  char cVar2;
  uint32_t puVar3;
  uint32_t puVar4;
  F33CanTpRxConnection *connection;
  uint uVar5;
  F33CanTpRxState *state;
  
  puVar3 = 0xfebeb800u;
  puVar4 = 0x23dfcu;
  uVar5 = 1;
  connection = cantp_find_receive_connection(configuration,receive_id);
  iVar1 = (uint)connection->channel_state_index * 0x20;
  state = ((F33CanTpRxState *)camry_host_ptr((uint32_t)(puVar3 + iVar1 + -0x68b0)));
  if (receive_id == (*((ushort *)camry_host_ptr((uint32_t)(puVar3 + iVar1 + -0x68ac))))) {
    cVar2 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(iVar1 + -0x68a6)))));
    if (cVar2 == 'K') {
      if (state->remaining_length <=
          (8 - ((byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(connection->addressing_format - 0x1264))))) + 1) & 0xff)) {
        return 1;
      }
    }
    else if (cVar2 == 'Z') {
      ((void)(connection->canif_fc_transmit_id), return_only_stub_7b246());
    }
    else if (cVar2 != 'i') {
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x68c4))))) = 0xf;
      cantp_reset_receive_owner(state);
      return 1;
    }
    cantp_finish_receive_aggregate(connection,state,'\x01');
    uVar5 = 0;
  }
  return uVar5;
}

void store_cantp_first_flow_byte_with_complement_7a84c(byte *param_1,ushort param_2)

{
  cantp_rx_flow_parameters_with_complements[*param_1][0] = param_2 | (param_2 ^ 0xff) << 8;
  return;
}

uint read_or_repair_cantp_first_flow_byte_7a862(byte *param_1)

{
  uint uVar1;
  
  uVar1 = (uint)cantp_rx_flow_parameters_with_complements[*param_1][0];
  if ((uVar1 & 0xff ^ (int)uVar1 >> 8) != 0xff) {
    uVar1 = (uint)param_1[0x16];
    DAT_febe4f3c = 0xf;
    store_cantp_first_flow_byte_with_complement_7a84c(param_1,uVar1);
  }
  return uVar1 & 0xff;
}

void store_cantp_second_flow_byte_with_complement_7a89a(byte *param_1,ushort param_2)

{
  cantp_rx_flow_parameters_with_complements[*param_1][1] = param_2 | (param_2 ^ 0xff) << 8;
  return;
}

uint read_or_repair_cantp_second_flow_byte_7a8b0(byte *param_1)

{
  uint uVar1;
  
  uVar1 = (uint)cantp_rx_flow_parameters_with_complements[*param_1][1];
  if ((uVar1 & 0xff ^ (int)uVar1 >> 8) != 0xff) {
    uVar1 = (uint)param_1[0x17];
    DAT_febe4f3c = 0xf;
    store_cantp_second_flow_byte_with_complement_7a89a(param_1,uVar1);
  }
  return uVar1 & 0xff;
}

uint cantp_copy_upper_receive_bytes(ushort upper_id,F33CanTpFrameInfo *chunk,uint *available)

{
  uint8_t stack_record_12[18];
  uint uVar1;
  (*((uint32_t *)(stack_record_12 + 2))) = chunk->data;
  (*((uint16_t *)(stack_record_12 + 6))) = (undefined2)chunk->length;
  (*((uint16_t *)(stack_record_12 + 0))) = (ushort)*available;
  uVar1 = ((void)(((uint32_t *)(stack_record_12 + 2))), (void)(stack_record_12), call_21cec_with_masked_u16_81a34(upper_id, camry_host_addr(((uint32_t *)(stack_record_12 + 2))), camry_host_addr(((uint8_t *)stack_record_12 + 0))));
  *available = (uint)(*((uint16_t *)(stack_record_12 + 0)));
  return uVar1;
}

uint cantp_multiply_receive_block_capacity(uchar cf_payload_capacity,uchar block_size)

{
  uint uVar1;
  uint uVar2;
  
  uVar2 = 0;
  uVar1 = 0;
  do {
    if ((1 << (uVar1 & 0x1f) & 0xffU & (uint)block_size) != 0) {
      uVar2 = uVar2 + ((uint)cf_payload_capacity << (uVar1 & 0x1f)) & 0xffff;
    }
    uVar1 = uVar1 + 1;
  } while (uVar1 < 8);
  return uVar2;
}

uint cantp_select_receive_flow_status
               (uint remaining,uint available,uchar cf_payload_capacity,uchar block_size)

{
  uint uVar1;
  uint uVar2;
  
  uVar2 = 0xe1;
  uVar1 = remaining;
  if ((block_size != '\0') &&
     (uVar1 = cantp_multiply_receive_block_capacity(cf_payload_capacity,block_size),
     remaining <= uVar1)) {
    uVar1 = remaining;
  }
  if (uVar1 <= available) {
    uVar2 = 0xf0;
  }
  return uVar2;
}

uint cantp_queue_receive_flow_control
               (F33CanTpRxConnection *connection,uchar flow_status,uchar block_size,uchar stmin)

{
  uint uVar1;
  F33CanTpFrameInfo local_c;
  
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe4efcu + (uint32_t)(3) * 1u)))) = DAT_00022c46;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe4efcu + (uint32_t)(4) * 1u)))) = DAT_00022c46;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe4efcu + (uint32_t)(5) * 1u)))) = DAT_00022c46;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe4efcu + (uint32_t)(6) * 1u)))) = DAT_00022c46;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe4efcu + (uint32_t)(7) * 1u)))) = DAT_00022c46;
  uVar1 = (uint)connection->addressing_format;
  if (uVar1 == 4) {
    ((volatile uint8_t *)camry_host_ptr(0xfebe4efcu))[0] = connection->flow_control_address_byte;
  }
  else if (uVar1 == 2 || uVar1 == 3) {
    ((volatile uint8_t *)camry_host_ptr(0xfebe4efcu))[0] = connection->extended_flow_address_byte;
  }
  uVar1 = (uint)(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x22b98u + (uint32_t)(uVar1) * 1u))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe4efcu + (uint32_t)(uVar1) * 1u)))) = flow_status | 0x30;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe4efcu + (uint32_t)(uVar1 + 1) * 1u)))) = block_size;
  local_c.length = 8;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe4efcu + (uint32_t)(uVar1 + 2) * 1u)))) = stmin;
  if (connection->pad_flow_control_to_eight == '\0') {
    local_c.length = uVar1 + 3 & 0xff;
  }
  local_c.data = camry_host_addr(cantp_shared_frame_scratch);
  uVar1 = cantp_submit_can_frame(connection->canif_fc_transmit_id,&local_c);
  return uVar1;
}

void cantp_poll_receive_capacity_and_flow
               (F33CanTpRxConnection *connection,F33CanTpRxState *state)

{
  ushort uVar1;
  uint32_t puVar2;
  uint32_t puVar3;
  int extraout_r6;
  uchar block_size;
  uchar stmin;
  ushort uVar4;
  uint uVar5;
  uint local_28;
  F33CanTpFrameInfo FStack_24;
  
  puVar2 = 0xfebeb800u;
  puVar3 = 0x23dfcu;
  uVar4 = state->wait_frame_count;
  uVar5 = (uint)state->flow_status_marker;
  block_size = read_or_repair_cantp_first_flow_byte_7a862(connection);
  stmin = read_or_repair_cantp_second_flow_byte_7a8b0(connection);
  if (uVar5 == 0xe1) {
    FStack_24.length = 0;
    FStack_24.data = 0;
    local_28 = 0;
    uVar5 = cantp_copy_upper_receive_bytes(connection->upper_receive_id,&FStack_24,&local_28);
    if (uVar5 != 0) goto LAB_0007aa86;
    uVar5 = cantp_select_receive_flow_status
                      (state->remaining_length,local_28,
                       '\a' - (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(connection->addressing_format - 0x1264))))),block_size);
    if (uVar5 == 0xf0) goto LAB_0007aa5c;
    if (state->timeout_ticks != 0) {
      return;
    }
    if (connection->wait_frame_limit <= uVar4) goto LAB_0007aa86;
    uVar4 = uVar4 + 1;
  }
  else {
    if (uVar5 != 0xd2) {
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x68c4))))) = 0xf;
      cantp_reset_receive_owner(state);
      return;
    }
LAB_0007aa5c:
    uVar4 = 0;
  }
  state->state = 'Z';
  uVar1 = connection->frame_confirmation_timeout_raw;
  state->flow_status_marker = (byte)uVar5;
  state->wait_frame_count = uVar4;
  state->block_remaining = block_size;
  state->timeout_ticks = uVar1 + 2;
  uVar5 = cantp_queue_receive_flow_control(connection,(byte)uVar5 & 0xf,block_size,stmin);
  if (uVar5 == 0) {
    return;
  }
LAB_0007aa86:
  cantp_finish_receive_aggregate(connection,state,'\x01');
  return;
}

void abort_cantp_receive_in_state_5a_7aaa2(int param_1,F33CanTpRxState *param_2)

{
  if (param_2->state == 'Z') {
    cantp_reset_receive_owner(param_2);
    ((void)((*((undefined2 *)camry_host_ptr((uint32_t)(param_1 + 10))))), return_only_stub_7b246());
    forward_cantp_receive_result_to_router_7a79e((*((undefined2 *)camry_host_ptr((uint32_t)(param_1 + 8)))),1);
  }
  return;
}

void abort_cantp_receive_in_state_4b_7aace(int param_1,F33CanTpRxState *param_2)

{
  if (param_2->state == 'K') {
    cantp_reset_receive_owner(param_2);
    forward_cantp_receive_result_to_router_7a79e((*((undefined2 *)camry_host_ptr((uint32_t)(param_1 + 8)))),1);
  }
  return;
}

void cantp_run_receive_channels(void)

{
  int iVar1;
  char cVar2;
  char cVar3;
  short sVar4;
  byte bVar5;
  undefined8 uVar6;
  F33CanTpConfiguration *configuration;
  F33CanTpRxConnection *unaff_r25;
  F33CanTpRxState *state;
  uint uVar7;
  
  uVar6 = 0xfebeb800;
  if ((((int8_t)DAT_febe4f3d) == -0x56) &&
     (configuration = (F33CanTpConfiguration *)get_cantp_configuration_pointer_7a32e(),camry_host_addr((configuration))!= 0)) {
    bVar5 = configuration->channel_count;
    for (uVar7 = 0; uVar7 < bVar5; uVar7 = uVar7 + 1 & 0xff) {
      iVar1 = uVar7 * 0x20 + (int)uVar6 + -0x68c0;
      state = ((F33CanTpRxState *)camry_host_ptr((uint32_t)(iVar1 + 0x10)));
      sVar4 = (*((short *)camry_host_ptr((uint32_t)(iVar1 + 0x16))));
      cVar2 = (*((char *)camry_host_ptr((uint32_t)(iVar1 + 0x1a))));
      cVar3 = (*((char *)camry_host_ptr((uint32_t)(iVar1 + 0x1f))));
      if (((cVar2 == 'K') || (cVar2 == 'Z')) || (cVar2 == 'i')) {
        unaff_r25 = cantp_find_receive_connection(configuration,(*((ushort *)camry_host_ptr((uint32_t)(iVar1 + 0x14)))));
        if (camry_host_addr((unaff_r25))!= 0) goto LAB_0007ab68;
LAB_0007ab52:
        (*((undefined1 *)camry_host_ptr((uint32_t)((int)uVar6 + -0x68c4)))) = 0xf;
        if ((*((char *)camry_host_ptr((uint32_t)(iVar1 + 0x1f)))) == cVar3) {
          cantp_reset_receive_owner(state);
        }
      }
      else {
        if (((int8_t)cVar2) != -0x1f) goto LAB_0007ab52;
LAB_0007ab68:
        if (((int8_t)cVar2) != -0x1f) {
          if (cVar2 == 'i') {
            cantp_poll_receive_capacity_and_flow(unaff_r25,state);
          }
          else if (sVar4 == 0) {
            if (cVar2 == 'Z') {
              abort_cantp_receive_in_state_5a_7aaa2(camry_host_addr(unaff_r25), state);
            }
            else {
              abort_cantp_receive_in_state_4b_7aace(camry_host_addr(unaff_r25), state);
            }
          }
        }
      }
    }
  }
  return;
}

uint cantp_reject_single_frame_extent(F33CanTpRxConnection *connection,F33CanTpFrameInfo *frame)

{
  uint uVar1;
  uint uVar2;
  uint uVar3;
  uint uVar4;
  uint uVar5;
  
  uVar3 = 1;
  uVar5 = frame->length;
  uVar4 = (uint)(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x22b98u + (uint32_t)(connection->addressing_format) * 1u))));
  if (((uVar5 < 9) && (uVar2 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)((uint32_t)(frame->data) + (uint32_t)(uVar4) * 1u)))) & 0xf, ((*((volatile uint8_t *)camry_host_ptr((uint32_t)((uint32_t)(frame->data) + (uint32_t)(uVar4) * 1u)))) & 0xf) != 0)) &&
     (uVar1 = 7 - uVar4,
     (int)(uVar2 - uVar1) < 0 != ((int)uVar1 < 0 && (int)uVar1 < 0 == (int)(uVar2 - uVar1) < 0) ||
     uVar2 == uVar1)) {
    if (connection->require_padded_receive == '\x01') {
      if (uVar5 != 8) {
        return uVar3;
      }
    }
    else if (uVar5 < (uVar2 + uVar4 + 1 & 0xff)) {
      return uVar3;
    }
    uVar3 = 0;
  }
  return uVar3;
}

undefined4 arbitrate_cantp_transmit_owner_for_receive_admission_7abe6(F33CanTpConfiguration *param_1,int param_2)

{
  uint uVar1;
  uint32_t puVar2;
  uchar uVar3;
  F33CanTpTxConnection *connection;
  F33CanTpTxStatePrefix *state;
  
  puVar2 = 0xfebeb800u;
  uVar1 = (uint)(*((byte *)camry_host_ptr((uint32_t)(param_2 + 1))));
  state = ((void *)camry_host_ptr((uint32_t)(0xfebe4f40u + (uint32_t)(uVar1 * 2) * (uint32_t)sizeof(F33CanTpTxStatePrefix))));
  connection = cantp_find_transmit_connection
                         (param_1,(*((volatile uint16_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe4f40u + (uint32_t)(uVar1 * 2) * (uint32_t)sizeof(F33CanTpTxStatePrefix)) + (uint32_t)(0) * (uint32_t)sizeof(F33CanTpTxStatePrefix) + (uint32_t)offsetof(F33CanTpTxStatePrefix, transmit_id))))));
  if (camry_host_addr(connection)==camry_host_addr((F33CanTpTxConnection *)0x0)) {
LAB_0007ac88:
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x68c4))))) = 0xf;
    (*((volatile uint16_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe4f40u + (uint32_t)(uVar1 * 2) * (uint32_t)sizeof(F33CanTpTxStatePrefix)) + (uint32_t)(0) * (uint32_t)sizeof(F33CanTpTxStatePrefix) + (uint32_t)offsetof(F33CanTpTxStatePrefix, transmit_id))))) = 0xffff;
    state->remaining_or_accepted_length = 0;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe4f40u + (uint32_t)(uVar1 * 2) * (uint32_t)sizeof(F33CanTpTxStatePrefix)) + (uint32_t)(0) * (uint32_t)sizeof(F33CanTpTxStatePrefix) + (uint32_t)offsetof(F33CanTpTxStatePrefix, state))))) = 0xe1;
    (*((volatile uint16_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe4f40u + (uint32_t)(uVar1 * 2) * (uint32_t)sizeof(F33CanTpTxStatePrefix)) + (uint32_t)(0) * (uint32_t)sizeof(F33CanTpTxStatePrefix) + (uint32_t)offsetof(F33CanTpTxStatePrefix, timeout_ticks))))) = 0;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe4f40u + (uint32_t)(uVar1 * 2) * (uint32_t)sizeof(F33CanTpTxStatePrefix)) + (uint32_t)(0) * (uint32_t)sizeof(F33CanTpTxStatePrefix) + (uint32_t)offsetof(F33CanTpTxStatePrefix, sequence_number))))) = 0xff;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe4f40u + (uint32_t)(uVar1 * 2) * (uint32_t)sizeof(F33CanTpTxStatePrefix)) + (uint32_t)(0) * (uint32_t)sizeof(F33CanTpTxStatePrefix) + (uint32_t)offsetof(F33CanTpTxStatePrefix, block_remaining))))) = '\0';
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe4f40u + (uint32_t)(uVar1 * 2) * (uint32_t)sizeof(F33CanTpTxStatePrefix)) + (uint32_t)(0) * (uint32_t)sizeof(F33CanTpTxStatePrefix) + (uint32_t)offsetof(F33CanTpTxStatePrefix, block_size))))) = '\0';
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe4f40u + (uint32_t)(uVar1 * 2) * (uint32_t)sizeof(F33CanTpTxStatePrefix)) + (uint32_t)(0) * (uint32_t)sizeof(F33CanTpTxStatePrefix) + (uint32_t)offsetof(F33CanTpTxStatePrefix, spacing_ticks))))) = '\0';
    return 0;
  }
  uVar3 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe4f40u + (uint32_t)(uVar1 * 2) * (uint32_t)sizeof(F33CanTpTxStatePrefix)) + (uint32_t)(0) * (uint32_t)sizeof(F33CanTpTxStatePrefix) + (uint32_t)offsetof(F33CanTpTxStatePrefix, state)))));
  if ((uVar3 == 0xc3) || ((uVar3 == 0x87 && (state->remaining_or_accepted_length == 0)))) {
    if (connection->overlap_final_confirmation_policy == '\0') goto LAB_0007ac40;
    if (connection->overlap_final_confirmation_policy == '\x01') {
      uVar3 = '\0';
      goto LAB_0007ac82;
    }
LAB_0007ac4c:
    ((void)(connection->canif_frame_id), return_only_stub_7b246());
  }
  else {
    if ((uVar3 == 0xb4) || (uVar3 == 0x87)) {
LAB_0007ac40:
      if (connection->preemption_rank <= (*((byte *)camry_host_ptr((uint32_t)(param_2 + 0x1d))))) {
        return 1;
      }
      goto LAB_0007ac4c;
    }
    if ((((uVar3 != 'x') && (uVar3 != 0x96)) && (uVar3 != 0xa5)) && (uVar3 != 0xd2))
    goto LAB_0007ac88;
    if (connection->preemption_rank <= (*((byte *)camry_host_ptr((uint32_t)(param_2 + 0x1d))))) {
      return 1;
    }
  }
  uVar3 = '\x01';
LAB_0007ac82:
  cantp_finish_transmit_aggregate(connection,state,uVar3);
  return 0;
}

undefined4 arbitrate_cantp_receive_owner_for_new_frame_7ac9c(F33CanTpConfiguration *param_1,int param_2)

{
  uchar uVar1;
  uchar uVar2;
  ushort receive_id;
  uint uVar3;
  uint32_t puVar4;
  F33CanTpRxConnection *connection;
  
  puVar4 = (0xfebeb800u);
  uVar3 = (uint)(*((byte *)camry_host_ptr((uint32_t)(param_2 + 1))));
  uVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe4f50u + (uint32_t)(uVar3 * 2) * (uint32_t)sizeof(F33CanTpRxState)) + (uint32_t)(0) * (uint32_t)sizeof(F33CanTpRxState) + (uint32_t)offsetof(F33CanTpRxState, state)))));
  uVar2 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe4f50u + (uint32_t)(uVar3 * 2) * (uint32_t)sizeof(F33CanTpRxState)) + (uint32_t)(0) * (uint32_t)sizeof(F33CanTpRxState) + (uint32_t)offsetof(F33CanTpRxState, flow_status_marker)))));
  if (uVar1 == 0xe1) {
    return 0;
  }
  if ((uVar1 == 'i') || (uVar1 == 'K')) {
    receive_id = (*((volatile uint16_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe4f50u + (uint32_t)(uVar3 * 2) * (uint32_t)sizeof(F33CanTpRxState)) + (uint32_t)(0) * (uint32_t)sizeof(F33CanTpRxState) + (uint32_t)offsetof(F33CanTpRxState, receive_id)))));
    puVar4 = (0xfebeb800u);
    connection = cantp_find_receive_connection(param_1,receive_id);
    if (camry_host_addr(connection)!=camry_host_addr((F33CanTpRxConnection *)0x0)) {
      if ((receive_id != (*((ushort *)camry_host_ptr((uint32_t)(param_2 + 2))))) &&
         (connection->preemption_rank <= (*((byte *)camry_host_ptr((uint32_t)(param_2 + 0x1d)))))) {
        return 1;
      }
LAB_0007ad36:
      cantp_finish_receive_aggregate(connection, ((F33CanTpRxState *)camry_host_ptr((uint32_t)(0xfebe4f50u + (uint32_t)(uVar3 * 2) * (uint32_t)sizeof(F33CanTpRxState)))), '\x01');
      return 0;
    }
  }
  else if ((uVar1 == 'Z') &&
          (puVar4 = (0xfebeb800u),
          connection = cantp_find_receive_connection
                                 (param_1,(*((volatile uint16_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe4f50u + (uint32_t)(uVar3 * 2) * (uint32_t)sizeof(F33CanTpRxState)) + (uint32_t)(0) * (uint32_t)sizeof(F33CanTpRxState) + (uint32_t)offsetof(F33CanTpRxState, receive_id)))))),camry_host_addr(connection)!=camry_host_addr((F33CanTpRxConnection *)0x0))) {
    if ((uVar2 == 0xf0) || (uVar2 == 0xe1)) {
      if (((*((volatile uint16_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe4f50u + (uint32_t)(uVar3 * 2) * (uint32_t)sizeof(F33CanTpRxState)) + (uint32_t)(0) * (uint32_t)sizeof(F33CanTpRxState) + (uint32_t)offsetof(F33CanTpRxState, receive_id))))) != (*((ushort *)camry_host_ptr((uint32_t)(param_2 + 2))))) &&
         (connection->preemption_rank <= (*((byte *)camry_host_ptr((uint32_t)(param_2 + 0x1d)))))) {
        return 1;
      }
      ((void)(connection->canif_fc_transmit_id), return_only_stub_7b246());
      goto LAB_0007ad36;
    }
    if (uVar2 == 0xd2) {
      ((void)(connection->canif_fc_transmit_id), return_only_stub_7b246());
      goto LAB_0007ad56;
    }
  }
  (*((volatile undefined *)camry_host_ptr((uint32_t)(0xfebeb800u + (uint32_t)(-0x68c4) * 1u)))) = 0xf;
LAB_0007ad56:
  cantp_reset_receive_owner(((F33CanTpRxState *)camry_host_ptr((uint32_t)(0xfebe4f50u + (uint32_t)(uVar3 * 2) * (uint32_t)sizeof(F33CanTpRxState)))));
  return 0;
}

uint cantp_start_upper_receive
               (ushort upper_id,F33CanTpFrameInfo *first_chunk,ushort total_length,uint *available)

{
  uint8_t stack_record_12[18];
  uint uVar1;
  (*((uint32_t *)(stack_record_12 + 2))) = first_chunk->data;
  (*((uint16_t *)(stack_record_12 + 0))) = 0;
  (*((uint16_t *)(stack_record_12 + 6))) = (undefined2)first_chunk->length;
  uVar1 = ((void)(stack_record_12), call_21ce8_with_masked_u16_and_two_values_81a1a(upper_id,  camry_host_addr(((uint32_t *)(stack_record_12 + 2))),  total_length, camry_host_addr(((uint8_t *)stack_record_12 + 0))));
  *available = (uint)(*((uint16_t *)(stack_record_12 + 0)));
  return uVar1;
}

void cantp_deliver_single_frame(F33CanTpRxConnection *connection,F33CanTpFrameInfo *frame)

{
  ushort upper_id;
  uint uVar1;
  undefined4 uVar2;
  uint uVar3;
  uint local_1c;
  F33CanTpFrameInfo FStack_18;
  
  upper_id = connection->upper_receive_id;
  FStack_18.data = frame->data + (byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x22b98u + (uint32_t)(connection->addressing_format) * 1u)))) + 1;
  local_1c = 0;
  uVar3 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)((uint32_t)(frame->data) + (uint32_t)((byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x22b98u + (uint32_t)(connection->addressing_format) * 1u))))) * 1u)))) & 0xf;
  FStack_18.length = uVar3;
  uVar1 = cantp_start_upper_receive(upper_id,&FStack_18,(ushort)uVar3,&local_1c);
  if (uVar1 == 0) {
    uVar2 = 1;
    if (uVar3 <= local_1c) {
      uVar1 = cantp_copy_upper_receive_bytes(upper_id,&FStack_18,&local_1c);
      if (uVar1 == 0) {
        uVar2 = 0;
      }
      else {
        uVar2 = 1;
      }
    }
    forward_cantp_receive_result_to_router_7a79e(upper_id,uVar2);
  }
  return;
}

void admit_and_deliver_cantp_single_frame_7adf8(int *param_1,F33CanTpRxConnection *param_2,F33CanTpFrameInfo *param_3)

{
  byte bVar1;
  uint32_t puVar2;
  int extraout_r8;
  uint uVar3;
  int iVar4;
  
  puVar2 = 0xfebeb800u;
  uVar3 = cantp_reject_single_frame_extent(param_2,param_3);
  if ((uVar3 == 0) &&
     (iVar4 = ((void)(param_2->receive_id), (void)(param_2->canif_receive_id), (void)((*((undefined1 *)camry_host_ptr((uint32_t)(((int)(param_3)) + 4))))), (void)(param_3->data), return_const_0_81f62()), iVar4 == 0)) {
    bVar1 = param_2->channel_state_index;
    if (((*((char *)camry_host_ptr((uint32_t)((short)(ushort)bVar1 * 0xc + *param_1 + 8)))) == '\x01') &&
       (((int8_t)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)((uint)bVar1 * 0x20 + -0x68b8)))))) != -0x1f)) {
      iVar4 = arbitrate_cantp_transmit_owner_for_receive_admission_7abe6(param_1, camry_host_addr(param_2));
    }
    else {
      iVar4 = arbitrate_cantp_receive_owner_for_new_frame_7ac9c(param_1, camry_host_addr(param_2));
    }
    if (iVar4 == 0) {
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)((uint)bVar1 * 0x20 + -0x68a1))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)((uint)bVar1 * 0x20 + -0x68a1))))) + '\x01';
      cantp_deliver_single_frame(param_2,param_3);
    }
  }
  return;
}

uint cantp_reject_first_frame_extent(F33CanTpRxConnection *connection,F33CanTpFrameInfo *frame)

{
  uint uVar1;
  uint uVar2;
  
  uVar2 = 1;
  if (((connection->single_frame_only == '\0') && (connection->canif_fc_transmit_id != 0xffff)) &&
     (frame->length == 8)) {
    uVar1 = (uint)(*((volatile uint8_t *)camry_host_ptr((uint32_t)((frame->data + (byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x22b98u + (uint32_t)(connection->addressing_format) * 1u))))) + (uint32_t)(1))))) |
            ((*((volatile uint8_t *)camry_host_ptr((uint32_t)((uint32_t)(frame->data) + (uint32_t)((byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x22b98u + (uint32_t)(connection->addressing_format) * 1u))))) * 1u)))) & 0xf) << 8;
    if (8 - (byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x22b98u + (uint32_t)(connection->addressing_format) * 1u)))) <= uVar1) {
      uVar2 = (uint)(DAT_00022c40 < uVar1);
    }
  }
  return uVar2;
}

void cantp_begin_first_frame_receive
               (F33CanTpRxConnection *connection,F33CanTpFrameInfo *frame,F33CanTpRxState *state)

{
  byte *pbVar1;
  byte bVar2;
  ushort uVar3;
  uint uVar4;
  uint uVar5;
  uint local_20;
  F33CanTpFrameInfo FStack_1c;
  
  bVar2 = (byte)frame->length;
  state->state = 'i';
  uVar3 = connection->buffer_wait_timeout_raw;
  state->first_frame_dlc = bVar2;
  state->timeout_ticks = uVar3 - 3;
  uVar3 = connection->receive_id;
  state->wait_frame_count = 0;
  state->receive_id = uVar3;
  state->expected_sequence_number = '\x01';
  state->flow_status_marker = 0xe1;
  uVar3 = connection->upper_receive_id;
  pbVar1 = ((void *)camry_host_ptr((uint32_t)(frame->data + (byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x22b98u + (uint32_t)(connection->addressing_format) * 1u)))))));
  uVar5 = (uint)bVar2 - ((byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x22b98u + (uint32_t)(connection->addressing_format) * 1u)))) + 2) & 0xff;
  FStack_1c.data = camry_host_addr(pbVar1 + 2);
  local_20 = 0;
  uVar4 = (uint)pbVar1[1] | (*pbVar1 & 0xf) << 8;
  state->remaining_length = uVar4 - uVar5;
  FStack_1c.length = uVar5;
  uVar4 = cantp_start_upper_receive(uVar3,&FStack_1c,(ushort)uVar4,&local_20);
  if (uVar4 == 0) {
    if ((local_20 < uVar5) ||
       (uVar4 = cantp_copy_upper_receive_bytes(uVar3,&FStack_1c,&local_20), uVar4 != 0)) {
      cantp_finish_receive_aggregate(connection,state,'\x01');
    }
  }
  else if (uVar4 == 3) {
    state->flow_status_marker = 0xd2;
  }
  else {
    cantp_reset_receive_owner(state);
  }
  return;
}

void admit_and_begin_cantp_first_frame_7af76(int *param_1,F33CanTpRxConnection *param_2,F33CanTpFrameInfo *param_3)

{
  byte bVar1;
  uint32_t puVar2;
  int extraout_r8;
  uint uVar3;
  int iVar4;
  
  puVar2 = 0xfebeb800u;
  uVar3 = cantp_reject_first_frame_extent(param_2,param_3);
  if ((uVar3 == 0) &&
     (iVar4 = ((void)(param_2->receive_id), (void)(param_2->canif_receive_id), (void)((*((undefined1 *)camry_host_ptr((uint32_t)(((int)(param_3)) + 4))))), (void)(param_3->data), return_const_0_81f62()), iVar4 == 0)) {
    bVar1 = param_2->channel_state_index;
    if (((*((char *)camry_host_ptr((uint32_t)((short)(ushort)bVar1 * 0xc + *param_1 + 8)))) == '\x01') &&
       (((int8_t)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)((uint)bVar1 * 0x20 + -0x68b8)))))) != -0x1f)) {
      iVar4 = arbitrate_cantp_transmit_owner_for_receive_admission_7abe6(param_1, camry_host_addr(param_2));
    }
    else {
      iVar4 = arbitrate_cantp_receive_owner_for_new_frame_7ac9c(param_1, camry_host_addr(param_2));
    }
    if (iVar4 == 0) {
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)((uint)bVar1 * 0x20 + -0x68a1))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)((uint)bVar1 * 0x20 + -0x68a1))))) + '\x01';
      cantp_begin_first_frame_receive
                (param_2,param_3,((F33CanTpRxState *)camry_host_ptr((uint32_t)(puVar2 + (uint)bVar1 * 0x20 + -0x68b0))));
    }
  }
  return;
}

uint cantp_reject_consecutive_frame
               (F33CanTpRxConnection *connection,F33CanTpFrameInfo *frame,F33CanTpRxState *state)

{
  bool bVar1;
  uint uVar2;
  uint uVar3;
  uint uVar4;
  
  uVar4 = 1;
  if (connection->single_frame_only != '\0') {
    return 1;
  }
  uVar2 = frame->length;
  uVar3 = (uint)(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x22b98u + (uint32_t)(connection->addressing_format) * 1u))));
  if ((7 - uVar3 & 0xff) < state->remaining_length) {
    if (uVar2 != 8) {
      return 1;
    }
  }
  else {
    if (8 < uVar2) {
      return 1;
    }
    if (connection->require_padded_receive == '\x01') {
      if (uVar2 != 8) goto LAB_0007b05c;
    }
    else if (uVar2 < (state->remaining_length + uVar3 + 1 & 0xff)) {
      return 1;
    }
  }
  bVar1 = ((*((volatile uint8_t *)camry_host_ptr((uint32_t)((uint32_t)(frame->data) + (uint32_t)(uVar3) * 1u)))) & 0xf) == state->expected_sequence_number;
  uVar4 = (uint)!bVar1;
  if (bVar1) {
    return 0;
  }
LAB_0007b05c:
  cantp_finish_receive_aggregate(connection,state,(uchar)uVar4);
  return uVar4;
}
