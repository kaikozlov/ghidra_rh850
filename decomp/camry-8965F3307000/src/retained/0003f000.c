#include "common.h"

undefined4 advance_coupled_threshold_first_delay_3f010(void)

{
  ushort uVar1;
  uint32_t puVar2;
  undefined4 uVar3;
  ushort uVar4;
  
  uVar4 = DAT_febe67c0;
  uVar1 = DAT_febe6764;
  puVar2 = 0xfebeb800u;
  if (DAT_febe67c0 < DAT_0002b6fa) {
    uVar3 = 0;
    uVar4 = DAT_febe67c0 + 1;
  }
  else {
    puVar2 = 0xfebeb800u;
    if ((DAT_febe6764 & 1) == 0) {
      puVar2 = 0xfebeb800u;
      set_secondary_channel_request_bounded5_56e66(DAT_febe6764 & 1,2);
      set_secondary_priority_mask_bounded2_56f14(0,4);
    }
    if ((uVar1 >> 1 & 1) == 0) {
      set_secondary_channel_request_bounded5_56e66(1,0x20000);
      set_secondary_priority_mask_bounded2_56f14(1,0x40000);
    }
    uVar3 = 1;
  }
  (*((ushort *)camry_host_ptr((uint32_t)(puVar2 + -0x5040)))) = uVar4;
  return uVar3;
}

undefined4 advance_coupled_threshold_second_delay_3f066(void)

{
  ushort uVar1;
  uint32_t puVar2;
  undefined4 uVar3;
  ushort uVar4;
  
  uVar4 = DAT_febe67c2;
  uVar1 = DAT_febe6764;
  puVar2 = 0xfebeb800u;
  if (DAT_febe67c2 < DAT_0002b6fc) {
    uVar3 = 1;
    uVar4 = DAT_febe67c2 + 1;
  }
  else {
    puVar2 = 0xfebeb800u;
    if ((DAT_febe6764 & 1) == 0) {
      puVar2 = 0xfebeb800u;
      set_priority_mask_8a9c_bounded2_56c26(DAT_febe6764 & 1,2);
    }
    if ((uVar1 >> 1 & 1) == 0) {
      set_priority_mask_8a9c_bounded2_56c26(1,0x20000);
    }
    uVar3 = 2;
  }
  (*((ushort *)camry_host_ptr((uint32_t)(puVar2 + -0x503e)))) = uVar4;
  return uVar3;
}

undefined4 advance_coupled_threshold_final_delay_3f0aa(void)

{
  undefined4 uVar1;
  
  uVar1 = 2;
  if (DAT_febe67c4 < DAT_0002b6fe) {
    DAT_febe67c4 = DAT_febe67c4 + 1;
  }
  else {
    uVar1 = 3;
  }
  return uVar1;
}

uint admit_coupled_sample_monitor(void)

{
  ushort uVar1;
  uint32_t puVar2;
  uint uVar3;
  int iVar4;
  uint uVar5;
  ushort uVar6;
  
  puVar2 = (0xfebeb800u);
  uVar5 = (uint)DAT_febe67bd;
  uVar3 = (uint)DAT_febe67bc;
  uVar6 = DAT_febe67be;
  if (uVar5 != 0x5a) {
    uVar1 = DAT_0002b6f8;
    if ((DAT_febe6764 & 3) == 0) {
      uVar1 = DAT_0002b6f6;
    }
    if (uVar1 < DAT_febe67be) {
      iVar4 = 0x5a;
    }
    else {
      iVar4 = 0;
      uVar6 = DAT_febe67be + 1;
    }
    if ((3 < uVar3) || (puVar2 = (0xfebeb800u), uVar3 == 0)) {
      puVar2 = (0xfebeb800u);
      uVar3 = advance_coupled_threshold_first_delay_3f010();
    }
    if (uVar3 == 1) {
      uVar3 = advance_coupled_threshold_second_delay_3f066();
    }
    if (uVar3 == 2) {
      uVar3 = advance_coupled_threshold_final_delay_3f0aa();
    }
    if ((iVar4 == 0x5a) && (uVar3 == 3)) {
      uVar5 = 0x5a;
    }
  }
  (*((volatile undefined *)camry_host_ptr((uint32_t)(0xfebeb800u + (uint32_t)(-0x5044) * 1u)))) = (char)uVar3;
  (*((volatile undefined *)camry_host_ptr((uint32_t)(0xfebeb800u + (uint32_t)(-0x5043) * 1u)))) = (char)uVar5;
  *(ushort *)(((undefined *)camry_host_ptr((uint32_t)(0xfebeb800u + (uint32_t)(-0x5042) * 1u)))) = uVar6;
  return uVar5;
}

void step_coupled_sample_threshold_both(void)

{
  ushort uVar1;
  uint32_t puVar2;
  F33TerminalMonitorState *state;
  uint uVar3;
  
  puVar2 = 0xfebeb800u;
  uVar1 = DAT_febe6764 & 3;
  uVar3 = admit_coupled_sample_monitor();
  state = ((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xffffbe0cu + (uint32_t)((int)puVar2)))));
  if (uVar3 == 0x5a) {
    if (DAT_0002bb88 == 'Z') {
      force_unconfirmed_terminal_monitor_healthy
                (camry_host_addr(state), (0x2b67au), 
                 (0x283f4u));
    }
    else if (uVar1 == 0) {
      step_terminal_monitor
                (state, ((F33MonitorLimits *)camry_host_ptr((uint32_t)((0x2b67au)))), ((F33TerminalMonitorCallbacks *)camry_host_ptr((uint32_t)((0x283f4u)))));
    }
    else {
      reset_terminal_monitor(state);
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbe0cu + (uint32_t)((int)puVar2) * 1u)))) = 0;
    }
  }
  else {
    reset_terminal_monitor(state);
  }
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbe0cu + (uint32_t)((int)puVar2) * 1u)))) == '\0') {
    mark_redundant_byte_6884_for_codes_21_to_34_32036(0x1d);
    mark_redundant_byte_6885_for_codes_21_to_34_32050(0x1d);
  }
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbe0cu + (uint32_t)((int)puVar2) * 1u)))) == '\"') {
    retain_and_clear_fault_record(9);
    encode_fault_action_kind('\t','\x1a');
    select_current_fault_record(9);
  }
  return;
}

uint classify_coupled_sample_threshold_both(void)

{
  if ((((((DAT_febe64d8 != '\x02') || (DAT_febe64d9 != '\x02')) || (DAT_febe64d0 != '\0')) ||
       ((DAT_febe64d1 != '\0' || ((DAT_febe6620 >> 1 & 1) == 0)))) ||
      (((DAT_febe6620 >> 2 & 1) != 0 ||
       (((DAT_febe6620 >> 0x11 & 1) == 0 || ((DAT_febe6620 >> 0x12 & 1) != 0)))))) ||
     (((DAT_febe661c >> 2 & 1) == 0 ||
      (((((DAT_febe661c & 0x40000) == 0 || ((DAT_febe6628 >> 1 & 1) == 0)) ||
        ((DAT_febe6628 >> 0x11 & 1) == 0)) || (((DAT_febe6614 & 1) != 0 || (DAT_febe65f0 != 'Z')))))
      ))) {
    return 0x44;
  }
  if (((DAT_0002b702 <= DAT_febe66b2) ||
      ((DAT_0002b704 <= DAT_febe66b4 || (DAT_0002b700 < DAT_febe66b8)))) &&
     ((DAT_0002b708 <= DAT_febe66b2 ||
      ((DAT_0002b706 <= DAT_febe66b4 || (DAT_febe66b8 <= DAT_0002b700)))))) {
    return 0x11;
  }
  return 0x22;
}

void record_coupled_sample_threshold_both_healthy_observed(void)

{
  report_diagnostic_healthy_observed(0x60);
  report_diagnostic_healthy_observed(0x61);
  return;
}

void record_coupled_sample_threshold_both_failure(void)

{
  report_diagnostic_event_failure(0x60,0x32);
  report_diagnostic_event_failure(0x61,0x32);
  return;
}

undefined4 status_failing_coupled_sample_threshold_both_states(void)

{
  if (coupled_sample_threshold_both_states.failing_count != 0) {
    return 0x11;
  }
  return 0;
}

void reset_command_status_bit_clear_a(void)

{
  reset_terminal_monitor(((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xfebe7614u)))));
  return;
}

void reset_command_status_a_monitor_and_delays_3f2d6(void)

{
  DAT_febe67c8 = 0;
  DAT_febe67c9 = 0;
  DAT_febe67ca = 0;
  DAT_febe67cc = 0;
  DAT_febe67ce = 0;
  DAT_febe67d0 = 0;
  reset_terminal_monitor(((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xfebe7614u)))));
  return;
}

undefined4 advance_command_status_a_initial_delay_3f2f6(void)

{
  ushort uVar1;
  uint32_t puVar2;
  undefined4 uVar3;
  ushort uVar4;
  
  uVar4 = DAT_febe67ca;
  uVar1 = DAT_febe6764;
  puVar2 = 0xfebeb800u;
  if (DAT_febe67ca < DAT_0002b70a) {
    uVar3 = 0;
    uVar4 = DAT_febe67ca + 1;
  }
  else {
    puVar2 = 0xfebeb800u;
    set_indexed_status_mask_word_if_below_five_50c82(0,0);
    if ((uVar1 & 1) == 0) {
      set_request_word_8aa8_bounded6_56cda(uVar1 & 1,2);
    }
    uVar3 = 1;
  }
  (*((ushort *)camry_host_ptr((uint32_t)(puVar2 + -0x5036)))) = uVar4;
  return uVar3;
}

undefined4 advance_command_status_a_three_delays_3f334(void)

{
  undefined4 uVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  
  iVar3 = 0;
  uVar1 = 1;
  iVar2 = 0;
  if (DAT_febe67cc < DAT_0002b70c) {
    iVar4 = 0;
    DAT_febe67cc = DAT_febe67cc + 1;
  }
  else {
    iVar4 = 0x5a;
  }
  if (DAT_febe67ce < DAT_0002b70e) {
    DAT_febe67ce = DAT_febe67ce + 1;
  }
  else {
    iVar3 = 0x5a;
  }
  if (DAT_febe67d0 < DAT_0002b710) {
    DAT_febe67d0 = DAT_febe67d0 + 1;
  }
  else {
    iVar2 = 0x5a;
  }
  if ((iVar4 == 0x5a) && (iVar3 == 0x5a)) {
    if (iVar2 == 0x5a) {
      uVar1 = 2;
    }
    else {
      uVar1 = 1;
    }
  }
  return uVar1;
}

uint admit_command_status_monitor_a(void)

{
  uint32_t puVar1;
  uint uVar2;
  uint uVar3;
  
  puVar1 = (0xfebeb800u);
  uVar3 = (uint)DAT_febe67c9;
  uVar2 = (uint)DAT_febe67c8;
  if (uVar3 != 0x5a) {
    if ((2 < uVar2) || (puVar1 = (0xfebeb800u), uVar2 == 0)) {
      puVar1 = (0xfebeb800u);
      uVar2 = advance_command_status_a_initial_delay_3f2f6();
    }
    if (uVar2 == 1) {
      uVar2 = advance_command_status_a_three_delays_3f334();
    }
    if (uVar2 == 2) {
      uVar3 = 0x5a;
    }
  }
  (*((volatile undefined *)camry_host_ptr((uint32_t)(0xfebeb800u + (uint32_t)(-0x5038) * 1u)))) = (char)uVar2;
  (*((volatile undefined *)camry_host_ptr((uint32_t)(0xfebeb800u + (uint32_t)(-0x5037) * 1u)))) = (char)uVar3;
  return uVar3;
}

void step_command_status_bit_clear_a(void)

{
  ushort uVar1;
  uint32_t puVar2;
  uint uVar3;
  
  uVar1 = DAT_febe6764;
  puVar2 = 0xfebeb800u;
  uVar3 = admit_command_status_monitor_a();
  if (uVar3 == 0x5a) {
    if (DAT_0002bb8c == 'Z') {
      force_unconfirmed_terminal_monitor_healthy
                (camry_host_addr(((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xffffbe14u + (uint32_t)((int)puVar2)))))), 
                 (0x2b67eu), (0x28400u));
    }
    else if ((uVar1 & 1) == 0) {
      step_terminal_monitor
                (((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xffffbe14u + (uint32_t)((int)puVar2))))), ((F33MonitorLimits *)camry_host_ptr((uint32_t)((0x2b67eu)))), ((F33TerminalMonitorCallbacks *)camry_host_ptr((uint32_t)((0x28400u)))));
    }
  }
  else {
    reset_terminal_monitor(((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xffffbe14u + (uint32_t)((int)puVar2))))));
  }
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbe14u + (uint32_t)((int)puVar2) * 1u)))) == '\0') {
    mark_redundant_byte_6884_for_codes_21_to_34_32036(0x1b);
  }
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbe14u + (uint32_t)((int)puVar2) * 1u)))) == '\"') {
    retain_and_clear_fault_record(10);
    encode_fault_action_kind('\n','\x1d');
    select_current_fault_record(10);
  }
  return;
}

uint classify_command_status_bit_clear_a(void)

{
  if ((((DAT_febe64d8 == '\0') && (DAT_febe64d0 == '\0')) && ((DAT_febe6620 >> 2 & 1) != 0)) &&
     ((((DAT_febe661c >> 2 & 1) != 0 && ((DAT_febe6628 >> 1 & 1) == 0)) &&
      (((DAT_febe6614 & 1) == 0 && (DAT_febe65f0 == 'Z')))))) {
    if (DAT_febe8291 != '\0') {
      return 0x11;
    }
    return 0x22;
  }
  return 0x44;
}

void record_command_status_bit_clear_a_healthy_observed(void)

{
  report_diagnostic_healthy_observed(0x74);
  return;
}

void record_command_status_bit_clear_a_failure(void)

{
  report_diagnostic_event_failure(0x74,0x32);
  return;
}

undefined4 status_failing_command_status_bit_clear_a_states(void)

{
  if (command_status_bit_clear_a_states.failing_count != 0) {
    return 0x11;
  }
  return 0;
}

void reset_command_status_bit_clear_b(void)

{
  reset_terminal_monitor(((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xfebe761cu)))));
  return;
}

void reset_command_status_b_monitor_and_delays_3f4ec(void)

{
  DAT_febe67d4 = 0;
  DAT_febe67d5 = 0;
  DAT_febe67d6 = 0;
  DAT_febe67d8 = 0;
  DAT_febe67da = 0;
  DAT_febe67dc = 0;
  reset_terminal_monitor(((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xfebe761cu)))));
  return;
}

undefined4 advance_command_status_b_initial_delay_3f50c(void)

{
  ushort uVar1;
  uint32_t puVar2;
  undefined4 uVar3;
  ushort uVar4;
  
  uVar4 = DAT_febe67d6;
  uVar1 = DAT_febe6764;
  puVar2 = 0xfebeb800u;
  if (DAT_febe67d6 < DAT_0002b712) {
    uVar3 = 0;
    uVar4 = DAT_febe67d6 + 1;
  }
  else {
    puVar2 = 0xfebeb800u;
    set_indexed_status_mask_word_if_below_five_50c82(1,0);
    if ((uVar1 >> 1 & 1) == 0) {
      set_request_word_8aa8_bounded6_56cda(1,0x20000);
    }
    uVar3 = 1;
  }
  (*((ushort *)camry_host_ptr((uint32_t)(puVar2 + -0x502a)))) = uVar4;
  return uVar3;
}

undefined4 advance_command_status_b_three_delays_3f54a(void)

{
  undefined4 uVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  
  iVar3 = 0;
  uVar1 = 1;
  iVar2 = 0;
  if (DAT_febe67d8 < DAT_0002b714) {
    iVar4 = 0;
    DAT_febe67d8 = DAT_febe67d8 + 1;
  }
  else {
    iVar4 = 0x5a;
  }
  if (DAT_febe67da < DAT_0002b716) {
    DAT_febe67da = DAT_febe67da + 1;
  }
  else {
    iVar3 = 0x5a;
  }
  if (DAT_febe67dc < DAT_0002b718) {
    DAT_febe67dc = DAT_febe67dc + 1;
  }
  else {
    iVar2 = 0x5a;
  }
  if ((iVar4 == 0x5a) && (iVar3 == 0x5a)) {
    if (iVar2 == 0x5a) {
      uVar1 = 2;
    }
    else {
      uVar1 = 1;
    }
  }
  return uVar1;
}

uint admit_command_status_monitor_b(void)

{
  uint32_t puVar1;
  uint uVar2;
  uint uVar3;
  
  puVar1 = (0xfebeb800u);
  uVar3 = (uint)DAT_febe67d5;
  uVar2 = (uint)DAT_febe67d4;
  if (uVar3 != 0x5a) {
    if ((2 < uVar2) || (puVar1 = (0xfebeb800u), uVar2 == 0)) {
      puVar1 = (0xfebeb800u);
      uVar2 = advance_command_status_b_initial_delay_3f50c();
    }
    if (uVar2 == 1) {
      uVar2 = advance_command_status_b_three_delays_3f54a();
    }
    if (uVar2 == 2) {
      uVar3 = 0x5a;
    }
  }
  (*((volatile undefined *)camry_host_ptr((uint32_t)(0xfebeb800u + (uint32_t)(-0x502c) * 1u)))) = (char)uVar2;
  (*((volatile undefined *)camry_host_ptr((uint32_t)(0xfebeb800u + (uint32_t)(-0x502b) * 1u)))) = (char)uVar3;
  return uVar3;
}

void step_command_status_bit_clear_b(void)

{
  ushort uVar1;
  uint32_t puVar2;
  uint uVar3;
  
  uVar1 = DAT_febe6764;
  puVar2 = 0xfebeb800u;
  uVar3 = admit_command_status_monitor_b();
  if (uVar3 == 0x5a) {
    if (DAT_0002bb90 == 'Z') {
      force_unconfirmed_terminal_monitor_healthy
                (camry_host_addr(((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xffffbe1cu + (uint32_t)((int)puVar2)))))), 
                 (0x2b682u), (0x2840cu));
    }
    else if ((uVar1 >> 1 & 1) == 0) {
      step_terminal_monitor
                (((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xffffbe1cu + (uint32_t)((int)puVar2))))), ((F33MonitorLimits *)camry_host_ptr((uint32_t)((0x2b682u)))), ((F33TerminalMonitorCallbacks *)camry_host_ptr((uint32_t)((0x2840cu)))));
    }
  }
  else {
    reset_terminal_monitor(((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xffffbe1cu + (uint32_t)((int)puVar2))))));
  }
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbe1cu + (uint32_t)((int)puVar2) * 1u)))) == '\0') {
    mark_redundant_byte_6885_for_codes_21_to_34_32050(0x1b);
  }
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbe1cu + (uint32_t)((int)puVar2) * 1u)))) == '\"') {
    retain_and_clear_fault_record(0xb);
    encode_fault_action_kind('\v','\x1e');
    select_current_fault_record(0xb);
  }
  return;
}

uint classify_command_status_bit_clear_b(void)

{
  if ((((DAT_febe64d9 == '\0') && (DAT_febe64d1 == '\0')) && ((DAT_febe6620 >> 0x12 & 1) != 0)) &&
     ((((DAT_febe661c >> 0x12 & 1) != 0 && ((DAT_febe6628 >> 0x11 & 1) == 0)) &&
      (((DAT_febe6614 & 1) == 0 && (DAT_febe65f0 == 'Z')))))) {
    if (DAT_febe8292 != '\0') {
      return 0x11;
    }
    return 0x22;
  }
  return 0x44;
}

void record_command_status_bit_clear_b_healthy_observed(void)

{
  report_diagnostic_healthy_observed(0x75);
  return;
}

void record_command_status_bit_clear_b_failure(void)

{
  report_diagnostic_event_failure(0x75,0x32);
  return;
}

undefined4 status_failing_command_status_bit_clear_b_states(void)

{
  if (command_status_bit_clear_b_states.failing_count != 0) {
    return 0x11;
  }
  return 0;
}

void reset_bounded_sample_or_status_a(void)

{
  reset_terminal_monitor(((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xfebe7624u)))));
  return;
}

void reset_bounded_sample_status_a_monitor_3f702(void)

{
  DAT_febe67e0 = 0;
  DAT_febe67e4 = 0;
  DAT_febe67e2 = 0;
  reset_terminal_monitor(((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xfebe7624u)))));
  return;
}

uint admit_bounded_sample_monitor_a(void)

{
  uint uVar1;
  
  uVar1 = (uint)DAT_febe67e0;
  if (uVar1 != 0x5a) {
    if (DAT_febe67e2 < DAT_0002b71c) {
      DAT_febe67e2 = DAT_febe67e2 + 1;
    }
    else {
      uVar1 = 0x5a;
    }
  }
  DAT_febe67e0 = (char)uVar1;
  return uVar1;
}

void step_bounded_sample_or_status_a(void)

{
  ushort uVar1;
  ushort uVar2;
  ushort uVar3;
  uint32_t puVar4;
  uint uVar5;
  
  uVar3 = DAT_febe67e4;
  uVar2 = DAT_febe6764;
  uVar1 = DAT_0002b71e;
  puVar4 = 0xfebeb800u;
  if (DAT_febe67e4 < DAT_0002b71e) {
    puVar4 = 0xfebeb800u;
    uVar5 = admit_bounded_sample_monitor_a();
    if (uVar5 == 0x5a) {
      if (DAT_0002bb94 == 'Z') {
        force_unconfirmed_terminal_monitor_healthy
                  (camry_host_addr(((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xffffbe24u + (uint32_t)((int)puVar4)))))), 
                   (0x2b686u), (0x28418u))
        ;
      }
      else if ((uVar2 & 1) == 0) {
        step_terminal_monitor
                  (((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xffffbe24u + (uint32_t)((int)puVar4))))), ((F33MonitorLimits *)camry_host_ptr((uint32_t)((0x2b686u)))), ((F33TerminalMonitorCallbacks *)camry_host_ptr((uint32_t)((0x28418u)))))
        ;
      }
    }
    else {
      reset_terminal_monitor(((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xffffbe24u + (uint32_t)((int)puVar4))))));
    }
  }
  if (((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbe24u + (uint32_t)((int)puVar4) * 1u)))) == '\0') || (uVar1 <= uVar3)) {
    mark_redundant_byte_6884_for_codes_21_to_34_32036(0x16);
  }
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbe24u + (uint32_t)((int)puVar4) * 1u)))) == '\"') {
    retain_and_clear_fault_record(10);
    encode_fault_action_kind('\n','\x1d');
    select_current_fault_record(10);
  }
  return;
}

uint classify_bounded_sample_or_status_a(void)

{
  uint uVar1;
  
  if (((((DAT_febe64d8 == '\0') && (DAT_febe64d0 == '\0')) && ((DAT_febe6620 >> 2 & 1) != 0)) &&
      (((DAT_febe661c >> 2 & 1) != 0 && ((DAT_febe6628 >> 1 & 1) == 0)))) &&
     (((DAT_febe6614 & 1) == 0 && (DAT_febe65f0 == 'Z')))) {
    if ((DAT_febe66bc < DAT_0002b71a) || (DAT_febe8284 == 'Z')) {
      uVar1 = 0x22;
    }
    else {
      uVar1 = 0x11;
    }
  }
  else {
    DAT_febe67e4 = DAT_febe67e4 + 1;
    uVar1 = 0x44;
  }
  return uVar1;
}

void record_bounded_sample_or_status_a_healthy_observed(void)

{
  report_diagnostic_healthy_observed(0x89);
  return;
}

void record_bounded_sample_or_status_a_failure(void)

{
  report_diagnostic_event_failure(0x89,0x32);
  return;
}

undefined4 status_failing_bounded_sample_or_status_a_states(void)

{
  if (bounded_sample_or_status_a_states.failing_count != 0) {
    return 0x11;
  }
  return 0;
}

void reset_bounded_sample_or_status_b(void)

{
  reset_terminal_monitor(((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xfebe762cu)))));
  return;
}

void reset_bounded_sample_status_b_monitor_3f88e(void)

{
  DAT_febe67e8 = 0;
  DAT_febe67ec = 0;
  DAT_febe67ea = 0;
  reset_terminal_monitor(((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xfebe762cu)))));
  return;
}

uint admit_bounded_sample_monitor_b(void)

{
  uint uVar1;
  
  uVar1 = (uint)DAT_febe67e8;
  if (uVar1 != 0x5a) {
    if (DAT_febe67ea < DAT_0002b724) {
      DAT_febe67ea = DAT_febe67ea + 1;
    }
    else {
      uVar1 = 0x5a;
    }
  }
  DAT_febe67e8 = (char)uVar1;
  return uVar1;
}

void step_bounded_sample_or_status_b(void)

{
  ushort uVar1;
  ushort uVar2;
  ushort uVar3;
  uint32_t puVar4;
  uint uVar5;
  
  uVar3 = DAT_febe67ec;
  uVar2 = DAT_febe6764;
  uVar1 = DAT_0002b726;
  puVar4 = 0xfebeb800u;
  if (DAT_febe67ec < DAT_0002b726) {
    puVar4 = 0xfebeb800u;
    uVar5 = admit_bounded_sample_monitor_b();
    if (uVar5 == 0x5a) {
      if (DAT_0002bb98 == 'Z') {
        force_unconfirmed_terminal_monitor_healthy
                  (camry_host_addr(((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xffffbe2cu + (uint32_t)((int)puVar4)))))), 
                   (0x2b68au), (0x28424u))
        ;
      }
      else if ((uVar2 >> 1 & 1) == 0) {
        step_terminal_monitor
                  (((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xffffbe2cu + (uint32_t)((int)puVar4))))), ((F33MonitorLimits *)camry_host_ptr((uint32_t)((0x2b68au)))), ((F33TerminalMonitorCallbacks *)camry_host_ptr((uint32_t)((0x28424u)))))
        ;
      }
    }
    else {
      reset_terminal_monitor(((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xffffbe2cu + (uint32_t)((int)puVar4))))));
    }
  }
  if (((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbe2cu + (uint32_t)((int)puVar4) * 1u)))) == '\0') || (uVar1 <= uVar3)) {
    mark_redundant_byte_6885_for_codes_21_to_34_32050(0x16);
  }
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbe2cu + (uint32_t)((int)puVar4) * 1u)))) == '\"') {
    retain_and_clear_fault_record(0xb);
    encode_fault_action_kind('\v','\x1e');
    select_current_fault_record(0xb);
  }
  return;
}

uint classify_bounded_sample_or_status_b(void)

{
  uint uVar1;
  
  if (((((DAT_febe64d9 == '\0') && (DAT_febe64d1 == '\0')) && ((DAT_febe6620 >> 0x12 & 1) != 0)) &&
      (((DAT_febe661c >> 0x12 & 1) != 0 && ((DAT_febe6628 >> 0x11 & 1) == 0)))) &&
     (((DAT_febe6614 & 1) == 0 && (DAT_febe65f0 == 'Z')))) {
    if ((DAT_febe66be < DAT_0002b722) || (DAT_febe8283 == 'Z')) {
      uVar1 = 0x22;
    }
    else {
      uVar1 = 0x11;
    }
  }
  else {
    DAT_febe67ec = DAT_febe67ec + 1;
    uVar1 = 0x44;
  }
  return uVar1;
}

void record_bounded_sample_or_status_b_healthy_observed(void)

{
  report_diagnostic_healthy_observed(0x8a);
  return;
}

void record_bounded_sample_or_status_b_failure(void)

{
  report_diagnostic_event_failure(0x8a,0x32);
  return;
}

undefined4 status_failing_bounded_sample_or_status_b_states(void)

{
  if (bounded_sample_or_status_b_states.failing_count != 0) {
    return 0x11;
  }
  return 0;
}

void reset_requested_state_sample_threshold_a(void)

{
  reset_terminal_monitor(((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xfebe7634u)))));
  return;
}

void reset_requested_state_threshold_a_monitor_3fa1a(void)

{
  DAT_febe763c = 0;
  DAT_febe763d = 0;
  DAT_febe763e = 0;
  DAT_febe7640 = 0;
  reset_terminal_monitor(((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xfebe7634u)))));
  return;
}

bool delay_then_clear_channel_zero_owner_request_3fa36(void)

{
  bool bVar1;
  uint32_t puVar2;
  ushort uVar3;
  
  uVar3 = DAT_febe763e;
  puVar2 = 0xfebeb800u;
  bVar1 = DAT_febe763e < DAT_0002b72a;
  if (bVar1) {
    uVar3 = DAT_febe763e + 1;
  }
  else {
    puVar2 = 0xfebeb800u;
    set_channel_owner_request('\0',0);
  }
  (*((ushort *)camry_host_ptr((uint32_t)((0xffffbe3eu + (uint32_t)((int)puVar2)))))) = uVar3;
  return !bVar1;
}

undefined4 advance_requested_state_a_final_delay_3fa62(void)

{
  undefined4 uVar1;
  
  uVar1 = 1;
  if (DAT_febe7640 < DAT_0002b72c) {
    DAT_febe7640 = DAT_febe7640 + 1;
  }
  else {
    uVar1 = 2;
  }
  return uVar1;
}

uint admit_requested_state_sample_monitor_a(void)

{
  undefined *puVar1;
  uint uVar2;
  uint uVar3;
  
  puVar1 = ((undefined *)camry_host_ptr(0xfebeb800u));
  uVar3 = (uint)DAT_febe763d;
  uVar2 = (uint)DAT_febe763c;
  if (uVar3 != 0x5a) {
    if ((2 < uVar2) || (puVar1 = ((undefined *)camry_host_ptr(0xfebeb800u)), uVar2 == 0)) {
      puVar1 = ((undefined *)camry_host_ptr(0xfebeb800u));
      uVar2 = delay_then_clear_channel_zero_owner_request_3fa36();
    }
    if (uVar2 == 1) {
      uVar2 = advance_requested_state_a_final_delay_3fa62();
    }
    if (uVar2 == 2) {
      uVar3 = 0x5a;
    }
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbe3cu + (uint32_t)((int)camry_host_addr(puVar1)) * 1u)))) = (char)uVar2;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbe3du + (uint32_t)((int)camry_host_addr(puVar1)) * 1u)))) = (char)uVar3;
  return uVar3;
}

void step_requested_state_sample_threshold_a(void)

{
  ushort uVar1;
  uint32_t puVar2;
  uint uVar3;
  
  uVar1 = DAT_febe6764;
  puVar2 = 0xfebeb800u;
  uVar3 = admit_requested_state_sample_monitor_a();
  if (uVar3 == 0x5a) {
    if (DAT_0002bb9c == 'Z') {
      force_unconfirmed_terminal_monitor_healthy
                (camry_host_addr(((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xffffbe34u + (uint32_t)((int)puVar2)))))), 
                 (0x2b68eu), 
                 (0x28430u));
    }
    else if ((uVar1 & 1) == 0) {
      step_terminal_monitor
                (((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xffffbe34u + (uint32_t)((int)puVar2))))), ((F33MonitorLimits *)camry_host_ptr((uint32_t)((0x2b68eu)))), ((F33TerminalMonitorCallbacks *)camry_host_ptr((uint32_t)((0x28430u)))));
    }
  }
  else {
    reset_terminal_monitor(((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xffffbe34u + (uint32_t)((int)puVar2))))));
  }
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbe34u + (uint32_t)((int)puVar2) * 1u)))) == '\0') {
    mark_redundant_byte_6884_for_codes_21_to_34_32036(0x18);
  }
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbe34u + (uint32_t)((int)puVar2) * 1u)))) == '\"') {
    retain_and_clear_fault_record(10);
    encode_fault_action_kind('\n','\x1d');
    select_current_fault_record(10);
  }
  return;
}

uint classify_requested_state_sample_threshold_a(void)

{
  if (((((DAT_febe64d8 != '\x02') || (DAT_febe64d0 != '\0')) || ((DAT_febe6620 >> 2 & 1) == 0)) ||
      (((DAT_febe661c >> 2 & 1) == 0 || ((DAT_febe6628 >> 1 & 1) != 0)))) ||
     (((DAT_febe6614 & 1) == 0 || (DAT_febe65f0 != 'Z')))) {
    return 0x44;
  }
  if (((DAT_febe66b2 <= DAT_0002b730) || (DAT_0002b72e < DAT_febe66b8)) &&
     ((DAT_febe66b2 <= DAT_0002b732 || (DAT_febe66b8 <= DAT_0002b72e)))) {
    return 0x11;
  }
  return 0x22;
}

void record_requested_state_sample_threshold_a_healthy_observed(void)

{
  report_diagnostic_healthy_observed(0xef);
  return;
}

void record_requested_state_sample_threshold_a_failure(void)

{
  report_diagnostic_event_failure(0xef,0x32);
  return;
}

undefined4 status_failing_requested_state_sample_threshold_a_states(void)

{
  if (requested_state_sample_threshold_a_states.failing_count != 0) {
    return 0x11;
  }
  return 0;
}

void reset_requested_state_sample_threshold_b(void)

{
  reset_terminal_monitor(((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xfebe7644u)))));
  return;
}

void reset_requested_state_threshold_b_monitor_3fbf4(void)

{
  DAT_febe764c = 0;
  DAT_febe764d = 0;
  DAT_febe764e = 0;
  DAT_febe7650 = 0;
  reset_terminal_monitor(((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xfebe7644u)))));
  return;
}

bool delay_then_clear_channel_one_owner_request_3fc10(void)

{
  bool bVar1;
  uint32_t puVar2;
  ushort uVar3;
  
  uVar3 = DAT_febe764e;
  puVar2 = 0xfebeb800u;
  bVar1 = DAT_febe764e < DAT_0002b736;
  if (bVar1) {
    uVar3 = DAT_febe764e + 1;
  }
  else {
    puVar2 = 0xfebeb800u;
    set_channel_owner_request('\x01',0);
  }
  (*((ushort *)camry_host_ptr((uint32_t)((0xffffbe4eu + (uint32_t)((int)puVar2)))))) = uVar3;
  return !bVar1;
}

undefined4 advance_requested_state_b_final_delay_3fc3c(void)

{
  undefined4 uVar1;
  
  uVar1 = 1;
  if (DAT_febe7650 < DAT_0002b738) {
    DAT_febe7650 = DAT_febe7650 + 1;
  }
  else {
    uVar1 = 2;
  }
  return uVar1;
}

uint admit_requested_state_sample_monitor_b(void)

{
  undefined *puVar1;
  uint uVar2;
  uint uVar3;
  
  puVar1 = ((undefined *)camry_host_ptr(0xfebeb800u));
  uVar3 = (uint)DAT_febe764d;
  uVar2 = (uint)DAT_febe764c;
  if (uVar3 != 0x5a) {
    if ((2 < uVar2) || (puVar1 = ((undefined *)camry_host_ptr(0xfebeb800u)), uVar2 == 0)) {
      puVar1 = ((undefined *)camry_host_ptr(0xfebeb800u));
      uVar2 = delay_then_clear_channel_one_owner_request_3fc10();
    }
    if (uVar2 == 1) {
      uVar2 = advance_requested_state_b_final_delay_3fc3c();
    }
    if (uVar2 == 2) {
      uVar3 = 0x5a;
    }
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbe4cu + (uint32_t)((int)camry_host_addr(puVar1)) * 1u)))) = (char)uVar2;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbe4du + (uint32_t)((int)camry_host_addr(puVar1)) * 1u)))) = (char)uVar3;
  return uVar3;
}

void step_requested_state_sample_threshold_b(void)

{
  ushort uVar1;
  uint32_t puVar2;
  uint uVar3;
  
  uVar1 = DAT_febe6764;
  puVar2 = 0xfebeb800u;
  uVar3 = admit_requested_state_sample_monitor_b();
  if (uVar3 == 0x5a) {
    if (DAT_0002bba0 == 'Z') {
      force_unconfirmed_terminal_monitor_healthy
                (camry_host_addr(((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xffffbe44u + (uint32_t)((int)puVar2)))))), 
                 (0x2b692u), 
                 (0x2843cu));
    }
    else if ((uVar1 >> 1 & 1) == 0) {
      step_terminal_monitor
                (((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xffffbe44u + (uint32_t)((int)puVar2))))), ((F33MonitorLimits *)camry_host_ptr((uint32_t)((0x2b692u)))), ((F33TerminalMonitorCallbacks *)camry_host_ptr((uint32_t)((0x2843cu)))));
    }
  }
  else {
    reset_terminal_monitor(((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xffffbe44u + (uint32_t)((int)puVar2))))));
  }
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbe44u + (uint32_t)((int)puVar2) * 1u)))) == '\0') {
    mark_redundant_byte_6885_for_codes_21_to_34_32050(0x18);
  }
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbe44u + (uint32_t)((int)puVar2) * 1u)))) == '\"') {
    retain_and_clear_fault_record(0xb);
    encode_fault_action_kind('\v','\x1e');
    select_current_fault_record(0xb);
  }
  return;
}

uint classify_requested_state_sample_threshold_b(void)

{
  if (((((DAT_febe64d9 != '\x02') || (DAT_febe64d1 != '\0')) || ((DAT_febe6620 >> 0x12 & 1) == 0))
      || (((DAT_febe661c >> 0x12 & 1) == 0 || ((DAT_febe6628 >> 0x11 & 1) != 0)))) ||
     (((DAT_febe6614 & 1) == 0 || (DAT_febe65f0 != 'Z')))) {
    return 0x44;
  }
  if (((DAT_febe66b4 <= DAT_0002b73c) || (DAT_0002b73a < DAT_febe66b8)) &&
     ((DAT_febe66b4 <= DAT_0002b73e || (DAT_febe66b8 <= DAT_0002b73a)))) {
    return 0x11;
  }
  return 0x22;
}

void record_requested_state_sample_threshold_b_healthy_observed(void)

{
  report_diagnostic_healthy_observed(0xf0);
  return;
}

void record_requested_state_sample_threshold_b_failure(void)

{
  report_diagnostic_event_failure(0xf0,0x32);
  return;
}

undefined4 status_failing_requested_state_sample_threshold_b_states(void)

{
  if (requested_state_sample_threshold_b_states.failing_count != 0) {
    return 0x11;
  }
  return 0;
}

void reset_asserted_state_sample_threshold_a(void)

{
  reset_terminal_monitor(((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xfebe67f0u)))));
  return;
}

void reset_asserted_state_sample_threshold_a_3fdce(void)

{
  reset_terminal_monitor(((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xfebe67f0u)))));
  return;
}

void step_asserted_state_sample_threshold_a(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  if (DAT_0002bba4 == 'Z') {
    puVar1 = 0xfebeb800u;
    force_unconfirmed_terminal_monitor_healthy
              ((0xfebe67f0u),
               (0x2b696u),
               (0x28448u));
  }
  else if ((DAT_febe6764 & 1) == 0) {
    puVar1 = 0xfebeb800u;
    step_terminal_monitor
              (((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xfebe67f0u)))), ((F33MonitorLimits *)camry_host_ptr((uint32_t)((0x2b696u)))), ((F33TerminalMonitorCallbacks *)camry_host_ptr((uint32_t)((0x28448u)))));
  }
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x5010))))) == '\0') {
    mark_redundant_byte_6884_for_codes_21_to_34_32036(0x1e);
  }
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x5010))))) == '\"') {
    retain_and_clear_fault_record(10);
    encode_fault_action_kind('\n','\x1d');
    select_current_fault_record(10);
  }
  return;
}

uint classify_asserted_state_sample_threshold_a(void)

{
  if (((((DAT_febe64d8 != '\x02') || (DAT_febe64d0 != '\0')) || ((DAT_febe6620 >> 1 & 1) == 0)) ||
      (((DAT_febe6620 >> 2 & 1) != 0 || ((DAT_febe661c >> 2 & 1) == 0)))) ||
     (((DAT_febe6628 >> 1 & 1) == 0 || (((DAT_febe6614 & 1) != 0 || (DAT_febe65f0 != 'Z')))))) {
    return 0x44;
  }
  if (((DAT_0002b744 <= DAT_febe66b2) || (DAT_0002b742 < DAT_febe66b8)) &&
     ((DAT_0002b746 <= DAT_febe66b2 || (DAT_febe66b8 <= DAT_0002b742)))) {
    return 0x11;
  }
  return 0x22;
}

void record_asserted_state_sample_threshold_a_healthy_observed(void)

{
  report_diagnostic_healthy_observed(0x9d);
  return;
}

void record_asserted_state_sample_threshold_a_failure(void)

{
  report_diagnostic_event_failure(0x9d,0x32);
  return;
}

undefined4 status_failing_asserted_state_sample_threshold_a_states(void)

{
  if (asserted_state_sample_threshold_a_states.failing_count != 0) {
    return 0x11;
  }
  return 0;
}

void reset_asserted_state_sample_threshold_b(void)

{
  reset_terminal_monitor(((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xfebe67f8u)))));
  return;
}

void reset_asserted_state_sample_threshold_b_3ff08(void)

{
  reset_terminal_monitor(((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xfebe67f8u)))));
  return;
}

void step_asserted_state_sample_threshold_b(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  if (DAT_0002bba8 == 'Z') {
    puVar1 = 0xfebeb800u;
    force_unconfirmed_terminal_monitor_healthy
              ((0xfebe67f8u),
               (0x2b69au),
               (0x28454u));
  }
  else if ((DAT_febe6764 >> 1 & 1) == 0) {
    puVar1 = 0xfebeb800u;
    step_terminal_monitor
              (((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xfebe67f8u)))), ((F33MonitorLimits *)camry_host_ptr((uint32_t)((0x2b69au)))), ((F33TerminalMonitorCallbacks *)camry_host_ptr((uint32_t)((0x28454u)))));
  }
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x5008))))) == '\0') {
    mark_redundant_byte_6885_for_codes_21_to_34_32050(0x1e);
  }
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x5008))))) == '\"') {
    retain_and_clear_fault_record(0xb);
    encode_fault_action_kind('\v','\x1e');
    select_current_fault_record(0xb);
  }
  return;
}

uint classify_asserted_state_sample_threshold_b(void)

{
  if (((((DAT_febe64d9 != '\x02') || (DAT_febe64d1 != '\0')) || ((DAT_febe6620 >> 0x11 & 1) == 0))
      || (((DAT_febe6620 >> 0x12 & 1) != 0 || ((DAT_febe661c >> 0x12 & 1) == 0)))) ||
     (((DAT_febe6628 >> 0x11 & 1) == 0 || (((DAT_febe6614 & 1) != 0 || (DAT_febe65f0 != 'Z')))))) {
    return 0x44;
  }
  if (((DAT_0002b74c <= DAT_febe66b4) || (DAT_0002b74a < DAT_febe66b8)) &&
     ((DAT_0002b74e <= DAT_febe66b4 || (DAT_febe66b8 <= DAT_0002b74a)))) {
    return 0x11;
  }
  return 0x22;
}

void record_asserted_state_sample_threshold_b_healthy_observed(void)

{
  report_diagnostic_healthy_observed(199);
  return;
}
