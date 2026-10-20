#include "common.h"

undefined4 get_icus_state_integrity_code_8b026(void)

{
  if (((((int8_t)DAT_febf136c) == -0x1f) || (((int8_t)DAT_febf136c) == -0x2e)) || (((int8_t)DAT_febf136c) == -0x3d)) {
    if (DAT_febf136d == '\0') {
      return 1;
    }
  }
  else if (DAT_febf136c == '\0') {
    return 0x1000;
  }
  return 0x2000;
}

void synchronize_instruction_execution_8b060(void)

{
  __synchronize();
  return;
}

void clear_state3800_and_768_byte_buffer_8b070(void)

{
  uint uVar1;
  
  DAT_febf380a = 0;
  DAT_febf3810 = 0;
  DAT_febf380f = 0;
  DAT_febf380e = 0;
  DAT_febf3806 = 0;
  DAT_febf3804 = 0;
  DAT_febf380d = 0;
  DAT_febf380c = 0;
  DAT_febf3800 = 0;
  DAT_febf3808 = 0;
  DAT_febf3811 = 0;
  uVar1 = 0;
  do {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebf3812u + (uint32_t)(uVar1) * 1u)))) = 0;
    uVar1 = uVar1 + 1;
  } while (uVar1 < 0x300);
  return;
}

void notify_application_and_6a156_session_change_8b0de(uchar param_1,uchar param_2)

{
  diagnostic_session_changed_application(param_1,param_2);
  request_crypto_direct_abort_for_mode1_or40_6a156(param_1,param_2);
  return;
}

uint check_diagnostic_addressing_admission(uchar addressing_flags)

{
  uint uVar1;
  
  uVar1 = check_diagnostic_application_admission(addressing_flags & 1);
  return uVar1;
}

undefined4 return_const_0_8b10c(void)

{
  return 0;
}

undefined4 return_const_0_8b110(void)

{
  return 0;
}

void call_98898_with_zero_byte_8b120(void)

{
  undefined1 uStack_5;
  
  uStack_5 = 0;
  ((void)(&uStack_5), conditionally_initialize_diagnostics_and_mark_a5_98898());
  return;
}

void reset_application_programming_admission_state_8b134(void)

{
  app_programming_local_word = 0;
  DAT_febf3b1c = 1;
  DAT_febf3b1b = 1;
  DAT_febf3b1a = 0;
  app_programming_pending_latch = '\0';
  app_programming_admission_latched = '\0';
  DAT_febf3b1d = 0xff;
  return;
}

void thunk_reset_application_programming_admission_state_8b134(void)

{
  reset_application_programming_admission_state_8b134();
  return;
}

int latch_programming_admission_after_4d5d8_success_8b17e(void)

{
  int iVar1;
  
  if (app_programming_admission_latched == '\0') {
    iVar1 = test_mode_or_low_66ba_or_latched_condition_4d5d8();
    if (iVar1 == 0) {
      ((void)(0), clear_programming_mode_request_latch_4d5fe());
      app_programming_admission_latched = 'Z';
    }
  }
  else {
    iVar1 = 0;
  }
  return iVar1;
}

uint app_programming_admit_and_stage(void)

{
  uint8_t stack_record_1d[29];
  uint uVar1;
  uchar lower_status;
  uchar application_status;
  uint uVar2;
  uchar uVar3;
  
  application_status = DAT_febf3b1b;
  stack_record_1d[0] = DAT_febf3b1d;
  if (DAT_febf3b1a == '\0') {
    uVar2 = 0;
    do {
      uVar1 = uVar2 + 1;
      ((uint8_t *)((stack_record_1d + 1)))[uVar2] = 0;
      uVar2 = uVar1;
    } while (uVar1 < 8);
    lower_status = ((void)(0x8000200), (void)(10), (void)(0), (void)(((uint8_t *)((stack_record_1d + 1)))), (void)(((uint8_t *)(stack_record_1d))), return_const_0_8b10c());
  }
  else {
    if (DAT_febf3b1a != '\x01') {
      return 0;
    }
    lower_status = DAT_febf3b1c;
    if (DAT_febf3b1c == '\n') {
      lower_status = ((void)(0), (void)(10), return_const_0_8b110());
    }
    if (application_status != '\n') goto LAB_0008b232;
  }
  application_status = ((void)(stack_record_1d[0]), latch_programming_admission_after_4d5d8_success_8b17e());
LAB_0008b232:
  uVar3 = '\x01';
  uVar2 = merge_two_diagnostic_statuses(application_status,lower_status,'\0','\n');
  if ((uVar2 != 10) && (application_status = uVar3, lower_status = uVar3, uVar2 != 0)) {
    uVar3 = '\0';
  }
  DAT_febf3b1b = application_status;
  DAT_febf3b1c = lower_status;
  DAT_febf3b1a = uVar3;
  DAT_febf3b1d = stack_record_1d[0];
  return uVar2;
}

uint app_programming_submit_local_word(uint *param_1)

{
  uint8_t stack_record_21[33];
  bool bVar1;
  uint uVar2;
  uchar lower_status;
  char cVar3;
  uchar application_status;
  
  application_status = DAT_febf3b1b;
  cVar3 = DAT_febf3b1a;
  uVar2 = 0;
  stack_record_21[0] = DAT_febf3b1d;
  do {
    ((uint8_t *)((stack_record_21 + 1)))[uVar2] = 0;
    uVar2 = uVar2 + 1;
  } while (uVar2 < 8);
  if (DAT_febf3b1a == '\x01') {
    uVar2 = *param_1;
    cVar3 = '\x02';
    ((uint8_t *)((stack_record_21 + 1)))[0] = (undefined1)(uVar2 >> 0x18);
    ((uint8_t *)((stack_record_21 + 1)))[1] = (undefined1)(uVar2 >> 0x10);
    ((uint8_t *)((stack_record_21 + 1)))[3] = (undefined1)uVar2;
    ((uint8_t *)((stack_record_21 + 1)))[2] = (undefined1)(uVar2 >> 8);
    lower_status = ((void)(0x8000201), (void)(10), (void)(4), (void)(((uint8_t *)((stack_record_21 + 1)))), (void)(((uint8_t *)(stack_record_21))), return_const_0_8b10c());
  }
  else {
    if (DAT_febf3b1a != '\x02') {
      application_status = '\x01';
      lower_status = '\x01';
      goto LAB_0008b308;
    }
    lower_status = DAT_febf3b1c;
    if (DAT_febf3b1c == '\n') {
      lower_status = ((void)(0), (void)(10), return_const_0_8b110());
    }
    if (application_status != '\n') goto LAB_0008b308;
  }
  app_request_programming_transition();
  application_status = '\0';
LAB_0008b308:
  uVar2 = merge_two_diagnostic_statuses(application_status,lower_status,'\0','\n');
  bVar1 = uVar2 != 10;
  if (bVar1) {
    application_status = '\x01';
  }
  DAT_febf3b1b = application_status;
  if (bVar1) {
    lower_status = '\x01';
  }
  DAT_febf3b1c = lower_status;
  if (bVar1) {
    cVar3 = '\0';
  }
  DAT_febf3b1a = cVar3;
  DAT_febf3b1d = stack_record_21[0];
  return uVar2;
}

uint app_programming_handoff_pending_join(void)

{
  uint uVar1;
  uchar uVar2;
  
  uVar2 = app_programming_pending_latch;
  if (app_programming_pending_latch == '\0') {
    uVar1 = app_programming_admit_and_stage();
    if (uVar1 == 0) {
      app_programming_local_word = 0;
      uVar1 = app_programming_submit_local_word(((uint *)camry_host_ptr((uint32_t)((0xfebf3b14u)))));
      if (uVar1 == 0) {
        uVar1 = 10;
        uVar2 = 'Z';
      }
    }
  }
  else {
    uVar1 = 10;
  }
  app_programming_pending_latch = uVar2;
  return uVar1;
}

uint check_session_transition_and_map_nrc_8b36e(uchar param_1,uchar *param_2)

{
  uint uVar1;
  uchar uStack_d;
  
  dcm_get_session(&uStack_d);
  uVar1 = app_session_transition_precondition(uStack_d,param_1);
  return diagnostic_status_to_nrc((uchar)uVar1,param_2);
}

void reset_write_did_transaction(void)

{
  DAT_febf3b25 = 0;
  DAT_febf3b20 = 0;
  DAT_febf3b1e = 0;
  DAT_febf3b23 = 1;
  DAT_febf3b22 = 1;
  DAT_febf3b21 = 0;
  DAT_febf3b24 = 0xff;
  return;
}

void reset_state3b26_to3b29_8b3d4(void)

{
  DAT_febf3b27 = 1;
  DAT_febf3b28 = 1;
  DAT_febf3b26 = 0;
  DAT_febf3b29 = 0xff;
  return;
}

void reset_write_did_transaction_wrapper_8b3e8(void)

{
  reset_write_did_transaction();
  return;
}

void thunk_reset_state3b26_to3b29_8b3d4(void)

{
  reset_state3b26_to3b29_8b3d4();
  return;
}

uint dcm_probe_did_metadata(ushort did)

{
  uint uVar1;
  
  uVar1 = select_available_did_metadata(did);
  return uVar1;
}

void dcm_selected_did_payload_length(ushort *length)

{
  get_selected_did_payload_length(length);
  return;
}

uint copy_successful_diagnostic_payload_or_map_nrc_8b41a(char param_1,uchar *param_2,int *param_3)

{
  uint uVar1;
  
  if (*param_2 == '\0') {
    if ((param_1 == '\0') && (uVar1 = 0, *(int *)(param_2 + 4) != 0)) {
      for (; uVar1 < *(ushort *)(param_2 + 2); uVar1 = uVar1 + 1 & 0xffff) {
        (*((undefined1 *)camry_host_ptr((uint32_t)(*param_3 + uVar1)))) = (*((undefined1 *)camry_host_ptr((uint32_t)(*(int *)(param_2 + 4) + uVar1))));
      }
    }
    uVar1 = 0;
  }
  else {
    uVar1 = diagnostic_status_to_nrc(*param_2,((uchar *)camry_host_ptr((uint32_t)(param_3[3]))));
  }
  return uVar1;
}

uint did_read_application_adapter(uchar *output,ushort *length,uchar *nrc,ushort did)

{
  uint8_t stack_record_43[68];
  char cVar1;
  uchar uVar2;
  undefined4 uVar3;
  uint uVar4;
  uint uVar5;
  uint32_t apuStack_40[4];
  
  cVar1 = DAT_febf3b26;
  uVar5 = (uint)DAT_febf3b27;
  uVar4 = (uint)DAT_febf3b28;
  uVar2 = get_did_metadata_route_kind(did);
  dcm_selected_did_payload_length(length);
  stack_record_43[2] = (undefined1)did;
  stack_record_43[0] = DAT_febf3b29;
  stack_record_43[1] = (undefined1)(did >> 8);
  if (cVar1 == '\0') {
    if (uVar2 == '\0') {
      uVar5 = read_selected_did_payload(output,*length);
      did = CONCAT11(stack_record_43[1],stack_record_43[2]);
LAB_0008b4b4:
      uVar4 = 1;
LAB_0008b514:
      if (uVar5 != 2) goto LAB_0008b518;
    }
    else {
      uVar5 = 1;
      if (uVar2 != '\x01') goto LAB_0008b4b4;
      uVar4 = ((void)(0x40000000), (void)(2), (void)(2), (void)(((uint8_t *)((stack_record_43 + 1)))), (void)(((uint8_t *)(stack_record_43))), return_const_0_8b10c());
      did = CONCAT11(stack_record_43[1],stack_record_43[2]);
LAB_0008b518:
      ((uint8_t *)((stack_record_43 + 19)))[0] = (undefined1)uVar5;
      if (uVar4 != 2) goto LAB_0008b51c;
    }
    DAT_febf3b26 = 2;
    DAT_febf3b28 = (byte)uVar4;
    DAT_febf3b27 = (byte)uVar5;
    *length = 0;
  }
  else {
    if (cVar1 == '\x02') {
      if (uVar2 == '\0') {
        if (uVar5 == 2) {
          uVar5 = read_selected_did_payload(output,*length);
          did = CONCAT11(stack_record_43[1],stack_record_43[2]);
        }
      }
      else {
        uVar5 = 1;
      }
      stack_record_43[1] = (undefined1)(did >> 8);
      stack_record_43[2] = (undefined1)did;
      if (uVar2 != '\x01') goto LAB_0008b4b4;
      if (uVar4 == 2) {
        uVar4 = ((void)(5), (void)(2), (void)(stack_record_43[0]), return_const_0_8b110());
        did = CONCAT11(stack_record_43[1],stack_record_43[2]);
      }
      goto LAB_0008b514;
    }
    ((uint8_t *)((stack_record_43 + 19)))[0] = 1;
    uVar4 = 1;
LAB_0008b51c:
    stack_record_43[1] = (undefined1)(did >> 8);
    stack_record_43[2] = (undefined1)did;
    if (uVar2 == '\x01') {
      ((uint8_t *)((stack_record_43 + 19)))[0] = (undefined1)uVar4;
    }
    uVar3 = 0x5a;
    if (uVar2 == '\x01') {
      uVar3 = 0;
    }
    (*((uint16_t *)(stack_record_43 + 21))) = *length;
    (*((uint32_t *)(stack_record_43 + 23))) = 0;
    apuStack_40[0] = camry_host_addr(output);
    apuStack_40[3] = camry_host_addr(nrc);
    uVar5 = copy_successful_diagnostic_payload_or_map_nrc_8b41a(uVar3,((uint8_t *)((stack_record_43 + 19))),apuStack_40);
    DAT_febf3b27 = 1;
    DAT_febf3b28 = 1;
    DAT_febf3b26 = 0;
    stack_record_43[0] = 0xff;
    if (uVar5 != 2) {
      DAT_febf3b26 = 0;
      DAT_febf3b27 = 1;
      DAT_febf3b28 = 1;
      DAT_febf3b29 = 0xff;
      DAT_febf3b2a = uVar2;
      return uVar5;
    }
  }
  DAT_febf3b29 = stack_record_43[0];
  DAT_febf3b2a = uVar2;
  return 10;
}

uint write_did_precondition_phase(ushort *matched_index,ushort did)

{
  uint8_t stack_record_25[37];
  uint uVar1;
  uchar lower_status;
  uint uVar2;
  uchar uVar3;
  uchar application_status;
  
  application_status = DAT_febf3b22;
  stack_record_25[0] = DAT_febf3b24;
  if (DAT_febf3b21 == '\0') {
    uVar2 = 0;
    do {
      uVar1 = uVar2 + 1;
      ((uint8_t *)((stack_record_25 + 1)))[uVar2] = 0;
      uVar2 = uVar1;
    } while (uVar1 < 8);
    ((uint8_t *)((stack_record_25 + 1)))[0] = (undefined1)(did >> 8);
    ((uint8_t *)((stack_record_25 + 1)))[1] = (undefined1)did;
    lower_status = ((void)(0x78000000), (void)(2), (void)(2), (void)(((uint8_t *)((stack_record_25 + 1)))), (void)(((uint8_t *)(stack_record_25))), return_const_0_8b10c());
  }
  else {
    if (DAT_febf3b21 != '\x01') {
      return 0;
    }
    lower_status = DAT_febf3b23;
    if (DAT_febf3b23 == '\x02') {
      lower_status = ((void)(5), (void)(2), return_const_0_8b110());
    }
    if (application_status != '\x02') goto LAB_0008b602;
  }
  uVar2 = find_write_did_and_check_precondition(matched_index,did);
  application_status = (uchar)uVar2;
LAB_0008b602:
  uVar3 = '\x01';
  uVar2 = merge_two_diagnostic_statuses(application_status,lower_status,'\0','\x02');
  if ((uVar2 != 2) && (application_status = uVar3, lower_status = uVar3, uVar2 != 0)) {
    uVar3 = '\0';
  }
  DAT_febf3b22 = application_status;
  DAT_febf3b23 = lower_status;
  DAT_febf3b21 = uVar3;
  DAT_febf3b24 = stack_record_25[0];
  return uVar2;
}

uint write_did_payload_phase(ushort matched_index,uchar *payload,ushort length)

{
  uint8_t stack_record_2d[45];
  bool bVar1;
  uchar completion_status;
  uint uVar2;
  uchar lower_status;
  uint uVar3;
  char cVar4;
  uchar application_status;
  
  application_status = DAT_febf3b22;
  cVar4 = DAT_febf3b21;
  completion_status = DAT_febf3b20;
  uVar3 = (uint)length;
  uVar2 = 0;
  stack_record_2d[0] = DAT_febf3b24;
  do {
    ((uint8_t *)((stack_record_2d + 1)))[uVar2] = '\0';
    uVar2 = uVar2 + 1;
  } while (uVar2 < 8);
  if (DAT_febf3b21 == '\x01') {
    cVar4 = '\x02';
    if (uVar3 < 8) {
      for (uVar2 = 0; uVar2 < uVar3; uVar2 = uVar2 + 1 & 0xffff) {
        ((uint8_t *)((stack_record_2d + 1)))[uVar2] = payload[uVar2];
      }
      lower_status = ((void)(0x78000001), (void)(2), (void)(uVar3), (void)(((uint8_t *)((stack_record_2d + 1)))), (void)(((uint8_t *)(stack_record_2d))), return_const_0_8b10c());
    }
    else {
      lower_status = '\x04';
    }
  }
  else {
    if (DAT_febf3b21 != '\x02') {
      application_status = '\t';
      lower_status = '\t';
      goto LAB_0008b6f4;
    }
    lower_status = DAT_febf3b23;
    if (DAT_febf3b23 == '\x02') {
      lower_status = ((void)(5), (void)(2), return_const_0_8b110());
    }
    if (application_status != '\x02') goto LAB_0008b6f4;
  }
  uVar2 = dispatch_or_poll_write_did_action(completion_status,matched_index,payload,length);
  application_status = (uchar)uVar2;
LAB_0008b6f4:
  uVar2 = merge_two_diagnostic_statuses(application_status,lower_status,'\0','\x02');
  bVar1 = uVar2 != 2;
  if (bVar1) {
    application_status = '\x01';
  }
  DAT_febf3b22 = application_status;
  if (bVar1) {
    lower_status = '\x01';
  }
  DAT_febf3b23 = lower_status;
  if (bVar1) {
    cVar4 = '\0';
  }
  DAT_febf3b21 = cVar4;
  DAT_febf3b24 = stack_record_2d[0];
  return uVar2;
}

uint write_did_request_adapter(ushort did,uchar *payload,ushort length,uchar *nrc)

{
  uint uVar1;
  ushort uStack_16;
  
  uStack_16 = DAT_febf3b1e;
  uVar1 = write_did_precondition_phase(&uStack_16,did);
  if (uVar1 == 0) {
    uVar1 = write_did_payload_phase(uStack_16,payload,length);
  }
  if (uVar1 == 2) {
    uVar1 = 10;
    DAT_febf3b20 = 0xff;
  }
  else {
    uVar1 = diagnostic_status_to_nrc((uchar)uVar1,nrc);
  }
  DAT_febf3b1e = uStack_16;
  return uVar1;
}

uint get_status3b20_as_nrc_or_pending_8b77a(uchar *param_1)

{
  uint uVar1;
  
  if (DAT_febf3b20 == 0xff) {
    uVar1 = 10;
  }
  else {
    uVar1 = diagnostic_status_to_nrc(DAT_febf3b20,param_1);
  }
  return uVar1;
}

void set_status_byte3b20_8b79a(undefined1 param_1)

{
  DAT_febf3b20 = param_1;
  return;
}

undefined1 get_byte3b25_8b7a4(void)

{
  return DAT_febf3b25;
}

void set_byte3b25_8b7ae(undefined1 param_1)

{
  DAT_febf3b25 = param_1;
  return;
}

void diag_reset_routine_class_state(void)

{
  uint uVar1;
  
  DAT_febf3b2c = 0;
  DAT_febf3b32 = 1;
  DAT_febf3b31 = 1;
  DAT_febf3b35 = 2;
  DAT_febf3b34 = 2;
  DAT_febf3b33 = 0xff;
  DAT_febf3b30 = 0;
  DAT_febf3b2e = 0;
  uVar1 = 0;
  do {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebf3b36u + (uint32_t)(uVar1) * 1u)))) = 0;
    uVar1 = uVar1 + 1;
  } while (uVar1 < 0x20);
  uVar1 = 0;
  do {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebf3b56u + (uint32_t)(uVar1) * 1u)))) = 0;
    uVar1 = uVar1 + 1;
  } while (uVar1 < 0x31);
  uVar1 = 0;
  do {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebf3b87u + (uint32_t)(uVar1) * 1u)))) = 0;
    uVar1 = uVar1 + 1;
  } while (uVar1 < 0x44);
  return;
}

void reset_routine_class_state_wrapper_a_8b83c(void)

{
  diag_reset_routine_class_state();
  return;
}

void reset_routine_class_state_wrapper_b_8b848(void)

{
  diag_reset_routine_class_state();
  return;
}

undefined4 return_const_0_8b854(void)

{
  return 0;
}

uint diag_routine_crypto_admit(void)

{
  uint uVar1;
  
  uVar1 = return_const_0_8b854();
  return uVar1;
}

uint diag_routine_100e_activate_fixed_crypto_bank0(void)

{
  crypto_bank_activate_collected_update();
  return 0;
}

uint diag_routine_100f_activate_fixed_crypto_bank1(void)

{
  crypto_bank_activate_test_operation();
  return 0;
}

uint advance_direct_read_prepare_status_8b880(void)

{
  uint8_t stack_record_1d[29];
  uint uVar1;
  uchar lower_status;
  uchar application_status;
  uint uVar2;
  uchar uVar3;
  
  application_status = DAT_febf3b31;
  stack_record_1d[0] = DAT_febf3b33;
  if (DAT_febf3b30 == '\0') {
    uVar2 = 0;
    do {
      uVar1 = uVar2 + 1;
      ((uint8_t *)((stack_record_1d + 1)))[uVar2] = 0;
      uVar2 = uVar1;
    } while (uVar1 < 8);
    lower_status = ((void)((int)0x88101030), (void)(2), (void)(0), (void)(((uint8_t *)((stack_record_1d + 1)))), (void)(((uint8_t *)(stack_record_1d))), return_const_0_8b10c());
  }
  else {
    if (DAT_febf3b30 != '\x01') {
      return 0;
    }
    lower_status = DAT_febf3b32;
    if (DAT_febf3b32 == '\x02') {
      lower_status = ((void)(5), (void)(2), return_const_0_8b110());
    }
    if (application_status != '\x02') goto LAB_0008b900;
  }
  application_status = ((void)(stack_record_1d[0]), return_const_0_8b854());
LAB_0008b900:
  uVar3 = '\x01';
  uVar2 = merge_two_diagnostic_statuses(application_status,lower_status,'\0','\x02');
  if ((uVar2 != 2) && (application_status = uVar3, lower_status = uVar3, uVar2 != 0)) {
    uVar3 = '\0';
  }
  DAT_febf3b31 = application_status;
  DAT_febf3b32 = lower_status;
  DAT_febf3b30 = uVar3;
  DAT_febf3b33 = stack_record_1d[0];
  return uVar2;
}

void copy_u16_length_bytes_and_zero_source_8b930(int param_1,int param_2,uint param_3)

{
  uint uVar1;
  
  for (uVar1 = 0; uVar1 < (param_3 & 0xffff); uVar1 = uVar1 + 1 & 0xffff) {
    (*((undefined1 *)camry_host_ptr((uint32_t)(uVar1 + param_1)))) = (*((undefined1 *)camry_host_ptr((uint32_t)(uVar1 + param_2))));
    (*((undefined1 *)camry_host_ptr((uint32_t)(uVar1 + param_2)))) = 0;
  }
  return;
}

uint32_t advance_direct_read_and_clear_result_buffer_8b950(undefined4 param_1,ushort param_2)

{
  uint32_t camry_r10_result;
  uint8_t stack_record_31[52];
  camry_fill_bytes(stack_record_31, sizeof stack_record_31);
  uint uVar1;
  undefined1 uVar2;
  undefined1 uVar3;
  uchar lower_status;
  uint uVar4;
  char cVar5;
  uchar application_status;
  
  uVar3 = DAT_febf3b35;
  uVar2 = DAT_febf3b34;
  application_status = DAT_febf3b31;
  cVar5 = DAT_febf3b30;
  stack_record_31[0] = DAT_febf3b33;
  uVar4 = 0;
  do {
    uVar1 = uVar4 + 1;
    ((uint8_t *)((stack_record_31 + 1)))[uVar4] = 0;
    uVar4 = uVar1;
  } while (uVar1 < 8);
  if (DAT_febf3b30 == '\x01') {
    cVar5 = '\x02';
    ((uint8_t *)((stack_record_31 + 1)))[0] = (undefined1)(param_2 >> 8);
    ((uint8_t *)((stack_record_31 + 1)))[1] = (undefined1)param_2;
    lower_status = (camry_r10_result = ((void)((int)0x88101031), (void)(2), (void)(2), (void)(((uint8_t *)((stack_record_31 + 1)))), (void)(((uint8_t *)(stack_record_31))), return_const_0_8b10c()));
    uVar4 = (camry_r10_result = diag_routine_local_dispatch_enabled());
    if (uVar4 != 0x5a) {
      application_status = '\x02';
      goto LAB_0008b9f4;
    }
  }
  else {
    if (DAT_febf3b30 != '\x02') {
      application_status = '\x01';
      lower_status = '\x01';
      goto LAB_0008b9f4;
    }
    lower_status = DAT_febf3b32;
    if (DAT_febf3b32 == '\x02') {
      lower_status = (camry_r10_result = ((void)(5), (void)(2), return_const_0_8b110()));
    }
    uVar4 = (camry_r10_result = diag_routine_local_dispatch_enabled());
    if ((application_status != '\x02') || (uVar4 != 0x5a)) goto LAB_0008b9f4;
  }
  uVar4 = (camry_r10_result = crypto_bank_read_direct_result(((undefined *)camry_host_ptr(0xfebf3b56u)),param_2));
  application_status = (uchar)uVar4;
LAB_0008b9f4:
  uVar4 = (camry_r10_result = merge_two_diagnostic_statuses(application_status,lower_status,'\0','\x02'));
  if (uVar4 != 2) {
    application_status = '\x01';
    lower_status = '\x01';
    cVar5 = '\0';
    copy_u16_length_bytes_and_zero_source_8b930(param_1, (int)((uint32_t)(0xfebf3b56u)), param_2);
  }
  DAT_febf3b31 = application_status;
  DAT_febf3b32 = lower_status;
  DAT_febf3b30 = cVar5;
  DAT_febf3b34 = uVar2;
  DAT_febf3b35 = uVar3;
  DAT_febf3b33 = stack_record_31[0];
  return camry_r10_result;
}

uint run_direct_read_sequence_and_map_nrc_8ba2c(undefined4 param_1,undefined2 param_2,uchar *param_3)

{
  int iVar1;
  uint uVar2;
  
  iVar1 = advance_direct_read_prepare_status_8b880();
  if (iVar1 == 0) {
    iVar1 = advance_direct_read_and_clear_result_buffer_8b950(param_1,param_2);
  }
  if (iVar1 == 2) {
    uVar2 = 10;
  }
  else {
    uVar2 = diagnostic_status_to_nrc((uchar)iVar1,param_3);
  }
  return uVar2;
}

uint advance_direct_request_prepare_status_8ba5e(void)

{
  uint8_t stack_record_1d[29];
  uint uVar1;
  uchar lower_status;
  uchar application_status;
  uint uVar2;
  uchar uVar3;
  
  application_status = DAT_febf3b31;
  stack_record_1d[0] = DAT_febf3b33;
  if (DAT_febf3b30 == '\0') {
    uVar2 = 0;
    do {
      uVar1 = uVar2 + 1;
      ((uint8_t *)((stack_record_1d + 1)))[uVar2] = 0;
      uVar2 = uVar1;
    } while (uVar1 < 8);
    lower_status = ((void)((int)0x88101010), (void)(2), (void)(7), (void)(((uint8_t *)((stack_record_1d + 1)))), (void)(((uint8_t *)(stack_record_1d))), return_const_0_8b10c());
  }
  else {
    if (DAT_febf3b30 != '\x01') {
      return 0;
    }
    lower_status = DAT_febf3b32;
    if (DAT_febf3b32 == '\x02') {
      lower_status = ((void)(5), (void)(2), return_const_0_8b110());
    }
    if (application_status != '\x02') goto LAB_0008bade;
  }
  application_status = ((void)(stack_record_1d[0]), return_const_0_8b854());
LAB_0008bade:
  uVar3 = '\x01';
  uVar2 = merge_two_diagnostic_statuses(application_status,lower_status,'\0','\x02');
  if ((uVar2 != 2) && (application_status = uVar3, lower_status = uVar3, uVar2 != 0)) {
    uVar3 = '\0';
  }
  DAT_febf3b31 = application_status;
  DAT_febf3b32 = lower_status;
  DAT_febf3b30 = uVar3;
  DAT_febf3b33 = stack_record_1d[0];
  return uVar2;
}

uint stage_direct_request_and_clear_result_bytes_8bb0e(uchar *param_1,uint param_2,int param_3,uint param_4)

{
  uint uVar1;
  undefined1 uVar2;
  undefined1 uVar3;
  uint uVar4;
  uchar lower_status;
  char cVar5;
  uchar application_status;
  undefined1 uStack_2d;
  
  uVar3 = DAT_febf3b35;
  uVar2 = DAT_febf3b34;
  lower_status = DAT_febf3b32;
  application_status = DAT_febf3b31;
  cVar5 = DAT_febf3b30;
  param_2 = param_2 & 0xffff;
  param_4 = param_4 & 0xffff;
  uStack_2d = DAT_febf3b33;
  if (0x31 < param_4) {
    param_4 = 0x31;
  }
  if (0x40 < param_2) {
    param_2 = 0x40;
  }
  uVar4 = 0;
  do {
    uVar1 = uVar4 + 1;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebf3b87u + (uint32_t)(uVar4) * 1u)))) = 0;
    uVar4 = uVar1;
  } while (uVar1 < 0x44);
  if (cVar5 == '\x01') {
    DAT_febf3b87 = (undefined1)(param_2 >> 8);
    DAT_febf3b88 = (undefined1)param_2;
    cVar5 = '\x02';
    for (uVar4 = 0; uVar4 < param_2; uVar4 = uVar4 + 1 & 0xffff) {
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebf3b89u + (uint32_t)(uVar4) * 1u)))) = param_1[uVar4];
    }
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebf3b89u + (uint32_t)(param_2) * 1u)))) = (char)(param_4 >> 8);
    (*((char *)camry_host_ptr((uint32_t)(param_2 + 0xfebf3b8a)))) = (char)param_4;
    lower_status = ((void)((int)0x88101011), (void)(2), (void)(0x44), (void)(((undefined *)camry_host_ptr(0xfebf3b87u))), (void)(&uStack_2d), return_const_0_8b10c());
  }
  else {
    if (cVar5 != '\x02') {
      application_status = '\x01';
      lower_status = '\x01';
      goto LAB_0008bc00;
    }
    if (lower_status == '\x02') {
      lower_status = ((void)(5), (void)(2), return_const_0_8b110());
    }
    if (application_status != '\x02') goto LAB_0008bc00;
  }
  uVar4 = crypto_bank_stage_direct_request
                    (param_1,(ushort)param_2,((undefined *)camry_host_ptr(0xfebf3b56u)),(ushort)param_4);
  application_status = (uchar)uVar4;
LAB_0008bc00:
  uVar1 = merge_two_diagnostic_statuses(application_status,lower_status,'\0','\x02');
  if (uVar1 != 2) {
    for (uVar4 = 0; uVar4 < param_4; uVar4 = uVar4 + 1 & 0xffff) {
      (*((undefined1 *)camry_host_ptr((uint32_t)(uVar4 + param_3)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebf3b56u + (uint32_t)(uVar4) * 1u))));
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebf3b56u + (uint32_t)(uVar4) * 1u)))) = 0;
    }
    application_status = '\x01';
    lower_status = '\x01';
    cVar5 = '\0';
  }
  DAT_febf3b31 = application_status;
  DAT_febf3b32 = lower_status;
  DAT_febf3b30 = cVar5;
  DAT_febf3b34 = uVar2;
  DAT_febf3b35 = uVar3;
  DAT_febf3b33 = uStack_2d;
  return uVar1;
}

uint run_direct_request_sequence_and_map_nrc_8bc4a(undefined4 param_1,undefined2 param_2,undefined4 param_3,undefined2 param_4,
                 uchar *param_5)

{
  int iVar1;
  uint uVar2;
  
  iVar1 = advance_direct_request_prepare_status_8ba5e();
  if (iVar1 == 0) {
    iVar1 = stage_direct_request_and_clear_result_bytes_8bb0e(((uchar *)camry_host_ptr((uint32_t)(param_1))), param_2, param_3, param_4);
  }
  if (iVar1 == 2) {
    uVar2 = 10;
  }
  else {
    uVar2 = diagnostic_status_to_nrc((uchar)iVar1,param_5);
  }
  return uVar2;
}

uint diag_routine_begin_admission
               (ushort rid,uchar control_type,ushort *callback_index,uchar *encoded_input,
               ushort input_length)

{
  uint8_t stack_record_2d[45];
  uint uVar1;
  uchar lower_status;
  uchar uVar2;
  uchar application_status;
  
  application_status = DAT_febf3b31;
  stack_record_2d[0] = DAT_febf3b33;
  if (DAT_febf3b30 == '\0') {
    uVar1 = 0;
    do {
      ((uint8_t *)((stack_record_2d + 1)))[uVar1] = '\0';
      uVar1 = uVar1 + 1;
    } while (uVar1 < 8);
    ((uint8_t *)((stack_record_2d + 1)))[0] = (uchar)(rid >> 8);
    ((uint8_t *)((stack_record_2d + 1)))[3] = *encoded_input;
    ((uint8_t *)((stack_record_2d + 1)))[1] = (uchar)rid;
    ((uint8_t *)((stack_record_2d + 1)))[4] = encoded_input[1];
    ((uint8_t *)((stack_record_2d + 1)))[6] = (uchar)input_length;
    ((uint8_t *)((stack_record_2d + 1)))[5] = (uchar)(input_length >> 8);
    ((uint8_t *)((stack_record_2d + 1)))[2] = control_type;
    lower_status = ((void)((int)0x88000010), (void)(2), (void)(7), (void)(((uint8_t *)((stack_record_2d + 1)))), (void)(((uint8_t *)(stack_record_2d))), return_const_0_8b10c());
  }
  else {
    if (DAT_febf3b30 != '\x01') {
      return 0;
    }
    lower_status = DAT_febf3b32;
    if (DAT_febf3b32 == '\x02') {
      lower_status = ((void)(5), (void)(2), return_const_0_8b110());
    }
    if (application_status != '\x02') goto LAB_0008bd42;
  }
  uVar1 = diag_routine_select_precondition
                    (callback_index,rid,control_type,encoded_input,input_length);
  application_status = (uchar)uVar1;
LAB_0008bd42:
  uVar2 = '\x01';
  uVar1 = merge_two_diagnostic_statuses(application_status,lower_status,'\0','\x02');
  if ((uVar1 != 2) && (application_status = uVar2, lower_status = uVar2, uVar1 != 0)) {
    uVar2 = '\0';
  }
  DAT_febf3b31 = application_status;
  DAT_febf3b32 = lower_status;
  DAT_febf3b30 = uVar2;
  DAT_febf3b33 = stack_record_2d[0];
  return uVar1;
}

undefined4 return_const_2_8bd72(void)

{
  return 2;
}

undefined1 return_input_byte_8bd76(undefined1 param_1)

{
  return param_1;
}

uint diag_routine_run_action_phase
               (uchar control_type,ushort callback_index,uchar *encoded_input,ushort input_length,
               uchar *output,ushort *output_length)

{
  uint8_t stack_record_38[56];
  uint uVar1;
  uint uVar2;
  uchar lower_status;
  uchar uVar3;
  uchar uVar4;
  char cVar5;
  uint uVar6;
  uint uVar7;
  undefined2 uVar8;
  uint uVar9;
  uchar auStack_34 [8];
  
  uVar4 = DAT_febf3b34;
  cVar5 = DAT_febf3b30;
  uVar9 = (uint)DAT_febf3b2e;
  uVar6 = (uint)DAT_febf3b32;
  uVar7 = (uint)DAT_febf3b31;
  stack_record_38[0] = DAT_febf3b33;
  stack_record_38[1] = DAT_febf3b35;
  uVar2 = 0;
  do {
    uVar1 = uVar2 + 1;
    auStack_34[uVar2] = '\0';
    uVar2 = uVar1;
  } while (uVar1 < 8);
  (*((uint16_t *)(stack_record_38 + 2))) = callback_index;
  if (DAT_febf3b30 == '\x01') {
    auStack_34[1] = *encoded_input;
    cVar5 = '\x02';
    auStack_34[4] = (uchar)input_length;
    auStack_34[2] = encoded_input[1];
    auStack_34[3] = (uchar)(input_length >> 8);
    auStack_34[0] = control_type;
    uVar6 = ((void)((int)0x88000011), (void)(2), (void)(5), (void)(auStack_34), (void)(stack_record_38), return_const_0_8b10c());
    uVar7 = diag_routine_dispatch_action
                      ((*((uint16_t *)(stack_record_38 + 2))),control_type,encoded_input,input_length,output,output_length);
    if (uVar7 == 0) {
      if (control_type == '\x03') {
LAB_0008be9c:
        uVar4 = *output;
      }
      else {
        uVar9 = (uint)*output_length;
        if (0x20 < uVar9) {
          uVar9 = 0x20;
        }
        for (uVar2 = 0; uVar2 < uVar9; uVar2 = uVar2 + 1 & 0xffff) {
          (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebf3b36u + (uint32_t)(uVar2) * 1u)))) = output[uVar2];
        }
      }
    }
  }
  else {
    if (DAT_febf3b30 != '\x02') {
      uVar6 = 1;
      uVar3 = '\x01';
      goto LAB_0008beae;
    }
    if (uVar6 == 2) {
      uVar6 = ((void)(5), (void)(2), return_const_0_8b110());
    }
    if ((uVar7 == 2) &&
       (uVar7 = diag_routine_dispatch_action
                          ((*((uint16_t *)(stack_record_38 + 2))),control_type,encoded_input,input_length,output,output_length),
       uVar7 == 0)) {
      if (control_type == '\x03') goto LAB_0008be9c;
      uVar9 = (uint)*output_length;
      if (0x20 < uVar9) {
        uVar9 = 0x20;
      }
      for (uVar2 = 0; uVar2 < uVar9; uVar2 = uVar2 + 1 & 0xffff) {
        (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebf3b36u + (uint32_t)(uVar2) * 1u)))) = output[uVar2];
      }
    }
  }
  uVar3 = (uchar)uVar7;
  if (uVar6 == 0) {
    stack_record_38[1] = return_const_2_8bd72();
  }
LAB_0008beae:
  uVar8 = (undefined2)uVar9;
  lower_status = (uchar)uVar6;
  uVar2 = merge_two_diagnostic_statuses(uVar3,lower_status,'\0','\x02');
  if (uVar2 != 2) {
    if (control_type == '\x03') {
      uVar3 = ((void)(stack_record_38[1]), return_input_byte_8bd76(uVar4));
      *output = uVar3;
    }
    else {
      if (0x20 < uVar9) {
        uVar9 = 0x20;
      }
      for (uVar6 = 0; uVar6 < uVar9; uVar6 = uVar6 + 1 & 0xffff) {
        output[uVar6] = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebf3b36u + (uint32_t)(uVar6) * 1u))));
      }
      *output_length = (ushort)uVar9;
    }
    uVar3 = '\x01';
    cVar5 = '\0';
    lower_status = '\x01';
    uVar8 = 0;
  }
  DAT_febf3b31 = uVar3;
  DAT_febf3b32 = lower_status;
  DAT_febf3b30 = cVar5;
  DAT_febf3b35 = stack_record_38[1];
  DAT_febf3b34 = uVar4;
  DAT_febf3b2e = uVar8;
  DAT_febf3b33 = stack_record_38[0];
  return uVar2;
}

uint diag_routine_application_class
               (uchar control_type,ushort configured_index,uint encoded_input,uchar *output,
               ushort *unused_length,uchar *nrc)

{
  uint8_t stack_record_16[22];
  uint uVar1;
  
  (*((uint16_t *)(stack_record_16 + 0))) = DAT_febf3b2c;
  if (configured_index < 0x14) {
    stack_record_16[2] = (uchar)(encoded_input >> 8);
    stack_record_16[3] = (undefined1)encoded_input;
    (*((uint16_t *)(stack_record_16 + 4))) = 0;
    uVar1 = diag_routine_begin_admission
                      ((*((volatile uint16_t *)camry_host_ptr((uint32_t)(0x26918u + (uint32_t)((uint)configured_index * 4) * 2u)))),control_type,stack_record_16,
                       (stack_record_16 + 2),7);
    if (uVar1 == 0) {
      uVar1 = diag_routine_run_action_phase
                        (control_type,(*((uint16_t *)(stack_record_16 + 0))),(stack_record_16 + 2),7,output,(stack_record_16 + 4));
    }
    if (uVar1 == 2) {
      DAT_febf3b2c = (*((uint16_t *)(stack_record_16 + 0)));
      return 10;
    }
  }
  else {
    uVar1 = 5;
  }
  uVar1 = diagnostic_status_to_nrc((uchar)uVar1,nrc);
  DAT_febf3b2c = (*((uint16_t *)(stack_record_16 + 0)));
  return uVar1;
}

void fill_constant_block_8bfea(void)

{
  DAT_febf3bd2 = 1;
  DAT_febf3bd1 = 1;
  DAT_febf3bd0 = 0;
  DAT_febf3bcc = 0;
  DAT_febf3bd3 = 0xff;
  return;
}
