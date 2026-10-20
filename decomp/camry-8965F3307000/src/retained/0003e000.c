#include "common.h"

void run_init_chain_3e032(void)

{
  report_diagnostic_healthy_observed(0xfb);
  report_diagnostic_healthy_observed(0xfc);
  report_diagnostic_healthy_observed(0xfd);
  report_diagnostic_healthy_observed(0xfe);
  return;
}

void report_events_fb_to_fe_from_7544_flags_3e05a(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  if (DAT_febe7544 == 'Z') {
    puVar1 = 0xfebeb800u;
    report_diagnostic_event_failure(0xfb,10);
  }
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbd45u + (uint32_t)((int)puVar1) * 1u)))) == 'Z') {
    report_diagnostic_event_failure(0xfc,10);
  }
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbd46u + (uint32_t)((int)puVar1) * 1u)))) == 'Z') {
    report_diagnostic_event_failure(0xfd,10);
  }
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbd47u + (uint32_t)((int)puVar1) * 1u)))) == 'Z') {
    report_diagnostic_event_failure(0xfe,10);
  }
  return;
}

void return_only_stub_3e0b2(void)

{
  return;
}

void clear_754f_through_7552_flags_3e0b4(void)

{
  DAT_febe754f = 0;
  DAT_febe7550 = 0;
  DAT_febe7551 = 0;
  DAT_febe7552 = 0;
  return;
}

uint classify_paired_source_sample_differences(void)

{
  int iVar1;
  uint uVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  
  iVar1 = (int)DAT_0002b65a;
  iVar3 = (int)(short)(DAT_febe8250 - DAT_febe8252);
  iVar4 = (int)(short)(DAT_febe824c - DAT_febe824e);
  uVar2 = 0;
  iVar5 = (int)(short)(DAT_febe824c - DAT_febe8250);
  if ((iVar4 - iVar1 < 0 == (iVar4 < 0 != iVar1 < 0 && iVar1 < 0 == iVar4 - iVar1 < 0) &&
       iVar4 != iVar1) ||
     (iVar4 + iVar1 < 0 != (iVar4 < 0 != -iVar1 < 0 && -iVar1 < 0 == iVar4 + iVar1 < 0))) {
    uVar2 = 1;
  }
  iVar1 = (int)DAT_0002b65c;
  if ((iVar3 - iVar1 < 0 == (iVar3 < 0 != iVar1 < 0 && iVar1 < 0 == iVar3 - iVar1 < 0) &&
       iVar3 != iVar1) ||
     (iVar3 + iVar1 < 0 != (iVar3 < 0 != -iVar1 < 0 && -iVar1 < 0 == iVar3 + iVar1 < 0))) {
    uVar2 = uVar2 | 4;
  }
  iVar1 = (int)DAT_0002b65e;
  if ((iVar5 - iVar1 < 0 == (iVar5 < 0 != iVar1 < 0 && iVar1 < 0 == iVar5 - iVar1 < 0) &&
       iVar5 != iVar1) ||
     (iVar5 + iVar1 < 0 != (iVar5 < 0 != -iVar1 < 0 && -iVar1 < 0 == iVar5 + iVar1 < 0))) {
    uVar2 = uVar2 | 2;
  }
  return uVar2;
}

uint classify_paired_source_difference_first(uint mask)

{
  uint uVar1;
  
  uVar1 = 0;
  if ((((mask & 1) != 0) || ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe755cu + (uint32_t)(6) * 1u)))) == '\"')) ||
     ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe755cu + (uint32_t)(7) * 1u)))) == '\"')) {
    uVar1 = 0x5a;
  }
  return uVar1;
}

uint classify_paired_source_difference_middle(uint mask)

{
  uint uVar1;
  
  uVar1 = 0;
  if ((((mask >> 1 & 1) != 0) || ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe755cu + (uint32_t)(6) * 1u)))) == '\"')) ||
     ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe755cu + (uint32_t)(8) * 1u)))) == '\"')) {
    uVar1 = 0x5a;
  }
  return uVar1;
}

uint classify_paired_source_difference_last(uint mask)

{
  uint uVar1;
  
  uVar1 = 0;
  if ((((mask >> 2 & 1) != 0) || ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe755cu + (uint32_t)(8) * 1u)))) == '\"')) ||
     ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe755cu + (uint32_t)(9) * 1u)))) == '\"')) {
    uVar1 = 0x5a;
  }
  return uVar1;
}

void accumulate_paired_source_difference_counts(void)

{
  uint32_t puVar1;
  uint uVar2;
  uint uVar3;
  uint uVar4;
  char cVar5;
  char cVar6;
  char cVar7;
  char cVar8;
  
  cVar5 = DAT_febe7552;
  cVar6 = DAT_febe7551;
  cVar7 = DAT_febe7550;
  cVar8 = DAT_febe754f;
  puVar1 = 0xfebeb800u;
  uVar2 = classify_paired_source_sample_differences();
  uVar3 = classify_paired_source_difference_first(uVar2);
  uVar4 = classify_paired_source_difference_middle(uVar2);
  uVar2 = classify_paired_source_difference_last(uVar2);
  if (uVar3 == 0) {
    if (uVar2 == 0) goto LAB_0003e1c2;
    if (uVar4 == 0) goto LAB_0003e1b4;
  }
  else {
    if (uVar4 == 0) {
      cVar7 = cVar7 + '\x01';
      if (uVar2 == 0) goto LAB_0003e1c2;
LAB_0003e1b4:
      cVar5 = cVar5 + '\x01';
      goto LAB_0003e1c2;
    }
    cVar8 = cVar8 + '\x01';
    if (uVar2 == 0) goto LAB_0003e1c2;
  }
  cVar6 = cVar6 + '\x01';
LAB_0003e1c2:
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbd4cu + (uint32_t)((int)puVar1) * 1u)))) = (char)uVar3;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbd4du + (uint32_t)((int)puVar1) * 1u)))) = (char)uVar4;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbd4eu + (uint32_t)((int)puVar1) * 1u)))) = (char)uVar2;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbd4fu + (uint32_t)((int)puVar1) * 1u)))) = cVar8;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbd50u + (uint32_t)((int)puVar1) * 1u)))) = cVar7;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbd51u + (uint32_t)((int)puVar1) * 1u)))) = cVar6;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbd52u + (uint32_t)((int)puVar1) * 1u)))) = cVar5;
  return;
}

void return_only_stub_3e1d8(void)

{
  return;
}

void fill_constant_block_3e1da(void)

{
  DAT_febe7554 = 0;
  DAT_febe7555 = 0;
  DAT_febe7556 = 0;
  DAT_febe7557 = 0;
  DAT_febe7558 = 0;
  return;
}

void publish_paired_source_difference_changes(void)

{
  DAT_febe7554 = DAT_febe642c != DAT_febe7555;
  if (DAT_febe642d != DAT_febe7556) {
    DAT_febe7554 = DAT_febe7554 | 2;
  }
  if (DAT_febe642e != DAT_febe7557) {
    DAT_febe7554 = DAT_febe7554 | 0x10;
  }
  if (DAT_febe642f != DAT_febe7558) {
    DAT_febe7554 = DAT_febe7554 | 0x20;
  }
  DAT_febe7555 = DAT_febe642c;
  DAT_febe7556 = DAT_febe642d;
  DAT_febe7557 = DAT_febe642e;
  DAT_febe7558 = DAT_febe642f;
  return;
}

void return_only_stub_3e22c(void)

{
  return;
}

void return_only_stub_3e22e(void)

{
  return;
}

void publish_paired_source_monitor_actions(void)

{
  char cVar1;
  char cVar2;
  char cVar3;
  uint32_t puVar4;
  uchar uVar5;
  
  cVar2 = DAT_febe7bc3;
  cVar1 = DAT_febe7bc2;
  puVar4 = 0xfebeb800u;
  retain_and_clear_fault_record(4);
  if ((((((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbd71u + (uint32_t)((int)puVar4) * 1u)))) |
         (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbd70u + (uint32_t)((int)puVar4) * 1u)))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbd6cu + (uint32_t)((int)puVar4) * 1u)))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbd6au + (uint32_t)((int)puVar4) * 1u)))))
        & 0x11) == 0x11) &&
      ((byte)((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe755cu + (uint32_t)(7) * 1u)))) |
             (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe755cu + (uint32_t)(6) * 1u)))) |
             (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe755cu + (uint32_t)(2) * 1u)))) | ((volatile uint8_t *)camry_host_ptr(0xfebe755cu))[0]) == 0x11)) ||
     (((((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbd73u + (uint32_t)((int)puVar4) * 1u)))) |
        (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbd72u + (uint32_t)((int)puVar4) * 1u)))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbd6du + (uint32_t)((int)puVar4) * 1u)))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbd6bu + (uint32_t)((int)puVar4) * 1u)))))
       & 0x11) == 0x11 &&
      ((byte)((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe755cu + (uint32_t)(9) * 1u)))) |
             (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe755cu + (uint32_t)(8) * 1u)))) |
             (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe755cu + (uint32_t)(3) * 1u)))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe755cu + (uint32_t)(1) * 1u))))) == 0x11))))
  {
    cVar3 = 'Z';
  }
  else {
    cVar3 = '\0';
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbd66u + (uint32_t)((int)puVar4) * 1u)))) = cVar3;
  if (cVar3 != 'Z') {
    (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffbd76u + (uint32_t)((int)puVar4)))))) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar4 + -0x556e))));
    (*((undefined4 *)camry_host_ptr((uint32_t)((0xffffbd78u + (uint32_t)((int)puVar4)))))) = (*((undefined4 *)camry_host_ptr((uint32_t)(puVar4 + -0x5568))));
  }
  if ((((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe755cu + (uint32_t)(7) * 1u)))) |
       (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe755cu + (uint32_t)(6) * 1u)))) |
       (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe755cu + (uint32_t)(2) * 1u)))) | ((volatile uint8_t *)camry_host_ptr(0xfebe755cu))[0]) & 0x22) == 0x22) {
    encode_fault_action_kind('\x04','5');
  }
  if ((((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe755cu + (uint32_t)(9) * 1u)))) |
       (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe755cu + (uint32_t)(8) * 1u)))) |
       (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe755cu + (uint32_t)(3) * 1u)))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe755cu + (uint32_t)(1) * 1u))))) & 0x22) == 0x22) {
    encode_fault_action_kind('\x04','6');
  }
  select_current_fault_record(4);
  if ((cVar1 == 'Z') || (cVar2 == 'Z')) {
    DAT_febe7569 = 0x5a;
  }
  else {
    DAT_febe7569 = 0;
  }
  uVar5 = '\0';
  DAT_febe7574 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe755cu + (uint32_t)(7) * 1u)))) |
                 (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe755cu + (uint32_t)(6) * 1u)))) |
                 (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe755cu + (uint32_t)(2) * 1u)))) | ((volatile uint8_t *)camry_host_ptr(0xfebe755cu))[0];
  DAT_febe7567 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe755cu + (uint32_t)(9) * 1u)))) |
                 (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe755cu + (uint32_t)(8) * 1u)))) |
                 (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe755cu + (uint32_t)(3) * 1u)))) |
                 (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe755cu + (uint32_t)(1) * 1u)))) | DAT_febe7574;
  DAT_febe7575 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe755cu + (uint32_t)(9) * 1u)))) |
                 (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe755cu + (uint32_t)(8) * 1u)))) |
                 (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe755cu + (uint32_t)(3) * 1u)))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe755cu + (uint32_t)(1) * 1u))));
  DAT_febe7568 = 0x11;
  if (DAT_febe7567 == 0) {
    DAT_febe7568 = 0;
  }
  else {
    uVar5 = '\x11';
  }
  set_diagnostic_cache_blocker('\x02',uVar5);
  uVar5 = '\0';
  if ((((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe755cu + (uint32_t)(9) * 1u)))) |
       (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe755cu + (uint32_t)(8) * 1u)))) |
       (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe755cu + (uint32_t)(3) * 1u)))) |
       (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe755cu + (uint32_t)(1) * 1u)))) |
       (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe755cu + (uint32_t)(7) * 1u)))) |
       (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe755cu + (uint32_t)(6) * 1u)))) |
       (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe755cu + (uint32_t)(2) * 1u)))) | ((volatile uint8_t *)camry_host_ptr(0xfebe755cu))[0]) & 0x11) == 0x11) {
    uVar5 = 'Z';
  }
  set_monitor_pending_projection('\0',uVar5);
  return;
}

void publish_paired_source_monitor_status(uint index,uint packed)

{
  uint uVar1;
  
  uVar1 = index & 0xff;
  if (uVar1 < 10) {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe755cu + (uint32_t)(uVar1) * 1u)))) = (uchar)packed;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe756au + (uint32_t)(uVar1) * 1u)))) = (uchar)(packed >> 0x10);
  }
  return;
}

void reset_windowed_monitor_febe757c(void)

{
  reset_windowed_monitor((F33WindowedMonitorState *)((undefined *)camry_host_ptr(0xfebe757cu)));
  return;
}

void reset_windowed_monitor_febe757c_3e3ea(void)

{
  reset_windowed_monitor((F33WindowedMonitorState *)((undefined *)camry_host_ptr(0xfebe757cu)));
  return;
}

void step_paired_source_mask_monitor_a(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  if (DAT_0002bb70 == 'Z') {
    reset_windowed_monitor((F33WindowedMonitorState *)((undefined *)camry_host_ptr(0xfebe757cu)));
  }
  else if ((DAT_febe71ec >> 7 & 1) == 0) {
    step_windowed_monitor
              ((F33WindowedMonitorState *)((undefined *)camry_host_ptr(0xfebe757cu)),(F33WindowedMonitorLimits *)((undefined *)camry_host_ptr(0x2b64au)),
               (F33TwoSidedMonitorCallbacks *)
               &PTR_classify_paired_source_status_masks_a_0002835c);
  }
  else {
    classify_counter_limits_and_clear_selected_fields_6ae48((undefined4 *)camry_host_ptr(0xfebe757cu), (ushort *)camry_host_ptr(0x2b64au));
  }
  publish_paired_source_monitor_status(2,(*((uint *)camry_host_ptr((uint32_t)((0xffffbd7cu + (uint32_t)((int)puVar1)))))));
  return;
}

uint classify_paired_source_status_masks_a(void)

{
  if (((DAT_febe7bc2 == 'Z') || (DAT_febe7bc3 == 'Z')) &&
     (((volatile uint8_t *)camry_host_ptr(0xfebe755cu))[0] == '\0')) {
    if (((DAT_0002b662 & DAT_febe6360) == 0) && ((DAT_0002b664 & DAT_febe6362) == 0)) {
      return 0x11;
    }
    return 0x22;
  }
  return 0x44;
}

void report_diagnostic_healthy_observed_4d_3e48a(void)

{
  report_diagnostic_healthy_observed(0x4d);
  return;
}

void report_diagnostic_event_failure_4d_10_3e49a(void)

{
  report_diagnostic_event_failure(0x4d,10);
  return;
}

void reset_windowed_monitor_febe758c(void)

{
  reset_windowed_monitor((F33WindowedMonitorState *)((undefined *)camry_host_ptr(0xfebe758cu)));
  return;
}

void reset_windowed_monitor_febe758c_3e4bc(void)

{
  reset_windowed_monitor((F33WindowedMonitorState *)((undefined *)camry_host_ptr(0xfebe758cu)));
  return;
}

void step_paired_source_mask_monitor_b(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  if (DAT_0002bb74 == 'Z') {
    reset_windowed_monitor((F33WindowedMonitorState *)((undefined *)camry_host_ptr(0xfebe758cu)));
  }
  else if ((DAT_febe71ec >> 8 & 1) == 0) {
    step_windowed_monitor
              ((F33WindowedMonitorState *)((undefined *)camry_host_ptr(0xfebe758cu)),(F33WindowedMonitorLimits *)((undefined *)camry_host_ptr(0x2b652u)),
               (F33TwoSidedMonitorCallbacks *)
               &PTR_classify_paired_source_status_masks_b_00028390);
  }
  else {
    classify_counter_limits_and_clear_selected_fields_6ae48((undefined4 *)camry_host_ptr(0xfebe758cu), (ushort *)camry_host_ptr(0x2b652u));
  }
  publish_paired_source_monitor_status(3,(*((uint *)camry_host_ptr((uint32_t)((0xffffbd8cu + (uint32_t)((int)puVar1)))))));
  return;
}

uint classify_paired_source_status_masks_b(void)

{
  if (((DAT_febe7bc2 == 'Z') || (DAT_febe7bc3 == 'Z')) &&
     ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe755cu + (uint32_t)(1) * 1u)))) == '\0')) {
    if (((DAT_0002b666 & DAT_febe6364) == 0) && ((DAT_0002b668 & DAT_febe6366) == 0)) {
      return 0x11;
    }
    return 0x22;
  }
  return 0x44;
}

void report_diagnostic_healthy_observed_112_3e55c(void)

{
  report_diagnostic_healthy_observed(0x112);
  return;
}

void report_diagnostic_event_failure_112_10_3e56c(void)

{
  report_diagnostic_event_failure(0x112,10);
  return;
}

void reset_delayed_triplet_a_and_75b4_counters_3e57e(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  DAT_febe75b4 = 0;
  DAT_febe75b6 = 0;
  reset_terminal_monitor(delayed_status_bit_triplet_a_states);
  reset_terminal_monitor(((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xffffbda4u + (uint32_t)((int)puVar1))))));
  reset_terminal_monitor(((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xffffbdacu + (uint32_t)((int)puVar1))))));
  return;
}

void reset_delayed_triplet_a_and_67a4_state_3e5a6(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  DAT_febe67a5 = 0;
  DAT_febe67a4 = 0;
  DAT_febe67a6 = 0;
  DAT_febe67a8 = 0;
  reset_terminal_monitor(delayed_status_bit_triplet_a_states);
  reset_terminal_monitor(((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xffffbda4u + (uint32_t)((int)puVar1))))));
  reset_terminal_monitor(((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xffffbdacu + (uint32_t)((int)puVar1))))));
  return;
}

uint admit_delayed_status_bit_triplet_a(void)

{
  uint32_t puVar1;
  uint uVar2;
  ushort uVar3;
  
  uVar3 = DAT_febe67a8;
  puVar1 = 0xfebeb800u;
  uVar2 = (uint)DAT_febe67a4;
  if (uVar2 != 0x5a) {
    if (DAT_febe67a8 < DAT_0002b6d8) {
      uVar3 = DAT_febe67a8 + 1;
    }
    else {
      puVar1 = 0xfebeb800u;
      if ((DAT_febe6764 & 1) == 0) {
        puVar1 = 0xfebeb800u;
        set_output_request_word((uchar)(DAT_febe6764 & 1),DAT_febe6764 & 1);
        set_direct_output_codes_bank0((ushort *)((undefined *)camry_host_ptr(0x2b6dau)));
        request_direct_output_bank0();
      }
      uVar2 = 0x5a;
    }
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x505c))))) = (char)uVar2;
  (*((ushort *)camry_host_ptr((uint32_t)(puVar1 + -0x5058)))) = uVar3;
  return uVar2;
}

void step_delayed_status_bit_triplet_a(void)

{
  uint uVar1;
  ushort uVar2;
  uint32_t puVar3;
  uint uVar4;
  char cVar5;
  byte bVar6;
  
  bVar6 = DAT_febe67a6;
  cVar5 = DAT_febe67a5;
  uVar2 = DAT_febe6764;
  uVar1 = DAT_febe64cc;
  puVar3 = 0xfebeb800u;
  uVar4 = admit_delayed_status_bit_triplet_a();
  if (uVar4 != 0x5a) {
    reset_terminal_monitor(((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xffffbd9cu + (uint32_t)((int)puVar3))))));
    reset_terminal_monitor(((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xffffbda4u + (uint32_t)((int)puVar3))))));
    reset_terminal_monitor(((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xffffbdacu + (uint32_t)((int)puVar3))))));
    goto LAB_0003e71e;
  }
  if (DAT_0002bb78 == 'Z') {
    force_unconfirmed_terminal_monitor_healthy
              (camry_host_addr(((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xffffbd9cu + (uint32_t)((int)puVar3)))))), 
               (0x2b66au), (0x283c4u))
    ;
    force_unconfirmed_terminal_monitor_healthy
              (camry_host_addr(((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xffffbda4u + (uint32_t)((int)puVar3)))))), 
               (0x2b66au), (0x283c4u))
    ;
    force_unconfirmed_terminal_monitor_healthy
              (camry_host_addr(((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xffffbdacu + (uint32_t)((int)puVar3)))))), 
               (0x2b66au), (0x283c4u))
    ;
    goto LAB_0003e71e;
  }
  if ((uVar2 & 1) != 0) goto LAB_0003e71e;
  if (((cVar5 == '\0') && ((uVar1 & 0x7000) == 0)) && ((uVar1 & 1) == 0)) {
    if (bVar6 < DAT_0002b6d6) {
      bVar6 = bVar6 + 1;
      goto LAB_0003e67c;
    }
    cVar5 = '\x11';
    bVar6 = 0;
  }
  else {
LAB_0003e67c:
    if (cVar5 != '\x11') goto LAB_0003e71e;
  }
  (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffbdb6u + (uint32_t)((int)puVar3)))))) = 0x57;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbdb4u + (uint32_t)((int)puVar3) * 1u)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x3578)))));
  step_terminal_monitor
            (((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xffffbd9cu + (uint32_t)((int)puVar3))))), ((F33MonitorLimits *)camry_host_ptr((uint32_t)((0x2b66au)))), ((F33TerminalMonitorCallbacks *)camry_host_ptr((uint32_t)((0x283c4u)))));
  (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffbdb6u + (uint32_t)((int)puVar3)))))) = 0x58;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbdb4u + (uint32_t)((int)puVar3) * 1u)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x3577)))));
  step_terminal_monitor
            (((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xffffbda4u + (uint32_t)((int)puVar3))))), ((F33MonitorLimits *)camry_host_ptr((uint32_t)((0x2b66au)))), ((F33TerminalMonitorCallbacks *)camry_host_ptr((uint32_t)((0x283c4u)))));
  (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffbdb6u + (uint32_t)((int)puVar3)))))) = 0x59;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbdb4u + (uint32_t)((int)puVar3) * 1u)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x3576)))));
  step_terminal_monitor
            (((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xffffbdacu + (uint32_t)((int)puVar3))))), ((F33MonitorLimits *)camry_host_ptr((uint32_t)((0x2b66au)))), ((F33TerminalMonitorCallbacks *)camry_host_ptr((uint32_t)((0x283c4u)))));
LAB_0003e71e:
  if ((((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbd9cu + (uint32_t)((int)puVar3) * 1u)))) == '\0') && ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbda4u + (uint32_t)((int)puVar3) * 1u)))) == '\0')) &&
     ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbdacu + (uint32_t)((int)puVar3) * 1u)))) == '\0')) {
    mark_redundant_byte_6884_for_codes_21_to_34_32036(0x1a);
  }
  if ((((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbd9cu + (uint32_t)((int)puVar3) * 1u)))) == '\"') || ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbda4u + (uint32_t)((int)puVar3) * 1u)))) == '\"')) ||
     ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbdacu + (uint32_t)((int)puVar3) * 1u)))) == '\"')) {
    retain_and_clear_fault_record(10);
    encode_fault_action_kind('\n','\x1d');
    select_current_fault_record(10);
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x505b))))) = cVar5;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x505a))))) = bVar6;
  return;
}

uint classify_delayed_status_bit_triplet_a(void)

{
  if ((((DAT_febe64d8 == '\0') && (DAT_febe64d0 == '\0')) && ((DAT_febe6620 >> 2 & 1) != 0)) &&
     ((((DAT_febe661c >> 2 & 1) != 0 && ((DAT_febe6628 >> 1 & 1) == 0)) &&
      (((DAT_febe6614 & 1) != 0 && (DAT_febe65f0 == 'Z')))))) {
    if (DAT_febe75b4 != 'Z') {
      return 0x11;
    }
    return 0x22;
  }
  return 0x44;
}

void record_delayed_status_bit_triplet_a_healthy_observed(void)

{
  report_diagnostic_healthy_observed((uint)DAT_febe75b6);
  return;
}

void record_delayed_status_bit_triplet_a_failure(void)

{
  report_diagnostic_event_failure((uint)DAT_febe75b6,0x32);
  return;
}

undefined2 return_17_if_delayed_triplet_a_has_failing_count_3e7f8(void)

{
  undefined2 uVar1;
  
  if ((((*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe759cu + (uint32_t)(0) * (uint32_t)sizeof(F33TerminalMonitorState) + (uint32_t)offsetof(F33TerminalMonitorState, failing_count))))) != 0) ||
      ((*((volatile uint16_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe759cu + (uint32_t)(1) * (uint32_t)sizeof(F33TerminalMonitorState)) + (uint32_t)(0) * (uint32_t)sizeof(F33TerminalMonitorState) + (uint32_t)offsetof(F33TerminalMonitorState, failing_count))))) != 0)) ||
     (uVar1 = 0, (*((volatile uint16_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe759cu + (uint32_t)(2) * (uint32_t)sizeof(F33TerminalMonitorState)) + (uint32_t)(0) * (uint32_t)sizeof(F33TerminalMonitorState) + (uint32_t)offsetof(F33TerminalMonitorState, failing_count))))) != 0)) {
    uVar1 = 0x11;
  }
  return uVar1;
}

void reset_delayed_triplet_b_and_75d0_counters_3e816(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  DAT_febe75d0 = 0;
  DAT_febe75d2 = 0;
  reset_terminal_monitor(delayed_status_bit_triplet_b_states);
  reset_terminal_monitor(((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xffffbdc0u + (uint32_t)((int)puVar1))))));
  reset_terminal_monitor(((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xffffbdc8u + (uint32_t)((int)puVar1))))));
  return;
}

void reset_delayed_triplet_b_and_67ac_state_3e83e(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  DAT_febe67ad = 0;
  DAT_febe67ac = 0;
  DAT_febe67ae = 0;
  DAT_febe67b0 = 0;
  reset_terminal_monitor(delayed_status_bit_triplet_b_states);
  reset_terminal_monitor(((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xffffbdc0u + (uint32_t)((int)puVar1))))));
  reset_terminal_monitor(((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xffffbdc8u + (uint32_t)((int)puVar1))))));
  return;
}

uint admit_delayed_status_bit_triplet_b(void)

{
  uint32_t puVar1;
  uint uVar2;
  ushort uVar3;
  
  uVar3 = DAT_febe67b0;
  puVar1 = 0xfebeb800u;
  uVar2 = (uint)DAT_febe67ac;
  if (uVar2 != 0x5a) {
    if (DAT_febe67b0 < DAT_0002b6e4) {
      uVar3 = DAT_febe67b0 + 1;
    }
    else {
      puVar1 = 0xfebeb800u;
      if ((DAT_febe6764 & 2) == 0) {
        puVar1 = 0xfebeb800u;
        set_output_request_word('\x01',DAT_febe6764 & 2);
        set_direct_output_codes_bank1((ushort *)((undefined *)camry_host_ptr(0x2b6e6u)));
        request_direct_output_bank1();
      }
      uVar2 = 0x5a;
    }
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x5054))))) = (char)uVar2;
  (*((ushort *)camry_host_ptr((uint32_t)(puVar1 + -0x5050)))) = uVar3;
  return uVar2;
}

void step_delayed_status_bit_triplet_b(void)

{
  uint uVar1;
  ushort uVar2;
  uint32_t puVar3;
  uint uVar4;
  char cVar5;
  byte bVar6;
  
  bVar6 = DAT_febe67ae;
  cVar5 = DAT_febe67ad;
  uVar2 = DAT_febe6764;
  uVar1 = DAT_febe64cc;
  puVar3 = 0xfebeb800u;
  uVar4 = admit_delayed_status_bit_triplet_b();
  if (uVar4 != 0x5a) {
    reset_terminal_monitor(((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xffffbdb8u + (uint32_t)((int)puVar3))))));
    reset_terminal_monitor(((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xffffbdc0u + (uint32_t)((int)puVar3))))));
    reset_terminal_monitor(((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xffffbdc8u + (uint32_t)((int)puVar3))))));
    goto LAB_0003e9bc;
  }
  if (DAT_0002bb7c == 'Z') {
    force_unconfirmed_terminal_monitor_healthy
              (camry_host_addr(((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xffffbdb8u + (uint32_t)((int)puVar3)))))), 
               (0x2b66eu), (0x283d0u))
    ;
    force_unconfirmed_terminal_monitor_healthy
              (camry_host_addr(((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xffffbdc0u + (uint32_t)((int)puVar3)))))), 
               (0x2b66eu), (0x283d0u))
    ;
    force_unconfirmed_terminal_monitor_healthy
              (camry_host_addr(((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xffffbdc8u + (uint32_t)((int)puVar3)))))), 
               (0x2b66eu), (0x283d0u))
    ;
    goto LAB_0003e9bc;
  }
  if ((uVar2 >> 1 & 1) != 0) goto LAB_0003e9bc;
  if (((cVar5 == '\0') && ((uVar1 & 0x70000000) == 0)) && ((uVar1 & 0x10000) == 0)) {
    if (bVar6 < DAT_0002b6e2) {
      bVar6 = bVar6 + 1;
      goto LAB_0003e91a;
    }
    cVar5 = '\x11';
    bVar6 = 0;
  }
  else {
LAB_0003e91a:
    if (cVar5 != '\x11') goto LAB_0003e9bc;
  }
  (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffbdd2u + (uint32_t)((int)puVar3)))))) = 0x5d;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbdd0u + (uint32_t)((int)puVar3) * 1u)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x3572)))));
  step_terminal_monitor
            (((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xffffbdb8u + (uint32_t)((int)puVar3))))), ((F33MonitorLimits *)camry_host_ptr((uint32_t)((0x2b66eu)))), ((F33TerminalMonitorCallbacks *)camry_host_ptr((uint32_t)((0x283d0u)))));
  (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffbdd2u + (uint32_t)((int)puVar3)))))) = 0x5e;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbdd0u + (uint32_t)((int)puVar3) * 1u)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x3571)))));
  step_terminal_monitor
            (((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xffffbdc0u + (uint32_t)((int)puVar3))))), ((F33MonitorLimits *)camry_host_ptr((uint32_t)((0x2b66eu)))), ((F33TerminalMonitorCallbacks *)camry_host_ptr((uint32_t)((0x283d0u)))));
  (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffbdd2u + (uint32_t)((int)puVar3)))))) = 0x5f;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbdd0u + (uint32_t)((int)puVar3) * 1u)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x3570)))));
  step_terminal_monitor
            (((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xffffbdc8u + (uint32_t)((int)puVar3))))), ((F33MonitorLimits *)camry_host_ptr((uint32_t)((0x2b66eu)))), ((F33TerminalMonitorCallbacks *)camry_host_ptr((uint32_t)((0x283d0u)))));
LAB_0003e9bc:
  if ((((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbdb8u + (uint32_t)((int)puVar3) * 1u)))) == '\0') && ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbdc0u + (uint32_t)((int)puVar3) * 1u)))) == '\0')) &&
     ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbdc8u + (uint32_t)((int)puVar3) * 1u)))) == '\0')) {
    mark_redundant_byte_6885_for_codes_21_to_34_32050(0x1a);
  }
  if ((((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbdb8u + (uint32_t)((int)puVar3) * 1u)))) == '\"') || ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbdc0u + (uint32_t)((int)puVar3) * 1u)))) == '\"')) ||
     ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbdc8u + (uint32_t)((int)puVar3) * 1u)))) == '\"')) {
    retain_and_clear_fault_record(0xb);
    encode_fault_action_kind('\v','\x1e');
    select_current_fault_record(0xb);
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x5053))))) = cVar5;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x5052))))) = bVar6;
  return;
}

uint classify_delayed_status_bit_triplet_b(void)

{
  if ((((DAT_febe64d9 == '\0') && (DAT_febe64d1 == '\0')) && ((DAT_febe6620 >> 0x12 & 1) != 0)) &&
     ((((DAT_febe661c >> 0x12 & 1) != 0 && ((DAT_febe6628 >> 0x11 & 1) == 0)) &&
      (((DAT_febe6614 & 1) != 0 && (DAT_febe65f0 == 'Z')))))) {
    if (DAT_febe75d0 != 'Z') {
      return 0x11;
    }
    return 0x22;
  }
  return 0x44;
}

void record_delayed_status_bit_triplet_b_healthy_observed(void)

{
  report_diagnostic_healthy_observed((uint)DAT_febe75d2);
  return;
}

void record_delayed_status_bit_triplet_b_failure(void)

{
  report_diagnostic_event_failure((uint)DAT_febe75d2,0x32);
  return;
}

undefined2 return_17_if_delayed_triplet_b_has_failing_count_3ea96(void)

{
  undefined2 uVar1;
  
  if ((((*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe75b8u + (uint32_t)(0) * (uint32_t)sizeof(F33TerminalMonitorState) + (uint32_t)offsetof(F33TerminalMonitorState, failing_count))))) != 0) ||
      ((*((volatile uint16_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe75b8u + (uint32_t)(1) * (uint32_t)sizeof(F33TerminalMonitorState)) + (uint32_t)(0) * (uint32_t)sizeof(F33TerminalMonitorState) + (uint32_t)offsetof(F33TerminalMonitorState, failing_count))))) != 0)) ||
     (uVar1 = 0, (*((volatile uint16_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe75b8u + (uint32_t)(2) * (uint32_t)sizeof(F33TerminalMonitorState)) + (uint32_t)(0) * (uint32_t)sizeof(F33TerminalMonitorState) + (uint32_t)offsetof(F33TerminalMonitorState, failing_count))))) != 0)) {
    uVar1 = 0x11;
  }
  return uVar1;
}

void reset_matched_state2_triplet_a_and_75ec_counters_3eab4(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  DAT_febe75ec = 0;
  DAT_febe75ee = 0;
  reset_terminal_monitor(matched_state2_status_bit_triplet_a_states);
  reset_terminal_monitor(((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xffffbddcu + (uint32_t)((int)puVar1))))));
  reset_terminal_monitor(((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xffffbde4u + (uint32_t)((int)puVar1))))));
  return;
}

void reset_matched_state2_triplet_a_and_67b4_flags_3eadc(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  DAT_febe67b4 = 0;
  DAT_febe67b5 = 0;
  reset_terminal_monitor(matched_state2_status_bit_triplet_a_states);
  reset_terminal_monitor(((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xffffbddcu + (uint32_t)((int)puVar1))))));
  reset_terminal_monitor(((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xffffbde4u + (uint32_t)((int)puVar1))))));
  return;
}

void step_matched_state2_status_bit_triplet_a(void)

{
  uint32_t puVar1;
  char cVar2;
  byte bVar3;
  
  bVar3 = DAT_febe67b5;
  cVar2 = DAT_febe67b4;
  puVar1 = 0xfebeb800u;
  if (DAT_0002bb80 == 'Z') {
    puVar1 = 0xfebeb800u;
    force_unconfirmed_terminal_monitor_healthy
              (camry_host_addr(matched_state2_status_bit_triplet_a_states), 
               (0x2b672u), 
               (0x283dcu));
    force_unconfirmed_terminal_monitor_healthy
              (camry_host_addr(((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xffffbddcu + (uint32_t)((int)puVar1)))))), 
               (0x2b672u), 
               (0x283dcu));
    force_unconfirmed_terminal_monitor_healthy
              (camry_host_addr(((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xffffbde4u + (uint32_t)((int)puVar1)))))), 
               (0x2b672u), 
               (0x283dcu));
    goto LAB_0003ebd6;
  }
  if ((DAT_febe6764 & 1) != 0) goto LAB_0003ebd6;
  if ((DAT_febe67b4 == '\0') && ((DAT_febe64cc & 0x7000) == 0)) {
    if (DAT_febe67b5 < DAT_0002b6ee) {
      bVar3 = DAT_febe67b5 + 1;
      goto LAB_0003eb4e;
    }
    bVar3 = 0;
    cVar2 = '\x11';
  }
  else {
LAB_0003eb4e:
    if (DAT_febe67b4 != '\x11') goto LAB_0003ebd6;
  }
  DAT_febe75ee = 0xce;
  DAT_febe75ec = DAT_febe8288;
  puVar1 = 0xfebeb800u;
  step_terminal_monitor
            (matched_state2_status_bit_triplet_a_states, ((F33MonitorLimits *)camry_host_ptr((uint32_t)((0x2b672u)))), ((F33TerminalMonitorCallbacks *)camry_host_ptr((uint32_t)((0x283dcu)))));
  (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffbdeeu + (uint32_t)((int)puVar1)))))) = 0xcf;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbdecu + (uint32_t)((int)puVar1) * 1u)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x3577)))));
  step_terminal_monitor
            (((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xffffbddcu + (uint32_t)((int)puVar1))))), ((F33MonitorLimits *)camry_host_ptr((uint32_t)((0x2b672u)))), ((F33TerminalMonitorCallbacks *)camry_host_ptr((uint32_t)((0x283dcu)))));
  (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffbdeeu + (uint32_t)((int)puVar1)))))) = 0xd0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbdecu + (uint32_t)((int)puVar1) * 1u)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x3576)))));
  step_terminal_monitor
            (((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xffffbde4u + (uint32_t)((int)puVar1))))), ((F33MonitorLimits *)camry_host_ptr((uint32_t)((0x2b672u)))), ((F33TerminalMonitorCallbacks *)camry_host_ptr((uint32_t)((0x283dcu)))));
LAB_0003ebd6:
  if ((((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbdd4u + (uint32_t)((int)puVar1) * 1u)))) == '\0') && ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbddcu + (uint32_t)((int)puVar1) * 1u)))) == '\0')) &&
     ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbde4u + (uint32_t)((int)puVar1) * 1u)))) == '\0')) {
    mark_redundant_byte_6884_for_codes_21_to_34_32036(0x22);
  }
  if ((((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbdd4u + (uint32_t)((int)puVar1) * 1u)))) == '\"') || ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbddcu + (uint32_t)((int)puVar1) * 1u)))) == '\"')) ||
     ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbde4u + (uint32_t)((int)puVar1) * 1u)))) == '\"')) {
    retain_and_clear_fault_record(10);
    encode_fault_action_kind('\n','\x1b');
    encode_fault_action_kind('\n','2');
    select_current_fault_record(10);
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x504c))))) = cVar2;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x504b))))) = bVar3;
  return;
}

uint classify_matched_state2_status_bit_triplet_a(void)

{
  if ((((((DAT_febe64d8 == '\x02') && (DAT_febe64d0 == '\x02')) && ((DAT_febe6620 >> 1 & 1) == 0))
       && (((DAT_febe6620 >> 2 & 1) != 0 && ((DAT_febe661c >> 1 & 1) == 0)))) &&
      (((DAT_febe661c >> 2 & 1) != 0 &&
       (((DAT_febe6628 >> 1 & 1) == 0 && ((DAT_febe6614 & 1) == 0)))))) && (DAT_febe65f6 == 'Z')) {
    if (DAT_febe75ec != 'Z') {
      return 0x11;
    }
    return 0x22;
  }
  return 0x44;
}

void record_matched_state2_status_bit_triplet_a_healthy_observed(void)

{
  report_diagnostic_healthy_observed((uint)DAT_febe75ee);
  return;
}

void record_matched_state2_status_bit_triplet_a_failure(void)

{
  report_diagnostic_event_failure((uint)DAT_febe75ee,0x32);
  return;
}

undefined2 return_17_if_matched_state2_triplet_a_has_failing_count_3ecc6(void)

{
  undefined2 uVar1;
  
  if ((((*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe75d4u + (uint32_t)(0) * (uint32_t)sizeof(F33TerminalMonitorState) + (uint32_t)offsetof(F33TerminalMonitorState, failing_count))))) != 0) ||
      ((*((volatile uint16_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe75d4u + (uint32_t)(1) * (uint32_t)sizeof(F33TerminalMonitorState)) + (uint32_t)(0) * (uint32_t)sizeof(F33TerminalMonitorState) + (uint32_t)offsetof(F33TerminalMonitorState, failing_count))))) != 0)) ||
     (uVar1 = 0, (*((volatile uint16_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe75d4u + (uint32_t)(2) * (uint32_t)sizeof(F33TerminalMonitorState)) + (uint32_t)(0) * (uint32_t)sizeof(F33TerminalMonitorState) + (uint32_t)offsetof(F33TerminalMonitorState, failing_count))))) != 0)) {
    uVar1 = 0x11;
  }
  return uVar1;
}

void reset_triplet_b_monitors_and_summary_3ece4(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  DAT_febe7608 = 0;
  DAT_febe760a = 0;
  reset_terminal_monitor(matched_state2_status_bit_triplet_b_states);
  reset_terminal_monitor(((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xffffbdf8u + (uint32_t)((int)puVar1))))));
  reset_terminal_monitor(((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xffffbe00u + (uint32_t)((int)puVar1))))));
  return;
}

void reset_triplet_b_monitors_and_control_bytes_3ed0c(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  DAT_febe67b8 = 0;
  DAT_febe67b9 = 0;
  reset_terminal_monitor(matched_state2_status_bit_triplet_b_states);
  reset_terminal_monitor(((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xffffbdf8u + (uint32_t)((int)puVar1))))));
  reset_terminal_monitor(((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xffffbe00u + (uint32_t)((int)puVar1))))));
  return;
}

void step_matched_state2_status_bit_triplet_b(void)

{
  uint32_t puVar1;
  char cVar2;
  byte bVar3;
  
  bVar3 = DAT_febe67b9;
  cVar2 = DAT_febe67b8;
  puVar1 = 0xfebeb800u;
  if (DAT_0002bb84 == 'Z') {
    puVar1 = 0xfebeb800u;
    force_unconfirmed_terminal_monitor_healthy
              (camry_host_addr(matched_state2_status_bit_triplet_b_states), 
               (0x2b676u), 
               (0x283e8u));
    force_unconfirmed_terminal_monitor_healthy
              (camry_host_addr(((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xffffbdf8u + (uint32_t)((int)puVar1)))))), 
               (0x2b676u), 
               (0x283e8u));
    force_unconfirmed_terminal_monitor_healthy
              (camry_host_addr(((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xffffbe00u + (uint32_t)((int)puVar1)))))), 
               (0x2b676u), 
               (0x283e8u));
    goto LAB_0003ee06;
  }
  if ((DAT_febe6764 >> 1 & 1) != 0) goto LAB_0003ee06;
  if ((DAT_febe67b8 == '\0') && (((int)DAT_febe64cc & 0x7fffffff) >> 0x1c == 0)) {
    if (DAT_febe67b9 < DAT_0002b6f2) {
      bVar3 = DAT_febe67b9 + 1;
      goto LAB_0003ed7e;
    }
    bVar3 = 0;
    cVar2 = '\x11';
  }
  else {
LAB_0003ed7e:
    if (DAT_febe67b8 != '\x11') goto LAB_0003ee06;
  }
  DAT_febe760a = 0xdb;
  DAT_febe7608 = DAT_febe828e;
  puVar1 = 0xfebeb800u;
  step_terminal_monitor
            (matched_state2_status_bit_triplet_b_states, ((F33MonitorLimits *)camry_host_ptr((uint32_t)((0x2b676u)))), ((F33TerminalMonitorCallbacks *)camry_host_ptr((uint32_t)((0x283e8u)))));
  (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffbe0au + (uint32_t)((int)puVar1)))))) = 0xdc;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbe08u + (uint32_t)((int)puVar1) * 1u)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x3571)))));
  step_terminal_monitor
            (((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xffffbdf8u + (uint32_t)((int)puVar1))))), ((F33MonitorLimits *)camry_host_ptr((uint32_t)((0x2b676u)))), ((F33TerminalMonitorCallbacks *)camry_host_ptr((uint32_t)((0x283e8u)))));
  (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffbe0au + (uint32_t)((int)puVar1)))))) = 0xdd;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbe08u + (uint32_t)((int)puVar1) * 1u)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x3570)))));
  step_terminal_monitor
            (((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xffffbe00u + (uint32_t)((int)puVar1))))), ((F33MonitorLimits *)camry_host_ptr((uint32_t)((0x2b676u)))), ((F33TerminalMonitorCallbacks *)camry_host_ptr((uint32_t)((0x283e8u)))));
LAB_0003ee06:
  if ((((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbdf0u + (uint32_t)((int)puVar1) * 1u)))) == '\0') && ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbdf8u + (uint32_t)((int)puVar1) * 1u)))) == '\0')) &&
     ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbe00u + (uint32_t)((int)puVar1) * 1u)))) == '\0')) {
    mark_redundant_byte_6885_for_codes_21_to_34_32050(0x22);
  }
  if ((((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbdf0u + (uint32_t)((int)puVar1) * 1u)))) == '\"') || ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbdf8u + (uint32_t)((int)puVar1) * 1u)))) == '\"')) ||
     ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbe00u + (uint32_t)((int)puVar1) * 1u)))) == '\"')) {
    retain_and_clear_fault_record(0xb);
    encode_fault_action_kind('\v','\x1c');
    encode_fault_action_kind('\v','2');
    select_current_fault_record(0xb);
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x5048))))) = cVar2;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x5047))))) = bVar3;
  return;
}

uint classify_matched_state2_status_bit_triplet_b(void)

{
  if ((((((DAT_febe64d9 == '\x02') && (DAT_febe64d1 == '\x02')) && ((DAT_febe6620 >> 0x11 & 1) == 0)
        ) && (((DAT_febe6620 >> 0x12 & 1) != 0 && ((DAT_febe661c >> 0x11 & 1) == 0)))) &&
      (((DAT_febe661c & 0x40000) != 0 &&
       (((DAT_febe6628 >> 0x11 & 1) == 0 && ((DAT_febe6614 & 1) == 0)))))) && (DAT_febe65f7 == 'Z'))
  {
    if (DAT_febe7608 != 'Z') {
      return 0x11;
    }
    return 0x22;
  }
  return 0x44;
}

void record_matched_state2_status_bit_triplet_b_healthy_observed(void)

{
  report_diagnostic_healthy_observed((uint)DAT_febe760a);
  return;
}

void record_matched_state2_status_bit_triplet_b_failure(void)

{
  report_diagnostic_event_failure((uint)DAT_febe760a,0x32);
  return;
}

undefined2 summarize_triplet_b_failure_counts_3eefa(void)

{
  undefined2 uVar1;
  
  if ((((*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe75f0u + (uint32_t)(0) * (uint32_t)sizeof(F33TerminalMonitorState) + (uint32_t)offsetof(F33TerminalMonitorState, failing_count))))) != 0) ||
      ((*((volatile uint16_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe75f0u + (uint32_t)(1) * (uint32_t)sizeof(F33TerminalMonitorState)) + (uint32_t)(0) * (uint32_t)sizeof(F33TerminalMonitorState) + (uint32_t)offsetof(F33TerminalMonitorState, failing_count))))) != 0)) ||
     (uVar1 = 0, (*((volatile uint16_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe75f0u + (uint32_t)(2) * (uint32_t)sizeof(F33TerminalMonitorState)) + (uint32_t)(0) * (uint32_t)sizeof(F33TerminalMonitorState) + (uint32_t)offsetof(F33TerminalMonitorState, failing_count))))) != 0)) {
    uVar1 = 0x11;
  }
  return uVar1;
}

void return_only_stub_3ef18(void)

{
  return;
}

void return_only_stub_3ef1a(void)

{
  return;
}

int publish_configured_monitor_failure_count_summary(void)

{
  uchar status;
  int iVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  int iVar6;
  int iVar7;
  int iVar8;
  int iVar9;
  int iVar10;
  int iVar11;
  int iVar12;
  int iVar13;
  int iVar14;
  int iVar15;
  int iVar16;
  int iVar17;
  int iVar18;
  int iVar19;
  int iVar20;
  int iVar21;
  int iVar22;
  int iVar23;
  int iVar24;
  int iVar25;
  int iVar26;
  int iVar27;
  
  iVar1 = status_failing_sample_difference_window_a_states();
  iVar2 = status_failing_sample_difference_window_b_states();
  iVar3 = status_failing_baseline_sample_threshold_a_states();
  iVar4 = status_failing_baseline_sample_threshold_b_states();
  iVar5 = status_failing_requested_state_sample_threshold_a_states();
  iVar6 = status_failing_requested_state_sample_threshold_b_states();
  iVar7 = summarize_startup_triplet_a_failures_41788();
  iVar8 = summarize_startup_triplet_b_failures_419c0();
  iVar9 = return_17_if_delayed_triplet_a_has_failing_count_3e7f8();
  iVar10 = return_17_if_delayed_triplet_b_has_failing_count_3ea96();
  iVar11 = status_failing_observed_state_sample_regions_a_states();
  iVar12 = status_failing_observed_state_sample_regions_b_states();
  iVar13 = status_failing_coupled_sample_threshold_both_states();
  iVar14 = status_failing_asserted_state_sample_threshold_a_states();
  iVar15 = status_failing_asserted_state_sample_threshold_b_states();
  iVar16 = status_failing_matched_state2_status_bit_a_states();
  iVar17 = status_failing_matched_state2_status_bit_b_states();
  iVar18 = summarize_sample_range_triplet_a_failures_412e2();
  iVar19 = summarize_sample_range_triplet_b_failures_41550();
  iVar20 = summarize_matched_startup_triplet_a_failures_41bf0();
  iVar21 = summarize_matched_startup_triplet_b_failures_41e24();
  iVar22 = return_17_if_matched_state2_triplet_a_has_failing_count_3ecc6();
  iVar23 = summarize_triplet_b_failure_counts_3eefa();
  iVar24 = status_failing_bounded_sample_or_status_a_states();
  iVar25 = status_failing_bounded_sample_or_status_b_states();
  iVar26 = status_failing_command_status_bit_clear_a_states();
  iVar27 = status_failing_command_status_bit_clear_b_states();
  status = '\0';
  if ((((((((((((((((((((((((((iVar1 != 0 || iVar2 != 0) || iVar3 != 0) || iVar4 != 0) || iVar5 != 0
                           ) || iVar6 != 0) || iVar7 != 0) || iVar8 != 0) || iVar9 != 0) ||
                      iVar10 != 0) || iVar11 != 0) || iVar12 != 0) || iVar13 != 0) || iVar14 != 0)
                 || iVar15 != 0) || iVar16 != 0) || iVar17 != 0) || iVar18 != 0) || iVar19 != 0) ||
            iVar20 != 0) || iVar21 != 0) || iVar22 != 0) || iVar23 != 0) || iVar24 != 0) ||
       iVar25 != 0) || iVar26 != 0) || iVar27 != 0) {
    status = '\x11';
  }
  set_diagnostic_cache_blocker('\t',status);
  return iVar27;
}

void publish_monitor_failure_count_summary_wrapper_3efd4(void)

{
  publish_configured_monitor_failure_count_summary();
  return;
}

void reset_coupled_sample_threshold_both(void)

{
  reset_terminal_monitor(((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xfebe760cu)))));
  return;
}

void reset_coupled_threshold_monitor_and_sequence_3eff0(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  reset_terminal_monitor(((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xfebe760cu)))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x5044))))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x5043))))) = 0;
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x5042)))) = 0;
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x5040)))) = 0;
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x503e)))) = 0;
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x503c)))) = 0;
  return;
}
