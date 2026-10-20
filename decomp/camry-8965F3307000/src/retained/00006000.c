#include "common.h"

void return_only_stub_6082(void)

{
  return;
}

void boot_ecu_reset_negative_response_6084(uchar param_1)

{
  boot_negative_response('\x11',param_1);
  return;
}

void boot_ecu_reset_positive_response_6098(void)

{
  (*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff92d0u)))) = 0x51;
  (*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff92d1u)))) = (*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff939eu)))) & 0x7f;
  boot_response_submit((*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff939eu)))) >> 7 ^ 1,((undefined *)camry_host_ptr((camry_gp + 0xffff92d0u))),2);
  return;
}

void boot_service_reset_request(ushort request_length)

{
  uint8_t stack_record_a[10];
  uint32_t puVar1;
  F33BootInterruptEntry *pFVar2;
  undefined4 uVar3;
  
  puVar1 = (camry_gp + 0x0u);
  pFVar2 = ((volatile F33BootInterruptEntry *)camry_host_ptr((camry_tp + 0x0u)));
  stack_record_a[0] = 0;
  stack_record_a[1] = 0;
  boot_copy_request_bytes_and_clear_append_index_67b0(((uint8_t *)(stack_record_a)),2);
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6cf2))))) != (char)pFVar2[0x10b].eiic) {
    uVar3 = 0x7f;
    goto LAB_000060ee;
  }
  if (1 < request_length) {
    if ((stack_record_a[1] & 0x7f) != 1) {
      uVar3 = 0x12;
      goto LAB_000060ee;
    }
    if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6cf1))))) != '\x02') {
      uVar3 = 0x33;
      goto LAB_000060ee;
    }
    if (request_length == 2) {
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6c62))))) = stack_record_a[1];
      boot_call_terminal_action_or_defer_until_response_67da();
      boot_ecu_reset_positive_response_6098();
      return;
    }
  }
  uVar3 = 0x13;
LAB_000060ee:
  boot_ecu_reset_negative_response_6084(uVar3);
  return;
}

void return_only_stub_6134(void)

{
  return;
}

void boot_session_control_negative_response_6136(uchar param_1)

{
  boot_negative_response('\x10',param_1);
  return;
}

void boot_service_session_control(ushort request_length)

{
  uint8_t stack_record_e[14];
  uint32_t puVar1;
  undefined4 uVar2;
  int iVar3;
  byte bVar4;
  bool bVar5;
  
  puVar1 = (camry_gp + 0x0u);
  stack_record_e[0] = 0;
  stack_record_e[1] = 0;
  boot_copy_request_bytes_and_clear_append_index_67b0(((uint8_t *)(stack_record_e)),2);
  bVar4 = stack_record_e[1] & 0x7f;
  if (1 < request_length) {
    if (((bVar4 != 1) && (bVar4 != 2)) && (bVar4 != 3)) {
      uVar2 = 0x12;
      goto LAB_0000617e;
    }
    if (bVar4 == 2) {
      bVar5 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6cf2))))) == '\x01';
LAB_0000619c:
      if (bVar5) {
        uVar2 = 0x7e;
        goto LAB_0000617e;
      }
    }
    else if (bVar4 == 3) {
      bVar5 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6cf2))))) == '\x02';
      goto LAB_0000619c;
    }
    if (request_length == 2) {
      if ((stack_record_e[1] & 0x7f) == 0) {
        return;
      }
      if (bVar4 != 1) {
        if (3 < bVar4) {
          return;
        }
        if (bVar4 < 3) {
          if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6c5f))))) == '\0') {
            iVar3 = latch_initialization_once_and_set_state_two_4776();
            if (iVar3 != 0) {
              boot_session_control_negative_response_6136(0x22);
              (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6c5d))))) = 0;
              return;
            }
            (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6c60))))) = bVar4;
            (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6c61))))) = stack_record_e[1];
            (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6c5d))))) = 1;
            return;
          }
          (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6c5f))))) = 0;
          (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6c5e))))) = 1;
        }
      }
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6c60))))) = bVar4;
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6c61))))) = stack_record_e[1];
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6c5d))))) = 2;
      return;
    }
  }
  uVar2 = 0x13;
LAB_0000617e:
  boot_session_control_negative_response_6136(uVar2);
  return;
}

void boot_session_control_positive_timing_response_6204(void)

{
  (*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff92d0u)))) = 0x50;
  (*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff92d1u)))) = (undefined1)((*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff939fu)))) & 0x7f);
  if ((((*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff939fu)))) & 0x7fu) - 1u) < 3u) {
    (*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff92d2u)))) = 0;
    (*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff92d3u)))) = 0x32;
    (*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff92d4u)))) = 1;
    (*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff92d5u)))) = 0xf4;
  }
  boot_response_submit((*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff939fu)))) >> 7 ^ 1,((undefined *)camry_host_ptr((camry_gp + 0xffff92d0u))),6);
  return;
}

void boot_session_progress(void)

{
  byte bVar1;
  undefined1 uVar2;
  uint32_t puVar3;
  uchar session;
  undefined4 uVar4;
  int iVar5;
  
  puVar3 = (camry_gp + 0x0u);
  if ((*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff93a3u)))) == '\0') {
    return;
  }
  if ((*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff93bcu)))) == '\x01') {
    return;
  }
  iVar5 = boot_get_combined_request_response_state_67f6();
  if (iVar5 == 6) {
    uVar4 = 0x10;
LAB_000062ce:
    boot_session_control_negative_response_6136(uVar4);
  }
  else {
    bVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6c60)))));
    if (bVar1 != 0) {
      if (bVar1 == 1) {
        if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6c5d))))) == '\x02') {
          session = '\x01';
LAB_000062c0:
          boot_session_publish(session);
          boot_session_control_positive_timing_response_6204();
        }
      }
      else if (bVar1 < 3) {
        if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6c5d))))) == '\x01') {
          iVar5 = get_gp_initialization_latch_byte_92a3_4794();
          if (iVar5 != 0) {
            return;
          }
          iVar5 = get_gp_state_byte_92a2_478e();
          if (iVar5 == 0) {
            (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6c5e))))) = 1;
            uVar2 = 2;
            goto LAB_000062d4;
          }
          uVar4 = 0x22;
          goto LAB_000062ce;
        }
        if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6c5d))))) == '\x02') {
          if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6c5e))))) != '\0') {
            return;
          }
          session = '\x02';
          goto LAB_000062c0;
        }
      }
      else if ((bVar1 == 3) && ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6c5d))))) == '\x02')) {
        session = '\x03';
        goto LAB_000062c0;
      }
    }
  }
  uVar2 = 0;
LAB_000062d4:
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6c5d))))) = uVar2;
  return;
}

void boot_session_foreground_join(void)

{
  uint32_t puVar1;
  puVar1 = (camry_gp + 0x0u);
  if ((*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff93a2u)))) == '\x01') {
    if (DAT_febf2bd1 == '\0') {
      puVar1 = (camry_gp + 0x0u);
      boot_programming_prepare();
    }
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6c5e))))) = 0;
  }
  return;
}

void clear_session_transition_bytes_6300(void)

{
  (*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff93a1u)))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff93a2u)))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff93a3u)))) = 0;
  return;
}

uint32_t boot_flag_transition_and_publish_session_three_630c(void)

{
  uint32_t camry_r10_result;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)((camry_gp + 0xffff93a1u))))) = 1;
  (camry_r10_result = boot_session_publish('\x03'));
  return camry_r10_result;
}

undefined4 boot_reset_transport_and_sample_register_6320(void)

{
  uint32_t puVar1;
  undefined4 uVar2;
  
  puVar1 = (camry_gp + 0x0u);
  (*((volatile uint16_t *)camry_host_ptr((camry_gp + 0xffff93b8u)))) = 0;
  (*((volatile uint16_t *)camry_host_ptr((camry_gp + 0xffff98b8u)))) = 0;
  (*((volatile uint16_t *)camry_host_ptr((camry_gp + 0xffff98bau)))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff93bau)))) = '\0';
  (*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff93bbu)))) = '\0';
  (*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff93bcu)))) = '\0';
  uVar2 = read_ffe51010_word_1d24();
  (*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + -0x6c4c)))) = uVar2;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6c43))))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6c41))))) = 0;
  return uVar2;
}

void boot_clear_request_append_index_636e(void)

{
  (*((volatile uint16_t *)camry_host_ptr((camry_gp + 0xffff93b8u)))) = 0;
  return;
}

uint boot_request_admit
               (ushort channel,F33BootPduInfo *first_chunk,ushort total_length,
               ushort *remaining_capacity)

{
  undefined1 uVar1;
  uchar uVar2;
  uint32_t puVar3;
  int iVar4;
  uchar *puVar5;
  uint uVar6;
  
  puVar3 = (camry_gp + 0x0u);
  puVar5 = ((void *)camry_host_ptr((uint32_t)(first_chunk->data)));
  uVar2 = *(volatile uint8_t *)camry_host_ptr((camry_tp + 0x86du) + (uint32_t)channel * 8u);
  uVar1 = (undefined1)first_chunk->length;
  if (total_length < 0x1001) {
    uVar6 = 0;
    *remaining_capacity = 0x1000;
  }
  else {
    uVar6 = 3;
  }
  if ((*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff93bau)))) == '\x02') {
LAB_000063dc:
    uVar6 = 1;
  }
  else {
    iVar4 = is_suppressed_tester_present_526a(camry_host_addr(puVar5), uVar1, uVar2);
    if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6c46))))) == '\x01') {
      if (iVar4 == 1) goto LAB_000063dc;
      if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6c42))))) == '\x01') {
        ((void)((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6742)))))), return_only_stub_5284());
      }
    }
    else if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6c41))))) == '\x01') goto LAB_000063dc;
    if (uVar6 == 0) {
      (*((ushort *)camry_host_ptr((uint32_t)(puVar3 + -0x6744)))) = channel;
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6741))))) = uVar2;
      uVar2 = *puVar5;
      (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x6748)))) = 0;
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6742))))) = uVar2;
      boot_clear_request_append_index_636e();
      if (iVar4 == 2) {
        (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6c42))))) = 1;
        ((void)((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6742)))))), (void)(uVar1), return_only_stub_5280());
      }
      else {
        (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6c42))))) = 0;
      }
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6c46))))) = 1;
    }
  }
  return uVar6;
}

void boot_request_append_bytes(uchar *source,uchar length)

{
  uchar uVar1;
  uint uVar2;
  uint uVar3;
  
  uVar3 = (uint)length;
  uVar2 = (uint)(*((volatile uint16_t *)camry_host_ptr((camry_gp + 0xffff93b8u))));
  if ((-1 < (int)(uVar3 + uVar2 + -0x1000)) && (uVar3 = 0, uVar2 < 0x1000)) {
    uVar3 = 0x1000 - uVar2 & 0xffff;
  }
  for (; uVar3 != 0; uVar3 = uVar3 - 1) {
    uVar1 = *source;
    source = source + 1;
    (*((volatile uint16_t *)camry_host_ptr((camry_gp + 0xffff93b8u)))) = (ushort)(uVar2 + 1);
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)((camry_gp + 0xffff98c0u) + (uint32_t)(uVar2) * 1u)))) = uVar1;
    uVar2 = uVar2 + 1 & 0xffff;
  }
  return;
}

uint boot_request_append(ushort channel,F33BootPduInfo *chunk,ushort *remaining_capacity)

{
  uchar uVar1;
  byte bVar2;
  uchar *puVar3;
  uint uVar4;
  uint uVar5;
  uint uVar6;
  
  bVar2 = (byte)chunk->length;
  uVar6 = (uint)bVar2;
  puVar3 = ((void *)camry_host_ptr((uint32_t)(chunk->data)));
  uVar5 = 1;
  if (uVar6 != 0) {
    uVar4 = 0x1000 - (*((volatile uint16_t *)camry_host_ptr((camry_gp + 0xffff98b8u))));
    if ((int)(uVar6 - uVar4) < 0 == ((int)uVar4 < 0 && (int)uVar4 < 0 == (int)(uVar6 - uVar4) < 0)
        && uVar6 != uVar4) goto LAB_000064a0;
    (*((volatile uint16_t *)camry_host_ptr((camry_gp + 0xffff98b8u)))) = bVar2 + (*((volatile uint16_t *)camry_host_ptr((camry_gp + 0xffff98b8u))));
    uVar5 = (uint)boot_request_append_index;
    uVar4 = uVar6;
    if ((-1 < (int)(uVar6 + uVar5 + -0x1000)) && (uVar4 = 0, uVar5 < 0x1000)) {
      uVar4 = 0x1000 - uVar5 & 0xffff;
    }
    for (; uVar4 != 0; uVar4 = uVar4 - 1) {
      uVar1 = *puVar3;
      puVar3 = puVar3 + 1;
      boot_request_append_index = (ushort)(uVar5 + 1);
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebf30c0u + (uint32_t)(uVar5) * 1u)))) = uVar1;
      uVar5 = uVar5 + 1 & 0xffff;
    }
  }
  uVar5 = 0;
  *remaining_capacity = 0x1000 - (*((volatile uint16_t *)camry_host_ptr((camry_gp + 0xffff98b8u))));
LAB_000064a0:
  if ((*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff93beu)))) == '\x01') {
    ((void)((*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff98beu))))), (void)(uVar6), return_only_stub_5282());
  }
  return uVar5;
}

void boot_request_receive_complete(ushort channel,uchar status)

{
  uint32_t puVar1;
  uint32_t puVar2;
  undefined4 uVar3;
  
  puVar2 = (camry_gp + 0x0u);
  puVar1 = (camry_gp + 0x0u);
  if (status == '\0') {
    uVar3 = ((void)(channel), read_ffe51010_word_1d24());
    (*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + -0x6c54)))) = uVar3;
    (*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + -0x6c50)))) = uVar3;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6c46))))) = 2;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6c45))))) = 0;
    boot_dispatch_diagnostic_service((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6742))))),(*((ushort *)camry_host_ptr((uint32_t)(puVar1 + -0x6748)))));
  }
  else {
    if ((*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff93beu)))) == '\x01') {
      puVar2 = (camry_gp + 0x0u);
      ((void)((*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff98beu))))), return_only_stub_5284());
    }
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x6c46))))) = 0;
    uVar3 = read_ffe51010_word_1d24();
    (*((undefined4 *)camry_host_ptr((uint32_t)(puVar2 + -0x6c4c)))) = uVar3;
  }
  return;
}

void boot_diagnostic_replay_handoff_session(uint in_r6)

{
  uint8_t stack_record_14[20];
  int iVar1;
  int iVar2;
  int iVar3;
  ushort channel;
  uint uVar4;
  F33BootPduInfo FStack_10;
  
  iVar3 = 0;
  do {
    if ((*((uint *)camry_host_ptr((uint32_t)(in_r6 + 4)))) == (*((volatile uint32_t *)camry_host_ptr((uint32_t)((uint32_t)((camry_tp + 0x868u) + (uint32_t)(iVar3) * (uint32_t)sizeof(F33BootChannelEntry)) + (uint32_t)(0) * (uint32_t)sizeof(F33BootChannelEntry) + (uint32_t)offsetof(F33BootChannelEntry, handoff_selector)))))) {
      stack_record_14[2] = '\x10';
      stack_record_14[3] = (*((byte *)camry_host_ptr((uint32_t)(in_r6 + 0x10))));
      if ((*((char *)camry_host_ptr((uint32_t)(in_r6 + 0x14)))) != '\0') {
        stack_record_14[3] = stack_record_14[3] | 0x80;
      }
      boot_publish_session_three_and_cancel_security_delay_5148();
      FStack_10.data = camry_host_addr((stack_record_14 + 2));
      FStack_10.length = 2;
      channel = (ushort)iVar3;
      uVar4 = boot_request_admit(channel,&FStack_10,2,stack_record_14);
      if (((uVar4 == 0) && (1 < (*((uint16_t *)(stack_record_14 + 0))))) &&
         (uVar4 = boot_request_append(channel,&FStack_10,stack_record_14), uVar4 == 0)) {
        boot_request_receive_complete(channel,'\0');
      }
      return;
    }
    iVar2 = iVar3 + 1;
    iVar1 = iVar3 + -1;
    iVar3 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  do {
                    /* WARNING: Do nothing block with infinite loop */
  } while( true );
}

void boot_finalize_received_request_6588(void)

{
  (*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff93beu)))) = 0;
  (*((volatile uint16_t *)camry_host_ptr((camry_gp + 0xffff93b8u)))) = (*((volatile uint16_t *)camry_host_ptr((camry_gp + 0xffff98b8u))));
  (*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff93bau)))) = '\x01';
  boot_request_receive_complete(0,'\0');
  return;
}

void boot_response_timer_progress(void)

{
  undefined1 uVar1;
  uint32_t puVar2;
  F33BootInterruptEntry *pFVar3;
  int iVar4;
  undefined4 uVar5;
  uint32_t puVar6;
  
  puVar2 = (camry_gp + 0x0u);
  pFVar3 = ((volatile F33BootInterruptEntry *)camry_host_ptr((camry_tp + 0x0u)));
  if ((*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff93bbu)))) == '\x01') {
    iVar4 = read_ffe51010_word_1d24();
    if (iVar4 == (*((int *)camry_host_ptr((uint32_t)(puVar2 + -0x6c54))))) {
      return;
    }
    start_response_if_enabled_without_busy_state_2d88((*((undefined1 *)((uint8_t *)&pFVar3[(*((volatile uint16_t *)camry_host_ptr((uint32_t)(puVar2 + -0x6744)))) + 0x10d].handler + (2)))), ((uint32_t)((uint32_t)(puVar2 + -0x6c5c))));
    uVar1 = 2;
  }
  else {
    if ((*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff93bbu)))) == '\x02') {
      return;
    }
    if ((*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff93bbu)))) == '\x04') {
      return;
    }
    puVar6 = (0x9c40u);
    if ((*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff93bbu)))) == '\x03') {
      puVar6 = ((uint32_t)(0x2349340));
    }
    puVar2 = (camry_gp + 0x0u);
    iVar4 = read_ffe51010_word_1d24();
    if ((uint)(iVar4 - (*((int *)camry_host_ptr((uint32_t)(puVar2 + -0x6c50))))) < 3600000000) {
      if ((uint32_t)(iVar4 - (*((volatile int32_t *)camry_host_ptr((uint32_t)(puVar2 + -0x6c54))))) <=(puVar6)) {
        return;
      }
      if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x6c44))))) == '\x01') {
        return;
      }
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x6c40))))) = 0x7f;
      (*((volatile uint32_t *)camry_host_ptr((uint32_t)(puVar2 + -0x6c5c)))) = ((uint32_t)((uint32_t)(puVar2 + -0x6c40)));
      (*((undefined2 *)camry_host_ptr((uint32_t)(puVar2 + -0x6c58)))) = 3;
      (*((undefined2 *)camry_host_ptr((uint32_t)(puVar2 + -0x6746)))) = 3;
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x6c3f))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x6742)))));
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x6c3e))))) = 0x78;
      start_response_if_enabled_without_busy_state_2d88((*((undefined1 *)((uint8_t *)&pFVar3[(*((volatile uint16_t *)camry_host_ptr((uint32_t)(puVar2 + -0x6744)))) + 0x10d].handler + (2)))), ((uint32_t)((uint32_t)(puVar2 + -0x6c5c))));
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x6c44))))) = 1;
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x6c45))))) = 3;
      uVar5 = read_ffe51010_word_1d24();
      (*((undefined4 *)camry_host_ptr((uint32_t)(puVar2 + -0x6c54)))) = uVar5;
      return;
    }
    uVar1 = 4;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x6c45))))) = uVar1;
  return;
}

void boot_diagnostic_timeout_progress(void)

{
  uint32_t puVar1;
  int iVar2;
  undefined4 uVar3;
  uint uVar4;
  
  puVar1 = (camry_gp + 0x0u);
  if ((*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff93bau)))) == '\x02') {
    boot_response_timer_progress();
  }
  else if (((*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff93bau)))) == '\0') && ((*((volatile uint8_t *)camry_host_ptr((uint32_t)((camry_gp + 0xffff93bfu))))) != '\x01')) {
    iVar2 = read_ffe51010_word_1d24();
    if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6cf2))))) == '\x02' || (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6cf2))))) == '\x03') {
      uVar4 = 100000000;
    }
    else {
      uVar4 = 0xffffffff;
    }
    if (uVar4 < (uint)(iVar2 - (*((int *)camry_host_ptr((uint32_t)(puVar1 + -0x6c4c)))))) {
      boot_session_publish('\x01');
      uVar3 = read_ffe51010_word_1d24();
      (*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + -0x6c4c)))) = uVar3;
    }
  }
  return;
}

void boot_response_complete(ushort channel,uchar status)

{
  uint32_t puVar1;
  undefined4 uVar2;
  
  puVar1 = (camry_gp + 0x0u);
  if ((*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff93bbu)))) == '\x03') {
    (*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff93bcu)))) = '\0';
  }
  else {
    (*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff93bau)))) = '\0';
    uVar2 = ((void)(channel), read_ffe51010_word_1d24());
    (*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + -0x6c4c)))) = uVar2;
    if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6c43))))) == '\x01') {
      if (status == '\0') {
        set_state_three_and_enter_stop_loop_159e();
      }
      else {
        (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6c43))))) = 0;
      }
    }
  }
  return;
}

uint boot_response_copy_chunk
               (ushort channel,F33BootPduInfo *chunk,uint unused,ushort *remaining)

{
  byte bVar1;
  uint uVar2;
  uchar *puVar3;
  uint uVar4;
  uint uVar5;
  uint uVar6;
  
  bVar1 = (byte)chunk->length;
  uVar4 = (uint)bVar1;
  puVar3 = ((void *)camry_host_ptr((uint32_t)(chunk->data)));
  if (uVar4 != 0) {
    if ((*((volatile uint16_t *)camry_host_ptr((camry_gp + 0xffff98bau)))) < uVar4) {
      return 1;
    }
    uVar6 = (uint)(*((volatile uint16_t *)camry_host_ptr((camry_gp + 0xffff93a8u)))) - (uint)(*((volatile uint16_t *)camry_host_ptr((camry_gp + 0xffff98bau))));
    for (uVar2 = 0; uVar2 < uVar4; uVar2 = uVar2 + 1 & 0xff) {
      uVar5 = uVar6 & 0xffff;
      uVar6 = uVar5 + 1;
      puVar3[uVar2] = (*((uchar *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((camry_gp + 0xffff93a4u)))) + uVar5))));
    }
    (*((volatile uint16_t *)camry_host_ptr((camry_gp + 0xffff98bau)))) = (*((volatile uint16_t *)camry_host_ptr((camry_gp + 0xffff98bau)))) - bVar1;
  }
  *remaining = (*((volatile uint16_t *)camry_host_ptr((camry_gp + 0xffff98bau))));
  return 0;
}

void boot_response_submit(uchar mode,uchar *data,ushort length)

{
  undefined1 uVar1;
  uint32_t puVar2;
  uint32_t puVar3;
  F33BootInterruptEntry *pFVar4;
  int iVar5;
  undefined4 uVar6;
  
  puVar2 = (camry_gp + 0x0u);
  puVar3 = (camry_gp + 0x0u);
  pFVar4 = ((volatile F33BootInterruptEntry *)camry_host_ptr((camry_tp + 0x0u)));
  if (((*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff93bbu)))) == '\x03') || (mode != '\0')) {
    (*((volatile uint32_t *)camry_host_ptr((camry_gp + 0xffff93a4u)))) = camry_host_addr(data);
    (*((volatile uint16_t *)camry_host_ptr((camry_gp + 0xffff93a8u)))) = length;
    (*((volatile uint16_t *)camry_host_ptr((camry_gp + 0xffff98bau)))) = length;
    iVar5 = read_ffe51010_word_1d24();
    if (iVar5 == (*((int *)camry_host_ptr((uint32_t)(puVar3 + -0x6c54))))) {
      uVar1 = 1;
    }
    else {
      start_response_if_enabled_without_busy_state_2d88((*((undefined1 *)((uint8_t *)&pFVar4[(*((volatile uint16_t *)camry_host_ptr((uint32_t)(puVar3 + -0x6744)))) + 0x10d].handler + (2)))), ((uint32_t)((uint32_t)(puVar3 + -0x6c5c))));
      uVar1 = 2;
    }
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6c45))))) = uVar1;
  }
  else {
    (*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff93bau)))) = '\0';
    uVar6 = read_ffe51010_word_1d24();
    (*((undefined4 *)camry_host_ptr((uint32_t)(puVar2 + -0x6c4c)))) = uVar6;
    if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x6c43))))) == '\x01') {
      set_state_three_and_enter_stop_loop_159e();
    }
  }
  return;
}

void boot_copy_request_bytes_and_clear_append_index_67b0(undefined1 *param_1,uint param_2)

{
  uint uVar1;
  
  for (uVar1 = 0; uVar1 < (param_2 & 0xffff); uVar1 = uVar1 + 1) {
    *param_1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)((camry_gp + 0xffff98c0u) + (uint32_t)(uVar1) * 1u))));
    param_1 = param_1 + 1;
  }
  (*((volatile uint16_t *)camry_host_ptr((camry_gp + 0xffff93b8u)))) = 0;
  return;
}

undefined1 * boot_get_request_buffer_and_clear_append_index_67d0(void)

{
  (*((volatile uint16_t *)camry_host_ptr((camry_gp + 0xffff93b8u)))) = 0;
  return ((undefined *)camry_host_ptr((camry_gp + 0xffff98c0u)));
}

void boot_call_terminal_action_or_defer_until_response_67da(void)

{
  if ((*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff93bau)))) == '\0') {
    set_state_three_and_enter_stop_loop_159e();
  }
  else {
    (*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff93bdu)))) = '\x01';
  }
  return;
}

char boot_get_combined_request_response_state_67f6(void)

{
  uint32_t puVar1;
  undefined4 uVar2;
  char cVar3;
  
  puVar1 = (camry_gp + 0x0u);
  uVar2 = raise_pmr_and_return_previous_mask_721e(0xffff);
  cVar3 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6c46)))));
  if (cVar3 == '\x02') {
    cVar3 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6c45))))) + '\x02';
  }
  restore_pmr_preserving_interrupt_disable_state_7244(uVar2);
  return cVar3;
}

void boot_store_transport_control_and_refresh_idle_sample_681e(undefined1 param_1)

{
  uint32_t puVar1;
  undefined4 uVar2;
  undefined4 uVar3;
  
  puVar1 = (camry_gp + 0x0u);
  uVar2 = raise_pmr_and_return_previous_mask_721e(0xffff);
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6c41))))) = param_1;
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6c46))))) == '\0') {
    uVar3 = read_ffe51010_word_1d24();
    (*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + -0x6c4c)))) = uVar3;
  }
  restore_pmr_preserving_interrupt_disable_state_7244(uVar2);
  return;
}

void boot_communication_control_negative_response_684c(uchar param_1)

{
  boot_negative_response('(',param_1);
  return;
}

void boot_communication_control_positive_response_6860(void)

{
  (*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff92d0u)))) = 0x68;
  (*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff92d1u)))) = (*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff93c3u)))) & 0x7f;
  boot_response_submit((*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff93c3u)))) >> 7 ^ 1,((undefined *)camry_host_ptr((camry_gp + 0xffff92d0u))),2);
  return;
}

void boot_service_communication_control(ushort request_length)

{
  uint8_t stack_record_b[11];
  uint32_t puVar1;
  F33BootInterruptEntry *pFVar2;
  undefined4 uVar3;
  
  puVar1 = (camry_gp + 0x0u);
  pFVar2 = ((volatile F33BootInterruptEntry *)camry_host_ptr((camry_tp + 0x0u)));
  stack_record_b[0] = 0;
  stack_record_b[1] = 0;
  stack_record_b[2] = '\0';
  boot_copy_request_bytes_and_clear_append_index_67b0(((uint8_t *)(stack_record_b)),3);
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6cf2))))) != (*((char *)((uint8_t *)&pFVar2[0x10b].eiic + (2))))) {
    uVar3 = 0x7f;
    goto LAB_000068b8;
  }
  if (2 < request_length) {
    if ((stack_record_b[1] & 0x7f) != 1) {
      uVar3 = 0x12;
      goto LAB_000068b8;
    }
    if (request_length == 3) {
      if (stack_record_b[2] == '\x01') {
        (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6c3d))))) = stack_record_b[1];
        boot_communication_control_positive_response_6860();
        return;
      }
      uVar3 = 0x31;
      goto LAB_000068b8;
    }
  }
  uVar3 = 0x13;
LAB_000068b8:
  boot_communication_control_negative_response_684c(uVar3);
  return;
}

void return_only_stub_68fa(void)

{
  return;
}

void boot_control_dtc_setting_negative_response_68fc(uchar param_1)

{
  boot_negative_response(0x85,param_1);
  return;
}

void boot_control_dtc_setting_positive_response_6910(void)

{
  (*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff92d0u)))) = 0xc5;
  (*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff92d1u)))) = (*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff93c4u)))) & 0x7f;
  boot_response_submit((*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff93c4u)))) >> 7 ^ 1,((undefined *)camry_host_ptr((camry_gp + 0xffff92d0u))),2);
  return;
}

void boot_service_dtc_setting(ushort request_length)

{
  uint8_t stack_record_a[10];
  uint32_t puVar1;
  F33BootInterruptEntry *pFVar2;
  undefined4 uVar3;
  
  puVar1 = (camry_gp + 0x0u);
  pFVar2 = ((volatile F33BootInterruptEntry *)camry_host_ptr((camry_tp + 0x0u)));
  stack_record_a[0] = 0;
  stack_record_a[1] = 0;
  boot_copy_request_bytes_and_clear_append_index_67b0(((uint8_t *)(stack_record_a)),2);
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6cf2))))) == (*((char *)((uint8_t *)&pFVar2[0x10b].eiic + (3))))) {
    if (1 < request_length) {
      if ((stack_record_a[1] & 0x7f) != 2) {
        uVar3 = 0x12;
        goto LAB_00006966;
      }
      if (request_length == 2) {
        (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6c3c))))) = stack_record_a[1];
        boot_control_dtc_setting_positive_response_6910();
        return;
      }
    }
    uVar3 = 0x13;
  }
  else {
    uVar3 = 0x7f;
  }
LAB_00006966:
  boot_control_dtc_setting_negative_response_68fc(uVar3);
  return;
}

void return_only_stub_699a(void)

{
  return;
}

void boot_current_service_negative_response_699c(uchar param_1)

{
  boot_negative_response((*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff93c5u)))),param_1);
  return;
}

void boot_service_reject_configured(ushort request_length)

{
  uint32_t puVar1;
  undefined1 uStack_5;
  
  puVar1 = (camry_gp + 0x0u);
  boot_copy_request_bytes_and_clear_append_index_67b0(&uStack_5,1);
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6c3b))))) = uStack_5;
  boot_current_service_negative_response_699c(0x7f);
  return;
}

void boot_diagnostic_enable_from_handoff(void)

{
  int local_c;
  
  DAT_febf2bd0 = 0;
  copy_gp_words_to_destination_u8_count_1514(camry_host_addr(&local_c), 1);
  if ((local_c == 0) || (local_c == 0xff)) {
    DAT_febf2bd0 = 1;
    set_gp_event_mask_bit_guarded_14be(0);
  }
  return;
}

void boot_diagnostic_timer_services(void)

{
  if (DAT_febf2bd0 != '\0') {
    boot_diagnostic_timeout_progress();
    boot_diagnostic_timer_progress();
  }
  return;
}

void boot_diagnostic_initialize_from_handoff(void)

{
  int local_2c [8];
  
  if (DAT_febf2bd0 != '\0') {
    DAT_febf2bd1 = 0;
    DAT_febf2bd2 = 0;
    boot_reset_transport_and_sample_register_6320();
    boot_initialize_default_session_and_service_state_5086();
    boot_region_authentication_clear_activity();
    reset_memory_transfer_result_and_pending_6ea2();
    boot_block_transform_clear_activity();
    set_compare_error_and_clear_pending_6d02();
    copy_gp_words_to_destination_u8_count_1514(camry_host_addr(local_2c), 8);
    if (local_2c[0] == 0) {
      DAT_febf2bcc = 0xffffffff;
      DAT_febf2bd1 = 1;
      DAT_febf2bd2 = 0;
      prepare_and_run_relocated_flash_driver_152a();
      refresh_authentication_enable_and_clear_verified_mask_519c();
      boot_diagnostic_replay_handoff_session(camry_host_addr(local_2c));
    }
    else if (local_2c[0] == 0xff) {
      DAT_febf2bcc = 0xffffffff;
      DAT_febf2bc8 = read_ffe51010_word_1d24();
    }
  }
  return;
}

void boot_diagnostic_foreground(void)

{
  undefined4 uVar1;
  int iVar2;
  
  if (DAT_febf2bd0 != '\0') {
    boot_join_session_and_consume_transfer_foreground_51c8();
    boot_poll_program_or_memory_write_completion_6e60();
    boot_region_authentication_progress();
    boot_transfer_block_transform_progress();
    boot_transfer_compare_progress();
    uVar1 = raise_pmr_and_return_previous_mask_721e(0xffff);
    if (DAT_febf2bd1 != '\x01') {
      iVar2 = read_ffe51010_word_1d24();
      if ((((uint)(iVar2 - DAT_febf2bc8) <= DAT_febf2bcc) && (DAT_febf2bd2 == '\x01')) &&
         (iVar2 != DAT_febf2bc8)) {
        DAT_febf2bd2 = '\0';
      }
    }
    restore_pmr_preserving_interrupt_disable_state_7244(uVar1);
  }
  return;
}

void boot_programming_prepare(void)

{
  DAT_febf2bd2 = 0;
  prepare_and_run_relocated_flash_driver_152a();
  refresh_authentication_enable_and_clear_verified_mask_519c();
  DAT_febf2bd1 = 1;
  return;
}

void thunk_set_boot_flag_2b10_5158(void)

{
  set_boot_flag_2b10_5158();
  return;
}

uint boot_transport_request_admit
               (ushort channel,F33BootPduInfo *first_chunk,ushort total_length,
               ushort *remaining_capacity)

{
  uint uVar1;
  
  if (DAT_febf2bd0 == '\0') {
    uVar1 = 1;
  }
  else {
    uVar1 = boot_request_admit(channel,first_chunk,total_length,remaining_capacity);
  }
  return uVar1;
}

uint boot_transport_request_append
               (ushort channel,F33BootPduInfo *chunk,ushort *remaining_capacity)

{
  uint uVar1;
  
  uVar1 = boot_request_append(channel,chunk,remaining_capacity);
  return uVar1;
}

void boot_transport_receive_complete(ushort channel,uchar status)

{
  camry_write32((camry_sp - 4u) & ~3u, camry_gpr[31]);
  camry_sp -= 4u;
  camry_gpr[3] = camry_sp;

  (camry_gpr[6] = channel, camry_r7 = camry_gpr[7] = status, camry_gpr[31] = 0x6b86u, boot_request_receive_complete)(channel,status);
  { if (!camry_halted) { camry_gpr[31] = camry_read32((camry_sp + 0u) & ~3u); camry_sp += 4u; camry_gpr[3] = camry_sp; } return; }
}

uint boot_transport_response_copy
               (ushort channel,F33BootPduInfo *chunk,uint unused,ushort *remaining)

{
  uint uVar1;
  
  uVar1 = boot_response_copy_chunk(channel,chunk,unused,remaining);
  return uVar1;
}

void boot_transport_response_complete(ushort channel,uchar status)

{
  boot_response_complete(channel,status);
  return;
}

uint boot_transfer_crypto_initialize(void)

{
  return boot_image_crypto_initialize();
}

uint boot_block_transform_submit(ushort length,uchar *source,uchar *destination)

{
  bool bVar1;
  
  bVar1 = (*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff93deu)))) == '\0';
  if (bVar1) {
    (*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff93deu)))) = '\x01';
    (*((volatile uint32_t *)camry_host_ptr((camry_gp + 0xffff93d4u)))) = camry_host_addr(source);
    (*((volatile uint32_t *)camry_host_ptr((camry_gp + 0xffff93d8u)))) = camry_host_addr(destination);
    (*((volatile uint16_t *)camry_host_ptr((camry_gp + 0xffff93dcu)))) = length;
  }
  return (uint)!bVar1;
}

void boot_transfer_crypto_clear(void)

{
  boot_image_crypto_clear();
  return;
}

void boot_transfer_block_transform_progress(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  undefined *puVar4;
  undefined8 uVar5;
  int iVar6;
  uint uVar7;
  uchar local_1c [16];
  camry_fill_bytes(local_1c, sizeof local_1c);
  
  uVar5 = (camry_gp + 0x0u);
  puVar4 = ((undefined *)camry_host_ptr((camry_gp + 0x0u)));
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)((camry_gp + 0xffff93deu))))) != '\0') {
    uVar7 = (uint)(*((volatile uint16_t *)camry_host_ptr((uint32_t)((camry_gp + 0xffff93dcu)))));
    if (0xf < uVar7) {
      uVar7 = 0x10;
    }
    for (iVar6 = (int)uVar7 >> 4; iVar6 != 0; iVar6 = iVar6 + -1) {
      boot_image_decrypt_block((((uchar *)camry_host_ptr((*((volatile uint32_t *)camry_host_ptr((uint32_t)((int)uVar5 + -0x6c2c))))))),local_1c);
      puVar4 = ((undefined *)camry_host_ptr((uint32_t)(uVar5)));
      *(int *)(puVar4 + -0x6c2c) = *(int *)(puVar4 + -0x6c2c) + 0x10;
      iVar3 = 0;
      do {
        iVar2 = iVar3 + 1;
        (*((volatile uchar *)camry_host_ptr((*((volatile uint32_t *)(puVar4 + -0x6c28)))))) = local_1c[iVar3];
        iVar1 = iVar3 + -0xf;
        *(int *)(puVar4 + -0x6c28) = *(int *)(puVar4 + -0x6c28) + 1;
        iVar3 = iVar2;
      } while (((iVar1 < 0) || (iVar2 < 0)));
    }
    uVar7 = *(ushort *)(puVar4 + -0x6c24) - uVar7;
    *(ushort *)(puVar4 + -0x6c24) = (ushort)uVar7;
    if ((uVar7 & 0xffff) == 0) {
      puVar4[-0x6c22] = 0;
    }
  }
  return;
}

void boot_block_transform_clear_activity(void)

{
  (*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff93deu)))) = 0;
  return;
}

bool is_completion_marker_word_mismatched_6c5a(int *param_1)

{
  return *param_1 != 0x5aa5a55a;
}

uint boot_compare_submit(uchar *left,uchar *right,uint length)

{
  bool bVar1;
  
  bVar1 = (*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff93edu)))) == '\0';
  if (bVar1) {
    (*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff93ecu)))) = 1;
    (*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff93edu)))) = '\x01';
    (*((volatile uint32_t *)camry_host_ptr((camry_gp + 0xffff93e0u)))) = length;
    (*((volatile uint32_t *)camry_host_ptr((camry_gp + 0xffff93e4u)))) = camry_host_addr(left);
    (*((volatile uint32_t *)camry_host_ptr((camry_gp + 0xffff93e8u)))) = camry_host_addr(right);
  }
  return (uint)!bVar1;
}

void boot_transfer_compare_progress(void)

{
  bool bVar1;
  uint32_t puVar2;
  undefined4 uVar3;
  uint uVar4;
  uint uVar5;
  
  puVar2 = (camry_gp + 0x0u);
  if ((*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff93edu)))) != '\0') {
    uVar5 = 0;
    uVar4 = (*((volatile uint32_t *)camry_host_ptr((camry_gp + 0xffff93e0u))));
    if (0xf < (*((volatile uint32_t *)camry_host_ptr((camry_gp + 0xffff93e0u))))) {
      uVar4 = 0x10;
    }
    for (; uVar5 < uVar4; uVar5 = uVar5 + 1) {
      if ((*((char *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((camry_gp + 0xffff93e4u)))) + uVar5)))) != (*((char *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((camry_gp + 0xffff93e8u)))) + uVar5))))) {
        (*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff93edu)))) = 0;
        return;
      }
    }
    (*((volatile uint32_t *)camry_host_ptr((camry_gp + 0xffff93e4u)))) = (*((volatile uint32_t *)camry_host_ptr((camry_gp + 0xffff93e4u)))) + uVar4;
    (*((volatile uint32_t *)camry_host_ptr((camry_gp + 0xffff93e8u)))) = (*((volatile uint32_t *)camry_host_ptr((camry_gp + 0xffff93e8u)))) + uVar4;
    uVar5 = (*((volatile uint32_t *)camry_host_ptr((camry_gp + 0xffff93e0u)))) - uVar4;
    bVar1 = (*((volatile uint32_t *)camry_host_ptr((camry_gp + 0xffff93e0u)))) == uVar4;
    (*((volatile uint32_t *)camry_host_ptr((camry_gp + 0xffff93e0u)))) = uVar5;
    if (bVar1) {
      uVar3 = raise_pmr_and_return_previous_mask_721e(0xffff);
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x6c14))))) = 0;
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x6c13))))) = 0;
      restore_pmr_preserving_interrupt_disable_state_7244(uVar3);
    }
  }
  return;
}

void set_compare_error_and_clear_pending_6d02(void)

{
  (*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff93ecu)))) = 1;
  (*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff93edu)))) = 0;
  return;
}

uint boot_submit_descriptor_program_and_append_data_6d10(uint *param_1,uchar *param_2)

{
  uint uVar1;
  
  uVar1 = boot_submit_program_stream(*param_1,(uint)(ushort)param_1[1]);
  if (uVar1 == 0) {
    boot_append_program_input(param_2,(ushort)param_1[1]);
  }
  return uVar1;
}

undefined4 copy_bytes_to_descriptor_address_6d3a(int *param_1,int param_2)

{
  int iVar1;
  int iVar2;
  
  iVar2 = *param_1;
  for (iVar1 = 0;
      (int)(iVar1 - (uint)*(ushort *)(param_1 + 1)) < 0 !=
      (iVar1 < 0 && -1 < (int)(iVar1 - (uint)*(ushort *)(param_1 + 1))); iVar1 = iVar1 + 1) {
    (*((undefined1 *)camry_host_ptr((uint32_t)(iVar1 + iVar2)))) = (*((undefined1 *)camry_host_ptr((uint32_t)(iVar1 + param_2))));
  }
  return 0;
}

int boot_submit_program_or_memory_write_when_idle_6d5e(undefined4 *param_1,undefined4 param_2)

{
  undefined1 uVar1;
  undefined4 uVar2;
  uint32_t puVar3;
  undefined4 uVar4;
  int iVar5;
  
  puVar3 = (camry_gp + 0x0u);
  iVar5 = 1;
  uVar4 = raise_pmr_and_return_previous_mask_721e(0xffff);
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6c05))))) != '\x01') {
    if ((*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 9)))) < 2) {
      if ((*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 9)))) == 0) {
        iVar5 = boot_submit_descriptor_program_and_append_data_6d10(param_1, ((uchar *)camry_host_ptr((uint32_t)(param_2))));
      }
      else {
        iVar5 = copy_bytes_to_descriptor_address_6d3a(param_1,param_2);
      }
    }
    if (iVar5 == 0) {
      uVar2 = *param_1;
      (*((undefined4 *)camry_host_ptr((uint32_t)(puVar3 + -0x6c0c)))) = 0;
      (*((undefined4 *)camry_host_ptr((uint32_t)(puVar3 + -0x6c10)))) = uVar2;
      uVar1 = (*((undefined1 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 9))));
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6c07))))) = 0;
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6c08))))) = uVar1;
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6c06))))) = 1;
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6c05))))) = 1;
    }
  }
  restore_pmr_preserving_interrupt_disable_state_7244(uVar4);
  return iVar5;
}

undefined4 copy_descriptor_bytes_to_output_mode_zero_6dc0(int *param_1,int param_2)

{
  int iVar1;
  int iVar2;
  
  iVar2 = *param_1;
  for (iVar1 = 0;
      (int)(iVar1 - (uint)*(ushort *)(param_1 + 1)) < 0 !=
      (iVar1 < 0 && -1 < (int)(iVar1 - (uint)*(ushort *)(param_1 + 1))); iVar1 = iVar1 + 1) {
    (*((undefined1 *)camry_host_ptr((uint32_t)(iVar1 + param_2)))) = (*((undefined1 *)camry_host_ptr((uint32_t)(iVar1 + iVar2))));
  }
  return 0;
}

undefined4 copy_descriptor_bytes_to_output_mode_one_6de4(int *param_1,int param_2)

{
  int iVar1;
  int iVar2;
  
  iVar2 = *param_1;
  for (iVar1 = 0;
      (int)(iVar1 - (uint)*(ushort *)(param_1 + 1)) < 0 !=
      (iVar1 < 0 && -1 < (int)(iVar1 - (uint)*(ushort *)(param_1 + 1))); iVar1 = iVar1 + 1) {
    (*((undefined1 *)camry_host_ptr((uint32_t)(iVar1 + param_2)))) = (*((undefined1 *)camry_host_ptr((uint32_t)(iVar1 + iVar2))));
  }
  return 0;
}

undefined4 boot_read_descriptor_bytes_when_idle_6e08(int param_1,undefined4 param_2)

{
  uint32_t puVar1;
  undefined4 uVar2;
  undefined4 uVar3;
  
  puVar1 = (camry_gp + 0x0u);
  uVar3 = 1;
  uVar2 = raise_pmr_and_return_previous_mask_721e(0xffff);
  if (((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6c05))))) != '\x01') && ((*((byte *)camry_host_ptr((uint32_t)(param_1 + 9)))) < 2)) {
    if ((*((byte *)camry_host_ptr((uint32_t)(param_1 + 9)))) == 0) {
      uVar3 = copy_descriptor_bytes_to_output_mode_zero_6dc0(((int *)camry_host_ptr((uint32_t)(param_1))),  param_2);
    }
    else {
      uVar3 = copy_descriptor_bytes_to_output_mode_one_6de4(((int *)camry_host_ptr((uint32_t)(param_1))), param_2);
    }
  }
  restore_pmr_preserving_interrupt_disable_state_7244(uVar2);
  return uVar3;
}

void clear_memory_transfer_result_and_pending_6e4a(void)

{
  (*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff93fau)))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff93fbu)))) = 0;
  return;
}

void set_memory_transfer_error_and_clear_pending_6e54(void)

{
  (*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff93fau)))) = 1;
  (*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff93fbu)))) = 0;
  return;
}

undefined4 boot_poll_program_or_memory_write_completion_6e60(void)

{
  uint32_t puVar1;
  undefined4 uVar2;
  
  puVar1 = (camry_gp + 0x0u);
  uVar2 = raise_pmr_and_return_previous_mask_721e(0xffff);
  if (((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6c05))))) != '\x01') || (1 < (byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6c08))))))) goto LAB_00006e98;
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6c08))))) == 0) {
    if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-27999))))) == '\x01') goto LAB_00006e98;
    if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-28000))))) != '\0') {
      set_memory_transfer_error_and_clear_pending_6e54();
      goto LAB_00006e98;
    }
  }
  clear_memory_transfer_result_and_pending_6e4a();
LAB_00006e98:
  restore_pmr_preserving_interrupt_disable_state_7244(uVar2);
  return uVar2;
}

void reset_memory_transfer_result_and_pending_6ea2(void)

{
  (*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff93fau)))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff93fbu)))) = 0;
  return;
}

uint boot_authentication_crypto_initialize(void)

{
  return boot_image_crypto_initialize();
}

uint boot_region_authentication_submit(uint start,uint length)

{
  uint32_t puVar1;
  uint uVar2;
  uint uVar3;
  
  puVar1 = (camry_gp + 0x0u);
  uVar3 = 1;
  if (((*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff93fdu)))) == '\0') &&
     (uVar2 = boot_image_authentication_begin(start,length), uVar2 == 0)) {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6c04))))) = 1;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6c03))))) = 1;
    uVar3 = 0;
  }
  return uVar3;
}

void boot_region_authentication_progress(void)

{
  camry_write32((camry_sp - 4u) & ~3u, camry_gpr[31]);
  camry_sp -= 4u;
  camry_gpr[3] = camry_sp;

  uint32_t puVar1;
  uint uVar2;
  
  puVar1 = (camry_gp + 0x0u);
  if (((*((volatile uint8_t *)camry_host_ptr((uint32_t)((camry_gp + 0xffff93fdu))))) != '\0') && (uVar2 = (camry_gpr[31] = 0x6ef0u, boot_image_authentication_step)(), uVar2 != 2)) {
    if (uVar2 == 0) {
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6c04))))) = 0;
    }
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6c03))))) = 0;
  }
  { if (!camry_halted) { camry_gpr[31] = camry_read32((camry_sp + 0u) & ~3u); camry_sp += 4u; camry_gpr[3] = camry_sp; } return; }
}

void boot_region_authentication_clear_contexts(void)

{
  boot_image_crypto_clear();
  return;
}

void boot_region_authentication_clear_activity(void)

{
  (*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff93fcu)))) = 1;
  (*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff93fdu)))) = 0;
  return;
}

uint boot_security_generate_challenge(uchar *challenge_out)

{
  int iVar1;
  int iVar2;
  uchar uVar3;
  F33BootInterruptEntry *pFVar4;
  int iVar5;
  uint32_t puVar6;
  F33BootInterruptEntry *pFVar7;
  uint uVar8;
  int iVar9;
  F33BootAes128CtrContext *context;
  byte bVar10;
  uint unaff_r28;
  uchar *pFVar11;
  uchar local_28 [16];
  
  puVar6 = (camry_gp + 0x0u);
  pFVar7 = ((volatile F33BootInterruptEntry *)camry_host_ptr((camry_tp + 0x0u)));
  bVar10 = 0;
  do {
    fill_buffer_with_register_samples_be16_48d2(local_28,0x10);
    context = ((F33BootAes128CtrContext *)camry_host_ptr((uint32_t)(puVar6 + -0x69f4)));
    boot_security_initialize_candidate_context(local_28,'\x10',context);
    uVar8 = boot_security_generate_candidate_block(challenge_out,context);
    boot_security_clear_candidate_context(context);
    if (uVar8 == 0) {
      pFVar4 = pFVar7 + 0x120;
      if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(-0x674c))))) != '\0') {
        pFVar4 = pFVar7 + 0x122;
      }
      for (iVar5 = 0; iVar9 = iVar5 - (uint)*((byte *)pFVar4 + 12),
          ((iVar9 < 0) || (iVar5 < 0)); iVar5 = iVar5 + 1) {
        pFVar11 = (uchar *)camry_host_ptr(((uint32_t *)pFVar4)[iVar5]);
        iVar9 = 0;
        while ((uchar)challenge_out[iVar9] == *pFVar11) {
          pFVar11 = pFVar11 + 1;
          iVar2 = iVar9 + 1;
          iVar1 = iVar9 + -0xf;
          iVar9 = iVar2;
          if (iVar1 < 0 == (iVar2 < 0 && -1 < iVar1)) goto LAB_00006fa2;
        }
        unaff_r28 = 0;
      }
    }
    else {
LAB_00006fa2:
      unaff_r28 = 1;
      bVar10 = bVar10 + 1;
    }
    if ((unaff_r28 != 1) || (1 < bVar10)) {
      iVar5 = 0;
      if (unaff_r28 == 0) {
        do {
          uVar3 = *challenge_out;
          challenge_out = challenge_out + 1;
          iVar1 = iVar5 + 1;
          iVar9 = iVar5 + -0xf;
          (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(iVar5 + -0x6ac8))))) = uVar3;
          iVar5 = iVar1;
        } while (((iVar9 < 0) || (iVar1 < 0)));
        (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(-0x674c))))) = 1;
      }
      else {
        do {
          iVar1 = iVar5 + 1;
          *challenge_out = local_28[iVar5];
          challenge_out = challenge_out + 1;
          iVar9 = iVar5 + -0xf;
          iVar5 = iVar1;
        } while (((iVar9 < 0) || (iVar1 < 0)));
      }
      return unaff_r28;
    }
  } while( true );
}

uint32_t boot_security_decrypt_client_material(uchar *client_material,uchar *intermediate_key)

{
  uint32_t camry_r10_result;
  (camry_r10_result = boot_aes128_initialize_context
            (boot_security_client_decryption_key, '\x10', ((F33BootAes128Context *)camry_host_ptr((uint32_t)(((camry_gp + 0xffff9548u)))))));
  (camry_r10_result = boot_aes128_decrypt_block
            (client_material, intermediate_key, '\x10', ((F33BootAes128Context *)camry_host_ptr((uint32_t)(((camry_gp + 0xffff9548u)))))));
  boot_aes128_clear_context(((F33BootAes128Context *)camry_host_ptr((uint32_t)(((camry_gp + 0xffff9548u))))));
  return camry_r10_result;
}
