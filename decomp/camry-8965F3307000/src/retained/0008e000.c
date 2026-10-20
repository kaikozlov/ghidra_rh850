#include "common.h"

uint serialize_event_and_merge_selected_output_8e074(undefined4 param_1,uint *param_2,undefined4 param_3)

{
  uint8_t stack_record_5e[94];
  uint8_t stack_record_62[98];
  char cVar1;
  char cVar2;
  undefined1 uVar3;
  undefined1 uVar4;
  undefined1 uVar5;
  undefined2 uVar6;
  ushort uVar7;
  short sVar8;
  uint uVar9;
  uint *puStack_58;
  ushort *puStack_48;
  undefined1 *puStack_44;
  uVar3 = DAT_febf45e2;
  uVar5 = DAT_febf45e0;
  cVar2 = DAT_febf45df;
  uVar4 = DAT_febf45de;
  cVar1 = DAT_febf45dc;
  uVar6 = DAT_febf45d8;
  uVar7 = DAT_febf45d6;
  sVar8 = DAT_febf45d4;
  (*((uint16_t *)(stack_record_62 + 6))) = DAT_febf45d0;
  (*((uint16_t *)(stack_record_62 + 8))) = DAT_febf45d2;
  uVar9 = (uint)DAT_febf45dd;
  (*((uint16_t *)(stack_record_62 + 2))) = 0;
  puStack_58 = param_2;
  (*((uint32_t *)(stack_record_62 + 14))) = param_1;
  (*((uint32_t *)(stack_record_62 + 18))) = param_3;
  if (DAT_febf45e1 == '\0') {
    if (*param_2 < 0x10000) {
      (*((uint16_t *)(stack_record_62 + 0))) = (ushort)*param_2;
    }
    else {
      (*((uint16_t *)(stack_record_62 + 0))) = 0xffff;
    }
    uVar9 = serialize_selected_proprietary_event(((undefined *)camry_host_ptr(0xfebf45e4u)),stack_record_62);
    uVar7 = uVar7 - (*((uint16_t *)(stack_record_62 + 0)));
    sVar8 = sVar8 + (*((uint16_t *)(stack_record_62 + 0)));
    if ((uVar9 != 0) && (uVar9 != 2)) {
      uVar4 = map_event_serialization_status_to_nrc_8debe(uVar9);
    }
    stack_record_62[38] = '\x01';
  }
  else {
    if (DAT_febf45e1 != '\x02') {
      uVar9 = 1;
      sVar8 = 0;
      stack_record_62[38] = '\x01';
      uVar6 = 0;
      stack_record_62[47] = DAT_febf45de;
      stack_record_62[39] = DAT_febf45e0;
      goto LAB_0008e14e;
    }
    if (uVar9 == 2) {
      (*((uint16_t *)(stack_record_62 + 0))) = DAT_febf45d6;
      uVar9 = serialize_selected_proprietary_event(((undefined *)camry_host_ptr(0xfebf45e4u)),stack_record_62);
      uVar7 = uVar7 - (*((uint16_t *)(stack_record_62 + 0)));
      sVar8 = sVar8 + (*((uint16_t *)(stack_record_62 + 0)));
      if ((uVar9 != 0) && (uVar9 != 2)) {
        uVar4 = map_event_serialization_status_to_nrc_8debe(uVar9);
      }
    }
    stack_record_62[38] = cVar2;
    if (cVar2 == '\x02') {
      uVar6 = 0;
      uVar5 = map_event_serialization_status_to_nrc_8debe(1);
      stack_record_62[38] = '\x01';
    }
  }
  stack_record_62[47] = uVar4;
  stack_record_62[39] = uVar5;
  if (uVar9 == 2) {
    DAT_febf45d0 = (*((uint16_t *)(stack_record_62 + 6)));
    DAT_febf45d2 = (*((uint16_t *)(stack_record_62 + 8)));
    DAT_febf45d4 = sVar8;
    DAT_febf45d6 = uVar7;
    DAT_febf45d8 = uVar6;
    DAT_febf45dc = cVar1;
    DAT_febf45dd = 2;
    DAT_febf45de = uVar4;
    DAT_febf45df = stack_record_62[38];
    DAT_febf45e0 = uVar5;
    DAT_febf45e1 = 2;
    DAT_febf45e2 = uVar3;
    DAT_febf45e3 = 10;
    return DAT_febf45e3;
  }
LAB_0008e14e:
  puStack_48 = (stack_record_62 + 2);
  stack_record_62[46] = (undefined1)uVar9;
  puStack_44 = ((uint8_t *)(stack_record_5e));
  (*((uint32_t *)(stack_record_5e + 46))) = 0xfebf45e4u;
  (*((uint32_t *)(stack_record_62 + 42))) = 0;
  (*((uint32_t *)(stack_record_62 + 22))) = (*((uint32_t *)(stack_record_62 + 14)));
  (*((uint32_t *)(stack_record_62 + 34))) = (*((uint32_t *)(stack_record_62 + 18)));
  (*((uint16_t *)(stack_record_62 + 40))) = uVar6;
  (*((int16_t *)(stack_record_62 + 48))) = sVar8;
  if (cVar1 == '\x01') {
    DAT_febf45e3 = merge_sorted_big_endian_u16_lists_dedup_equal_heads_8dee2(((uint8_t *)stack_record_62 + 46), ((uint8_t *)stack_record_62 + 38), ((uint8_t *)stack_record_62 + 22));
  }
  else {
    DAT_febf45e3 = select_first_successful_payload_or_error_8dff6((stack_record_62 + 46),(stack_record_62 + 38),(stack_record_62 + 22));
  }
  *puStack_58 = (uint)(*((uint16_t *)(stack_record_62 + 2)));
  DAT_febf45dc = 0;
  DAT_febf45d0 = 0;
  DAT_febf45e1 = 0;
  DAT_febf45dd = 1;
  DAT_febf45d4 = 0;
  DAT_febf45d2 = 0;
  DAT_febf45d6 = 0x300;
  DAT_febf45de = 0;
  DAT_febf45df = 1;
  DAT_febf45d8 = 0;
  DAT_febf45e0 = 0;
  DAT_febf45e2 = uVar3;
  return DAT_febf45e3;
}

void reset_proprietary_dispatch_continuation_8e1e0(void)

{
  dcm_proprietary_continuation.selected_index = '\0';
  dcm_proprietary_continuation.side_result = '\x01';
  dcm_proprietary_continuation.application_result = '\x01';
  dcm_proprietary_continuation.phase = '\0';
  dcm_proprietary_continuation.side_status = 0xff;
  return;
}

uint dcm_join_proprietary_start(F33DiagProprietaryMessage *message,uchar *selected_index)

{
  uint uVar1;
  uint uVar2;
  uchar lower_status;
  uchar uVar3;
  uint uVar4;
  uchar uVar5;
  uchar uStack_1d;
  
  uVar3 = dcm_proprietary_continuation.application_result;
  uStack_1d = dcm_proprietary_continuation.side_status;
  if (dcm_proprietary_continuation.phase == '\0') {
    uVar4 = 0;
    do {
      uVar2 = message->request_length;
      uVar3 = '\0';
      if (uVar4 < (uVar2 & 0xff)) {
        uVar3 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)((uint32_t)(message->request) + (uint32_t)(uVar4) * 1u))));
      }
      uVar1 = uVar4 + 1;
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebf48fcu + (uint32_t)(uVar4) * 1u)))) = uVar3;
      uVar4 = uVar1;
    } while (uVar1 < 0x40);
    lower_status = ((void)((int)0xe0000000), (void)(2), (void)(uVar2 & 0xffff), (void)(((undefined *)camry_host_ptr(0xfebf48fcu))), (void)(&uStack_1d), return_const_0_8b10c());
  }
  else {
    if (dcm_proprietary_continuation.phase != '\x01') {
      return 0;
    }
    lower_status = dcm_proprietary_continuation.side_result;
    if (dcm_proprietary_continuation.side_result == '\x02') {
      lower_status = ((void)(0x22), (void)(2), return_const_0_8b110());
    }
    if (uVar3 != '\x02') goto LAB_0008e2ae;
  }
  uVar3 = begin_proprietary_operation('\0',message,selected_index);
LAB_0008e2ae:
  uVar5 = '\x01';
  uVar4 = merge_two_diagnostic_statuses(uVar3,lower_status,'\0','\x02');
  if ((uVar4 != 2) && (uVar3 = uVar5, lower_status = uVar5, uVar4 != 0)) {
    uVar5 = '\0';
  }
  dcm_proprietary_continuation.application_result = uVar3;
  dcm_proprietary_continuation.side_result = lower_status;
  dcm_proprietary_continuation.phase = uVar5;
  dcm_proprietary_continuation.side_status = uStack_1d;
  return uVar4;
}

uint proprietary_operation_finish_join(uchar selected_index,uint *response_length)

{
  bool bVar1;
  uint uVar2;
  uchar uVar3;
  uchar lower_status;
  uchar application_status;
  uint uVar4;
  uchar uVar5;
  uchar uStack_1d;
  
  uVar3 = dcm_proprietary_continuation.side_status;
  lower_status = dcm_proprietary_continuation.side_result;
  application_status = dcm_proprietary_continuation.application_result;
  uVar5 = dcm_proprietary_continuation.phase;
  uStack_1d = dcm_proprietary_continuation.side_status;
  uVar4 = 0;
  do {
    uVar2 = uVar4 + 1;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebf48fcu + (uint32_t)(uVar4) * 1u)))) = 0;
    uVar4 = uVar2;
  } while (uVar2 < 0x40);
  if (uVar5 == '\x01') {
    uVar5 = '\x02';
    lower_status = ((void)((int)0xe0000001), (void)(2), (void)(0), (void)(((undefined *)camry_host_ptr(0xfebf48fcu))), (void)(&uStack_1d), return_const_0_8b10c());
  }
  else {
    if (uVar5 != '\x02') {
      application_status = '\x01';
      lower_status = '\x01';
      goto LAB_0008e376;
    }
    if (lower_status == '\x02') {
      lower_status = ((void)(0x22), (void)(2), (void)(uVar3), (void)(((undefined *)camry_host_ptr(0xfebf48fcu))), return_const_0_8b110());
    }
    if (application_status != '\x02') goto LAB_0008e376;
  }
  application_status = finish_proprietary_operation(selected_index,response_length);
LAB_0008e376:
  uVar4 = merge_two_diagnostic_statuses(application_status,lower_status,'\0','\x02');
  bVar1 = uVar4 != 2;
  if (bVar1) {
    application_status = '\x01';
  }
  dcm_proprietary_continuation.application_result = application_status;
  if (bVar1) {
    lower_status = '\x01';
  }
  dcm_proprietary_continuation.side_result = lower_status;
  if (bVar1) {
    uVar5 = '\0';
  }
  dcm_proprietary_continuation.phase = uVar5;
  dcm_proprietary_continuation.side_status = uStack_1d;
  return uVar4;
}

void dcm_advance_proprietary_operation(F33DiagProprietaryMessage *message)

{
  camry_write32((camry_sp - 4u) & ~3u, camry_gpr[28]);
  camry_write32((camry_sp - 8u) & ~3u, camry_gpr[29]);
  camry_write32((camry_sp - 12u) & ~3u, camry_gpr[31]);
  camry_sp -= 20u;
  camry_gpr[3] = camry_sp;

  uint8_t *stack_record_11 = (uint8_t *)camry_host_ptr(camry_sp + 3u);
  uint uVar1;
  
  (*((uint32_t *)(stack_record_11 + 1))) = 0;
  stack_record_11[0] = dcm_proprietary_continuation.selected_index;
  uVar1 = (camry_gpr[28] = camry_host_addr(message), camry_gpr[29] = 0xfebf48e4u, camry_gpr[6] = camry_host_addr(message), camry_r7 = camry_gpr[7] = camry_sp + 3u, camry_gpr[31] = 0x8e3c0u, dcm_join_proprietary_start)(message,stack_record_11);
  if (uVar1 == 0) {
    uVar1 = (camry_gpr[6] = camry_read8(camry_sp + 3u), camry_r7 = camry_gpr[7] = camry_sp + 4u, camry_gpr[31] = 0x8e3d2u, proprietary_operation_finish_join)(stack_record_11[0],(stack_record_11 + 1));
  }
  if (uVar1 == 2) {
    dcm_post_service_event(0xf1);
  }
  else if (uVar1 == 0) {
    *((uint8_t *)camry_host_ptr((uint32_t)(message->response))) = *((uint8_t *)camry_host_ptr((uint32_t)(dcm_proprietary_retained_message.request)));
    message->response_length = DAT_0002fc00 + (*((uint32_t *)(stack_record_11 + 1)));
    (camry_gpr[6] = camry_host_addr(message), camry_r7 = camry_gpr[7] = uVar1, camry_gpr[10] = uVar1, camry_gpr[31] = 0x8e402u, dcm_complete_proprietary_message)(message);
  }
  else {
    (camry_gpr[6] = camry_host_addr(message), camry_r7 = camry_gpr[7] = uVar1, camry_gpr[10] = uVar1, camry_gpr[31] = 0x8e408u, dcm_reject_proprietary_message)(message,(uchar)uVar1);
  }
  dcm_proprietary_continuation.selected_index = stack_record_11[0];
  { if (!camry_halted) { camry_gpr[28] = camry_read32((camry_sp + 16u) & ~3u); camry_gpr[29] = camry_read32((camry_sp + 12u) & ~3u); camry_gpr[31] = camry_read32((camry_sp + 8u) & ~3u); camry_sp += 20u; camry_gpr[3] = camry_sp; } return; }
}

void dcm_cancel_retained_proprietary_operation(void)

{
  dcm_cancel_service_events(0xf1,'\0');
  reset_proprietary_dispatch_continuation_8e1e0();
  return;
}

uint dcm_proprietary_operation_service(uchar operation,F33DcmMessageContext *message)

{
  camry_write32((camry_sp - 4u) & ~3u, camry_gpr[31]);
  camry_sp -= 4u;
  camry_gpr[3] = camry_sp;

  if (operation == '\0') {
    dcm_proprietary_retained_message.request = message->request;
    dcm_proprietary_retained_message.request_length = message->request_length;
    dcm_proprietary_retained_message.response = message->response;
    dcm_proprietary_retained_message.response_length = message->response_length;
    dcm_proprietary_retained_message.addressing_kind = message->addressing_kind;
    dcm_proprietary_retained_message.suppress_positive = message->suppress_positive;
    dcm_proprietary_retained_message.response_capacity = message->response_capacity;
    dcm_proprietary_retained_message.service_id = message->service_id;
    dcm_proprietary_retained_message.service_list_selector = message->service_list_selector;
    diag_proprietary_message.request = message->request;
    diag_proprietary_message.request_length = message->request_length;
    diag_proprietary_message.response = message->response;
    diag_proprietary_message.response_length = message->response_length;
    (camry_gpr[6] = 0xfebf48ecu, camry_gpr[31] = 0x8e49eu, dcm_advance_proprietary_operation)(((F33DiagProprietaryMessage *)camry_host_ptr((uint32_t)((0xfebf48ecu)))));
  }
  else {
    (camry_gpr[31] = 0x8e4a4u, dcm_cancel_retained_proprietary_operation)();
  }
  { uint32_t camry_return_value = (0); if (camry_halted) return 0; camry_gpr[31] = camry_read32((camry_sp + 0u) & ~3u); camry_sp += 4u; camry_gpr[3] = camry_sp; return camry_return_value; }
}

void dcm_resume_queued_proprietary_operation(void)

{
  camry_write32((camry_sp - 4u) & ~3u, camry_gpr[31]);
  camry_sp -= 4u;
  camry_gpr[3] = camry_sp;

  (camry_gpr[6] = 0xfebf48ecu, camry_gpr[31] = 0x8e4b8u, dcm_advance_proprietary_operation)(((F33DiagProprietaryMessage *)camry_host_ptr((uint32_t)((0xfebf48ecu)))));
  { if (!camry_halted) { camry_gpr[31] = camry_read32((camry_sp + 0u) & ~3u); camry_sp += 4u; camry_gpr[3] = camry_sp; } return; }
}

uint find_write_did_and_check_precondition(ushort *matched_index,ushort did)

{
  ushort *puVar1;
  undefined8 uVar2;
  int iVar3;
  uint uVar4;
  uint uVar5;
  
  uVar2 = 0x23dfc00000000;
  uVar4 = 3;
  uVar5 = 0;
  do {
    while( true ) {
      iVar3 = (int)((ulonglong)uVar2 >> 0x20);
      puVar1 = ((ushort *)camry_host_ptr((uint32_t)(uVar5 * 0xc + iVar3 + 0x1844)));
      if ((did == *puVar1) && (*(int *)(puVar1 + 2) != 0)) break;
      uVar5 = uVar5 + 1 & 0xffff;
      if (0xc < uVar5) goto LAB_0008e4fe;
    }
    uVar4 = (*(int (*)())camry_indirect((uint32_t)(((((code *)(uintptr_t)((uint32_t)((uintptr_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)((short)uVar5 * 0xc + iVar3 + 0x1848))))))))))))();
  } while (uVar4 == 3);
LAB_0008e4fe:
  *matched_index = (ushort)uVar5;
  return uVar4;
}

uint dispatch_or_poll_write_did_action
               (uchar completion_status,ushort matched_index,uchar *payload,ushort length)

{
  uint32_t puVar1;
  int iVar2;
  uint uVar3;
  
  uVar3 = (uint)completion_status;
  puVar1 = 0x23dfcu;
  iVar2 = get_byte3b25_8b7a4();
  if (iVar2 == 2) {
    if (uVar3 == 0xff) {
      uVar3 = 2;
    }
  }
  else if ((matched_index < 0xd) && ((*((int *)camry_host_ptr((uint32_t)(puVar1 + (uint)matched_index * 0xc + 0x184c)))) != 0)) {
    uVar3 = (*(int (*)())camry_indirect((uint32_t)(((((code *)(uintptr_t)((uint32_t)((uintptr_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(puVar1 + (short)matched_index * 0xc + 0x184c))))))))))))(camry_host_addr(payload),length, camry_host_addr(payload), length);
  }
  else {
    uVar3 = 4;
  }
  set_byte3b25_8b7ae(uVar3);
  return uVar3;
}

uint diag_routine_select_precondition
               (ushort *callback_index,ushort rid,uchar control_type,uchar *input,
               ushort input_length)

{
  ushort *puVar1;
  undefined8 uVar2;
  int iVar3;
  uint uVar4;
  uint uVar5;
  
  uVar2 = 0x23dfc00000000;
  uVar4 = 3;
  uVar5 = 0;
  do {
    while( true ) {
      iVar3 = (int)((ulonglong)uVar2 >> 0x20);
      puVar1 = ((ushort *)camry_host_ptr((uint32_t)(uVar5 * 0xc + iVar3 + 0x18e0)));
      if ((rid == *puVar1) && (*(int *)(puVar1 + 2) != 0)) break;
      uVar5 = uVar5 + 1 & 0xffff;
      if (0x12 < uVar5) goto LAB_0008e5b4;
    }
    uVar4 = (*(int (*)())camry_indirect((uint32_t)(((((code *)(uintptr_t)((uint32_t)((uintptr_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)((short)uVar5 * 0xc + iVar3 + 0x18e4))))))))))))(control_type,camry_host_addr(input),input_length);
  } while (uVar4 == 3);
LAB_0008e5b4:
  *callback_index = (ushort)uVar5;
  return uVar4;
}

uint diag_routine_dispatch_action
               (ushort callback_index,uchar control_type,uchar *input,ushort input_length,
               uchar *output,ushort *output_length)

{
  uint uVar1;
  
  uVar1 = 3;
  if ((callback_index < 0x13) && ((*((volatile uint32_t *)camry_host_ptr((uint32_t)((uint32_t)(0x256dcu + (uint32_t)(callback_index) * (uint32_t)sizeof(F33RoutineCallbacks)) + (uint32_t)(0) * (uint32_t)sizeof(F33RoutineCallbacks) + (uint32_t)offsetof(F33RoutineCallbacks, action))))) != 0x0u))
  {
    uVar1 = (*(int (*)())camry_indirect((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)((uint32_t)(0x256dcu + (uint32_t)((short)callback_index) * (uint32_t)sizeof(F33RoutineCallbacks)) + (uint32_t)(0) * (uint32_t)sizeof(F33RoutineCallbacks) + (uint32_t)offsetof(F33RoutineCallbacks, action))))))))(control_type,camry_host_addr(input),input_length,camry_host_addr(output),camry_host_addr(output_length));
  }
  return uVar1;
}

uint merge_two_diagnostic_statuses
               (uchar application_status,uchar lower_status,uchar success_status,
               uchar pending_status)

{
  uint uVar1;
  uint uVar2;
  uint uVar3;
  
  uVar1 = (uint)application_status;
  uVar2 = (uint)lower_status;
  uVar3 = (uint)pending_status;
  if ((((uVar2 != uVar3) && (uVar1 != uVar3)) && (uVar3 = uVar1, uVar1 == success_status)) &&
     (uVar2 != success_status)) {
    uVar3 = uVar2;
  }
  return uVar3;
}

uint diag_routine_local_dispatch_enabled(void)

{
  return 0x5a;
}

void run_init_chain_8e62a(void)

{
  clear_state3800_and_768_byte_buffer_8b070();
  reset_application_programming_admission_state_8b134();
  fill_constant_block_8bfea();
  reset_dtc_count_state_and_scratch_8c318();
  reset_dtc_list_continuation_and_scratch_8c70c();
  fill_constant_block_8cb8c();
  fill_constant_block_8cef0();
  reset_state3b26_to3b29_8b3d4();
  reset_memory_read_status4598_8d4ae();
  app_security_reset_challenge_material();
  reset_communication_local_state_8d9ca();
  reset_write_did_transaction();
  diag_reset_routine_class_state();
  fill_constant_block_8db22();
  fill_constant_block_8de1a();
  reset_proprietary_dispatch_continuation_8e1e0();
  return;
}

undefined4 snapshot_seven_word_context_and_call_4d4c2_8e672(undefined1 param_1,undefined4 *param_2)

{
  undefined4 *puVar1;
  undefined4 uVar2;
  undefined4 *puVar3;
  
  puVar3 = ((undefined *)camry_host_ptr(0xfebe52bcu));
  puVar1 = param_2;
  do {
    uVar2 = *puVar1;
    puVar1 = puVar1 + 1;
    *puVar3 = uVar2;
    puVar3 = puVar3 + 1;
  } while (camry_host_addr(param_2 + 7)!=camry_host_addr(puVar1));
  DAT_febe52ac = *param_2;
  DAT_febe52b0 = param_2[1];
  DAT_febe52b4 = param_2[2];
  DAT_febe52b8 = param_2[3];
  ((void)(param_1), (void)(((undefined *)camry_host_ptr(0xfebe52acu))), return_only_stub_4d4c2());
  return 0;
}

void dcm_complete_proprietary_message(F33DiagProprietaryMessage *message)

{
  DAT_febe52c8 = message->response_length;
  dcm_complete_service_response((F33DcmMessageContext *)((undefined *)camry_host_ptr(0xfebe52bcu)));
  return;
}

void dcm_reject_proprietary_message(F33DiagProprietaryMessage *ignored_message,uchar nrc)

{
  dcm_stage_negative_response((F33DcmMessageContext *)((undefined *)camry_host_ptr(0xfebe52bcu)),nrc);
  dcm_complete_service_response((F33DcmMessageContext *)((undefined *)camry_host_ptr(0xfebe52bcu)));
  return;
}

uint diagnostic_status_to_nrc(uchar status,uchar *nrc)

{
  uchar uVar1;
  
  switch(status) {
  case '\0':
    *nrc = '\0';
    return 0;
  default:
    uVar1 = '\x10';
    break;
  case '\x02':
    uVar1 = 'x';
    break;
  case '\x03':
  case '\x04':
    uVar1 = '1';
    break;
  case '\x05':
    uVar1 = '\"';
    break;
  case '\x06':
    uVar1 = '\x14';
    break;
  case '\a':
    uVar1 = '\x12';
    break;
  case '\b':
    uVar1 = '$';
    break;
  case '\t':
    uVar1 = 'r';
    break;
  case '\v':
    uVar1 = 0x88;
  }
  *nrc = uVar1;
  return 1;
}

void reset_four_96_byte_tracking_arrays_8e74e(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  
  iVar3 = 0;
  do {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe5338u + (uint32_t)(iVar3) * 1u)))) = 0;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe5398u + (uint32_t)(iVar3) * 1u)))) = 0;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe52d8u + (uint32_t)(iVar3) * 1u)))) = 0x5a;
    iVar2 = iVar3 + 1;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe53f8u + (uint32_t)(iVar3) * 1u)))) = 0x5a;
    iVar1 = iVar3 + -0x5f;
    iVar3 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  return;
}

void clear_tracking_flag_and_increment_counter_8e772(uint param_1)

{
  param_1 = param_1 & 0xffff;
  if (param_1 < 0x60) {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe52d8u + (uint32_t)(param_1) * 1u)))) = 0;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe5338u + (uint32_t)(param_1) * 1u)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe5338u + (uint32_t)(param_1) * 1u)))) + '\x01';
  }
  return;
}

void set_tracking_flag_to_5a_8e790(uint param_1)

{
  if ((param_1 & 0xffff) < 0x60) {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe52d8u + (uint32_t)(param_1 & 0xffff) * 1u)))) = 0x5a;
  }
  return;
}

void increment_tracking_counter5338_8e7a4(uint param_1)

{
  if ((param_1 & 0xffff) < 0x60) {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe5338u + (uint32_t)(param_1 & 0xffff) * 1u)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe5338u + (uint32_t)(param_1 & 0xffff) * 1u)))) + '\x01';
  }
  return;
}

void increment_tracking_counter5398_8e7ba(uint param_1)

{
  if ((param_1 & 0xffff) < 0x60) {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe5398u + (uint32_t)(param_1 & 0xffff) * 1u)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe5398u + (uint32_t)(param_1 & 0xffff) * 1u)))) + '\x01';
  }
  return;
}

void set_tracking_result_byte53f8_8e7d0(uint param_1,undefined1 param_2)

{
  if ((param_1 & 0xffff) < 0x60) {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe53f8u + (uint32_t)(param_1 & 0xffff) * 1u)))) = param_2;
  }
  return;
}

void return_only_stub_8e7e0(void)

{
  return;
}

void clear_two_queue_storage_regions_8e7e2(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  ((volatile uint16_t *)camry_host_ptr(0xfebe5460u))[0] = 0;
  (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe5460u + (uint32_t)(1) * 2u)))) = 0;
  memzero(((void *)camry_host_ptr((uint32_t)((0xfebe5458u)))), 8);
  memzero(((undefined *)camry_host_ptr((uint32_t)(puVar1 + -0x637c))), 0x24);
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x639c)))) = 0;
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x639a)))) = 0;
  memzero(((undefined *)camry_host_ptr((uint32_t)(puVar1 + -0x6396))), 0x18);
  memzero(((undefined *)camry_host_ptr((uint32_t)(puVar1 + -0x6358))), 0x4c);
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6398))))) = 0;
  return;
}

void initialize_empty_queue_heads_and_ready_marker_8e82c(void)

{
  uint uVar1;
  uint32_t puVar2;
  puVar2 = 0xfebeb800u;
  clear_two_queue_storage_regions_8e7e2();
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar2 + -0x63a0)))) = 0xffff;
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar2 + -0x63a6)))) = 0xffff;
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar2 + -0x639c)))) = 0xffff;
  uVar1 = 0;
  do {
    (*((undefined2 *)camry_host_ptr((uint32_t)(puVar2 + uVar1 * 8 + -0x6394)))) = 0xffff;
    uVar1 = uVar1 + 1;
  } while (uVar1 < 3);
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x6398))))) = 0x5a;
  return;
}

bool select_one_slot_or_three_slot_queue_layout_8e862(ushort param_1,undefined4 *param_2)

{
  if (param_1 == 0) {
    *(undefined2 *)(param_2 + 3) = 1;
    *param_2 = (0xfebe5458u);
    param_2[1] = camry_host_addr(secoc_tx_queue_head_pair);
    param_2[2] = camry_host_addr(secoc_tx_application_snapshot);
  }
  if (param_1 == 1) {
    *param_2 = ((uint32_t)(0xfebe546au));
    param_2[1] = ((uint32_t)(0xfebe5464u));
    param_2[2] = ((uint32_t)(0xfebe54acu));
    *(undefined2 *)(param_2 + 3) = 3;
  }
  return 1 < param_1;
}

undefined4 get_queue_slot_by_link_position_8e8a0(undefined2 param_1,ushort param_2,ushort *param_3)

{
  uint8_t stack_record_20[32];
  ushort uVar1;
  ushort uVar2;
  uint32_t puVar3;
  int extraout_r8;
  int iVar4;
  undefined4 uVar5;
  uint uVar6;
  ushort *puStack_1c;
  
  puVar3 = 0xfebeb800u;
  uVar5 = 1;
  iVar4 = select_one_slot_or_three_slot_queue_layout_8e862(param_1,stack_record_20);
  if ((((iVar4 == 0) && (((int)(param_3)) != 0)) && (param_2 < (*((uint16_t *)(stack_record_20 + 12))))) && ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6398))))) == 'Z')) {
    thunk_push_priority_mask_and_raise_to_ff00_6a45e();
    uVar2 = 0;
    uVar1 = *puStack_1c;
    while ((uVar6 = (uint)uVar1, uVar2 < param_2 && (uVar6 < (*((uint16_t *)(stack_record_20 + 12)))))) {
      uVar2 = uVar2 + 1;
      uVar1 = (*((ushort *)camry_host_ptr((uint32_t)(uVar6 * 8 + (*((int32_t *)(stack_record_20 + 0))) + 2))));
    }
    if ((uVar2 == param_2) && (uVar6 < (*((uint16_t *)(stack_record_20 + 12))))) {
      *param_3 = uVar1;
      uVar5 = 0;
    }
    thunk_pop_and_restore_priority_mask_stack_6a4c4();
  }
  return uVar5;
}

undefined2 lookup_queue_slot_capacity_and_offset_8e912(short param_1,ushort param_2,undefined4 *param_3,undefined4 *param_4)

{
  undefined2 uVar1;
  
  uVar1 = 1;
  if ((param_1 == 0) && (param_2 == 0)) {
    *param_3 = DAT_00025954;
    *param_4 = DAT_00025958;
    uVar1 = 0;
  }
  if ((param_1 == 1) && (param_2 < 3)) {
    uVar1 = 0;
    *param_3 = *(undefined4 *)(((undefined *)camry_host_ptr((uint32_t)(0x2586cu + (uint32_t)((short)param_2 * 0x50) * 1u))));
    *param_4 = *(undefined4 *)(((undefined *)camry_host_ptr((uint32_t)(0x25870u + (uint32_t)((short)param_2 * 0x50) * 1u))));
  }
  return uVar1;
}

undefined2 get_queue_head_with_complement_check_8e954(short param_1,ushort *param_2)

{
  undefined2 uVar1;
  
  uVar1 = 1;
  if (param_1 == 0) {
    if (((volatile uint16_t *)camry_host_ptr(0xfebe5460u))[0] == (ushort)~(*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe5460u + (uint32_t)(1) * 2u))))) {
      *param_2 = ((volatile uint16_t *)camry_host_ptr(0xfebe5460u))[0];
      uVar1 = 0;
    }
    else {
      DAT_febe5468 = 0xa5;
    }
  }
  if (param_1 == 1) {
    if (DAT_febe5464 == (ushort)~DAT_febe5466) {
      *param_2 = DAT_febe5464;
      return 0;
    }
    DAT_febe5468 = 0xa5;
  }
  return uVar1;
}

bool set_queue_head_and_complement_8e9a0(ushort param_1,ushort param_2)

{
  if (param_1 == 0) {
    (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe5460u + (uint32_t)(1) * 2u)))) = ~param_2;
    ((volatile uint16_t *)camry_host_ptr(0xfebe5460u))[0] = param_2;
  }
  if (param_1 == 1) {
    DAT_febe5466 = ~param_2;
    DAT_febe5464 = param_2;
  }
  return 1 < param_1;
}

undefined4 copy_payload_and_append_queue_slot_8e9c6(undefined2 param_1,ushort param_2,undefined4 *param_3)

{
  uint8_t stack_record_34[52];
  undefined2 *puVar1;
  ushort uVar2;
  uint32_t puVar3;
  int iVar4;
  int iVar5;
  undefined4 uVar6;
  uint uVar7;
  uint uVar8;
  puVar3 = 0xfebeb800u;
  uVar7 = (uint)param_2;
  uVar6 = 1;
  iVar4 = select_one_slot_or_three_slot_queue_layout_8e862(param_1,((int *)(stack_record_34 + 12)));
  iVar5 = lookup_queue_slot_capacity_and_offset_8e912(param_1,uVar7,(stack_record_34 + 4),stack_record_34);
  if ((((iVar4 == 0) && (iVar5 == 0)) && (camry_host_addr((param_3))!= 0)) &&
     (*(ushort *)(param_3 + 1) <= (*((uint32_t *)(stack_record_34 + 4))))) {
    memcpy_forward(((void *)camry_host_ptr((uint32_t)((*((int32_t *)(stack_record_34 + 0))) + (*((int32_t *)(stack_record_34 + 20)))))),((void *)camry_host_ptr((uint32_t)(*param_3))),
                       (uint)*(ushort *)(param_3 + 1));
    puVar1 = ((undefined2 *)camry_host_ptr((uint32_t)(((int *)(stack_record_34 + 12))[0] + uVar7 * 8)));
    *puVar1 = *(undefined2 *)(param_3 + 1);
    puVar1[1] = 0xffff;
    puVar1[2] = 0;
    thunk_push_priority_mask_and_raise_to_ff00_6a45e();
    iVar4 = get_queue_head_with_complement_check_8e954(param_1,(stack_record_34 + 10));
    if (iVar4 == 0) {
      uVar8 = (uint)(*((uint16_t *)(stack_record_34 + 10)));
      if (uVar8 == 0xffff) {
        uVar6 = set_queue_head_and_complement_8e9a0(param_1,uVar7);
      }
      else {
        uVar2 = (*((uint16_t *)(stack_record_34 + 10)));
        if (uVar8 < (*((uint16_t *)(stack_record_34 + 24)))) {
          do {
            (*((uint16_t *)(stack_record_34 + 10))) = uVar2;
            iVar4 = uVar8 * 8 + ((int *)(stack_record_34 + 12))[0];
            uVar8 = (uint)(*((ushort *)camry_host_ptr((uint32_t)(iVar4 + 2))));
            if (uVar8 != (ushort)~(*((ushort *)camry_host_ptr((uint32_t)(iVar4 + 4))))) {
              (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6398))))) = 0xa5;
              goto LAB_0008ea96;
            }
            uVar2 = (*((ushort *)camry_host_ptr((uint32_t)(iVar4 + 2))));
          } while (uVar8 < (*((uint16_t *)(stack_record_34 + 24))));
          (*((ushort *)camry_host_ptr((uint32_t)(iVar4 + 2)))) = param_2;
          (*((ushort *)camry_host_ptr((uint32_t)(iVar4 + 4)))) = ~param_2;
          uVar6 = 0;
        }
        else {
          (*((undefined2 *)camry_host_ptr((uint32_t)(((int *)(stack_record_34 + 12))[0] + uVar7 * 8)))) = 0;
        }
      }
    }
LAB_0008ea96:
    thunk_pop_and_restore_priority_mask_stack_6a4c4();
  }
  return uVar6;
}

undefined4 copy_payload_at_slot_offset_and_return_view_8eaa0(undefined2 param_1,uint param_2,uint param_3,int *param_4)

{
  uint8_t stack_record_34[52];
  uint uVar1;
  int iVar2;
  int iVar3;
  undefined4 uVar4;
  undefined2 uVar5;
  int aiStack_2c [2];
  
  uVar4 = 1;
  iVar2 = select_one_slot_or_three_slot_queue_layout_8e862(param_1,aiStack_2c);
  iVar3 = lookup_queue_slot_capacity_and_offset_8e912(param_1,param_2 & 0xffff,(stack_record_34 + 4),stack_record_34);
  if (((iVar2 == 0) && (iVar3 == 0)) && (camry_host_addr((param_4))!= 0)) {
    uVar1 = (uint)*(ushort *)(param_4 + 1) + (param_3 & 0xffff);
    if (uVar1 <= (*((uint32_t *)(stack_record_34 + 4)))) {
      memcpy_forward(((void *)camry_host_ptr((uint32_t)((*((int32_t *)(stack_record_34 + 0))) + (param_3 & 0xffff) + (*((int32_t *)(stack_record_34 + 16)))))),((void *)camry_host_ptr((uint32_t)(*param_4))),
                         (uint)*(ushort *)(param_4 + 1));
      uVar5 = (undefined2)uVar1;
      (*((undefined2 *)camry_host_ptr((uint32_t)((param_2 & 0xffff) * 8 + aiStack_2c[0])))) = uVar5;
      *(undefined2 *)(param_4 + 1) = uVar5;
      *param_4 = (*((int32_t *)(stack_record_34 + 0))) + (*((int32_t *)(stack_record_34 + 16)));
      uVar4 = 0;
    }
  }
  return uVar4;
}

undefined4 get_queue_slot_payload_view_clamped_8eb1c(undefined2 param_1,uint param_2,int *param_3)

{
  uint8_t stack_record_30[48];
  ushort uVar1;
  int iVar2;
  int iVar3;
  undefined4 uVar4;
  
  uVar4 = 1;
  iVar2 = select_one_slot_or_three_slot_queue_layout_8e862(param_1,((int32_t *)((stack_record_30 + 8))));
  iVar3 = lookup_queue_slot_capacity_and_offset_8e912(param_1,param_2 & 0xffff,((uint32_t *)((stack_record_30 + 4))),((int32_t *)(stack_record_30)));
  if (((iVar2 == 0) && (iVar3 == 0)) && (camry_host_addr((param_3))!= 0)) {
    *param_3 = (*((int32_t *)(stack_record_30 + 0))) + (*((int32_t *)(stack_record_30 + 16)));
    uVar1 = (*((ushort *)camry_host_ptr((uint32_t)((param_2 & 0xffff) * 8 + ((int32_t *)((stack_record_30 + 8)))[0]))));
    if ((*((uint32_t *)(stack_record_30 + 4))) < uVar1) {
      uVar1 = (ushort)(*((uint32_t *)(stack_record_30 + 4)));
    }
    *(ushort *)(param_3 + 1) = uVar1;
    uVar4 = 0;
  }
  return uVar4;
}

undefined4 unlink_queue_slot_and_clear_payload_8eb7e(undefined2 param_1,uint param_2)

{
  uint8_t stack_record_30[48];
  undefined2 *puVar1;
  uint uVar2;
  uint uVar3;
  uint32_t puVar4;
  ushort uVar5;
  int iVar6;
  int iVar7;
  uint uVar8;
  int aiStack_24 [2];
  
  puVar4 = 0xfebeb800u;
  param_2 = param_2 & 0xffff;
  (*((int32_t *)(stack_record_30 + 0))) = 0;
  (*((uint32_t *)(stack_record_30 + 4))) = 0;
  iVar6 = select_one_slot_or_three_slot_queue_layout_8e862(param_1,aiStack_24);
  iVar7 = lookup_queue_slot_capacity_and_offset_8e912(param_1,param_2,(stack_record_30 + 4),stack_record_30);
  if (iVar6 != 0) {
    return 1;
  }
  if (iVar7 != 0) {
    return 1;
  }
  thunk_push_priority_mask_and_raise_to_ff00_6a45e();
  iVar6 = get_queue_head_with_complement_check_8e954(param_1,(stack_record_30 + 10));
  if (iVar6 == 0) {
    uVar2 = (uint)(*((uint16_t *)(stack_record_30 + 10)));
    if (uVar2 == param_2) {
      iVar6 = uVar2 * 8 + aiStack_24[0];
      uVar5 = (*((ushort *)camry_host_ptr((uint32_t)(iVar6 + 2))));
      if (uVar5 != (ushort)~(*((ushort *)camry_host_ptr((uint32_t)(iVar6 + 4))))) {
LAB_0008ec26:
        (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x6398))))) = 0xa5;
        goto LAB_0008ec3a;
      }
    }
    else {
      uVar8 = uVar2;
      uVar5 = (*((uint16_t *)(stack_record_30 + 10)));
      if (uVar2 < (*((uint16_t *)(stack_record_30 + 24)))) {
        do {
          (*((uint16_t *)(stack_record_30 + 10))) = uVar5;
          uVar3 = uVar2;
          iVar6 = uVar3 * 8 + aiStack_24[0];
          uVar5 = (*((ushort *)camry_host_ptr((uint32_t)(iVar6 + 2))));
          uVar2 = (uint)uVar5;
          if (uVar2 != (ushort)~(*((ushort *)camry_host_ptr((uint32_t)(iVar6 + 4))))) goto LAB_0008ec26;
          if (uVar3 == param_2) {
            iVar6 = uVar8 * 8 + aiStack_24[0];
            (*((ushort *)camry_host_ptr((uint32_t)(iVar6 + 2)))) = uVar5;
            (*((ushort *)camry_host_ptr((uint32_t)(iVar6 + 4)))) = ~uVar5;
            break;
          }
          uVar8 = uVar3;
        } while (uVar2 < (*((uint16_t *)(stack_record_30 + 24))));
        goto LAB_0008ec3a;
      }
      uVar5 = 0xffff;
    }
    set_queue_head_and_complement_8e9a0(param_1,uVar5);
  }
LAB_0008ec3a:
  thunk_pop_and_restore_priority_mask_stack_6a4c4();
  memzero(((void *)camry_host_ptr((uint32_t)((*((int32_t *)(stack_record_30 + 0))) + (*((int32_t *)(stack_record_30 + 20)))))),(*((uint32_t *)(stack_record_30 + 4))));
  puVar1 = ((undefined2 *)camry_host_ptr((uint32_t)(param_2 * 8 + aiStack_24[0])));
  *puVar1 = 0;
  puVar1[1] = 0xffff;
  puVar1[2] = 0;
  return 0;
}

undefined4 check_u16_complement_pairs_and_valid_marker_8ec66(void)

{
  uint32_t puVar1;
  undefined4 uVar2;
  
  puVar1 = 0xfebeb800u;
  thunk_push_priority_mask_and_raise_to_ff00_6a45e();
  if ((*((ushort *)camry_host_ptr((uint32_t)(puVar1 + -0x63a0)))) != (ushort)~(*((ushort *)camry_host_ptr((uint32_t)(puVar1 + -0x639e))))) {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6398))))) = 0xa5;
  }
  if ((*((ushort *)camry_host_ptr((uint32_t)(puVar1 + -0x639c)))) != (ushort)~(*((ushort *)camry_host_ptr((uint32_t)(puVar1 + -0x639a))))) {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6398))))) = 0xa5;
  }
  thunk_pop_and_restore_priority_mask_stack_6a4c4();
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6398))))) == 'Z') {
    uVar2 = 0;
  }
  else {
    uVar2 = 2;
  }
  return uVar2;
}

void serialize_be16_header_and_two_buffers_8ecb2(undefined4 *param_1,undefined1 *param_2,uint *param_3)

{
  int iVar1;
  
  if ((((camry_host_addr((param_1))!= 0) && (camry_host_addr((param_2))!= 0)) &&
      (camry_host_addr((param_3))!= 0)) &&
     ((uint)*(ushort *)(param_1 + 3) + (uint)(*((ushort *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 10)))) + 2 <= *param_3)) {
    *param_2 = (char)((ushort)*(undefined2 *)(param_1 + 2) >> 8);
    param_2[1] = *(undefined1 *)(param_1 + 2);
    memcpy_forward(param_2 + 2,((void *)camry_host_ptr((uint32_t)(*param_1))),(uint)(*((ushort *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 10)))));
    iVar1 = (*((ushort *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 10)))) + 2;
    memcpy_forward(param_2 + iVar1,((void *)camry_host_ptr((uint32_t)(param_1[1]))),(uint)*(ushort *)(param_1 + 3));
    *param_3 = (uint)*(ushort *)(param_1 + 3) + iVar1;
  }
  return;
}

void initialize_secoc_context_and_publish_ready_8ed14(void)

{
  uint32_t puVar1;
  uint32_t puVar2;
  puVar1 = 0xfebeb800u;
  puVar2 = 0x23dfcu;
  DAT_febe54f4 = 0;
  DAT_febe54f6 = 0xfe01;
  DAT_febe54f8 = 0;
  return_only_stub_8e7e0();
  initialize_secoc_transmit_context_8fa20();
  initialize_three_secoc_receive_slots_8f26c();
  initialize_empty_queue_heads_and_ready_marker_8e82c();
  initialize_secoc_key_descriptor_and_mirrors_8f11a();
  store_secoc_key_descriptor_with_byte_complements_8f148(0, ((undefined *)camry_host_ptr((uint32_t)(puVar2 + 0x1a2c))));
  initialize_freshness_check_counters_and_state_90212();
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x630c)))) = 0xfe01;
  return;
}

void deinitialize_ready_secoc_context_8ed56(void)

{
  if (((int16_t)DAT_febe54f4) == -0x1ff) {
    DAT_febe54f4 = 0;
    DAT_febe54f6 = 0xfe01;
    DAT_febe54f8 = 0;
    initialize_secoc_transmit_context_8fa20();
    initialize_three_secoc_receive_slots_8f26c();
    clear_two_queue_storage_regions_8e7e2();
    initialize_secoc_key_descriptor_and_mirrors_8f11a();
    initialize_freshness_check_counters_and_state_90212();
  }
  return;
}

uint secoc_transmit(ushort source_pdu,F33PduInfo *info)

{
  uint32_t puVar1;
  uint uVar2;
  int iVar3;
  ushort uStack_a;
  
  puVar1 = 0x23dfcu;
  uVar2 = 1;
  uStack_a = 0;
  if (((((int16_t)DAT_febe54f4) == -0x1ff) && (camry_host_addr((info))!= 0)) && (((uint32_t)(info->data))!=camry_host_addr((((uchar *)0x0))))) {
    iVar3 = find_single_secoc_transmit_slot_by_pdu_id_8fa5a(source_pdu,0,&uStack_a);
    if (((iVar3 == 0) && ((uint)info->length <= (*((uint *)camry_host_ptr((uint32_t)(puVar1 + 7000)))))) &&
       ((uint)(*((ushort *)camry_host_ptr((uint32_t)(puVar1 + 0x1b42)))) <= (uint)info->length)) {
      uVar2 = claim_secoc_tx_snapshot(uStack_a,info);
    }
    else {
      uVar2 = 1;
    }
  }
  return uVar2;
}

int cancel_configured_secoc_transmit_8ede6(undefined2 param_1)

{
  int iVar1;
  undefined2 uStack_6;
  
  iVar1 = 1;
  uStack_6 = 0;
  if ((((int16_t)DAT_febe54f4) == -0x1ff) && (iVar1 = find_single_secoc_transmit_slot_by_pdu_id_8fa5a(param_1,0,&uStack_6), iVar1 == 0)) {
    iVar1 = cancel_secoc_transmit_state_and_release_buffer_8fb52(uStack_6);
  }
  return iVar1;
}

uint set_secoc_key_or_crypto_qualification_8ee16(char param_1,int param_2)

{
  uint uVar1;
  
  uVar1 = 1;
  if ((((int16_t)DAT_febe54f4) == -0x1ff) && (param_2 != 0)) {
    if (param_1 == -1) {
      uVar1 = secoc_publish_crypto_qualification((*((uchar *)camry_host_ptr((uint32_t)(param_2 + 4)))));
    }
    else {
      uVar1 = store_secoc_key_descriptor_with_byte_complements_8f148((uint)(byte)param_1, ((int *)camry_host_ptr((uint32_t)(param_2))));
    }
  }
  return uVar1;
}

undefined4 get_configured_freshness_when_ready_8ee44(undefined2 param_1, undefined4 param_2, undefined4 param_3)

{
  undefined4 uVar1;
  
  if (((int16_t)DAT_febe54f4) == -0x1ff) {
    uVar1 = dispatch_freshness_export_by_configured_id_902e4(param_1, param_2, param_3);
  }
  else {
    uVar1 = 1;
  }
  return uVar1;
}

undefined4 set_configured_freshness_when_ready_8ee60(undefined2 param_1, undefined4 param_2, undefined4 param_3)

{
  undefined4 uVar1;
  
  if (((int16_t)DAT_febe54f4) == -0x1ff) {
    uVar1 = dispatch_freshness_import_by_configured_id_90342(param_1, param_2, param_3);
  }
  else {
    uVar1 = 1;
  }
  return uVar1;
}

void queue_configured_secoc_receive_payload_8ee7c(undefined2 param_1,int *param_2)

{
  int iVar1;
  undefined2 uStack_a;
  
  uStack_a = 0;
  if ((((((int16_t)DAT_febe54f4) == -0x1ff) && (camry_host_addr((param_2))!= 0)) && (*param_2 != 0)) &&
     (iVar1 = find_secoc_receive_slot_by_pdu_id_8f2b0(param_1,0,&uStack_a), iVar1 == 0)) {
    queue_or_update_secoc_receive_buffer_8f34a(uStack_a,param_2);
  }
  return;
}

void confirm_configured_secoc_transmit_8eeba(undefined2 param_1)

{
  int iVar1;
  undefined2 uStack_6;
  
  uStack_6 = 0;
  if ((((int16_t)DAT_febe54f4) == -0x1ff) && (iVar1 = find_single_secoc_transmit_slot_by_pdu_id_8fa5a(param_1,1,&uStack_6), iVar1 == 0)) {
    confirm_secoc_transmit_and_notify_upper_8fc00(uStack_6);
  }
  return;
}

short read_crypto_status_and_bound_to_two_8eee8(void)

{
  short sStack_6;
  
  sStack_6 = 0;
  write_zero_u16_if_nonnull_89d08(&sStack_6);
  if ((sStack_6 != 0) && (sStack_6 != 1)) {
    sStack_6 = 2;
  }
  return sStack_6;
}

undefined4 classify_secoc_ready_and_cycle_markers_8ef0c(void)

{
  undefined4 uVar1;
  
  if (((int16_t)DAT_febe54f4) == -0x1ff) {
    uVar1 = 0;
    if (((int16_t)DAT_febe54f6) != -0x1ff) {
      if (((int16_t)DAT_febe54f6) == -0x2fe) {
        uVar1 = 0;
      }
      else {
        uVar1 = 2;
      }
    }
    return uVar1;
  }
  if (DAT_febe54f4 == 0) {
    uVar1 = 1;
  }
  else {
    uVar1 = 2;
  }
  return uVar1;
}

uint32_t check_secoc_integrity_then_freshness_8ef3a(void)

{
  uint32_t camry_r10_result;
  int iVar1;
  
  iVar1 = (camry_r10_result = read_crypto_status_and_bound_to_two_8eee8());
  if ((((iVar1 == 0) && (iVar1 = (camry_r10_result = classify_secoc_ready_and_cycle_markers_8ef0c()), iVar1 == 0)) &&
      (iVar1 = (camry_r10_result = check_rotating_secoc_receive_state_8f9c6()), iVar1 == 0)) &&
     (((iVar1 = (camry_r10_result = validate_secoc_transmit_state_and_lock_90146()), iVar1 == 0 && (iVar1 = (camry_r10_result = validate_secoc_key_byte_complements_8f210()), iVar1 == 0)) &&
      (iVar1 = (camry_r10_result = check_u16_complement_pairs_and_valid_marker_8ec66()), iVar1 == 0)))) {
    (camry_r10_result = run_freshness_check_and_latch_cycle_error_904c0());
  }
  return camry_r10_result;
}

void thunk_increment_secoc_receive_age_to_configured_limit_8f3ca(void)

{
  increment_secoc_receive_age_to_configured_limit_8f3ca();
  return;
}

undefined4 process_secoc_receive_with_reserved_transmit_quota_8ef84(void)

{
  uint32_t puVar1;
  uint32_t puVar2;
  int iVar3;
  int iVar4;
  
  puVar1 = 0xfebeb800u;
  puVar2 = 0x23dfcu;
  while( true ) {
    iVar3 = get_bounded_secoc_pending_transmit_count_8fc58();
    iVar3 = (uint)(*((ushort *)camry_host_ptr((uint32_t)(puVar2 + 0x1a28)))) - iVar3;
    iVar4 = (uint)(*((ushort *)camry_host_ptr((uint32_t)(puVar1 + -0x6308)))) - iVar3;
    if (iVar4 < 0 == (iVar3 < 0 && iVar3 < 0 == iVar4 < 0)) {
      return 0;
    }
    (*((ushort *)camry_host_ptr((uint32_t)(puVar1 + -0x6308)))) = (*((ushort *)camry_host_ptr((uint32_t)(puVar1 + -0x6308)))) + 1;
    iVar4 = process_next_secoc_receive_slot_8f98c();
    if (iVar4 == 0x300) {
      (*((short *)camry_host_ptr((uint32_t)(puVar1 + -0x6308)))) = (*((short *)camry_host_ptr((uint32_t)(puVar1 + -0x6308)))) + -1;
    }
    if (iVar4 == 0x202) break;
    if (iVar4 == 0x300) {
      return 0;
    }
  }
  return 0;
}

undefined4 process_secoc_transmit_with_cycle_budget_8efc6(void)

{
  uint32_t puVar1;
  uint32_t puVar2;
  int iVar3;
  
  puVar1 = 0xfebeb800u;
  puVar2 = 0x23dfcu;
  do {
    if ((*((ushort *)camry_host_ptr((uint32_t)(puVar2 + 0x1a28)))) <= (*((ushort *)camry_host_ptr((uint32_t)(puVar1 + -0x6308))))) {
      return 0;
    }
    (*((ushort *)camry_host_ptr((uint32_t)(puVar1 + -0x6308)))) = (*((ushort *)camry_host_ptr((uint32_t)(puVar1 + -0x6308)))) + 1;
    iVar3 = process_next_eligible_secoc_transmit_900ea();
    if (iVar3 == 0x202) {
      return 0;
    }
    if (iVar3 == 0x203) {
      return 0;
    }
  } while (iVar3 != 0x300);
  return 0;
}

uint32_t run_secoc_integrity_and_bounded_work_cycle_8eff8(void)

{
  uint32_t camry_r10_result;
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  (camry_r10_result = check_secoc_integrity_then_freshness_8ef3a());
  if ((*((short *)camry_host_ptr((uint32_t)(puVar1 + -0x630c)))) == -0x1ff) {
    if ((*((short *)camry_host_ptr((uint32_t)(puVar1 + -0x630a)))) == -0x1ff) {
      (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x6308)))) = 0;
      (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x630a)))) = 0xfd02;
      thunk_increment_secoc_receive_age_to_configured_limit_8f3ca();
      (camry_r10_result = process_secoc_receive_with_reserved_transmit_quota_8ef84());
      (camry_r10_result = process_secoc_transmit_with_cycle_budget_8efc6());
      (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x630a)))) = 0xfe01;
    }
    else {
      thunk_increment_secoc_receive_age_to_configured_limit_8f3ca();
    }
  }
  return camry_r10_result;
}
