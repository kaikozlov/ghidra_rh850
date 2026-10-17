#include "common.h"


/* WARNING: Inlined function: f33_diag_routine_local_dispatch_enabled */

undefined4 FUN_0008c018(F33DcmMessageContext *param_1,uint param_2)

{
  uint uVar1;
  uchar uVar2;
  uchar lower_status;
  uint uVar3;
  undefined1 uStack_29;
  undefined1 auStack_28 [8];
  
  uVar2 = DAT_febf3bd1;
  uStack_29 = DAT_febf3bd3;
  uVar3 = 0;
  do {
    uVar1 = uVar3 + 1;
    auStack_28[uVar3] = 0;
    uVar3 = uVar1;
  } while (uVar1 < 8);
  if (DAT_febf3bd0 == '\0') {
    auStack_28[0] = (undefined1)(param_2 >> 0x18);
    auStack_28[1] = (undefined1)(param_2 >> 0x10);
    auStack_28[2] = (undefined1)(param_2 >> 8);
    auStack_28[3] = (undefined1)param_2;
    lower_status = ((void)(0x18000000), (void)(4), (void)(4), (void)(auStack_28), (void)(&uStack_29), f33_return_const_0_8b10c());
  }
  else {
    if (DAT_febf3bd0 != '\x01') {
      return 0;
    }
    lower_status = DAT_febf3bd2;
    if (DAT_febf3bd2 == '\x04') {
      lower_status = ((void)(6), (void)(4), f33_return_const_0_8b110());
    }
    if (uVar2 != '\x04') goto LAB_0008c0b8;
  }
  uVar3 = f33_validate_clear_all_diagnostic_group(param_2);
  uVar2 = (uchar)uVar3;
LAB_0008c0b8:
  uVar3 = f33_merge_two_diagnostic_statuses(uVar2,lower_status,'\0','\x04');
  if (uVar3 == 4) {
    f33_dcm_post_service_event(0xeb);
    DAT_febf3bd0 = 1;
    DAT_febf3bd1 = uVar2;
    DAT_febf3bd2 = lower_status;
    DAT_febf3bd3 = uStack_29;
    return 1;
  }
  if (uVar3 == 0) {
    DAT_febf3bd1 = 1;
    DAT_febf3bd2 = 1;
    DAT_febf3bd0 = 1;
    DAT_febf3bd3 = uStack_29;
    return 0;
  }
  uVar2 = '\"';
  if (uVar3 == 1) {
    uVar2 = '1';
  }
  f33_dcm_report_negative_or_pending(param_1,uVar2);
  DAT_febf3bd0 = 0;
  DAT_febf3bd1 = 1;
  DAT_febf3bd2 = 1;
  DAT_febf3bd3 = uStack_29;
  return 1;
}



/* WARNING: Inlined function: f33_diag_routine_local_dispatch_enabled */
/* WARNING: Removing unreachable block (ram,0x0008c174) */

undefined4 FUN_0008c104(F33DcmMessageContext *param_1,undefined4 param_2)

{
  uint uVar1;
  uchar nrc;
  uchar lower_status;
  ushort uVar2;
  uint uVar3;
  undefined4 uVar4;
  char cVar5;
  uchar application_status;
  undefined1 uStack_25;
  undefined1 auStack_24 [8];
  
  application_status = DAT_febf3bd1;
  cVar5 = DAT_febf3bd0;
  uStack_25 = DAT_febf3bd3;
  uVar3 = 0;
  do {
    uVar1 = uVar3 + 1;
    auStack_24[uVar3] = 0;
    uVar3 = uVar1;
  } while (uVar1 < 8);
  if (DAT_febf3bd0 == '\x01') {
    auStack_24[0] = (undefined1)((uint)param_2 >> 0x18);
    auStack_24[1] = (undefined1)((uint)param_2 >> 0x10);
    cVar5 = '\x02';
    auStack_24[2] = (undefined1)((uint)param_2 >> 8);
    auStack_24[3] = (undefined1)param_2;
    lower_status = ((void)(0x18000001), (void)(4), (void)(4), (void)(auStack_24), (void)(&uStack_25), f33_return_const_0_8b10c());
  }
  else {
    if (DAT_febf3bd0 != '\x02') {
      application_status = '\x06';
      lower_status = '\x06';
      goto LAB_0008c1b0;
    }
    lower_status = DAT_febf3bd2;
    if (DAT_febf3bd2 == '\x04') {
      lower_status = ((void)(6), (void)(4), f33_return_const_0_8b110());
    }
    if (application_status != '\x04') goto LAB_0008c1b0;
  }
  uVar2 = f33_diagnostic_clear_request_callback();
  application_status = (uchar)uVar2;
LAB_0008c1b0:
  uVar3 = f33_merge_two_diagnostic_statuses(application_status,lower_status,'\0','\x04');
  if (uVar3 == 4) {
    uVar4 = 10;
    f33_dcm_post_service_event(0xeb);
  }
  else {
    application_status = '\x01';
    lower_status = '\x01';
    uVar4 = 1;
    cVar5 = '\0';
    if (uVar3 == 0) {
      f33_dcm_report_positive_response(param_1);
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
      f33_dcm_report_negative_or_pending(param_1,nrc);
    }
  }
  DAT_febf3bd1 = application_status;
  DAT_febf3bd2 = lower_status;
  DAT_febf3bd0 = cVar5;
  DAT_febf3bd3 = uStack_25;
  return uVar4;
}



/* Preserve group/message, call8C018(message,group), and on success8C104(message,group). Return
   consequentialR10 from last phase without manufacturing success;8C2A8 retains it. */

uint f33_dcm_join_clear_diagnostic_phases(uint group,F33DcmMessageContext *message)

{
  uint uVar1;
  
  uVar1 = FUN_0008c018(message,group);
  if (uVar1 == 0) {
    uVar1 = FUN_0008c104(message,group);
  }
  return uVar1;
}



/* Require exactly3 remaining bytes, assemble big-endian24 group and retain message3BD4. Application
   validation accepts onlyFFFFFF; accepted group enters existing asynchronous clear owner1410. */

uint f33_dcm_begin_clear_diagnostic_request(F33DcmMessageContext *message)

{
  uint uVar1;
  uint group;
  byte *pbVar2;
  
  FUN_0009560e(0);
  f33_dcm_clear_message.request = message->request;
  DAT_febf3bcc = 0;
  f33_dcm_clear_message.request_length = message->request_length;
  f33_dcm_clear_message.response = message->response;
  f33_dcm_clear_message.response_length = message->response_length;
  f33_dcm_clear_message.addressing_kind = message->addressing_kind;
  f33_dcm_clear_message.suppress_positive = message->suppress_positive;
  f33_dcm_clear_message.response_capacity = message->response_capacity;
  f33_dcm_clear_message.service_id = message->service_id;
  f33_dcm_clear_message.service_list_selector = message->service_list_selector;
  if (message->request_length == 3) {
    pbVar2 = ((void *)camry_host_ptr((uint32_t)(message->request)));
    group = (uint)pbVar2[2] | (uint)pbVar2[1] << 8 | (uint)*pbVar2 << 0x10;
    uVar1 = f33_dcm_join_clear_diagnostic_phases(group, ((F33DcmMessageContext *)camry_host_ptr((uint32_t)((0xfebf3bd4u)))));
  }
  else {
    uVar1 = 0;
    group = 0;
    f33_dcm_report_negative_or_pending(((F33DcmMessageContext *)camry_host_ptr((uint32_t)((0xfebf3bd4u)))), '\x13');
  }
  DAT_febf3bcc = group;
  return uVar1;
}



void FUN_0008c2c4(void)

{
  f33_fill_constant_block_8bfea();
  f33_dcm_cancel_service_events(0xeb,'\0');
  FUN_0009560e(1);
  return;
}



/* Clear service operation callback. Retain advanced message for operation0; nonzero operations
   reset/cancel module state. Response submission is not acknowledgement or durable completion. */

uint f33_dcm_clear_diagnostic_service(uchar operation,F33DcmMessageContext *message)

{
  uint uVar1;
  
  if (operation == '\0') {
    uVar1 = f33_dcm_begin_clear_diagnostic_request(message);
  }
  else {
    uVar1 = 0;
    FUN_0008c2c4();
  }
  return uVar1;
}



/* EventEB re-enters8C214 with retained group3BCC and existing28-byte message3BD4; no per-event
   message pointer is stored. */

uint f33_dcm_resume_queued_clear_request(void)

{
  return f33_dcm_join_clear_diagnostic_phases(DAT_febf3bcc, ((F33DcmMessageContext *)camry_host_ptr((uint32_t)((0xfebf3bd4u)))));
}



void FUN_0008c318(void)

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
    f33_dtc_count_local_tuple_scratch[uVar1] = '\0';
    uVar1 = uVar1 + 1;
  } while (uVar1 < 0x300);
  DAT_febf3bf9 = 0;
  return;
}



void FUN_0008c368(void)

{
  FUN_0008c318();
  f33_dcm_cancel_service_events(0xec,'\0');
  FUN_0009560e(1);
  return;
}



void FUN_0008c384(uchar param_1)

{
  ((uint8_t *)camry_host_ptr((uint32_t)(f33_dcm_dtc_count_message.response)))[f33_dcm_dtc_count_message.response_length] = param_1;
  ((uint8_t *)camry_host_ptr((uint32_t)(f33_dcm_dtc_count_message.response)))[f33_dcm_dtc_count_message.response_length + 1] = '\x01';
  f33_dcm_dtc_count_message.response_length = f33_dcm_dtc_count_message.response_length + 2;
  return;
}



/* Forward status mask to4D69C and retain unmasked byte3BF5. Preserve returnedR10 through final
   store/dispose; caller8C66A checks it. */

uint f33_begin_dtc_count_iteration(uchar mask)

{
  uint uVar1;
  
  uVar1 = f33_begin_filtered_dtc_iteration(mask);
  DAT_febf3bf5 = mask;
  return uVar1;
}



bool FUN_0008c3c0(int param_1,ushort *param_2,undefined1 *param_3)

{
  uint uVar1;
  uchar uStack_15;
  uint uStack_14;
  
  uVar1 = f33_next_filtered_dtc(&uStack_14,&uStack_15);
  if (uVar1 == 0) {
    (*((char *)camry_host_ptr((uint32_t)((uint)*param_2 + param_1)))) = (char)(uStack_14 >> 0x10);
    (*((char *)camry_host_ptr((uint32_t)((uint)*param_2 + param_1 + 1)))) = (char)(uStack_14 >> 8);
    (*((char *)camry_host_ptr((uint32_t)((uint)*param_2 + param_1 + 2)))) = (char)uStack_14;
    (*((uchar *)camry_host_ptr((uint32_t)((uint)*param_2 + param_1 + 3)))) = uStack_15;
    *param_2 = *param_2 + 4;
  }
  *param_3 = (char)uVar1;
  return uVar1 != 0;
}



/* Append big-endian16-bit count and increment body length by2. Caller19/01 only tests capacity!=0
   before writing its4-byte body; shared transport allocation is larger but this is not a
   general4-byte caller-capacity guard. */

void f33_append_dtc_count(ushort count)

{
  ((uint8_t *)camry_host_ptr((uint32_t)(f33_dcm_dtc_count_message.response)))[f33_dcm_dtc_count_message.response_length] =
       (uchar)(count >> 8);
  ((uint8_t *)camry_host_ptr((uint32_t)(f33_dcm_dtc_count_message.response)))[f33_dcm_dtc_count_message.response_length + 1] = (uchar)count;
  f33_dcm_dtc_count_message.response_length = f33_dcm_dtc_count_message.response_length + 2;
  return;
}



undefined4 FUN_0008c4f8(F33DcmMessageContext *param_1)

{
  undefined4 uVar1;
  undefined2 uVar2;
  undefined1 uVar3;
  char cVar4;
  int iVar5;
  char cVar6;
  uint uVar7;
  uchar uStack_44;
  undefined1 uStack_43;
  ushort uStack_42;
  F33DiagSourceBuffer FStack_40;
  F33DiagSourceBuffer FStack_38;
  undefined1 auStack_30 [8];
  
  cVar4 = DAT_febf3bf7;
  uVar3 = DAT_febf3bf5;
  cVar6 = DAT_febf3bf4;
  uVar2 = DAT_febf3bf0;
  iVar5 = 0;
  uStack_42 = DAT_febf3bf2;
  uVar7 = (uint)DAT_febf3bf9;
  uStack_44 = DAT_febf3bf6;
  uStack_43 = DAT_febf3bf8;
  if (DAT_febf3bf4 == '\0') {
    cVar6 = '\x02';
    auStack_30[0] = DAT_febf3bf5;
    uVar7 = ((void)(0x20000100), (void)(2), (void)(1), (void)(auStack_30), (void)(&uStack_43), f33_return_const_0_8b10c());
    while ((uStack_44 != '\x01' && (iVar5 != 1))) {
      iVar5 = FUN_0008c3c0(camry_host_addr(f33_dtc_count_local_tuple_scratch), &uStack_42, &uStack_44);
    }
  }
  else if (DAT_febf3bf4 == '\x02') {
    if (uVar7 == 2) {
      uVar7 = ((void)(1), (void)(2), f33_return_const_0_8b110());
    }
    while ((uStack_44 != '\x01' && (iVar5 != 1))) {
      iVar5 = FUN_0008c3c0(camry_host_addr(f33_dtc_count_local_tuple_scratch), &uStack_42, &uStack_44);
    }
  }
  else {
    uStack_44 = '\x01';
    uVar7 = 1;
    uStack_42 = 0;
    uVar2 = 0;
  }
  if ((uStack_44 == '\x02') || (uVar7 == 2)) {
    f33_dcm_post_service_event(0xec);
  }
  else {
    if (cVar4 != '\0') {
      FStack_38.bytes = camry_host_addr(f33_dtc_count_local_tuple_scratch);
      FStack_40.status = (uchar)uVar7;
      FStack_40.bytes = 0;
      FStack_38.length = uStack_42;
      FStack_40.length = 0;
      FStack_38.status = uStack_44;
      f33_count_merged_dtc_sources(&FStack_38,&FStack_40);
      f33_dcm_report_positive_response(param_1);
      cVar6 = '\0';
      uVar2 = 0;
      uVar7 = 0;
      uStack_42 = 0;
      uVar3 = 0;
      uStack_44 = '\0';
      cVar4 = '\0';
      uVar1 = 0;
      goto LAB_0008c600;
    }
    f33_dcm_post_service_event(0xec);
    cVar4 = 'Z';
  }
  uVar1 = 10;
LAB_0008c600:
  DAT_febf3bf0 = uVar2;
  DAT_febf3bf9 = (char)uVar7;
  DAT_febf3bf5 = uVar3;
  DAT_febf3bf2 = uStack_42;
  DAT_febf3bf4 = cVar6;
  DAT_febf3bf7 = cVar4;
  DAT_febf3bf6 = uStack_44;
  DAT_febf3bf8 = uStack_43;
  return uVar1;
}



undefined4 FUN_0008c622(void)

{
  uchar nrc;
  uint uVar1;
  undefined4 uVar2;
  uchar auStack_11 [5];
  
  auStack_11[0] = '\0';
  FUN_0009560e(0);
  if (f33_dcm_dtc_count_message.request_length == 1) {
    if (f33_dcm_dtc_count_message.response_capacity == 0) {
      return 0;
    }
    uVar1 = f33_get_dtc_status_availability_mask(auStack_11);
    if (uVar1 == 0) {
      FUN_0008c384(auStack_11[0]);
      if (*((uint8_t *)camry_host_ptr((uint32_t)(f33_dcm_dtc_count_message.request))) == '\0') {
        f33_append_dtc_count(0);
        f33_dcm_report_positive_response(((F33DcmMessageContext *)camry_host_ptr((uint32_t)((0xfebf3bfcu)))));
        return 0;
      }
      uVar1 = f33_begin_dtc_count_iteration(*((uint8_t *)camry_host_ptr((uint32_t)(f33_dcm_dtc_count_message.request))));
      if (uVar1 == 0) {
        uVar2 = FUN_0008c4f8(((F33DcmMessageContext *)camry_host_ptr((uint32_t)((0xfebf3bfcu)))));
        return uVar2;
      }
    }
    nrc = '!';
  }
  else {
    nrc = '\x13';
  }
  f33_dcm_report_negative_or_pending(((F33DcmMessageContext *)camry_host_ptr((uint32_t)((0xfebf3bfcu)))), nrc);
  return 0;
}



/* DTC count operation callback. Retain advanced message for operation0; nonzero operations
   reset/cancel module state. Response submission is not acknowledgement or durable completion. */

uint f33_dcm_read_dtc_count_service(uchar operation,F33DcmMessageContext *message)

{
  uint uVar1;
  
  f33_dcm_dtc_count_message.request = message->request;
  f33_dcm_dtc_count_message.request_length = message->request_length;
  f33_dcm_dtc_count_message.response = message->response;
  f33_dcm_dtc_count_message.response_length = message->response_length;
  f33_dcm_dtc_count_message.addressing_kind = message->addressing_kind;
  f33_dcm_dtc_count_message.suppress_positive = message->suppress_positive;
  f33_dcm_dtc_count_message.response_capacity = message->response_capacity;
  f33_dcm_dtc_count_message.service_id = message->service_id;
  f33_dcm_dtc_count_message.service_list_selector = message->service_list_selector;
  if (operation == '\0') {
    uVar1 = FUN_0008c622();
  }
  else {
    uVar1 = 0;
    FUN_0008c368();
  }
  return uVar1;
}



/* EventEC re-enters8C4F8 with retained28-byte message3BFC. */

undefined4 f33_dcm_resume_queued_dtc_count(void)

{
  return FUN_0008c4f8(((F33DcmMessageContext *)camry_host_ptr((uint32_t)((0xfebf3bfcu)))));
}



void FUN_0008c70c(void)

{
  uint uVar1;
  
  f33_dtc_list_continuation.side_status = 0xff;
  f33_dtc_list_continuation.yielded = '\0';
  f33_dtc_list_continuation.scratch_length = 0;
  f33_dtc_list_continuation.local_result = '\0';
  f33_dtc_list_continuation.requested_mask = '\0';
  f33_dtc_list_continuation.phase = '\0';
  uVar1 = 0;
  do {
    f33_dtc_list_local_tuple_scratch[uVar1] = '\0';
    uVar1 = uVar1 + 1;
  } while (uVar1 < 0x300);
  f33_dtc_list_continuation.side_result = '\0';
  return;
}



void FUN_0008c75c(uchar param_1)

{
  ((uint8_t *)camry_host_ptr((uint32_t)(f33_dcm_dtc_list_message.response)))[f33_dcm_dtc_list_message.response_length] = param_1;
  f33_dcm_dtc_list_message.response_length = f33_dcm_dtc_list_message.response_length + 1;
  return;
}



void FUN_0008c778(uchar param_1)

{
  f33_begin_filtered_dtc_iteration(param_1);
  f33_dtc_list_continuation.requested_mask = param_1;
  return;
}



bool FUN_0008c790(int param_1,ushort *param_2,undefined1 *param_3)

{
  uint uVar1;
  uchar uStack_15;
  uint uStack_14;
  
  uVar1 = f33_next_filtered_dtc(&uStack_14,&uStack_15);
  if (uVar1 == 0) {
    (*((char *)camry_host_ptr((uint32_t)((uint)*param_2 + param_1)))) = (char)(uStack_14 >> 0x10);
    (*((char *)camry_host_ptr((uint32_t)((uint)*param_2 + param_1 + 1)))) = (char)(uStack_14 >> 8);
    (*((char *)camry_host_ptr((uint32_t)((uint)*param_2 + param_1 + 2)))) = (char)uStack_14;
    (*((uchar *)camry_host_ptr((uint32_t)((uint)*param_2 + param_1 + 3)))) = uStack_15;
    *param_2 = *param_2 + 4;
  }
  *param_3 = (char)uVar1;
  return uVar1 != 0;
}



/* Collect local tuples and poll side source; always queueED before the first ready result. A later
   ready call merges retained scratch, retaining only complete tuples that fit, then calls95644.
   Clear continuation only after that API returns. A later derived-status generation does not
   replace the already collected local snapshot; direct native re-entry is not proof of OS event
   dispatch. queueED before first ready result. Later ready call merges retained scratch and only
   complete tuples that fit, then calls95644. Clear continuation after that API returns. Later
   derived-status generation does not replace the collected snapshot; direct native re-entry does
   not prove OS event dispatch. */

uint f33_dcm_advance_dtc_list_request(F33DcmMessageContext *message)

{
  uint uVar1;
  ushort uVar2;
  uchar uVar3;
  uchar uVar4;
  int iVar5;
  uchar uVar6;
  uint uVar7;
  uchar uStack_44;
  uchar uStack_43;
  ushort uStack_42;
  F33DiagSourceBuffer FStack_40;
  F33DiagSourceBuffer FStack_38;
  uchar auStack_30 [8];
  
  uVar4 = f33_dtc_list_continuation.yielded;
  uVar3 = f33_dtc_list_continuation.requested_mask;
  uVar6 = f33_dtc_list_continuation.phase;
  uVar2 = f33_dtc_list_continuation.opaque_00;
  iVar5 = 0;
  uStack_42 = f33_dtc_list_continuation.scratch_length;
  uVar7 = (uint)f33_dtc_list_continuation.side_result;
  uStack_44 = f33_dtc_list_continuation.local_result;
  uStack_43 = f33_dtc_list_continuation.side_status;
  if (f33_dtc_list_continuation.phase == '\0') {
    uVar6 = '\x02';
    auStack_30[0] = f33_dtc_list_continuation.requested_mask;
    uVar7 = ((void)(0x28000200), (void)(2), (void)(1), (void)(auStack_30), (void)(&uStack_43), f33_return_const_0_8b10c());
    while ((uStack_44 != '\x01' && (iVar5 != 1))) {
      iVar5 = FUN_0008c790(camry_host_addr(f33_dtc_list_local_tuple_scratch), &uStack_42, &uStack_44);
    }
  }
  else if (f33_dtc_list_continuation.phase == '\x02') {
    if (uVar7 == 2) {
      uVar7 = ((void)(1), (void)(2), f33_return_const_0_8b110());
    }
    while ((uStack_44 != '\x01' && (iVar5 != 1))) {
      iVar5 = FUN_0008c790(camry_host_addr(f33_dtc_list_local_tuple_scratch), &uStack_42, &uStack_44);
    }
  }
  else {
    uStack_44 = '\x01';
    uVar7 = 1;
    uStack_42 = 0;
    uVar2 = 0;
  }
  if ((uStack_44 == '\x02') || (uVar7 == 2)) {
    f33_dcm_post_service_event(0xed);
  }
  else {
    if (uVar4 != '\0') {
      FStack_38.bytes = camry_host_addr(f33_dtc_list_local_tuple_scratch);
      FStack_40.status = (uchar)uVar7;
      FStack_40.bytes = 0;
      FStack_38.length = uStack_42;
      FStack_40.length = 0;
      FStack_38.status = uStack_44;
      f33_merge_dtc_list_sources(&FStack_38,&FStack_40);
      f33_dcm_report_positive_response(message);
      uVar6 = '\0';
      uVar2 = 0;
      uVar7 = 0;
      uStack_42 = 0;
      uVar3 = '\0';
      uStack_44 = '\0';
      uVar4 = '\0';
      uVar1 = 0;
      goto LAB_0008ca68;
    }
    f33_dcm_post_service_event(0xed);
    uVar4 = 'Z';
  }
  uVar1 = 10;
LAB_0008ca68:
  f33_dtc_list_continuation.opaque_00 = uVar2;
  f33_dtc_list_continuation.side_result = (uchar)uVar7;
  f33_dtc_list_continuation.requested_mask = uVar3;
  f33_dtc_list_continuation.scratch_length = uStack_42;
  f33_dtc_list_continuation.phase = uVar6;
  f33_dtc_list_continuation.yielded = uVar4;
  f33_dtc_list_continuation.local_result = uStack_44;
  f33_dtc_list_continuation.side_status = uStack_43;
  return uVar1;
}



/* Reset DTC-list scratch/phase/yield state, tombstone all queuedED slots and release shared
   diagnostic continuation token through9560E(1). Ring occupancy is retained until dispatch pops
   tombstones. */

void f33_dcm_cancel_retained_dtc_list(void)

{
  FUN_0008c70c();
  f33_dcm_cancel_service_events(0xed,'\0');
  FUN_0009560e(1);
  return;
}



/* DTC list operation callback. Retain advanced message for operation0; nonzero operations
   reset/cancel module state. Response submission is not acknowledgement or durable completion. */

uint f33_dcm_read_dtc_list_service(uchar operation,F33DcmMessageContext *message)

{
  uint uVar1;
  
  f33_dcm_dtc_list_message.request = message->request;
  f33_dcm_dtc_list_message.request_length = message->request_length;
  f33_dcm_dtc_list_message.response = message->response;
  f33_dcm_dtc_list_message.response_length = message->response_length;
  f33_dcm_dtc_list_message.addressing_kind = message->addressing_kind;
  f33_dcm_dtc_list_message.suppress_positive = message->suppress_positive;
  f33_dcm_dtc_list_message.response_capacity = message->response_capacity;
  f33_dcm_dtc_list_message.service_id = message->service_id;
  f33_dcm_dtc_list_message.service_list_selector = message->service_list_selector;
  if (operation == '\0') {
    uVar1 = FUN_0008ca8a();
  }
  else {
    uVar1 = 0;
    f33_dcm_cancel_retained_dtc_list();
  }
  return uVar1;
}



/* EventED re-enters8C960 with existing28-byte message3F24 and retained local snapshot/scratch.
   Dispatcher has already consumed the queue slot. */

uint f33_dcm_resume_queued_dtc_list(void)

{
  return f33_dcm_advance_dtc_list_request(((F33DcmMessageContext *)camry_host_ptr((uint32_t)((0xfebf3f24u)))));
}



/* Constant-block fill: 6 literal assignments into one contiguous cell block; shape-verified.
   Literals are default/reset values; cell meanings are not recovered. */

void f33_fill_constant_block_8cb8c(void)

{
  DAT_febf4247 = 0xff;
  DAT_febf4246 = 0;
  DAT_febf4242 = 0;
  DAT_febf4240 = 0;
  DAT_febf4245 = 0;
  DAT_febf4244 = 0;
  return;
}



/* Constant source: return 0; shape-classified from the canonical corpus. Callers receive this
   literal directly; its meaning is not recovered. */

undefined4 f33_return_const_0_8cbc0(void)

{
  return 0;
}



undefined4 FUN_0008cbc4(int param_1,ushort *param_2,undefined1 *param_3)

{
  undefined1 *puVar1;
  ushort uVar2;
  uint uVar3;
  undefined4 uVar4;
  uchar uStack_19;
  uint uStack_18;
  
  uVar2 = *param_2;
  uVar3 = f33_next_snapshot_identifier_tuple(&uStack_18,&uStack_19);
  if (uVar3 == 0) {
    puVar1 = ((undefined1 *)camry_host_ptr((uint32_t)((uint)uVar2 + param_1)));
    puVar1[2] = (char)uStack_18;
    *puVar1 = (char)(uStack_18 >> 0x10);
    puVar1[1] = (char)(uStack_18 >> 8);
    puVar1[3] = uStack_19;
    *param_2 = uVar2 + 4;
    uVar4 = 0;
  }
  else {
    uVar4 = 0x5a;
  }
  *param_3 = (char)uVar3;
  return uVar4;
}



/* Copy each nonempty source only if its whole length fits u16 capacity. Compare first24-bit DTCs to
   avoid duplicate second source; do not merge snapshot record numbers or publish partial source
   bytes. */

uint f33_merge_snapshot_identifier_sources
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
        ((uint8_t *)camry_host_ptr((uint32_t)(output->bytes)))[uVar2] = pbVar7[uVar2];
      }
      uVar1 = (uint)pbVar7[2] | (uint)pbVar7[1] << 8 | (uint)*pbVar7 << 0x10;
      uVar6 = uVar2;
    }
    if (((uVar4 != 0) && ((int)((uVar5 + uVar4) - uVar3) < 0 || uVar5 + uVar4 == uVar3)) &&
       (pbVar7 = ((void *)camry_host_ptr((uint32_t)(side->bytes))),
       uVar1 != ((uint)pbVar7[2] | (uint)pbVar7[1] << 8 | (uint)*pbVar7 << 0x10))) {
      for (uVar1 = 0; uVar1 < uVar4; uVar1 = uVar1 + 1 & 0xffff) {
        ((uint8_t *)camry_host_ptr((uint32_t)(output->bytes)))[uVar6 + uVar1] = ((uint8_t *)camry_host_ptr((uint32_t)(side->bytes)))[uVar1];
      }
      uVar6 = uVar6 + uVar1;
    }
  }
  *((uint16_t *)camry_host_ptr((uint32_t)(output->length))) = (ushort)uVar6;
  return 0;
}



uint FUN_0008ccb8(void)

{
  int iVar1;
  uint uVar2;
  ushort uVar3;
  char cVar4;
  uint uVar5;
  ushort uVar6;
  uchar uStack_45;
  undefined1 uStack_44;
  undefined1 uStack_43;
  ushort uStack_42;
  ushort uStack_40;
  ushort uStack_3e;
  F33DiagOutputView FStack_3c;
  F33DiagSourceBuffer FStack_2c;
  F33DiagSourceBuffer FStack_24;
  
  cVar4 = DAT_febf4246;
  uVar3 = DAT_febf4242;
  uVar6 = DAT_febf4240;
  uVar5 = (uint)DAT_febf4245;
  uStack_45 = DAT_febf4244;
  uStack_44 = DAT_febf4247;
  FStack_2c.detail = '\0';
  if (DAT_febf4246 == '\0') {
    uStack_42 = 0;
    cVar4 = '\x02';
    iVar1 = 0;
    while ((uStack_45 != '\x01' && (iVar1 != 0x5a))) {
      iVar1 = FUN_0008cbc4(camry_host_addr(f33_snapshot_identifier_local_scratch), &uStack_42, &uStack_45);
    }
    uVar6 = uVar6 + uStack_42;
    uStack_43 = 3;
    uVar5 = ((void)(0x30000300), (void)(2), (void)(1), (void)(&uStack_43), (void)(&uStack_44), f33_return_const_0_8b10c());
  }
  else if (DAT_febf4246 == '\x02') {
    if (DAT_febf4244 == '\x02') {
      uStack_42 = DAT_febf4240;
      iVar1 = 0;
      while ((uStack_45 != '\x01' && (iVar1 != 0x5a))) {
        iVar1 = FUN_0008cbc4(camry_host_addr(f33_snapshot_identifier_local_scratch), &uStack_42, &uStack_45);
      }
      uVar6 = uVar6 + uStack_42;
    }
    if ((uVar5 == 2) && (uVar5 = ((void)(1), (void)(2), (void)(uStack_44), f33_return_const_0_8b110()), uVar5 != 2)) {
      uVar3 = 0;
    }
  }
  else {
    uVar5 = 1;
    uStack_45 = '\x01';
    uVar6 = 0;
    uVar3 = 0;
  }
  if ((uStack_45 == '\x02') || (uVar5 == 2)) {
    f33_dcm_post_service_event(0xee);
    uVar2 = 10;
  }
  else {
    FStack_24.status = uStack_45;
    FStack_2c.status = (uchar)uVar5;
    FStack_24.bytes = camry_host_addr(f33_snapshot_identifier_local_scratch);
    uVar5 = 0;
    FStack_3c.bytes = f33_dcm_snapshot_identifiers_message.response;
    FStack_2c.bytes = 0;
    uStack_40 = (ushort)f33_dcm_snapshot_identifiers_message.response_length;
    FStack_3c.length = camry_host_addr(&uStack_40);
    uStack_3e = (ushort)f33_dcm_snapshot_identifiers_message.response_capacity;
    FStack_3c.capacity = camry_host_addr(&uStack_3e);
    FStack_2c.length = uVar3;
    FStack_24.length = uVar6;
    uVar2 = f33_merge_snapshot_identifier_sources(&FStack_24,&FStack_2c,&FStack_3c);
    f33_dcm_snapshot_identifiers_message.response_length = (uint)uStack_40;
    f33_dcm_snapshot_identifiers_message.response_capacity = (uint)uStack_3e;
    f33_dcm_report_positive_response(((F33DcmMessageContext *)camry_host_ptr((uint32_t)((0xfebf4248u)))));
    uVar3 = 0;
    uStack_45 = '\0';
    uVar6 = 0;
    cVar4 = '\0';
    uStack_44 = 0xff;
  }
  DAT_febf4245 = (char)uVar5;
  DAT_febf4240 = uVar6;
  DAT_febf4242 = uVar3;
  DAT_febf4244 = uStack_45;
  DAT_febf4246 = cVar4;
  DAT_febf4247 = uStack_44;
  return uVar2;
}



undefined4 FUN_0008ce20(void)

{
  int iVar1;
  undefined4 uVar2;
  undefined2 uStack_e;
  
  uVar2 = 0;
  uStack_e = 0;
  FUN_0009560e(0);
  f33_dcm_snapshot_identifiers_message.response_length = 0;
  if (f33_dcm_snapshot_identifiers_message.request_length == 0) {
    iVar1 = ((void)(0x11), (void)(&uStack_e), f33_return_const_0_8cbc0());
    if (iVar1 == 0) {
      uVar2 = FUN_0008ccb8();
    }
  }
  else {
    f33_dcm_report_negative_or_pending(((F33DcmMessageContext *)camry_host_ptr((uint32_t)((0xfebf4248u)))), '\x13');
  }
  return uVar2;
}



void FUN_0008ce68(void)

{
  f33_dcm_cancel_service_events(0xee,'\0');
  FUN_0009560e(1);
  f33_fill_constant_block_8cb8c();
  return;
}



/* Snapshot identifiers operation callback. Retain advanced message for operation0; nonzero
   operations reset/cancel module state. Response submission is not acknowledgement or durable
   completion. */

uint f33_dcm_read_snapshot_identifiers_service(uchar operation,F33DcmMessageContext *message)

{
  uint uVar1;
  
  f33_dcm_snapshot_identifiers_message.request = message->request;
  f33_dcm_snapshot_identifiers_message.request_length = message->request_length;
  f33_dcm_snapshot_identifiers_message.response = message->response;
  f33_dcm_snapshot_identifiers_message.response_length = message->response_length;
  f33_dcm_snapshot_identifiers_message.addressing_kind = message->addressing_kind;
  f33_dcm_snapshot_identifiers_message.suppress_positive = message->suppress_positive;
  f33_dcm_snapshot_identifiers_message.response_capacity = message->response_capacity;
  f33_dcm_snapshot_identifiers_message.service_id = message->service_id;
  f33_dcm_snapshot_identifiers_message.service_list_selector = message->service_list_selector;
  if (operation == '\0') {
    uVar1 = FUN_0008ce20();
  }
  else {
    uVar1 = 0;
    FUN_0008ce68();
  }
  return uVar1;
}



/* EventEE re-enters8CCB8 using that module's retained state and existing message4248. */

uint f33_dcm_resume_queued_snapshot_identifiers(void)

{
  return FUN_0008ccb8();
}



/* Constant-block fill: 19 literal assignments into one contiguous cell block; shape-verified.
   Literals are default/reset values; cell meanings are not recovered. */

void f33_fill_constant_block_8cef0(void)

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



bool FUN_0008cf8e(undefined4 param_1,int *param_2)

{
  int iVar1;
  undefined1 uStack_9;
  
  uStack_9 = 0;
  iVar1 = FUN_0004d79a(param_1,0,&uStack_9);
  if (iVar1 == 0) {
    *(undefined1 *)param_2[2] = *(undefined1 *)*param_2;
    *(undefined1 *)(param_2[2] + 1) = (*((undefined1 *)camry_host_ptr((uint32_t)(*param_2 + 1))));
    *(undefined1 *)(param_2[2] + 2) = (*((undefined1 *)camry_host_ptr((uint32_t)(*param_2 + 2))));
    *(undefined1 *)(param_2[2] + 3) = uStack_9;
    param_2[3] = 4;
  }
  return iVar1 != 0;
}



undefined1 FUN_0008cfe8(char param_1,undefined1 *param_2,undefined1 *param_3,byte *param_4)

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



undefined4 FUN_0008d020(undefined4 param_1,undefined4 param_2,char param_3,undefined1 *param_4)

{
  short sVar1;
  undefined1 uVar2;
  undefined1 uVar3;
  undefined1 *puVar4;
  undefined1 *extraout_r9;
  int iVar5;
  undefined4 uVar6;
  undefined1 uVar7;
  undefined1 uVar8;
  char cVar9;
  uint uVar10;
  char *pcVar11;
  char local_2c;
  char local_2b;
  ushort uStack_2a;
  
  sVar1 = (short)f33_dcm_snapshot_record_message.response_capacity;
  uVar8 = 0;
  uVar7 = 0;
  uVar10 = f33_dcm_snapshot_record_message.response_length & 0xffff;
  cVar9 = '\0';
  local_2c = '\0';
  local_2b = '\0';
  puVar4 = param_4;
  do {
    cVar9 = cVar9 + '\x01';
    uStack_2a = sVar1 - (short)uVar10;
    iVar5 = FUN_0004d7c4(param_1,*puVar4,f33_dcm_snapshot_record_message.response + uVar10,
                         &uStack_2a);
    if (iVar5 == 0) {
      uVar10 = uVar10 + uStack_2a & 0xffff;
      pcVar11 = &local_2b;
      if (param_3 != 'Z') {
LAB_0008d07c:
        *pcVar11 = 'Z';
        break;
      }
    }
    else {
      if (iVar5 != 3) {
        pcVar11 = &local_2c;
        if (iVar5 == 5) goto LAB_0008d07c;
        break;
      }
      if (param_3 != 'Z') {
        uVar2 = 0x5a;
        uVar3 = 0x31;
        goto LAB_0008d0bc;
      }
    }
    iVar5 = FUN_0008cfe8(cVar9,&local_2c,&local_2b,param_4);
    puVar4 = extraout_r9;
  } while (iVar5 == 0);
  uVar2 = 0;
  uVar3 = 0;
  if (local_2b == 'Z') {
LAB_0008d0bc:
    uVar7 = uVar3;
    uVar8 = uVar2;
    uVar6 = 0;
  }
  else if (local_2c == 'Z') {
    uVar6 = 10;
  }
  else {
    uVar6 = 1;
  }
  f33_dcm_snapshot_record_message.response_length = uVar10;
  DAT_febf4570 = uVar8;
  DAT_febf4571 = uVar7;
  DAT_febf456f = local_2b;
  return uVar6;
}



undefined4 FUN_0008d0e6(char *param_1,int param_2,int *param_3)

{
  uint uVar1;
  uint uVar2;
  
  uVar1 = (uint)(*((ushort *)camry_host_ptr((uint32_t)(param_2 + 2))));
  if ((*param_1 != 'Z') || (*(ushort *)param_3[1] < 5)) {
    if ((param_1[3] != 'Z') || (uVar1 < 8)) {
      if (*param_1 == 'Z') {
        return 0;
      }
      if (param_1[3] != 'Z') {
        *(char *)param_3[3] = param_1[2];
        return 1;
      }
    }
    if ((*((int *)camry_host_ptr((uint32_t)(param_2 + 4)))) != 0) {
      uVar2 = 0;
      if (3 < uVar1) {
        uVar2 = uVar1 - 3 & 0xffff;
      }
      for (uVar1 = 0; uVar1 < uVar2; uVar1 = uVar1 + 1 & 0xffff) {
        (*((undefined1 *)camry_host_ptr((uint32_t)(*param_3 + uVar1)))) = (*((undefined1 *)camry_host_ptr((uint32_t)(*(int *)(param_2 + 4) + uVar1 + 3))));
      }
      *(short *)param_3[1] = (short)uVar2;
    }
  }
  return 0;
}



uint FUN_0008d366(void)

{
  uint uVar1;
  int iVar2;
  uint uVar3;
  uint uVar4;
  uint uVar5;
  uint uVar6;
  
  uVar3 = 0;
  FUN_0009560e(0);
  uVar6 = 0;
  uVar5 = 0;
  uVar4 = 0;
  FUN_000955b6(0);
  if (f33_dcm_snapshot_record_message.request_length == 4) {
    if (3 < f33_dcm_snapshot_record_message.response_capacity) {
      uVar6 = (uint)((uint8_t *)camry_host_ptr((uint32_t)(f33_dcm_snapshot_record_message.request)))[2] |
              (uint)((uint8_t *)camry_host_ptr((uint32_t)(f33_dcm_snapshot_record_message.request)))[1] << 8 |
              (uint)*((uint8_t *)camry_host_ptr((uint32_t)(f33_dcm_snapshot_record_message.request))) << 0x10;
      uVar1 = (uint)((uint8_t *)camry_host_ptr((uint32_t)(f33_dcm_snapshot_record_message.request)))[3];
      if (uVar1 == 0xff) {
        uVar4 = 0x5a;
        uVar1 = uVar5;
      }
      FUN_000955b6(1);
      iVar2 = FUN_0008d15e(uVar6,uVar1,uVar4);
      if (iVar2 == 10) {
        uVar3 = 10;
        uVar5 = uVar1;
      }
      else {
        uVar3 = 0;
        f33_fill_constant_block_8cef0();
        FUN_000955b6(0);
        uVar4 = uVar3;
        uVar5 = uVar3;
        uVar6 = uVar3;
      }
    }
  }
  else {
    f33_dcm_report_negative_or_pending(((F33DcmMessageContext *)camry_host_ptr((uint32_t)((0xfebf457cu)))), '\x13');
  }
  DAT_febf4564 = uVar6;
  DAT_febf4573 = (char)uVar5;
  DAT_febf4574 = (char)uVar4;
  return uVar3;
}



void FUN_0008d3fa(void)

{
  f33_dcm_cancel_service_events(0xef,'\0');
  FUN_0009560e(1);
  f33_fill_constant_block_8cef0();
  return;
}



/* Snapshot records operation callback. Retain advanced message for operation0; nonzero operations
   reset/cancel module state. Response submission is not acknowledgement or durable completion.
   Exact capacity4 path reaches95626 with NRC0 and consequently submits a positive header-only
   response through CanTp length acceptance; not NRC14 or a transmitted negative response. */

uint f33_dcm_read_snapshot_by_dtc_service(uchar operation,F33DcmMessageContext *message)

{
  uint uVar1;
  
  f33_dcm_snapshot_record_message.request = message->request;
  f33_dcm_snapshot_record_message.request_length = message->request_length;
  f33_dcm_snapshot_record_message.response = message->response;
  f33_dcm_snapshot_record_message.response_length = message->response_length;
  f33_dcm_snapshot_record_message.addressing_kind = message->addressing_kind;
  f33_dcm_snapshot_record_message.suppress_positive = message->suppress_positive;
  f33_dcm_snapshot_record_message.response_capacity = message->response_capacity;
  f33_dcm_snapshot_record_message.service_id = message->service_id;
  f33_dcm_snapshot_record_message.service_list_selector = message->service_list_selector;
  if (operation == '\0') {
    uVar1 = FUN_0008d366();
  }
  else {
    uVar1 = 0;
    FUN_0008d3fa();
  }
  return uVar1;
}



/* EventEF polls8D15E with retained4564/4573/4574. Result10 retains them; other results reset the
   snapshot module through8CEF0 and clear those retained inputs. */

void f33_dcm_resume_queued_snapshot_record(void)

{
  int iVar1;
  undefined4 uVar2;
  undefined1 uVar3;
  undefined1 uVar4;
  
  uVar3 = DAT_febf4574;
  uVar4 = DAT_febf4573;
  uVar2 = DAT_febf4564;
  iVar1 = FUN_0008d15e(DAT_febf4564,DAT_febf4573,DAT_febf4574);
  if (iVar1 != 10) {
    f33_fill_constant_block_8cef0();
    uVar2 = 0;
    uVar4 = 0;
    uVar3 = 0;
  }
  DAT_febf4564 = uVar2;
  DAT_febf4573 = uVar4;
  DAT_febf4574 = uVar3;
  return;
}



void FUN_0008d4ae(void)

{
  DAT_febf459a = 0;
  DAT_febf4599 = 1;
  DAT_febf4598 = 1;
  DAT_febf459b = 0xff;
  return;
}



/* Far-call trampoline: prepare {lp},0 / jarl 0x8D4AE / dispose 0,{lp},lp; byte-verified against the
   exact image. Forwards with registers and stack unchanged; marked as a thunk. Forwarding shape
   machine-verified; target semantics not recovered. */

void thunk_FUN_0008d4ae(void)

{
  FUN_0008d4ae();
  return;
}



undefined4 FUN_0008d4e0(char param_1)

{
  if ((param_1 != '\x01') && (param_1 != '\x03' && param_1 != '\x04')) {
    return 0;
  }
  return 0x31;
}



undefined4
FUN_0008d546(undefined4 param_1,byte param_2,undefined4 param_3,uint param_4,uchar *param_5,
            undefined1 *param_6)

{
  ushort length;
  undefined1 uVar1;
  undefined4 uVar2;
  int iVar3;
  uint uVar4;
  uint uVar5;
  undefined1 uStack_3d;
  uchar *apuStack_3c [3];
  undefined1 *puStack_30;
  undefined1 auStack_2c [2];
  ushort uStack_2a;
  undefined4 uStack_28;
  byte bStack_22;
  undefined1 uStack_21;
  undefined1 uStack_20;
  undefined1 uStack_1f;
  undefined1 uStack_1e;
  undefined1 uStack_1d;
  
  uVar5 = (uint)DAT_febf4598;
  uVar4 = (uint)DAT_febf4599;
  uStack_3d = DAT_febf459b;
  uStack_1e = (undefined1)param_3;
  bStack_22 = param_2 & 0xf;
  iVar3 = (int)(uint)param_2 >> 4;
  uStack_21 = (undefined1)((uint)param_3 >> 0x18);
  uStack_20 = (undefined1)((uint)param_3 >> 0x10);
  uStack_1f = (undefined1)((uint)param_3 >> 8);
  uStack_1d = (undefined1)param_4;
  length = (ushort)param_4;
  if (DAT_febf459a == '\0') {
    if (iVar3 == 0) {
      uVar5 = f33_read_configured_application_memory(&bStack_22,param_5,length);
LAB_0008d59e:
      uVar4 = 1;
LAB_0008d61a:
      if (uVar5 != 2) {
LAB_0008d61e:
        auStack_2c[0] = (undefined1)uVar5;
        if (uVar4 != 2) goto LAB_0008d622;
      }
      DAT_febf459a = 2;
      DAT_febf4599 = (byte)uVar4;
      DAT_febf4598 = (byte)uVar5;
      uVar2 = 1;
      goto LAB_0008d656;
    }
    uVar5 = 1;
    if (iVar3 != 1) goto LAB_0008d59e;
    if (param_4 < 5) {
      uVar4 = ((void)(0x48000000), (void)(2), (void)(6), (void)(&bStack_22), (void)(&uStack_3d), f33_return_const_0_8b10c());
      goto LAB_0008d61e;
    }
    *param_6 = 0x31;
    uVar1 = 1;
LAB_0008d5d4:
    auStack_2c[0] = uVar1;
    uVar2 = 0;
  }
  else {
    if (DAT_febf459a == '\x02') {
      if (iVar3 == 0) {
        if (uVar5 == 2) {
          uVar5 = f33_read_configured_application_memory(&bStack_22,param_5,length);
        }
      }
      else {
        uVar5 = 1;
      }
      if (iVar3 != 1) goto LAB_0008d59e;
      if (uVar4 == 2) {
        uVar4 = ((void)(1), (void)(2), (void)(uStack_3d), f33_return_const_0_8b110());
      }
      goto LAB_0008d61a;
    }
    auStack_2c[0] = 1;
    uVar4 = 1;
LAB_0008d622:
    uVar1 = (char)uVar4;
    if (iVar3 == 1) goto LAB_0008d5d4;
    uVar2 = 0x5a;
  }
  uStack_28 = 0;
  apuStack_3c[0] = param_5;
  puStack_30 = param_6;
  uStack_2a = length;
  uVar2 = FUN_0008d4f6(uVar2,auStack_2c,apuStack_3c);
  DAT_febf4598 = 1;
  DAT_febf4599 = 1;
  DAT_febf459a = 0;
  uStack_3d = 0xff;
LAB_0008d656:
  DAT_febf459b = uStack_3d;
  DAT_febf459c = (char)iVar3;
  return uVar2;
}



/* Zerochallenge495A[16],copy496A[16],client497A[16],active4958/result4959. Calledstartup, every
   session notification4D582 and fullapplicationdiagnostic reset8E62A.
   Genericdelaybits/failures/securitybitmap areseparate. */

void f33_app_security_reset_challenge_material(void)

{
  uint uVar1;
  
  uVar1 = 0;
  do {
    f33_app_security_challenge[uVar1] = '\0';
    f33_app_security_challenge_duplicate[uVar1] = '\0';
    f33_app_security_client_material[uVar1] = '\0';
    uVar1 = uVar1 + 1;
  } while (uVar1 < 0x10);
  f33_app_security_challenge_active = '\0';
  f33_app_security_comparison_result = '\0';
  return;
}



void FUN_0008d6a4(void)

{
  f33_app_security_reset_challenge_material();
  return;
}



/* WARNING: Inlined function: f33_read_inverted_profile_counter */
/* For floor(low8(length)/2) iterations sample64E2A and write low16 big-endian; leave an odd
   trailing byte untouched.8D74A uses16 bytes as candidate challenge material. Same counter as
   profiler, independent of31910 profiling gate. No entropy-quality or hardware-timer execution
   claim. */

void f33_fill_counter_sample_pairs(uchar *output,uchar length)

{
  uint uVar1;
  uint uVar2;
  
  for (uVar2 = (uint)(length >> 1); uVar2 != 0; uVar2 = uVar2 - 1) {
    uVar1 = DAT_ffe51010;
    *output = (uchar)(~uVar1 >> 8);
    output[1] = (uchar)~uVar1;
    output = output + 2;
  }
  return;
}



/* Up to2 timer-derived candidates: sample16 bytes, initializeCTR(timerkey,counter0),
   outputAES_timerkey(0), reinitializeCTR(output,currentcounter1), then outputAES_output(1).
   Clear228-byteCTRcontext4A50. Exclusion checkzero/FF and activehistory496A. If
   transformedcandidates fail, rawlasttimerkey is ALSO checked; accepted raw fallback
   updateschallenge/copy/active. Unlike resident6F22, invalid raw fallback returns failure rather
   than unconditionalsuccess. A prior library-failure marker isnotreseton retry, so not every second
   attempt is independent. */

uint f33_app_security_generate_challenge(uchar *seed_out)

{
  uchar *puVar1;
  uchar *puVar2;
  uint uVar3;
  uint uVar4;
  int iVar5;
  int iVar6;
  int iVar7;
  int iVar8;
  uint uVar9;
  uchar local_30 [16];
  
  uVar9 = 0;
  iVar6 = 0xff;
  iVar8 = 0;
  iVar7 = 2;
  do {
    f33_fill_counter_sample_pairs(local_30,'\x10');
    FUN_00085940(camry_host_addr(local_30), 0x10, (0xfebf4a50u));
    iVar5 = FUN_00085964(camry_host_addr(seed_out), (0xfebf4a50u));
    if (iVar5 == 0) {
      iVar6 = FUN_0008597c(camry_host_addr(seed_out), 0x10, (0xfebf4a50u));
    }
    else {
      iVar8 = 0xff;
    }
    if ((iVar6 == 0) && (iVar8 == 0)) {
      iVar8 = FUN_00085964(camry_host_addr(seed_out), (0xfebf4a50u));
    }
    else {
      iVar8 = 0xff;
    }
    FUN_000859a8(((undefined4 *)camry_host_ptr((uint32_t)((0xfebf4a50u)))));
  } while (((iVar8 != 0) || (uVar9 = FUN_0008d6d6(camry_host_addr(seed_out)), uVar9 == 0)) &&
          (iVar7 = iVar7 + -1, iVar7 != 0));
  if (uVar9 != 0x5a) {
    uVar9 = 0;
    do {
      puVar1 = local_30 + uVar9;
      puVar2 = seed_out + uVar9;
      uVar9 = uVar9 + 1;
      *puVar2 = *puVar1;
    } while (uVar9 < 0x10);
    uVar9 = FUN_0008d6d6(camry_host_addr(seed_out));
    if (uVar9 != 0x5a) {
      return uVar9;
    }
  }
  uVar4 = 0;
  do {
    uVar3 = uVar4 + 1;
    f33_app_security_challenge[uVar4] = seed_out[uVar4];
    f33_app_security_challenge_duplicate[uVar4] = seed_out[uVar4];
    uVar4 = uVar3;
  } while (uVar3 < 0x10);
  f33_app_security_challenge_active = 'Z';
  return uVar9;
}



/* Always copy16 client bytes to497A. If4958==0 or retainedchallenge allzero generate8D74A;
   failureNRC22. Otherwise copyexisting challenge495A toseed_out unchanged. Delay/current-security
   gating occurs later96692. No CMAC or ICU-S ownership. */

uint f33_app_security_prepare_seed(uchar *client_material,uchar *seed_out,uchar *negative_response)

{
  uchar *puVar1;
  uchar *puVar2;
  uint uVar3;
  uchar uVar4;
  int iVar5;
  uint uVar6;
  
  uVar4 = f33_app_security_challenge_active;
  uVar6 = 0;
  do {
    uVar3 = uVar6 + 1;
    f33_app_security_client_material[uVar6] = client_material[uVar6];
    uVar6 = uVar3;
  } while (uVar3 < 0x10);
  if (uVar4 == '\0') {
LAB_0008d872:
    uVar6 = f33_app_security_generate_challenge(seed_out);
    if (uVar6 == 0x5a) {
LAB_0008d8a6:
      uVar6 = 0;
    }
    else {
      uVar6 = 1;
      *negative_response = '\"';
    }
    return uVar6;
  }
  iVar5 = 0x5a;
  uVar6 = 0;
LAB_0008d856:
  if (f33_app_security_challenge[uVar6] != '\0') {
    iVar5 = 0;
  }
  if (iVar5 == 0x5a) goto code_r0x0008d868;
  uVar6 = 0;
  do {
    puVar1 = f33_app_security_challenge + uVar6;
    puVar2 = seed_out + uVar6;
    uVar6 = uVar6 + 1;
    *puVar2 = *puVar1;
  } while (uVar6 < 0x10);
  goto LAB_0008d8a6;
code_r0x0008d868:
  uVar6 = uVar6 + 1 & 0xff;
  if (0xf < uVar6) goto LAB_0008d872;
  goto LAB_0008d856;
}



/* Software AES128 single-block DECRYPT underROM20840 key, via876C4/864DE in shared196-byte498C
   context; clearcontext87AC2 thenreturnstatus. */

uint f33_app_security_decrypt_client_material(uchar *client_material,uchar *intermediate_key)

{
  uint uVar1;
  
  FUN_000876c4(f33_app_security_client_decryption_key, 0x10, ((uint *)camry_host_ptr((uint32_t)((0xfebf498cu)))));
  uVar1 = FUN_000864de(client_material, intermediate_key, 0x10, ((uint *)camry_host_ptr((uint32_t)((0xfebf498cu)))));
  FUN_00087ac2(((undefined4 *)camry_host_ptr((uint32_t)((0xfebf498cu)))));
  return uVar1;
}



/* Software AES128 single-block ENCRYPT via876C4/863A0 inshared498C context;
   clearentire196-bytecontext afterward. No SecOC secret, CMAC or hardwarecrypto command is used. */

uint f33_app_security_encrypt_challenge
               (uchar *intermediate_key,uchar *challenge,uchar *expected_key)

{
  uint uVar1;
  
  FUN_000876c4(intermediate_key, 0x10, ((uint *)camry_host_ptr((uint32_t)((0xfebf498cu)))));
  uVar1 = FUN_000863a0(challenge,expected_key,0x10,(0xfebf498cu));
  FUN_00087ac2(((undefined4 *)camry_host_ptr((uint32_t)((0xfebf498cu)))));
  return uVar1;
}



/* Require active4958==5A; derive intermediate=AES128_DECRYPT(ROM20840,497A),
   expected=AES128_ENCRYPT(intermediate,495A). Early-exit16-byte compare returnsB on firstmismatch.
   Success clears495A/496A andactive4958, retains497A; publishesresult4959. Doesnotpublish security
   itself, which96788 doesnext. Stackintermediate/expected notwiped. */

uint f33_app_security_compare_key(uchar *submitted_key)

{
  uint uVar1;
  uint uVar2;
  uchar auStack_34 [16];
  uchar auStack_24 [16];
  
  uVar2 = 0xb;
  if ((f33_app_security_challenge_active == 'Z') &&
     (uVar1 = f33_app_security_decrypt_client_material(f33_app_security_client_material,auStack_24),
     uVar1 == 0)) {
    uVar2 = f33_app_security_encrypt_challenge(auStack_24,f33_app_security_challenge,auStack_34);
    if (uVar2 == 0) {
      uVar1 = 0;
      uVar2 = 0;
      do {
        if (submitted_key[uVar1] != auStack_34[uVar1]) {
          uVar2 = 0xb;
        }
        uVar1 = uVar1 + 1 & 0xff;
        if (uVar2 != 0) goto LAB_0008d998;
      } while (uVar1 < 0x10);
      uVar1 = 0;
      do {
        f33_app_security_challenge[uVar1] = '\0';
        f33_app_security_challenge_duplicate[uVar1] = '\0';
        uVar1 = uVar1 + 1;
      } while (uVar1 < 0x10);
      f33_app_security_challenge_active = '\0';
    }
    else {
      uVar2 = 0xb;
    }
  }
LAB_0008d998:
  f33_app_security_comparison_result = (uchar)uVar2;
  return uVar2;
}



uchar FUN_0008d9a2(void)

{
  return f33_app_security_comparison_result;
}



void FUN_0008d9ac(void)

{
  f33_app_security_comparison_result = '\0';
  return;
}



uchar FUN_0008d9b6(void)

{
  uchar uStack_5;
  
  f33_dcm_get_security_level(&uStack_5);
  return uStack_5;
}



void FUN_0008d9ca(void)

{
  f33_dcm_communication_local_state.last_tx_disable_bit = '\0';
  f33_dcm_communication_local_state.last_mapped_mode = '\0';
  f33_dcm_communication_local_state.retained_subnet = '\0';
  f33_dcm_communication_local_state.action_state = '\0';
  f33_dcm_communication_local_state.lower_status = '\0';
  f33_dcm_communication_local_state.application_status = '\0';
  f33_dcm_communication_local_state.admission_result = '\x01';
  f33_dcm_communication_local_state.side_status = 0xff;
  return;
}



/* Idle45A0andE892<=384 admit;busy/strictunsignedgreaterreject22.
   Stagehighnibbleandactionstate;459Drecordsadmission. */

uint f33_admit_application_communication_request
               (uchar subfunction,uchar communication_type,ushort node,uchar *nrc)

{
  uint uVar1;
  byte bVar2;
  
  bVar2 = f33_dcm_communication_local_state.retained_subnet;
  if (f33_dcm_communication_local_state.action_state == '\0') {
    bVar2 = communication_type >> 4;
    uVar1 = f33_communication_request_sample_above_limit();
    f33_dcm_communication_local_state.action_state = uVar1 != 1;
    if ((bool)f33_dcm_communication_local_state.action_state) {
      uVar1 = 0;
      goto LAB_0008da52;
    }
  }
  uVar1 = 1;
  *nrc = '\"';
LAB_0008da52:
  f33_dcm_communication_local_state.admission_result = (uchar)uVar1;
  f33_dcm_communication_local_state.retained_subnet = bVar2;
  return uVar1;
}



/* WARNING: Inlined function: f33_diag_routine_local_dispatch_enabled */
/* WARNING: Removing unreachable block (ram,0x0008dab2) */
/* RealR10merge status;state1loweradapterisexactreturn0,dispatchgatefixed5A,then4FD18publishes8196.
   Retainlastmappedmode/bit0aftercompletion. */

uint f33_apply_and_complete_communication_policy_request(uchar channel,uchar mapped_mode)

{
  uchar lower_status;
  uint uVar1;
  uchar network_selector;
  byte disable_tx;
  uchar uVar2;
  uchar application_status;
  uchar uStack_23;
  uchar uStack_22;
  byte bStack_21;
  
  network_selector = f33_dcm_communication_local_state.retained_subnet;
  uVar2 = f33_dcm_communication_local_state.action_state;
  application_status = f33_dcm_communication_local_state.application_status;
  disable_tx = mapped_mode & 1;
  uStack_23 = f33_dcm_communication_local_state.side_status;
  if (f33_dcm_communication_local_state.action_state == '\x01') {
    uVar2 = '\x02';
    uStack_22 = f33_dcm_communication_local_state.retained_subnet;
    bStack_21 = disable_tx;
    lower_status = ((void)(0x60000001), (void)(10), (void)(2), (void)(&uStack_22), (void)(&uStack_23), f33_return_const_0_8b10c());
  }
  else {
    if (f33_dcm_communication_local_state.action_state != '\x02') {
      application_status = '\0';
      lower_status = '\0';
      goto LAB_0008daea;
    }
    lower_status = f33_dcm_communication_local_state.lower_status;
    if (f33_dcm_communication_local_state.lower_status == '\n') {
      lower_status = ((void)(0), (void)(10), f33_return_const_0_8b110());
    }
    if (application_status != '\n') goto LAB_0008daea;
  }
  f33_publish_diagnostic_normal_tx_policy_request(network_selector,disable_tx);
  application_status = '\0';
LAB_0008daea:
  uVar1 = f33_merge_two_diagnostic_statuses(application_status,lower_status,'\0','\n');
  if (uVar1 != 10) {
    uVar1 = 0;
    application_status = '\0';
    lower_status = '\0';
    uVar2 = '\0';
    network_selector = '\0';
    uStack_23 = 0xff;
  }
  f33_dcm_communication_local_state.application_status = application_status;
  f33_dcm_communication_local_state.lower_status = lower_status;
  f33_dcm_communication_local_state.action_state = uVar2;
  f33_dcm_communication_local_state.retained_subnet = network_selector;
  f33_dcm_communication_local_state.side_status = uStack_23;
  f33_dcm_communication_local_state.last_mapped_mode = mapped_mode;
  f33_dcm_communication_local_state.last_tx_disable_bit = disable_tx;
  return uVar1;
}



/* Constant-block fill: 9 literal assignments into one contiguous cell block; shape-verified.
   Literals are default/reset values; cell meanings are not recovered. */

void f33_fill_constant_block_8db22(void)

{
  DAT_febf45ae = 1;
  DAT_febf45ad = 1;
  DAT_febf45ac = 0;
  DAT_febf45ab = 0;
  DAT_febf45aa = 0;
  DAT_febf45a8 = 0;
  DAT_febf45a9 = 0xff;
  DAT_febf45b0 = 1;
  DAT_febf45af = 1;
  return;
}



void FUN_0008db70(void)

{
  f33_dcm_cancel_service_events(0xf0,'\0');
  FUN_0009560e(1);
  f33_fill_constant_block_8db22();
  return;
}



/* WARNING: Inlined function: f33_diag_routine_local_dispatch_enabled */

undefined1 FUN_0008db8c(F33DcmMessageContext *param_1)

{
  uchar lower_status;
  uchar application_status;
  uint uVar1;
  undefined1 uVar2;
  bool bVar3;
  undefined1 uStack_1e;
  undefined1 uStack_1d;
  
  application_status = DAT_febf45ad;
  uStack_1d = DAT_febf45a9;
  if (DAT_febf45ac == '\0') {
    DAT_febf45aa = 0;
    DAT_febf45ab = 0;
    uStack_1e = DAT_febf45a8;
    lower_status = ((void)((int)0xc0000000), (void)(2), (void)(1), (void)(&uStack_1e), (void)(&uStack_1d), f33_return_const_0_8b10c());
  }
  else {
    if (DAT_febf45ac != '\x01') {
      return 0;
    }
    lower_status = DAT_febf45ae;
    if (DAT_febf45ae == '\x02') {
      lower_status = ((void)(0), (void)(2), f33_return_const_0_8b110());
    }
    if (application_status != '\x02') goto LAB_0008dc0c;
  }
  application_status = ((void)(0xffffff), (void)(1), f33_return_const_0_50900());
LAB_0008dc0c:
  bVar3 = true;
  uVar1 = f33_merge_two_diagnostic_statuses(application_status,lower_status,'\0','\x02');
  if (uVar1 == 2) {
    f33_dcm_post_service_event(0xf0);
    uVar2 = 10;
  }
  else {
    application_status = '\x01';
    lower_status = '\x01';
    uVar2 = uVar1 != 0;
    if ((bool)uVar2) {
      f33_dcm_report_negative_or_pending(param_1,'\"');
    }
    bVar3 = !(bool)uVar2;
    DAT_febf45aa = 0x5a;
  }
  DAT_febf45ad = application_status;
  DAT_febf45ae = lower_status;
  DAT_febf45ac = bVar3;
  DAT_febf45a9 = uStack_1d;
  return uVar2;
}



undefined4 FUN_0008dc60(void)

{
  uchar selection;
  
  if (DAT_febf45a8 == '\x01') {
    selection = '\x01';
  }
  else {
    selection = '\x02';
  }
  f33_publish_dtc_setting_request(selection);
  return 0;
}



/* WARNING: Inlined function: f33_diag_routine_local_dispatch_enabled */
/* WARNING: Removing unreachable block (ram,0x0008dccc) */

undefined1 FUN_0008dc7c(F33DcmMessageContext *param_1)

{
  uchar lower_status;
  uchar application_status;
  uint uVar1;
  undefined1 uVar2;
  char cVar3;
  undefined1 uStack_1e;
  undefined1 uStack_1d;
  
  application_status = DAT_febf45af;
  cVar3 = DAT_febf45ac;
  uStack_1d = DAT_febf45a9;
  if (DAT_febf45ac == '\x01') {
    uStack_1e = DAT_febf45a8;
    cVar3 = '\x02';
    lower_status = ((void)((int)0xc0000001), (void)(2), (void)(1), (void)(&uStack_1e), (void)(&uStack_1d), f33_return_const_0_8b10c());
  }
  else {
    if (DAT_febf45ac != '\x02') {
      application_status = '\x01';
      lower_status = '\x01';
      goto LAB_0008dd00;
    }
    lower_status = DAT_febf45b0;
    if (DAT_febf45b0 == '\x02') {
      lower_status = ((void)(0), (void)(2), f33_return_const_0_8b110());
    }
    if (application_status != '\x02') goto LAB_0008dd00;
  }
  application_status = ((void)(uStack_1d), FUN_0008dc60());
LAB_0008dd00:
  uVar1 = f33_merge_two_diagnostic_statuses(application_status,lower_status,'\0','\x02');
  if (uVar1 == 2) {
    f33_dcm_post_service_event(0xf0);
    uVar2 = 10;
  }
  else {
    application_status = '\x01';
    lower_status = '\x01';
    cVar3 = '\0';
    uVar2 = uVar1 != 0;
    if ((bool)uVar2) {
      f33_dcm_report_negative_or_pending(param_1,'\"');
    }
    else {
      f33_dcm_report_positive_response(param_1);
    }
    DAT_febf45ab = 0x5a;
  }
  DAT_febf45af = application_status;
  DAT_febf45b0 = lower_status;
  DAT_febf45ac = cVar3;
  DAT_febf45a9 = uStack_1d;
  return uVar2;
}



void FUN_0008dd54(undefined4 param_1)

{
  int iVar1;
  
  iVar1 = FUN_0008db8c(((F33DcmMessageContext *)camry_host_ptr((uint32_t)(param_1))));
  if (iVar1 == 0) {
    FUN_0008dc7c(((F33DcmMessageContext *)camry_host_ptr((uint32_t)(param_1))));
  }
  return;
}



/* Operation0 forwards fixed selection1 and requires zero remaining bytes; other operations reset
   module continuation. Application action clears8197, not stored diagnostic histories. */

uint f33_dcm_enable_dtc_setting_service(uchar operation,F33DcmMessageContext *message)

{
  uint uVar1;
  
  if (operation == '\0') {
    uVar1 = FUN_0008dd6c(1, message);
  }
  else {
    uVar1 = 0;
    FUN_0008db70();
  }
  return uVar1;
}



/* Operation0 forwards fixed selection2 and requires zero remaining bytes; other operations reset
   continuation. Application action requests8197=5A; grouped status propagation occurs later. */

uint f33_dcm_disable_dtc_setting_service(uchar operation,F33DcmMessageContext *message)

{
  uint uVar1;
  
  if (operation == '\0') {
    uVar1 = FUN_0008dd6c(2, message);
  }
  else {
    uVar1 = 0;
    FUN_0008db70();
  }
  return uVar1;
}



/* EventF0 re-enters8DD54 with retained28-byte message45B4. */

void f33_dcm_resume_queued_dtc_setting(void)

{
  FUN_0008dd54((0xfebf45b4u));
  return;
}



/* Constant-block fill: 13 literal assignments into one contiguous cell block; shape-verified.
   Literals are default/reset values; cell meanings are not recovered. */

void f33_fill_constant_block_8de1a(void)

{
  DAT_febf45d6 = 0x300;
  DAT_febf45d4 = 0;
  DAT_febf45dd = 1;
  DAT_febf45d2 = 0;
  DAT_febf45d0 = 0;
  DAT_febf45dc = 0;
  DAT_febf45e3 = 1;
  DAT_febf45e2 = 0xff;
  DAT_febf45e1 = 0;
  DAT_febf45e0 = 0;
  DAT_febf45d8 = 0;
  DAT_febf45df = 1;
  DAT_febf45de = 0;
  return;
}



/* Retain bounded selector/IDs at45D0/45D2/45DC and publish selection through50916. IDs index event
   data catalogue, not callback addresses. */

uint f33_begin_proprietary_event_selection
               (uchar operation,uchar selector,ushort event_id,ushort subselector)

{
  DAT_febf45d0 = event_id;
  DAT_febf45d2 = subselector;
  DAT_febf45dc = selector;
  FUN_00050916((uint)(byte)selector, (uint)(ushort)event_id, (uint)(ushort)subselector);
  return 0;
}



undefined4 FUN_0008debe(char param_1)

{
  if (param_1 == '\x04') {
    return 0x31;
  }
  if (param_1 != '\x06') {
    if (param_1 != '\n') {
      return 0;
    }
    return 0x10;
  }
  return 0x14;
}



undefined4 FUN_0008dee2(char *param_1,char *param_2,int *param_3)

{
  int iVar1;
  short sVar2;
  uint uVar3;
  uint uVar4;
  uint uVar5;
  uint uVar6;
  uint uVar7;
  undefined1 local_4 [4];
  
  uVar7 = 0;
  uVar6 = 0;
  sVar2 = *(short *)(param_2 + 2);
  uVar3 = 0;
  uVar4 = 0;
  do {
    local_4[uVar4] = 0;
    uVar5 = uVar4 + 1;
    local_4[uVar4 + 2] = 0;
    uVar4 = uVar5;
  } while (uVar5 < 2);
  if ((*param_1 != '\0') && (*param_2 != '\0')) {
    return 0;
  }
  if (*(short *)(param_1 + 2) == 0) {
    uVar4 = 0xffffffff;
  }
  else {
    uVar4 = 0;
  }
  if (sVar2 == 0) {
    uVar5 = 0xffffffff;
    goto LAB_0008dfe2;
  }
  uVar5 = 0;
  do {
    if (uVar4 != 0) goto LAB_0008df46;
LAB_0008df24:
    if (uVar7 < *(ushort *)(param_1 + 2)) {
      local_4[0] = (*((undefined1 *)camry_host_ptr((uint32_t)(*(int *)(param_1 + 4) + uVar7))));
      local_4[1] = (((undefined1 *)camry_host_ptr((uint32_t)(*(int *)(param_1 + 4) + uVar7))))[1];
      uVar4 = (uint)CONCAT11(local_4[0],local_4[1]);
    }
    else {
      uVar4 = 0xffffffff;
    }
LAB_0008df46:
    if (uVar5 == 0) {
      if (uVar6 < *(ushort *)(param_2 + 2)) {
        local_4[2] = (*((undefined1 *)camry_host_ptr((uint32_t)(*(int *)(param_2 + 4) + uVar6))));
        local_4[3] = (((undefined1 *)camry_host_ptr((uint32_t)(*(int *)(param_2 + 4) + uVar6))))[1];
        uVar5 = (uint)CONCAT11(local_4[2],local_4[3]);
      }
      else {
        uVar5 = 0xffffffff;
      }
    }
    if (uVar4 <= uVar5) {
      if (uVar5 <= uVar4) {
        if (uVar4 != 0xffffffff) {
          uVar7 = uVar7 + 2 & 0xffff;
          (*((undefined1 *)camry_host_ptr((uint32_t)(*param_3 + uVar3)))) = local_4[0];
          iVar1 = *param_3 + uVar3;
          uVar3 = uVar3 + 2 & 0xffff;
          uVar6 = uVar6 + 2 & 0xffff;
          (*((undefined1 *)camry_host_ptr((uint32_t)(iVar1 + 1)))) = local_4[1];
          uVar5 = 0;
          goto LAB_0008df24;
        }
        goto LAB_0008dfe6;
      }
      (*((undefined1 *)camry_host_ptr((uint32_t)(*param_3 + uVar3)))) = local_4[0];
      iVar1 = *param_3 + uVar3;
      uVar3 = uVar3 + 2 & 0xffff;
      uVar7 = uVar7 + 2 & 0xffff;
      (*((undefined1 *)camry_host_ptr((uint32_t)(iVar1 + 1)))) = local_4[1];
      goto LAB_0008df24;
    }
    uVar6 = uVar6 + 2 & 0xffff;
    (*((undefined1 *)camry_host_ptr((uint32_t)(*param_3 + uVar3)))) = local_4[2];
    iVar1 = *param_3 + uVar3;
    uVar3 = uVar3 + 2 & 0xffff;
    (*((undefined1 *)camry_host_ptr((uint32_t)(iVar1 + 1)))) = local_4[3];
    uVar5 = 0;
LAB_0008dfe2:
    if (uVar4 == 0xffffffff) {
LAB_0008dfe6:
      if (uVar5 == 0xffffffff) {
        *(short *)param_3[1] = (short)uVar3;
        return 0;
      }
    }
  } while( true );
}



undefined4 FUN_0008dff6(byte *param_1,byte *param_2,int *param_3)

{
  ushort uVar1;
  uint uVar2;
  undefined4 uVar3;
  uint uVar4;
  ushort uVar5;
  
  uVar2 = (uint)*param_1;
  uVar4 = (uint)*param_2;
  uVar1 = *(ushort *)(param_1 + 2);
  uVar5 = *(ushort *)(param_2 + 2);
  if ((uVar2 == 0) && (uVar1 != 0)) {
LAB_0008e038:
    for (; uVar5 = uVar1, uVar2 < uVar1; uVar2 = uVar2 + 1 & 0xffff) {
      (*((undefined1 *)camry_host_ptr((uint32_t)(*param_3 + uVar2)))) = (*((undefined1 *)camry_host_ptr((uint32_t)(*(int *)(param_1 + 4) + uVar2))));
    }
  }
  else {
    if ((uVar4 != 0) || (uVar5 == 0)) {
      if (uVar2 == 0) goto LAB_0008e038;
      if (uVar4 != 0) {
        uVar3 = 1;
        *(byte *)param_3[3] = param_1[1];
        uVar5 = *(ushort *)(param_1 + 2);
        goto LAB_0008e06c;
      }
    }
    for (; uVar4 < uVar5; uVar4 = uVar4 + 1 & 0xffff) {
      (*((undefined1 *)camry_host_ptr((uint32_t)(*param_3 + uVar4)))) = (*((undefined1 *)camry_host_ptr((uint32_t)(*(int *)(param_2 + 4) + uVar4))));
    }
  }
  uVar3 = 0;
LAB_0008e06c:
  *(ushort *)param_3[1] = uVar5;
  return uVar3;
}



void FUN_0008e1e0(void)

{
  f33_dcm_proprietary_continuation.selected_index = '\0';
  f33_dcm_proprietary_continuation.side_result = '\x01';
  f33_dcm_proprietary_continuation.application_result = '\x01';
  f33_dcm_proprietary_continuation.phase = '\0';
  f33_dcm_proprietary_continuation.side_status = 0xff;
  return;
}



/* WARNING: Inlined function: f33_diag_routine_local_dispatch_enabled */
/* Start phase0 or poll phase1 with existing local/side status merge. Preserve selected index and
   module results;phase2 returns0 for the finish join without restarting the start action. */

uint f33_dcm_join_proprietary_start(F33DiagProprietaryMessage *message,uchar *selected_index)

{
  uint uVar1;
  uint uVar2;
  uchar lower_status;
  uchar uVar3;
  uint uVar4;
  uchar uVar5;
  uchar uStack_1d;
  
  uVar3 = f33_dcm_proprietary_continuation.application_result;
  uStack_1d = f33_dcm_proprietary_continuation.side_status;
  if (f33_dcm_proprietary_continuation.phase == '\0') {
    uVar4 = 0;
    do {
      uVar2 = message->request_length;
      uVar3 = '\0';
      if (uVar4 < (uVar2 & 0xff)) {
        uVar3 = ((uint8_t *)camry_host_ptr((uint32_t)(message->request)))[uVar4];
      }
      uVar1 = uVar4 + 1;
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebf48fcu + (uint32_t)(uVar4) * 1u)))) = uVar3;
      uVar4 = uVar1;
    } while (uVar1 < 0x40);
    lower_status = ((void)((int)0xe0000000), (void)(2), (void)(uVar2 & 0xffff), (void)(((undefined *)camry_host_ptr(0xfebf48fcu))), (void)(&uStack_1d), f33_return_const_0_8b10c());
  }
  else {
    if (f33_dcm_proprietary_continuation.phase != '\x01') {
      return 0;
    }
    lower_status = f33_dcm_proprietary_continuation.side_result;
    if (f33_dcm_proprietary_continuation.side_result == '\x02') {
      lower_status = ((void)(0x22), (void)(2), f33_return_const_0_8b110());
    }
    if (uVar3 != '\x02') goto LAB_0008e2ae;
  }
  uVar3 = f33_begin_proprietary_operation('\0',message,selected_index);
LAB_0008e2ae:
  uVar5 = '\x01';
  uVar4 = f33_merge_two_diagnostic_statuses(uVar3,lower_status,'\0','\x02');
  if ((uVar4 != 2) && (uVar3 = uVar5, lower_status = uVar5, uVar4 != 0)) {
    uVar5 = '\0';
  }
  f33_dcm_proprietary_continuation.application_result = uVar3;
  f33_dcm_proprietary_continuation.side_result = lower_status;
  f33_dcm_proprietary_continuation.phase = uVar5;
  f33_dcm_proprietary_continuation.side_status = uStack_1d;
  return uVar4;
}



/* WARNING: Inlined function: f33_diag_routine_local_dispatch_enabled */
/* WARNING: Removing unreachable block (ram,0x0008e33c) */
/* Join local fixed finish callback and exact side stub0. Preserve full mergeR10 through status
   stores and dispose; caller8E3A2 compares0/2/other for completion/pending/error. No fake side
   completion needed. */

uint f33_proprietary_operation_finish_join(uchar selected_index,uint *response_length)

{
  bool bVar1;
  uint uVar2;
  uchar uVar3;
  uchar lower_status;
  uchar application_status;
  uint uVar4;
  uchar uVar5;
  uchar uStack_1d;
  
  uVar3 = f33_dcm_proprietary_continuation.side_status;
  lower_status = f33_dcm_proprietary_continuation.side_result;
  application_status = f33_dcm_proprietary_continuation.application_result;
  uVar5 = f33_dcm_proprietary_continuation.phase;
  uStack_1d = f33_dcm_proprietary_continuation.side_status;
  uVar4 = 0;
  do {
    uVar2 = uVar4 + 1;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebf48fcu + (uint32_t)(uVar4) * 1u)))) = 0;
    uVar4 = uVar2;
  } while (uVar2 < 0x40);
  if (uVar5 == '\x01') {
    uVar5 = '\x02';
    lower_status = ((void)((int)0xe0000001), (void)(2), (void)(0), (void)(((undefined *)camry_host_ptr(0xfebf48fcu))), (void)(&uStack_1d), f33_return_const_0_8b10c());
  }
  else {
    if (uVar5 != '\x02') {
      application_status = '\x01';
      lower_status = '\x01';
      goto LAB_0008e376;
    }
    if (lower_status == '\x02') {
      lower_status = ((void)(0x22), (void)(2), (void)(uVar3), (void)(((undefined *)camry_host_ptr(0xfebf48fcu))), f33_return_const_0_8b110());
    }
    if (application_status != '\x02') goto LAB_0008e376;
  }
  application_status = f33_finish_proprietary_operation(selected_index,response_length);
LAB_0008e376:
  uVar4 = f33_merge_two_diagnostic_statuses(application_status,lower_status,'\0','\x02');
  bVar1 = uVar4 != 2;
  if (bVar1) {
    application_status = '\x01';
  }
  f33_dcm_proprietary_continuation.application_result = application_status;
  if (bVar1) {
    lower_status = '\x01';
  }
  f33_dcm_proprietary_continuation.side_result = lower_status;
  if (bVar1) {
    uVar5 = '\0';
  }
  f33_dcm_proprietary_continuation.phase = uVar5;
  f33_dcm_proprietary_continuation.side_status = uStack_1d;
  return uVar4;
}



/* Join retained proprietary start/finish state. Merged2 postsF1;0 echoes retained command and
   completes message;other statuses select negative response. Re-entry retains module state rather
   than restarting the application action. */

void f33_dcm_advance_proprietary_operation(F33DiagProprietaryMessage *message)

{
  uint uVar1;
  uchar uStack_11;
  uint uStack_10;
  
  uStack_10 = 0;
  uStack_11 = f33_dcm_proprietary_continuation.selected_index;
  uVar1 = f33_dcm_join_proprietary_start(message,&uStack_11);
  if (uVar1 == 0) {
    uVar1 = f33_proprietary_operation_finish_join(uStack_11,&uStack_10);
  }
  if (uVar1 == 2) {
    f33_dcm_post_service_event(0xf1);
  }
  else if (uVar1 == 0) {
    *((uint8_t *)camry_host_ptr((uint32_t)(message->response))) = *((uint8_t *)camry_host_ptr((uint32_t)(f33_dcm_proprietary_retained_message.request)));
    message->response_length = DAT_0002fc00 + uStack_10;
    f33_dcm_complete_proprietary_message(message);
  }
  else {
    f33_dcm_reject_proprietary_message(message,(uchar)uVar1);
  }
  f33_dcm_proprietary_continuation.selected_index = uStack_11;
  return;
}



/* Tombstone all queuedF1 slots and reset selected index, phase and module result bytes
   through8E1E0. Does not revoke BA application/requester ownership or undo an earlier record
   request. */

void f33_dcm_cancel_retained_proprietary_operation(void)

{
  f33_dcm_cancel_service_events(0xf1,'\0');
  FUN_0008e1e0();
  return;
}



/* Operation0 copies interpreted full-context fields to493C and first four words to
   existing16-byte48EC operation view, then enters8E3A2. Nonzero operations cancel queuedF1/module
   continuation without copying the incoming cleared main context. Return0; operation state is
   retained separately. */

uint f33_dcm_proprietary_operation_service(uchar operation,F33DcmMessageContext *message)

{
  if (operation == '\0') {
    f33_dcm_proprietary_retained_message.request = message->request;
    f33_dcm_proprietary_retained_message.request_length = message->request_length;
    f33_dcm_proprietary_retained_message.response = message->response;
    f33_dcm_proprietary_retained_message.response_length = message->response_length;
    f33_dcm_proprietary_retained_message.addressing_kind = message->addressing_kind;
    f33_dcm_proprietary_retained_message.suppress_positive = message->suppress_positive;
    f33_dcm_proprietary_retained_message.response_capacity = message->response_capacity;
    f33_dcm_proprietary_retained_message.service_id = message->service_id;
    f33_dcm_proprietary_retained_message.service_list_selector = message->service_list_selector;
    f33_diag_proprietary_message.request = message->request;
    f33_diag_proprietary_message.request_length = message->request_length;
    f33_diag_proprietary_message.response = message->response;
    f33_diag_proprietary_message.response_length = message->response_length;
    f33_dcm_advance_proprietary_operation(((F33DiagProprietaryMessage *)camry_host_ptr((uint32_t)((0xfebf48ecu)))));
  }
  else {
    f33_dcm_cancel_retained_proprietary_operation();
  }
  return 0;
}



/* EventF1 re-enters8E3A2 with existing16-byte proprietary operation view48EC. Its response length
   is separate from retained full DCM context493C; no new request/action is implied by this wrapper.
    */

void f33_dcm_resume_queued_proprietary_operation(void)

{
  f33_dcm_advance_proprietary_operation(((F33DiagProprietaryMessage *)camry_host_ptr((uint32_t)((0xfebf48ecu)))));
  return;
}



/* 8E4C0 savesdid,4C2 indexptr;13-entry table25640. Fullr10 cmp3 at4F0 re-enters SAME index at4CA
   via4F2; increments only4F6. Storesu16 index4FE. */

uint f33_find_write_did_and_check_precondition(ushort *matched_index,ushort did)

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
    uVar4 = (*(int (*)())*(code **)((short)uVar5 * 0xc + iVar3 + 0x1848))();
  } while (uVar4 == 3);
LAB_0008e4fe:
  *matched_index = (ushort)uVar5;
  return uVar4;
}



/* 8E50A..510 savesargs;3B25==2 bypassescallback, usescompletion withFF->2;elseboundedfixedcallback.
   Storeslateststatus8B7AE. */

uint f33_dispatch_or_poll_write_did_action
               (uchar completion_status,ushort matched_index,uchar *payload,ushort length)

{
  uint32_t puVar1;
  int iVar2;
  uint uVar3;
  
  uVar3 = (uint)completion_status;
  puVar1 = 0x23dfcu;
  iVar2 = FUN_0008b7a4();
  if (iVar2 == 2) {
    if (uVar3 == 0xff) {
      uVar3 = 2;
    }
  }
  else if ((matched_index < 0xd) && ((*((int *)camry_host_ptr((uint32_t)(puVar1 + (uint)matched_index * 0xc + 0x184c)))) != 0)) {
    uVar3 = (*(int (*)())*(code **)(puVar1 + (short)matched_index * 0xc + 0x184c))(payload,length);
  }
  else {
    uVar3 = 4;
  }
  FUN_0008b7ae(uVar3);
  return uVar3;
}



/* 8E566/56C retainu16RID;56E zxbcontrol;594 ld.hu original fifthargument;5A0 indirectcall
   row+4;5A4/A6 fullR10==3 re-enters sameindex;5AA only mismatch/null increments;5B4 writesu16index.
    */

uint f33_diag_routine_select_precondition
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
    uVar4 = (*(int (*)())*(code **)((short)uVar5 * 0xc + iVar3 + 0x18e4))(control_type,input,input_length);
  } while (uVar4 == 3);
LAB_0008e5b4:
  *callback_index = (ushort)uVar5;
  return uVar4;
}



/* 8E5C0/C2/C4 zxh/zxb/zxh;5C8 bounds19;5D6+5F6 row+8;5E2+5EC loadoriginalstackarg6/5
   andshuffle5argcallback;5FA indirectcall. Native dispatch through real callbacks verifies a stop
   request leaves the running result pending while setting cancellation, and a busy
   diagnostic-history owner queues a request without claiming completion. Other RIDs remain
   statically reconstructed. */

uint f33_diag_routine_dispatch_action
               (ushort callback_index,uchar control_type,uchar *input,ushort input_length,
               uchar *output,ushort *output_length)

{
  uint uVar1;
  
  uVar1 = 3;
  if ((callback_index < 0x13) && (f33_routine_callbacks[callback_index].action != 0x0u))
  {
    uVar1 = (*(int (*)())f33_routine_callbacks[(short)callback_index].action)(control_type,input,input_length,output,output_length);
  }
  return uVar1;
}



/* ZXB R6/R7/R8/R9 at8E602..608; choose pending if either input is pending, otherwise local failure
   or nonzero side result after local success. MOV R9,R10 at8E620 and JMP LP guarantee full
   zero-extended32 result0..255. */

uint f33_merge_two_diagnostic_statuses
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



/* WARNING: This is an inlined function */
/* Exactfunctionreturns5Aunconditionally;nominalside-statusargumentisignored. No status-dependent
   admission inferred. */

uint f33_diag_routine_local_dispatch_enabled(void)

{
  return 0x5a;
}



/* Sequential initializer chain: 16 unconditional calls and no other statements; shape-verified. The
   called sequence is the function's entire behavior; chain family members differ in callee sets. */

void f33_run_init_chain_8e62a(void)

{
  FUN_0008b070();
  FUN_0008b134();
  f33_fill_constant_block_8bfea();
  FUN_0008c318();
  FUN_0008c70c();
  f33_fill_constant_block_8cb8c();
  f33_fill_constant_block_8cef0();
  FUN_0008b3d4();
  FUN_0008d4ae();
  f33_app_security_reset_challenge_material();
  FUN_0008d9ca();
  f33_reset_write_did_transaction();
  f33_diag_reset_routine_class_state();
  f33_fill_constant_block_8db22();
  f33_fill_constant_block_8de1a();
  FUN_0008e1e0();
  return;
}



undefined4 FUN_0008e672(undefined1 param_1,undefined4 *param_2)

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
  } while ((uintptr_t)(param_2 + 7)!=(uintptr_t)(puVar1));
  DAT_febe52ac = *param_2;
  DAT_febe52b0 = param_2[1];
  DAT_febe52b4 = param_2[2];
  DAT_febe52b8 = param_2[3];
  ((void)(param_1), (void)(((undefined *)camry_host_ptr(0xfebe52acu))), f33_return_only_stub_4d4c2());
  return 0;
}



/* Copy proprietary operation response length to existing52C8, then complete the enclosing52BC DCM
   context. Completion readiness is not transport confirmation. */

void f33_dcm_complete_proprietary_message(F33DiagProprietaryMessage *message)

{
  DAT_febe52c8 = message->response_length;
  f33_dcm_complete_service_response((F33DcmMessageContext *)((undefined *)camry_host_ptr(0xfebe52bcu)));
  return;
}



/* Use incomingR7 NRC to stage and complete the enclosing52BC DCM context. IncomingR6 operation-view
   pointer is not consumed. */

void f33_dcm_reject_proprietary_message(F33DiagProprietaryMessage *ignored_message,uchar nrc)

{
  f33_dcm_stage_negative_response((F33DcmMessageContext *)((undefined *)camry_host_ptr(0xfebe52bcu)),nrc);
  f33_dcm_complete_service_response((F33DcmMessageContext *)((undefined *)camry_host_ptr(0xfebe52bcu)));
  return;
}



/* status0 =>0,NRC0;other =>1 andconfigured byte mapping, no pending scheduling itself. */

uint f33_diagnostic_status_to_nrc(uchar status,uchar *nrc)

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



void FUN_0008e74e(void)

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



void FUN_0008e772(uint param_1)

{
  param_1 = param_1 & 0xffff;
  if (param_1 < 0x60) {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe52d8u + (uint32_t)(param_1) * 1u)))) = 0;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe5338u + (uint32_t)(param_1) * 1u)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe5338u + (uint32_t)(param_1) * 1u)))) + '\x01';
  }
  return;
}



void FUN_0008e790(uint param_1)

{
  if ((param_1 & 0xffff) < 0x60) {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe52d8u + (uint32_t)(param_1 & 0xffff) * 1u)))) = 0x5a;
  }
  return;
}



void FUN_0008e7a4(uint param_1)

{
  if ((param_1 & 0xffff) < 0x60) {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe5338u + (uint32_t)(param_1 & 0xffff) * 1u)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe5338u + (uint32_t)(param_1 & 0xffff) * 1u)))) + '\x01';
  }
  return;
}



void FUN_0008e7ba(uint param_1)

{
  if ((param_1 & 0xffff) < 0x60) {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe5398u + (uint32_t)(param_1 & 0xffff) * 1u)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe5398u + (uint32_t)(param_1 & 0xffff) * 1u)))) + '\x01';
  }
  return;
}



void FUN_0008e7d0(uint param_1,undefined1 param_2)

{
  if ((param_1 & 0xffff) < 0x60) {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe53f8u + (uint32_t)(param_1 & 0xffff) * 1u)))) = param_2;
  }
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_8e7e0(void)

{
  return;
}



void FUN_0008e7e2(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  f33_secoc_tx_queue_head_pair[0] = 0;
  f33_secoc_tx_queue_head_pair[1] = 0;
  f33_memzero(((void *)camry_host_ptr((uint32_t)((0xfebe5458u)))), 8);
  f33_memzero(((undefined *)camry_host_ptr((uint32_t)(puVar1 + -0x637c))), 0x24);
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x639c)))) = 0;
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x639a)))) = 0;
  f33_memzero(((undefined *)camry_host_ptr((uint32_t)(puVar1 + -0x6396))), 0x18);
  f33_memzero(((undefined *)camry_host_ptr((uint32_t)(puVar1 + -0x6358))), 0x4c);
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6398))))) = 0;
  return;
}



void FUN_0008e82c(void)

{
  uint uVar1;
  uint32_t puVar2;
  puVar2 = 0xfebeb800u;
  FUN_0008e7e2();
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



bool FUN_0008e862(ushort param_1,undefined4 *param_2)

{
  if (param_1 == 0) {
    *(undefined2 *)(param_2 + 3) = 1;
    *param_2 = (0xfebe5458u);
    param_2[1] = camry_host_addr(f33_secoc_tx_queue_head_pair);
    param_2[2] = camry_host_addr(f33_secoc_tx_application_snapshot);
  }
  if (param_1 == 1) {
    *param_2 = camry_host_addr(((undefined *)camry_host_ptr(0xfebe546au)));
    param_2[1] = camry_host_addr(((undefined *)camry_host_ptr(0xfebe5464u)));
    param_2[2] = camry_host_addr(((undefined *)camry_host_ptr(0xfebe54acu)));
    *(undefined2 *)(param_2 + 3) = 3;
  }
  return 1 < param_1;
}



undefined4 FUN_0008e8a0(undefined2 param_1,ushort param_2,ushort *param_3)

{
  ushort uVar1;
  ushort uVar2;
  uint32_t puVar3;
  int extraout_r8;
  int iVar4;
  undefined4 uVar5;
  uint uVar6;
  int local_20;
  ushort *puStack_1c;
  ushort uStack_14;
  
  puVar3 = 0xfebeb800u;
  uVar5 = 1;
  iVar4 = FUN_0008e862(param_1,&local_20);
  if ((((iVar4 == 0) && (extraout_r8 != 0)) && (param_2 < uStack_14)) && ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6398))))) == 'Z')) {
    thunk_FUN_0006a45e();
    uVar2 = 0;
    uVar1 = *puStack_1c;
    while ((uVar6 = (uint)uVar1, uVar2 < param_2 && (uVar6 < uStack_14))) {
      uVar2 = uVar2 + 1;
      uVar1 = (*((ushort *)camry_host_ptr((uint32_t)(uVar6 * 8 + local_20 + 2))));
    }
    if ((uVar2 == param_2) && (uVar6 < uStack_14)) {
      *param_3 = uVar1;
      uVar5 = 0;
    }
    thunk_FUN_0006a4c4();
  }
  return uVar5;
}



undefined2 FUN_0008e912(short param_1,ushort param_2,undefined4 *param_3,undefined4 *param_4)

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
    *param_3 = *(undefined4 *)(((undefined *)camry_host_ptr(0x2586cu)) + (short)param_2 * 0x50);
    *param_4 = *(undefined4 *)(((undefined *)camry_host_ptr(0x25870u)) + (short)param_2 * 0x50);
  }
  return uVar1;
}



undefined2 FUN_0008e954(short param_1,ushort *param_2)

{
  undefined2 uVar1;
  
  uVar1 = 1;
  if (param_1 == 0) {
    if (f33_secoc_tx_queue_head_pair[0] == (ushort)~f33_secoc_tx_queue_head_pair[1]) {
      *param_2 = f33_secoc_tx_queue_head_pair[0];
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



bool FUN_0008e9a0(ushort param_1,ushort param_2)

{
  if (param_1 == 0) {
    f33_secoc_tx_queue_head_pair[1] = ~param_2;
    f33_secoc_tx_queue_head_pair[0] = param_2;
  }
  if (param_1 == 1) {
    DAT_febe5466 = ~param_2;
    DAT_febe5464 = param_2;
  }
  return 1 < param_1;
}



undefined4 FUN_0008e9c6(undefined2 param_1,ushort param_2,undefined4 *param_3)

{
  undefined2 *puVar1;
  ushort uVar2;
  uint32_t puVar3;
  int iVar4;
  int iVar5;
  undefined4 uVar6;
  uint uVar7;
  uint uVar8;
  int local_34;
  uint uStack_30;
  ushort uStack_2a;
  int aiStack_28 [2];
  int iStack_20;
  ushort uStack_1c;
  
  puVar3 = 0xfebeb800u;
  uVar7 = (uint)param_2;
  uVar6 = 1;
  iVar4 = FUN_0008e862(param_1,aiStack_28);
  iVar5 = FUN_0008e912(param_1,uVar7,&uStack_30,&local_34);
  if ((((iVar4 == 0) && (iVar5 == 0)) && ((uintptr_t)(param_3)!=(uintptr_t)((undefined4 *)0x0))) &&
     (*(ushort *)(param_3 + 1) <= uStack_30)) {
    f33_memcpy_forward(((void *)camry_host_ptr((uint32_t)(local_34 + iStack_20))),(void *)*param_3,
                       (uint)*(ushort *)(param_3 + 1));
    puVar1 = ((undefined2 *)camry_host_ptr((uint32_t)(aiStack_28[0] + uVar7 * 8)));
    *puVar1 = *(undefined2 *)(param_3 + 1);
    puVar1[1] = 0xffff;
    puVar1[2] = 0;
    thunk_FUN_0006a45e();
    iVar4 = FUN_0008e954(param_1,&uStack_2a);
    if (iVar4 == 0) {
      uVar8 = (uint)uStack_2a;
      if (uVar8 == 0xffff) {
        uVar6 = FUN_0008e9a0(param_1,uVar7);
      }
      else {
        uVar2 = uStack_2a;
        if (uVar8 < uStack_1c) {
          do {
            uStack_2a = uVar2;
            iVar4 = uVar8 * 8 + aiStack_28[0];
            uVar8 = (uint)(*((ushort *)camry_host_ptr((uint32_t)(iVar4 + 2))));
            if (uVar8 != (ushort)~(*((ushort *)camry_host_ptr((uint32_t)(iVar4 + 4))))) {
              (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6398))))) = 0xa5;
              goto LAB_0008ea96;
            }
            uVar2 = (*((ushort *)camry_host_ptr((uint32_t)(iVar4 + 2))));
          } while (uVar8 < uStack_1c);
          (*((ushort *)camry_host_ptr((uint32_t)(iVar4 + 2)))) = param_2;
          (*((ushort *)camry_host_ptr((uint32_t)(iVar4 + 4)))) = ~param_2;
          uVar6 = 0;
        }
        else {
          (*((undefined2 *)camry_host_ptr((uint32_t)(aiStack_28[0] + uVar7 * 8)))) = 0;
        }
      }
    }
LAB_0008ea96:
    thunk_FUN_0006a4c4();
  }
  return uVar6;
}



undefined4 FUN_0008eaa0(undefined2 param_1,uint param_2,uint param_3,int *param_4)

{
  uint uVar1;
  int iVar2;
  int iVar3;
  undefined4 uVar4;
  undefined2 uVar5;
  int local_34;
  uint uStack_30;
  int aiStack_2c [2];
  int iStack_24;
  
  uVar4 = 1;
  iVar2 = FUN_0008e862(param_1,aiStack_2c);
  iVar3 = FUN_0008e912(param_1,param_2 & 0xffff,&uStack_30,&local_34);
  if (((iVar2 == 0) && (iVar3 == 0)) && ((uintptr_t)(param_4)!=(uintptr_t)((int *)0x0))) {
    uVar1 = (uint)*(ushort *)(param_4 + 1) + (param_3 & 0xffff);
    if (uVar1 <= uStack_30) {
      f33_memcpy_forward(((void *)camry_host_ptr((uint32_t)(local_34 + (param_3 & 0xffff) + iStack_24))),(void *)*param_4,
                         (uint)*(ushort *)(param_4 + 1));
      uVar5 = (undefined2)uVar1;
      (*((undefined2 *)camry_host_ptr((uint32_t)((param_2 & 0xffff) * 8 + aiStack_2c[0])))) = uVar5;
      *(undefined2 *)(param_4 + 1) = uVar5;
      *param_4 = local_34 + iStack_24;
      uVar4 = 0;
    }
  }
  return uVar4;
}



undefined4 FUN_0008eb1c(undefined2 param_1,uint param_2,int *param_3)

{
  ushort uVar1;
  int iVar2;
  int iVar3;
  undefined4 uVar4;
  int local_30;
  uint uStack_2c;
  int aiStack_28 [2];
  int iStack_20;
  
  uVar4 = 1;
  iVar2 = FUN_0008e862(param_1,aiStack_28);
  iVar3 = FUN_0008e912(param_1,param_2 & 0xffff,&uStack_2c,&local_30);
  if (((iVar2 == 0) && (iVar3 == 0)) && ((uintptr_t)(param_3)!=(uintptr_t)((int *)0x0))) {
    *param_3 = local_30 + iStack_20;
    uVar1 = (*((ushort *)camry_host_ptr((uint32_t)((param_2 & 0xffff) * 8 + aiStack_28[0]))));
    if (uStack_2c < uVar1) {
      uVar1 = (ushort)uStack_2c;
    }
    *(ushort *)(param_3 + 1) = uVar1;
    uVar4 = 0;
  }
  return uVar4;
}



undefined4 FUN_0008eb7e(undefined2 param_1,uint param_2)

{
  undefined2 *puVar1;
  uint uVar2;
  uint uVar3;
  uint32_t puVar4;
  ushort uVar5;
  int iVar6;
  int iVar7;
  uint uVar8;
  int local_30;
  uint uStack_2c;
  ushort uStack_26;
  int aiStack_24 [2];
  int iStack_1c;
  ushort uStack_18;
  
  puVar4 = 0xfebeb800u;
  param_2 = param_2 & 0xffff;
  local_30 = 0;
  uStack_2c = 0;
  iVar6 = FUN_0008e862(param_1,aiStack_24);
  iVar7 = FUN_0008e912(param_1,param_2,&uStack_2c,&local_30);
  if (iVar6 != 0) {
    return 1;
  }
  if (iVar7 != 0) {
    return 1;
  }
  thunk_FUN_0006a45e();
  iVar6 = FUN_0008e954(param_1,&uStack_26);
  if (iVar6 == 0) {
    uVar2 = (uint)uStack_26;
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
      uVar5 = uStack_26;
      if (uVar2 < uStack_18) {
        do {
          uStack_26 = uVar5;
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
        } while (uVar2 < uStack_18);
        goto LAB_0008ec3a;
      }
      uVar5 = 0xffff;
    }
    FUN_0008e9a0(param_1,uVar5);
  }
LAB_0008ec3a:
  thunk_FUN_0006a4c4();
  f33_memzero(((void *)camry_host_ptr((uint32_t)(local_30 + iStack_1c))),uStack_2c);
  puVar1 = ((undefined2 *)camry_host_ptr((uint32_t)(param_2 * 8 + aiStack_24[0])));
  *puVar1 = 0;
  puVar1[1] = 0xffff;
  puVar1[2] = 0;
  return 0;
}



undefined4 FUN_0008ec66(void)

{
  uint32_t puVar1;
  undefined4 uVar2;
  
  puVar1 = 0xfebeb800u;
  thunk_FUN_0006a45e();
  if ((*((ushort *)camry_host_ptr((uint32_t)(puVar1 + -0x63a0)))) != (ushort)~(*((ushort *)camry_host_ptr((uint32_t)(puVar1 + -0x639e))))) {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6398))))) = 0xa5;
  }
  if ((*((ushort *)camry_host_ptr((uint32_t)(puVar1 + -0x639c)))) != (ushort)~(*((ushort *)camry_host_ptr((uint32_t)(puVar1 + -0x639a))))) {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6398))))) = 0xa5;
  }
  thunk_FUN_0006a4c4();
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6398))))) == 'Z') {
    uVar2 = 0;
  }
  else {
    uVar2 = 2;
  }
  return uVar2;
}



void FUN_0008ecb2(undefined4 *param_1,undefined1 *param_2,uint *param_3)

{
  int iVar1;
  
  if (((((uintptr_t)(param_1)!=(uintptr_t)((undefined4 *)0x0)) && ((uintptr_t)(param_2)!=(uintptr_t)((undefined1 *)0x0))) &&
      ((uintptr_t)(param_3)!=(uintptr_t)((uint *)0x0))) &&
     ((uint)*(ushort *)(param_1 + 3) + (uint)(*((ushort *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 10)))) + 2 <= *param_3)) {
    *param_2 = (char)((ushort)*(undefined2 *)(param_1 + 2) >> 8);
    param_2[1] = *(undefined1 *)(param_1 + 2);
    f33_memcpy_forward(param_2 + 2,(void *)*param_1,(uint)(*((ushort *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 10)))));
    iVar1 = (*((ushort *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 10)))) + 2;
    f33_memcpy_forward(param_2 + iVar1,(void *)param_1[1],(uint)*(ushort *)(param_1 + 3));
    *param_3 = (uint)*(ushort *)(param_1 + 3) + iVar1;
  }
  return;
}



void FUN_0008ed14(void)

{
  uint32_t puVar1;
  uint32_t puVar2;
  puVar1 = 0xfebeb800u;
  puVar2 = 0x23dfcu;
  DAT_febe54f4 = 0;
  DAT_febe54f6 = 0xfe01;
  DAT_febe54f8 = 0;
  f33_return_only_stub_8e7e0();
  FUN_0008fa20();
  FUN_0008f26c();
  FUN_0008e82c();
  FUN_0008f11a();
  FUN_0008f148(0, ((undefined *)camry_host_ptr((uint32_t)(puVar2 + 0x1a2c))));
  FUN_00090212();
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x630c)))) = 0xfe01;
  return;
}



void FUN_0008ed56(void)

{
  if (((int16_t)DAT_febe54f4) == -0x1ff) {
    DAT_febe54f4 = 0;
    DAT_febe54f6 = 0xfe01;
    DAT_febe54f8 = 0;
    FUN_0008fa20();
    FUN_0008f26c();
    FUN_0008e7e2();
    FUN_0008f11a();
    FUN_00090212();
  }
  return;
}



/* Require54F4FE01, nonnull descriptor/data, mapped source0 and exact allowed length4..32 before
   protected claim. */

uint f33_secoc_transmit(ushort source_pdu,F33PduInfo *info)

{
  uint32_t puVar1;
  uint uVar2;
  int iVar3;
  ushort uStack_a;
  
  puVar1 = 0x23dfcu;
  uVar2 = 1;
  uStack_a = 0;
  if (((((int16_t)DAT_febe54f4) == -0x1ff) && ((uintptr_t)(info)!=(uintptr_t)((F33PduInfo *)0x0))) && ((uintptr_t)(info->data)!=(uintptr_t)((uchar *)0x0))) {
    iVar3 = FUN_0008fa5a(source_pdu,0,&uStack_a);
    if (((iVar3 == 0) && ((uint)info->length <= (*((uint *)camry_host_ptr((uint32_t)(puVar1 + 7000)))))) &&
       ((uint)(*((ushort *)camry_host_ptr((uint32_t)(puVar1 + 0x1b42)))) <= (uint)info->length)) {
      uVar2 = f33_claim_secoc_tx_snapshot(uStack_a,info);
    }
    else {
      uVar2 = 1;
    }
  }
  return uVar2;
}



int FUN_0008ede6(undefined2 param_1)

{
  int iVar1;
  undefined2 uStack_6;
  
  iVar1 = 1;
  uStack_6 = 0;
  if ((((int16_t)DAT_febe54f4) == -0x1ff) && (iVar1 = FUN_0008fa5a(param_1,0,&uStack_6), iVar1 == 0)) {
    iVar1 = FUN_0008fb52(uStack_6);
  }
  return iVar1;
}



uint FUN_0008ee16(char param_1,int param_2)

{
  uint uVar1;
  
  uVar1 = 1;
  if ((((int16_t)DAT_febe54f4) == -0x1ff) && (param_2 != 0)) {
    if (param_1 == -1) {
      uVar1 = f33_secoc_publish_crypto_qualification((*((uchar *)camry_host_ptr((uint32_t)(param_2 + 4)))));
    }
    else {
      uVar1 = FUN_0008f148((uint)(byte)param_1, ((int *)camry_host_ptr((uint32_t)(param_2))));
    }
  }
  return uVar1;
}



undefined4 FUN_0008ee44(undefined2 param_1, undefined4 param_2)

{
  undefined4 uVar1;
  
  if (((int16_t)DAT_febe54f4) == -0x1ff) {
    uVar1 = FUN_000902e4(param_1, param_2);
  }
  else {
    uVar1 = 1;
  }
  return uVar1;
}



undefined4 FUN_0008ee60(undefined2 param_1, undefined4 param_2)

{
  undefined4 uVar1;
  
  if (((int16_t)DAT_febe54f4) == -0x1ff) {
    uVar1 = FUN_00090342(param_1, param_2);
  }
  else {
    uVar1 = 1;
  }
  return uVar1;
}



void FUN_0008ee7c(undefined2 param_1,int *param_2)

{
  int iVar1;
  undefined2 uStack_a;
  
  uStack_a = 0;
  if ((((((int16_t)DAT_febe54f4) == -0x1ff) && ((uintptr_t)(param_2)!=(uintptr_t)((int *)0x0))) && (*param_2 != 0)) &&
     (iVar1 = FUN_0008f2b0(param_1,0,&uStack_a), iVar1 == 0)) {
    FUN_0008f34a(uStack_a,param_2);
  }
  return;
}



void FUN_0008eeba(undefined2 param_1)

{
  int iVar1;
  undefined2 uStack_6;
  
  uStack_6 = 0;
  if ((((int16_t)DAT_febe54f4) == -0x1ff) && (iVar1 = FUN_0008fa5a(param_1,1,&uStack_6), iVar1 == 0)) {
    FUN_0008fc00(uStack_6);
  }
  return;
}



short FUN_0008eee8(void)

{
  short sStack_6;
  
  sStack_6 = 0;
  FUN_00089d08(&sStack_6);
  if ((sStack_6 != 0) && (sStack_6 != 1)) {
    sStack_6 = 2;
  }
  return sStack_6;
}



undefined4 FUN_0008ef0c(void)

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



void FUN_0008ef3a(void)

{
  int iVar1;
  
  iVar1 = FUN_0008eee8();
  if ((((iVar1 == 0) && (iVar1 = FUN_0008ef0c(), iVar1 == 0)) &&
      (iVar1 = FUN_0008f9c6(), iVar1 == 0)) &&
     (((iVar1 = FUN_00090146(), iVar1 == 0 && (iVar1 = FUN_0008f210(), iVar1 == 0)) &&
      (iVar1 = FUN_0008ec66(), iVar1 == 0)))) {
    FUN_000904c0();
  }
  return;
}



/* Far-call trampoline: prepare {lp},0 / jarl 0x8F3CA / dispose 0,{lp},lp; byte-verified against the
   exact image. Forwards with registers and stack unchanged; marked as a thunk. Forwarding shape
   machine-verified; target semantics not recovered. */

void thunk_FUN_0008f3ca(void)

{
  FUN_0008f3ca();
  return;
}



undefined4 FUN_0008ef84(void)

{
  uint32_t puVar1;
  uint32_t puVar2;
  int iVar3;
  int iVar4;
  
  puVar1 = 0xfebeb800u;
  puVar2 = 0x23dfcu;
  while( true ) {
    iVar3 = FUN_0008fc58();
    iVar3 = (uint)(*((ushort *)camry_host_ptr((uint32_t)(puVar2 + 0x1a28)))) - iVar3;
    iVar4 = (uint)(*((ushort *)camry_host_ptr((uint32_t)(puVar1 + -0x6308)))) - iVar3;
    if (iVar4 < 0 == (iVar3 < 0 && iVar3 < 0 == iVar4 < 0)) {
      return 0;
    }
    (*((ushort *)camry_host_ptr((uint32_t)(puVar1 + -0x6308)))) = (*((ushort *)camry_host_ptr((uint32_t)(puVar1 + -0x6308)))) + 1;
    iVar4 = FUN_0008f98c();
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



undefined4 FUN_0008efc6(void)

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
    iVar3 = FUN_000900ea();
    if (iVar3 == 0x202) {
      return 0;
    }
    if (iVar3 == 0x203) {
      return 0;
    }
  } while (iVar3 != 0x300);
  return 0;
}



void FUN_0008eff8(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  FUN_0008ef3a();
  if ((*((short *)camry_host_ptr((uint32_t)(puVar1 + -0x630c)))) == -0x1ff) {
    if ((*((short *)camry_host_ptr((uint32_t)(puVar1 + -0x630a)))) == -0x1ff) {
      (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x6308)))) = 0;
      (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x630a)))) = 0xfd02;
      thunk_FUN_0008f3ca();
      FUN_0008ef84();
      FUN_0008efc6();
      (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x630a)))) = 0xfe01;
    }
    else {
      thunk_FUN_0008f3ca();
    }
  }
  return;
}



/* Far-call trampoline: prepare {lp},0 / jarl 0x8FA86 / dispose 0,{lp},lp; byte-verified against the
   exact image. Forwards with registers and stack unchanged; marked as a thunk. Forwarding shape
   machine-verified; target semantics not recovered. */

undefined4 thunk_FUN_0008fa86(void)

{
  return FUN_0008fa86();
}



/* Far-call trampoline: prepare {lp},0 / jarl 0x8F2FC / dispose 0,{lp},lp; byte-verified against the
   exact image. Forwards with registers and stack unchanged; marked as a thunk. Forwarding shape
   machine-verified; target semantics not recovered. */

int thunk_FUN_0008f2fc(void)

{
  return FUN_0008f2fc();
}



undefined4 FUN_0008f05e(undefined1 *param_1)

{
  undefined1 uVar1;
  int iVar2;
  int iVar3;
  undefined4 uVar4;
  
  uVar4 = 1;
  if ((uintptr_t)(param_1)!=(uintptr_t)((undefined1 *)0x0)) {
    uVar4 = 0;
    if (((int16_t)DAT_febe54f4) == -0x1ff) {
      iVar2 = thunk_FUN_0008fa86();
      iVar3 = thunk_FUN_0008f2fc();
      if ((iVar2 == 2) || (iVar3 == 2)) {
        uVar1 = 2;
      }
      else if ((iVar2 == 3) || (iVar3 == 3)) {
        uVar1 = 3;
      }
      else {
        uVar1 = 1;
      }
    }
    else {
      uVar1 = 0;
    }
    *param_1 = uVar1;
  }
  return uVar4;
}



undefined4 FUN_0008f0a8(short param_1)

{
  undefined4 uVar1;
  
  uVar1 = 1;
  if ((((int16_t)DAT_febe54f4) == -0x1ff) && (param_1 == DAT_0002583c)) {
    ((void)(0), FUN_0008f3ec());
    uVar1 = FUN_00090482(param_1);
  }
  return uVar1;
}



undefined4 FUN_0008f0d4(short param_1)

{
  undefined4 uVar1;
  
  uVar1 = 1;
  if ((((int16_t)DAT_febe54f4) == -0x1ff) && (param_1 == DAT_0002583c)) {
    ((void)(0), FUN_0008f3ec());
    uVar1 = 0;
  }
  return uVar1;
}



/* Far-call trampoline: prepare {lp},0 / jarl 0x8ED14 / dispose 0,{lp},lp; byte-verified against the
   exact image. Forwards with registers and stack unchanged; marked as a thunk. Forwarding shape
   machine-verified; target semantics not recovered. */

void thunk_FUN_0008ed14(void)

{
  FUN_0008ed14();
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_8f106(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_8f108(void)

{
  return;
}



/* Constant source: return 1; shape-classified from the canonical corpus. Callers receive this
   literal directly; its meaning is not recovered. */

undefined4 f33_return_const_1_8f10e(void)

{
  return 1;
}



/* Constant source: return 1; shape-classified from the canonical corpus. Callers receive this
   literal directly; its meaning is not recovered. */

undefined4 f33_return_const_1_8f112(void)

{
  return 1;
}



/* Constant source: return 1; shape-classified from the canonical corpus. Callers receive this
   literal directly; its meaning is not recovered. */

undefined4 f33_return_const_1_8f116(void)

{
  return 1;
}



void FUN_0008f11a(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  f33_memzero(((undefined *)camry_host_ptr(0xfebe5504u)),0x14);
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x6300)))) = 0;
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x6302)))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x62fe))))) = 0xe1;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6303))))) = 0xff;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6304))))) = 0xff;
  return;
}



undefined4 FUN_0008f148(short param_1,int *param_2)

{
  uint32_t puVar1;
  undefined4 uVar2;
  
  puVar1 = 0xfebeb800u;
  uVar2 = 1;
  if ((param_1 == 0) && (*param_2 - 1U < 0x10)) {
    thunk_FUN_0006a45e();
    (*((int *)camry_host_ptr((uint32_t)(puVar1 + -0x62fc)))) = *param_2;
    f33_memcpy_forward(((undefined *)camry_host_ptr((uint32_t)(puVar1 + -0x62f8))), param_2 + 1, 0x10);
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6304))))) = ~(byte)*param_2;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6303))))) = ~*(byte *)(param_2 + 1);
    thunk_FUN_0006a4c4();
    uVar2 = 0;
  }
  return uVar2;
}



bool FUN_0008f19a(short param_1,undefined4 *param_2)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  if (param_1 == 0) {
    thunk_FUN_0006a45e();
    *param_2 = (*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + -0x62fc))));
    f33_memcpy_forward(param_2 + 1, ((undefined *)camry_host_ptr((uint32_t)(puVar1 + -0x62f8))), 0x10);
    thunk_FUN_0006a4c4();
  }
  return param_1 != 0;
}



/* Under the existing critical pair: input1 storesD2,0 storesE1 at5502; other low-byte inputs
   return1 without changing it. Valid input returns0. This flag is not a global steering permission.
    */

uint f33_secoc_publish_crypto_qualification(uchar qualified)

{
  undefined1 uVar1;
  uint32_t puVar2;
  uint uVar3;
  
  puVar2 = 0xfebeb800u;
  uVar3 = 0;
  thunk_FUN_0006a45e();
  if (qualified == '\x01') {
    uVar1 = 0xd2;
  }
  else {
    if (qualified != '\0') {
      uVar3 = 1;
      goto LAB_0008f1f8;
    }
    uVar1 = 0xe1;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x62fe))))) = uVar1;
LAB_0008f1f8:
  thunk_FUN_0006a4c4();
  return uVar3;
}



/* Return1 only for5502==D2. RX recovery8F596 and completion8F906 combine this with per-profile
   configuration; do not interpret it as universal successful authentication. */

uint f33_secoc_crypto_qualification_reported(void)

{
  return (uint)(f33_secoc_crypto_qualification == 0xd2);
}



int FUN_0008f210(void)

{
  uint32_t puVar1;
  int iVar2;
  
  puVar1 = 0xfebeb800u;
  iVar2 = 2;
  thunk_FUN_0006a45e();
  if (((*((uint *)camry_host_ptr((uint32_t)(puVar1 + -0x62fc)))) < 0x11) &&
     ((*((uint *)camry_host_ptr((uint32_t)(puVar1 + -0x62fc)))) == (uint)(byte)~(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6304))))))) {
    if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x62f8))))) == (undefined)~(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6303)))))) {
      iVar2 = 0;
    }
    else {
      iVar2 = 2;
    }
  }
  thunk_FUN_0006a4c4();
  if (iVar2 != 0) {
    (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x6300)))) = 1;
  }
  if ((*((short *)camry_host_ptr((uint32_t)(puVar1 + -0x6300)))) != 0) {
    iVar2 = 2;
    (*((short *)camry_host_ptr((uint32_t)(puVar1 + -0x6300)))) = (*((short *)camry_host_ptr((uint32_t)(puVar1 + -0x6300)))) + -1;
  }
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x6302)))) = 1;
  return iVar2;
}



void FUN_0008f26c(void)

{
  uint uVar1;
  uint uVar2;
  uint32_t puVar3;
  puVar3 = 0xfebeb800u;
  f33_memzero(((undefined *)camry_host_ptr(0xfebe5518u)),4);
  f33_memzero(((undefined *)camry_host_ptr((uint32_t)(puVar3 + -0x62e4))), 4);
  f33_memzero(((undefined *)camry_host_ptr((uint32_t)(puVar3 + -0x62d8))), 0x40);
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x62e0)))) = 0;
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x62de)))) = 0;
  uVar2 = 0;
  do {
    uVar1 = uVar2 + 1;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(uVar2 - 0x62dc))))) = 0xe1;
    uVar2 = uVar1;
  } while (uVar1 < 3);
  return;
}



undefined4 FUN_0008f2b0(short param_1,char param_2,ushort *param_3)

{
  ushort uVar1;
  
  if ((uintptr_t)(param_3)!=(uintptr_t)((ushort *)0x0)) {
    uVar1 = 0;
    if (param_2 == '\0') {
      while (param_1 != (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0x2587cu + (uint32_t)((short)uVar1 * 0x28) * 2u))))) {
        uVar1 = uVar1 + 1;
        if (2 < uVar1) {
          return 1;
        }
      }
LAB_0008f2ec:
      *param_3 = uVar1;
      return 0;
    }
    if (param_2 == '\x01') {
      uVar1 = 0;
      do {
        if (param_1 == (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0x2587eu + (uint32_t)((short)uVar1 * 0x28) * 2u))))) goto LAB_0008f2ec;
        uVar1 = uVar1 + 1;
      } while (uVar1 < 3);
    }
  }
  return 1;
}



int FUN_0008f2fc(void)

{
  char cVar1;
  int iVar2;
  int iVar3;
  uint uVar4;
  
  iVar3 = 0;
  iVar2 = 1;
  uVar4 = 0;
  do {
    cVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe5524u + (uint32_t)(uVar4) * 1u))));
    if (((int8_t)cVar1) != -0x1f) {
      if ((((((int8_t)cVar1) == -0x6a) || (((int8_t)cVar1) == -0x5b)) || (((int8_t)cVar1) == -0x4c)) ||
         ((((int8_t)cVar1) == -0x3d || (((int8_t)cVar1) == -0x2e)))) {
        iVar2 = 2;
      }
      else {
        iVar3 = 0xff;
      }
    }
    uVar4 = uVar4 + 1;
  } while (uVar4 < 3);
  if ((iVar3 == 0xff) && (iVar2 == 1)) {
    iVar2 = 3;
  }
  return iVar2;
}



void FUN_0008f34a(ushort param_1,undefined4 *param_2)

{
  uint32_t puVar1;
  int iVar2;
  uint uVar3;
  undefined4 local_14;
  ushort uStack_10;
  
  puVar1 = 0xfebeb800u;
  uVar3 = (uint)param_1;
  local_14 = *param_2;
  uStack_10 = *(ushort *)(param_2 + 1);
  if ((*(uint *)(((undefined *)camry_host_ptr(0x2586cu)) + (short)param_1 * 0x50) & 0xffff) < (uint)uStack_10) {
    uStack_10 = (ushort)*(uint *)(((undefined *)camry_host_ptr(0x2586cu)) + (short)param_1 * 0x50);
  }
  thunk_FUN_0006a45e();
  if (((int8_t)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(uVar3 - 0x62dc)))))) == -0x1f) {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(uVar3 - 0x62dc))))) = 0xd2;
    thunk_FUN_0006a4c4();
    iVar2 = FUN_0008e9c6(1,uVar3,&local_14);
    if (iVar2 != 0) {
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(uVar3 - 0x62dc))))) = 0xe1;
    }
  }
  else {
    if (((int8_t)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(uVar3 - 0x62dc)))))) == -0x2e) {
      FUN_0008eaa0(1,uVar3,0,&local_14);
    }
    thunk_FUN_0006a4c4();
  }
  return;
}



void FUN_0008f3ca(void)

{
  uint32_t puVar1;
  uint32_t puVar2;
  puVar1 = 0xfebeb800u;
  puVar2 = 0x23dfcu;
  thunk_FUN_0006a45e();
  if ((*((uint *)camry_host_ptr((uint32_t)(puVar1 + -0x62e4)))) < (uint)(*((ushort *)camry_host_ptr((uint32_t)(puVar2 + 0x1a46))))) {
    (*((uint *)camry_host_ptr((uint32_t)(puVar1 + -0x62e4)))) = (*((uint *)camry_host_ptr((uint32_t)(puVar1 + -0x62e4)))) + 1;
  }
  thunk_FUN_0006a4c4();
  return;
}



/* Single constant publisher: DAT_febe551c = 0; Shape-classified from the canonical corpus; the
   target cell is not yet named, so the written state's meaning is unknown. */

void FUN_0008f3ec(void)

{
  DAT_febe551c = 0;
  return;
}



void FUN_0008f3f2(uint param_1)

{
  char cVar1;
  char cVar2;
  uint32_t puVar3;
  puVar3 = 0xfebeb800u;
  thunk_FUN_0006a45e();
  cVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)((param_1 & 0xffff) - 0x62dc)))));
  if ((((int8_t)cVar1) == -0x2e) || (((int8_t)cVar1) == -0x4c)) {
    cVar2 = -0x3d;
  }
  else {
    cVar2 = -0x6a;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)((param_1 & 0xffff) - 0x62dc))))) = cVar2;
  thunk_FUN_0006a4c4();
  if (((int8_t)cVar1) == -0x2e) {
    (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x62e8)))) = 0;
    (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x62e6)))) = 0;
  }
  return;
}



void FUN_0008f434(short param_1,int *param_2,void *param_3)

{
  char *pcVar1;
  byte bVar2;
  uint32_t puVar3;
  uint uVar4;
  uint uVar5;
  int iVar6;
  uint byte_count;
  byte local_30 [16];
  
  puVar3 = 0xfebeb800u;
  iVar6 = param_1 * 0x50;
  if (*(ushort *)(((undefined *)camry_host_ptr(0x2584eu)) + iVar6) <= *(ushort *)(param_2 + 1)) {
    bVar2 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x2585du + (uint32_t)(iVar6) * 1u))));
    uVar4 = (uint)(ushort)(*(ushort *)(param_2 + 1) - *(ushort *)(((undefined *)camry_host_ptr(0x2584eu)) + iVar6));
    f33_memcpy_forward(param_3,((void *)camry_host_ptr((uint32_t)(*param_2 + uVar4))),bVar2 + 7 >> 3);
    uVar5 = bVar2 & 7;
    byte_count = *(ushort *)(((undefined *)camry_host_ptr(0x2584au)) + iVar6) + 7 >> 3;
    f33_memcpy_forward(local_30,((void *)camry_host_ptr((uint32_t)(*param_2 + (bVar2 >> 3) + uVar4))),byte_count);
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x62ac))))) = local_30[0] << uVar5;
    for (uVar4 = 1; uVar4 < byte_count; uVar4 = uVar4 + 1 & 0xffff) {
      bVar2 = local_30[uVar4];
      pcVar1 = ((undefined *)camry_host_ptr((uint32_t)(puVar3 + (uVar4 - 0x62ac))));
      pcVar1[-1] = pcVar1[-1] | (byte)((int)(uint)bVar2 >> (8 - uVar5 & 0x1f));
      *pcVar1 = bVar2 << uVar5;
    }
  }
  return;
}



void FUN_0008f506(short param_1)

{
  if ((uintptr_t)(((code *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x25894u + (uint32_t)(param_1 * 0x14) * 4u)))))))!=(uintptr_t)(f33_reset_vector)) {
    (*(int (*)())camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x25894u + (uint32_t)(param_1 * 0x14) * 4u))))))();
  }
  return;
}



undefined2 FUN_0008f546(ushort param_1,undefined2 param_2)

{
  uint32_t puVar1;
  int iVar2;
  undefined4 local_20;
  undefined2 uStack_1c;
  undefined4 uStack_18;
  undefined2 uStack_14;
  
  puVar1 = 0xfebeb800u;
  iVar2 = FUN_0008eb1c(1,(uint)param_1,&local_20);
  if (iVar2 == 0) {
    uStack_18 = local_20;
    uStack_14 = uStack_1c;
    ((void)(&uStack_18), FUN_00090204((*((volatile uint16_t *)camry_host_ptr((uint32_t)(0x2587eu + (uint32_t)((short)param_1 * 0x28) * 2u))))));
  }
  else {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(param_1 - 0x62dc))))) = 0x96;
    param_2 = 0x103;
  }
  return param_2;
}



void FUN_0008f596(ushort param_1)

{
  uint32_t puVar1;
  uint32_t puVar2;
  uint uVar3;
  uint uVar4;
  undefined4 uVar5;
  
  puVar1 = 0xfebeb800u;
  puVar2 = 0x23dfcu;
  uVar3 = (uint)param_1;
  if (((int8_t)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe5524u + (uint32_t)(uVar3) * 1u))))) == -0x5b) {
    uVar5 = 2;
  }
  else {
    uVar5 = 1;
  }
  FUN_0008f4d0(uVar3,uVar5);
  ((void)(uVar5), FUN_0008f506(uVar3));
  FUN_0008f528(uVar3);
  uVar4 = f33_secoc_crypto_qualification_reported();
  if ((uVar4 == 1) ||
     (((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x25851u + (uint32_t)((short)param_1 * 0x50) * 1u)))) != '\x01' &&
      ((*((uint *)camry_host_ptr((uint32_t)(puVar1 + -0x62e4)))) < (uint)(*((ushort *)camry_host_ptr((uint32_t)(puVar2 + 0x1a46)))))))) {
    FUN_0008f546(uVar3,0x103);
  }
  return;
}



short FUN_0008f60e(ushort param_1,short param_2)

{
  uint uVar1;
  undefined4 uVar2;
  short sVar3;
  
  uVar1 = (uint)param_1;
  if (DAT_febe551a < *(ushort *)(((undefined *)camry_host_ptr(0x25858u)) + (short)param_1 * 0x50)) {
    sVar3 = 0x103;
    if (((int8_t)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe5524u + (uint32_t)(uVar1) * 1u))))) == -0x3d) {
      DAT_febe551a = DAT_febe551a + 1;
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe5524u + (uint32_t)(uVar1) * 1u)))) = -0x4c;
      DAT_febe5518 = 0;
      sVar3 = param_2;
    }
    if (param_2 == 0x201) {
      uVar2 = 2;
    }
    else {
      uVar2 = 1;
    }
    FUN_0008f4d0(uVar1,uVar2);
  }
  else {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe5524u + (uint32_t)(uVar1) * 1u)))) = 0x96;
    FUN_0008f596((uint)(ushort)param_1);
    sVar3 = 0x102;
  }
  return sVar3;
}



void FUN_0008f676(undefined2 param_1, undefined4 param_2)

{
  uint32_t puVar1;
  int iVar2;
  
  puVar1 = 0xfebeb800u;
  iVar2 = FUN_00089c5a((uint)(ushort)param_1, param_2);
  if ((iVar2 == 0) &&
     (iVar2 = FUN_00089c8c(param_1, camry_host_addr(((undefined *)camry_host_ptr((uint32_t)(puVar1 + -0x62d4)))),  (*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + -0x62d8))))), iVar2 == 0))
  {
    FUN_00089c98(param_1, camry_host_addr(((undefined *)camry_host_ptr((uint32_t)(puVar1 + -0x62ac)))),  (*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + -0x62b0)))), camry_host_addr(((undefined *)camry_host_ptr((uint32_t)(puVar1 + -0x629c)))));
  }
  return;
}



undefined2 FUN_0008f6b2(ushort param_1,undefined2 param_2)

{
  uint uVar1;
  undefined2 uVar2;
  
  uVar1 = (uint)param_1;
  if (DAT_febe5518 < *(ushort *)(((undefined *)camry_host_ptr(0x25876u)) + (short)param_1 * 0x50)) {
    uVar2 = 0x103;
    if (((int8_t)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe5524u + (uint32_t)(uVar1) * 1u))))) == -0x3d) {
      DAT_febe5518 = DAT_febe5518 + 1;
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe5524u + (uint32_t)(uVar1) * 1u)))) = -0x4c;
      uVar2 = param_2;
    }
    FUN_0008f4d0(uVar1,1);
  }
  else {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe5524u + (uint32_t)(uVar1) * 1u)))) = 0x96;
    FUN_0008f596((uint)(ushort)param_1);
    uVar2 = 0x102;
  }
  return uVar2;
}



void FUN_0008f70e(uint param_1)

{
  uint32_t puVar1;
  int iVar2;
  
  puVar1 = 0xfebeb800u;
  iVar2 = FUN_0008eb7e(1,param_1 & 0xffff);
  if (iVar2 == 0) {
    f33_memzero(((undefined *)camry_host_ptr((uint32_t)(puVar1 + -0x62e8))), 4);
    f33_memzero(((undefined *)camry_host_ptr((uint32_t)(puVar1 + -0x62d8))), 0x40);
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)((param_1 & 0xffff) - 0x62dc))))) = 0xe1;
  }
  return;
}



void FUN_0008f8d2(short param_1,char param_2)

{
  int iVar1;
  uint uVar2;
  
  iVar1 = (int)param_1;
  if (*(short *)(((undefined *)camry_host_ptr(0x25874u)) + iVar1 * 0x50) == 2) {
    uVar2 = (ushort)(*((volatile uint16_t *)camry_host_ptr((uint32_t)(0x2585au + (uint32_t)(iVar1 * 0x28) * 2u)))) | 0x10000;
    if (param_2 == '\0') {
      uVar2 = (uint)(ushort)(*((volatile uint16_t *)camry_host_ptr((uint32_t)(0x2585au + (uint32_t)(iVar1 * 0x28) * 2u))));
    }
    if ((uintptr_t)(((code *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x25878u + (uint32_t)(iVar1 * 0x14) * 4u)))))))!=(uintptr_t)(f33_reset_vector)) {
      (*(int (*)())camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x25878u + (uint32_t)(iVar1 * 0x14) * 4u))))))(uVar2);
    }
  }
  return;
}



undefined4 FUN_0008f906(ushort param_1)

{
  bool bVar1;
  bool bVar2;
  uint uVar3;
  undefined4 uVar4;
  uint uVar5;
  
  uVar5 = (uint)param_1;
  if (((int8_t)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe5524u + (uint32_t)(uVar5) * 1u))))) == -0x3d) {
    bVar1 = DAT_febe5564 != '\0';
    uVar3 = f33_secoc_crypto_qualification_reported();
    bVar2 = bVar1;
    if ((uVar3 == 1) && ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x25851u + (uint32_t)((short)param_1 * 0x50) * 1u)))) == '\x01')) {
      bVar2 = false;
    }
    FUN_0008f8d2(uVar5,bVar2);
    if (bVar1) {
      uVar4 = FUN_0008f60e(uVar5,0x200);
    }
    else {
      FUN_0008f4d0(uVar5,0);
      uVar4 = FUN_0008f546(uVar5,0);
    }
  }
  else {
    uVar4 = 0x103;
  }
  if (((int8_t)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe5524u + (uint32_t)(uVar5) * 1u))))) != -0x4c) {
    FUN_0008f70e(uVar5);
  }
  return uVar4;
}



int FUN_0008f98c(void)

{
  int iVar1;
  int iVar2;
  undefined2 uStack_a;
  
  iVar2 = 0x300;
  uStack_a = 0;
  iVar1 = FUN_0008e8a0(1,0,&uStack_a);
  if ((iVar1 == 0) && (iVar2 = FUN_0008f746(uStack_a), iVar2 == 0)) {
    iVar2 = FUN_0008f906(uStack_a);
  }
  return iVar2;
}



undefined4 FUN_0008f9c6(void)

{
  char cVar1;
  undefined4 uVar2;
  uint uVar3;
  
  uVar3 = (uint)DAT_febe5520;
  uVar2 = 2;
  if (2 < uVar3) {
    uVar3 = 0;
  }
  cVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe5524u + (uint32_t)(uVar3) * 1u))));
  if ((((((int8_t)cVar1) == -0x6a) || (((int8_t)cVar1) == -0x5b)) || (((int8_t)cVar1) == -0x4c)) ||
     (((((int8_t)cVar1) == -0x3d || (((int8_t)cVar1) == -0x2e)) || (((int8_t)cVar1) == -0x1f)))) {
    uVar2 = 0;
  }
  else {
    DAT_febe5522 = 3;
  }
  if (DAT_febe5522 != 0) {
    DAT_febe5522 = DAT_febe5522 + -1;
    uVar2 = 2;
  }
  DAT_febe5520 = (short)uVar3 + 1;
  return uVar2;
}



void FUN_0008fa20(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  f33_memzero(((undefined *)camry_host_ptr(0xfebe5570u)),0xc);
  f33_memzero(((undefined *)camry_host_ptr((uint32_t)(puVar1 + -0x6284))), 0x3c);
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x6292)))) = 0;
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x6294)))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6298))))) = 0xe1;
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x6296)))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6297))))) = 0x5a;
  return;
}



undefined4 FUN_0008fa5a(short param_1,char param_2,undefined2 *param_3)

{
  short sVar1;
  undefined4 uVar2;
  
  uVar2 = 1;
  if ((uintptr_t)(param_3)!=(uintptr_t)((undefined2 *)0x0)) {
    sVar1 = DAT_00025964;
    if (((param_2 != '\0') && (sVar1 = DAT_00025966, param_2 != '\x01')) || (param_1 != sVar1)) {
      return uVar2;
    }
    *param_3 = 0;
    uVar2 = 0;
  }
  return uVar2;
}



undefined4 FUN_0008fa86(void)

{
  if (((int8_t)DAT_febe5568) == -0x1f) {
    return 1;
  }
  if ((((((int8_t)DAT_febe5568) != -0x6a) && (((int8_t)DAT_febe5568) != -0x5b)) && (((int8_t)DAT_febe5568) != -0x4c)) &&
     ((((int8_t)DAT_febe5568) != -0x3d && (((int8_t)DAT_febe5568) != -0x2e)))) {
    return 3;
  }
  return 2;
}



/* Require5568E1/55695A; claimD2/A5 and increment generation before copy. Subtract four reserved
   bytes. Occupied rejection21 preserves prior snapshot/head/count but COM consumes this request.
   Native protected admission claims generation and copies28 application bytes, leaving trailer
   outside extent. Occupied claim21 preserves old snapshot/head/generation. Internal malformed-queue
   failures are not claimed to preserve payload. */

uint f33_claim_secoc_tx_snapshot(ushort profile,F33PduInfo *info)

{
  uint32_t puVar1;
  uint32_t puVar2;
  uint uVar3;
  uchar *local_18;
  short sStack_14;
  
  puVar1 = 0xfebeb800u;
  puVar2 = 0x23dfcu;
  uVar3 = 0;
  thunk_FUN_0006a45e();
  if ((((int8_t)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6298)))))) == -0x1f) && ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6297))))) == 'Z')) {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6298))))) = 0xd2;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6297))))) = 0xa5;
    (*((short *)camry_host_ptr((uint32_t)(puVar1 + -0x6296)))) = (*((short *)camry_host_ptr((uint32_t)(puVar1 + -0x6296)))) + 1;
  }
  else {
    uVar3 = 0x21;
  }
  thunk_FUN_0006a4c4();
  if (uVar3 == 0) {
    local_18 = ((void *)camry_host_ptr((uint32_t)(info->data)));
    sStack_14 = info->length - (*((short *)camry_host_ptr((uint32_t)(puVar2 + 0x1b42))));
    uVar3 = FUN_0008e9c6(0,profile,&local_18);
    if (uVar3 != 0) {
      thunk_FUN_0006a45e();
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6298))))) = 0xe1;
      (*((short *)camry_host_ptr((uint32_t)(puVar1 + -0x6296)))) = (*((short *)camry_host_ptr((uint32_t)(puVar1 + -0x6296)))) + -1;
      thunk_FUN_0006a4c4();
    }
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6297))))) = 0x5a;
  }
  return uVar3;
}



int FUN_0008fb52(undefined2 param_1)

{
  char cVar1;
  uint32_t puVar2;
  uint32_t puVar3;
  char cVar4;
  int iVar5;
  
  puVar2 = 0xfebeb800u;
  puVar3 = 0x23dfcu;
  cVar4 = 'Z';
  thunk_FUN_0006a45e();
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x6297))))) == 'Z') {
    cVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x6298)))));
    iVar5 = 0;
    if (((int8_t)cVar1) == -0x5b) {
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x6297))))) = 0xa5;
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x6298))))) = 0xe1;
      cVar4 = -0x5b;
    }
    else if (((int8_t)cVar1) == -0x3d) {
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x6298))))) = 0x96;
    }
    else if (((int8_t)cVar1) != -0x6a) {
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x6297))))) = 0xa5;
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x6298))))) = 0xe1;
      if ((((int8_t)cVar1) == -0x2e) || (((int8_t)cVar1) == -0x4c)) {
        (*((short *)camry_host_ptr((uint32_t)(puVar2 + -0x6296)))) = (*((short *)camry_host_ptr((uint32_t)(puVar2 + -0x6296)))) + -1;
      }
    }
  }
  else {
    iVar5 = 1;
  }
  thunk_FUN_0006a4c4();
  if (iVar5 == 0) {
    if (((int8_t)cVar4) == -0x5b) {
      FUN_000901e8((*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + 0x1b68)))));
    }
    if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x6297))))) != 'Z') {
      iVar5 = FUN_0008eb7e(0,param_1);
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x6297))))) = 0x5a;
    }
  }
  return iVar5;
}



void FUN_0008fc00(undefined2 param_1)

{
  undefined2 uVar1;
  uint32_t puVar2;
  uint32_t puVar3;
  char cVar4;
  
  puVar2 = 0xfebeb800u;
  puVar3 = 0x23dfcu;
  cVar4 = 'Z';
  thunk_FUN_0006a45e();
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x6297))))) == 'Z') {
    if (((int8_t)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x6298)))))) == -0x5b) {
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x6297))))) = 0xa5;
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x6298))))) = 0xe1;
      cVar4 = -0x5b;
    }
  }
  thunk_FUN_0006a4c4();
  if (cVar4 != 'Z') {
    FUN_0008eb7e(0,param_1);
    uVar1 = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + 0x1b6a))));
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x6297))))) = 0x5a;
    FUN_000901f6(uVar1);
  }
  return;
}



ushort FUN_0008fc58(void)

{
  ushort uVar1;
  
  uVar1 = DAT_00025826;
  if (DAT_febe556a < DAT_00025826) {
    uVar1 = DAT_febe556a;
  }
  return uVar1;
}



void FUN_0008fc68(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  thunk_FUN_0006a45e();
  if (((int8_t)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6298)))))) == -0x2e) {
    (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x6288)))) = 0;
  }
  else {
    if (((int8_t)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6298)))))) != -0x4c) {
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6298))))) = 0x96;
      goto LAB_0008fcac;
    }
    (*((short *)camry_host_ptr((uint32_t)(puVar1 + -0x6288)))) = (*((short *)camry_host_ptr((uint32_t)(puVar1 + -0x6288)))) + 1;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6298))))) = 0xc3;
  (*((short *)camry_host_ptr((uint32_t)(puVar1 + -0x6296)))) = (*((short *)camry_host_ptr((uint32_t)(puVar1 + -0x6296)))) + -1;
LAB_0008fcac:
  thunk_FUN_0006a4c4();
  return;
}



void FUN_0008fcca(undefined2 param_1, undefined4 param_2)

{
  uint32_t puVar1;
  int iVar2;
  
  puVar1 = 0xfebeb800u;
  iVar2 = FUN_00089b84((uint)(ushort)param_1, param_2);
  if ((iVar2 == 0) &&
     (iVar2 = FUN_00089bb6(param_1, camry_host_addr(((undefined *)camry_host_ptr((uint32_t)(puVar1 + -0x6280)))),  (*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + -0x6284))))), iVar2 == 0))
  {
    FUN_00089bc2(param_1, camry_host_addr(((undefined *)camry_host_ptr((uint32_t)(puVar1 + -0x6258)))),  ((undefined *)camry_host_ptr((uint32_t)(puVar1 + -0x625c))),  0);
  }
  return;
}



undefined2 FUN_0008fd04(undefined4 param_1,undefined2 param_2)

{
  uint32_t puVar1;
  undefined2 uVar2;
  
  puVar1 = 0xfebeb800u;
  if (DAT_febe5578 < DAT_00025942) {
    thunk_FUN_0006a45e();
    if ((((int8_t)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6298)))))) == -0x3d) || (uVar2 = 0x104, ((int8_t)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6298)))))) == -0x5b)) {
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6298))))) = 0xb4;
      (*((short *)camry_host_ptr((uint32_t)(puVar1 + -0x6296)))) = (*((short *)camry_host_ptr((uint32_t)(puVar1 + -0x6296)))) + 1;
      uVar2 = param_2;
    }
    thunk_FUN_0006a4c4();
  }
  else {
    uVar2 = 0x103;
    DAT_febe5568 = 0x96;
  }
  return uVar2;
}



void FUN_0008fd5c(undefined2 param_1)

{
  uint32_t puVar1;
  int iVar2;
  
  puVar1 = 0xfebeb800u;
  iVar2 = FUN_0008eb7e(0,param_1);
  if (iVar2 == 0) {
    f33_memzero(((undefined *)camry_host_ptr((uint32_t)(puVar1 + -0x6290))), 0xc);
    f33_memzero(((undefined *)camry_host_ptr((uint32_t)(puVar1 + -0x6284))), 0x3c);
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6298))))) = 0xe1;
  }
  return;
}



void FUN_0008fed0(short param_1,int param_2,uint *param_3)

{
  undefined1 *puVar1;
  byte bVar2;
  uint uVar3;
  uint uVar4;
  uint uVar5;
  uint uVar6;
  uint uVar7;
  uint uVar8;
  byte *pbVar9;
  
  uVar3 = (uint)(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x2594du + (uint32_t)(param_1 * 0x44) * 1u))));
  if (DAT_febe5570 <= uVar3) {
    uVar3 = DAT_febe5570;
  }
  for (uVar4 = 0; uVar4 < (uVar3 + 7 >> 3 & 0xffff); uVar4 = uVar4 + 1 & 0xffff) {
    (*((undefined1 *)camry_host_ptr((uint32_t)(uVar4 + param_2)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe5574u + (uint32_t)(uVar4) * 1u))));
  }
  uVar7 = uVar3 & 7;
  uVar5 = (uint)*(ushort *)(((undefined *)camry_host_ptr(0x2593au)) + param_1 * 0x44);
  if ((uint)(DAT_febe55a4 * 8) <= uVar5) {
    uVar5 = DAT_febe55a4 * 8;
  }
  uVar8 = uVar5 >> 3 & 0xffff;
  uVar6 = 0;
  if (uVar7 == 0) {
    for (; uVar6 < uVar8; uVar6 = uVar6 + 1 & 0xffff) {
      puVar1 = ((undefined1 *)camry_host_ptr((uint32_t)(uVar4 + param_2)));
      uVar4 = uVar4 + 1 & 0xffff;
      *puVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe55a8u + (uint32_t)(uVar6) * 1u))));
    }
    if ((uVar5 & 7) == 0) goto LAB_0008ffce;
    uVar7 = 8 - (uVar5 & 7);
    pbVar9 = ((byte *)camry_host_ptr((uint32_t)(uVar4 + param_2)));
    bVar2 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe55a8u + (uint32_t)(uVar6) * 1u)))) & (byte)((0xff >> (uVar7 & 0x1f)) << (uVar7 & 0x1f));
  }
  else {
    uVar4 = uVar4 - 1 & 0xffff;
    for (; uVar6 < uVar8; uVar6 = uVar6 + 1 & 0xffff) {
      pbVar9 = ((byte *)camry_host_ptr((uint32_t)(uVar4 + param_2)));
      uVar4 = uVar4 + 1 & 0xffff;
      *pbVar9 = *pbVar9 | (byte)((int)(uint)(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe55a8u + (uint32_t)(uVar6) * 1u)))) >> uVar7);
      (*((undefined1 *)camry_host_ptr((uint32_t)(uVar4 + param_2)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe55a8u + (uint32_t)(uVar6) * 1u)))) << (8 - uVar7 & 0x1f);
    }
    if ((uVar5 & 7) == 0) goto LAB_0008ffce;
    uVar8 = 8 - (uVar5 & 7);
    pbVar9 = ((byte *)camry_host_ptr((uint32_t)(uVar4 + param_2)));
    bVar2 = *pbVar9 | (byte)((int)((uint)(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe55a8u + (uint32_t)(uVar6) * 1u)))) &
                                  (0xff >> (uVar8 & 0x1f)) << (uVar8 & 0x1f)) >> uVar7);
  }
  *pbVar9 = bVar2;
LAB_0008ffce:
  *param_3 = uVar3 + uVar5 + 7 >> 3;
  return;
}


