#include "common.h"

uint diag_routine_class01_98034(byte param_1,uchar *param_2)

{
  uint8_t stack_record_b[12];
  uint uVar1;
  
  stack_record_b[0] = '\0';
  (*((uint16_t *)(stack_record_b + 1))) = 0;
  if (param_1 < 2) {
    uVar1 = diag_routine_application_class('\x01',8,0,((uint8_t *)(stack_record_b)),((uint16_t *)((stack_record_b + 1))),param_2);
  }
  else {
    uVar1 = 0;
    reset_routine_class_state_wrapper_a_8b83c();
  }
  return uVar1;
}

undefined4
request_routine_class40_service31_or_reset_9806a(undefined4 param_1,char param_2,undefined4 param_3,undefined4 param_4,
            undefined4 param_5)

{
  undefined4 uVar1;
  
  if (param_2 == '\0') {
    uVar1 = run_direct_request_sequence_and_map_nrc_8bc4a(param_1, 0x40, param_3, 0x31, ((uchar *)camry_host_ptr((uint32_t)(param_5))));
  }
  else {
    uVar1 = 0;
    reset_routine_class_state_wrapper_a_8b83c();
  }
  return uVar1;
}

uint diag_routine_class01_98094(byte param_1,uchar *param_2,ushort *param_3,uchar *param_4)

{
  uint uVar1;
  
  if (param_1 < 2) {
    uVar1 = diag_routine_application_class('\x01',10,0,param_2,param_3,param_4);
  }
  else {
    uVar1 = 0;
    reset_routine_class_state_wrapper_a_8b83c();
  }
  return uVar1;
}

uint diag_routine_class01_980c0(byte param_1,uchar *param_2)

{
  uint8_t stack_record_b[12];
  uint uVar1;
  
  stack_record_b[0] = '\0';
  (*((uint16_t *)(stack_record_b + 1))) = 0;
  if (param_1 < 2) {
    uVar1 = diag_routine_application_class('\x01',0xb,0,((uint8_t *)(stack_record_b)),((uint16_t *)((stack_record_b + 1))),param_2);
  }
  else {
    uVar1 = 0;
    reset_routine_class_state_wrapper_a_8b83c();
  }
  return uVar1;
}

uint diag_routine_class01_980f6(byte param_1,uchar *param_2)

{
  uint8_t stack_record_b[12];
  uint uVar1;
  
  stack_record_b[0] = '\0';
  (*((uint16_t *)(stack_record_b + 1))) = 0;
  if (param_1 < 2) {
    uVar1 = diag_routine_application_class('\x01',0xc,0,((uint8_t *)(stack_record_b)),((uint16_t *)((stack_record_b + 1))),param_2);
  }
  else {
    uVar1 = 0;
    reset_routine_class_state_wrapper_a_8b83c();
  }
  return uVar1;
}

uint diag_routine_class01_9812c(byte param_1,uchar *param_2)

{
  uint8_t stack_record_b[12];
  uint uVar1;
  
  stack_record_b[0] = '\0';
  (*((uint16_t *)(stack_record_b + 1))) = 0;
  if (param_1 < 2) {
    uVar1 = diag_routine_application_class('\x01',0xd,0,((uint8_t *)(stack_record_b)),((uint16_t *)((stack_record_b + 1))),param_2);
  }
  else {
    uVar1 = 0;
    reset_routine_class_state_wrapper_a_8b83c();
  }
  return uVar1;
}

uint diag_routine_class01_98162(byte param_1,uchar *param_2)

{
  uint8_t stack_record_b[12];
  uint uVar1;
  
  stack_record_b[0] = '\0';
  (*((uint16_t *)(stack_record_b + 1))) = 0;
  if (param_1 < 2) {
    uVar1 = diag_routine_application_class('\x01',0xe,0,((uint8_t *)(stack_record_b)),((uint16_t *)((stack_record_b + 1))),param_2);
  }
  else {
    uVar1 = 0;
    reset_routine_class_state_wrapper_a_8b83c();
  }
  return uVar1;
}

uint diag_routine_class01_98198(byte param_1,uchar *param_2)

{
  uint8_t stack_record_b[12];
  uint uVar1;
  
  stack_record_b[0] = '\0';
  (*((uint16_t *)(stack_record_b + 1))) = 0;
  if (param_1 < 2) {
    uVar1 = diag_routine_application_class('\x01',0xf,0,((uint8_t *)(stack_record_b)),((uint16_t *)((stack_record_b + 1))),param_2);
  }
  else {
    uVar1 = 0;
    reset_routine_class_state_wrapper_a_8b83c();
  }
  return uVar1;
}

uint diag_routine_class01_981ce(byte param_1,uchar *param_2)

{
  uint8_t stack_record_b[12];
  uint uVar1;
  
  stack_record_b[0] = '\0';
  (*((uint16_t *)(stack_record_b + 1))) = 0;
  if (param_1 < 2) {
    uVar1 = diag_routine_application_class('\x01',0x10,0,((uint8_t *)(stack_record_b)),((uint16_t *)((stack_record_b + 1))),param_2);
  }
  else {
    uVar1 = 0;
    reset_routine_class_state_wrapper_a_8b83c();
  }
  return uVar1;
}

uint diag_routine_class01_98206(byte param_1,uchar *param_2)

{
  uint8_t stack_record_b[12];
  uint uVar1;
  
  stack_record_b[0] = '\0';
  (*((uint16_t *)(stack_record_b + 1))) = 0;
  if (param_1 < 2) {
    uVar1 = diag_routine_application_class('\x01',0x11,0,((uint8_t *)(stack_record_b)),((uint16_t *)((stack_record_b + 1))),param_2);
  }
  else {
    uVar1 = 0;
    reset_routine_class_state_wrapper_a_8b83c();
  }
  return uVar1;
}

uint diag_routine_class01_9823e(byte param_1,uchar *param_2)

{
  uint8_t stack_record_b[12];
  uint uVar1;
  
  stack_record_b[0] = '\0';
  (*((uint16_t *)(stack_record_b + 1))) = 0;
  if (param_1 < 2) {
    uVar1 = diag_routine_application_class('\x01',0x12,0,((uint8_t *)(stack_record_b)),((uint16_t *)((stack_record_b + 1))),param_2);
  }
  else {
    uVar1 = 0;
    reset_routine_class_state_wrapper_a_8b83c();
  }
  return uVar1;
}

uint diag_routine_class02_98276(byte param_1,uchar *param_2)

{
  uint8_t stack_record_b[12];
  uint uVar1;
  
  stack_record_b[0] = '\0';
  (*((uint16_t *)(stack_record_b + 1))) = 0;
  if (param_1 < 2) {
    uVar1 = diag_routine_application_class('\x02',0xf,0,((uint8_t *)(stack_record_b)),((uint16_t *)((stack_record_b + 1))),param_2);
  }
  else {
    uVar1 = 0;
    reset_routine_class_state_wrapper_a_8b83c();
  }
  return uVar1;
}

uint diag_routine_class02_982ac(byte param_1,uchar *param_2)

{
  uint8_t stack_record_b[12];
  uint uVar1;
  
  stack_record_b[0] = '\0';
  (*((uint16_t *)(stack_record_b + 1))) = 0;
  if (param_1 < 2) {
    uVar1 = diag_routine_application_class('\x02',0x12,0,((uint8_t *)(stack_record_b)),((uint16_t *)((stack_record_b + 1))),param_2);
  }
  else {
    uVar1 = 0;
    reset_routine_class_state_wrapper_a_8b83c();
  }
  return uVar1;
}

undefined4 dispatch_routine_result_callbacks_by_row_982e4(undefined2 param_1,uint *param_2,undefined1 param_3,undefined4 param_4)

{
  uint8_t stack_record_18[24];
  uint uVar1;
  undefined4 uVar2;
  
  stack_record_18[0] = 0;
  stack_record_18[1] = 0;
  uVar2 = 0;
  stack_record_18[2] = 0;
  stack_record_18[3] = 0;
  stack_record_18[4] = 0;
  stack_record_18[5] = 0;
  stack_record_18[6] = 0;
  stack_record_18[7] = 0;
  stack_record_18[8] = 0;
  stack_record_18[9] = 0;
  stack_record_18[10] = 0;
  stack_record_18[11] = 0;
  stack_record_18[12] = 0;
  stack_record_18[13] = 0;
  stack_record_18[14] = 0;
  stack_record_18[15] = 0;
  switch(param_1) {
  case 0:
    uVar2 = diag_routine_class03_97b2c(param_3, stack_record_18, ((uchar *)camry_host_ptr((uint32_t)(param_4))));
    uVar1 = (uint)stack_record_18[0];
    break;
  case 1:
    uVar2 = diag_routine_class03_97b60(param_3, (stack_record_18 + 1), ((uchar *)camry_host_ptr((uint32_t)(param_4))));
    uVar1 = (uint)stack_record_18[1];
    break;
  case 2:
    uVar2 = diag_routine_class03_97b94(param_3, (stack_record_18 + 2), ((uchar *)camry_host_ptr((uint32_t)(param_4))));
    uVar1 = (uint)stack_record_18[2];
    break;
  case 3:
    uVar2 = diag_routine_class03_97bc8(param_3, (stack_record_18 + 3), ((uchar *)camry_host_ptr((uint32_t)(param_4))));
    uVar1 = (uint)stack_record_18[3];
    break;
  case 4:
    uVar2 = diag_routine_class03_97bfc(param_3, (stack_record_18 + 4), ((uchar *)camry_host_ptr((uint32_t)(param_4))));
    uVar1 = (uint)stack_record_18[4];
    break;
  case 5:
    uVar2 = diag_routine_class03_97c30(param_3, (stack_record_18 + 5), ((uchar *)camry_host_ptr((uint32_t)(param_4))));
    uVar1 = (uint)stack_record_18[5];
    break;
  case 6:
    uVar2 = diag_routine_class03_97c64(param_3, (stack_record_18 + 6), ((uchar *)camry_host_ptr((uint32_t)(param_4))));
    uVar1 = (uint)stack_record_18[6];
    break;
  default:
    goto switchD_0009831a_caseD_7;
  case 9:
    uVar2 = request_routine_payload_service31_or_reset_97c98(param_3, param_2[5], camry_host_addr(param_2 + 6), param_4);
    return uVar2;
  case 10:
    uVar2 = diag_routine_class03_97cbc(param_3, (stack_record_18 + 7), ((uchar *)camry_host_ptr((uint32_t)(param_4))));
    uVar1 = (uint)stack_record_18[7];
    break;
  case 0xb:
    uVar2 = diag_routine_class03_97cf0(param_3, (stack_record_18 + 8), ((uchar *)camry_host_ptr((uint32_t)(param_4))));
    uVar1 = (uint)stack_record_18[8];
    break;
  case 0xc:
    uVar2 = diag_routine_class03_97d24(param_3, (stack_record_18 + 9), ((uchar *)camry_host_ptr((uint32_t)(param_4))));
    uVar1 = (uint)stack_record_18[9];
    break;
  case 0xd:
    uVar2 = diag_routine_class03_97d58(param_3, (stack_record_18 + 10), ((uchar *)camry_host_ptr((uint32_t)(param_4))));
    uVar1 = (uint)stack_record_18[10];
    break;
  case 0xe:
    uVar2 = diag_routine_class03_97d8c(param_3, (stack_record_18 + 11), ((uchar *)camry_host_ptr((uint32_t)(param_4))));
    uVar1 = (uint)stack_record_18[11];
    break;
  case 0xf:
    uVar2 = diag_routine_class03_97dc0(param_3, (stack_record_18 + 12), ((uchar *)camry_host_ptr((uint32_t)(param_4))));
    uVar1 = (uint)stack_record_18[12];
    break;
  case 0x10:
    uVar2 = diag_routine_class03_97df4(param_3, (stack_record_18 + 13), ((uchar *)camry_host_ptr((uint32_t)(param_4))));
    uVar1 = (uint)stack_record_18[13];
    break;
  case 0x11:
    uVar2 = diag_routine_class03_97e2a(param_3, (stack_record_18 + 14), ((uchar *)camry_host_ptr((uint32_t)(param_4))));
    uVar1 = (uint)stack_record_18[14];
    break;
  case 0x12:
    uVar2 = diag_routine_class03_97e60(param_3, (stack_record_18 + 15), ((uchar *)camry_host_ptr((uint32_t)(param_4))));
    uVar1 = (uint)stack_record_18[15];
  }
  *param_2 = uVar1;
switchD_0009831a_caseD_7:
  return uVar2;
}

undefined4
dispatch_routine_start_callbacks_by_row_9847a(undefined2 param_1,undefined2 *param_2,undefined1 param_3,undefined4 param_4)

{
  undefined4 uVar1;
  
  uVar1 = 0;
  switch(param_1) {
  case 0:
    uVar1 = diag_routine_class01_97e96(param_3, ((uchar *)camry_host_ptr((uint32_t)(*(undefined4 *)(param_2 + 10)))), param_2 + 0xc, ((uchar *)camry_host_ptr((uint32_t)(param_4))));
    break;
  case 1:
    uVar1 = diag_routine_class01_97ec2(param_3, ((uchar *)camry_host_ptr((uint32_t)(*(undefined4 *)(param_2 + 10)))), param_2 + 0xc, ((uchar *)camry_host_ptr((uint32_t)(param_4))));
    break;
  case 2:
    uVar1 = diag_routine_class01_97eee(param_3, ((uchar *)camry_host_ptr((uint32_t)(param_4))));
    break;
  case 3:
    uVar1 = invoke_routine_class_one_index_three_97f24(*param_2, param_3, ((uchar *)camry_host_ptr((uint32_t)(param_4))));
    break;
  case 4:
    uVar1 = diag_routine_class01_97f5c(param_3, ((uchar *)camry_host_ptr((uint32_t)(param_4))));
    break;
  case 5:
    uVar1 = diag_routine_class01_97f92(param_3, ((uchar *)camry_host_ptr((uint32_t)(param_4))));
    break;
  case 6:
    uVar1 = diag_routine_class01_97fc8(param_3, ((uchar *)camry_host_ptr((uint32_t)(param_4))));
    break;
  case 7:
    uVar1 = diag_routine_class01_97ffe(param_3, ((uchar *)camry_host_ptr((uint32_t)(param_4))));
    break;
  case 8:
    uVar1 = diag_routine_class01_98034(param_3, ((uchar *)camry_host_ptr((uint32_t)(param_4))));
    break;
  case 9:
    uVar1 = request_routine_class40_service31_or_reset_9806a(*(undefined4 *)(param_2 + 8), param_3, *(undefined4 *)(param_2 + 10), camry_host_addr(param_2 + 0xc), param_4);
    break;
  case 10:
    uVar1 = diag_routine_class01_98094(param_3, ((uchar *)camry_host_ptr((uint32_t)(*(undefined4 *)(param_2 + 10)))), param_2 + 0xc, ((uchar *)camry_host_ptr((uint32_t)(param_4))));
    break;
  case 0xb:
    uVar1 = diag_routine_class01_980c0(param_3, ((uchar *)camry_host_ptr((uint32_t)(param_4))));
    break;
  case 0xc:
    uVar1 = diag_routine_class01_980f6(param_3, ((uchar *)camry_host_ptr((uint32_t)(param_4))));
    break;
  case 0xd:
    uVar1 = diag_routine_class01_9812c(param_3, ((uchar *)camry_host_ptr((uint32_t)(param_4))));
    break;
  case 0xe:
    uVar1 = diag_routine_class01_98162(param_3, ((uchar *)camry_host_ptr((uint32_t)(param_4))));
    break;
  case 0xf:
    uVar1 = diag_routine_class01_98198(param_3, ((uchar *)camry_host_ptr((uint32_t)(param_4))));
    break;
  case 0x10:
    uVar1 = diag_routine_class01_981ce(param_3, ((uchar *)camry_host_ptr((uint32_t)(param_4))));
    break;
  case 0x11:
    uVar1 = diag_routine_class01_98206(param_3, ((uchar *)camry_host_ptr((uint32_t)(param_4))));
    break;
  case 0x12:
    uVar1 = diag_routine_class01_9823e(param_3, ((uchar *)camry_host_ptr((uint32_t)(param_4))));
  }
  return uVar1;
}

undefined4 dispatch_routine_stop_callbacks_rows_f_and_12_98590(short param_1,undefined4 param_2,undefined1 param_3,undefined4 param_4)

{
  undefined4 uVar1;
  
  if (param_1 == 0xf) {
    uVar1 = diag_routine_class02_98276(param_3, ((uchar *)camry_host_ptr((uint32_t)(param_4))));
  }
  else {
    uVar1 = 0;
    if (param_1 == 0x12) {
      uVar1 = diag_routine_class02_982ac(param_3, ((uchar *)camry_host_ptr((uint32_t)(param_4))));
    }
  }
  return uVar1;
}

undefined4 read_selected_proprietary_events_and_report_985bc(undefined1 *param_1)

{
  uint8_t stack_record_d[13];
  uint32_t puVar1;
  int iVar2;
  undefined4 uVar3;
  
  puVar1 = 0xfebeb800u;
  stack_record_d[0] = 0;
  (*((int32_t *)(stack_record_d + 1))) = DAT_febe5e48 - DAT_febe5e40;
  set_diagnostic_callback_pending_955b6(0);
  iVar2 = thunk_serialize_event_and_merge_selected_output_8e074(((uint32_t)((uint32_t)((*((int *)camry_host_ptr((uint32_t)(puVar1 + -0x59c0)))) + (*((int *)camry_host_ptr((uint32_t)(puVar1 + -0x59c4))))))), camry_host_addr((stack_record_d + 1)), camry_host_addr(stack_record_d));
  if (iVar2 == 0) {
    (*((int *)camry_host_ptr((uint32_t)(puVar1 + -0x59c0)))) = (*((int *)camry_host_ptr((uint32_t)(puVar1 + -0x59c0)))) + (*((int32_t *)(stack_record_d + 1)));
    dcm_report_positive_response(((F33DcmMessageContext *)camry_host_ptr((uint32_t)(puVar1 + -0x59cc))));
    uVar3 = 0;
  }
  else {
    uVar3 = 1;
    if (iVar2 == 10) {
      set_diagnostic_callback_pending_955b6(1);
      dcm_enqueue_event('\x16');
      uVar3 = 10;
    }
    else {
      *param_1 = stack_record_d[0];
    }
  }
  return uVar3;
}

uint dcm_begin_proprietary_event_read(F33DcmMessageContext *message,uchar selector)

{
  uchar **ppuVar1;
  uchar uVar2;
  undefined4 *puVar3;
  int iVar4;
  uint32_t puVar5;
  undefined2 uVar6;
  undefined2 uVar7;
  F33DcmMessageContext *pFVar8;
  uint uVar9;
  byte bVar10;
  undefined1 *puVar11;
  uchar uStack_11;
  
  puVar5 = 0xfebeb800u;
  puVar3 = ((undefined *)camry_host_ptr(0xfebe5e34u));
  pFVar8 = message + 1;
  do {
    ppuVar1 = &message->request;
    message = (F33DcmMessageContext *)&message->request_length;
    *puVar3 = *(uint32_t *)ppuVar1;
    puVar3 = puVar3 + 1;
  } while (camry_host_addr(pFVar8)!=camry_host_addr(message));
  uStack_11 = '\0';
  bVar10 = selector & 0xf;
  set_diagnostic_busy_marker_from_done_flag_9560e(0x0);
  set_diagnostic_callback_pending_955b6(0);
  if (bVar10 == 1) {
    iVar4 = 0;
    uVar6 = 0xffff;
    uVar9 = 0;
    uVar7 = 0xffff;
  }
  else {
    puVar11 = ((undefined1 *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)((puVar5 + -0x59cc))))))));
    uVar9 = 2;
    uVar6 = CONCAT11(*puVar11,puVar11[1]);
    if (bVar10 == 2) {
      uVar7 = 0xffff;
      iVar4 = 2;
    }
    else {
      iVar4 = 4;
      uVar7 = CONCAT11(puVar11[2],puVar11[3]);
    }
  }
  uVar2 = '\x13';
  if ((*((int *)camry_host_ptr((uint32_t)(puVar5 + -0x59c8)))) == iVar4) {
    if ((*((uint *)camry_host_ptr((uint32_t)(puVar5 + -0x59b8)))) < uVar9) {
      return 0;
    }
    if (bVar10 != 1) {
      (*((volatile undefined1 *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)((puVar5 + -0x59c4))))))))) = (*((volatile undefined1 *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)((puVar5 + -0x59cc)))))))));
      (*((undefined1 *)camry_host_ptr((uint32_t)((*((volatile int32_t *)camry_host_ptr((uint32_t)(puVar5 + -0x59c4)))) + 1)))) =
           (*((undefined1 *)camry_host_ptr((uint32_t)((*((volatile int32_t *)camry_host_ptr((uint32_t)(puVar5 + -0x59cc)))) + 1))));
    }
    (*((uint *)camry_host_ptr((uint32_t)(puVar5 + -0x59c0)))) = uVar9;
    iVar4 = select_proprietary_events_or_reset_selection_98850(0,selector,uVar6,uVar7);
    uVar2 = '1';
    if (iVar4 == 0) {
      iVar4 = read_selected_proprietary_events_and_report_985bc(&uStack_11);
      if (iVar4 == 0) {
        return 0;
      }
      if (iVar4 == 10) {
        return 10;
      }
      uVar2 = uStack_11;
      if (uStack_11 == '\x14') {
        return 0;
      }
    }
  }
  uStack_11 = uVar2;
  dcm_report_negative_or_pending(((F33DcmMessageContext *)camry_host_ptr((uint32_t)(puVar5 + -0x59cc))),uStack_11);
  return 0;
}

void cancel_proprietary_event_read_98712(undefined1 param_1)

{
  int iVar1;
  
  iVar1 = get_diagnostic_callback_pending_955bc();
  if (iVar1 == 1) {
    select_proprietary_events_or_reset_selection_98850(2,param_1,0xffff,0xffff);
    set_diagnostic_callback_pending_955b6(0);
  }
  dcm_invalidate_queued_event('\x16','\0');
  set_diagnostic_busy_marker_from_done_flag_9560e(1);
  return;
}

uint dispatch_proprietary_event_read_kind01_9874a(char param_1,F33DcmMessageContext *param_2)

{
  uint uVar1;
  
  if (param_1 == '\0') {
    uVar1 = dcm_begin_proprietary_event_read(param_2,'\x01');
  }
  else {
    uVar1 = 0;
    cancel_proprietary_event_read_98712(1);
  }
  return uVar1;
}

uint dispatch_proprietary_event_read_kind02_9876c(char param_1,F33DcmMessageContext *param_2)

{
  uint uVar1;
  
  if (param_1 == '\0') {
    uVar1 = dcm_begin_proprietary_event_read(param_2,'\x02');
  }
  else {
    uVar1 = 0;
    cancel_proprietary_event_read_98712(2);
  }
  return uVar1;
}

uint dispatch_proprietary_event_read_kind03_9878e(char param_1,F33DcmMessageContext *param_2)

{
  uint uVar1;
  
  if (param_1 == '\0') {
    uVar1 = dcm_begin_proprietary_event_read(param_2,'\x03');
  }
  else {
    uVar1 = 0;
    cancel_proprietary_event_read_98712(3);
  }
  return uVar1;
}

uint dispatch_proprietary_event_read_kind11_987b0(char param_1,F33DcmMessageContext *param_2)

{
  uint uVar1;
  
  if (param_1 == '\0') {
    uVar1 = dcm_begin_proprietary_event_read(param_2,'\x11');
  }
  else {
    uVar1 = 0;
    cancel_proprietary_event_read_98712(0x11);
  }
  return uVar1;
}

uint dispatch_proprietary_event_read_kind12_987d6(char param_1,F33DcmMessageContext *param_2)

{
  uint uVar1;
  
  if (param_1 == '\0') {
    uVar1 = dcm_begin_proprietary_event_read(param_2,'\x12');
  }
  else {
    uVar1 = 0;
    cancel_proprietary_event_read_98712(0x12);
  }
  return uVar1;
}

uint dispatch_proprietary_event_read_kind13_987fc(char param_1,F33DcmMessageContext *param_2)

{
  uint uVar1;
  
  if (param_1 == '\0') {
    uVar1 = dcm_begin_proprietary_event_read(param_2,'\x13');
  }
  else {
    uVar1 = 0;
    cancel_proprietary_event_read_98712(0x13);
  }
  return uVar1;
}

void resume_proprietary_event_read_and_report_error_98822(void)

{
  uint32_t puVar1;
  int iVar2;
  uchar uStack_5;
  
  puVar1 = 0xfebeb800u;
  uStack_5 = '\0';
  iVar2 = read_selected_proprietary_events_and_report_985bc(&uStack_5);
  if (((iVar2 != 0) && (iVar2 != 10)) && (uStack_5 != '\x14')) {
    dcm_report_negative_or_pending(((F33DcmMessageContext *)camry_host_ptr((uint32_t)(puVar1 + -0x59cc))),uStack_5);
  }
  return;
}

uint select_proprietary_events_or_reset_selection_98850(uchar param_1,uchar param_2,ushort param_3,ushort param_4)

{
  uint uVar1;
  
  if (param_1 == '\x02') {
    fill_constant_block_8de1a();
    uVar1 = 0;
  }
  else {
    uVar1 = begin_proprietary_event_selection(param_1,param_2,param_3,param_4);
  }
  return uVar1;
}

uint thunk_serialize_event_and_merge_selected_output_8e074(undefined4 param_1, undefined4 param_2, undefined4 param_3)

{
  return serialize_event_and_merge_selected_output_8e074(param_1, ((uint *)camry_host_ptr((uint32_t)(param_2))),  param_3);
}

void run_init_chain_9887c(void)

{
  dcm_reset_timer_slots();
  dcm_reset_event_ring();
  clear_diagnostic_callback_state_and_run_four_initializers_95590();
  reset_dcm_active_service_and_final_nrc_90ee6();
  run_init_chain_91ffa();
  return;
}

void conditionally_initialize_diagnostics_and_mark_a5_98898(void)

{
  undefined4 *puVar1;
  uint32_t puVar2;
  uint uVar3;
  
  puVar1 = ((void *)camry_host_ptr((uint32_t)(DAT_00026ae4)));
  puVar2 = (0xfebeb800u);
  if ((DAT_00026ae4 == 0) ||
     (puVar2 = (0xfebeb800u), uVar3 = return_const_0_98936(), uVar3 == (*((byte *)camry_host_ptr((uint32_t)(*puVar1)))))) {
    run_init_chain_9887c();
    (*((volatile undefined *)camry_host_ptr((uint32_t)(0xfebeb800u + (uint32_t)(-0x59b0) * 1u)))) = 0xa5;
  }
  return;
}

void dcm_foreground_cycle(void)

{
  if (dcm_foreground_enabled == 0xa5) {
    dcm_rewrite_dispatch_context_under_lock_91fbe();
    dcm_advance_software_timers();
    dcm_dispatch_entry_event_generation();
  }
  return;
}

undefined4 return_const_1_988e4(void)

{
  return 1;
}

undefined4 return_one_with_nonzero_argument_callback_988e8(int param_1)

{
  undefined4 uVar1;
  
  if (param_1 == 0) {
    uVar1 = 1;
  }
  else {
    uVar1 = return_const_1_988e4();
  }
  return uVar1;
}

void return_only_stub_98900(void)

{
  return;
}

void query_diagnostic_readiness_when_transport_and_service_idle_98902(void)

{
  int iVar1;
  
  iVar1 = is_dcm_phase_zero_without_receiving_slots_91e2c();
  if ((iVar1 == 1) && (iVar1 = is_dcm_active_service_callback_absent_9177c(), iVar1 == 1)) {
    query_diagnostic_readiness_unless_busy_955e4();
  }
  return;
}

void select_transport_idle_check_by_flag_9891e(char param_1)

{
  if (param_1 == '\x01') {
    is_dcm_phase_zero_without_receiving_slots_91e2c();
  }
  else {
    is_dcm_request_phase_zero_91e52();
  }
  return;
}

undefined4 return_const_0_98936(void)

{
  return 0;
}

void dcm_reset_event_ring(void)

{
  dcm_event_ring.producer = '\0';
  dcm_event_ring.consumer = '\0';
  dcm_event_ring.occupied_slots = '\0';
  return;
}

void dcm_dispatch_entry_event_generation(void)

{
  camry_write32((camry_sp - 4u) & ~3u, camry_gpr[26]);
  camry_write32((camry_sp - 8u) & ~3u, camry_gpr[27]);
  camry_write32((camry_sp - 12u) & ~3u, camry_gpr[28]);
  camry_write32((camry_sp - 16u) & ~3u, camry_gpr[29]);
  camry_write32((camry_sp - 20u) & ~3u, camry_gpr[31]);
  camry_sp -= 20u;
  camry_gpr[3] = camry_sp;

  uchar uVar1;
  uint uVar2;
  uint32_t puVar3;
  uint32_t puVar4;
  char cVar5;
  uint32_t pcVar6;
  byte bVar7;
  uint uVar8;
  
  uVar1 = dcm_event_ring.occupied_slots;
  puVar3 = 0xfebeb800u;
  puVar4 = 0x23dfcu;
  uVar8 = 0xff;
  bVar7 = 0;
LAB_000989c4:
  do {
    do {
      if (uVar1 <= bVar7) {
        { if (!camry_halted) { camry_gpr[26] = camry_read32((camry_sp + 16u) & ~3u); camry_gpr[27] = camry_read32((camry_sp + 12u) & ~3u); camry_gpr[28] = camry_read32((camry_sp + 8u) & ~3u); camry_gpr[29] = camry_read32((camry_sp + 4u) & ~3u); camry_gpr[31] = camry_read32((camry_sp + 0u) & ~3u); camry_sp += 20u; camry_gpr[3] = camry_sp; } return; }
      }
      bVar7 = bVar7 + 1;
      thunk_push_priority_mask_and_raise_to_ff00_6a45e();
      uVar2 = (uint)(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x59ae)))));
      if (uVar2 < 0x1f) {
        uVar8 = (uint)(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(uVar2 - 0x59ac)))));
      }
      cVar5 = '\0';
      if (uVar2 < 0x1e) {
        cVar5 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x59ae))))) + 1;
      }
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x59ae))))) = cVar5;
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x59ad))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x59ad))))) + -1;
      thunk_pop_and_restore_priority_mask_stack_6a4c4();
    } while (uVar8 == 0xff);
    if (0xea < uVar8) goto LAB_000989ac;
  } while (0x2c < uVar8);
  pcVar6 = (uint32_t)((uintptr_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(puVar4 + uVar8 * 4 + 0x2d1c)))));
  goto LAB_000989c0;
LAB_000989ac:
  uVar2 = uVar8 + 0x15 & 0xff;
  if (uVar2 < 8) {
    pcVar6 = (uint32_t)((uintptr_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(puVar4 + uVar2 * 4 + 0x2cfc)))));
LAB_000989c0:
    (*(int (*)())camry_indirect((camry_gpr[26] = uVar1, camry_gpr[27] = (uint32_t)(uintptr_t)pcVar6, camry_gpr[28] = bVar7, camry_gpr[29] = uVar8, camry_gpr[6] = uVar8, camry_gpr[31] = 0x989c4u, (uint32_t)(pcVar6))))(uVar8);
  }
  goto LAB_000989c4;
}

uint dcm_validate_event_id(uchar event_id)

{
  uint uVar1;
  uint uVar2;
  
  uVar1 = (uint)event_id;
  uVar2 = 1;
  if ((uVar1 < 0x2c) ||
     ((0xea < uVar1 && ((int)(uVar1 - (dcm_extended_event_count + 0xeb)) < 0)))) {
    uVar2 = 0;
  }
  return uVar2;
}

uint dcm_enqueue_event(uchar event_id)

{
  byte bVar1;
  byte bVar2;
  uint32_t puVar3;
  uint uVar4;
  char cVar5;
  uint uVar6;
  
  puVar3 = 0xfebeb800u;
  uVar6 = 1;
  uVar4 = dcm_validate_event_id(event_id);
  if (uVar4 == 0) {
    thunk_push_priority_mask_and_raise_to_ff00_6a45e();
    bVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x59ad)))));
    if (bVar1 < 0x1f) {
      bVar2 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x59af)))));
      uVar4 = (uint)bVar2;
      uVar6 = 0;
      if (uVar4 < 0x1f) {
        (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(uVar4 - 0x59ac))))) = event_id;
      }
      cVar5 = '\0';
      if (uVar4 < 0x1e) {
        cVar5 = bVar2 + 1;
      }
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x59af))))) = cVar5;
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x59ad))))) = bVar1 + 1;
    }
    else {
      uVar6 = 2;
    }
    thunk_pop_and_restore_priority_mask_stack_6a4c4();
  }
  return uVar6;
}

uint dcm_invalidate_queued_event(uchar event_id,uchar first_only)

{
  byte bVar1;
  bool bVar2;
  uint32_t puVar3;
  uint uVar4;
  uint uVar5;
  byte bVar6;
  
  puVar3 = 0xfebeb800u;
  bVar6 = 0;
  bVar2 = false;
  uVar5 = 1;
  uVar4 = dcm_validate_event_id(event_id);
  if (uVar4 == 0) {
    uVar5 = 3;
    thunk_push_priority_mask_and_raise_to_ff00_6a45e();
    bVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x59ad)))));
    uVar4 = (uint)(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x59ae)))));
    do {
      if (bVar1 <= bVar6) break;
      bVar6 = bVar6 + 1;
      if ((uVar4 < 0x1f) && (event_id == (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(uVar4 - 0x59ac))))))) {
        (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(uVar4 - 0x59ac))))) = 0xff;
        if (first_only == '\x01') {
          bVar2 = true;
        }
        uVar5 = 0;
      }
      if (uVar4 < 0x1e) {
        uVar4 = uVar4 + 1 & 0xff;
      }
      else {
        uVar4 = 0;
      }
    } while (!bVar2);
    thunk_pop_and_restore_priority_mask_stack_6a4c4();
  }
  return uVar5;
}

uint dcm_post_service_event(uchar event_id)

{
  return dcm_enqueue_event(event_id);
}

uint dcm_cancel_service_events(uchar event_id,uchar first_only)

{
  return dcm_invalidate_queued_event(event_id,first_only);
}

void dcm_reset_timer_slots(void)

{
  uint uVar1;
  uint uVar2;
  
  uVar2 = 0;
  do {
    uVar1 = uVar2 + 1;
    (*((volatile uint32_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe5e74u + (uint32_t)(uVar2) * (uint32_t)sizeof(F33DcmSoftwareTimer)) + (uint32_t)(0) * (uint32_t)sizeof(F33DcmSoftwareTimer) + (uint32_t)offsetof(F33DcmSoftwareTimer, remaining))))) = 0;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe5e74u + (uint32_t)(uVar2) * (uint32_t)sizeof(F33DcmSoftwareTimer)) + (uint32_t)(0) * (uint32_t)sizeof(F33DcmSoftwareTimer) + (uint32_t)offsetof(F33DcmSoftwareTimer, active))))) = '\0';
    uVar2 = uVar1;
  } while (uVar1 < 9);
  return;
}

void dcm_advance_software_timers(void)

{
  uint *puVar1;
  bool bVar2;
  uint32_t puVar3;
  uint32_t puVar4;
  uint uVar5;
  
  puVar3 = 0xfebeb800u;
  puVar4 = 0x23dfcu;
  uVar5 = 0;
  do {
    bVar2 = false;
    thunk_push_priority_mask_and_raise_to_ff00_6a45e();
    puVar1 = ((uint *)camry_host_ptr((uint32_t)(puVar3 + uVar5 * 8 + -0x598c)));
    if ((char)puVar1[1] == '\x01') {
      if (*puVar1 < (*((uint *)camry_host_ptr((uint32_t)(puVar4 + 0x2cf0))))) {
        *(undefined1 *)(puVar1 + 1) = 0;
        bVar2 = true;
      }
      else {
        *puVar1 = ((uint32_t)((uint32_t)(*puVar1 - (*((int *)camry_host_ptr((uint32_t)(puVar4 + 0x2cf0)))))));
      }
    }
    thunk_pop_and_restore_priority_mask_stack_6a4c4();
    if (bVar2) {
      (*(int (*)())camry_indirect((uint32_t)(((((code *)(uintptr_t)((uint32_t)((uintptr_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(puVar4 + uVar5 * 4 + 0x2dd0))))))))))))(uVar5);
    }
    uVar5 = uVar5 + 1;
  } while (uVar5 < 9);
  return;
}

void dcm_arm_software_timer(uchar timer_slot,uint duration)

{
  uint32_t puVar1;
  uint32_t puVar2;
  uint uVar3;
  
  uVar3 = (uint)timer_slot;
  puVar1 = 0xfebeb800u;
  puVar2 = 0x23dfcu;
  if (uVar3 < 9) {
    thunk_push_priority_mask_and_raise_to_ff00_6a45e();
    (*((uint *)camry_host_ptr((uint32_t)(puVar1 + uVar3 * 8 + -0x598c)))) = (*((int *)camry_host_ptr((uint32_t)(puVar2 + 0x2cf0)))) + -1 + duration;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(uVar3 * 8 + -0x5988))))) = 1;
    thunk_pop_and_restore_priority_mask_stack_6a4c4();
  }
  return;
}

void dcm_cancel_software_timer(uchar timer_slot)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  if (timer_slot < 9) {
    thunk_push_priority_mask_and_raise_to_ff00_6a45e();
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)((uint)timer_slot * 8 + -0x5988))))) = 0;
    thunk_pop_and_restore_priority_mask_stack_6a4c4();
  }
  return;
}

void thunk_push_priority_mask_and_raise_to_ff00_6a45e(void)

{
  push_priority_mask_and_raise_to_ff00_6a45e();
  return;
}

void thunk_pop_and_restore_priority_mask_stack_6a4c4(void)

{
  pop_and_restore_priority_mask_stack_6a4c4();
  return;
}

undefined1 dispatch_eight_byte_command_reply_98e80(undefined1 param_1,char *param_2,undefined2 param_3)

{
  int iVar1;
  int iVar2;
  uint32_t puVar3;
  int iVar4;
  int iVar5;
  undefined1 uVar6;
  
  puVar3 = 0x23dfcu;
  if (DAT_00030d68 == '\0') {
    iVar4 = wrapper_session_id_not_active_83072(param_1);
    uVar6 = 0;
    if (iVar4 == 0) {
      iVar4 = 0;
      do {
        if (*param_2 == (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(iVar4 * 8 + 0x7454)))))) {
          iVar5 = (*(int (*)())camry_indirect((uint32_t)(((((code *)(uintptr_t)((uint32_t)((uintptr_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(puVar3 + iVar4 * 8 + 0x7454 + 4))))))))))))(camry_host_addr(param_2),param_3, param_3);
          uVar6 = 1;
          break;
        }
        iVar2 = iVar4 + 1;
        iVar1 = iVar4 + -6;
        iVar5 = 0;
        iVar4 = iVar2;
      } while (((iVar1 < 0) || (iVar2 < 0)));
      if (iVar5 == 0x5a) {
        send_bounded_zero_padded_packet_8300e(param_1, (int)((uint32_t)(0xfebe5ebcu)), 8);
      }
    }
  }
  else {
    uVar6 = 1;
  }
  return uVar6;
}

undefined4 return_const_5_98eee(void)

{
  return 5;
}

undefined4 test_memory_span_overlap_with_configured_ranges_98ef2(undefined *param_1,uint param_2)

{
  int iVar1;
  
  iVar1 = 0;
  while( true ) {
    if (iVar1 - (*((volatile int32_t *)camry_host_ptr(0x2b218u))) < 0 ==
        (iVar1 < 0 != (*((volatile int32_t *)camry_host_ptr(0x2b218u))) < 0 && (*((volatile int32_t *)camry_host_ptr(0x2b218u))) < 0 == iVar1 - (*((volatile int32_t *)camry_host_ptr(0x2b218u))) < 0)) {
      return 0;
    }
    if (((uint32_t)camry_host_addr(param_1) <= (*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x29258u + (uint32_t)(iVar1 * 2) * 4u))))) &&
       ((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x29254u + (uint32_t)(iVar1 * 2) * 4u)))) <= (uint32_t)camry_host_addr(param_1) + ((param_2 & 0xff) - 1))) break;
    iVar1 = iVar1 + 1;
  }
  return 1;
}

bool reject_memory_span_outside_configured_window_98f2c(undefined *param_1,uint param_2)

{
  if (PTR_DAT_0002b21c <= (uint32_t)camry_host_addr(param_1)) {
    return PTR_DAT_0002b220 < (uint32_t)camry_host_addr(param_1) + ((param_2 & 0xff) - 1);
  }
  return true;
}

void reset_eight_byte_reply_and_memory_mode_flags_98f4c(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  
  iVar3 = 0;
  do {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe5ebcu + (uint32_t)(iVar3) * 1u)))) = 0;
    iVar2 = iVar3 + 1;
    iVar1 = iVar3 + -7;
    iVar3 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  DAT_febe5ec4 = 1;
  DAT_febe5ec5 = 0;
  DAT_febe5ec6 = 0;
  return;
}

void build_ff_success_or_fe_error_reply_98f6e(int param_1,char param_2,undefined1 param_3)

{
  int iVar1;
  int iVar2;
  int iVar3;
  
  if (param_2 == 'Z') {
    DAT_febe5ebc = 0xff;
    iVar3 = 1;
    do {
      iVar2 = iVar3 + 1;
      iVar1 = iVar3 + -7;
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe5ebcu + (uint32_t)(iVar3) * 1u)))) = (*((undefined1 *)camry_host_ptr((uint32_t)(iVar3 + param_1))));
      iVar3 = iVar2;
    } while (((iVar1 < 0) || (iVar2 < 0)));
    return;
  }
  DAT_febe5ebc = 0xfe;
  iVar3 = 2;
  DAT_febe5ebd = param_3;
  do {
    iVar2 = iVar3 + 1;
    iVar1 = iVar3 + -7;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe5ebcu + (uint32_t)(iVar3) * 1u)))) = (*((undefined1 *)camry_host_ptr((uint32_t)(iVar3 + param_1))));
    iVar3 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  return;
}

undefined4 build_fixed_reply_payload_01320111_98fba(undefined4 param_1,short param_2)

{
  uint8_t stack_record_c[12];
  int iVar1;
  int iVar2;
  int iVar3;
  undefined4 uVar4;
  
  uVar4 = 0xa5;
  iVar3 = 0;
  do {
    ((uint8_t *)(stack_record_c))[iVar3] = 0;
    iVar2 = iVar3 + 1;
    iVar1 = iVar3 + -7;
    iVar3 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  if (param_2 == 8) {
    stack_record_c[4] = 1;
    stack_record_c[6] = 1;
    uVar4 = 0x5a;
    ((uint8_t *)(stack_record_c))[2] = 0;
    stack_record_c[5] = 0x32;
    stack_record_c[7] = 0x11;
  }
  build_ff_success_or_fe_error_reply_98f6e(camry_host_addr(((uint8_t *)(stack_record_c))), uVar4, 0x21);
  return 0x5a;
}
