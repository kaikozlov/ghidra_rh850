#include "common.h"

void initialize_7004_calibrated_ratio_pair_3b0a2(short param_1,short param_2)

{
  uint32_t puVar1;
  undefined4 uVar2;
  undefined4 uVar3;
  
  puVar1 = 0xfebeb800u;
  uVar2 = compute_signed_ratio_q19_saturating_3ae66((int)param_1,(int)DAT_0002b53c);
  uVar3 = compute_signed_ratio_q19_saturating_3ae66((int)param_2,(int)DAT_0002b53e);
  (*((undefined4 *)camry_host_ptr((uint32_t)((0xffffb804u + (uint32_t)((int)puVar1)))))) = uVar2;
  (*((undefined4 *)camry_host_ptr((uint32_t)((0xffffb808u + (uint32_t)((int)puVar1)))))) = uVar3;
  (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffb7fcu + (uint32_t)((int)puVar1)))))) = 0x3480;
  return;
}

void clear_7000_pair_and_7004_ratio_states_3b0d8(void)

{
  DAT_febe7000 = 0;
  DAT_febe7002 = 0;
  DAT_febe7004 = 0;
  DAT_febe7008 = 0;
  return;
}

void return_only_stub_3b0e6(void)

{
  return;
}

void initialize_700c_half_ratio_constants_3b0e8(void)

{
  DAT_febe700c = 0x569a;
  DAT_febe700e = 0x2b4d;
  return;
}

void publish_ecu_source3_thermal_limit_maps(void)

{
  uint8_t stack_record_c[12];
  uint32_t puVar1;
  int iVar2;
  
  puVar1 = 0xfebeb800u;
  iVar2 = (int)((int)(int16_t)DAT_febe6fe2);
  interpolate_s16_axis_u16_values_7025c(((undefined *)camry_host_ptr(0x2b554u)),iVar2,((uint16_t *)(stack_record_c)));
  interpolate_s16_axis_u16_values_7025c(((undefined *)camry_host_ptr(0x2b570u)),iVar2,((uint16_t *)((stack_record_c + 2))));
  (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffb80cu + (uint32_t)((int)puVar1)))))) = (*((uint16_t *)(stack_record_c + 0)));
  (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffb80eu + (uint32_t)((int)puVar1)))))) = (*((uint16_t *)(stack_record_c + 2)));
  return;
}

void return_only_stub_3b132(void)

{
  return;
}

void initialize_two_six_sample_histories_3b134(void)

{
  uint uVar1;
  uint uVar2;
  
  DAT_febe7010 = 0x5a;
  uVar2 = 0;
  do {
    (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe701eu + (uint32_t)(uVar2) * 2u)))) = 0x3480;
    uVar2 = uVar2 + 1;
  } while (uVar2 < 6);
  uVar2 = 0;
  do {
    uVar1 = uVar2 + 1;
    (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe702au + (uint32_t)(uVar2) * 2u)))) = 0x3480;
    uVar2 = uVar1;
  } while (uVar1 < 6);
  DAT_febe7038 = 0;
  DAT_febe703c = 0;
  return;
}

void update_clamped_7dce_six_sample_history_3b16c(void)

{
  uint uVar1;
  short sVar2;
  uint uVar3;
  uint uVar4;
  int iVar5;
  int iVar6;
  int iVar7;
  undefined2 auStack_c [6];
  
  sVar2 = ((int)(int16_t)DAT_febe7dce);
  uVar3 = DAT_febe7bf8 & 0x33;
  if ((DAT_febe7bf8 & 0x33) == 0) {
    iVar6 = (int)((int)(int16_t)DAT_febe7dce);
    if (DAT_febe7010 == 0x5a) {
      uVar4 = 1;
      do {
        uVar1 = uVar4 + 1;
        (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe701eu + (uint32_t)(uVar4) * 2u)))) = sVar2;
        uVar4 = uVar1;
      } while (uVar1 < 6);
    }
    else {
      do {
        uVar4 = uVar3 + 1;
        auStack_c[uVar3] = (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe701eu + (uint32_t)(uVar3) * 2u))));
        uVar3 = uVar4;
      } while (uVar4 < 6);
      uVar4 = 0;
      do {
        uVar1 = uVar4 + 1;
        (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe7020u + (uint32_t)(uVar4) * 2u)))) = auStack_c[uVar4];
        uVar4 = uVar1;
        uVar3 = (uint)DAT_febe7010;
      } while (uVar1 < 5);
    }
  }
  else {
    iVar6 = (int)((int)(int16_t)DAT_febe7028);
    uVar3 = 0x5a;
  }
  iVar5 = (int)(int16_t)DAT_0002b58c;
  iVar7 = (int)(int16_t)DAT_0002b58e;
  DAT_febe7010 = (char)uVar3;
  if (iVar5 - iVar6 < 0 != (iVar5 < 0 != iVar6 < 0 && iVar6 < 0 == iVar5 - iVar6 < 0)) {
    iVar6 = iVar5;
  }
  DAT_febe701e = DAT_0002b58e;
  if (iVar6 - iVar7 < 0 == (iVar6 < 0 != iVar7 < 0 && iVar7 < 0 == iVar6 - iVar7 < 0)) {
    DAT_febe701e = (short)iVar6;
  }
  return;
}

void update_clamped_7dd6_six_sample_history_3b1fa(void)

{
  uint uVar1;
  short sVar2;
  uint uVar3;
  uint uVar4;
  int iVar5;
  int iVar6;
  int iVar7;
  undefined2 auStack_c [6];
  
  sVar2 = ((int)(int16_t)DAT_febe7dd6);
  uVar3 = DAT_febe7bf8 & 0x3300;
  if ((DAT_febe7bf8 & 0x3300) == 0) {
    iVar6 = (int)((int)(int16_t)DAT_febe7dd6);
    if (DAT_febe7011 == 0x5a) {
      uVar4 = 1;
      do {
        uVar1 = uVar4 + 1;
        (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe702au + (uint32_t)(uVar4) * 2u)))) = sVar2;
        uVar4 = uVar1;
      } while (uVar1 < 6);
    }
    else {
      do {
        uVar4 = uVar3 + 1;
        auStack_c[uVar3] = (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe702au + (uint32_t)(uVar3) * 2u))));
        uVar3 = uVar4;
      } while (uVar4 < 6);
      uVar4 = 0;
      do {
        uVar1 = uVar4 + 1;
        (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe702cu + (uint32_t)(uVar4) * 2u)))) = auStack_c[uVar4];
        uVar4 = uVar1;
        uVar3 = (uint)DAT_febe7011;
      } while (uVar1 < 5);
    }
  }
  else {
    iVar6 = (int)((int)(int16_t)DAT_febe7034);
    uVar3 = 0x5a;
  }
  iVar5 = (int)(int16_t)DAT_0002b58c;
  iVar7 = (int)(int16_t)DAT_0002b58e;
  DAT_febe7011 = (char)uVar3;
  if (iVar5 - iVar6 < 0 != (iVar5 < 0 != iVar6 < 0 && iVar6 < 0 == iVar5 - iVar6 < 0)) {
    iVar6 = iVar5;
  }
  DAT_febe702a = DAT_0002b58e;
  if (iVar6 - iVar7 < 0 == (iVar6 < 0 != iVar7 < 0 && iVar7 < 0 == iVar6 - iVar7 < 0)) {
    DAT_febe702a = (short)iVar6;
  }
  return;
}

void select_larger_history_sample_with_fault_latching_3b288(void)

{
  int iVar1;
  int iVar2;
  
  iVar2 = (int)((int)(int16_t)DAT_febe701e);
  iVar1 = (int)((int)(int16_t)DAT_febe702a);
  DAT_febe7036 = ((int)(int16_t)DAT_febe701e);
  if (iVar1 - iVar2 < 0 == (iVar1 < 0 != iVar2 < 0 && iVar2 < 0 == iVar1 - iVar2 < 0) &&
      iVar1 != iVar2) {
    DAT_febe7036 = ((int)(int16_t)DAT_febe702a);
  }
  if ((((DAT_febe7bf8 & 0x22) == 0) && ((DAT_febe7bf8 & 0x2200) != 0)) || (DAT_febe6764 == 2)) {
    DAT_febe7012 = '\x11';
    DAT_febe7014 = ((int)(int16_t)DAT_febe701e);
  }
  else if ((((DAT_febe7bf8 & 0x22) == 0) || ((DAT_febe7bf8 & 0x2200) != 0)) && (DAT_febe6764 != 1))
  {
    DAT_febe7014 = DAT_febe7036;
    if (((DAT_febe7bf8 & 0x22) == 0) || ((DAT_febe7bf8 & 0x2200) == 0)) {
      DAT_febe7012 = '\0';
    }
    else {
      if (DAT_febe7012 == '\x11') {
        DAT_febe7014 = ((int)(int16_t)DAT_febe701e);
        return;
      }
      if (DAT_febe7012 == '\"') {
        DAT_febe7014 = ((int)(int16_t)DAT_febe702a);
        return;
      }
    }
  }
  else {
    DAT_febe7012 = '\"';
    DAT_febe7014 = ((int)(int16_t)DAT_febe702a);
  }
  return;
}

void follow_selected_sample_with_two_fractional_filters_3b2f6(void)

{
  uint8_t stack_record_2c[44];
  short sVar1;
  short sVar2;
  uint32_t puVar3;
  int iVar4;
  F33FractionalFollowing16 FStack_20;
  F33FractionalFollowing16 FStack_18;
  
  sVar1 = ((int)(int16_t)DAT_febe7014);
  puVar3 = 0xfebeb800u;
  iVar4 = (int)((int)(int16_t)DAT_febe7014);
  FStack_18.accumulator = DAT_febe7038;
  FStack_18.target = ((int)(int16_t)DAT_febe7014);
  FStack_18.previous = ((int)(int16_t)DAT_febe7016);
  if ((short)( (int)(DAT_febe7038) / (int)0x10000) != ((int)(int16_t)DAT_febe7016)) {
    FStack_18.previous = ((int)(int16_t)DAT_febe7014);
    FStack_18.accumulator = iVar4 << 0x10;
  }
  follow_s16_fractional(&FStack_18,(uint)DAT_0002b590,((int16_t *)((stack_record_2c + 4))),((int32_t *)(stack_record_2c)));
  sVar2 = ((int)(int16_t)DAT_febe7018);
  FStack_20.target = sVar1;
  DAT_febe7016 = (*((int16_t *)(stack_record_2c + 4)));
  FStack_20.previous = ((int)(int16_t)DAT_febe7018);
  (*((int *)camry_host_ptr((uint32_t)((0xffffb838u + (uint32_t)((int)puVar3)))))) = (*((int32_t *)(stack_record_2c + 0)));
  FStack_20.accumulator = (*((int *)camry_host_ptr((uint32_t)((0xffffb83cu + (uint32_t)((int)puVar3))))));
  if ((short)(FStack_20.accumulator / 0x10000) != sVar2) {
    FStack_20.previous = sVar1;
    FStack_20.accumulator = iVar4 << 0x10;
  }
  follow_s16_fractional(&FStack_20,(uint)DAT_0002b592,((int16_t *)((stack_record_2c + 6))),((int32_t *)((stack_record_2c + 8))));
  DAT_febe7018 = (*((int16_t *)(stack_record_2c + 6)));
  (*((int *)camry_host_ptr((uint32_t)((0xffffb83cu + (uint32_t)((int)puVar3)))))) = (*((int32_t *)(stack_record_2c + 8)));
  return;
}

void run_init_chain_3b398(void)

{
  update_clamped_7dce_six_sample_history_3b16c();
  update_clamped_7dd6_six_sample_history_3b1fa();
  select_larger_history_sample_with_fault_latching_3b288();
  follow_selected_sample_with_two_fractional_filters_3b2f6();
  return;
}

void reset_latched_monitor_febe7040(void)

{
  reset_latched_monitor((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe7040u)));
  return;
}

void reset_latched_monitor_febe7040_3b3c0(void)

{
  reset_latched_monitor((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe7040u)));
  return;
}

void reset_or_step_7040_latched_monitor_3b3d0(void)

{
  if (DAT_0002bb30 == 'Z') {
    reset_latched_monitor((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe7040u)));
  }
  else {
    step_latched_monitor
              ((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe7040u)),(F33MonitorLimits *)((undefined *)camry_host_ptr(0x2b5d0u)),
               (F33TwoSidedMonitorCallbacks *)&PTR_FUN_00027f64);
  }
  return;
}

undefined4 classify_6772_magnitude_minus_6f6e_threshold_3b400(void)

{
  int iVar1;
  undefined4 uVar2;
  int iVar3;
  uint uVar4;
  short sStack_a;
  
  uVar4 = (uint)DAT_febe6f6e;
  store_saturating_absolute_s16_6a522((int)((int)(int16_t)DAT_febe6772),&sStack_a);
  iVar3 = (int)DAT_0002b5d8;
  iVar1 = ((int)sStack_a - uVar4) - iVar3;
  if (iVar1 < 0 == ((int)((int)sStack_a - uVar4) < 0 != iVar3 < 0 && iVar3 < 0 == iVar1 < 0)) {
    uVar2 = 0x22;
  }
  else {
    uVar2 = 0x11;
  }
  return uVar2;
}

void report_event_6e_and_channel_zero_failure_3b434(void)

{
  report_diagnostic_event_failure(0x6e,800);
  increment_indexed_u16_counter_once_until_rearmed_545de(3);
  gate_indexed_event_payload_during_diagnostic_clears_51cf6(0,800);
  return;
}

void reset_latched_monitor_febe704c(void)

{
  reset_latched_monitor((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe704cu)));
  return;
}

void reset_latched_monitor_febe704c_3b468(void)

{
  reset_latched_monitor((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe704cu)));
  return;
}

void reset_or_step_704c_latched_monitor_3b478(void)

{
  if (DAT_0002bb34 == 'Z') {
    reset_latched_monitor((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe704cu)));
  }
  else {
    step_latched_monitor
              ((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe704cu)),(F33MonitorLimits *)((undefined *)camry_host_ptr(0x2b5d4u)),
               (F33TwoSidedMonitorCallbacks *)&PTR_FUN_00027f98);
  }
  return;
}

undefined4 classify_6772_magnitude_minus_6f74_threshold_3b4a8(void)

{
  int iVar1;
  undefined4 uVar2;
  int iVar3;
  uint uVar4;
  short sStack_a;
  
  uVar4 = (uint)DAT_febe6f74;
  store_saturating_absolute_s16_6a522((int)((int)(int16_t)DAT_febe6772),&sStack_a);
  iVar3 = (int)DAT_0002b5dc;
  iVar1 = ((int)sStack_a - uVar4) - iVar3;
  if (iVar1 < 0 == ((int)((int)sStack_a - uVar4) < 0 != iVar3 < 0 && iVar3 < 0 == iVar1 < 0)) {
    uVar2 = 0x22;
  }
  else {
    uVar2 = 0x11;
  }
  return uVar2;
}

void report_event_6d_and_channel_one_failure_3b4dc(void)

{
  report_diagnostic_event_failure(0x6d,800);
  increment_indexed_u16_counter_once_until_rearmed_545de(2);
  gate_indexed_event_payload_during_diagnostic_clears_51cf6(1,800);
  return;
}

void return_only_stub_3b500(void)

{
  return;
}

uint32_t clear_eight_channel_7058_state_when_inactive_3b502(void)

{
  uint32_t camry_r10_result;
  int iVar1;
  int iVar2;
  uint32_t puVar3;
  int iVar4;
  
  puVar3 = 0xfebeb800u;
  iVar4 = (camry_r10_result = test_redundant_status_a5_or_vote_error13_588b6());
  if (iVar4 == 0) {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffb858u + (uint32_t)((int)puVar3) * 1u)))) = 0;
    iVar4 = 0;
    do {
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe7059u + (uint32_t)(iVar4) * 1u)))) = 0;
      iVar2 = iVar4 + 1;
      iVar1 = iVar4 + -7;
      iVar4 = iVar2;
    } while (((iVar1 < 0) || (iVar2 < 0)));
    iVar4 = 0;
    do {
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe7061u + (uint32_t)(iVar4) * 1u)))) = 0;
      iVar2 = iVar4 + 1;
      iVar1 = iVar4 + -7;
      iVar4 = iVar2;
    } while (((iVar1 < 0) || (iVar2 < 0)));
    iVar4 = 0;
    do {
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe7069u + (uint32_t)(iVar4) * 1u)))) = 0;
      iVar2 = iVar4 + 1;
      iVar1 = iVar4 + -7;
      iVar4 = iVar2;
    } while (((iVar1 < 0) || (iVar2 < 0)));
    iVar4 = 0;
    do {
      iVar2 = iVar4 + 1;
      *(undefined4 *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe7090u + (uint32_t)(iVar4 * 4) * 1u)))) = 0;
      iVar1 = iVar4 + -7;
      iVar4 = iVar2;
    } while (((iVar1 < 0) || (iVar2 < 0)));
    DAT_febe7071 = 0;
    DAT_febe7072 = 0;
  }
  return camry_r10_result;
}

uint should_zero_restored_thermal_offset(short record_marker)

{
  int iVar1;
  uint uVar2;
  int iVar3;
  int iVar4;
  
  iVar4 = (int)((int)(int16_t)DAT_febe7dce);
  iVar3 = (int)((int)(int16_t)DAT_febe7dd6);
  if ((DAT_febe7bf8 & 0xff) == 0) {
    iVar1 = iVar4;
    if ((DAT_febe7bf8 & 0xff00) != 0) goto LAB_0003b586;
  }
  else {
    iVar1 = iVar3;
    if ((DAT_febe7bf8 & 0xff00) == 0) goto LAB_0003b586;
  }
  iVar1 = iVar4;
  if (iVar3 - iVar4 < 0 == (iVar3 < 0 != iVar4 < 0 && iVar4 < 0 == iVar3 - iVar4 < 0) &&
      iVar3 != iVar4) {
    iVar1 = iVar3;
  }
LAB_0003b586:
  iVar3 = (int)DAT_0002b59e;
  if ((iVar1 - iVar3 < 0 == (iVar1 < 0 != iVar3 < 0 && iVar3 < 0 == iVar1 - iVar3 < 0)) ||
     (record_marker != 0)) {
    uVar2 = 0;
  }
  else {
    uVar2 = 0x5a;
  }
  DAT_febe707e = ((int)(int16_t)DAT_febe7dce);
  DAT_febe7080 = ((int)(int16_t)DAT_febe7dd6);
  return uVar2;
}

int seed_thermal_offset_pole(short contribution,short gain)

{
  int iVar1;
  int iVar2;
  int local_8;
  
  iVar2 = (int)gain;
  if (iVar2 == 0) {
    local_8 = 0;
  }
  else {
    iVar1 = (int)contribution << 0xc;
    if (iVar2 != 0) {
      if (iVar1 == -0x80000000 && iVar2 == -1) {
        iVar1 = -0x80000000;
      }
      else {
        iVar1 = (int)iVar1 / (int)iVar2;
      }
    }
    store_symmetric_saturating_s32_product_706ae(iVar1,0x80,&local_8);
  }
  return local_8;
}

void seed_dual_thermal_offset_poles_and_outputs_3b5d2(short param_1,short param_2)

{
  uint32_t puVar1;
  int iVar2;
  int iVar3;
  
  puVar1 = 0xfebeb800u;
  iVar2 = seed_thermal_offset_pole(param_1,DAT_0002b5ac);
  iVar3 = seed_thermal_offset_pole(param_2,DAT_0002b5ae);
  (*((int *)camry_host_ptr((uint32_t)((0xffffb8bcu + (uint32_t)((int)puVar1)))))) = iVar2;
  (*((int *)camry_host_ptr((uint32_t)((0xffffb8c0u + (uint32_t)((int)puVar1)))))) = iVar3;
  (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffb874u + (uint32_t)((int)puVar1)))))) = 0x3980;
  (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffb876u + (uint32_t)((int)puVar1)))))) = 0x3980;
  (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffb878u + (uint32_t)((int)puVar1)))))) = 0x3980;
  return;
}

void restore_thermal_offset_terms(void)

{
  uint8_t stack_record_3c[60];
  uint *puVar1;
  uint32_t puVar2;
  int iVar3;
  int iVar4;
  uint uVar5;
  undefined4 uVar6;
  undefined4 *puVar7;
  
  puVar2 = 0xfebeb800u;
  puVar1 = ((uint32_t *)(stack_record_3c));
  puVar7 = ((undefined *)camry_host_ptr(0x21268u));
  do {
    uVar6 = *puVar7;
    puVar7 = puVar7 + 1;
    *puVar1 = uVar6;
    puVar1 = puVar1 + 1;
  } while (camry_host_addr(puVar7)!=((uint32_t)(0x212a0u)));
  uVar5 = nvm_get_record(6, camry_host_addr(((uint32_t *)(stack_record_3c))));
  if ((uVar5 == 0x10) && ((*((int16_t *)(stack_record_3c + 50))) != -0x5aa6)) {
    if ((((((*((ushort *)camry_host_ptr((uint32_t)(puVar2 + -0x3c08)))) & 0xff) == 0) ||
         (((*((ushort *)camry_host_ptr((uint32_t)(puVar2 + -0x3c08)))) & 0xff00) == 0)) && ((*((int16_t *)(stack_record_3c + 50))) != 0x5aa5)) &&
       (uVar5 = should_zero_restored_thermal_offset((*((int16_t *)(stack_record_3c + 50)))), uVar5 == 0x5a)) {
      iVar3 = 0;
      iVar4 = 0;
    }
    else {
      iVar3 = (int)(*((int16_t *)(stack_record_3c + 22)));
      iVar4 = (int)(*((int16_t *)(stack_record_3c + 20)));
    }
  }
  else {
    iVar3 = (int)DAT_0002b5b0;
    iVar4 = (int)DAT_0002b5b2;
  }
  seed_dual_thermal_offset_poles_and_outputs_3b5d2(iVar3,iVar4);
  return;
}

int stage_dual_thermal_squared_inputs(short upper,short lower)

{
  uint8_t stack_record_38[56];
  undefined4 uVar1;
  undefined4 uVar2;
  short sVar3;
  short sVar4;
  int iVar5;
  int iVar6;
  uint32_t puVar7;
  int iVar8;
  int iVar9;
  int iVar10;
  int iVar11;
  
  iVar9 = DAT_febe70c0;
  iVar8 = DAT_febe70bc;
  sVar4 = ((int)(int16_t)DAT_febe66ec);
  sVar3 = ((int)(int16_t)DAT_febe66ea);
  uVar2 = DAT_0002b5c4;
  uVar1 = DAT_0002b5c0;
  puVar7 = 0xfebeb800u;
  (*((int32_t *)(stack_record_38 + 8))) = (int)((int)(int16_t)DAT_febe66e8) * (int)((int)(int16_t)DAT_febe66e8) + (int)((int)(int16_t)DAT_febe66e6) * (int)((int)(int16_t)DAT_febe66e6);
  store_u32_max_third_min_first_two_7013e((*((int32_t *)(stack_record_38 + 8))),DAT_0002b5c0,DAT_0002b5c4,((int32_t *)((stack_record_38 + 8))));
  (*((int32_t *)(stack_record_38 + 12))) = (int)sVar4 * (int)sVar4 + (int)sVar3 * (int)sVar3;
  store_u32_max_third_min_first_two_7013e((*((int32_t *)(stack_record_38 + 12))),uVar1,uVar2,((int32_t *)((stack_record_38 + 12))));
  iVar6 = (*((int32_t *)(stack_record_38 + 12)));
  iVar5 = (*((int32_t *)(stack_record_38 + 8)));
  (*((int32_t *)(stack_record_38 + 0))) = (*((int32_t *)(stack_record_38 + 12))) + (*((int32_t *)(stack_record_38 + 8)));
  store_s32_max_third_min_first_two_7012a((*((int32_t *)(stack_record_38 + 0))),DAT_0002b5c8,DAT_0002b5cc,((int32_t *)(stack_record_38)));
  iVar8 = update_nonnegative_thermal_pole(iVar8,(*((int32_t *)(stack_record_38 + 0))),(uint)DAT_0002b5a8);
  iVar9 = update_nonnegative_thermal_pole(iVar9,(*((int32_t *)(stack_record_38 + 0))),(uint)DAT_0002b5aa);
  iVar10 = scale_thermal_contribution(iVar8,DAT_0002b5ac,upper,lower);
  iVar11 = scale_thermal_contribution(iVar9,DAT_0002b5ae,upper,lower);
  (*((int32_t *)(stack_record_38 + 4))) = (int)DAT_0002b59e + iVar10 + iVar11;
  store_s32_max_third_min_first_two_7012a((*((int32_t *)(stack_record_38 + 4))),(int)upper,(int)lower,((int32_t *)((stack_record_38 + 4))));
  (*((int *)camry_host_ptr((uint32_t)((0xffffb8b4u + (uint32_t)((int)puVar7)))))) = iVar5;
  (*((int *)camry_host_ptr((uint32_t)((0xffffb8b8u + (uint32_t)((int)puVar7)))))) = iVar6;
  (*((int *)camry_host_ptr((uint32_t)((0xffffb8b0u + (uint32_t)((int)puVar7)))))) = (*((int32_t *)(stack_record_38 + 0)));
  (*((int *)camry_host_ptr((uint32_t)((0xffffb8c0u + (uint32_t)((int)puVar7)))))) = iVar9;
  (*((int *)camry_host_ptr((uint32_t)((0xffffb8bcu + (uint32_t)((int)puVar7)))))) = iVar8;
  (*((short *)camry_host_ptr((uint32_t)((0xffffb87au + (uint32_t)((int)puVar7)))))) = (short)iVar10;
  (*((short *)camry_host_ptr((uint32_t)((0xffffb87cu + (uint32_t)((int)puVar7)))))) = (short)iVar11;
  return (int)(short)(*((int32_t *)(stack_record_38 + 4)));
}

void follow_7074_with_two_fractional_filters_3b76e(void)

{
  uint8_t stack_record_2c[44];
  short sVar1;
  short sVar2;
  uint32_t puVar3;
  int iVar4;
  F33FractionalFollowing16 FStack_20;
  F33FractionalFollowing16 FStack_18;
  
  sVar1 = ((int)(int16_t)DAT_febe7074);
  puVar3 = 0xfebeb800u;
  iVar4 = (int)((int)(int16_t)DAT_febe7074);
  FStack_18.accumulator = DAT_febe7088;
  FStack_18.target = ((int)(int16_t)DAT_febe7074);
  FStack_18.previous = ((int)(int16_t)DAT_febe7076);
  if ((short)( (int)(DAT_febe7088) / (int)0x10000) != ((int)(int16_t)DAT_febe7076)) {
    FStack_18.previous = ((int)(int16_t)DAT_febe7074);
    FStack_18.accumulator = iVar4 << 0x10;
  }
  follow_s16_fractional(&FStack_18,(uint)DAT_0002b5b4,((int16_t *)((stack_record_2c + 4))),((int32_t *)(stack_record_2c)));
  sVar2 = ((int)(int16_t)DAT_febe7078);
  FStack_20.target = sVar1;
  DAT_febe7076 = (*((int16_t *)(stack_record_2c + 4)));
  FStack_20.previous = ((int)(int16_t)DAT_febe7078);
  (*((int *)camry_host_ptr((uint32_t)((0xffffb888u + (uint32_t)((int)puVar3)))))) = (*((int32_t *)(stack_record_2c + 0)));
  FStack_20.accumulator = (*((int *)camry_host_ptr((uint32_t)((0xffffb88cu + (uint32_t)((int)puVar3))))));
  if ((short)(FStack_20.accumulator / 0x10000) != sVar2) {
    FStack_20.previous = sVar1;
    FStack_20.accumulator = iVar4 << 0x10;
  }
  follow_s16_fractional(&FStack_20,(uint)DAT_0002b5b6,((int16_t *)((stack_record_2c + 6))),((int32_t *)((stack_record_2c + 8))));
  DAT_febe7078 = (*((int16_t *)(stack_record_2c + 6)));
  (*((int *)camry_host_ptr((uint32_t)((0xffffb88cu + (uint32_t)((int)puVar3)))))) = (*((int32_t *)(stack_record_2c + 8)));
  return;
}

void update_7058_state_from_eight_channel_flags_3b810(void)

{
  int iVar1;
  ushort uVar2;
  int iVar3;
  
  uVar2 = DAT_febe7bf8;
  iVar3 = 7;
  do {
    if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe7061u + (uint32_t)(iVar3) * 1u)))) == '\0') goto LAB_0003b83a;
    iVar1 = iVar3 + -1;
    iVar3 = iVar3 + -1;
  } while (-1 < iVar1);
  DAT_febe7058 = '\x02';
  iVar3 = 7;
  do {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe7061u + (uint32_t)(iVar3) * 1u)))) = 0;
    iVar1 = iVar3 + -1;
    iVar3 = iVar3 + -1;
  } while (-1 < iVar1);
LAB_0003b83a:
  iVar3 = 7;
  do {
    if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe7069u + (uint32_t)(iVar3) * 1u)))) == '\0') goto LAB_0003b85a;
    iVar1 = iVar3 + -1;
    iVar3 = iVar3 + -1;
  } while (-1 < iVar1);
  DAT_febe7058 = '\0';
  iVar3 = 7;
  do {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe7069u + (uint32_t)(iVar3) * 1u)))) = 0;
    iVar1 = iVar3 + -1;
    iVar3 = iVar3 + -1;
  } while (-1 < iVar1);
LAB_0003b85a:
  if ((((DAT_febe7058 == '\0') || (DAT_febe7058 == '\x03')) && ((uVar2 & 0x22) != 0)) &&
     ((uVar2 & 0x2200) != 0)) {
    DAT_febe7058 = '\x01';
  }
  else if (DAT_febe7058 != '\x01' && DAT_febe7058 != '\x02') {
    return;
  }
  if (((uVar2 & 0x22) == 0) || ((uVar2 & 0x2200) == 0)) {
    DAT_febe7058 = '\x03';
  }
  return;
}

void restore_and_step_dual_thermal_offset_state_3b88e(void)

{
  uint32_t puVar1;
  undefined *puVar2;
  int iVar4;
  char cVar5;
  uint32_t puVar3;
  puVar3 = 0xfebeb800u;
  puVar2 = ((undefined *)camry_host_ptr(0xfebeb800u));
  cVar5 = DAT_febe7072;
  puVar1 = (0xfebeb800u);
  if (DAT_febe7072 == '\0') {
    if ((DAT_febe7dcc != 'Z') || (DAT_febe7bf6 != 'Z')) goto LAB_0003b8dc;
    restore_thermal_offset_terms();
    cVar5 = 'Z';
    puVar1 = ((uint32_t)(puVar3));
  }
  puVar2 = ((void *)camry_host_ptr((uint32_t)(puVar1)));
  iVar4 = stage_dual_thermal_squared_inputs(DAT_0002b596,DAT_0002b598);
  DAT_febe7074 = (undefined2)iVar4;
  follow_7074_with_two_fractional_filters_3b76e();
  update_7058_state_from_eight_channel_flags_3b810();
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffb871u + (uint32_t)((int)camry_host_addr(puVar2)) * 1u)))) = 0x5a;
LAB_0003b8dc:
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffb872u + (uint32_t)((int)camry_host_addr(puVar2)) * 1u)))) = cVar5;
  return;
}

int follow_thermal_offset_target(uint selector,short target,short previous,short bias)

{
  uint8_t stack_record_22[34];
  int iVar1;
  int iVar2;
  F33FractionalFollowing16 FStack_18;
  
  iVar1 = (selector & 0xff) * 4;
  FStack_18.accumulator = *(int *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe7090u + (uint32_t)(iVar1) * 1u))));
  if ((int)(short)(FStack_18.accumulator / 0x10000) != (int)previous) {
    FStack_18.accumulator = (int)previous << 0x10;
  }
  FStack_18.previous = previous;
  FStack_18.target = target;
  follow_s16_fractional(&FStack_18,(uint)DAT_0002b594 * 800,((int16_t *)(stack_record_22)),((int32_t *)((stack_record_22 + 6))));
  iVar2 = (int)DAT_0002b596;
  *(int *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe7090u + (uint32_t)(iVar1) * 1u)))) = bias * 0x10000 + (*((int32_t *)(stack_record_22 + 6)));
  (*((int32_t *)(stack_record_22 + 2))) = (int)(*((int16_t *)(stack_record_22 + 0))) + (int)bias;
  store_minimum_s32_70160((*((int32_t *)(stack_record_22 + 2))),iVar2,((int32_t *)((stack_record_22 + 2))));
  return (int)(short)(*((int32_t *)(stack_record_22 + 2)));
}

int apply_thermal_offset_and_following(uint selector,short raw_estimate,short previous)

{
  uint8_t stack_record_1c[28];
  char cVar1;
  undefined4 uVar2;
  uint32_t puVar3;
  short sVar4;
  int iVar5;
  int iVar6;
  uint selector_00;
  
  puVar3 = 0xfebeb800u;
  selector_00 = selector & 0xff;
  if (((DAT_febe7bf8 & 0x22) == 0) || ((DAT_febe7bf8 & 0x2200) == 0)) {
    sVar4 = (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe7014u + (uint32_t)(""[selector_00 * 2]) * 2u))));
  }
  else {
    sVar4 = (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe7074u + (uint32_t)(""[selector_00 * 2 + 1]) * 2u))));
  }
  store_s32_saturated_to_symmetric_s16_6a5fa((int)sVar4 + (int)raw_estimate,((int16_t *)(stack_record_1c)));
  store_s16_max_third_min_first_two_70110((int)(*((int16_t *)(stack_record_1c + 0))),(int)DAT_0002b59a,(int)DAT_0002b59c,((int16_t *)(stack_record_1c)));
  cVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffb858u + (uint32_t)((int)puVar3) * 1u))));
  store_symmetric_saturating_s16_difference_70706((int)(*((int16_t *)(stack_record_1c + 0))),(int)previous,((int16_t *)((stack_record_1c + 2))));
  store_saturating_absolute_s16_6a522((int)(*((int16_t *)(stack_record_1c + 2))),((int16_t *)((stack_record_1c + 2))));
  uVar2 = 0;
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe7059u + (uint32_t)(selector_00) * 1u)))) != '\0') {
    if (cVar1 == '\x01') {
      iVar6 = (int)DAT_0002b5a0;
      iVar5 = (*((int16_t *)(stack_record_1c + 2))) - iVar6;
      if (iVar5 < 0 == ((*((int16_t *)(stack_record_1c + 2))) < 0 != iVar6 < 0 && iVar6 < 0 == iVar5 < 0)) {
        uVar2 = 2;
      }
      else {
        uVar2 = 3;
      }
    }
    else if (cVar1 == '\x03') {
      iVar6 = (int)DAT_0002b5a0;
      iVar5 = (*((int16_t *)(stack_record_1c + 2))) - iVar6;
      if (iVar5 < 0 == ((*((int16_t *)(stack_record_1c + 2))) < 0 != iVar6 < 0 && iVar6 < 0 == iVar5 < 0)) {
        uVar2 = 4;
      }
      else {
        uVar2 = 5;
      }
    }
    else if (cVar1 == '\0') {
      uVar2 = 1;
    }
    else {
      uVar2 = 6;
    }
  }
  switch(uVar2) {
  case 0:
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe7059u + (uint32_t)(selector_00) * 1u)))) = 1;
    break;
  case 2:
    sVar4 = DAT_0002b5a2;
    goto LAB_0003ba5e;
  case 3:
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe7061u + (uint32_t)(selector_00) * 1u)))) = 1;
    break;
  case 4:
    sVar4 = DAT_0002b5a4;
LAB_0003ba5e:
    iVar5 = follow_thermal_offset_target(selector_00,(*((int16_t *)(stack_record_1c + 0))),previous,sVar4);
    (*((int16_t *)(stack_record_1c + 0))) = (short)iVar5;
    break;
  case 5:
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe7069u + (uint32_t)(selector_00) * 1u)))) = 1;
  }
  return (int)(*((int16_t *)(stack_record_1c + 0)));
}

void clear_70b0_70b4_70b8_states_3ba78(void)

{
  DAT_febe70b4 = 0;
  DAT_febe70b8 = 0;
  DAT_febe70b0 = 0;
  return;
}

void clear_707a_pair_and_thermal_offset_poles_3ba84(void)

{
  DAT_febe707a = 0;
  DAT_febe707c = 0;
  DAT_febe70bc = 0;
  DAT_febe70c0 = 0;
  return;
}

void reset_scalar_monitor_3bab2(void)

{
  reset_windowed_monitor(((F33WindowedMonitorState *)camry_host_ptr((uint32_t)((0xfebe70c8u)))));
  return;
}

void reset_scalar_monitor_3bab2_3baa2(void)

{
  reset_windowed_monitor(((F33WindowedMonitorState *)camry_host_ptr((uint32_t)((0xfebe70c8u)))));
  return;
}

void step_acquisition_status_a_monitor(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  if (DAT_0002bb38 == 'Z') {
    reset_windowed_monitor(((F33WindowedMonitorState *)camry_host_ptr((uint32_t)((0xfebe70c8u)))));
  }
  else {
    step_windowed_monitor
              (((F33WindowedMonitorState *)camry_host_ptr((uint32_t)((0xfebe70c8u)))), ((F33WindowedMonitorLimits *)camry_host_ptr((uint32_t)((0x2b5e0u)))), ((F33TwoSidedMonitorCallbacks *)camry_host_ptr((uint32_t)((0x27fccu)))));
  }
  publish_acquisition_monitor_status('\0',(*((uint *)camry_host_ptr((uint32_t)((0xffffb8c8u + (uint32_t)((int)puVar1)))))));
  return;
}

uint classify_acquisition_status_a(void)

{
  if (DAT_febe81d0 == 'Z') {
    return 0x22;
  }
  return 0x11;
}

void report_scalar_event_d3_healthy_observed(void)

{
  report_diagnostic_healthy_observed(0xd3);
  return;
}

void report_scalar_event_d3_failure(void)

{
  report_diagnostic_event_failure(0xd3,10);
  return;
}

void reset_scalar_monitor_3bb44(void)

{
  reset_windowed_monitor(((F33WindowedMonitorState *)camry_host_ptr((uint32_t)((0xfebe70d8u)))));
  return;
}

void reset_scalar_monitor_3bb44_3bb34(void)

{
  reset_windowed_monitor(((F33WindowedMonitorState *)camry_host_ptr((uint32_t)((0xfebe70d8u)))));
  return;
}

void step_acquisition_status_b_monitor(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  if (DAT_0002bb3c == 'Z') {
    reset_windowed_monitor(((F33WindowedMonitorState *)camry_host_ptr((uint32_t)((0xfebe70d8u)))));
  }
  else {
    step_windowed_monitor
              (((F33WindowedMonitorState *)camry_host_ptr((uint32_t)((0xfebe70d8u)))), ((F33WindowedMonitorLimits *)camry_host_ptr((uint32_t)((0x2b5e8u)))), ((F33TwoSidedMonitorCallbacks *)camry_host_ptr((uint32_t)((0x28000u)))));
  }
  publish_acquisition_monitor_status('\x01',(*((uint *)camry_host_ptr((uint32_t)((0xffffb8d8u + (uint32_t)((int)puVar1)))))));
  return;
}

uint classify_acquisition_status_b(void)

{
  if (DAT_febe81d1 == 'Z') {
    return 0x22;
  }
  return 0x11;
}

void report_scalar_event_d4_healthy_observed(void)

{
  report_diagnostic_healthy_observed(0xd4);
  return;
}

void report_scalar_event_d4_failure(void)

{
  report_diagnostic_event_failure(0xd4,10);
  return;
}

void return_only_stub_3bbb6(void)

{
  return;
}

void return_only_stub_3bbb8(void)

{
  return;
}

void publish_acquisition_monitor_actions(void)

{
  uint32_t puVar1;
  uchar status;
  
  puVar1 = 0xfebeb800u;
  retain_and_clear_fault_record(0x14);
  if ((((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffb8ebu + (uint32_t)((int)puVar1) * 1u)))) |
       (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffb8eau + (uint32_t)((int)puVar1) * 1u)))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffb8e9u + (uint32_t)((int)puVar1) * 1u)))) | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffb8e8u + (uint32_t)((int)puVar1) * 1u))))) &
      0x22) == 0x22) {
    encode_fault_action_kind('\x14','1');
  }
  select_current_fault_record(0x14);
  status = '\0';
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffb8ebu + (uint32_t)((int)puVar1) * 1u)))) != '\0' ||
      ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffb8eau + (uint32_t)((int)puVar1) * 1u)))) != '\0' ||
      ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffb8e9u + (uint32_t)((int)puVar1) * 1u)))) != '\0' || (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffb8e8u + (uint32_t)((int)puVar1) * 1u)))) != '\0'))) {
    status = '\x11';
  }
  set_diagnostic_cache_blocker('\x01',status);
  return;
}

void publish_acquisition_monitor_status(uchar index,uint packed_status)

{
  if (index < 4) {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe70e8u + (uint32_t)(index) * 1u)))) = (char)packed_status;
  }
  return;
}

void reset_scalar_monitor_3bc4c(void)

{
  reset_latched_monitor(((F33LatchedMonitorState *)camry_host_ptr((uint32_t)((0xfebe70ecu)))));
  return;
}

void reset_scalar_monitor_3bc4c_3bc3c(void)

{
  reset_latched_monitor(((F33LatchedMonitorState *)camry_host_ptr((uint32_t)((0xfebe70ecu)))));
  return;
}

void step_acquisition_range_a_monitor(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  if (DAT_0002bb40 == 'Z') {
    reset_latched_monitor(((F33LatchedMonitorState *)camry_host_ptr((uint32_t)((0xfebe70ecu)))));
  }
  else {
    step_latched_monitor
              (((F33LatchedMonitorState *)camry_host_ptr((uint32_t)((0xfebe70ecu)))), ((F33MonitorLimits *)camry_host_ptr((uint32_t)((0x2b5f0u)))), ((F33TwoSidedMonitorCallbacks *)camry_host_ptr((uint32_t)((0x28034u)))));
  }
  publish_acquisition_monitor_status('\x02',(*((uint *)camry_host_ptr((uint32_t)((0xffffb8ecu + (uint32_t)((int)puVar1)))))));
  return;
}

uint classify_acquisition_range_a(void)

{
  if (DAT_febe81d4 != 'Z') {
    return 0x44;
  }
  if ((DAT_0002b5f8 <= DAT_febe81d6) && (DAT_febe81d8 <= DAT_0002b5fa)) {
    return 0x11;
  }
  return 0x22;
}

void report_scalar_event_d6_healthy_observed(void)

{
  report_diagnostic_healthy_observed(0xd6);
  return;
}

void report_scalar_event_d6_failure(void)

{
  report_diagnostic_event_failure(0xd6,10);
  return;
}

void reset_scalar_monitor_3bcfc(void)

{
  reset_latched_monitor(((F33LatchedMonitorState *)camry_host_ptr((uint32_t)((0xfebe70f8u)))));
  return;
}

void reset_scalar_monitor_3bcfc_3bcec(void)

{
  reset_latched_monitor(((F33LatchedMonitorState *)camry_host_ptr((uint32_t)((0xfebe70f8u)))));
  return;
}

void step_acquisition_range_b_monitor(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  if (DAT_0002bb44 == 'Z') {
    reset_latched_monitor(((F33LatchedMonitorState *)camry_host_ptr((uint32_t)((0xfebe70f8u)))));
  }
  else {
    step_latched_monitor
              (((F33LatchedMonitorState *)camry_host_ptr((uint32_t)((0xfebe70f8u)))), ((F33MonitorLimits *)camry_host_ptr((uint32_t)((0x2b5f4u)))), ((F33TwoSidedMonitorCallbacks *)camry_host_ptr((uint32_t)((0x28068u)))));
  }
  publish_acquisition_monitor_status('\x03',(*((uint *)camry_host_ptr((uint32_t)((0xffffb8f8u + (uint32_t)((int)puVar1)))))));
  return;
}

uint classify_acquisition_range_b(void)

{
  if (DAT_febe81d5 != 'Z') {
    return 0x44;
  }
  if ((DAT_0002b5fc <= DAT_febe81da) && (DAT_febe81dc <= DAT_0002b5fe)) {
    return 0x11;
  }
  return 0x22;
}

void report_scalar_event_d7_healthy_observed(void)

{
  report_diagnostic_healthy_observed(0xd7);
  return;
}

void report_scalar_event_d7_failure(void)

{
  report_diagnostic_event_failure(0xd7,10);
  return;
}

void return_only_stub_3bd8c(void)

{
  return;
}

char increment_one_of_three_saturating_byte_counters_3bd8e(uint param_1)

{
  char cVar1;
  uint saved_mask;
  char cVar2;
  
  cVar2 = '\0';
  if ((param_1 & 0xff) < 3) {
    saved_mask = priority_mask_enter(0xffc0);
    cVar2 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe7104u + (uint32_t)(param_1 & 0xff) * 1u))));
    if (((int8_t)cVar2) != -1) {
      cVar1 = cVar2 + '\x01';
      cVar2 = cVar2 + '\x01';
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe7104u + (uint32_t)(param_1 & 0xff) * 1u)))) = cVar1;
    }
    priority_mask_restore(saved_mask);
  }
  return cVar2;
}

void publish_fault_qualification_limit(ushort classes)

{
  uint uVar1;
  uint32_t puVar2;
  uint uVar3;
  uint uVar4;
  
  puVar2 = 0xfebeb800u;
  uVar3 = 0x569a;
  if (classes != 0) {
    uVar1 = 0;
    uVar4 = uVar3;
    do {
      uVar3 = uVar4;
      if (((classes >> (uVar1 & 0x1f) & 1) != 0) &&
         (uVar3 = (uint)(*((volatile uint16_t *)camry_host_ptr((uint32_t)(0x317e0u + (uint32_t)(uVar1) * 2u)))), (int)(uVar4 - uVar3) < 0)) {
        uVar3 = uVar4;
      }
      uVar1 = uVar1 + 1;
      uVar4 = uVar3;
    } while (uVar1 < 0x10);
  }
  uVar1 = priority_mask_enter(0xffc0);
  publish_redundant_u16
            (classes,((ushort *)camry_host_ptr((uint32_t)((0xffffb9ecu + (uint32_t)((int)puVar2))))),((ushort *)camry_host_ptr((uint32_t)((0xffffb908u + (uint32_t)((int)puVar2)))))
             ,((ushort *)camry_host_ptr((uint32_t)((0xffffb90au + (uint32_t)((int)puVar2))))));
  (*((short *)camry_host_ptr((uint32_t)((0xffffb9f2u + (uint32_t)((int)puVar2)))))) = (short)uVar3;
  priority_mask_restore(uVar1);
  return;
}

void initialize_four_24_halfword_fault_arrays_3be22(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  
  iVar4 = 0;
  do {
    iVar3 = iVar4 * 2;
    *(undefined2 *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe710cu + (uint32_t)(iVar3) * 1u)))) = 0xffff;
    iVar2 = iVar4 + 1;
    *(undefined2 *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe713cu + (uint32_t)(iVar3) * 1u)))) = 0xffff;
    iVar1 = iVar4 + -0x17;
    *(undefined2 *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe716cu + (uint32_t)(iVar3) * 1u)))) = 0xffff;
    *(undefined2 *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe719cu + (uint32_t)(iVar3) * 1u)))) = 0xffff;
    iVar4 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  publish_fault_qualification_limit(0);
  return;
}

void clear_fault_qualification_and_request_counters_3be52(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  publish_fault_qualification_limit(0);
  (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffb9eeu + (uint32_t)((int)puVar1)))))) = 0;
  (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffbc40u + (uint32_t)((int)puVar1)))))) = 0;
  (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffbc42u + (uint32_t)((int)puVar1)))))) = 0;
  (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffbc44u + (uint32_t)((int)puVar1)))))) = 0;
  (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffbc46u + (uint32_t)((int)puVar1)))))) = 0;
  (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffbc48u + (uint32_t)((int)puVar1)))))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffb9e4u + (uint32_t)((int)puVar1) * 1u)))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffb9e5u + (uint32_t)((int)puVar1) * 1u)))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffb9e6u + (uint32_t)((int)puVar1) * 1u)))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffb9e7u + (uint32_t)((int)puVar1) * 1u)))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffb9e8u + (uint32_t)((int)puVar1) * 1u)))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffb9e9u + (uint32_t)((int)puVar1) * 1u)))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffb9eau + (uint32_t)((int)puVar1) * 1u)))) = 0;
  (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffb9f0u + (uint32_t)((int)puVar1)))))) = 0;
  return;
}

void classify_fault_qualification(uint classes)

{
  int iVar1;
  uint uVar2;
  uint uVar3;
  uint uVar4;
  uint uVar5;
  
  DAT_febe71ee = 0;
  if ((classes & 0xffff) != 0) {
    uVar3 = 0;
    uVar4 = 0;
    do {
      uVar5 = uVar4;
      if ((((classes & 0xffff) >> (uVar3 & 0x1f) & 1) != 0) && (uVar5 = 0x8000, uVar4 == 0)) {
        uVar5 = 1 << (uVar3 & 0x1f) & 0xffff;
      }
      DAT_febe71ee = (undefined2)uVar5;
      uVar2 = uVar3 + 1;
      iVar1 = uVar3 - 0xf;
      uVar3 = uVar2;
      uVar4 = uVar5;
    } while (iVar1 < 0 != ((int)uVar2 < 0 && -1 < iVar1));
  }
  return;
}

uint vote_fault_qualification(void)

{
  ushort uStack_6;
  
  read_xor_redundant_u16_with_vote_status_707ac(((undefined *)camry_host_ptr(0xfebe71ecu)),((undefined *)camry_host_ptr(0xfebe7108u)),((undefined *)camry_host_ptr(0xfebe710au)),&uStack_6);
  return (uint)uStack_6;
}

void update_fault_qualification(void)

{
  ushort uVar1;
  undefined1 uVar2;
  uint32_t puVar3;
  uint uVar4;
  uint uVar5;
  
  uVar1 = DAT_febe71ee;
  puVar3 = 0xfebeb800u;
  uVar5 = (uint)DAT_febe71ee;
  uVar4 = vote_fault_qualification();
  if ((DAT_000317da & uVar1) == 0) {
    if (uVar5 == 0) {
      uVar5 = uVar4;
      if ((uVar4 >> 0xf & 1) == 0) {
        uVar5 = uVar4 & 0xffffbfff;
      }
      goto LAB_0003bf1c;
    }
  }
  else {
    uVar5 = 0x8000;
  }
  if (((uVar5 & uVar4) == 0) && (uVar4 != 0)) {
    uVar5 = 0x8000;
  }
  uVar5 = uVar4 | uVar5;
LAB_0003bf1c:
  publish_fault_qualification_limit((ushort)uVar5);
  if ((uVar4 == 0) && (uVar5 != 0)) {
    uVar2 = 0x5a;
  }
  else {
    uVar2 = 0;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffb9e4u + (uint32_t)((int)puVar3) * 1u)))) = uVar2;
  return;
}

void maintain_qualified_fault_actions
               (ushort mode_actions,ushort status_actions,ushort output_actions)

{
  int iVar1;
  int iVar2;
  byte *pbVar3;
  ushort uVar4;
  ushort uVar5;
  ushort uVar6;
  ushort uVar7;
  ushort uVar8;
  int iVar9;
  
  uVar4 = DAT_febe71ec;
  if (DAT_febe71e4 == 'Z') {
    iVar9 = 0;
    do {
      if (((*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe7208u + (uint32_t)(iVar9 * 6) * 2u)))) & uVar4) != 0) {
        uVar5 = (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe7200u + (uint32_t)(iVar9 * 6) * 2u))));
        pbVar3 = ((byte *)camry_host_ptr((uint32_t)((int)0xfebe7204u + iVar9 * 0xc + 1)));
        *pbVar3 = *pbVar3 & 0xf7;
        pbVar3 = ((byte *)camry_host_ptr((uint32_t)((int)0xfebe7204u + iVar9 * 0xc + 1)));
        *pbVar3 = *pbVar3 & 0xfb;
        (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe7200u + (uint32_t)(iVar9 * 6) * 2u)))) = uVar5 & 0xffed;
        (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe7202u + (uint32_t)(iVar9 * 6) * 2u)))) = (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe7202u + (uint32_t)(iVar9 * 6) * 2u)))) & 0xff8f;
        *(ushort *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe713cu + (uint32_t)(iVar9 * 2) * 1u)))) = *(ushort *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe713cu + (uint32_t)(iVar9 * 2) * 1u)))) | 0x12;
      }
      iVar2 = iVar9 + 1;
      iVar1 = iVar9 + -0x17;
      iVar9 = iVar2;
    } while (((iVar1 < 0) || (iVar2 < 0)));
  }
  uVar8 = uVar4 & 0x8000;
  uVar5 = uVar8;
  uVar6 = uVar8;
  uVar7 = uVar8;
  if ((uVar4 & 0x8000) != 0) {
    uVar8 = DAT_febe7440 | mode_actions & 0x12;
    uVar5 = DAT_febe7446;
    uVar6 = DAT_febe7444 | output_actions & 0xc00;
    uVar7 = DAT_febe7442 | status_actions & 0x70;
  }
  DAT_febe7440 = uVar8;
  DAT_febe7442 = uVar7;
  DAT_febe7444 = uVar6;
  DAT_febe7446 = uVar5;
  return;
}

void qualify_fault_action_aggregate(ushort *actions)

{
  ushort mode_actions;
  ushort status_actions;
  ushort output_actions;
  ushort uVar1;
  
  mode_actions = *actions;
  status_actions = actions[1];
  output_actions = actions[2];
  uVar1 = actions[4];
  if (DAT_000317d4 == 'Z') {
    uVar1 = uVar1 | DAT_000317d8;
  }
  classify_fault_qualification((uint)uVar1);
  update_fault_qualification();
  maintain_qualified_fault_actions(mode_actions,status_actions,output_actions);
  return;
}
