#include "common.h"

void dispatch_pending_request_word_service_and_status_4d03e(void)

{
  ushort uVar1;
  uint32_t puVar2;
  ushort uVar3;
  
  puVar2 = 0xfebeb800u;
  uVar3 = DAT_febe81b2 & 0xff00;
  uVar1 = DAT_febe81b2 & 0xff;
  if (uVar3 != 0x1400) {
    if (uVar3 == 0x2e00) {
      if (uVar1 == 0x10) {
        start_pending_write_mode_request();
        return;
      }
      if ((DAT_febe81b2 & 0xff) != 0) {
        uVar1 = 9;
      }
      puVar2 = 0xfebeb800u;
      forward_byte_store_to_febf3b20_50094(uVar1);
    }
    else if (uVar3 == 0xba00) {
      if (uVar1 == 0x10) {
        return;
      }
      puVar2 = 0xfebeb800u;
      clear_byte_febe8195_4d4c4();
      if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x366b))))) != '\0') {
        return;
      }
    }
    (*((undefined2 *)camry_host_ptr((uint32_t)(puVar2 + -0x364e)))) = 0;
  }
  return;
}

void refresh_diagnostic_admission_and_dispatch_pending_request_4d094(void)

{
  refresh_mode_diagnostic_admission();
  dispatch_pending_request_word_service_and_status_4d03e();
  return;
}

void publish_routine_or_pending_write_terminal_result_4d0a4(byte param_1,byte param_2)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  if (param_1 < 0x10) {
    diag_routine_publish_terminal_result(param_1,param_2);
  }
  else {
    if (param_1 == 0x12) {
      puVar1 = 0xfebeb800u;
      finish_pending_write_mode_request();
    }
    if ((((*((ushort *)camry_host_ptr((uint32_t)(puVar1 + -0x364e)))) & 0xff) == 0x10) && (param_2 != 0x10)) {
      (*((ushort *)camry_host_ptr((uint32_t)(puVar1 + -0x364e)))) = (*((ushort *)camry_host_ptr((uint32_t)(puVar1 + -0x364e)))) & 0xff00 | (ushort)param_2;
    }
  }
  return;
}

void publish_result_to_active_routines3_and10_4d0e8(undefined2 param_1)

{
  if (DAT_febe819e == '\x01') {
    publish_routine_or_pending_write_terminal_result_4d0a4(3,param_1);
  }
  if (DAT_febe81a5 == '\x01') {
    publish_routine_or_pending_write_terminal_result_4d0a4(10,param_1);
  }
  return;
}

uint diag_translate_application_request_status(int application_status)

{
  if (application_status == 0) {
    return 0;
  }
  if (application_status == -0xc) {
    return 4;
  }
  if (application_status == -7) {
    return 8;
  }
  if (application_status != -6) {
    if (application_status != -1) {
      return 9;
    }
    return 2;
  }
  return 5;
}

void map_signed_error_to_diagnostic_result_byte_4d144(int param_1,undefined1 *param_2)

{
  undefined1 uVar1;
  
  if ((param_1 == -3) || (param_1 == -5)) {
    uVar1 = 0x12;
  }
  else if (param_1 == -6) {
    uVar1 = 0x22;
  }
  else if (param_1 == -0xd) {
    uVar1 = 0x11;
  }
  else if (param_1 == -0xe) {
    uVar1 = 0x33;
  }
  else {
    uVar1 = 0x10;
  }
  *param_2 = uVar1;
  return;
}

uint check_diagnostic_application_admission(uchar addressing_kind)

{
  uint uVar1;
  
  if ((DAT_febe81cc == 'Z') && (DAT_febe81ac == 'Z')) {
    uVar1 = (uint)(DAT_febe7f97 == 'Z');
  }
  else {
    uVar1 = 1;
  }
  DAT_febe819a = addressing_kind;
  return uVar1;
}

void build_available_direct_did_group_bitmap_4d1a4(int param_1,uint param_2)

{
  F33DidPublicationMetadata *pFVar1;
  byte *pbVar2;
  ushort uVar3;
  uint uVar4;
  F33DidPublicationMetadata *pFVar5;
  int iVar6;
  ushort uStack_1e;
  
  for (uVar4 = 0; uVar4 < (param_2 & 0xffff); uVar4 = uVar4 + 1 & 0xffff) {
    (*((undefined1 *)camry_host_ptr((uint32_t)(uVar4 + param_1)))) = 0;
  }
  pFVar5 = get_did_publication_metadata(&uStack_1e);
  for (iVar6 = 0;
      (int)(iVar6 - (uint)uStack_1e) < 0 != (iVar6 < 0 && -1 < (int)(iVar6 - (uint)uStack_1e));
      iVar6 = iVar6 + 1) {
    pFVar1 = pFVar5 + iVar6;
    uVar3 = pFVar1->did;
    if (((pFVar1->route_kind == '\0') && ((uVar3 & 0xff) == 0)) &&
       (((uint32_t)(pFVar1->available) == 0u|| (uVar4 = (*(int (*)())camry_indirect((uint32_t)(pFVar1->available)))(), uVar4 == 0x5a))))
    {
      uVar4 = (int)(uint)uVar3 >> 0xb;
      if (uVar4 < (param_2 & 0xff)) {
        pbVar2 = ((byte *)camry_host_ptr((uint32_t)(uVar4 + param_1)));
        *pbVar2 = *pbVar2 | (byte)(0x80 >> ((int)(uint)uVar3 >> 8 & 7U));
      }
    }
  }
  return;
}

void build_table_identifier_group_bitmap_4d222(int param_1,uint param_2)

{
  byte *pbVar1;
  ushort uVar2;
  uint uVar3;
  int iVar4;
  
  for (uVar3 = 0; uVar3 < (param_2 & 0xffff); uVar3 = uVar3 + 1 & 0xffff) {
    (*((undefined1 *)camry_host_ptr((uint32_t)(uVar3 + param_1)))) = 0;
  }
  for (iVar4 = 0;
      (int)(iVar4 - (uint)DAT_00026492) < 0 != (iVar4 < 0 && -1 < (int)(iVar4 - (uint)DAT_00026492))
      ; iVar4 = iVar4 + 1) {
    uVar2 = (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0x26918u + (uint32_t)(iVar4 * 4) * 2u))));
    if ((uVar2 & 0xff) == 0) {
      uVar3 = (int)(uint)uVar2 >> 0xb;
      if (uVar3 < (param_2 & 0xff)) {
        pbVar1 = ((byte *)camry_host_ptr((uint32_t)(uVar3 + param_1)));
        *pbVar1 = *pbVar1 | (byte)(0x80 >> ((int)(uint)uVar2 >> 8 & 7U));
      }
    }
  }
  return;
}

void serialize_available_did_bitmap(ushort did_page,uchar *output,ushort length)

{
  F33DidPublicationMetadata *pFVar1;
  uint uVar2;
  F33DidPublicationMetadata *pFVar3;
  uint uVar4;
  int iVar5;
  ushort uStack_26;
  
  for (uVar2 = 0; uVar2 < length; uVar2 = uVar2 + 1 & 0xffff) {
    output[uVar2] = '\0';
  }
  pFVar3 = get_did_publication_metadata(&uStack_26);
  for (iVar5 = 0;
      (int)(iVar5 - (uint)uStack_26) < 0 != (iVar5 < 0 && -1 < (int)(iVar5 - (uint)uStack_26));
      iVar5 = iVar5 + 1) {
    pFVar1 = pFVar3 + iVar5;
    uVar2 = (uint)pFVar1->did;
    if ((((pFVar1->route_kind == '\0') && ((did_page & 0xff00) < uVar2)) &&
        (uVar2 < ((did_page & 0xff00) + 0x100 & 0xffff))) &&
       (((uint32_t)(pFVar1->available) == 0u|| (uVar4 = (*(int (*)())camry_indirect((uint32_t)(pFVar1->available)))(), uVar4 == 0x5a))))
    {
      uVar4 = (int)(uVar2 - 1 & 0xff) >> 3;
      if (uVar4 < (length & 0xff)) {
        output[uVar4] = output[uVar4] | (byte)(0x80 >> (uVar2 - 1 & 7));
      }
    }
  }
  return;
}

void build_identifier_page_member_bitmap_4d308(uint param_1,int param_2,uint param_3)

{
  byte *pbVar1;
  uint uVar2;
  int iVar3;
  uint uVar4;
  
  for (uVar2 = 0; uVar2 < (param_3 & 0xffff); uVar2 = uVar2 + 1 & 0xffff) {
    (*((undefined1 *)camry_host_ptr((uint32_t)(uVar2 + param_2)))) = 0;
  }
  for (iVar3 = 0;
      (int)(iVar3 - (uint)DAT_00026492) < 0 != (iVar3 < 0 && -1 < (int)(iVar3 - (uint)DAT_00026492))
      ; iVar3 = iVar3 + 1) {
    param_1 = param_1 & 0xff00;
    uVar2 = (uint)(ushort)(*((volatile uint16_t *)camry_host_ptr((uint32_t)(0x26918u + (uint32_t)(iVar3 * 4) * 2u))));
    if ((param_1 < uVar2) && (uVar2 < (param_1 + 0x100 & 0xffff))) {
      uVar4 = (int)(uVar2 - 1 & 0xff) >> 3;
      if (uVar4 < (param_3 & 0xff)) {
        pbVar1 = ((byte *)camry_host_ptr((uint32_t)(uVar4 + param_2)));
        *pbVar1 = *pbVar1 | (byte)(0x80 >> (uVar2 - 1 & 7));
      }
    }
  }
  return;
}

uint select_available_did_metadata(ushort did)

{
  F33DidPublicationMetadata *pFVar1;
  uint32_t puVar2;
  F33DidPublicationMetadata *pFVar3;
  uint uVar4;
  int iVar5;
  ushort uStack_12;
  
  puVar2 = 0xfebeb800u;
  pFVar3 = get_did_publication_metadata(&uStack_12);
  iVar5 = 0;
  while( true ) {
    if ((int)(iVar5 - (uint)uStack_12) < 0 == (iVar5 < 0 && -1 < (int)(iVar5 - (uint)uStack_12))) {
      return 3;
    }
    pFVar1 = pFVar3 + iVar5;
    if ((pFVar1->route_kind == '\0') && (pFVar1->did == did)) break;
    iVar5 = iVar5 + 1;
  }
  if (((uint32_t)(pFVar1->available) != 0u) && (uVar4 = (*(int (*)())camry_indirect((uint32_t)(pFVar1->available)))(camry_host_addr(&uStack_12)), uVar4 != 0x5a)) {
    return 3;
  }
  (*((short *)camry_host_ptr((uint32_t)(puVar2 + -0x3648)))) = (short)iVar5;
  return 0;
}

uint did_available_4d3be(void)

{
  if (DAT_febee91c == -0x55aaaa56) {
    return 0x5a;
  }
  return 0;
}

uint did_available_4d3d6(void)

{
  uint uVar1;
  
  if (DAT_febee802 == 'Z') {
    uVar1 = 0x5a;
  }
  else {
    uVar1 = 0;
  }
  return uVar1;
}

uint did_available_4d3e4(void)

{
  uint uVar1;
  
  if (DAT_febee804 == 'Z') {
    uVar1 = 0x5a;
  }
  else {
    uVar1 = 0;
  }
  return uVar1;
}

uint did_available_4d3f2(void)

{
  uint uVar1;
  
  if (DAT_febee803 == 'Z') {
    uVar1 = 0x5a;
  }
  else {
    uVar1 = 0;
  }
  return uVar1;
}

uint did_available_4d400(void)

{
  uint uVar1;
  
  uVar1 = 0x5a;
  if (DAT_febee870 == 'Z') {
    uVar1 = 0;
  }
  return uVar1;
}

uint did_available_4d412(void)

{
  uint uVar1;
  
  if (DAT_febee870 == 'Z') {
    uVar1 = 0x5a;
  }
  else {
    uVar1 = 0;
  }
  return uVar1;
}

uint did_available_4d420(void)

{
  uint uVar1;
  
  if (DAT_febee805 == 'Z') {
    uVar1 = 0x5a;
  }
  else {
    uVar1 = 0;
  }
  return uVar1;
}

uint did_available_4d42e(void)

{
  uint uVar1;
  
  if (DAT_febee806 == 'Z') {
    uVar1 = 0x5a;
  }
  else {
    uVar1 = 0;
  }
  return uVar1;
}

uint did_metadata_always_available(void)

{
  return 0x5a;
}

uint did_always_available(void)

{
  return 0x5a;
}

void get_selected_did_payload_length(ushort *length)

{
  ushort uVar1;
  uint32_t puVar2;
  F33DidPublicationMetadata *pFVar3;
  ushort uStack_a;
  
  puVar2 = 0xfebeb800u;
  pFVar3 = get_did_publication_metadata(&uStack_a);
  uVar1 = 0;
  if ((uint)(*((ushort *)camry_host_ptr((uint32_t)(puVar2 + -0x3648)))) < (uint)uStack_a) {
    uVar1 = pFVar3[(*((ushort *)camry_host_ptr((uint32_t)(puVar2 + -0x3648))))].payload_length;
  }
  *length = uVar1;
  return;
}

void clear_word_febe81c8_4d4bc(void)

{
  DAT_febe81c8 = 0;
  return;
}

void return_only_stub_4d4c2(void)

{
  return;
}

void clear_byte_febe8195_4d4c4(void)

{
  DAT_febe8195 = 0;
  return;
}

void complete_ba10_pending_result_4d4ca(uint param_1,uint param_2)

{
  param_2 = param_2 & 0xff;
  if (((int16_t)DAT_febe81b2) == -0x45f0) {
    DAT_febe8194 = 0;
    DAT_febe81b2 = -0x4600;
    if ((int)param_1 < 0) {
      param_2 = param_1;
    }
    DAT_febe8195 = 0x5a;
    DAT_febe81c0 = param_2;
  }
  return;
}

undefined1 map_signed_result_with_zero_and_minus_one_cases_4d4f2(int param_1)

{
  undefined1 uStack_5;
  
  uStack_5 = 0;
  if (param_1 == 0) {
    uStack_5 = 0;
  }
  else if (param_1 == -1) {
    uStack_5 = 2;
  }
  else {
    map_signed_error_to_diagnostic_result_byte_4d144(param_1,&uStack_5);
  }
  return uStack_5;
}

uchar begin_proprietary_operation
                (uchar operation,F33DiagProprietaryMessage *message,uchar *selected_index)

{
  undefined2 uVar1;
  uint32_t puVar2;
  uchar uVar3;
  int iVar4;
  
  puVar2 = 0xfebeb800u;
  if (operation == '\0') {
    DAT_febe81c8 = camry_host_addr(message);
    iVar4 = dispatch_ba_configured_start
                      ((uchar)message->request_length, ((uchar *)camry_host_ptr((uint32_t)(message->request))), ((uchar *)camry_host_ptr((uint32_t)(message->response + 1))), 
                       selected_index);
    uVar1 = 0xba10;
    if (iVar4 != -1) {
      uVar1 = 0xba00;
    }
    (*((undefined2 *)camry_host_ptr((uint32_t)(puVar2 + -0x364e)))) = uVar1;
  }
  else {
    iVar4 = 0;
    dcm_complete_proprietary_message(message);
  }
  uVar3 = map_signed_result_with_zero_and_minus_one_cases_4d4f2(iVar4);
  return uVar3;
}

uchar finish_proprietary_operation(uchar selected_index,uint *response_length)

{
  undefined2 uVar1;
  uint32_t puVar2;
  uchar uVar3;
  int iVar4;
  
  puVar2 = 0xfebeb800u;
  iVar4 = dispatch_ba_configured_finish(selected_index,response_length);
  uVar1 = 0xba10;
  if (iVar4 != -1) {
    uVar1 = 0xba00;
  }
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar2 + -0x364e)))) = uVar1;
  uVar3 = map_signed_result_with_zero_and_minus_one_cases_4d4f2(iVar4);
  return uVar3;
}

void diagnostic_session_changed_application(uchar old_session,uchar new_session)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  app_security_reset_challenge_material();
  if ((new_session == '\x01') || ((old_session == '\x01' && (new_session == '@')))) {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x366a))))) = 0;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x3669))))) = 0;
    thunk_set_byte_febeaf47_b9320(0x88);
    diag_routine_clear_nonrunning_results('\0');
  }
  return;
}

uint app_session_transition_precondition(uchar current_session_ignored,uchar target)

{
  if ((target == '\x02') && (communication_control_admission_limit < DAT_febee892)) {
    return 0xb;
  }
  return 0;
}

undefined1 test_mode_or_low_66ba_or_latched_condition_4d5d8(void)

{
  undefined1 uVar1;
  
  if (((DAT_febee81f == '\x11') || (DAT_febe66ba < DAT_000318b2)) ||
     (uVar1 = 0, DAT_febe819a != '\0')) {
    uVar1 = 1;
  }
  return uVar1;
}

void clear_programming_mode_request_latch_4d5fe(void)

{
  app_programming_mode_request_latched = '\0';
  return;
}

void app_request_programming_transition(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  if (DAT_febe819a == '\0') {
    if (app_programming_mode_request_latched == '\0') {
      thunk_set_indexed_request_and_clear_complement_b15ac(9);
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x3652))))) = 0x5a;
    }
  }
  else {
    call_98898_with_zero_byte_8b120();
    restore_default_dcm_session_when_not_busy_91b50();
    set_matching_dcm_communication_mode_two_917a4(0);
    run_init_chain_8e62a();
  }
  return;
}

ushort diagnostic_clear_request_callback(void)

{
  ushort uVar1;
  ushort uVar2;
  
  if (DAT_febe81b2 == 0) {
    DAT_febe81b2 = 0x1410;
    request_diagnostic_clear();
    uVar2 = 4;
  }
  else if ((DAT_febe81b2 & 0xff00) == 0x1400) {
    uVar1 = DAT_febe81b2 & 0xff;
    uVar2 = DAT_febe81b2 & 0xff;
    if (uVar2 == 0x10) {
      uVar2 = 4;
    }
    else {
      DAT_febe81b2 = 0;
      if (uVar1 != 0) {
        uVar2 = 6;
      }
    }
  }
  else {
    uVar2 = 6;
  }
  return uVar2;
}

uint validate_clear_all_diagnostic_group(uint group)

{
  return (uint)(group != 0xffffff);
}

uint get_dtc_status_availability_mask(uchar *mask)

{
  *mask = 0xb9;
  return 0;
}

uint begin_filtered_dtc_iteration(uchar mask)

{
  dtc_requested_status_mask = mask & 0xb9;
  dtc_iteration_result_count = 0;
  dtc_iteration_catalogue_cursor = 0;
  return 0;
}

undefined4 store_masked_dtc_count_capped_at1023_4d6ae(undefined2 *param_1)

{
  uint uVar1;
  
  if (camry_host_addr((param_1))!= 0) {
    uVar1 = count_nonzero_dtcs_matching_status_mask_526cc(dtc_requested_status_mask);
    if (0x3ff < uVar1) {
      uVar1 = 0x3ff;
    }
    *param_1 = (short)uVar1;
  }
  return 0;
}

uint next_filtered_dtc(uint *dtc,uchar *status)

{
  uint8_t stack_record_15[21];
  ushort uVar1;
  uint32_t puVar2;
  uint uVar3;
  
  uVar1 = dtc_iteration_result_count;
  puVar2 = 0xfebeb800u;
  if ((((camry_host_addr((dtc))== 0) || (camry_host_addr((status))== 0)) ||
      (uVar3 = scan_dtc_status_snapshot
                         (dtc_requested_status_mask,((uint32_t *)((stack_record_15 + 1))),((uint8_t *)(stack_record_15)),
                          dtc_iteration_catalogue_cursor + 1), uVar3 == 0)) ||
     (0x3ff < (ushort)(uVar1 + 1))) {
    uVar3 = 1;
  }
  else {
    (*((short *)camry_host_ptr((uint32_t)(puVar2 + -0x364a)))) = (short)uVar3;
    (*((ushort *)camry_host_ptr((uint32_t)(puVar2 + -0x364c)))) = uVar1 + 1;
    uVar3 = 0;
    *dtc = (*((uint32_t *)(stack_record_15 + 1)));
    *status = stack_record_15[0];
  }
  return uVar3;
}

uint next_snapshot_identifier_tuple(uint *dtc,uchar *record_number)

{
  uint32_t puVar1;
  byte bVar2;
  uint uVar3;
  uchar uVar4;
  uint local_10;
  
  puVar1 = 0xfebeb800u;
  uVar3 = (uint)DAT_febe8199;
  local_10 = snapshot_identifier_cached_dtc;
  if ((camry_host_addr((dtc))== 0) || (camry_host_addr((record_number))== 0)) {
LAB_0004d786:
    local_10 = 0;
    bVar2 = 0;
    uVar3 = 1;
  }
  else {
    puVar1 = 0xfebeb800u;
    if (snapshot_identifier_cached_dtc == 0) {
      puVar1 = 0xfebeb800u;
      uVar3 = get_secondary_capture_record_mask(&local_10);
    }
    if ((uVar3 & 1) == 0) {
      if ((uVar3 >> 1 & 1) == 0) goto LAB_0004d786;
      bVar2 = (byte)uVar3 & 0xfd;
      uVar4 = '\x10';
      *dtc = local_10;
    }
    else {
      bVar2 = (byte)uVar3 & 0xfe;
      uVar4 = '\x01';
      *dtc = local_10;
    }
    *record_number = uVar4;
    uVar3 = 0;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x3667))))) = bVar2;
  (*((uint *)camry_host_ptr((uint32_t)(puVar1 + -0x363c)))) = local_10;
  return uVar3;
}

undefined4 read_dtc_status_with_zero_success_code_4d79a(undefined4 param_1,undefined4 param_2,undefined1 *param_3)

{
  int iVar1;
  undefined4 uVar2;
  undefined1 uStack_9;
  
  if ((camry_host_addr((param_3))== 0) || (iVar1 = lookup_dtc_code_and_store_composed_status_52922(param_1, camry_host_addr(&uStack_9)), iVar1 != 0x5a)) {
    uVar2 = 1;
  }
  else {
    uVar2 = 0;
    *param_3 = uStack_9;
  }
  return uVar2;
}

undefined4 read_retained_capture_and_update_result_length_4d7c4(undefined4 param_1,char param_2,int param_3,ushort *param_4)

{
  int iVar1;
  ushort uVar2;
  uint uVar3;
  
  if ((param_3 != 0) && (camry_host_addr((param_4))!= 0)) {
    if ((param_2 != '\x01') && (param_2 != '\x10')) {
      return 3;
    }
    uVar2 = *param_4;
    uVar3 = serialize_matching_retained_capture_record_view_53298(param_1, (uint)(byte)param_2, param_3, (*((volatile uint16_t *)((uint8_t *)(param_4) + (0)))));
    if ((-1 < (int)uVar3) &&
       (iVar1 = uVar3 - uVar2, iVar1 < 0 != ((int)uVar3 < 0 && -1 < iVar1) || uVar3 == uVar2)) {
      *param_4 = (ushort)uVar3;
      return 0;
    }
  }
  return 4;
}

uint read_selected_did_payload(uchar *output,ushort length)

{
  uint32_t puVar1;
  F33DidPublicationMetadata *pFVar2;
  uint uVar3;
  ushort uStack_e;
  
  puVar1 = 0xfebeb800u;
  pFVar2 = get_did_publication_metadata(&uStack_e);
  if ((uint)(*((ushort *)camry_host_ptr((uint32_t)(puVar1 + -0x3648)))) < (uint)uStack_e) {
    uVar3 = (*(int (*)())camry_indirect((uint32_t)(pFVar2[(*((ushort *)camry_host_ptr((uint32_t)(puVar1 + -0x3648))))].reader)))(camry_host_addr(output),length);
  }
  else {
    uVar3 = 3;
  }
  return uVar3;
}

uchar get_did_metadata_route_kind(ushort did)

{
  uint uVar1;
  F33DidPublicationMetadata *pFVar2;
  uchar uVar3;
  ushort uStack_e;
  
  uVar3 = 0xff;
  pFVar2 = get_did_publication_metadata(&uStack_e);
  for (uVar1 = 0; (int)(uVar1 - uStack_e) < 0 != ((int)uVar1 < 0 && -1 < (int)(uVar1 - uStack_e));
      uVar1 = uVar1 + 1) {
    if (pFVar2[uVar1].did == did) {
      uVar3 = pFVar2[uVar1 & 0xffff].route_kind;
    }
  }
  return uVar3;
}

undefined4 rdbi_0102_callback(int param_1)

{
  uint8_t stack_record_f[15];
  
  if (DAT_febee813 == 'Z') {
    (*((uint32_t *)(stack_record_f + 3))) = DAT_febee90c;
    (*((uint16_t *)(stack_record_f + 1))) = DAT_febee896;
    stack_record_f[0] = DAT_febee815;
    store_min_u16_70180(DAT_febee896,0xfffe,(stack_record_f + 1));
    store_min_u32_70192((*((uint32_t *)(stack_record_f + 3))),(int)0xfffffffe,(stack_record_f + 3));
    store_minimum_u8_7016e(stack_record_f[0],1,stack_record_f);
  }
  else {
    (*((uint16_t *)(stack_record_f + 1))) = 0xffff;
    (*((uint32_t *)(stack_record_f + 3))) = 0xffffffff;
    stack_record_f[0] = 0;
  }
  store_low_u16_big_endian_bytes_6a574((*((uint16_t *)(stack_record_f + 1))), ((undefined1 *)camry_host_ptr((uint32_t)(param_1))));
  store_u32_big_endian_bytes_6a55c((*((uint32_t *)(stack_record_f + 3))), ((undefined1 *)camry_host_ptr((uint32_t)(param_1 + 2))));
  (*((undefined1 *)camry_host_ptr((uint32_t)(param_1 + 6)))) = stack_record_f[0];
  return 0;
}

undefined4 rdbi_0103_callback(undefined1 *param_1)

{
  uint32_t puVar1;
  undefined1 uStack_d;
  
  puVar1 = ((uint32_t)(DAT_febee910));
  if (DAT_febee813 == 'Z') {
    uStack_d = DAT_febee814;
    store_minimum_u8_7016e(DAT_febee814,2,&uStack_d);
    if ((puVar1)<((uint32_t)(0xf4240u))) goto LAB_0004d926;
  }
  else {
    uStack_d = 0;
  }
  puVar1 = (0x0);
LAB_0004d926:
  store_u32_big_endian_bytes_6a55c((puVar1), param_1);
  *param_1 = uStack_d;
  return 0;
}

undefined4 rdbi_0105_callback(int param_1)

{
  uint8_t stack_record_18[24];
  int iVar1;
  int iVar2;
  uint *puVar3;
  int iVar4;
  uint uVar5;
  undefined4 uVar6;
  undefined4 *puVar7;
  
  puVar3 = stack_record_18;
  puVar7 = ((undefined *)camry_host_ptr(0x212f8u));
  do {
    uVar6 = *puVar7;
    puVar7 = puVar7 + 1;
    *puVar3 = uVar6;
    puVar3 = puVar3 + 1;
  } while (camry_host_addr(puVar7)!=((uint32_t)(0x21308u)));
  uVar5 = nvm_get_record(0x204, camry_host_addr(stack_record_18));
  if ((uVar5 == 0x10) && ((*((uint32_t *)(stack_record_18 + 0))) == 0xa55a5aa5)) {
    iVar4 = 0;
    do {
      iVar2 = iVar4 + 1;
      iVar1 = iVar4 + -9;
      (*((undefined1 *)camry_host_ptr((uint32_t)(iVar4 + param_1)))) = (stack_record_18 + 4)[iVar4];
      iVar4 = iVar2;
    } while (((iVar1 < 0) || (iVar2 < 0)));
  }
  else {
    iVar4 = 0;
    do {
      iVar2 = iVar4 + 1;
      (*((undefined1 *)camry_host_ptr((uint32_t)(iVar4 + param_1)))) = 0x3f;
      iVar1 = iVar4 + -9;
      iVar4 = iVar2;
    } while (((iVar1 < 0) || (iVar2 < 0)));
  }
  (*((undefined1 *)camry_host_ptr((uint32_t)(param_1 + 10)))) = 0;
  (*((undefined1 *)camry_host_ptr((uint32_t)(param_1 + 0xb)))) = 0;
  return 0;
}

undefined4 rdbi_0109_callback(undefined1 *param_1)

{
  undefined1 uVar1;
  undefined1 uVar2;
  undefined1 uVar3;
  undefined1 uVar4;
  undefined1 uVar5;
  undefined1 uVar6;
  
  uVar1 = DAT_febee867;
  uVar6 = DAT_febee868;
  uVar5 = DAT_febee869;
  uVar4 = DAT_febee86a;
  uVar3 = DAT_febee86b;
  uVar2 = DAT_febee86c;
  if (DAT_febee813 != 'Z') {
    uVar1 = 0xff;
    uVar6 = 0xff;
    uVar5 = 0xff;
    uVar4 = 0xff;
    uVar3 = 0xff;
    uVar2 = 0xff;
  }
  *param_1 = uVar1;
  param_1[1] = uVar6;
  param_1[2] = uVar5;
  param_1[3] = uVar4;
  param_1[4] = uVar3;
  param_1[5] = uVar2;
  return 0;
}

undefined4 rdbi_010b_callback(int param_1)

{
  uint8_t stack_record_20[32];
  int iVar1;
  int iVar2;
  uint *puVar3;
  int iVar4;
  uint uVar5;
  undefined4 uVar6;
  undefined4 *puVar7;
  
  puVar3 = stack_record_20;
  puVar7 = ((undefined *)camry_host_ptr(0x21308u));
  do {
    uVar6 = *puVar7;
    puVar7 = puVar7 + 1;
    *puVar3 = uVar6;
    puVar3 = puVar3 + 1;
  } while (camry_host_addr(puVar7)!=((uint32_t)(0x21320u)));
  uVar5 = nvm_get_record(0x20a, camry_host_addr(stack_record_20));
  if ((uVar5 == 0x10) && ((*((uint32_t *)(stack_record_20 + 0))) == 0xa55a5aa5)) {
    uVar6 = 0;
    iVar4 = 0;
    do {
      iVar2 = iVar4 + 1;
      iVar1 = iVar4 + -0xf;
      (*((undefined1 *)camry_host_ptr((uint32_t)(iVar4 + param_1)))) = (stack_record_20 + 4)[iVar4];
      iVar4 = iVar2;
    } while (((iVar1 < 0) || (iVar2 < 0)));
  }
  else {
    uVar6 = 5;
  }
  return uVar6;
}

undefined4 rdbi_0110_callback(undefined4 param_1)

{
  uint32_t puVar1;
  int iVar2;
  uint uVar3;
  
  puVar1 = 0xfebeb800u;
  uVar3 = get_febe505c_word_6a130();
  if (~(*((uint *)camry_host_ptr((uint32_t)(puVar1 + -0x2e1c)))) < uVar3) {
    iVar2 = -1;
  }
  else {
    iVar2 = uVar3 + (*((uint *)camry_host_ptr((uint32_t)(puVar1 + -0x2e1c))));
  }
  store_u32_big_endian_bytes_6a55c(iVar2, ((undefined1 *)camry_host_ptr((uint32_t)(param_1))));
  return 0;
}

undefined4 rdbi_0111_callback(void)

{
  return 0;
}

undefined4 rdbi_0112_callback(undefined4 param_1)

{
  int iVar1;
  
  if (~DAT_febe89ec < DAT_febe8afc) {
    iVar1 = -1;
  }
  else {
    iVar1 = DAT_febe8afc + DAT_febe89ec;
  }
  store_u32_big_endian_bytes_6a55c(iVar1, ((undefined1 *)camry_host_ptr((uint32_t)(param_1))));
  return 0;
}

undefined4 rdbi_0204_callback(undefined1 *param_1)

{
  char cVar1;
  undefined1 uVar2;
  
  cVar1 = DAT_febee856;
  *param_1 = 0x80;
  uVar2 = 0;
  if (cVar1 == '\x11') {
    uVar2 = 0x80;
  }
  param_1[1] = uVar2;
  return 0;
}

undefined4 rdbi_1031_callback(undefined4 param_1)

{
  uint uVar1;
  undefined2 uStack_a;
  
  uVar1 = (uint)DAT_febee894 * 10 >> 7;
  uStack_a = (undefined2)uVar1;
  store_min_u16_70180(uVar1,3000,&uStack_a);
  store_low_u16_big_endian_bytes_6a574(uStack_a, ((undefined1 *)camry_host_ptr((uint32_t)(param_1))));
  return 0;
}

undefined4 rdbi_1032_callback(undefined4 param_1)

{
  undefined2 uStack_a;
  
  uStack_a = DAT_febee890;
  store_min_u16_70180(DAT_febee890,0x3200,&uStack_a);
  store_low_u16_big_endian_bytes_6a574(uStack_a, ((undefined1 *)camry_host_ptr((uint32_t)(param_1))));
  return 0;
}

undefined4 rdbi_1033_callback(undefined1 *param_1)

{
  undefined1 uStack_9;
  
  uStack_9 = DAT_febee811;
  store_minimum_u8_7016e(DAT_febee811,1,&uStack_9);
  *param_1 = uStack_9;
  return 0;
}

uint rdbi_1034_callback(uchar *output)

{
  undefined2 uStack_a;
  
  uStack_a = (undefined2)((uint)DAT_febe66ba * 100 >> 8);
  store_min_u16_70180((uint)DAT_febe66ba * 100 >> 8,0x9c4,&uStack_a);
  store_low_u16_big_endian_bytes_6a574(uStack_a,output);
  return 0;
}

undefined4 did_1035_steering_wheel_torque(undefined4 param_1)

{
  int iVar1;
  int local_c;
  
  if (DAT_febe6af0 == -0x5aa5a55b) {
    local_c = (((int)(int16_t)DAT_febe66a8) * 1000) / 0x100;
    store_s32_max_third_min_first_two_7012a(local_c,25000,(int)0xffff9e58,&local_c);
    iVar1 = (int)(short)local_c;
  }
  else {
    iVar1 = -0x8000;
  }
  store_low_u16_big_endian_bytes_6a5ac(iVar1, ((undefined1 *)camry_host_ptr((uint32_t)(param_1))));
  return 0;
}

undefined4 did_1036_steering_angle_velocity(undefined4 param_1)

{
  short sStack_a;
  
  sStack_a = (short)((((int)(int16_t)DAT_febe66a4) * 0x168) / 0x400);
  store_s16_max_third_min_first_two_70110((int)sStack_a,0x7fff,(int)0xffff8000,&sStack_a);
  store_low_u16_big_endian_bytes_6a5ac((int)sStack_a, ((undefined1 *)camry_host_ptr((uint32_t)(param_1))));
  return 0;
}

undefined4 did_1037_steering_angle(undefined4 param_1)

{
  short sStack_a;
  
  sStack_a = ((int)(int16_t)DAT_febe7d46);
  store_s16_max_third_min_first_two_70110((int)((int)(int16_t)DAT_febe7d46),0x7ff,(int)0xfffff800,&sStack_a);
  store_low_u16_big_endian_bytes_6a5ac((int)sStack_a, ((undefined1 *)camry_host_ptr((uint32_t)(param_1))));
  return 0;
}

undefined4 rdbi_1038_callback(byte *param_1)

{
  *param_1 = DAT_febe7fec & 0xf;
  return 0;
}

undefined4 rdbi_1061_callback(undefined4 param_1)

{
  undefined2 uStack_a;
  
  uStack_a = (undefined2)((uint)DAT_febe66b8 * 100 >> 8);
  store_min_u16_70180((uint)DAT_febe66b8 * 100 >> 8,0x9c4,&uStack_a);
  store_low_u16_big_endian_bytes_6a574(uStack_a, ((undefined1 *)camry_host_ptr((uint32_t)(param_1))));
  return 0;
}

undefined4 rdbi_1062_callback(undefined4 param_1)

{
  undefined2 uStack_a;
  
  uStack_a = (undefined2)((uint)DAT_febe66ae * 100 >> 8);
  store_min_u16_70180((uint)DAT_febe66ae * 100 >> 8,0x9c4,&uStack_a);
  store_low_u16_big_endian_bytes_6a574(uStack_a, ((undefined1 *)camry_host_ptr((uint32_t)(param_1))));
  return 0;
}

uint rdbi_1063_callback(uchar *output)

{
  short sStack_a;
  
  sStack_a = (short)((((int)(int16_t)DAT_febe7dda) * 10) / 0x80);
  store_s16_max_third_min_first_two_70110((int)sStack_a,2000,(int)0xfffffe0c,&sStack_a);
  store_low_u16_big_endian_bytes_6a5ac((int)sStack_a,output);
  return 0;
}

undefined4 rdbi_1064_callback(undefined1 *param_1)

{
  undefined1 uStack_9;
  
  uStack_9 = DAT_febee829;
  store_minimum_u8_7016e(DAT_febee829,2,&uStack_9);
  *param_1 = uStack_9;
  return 0;
}

undefined4 rdbi_1065_callback(undefined1 *param_1)

{
  undefined1 uStack_9;
  
  uStack_9 = 0 < ((int)(int16_t)DAT_febe678c);
  store_minimum_u8_7016e(uStack_9,1,&uStack_9);
  *param_1 = uStack_9;
  return 0;
}

undefined4 rdbi_1066_callback(void)

{
  return 0;
}

undefined4 rdbi_106a_callback(void)

{
  return 0;
}

undefined4 rdbi_106b_callback(undefined4 param_1)

{
  undefined2 uStack_a;
  
  uStack_a = (undefined2)((uint)DAT_febe66b2 * 100 >> 8);
  store_min_u16_70180((uint)DAT_febe66b2 * 100 >> 8,0x9c4,&uStack_a);
  store_low_u16_big_endian_bytes_6a574(uStack_a, ((undefined1 *)camry_host_ptr((uint32_t)(param_1))));
  return 0;
}

undefined4 rdbi_1091_callback(undefined4 param_1)

{
  int local_c;
  
  local_c = (((int)(int16_t)DAT_febe64f2) * 1000) / 0x100;
  store_s32_max_third_min_first_two_7012a(local_c,25000,(int)0xffff9e58,&local_c);
  store_low_u16_big_endian_bytes_6a5ac((int)(short)local_c, ((undefined1 *)camry_host_ptr((uint32_t)(param_1))));
  return 0;
}

undefined4 rdbi_1092_callback(undefined4 param_1)

{
  int local_c;
  
  local_c = (((int)(int16_t)DAT_febe64f4) * 1000) / 0x100;
  store_s32_max_third_min_first_two_7012a(local_c,25000,(int)0xffff9e58,&local_c);
  store_low_u16_big_endian_bytes_6a5ac((int)(short)local_c, ((undefined1 *)camry_host_ptr((uint32_t)(param_1))));
  return 0;
}

undefined4 rdbi_1093_callback(undefined4 param_1)

{
  int local_c;
  
  local_c = (((int)(int16_t)DAT_febe64f6) * 1000) / 0x100;
  store_s32_max_third_min_first_two_7012a(local_c,25000,(int)0xffff9e58,&local_c);
  store_low_u16_big_endian_bytes_6a5ac((int)(short)local_c, ((undefined1 *)camry_host_ptr((uint32_t)(param_1))));
  return 0;
}

undefined4 rdbi_1094_callback(undefined4 param_1)

{
  int local_c;
  
  local_c = (((int)(int16_t)DAT_febe64f8) * 1000) / 0x100;
  store_s32_max_third_min_first_two_7012a(local_c,25000,(int)0xffff9e58,&local_c);
  store_low_u16_big_endian_bytes_6a5ac((int)(short)local_c, ((undefined1 *)camry_host_ptr((uint32_t)(param_1))));
  return 0;
}

undefined4 rdbi_1095_callback(undefined4 param_1)

{
  undefined2 uStack_a;
  
  uStack_a = DAT_febe66d6;
  store_min_u16_70180(DAT_febe66d6,0xffff,&uStack_a);
  store_low_u16_big_endian_bytes_6a574(uStack_a, ((undefined1 *)camry_host_ptr((uint32_t)(param_1))));
  return 0;
}

undefined4 rdbi_1096_callback(undefined4 param_1)

{
  undefined2 uStack_a;
  
  uStack_a = DAT_febe66d8;
  store_min_u16_70180(DAT_febe66d8,0xffff,&uStack_a);
  store_low_u16_big_endian_bytes_6a574(uStack_a, ((undefined1 *)camry_host_ptr((uint32_t)(param_1))));
  return 0;
}

undefined4 rdbi_1097_callback(undefined4 param_1)

{
  undefined2 uStack_a;
  
  uStack_a = DAT_febe66da;
  store_min_u16_70180(DAT_febe66da,0xffff,&uStack_a);
  store_low_u16_big_endian_bytes_6a574(uStack_a, ((undefined1 *)camry_host_ptr((uint32_t)(param_1))));
  return 0;
}

undefined4 rdbi_1098_callback(undefined4 param_1)

{
  undefined2 uStack_a;
  
  uStack_a = DAT_febe66dc;
  store_min_u16_70180(DAT_febe66dc,0xffff,&uStack_a);
  store_low_u16_big_endian_bytes_6a574(uStack_a, ((undefined1 *)camry_host_ptr((uint32_t)(param_1))));
  return 0;
}

undefined4 rdbi_10c1_callback(undefined4 param_1)

{
  short sStack_a;
  
  sStack_a = (short)((((int)(int16_t)DAT_febe6654) * 100) / 0x80);
  store_s16_max_third_min_first_two_70110((int)sStack_a,0x7fff,(int)0xffff8000,&sStack_a);
  store_low_u16_big_endian_bytes_6a5ac((int)sStack_a, ((undefined1 *)camry_host_ptr((uint32_t)(param_1))));
  return 0;
}

undefined4 rdbi_10c2_callback(undefined4 param_1)

{
  short sStack_a;
  
  sStack_a = (short)((((int)(int16_t)DAT_febe6656) * 100) / 0x80);
  store_s16_max_third_min_first_two_70110((int)sStack_a,0x7fff,(int)0xffff8000,&sStack_a);
  store_low_u16_big_endian_bytes_6a5ac((int)sStack_a, ((undefined1 *)camry_host_ptr((uint32_t)(param_1))));
  return 0;
}

undefined4 rdbi_10c3_callback(undefined4 param_1)

{
  short sStack_a;
  
  sStack_a = (short)((((int)(int16_t)DAT_febe6658) * 100) / 0x80);
  store_s16_max_third_min_first_two_70110((int)sStack_a,0x7fff,(int)0xffff8000,&sStack_a);
  store_low_u16_big_endian_bytes_6a5ac((int)sStack_a, ((undefined1 *)camry_host_ptr((uint32_t)(param_1))));
  return 0;
}

undefined4 rdbi_10c4_callback(undefined4 param_1)

{
  uint uVar1;
  undefined2 uStack_a;
  
  uVar1 = (uint)DAT_febe64a2 * 0x271 >> 0xb;
  uStack_a = (undefined2)uVar1;
  store_min_u16_70180(uVar1,10000,&uStack_a);
  store_low_u16_big_endian_bytes_6a574(uStack_a, ((undefined1 *)camry_host_ptr((uint32_t)(param_1))));
  return 0;
}

undefined4 rdbi_10c5_callback(undefined4 param_1)

{
  uint uVar1;
  undefined2 uStack_a;
  
  uVar1 = (uint)DAT_febe64a4 * 0x271 >> 0xb;
  uStack_a = (undefined2)uVar1;
  store_min_u16_70180(uVar1,10000,&uStack_a);
  store_low_u16_big_endian_bytes_6a574(uStack_a, ((undefined1 *)camry_host_ptr((uint32_t)(param_1))));
  return 0;
}
