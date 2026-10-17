#include "common.h"


void FUN_0004400a(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  if (DAT_0002bc20 == 'Z') {
    f33_reset_latched_monitor((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe797cu)));
  }
  else if (((DAT_febe71ec & 1) == 0) || (DAT_febeeb85 != 'Z')) {
    f33_report_diagnostic_healthy_observed(0xe3);
  }
  else {
    f33_step_latched_monitor
              ((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe797cu)),(F33MonitorLimits *)((undefined *)camry_host_ptr(0x2b8c8u)),
               (F33TwoSidedMonitorCallbacks *)&PTR_f33_classify_inverse_gate_b_00028824);
  }
  f33_publish_shared_condition_monitor_status(8,(*((uint *)camry_host_ptr((uint32_t)(puVar1 + -0x3e84)))));
  return;
}



/* Exact slot0/1 callback predicate. Return11/22/33/44 protocol; software source, qualification and
   retained-snapshot conditions are not physical freshness guarantees. InverseB gate>6400 and
   shared<=4096 fails22, else11; opposite qualification bit admits it and failure51 confirms. */

uint f33_classify_inverse_gate_b(void)

{
  if ((DAT_0002b8ee < DAT_febe7da8) && (DAT_febe7db0 <= DAT_0002b8ec)) {
    return 0x22;
  }
  return 0x11;
}



/* f33_report_diagnostic_event_failure(0xe3,10); whole-body shape-verified. The literal is the
   encoded diagnostic event, not a recovered OEM name. */

void f33_report_diagnostic_event_failure_e3_10_4408a(void)

{
  f33_report_diagnostic_event_failure(0xe3,10);
  return;
}



/* f33_reset_latched_monitor wrapper resetting exactly one monitor state ((F33LatchedMonitorState
   *)((undefined *)camry_host_ptr(0xfebe7988u))); whole-body shape-verified from the canonical corpus. Per-instance semantics
   derive from the referenced state cell; not individually executed. */

void f33_reset_latched_monitor_febe7988(void)

{
  f33_reset_latched_monitor((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe7988u)));
  return;
}



/* f33_reset_latched_monitor wrapper resetting exactly one monitor state ((F33LatchedMonitorState
   *)((undefined *)camry_host_ptr(0xfebe7988u))); whole-body shape-verified from the canonical corpus. Per-instance semantics
   derive from the referenced state cell; not individually executed. */

void f33_reset_latched_monitor_febe7988_440ac(void)

{
  f33_reset_latched_monitor((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe7988u)));
  return;
}



void FUN_000440bc(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  if (DAT_0002bc24 == 'Z') {
    f33_reset_latched_monitor((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe7988u)));
  }
  else if (((DAT_febe71ec & 1) == 0) && (DAT_febeeb85 == 'Z')) {
    f33_step_latched_monitor
              ((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe7988u)),(F33MonitorLimits *)((undefined *)camry_host_ptr(0x2b8ccu)),
               (F33TwoSidedMonitorCallbacks *)&PTR_FUN_00028858);
  }
  else {
    f33_retain_disabled_latched_monitor
              ((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe7988u)),(F33MonitorLimits *)((undefined *)camry_host_ptr(0x2b8ccu)));
  }
  f33_publish_shared_condition_monitor_status(3,(*((uint *)camry_host_ptr((uint32_t)(puVar1 + -0x3e78)))));
  return;
}



undefined4 FUN_00044116(void)

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



undefined4 FUN_00044184(void)

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
  uVar12 = f33_shared_condition_status[1];
  uVar11 = f33_shared_condition_status[0];
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
  iVar19 = FUN_00044116();
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



/* f33_report_diagnostic_healthy_observed(0xa4); whole-body shape-verified. The literal is the
   encoded diagnostic event, not a recovered OEM name. */

void f33_report_diagnostic_healthy_observed_a4_4422a(void)

{
  f33_report_diagnostic_healthy_observed(0xa4);
  return;
}



/* f33_report_diagnostic_event_failure(0xa4,10); whole-body shape-verified. The literal is the
   encoded diagnostic event, not a recovered OEM name. */

void f33_report_diagnostic_event_failure_a4_10_4423a(void)

{
  f33_report_diagnostic_event_failure(0xa4,10);
  return;
}



/* f33_reset_latched_monitor wrapper resetting exactly one monitor state ((F33LatchedMonitorState
   *)((undefined *)camry_host_ptr(0xfebe7994u))); whole-body shape-verified from the canonical corpus. Per-instance semantics
   derive from the referenced state cell; not individually executed. */

void f33_reset_latched_monitor_febe7994(void)

{
  f33_reset_latched_monitor((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe7994u)));
  return;
}



/* f33_reset_latched_monitor wrapper resetting exactly one monitor state ((F33LatchedMonitorState
   *)((undefined *)camry_host_ptr(0xfebe7994u))); whole-body shape-verified from the canonical corpus. Per-instance semantics
   derive from the referenced state cell; not individually executed. */

void f33_reset_latched_monitor_febe7994_4425c(void)

{
  f33_reset_latched_monitor((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe7994u)));
  return;
}



void FUN_0004426c(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  if (DAT_0002bc28 == 'Z') {
    f33_reset_latched_monitor((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe7994u)));
  }
  else if (((DAT_febe71ec >> 1 & 1) == 0) && (DAT_febeeb85 == 'Z')) {
    f33_step_latched_monitor
              ((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe7994u)),(F33MonitorLimits *)((undefined *)camry_host_ptr(0x2b8d0u)),
               (F33TwoSidedMonitorCallbacks *)&PTR_FUN_0002888c);
  }
  else {
    f33_retain_disabled_latched_monitor
              ((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe7994u)),(F33MonitorLimits *)((undefined *)camry_host_ptr(0x2b8d0u)));
  }
  f33_publish_shared_condition_monitor_status(4,(*((uint *)camry_host_ptr((uint32_t)(puVar1 + -0x3e6c)))));
  return;
}



undefined4 FUN_000442c6(void)

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



undefined4 FUN_00044334(void)

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
  uVar12 = f33_shared_condition_status[2];
  uVar11 = f33_shared_condition_status[0];
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
  iVar19 = FUN_000442c6();
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



/* f33_report_diagnostic_healthy_observed(0xa7); whole-body shape-verified. The literal is the
   encoded diagnostic event, not a recovered OEM name. */

void f33_report_diagnostic_healthy_observed_a7_443da(void)

{
  f33_report_diagnostic_healthy_observed(0xa7);
  return;
}



/* f33_report_diagnostic_event_failure(0xa7,10); whole-body shape-verified. The literal is the
   encoded diagnostic event, not a recovered OEM name. */

void f33_report_diagnostic_event_failure_a7_10_443ea(void)

{
  f33_report_diagnostic_event_failure(0xa7,10);
  return;
}



/* f33_reset_latched_monitor wrapper resetting exactly one monitor state ((F33LatchedMonitorState
   *)((undefined *)camry_host_ptr(0xfebe79a0u))); whole-body shape-verified from the canonical corpus. Per-instance semantics
   derive from the referenced state cell; not individually executed. */

void f33_reset_latched_monitor_febe79a0(void)

{
  f33_reset_latched_monitor((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe79a0u)));
  return;
}



/* f33_reset_latched_monitor wrapper resetting exactly one monitor state ((F33LatchedMonitorState
   *)((undefined *)camry_host_ptr(0xfebe79a0u))); whole-body shape-verified from the canonical corpus. Per-instance semantics
   derive from the referenced state cell; not individually executed. */

void f33_reset_latched_monitor_febe79a0_4440c(void)

{
  f33_reset_latched_monitor((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe79a0u)));
  return;
}



void FUN_0004441c(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  if (DAT_0002bc2c == 'Z') {
    f33_reset_latched_monitor((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe79a0u)));
  }
  else if (((DAT_febe71ec & 3) == 0) && (DAT_febeeb85 == 'Z')) {
    f33_step_latched_monitor
              ((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe79a0u)),(F33MonitorLimits *)((undefined *)camry_host_ptr(0x2b8d4u)),
               (F33TwoSidedMonitorCallbacks *)&PTR_FUN_000288c0);
  }
  else {
    f33_retain_disabled_latched_monitor
              ((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe79a0u)),(F33MonitorLimits *)((undefined *)camry_host_ptr(0x2b8d4u)));
  }
  f33_publish_shared_condition_monitor_status(0,(*((uint *)camry_host_ptr((uint32_t)(puVar1 + -0x3e60)))));
  return;
}



undefined4 FUN_00044478(ushort param_1,char param_2)

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



int FUN_00044516(void)

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
    iVar3 = FUN_00044478(DAT_febe7da6,DAT_febe8291);
    iVar4 = FUN_00044478(uVar1,uVar2);
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



void FUN_000445b8(void)

{
  f33_report_diagnostic_healthy_observed(0x62);
  f33_report_diagnostic_healthy_observed(99);
  return;
}



void FUN_000445d0(void)

{
  f33_report_diagnostic_event_failure(0x62,10);
  f33_report_diagnostic_event_failure(99,10);
  return;
}



/* f33_reset_latched_monitor wrapper resetting exactly one monitor state ((F33LatchedMonitorState
   *)((undefined *)camry_host_ptr(0xfebe79acu))); whole-body shape-verified from the canonical corpus. Per-instance semantics
   derive from the referenced state cell; not individually executed. */

void f33_reset_latched_monitor_febe79ac(void)

{
  f33_reset_latched_monitor((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe79acu)));
  return;
}



/* f33_reset_latched_monitor wrapper resetting exactly one monitor state ((F33LatchedMonitorState
   *)((undefined *)camry_host_ptr(0xfebe79acu))); whole-body shape-verified from the canonical corpus. Per-instance semantics
   derive from the referenced state cell; not individually executed. */

void f33_reset_latched_monitor_febe79ac_445fc(void)

{
  f33_reset_latched_monitor((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe79acu)));
  return;
}



void FUN_0004460c(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  if (DAT_0002bc30 == 'Z') {
    f33_reset_latched_monitor((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe79acu)));
  }
  else if ((DAT_febe71ec & 1) == 0) {
    f33_step_latched_monitor
              ((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe79acu)),(F33MonitorLimits *)((undefined *)camry_host_ptr(0x2b8d8u)),
               (F33TwoSidedMonitorCallbacks *)&PTR_f33_classify_direct_source_a_000288f4);
  }
  else {
    f33_retain_disabled_latched_monitor
              ((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe79acu)),(F33MonitorLimits *)((undefined *)camry_host_ptr(0x2b8d8u)));
  }
  f33_publish_shared_condition_monitor_status(1,(*((uint *)camry_host_ptr((uint32_t)(puVar1 + -0x3e54)))));
  return;
}



/* Exact slot0/1 callback predicate. Return11/22/33/44 protocol; software source, qualification and
   retained-snapshot conditions are not physical freshness guarantees. Direct sourceA returns44 for
   any nonzero common status before inspecting8291. */

uint f33_classify_direct_source_a(void)

{
  if (f33_shared_condition_status[0] != '\0') {
    return 0x44;
  }
  if (DAT_febe8291 == 'Z') {
    return 0x22;
  }
  return 0x11;
}



/* f33_report_diagnostic_healthy_observed(0x8b); whole-body shape-verified. The literal is the
   encoded diagnostic event, not a recovered OEM name. */

void f33_report_diagnostic_healthy_observed_8b_44678(void)

{
  f33_report_diagnostic_healthy_observed(0x8b);
  return;
}



/* f33_report_diagnostic_event_failure(0x8b,10); whole-body shape-verified. The literal is the
   encoded diagnostic event, not a recovered OEM name. */

void f33_report_diagnostic_event_failure_8b_10_44688(void)

{
  f33_report_diagnostic_event_failure(0x8b,10);
  return;
}



/* f33_reset_latched_monitor wrapper resetting exactly one monitor state ((F33LatchedMonitorState
   *)((undefined *)camry_host_ptr(0xfebe79b8u))); whole-body shape-verified from the canonical corpus. Per-instance semantics
   derive from the referenced state cell; not individually executed. */

void f33_reset_latched_monitor_febe79b8(void)

{
  f33_reset_latched_monitor((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe79b8u)));
  return;
}



/* f33_reset_latched_monitor wrapper resetting exactly one monitor state ((F33LatchedMonitorState
   *)((undefined *)camry_host_ptr(0xfebe79b8u))); whole-body shape-verified from the canonical corpus. Per-instance semantics
   derive from the referenced state cell; not individually executed. */

void f33_reset_latched_monitor_febe79b8_446aa(void)

{
  f33_reset_latched_monitor((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe79b8u)));
  return;
}



void FUN_000446ba(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  if (DAT_0002bc34 == 'Z') {
    f33_reset_latched_monitor((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe79b8u)));
  }
  else if ((DAT_febe71ec >> 1 & 1) == 0) {
    f33_step_latched_monitor
              ((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe79b8u)),(F33MonitorLimits *)((undefined *)camry_host_ptr(0x2b8dcu)),
               (F33TwoSidedMonitorCallbacks *)&PTR_f33_classify_direct_source_b_00028928);
  }
  else {
    f33_retain_disabled_latched_monitor
              ((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe79b8u)),(F33MonitorLimits *)((undefined *)camry_host_ptr(0x2b8dcu)));
  }
  f33_publish_shared_condition_monitor_status(2,(*((uint *)camry_host_ptr((uint32_t)(puVar1 + -0x3e48)))));
  return;
}



/* Exact slot0/1 callback predicate. Return11/22/33/44 protocol; software source, qualification and
   retained-snapshot conditions are not physical freshness guarantees. Direct sourceB returns44 for
   any nonzero common status before inspecting8292. */

uint f33_classify_direct_source_b(void)

{
  if (f33_shared_condition_status[0] != '\0') {
    return 0x44;
  }
  if (DAT_febe8292 == 'Z') {
    return 0x22;
  }
  return 0x11;
}



/* f33_report_diagnostic_healthy_observed(0x8c); whole-body shape-verified. The literal is the
   encoded diagnostic event, not a recovered OEM name. */

void f33_report_diagnostic_healthy_observed_8c_44726(void)

{
  f33_report_diagnostic_healthy_observed(0x8c);
  return;
}



/* f33_report_diagnostic_event_failure(0x8c,10); whole-body shape-verified. The literal is the
   encoded diagnostic event, not a recovered OEM name. */

void f33_report_diagnostic_event_failure_8c_10_44736(void)

{
  f33_report_diagnostic_event_failure(0x8c,10);
  return;
}



/* f33_reset_latched_monitor wrapper resetting exactly one monitor state ((F33LatchedMonitorState
   *)((undefined *)camry_host_ptr(0xfebe79c4u))); whole-body shape-verified from the canonical corpus. Per-instance semantics
   derive from the referenced state cell; not individually executed. */

void f33_reset_latched_monitor_febe79c4(void)

{
  f33_reset_latched_monitor((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe79c4u)));
  return;
}



/* f33_reset_latched_monitor wrapper resetting exactly one monitor state ((F33LatchedMonitorState
   *)((undefined *)camry_host_ptr(0xfebe79c4u))); whole-body shape-verified from the canonical corpus. Per-instance semantics
   derive from the referenced state cell; not individually executed. */

void f33_reset_latched_monitor_febe79c4_44758(void)

{
  f33_reset_latched_monitor((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe79c4u)));
  return;
}



void FUN_00044768(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  if (DAT_0002bc38 == 'Z') {
    f33_reset_latched_monitor((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe79c4u)));
  }
  else if (((DAT_febe71ec & 3) == 0) && (DAT_febeeb85 == 'Z')) {
    f33_step_latched_monitor
              ((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe79c4u)),(F33MonitorLimits *)((undefined *)camry_host_ptr(0x2b8e0u)),
               (F33TwoSidedMonitorCallbacks *)&PTR_f33_classify_paired_shared_gate_a_0002895c);
  }
  else {
    f33_retain_disabled_latched_monitor
              ((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe79c4u)),(F33MonitorLimits *)((undefined *)camry_host_ptr(0x2b8e0u)));
  }
  f33_publish_shared_condition_monitor_status(5,(*((uint *)camry_host_ptr((uint32_t)(puVar1 + -0x3e3c)))));
  return;
}



/* Exact slot0/1 callback predicate. Return11/22/33/44 protocol; software source, qualification and
   retained-snapshot conditions are not physical freshness guarantees. PairedA fails own>6400 with
   shared<=4096 or qualifying opposite/latch condition; all three low bounds pass, remaining
   cases33. */

uint f33_classify_paired_shared_gate_a(void)

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



/* f33_report_diagnostic_healthy_observed(0xa3); whole-body shape-verified. The literal is the
   encoded diagnostic event, not a recovered OEM name. */

void f33_report_diagnostic_healthy_observed_a3_44814(void)

{
  f33_report_diagnostic_healthy_observed(0xa3);
  return;
}



/* f33_report_diagnostic_event_failure(0xa3,10); whole-body shape-verified. The literal is the
   encoded diagnostic event, not a recovered OEM name. */

void f33_report_diagnostic_event_failure_a3_10_44824(void)

{
  f33_report_diagnostic_event_failure(0xa3,10);
  return;
}



/* f33_reset_latched_monitor wrapper resetting exactly one monitor state ((F33LatchedMonitorState
   *)((undefined *)camry_host_ptr(0xfebe79d0u))); whole-body shape-verified from the canonical corpus. Per-instance semantics
   derive from the referenced state cell; not individually executed. */

void f33_reset_latched_monitor_febe79d0(void)

{
  f33_reset_latched_monitor((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe79d0u)));
  return;
}



/* f33_reset_latched_monitor wrapper resetting exactly one monitor state ((F33LatchedMonitorState
   *)((undefined *)camry_host_ptr(0xfebe79d0u))); whole-body shape-verified from the canonical corpus. Per-instance semantics
   derive from the referenced state cell; not individually executed. */

void f33_reset_latched_monitor_febe79d0_44846(void)

{
  f33_reset_latched_monitor((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe79d0u)));
  return;
}



void FUN_00044856(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  if (DAT_0002bc3c == 'Z') {
    f33_reset_latched_monitor((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe79d0u)));
  }
  else if (((DAT_febe71ec & 3) == 0) && (DAT_febeeb85 == 'Z')) {
    f33_step_latched_monitor
              ((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe79d0u)),(F33MonitorLimits *)((undefined *)camry_host_ptr(0x2b8e4u)),
               (F33TwoSidedMonitorCallbacks *)&PTR_f33_classify_paired_shared_gate_b_00028990);
  }
  else {
    f33_retain_disabled_latched_monitor
              ((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe79d0u)),(F33MonitorLimits *)((undefined *)camry_host_ptr(0x2b8e4u)));
  }
  f33_publish_shared_condition_monitor_status(6,(*((uint *)camry_host_ptr((uint32_t)(puVar1 + -0x3e30)))));
  return;
}



/* Exact slot0/1 callback predicate. Return11/22/33/44 protocol; software source, qualification and
   retained-snapshot conditions are not physical freshness guarantees. Parallel pairedB unsigned
   gate predicate with independent opposite latch; strict6400 and inclusive4096 boundaries. */

uint f33_classify_paired_shared_gate_b(void)

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



/* f33_report_diagnostic_healthy_observed(0xa6); whole-body shape-verified. The literal is the
   encoded diagnostic event, not a recovered OEM name. */

void f33_report_diagnostic_healthy_observed_a6_44902(void)

{
  f33_report_diagnostic_healthy_observed(0xa6);
  return;
}



/* f33_report_diagnostic_event_failure(0xa6,10); whole-body shape-verified. The literal is the
   encoded diagnostic event, not a recovered OEM name. */

void f33_report_diagnostic_event_failure_a6_10_44912(void)

{
  f33_report_diagnostic_event_failure(0xa6,10);
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_44924(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_44926(void)

{
  return;
}



/* Rebuild slot1 from nine statuses. Current classifier36066(2,643E)==1 OR earlier snapshot63DC==1
   selects kind0B for common confirmed fault, otherwise17. Inverse monitors7/8 affect
   actions/summary but are excluded from both channel caches. Slot1 joins ordinary/inverse monitor
   statuses with older63DC/643E snapshots. Snapshot63DC can override consumed classifier result;
   inverse7/8 excluded from channel caches but included in actions/summary. */

void f33_publish_shared_condition_monitor_actions(void)

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
  iVar5 = (int)DAT_febe643e;
  f33_retain_and_clear_fault_record(1);
  if ((((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x3e22))))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x3e20))))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x3e23))))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x3e21))))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x3e24)))))) &
      0x11) == 0x11) {
    f33_encode_fault_action_kind('\x01','\n');
  }
  if (((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x3e24))))) & 0x22) == 0x22) {
    iVar5 = FUN_00036066(2,iVar5);
    if ((iVar5 == 1) || (cVar1 == '\x01')) {
      uVar4 = '\v';
    }
    else {
      uVar4 = '\x17';
    }
    f33_encode_fault_action_kind('\x01',uVar4);
  }
  if ((((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x3e23))))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x3e21)))))) & 0x22) == 0x22) {
    f33_encode_fault_action_kind('\x01','#');
  }
  if ((((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x3e22))))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x3e20)))))) & 0x22) == 0x22) {
    f33_encode_fault_action_kind('\x01','$');
  }
  if ((((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x3e1d))))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x3e1f)))))) & 0x22) == 0x22) {
    f33_encode_fault_action_kind('\x01','\x1b');
  }
  if ((((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x3e1c))))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x3e1e)))))) & 0x22) == 0x22) {
    f33_encode_fault_action_kind('\x01','\x1c');
  }
  if (((((((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x3e23))))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x3e21)))))) & 0x22) == 0x22) && ((uVar2 & 1) == 0)) ||
      (((((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x3e22))))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x3e20)))))) & 0x22) == 0x22 && ((uVar2 >> 1 & 1) == 0)))) ||
     (((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x3e24))))) & 0x22) == 0x22)) {
    f33_encode_fault_action_kind('\x01','\n');
  }
  if ((((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x3e22))))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x3e20))))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x3e23))))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x3e21)))))) & 0x22) == 0x22) {
    f33_encode_fault_action_kind('\x01','2');
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
  f33_select_current_fault_record(1);
  uVar4 = '\0';
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x3e22))))) != '\0' ||
      ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x3e1e))))) != '\0' ||
      ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x3e20))))) != '\0' ||
      ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x3e23))))) != '\0' ||
      ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x3e1f))))) != '\0' || ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x3e21))))) != '\0' || (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x3e24))))) != '\0')))))) {
    uVar4 = '\x11';
  }
  f33_set_diagnostic_cache_blocker('\x05',uVar4);
  uVar4 = '\0';
  if ((((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x3e22))))) |
       (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x3e1e))))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x3e20))))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x3e23))))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x3e1f))))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x3e21)))))) &
      0x11) == 0x11) {
    uVar4 = 'Z';
  }
  f33_set_monitor_pending_projection('\x01',uVar4);
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x3e1b))))) = uVar6;
  return;
}



/* Unsigned index<9: publish only low status byte at79DC[index]. Index<9 publishes only the low
   packed status byte at79DC; inverse entries share this array but not all cache reductions. */

void f33_publish_shared_condition_monitor_status(uint index,uint packed)

{
  if ((index & 0xff) < 9) {
    f33_shared_condition_status[index & 0xff] = (uchar)packed;
  }
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_44b1e(void)

{
  return;
}



void FUN_00044b20(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  f33_reset_windowed_monitor((F33WindowedMonitorState *)((undefined *)camry_host_ptr(0xfebe7a00u)));
  f33_reset_windowed_monitor(((F33WindowedMonitorState *)camry_host_ptr((uint32_t)(puVar1 + -0x3df0))));
  f33_reset_windowed_monitor(((F33WindowedMonitorState *)camry_host_ptr((uint32_t)(puVar1 + -0x3de0))));
  f33_reset_windowed_monitor(((F33WindowedMonitorState *)camry_host_ptr((uint32_t)(puVar1 + -0x3dd0))));
  f33_reset_windowed_monitor(((F33WindowedMonitorState *)camry_host_ptr((uint32_t)(puVar1 + -0x3dc0))));
  f33_reset_windowed_monitor(((F33WindowedMonitorState *)camry_host_ptr((uint32_t)(puVar1 + -0x3db0))));
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x3da0)))) = 0;
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x3d9e)))) = 0;
  (*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + -0x3d9c)))) = 0;
  (*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + -0x3d98)))) = 0;
  return;
}



/* f33_report_diagnostic_healthy_observed((uint)DAT_febe7a62); whole-body shape-verified. The
   literal is the encoded diagnostic event, not a recovered OEM name. */

void f33_report_diagnostic_healthy_observed_cell_44c00(void)

{
  f33_report_diagnostic_healthy_observed((uint)DAT_febe7a62);
  return;
}



/* f33_report_diagnostic_event_failure((uint)DAT_febe7a62,10); whole-body shape-verified. The
   literal is the encoded diagnostic event, not a recovered OEM name. */

void f33_report_diagnostic_event_failure_10_44c10(void)

{
  f33_report_diagnostic_event_failure((uint)DAT_febe7a62,10);
  return;
}



void FUN_00044c22(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  f33_reset_windowed_monitor((F33WindowedMonitorState *)((undefined *)camry_host_ptr(0xfebe7a74u)));
  f33_reset_windowed_monitor(((F33WindowedMonitorState *)camry_host_ptr((uint32_t)(puVar1 + -0x3d7c))));
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x3d94)))) = 0;
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x3d92)))) = 0;
  (*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + -0x3d90)))) = 0;
  return;
}



void FUN_00044cb2(void)

{
  uint event;
  
  event = (uint)DAT_febe7a6e;
  f33_report_diagnostic_event_failure((uint)DAT_febe7a6c,10);
  f33_report_diagnostic_event_failure(event,10);
  return;
}



void FUN_00044cd0(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  f33_reset_windowed_monitor((F33WindowedMonitorState *)((undefined *)camry_host_ptr(0xfebe7a9cu)));
  f33_reset_windowed_monitor(((F33WindowedMonitorState *)camry_host_ptr((uint32_t)(puVar1 + -0x3d54))));
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x3d6c)))) = 0;
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x3d6a)))) = 0;
  (*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + -0x3d68)))) = 0;
  return;
}



void FUN_00044d60(void)

{
  uint event;
  
  event = (uint)DAT_febe7a96;
  f33_report_diagnostic_event_failure((uint)DAT_febe7a94,10);
  f33_report_diagnostic_event_failure(event,10);
  return;
}



void FUN_00044d7e(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  f33_reset_windowed_monitor((F33WindowedMonitorState *)((undefined *)camry_host_ptr(0xfebe7ac4u)));
  f33_reset_windowed_monitor(((F33WindowedMonitorState *)camry_host_ptr((uint32_t)(puVar1 + -0x3d2c))));
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x3d44)))) = 0;
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x3d42)))) = 0;
  (*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + -0x3d40)))) = 0;
  return;
}



void FUN_00044e0e(void)

{
  uint event;
  
  event = (uint)DAT_febe7abe;
  f33_report_diagnostic_event_failure((uint)DAT_febe7abc,10);
  f33_report_diagnostic_event_failure(event,10);
  return;
}



void FUN_00044e2c(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  DAT_febe7ae4 = 0;
  DAT_febe7ae6 = 0;
  f33_reset_latched_monitor((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe7ae8u)));
  f33_reset_latched_monitor(((F33LatchedMonitorState *)camry_host_ptr((uint32_t)(puVar1 + -0x3d0c))));
  f33_reset_latched_monitor(((F33LatchedMonitorState *)camry_host_ptr((uint32_t)(puVar1 + -0x3d00))));
  f33_reset_latched_monitor(((F33LatchedMonitorState *)camry_host_ptr((uint32_t)(puVar1 + -0x3cf4))));
  f33_reset_latched_monitor(((F33LatchedMonitorState *)camry_host_ptr((uint32_t)(puVar1 + -0x3ce8))));
  f33_reset_latched_monitor(((F33LatchedMonitorState *)camry_host_ptr((uint32_t)(puVar1 + -0x3cdc))));
  return;
}



/* f33_report_diagnostic_healthy_observed((uint)DAT_febe7ae4); whole-body shape-verified. The
   literal is the encoded diagnostic event, not a recovered OEM name. */

void f33_report_diagnostic_healthy_observed_cell_44ea8(void)

{
  f33_report_diagnostic_healthy_observed((uint)DAT_febe7ae4);
  return;
}



/* f33_report_diagnostic_event_failure((uint)DAT_febe7ae4,10); whole-body shape-verified. The
   literal is the encoded diagnostic event, not a recovered OEM name. */

void f33_report_diagnostic_event_failure_10_44eb8(void)

{
  f33_report_diagnostic_event_failure((uint)DAT_febe7ae4,10);
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_44eca(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_44ecc(void)

{
  return;
}



void FUN_00044ece(uint param_1,ushort *param_2)

{
  *param_2 = *param_2 | (ushort)(1 << ((int)(param_1 & 0xffff) >> 0xc));
  return;
}



void FUN_00045086(void)

{
  int iVar1;
  uint32_t puVar2;
  int iVar3;
  int iVar4;
  undefined2 uStack_6;
  
  puVar2 = 0xfebeb800u;
  iVar3 = (int)DAT_febe63e8;
  uStack_6 = DAT_febe7b34;
  iVar1 = (int)DAT_febe629e;
  if (iVar1 + 0x7fff < 0 == (-1 < iVar1 && iVar1 + 0x7fff < 0) && iVar1 != -0x7fff) {
    if (iVar1 < 0) {
      iVar1 = (int)-DAT_febe629e;
    }
  }
  else {
    iVar1 = 0x7fff;
  }
  if (iVar3 + 0x7fff < 0 == (-1 < iVar3 && iVar3 + 0x7fff < 0) && iVar3 != -0x7fff) {
    if (iVar3 < 0) {
      iVar3 = (int)-DAT_febe63e8;
    }
  }
  else {
    iVar3 = 0x7fff;
  }
  iVar4 = (int)DAT_0002b99c;
  if ((iVar3 - iVar4 < 0 == (iVar3 < 0 != iVar4 < 0 && iVar4 < 0 == iVar3 - iVar4 < 0) &&
       iVar3 != iVar4) &&
     (iVar3 = (int)DAT_0002b99e,
     iVar1 - iVar3 < 0 != (iVar1 < 0 != iVar3 < 0 && iVar3 < 0 == iVar1 - iVar3 < 0) ||
     iVar1 == iVar3)) {
    puVar2 = 0xfebeb800u;
    FUN_00044ece(DAT_febe63b8,&uStack_6);
  }
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar2 + -0x3ccc)))) = uStack_6;
  return;
}



void FUN_000450f0(void)

{
  int iVar1;
  uint32_t puVar2;
  int iVar3;
  int iVar4;
  undefined2 uStack_6;
  
  puVar2 = 0xfebeb800u;
  iVar3 = (int)DAT_febe63ec;
  uStack_6 = DAT_febe7b36;
  iVar1 = (int)DAT_febe629e;
  if (iVar1 + 0x7fff < 0 == (-1 < iVar1 && iVar1 + 0x7fff < 0) && iVar1 != -0x7fff) {
    if (iVar1 < 0) {
      iVar1 = (int)-DAT_febe629e;
    }
  }
  else {
    iVar1 = 0x7fff;
  }
  if (iVar3 + 0x7fff < 0 == (-1 < iVar3 && iVar3 + 0x7fff < 0) && iVar3 != -0x7fff) {
    if (iVar3 < 0) {
      iVar3 = (int)-DAT_febe63ec;
    }
  }
  else {
    iVar3 = 0x7fff;
  }
  iVar4 = (int)DAT_0002b99c;
  if ((iVar3 - iVar4 < 0 == (iVar3 < 0 != iVar4 < 0 && iVar4 < 0 == iVar3 - iVar4 < 0) &&
       iVar3 != iVar4) &&
     (iVar3 = (int)DAT_0002b99e,
     iVar1 - iVar3 < 0 != (iVar1 < 0 != iVar3 < 0 && iVar3 < 0 == iVar1 - iVar3 < 0) ||
     iVar1 == iVar3)) {
    puVar2 = 0xfebeb800u;
    FUN_00044ece(DAT_febe63b8,&uStack_6);
  }
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar2 + -0x3cca)))) = uStack_6;
  return;
}



void FUN_0004522e(void)

{
  FUN_0004517e();
  FUN_000451d6();
  return;
}



void FUN_0004523e(void)

{
  FUN_00045062();
  FUN_0004515a();
  FUN_0004522e();
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_45252(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_45254(void)

{
  return;
}



void FUN_00045256(void)

{
  int iVar1;
  int iVar2;
  
  if ((DAT_febe8a24 == 'Z') &&
     (f33_shared_snapshot_status[9] == '\0' &&
      (f33_shared_snapshot_status[8] == '\0' &&
      (f33_shared_snapshot_status[3] == '\0' &&
      (f33_shared_snapshot_status[2] == '\0' &&
      (f33_shared_snapshot_status[1] == '\0' && f33_shared_snapshot_status[0] == '\0')))))) {
    iVar1 = (int)DAT_febe62ba;
    iVar2 = (int)DAT_0002b9b2;
    if (iVar1 - iVar2 < 0 != (iVar1 < 0 != iVar2 < 0 && iVar2 < 0 == iVar1 - iVar2 < 0) ||
        iVar1 == iVar2) {
      DAT_febe7b48 = 0x5a;
    }
    iVar2 = (int)DAT_0002b9b0;
    if (iVar1 - iVar2 < 0 == (iVar1 < 0 != iVar2 < 0 && iVar2 < 0 == iVar1 - iVar2 < 0)) {
      DAT_febe7b49 = 0x5a;
    }
  }
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_452a4(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_452a6(void)

{
  return;
}



/* Always retain/clear slot7, then low-byte confirmed mask22 at7B4D adds kind1B and7B4C adds1D;
   select current. Any nonzero status sets diagnostic-cache blocker6=11; combined pending mask11
   sets817D[4]=5A, otherwise0. Pending and confirmed consumers differ. */

void f33_publish_local_channel_monitor_actions_a(void)

{
  uint32_t puVar1;
  uchar uVar2;
  
  puVar1 = 0xfebeb800u;
  f33_retain_and_clear_fault_record(7);
  if (((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x3cb3))))) & 0x22) == 0x22) {
    f33_encode_fault_action_kind('\a','\x1b');
  }
  if (((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x3cb4))))) & 0x22) == 0x22) {
    f33_encode_fault_action_kind('\a','\x1d');
  }
  f33_select_current_fault_record(7);
  uVar2 = '\0';
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x3cb3))))) != '\0' || (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x3cb4))))) != '\0') {
    uVar2 = '\x11';
  }
  f33_set_diagnostic_cache_blocker('\x06',uVar2);
  uVar2 = '\0';
  if ((((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x3cb3))))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x3cb4)))))) & 0x11) == 0x11) {
    uVar2 = 'Z';
  }
  f33_set_monitor_pending_projection('\x04',uVar2);
  return;
}



/* If low8(index)<2, store low8(packed_status) to FEBE7B4C+index. Other bits of the packed qualifier
   result are not published. */

void f33_publish_local_channel_a_monitor_status(uchar index,uint packed_status)

{
  if (index < 2) {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe7b4cu + (uint32_t)(index) * 1u)))) = (char)packed_status;
  }
  return;
}



/* f33_reset_latched_monitor wrapper resetting exactly one monitor state
   ((0xfebe7b50u)); whole-body shape-verified from the canonical corpus.
   Per-instance semantics derive from the referenced state cell; not individually executed. */

void f33_reset_scalar_monitor_45356(void)

{
  f33_reset_latched_monitor(((F33LatchedMonitorState *)camry_host_ptr((uint32_t)((0xfebe7b50u)))));
  return;
}



/* f33_reset_latched_monitor wrapper resetting exactly one monitor state
   ((0xfebe7b50u)); whole-body shape-verified from the canonical corpus.
   Per-instance semantics derive from the referenced state cell; not individually executed. */

void f33_reset_scalar_monitor_45356_45346(void)

{
  f33_reset_latched_monitor(((F33LatchedMonitorState *)camry_host_ptr((uint32_t)((0xfebe7b50u)))));
  return;
}



/* State7B50 -> slot7 index1. Qualification6764.bit0 holds confirmed state via6AE18; otherwise
   predicate requires6624.bit0 and65F6=5A, then8284=5A fails. Limits200/200; event8E. Policy2BC54=0
   in this image. */

void f33_step_local_output_status_a_monitor(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  if (DAT_0002bc54 == 'Z') {
    f33_reset_latched_monitor(((F33LatchedMonitorState *)camry_host_ptr((uint32_t)((0xfebe7b50u)))));
  }
  else if ((DAT_febe6764 & 1) == 0) {
    f33_step_latched_monitor
              (((F33LatchedMonitorState *)camry_host_ptr((uint32_t)((0xfebe7b50u)))), ((F33MonitorLimits *)camry_host_ptr((uint32_t)((0x2b9b4u)))), ((F33TwoSidedMonitorCallbacks *)camry_host_ptr((uint32_t)((0x28ac8u)))));
  }
  else {
    f33_retain_disabled_latched_monitor
              (((F33LatchedMonitorState *)camry_host_ptr((uint32_t)((0xfebe7b50u)))), ((F33MonitorLimits *)camry_host_ptr((uint32_t)((0x2b9b4u)))));
  }
  f33_publish_local_channel_a_monitor_status('\x01',(*((uint *)camry_host_ptr((uint32_t)(puVar1 + -0x3cb0)))));
  return;
}



/* 6624.bit0 and65F6=5A admit;8284=5A returns22,otherwise11; inadmissible44.8284 is staged
   local383A.bit3. */

uint f33_classify_local_output_status_a(void)

{
  if (((DAT_febe6624 & 1) != 0) && (DAT_febe65f6 == 'Z')) {
    if (DAT_febe8284 == 'Z') {
      return 0x22;
    }
    return 0x11;
  }
  return 0x44;
}



/* Report event8E through51E2C/52A2A healthy-observed bitmap; does not clear current failure
   history. */

void f33_report_scalar_event_8e_healthy_observed(void)

{
  f33_report_diagnostic_healthy_observed(0x8e);
  return;
}



/* Report event8E with capture kind50; diagnostic admission remains in51C66. */

void f33_report_scalar_event_8e_failure(void)

{
  f33_report_diagnostic_event_failure(0x8e,0x32);
  return;
}



/* f33_reset_latched_monitor wrapper resetting exactly one monitor state
   ((0xfebe7b5cu)); whole-body shape-verified from the canonical corpus.
   Per-instance semantics derive from the referenced state cell; not individually executed. */

void f33_reset_scalar_monitor_45410(void)

{
  f33_reset_latched_monitor(((F33LatchedMonitorState *)camry_host_ptr((uint32_t)((0xfebe7b5cu)))));
  return;
}



/* f33_reset_latched_monitor wrapper resetting exactly one monitor state
   ((0xfebe7b5cu)); whole-body shape-verified from the canonical corpus.
   Per-instance semantics derive from the referenced state cell; not individually executed. */

void f33_reset_scalar_monitor_45410_45400(void)

{
  f33_reset_latched_monitor(((F33LatchedMonitorState *)camry_host_ptr((uint32_t)((0xfebe7b5cu)))));
  return;
}



/* State7B5C -> slot7 index0. Requires qualification bit0 clear andE820=5A; predicate
   requires64DC.bit1/64D4.bit1 clear and65F6=5A, then8282=5A fails. Limits16/16; event77. Disabled
   gate preserves confirmed state. */

void f33_step_local_channel_mismatch_a_monitor(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  if (DAT_0002bc58 == 'Z') {
    f33_reset_latched_monitor(((F33LatchedMonitorState *)camry_host_ptr((uint32_t)((0xfebe7b5cu)))));
  }
  else if (((DAT_febe6764 & 1) == 0) && (DAT_febee820 == 'Z')) {
    f33_step_latched_monitor
              (((F33LatchedMonitorState *)camry_host_ptr((uint32_t)((0xfebe7b5cu)))), ((F33MonitorLimits *)camry_host_ptr((uint32_t)((0x2b9b8u)))), ((F33TwoSidedMonitorCallbacks *)camry_host_ptr((uint32_t)((0x28afcu)))));
  }
  else {
    f33_retain_disabled_latched_monitor
              (((F33LatchedMonitorState *)camry_host_ptr((uint32_t)((0xfebe7b5cu)))), ((F33MonitorLimits *)camry_host_ptr((uint32_t)((0x2b9b8u)))));
  }
  f33_publish_local_channel_a_monitor_status('\0',(*((uint *)camry_host_ptr((uint32_t)(puVar1 + -0x3ca4)))));
  return;
}



/* 64DC.bit1/64D4.bit1 clear and65F6=5A admit;8282=5A fails22 else11; inadmissible44.8282 is
   local383A.bit9. */

uint f33_classify_local_channel_mismatch_a(void)

{
  if (((((byte)DAT_febe64dc & 2) == 0) && (((byte)DAT_febe64d4 & 2) == 0)) && (DAT_febe65f6 == 'Z'))
  {
    if (DAT_febe8282 == 'Z') {
      return 0x22;
    }
    return 0x11;
  }
  return 0x44;
}



/* Report event77 through51E2C/52A2A healthy-observed bitmap; does not clear current failure
   history. */

void f33_report_scalar_event_77_healthy_observed(void)

{
  f33_report_diagnostic_healthy_observed(0x77);
  return;
}



/* Report event77 with capture kind50; diagnostic admission remains in51C66. */

void f33_report_scalar_event_77_failure(void)

{
  f33_report_diagnostic_event_failure(0x77,0x32);
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_454c0(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_454c2(void)

{
  return;
}



/* Rebuild slot8 from7B69 kind1C and7B68 kind1E. Any nonzero sets blocker7=11; pending mask11
   sets817D[5]=5A. Current selected even when no action remains. */

void f33_publish_local_channel_monitor_actions_b(void)

{
  uint32_t puVar1;
  uchar uVar2;
  
  puVar1 = 0xfebeb800u;
  f33_retain_and_clear_fault_record(8);
  if (((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x3c97))))) & 0x22) == 0x22) {
    f33_encode_fault_action_kind('\b','\x1c');
  }
  if (((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x3c98))))) & 0x22) == 0x22) {
    f33_encode_fault_action_kind('\b','\x1e');
  }
  f33_select_current_fault_record(8);
  uVar2 = '\0';
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x3c97))))) != '\0' || (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x3c98))))) != '\0') {
    uVar2 = '\x11';
  }
  f33_set_diagnostic_cache_blocker('\a',uVar2);
  uVar2 = '\0';
  if ((((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x3c97))))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x3c98)))))) & 0x11) == 0x11) {
    uVar2 = 'Z';
  }
  f33_set_monitor_pending_projection('\x05',uVar2);
  return;
}



/* If low8(index)<2, store low8(packed_status) to FEBE7B68+index. Other bits of the packed qualifier
   result are not published. */

void f33_publish_local_channel_b_monitor_status(uchar index,uint packed_status)

{
  if (index < 2) {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe7b68u + (uint32_t)(index) * 1u)))) = (char)packed_status;
  }
  return;
}



/* f33_reset_latched_monitor wrapper resetting exactly one monitor state
   ((0xfebe7b6cu)); whole-body shape-verified from the canonical corpus.
   Per-instance semantics derive from the referenced state cell; not individually executed. */

void f33_reset_scalar_monitor_45572(void)

{
  f33_reset_latched_monitor(((F33LatchedMonitorState *)camry_host_ptr((uint32_t)((0xfebe7b6cu)))));
  return;
}



/* f33_reset_latched_monitor wrapper resetting exactly one monitor state
   ((0xfebe7b6cu)); whole-body shape-verified from the canonical corpus.
   Per-instance semantics derive from the referenced state cell; not individually executed. */

void f33_reset_scalar_monitor_45572_45562(void)

{
  f33_reset_latched_monitor(((F33LatchedMonitorState *)camry_host_ptr((uint32_t)((0xfebe7b6cu)))));
  return;
}



/* State7B6C -> slot8 index1. Qualification6764.bit1 holds confirmed state; predicate
   requires6624.bit1 and65F7=5A, then8283=5A fails. Limits200/200; event8F. */

void f33_step_local_output_status_b_monitor(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  if (DAT_0002bc5c == 'Z') {
    f33_reset_latched_monitor(((F33LatchedMonitorState *)camry_host_ptr((uint32_t)((0xfebe7b6cu)))));
  }
  else if ((DAT_febe6764 >> 1 & 1) == 0) {
    f33_step_latched_monitor
              (((F33LatchedMonitorState *)camry_host_ptr((uint32_t)((0xfebe7b6cu)))), ((F33MonitorLimits *)camry_host_ptr((uint32_t)((0x2b9bcu)))), ((F33TwoSidedMonitorCallbacks *)camry_host_ptr((uint32_t)((0x28b30u)))));
  }
  else {
    f33_retain_disabled_latched_monitor
              (((F33LatchedMonitorState *)camry_host_ptr((uint32_t)((0xfebe7b6cu)))), ((F33MonitorLimits *)camry_host_ptr((uint32_t)((0x2b9bcu)))));
  }
  f33_publish_local_channel_b_monitor_status('\x01',(*((uint *)camry_host_ptr((uint32_t)(puVar1 + -0x3c94)))));
  return;
}



/* 6624.bit1 and65F7=5A admit;8283=5A fails22 else11; inadmissible44.8283 is local383A.bit2. */

uint f33_classify_local_output_status_b(void)

{
  if ((((byte)DAT_febe6624 & 2) != 0) && (DAT_febe65f7 == 'Z')) {
    if (DAT_febe8283 == 'Z') {
      return 0x22;
    }
    return 0x11;
  }
  return 0x44;
}



/* Report event8F through51E2C/52A2A healthy-observed bitmap; does not clear current failure
   history. */

void f33_report_scalar_event_8f_healthy_observed(void)

{
  f33_report_diagnostic_healthy_observed(0x8f);
  return;
}



/* Report event8F with capture kind50; diagnostic admission remains in51C66. */

void f33_report_scalar_event_8f_failure(void)

{
  f33_report_diagnostic_event_failure(0x8f,0x32);
  return;
}



/* f33_reset_latched_monitor wrapper resetting exactly one monitor state
   ((0xfebe7b78u)); whole-body shape-verified from the canonical corpus.
   Per-instance semantics derive from the referenced state cell; not individually executed. */

void f33_reset_scalar_monitor_4562a(void)

{
  f33_reset_latched_monitor(((F33LatchedMonitorState *)camry_host_ptr((uint32_t)((0xfebe7b78u)))));
  return;
}



/* f33_reset_latched_monitor wrapper resetting exactly one monitor state
   ((0xfebe7b78u)); whole-body shape-verified from the canonical corpus.
   Per-instance semantics derive from the referenced state cell; not individually executed. */

void f33_reset_scalar_monitor_4562a_4561a(void)

{
  f33_reset_latched_monitor(((F33LatchedMonitorState *)camry_host_ptr((uint32_t)((0xfebe7b78u)))));
  return;
}



/* State7B78 -> slot8 index0. Requires qualification bit1 clear andE820=5A; predicate
   requires64DC.bit17/64D4.bit17 clear and65F7=5A, then8281=5A fails. Limits16/16; event73. */

void f33_step_local_channel_mismatch_b_monitor(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  if (DAT_0002bc60 == 'Z') {
    f33_reset_latched_monitor(((F33LatchedMonitorState *)camry_host_ptr((uint32_t)((0xfebe7b78u)))));
  }
  else if (((DAT_febe6764 >> 1 & 1) == 0) && (DAT_febee820 == 'Z')) {
    f33_step_latched_monitor
              (((F33LatchedMonitorState *)camry_host_ptr((uint32_t)((0xfebe7b78u)))), ((F33MonitorLimits *)camry_host_ptr((uint32_t)((0x2b9c0u)))), ((F33TwoSidedMonitorCallbacks *)camry_host_ptr((uint32_t)((0x28b64u)))));
  }
  else {
    f33_retain_disabled_latched_monitor
              (((F33LatchedMonitorState *)camry_host_ptr((uint32_t)((0xfebe7b78u)))), ((F33MonitorLimits *)camry_host_ptr((uint32_t)((0x2b9c0u)))));
  }
  f33_publish_local_channel_b_monitor_status('\0',(*((uint *)camry_host_ptr((uint32_t)(puVar1 + -0x3c88)))));
  return;
}



/* Report event73 through51E2C/52A2A healthy-observed bitmap; does not clear current failure
   history. */

void f33_report_scalar_event_73_healthy_observed(void)

{
  f33_report_diagnostic_healthy_observed(0x73);
  return;
}



/* Report event73 with capture kind50; diagnostic admission remains in51C66. */

void f33_report_scalar_event_73_failure(void)

{
  f33_report_diagnostic_event_failure(0x73,0x32);
  return;
}



/* f33_reset_recoverable_monitor wrapper resetting exactly one monitor state
   ((0xfebe7b84u)); whole-body shape-verified from the canonical corpus.
   Per-instance semantics derive from the referenced state cell; not individually executed. */

void f33_reset_scalar_monitor_456fa(void)

{
  f33_reset_recoverable_monitor(((F33RecoverableMonitorState *)camry_host_ptr((uint32_t)((0xfebe7b84u)))));
  return;
}



/* f33_reset_recoverable_monitor wrapper resetting exactly one monitor state
   ((0xfebe7b84u)); whole-body shape-verified from the canonical corpus.
   Per-instance semantics derive from the referenced state cell; not individually executed. */

void f33_reset_scalar_monitor_456fa_456ea(void)

{
  f33_reset_recoverable_monitor(((F33RecoverableMonitorState *)camry_host_ptr((uint32_t)((0xfebe7b84u)))));
  return;
}



/* State7B84 -> slot6 index3. E820 admits recoverable qualifier with limits25/125/25. Reset/disabled
   gate also clears admission count6868. Predicate relates E822/E823, receive803C/803E and
   unsigned66B8; eventA5. */

void f33_step_admitted_scalar_receive_condition_monitor(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  if (DAT_0002bc64 == 'Z') {
    DAT_febe6868 = 0;
    f33_reset_recoverable_monitor(((F33RecoverableMonitorState *)camry_host_ptr((uint32_t)((0xfebe7b84u)))));
  }
  else if (DAT_febee820 == 'Z') {
    f33_step_recoverable_monitor
              (((F33RecoverableMonitorState *)camry_host_ptr((uint32_t)((0xfebe7b84u)))), ((F33RecoverableMonitorLimits *)camry_host_ptr((uint32_t)((0x2b9c4u)))), ((F33RecoverableMonitorCallbacks *)camry_host_ptr((uint32_t)((0x28b98u)))));
  }
  else {
    DAT_febe6868 = 0;
    f33_retain_disabled_recoverable_monitor
              (((F33RecoverableMonitorState *)camry_host_ptr((uint32_t)((0xfebe7b84u)))), ((F33RecoverableMonitorLimits *)camry_host_ptr((uint32_t)((0x2b9c4u)))));
  }
  f33_publish_scalar_relation_monitor_status('\x03',(*((uint *)camry_host_ptr((uint32_t)(puVar1 + -0x3c7c)))));
  return;
}



/* With E822=5A/E823=0, increment6868 until entry count11. Thereafter803C=1 and803E=0 fails22.
   Strict2304<66B8<4096 returns11; outside gives33 after admitted delay,44 before it. Inactive gate
   resets6868. Inputs and comparisons are unsigned. */

uint f33_classify_admitted_scalar_receive_condition(void)

{
  if ((DAT_febee822 == 'Z') && (DAT_febee823 == '\0')) {
    if (DAT_0002b9d8 <= DAT_febe6868) {
      if ((DAT_febe803c == '\x01') && (DAT_febe803e == '\0')) {
        return 0x22;
      }
      if ((DAT_febe66b8 < DAT_0002b9de) && (DAT_0002b9e0 < DAT_febe66b8)) {
        return 0x11;
      }
      return 0x33;
    }
    DAT_febe6868 = DAT_febe6868 + 1;
  }
  else {
    DAT_febe6868 = 0;
  }
  if ((DAT_febe66b8 < DAT_0002b9de) && (DAT_0002b9e0 < DAT_febe66b8)) {
    return 0x11;
  }
  return 0x44;
}



/* Strict2304<66B8<4096 returns11; endpoints and outside return22. Recovery count is separate from
   admission6868. */

uint f33_classify_scalar_receive_recovery(void)

{
  if ((DAT_febe66b8 < DAT_0002b9da) && (DAT_0002b9dc < DAT_febe66b8)) {
    return 0x11;
  }
  return 0x22;
}



/* Report eventA5 through51E2C/52A2A healthy-observed bitmap; does not clear current failure
   history. */

void f33_report_scalar_event_a5_healthy_observed(void)

{
  f33_report_diagnostic_healthy_observed(0xa5);
  return;
}



/* Clear admission counter6868 before reporting eventA5 with capture kind400; diagnostic rejection
   does not undo that clear. */

void f33_report_scalar_event_a5_failure(void)

{
  DAT_febe6868 = 0;
  f33_report_diagnostic_event_failure(0xa5,400);
  return;
}



/* Report eventA5 through51D5E ordinary pass; current failure clears while normal retained histories
   survive. */

void f33_report_scalar_event_a5_pass(void)

{
  f33_report_diagnostic_event_pass(0xa5);
  return;
}



/* f33_reset_recoverable_monitor wrapper resetting exactly one monitor state
   ((0xfebe7b90u)); whole-body shape-verified from the canonical corpus.
   Per-instance semantics derive from the referenced state cell; not individually executed. */

void f33_reset_scalar_monitor_45838(void)

{
  f33_reset_recoverable_monitor(((F33RecoverableMonitorState *)camry_host_ptr((uint32_t)((0xfebe7b90u)))));
  return;
}



/* f33_reset_recoverable_monitor wrapper resetting exactly one monitor state
   ((0xfebe7b90u)); whole-body shape-verified from the canonical corpus.
   Per-instance semantics derive from the referenced state cell; not individually executed. */

void f33_reset_scalar_monitor_45838_45828(void)

{
  f33_reset_recoverable_monitor(((F33RecoverableMonitorState *)camry_host_ptr((uint32_t)((0xfebe7b90u)))));
  return;
}



/* State7B90 -> slot6 index0. Requires qualification bits0/1 clear andE820=5A, otherwise retain
   confirmed state. Relation predicate uses unsigned66B8 against66AE/66B0 plus source-status gates.
   Recoverable limits125/125/25; eventA2. */

void f33_step_paired_scalar_relation_monitor(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  if (DAT_0002bc68 == 'Z') {
    f33_reset_recoverable_monitor(((F33RecoverableMonitorState *)camry_host_ptr((uint32_t)((0xfebe7b90u)))));
  }
  else if (((DAT_febe6764 & 3) == 0) && (DAT_febee820 == 'Z')) {
    f33_step_recoverable_monitor
              (((F33RecoverableMonitorState *)camry_host_ptr((uint32_t)((0xfebe7b90u)))), ((F33RecoverableMonitorLimits *)camry_host_ptr((uint32_t)((0x2b9cau)))), ((F33RecoverableMonitorCallbacks *)camry_host_ptr((uint32_t)((0x28bd4u)))));
  }
  else {
    f33_retain_disabled_recoverable_monitor
              (((F33RecoverableMonitorState *)camry_host_ptr((uint32_t)((0xfebe7b90u)))), ((F33RecoverableMonitorLimits *)camry_host_ptr((uint32_t)((0x2b9cau)))));
  }
  f33_publish_scalar_relation_monitor_status('\0',(*((uint *)camry_host_ptr((uint32_t)(puVar1 + -0x3c70)))));
  return;
}



/* Any6751/52 or65C2/3/4/5 nonzero returns44. Otherwise66B8>4736 and either66AE/66B0<=4096
   returns22;66B8<=4736 and either peer<=4096 returns11; other combinations33. All raw values
   unsigned. */

uint f33_classify_paired_scalar_relation(void)

{
  if (DAT_febe6752 != '\0' ||
      (DAT_febe6751 != '\0' ||
      (DAT_febe65c4 != '\0' ||
      (DAT_febe65c3 != '\0' || (DAT_febe65c2 != '\0' || DAT_febe65c5 != '\0'))))) {
    return 0x44;
  }
  if ((DAT_0002b9e4 < DAT_febe66b8) &&
     ((DAT_febe66ae <= DAT_0002b9e8 || (DAT_febe66b0 <= DAT_0002b9ea)))) {
    return 0x22;
  }
  if ((DAT_febe66b8 <= DAT_0002b9ee) &&
     ((DAT_febe66ae <= DAT_0002b9f0 || (DAT_febe66b0 <= DAT_0002b9f2)))) {
    return 0x11;
  }
  return 0x33;
}



/* Same six source-status gates; then inclusive768<=66B8<=4096 returns11,otherwise22. This is not
   the entry predicate range. */

uint f33_classify_paired_scalar_recovery(void)

{
  if (DAT_febe6752 != '\0' ||
      (DAT_febe6751 != '\0' ||
      (DAT_febe65c4 != '\0' ||
      (DAT_febe65c3 != '\0' || (DAT_febe65c2 != '\0' || DAT_febe65c5 != '\0'))))) {
    return 0x44;
  }
  if ((DAT_febe66b8 <= DAT_0002b9e6) && (DAT_0002b9ec <= DAT_febe66b8)) {
    return 0x11;
  }
  return 0x22;
}



/* Report eventA2 through51E2C/52A2A healthy-observed bitmap; does not clear current failure
   history. */

void f33_report_scalar_event_a2_healthy_observed(void)

{
  f33_report_diagnostic_healthy_observed(0xa2);
  return;
}



/* Report eventA2 with capture kind400; diagnostic admission remains in51C66. */

void f33_report_scalar_event_a2_failure(void)

{
  f33_report_diagnostic_event_failure(0xa2,400);
  return;
}



/* Report eventA2 through51D5E ordinary pass; current failure clears while normal retained histories
   survive. */

void f33_report_scalar_event_a2_pass(void)

{
  f33_report_diagnostic_event_pass(0xa2);
  return;
}



/* f33_reset_latched_monitor wrapper resetting exactly one monitor state
   ((0xfebe7b9cu)); whole-body shape-verified from the canonical corpus.
   Per-instance semantics derive from the referenced state cell; not individually executed. */

void f33_reset_scalar_monitor_4599c(void)

{
  f33_reset_latched_monitor(((F33LatchedMonitorState *)camry_host_ptr((uint32_t)((0xfebe7b9cu)))));
  return;
}



/* f33_reset_latched_monitor wrapper resetting exactly one monitor state
   ((0xfebe7b9cu)); whole-body shape-verified from the canonical corpus.
   Per-instance semantics derive from the referenced state cell; not individually executed. */

void f33_reset_scalar_monitor_4599c_4598c(void)

{
  f33_reset_latched_monitor(((F33LatchedMonitorState *)camry_host_ptr((uint32_t)((0xfebe7b9cu)))));
  return;
}



/* State7B9C -> slot6 index1. Only qualification bit1 SET andE820=5A runs qualifier. Otherwise
   report healthy-observed9E without clearing retained monitor state, then publish its low status
   byte. Limits0/125; confirmed failure is latched until explicit reset. */

void f33_step_qualified_scalar_relation_a_monitor(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  if (DAT_0002bc6c == 'Z') {
    f33_reset_latched_monitor(((F33LatchedMonitorState *)camry_host_ptr((uint32_t)((0xfebe7b9cu)))));
  }
  else if (((DAT_febe6764 >> 1 & 1) == 0) || (DAT_febee820 != 'Z')) {
    f33_report_diagnostic_healthy_observed(0x9e);
  }
  else {
    f33_step_latched_monitor
              (((F33LatchedMonitorState *)camry_host_ptr((uint32_t)((0xfebe7b9cu)))), ((F33MonitorLimits *)camry_host_ptr((uint32_t)((0x2b9d0u)))), ((F33TwoSidedMonitorCallbacks *)camry_host_ptr((uint32_t)((0x28c10u)))));
  }
  f33_publish_scalar_relation_monitor_status('\x01',(*((uint *)camry_host_ptr((uint32_t)(puVar1 + -0x3c64)))));
  return;
}



/* 6751 or65C2/4/5 nonzero returns44; otherwise unsigned66B8>4736 and66AE<=4096 returns22,else11. */

uint f33_classify_qualified_scalar_relation_a(void)

{
  if (DAT_febe6751 != '\0' ||
      (DAT_febe65c4 != '\0' || (DAT_febe65c2 != '\0' || DAT_febe65c5 != '\0'))) {
    return 0x44;
  }
  if ((DAT_0002b9f4 < DAT_febe66b8) && (DAT_febe66ae <= DAT_0002b9f6)) {
    return 0x22;
  }
  return 0x11;
}



/* Report event9E with capture kind400; diagnostic admission remains in51C66. */

void f33_report_scalar_event_9e_failure(void)

{
  f33_report_diagnostic_event_failure(0x9e,400);
  return;
}



/* f33_reset_latched_monitor wrapper resetting exactly one monitor state
   ((0xfebe7ba8u)); whole-body shape-verified from the canonical corpus.
   Per-instance semantics derive from the referenced state cell; not individually executed. */

void f33_reset_scalar_monitor_45a6c(void)

{
  f33_reset_latched_monitor(((F33LatchedMonitorState *)camry_host_ptr((uint32_t)((0xfebe7ba8u)))));
  return;
}



/* f33_reset_latched_monitor wrapper resetting exactly one monitor state
   ((0xfebe7ba8u)); whole-body shape-verified from the canonical corpus.
   Per-instance semantics derive from the referenced state cell; not individually executed. */

void f33_reset_scalar_monitor_45a6c_45a5c(void)

{
  f33_reset_latched_monitor(((F33LatchedMonitorState *)camry_host_ptr((uint32_t)((0xfebe7ba8u)))));
  return;
}



/* State7BA8 -> slot6 index2. Only qualification bit0 SET andE820=5A runs qualifier. Otherwise
   healthy-observed9F leaves retained state unchanged. Limits0/125; raw source66B0 replaces66AE. */

void f33_step_qualified_scalar_relation_b_monitor(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  if (DAT_0002bc70 == 'Z') {
    f33_reset_latched_monitor(((F33LatchedMonitorState *)camry_host_ptr((uint32_t)((0xfebe7ba8u)))));
  }
  else if (((DAT_febe6764 & 1) == 0) || (DAT_febee820 != 'Z')) {
    f33_report_diagnostic_healthy_observed(0x9f);
  }
  else {
    f33_step_latched_monitor
              (((F33LatchedMonitorState *)camry_host_ptr((uint32_t)((0xfebe7ba8u)))), ((F33MonitorLimits *)camry_host_ptr((uint32_t)((0x2b9d4u)))), ((F33TwoSidedMonitorCallbacks *)camry_host_ptr((uint32_t)((0x28c44u)))));
  }
  f33_publish_scalar_relation_monitor_status('\x02',(*((uint *)camry_host_ptr((uint32_t)(puVar1 + -0x3c58)))));
  return;
}



/* 6752 or65C3/4/5 nonzero returns44; otherwise unsigned66B8>4736 and66B0<=4096 returns22,else11. */

uint f33_classify_qualified_scalar_relation_b(void)

{
  if (DAT_febe6752 != '\0' ||
      (DAT_febe65c4 != '\0' || (DAT_febe65c3 != '\0' || DAT_febe65c5 != '\0'))) {
    return 0x44;
  }
  if ((DAT_0002b9f8 < DAT_febe66b8) && (DAT_febe66b0 <= DAT_0002b9fa)) {
    return 0x22;
  }
  return 0x11;
}



/* Report event9F with capture kind400; diagnostic admission remains in51C66. */

void f33_report_scalar_event_9f_failure(void)

{
  f33_report_diagnostic_event_failure(0x9f,400);
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_45b1c(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_45b1e(void)

{
  return;
}



/* Always rebuild slot6; OR7BB4..7BB7 with mask22 selects kind16.7BB8 is any nonzero
   status;7BB9/7BBA are confirmed indices0/3 respectively. General blocking is not the same as
   either endpoint-specific flag. Native four-worker scheduler composition publishes retained slot6
   failure/action despite healthy-observed notifications; current diagnostic failure remains set. */

void f33_publish_scalar_relation_monitor_actions(void)

{
  uint32_t puVar1;
  undefined1 uVar2;
  undefined1 uVar3;
  undefined1 uVar4;
  
  puVar1 = 0xfebeb800u;
  f33_retain_and_clear_fault_record(6);
  if ((((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x3c49))))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x3c4a))))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x3c4b))))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x3c4c)))))) & 0x22) == 0x22) {
    f33_encode_fault_action_kind('\x06','\x16');
  }
  uVar4 = 0;
  if ((((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x3c4b))))) != '\0' || (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x3c4c))))) != 0) || (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x3c4a))))) != '\0') ||
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x3c49))))) != 0) {
    uVar4 = 0x5a;
  }
  uVar3 = 0;
  if (((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x3c4c))))) & 0x22) == 0x22) {
    uVar3 = 0x5a;
  }
  uVar2 = 0;
  if (((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x3c49))))) & 0x22) == 0x22) {
    uVar2 = 0x5a;
  }
  f33_select_current_fault_record(6);
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x3c48))))) = uVar4;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x3c47))))) = uVar3;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x3c46))))) = uVar2;
  return;
}



/* If low8(index)<4, store low8(packed_status) to FEBE7BB4+index. Other bits of the packed qualifier
   result are not published. */

void f33_publish_scalar_relation_monitor_status(uchar index,uint packed_status)

{
  if (index < 4) {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe7bb4u + (uint32_t)(index) * 1u)))) = (char)packed_status;
  }
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_45bb0(void)

{
  return;
}



/* Constant-block fill: 8 literal assignments into one contiguous cell block; shape-verified.
   Literals are default/reset values; cell meanings are not recovered. */

void f33_fill_constant_block_45bb2(void)

{
  DAT_febe7bbc = 0;
  DAT_febe7bbd = 0;
  DAT_febe7bbe = 0;
  DAT_febe7bbf = 0;
  DAT_febe7bc0 = 0;
  DAT_febe7bc1 = 0;
  DAT_febe7bc2 = 0;
  DAT_febe7bc3 = 0;
  return;
}



/* Unsigned7DB0>=2125 sets7BBC=5A; inclusive2125..4736 sets7BBD=5A. Below lower bound clears both;
   above upper retains7BBC but clears7BBD. */

void f33_publish_primary_scalar_availability(void)

{
  if (DAT_febe7db0 < DAT_0002b9fe) {
    DAT_febe7bbd = 0;
    DAT_febe7bbc = 0;
  }
  else {
    DAT_febe7bbd = 0x5a;
    DAT_febe7bbc = 0x5a;
    if (DAT_0002b9fc < DAT_febe7db0) {
      DAT_febe7bbd = 0;
    }
  }
  return;
}



/* Unsigned7DA6>=1818 sets7BC0=5A;>=2125 additionally7BBE=5A. No upper bound in this helper. */

void f33_publish_channel_scalar_availability_a(void)

{
  if (DAT_febe7da6 < DAT_0002ba08) {
    DAT_febe7bbe = 0;
    DAT_febe7bc0 = 0;
  }
  else {
    DAT_febe7bbe = 0x5a;
    DAT_febe7bc0 = 0x5a;
    if (DAT_febe7da6 < DAT_0002ba04) {
      DAT_febe7bbe = 0;
    }
  }
  return;
}



/* Unsigned7DA8>=1818 sets7BC1=5A;>=2125 additionally7BBF=5A. No upper bound in this helper. */

void f33_publish_channel_scalar_availability_b(void)

{
  if (DAT_febe7da8 < DAT_0002ba08) {
    DAT_febe7bbf = 0;
    DAT_febe7bc1 = 0;
  }
  else {
    DAT_febe7bbf = 0x5a;
    DAT_febe7bc1 = 0x5a;
    if (DAT_febe7da8 < DAT_0002ba04) {
      DAT_febe7bbf = 0;
    }
  }
  return;
}



/* 7BC2/3=5A if primary7DB0 OR respective7DA6/7DA8 is inside inclusive2125..4736. EB85 selects
   alternate ROM lower-bound entries, but both equal2125 in this exact image. Later5D6DC
   publishes65F6/7. */

void f33_publish_paired_scalar_availability(void)

{
  ushort uVar1;
  ushort uVar2;
  
  uVar1 = DAT_0002ba04;
  uVar2 = DAT_0002b9fe;
  if (DAT_febeeb85 == 'Z') {
    uVar1 = DAT_0002ba06;
    uVar2 = DAT_0002ba00;
  }
  if (((DAT_febe7db0 < uVar2) || (DAT_0002b9fc < DAT_febe7db0)) &&
     ((DAT_febe7da6 < uVar1 || (DAT_0002ba02 < DAT_febe7da6)))) {
    DAT_febe7bc2 = 0;
  }
  else {
    DAT_febe7bc2 = 0x5a;
  }
  if (((DAT_febe7db0 < uVar2) || (DAT_0002b9fc < DAT_febe7db0)) &&
     ((DAT_febe7da8 < uVar1 || (DAT_0002ba02 < DAT_febe7da8)))) {
    DAT_febe7bc3 = 0;
  }
  else {
    DAT_febe7bc3 = 0x5a;
  }
  return;
}



/* Run primary,channelA,channelB andpaired availability publishers in that order. Their destination
   bank7BBC..7BC3 is distinct from the later65F0..65F7 snapshot. */

void f33_update_scalar_availability(void)

{
  f33_publish_primary_scalar_availability();
  f33_publish_channel_scalar_availability_a();
  f33_publish_channel_scalar_availability_b();
  f33_publish_paired_scalar_availability();
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_45cca(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_45ccc(void)

{
  return;
}



/* Retain/clear slot21, select its empty current record, clear diagnostic-cache blocker10. No
   monitor predicate or fault action is produced here. */

void f33_clear_reserved_monitor_action_slot(void)

{
  f33_retain_and_clear_fault_record(0x15);
  f33_select_current_fault_record(0x15);
  f33_set_diagnostic_cache_blocker('\n','\0');
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_45cfa(void)

{
  return;
}



void FUN_00045e12(void)

{
  undefined2 local_1c;
  undefined2 uStack_1a;
  undefined4 uStack_18;
  undefined1 uStack_14;
  undefined1 uStack_13;
  undefined2 uStack_12;
  undefined4 uStack_10;
  undefined1 uStack_c;
  undefined1 uStack_b;
  undefined2 uStack_a;
  undefined4 uStack_8;
  
  DAT_febe7bcc = 0;
  DAT_febe7bc9 = 0;
  DAT_febe7bd0 = 0;
  DAT_febe7bd4 = 0;
  local_1c = 0;
  uStack_14 = 0;
  uStack_12 = 0;
  uStack_10 = 0;
  DAT_febe7bce = 0;
  DAT_febe7bca = 0;
  DAT_febe7bd2 = 0;
  DAT_febe7bd8 = 0;
  uStack_1a = 0;
  uStack_c = 0;
  uStack_a = 0;
  uStack_8 = 0;
  uStack_18 = 0;
  uStack_13 = 0;
  uStack_b = 0;
  f33_nvm_set_record(0xc,(uint *)&local_1c);
  return;
}



/* f33_reset_recoverable_monitor wrapper resetting exactly one monitor state
   ((0xfebe7bdcu)); whole-body shape-verified from the canonical corpus.
   Per-instance semantics derive from the referenced state cell; not individually executed. */

void f33_reset_scalar_monitor_45e74(void)

{
  f33_reset_recoverable_monitor(((F33RecoverableMonitorState *)camry_host_ptr((uint32_t)((0xfebe7bdcu)))));
  return;
}



/* f33_reset_recoverable_monitor wrapper resetting exactly one monitor state
   ((0xfebe7bdcu)); whole-body shape-verified from the canonical corpus.
   Per-instance semantics derive from the referenced state cell; not individually executed. */

void f33_reset_scalar_monitor_45e74_45e64(void)

{
  f33_reset_recoverable_monitor(((F33RecoverableMonitorState *)camry_host_ptr((uint32_t)((0xfebe7bdcu)))));
  return;
}



/* State7BDC -> slot18 index0. Qualification bit0 clear admits recoverable qualifier; otherwise
   retain confirmed state. Raw unsigned6492 range1206..65231 inclusive. Pass/fail/recovery
   limits25/25/25; event88. */

void f33_step_raw_thermistor_range_a_monitor(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  if (DAT_0002bc74 == 'Z') {
    f33_reset_recoverable_monitor(((F33RecoverableMonitorState *)camry_host_ptr((uint32_t)((0xfebe7bdcu)))));
  }
  else if ((DAT_febe6764 & 1) == 0) {
    f33_step_recoverable_monitor
              (((F33RecoverableMonitorState *)camry_host_ptr((uint32_t)((0xfebe7bdcu)))), ((F33RecoverableMonitorLimits *)camry_host_ptr((uint32_t)((0x2ba0cu)))), ((F33RecoverableMonitorCallbacks *)camry_host_ptr((uint32_t)((0x28c78u)))));
  }
  else {
    f33_retain_disabled_recoverable_monitor
              (((F33RecoverableMonitorState *)camry_host_ptr((uint32_t)((0xfebe7bdcu)))), ((F33RecoverableMonitorLimits *)camry_host_ptr((uint32_t)((0x2ba0cu)))));
  }
  f33_publish_thermistor_range_monitor_status('\0',(*((uint *)camry_host_ptr((uint32_t)(puVar1 + -0x3c24)))));
  return;
}



/* Unsigned6492 inside inclusive1206..65231 returns11,otherwise22. LD.HU and unsigned branches prove
   raw-domain bounds, not signed temperatures. */

uint f33_classify_raw_thermistor_range_a(void)

{
  if ((DAT_0002ba1a <= DAT_febe6492) && (DAT_febe6492 <= DAT_0002ba18)) {
    return 0x11;
  }
  return 0x22;
}



/* Report event88 through51E2C/52A2A healthy-observed bitmap; does not clear current failure
   history. */

void f33_report_scalar_event_88_healthy_observed(void)

{
  f33_report_diagnostic_healthy_observed(0x88);
  return;
}



/* Report event88 with capture kind800; diagnostic admission remains in51C66. */

void f33_report_scalar_event_88_failure(void)

{
  f33_report_diagnostic_event_failure(0x88,800);
  return;
}



/* Report event88 through51D5E ordinary pass; current failure clears while normal retained histories
   survive. */

void f33_report_scalar_event_88_pass(void)

{
  f33_report_diagnostic_event_pass(0x88);
  return;
}



/* f33_reset_recoverable_monitor wrapper resetting exactly one monitor state
   ((0xfebe7be8u)); whole-body shape-verified from the canonical corpus.
   Per-instance semantics derive from the referenced state cell; not individually executed. */

void f33_reset_scalar_monitor_45f32(void)

{
  f33_reset_recoverable_monitor(((F33RecoverableMonitorState *)camry_host_ptr((uint32_t)((0xfebe7be8u)))));
  return;
}



/* f33_reset_recoverable_monitor wrapper resetting exactly one monitor state
   ((0xfebe7be8u)); whole-body shape-verified from the canonical corpus.
   Per-instance semantics derive from the referenced state cell; not individually executed. */

void f33_reset_scalar_monitor_45f32_45f22(void)

{
  f33_reset_recoverable_monitor(((F33RecoverableMonitorState *)camry_host_ptr((uint32_t)((0xfebe7be8u)))));
  return;
}



/* State7BE8 -> slot18 index1. Qualification bit1 clear admits recoverable qualifier. Raw
   unsigned6498 range1206..65231 inclusive; same25/25/25 limits; event85. */

void f33_step_raw_thermistor_range_b_monitor(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  if (DAT_0002bc78 == 'Z') {
    f33_reset_recoverable_monitor(((F33RecoverableMonitorState *)camry_host_ptr((uint32_t)((0xfebe7be8u)))));
  }
  else if ((DAT_febe6764 >> 1 & 1) == 0) {
    f33_step_recoverable_monitor
              (((F33RecoverableMonitorState *)camry_host_ptr((uint32_t)((0xfebe7be8u)))), ((F33RecoverableMonitorLimits *)camry_host_ptr((uint32_t)((0x2ba12u)))), ((F33RecoverableMonitorCallbacks *)camry_host_ptr((uint32_t)((0x28cb4u)))));
  }
  else {
    f33_retain_disabled_recoverable_monitor
              (((F33RecoverableMonitorState *)camry_host_ptr((uint32_t)((0xfebe7be8u)))), ((F33RecoverableMonitorLimits *)camry_host_ptr((uint32_t)((0x2ba12u)))));
  }
  f33_publish_thermistor_range_monitor_status('\x01',(*((uint *)camry_host_ptr((uint32_t)(puVar1 + -0x3c18)))));
  return;
}



/* Unsigned6498 inside inclusive1206..65231 returns11,otherwise22. Same predicate used for entry and
   recovery. */

uint f33_classify_raw_thermistor_range_b(void)

{
  if ((DAT_0002ba1e <= DAT_febe6498) && (DAT_febe6498 <= DAT_0002ba1c)) {
    return 0x11;
  }
  return 0x22;
}



/* Report event85 through51E2C/52A2A healthy-observed bitmap; does not clear current failure
   history. */

void f33_report_scalar_event_85_healthy_observed(void)

{
  f33_report_diagnostic_healthy_observed(0x85);
  return;
}



/* Report event85 with capture kind800; diagnostic admission remains in51C66. */

void f33_report_scalar_event_85_failure(void)

{
  f33_report_diagnostic_event_failure(0x85,800);
  return;
}



/* Report event85 through51D5E ordinary pass; current failure clears while normal retained histories
   survive. */

void f33_report_scalar_event_85_pass(void)

{
  f33_report_diagnostic_event_pass(0x85);
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_45fd0(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_45fd2(void)

{
  return;
}



/* Rebuild slot18 with kind16 when either7BF4/5 has confirmed mask22. Publish packed per-channel
   status at7BF8 with pending11 precedence over22 within each byte; always set publication
   marker7BF6=5A. Native paired recovery clears slot18 current action while retained diagnostic
   failure histories and monitor high-water survive. */

void f33_publish_thermistor_range_monitor_actions(void)

{
  ushort uVar1;
  uint32_t puVar2;
  puVar2 = 0xfebeb800u;
  f33_retain_and_clear_fault_record(0x12);
  if ((((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x3c0b))))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x3c0c)))))) & 0x22) == 0x22) {
    f33_encode_fault_action_kind('\x12','\x16');
  }
  f33_select_current_fault_record(0x12);
  if (((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x3c0c))))) & 0x11) == 0x11) {
    uVar1 = 0x11;
  }
  else {
    uVar1 = 0;
    if (((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x3c0c))))) & 0x22) == 0x22) {
      uVar1 = 0x22;
    }
  }
  if (((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x3c0b))))) & 0x11) == 0x11) {
    uVar1 = uVar1 | 0x1100;
  }
  else if (((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x3c0b))))) & 0x22) == 0x22) {
    uVar1 = uVar1 | 0x2200;
  }
  (*((ushort *)camry_host_ptr((uint32_t)(puVar2 + -0x3c08)))) = uVar1;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x3c0a))))) = 0x5a;
  return;
}



/* If low8(index)<2, store low8(packed_status) to FEBE7BF4+index. Other bits of the packed qualifier
   result are not published. */

void f33_publish_thermistor_range_monitor_status(uchar index,uint packed_status)

{
  if (index < 2) {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe7bf4u + (uint32_t)(index) * 1u)))) = (char)packed_status;
  }
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_4606a(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_4606c(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_4606e(void)

{
  return;
}



void FUN_00046070(void)

{
  FUN_0006b98a(((undefined4 *)camry_host_ptr((uint32_t)((0xfebe7c00u)))));
  return;
}



void FUN_00046080(void)

{
  FUN_0006b98a(((undefined4 *)camry_host_ptr((uint32_t)((0xfebe7c00u)))));
  return;
}



void FUN_00046090(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  if (DAT_febe8a24 != 'Z') {
    return;
  }
  if (DAT_0002bc7c == 'Z') {
    FUN_0006b98a(((undefined4 *)camry_host_ptr((uint32_t)((0xfebe7c00u)))));
  }
  else {
    if ((DAT_febeeb85 == 'Z') && ((DAT_febe71ec >> 5 & 1) == 0)) {
      puVar1 = 0xfebeb800u;
      f33_step_escalating_monitor
                (((F33EscalatingMonitorState *)camry_host_ptr((uint32_t)((0xfebe7c00u)))), (ushort *)((undefined *)camry_host_ptr(0x2ba20u)), 
                 (uint *)&PTR_f33_classify_snapshot_status_a_00028cf0);
      if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x3bf0))))) == 'Z') {
        f33_force_monitor_escalation
                  (((F33EscalatingMonitorState *)camry_host_ptr((uint32_t)((0xfebe7c00u)))), (ushort *)((undefined *)camry_host_ptr(0x2ba20u)), 
                   (uint *)&PTR_f33_classify_snapshot_status_a_00028cf0);
      }
      goto LAB_0004610e;
    }
    f33_retain_disabled_escalating_monitor(((F33EscalatingMonitorState *)camry_host_ptr((uint32_t)((0xfebe7c00u)))), (ushort *)((undefined *)camry_host_ptr(0x2ba20u)));
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x3bf0))))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x3bef))))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x3bee))))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x3bed))))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x3bec))))) = 0;
LAB_0004610e:
  f33_publish_shared_snapshot_monitor_status(0,(*((uint *)camry_host_ptr((uint32_t)(puVar1 + -0x3c00)))));
  return;
}



/* Exact slot0/1 callback predicate. Return11/22/33/44 protocol; software source, qualification and
   retained-snapshot conditions are not physical freshness guarantees. ChannelA snapshot
   status/sequence change requires7DB2>=2125; unchanged initial pass needs both sticky evidence
   bytes5A. */

uint f33_classify_snapshot_status_a(void)

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



/* Exact slot0/1 callback predicate. Return11/22/33/44 protocol; software source, qualification and
   retained-snapshot conditions are not physical freshness guarantees. ChannelA confirmed-state
   snapshot predicate drops initial sticky admission, refreshes retained snapshot and returns22/11.
    */

uint f33_classify_snapshot_status_recovery_a(void)

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



/* f33_report_diagnostic_healthy_observed(0x155); whole-body shape-verified. The literal is the
   encoded diagnostic event, not a recovered OEM name. */

void f33_report_diagnostic_healthy_observed_155_4623e(void)

{
  f33_report_diagnostic_healthy_observed(0x155);
  return;
}



void FUN_0004624e(void)

{
  byte bVar1;
  short sVar2;
  uint32_t puVar3;
  sVar2 = DAT_febe71ec;
  puVar3 = 0xfebeb800u;
  bVar1 = f33_shared_snapshot_status[9] |
          f33_shared_snapshot_status[3] | f33_shared_snapshot_status[1];
  if (DAT_febe7c11 == 'Z') {
    puVar3 = 0xfebeb800u;
    f33_report_diagnostic_event_failure(0x151,10);
  }
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x3bee))))) == 'Z') {
    f33_report_diagnostic_event_failure(0x152,10);
  }
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x3bed))))) == 'Z') {
    f33_report_diagnostic_event_failure(0x153,10);
  }
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x3bec))))) == 'Z') {
    f33_report_diagnostic_event_failure(0x154,10);
  }
  if ((((bVar1 & 0x22) == 0x22) || ((bVar1 & 0x44) == 0x44)) || (sVar2 != 0)) {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x3bf0))))) = 0x5a;
  }
  return;
}



/* Slot0 callback in the retained/escalation family; action and diagnostic reporting remain
   independent. See exact callback vector and shared-monitor composition report. A status retained
   callback requests escalation on opposite-group complete22/44 or any nonzero qualification word;
   not only its own bit. */

void f33_request_shared_monitor_escalation_status_a(void)

{
  byte bVar1;
  
  bVar1 = f33_shared_snapshot_status[3] | f33_shared_snapshot_status[1] |
          f33_shared_snapshot_status[9];
  if ((((bVar1 & 0x22) == 0x22) || ((bVar1 & 0x44) == 0x44)) || (DAT_febe71ec != 0)) {
    DAT_febe7c10 = 0x5a;
  }
  return;
}



/* Sequential initializer chain: 4 unconditional calls and no other statements; shape-verified. The
   called sequence is the function's entire behavior; chain family members differ in callee sets. */

void f33_run_init_chain_4630c(void)

{
  f33_report_diagnostic_event_pass(0x151);
  f33_report_diagnostic_event_pass(0x152);
  f33_report_diagnostic_event_pass(0x153);
  f33_report_diagnostic_event_pass(0x154);
  return;
}



/* f33_report_diagnostic_event_failure(0x155,10); whole-body shape-verified. The literal is the
   encoded diagnostic event, not a recovered OEM name. */

void f33_report_diagnostic_event_failure_155_10_46334(void)

{
  f33_report_diagnostic_event_failure(0x155,10);
  return;
}



void FUN_00046346(void)

{
  FUN_0006b98a(((undefined4 *)camry_host_ptr((uint32_t)((0xfebe7c1cu)))));
  return;
}



void FUN_00046356(void)

{
  FUN_0006b98a(((undefined4 *)camry_host_ptr((uint32_t)((0xfebe7c1cu)))));
  return;
}



void FUN_00046366(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  if (DAT_febe8a24 != 'Z') {
    return;
  }
  if (DAT_0002bc80 == 'Z') {
    FUN_0006b98a(((undefined4 *)camry_host_ptr((uint32_t)((0xfebe7c1cu)))));
  }
  else {
    if ((DAT_febeeb85 == 'Z') && ((DAT_febe71ec >> 6 & 1) == 0)) {
      puVar1 = 0xfebeb800u;
      f33_step_escalating_monitor
                (((F33EscalatingMonitorState *)camry_host_ptr((uint32_t)((0xfebe7c1cu)))), (ushort *)((undefined *)camry_host_ptr(0x2ba30u)), 
                 (uint *)&PTR_f33_classify_snapshot_status_b_00028d34);
      if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x3bd4))))) == 'Z') {
        f33_force_monitor_escalation
                  (((F33EscalatingMonitorState *)camry_host_ptr((uint32_t)((0xfebe7c1cu)))), (ushort *)((undefined *)camry_host_ptr(0x2ba30u)), 
                   (uint *)&PTR_f33_classify_snapshot_status_b_00028d34);
      }
      goto LAB_000463e4;
    }
    f33_retain_disabled_escalating_monitor(((F33EscalatingMonitorState *)camry_host_ptr((uint32_t)((0xfebe7c1cu)))), (ushort *)((undefined *)camry_host_ptr(0x2ba30u)));
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x3bd4))))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x3bd3))))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x3bd2))))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x3bd1))))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x3bd0))))) = 0;
LAB_000463e4:
  f33_publish_shared_snapshot_monitor_status(1,(*((uint *)camry_host_ptr((uint32_t)(puVar1 + -0x3be4)))));
  return;
}



/* Exact slot0/1 callback predicate. Return11/22/33/44 protocol; software source, qualification and
   retained-snapshot conditions are not physical freshness guarantees. ChannelB snapshot
   status/sequence change uses inclusive2125 gate and initial sticky evidence admission. */

uint f33_classify_snapshot_status_b(void)

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



/* Exact slot0/1 callback predicate. Return11/22/33/44 protocol; software source, qualification and
   retained-snapshot conditions are not physical freshness guarantees. ChannelB confirmed-state
   snapshot predicate refreshes retained generation and classifies change without initial sticky
   gate. */

uint f33_classify_snapshot_status_recovery_b(void)

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



/* f33_report_diagnostic_healthy_observed(0x15a); whole-body shape-verified. The literal is the
   encoded diagnostic event, not a recovered OEM name. */

void f33_report_diagnostic_healthy_observed_15a_46514(void)

{
  f33_report_diagnostic_healthy_observed(0x15a);
  return;
}



void FUN_00046524(void)

{
  byte bVar1;
  short sVar2;
  uint32_t puVar3;
  sVar2 = DAT_febe71ec;
  puVar3 = 0xfebeb800u;
  bVar1 = f33_shared_snapshot_status[8] |
          f33_shared_snapshot_status[2] | f33_shared_snapshot_status[0];
  if (DAT_febe7c2d == 'Z') {
    puVar3 = 0xfebeb800u;
    f33_report_diagnostic_event_failure(0x156,10);
  }
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x3bd2))))) == 'Z') {
    f33_report_diagnostic_event_failure(0x157,10);
  }
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x3bd1))))) == 'Z') {
    f33_report_diagnostic_event_failure(0x158,10);
  }
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x3bd0))))) == 'Z') {
    f33_report_diagnostic_event_failure(0x159,10);
  }
  if ((((bVar1 & 0x22) == 0x22) || ((bVar1 & 0x44) == 0x44)) || (sVar2 != 0)) {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x3bd4))))) = 0x5a;
  }
  return;
}



/* Slot0 callback in the retained/escalation family; action and diagnostic reporting remain
   independent. See exact callback vector and shared-monitor composition report. B status retained
   callback requests escalation on opposite-group complete22/44 or any nonzero qualification word;
   not only its own bit. */

void f33_request_shared_monitor_escalation_status_b(void)

{
  byte bVar1;
  
  bVar1 = f33_shared_snapshot_status[2] | f33_shared_snapshot_status[0] |
          f33_shared_snapshot_status[8];
  if ((((bVar1 & 0x22) == 0x22) || ((bVar1 & 0x44) == 0x44)) || (DAT_febe71ec != 0)) {
    DAT_febe7c2c = 0x5a;
  }
  return;
}



/* Sequential initializer chain: 4 unconditional calls and no other statements; shape-verified. The
   called sequence is the function's entire behavior; chain family members differ in callee sets. */

void f33_run_init_chain_465e2(void)

{
  f33_report_diagnostic_event_pass(0x156);
  f33_report_diagnostic_event_pass(0x157);
  f33_report_diagnostic_event_pass(0x158);
  f33_report_diagnostic_event_pass(0x159);
  return;
}



/* f33_report_diagnostic_event_failure(0x15a,10); whole-body shape-verified. The literal is the
   encoded diagnostic event, not a recovered OEM name. */

void f33_report_diagnostic_event_failure_15a_10_4660a(void)

{
  f33_report_diagnostic_event_failure(0x15a,10);
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_4661c(void)

{
  return;
}



void FUN_0004661e(void)

{
  DAT_febe7c4e = (byte)DAT_febe81ee & 3;
  if (DAT_febe8a1c == 'Z') {
    DAT_febe7c4e = DAT_febe7c4e - 1 & 3;
  }
  return;
}



void FUN_0004663c(void)

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



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_467ce(void)

{
  return;
}



void FUN_000467d0(void)

{
  DAT_febe7c66 = (byte)DAT_febe81f0 & 3;
  if (DAT_febe8a1c == 'Z') {
    DAT_febe7c66 = DAT_febe7c66 - 1 & 3;
  }
  return;
}



void FUN_000467ee(void)

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



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_46980(void)

{
  return;
}



void FUN_00046982(void)

{
  DAT_febe686c = 0;
  DAT_febe6870 = 0;
  DAT_febe6874 = 0;
  DAT_febe6872 = 0;
  return;
}



void FUN_00046994(void)

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
  sVar4 = DAT_febe6874;
  sVar3 = DAT_febe6872;
  cVar2 = DAT_febe686e;
  cVar9 = DAT_febe686c;
  sVar1 = DAT_febe62ac;
  puVar6 = 0xfebeb800u;
  sVar8 = DAT_febe6870;
  if (DAT_febe686d == '\0') {
    if (DAT_febe8a24 == 'Z') {
      if (DAT_febe7cb7 == '\x02') {
        sVar8 = DAT_febe62b6 << 1;
      }
      else {
        sVar8 = DAT_febe62ba;
        if (DAT_febe7cb7 == '\x01') {
          sVar8 = DAT_febe62b8 * -2;
        }
      }
      puVar6 = 0xfebeb800u;
      sVar7 = f33_clamp_decoded_torque(sVar8);
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
  saved_mask = f33_priority_mask_enter(0xffc0);
  DAT_febe686c = cVar9;
  DAT_febe6870 = sVar8;
  f33_priority_mask_restore(saved_mask);
  return;
}



void FUN_00046a2c(undefined1 param_1)

{
  DAT_febe686d = param_1;
  return;
}



/* f33_reset_recoverable_monitor wrapper resetting exactly one monitor state
   ((F33RecoverableMonitorState *)((undefined *)camry_host_ptr(0xfebe7c68u))); whole-body shape-verified from the canonical
   corpus. Per-instance semantics derive from the referenced state cell; not individually executed.
    */

void f33_reset_recoverable_monitor_febe7c68(void)

{
  f33_reset_recoverable_monitor((F33RecoverableMonitorState *)((undefined *)camry_host_ptr(0xfebe7c68u)));
  return;
}



/* f33_reset_recoverable_monitor wrapper resetting exactly one monitor state
   ((F33RecoverableMonitorState *)((undefined *)camry_host_ptr(0xfebe7c68u))); whole-body shape-verified from the canonical
   corpus. Per-instance semantics derive from the referenced state cell; not individually executed.
    */

void f33_reset_recoverable_monitor_febe7c68_46a42(void)

{
  f33_reset_recoverable_monitor((F33RecoverableMonitorState *)((undefined *)camry_host_ptr(0xfebe7c68u)));
  return;
}



void FUN_00046a52(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  if (DAT_febe8a24 == 'Z') {
    if (DAT_0002bc84 == 'Z') {
      f33_reset_recoverable_monitor((F33RecoverableMonitorState *)((undefined *)camry_host_ptr(0xfebe7c68u)));
    }
    else if (DAT_febeeb85 == 'Z') {
      f33_step_recoverable_monitor
                ((F33RecoverableMonitorState *)((undefined *)camry_host_ptr(0xfebe7c68u)),
                 (F33RecoverableMonitorLimits *)&PTR_LAB_0002ba40,
                 (F33RecoverableMonitorCallbacks *)&PTR_f33_classify_selected_source_hold_00028d78);
    }
    else {
      f33_retain_disabled_recoverable_monitor
                ((F33RecoverableMonitorState *)((undefined *)camry_host_ptr(0xfebe7c68u)),
                 (F33RecoverableMonitorLimits *)&PTR_LAB_0002ba40);
    }
    f33_publish_shared_snapshot_monitor_status(10,(*((uint *)camry_host_ptr((uint32_t)(puVar1 + -0x3b98)))));
  }
  return;
}



/* Exact slot0/1 callback predicate. Return11/22/33/44 protocol; software source, qualification and
   retained-snapshot conditions are not physical freshness guarantees. Selected-source hold
   detection requires previous686C5A and7CB85A. */

uint f33_classify_selected_source_hold(void)

{
  if ((DAT_febe686c == 'Z') && (DAT_febe7cb8 == 'Z')) {
    return 0x22;
  }
  return 0x11;
}



/* Exact slot0/1 callback predicate. Return11/22/33/44 protocol; software source, qualification and
   retained-snapshot conditions are not physical freshness guarantees. Confirmed selected-source
   hold recovery checks686C alone, not initial7CB8 conjunction. */

uint f33_classify_selected_source_hold_recovery(void)

{
  if (DAT_febe686c == 'Z') {
    return 0x22;
  }
  return 0x11;
}



/* f33_report_diagnostic_event_failure(0x50,10); whole-body shape-verified. The literal is the
   encoded diagnostic event, not a recovered OEM name. */

void f33_report_diagnostic_event_failure_50_10_46adc(void)

{
  f33_report_diagnostic_event_failure(0x50,10);
  return;
}



/* f33_report_diagnostic_event_pass(0x50); whole-body shape-verified. The literal is the encoded
   diagnostic event, not a recovered OEM name. */

void f33_report_diagnostic_event_pass_50_46aee(void)

{
  f33_report_diagnostic_event_pass(0x50);
  return;
}



void FUN_00046afe(void)

{
  FUN_0006b98a(((undefined4 *)camry_host_ptr((uint32_t)((0xfebe7c74u)))));
  return;
}



void FUN_00046b0e(void)

{
  FUN_0006b98a(((undefined4 *)camry_host_ptr((uint32_t)((0xfebe7c74u)))));
  return;
}



void FUN_00046b1e(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  if (DAT_febe8a24 != 'Z') {
    return;
  }
  if (DAT_0002bc88 == 'Z') {
    FUN_0006b98a(((undefined4 *)camry_host_ptr((uint32_t)((0xfebe7c74u)))));
  }
  else {
    if ((DAT_febeeb85 == 'Z') && ((DAT_febe71ec >> 5 & 1) == 0)) {
      puVar1 = 0xfebeb800u;
      f33_step_escalating_monitor
                (((F33EscalatingMonitorState *)camry_host_ptr((uint32_t)((0xfebe7c74u)))), (ushort *)((undefined *)camry_host_ptr(0x2ba46u)), (uint *)&PTR_FUN_00028db4);
      if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x3b7c))))) == 'Z') {
        f33_force_monitor_escalation
                  (((F33EscalatingMonitorState *)camry_host_ptr((uint32_t)((0xfebe7c74u)))), (ushort *)((undefined *)camry_host_ptr(0x2ba46u)), (uint *)&PTR_FUN_00028db4)
        ;
      }
      goto LAB_00046b9e;
    }
    f33_retain_disabled_escalating_monitor(((F33EscalatingMonitorState *)camry_host_ptr((uint32_t)((0xfebe7c74u)))), (ushort *)((undefined *)camry_host_ptr(0x2ba46u)));
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x3b7c))))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x3b7b))))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x3b7a))))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x3b79))))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x3b78))))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x3b77))))) = 0;
LAB_00046b9e:
  f33_publish_shared_snapshot_monitor_status(2,(*((uint *)camry_host_ptr((uint32_t)(puVar1 + -0x3b8c)))));
  return;
}



undefined4 FUN_00046bac(void)

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



/* Exact slot0/1 callback predicate. Return11/22/33/44 protocol; software source, qualification and
   retained-snapshot conditions are not physical freshness guarantees. ChannelA five sample-bound
   snapshot counters refresh retained generations and change flags; confirmed predicate returns22/11
   without initial sticky gate. */

uint f33_classify_snapshot_sample_bounds_recovery_a(void)

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



/* f33_report_diagnostic_healthy_observed(0x160); whole-body shape-verified. The literal is the
   encoded diagnostic event, not a recovered OEM name. */

void f33_report_diagnostic_healthy_observed_160_46ce4(void)

{
  f33_report_diagnostic_healthy_observed(0x160);
  return;
}



void FUN_00046cf4(void)

{
  byte bVar1;
  short sVar2;
  uint32_t puVar3;
  sVar2 = DAT_febe71ec;
  puVar3 = 0xfebeb800u;
  bVar1 = f33_shared_snapshot_status[9] |
          f33_shared_snapshot_status[3] | f33_shared_snapshot_status[1];
  if (DAT_febe7c85 == 'Z') {
    puVar3 = 0xfebeb800u;
    f33_report_diagnostic_event_failure(0x15b,10);
  }
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x3b7a))))) == 'Z') {
    f33_report_diagnostic_event_failure(0x15c,10);
  }
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x3b79))))) == 'Z') {
    f33_report_diagnostic_event_failure(0x15d,10);
  }
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x3b78))))) == 'Z') {
    f33_report_diagnostic_event_failure(0x15e,10);
  }
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x3b77))))) == 'Z') {
    f33_report_diagnostic_event_failure(0x15f,10);
  }
  if ((((bVar1 & 0x22) == 0x22) || ((bVar1 & 0x44) == 0x44)) || (sVar2 != 0)) {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x3b7c))))) = 0x5a;
  }
  return;
}



/* Slot0 callback in the retained/escalation family; action and diagnostic reporting remain
   independent. See exact callback vector and shared-monitor composition report. A sample-bound
   retained callback requests escalation on opposite-group complete22/44 or any nonzero
   qualification word; not only its own bit. */

void f33_request_shared_monitor_escalation_sample_bounds_a(void)

{
  byte bVar1;
  
  bVar1 = f33_shared_snapshot_status[3] | f33_shared_snapshot_status[1] |
          f33_shared_snapshot_status[9];
  if ((((bVar1 & 0x22) == 0x22) || ((bVar1 & 0x44) == 0x44)) || (DAT_febe71ec != 0)) {
    DAT_febe7c84 = 0x5a;
  }
  return;
}



/* Sequential initializer chain: 5 unconditional calls and no other statements; shape-verified. The
   called sequence is the function's entire behavior; chain family members differ in callee sets. */

void f33_run_init_chain_46dc6(void)

{
  f33_report_diagnostic_event_pass(0x15b);
  f33_report_diagnostic_event_pass(0x15c);
  f33_report_diagnostic_event_pass(0x15d);
  f33_report_diagnostic_event_pass(0x15e);
  f33_report_diagnostic_event_pass(0x15f);
  return;
}



/* f33_report_diagnostic_event_failure(0x160,10); whole-body shape-verified. The literal is the
   encoded diagnostic event, not a recovered OEM name. */

void f33_report_diagnostic_event_failure_160_10_46df6(void)

{
  f33_report_diagnostic_event_failure(0x160,10);
  return;
}



void FUN_00046e08(void)

{
  FUN_0006b98a(((undefined4 *)camry_host_ptr((uint32_t)((0xfebe7c90u)))));
  return;
}



void FUN_00046e18(void)

{
  FUN_0006b98a(((undefined4 *)camry_host_ptr((uint32_t)((0xfebe7c90u)))));
  return;
}



void FUN_00046e28(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  if (DAT_febe8a24 != 'Z') {
    return;
  }
  if (DAT_0002bc8c == 'Z') {
    FUN_0006b98a(((undefined4 *)camry_host_ptr((uint32_t)((0xfebe7c90u)))));
  }
  else {
    if ((DAT_febeeb85 == 'Z') && ((DAT_febe71ec >> 6 & 1) == 0)) {
      puVar1 = 0xfebeb800u;
      f33_step_escalating_monitor
                (((F33EscalatingMonitorState *)camry_host_ptr((uint32_t)((0xfebe7c90u)))), (ushort *)((undefined *)camry_host_ptr(0x2ba56u)), (uint *)&PTR_FUN_00028df8);
      if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x3b60))))) == 'Z') {
        f33_force_monitor_escalation
                  (((F33EscalatingMonitorState *)camry_host_ptr((uint32_t)((0xfebe7c90u)))), (ushort *)((undefined *)camry_host_ptr(0x2ba56u)), (uint *)&PTR_FUN_00028df8)
        ;
      }
      goto LAB_00046ea8;
    }
    f33_retain_disabled_escalating_monitor(((F33EscalatingMonitorState *)camry_host_ptr((uint32_t)((0xfebe7c90u)))), (ushort *)((undefined *)camry_host_ptr(0x2ba56u)));
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x3b60))))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x3b5f))))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x3b5e))))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x3b5d))))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x3b5c))))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x3b5b))))) = 0;
LAB_00046ea8:
  f33_publish_shared_snapshot_monitor_status(3,(*((uint *)camry_host_ptr((uint32_t)(puVar1 + -0x3b70)))));
  return;
}



undefined4 FUN_00046eb6(void)

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



/* Exact slot0/1 callback predicate. Return11/22/33/44 protocol; software source, qualification and
   retained-snapshot conditions are not physical freshness guarantees. Parallel channelB
   five-counter confirmed predicate; snapshot changes rather than nonzero values are detection
   inputs. */

uint f33_classify_snapshot_sample_bounds_recovery_b(void)

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



/* f33_report_diagnostic_healthy_observed(0x166); whole-body shape-verified. The literal is the
   encoded diagnostic event, not a recovered OEM name. */

void f33_report_diagnostic_healthy_observed_166_46fee(void)

{
  f33_report_diagnostic_healthy_observed(0x166);
  return;
}



void FUN_00046ffe(void)

{
  byte bVar1;
  short sVar2;
  uint32_t puVar3;
  sVar2 = DAT_febe71ec;
  puVar3 = 0xfebeb800u;
  bVar1 = f33_shared_snapshot_status[8] |
          f33_shared_snapshot_status[2] | f33_shared_snapshot_status[0];
  if (DAT_febe7ca1 == 'Z') {
    puVar3 = 0xfebeb800u;
    f33_report_diagnostic_event_failure(0x161,10);
  }
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x3b5e))))) == 'Z') {
    f33_report_diagnostic_event_failure(0x162,10);
  }
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x3b5d))))) == 'Z') {
    f33_report_diagnostic_event_failure(0x163,10);
  }
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x3b5c))))) == 'Z') {
    f33_report_diagnostic_event_failure(0x164,10);
  }
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x3b5b))))) == 'Z') {
    f33_report_diagnostic_event_failure(0x165,10);
  }
  if ((((bVar1 & 0x22) == 0x22) || ((bVar1 & 0x44) == 0x44)) || (sVar2 != 0)) {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x3b60))))) = 0x5a;
  }
  return;
}



/* Slot0 callback in the retained/escalation family; action and diagnostic reporting remain
   independent. See exact callback vector and shared-monitor composition report. B sample-bound
   retained callback requests escalation on opposite-group complete22/44 or any nonzero
   qualification word; not only its own bit. */

void f33_request_shared_monitor_escalation_sample_bounds_b(void)

{
  byte bVar1;
  
  bVar1 = f33_shared_snapshot_status[2] | f33_shared_snapshot_status[0] |
          f33_shared_snapshot_status[8];
  if ((((bVar1 & 0x22) == 0x22) || ((bVar1 & 0x44) == 0x44)) || (DAT_febe71ec != 0)) {
    DAT_febe7ca0 = 0x5a;
  }
  return;
}



/* Sequential initializer chain: 5 unconditional calls and no other statements; shape-verified. The
   called sequence is the function's entire behavior; chain family members differ in callee sets. */

void f33_run_init_chain_470d0(void)

{
  f33_report_diagnostic_event_pass(0x161);
  f33_report_diagnostic_event_pass(0x162);
  f33_report_diagnostic_event_pass(0x163);
  f33_report_diagnostic_event_pass(0x164);
  f33_report_diagnostic_event_pass(0x165);
  return;
}



/* f33_report_diagnostic_event_failure(0x166,10); whole-body shape-verified. The literal is the
   encoded diagnostic event, not a recovered OEM name. */

void f33_report_diagnostic_event_failure_166_10_47100(void)

{
  f33_report_diagnostic_event_failure(0x166,10);
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_47112(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_47114(void)

{
  return;
}



/* Rebuild slot0. Groups{0,2,8}/{1,3,9} select7CB7 with groupB priority. Kinds05/10/11/2F/30;
   qualification can force escalation. Upper pending transitions also affect686D selected-source
   hold without changing confirmed group selection. Slot0 composes snapshot-change groups,
   qualification, transition-sensitive hold and action requests. Qualification merger can suppress
   kind10 mode/channel/limit fields while retaining class and ancillary action. */

void f33_publish_shared_snapshot_monitor_actions(void)

{
  byte bVar1;
  ushort uVar2;
  undefined1 uVar3;
  byte bVar4;
  uint32_t puVar5;
  uchar uVar6;
  undefined1 uVar7;
  undefined4 uVar8;
  int iVar9;
  int iVar10;
  
  uVar2 = DAT_febe71ec;
  puVar5 = 0xfebeb800u;
  uVar8 = 0;
  iVar9 = 0;
  f33_retain_and_clear_fault_record(0);
  bVar4 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x3b4b))))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x3b51))))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x3b53)))));
  if (((bVar4 & 0x22) == 0x22) || ((bVar4 & 0x44) == 0x44)) {
    uVar3 = 2;
  }
  else {
    uVar3 = 1;
    bVar4 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x3b4c))))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x3b52))))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x3b54)))));
    if ((bVar4 & 0x22) != 0x22) {
      uVar3 = (bVar4 & 0x44) == 0x44;
    }
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x3b49))))) = uVar3;
  if ((((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x3b4f))))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x3b50))))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x3b4a)))))) & 0x22) == 0x22) {
    f33_encode_fault_action_kind('\0','\x05');
  }
  bVar4 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x3b4c))))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x3b52))))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x3b54)))));
  iVar10 = 0;
  if ((((bVar4 & 0x22) == 0x22) || ((bVar4 & 0x44) == 0x44)) &&
     ((bVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x3b4b))))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x3b51))))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x3b53))))), (bVar1 & 0x22) == 0x22 ||
      ((bVar1 & 0x44) == 0x44)))) {
    iVar10 = 0x5a;
  }
  if (((bVar4 & 0x44) == 0x44) || (iVar10 == 0x5a)) {
    f33_encode_fault_action_kind('\0','\x10');
  }
  if (((((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x3b4b))))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x3b51))))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x3b53)))))) & 0x44) == 0x44) || (iVar10 == 0x5a))
  {
    f33_encode_fault_action_kind('\0','\x11');
  }
  bVar4 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x3b4c))))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x3b52))))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x3b54)))));
  if (((bVar4 & 0x22) == 0x22) || ((bVar4 & 0x44) == 0x44)) {
    bVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x3b4b))))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x3b51))))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x3b53)))));
    if (((bVar1 & 0x22) != 0x22) && ((bVar1 & 0x44) != 0x44)) {
      if ((bVar4 & 0x22) != 0x22) goto LAB_0004725e;
      goto LAB_00047268;
    }
LAB_0004729a:
    iVar9 = 0x5a;
  }
  else {
LAB_0004725e:
    if ((bVar4 & 0x44) == 0x44) {
LAB_00047268:
      if ((uVar2 != 0) && ((uVar2 >> 5 & 1) == 0)) goto LAB_0004729a;
    }
    bVar4 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x3b4b))))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x3b51))))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x3b53)))));
    if ((((bVar4 & 0x22) == 0x22) || ((bVar4 & 0x44) == 0x44)) &&
       ((uVar2 != 0 && ((uVar2 >> 6 & 1) == 0)))) goto LAB_0004729a;
  }
  if ((uVar2 >> 5 & 1) != 0) {
    f33_encode_fault_action_kind('\0','/');
  }
  if ((uVar2 >> 6 & 1) != 0) {
    f33_encode_fault_action_kind('\0','0');
  }
  bVar4 = ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x3b4f))))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x3b50)))))) & 0x22;
  if ((bVar4 == 0x22) || (uVar3 = 0x5a, iVar9 == 0x5a)) {
    uVar7 = 0;
    uVar3 = 0;
    if (bVar4 != 0x22) goto LAB_000472dc;
  }
  else {
LAB_000472dc:
    uVar7 = uVar3;
    if (((((((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x3b42))))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x3b43)))))) & 0x11) != 0x11) &&
         ((((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x3b3f))))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x3b45))))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x3b47)))))) & 0x11) != 0x11)) &&
        ((((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x3b3e))))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x3b44))))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x3b46)))))) & 0x11) != 0x11)) && (iVar9 != 0x5a)
       ) goto LAB_00047328;
  }
  uVar8 = 0x5a;
LAB_00047328:
  FUN_00046a2c(uVar8);
  f33_select_current_fault_record(0);
  uVar6 = '\0';
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x3b4b))))) != '\0' ||
      ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x3b4c))))) != '\0' ||
      ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x3b51))))) != '\0' ||
      ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x3b52))))) != '\0' || ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x3b53))))) != '\0' || (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x3b54))))) != '\0'))))) {
    uVar6 = '\x11';
  }
  f33_set_diagnostic_cache_blocker('\b',uVar6);
  bVar4 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x3b51))))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x3b52))))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x3b53))))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x3b54)))));
  bVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x3b4a))))) |
          (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x3b4b))))) |
          (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x3b4e))))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x3b4f))))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x3b50))))) | bVar4 | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x3b4d))))) |
          (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x3b4c)))));
  if ((bVar1 == 0) || (bVar1 == 0x11)) {
    uVar3 = 0;
  }
  else {
    uVar3 = 0x5a;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x3b3c))))) = uVar3;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x3b48))))) = uVar7;
  bVar4 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x3b4b))))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x3b4c))))) | bVar4;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x3b3b))))) = bVar1;
  if ((((bVar4 & 0x11) == 0x11) || ((bVar4 & 0x22) == 0x22)) || ((bVar4 & 0x44) == 0x44)) {
    uVar6 = 'Z';
  }
  else {
    uVar6 = '\0';
  }
  f33_set_monitor_pending_projection('\x06',uVar6);
  return;
}



/* Unsigned index<11: low byte to7CAC[index], bits16..23 to7CB9[index]. Index<11 publishes low
   packed status at7CAC and bits16..23 separately at7CB9; upper pending transitions affect
   selected-source hold. */

void f33_publish_shared_snapshot_monitor_status(uint index,uint packed)

{
  uint uVar1;
  
  uVar1 = index & 0xff;
  if (uVar1 < 0xb) {
    f33_shared_snapshot_status[uVar1] = (uchar)packed;
    f33_shared_snapshot_transition[uVar1] = (uchar)(packed >> 0x10);
  }
  return;
}



void FUN_000473ec(void)

{
  FUN_0006b98a(((undefined4 *)camry_host_ptr((uint32_t)((0xfebe7cc8u)))));
  return;
}



void FUN_000473fc(void)

{
  FUN_0006b98a(((undefined4 *)camry_host_ptr((uint32_t)((0xfebe7cc8u)))));
  return;
}



void FUN_0004740c(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  if (DAT_febe8a24 == 'Z') {
    if (DAT_0002bc90 == 'Z') {
      FUN_0006b98a(((undefined4 *)camry_host_ptr((uint32_t)((0xfebe7cc8u)))));
    }
    else if ((DAT_febeeb85 == 'Z') && ((DAT_febe71ec >> 5 & 1) == 0)) {
      f33_step_escalating_monitor
                (((F33EscalatingMonitorState *)camry_host_ptr((uint32_t)((0xfebe7cc8u)))), (ushort *)((undefined *)camry_host_ptr(0x2ba66u)), 
                 (uint *)&PTR_f33_classify_snapshot_bit3_a_00028e3c);
    }
    else {
      f33_retain_disabled_escalating_monitor(((F33EscalatingMonitorState *)camry_host_ptr((uint32_t)((0xfebe7cc8u)))), (ushort *)((undefined *)camry_host_ptr(0x2ba66u)))
      ;
    }
    f33_publish_shared_snapshot_monitor_status(6,(*((uint *)camry_host_ptr((uint32_t)(puVar1 + -0x3b38)))));
  }
  return;
}



/* Exact slot0/1 callback predicate. Return11/22/33/44 protocol; software source, qualification and
   retained-snapshot conditions are not physical freshness guarantees. ChannelA bit3 counter-change
   predicate requires inclusive7DB2>=2125 and initial evidence admission. */

uint f33_classify_snapshot_bit3_a(void)

{
  uint uVar1;
  
  if ((DAT_febe6321 == DAT_febe7cd8) || (DAT_febe7db2 < DAT_0002bade)) {
    uVar1 = 0x11;
  }
  else {
    uVar1 = 0x22;
  }
  DAT_febe7cd8 = DAT_febe6321;
  return uVar1;
}



/* Exact slot0/1 callback predicate. Return11/22/33/44 protocol; software source, qualification and
   retained-snapshot conditions are not physical freshness guarantees. ChannelA bit3 confirmed-state
   predicate is constant44, retaining confirmed failure while resetting recovery timers. */

uint f33_classify_snapshot_bit3_recovery_a(void)

{
  return 0x44;
}



/* f33_report_diagnostic_event_failure(0x16b,10); whole-body shape-verified. The literal is the
   encoded diagnostic event, not a recovered OEM name. */

void f33_report_diagnostic_event_failure_16b_10_474a2(void)

{
  f33_report_diagnostic_event_failure(0x16b,10);
  return;
}



void FUN_000474b4(void)

{
  FUN_0006b98a(((undefined4 *)camry_host_ptr((uint32_t)((0xfebe7cdcu)))));
  return;
}



void FUN_000474c4(void)

{
  FUN_0006b98a(((undefined4 *)camry_host_ptr((uint32_t)((0xfebe7cdcu)))));
  return;
}



void FUN_000474d4(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  if (DAT_febe8a24 == 'Z') {
    if (DAT_0002bc94 == 'Z') {
      FUN_0006b98a(((undefined4 *)camry_host_ptr((uint32_t)((0xfebe7cdcu)))));
    }
    else if ((DAT_febeeb85 == 'Z') && ((DAT_febe71ec >> 6 & 1) == 0)) {
      f33_step_escalating_monitor
                (((F33EscalatingMonitorState *)camry_host_ptr((uint32_t)((0xfebe7cdcu)))), (ushort *)((undefined *)camry_host_ptr(0x2ba76u)), 
                 (uint *)&PTR_f33_classify_snapshot_bit3_b_00028e80);
    }
    else {
      f33_retain_disabled_escalating_monitor(((F33EscalatingMonitorState *)camry_host_ptr((uint32_t)((0xfebe7cdcu)))), (ushort *)((undefined *)camry_host_ptr(0x2ba76u)))
      ;
    }
    f33_publish_shared_snapshot_monitor_status(7,(*((uint *)camry_host_ptr((uint32_t)(puVar1 + -0x3b24)))));
  }
  return;
}



/* Exact slot0/1 callback predicate. Return11/22/33/44 protocol; software source, qualification and
   retained-snapshot conditions are not physical freshness guarantees. ChannelB bit3 change with
   inclusive2125 gate and separate retained snapshot. */

uint f33_classify_snapshot_bit3_b(void)

{
  uint uVar1;
  
  if ((DAT_febe6339 == DAT_febe7cec) || (DAT_febe7db2 < DAT_0002bae2)) {
    uVar1 = 0x11;
  }
  else {
    uVar1 = 0x22;
  }
  DAT_febe7cec = DAT_febe6339;
  return uVar1;
}



/* Exact slot0/1 callback predicate. Return11/22/33/44 protocol; software source, qualification and
   retained-snapshot conditions are not physical freshness guarantees. ChannelB bit3 confirmed
   predicate constant44; no forced escalation wrapper. */

uint f33_classify_snapshot_bit3_recovery_b(void)

{
  return 0x44;
}



/* f33_report_diagnostic_event_failure(0x16c,10); whole-body shape-verified. The literal is the
   encoded diagnostic event, not a recovered OEM name. */

void f33_report_diagnostic_event_failure_16c_10_4756a(void)

{
  f33_report_diagnostic_event_failure(0x16c,10);
  return;
}



void FUN_0004757c(void)

{
  FUN_0006b98a(((undefined4 *)camry_host_ptr((uint32_t)((0xfebe7cf0u)))));
  return;
}



void FUN_0004758c(void)

{
  FUN_0006b98a(((undefined4 *)camry_host_ptr((uint32_t)((0xfebe7cf0u)))));
  return;
}



void FUN_0004759c(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  if (DAT_febe8a24 == 'Z') {
    if (DAT_0002bc98 == 'Z') {
      puVar1 = 0xfebeb800u;
      FUN_0006b98a(((undefined4 *)camry_host_ptr((uint32_t)((0xfebe7cf0u)))));
    }
    else if ((DAT_febeeb85 == 'Z') && ((DAT_febe71ec >> 5 & 1) == 0)) {
      puVar1 = 0xfebeb800u;
      f33_step_escalating_monitor
                (((F33EscalatingMonitorState *)camry_host_ptr((uint32_t)((0xfebe7cf0u)))), (ushort *)((undefined *)camry_host_ptr(0x2ba86u)), 
                 (uint *)&PTR_f33_classify_snapshot_low_gate_a_00028ec4);
    }
    else {
      f33_shared_snapshot_monitor_4.packed_status = 0;
      f33_shared_snapshot_monitor_4.passing_count = 0;
      f33_shared_snapshot_monitor_4.failing_count = 0;
      f33_shared_snapshot_monitor_4.recovery_count = 0;
      f33_shared_snapshot_monitor_4.elapsed_count = 0;
    }
    f33_publish_shared_snapshot_monitor_status(4,(*((uint *)camry_host_ptr((uint32_t)(puVar1 + -0x3b10)))));
  }
  return;
}



/* Exact slot0/1 callback predicate. Return11/22/33/44 protocol; software source, qualification and
   retained-snapshot conditions are not physical freshness guarantees. ChannelA ancillary
   status/sequence change uses strictly7DB2<2125, opposite main gate; no diagnostic callbacks. */

uint f33_classify_snapshot_low_gate_a(void)

{
  int iVar1;
  uint uVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  
  iVar1 = 0;
  iVar5 = 0;
  iVar4 = 0;
  iVar3 = 0;
  if (DAT_febe631c != DAT_febe7d00) {
    iVar1 = 0x5a;
  }
  if (DAT_febe631d != DAT_febe7d01) {
    iVar5 = 0x5a;
  }
  if (DAT_febe631e != DAT_febe7d02) {
    iVar4 = 0x5a;
  }
  if (DAT_febe631f != DAT_febe7d03) {
    iVar3 = 0x5a;
  }
  if (((((iVar1 == 0x5a) || (iVar5 == 0x5a)) || (iVar4 == 0x5a)) || (iVar3 == 0x5a)) &&
     (DAT_febe7db2 < DAT_0002bae6)) {
    uVar2 = 0x22;
  }
  else {
    uVar2 = 0x11;
  }
  DAT_febe7d00 = DAT_febe631c;
  DAT_febe7d01 = DAT_febe631d;
  DAT_febe7d02 = DAT_febe631e;
  DAT_febe7d03 = DAT_febe631f;
  return uVar2;
}



void FUN_00047682(void)

{
  FUN_0006b98a(((undefined4 *)camry_host_ptr((uint32_t)((0xfebe7d04u)))));
  return;
}



void FUN_00047692(void)

{
  FUN_0006b98a(((undefined4 *)camry_host_ptr((uint32_t)((0xfebe7d04u)))));
  return;
}



void FUN_000476a2(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  if (DAT_febe8a24 == 'Z') {
    if (DAT_0002bc9c == 'Z') {
      puVar1 = 0xfebeb800u;
      FUN_0006b98a(((undefined4 *)camry_host_ptr((uint32_t)((0xfebe7d04u)))));
    }
    else if ((DAT_febeeb85 == 'Z') && ((DAT_febe71ec >> 6 & 1) == 0)) {
      puVar1 = 0xfebeb800u;
      f33_step_escalating_monitor
                (((F33EscalatingMonitorState *)camry_host_ptr((uint32_t)((0xfebe7d04u)))), (ushort *)((undefined *)camry_host_ptr(0x2ba96u)), 
                 (uint *)&PTR_f33_classify_snapshot_low_gate_b_00028f08);
    }
    else {
      f33_shared_snapshot_monitor_5.packed_status = 0;
      f33_shared_snapshot_monitor_5.passing_count = 0;
      f33_shared_snapshot_monitor_5.failing_count = 0;
      f33_shared_snapshot_monitor_5.recovery_count = 0;
      f33_shared_snapshot_monitor_5.elapsed_count = 0;
    }
    f33_publish_shared_snapshot_monitor_status(5,(*((uint *)camry_host_ptr((uint32_t)(puVar1 + -0x3afc)))));
  }
  return;
}



/* Exact slot0/1 callback predicate. Return11/22/33/44 protocol; software source, qualification and
   retained-snapshot conditions are not physical freshness guarantees. Parallel channelB ancillary
   low-gate change predicate; no diagnostic callbacks. */

uint f33_classify_snapshot_low_gate_b(void)

{
  int iVar1;
  uint uVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  
  iVar1 = 0;
  iVar5 = 0;
  iVar4 = 0;
  iVar3 = 0;
  if (DAT_febe6334 != DAT_febe7d14) {
    iVar1 = 0x5a;
  }
  if (DAT_febe6335 != DAT_febe7d15) {
    iVar5 = 0x5a;
  }
  if (DAT_febe6336 != DAT_febe7d16) {
    iVar4 = 0x5a;
  }
  if (DAT_febe6337 != DAT_febe7d17) {
    iVar3 = 0x5a;
  }
  if (((((iVar1 == 0x5a) || (iVar5 == 0x5a)) || (iVar4 == 0x5a)) || (iVar3 == 0x5a)) &&
     (DAT_febe7db2 < DAT_0002baea)) {
    uVar2 = 0x22;
  }
  else {
    uVar2 = 0x11;
  }
  DAT_febe7d14 = DAT_febe6334;
  DAT_febe7d15 = DAT_febe6335;
  DAT_febe7d16 = DAT_febe6336;
  DAT_febe7d17 = DAT_febe6337;
  return uVar2;
}



void FUN_00047788(void)

{
  FUN_0006b98a(((undefined4 *)camry_host_ptr((uint32_t)((0xfebe7d18u)))));
  return;
}



void FUN_00047798(void)

{
  FUN_0006b98a(((undefined4 *)camry_host_ptr((uint32_t)((0xfebe7d18u)))));
  return;
}



void FUN_000477a8(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  if (DAT_febe8a24 != 'Z') {
    return;
  }
  if (DAT_0002bca0 == 'Z') {
    FUN_0006b98a(((undefined4 *)camry_host_ptr((uint32_t)((0xfebe7d18u)))));
  }
  else {
    if ((DAT_febeeb85 == 'Z') && ((DAT_febe71ec >> 5 & 1) == 0)) {
      puVar1 = 0xfebeb800u;
      f33_step_escalating_monitor
                (((F33EscalatingMonitorState *)camry_host_ptr((uint32_t)((0xfebe7d18u)))), (ushort *)((undefined *)camry_host_ptr(0x2baa6u)), 
                 (uint *)&PTR_f33_classify_snapshot_bit2_a_00028f4c);
      if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x3ad8))))) == 'Z') {
        f33_force_monitor_escalation
                  (((F33EscalatingMonitorState *)camry_host_ptr((uint32_t)((0xfebe7d18u)))), (ushort *)((undefined *)camry_host_ptr(0x2baa6u)), 
                   (uint *)&PTR_f33_classify_snapshot_bit2_a_00028f4c);
      }
      goto LAB_0004781c;
    }
    f33_retain_disabled_escalating_monitor(((F33EscalatingMonitorState *)camry_host_ptr((uint32_t)((0xfebe7d18u)))), (ushort *)((undefined *)camry_host_ptr(0x2baa6u)));
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x3ad8))))) = 0;
LAB_0004781c:
  f33_publish_shared_snapshot_monitor_status(8,(*((uint *)camry_host_ptr((uint32_t)(puVar1 + -0x3ae8)))));
  return;
}



/* Exact slot0/1 callback predicate. Return11/22/33/44 protocol; software source, qualification and
   retained-snapshot conditions are not physical freshness guarantees. ChannelA bit2 snapshot change
   with initial sticky evidence admission; tracks source generation. */

uint f33_classify_snapshot_bit2_a(void)

{
  uint uVar1;
  
  if (DAT_febe6320 == DAT_febe7d29) {
    if ((DAT_febe7b48 == 'Z') && (DAT_febe7b49 == 'Z')) {
      uVar1 = 0x11;
    }
    else {
      uVar1 = 0x33;
    }
  }
  else {
    uVar1 = 0x22;
  }
  DAT_febe7d29 = DAT_febe6320;
  return uVar1;
}



/* Exact slot0/1 callback predicate. Return11/22/33/44 protocol; software source, qualification and
   retained-snapshot conditions are not physical freshness guarantees. ChannelA confirmed bit2
   predicate drops initial evidence admission and refreshes snapshot. */

uint f33_classify_snapshot_bit2_recovery_a(void)

{
  uint uVar1;
  
  uVar1 = 0x11;
  if (DAT_febe6320 != DAT_febe7d29) {
    uVar1 = 0x22;
  }
  DAT_febe7d29 = DAT_febe6320;
  return uVar1;
}



/* f33_report_diagnostic_healthy_observed(0x16e); whole-body shape-verified. The literal is the
   encoded diagnostic event, not a recovered OEM name. */

void f33_report_diagnostic_healthy_observed_16e_4787a(void)

{
  f33_report_diagnostic_healthy_observed(0x16e);
  return;
}



void FUN_0004788a(void)

{
  byte bVar1;
  short sVar2;
  uint32_t puVar3;
  sVar2 = DAT_febe71ec;
  puVar3 = 0xfebeb800u;
  bVar1 = f33_shared_snapshot_status[9] |
          f33_shared_snapshot_status[3] | f33_shared_snapshot_status[1];
  f33_report_diagnostic_event_failure(0x16d,10);
  if ((((bVar1 & 0x22) == 0x22) || ((bVar1 & 0x44) == 0x44)) || (sVar2 != 0)) {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x3ad8))))) = 0x5a;
  }
  return;
}



/* Slot0 callback in the retained/escalation family; action and diagnostic reporting remain
   independent. See exact callback vector and shared-monitor composition report. A bit2 retained
   callback requests escalation on opposite-group complete22/44 or any nonzero qualification word;
   not only its own bit. */

void f33_request_shared_monitor_escalation_bit2_a(void)

{
  byte bVar1;
  
  bVar1 = f33_shared_snapshot_status[3] | f33_shared_snapshot_status[1] |
          f33_shared_snapshot_status[9];
  if ((((bVar1 & 0x22) == 0x22) || ((bVar1 & 0x44) == 0x44)) || (DAT_febe71ec != 0)) {
    DAT_febe7d28 = 0x5a;
  }
  return;
}



/* f33_report_diagnostic_event_pass(0x16d); whole-body shape-verified. The literal is the encoded
   diagnostic event, not a recovered OEM name. */

void f33_report_diagnostic_event_pass_16d_47902(void)

{
  f33_report_diagnostic_event_pass(0x16d);
  return;
}



/* f33_report_diagnostic_event_failure(0x16e,10); whole-body shape-verified. The literal is the
   encoded diagnostic event, not a recovered OEM name. */

void f33_report_diagnostic_event_failure_16e_10_47912(void)

{
  f33_report_diagnostic_event_failure(0x16e,10);
  return;
}



void FUN_00047924(void)

{
  FUN_0006b98a(((undefined4 *)camry_host_ptr((uint32_t)((0xfebe7d2cu)))));
  return;
}



void FUN_00047934(void)

{
  FUN_0006b98a(((undefined4 *)camry_host_ptr((uint32_t)((0xfebe7d2cu)))));
  return;
}



void FUN_00047944(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  if (DAT_febe8a24 != 'Z') {
    return;
  }
  if (DAT_0002bca4 == 'Z') {
    FUN_0006b98a(((undefined4 *)camry_host_ptr((uint32_t)((0xfebe7d2cu)))));
  }
  else {
    if ((DAT_febeeb85 == 'Z') && ((DAT_febe71ec >> 6 & 1) == 0)) {
      puVar1 = 0xfebeb800u;
      f33_step_escalating_monitor
                (((F33EscalatingMonitorState *)camry_host_ptr((uint32_t)((0xfebe7d2cu)))), (ushort *)((undefined *)camry_host_ptr(0x2bab6u)), 
                 (uint *)&PTR_f33_classify_snapshot_bit2_b_00028f90);
      if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x3ac4))))) == 'Z') {
        f33_force_monitor_escalation
                  (((F33EscalatingMonitorState *)camry_host_ptr((uint32_t)((0xfebe7d2cu)))), (ushort *)((undefined *)camry_host_ptr(0x2bab6u)), 
                   (uint *)&PTR_f33_classify_snapshot_bit2_b_00028f90);
      }
      goto LAB_000479b8;
    }
    f33_retain_disabled_escalating_monitor(((F33EscalatingMonitorState *)camry_host_ptr((uint32_t)((0xfebe7d2cu)))), (ushort *)((undefined *)camry_host_ptr(0x2bab6u)));
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x3ac4))))) = 0;
LAB_000479b8:
  f33_publish_shared_snapshot_monitor_status(9,(*((uint *)camry_host_ptr((uint32_t)(puVar1 + -0x3ad4)))));
  return;
}



/* Exact slot0/1 callback predicate. Return11/22/33/44 protocol; software source, qualification and
   retained-snapshot conditions are not physical freshness guarantees. ChannelB bit2 snapshot change
   with initial sticky admission. */

uint f33_classify_snapshot_bit2_b(void)

{
  uint uVar1;
  
  if (DAT_febe6338 == DAT_febe7d3d) {
    if ((DAT_febe7b48 == 'Z') && (DAT_febe7b49 == 'Z')) {
      uVar1 = 0x11;
    }
    else {
      uVar1 = 0x33;
    }
  }
  else {
    uVar1 = 0x22;
  }
  DAT_febe7d3d = DAT_febe6338;
  return uVar1;
}



/* Exact slot0/1 callback predicate. Return11/22/33/44 protocol; software source, qualification and
   retained-snapshot conditions are not physical freshness guarantees. ChannelB confirmed bit2
   predicate refreshes generation and classifies change without initial sticky gate. */

uint f33_classify_snapshot_bit2_recovery_b(void)

{
  uint uVar1;
  
  uVar1 = 0x11;
  if (DAT_febe6338 != DAT_febe7d3d) {
    uVar1 = 0x22;
  }
  DAT_febe7d3d = DAT_febe6338;
  return uVar1;
}



/* f33_report_diagnostic_healthy_observed(0x170); whole-body shape-verified. The literal is the
   encoded diagnostic event, not a recovered OEM name. */

void f33_report_diagnostic_healthy_observed_170_47a16(void)

{
  f33_report_diagnostic_healthy_observed(0x170);
  return;
}



void FUN_00047a26(void)

{
  byte bVar1;
  short sVar2;
  uint32_t puVar3;
  sVar2 = DAT_febe71ec;
  puVar3 = 0xfebeb800u;
  bVar1 = f33_shared_snapshot_status[8] |
          f33_shared_snapshot_status[2] | f33_shared_snapshot_status[0];
  f33_report_diagnostic_event_failure(0x16f,10);
  if ((((bVar1 & 0x22) == 0x22) || ((bVar1 & 0x44) == 0x44)) || (sVar2 != 0)) {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x3ac4))))) = 0x5a;
  }
  return;
}



/* Slot0 callback in the retained/escalation family; action and diagnostic reporting remain
   independent. See exact callback vector and shared-monitor composition report. B bit2 retained
   callback requests escalation on opposite-group complete22/44 or any nonzero qualification word;
   not only its own bit. */

void f33_request_shared_monitor_escalation_bit2_b(void)

{
  byte bVar1;
  
  bVar1 = f33_shared_snapshot_status[2] | f33_shared_snapshot_status[0] |
          f33_shared_snapshot_status[8];
  if ((((bVar1 & 0x22) == 0x22) || ((bVar1 & 0x44) == 0x44)) || (DAT_febe71ec != 0)) {
    DAT_febe7d3c = 0x5a;
  }
  return;
}



/* f33_report_diagnostic_event_pass(0x16f); whole-body shape-verified. The literal is the encoded
   diagnostic event, not a recovered OEM name. */

void f33_report_diagnostic_event_pass_16f_47a9e(void)

{
  f33_report_diagnostic_event_pass(0x16f);
  return;
}



/* f33_report_diagnostic_event_failure(0x170,10); whole-body shape-verified. The literal is the
   encoded diagnostic event, not a recovered OEM name. */

void f33_report_diagnostic_event_failure_170_10_47aae(void)

{
  f33_report_diagnostic_event_failure(0x170,10);
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_47ac0(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_47ac2(void)

{
  return;
}



void FUN_00047ac4(void)

{
  DAT_febe7d40 = 0;
  if (DAT_febe8026 < 0x10) {
    DAT_febe7d40 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x212b8u + (uint32_t)(DAT_febe8026) * 1u))));
  }
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_47adc(void)

{
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_47ade(void)

{
  return;
}



void FUN_00047ae0(void)

{
  bool bVar1;
  bool bVar2;
  bool bVar3;
  char cVar4;
  uint32_t puVar5;
  undefined2 uStack_e;
  
  cVar4 = DAT_febe8052;
  puVar5 = 0xfebeb800u;
  bVar1 = DAT_febe8052 == '\0';
  bVar2 = DAT_febe7fe0 != '\x02';
  FUN_0006a5fa((int)DAT_febe8048,&uStack_e);
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar5 + -0x3aba)))) = uStack_e;
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x3000u + (uint32_t)((int)(puVar5 + 1)))))) == (code)0x5a) {
    bVar3 = cVar4 != '\0';
    if ((bVar1) && (bVar3 = false, (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x37b2))))) == '\0')) {
      bVar3 = bVar2;
    }
  }
  else {
    bVar3 = false;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x3abc))))) = bVar3;
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_47b3a(void)

{
  return;
}



/* Constant-block fill: 20 literal assignments into one contiguous cell block; shape-verified.
   Literals are default/reset values; cell meanings are not recovered. */

void f33_fill_constant_block_47b3c(void)

{
  DAT_febe7d48 = 0;
  DAT_febe7d49 = 0;
  DAT_febe7d4a = 0;
  DAT_febe7d4c = 0;
  DAT_febe7d4e = 0;
  DAT_febe7d50 = 0;
  DAT_febe7d52 = 0;
  DAT_febe7d54 = 0;
  DAT_febe7d56 = 0;
  DAT_febe7d58 = 0;
  DAT_febe7d5a = 0;
  DAT_febe7d5c = 0;
  DAT_febe7d5e = 0;
  DAT_febe7d60 = 0;
  DAT_febe7d62 = 0;
  DAT_febe7d64 = 0;
  DAT_febe7d66 = 0;
  DAT_febe7d68 = 0;
  DAT_febe7d6c = 0;
  DAT_febe7d70 = 0;
  return;
}



int FUN_00047b6a(void)

{
  return (int)DAT_febe689a;
}



/* WARNING: Removing unreachable block (ram,0x00047cf4) */
/* WARNING: Removing unreachable block (ram,0x00047ce8) */
/* WARNING: Removing unreachable block (ram,0x00047ce4) */
/* WARNING: Removing unreachable block (ram,0x00047ce0) */
/* WARNING: Removing unreachable block (ram,0x00047c74) */
/* WARNING: Removing unreachable block (ram,0x00047c68) */
/* WARNING: Removing unreachable block (ram,0x00047c64) */
/* WARNING: Removing unreachable block (ram,0x00047c60) */
/* WARNING: Removing unreachable block (ram,0x00047bd6) */
/* WARNING: Removing unreachable block (ram,0x00047bd2) */

void FUN_00047b70(void)

{
  short sVar1;
  char cVar2;
  short sVar3;
  int iVar4;
  uint32_t puVar5;
  short sVar6;
  undefined2 uVar7;
  int iVar8;
  int iVar9;
  int iVar10;
  undefined *puVar11;
  int iVar12;
  short local_14;
  short sStack_12;
  short sStack_10;
  short sStack_e;
  
  iVar4 = DAT_febe7d94;
  puVar5 = 0xfebeb800u;
  iVar12 = (int)DAT_febe5f36;
  sVar6 = FUN_00047b6a();
  sVar1 = DAT_00031e48;
  cVar2 = DAT_0002fbd4;
  iVar9 = (int)DAT_00031e4a;
  sVar3 = sVar6 + (short)(iVar4 * 5);
  iVar10 = iVar9;
  if (iVar12 - iVar9 < 0 != (iVar12 < 0 != iVar9 < 0 && iVar9 < 0 == iVar12 - iVar9 < 0)) {
    iVar10 = iVar12;
  }
  iVar8 = -iVar9;
  if (iVar10 + iVar9 < 0 == (iVar10 < 0 != iVar8 < 0 && iVar8 < 0 == iVar10 + iVar9 < 0)) {
    iVar8 = iVar10;
  }
  iVar9 = (int)DAT_00031e4c;
  iVar10 = iVar9;
  if (iVar12 - iVar9 < 0 != (iVar12 < 0 != iVar9 < 0 && iVar9 < 0 == iVar12 - iVar9 < 0)) {
    iVar10 = iVar12;
  }
  iVar12 = -iVar9;
  if (iVar10 + iVar9 < 0 == (iVar10 < 0 != iVar12 < 0 && iVar12 < 0 == iVar10 + iVar9 < 0)) {
    iVar12 = iVar10;
  }
  iVar10 = (int)DAT_00031e46;
  (*((short *)camry_host_ptr((uint32_t)(puVar5 + -0x3ab6)))) = sVar3;
  (*((short *)camry_host_ptr((uint32_t)(puVar5 + -0x3a9a)))) = sVar6;
  (*((int *)camry_host_ptr((uint32_t)(puVar5 + -15000)))) = iVar4 * 5;
  iVar4 = (int)(short)((iVar10 * (short)iVar8 * 5) / 0x400) + (int)sVar3;
  (*((int *)camry_host_ptr((uint32_t)(puVar5 + -0x3a94)))) = iVar4;
  iVar10 = (int)(short)(((int)(short)iVar12 * (int)sVar1) / 0x400) + (int)sVar3;
  (*((int *)camry_host_ptr((uint32_t)(puVar5 + -0x3a90)))) = iVar10;
  if (cVar2 == '\0') {
    iVar9 = 0;
  }
  else {
    iVar9 = 0xaab;
    if (cVar2 != 'Z') {
      iVar9 = -0xaab;
    }
  }
  sVar1 = (short)iVar9;
  (*((short *)camry_host_ptr((uint32_t)(puVar5 + -0x3aa8)))) = sVar1 + (short)iVar4;
  (*((short *)camry_host_ptr((uint32_t)(puVar5 + -0x3ab4)))) = (short)(iVar4 - iVar9);
  sVar3 = (short)iVar10;
  (*((short *)camry_host_ptr((uint32_t)(puVar5 + -0x3aae)))) = sVar3 - sVar1;
  (*((short *)camry_host_ptr((uint32_t)(puVar5 + -0x3aa2)))) = sVar1 + sVar3;
  if (cVar2 == '\0') {
    puVar11 = ((undefined *)camry_host_ptr((uint32_t)(0x10000)));
    iVar10 = 0;
  }
  else {
    puVar11 = ((undefined *)camry_host_ptr(0xddb4u));
    iVar10 = -0x8000;
    if (cVar2 == 'Z') {
      iVar10 = 0x8000;
    }
  }
  FUN_00070e32(iVar4 - iVar9 & 0xffff,&local_14,&sStack_12);
  (*((short *)camry_host_ptr((uint32_t)(puVar5 + -0x3ab2)))) = local_14;
  (*((short *)camry_host_ptr((uint32_t)(puVar5 + -0x3ab0)))) = sStack_12;
  iVar9 = (sStack_12 * iVar10) / 0x10000 + ((int)local_14 * (int)camry_host_addr(puVar11)) / 0x10000;
  iVar4 = ((int)sStack_12 * (int)camry_host_addr(puVar11)) / 0x10000 - (local_14 * iVar10) / 0x10000;
  if (iVar9 + -0x7fff < 0 == (iVar9 < 0 && -1 < iVar9 + -0x7fff) && iVar9 != 0x7fff) {
    uVar7 = 0x7fff;
  }
  else if (iVar9 + 0x8000 < 0 == (-1 < iVar9 && iVar9 + 0x8000 < 0)) {
    uVar7 = (undefined2)iVar9;
  }
  else {
    uVar7 = 0x8000;
  }
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar5 + -0x3aa6)))) = uVar7;
  if (iVar4 + -0x7fff < 0 == (iVar4 < 0 && -1 < iVar4 + -0x7fff) && iVar4 != 0x7fff) {
    iVar4 = 0x7fff;
  }
  else if (iVar4 + 0x8000 < 0 != (-1 < iVar4 && iVar4 + 0x8000 < 0)) {
    iVar4 = -0x8000;
  }
  (*((short *)camry_host_ptr((uint32_t)(puVar5 + -0x3aa4)))) = (short)iVar4;
  FUN_00070e32((*((undefined2 *)camry_host_ptr((uint32_t)(puVar5 + -0x3aae)))),&sStack_10,&sStack_e);
  (*((short *)camry_host_ptr((uint32_t)(puVar5 + -0x3aac)))) = sStack_10;
  (*((short *)camry_host_ptr((uint32_t)(puVar5 + -0x3aaa)))) = sStack_e;
  iVar9 = (sStack_e * iVar10) / 0x10000 + ((int)sStack_10 * (int)camry_host_addr(puVar11)) / 0x10000;
  iVar4 = ((int)sStack_e * (int)camry_host_addr(puVar11)) / 0x10000 - (sStack_10 * iVar10) / 0x10000;
  if (iVar9 + -0x7fff < 0 == (iVar9 < 0 && -1 < iVar9 + -0x7fff) && iVar9 != 0x7fff) {
    uVar7 = 0x7fff;
  }
  else if (iVar9 + 0x8000 < 0 == (-1 < iVar9 && iVar9 + 0x8000 < 0)) {
    uVar7 = (undefined2)iVar9;
  }
  else {
    uVar7 = 0x8000;
  }
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar5 + -0x3aa0)))) = uVar7;
  if (iVar4 + -0x7fff < 0 == (iVar4 < 0 && -1 < iVar4 + -0x7fff) && iVar4 != 0x7fff) {
    uVar7 = 0x7fff;
  }
  else if (iVar4 + 0x8000 < 0 == (-1 < iVar4 && iVar4 + 0x8000 < 0)) {
    uVar7 = (undefined2)iVar4;
  }
  else {
    uVar7 = 0x8000;
  }
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar5 + -0x3a9e)))) = uVar7;
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_47d32(void)

{
  return;
}



/* Single constant publisher: DAT_febe7d74 = 0; Shape-classified from the canonical corpus; the
   target cell is not yet named, so the written state's meaning is unknown. */

void FUN_00047d34(void)

{
  DAT_febe7d74 = 0;
  return;
}



void FUN_00047d3a(void)

{
  if (DAT_febe7d94 + -0x3330000 < 0 == (DAT_febe7d94 < 0 && -1 < DAT_febe7d94 + -0x3330000)) {
    DAT_febe7d74 = DAT_febe7d94 + -0x6660000;
  }
  else {
    DAT_febe7d74 = DAT_febe7d94;
    if (DAT_febe7d94 + 0x3330000 < 0 != (-1 < DAT_febe7d94 && DAT_febe7d94 + 0x3330000 < 0)) {
      DAT_febe7d74 = DAT_febe7d94 + 0x6660000;
    }
  }
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_47d60(void)

{
  return;
}



/* WARNING: This is an inlined function */
/* Channel1 selects8250, all others824C. Store7D90 and RETURN the selected halfword inR10. The real
   leaf preserves caller R7, reused as the correction-table bank. Select824C unless channel==1
   then8250; store7D90 and return u16 while preserving caller R7. Inline the real leaf to retain the
   bank input into the next call. */

ushort f33_select_electrical_angle_sample(uchar channel)

{
  DAT_febe7d90 = DAT_febe824c;
  if (channel == '\x01') {
    DAT_febe7d90 = DAT_febe8250;
  }
  return DAT_febe7d90;
}



/* WARNING: Inlined function: f33_select_electrical_angle_sample */

void FUN_00047d78(void)

{
  DAT_febe7d90 = DAT_febe824c;
  if ((DAT_febe71ec & 0x80) == 0x80) {
    DAT_febe7d90 = DAT_febe8250;
  }
  DAT_febe7d94 = (uint)DAT_febe7d90;
  DAT_febe7da0 = (uint)DAT_febe7d90;
  return;
}



/* Far-call trampoline: prepare {lp},0 / jarl 0x47D78 / dispose 0,{lp},lp; byte-verified against the
   exact image. Forwards with registers and stack unchanged; marked as a thunk. Forwarding shape
   machine-verified; target semantics not recovered. */

void thunk_FUN_00047d78(void)

{
  FUN_00047d78();
  return;
}



/* WARNING: Removing unreachable block (ram,0x00047de4) */
/* When enabled==5A subtract signed-byte circular interpolation at A0C0+256*bank. Index255 wraps
   to0; signed division256 truncates toward zero. Return narrowed signed16 phase. Enabled5A
   interpolates signed-byte curve A0C0+bank*100 with circular255-to0 indexing and signed division
   truncating toward zero. Subtract correction from phase and narrow signed16; no mechanical-angle
   unit inference. */

short f33_correct_electrical_angle_sample(uchar enabled,uchar bank,short phase)

{
  char cVar1;
  short sVar2;
  int iVar3;
  
  if (enabled == 'Z') {
    iVar3 = camry_host_addr(FUN_000567be());
    iVar3 = (uint)bank * 0x100 + iVar3 + 0xc0;
    cVar1 = (*((char *)camry_host_ptr((uint32_t)((uint)((ushort)phase >> 8) + iVar3))));
    sVar2 = (short)((int)(((int)(*((char *)camry_host_ptr((uint32_t)((((ushort)phase >> 8) + 1 & 0xff) + iVar3)))) - (int)cVar1) *
                         ((int)phase & 0xffU)) / 0x100) + (short)cVar1;
  }
  else {
    sVar2 = 0;
  }
  return phase - sVar2;
}



/* Wrap low-half phase delta into[-32768,32768), retain the coarse accumulator and recenter
   at+-03330000 with span06660000. Software coarse count is not a proven mechanical turn count. */

int f33_accumulate_electrical_angle(int previous,short phase)

{
  int iVar1;
  int iVar2;
  int iVar3;
  
  iVar2 = (int)phase - (int)(short)previous;
  if (iVar2 + -0x8000 < 0 == (iVar2 < 0 && -1 < iVar2 + -0x8000)) {
    iVar2 = iVar2 + -0x10000;
  }
  else if (iVar2 + 0x8000 < 0 != (-1 < iVar2 && iVar2 + 0x8000 < 0)) {
    iVar2 = iVar2 + 0x10000;
  }
  iVar1 = 0x3330000 - iVar2;
  iVar3 = previous + -0x6660000;
  if ((iVar1 - previous < 0 == (iVar1 < 0 != previous < 0 && previous < 0 == iVar1 - previous < 0)
       && iVar1 != previous) &&
     (iVar1 = -0x3330000 - iVar2, iVar3 = previous,
     iVar1 - previous < 0 == (iVar1 < 0 != previous < 0 && previous < 0 == iVar1 - previous < 0) &&
     iVar1 != previous)) {
    iVar3 = previous + 0x6660000;
  }
  return (uint)(ushort)phase | iVar2 + iVar3 & 0xffff0000U;
}



/* WARNING: Inlined function: f33_select_electrical_angle_sample */
/* Select by71EC.bit7, correct using6A7B and the retained channel bank, accumulate into7DA0 and
   publish7D92. Normally copy to7D78/7D94;7566==5A substitutes7576/7578 only in publication. Feeds
   rotating-frame coefficients; physical sensor mount is not inferred. Native bank1 endpoint
   composition preserves bank through the real selector; FF80 interpolates signed correction9 and
   produces phase-137/accumulator1FF77. Separate7566 substitution gate affects publication rather
   than internal accumulation. */

void f33_update_electrical_angle_feedback(void)

{
  char cVar1;
  uint32_t puVar2;
  uint uVar3;
  short phase;
  int iVar4;
  
  iVar4 = DAT_febe7da0;
  puVar2 = 0xfebeb800u;
  uVar3 = (DAT_febe71ec & 0x80) >> 7;
  DAT_febe7d90 = DAT_febe824c;
  if (uVar3 == 1) {
    DAT_febe7d90 = DAT_febe8250;
  }
  phase = f33_correct_electrical_angle_sample(DAT_febe6a7b,(uchar)uVar3,DAT_febe7d90);
  iVar4 = f33_accumulate_electrical_angle(iVar4,phase);
  cVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbd66u + (uint32_t)((int)puVar2) * 1u))));
  (*((short *)camry_host_ptr((uint32_t)(puVar2 + -0x3a6e)))) = phase;
  (*((int *)camry_host_ptr((uint32_t)(puVar2 + -0x3a60)))) = iVar4;
  if (cVar1 == 'Z') {
    phase = (*((short *)camry_host_ptr((uint32_t)((0xffffbd76u + (uint32_t)((int)puVar2))))));
    iVar4 = (*((int *)camry_host_ptr((uint32_t)((0xffffbd78u + (uint32_t)((int)puVar2))))));
  }
  (*((short *)camry_host_ptr((uint32_t)(puVar2 + -0x3a88)))) = phase;
  (*((int *)camry_host_ptr((uint32_t)(puVar2 + -0x3a6c)))) = iVar4;
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_47ea2(void)

{
  return;
}



/* Constant-block fill: 5 literal assignments into one contiguous cell block; shape-verified.
   Literals are default/reset values; cell meanings are not recovered. */

void f33_fill_constant_block_47ea4(void)

{
  DAT_febe5f34 = 0;
  DAT_febe5f36 = 0;
  DAT_febe5f40 = 0;
  DAT_febe5f38 = DAT_febe7d74;
  DAT_febe5f3c = 0;
  return;
}



/* WARNING: Removing unreachable block (ram,0x00047f7e) */
/* WARNING: Removing unreachable block (ram,0x00047f30) */
/* WARNING: Removing unreachable block (ram,0x00047f28) */
/* WARNING: Removing unreachable block (ram,0x00047ece) */

void FUN_00047eb8(void)

{
  int iVar1;
  uint uVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  
  iVar4 = DAT_febe5f38;
  if (DAT_febe8a14 == '\x01') {
    iVar3 = (int)DAT_febe5f36;
    if ((short)(DAT_febe5f3c / 0x10000) != iVar3) {
      iVar3 = (int)DAT_febe5f34;
      DAT_febe5f3c = iVar3 << 0x10;
    }
    DAT_febe5f38 = DAT_febe7d74;
    DAT_febe5f40 = DAT_febe7d74 - iVar4;
    if (DAT_febe5f40 + 0x3330000 < 0 == (-1 < DAT_febe5f40 && DAT_febe5f40 + 0x3330000 < 0)) {
      if (DAT_febe5f40 + -0x3330000 < 0 == (DAT_febe5f40 < 0 && -1 < DAT_febe5f40 + -0x3330000)) {
        DAT_febe5f40 = DAT_febe5f40 + -0x6660000;
      }
    }
    else {
      DAT_febe5f40 = DAT_febe5f40 + 0x6660000;
    }
    if (DAT_febe5f40 + -0x10000 < 0 == (DAT_febe5f40 < 0 && -1 < DAT_febe5f40 + -0x10000)) {
      DAT_febe5f40 = 0x10000;
    }
    if (DAT_febe5f40 + 0x10000 < 0 != (-1 < DAT_febe5f40 && DAT_febe5f40 + 0x10000 < 0)) {
      DAT_febe5f40 = -0x10000;
    }
    iVar4 = (DAT_febe5f40 * 10000) / 0x1000;
    if (iVar4 + 0x7fff < 0 == (-1 < iVar4 && iVar4 + 0x7fff < 0) && iVar4 != -0x7fff) {
      if (iVar4 + -0x7fff < 0 == (iVar4 < 0 && -1 < iVar4 + -0x7fff) && iVar4 != 0x7fff) {
        iVar4 = 0x7fff;
      }
      else {
        iVar4 = (int)(short)iVar4;
      }
    }
    else {
      iVar4 = -0x7fff;
    }
    uVar2 = (uint)DAT_00031e50;
    if (uVar2 == 0) {
      iVar5 = iVar3 << 0x10;
      iVar1 = iVar4 << 0x10;
    }
    else {
      iVar5 = iVar3 * uVar2;
      iVar1 = iVar4 * uVar2;
    }
    DAT_febe5f34 = (short)iVar4;
    DAT_febe5f3c = iVar1 + (DAT_febe5f3c - iVar5);
    DAT_febe5f36 = (short)(DAT_febe5f3c / 0x10000);
    DAT_febe5f44 = (DAT_febe5f36 - iVar3) * 0x9c4;
  }
  return;
}



/* Two-byte return-only stub: single jmp [lp] (7f00); byte-verified against the exact image.
   Referenced placeholder implementing no behavior; structural classification, not individually
   executed. */

void f33_return_only_stub_47f96(void)

{
  return;
}



void FUN_00047f98(void)

{
  uint uVar1;
  uint uVar2;
  uint uVar3;
  uint uVar4;
  uint uVar5;
  uint32_t puVar6;
  int iVar7;
  uint uVar8;
  
  puVar6 = 0xfebeb800u;
  iVar7 = FUN_000588b6();
  if (iVar7 == 0) {
    uVar1 = (uint)(*((ushort *)camry_host_ptr((uint32_t)(puVar6 + -0x35f4)))) * (uint)DAT_0002fbe2;
    uVar2 = (uint)DAT_0002fbe2 * (uint)(*((ushort *)camry_host_ptr((uint32_t)(puVar6 + -0x35f2))));
    uVar3 = (uint)DAT_0002fbe4;
    uVar4 = (uint)DAT_0002fbe6;
    uVar8 = (uint)DAT_0002fbea;
    uVar5 = (uint)DAT_0002fbe8;
    (*((short *)camry_host_ptr((uint32_t)(puVar6 + -0x3a4c)))) = (short)((*((ushort *)camry_host_ptr((uint32_t)(puVar6 + -0x35da)))) * uVar8 >> 0x10);
    (*((short *)camry_host_ptr((uint32_t)(puVar6 + -0x3a50)))) = (short)(uVar5 * (*((ushort *)camry_host_ptr((uint32_t)(puVar6 + -0x35f0)))) >> 0x10);
    (*((short *)camry_host_ptr((uint32_t)(puVar6 + -0x3a54)))) = (short)(uVar4 * (*((ushort *)camry_host_ptr((uint32_t)(puVar6 + -0x35de)))) >> 0x10);
    (*((short *)camry_host_ptr((uint32_t)(puVar6 + -0x3a56)))) = (short)(uVar3 * (*((ushort *)camry_host_ptr((uint32_t)(puVar6 + -0x35e0)))) >> 0x10);
    (*((short *)camry_host_ptr((uint32_t)(puVar6 + -0x3a58)))) = (short)(uVar2 >> 0x10);
    (*((short *)camry_host_ptr((uint32_t)(puVar6 + -0x3a5a)))) = (short)(uVar1 >> 0x10);
    (*((uint *)camry_host_ptr((uint32_t)(puVar6 + -0x3a38)))) = uVar5 * (*((ushort *)camry_host_ptr((uint32_t)(puVar6 + -0x35f0)))) & 0xffff0000;
    (*((uint *)camry_host_ptr((uint32_t)(puVar6 + -0x3a3c)))) = uVar4 * (*((ushort *)camry_host_ptr((uint32_t)(puVar6 + -0x35de)))) & 0xffff0000;
    (*((uint *)camry_host_ptr((uint32_t)(puVar6 + -0x3a40)))) = uVar3 * (*((ushort *)camry_host_ptr((uint32_t)(puVar6 + -0x35e0)))) & 0xffff0000;
    (*((uint *)camry_host_ptr((uint32_t)(puVar6 + -0x3a44)))) = uVar2 & 0xffff0000;
    (*((uint *)camry_host_ptr((uint32_t)(puVar6 + -0x3a48)))) = uVar1 & 0xffff0000;
    (*((short *)camry_host_ptr((uint32_t)(puVar6 + -0x3a4a)))) = (short)((*((ushort *)camry_host_ptr((uint32_t)(puVar6 + -0x35d8)))) * uVar8 >> 0x10);
  }
  return;
}


