#include "common.h"

uint dcm_resolve_subfunction
               (F33DcmMessageContext *message,F33DcmSubfunctionSelection *selection,
               uchar *negative_response)

{
  uchar uVar1;
  uchar *puVar2;
  F33DcmSubfunction *pFVar3;
  uint uVar4;
  F33DcmSubfunction *pFVar5;
  
  *negative_response = '\0';
  puVar2 = ((void *)camry_host_ptr((uint32_t)(message->request)));
  selection->subfunction = 0;
  pFVar3 = ((F33DcmSubfunction *)camry_host_ptr((uint32_t)(((F33DcmService *)camry_host_ptr((uint32_t)(selection->service)))->subfunctions)));
  if (message->request_length < 2) {
    uVar1 = '\x13';
  }
  else {
    for (uVar4 = 0; pFVar5 = (F33DcmSubfunction *)0x0, uVar4 < ((F33DcmService *)camry_host_ptr((uint32_t)(selection->service)))->subfunction_count
        ; uVar4 = uVar4 + 1 & 0xff) {
      pFVar5 = pFVar3 + uVar4;
      if ((camry_host_addr(((pFVar3 + uVar4)))!=camry_host_addr((((F33DcmSubfunction *)0x0)))) &&
         ((uintptr_t)(((((puVar2[1] & 0x7f)))))==(uintptr_t)((((pFVar5->subfunction)))))) {
        selection->subfunction = camry_host_addr(pFVar5);
        break;
      }
    }
    if (camry_host_addr((pFVar5))!= 0) {
      uVar4 = dcm_check_session_list(((uchar *)camry_host_ptr((uint32_t)(pFVar5->sessions))), pFVar5->session_count);
      if (uVar4 == 0) {
        uVar4 = dcm_check_security_list
                          (((uint8_t *)camry_host_ptr((uint32_t)(((F33DcmSubfunction *)camry_host_ptr((uint32_t)(selection->subfunction)))->security))),((F33DcmSubfunction *)camry_host_ptr((uint32_t)(selection->subfunction)))->security_count);
        if (uVar4 == 0) {
          return 0;
        }
        uVar1 = '3';
      }
      else {
        uVar1 = '~';
      }
      *negative_response = uVar1;
      return 1;
    }
    uVar1 = '\x12';
  }
  *negative_response = uVar1;
  return 1;
}

uint dcm_invoke_request_policy
               (uchar service_id,F33DcmMessageContext *message,uint stage,uchar *negative_response)

{
  uint8_t stack_record_2e[46];
  char cVar1;
  undefined4 *puVar2;
  uint uVar3;
  uint32_t puVar4;
  byte bVar5;
  uint uVar6;
  
  *negative_response = '\0';
  uVar3 = 0;
  cVar1 = DAT_00025bf8;
  if ((stage & 2) != 0) {
    cVar1 = DAT_00025bf9;
  }
  if (cVar1 == '\x01') {
    puVar2 = ((undefined4 *)camry_host_ptr((uint32_t)(PTR_PTR_00025bfc)));
    if ((stage & 2) != 0) {
      puVar2 = ((undefined4 *)camry_host_ptr((uint32_t)(PTR_PTR_00025c04)));
    }
    if (camry_host_addr((puVar2))!= 0) {
      bVar5 = message->addressing_kind;
      puVar4 = ((uint32_t)(message->request));
      uVar6 = message->request_length;
      if ((stage & 1) == 0) {
        puVar4 = puVar4 + 1;
        uVar6 = uVar6 - 1;
      }
      else {
        bVar5 = bVar5 | 0x10;
      }
      if (0xffff < uVar6) {
        uVar6 = 0xffff;
      }
      stack_record_2e[0] = '\0';
      stack_record_2e[1] = service_id;
      uVar6 = (*(int (*)())camry_indirect((uint32_t)(*puVar2)))(service_id,puVar4,uVar6 & 0xffff,bVar5,
                                 message->service_list_selector,camry_host_addr(stack_record_2e));
      if (uVar6 != 0) {
        uVar3 = uVar6;
        if (uVar6 == 1) {
          *negative_response = stack_record_2e[0];
        }
        else {
          *negative_response = stack_record_2e[0];
        }
      }
    }
  }
  return uVar3;
}

void dcm_stage_negative_response(F33DcmMessageContext *message,uchar nrc)

{
  uint32_t puVar1;
  undefined4 uVar2;
  
  puVar1 = 0xfebeb800u;
  uVar2 = get_dcm_current_service_id_9168e();
  if (nrc == 'x') {
    request_dcm_explicit_pending_response_in_phase_two_91df8(uVar2);
  }
  else {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x61dc))))) = nrc;
    build_dcm_final_negative_response_bytes_91cd2(uVar2,nrc);
  }
  return;
}

void dcm_select_response_disposition(F33DcmMessageContext *message)

{
  char cVar1;
  uint32_t puVar2;
  uchar disposition;
  uint uVar3;
  int iVar4;
  int iVar5;
  
  puVar2 = (0xfebeb800u);
  if ((DAT_00026aeb == '\x01') ||
     (puVar2 = (0xfebeb800u), uVar3 = get_dcm_current_service_id_9168e(), (uVar3 >> 6 & 1) == 0)) {
    iVar4 = get_dcm_pending_transport_accepted_guarded_91bf2();
    iVar5 = thunk_dcm_get_current_receive_descriptor_flag_nine_93d9a();
    cVar1 = (*((volatile undefined *)camry_host_ptr((uint32_t)(0xfebeb800u + (uint32_t)(-0x61dc) * 1u))));
    if (cVar1 == '\0') {
      disposition = '\0';
      if ((iVar4 == 0) &&
         ((message->suppress_positive != '\0' ||
          ((message->addressing_kind == '\x01' && (iVar5 == 1)))))) {
        disposition = '\x02';
      }
    }
    else {
      disposition = '\x01';
      if (((iVar4 == 0) && (message->addressing_kind == '\x01')) &&
         ((cVar1 == '\x11' ||
          ((((cVar1 == '\x12' || (cVar1 == '1')) || (cVar1 == '~')) ||
           ((cVar1 == '\x7f' || (iVar5 == 1)))))))) {
        disposition = '\x03';
      }
    }
  }
  else if ((*((volatile undefined *)camry_host_ptr((uint32_t)(0xfebeb800u + (uint32_t)(-0x61dc) * 1u)))) == '\0') {
    disposition = '\x02';
  }
  else {
    disposition = '\x03';
  }
  dcm_stage_final_response(message,disposition);
  return;
}

void dcm_complete_service_response(F33DcmMessageContext *message)

{
  uchar uVar1;
  F33DcmMessageContext *message_00;
  int iVar2;
  
  message_00 = dcm_get_message_context();
  message_00->request_length = message->request_length;
  iVar2 = get_dcm_status_byte_562d_916a6();
  message_00->response_length = message->response_length + iVar2;
  uVar1 = message->suppress_positive;
  message_00->addressing_kind = message->addressing_kind;
  message_00->suppress_positive = uVar1;
  message_00->service_id = message->service_id;
  message_00->service_list_selector = message->service_list_selector;
  dcm_select_response_disposition(message_00);
  return;
}

void clear_dcm_final_negative_response_code_912b2(void)

{
  dcm_final_nrc = '\0';
  return;
}

void reset_dcm_final_negative_response_code_912b8(void)

{
  dcm_final_nrc = '\0';
  return;
}

uint dcm_deliver_response_notification(uchar result,uchar pending_notification)

{
  uint32_t puVar1;
  F33DcmMessageContext *pFVar2;
  int iVar3;
  undefined4 uVar4;
  
  puVar1 = 0x23dfcu;
  if (pending_notification == '\0') {
    pFVar2 = dcm_get_message_context();
    iVar3 = is_dcm_active_service_callback_present_9169a();
    if (iVar3 == 1) {
      invoke_matching_completion_callback_and_clear_busy_95650(pFVar2->service_id,pFVar2->service_list_selector,result);
    }
    uVar4 = get_dcm_current_service_id_9168e();
    if (((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x1dfc))))) == '\x01') && ((*((int *)camry_host_ptr((uint32_t)(0x1e04u + (int)puVar1)))) != 0)) {
      (*(int (*)())camry_indirect((uint32_t)(*(((undefined4 *)camry_host_ptr((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x1e04u + (int)puVar1))))))))))(uVar4,pFVar2->addressing_kind,pFVar2->service_list_selector,result);
    }
    if (((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x1dfd))))) == '\x01') && ((*((int *)camry_host_ptr((uint32_t)(puVar1 + 0x1e0c)))) != 0)) {
      (*(int (*)())camry_indirect((uint32_t)(*(((undefined4 *)camry_host_ptr((*((volatile uint32_t *)camry_host_ptr((uint32_t)(puVar1 + 0x1e0c))))))))))(uVar4,pFVar2->addressing_kind,pFVar2->service_list_selector,result);
    }
    dcm_clear_active_service();
    reset_dcm_final_negative_response_code_912b8();
  }
  else {
    dcm_notify_active_service_operation_three();
  }
  return 0;
}

void stage_dcm_final_response_kind_three_9136c(F33DcmMessageContext *param_1)

{
  dcm_stage_final_response(param_1,'\x03');
  return;
}

void thunk_stage_dcm_final_response_kind_three_9136c(undefined4 param_1)

{
  stage_dcm_final_response_kind_three_9136c(((F33DcmMessageContext *)camry_host_ptr((uint32_t)(param_1))));
  return;
}

void dcm_reset_message_context(void)

{
  dcm_message_context.request = 0;
  dcm_message_context.request_length = 0;
  dcm_message_context.response = 0;
  dcm_message_context.response_length = 0;
  dcm_message_context.addressing_kind = '\0';
  dcm_message_context.suppress_positive = '\0';
  dcm_message_context.response_capacity = 0;
  dcm_message_context.service_id = '\0';
  dcm_message_context.service_list_selector = 0;
  return;
}

void dcm_clear_active_service(void)

{
  DAT_febe562c = 0;
  dcm_active_service_callback = 0;
  DAT_febe562d = 0;
  dcm_reset_message_context();
  return;
}

void clear_dcm_active_service_callback_913b6(void)

{
  dcm_clear_active_service();
  return;
}

void dcm_initialize_message_context
               (ushort service_list_selector,uchar addressing_kind,F33PduInfo *request,
               F33PduInfo *response)

{
  dcm_message_context.request = ((uint32_t)((uint32_t)(request->data)));
  dcm_message_context.response_length = 0;
  dcm_message_context.addressing_kind = addressing_kind;
  dcm_message_context.request_length = (uint)request->length;
  dcm_message_context.suppress_positive = '\0';
  dcm_message_context.service_id = '\0';
  dcm_message_context.response = ((uint32_t)((uint32_t)(response->data)));
  dcm_message_context.service_list_selector = service_list_selector;
  dcm_message_context.response_capacity = (uint)response->length;
  return;
}

void set_dcm_current_service_id_913ea(undefined1 param_1)

{
  DAT_febe562c = param_1;
  return;
}

uint dcm_select_service_list(ushort selector)

{
  uint uVar1;
  
  uVar1 = 0;
  do {
    if ((*((volatile uint16_t *)camry_host_ptr((uint32_t)((uint32_t)(0x25c0cu + (uint32_t)(uVar1) * (uint32_t)sizeof(F33DcmServiceList)) + (uint32_t)(0) * (uint32_t)sizeof(F33DcmServiceList) + (uint32_t)offsetof(F33DcmServiceList, selector))))) == selector) {
      return uVar1;
    }
    uVar1 = uVar1 + 1;
  } while (uVar1 < 3);
  return 0;
}

void dcm_dispatch_direct_service(F33DcmMessageContext *message,F33DcmService *service)

{
  *((uint8_t *)camry_host_ptr((uint32_t)(message->response))) = *((uint8_t *)camry_host_ptr((uint32_t)(message->request))) | 0x40;
  message->request = message->request + 1;
  message->request_length = message->request_length - 1;
  message->response = message->response + 1;
  message->response_capacity = message->response_capacity - 1;
  DAT_febe562d = 1;
  if (service->callback == 0) {
    stage_dcm_final_response_kind_three_9136c(message);
  }
  else {
    dcm_active_service_callback = service->callback;
    (*(int (*)())camry_indirect((uint32_t)(dcm_active_service_callback)))(0,camry_host_addr(message));
  }
  return;
}

void dcm_dispatch_subfunction_service(F33DcmMessageContext *message,F33DcmService *service)

{
  uchar service_id;
  uint32_t puVar1;
  byte bVar2;
  uint uVar3;
  uint32_t pFVar4;
  byte *pbVar5;
  uchar uStack_11;
  F33DcmSubfunctionSelection FStack_10;
  
  puVar1 = 0xfebeb800u;
  uStack_11 = '\0';
  FStack_10.subfunction = 0;
  FStack_10.service = camry_host_addr(service);
  uVar3 = dcm_resolve_subfunction(message,&FStack_10,&uStack_11);
  bVar2 = *((uint8_t *)camry_host_ptr((uint32_t)(message->request)));
  if (uVar3 == 0) {
    *((uint8_t *)camry_host_ptr((uint32_t)(message->response))) = bVar2 | 0x40;
    service_id = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x61d4)))));
    uStack_11 = '\0';
    message->request = message->request + 1;
    message->request_length = message->request_length - 1;
    uVar3 = dcm_invoke_request_policy(service_id,message,1,&uStack_11);
    if (uVar3 == 0) {
      uStack_11 = '\0';
      uVar3 = dcm_invoke_request_policy((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x61d4))))),message,3,&uStack_11);
      if (uVar3 != 0) goto LAB_00091534;
      pbVar5 = ((void *)camry_host_ptr((uint32_t)(message->request)));
      message->suppress_positive = '\0';
      if ((*pbVar5 & 0x80) != 0) {
        message->suppress_positive = '\x01';
      }
      *pbVar5 = *pbVar5 & 0x7f;
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)((uint32_t)(message->response) + (uint32_t)(1) * 1u)))) = *((uint8_t *)camry_host_ptr((uint32_t)(message->request)));
      message->request = message->request + 1;
      message->request_length = message->request_length - 1;
      message->response = message->response + 2;
      message->response_capacity = message->response_capacity - 2;
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x61d3))))) = 2;
      if ((*((volatile uint32_t *)camry_host_ptr((uint32_t)(((FStack_10.subfunction)))))) != 0x0u) {
        pFVar4 = (*((volatile uint32_t *)camry_host_ptr((uint32_t)(((FStack_10.subfunction))))));
        (*((volatile uint32_t *)camry_host_ptr((uint32_t)((puVar1 + -0x61d8))))) = pFVar4;
        (*(int (*)())camry_indirect((uint32_t)(pFVar4)))('\0',camry_host_addr(message));
        return;
      }
    }
    else {
LAB_00091534:
      bVar2 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x61d4)))));
      if (uVar3 == 1) goto LAB_0009154a;
      invoke_matching_nonzero_tag_callback_955c2(bVar2,0);
    }
    stage_dcm_final_response_kind_three_9136c(message);
  }
  else {
LAB_0009154a:
    invoke_matching_nonzero_tag_callback_955c2(bVar2,uStack_11);
    dcm_stage_negative_response(message,uStack_11);
    dcm_complete_service_response(message);
  }
  return;
}

void dcm_begin_service_request
               (F33DcmRequestRoute *route,F33PduInfo *request,F33PduInfo *response)

{
  uint8_t stack_record_16[22];
  uint32_t puVar1;
  uint32_t puVar2;
  undefined1 uVar3;
  uint uVar4;
  F33DcmMessageContext *message;
  F33DcmServiceSelection FStack_14;
  
  puVar1 = 0xfebeb800u;
  puVar2 = 0x23dfcu;
  stack_record_16[1] = '\0';
  stack_record_16[0] = '\0';
  dcm_initialize_message_context
            (route->service_list_selector,route->addressing_kind,request,response);
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x61b8))))) = *(((undefined1 *)camry_host_ptr((*((volatile uint32_t *)camry_host_ptr((uint32_t)(puVar1 + -0x61d0)))))));
  set_dcm_current_service_id_913ea(*(((undefined1 *)camry_host_ptr((*((volatile uint32_t *)camry_host_ptr((uint32_t)(puVar1 + -0x61d0))))))));
  message = ((F33DcmMessageContext *)camry_host_ptr((uint32_t)(puVar1 + -0x61d0)));
  uVar4 = dcm_invoke_request_policy(*(((uchar *)camry_host_ptr((*((volatile uint32_t *)camry_host_ptr((uint32_t)(puVar1 + -0x61d0))))))),message,0,((uint8_t *)((stack_record_16 + 1))));
  if (uVar4 == 0) {
    uVar4 = dcm_select_service_list(route->service_list_selector);
    FStack_14.list = camry_host_addr(((F33DcmServiceList *)camry_host_ptr((uint32_t)(0x1e10u + (int)(puVar2 + uVar4 * 8)))));
    FStack_14.service = 0;
    stack_record_16[1] = '\0';
    uVar4 = dcm_resolve_service(message,&FStack_14,((uint8_t *)(stack_record_16)),((uint8_t *)((stack_record_16 + 1))));
    if (uVar4 != 0) {
      uVar3 = 0;
      if (stack_record_16[1] != '\x11') {
        uVar3 = *(((undefined1 *)camry_host_ptr((*((volatile uint32_t *)camry_host_ptr((uint32_t)(puVar1 + -0x61d0)))))));
      }
      goto LAB_0009162a;
    }
    stack_record_16[1] = '\0';
    uVar4 = dcm_invoke_request_policy(*(((uchar *)camry_host_ptr((*((volatile uint32_t *)camry_host_ptr((uint32_t)(puVar1 + -0x61d0))))))),message,2,((uint8_t *)((stack_record_16 + 1))));
    if (uVar4 == 0) {
      if (stack_record_16[0] == '\0') {
        dcm_dispatch_direct_service(message, ((F33DcmService *)camry_host_ptr((uint32_t)(FStack_14.service))));
        return;
      }
      dcm_dispatch_subfunction_service(message, ((F33DcmService *)camry_host_ptr((uint32_t)(FStack_14.service))));
      return;
    }
    uVar3 = *(((undefined1 *)camry_host_ptr((*((volatile uint32_t *)camry_host_ptr((uint32_t)(puVar1 + -0x61d0)))))));
  }
  else {
    uVar3 = 0;
  }
  if (uVar4 != 1) {
    invoke_matching_nonzero_tag_callback_955c2(uVar3,0);
    stage_dcm_final_response_kind_three_9136c(message);
    return;
  }
LAB_0009162a:
  invoke_matching_nonzero_tag_callback_955c2(uVar3,stack_record_16[1]);
  dcm_stage_negative_response(message,stack_record_16[1]);
  dcm_complete_service_response(message);
  return;
}

void dcm_cancel_active_service(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  if (dcm_active_service_callback !=0x0u) {
    dcm_reset_message_context();
    (*(int (*)())camry_indirect((uint32_t)(*((code * *)camry_host_ptr((uint32_t)(puVar1 + -0x61d8))))))(2,puVar1 + -0x61d0);
  }
  reset_dcm_final_negative_response_code_912b8();
  dcm_clear_active_service();
  return;
}

F33DcmMessageContext * dcm_get_message_context(void)

{
  return ((undefined *)camry_host_ptr(0xfebe5630u));
}

undefined1 get_dcm_current_service_id_9168e(void)

{
  return DAT_febe562c;
}

undefined1 get_first_request_byte_91694(undefined1 *param_1)

{
  return *param_1;
}

bool is_dcm_active_service_callback_present_9169a(void)

{
  return dcm_active_service_callback != 0x0u;
}

undefined1 get_dcm_status_byte_562d_916a6(void)

{
  return DAT_febe562d;
}

void dcm_notify_active_service_operation_three(void)

{
  if (dcm_active_service_callback !=0x0u) {
    (*(int (*)())camry_indirect((uint32_t)(dcm_active_service_callback)))('\x03',(0xfebe5630u));
  }
  return;
}

bool is_functional_suppressed_tester_present_916c6(char param_1,undefined4 *param_2)

{
  bool bVar1;
  
  bVar1 = false;
  if (((param_1 == '\x01') && (*(short *)(param_2 + 1) == 2)) && ((*((char *)camry_host_ptr((uint32_t)(*param_2 ))))== '>')) {
    bVar1 = (((char *)camry_host_ptr((uint32_t)(*param_2))))[1] == -0x80;
  }
  return bVar1;
}

undefined4 check_dcm_service_and_optional_subfunction_membership_916ec(char param_1,ushort param_2,char param_3)

{
  short *psVar1;
  uint uVar2;
  uint32_t puVar3;
  uint uVar4;
  
  puVar3 = 0x23dfcu;
  uVar4 = dcm_select_service_list(param_2);
  uVar2 = 0;
  while( true ) {
    if ((byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x1e10u + (uint32_t)((int)(puVar3 + uVar4 * 8 + 2)))))) <= uVar2) {
      return 1;
    }
    psVar1 = ((short *)camry_host_ptr((uint32_t)(uVar2 * 2 + (*((volatile int *)camry_host_ptr((uint32_t)(0x23dfcu + (uint32_t)(uVar4 * 8 + 0x1e14) * 1u)))))));
    if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(*psVar1 * 0x18 + 0x1e68))))) == param_1) break;
    uVar2 = uVar2 + 1 & 0xff;
  }
  uVar2 = 0;
  if ((*((int *)camry_host_ptr((uint32_t)(puVar3 + *psVar1 * 0x18 + 0x1e60)))) != 0) {
    while( true ) {
      if ((byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(*psVar1 * 0x18 + 0x1e6b))))) <= uVar2) {
        return 1;
      }
      if ((*((char *)camry_host_ptr((uint32_t)((*((volatile int32_t *)camry_host_ptr((uint32_t)(puVar3 + *psVar1 * 0x18 + 0x1e60)))) + uVar2)))) == param_3) break;
      uVar2 = uVar2 + 1 & 0xff;
    }
  }
  return 0;
}

bool is_dcm_active_service_callback_absent_9177c(void)

{
  return dcm_active_service_callback == 0x0u;
}

undefined4 set_matching_dcm_communication_mode_zero_91788(undefined1 param_1)

{
  return set_matching_connection_state_zero_92094(param_1);
}

undefined4 set_matching_dcm_communication_mode_one_91796(undefined1 param_1)

{
  return set_matching_connection_state_one_920a2(param_1);
}

undefined4 set_matching_dcm_communication_mode_two_917a4(undefined1 param_1)

{
  return set_matching_connection_state_two_920b0(param_1);
}

void initialize_dcm_communication_slots_and_enable_917b2(void)

{
  int iVar1;
  uint uVar2;
  
  uVar2 = 0;
  do {
    iVar1 = uVar2 * 2;
    uVar2 = uVar2 + 1;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe564cu + (uint32_t)(iVar1) * 1u)))) = 0;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe564du + (uint32_t)(iVar1) * 1u)))) = 0;
  } while (uVar2 < 2);
  DAT_febe5650 = 1;
  return;
}

void set_dcm_communication_mode_by_connection_id_917d0(char param_1,undefined1 param_2)

{
  uint32_t puVar1;
  undefined *puVar2;
  undefined *puVar3;
  short sVar4;
  uint uVar5;
  
  puVar1 = 0xfebeb800u;
  puVar2 = ((undefined *)camry_host_ptr(0x23dfcu));
  uVar5 = 0;
  do {
    sVar4 = (short)uVar5;
    if (param_1 ==
        (*((char *)camry_host_ptr((uint32_t)((*((volatile int32_t *)camry_host_ptr((uint32_t)((uint)*(ushort *)(puVar2 + sVar4 * 0xc + 0x20ee) * 4 +
                          *(int *)(puVar2 + *(short *)(puVar2 + sVar4 * 0xc + 0x20ec) * 0x14 +
                                            0x20c4))))) + 2))))) {
      puVar3 = puVar2;
      thunk_push_priority_mask_and_raise_to_ff00_6a45e();
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)((uint)*(ushort *)(puVar2 + sVar4 * 0xc + 0x20f2) * 2 + -0x61b4))))) = param_2;
      thunk_pop_and_restore_priority_mask_stack_6a4c4();
      puVar2 = puVar3;
    }
    uVar5 = uVar5 + 1;
  } while (uVar5 < 3);
  return;
}

undefined4 set_dcm_communication_mode_zero_and_return_success_91826(undefined1 param_1)

{
  set_dcm_communication_mode_by_connection_id_917d0(param_1,0);
  return 0;
}

undefined4 set_dcm_communication_mode_one_and_return_success_91838(undefined1 param_1)

{
  set_dcm_communication_mode_by_connection_id_917d0(param_1,1);
  return 0;
}

undefined4 set_dcm_communication_mode_two_and_return_success_9184a(undefined1 param_1)

{
  set_dcm_communication_mode_by_connection_id_917d0(param_1,2);
  return 0;
}

undefined4 is_dcm_route_communication_mode_blocked_9185c(short param_1,char param_2)

{
  ushort uVar1;
  uint32_t puVar2;
  undefined4 uVar3;
  
  puVar2 = 0xfebeb800u;
  uVar3 = 0;
  uVar1 = (*((volatile uint16_t *)camry_host_ptr((uint32_t)((uint32_t)(0x25ee8u + (int32_t)(int16_t)param_1 * (uint32_t)sizeof(F33DcmReceiveRoute)) + (uint32_t)(0) * (uint32_t)sizeof(F33DcmReceiveRoute) + (uint32_t)offsetof(F33DcmReceiveRoute, communication_slot)))));
  thunk_push_priority_mask_and_raise_to_ff00_6a45e();
  if (((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)((uint)uVar1 * 2 + -0x61b4))))) == '\x02') ||
     ((param_2 == '\x01' && ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)((uint)uVar1 * 2 + -0x61b4))))) == '\x01')))) {
    uVar3 = 1;
  }
  thunk_pop_and_restore_priority_mask_stack_6a4c4();
  return uVar3;
}

undefined4 enable_dcm_connection_activity_notifications_91894(char param_1)

{
  short *psVar1;
  undefined8 uVar2;
  int iVar3;
  uint uVar4;
  char *pcVar5;
  
  uVar2 = 0x23dfcfebeb800;
  thunk_push_priority_mask_and_raise_to_ff00_6a45e();
  pcVar5 = ((char *)camry_host_ptr((uint32_t)((int)uVar2 + -0x61b0)));
  *pcVar5 = param_1 == '\x01';
  uVar4 = 0;
  if (*pcVar5 == '\x01') {
    do {
      iVar3 = (int)((ulonglong)uVar2 >> 0x20);
      psVar1 = ((short *)camry_host_ptr((uint32_t)((short)uVar4 * 0xc + iVar3 + 0x20ec)));
      if ((*((char *)camry_host_ptr((uint32_t)((uint)(ushort)psVar1[3] * 2 + (int)uVar2 + -0x61b3)))) == '\x01') {
        set_connection_request_word_01fe_91ac2((*((undefined1 *)camry_host_ptr((uint32_t)((*((volatile int32_t *)camry_host_ptr((uint32_t)((uint)(ushort)psVar1[1] * 4 +
                               (*((volatile int32_t *)camry_host_ptr((uint32_t)(*psVar1 * 0x14 + iVar3 + 0x20c4)))))))) + 2)))));
      }
      uVar4 = uVar4 + 1;
    } while (uVar4 < 3);
  }
  else {
    do {
      iVar3 = (int)((ulonglong)uVar2 >> 0x20);
      psVar1 = ((short *)camry_host_ptr((uint32_t)((short)uVar4 * 0xc + iVar3 + 0x20ec)));
      if ((*((char *)camry_host_ptr((uint32_t)((uint)(ushort)psVar1[3] * 2 + (int)uVar2 + -0x61b3)))) == '\x01') {
        set_connection_request_word_00ff_91ad0((*((undefined1 *)camry_host_ptr((uint32_t)((*((volatile int32_t *)camry_host_ptr((uint32_t)((uint)(ushort)psVar1[1] * 4 +
                               (*((volatile int32_t *)camry_host_ptr((uint32_t)(*psVar1 * 0x14 + iVar3 + 0x20c4)))))))) + 2)))));
      }
      uVar4 = uVar4 + 1;
    } while (uVar4 < 3);
  }
  thunk_pop_and_restore_priority_mask_stack_6a4c4();
  return 0;
}

void update_dcm_connection_activity_requests_91938(short param_1,char param_2)

{
  short *psVar1;
  char cVar2;
  uint32_t puVar3;
  undefined *puVar4;
  undefined *puVar5;
  short sVar6;
  uint uVar7;
  uchar uStack_d;
  
  puVar3 = 0xfebeb800u;
  puVar4 = ((undefined *)camry_host_ptr(0x23dfcu));
  uStack_d = '\0';
  thunk_push_priority_mask_and_raise_to_ff00_6a45e();
  cVar2 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x61b0)))));
  if (param_2 == '\0') {
    if (cVar2 == '\x01') {
      psVar1 = (short *)(puVar4 + param_1 * 0xc + 0x20ec);
      if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)((uint)(ushort)psVar1[3] * 2 + -0x61b3))))) != '\0') goto LAB_00091a1c;
      set_connection_request_word_01fe_91ac2((*((undefined1 *)camry_host_ptr((uint32_t)((*((volatile int32_t *)camry_host_ptr((uint32_t)((uint)(ushort)psVar1[1] * 4 +
                             *(int *)(puVar4 + *psVar1 * 0x14 + 0x20c4))))) + 2)))));
    }
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)((uint)*(ushort *)(puVar4 + param_1 * 0xc + 0x20f2) * 2 + -0x61b3))))) = 1;
  }
  else {
    dcm_get_session(&uStack_d);
    if (uStack_d == '\x01') {
      uVar7 = 0;
      if (cVar2 == '\x01') {
        do {
          sVar6 = (short)uVar7;
          if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)((uint)*(ushort *)(puVar4 + sVar6 * 0xc + 0x20f2) * 2 + -0x61b3))))) == '\x01') {
            puVar5 = puVar4;
            set_connection_request_word_00ff_91ad0((*((undefined1 *)camry_host_ptr((uint32_t)((*((volatile int32_t *)camry_host_ptr((uint32_t)((uint)*(ushort *)(puVar4 + sVar6 * 0xc + 0x20ee) * 4 +
                                   *(int *)(puVar4 + *(short *)(puVar4 + sVar6 * 0xc + 0x20ec) *
                                                     0x14 + 0x20c4))))) + 2)))));
            (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)((uint)*(ushort *)(puVar4 + sVar6 * 0xc + 0x20f2) * 2 + -0x61b3))))) = 0;
            puVar4 = puVar5;
          }
          uVar7 = uVar7 + 1;
        } while (uVar7 < 3);
      }
      else {
        do {
          sVar6 = (short)uVar7;
          uVar7 = uVar7 + 1;
          (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)((uint)*(ushort *)(puVar4 + sVar6 * 0xc + 0x20f2) * 2 + -0x61b3))))) = 0;
        } while (uVar7 < 3);
      }
    }
  }
LAB_00091a1c:
  thunk_pop_and_restore_priority_mask_stack_6a4c4();
  return;
}

void clear_all_dcm_connection_activity_requests_91a24(void)

{
  uint32_t puVar1;
  undefined *puVar2;
  undefined *puVar3;
  short sVar4;
  uint uVar5;
  
  puVar1 = 0xfebeb800u;
  puVar2 = ((undefined *)camry_host_ptr(0x23dfcu));
  thunk_push_priority_mask_and_raise_to_ff00_6a45e();
  uVar5 = 0;
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x61b0))))) == '\x01') {
    do {
      sVar4 = (short)uVar5;
      if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)((uint)*(ushort *)(puVar2 + sVar4 * 0xc + 0x20f2) * 2 + -0x61b3))))) == '\x01') {
        puVar3 = puVar2;
        set_connection_request_word_00ff_91ad0((*((undefined1 *)camry_host_ptr((uint32_t)((*((volatile int32_t *)camry_host_ptr((uint32_t)((uint)*(ushort *)(puVar2 + sVar4 * 0xc + 0x20ee) * 4 +
                               *(int *)(puVar2 + *(short *)(puVar2 + sVar4 * 0xc + 0x20ec) * 0x14 +
                                                 0x20c4))))) + 2)))));
        (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)((uint)*(ushort *)(puVar2 + sVar4 * 0xc + 0x20f2) * 2 + -0x61b3))))) = 0;
        puVar2 = puVar3;
      }
      uVar5 = uVar5 + 1;
    } while (uVar5 < 3);
  }
  else {
    do {
      if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)((uint)*(ushort *)(puVar2 + (short)uVar5 * 0xc + 0x20f2) * 2 + -0x61b3))))) == '\x01') {
        (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)((uint)*(ushort *)(puVar2 + (short)uVar5 * 0xc + 0x20f2) * 2 + -0x61b3))))) = 0;
      }
      uVar5 = uVar5 + 1;
    } while (uVar5 < 3);
  }
  thunk_pop_and_restore_priority_mask_stack_6a4c4();
  return;
}

void rewrite_dcm_communication_enable_byte_unchanged_91ab8(void)

{
  return;
}

void set_connection_request_word_01fe_91ac2(undefined1 param_1)

{
  set_record_492e_token_1fe_7ed16(param_1);
  return;
}

void set_connection_request_word_00ff_91ad0(undefined1 param_1)

{
  set_record_492e_token_ff_7ed2e(param_1);
  return;
}

void return_only_stub_91ade(void)

{
  return;
}

uint dcm_get_security_level(uchar *level)

{
  uint uVar1;
  
  if (camry_host_addr((level))== 0) {
    uVar1 = 0;
  }
  else {
    uVar1 = dcm_read_security_bitmap_level(level);
  }
  return uVar1;
}

uint dcm_get_session(uchar *session)

{
  uint uVar1;
  
  if (camry_host_addr((session))== 0) {
    uVar1 = 0;
  }
  else {
    uVar1 = dcm_read_session_snapshot(session);
  }
  return uVar1;
}

void stage_or_publish_dcm_session_91b08(uchar param_1,uchar param_2)

{
  dcm_stage_or_publish_session(param_1,param_2);
  return;
}

undefined4 dcm_restore_default_session(void)

{
  uint uVar1;
  
  stage_or_publish_dcm_session_91b08(1,0);
  thunk_push_priority_mask_and_raise_to_ff00_6a45e();
  uVar1 = 0;
  do {
    dcm_set_slot_inactivity_participant_93f4e(uVar1,0);
    uVar1 = uVar1 + 1;
  } while (uVar1 < 3);
  dcm_set_request_phase_92610(0);
  thunk_pop_and_restore_priority_mask_stack_6a4c4();
  clear_all_dcm_connection_activity_requests_91a24();
  return return_zero_via_byte_hook_925a0(1);
}

undefined4 restore_default_dcm_session_when_not_busy_91b50(void)

{
  ushort uVar1;
  uint uVar2;
  undefined4 uVar3;
  
  uVar3 = 1;
  uVar2 = dcm_get_request_phase_92624();
  if ((uVar2 < 2) && (uVar1 = dcm_count_receiving_slots(), uVar1 == 0)) {
    dcm_cancel_software_timer('\x05');
    dcm_restore_default_session();
    uVar3 = 0;
  }
  return uVar3;
}

undefined4 restore_default_dcm_session_91b78(void)

{
  return dcm_restore_default_session();
}

bool check_buffered_functional_suppressed_tester_present_91b84(short param_1)

{
  uint8_t stack_record_10[16];
  uchar uVar1;
  
  (*((uint32_t *)(stack_record_10 + 0))) = 0;
  (*((uint16_t *)(stack_record_10 + 4))) = 0;
  uVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)((uint32_t)((uint32_t)(((F33DcmConnection *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(((*((volatile uint32_t *)camry_host_ptr((uint32_t)((uint32_t)(0x25ec0u + (uint32_t)((short)(*((volatile uint16_t *)camry_host_ptr((uint32_t)((uint32_t)(0x25ee8u + (uint32_t)(param_1) * (uint32_t)sizeof(F33DcmReceiveRoute)) + (uint32_t)(0) * (uint32_t)sizeof(F33DcmReceiveRoute) + (uint32_t)offsetof(F33DcmReceiveRoute, protocol_index)))))) * (uint32_t)sizeof(F33DcmProtocolConfiguration)) + (uint32_t)(0) * (uint32_t)sizeof(F33DcmProtocolConfiguration) + (uint32_t)offsetof(F33DcmProtocolConfiguration, connections)))))) + (uint32_t)((*((volatile uint16_t *)camry_host_ptr((uint32_t)((uint32_t)(0x25ee8u + (uint32_t)(param_1) * (uint32_t)sizeof(F33DcmReceiveRoute)) + (uint32_t)(0) * (uint32_t)sizeof(F33DcmReceiveRoute) + (uint32_t)offsetof(F33DcmReceiveRoute, connection_index)))))) * 4u)))))))->receive_rows) + (uint32_t)((*((volatile uint16_t *)camry_host_ptr((uint32_t)((uint32_t)(0x25ee8u + (uint32_t)(param_1) * (uint32_t)sizeof(F33DcmReceiveRoute)) + (uint32_t)(0) * (uint32_t)sizeof(F33DcmReceiveRoute) + (uint32_t)offsetof(F33DcmReceiveRoute, receive_descriptor_index)))))) * (uint32_t)sizeof(F33DcmReceiveDescriptor)) + (uint32_t)(0) * (uint32_t)sizeof(F33DcmReceiveDescriptor) + (uint32_t)offsetof(F33DcmReceiveDescriptor, addressing_kind)))));
  dcm_rewind_receive_cursor_and_get_received_pdu_93c6c(param_1,stack_record_10);
  return is_functional_suppressed_tester_present_916c6(uVar1,stack_record_10);
}

undefined4 read_dcm_state_byte_if_output_nonnull_91bd2(int param_1)

{
  undefined4 uVar1;
  
  if (param_1 == 0) {
    uVar1 = 0;
  }
  else {
    uVar1 = dcm_get_cached_protocol_byte_93a70(((undefined1 *)camry_host_ptr((uint32_t)(param_1))));
  }
  return uVar1;
}

ushort thunk_dcm_get_current_dispatch_receive_slot_93c60(void)

{
  return dcm_get_current_dispatch_receive_slot_93c60();
}

undefined4 get_dcm_pending_transport_accepted_guarded_91bf2(void)

{
  undefined4 uVar1;
  
  thunk_push_priority_mask_and_raise_to_ff00_6a45e();
  uVar1 = dcm_get_pending_transport_accepted_93c8e();
  thunk_pop_and_restore_priority_mask_stack_6a4c4();
  return uVar1;
}

void dcm_dispatch_retained_receive(ushort receive_slot)

{
  F33DcmRequestRoute local_1c;
  F33PduInfo FStack_18;
  F33PduInfo FStack_10;
  
  FStack_18.length = 0;
  FStack_18.data = 0;
  FStack_10.length = 0;
  FStack_10.data = 0;
  local_1c.addressing_kind =
       (*((volatile uint8_t *)camry_host_ptr((uint32_t)((uint32_t)((uint32_t)(((F33DcmConnection *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(((*((volatile uint32_t *)camry_host_ptr((uint32_t)((uint32_t)(0x25ec0u + (uint32_t)((short)(*((volatile uint16_t *)camry_host_ptr((uint32_t)((uint32_t)(0x25ee8u + (uint32_t)((short)receive_slot) * (uint32_t)sizeof(F33DcmReceiveRoute)) + (uint32_t)(0) * (uint32_t)sizeof(F33DcmReceiveRoute) + (uint32_t)offsetof(F33DcmReceiveRoute, protocol_index)))))) * (uint32_t)sizeof(F33DcmProtocolConfiguration)) + (uint32_t)(0) * (uint32_t)sizeof(F33DcmProtocolConfiguration) + (uint32_t)offsetof(F33DcmProtocolConfiguration, connections)))))) + (uint32_t)((*((volatile uint16_t *)camry_host_ptr((uint32_t)((uint32_t)(0x25ee8u + (uint32_t)((short)receive_slot) * (uint32_t)sizeof(F33DcmReceiveRoute)) + (uint32_t)(0) * (uint32_t)sizeof(F33DcmReceiveRoute) + (uint32_t)offsetof(F33DcmReceiveRoute, connection_index)))))) * 4u)))))))->receive_rows) + (uint32_t)((*((volatile uint16_t *)camry_host_ptr((uint32_t)((uint32_t)(0x25ee8u + (uint32_t)((short)receive_slot) * (uint32_t)sizeof(F33DcmReceiveRoute)) + (uint32_t)(0) * (uint32_t)sizeof(F33DcmReceiveRoute) + (uint32_t)offsetof(F33DcmReceiveRoute, receive_descriptor_index)))))) * (uint32_t)sizeof(F33DcmReceiveDescriptor)) + (uint32_t)(0) * (uint32_t)sizeof(F33DcmReceiveDescriptor) + (uint32_t)offsetof(F33DcmReceiveDescriptor, addressing_kind)))));
  local_1c.service_list_selector = (*((volatile uint16_t *)camry_host_ptr((uint32_t)((uint32_t)(0x25ee8u + (uint32_t)((short)receive_slot) * (uint32_t)sizeof(F33DcmReceiveRoute)) + (uint32_t)(0) * (uint32_t)sizeof(F33DcmReceiveRoute) + (uint32_t)offsetof(F33DcmReceiveRoute, receive_id)))));
  thunk_push_priority_mask_and_raise_to_ff00_6a45e();
  dcm_rewind_receive_cursor_and_get_received_pdu_93c6c(receive_slot,&FStack_10);
  thunk_pop_and_restore_priority_mask_stack_6a4c4();
  dcm_get_shared_response_buffer_and_connection_limit_93ce6(&FStack_18);
  dcm_begin_service_request(&local_1c,&FStack_10,&FStack_18);
  return;
}

uint deliver_dcm_response_notification_91c82(uchar param_1,uchar param_2)

{
  return dcm_deliver_response_notification(param_1,param_2);
}

uint dcm_run_queued_response_notification(void)

{
  uint8_t stack_record_6[8];
  int iVar1;
  
  stack_record_6[0] = '\0';
  stack_record_6[1] = '\0';
  dcm_snapshot_response_notification(((uint8_t *)(stack_record_6)),((uint8_t *)((stack_record_6 + 1))));
  if (stack_record_6[1] != '\x01') {
    dcm_clear_response_notification_and_state_92a9c();
    iVar1 = dcm_get_request_phase_92624();
    if (iVar1 == 2) {
      dcm_activate_idle_response_queue_92b4a();
    }
  }
  dcm_finish_staged_session_notifications();
  return dcm_deliver_response_notification(stack_record_6[0],stack_record_6[1]);
}

void build_dcm_final_negative_response_bytes_91cd2(undefined1 param_1,undefined1 param_2)

{
  dcm_format_final_negative_response_93162(param_1,param_2);
  return;
}

void dcm_stage_final_response(F33DcmMessageContext *message,uchar disposition)

{
  int iVar1;
  F33PduInfo local_14;
  
  local_14.data = 0;
  local_14.length = 0;
  iVar1 = dcm_get_request_phase_92624();
  if (iVar1 == 2) {
    dcm_get_shared_response_buffer_and_connection_limit_93ce6(&local_14);
    local_14.length = (ushort)message->response_length;
    dcm_enqueue_final_disposition(&local_14,disposition);
  }
  return;
}

void thunk_dcm_request_response_stop_and_save_displaced_id_935b6(void)

{
  dcm_request_response_stop_and_save_displaced_id_935b6();
  return;
}

void handle_dcm_overall_timeout_with_general_reject_91d20(void)

{
  uint8_t stack_record_10[16];
  uchar service_id;
  int iVar1;
  undefined4 uVar2;
  
  (*((uint32_t *)(stack_record_10 + 0))) = 0;
  (*((uint16_t *)(stack_record_10 + 4))) = 0;
  iVar1 = dcm_get_request_phase_92624();
  if (iVar1 == 2) {
    thunk_push_priority_mask_and_raise_to_ff00_6a45e();
    iVar1 = dcm_get_selected_zero_timeout_flag_940e6(1);
    if (iVar1 == 1) {
      uVar2 = dcm_get_pending_dispatch_receive_slot_9400e();
      dcm_rewind_receive_cursor_and_get_received_pdu_93c6c(uVar2,((uint32_t *)(stack_record_10)));
      service_id = get_first_request_byte_91694(((undefined1 *)camry_host_ptr((uint32_t)((*((uint32_t *)(stack_record_10 + 0)))))));
      dcm_set_selected_zero_timeout_flag_940d0(0,1);
    }
    else {
      service_id = get_dcm_current_service_id_9168e();
    }
    iVar1 = dcm_response_state_allows_completion_notification_92d72();
    if (iVar1 != 1) {
      dcm_cancel_active_service();
    }
    thunk_pop_and_restore_priority_mask_stack_6a4c4();
    dcm_enqueue_general_reject(service_id);
  }
  return;
}

void handle_dcm_p2_deadline_for_active_request_91d80(void)

{
  uint8_t stack_record_14[20];
  uchar service_id;
  int iVar1;
  undefined4 uVar2;
  
  (*((uint32_t *)(stack_record_14 + 0))) = 0;
  (*((uint16_t *)(stack_record_14 + 4))) = 0;
  iVar1 = dcm_get_request_phase_92624();
  if (iVar1 == 2) {
    thunk_push_priority_mask_and_raise_to_ff00_6a45e();
    iVar1 = dcm_get_pending_transport_accepted_93c8e();
    if ((iVar1 == 0) && (iVar1 = dcm_get_selected_zero_timeout_flag_940e6(0), iVar1 == 1)) {
      uVar2 = dcm_get_pending_dispatch_receive_slot_9400e();
      dcm_rewind_receive_cursor_and_get_received_pdu_93c6c(uVar2,((uint32_t *)(stack_record_14)));
      service_id = get_first_request_byte_91694(((undefined1 *)camry_host_ptr((uint32_t)((*((uint32_t *)(stack_record_14 + 0)))))));
      dcm_set_current_dispatch_receive_slot_93c66(uVar2);
      dcm_set_selected_zero_timeout_flag_940d0(0,0);
    }
    else {
      service_id = get_dcm_current_service_id_9168e();
    }
    thunk_pop_and_restore_priority_mask_stack_6a4c4();
    dcm_p2_response_deadline(service_id);
  }
  return;
}

void advance_dcm_pending_response_in_phase_two_91de4(void)

{
  int iVar1;
  
  iVar1 = dcm_get_request_phase_92624();
  if (iVar1 == 2) {
    dcm_send_pending_response_or_leave_wait_state_93230();
  }
  return;
}

void request_dcm_explicit_pending_response_in_phase_two_91df8(uchar param_1)

{
  int iVar1;
  
  iVar1 = dcm_get_request_phase_92624();
  if (iVar1 == 2) {
    dcm_request_explicit_pending_response(param_1);
  }
  return;
}

void publish_dcm_security_level_91e12(uchar param_1)

{
  dcm_publish_security_level(param_1);
  return;
}

undefined1 thunk_dcm_get_current_receive_descriptor_flag_nine_93d9a(void)

{
  return dcm_get_current_receive_descriptor_flag_nine_93d9a();
}

bool is_dcm_phase_zero_without_receiving_slots_91e2c(void)

{
  ushort uVar1;
  int iVar2;
  bool bVar3;
  
  thunk_push_priority_mask_and_raise_to_ff00_6a45e();
  bVar3 = false;
  iVar2 = dcm_get_request_phase_92624();
  if (iVar2 == 0) {
    uVar1 = dcm_count_receiving_slots();
    bVar3 = uVar1 == 0;
  }
  thunk_pop_and_restore_priority_mask_stack_6a4c4();
  return bVar3;
}

bool is_dcm_request_phase_zero_91e52(void)

{
  int iVar1;
  
  thunk_push_priority_mask_and_raise_to_ff00_6a45e();
  iVar1 = dcm_get_request_phase_92624();
  thunk_pop_and_restore_priority_mask_stack_6a4c4();
  return iVar1 == 0;
}

void cancel_dcm_active_service_91e6e(void)

{
  dcm_cancel_active_service();
  return;
}

undefined4 publish_default_session_and_clear_inactivity_participants_91e7a(void)

{
  uint uVar1;
  
  stage_or_publish_dcm_session_91b08(1,0);
  thunk_push_priority_mask_and_raise_to_ff00_6a45e();
  uVar1 = 0;
  do {
    dcm_set_slot_inactivity_participant_93f4e(uVar1,0);
    uVar1 = uVar1 + 1;
  } while (uVar1 < 3);
  thunk_pop_and_restore_priority_mask_stack_6a4c4();
  return return_zero_via_byte_hook_925a0(1);
}

uint32_t dcm_restart_inactivity_after_request(void)

{
  uint32_t camry_r10_result;
  bool bVar1;
  undefined4 uVar2;
  uint uVar3;
  uchar uStack_9;
  
  uStack_9 = '\x01';
  uVar2 = (camry_r10_result = dcm_get_current_dispatch_receive_slot_93c60());
  (camry_r10_result = dcm_read_session_snapshot(&uStack_9));
  bVar1 = uStack_9 != '\x01';
  if (bVar1) {
    uVar3 = (camry_r10_result = dcm_get_current_protocol_inactivity_timeout_93b18());
    dcm_arm_software_timer('\x05',uVar3);
    thunk_push_priority_mask_and_raise_to_ff00_6a45e();
  }
  else {
    thunk_push_priority_mask_and_raise_to_ff00_6a45e();
  }
  dcm_set_request_phase_92610(bVar1);
  thunk_pop_and_restore_priority_mask_stack_6a4c4();
  thunk_push_priority_mask_and_raise_to_ff00_6a45e();
  dcm_reset_receive_slot_and_optionally_shared_response_93c9a(uVar2,0);
  uVar3 = 0;
  do {
    dcm_set_slot_inactivity_participant_93f4e(uVar3,0);
    uVar3 = uVar3 + 1;
  } while (uVar3 < 3);
  thunk_pop_and_restore_priority_mask_stack_6a4c4();
  return camry_r10_result;
}

void cancel_service_and_cleanup_dcm_response_state_91f0e(void)

{
  int iVar1;
  
  iVar1 = dcm_response_state_allows_completion_notification_92d72();
  if (iVar1 != 1) {
    dcm_cancel_active_service();
  }
  dcm_finish_stop_event_by_response_state_9338e();
  return;
}

uint32_t arm_dcm_inactivity_timer_if_no_other_participant_91f26(uint param_1,char param_2)

{
  uint32_t camry_r10_result;
  int iVar1;
  uint uVar2;
  
  iVar1 = (camry_r10_result = dcm_get_request_phase_92624());
  if (iVar1 == 1) {
    uVar2 = 0;
    do {
      iVar1 = (camry_r10_result = dcm_get_slot_inactivity_participant_93f5a(uVar2));
      if ((iVar1 == 1) && (uVar2 != (param_1 & 0xffff))) {
        return camry_r10_result;
      }
      uVar2 = uVar2 + 1;
    } while (uVar2 < 3);
    if (param_2 == '\x01') {
      uVar2 = (camry_r10_result = dcm_get_current_protocol_inactivity_timeout_93b18());
      dcm_arm_software_timer('\x05',uVar2);
    }
  }
  return camry_r10_result;
}

void commit_or_discard_dcm_staged_session_91f64(uchar param_1)

{
  dcm_commit_or_discard_staged_session(param_1);
  return;
}

uint32_t set_dcm_phase_and_prepare_response_queue_when_not_active_91f72(undefined1 param_1)

{
  uint32_t camry_r10_result;
  uint uVar1;
  
  uVar1 = (camry_r10_result = dcm_get_request_phase_92624());
  if (uVar1 < 2) {
    dcm_set_request_phase_92610(param_1);
    (camry_r10_result = dcm_activate_idle_response_queue_92b4a());
  }
  return camry_r10_result;
}

void dcm_finish_staged_session_notifications_wrapper_91f90(void)

{
  dcm_finish_staged_session_notifications();
  return;
}

undefined4 return_zero_via_session_byte_hook_91f9c(undefined1 param_1)

{
  return return_zero_via_byte_hook_925a0(param_1);
}

uint32_t dcm_reset_current_receive_slot_and_shared_response_91faa(void)

{
  uint32_t camry_r10_result;
  undefined4 uVar1;
  
  uVar1 = (camry_r10_result = dcm_get_current_dispatch_receive_slot_93c60());
  dcm_reset_receive_slot_and_optionally_shared_response_93c9a(uVar1,0);
  return camry_r10_result;
}

undefined4 dcm_rewrite_dispatch_context_under_lock_91fbe(void)

{
  undefined4 uVar1;
  undefined4 uVar2;
  undefined4 uVar3;
  
  thunk_push_priority_mask_and_raise_to_ff00_6a45e();
  uVar1 = dcm_get_request_phase_92624();
  uVar2 = dcm_get_current_dispatch_receive_slot_93c60();
  uVar3 = dcm_get_pending_dispatch_receive_slot_9400e();
  dcm_set_request_phase_92610(uVar1);
  dcm_set_current_dispatch_receive_slot_93c66(uVar2);
  dcm_set_pending_dispatch_receive_slot_94008(uVar3);
  dcm_rewrite_current_session_byte_92602();
  rewrite_dcm_communication_enable_byte_unchanged_91ab8();
  thunk_pop_and_restore_priority_mask_stack_6a4c4();
  return uVar3;
}

void run_init_chain_91ffa(void)

{
  return_only_stub_9262a();
  return_only_stub_922e8();
  initialize_dcm_communication_slots_and_enable_917b2();
  dcm_initialize_session_snapshot_to_default_924e8();
  clear_two_locked_state_words_923ec();
  dcm_clear_request_phase_92616();
  dcm_reset_response_state_and_queue_92b24();
  dcm_invalidate_cached_protocol_byte_93ab2();
  dcm_initialize_receive_buffers_and_transport_state_93aba();
  return_only_stub_91ade();
  return;
}
