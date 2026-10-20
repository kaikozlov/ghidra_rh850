#include "common.h"

void return_only_stub_3d026(void)

{
  return;
}

void return_only_stub_3d028(void)

{
  return;
}

void publish_105_107_healthy_from_e91c_signature_3d02a(void)

{
  char cVar1;
  uint32_t puVar2;
  char cVar3;
  char cVar4;
  
  cVar1 = DAT_febe802d;
  cVar3 = DAT_febe7471;
  cVar4 = DAT_febe7470;
  puVar2 = 0xfebeb800u;
  if (DAT_febee91c == 0x55aaaa55) {
    puVar2 = 0xfebeb800u;
    report_diagnostic_healthy_observed(0x107);
    cVar3 = 'Z';
    if ((cVar1 == '\0') && (cVar4 != 'Z')) {
      report_diagnostic_healthy_observed(0x105);
      cVar4 = cVar3;
    }
  }
  else if (DAT_febee91c == -0x55aaaa56) {
    puVar2 = 0xfebeb800u;
    report_diagnostic_healthy_observed(0x105);
    cVar4 = 'Z';
    if ((cVar1 == '\0') && (cVar3 != 'Z')) {
      report_diagnostic_healthy_observed(0x107);
      cVar3 = cVar4;
    }
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbc70u + (uint32_t)((int)puVar2) * 1u)))) = cVar4;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbc71u + (uint32_t)((int)puVar2) * 1u)))) = cVar3;
  return;
}

void publish_source_family_fault_edges(void)

{
  char cVar1;
  char cVar2;
  char cVar3;
  char cVar4;
  char cVar5;
  char cVar6;
  char cVar7;
  char cVar8;
  uint32_t puVar9;
  uchar status;
  uchar status_00;
  uchar status_01;
  uchar status_02;
  uchar status_03;
  uchar status_04;
  uchar status_05;
  uchar status_06;
  char cVar10;
  char cVar11;
  char cVar12;
  char cVar13;
  char cVar14;
  char cVar15;
  char cVar16;
  char cVar17;
  
  cVar8 = DAT_febe7fb7;
  cVar7 = DAT_febe7fb6;
  cVar6 = DAT_febe7fb5;
  cVar5 = DAT_febe7fb4;
  cVar4 = DAT_febe7fb3;
  cVar3 = DAT_febe7fb2;
  cVar2 = DAT_febe7fb1;
  cVar1 = DAT_febe7fb0;
  cVar10 = DAT_febe746f;
  cVar14 = DAT_febe746e;
  cVar11 = DAT_febe746d;
  cVar15 = DAT_febe746c;
  cVar12 = DAT_febe746b;
  cVar16 = DAT_febe746a;
  cVar13 = DAT_febe7469;
  cVar17 = DAT_febe7468;
  puVar9 = 0xfebeb800u;
  publish_105_107_healthy_from_e91c_signature_3d02a();
  if (cVar1 == 'Z') {
    if (cVar17 != 'Z') {
      report_diagnostic_event_failure(0x104,0x32);
      cVar17 = 'Z';
    }
    status_06 = '\"';
  }
  else {
    if (cVar17 == 'Z') {
      report_diagnostic_event_pass(0x104);
      cVar17 = '\0';
    }
    status_06 = '\0';
  }
  if (cVar3 == 'Z') {
    if (cVar16 != 'Z') {
      report_diagnostic_event_failure(0x106,0x32);
      cVar16 = 'Z';
    }
    status_05 = '\"';
  }
  else {
    if (cVar16 == 'Z') {
      report_diagnostic_event_pass(0x106);
      cVar16 = '\0';
    }
    status_05 = '\0';
  }
  if (cVar5 == 'Z') {
    if (cVar15 != 'Z') {
      report_diagnostic_event_failure(0x108,0x32);
      cVar15 = 'Z';
    }
    status = '\"';
  }
  else {
    if (cVar15 == 'Z') {
      report_diagnostic_event_pass(0x108);
      cVar15 = '\0';
    }
    status = '\0';
  }
  if (cVar7 == 'Z') {
    if (cVar14 != 'Z') {
      report_diagnostic_event_failure(0x10a,0x32);
      cVar14 = 'Z';
    }
    status_00 = '\"';
  }
  else {
    if (cVar14 == 'Z') {
      report_diagnostic_event_pass(0x10a);
      cVar14 = '\0';
    }
    status_00 = '\0';
  }
  if (cVar2 == 'Z') {
    if (cVar13 != 'Z') {
      report_diagnostic_event_failure(0x105,0x32);
      cVar13 = 'Z';
    }
    status_01 = '\"';
  }
  else {
    if (cVar13 == 'Z') {
      report_diagnostic_event_pass(0x105);
      cVar13 = '\0';
    }
    status_01 = '\0';
  }
  if (cVar4 == 'Z') {
    if (cVar12 != 'Z') {
      report_diagnostic_event_failure(0x107,0x32);
      cVar12 = 'Z';
    }
    status_02 = '\"';
  }
  else {
    if (cVar12 == 'Z') {
      report_diagnostic_event_pass(0x107);
      cVar12 = '\0';
    }
    status_02 = '\0';
  }
  if (cVar6 == 'Z') {
    if (cVar11 != 'Z') {
      report_diagnostic_event_failure(0x109,0x32);
      cVar11 = 'Z';
    }
    status_03 = '\"';
  }
  else {
    if (cVar11 == 'Z') {
      report_diagnostic_event_pass(0x109);
      cVar11 = '\0';
    }
    status_03 = '\0';
  }
  if (cVar8 == 'Z') {
    if (cVar10 != 'Z') {
      report_diagnostic_event_failure(0x10b,0x32);
      cVar10 = 'Z';
    }
    status_04 = '\"';
  }
  else {
    if (cVar10 == 'Z') {
      report_diagnostic_event_pass(0x10b);
      cVar10 = '\0';
    }
    status_04 = '\0';
  }
  set_communication_monitor_status(7,status_06);
  set_communication_monitor_status(9,status_05);
  set_communication_monitor_status(0xb,status);
  set_communication_monitor_status(0xd,status_00);
  set_communication_monitor_status(8,status_01);
  set_communication_monitor_status(10,status_02);
  set_communication_monitor_status(0xc,status_03);
  set_communication_monitor_status(0xe,status_04);
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbc68u + (uint32_t)((int)puVar9) * 1u)))) = cVar17;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbc6au + (uint32_t)((int)puVar9) * 1u)))) = cVar16;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbc6cu + (uint32_t)((int)puVar9) * 1u)))) = cVar15;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbc6eu + (uint32_t)((int)puVar9) * 1u)))) = cVar14;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbc69u + (uint32_t)((int)puVar9) * 1u)))) = cVar13;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbc6bu + (uint32_t)((int)puVar9) * 1u)))) = cVar12;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbc6du + (uint32_t)((int)puVar9) * 1u)))) = cVar11;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbc6fu + (uint32_t)((int)puVar9) * 1u)))) = cVar10;
  return;
}

void return_only_stub_3d318(void)

{
  return;
}

void return_only_stub_3d31a(void)

{
  return;
}

void set_communication_monitor_status(uint index,uchar status)

{
  if ((index & 0xff) < 0x19) {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe7476u + (uint32_t)(index & 0xff) * 1u)))) = status;
  }
  return;
}

void clear_7474_state_3d330(void)

{
  DAT_febe7474 = 0;
  return;
}

void set_7475_if_7486_equals_34_3d336(void)

{
  DAT_febe7475 = DAT_febe7486 == '\"';
  return;
}

void compose_communication_status_fault_actions(void)

{
  uint32_t puVar1;
  byte status;
  
  puVar1 = 0xfebeb800u;
  status = (byte)DAT_febe7f3a & 0x10;
  if ((DAT_febe7f3a & 0x1010) == 0) {
    thunk_clear_indexed_bef1_request_bef8e(0x0);
  }
  else {
    status = 0x22;
    thunk_set_indexed_bef1_request_to_5a_bef80(0);
  }
  set_communication_monitor_status(1,status);
  retain_and_clear_fault_record(0x10);
  if ((((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbc83u + (uint32_t)((int)puVar1) * 1u)))) |
       (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbc81u + (uint32_t)((int)puVar1) * 1u)))) |
       (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbc7fu + (uint32_t)((int)puVar1) * 1u)))) |
       (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbc7du + (uint32_t)((int)puVar1) * 1u)))) |
       (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbc7cu + (uint32_t)((int)puVar1) * 1u)))) |
       (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbc7au + (uint32_t)((int)puVar1) * 1u)))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbc78u + (uint32_t)((int)puVar1) * 1u)))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbc77u + (uint32_t)((int)puVar1) * 1u))))) &
      0x22) == 0x22) {
    encode_fault_action_kind('\x10','\x16');
  }
  if ((((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x3024))))) == 'Z') || ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x3c46))))) == 'Z')) &&
     (((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbc89u + (uint32_t)((int)puVar1) * 1u)))) & 0x22) == 0x22)) {
    encode_fault_action_kind('\x10','\x16');
  }
  if ((((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbc89u + (uint32_t)((int)puVar1) * 1u)))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbc76u + (uint32_t)((int)puVar1) * 1u)))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbc7cu + (uint32_t)((int)puVar1) * 1u)))))
      & 0x44) == 0x44) {
    encode_fault_action_kind('\x10','\x16');
  }
  select_current_fault_record(0x10);
  clear_7474_state_3d330();
  set_7475_if_7486_equals_34_3d336();
  return;
}

void reset_latched_monitor_febe7490(void)

{
  reset_latched_monitor((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe7490u)));
  return;
}

void reset_latched_monitor_febe7490_3d426(void)

{
  reset_latched_monitor((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe7490u)));
  return;
}

void update_received_content_monitor_a(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  if (DAT_0002bb48 == 'Z') {
    reset_latched_monitor((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe7490u)));
  }
  else {
    step_latched_monitor
              ((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe7490u)),(F33MonitorLimits *)((undefined *)camry_host_ptr(0x2b600u)),
               (F33TwoSidedMonitorCallbacks *)&PTR_classify_received_content_a_000280d4);
  }
  set_communication_monitor_status(0x10,(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbc90u + (uint32_t)((int)puVar1) * 1u)))));
  return;
}

uint classify_received_content_a(void)

{
  if ((internal_source_admission_state == '\0') && (DAT_febe8052 == '\0')) {
    if (DAT_febe804d == '\x01') {
      return 0x22;
    }
    return 0x11;
  }
  return 0x44;
}

void report_diagnostic_event_failure_de_32_3d49c(void)

{
  report_diagnostic_event_failure(0xde,0x32);
  return;
}

void reset_latched_monitor_febe749c(void)

{
  reset_latched_monitor((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe749cu)));
  return;
}

void reset_latched_monitor_febe749c_3d4c0(void)

{
  reset_latched_monitor((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe749cu)));
  return;
}

void update_received_content_monitor_b(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  if (DAT_0002bb4c == 'Z') {
    reset_latched_monitor((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe749cu)));
  }
  else {
    step_latched_monitor
              ((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe749cu)),(F33MonitorLimits *)((undefined *)camry_host_ptr(0x2b604u)),
               (F33TwoSidedMonitorCallbacks *)&PTR_classify_received_content_b_00028108);
  }
  set_communication_monitor_status(0x11,(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbc9cu + (uint32_t)((int)puVar1) * 1u)))));
  return;
}

uint classify_received_content_b(void)

{
  if ((internal_source_admission_state == '\0') && (DAT_febe8052 == '\0')) {
    if (DAT_febe804e == '\x01') {
      return 0x22;
    }
    return 0x11;
  }
  return 0x44;
}

void report_diagnostic_event_failure_df_32_3d536(void)

{
  report_diagnostic_event_failure(0xdf,0x32);
  return;
}

void return_only_stub_3d54a(void)

{
  return;
}

void return_only_stub_3d54c(void)

{
  return;
}

void report_6879_687a_fault_transitions_and_comm_status_3d54e(void)

{
  char cVar1;
  uchar status;
  uint32_t puVar2;
  char cVar3;
  char cVar4;
  
  status = DAT_febe687b;
  cVar1 = DAT_febe687a;
  cVar3 = DAT_febe679d;
  puVar2 = 0xfebeb800u;
  cVar4 = DAT_febe679c;
  if (DAT_febe6879 == 'Z') {
    if (DAT_febe679c != 'Z') {
      puVar2 = 0xfebeb800u;
      report_diagnostic_event_failure(0x97,0x32);
      increment_indexed_u16_counter_once_until_rearmed_545de(0xb);
      gate_indexed_event_payload_during_diagnostic_clears_51cf6(9,0x32);
      cVar4 = 'Z';
    }
  }
  else if (DAT_febe679c == 'Z') {
    puVar2 = 0xfebeb800u;
    report_diagnostic_event_pass(0x97);
    cVar4 = '\0';
  }
  if (cVar1 == 'Z') {
    if (cVar3 != 'Z') {
      report_diagnostic_event_failure(0x98,0x32);
      cVar3 = 'Z';
    }
  }
  else if (cVar3 == 'Z') {
    report_diagnostic_event_pass(0x98);
    cVar3 = '\0';
  }
  set_communication_monitor_status(6,status);
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x5064))))) = cVar4;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x5063))))) = cVar3;
  return;
}

void return_only_stub_3d5e2(void)

{
  return;
}

void report_8294_fault_bits_when_588b6_zero_3d5e4(void)

{
  uint uVar1;
  int iVar2;
  
  uVar1 = DAT_febe8294;
  iVar2 = test_redundant_status_a5_or_vote_error13_588b6();
  report_diagnostic_healthy_observed(0xe8);
  report_diagnostic_healthy_observed(0xd2);
  report_diagnostic_healthy_observed(0xc2);
  report_diagnostic_healthy_observed(0xd1);
  report_diagnostic_healthy_observed(0xc3);
  report_diagnostic_healthy_observed(0xec);
  if (iVar2 == 0) {
    if ((uVar1 >> 8 & 1) != 0) {
      report_diagnostic_event_failure(0xe1,0x32);
    }
    if ((uVar1 >> 0x10 & 1) != 0) {
      report_diagnostic_event_failure(0xe8,0x32);
    }
    if ((uVar1 >> 0x14 & 1) != 0) {
      report_diagnostic_event_failure(0xd2,0x32);
    }
    if ((uVar1 >> 0x18 & 1) != 0) {
      report_diagnostic_event_failure(0xc5,0x32);
    }
    if ((uVar1 >> 4 & 1) != 0) {
      report_diagnostic_event_failure(0xc2,0x32);
    }
    if ((uVar1 >> 0x1c & 1) != 0) {
      report_diagnostic_event_failure(0xd1,0x32);
    }
    if (SUB51(((uint5)uVar1 << 1) >> 0x20,0)) {
      report_diagnostic_event_failure(0xc3,0x32);
    }
  }
  return;
}

void publish_local_status_link_fault(void)

{
  uchar status;
  
  status = (uchar)(DAT_febe8294 & 1);
  if ((DAT_febe8294 & 1) != 0) {
    report_diagnostic_event_failure(0xec,0x32);
    status = '\"';
  }
  set_local_status_monitor_status(0,status);
  return;
}

void return_only_stub_3d6ce(void)

{
  return;
}

void return_only_stub_3d6d0(void)

{
  return;
}

void compose_local_status_fault_actions(void)

{
  uint32_t puVar1;
  uchar status;
  
  puVar1 = 0xfebeb800u;
  retain_and_clear_fault_record(0xc);
  if ((((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbcadu + (uint32_t)((int)puVar1) * 1u)))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbca9u + (uint32_t)((int)puVar1) * 1u)))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbca8u + (uint32_t)((int)puVar1) * 1u)))))
      & 0x22) == 0x22) {
    encode_fault_action_kind('\f','\x17');
  }
  select_current_fault_record(0xc);
  status = '\0';
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbcadu + (uint32_t)((int)puVar1) * 1u)))) != '\0' ||
      ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbca9u + (uint32_t)((int)puVar1) * 1u)))) != '\0' || (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbca8u + (uint32_t)((int)puVar1) * 1u)))) != '\0')) {
    status = '\x11';
  }
  set_diagnostic_cache_blocker('\0',status);
  return;
}

void set_local_status_monitor_status(uint index,uchar status)

{
  if ((index & 0xff) < 6) {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe74a8u + (uint32_t)(index & 0xff) * 1u)))) = status;
  }
  return;
}

void reset_latched_monitor_febe74b0(void)

{
  reset_latched_monitor((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe74b0u)));
  return;
}

void reset_latched_monitor_febe74b0_3d746(void)

{
  reset_latched_monitor((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe74b0u)));
  return;
}

void update_qualified_local_status_monitor(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  if (DAT_0002bb50 == 'Z') {
    reset_latched_monitor((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe74b0u)));
  }
  else {
    step_latched_monitor
              ((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe74b0u)),(F33MonitorLimits *)((undefined *)camry_host_ptr(0x2b608u)),
               (F33TwoSidedMonitorCallbacks *)&PTR_classify_qualified_local_status_0002813c);
  }
  set_local_status_monitor_status(5,(uchar)(*((undefined4 *)camry_host_ptr((uint32_t)((0xffffbcb0u + (uint32_t)((int)puVar1)))))));
  return;
}

uint classify_qualified_local_status(void)

{
  char cVar1;
  uint uVar2;
  
  cVar1 = DAT_febe65f1;
  if ((DAT_febe64d0 == '\x02') || (DAT_febe64d1 == '\x02')) {
    if (DAT_febe67a0 < DAT_0002b61e) {
      DAT_febe67a0 = DAT_febe67a0 + 1;
    }
    else {
      cVar1 = DAT_febe65f7;
      if (DAT_febe65f6 == 'Z') goto LAB_0003d7de;
    }
  }
  else {
    DAT_febe67a0 = 0;
  }
  if (cVar1 != 'Z') {
    return 0x44;
  }
LAB_0003d7de:
  uVar2 = 0x11;
  if (DAT_febe8278 == 'Z') {
    uVar2 = 0x22;
  }
  return uVar2;
}

void report_diagnostic_healthy_observed_f3_3d7f2(void)

{
  report_diagnostic_healthy_observed(0xf3);
  return;
}

void report_diagnostic_event_failure_f3_32_3d802(void)

{
  report_diagnostic_event_failure(0xf3,0x32);
  return;
}

void reset_recoverable_monitor_febe74bc(void)

{
  reset_recoverable_monitor((F33RecoverableMonitorState *)((undefined *)camry_host_ptr(0xfebe74bcu)));
  return;
}

void reset_74bc_recoverable_monitor_and_flag_3d826(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  reset_recoverable_monitor((F33RecoverableMonitorState *)((undefined *)camry_host_ptr(0xfebe74bcu)));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbcc8u + (uint32_t)((int)puVar1) * 1u)))) = 0;
  return;
}

void update_paired_local_status_monitor(void)

{
  uchar status;
  uchar uVar1;
  uint32_t puVar2;
  puVar2 = 0xfebeb800u;
  if (DAT_0002bb54 == 'Z') {
    reset_recoverable_monitor((F33RecoverableMonitorState *)((undefined *)camry_host_ptr(0xfebe74bcu)));
  }
  else if ((DAT_febe6764 & 3) == 0) {
    step_recoverable_monitor
              ((F33RecoverableMonitorState *)((undefined *)camry_host_ptr(0xfebe74bcu)),
               (F33RecoverableMonitorLimits *)((undefined *)camry_host_ptr(0x2b60cu)),
               (F33RecoverableMonitorCallbacks *)&PTR_classify_paired_local_status_00028170);
  }
  else {
    retain_disabled_recoverable_monitor
              ((F33RecoverableMonitorState *)((undefined *)camry_host_ptr(0xfebe74bcu)),
               (F33RecoverableMonitorLimits *)((undefined *)camry_host_ptr(0x2b60cu)));
  }
  status = (uchar)(*((uint *)camry_host_ptr((uint32_t)((0xffffbcbcu + (uint32_t)((int)puVar2))))));
  uVar1 = status;
  if (((*((uint *)camry_host_ptr((uint32_t)((0xffffbcbcu + (uint32_t)((int)puVar2)))))) & 0xff) != 0) {
    uVar1 = 'Z';
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbcc8u + (uint32_t)((int)puVar2) * 1u)))) = uVar1;
  set_local_status_monitor_status(4,status);
  return;
}

uint classify_paired_local_status(void)

{
  if ((DAT_febe827e == 'Z') && (DAT_febe827d == 'Z')) {
    return 0x22;
  }
  return 0x11;
}

uint classify_paired_local_status_recovery(void)

{
  if ((DAT_febe827e == 'Z') && (DAT_febe827d == 'Z')) {
    return 0x22;
  }
  return 0x11;
}

void report_diagnostic_event_failure_f4_32_3d8d2(void)

{
  report_diagnostic_event_failure(0xf4,0x32);
  return;
}

void report_diagnostic_event_pass_f4_3d8e6(void)

{
  report_diagnostic_event_pass(0xf4);
  return;
}

void reset_recoverable_monitor_febe74cc(void)

{
  reset_recoverable_monitor((F33RecoverableMonitorState *)((undefined *)camry_host_ptr(0xfebe74ccu)));
  return;
}

void reset_recoverable_monitor_febe74cc_3d906(void)

{
  reset_recoverable_monitor((F33RecoverableMonitorState *)((undefined *)camry_host_ptr(0xfebe74ccu)));
  return;
}

void update_individual_local_status_a(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  if (DAT_0002bb58 == 'Z') {
    reset_recoverable_monitor((F33RecoverableMonitorState *)((undefined *)camry_host_ptr(0xfebe74ccu)));
  }
  else if ((DAT_febe6764 & 1) == 0) {
    step_recoverable_monitor
              ((F33RecoverableMonitorState *)((undefined *)camry_host_ptr(0xfebe74ccu)),
               (F33RecoverableMonitorLimits *)((undefined *)camry_host_ptr(0x2b612u)),
               (F33RecoverableMonitorCallbacks *)
               &PTR_classify_individual_local_status_a_000281ac);
  }
  else {
    retain_disabled_recoverable_monitor
              ((F33RecoverableMonitorState *)((undefined *)camry_host_ptr(0xfebe74ccu)),
               (F33RecoverableMonitorLimits *)((undefined *)camry_host_ptr(0x2b612u)));
  }
  set_local_status_monitor_status(2,(uchar)(*((undefined4 *)camry_host_ptr((uint32_t)((0xffffbcccu + (uint32_t)((int)puVar1)))))));
  return;
}

uint classify_individual_local_status_a(void)

{
  if (DAT_febe74c8 == 'Z') {
    return 0x44;
  }
  if (DAT_febe827e == 'Z') {
    return 0x22;
  }
  return 0x11;
}

void report_diagnostic_event_failure_f1_32_3d984(void)

{
  report_diagnostic_event_failure(0xf1,0x32);
  return;
}

void report_diagnostic_event_pass_f1_3d998(void)

{
  report_diagnostic_event_pass(0xf1);
  return;
}

void reset_recoverable_monitor_febe74d8(void)

{
  reset_recoverable_monitor((F33RecoverableMonitorState *)((undefined *)camry_host_ptr(0xfebe74d8u)));
  return;
}

void reset_recoverable_monitor_febe74d8_3d9b8(void)

{
  reset_recoverable_monitor((F33RecoverableMonitorState *)((undefined *)camry_host_ptr(0xfebe74d8u)));
  return;
}

void update_individual_local_status_b(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  if (DAT_0002bb5c == 'Z') {
    reset_recoverable_monitor((F33RecoverableMonitorState *)((undefined *)camry_host_ptr(0xfebe74d8u)));
  }
  else if ((DAT_febe6764 >> 1 & 1) == 0) {
    step_recoverable_monitor
              ((F33RecoverableMonitorState *)((undefined *)camry_host_ptr(0xfebe74d8u)),
               (F33RecoverableMonitorLimits *)((undefined *)camry_host_ptr(0x2b618u)),
               (F33RecoverableMonitorCallbacks *)
               &PTR_classify_individual_local_status_b_000281e8);
  }
  else {
    retain_disabled_recoverable_monitor
              ((F33RecoverableMonitorState *)((undefined *)camry_host_ptr(0xfebe74d8u)),
               (F33RecoverableMonitorLimits *)((undefined *)camry_host_ptr(0x2b618u)));
  }
  set_local_status_monitor_status(3,(uchar)(*((undefined4 *)camry_host_ptr((uint32_t)((0xffffbcd8u + (uint32_t)((int)puVar1)))))));
  return;
}

uint classify_individual_local_status_b(void)

{
  if (DAT_febe74c8 == 'Z') {
    return 0x44;
  }
  if (DAT_febe827d == 'Z') {
    return 0x22;
  }
  return 0x11;
}

void report_diagnostic_event_failure_f2_32_3da36(void)

{
  report_diagnostic_event_failure(0xf2,0x32);
  return;
}

void report_diagnostic_event_pass_f2_3da4a(void)

{
  report_diagnostic_event_pass(0xf2);
  return;
}

void reset_74e4_and_74f4_windowed_monitors_3da5a(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  reset_windowed_monitor((F33WindowedMonitorState *)((undefined *)camry_host_ptr(0xfebe74e4u)));
  reset_windowed_monitor(((F33WindowedMonitorState *)camry_host_ptr((uint32_t)((0xffffbcf4u + (uint32_t)((int)puVar1))))));
  return;
}

void reset_74e4_and_74f4_windowed_monitors_3da72(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  reset_windowed_monitor((F33WindowedMonitorState *)((undefined *)camry_host_ptr(0xfebe74e4u)));
  reset_windowed_monitor(((F33WindowedMonitorState *)camry_host_ptr((uint32_t)((0xffffbcf4u + (uint32_t)((int)puVar1))))));
  return;
}

void step_paired_source_difference_monitors_a(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  if (DAT_0002bb60 == 'Z') {
    reset_windowed_monitor((F33WindowedMonitorState *)((undefined *)camry_host_ptr(0xfebe74e4u)));
    reset_windowed_monitor(((F33WindowedMonitorState *)camry_host_ptr((uint32_t)((0xffffbcf4u + (uint32_t)((int)puVar1))))));
  }
  else {
    step_windowed_monitor
              ((F33WindowedMonitorState *)((undefined *)camry_host_ptr(0xfebe74e4u)),(F33WindowedMonitorLimits *)((undefined *)camry_host_ptr(0x2b622u)),
               (F33TwoSidedMonitorCallbacks *)
               &PTR_classify_paired_source_delayed_difference_aa_00028224);
    step_windowed_monitor
              (((F33WindowedMonitorState *)camry_host_ptr((uint32_t)((0xffffbcf4u + (uint32_t)((int)puVar1))))),
               (F33WindowedMonitorLimits *)((undefined *)camry_host_ptr(0x2b62au)),
               (F33TwoSidedMonitorCallbacks *)
               &PTR_classify_paired_source_delayed_difference_ab_00028258);
  }
  publish_paired_source_monitor_status(6,(*((uint *)camry_host_ptr((uint32_t)((0xffffbce4u + (uint32_t)((int)puVar1)))))));
  publish_paired_source_monitor_status(7,(*((uint *)camry_host_ptr((uint32_t)((0xffffbcf4u + (uint32_t)((int)puVar1)))))));
  return;
}

uint classify_paired_source_delayed_difference_aa(void)

{
  if (((DAT_febe7bc2 != 'Z') && (DAT_febe7bc3 != 'Z')) ||
     (((volatile uint8_t *)camry_host_ptr(0xfebe755cu))[0] != '\0')) {
    return 0x44;
  }
  if ((DAT_febe7554 & 1) != 0) {
    return 0x22;
  }
  if (((DAT_febe7554 == 0) && (((int16_t)DAT_febe7b44) == -1)) && ((DAT_febe71ec >> 7 & 1) == 0)) {
    return 0x11;
  }
  return 0x33;
}

void report_diagnostic_healthy_observed_29_3db3e(void)

{
  report_diagnostic_healthy_observed(0x29);
  return;
}

void report_event_29_or_22_from_71ec_bit7_3db4e(void)

{
  uint event;
  
  event = 0x29;
  if (((byte)DAT_febe71ec & 0x80) != 0) {
    event = 0x22;
  }
  report_diagnostic_event_failure(event,10);
  return;
}

uint classify_paired_source_delayed_difference_ab(void)

{
  if (((DAT_febe7bc2 != 'Z') && (DAT_febe7bc3 != 'Z')) ||
     (((volatile uint8_t *)camry_host_ptr(0xfebe755cu))[0] != '\0')) {
    return 0x44;
  }
  if ((DAT_febe7554 >> 1 & 1) != 0) {
    return 0x22;
  }
  if (((DAT_febe7554 == 0) && (((int16_t)DAT_febe7b44) == -1)) && ((DAT_febe71ec >> 7 & 1) == 0)) {
    return 0x11;
  }
  return 0x33;
}

void report_diagnostic_healthy_observed_2a_3dbbc(void)

{
  report_diagnostic_healthy_observed(0x2a);
  return;
}

void report_event_2a_or_23_from_71ec_bit7_3dbcc(void)

{
  uint event;
  
  event = 0x2a;
  if (((byte)DAT_febe71ec & 0x80) != 0) {
    event = 0x23;
  }
  report_diagnostic_event_failure(event,10);
  return;
}

void reset_7504_and_7514_windowed_monitors_3dbe6(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  reset_windowed_monitor((F33WindowedMonitorState *)((undefined *)camry_host_ptr(0xfebe7504u)));
  reset_windowed_monitor(((F33WindowedMonitorState *)camry_host_ptr((uint32_t)((0xffffbd14u + (uint32_t)((int)puVar1))))));
  return;
}

void reset_7504_and_7514_windowed_monitors_3dbfe(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  reset_windowed_monitor((F33WindowedMonitorState *)((undefined *)camry_host_ptr(0xfebe7504u)));
  reset_windowed_monitor(((F33WindowedMonitorState *)camry_host_ptr((uint32_t)((0xffffbd14u + (uint32_t)((int)puVar1))))));
  return;
}

void step_paired_source_difference_monitors_b(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  if (DAT_0002bb64 == 'Z') {
    reset_windowed_monitor((F33WindowedMonitorState *)((undefined *)camry_host_ptr(0xfebe7504u)));
    reset_windowed_monitor(((F33WindowedMonitorState *)camry_host_ptr((uint32_t)((0xffffbd14u + (uint32_t)((int)puVar1))))));
  }
  else {
    step_windowed_monitor
              ((F33WindowedMonitorState *)((undefined *)camry_host_ptr(0xfebe7504u)),(F33WindowedMonitorLimits *)((undefined *)camry_host_ptr(0x2b632u)),
               (F33TwoSidedMonitorCallbacks *)
               &PTR_classify_paired_source_delayed_difference_ba_0002828c);
    step_windowed_monitor
              (((F33WindowedMonitorState *)camry_host_ptr((uint32_t)((0xffffbd14u + (uint32_t)((int)puVar1))))),
               (F33WindowedMonitorLimits *)((undefined *)camry_host_ptr(0x2b63au)),
               (F33TwoSidedMonitorCallbacks *)
               &PTR_classify_paired_source_delayed_difference_bb_000282c0);
  }
  publish_paired_source_monitor_status(8,(*((uint *)camry_host_ptr((uint32_t)((0xffffbd04u + (uint32_t)((int)puVar1)))))));
  publish_paired_source_monitor_status(9,(*((uint *)camry_host_ptr((uint32_t)((0xffffbd14u + (uint32_t)((int)puVar1)))))));
  return;
}

uint classify_paired_source_delayed_difference_ba(void)

{
  if (((DAT_febe7bc2 != 'Z') && (DAT_febe7bc3 != 'Z')) ||
     ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe755cu + (uint32_t)(1) * 1u)))) != '\0')) {
    return 0x44;
  }
  if ((DAT_febe7554 >> 4 & 1) != 0) {
    return 0x22;
  }
  if (((DAT_febe7554 == 0) && (((int16_t)DAT_febe7b46) == -1)) && ((DAT_febe71ec >> 8 & 1) == 0)) {
    return 0x11;
  }
  return 0x33;
}

void report_diagnostic_healthy_observed_2b_3dcca(void)

{
  report_diagnostic_healthy_observed(0x2b);
  return;
}

void report_event_2b_or_33_from_71ec_bit8_3dcda(void)

{
  uint event;
  
  event = 0x2b;
  if (((*((volatile uint8_t *)camry_host_ptr(0xfebe71edu))) & 1) != 0) {
    event = 0x33;
  }
  report_diagnostic_event_failure(event,10);
  return;
}

uint classify_paired_source_delayed_difference_bb(void)

{
  if (((DAT_febe7bc2 != 'Z') && (DAT_febe7bc3 != 'Z')) ||
     ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe755cu + (uint32_t)(1) * 1u)))) != '\0')) {
    return 0x44;
  }
  if ((DAT_febe7554 >> 5 & 1) != 0) {
    return 0x22;
  }
  if (((DAT_febe7554 == 0) && (((int16_t)DAT_febe7b46) == -1)) && ((DAT_febe71ec >> 8 & 1) == 0)) {
    return 0x11;
  }
  return 0x33;
}

void report_diagnostic_healthy_observed_2c_3dd48(void)

{
  report_diagnostic_healthy_observed(0x2c);
  return;
}

void report_event_2c_or_34_from_71ec_bit8_3dd58(void)

{
  uint event;
  
  event = 0x2c;
  if (((*((volatile uint8_t *)camry_host_ptr(0xfebe71edu))) & 1) != 0) {
    event = 0x34;
  }
  report_diagnostic_event_failure(event,10);
  return;
}

void reset_latched_monitor_febe7524(void)

{
  reset_latched_monitor((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe7524u)));
  return;
}

void reset_7524_monitor_and_snapshot_even_source_bytes_3dd82(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  reset_latched_monitor((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe7524u)));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbd34u + (uint32_t)((int)puVar1) * 1u)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x54b4)))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbd35u + (uint32_t)((int)puVar1) * 1u)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x54b2)))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbd36u + (uint32_t)((int)puVar1) * 1u)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x54b0)))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbd37u + (uint32_t)((int)puVar1) * 1u)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x54ae)))));
  return;
}

void step_paired_source_counter_monitor_a(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  if (DAT_0002bb68 == 'Z') {
    puVar1 = 0xfebeb800u;
    reset_latched_monitor((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe7524u)));
  }
  else {
    if (((byte)DAT_febe71ec & 0x80) == 0) {
      step_latched_monitor
                ((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe7524u)),(F33MonitorLimits *)((undefined *)camry_host_ptr(0x2b642u)),
                 (F33TwoSidedMonitorCallbacks *)
                 &PTR_classify_paired_source_counter_changes_a_000282f4);
      goto LAB_0003ddf2;
    }
    puVar1 = 0xfebeb800u;
    retain_disabled_latched_monitor
              ((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe7524u)),(F33MonitorLimits *)((undefined *)camry_host_ptr(0x2b642u)));
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbd30u + (uint32_t)((int)puVar1) * 1u)))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbd31u + (uint32_t)((int)puVar1) * 1u)))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbd32u + (uint32_t)((int)puVar1) * 1u)))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbd33u + (uint32_t)((int)puVar1) * 1u)))) = 0;
LAB_0003ddf2:
  publish_paired_source_monitor_status(0,(*((uint *)camry_host_ptr((uint32_t)((0xffffbd24u + (uint32_t)((int)puVar1)))))));
  return;
}

uint classify_paired_source_counter_changes_a(void)

{
  uint uVar1;
  
  DAT_febe7530 = '\0';
  DAT_febe7531 = '\0';
  DAT_febe7532 = '\0';
  DAT_febe7533 = '\0';
  if ((DAT_febe7bc2 == 'Z') || (DAT_febe7bc3 == 'Z')) {
    DAT_febe7530 = '\0';
    if (DAT_febe634c != DAT_febe7534) {
      DAT_febe7530 = 'Z';
    }
    DAT_febe7531 = '\0';
    if (DAT_febe634e != DAT_febe7535) {
      DAT_febe7531 = 'Z';
    }
    DAT_febe7532 = '\0';
    if (DAT_febe6350 != DAT_febe7536) {
      DAT_febe7532 = 'Z';
    }
    DAT_febe7533 = '\0';
    if (DAT_febe6352 != DAT_febe7537) {
      DAT_febe7533 = 'Z';
    }
    if ((((DAT_febe7530 == 'Z') || (DAT_febe7531 == 'Z')) || (DAT_febe7532 == 'Z')) ||
       (DAT_febe7533 == 'Z')) {
      uVar1 = 0x22;
    }
    else {
      uVar1 = 0x11;
    }
  }
  else {
    uVar1 = 0x44;
  }
  DAT_febe7534 = DAT_febe634c;
  DAT_febe7535 = DAT_febe634e;
  DAT_febe7536 = DAT_febe6350;
  DAT_febe7537 = DAT_febe6352;
  return uVar1;
}

void run_init_chain_3de92(void)

{
  report_diagnostic_healthy_observed(0x46);
  report_diagnostic_healthy_observed(0x47);
  report_diagnostic_healthy_observed(0x48);
  report_diagnostic_healthy_observed(0x49);
  return;
}

void report_events_46_to_49_from_7530_flags_3deba(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  if (DAT_febe7530 == 'Z') {
    puVar1 = 0xfebeb800u;
    report_diagnostic_event_failure(0x46,10);
  }
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbd31u + (uint32_t)((int)puVar1) * 1u)))) == 'Z') {
    report_diagnostic_event_failure(0x47,10);
  }
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbd32u + (uint32_t)((int)puVar1) * 1u)))) == 'Z') {
    report_diagnostic_event_failure(0x48,10);
  }
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbd33u + (uint32_t)((int)puVar1) * 1u)))) == 'Z') {
    report_diagnostic_event_failure(0x49,10);
  }
  return;
}

void reset_latched_monitor_febe7538(void)

{
  reset_latched_monitor((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe7538u)));
  return;
}

void reset_7538_monitor_and_snapshot_odd_source_bytes_3df22(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  reset_latched_monitor((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe7538u)));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbd48u + (uint32_t)((int)puVar1) * 1u)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x54b3)))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbd49u + (uint32_t)((int)puVar1) * 1u)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x54b1)))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbd4au + (uint32_t)((int)puVar1) * 1u)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x54af)))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbd4bu + (uint32_t)((int)puVar1) * 1u)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x54ad)))));
  return;
}

void step_paired_source_counter_monitor_b(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  if (DAT_0002bb6c == 'Z') {
    puVar1 = 0xfebeb800u;
    reset_latched_monitor((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe7538u)));
  }
  else {
    if (((*((volatile uint8_t *)camry_host_ptr(0xfebe71edu))) & 1) == 0) {
      step_latched_monitor
                ((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe7538u)),(F33MonitorLimits *)((undefined *)camry_host_ptr(0x2b646u)),
                 (F33TwoSidedMonitorCallbacks *)
                 &PTR_classify_paired_source_counter_changes_b_00028328);
      goto LAB_0003df92;
    }
    puVar1 = 0xfebeb800u;
    retain_disabled_latched_monitor
              ((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe7538u)),(F33MonitorLimits *)((undefined *)camry_host_ptr(0x2b646u)));
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbd44u + (uint32_t)((int)puVar1) * 1u)))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbd45u + (uint32_t)((int)puVar1) * 1u)))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbd46u + (uint32_t)((int)puVar1) * 1u)))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbd47u + (uint32_t)((int)puVar1) * 1u)))) = 0;
LAB_0003df92:
  publish_paired_source_monitor_status(1,(*((uint *)camry_host_ptr((uint32_t)((0xffffbd38u + (uint32_t)((int)puVar1)))))));
  return;
}

uint classify_paired_source_counter_changes_b(void)

{
  uint uVar1;
  
  DAT_febe7544 = '\0';
  DAT_febe7545 = '\0';
  DAT_febe7546 = '\0';
  DAT_febe7547 = '\0';
  if ((DAT_febe7bc2 == 'Z') || (DAT_febe7bc3 == 'Z')) {
    DAT_febe7544 = '\0';
    if (DAT_febe634d != DAT_febe7548) {
      DAT_febe7544 = 'Z';
    }
    DAT_febe7545 = '\0';
    if (DAT_febe634f != DAT_febe7549) {
      DAT_febe7545 = 'Z';
    }
    DAT_febe7546 = '\0';
    if (DAT_febe6351 != DAT_febe754a) {
      DAT_febe7546 = 'Z';
    }
    DAT_febe7547 = '\0';
    if (DAT_febe6353 != DAT_febe754b) {
      DAT_febe7547 = 'Z';
    }
    if ((((DAT_febe7544 == 'Z') || (DAT_febe7545 == 'Z')) || (DAT_febe7546 == 'Z')) ||
       (DAT_febe7547 == 'Z')) {
      uVar1 = 0x22;
    }
    else {
      uVar1 = 0x11;
    }
  }
  else {
    uVar1 = 0x44;
  }
  DAT_febe7548 = DAT_febe634d;
  DAT_febe7549 = DAT_febe634f;
  DAT_febe754a = DAT_febe6351;
  DAT_febe754b = DAT_febe6353;
  return uVar1;
}
