#include "common.h"

void request_shared_monitor_escalation_sample_bounds_b(void)

{
  byte bVar1;
  
  bVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe7cacu + (uint32_t)(2) * 1u)))) | ((volatile uint8_t *)camry_host_ptr(0xfebe7cacu))[0] |
          (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe7cacu + (uint32_t)(8) * 1u))));
  if ((((bVar1 & 0x22) == 0x22) || ((bVar1 & 0x44) == 0x44)) || (DAT_febe71ec != 0)) {
    DAT_febe7ca0 = 0x5a;
  }
  return;
}

void run_init_chain_470d0(void)

{
  report_diagnostic_event_pass(0x161);
  report_diagnostic_event_pass(0x162);
  report_diagnostic_event_pass(0x163);
  report_diagnostic_event_pass(0x164);
  report_diagnostic_event_pass(0x165);
  return;
}

void report_diagnostic_event_failure_166_10_47100(void)

{
  report_diagnostic_event_failure(0x166,10);
  return;
}

void return_only_stub_47112(void)

{
  return;
}

void return_only_stub_47114(void)

{
  return;
}

void publish_shared_snapshot_monitor_actions(void)

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
  retain_and_clear_fault_record(0);
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
    encode_fault_action_kind('\0','\x05');
  }
  bVar4 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x3b4c))))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x3b52))))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x3b54)))));
  iVar10 = 0;
  if ((((bVar4 & 0x22) == 0x22) || ((bVar4 & 0x44) == 0x44)) &&
     ((bVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x3b4b))))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x3b51))))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x3b53))))), (bVar1 & 0x22) == 0x22 ||
      ((bVar1 & 0x44) == 0x44)))) {
    iVar10 = 0x5a;
  }
  if (((bVar4 & 0x44) == 0x44) || (iVar10 == 0x5a)) {
    encode_fault_action_kind('\0','\x10');
  }
  if (((((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x3b4b))))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x3b51))))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x3b53)))))) & 0x44) == 0x44) || (iVar10 == 0x5a))
  {
    encode_fault_action_kind('\0','\x11');
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
    encode_fault_action_kind('\0','/');
  }
  if ((uVar2 >> 6 & 1) != 0) {
    encode_fault_action_kind('\0','0');
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
  set_decoded_torque_override_byte_46a2c(uVar8);
  select_current_fault_record(0);
  uVar6 = '\0';
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x3b4b))))) != '\0' ||
      ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x3b4c))))) != '\0' ||
      ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x3b51))))) != '\0' ||
      ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x3b52))))) != '\0' || ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x3b53))))) != '\0' || (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x3b54))))) != '\0'))))) {
    uVar6 = '\x11';
  }
  set_diagnostic_cache_blocker('\b',uVar6);
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
  set_monitor_pending_projection('\x06',uVar6);
  return;
}

void publish_shared_snapshot_monitor_status(uint index,uint packed)

{
  uint uVar1;
  
  uVar1 = index & 0xff;
  if (uVar1 < 0xb) {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe7cacu + (uint32_t)(uVar1) * 1u)))) = (uchar)packed;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe7cb9u + (uint32_t)(uVar1) * 1u)))) = (uchar)(packed >> 0x10);
  }
  return;
}

void reset_shared_snapshot_monitor_6_473ec(void)

{
  clear_word_state_and_five_halfword_counters_6b98a(((undefined4 *)camry_host_ptr((uint32_t)((0xfebe7cc8u)))));
  return;
}

void reset_shared_snapshot_monitor_6_473fc(void)

{
  clear_word_state_and_five_halfword_counters_6b98a(((undefined4 *)camry_host_ptr((uint32_t)((0xfebe7cc8u)))));
  return;
}

void update_and_publish_snapshot_monitor_6_4740c(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  if (DAT_febe8a24 == 'Z') {
    if (DAT_0002bc90 == 'Z') {
      clear_word_state_and_five_halfword_counters_6b98a(((undefined4 *)camry_host_ptr((uint32_t)((0xfebe7cc8u)))));
    }
    else if ((DAT_febeeb85 == 'Z') && ((DAT_febe71ec >> 5 & 1) == 0)) {
      step_escalating_monitor
                (((F33EscalatingMonitorState *)camry_host_ptr((uint32_t)((0xfebe7cc8u)))), (ushort *)((undefined *)camry_host_ptr(0x2ba66u)), 
                 (uint *)&PTR_classify_snapshot_bit3_a_00028e3c);
    }
    else {
      retain_disabled_escalating_monitor(((F33EscalatingMonitorState *)camry_host_ptr((uint32_t)((0xfebe7cc8u)))), (ushort *)((undefined *)camry_host_ptr(0x2ba66u)))
      ;
    }
    publish_shared_snapshot_monitor_status(6,(*((uint *)camry_host_ptr((uint32_t)(puVar1 + -0x3b38)))));
  }
  return;
}

uint classify_snapshot_bit3_a(void)

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

uint classify_snapshot_bit3_recovery_a(void)

{
  return 0x44;
}

void report_diagnostic_event_failure_16b_10_474a2(void)

{
  report_diagnostic_event_failure(0x16b,10);
  return;
}

void reset_shared_snapshot_monitor_7_474b4(void)

{
  clear_word_state_and_five_halfword_counters_6b98a(((undefined4 *)camry_host_ptr((uint32_t)((0xfebe7cdcu)))));
  return;
}

void reset_shared_snapshot_monitor_7_474c4(void)

{
  clear_word_state_and_five_halfword_counters_6b98a(((undefined4 *)camry_host_ptr((uint32_t)((0xfebe7cdcu)))));
  return;
}

void update_and_publish_snapshot_monitor_7_474d4(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  if (DAT_febe8a24 == 'Z') {
    if (DAT_0002bc94 == 'Z') {
      clear_word_state_and_five_halfword_counters_6b98a(((undefined4 *)camry_host_ptr((uint32_t)((0xfebe7cdcu)))));
    }
    else if ((DAT_febeeb85 == 'Z') && ((DAT_febe71ec >> 6 & 1) == 0)) {
      step_escalating_monitor
                (((F33EscalatingMonitorState *)camry_host_ptr((uint32_t)((0xfebe7cdcu)))), (ushort *)((undefined *)camry_host_ptr(0x2ba76u)), 
                 (uint *)&PTR_classify_snapshot_bit3_b_00028e80);
    }
    else {
      retain_disabled_escalating_monitor(((F33EscalatingMonitorState *)camry_host_ptr((uint32_t)((0xfebe7cdcu)))), (ushort *)((undefined *)camry_host_ptr(0x2ba76u)))
      ;
    }
    publish_shared_snapshot_monitor_status(7,(*((uint *)camry_host_ptr((uint32_t)(puVar1 + -0x3b24)))));
  }
  return;
}

uint classify_snapshot_bit3_b(void)

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

uint classify_snapshot_bit3_recovery_b(void)

{
  return 0x44;
}

void report_diagnostic_event_failure_16c_10_4756a(void)

{
  report_diagnostic_event_failure(0x16c,10);
  return;
}

void reset_shared_snapshot_monitor_4_4757c(void)

{
  clear_word_state_and_five_halfword_counters_6b98a(((undefined4 *)camry_host_ptr((uint32_t)((0xfebe7cf0u)))));
  return;
}

void reset_shared_snapshot_monitor_4_4758c(void)

{
  clear_word_state_and_five_halfword_counters_6b98a(((undefined4 *)camry_host_ptr((uint32_t)((0xfebe7cf0u)))));
  return;
}

void update_and_publish_snapshot_monitor_4_4759c(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  if (DAT_febe8a24 == 'Z') {
    if (DAT_0002bc98 == 'Z') {
      puVar1 = 0xfebeb800u;
      clear_word_state_and_five_halfword_counters_6b98a(((undefined4 *)camry_host_ptr((uint32_t)((0xfebe7cf0u)))));
    }
    else if ((DAT_febeeb85 == 'Z') && ((DAT_febe71ec >> 5 & 1) == 0)) {
      puVar1 = 0xfebeb800u;
      step_escalating_monitor
                (((F33EscalatingMonitorState *)camry_host_ptr((uint32_t)((0xfebe7cf0u)))), (ushort *)((undefined *)camry_host_ptr(0x2ba86u)), 
                 (uint *)&PTR_classify_snapshot_low_gate_a_00028ec4);
    }
    else {
      shared_snapshot_monitor_4.packed_status = 0;
      shared_snapshot_monitor_4.passing_count = 0;
      shared_snapshot_monitor_4.failing_count = 0;
      shared_snapshot_monitor_4.recovery_count = 0;
      shared_snapshot_monitor_4.elapsed_count = 0;
    }
    publish_shared_snapshot_monitor_status(4,(*((uint *)camry_host_ptr((uint32_t)(puVar1 + -0x3b10)))));
  }
  return;
}

uint classify_snapshot_low_gate_a(void)

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

void reset_shared_snapshot_monitor_5_47682(void)

{
  clear_word_state_and_five_halfword_counters_6b98a(((undefined4 *)camry_host_ptr((uint32_t)((0xfebe7d04u)))));
  return;
}

void reset_shared_snapshot_monitor_5_47692(void)

{
  clear_word_state_and_five_halfword_counters_6b98a(((undefined4 *)camry_host_ptr((uint32_t)((0xfebe7d04u)))));
  return;
}

void update_and_publish_snapshot_monitor_5_476a2(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  if (DAT_febe8a24 == 'Z') {
    if (DAT_0002bc9c == 'Z') {
      puVar1 = 0xfebeb800u;
      clear_word_state_and_five_halfword_counters_6b98a(((undefined4 *)camry_host_ptr((uint32_t)((0xfebe7d04u)))));
    }
    else if ((DAT_febeeb85 == 'Z') && ((DAT_febe71ec >> 6 & 1) == 0)) {
      puVar1 = 0xfebeb800u;
      step_escalating_monitor
                (((F33EscalatingMonitorState *)camry_host_ptr((uint32_t)((0xfebe7d04u)))), (ushort *)((undefined *)camry_host_ptr(0x2ba96u)), 
                 (uint *)&PTR_classify_snapshot_low_gate_b_00028f08);
    }
    else {
      shared_snapshot_monitor_5.packed_status = 0;
      shared_snapshot_monitor_5.passing_count = 0;
      shared_snapshot_monitor_5.failing_count = 0;
      shared_snapshot_monitor_5.recovery_count = 0;
      shared_snapshot_monitor_5.elapsed_count = 0;
    }
    publish_shared_snapshot_monitor_status(5,(*((uint *)camry_host_ptr((uint32_t)(puVar1 + -0x3afc)))));
  }
  return;
}

uint classify_snapshot_low_gate_b(void)

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

void reset_shared_snapshot_monitor_8_47788(void)

{
  clear_word_state_and_five_halfword_counters_6b98a(((undefined4 *)camry_host_ptr((uint32_t)((0xfebe7d18u)))));
  return;
}

void reset_shared_snapshot_monitor_8_47798(void)

{
  clear_word_state_and_five_halfword_counters_6b98a(((undefined4 *)camry_host_ptr((uint32_t)((0xfebe7d18u)))));
  return;
}

void update_and_publish_snapshot_monitor_8_477a8(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  if (DAT_febe8a24 != 'Z') {
    return;
  }
  if (DAT_0002bca0 == 'Z') {
    clear_word_state_and_five_halfword_counters_6b98a(((undefined4 *)camry_host_ptr((uint32_t)((0xfebe7d18u)))));
  }
  else {
    if ((DAT_febeeb85 == 'Z') && ((DAT_febe71ec >> 5 & 1) == 0)) {
      puVar1 = 0xfebeb800u;
      step_escalating_monitor
                (((F33EscalatingMonitorState *)camry_host_ptr((uint32_t)((0xfebe7d18u)))), (ushort *)((undefined *)camry_host_ptr(0x2baa6u)), 
                 (uint *)&PTR_classify_snapshot_bit2_a_00028f4c);
      if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x3ad8))))) == 'Z') {
        force_monitor_escalation
                  (((F33EscalatingMonitorState *)camry_host_ptr((uint32_t)((0xfebe7d18u)))), (ushort *)((undefined *)camry_host_ptr(0x2baa6u)), 
                   (uint *)&PTR_classify_snapshot_bit2_a_00028f4c);
      }
      goto LAB_0004781c;
    }
    retain_disabled_escalating_monitor(((F33EscalatingMonitorState *)camry_host_ptr((uint32_t)((0xfebe7d18u)))), (ushort *)((undefined *)camry_host_ptr(0x2baa6u)));
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x3ad8))))) = 0;
LAB_0004781c:
  publish_shared_snapshot_monitor_status(8,(*((uint *)camry_host_ptr((uint32_t)(puVar1 + -0x3ae8)))));
  return;
}

uint classify_snapshot_bit2_a(void)

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

uint classify_snapshot_bit2_recovery_a(void)

{
  uint uVar1;
  
  uVar1 = 0x11;
  if (DAT_febe6320 != DAT_febe7d29) {
    uVar1 = 0x22;
  }
  DAT_febe7d29 = DAT_febe6320;
  return uVar1;
}

void report_diagnostic_healthy_observed_16e_4787a(void)

{
  report_diagnostic_healthy_observed(0x16e);
  return;
}

void report_event_16d_and_latch_snapshot_8_escalation_4788a(void)

{
  byte bVar1;
  short sVar2;
  uint32_t puVar3;
  sVar2 = DAT_febe71ec;
  puVar3 = 0xfebeb800u;
  bVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe7cacu + (uint32_t)(9) * 1u)))) |
          (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe7cacu + (uint32_t)(3) * 1u)))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe7cacu + (uint32_t)(1) * 1u))));
  report_diagnostic_event_failure(0x16d,10);
  if ((((bVar1 & 0x22) == 0x22) || ((bVar1 & 0x44) == 0x44)) || (sVar2 != 0)) {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x3ad8))))) = 0x5a;
  }
  return;
}

void request_shared_monitor_escalation_bit2_a(void)

{
  byte bVar1;
  
  bVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe7cacu + (uint32_t)(3) * 1u)))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe7cacu + (uint32_t)(1) * 1u)))) |
          (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe7cacu + (uint32_t)(9) * 1u))));
  if ((((bVar1 & 0x22) == 0x22) || ((bVar1 & 0x44) == 0x44)) || (DAT_febe71ec != 0)) {
    DAT_febe7d28 = 0x5a;
  }
  return;
}

void report_diagnostic_event_pass_16d_47902(void)

{
  report_diagnostic_event_pass(0x16d);
  return;
}

void report_diagnostic_event_failure_16e_10_47912(void)

{
  report_diagnostic_event_failure(0x16e,10);
  return;
}

void reset_shared_snapshot_monitor_9_47924(void)

{
  clear_word_state_and_five_halfword_counters_6b98a(((undefined4 *)camry_host_ptr((uint32_t)((0xfebe7d2cu)))));
  return;
}

void reset_shared_snapshot_monitor_9_47934(void)

{
  clear_word_state_and_five_halfword_counters_6b98a(((undefined4 *)camry_host_ptr((uint32_t)((0xfebe7d2cu)))));
  return;
}

void update_and_publish_snapshot_monitor_9_47944(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  if (DAT_febe8a24 != 'Z') {
    return;
  }
  if (DAT_0002bca4 == 'Z') {
    clear_word_state_and_five_halfword_counters_6b98a(((undefined4 *)camry_host_ptr((uint32_t)((0xfebe7d2cu)))));
  }
  else {
    if ((DAT_febeeb85 == 'Z') && ((DAT_febe71ec >> 6 & 1) == 0)) {
      puVar1 = 0xfebeb800u;
      step_escalating_monitor
                (((F33EscalatingMonitorState *)camry_host_ptr((uint32_t)((0xfebe7d2cu)))), (ushort *)((undefined *)camry_host_ptr(0x2bab6u)), 
                 (uint *)&PTR_classify_snapshot_bit2_b_00028f90);
      if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x3ac4))))) == 'Z') {
        force_monitor_escalation
                  (((F33EscalatingMonitorState *)camry_host_ptr((uint32_t)((0xfebe7d2cu)))), (ushort *)((undefined *)camry_host_ptr(0x2bab6u)), 
                   (uint *)&PTR_classify_snapshot_bit2_b_00028f90);
      }
      goto LAB_000479b8;
    }
    retain_disabled_escalating_monitor(((F33EscalatingMonitorState *)camry_host_ptr((uint32_t)((0xfebe7d2cu)))), (ushort *)((undefined *)camry_host_ptr(0x2bab6u)));
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x3ac4))))) = 0;
LAB_000479b8:
  publish_shared_snapshot_monitor_status(9,(*((uint *)camry_host_ptr((uint32_t)(puVar1 + -0x3ad4)))));
  return;
}

uint classify_snapshot_bit2_b(void)

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

uint classify_snapshot_bit2_recovery_b(void)

{
  uint uVar1;
  
  uVar1 = 0x11;
  if (DAT_febe6338 != DAT_febe7d3d) {
    uVar1 = 0x22;
  }
  DAT_febe7d3d = DAT_febe6338;
  return uVar1;
}

void report_diagnostic_healthy_observed_170_47a16(void)

{
  report_diagnostic_healthy_observed(0x170);
  return;
}

void report_event_16f_and_latch_snapshot_9_escalation_47a26(void)

{
  byte bVar1;
  short sVar2;
  uint32_t puVar3;
  sVar2 = DAT_febe71ec;
  puVar3 = 0xfebeb800u;
  bVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe7cacu + (uint32_t)(8) * 1u)))) |
          (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe7cacu + (uint32_t)(2) * 1u)))) | ((volatile uint8_t *)camry_host_ptr(0xfebe7cacu))[0];
  report_diagnostic_event_failure(0x16f,10);
  if ((((bVar1 & 0x22) == 0x22) || ((bVar1 & 0x44) == 0x44)) || (sVar2 != 0)) {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x3ac4))))) = 0x5a;
  }
  return;
}

void request_shared_monitor_escalation_bit2_b(void)

{
  byte bVar1;
  
  bVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe7cacu + (uint32_t)(2) * 1u)))) | ((volatile uint8_t *)camry_host_ptr(0xfebe7cacu))[0] |
          (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe7cacu + (uint32_t)(8) * 1u))));
  if ((((bVar1 & 0x22) == 0x22) || ((bVar1 & 0x44) == 0x44)) || (DAT_febe71ec != 0)) {
    DAT_febe7d3c = 0x5a;
  }
  return;
}

void report_diagnostic_event_pass_16f_47a9e(void)

{
  report_diagnostic_event_pass(0x16f);
  return;
}

void report_diagnostic_event_failure_170_10_47aae(void)

{
  report_diagnostic_event_failure(0x170,10);
  return;
}

void return_only_stub_47ac0(void)

{
  return;
}

void return_only_stub_47ac2(void)

{
  return;
}

void lookup_low_nibble_code_or_zero_47ac4(void)

{
  DAT_febe7d40 = 0;
  if (DAT_febe8026 < 0x10) {
    DAT_febe7d40 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x212b8u + (uint32_t)(DAT_febe8026) * 1u))));
  }
  return;
}

void return_only_stub_47adc(void)

{
  return;
}

void return_only_stub_47ade(void)

{
  return;
}

void clamp_sample_8048_and_compute_enable_gate_47ae0(void)

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
  store_s32_saturated_to_symmetric_s16_6a5fa((int)((int)(int16_t)DAT_febe8048),&uStack_e);
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

void return_only_stub_47b3a(void)

{
  return;
}

void fill_constant_block_47b3c(void)

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

int get_signed_halfword_689a_47b6a(void)

{
  return (int)((int)(int16_t)DAT_febe689a);
}

uint32_t compute_shifted_angle_polynomial_pairs_47b70(void)

{
  uint32_t camry_r10_result;
  uint8_t stack_record_14[20];
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
  uint32_t puVar11;
  int iVar12;
  
  iVar4 = DAT_febe7d94;
  puVar5 = 0xfebeb800u;
  iVar12 = (int)((int)(int16_t)DAT_febe5f36);
  sVar6 = (camry_r10_result = get_signed_halfword_689a_47b6a());
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
    puVar11 = (uint32_t)((uint32_t)(0x10000));
    iVar10 = 0;
  }
  else {
    puVar11 = (uint32_t)(0xddb4u);
    iVar10 = -0x8000;
    if (cVar2 == 'Z') {
      iVar10 = 0x8000;
    }
  }
  compute_q15_sine_cosine_turn_angle_70e32(iVar4 - iVar9 & 0xffff,stack_record_14,(stack_record_14 + 2));
  (*((short *)camry_host_ptr((uint32_t)(puVar5 + -0x3ab2)))) = (*((int16_t *)(stack_record_14 + 0)));
  (*((short *)camry_host_ptr((uint32_t)(puVar5 + -0x3ab0)))) = (*((int16_t *)(stack_record_14 + 2)));
  iVar9 = ((*((int16_t *)(stack_record_14 + 2))) * iVar10) / 0x10000 + (int)(((int)(*((int16_t *)(stack_record_14 + 0))) * (int)puVar11)) / (int)0x10000;
  iVar4 = (int)(((int)(*((int16_t *)(stack_record_14 + 2))) * (int)puVar11)) / (int)0x10000 - ((*((int16_t *)(stack_record_14 + 0))) * iVar10) / 0x10000;
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
  compute_q15_sine_cosine_turn_angle_70e32((*((undefined2 *)camry_host_ptr((uint32_t)(puVar5 + -0x3aae)))),(stack_record_14 + 4),(stack_record_14 + 6));
  (*((short *)camry_host_ptr((uint32_t)(puVar5 + -0x3aac)))) = (*((int16_t *)(stack_record_14 + 4)));
  (*((short *)camry_host_ptr((uint32_t)(puVar5 + -0x3aaa)))) = (*((int16_t *)(stack_record_14 + 6)));
  iVar9 = ((*((int16_t *)(stack_record_14 + 6))) * iVar10) / 0x10000 + (int)(((int)(*((int16_t *)(stack_record_14 + 4))) * (int)puVar11)) / (int)0x10000;
  iVar4 = (int)(((int)(*((int16_t *)(stack_record_14 + 6))) * (int)puVar11)) / (int)0x10000 - ((*((int16_t *)(stack_record_14 + 4))) * iVar10) / 0x10000;
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
  return camry_r10_result;
}

void return_only_stub_47d32(void)

{
  return;
}

void clear_wrapped_value_7d74_47d34(void)

{
  DAT_febe7d74 = 0;
  return;
}

void wrap_signed_value_by_06660000_47d3a(void)

{
  int value;

  value = (int)DAT_febe7d94;
  if (value >= 0x3330000) {
    value = value + -0x6660000;
  }
  else if (value < -0x3330000) {
    value = value + 0x6660000;
  }
  DAT_febe7d74 = (uint)value;
  return;
}

void return_only_stub_47d60(void)

{
  return;
}

ushort select_electrical_angle_sample(uchar channel)

{
  DAT_febe7d90 = DAT_febe824c;
  if (channel == '\x01') {
    DAT_febe7d90 = DAT_febe8250;
  }
  return DAT_febe7d90;
}

void seed_selected_electrical_angle_words_47d78(void)

{
  DAT_febe7d90 = DAT_febe824c;
  if ((DAT_febe71ec & 0x80) == 0x80) {
    DAT_febe7d90 = DAT_febe8250;
  }
  DAT_febe7d94 = (uint)DAT_febe7d90;
  DAT_febe7da0 = (uint)DAT_febe7d90;
  return;
}

void thunk_seed_selected_electrical_angle_words_47d78(void)

{
  seed_selected_electrical_angle_words_47d78();
  return;
}

short correct_electrical_angle_sample(uchar enabled,uchar bank,short phase)

{
  char cVar1;
  short sVar2;
  int iVar3;
  
  if (enabled == 'Z') {
    iVar3 = camry_host_addr(get_monitor_current_rom_record_567be());
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

int accumulate_electrical_angle(int previous,short phase)

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

void update_electrical_angle_feedback(void)

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
  phase = correct_electrical_angle_sample(DAT_febe6a7b,(uchar)uVar3,DAT_febe7d90);
  iVar4 = accumulate_electrical_angle(iVar4,phase);
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

void return_only_stub_47ea2(void)

{
  return;
}

void fill_constant_block_47ea4(void)

{
  DAT_febe5f34 = 0;
  DAT_febe5f36 = 0;
  DAT_febe5f40 = 0;
  DAT_febe5f38 = DAT_febe7d74;
  DAT_febe5f3c = 0;
  return;
}

void update_wrapped_difference_and_fixed_point_filter_47eb8(void)

{
  int iVar1;
  uint uVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  
  iVar4 = DAT_febe5f38;
  if (DAT_febe8a14 == '\x01') {
    iVar3 = (int)((int)(int16_t)DAT_febe5f36);
    if ((short)( (int)(DAT_febe5f3c) / (int)0x10000) != iVar3) {
      iVar3 = (int)((int)(int16_t)DAT_febe5f34);
      DAT_febe5f3c = iVar3 << 0x10;
    }
    DAT_febe5f38 = DAT_febe7d74;
    DAT_febe5f40 = DAT_febe7d74 - iVar4;
    if (((int)(int32_t)DAT_febe5f40) + 0x3330000 < 0 == (-1 < ((int)(int32_t)DAT_febe5f40) && ((int)(int32_t)DAT_febe5f40) + 0x3330000 < 0)) {
      if (((int)(int32_t)DAT_febe5f40) + -0x3330000 < 0 == (((int)(int32_t)DAT_febe5f40) < 0 && -1 < ((int)(int32_t)DAT_febe5f40) + -0x3330000)) {
        DAT_febe5f40 = ((int)(int32_t)DAT_febe5f40) + -0x6660000;
      }
    }
    else {
      DAT_febe5f40 = ((int)(int32_t)DAT_febe5f40) + 0x6660000;
    }
    if (((int)(int32_t)DAT_febe5f40) + -0x10000 < 0 == (((int)(int32_t)DAT_febe5f40) < 0 && -1 < ((int)(int32_t)DAT_febe5f40) + -0x10000)) {
      DAT_febe5f40 = 0x10000;
    }
    if (((int)(int32_t)DAT_febe5f40) + 0x10000 < 0 != (-1 < ((int)(int32_t)DAT_febe5f40) && ((int)(int32_t)DAT_febe5f40) + 0x10000 < 0)) {
      DAT_febe5f40 = -0x10000;
    }
    iVar4 = (int)((((int)(int32_t)DAT_febe5f40) * 10000)) / (int)0x1000;
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
    DAT_febe5f36 = (short)( (int)(DAT_febe5f3c) / (int)0x10000);
    DAT_febe5f44 = (((int)(int16_t)DAT_febe5f36) - iVar3) * 0x9c4;
  }
  return;
}

void return_only_stub_47f96(void)

{
  return;
}

int seed_seven_scaled_samples_and_five_accumulators_47f98(void)

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
  iVar7 = test_redundant_status_a5_or_vote_error13_588b6();
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
  return iVar7;
}
