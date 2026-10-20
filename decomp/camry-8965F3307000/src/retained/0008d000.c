#include "common.h"

undefined4 append_snapshot_records_until_end_or_yield_8d020(undefined4 param_1,undefined4 param_2,char param_3,undefined1 *param_4)

{
  uint8_t stack_record_2c[44];
  short sVar1;
  undefined1 uVar2;
  undefined1 uVar3;
  undefined1 *puVar4;
  uint32_t extraout_r9;
  int iVar5;
  undefined4 uVar6;
  undefined1 uVar7;
  undefined1 uVar8;
  char cVar9;
  uint uVar10;
  char *pcVar11;
  
  sVar1 = (short)dcm_snapshot_record_message.response_capacity;
  uVar8 = 0;
  uVar7 = 0;
  uVar10 = dcm_snapshot_record_message.response_length & 0xffff;
  cVar9 = '\0';
  stack_record_2c[0] = '\0';
  stack_record_2c[1] = '\0';
  puVar4 = param_4;
  do {
    cVar9 = cVar9 + '\x01';
    (*((uint16_t *)(stack_record_2c + 2))) = sVar1 - (short)uVar10;
    iVar5 = read_retained_capture_and_update_result_length_4d7c4(param_1,*puVar4,dcm_snapshot_record_message.response + uVar10,
                         (stack_record_2c + 2));
    if (iVar5 == 0) {
      uVar10 = uVar10 + (*((uint16_t *)(stack_record_2c + 2))) & 0xffff;
      pcVar11 = (stack_record_2c + 1);
      if (param_3 != 'Z') {
LAB_0008d07c:
        *pcVar11 = 'Z';
        break;
      }
    }
    else {
      if (iVar5 != 3) {
        pcVar11 = stack_record_2c;
        if (iVar5 == 5) goto LAB_0008d07c;
        break;
      }
      if (param_3 != 'Z') {
        uVar2 = 0x5a;
        uVar3 = 0x31;
        goto LAB_0008d0bc;
      }
    }
    iVar5 = increment_record_index_and_latch_end_flags_8cfe8(cVar9,stack_record_2c,(stack_record_2c + 1),param_4);
    puVar4 = ((void *)camry_host_ptr((uint32_t)(((uint32_t)(param_4)))));
  } while (iVar5 == 0);
  uVar2 = 0;
  uVar3 = 0;
  if (stack_record_2c[1] == 'Z') {
LAB_0008d0bc:
    uVar7 = uVar3;
    uVar8 = uVar2;
    uVar6 = 0;
  }
  else if (stack_record_2c[0] == 'Z') {
    uVar6 = 10;
  }
  else {
    uVar6 = 1;
  }
  dcm_snapshot_record_message.response_length = uVar10;
  DAT_febf4570 = uVar8;
  DAT_febf4571 = uVar7;
  DAT_febf456f = stack_record_2c[1];
  return uVar6;
}

undefined4 merge_snapshot_record_payload_or_error_8d0e6(char *param_1,int param_2,int *param_3)

{
  uint uVar1;
  uint uVar2;
  
  uVar1 = (uint)(*((ushort *)camry_host_ptr((uint32_t)(param_2 + 2))));
  if ((*param_1 != 'Z') || ((*((ushort *)camry_host_ptr((uint32_t)(param_3[1] ))))< 5)) {
    if ((param_1[3] != 'Z') || (uVar1 < 8)) {
      if (*param_1 == 'Z') {
        return 0;
      }
      if (param_1[3] != 'Z') {
        (*((char *)camry_host_ptr((uint32_t)(param_3[3] ))))= param_1[2];
        return 1;
      }
    }
    if ((*((int *)camry_host_ptr((uint32_t)(param_2 + 4)))) != 0) {
      uVar2 = 0;
      if (3 < uVar1) {
        uVar2 = uVar1 - 3 & 0xffff;
      }
      for (uVar1 = 0; uVar1 < uVar2; uVar1 = uVar1 + 1 & 0xffff) {
        (*((undefined1 *)camry_host_ptr((uint32_t)(*param_3 + uVar1)))) = (*((undefined1 *)camry_host_ptr((uint32_t)((*((volatile int32_t *)camry_host_ptr((uint32_t)(param_2 + 4)))) + uVar1 + 3))));
      }
      (*((short *)camry_host_ptr((uint32_t)(param_3[1] ))))= (short)uVar2;
    }
  }
  return 0;
}

int advance_snapshot_record_local_and_side_sources_8d15e(undefined4 param_1,undefined1 param_2,undefined1 param_3)

{
  uint8_t stack_record_5b[92];
  undefined2 uVar1;
  undefined2 uVar2;
  int iVar3;
  char cVar4;
  uint uVar5;
  uint uVar6;
  int puStack_54[4];
  
  cVar4 = DAT_febf456e;
  uVar2 = DAT_febf456a;
  uVar1 = DAT_febf4568;
  stack_record_5b[2] = DAT_febf4572;
  stack_record_5b[1] = DAT_febf4575;
  stack_record_5b[33] = DAT_febf4576;
  uVar5 = (uint)DAT_febf456d;
  uVar6 = (uint)DAT_febf456c;
  stack_record_5b[34] = DAT_febf4577;
  stack_record_5b[35] = DAT_febf4578;
  stack_record_5b[36] = DAT_febf4579;
  stack_record_5b[37] = DAT_febf457a;
  (*((uint32_t *)(stack_record_5b + 27))) = 0;
  (*((uint16_t *)(stack_record_5b + 25))) = 0;
  stack_record_5b[38] = DAT_febf457b;
  ((uint8_t *)((stack_record_5b + 23)))[0] = 1;
  if (DAT_febf456e == '\0') {
    cVar4 = '\x02';
    iVar3 = build_three_byte_identifier_and_status_response_8cf8e(param_1, ((int *)camry_host_ptr((uint32_t)((0xfebf457cu)))));
    if (iVar3 == 0) {
      stack_record_5b[1] = param_2;
      uVar6 = append_snapshot_records_until_end_or_yield_8d020(param_1,param_2,param_3,((uint8_t *)((stack_record_5b + 1))));
      stack_record_5b[33] = DAT_febf456f;
      stack_record_5b[34] = DAT_febf4570;
      stack_record_5b[35] = DAT_febf4571;
    }
    else {
      stack_record_5b[34] = 0x5a;
      uVar6 = 1;
      stack_record_5b[33] = 0;
      stack_record_5b[35] = 0x31;
    }
    stack_record_5b[42] = 4;
    stack_record_5b[43] = *((uint8_t *)camry_host_ptr((uint32_t)(dcm_snapshot_record_message.request)));
    stack_record_5b[44] = (*((volatile uint8_t *)camry_host_ptr((uint32_t)((uint32_t)(dcm_snapshot_record_message.request) + (uint32_t)(1) * 1u))));
    stack_record_5b[45] = (*((volatile uint8_t *)camry_host_ptr((uint32_t)((uint32_t)(dcm_snapshot_record_message.request) + (uint32_t)(2) * 1u))));
    stack_record_5b[46] = (*((volatile uint8_t *)camry_host_ptr((uint32_t)((uint32_t)(dcm_snapshot_record_message.request) + (uint32_t)(3) * 1u))));
    uVar5 = ((void)(0x38000400), (void)(10), (void)(5), (void)(((uint8_t *)((stack_record_5b + 42)))), (void)(((uint8_t *)((stack_record_5b + 2)))), return_const_0_8b10c());
LAB_0008d2b4:
    if ((uVar6 == 10) || (uVar5 == 10)) {
      iVar3 = 10;
      dcm_post_service_event(0xef);
      goto LAB_0008d324;
    }
  }
  else {
    if (DAT_febf456e == '\x02') {
      if (uVar6 == 10) {
        uVar6 = append_snapshot_records_until_end_or_yield_8d020(param_1,param_2,param_3,((uint8_t *)((stack_record_5b + 1))));
        stack_record_5b[33] = DAT_febf456f;
        stack_record_5b[34] = DAT_febf4570;
        stack_record_5b[35] = DAT_febf4571;
      }
      if ((uVar5 == 10) && (uVar5 = ((void)(1), (void)(10), (void)(stack_record_5b[2]), return_const_0_8b110()), uVar5 != 10)) {
        (*((uint32_t *)(stack_record_5b + 27))) = 0;
        (*((uint16_t *)(stack_record_5b + 25))) = 0;
        stack_record_5b[36] = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0u))));
        stack_record_5b[37] = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(1u))));
        stack_record_5b[38] = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(2u))));
      }
      goto LAB_0008d2b4;
    }
    stack_record_5b[36] = (code)0x0;
    stack_record_5b[33] = 0;
    stack_record_5b[38] = 0x31;
    stack_record_5b[37] = 0x5a;
    stack_record_5b[35] = 0x31;
    uVar6 = 1;
    stack_record_5b[34] = 0x5a;
    uVar5 = 1;
  }
  puStack_54[0] = dcm_snapshot_record_message.response;
  puStack_54[3] = camry_host_addr(((uint8_t *)(stack_record_5b)));
  (*((uint16_t *)(stack_record_5b + 3))) = (ushort)dcm_snapshot_record_message.response_length;
  puStack_54[1] = camry_host_addr(((uint16_t *)((stack_record_5b + 3))));
  (*((uint16_t *)(stack_record_5b + 5))) = (ushort)dcm_snapshot_record_message.response_capacity;
  puStack_54[2] = camry_host_addr(((uint16_t *)((stack_record_5b + 5))));
  iVar3 = merge_snapshot_record_payload_or_error_8d0e6(((uint8_t *)((stack_record_5b + 33))), camry_host_addr(((uint8_t *)((stack_record_5b + 23)))), puStack_54);
  dcm_snapshot_record_message.response_length = (uint)(*((uint16_t *)(stack_record_5b + 3)));
  dcm_snapshot_record_message.response_capacity = (uint)(*((uint16_t *)(stack_record_5b + 5)));
  if (iVar3 == 0) {
    dcm_report_positive_response(((F33DcmMessageContext *)camry_host_ptr((uint32_t)((0xfebf457cu)))));
  }
  else {
    dcm_report_negative_or_pending(((F33DcmMessageContext *)camry_host_ptr((uint32_t)((0xfebf457cu)))), stack_record_5b[0]);
  }
LAB_0008d324:
  DAT_febf456c = (char)uVar6;
  DAT_febf456d = (char)uVar5;
  DAT_febf4568 = uVar1;
  DAT_febf4572 = stack_record_5b[2];
  DAT_febf456a = uVar2;
  DAT_febf456e = cVar4;
  DAT_febf4575 = stack_record_5b[1];
  DAT_febf4576 = stack_record_5b[33];
  DAT_febf4577 = stack_record_5b[34];
  DAT_febf4578 = stack_record_5b[35];
  DAT_febf4579 = stack_record_5b[36];
  DAT_febf457a = stack_record_5b[37];
  DAT_febf457b = stack_record_5b[38];
  return iVar3;
}

uint start_snapshot_record_request_8d366(void)

{
  uint uVar1;
  int iVar2;
  uint uVar3;
  uint uVar4;
  uint uVar5;
  uint uVar6;
  
  uVar3 = 0;
  set_diagnostic_busy_marker_from_done_flag_9560e(0);
  uVar6 = 0;
  uVar5 = 0;
  uVar4 = 0;
  set_diagnostic_callback_pending_955b6(0);
  if (dcm_snapshot_record_message.request_length == 4) {
    if (3 < dcm_snapshot_record_message.response_capacity) {
      uVar6 = (uint)(*((volatile uint8_t *)camry_host_ptr((uint32_t)((uint32_t)(dcm_snapshot_record_message.request) + (uint32_t)(2) * 1u)))) |
              (uint)(*((volatile uint8_t *)camry_host_ptr((uint32_t)((uint32_t)(dcm_snapshot_record_message.request) + (uint32_t)(1) * 1u)))) << 8 |
              (uint)*((uint8_t *)camry_host_ptr((uint32_t)(dcm_snapshot_record_message.request))) << 0x10;
      uVar1 = (uint)(*((volatile uint8_t *)camry_host_ptr((uint32_t)((uint32_t)(dcm_snapshot_record_message.request) + (uint32_t)(3) * 1u))));
      if (uVar1 == 0xff) {
        uVar4 = 0x5a;
        uVar1 = uVar5;
      }
      set_diagnostic_callback_pending_955b6(1);
      iVar2 = advance_snapshot_record_local_and_side_sources_8d15e(uVar6,uVar1,uVar4);
      if (iVar2 == 10) {
        uVar3 = 10;
        uVar5 = uVar1;
      }
      else {
        uVar3 = 0;
        fill_constant_block_8cef0();
        set_diagnostic_callback_pending_955b6(0);
        uVar4 = uVar3;
        uVar5 = uVar3;
        uVar6 = uVar3;
      }
    }
  }
  else {
    dcm_report_negative_or_pending(((F33DcmMessageContext *)camry_host_ptr((uint32_t)((0xfebf457cu)))), '\x13');
  }
  DAT_febf4564 = uVar6;
  DAT_febf4573 = (char)uVar5;
  DAT_febf4574 = (char)uVar4;
  return uVar3;
}

void cancel_snapshot_record_service_and_reset_8d3fa(void)

{
  dcm_cancel_service_events(0xef,'\0');
  set_diagnostic_busy_marker_from_done_flag_9560e(1);
  fill_constant_block_8cef0();
  return;
}

uint dcm_read_snapshot_by_dtc_service(uchar operation,F33DcmMessageContext *message)

{
  uint uVar1;
  
  dcm_snapshot_record_message.request = message->request;
  dcm_snapshot_record_message.request_length = message->request_length;
  dcm_snapshot_record_message.response = message->response;
  dcm_snapshot_record_message.response_length = message->response_length;
  dcm_snapshot_record_message.addressing_kind = message->addressing_kind;
  dcm_snapshot_record_message.suppress_positive = message->suppress_positive;
  dcm_snapshot_record_message.response_capacity = message->response_capacity;
  dcm_snapshot_record_message.service_id = message->service_id;
  dcm_snapshot_record_message.service_list_selector = message->service_list_selector;
  if (operation == '\0') {
    uVar1 = start_snapshot_record_request_8d366();
  }
  else {
    uVar1 = 0;
    cancel_snapshot_record_service_and_reset_8d3fa();
  }
  return uVar1;
}

uint32_t dcm_resume_queued_snapshot_record(void)

{
  uint32_t camry_r10_result;
  int iVar1;
  undefined4 uVar2;
  undefined1 uVar3;
  undefined1 uVar4;
  
  uVar3 = DAT_febf4574;
  uVar4 = DAT_febf4573;
  uVar2 = DAT_febf4564;
  iVar1 = (camry_r10_result = advance_snapshot_record_local_and_side_sources_8d15e(DAT_febf4564,DAT_febf4573,DAT_febf4574));
  if (iVar1 != 10) {
    fill_constant_block_8cef0();
    uVar2 = 0;
    uVar4 = 0;
    uVar3 = 0;
  }
  DAT_febf4564 = uVar2;
  DAT_febf4573 = uVar4;
  DAT_febf4574 = uVar3;
  return camry_r10_result;
}

void reset_memory_read_status4598_8d4ae(void)

{
  DAT_febf459a = 0;
  DAT_febf4599 = 1;
  DAT_febf4598 = 1;
  DAT_febf459b = 0xff;
  return;
}

void thunk_reset_memory_read_status4598_8d4ae(void)

{
  reset_memory_read_status4598_8d4ae();
  return;
}

undefined4 map_memory_read_status_to_nrc31_8d4e0(char param_1)

{
  if ((param_1 != '\x01') && (param_1 != '\x03' && param_1 != '\x04')) {
    return 0;
  }
  return 0x31;
}

undefined4 copy_memory_read_payload_or_write_nrc_8d4f6(char param_1,char *param_2,int *param_3)

{
  uint uVar1;
  undefined4 uVar2;
  undefined1 uVar3;
  undefined1 *puVar4;
  
  if (*param_2 == '\0') {
    uVar2 = 0;
    if ((param_1 == '\0') && (uVar1 = 0, *(int *)(param_2 + 4) != 0)) {
      for (; uVar1 < *(ushort *)(param_2 + 2); uVar1 = uVar1 + 1 & 0xffff) {
        (*((undefined1 *)camry_host_ptr((uint32_t)(*param_3 + uVar1)))) = (*((undefined1 *)camry_host_ptr((uint32_t)(*(int *)(param_2 + 4) + uVar1))));
      }
    }
  }
  else {
    puVar4 = ((undefined1 *)camry_host_ptr((uint32_t)(param_3[3])));
    uVar3 = map_memory_read_status_to_nrc31_8d4e0((*((volatile uint8_t *)((uint8_t *)(param_2) + (0)))));
    *puVar4 = uVar3;
    uVar2 = 2;
  }
  return uVar2;
}

undefined4
dispatch_memory_read_by_selector_nibble_8d546(undefined4 param_1,byte param_2,undefined4 param_3,uint param_4,uchar *param_5,
            undefined1 *param_6)

{
  uint8_t stack_record_3d[64];
  ushort length;
  undefined1 uVar1;
  undefined4 uVar2;
  int iVar3;
  uint uVar4;
  uint uVar5;
  uint32_t apuStack_3c[4];
  
  uVar5 = (uint)DAT_febf4598;
  uVar4 = (uint)DAT_febf4599;
  stack_record_3d[0] = DAT_febf459b;
  stack_record_3d[31] = (undefined1)param_3;
  stack_record_3d[27] = param_2 & 0xf;
  iVar3 = (int)(uint)param_2 >> 4;
  stack_record_3d[28] = (undefined1)((uint)param_3 >> 0x18);
  stack_record_3d[29] = (undefined1)((uint)param_3 >> 0x10);
  stack_record_3d[30] = (undefined1)((uint)param_3 >> 8);
  stack_record_3d[32] = (undefined1)param_4;
  length = (ushort)param_4;
  if (DAT_febf459a == '\0') {
    if (iVar3 == 0) {
      uVar5 = read_configured_application_memory(((uint8_t *)((stack_record_3d + 27))),param_5,length);
LAB_0008d59e:
      uVar4 = 1;
LAB_0008d61a:
      if (uVar5 != 2) {
LAB_0008d61e:
        ((uint8_t *)((stack_record_3d + 17)))[0] = (undefined1)uVar5;
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
      uVar4 = ((void)(0x48000000), (void)(2), (void)(6), (void)(((uint8_t *)((stack_record_3d + 27)))), (void)(((uint8_t *)(stack_record_3d))), return_const_0_8b10c());
      goto LAB_0008d61e;
    }
    *param_6 = 0x31;
    uVar1 = 1;
LAB_0008d5d4:
    ((uint8_t *)((stack_record_3d + 17)))[0] = uVar1;
    uVar2 = 0;
  }
  else {
    if (DAT_febf459a == '\x02') {
      if (iVar3 == 0) {
        if (uVar5 == 2) {
          uVar5 = read_configured_application_memory(((uint8_t *)((stack_record_3d + 27))),param_5,length);
        }
      }
      else {
        uVar5 = 1;
      }
      if (iVar3 != 1) goto LAB_0008d59e;
      if (uVar4 == 2) {
        uVar4 = ((void)(1), (void)(2), (void)(stack_record_3d[0]), return_const_0_8b110());
      }
      goto LAB_0008d61a;
    }
    ((uint8_t *)((stack_record_3d + 17)))[0] = 1;
    uVar4 = 1;
LAB_0008d622:
    uVar1 = (char)uVar4;
    if (iVar3 == 1) goto LAB_0008d5d4;
    uVar2 = 0x5a;
  }
  (*((uint32_t *)(stack_record_3d + 21))) = 0;
  apuStack_3c[0] = camry_host_addr(param_5);
  apuStack_3c[3] = camry_host_addr(param_6);
  (*((uint16_t *)(stack_record_3d + 19))) = length;
  uVar2 = copy_memory_read_payload_or_write_nrc_8d4f6(uVar2,((uint8_t *)((stack_record_3d + 17))),apuStack_3c);
  DAT_febf4598 = 1;
  DAT_febf4599 = 1;
  DAT_febf459a = 0;
  stack_record_3d[0] = 0xff;
LAB_0008d656:
  DAT_febf459b = stack_record_3d[0];
  DAT_febf459c = (char)iVar3;
  return uVar2;
}

void app_security_reset_challenge_material(void)

{
  uint uVar1;
  
  uVar1 = 0;
  do {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebf495au + (uint32_t)(uVar1) * 1u)))) = '\0';
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebf496au + (uint32_t)(uVar1) * 1u)))) = '\0';
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebf497au + (uint32_t)(uVar1) * 1u)))) = '\0';
    uVar1 = uVar1 + 1;
  } while (uVar1 < 0x10);
  app_security_challenge_active = '\0';
  app_security_comparison_result = '\0';
  return;
}

void reset_security_challenge_material_wrapper_8d6a4(void)

{
  app_security_reset_challenge_material();
  return;
}

void fill_counter_sample_pairs(uchar *output,uchar length)

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

undefined4 compare_block_against_selected_exclusion_list_8d6d6(int param_1)

{
  F33BootChallengeExclusionRecord *pFVar1;
  uint uVar2;
  int iVar3;
  uint uVar4;
  int iVar5;
  
  pFVar1 = ((void *)camry_host_ptr((uint32_t)((0x25620u))));
  iVar3 = 0x5a;
  uVar4 = 0;
  iVar5 = iVar3;
  if (app_security_challenge_active != '\0') {
    pFVar1 = ((void *)camry_host_ptr((uint32_t)((0x25630u))));
  }
  do {
    if (pFVar1->count <= uVar4) break;
    uVar2 = 0;
    iVar5 = iVar3;
    do {
      if ((*((uchar *)camry_host_ptr((uint32_t)(uVar2 + param_1)))) != (*((volatile uint8_t *)camry_host_ptr((uint32_t)((pFVar1->excluded_blocks[uVar4]) + (uint32_t)(uVar2)))))) {
        iVar5 = 0;
      }
      uVar2 = uVar2 + 1 & 0xff;
    } while ((iVar5 == 0x5a) && (uVar2 < 0x10));
    if (iVar5 != 0) {
      iVar3 = 0;
    }
    uVar4 = uVar4 + 1 & 0xff;
  } while (iVar3 == 0x5a);
  if (iVar5 != 0) {
    return 0;
  }
  return 0x5a;
}

uint app_security_generate_challenge(uchar *seed_out)

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
    fill_counter_sample_pairs(local_30,'\x10');
    initialize_aes128_counter_context_with_fixed_iv_85940(camry_host_addr(local_30), 0x10, (0xfebf4a50u));
    iVar5 = xor_fixed_input_with_aes128_counter_block_85964(camry_host_addr(seed_out), (0xfebf4a50u));
    if (iVar5 == 0) {
      iVar6 = rekey_initialized_aes128_counter_context_8597c(camry_host_addr(seed_out), 0x10, (0xfebf4a50u));
    }
    else {
      iVar8 = 0xff;
    }
    if ((iVar6 == 0) && (iVar8 == 0)) {
      iVar8 = xor_fixed_input_with_aes128_counter_block_85964(camry_host_addr(seed_out), (0xfebf4a50u));
    }
    else {
      iVar8 = 0xff;
    }
    clear_aes128_counter_context_228_bytes_859a8(((undefined4 *)camry_host_ptr((uint32_t)((0xfebf4a50u)))));
  } while (((iVar8 != 0) || (uVar9 = compare_block_against_selected_exclusion_list_8d6d6(camry_host_addr(seed_out)), uVar9 == 0)) &&
          (iVar7 = iVar7 + -1, iVar7 != 0));
  if (uVar9 != 0x5a) {
    uVar9 = 0;
    do {
      puVar1 = local_30 + uVar9;
      puVar2 = seed_out + uVar9;
      uVar9 = uVar9 + 1;
      *puVar2 = *puVar1;
    } while (uVar9 < 0x10);
    uVar9 = compare_block_against_selected_exclusion_list_8d6d6(camry_host_addr(seed_out));
    if (uVar9 != 0x5a) {
      return uVar9;
    }
  }
  uVar4 = 0;
  do {
    uVar3 = uVar4 + 1;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebf495au + (uint32_t)(uVar4) * 1u)))) = seed_out[uVar4];
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebf496au + (uint32_t)(uVar4) * 1u)))) = seed_out[uVar4];
    uVar4 = uVar3;
  } while (uVar3 < 0x10);
  app_security_challenge_active = 'Z';
  return uVar9;
}

uint app_security_prepare_seed(uchar *client_material,uchar *seed_out,uchar *negative_response)

{
  uchar *puVar1;
  uchar *puVar2;
  uint uVar3;
  uchar uVar4;
  int iVar5;
  uint uVar6;
  
  uVar4 = app_security_challenge_active;
  uVar6 = 0;
  do {
    uVar3 = uVar6 + 1;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebf497au + (uint32_t)(uVar6) * 1u)))) = client_material[uVar6];
    uVar6 = uVar3;
  } while (uVar3 < 0x10);
  if (uVar4 == '\0') {
LAB_0008d872:
    uVar6 = app_security_generate_challenge(seed_out);
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
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebf495au + (uint32_t)(uVar6) * 1u)))) != '\0') {
    iVar5 = 0;
  }
  if (iVar5 == 0x5a) goto code_r0x0008d868;
  uVar6 = 0;
  do {
    puVar1 = ((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebf495au + (uint32_t)(uVar6) * 1u)));
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

uint app_security_decrypt_client_material(uchar *client_material,uchar *intermediate_key)

{
  uint uVar1;
  
  expand_aes128_key_and_mark_context_initialized_876c4(app_security_client_decryption_key, 0x10, ((uint *)camry_host_ptr((uint32_t)((0xfebf498cu)))));
  uVar1 = aes128_decrypt_16byte_block_with_initialized_context_864de(client_material, intermediate_key, 0x10, ((uint *)camry_host_ptr((uint32_t)((0xfebf498cu)))));
  clear_aes128_block_context_196_bytes_87ac2(((undefined4 *)camry_host_ptr((uint32_t)((0xfebf498cu)))));
  return uVar1;
}

uint app_security_encrypt_challenge
               (uchar *intermediate_key,uchar *challenge,uchar *expected_key)

{
  uint uVar1;
  
  expand_aes128_key_and_mark_context_initialized_876c4(intermediate_key, 0x10, ((uint *)camry_host_ptr((uint32_t)((0xfebf498cu)))));
  uVar1 = aes128_encrypt_16byte_block_with_initialized_context_863a0(challenge,expected_key,0x10,(0xfebf498cu));
  clear_aes128_block_context_196_bytes_87ac2(((undefined4 *)camry_host_ptr((uint32_t)((0xfebf498cu)))));
  return uVar1;
}

uint app_security_compare_key(uchar *submitted_key)

{
  uint8_t stack_record_34[52];
  uint uVar1;
  uint uVar2;
  
  uVar2 = 0xb;
  if ((app_security_challenge_active == 'Z') &&
     (uVar1 = app_security_decrypt_client_material(app_security_client_material,((uint8_t *)((stack_record_34 + 16)))),
     uVar1 == 0)) {
    uVar2 = app_security_encrypt_challenge(((uint8_t *)((stack_record_34 + 16))),app_security_challenge,((uint8_t *)(stack_record_34)));
    if (uVar2 == 0) {
      uVar1 = 0;
      uVar2 = 0;
      do {
        if (submitted_key[uVar1] != ((uint8_t *)(stack_record_34))[uVar1]) {
          uVar2 = 0xb;
        }
        uVar1 = uVar1 + 1 & 0xff;
        if (uVar2 != 0) goto LAB_0008d998;
      } while (uVar1 < 0x10);
      uVar1 = 0;
      do {
        (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebf495au + (uint32_t)(uVar1) * 1u)))) = '\0';
        (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebf496au + (uint32_t)(uVar1) * 1u)))) = '\0';
        uVar1 = uVar1 + 1;
      } while (uVar1 < 0x10);
      app_security_challenge_active = '\0';
    }
    else {
      uVar2 = 0xb;
    }
  }
LAB_0008d998:
  app_security_comparison_result = (uchar)uVar2;
  return uVar2;
}

uchar get_security_comparison_result_8d9a2(void)

{
  return app_security_comparison_result;
}

void clear_security_comparison_result_8d9ac(void)

{
  app_security_comparison_result = '\0';
  return;
}

uchar get_current_security_level_byte_8d9b6(void)

{
  uchar uStack_5;
  
  dcm_get_security_level(&uStack_5);
  return uStack_5;
}

void reset_communication_local_state_8d9ca(void)

{
  dcm_communication_local_state.last_tx_disable_bit = '\0';
  dcm_communication_local_state.last_mapped_mode = '\0';
  dcm_communication_local_state.retained_subnet = '\0';
  dcm_communication_local_state.action_state = '\0';
  dcm_communication_local_state.lower_status = '\0';
  dcm_communication_local_state.application_status = '\0';
  dcm_communication_local_state.admission_result = '\x01';
  dcm_communication_local_state.side_status = 0xff;
  return;
}

uint admit_application_communication_request
               (uchar subfunction,uchar communication_type,ushort node,uchar *nrc)

{
  uint uVar1;
  byte bVar2;
  
  bVar2 = dcm_communication_local_state.retained_subnet;
  if (dcm_communication_local_state.action_state == '\0') {
    bVar2 = communication_type >> 4;
    uVar1 = communication_request_sample_above_limit();
    dcm_communication_local_state.action_state = uVar1 != 1;
    if ((bool)dcm_communication_local_state.action_state) {
      uVar1 = 0;
      goto LAB_0008da52;
    }
  }
  uVar1 = 1;
  *nrc = '\"';
LAB_0008da52:
  dcm_communication_local_state.admission_result = (uchar)uVar1;
  dcm_communication_local_state.retained_subnet = bVar2;
  return uVar1;
}

uint apply_and_complete_communication_policy_request(uchar channel,uchar mapped_mode)

{
  uint8_t stack_record_23[35];
  uchar lower_status;
  uint uVar1;
  uchar network_selector;
  byte disable_tx;
  uchar uVar2;
  uchar application_status;
  
  network_selector = dcm_communication_local_state.retained_subnet;
  uVar2 = dcm_communication_local_state.action_state;
  application_status = dcm_communication_local_state.application_status;
  disable_tx = mapped_mode & 1;
  stack_record_23[0] = dcm_communication_local_state.side_status;
  if (dcm_communication_local_state.action_state == '\x01') {
    uVar2 = '\x02';
    stack_record_23[1] = dcm_communication_local_state.retained_subnet;
    stack_record_23[2] = disable_tx;
    lower_status = ((void)(0x60000001), (void)(10), (void)(2), (void)(((uint8_t *)((stack_record_23 + 1)))), (void)(((uint8_t *)(stack_record_23))), return_const_0_8b10c());
  }
  else {
    if (dcm_communication_local_state.action_state != '\x02') {
      application_status = '\0';
      lower_status = '\0';
      goto LAB_0008daea;
    }
    lower_status = dcm_communication_local_state.lower_status;
    if (dcm_communication_local_state.lower_status == '\n') {
      lower_status = ((void)(0), (void)(10), return_const_0_8b110());
    }
    if (application_status != '\n') goto LAB_0008daea;
  }
  publish_diagnostic_normal_tx_policy_request(network_selector,disable_tx);
  application_status = '\0';
LAB_0008daea:
  uVar1 = merge_two_diagnostic_statuses(application_status,lower_status,'\0','\n');
  if (uVar1 != 10) {
    uVar1 = 0;
    application_status = '\0';
    lower_status = '\0';
    uVar2 = '\0';
    network_selector = '\0';
    stack_record_23[0] = 0xff;
  }
  dcm_communication_local_state.application_status = application_status;
  dcm_communication_local_state.lower_status = lower_status;
  dcm_communication_local_state.action_state = uVar2;
  dcm_communication_local_state.retained_subnet = network_selector;
  dcm_communication_local_state.side_status = stack_record_23[0];
  dcm_communication_local_state.last_mapped_mode = mapped_mode;
  dcm_communication_local_state.last_tx_disable_bit = disable_tx;
  return uVar1;
}

void fill_constant_block_8db22(void)

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

void cancel_dtc_setting_service_and_reset_8db70(void)

{
  dcm_cancel_service_events(0xf0,'\0');
  set_diagnostic_busy_marker_from_done_flag_9560e(1);
  fill_constant_block_8db22();
  return;
}

undefined1 advance_dtc_setting_admission_8db8c(F33DcmMessageContext *param_1)

{
  uint8_t stack_record_1e[30];
  uchar lower_status;
  uchar application_status;
  uint uVar1;
  undefined1 uVar2;
  bool bVar3;
  
  application_status = DAT_febf45ad;
  stack_record_1e[1] = DAT_febf45a9;
  if (DAT_febf45ac == '\0') {
    DAT_febf45aa = 0;
    DAT_febf45ab = 0;
    stack_record_1e[0] = DAT_febf45a8;
    lower_status = ((void)((int)0xc0000000), (void)(2), (void)(1), (void)(((uint8_t *)(stack_record_1e))), (void)(((uint8_t *)((stack_record_1e + 1)))), return_const_0_8b10c());
  }
  else {
    if (DAT_febf45ac != '\x01') {
      return 0;
    }
    lower_status = DAT_febf45ae;
    if (DAT_febf45ae == '\x02') {
      lower_status = ((void)(0), (void)(2), return_const_0_8b110());
    }
    if (application_status != '\x02') goto LAB_0008dc0c;
  }
  application_status = ((void)(0xffffff), (void)(1), return_const_0_50900());
LAB_0008dc0c:
  bVar3 = true;
  uVar1 = merge_two_diagnostic_statuses(application_status,lower_status,'\0','\x02');
  if (uVar1 == 2) {
    dcm_post_service_event(0xf0);
    uVar2 = 10;
  }
  else {
    application_status = '\x01';
    lower_status = '\x01';
    uVar2 = uVar1 != 0;
    if ((bool)uVar2) {
      dcm_report_negative_or_pending(param_1,'\"');
    }
    bVar3 = !(bool)uVar2;
    DAT_febf45aa = 0x5a;
  }
  DAT_febf45ad = application_status;
  DAT_febf45ae = lower_status;
  DAT_febf45ac = bVar3;
  DAT_febf45a9 = stack_record_1e[1];
  return uVar2;
}

undefined4 publish_selected_dtc_setting_8dc60(void)

{
  uchar selection;
  
  if (DAT_febf45a8 == '\x01') {
    selection = '\x01';
  }
  else {
    selection = '\x02';
  }
  publish_dtc_setting_request(selection);
  return 0;
}

undefined1 advance_dtc_setting_execution_8dc7c(F33DcmMessageContext *param_1)

{
  uint8_t stack_record_1e[30];
  uchar lower_status;
  uchar application_status;
  uint uVar1;
  undefined1 uVar2;
  char cVar3;
  
  application_status = DAT_febf45af;
  cVar3 = DAT_febf45ac;
  stack_record_1e[1] = DAT_febf45a9;
  if (DAT_febf45ac == '\x01') {
    stack_record_1e[0] = DAT_febf45a8;
    cVar3 = '\x02';
    lower_status = ((void)((int)0xc0000001), (void)(2), (void)(1), (void)(stack_record_1e), (void)((stack_record_1e + 1)), return_const_0_8b10c());
  }
  else {
    if (DAT_febf45ac != '\x02') {
      application_status = '\x01';
      lower_status = '\x01';
      goto LAB_0008dd00;
    }
    lower_status = DAT_febf45b0;
    if (DAT_febf45b0 == '\x02') {
      lower_status = ((void)(0), (void)(2), return_const_0_8b110());
    }
    if (application_status != '\x02') goto LAB_0008dd00;
  }
  application_status = ((void)(stack_record_1e[1]), publish_selected_dtc_setting_8dc60());
LAB_0008dd00:
  uVar1 = merge_two_diagnostic_statuses(application_status,lower_status,'\0','\x02');
  if (uVar1 == 2) {
    dcm_post_service_event(0xf0);
    uVar2 = 10;
  }
  else {
    application_status = '\x01';
    lower_status = '\x01';
    cVar3 = '\0';
    uVar2 = uVar1 != 0;
    if ((bool)uVar2) {
      dcm_report_negative_or_pending(param_1,'\"');
    }
    else {
      dcm_report_positive_response(param_1);
    }
    DAT_febf45ab = 0x5a;
  }
  DAT_febf45af = application_status;
  DAT_febf45b0 = lower_status;
  DAT_febf45ac = cVar3;
  DAT_febf45a9 = stack_record_1e[1];
  return uVar2;
}

uint32_t run_dtc_setting_admission_then_execution_8dd54(undefined4 param_1)

{
  uint32_t camry_r10_result;
  int iVar1;
  
  iVar1 = (camry_r10_result = advance_dtc_setting_admission_8db8c(((F33DcmMessageContext *)camry_host_ptr((uint32_t)(param_1)))));
  if (iVar1 == 0) {
    (camry_r10_result = advance_dtc_setting_execution_8dc7c(((F33DcmMessageContext *)camry_host_ptr((uint32_t)(param_1)))));
  }
  return camry_r10_result;
}

undefined4 dispatch_dtc_setting_with_empty_payload_8dd6c(undefined1 param_1,undefined4 *param_2)

{
  undefined4 uVar1;
  uint32_t puVar2;
  undefined4 *puVar3;
  F33DcmMessageContext *pFVar4;
  F33DcmMessageContext *pFVar5;
  F33DcmMessageContext local_24;
  
  pFVar4 = &local_24;
  pFVar5 = &local_24;
  puVar3 = param_2 + 7;
  do {
    uVar1 = *param_2;
    param_2 = param_2 + 1;
    pFVar4->request = uVar1;
    pFVar4 = ((F33DcmMessageContext *)camry_host_ptr((uint32_t)((int)camry_host_addr(pFVar4) + 4)));
  } while (camry_host_addr(puVar3)!=camry_host_addr(param_2));
  pFVar4 = ((void *)camry_host_ptr((uint32_t)((0xfebf45b4u))));
  do {
    puVar2 = (uint32_t)((uint32_t)(pFVar5->request));
    pFVar5 = ((F33DcmMessageContext *)camry_host_ptr((uint32_t)((int)camry_host_addr(pFVar5) + 4)));
    pFVar4->request = puVar2;
    pFVar4 = (F33DcmMessageContext *)&pFVar4->request_length;
  } while (camry_host_addr((F33DcmMessageContext *)((uint8_t *)&local_24 + 28))!=camry_host_addr(pFVar5));
  if (local_24.request_length == 0) {
    DAT_febf45a8 = param_1;
    uVar1 = run_dtc_setting_admission_then_execution_8dd54(camry_host_addr(&local_24));
  }
  else {
    uVar1 = 1;
    dcm_report_negative_or_pending(&local_24,'\x13');
  }
  return uVar1;
}

uint dcm_enable_dtc_setting_service(uchar operation,F33DcmMessageContext *message)

{
  uint uVar1;
  
  if (operation == '\0') {
    uVar1 = dispatch_dtc_setting_with_empty_payload_8dd6c(1, message);
  }
  else {
    uVar1 = 0;
    cancel_dtc_setting_service_and_reset_8db70();
  }
  return uVar1;
}

uint dcm_disable_dtc_setting_service(uchar operation,F33DcmMessageContext *message)

{
  uint uVar1;
  
  if (operation == '\0') {
    uVar1 = dispatch_dtc_setting_with_empty_payload_8dd6c(2, message);
  }
  else {
    uVar1 = 0;
    cancel_dtc_setting_service_and_reset_8db70();
  }
  return uVar1;
}

uint32_t dcm_resume_queued_dtc_setting(void)

{
  uint32_t camry_r10_result;
  (camry_r10_result = run_dtc_setting_admission_then_execution_8dd54((0xfebf45b4u)));
  return camry_r10_result;
}

void fill_constant_block_8de1a(void)

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

uint begin_proprietary_event_selection
               (uchar operation,uchar selector,ushort event_id,ushort subselector)

{
  DAT_febf45d0 = event_id;
  DAT_febf45d2 = subselector;
  DAT_febf45dc = selector;
  set_pending_kind_and_two_halfword_arguments_50916((uint)(byte)selector, (uint)(ushort)event_id, (uint)(ushort)subselector);
  return 0;
}

undefined4 map_event_serialization_status_to_nrc_8debe(char param_1)

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

undefined4 merge_sorted_big_endian_u16_lists_dedup_equal_heads_8dee2(char *param_1,char *param_2,int *param_3)

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
        (*((short *)camry_host_ptr((uint32_t)(param_3[1] ))))= (short)uVar3;
        return 0;
      }
    }
  } while( true );
}

undefined4 select_first_successful_payload_or_error_8dff6(byte *param_1,byte *param_2,int *param_3)

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
        (*((byte *)camry_host_ptr((uint32_t)(param_3[3] ))))= param_1[1];
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
  (*((ushort *)camry_host_ptr((uint32_t)(param_3[1] ))))= uVar5;
  return uVar3;
}
