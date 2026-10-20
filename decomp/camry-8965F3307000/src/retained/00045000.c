#include "common.h"

void update_unfilled_reference_sum_binmaps_45062(void)

{
  short sVar1;
  
  sVar1 = DAT_febe7b32;
  if (((int16_t)DAT_febe7b30) != -1) {
    record_a_reference_sum_gated_bins_44ee2();
  }
  if (sVar1 != -1) {
    record_b_reference_sum_gated_bins_44fa2();
  }
  return;
}

void record_a_absolute_sample_gated_bins_45086(void)

{
  int iVar1;
  uint32_t puVar2;
  int iVar3;
  int iVar4;
  undefined2 uStack_6;
  
  puVar2 = 0xfebeb800u;
  iVar3 = (int)((int)(int16_t)DAT_febe63e8);
  uStack_6 = DAT_febe7b34;
  iVar1 = (int)((int)(int16_t)DAT_febe629e);
  if (iVar1 + 0x7fff < 0 == (-1 < iVar1 && iVar1 + 0x7fff < 0) && iVar1 != -0x7fff) {
    if (iVar1 < 0) {
      iVar1 = (int)-((int)(int16_t)DAT_febe629e);
    }
  }
  else {
    iVar1 = 0x7fff;
  }
  if (iVar3 + 0x7fff < 0 == (-1 < iVar3 && iVar3 + 0x7fff < 0) && iVar3 != -0x7fff) {
    if (iVar3 < 0) {
      iVar3 = (int)-((int)(int16_t)DAT_febe63e8);
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
    set_high_nibble_indexed_halfword_bit_44ece(DAT_febe63b8,&uStack_6);
  }
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar2 + -0x3ccc)))) = uStack_6;
  return;
}

void record_b_absolute_sample_gated_bins_450f0(void)

{
  int iVar1;
  uint32_t puVar2;
  int iVar3;
  int iVar4;
  undefined2 uStack_6;
  
  puVar2 = 0xfebeb800u;
  iVar3 = (int)((int)(int16_t)DAT_febe63ec);
  uStack_6 = DAT_febe7b36;
  iVar1 = (int)((int)(int16_t)DAT_febe629e);
  if (iVar1 + 0x7fff < 0 == (-1 < iVar1 && iVar1 + 0x7fff < 0) && iVar1 != -0x7fff) {
    if (iVar1 < 0) {
      iVar1 = (int)-((int)(int16_t)DAT_febe629e);
    }
  }
  else {
    iVar1 = 0x7fff;
  }
  if (iVar3 + 0x7fff < 0 == (-1 < iVar3 && iVar3 + 0x7fff < 0) && iVar3 != -0x7fff) {
    if (iVar3 < 0) {
      iVar3 = (int)-((int)(int16_t)DAT_febe63ec);
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
    set_high_nibble_indexed_halfword_bit_44ece(DAT_febe63b8,&uStack_6);
  }
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar2 + -0x3cca)))) = uStack_6;
  return;
}

void update_unfilled_absolute_sample_binmaps_4515a(void)

{
  short sVar1;
  
  sVar1 = DAT_febe7b36;
  if (((int16_t)DAT_febe7b34) != -1) {
    record_a_absolute_sample_gated_bins_45086();
  }
  if (sVar1 != -1) {
    record_b_absolute_sample_gated_bins_450f0();
  }
  return;
}

void record_a_bounded_difference_bins_4517e(void)

{
  int iVar1;
  uint32_t puVar2;
  int iVar3;
  short sStack_6;
  
  puVar2 = 0xfebeb800u;
  sStack_6 = DAT_febe7b44;
  if (((int16_t)DAT_febe7b44) != -1) {
    iVar1 = (int)DAT_0002b9a2;
    iVar3 = (int)(short)(DAT_febe6354 - DAT_febe6356);
    if ((iVar3 - iVar1 < 0 != (iVar3 < 0 != iVar1 < 0 && iVar1 < 0 == iVar3 - iVar1 < 0) ||
         iVar3 == iVar1) &&
       (iVar3 + iVar1 < 0 == (iVar3 < 0 != -iVar1 < 0 && -iVar1 < 0 == iVar3 + iVar1 < 0))) {
      iVar3 = (int)((int)(int16_t)DAT_febe629e);
      iVar1 = (int)DAT_0002b9a4;
      if ((iVar3 - iVar1 < 0 != (iVar3 < 0 != iVar1 < 0 && iVar1 < 0 == iVar3 - iVar1 < 0) ||
           iVar3 == iVar1) &&
         (iVar3 + iVar1 < 0 == (iVar3 < 0 != -iVar1 < 0 && -iVar1 < 0 == iVar3 + iVar1 < 0))) {
        puVar2 = 0xfebeb800u;
        set_high_nibble_indexed_halfword_bit_44ece(DAT_febe6284,&sStack_6);
      }
    }
    (*((short *)camry_host_ptr((uint32_t)(puVar2 + -0x3cbc)))) = sStack_6;
  }
  return;
}

void record_b_bounded_difference_bins_451d6(void)

{
  int iVar1;
  uint32_t puVar2;
  int iVar3;
  short sStack_6;
  
  puVar2 = 0xfebeb800u;
  sStack_6 = DAT_febe7b46;
  if (((int16_t)DAT_febe7b46) != -1) {
    iVar1 = (int)DAT_0002b9a2;
    iVar3 = (int)(short)(DAT_febe6358 - DAT_febe635a);
    if ((iVar3 - iVar1 < 0 != (iVar3 < 0 != iVar1 < 0 && iVar1 < 0 == iVar3 - iVar1 < 0) ||
         iVar3 == iVar1) &&
       (iVar3 + iVar1 < 0 == (iVar3 < 0 != -iVar1 < 0 && -iVar1 < 0 == iVar3 + iVar1 < 0))) {
      iVar3 = (int)((int)(int16_t)DAT_febe629e);
      iVar1 = (int)DAT_0002b9a4;
      if ((iVar3 - iVar1 < 0 != (iVar3 < 0 != iVar1 < 0 && iVar1 < 0 == iVar3 - iVar1 < 0) ||
           iVar3 == iVar1) &&
         (iVar3 + iVar1 < 0 == (iVar3 < 0 != -iVar1 < 0 && -iVar1 < 0 == iVar3 + iVar1 < 0))) {
        puVar2 = 0xfebeb800u;
        set_high_nibble_indexed_halfword_bit_44ece(DAT_febe6284,&sStack_6);
      }
    }
    (*((short *)camry_host_ptr((uint32_t)(puVar2 + -0x3cba)))) = sStack_6;
  }
  return;
}

void update_bounded_difference_binmap_pair_4522e(void)

{
  record_a_bounded_difference_bins_4517e();
  record_b_bounded_difference_bins_451d6();
  return;
}

void update_all_six_sample_binmaps_4523e(void)

{
  update_unfilled_reference_sum_binmaps_45062();
  update_unfilled_absolute_sample_binmaps_4515a();
  update_bounded_difference_binmap_pair_4522e();
  return;
}

void return_only_stub_45252(void)

{
  return;
}

void return_only_stub_45254(void)

{
  return;
}

void latch_gated_sample_lower_and_upper_crossings_45256(void)

{
  int iVar1;
  int iVar2;
  
  if ((DAT_febe8a24 == 'Z') &&
     ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe7cacu + (uint32_t)(9) * 1u)))) == '\0' &&
      ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe7cacu + (uint32_t)(8) * 1u)))) == '\0' &&
      ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe7cacu + (uint32_t)(3) * 1u)))) == '\0' &&
      ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe7cacu + (uint32_t)(2) * 1u)))) == '\0' &&
      ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe7cacu + (uint32_t)(1) * 1u)))) == '\0' && ((volatile uint8_t *)camry_host_ptr(0xfebe7cacu))[0] == '\0')))))) {
    iVar1 = (int)((int)(int16_t)DAT_febe62ba);
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

void return_only_stub_452a4(void)

{
  return;
}

void return_only_stub_452a6(void)

{
  return;
}

void publish_local_channel_monitor_actions_a(void)

{
  uint32_t puVar1;
  uchar uVar2;
  
  puVar1 = 0xfebeb800u;
  retain_and_clear_fault_record(7);
  if (((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x3cb3))))) & 0x22) == 0x22) {
    encode_fault_action_kind('\a','\x1b');
  }
  if (((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x3cb4))))) & 0x22) == 0x22) {
    encode_fault_action_kind('\a','\x1d');
  }
  select_current_fault_record(7);
  uVar2 = '\0';
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x3cb3))))) != '\0' || (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x3cb4))))) != '\0') {
    uVar2 = '\x11';
  }
  set_diagnostic_cache_blocker('\x06',uVar2);
  uVar2 = '\0';
  if ((((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x3cb3))))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x3cb4)))))) & 0x11) == 0x11) {
    uVar2 = 'Z';
  }
  set_monitor_pending_projection('\x04',uVar2);
  return;
}

void publish_local_channel_a_monitor_status(uchar index,uint packed_status)

{
  if (index < 2) {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe7b4cu + (uint32_t)(index) * 1u)))) = (char)packed_status;
  }
  return;
}

void reset_scalar_monitor_45356(void)

{
  reset_latched_monitor(((F33LatchedMonitorState *)camry_host_ptr((uint32_t)((0xfebe7b50u)))));
  return;
}

void reset_scalar_monitor_45356_45346(void)

{
  reset_latched_monitor(((F33LatchedMonitorState *)camry_host_ptr((uint32_t)((0xfebe7b50u)))));
  return;
}

void step_local_output_status_a_monitor(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  if (DAT_0002bc54 == 'Z') {
    reset_latched_monitor(((F33LatchedMonitorState *)camry_host_ptr((uint32_t)((0xfebe7b50u)))));
  }
  else if ((DAT_febe6764 & 1) == 0) {
    step_latched_monitor
              (((F33LatchedMonitorState *)camry_host_ptr((uint32_t)((0xfebe7b50u)))), ((F33MonitorLimits *)camry_host_ptr((uint32_t)((0x2b9b4u)))), ((F33TwoSidedMonitorCallbacks *)camry_host_ptr((uint32_t)((0x28ac8u)))));
  }
  else {
    retain_disabled_latched_monitor
              (((F33LatchedMonitorState *)camry_host_ptr((uint32_t)((0xfebe7b50u)))), ((F33MonitorLimits *)camry_host_ptr((uint32_t)((0x2b9b4u)))));
  }
  publish_local_channel_a_monitor_status('\x01',(*((uint *)camry_host_ptr((uint32_t)(puVar1 + -0x3cb0)))));
  return;
}

uint classify_local_output_status_a(void)

{
  if (((DAT_febe6624 & 1) != 0) && (DAT_febe65f6 == 'Z')) {
    if (DAT_febe8284 == 'Z') {
      return 0x22;
    }
    return 0x11;
  }
  return 0x44;
}

void report_scalar_event_8e_healthy_observed(void)

{
  report_diagnostic_healthy_observed(0x8e);
  return;
}

void report_scalar_event_8e_failure(void)

{
  report_diagnostic_event_failure(0x8e,0x32);
  return;
}

void reset_scalar_monitor_45410(void)

{
  reset_latched_monitor(((F33LatchedMonitorState *)camry_host_ptr((uint32_t)((0xfebe7b5cu)))));
  return;
}

void reset_scalar_monitor_45410_45400(void)

{
  reset_latched_monitor(((F33LatchedMonitorState *)camry_host_ptr((uint32_t)((0xfebe7b5cu)))));
  return;
}

void step_local_channel_mismatch_a_monitor(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  if (DAT_0002bc58 == 'Z') {
    reset_latched_monitor(((F33LatchedMonitorState *)camry_host_ptr((uint32_t)((0xfebe7b5cu)))));
  }
  else if (((DAT_febe6764 & 1) == 0) && (DAT_febee820 == 'Z')) {
    step_latched_monitor
              (((F33LatchedMonitorState *)camry_host_ptr((uint32_t)((0xfebe7b5cu)))), ((F33MonitorLimits *)camry_host_ptr((uint32_t)((0x2b9b8u)))), ((F33TwoSidedMonitorCallbacks *)camry_host_ptr((uint32_t)((0x28afcu)))));
  }
  else {
    retain_disabled_latched_monitor
              (((F33LatchedMonitorState *)camry_host_ptr((uint32_t)((0xfebe7b5cu)))), ((F33MonitorLimits *)camry_host_ptr((uint32_t)((0x2b9b8u)))));
  }
  publish_local_channel_a_monitor_status('\0',(*((uint *)camry_host_ptr((uint32_t)(puVar1 + -0x3ca4)))));
  return;
}

uint classify_local_channel_mismatch_a(void)

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

void report_scalar_event_77_healthy_observed(void)

{
  report_diagnostic_healthy_observed(0x77);
  return;
}

void report_scalar_event_77_failure(void)

{
  report_diagnostic_event_failure(0x77,0x32);
  return;
}

void return_only_stub_454c0(void)

{
  return;
}

void return_only_stub_454c2(void)

{
  return;
}

void publish_local_channel_monitor_actions_b(void)

{
  uint32_t puVar1;
  uchar uVar2;
  
  puVar1 = 0xfebeb800u;
  retain_and_clear_fault_record(8);
  if (((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x3c97))))) & 0x22) == 0x22) {
    encode_fault_action_kind('\b','\x1c');
  }
  if (((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x3c98))))) & 0x22) == 0x22) {
    encode_fault_action_kind('\b','\x1e');
  }
  select_current_fault_record(8);
  uVar2 = '\0';
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x3c97))))) != '\0' || (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x3c98))))) != '\0') {
    uVar2 = '\x11';
  }
  set_diagnostic_cache_blocker('\a',uVar2);
  uVar2 = '\0';
  if ((((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x3c97))))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x3c98)))))) & 0x11) == 0x11) {
    uVar2 = 'Z';
  }
  set_monitor_pending_projection('\x05',uVar2);
  return;
}

void publish_local_channel_b_monitor_status(uchar index,uint packed_status)

{
  if (index < 2) {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe7b68u + (uint32_t)(index) * 1u)))) = (char)packed_status;
  }
  return;
}

void reset_scalar_monitor_45572(void)

{
  reset_latched_monitor(((F33LatchedMonitorState *)camry_host_ptr((uint32_t)((0xfebe7b6cu)))));
  return;
}

void reset_scalar_monitor_45572_45562(void)

{
  reset_latched_monitor(((F33LatchedMonitorState *)camry_host_ptr((uint32_t)((0xfebe7b6cu)))));
  return;
}

void step_local_output_status_b_monitor(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  if (DAT_0002bc5c == 'Z') {
    reset_latched_monitor(((F33LatchedMonitorState *)camry_host_ptr((uint32_t)((0xfebe7b6cu)))));
  }
  else if ((DAT_febe6764 >> 1 & 1) == 0) {
    step_latched_monitor
              (((F33LatchedMonitorState *)camry_host_ptr((uint32_t)((0xfebe7b6cu)))), ((F33MonitorLimits *)camry_host_ptr((uint32_t)((0x2b9bcu)))), ((F33TwoSidedMonitorCallbacks *)camry_host_ptr((uint32_t)((0x28b30u)))));
  }
  else {
    retain_disabled_latched_monitor
              (((F33LatchedMonitorState *)camry_host_ptr((uint32_t)((0xfebe7b6cu)))), ((F33MonitorLimits *)camry_host_ptr((uint32_t)((0x2b9bcu)))));
  }
  publish_local_channel_b_monitor_status('\x01',(*((uint *)camry_host_ptr((uint32_t)(puVar1 + -0x3c94)))));
  return;
}

uint classify_local_output_status_b(void)

{
  if ((((byte)DAT_febe6624 & 2) != 0) && (DAT_febe65f7 == 'Z')) {
    if (DAT_febe8283 == 'Z') {
      return 0x22;
    }
    return 0x11;
  }
  return 0x44;
}

void report_scalar_event_8f_healthy_observed(void)

{
  report_diagnostic_healthy_observed(0x8f);
  return;
}

void report_scalar_event_8f_failure(void)

{
  report_diagnostic_event_failure(0x8f,0x32);
  return;
}

void reset_scalar_monitor_4562a(void)

{
  reset_latched_monitor(((F33LatchedMonitorState *)camry_host_ptr((uint32_t)((0xfebe7b78u)))));
  return;
}

void reset_scalar_monitor_4562a_4561a(void)

{
  reset_latched_monitor(((F33LatchedMonitorState *)camry_host_ptr((uint32_t)((0xfebe7b78u)))));
  return;
}

void step_local_channel_mismatch_b_monitor(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  if (DAT_0002bc60 == 'Z') {
    reset_latched_monitor(((F33LatchedMonitorState *)camry_host_ptr((uint32_t)((0xfebe7b78u)))));
  }
  else if (((DAT_febe6764 >> 1 & 1) == 0) && (DAT_febee820 == 'Z')) {
    step_latched_monitor
              (((F33LatchedMonitorState *)camry_host_ptr((uint32_t)((0xfebe7b78u)))), ((F33MonitorLimits *)camry_host_ptr((uint32_t)((0x2b9c0u)))), ((F33TwoSidedMonitorCallbacks *)camry_host_ptr((uint32_t)((0x28b64u)))));
  }
  else {
    retain_disabled_latched_monitor
              (((F33LatchedMonitorState *)camry_host_ptr((uint32_t)((0xfebe7b78u)))), ((F33MonitorLimits *)camry_host_ptr((uint32_t)((0x2b9c0u)))));
  }
  publish_local_channel_b_monitor_status('\0',(*((uint *)camry_host_ptr((uint32_t)(puVar1 + -0x3c88)))));
  return;
}

uint classify_local_channel_mismatch_b(void)

{
  if (((((*((volatile uint8_t *)camry_host_ptr(0xfebe64deu))) & 2) == 0) && (((*((volatile uint8_t *)camry_host_ptr(0xfebe64d6u))) & 2) == 0)) && (DAT_febe65f7 == 'Z'))
  {
    if (DAT_febe8281 == 'Z') {
      return 0x22;
    }
    return 0x11;
  }
  return 0x44;
}

void report_scalar_event_73_healthy_observed(void)

{
  report_diagnostic_healthy_observed(0x73);
  return;
}

void report_scalar_event_73_failure(void)

{
  report_diagnostic_event_failure(0x73,0x32);
  return;
}

void reset_scalar_monitor_456fa(void)

{
  reset_recoverable_monitor(((F33RecoverableMonitorState *)camry_host_ptr((uint32_t)((0xfebe7b84u)))));
  return;
}

void reset_scalar_monitor_456fa_456ea(void)

{
  reset_recoverable_monitor(((F33RecoverableMonitorState *)camry_host_ptr((uint32_t)((0xfebe7b84u)))));
  return;
}

void step_admitted_scalar_receive_condition_monitor(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  if (DAT_0002bc64 == 'Z') {
    DAT_febe6868 = 0;
    reset_recoverable_monitor(((F33RecoverableMonitorState *)camry_host_ptr((uint32_t)((0xfebe7b84u)))));
  }
  else if (DAT_febee820 == 'Z') {
    step_recoverable_monitor
              (((F33RecoverableMonitorState *)camry_host_ptr((uint32_t)((0xfebe7b84u)))), ((F33RecoverableMonitorLimits *)camry_host_ptr((uint32_t)((0x2b9c4u)))), ((F33RecoverableMonitorCallbacks *)camry_host_ptr((uint32_t)((0x28b98u)))));
  }
  else {
    DAT_febe6868 = 0;
    retain_disabled_recoverable_monitor
              (((F33RecoverableMonitorState *)camry_host_ptr((uint32_t)((0xfebe7b84u)))), ((F33RecoverableMonitorLimits *)camry_host_ptr((uint32_t)((0x2b9c4u)))));
  }
  publish_scalar_relation_monitor_status('\x03',(*((uint *)camry_host_ptr((uint32_t)(puVar1 + -0x3c7c)))));
  return;
}

uint classify_admitted_scalar_receive_condition(void)

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

uint classify_scalar_receive_recovery(void)

{
  if ((DAT_febe66b8 < DAT_0002b9da) && (DAT_0002b9dc < DAT_febe66b8)) {
    return 0x11;
  }
  return 0x22;
}

void report_scalar_event_a5_healthy_observed(void)

{
  report_diagnostic_healthy_observed(0xa5);
  return;
}

void report_scalar_event_a5_failure(void)

{
  DAT_febe6868 = 0;
  report_diagnostic_event_failure(0xa5,400);
  return;
}

void report_scalar_event_a5_pass(void)

{
  report_diagnostic_event_pass(0xa5);
  return;
}

void reset_scalar_monitor_45838(void)

{
  reset_recoverable_monitor(((F33RecoverableMonitorState *)camry_host_ptr((uint32_t)((0xfebe7b90u)))));
  return;
}

void reset_scalar_monitor_45838_45828(void)

{
  reset_recoverable_monitor(((F33RecoverableMonitorState *)camry_host_ptr((uint32_t)((0xfebe7b90u)))));
  return;
}

void step_paired_scalar_relation_monitor(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  if (DAT_0002bc68 == 'Z') {
    reset_recoverable_monitor(((F33RecoverableMonitorState *)camry_host_ptr((uint32_t)((0xfebe7b90u)))));
  }
  else if (((DAT_febe6764 & 3) == 0) && (DAT_febee820 == 'Z')) {
    step_recoverable_monitor
              (((F33RecoverableMonitorState *)camry_host_ptr((uint32_t)((0xfebe7b90u)))), ((F33RecoverableMonitorLimits *)camry_host_ptr((uint32_t)((0x2b9cau)))), ((F33RecoverableMonitorCallbacks *)camry_host_ptr((uint32_t)((0x28bd4u)))));
  }
  else {
    retain_disabled_recoverable_monitor
              (((F33RecoverableMonitorState *)camry_host_ptr((uint32_t)((0xfebe7b90u)))), ((F33RecoverableMonitorLimits *)camry_host_ptr((uint32_t)((0x2b9cau)))));
  }
  publish_scalar_relation_monitor_status('\0',(*((uint *)camry_host_ptr((uint32_t)(puVar1 + -0x3c70)))));
  return;
}

uint classify_paired_scalar_relation(void)

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

uint classify_paired_scalar_recovery(void)

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

void report_scalar_event_a2_healthy_observed(void)

{
  report_diagnostic_healthy_observed(0xa2);
  return;
}

void report_scalar_event_a2_failure(void)

{
  report_diagnostic_event_failure(0xa2,400);
  return;
}

void report_scalar_event_a2_pass(void)

{
  report_diagnostic_event_pass(0xa2);
  return;
}

void reset_scalar_monitor_4599c(void)

{
  reset_latched_monitor(((F33LatchedMonitorState *)camry_host_ptr((uint32_t)((0xfebe7b9cu)))));
  return;
}

void reset_scalar_monitor_4599c_4598c(void)

{
  reset_latched_monitor(((F33LatchedMonitorState *)camry_host_ptr((uint32_t)((0xfebe7b9cu)))));
  return;
}

void step_qualified_scalar_relation_a_monitor(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  if (DAT_0002bc6c == 'Z') {
    reset_latched_monitor(((F33LatchedMonitorState *)camry_host_ptr((uint32_t)((0xfebe7b9cu)))));
  }
  else if (((DAT_febe6764 >> 1 & 1) == 0) || (DAT_febee820 != 'Z')) {
    report_diagnostic_healthy_observed(0x9e);
  }
  else {
    step_latched_monitor
              (((F33LatchedMonitorState *)camry_host_ptr((uint32_t)((0xfebe7b9cu)))), ((F33MonitorLimits *)camry_host_ptr((uint32_t)((0x2b9d0u)))), ((F33TwoSidedMonitorCallbacks *)camry_host_ptr((uint32_t)((0x28c10u)))));
  }
  publish_scalar_relation_monitor_status('\x01',(*((uint *)camry_host_ptr((uint32_t)(puVar1 + -0x3c64)))));
  return;
}

uint classify_qualified_scalar_relation_a(void)

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

void report_scalar_event_9e_failure(void)

{
  report_diagnostic_event_failure(0x9e,400);
  return;
}

void reset_scalar_monitor_45a6c(void)

{
  reset_latched_monitor(((F33LatchedMonitorState *)camry_host_ptr((uint32_t)((0xfebe7ba8u)))));
  return;
}

void reset_scalar_monitor_45a6c_45a5c(void)

{
  reset_latched_monitor(((F33LatchedMonitorState *)camry_host_ptr((uint32_t)((0xfebe7ba8u)))));
  return;
}

void step_qualified_scalar_relation_b_monitor(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  if (DAT_0002bc70 == 'Z') {
    reset_latched_monitor(((F33LatchedMonitorState *)camry_host_ptr((uint32_t)((0xfebe7ba8u)))));
  }
  else if (((DAT_febe6764 & 1) == 0) || (DAT_febee820 != 'Z')) {
    report_diagnostic_healthy_observed(0x9f);
  }
  else {
    step_latched_monitor
              (((F33LatchedMonitorState *)camry_host_ptr((uint32_t)((0xfebe7ba8u)))), ((F33MonitorLimits *)camry_host_ptr((uint32_t)((0x2b9d4u)))), ((F33TwoSidedMonitorCallbacks *)camry_host_ptr((uint32_t)((0x28c44u)))));
  }
  publish_scalar_relation_monitor_status('\x02',(*((uint *)camry_host_ptr((uint32_t)(puVar1 + -0x3c58)))));
  return;
}

uint classify_qualified_scalar_relation_b(void)

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

void report_scalar_event_9f_failure(void)

{
  report_diagnostic_event_failure(0x9f,400);
  return;
}

void return_only_stub_45b1c(void)

{
  return;
}

void return_only_stub_45b1e(void)

{
  return;
}

void publish_scalar_relation_monitor_actions(void)

{
  uint32_t puVar1;
  undefined1 uVar2;
  undefined1 uVar3;
  undefined1 uVar4;
  
  puVar1 = 0xfebeb800u;
  retain_and_clear_fault_record(6);
  if ((((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x3c49))))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x3c4a))))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x3c4b))))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x3c4c)))))) & 0x22) == 0x22) {
    encode_fault_action_kind('\x06','\x16');
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
  select_current_fault_record(6);
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x3c48))))) = uVar4;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x3c47))))) = uVar3;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x3c46))))) = uVar2;
  return;
}

void publish_scalar_relation_monitor_status(uchar index,uint packed_status)

{
  if (index < 4) {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe7bb4u + (uint32_t)(index) * 1u)))) = (char)packed_status;
  }
  return;
}

void return_only_stub_45bb0(void)

{
  return;
}

void fill_constant_block_45bb2(void)

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

void publish_primary_scalar_availability(void)

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

void publish_channel_scalar_availability_a(void)

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

void publish_channel_scalar_availability_b(void)

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

void publish_paired_scalar_availability(void)

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

void update_scalar_availability(void)

{
  publish_primary_scalar_availability();
  publish_channel_scalar_availability_a();
  publish_channel_scalar_availability_b();
  publish_paired_scalar_availability();
  return;
}

void return_only_stub_45cca(void)

{
  return;
}

void return_only_stub_45ccc(void)

{
  return;
}

void clear_reserved_monitor_action_slot(void)

{
  retain_and_clear_fault_record(0x15);
  select_current_fault_record(0x15);
  set_diagnostic_cache_blocker('\n','\0');
  return;
}

void return_only_stub_45cfa(void)

{
  return;
}

void capture_and_persist_record_twelve_samples_45cfc(void)

{
  uint8_t stack_record_3c[60];
  uint32_t puVar1;
  undefined4 uVar2;
  undefined2 uVar3;
  undefined1 uVar4;
  undefined4 uVar5;
  undefined2 uVar6;
  undefined1 uVar7;
  short sVar8;
  short sVar9;
  
  puVar1 = 0xfebeb800u;
  if (DAT_febe7bc8 != 'Z') {
    return;
  }
  uVar2 = DAT_febe7bd8;
  uVar4 = DAT_febe7bca;
  uVar3 = DAT_febe7bd2;
  sVar9 = DAT_febe7bcc;
  sVar8 = DAT_febe7bce;
  if (DAT_febe7dcd == 'Z') {
    uVar5 = DAT_febee90c;
    uVar7 = DAT_febee815;
    uVar6 = DAT_febee896;
    if (((int16_t)DAT_febe7bcc) != -1) {
      sVar9 = DAT_febe7bcc + 1;
    }
  }
  else {
    uVar5 = DAT_febe7bd4;
    uVar7 = DAT_febe7bc9;
    uVar6 = DAT_febe7bd0;
    if (DAT_febe8b08 == '\0') goto LAB_00045d7e;
    uVar2 = DAT_febee90c;
    uVar4 = DAT_febee815;
    uVar3 = DAT_febee896;
    if (((int16_t)DAT_febe7bce) != -1) {
      sVar8 = DAT_febe7bce + 1;
    }
  }
  (*((uint32_t *)(stack_record_3c + 4))) = 0;
  stack_record_3c[9] = 0;
  stack_record_3c[17] = 0;
  puVar1 = 0xfebeb800u;
  (*((int16_t *)(stack_record_3c + 0))) = sVar9;
  (*((int16_t *)(stack_record_3c + 2))) = sVar8;
  stack_record_3c[8] = uVar7;
  (*((uint16_t *)(stack_record_3c + 10))) = uVar6;
  (*((uint32_t *)(stack_record_3c + 12))) = uVar5;
  stack_record_3c[16] = uVar4;
  (*((uint16_t *)(stack_record_3c + 18))) = uVar3;
  (*((uint32_t *)(stack_record_3c + 20))) = uVar2;
  nvm_set_record(0xc,(uint *)((int16_t *)(stack_record_3c)));
LAB_00045d7e:
  (*((short *)camry_host_ptr((uint32_t)(puVar1 + -0x3c34)))) = sVar9;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x3c37))))) = uVar7;
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x3c30)))) = uVar6;
  (*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + -0x3c2c)))) = uVar5;
  (*((short *)camry_host_ptr((uint32_t)(puVar1 + -0x3c32)))) = sVar8;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x3c36))))) = uVar4;
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x3c2e)))) = uVar3;
  (*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + -0x3c28)))) = uVar2;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x3c38))))) = 0;
  return;
}

uint load_record_twelve_samples_and_arm_capture_45d98(void)

{
  uint8_t stack_record_1c[28];
  undefined4 *puVar1;
  uint32_t puVar2;
  uint uVar3;
  undefined4 uVar4;
  undefined4 *puVar5;
  
  puVar2 = 0xfebeb800u;
  puVar1 = stack_record_1c;
  puVar5 = ((undefined *)camry_host_ptr(0x212a0u));
  do {
    uVar4 = *puVar5;
    puVar5 = puVar5 + 1;
    *puVar1 = uVar4;
    puVar1 = puVar1 + 1;
  } while (camry_host_addr(puVar5)!=((uint32_t)(0x212b8u)));
  uVar3 = nvm_get_record(0xc, camry_host_addr(stack_record_1c));
  if (uVar3 == 0x11) {
    (*((uint16_t *)((uint8_t *)stack_record_1c + 0u))) = 0;
    stack_record_1c[8] = 0;
    (*((uint16_t *)(stack_record_1c + 10))) = 0;
    (*((uint32_t *)(stack_record_1c + 12))) = 0;
    (*((uint16_t *)((uint8_t *)stack_record_1c + 2u))) = 0;
    stack_record_1c[16] = 0;
    (*((uint16_t *)(stack_record_1c + 18))) = 0;
    (*((uint32_t *)(stack_record_1c + 20))) = 0;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x3c38))))) = 0x5a;
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar2 + -0x3c34)))) = (undefined2)(*((uint32_t *)(stack_record_1c + 0)));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x3c37))))) = stack_record_1c[8];
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar2 + -0x3c30)))) = (*((uint16_t *)(stack_record_1c + 10)));
  (*((undefined4 *)camry_host_ptr((uint32_t)(puVar2 + -0x3c2c)))) = (*((uint32_t *)(stack_record_1c + 12)));
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar2 + -0x3c32)))) = (*((uint16_t *)((uint8_t *)stack_record_1c + 2u)));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x3c36))))) = stack_record_1c[16];
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar2 + -0x3c2e)))) = (*((uint16_t *)(stack_record_1c + 18)));
  (*((undefined4 *)camry_host_ptr((uint32_t)(puVar2 + -0x3c28)))) = (*((uint32_t *)(stack_record_1c + 20)));
  return uVar3;
}

uint clear_and_persist_record_twelve_samples_45e12(void)

{
  uint8_t stack_record_1c[28];
  
  DAT_febe7bcc = 0;
  DAT_febe7bc9 = 0;
  DAT_febe7bd0 = 0;
  DAT_febe7bd4 = 0;
  (*((uint16_t *)(stack_record_1c + 0))) = 0;
  stack_record_1c[8] = 0;
  (*((uint16_t *)(stack_record_1c + 10))) = 0;
  (*((uint32_t *)(stack_record_1c + 12))) = 0;
  DAT_febe7bce = 0;
  DAT_febe7bca = 0;
  DAT_febe7bd2 = 0;
  DAT_febe7bd8 = 0;
  (*((uint16_t *)(stack_record_1c + 2))) = 0;
  stack_record_1c[16] = 0;
  (*((uint16_t *)(stack_record_1c + 18))) = 0;
  (*((uint32_t *)(stack_record_1c + 20))) = 0;
  (*((uint32_t *)(stack_record_1c + 4))) = 0;
  stack_record_1c[9] = 0;
  stack_record_1c[17] = 0;
  return nvm_set_record(0xc,(uint *)stack_record_1c);
}

void reset_scalar_monitor_45e74(void)

{
  reset_recoverable_monitor(((F33RecoverableMonitorState *)camry_host_ptr((uint32_t)((0xfebe7bdcu)))));
  return;
}

void reset_scalar_monitor_45e74_45e64(void)

{
  reset_recoverable_monitor(((F33RecoverableMonitorState *)camry_host_ptr((uint32_t)((0xfebe7bdcu)))));
  return;
}

void step_raw_thermistor_range_a_monitor(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  if (DAT_0002bc74 == 'Z') {
    reset_recoverable_monitor(((F33RecoverableMonitorState *)camry_host_ptr((uint32_t)((0xfebe7bdcu)))));
  }
  else if ((DAT_febe6764 & 1) == 0) {
    step_recoverable_monitor
              (((F33RecoverableMonitorState *)camry_host_ptr((uint32_t)((0xfebe7bdcu)))), ((F33RecoverableMonitorLimits *)camry_host_ptr((uint32_t)((0x2ba0cu)))), ((F33RecoverableMonitorCallbacks *)camry_host_ptr((uint32_t)((0x28c78u)))));
  }
  else {
    retain_disabled_recoverable_monitor
              (((F33RecoverableMonitorState *)camry_host_ptr((uint32_t)((0xfebe7bdcu)))), ((F33RecoverableMonitorLimits *)camry_host_ptr((uint32_t)((0x2ba0cu)))));
  }
  publish_thermistor_range_monitor_status('\0',(*((uint *)camry_host_ptr((uint32_t)(puVar1 + -0x3c24)))));
  return;
}

uint classify_raw_thermistor_range_a(void)

{
  if ((DAT_0002ba1a <= DAT_febe6492) && (DAT_febe6492 <= DAT_0002ba18)) {
    return 0x11;
  }
  return 0x22;
}

void report_scalar_event_88_healthy_observed(void)

{
  report_diagnostic_healthy_observed(0x88);
  return;
}

void report_scalar_event_88_failure(void)

{
  report_diagnostic_event_failure(0x88,800);
  return;
}

void report_scalar_event_88_pass(void)

{
  report_diagnostic_event_pass(0x88);
  return;
}

void reset_scalar_monitor_45f32(void)

{
  reset_recoverable_monitor(((F33RecoverableMonitorState *)camry_host_ptr((uint32_t)((0xfebe7be8u)))));
  return;
}

void reset_scalar_monitor_45f32_45f22(void)

{
  reset_recoverable_monitor(((F33RecoverableMonitorState *)camry_host_ptr((uint32_t)((0xfebe7be8u)))));
  return;
}

void step_raw_thermistor_range_b_monitor(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  if (DAT_0002bc78 == 'Z') {
    reset_recoverable_monitor(((F33RecoverableMonitorState *)camry_host_ptr((uint32_t)((0xfebe7be8u)))));
  }
  else if ((DAT_febe6764 >> 1 & 1) == 0) {
    step_recoverable_monitor
              (((F33RecoverableMonitorState *)camry_host_ptr((uint32_t)((0xfebe7be8u)))), ((F33RecoverableMonitorLimits *)camry_host_ptr((uint32_t)((0x2ba12u)))), ((F33RecoverableMonitorCallbacks *)camry_host_ptr((uint32_t)((0x28cb4u)))));
  }
  else {
    retain_disabled_recoverable_monitor
              (((F33RecoverableMonitorState *)camry_host_ptr((uint32_t)((0xfebe7be8u)))), ((F33RecoverableMonitorLimits *)camry_host_ptr((uint32_t)((0x2ba12u)))));
  }
  publish_thermistor_range_monitor_status('\x01',(*((uint *)camry_host_ptr((uint32_t)(puVar1 + -0x3c18)))));
  return;
}

uint classify_raw_thermistor_range_b(void)

{
  if ((DAT_0002ba1e <= DAT_febe6498) && (DAT_febe6498 <= DAT_0002ba1c)) {
    return 0x11;
  }
  return 0x22;
}

void report_scalar_event_85_healthy_observed(void)

{
  report_diagnostic_healthy_observed(0x85);
  return;
}

void report_scalar_event_85_failure(void)

{
  report_diagnostic_event_failure(0x85,800);
  return;
}

void report_scalar_event_85_pass(void)

{
  report_diagnostic_event_pass(0x85);
  return;
}

void return_only_stub_45fd0(void)

{
  return;
}

void return_only_stub_45fd2(void)

{
  return;
}

void publish_thermistor_range_monitor_actions(void)

{
  ushort uVar1;
  uint32_t puVar2;
  puVar2 = 0xfebeb800u;
  retain_and_clear_fault_record(0x12);
  if ((((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x3c0b))))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x3c0c)))))) & 0x22) == 0x22) {
    encode_fault_action_kind('\x12','\x16');
  }
  select_current_fault_record(0x12);
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
