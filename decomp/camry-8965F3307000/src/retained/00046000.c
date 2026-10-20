#include "common.h"

void publish_thermistor_range_monitor_status(uchar index,uint packed_status)

{
  if (index < 2) {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe7bf4u + (uint32_t)(index) * 1u)))) = (char)packed_status;
  }
  return;
}

void return_only_stub_4606a(void)

{
  return;
}

void return_only_stub_4606c(void)

{
  return;
}

void return_only_stub_4606e(void)

{
  return;
}

void reset_shared_snapshot_monitor_zero_46070(void)

{
  clear_word_state_and_five_halfword_counters_6b98a(((undefined4 *)camry_host_ptr((uint32_t)((0xfebe7c00u)))));
  return;
}

void reset_shared_snapshot_monitor_0_46080(void)

{
  clear_word_state_and_five_halfword_counters_6b98a(((undefined4 *)camry_host_ptr((uint32_t)((0xfebe7c00u)))));
  return;
}

void update_and_publish_snapshot_monitor_0_46090(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  if (DAT_febe8a24 != 'Z') {
    return;
  }
  if (DAT_0002bc7c == 'Z') {
    clear_word_state_and_five_halfword_counters_6b98a(((undefined4 *)camry_host_ptr((uint32_t)((0xfebe7c00u)))));
  }
  else {
    if ((DAT_febeeb85 == 'Z') && ((DAT_febe71ec >> 5 & 1) == 0)) {
      puVar1 = 0xfebeb800u;
      step_escalating_monitor
                (((F33EscalatingMonitorState *)camry_host_ptr((uint32_t)((0xfebe7c00u)))), (ushort *)((undefined *)camry_host_ptr(0x2ba20u)), 
                 (uint *)&PTR_classify_snapshot_status_a_00028cf0);
      if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x3bf0))))) == 'Z') {
        force_monitor_escalation
                  (((F33EscalatingMonitorState *)camry_host_ptr((uint32_t)((0xfebe7c00u)))), (ushort *)((undefined *)camry_host_ptr(0x2ba20u)), 
                   (uint *)&PTR_classify_snapshot_status_a_00028cf0);
      }
      goto LAB_0004610e;
    }
    retain_disabled_escalating_monitor(((F33EscalatingMonitorState *)camry_host_ptr((uint32_t)((0xfebe7c00u)))), (ushort *)((undefined *)camry_host_ptr(0x2ba20u)));
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x3bf0))))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x3bef))))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x3bee))))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x3bed))))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x3bec))))) = 0;
LAB_0004610e:
  publish_shared_snapshot_monitor_status(0,(*((uint *)camry_host_ptr((uint32_t)(puVar1 + -0x3c00)))));
  return;
}

uint classify_snapshot_status_a(void)

{
  uint uVar1;
  
  DAT_febe7c11 = '\0';
  DAT_febe7c12 = '\0';
  DAT_febe7c13 = '\0';
  DAT_febe7c14 = '\0';
  if (DAT_febe631c != DAT_febe7c15) {
    DAT_febe7c11 = 'Z';
  }
  if (DAT_febe631d != DAT_febe7c16) {
    DAT_febe7c12 = 'Z';
  }
  if (DAT_febe631e != DAT_febe7c17) {
    DAT_febe7c13 = 'Z';
  }
  if (DAT_febe631f != DAT_febe7c18) {
    DAT_febe7c14 = 'Z';
  }
  if (((((DAT_febe7c11 == 'Z') || (DAT_febe7c12 == 'Z')) || (DAT_febe7c13 == 'Z')) ||
      (DAT_febe7c14 == 'Z')) && (DAT_0002bac6 <= DAT_febe7db2)) {
    uVar1 = 0x22;
  }
  else if ((DAT_febe7b48 == 'Z') && (DAT_febe7b49 == 'Z')) {
    uVar1 = 0x11;
  }
  else {
    uVar1 = 0x33;
  }
  DAT_febe7c15 = DAT_febe631c;
  DAT_febe7c16 = DAT_febe631d;
  DAT_febe7c17 = DAT_febe631e;
  DAT_febe7c18 = DAT_febe631f;
  return uVar1;
}

uint classify_snapshot_status_recovery_a(void)

{
  uint uVar1;
  
  DAT_febe7c11 = '\0';
  DAT_febe7c12 = '\0';
  DAT_febe7c13 = '\0';
  DAT_febe7c14 = '\0';
  if (DAT_febe631c != DAT_febe7c15) {
    DAT_febe7c11 = 'Z';
  }
  if (DAT_febe631d != DAT_febe7c16) {
    DAT_febe7c12 = 'Z';
  }
  if (DAT_febe631e != DAT_febe7c17) {
    DAT_febe7c13 = 'Z';
  }
  if (DAT_febe631f != DAT_febe7c18) {
    DAT_febe7c14 = 'Z';
  }
  if (((((DAT_febe7c11 == 'Z') || (DAT_febe7c12 == 'Z')) || (DAT_febe7c13 == 'Z')) ||
      (DAT_febe7c14 == 'Z')) && (DAT_0002bac6 <= DAT_febe7db2)) {
    uVar1 = 0x22;
  }
  else {
    uVar1 = 0x11;
  }
  DAT_febe7c15 = DAT_febe631c;
  DAT_febe7c16 = DAT_febe631d;
  DAT_febe7c17 = DAT_febe631e;
  DAT_febe7c18 = DAT_febe631f;
  return uVar1;
}

void report_diagnostic_healthy_observed_155_4623e(void)

{
  report_diagnostic_healthy_observed(0x155);
  return;
}

void report_snapshot_monitor_0_events_and_latch_escalation_4624e(void)

{
  byte bVar1;
  short sVar2;
  uint32_t puVar3;
  sVar2 = DAT_febe71ec;
  puVar3 = 0xfebeb800u;
  bVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe7cacu + (uint32_t)(9) * 1u)))) |
          (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe7cacu + (uint32_t)(3) * 1u)))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe7cacu + (uint32_t)(1) * 1u))));
  if (DAT_febe7c11 == 'Z') {
    puVar3 = 0xfebeb800u;
    report_diagnostic_event_failure(0x151,10);
  }
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x3bee))))) == 'Z') {
    report_diagnostic_event_failure(0x152,10);
  }
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x3bed))))) == 'Z') {
    report_diagnostic_event_failure(0x153,10);
  }
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x3bec))))) == 'Z') {
    report_diagnostic_event_failure(0x154,10);
  }
  if ((((bVar1 & 0x22) == 0x22) || ((bVar1 & 0x44) == 0x44)) || (sVar2 != 0)) {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x3bf0))))) = 0x5a;
  }
  return;
}

void request_shared_monitor_escalation_status_a(void)

{
  byte bVar1;
  
  bVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe7cacu + (uint32_t)(3) * 1u)))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe7cacu + (uint32_t)(1) * 1u)))) |
          (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe7cacu + (uint32_t)(9) * 1u))));
  if ((((bVar1 & 0x22) == 0x22) || ((bVar1 & 0x44) == 0x44)) || (DAT_febe71ec != 0)) {
    DAT_febe7c10 = 0x5a;
  }
  return;
}

void run_init_chain_4630c(void)

{
  report_diagnostic_event_pass(0x151);
  report_diagnostic_event_pass(0x152);
  report_diagnostic_event_pass(0x153);
  report_diagnostic_event_pass(0x154);
  return;
}

void report_diagnostic_event_failure_155_10_46334(void)

{
  report_diagnostic_event_failure(0x155,10);
  return;
}

void reset_shared_snapshot_monitor_1_46346(void)

{
  clear_word_state_and_five_halfword_counters_6b98a(((undefined4 *)camry_host_ptr((uint32_t)((0xfebe7c1cu)))));
  return;
}

void reset_shared_snapshot_monitor_1_46356(void)

{
  clear_word_state_and_five_halfword_counters_6b98a(((undefined4 *)camry_host_ptr((uint32_t)((0xfebe7c1cu)))));
  return;
}

void update_and_publish_snapshot_monitor_1_46366(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  if (DAT_febe8a24 != 'Z') {
    return;
  }
  if (DAT_0002bc80 == 'Z') {
    clear_word_state_and_five_halfword_counters_6b98a(((undefined4 *)camry_host_ptr((uint32_t)((0xfebe7c1cu)))));
  }
  else {
    if ((DAT_febeeb85 == 'Z') && ((DAT_febe71ec >> 6 & 1) == 0)) {
      puVar1 = 0xfebeb800u;
      step_escalating_monitor
                (((F33EscalatingMonitorState *)camry_host_ptr((uint32_t)((0xfebe7c1cu)))), (ushort *)((undefined *)camry_host_ptr(0x2ba30u)), 
                 (uint *)&PTR_classify_snapshot_status_b_00028d34);
      if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x3bd4))))) == 'Z') {
        force_monitor_escalation
                  (((F33EscalatingMonitorState *)camry_host_ptr((uint32_t)((0xfebe7c1cu)))), (ushort *)((undefined *)camry_host_ptr(0x2ba30u)), 
                   (uint *)&PTR_classify_snapshot_status_b_00028d34);
      }
      goto LAB_000463e4;
    }
    retain_disabled_escalating_monitor(((F33EscalatingMonitorState *)camry_host_ptr((uint32_t)((0xfebe7c1cu)))), (ushort *)((undefined *)camry_host_ptr(0x2ba30u)));
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x3bd4))))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x3bd3))))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x3bd2))))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x3bd1))))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x3bd0))))) = 0;
LAB_000463e4:
  publish_shared_snapshot_monitor_status(1,(*((uint *)camry_host_ptr((uint32_t)(puVar1 + -0x3be4)))));
  return;
}

uint classify_snapshot_status_b(void)

{
  uint uVar1;
  
  DAT_febe7c2d = '\0';
  DAT_febe7c2e = '\0';
  DAT_febe7c2f = '\0';
  DAT_febe7c30 = '\0';
  if (DAT_febe6334 != DAT_febe7c31) {
    DAT_febe7c2d = 'Z';
  }
  if (DAT_febe6335 != DAT_febe7c32) {
    DAT_febe7c2e = 'Z';
  }
  if (DAT_febe6336 != DAT_febe7c33) {
    DAT_febe7c2f = 'Z';
  }
  if (DAT_febe6337 != DAT_febe7c34) {
    DAT_febe7c30 = 'Z';
  }
  if (((((DAT_febe7c2d == 'Z') || (DAT_febe7c2e == 'Z')) || (DAT_febe7c2f == 'Z')) ||
      (DAT_febe7c30 == 'Z')) && (DAT_0002baca <= DAT_febe7db2)) {
    uVar1 = 0x22;
  }
  else if ((DAT_febe7b48 == 'Z') && (DAT_febe7b49 == 'Z')) {
    uVar1 = 0x11;
  }
  else {
    uVar1 = 0x33;
  }
  DAT_febe7c31 = DAT_febe6334;
  DAT_febe7c32 = DAT_febe6335;
  DAT_febe7c33 = DAT_febe6336;
  DAT_febe7c34 = DAT_febe6337;
  return uVar1;
}

uint classify_snapshot_status_recovery_b(void)

{
  uint uVar1;
  
  DAT_febe7c2d = '\0';
  DAT_febe7c2e = '\0';
  DAT_febe7c2f = '\0';
  DAT_febe7c30 = '\0';
  if (DAT_febe6334 != DAT_febe7c31) {
    DAT_febe7c2d = 'Z';
  }
  if (DAT_febe6335 != DAT_febe7c32) {
    DAT_febe7c2e = 'Z';
  }
  if (DAT_febe6336 != DAT_febe7c33) {
    DAT_febe7c2f = 'Z';
  }
  if (DAT_febe6337 != DAT_febe7c34) {
    DAT_febe7c30 = 'Z';
  }
  if (((((DAT_febe7c2d == 'Z') || (DAT_febe7c2e == 'Z')) || (DAT_febe7c2f == 'Z')) ||
      (DAT_febe7c30 == 'Z')) && (DAT_0002baca <= DAT_febe7db2)) {
    uVar1 = 0x22;
  }
  else {
    uVar1 = 0x11;
  }
  DAT_febe7c31 = DAT_febe6334;
  DAT_febe7c32 = DAT_febe6335;
  DAT_febe7c33 = DAT_febe6336;
  DAT_febe7c34 = DAT_febe6337;
  return uVar1;
}

void report_diagnostic_healthy_observed_15a_46514(void)

{
  report_diagnostic_healthy_observed(0x15a);
  return;
}

void report_snapshot_monitor_1_events_and_latch_escalation_46524(void)

{
  byte bVar1;
  short sVar2;
  uint32_t puVar3;
  sVar2 = DAT_febe71ec;
  puVar3 = 0xfebeb800u;
  bVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe7cacu + (uint32_t)(8) * 1u)))) |
          (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe7cacu + (uint32_t)(2) * 1u)))) | ((volatile uint8_t *)camry_host_ptr(0xfebe7cacu))[0];
  if (DAT_febe7c2d == 'Z') {
    puVar3 = 0xfebeb800u;
    report_diagnostic_event_failure(0x156,10);
  }
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x3bd2))))) == 'Z') {
    report_diagnostic_event_failure(0x157,10);
  }
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x3bd1))))) == 'Z') {
    report_diagnostic_event_failure(0x158,10);
  }
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x3bd0))))) == 'Z') {
    report_diagnostic_event_failure(0x159,10);
  }
  if ((((bVar1 & 0x22) == 0x22) || ((bVar1 & 0x44) == 0x44)) || (sVar2 != 0)) {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x3bd4))))) = 0x5a;
  }
  return;
}

void request_shared_monitor_escalation_status_b(void)

{
  byte bVar1;
  
  bVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe7cacu + (uint32_t)(2) * 1u)))) | ((volatile uint8_t *)camry_host_ptr(0xfebe7cacu))[0] |
          (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe7cacu + (uint32_t)(8) * 1u))));
  if ((((bVar1 & 0x22) == 0x22) || ((bVar1 & 0x44) == 0x44)) || (DAT_febe71ec != 0)) {
    DAT_febe7c2c = 0x5a;
  }
  return;
}

void run_init_chain_465e2(void)

{
  report_diagnostic_event_pass(0x156);
  report_diagnostic_event_pass(0x157);
  report_diagnostic_event_pass(0x158);
  report_diagnostic_event_pass(0x159);
  return;
}

void report_diagnostic_event_failure_15a_10_4660a(void)

{
  report_diagnostic_event_failure(0x15a,10);
  return;
}

void return_only_stub_4661c(void)

{
  return;
}

void seed_snapshot_a_modulo_four_sequence_4661e(void)

{
  DAT_febe7c4e = (byte)DAT_febe81ee & 3;
  if (DAT_febe8a1c == 'Z') {
    DAT_febe7c4e = DAT_febe7c4e - 1 & 3;
  }
  return;
}

void count_snapshot_a_flag_sequence_and_pair_range_failures_4663c(void)

{
  int iVar1;
  uint uVar2;
  uint uVar3;
  uint uVar4;
  
  if (DAT_febe8a1c == 'Z') {
    uVar4 = (uint)DAT_febe81e6;
    uVar3 = (uint)DAT_febe81e8;
    if ((DAT_febe81e0 == 'Z') &&
       (DAT_febe7c38 = DAT_febe7c38 + 1,
       -1 < (int)((uint)DAT_febe7c38 - (uint)DAT_febe7c43) &&
       (uint)DAT_febe7c38 != (uint)DAT_febe7c43)) {
      DAT_febe7c43 = DAT_febe7c38;
    }
    if ((DAT_febe81e1 == 'Z') &&
       (DAT_febe7c39 = DAT_febe7c39 + 1,
       -1 < (int)((uint)DAT_febe7c39 - (uint)DAT_febe7c44) &&
       (uint)DAT_febe7c39 != (uint)DAT_febe7c44)) {
      DAT_febe7c44 = DAT_febe7c39;
    }
    if ((DAT_febe81e2 == 'Z') &&
       (DAT_febe7c3a = DAT_febe7c3a + 1,
       -1 < (int)((uint)DAT_febe7c3a - (uint)DAT_febe7c45) &&
       (uint)DAT_febe7c3a != (uint)DAT_febe7c45)) {
      DAT_febe7c45 = DAT_febe7c3a;
    }
    if (((DAT_febe81ee & 3) != (DAT_febe7c4e + 1 & 3)) &&
       (DAT_febe7c3b = DAT_febe7c3b + 1,
       -1 < (int)((uint)DAT_febe7c3b - (uint)DAT_febe7c46) &&
       (uint)DAT_febe7c3b != (uint)DAT_febe7c46)) {
      DAT_febe7c46 = DAT_febe7c3b;
    }
    if (((DAT_febe81ee >> 2 & 1) != 0) &&
       (DAT_febe7c3c = DAT_febe7c3c + 1,
       -1 < (int)((uint)DAT_febe7c3c - (uint)DAT_febe7c47) &&
       (uint)DAT_febe7c3c != (uint)DAT_febe7c47)) {
      DAT_febe7c47 = DAT_febe7c3c;
    }
    if (((DAT_febe81ee >> 3 & 1) != 0) &&
       (DAT_febe7c3d = DAT_febe7c3d + 1,
       -1 < (int)((uint)DAT_febe7c3d - (uint)DAT_febe7c48) &&
       (uint)DAT_febe7c3d != (uint)DAT_febe7c48)) {
      DAT_febe7c48 = DAT_febe7c3d;
    }
    if ((DAT_0002bace < uVar4) &&
       (DAT_febe7c3e = DAT_febe7c3e + 1,
       -1 < (int)((uint)DAT_febe7c3e - (uint)DAT_febe7c49) &&
       (uint)DAT_febe7c3e != (uint)DAT_febe7c49)) {
      DAT_febe7c49 = DAT_febe7c3e;
    }
    if ((DAT_0002bace < uVar3) &&
       (DAT_febe7c3f = DAT_febe7c3f + 1,
       -1 < (int)((uint)DAT_febe7c3f - (uint)DAT_febe7c4a) &&
       (uint)DAT_febe7c3f != (uint)DAT_febe7c4a)) {
      DAT_febe7c4a = DAT_febe7c3f;
    }
    if ((uVar4 < DAT_0002bad0) &&
       (DAT_febe7c40 = DAT_febe7c40 + 1,
       -1 < (int)((uint)DAT_febe7c40 - (uint)DAT_febe7c4b) &&
       (uint)DAT_febe7c40 != (uint)DAT_febe7c4b)) {
      DAT_febe7c4b = DAT_febe7c40;
    }
    if ((uVar3 < DAT_0002bad0) &&
       (DAT_febe7c41 = DAT_febe7c41 + 1,
       -1 < (int)((uint)DAT_febe7c41 - (uint)DAT_febe7c4c) &&
       (uint)DAT_febe7c41 != (uint)DAT_febe7c4c)) {
      DAT_febe7c4c = DAT_febe7c41;
    }
    uVar2 = (uVar3 + uVar4) - 0x1000;
    iVar1 = uVar3 + uVar4 + 0x7fffefff;
    if (iVar1 < 0 == (-1 < (int)uVar2 && iVar1 < 0) && uVar2 != 0x80000001) {
      if ((int)uVar2 < 0) {
        uVar2 = -uVar2;
      }
    }
    else {
      uVar2 = 0x7fffffff;
    }
    iVar1 = uVar2 - DAT_0002bad2;
    if ((iVar1 < 0 == ((int)uVar2 < 0 && -1 < iVar1) && uVar2 != DAT_0002bad2) &&
       (DAT_febe7c42 = DAT_febe7c42 + 1,
       -1 < (int)((uint)DAT_febe7c42 - (uint)DAT_febe7c4d) &&
       (uint)DAT_febe7c42 != (uint)DAT_febe7c4d)) {
      DAT_febe7c4d = DAT_febe7c42;
    }
    DAT_febe7c4e = (byte)(DAT_febe81ee & 3);
  }
  return;
}

void return_only_stub_467ce(void)

{
  return;
}

void seed_snapshot_b_modulo_four_sequence_467d0(void)

{
  DAT_febe7c66 = (byte)DAT_febe81f0 & 3;
  if (DAT_febe8a1c == 'Z') {
    DAT_febe7c66 = DAT_febe7c66 - 1 & 3;
  }
  return;
}

void count_snapshot_b_flag_sequence_and_pair_range_failures_467ee(void)

{
  int iVar1;
  uint uVar2;
  uint uVar3;
  uint uVar4;
  
  if (DAT_febe8a1c == 'Z') {
    uVar4 = (uint)DAT_febe81ea;
    uVar3 = (uint)DAT_febe81ec;
    if ((DAT_febe81e3 == 'Z') &&
       (DAT_febe7c50 = DAT_febe7c50 + 1,
       -1 < (int)((uint)DAT_febe7c50 - (uint)DAT_febe7c5b) &&
       (uint)DAT_febe7c50 != (uint)DAT_febe7c5b)) {
      DAT_febe7c5b = DAT_febe7c50;
    }
    if ((DAT_febe81e4 == 'Z') &&
       (DAT_febe7c51 = DAT_febe7c51 + 1,
       -1 < (int)((uint)DAT_febe7c51 - (uint)DAT_febe7c5c) &&
       (uint)DAT_febe7c51 != (uint)DAT_febe7c5c)) {
      DAT_febe7c5c = DAT_febe7c51;
    }
    if ((DAT_febe81e5 == 'Z') &&
       (DAT_febe7c52 = DAT_febe7c52 + 1,
       -1 < (int)((uint)DAT_febe7c52 - (uint)DAT_febe7c5d) &&
       (uint)DAT_febe7c52 != (uint)DAT_febe7c5d)) {
      DAT_febe7c5d = DAT_febe7c52;
    }
    if (((DAT_febe81f0 & 3) != (DAT_febe7c66 + 1 & 3)) &&
       (DAT_febe7c53 = DAT_febe7c53 + 1,
       -1 < (int)((uint)DAT_febe7c53 - (uint)DAT_febe7c5e) &&
       (uint)DAT_febe7c53 != (uint)DAT_febe7c5e)) {
      DAT_febe7c5e = DAT_febe7c53;
    }
    if (((DAT_febe81f0 >> 2 & 1) != 0) &&
       (DAT_febe7c54 = DAT_febe7c54 + 1,
       -1 < (int)((uint)DAT_febe7c54 - (uint)DAT_febe7c5f) &&
       (uint)DAT_febe7c54 != (uint)DAT_febe7c5f)) {
      DAT_febe7c5f = DAT_febe7c54;
    }
    if (((DAT_febe81f0 >> 3 & 1) != 0) &&
       (DAT_febe7c55 = DAT_febe7c55 + 1,
       -1 < (int)((uint)DAT_febe7c55 - (uint)DAT_febe7c60) &&
       (uint)DAT_febe7c55 != (uint)DAT_febe7c60)) {
      DAT_febe7c60 = DAT_febe7c55;
    }
    if ((DAT_0002bad6 < uVar4) &&
       (DAT_febe7c56 = DAT_febe7c56 + 1,
       -1 < (int)((uint)DAT_febe7c56 - (uint)DAT_febe7c61) &&
       (uint)DAT_febe7c56 != (uint)DAT_febe7c61)) {
      DAT_febe7c61 = DAT_febe7c56;
    }
    if ((DAT_0002bad6 < uVar3) &&
       (DAT_febe7c57 = DAT_febe7c57 + 1,
       -1 < (int)((uint)DAT_febe7c57 - (uint)DAT_febe7c62) &&
       (uint)DAT_febe7c57 != (uint)DAT_febe7c62)) {
      DAT_febe7c62 = DAT_febe7c57;
    }
    if ((uVar4 < DAT_0002bad8) &&
       (DAT_febe7c58 = DAT_febe7c58 + 1,
       -1 < (int)((uint)DAT_febe7c58 - (uint)DAT_febe7c63) &&
       (uint)DAT_febe7c58 != (uint)DAT_febe7c63)) {
      DAT_febe7c63 = DAT_febe7c58;
    }
    if ((uVar3 < DAT_0002bad8) &&
       (DAT_febe7c59 = DAT_febe7c59 + 1,
       -1 < (int)((uint)DAT_febe7c59 - (uint)DAT_febe7c64) &&
       (uint)DAT_febe7c59 != (uint)DAT_febe7c64)) {
      DAT_febe7c64 = DAT_febe7c59;
    }
    uVar2 = (uVar3 + uVar4) - 0x1000;
    iVar1 = uVar3 + uVar4 + 0x7fffefff;
    if (iVar1 < 0 == (-1 < (int)uVar2 && iVar1 < 0) && uVar2 != 0x80000001) {
      if ((int)uVar2 < 0) {
        uVar2 = -uVar2;
      }
    }
    else {
      uVar2 = 0x7fffffff;
    }
    iVar1 = uVar2 - DAT_0002bada;
    if ((iVar1 < 0 == ((int)uVar2 < 0 && -1 < iVar1) && uVar2 != DAT_0002bada) &&
       (DAT_febe7c5a = DAT_febe7c5a + 1,
       -1 < (int)((uint)DAT_febe7c5a - (uint)DAT_febe7c65) &&
       (uint)DAT_febe7c5a != (uint)DAT_febe7c65)) {
      DAT_febe7c65 = DAT_febe7c5a;
    }
    DAT_febe7c66 = (byte)(DAT_febe81f0 & 3);
  }
  return;
}

void return_only_stub_46980(void)

{
  return;
}

void clear_decoded_torque_history_46982(void)

{
  DAT_febe686c = 0;
  DAT_febe6870 = 0;
  DAT_febe6874 = 0;
  DAT_febe6872 = 0;
  return;
}

uint select_clamp_and_publish_decoded_torque_history_46994(void)

{
  short sVar1;
  char cVar2;
  short sVar3;
  short sVar4;
  char cVar5;
  uint32_t puVar6;
  short sVar7;
  uint saved_mask;
  short sVar8;
  char cVar9;
  
  cVar5 = DAT_febe7cb7;
  sVar4 = ((int)(int16_t)DAT_febe6874);
  sVar3 = ((int)(int16_t)DAT_febe6872);
  cVar2 = DAT_febe686e;
  cVar9 = DAT_febe686c;
  sVar1 = ((int)(int16_t)DAT_febe62ac);
  puVar6 = 0xfebeb800u;
  sVar8 = ((int)(int16_t)DAT_febe6870);
  if (DAT_febe686d == '\0') {
    if (DAT_febe8a24 == 'Z') {
      if (DAT_febe7cb7 == '\x02') {
        sVar8 = ((int)(int16_t)DAT_febe62b6) << 1;
      }
      else {
        sVar8 = ((int)(int16_t)DAT_febe62ba);
        if (DAT_febe7cb7 == '\x01') {
          sVar8 = ((int)(int16_t)DAT_febe62b8) * -2;
        }
      }
      puVar6 = 0xfebeb800u;
      sVar7 = clamp_decoded_torque(sVar8);
      sVar8 = sVar7;
      DAT_febe6874 = sVar7;
      DAT_febe6872 = sVar7;
      if (((cVar9 != 'Z') &&
          (sVar8 = sVar4, DAT_febe6874 = sVar3, DAT_febe6872 = sVar1, cVar2 == '\0')) &&
         (DAT_febe6872 = sVar7, cVar5 == '\0')) {
        DAT_febe6872 = sVar1;
      }
      cVar9 = '\0';
    }
  }
  else {
    cVar9 = 'Z';
  }
  (*((char *)camry_host_ptr((uint32_t)((int)(0xffffb06eu + (uint32_t)((int)puVar6)))))) = cVar5;
  saved_mask = priority_mask_enter(0xffc0);
  DAT_febe686c = cVar9;
  DAT_febe6870 = sVar8;
  priority_mask_restore(saved_mask);
  return saved_mask;
}

void set_decoded_torque_override_byte_46a2c(undefined1 param_1)

{
  DAT_febe686d = param_1;
  return;
}

void reset_recoverable_monitor_febe7c68(void)

{
  reset_recoverable_monitor((F33RecoverableMonitorState *)((undefined *)camry_host_ptr(0xfebe7c68u)));
  return;
}

void reset_recoverable_monitor_febe7c68_46a42(void)

{
  reset_recoverable_monitor((F33RecoverableMonitorState *)((undefined *)camry_host_ptr(0xfebe7c68u)));
  return;
}

void update_and_publish_selected_source_recoverable_monitor_46a52(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  if (DAT_febe8a24 == 'Z') {
    if (DAT_0002bc84 == 'Z') {
      reset_recoverable_monitor((F33RecoverableMonitorState *)((undefined *)camry_host_ptr(0xfebe7c68u)));
    }
    else if (DAT_febeeb85 == 'Z') {
      step_recoverable_monitor
                ((F33RecoverableMonitorState *)((undefined *)camry_host_ptr(0xfebe7c68u)),
                 (F33RecoverableMonitorLimits *)&PTR_LAB_0002ba40,
                 (F33RecoverableMonitorCallbacks *)&PTR_classify_selected_source_hold_00028d78);
    }
    else {
      retain_disabled_recoverable_monitor
                ((F33RecoverableMonitorState *)((undefined *)camry_host_ptr(0xfebe7c68u)),
                 (F33RecoverableMonitorLimits *)&PTR_LAB_0002ba40);
    }
    publish_shared_snapshot_monitor_status(10,(*((uint *)camry_host_ptr((uint32_t)(puVar1 + -0x3b98)))));
  }
  return;
}

uint classify_selected_source_hold(void)

{
  if ((DAT_febe686c == 'Z') && (DAT_febe7cb8 == 'Z')) {
    return 0x22;
  }
  return 0x11;
}

uint classify_selected_source_hold_recovery(void)

{
  if (DAT_febe686c == 'Z') {
    return 0x22;
  }
  return 0x11;
}

void report_diagnostic_event_failure_50_10_46adc(void)

{
  report_diagnostic_event_failure(0x50,10);
  return;
}

void report_diagnostic_event_pass_50_46aee(void)

{
  report_diagnostic_event_pass(0x50);
  return;
}

void reset_shared_snapshot_monitor_2_46afe(void)

{
  clear_word_state_and_five_halfword_counters_6b98a(((undefined4 *)camry_host_ptr((uint32_t)((0xfebe7c74u)))));
  return;
}

void reset_shared_snapshot_monitor_2_46b0e(void)

{
  clear_word_state_and_five_halfword_counters_6b98a(((undefined4 *)camry_host_ptr((uint32_t)((0xfebe7c74u)))));
  return;
}

void update_and_publish_snapshot_monitor_2_46b1e(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  if (DAT_febe8a24 != 'Z') {
    return;
  }
  if (DAT_0002bc88 == 'Z') {
    clear_word_state_and_five_halfword_counters_6b98a(((undefined4 *)camry_host_ptr((uint32_t)((0xfebe7c74u)))));
  }
  else {
    if ((DAT_febeeb85 == 'Z') && ((DAT_febe71ec >> 5 & 1) == 0)) {
      puVar1 = 0xfebeb800u;
      step_escalating_monitor
                (((F33EscalatingMonitorState *)camry_host_ptr((uint32_t)((0xfebe7c74u)))), (ushort *)((undefined *)camry_host_ptr(0x2ba46u)), (uint *)&PTR_FUN_00028db4);
      if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x3b7c))))) == 'Z') {
        force_monitor_escalation
                  (((F33EscalatingMonitorState *)camry_host_ptr((uint32_t)((0xfebe7c74u)))), (ushort *)((undefined *)camry_host_ptr(0x2ba46u)), (uint *)&PTR_FUN_00028db4)
        ;
      }
      goto LAB_00046b9e;
    }
    retain_disabled_escalating_monitor(((F33EscalatingMonitorState *)camry_host_ptr((uint32_t)((0xfebe7c74u)))), (ushort *)((undefined *)camry_host_ptr(0x2ba46u)));
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x3b7c))))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x3b7b))))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x3b7a))))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x3b79))))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x3b78))))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x3b77))))) = 0;
LAB_00046b9e:
  publish_shared_snapshot_monitor_status(2,(*((uint *)camry_host_ptr((uint32_t)(puVar1 + -0x3b8c)))));
  return;
}

undefined4 classify_and_snapshot_five_bytes_at_6322_46bac(void)

{
  undefined4 uVar1;
  
  DAT_febe7c85 = '\0';
  DAT_febe7c86 = '\0';
  DAT_febe7c87 = '\0';
  DAT_febe7c88 = '\0';
  DAT_febe7c89 = '\0';
  if (DAT_febe6322 != DAT_febe7c8a) {
    DAT_febe7c85 = 'Z';
  }
  if (DAT_febe6323 != DAT_febe7c8b) {
    DAT_febe7c86 = 'Z';
  }
  if (DAT_febe6324 != DAT_febe7c8c) {
    DAT_febe7c87 = 'Z';
  }
  if (DAT_febe6325 != DAT_febe7c8d) {
    DAT_febe7c88 = 'Z';
  }
  if (DAT_febe6326 != DAT_febe7c8e) {
    DAT_febe7c89 = 'Z';
  }
  if ((((DAT_febe7c85 == 'Z') || (DAT_febe7c86 == 'Z')) || (DAT_febe7c87 == 'Z')) ||
     ((DAT_febe7c88 == 'Z' || (DAT_febe7c89 == 'Z')))) {
    uVar1 = 0x22;
  }
  else if ((DAT_febe7b48 == 'Z') && (DAT_febe7b49 == 'Z')) {
    uVar1 = 0x11;
  }
  else {
    uVar1 = 0x33;
  }
  DAT_febe7c8a = DAT_febe6322;
  DAT_febe7c8b = DAT_febe6323;
  DAT_febe7c8c = DAT_febe6324;
  DAT_febe7c8d = DAT_febe6325;
  DAT_febe7c8e = DAT_febe6326;
  return uVar1;
}

uint classify_snapshot_sample_bounds_recovery_a(void)

{
  uint uVar1;
  
  DAT_febe7c85 = '\0';
  DAT_febe7c86 = '\0';
  DAT_febe7c87 = '\0';
  DAT_febe7c88 = '\0';
  DAT_febe7c89 = '\0';
  if (DAT_febe6322 != DAT_febe7c8a) {
    DAT_febe7c85 = 'Z';
  }
  if (DAT_febe6323 != DAT_febe7c8b) {
    DAT_febe7c86 = 'Z';
  }
  if (DAT_febe6324 != DAT_febe7c8c) {
    DAT_febe7c87 = 'Z';
  }
  if (DAT_febe6325 != DAT_febe7c8d) {
    DAT_febe7c88 = 'Z';
  }
  if (DAT_febe6326 != DAT_febe7c8e) {
    DAT_febe7c89 = 'Z';
  }
  if ((((DAT_febe7c85 == 'Z') || (DAT_febe7c86 == 'Z')) || (DAT_febe7c87 == 'Z')) ||
     ((DAT_febe7c88 == 'Z' || (DAT_febe7c89 == 'Z')))) {
    uVar1 = 0x22;
  }
  else {
    uVar1 = 0x11;
  }
  DAT_febe7c8a = DAT_febe6322;
  DAT_febe7c8b = DAT_febe6323;
  DAT_febe7c8c = DAT_febe6324;
  DAT_febe7c8d = DAT_febe6325;
  DAT_febe7c8e = DAT_febe6326;
  return uVar1;
}

void report_diagnostic_healthy_observed_160_46ce4(void)

{
  report_diagnostic_healthy_observed(0x160);
  return;
}

void report_snapshot_monitor_2_events_and_latch_escalation_46cf4(void)

{
  byte bVar1;
  short sVar2;
  uint32_t puVar3;
  sVar2 = DAT_febe71ec;
  puVar3 = 0xfebeb800u;
  bVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe7cacu + (uint32_t)(9) * 1u)))) |
          (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe7cacu + (uint32_t)(3) * 1u)))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe7cacu + (uint32_t)(1) * 1u))));
  if (DAT_febe7c85 == 'Z') {
    puVar3 = 0xfebeb800u;
    report_diagnostic_event_failure(0x15b,10);
  }
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x3b7a))))) == 'Z') {
    report_diagnostic_event_failure(0x15c,10);
  }
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x3b79))))) == 'Z') {
    report_diagnostic_event_failure(0x15d,10);
  }
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x3b78))))) == 'Z') {
    report_diagnostic_event_failure(0x15e,10);
  }
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x3b77))))) == 'Z') {
    report_diagnostic_event_failure(0x15f,10);
  }
  if ((((bVar1 & 0x22) == 0x22) || ((bVar1 & 0x44) == 0x44)) || (sVar2 != 0)) {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x3b7c))))) = 0x5a;
  }
  return;
}

void request_shared_monitor_escalation_sample_bounds_a(void)

{
  byte bVar1;
  
  bVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe7cacu + (uint32_t)(3) * 1u)))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe7cacu + (uint32_t)(1) * 1u)))) |
          (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe7cacu + (uint32_t)(9) * 1u))));
  if ((((bVar1 & 0x22) == 0x22) || ((bVar1 & 0x44) == 0x44)) || (DAT_febe71ec != 0)) {
    DAT_febe7c84 = 0x5a;
  }
  return;
}

void run_init_chain_46dc6(void)

{
  report_diagnostic_event_pass(0x15b);
  report_diagnostic_event_pass(0x15c);
  report_diagnostic_event_pass(0x15d);
  report_diagnostic_event_pass(0x15e);
  report_diagnostic_event_pass(0x15f);
  return;
}

void report_diagnostic_event_failure_160_10_46df6(void)

{
  report_diagnostic_event_failure(0x160,10);
  return;
}

void reset_shared_snapshot_monitor_3_46e08(void)

{
  clear_word_state_and_five_halfword_counters_6b98a(((undefined4 *)camry_host_ptr((uint32_t)((0xfebe7c90u)))));
  return;
}

void reset_shared_snapshot_monitor_3_46e18(void)

{
  clear_word_state_and_five_halfword_counters_6b98a(((undefined4 *)camry_host_ptr((uint32_t)((0xfebe7c90u)))));
  return;
}

void update_and_publish_snapshot_monitor_3_46e28(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  if (DAT_febe8a24 != 'Z') {
    return;
  }
  if (DAT_0002bc8c == 'Z') {
    clear_word_state_and_five_halfword_counters_6b98a(((undefined4 *)camry_host_ptr((uint32_t)((0xfebe7c90u)))));
  }
  else {
    if ((DAT_febeeb85 == 'Z') && ((DAT_febe71ec >> 6 & 1) == 0)) {
      puVar1 = 0xfebeb800u;
      step_escalating_monitor
                (((F33EscalatingMonitorState *)camry_host_ptr((uint32_t)((0xfebe7c90u)))), (ushort *)((undefined *)camry_host_ptr(0x2ba56u)), (uint *)&PTR_FUN_00028df8);
      if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x3b60))))) == 'Z') {
        force_monitor_escalation
                  (((F33EscalatingMonitorState *)camry_host_ptr((uint32_t)((0xfebe7c90u)))), (ushort *)((undefined *)camry_host_ptr(0x2ba56u)), (uint *)&PTR_FUN_00028df8)
        ;
      }
      goto LAB_00046ea8;
    }
    retain_disabled_escalating_monitor(((F33EscalatingMonitorState *)camry_host_ptr((uint32_t)((0xfebe7c90u)))), (ushort *)((undefined *)camry_host_ptr(0x2ba56u)));
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x3b60))))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x3b5f))))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x3b5e))))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x3b5d))))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x3b5c))))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x3b5b))))) = 0;
LAB_00046ea8:
  publish_shared_snapshot_monitor_status(3,(*((uint *)camry_host_ptr((uint32_t)(puVar1 + -0x3b70)))));
  return;
}

undefined4 classify_and_snapshot_five_bytes_at_633a_46eb6(void)

{
  undefined4 uVar1;
  
  DAT_febe7ca1 = '\0';
  DAT_febe7ca2 = '\0';
  DAT_febe7ca3 = '\0';
  DAT_febe7ca4 = '\0';
  DAT_febe7ca5 = '\0';
  if (DAT_febe633a != DAT_febe7ca6) {
    DAT_febe7ca1 = 'Z';
  }
  if (DAT_febe633b != DAT_febe7ca7) {
    DAT_febe7ca2 = 'Z';
  }
  if (DAT_febe633c != DAT_febe7ca8) {
    DAT_febe7ca3 = 'Z';
  }
  if (DAT_febe633d != DAT_febe7ca9) {
    DAT_febe7ca4 = 'Z';
  }
  if (DAT_febe633e != DAT_febe7caa) {
    DAT_febe7ca5 = 'Z';
  }
  if ((((DAT_febe7ca1 == 'Z') || (DAT_febe7ca2 == 'Z')) || (DAT_febe7ca3 == 'Z')) ||
     ((DAT_febe7ca4 == 'Z' || (DAT_febe7ca5 == 'Z')))) {
    uVar1 = 0x22;
  }
  else if ((DAT_febe7b48 == 'Z') && (DAT_febe7b49 == 'Z')) {
    uVar1 = 0x11;
  }
  else {
    uVar1 = 0x33;
  }
  DAT_febe7ca6 = DAT_febe633a;
  DAT_febe7ca7 = DAT_febe633b;
  DAT_febe7ca8 = DAT_febe633c;
  DAT_febe7ca9 = DAT_febe633d;
  DAT_febe7caa = DAT_febe633e;
  return uVar1;
}

uint classify_snapshot_sample_bounds_recovery_b(void)

{
  uint uVar1;
  
  DAT_febe7ca1 = '\0';
  DAT_febe7ca2 = '\0';
  DAT_febe7ca3 = '\0';
  DAT_febe7ca4 = '\0';
  DAT_febe7ca5 = '\0';
  if (DAT_febe633a != DAT_febe7ca6) {
    DAT_febe7ca1 = 'Z';
  }
  if (DAT_febe633b != DAT_febe7ca7) {
    DAT_febe7ca2 = 'Z';
  }
  if (DAT_febe633c != DAT_febe7ca8) {
    DAT_febe7ca3 = 'Z';
  }
  if (DAT_febe633d != DAT_febe7ca9) {
    DAT_febe7ca4 = 'Z';
  }
  if (DAT_febe633e != DAT_febe7caa) {
    DAT_febe7ca5 = 'Z';
  }
  if ((((DAT_febe7ca1 == 'Z') || (DAT_febe7ca2 == 'Z')) || (DAT_febe7ca3 == 'Z')) ||
     ((DAT_febe7ca4 == 'Z' || (DAT_febe7ca5 == 'Z')))) {
    uVar1 = 0x22;
  }
  else {
    uVar1 = 0x11;
  }
  DAT_febe7ca6 = DAT_febe633a;
  DAT_febe7ca7 = DAT_febe633b;
  DAT_febe7ca8 = DAT_febe633c;
  DAT_febe7ca9 = DAT_febe633d;
  DAT_febe7caa = DAT_febe633e;
  return uVar1;
}

void report_diagnostic_healthy_observed_166_46fee(void)

{
  report_diagnostic_healthy_observed(0x166);
  return;
}

void report_snapshot_monitor_3_events_and_latch_escalation_46ffe(void)

{
  byte bVar1;
  short sVar2;
  uint32_t puVar3;
  sVar2 = DAT_febe71ec;
  puVar3 = 0xfebeb800u;
  bVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe7cacu + (uint32_t)(8) * 1u)))) |
          (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe7cacu + (uint32_t)(2) * 1u)))) | ((volatile uint8_t *)camry_host_ptr(0xfebe7cacu))[0];
  if (DAT_febe7ca1 == 'Z') {
    puVar3 = 0xfebeb800u;
    report_diagnostic_event_failure(0x161,10);
  }
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x3b5e))))) == 'Z') {
    report_diagnostic_event_failure(0x162,10);
  }
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x3b5d))))) == 'Z') {
    report_diagnostic_event_failure(0x163,10);
  }
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x3b5c))))) == 'Z') {
    report_diagnostic_event_failure(0x164,10);
  }
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x3b5b))))) == 'Z') {
    report_diagnostic_event_failure(0x165,10);
  }
  if ((((bVar1 & 0x22) == 0x22) || ((bVar1 & 0x44) == 0x44)) || (sVar2 != 0)) {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x3b60))))) = 0x5a;
  }
  return;
}
