#include "common.h"

void update_inverse_gate_shared_monitor_eight_4400a(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  if (DAT_0002bc20 == 'Z') {
    reset_latched_monitor((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe797cu)));
  }
  else if (((DAT_febe71ec & 1) == 0) || (DAT_febeeb85 != 'Z')) {
    report_diagnostic_healthy_observed(0xe3);
  }
  else {
    step_latched_monitor
              ((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe797cu)),(F33MonitorLimits *)((undefined *)camry_host_ptr(0x2b8c8u)),
               (F33TwoSidedMonitorCallbacks *)&PTR_classify_inverse_gate_b_00028824);
  }
  publish_shared_condition_monitor_status(8,(*((uint *)camry_host_ptr((uint32_t)(puVar1 + -0x3e84)))));
  return;
}

uint classify_inverse_gate_b(void)

{
  if ((DAT_0002b8ee < DAT_febe7da8) && (DAT_febe7db0 <= DAT_0002b8ec)) {
    return 0x22;
  }
  return 0x11;
}

void report_diagnostic_event_failure_e3_10_4408a(void)

{
  report_diagnostic_event_failure(0xe3,10);
  return;
}

void reset_latched_monitor_febe7988(void)

{
  reset_latched_monitor((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe7988u)));
  return;
}

void reset_latched_monitor_febe7988_440ac(void)

{
  reset_latched_monitor((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe7988u)));
  return;
}

void update_a_shared_sample_window_latched_monitor_440bc(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  if (DAT_0002bc24 == 'Z') {
    reset_latched_monitor((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe7988u)));
  }
  else if (((DAT_febe71ec & 1) == 0) && (DAT_febeeb85 == 'Z')) {
    step_latched_monitor
              ((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe7988u)),(F33MonitorLimits *)((undefined *)camry_host_ptr(0x2b8ccu)),
               (F33TwoSidedMonitorCallbacks *)&PTR_FUN_00028858);
  }
  else {
    retain_disabled_latched_monitor
              ((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe7988u)),(F33MonitorLimits *)((undefined *)camry_host_ptr(0x2b8ccu)));
  }
  publish_shared_condition_monitor_status(3,(*((uint *)camry_host_ptr((uint32_t)(puVar1 + -0x3e78)))));
  return;
}

undefined4 test_a_flag_selected_sample_window_44116(void)

{
  if (((((DAT_febe7bba != '\0') || (DAT_febeeb86 != '\0')) || (DAT_febeeb80 != 'Z')) ||
      ((((DAT_febeeb88 != '\0' || (DAT_0002b8f0 <= DAT_febe7da6)) || (DAT_febe7db0 < DAT_0002b8f2))
       && (((DAT_febeeb88 != 'Z' || (DAT_0002b8f4 <= DAT_febe7da6)) || (DAT_febe7db0 < DAT_0002b8f2)
           ))))) &&
     ((DAT_0002b8f6 <= DAT_febe7da6 ||
      (((DAT_febe7bba != 'Z' && (DAT_febeeb86 != 'Z')) && (((int8_t)DAT_febeeb80) != -0x5b)))))) {
    return 0;
  }
  return 0x5a;
}

undefined4 classify_a_sample_window_and_monitor_flags_44184(void)

{
  char cVar1;
  char cVar2;
  char cVar3;
  char cVar4;
  char cVar5;
  char cVar6;
  char cVar7;
  char cVar8;
  char cVar9;
  char cVar10;
  uchar uVar11;
  uchar uVar12;
  char cVar13;
  ushort uVar14;
  ushort uVar15;
  char cVar16;
  char cVar17;
  char cVar18;
  int iVar19;
  undefined4 uVar20;
  
  cVar18 = DAT_febeeb88;
  cVar17 = DAT_febeeb86;
  cVar16 = DAT_febeeb80;
  uVar15 = DAT_febe7db0;
  uVar14 = DAT_febe7da6;
  cVar13 = DAT_febe7bba;
  uVar12 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe79dcu + (uint32_t)(1) * 1u))));
  uVar11 = ((volatile uint8_t *)camry_host_ptr(0xfebe79dcu))[0];
  cVar10 = DAT_febe7824;
  cVar9 = DAT_febe781e;
  cVar8 = DAT_febe781d;
  cVar7 = DAT_febe781c;
  cVar6 = DAT_febe781a;
  cVar5 = DAT_febe7819;
  cVar4 = DAT_febe7818;
  cVar3 = DAT_febe74ad;
  cVar2 = DAT_febe74ac;
  cVar1 = DAT_febe74aa;
  iVar19 = test_a_flag_selected_sample_window_44116();
  if (cVar3 == '\0' &&
      (cVar2 == '\0' &&
      (cVar1 == '\0' &&
      (uVar11 == '\0' &&
      (uVar12 == '\0' &&
      (cVar9 == '\0' &&
      (cVar8 == '\0' &&
      (cVar7 == '\0' && (cVar10 == '\0' && (cVar6 == '\0' && (cVar5 == '\0' && cVar4 == '\0'))))))))
      ))) {
    if (iVar19 == 0x5a) {
      uVar20 = 0x22;
    }
    else if ((((cVar13 == '\0') && (cVar17 == '\0')) && (cVar16 == 'Z')) &&
            (((cVar18 == '\0' && (DAT_0002b8f8 <= uVar14)) && (DAT_0002b8fa <= uVar15)))) {
      uVar20 = 0x11;
    }
    else {
      uVar20 = 0x33;
    }
  }
  else {
    uVar20 = 0x44;
  }
  return uVar20;
}

void report_diagnostic_healthy_observed_a4_4422a(void)

{
  report_diagnostic_healthy_observed(0xa4);
  return;
}

void report_diagnostic_event_failure_a4_10_4423a(void)

{
  report_diagnostic_event_failure(0xa4,10);
  return;
}

void reset_latched_monitor_febe7994(void)

{
  reset_latched_monitor((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe7994u)));
  return;
}

void reset_latched_monitor_febe7994_4425c(void)

{
  reset_latched_monitor((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe7994u)));
  return;
}

void update_b_shared_sample_window_latched_monitor_4426c(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  if (DAT_0002bc28 == 'Z') {
    reset_latched_monitor((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe7994u)));
  }
  else if (((DAT_febe71ec >> 1 & 1) == 0) && (DAT_febeeb85 == 'Z')) {
    step_latched_monitor
              ((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe7994u)),(F33MonitorLimits *)((undefined *)camry_host_ptr(0x2b8d0u)),
               (F33TwoSidedMonitorCallbacks *)&PTR_FUN_0002888c);
  }
  else {
    retain_disabled_latched_monitor
              ((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe7994u)),(F33MonitorLimits *)((undefined *)camry_host_ptr(0x2b8d0u)));
  }
  publish_shared_condition_monitor_status(4,(*((uint *)camry_host_ptr((uint32_t)(puVar1 + -0x3e6c)))));
  return;
}

undefined4 test_b_flag_selected_sample_window_442c6(void)

{
  if (((((DAT_febe7bba != '\0') || (DAT_febeeb86 != '\0')) || (DAT_febeeb80 != 'Z')) ||
      ((((DAT_febeeb88 != '\0' || (DAT_0002b8fc <= DAT_febe7da8)) || (DAT_febe7db0 < DAT_0002b8fe))
       && (((DAT_febeeb88 != 'Z' || (DAT_0002b900 <= DAT_febe7da8)) || (DAT_febe7db0 < DAT_0002b8fe)
           ))))) &&
     ((DAT_0002b902 <= DAT_febe7da8 ||
      (((DAT_febe7bba != 'Z' && (DAT_febeeb86 != 'Z')) && (((int8_t)DAT_febeeb80) != -0x5b)))))) {
    return 0;
  }
  return 0x5a;
}

undefined4 classify_b_sample_window_and_monitor_flags_44334(void)

{
  char cVar1;
  char cVar2;
  char cVar3;
  char cVar4;
  char cVar5;
  char cVar6;
  char cVar7;
  char cVar8;
  char cVar9;
  char cVar10;
  uchar uVar11;
  uchar uVar12;
  char cVar13;
  ushort uVar14;
  ushort uVar15;
  char cVar16;
  char cVar17;
  char cVar18;
  int iVar19;
  undefined4 uVar20;
  
  cVar18 = DAT_febeeb88;
  cVar17 = DAT_febeeb86;
  cVar16 = DAT_febeeb80;
  uVar15 = DAT_febe7db0;
  uVar14 = DAT_febe7da8;
  cVar13 = DAT_febe7bba;
  uVar12 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe79dcu + (uint32_t)(2) * 1u))));
  uVar11 = ((volatile uint8_t *)camry_host_ptr(0xfebe79dcu))[0];
  cVar10 = DAT_febe7934;
  cVar9 = DAT_febe792e;
  cVar8 = DAT_febe792d;
  cVar7 = DAT_febe792c;
  cVar6 = DAT_febe792a;
  cVar5 = DAT_febe7929;
  cVar4 = DAT_febe7928;
  cVar3 = DAT_febe74ad;
  cVar2 = DAT_febe74ac;
  cVar1 = DAT_febe74ab;
  iVar19 = test_b_flag_selected_sample_window_442c6();
  if (cVar3 == '\0' &&
      (cVar2 == '\0' &&
      (cVar1 == '\0' &&
      (uVar11 == '\0' &&
      (uVar12 == '\0' &&
      (cVar9 == '\0' &&
      (cVar8 == '\0' &&
      (cVar7 == '\0' && (cVar10 == '\0' && (cVar6 == '\0' && (cVar5 == '\0' && cVar4 == '\0'))))))))
      ))) {
    if (iVar19 == 0x5a) {
      uVar20 = 0x22;
    }
    else if ((((cVar13 == '\0') && (cVar17 == '\0')) && (cVar16 == 'Z')) &&
            (((cVar18 == '\0' && (DAT_0002b904 <= uVar14)) && (DAT_0002b906 <= uVar15)))) {
      uVar20 = 0x11;
    }
    else {
      uVar20 = 0x33;
    }
  }
  else {
    uVar20 = 0x44;
  }
  return uVar20;
}

void report_diagnostic_healthy_observed_a7_443da(void)

{
  report_diagnostic_healthy_observed(0xa7);
  return;
}

void report_diagnostic_event_failure_a7_10_443ea(void)

{
  report_diagnostic_event_failure(0xa7,10);
  return;
}

void reset_latched_monitor_febe79a0(void)

{
  reset_latched_monitor((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe79a0u)));
  return;
}

void reset_latched_monitor_febe79a0_4440c(void)

{
  reset_latched_monitor((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe79a0u)));
  return;
}

void update_dual_channel_shared_latched_monitor_4441c(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  if (DAT_0002bc2c == 'Z') {
    reset_latched_monitor((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe79a0u)));
  }
  else if (((DAT_febe71ec & 3) == 0) && (DAT_febeeb85 == 'Z')) {
    step_latched_monitor
              ((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe79a0u)),(F33MonitorLimits *)((undefined *)camry_host_ptr(0x2b8d4u)),
               (F33TwoSidedMonitorCallbacks *)&PTR_FUN_000288c0);
  }
  else {
    retain_disabled_latched_monitor
              ((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe79a0u)),(F33MonitorLimits *)((undefined *)camry_host_ptr(0x2b8d4u)));
  }
  publish_shared_condition_monitor_status(0,(*((uint *)camry_host_ptr((uint32_t)(puVar1 + -0x3e60)))));
  return;
}

undefined4 classify_input_latch_and_flag_selected_window_44478(ushort param_1,char param_2)

{
  if ((param_2 != 'Z') &&
     (((((DAT_febe7bba != '\0' || (DAT_febeeb86 != '\0')) || (DAT_febeeb80 != 'Z')) ||
       ((((DAT_febeeb88 != '\0' || (DAT_0002b908 <= param_1)) || (DAT_febe7db0 < DAT_0002b90a)) &&
        (((DAT_febeeb88 != 'Z' || (DAT_0002b90c <= param_1)) || (DAT_febe7db0 < DAT_0002b90a))))))
      && ((((DAT_febe7bba != 'Z' && (((int8_t)DAT_febeeb80) != -0x5b)) && (DAT_febeeb86 != 'Z')) ||
          (DAT_0002b90e <= param_1)))))) {
    if ((((param_2 == '\0') && (DAT_febe7bba == '\0')) &&
        (((DAT_febeeb86 == '\0' && ((DAT_febeeb80 == 'Z' && (DAT_febeeb88 == '\0')))) &&
         (DAT_0002b910 <= param_1)))) && (DAT_0002b912 <= DAT_febe7db0)) {
      return 0x11;
    }
    return 0x33;
  }
  return 0x22;
}

int combine_two_sample_window_classifications_44516(void)

{
  undefined2 uVar1;
  undefined1 uVar2;
  int iVar3;
  int iVar4;
  
  uVar2 = DAT_febe8292;
  uVar1 = DAT_febe7da8;
  if (DAT_febe74ad == '\0' &&
      (DAT_febe74ac == '\0' &&
      (DAT_febe74ab == '\0' &&
      (DAT_febe74aa == '\0' &&
      (DAT_febe792e == '\0' &&
      (DAT_febe792d == '\0' &&
      (DAT_febe792c == '\0' &&
      (DAT_febe7934 == '\0' &&
      (DAT_febe792a == '\0' &&
      (DAT_febe7929 == '\0' &&
      (DAT_febe7928 == '\0' &&
      (DAT_febe781e == '\0' &&
      (DAT_febe781d == '\0' &&
      (DAT_febe781c == '\0' &&
      (DAT_febe7824 == '\0' &&
      (DAT_febe781a == '\0' && (DAT_febe7819 == '\0' && DAT_febe7818 == '\0'))))))))))))))))) {
    iVar3 = classify_input_latch_and_flag_selected_window_44478(DAT_febe7da6,DAT_febe8291);
    iVar4 = classify_input_latch_and_flag_selected_window_44478(uVar1,uVar2);
    if ((iVar3 != 0x22) || (iVar4 != 0x22)) {
      if ((iVar3 == 0x11) || (iVar4 == 0x11)) {
        iVar4 = 0x11;
      }
      else {
        iVar4 = 0x33;
      }
    }
  }
  else {
    iVar4 = 0x44;
  }
  return iVar4;
}

void report_events_62_63_healthy_445b8(void)

{
  report_diagnostic_healthy_observed(0x62);
  report_diagnostic_healthy_observed(99);
  return;
}

void report_events_62_63_failure_445d0(void)

{
  report_diagnostic_event_failure(0x62,10);
  report_diagnostic_event_failure(99,10);
  return;
}

void reset_latched_monitor_febe79ac(void)

{
  reset_latched_monitor((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe79acu)));
  return;
}

void reset_latched_monitor_febe79ac_445fc(void)

{
  reset_latched_monitor((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe79acu)));
  return;
}

void update_direct_source_a_shared_latched_monitor_4460c(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  if (DAT_0002bc30 == 'Z') {
    reset_latched_monitor((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe79acu)));
  }
  else if ((DAT_febe71ec & 1) == 0) {
    step_latched_monitor
              ((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe79acu)),(F33MonitorLimits *)((undefined *)camry_host_ptr(0x2b8d8u)),
               (F33TwoSidedMonitorCallbacks *)&PTR_classify_direct_source_a_000288f4);
  }
  else {
    retain_disabled_latched_monitor
              ((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe79acu)),(F33MonitorLimits *)((undefined *)camry_host_ptr(0x2b8d8u)));
  }
  publish_shared_condition_monitor_status(1,(*((uint *)camry_host_ptr((uint32_t)(puVar1 + -0x3e54)))));
  return;
}

uint classify_direct_source_a(void)

{
  if (((volatile uint8_t *)camry_host_ptr(0xfebe79dcu))[0] != '\0') {
    return 0x44;
  }
  if (DAT_febe8291 == 'Z') {
    return 0x22;
  }
  return 0x11;
}

void report_diagnostic_healthy_observed_8b_44678(void)

{
  report_diagnostic_healthy_observed(0x8b);
  return;
}

void report_diagnostic_event_failure_8b_10_44688(void)

{
  report_diagnostic_event_failure(0x8b,10);
  return;
}

void reset_latched_monitor_febe79b8(void)

{
  reset_latched_monitor((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe79b8u)));
  return;
}

void reset_latched_monitor_febe79b8_446aa(void)

{
  reset_latched_monitor((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe79b8u)));
  return;
}

void update_direct_source_b_shared_latched_monitor_446ba(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  if (DAT_0002bc34 == 'Z') {
    reset_latched_monitor((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe79b8u)));
  }
  else if ((DAT_febe71ec >> 1 & 1) == 0) {
    step_latched_monitor
              ((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe79b8u)),(F33MonitorLimits *)((undefined *)camry_host_ptr(0x2b8dcu)),
               (F33TwoSidedMonitorCallbacks *)&PTR_classify_direct_source_b_00028928);
  }
  else {
    retain_disabled_latched_monitor
              ((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe79b8u)),(F33MonitorLimits *)((undefined *)camry_host_ptr(0x2b8dcu)));
  }
  publish_shared_condition_monitor_status(2,(*((uint *)camry_host_ptr((uint32_t)(puVar1 + -0x3e48)))));
  return;
}

uint classify_direct_source_b(void)

{
  if (((volatile uint8_t *)camry_host_ptr(0xfebe79dcu))[0] != '\0') {
    return 0x44;
  }
  if (DAT_febe8292 == 'Z') {
    return 0x22;
  }
  return 0x11;
}

void report_diagnostic_healthy_observed_8c_44726(void)

{
  report_diagnostic_healthy_observed(0x8c);
  return;
}

void report_diagnostic_event_failure_8c_10_44736(void)

{
  report_diagnostic_event_failure(0x8c,10);
  return;
}

void reset_latched_monitor_febe79c4(void)

{
  reset_latched_monitor((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe79c4u)));
  return;
}

void reset_latched_monitor_febe79c4_44758(void)

{
  reset_latched_monitor((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe79c4u)));
  return;
}

void update_paired_gate_a_shared_latched_monitor_44768(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  if (DAT_0002bc38 == 'Z') {
    reset_latched_monitor((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe79c4u)));
  }
  else if (((DAT_febe71ec & 3) == 0) && (DAT_febeeb85 == 'Z')) {
    step_latched_monitor
              ((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe79c4u)),(F33MonitorLimits *)((undefined *)camry_host_ptr(0x2b8e0u)),
               (F33TwoSidedMonitorCallbacks *)&PTR_classify_paired_shared_gate_a_0002895c);
  }
  else {
    retain_disabled_latched_monitor
              ((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe79c4u)),(F33MonitorLimits *)((undefined *)camry_host_ptr(0x2b8e0u)));
  }
  publish_shared_condition_monitor_status(5,(*((uint *)camry_host_ptr((uint32_t)(puVar1 + -0x3e3c)))));
  return;
}

uint classify_paired_shared_gate_a(void)

{
  if ((DAT_0002b916 < DAT_febe7da6) &&
     ((DAT_febe7db0 <= DAT_0002b914 || ((DAT_febe7da8 <= DAT_0002b918 && (DAT_febe7966 != 'Z'))))))
  {
    return 0x22;
  }
  if ((DAT_febe7da6 <= DAT_0002b91c) &&
     ((DAT_febe7db0 <= DAT_0002b91a && (DAT_febe7da8 <= DAT_0002b91e)))) {
    return 0x11;
  }
  return 0x33;
}

void report_diagnostic_healthy_observed_a3_44814(void)

{
  report_diagnostic_healthy_observed(0xa3);
  return;
}

void report_diagnostic_event_failure_a3_10_44824(void)

{
  report_diagnostic_event_failure(0xa3,10);
  return;
}

void reset_latched_monitor_febe79d0(void)

{
  reset_latched_monitor((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe79d0u)));
  return;
}

void reset_latched_monitor_febe79d0_44846(void)

{
  reset_latched_monitor((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe79d0u)));
  return;
}

void update_paired_gate_b_shared_latched_monitor_44856(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  if (DAT_0002bc3c == 'Z') {
    reset_latched_monitor((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe79d0u)));
  }
  else if (((DAT_febe71ec & 3) == 0) && (DAT_febeeb85 == 'Z')) {
    step_latched_monitor
              ((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe79d0u)),(F33MonitorLimits *)((undefined *)camry_host_ptr(0x2b8e4u)),
               (F33TwoSidedMonitorCallbacks *)&PTR_classify_paired_shared_gate_b_00028990);
  }
  else {
    retain_disabled_latched_monitor
              ((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe79d0u)),(F33MonitorLimits *)((undefined *)camry_host_ptr(0x2b8e4u)));
  }
  publish_shared_condition_monitor_status(6,(*((uint *)camry_host_ptr((uint32_t)(puVar1 + -0x3e30)))));
  return;
}

uint classify_paired_shared_gate_b(void)

{
  if ((DAT_0002b922 < DAT_febe7da8) &&
     ((DAT_febe7db0 <= DAT_0002b920 || ((DAT_febe7da6 <= DAT_0002b924 && (DAT_febe7967 != 'Z'))))))
  {
    return 0x22;
  }
  if ((DAT_febe7da8 <= DAT_0002b928) &&
     ((DAT_febe7db0 <= DAT_0002b926 && (DAT_febe7da6 <= DAT_0002b92a)))) {
    return 0x11;
  }
  return 0x33;
}

void report_diagnostic_healthy_observed_a6_44902(void)

{
  report_diagnostic_healthy_observed(0xa6);
  return;
}

void report_diagnostic_event_failure_a6_10_44912(void)

{
  report_diagnostic_event_failure(0xa6,10);
  return;
}

void return_only_stub_44924(void)

{
  return;
}

void return_only_stub_44926(void)

{
  return;
}

void publish_shared_condition_monitor_actions(void)

{
  char cVar1;
  ushort uVar2;
  uint32_t puVar3;
  uchar uVar4;
  int iVar5;
  undefined1 uVar6;
  
  uVar2 = DAT_febe71ec;
  cVar1 = DAT_febe63dc;
  puVar3 = 0xfebeb800u;
  iVar5 = (int)((int)(int16_t)DAT_febe643e);
  retain_and_clear_fault_record(1);
  if ((((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x3e22))))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x3e20))))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x3e23))))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x3e21))))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x3e24)))))) &
      0x11) == 0x11) {
    encode_fault_action_kind('\x01','\n');
  }
  if (((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x3e24))))) & 0x22) == 0x22) {
    iVar5 = latch_request_bits_and_check_signed_magnitude_36066(2,iVar5);
    if ((iVar5 == 1) || (cVar1 == '\x01')) {
      uVar4 = '\v';
    }
    else {
      uVar4 = '\x17';
    }
    encode_fault_action_kind('\x01',uVar4);
  }
  if ((((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x3e23))))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x3e21)))))) & 0x22) == 0x22) {
    encode_fault_action_kind('\x01','#');
  }
  if ((((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x3e22))))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x3e20)))))) & 0x22) == 0x22) {
    encode_fault_action_kind('\x01','$');
  }
  if ((((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x3e1d))))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x3e1f)))))) & 0x22) == 0x22) {
    encode_fault_action_kind('\x01','\x1b');
  }
  if ((((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x3e1c))))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x3e1e)))))) & 0x22) == 0x22) {
    encode_fault_action_kind('\x01','\x1c');
  }
  if (((((((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x3e23))))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x3e21)))))) & 0x22) == 0x22) && ((uVar2 & 1) == 0)) ||
      (((((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x3e22))))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x3e20)))))) & 0x22) == 0x22 && ((uVar2 >> 1 & 1) == 0)))) ||
     (((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x3e24))))) & 0x22) == 0x22)) {
    encode_fault_action_kind('\x01','\n');
  }
  if ((((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x3e22))))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x3e20))))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x3e23))))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x3e21)))))) & 0x22) == 0x22) {
    encode_fault_action_kind('\x01','2');
  }
  uVar6 = 0;
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x3e22))))) != '\0' ||
      ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x3e1c))))) != '\0' ||
      ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x3e20))))) != '\0' ||
      ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x3e1e))))) != '\0' ||
      ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x3e23))))) != '\0' ||
      ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x3e1d))))) != '\0' ||
      ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x3e21))))) != '\0' || ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x3e1f))))) != '\0' || (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x3e24))))) != '\0')))))))) {
    uVar6 = 0x5a;
  }
  select_current_fault_record(1);
  uVar4 = '\0';
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x3e22))))) != '\0' ||
      ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x3e1e))))) != '\0' ||
      ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x3e20))))) != '\0' ||
      ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x3e23))))) != '\0' ||
      ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x3e1f))))) != '\0' || ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x3e21))))) != '\0' || (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x3e24))))) != '\0')))))) {
    uVar4 = '\x11';
  }
  set_diagnostic_cache_blocker('\x05',uVar4);
  uVar4 = '\0';
  if ((((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x3e22))))) |
       (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x3e1e))))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x3e20))))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x3e23))))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x3e1f))))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x3e21)))))) &
      0x11) == 0x11) {
    uVar4 = 'Z';
  }
  set_monitor_pending_projection('\x01',uVar4);
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x3e1b))))) = uVar6;
  return;
}

void publish_shared_condition_monitor_status(uint index,uint packed)

{
  if ((index & 0xff) < 9) {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe79dcu + (uint32_t)(index & 0xff) * 1u)))) = (uchar)packed;
  }
  return;
}

void return_only_stub_44b1e(void)

{
  return;
}

void reset_six_window_monitors_and_input_fields_44b20(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  reset_windowed_monitor((F33WindowedMonitorState *)((undefined *)camry_host_ptr(0xfebe7a00u)));
  reset_windowed_monitor(((F33WindowedMonitorState *)camry_host_ptr((uint32_t)(puVar1 + -0x3df0))));
  reset_windowed_monitor(((F33WindowedMonitorState *)camry_host_ptr((uint32_t)(puVar1 + -0x3de0))));
  reset_windowed_monitor(((F33WindowedMonitorState *)camry_host_ptr((uint32_t)(puVar1 + -0x3dd0))));
  reset_windowed_monitor(((F33WindowedMonitorState *)camry_host_ptr((uint32_t)(puVar1 + -0x3dc0))));
  reset_windowed_monitor(((F33WindowedMonitorState *)camry_host_ptr((uint32_t)(puVar1 + -0x3db0))));
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x3da0)))) = 0;
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x3d9e)))) = 0;
  (*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + -0x3d9c)))) = 0;
  (*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + -0x3d98)))) = 0;
  return;
}

void report_diagnostic_healthy_observed_cell_44c00(void)

{
  report_diagnostic_healthy_observed((uint)DAT_febe7a62);
  return;
}

void report_diagnostic_event_failure_10_44c10(void)

{
  report_diagnostic_event_failure((uint)DAT_febe7a62,10);
  return;
}

void reset_first_window_pair_and_input_fields_44c22(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  reset_windowed_monitor((F33WindowedMonitorState *)((undefined *)camry_host_ptr(0xfebe7a74u)));
  reset_windowed_monitor(((F33WindowedMonitorState *)camry_host_ptr((uint32_t)(puVar1 + -0x3d7c))));
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x3d94)))) = 0;
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x3d92)))) = 0;
  (*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + -0x3d90)))) = 0;
  return;
}

void report_first_stored_event_pair_failure_44cb2(void)

{
  uint event;
  
  event = (uint)DAT_febe7a6e;
  report_diagnostic_event_failure((uint)DAT_febe7a6c,10);
  report_diagnostic_event_failure(event,10);
  return;
}

void reset_second_window_pair_and_input_fields_44cd0(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  reset_windowed_monitor((F33WindowedMonitorState *)((undefined *)camry_host_ptr(0xfebe7a9cu)));
  reset_windowed_monitor(((F33WindowedMonitorState *)camry_host_ptr((uint32_t)(puVar1 + -0x3d54))));
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x3d6c)))) = 0;
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x3d6a)))) = 0;
  (*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + -0x3d68)))) = 0;
  return;
}

void report_second_stored_event_pair_failure_44d60(void)

{
  uint event;
  
  event = (uint)DAT_febe7a96;
  report_diagnostic_event_failure((uint)DAT_febe7a94,10);
  report_diagnostic_event_failure(event,10);
  return;
}

void reset_third_window_pair_and_input_fields_44d7e(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  reset_windowed_monitor((F33WindowedMonitorState *)((undefined *)camry_host_ptr(0xfebe7ac4u)));
  reset_windowed_monitor(((F33WindowedMonitorState *)camry_host_ptr((uint32_t)(puVar1 + -0x3d2c))));
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x3d44)))) = 0;
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x3d42)))) = 0;
  (*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + -0x3d40)))) = 0;
  return;
}

void report_third_stored_event_pair_failure_44e0e(void)

{
  uint event;
  
  event = (uint)DAT_febe7abe;
  report_diagnostic_event_failure((uint)DAT_febe7abc,10);
  report_diagnostic_event_failure(event,10);
  return;
}

void reset_six_latched_monitors_and_input_halfwords_44e2c(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  DAT_febe7ae4 = 0;
  DAT_febe7ae6 = 0;
  reset_latched_monitor((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe7ae8u)));
  reset_latched_monitor(((F33LatchedMonitorState *)camry_host_ptr((uint32_t)(puVar1 + -0x3d0c))));
  reset_latched_monitor(((F33LatchedMonitorState *)camry_host_ptr((uint32_t)(puVar1 + -0x3d00))));
  reset_latched_monitor(((F33LatchedMonitorState *)camry_host_ptr((uint32_t)(puVar1 + -0x3cf4))));
  reset_latched_monitor(((F33LatchedMonitorState *)camry_host_ptr((uint32_t)(puVar1 + -0x3ce8))));
  reset_latched_monitor(((F33LatchedMonitorState *)camry_host_ptr((uint32_t)(puVar1 + -0x3cdc))));
  return;
}

void report_diagnostic_healthy_observed_cell_44ea8(void)

{
  report_diagnostic_healthy_observed((uint)DAT_febe7ae4);
  return;
}

void report_diagnostic_event_failure_10_44eb8(void)

{
  report_diagnostic_event_failure((uint)DAT_febe7ae4,10);
  return;
}

void return_only_stub_44eca(void)

{
  return;
}

void return_only_stub_44ecc(void)

{
  return;
}

void set_high_nibble_indexed_halfword_bit_44ece(uint param_1,ushort *param_2)

{
  *param_2 = *param_2 | (ushort)(1 << ((int)(param_1 & 0xffff) >> 0xc));
  return;
}

void record_a_reference_sum_gated_bins_44ee2(void)

{
  int iVar1;
  uint32_t puVar2;
  uint uVar3;
  int iVar4;
  uint32_t puVar5;
  int iVar6;
  undefined2 uStack_6;
  
  puVar2 = 0xfebeb800u;
  iVar4 = (int)((int)(int16_t)DAT_febe63e8);
  uVar3 = (uint)((int)(int16_t)DAT_febe63e6);
  uStack_6 = DAT_febe7b30;
  puVar5 = ((int)(*((volatile int16_t *)camry_host_ptr((uint32_t)(0xfebe7e78u + (uint32_t)(2) * 2u)))) +
           (int)(*((volatile int16_t *)camry_host_ptr((uint32_t)(0xfebe7e78u + (uint32_t)(1) * 2u)))) +
           (int)((volatile int16_t *)camry_host_ptr(0xfebe7e78u))[0]);
  iVar1 = (int)((int)(int16_t)DAT_febe629e);
  if (iVar1 + 0x7fff < 0 == (-1 < iVar1 && iVar1 + 0x7fff < 0) && iVar1 != -0x7fff) {
    if (iVar1 < 0) {
      iVar1 = (int)-((int)(int16_t)DAT_febe629e);
    }
  }
  else {
    iVar1 = 0x7fff;
  }
  if (iVar4 + 0x7fff < 0 == (-1 < iVar4 && iVar4 + 0x7fff < 0) && iVar4 != -0x7fff) {
    if (iVar4 < 0) {
      iVar4 = (int)-((int)(int16_t)DAT_febe63e8);
    }
  }
  else {
    iVar4 = 0x7fff;
  }
  if ((int)((int)uVar3 + 0x7fff) < 0 == (-1 < (int)uVar3 && (int)((int)uVar3 + 0x7fff) < 0) &&
      uVar3 != 0xffff8001) {
    if ((int)uVar3 < 0) {
      uVar3 = -uVar3;
    }
  }
  else {
    uVar3 = 0x7fff;
  }
  if ((int)((int)puVar5 + 0x7fffffff) < 0 == (-1 < (int)puVar5 && (int)((int)puVar5 + 0x7fffffff) < 0) &&
      puVar5 != 0x80000001u) {
    if ((int)puVar5 < 0) {
      puVar5 = -(int)puVar5;
    }
  }
  else {
    puVar5 = 0x7fffffff;
  }
  if (((((int)puVar5 - (int)PTR_LAB_000010ca_4_0002b9a8 < 0 !=
         ((int)puVar5 < 0 != (int)PTR_LAB_000010ca_4_0002b9a8 < 0 &&
         (int)PTR_LAB_000010ca_4_0002b9a8 < 0 == (int)puVar5 - (int)PTR_LAB_000010ca_4_0002b9a8 < 0)
         || puVar5 == PTR_LAB_000010ca_4_0002b9a8) && (DAT_febe6368 == 'Z')) &&
      (iVar6 = (int)DAT_0002b99a,
      iVar1 - iVar6 < 0 != (iVar1 < 0 != iVar6 < 0 && iVar6 < 0 == iVar1 - iVar6 < 0) ||
      iVar1 == iVar6)) &&
     ((iVar1 = (int)DAT_0002b998,
      iVar4 - iVar1 < 0 == (iVar4 < 0 != iVar1 < 0 && iVar1 < 0 == iVar4 - iVar1 < 0) &&
      iVar4 != iVar1 && ((uVar3 & 0xffff) < (uint)DAT_0002b9a6)))) {
    puVar2 = 0xfebeb800u;
    set_high_nibble_indexed_halfword_bit_44ece(DAT_febe63b8,&uStack_6);
  }
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar2 + -0x3cd0)))) = uStack_6;
  return;
}

void record_b_reference_sum_gated_bins_44fa2(void)

{
  int iVar1;
  uint32_t puVar2;
  uint uVar3;
  int iVar4;
  uint32_t puVar5;
  int iVar6;
  undefined2 uStack_6;
  
  puVar2 = 0xfebeb800u;
  iVar4 = (int)((int)(int16_t)DAT_febe63ec);
  uVar3 = (uint)((int)(int16_t)DAT_febe63ea);
  uStack_6 = DAT_febe7b32;
  puVar5 = ((int)(*((volatile int16_t *)camry_host_ptr((uint32_t)(0xfebe7e78u + (uint32_t)(5) * 2u)))) +
           (int)(*((volatile int16_t *)camry_host_ptr((uint32_t)(0xfebe7e78u + (uint32_t)(4) * 2u)))) +
           (int)(*((volatile int16_t *)camry_host_ptr((uint32_t)(0xfebe7e78u + (uint32_t)(3) * 2u)))));
  iVar1 = (int)((int)(int16_t)DAT_febe629e);
  if (iVar1 + 0x7fff < 0 == (-1 < iVar1 && iVar1 + 0x7fff < 0) && iVar1 != -0x7fff) {
    if (iVar1 < 0) {
      iVar1 = (int)-((int)(int16_t)DAT_febe629e);
    }
  }
  else {
    iVar1 = 0x7fff;
  }
  if (iVar4 + 0x7fff < 0 == (-1 < iVar4 && iVar4 + 0x7fff < 0) && iVar4 != -0x7fff) {
    if (iVar4 < 0) {
      iVar4 = (int)-((int)(int16_t)DAT_febe63ec);
    }
  }
  else {
    iVar4 = 0x7fff;
  }
  if ((int)((int)uVar3 + 0x7fff) < 0 == (-1 < (int)uVar3 && (int)((int)uVar3 + 0x7fff) < 0) &&
      uVar3 != 0xffff8001) {
    if ((int)uVar3 < 0) {
      uVar3 = -uVar3;
    }
  }
  else {
    uVar3 = 0x7fff;
  }
  if ((int)((int)puVar5 + 0x7fffffff) < 0 == (-1 < (int)puVar5 && (int)((int)puVar5 + 0x7fffffff) < 0) &&
      puVar5 != 0x80000001u) {
    if ((int)puVar5 < 0) {
      puVar5 = -(int)puVar5;
    }
  }
  else {
    puVar5 = 0x7fffffff;
  }
  if (((((int)puVar5 - (int)PTR_LAB_000010ca_4_0002b9a8 < 0 !=
         ((int)puVar5 < 0 != (int)PTR_LAB_000010ca_4_0002b9a8 < 0 &&
         (int)PTR_LAB_000010ca_4_0002b9a8 < 0 == (int)puVar5 - (int)PTR_LAB_000010ca_4_0002b9a8 < 0)
         || puVar5 == PTR_LAB_000010ca_4_0002b9a8) && (DAT_febe6369 == 'Z')) &&
      (iVar6 = (int)DAT_0002b99a,
      iVar1 - iVar6 < 0 != (iVar1 < 0 != iVar6 < 0 && iVar6 < 0 == iVar1 - iVar6 < 0) ||
      iVar1 == iVar6)) &&
     ((iVar1 = (int)DAT_0002b998,
      iVar4 - iVar1 < 0 == (iVar4 < 0 != iVar1 < 0 && iVar1 < 0 == iVar4 - iVar1 < 0) &&
      iVar4 != iVar1 && ((uVar3 & 0xffff) < (uint)DAT_0002b9a6)))) {
    puVar2 = 0xfebeb800u;
    set_high_nibble_indexed_halfword_bit_44ece(DAT_febe63b8,&uStack_6);
  }
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar2 + -0x3cce)))) = uStack_6;
  return;
}
