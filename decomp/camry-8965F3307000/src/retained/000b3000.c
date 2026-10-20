#include "common.h"

void set_request_47_for_service_states_zero_two_three_b301e(void)

{
  if (((DAT_febeb3cb == '\x02') || (DAT_febeb3cb == '\x03')) || (DAT_febeb3cb == '\0')) {
    set_indexed_request_and_clear_complement_b15ac(0x2f);
  }
  return;
}

void publish_service_terminal_result_and_clear_selected_mode_bit_b303e(void)

{
  uint32_t puVar1;
  undefined4 uVar2;
  undefined4 uVar3;
  byte bVar4;
  
  puVar1 = 0xfebeb800u;
  if (DAT_febeb3d5 == '\x01') {
    uVar2 = 0xc;
    bVar4 = 4;
  }
  else {
    bVar4 = 0x10;
    if (DAT_febeb3d5 == '\x02') {
      bVar4 = 8;
      uVar2 = 0xe;
    }
    else {
      uVar2 = 0xf;
    }
  }
  if (DAT_febeb3cb == '\x02') {
    uVar3 = 0;
  }
  else {
    uVar3 = 0x20;
    if (DAT_febeb3cb == '\0') {
      uVar3 = 0x30;
    }
  }
  thunk_publish_routine_or_pending_write_terminal_result_4d0a4(uVar2,uVar3);
  stop_service_phase_and_reset_output_requests_b856a();
  set_byte_febeb3d1_b83f2(0);
  set_byte_febeb3d7_b85a8(0);
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6f2))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6f2))))) & ~bVar4;
  return;
}

void advance_service_family(void)

{
  uchar request_id;
  ushort mode;
  uint uVar1;
  
  if (DAT_febeb11a != 0x500) {
    if (DAT_febeb11a == 0x512) {
      set_request_43_on_status44_and_completion_marker_b2f8c();
      uVar1 = probe_pending_mode_request('+');
      if (uVar1 == 1) {
        clear_mode_bit0_and_reset_6958_state_b2fb4();
        publish_live_application_mode(0x500);
      }
      request_id = '+';
    }
    else if (DAT_febeb11a == 0x520) {
      set_request_47_for_service_states_zero_two_three_b301e();
      uVar1 = probe_pending_mode_request('/');
      if (uVar1 == 1) {
        publish_service_terminal_result_and_clear_selected_mode_bit_b303e();
        publish_live_application_mode(0x500);
      }
      request_id = '/';
    }
    else {
      if (DAT_febeb11a != 0x522) {
        return;
      }
      set_request_45_on_status44_and_completion_marker_b2fc6();
      uVar1 = probe_pending_mode_request('-');
      if (uVar1 == 1) {
        publish_routine8_completion_and_clear_mode_bit1_b2fee();
        publish_live_application_mode(0x500);
      }
      request_id = '-';
    }
    goto LAB_000b317a;
  }
  select_request_from_mode_bits_and_completion_markers_b2ee6();
  uVar1 = probe_pending_mode_request('*');
  if (uVar1 == 1) {
    mode = 0x512;
LAB_000b311e:
    publish_live_application_mode(mode);
  }
  else {
    uVar1 = probe_pending_mode_request(',');
    if (uVar1 == 1) {
      thunk_latch_b1a7_and_clear_requests_zero_one_b77f4();
      mode = 0x522;
      goto LAB_000b311e;
    }
    uVar1 = probe_pending_mode_request('.');
    if (uVar1 == 1) {
      initialize_service_engine_kind_from_mode_bits_b2f5e();
      mode = 0x520;
      goto LAB_000b311e;
    }
  }
  acknowledge_selected_mode_request('*');
  acknowledge_selected_mode_request(',');
  request_id = '.';
LAB_000b317a:
  acknowledge_selected_mode_request(request_id);
  return;
}

void invoke_record100_initialization_for_mode_bit1_b3182(void)

{
  if ((DAT_febeb10e & 2) != 0) {
    thunk_invalidate_learned_quad_record_with_default_payload_3599e();
  }
  return;
}

void report_pending_service_aborts(void)

{
  byte bVar1;
  byte bVar2;
  byte bVar3;
  char cVar4;
  char cVar5;
  undefined4 uVar6;
  
  cVar5 = DAT_febeb3dd;
  cVar4 = DAT_febeb3dc;
  bVar1 = DAT_febeb10e & 4;
  bVar2 = DAT_febeb10e & 8;
  bVar3 = DAT_febeb10e & 0x10;
  if ((DAT_febeb10e >> 1 & 1) != 0) {
    thunk_clear_quad_status_if_88_35ad6();
    thunk_publish_routine_or_pending_write_terminal_result_4d0a4(8,0x20);
  }
  if (bVar1 != 0) {
    uVar6 = 0x20;
    if (cVar5 == 'Z') {
      uVar6 = 0x30;
    }
    thunk_publish_routine_or_pending_write_terminal_result_4d0a4(0xc,uVar6);
  }
  if (bVar2 != 0) {
    thunk_publish_routine_or_pending_write_terminal_result_4d0a4(0xe,0x20);
  }
  if (bVar3 != 0) {
    uVar6 = 0x20;
    if (cVar4 == 'Z') {
      uVar6 = 0x30;
    }
    thunk_publish_routine_or_pending_write_terminal_result_4d0a4(0xf,uVar6);
  }
  return;
}

void exit_service_family(void)

{
  report_pending_service_aborts();
  stop_service_phase_and_reset_output_requests_b856a();
  set_byte_febeb3d1_b83f2(0);
  set_byte_febeb3d7_b85a8(0);
  publish_requests_zero_one_when_b1a4_clear_b7810();
  return;
}

int queue_application_service(uchar service_id)

{
  uint32_t puVar1;
  uint32_t puVar2;
  undefined4 uVar3;
  ushort uVar4;
  uint uVar5;
  int iVar6;
  
  puVar2 = 0xfebeb800u;
  puVar1 = 0xfebeb800u;
  uVar5 = (uint)service_id;
  uVar4 = DAT_febeb11a & 0xff00;
  if (DAT_febeb11a < 0x600) {
    if (uVar5 == 1) {
      uVar3 = raise_priority_mask_and_return_previous_d1da0(0xffc0);
      if (((byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6f2))))) >> 1 & 1) == 0) {
        iVar6 = -1;
        (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6f2))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6f2))))) | 2;
        if ((*((int *)camry_host_ptr((uint32_t)(puVar1 + 0x3a08)))) != 0) {
          set_indexed_request_and_clear_complement_b15ac(6);
        }
      }
      else {
        iVar6 = -7;
      }
      restore_priority_mask_preserving_interrupt_enable_d1dc6(uVar3);
      return iVar6;
    }
    if ((uVar5 == 2) || (uVar5 == 3)) {
      set_byte_febeb3d1_b83f2(0x5a);
    }
    else {
      if (uVar5 != 4) goto LAB_000b3282;
      set_byte_febeb3d7_b85a8(0x5a);
    }
    clear_indexed_request_and_set_complement_b14d2(4);
    uVar5 = 1 << (uVar5 & 0x1f);
    uVar3 = raise_priority_mask_and_return_previous_d1da0(0xffc0);
    if ((uVar5 & 0xff & (uint)(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x6f2)))))) == 0) {
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x6f2))))) = (byte)uVar5 | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x6f2)))));
      iVar6 = -1;
    }
    else {
      iVar6 = -7;
    }
    restore_priority_mask_preserving_interrupt_enable_d1dc6(uVar3);
    if ((iVar6 == -1) && (uVar4 != 0x500)) {
      set_indexed_request_and_clear_complement_b15ac(6);
    }
  }
  else {
LAB_000b3282:
    iVar6 = -6;
  }
  return iVar6;
}

uint select_service_join_after_mode200(void)

{
  uint uVar1;
  
  if (DAT_febef208 == 0) {
    uVar1 = 2;
  }
  else {
    uVar1 = 1;
  }
  DAT_febeb10f = (char)uVar1;
  return uVar1;
}

void return_only_stub_b32f2(void)

{
  return;
}

void enter_mode600(void)

{
  DAT_febeb110 = 0;
  return;
}

void exit_mode600(void)

{
  DAT_febeb111 = 0;
  cancel_mode600_stimulus_fit();
  return;
}

void return_only_stub_b33d8(void)

{
  return;
}

void enter_mode900(void)

{
  set_output_request_word('\0',0x70017001);
  set_output_request_word('\x01',0x70017001);
  set_channel_owner_request('\0',0x20002);
  set_channel_owner_request('\x01',0x20002);
  thunk_set_secondary_channel_request_bounded5_56e66(0, ((uint32_t)(0x20002u)));
  thunk_set_secondary_channel_request_bounded5_56e66(1, ((uint32_t)(0x20002u)));
  return;
}

void mode_hook_b342a(void)

{
  return;
}

void return_only_stub_b342c(void)

{
  return;
}

void return_only_stub_b342e(void)

{
  return;
}

void debounce_and_latch_paired_status_codes_b3430(void)

{
  char cVar1;
  char cVar2;
  char cVar3;
  ushort uVar4;
  ushort uVar5;
  uint32_t puVar6;
  uchar uVar7;
  uchar uVar8;
  char cVar9;
  char cVar10;
  char cVar11;
  char cVar12;
  ushort uVar13;
  
  puVar6 = 0xfebeb800u;
  uVar7 = get_grouped_status_byte(0xc);
  uVar8 = get_grouped_status_byte(0x1d);
  cVar11 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(0x3956)))));
  cVar2 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(0x3850)))));
  uVar5 = (*((ushort *)camry_host_ptr((uint32_t)(puVar6 + -0x6ce))));
  cVar9 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(-0x6d1)))));
  cVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(-0x6d2)))));
  cVar10 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(-0x6dc)))));
  cVar12 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(-0x6de)))));
  uVar13 = (ushort)(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(-0x6e0)))));
  if (((((uVar7 == '\0' && uVar8 == '\0') && ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(0x3800))))) == '\0')) && ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(0x384f))))) == '\0'))
      && (cVar12 == cVar2)) &&
     ((cVar3 = cVar9, uVar4 = DAT_000aef40, cVar2 != '\a' ||
      ((cVar2 = cVar12, (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(0x3957))))) == '\0' &&
       (cVar3 = cVar1, uVar4 = DAT_000aef42, cVar1 == cVar11)))))) {
    cVar11 = cVar1;
    if (uVar13 == 0) {
      if (uVar5 < uVar4) {
        uVar5 = uVar5 + 1;
      }
      else {
        cVar10 = cVar12;
        cVar9 = cVar3;
        uVar13 = 0x5a;
      }
    }
    else {
      uVar5 = 0;
    }
  }
  else {
    cVar12 = cVar2;
    uVar5 = 0;
    uVar13 = uVar5;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(-0x6e0))))) = (char)uVar13;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(-0x6de))))) = cVar12;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(-0x6dc))))) = cVar10;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(-0x6d2))))) = cVar11;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(-0x6d1))))) = cVar9;
  (*((ushort *)camry_host_ptr((uint32_t)(puVar6 + -0x6ce)))) = uVar5;
  return;
}

void debounce_and_latch_single_status_code_b34d4(void)

{
  char cVar1;
  ushort uVar2;
  uint32_t puVar3;
  uchar uVar4;
  char cVar5;
  char cVar6;
  char cVar7;
  
  puVar3 = 0xfebeb800u;
  uVar4 = get_grouped_status_byte(0xc);
  cVar6 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(0x3941)))));
  cVar7 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6da)))));
  cVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6d9)))));
  cVar5 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6d8)))));
  uVar2 = (*((ushort *)camry_host_ptr((uint32_t)(puVar3 + -0x6cc))));
  if ((((uVar4 == '\0') && ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(0x3800))))) == '\0')) && ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(0x384f))))) == '\0')) &&
     (cVar1 == cVar6)) {
    cVar6 = cVar1;
    if (cVar7 == '\0') {
      if (uVar2 < DAT_000aef44) {
        uVar2 = uVar2 + 1;
      }
      else {
        cVar7 = 'Z';
        cVar5 = cVar1;
      }
    }
    else {
      uVar2 = 0;
    }
  }
  else {
    uVar2 = 0;
    cVar7 = '\0';
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6da))))) = cVar7;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6d9))))) = cVar6;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x6d8))))) = cVar5;
  (*((ushort *)camry_host_ptr((uint32_t)(puVar3 + -0x6cc)))) = uVar2;
  return;
}

void debounce_f14a_f14b_snapshot_b3538(void)

{
  char cVar1;
  char cVar2;
  char cVar3;
  ushort uVar4;
  ushort uVar5;
  uint32_t puVar6;
  uchar uVar7;
  uchar uVar8;
  char cVar9;
  char cVar10;
  char cVar11;
  char cVar12;
  ushort uVar13;
  
  puVar6 = 0xfebeb800u;
  uVar7 = get_grouped_status_byte(0xc);
  uVar8 = get_grouped_status_byte(0x15);
  cVar11 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(0x394b)))));
  cVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(0x394a)))));
  uVar5 = (*((ushort *)camry_host_ptr((uint32_t)(puVar6 + -0x6ca))));
  cVar9 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(-0x6d3)))));
  cVar2 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(-0x6d4)))));
  cVar10 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(-0x6d5)))));
  cVar12 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(-0x6d6)))));
  uVar13 = (ushort)(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(-0x6d7)))));
  if (((((uVar7 == '\0' && uVar8 == '\0') && ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(0x3800))))) == '\0')) && ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(0x384f))))) == '\0'))
      && (cVar12 == cVar1)) &&
     ((cVar3 = cVar9, uVar4 = DAT_000aef46, cVar1 != '\t' ||
      ((cVar1 = cVar12, (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(0x38c2))))) == '\0' &&
       (cVar3 = cVar2, uVar4 = DAT_000aef48, cVar2 == cVar11)))))) {
    cVar11 = cVar2;
    if (uVar13 == 0) {
      if (uVar5 < uVar4) {
        uVar5 = uVar5 + 1;
      }
      else {
        cVar10 = cVar12;
        cVar9 = cVar3;
        uVar13 = 0x5a;
      }
    }
    else {
      uVar5 = 0;
    }
  }
  else {
    cVar12 = cVar1;
    uVar5 = 0;
    uVar13 = uVar5;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(-0x6d7))))) = (char)uVar13;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(-0x6d6))))) = cVar12;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(-0x6d5))))) = cVar10;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(-0x6d4))))) = cVar11;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(-0x6d3))))) = cVar9;
  (*((ushort *)camry_host_ptr((uint32_t)(puVar6 + -0x6ca)))) = uVar5;
  return;
}

void classify_latched_state_using_b12f_b35dc(char param_1,char param_2,char param_3)

{
  uint uVar1;
  
  uVar1 = (uint)DAT_febeb124;
  if (((DAT_febeb120 != 'Z') || (param_1 != '\0')) && ((DAT_febeb126 != 'Z' || (param_2 != '\0'))))
  {
    if (DAT_febeb129 != 'Z') {
      return;
    }
    if (param_3 != '\0') {
      return;
    }
  }
  if (uVar1 == 0) {
    if (DAT_febeb128 == '\0') {
      if ((DAT_febeb12b == '\0') || ((DAT_febeb12b == '\t' && (DAT_febeb12d == '\0'))))
      goto LAB_000b367e;
    }
    else if (DAT_febeb128 != '\x01' && DAT_febeb128 != '\x02') {
      return;
    }
    DAT_febeb121 = 0x22;
  }
  else {
    if (((uVar1 == 2) || (uVar1 == 4)) || ((uVar1 == 7 && (DAT_febeb12f == '\x01')))) {
      DAT_febeb121 = 0x11;
      return;
    }
    if ((((uVar1 != 1) && (uVar1 != 3)) && (1 < uVar1 - 5)) &&
       ((uVar1 - 5 != 2 || (DAT_febeb12f != '\x02')))) {
      if (uVar1 == 7) {
        if (DAT_febeb12f != '\x03') {
          return;
        }
      }
      else if ((uVar1 != 8) && (uVar1 != 10 && uVar1 != 0xb)) {
        return;
      }
      DAT_febeb121 = 0x33;
      return;
    }
LAB_000b367e:
    DAT_febeb121 = 0;
  }
  return;
}

void debounce_f050_f0a1_snapshot_b3686(void)

{
  char cVar1;
  char cVar2;
  char cVar3;
  ushort uVar4;
  ushort uVar5;
  uint32_t puVar6;
  uchar uVar7;
  uchar uVar8;
  char cVar9;
  char cVar10;
  char cVar11;
  char cVar12;
  ushort uVar13;
  
  puVar6 = 0xfebeb800u;
  uVar7 = get_grouped_status_byte(0xc);
  uVar8 = get_grouped_status_byte(0x1c);
  cVar11 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(0x38a1)))));
  cVar2 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(0x3850)))));
  uVar5 = (*((ushort *)camry_host_ptr((uint32_t)(puVar6 + -0x6ce))));
  cVar9 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(-0x6db)))));
  cVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(-0x6dd)))));
  cVar10 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(-0x6dc)))));
  cVar12 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(-0x6de)))));
  uVar13 = (ushort)(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(-0x6e0)))));
  if (((((uVar7 == '\0' && uVar8 == '\0') && ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(0x3800))))) == '\0')) && ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(0x384f))))) == '\0'))
      && (cVar12 == cVar2)) &&
     ((cVar3 = cVar9, uVar4 = DAT_000aef40, cVar2 != '\a' ||
      ((cVar2 = cVar12, (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(0x38a0))))) == '\0' &&
       (cVar3 = cVar1, uVar4 = DAT_000aef42, cVar1 == cVar11)))))) {
    cVar11 = cVar1;
    if (uVar13 == 0) {
      if (uVar5 < uVar4) {
        uVar5 = uVar5 + 1;
      }
      else {
        cVar10 = cVar12;
        cVar9 = cVar3;
        uVar13 = 0x5a;
      }
    }
    else {
      uVar5 = 0;
    }
  }
  else {
    cVar12 = cVar2;
    uVar5 = 0;
    uVar13 = uVar5;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(-0x6e0))))) = (char)uVar13;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(-0x6de))))) = cVar12;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(-0x6dc))))) = cVar10;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(-0x6dd))))) = cVar11;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(-0x6db))))) = cVar9;
  (*((ushort *)camry_host_ptr((uint32_t)(puVar6 + -0x6ce)))) = uVar5;
  return;
}

void classify_latched_state_using_b125_b372a(char param_1,char param_2,char param_3)

{
  uint uVar1;
  
  uVar1 = (uint)DAT_febeb124;
  if (((DAT_febeb120 != 'Z') || (param_1 != '\0')) && ((DAT_febeb126 != 'Z' || (param_2 != '\0'))))
  {
    if (DAT_febeb129 != 'Z') {
      return;
    }
    if (param_3 != '\0') {
      return;
    }
  }
  if (uVar1 == 0) {
    if (DAT_febeb128 == '\0') {
      if ((DAT_febeb12b == '\0') || ((DAT_febeb12b == '\t' && (DAT_febeb12d == '\0'))))
      goto LAB_000b37d2;
    }
    else if (DAT_febeb128 != '\x01' && DAT_febeb128 != '\x02') {
      return;
    }
    DAT_febeb121 = 0x22;
  }
  else {
    if (((uVar1 == 2) || (uVar1 == 4)) ||
       ((uVar1 == 7 &&
        (((DAT_febeb125 == '\x01' || (DAT_febeb125 == '\x03')) || (DAT_febeb125 == '\x05')))))) {
      DAT_febeb121 = 0x11;
      return;
    }
    if ((((uVar1 != 1) && (uVar1 != 3)) && (1 < uVar1 - 5)) &&
       ((uVar1 - 5 != 2 ||
        (((DAT_febeb125 != '\x02' && (DAT_febeb125 != '\x04')) && (DAT_febeb125 != '\b')))))) {
      if ((uVar1 != 8) && (uVar1 != 10 && uVar1 != 0xb)) {
        return;
      }
      DAT_febeb121 = 0x33;
      return;
    }
LAB_000b37d2:
    DAT_febeb121 = 0;
  }
  return;
}

void select_snapshot_debounce_classification_path_b37da(void)

{
  undefined1 uVar1;
  undefined1 uVar2;
  undefined1 uVar3;
  char cVar4;
  uint32_t puVar5;
  uchar uVar6;
  uchar uVar7;
  char cVar8;
  
  cVar4 = DAT_febeb130;
  uVar3 = DAT_febeb129;
  uVar2 = DAT_febeb126;
  uVar1 = DAT_febeb120;
  puVar5 = 0xfebeb800u;
  uVar6 = get_grouped_status_byte(0x1c);
  uVar7 = get_grouped_status_byte(0x1d);
  if ((uVar6 == '\0' && uVar7 == '\0') && ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(0x3800))))) == '\0')) {
    if (((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(0x38a0))))) == '\0') && (cVar8 = '\0', (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(0x3968))))) != '\x03')) goto LAB_000b3844;
    if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(0x3957))))) != '\0') goto LAB_000b3826;
    cVar8 = '\x01';
  }
  else {
LAB_000b3826:
    cVar8 = cVar4;
    if (cVar4 != '\x01') {
LAB_000b3844:
      debounce_f050_f0a1_snapshot_b3686();
      debounce_and_latch_single_status_code_b34d4();
      debounce_f14a_f14b_snapshot_b3538();
      classify_latched_state_using_b125_b372a(uVar1,uVar2,uVar3);
      goto LAB_000b385a;
    }
  }
  debounce_and_latch_paired_status_codes_b3430();
  debounce_and_latch_single_status_code_b34d4();
  debounce_f14a_f14b_snapshot_b3538();
  classify_latched_state_using_b12f_b35dc(uVar1,uVar2,uVar3);
LAB_000b385a:
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x6d0))))) = cVar8;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x6cf))))) = cVar4;
  return;
}

void initialize_aef4c_scale_factors_b3866(void)

{
  uint uVar1;
  
  DAT_febeb13a = 0;
  uVar1 = (uint)DAT_000aef4c;
  if (uVar1 != 0) {
    DAT_febeb13a = (undefined2)(0x10000000 / uVar1);
  }
  DAT_febeb138 = DAT_000aef4c;
  DAT_febeb13c = 0x564e;
  if (uVar1 != 0) {
    DAT_febeb13c = (undefined2)(0x2774564e / uVar1);
  }
  DAT_febeb140 = DAT_febeb13c;
  DAT_febeb13e = (undefined2)((uVar1 << 0xe) / 0x9dd1);
  DAT_febeb142 = DAT_febeb13e;
  return;
}

void reload_aef4c_scale_factors_b389c(void)

{
  uint uVar1;
  
  DAT_febeb13a = 0;
  uVar1 = (uint)DAT_000aef4c;
  if (uVar1 != 0) {
    DAT_febeb13a = (undefined2)(0x10000000 / uVar1);
  }
  DAT_febeb138 = DAT_000aef4c;
  DAT_febeb13c = 0x564e;
  if (uVar1 != 0) {
    DAT_febeb13c = (undefined2)(0x2774564e / uVar1);
  }
  DAT_febeb140 = DAT_febeb13c;
  DAT_febeb13e = (undefined2)((uVar1 << 0xe) / 0x9dd1);
  DAT_febeb142 = DAT_febeb13e;
  return;
}

undefined4 reload_aef4c_scale_factors_guarded_b38d2(void)

{
  ushort uVar1;
  uint32_t puVar2;
  undefined4 uVar3;
  undefined2 uVar4;
  undefined2 uVar5;
  uint uVar6;
  
  uVar1 = DAT_000aef4c;
  puVar2 = 0xfebeb800u;
  uVar6 = (uint)DAT_000aef4c;
  uVar3 = raise_priority_mask_and_return_previous_d1da0(0xffc0);
  uVar5 = 0;
  uVar4 = 0x564e;
  (*((ushort *)camry_host_ptr((uint32_t)(puVar2 + -0x6c8)))) = uVar1;
  if (uVar6 != 0) {
    uVar5 = (undefined2)(0x10000000 / uVar6);
    uVar4 = (undefined2)(0x2774564e / uVar6);
  }
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar2 + -0x6c6)))) = uVar5;
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar2 + -0x6c4)))) = uVar4;
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar2 + -0x6c0)))) = uVar4;
  uVar5 = (undefined2)((uVar6 << 0xe) / 0x9dd1);
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar2 + -0x6c2)))) = uVar5;
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar2 + -0x6be)))) = uVar5;
  restore_priority_mask_preserving_interrupt_enable_d1dc6(uVar3);
  return uVar3;
}

void return_only_stub_b391c(void)

{
  return;
}

void return_only_stub_b391e(void)

{
  return;
}

int multiply_divide_signed_split_16_b3920(int param_1,int param_2,int param_3)

{
  int iVar1;
  int in_r17;
  int iVar2;
  
  if (param_3 == 0) {
    return 0;
  }
  iVar2 = (param_1 / 0x10000) * 0x10000;
  if (param_3 != 0) {
    if (iVar2 == -0x80000000 && param_3 == -1) {
      iVar2 = -0x80000000;
      in_r17 = 0;
    }
    else {
      in_r17 = (int)iVar2 % (int)param_3;
      iVar2 = (int)iVar2 / (int)param_3;
    }
  }
  iVar1 = (param_1 % 0x10000 + in_r17) * param_2;
  if (param_3 != 0) {
    if (iVar1 == -0x80000000 && param_3 == -1) {
      iVar1 = -0x80000000;
    }
    else {
      iVar1 = (int)iVar1 / (int)param_3;
    }
  }
  return iVar1 + iVar2 * param_2;
}

void update_scaled_b178_and_b054_sum_b394c(void)

{
  int iVar1;
  uint32_t puVar2;
  undefined4 uVar3;
  int iVar4;
  int iVar5;
  int iVar6;
  int local_10;
  
  puVar2 = 0xfebeb800u;
  iVar5 = (int)((int)(int16_t)DAT_febeb054);
  iVar1 = DAT_febeb150;
  uVar3 = DAT_febeb158;
  iVar4 = DAT_febeb14c;
  iVar6 = DAT_febeb148;
  if ((DAT_febeb168 == 'Z') && (DAT_febeb16a == 'Z')) {
    puVar2 = 0xfebeb800u;
    local_10 = multiply_divide_signed_split_16_b3920(DAT_febeb178,0x400,DAT_febeb138);
    store_signed32_clamped_between_upper_and_lower_d1cf6(local_10,0x5b05b0,(int)0xffa4fa50,&local_10);
    iVar6 = local_10;
    uVar3 = multiply_divide_signed_split_16_b3920(local_10, 0x4507, ((uint32_t)(0xb400u)));
    iVar1 = (DAT_000af100 * iVar5) / 0x4000;
    iVar4 = iVar1 + iVar6;
  }
  (*((int *)camry_host_ptr((uint32_t)(puVar2 + -0x6b0)))) = iVar1;
  (*((int *)camry_host_ptr((uint32_t)(puVar2 + -0x6b8)))) = iVar6;
  (*((undefined4 *)camry_host_ptr((uint32_t)(puVar2 + -0x6a8)))) = uVar3;
  (*((int *)camry_host_ptr((uint32_t)(puVar2 + -0x6b4)))) = iVar4;
  return;
}

void compute_b14c_reference_error_gate_b39d8(void)

{
  char cVar1;
  char cVar2;
  uchar uVar3;
  char cVar4;
  char cVar5;
  uint32_t puVar6;
  undefined1 uVar7;
  int local_1c;
  
  cVar5 = DAT_febef154;
  cVar4 = DAT_febef069;
  uVar3 = published_internal_source_admission_state;
  cVar2 = DAT_febeb16a;
  cVar1 = DAT_febeb078;
  puVar6 = 0xfebeb800u;
  store_saturated_signed32_absolute_d1194(DAT_febeb14c - ((int)((int)(int16_t)DAT_febeb16c) << 0x10) / 0xe10,&local_1c);
  if ((((cVar2 == '\0') || (cVar5 != '\x02')) ||
      ((local_1c - DAT_000af0fc < 0 ==
        (local_1c < 0 != DAT_000af0fc < 0 && DAT_000af0fc < 0 == local_1c - DAT_000af0fc < 0) &&
       ((uVar3 < 2 && (cVar4 == '\0')))))) || (uVar7 = 0, cVar1 != '\0')) {
    uVar7 = 0x5a;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(-0x6bc))))) = uVar7;
  (*((int *)camry_host_ptr((uint32_t)(puVar6 + -0x6ac)))) = local_1c;
  return;
}

void update_scaled_reference_and_error_b3a42(void)

{
  update_scaled_b178_and_b054_sum_b394c();
  compute_b14c_reference_error_gate_b39d8();
  return;
}

void return_only_stub_b3a52(void)

{
  return;
}

void return_only_stub_b3a54(void)

{
  return;
}

void aggregate_b067_b071_and_marker_fault_b3a56(void)

{
  if (((((((DAT_febeb067 == '\0') && (DAT_febeb068 == '\0')) && (DAT_febeb069 == '\0')) &&
        ((DAT_febeb06a == '\0' && (DAT_febeb06b == '\0')))) &&
       (((DAT_febeb06c == '\0' && ((DAT_febeb06d == '\0' && (DAT_febeb06e == '\0')))) &&
        (DAT_febeb06f == '\0')))) &&
      (((DAT_febeb070 == '\0' && (DAT_febeb071 == '\0')) &&
       ((DAT_febeb358 == '\0' || (DAT_febeb358 == '\x02')))))) && (DAT_febef208 == -0x5aa5a55b)) {
    DAT_febeb16b = 0;
  }
  else {
    DAT_febeb16b = 0x5a;
  }
  return;
}

void publish_b078_clear_as_b168_b3ac4(void)

{
  DAT_febeb168 = 0;
  if (DAT_febeb078 == '\0') {
    DAT_febeb168 = 0x5a;
  }
  return;
}

void publish_admitted_f154_mode_two_gate_b3ad8(void)

{
  if ((((DAT_febef06b == '\0') && (DAT_febef069 == '\0')) && (DAT_febef154 == '\x02')) &&
     (published_internal_source_admission_state < 2)) {
    DAT_febeb169 = 0x5a;
  }
  else {
    DAT_febeb169 = 0;
  }
  return;
}

void update_admitted_f1a0_times_fifteen_plus_f06f_b3b06(void)

{
  if ((DAT_febef069 == '\0') && (published_internal_source_admission_state < 2)) {
    DAT_febeb16c = ((int)(int16_t)DAT_febef1a0) * 0xf + (short)((int)(int8_t)DAT_febef06f);
  }
  return;
}

void derive_b16c_offset_and_scaled_negative_sum_b3b2e(void)

{
  int iVar1;
  int iVar2;
  uint32_t puVar3;
  int iVar4;
  
  iVar2 = DAT_febeafe8;
  puVar3 = 0xfebeb800u;
  iVar1 = (int)((int)(int16_t)DAT_febeb16c) - (DAT_000af104 * ((int)(int16_t)DAT_febeb054)) / 0x4000;
  iVar4 = multiply_divide_signed_split_16_b3920(iVar1 * (uint)DAT_febeb138,4,0xe1);
  (*((int *)camry_host_ptr((uint32_t)(puVar3 + -0x690)))) = iVar1;
  (*((int *)camry_host_ptr((uint32_t)(puVar3 + -0x68c)))) = -iVar4 - iVar2;
  (*((int *)camry_host_ptr((uint32_t)(puVar3 + -0x684)))) = iVar4;
  return;
}

void latch_initial_scaled_reference_once_b3b7a(void)

{
  char cVar1;
  char cVar2;
  uint32_t puVar3;
  char cVar4;
  
  cVar4 = DAT_febeb16a;
  cVar2 = DAT_febeb169;
  cVar1 = DAT_febeb168;
  puVar3 = 0xfebeb800u;
  update_admitted_f1a0_times_fifteen_plus_f06f_b3b06();
  if (((cVar1 == 'Z') && (cVar2 == 'Z')) && (cVar4 == '\0')) {
    derive_b16c_offset_and_scaled_negative_sum_b3b2e();
    cVar4 = 'Z';
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x696))))) = cVar4;
  return;
}

void update_negated_b174_afe8_sum_b3baa(void)

{
  if ((DAT_febeb168 == 'Z') && (DAT_febeb16a == 'Z')) {
    DAT_febeb178 = -DAT_febeb174 - DAT_febeafe8;
  }
  return;
}

void run_init_chain_b3bd2(void)

{
  aggregate_b067_b071_and_marker_fault_b3a56();
  publish_b078_clear_as_b168_b3ac4();
  publish_admitted_f154_mode_two_gate_b3ad8();
  latch_initial_scaled_reference_once_b3b7a();
  update_negated_b174_afe8_sum_b3baa();
  return;
}

void interpolate_u32_sentinel_pair_table_b3bee(uint *param_1,uint param_2,uint *param_3)

{
  uint uVar1;
  uint uVar2;
  undefined8 uVar3;
  uint uVar4;
  uint uVar5;
  int iVar6;
  
  iVar6 = 0;
  if ((*param_1 == 0xffffffff) || (param_2 <= *param_1)) {
    uVar1 = param_1[1];
  }
  else {
    uVar2 = 0;
    while( true ) {
      uVar4 = param_1[uVar2 * 2];
      if ((param_2 < uVar4) || (uVar4 == 0xffffffff)) break;
      uVar2 = uVar2 + 1;
    }
    if (1 < uVar2) {
      iVar6 = uVar2 - 1;
    }
    uVar1 = (param_1 + iVar6 * 2)[1];
    if (uVar4 != 0xffffffff) {
      uVar5 = param_1[iVar6 * 2];
      uVar2 = (param_1 + uVar2 * 2)[1];
      uVar3 = multiply_two_word_integers_modulo_64_bits_d2834(param_2 - uVar5,-(uint)(param_2 < uVar5),uVar2 - uVar1,
                           -(uint)(uVar2 < uVar1));
      iVar6 = divide_signed_two_word_integers_d28ea((int)uVar3,(int)((ulonglong)uVar3 >> 0x20),uVar4 - uVar5,
                           -(uint)(uVar4 < uVar5));
      uVar1 = uVar1 + iVar6;
    }
  }
  *param_3 = uVar1;
  return;
}

void return_only_stub_b3c68(void)

{
  return;
}

void return_only_stub_b3c6a(void)

{
  return;
}

void publish_health_coherence_fault_actions(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  retain_and_clear_fault_record(0x13);
  if (((((*((int *)camry_host_ptr((uint32_t)(puVar1 + -0x5e8)))) != -0x5aa5a55b) || ((*((int *)camry_host_ptr((uint32_t)(puVar1 + -0x5e4)))) != -0x5aa5a55b)) ||
      ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x5f2))))) == '3')) ||
     ((((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x5eb))))) != '\0' || ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x5ae))))) != 'D')) || ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x5ad))))) != '\0')))) {
    encode_fault_action_kind('\x13','\x16');
  }
  select_current_fault_record(0x13);
  return;
}

undefined4 initialize_source_coherence_history(void)

{
  return write_xor_encoded_u8_triplicate_d268c(0, ((byte *)camry_host_ptr((uint32_t)((0xfebeb18eu)))), ((byte *)camry_host_ptr((uint32_t)((0xfebeb18cu)))), ((undefined *)camry_host_ptr(0xfebeb18du)));
}

undefined4 reset_current_source_coherence_observations(void)

{
  DAT_febeb198 = 0;
  DAT_febeb19a = 0;
  DAT_febeb19c = 0;
  DAT_febeb190 = 0;
  current_source_coherence_observations = '\0';
  return write_xor_encoded_u8_triplicate_d268c(0, ((byte *)camry_host_ptr((uint32_t)((0xfebeb18eu)))), ((byte *)camry_host_ptr((uint32_t)((0xfebeb18cu)))), ((undefined *)camry_host_ptr(0xfebeb18du)));
}

uint qualify_packed_channel_zero_status
               (ushort *count,uint packed_status_qualifier_limit,uint current_tag,uint expected_tag,
               uchar generation_armed)

{
  ushort uVar1;
  uint uVar2;
  undefined1 uStack_c;
  undefined1 uStack_b;
  undefined2 uStack_a;
  
  uVar2 = 0;
  if (generation_armed == 'Z') {
    uStack_b = (char)(packed_status_qualifier_limit >> 8);
    if ((((((int8_t)uStack_b) == -0x5b) && (DAT_000aefa8 <= DAT_febeb084)) &&
        (uStack_c = (char)packed_status_qualifier_limit, uStack_c == '\0')) &&
       (((current_tag == 0x33333333 || (current_tag == 0xffffffff)) || (current_tag == expected_tag)
        ))) {
      uVar1 = *count;
      uStack_a = (ushort)(packed_status_qualifier_limit >> 0x10);
      if ((uStack_a < uVar1) || (*count = uVar1 + 1, uStack_a < (ushort)(uVar1 + 1))) {
        uVar2 = 1;
      }
    }
    else {
      *count = 0;
    }
  }
  return uVar2;
}

uint qualify_secondary_received_status_delay(void)

{
  uint uVar1;
  
  uVar1 = 0;
  if (((DAT_febebedd == 'Z') && (DAT_000aefae <= DAT_febebede)) && (DAT_000aefa8 <= DAT_febeb084)) {
    if ((DAT_000aefb0 < DAT_febeb19c) ||
       (DAT_febeb19c = DAT_febeb19c + 1, DAT_000aefb0 < DAT_febeb19c)) {
      uVar1 = 1;
    }
  }
  else {
    DAT_febeb19c = 0;
  }
  return uVar1;
}

void refresh_gated_source_coherence_indicator(uint source_history)

{
  DAT_febeb192 = 0;
  if ((DAT_000aefa8 <= DAT_febeb084) &&
     (((((source_history & 1) != 0 || (DAT_febeb18f == 'Z')) || ((DAT_febef16a & 0x1010) != 0)) ||
      ((((((DAT_febebe7c == '\"' && (DAT_febeb314 == 0x55aaaa55)) ||
          ((DAT_febebe7d == '\"' && (DAT_febeb314 == -0x55aaaa56)))) ||
         ((DAT_febebe89 == '\"' || (DAT_febeb314 == -1)))) ||
        ((DAT_febeb314 == 0x33333333 || (DAT_febeb300 == '\"')))) &&
       (((source_history >> 1 & 1) != 0 || ((DAT_febef093 >> 1 & 1) != 0)))))))) {
    DAT_febeb192 = 0x5a;
  }
  return;
}

uint32_t update_latched_secondary_channel_qualification(void)

{
  uint32_t camry_r10_result;
  uint8_t stack_record_34[52];
  ushort uVar1;
  undefined1 uVar2;
  undefined1 uVar3;
  uint32_t puVar4;
  uint uVar5;
  uint uVar6;
  undefined1 uVar7;
  byte bVar8;
  
  uVar3 = DAT_febebe7c;
  uVar2 = DAT_febebe79;
  uVar6 = DAT_febeb314;
  bVar8 = DAT_febeb194;
  uVar7 = DAT_febeb193;
  uVar1 = DAT_febeb084;
  puVar4 = 0xfebeb800u;
  (*((uint16_t *)(stack_record_34 + 0))) = DAT_febeb19e;
  (*((uint32_t *)(stack_record_34 + 8))) = DAT_febeb314;
  (*((uint16_t *)(stack_record_34 + 2))) = DAT_febeb1a0;
  (*((uint16_t *)((uint8_t *)(stack_record_34 + 4) + 0u))) = CONCAT11(DAT_febebe7a,DAT_febebe7d);
  (*((uint32_t *)(stack_record_34 + 4))) = CONCAT22(DAT_000aefac,(undefined2)(*((uint32_t *)(stack_record_34 + 4))));
  (*((uint32_t *)(stack_record_34 + 12))) = 0xaa5555aa;
  stack_record_34[16] = health_receive_generation_armed;
  uVar5 = (camry_r10_result = qualify_packed_channel_zero_status
                    (stack_record_34,(*((uint32_t *)(stack_record_34 + 4))),DAT_febeb314,(int)0xaa5555aa,health_receive_generation_armed
                    ));
  if (uVar5 == 1) {
    bVar8 = bVar8 | 1;
  }
  (*((uint32_t *)(stack_record_34 + 8))) = uVar6;
  (*((uint16_t *)((uint8_t *)(stack_record_34 + 4) + 0u))) = CONCAT11(uVar2,uVar3);
  (*((uint32_t *)(stack_record_34 + 4))) = CONCAT22(DAT_000aefaa,(undefined2)(*((uint32_t *)(stack_record_34 + 4))));
  (*((uint32_t *)(stack_record_34 + 12))) = 0x55aaaa55;
  (*((uint32_t *)(stack_record_34 + 16))) = CONCAT31(((uint32_t)stack_record_34[17] | ((uint32_t)stack_record_34[18] << 8) | ((uint32_t)stack_record_34[19] << 16)),(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x66a))))));
  uVar6 = (camry_r10_result = qualify_packed_channel_zero_status
                    ((stack_record_34 + 2),(*((uint32_t *)(stack_record_34 + 4))),uVar6,0x55aaaa55,(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x66a)))))));
  if (uVar6 == 1) {
    bVar8 = bVar8 | 1;
  }
  (*((ushort *)camry_host_ptr((uint32_t)(puVar4 + -0x662)))) = (*((uint16_t *)(stack_record_34 + 0)));
  (*((ushort *)camry_host_ptr((uint32_t)(puVar4 + -0x660)))) = (*((uint16_t *)(stack_record_34 + 2)));
  if ((DAT_000aefa8 <= uVar1) && ((bVar8 & 1) != 0)) {
    uVar7 = 0x5a;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x66d))))) = uVar7;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x66c))))) = bVar8;
  return camry_r10_result;
}

uint is_health_or_command_completion_observed(void)

{
  uint uVar1;
  
  uVar1 = 0;
  if ((DAT_febeb20e == '\x11') || (DAT_febeb190 == 'Z')) {
    uVar1 = 1;
  }
  return uVar1;
}

uint32_t update_source_coherence_history(void)

{
  uint32_t camry_r10_result;
  uint8_t stack_record_51[81];
  char cVar1;
  char cVar2;
  char cVar3;
  char cVar4;
  char cVar5;
  char cVar6;
  uint32_t puVar7;
  int iVar8;
  uint uVar9;
  uint uVar10;
  byte bVar11;
  uint32_t puStack_44;
  uchar *puStack_40;
  
  puVar7 = 0xfebeb800u;
  puStack_40 = ((void *)camry_host_ptr((uint32_t)((0xfebeb18cu))));
  puStack_44 = 0xfebeb18du;
  iVar8 = (camry_r10_result = read_vote_xor_encoded_u8_triplicate_d23b8(((byte *)camry_host_ptr((uint32_t)((0xfebeb18eu)))), ((byte *)camry_host_ptr((uint32_t)((0xfebeb18cu)))), 
                       ((undefined *)camry_host_ptr(0xfebeb18du)), stack_record_51));
  cVar6 = DAT_febeb18f;
  bVar11 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar7 + (uint32_t)(-0x66f)))));
  if (iVar8 == -0xd) {
    stack_record_51[0] = 0;
  }
  stack_record_51[4] = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar7 + (uint32_t)(0x3893)))));
  (*((uint16_t *)(stack_record_51 + 11))) = (*((ushort *)camry_host_ptr((uint32_t)(puVar7 + 0x396a))));
  stack_record_51[3] = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar7 + (uint32_t)(0x67e)))));
  (*((uint16_t *)(stack_record_51 + 5))) = DAT_febeb19a;
  stack_record_51[2] = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar7 + (uint32_t)(-0x62a)))));
  (*((uint16_t *)(stack_record_51 + 9))) = (*((ushort *)camry_host_ptr((uint32_t)(puVar7 + -0x77c))));
  (*((uint16_t *)(stack_record_51 + 7))) = DAT_febeb198;
  cVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar7 + (uint32_t)(-0x500)))));
  uVar10 = (*((uint *)camry_host_ptr((uint32_t)(puVar7 + -0x4ec))));
  cVar2 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar7 + (uint32_t)(0x67c)))));
  cVar3 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar7 + (uint32_t)(0x67d)))));
  cVar4 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar7 + (uint32_t)(0x689)))));
  cVar5 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar7 + (uint32_t)(-0x62f)))));
  if (((byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar7 + (uint32_t)(0x3800))))) < 2) && (previous_health_receive_generation != stack_record_51[3])) {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar7 + (uint32_t)(-0x66a))))) = 0x5a;
  }
  (*((uint16_t *)((uint8_t *)(stack_record_51 + 21) + 0u))) = CONCAT11((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar7 + (uint32_t)(0x67a))))),cVar3);
  (*((uint32_t *)(stack_record_51 + 21))) = CONCAT22(DAT_000aefac,(undefined2)(*((uint32_t *)(stack_record_51 + 21))));
  (*((uint32_t *)(stack_record_51 + 29))) = 0xaa5555aa;
  (*((uint32_t *)(stack_record_51 + 25))) = uVar10;
  stack_record_51[33] = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar7 + (uint32_t)(-0x66a)))));
  uVar9 = (camry_r10_result = qualify_packed_channel_zero_status
                    ((stack_record_51 + 5),(*((uint32_t *)(stack_record_51 + 21))),uVar10,(int)0xaa5555aa,(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar7 + (uint32_t)(-0x66a)))))));
  stack_record_51[1] = uVar9 == 1;
  if ((bool)stack_record_51[1]) {
    stack_record_51[0] = stack_record_51[0] | 1;
  }
  (*((uint16_t *)((uint8_t *)(stack_record_51 + 21) + 0u))) = CONCAT11((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar7 + (uint32_t)(0x679))))),cVar2);
  (*((uint32_t *)(stack_record_51 + 21))) = CONCAT22(DAT_000aefaa,(undefined2)(*((uint32_t *)(stack_record_51 + 21))));
  (*((uint32_t *)(stack_record_51 + 29))) = 0x55aaaa55;
  (*((uint32_t *)(stack_record_51 + 33))) = CONCAT31(((uint32_t)stack_record_51[34] | ((uint32_t)stack_record_51[35] << 8) | ((uint32_t)stack_record_51[36] << 16)),(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar7 + (uint32_t)(-0x66a))))));
  (*((uint32_t *)(stack_record_51 + 25))) = uVar10;
  uVar9 = (camry_r10_result = qualify_packed_channel_zero_status
                    ((stack_record_51 + 7),(*((uint32_t *)(stack_record_51 + 21))),uVar10,0x55aaaa55,(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar7 + (uint32_t)(-0x66a)))))));
  if (uVar9 == 1) {
    stack_record_51[0] = stack_record_51[0] | 1;
  }
  else if (stack_record_51[1] != '\x01') {
    bVar11 = bVar11 & 0xfc;
    goto LAB_000b4080;
  }
  bVar11 = bVar11 | 1;
LAB_000b4080:
  (*((ushort *)camry_host_ptr((uint32_t)(puVar7 + -0x666)))) = (*((uint16_t *)(stack_record_51 + 5)));
  (*((ushort *)camry_host_ptr((uint32_t)(puVar7 + -0x668)))) = (*((uint16_t *)(stack_record_51 + 7)));
  uVar9 = (camry_r10_result = qualify_secondary_received_status_delay());
  if (uVar9 == 1) {
    stack_record_51[0] = stack_record_51[0] | 2;
    bVar11 = bVar11 | 2;
  }
  else {
    bVar11 = bVar11 & 0xfd;
  }
  if ((DAT_000aefa8 <= (*((uint16_t *)(stack_record_51 + 9)))) &&
     (((((stack_record_51[0] & 3) != 0 || (cVar6 == 'Z')) || (((*((uint16_t *)(stack_record_51 + 11))) & 0x1010) != 0)) ||
      ((((((cVar2 == '\"' && (uVar10 == 0x55aaaa55)) || ((cVar3 == '\"' && (uVar10 == 0xaa5555aa))))
         || ((cVar4 == '\"' || (uVar10 == 0xffffffff)))) ||
        ((uVar10 == 0x33333333 || (cVar1 == '\"')))) && ((stack_record_51[4] >> 1 & 1) != 0)))))) {
    stack_record_51[0] = stack_record_51[0] | 8;
  }
  if (cVar5 == 'Z') {
    refresh_gated_source_coherence_indicator((uint)stack_record_51[0]);
  }
  if (stack_record_51[2] == 'Z') {
    (camry_r10_result = update_latched_secondary_channel_qualification());
  }
  uVar10 = (camry_r10_result = is_health_or_command_completion_observed());
  if (uVar10 == 1) {
    stack_record_51[0] = stack_record_51[0] | 0x10;
  }
  (camry_r10_result = write_xor_encoded_u8_triplicate_d268c(stack_record_51[0], ((byte *)camry_host_ptr((uint32_t)((0xfebeb18eu)))),  puStack_40,  ((undefined *)camry_host_ptr((uint32_t)(puStack_44)))));
  current_source_coherence_observations = bVar11;
  previous_health_receive_generation = stack_record_51[3];
  return camry_r10_result;
}
