#include "common.h"

void record_observed_state_sample_regions_b_healthy_observed(void)

{
  report_diagnostic_healthy_observed(0xba);
  return;
}

void record_observed_state_sample_regions_b_failure(void)

{
  report_diagnostic_event_failure(0xba,0x32);
  return;
}

undefined4 status_failing_observed_state_sample_regions_b_states(void)

{
  if (observed_state_sample_regions_b_states.failing_count != 0) {
    return 0x11;
  }
  return 0;
}

void reset_sample_range_triplet_a_and_counters_41096(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  DAT_febe76ac = 0;
  DAT_febe76ae = 0;
  DAT_febe76b0 = 0;
  reset_terminal_monitor(sample_range_triplet_a_states);
  reset_terminal_monitor(((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xffffbe9cu + (uint32_t)((int)puVar1))))));
  reset_terminal_monitor(((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xffffbea4u + (uint32_t)((int)puVar1))))));
  return;
}

void reset_sample_range_triplet_a_and_control_410c0(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  DAT_febe684a = 0;
  reset_terminal_monitor(sample_range_triplet_a_states);
  reset_terminal_monitor(((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xffffbe9cu + (uint32_t)((int)puVar1))))));
  reset_terminal_monitor(((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xffffbea4u + (uint32_t)((int)puVar1))))));
  return;
}

uint admit_sample_range_triplet_a(void)

{
  uint uVar1;
  
  uVar1 = (uint)DAT_febe6848;
  if (uVar1 != 0x5a) {
    if (DAT_febe684c < DAT_0002b7c6) {
      DAT_febe684c = DAT_febe684c + 1;
    }
    else {
      uVar1 = 0x5a;
    }
  }
  DAT_febe6848 = (char)uVar1;
  return uVar1;
}

void step_sample_range_triplet_a(void)

{
  ushort uVar1;
  uint32_t puVar2;
  uint uVar3;
  
  uVar1 = DAT_febe6764;
  puVar2 = 0xfebeb800u;
  uVar3 = admit_sample_range_triplet_a();
  if (uVar3 == 0x5a) {
    if (DAT_0002bbcc == 'Z') {
      force_unconfirmed_terminal_monitor_healthy
                (camry_host_addr(((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xffffbe94u + (uint32_t)((int)puVar2)))))), 
                 (0x2b6beu), (0x284c0u));
      force_unconfirmed_terminal_monitor_healthy
                (camry_host_addr(((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xffffbe9cu + (uint32_t)((int)puVar2)))))), 
                 (0x2b6beu), (0x284c0u));
      force_unconfirmed_terminal_monitor_healthy
                (camry_host_addr(((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xffffbea4u + (uint32_t)((int)puVar2)))))), 
                 (0x2b6beu), (0x284c0u));
    }
    else if ((uVar1 & 1) == 0) {
      (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffbeacu + (uint32_t)((int)puVar2)))))) = 0x66;
      (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffbeaeu + (uint32_t)((int)puVar2)))))) = 0x69;
      (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffbeb0u + (uint32_t)((int)puVar2)))))) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar2 + -0x53b0))));
      step_terminal_monitor
                (((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xffffbe94u + (uint32_t)((int)puVar2))))), ((F33MonitorLimits *)camry_host_ptr((uint32_t)((0x2b6beu)))), ((F33TerminalMonitorCallbacks *)camry_host_ptr((uint32_t)((0x284c0u)))));
      (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffbeacu + (uint32_t)((int)puVar2)))))) = 0x67;
      (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffbeaeu + (uint32_t)((int)puVar2)))))) = 0x6a;
      (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffbeb0u + (uint32_t)((int)puVar2)))))) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar2 + -0x53ae))));
      step_terminal_monitor
                (((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xffffbe9cu + (uint32_t)((int)puVar2))))), ((F33MonitorLimits *)camry_host_ptr((uint32_t)((0x2b6beu)))), ((F33TerminalMonitorCallbacks *)camry_host_ptr((uint32_t)((0x284c0u)))));
      (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffbeacu + (uint32_t)((int)puVar2)))))) = 0x68;
      (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffbeaeu + (uint32_t)((int)puVar2)))))) = 0x6b;
      (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffbeb0u + (uint32_t)((int)puVar2)))))) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar2 + -0x53ac))));
      step_terminal_monitor
                (((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xffffbea4u + (uint32_t)((int)puVar2))))), ((F33MonitorLimits *)camry_host_ptr((uint32_t)((0x2b6beu)))), ((F33TerminalMonitorCallbacks *)camry_host_ptr((uint32_t)((0x284c0u)))));
    }
  }
  else {
    reset_terminal_monitor(((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xffffbe94u + (uint32_t)((int)puVar2))))));
    reset_terminal_monitor(((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xffffbe9cu + (uint32_t)((int)puVar2))))));
    reset_terminal_monitor(((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xffffbea4u + (uint32_t)((int)puVar2))))));
  }
  if ((((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbe94u + (uint32_t)((int)puVar2) * 1u)))) == '\0') && ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbe9cu + (uint32_t)((int)puVar2) * 1u)))) == '\0')) &&
     ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbea4u + (uint32_t)((int)puVar2) * 1u)))) == '\0')) {
    mark_redundant_byte_6884_for_codes_21_to_34_32036(0x20);
  }
  if ((((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbe94u + (uint32_t)((int)puVar2) * 1u)))) == '\"') || ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbe9cu + (uint32_t)((int)puVar2) * 1u)))) == '\"')) ||
     ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbea4u + (uint32_t)((int)puVar2) * 1u)))) == '\"')) {
    retain_and_clear_fault_record(10);
    encode_fault_action_kind('\n','\x1b');
    select_current_fault_record(10);
  }
  return;
}

uint classify_sample_range_triplet_a(void)

{
  undefined2 uVar1;
  
  if ((((((DAT_febe64d8 == '\x02') && (DAT_febe64d0 == '\x02')) && ((DAT_febe6620 >> 1 & 1) == 0))
       && (((DAT_febe6620 >> 2 & 1) != 0 && ((DAT_febe661c >> 1 & 1) == 0)))) &&
      (((DAT_febe661c >> 2 & 1) != 0 &&
       (((DAT_febe6628 >> 1 & 1) == 0 && ((DAT_febe6614 & 1) == 0)))))) && (DAT_febe65f2 == 'Z')) {
    uVar1 = DAT_febe76ac;
    if ((DAT_febe76b0 <= DAT_0002b7c2) && (uVar1 = DAT_febe76ae, DAT_0002b7c4 <= DAT_febe76b0)) {
      return 0x11;
    }
    DAT_febe684a = uVar1;
    return 0x22;
  }
  return 0x44;
}

void record_sample_range_triplet_a_healthy_observed(void)

{
  uint event;
  
  event = (uint)DAT_febe76ae;
  report_diagnostic_healthy_observed((uint)DAT_febe76ac);
  report_diagnostic_healthy_observed(event);
  return;
}

void record_sample_range_triplet_a_failure(void)

{
  report_diagnostic_event_failure((uint)DAT_febe684a,0x32);
  return;
}

undefined2 summarize_sample_range_triplet_a_failures_412e2(void)

{
  undefined2 uVar1;
  
  if ((((*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe7694u + (uint32_t)(0) * (uint32_t)sizeof(F33TerminalMonitorState) + (uint32_t)offsetof(F33TerminalMonitorState, failing_count))))) != 0) ||
      ((*((volatile uint16_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe7694u + (uint32_t)(1) * (uint32_t)sizeof(F33TerminalMonitorState)) + (uint32_t)(0) * (uint32_t)sizeof(F33TerminalMonitorState) + (uint32_t)offsetof(F33TerminalMonitorState, failing_count))))) != 0)) ||
     (uVar1 = 0, (*((volatile uint16_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe7694u + (uint32_t)(2) * (uint32_t)sizeof(F33TerminalMonitorState)) + (uint32_t)(0) * (uint32_t)sizeof(F33TerminalMonitorState) + (uint32_t)offsetof(F33TerminalMonitorState, failing_count))))) != 0)) {
    uVar1 = 0x11;
  }
  return uVar1;
}

void reset_sample_range_triplet_b_and_counters_41300(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  DAT_febe76cc = 0;
  DAT_febe76ce = 0;
  DAT_febe76d0 = 0;
  reset_terminal_monitor(sample_range_triplet_b_states);
  reset_terminal_monitor(((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xffffbebcu + (uint32_t)((int)puVar1))))));
  reset_terminal_monitor(((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xffffbec4u + (uint32_t)((int)puVar1))))));
  return;
}

void reset_sample_range_triplet_b_and_control_4132a(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  DAT_febe6852 = 0;
  reset_terminal_monitor(sample_range_triplet_b_states);
  reset_terminal_monitor(((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xffffbebcu + (uint32_t)((int)puVar1))))));
  reset_terminal_monitor(((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xffffbec4u + (uint32_t)((int)puVar1))))));
  return;
}

uint admit_sample_range_triplet_b(void)

{
  uint uVar1;
  
  uVar1 = (uint)DAT_febe6850;
  if (uVar1 != 0x5a) {
    if (DAT_febe6854 < DAT_0002b7ce) {
      DAT_febe6854 = DAT_febe6854 + 1;
    }
    else {
      uVar1 = 0x5a;
    }
  }
  DAT_febe6850 = (char)uVar1;
  return uVar1;
}

void step_sample_range_triplet_b(void)

{
  ushort uVar1;
  uint32_t puVar2;
  uint uVar3;
  
  uVar1 = DAT_febe6764;
  puVar2 = 0xfebeb800u;
  uVar3 = admit_sample_range_triplet_b();
  if (uVar3 == 0x5a) {
    if (DAT_0002bbd0 == 'Z') {
      force_unconfirmed_terminal_monitor_healthy
                (camry_host_addr(((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xffffbeb4u + (uint32_t)((int)puVar2)))))), 
                 (0x2b6c2u), (0x284ccu));
      force_unconfirmed_terminal_monitor_healthy
                (camry_host_addr(((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xffffbebcu + (uint32_t)((int)puVar2)))))), 
                 (0x2b6c2u), (0x284ccu));
      force_unconfirmed_terminal_monitor_healthy
                (camry_host_addr(((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xffffbec4u + (uint32_t)((int)puVar2)))))), 
                 (0x2b6c2u), (0x284ccu));
    }
    else if ((uVar1 >> 1 & 1) == 0) {
      (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffbeccu + (uint32_t)((int)puVar2)))))) = 0xf5;
      (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffbeceu + (uint32_t)((int)puVar2)))))) = 0xf8;
      (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffbed0u + (uint32_t)((int)puVar2)))))) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar2 + -0x53aa))));
      step_terminal_monitor
                (((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xffffbeb4u + (uint32_t)((int)puVar2))))), ((F33MonitorLimits *)camry_host_ptr((uint32_t)((0x2b6c2u)))), ((F33TerminalMonitorCallbacks *)camry_host_ptr((uint32_t)((0x284ccu)))));
      (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffbeccu + (uint32_t)((int)puVar2)))))) = 0xf6;
      (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffbeceu + (uint32_t)((int)puVar2)))))) = 0xf9;
      (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffbed0u + (uint32_t)((int)puVar2)))))) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar2 + -0x53a8))));
      step_terminal_monitor
                (((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xffffbebcu + (uint32_t)((int)puVar2))))), ((F33MonitorLimits *)camry_host_ptr((uint32_t)((0x2b6c2u)))), ((F33TerminalMonitorCallbacks *)camry_host_ptr((uint32_t)((0x284ccu)))));
      (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffbeccu + (uint32_t)((int)puVar2)))))) = 0xf7;
      (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffbeceu + (uint32_t)((int)puVar2)))))) = 0xfa;
      (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffbed0u + (uint32_t)((int)puVar2)))))) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar2 + -0x53a6))));
      step_terminal_monitor
                (((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xffffbec4u + (uint32_t)((int)puVar2))))), ((F33MonitorLimits *)camry_host_ptr((uint32_t)((0x2b6c2u)))), ((F33TerminalMonitorCallbacks *)camry_host_ptr((uint32_t)((0x284ccu)))));
    }
  }
  else {
    reset_terminal_monitor(((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xffffbeb4u + (uint32_t)((int)puVar2))))));
    reset_terminal_monitor(((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xffffbebcu + (uint32_t)((int)puVar2))))));
    reset_terminal_monitor(((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xffffbec4u + (uint32_t)((int)puVar2))))));
  }
  if ((((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbeb4u + (uint32_t)((int)puVar2) * 1u)))) == '\0') && ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbebcu + (uint32_t)((int)puVar2) * 1u)))) == '\0')) &&
     ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbec4u + (uint32_t)((int)puVar2) * 1u)))) == '\0')) {
    mark_redundant_byte_6885_for_codes_21_to_34_32050(0x20);
  }
  if ((((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbeb4u + (uint32_t)((int)puVar2) * 1u)))) == '\"') || ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbebcu + (uint32_t)((int)puVar2) * 1u)))) == '\"')) ||
     ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbec4u + (uint32_t)((int)puVar2) * 1u)))) == '\"')) {
    retain_and_clear_fault_record(0xb);
    encode_fault_action_kind('\v','\x1c');
    select_current_fault_record(0xb);
  }
  return;
}

uint classify_sample_range_triplet_b(void)

{
  undefined2 uVar1;
  
  if ((((((DAT_febe64d9 == '\x02') && (DAT_febe64d1 == '\x02')) && ((DAT_febe6620 >> 0x11 & 1) == 0)
        ) && (((DAT_febe6620 >> 0x12 & 1) != 0 && ((DAT_febe661c >> 0x11 & 1) == 0)))) &&
      (((DAT_febe661c & 0x40000) != 0 &&
       (((DAT_febe6628 >> 0x11 & 1) == 0 && ((DAT_febe6614 & 1) == 0)))))) && (DAT_febe65f3 == 'Z'))
  {
    uVar1 = DAT_febe76cc;
    if ((DAT_febe76d0 <= DAT_0002b7ca) && (uVar1 = DAT_febe76ce, DAT_0002b7cc <= DAT_febe76d0)) {
      return 0x11;
    }
    DAT_febe6852 = uVar1;
    return 0x22;
  }
  return 0x44;
}

void record_sample_range_triplet_b_healthy_observed(void)

{
  uint event;
  
  event = (uint)DAT_febe76ce;
  report_diagnostic_healthy_observed((uint)DAT_febe76cc);
  report_diagnostic_healthy_observed(event);
  return;
}

void record_sample_range_triplet_b_failure(void)

{
  report_diagnostic_event_failure((uint)DAT_febe6852,0x32);
  return;
}

undefined2 summarize_sample_range_triplet_b_failures_41550(void)

{
  undefined2 uVar1;
  
  if ((((*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe76b4u + (uint32_t)(0) * (uint32_t)sizeof(F33TerminalMonitorState) + (uint32_t)offsetof(F33TerminalMonitorState, failing_count))))) != 0) ||
      ((*((volatile uint16_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe76b4u + (uint32_t)(1) * (uint32_t)sizeof(F33TerminalMonitorState)) + (uint32_t)(0) * (uint32_t)sizeof(F33TerminalMonitorState) + (uint32_t)offsetof(F33TerminalMonitorState, failing_count))))) != 0)) ||
     (uVar1 = 0, (*((volatile uint16_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe76b4u + (uint32_t)(2) * (uint32_t)sizeof(F33TerminalMonitorState)) + (uint32_t)(0) * (uint32_t)sizeof(F33TerminalMonitorState) + (uint32_t)offsetof(F33TerminalMonitorState, failing_count))))) != 0)) {
    uVar1 = 0x11;
  }
  return uVar1;
}

void reset_startup_triplet_a_and_summary_4156e(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  DAT_febe76ec = 0;
  DAT_febe76ee = 0;
  reset_terminal_monitor(startup_status_bit_triplet_a_states);
  reset_terminal_monitor(((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xffffbedcu + (uint32_t)((int)puVar1))))));
  reset_terminal_monitor(((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xffffbee4u + (uint32_t)((int)puVar1))))));
  return;
}

void reset_startup_triplet_a_and_control_41596(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  DAT_febe6858 = 0;
  DAT_febe6859 = 0;
  DAT_febe685a = 0;
  reset_terminal_monitor(startup_status_bit_triplet_a_states);
  reset_terminal_monitor(((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xffffbedcu + (uint32_t)((int)puVar1))))));
  reset_terminal_monitor(((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xffffbee4u + (uint32_t)((int)puVar1))))));
  return;
}

void step_startup_status_bit_triplet_a(void)

{
  int iVar1;
  uint32_t puVar2;
  char cVar3;
  ushort uVar4;
  byte bVar5;
  
  bVar5 = DAT_febe6859;
  cVar3 = DAT_febe6858;
  puVar2 = 0xfebeb800u;
  if (DAT_febe685a < DAT_0002b7d4) {
    iVar1 = 0;
    uVar4 = DAT_febe685a + 1;
  }
  else {
    iVar1 = 0x5a;
    uVar4 = DAT_febe685a;
  }
  if (DAT_0002bbd4 == 'Z') {
    puVar2 = 0xfebeb800u;
    force_unconfirmed_terminal_monitor_healthy
              (camry_host_addr(startup_status_bit_triplet_a_states), (0x2b6c6u), 
               (0x284d8u));
    force_unconfirmed_terminal_monitor_healthy
              (camry_host_addr(((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xffffbedcu + (uint32_t)((int)puVar2)))))), 
               (0x2b6c6u), (0x284d8u))
    ;
    force_unconfirmed_terminal_monitor_healthy
              (camry_host_addr(((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xffffbee4u + (uint32_t)((int)puVar2)))))), 
               (0x2b6c6u), (0x284d8u))
    ;
    goto LAB_000416ac;
  }
  if ((DAT_febe6764 & 1) != 0) goto LAB_000416ac;
  if (((DAT_febe6858 == '\0') && ((DAT_febe64cc & 0x7000) == 0)) && ((DAT_febe64cc & 1) == 0)) {
    if (DAT_febe6859 < DAT_0002b7d2) {
      bVar5 = DAT_febe6859 + 1;
      goto LAB_00041620;
    }
    bVar5 = 0;
    cVar3 = '\x11';
  }
  else {
LAB_00041620:
    if (DAT_febe6858 != '\x11') goto LAB_000416ac;
  }
  if (iVar1 == 0x5a) {
    DAT_febe76ee = 0x54;
    DAT_febe76ec = DAT_febe8285;
    puVar2 = 0xfebeb800u;
    step_terminal_monitor
              (startup_status_bit_triplet_a_states, ((F33MonitorLimits *)camry_host_ptr((uint32_t)((0x2b6c6u)))), ((F33TerminalMonitorCallbacks *)camry_host_ptr((uint32_t)((0x284d8u)))));
    (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffbeeeu + (uint32_t)((int)puVar2)))))) = 0x55;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbeecu + (uint32_t)((int)puVar2) * 1u)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x357a)))));
    step_terminal_monitor
              (((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xffffbedcu + (uint32_t)((int)puVar2))))), ((F33MonitorLimits *)camry_host_ptr((uint32_t)((0x2b6c6u)))), ((F33TerminalMonitorCallbacks *)camry_host_ptr((uint32_t)((0x284d8u)))))
    ;
    (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffbeeeu + (uint32_t)((int)puVar2)))))) = 0x56;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbeecu + (uint32_t)((int)puVar2) * 1u)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x3579)))));
    step_terminal_monitor
              (((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xffffbee4u + (uint32_t)((int)puVar2))))), ((F33MonitorLimits *)camry_host_ptr((uint32_t)((0x2b6c6u)))), ((F33TerminalMonitorCallbacks *)camry_host_ptr((uint32_t)((0x284d8u)))))
    ;
  }
LAB_000416ac:
  if ((((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbed4u + (uint32_t)((int)puVar2) * 1u)))) == '\0') && ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbedcu + (uint32_t)((int)puVar2) * 1u)))) == '\0')) &&
     ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbee4u + (uint32_t)((int)puVar2) * 1u)))) == '\0')) {
    mark_redundant_byte_6884_for_codes_21_to_34_32036(0x19);
  }
  if ((((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbed4u + (uint32_t)((int)puVar2) * 1u)))) == '\"') || ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbedcu + (uint32_t)((int)puVar2) * 1u)))) == '\"')) ||
     ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbee4u + (uint32_t)((int)puVar2) * 1u)))) == '\"')) {
    retain_and_clear_fault_record(10);
    encode_fault_action_kind('\n','\x1d');
    select_current_fault_record(10);
  }
  (*((char *)camry_host_ptr((uint32_t)((int)(0xffffb058u + (uint32_t)((int)puVar2)))))) = cVar3;
  (*((byte *)camry_host_ptr((uint32_t)((int)0xffffb058u + (int)(puVar2 + 1))))) = bVar5;
  (*((ushort *)camry_host_ptr((uint32_t)((int)(0xffffb05au + (uint32_t)((int)puVar2)))))) = uVar4;
  return;
}

uint classify_startup_status_bit_triplet_a(void)

{
  if ((((DAT_febe64d8 == '\0') && (DAT_febe64d0 == '\0')) && ((DAT_febe6620 >> 2 & 1) != 0)) &&
     ((((DAT_febe661c >> 2 & 1) != 0 && ((DAT_febe6628 >> 1 & 1) == 0)) &&
      (((DAT_febe6614 & 1) != 0 && (DAT_febe65f0 == 'Z')))))) {
    if (DAT_febe76ec != 'Z') {
      return 0x11;
    }
    return 0x22;
  }
  return 0x44;
}

void record_startup_status_bit_triplet_a_healthy_observed(void)

{
  report_diagnostic_healthy_observed((uint)DAT_febe76ee);
  return;
}

void record_startup_status_bit_triplet_a_failure(void)

{
  report_diagnostic_event_failure((uint)DAT_febe76ee,0x32);
  return;
}

undefined2 summarize_startup_triplet_a_failures_41788(void)

{
  undefined2 uVar1;
  
  if ((((*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe76d4u + (uint32_t)(0) * (uint32_t)sizeof(F33TerminalMonitorState) + (uint32_t)offsetof(F33TerminalMonitorState, failing_count))))) != 0) ||
      ((*((volatile uint16_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe76d4u + (uint32_t)(1) * (uint32_t)sizeof(F33TerminalMonitorState)) + (uint32_t)(0) * (uint32_t)sizeof(F33TerminalMonitorState) + (uint32_t)offsetof(F33TerminalMonitorState, failing_count))))) != 0)) ||
     (uVar1 = 0, (*((volatile uint16_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe76d4u + (uint32_t)(2) * (uint32_t)sizeof(F33TerminalMonitorState)) + (uint32_t)(0) * (uint32_t)sizeof(F33TerminalMonitorState) + (uint32_t)offsetof(F33TerminalMonitorState, failing_count))))) != 0)) {
    uVar1 = 0x11;
  }
  return uVar1;
}

void reset_startup_triplet_b_and_summary_417a6(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  DAT_febe7708 = 0;
  DAT_febe770a = 0;
  reset_terminal_monitor(startup_status_bit_triplet_b_states);
  reset_terminal_monitor(((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xffffbef8u + (uint32_t)((int)puVar1))))));
  reset_terminal_monitor(((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xffffbf00u + (uint32_t)((int)puVar1))))));
  return;
}

void reset_startup_triplet_b_and_control_417ce(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  DAT_febe685c = 0;
  DAT_febe685d = 0;
  DAT_febe685e = 0;
  reset_terminal_monitor(startup_status_bit_triplet_b_states);
  reset_terminal_monitor(((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xffffbef8u + (uint32_t)((int)puVar1))))));
  reset_terminal_monitor(((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xffffbf00u + (uint32_t)((int)puVar1))))));
  return;
}

void step_startup_status_bit_triplet_b(void)

{
  int iVar1;
  uint32_t puVar2;
  char cVar3;
  ushort uVar4;
  byte bVar5;
  
  bVar5 = DAT_febe685d;
  cVar3 = DAT_febe685c;
  puVar2 = 0xfebeb800u;
  if (DAT_febe685e < DAT_0002b7d8) {
    iVar1 = 0;
    uVar4 = DAT_febe685e + 1;
  }
  else {
    iVar1 = 0x5a;
    uVar4 = DAT_febe685e;
  }
  if (DAT_0002bbd8 == 'Z') {
    puVar2 = 0xfebeb800u;
    force_unconfirmed_terminal_monitor_healthy
              (camry_host_addr(startup_status_bit_triplet_b_states), (0x2b6cau), 
               (0x284e4u));
    force_unconfirmed_terminal_monitor_healthy
              (camry_host_addr(((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xffffbef8u + (uint32_t)((int)puVar2)))))), 
               (0x2b6cau), (0x284e4u))
    ;
    force_unconfirmed_terminal_monitor_healthy
              (camry_host_addr(((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xffffbf00u + (uint32_t)((int)puVar2)))))), 
               (0x2b6cau), (0x284e4u))
    ;
    goto LAB_000418e4;
  }
  if ((DAT_febe6764 >> 1 & 1) != 0) goto LAB_000418e4;
  if (((DAT_febe685c == '\0') && ((DAT_febe64cc & 0x70000000) == 0)) &&
     ((DAT_febe64cc >> 0x10 & 1) == 0)) {
    if (DAT_febe685d < DAT_0002b7d6) {
      bVar5 = DAT_febe685d + 1;
      goto LAB_0004185a;
    }
    bVar5 = 0;
    cVar3 = '\x11';
  }
  else {
LAB_0004185a:
    if (DAT_febe685c != '\x11') goto LAB_000418e4;
  }
  if (iVar1 == 0x5a) {
    DAT_febe770a = 0x5a;
    DAT_febe7708 = DAT_febe828b;
    puVar2 = 0xfebeb800u;
    step_terminal_monitor
              (startup_status_bit_triplet_b_states, ((F33MonitorLimits *)camry_host_ptr((uint32_t)((0x2b6cau)))), ((F33TerminalMonitorCallbacks *)camry_host_ptr((uint32_t)((0x284e4u)))));
    (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffbf0au + (uint32_t)((int)puVar2)))))) = 0x5b;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbf08u + (uint32_t)((int)puVar2) * 1u)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x3574)))));
    step_terminal_monitor
              (((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xffffbef8u + (uint32_t)((int)puVar2))))), ((F33MonitorLimits *)camry_host_ptr((uint32_t)((0x2b6cau)))), ((F33TerminalMonitorCallbacks *)camry_host_ptr((uint32_t)((0x284e4u)))))
    ;
    (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffbf0au + (uint32_t)((int)puVar2)))))) = 0x5c;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbf08u + (uint32_t)((int)puVar2) * 1u)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x3573)))));
    step_terminal_monitor
              (((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xffffbf00u + (uint32_t)((int)puVar2))))), ((F33MonitorLimits *)camry_host_ptr((uint32_t)((0x2b6cau)))), ((F33TerminalMonitorCallbacks *)camry_host_ptr((uint32_t)((0x284e4u)))))
    ;
  }
LAB_000418e4:
  if ((((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbef0u + (uint32_t)((int)puVar2) * 1u)))) == '\0') && ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbef8u + (uint32_t)((int)puVar2) * 1u)))) == '\0')) &&
     ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbf00u + (uint32_t)((int)puVar2) * 1u)))) == '\0')) {
    mark_redundant_byte_6885_for_codes_21_to_34_32050(0x19);
  }
  if ((((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbef0u + (uint32_t)((int)puVar2) * 1u)))) == '\"') || ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbef8u + (uint32_t)((int)puVar2) * 1u)))) == '\"')) ||
     ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbf00u + (uint32_t)((int)puVar2) * 1u)))) == '\"')) {
    retain_and_clear_fault_record(0xb);
    encode_fault_action_kind('\v','\x1e');
    select_current_fault_record(0xb);
  }
  (*((char *)camry_host_ptr((uint32_t)((int)(0xffffb05cu + (uint32_t)((int)puVar2)))))) = cVar3;
  (*((byte *)camry_host_ptr((uint32_t)((int)0xffffb05cu + (int)(puVar2 + 1))))) = bVar5;
  (*((ushort *)camry_host_ptr((uint32_t)((int)(0xffffb05eu + (uint32_t)((int)puVar2)))))) = uVar4;
  return;
}

uint classify_startup_status_bit_triplet_b(void)

{
  if ((((DAT_febe64d9 == '\0') && (DAT_febe64d1 == '\0')) && ((DAT_febe6620 >> 0x12 & 1) != 0)) &&
     ((((DAT_febe661c >> 0x12 & 1) != 0 && ((DAT_febe6628 >> 0x11 & 1) == 0)) &&
      (((DAT_febe6614 & 1) != 0 && (DAT_febe65f0 == 'Z')))))) {
    if (DAT_febe7708 != 'Z') {
      return 0x11;
    }
    return 0x22;
  }
  return 0x44;
}

void record_startup_status_bit_triplet_b_healthy_observed(void)

{
  report_diagnostic_healthy_observed((uint)DAT_febe770a);
  return;
}

void record_startup_status_bit_triplet_b_failure(void)

{
  report_diagnostic_event_failure((uint)DAT_febe770a,0x32);
  return;
}

undefined2 summarize_startup_triplet_b_failures_419c0(void)

{
  undefined2 uVar1;
  
  if ((((*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe76f0u + (uint32_t)(0) * (uint32_t)sizeof(F33TerminalMonitorState) + (uint32_t)offsetof(F33TerminalMonitorState, failing_count))))) != 0) ||
      ((*((volatile uint16_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe76f0u + (uint32_t)(1) * (uint32_t)sizeof(F33TerminalMonitorState)) + (uint32_t)(0) * (uint32_t)sizeof(F33TerminalMonitorState) + (uint32_t)offsetof(F33TerminalMonitorState, failing_count))))) != 0)) ||
     (uVar1 = 0, (*((volatile uint16_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe76f0u + (uint32_t)(2) * (uint32_t)sizeof(F33TerminalMonitorState)) + (uint32_t)(0) * (uint32_t)sizeof(F33TerminalMonitorState) + (uint32_t)offsetof(F33TerminalMonitorState, failing_count))))) != 0)) {
    uVar1 = 0x11;
  }
  return uVar1;
}

void reset_matched_startup_triplet_a_and_summary_419de(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  DAT_febe7724 = 0;
  DAT_febe7726 = 0;
  reset_terminal_monitor(matched_state2_startup_triplet_a_states);
  reset_terminal_monitor(((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xffffbf14u + (uint32_t)((int)puVar1))))));
  reset_terminal_monitor(((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xffffbf1cu + (uint32_t)((int)puVar1))))));
  return;
}

void reset_matched_startup_triplet_a_and_control_41a06(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  DAT_febe6860 = 0;
  DAT_febe6861 = 0;
  reset_terminal_monitor(matched_state2_startup_triplet_a_states);
  reset_terminal_monitor(((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xffffbf14u + (uint32_t)((int)puVar1))))));
  reset_terminal_monitor(((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xffffbf1cu + (uint32_t)((int)puVar1))))));
  return;
}

void step_matched_state2_startup_triplet_a(void)

{
  uint32_t puVar1;
  char cVar2;
  byte bVar3;
  
  bVar3 = DAT_febe6861;
  cVar2 = DAT_febe6860;
  puVar1 = 0xfebeb800u;
  if (DAT_0002bbdc == 'Z') {
    puVar1 = 0xfebeb800u;
    force_unconfirmed_terminal_monitor_healthy
              (camry_host_addr(matched_state2_startup_triplet_a_states), 
               (0x2b6ceu), 
               (0x284f0u));
    force_unconfirmed_terminal_monitor_healthy
              (camry_host_addr(((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xffffbf14u + (uint32_t)((int)puVar1)))))), 
               (0x2b6ceu), 
               (0x284f0u));
    force_unconfirmed_terminal_monitor_healthy
              (camry_host_addr(((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xffffbf1cu + (uint32_t)((int)puVar1)))))), 
               (0x2b6ceu), 
               (0x284f0u));
    goto LAB_00041b00;
  }
  if ((DAT_febe6764 & 1) != 0) goto LAB_00041b00;
  if ((DAT_febe6860 == '\0') && ((DAT_febe64cc & 0x7000) == 0)) {
    if (DAT_febe6861 < DAT_0002b7da) {
      bVar3 = DAT_febe6861 + 1;
      goto LAB_00041a78;
    }
    bVar3 = 0;
    cVar2 = '\x11';
  }
  else {
LAB_00041a78:
    if (DAT_febe6860 != '\x11') goto LAB_00041b00;
  }
  DAT_febe7726 = 0x7f;
  DAT_febe7724 = DAT_febe8285;
  puVar1 = 0xfebeb800u;
  step_terminal_monitor
            (matched_state2_startup_triplet_a_states, ((F33MonitorLimits *)camry_host_ptr((uint32_t)((0x2b6ceu)))), ((F33TerminalMonitorCallbacks *)camry_host_ptr((uint32_t)((0x284f0u)))));
  (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffbf26u + (uint32_t)((int)puVar1)))))) = 0x80;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbf24u + (uint32_t)((int)puVar1) * 1u)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x357a)))));
  step_terminal_monitor
            (((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xffffbf14u + (uint32_t)((int)puVar1))))), ((F33MonitorLimits *)camry_host_ptr((uint32_t)((0x2b6ceu)))), ((F33TerminalMonitorCallbacks *)camry_host_ptr((uint32_t)((0x284f0u)))));
  (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffbf26u + (uint32_t)((int)puVar1)))))) = 0x81;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbf24u + (uint32_t)((int)puVar1) * 1u)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x3579)))));
  step_terminal_monitor
            (((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xffffbf1cu + (uint32_t)((int)puVar1))))), ((F33MonitorLimits *)camry_host_ptr((uint32_t)((0x2b6ceu)))), ((F33TerminalMonitorCallbacks *)camry_host_ptr((uint32_t)((0x284f0u)))));
LAB_00041b00:
  if ((((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbf0cu + (uint32_t)((int)puVar1) * 1u)))) == '\0') && ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbf14u + (uint32_t)((int)puVar1) * 1u)))) == '\0')) &&
     ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbf1cu + (uint32_t)((int)puVar1) * 1u)))) == '\0')) {
    mark_redundant_byte_6884_for_codes_21_to_34_32036(0x21);
  }
  if ((((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbf0cu + (uint32_t)((int)puVar1) * 1u)))) == '\"') || ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbf14u + (uint32_t)((int)puVar1) * 1u)))) == '\"')) ||
     ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbf1cu + (uint32_t)((int)puVar1) * 1u)))) == '\"')) {
    retain_and_clear_fault_record(10);
    encode_fault_action_kind('\n','\x1b');
    encode_fault_action_kind('\n','2');
    select_current_fault_record(10);
  }
  (*((char *)camry_host_ptr((uint32_t)((int)(0xffffb060u + (uint32_t)((int)puVar1)))))) = cVar2;
  (*((byte *)camry_host_ptr((uint32_t)((int)0xffffb060u + (int)(puVar1 + 1))))) = bVar3;
  return;
}

uint classify_matched_state2_startup_triplet_a(void)

{
  if ((((((DAT_febe64d8 == '\x02') && (DAT_febe64d0 == '\x02')) && ((DAT_febe6620 >> 1 & 1) == 0))
       && (((DAT_febe6620 >> 2 & 1) != 0 && ((DAT_febe661c >> 1 & 1) == 0)))) &&
      (((DAT_febe661c >> 2 & 1) != 0 &&
       (((DAT_febe6628 >> 1 & 1) == 0 && ((DAT_febe6614 & 1) == 0)))))) && (DAT_febe65f6 == 'Z')) {
    if (DAT_febe7724 != 'Z') {
      return 0x11;
    }
    return 0x22;
  }
  return 0x44;
}

void record_matched_state2_startup_triplet_a_healthy_observed(void)

{
  report_diagnostic_healthy_observed((uint)DAT_febe7726);
  return;
}

void record_matched_state2_startup_triplet_a_failure(void)

{
  report_diagnostic_event_failure((uint)DAT_febe7726,0x32);
  return;
}

undefined2 summarize_matched_startup_triplet_a_failures_41bf0(void)

{
  undefined2 uVar1;
  
  if ((((*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe770cu + (uint32_t)(0) * (uint32_t)sizeof(F33TerminalMonitorState) + (uint32_t)offsetof(F33TerminalMonitorState, failing_count))))) != 0) ||
      ((*((volatile uint16_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe770cu + (uint32_t)(1) * (uint32_t)sizeof(F33TerminalMonitorState)) + (uint32_t)(0) * (uint32_t)sizeof(F33TerminalMonitorState) + (uint32_t)offsetof(F33TerminalMonitorState, failing_count))))) != 0)) ||
     (uVar1 = 0, (*((volatile uint16_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe770cu + (uint32_t)(2) * (uint32_t)sizeof(F33TerminalMonitorState)) + (uint32_t)(0) * (uint32_t)sizeof(F33TerminalMonitorState) + (uint32_t)offsetof(F33TerminalMonitorState, failing_count))))) != 0)) {
    uVar1 = 0x11;
  }
  return uVar1;
}

void reset_matched_startup_triplet_b_and_summary_41c0e(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  DAT_febe7740 = 0;
  DAT_febe7742 = 0;
  reset_terminal_monitor(matched_state2_startup_triplet_b_states);
  reset_terminal_monitor(((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xffffbf30u + (uint32_t)((int)puVar1))))));
  reset_terminal_monitor(((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xffffbf38u + (uint32_t)((int)puVar1))))));
  return;
}

void reset_matched_startup_triplet_b_and_control_41c36(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  DAT_febe6864 = 0;
  DAT_febe6865 = 0;
  reset_terminal_monitor(matched_state2_startup_triplet_b_states);
  reset_terminal_monitor(((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xffffbf30u + (uint32_t)((int)puVar1))))));
  reset_terminal_monitor(((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xffffbf38u + (uint32_t)((int)puVar1))))));
  return;
}

void step_matched_state2_startup_triplet_b(void)

{
  uint32_t puVar1;
  char cVar2;
  byte bVar3;
  
  bVar3 = DAT_febe6865;
  cVar2 = DAT_febe6864;
  puVar1 = 0xfebeb800u;
  if (DAT_0002bbe0 == 'Z') {
    puVar1 = 0xfebeb800u;
    force_unconfirmed_terminal_monitor_healthy
              (camry_host_addr(matched_state2_startup_triplet_b_states), 
               (0x2b6d2u), 
               (0x284fcu));
    force_unconfirmed_terminal_monitor_healthy
              (camry_host_addr(((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xffffbf30u + (uint32_t)((int)puVar1)))))), 
               (0x2b6d2u), 
               (0x284fcu));
    force_unconfirmed_terminal_monitor_healthy
              (camry_host_addr(((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xffffbf38u + (uint32_t)((int)puVar1)))))), 
               (0x2b6d2u), 
               (0x284fcu));
    goto LAB_00041d30;
  }
  if ((DAT_febe6764 >> 1 & 1) != 0) goto LAB_00041d30;
  if ((DAT_febe6864 == '\0') && (((int)DAT_febe64cc & 0x7fffffff) >> 0x1c == 0)) {
    if (DAT_febe6865 < DAT_0002b7de) {
      bVar3 = DAT_febe6865 + 1;
      goto LAB_00041ca8;
    }
    bVar3 = 0;
    cVar2 = '\x11';
  }
  else {
LAB_00041ca8:
    if (DAT_febe6864 != '\x11') goto LAB_00041d30;
  }
  DAT_febe7742 = 0x82;
  DAT_febe7740 = DAT_febe828b;
  puVar1 = 0xfebeb800u;
  step_terminal_monitor
            (matched_state2_startup_triplet_b_states, ((F33MonitorLimits *)camry_host_ptr((uint32_t)((0x2b6d2u)))), ((F33TerminalMonitorCallbacks *)camry_host_ptr((uint32_t)((0x284fcu)))));
  (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffbf42u + (uint32_t)((int)puVar1)))))) = 0x83;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbf40u + (uint32_t)((int)puVar1) * 1u)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x3574)))));
  step_terminal_monitor
            (((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xffffbf30u + (uint32_t)((int)puVar1))))), ((F33MonitorLimits *)camry_host_ptr((uint32_t)((0x2b6d2u)))), ((F33TerminalMonitorCallbacks *)camry_host_ptr((uint32_t)((0x284fcu)))));
  (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffbf42u + (uint32_t)((int)puVar1)))))) = 0x84;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbf40u + (uint32_t)((int)puVar1) * 1u)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x3573)))));
  step_terminal_monitor
            (((F33TerminalMonitorState *)camry_host_ptr((uint32_t)((0xffffbf38u + (uint32_t)((int)puVar1))))), ((F33MonitorLimits *)camry_host_ptr((uint32_t)((0x2b6d2u)))), ((F33TerminalMonitorCallbacks *)camry_host_ptr((uint32_t)((0x284fcu)))));
LAB_00041d30:
  if ((((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbf28u + (uint32_t)((int)puVar1) * 1u)))) == '\0') && ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbf30u + (uint32_t)((int)puVar1) * 1u)))) == '\0')) &&
     ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbf38u + (uint32_t)((int)puVar1) * 1u)))) == '\0')) {
    mark_redundant_byte_6885_for_codes_21_to_34_32050(0x21);
  }
  if ((((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbf28u + (uint32_t)((int)puVar1) * 1u)))) == '\"') || ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbf30u + (uint32_t)((int)puVar1) * 1u)))) == '\"')) ||
     ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbf38u + (uint32_t)((int)puVar1) * 1u)))) == '\"')) {
    retain_and_clear_fault_record(0xb);
    encode_fault_action_kind('\v','\x1c');
    encode_fault_action_kind('\v','2');
    select_current_fault_record(0xb);
  }
  (*((char *)camry_host_ptr((uint32_t)((int)(0xffffb064u + (uint32_t)((int)puVar1)))))) = cVar2;
  (*((byte *)camry_host_ptr((uint32_t)((int)0xffffb064u + (int)(puVar1 + 1))))) = bVar3;
  return;
}

uint classify_matched_state2_startup_triplet_b(void)

{
  if ((((((DAT_febe64d9 == '\x02') && (DAT_febe64d1 == '\x02')) && ((DAT_febe6620 >> 0x11 & 1) == 0)
        ) && (((DAT_febe6620 >> 0x12 & 1) != 0 && ((DAT_febe661c >> 0x11 & 1) == 0)))) &&
      (((DAT_febe661c & 0x40000) != 0 &&
       (((DAT_febe6628 >> 0x11 & 1) == 0 && ((DAT_febe6614 & 1) == 0)))))) && (DAT_febe65f7 == 'Z'))
  {
    if (DAT_febe7740 != 'Z') {
      return 0x11;
    }
    return 0x22;
  }
  return 0x44;
}

void record_matched_state2_startup_triplet_b_healthy_observed(void)

{
  report_diagnostic_healthy_observed((uint)DAT_febe7742);
  return;
}

void record_matched_state2_startup_triplet_b_failure(void)

{
  report_diagnostic_event_failure((uint)DAT_febe7742,0x32);
  return;
}

undefined2 summarize_matched_startup_triplet_b_failures_41e24(void)

{
  undefined2 uVar1;
  
  if ((((*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe7728u + (uint32_t)(0) * (uint32_t)sizeof(F33TerminalMonitorState) + (uint32_t)offsetof(F33TerminalMonitorState, failing_count))))) != 0) ||
      ((*((volatile uint16_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe7728u + (uint32_t)(1) * (uint32_t)sizeof(F33TerminalMonitorState)) + (uint32_t)(0) * (uint32_t)sizeof(F33TerminalMonitorState) + (uint32_t)offsetof(F33TerminalMonitorState, failing_count))))) != 0)) ||
     (uVar1 = 0, (*((volatile uint16_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe7728u + (uint32_t)(2) * (uint32_t)sizeof(F33TerminalMonitorState)) + (uint32_t)(0) * (uint32_t)sizeof(F33TerminalMonitorState) + (uint32_t)offsetof(F33TerminalMonitorState, failing_count))))) != 0)) {
    uVar1 = 0x11;
  }
  return uVar1;
}

void reset_midpoint_pair_latched_triplet_41e42(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  DAT_febe7744 = 0;
  DAT_febe7746 = 0;
  DAT_febe7748 = 0;
  reset_latched_monitor((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe774cu)));
  reset_latched_monitor(((F33LatchedMonitorState *)camry_host_ptr((uint32_t)((0xffffbf58u + (uint32_t)((int)puVar1))))));
  reset_latched_monitor(((F33LatchedMonitorState *)camry_host_ptr((uint32_t)((0xffffbf64u + (uint32_t)((int)puVar1))))));
  return;
}

void clear_midpoint_pair_latched_triplet_41e6c(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  DAT_febe7744 = 0;
  DAT_febe7746 = 0;
  DAT_febe7748 = 0;
  reset_latched_monitor((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe774cu)));
  reset_latched_monitor(((F33LatchedMonitorState *)camry_host_ptr((uint32_t)((0xffffbf58u + (uint32_t)((int)puVar1))))));
  reset_latched_monitor(((F33LatchedMonitorState *)camry_host_ptr((uint32_t)((0xffffbf64u + (uint32_t)((int)puVar1))))));
  return;
}

void update_midpoint_pair_latched_triplet_41e96(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  if (DAT_0002bbe4 == 'Z') {
    reset_latched_monitor((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe774cu)));
    reset_latched_monitor(((F33LatchedMonitorState *)camry_host_ptr((uint32_t)((0xffffbf58u + (uint32_t)((int)puVar1))))));
    reset_latched_monitor(((F33LatchedMonitorState *)camry_host_ptr((uint32_t)((0xffffbf64u + (uint32_t)((int)puVar1))))));
  }
  else if ((DAT_febe71ec & 1) == 0) {
    DAT_febe7744 = 0x4a;
    DAT_febe7746 = ((volatile int16_t *)camry_host_ptr(0xfebe7e84u))[0];
    DAT_febe7748 = ((volatile int16_t *)camry_host_ptr(0xfebe7e90u))[0];
    step_latched_monitor
              ((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe774cu)),(F33MonitorLimits *)&PTR_DAT_0002b7e4,
               (F33TwoSidedMonitorCallbacks *)&PTR_classify_channel_negative_pair_a_00028508);
    (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffbf44u + (uint32_t)((int)puVar1)))))) = 0x4b;
    (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffbf46u + (uint32_t)((int)puVar1)))))) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x397a))));
    (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffbf48u + (uint32_t)((int)puVar1)))))) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x396e))));
    step_latched_monitor
              (((F33LatchedMonitorState *)camry_host_ptr((uint32_t)((0xffffbf58u + (uint32_t)((int)puVar1))))),
               (F33MonitorLimits *)&PTR_DAT_0002b7e4,
               (F33TwoSidedMonitorCallbacks *)&PTR_classify_channel_negative_pair_a_00028508);
    (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffbf44u + (uint32_t)((int)puVar1)))))) = 0x4c;
    (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffbf46u + (uint32_t)((int)puVar1)))))) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x3978))));
    (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffbf48u + (uint32_t)((int)puVar1)))))) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x396c))));
    step_latched_monitor
              (((F33LatchedMonitorState *)camry_host_ptr((uint32_t)((0xffffbf64u + (uint32_t)((int)puVar1))))),
               (F33MonitorLimits *)&PTR_DAT_0002b7e4,
               (F33TwoSidedMonitorCallbacks *)&PTR_classify_channel_negative_pair_a_00028508);
  }
  else {
    retain_disabled_latched_monitor
              ((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe774cu)),(F33MonitorLimits *)&PTR_DAT_0002b7e4);
    retain_disabled_latched_monitor
              (((F33LatchedMonitorState *)camry_host_ptr((uint32_t)((0xffffbf58u + (uint32_t)((int)puVar1))))),
               (F33MonitorLimits *)&PTR_DAT_0002b7e4);
    retain_disabled_latched_monitor
              (((F33LatchedMonitorState *)camry_host_ptr((uint32_t)((0xffffbf64u + (uint32_t)((int)puVar1))))),
               (F33MonitorLimits *)&PTR_DAT_0002b7e4);
  }
  set_channel_monitor_status_a(4,(uchar)(*((undefined4 *)camry_host_ptr((uint32_t)((0xffffbf4cu + (uint32_t)((int)puVar1)))))));
  set_channel_monitor_status_a(5,(uchar)(*((undefined4 *)camry_host_ptr((uint32_t)((0xffffbf58u + (uint32_t)((int)puVar1)))))));
  set_channel_monitor_status_a(6,(uchar)(*((undefined4 *)camry_host_ptr((uint32_t)((0xffffbf64u + (uint32_t)((int)puVar1)))))));
  return;
}

uint classify_channel_negative_pair_a(void)

{
  int iVar1;
  int iVar2;
  
  iVar2 = (int)(int16_t)DAT_0002b80e;
  iVar1 = ((int)(int16_t)DAT_febe7746) - iVar2;
  if ((iVar1 < 0 != (((int)(int16_t)DAT_febe7746) < 0 != iVar2 < 0 && iVar2 < 0 == iVar1 < 0)) &&
     (iVar2 = (int)(int16_t)DAT_0002b810, iVar1 = ((int)(int16_t)DAT_febe7748) - iVar2,
     iVar1 < 0 != (((int)(int16_t)DAT_febe7748) < 0 != iVar2 < 0 && iVar2 < 0 == iVar1 < 0))) {
    return 0x22;
  }
  return 0x11;
}

void report_diagnostic_healthy_observed_cell_41f9a(void)

{
  report_diagnostic_healthy_observed((uint)DAT_febe7744);
  return;
}

void report_diagnostic_event_failure_10_41faa(void)

{
  report_diagnostic_event_failure((uint)DAT_febe7744,10);
  return;
}

void return_only_stub_41fbc(void)

{
  return;
}

void initialize_clipped_three_channel_q16_state_41fbe(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  
  if ((int)DAT_febe62f8 + 0x7fff < 0 == (-1 < (int)DAT_febe62f8 && (int)DAT_febe62f8 + 0x7fff < 0) &&
      ((int)(int32_t)DAT_febe62f8) != -0x7fff) {
    iVar3 = ((int)(int32_t)DAT_febe62f8);
    if ((int)DAT_febe62f8 + -0x7fff < 0 == ((int)DAT_febe62f8 < 0 && -1 < (int)DAT_febe62f8 + -0x7fff) &&
        ((int)(int32_t)DAT_febe62f8) != 0x7fff) {
      iVar3 = 0x7fff;
    }
  }
  else {
    iVar3 = -0x7fff;
  }
  if ((int)DAT_febe62fc + 0x7fff < 0 == (-1 < (int)DAT_febe62fc && (int)DAT_febe62fc + 0x7fff < 0) &&
      ((int)(int32_t)DAT_febe62fc) != -0x7fff) {
    iVar2 = ((int)(int32_t)DAT_febe62fc);
    if ((int)DAT_febe62fc + -0x7fff < 0 == ((int)DAT_febe62fc < 0 && -1 < (int)DAT_febe62fc + -0x7fff) &&
        ((int)(int32_t)DAT_febe62fc) != 0x7fff) {
      iVar2 = 0x7fff;
    }
  }
  else {
    iVar2 = -0x7fff;
  }
  if ((int)DAT_febe6300 + 0x7fff < 0 == (-1 < (int)DAT_febe6300 && (int)DAT_febe6300 + 0x7fff < 0) &&
      ((int)(int32_t)DAT_febe6300) != -0x7fff) {
    iVar1 = ((int)(int32_t)DAT_febe6300);
    if ((int)DAT_febe6300 + -0x7fff < 0 == ((int)DAT_febe6300 < 0 && -1 < (int)DAT_febe6300 + -0x7fff) &&
        ((int)(int32_t)DAT_febe6300) != 0x7fff) {
      iVar1 = 0x7fff;
    }
  }
  else {
    iVar1 = -0x7fff;
  }
  DAT_febe7770 = (short)iVar3;
  DAT_febe7772 = (short)iVar2;
  DAT_febe7774 = (short)iVar1;
  DAT_febe7778 = iVar3 << 0x10;
  DAT_febe777c = iVar2 << 0x10;
  DAT_febe7780 = iVar1 << 0x10;
  return;
}
