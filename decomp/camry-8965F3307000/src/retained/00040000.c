#include "common.h"

void record_asserted_state_sample_threshold_b_failure(void)

{
  report_diagnostic_event_failure(199,0x32);
  return;
}

undefined4 status_failing_asserted_state_sample_threshold_b_states(void)

{
  if (asserted_state_sample_threshold_b_states.failing_count != 0) {
    return 0x11;
  }
  return 0;
}

void reset_sample_difference_window_a(void)

{
  reset_terminal_monitor(((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xfebe7654u)))));
  return;
}

void reset_sample_difference_a_monitor_40042(void)

{
  DAT_febe6800 = 0;
  DAT_febe6801 = 0;
  DAT_febe6802 = 0;
  DAT_febe6804 = 0;
  reset_terminal_monitor(((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xfebe7654u)))));
  return;
}

uint admit_sample_difference_monitor_a(void)

{
  int iVar1;
  uint uVar2;
  int iVar3;
  
  uVar2 = (uint)DAT_febe6800;
  iVar1 = (uint)DAT_febe66b8 - (uint)DAT_febe66ae;
  if (uVar2 != 0x5a) {
    if (DAT_febe65f0 == 'Z') {
      iVar3 = (int)DAT_0002b758;
      if ((iVar1 - iVar3 < 0 == (iVar1 < 0 != iVar3 < 0 && iVar3 < 0 == iVar1 - iVar3 < 0) &&
           iVar1 != iVar3) && (DAT_febe6802 <= DAT_0002b752)) {
        DAT_febe6802 = DAT_febe6802 + 1;
      }
      else {
        uVar2 = 0x5a;
      }
    }
    else {
      DAT_febe6802 = 0;
    }
  }
  DAT_febe6800 = (char)uVar2;
  return uVar2;
}

uint admit_sample_difference_elapsed_a(void)

{
  uint uVar1;
  
  uVar1 = (uint)DAT_febe6801;
  if (uVar1 != 0x5a) {
    if (DAT_febe6804 < DAT_0002b754) {
      DAT_febe6804 = DAT_febe6804 + 1;
    }
    else {
      uVar1 = 0x5a;
    }
  }
  DAT_febe6801 = (char)uVar1;
  return uVar1;
}

void step_sample_difference_window_a(void)

{
  ushort uVar1;
  uint32_t puVar2;
  uint uVar3;
  uint uVar4;
  
  uVar1 = DAT_febe6764;
  puVar2 = 0xfebeb800u;
  uVar3 = admit_sample_difference_monitor_a();
  uVar4 = admit_sample_difference_elapsed_a();
  if ((uVar3 == 0x5a) && (uVar4 == 0x5a)) {
    if (DAT_0002bbac == 'Z') {
      force_unconfirmed_terminal_monitor_healthy
                (camry_host_addr(((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xffffbe54u + (uint32_t)((int)puVar2)))))), 
                 (0x2b69eu), (0x28460u));
    }
    else if ((uVar1 & 1) == 0) {
      step_terminal_monitor
                (((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xffffbe54u + (uint32_t)((int)puVar2))))), ((F33MonitorLimits *)camry_host_ptr((uint32_t)((0x2b69eu)))), ((F33TerminalMonitorCallbacks *)camry_host_ptr((uint32_t)((0x28460u)))));
    }
  }
  else {
    reset_terminal_monitor(((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xffffbe54u + (uint32_t)((int)puVar2))))));
  }
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbe54u + (uint32_t)((int)puVar2) * 1u)))) == '\0') {
    mark_redundant_byte_6884_for_codes_21_to_34_32036(0x15);
  }
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbe54u + (uint32_t)((int)puVar2) * 1u)))) == '\"') {
    retain_and_clear_fault_record(10);
    encode_fault_action_kind('\n','\x1d');
    encode_fault_action_kind('\n','2');
    select_current_fault_record(10);
  }
  return;
}

uint classify_sample_difference_window_a(void)

{
  int iVar1;
  uint uVar2;
  int iVar3;
  
  uVar2 = (uint)DAT_febe66b8;
  iVar1 = uVar2 - DAT_febe66ae;
  if (((((DAT_febe64d8 != '\0') || (DAT_febe64d0 != '\0')) || ((DAT_febe6620 >> 2 & 1) == 0)) ||
      (((DAT_febe661c >> 2 & 1) == 0 || ((DAT_febe6628 >> 1 & 1) != 0)))) ||
     (((DAT_febe6614 & 1) != 0 || (DAT_febe65f0 != 'Z')))) {
    return 0x44;
  }
  iVar3 = (int)DAT_0002b758;
  if (((iVar1 - iVar3 < 0 != (iVar1 < 0 != iVar3 < 0 && iVar3 < 0 == iVar1 - iVar3 < 0) ||
        iVar1 == iVar3) || (DAT_0002b756 < uVar2)) &&
     (((uint)DAT_0002b75a <= (uint)DAT_febe66ae || (uVar2 <= DAT_0002b756)))) {
    return 0x11;
  }
  return 0x22;
}

void record_sample_difference_window_a_healthy_observed(void)

{
  report_diagnostic_healthy_observed(0x79);
  return;
}

void record_sample_difference_window_a_failure(void)

{
  report_diagnostic_event_failure(0x79,0x32);
  return;
}

undefined4 status_failing_sample_difference_window_a_states(void)

{
  if (sample_difference_window_a_states.failing_count != 0) {
    return 0x11;
  }
  return 0;
}

void reset_sample_difference_window_b(void)

{
  reset_terminal_monitor(((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xfebe765cu)))));
  return;
}

void reset_sample_difference_b_monitor_40222(void)

{
  DAT_febe6808 = 0;
  DAT_febe6809 = 0;
  DAT_febe680a = 0;
  DAT_febe680c = 0;
  reset_terminal_monitor(((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xfebe765cu)))));
  return;
}

uint admit_sample_difference_monitor_b(void)

{
  int iVar1;
  uint uVar2;
  int iVar3;
  
  uVar2 = (uint)DAT_febe6808;
  iVar1 = (uint)DAT_febe66b8 - (uint)DAT_febe66b0;
  if (uVar2 != 0x5a) {
    if (DAT_febe65f0 == 'Z') {
      iVar3 = (int)DAT_0002b764;
      if ((iVar1 - iVar3 < 0 == (iVar1 < 0 != iVar3 < 0 && iVar3 < 0 == iVar1 - iVar3 < 0) &&
           iVar1 != iVar3) && (DAT_febe680a <= DAT_0002b75e)) {
        DAT_febe680a = DAT_febe680a + 1;
      }
      else {
        uVar2 = 0x5a;
      }
    }
    else {
      DAT_febe680a = 0;
    }
  }
  DAT_febe6808 = (char)uVar2;
  return uVar2;
}

uint admit_sample_difference_elapsed_b(void)

{
  uint uVar1;
  
  uVar1 = (uint)DAT_febe6809;
  if (uVar1 != 0x5a) {
    if (DAT_febe680c < DAT_0002b760) {
      DAT_febe680c = DAT_febe680c + 1;
    }
    else {
      uVar1 = 0x5a;
    }
  }
  DAT_febe6809 = (char)uVar1;
  return uVar1;
}

void step_sample_difference_window_b(void)

{
  ushort uVar1;
  uint32_t puVar2;
  uint uVar3;
  uint uVar4;
  
  uVar1 = DAT_febe6764;
  puVar2 = 0xfebeb800u;
  uVar3 = admit_sample_difference_monitor_b();
  uVar4 = admit_sample_difference_elapsed_b();
  if ((uVar3 == 0x5a) && (uVar4 == 0x5a)) {
    if (DAT_0002bbb0 == 'Z') {
      force_unconfirmed_terminal_monitor_healthy
                (camry_host_addr(((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xffffbe5cu + (uint32_t)((int)puVar2)))))), 
                 (0x2b6a2u), (0x2846cu));
    }
    else if ((uVar1 >> 1 & 1) == 0) {
      step_terminal_monitor
                (((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xffffbe5cu + (uint32_t)((int)puVar2))))), ((F33MonitorLimits *)camry_host_ptr((uint32_t)((0x2b6a2u)))), ((F33TerminalMonitorCallbacks *)camry_host_ptr((uint32_t)((0x2846cu)))));
    }
  }
  else {
    reset_terminal_monitor(((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xffffbe5cu + (uint32_t)((int)puVar2))))));
  }
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbe5cu + (uint32_t)((int)puVar2) * 1u)))) == '\0') {
    mark_redundant_byte_6885_for_codes_21_to_34_32050(0x15);
  }
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbe5cu + (uint32_t)((int)puVar2) * 1u)))) == '\"') {
    retain_and_clear_fault_record(0xb);
    encode_fault_action_kind('\v','\x1e');
    encode_fault_action_kind('\v','2');
    select_current_fault_record(0xb);
  }
  return;
}

uint classify_sample_difference_window_b(void)

{
  int iVar1;
  int iVar2;
  uint uVar3;
  
  uVar3 = (uint)DAT_febe66b8;
  iVar1 = uVar3 - DAT_febe66b0;
  if (((((DAT_febe64d9 != '\0') || (DAT_febe64d1 != '\0')) || ((DAT_febe6620 >> 0x12 & 1) == 0)) ||
      (((DAT_febe661c >> 0x12 & 1) == 0 || ((DAT_febe6628 >> 0x11 & 1) != 0)))) ||
     (((DAT_febe6614 & 1) != 0 || (DAT_febe65f0 != 'Z')))) {
    return 0x44;
  }
  iVar2 = (int)DAT_0002b764;
  if (((iVar1 - iVar2 < 0 != (iVar1 < 0 != iVar2 < 0 && iVar2 < 0 == iVar1 - iVar2 < 0) ||
        iVar1 == iVar2) || (DAT_0002b762 < uVar3)) &&
     (((uint)DAT_0002b766 <= (uint)DAT_febe66b0 || (uVar3 <= DAT_0002b762)))) {
    return 0x11;
  }
  return 0x22;
}

void record_sample_difference_window_b_healthy_observed(void)

{
  report_diagnostic_healthy_observed(0xb8);
  return;
}

void record_sample_difference_window_b_failure(void)

{
  report_diagnostic_event_failure(0xb8,0x32);
  return;
}

undefined4 status_failing_sample_difference_window_b_states(void)

{
  if (sample_difference_window_b_states.failing_count != 0) {
    return 0x11;
  }
  return 0;
}

void reset_matched_state2_status_bit_a(void)

{
  reset_terminal_monitor(((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xfebe7664u)))));
  return;
}

void reset_matched_state2_a_monitor_and_delays_40402(void)

{
  DAT_febe6811 = 0;
  DAT_febe6810 = 0;
  DAT_febe6812 = 0;
  DAT_febe6814 = 0;
  DAT_febe6816 = 0;
  DAT_febe6818 = 0;
  DAT_febe681a = 0;
  reset_terminal_monitor(((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xfebe7664u)))));
  return;
}

undefined4 advance_matched_state2_a_three_delays_40424(void)

{
  int iVar1;
  uint32_t puVar2;
  undefined4 uVar3;
  int iVar4;
  int iVar5;
  ushort uVar6;
  ushort uVar7;
  ushort uVar8;
  
  puVar2 = 0xfebeb800u;
  uVar3 = 0;
  iVar5 = 0;
  iVar4 = 0;
  if (DAT_febe6814 < DAT_0002b76c) {
    iVar1 = 0;
    uVar8 = DAT_febe6814 + 1;
  }
  else {
    iVar1 = 0x5a;
    uVar8 = DAT_febe6814;
  }
  if (DAT_febe6816 < DAT_0002b76e) {
    uVar7 = DAT_febe6816 + 1;
  }
  else {
    iVar5 = 0x5a;
    uVar7 = DAT_febe6816;
  }
  if (DAT_febe6818 < DAT_0002b770) {
    uVar6 = DAT_febe6818 + 1;
  }
  else {
    iVar4 = 0x5a;
    uVar6 = DAT_febe6818;
  }
  if (((iVar1 == 0x5a) && (iVar5 == 0x5a)) && (iVar4 == 0x5a)) {
    puVar2 = 0xfebeb800u;
    if ((DAT_febe6764 & 1) == 0) {
      puVar2 = 0xfebeb800u;
      set_priority_mask_8a9c_bounded2_56c26(DAT_febe6764 & 1,4);
    }
    uVar3 = 1;
  }
  (*((ushort *)camry_host_ptr((uint32_t)((0xffffb014u + (uint32_t)((int)puVar2)))))) = uVar8;
  (*((ushort *)camry_host_ptr((uint32_t)((0xffffb016u + (uint32_t)((int)puVar2)))))) = uVar7;
  (*((ushort *)camry_host_ptr((uint32_t)((0xffffb018u + (uint32_t)((int)puVar2)))))) = uVar6;
  return uVar3;
}

undefined4 advance_matched_state2_a_final_delay_4049e(void)

{
  undefined4 uVar1;
  
  uVar1 = 1;
  if (DAT_febe681a < DAT_0002b772) {
    DAT_febe681a = DAT_febe681a + 1;
  }
  else {
    uVar1 = 2;
  }
  return uVar1;
}

uint admit_matched_state2_status_monitor_a(void)

{
  undefined *puVar1;
  uint uVar2;
  int iVar3;
  uint uVar4;
  ushort uVar5;
  
  puVar1 = ((undefined *)camry_host_ptr(0xfebeb800u));
  uVar4 = (uint)DAT_febe6811;
  uVar2 = (uint)DAT_febe6810;
  uVar5 = DAT_febe6812;
  if (uVar4 != 0x5a) {
    if (DAT_0002b76a < DAT_febe6812) {
      iVar3 = 0x5a;
    }
    else {
      uVar5 = DAT_febe6812 + 1;
      iVar3 = 0;
    }
    if ((2 < uVar2) || (puVar1 = ((undefined *)camry_host_ptr(0xfebeb800u)), uVar2 == 0)) {
      puVar1 = ((undefined *)camry_host_ptr(0xfebeb800u));
      uVar2 = advance_matched_state2_a_three_delays_40424();
    }
    if (uVar2 == 1) {
      uVar2 = advance_matched_state2_a_final_delay_4049e();
    }
    if ((iVar3 == 0x5a) && (uVar2 == 2)) {
      uVar4 = 0x5a;
    }
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffb010u + (uint32_t)((int)camry_host_addr(puVar1)) * 1u)))) = (char)uVar2;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffb011u + (uint32_t)((int)camry_host_addr(puVar1)) * 1u)))) = (char)uVar4;
  *(ushort *)camry_host_ptr((uint32_t)(0xffffb012u + (uint32_t)camry_host_addr(puVar1))) = uVar5;
  return uVar4;
}

void step_matched_state2_status_bit_a(void)

{
  ushort uVar1;
  uint32_t puVar2;
  uint uVar3;
  
  uVar1 = DAT_febe6764;
  puVar2 = 0xfebeb800u;
  uVar3 = admit_matched_state2_status_monitor_a();
  if (uVar3 == 0x5a) {
    if (DAT_0002bbb4 == 'Z') {
      force_unconfirmed_terminal_monitor_healthy
                (camry_host_addr(((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xffffbe64u + (uint32_t)((int)puVar2)))))), 
                 (0x2b6a6u), (0x28478u))
      ;
    }
    else if ((uVar1 & 1) == 0) {
      step_terminal_monitor
                (((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xffffbe64u + (uint32_t)((int)puVar2))))), ((F33MonitorLimits *)camry_host_ptr((uint32_t)((0x2b6a6u)))), ((F33TerminalMonitorCallbacks *)camry_host_ptr((uint32_t)((0x28478u)))))
      ;
    }
  }
  else {
    reset_terminal_monitor(((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xffffbe64u + (uint32_t)((int)puVar2))))));
  }
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbe64u + (uint32_t)((int)puVar2) * 1u)))) == '\0') {
    mark_redundant_byte_6884_for_codes_21_to_34_32036(0x1f);
  }
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbe64u + (uint32_t)((int)puVar2) * 1u)))) == '\"') {
    retain_and_clear_fault_record(10);
    encode_fault_action_kind('\n','\x1d');
    select_current_fault_record(10);
  }
  return;
}

uint classify_matched_state2_status_bit_a(void)

{
  if ((((((DAT_febe64d8 == '\x02') && (DAT_febe64d0 == '\x02')) && ((DAT_febe6620 >> 1 & 1) == 0))
       && (((DAT_febe6620 >> 2 & 1) != 0 && ((DAT_febe661c >> 1 & 1) == 0)))) &&
      (((DAT_febe661c >> 2 & 1) != 0 &&
       (((DAT_febe6628 >> 1 & 1) == 0 && ((DAT_febe6614 & 1) == 0)))))) && (DAT_febe65f6 == 'Z')) {
    if (DAT_febe8282 != 'Z') {
      return 0x11;
    }
    return 0x22;
  }
  return 0x44;
}

void record_matched_state2_status_bit_a_healthy_observed(void)

{
  report_diagnostic_healthy_observed(0x78);
  return;
}

void record_matched_state2_status_bit_a_failure(void)

{
  report_diagnostic_event_failure(0x78,0x32);
  return;
}

undefined4 status_failing_matched_state2_status_bit_a_states(void)

{
  if (matched_state2_status_bit_a_states.failing_count != 0) {
    return 0x11;
  }
  return 0;
}

void reset_matched_state2_status_bit_b(void)

{
  reset_terminal_monitor(((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xfebe766cu)))));
  return;
}

void reset_matched_state2_b_monitor_and_delays_4063e(void)

{
  DAT_febe681d = 0;
  DAT_febe681c = 0;
  DAT_febe681e = 0;
  DAT_febe6820 = 0;
  DAT_febe6822 = 0;
  DAT_febe6824 = 0;
  DAT_febe6826 = 0;
  reset_terminal_monitor(((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xfebe766cu)))));
  return;
}

undefined4 advance_matched_state2_b_three_delays_40660(void)

{
  int iVar1;
  uint32_t puVar2;
  undefined4 uVar3;
  int iVar4;
  int iVar5;
  ushort uVar6;
  ushort uVar7;
  ushort uVar8;
  
  puVar2 = 0xfebeb800u;
  uVar3 = 0;
  iVar5 = 0;
  iVar4 = 0;
  if (DAT_febe6820 < DAT_0002b778) {
    iVar1 = 0;
    uVar8 = DAT_febe6820 + 1;
  }
  else {
    iVar1 = 0x5a;
    uVar8 = DAT_febe6820;
  }
  if (DAT_febe6822 < DAT_0002b77a) {
    uVar7 = DAT_febe6822 + 1;
  }
  else {
    iVar5 = 0x5a;
    uVar7 = DAT_febe6822;
  }
  if (DAT_febe6824 < DAT_0002b77c) {
    uVar6 = DAT_febe6824 + 1;
  }
  else {
    iVar4 = 0x5a;
    uVar6 = DAT_febe6824;
  }
  if (((iVar1 == 0x5a) && (iVar5 == 0x5a)) && (iVar4 == 0x5a)) {
    puVar2 = 0xfebeb800u;
    if ((DAT_febe6764 >> 1 & 1) == 0) {
      puVar2 = 0xfebeb800u;
      set_priority_mask_8a9c_bounded2_56c26(1,0x40000);
    }
    uVar3 = 1;
  }
  (*((ushort *)camry_host_ptr((uint32_t)((0xffffb020u + (uint32_t)((int)puVar2)))))) = uVar8;
  (*((ushort *)camry_host_ptr((uint32_t)((0xffffb022u + (uint32_t)((int)puVar2)))))) = uVar7;
  (*((ushort *)camry_host_ptr((uint32_t)((0xffffb024u + (uint32_t)((int)puVar2)))))) = uVar6;
  return uVar3;
}

undefined4 advance_matched_state2_b_final_delay_406da(void)

{
  undefined4 uVar1;
  
  uVar1 = 1;
  if (DAT_febe6826 < DAT_0002b77e) {
    DAT_febe6826 = DAT_febe6826 + 1;
  }
  else {
    uVar1 = 2;
  }
  return uVar1;
}

uint admit_matched_state2_status_monitor_b(void)

{
  undefined *puVar1;
  uint uVar2;
  int iVar3;
  uint uVar4;
  ushort uVar5;
  
  puVar1 = ((undefined *)camry_host_ptr(0xfebeb800u));
  uVar4 = (uint)DAT_febe681d;
  uVar2 = (uint)DAT_febe681c;
  uVar5 = DAT_febe681e;
  if (uVar4 != 0x5a) {
    if (DAT_0002b776 < DAT_febe681e) {
      iVar3 = 0x5a;
    }
    else {
      uVar5 = DAT_febe681e + 1;
      iVar3 = 0;
    }
    if ((2 < uVar2) || (puVar1 = ((undefined *)camry_host_ptr(0xfebeb800u)), uVar2 == 0)) {
      puVar1 = ((undefined *)camry_host_ptr(0xfebeb800u));
      uVar2 = advance_matched_state2_b_three_delays_40660();
    }
    if (uVar2 == 1) {
      uVar2 = advance_matched_state2_b_final_delay_406da();
    }
    if ((iVar3 == 0x5a) && (uVar2 == 2)) {
      uVar4 = 0x5a;
    }
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffb01cu + (uint32_t)((int)camry_host_addr(puVar1)) * 1u)))) = (char)uVar2;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffb01du + (uint32_t)((int)camry_host_addr(puVar1)) * 1u)))) = (char)uVar4;
  *(ushort *)camry_host_ptr((uint32_t)(0xffffb01eu + (uint32_t)camry_host_addr(puVar1))) = uVar5;
  return uVar4;
}

void step_matched_state2_status_bit_b(void)

{
  ushort uVar1;
  uint32_t puVar2;
  uint uVar3;
  
  uVar1 = DAT_febe6764;
  puVar2 = 0xfebeb800u;
  uVar3 = admit_matched_state2_status_monitor_b();
  if (uVar3 == 0x5a) {
    if (DAT_0002bbb8 == 'Z') {
      force_unconfirmed_terminal_monitor_healthy
                (camry_host_addr(((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xffffbe6cu + (uint32_t)((int)puVar2)))))), 
                 (0x2b6aau), (0x28484u))
      ;
    }
    else if ((uVar1 >> 1 & 1) == 0) {
      step_terminal_monitor
                (((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xffffbe6cu + (uint32_t)((int)puVar2))))), ((F33MonitorLimits *)camry_host_ptr((uint32_t)((0x2b6aau)))), ((F33TerminalMonitorCallbacks *)camry_host_ptr((uint32_t)((0x28484u)))))
      ;
    }
  }
  else {
    reset_terminal_monitor(((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xffffbe6cu + (uint32_t)((int)puVar2))))));
  }
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbe6cu + (uint32_t)((int)puVar2) * 1u)))) == '\0') {
    mark_redundant_byte_6885_for_codes_21_to_34_32050(0x1f);
  }
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbe6cu + (uint32_t)((int)puVar2) * 1u)))) == '\"') {
    retain_and_clear_fault_record(0xb);
    encode_fault_action_kind('\v','\x1e');
    select_current_fault_record(0xb);
  }
  return;
}

uint classify_matched_state2_status_bit_b(void)

{
  if ((((((DAT_febe64d9 == '\x02') && (DAT_febe64d1 == '\x02')) && ((DAT_febe6620 >> 0x11 & 1) == 0)
        ) && (((DAT_febe6620 >> 0x12 & 1) != 0 && ((DAT_febe661c >> 0x11 & 1) == 0)))) &&
      (((DAT_febe661c & 0x40000) != 0 &&
       (((DAT_febe6628 >> 0x11 & 1) == 0 && ((DAT_febe6614 & 1) == 0)))))) && (DAT_febe65f7 == 'Z'))
  {
    if (DAT_febe8281 != 'Z') {
      return 0x11;
    }
    return 0x22;
  }
  return 0x44;
}

void record_matched_state2_status_bit_b_healthy_observed(void)

{
  report_diagnostic_healthy_observed(0xc4);
  return;
}

void record_matched_state2_status_bit_b_failure(void)

{
  report_diagnostic_event_failure(0xc4,0x32);
  return;
}

undefined4 status_failing_matched_state2_status_bit_b_states(void)

{
  if (matched_state2_status_bit_b_states.failing_count != 0) {
    return 0x11;
  }
  return 0;
}

void reset_baseline_sample_threshold_a(void)

{
  reset_terminal_monitor(((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xfebe7674u)))));
  return;
}

void reset_baseline_threshold_a_monitor_4087e(void)

{
  DAT_febe6828 = 0;
  DAT_febe682a = 0;
  reset_terminal_monitor(((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xfebe7674u)))));
  return;
}

uint admit_baseline_sample_monitor_a(void)

{
  uint uVar1;
  
  uVar1 = (uint)DAT_febe6828;
  if (uVar1 != 0x5a) {
    if (DAT_febe682a < DAT_0002b788) {
      DAT_febe682a = DAT_febe682a + 1;
    }
    else {
      uVar1 = 0x5a;
    }
  }
  DAT_febe6828 = (char)uVar1;
  return uVar1;
}

void step_baseline_sample_threshold_a(void)

{
  ushort uVar1;
  uint32_t puVar2;
  uint uVar3;
  
  uVar1 = DAT_febe6764;
  puVar2 = 0xfebeb800u;
  uVar3 = admit_baseline_sample_monitor_a();
  if (uVar3 == 0x5a) {
    if (DAT_0002bbbc == 'Z') {
      force_unconfirmed_terminal_monitor_healthy
                (camry_host_addr(((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xffffbe74u + (uint32_t)((int)puVar2)))))), 
                 (0x2b6aeu), (0x28490u))
      ;
    }
    else if ((uVar1 & 1) == 0) {
      step_terminal_monitor
                (((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xffffbe74u + (uint32_t)((int)puVar2))))), ((F33MonitorLimits *)camry_host_ptr((uint32_t)((0x2b6aeu)))), ((F33TerminalMonitorCallbacks *)camry_host_ptr((uint32_t)((0x28490u)))))
      ;
    }
  }
  else {
    reset_terminal_monitor(((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xffffbe74u + (uint32_t)((int)puVar2))))));
  }
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbe74u + (uint32_t)((int)puVar2) * 1u)))) == '\0') {
    mark_redundant_byte_6884_for_codes_21_to_34_32036(0x17);
  }
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbe74u + (uint32_t)((int)puVar2) * 1u)))) == '\"') {
    retain_and_clear_fault_record(10);
    encode_fault_action_kind('\n','\x1d');
    select_current_fault_record(10);
  }
  return;
}

uint classify_baseline_sample_threshold_a(void)

{
  if (((((DAT_febe64d8 != '\0') || (DAT_febe64d0 != '\0')) || ((DAT_febe6620 >> 2 & 1) == 0)) ||
      (((DAT_febe661c >> 2 & 1) == 0 || ((DAT_febe6628 >> 1 & 1) != 0)))) ||
     (((DAT_febe6614 & 1) != 0 || (DAT_febe65f0 != 'Z')))) {
    return 0x44;
  }
  if (((DAT_febe66b2 <= DAT_0002b784) || (DAT_0002b782 < DAT_febe66b8)) &&
     ((DAT_febe66b2 <= DAT_0002b786 || (DAT_febe66b8 <= DAT_0002b782)))) {
    return 0x11;
  }
  return 0x22;
}

void record_baseline_sample_threshold_a_healthy_observed(void)

{
  report_diagnostic_healthy_observed(0x9c);
  return;
}

void record_baseline_sample_threshold_a_failure(void)

{
  report_diagnostic_event_failure(0x9c,0x32);
  return;
}

undefined4 status_failing_baseline_sample_threshold_a_states(void)

{
  if (baseline_sample_threshold_a_states.failing_count != 0) {
    return 0x11;
  }
  return 0;
}

void reset_baseline_sample_threshold_b(void)

{
  reset_terminal_monitor(((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xfebe767cu)))));
  return;
}

void reset_baseline_threshold_b_monitor_409f6(void)

{
  DAT_febe682c = 0;
  DAT_febe682e = 0;
  reset_terminal_monitor(((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xfebe767cu)))));
  return;
}

uint admit_baseline_sample_monitor_b(void)

{
  uint uVar1;
  
  uVar1 = (uint)DAT_febe682c;
  if (uVar1 != 0x5a) {
    if (DAT_febe682e < DAT_0002b790) {
      DAT_febe682e = DAT_febe682e + 1;
    }
    else {
      uVar1 = 0x5a;
    }
  }
  DAT_febe682c = (char)uVar1;
  return uVar1;
}

void step_baseline_sample_threshold_b(void)

{
  ushort uVar1;
  uint32_t puVar2;
  uint uVar3;
  
  uVar1 = DAT_febe6764;
  puVar2 = 0xfebeb800u;
  uVar3 = admit_baseline_sample_monitor_b();
  if (uVar3 == 0x5a) {
    if (DAT_0002bbc0 == 'Z') {
      force_unconfirmed_terminal_monitor_healthy
                (camry_host_addr(((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xffffbe7cu + (uint32_t)((int)puVar2)))))), 
                 (0x2b6b2u), (0x2849cu))
      ;
    }
    else if ((uVar1 >> 1 & 1) == 0) {
      step_terminal_monitor
                (((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xffffbe7cu + (uint32_t)((int)puVar2))))), ((F33MonitorLimits *)camry_host_ptr((uint32_t)((0x2b6b2u)))), ((F33TerminalMonitorCallbacks *)camry_host_ptr((uint32_t)((0x2849cu)))))
      ;
    }
  }
  else {
    reset_terminal_monitor(((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xffffbe7cu + (uint32_t)((int)puVar2))))));
  }
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbe7cu + (uint32_t)((int)puVar2) * 1u)))) == '\0') {
    mark_redundant_byte_6885_for_codes_21_to_34_32050(0x17);
  }
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbe7cu + (uint32_t)((int)puVar2) * 1u)))) == '\"') {
    retain_and_clear_fault_record(0xb);
    encode_fault_action_kind('\v','\x1e');
    select_current_fault_record(0xb);
  }
  return;
}

uint classify_baseline_sample_threshold_b(void)

{
  if (((((DAT_febe64d9 != '\0') || (DAT_febe64d1 != '\0')) || ((DAT_febe6620 >> 0x12 & 1) == 0)) ||
      (((DAT_febe661c >> 0x12 & 1) == 0 || ((DAT_febe6628 >> 0x11 & 1) != 0)))) ||
     (((DAT_febe6614 & 1) != 0 || (DAT_febe65f0 != 'Z')))) {
    return 0x44;
  }
  if (((DAT_febe66b4 <= DAT_0002b78c) || (DAT_0002b78a < DAT_febe66b8)) &&
     ((DAT_febe66b4 <= DAT_0002b78e || (DAT_febe66b8 <= DAT_0002b78a)))) {
    return 0x11;
  }
  return 0x22;
}

void record_baseline_sample_threshold_b_healthy_observed(void)

{
  report_diagnostic_healthy_observed(0xc6);
  return;
}

void record_baseline_sample_threshold_b_failure(void)

{
  report_diagnostic_event_failure(0xc6,0x32);
  return;
}

undefined4 status_failing_baseline_sample_threshold_b_states(void)

{
  if (baseline_sample_threshold_b_states.failing_count != 0) {
    return 0x11;
  }
  return 0;
}

void reset_observed_state_sample_regions_a(void)

{
  reset_terminal_monitor(((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xfebe7684u)))));
  return;
}

void reset_observed_state_regions_a_monitor_40b6e(void)

{
  DAT_febe6830 = 0;
  DAT_febe6831 = 0;
  DAT_febe6832 = 0;
  DAT_febe6836 = 0;
  DAT_febe6834 = 0;
  DAT_febe6838 = 0;
  reset_terminal_monitor(((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xfebe7684u)))));
  return;
}

undefined4 advance_observed_regions_a_first_delay_40b8e(void)

{
  uint32_t puVar1;
  undefined4 uVar2;
  ushort uVar3;
  
  uVar3 = DAT_febe6832;
  puVar1 = 0xfebeb800u;
  if (DAT_febe6832 < DAT_0002b792) {
    uVar2 = 0;
    uVar3 = DAT_febe6832 + 1;
  }
  else {
    puVar1 = 0xfebeb800u;
    if ((DAT_febe6764 & 1) == 0) {
      puVar1 = 0xfebeb800u;
      set_request_word_8a50_bounded5_569ac(DAT_febe6764 & 1,2);
    }
    uVar2 = 1;
  }
  (*((ushort *)camry_host_ptr((uint32_t)((0xffffb032u + (uint32_t)((int)puVar1)))))) = uVar3;
  return uVar2;
}

undefined4 advance_observed_regions_a_second_delay_40bc4(void)

{
  uint32_t puVar1;
  undefined4 uVar2;
  ushort uVar3;
  
  uVar3 = DAT_febe6836;
  puVar1 = 0xfebeb800u;
  if (DAT_febe6836 < DAT_0002b796) {
    uVar2 = 1;
    uVar3 = DAT_febe6836 + 1;
  }
  else {
    puVar1 = 0xfebeb800u;
    if ((DAT_febe6764 & 1) == 0) {
      puVar1 = 0xfebeb800u;
      set_secondary_priority_mask_bounded2_56f14(DAT_febe6764 & 1,2);
    }
    uVar2 = 2;
  }
  (*((ushort *)camry_host_ptr((uint32_t)((0xffffb036u + (uint32_t)((int)puVar1)))))) = uVar3;
  return uVar2;
}

undefined4 advance_observed_regions_a_third_delay_40bfa(void)

{
  undefined4 uVar1;
  
  uVar1 = 2;
  if (DAT_febe6834 < DAT_0002b794) {
    DAT_febe6834 = DAT_febe6834 + 1;
  }
  else {
    uVar1 = 3;
  }
  return uVar1;
}

undefined4 count_observed_regions_a_until_over_limit_40c18(void)

{
  undefined4 uVar1;
  
  if (DAT_0002b798 < DAT_febe6838) {
    uVar1 = 0x5a;
  }
  else {
    DAT_febe6838 = DAT_febe6838 + 1;
    uVar1 = 0;
  }
  return uVar1;
}

uint admit_observed_state_sample_monitor_a(void)

{
  undefined *puVar1;
  int iVar2;
  uint uVar3;
  uint uVar4;
  
  puVar1 = ((undefined *)camry_host_ptr(0xfebeb800u));
  uVar3 = (uint)DAT_febe6831;
  uVar4 = (uint)DAT_febe6830;
  if (uVar3 != 0x5a) {
    if ((3 < uVar4) || (puVar1 = ((undefined *)camry_host_ptr(0xfebeb800u)), uVar4 == 0)) {
      puVar1 = ((undefined *)camry_host_ptr(0xfebeb800u));
      uVar4 = advance_observed_regions_a_first_delay_40b8e();
    }
    if (uVar4 == 1) {
      uVar4 = advance_observed_regions_a_second_delay_40bc4();
    }
    if (uVar4 == 2) {
      uVar4 = advance_observed_regions_a_third_delay_40bfa();
    }
    if (((uVar4 < 4) && (iVar2 = count_observed_regions_a_until_over_limit_40c18(), uVar4 == 3)) && (iVar2 == 0x5a)) {
      uVar3 = 0x5a;
    }
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffb031u + (uint32_t)((int)camry_host_addr(puVar1)) * 1u)))) = (char)uVar3;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffb030u + (uint32_t)((int)camry_host_addr(puVar1)) * 1u)))) = (char)uVar4;
  return uVar3;
}

void step_observed_state_sample_regions_a(void)

{
  ushort uVar1;
  uint32_t puVar2;
  uint uVar3;
  
  uVar1 = DAT_febe6764;
  puVar2 = 0xfebeb800u;
  uVar3 = admit_observed_state_sample_monitor_a();
  if (uVar3 == 0x5a) {
    if (DAT_0002bbc4 == 'Z') {
      force_unconfirmed_terminal_monitor_healthy
                (camry_host_addr(((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xffffbe84u + (uint32_t)((int)puVar2)))))), 
                 (0x2b6b6u), 
                 (0x284a8u));
    }
    else if ((uVar1 & 1) == 0) {
      step_terminal_monitor
                (((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xffffbe84u + (uint32_t)((int)puVar2))))), ((F33MonitorLimits *)camry_host_ptr((uint32_t)((0x2b6b6u)))), ((F33TerminalMonitorCallbacks *)camry_host_ptr((uint32_t)((0x284a8u)))));
    }
  }
  else {
    reset_terminal_monitor(((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xffffbe84u + (uint32_t)((int)puVar2))))));
  }
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbe84u + (uint32_t)((int)puVar2) * 1u)))) == '\0') {
    mark_redundant_byte_6884_for_codes_21_to_34_32036(0x1c);
  }
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbe84u + (uint32_t)((int)puVar2) * 1u)))) == '\"') {
    retain_and_clear_fault_record(10);
    encode_fault_action_kind('\n','\x1d');
    select_current_fault_record(10);
  }
  return;
}

uint classify_observed_state_sample_regions_a(void)

{
  if (((((DAT_febe64d8 != '\0') || (DAT_febe64d0 != '\x02')) || ((DAT_febe6620 >> 2 & 1) == 0)) ||
      (((DAT_febe661c >> 1 & 1) == 0 || ((DAT_febe661c >> 2 & 1) != 0)))) ||
     (((DAT_febe6628 >> 1 & 1) == 0 || (((DAT_febe6614 & 1) != 0 || (DAT_febe65f0 != 'Z')))))) {
    return 0x44;
  }
  if (((DAT_0002b79e <= DAT_febe66b2) || (DAT_0002b79a < DAT_febe66b8)) &&
     ((((((DAT_0002b7a0 <= DAT_febe66b2 || (DAT_febe66b8 <= DAT_0002b79a)) ||
         (DAT_0002b79c < DAT_febe66b8)) &&
        (((DAT_0002b7a2 <= DAT_febe66b2 || (DAT_febe66b8 <= DAT_0002b79c)) &&
         ((DAT_febe66b2 <= DAT_0002b7a4 || (DAT_0002b79a < DAT_febe66b8)))))) &&
       (((DAT_febe66b2 <= DAT_0002b7a6 || (DAT_febe66b8 <= DAT_0002b79a)) ||
        (DAT_0002b79c < DAT_febe66b8)))) &&
      ((DAT_febe66b2 <= DAT_0002b7a8 || (DAT_febe66b8 <= DAT_0002b79c)))))) {
    return 0x11;
  }
  return 0x22;
}

void record_observed_state_sample_regions_a_healthy_observed(void)

{
  report_diagnostic_healthy_observed(0x7b);
  return;
}

void record_observed_state_sample_regions_a_failure(void)

{
  report_diagnostic_event_failure(0x7b,0x32);
  return;
}

undefined4 status_failing_observed_state_sample_regions_a_states(void)

{
  if (observed_state_sample_regions_a_states.failing_count != 0) {
    return 0x11;
  }
  return 0;
}

void reset_observed_state_sample_regions_b(void)

{
  reset_terminal_monitor(((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xfebe768cu)))));
  return;
}

void reset_observed_state_regions_b_monitor_40e08(void)

{
  DAT_febe683c = 0;
  DAT_febe683d = 0;
  DAT_febe683e = 0;
  DAT_febe6842 = 0;
  DAT_febe6840 = 0;
  DAT_febe6844 = 0;
  reset_terminal_monitor(((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xfebe768cu)))));
  return;
}

undefined4 advance_observed_regions_b_first_delay_40e28(void)

{
  uint32_t puVar1;
  undefined4 uVar2;
  ushort uVar3;
  
  uVar3 = DAT_febe683e;
  puVar1 = 0xfebeb800u;
  if (DAT_febe683e < DAT_0002b7aa) {
    uVar2 = 0;
    uVar3 = DAT_febe683e + 1;
  }
  else {
    puVar1 = 0xfebeb800u;
    if ((DAT_febe6764 >> 1 & 1) == 0) {
      puVar1 = 0xfebeb800u;
      set_request_word_8a50_bounded5_569ac(1,0x20000);
    }
    uVar2 = 1;
  }
  (*((ushort *)camry_host_ptr((uint32_t)((0xffffb03eu + (uint32_t)((int)puVar1)))))) = uVar3;
  return uVar2;
}

undefined4 advance_observed_regions_b_second_delay_40e5e(void)

{
  uint32_t puVar1;
  undefined4 uVar2;
  ushort uVar3;
  
  uVar3 = DAT_febe6842;
  puVar1 = 0xfebeb800u;
  uVar2 = 1;
  if (DAT_febe6842 < DAT_0002b7ae) {
    uVar3 = DAT_febe6842 + 1;
  }
  else {
    puVar1 = 0xfebeb800u;
    if ((DAT_febe6764 >> 1 & 1) == 0) {
      puVar1 = 0xfebeb800u;
      set_secondary_priority_mask_bounded2_56f14(1,0x20000);
    }
    uVar2 = 2;
  }
  (*((ushort *)camry_host_ptr((uint32_t)((int)(0xffffb042u + (uint32_t)((int)puVar1)))))) = uVar3;
  return uVar2;
}

undefined4 advance_observed_regions_b_third_delay_40e94(void)

{
  undefined4 uVar1;
  
  uVar1 = 2;
  if (DAT_febe6840 < DAT_0002b7ac) {
    DAT_febe6840 = DAT_febe6840 + 1;
  }
  else {
    uVar1 = 3;
  }
  return uVar1;
}

undefined4 count_observed_regions_b_until_over_limit_40eb2(void)

{
  undefined4 uVar1;
  
  if (DAT_0002b7b0 < DAT_febe6844) {
    uVar1 = 0x5a;
  }
  else {
    DAT_febe6844 = DAT_febe6844 + 1;
    uVar1 = 0;
  }
  return uVar1;
}

uint admit_observed_state_sample_monitor_b(void)

{
  undefined *puVar1;
  int iVar2;
  uint uVar3;
  uint uVar4;
  
  puVar1 = ((undefined *)camry_host_ptr(0xfebeb800u));
  uVar3 = (uint)DAT_febe683d;
  uVar4 = (uint)DAT_febe683c;
  if (uVar3 != 0x5a) {
    if ((3 < uVar4) || (puVar1 = ((undefined *)camry_host_ptr(0xfebeb800u)), uVar4 == 0)) {
      puVar1 = ((undefined *)camry_host_ptr(0xfebeb800u));
      uVar4 = advance_observed_regions_b_first_delay_40e28();
    }
    if (uVar4 == 1) {
      uVar4 = advance_observed_regions_b_second_delay_40e5e();
    }
    if (uVar4 == 2) {
      uVar4 = advance_observed_regions_b_third_delay_40e94();
    }
    if (((uVar4 < 4) && (iVar2 = count_observed_regions_b_until_over_limit_40eb2(), uVar4 == 3)) && (iVar2 == 0x5a)) {
      uVar3 = 0x5a;
    }
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffb03du + (uint32_t)((int)camry_host_addr(puVar1)) * 1u)))) = (char)uVar3;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffb03cu + (uint32_t)((int)camry_host_addr(puVar1)) * 1u)))) = (char)uVar4;
  return uVar3;
}

void step_observed_state_sample_regions_b(void)

{
  ushort uVar1;
  uint32_t puVar2;
  uint uVar3;
  
  uVar1 = DAT_febe6764;
  puVar2 = 0xfebeb800u;
  uVar3 = admit_observed_state_sample_monitor_b();
  if (uVar3 == 0x5a) {
    if (DAT_0002bbc8 == 'Z') {
      force_unconfirmed_terminal_monitor_healthy
                (camry_host_addr(((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xffffbe8cu + (uint32_t)((int)puVar2)))))), 
                 (0x2b6bau), 
                 (0x284b4u));
    }
    else if ((uVar1 >> 1 & 1) == 0) {
      step_terminal_monitor
                (((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xffffbe8cu + (uint32_t)((int)puVar2))))), ((F33MonitorLimits *)camry_host_ptr((uint32_t)((0x2b6bau)))), ((F33TerminalMonitorCallbacks *)camry_host_ptr((uint32_t)((0x284b4u)))));
    }
  }
  else {
    reset_terminal_monitor(((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xffffbe8cu + (uint32_t)((int)puVar2))))));
  }
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbe8cu + (uint32_t)((int)puVar2) * 1u)))) == '\0') {
    mark_redundant_byte_6885_for_codes_21_to_34_32050(0x1c);
  }
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbe8cu + (uint32_t)((int)puVar2) * 1u)))) == '\"') {
    retain_and_clear_fault_record(0xb);
    encode_fault_action_kind('\v','\x1e');
    select_current_fault_record(0xb);
  }
  return;
}

uint classify_observed_state_sample_regions_b(void)

{
  if (((((DAT_febe64d9 != '\0') || (DAT_febe64d1 != '\x02')) || ((DAT_febe6620 >> 0x12 & 1) == 0))
      || (((DAT_febe661c >> 0x11 & 1) == 0 || ((DAT_febe661c & 0x40000) != 0)))) ||
     (((DAT_febe6628 >> 0x11 & 1) == 0 || (((DAT_febe6614 & 1) != 0 || (DAT_febe65f0 != 'Z')))))) {
    return 0x44;
  }
  if (((DAT_0002b7b6 <= DAT_febe66b4) || (DAT_0002b7b2 < DAT_febe66b8)) &&
     ((((((DAT_0002b7b8 <= DAT_febe66b4 || (DAT_febe66b8 <= DAT_0002b7b2)) ||
         (DAT_0002b7b4 < DAT_febe66b8)) &&
        (((DAT_0002b7ba <= DAT_febe66b4 || (DAT_febe66b8 <= DAT_0002b7b4)) &&
         ((DAT_febe66b4 <= DAT_0002b7bc || (DAT_0002b7b2 < DAT_febe66b8)))))) &&
       (((DAT_febe66b4 <= DAT_0002b7be || (DAT_febe66b8 <= DAT_0002b7b2)) ||
        (DAT_0002b7b4 < DAT_febe66b8)))) &&
      ((DAT_febe66b4 <= DAT_0002b7c0 || (DAT_febe66b8 <= DAT_0002b7b4)))))) {
    return 0x11;
  }
  return 0x22;
}
