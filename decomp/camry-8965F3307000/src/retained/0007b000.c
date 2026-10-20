#include "common.h"

void cantp_append_consecutive_receive
               (F33CanTpRxConnection *connection,F33CanTpFrameInfo *frame,F33CanTpRxState *state)

{
  ushort uVar1;
  F33CanTpRxConnection *extraout_r6;
  F33CanTpRxConnection *pFVar2;
  F33CanTpRxState *extraout_r8;
  F33CanTpRxState *pFVar3;
  int iVar4;
  uint uVar5;
  uint uVar6;
  uchar uVar7;
  uint uVar8;
  uint local_2c;
  F33CanTpFrameInfo FStack_28;
  
  uVar8 = state->remaining_length;
  uVar6 = (byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x22b98u + (uint32_t)(connection->addressing_format) * 1u)))) + 1 & 0xff;
  uVar5 = (byte)frame->length - uVar6 & 0xff;
  pFVar2 = connection;
  pFVar3 = state;
  FStack_28.length = uVar8 & 0xff;
  if (uVar5 < uVar8) {
    uVar7 = state->block_remaining;
    state->expected_sequence_number =
         (*((volatile uint8_t *)camry_host_ptr((uint32_t)((uint32_t)(frame->data) + (uint32_t)((byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x22b98u + (uint32_t)(connection->addressing_format) * 1u))))) * 1u)))) + 1 & 0xf;
    if (uVar7 != '\0') {
      uVar7 = uVar7 + 0xff;
    }
    iVar4 = read_or_repair_cantp_first_flow_byte_7a862(connection);
    if ((iVar4 == 0) || (uVar7 != '\0')) {
      ((F33CanTpRxState *)(state))->state = 'K';
      uVar1 = ((F33CanTpRxConnection *)(connection))->consecutive_receive_timeout_raw + 2;
    }
    else {
      ((F33CanTpRxState *)(state))->state = 'i';
      uVar1 = ((F33CanTpRxConnection *)(connection))->buffer_wait_timeout_raw;
      ((F33CanTpRxState *)(state))->flow_status_marker = 0xe1;
      uVar1 = uVar1 - 3;
    }
    ((F33CanTpRxState *)(state))->timeout_ticks = uVar1;
    ((F33CanTpRxState *)(state))->block_remaining = uVar7;
    pFVar2 = ((F33CanTpRxConnection *)(connection));
    pFVar3 = ((F33CanTpRxState *)(state));
    FStack_28.length = uVar5;
  }
  FStack_28.data = frame->data;
  uVar8 = uVar8 - FStack_28.length;
  uVar1 = pFVar2->upper_receive_id;
  pFVar3->remaining_length = uVar8;
  local_2c = 0;
  FStack_28.data = FStack_28.data + uVar6;
  uVar5 = cantp_copy_upper_receive_bytes(uVar1,&FStack_28,&local_2c);
  uVar7 = '\x01';
  if ((uVar5 != 0) || (uVar7 = '\0', uVar8 == 0)) {
    cantp_finish_receive_aggregate(connection,state,uVar7);
  }
  return;
}

void cantp_handle_consecutive_receive(F33CanTpRxConnection *connection,F33CanTpFrameInfo *frame)

{
  uchar uVar1;
  uint uVar2;
  uint uVar3;
  
  uVar2 = (uint)connection->channel_state_index;
  uVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe4f50u + (uint32_t)(uVar2 * 2) * (uint32_t)sizeof(F33CanTpRxState)) + (uint32_t)(0) * (uint32_t)sizeof(F33CanTpRxState) + (uint32_t)offsetof(F33CanTpRxState, state)))));
  if ((((uVar1 == 'Z') && ((*((volatile uint8_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe4f50u + (uint32_t)(uVar2 * 2) * (uint32_t)sizeof(F33CanTpRxState)) + (uint32_t)(0) * (uint32_t)sizeof(F33CanTpRxState) + (uint32_t)offsetof(F33CanTpRxState, flow_status_marker))))) == 0xf0)) ||
      (uVar1 == 'K')) &&
     ((connection->receive_id == (*((volatile uint16_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe4f50u + (uint32_t)(uVar2 * 2) * (uint32_t)sizeof(F33CanTpRxState)) + (uint32_t)(0) * (uint32_t)sizeof(F33CanTpRxState) + (uint32_t)offsetof(F33CanTpRxState, receive_id))))) &&
      (uVar3 = cantp_reject_consecutive_frame
                         (connection, frame, ((F33CanTpRxState *)camry_host_ptr((uint32_t)((0xfebe4f50u) + uVar2 * 2)))), uVar3 == 0)))) {
    if (uVar1 != 'K') {
      ((void)(connection->canif_fc_transmit_id), return_only_stub_7b246());
    }
    cantp_append_consecutive_receive(connection, frame, ((F33CanTpRxState *)camry_host_ptr((uint32_t)((0xfebe4f50u) + uVar2 * 2))));
  }
  return;
}

void cantp_confirm_receive_flow_control(F33CanTpRxConnection *connection)

{
  uchar uVar1;
  uint uVar2;
  
  uVar2 = (uint)connection->channel_state_index;
  uVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe4f50u + (uint32_t)(uVar2 * 2) * (uint32_t)sizeof(F33CanTpRxState)) + (uint32_t)(0) * (uint32_t)sizeof(F33CanTpRxState) + (uint32_t)offsetof(F33CanTpRxState, state)))));
  if (uVar1 == 'K') {
    return;
  }
  if (uVar1 == 'Z') {
    uVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe4f50u + (uint32_t)(uVar2 * 2) * (uint32_t)sizeof(F33CanTpRxState)) + (uint32_t)(0) * (uint32_t)sizeof(F33CanTpRxState) + (uint32_t)offsetof(F33CanTpRxState, flow_status_marker)))));
    if (uVar1 == 0xf0) {
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe4f50u + (uint32_t)(uVar2 * 2) * (uint32_t)sizeof(F33CanTpRxState)) + (uint32_t)(0) * (uint32_t)sizeof(F33CanTpRxState) + (uint32_t)offsetof(F33CanTpRxState, state))))) = 'K';
      (*((volatile uint16_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe4f50u + (uint32_t)(uVar2 * 2) * (uint32_t)sizeof(F33CanTpRxState)) + (uint32_t)(0) * (uint32_t)sizeof(F33CanTpRxState) + (uint32_t)offsetof(F33CanTpRxState, timeout_ticks))))) =
           connection->consecutive_receive_timeout_raw + 2;
      return;
    }
    if (uVar1 == 0xe1) {
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe4f50u + (uint32_t)(uVar2 * 2) * (uint32_t)sizeof(F33CanTpRxState)) + (uint32_t)(0) * (uint32_t)sizeof(F33CanTpRxState) + (uint32_t)offsetof(F33CanTpRxState, state))))) = 'i';
      (*((volatile uint16_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe4f50u + (uint32_t)(uVar2 * 2) * (uint32_t)sizeof(F33CanTpRxState)) + (uint32_t)(0) * (uint32_t)sizeof(F33CanTpRxState) + (uint32_t)offsetof(F33CanTpRxState, timeout_ticks))))) = connection->buffer_wait_timeout_raw - 3;
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe4f50u + (uint32_t)(uVar2 * 2) * (uint32_t)sizeof(F33CanTpRxState)) + (uint32_t)(0) * (uint32_t)sizeof(F33CanTpRxState) + (uint32_t)offsetof(F33CanTpRxState, flow_status_marker))))) = 0xe1;
      return;
    }
    if (uVar1 == 0xd2) goto LAB_0007b1fc;
  }
  else if (uVar1 == 'i') {
    return;
  }
  DAT_febe4f3c = 0xf;
LAB_0007b1fc:
  cantp_reset_receive_owner(((F33CanTpRxState *)camry_host_ptr((uint32_t)(0xfebe4f50u + uVar2 * 32u))));
  return;
}

void return_only_stub_7b204(void)

{
  return;
}

void return_only_stub_7b206(void)

{
  return;
}

void return_only_stub_7b208(void)

{
  return;
}

uint cantp_submit_can_frame(ushort canif_id,F33CanTpFrameInfo *frame)

{
  int iVar1;
  uint uVar2;
  bool bVar3;
  F33PduInfo local_14;
  
  local_14.data = frame->data;
  local_14.length = (ushort)frame->length;
  iVar1 = ((void)(canif_id), (void)(&local_14), return_const_0_81ffa());
  if (iVar1 == 0) {
    uVar2 = canif_transmit(canif_id,&local_14);
    bVar3 = uVar2 == 0;
  }
  else {
    bVar3 = iVar1 == 1;
  }
  return (uint)!bVar3;
}

void return_only_stub_7b246(void)

{
  return;
}

void cantp_tick_channel_timeouts(void)

{
  byte bVar1;
  ushort uVar2;
  ushort uVar3;
  uint32_t puVar4;
  uint32_t puVar5;
  int iVar6;
  uint uVar7;
  ushort uVar8;
  
  puVar4 = 0xfebeb800u;
  puVar5 = 0x23dfcu;
  if (((int8_t)DAT_febe4f3d) == -0x56) {
    iVar6 = camry_host_addr(get_cantp_configuration_pointer_7a32e());
    if (iVar6 != 0) {
      bVar1 = (*((byte *)camry_host_ptr((uint32_t)(iVar6 + 0xc))));
      uVar2 = (*((ushort *)camry_host_ptr((uint32_t)(puVar5 + -0x11b8))));
      for (uVar7 = 0; uVar7 < bVar1; uVar7 = uVar7 + 1 & 0xff) {
        iVar6 = uVar7 * 0x20;
        uVar3 = (*((ushort *)camry_host_ptr((uint32_t)(puVar4 + iVar6 + -0x68aa))));
        uVar8 = (*((ushort *)camry_host_ptr((uint32_t)(puVar4 + iVar6 + -0x68ba))));
        if (uVar2 < uVar3) {
          (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x68c4))))) = 0xf;
          uVar3 = 0;
        }
        else if (uVar3 != 0) {
          uVar3 = uVar3 - 1;
        }
        if (uVar2 < uVar8) {
          (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x68c4))))) = 0xf;
          uVar8 = 0;
        }
        else if (uVar8 != 0) {
          uVar8 = uVar8 - 1;
        }
        (*((ushort *)camry_host_ptr((uint32_t)(puVar4 + iVar6 + -0x68aa)))) = uVar3;
        (*((ushort *)camry_host_ptr((uint32_t)(puVar4 + iVar6 + -0x68ba)))) = uVar8;
      }
    }
  }
  else if (DAT_febe4f3d != 'U') {
    DAT_febe4f3c = 0xf;
  }
  return;
}

void reset_cantp_channels_and_seed_flow_parameters_7b2c4(int *param_1)

{
  byte bVar1;
  byte bVar2;
  int iVar3;
  undefined8 uVar4;
  uint uVar5;
  ushort uVar6;
  uint uVar7;
  
  uVar4 = 0x23dfcfebeb800;
  uVar5 = (uint)DAT_00022c48;
  for (uVar7 = 0; uVar7 < uVar5; uVar7 = uVar7 + 1 & 0xff) {
    (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe4f40u + (uint32_t)(uVar7 * 2) * (uint32_t)sizeof(F33CanTpTxStatePrefix) + (uint32_t)offsetof(F33CanTpTxStatePrefix, transmit_id))))) = 0xffff;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe4f40u + (uint32_t)(uVar7 * 2) * (uint32_t)sizeof(F33CanTpTxStatePrefix) + (uint32_t)offsetof(F33CanTpTxStatePrefix, sequence_number))))) = 0xff;
    (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe4f50u + (uint32_t)(uVar7 * 2) * (uint32_t)sizeof(F33CanTpRxState) + (uint32_t)offsetof(F33CanTpRxState, receive_id))))) = 0xffff;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe4f50u + (uint32_t)(uVar7 * 2) * (uint32_t)sizeof(F33CanTpRxState) + (uint32_t)offsetof(F33CanTpRxState, expected_sequence_number))))) = 0xff;
    (*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xfebe4f40u + (uint32_t)(uVar7 * 2) * (uint32_t)sizeof(F33CanTpTxStatePrefix) + (uint32_t)offsetof(F33CanTpTxStatePrefix, remaining_or_accepted_length))))) = 0;
    (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe4f40u + (uint32_t)(uVar7 * 2) * (uint32_t)sizeof(F33CanTpTxStatePrefix) + (uint32_t)offsetof(F33CanTpTxStatePrefix, timeout_ticks))))) = 0;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe4f40u + (uint32_t)(uVar7 * 2) * (uint32_t)sizeof(F33CanTpTxStatePrefix) + (uint32_t)offsetof(F33CanTpTxStatePrefix, state))))) = 0xe1;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe4f40u + (uint32_t)(uVar7 * 2) * (uint32_t)sizeof(F33CanTpTxStatePrefix) + (uint32_t)offsetof(F33CanTpTxStatePrefix, block_remaining))))) = '\0';
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe4f40u + (uint32_t)(uVar7 * 2) * (uint32_t)sizeof(F33CanTpTxStatePrefix) + (uint32_t)offsetof(F33CanTpTxStatePrefix, block_size))))) = '\0';
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe4f40u + (uint32_t)(uVar7 * 2) * (uint32_t)sizeof(F33CanTpTxStatePrefix) + (uint32_t)offsetof(F33CanTpTxStatePrefix, spacing_ticks))))) = '\0';
    ((volatile F33CanTpTxStatePrefix *)camry_host_ptr((uint32_t)(0xfebe4f40u + (uint32_t)(uVar7 * 2) * (uint32_t)sizeof(F33CanTpTxStatePrefix))))[0].opaque_0d[0] = '\0';
    ((volatile F33CanTpTxStatePrefix *)camry_host_ptr((uint32_t)(0xfebe4f40u + (uint32_t)(uVar7 * 2) * (uint32_t)sizeof(F33CanTpTxStatePrefix))))[0].opaque_0d[1] = '\0';
    ((volatile F33CanTpTxStatePrefix *)camry_host_ptr((uint32_t)(0xfebe4f40u + (uint32_t)(uVar7 * 2) * (uint32_t)sizeof(F33CanTpTxStatePrefix))))[0].opaque_0d[2] = '\0';
    (*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xfebe4f50u + (uint32_t)(uVar7 * 2) * (uint32_t)sizeof(F33CanTpRxState) + (uint32_t)offsetof(F33CanTpRxState, remaining_length))))) = 0;
    (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe4f50u + (uint32_t)(uVar7 * 2) * (uint32_t)sizeof(F33CanTpRxState) + (uint32_t)offsetof(F33CanTpRxState, timeout_ticks))))) = 0;
    (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe4f50u + (uint32_t)(uVar7 * 2) * (uint32_t)sizeof(F33CanTpRxState) + (uint32_t)offsetof(F33CanTpRxState, wait_frame_count))))) = 0;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe4f50u + (uint32_t)(uVar7 * 2) * (uint32_t)sizeof(F33CanTpRxState) + (uint32_t)offsetof(F33CanTpRxState, state))))) = 0xe1;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe4f50u + (uint32_t)(uVar7 * 2) * (uint32_t)sizeof(F33CanTpRxState) + (uint32_t)offsetof(F33CanTpRxState, first_frame_dlc))))) = '\0';
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe4f50u + (uint32_t)(uVar7 * 2) * (uint32_t)sizeof(F33CanTpRxState) + (uint32_t)offsetof(F33CanTpRxState, block_remaining))))) = '\0';
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe4f50u + (uint32_t)(uVar7 * 2) * (uint32_t)sizeof(F33CanTpRxState) + (uint32_t)offsetof(F33CanTpRxState, flow_status_marker))))) = 0xf0;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe4f50u + (uint32_t)(uVar7 * 2) * (uint32_t)sizeof(F33CanTpRxState) + (uint32_t)offsetof(F33CanTpRxState, admission_generation))))) = '\0';
  }
  uVar5 = (uint)DAT_00022c47;
  for (uVar7 = 0; uVar7 < uVar5; uVar7 = uVar7 + 1 & 0xff) {
    cantp_rx_flow_parameters_with_complements[uVar7][0] = 0;
    cantp_rx_flow_parameters_with_complements[uVar7][1] = 0;
  }
  bVar2 = *(byte *)(param_1 + 3);
  uVar6 = 0;
  while( true ) {
    iVar3 = (int)uVar4;
    uVar5 = 0;
    if (bVar2 <= uVar6) break;
    bVar1 = (*((byte *)camry_host_ptr((uint32_t)(*param_1 + (short)uVar6 * 0xc + 9))));
    for (uVar5 = 0; uVar5 < bVar1; uVar5 = uVar5 + 1 & 0xff) {
      iVar3 = uVar5 * 0x20 + (*((int *)camry_host_ptr((uint32_t)(*param_1 + (short)uVar6 * 0xc))));
      store_cantp_first_flow_byte_with_complement_7a84c(((byte *)camry_host_ptr((uint32_t)(iVar3))), (*((undefined1 *)camry_host_ptr((uint32_t)(iVar3 + 0x16)))));
      store_cantp_second_flow_byte_with_complement_7a89a(((byte *)camry_host_ptr((uint32_t)(iVar3))), (*((undefined1 *)camry_host_ptr((uint32_t)(iVar3 + 0x17)))));
    }
    uVar6 = uVar6 + 1 & 0xff;
  }
  do {
    (*((undefined1 *)camry_host_ptr((uint32_t)(uVar5 + iVar3 + -0x6904)))) = 0;
    uVar5 = uVar5 + 1;
  } while (uVar5 < 0x40);
  (*((undefined1 *)camry_host_ptr((uint32_t)(iVar3 + -0x68c4)))) = 0xf0;
  return_only_stub_7b208();
  (*((undefined1 *)camry_host_ptr((uint32_t)(iVar3 + -0x68c3)))) = 0xaa;
  return;
}

void mark_cantp_uninitialized_with_clear_fault_status_7b3a6(void)

{
  DAT_febe4f3c = 0xf0;
  DAT_febe4f3d = 0x55;
  return;
}

undefined4 reject_cantp_payload_exceeding_eight_byte_frame_7b3b6(int param_1,int param_2)

{
  undefined4 uVar1;
  
  uVar1 = 0x10;
  if ((uint)(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x22b98u + (uint32_t)((*((byte *)camry_host_ptr((uint32_t)(param_1 + 0xc))))) * 1u)))) + param_2 + 1 < 9) {
    uVar1 = 0;
  }
  return uVar1;
}

uint cantp_accept_transmit_length
               (F33CanTpConfiguration *configuration,ushort transmit_id,uint length)

{
  byte bVar1;
  uint32_t puVar2;
  F33CanTpTxConnection *pFVar3;
  int iVar4;
  uint uVar5;
  
  puVar2 = 0xfebeb800u;
  uVar5 = 1;
  if ((length != 0) && (length <= DAT_00022c40)) {
    pFVar3 = cantp_find_transmit_connection(configuration,transmit_id);
    iVar4 = reject_cantp_payload_exceeding_eight_byte_frame_7b3b6(camry_host_addr(pFVar3), length);
    if ((iVar4 != 0x10) || (pFVar3->single_frame_only == '\0')) {
      bVar1 = pFVar3->channel_state_index;
      if ((((int8_t)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)((uint)bVar1 * 0x20 + -0x68b8)))))) == -0x1f) &&
         (((*((volatile uint8_t *)camry_host_ptr((uint32_t)((uint32_t)((uint32_t)(configuration->channel_rows) + (uint32_t)((short)(ushort)bVar1) * (uint32_t)sizeof(F33CanTpChannelConfiguration)) + (uint32_t)(0) * (uint32_t)sizeof(F33CanTpChannelConfiguration) + (uint32_t)offsetof(F33CanTpChannelConfiguration, half_duplex))))) == '\0' ||
          ((((int8_t)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)((uint)bVar1 * 0x20 + -0x68a6)))))) == -0x1f &&
           ((*((volatile uint8_t *)camry_host_ptr((uint32_t)((uint32_t)((uint32_t)(configuration->channel_rows) + (uint32_t)((short)(ushort)bVar1) * (uint32_t)sizeof(F33CanTpChannelConfiguration)) + (uint32_t)(0) * (uint32_t)sizeof(F33CanTpChannelConfiguration) + (uint32_t)offsetof(F33CanTpChannelConfiguration, half_duplex))))) == '\x01')))))) {
        (*((ushort *)camry_host_ptr((uint32_t)(puVar2 + (uint)bVar1 * 0x20 + -0x68bc)))) = transmit_id;
        (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)((uint)bVar1 * 0x20 + -0x68b8))))) = 0xd2;
        uVar5 = 0;
        (*((uint *)camry_host_ptr((uint32_t)(puVar2 + (uint)bVar1 * 0x20 + -0x68c0)))) = length;
      }
    }
  }
  return uVar5;
}

void cantp_reset_transmit_owner(F33CanTpTxStatePrefix *state)

{
  state->transmit_id = 0xffff;
  state->remaining_or_accepted_length = 0;
  state->state = 0xe1;
  state->timeout_ticks = 0;
  state->sequence_number = 0xff;
  state->block_remaining = '\0';
  state->block_size = '\0';
  state->spacing_ticks = '\0';
  return;
}

void forward_cantp_transmit_result_to_router_7b46e(undefined2 param_1,undefined1 param_2)

{
  call_21cf8_with_masked_u16_and_byte_81a4c(param_1,param_2);
  return;
}

uint cantp_cancel_transmit_owner(F33CanTpConfiguration *configuration,ushort transmit_id)

{
  char cVar1;
  byte bVar2;
  uint32_t puVar3;
  F33CanTpTxConnection *pFVar4;
  int iVar5;
  uint uVar6;
  int *piVar7;
  
  puVar3 = 0xfebeb800u;
  uVar6 = 1;
  pFVar4 = cantp_find_transmit_connection(configuration,transmit_id);
  if (pFVar4->cancel_supported != '\x01') {
    return 1;
  }
  bVar2 = pFVar4->channel_state_index;
  piVar7 = ((int *)camry_host_ptr((uint32_t)(puVar3 + (uint)bVar2 * 0x20 + -0x68c0)));
  cVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)((uint)bVar2 * 0x20 + -0x68b8)))));
  if ((*((ushort *)camry_host_ptr((uint32_t)(puVar3 + (uint)bVar2 * 0x20 + -0x68bc)))) != transmit_id) {
    return 1;
  }
  if (cVar1 == 'x') {
LAB_0007b4ec:
    uVar6 = 0;
  }
  else {
    if (((int8_t)cVar1) == -0x79) {
      if (*piVar7 == 0) goto LAB_0007b4fc;
      goto LAB_0007b4ec;
    }
    if (((((int8_t)cVar1) == -0x6a) || (((int8_t)cVar1) == -0x5b)) || (((int8_t)cVar1) == -0x4c)) goto LAB_0007b4ec;
    if (((int8_t)cVar1) == -0x3d) goto LAB_0007b4fc;
    if (((int8_t)cVar1) == -0x2e) {
      iVar5 = reject_cantp_payload_exceeding_eight_byte_frame_7b3b6(camry_host_addr(pFVar4), *piVar7);
      if (iVar5 != 0x10) goto LAB_0007b4fc;
      goto LAB_0007b4ec;
    }
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x68c4))))) = 0xf;
  }
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + (uint)bVar2 * 0x20 + -0x68bc)))) = 0xffff;
  *piVar7 = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)((uint)bVar2 * 0x20 + -0x68b8))))) = 0xe1;
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + (uint)bVar2 * 0x20 + -0x68ba)))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)((uint)bVar2 * 0x20 + -0x68b7))))) = 0xff;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)((uint)bVar2 * 0x20 + -0x68b6))))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)((uint)bVar2 * 0x20 + -0x68b5))))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)((uint)bVar2 * 0x20 + -0x68b4))))) = 0;
LAB_0007b4fc:
  if (uVar6 == 0) {
    if ((((int8_t)cVar1) == -0x4c) || (((int8_t)cVar1) == -0x79)) {
      ((void)(pFVar4->canif_frame_id), return_only_stub_7b246());
    }
    forward_cantp_transmit_result_to_router_7b46e(pFVar4->upper_response_id,1);
  }
  return uVar6;
}

void cantp_write_transmit_address_byte(F33CanTpTxConnection *connection,uchar *frame)

{
  uchar uVar1;
  
  uVar1 = connection->addressing_format;
  if (uVar1 == '\x04') {
    uVar1 = connection->address_byte;
  }
  else {
    if (uVar1 != '\x02' && uVar1 != '\x03') {
      return;
    }
    uVar1 = connection->extended_transmit_address_byte;
  }
  *frame = uVar1;
  return;
}

uint cantp_copy_upper_transmit_bytes(ushort upper_id,F33CanTpFrameInfo *chunk,uint *remaining)

{
  uint8_t stack_record_12[18];
  uint uVar1;
  (*((uint16_t *)(stack_record_12 + 6))) = (undefined2)chunk->length;
  (*((uint32_t *)(stack_record_12 + 2))) = chunk->data;
  (*((uint16_t *)(stack_record_12 + 0))) = 0;
  uVar1 = ((void)(((uint32_t *)(stack_record_12 + 2))), (void)(0), (void)(stack_record_12), call_21cf0_with_masked_u16_81a66(upper_id, camry_host_addr(((uint32_t *)(stack_record_12 + 2))),  0x0, camry_host_addr(((uint8_t *)stack_record_12 + 0))));
  *remaining = (uint)(*((uint16_t *)(stack_record_12 + 0)));
  return uVar1;
}

void abort_cantp_transmit_if_state_matches_7b572(int param_1,undefined4 *param_2,char param_3)

{
  if (*(char *)(param_2 + 2) == param_3) {
    *(undefined2 *)(param_2 + 1) = 0xffff;
    *param_2 = 0;
    *(undefined1 *)(param_2 + 2) = 0xe1;
    (*((undefined2 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_2) + 6)))) = 0;
    (*((undefined1 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_2) + 9)))) = 0xff;
    (*((undefined1 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_2) + 10)))) = 0;
    (*((undefined1 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_2) + 0xb)))) = 0;
    *(undefined1 *)(param_2 + 3) = 0;
    forward_cantp_transmit_result_to_router_7b46e((*((undefined2 *)camry_host_ptr((uint32_t)(param_1 + 8)))),1);
  }
  return;
}

void cantp_build_and_queue_single_frame
               (F33CanTpTxConnection *connection,F33CanTpTxStatePrefix *state,uchar payload_length)

{
  uchar uVar1;
  ushort uVar2;
  uint32_t puVar3;
  undefined4 uVar4;
  uint uVar5;
  uint uVar6;
  uint uVar7;
  uint uVar8;
  uint local_28;
  F33CanTpFrameInfo FStack_24;
  
  puVar3 = 0x23dfcu;
  uVar6 = (uint)payload_length;
  uVar1 = connection->addressing_format;
  if (uVar1 == '\x04') {
    ((volatile uint8_t *)camry_host_ptr(0xfebe4efcu))[0] = connection->address_byte;
  }
  else if (uVar1 == '\x02' || uVar1 == '\x03') {
    ((volatile uint8_t *)camry_host_ptr(0xfebe4efcu))[0] = connection->extended_transmit_address_byte;
  }
  uVar8 = (uint)(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x22b98u + (uint32_t)(connection->addressing_format) * 1u))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe4efcu + (uint32_t)(uVar8) * 1u)))) = payload_length;
  uVar7 = uVar8 + uVar6 + 1 & 0xff;
  uVar8 = uVar8 + 1 & 0xff;
  local_28 = 0;
  if (connection->pad_frames_to_eight == '\x01') {
    uVar7 = 8;
  }
  FStack_24.data = camry_host_addr(((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe4efcu + (uint32_t)(uVar8) * 1u))));
  FStack_24.length = uVar6;
  uVar5 = cantp_copy_upper_transmit_bytes(connection->upper_response_id,&FStack_24,&local_28);
  uVar4 = 0xd2;
  if (uVar5 == 0) {
    uVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x11b6)))));
    while (uVar8 = uVar8 + uVar6 & 0xff, uVar8 < uVar7) {
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe4efcu + (uint32_t)(uVar8) * 1u)))) = uVar1;
      uVar6 = 1;
    }
    FStack_24.data = camry_host_addr(cantp_shared_frame_scratch);
    if (state->state == 0xd2) {
      state->state = 0xc3;
      uVar2 = connection->frame_confirmation_timeout_raw;
      state->remaining_or_accepted_length = 0;
      state->timeout_ticks = uVar2 + 2;
    }
    FStack_24.length = uVar7;
    uVar6 = cantp_submit_can_frame(connection->canif_frame_id,&FStack_24);
    uVar4 = 0xc3;
    if (uVar6 == 0) {
      return;
    }
  }
  abort_cantp_transmit_if_state_matches_7b572(camry_host_addr(connection), state, uVar4);
  return;
}

void cantp_build_and_queue_first_frame
               (F33CanTpTxConnection *connection,F33CanTpTxStatePrefix *state,uint total_length)

{
  uchar uVar1;
  byte bVar2;
  ushort uVar3;
  uint uVar4;
  undefined4 uVar5;
  uint uVar6;
  uint local_28;
  F33CanTpFrameInfo FStack_24;
  
  uVar1 = connection->addressing_format;
  if (uVar1 == '\x04') {
    ((volatile uint8_t *)camry_host_ptr(0xfebe4efcu))[0] = connection->address_byte;
  }
  else if (uVar1 == '\x02' || uVar1 == '\x03') {
    ((volatile uint8_t *)camry_host_ptr(0xfebe4efcu))[0] = connection->extended_transmit_address_byte;
  }
  uVar4 = (uint)(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x22b98u + (uint32_t)(connection->addressing_format) * 1u))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe4efcu + (uint32_t)(uVar4 + 1) * 1u)))) = (uchar)total_length;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe4efcu + (uint32_t)(uVar4) * 1u)))) = (byte)(total_length >> 8) | 0x10;
  bVar2 = connection->frame_capacity;
  uVar4 = uVar4 + 2 & 0xff;
  local_28 = 0;
  FStack_24.data = camry_host_addr(((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe4efcu + (uint32_t)(uVar4) * 1u))));
  uVar6 = bVar2 - uVar4 & 0xff;
  FStack_24.length = uVar6;
  uVar4 = cantp_copy_upper_transmit_bytes(connection->upper_response_id,&FStack_24,&local_28);
  uVar5 = 0xd2;
  if (uVar4 == 0) {
    FStack_24.data = camry_host_addr(cantp_shared_frame_scratch);
    if (state->state == 0xd2) {
      state->state = 0xb4;
      uVar3 = connection->frame_confirmation_timeout_raw;
      state->remaining_or_accepted_length = total_length - uVar6;
      state->timeout_ticks = uVar3 + 2;
      state->sequence_number = 0xff;
    }
    FStack_24.length = (uint)bVar2;
    uVar4 = cantp_submit_can_frame(connection->canif_frame_id,&FStack_24);
    uVar5 = 0xb4;
    if (uVar4 == 0) {
      return;
    }
  }
  abort_cantp_transmit_if_state_matches_7b572(camry_host_addr(connection), state, uVar5);
  return;
}

void abort_cantp_transmit_in_confirmation_states_7b6f2(int param_1,undefined4 *param_2)

{
  char cVar1;
  
  cVar1 = *(char *)(param_2 + 2);
  if (((((int8_t)cVar1) == -0x3d) || (((int8_t)cVar1) == -0x4c)) || (((int8_t)cVar1) == -0x79)) {
    *(undefined2 *)(param_2 + 1) = 0xffff;
    *param_2 = 0;
    *(undefined1 *)(param_2 + 2) = 0xe1;
    (*((undefined2 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_2) + 6)))) = 0;
    (*((undefined1 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_2) + 9)))) = 0xff;
    (*((undefined1 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_2) + 10)))) = 0;
    (*((undefined1 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_2) + 0xb)))) = 0;
    *(undefined1 *)(param_2 + 3) = 0;
    ((void)((*((undefined2 *)camry_host_ptr((uint32_t)(param_1 + 10))))), return_only_stub_7b246());
    forward_cantp_transmit_result_to_router_7b46e((*((undefined2 *)camry_host_ptr((uint32_t)(param_1 + 8)))),1);
  }
  return;
}

void abort_cantp_transmit_in_state_a5_7b72a(int param_1,undefined4 *param_2)

{
  if (*(char *)(param_2 + 2) == -0x5b) {
    *(undefined2 *)(param_2 + 1) = 0xffff;
    *param_2 = 0;
    *(undefined1 *)(param_2 + 2) = 0xe1;
    (*((undefined2 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_2) + 6)))) = 0;
    (*((undefined1 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_2) + 9)))) = 0xff;
    (*((undefined1 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_2) + 10)))) = 0;
    (*((undefined1 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_2) + 0xb)))) = 0;
    *(undefined1 *)(param_2 + 3) = 0;
    forward_cantp_transmit_result_to_router_7b46e((*((undefined2 *)camry_host_ptr((uint32_t)(param_1 + 8)))),1);
  }
  return;
}

void cantp_build_and_queue_consecutive_frame
               (F33CanTpTxConnection *connection,F33CanTpTxStatePrefix *state)

{
  byte bVar1;
  ushort uVar2;
  uchar uVar3;
  uint uVar4;
  uint32_t puVar5;
  undefined4 uVar6;
  uint uVar7;
  uint uVar8;
  uint uVar9;
  uint uVar10;
  byte bVar11;
  uint local_30;
  F33CanTpFrameInfo FStack_2c;
  
  puVar5 = 0x23dfcu;
  uVar3 = connection->addressing_format;
  if (uVar3 == '\x04') {
    ((volatile uint8_t *)camry_host_ptr(0xfebe4efcu))[0] = connection->address_byte;
  }
  else if (uVar3 == '\x02' || uVar3 == '\x03') {
    ((volatile uint8_t *)camry_host_ptr(0xfebe4efcu))[0] = connection->extended_transmit_address_byte;
  }
  bVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x22b98u + (uint32_t)(connection->addressing_format) * 1u))));
  if (state->sequence_number == 0xff) {
    bVar11 = 1;
  }
  else {
    bVar11 = state->sequence_number + 1 & 0xf;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe4efcu + (uint32_t)(bVar1) * 1u)))) = bVar11 | 0x20;
  uVar9 = (uint)connection->frame_capacity;
  uVar8 = state->remaining_or_accepted_length;
  uVar10 = bVar1 + 1 & 0xff;
  uVar4 = uVar9 - uVar10 & 0xff;
  if (uVar4 < uVar8) {
    uVar8 = uVar8 - uVar4;
  }
  else {
    uVar4 = uVar8 & 0xff;
    uVar8 = 0;
    uVar9 = uVar10 + uVar4 & 0xff;
    if (connection->pad_frames_to_eight == '\x01') {
      uVar9 = 8;
    }
  }
  FStack_2c.data = camry_host_addr(((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe4efcu + (uint32_t)(uVar10) * 1u))));
  local_30 = 0;
  FStack_2c.length = uVar4;
  uVar7 = cantp_copy_upper_transmit_bytes(connection->upper_response_id,&FStack_2c,&local_30);
  if (uVar7 == 0) {
    uVar3 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x11b6)))));
    while (uVar10 = uVar10 + uVar4 & 0xff, uVar10 < uVar9) {
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe4efcu + (uint32_t)(uVar10) * 1u)))) = uVar3;
      uVar4 = 1;
    }
    FStack_2c.data = camry_host_addr(cantp_shared_frame_scratch);
    if (state->state == 0x96) {
      state->state = 0x87;
      uVar2 = connection->frame_confirmation_timeout_raw;
      state->sequence_number = bVar11;
      state->remaining_or_accepted_length = uVar8;
      state->timeout_ticks = uVar2 + 2;
      uVar3 = state->block_remaining;
      if (uVar3 != '\0') {
        uVar3 = uVar3 + 0xff;
      }
      state->block_remaining = uVar3;
    }
    FStack_2c.length = uVar9;
    uVar8 = cantp_submit_can_frame(connection->canif_frame_id,&FStack_2c);
    uVar6 = 0x87;
    if (uVar8 == 0) {
      return;
    }
  }
  else {
    uVar6 = 0x96;
    if (uVar7 == 2) {
      return;
    }
  }
  abort_cantp_transmit_if_state_matches_7b572(camry_host_addr(connection), state, uVar6);
  return;
}

void abort_cantp_transmit_in_state_96_7b848(int param_1,undefined4 *param_2)

{
  if (*(char *)(param_2 + 2) == -0x6a) {
    *(undefined2 *)(param_2 + 1) = 0xffff;
    *param_2 = 0;
    *(undefined1 *)(param_2 + 2) = 0xe1;
    (*((undefined2 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_2) + 6)))) = 0;
    (*((undefined1 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_2) + 9)))) = 0xff;
    (*((undefined1 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_2) + 10)))) = 0;
    (*((undefined1 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_2) + 0xb)))) = 0;
    *(undefined1 *)(param_2 + 3) = 0;
    forward_cantp_transmit_result_to_router_7b46e((*((undefined2 *)camry_host_ptr((uint32_t)(param_1 + 8)))),1);
  }
  return;
}

void cantp_open_consecutive_copy_window
               (F33CanTpTxConnection *connection,F33CanTpTxStatePrefix *state)

{
  ushort uVar1;
  ushort uVar2;
  
  uVar2 = 0;
  uVar1 = state->spacing_ticks + 3;
  if (uVar1 <= connection->consecutive_copy_timeout_raw) {
    uVar2 = connection->consecutive_copy_timeout_raw - uVar1;
  }
  if (state->state == 'x') {
    state->timeout_ticks = uVar2;
    state->state = 0x96;
  }
  return;
}

void cantp_run_transmit_channels(void)

{
  char cVar1;
  short sVar2;
  byte bVar3;
  undefined8 uVar4;
  F33CanTpTxConnection *connection;
  F33CanTpTxConnection *connection_00;
  F33CanTpTxStatePrefix *state;
  F33CanTpConfiguration *configuration;
  int iVar5;
  uint total_length;
  uint uVar6;
  F33CanTpTxConnection *unaff_r27;
  F33CanTpTxStatePrefix *state_00;
  
  uVar4 = 0xfebeb800;
  if ((((int8_t)DAT_febe4f3d) == -0x56) &&
     (configuration = (F33CanTpConfiguration *)get_cantp_configuration_pointer_7a32e(),camry_host_addr(configuration)!=camry_host_addr((F33CanTpConfiguration *)0x0))) {
    bVar3 = configuration->channel_count;
    for (uVar6 = 0; uVar6 < bVar3; uVar6 = uVar6 + 1 & 0xff) {
      iVar5 = uVar6 * 0x20 + (int)uVar4;
      state_00 = ((F33CanTpTxStatePrefix *)camry_host_ptr((uint32_t)(iVar5 + -0x68c0)));
      cVar1 = (*((char *)camry_host_ptr((uint32_t)(iVar5 + -0x68b8))));
      total_length = state_00->remaining_or_accepted_length;
      sVar2 = (*((short *)camry_host_ptr((uint32_t)(iVar5 + -0x68ba))));
      if (((((cVar1 == 'x') || (((int8_t)cVar1) == -0x79)) || (((int8_t)cVar1) == -0x6a)) ||
          ((((int8_t)cVar1) == -0x5b || (((int8_t)cVar1) == -0x4c)))) || ((((int8_t)cVar1) == -0x3d || (((int8_t)cVar1) == -0x2e)))) {
        unaff_r27 = cantp_find_transmit_connection(configuration,(*((ushort *)camry_host_ptr((uint32_t)(iVar5 + -0x68bc)))));
        if (camry_host_addr(unaff_r27)!=camry_host_addr((F33CanTpTxConnection *)0x0)) goto LAB_0007b916;
LAB_0007b908:
        (*((undefined1 *)camry_host_ptr((uint32_t)((int)uVar4 + -0x68c4)))) = 0xf;
        cantp_reset_transmit_owner(state_00);
      }
      else {
        if (((int8_t)cVar1) != -0x1f) goto LAB_0007b908;
LAB_0007b916:
        if (((int8_t)cVar1) != -0x1f) {
          if (((int8_t)cVar1) == -0x2e) {
            iVar5 = reject_cantp_payload_exceeding_eight_byte_frame_7b3b6(camry_host_addr(unaff_r27), total_length);
            if (iVar5 == 0) {
              cantp_build_and_queue_single_frame(unaff_r27,state_00,(uchar)total_length);
            }
            else {
              cantp_build_and_queue_first_frame(unaff_r27,state_00,total_length);
            }
          }
          else if (((((int8_t)cVar1) == -0x3d) || (((int8_t)cVar1) == -0x4c)) || (((int8_t)cVar1) == -0x79)) {
            if (sVar2 == 0) {
              abort_cantp_transmit_in_confirmation_states_7b6f2(camry_host_addr(unaff_r27), state_00);
            }
          }
          else if (((int8_t)cVar1) == -0x5b) {
            if (sVar2 == 0) {
              abort_cantp_transmit_in_state_a5_7b72a(camry_host_addr(unaff_r27), state_00);
            }
          }
          else if (((int8_t)cVar1) == -0x6a) {
            cantp_build_and_queue_consecutive_frame(unaff_r27,state_00);
            if (sVar2 == 0) {
              abort_cantp_transmit_in_state_96_7b848(camry_host_addr(unaff_r27), state_00);
            }
          }
          else if (sVar2 == 0) {
            cantp_open_consecutive_copy_window(unaff_r27,state_00);
            cantp_build_and_queue_consecutive_frame(unaff_r27,state_00);
          }
        }
      }
    }
  }
  return;
}

void cantp_finish_transmit_aggregate
               (F33CanTpTxConnection *connection,F33CanTpTxStatePrefix *state,uchar result)

{
  state->transmit_id = 0xffff;
  state->remaining_or_accepted_length = 0;
  state->state = 0xe1;
  state->timeout_ticks = 0;
  state->sequence_number = 0xff;
  state->block_remaining = '\0';
  state->block_size = '\0';
  state->spacing_ticks = '\0';
  forward_cantp_transmit_result_to_router_7b46e(connection->upper_response_id,result);
  return;
}

uint cantp_reject_flow_control_frame
               (F33CanTpTxConnection *connection,F33CanTpFrameInfo *frame,
               F33CanTpTxStatePrefix *state)

{
  byte bVar1;
  uint uVar2;
  
  uVar2 = 1;
  if (connection->single_frame_only != '\0') {
    return 1;
  }
  if (frame->length < 8) {
    if (connection->require_padded_flow_control == '\x01') goto LAB_0007ba0c;
    if (frame->length < ((byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x22b98u + (uint32_t)(connection->addressing_format) * 1u)))) + 3 & 0xff)) {
      return 1;
    }
  }
  bVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)((uint32_t)(frame->data) + (uint32_t)((byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x22b98u + (uint32_t)(connection->addressing_format) * 1u))))) * 1u)))) & 0xf;
  uVar2 = (uint)(2 < bVar1);
  if (bVar1 < 3) {
    return uVar2;
  }
LAB_0007ba0c:
  cantp_finish_transmit_aggregate(connection,state,(uchar)uVar2);
  return uVar2;
}

void cantp_capture_initial_flow_parameters
               (F33CanTpTxStatePrefix *state,uchar block_size,uchar stmin_encoding)

{
  uchar uVar1;
  
  if (state->sequence_number == 0xff) {
    uVar1 = "\x01\x03\x03\x03\x03\x03\x04\x04\x04\x04\x04\x05\x05\x05\x05\x05\x06\x06\x06\x06\x06\a\a\a\a\a\b\b\b\b\b\t\t\t\t\t\n\n\n\n\n\v\v\v\v\v\f\f\f\f\f\r\r\r\r\r\x0e\x0e\x0e\x0e\x0e\x0f\x0f\x0f\x0f\x0f\x10\x10\x10\x10\x10\x11\x11\x11\x11\x11\x12\x12\x12\x12\x12\x13\x13\x13\x13\x13\x14\x14\x14\x14\x14\x15\x15\x15\x15\x15\x16\x16\x16\x16\x16\x17\x17\x17\x17\x17\x18\x18\x18\x18\x18\x19\x19\x19\x19\x19\x1a\x1a\x1a\x1a\x1a\x1b\x1b\x1b\x1b\x1b\x1c\x1c\x1c\x1c\x1c\x1c\x1c\x1c\x1c\x1c\x1c\x1c\x1c\x1c\x1c\x1c\x1c\x1c\x1c\x1c\x1c\x1c\x1c\x1c\x1c\x1c\x1c\x1c\x1c\x1c\x1c\x1c\x1c\x1c\x1c\x1c\x1c\x1c\x1c\x1c\x1c\x1c\x1c\x1c\x1c\x1c\x1c\x1c\x1c\x1c\x1c\x1c\x1c\x1c\x1c\x1c\x1c\x1c\x1c\x1c\x1c\x1c\x1c\x1c\x1c\x1c\x1c\x1c\x1c\x1c\x1c\x1c\x1c\x1c\x1c\x1c\x1c\x1c\x1c\x1c\x1c\x1c\x1c\x1c\x1c\x1c\x1c\x1c\x1c\x1c\x1c\x1c\x1c\x1c\x1c\x1c\x1c\x1c\x1c\x1c\x1c\x1c\x1c\x1c\x1c\x1c\x1c\x1c\x1c\x1c\x1c\x1c\x1c\x1c\x1c\x03\x03\x03\x03\x03\x03\x03\x03\x03\x1c\x1c\x1c\x1c\x1c\x1c"
            [stmin_encoding];
    state->block_size = block_size;
    state->spacing_ticks = uVar1;
  }
  return;
}

void cantp_apply_flow_control(F33CanTpTxConnection *connection,F33CanTpFrameInfo *frame)

{
  byte *pbVar1;
  uint uVar2;
  ushort uVar3;
  
  uVar2 = (uint)connection->channel_state_index;
  pbVar1 = ((void *)camry_host_ptr((uint32_t)(frame->data + (byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x22b98u + (uint32_t)(connection->addressing_format) * 1u)))))));
  if ((*pbVar1 & 0xf) == 0) {
    cantp_capture_initial_flow_parameters
              (((F33CanTpTxStatePrefix *)camry_host_ptr((uint32_t)(0xfebe4f40u + uVar2 * 32u))), pbVar1[1], pbVar1[2]);
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe4f40u + (uint32_t)(uVar2 * 2) * (uint32_t)sizeof(F33CanTpTxStatePrefix)) + (uint32_t)(0) * (uint32_t)sizeof(F33CanTpTxStatePrefix) + (uint32_t)offsetof(F33CanTpTxStatePrefix, block_remaining))))) =
         (*((volatile uint8_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe4f40u + (uint32_t)(uVar2 * 2) * (uint32_t)sizeof(F33CanTpTxStatePrefix)) + (uint32_t)(0) * (uint32_t)sizeof(F33CanTpTxStatePrefix) + (uint32_t)offsetof(F33CanTpTxStatePrefix, block_size)))));
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe4f40u + (uint32_t)(uVar2 * 2) * (uint32_t)sizeof(F33CanTpTxStatePrefix)) + (uint32_t)(0) * (uint32_t)sizeof(F33CanTpTxStatePrefix) + (uint32_t)offsetof(F33CanTpTxStatePrefix, state))))) = 0x96;
    uVar3 = connection->consecutive_copy_timeout_raw - 3;
  }
  else {
    if ((*pbVar1 & 0xf) != 1) {
      cantp_finish_transmit_aggregate
                (connection, ((F33CanTpTxStatePrefix *)camry_host_ptr((uint32_t)(0xfebe4f40u + uVar2 * 32u))), '\x01');
      return;
    }
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe4f40u + (uint32_t)(uVar2 * 2) * (uint32_t)sizeof(F33CanTpTxStatePrefix)) + (uint32_t)(0) * (uint32_t)sizeof(F33CanTpTxStatePrefix) + (uint32_t)offsetof(F33CanTpTxStatePrefix, state))))) = 0xa5;
    uVar3 = connection->flow_control_timeout_raw + 2;
  }
  (*((volatile uint16_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe4f40u + (uint32_t)(uVar2 * 2) * (uint32_t)sizeof(F33CanTpTxStatePrefix)) + (uint32_t)(0) * (uint32_t)sizeof(F33CanTpTxStatePrefix) + (uint32_t)offsetof(F33CanTpTxStatePrefix, timeout_ticks))))) = uVar3;
  return;
}

void cantp_handle_flow_control(F33CanTpTxConnection *connection,F33CanTpFrameInfo *frame)

{
  uchar uVar1;
  uint uVar2;
  
  uVar2 = (uint)connection->channel_state_index;
  uVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe4f40u + (uint32_t)(uVar2 * 2) * (uint32_t)sizeof(F33CanTpTxStatePrefix)) + (uint32_t)(0) * (uint32_t)sizeof(F33CanTpTxStatePrefix) + (uint32_t)offsetof(F33CanTpTxStatePrefix, state)))));
  if ((((uVar1 == 0xb4) || (uVar1 == 0xa5)) ||
      ((uVar1 == 0x87 &&
       ((((*((volatile uint8_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe4f40u + (uint32_t)(uVar2 * 2) * (uint32_t)sizeof(F33CanTpTxStatePrefix)) + (uint32_t)(0) * (uint32_t)sizeof(F33CanTpTxStatePrefix) + (uint32_t)offsetof(F33CanTpTxStatePrefix, block_remaining))))) == '\0' &&
         ((*((volatile uint8_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe4f40u + (uint32_t)(uVar2 * 2) * (uint32_t)sizeof(F33CanTpTxStatePrefix)) + (uint32_t)(0) * (uint32_t)sizeof(F33CanTpTxStatePrefix) + (uint32_t)offsetof(F33CanTpTxStatePrefix, block_size))))) != '\0')) &&
        ((*((volatile uint32_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe4f40u + (uint32_t)(uVar2 * 2) * (uint32_t)sizeof(F33CanTpTxStatePrefix)) + (uint32_t)(0) * (uint32_t)sizeof(F33CanTpTxStatePrefix) + (uint32_t)offsetof(F33CanTpTxStatePrefix, remaining_or_accepted_length))))) != 0)))))) &&
     (((*((volatile uint16_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe4f40u + (uint32_t)(uVar2 * 2) * (uint32_t)sizeof(F33CanTpTxStatePrefix)) + (uint32_t)(0) * (uint32_t)sizeof(F33CanTpTxStatePrefix) + (uint32_t)offsetof(F33CanTpTxStatePrefix, transmit_id))))) == connection->transmit_id &&
      (uVar2 = cantp_reject_flow_control_frame
                         (connection, frame, ((F33CanTpTxStatePrefix *)camry_host_ptr((uint32_t)((0xfebe4f40u) + uVar2 * 2)))), uVar2 == 0))))
  {
    if (uVar1 != 0xa5) {
      ((void)(connection->canif_frame_id), return_only_stub_7b246());
    }
    cantp_apply_flow_control(connection,frame);
  }
  return;
}

void cantp_handle_frame_confirmation(F33CanTpTxConnection *connection)

{
  uchar uVar1;
  uint uVar2;
  F33CanTpTxStatePrefix *state;
  
  uVar2 = (uint)connection->channel_state_index;
  uVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe4f40u + (uint32_t)(uVar2 * 2) * (uint32_t)sizeof(F33CanTpTxStatePrefix)) + (uint32_t)(0) * (uint32_t)sizeof(F33CanTpTxStatePrefix) + (uint32_t)offsetof(F33CanTpTxStatePrefix, state)))));
  state = ((void *)camry_host_ptr((uint32_t)((0xfebe4f40u) + uVar2 * 2)));
  if (uVar1 == 'x') {
    return;
  }
  if (uVar1 == 0x87) {
    if (state->remaining_or_accepted_length != 0) {
      if (((*((volatile uint8_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe4f40u + (uint32_t)(uVar2 * 2) * (uint32_t)sizeof(F33CanTpTxStatePrefix)) + (uint32_t)(0) * (uint32_t)sizeof(F33CanTpTxStatePrefix) + (uint32_t)offsetof(F33CanTpTxStatePrefix, block_remaining))))) != '\0') ||
         ((*((volatile uint8_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe4f40u + (uint32_t)(uVar2 * 2) * (uint32_t)sizeof(F33CanTpTxStatePrefix)) + (uint32_t)(0) * (uint32_t)sizeof(F33CanTpTxStatePrefix) + (uint32_t)offsetof(F33CanTpTxStatePrefix, block_size))))) == '\0')) {
        (*((volatile uint8_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe4f40u + (uint32_t)(uVar2 * 2) * (uint32_t)sizeof(F33CanTpTxStatePrefix)) + (uint32_t)(0) * (uint32_t)sizeof(F33CanTpTxStatePrefix) + (uint32_t)offsetof(F33CanTpTxStatePrefix, state))))) = 'x';
        (*((volatile uint16_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe4f40u + (uint32_t)(uVar2 * 2) * (uint32_t)sizeof(F33CanTpTxStatePrefix)) + (uint32_t)(0) * (uint32_t)sizeof(F33CanTpTxStatePrefix) + (uint32_t)offsetof(F33CanTpTxStatePrefix, timeout_ticks))))) =
             (ushort)(*((volatile uint8_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe4f40u + (uint32_t)(uVar2 * 2) * (uint32_t)sizeof(F33CanTpTxStatePrefix)) + (uint32_t)(0) * (uint32_t)sizeof(F33CanTpTxStatePrefix) + (uint32_t)offsetof(F33CanTpTxStatePrefix, spacing_ticks)))));
        return;
      }
      goto LAB_0007bb80;
    }
  }
  else {
    if (uVar1 == 0x96) {
      return;
    }
    if (uVar1 == 0xa5) {
      return;
    }
    if (uVar1 == 0xb4) {
LAB_0007bb80:
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe4f40u + (uint32_t)(uVar2 * 2) * (uint32_t)sizeof(F33CanTpTxStatePrefix)) + (uint32_t)(0) * (uint32_t)sizeof(F33CanTpTxStatePrefix) + (uint32_t)offsetof(F33CanTpTxStatePrefix, state))))) = 0xa5;
      (*((volatile uint16_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe4f40u + (uint32_t)(uVar2 * 2) * (uint32_t)sizeof(F33CanTpTxStatePrefix)) + (uint32_t)(0) * (uint32_t)sizeof(F33CanTpTxStatePrefix) + (uint32_t)offsetof(F33CanTpTxStatePrefix, timeout_ticks))))) =
           connection->flow_control_timeout_raw + 2;
      return;
    }
    if (uVar1 != 0xc3) {
      if (uVar1 == 0xd2) {
        return;
      }
      DAT_febe4f3c = 0xf;
      (*((volatile uint16_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe4f40u + (uint32_t)(uVar2 * 2) * (uint32_t)sizeof(F33CanTpTxStatePrefix)) + (uint32_t)(0) * (uint32_t)sizeof(F33CanTpTxStatePrefix) + (uint32_t)offsetof(F33CanTpTxStatePrefix, transmit_id))))) = 0xffff;
      state->remaining_or_accepted_length = 0;
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe4f40u + (uint32_t)(uVar2 * 2) * (uint32_t)sizeof(F33CanTpTxStatePrefix)) + (uint32_t)(0) * (uint32_t)sizeof(F33CanTpTxStatePrefix) + (uint32_t)offsetof(F33CanTpTxStatePrefix, state))))) = 0xe1;
      (*((volatile uint16_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe4f40u + (uint32_t)(uVar2 * 2) * (uint32_t)sizeof(F33CanTpTxStatePrefix)) + (uint32_t)(0) * (uint32_t)sizeof(F33CanTpTxStatePrefix) + (uint32_t)offsetof(F33CanTpTxStatePrefix, timeout_ticks))))) = 0;
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe4f40u + (uint32_t)(uVar2 * 2) * (uint32_t)sizeof(F33CanTpTxStatePrefix)) + (uint32_t)(0) * (uint32_t)sizeof(F33CanTpTxStatePrefix) + (uint32_t)offsetof(F33CanTpTxStatePrefix, sequence_number))))) = 0xff;
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe4f40u + (uint32_t)(uVar2 * 2) * (uint32_t)sizeof(F33CanTpTxStatePrefix)) + (uint32_t)(0) * (uint32_t)sizeof(F33CanTpTxStatePrefix) + (uint32_t)offsetof(F33CanTpTxStatePrefix, block_remaining))))) = '\0';
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe4f40u + (uint32_t)(uVar2 * 2) * (uint32_t)sizeof(F33CanTpTxStatePrefix)) + (uint32_t)(0) * (uint32_t)sizeof(F33CanTpTxStatePrefix) + (uint32_t)offsetof(F33CanTpTxStatePrefix, block_size))))) = '\0';
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe4f40u + (uint32_t)(uVar2 * 2) * (uint32_t)sizeof(F33CanTpTxStatePrefix)) + (uint32_t)(0) * (uint32_t)sizeof(F33CanTpTxStatePrefix) + (uint32_t)offsetof(F33CanTpTxStatePrefix, spacing_ticks))))) = '\0';
      return;
    }
  }
  cantp_finish_transmit_aggregate(connection,state,'\0');
  return;
}

byte initialize_network_enable_mask_complement_pairs_7bb9c(void)

{
  uint32_t puVar1;
  byte bVar2;
  
  puVar1 = 0xfebeb800u;
  bVar2 = return_low_byte_first_argument_7be2e(DAT_00021866);
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6853))))) = 0xff;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6854))))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6852))))) = bVar2;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6851))))) = bVar2 ^ 0xff;
  return bVar2;
}

void publish_changed_network_enable_mask_to_eight_channels_7bbc2(void)

{
  byte bVar1;
  undefined1 uVar2;
  uint32_t puVar3;
  undefined4 uVar4;
  uint uVar5;
  
  puVar3 = 0xfebeb800u;
  uVar5 = (uint)DAT_febe4fac;
  uVar4 = call_interrupt_guard_and_return_zero_7a2da();
  bVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6852)))));
  uVar2 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6851)))));
  ((void)(uVar4), thunk_pop_and_restore_priority_mask_stack_6a4c4());
  if (uVar5 != bVar1) {
    uVar4 = call_interrupt_guard_and_return_zero_7a2da();
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6854))))) = bVar1;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6853))))) = uVar2;
    ((void)(uVar4), thunk_pop_and_restore_priority_mask_stack_6a4c4());
    uVar5 = 0;
    do {
      if ((1 << (uVar5 & 0x1f) & 0xffU & (uint)bVar1) == 0) {
        uVar4 = 0;
      }
      else {
        uVar4 = 2;
      }
      update_complemented_global_mask_bit_7ea26(uVar5,uVar4);
      uVar5 = uVar5 + 1;
    } while (uVar5 < 8);
  }
  return;
}

undefined4 update_masked_network_enable_request_with_complement_7bc12(byte param_1,byte param_2)

{
  uint32_t puVar1;
  undefined4 uVar2;
  byte bVar3;
  
  puVar1 = 0xfebeb800u;
  uVar2 = call_interrupt_guard_and_return_zero_7a2da();
  bVar3 = (param_1 ^ 0xff) & (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6852))))) | param_1 & param_2;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6852))))) = bVar3;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6851))))) = bVar3 ^ 0xff;
  ((void)(uVar2), thunk_pop_and_restore_priority_mask_stack_6a4c4());
  return uVar2;
}

byte get_validated_published_network_enable_mask_7bc42(void)

{
  byte bVar1;
  
  bVar1 = DAT_febe4fac;
  if ((DAT_febe4fad ^ DAT_febe4fac) != 0xff) {
    bVar1 = 0;
  }
  return bVar1;
}

undefined4 invoke_enabled_network_callback_slot_zero_7bc56(uint param_1)

{
  undefined4 uVar1;
  
  param_1 = param_1 & 0xff;
  uVar1 = 0x11;
  if ((param_1 < DAT_00021865) && ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x21869u + (uint32_t)(param_1) * 1u)))) != '\0')) {
    uVar1 = (*(int (*)())camry_indirect((uint32_t)(((((code *)(uintptr_t)((uint32_t)((uintptr_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x2186cu + (uint32_t)((byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x21867u + (uint32_t)(param_1) * 1u))))) * 4u)))))))))))))))((uint)(byte)param_1);
  }
  return uVar1;
}

undefined4 invoke_enabled_network_callback_slot_four_7bc8a(uint param_1)

{
  undefined4 uVar1;
  
  param_1 = param_1 & 0xff;
  uVar1 = 0x11;
  if ((param_1 < DAT_00021865) && ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x21869u + (uint32_t)(param_1) * 1u)))) != '\0')) {
    uVar1 = (*(int (*)())camry_indirect((uint32_t)(((((code *)(uintptr_t)((uint32_t)((uintptr_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x2186cu + (uint32_t)((byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x21867u + (uint32_t)(param_1) * 1u))))) * 4u)))) + 4))))))))))))(param_1);
  }
  return uVar1;
}

undefined4 scale_network_zero_stub_value_by_config_period_7bcbe(byte param_1)

{
  undefined4 uVar1;
  
  if (param_1 < DAT_00021865) {
    uVar1 = return_const_0_7be42();
    uVar1 = convert_u16_units_to_ceiling_configured_ticks_7bde2(uVar1);
  }
  else {
    uVar1 = 0;
  }
  return uVar1;
}

undefined1 get_bounded_network_configuration_flags_7bcde(uint param_1)

{
  if ((param_1 & 0xff) < (uint)DAT_00021865) {
    return (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x21869u + (uint32_t)(param_1 & 0xff) * 1u))));
  }
  return 0;
}

void mark_bounded_network_group_request_one_7bcf4(byte param_1)

{
  if (param_1 < DAT_00021865) {
    set_valid_tx_group_mode_one_7e4ea((uint)(byte)param_1);
  }
  return;
}

void mark_bounded_network_group_request_two_and_schedule_pdus_7bd0a(byte param_1)

{
  if (param_1 < DAT_00021865) {
    set_tx_group_mode_two_and_defer_periods_7e4fe((uint)(byte)param_1);
  }
  return;
}

byte get_upper_network_indication_zero_one_or_three_7bd3a(uint param_1)

{
  byte bVar1;
  byte bVar2;
  
  bVar2 = 0;
  if (((param_1 & 0xff) < (uint)DAT_00021865) &&
     ((bVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe3df0u + (uint32_t)(param_1 & 0xff) * 1u)))), bVar1 < 2 || (bVar1 == 3)))) {
    bVar2 = bVar1;
  }
  return bVar2;
}

uint map_kind_1800_or_2000_to_first_network_index_7bd58(short param_1,undefined2 param_2)

{
  byte bVar1;
  uint32_t puVar2;
  uint uVar3;
  uint uVar4;
  uint uVar5;
  
  puVar2 = 0x23dfcu;
  uVar5 = 0xff;
  uVar4 = uVar5;
  if ((param_1 == 0x1800) || (param_1 == 0x2000)) {
    uVar3 = query_group_callback_with_masked_u16_81f30(param_1,param_2);
    if ((((uVar3 & 0xf800) == 0) || ((uVar3 & 0xf800) == 0x800)) &&
       (bVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x2597))))), uVar4 = map_first_encoded_pdu_table_to_global_network_7c6c4(uVar3), bVar1 <= uVar4)) {
      uVar4 = uVar5;
    }
  }
  return uVar4;
}

uint map_kind_zero_1800_or_2000_to_second_network_index_7bd96(short param_1,undefined2 param_2)

{
  byte bVar1;
  uint32_t puVar2;
  uint uVar3;
  uint uVar4;
  uint uVar5;
  
  puVar2 = 0x23dfcu;
  if (((param_1 != 0) && (param_1 != 0x1800)) && (param_1 != 0x2000)) {
    param_1 = -1;
  }
  uVar5 = 0xff;
  uVar4 = uVar5;
  if (param_1 != -1) {
    uVar3 = query_group_callback_with_masked_u16_81f30(param_1,param_2);
    if ((((uVar3 & 0xf800) == 0) || ((uVar3 & 0xf800) == 0x800)) &&
       (bVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x2597))))), uVar4 = map_second_encoded_pdu_table_to_global_network_7c6e8(uVar3), bVar1 <= uVar4)) {
      uVar4 = uVar5;
    }
  }
  return uVar4;
}

uint convert_u16_units_to_ceiling_configured_ticks_7bde2(uint param_1)

{
  uint uVar1;
  uint uVar2;
  int iVar3;
  int iVar4;
  uint uVar5;
  ushort uVar6;
  
  iVar4 = 0x1e;
  iVar3 = 0x11;
  uVar6 = 0;
  uVar5 = ((param_1 & 0xffff) * 1000 + (uint)DAT_00021860) - 1;
  uVar2 = (uint)DAT_00021860 << 0x10;
  do {
    uVar6 = (ushort)(uVar6 << 1);
    uVar1 = uVar2;
    if (iVar4 == 0x1e) {
      uVar1 = -uVar2;
    }
    uVar5 = uVar5 + uVar1;
    if ((uVar5 & 0x80000000) == 0) {
      uVar6 = (ushort)(uVar6 | 1);
      iVar4 = 0x1e;
    }
    else {
      iVar4 = 0xe1;
    }
    uVar2 = uVar2 >> 1;
    iVar3 = iVar3 + -1;
  } while (iVar3 != 0);
  return (uint)uVar6;
}

undefined1 return_low_byte_first_argument_7be2e(undefined1 param_1)

{
  return param_1;
}

void return_only_stub_7be34(void)

{
  return;
}

void return_only_stub_7be36(void)

{
  return;
}

void return_only_stub_7be38(void)

{
  return;
}

void return_only_stub_7be3a(void)

{
  return;
}

void return_only_stub_7be3c(void)

{
  return;
}

void return_only_stub_7be3e(void)

{
  return;
}

void return_only_stub_7be40(void)

{
  return;
}

undefined4 return_const_0_7be42(void)

{
  return 0;
}

void return_only_stub_7be46(void)

{
  return;
}

void return_only_stub_7be48(void)

{
  return;
}

void return_only_stub_7be4a(void)

{
  return;
}

void return_only_stub_7be4c(void)

{
  return;
}

void return_only_stub_7be4e(void)

{
  return;
}

void return_only_stub_7be50(void)

{
  return;
}

void return_only_stub_7be52(void)

{
  return;
}

void return_only_stub_7be56(void)

{
  return;
}

uint dispatch_dcm_start_of_reception_callback_7be58(undefined2 param_1,undefined4 param_2,undefined2 param_3, undefined4 param_4)

{
  return (*(int (*)())camry_indirect((uint32_t)(PTR_dcm_start_of_reception_0002188c)))(param_1,param_2,param_3, param_4);
}

uint dispatch_dcm_copy_receive_data_callback_7be6c(undefined2 param_1, undefined4 param_2, undefined4 param_3)

{
  return (*(int (*)())camry_indirect((uint32_t)(PTR_dcm_copy_receive_data_00021890)))(param_1, param_2, param_3);
}

uint dispatch_dcm_copy_transmit_data_callback_7be7e(undefined2 param_1, undefined4 param_2, undefined4 param_3, undefined4 param_4)

{
  return (*(int (*)())camry_indirect((uint32_t)(PTR_dcm_copy_transmit_data_00021894)))(param_1, param_2, param_3, param_4);
}

uint32_t dispatch_dcm_receive_indication_callback_7be90(undefined2 param_1,undefined1 param_2)

{
  return (*(int (*)())camry_indirect((uint32_t)(PTR_dcm_receive_indication_00021898)))(param_1,param_2);
}

void dispatch_dcm_transmit_confirmation_callback_7bea4(undefined2 param_1,undefined1 param_2)

{
  (*(int (*)())camry_indirect((uint32_t)(PTR_dcm_transmit_confirmation_0002189c)))(param_1,param_2);
  return;
}

uint32_t invoke_pdu_callback_slot_218a0_7beb8(undefined2 param_1)

{
  return (*(int (*)())camry_indirect((uint32_t)(PTR_FUN_000218a0)))(param_1);
}

void apply_offset_network_policy_with_optional_zero_reset_7bed0(char param_1,undefined1 param_2,char param_3)

{
  undefined4 uVar1;
  
  param_1 = DAT_0002183d + param_1;
  if (param_3 == '\x01') {
    uVar1 = call_interrupt_guard_and_return_zero_7a2da();
    forward_bounded_network_u16_policy_value_7a09c(param_1,0);
    forward_bounded_network_low_two_policy_bits_7a074(param_1,param_2);
    ((void)(uVar1), thunk_pop_and_restore_priority_mask_stack_6a4c4());
  }
  else {
    forward_bounded_network_low_two_policy_bits_7a074(param_1,param_2);
  }
  return;
}

void reconcile_and_apply_swapped_network_policy_bits_7bf10(ushort param_1,undefined1 param_2)

{
  int iVar1;
  uint uVar2;
  uint uVar3;
  
  param_1 = param_1 & 0xff;
  uVar3 = 0;
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe3de5u + (uint32_t)((short)param_1 * 6) * 1u)))) != '\x0f') {
    iVar1 = (*(int (*)())camry_indirect((uint32_t)(PTR_reconcile_requested_normal_network_policy_00021820)))(param_1,param_2);
    if (iVar1 != 0) {
      return;
    }
    uVar2 = dispatch_record_callback_slot_thirty_two_7f3a6(param_1);
    if ((uVar2 & 1) == 0) {
      uVar3 = 0;
    }
    else {
      uVar3 = 2;
    }
    if ((uVar2 >> 1 & 1) != 0) {
      uVar3 = uVar3 | 1;
    }
  }
  apply_offset_network_policy_with_optional_zero_reset_7bed0(param_1,uVar3,param_2);
  return;
}

void reconcile_all_network_enable_and_policy_masks_7bf60(void)

{
  uint8_t stack_record_27[39];
  char *pcVar1;
  byte bVar2;
  byte bVar3;
  uint32_t puVar4;
  uint32_t puVar5;
  uint uVar6;
  int iVar7;
  undefined4 uVar8;
  uint uVar9;
  uint uVar10;
  ushort uVar11;
  ushort uVar12;
  
  puVar4 = 0xfebeb800u;
  puVar5 = 0x23dfcu;
  uVar6 = get_validated_published_network_enable_mask_7bc42();
  bVar2 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x25c0)))));
  bVar3 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x25bf)))));
  for (uVar12 = 0; uVar12 < bVar2; uVar12 = uVar12 + 1 & 0xff) {
    uVar11 = bVar3 + uVar12 & 0xff;
    pcVar1 = ((undefined *)camry_host_ptr((uint32_t)(puVar4 + (short)uVar12 * 6 + -0x7a1c)));
    set_paired_channel_bytes_831be(uVar11,uVar6,uVar6);
    iVar7 = get_record_compact_state_or_five_7e998(uVar11);
    uVar9 = 0;
    uVar10 = 0;
    if (iVar7 == 2 || iVar7 == 3) {
      (*((uint16_t *)(stack_record_27 + 1))) = 0xff;
      stack_record_27[0] = -1;
      ((void)((stack_record_27 + 1)), (void)(stack_record_27), dispatch_offset_record_callback_slot_twenty_eight_7f316(uVar11));
      uVar9 = uVar6;
      if (stack_record_27[0] != '\x03') {
        uVar9 = 0;
      }
      if (*pcVar1 == '\x0f') {
        uVar10 = get_record_u16_mask_low_byte_or_zero_7eb62(uVar11);
        uVar10 = (uVar10 ^ 0xff) & uVar6;
      }
    }
    uVar8 = (*(int (*)())camry_indirect((uint32_t)(((((code *)(uintptr_t)((uint32_t)((uintptr_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(puVar5 + -0x25cc))))))))))))(uVar12,uVar9);
    set_second_bank_3dec_channel_byte_831dc(uVar11,uVar8);
    set_second_bank_3dee_channel_byte_831f0(uVar11,uVar10);
    (*(int (*)())camry_indirect((uint32_t)(((((code *)(uintptr_t)((uint32_t)((uintptr_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(puVar5 + -0x25d8))))))))))))(uVar12);
    reconcile_and_apply_swapped_network_policy_bits_7bf10(uVar12,0);
  }
  return;
}
