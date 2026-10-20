#include "common.h"

uint dcm_preflight_read_did_body(uchar operation)

{
  ushort uVar1;
  uint32_t puVar2;
  int iVar3;
  undefined8 uVar4;
  int iVar5;
  uint uVar6;
  ushort uVar7;
  
  uVar1 = dcm_read_did_count;
  uVar4 = 0xfebeb800;
  uVar6 = 0;
  uVar7 = dcm_read_did_cursor;
  do {
    iVar3 = (int)uVar4;
    if (uVar1 <= uVar7) {
LAB_000961a2:
      if (uVar7 == uVar1) {
        puVar2 = ((uint32_t)((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)((iVar3 + -0x5a68))))))));
        if (0xfffdu < puVar2) {
          puVar2 = 0xfffe;
        }
        if (puVar2 <((uint32_t)((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)((iVar3 + -0x5a8c))))))))) {
          dcm_report_negative_or_pending(((F33DcmMessageContext *)camry_host_ptr((uint32_t)(iVar3 + -0x5a7c))),'\x14');
        }
        else {
          (*((undefined2 *)camry_host_ptr((uint32_t)(iVar3 + -0x5a82)))) = 0;
          uVar6 = dcm_serialize_read_did_body('\0');
        }
      }
      return uVar6;
    }
    (*((ushort *)camry_host_ptr((uint32_t)(iVar3 + -0x5a84)))) =
         CONCAT11((*((undefined1 *)camry_host_ptr((uint32_t)((uint)(ushort)(uVar7 * 2) + (*((volatile int32_t *)camry_host_ptr((uint32_t)(iVar3 + -0x5a7c)))))))),
                  (*((undefined1 *)camry_host_ptr((uint32_t)((uint)(ushort)(uVar7 * 2 + 1) + (*((volatile int32_t *)camry_host_ptr((uint32_t)(iVar3 + -0x5a7c)))))))));
    if (operation == '\x01') {
      iVar5 = check_read_did_condition_or_queue_pending_95e76(operation);
    }
    else if (operation == '\x02') {
      iVar5 = accumulate_read_did_length_or_queue_pending_95d60(1);
    }
    else {
      iVar5 = resolve_read_did_route_then_check_policy_95f78();
    }
    iVar3 = (int)uVar4;
    if (iVar5 != 0) {
      if (iVar5 == 10) {
        (*((ushort *)camry_host_ptr((uint32_t)(iVar3 + -0x5a82)))) = uVar7;
        uVar6 = 10;
      }
      goto LAB_000961a2;
    }
    uVar7 = uVar7 + 1;
    operation = '\0';
  } while( true );
}

uint dcm_begin_read_did_request(F33DcmMessageContext *message)

{
  uchar **ppuVar1;
  undefined4 *puVar2;
  uint uVar3;
  uint32_t puVar4;
  F33DcmMessageContext *pFVar5;
  uint uVar6;
  
  puVar4 = 0xfebeb800u;
  uVar6 = 0;
  set_diagnostic_busy_marker_from_done_flag_9560e(0);
  puVar2 = ((undefined4 *)camry_host_ptr((uint32_t)(puVar4 + -0x5a7c)));
  pFVar5 = message + 1;
  do {
    ppuVar1 = &message->request;
    message = (F33DcmMessageContext *)&message->request_length;
    *puVar2 = *(uint32_t *)ppuVar1;
    puVar2 = puVar2 + 1;
  } while (camry_host_addr(pFVar5)!=camry_host_addr(message));
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar4 + -0x5a82)))) = 0;
  (*((undefined4 *)camry_host_ptr((uint32_t)(puVar4 + -0x5a8c)))) = 0;
  set_diagnostic_callback_pending_955b6(0);
  uVar3 = (*((uint *)camry_host_ptr((uint32_t)(puVar4 + -0x5a78))));
  if (((uVar3 < 2) || ((uVar3 & 1) != 0)) || (1 < uVar3 >> 1)) {
    dcm_report_negative_or_pending(((F33DcmMessageContext *)camry_host_ptr((uint32_t)(puVar4 + -0x5a7c))),'\x13');
  }
  else {
    (*((short *)camry_host_ptr((uint32_t)(puVar4 + -0x5a80)))) = (short)(uVar3 >> 1);
    uVar6 = dcm_preflight_read_did_body('\0');
  }
  return uVar6;
}

undefined4 cancel_read_did_callbacks_and_events_96244(void)

{
  uint8_t stack_record_16[22];
  undefined2 uVar1;
  ushort uVar2;
  uchar *puVar3;
  uint32_t puVar4;
  int iVar5;
  
  puVar3 = ((void *)camry_host_ptr((uint32_t)(dcm_read_message.response)));
  uVar2 = dcm_read_current_did;
  puVar4 = 0xfebeb800u;
  (*((uint16_t *)(stack_record_16 + 4))) = 0;
  stack_record_16[1] = 0;
  (*((uint16_t *)(stack_record_16 + 2))) = 0;
  stack_record_16[0] = 1;
  iVar5 = get_diagnostic_callback_pending_955bc();
  if (iVar5 == 1) {
    uVar1 = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar4 + -0x5a88))));
    if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x5a86))))) == '\x01') {
      dcm_dispatch_did_presence_probe_9445a(uVar1,uVar2,2,stack_record_16);
      dcm_dispatch_did_length_callback_9449e(uVar1,uVar2,2,(stack_record_16 + 2));
      dcm_dispatch_did_read_callback_94526(uVar1,uVar2,puVar3,2,(stack_record_16 + 2),(stack_record_16 + 1));
      dcm_invalidate_queued_event('\x04','\0');
      dcm_invalidate_queued_event('\x1f','\0');
    }
    else {
      dcm_read_dynamic_did_with_pending_cancellation_946c6(uVar1, camry_host_addr(puVar3), 2, (stack_record_16 + 2), (stack_record_16 + 1), camry_host_addr((stack_record_16 + 4)));
    }
    dcm_invalidate_queued_event('\x05','\0');
    set_diagnostic_callback_pending_955b6(0);
  }
  dcm_invalidate_queued_event('$','\0');
  set_diagnostic_busy_marker_from_done_flag_9560e(1);
  return 0;
}

uint dcm_read_did_service(uchar operation,F33DcmMessageContext *message)

{
  uint uVar1;
  
  if (operation == '\0') {
    uVar1 = dcm_begin_read_did_request(message);
  }
  else {
    uVar1 = 0;
    if (operation == '\x02') {
      uVar1 = cancel_read_did_callbacks_and_events_96244();
    }
  }
  return uVar1;
}

uint resume_read_did_preflight_stage_one_96312(void)

{
  return dcm_preflight_read_did_body('\x01');
}

uint serialize_read_did_for_noncontinuation_event_96320(char param_1)

{
  return dcm_serialize_read_did_body(param_1 != '$');
}

uint resume_read_did_preflight_stage_two_96336(void)

{
  return dcm_preflight_read_did_body('\x02');
}

bool decode_memory_size_and_reject_zero_or_overflow_96344(uint param_1,uint param_2)

{
  uint uVar1;
  
  for (uVar1 = 0; uVar1 < (param_2 & 0xff); uVar1 = uVar1 + 1 & 0xff) {
    DAT_febe5da4 = (uint)(*((byte *)camry_host_ptr((uint32_t)(uVar1 + (param_1 & 0xff) + DAT_febe5dac + 1)))) +
                   DAT_febe5da4 * 0x100;
  }
  return DAT_febe5da4 == 0 || (uint)(DAT_febe5dc0 - DAT_febe5db8) < DAT_febe5da4;
}

undefined4 decode_and_validate_memory_read_address_96388(uint param_1)

{
  uint uVar1;
  uint32_t puVar2;
  undefined4 uVar3;
  int iVar4;
  undefined4 uVar5;
  
  puVar2 = 0xfebeb800u;
  uVar5 = 1;
  if (DAT_00026154 == '\x01') {
    uVar3 = 0;
    DAT_febe5da8 = (*((undefined1 *)camry_host_ptr((uint32_t)(DAT_febe5dac + 1))));
    uVar1 = 1;
  }
  else {
    uVar1 = 0;
    uVar3 = 1;
  }
  for (; uVar1 < (param_1 & 0xff); uVar1 = uVar1 + 1 & 0xff) {
    DAT_febe5da0 = (uint)(*((byte *)camry_host_ptr((uint32_t)(DAT_febe5dac + uVar1 + 1)))) + DAT_febe5da0 * 0x100;
  }
  iVar4 = resolve_configured_address_range_by_mode_and_identifier_94be2(0,DAT_febe5da0,uVar3,DAT_febe5da8,((undefined *)camry_host_ptr(0xfebe5da9u)),((undefined *)camry_host_ptr(0xfebe5daau)));
  if (iVar4 == 0) {
    iVar4 = is_requested_range_past_configured_end_94cc4(0,(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x5a57))))),(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x5a56))))),(*((undefined4 *)camry_host_ptr((uint32_t)(puVar2 + -0x5a60)))),
                         (*((undefined4 *)camry_host_ptr((uint32_t)(puVar2 + -0x5a5c)))));
    if (iVar4 == 0) {
      uVar5 = 0;
    }
    else {
      uVar5 = 1;
    }
  }
  return uVar5;
}

undefined4 execute_memory_read_and_report_result_96410(byte param_1)

{
  uint32_t puVar1;
  undefined4 uVar2;
  uchar nrc;
  uchar uStack_d;
  
  puVar1 = 0xfebeb800u;
  uStack_d = '\0';
  if ((1 < param_1) && (param_1 != 3)) {
    return 0;
  }
  uVar2 = dispatch_memory_read_or_reset_965fc(param_1, DAT_febe5da8, DAT_febe5da0, DAT_febe5da4, DAT_febe5db8 + DAT_febe5db4, camry_host_addr(&uStack_d));
  nrc = uStack_d;
  switch(uVar2) {
  case 0:
    (*((int *)camry_host_ptr((uint32_t)(puVar1 + -0x5a48)))) = (*((int *)camry_host_ptr((uint32_t)(puVar1 + -0x5a48)))) + (*((int *)camry_host_ptr((uint32_t)(puVar1 + -0x5a5c))));
    dcm_report_positive_response(((F33DcmMessageContext *)camry_host_ptr((uint32_t)(puVar1 + -0x5a54))));
  default:
    set_diagnostic_callback_pending_955b6(0);
    return 0;
  case 1:
    dcm_enqueue_event('#');
    set_diagnostic_callback_pending_955b6(1);
    return 10;
  case 2:
    set_diagnostic_callback_pending_955b6(0);
    if (nrc == '\0') {
      return 0;
    }
    break;
  case 3:
    nrc = 'x';
    set_diagnostic_callback_pending_955b6(1);
  }
  dcm_report_negative_or_pending(((F33DcmMessageContext *)camry_host_ptr((uint32_t)(puVar1 + -0x5a54))),nrc);
  return 0;
}

undefined4 begin_read_memory_by_address_request_964b0(undefined4 *param_1)

{
  undefined4 *puVar1;
  uint32_t puVar2;
  uchar nrc;
  int iVar3;
  undefined4 uVar4;
  uint uVar5;
  undefined4 *puVar6;
  uchar uStack_11;
  
  puVar2 = 0xfebeb800u;
  uStack_11 = '\0';
  set_diagnostic_busy_marker_from_done_flag_9560e(0x0);
  puVar1 = ((undefined4 *)camry_host_ptr((uint32_t)(puVar2 + -0x5a54)));
  puVar6 = param_1;
  do {
    uVar4 = *puVar6;
    puVar6 = puVar6 + 1;
    *puVar1 = uVar4;
    puVar1 = puVar1 + 1;
  } while (camry_host_addr(param_1 + 7)!=camry_host_addr(puVar6));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x5a58))))) = 0;
  (*((undefined4 *)camry_host_ptr((uint32_t)(puVar2 + -0x5a60)))) = 0;
  (*((undefined4 *)camry_host_ptr((uint32_t)(puVar2 + -0x5a5c)))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x5a57))))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x5a56))))) = 0;
  set_diagnostic_callback_pending_955b6(0);
  if ((uint)param_1[1] < 3) {
LAB_00096570:
    nrc = '\x13';
  }
  else {
    iVar3 = check_configured_range_byte_allowlist_94ba8((*((volatile undefined1 *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)((puVar2 + -0x5a54))))))))));
    if (iVar3 == 0) {
      uVar5 = (*((byte *)camry_host_ptr((uint32_t)(*param_1 ))))& 0xf;
      iVar3 = (int)(uint)(*((byte *)camry_host_ptr((uint32_t)(*param_1 ))))>> 4;
      if (param_1[1] != iVar3 + uVar5 + 1) goto LAB_00096570;
      iVar3 = decode_memory_size_and_reject_zero_or_overflow_96344(uVar5,iVar3);
      if ((iVar3 == 0) && (iVar3 = decode_and_validate_memory_read_address_96388(uVar5), iVar3 == 0)) {
        dcm_get_security_level(&uStack_11);
        iVar3 = check_selected_range_byte_allowlist_94d04(0,(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x5a57))))),(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x5a56))))),uStack_11);
        if (iVar3 == 0) {
          iVar3 = execute_memory_read_and_report_result_96410(0);
          if (iVar3 == 0) {
            return 0;
          }
          return 10;
        }
        nrc = '3';
        goto LAB_00096574;
      }
    }
    nrc = '1';
  }
LAB_00096574:
  dcm_report_negative_or_pending(((F33DcmMessageContext *)camry_host_ptr((uint32_t)(puVar2 + -0x5a54))),nrc);
  return 0;
}

void cancel_memory_read_and_clear_event_96582(void)

{
  uint32_t puVar1;
  int iVar2;
  
  puVar1 = 0xfebeb800u;
  iVar2 = get_diagnostic_callback_pending_955bc();
  if (iVar2 == 1) {
    dispatch_memory_read_or_reset_965fc(2,(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x5a58))))),(*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + -0x5a60)))),
                 (*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + -0x5a5c)))),0,0);
    set_diagnostic_callback_pending_955b6(0);
  }
  dcm_invalidate_queued_event('#','\0');
  set_diagnostic_busy_marker_from_done_flag_9560e(1);
  return;
}

uint dcm_read_memory_service(uchar operation,F33DcmMessageContext *message)

{
  uint uVar1;
  
  if (operation == '\0') {
    uVar1 = begin_read_memory_by_address_request_964b0(message);
  }
  else {
    uVar1 = 0;
    if (operation == '\x02') {
      cancel_memory_read_and_clear_event_96582();
    }
    else if (operation == '\x03') {
      uVar1 = execute_memory_read_and_report_result_96410((uint)(byte)operation);
    }
  }
  return uVar1;
}

undefined4 resume_memory_read_965ee(void)

{
  return execute_memory_read_and_report_result_96410(1);
}

undefined4
dispatch_memory_read_or_reset_965fc(char param_1,undefined1 param_2,undefined4 param_3,undefined4 param_4,
            undefined4 param_5,undefined4 param_6)

{
  undefined4 uVar1;
  
  if (param_1 == '\x02') {
    thunk_reset_memory_read_status4598_8d4ae();
    uVar1 = 0;
  }
  else {
    uVar1 = dispatch_memory_read_by_selector_nibble_8d546(param_1, param_2, param_3, param_4, ((uchar *)camry_host_ptr((uint32_t)(param_5))), ((undefined1 *)camry_host_ptr((uint32_t)(param_6))));
  }
  return uVar1;
}

void set_or_clear_security_delay_bit_96622(uint param_1,char param_2)

{
  uint uVar1;
  
  if ((param_1 & 0xff) < 2) {
    uVar1 = 1 << (param_1 & 0x1f);
    if (param_2 == '\x01') {
      app_security_delay_bits = app_security_delay_bits | uVar1;
    }
    else {
      app_security_delay_bits = app_security_delay_bits & ~uVar1;
    }
  }
  return;
}

void dcm_security_initialize_delays(void)

{
  uint32_t puVar1;
  uint32_t puVar2;
  uint uVar3;
  int iVar4;
  
  puVar1 = 0xfebeb800u;
  puVar2 = 0x23dfcu;
  app_security_delay_bits = 0;
  uVar3 = 0;
  do {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(uVar3 - 0x5a31))))) = 0;
    iVar4 = (short)uVar3 * 0x18;
    if ((*((int *)camry_host_ptr((uint32_t)(puVar2 + iVar4 + 0x2370)))) != 0) {
      dcm_arm_software_timer((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(uVar3 * 2 + 0x235d))))),(*((uint *)camry_host_ptr((uint32_t)(puVar2 + iVar4 + 0x2370)))));
      set_or_clear_security_delay_bit_96622(uVar3,1);
    }
    uVar3 = uVar3 + 1;
  } while (uVar3 < 2);
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x5a33))))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x5a32))))) = 0;
  return;
}

uint dcm_security_seed_callback_join(uchar level,uchar operation)

{
  uint8_t stack_record_12[20];
  uint uVar1;
  uint32_t puVar2;
  uint32_t puVar3;
  uchar uVar4;
  int iVar5;
  uint uVar6;
  
  uVar4 = app_security_selected_row;
  puVar2 = 0xfebeb800u;
  puVar3 = 0x23dfcu;
  uVar6 = (uint)app_security_selected_row;
  stack_record_12[0] = '\0';
  if (uVar6 < 2) {
    stack_record_12[1] = '\0';
    iVar5 = dispatch_security_seed_by_callback_kind_96b98(level, app_dcm_security_message.request, operation, 
                         app_dcm_security_message.response, camry_host_addr(((uint8_t *)((stack_record_12 + 1)))));
    if (iVar5 == 0) {
      set_diagnostic_callback_pending_955b6(0);
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x5a32))))) = 1;
      if (((*((uint *)camry_host_ptr((uint32_t)(puVar2 + -0x5a38)))) & 1 << (uVar6 & 0x1f)) == 0) {
        dcm_get_security_level(((uint8_t *)(stack_record_12)));
        uVar6 = (*((uint *)camry_host_ptr((uint32_t)(puVar3 + (short)(ushort)uVar4 * 0x18 + 0x2378))));
        if (level == stack_record_12[0]) {
          for (uVar1 = 0; uVar1 < uVar6; uVar1 = uVar1 + 1) {
            (*((undefined1 *)camry_host_ptr((uint32_t)((*((volatile int32_t *)camry_host_ptr((uint32_t)(puVar2 + -0x5a24)))) + uVar1)))) = 0;
          }
          level = '\0';
        }
        (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x5a33))))) = level;
        (*((uint *)camry_host_ptr((uint32_t)(puVar2 + -0x5a20)))) = uVar6;
        dcm_report_positive_response(((F33DcmMessageContext *)camry_host_ptr((uint32_t)(puVar2 + -0x5a2c))));
        return 0;
      }
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x5a33))))) = 0;
      uVar4 = '7';
    }
    else {
      if (iVar5 != 1) {
        if (iVar5 != 10) {
          set_diagnostic_callback_pending_955b6(0);
          (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x5a33))))) = 0;
          return 0;
        }
        set_diagnostic_callback_pending_955b6(1);
        dcm_enqueue_event('\x0f');
        return 10;
      }
      set_diagnostic_callback_pending_955b6(0);
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x5a33))))) = 0;
      uVar4 = stack_record_12[1];
    }
    dcm_report_negative_or_pending(((F33DcmMessageContext *)camry_host_ptr((uint32_t)(puVar2 + -0x5a2c))),uVar4);
  }
  return 0;
}

void resume_selected_security_seed_callback_96768(void)

{
  if (app_security_selected_row < 2) {
    dcm_security_seed_callback_join
              ((*((volatile uint8_t *)camry_host_ptr((uint32_t)((uint32_t)(0x26164u + (uint32_t)((short)(ushort)app_security_selected_row) * (uint32_t)sizeof(F33DcmSecurityLevelConfig)) + (uint32_t)(0) * (uint32_t)sizeof(F33DcmSecurityLevelConfig) + (uint32_t)offsetof(F33DcmSecurityLevelConfig, security_level))))),'\x01');
  }
  return;
}

uint dcm_security_key_callback_join(uchar level,uchar operation)

{
  byte bVar1;
  byte bVar2;
  uint32_t puVar3;
  uint32_t puVar4;
  F33DcmMessageContext *message;
  uchar uVar5;
  int iVar6;
  uint uVar7;
  uchar uStack_11;
  
  uVar5 = app_security_selected_row;
  puVar3 = 0xfebeb800u;
  puVar4 = 0x23dfcu;
  uVar7 = (uint)app_security_selected_row;
  if (uVar7 < 2) {
    uStack_11 = '\0';
    iVar6 = dispatch_security_key_by_callback_kind_96bce(level, app_dcm_security_message.request, operation, camry_host_addr(&uStack_11));
    if (iVar6 == 0) {
      set_diagnostic_callback_pending_955b6(0);
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(uVar7 - 0x5a31))))) = 0;
      publish_dcm_security_level_91e12(level);
      (*((undefined4 *)camry_host_ptr((uint32_t)(puVar3 + -0x5a20)))) = 0;
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x5a33))))) = 0;
      dcm_report_positive_response(((F33DcmMessageContext *)camry_host_ptr((uint32_t)(puVar3 + -0x5a2c))));
    }
    else {
      if (iVar6 == 1) {
        set_diagnostic_callback_pending_955b6(0);
        (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x5a33))))) = 0;
        message = ((F33DcmMessageContext *)camry_host_ptr((uint32_t)(puVar3 + -0x5a2c)));
        uVar5 = uStack_11;
      }
      else {
        if (iVar6 == 10) {
          set_diagnostic_callback_pending_955b6(1);
          dcm_enqueue_event('\x10');
          return 10;
        }
        if (iVar6 != 0xb) {
          set_diagnostic_callback_pending_955b6(0);
          (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x5a33))))) = 0;
          return 0;
        }
        set_diagnostic_callback_pending_955b6(0);
        bVar2 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(uVar7 - 0x5a31)))));
        if (bVar2 != 0xff) {
          bVar1 = bVar2 + 1;
          bVar2 = bVar2 + 1;
          (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(uVar7 - 0x5a31))))) = bVar1;
        }
        if (bVar2 < (byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)((short)(ushort)uVar5 * 0x18 + 0x237d)))))) {
          (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x5a33))))) = 0;
          message = ((F33DcmMessageContext *)camry_host_ptr((uint32_t)(puVar3 + -0x5a2c)));
          uVar5 = '5';
        }
        else {
          if ((*((int *)camry_host_ptr((uint32_t)(puVar4 + (short)(ushort)uVar5 * 0x18 + 0x236c)))) != 0) {
            dcm_arm_software_timer
                      ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(uVar7 * 2 + 0x235d))))),
                       (*((uint *)camry_host_ptr((uint32_t)(puVar4 + (short)(ushort)uVar5 * 0x18 + 0x236c)))));
            set_or_clear_security_delay_bit_96622(uVar7,1);
          }
          (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x5a33))))) = 0;
          message = ((F33DcmMessageContext *)camry_host_ptr((uint32_t)(puVar3 + -0x5a2c)));
          uVar5 = '6';
        }
      }
      dcm_report_negative_or_pending(message,uVar5);
    }
  }
  return 0;
}

void resume_selected_security_key_callback_9687c(void)

{
  if (app_security_selected_row < 2) {
    dcm_security_key_callback_join
              ((*((volatile uint8_t *)camry_host_ptr((uint32_t)((uint32_t)(0x26164u + (uint32_t)((short)(ushort)app_security_selected_row) * (uint32_t)sizeof(F33DcmSecurityLevelConfig)) + (uint32_t)(0) * (uint32_t)sizeof(F33DcmSecurityLevelConfig) + (uint32_t)offsetof(F33DcmSecurityLevelConfig, security_level))))),'\x01');
  }
  return;
}

void dcm_security_delay_expired(uchar timer_slot)

{
  uint uVar1;
  
  uVar1 = 0;
  do {
    if (timer_slot == (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x26159u + (uint32_t)(uVar1 * 2) * 1u))))) {
      set_or_clear_security_delay_bit_96622(uVar1,0);
      return;
    }
    uVar1 = uVar1 + 1;
  } while (uVar1 < 2);
  return;
}

void clear_security_issued_level_968c6(void)

{
  app_security_issued_level = '\0';
  return;
}

void dcm_security_session_notification(uchar old_session,uchar new_session)

{
  if (app_security_seed_callback_succeeded == '\x01') {
    app_security_issued_level = '\0';
    app_security_seed_callback_succeeded = '\0';
  }
  return;
}

undefined4 return_const_1_968de(void)

{
  return 1;
}

uint dcm_security_seed_request(uchar subfunction,uchar operation,F33DcmMessageContext *message)

{
  char cVar1;
  uchar **ppuVar2;
  short sVar3;
  undefined4 *puVar4;
  uint uVar5;
  uint32_t puVar6;
  uint32_t puVar7;
  uint uVar8;
  F33DcmMessageContext *pFVar9;
  int iVar10;
  
  puVar6 = 0xfebeb800u;
  puVar7 = 0x23dfcu;
  set_diagnostic_busy_marker_from_done_flag_9560e(0);
  puVar4 = ((undefined4 *)camry_host_ptr((uint32_t)(puVar6 + -0x5a2c)));
  pFVar9 = message + 1;
  do {
    ppuVar2 = &message->request;
    message = (F33DcmMessageContext *)&message->request_length;
    *puVar4 = *(uint32_t *)ppuVar2;
    puVar4 = puVar4 + 1;
  } while (camry_host_addr(pFVar9)!=camry_host_addr(message));
  set_diagnostic_callback_pending_955b6(0);
  uVar5 = 0;
  uVar8 = (int)(subfunction + 1) >> 1;
  do {
    sVar3 = (short)uVar5;
    if (uVar8 == (byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar7 + (uint32_t)(sVar3 * 0x18 + 0x237c)))))) {
      cVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar7 + (uint32_t)(uVar5 + 0x2362)))));
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(-0x5a34))))) = (char)uVar5;
      iVar10 = 0;
      if (cVar1 == '\x01') {
        iVar10 = (*((int *)camry_host_ptr((uint32_t)(puVar7 + sVar3 * 0x18 + 0x2368))));
      }
      if ((*((int *)camry_host_ptr((uint32_t)(puVar6 + -0x5a28)))) != iVar10) {
        (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(-0x5a33))))) = 0;
        dcm_report_negative_or_pending(((F33DcmMessageContext *)camry_host_ptr((uint32_t)(puVar6 + -0x5a2c))),'\x13');
        return 0;
      }
      if ((*((uint *)camry_host_ptr((uint32_t)(puVar7 + sVar3 * 0x18 + 0x2378)))) <= (*((uint *)camry_host_ptr((uint32_t)(puVar6 + -0x5a18))))) {
        uVar5 = dcm_security_seed_callback_join((uchar)uVar8,operation);
        return uVar5;
      }
      break;
    }
    uVar5 = uVar5 + 1;
  } while (uVar5 < 2);
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(-0x5a33))))) = 0;
  return 0;
}

uint dcm_security_cancel_seed(uchar subfunction,uchar operation)

{
  uint8_t stack_record_f[15];
  uint32_t puVar1;
  int iVar2;
  
  puVar1 = 0xfebeb800u;
  stack_record_f[2] = 0;
  stack_record_f[0] = 0;
  dcm_invalidate_queued_event('\x0f','\0');
  iVar2 = get_diagnostic_callback_pending_955bc();
  if (iVar2 == 1) {
    dispatch_security_seed_by_callback_kind_96b98((int)(subfunction + 1) >> 1, camry_host_addr(((uint8_t *)(stack_record_f))), operation, camry_host_addr(((uint8_t *)((stack_record_f + 1)))), camry_host_addr(((uint8_t *)((stack_record_f + 2)))));
    set_diagnostic_callback_pending_955b6(0);
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x5a33))))) = 0;
  set_diagnostic_busy_marker_from_done_flag_9560e(1);
  return 0;
}

uint dcm_security_seed_operation
               (uchar subfunction,uchar operation,F33DcmMessageContext *message)

{
  uint uVar1;
  
  if (operation == '\0') {
    uVar1 = dcm_security_seed_request(subfunction,'\0',message);
  }
  else {
    uVar1 = 0;
    if (operation == '\x02') {
      uVar1 = dcm_security_cancel_seed(subfunction,'\x02');
    }
  }
  return uVar1;
}

uint dcm_security_key_request(uchar subfunction,uchar operation,F33DcmMessageContext *message)

{
  char cVar1;
  uchar **ppuVar2;
  undefined4 *puVar3;
  uint uVar4;
  uint32_t puVar5;
  uint32_t puVar6;
  uint uVar7;
  uchar nrc;
  F33DcmMessageContext *pFVar8;
  
  puVar5 = 0xfebeb800u;
  puVar6 = 0x23dfcu;
  set_diagnostic_busy_marker_from_done_flag_9560e(0);
  puVar3 = ((undefined4 *)camry_host_ptr((uint32_t)(puVar5 + -0x5a2c)));
  pFVar8 = message + 1;
  do {
    ppuVar2 = &message->request;
    message = (F33DcmMessageContext *)&message->request_length;
    *puVar3 = *(uint32_t *)ppuVar2;
    puVar3 = puVar3 + 1;
  } while (camry_host_addr(pFVar8)!=camry_host_addr(message));
  set_diagnostic_callback_pending_955b6(0);
  uVar4 = (uint)(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x5a34)))));
  if (uVar4 < 2) {
    uVar7 = (int)(subfunction + 1) >> 1;
    if ((byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x5a33))))) == uVar7) {
      if ((*((int *)camry_host_ptr((uint32_t)(puVar5 + -0x5a28)))) ==
          (*((int *)camry_host_ptr((uint32_t)(puVar6 + (short)(ushort)(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x5a34))))) * 0x18 + 0x2374))))) {
        uVar4 = dcm_security_key_callback_join((uchar)uVar7,operation);
        return uVar4;
      }
      cVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(uVar4 - 0x5a31)))));
      if (((int8_t)cVar1) != -1) {
        (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(uVar4 - 0x5a31))))) = cVar1 + '\x01';
      }
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x5a33))))) = 0;
      nrc = '\x13';
    }
    else {
      if ((byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x5a33))))) != 0) {
        cVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(uVar4 - 0x5a31)))));
        if (((int8_t)cVar1) != -1) {
          (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(uVar4 - 0x5a31))))) = cVar1 + '\x01';
        }
        (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x5a33))))) = 0;
      }
      nrc = '$';
    }
    dcm_report_negative_or_pending(((F33DcmMessageContext *)camry_host_ptr((uint32_t)(puVar5 + -0x5a2c))),nrc);
  }
  return 0;
}

uint dcm_security_cancel_key(uchar subfunction,uchar operation)

{
  uint8_t stack_record_e[14];
  uint32_t puVar1;
  int iVar2;
  
  puVar1 = 0xfebeb800u;
  stack_record_e[1] = 0;
  stack_record_e[0] = 0;
  dcm_invalidate_queued_event('\x10','\0');
  iVar2 = get_diagnostic_callback_pending_955bc();
  if (iVar2 == 1) {
    dispatch_security_key_by_callback_kind_96bce((int)(subfunction + 1) >> 1, camry_host_addr(((uint8_t *)(stack_record_e))), operation, camry_host_addr(((uint8_t *)((stack_record_e + 1)))));
    set_diagnostic_callback_pending_955b6(0);
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x5a33))))) = 0;
  set_diagnostic_busy_marker_from_done_flag_9560e(1);
  return 0;
}

uint dcm_security_key_operation(uchar subfunction,uchar operation,F33DcmMessageContext *message)

{
  uint uVar1;
  
  if (operation == '\0') {
    uVar1 = dcm_security_key_request(subfunction,'\0',message);
  }
  else {
    uVar1 = 0;
    if (operation == '\x02') {
      uVar1 = dcm_security_cancel_key(subfunction,'\x02');
    }
  }
  return uVar1;
}

undefined4 return_const_1_96b24(void)

{
  return 1;
}

uint prepare_security_seed_ignoring_second_argument_96b28(uchar *param_1,undefined4 param_2,uchar *param_3,uchar *param_4)

{
  return app_security_prepare_seed(param_1,param_3,param_4);
}

undefined4 return_const_1_96b38(void)

{
  return 1;
}

uint compare_security_key_96b3c(uchar *param_1)

{
  return app_security_compare_key(param_1);
}

uint dcm_security_sub1_callback(uchar operation,F33DcmMessageContext *message)

{
  uint uVar1;
  
  uVar1 = dcm_security_seed_operation('\x01',operation,message);
  return uVar1;
}

uint dcm_security_sub2_callback(uchar operation,F33DcmMessageContext *message)

{
  uint uVar1;
  
  uVar1 = dcm_security_key_operation('\x02',operation,message);
  return uVar1;
}

uint dcm_security_sub3_callback(uchar operation,F33DcmMessageContext *message)

{
  uint uVar1;
  
  uVar1 = dcm_security_seed_operation('\x03',operation,message);
  return uVar1;
}

uint dcm_security_sub4_callback(uchar operation,F33DcmMessageContext *message)

{
  uint uVar1;
  
  uVar1 = dcm_security_key_operation('\x04',operation,message);
  return uVar1;
}

undefined4
dispatch_security_seed_by_callback_kind_96b98(char param_1,undefined4 param_2,undefined1 param_3,undefined4 param_4,
            undefined4 param_5)

{
  undefined4 uVar1;
  
  if (param_1 == '\x01') {
    uVar1 = ((void)(param_2), (void)(param_3), (void)(param_4), (void)(param_5), return_const_1_96b24());
  }
  else {
    uVar1 = 0;
    if (param_1 == '\x02') {
      uVar1 = prepare_security_seed_ignoring_second_argument_96b28(((uchar *)camry_host_ptr((uint32_t)(param_2))), param_3, ((uchar *)camry_host_ptr((uint32_t)(param_4))), ((uchar *)camry_host_ptr((uint32_t)(param_5))));
    }
  }
  return uVar1;
}

undefined4 dispatch_security_key_by_callback_kind_96bce(char param_1,undefined4 param_2,undefined1 param_3,undefined4 param_4)

{
  undefined4 uVar1;
  
  if (param_1 == '\x01') {
    uVar1 = ((void)(param_2), (void)(param_3), (void)(param_4), return_const_1_96b38());
  }
  else {
    uVar1 = 0;
    if (param_1 == '\x02') {
      uVar1 = ((void)(param_3), (void)(param_4), compare_security_key_96b3c(((uchar *)camry_host_ptr((uint32_t)(param_2)))));
    }
  }
  return uVar1;
}

uint dcm_validate_configured_communication_selection
               (uchar subfunction,uchar communication_class,uchar subnet,ushort node)

{
  uchar uVar1;
  ushort uVar2;
  uint uVar3;
  uint uVar4;
  
  uVar4 = 1;
  uVar1 = dcm_communication_configuration.normal_enabled;
  if ((((communication_class == '\x01') ||
       (uVar1 = dcm_communication_configuration.nm_enabled, communication_class == '\x02')) ||
      ((communication_class == '\x03' &&
       (dcm_communication_configuration.normal_enabled == '\x01')))) && (uVar1 == '\x01')) {
    if (subnet != '\0') {
      if (subnet == '\x0f') {
        if (dcm_communication_configuration.current_network_enabled != '\x01') {
          return uVar4;
        }
      }
      else {
        uVar2 = 0;
        while( true ) {
          if (dcm_communication_configuration.subnet_count <= uVar2) {
            return uVar4;
          }
          if (((*((uchar *)camry_host_ptr((uint32_t)((int)dcm_communication_configuration.subnets + (short)uVar2 * 3 + 1))))
               == subnet) &&
             ((*((char *)camry_host_ptr((uint32_t)((int)dcm_communication_configuration.subnets + (short)uVar2 * 3)))) ==
              '\x01')) break;
          uVar2 = uVar2 + 1 & 0xff;
        }
      }
    }
    if (subfunction == '\x04' || subfunction == '\x05') {
      uVar3 = 0;
      while( true ) {
        if ((ushort)(*((volatile uint16_t *)camry_host_ptr(0x261cau))) <= uVar3) {
          return uVar4;
        }
        if (((*((ushort *)camry_host_ptr((uint32_t)((int)dcm_communication_configuration.nodes + uVar3 * 4 + 2)))) == node) &&
           ((*((char *)camry_host_ptr((uint32_t)((int)dcm_communication_configuration.nodes + uVar3 * 4)))) == '\x01')) break;
        uVar3 = uVar3 + 1 & 0xffff;
      }
    }
    return 0;
  }
  return uVar4;
}

void notify_communication_callbacks_for_matching_node_96ca4(char param_1,short param_2,char param_3,undefined1 param_4)

{
  int iVar1;
  uint uVar2;
  
  if (param_1 == '\x04' || param_1 == '\x05') {
    for (uVar2 = 0; uVar2 < (ushort)(*((volatile uint16_t *)camry_host_ptr(0x261cau)));
        uVar2 = uVar2 + 1 & 0xffff) {
      iVar1 = uVar2 * 4;
      if ((((*((short *)camry_host_ptr((uint32_t)((int)dcm_communication_configuration.nodes + iVar1 + 2)))) == param_2) &&
          ((*((char *)camry_host_ptr((uint32_t)((int)dcm_communication_configuration.nodes + iVar1)))) == '\x01')) &&
         ((*((char *)camry_host_ptr((uint32_t)((int)dcm_communication_configuration.nodes + iVar1 + 1)))) == param_3))
      goto LAB_00096cf6;
    }
  }
  else {
LAB_00096cf6:
    ((void)(param_3), (void)(param_4), return_const_0_9713a());
    ((void)(param_3), (void)(param_4), return_only_stub_97138());
  }
  return;
}

undefined4 apply_communication_policy_for_matching_node_96d0a(char param_1,short param_2,char param_3,undefined1 param_4)

{
  uint uVar1;
  int iVar2;
  
  if (param_1 == '\x04' || param_1 == '\x05') {
    for (uVar1 = 0; uVar1 < (ushort)(*((volatile uint16_t *)camry_host_ptr(0x261cau)));
        uVar1 = uVar1 + 1 & 0xffff) {
      iVar2 = uVar1 * 4;
      if ((((*((short *)camry_host_ptr((uint32_t)((int)dcm_communication_configuration.nodes + iVar2 + 2)))) == param_2) &&
          ((*((char *)camry_host_ptr((uint32_t)((int)dcm_communication_configuration.nodes + iVar2)))) == '\x01')) &&
         ((*((char *)camry_host_ptr((uint32_t)((int)dcm_communication_configuration.nodes + iVar2 + 1)))) == param_3))
      goto LAB_00096d5a;
    }
  }
  else {
LAB_00096d5a:
    iVar2 = apply_and_complete_communication_policy_97128(param_3,param_4);
    if (iVar2 != 0) {
      if (iVar2 == 10) {
        return 10;
      }
      return 1;
    }
  }
  return 0;
}

void dcm_complete_or_queue_communication_request
               (uchar subnet,uchar subfunction,ushort node,uchar mapped_mode,uchar start_index)

{
  ushort uVar1;
  uint32_t puVar2;
  uint32_t puVar3;
  int iVar4;
  uint uVar5;
  
  puVar2 = 0xfebeb800u;
  puVar3 = 0x23dfcu;
  if (subnet == '\0') {
    for (uVar5 = (uint)start_index; uVar5 < (byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(0x23cc))))); uVar5 = uVar5 + 1 & 0xff) {
      if (((*((char *)camry_host_ptr((uint32_t)((*((volatile int32_t *)camry_host_ptr((uint32_t)(puVar3 + 0x23d0)))) + uVar5 * 2)))) == '\x01') &&
         (iVar4 = apply_communication_policy_for_matching_node_96d0a(subfunction,node,
                               (*((undefined1 *)camry_host_ptr((uint32_t)((*((volatile int32_t *)camry_host_ptr((uint32_t)(puVar3 + 0x23d0)))) + uVar5 * 2 + 1)))),
                               mapped_mode), iVar4 != 0)) goto LAB_00096dc0;
    }
  }
  else if (subnet == '\x0f') {
    uVar5 = thunk_dcm_get_current_dispatch_receive_slot_93c60();
    if (2 < uVar5) {
      return;
    }
    uVar1 = (*((ushort *)camry_host_ptr((uint32_t)(puVar3 + (short)uVar5 * 0xc + 0x20ec))));
    if (1 < uVar1) {
      return;
    }
    iVar4 = apply_communication_policy_for_matching_node_96d0a(subfunction,node,
                         (*((undefined1 *)camry_host_ptr((uint32_t)((*((volatile int32_t *)camry_host_ptr((uint32_t)((uint)(*((volatile uint16_t *)camry_host_ptr((uint32_t)((int)(puVar3 + (short)uVar5 * 0xc + 0x20ec) + 2)))) * 4 +
                                   (*((volatile int32_t *)camry_host_ptr((uint32_t)(puVar3 + (short)uVar1 * 0x14 + 0x20c4)))))))) + 2)))),mapped_mode
                        );
    if (iVar4 != 0) {
      if (iVar4 == 1) {
        return;
      }
      goto LAB_00096dc8;
    }
  }
  else {
    for (uVar5 = (uint)start_index; uVar5 < (byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(0x23cd))))); uVar5 = uVar5 + 1 & 0xff) {
      iVar4 = (short)uVar5 * 3;
      if ((((*((uchar *)camry_host_ptr((uint32_t)((*((volatile int32_t *)camry_host_ptr((uint32_t)(puVar3 + 0x23d4)))) + iVar4 + 1)))) == subnet) &&
          ((*((char *)camry_host_ptr((uint32_t)((*((volatile int32_t *)camry_host_ptr((uint32_t)(puVar3 + 0x23d4)))) + iVar4)))) == '\x01')) &&
         (iVar4 = apply_communication_policy_for_matching_node_96d0a(subfunction,node,
                               (*((undefined1 *)camry_host_ptr((uint32_t)((*((volatile int32_t *)camry_host_ptr((uint32_t)(puVar3 + 0x23d4)))) + iVar4 + 2)))),mapped_mode),
         iVar4 != 0)) goto LAB_00096dc0;
    }
  }
  dcm_report_positive_response(((F33DcmMessageContext *)camry_host_ptr((uint32_t)(puVar2 + -0x5a08))));
  return;
LAB_00096dc0:
  if (iVar4 == 1) {
    return;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x5a0d))))) = (char)uVar5;
LAB_00096dc8:
  dcm_enqueue_event('&');
  return;
}

uint dcm_begin_configured_communication_request(F33DcmMessageContext *message,uchar subfunction)

{
  uchar uVar1;
  uchar **ppuVar2;
  undefined4 *puVar3;
  uint uVar4;
  int iVar5;
  uint32_t puVar6;
  uint32_t puVar7;
  uint uVar8;
  uint uVar9;
  ushort node;
  ushort uVar10;
  F33DcmMessageContext *pFVar11;
  byte *pbVar12;
  uchar uStack_19;
  
  puVar6 = 0xfebeb800u;
  puVar7 = 0x23dfcu;
  uStack_19 = '\0';
  set_diagnostic_busy_marker_from_done_flag_9560e(0);
  puVar3 = ((undefined4 *)camry_host_ptr((uint32_t)(puVar6 + -0x5a08)));
  pFVar11 = message;
  do {
    ppuVar2 = &pFVar11->request;
    pFVar11 = (F33DcmMessageContext *)&pFVar11->request_length;
    *puVar3 = *(uint32_t *)ppuVar2;
    puVar3 = puVar3 + 1;
  } while (camry_host_addr(message + 1)!=camry_host_addr(pFVar11));
  uVar9 = message->request_length;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(-0x5a0e))))) = subfunction;
  if (subfunction == '\x04' || subfunction == '\x05') {
    uVar4 = 3;
  }
  else {
    uVar4 = 1;
  }
  uVar1 = '\x13';
  if (uVar9 == uVar4) {
    pbVar12 = ((void *)camry_host_ptr((uint32_t)(message->request)));
    node = 0;
    uVar9 = *pbVar12 & 0xf;
    uVar4 = (int)(uint)*pbVar12 >> 4;
    if (subfunction == '\x04' || subfunction == '\x05') {
      node = CONCAT11(pbVar12[1],pbVar12[2]);
    }
    uVar8 = dcm_validate_configured_communication_selection
                      (subfunction,(uchar)uVar9,(uchar)uVar4,node);
    uVar1 = '1';
    if (uVar8 == 0) {
      uVar8 = dcm_check_communication_application_admission
                        (subfunction,*((uint8_t *)camry_host_ptr((uint32_t)(message->request))),node,&uStack_19);
      if (uVar8 == 0) {
        (*((ushort *)camry_host_ptr((uint32_t)(puVar6 + -0x5a10)))) = message->service_list_selector;
        (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(-0x5a0c))))) = 1;
        if (5 < subfunction) {
          return 0;
        }
        uVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar7 + (uint32_t)((short)(ushort)subfunction * 3 + uVar9 + 0x23af)))));
        if (uVar4 == 0) {
          for (uVar9 = 0; uVar9 < (byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar7 + (uint32_t)(0x23cc))))); uVar9 = uVar9 + 1 & 0xff) {
            if ((*((char *)camry_host_ptr((uint32_t)((*((volatile int32_t *)camry_host_ptr((uint32_t)(puVar7 + 0x23d0)))) + uVar9 * 2)))) == '\x01') {
              notify_communication_callbacks_for_matching_node_96ca4(subfunction,node,
                           (*((undefined1 *)camry_host_ptr((uint32_t)((*((volatile int32_t *)camry_host_ptr((uint32_t)(puVar7 + 0x23d0)))) + uVar9 * 2 + 1)))),uVar1);
            }
          }
        }
        else if (uVar4 == 0xf) {
          uVar9 = thunk_dcm_get_current_dispatch_receive_slot_93c60();
          if (uVar9 < 3) {
            uVar10 = (*((ushort *)camry_host_ptr((uint32_t)(puVar7 + (short)uVar9 * 0xc + 0x20ec))));
            if (uVar10 < 2) {
              notify_communication_callbacks_for_matching_node_96ca4(subfunction,node,
                           (*((undefined1 *)camry_host_ptr((uint32_t)((*((volatile int32_t *)camry_host_ptr((uint32_t)((uint)(*((volatile uint16_t *)camry_host_ptr((uint32_t)((int)(puVar7 + (short)uVar9 * 0xc + 0x20ec) + 2)))) * 4 +
                                     (*((volatile int32_t *)camry_host_ptr((uint32_t)(puVar7 + (short)uVar10 * 0x14 + 0x20c4)))))))) + 2)))),uVar1);
            }
          }
        }
        else {
          for (uVar10 = 0; uVar10 < (byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar7 + (uint32_t)(0x23cd))))); uVar10 = uVar10 + 1 & 0xff) {
            iVar5 = (short)uVar10 * 3;
            if (((*((byte *)camry_host_ptr((uint32_t)((*((volatile int32_t *)camry_host_ptr((uint32_t)(puVar7 + 0x23d4)))) + iVar5 + 1)))) == uVar4) &&
               ((*((char *)camry_host_ptr((uint32_t)((*((volatile int32_t *)camry_host_ptr((uint32_t)(puVar7 + 0x23d4)))) + iVar5)))) == '\x01')) {
              notify_communication_callbacks_for_matching_node_96ca4(subfunction,node,(*((undefined1 *)camry_host_ptr((uint32_t)((*((volatile int32_t *)camry_host_ptr((uint32_t)(puVar7 + 0x23d4)))) + iVar5 + 2)))),
                           uVar1);
            }
          }
        }
        (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(-0x5a0d))))) = 0;
        dcm_complete_or_queue_communication_request((uchar)uVar4,subfunction,node,uVar1,'\0');
        return 0;
      }
      uVar1 = uStack_19;
      if (uVar8 != 1) {
        return 0;
      }
    }
  }
  uStack_19 = uVar1;
  dcm_report_negative_or_pending(((F33DcmMessageContext *)camry_host_ptr((uint32_t)(puVar6 + -0x5a08))),uStack_19);
  return 0;
}
