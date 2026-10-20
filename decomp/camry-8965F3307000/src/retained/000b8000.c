#include "common.h"

uchar return_to_phase_seven_after_b405_completion_b8040(uchar phase)

{
  undefined1 uVar1;
  uint32_t puVar2;
  puVar2 = 0xfebeb800u;
  uVar1 = DAT_febeb3d3;
  if (DAT_febeb405 == 'Z') {
    puVar2 = 0xfebeb800u;
    clear_b404_ramp_enable_output_and_counters_b8886();
    fill_constant_block_b7c42();
    fill_constant_block_b7abe();
    uVar1 = 0x5a;
    phase = '\a';
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x42d))))) = uVar1;
  return phase;
}

uchar dispatch_service_phases_six_through_eight_b8070(uchar phase)

{
  if (5 < phase) {
    if (phase == '\x06') {
      fill_constant_block_b7c42();
      fill_constant_block_b7abe();
      phase = '\a';
    }
    else if (phase < 8) {
      phase = complete_phase_seven_or_start_phase_eight_ramp_b7ff4(phase);
    }
    else if (phase == '\b') {
      phase = return_to_phase_seven_after_b405_completion_b8040('\b');
    }
  }
  return phase;
}

uchar advance_service_excursion_phase(uchar phase)

{
  uchar uVar1;
  
  switch(phase) {
  case '\x01':
    uVar1 = advance_to_phase_two_after_b3d4_latch_b7dba(phase);
    break;
  case '\x02':
    uVar1 = advance_to_phase_three_after_stable_delta_b7e44(phase);
    break;
  case '\x03':
    uVar1 = advance_to_phase_four_after_minimum_excursion_b7eb2(phase);
    break;
  case '\x04':
    uVar1 = advance_to_phase_five_after_stable_delta_b7edc(phase);
    break;
  case '\x05':
    uVar1 = select_phase_six_or_nine_after_maximum_excursion_b7f8a(phase);
    break;
  default:
    uVar1 = dispatch_service_phases_six_through_eight_b8070(phase);
  }
  return uVar1;
}

void update_excursion_phase_and_snapshot_afe8_b80e2(void)

{
  undefined4 uVar1;
  uchar phase;
  uint32_t puVar2;
  uchar uVar3;
  uchar uVar4;
  
  phase = DAT_febeb3cc;
  uVar1 = DAT_febeafe8;
  puVar2 = 0xfebeb800u;
  uVar3 = qualify_service_progress(DAT_febeb3ca,DAT_febeb3dd);
  uVar4 = '\t';
  if (uVar3 != 'Z') {
    uVar4 = advance_service_excursion_phase(phase);
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x434))))) = uVar4;
  (*((undefined4 *)camry_host_ptr((uint32_t)(puVar2 + -0x414)))) = uVar1;
  return;
}

undefined1 advance_to_phase_ten_after_b3d4_latch_b8116(undefined1 param_1)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  if (DAT_febeb3d4 == 'Z') {
    puVar1 = 0xfebeb800u;
    fill_constant_block_b7c42();
    fill_constant_block_b7abe();
    param_1 = 10;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x42c))))) = 0x5a;
  return param_1;
}

undefined1 complete_phase_ten_after_small_b398_dwell_b813e(undefined1 param_1)

{
  uint32_t puVar1;
  int iVar2;
  
  puVar1 = 0xfebeb800u;
  iVar2 = debounce_b398_magnitude_with_halfword_counter_b7fb8(DAT_000af4b4,DAT_000af4a2);
  if (iVar2 == 0x5a) {
    fill_constant_block_b7ad2();
    fill_constant_block_b7c62();
    enable_ratio_mode_two_and_refresh_output_b7966();
    param_1 = 0xb;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x425))))) = 0x5a;
  }
  return param_1;
}

uint dispatch_service_phases_one_and_ten_b8176(uint param_1)

{
  param_1 = param_1 & 0xff;
  if (param_1 == 1) {
    param_1 = advance_to_phase_ten_after_b3d4_latch_b8116((uint)(byte)param_1);
  }
  else if (param_1 == 10) {
    param_1 = complete_phase_ten_after_small_b398_dwell_b813e((uint)(byte)param_1);
  }
  return param_1;
}

void update_centering_phase_or_clear_on_qualification_b8196(void)

{
  undefined1 uVar1;
  uint32_t puVar2;
  uchar uVar3;
  undefined1 uVar4;
  
  uVar1 = DAT_febeb3cc;
  puVar2 = 0xfebeb800u;
  uVar3 = qualify_service_progress(DAT_febeb3db,'\0');
  uVar4 = 0;
  if (uVar3 != 'Z') {
    uVar4 = dispatch_service_phases_one_and_ten_b8176(uVar1);
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x434))))) = uVar4;
  return;
}

undefined1 debounce_b054_lower_and_upper_thresholds_b81c0(void)

{
  uint8_t stack_record_1e[30];
  byte bVar1;
  byte bVar2;
  int iVar3;
  int iVar4;
  uint32_t puVar5;
  undefined1 uVar6;
  int iVar7;
  char cVar8;
  char cVar9;
  
  iVar3 = DAT_febeb3ec;
  bVar2 = DAT_febeb3da;
  bVar1 = DAT_febeb3d9;
  iVar4 = DAT_febeafe8;
  puVar5 = 0xfebeb800u;
  iVar7 = (int)((int)(int16_t)DAT_febeb054);
  store_saturated_signed16_absolute_d1178((int)((int)(int16_t)DAT_febeafdc),((int16_t *)(stack_record_1e)));
  store_saturated_signed32_absolute_d1194(iVar4 - iVar3,((int32_t *)((stack_record_1e + 2))));
  iVar3 = (int)DAT_000af4a0;
  iVar4 = (*((int16_t *)(stack_record_1e + 0))) - iVar3;
  if ((iVar4 < 0 != ((*((int16_t *)(stack_record_1e + 0))) < 0 != iVar3 < 0 && iVar3 < 0 == iVar4 < 0)) &&
     ((*((int32_t *)(stack_record_1e + 2))) - DAT_000af4b0 < 0 !=
      ((*((int32_t *)(stack_record_1e + 2))) < 0 != DAT_000af4b0 < 0 && DAT_000af4b0 < 0 == (*((int32_t *)(stack_record_1e + 2))) - DAT_000af4b0 < 0))) {
    iVar4 = (int)DAT_000af4a8;
    if (iVar4 - iVar7 < 0 == (iVar4 < 0 != iVar7 < 0 && iVar7 < 0 == iVar4 - iVar7 < 0) &&
        iVar4 != iVar7) {
      cVar8 = '\0';
      uVar6 = DAT_000af496 <= bVar1;
      if ((bool)uVar6) {
        cVar9 = '\0';
      }
      else {
        cVar9 = bVar1 + 1;
      }
      goto LAB_000b8244;
    }
    iVar4 = (int)DAT_000af4a6;
    if (iVar7 - iVar4 < 0 == (iVar7 < 0 != iVar4 < 0 && iVar4 < 0 == iVar7 - iVar4 < 0) &&
        iVar7 != iVar4) {
      cVar9 = '\0';
      if (bVar2 < DAT_000af496) {
        uVar6 = 0;
        cVar8 = bVar2 + 1;
      }
      else {
        cVar8 = '\0';
        uVar6 = 2;
      }
      goto LAB_000b8244;
    }
  }
  cVar9 = '\0';
  cVar8 = '\0';
  uVar6 = 0;
LAB_000b8244:
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x427))))) = cVar9;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x426))))) = cVar8;
  return uVar6;
}

undefined1 select_extremum_or_geometry_completion_phase_b8250(undefined1 param_1)

{
  char cVar1;
  char cVar2;
  uint uVar3;
  int iVar4;
  
  cVar2 = DAT_febeb3c9;
  cVar1 = DAT_febeb3c8;
  if ((DAT_febeb3c8 == 'Z') && (DAT_febeb3c9 == 'Z')) {
    uVar3 = queue_service_center_and_check_geometry();
    if (uVar3 == 0x5a) {
      param_1 = 0x10;
    }
    else {
      enable_ratio_mode_two_and_refresh_output_b7966();
      param_1 = 0xf;
    }
  }
  else {
    iVar4 = debounce_b054_lower_and_upper_thresholds_b81c0();
    if ((iVar4 == 1) && (cVar1 != 'Z')) {
      param_1 = 0xd;
    }
    else if ((iVar4 == 2) && (cVar2 != 'Z')) {
      param_1 = 0xe;
    }
  }
  return param_1;
}

undefined1 record_minimum_excursion_and_return_phase_twelve_b82a8(undefined1 param_1)

{
  uint32_t puVar1;
  uchar uVar2;
  
  puVar1 = 0xfebeb800u;
  uVar2 = update_service_minimum_excursion(DAT_000af496);
  if (uVar2 == 'Z') {
    param_1 = 0xc;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x428))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x428))))) | 1;
  }
  return param_1;
}

undefined1 record_maximum_excursion_and_return_phase_twelve_b82d6(undefined1 param_1)

{
  uint32_t puVar1;
  uchar uVar2;
  
  puVar1 = 0xfebeb800u;
  uVar2 = update_service_maximum_excursion(DAT_000af496);
  if (uVar2 == 'Z') {
    param_1 = 0xc;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x428))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x428))))) | 2;
  }
  return param_1;
}

undefined1 latch_b3d6_and_finish_phase_fifteen_after_dwell_b8304(undefined1 param_1)

{
  uint32_t puVar1;
  int iVar2;
  
  puVar1 = 0xfebeb800u;
  iVar2 = debounce_b398_magnitude_with_halfword_counter_b7fb8(DAT_000af4bc,DAT_000af4aa);
  if (iVar2 == 0x5a) {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x42a))))) = 0x5a;
    param_1 = 0x10;
  }
  return param_1;
}

uint dispatch_extremum_capture_phases_b832e(uint param_1)

{
  uint uVar1;
  
  param_1 = param_1 & 0xff;
  if (param_1 == 1) {
    uVar1 = 1;
    if (DAT_febeb3d4 == 'Z') {
      uVar1 = 0xc;
    }
    DAT_febeb3d4 = 0x5a;
    return uVar1;
  }
  if (0xb < param_1) {
    if (param_1 == 0xc) {
      uVar1 = select_extremum_or_geometry_completion_phase_b8250((uint)(byte)param_1);
      return uVar1;
    }
    if (param_1 < 0xe) {
      uVar1 = record_minimum_excursion_and_return_phase_twelve_b82a8((uint)(byte)param_1);
      return uVar1;
    }
    if (param_1 == 0xe) {
      uVar1 = record_maximum_excursion_and_return_phase_twelve_b82d6((uint)(byte)param_1);
      return uVar1;
    }
    if (param_1 == 0xf) {
      uVar1 = latch_b3d6_and_finish_phase_fifteen_after_dwell_b8304((uint)(byte)param_1);
      return uVar1;
    }
  }
  DAT_febeb3cb = 3;
  return param_1;
}

void update_extremum_phase_and_snapshot_afe8_b8384(void)

{
  undefined4 uVar1;
  undefined1 uVar2;
  uint32_t puVar3;
  uchar uVar4;
  undefined1 uVar5;
  
  uVar2 = DAT_febeb3cc;
  uVar1 = DAT_febeafe8;
  puVar3 = 0xfebeb800u;
  uVar4 = qualify_service_progress(DAT_febeb3d6,DAT_febeb3dc);
  uVar5 = 0x10;
  if (uVar4 != 'Z') {
    uVar5 = dispatch_extremum_capture_phases_b832e(uVar2);
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x434))))) = uVar5;
  (*((undefined4 *)camry_host_ptr((uint32_t)(puVar3 + -0x414)))) = uVar1;
  return;
}

void dispatch_service_update_by_b3d5_mode_b83ba(void)

{
  if (DAT_febeb3d5 != 0) {
    if (DAT_febeb3d5 == 1) {
      latch_timed_b3cf_ratio_invalidation_b7c82();
      latch_b054_magnitude_ratio_invalidation_b7cd0();
      update_excursion_phase_and_snapshot_afe8_b80e2();
    }
    else if (DAT_febeb3d5 < 3) {
      latch_timed_b3cf_ratio_invalidation_b7c82();
      latch_b054_magnitude_ratio_invalidation_b7cd0();
      update_centering_phase_or_clear_on_qualification_b8196();
    }
    else if (DAT_febeb3d5 == 3) {
      update_extremum_phase_and_snapshot_afe8_b8384();
    }
  }
  return;
}

void set_byte_febeb3d1_b83f2(undefined1 param_1)

{
  DAT_febeb3d1 = param_1;
  return;
}

void initialize_service_engine(uchar kind)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  DAT_febeb3cc = 1;
  if (kind == '\x02') {
    DAT_febeb3db = 0;
  }
  else {
    DAT_febeb3c9 = 0;
    DAT_febeb3c8 = 0;
    DAT_febeb3e4 = 0x7fffffff;
    DAT_febeb3f0 = 0;
    DAT_febeb3e8 = 0x80000001;
    if (kind == '\x01') {
      DAT_febeb3ca = 0;
      DAT_febeb3db = 0;
    }
    else {
      DAT_febeb3d6 = 0;
      DAT_febeb3d8 = 0;
    }
    puVar1 = 0xfebeb800u;
    write_nvm_106_word_with_zero_tail_b865e(0);
    clear_byte_febeb39c_b79fa();
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x435))))) = 1;
  (*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + -0x414)))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x433))))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x432))))) = 0;
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x422)))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x431))))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x430))))) = 0;
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x420)))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x42d))))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x42c))))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x427))))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x426))))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x42b))))) = kind;
  set_b1a7_latch_b42f0();
  set_output_request_word('\0',0);
  set_output_request_word('\x01',0);
  return;
}

undefined4 check_b054_magnitude_for_b3d2_mode_b8474(void)

{
  char cVar1;
  int iVar2;
  undefined4 uVar3;
  int iVar4;
  short sStack_a;
  
  cVar1 = DAT_febeb3d2;
  store_saturated_signed16_absolute_d1178((int)((int)(int16_t)DAT_febeb054),&sStack_a);
  if (cVar1 == '\0') {
    iVar2 = (int)DAT_000af4ac;
    iVar4 = (int)sStack_a;
    if (iVar4 - iVar2 < 0 == (iVar4 < 0 != iVar2 < 0 && iVar2 < 0 == iVar4 - iVar2 < 0) &&
        iVar4 != iVar2) goto LAB_000b849c;
LAB_000b84ac:
    uVar3 = 0x5a;
  }
  else {
LAB_000b849c:
    if (cVar1 == 'Z') {
      iVar2 = (int)DAT_000af4ae;
      iVar4 = (int)sStack_a;
      if (iVar4 - iVar2 < 0 != (iVar4 < 0 != iVar2 < 0 && iVar2 < 0 == iVar4 - iVar2 < 0) ||
          iVar4 == iVar2) goto LAB_000b84ac;
    }
    uVar3 = 0;
  }
  return uVar3;
}

void stop_service_phase_and_reset_output_requests_b856a(void)

{
  char cVar1;
  
  cVar1 = DAT_febeb1a4;
  DAT_febeb3cc = 0;
  DAT_febeb3d5 = 0;
  reset_b3fc_status_and_two_halfword_counters_b87d2();
  if (cVar1 == '\0') {
    set_output_request_word('\0',0x70017001);
    set_output_request_word('\x01',0x70017001);
    clear_b1a7_latch_b42fa();
  }
  return;
}

void set_service_qualification_mode(uchar mode)

{
  DAT_febeb3d2 = mode;
  return;
}

void set_byte_febeb3d7_b85a8(undefined1 param_1)

{
  DAT_febeb3d7 = param_1;
  return;
}

void set_b3dc_ready_and_clear_b3cb_b85ae(void)

{
  DAT_febeb3dc = 0x5a;
  DAT_febeb3cb = 0;
  return;
}

void set_b3dd_ready_and_clear_b3cb_b85bc(void)

{
  DAT_febeb3dd = 0x5a;
  DAT_febeb3cb = 0;
  return;
}

void clear_byte_febeb3dc_b85ca(void)

{
  DAT_febeb3dc = 0;
  return;
}

void clear_byte_febeb3dd_b85d0(void)

{
  DAT_febeb3dd = 0;
  return;
}

void return_only_stub_b85d6(void)

{
  return;
}

int load_nvm_106_word_and_publish_read_status_b85d8(void)

{
  undefined1 uVar1;
  uint32_t puVar2;
  int iVar3;
  undefined4 uVar4;
  undefined4 local_10 [2];
  
  puVar2 = 0xfebeb800u;
  iVar3 = call_nvm_get_record_with_u16_selector_ff0b0(0x106,local_10);
  if (iVar3 == 0x10) {
    report_diagnostic_healthy_observed(0x17d);
    uVar1 = 1;
    uVar4 = local_10[0];
  }
  else {
    uVar4 = 0;
    if (iVar3 == 0x11) {
      uVar1 = 2;
    }
    else {
      if (((DAT_febe82d4 != '\x01') && (DAT_febe82d4 != '\x02')) &&
         ((DAT_febe82d4 != '\x04' && (DAT_febe82d4 != '\x06')))) {
        iVar3 = (int)(get_diagnostic_event_state(0x17d) >> 1);
      }
      report_diagnostic_event_failure(0x17d,0x32);
      uVar1 = 3;
    }
  }
  (*((undefined4 *)camry_host_ptr((uint32_t)(puVar2 + -0x408)))) = uVar4;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x40c))))) = uVar1;
  return iVar3;
}

void poll_nvm_106_write_completion_b8622(void)

{
  uint32_t puVar1;
  uint uVar2;
  char cVar3;
  
  cVar3 = DAT_febeb3f4;
  puVar1 = (0xfebeb800u);
  if (((DAT_febeb3f4 == '\x05') &&
      (puVar1 = (0xfebeb800u), uVar2 = call_nvm_record_status_with_u16_selector_ff0c4(0x106), (uVar2 & 0xf0) != 0x20)) &&
     (cVar3 = '\x01', uVar2 != 0x10)) {
    cVar3 = '\x04';
    report_diagnostic_event_failure(0x17e,0x32);
  }
  (*((volatile undefined *)camry_host_ptr((uint32_t)(0xfebeb800u + (uint32_t)(-0x40c) * 1u)))) = cVar3;
  return;
}

void write_nvm_106_word_with_zero_tail_b865e(undefined4 param_1)

{
  uint8_t stack_record_c[12];
  uint32_t puVar1;
  
  puVar1 = 0xfebeb800u;
  (*((uint32_t *)(stack_record_c + 4))) = 0;
  DAT_febeb3f8 = param_1;
  (*((uint32_t *)(stack_record_c + 0))) = param_1;
  call_nvm_set_record_with_u16_selector_ff09c(0x106,stack_record_c);
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x40c))))) = 5;
  return;
}

void return_only_stub_b8680(void)

{
  return;
}

void clear_b3fc_status_and_two_halfword_counters_b8682(void)

{
  DAT_febeb3fc = 0;
  DAT_febeb3fe = 0;
  DAT_febeb400 = 0;
  DAT_febeb3fd = 0;
  return;
}

uint select_service_kind1_sample(short *sample)

{
  short sVar1;
  uint uVar2;
  
  switch(DAT_febeb3cc) {
  case 2:
  case 4:
    uVar2 = 0x5a;
    sVar1 = ((int)(int16_t)DAT_febeb436);
    break;
  case 3:
    uVar2 = 0x5a;
    sVar1 = DAT_000af4c0;
    break;
  case 5:
    uVar2 = 0x5a;
    sVar1 = DAT_000af4c2;
    break;
  default:
    uVar2 = 0;
    sVar1 = 0;
    break;
  case 7:
    uVar2 = 0x5a;
    sVar1 = ((int)(int16_t)DAT_febeb3a6);
    break;
  case 8:
    uVar2 = 0x5a;
    sVar1 = ((int)(int16_t)DAT_febeb406);
  }
  *sample = sVar1;
  return uVar2;
}

uint select_service_kind2_sample(short *sample)

{
  short sVar1;
  uint uVar2;
  
  if (DAT_febeb3cc == '\n') {
    uVar2 = 0x5a;
    sVar1 = ((int)(int16_t)DAT_febeb3a6);
  }
  else {
    uVar2 = 0;
    sVar1 = 0;
  }
  *sample = sVar1;
  return uVar2;
}

uint select_service_kind3_sample(short *sample)

{
  short sVar1;
  uint uVar2;
  
  switch(DAT_febeb3cc) {
  case 0xc:
  case 0xf:
    uVar2 = 0x5a;
    sVar1 = ((int)(int16_t)DAT_febeac56);
    break;
  case 0xd:
    uVar2 = 0x5a;
    sVar1 = DAT_000af4c4;
    break;
  case 0xe:
    uVar2 = 0x5a;
    sVar1 = DAT_000af4c6;
    break;
  default:
    uVar2 = 0;
    sVar1 = 0;
  }
  *sample = sVar1;
  return uVar2;
}

uint minimum_ten_halfwords_except_index_five_when_ready_b8742(char param_1)

{
  uint uVar1;
  uint uVar2;
  
  if (param_1 != 'Z') {
    return 0;
  }
  uVar2 = 0x569a;
  uVar1 = 0;
  do {
    if ((int)((ushort)(*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebebd34u + (uint32_t)(uVar1) * 2u)))) - uVar2) < 0) {
      uVar2 = (uint)(ushort)(*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebebd34u + (uint32_t)(uVar1) * 2u))));
    }
    do {
      uVar1 = uVar1 + 1 & 0xff;
      if (9 < uVar1) {
        return uVar2;
      }
    } while (uVar1 == 5);
  } while( true );
}

undefined2 publish_service_engine_substitution(void)

{
  uint32_t puVar1;
  undefined2 uVar2;
  undefined1 uVar3;
  char cVar4;
  undefined2 local_e;
  
  puVar1 = 0xfebeb800u;
  if (DAT_febeb3d5 == 0) {
LAB_000b8792:
    local_e = 0;
    cVar4 = '\0';
  }
  else {
    local_e = DAT_febeb3a6;
    if (DAT_febeb3d5 == 1) {
      switch(DAT_febeb3cc) {
      case '\x02':
      case '\x04':
        cVar4 = 'Z';
        local_e = DAT_febeb436;
        break;
      case '\x03':
        cVar4 = 'Z';
        local_e = DAT_000af4c0;
        break;
      case '\x05':
        cVar4 = 'Z';
        local_e = DAT_000af4c2;
        break;
      default:
        cVar4 = '\0';
        local_e = 0;
        break;
      case '\a':
        cVar4 = 'Z';
        break;
      case '\b':
        cVar4 = 'Z';
        local_e = DAT_febeb406;
      }
    }
    else {
      if (2 < DAT_febeb3d5) {
        if (DAT_febeb3d5 == 3) {
          switch(DAT_febeb3cc) {
          case '\f':
          case '\x0f':
            cVar4 = 'Z';
            local_e = DAT_febeac56;
            break;
          case '\r':
            cVar4 = 'Z';
            local_e = DAT_000af4c4;
            break;
          case '\x0e':
            cVar4 = 'Z';
            local_e = DAT_000af4c6;
            break;
          default:
            cVar4 = '\0';
            local_e = 0;
          }
          if (cVar4 == 'Z') {
            uVar3 = 0x5a;
          }
          else {
            uVar3 = 0;
          }
          goto LAB_000b87b8;
        }
        goto LAB_000b8792;
      }
      if (DAT_febeb3cc == '\n') {
        cVar4 = 'Z';
      }
      else {
        cVar4 = '\0';
        local_e = 0;
      }
    }
  }
  uVar3 = 0;
LAB_000b87b8:
  uVar2 = minimum_ten_halfwords_except_index_five_when_ready_b8742(cVar4);
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x400)))) = uVar2;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x404))))) = cVar4;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x403))))) = uVar3;
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x402)))) = local_e;
  return uVar2;
}

void reset_b3fc_status_and_two_halfword_counters_b87d2(void)

{
  DAT_febeb3fc = 0;
  DAT_febeb3fe = 0;
  DAT_febeb400 = 0;
  DAT_febeb3fd = 0;
  return;
}

void return_only_stub_b87e0(void)

{
  return;
}

void fill_constant_block_b87e2(void)

{
  DAT_febeb406 = 0;
  DAT_febeb408 = 0;
  DAT_febeb40a = 0;
  DAT_febeb404 = 0;
  DAT_febeb405 = 0;
  return;
}

void advance_step_table_ramp_and_debounce_zero_completion_b87f2(void)

{
  int iVar1;
  uint32_t puVar2;
  char cVar3;
  ushort uVar4;
  short sVar5;
  short sStack_12;
  
  uVar4 = DAT_febeb40a;
  sVar5 = DAT_febeb408;
  cVar3 = DAT_febeb405;
  puVar2 = 0xfebeb800u;
  if (DAT_febeb405 == '\0') {
    puVar2 = 0xfebeb800u;
    lookup_unsigned16_step_table_to_output_d22c0(((undefined *)camry_host_ptr(0xaf4ccu)),DAT_febeb408,&sStack_12);
    iVar1 = (int)((uint)DAT_000af4ca * (int)sStack_12) / 0x4000;
    if (sVar5 != -1) {
      sVar5 = sVar5 + 1;
    }
    if (iVar1 == 0) {
      if (uVar4 < DAT_000af4c8) {
        uVar4 = uVar4 + 1;
      }
      else {
        cVar3 = 'Z';
      }
    }
  }
  else {
    iVar1 = 0;
  }
  (*((short *)camry_host_ptr((uint32_t)(puVar2 + -0x3fa)))) = (short)iVar1;
  (*((short *)camry_host_ptr((uint32_t)(puVar2 + -0x3f8)))) = sVar5;
  (*((ushort *)camry_host_ptr((uint32_t)(puVar2 + -0x3f6)))) = uVar4;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x3fb))))) = cVar3;
  return;
}

void advance_table_ramp_when_b404_ready_b885c(void)

{
  if (DAT_febeb404 == 'Z') {
    advance_step_table_ramp_and_debounce_zero_completion_b87f2();
  }
  return;
}

void fill_constant_block_b8872(void)

{
  DAT_febeb406 = 0;
  DAT_febeb408 = 0;
  DAT_febeb40a = 0;
  DAT_febeb405 = 0;
  DAT_febeb404 = 0x5a;
  return;
}

void clear_b404_ramp_enable_output_and_counters_b8886(void)

{
  DAT_febeb404 = 0;
  DAT_febeb406 = 0;
  DAT_febeb408 = 0;
  DAT_febeb40a = 0;
  return;
}

void return_only_stub_b8894(void)

{
  return;
}

void fill_constant_block_b8896(void)

{
  DAT_febeb40c = 0;
  DAT_febeb41c = 0;
  DAT_febeb420 = 0;
  DAT_febeb40e = 0;
  DAT_febeb424 = 0;
  DAT_febeb416 = 0;
  DAT_febeb410 = 0;
  DAT_febeb428 = 0;
  DAT_febeb412 = 0;
  DAT_febeb414 = 0;
  DAT_febeb42c = 0;
  return;
}

int compute_phase_signed_filtered_pi_with_feedforward_b88b2(int param_1,int param_2)

{
  uint8_t stack_record_2c[44];
  char cVar1;
  short sVar2;
  int iVar3;
  int iVar4;
  uint32_t puVar5;
  int iVar6;
  int iVar7;
  
  sVar2 = ((int)(int16_t)DAT_febeb40e);
  puVar5 = 0xfebeb800u;
  iVar4 = -param_2;
  if ((DAT_febeb3cc == '\x02') || (DAT_febeb41c = 0, iVar4 = param_2, DAT_febeb3cc == '\x04')) {
    DAT_febeb41c = iVar4 - param_1;
  }
  iVar6 = (int)((int)(int16_t)DAT_febeb40e);
  iVar4 = (DAT_febeb41c - DAT_febeb424) + DAT_febeb420;
  iVar3 = (int)DAT_000af54c;
  iVar7 = iVar4;
  if (iVar3 != 0) {
    if (iVar4 == -0x80000000 && iVar3 == -1) {
      iVar7 = -0x80000000;
    }
    else {
      iVar7 = (int)iVar4 / (int)iVar3;
    }
  }
  store_signed32_clamped_between_upper_and_lower_d1cf6(iVar7,0x7fff,(int)0xffff8001,((int32_t *)(stack_record_2c)));
  (*((int32_t *)(stack_record_2c + 8))) = (*((int *)camry_host_ptr((uint32_t)(puVar5 + -0x3d8))));
  (*((short *)camry_host_ptr((uint32_t)(puVar5 + -0x3ea)))) = sVar2;
  (*((int *)camry_host_ptr((uint32_t)(puVar5 + -0x3e0)))) = iVar4;
  (*((short *)camry_host_ptr((uint32_t)(puVar5 + -0x3f2)))) = (short)(*((int32_t *)(stack_record_2c + 0)));
  iVar4 = (int)DAT_000af54e;
  (*((int *)camry_host_ptr((uint32_t)(puVar5 + -0x3dc)))) = iVar7;
  cVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x7fc)))));
  (*((int32_t *)(stack_record_2c + 4))) = ((iVar6 + (*((int32_t *)(stack_record_2c + 0)))) * iVar4) / 0x80;
  store_signed32_clamped_between_upper_and_lower_d1cf6((*((int32_t *)(stack_record_2c + 4))),0x7fff,(int)0xffff8001,((int32_t *)((stack_record_2c + 4))));
  if (((cVar1 != '\x02') || ((*((int32_t *)(stack_record_2c + 4))) < 0)) && ((cVar1 != '\x01' || (-1 < (*((int32_t *)(stack_record_2c + 4))))))) {
    (*((int32_t *)(stack_record_2c + 8))) = (*((int32_t *)(stack_record_2c + 8))) + (*((int32_t *)(stack_record_2c + 4)));
  }
  store_signed32_clamped_between_upper_and_lower_d1cf6((*((int32_t *)(stack_record_2c + 8))),PTR_LAB_000af554,-(int)PTR_LAB_000af554,((int32_t *)((stack_record_2c + 8))));
  (*((short *)camry_host_ptr((uint32_t)(puVar5 + -0x3f0)))) = (short)(*((int32_t *)(stack_record_2c + 4)));
  (*((int *)camry_host_ptr((uint32_t)(puVar5 + -0x3d8)))) = (*((int32_t *)(stack_record_2c + 8)));
  (*((int32_t *)(stack_record_2c + 12))) = (*((int32_t *)(stack_record_2c + 0))) * DAT_000af550;
  store_signed32_clamped_between_upper_and_lower_d1cf6((*((int32_t *)(stack_record_2c + 12))),0x7fff,(int)0xffff8001,((int32_t *)((stack_record_2c + 12))));
  (*((short *)camry_host_ptr((uint32_t)(puVar5 + -0x3ee)))) = (short)(*((int32_t *)(stack_record_2c + 12)));
  (*((int32_t *)(stack_record_2c + 16))) = (param_2 * DAT_000af552) / 0x80;
  store_signed32_clamped_between_upper_and_lower_d1cf6((*((int32_t *)(stack_record_2c + 16))),0x7fff,(int)0xffff8001,((int32_t *)((stack_record_2c + 16))));
  (*((short *)camry_host_ptr((uint32_t)(puVar5 + -0x3ec)))) = (short)(*((int32_t *)(stack_record_2c + 16)));
  return (*((int32_t *)(stack_record_2c + 8))) + (*((int32_t *)(stack_record_2c + 12))) + (*((int32_t *)(stack_record_2c + 16)));
}

void update_b42c_pi_sum_when_b40c_ready_b89e0(void)

{
  uint32_t puVar1;
  undefined4 uVar2;
  
  puVar1 = 0xfebeb800u;
  if (DAT_febeb40c == 'Z') {
    uVar2 = compute_phase_signed_filtered_pi_with_feedforward_b88b2((((int)(int16_t)DAT_febeb032) * 10) / 8,(uint)DAT_febeb418 * 10);
    (*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + -0x3d4)))) = uVar2;
  }
  return;
}

void fill_constant_block_b8a10(void)

{
  DAT_febeb41c = 0;
  DAT_febeb420 = 0;
  DAT_febeb40e = 0;
  DAT_febeb424 = 0;
  DAT_febeb416 = 0;
  DAT_febeb410 = 0;
  DAT_febeb428 = 0;
  DAT_febeb412 = 0;
  DAT_febeb414 = 0;
  DAT_febeb42c = 0;
  DAT_febeb40c = 0x5a;
  return;
}

void fill_constant_block_b8a30(void)

{
  DAT_febeb40c = 0;
  DAT_febeb41c = 0;
  DAT_febeb420 = 0;
  DAT_febeb40e = 0;
  DAT_febeb424 = 0;
  DAT_febeb416 = 0;
  DAT_febeb410 = 0;
  DAT_febeb428 = 0;
  DAT_febeb412 = 0;
  DAT_febeb414 = 0;
  DAT_febeb42c = 0;
  return;
}

void set_service_numeric_target(ushort target)

{
  DAT_febeb418 = target;
  return;
}

void return_only_stub_b8a52(void)

{
  return;
}

void fill_constant_block_b8a54(void)

{
  DAT_febeb431 = 0;
  DAT_febeb432 = 0;
  DAT_febeb434 = 0;
  DAT_febeb436 = 0;
  DAT_febeb430 = 0;
  return;
}

void add_clamped_ac70_correction_to_b42c_b8a64(void)

{
  uint8_t stack_record_14[20];
  bool bVar1;
  int iVar2;
  undefined1 uVar3;
  int iVar4;
  uint32_t puVar5;
  short sVar6;
  int iVar7;
  
  iVar2 = DAT_febeb42c;
  puVar5 = 0xfebeb800u;
  (*((int32_t *)(stack_record_14 + 0))) = (((int)(int16_t)DAT_febeac70) * 10) / 8;
  store_signed32_clamped_between_upper_and_lower_d1cf6((*((int32_t *)(stack_record_14 + 0))),(int)DAT_000af55c,-(int)DAT_000af55c,((int32_t *)(stack_record_14)));
  iVar4 = (int)DAT_000af558;
  (*((short *)camry_host_ptr((uint32_t)(puVar5 + -0x3ce)))) = (short)(*((int32_t *)(stack_record_14 + 0)));
  (*((int32_t *)(stack_record_14 + 4))) = -((*((int32_t *)(stack_record_14 + 0))) * iVar4) / 0x40;
  store_signed32_clamped_between_upper_and_lower_d1cf6((*((int32_t *)(stack_record_14 + 4))),0x7fff,(int)0xffff8001,((int32_t *)((stack_record_14 + 4))));
  sVar6 = DAT_000af55a;
  iVar4 = (int)DAT_000af55a;
  (*((short *)camry_host_ptr((uint32_t)(puVar5 + -0x3cc)))) = (short)(*((int32_t *)(stack_record_14 + 4)));
  iVar2 = iVar2 + (*((int32_t *)(stack_record_14 + 4)));
  if (iVar2 - iVar4 < 0 == (iVar2 < 0 != iVar4 < 0 && iVar4 < 0 == iVar2 - iVar4 < 0) &&
      iVar2 != iVar4) {
    uVar3 = 2;
  }
  else {
    iVar7 = -iVar4;
    iVar4 = iVar2 + iVar4;
    bVar1 = iVar2 < 0 != iVar7 < 0 && iVar7 < 0 == iVar4 < 0;
    if (iVar4 < 0 == bVar1) {
      iVar7 = iVar2;
    }
    sVar6 = (short)iVar7;
    uVar3 = iVar4 < 0 != bVar1;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x3d0))))) = uVar3;
  (*((short *)camry_host_ptr((uint32_t)(puVar5 + -0x3ca)))) = sVar6;
  return;
}

void refresh_b42c_correction_when_b431_and_ed00_ready_b8af0(void)

{
  if ((DAT_febeb431 == 'Z') && (DAT_febeed00 == 'Z')) {
    add_clamped_ac70_correction_to_b42c_b8a64();
  }
  return;
}

void fill_constant_block_b8b10(void)

{
  DAT_febeb432 = 0;
  DAT_febeb434 = 0;
  DAT_febeb436 = 0;
  DAT_febeb430 = 0;
  DAT_febeb431 = 0x5a;
  return;
}

void fill_constant_block_b8b24(void)

{
  DAT_febeb431 = 0;
  DAT_febeb432 = 0;
  DAT_febeb434 = 0;
  DAT_febeb436 = 0;
  DAT_febeb430 = 0;
  return;
}

void return_only_stub_b8b34(void)

{
  return;
}

void return_only_stub_b8b36(void)

{
  return;
}

void monitor_routine_1007_lifecycle_group(void)

{
  ushort uVar1;
  
  uVar1 = DAT_febeb440;
  if (DAT_febeb438 == '\x11') {
    if (((((int)(uint)DAT_febeb2d4 >> 8 == 0x88) && ((int)(uint)DAT_febeb26c >> 8 == 0x88)) &&
        ((int)(uint)DAT_febeb324 >> 8 == 0x88)) &&
       (((int)(uint)DAT_febeb490 >> 8 == 0x88 && ((int)(uint)DAT_febeb352 >> 8 == 0x88)))) {
      if (((((DAT_febeb2d4 & 0xff) == 0x22) && ((DAT_febeb26c & 0xff) == 0x22)) &&
          ((DAT_febeb324 & 0xff) == 0x22)) &&
         (((DAT_febeb490 & 0xff) == 0x22 && ((DAT_febeb352 & 0xff) == 0x22)))) {
        thunk_publish_routine_or_pending_write_terminal_result_4d0a4(4,0);
        DAT_febeb438 = '\"';
        DAT_febeb43c = 0;
      }
      else {
        thunk_publish_routine_or_pending_write_terminal_result_4d0a4(4,0x20);
        DAT_febeb438 = 'D';
        DAT_febeb43c = 0;
      }
    }
    else if ((DAT_febeb440 < DAT_000aed64) && ((DAT_febeb20e != '\x11' && (DAT_febeb20e != '3')))) {
      uVar1 = DAT_febeb440 + 1;
    }
    else {
      DAT_febeb43c = 0x5a;
      uVar1 = DAT_000aed64;
    }
  }
  else {
    DAT_febeb43c = 0;
  }
  DAT_febeb440 = uVar1;
  return;
}

void monitor_four_88xx_statuses_and_b439_timeout_b8c16(void)

{
  if (DAT_febeb439 == '\x11') {
    if (((((int)(uint)DAT_febeb26c >> 8 == 0x88) && ((int)(uint)DAT_febeb324 >> 8 == 0x88)) &&
        ((int)(uint)DAT_febeb490 >> 8 == 0x88)) && ((int)(uint)DAT_febeb352 >> 8 == 0x88)) {
      DAT_febeb43b = 0;
      DAT_febeb439 = (char)DAT_febeb352;
      if ((((DAT_febeb26c & 0xff) != 0x22) || ((DAT_febeb324 & 0xff) != 0x22)) ||
         (((DAT_febeb490 & 0xff) != 0x22 || ((DAT_febeb352 & 0xff) != 0x22)))) {
        DAT_febeb439 = 'D';
      }
    }
    else if (((DAT_febeb43e < DAT_000aed64) && (DAT_febeb20e != '\x11')) && (DAT_febeb20e != '3')) {
      DAT_febeb43e = DAT_febeb43e + 1;
    }
    else {
      DAT_febeb43b = 0x5a;
      DAT_febeb43e = DAT_000aed64;
    }
  }
  else {
    DAT_febeb43b = 0;
  }
  return;
}

void update_routine_1007_group_and_four_status_monitor_b8cbe(void)

{
  monitor_routine_1007_lifecycle_group();
  monitor_four_88xx_statuses_and_b439_timeout_b8c16();
  return;
}

void monitor_routine_1008_lifecycle_group(void)

{
  ushort uVar1;
  
  uVar1 = DAT_febeb442;
  if (DAT_febeb43a == '\x11') {
    if ((((DAT_febeb2ce == '\x11') || (DAT_febeb25c == '\x11')) || (DAT_febeb302 == '\x11')) ||
       ((DAT_febeb462 == '\x11' || (DAT_febeb334 == '\x11')))) {
      if ((DAT_febeb442 < (ushort)PTR_LAB_000aed66) &&
         ((DAT_febeb20e != '\x11' && (DAT_febeb20e != '3')))) {
        uVar1 = DAT_febeb442 + 1;
      }
      else {
        DAT_febeb43d = 0x5a;
        uVar1 = (ushort)PTR_LAB_000aed66;
      }
    }
    else if ((((DAT_febeb2ce == '\"') && (DAT_febeb25c == '\"')) && (DAT_febeb302 == '\"')) &&
            ((DAT_febeb462 == '\"' && (DAT_febeb334 == '\"')))) {
      thunk_publish_routine_or_pending_write_terminal_result_4d0a4(5,0);
      DAT_febeb43a = '\"';
      DAT_febeb43d = 0;
    }
    else {
      thunk_publish_routine_or_pending_write_terminal_result_4d0a4(5,0x20);
      DAT_febeb43a = 'D';
      DAT_febeb43d = 0;
    }
  }
  else {
    DAT_febeb43d = 0;
  }
  DAT_febeb442 = uVar1;
  return;
}

void update_routine_1007_and_1008_lifecycle_groups_b8d8c(void)

{
  update_routine_1007_group_and_four_status_monitor_b8cbe();
  monitor_routine_1008_lifecycle_group();
  return;
}

undefined4 check_selected_pair_of_lifecycle_states_idle_b8d9c(char param_1)

{
  char cVar1;
  char cVar2;
  
  cVar1 = DAT_febeb43a;
  cVar2 = DAT_febeb439;
  if ((((param_1 == '\0') || (cVar2 = DAT_febeb438, param_1 == '\x01')) ||
      (cVar1 = DAT_febeb439, param_1 == '\x02')) && ((cVar2 != '\x11' && (cVar1 != '\x11')))) {
    return 0x5a;
  }
  return 0;
}

void start_selected_b438_or_b439_lifecycle_group_b8dda(char param_1)

{
  undefined2 uVar1;
  undefined2 uVar2;
  char cVar3;
  char cVar4;
  
  uVar2 = DAT_febeb440;
  uVar1 = DAT_febeb43e;
  cVar3 = DAT_febeb439;
  cVar4 = DAT_febeb438;
  if (param_1 == '\0') {
    if (DAT_febeb438 != '\x11') {
      start_record_103_channel_capture_b6944();
      if (cVar3 != '\x11') {
        initialize_b26c_status_and_b25d_mask_b5eda();
        start_b324_record_102_capture_b726c();
        initialize_b490_8822_and_clear_b48c_b48d_b8fd0();
        fill_constant_block_b7358();
      }
      cVar4 = '\x11';
      uVar2 = 0;
    }
  }
  else if ((param_1 == '\x01') && (DAT_febeb439 != '\x11')) {
    if (DAT_febeb438 != '\x11') {
      initialize_b26c_status_and_b25d_mask_b5eda();
      start_b324_record_102_capture_b726c();
      initialize_b490_8822_and_clear_b48c_b48d_b8fd0();
      fill_constant_block_b7358();
    }
    cVar3 = '\x11';
    uVar1 = 0;
  }
  DAT_febeb438 = cVar4;
  DAT_febeb439 = cVar3;
  DAT_febeb440 = uVar2;
  DAT_febeb43e = uVar1;
  return;
}

void start_b43a_lifecycle_group_and_clear_counter_b8e52(void)

{
  undefined2 uVar1;
  uint32_t puVar2;
  puVar2 = 0xfebeb800u;
  uVar1 = DAT_febeb442;
  if (DAT_febeb43a != '\x11') {
    puVar2 = 0xfebeb800u;
    start_or_bypass_record_103_comparison_b69de();
    finish_b25c_mode_and_clear_mismatch_b5f00();
    start_event_100_monitor_b6be6();
    initialize_b461_mode_and_b462_status_b8ef0();
    reset_b333_b335_workflow_state_b72ec();
    uVar1 = 0;
  }
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar2 + -0x3be)))) = uVar1;
  DAT_febeb43a = 0x11;
  return;
}

void return_only_stub_b8e8c(void)

{
  return;
}

void set_b446_and_b44c_to_one_b8e8e(void)

{
  DAT_febeb446 = 1;
  DAT_febeb44c = 1;
  return;
}

void initialize_two_states_and_snapshot_f07b_f02f_b8e9a(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  set_b446_and_b44c_to_one_b8e8e();
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x3bc))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x387b)))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x3b6))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x382f)))));
  return;
}

void thunk_set_b446_and_b44c_to_one_b8e8e(void)

{
  set_b446_and_b44c_to_one_b8e8e();
  return;
}

void clear_byte_febeb462_b8ec2(void)

{
  DAT_febeb462 = 0;
  return;
}

void return_only_stub_b8ec8(void)

{
  return;
}

void fill_constant_block_b8eca(void)

{
  DAT_febeb45f = 0x11;
  DAT_febeb461 = 2;
  DAT_febeb45c = 0;
  DAT_febeb45d = 0;
  DAT_febeb45e = 0;
  DAT_febeb460 = 0;
  return;
}

void initialize_b461_mode_and_b462_status_b8ef0(void)

{
  DAT_febeb461 = 2;
  DAT_febeb45c = 0;
  DAT_febeb462 = 0x22;
  return;
}

void return_only_stub_b8f3a(void)

{
  return;
}

void fill_constant_block_b8f16(void)

{
  DAT_febeb46c = 0x55aaaa55;
  DAT_febeb467 = 0;
  DAT_febeb464 = 0;
  DAT_febeb465 = 0;
  DAT_febeb466 = 0;
  DAT_febeb468 = 0;
  return;
}

void seed_two_55aaaa55_words_and_report_299_healthy_b8f4a(void)

{
  DAT_febeb474 = 0x55aaaa55;
  DAT_febeb478 = 0x55aaaa55;
  report_diagnostic_healthy_observed(299);
  return;
}

void seed_health_words_and_pass_events_20_120_b8f74(void)

{
  seed_two_55aaaa55_words_and_report_299_healthy_b8f4a();
  report_diagnostic_event_pass(0x20);
  report_diagnostic_event_pass(0x120);
  return;
}

void thunk_seed_two_55aaaa55_words_and_report_299_healthy_b8f4a(void)

{
  seed_two_55aaaa55_words_and_report_299_healthy_b8f4a();
  return;
}

void set_byte_b471_to_44_b8fa8(void)

{
  DAT_febeb471 = 0x44;
  return;
}

uint stage_encoded_mode_pair(uint first,uint second)

{
  DAT_febeb472 = 0x44;
  DAT_febeb480 = first;
  DAT_febeb484 = second;
  return 0;
}

void clear_halfword_febeb490_b8fc6(void)

{
  DAT_febeb490 = 0;
  return;
}

void return_only_stub_b8fcc(void)

{
  return;
}

void return_only_stub_b8fce(void)

{
  return;
}

void initialize_b490_8822_and_clear_b48c_b48d_b8fd0(void)

{
  DAT_febeb490 = 0x8822;
  DAT_febeb48c = 0;
  DAT_febeb48d = 0;
  return;
}

void return_only_stub_b8fe0(void)

{
  return;
}

void clear_b494_b495_b496_request_state_b8fe2(void)

{
  DAT_febeb494 = 0;
  DAT_febeb495 = 0;
  DAT_febeb496 = 0;
  return;
}

void finish_pending_b496_requests_with_status_b8fee(char param_1)

{
  uint32_t puVar1;
  undefined4 uVar2;
  undefined4 uVar3;
  undefined1 uVar4;
  byte bVar5;
  uint uVar6;
  
  bVar5 = DAT_febeb496;
  uVar4 = DAT_febeb495;
  puVar1 = 0xfebeb800u;
  uVar6 = (uint)DAT_febeb496;
  if (param_1 == '\x11') {
    uVar2 = 0;
    uVar3 = 0;
    if (DAT_febeb1a4 == '\0') {
      if (DAT_febef210 == -0x5aa5a55b) {
        puVar1 = 0xfebeb800u;
        set_indexed_request_and_clear_complement_b15ac(6);
      }
    }
    else {
      puVar1 = 0xfebeb800u;
      set_indexed_request_and_clear_complement_b15ac(0xb);
      latch_health_command_completion();
    }
  }
  else {
    uVar2 = 0x20;
    uVar3 = 0xfffffff7;
  }
  if ((bVar5 & 1) != 0) {
    thunk_publish_routine_or_pending_write_terminal_result_4d0a4(0xb,uVar2);
    uVar4 = 0;
    uVar6 = (uint)(bVar5 >> 1) << 1;
  }
  bVar5 = (byte)uVar6;
  if ((uVar6 >> 1 & 1) != 0) {
    thunk_submit_up_to_eight_response_bytes_or_error_34ea4(0,uVar3);
    bVar5 = bVar5 & 0xfd;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x36c))))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x36b))))) = uVar4;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x36a))))) = bVar5;
  return;
}
