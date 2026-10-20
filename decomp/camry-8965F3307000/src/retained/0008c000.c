#include "common.h"

undefined4 advance_clear_diagnostic_group_validation_8c018(F33DcmMessageContext *param_1,uint param_2)

{
  uint8_t stack_record_29[41];
  uint uVar1;
  uchar uVar2;
  uchar lower_status;
  uint uVar3;
  
  uVar2 = DAT_febf3bd1;
  stack_record_29[0] = DAT_febf3bd3;
  uVar3 = 0;
  do {
    uVar1 = uVar3 + 1;
    ((uint8_t *)((stack_record_29 + 1)))[uVar3] = 0;
    uVar3 = uVar1;
  } while (uVar1 < 8);
  if (DAT_febf3bd0 == '\0') {
    ((uint8_t *)((stack_record_29 + 1)))[0] = (undefined1)(param_2 >> 0x18);
    ((uint8_t *)((stack_record_29 + 1)))[1] = (undefined1)(param_2 >> 0x10);
    ((uint8_t *)((stack_record_29 + 1)))[2] = (undefined1)(param_2 >> 8);
    ((uint8_t *)((stack_record_29 + 1)))[3] = (undefined1)param_2;
    lower_status = ((void)(0x18000000), (void)(4), (void)(4), (void)(((uint8_t *)((stack_record_29 + 1)))), (void)(((uint8_t *)(stack_record_29))), return_const_0_8b10c());
  }
  else {
    if (DAT_febf3bd0 != '\x01') {
      return 0;
    }
    lower_status = DAT_febf3bd2;
    if (DAT_febf3bd2 == '\x04') {
      lower_status = ((void)(6), (void)(4), return_const_0_8b110());
    }
    if (uVar2 != '\x04') goto LAB_0008c0b8;
  }
  uVar3 = validate_clear_all_diagnostic_group(param_2);
  uVar2 = (uchar)uVar3;
LAB_0008c0b8:
  uVar3 = merge_two_diagnostic_statuses(uVar2,lower_status,'\0','\x04');
  if (uVar3 == 4) {
    dcm_post_service_event(0xeb);
    DAT_febf3bd0 = 1;
    DAT_febf3bd1 = uVar2;
    DAT_febf3bd2 = lower_status;
    DAT_febf3bd3 = stack_record_29[0];
    return 1;
  }
  if (uVar3 == 0) {
    DAT_febf3bd1 = 1;
    DAT_febf3bd2 = 1;
    DAT_febf3bd0 = 1;
    DAT_febf3bd3 = stack_record_29[0];
    return 0;
  }
  uVar2 = '\"';
  if (uVar3 == 1) {
    uVar2 = '1';
  }
  dcm_report_negative_or_pending(param_1,uVar2);
  DAT_febf3bd0 = 0;
  DAT_febf3bd1 = 1;
  DAT_febf3bd2 = 1;
  DAT_febf3bd3 = stack_record_29[0];
  return 1;
}

undefined4 advance_clear_diagnostic_group_execution_8c104(F33DcmMessageContext *param_1,undefined4 param_2)

{
  uint8_t stack_record_25[37];
  uint uVar1;
  uchar nrc;
  uchar lower_status;
  ushort uVar2;
  uint uVar3;
  undefined4 uVar4;
  char cVar5;
  uchar application_status;
  
  application_status = DAT_febf3bd1;
  cVar5 = DAT_febf3bd0;
  stack_record_25[0] = DAT_febf3bd3;
  uVar3 = 0;
  do {
    uVar1 = uVar3 + 1;
    ((uint8_t *)((stack_record_25 + 1)))[uVar3] = 0;
    uVar3 = uVar1;
  } while (uVar1 < 8);
  if (DAT_febf3bd0 == '\x01') {
    ((uint8_t *)((stack_record_25 + 1)))[0] = (undefined1)((uint)param_2 >> 0x18);
    ((uint8_t *)((stack_record_25 + 1)))[1] = (undefined1)((uint)param_2 >> 0x10);
    cVar5 = '\x02';
    ((uint8_t *)((stack_record_25 + 1)))[2] = (undefined1)((uint)param_2 >> 8);
    ((uint8_t *)((stack_record_25 + 1)))[3] = (undefined1)param_2;
    lower_status = ((void)(0x18000001), (void)(4), (void)(4), (void)(((uint8_t *)((stack_record_25 + 1)))), (void)(((uint8_t *)(stack_record_25))), return_const_0_8b10c());
  }
  else {
    if (DAT_febf3bd0 != '\x02') {
      application_status = '\x06';
      lower_status = '\x06';
      goto LAB_0008c1b0;
    }
    lower_status = DAT_febf3bd2;
    if (DAT_febf3bd2 == '\x04') {
      lower_status = ((void)(6), (void)(4), return_const_0_8b110());
    }
    if (application_status != '\x04') goto LAB_0008c1b0;
  }
  uVar2 = diagnostic_clear_request_callback();
  application_status = (uchar)uVar2;
LAB_0008c1b0:
  uVar3 = merge_two_diagnostic_statuses(application_status,lower_status,'\0','\x04');
  if (uVar3 == 4) {
    uVar4 = 10;
    dcm_post_service_event(0xeb);
  }
  else {
    application_status = '\x01';
    lower_status = '\x01';
    uVar4 = 1;
    cVar5 = '\0';
    if (uVar3 == 0) {
      dcm_report_positive_response(param_1);
      uVar4 = 0;
    }
    else {
      if (uVar3 == 1) {
        nrc = '1';
      }
      else if ((uVar3 == 3) || (uVar3 == 5)) {
        nrc = '\"';
      }
      else {
        nrc = 'r';
      }
      dcm_report_negative_or_pending(param_1,nrc);
    }
  }
  DAT_febf3bd1 = application_status;
  DAT_febf3bd2 = lower_status;
  DAT_febf3bd0 = cVar5;
  DAT_febf3bd3 = stack_record_25[0];
  return uVar4;
}

uint dcm_join_clear_diagnostic_phases(uint group,F33DcmMessageContext *message)

{
  uint uVar1;
  
  uVar1 = advance_clear_diagnostic_group_validation_8c018(message,group);
  if (uVar1 == 0) {
    uVar1 = advance_clear_diagnostic_group_execution_8c104(message,group);
  }
  return uVar1;
}

uint dcm_begin_clear_diagnostic_request(F33DcmMessageContext *message)

{
  uint uVar1;
  uint group;
  byte *pbVar2;
  
  set_diagnostic_busy_marker_from_done_flag_9560e(0);
  dcm_clear_message.request = message->request;
  DAT_febf3bcc = 0;
  dcm_clear_message.request_length = message->request_length;
  dcm_clear_message.response = message->response;
  dcm_clear_message.response_length = message->response_length;
  dcm_clear_message.addressing_kind = message->addressing_kind;
  dcm_clear_message.suppress_positive = message->suppress_positive;
  dcm_clear_message.response_capacity = message->response_capacity;
  dcm_clear_message.service_id = message->service_id;
  dcm_clear_message.service_list_selector = message->service_list_selector;
  if (message->request_length == 3) {
    pbVar2 = ((void *)camry_host_ptr((uint32_t)(message->request)));
    group = (uint)pbVar2[2] | (uint)pbVar2[1] << 8 | (uint)*pbVar2 << 0x10;
    uVar1 = dcm_join_clear_diagnostic_phases(group, ((F33DcmMessageContext *)camry_host_ptr((uint32_t)((0xfebf3bd4u)))));
  }
  else {
    uVar1 = 0;
    group = 0;
    dcm_report_negative_or_pending(((F33DcmMessageContext *)camry_host_ptr((uint32_t)((0xfebf3bd4u)))), '\x13');
  }
  DAT_febf3bcc = group;
  return uVar1;
}

void cancel_clear_group_service_and_reset_8c2c4(void)

{
  fill_constant_block_8bfea();
  dcm_cancel_service_events(0xeb,'\0');
  set_diagnostic_busy_marker_from_done_flag_9560e(1);
  return;
}

uint dcm_clear_diagnostic_service(uchar operation,F33DcmMessageContext *message)

{
  uint uVar1;
  
  if (operation == '\0') {
    uVar1 = dcm_begin_clear_diagnostic_request(message);
  }
  else {
    uVar1 = 0;
    cancel_clear_group_service_and_reset_8c2c4();
  }
  return uVar1;
}

uint dcm_resume_queued_clear_request(void)

{
  return dcm_join_clear_diagnostic_phases(DAT_febf3bcc, ((F33DcmMessageContext *)camry_host_ptr((uint32_t)((0xfebf3bd4u)))));
}

void reset_dtc_count_state_and_scratch_8c318(void)

{
  uint uVar1;
  
  DAT_febf3bf8 = 0xff;
  DAT_febf3bf7 = 0;
  DAT_febf3bf2 = 0;
  DAT_febf3bf6 = 0;
  DAT_febf3bf5 = 0;
  DAT_febf3bf4 = 0;
  uVar1 = 0;
  do {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebf3c18u + (uint32_t)(uVar1) * 1u)))) = '\0';
    uVar1 = uVar1 + 1;
  } while (uVar1 < 0x300);
  DAT_febf3bf9 = 0;
  return;
}

void cancel_dtc_count_service_and_reset_8c368(void)

{
  reset_dtc_count_state_and_scratch_8c318();
  dcm_cancel_service_events(0xec,'\0');
  set_diagnostic_busy_marker_from_done_flag_9560e(1);
  return;
}

void append_dtc_count_mask_and_format_one_8c384(uchar param_1)

{
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)((uint32_t)(dcm_dtc_count_message.response) + (uint32_t)(dcm_dtc_count_message.response_length) * 1u)))) = param_1;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)((uint32_t)(dcm_dtc_count_message.response) + (uint32_t)(dcm_dtc_count_message.response_length + 1) * 1u)))) = '\x01';
  dcm_dtc_count_message.response_length = dcm_dtc_count_message.response_length + 2;
  return;
}

uint begin_dtc_count_iteration(uchar mask)

{
  uint uVar1;
  
  uVar1 = begin_filtered_dtc_iteration(mask);
  DAT_febf3bf5 = mask;
  return uVar1;
}

bool append_next_filtered_dtc_tuple_for_count_8c3c0(int param_1,ushort *param_2,undefined1 *param_3)

{
  uint8_t stack_record_15[21];
  uint uVar1;
  
  uVar1 = next_filtered_dtc(((uint32_t *)((stack_record_15 + 1))),((uint8_t *)(stack_record_15)));
  if (uVar1 == 0) {
    (*((char *)camry_host_ptr((uint32_t)((uint)*param_2 + param_1)))) = (char)((*((uint32_t *)(stack_record_15 + 1))) >> 0x10);
    (*((char *)camry_host_ptr((uint32_t)((uint)*param_2 + param_1 + 1)))) = (char)((*((uint32_t *)(stack_record_15 + 1))) >> 8);
    (*((char *)camry_host_ptr((uint32_t)((uint)*param_2 + param_1 + 2)))) = (char)(*((uint32_t *)(stack_record_15 + 1)));
    (*((uchar *)camry_host_ptr((uint32_t)((uint)*param_2 + param_1 + 3)))) = stack_record_15[0];
    *param_2 = *param_2 + 4;
  }
  *param_3 = (char)uVar1;
  return uVar1 != 0;
}

void append_dtc_count(ushort count)

{
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)((uint32_t)(dcm_dtc_count_message.response) + (uint32_t)(dcm_dtc_count_message.response_length) * 1u)))) =
       (uchar)(count >> 8);
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)((uint32_t)(dcm_dtc_count_message.response) + (uint32_t)(dcm_dtc_count_message.response_length + 1) * 1u)))) = (uchar)count;
  dcm_dtc_count_message.response_length = dcm_dtc_count_message.response_length + 2;
  return;
}

uint count_merged_dtc_sources(F33DiagSourceBuffer *local,F33DiagSourceBuffer *side)

{
  byte *pbVar1;
  uint uVar2;
  ushort count;
  uint uVar4;
  uint uVar5;
  uint uVar6;
  ushort uVar3;
  
  uVar5 = 0;
  uVar4 = 0;
  count = 0;
  if ((local->status == '\x01') || (side->status == '\x01')) {
    if (local->length == 0) {
      uVar6 = 0xffffffff;
    }
    else {
      uVar6 = 0;
    }
    if (side->length == 0) {
      uVar2 = 0xffffffff;
      count = 0;
      goto LAB_0008c4e6;
    }
    uVar2 = 0;
    uVar3 = 0;
    do {
      do {
        if (uVar6 != 0) goto LAB_0008c49a;
        while( true ) {
          while( true ) {
            if (uVar5 < local->length) {
              pbVar1 = ((void *)camry_host_ptr((uint32_t)(local->bytes + uVar5)));
              uVar6 = (uint)pbVar1[2] | (uint)pbVar1[1] << 8 | (uint)*pbVar1 << 0x10;
            }
            else {
              uVar6 = 0xffffffff;
            }
LAB_0008c49a:
            if (uVar2 == 0) {
              if (uVar4 < side->length) {
                pbVar1 = ((void *)camry_host_ptr((uint32_t)(side->bytes + uVar4)));
                uVar2 = (uint)pbVar1[2] | (uint)pbVar1[1] << 8 | (uint)*pbVar1 << 0x10;
              }
              else {
                uVar2 = 0xffffffff;
              }
            }
            if (uVar6 != uVar2) break;
            if (uVar6 == 0xffffffff) goto LAB_0008c4ea;
            count = count + 1;
            uVar5 = uVar5 + 4 & 0xffff;
            uVar2 = 0;
            uVar4 = uVar4 + 4 & 0xffff;
            uVar3 = uVar3 + 1;
          }
          count = uVar3 + 1;
          if (uVar2 <= uVar6) break;
          uVar5 = uVar5 + 4 & 0xffff;
          uVar3 = count;
        }
        uVar2 = 0;
        uVar4 = uVar4 + 4 & 0xffff;
LAB_0008c4e6:
        uVar3 = count;
      } while (uVar6 != 0xffffffff);
LAB_0008c4ea:;
    } while (uVar2 != 0xffffffff);
  }
  append_dtc_count(count);
  return 0;
}

undefined4 advance_dtc_count_sources_and_respond_8c4f8(F33DcmMessageContext *param_1)

{
  uint8_t stack_record_44[68];
  undefined4 uVar1;
  undefined2 uVar2;
  undefined1 uVar3;
  char cVar4;
  int iVar5;
  char cVar6;
  uint uVar7;
  F33DiagSourceBuffer FStack_40;
  F33DiagSourceBuffer FStack_38;
  undefined1 auStack_30 [8];
  
  cVar4 = DAT_febf3bf7;
  uVar3 = DAT_febf3bf5;
  cVar6 = DAT_febf3bf4;
  uVar2 = DAT_febf3bf0;
  iVar5 = 0;
  (*((uint16_t *)(stack_record_44 + 2))) = DAT_febf3bf2;
  uVar7 = (uint)DAT_febf3bf9;
  stack_record_44[0] = DAT_febf3bf6;
  stack_record_44[1] = DAT_febf3bf8;
  if (DAT_febf3bf4 == '\0') {
    cVar6 = '\x02';
    auStack_30[0] = DAT_febf3bf5;
    uVar7 = ((void)(0x20000100), (void)(2), (void)(1), (void)(auStack_30), (void)((stack_record_44 + 1)), return_const_0_8b10c());
    while ((stack_record_44[0] != '\x01' && (iVar5 != 1))) {
      iVar5 = append_next_filtered_dtc_tuple_for_count_8c3c0(camry_host_addr(dtc_count_local_tuple_scratch), (stack_record_44 + 2), stack_record_44);
    }
  }
  else if (DAT_febf3bf4 == '\x02') {
    if (uVar7 == 2) {
      uVar7 = ((void)(1), (void)(2), return_const_0_8b110());
    }
    while ((stack_record_44[0] != '\x01' && (iVar5 != 1))) {
      iVar5 = append_next_filtered_dtc_tuple_for_count_8c3c0(camry_host_addr(dtc_count_local_tuple_scratch), (stack_record_44 + 2), stack_record_44);
    }
  }
  else {
    stack_record_44[0] = '\x01';
    uVar7 = 1;
    (*((uint16_t *)(stack_record_44 + 2))) = 0;
    uVar2 = 0;
  }
  if ((stack_record_44[0] == '\x02') || (uVar7 == 2)) {
    dcm_post_service_event(0xec);
  }
  else {
    if (cVar4 != '\0') {
      FStack_38.bytes = camry_host_addr(dtc_count_local_tuple_scratch);
      FStack_40.status = (uchar)uVar7;
      FStack_40.bytes = 0;
      FStack_38.length = (*((uint16_t *)(stack_record_44 + 2)));
      FStack_40.length = 0;
      FStack_38.status = stack_record_44[0];
      count_merged_dtc_sources(&FStack_38,&FStack_40);
      dcm_report_positive_response(param_1);
      cVar6 = '\0';
      uVar2 = 0;
      uVar7 = 0;
      (*((uint16_t *)(stack_record_44 + 2))) = 0;
      uVar3 = 0;
      stack_record_44[0] = '\0';
      cVar4 = '\0';
      uVar1 = 0;
      goto LAB_0008c600;
    }
    dcm_post_service_event(0xec);
    cVar4 = 'Z';
  }
  uVar1 = 10;
LAB_0008c600:
  DAT_febf3bf0 = uVar2;
  DAT_febf3bf9 = (char)uVar7;
  DAT_febf3bf5 = uVar3;
  DAT_febf3bf2 = (*((uint16_t *)(stack_record_44 + 2)));
  DAT_febf3bf4 = cVar6;
  DAT_febf3bf7 = cVar4;
  DAT_febf3bf6 = stack_record_44[0];
  DAT_febf3bf8 = stack_record_44[1];
  return uVar1;
}

undefined4 start_dtc_count_response_by_status_mask_8c622(void)

{
  uchar nrc;
  uint uVar1;
  undefined4 uVar2;
  uchar auStack_11 [5];
  
  auStack_11[0] = '\0';
  set_diagnostic_busy_marker_from_done_flag_9560e(0);
  if (dcm_dtc_count_message.request_length == 1) {
    if (dcm_dtc_count_message.response_capacity == 0) {
      return 0;
    }
    uVar1 = get_dtc_status_availability_mask(auStack_11);
    if (uVar1 == 0) {
      append_dtc_count_mask_and_format_one_8c384(auStack_11[0]);
      if (*((uint8_t *)camry_host_ptr((uint32_t)(dcm_dtc_count_message.request))) == '\0') {
        append_dtc_count(0);
        dcm_report_positive_response(((F33DcmMessageContext *)camry_host_ptr((uint32_t)((0xfebf3bfcu)))));
        return 0;
      }
      uVar1 = begin_dtc_count_iteration(*((uint8_t *)camry_host_ptr((uint32_t)(dcm_dtc_count_message.request))));
      if (uVar1 == 0) {
        uVar2 = advance_dtc_count_sources_and_respond_8c4f8(((F33DcmMessageContext *)camry_host_ptr((uint32_t)((0xfebf3bfcu)))));
        return uVar2;
      }
    }
    nrc = '!';
  }
  else {
    nrc = '\x13';
  }
  dcm_report_negative_or_pending(((F33DcmMessageContext *)camry_host_ptr((uint32_t)((0xfebf3bfcu)))), nrc);
  return 0;
}

uint dcm_read_dtc_count_service(uchar operation,F33DcmMessageContext *message)

{
  uint uVar1;
  
  dcm_dtc_count_message.request = message->request;
  dcm_dtc_count_message.request_length = message->request_length;
  dcm_dtc_count_message.response = message->response;
  dcm_dtc_count_message.response_length = message->response_length;
  dcm_dtc_count_message.addressing_kind = message->addressing_kind;
  dcm_dtc_count_message.suppress_positive = message->suppress_positive;
  dcm_dtc_count_message.response_capacity = message->response_capacity;
  dcm_dtc_count_message.service_id = message->service_id;
  dcm_dtc_count_message.service_list_selector = message->service_list_selector;
  if (operation == '\0') {
    uVar1 = start_dtc_count_response_by_status_mask_8c622();
  }
  else {
    uVar1 = 0;
    cancel_dtc_count_service_and_reset_8c368();
  }
  return uVar1;
}

undefined4 dcm_resume_queued_dtc_count(void)

{
  return advance_dtc_count_sources_and_respond_8c4f8(((F33DcmMessageContext *)camry_host_ptr((uint32_t)((0xfebf3bfcu)))));
}

void reset_dtc_list_continuation_and_scratch_8c70c(void)

{
  uint uVar1;
  
  dtc_list_continuation.side_status = 0xff;
  dtc_list_continuation.yielded = '\0';
  dtc_list_continuation.scratch_length = 0;
  dtc_list_continuation.local_result = '\0';
  dtc_list_continuation.requested_mask = '\0';
  dtc_list_continuation.phase = '\0';
  uVar1 = 0;
  do {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebf3f40u + (uint32_t)(uVar1) * 1u)))) = '\0';
    uVar1 = uVar1 + 1;
  } while (uVar1 < 0x300);
  dtc_list_continuation.side_result = '\0';
  return;
}

void append_dtc_list_availability_byte_8c75c(uchar param_1)

{
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)((uint32_t)(dcm_dtc_list_message.response) + (uint32_t)(dcm_dtc_list_message.response_length) * 1u)))) = param_1;
  dcm_dtc_list_message.response_length = dcm_dtc_list_message.response_length + 1;
  return;
}

uint begin_filtered_dtc_list_and_store_mask_8c778(uchar param_1)

{
  begin_filtered_dtc_iteration(param_1);
  dtc_list_continuation.requested_mask = param_1;
  return 0;
}

bool append_next_filtered_dtc_tuple_for_list_8c790(int param_1,ushort *param_2,undefined1 *param_3)

{
  uint8_t stack_record_15[21];
  uint uVar1;
  
  uVar1 = next_filtered_dtc(((uint32_t *)((stack_record_15 + 1))),((uint8_t *)(stack_record_15)));
  if (uVar1 == 0) {
    (*((char *)camry_host_ptr((uint32_t)((uint)*param_2 + param_1)))) = (char)((*((uint32_t *)(stack_record_15 + 1))) >> 0x10);
    (*((char *)camry_host_ptr((uint32_t)((uint)*param_2 + param_1 + 1)))) = (char)((*((uint32_t *)(stack_record_15 + 1))) >> 8);
    (*((char *)camry_host_ptr((uint32_t)((uint)*param_2 + param_1 + 2)))) = (char)(*((uint32_t *)(stack_record_15 + 1)));
    (*((uchar *)camry_host_ptr((uint32_t)((uint)*param_2 + param_1 + 3)))) = stack_record_15[0];
    *param_2 = *param_2 + 4;
  }
  *param_3 = (char)uVar1;
  return uVar1 != 0;
}

uint append_dtc_tuple_if_fits(uchar *tuple)

{
  uint uVar1;
  
  uVar1 = 1;
  if ((dcm_dtc_list_message.response != 0) &&
     (3 < dcm_dtc_list_message.response_capacity - dcm_dtc_list_message.response_length)) {
    uVar1 = 0;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)((uint32_t)(dcm_dtc_list_message.response) + (uint32_t)(dcm_dtc_list_message.response_length) * 1u)))) = *tuple;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)((uint32_t)(dcm_dtc_list_message.response) + (uint32_t)(dcm_dtc_list_message.response_length + 1) * 1u)))) = tuple[1];
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)((uint32_t)(dcm_dtc_list_message.response) + (uint32_t)(dcm_dtc_list_message.response_length + 2) * 1u)))) = tuple[2];
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)((uint32_t)(dcm_dtc_list_message.response) + (uint32_t)(dcm_dtc_list_message.response_length + 3) * 1u)))) = tuple[3];
    dcm_dtc_list_message.response_length = dcm_dtc_list_message.response_length + 4;
  }
  return uVar1;
}

uint merge_dtc_list_sources(F33DiagSourceBuffer *local,F33DiagSourceBuffer *side)

{
  uint8_t stack_record_24[36];
  byte *pbVar1;
  ushort uVar2;
  F33DiagSourceBuffer *extraout_r7;
  F33DiagSourceBuffer *extraout_r7_00;
  F33DiagSourceBuffer *extraout_r7_01;
  uint uVar3;
  uint uVar4;
  uint uVar5;
  uint uVar6;
  
  uVar2 = side->length;
  uVar4 = 0;
  uVar3 = 0;
  uVar5 = 0;
  do {
    ((uint8_t *)(stack_record_24))[uVar5] = 0;
    uVar6 = uVar5 + 1;
    ((uint8_t *)((stack_record_24 + 4)))[uVar5] = 0;
    uVar5 = uVar6;
  } while (uVar6 < 4);
  if ((local->status == '\x01') || (side->status == '\x01')) {
    if (local->length == 0) {
      uVar5 = 0xffffffff;
    }
    else {
      uVar5 = 0;
    }
    if (uVar2 == 0) {
      uVar6 = 0xffffffff;
      goto LAB_0008c952;
    }
    uVar6 = 0;
    do {
      do {
        if (uVar5 != 0) goto LAB_0008c8ce;
        while( true ) {
          if (uVar4 < local->length) {
            pbVar1 = ((void *)camry_host_ptr((uint32_t)(local->bytes + uVar4)));
            ((uint8_t *)(stack_record_24))[0] = *pbVar1;
            ((uint8_t *)(stack_record_24))[1] = pbVar1[1];
            ((uint8_t *)(stack_record_24))[2] = pbVar1[2];
            ((uint8_t *)(stack_record_24))[3] = pbVar1[3];
            uVar5 = (uint)((uint8_t *)(stack_record_24))[2] | (uint)((uint8_t *)(stack_record_24))[1] << 8 | (uint)((uint8_t *)(stack_record_24))[0] << 0x10;
          }
          else {
            uVar5 = 0xffffffff;
          }
LAB_0008c8ce:
          if (uVar6 == 0) {
            if (uVar3 < side->length) {
              pbVar1 = ((void *)camry_host_ptr((uint32_t)(side->bytes + uVar3)));
              ((uint8_t *)((stack_record_24 + 4)))[0] = *pbVar1;
              ((uint8_t *)((stack_record_24 + 4)))[1] = pbVar1[1];
              ((uint8_t *)((stack_record_24 + 4)))[2] = pbVar1[2];
              ((uint8_t *)((stack_record_24 + 4)))[3] = pbVar1[3];
              uVar6 = (uint)((uint8_t *)((stack_record_24 + 4)))[2] | (uint)((uint8_t *)((stack_record_24 + 4)))[1] << 8 | (uint)((uint8_t *)((stack_record_24 + 4)))[0] << 0x10;
            }
            else {
              uVar6 = 0xffffffff;
            }
          }
          if (uVar5 >= uVar6 && uVar5 != uVar6) break;
          if (uVar5 < uVar6) {
            append_dtc_tuple_if_fits(((uint8_t *)(stack_record_24)));
            uVar4 = uVar4 + 4 & 0xffff;
            side = ((F33DiagSourceBuffer *)(side));
          }
          else {
            if (uVar5 == 0xffffffff) goto LAB_0008c956;
            ((uint8_t *)((stack_record_24 + 4)))[3] = ((uint8_t *)((stack_record_24 + 4)))[3] | ((uint8_t *)(stack_record_24))[3];
            if ((((uint8_t *)((stack_record_24 + 4)))[3] & 0x29) != 0) {
              ((uint8_t *)((stack_record_24 + 4)))[3] = ((uint8_t *)((stack_record_24 + 4)))[3] & 0xef;
            }
            append_dtc_tuple_if_fits(((uint8_t *)((stack_record_24 + 4))));
            uVar4 = uVar4 + 4 & 0xffff;
            uVar6 = 0;
            uVar3 = uVar3 + 4 & 0xffff;
            side = ((F33DiagSourceBuffer *)(side));
          }
        }
        append_dtc_tuple_if_fits(((uint8_t *)((stack_record_24 + 4))));
        uVar6 = 0;
        uVar3 = uVar3 + 4 & 0xffff;
        side = ((F33DiagSourceBuffer *)(side));
LAB_0008c952:;
      } while (uVar5 != 0xffffffff);
LAB_0008c956:;
    } while (uVar6 != 0xffffffff);
  }
  return 0;
}

uint dcm_advance_dtc_list_request(F33DcmMessageContext *message)

{
  camry_write32((camry_sp - 4u) & ~3u, camry_gpr[21]);
  camry_write32((camry_sp - 8u) & ~3u, camry_gpr[22]);
  camry_write32((camry_sp - 12u) & ~3u, camry_gpr[23]);
  camry_write32((camry_sp - 16u) & ~3u, camry_gpr[24]);
  camry_write32((camry_sp - 20u) & ~3u, camry_gpr[25]);
  camry_write32((camry_sp - 24u) & ~3u, camry_gpr[26]);
  camry_write32((camry_sp - 28u) & ~3u, camry_gpr[27]);
  camry_write32((camry_sp - 32u) & ~3u, camry_gpr[28]);
  camry_write32((camry_sp - 36u) & ~3u, camry_gpr[29]);
  camry_write32((camry_sp - 40u) & ~3u, camry_gpr[31]);
  camry_sp -= 72u;
  camry_gpr[3] = camry_sp;

  uint8_t *stack_record_44 = (uint8_t *)camry_host_ptr(camry_sp + 4u);
  uint uVar1;
  ushort uVar2;
  uchar uVar3;
  uchar uVar4;
  int iVar5;
  uchar uVar6;
  uint uVar7;

  
  uVar4 = dtc_list_continuation.yielded;
  uVar3 = dtc_list_continuation.requested_mask;
  uVar6 = dtc_list_continuation.phase;
  uVar2 = dtc_list_continuation.opaque_00;
  iVar5 = 0;
  (*((uint16_t *)(stack_record_44 + 2))) = dtc_list_continuation.scratch_length;
  uVar7 = (uint)dtc_list_continuation.side_result;
  stack_record_44[0] = dtc_list_continuation.local_result;
  stack_record_44[1] = dtc_list_continuation.side_status;
  if (dtc_list_continuation.phase == '\0') {
    uVar6 = '\x02';
    ((uint8_t *)((stack_record_44 + 20)))[0] = dtc_list_continuation.requested_mask;
    uVar7 = ((void)(0x28000200), (void)(2), (void)(1), (void)(((uint8_t *)((stack_record_44 + 20)))), (void)(((uint8_t *)((stack_record_44 + 1)))), return_const_0_8b10c());
    while ((stack_record_44[0] != '\x01' && (iVar5 != 1))) {
      iVar5 = append_next_filtered_dtc_tuple_for_list_8c790(camry_host_addr(dtc_list_local_tuple_scratch), ((uint16_t *)((stack_record_44 + 2))), ((uint8_t *)(stack_record_44)));
    }
  }
  else if (dtc_list_continuation.phase == '\x02') {
    if (uVar7 == 2) {
      uVar7 = ((void)(1), (void)(2), return_const_0_8b110());
    }
    while ((stack_record_44[0] != '\x01' && (iVar5 != 1))) {
      iVar5 = append_next_filtered_dtc_tuple_for_list_8c790(camry_host_addr(dtc_list_local_tuple_scratch), ((uint16_t *)((stack_record_44 + 2))), ((uint8_t *)(stack_record_44)));
    }
  }
  else {
    stack_record_44[0] = '\x01';
    uVar7 = 1;
    (*((uint16_t *)(stack_record_44 + 2))) = 0;
    uVar2 = 0;
  }
  if ((stack_record_44[0] == '\x02') || (uVar7 == 2)) {
    dcm_post_service_event(0xed);
  }
  else {
    if (uVar4 != '\0') {
      (*((F33DiagSourceBuffer *)camry_host_ptr(camry_sp + 16u))).bytes = camry_host_addr(dtc_list_local_tuple_scratch);
      (*((F33DiagSourceBuffer *)camry_host_ptr(camry_sp + 8u))).status = (uchar)uVar7;
      (*((F33DiagSourceBuffer *)camry_host_ptr(camry_sp + 8u))).bytes = 0;
      (*((F33DiagSourceBuffer *)camry_host_ptr(camry_sp + 16u))).length = (*((uint16_t *)(stack_record_44 + 2)));
      (*((F33DiagSourceBuffer *)camry_host_ptr(camry_sp + 8u))).length = 0;
      (*((F33DiagSourceBuffer *)camry_host_ptr(camry_sp + 16u))).status = stack_record_44[0];
      merge_dtc_list_sources(&(*((F33DiagSourceBuffer *)camry_host_ptr(camry_sp + 16u))),&(*((F33DiagSourceBuffer *)camry_host_ptr(camry_sp + 8u))));
      (camry_gpr[21] = camry_host_addr(message), camry_gpr[22] = uVar2, camry_gpr[23] = uVar3, camry_gpr[24] = 0xfebf3f40u, camry_gpr[25] = uVar4, camry_gpr[26] = iVar5, camry_gpr[27] = uVar6, camry_gpr[28] = uVar7, camry_gpr[29] = 0xfebf3f18u, camry_gpr[6] = camry_host_addr(message), camry_gpr[31] = 0x8ca3cu, dcm_report_positive_response)(message);
      uVar6 = '\0';
      uVar2 = 0;
      uVar7 = 0;
      (*((uint16_t *)(stack_record_44 + 2))) = 0;
      uVar3 = '\0';
      stack_record_44[0] = '\0';
      uVar4 = '\0';
      uVar1 = 0;
      goto LAB_0008ca68;
    }
    dcm_post_service_event(0xed);
    uVar4 = 'Z';
  }
  uVar1 = 10;
LAB_0008ca68:
  dtc_list_continuation.opaque_00 = uVar2;
  dtc_list_continuation.side_result = (uchar)uVar7;
  dtc_list_continuation.requested_mask = uVar3;
  dtc_list_continuation.scratch_length = (*((uint16_t *)(stack_record_44 + 2)));
  dtc_list_continuation.phase = uVar6;
  dtc_list_continuation.yielded = uVar4;
  dtc_list_continuation.local_result = stack_record_44[0];
  dtc_list_continuation.side_status = stack_record_44[1];
  { uint32_t camry_return_value = (uVar1); if (camry_halted) return 0; camry_gpr[21] = camry_read32((camry_sp + 68u) & ~3u); camry_gpr[22] = camry_read32((camry_sp + 64u) & ~3u); camry_gpr[23] = camry_read32((camry_sp + 60u) & ~3u); camry_gpr[24] = camry_read32((camry_sp + 56u) & ~3u); camry_gpr[25] = camry_read32((camry_sp + 52u) & ~3u); camry_gpr[26] = camry_read32((camry_sp + 48u) & ~3u); camry_gpr[27] = camry_read32((camry_sp + 44u) & ~3u); camry_gpr[28] = camry_read32((camry_sp + 40u) & ~3u); camry_gpr[29] = camry_read32((camry_sp + 36u) & ~3u); camry_gpr[31] = camry_read32((camry_sp + 32u) & ~3u); camry_sp += 72u; camry_gpr[3] = camry_sp; return camry_return_value; }
}

uint start_dtc_list_response_by_status_mask_8ca8a(void)

{
  camry_write32((camry_sp - 4u) & ~3u, camry_gpr[27]);
  camry_write32((camry_sp - 8u) & ~3u, camry_gpr[29]);
  camry_write32((camry_sp - 12u) & ~3u, camry_gpr[31]);
  camry_sp -= 20u;
  camry_gpr[3] = camry_sp;

  uchar nrc;
  uint uVar1;
  int iVar2;
  uchar *auStack_11 = (uchar *)camry_host_ptr(camry_sp + 3u);
  
  auStack_11[0] = '\0';
  set_diagnostic_busy_marker_from_done_flag_9560e(0);
  if (dcm_dtc_list_message.request_length == 1) {
    if (dcm_dtc_list_message.response_capacity == 0) {
      { uint32_t camry_return_value = (0); if (camry_halted) return 0; camry_gpr[27] = camry_read32((camry_sp + 16u) & ~3u); camry_gpr[29] = camry_read32((camry_sp + 12u) & ~3u); camry_gpr[31] = camry_read32((camry_sp + 8u) & ~3u); camry_sp += 20u; camry_gpr[3] = camry_sp; return camry_return_value; }
    }
    uVar1 = get_dtc_status_availability_mask(auStack_11);
    if (uVar1 == 0) {
      append_dtc_list_availability_byte_8c75c(auStack_11[0]);
      if (*((uint8_t *)camry_host_ptr((uint32_t)(dcm_dtc_list_message.request))) == '\0') {
        (camry_gpr[27] = 0, camry_gpr[29] = 0xfebf3f24u, camry_gpr[6] = 0xfebf3f24u, camry_gpr[31] = 0x8caf8u, dcm_report_positive_response)(((F33DcmMessageContext *)camry_host_ptr((uint32_t)((0xfebf3f24u)))));
        { uint32_t camry_return_value = (0); if (camry_halted) return 0; camry_gpr[27] = camry_read32((camry_sp + 16u) & ~3u); camry_gpr[29] = camry_read32((camry_sp + 12u) & ~3u); camry_gpr[31] = camry_read32((camry_sp + 8u) & ~3u); camry_sp += 20u; camry_gpr[3] = camry_sp; return camry_return_value; }
      }
      iVar2 = begin_filtered_dtc_list_and_store_mask_8c778(*((uint8_t *)camry_host_ptr((uint32_t)(dcm_dtc_list_message.request))));
      if (iVar2 == 0) {
        uVar1 = (camry_gpr[27] = 0, camry_gpr[29] = 0xfebf3f24u, camry_gpr[6] = 0xfebf3f24u, camry_gpr[31] = 0x8cadcu, dcm_advance_dtc_list_request)(((F33DcmMessageContext *)camry_host_ptr((uint32_t)((0xfebf3f24u)))));
        { uint32_t camry_return_value = (uVar1); if (camry_halted) return 0; camry_gpr[27] = camry_read32((camry_sp + 16u) & ~3u); camry_gpr[29] = camry_read32((camry_sp + 12u) & ~3u); camry_gpr[31] = camry_read32((camry_sp + 8u) & ~3u); camry_sp += 20u; camry_gpr[3] = camry_sp; return camry_return_value; }
      }
    }
    nrc = '!';
  }
  else {
    nrc = '\x13';
  }
  (camry_gpr[27] = 0, camry_gpr[29] = 0xfebf3f24u, camry_gpr[6] = 0xfebf3f24u, camry_r7 = camry_gpr[7] = nrc, camry_gpr[31] = 0x8caf0u, dcm_report_negative_or_pending)(((F33DcmMessageContext *)camry_host_ptr((uint32_t)((0xfebf3f24u)))), nrc);
  { uint32_t camry_return_value = (0); if (camry_halted) return 0; camry_gpr[27] = camry_read32((camry_sp + 16u) & ~3u); camry_gpr[29] = camry_read32((camry_sp + 12u) & ~3u); camry_gpr[31] = camry_read32((camry_sp + 8u) & ~3u); camry_sp += 20u; camry_gpr[3] = camry_sp; return camry_return_value; }
}

void dcm_cancel_retained_dtc_list(void)

{
  reset_dtc_list_continuation_and_scratch_8c70c();
  dcm_cancel_service_events(0xed,'\0');
  set_diagnostic_busy_marker_from_done_flag_9560e(1);
  return;
}

uint dcm_read_dtc_list_service(uchar operation,F33DcmMessageContext *message)

{
  camry_write32((camry_sp - 4u) & ~3u, camry_gpr[29]);
  camry_write32((camry_sp - 8u) & ~3u, camry_gpr[31]);
  camry_sp -= 8u;
  camry_gpr[3] = camry_sp;

  uint uVar1;
  
  dcm_dtc_list_message.request = message->request;
  dcm_dtc_list_message.request_length = message->request_length;
  dcm_dtc_list_message.response = message->response;
  dcm_dtc_list_message.response_length = message->response_length;
  dcm_dtc_list_message.addressing_kind = message->addressing_kind;
  dcm_dtc_list_message.suppress_positive = message->suppress_positive;
  dcm_dtc_list_message.response_capacity = message->response_capacity;
  dcm_dtc_list_message.service_id = message->service_id;
  dcm_dtc_list_message.service_list_selector = message->service_list_selector;
  if (operation == '\0') {
    uVar1 = (camry_gpr[31] = 0x8cb6au, start_dtc_list_response_by_status_mask_8ca8a)();
  }
  else {
    uVar1 = 0;
    (camry_gpr[29] = 0, camry_gpr[31] = 0x8cb74u, dcm_cancel_retained_dtc_list)();
  }
  { uint32_t camry_return_value = (uVar1); if (camry_halted) return 0; camry_gpr[29] = camry_read32((camry_sp + 4u) & ~3u); camry_gpr[31] = camry_read32((camry_sp + 0u) & ~3u); camry_sp += 8u; camry_gpr[3] = camry_sp; return camry_return_value; }
}

uint dcm_resume_queued_dtc_list(void)

{
  camry_write32((camry_sp - 4u) & ~3u, camry_gpr[31]);
  camry_sp -= 4u;
  camry_gpr[3] = camry_sp;

  { uint32_t camry_return_value = ((camry_gpr[6] = 0xfebf3f24u, camry_gpr[31] = 0x8cb88u, dcm_advance_dtc_list_request)(((F33DcmMessageContext *)camry_host_ptr((uint32_t)((0xfebf3f24u)))))); if (camry_halted) return 0; camry_gpr[31] = camry_read32((camry_sp + 0u) & ~3u); camry_sp += 4u; camry_gpr[3] = camry_sp; return camry_return_value; }
}

void fill_constant_block_8cb8c(void)

{
  DAT_febf4247 = 0xff;
  DAT_febf4246 = 0;
  DAT_febf4242 = 0;
  DAT_febf4240 = 0;
  DAT_febf4245 = 0;
  DAT_febf4244 = 0;
  return;
}

undefined4 return_const_0_8cbc0(void)

{
  return 0;
}

undefined4 append_next_snapshot_identifier_tuple_8cbc4(int param_1,ushort *param_2,undefined1 *param_3)

{
  uint8_t stack_record_19[25];
  undefined1 *puVar1;
  ushort uVar2;
  uint uVar3;
  undefined4 uVar4;
  
  uVar2 = *param_2;
  uVar3 = next_snapshot_identifier_tuple((stack_record_19 + 1),stack_record_19);
  if (uVar3 == 0) {
    puVar1 = ((undefined1 *)camry_host_ptr((uint32_t)((uint)uVar2 + param_1)));
    puVar1[2] = (char)(*((uint32_t *)(stack_record_19 + 1)));
    *puVar1 = (char)((*((uint32_t *)(stack_record_19 + 1))) >> 0x10);
    puVar1[1] = (char)((*((uint32_t *)(stack_record_19 + 1))) >> 8);
    puVar1[3] = stack_record_19[0];
    *param_2 = uVar2 + 4;
    uVar4 = 0;
  }
  else {
    uVar4 = 0x5a;
  }
  *param_3 = (char)uVar3;
  return uVar4;
}

uint merge_snapshot_identifier_sources
               (F33DiagSourceBuffer *local,F33DiagSourceBuffer *side,F33DiagOutputView *output)

{
  uint uVar1;
  uint uVar2;
  uint uVar3;
  uint uVar4;
  uint uVar5;
  uint uVar6;
  byte *pbVar7;
  
  uVar6 = 0;
  uVar1 = 0;
  uVar5 = (uint)local->length;
  uVar4 = (uint)side->length;
  uVar3 = (uint)*((uint16_t *)camry_host_ptr((uint32_t)(output->capacity)));
  if ((local->status == '\x01') || (side->status == '\x01')) {
    if ((uVar5 != 0) && (uVar2 = uVar1, uVar5 <= uVar3)) {
      for (; pbVar7 = ((void *)camry_host_ptr((uint32_t)(local->bytes))), uVar2 < uVar5; uVar2 = uVar2 + 1 & 0xffff) {
        (*((volatile uint8_t *)camry_host_ptr((uint32_t)((uint32_t)(output->bytes) + (uint32_t)(uVar2) * 1u)))) = pbVar7[uVar2];
      }
      uVar1 = (uint)pbVar7[2] | (uint)pbVar7[1] << 8 | (uint)*pbVar7 << 0x10;
      uVar6 = uVar2;
    }
    if (((uVar4 != 0) && ((int)((uVar5 + uVar4) - uVar3) < 0 || uVar5 + uVar4 == uVar3)) &&
       (pbVar7 = ((void *)camry_host_ptr((uint32_t)(side->bytes))),
       uVar1 != ((uint)pbVar7[2] | (uint)pbVar7[1] << 8 | (uint)*pbVar7 << 0x10))) {
      for (uVar1 = 0; uVar1 < uVar4; uVar1 = uVar1 + 1 & 0xffff) {
        (*((volatile uint8_t *)camry_host_ptr((uint32_t)((uint32_t)(output->bytes) + (uint32_t)(uVar6 + uVar1) * 1u)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)((uint32_t)(side->bytes) + (uint32_t)(uVar1) * 1u))));
      }
      uVar6 = uVar6 + uVar1;
    }
  }
  *((uint16_t *)camry_host_ptr((uint32_t)(output->length))) = (ushort)uVar6;
  return 0;
}

uint advance_snapshot_identifier_sources_and_merge_8ccb8(void)

{
  uint8_t stack_record_45[69];
  int iVar1;
  uint uVar2;
  ushort uVar3;
  char cVar4;
  uint uVar5;
  ushort uVar6;
  F33DiagOutputView FStack_3c;
  F33DiagSourceBuffer FStack_2c;
  F33DiagSourceBuffer FStack_24;
  
  cVar4 = DAT_febf4246;
  uVar3 = DAT_febf4242;
  uVar6 = DAT_febf4240;
  uVar5 = (uint)DAT_febf4245;
  stack_record_45[0] = DAT_febf4244;
  stack_record_45[1] = DAT_febf4247;
  FStack_2c.detail = '\0';
  if (DAT_febf4246 == '\0') {
    (*((uint16_t *)(stack_record_45 + 3))) = 0;
    cVar4 = '\x02';
    iVar1 = 0;
    while ((stack_record_45[0] != '\x01' && (iVar1 != 0x5a))) {
      iVar1 = append_next_snapshot_identifier_tuple_8cbc4(camry_host_addr(snapshot_identifier_local_scratch), (stack_record_45 + 3), stack_record_45);
    }
    uVar6 = uVar6 + (*((uint16_t *)(stack_record_45 + 3)));
    stack_record_45[2] = 3;
    uVar5 = ((void)(0x30000300), (void)(2), (void)(1), (void)((stack_record_45 + 2)), (void)((stack_record_45 + 1)), return_const_0_8b10c());
  }
  else if (DAT_febf4246 == '\x02') {
    if (DAT_febf4244 == '\x02') {
      (*((uint16_t *)(stack_record_45 + 3))) = DAT_febf4240;
      iVar1 = 0;
      while ((stack_record_45[0] != '\x01' && (iVar1 != 0x5a))) {
        iVar1 = append_next_snapshot_identifier_tuple_8cbc4(camry_host_addr(snapshot_identifier_local_scratch), (stack_record_45 + 3), stack_record_45);
      }
      uVar6 = uVar6 + (*((uint16_t *)(stack_record_45 + 3)));
    }
    if ((uVar5 == 2) && (uVar5 = ((void)(1), (void)(2), (void)(stack_record_45[1]), return_const_0_8b110()), uVar5 != 2)) {
      uVar3 = 0;
    }
  }
  else {
    uVar5 = 1;
    stack_record_45[0] = '\x01';
    uVar6 = 0;
    uVar3 = 0;
  }
  if ((stack_record_45[0] == '\x02') || (uVar5 == 2)) {
    dcm_post_service_event(0xee);
    uVar2 = 10;
  }
  else {
    FStack_24.status = stack_record_45[0];
    FStack_2c.status = (uchar)uVar5;
    FStack_24.bytes = camry_host_addr(snapshot_identifier_local_scratch);
    uVar5 = 0;
    FStack_3c.bytes = dcm_snapshot_identifiers_message.response;
    FStack_2c.bytes = 0;
    (*((uint16_t *)(stack_record_45 + 5))) = (ushort)dcm_snapshot_identifiers_message.response_length;
    FStack_3c.length = camry_host_addr((stack_record_45 + 5));
    (*((uint16_t *)(stack_record_45 + 7))) = (ushort)dcm_snapshot_identifiers_message.response_capacity;
    FStack_3c.capacity = camry_host_addr((stack_record_45 + 7));
    FStack_2c.length = uVar3;
    FStack_24.length = uVar6;
    uVar2 = merge_snapshot_identifier_sources(&FStack_24,&FStack_2c,&FStack_3c);
    dcm_snapshot_identifiers_message.response_length = (uint)(*((uint16_t *)(stack_record_45 + 5)));
    dcm_snapshot_identifiers_message.response_capacity = (uint)(*((uint16_t *)(stack_record_45 + 7)));
    dcm_report_positive_response(((F33DcmMessageContext *)camry_host_ptr((uint32_t)((0xfebf4248u)))));
    uVar3 = 0;
    stack_record_45[0] = '\0';
    uVar6 = 0;
    cVar4 = '\0';
    stack_record_45[1] = 0xff;
  }
  DAT_febf4245 = (char)uVar5;
  DAT_febf4240 = uVar6;
  DAT_febf4242 = uVar3;
  DAT_febf4244 = stack_record_45[0];
  DAT_febf4246 = cVar4;
  DAT_febf4247 = stack_record_45[1];
  return uVar2;
}

undefined4 start_snapshot_identifiers_empty_request_8ce20(void)

{
  int iVar1;
  undefined4 uVar2;
  undefined2 uStack_e;
  
  uVar2 = 0;
  uStack_e = 0;
  set_diagnostic_busy_marker_from_done_flag_9560e(0);
  dcm_snapshot_identifiers_message.response_length = 0;
  if (dcm_snapshot_identifiers_message.request_length == 0) {
    iVar1 = ((void)(0x11), (void)(&uStack_e), return_const_0_8cbc0());
    if (iVar1 == 0) {
      uVar2 = advance_snapshot_identifier_sources_and_merge_8ccb8();
    }
  }
  else {
    dcm_report_negative_or_pending(((F33DcmMessageContext *)camry_host_ptr((uint32_t)((0xfebf4248u)))), '\x13');
  }
  return uVar2;
}

void cancel_snapshot_identifiers_service_and_reset_8ce68(void)

{
  dcm_cancel_service_events(0xee,'\0');
  set_diagnostic_busy_marker_from_done_flag_9560e(1);
  fill_constant_block_8cb8c();
  return;
}

uint dcm_read_snapshot_identifiers_service(uchar operation,F33DcmMessageContext *message)

{
  uint uVar1;
  
  dcm_snapshot_identifiers_message.request = message->request;
  dcm_snapshot_identifiers_message.request_length = message->request_length;
  dcm_snapshot_identifiers_message.response = message->response;
  dcm_snapshot_identifiers_message.response_length = message->response_length;
  dcm_snapshot_identifiers_message.addressing_kind = message->addressing_kind;
  dcm_snapshot_identifiers_message.suppress_positive = message->suppress_positive;
  dcm_snapshot_identifiers_message.response_capacity = message->response_capacity;
  dcm_snapshot_identifiers_message.service_id = message->service_id;
  dcm_snapshot_identifiers_message.service_list_selector = message->service_list_selector;
  if (operation == '\0') {
    uVar1 = start_snapshot_identifiers_empty_request_8ce20();
  }
  else {
    uVar1 = 0;
    cancel_snapshot_identifiers_service_and_reset_8ce68();
  }
  return uVar1;
}

uint dcm_resume_queued_snapshot_identifiers(void)

{
  return advance_snapshot_identifier_sources_and_merge_8ccb8();
}

void fill_constant_block_8cef0(void)

{
  DAT_febf4571 = 0;
  DAT_febf4570 = 0;
  DAT_febf456f = 0;
  DAT_febf456e = 0;
  DAT_febf456a = 0;
  DAT_febf4568 = 0;
  DAT_febf456d = 1;
  DAT_febf456c = 1;
  DAT_febf4577 = 0;
  DAT_febf4576 = 0;
  DAT_febf4575 = 0;
  DAT_febf4574 = 0;
  DAT_febf4573 = 0;
  DAT_febf4564 = 0;
  DAT_febf4572 = 0xff;
  DAT_febf457b = 0;
  DAT_febf457a = 0;
  DAT_febf4579 = 0;
  DAT_febf4578 = 0;
  return;
}

bool build_three_byte_identifier_and_status_response_8cf8e(undefined4 param_1,int *param_2)

{
  int iVar1;
  undefined1 uStack_9;
  
  uStack_9 = 0;
  iVar1 = read_dtc_status_with_zero_success_code_4d79a(param_1,0,&uStack_9);
  if (iVar1 == 0) {
    (*((undefined1 *)camry_host_ptr((uint32_t)(param_2[2] ))))= (*((undefined1 *)camry_host_ptr((uint32_t)(*param_2))));
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(param_2[2] + 1)))) = (*((undefined1 *)camry_host_ptr((uint32_t)(*param_2 + 1))));
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(param_2[2] + 2)))) = (*((undefined1 *)camry_host_ptr((uint32_t)(*param_2 + 2))));
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(param_2[2] + 3)))) = uStack_9;
    param_2[3] = 4;
  }
  return iVar1 != 0;
}

undefined1 increment_record_index_and_latch_end_flags_8cfe8(char param_1,undefined1 *param_2,undefined1 *param_3,byte *param_4)

{
  byte bVar1;
  undefined1 uVar2;
  undefined1 uVar3;
  undefined1 uVar4;
  
  bVar1 = *param_4;
  uVar4 = *param_2;
  if (bVar1 < 0xfe) {
    bVar1 = bVar1 + 1;
    uVar2 = *param_3;
    uVar3 = 0;
    if (param_1 == -1) {
      uVar4 = 0x5a;
      uVar3 = uVar4;
    }
  }
  else {
    uVar2 = 0x5a;
    uVar3 = uVar2;
  }
  *param_4 = bVar1;
  *param_2 = uVar4;
  *param_3 = uVar2;
  return uVar3;
}
