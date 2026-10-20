#include "common.h"

int check_all_dynamic_did_source_operation_conditions_9502a(undefined2 param_1,undefined1 param_2,undefined1 *param_3)

{
  uint8_t stack_record_1d[29];
  undefined8 uVar1;
  int iVar2;
  uint uVar3;
  byte bVar4;
  
  uVar1 = 0x23dfc00000000;
  *param_3 = 0;
  stack_record_1d[2] = 0;
  iVar2 = get_record_flag_for_selector_zero_95514(param_1,((uint8_t *)(stack_record_1d)));
  if ((iVar2 == 0) && (stack_record_1d[0] != 0)) {
    for (bVar4 = 0; iVar2 = 0, bVar4 < stack_record_1d[0]; bVar4 = bVar4 + 1) {
      iVar2 = ((void)(((uint16_t *)((stack_record_1d + 5)))), load_indexed_four_byte_record_9552a(param_1, bVar4));
      if ((iVar2 != 0) ||
         (uVar3 = dcm_resolve_did_group(((uint16_t *)((stack_record_1d + 5)))[0],'\x01',((uint16_t *)((stack_record_1d + 3))),((uint8_t *)((stack_record_1d + 1)))), uVar3 != 0)
         ) goto LAB_000950ba;
      iVar2 = check_policy_operation_availability_and_condition_94f94(param_2, ((int *)camry_host_ptr((uint32_t)((*((undefined4 *)camry_host_ptr((uint32_t)(0x2250u +
                                    (short)(*((uint16_t *)(stack_record_1d + 3))) * 0x1c + (int)((ulonglong)uVar1 >> 0x20)))))))), 
                           ((uint16_t *)((stack_record_1d + 5)))[0], ((uint8_t *)((stack_record_1d + 2))));
      if (iVar2 != 0) {
        if (iVar2 != 1) {
          return iVar2;
        }
        *param_3 = stack_record_1d[2];
        return 1;
      }
    }
  }
  else {
LAB_000950ba:
    iVar2 = 1;
  }
  return iVar2;
}

int check_configured_dynamic_did_operation_condition_950c0(short param_1,undefined1 param_2,undefined1 *param_3)

{
  uint8_t stack_record_1c[28];
  ushort uVar1;
  char cVar2;
  uint32_t puVar3;
  uint uVar4;
  int iVar5;
  
  puVar3 = 0x23dfcu;
  *param_3 = 0;
  cVar2 = DAT_00026019;
  uVar1 = DAT_00025fec;
  if ((param_1 != 0) ||
     (uVar4 = dcm_resolve_did_group(DAT_00025fec,'\0',((uint16_t *)((stack_record_1c + 2))),((uint8_t *)(stack_record_1c))), uVar4 != 0)) {
    return 1;
  }
  iVar5 = check_policy_operation_availability_and_condition_94f94(param_2, ((int *)camry_host_ptr((uint32_t)((*((undefined4 *)camry_host_ptr((uint32_t)(puVar3 + 0x2220))))))), uVar1, ((uint8_t *)((stack_record_1c + 1))));
  if (iVar5 != 0) {
    if (iVar5 != 1) {
      return iVar5;
    }
    *param_3 = stack_record_1c[1];
    return 1;
  }
  if (cVar2 != '\x01') {
    return 0;
  }
  iVar5 = check_all_dynamic_did_source_operation_conditions_9502a(0,param_2,param_3);
  return iVar5;
}

undefined4 reset_dynamic_did_read_progress_and_entries_9512c(void)

{
  DAT_febe5d20 = 0;
  DAT_febe5d21 = 0;
  return clear_record_flag_for_configured_count_95500();
}

undefined4 probe_did_metadata_failure_flag_for_active_modes_951b8(ushort param_1,byte param_2,undefined4 param_3)

{
  uint uVar1;
  
  if (param_2 < 2) {
    uVar1 = dcm_probe_did_metadata(param_1);
    (*((bool *)camry_host_ptr((uint32_t)(param_3)))) = uVar1 != 0;
  }
  return 0;
}

undefined4 probe_did_metadata_failure_flag_for_active_modes_951da(ushort param_1,byte param_2,undefined4 param_3)

{
  uint uVar1;
  
  if (param_2 < 2) {
    uVar1 = dcm_probe_did_metadata(param_1);
    (*((bool *)camry_host_ptr((uint32_t)(param_3)))) = uVar1 != 0;
  }
  return 0;
}

undefined4 probe_did_metadata_failure_flag_for_active_modes_951fc(ushort param_1,byte param_2,undefined4 param_3)

{
  uint uVar1;
  
  if (param_2 < 2) {
    uVar1 = dcm_probe_did_metadata(param_1);
    (*((bool *)camry_host_ptr((uint32_t)(param_3)))) = uVar1 != 0;
  }
  return 0;
}

undefined4 probe_did_metadata_failure_flag_for_active_modes_9521e(ushort param_1,byte param_2,undefined4 param_3)

{
  uint uVar1;
  
  if (param_2 < 2) {
    uVar1 = dcm_probe_did_metadata(param_1);
    (*((bool *)camry_host_ptr((uint32_t)(param_3)))) = uVar1 != 0;
  }
  return 0;
}

undefined4 probe_did_metadata_failure_flag_for_active_modes_95240(ushort param_1,byte param_2,undefined4 param_3)

{
  uint uVar1;
  
  if (param_2 < 2) {
    uVar1 = dcm_probe_did_metadata(param_1);
    (*((bool *)camry_host_ptr((uint32_t)(param_3)))) = uVar1 != 0;
  }
  return 0;
}

undefined4 get_selected_did_payload_length_for_active_modes_95262(undefined4 param_1,byte param_2,ushort *param_3)

{
  if (param_2 < 2) {
    dcm_selected_did_payload_length(param_3);
  }
  return 0;
}

undefined4 get_selected_did_payload_length_for_active_modes_95278(undefined4 param_1,byte param_2,ushort *param_3)

{
  if (param_2 < 2) {
    dcm_selected_did_payload_length(param_3);
  }
  return 0;
}

undefined4 get_selected_did_payload_length_for_active_modes_9528e(undefined4 param_1,byte param_2,ushort *param_3)

{
  if (param_2 < 2) {
    dcm_selected_did_payload_length(param_3);
  }
  return 0;
}

undefined4 get_selected_did_payload_length_for_active_modes_952a4(undefined4 param_1,byte param_2,ushort *param_3)

{
  if (param_2 < 2) {
    dcm_selected_did_payload_length(param_3);
  }
  return 0;
}

undefined4 get_selected_did_payload_length_for_active_modes_952ba(undefined4 param_1,byte param_2,ushort *param_3)

{
  if (param_2 < 2) {
    dcm_selected_did_payload_length(param_3);
  }
  return 0;
}

uint read_did_by_operation_status_952d0(ushort param_1,uchar *param_2,byte param_3,ushort *param_4,uchar *param_5)

{
  uint uVar1;
  
  if (param_3 < 2) {
    uVar1 = did_read_application_adapter(param_2,param_4,param_5,param_1);
  }
  else {
    uVar1 = 0;
    if (param_3 == 2) {
      thunk_reset_state3b26_to3b29_8b3d4();
    }
  }
  return uVar1;
}

uint read_did_by_operation_status_95300(ushort param_1,uchar *param_2,byte param_3,ushort *param_4,uchar *param_5)

{
  uint uVar1;
  
  if (param_3 < 2) {
    uVar1 = did_read_application_adapter(param_2,param_4,param_5,param_1);
  }
  else {
    uVar1 = 0;
    if (param_3 == 2) {
      thunk_reset_state3b26_to3b29_8b3d4();
    }
  }
  return uVar1;
}

uint read_did_by_operation_status_95330(ushort param_1,uchar *param_2,byte param_3,ushort *param_4,uchar *param_5)

{
  uint uVar1;
  
  if (param_3 < 2) {
    uVar1 = did_read_application_adapter(param_2,param_4,param_5,param_1);
  }
  else {
    uVar1 = 0;
    if (param_3 == 2) {
      thunk_reset_state3b26_to3b29_8b3d4();
    }
  }
  return uVar1;
}

uint read_did_by_operation_status_95360(ushort param_1,uchar *param_2,byte param_3,ushort *param_4,uchar *param_5)

{
  uint uVar1;
  
  if (param_3 < 2) {
    uVar1 = did_read_application_adapter(param_2,param_4,param_5,param_1);
  }
  else {
    uVar1 = 0;
    if (param_3 == 2) {
      thunk_reset_state3b26_to3b29_8b3d4();
    }
  }
  return uVar1;
}

uint read_did_by_operation_status_95390(ushort param_1,uchar *param_2,byte param_3,ushort *param_4,uchar *param_5)

{
  uint uVar1;
  
  if (param_3 < 2) {
    uVar1 = did_read_application_adapter(param_2,param_4,param_5,param_1);
  }
  else {
    uVar1 = 0;
    if (param_3 == 2) {
      thunk_reset_state3b26_to3b29_8b3d4();
    }
  }
  return uVar1;
}

uint write_did_by_operation_status_953c0(ushort param_1,uchar *param_2,byte param_3,ushort param_4,uchar *param_5)

{
  uint uVar1;
  
  if (param_3 < 2) {
    uVar1 = write_did_request_adapter(param_1,param_2,param_4,param_5);
  }
  else {
    uVar1 = 0;
    if (param_3 == 2) {
      reset_write_did_transaction_wrapper_8b3e8();
    }
  }
  return uVar1;
}

uint write_did_by_operation_status_953ec(ushort param_1,uchar *param_2,byte param_3,ushort param_4,uchar *param_5)

{
  uint uVar1;
  
  if (param_3 < 2) {
    uVar1 = write_did_request_adapter(param_1,param_2,param_4,param_5);
  }
  else {
    uVar1 = 0;
    if (param_3 == 2) {
      reset_write_did_transaction_wrapper_8b3e8();
    }
  }
  return uVar1;
}

undefined4 match_configured_record_id_to_zero_index_95418(ushort param_1,undefined2 *param_2)

{
  uint uVar1;
  undefined4 uVar2;
  uint uVar3;
  uint uVar4;
  
  uVar2 = 1;
  if (DAT_00026014 != 0) {
    uVar4 = 0;
    if (param_1 < DAT_00026028) {
      return uVar2;
    }
    if (DAT_00026028 != param_1) {
      uVar3 = (uint)(ushort)(DAT_00026014 - 1);
      if (DAT_00026028 < param_1) {
        return uVar2;
      }
      do {
        if (uVar3 <= uVar4) {
          return uVar2;
        }
        uVar1 = (int)(uVar4 + uVar3) >> 1;
        if (DAT_00026028 < param_1) {
          uVar4 = uVar1 + 1 & 0xffff;
          uVar1 = uVar3;
        }
        uVar3 = uVar1;
      } while (DAT_00026028 != param_1);
    }
    *param_2 = (short)uVar4;
    uVar2 = 0;
  }
  return uVar2;
}

undefined4 store_indexed_four_byte_record_95474(short param_1,uint param_2)

{
  uint32_t puVar1;
  undefined2 *extraout_r8;
  int iVar2;
  undefined4 uVar3;
  short asStack_12 [3];
  
  puVar1 = 0x23dfcu;
  uVar3 = 1;
  if ((((param_1 == 0) && (DAT_00025fe8 != 0)) &&
      (iVar2 = match_configured_record_id_to_zero_index_95418(DAT_00025fec,asStack_12), iVar2 == 0)) &&
     ((asStack_12[0] == 0 && ((param_2 & 0xff) < (uint)(*((byte *)camry_host_ptr((uint32_t)((*((volatile int32_t *)camry_host_ptr((uint32_t)(puVar1 + 0x2220)))) + 0xc)))))))
     ) {
    iVar2 = (param_2 & 0xff) * 4;
    (*((undefined2 *)camry_host_ptr((uint32_t)((*((volatile int32_t *)camry_host_ptr((uint32_t)(puVar1 + 0x21ec)))) + iVar2)))) = *extraout_r8;
    (*((undefined1 *)camry_host_ptr((uint32_t)((*((volatile int32_t *)camry_host_ptr((uint32_t)(puVar1 + 0x21ec)))) + iVar2 + 2)))) = *(undefined1 *)(extraout_r8 + 1);
    (*((undefined1 *)camry_host_ptr((uint32_t)(iVar2 + (*((volatile int32_t *)camry_host_ptr((uint32_t)(puVar1 + 0x21ec)))) + 3)))) = (*((undefined1 *)camry_host_ptr((uint32_t)((int)camry_host_addr(extraout_r8) + 3))));
    uVar3 = 0;
  }
  return uVar3;
}

bool set_record_flag_for_selector_zero_954dc(short param_1,undefined1 param_2)

{
  if (param_1 == 0) {
    DAT_febe5d23 = param_2;
  }
  return param_1 != 0;
}

bool clear_record_flag_for_selector_zero_954ee(short param_1)

{
  if (param_1 == 0) {
    DAT_febe5d23 = 0;
  }
  return param_1 != 0;
}

undefined4 clear_record_flag_for_configured_count_95500(void)

{
  uint uVar1;
  
  for (uVar1 = (uint)DAT_00026018; uVar1 != 0; uVar1 = uVar1 - 1) {
    DAT_febe5d23 = 0;
  }
  return 0;
}

bool get_record_flag_for_selector_zero_95514(short param_1,undefined1 *param_2)

{
  if (param_1 == 0) {
    *param_2 = DAT_febe5d23;
  }
  return param_1 != 0;
}

undefined4 load_indexed_four_byte_record_9552a(short param_1,uint param_2)

{
  uint32_t puVar1;
  undefined2 *extraout_r8;
  int iVar2;
  undefined4 uVar3;
  int iVar4;
  short asStack_12 [3];
  
  puVar1 = 0x23dfcu;
  uVar3 = 1;
  if ((((param_1 == 0) && (DAT_00025fe8 != 0)) &&
      (iVar2 = match_configured_record_id_to_zero_index_95418(DAT_00025fec,asStack_12), iVar2 == 0)) &&
     ((asStack_12[0] == 0 && ((param_2 & 0xff) < (uint)(*((byte *)camry_host_ptr((uint32_t)((*((volatile int32_t *)camry_host_ptr((uint32_t)(puVar1 + 0x2220)))) + 0xc)))))))
     ) {
    iVar2 = (param_2 & 0xff) * 4;
    iVar4 = (*((int *)camry_host_ptr((uint32_t)(puVar1 + 0x21ec))));
    *extraout_r8 = (*((undefined2 *)camry_host_ptr((uint32_t)((*((volatile int32_t *)camry_host_ptr((uint32_t)(puVar1 + 0x21ec)))) + iVar2))));
    *(undefined1 *)(extraout_r8 + 1) = (*((undefined1 *)camry_host_ptr((uint32_t)(iVar4 + iVar2 + 2))));
    (*((undefined1 *)camry_host_ptr((uint32_t)((int)camry_host_addr(extraout_r8) + 3)))) = (*((undefined1 *)camry_host_ptr((uint32_t)(iVar2 + (*((volatile int32_t *)camry_host_ptr((uint32_t)(puVar1 + 0x21ec)))) + 3))));
    uVar3 = 0;
  }
  return uVar3;
}

void clear_diagnostic_callback_state_and_run_four_initializers_95590(void)

{
  int iVar1;
  int iVar2;
  uint32_t puVar3;
  int iVar4;
  
  puVar3 = 0x23dfcu;
  app_dcm_callback_pending = '\0';
  DAT_febe5d24 = 0;
  iVar4 = 0;
  do {
    (*(int (*)())camry_indirect((uint32_t)(((((code *)(uintptr_t)((uint32_t)((uintptr_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(puVar3 + iVar4 * 4 + 0x2300))))))))))))();
    iVar2 = iVar4 + 1;
    iVar1 = iVar4 + -3;
    iVar4 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  return;
}

void set_diagnostic_callback_pending_955b6(uchar param_1)

{
  app_dcm_callback_pending = param_1;
  return;
}

uchar get_diagnostic_callback_pending_955bc(void)

{
  return app_dcm_callback_pending;
}

void invoke_matching_nonzero_tag_callback_955c2(char param_1,undefined1 param_2)

{
  if ((param_1 != '\0') && (param_1 == DAT_000260ec)) {
    (*(int (*)())camry_indirect((uint32_t)(PTR_FUN_000260f0)))(param_2);
  }
  return;
}

int query_diagnostic_readiness_unless_busy_955e4(void)

{
  int iVar1;
  
  if (DAT_febe5d24 == -0x5a5a5a5b) {
    iVar1 = 0;
  }
  else {
    iVar1 = (*(int (*)())camry_indirect((uint32_t)(PTR_return_const_1_968de_000260e4)))();
    if (iVar1 == 1) {
      iVar1 = return_const_1_95622();
    }
  }
  return iVar1;
}

void set_diagnostic_busy_marker_from_done_flag_9560e(char param_1)

{
  if (param_1 == '\x01') {
    DAT_febe5d24 = 0;
  }
  else {
    DAT_febe5d24 = 0xa5a5a5a5;
  }
  return;
}

undefined4 return_const_1_95622(void)

{
  return 1;
}

void dcm_report_negative_or_pending(F33DcmMessageContext *message,uchar nrc)

{
  dcm_stage_negative_response(message,nrc);
  if (nrc != 'x') {
    dcm_complete_service_response(message);
  }
  return;
}

void dcm_report_positive_response(F33DcmMessageContext *message)

{
  dcm_complete_service_response(message);
  return;
}

void invoke_matching_completion_callback_and_clear_busy_95650(char param_1,undefined2 param_2,undefined1 param_3)

{
  if (param_1 == DAT_00026114) {
    (*(int (*)())camry_indirect((uint32_t)(PTR_FUN_00026110)))(param_1,param_2,param_3);
  }
  set_diagnostic_busy_marker_from_done_flag_9560e(1);
  return;
}

undefined4 execute_write_did_payload_and_report_result_95674(undefined1 param_1)

{
  int iVar1;
  uint32_t puVar2;
  uint32_t puVar3;
  int iVar4;
  undefined4 uVar5;
  uchar uStack_11;
  
  puVar2 = 0xfebeb800u;
  puVar3 = 0x23dfcu;
  uVar5 = 0;
  iVar1 = DAT_febe5d30 + 2;
  iVar4 = dcm_dispatch_did_write_callback_94786(DAT_febe5d2c, DAT_febe5d2e, ((uchar *)camry_host_ptr((uint32_t)(iVar1))), param_1, DAT_febe5d34 - 2U & 0xffff, &uStack_11
                      );
  if (iVar4 == 0) {
    set_diagnostic_callback_pending_955b6(0);
    if (((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(0x2cf5))))) == '\x01') && ((*((short *)camry_host_ptr((uint32_t)(puVar3 + 0x2cf6)))) == (*((short *)camry_host_ptr((uint32_t)(puVar2 + -0x5ad2))))))
    {
      ((void)(iVar1), return_only_stub_98900());
    }
    if (1 < (*((uint *)camry_host_ptr((uint32_t)(puVar2 + -0x5abc))))) {
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(puVar2 + -0x5ac8)))))))) = (*((volatile undefined1 *)camry_host_ptr((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xfebeb800u + (uint32_t)(-0x5ad0) * 1u)))))));
      (*((undefined1 *)camry_host_ptr((uint32_t)((*((volatile int32_t *)camry_host_ptr((uint32_t)(puVar2 + -0x5ac8)))) + 1)))) =
           (*((undefined1 *)camry_host_ptr((uint32_t)((*((volatile int32_t *)camry_host_ptr((uint32_t)(puVar2 + -0x5ad0)))) + 1))));
      (*((undefined4 *)camry_host_ptr((uint32_t)(puVar2 + -0x5ac4)))) = 2;
      dcm_report_positive_response(((F33DcmMessageContext *)camry_host_ptr((uint32_t)(puVar2 + -0x5ad0))));
    }
  }
  else if (iVar4 == 10) {
    set_diagnostic_callback_pending_955b6(1);
    dcm_enqueue_event('\x13');
    uVar5 = 10;
  }
  else {
    set_diagnostic_callback_pending_955b6(0);
    if ((iVar4 == 1) && (uStack_11 != '\0')) {
      dcm_report_negative_or_pending(((F33DcmMessageContext *)camry_host_ptr((uint32_t)(puVar2 + -0x5ad0))),uStack_11);
    }
  }
  return uVar5;
}

undefined4 check_write_did_length_and_security_95734(undefined1 param_1)

{
  uint8_t stack_record_b[11];
  uint32_t puVar1;
  uchar nrc;
  int iVar2;
  undefined4 uVar3;
  
  puVar1 = 0xfebeb800u;
  uVar3 = 0;
  iVar2 = dcm_dispatch_did_length_callback_9449e(DAT_febe5d2c,DAT_febe5d2e,param_1,(stack_record_b + 1));
  if (iVar2 == 0) {
    set_diagnostic_callback_pending_955b6(0);
    if ((uint)(*((uint16_t *)(stack_record_b + 1))) == (*((int *)camry_host_ptr((uint32_t)(puVar1 + -0x5acc)))) - 2U) {
      dcm_get_security_level(stack_record_b);
      iVar2 = dcm_check_did_policy_byte_allowlist_943ce((*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x5ad4)))),1,0x22,stack_record_b[0]);
      if (iVar2 == 0) {
        uVar3 = execute_write_did_payload_and_report_result_95674(0);
        return uVar3;
      }
      nrc = '3';
    }
    else {
      nrc = '\x13';
    }
    dcm_report_negative_or_pending(((F33DcmMessageContext *)camry_host_ptr((uint32_t)(puVar1 + -0x5ad0))),nrc);
  }
  else if (iVar2 == 10) {
    set_diagnostic_callback_pending_955b6(1);
    dcm_enqueue_event('\x12');
    uVar3 = 10;
  }
  else {
    set_diagnostic_callback_pending_955b6(0);
  }
  return uVar3;
}

undefined4 check_write_did_session_then_length_957c8(void)

{
  uint32_t puVar1;
  int iVar2;
  undefined4 uVar3;
  uchar uStack_9;
  
  puVar1 = 0xfebeb800u;
  dcm_get_session(&uStack_9);
  iVar2 = dcm_check_did_policy_byte_allowlist_943ce((*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x5ad4)))),1,0x21,uStack_9);
  if (iVar2 == 0) {
    uVar3 = check_write_did_length_and_security_95734(0);
  }
  else {
    uVar3 = 0;
    dcm_report_negative_or_pending(((F33DcmMessageContext *)camry_host_ptr((uint32_t)(puVar1 + -0x5ad0))),'1');
  }
  return uVar3;
}

undefined4 check_write_did_condition_and_queue_pending_95808(undefined1 param_1)

{
  uint32_t puVar1;
  int iVar2;
  undefined4 uVar3;
  char cStack_9;
  
  puVar1 = 0xfebeb800u;
  uVar3 = 0;
  iVar2 = dcm_dispatch_did_presence_probe_9445a(DAT_febe5d2c,DAT_febe5d2e,param_1,&cStack_9);
  if (iVar2 == 0) {
    set_diagnostic_callback_pending_955b6(0);
    if (cStack_9 == '\0') {
      uVar3 = check_write_did_session_then_length_957c8();
    }
    else {
      dcm_report_negative_or_pending(((F33DcmMessageContext *)camry_host_ptr((uint32_t)(puVar1 + -0x5ad0))),'1');
    }
  }
  else if (iVar2 == 10) {
    set_diagnostic_callback_pending_955b6(1);
    dcm_enqueue_event('\x11');
    uVar3 = 10;
  }
  else {
    set_diagnostic_callback_pending_955b6(0);
  }
  return uVar3;
}

undefined4 begin_write_did_request_9586c(undefined4 *param_1)

{
  undefined4 *puVar1;
  uint32_t puVar2;
  ushort did;
  uchar nrc;
  uint uVar3;
  undefined4 uVar4;
  undefined4 *puVar5;
  byte bStack_d;
  
  puVar2 = 0xfebeb800u;
  set_diagnostic_busy_marker_from_done_flag_9560e(0);
  puVar1 = ((undefined4 *)camry_host_ptr((uint32_t)(puVar2 + -0x5ad0)));
  puVar5 = param_1 + 7;
  do {
    uVar4 = *param_1;
    param_1 = param_1 + 1;
    *puVar1 = uVar4;
    puVar1 = puVar1 + 1;
  } while (camry_host_addr(puVar5)!=camry_host_addr(param_1));
  set_diagnostic_callback_pending_955b6(0);
  if ((*((uint *)camry_host_ptr((uint32_t)(puVar2 + -0x5acc)))) < 3) {
    nrc = '\x13';
  }
  else {
    did = CONCAT11((*((volatile undefined1 *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)((puVar2 + -0x5ad0))))))))),(((undefined1 *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)((puVar2 + -0x5ad0)))))))))[1]);
    (*((ushort *)camry_host_ptr((uint32_t)(puVar2 + -0x5ad2)))) = did;
    uVar3 = dcm_resolve_did_group(did,'\x01',((ushort *)camry_host_ptr((uint32_t)(puVar2 + -0x5ad4))),&bStack_d);
    if (uVar3 == 0) {
      if ((bStack_d >> 2 & 1) != 0) {
        uVar4 = check_write_did_condition_and_queue_pending_95808(0);
        return uVar4;
      }
    }
    else if (uVar3 != 1) {
      return 0;
    }
    nrc = '1';
  }
  dcm_report_negative_or_pending(((F33DcmMessageContext *)camry_host_ptr((uint32_t)(puVar2 + -0x5ad0))),nrc);
  return 0;
}

undefined4 cancel_write_did_callbacks_and_events_958f4(undefined4 *param_1)

{
  uint8_t stack_record_c[12];
  uint32_t puVar1;
  int iVar2;
  
  puVar1 = 0xfebeb800u;
  stack_record_c[1] = 0;
  iVar2 = get_diagnostic_callback_pending_955bc();
  if (iVar2 == 1) {
    dcm_dispatch_did_presence_probe_9445a((*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x5ad4)))),(*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x5ad2)))),2,((uint8_t *)(stack_record_c)));
    dcm_dispatch_did_length_callback_9449e((*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x5ad4)))),(*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x5ad2)))),2,((uint16_t *)((stack_record_c + 2))));
    dcm_dispatch_did_write_callback_94786((*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x5ad4)))), (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x5ad2)))), ((uchar *)camry_host_ptr((uint32_t)(*param_1))), 2, 
                 (*((uint16_t *)(stack_record_c + 2))), ((uint8_t *)((stack_record_c + 1))));
    set_diagnostic_callback_pending_955b6(0);
    dcm_invalidate_queued_event('\x11','\0');
    dcm_invalidate_queued_event('\x12','\0');
    dcm_invalidate_queued_event('\x13','\0');
  }
  set_diagnostic_busy_marker_from_done_flag_9560e(1);
  return 0;
}

uint dcm_write_did_service(uchar operation,F33DcmMessageContext *message)

{
  uint uVar1;
  
  if (operation == '\0') {
    uVar1 = begin_write_did_request_9586c(message);
  }
  else {
    uVar1 = 0;
    if (operation == '\x02') {
      uVar1 = cancel_write_did_callbacks_and_events_958f4(((undefined *)camry_host_ptr(0xfebe5d30u)));
    }
  }
  return uVar1;
}

undefined4 resume_write_did_condition_9599c(void)

{
  return check_write_did_condition_and_queue_pending_95808(1);
}

undefined4 resume_write_did_length_check_959aa(void)

{
  return check_write_did_length_and_security_95734(1);
}

undefined4 resume_write_did_payload_959b8(void)

{
  return execute_write_did_payload_and_report_result_95674(1);
}

uint dcm_tester_present_request(F33DcmMessageContext *message)

{
  uchar **ppuVar1;
  F33DcmMessageContext *pFVar2;
  F33DcmMessageContext *pFVar3;
  F33DcmMessageContext local_24;
  
  pFVar2 = &local_24;
  set_diagnostic_busy_marker_from_done_flag_9560e(0);
  pFVar3 = message + 1;
  do {
    ppuVar1 = &message->request;
    message = (F33DcmMessageContext *)&message->request_length;
    pFVar2->request = *(uint32_t *)ppuVar1;
    pFVar2 = ((F33DcmMessageContext *)camry_host_ptr((uint32_t)((int)camry_host_addr(pFVar2) + 4)));
  } while (camry_host_addr(pFVar3)!=camry_host_addr(message));
  if (local_24.request_length == 0) {
    dcm_report_positive_response(&local_24);
  }
  else {
    dcm_report_negative_or_pending(&local_24,'\x13');
  }
  return 0;
}

void clear_diagnostic_busy_marker_95a06(void)

{
  set_diagnostic_busy_marker_from_done_flag_9560e(1);
  return;
}

uint dispatch_tester_present_or_cancel_95a14(char param_1,F33DcmMessageContext *param_2)

{
  uint uVar1;
  
  if (param_1 == '\0') {
    uVar1 = dcm_tester_present_request(param_2);
  }
  else {
    uVar1 = 0;
    if (param_1 == '\x02') {
      clear_diagnostic_busy_marker_95a06();
    }
  }
  return uVar1;
}

uint dcm_session_request(F33DcmMessageContext *message,uchar target)

{
  char *pcVar1;
  char cVar2;
  uchar **ppuVar3;
  undefined4 *puVar4;
  uint uVar5;
  uint32_t puVar6;
  uint32_t puVar7;
  undefined4 uVar8;
  ushort uVar9;
  int iVar10;
  F33DcmMessageContext *pFVar11;
  uchar uStack_d;
  
  puVar6 = 0xfebeb800u;
  puVar7 = 0x23dfcu;
  uStack_d = '\0';
  set_diagnostic_busy_marker_from_done_flag_9560e(0);
  puVar4 = ((undefined4 *)camry_host_ptr((uint32_t)(puVar6 + -0x5aa8)));
  pFVar11 = message;
  do {
    ppuVar3 = &pFVar11->request;
    pFVar11 = (F33DcmMessageContext *)&pFVar11->request_length;
    *puVar4 = *(uint32_t *)ppuVar3;
    puVar4 = puVar4 + 1;
  } while (camry_host_addr(message + 1)!=camry_host_addr(pFVar11));
  uVar5 = message->request_length;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(-0x5aac))))) = 0;
  if (uVar5 == 0) {
    iVar10 = adapt_session_transition_precondition_95cfe(target, camry_host_addr(&uStack_d));
    uVar9 = 0;
    if (iVar10 == 0) {
      while (pcVar1 = ((void *)camry_host_ptr((uint32_t)(puVar7 + (short)uVar9 * 10 + 0x2326))), target != pcVar1[1]) {
        uVar9 = uVar9 + 1 & 0xff;
        if (4 < uVar9) {
          return 0;
        }
      }
      cVar2 = *pcVar1;
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(-0x5aac))))) = (char)uVar9;
      if (cVar2 == '\0') {
        if (message->response_capacity < 4) {
          return 0;
        }
        if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar7 + (uint32_t)(0x2324))))) == '\0') {
          stage_or_publish_dcm_session_91b08(pcVar1[1],0);
          return_zero_via_session_byte_hook_91f9c(pcVar1[1]);
        }
        else {
          stage_or_publish_dcm_session_91b08(pcVar1[1],1);
        }
        (*((volatile undefined1 *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)((puVar6 + -0x5aa0))))))))) = (char)((ushort)*(undefined2 *)(pcVar1 + 2) >> 8);
        (*((char *)camry_host_ptr((uint32_t)((*((volatile int32_t *)camry_host_ptr((uint32_t)(puVar6 + -0x5aa0)))) + 1)))) = (char)*(undefined2 *)(pcVar1 + 2);
        (*((char *)camry_host_ptr((uint32_t)((*((volatile int32_t *)camry_host_ptr((uint32_t)(puVar6 + -0x5aa0)))) + 2)))) = (char)((ushort)*(undefined2 *)(pcVar1 + 8) >> 8)
        ;
        (*((char *)camry_host_ptr((uint32_t)((*((volatile int32_t *)camry_host_ptr((uint32_t)(puVar6 + -0x5aa0)))) + 3)))) = (char)*(undefined2 *)(pcVar1 + 8);
        (*((undefined4 *)camry_host_ptr((uint32_t)(puVar6 + -0x5a9c)))) = 4;
        dcm_report_positive_response(((F33DcmMessageContext *)camry_host_ptr((uint32_t)(puVar6 + -0x5aa8))));
        return 0;
      }
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(-0x5aab))))) = 1;
      if (*pcVar1 == '\x01') {
        uVar8 = 4;
      }
      else {
        uVar8 = 5;
      }
      reset_programming_state_on_initial_status_95d4e(uVar8);
      uStack_d = 'x';
    }
    else if (iVar10 != 1) {
      return 0;
    }
  }
  else {
    uStack_d = '\x13';
  }
  dcm_report_negative_or_pending(((F33DcmMessageContext *)camry_host_ptr((uint32_t)(puVar6 + -0x5aa8))),uStack_d);
  return 0;
}

void dcm_session_cancel(void)

{
  if (((app_dcm_session_row_index < 4) &&
      ((*((volatile uint8_t *)camry_host_ptr((uint32_t)((uint32_t)(0x26122u + (uint32_t)((short)(ushort)app_dcm_session_row_index) * (uint32_t)sizeof(F33DcmSessionTimingRow)) + (uint32_t)(0) * (uint32_t)sizeof(F33DcmSessionTimingRow) + (uint32_t)offsetof(F33DcmSessionTimingRow, transition_kind))))) !=
       '\0')) &&
     (app_dcm_session_deferred_state == '\x01' || app_dcm_session_deferred_state == '\x02'))
  {
    app_dcm_session_deferred_state = '\0';
    reset_programming_state_on_initial_status_95d4e(0);
  }
  dcm_invalidate_queued_event('\x0e','\0');
  set_diagnostic_busy_marker_from_done_flag_9560e(1);
  return;
}

uint dcm_programming_pending_response_join(uchar target)

{
  ushort uVar1;
  undefined2 uVar2;
  undefined1 uVar3;
  uint32_t puVar4;
  uint32_t puVar5;
  uint32_t puVar6;
  uint uVar7;
  int iVar8;
  uint uVar9;
  uchar nrc;
  
  puVar4 = (0xfebeb800u);
  puVar5 = 0xfebeb800u;
  puVar6 = 0x23dfcu;
  uVar9 = 0;
  if (app_dcm_session_deferred_state == '\x01') {
    uVar7 = thunk_dcm_get_current_dispatch_receive_slot_93c60();
    if (2 < uVar7) {
      return 0;
    }
    uVar1 = (*((ushort *)camry_host_ptr((uint32_t)(puVar6 + (short)uVar7 * 0xc + 0x20ec))));
    if (1 < uVar1) {
      return 0;
    }
    uVar2 = (*((volatile undefined2 *)camry_host_ptr((*((volatile uint32_t *)camry_host_ptr((uint32_t)((uint)(*((ushort *)camry_host_ptr((uint32_t)((int)(puVar6 + (short)uVar7 * 0xc + 0x20ec) + 2)))) * 4 +
              (*((int *)camry_host_ptr((uint32_t)(puVar6 + (short)uVar1 * 0x14 + 0x20c4)))))))))));
    uVar3 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)((short)uVar1 * 0x14 + 0x20d4)))));
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x5ab0))))) = target;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x5aae))))) = 0;
    (*((undefined2 *)camry_host_ptr((uint32_t)(puVar5 + -0x5ab4)))) = uVar2;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x5ab2))))) = uVar3;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x5ab1))))) = 0x10;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x5aaf))))) = target == '\x02';
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x5aad))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x5a97))))) != '\x01';
    iVar8 = ((void)(((undefined *)camry_host_ptr((uint32_t)(puVar5 + -0x5ab4)))), join_programming_handoff_pending_95cf2());
    puVar4 = ((uint32_t)(puVar5));
    if (iVar8 == 0) {
LAB_00095c40:
      (*((volatile undefined *)camry_host_ptr((uint32_t)(0xfebeb800u + (uint32_t)(-0x5aab) * 1u)))) = 4;
      reset_programming_state_on_initial_status_95d4e(6);
      return 0;
    }
    if (iVar8 == 1) {
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x5aab))))) = 0;
      reset_programming_state_on_initial_status_95d4e(0);
      nrc = '\"';
      puVar4 = ((uint32_t)(puVar5));
    }
    else {
      if (iVar8 != 10) {
        return 0;
      }
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x5aab))))) = 2;
      nrc = 'x';
      dcm_enqueue_event('\x0e');
      uVar9 = 10;
      puVar4 = ((uint32_t)(puVar5));
    }
  }
  else {
    if (app_dcm_session_deferred_state != '\x02') {
      if (app_dcm_session_deferred_state != '\x03') {
        return 0;
      }
      goto LAB_00095c40;
    }
    nrc = 'x';
  }
  dcm_report_negative_or_pending((F33DcmMessageContext *)(((undefined *)camry_host_ptr((uint32_t)(0xfebeb800u + (uint32_t)(-0x5aa8) * 1u)))),nrc);
  return uVar9;
}

uint dcm_session_operation(uchar operation,F33DcmMessageContext *message,uchar target)

{
  uint uVar1;
  
  if (operation == '\0') {
    uVar1 = dcm_session_request(message,target);
  }
  else {
    uVar1 = 0;
    if (operation == '\x02') {
      dcm_session_cancel();
    }
    else if (operation == '\x03') {
      uVar1 = dcm_programming_pending_response_join(target);
    }
  }
  return uVar1;
}

void apply_selected_session_after_success_95c86(undefined4 param_1,undefined4 param_2,char param_3)

{
  if (((param_3 == '\0') && (DAT_00026120 == '\x01')) && (app_dcm_session_row_index < 4)) {
    return_zero_via_session_byte_hook_91f9c((*((volatile uint8_t *)camry_host_ptr((uint32_t)((uint32_t)(0x26122u + (uint32_t)((short)(ushort)app_dcm_session_row_index) * (uint32_t)sizeof(F33DcmSessionTimingRow)) + (uint32_t)(0) * (uint32_t)sizeof(F33DcmSessionTimingRow) + (uint32_t)offsetof(F33DcmSessionTimingRow, session))))));
  }
  return;
}

void dcm_programming_deferred_event(void)

{
  uint32_t puVar1;
  int iVar2;
  
  puVar1 = 0xfebeb800u;
  iVar2 = ((void)((0xfebe5d4cu)), join_programming_handoff_pending_95cf2());
  if (iVar2 == 0) {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x5aab))))) = 3;
  }
  else if (iVar2 == 1) {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x5aab))))) = 0;
    reset_programming_state_on_initial_status_95d4e(0);
    dcm_report_negative_or_pending(((F33DcmMessageContext *)camry_host_ptr((uint32_t)(puVar1 + -0x5aa8))),'\"');
  }
  else if (iVar2 == 10) {
    dcm_enqueue_event('\x0e');
  }
  return;
}

uint join_programming_handoff_pending_95cf2(void)

{
  return app_programming_handoff_pending_join();
}

uint adapt_session_transition_precondition_95cfe(undefined1 param_1, undefined4 param_2)

{
  return check_session_transition_and_map_nrc_8b36e(param_1, ((uchar *)camry_host_ptr((uint32_t)(param_2))));
}

uint dcm_session_1_callback(uchar operation,F33DcmMessageContext *message)

{
  uint uVar1;
  
  uVar1 = dcm_session_operation(operation,message,'\x01');
  return uVar1;
}

uint dcm_session_2_callback(uchar operation,F33DcmMessageContext *message)

{
  uint uVar1;
  
  uVar1 = dcm_session_operation(operation,message,'\x02');
  return uVar1;
}

uint dcm_session_3_callback(uchar operation,F33DcmMessageContext *message)

{
  uint uVar1;
  
  uVar1 = dcm_session_operation(operation,message,'\x03');
  return uVar1;
}

uint dcm_session_64_callback(uchar operation,F33DcmMessageContext *message)

{
  uint uVar1;
  
  uVar1 = dcm_session_operation(operation,message,'@');
  return uVar1;
}

undefined4 reset_programming_state_on_initial_status_95d4e(char param_1)

{
  if (param_1 == '\0') {
    thunk_reset_application_programming_admission_state_8b134();
  }
  return 0;
}

int accumulate_read_did_length_or_queue_pending_95d60(undefined1 param_1)

{
  uint32_t puVar1;
  int iVar2;
  ushort uStack_a;
  
  puVar1 = 0xfebeb800u;
  if (dcm_read_route_kind == '\x01') {
    iVar2 = dcm_dispatch_did_length_callback_9449e(dcm_read_selected_class,dcm_read_current_did,param_1,&uStack_a);
  }
  else {
    iVar2 = dcm_sum_dynamic_did_entry_lengths_944cc(dcm_read_selected_class,&uStack_a);
  }
  if (iVar2 == 0) {
    set_diagnostic_callback_pending_955b6(0);
    (*((uint *)camry_host_ptr((uint32_t)(puVar1 + -0x5a8c)))) = (*((int *)camry_host_ptr((uint32_t)(puVar1 + -0x5a8c)))) + uStack_a + 2;
  }
  else if ((iVar2 == 1) || (iVar2 != 10)) {
    set_diagnostic_callback_pending_955b6(0);
  }
  else {
    set_diagnostic_callback_pending_955b6(1);
    dcm_enqueue_event('\x1f');
  }
  return iVar2;
}

uint dcm_check_read_did_policy_and_length(void)

{
  uint8_t stack_record_13[20];
  ushort uVar1;
  uint32_t puVar2;
  F33DcmMessageContext *message;
  uchar uVar3;
  int iVar4;
  uint uVar5;
  
  uVar3 = dcm_read_route_kind;
  uVar1 = dcm_read_selected_class;
  puVar2 = 0xfebeb800u;
  stack_record_13[2] = '\0';
  stack_record_13[1] = '\0';
  stack_record_13[0] = '\x01';
  dcm_get_session(((uint8_t *)(stack_record_13)));
  iVar4 = dcm_check_did_policy_byte_allowlist_943ce(uVar1,uVar3,0x11,stack_record_13[0]);
  if (iVar4 == 0) {
    dcm_get_security_level(((uint8_t *)((stack_record_13 + 1))));
    iVar4 = dcm_check_did_policy_byte_allowlist_943ce(uVar1,uVar3,0x12,stack_record_13[1]);
    if (iVar4 == 0) {
      if (uVar3 == '\x01') {
        iVar4 = check_selected_did_policy_operation_condition_94fea(uVar1,0x10,(*((undefined2 *)camry_host_ptr((uint32_t)(puVar2 + -0x5a84)))),((uint8_t *)((stack_record_13 + 2))));
      }
      else {
        iVar4 = check_configured_dynamic_did_operation_condition_950c0(uVar1,0x10,((uint8_t *)((stack_record_13 + 2))));
      }
      if (iVar4 == 0) {
        uVar5 = accumulate_read_did_length_or_queue_pending_95d60(0);
        return uVar5;
      }
      if (iVar4 != 1) {
        return 1;
      }
      if (stack_record_13[2] == '\0') {
        return 1;
      }
      message = ((F33DcmMessageContext *)camry_host_ptr((uint32_t)(puVar2 + -0x5a7c)));
      uVar3 = stack_record_13[2];
    }
    else {
      message = ((F33DcmMessageContext *)camry_host_ptr((uint32_t)(puVar2 + -0x5a7c)));
      uVar3 = '3';
    }
  }
  else {
    message = ((F33DcmMessageContext *)camry_host_ptr((uint32_t)(puVar2 + -0x5a7c)));
    uVar3 = '1';
  }
  dcm_report_negative_or_pending(message,uVar3);
  return 1;
}

uint check_read_did_condition_or_queue_pending_95e76(undefined1 param_1)

{
  uint32_t puVar1;
  int iVar2;
  uint uVar3;
  char cStack_9;
  
  puVar1 = 0xfebeb800u;
  uVar3 = 1;
  cStack_9 = '\x01';
  iVar2 = dcm_dispatch_did_presence_probe_9445a(dcm_read_selected_class,dcm_read_current_did,param_1,&cStack_9);
  if (iVar2 == 0) {
    set_diagnostic_callback_pending_955b6(0);
    if (cStack_9 == '\0') {
      uVar3 = dcm_check_read_did_policy_and_length();
    }
    else {
      dcm_report_negative_or_pending(((F33DcmMessageContext *)camry_host_ptr((uint32_t)(puVar1 + -0x5a7c))),'1');
    }
  }
  else if (iVar2 == 10) {
    set_diagnostic_callback_pending_955b6(1);
    dcm_enqueue_event('\x04');
    uVar3 = 10;
  }
  else {
    set_diagnostic_callback_pending_955b6(0);
  }
  return uVar3;
}

uint dcm_resolve_read_did_route(void)

{
  uint8_t stack_record_15[21];
  ushort did;
  uint32_t puVar1;
  uint uVar2;
  int iVar3;
  
  did = dcm_read_current_did;
  puVar1 = 0xfebeb800u;
  (*((uint16_t *)(stack_record_15 + 7))) = 0;
  stack_record_15[2] = '\0';
  stack_record_15[1] = 0;
  (*((uint16_t *)(stack_record_15 + 5))) = 0;
  stack_record_15[0] = 0;
  (*((uint16_t *)(stack_record_15 + 3))) = 0;
  uVar2 = dcm_resolve_did_group(dcm_read_current_did,'\0',((uint16_t *)((stack_record_15 + 3))),((uint8_t *)(stack_record_15)));
  if ((((uVar2 == 0) && ((stack_record_15[0] & 10) == 10)) &&
      (iVar3 = get_dynamic_did_index_and_entry_count_94f6a(did, ((int8_t *)((stack_record_15 + 2))), camry_host_addr(((uint16_t *)((stack_record_15 + 7))))), iVar3 == 0)) && (stack_record_15[2] != '\0')) {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x5a86))))) = 2;
  }
  else {
    uVar2 = dcm_resolve_did_group(did,'\x01',((uint16_t *)((stack_record_15 + 5))),((uint8_t *)((stack_record_15 + 1))));
    if (uVar2 != 0) {
      if (uVar2 == 1) {
        return 1;
      }
      return 2;
    }
    if ((stack_record_15[1] & 2) != 2) {
      return 1;
    }
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x5a86))))) = 1;
    (*((uint16_t *)(stack_record_15 + 7))) = (*((uint16_t *)(stack_record_15 + 5)));
  }
  (*((ushort *)camry_host_ptr((uint32_t)(puVar1 + -0x5a88)))) = (*((uint16_t *)(stack_record_15 + 7)));
  return 0;
}

uint resolve_read_did_route_then_check_policy_95f78(void)

{
  uint32_t puVar1;
  uint uVar2;
  uint uVar3;
  
  puVar1 = 0xfebeb800u;
  uVar2 = dcm_resolve_read_did_route();
  if (uVar2 == 0) {
    if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x5a86))))) == '\x02') {
      uVar3 = dcm_check_read_did_policy_and_length();
    }
    else {
      uVar3 = check_read_did_condition_or_queue_pending_95e76(0);
    }
  }
  else {
    uVar3 = 1;
    if (uVar2 == 1) {
      dcm_report_negative_or_pending(((F33DcmMessageContext *)camry_host_ptr((uint32_t)(puVar1 + -0x5a7c))),'1');
    }
  }
  return uVar3;
}

uint dcm_serialize_read_did_body(uchar operation)

{
  uint8_t stack_record_25[37];
  uint32_t puVar1;
  ushort uVar2;
  undefined2 uVar3;
  ushort uVar4;
  int iVar5;
  int iVar6;
  undefined8 uVar7;
  uchar event_id;
  uint uVar8;
  uint32_t puVar9;
  uint uVar10;
  ushort uVar11;
  ushort auStack_22 [3];
  
  uVar4 = dcm_read_did_count;
  uVar7 = 0xfebeb800;
  stack_record_25[0] = '\0';
  (*((int16_t *)(stack_record_25 + 1))) = 1;
  uVar10 = 0;
  uVar11 = dcm_read_did_cursor;
LAB_00096124:
  iVar6 = (int)uVar7;
  if (uVar11 < uVar4) {
    uVar2 = uVar11 * 2;
    uVar3 = CONCAT11((*((undefined1 *)camry_host_ptr((uint32_t)((uint)uVar2 + (*((volatile int32_t *)camry_host_ptr((uint32_t)(iVar6 + -0x5a7c)))))))),
                     (*((undefined1 *)camry_host_ptr((uint32_t)((uint)(ushort)(uVar2 + 1) + (*((volatile int32_t *)camry_host_ptr((uint32_t)(iVar6 + -0x5a7c)))))))));
    (*((undefined2 *)camry_host_ptr((uint32_t)(iVar6 + -0x5a84)))) = uVar3;
    uVar8 = dcm_resolve_read_did_route();
    iVar6 = (int)uVar7;
    if (uVar8 == 0) {
      if (operation == '\0') {
        iVar5 = (*((int *)camry_host_ptr((uint32_t)(iVar6 + -0x5a70))));
        (*((undefined1 *)camry_host_ptr((uint32_t)((*((volatile int32_t *)camry_host_ptr((uint32_t)(iVar6 + -0x5a74)))) + iVar5)))) =
             (*((undefined1 *)camry_host_ptr((uint32_t)((*((volatile int32_t *)camry_host_ptr((uint32_t)(iVar6 + -0x5a7c)))) + (uint)uVar2))));
        (*((undefined1 *)camry_host_ptr((uint32_t)(iVar5 + (*((volatile int32_t *)camry_host_ptr((uint32_t)(iVar6 + -0x5a74)))) + 1)))) =
             (*((undefined1 *)camry_host_ptr((uint32_t)((*((volatile int32_t *)camry_host_ptr((uint32_t)(iVar6 + -0x5a7c)))) + (uint)uVar2 + 1))));
        (*((int *)camry_host_ptr((uint32_t)(iVar6 + -0x5a70)))) = (*((int *)camry_host_ptr((uint32_t)(iVar6 + -0x5a70)))) + 2;
      }
      auStack_22[0] = 0;
      iVar5 = (*((int *)camry_host_ptr((uint32_t)(iVar6 + -0x5a70)))) + (*((int *)camry_host_ptr((uint32_t)(iVar6 + -0x5a74))));
      if ((*((char *)camry_host_ptr((uint32_t)(iVar6 + -0x5a86)))) == '\x01') {
        iVar5 = dcm_dispatch_did_read_callback_94526((*((undefined2 *)camry_host_ptr((uint32_t)(iVar6 + -0x5a88)))), uVar3, ((uchar *)camry_host_ptr((uint32_t)(iVar5))), operation, auStack_22, 
                             stack_record_25);
        (*((int16_t *)(stack_record_25 + 1))) = (*((int16_t *)(stack_record_25 + 1))) + -1;
      }
      else {
        iVar5 = dcm_read_dynamic_did_with_pending_cancellation_946c6((*((undefined2 *)camry_host_ptr((uint32_t)(iVar6 + -0x5a88)))), iVar5, operation, auStack_22, stack_record_25, camry_host_addr((stack_record_25 + 1)));
      }
      iVar6 = (int)uVar7;
      if (iVar5 == 0) {
        set_diagnostic_callback_pending_955b6(0);
        iVar6 = (int)uVar7;
        puVar1 = (uint32_t)((uint32_t)((*((volatile int32_t *)camry_host_ptr((uint32_t)(iVar6 + -0x5a70)))) + (uint)auStack_22[0]));
        puVar9 = ((uint32_t)((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)((iVar6 + -0x5a68))))))));
        (*((volatile uint32_t *)camry_host_ptr((uint32_t)((iVar6 + -0x5a70))))) = puVar1;
        if (0xfffdu < puVar9) {
          puVar9 = 0xfffe;
        }
        if (puVar1<= puVar9) goto code_r0x000960ac;
      }
      else if (iVar5 == 1) {
        set_diagnostic_callback_pending_955b6(0);
        if (stack_record_25[0] != '\0') {
          dcm_report_negative_or_pending(((F33DcmMessageContext *)camry_host_ptr((uint32_t)(iVar6 + -0x5a7c))),stack_record_25[0]);
        }
      }
      else if (iVar5 == 10) {
        set_diagnostic_callback_pending_955b6(1);
        puVar1 = (uint32_t)((uint32_t)((*((volatile int32_t *)camry_host_ptr((uint32_t)(iVar6 + -0x5a70)))) + (uint)auStack_22[0]));
        puVar9 = ((uint32_t)((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)((iVar6 + -0x5a68))))))));
        (*((volatile uint32_t *)camry_host_ptr((uint32_t)((iVar6 + -0x5a70))))) = puVar1;
        if (0xfffdu < puVar9) {
          puVar9 = 0xfffe;
        }
        if (puVar1<= puVar9) {
          (*((ushort *)camry_host_ptr((uint32_t)(iVar6 + -0x5a82)))) = uVar11;
          event_id = '\x05';
          goto LAB_00096114;
        }
      }
      else {
        set_diagnostic_callback_pending_955b6(0);
      }
    }
  }
  goto LAB_0009612a;
code_r0x000960ac:
  uVar11 = uVar11 + 1;
  if (uVar11 < uVar4) {
    if ((*((int16_t *)(stack_record_25 + 1))) == 0) {
      (*((ushort *)camry_host_ptr((uint32_t)(iVar6 + -0x5a82)))) = uVar11;
      event_id = '$';
LAB_00096114:
      dcm_enqueue_event(event_id);
      uVar10 = 10;
LAB_0009612a:
      if (uVar11 == uVar4) {
        dcm_report_positive_response(((F33DcmMessageContext *)camry_host_ptr((uint32_t)(iVar6 + -0x5a7c))));
      }
      return uVar10;
    }
    operation = '\0';
  }
  goto LAB_00096124;
}
