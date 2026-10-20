#include "common.h"

undefined4 clear_source_coherence_reentry_history(void)

{
  DAT_febeb198 = 0;
  DAT_febeb19a = 0;
  DAT_febeb19c = 0;
  DAT_febeb192 = 0;
  return write_xor_encoded_u8_triplicate_d268c(source_coherence_history & 0xf4, ((byte *)camry_host_ptr((uint32_t)((0xfebeb18eu)))), ((byte *)camry_host_ptr((uint32_t)((0xfebeb18cu)))), ((undefined *)camry_host_ptr(0xfebeb18du)));
}

void close_health_receive_generation_qualification(void)

{
  health_receive_generation_armed = '\0';
  return;
}

void reset_secondary_channel_qualification_history(void)

{
  DAT_febeb1a0 = 0;
  DAT_febeb19e = 0;
  DAT_febeb193 = 0;
  DAT_febeb194 = DAT_febeb194 & 0xfe;
  return;
}

undefined4 initialize_health_record_lifecycle(void)

{
  return write_xor_encoded_u8_triplicate_d268c(0,((undefined *)camry_host_ptr(0xfebeb1a4u)),((undefined *)camry_host_ptr(0xfebeb1a2u)),((undefined *)camry_host_ptr(0xfebeb1a3u)));
}

undefined4 reset_health_record_lifecycle_entry(void)

{
  DAT_febeb1a5 = 0;
  DAT_febeb1a7 = 0;
  return write_xor_encoded_u8_triplicate_d268c(0,((undefined *)camry_host_ptr(0xfebeb1a4u)),((undefined *)camry_host_ptr(0xfebeb1a2u)),((undefined *)camry_host_ptr(0xfebeb1a3u)));
}

void publish_health_lifecycle_mode_indicator(void)

{
  if (((DAT_febeb11a & 0xff00) < 0x301) ||
     (((DAT_febeb11a & 0xff00) == 0x400 && (DAT_febeb1bd == 'Z')))) {
    DAT_febeb1a6 = 0;
  }
  else {
    DAT_febeb1a6 = 0x5a;
  }
  return;
}

void advance_health_record_lifecycle(void)

{
  byte bVar1;
  uint32_t puVar2;
  int iVar3;
  uint uVar4;
  undefined1 uVar5;
  char cVar6;
  char cStack_1d;
  
  puVar2 = 0xfebeb800u;
  iVar3 = read_vote_xor_encoded_u8_triplicate_d23b8(((undefined *)camry_host_ptr(0xfebeb1a4u)),((undefined *)camry_host_ptr(0xfebeb1a2u)),((undefined *)camry_host_ptr(0xfebeb1a3u)),&cStack_1d);
  uVar5 = DAT_febeb1a7;
  cVar6 = DAT_febeb1a5;
  if (iVar3 == -0xd) {
    cStack_1d = '\x11';
  }
  bVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x672)))));
  uVar4 = vote_redundant_application_mode_u16_b1c64();
  if (cStack_1d == '\0') {
    uVar4 = uVar4 & 0xff00;
    if ((bVar1 >> 3 & 1) != 0) {
      if (uVar4 == 0x500) {
        set_output_request_word('\0',0);
        set_output_request_word('\x01',0);
        thunk_write_record5_pair_sentinels_4841e();
        invalidate_thermal_history_record();
        pack_and_write_record9_configuration_fields_bd8ea();
        clear_acec_and_write_record8_when_initialized_bd8ba();
        cStack_1d = '\x11';
      }
      else {
        if (uVar4 != 0x300) {
          if (uVar4 == 0x400) {
            cStack_1d = '\x11';
          }
          goto LAB_000b42d4;
        }
        if (cVar6 == '\0') {
          thunk_write_record5_pair_sentinels_4841e();
          invalidate_thermal_history_record();
          clear_acec_and_write_record8_when_initialized_bd8ba();
          cVar6 = 'Z';
        }
        set_indexed_request_and_clear_complement_b15ac(0x23);
      }
      uVar5 = 0x5a;
    }
  }
  else if ((cStack_1d == '\x11') && ((bVar1 >> 4 & 1) != 0)) {
    cStack_1d = '\"';
  }
LAB_000b42d4:
  publish_health_lifecycle_mode_indicator();
  write_xor_encoded_u8_triplicate_d268c(cStack_1d,((undefined *)camry_host_ptr(0xfebeb1a4u)),((undefined *)camry_host_ptr(0xfebeb1a2u)),((undefined *)camry_host_ptr(0xfebeb1a3u)));
  DAT_febeb1a5 = cVar6;
  DAT_febeb1a7 = uVar5;
  return;
}

void set_b1a7_latch_b42f0(void)

{
  DAT_febeb1a7 = 0x5a;
  return;
}

void clear_b1a7_latch_b42fa(void)

{
  DAT_febeb1a7 = 0;
  return;
}

void return_only_stub_b4300(void)

{
  return;
}

void fill_constant_block_b4302(void)

{
  DAT_febeb1ac = 0;
  DAT_febeb1ad = 0;
  DAT_febeb1b6 = 0;
  DAT_febeb1b8 = 0;
  DAT_febeb1ba = DAT_000aefba;
  return;
}

void reset_b1a8_filter_state_b431a(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  DAT_febeb1aa = 0;
  DAT_febeb1ab = 0;
  DAT_febeb1ae = 0;
  DAT_febeb1b0 = 0;
  DAT_febeb1b4 = 0;
  DAT_febeb1b2 = DAT_000aefba;
  fill_constant_block_b4302();
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x658))))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x657))))) = 0;
  return;
}

void update_first_health_status_window(uint classification)

{
  if (DAT_febebe9c == 'Z') {
    if (DAT_febef04d == '\x04') {
      if ((DAT_febeb1ae < DAT_000aefb4) &&
         ((DAT_febeb084 < DAT_000aefb6 ||
          (((current_source_coherence_observations & 1) == 0 &&
           (((current_source_coherence_observations >> 1 & 1) == 0 ||
            ((classification >> 1 & 1) == 0)))))))) {
        if (DAT_febeb1ae == 0) {
          DAT_febeb1ab = 0x5a;
          DAT_febeb1aa = 0x5a;
          DAT_febeb1b2 = 0;
        }
        DAT_febeb1ae = DAT_febeb1ae + 1;
        return;
      }
    }
    else {
      if ((DAT_febef04d != '\x02' && DAT_febef04d != '\x03') || (DAT_febef04c == '\0')) {
        if (DAT_febeb1b2 < DAT_000aefba) {
          DAT_febeb1b2 = DAT_febeb1b2 + 1;
        }
        else {
          DAT_febeb1ab = 0;
        }
        goto LAB_000b441e;
      }
      if ((DAT_febeb1b0 < DAT_000aefb8) &&
         ((DAT_febeb084 < DAT_000aefb6 ||
          (((current_source_coherence_observations & 1) == 0 &&
           (((current_source_coherence_observations >> 1 & 1) == 0 ||
            ((classification >> 1 & 1) == 0)))))))) {
        if (DAT_febeb1b0 == 0) {
          DAT_febeb1ab = 0x5a;
          DAT_febeb1aa = 0x5a;
        }
        DAT_febeb1b0 = DAT_febeb1b0 + 1;
        return;
      }
    }
    DAT_febeb1ab = 0;
  }
  else {
    DAT_febeb1ab = 0;
LAB_000b441e:
    DAT_febeb1ae = 0;
    DAT_febeb1b0 = 0;
  }
  DAT_febeb1aa = 0;
  return;
}

void return_only_stub_b4536(void)

{
  return;
}

void reset_b1bc_latches_and_timers_b4538(void)

{
  DAT_febeb1bc = 0;
  DAT_febeb1bd = 0;
  DAT_febeb1c0 = 0;
  DAT_febeb1c2 = 0;
  return;
}

void debounce_thermal_record_diagnostic_capture_b4546(void)

{
  char cVar1;
  int iVar2;
  char cVar3;
  char cVar4;
  uint32_t puVar5;
  uint event;
  char cVar6;
  char cVar7;
  ushort uVar8;
  char cVar9;
  ushort uVar10;
  char cVar11;
  
  cVar4 = DAT_febef0fe;
  cVar3 = DAT_febef0fd;
  iVar2 = DAT_febeb30c;
  cVar1 = DAT_febeb1d1;
  cVar11 = DAT_febeb1be;
  puVar5 = 0xfebeb800u;
  if (DAT_febeb30c == 0x55aaaa55) {
    cVar9 = DAT_febebe79;
    uVar8 = DAT_000aefc0;
    cVar7 = DAT_febebe7c;
    cVar6 = '\0';
  }
  else {
    cVar9 = DAT_febebe7a;
    uVar8 = DAT_000aefc6;
    cVar7 = DAT_febebe7d;
    cVar6 = DAT_febef10d;
    if (DAT_febeb30c != -0x55aaaa56) {
      cVar9 = -1;
      cVar7 = '\"';
      uVar8 = 0xffff;
      cVar6 = '\0';
    }
  }
  uVar10 = DAT_febeb1c0;
  if (DAT_febeb1bc == 'Z') {
    cVar9 = 'Z';
    goto LAB_000b46d2;
  }
  if (((((DAT_febeb1a4 == '\x11') &&
        ((((DAT_febeb20e == '\0' || (DAT_febeb20e == '3')) &&
          (published_internal_source_admission_state < 2)) &&
         ((cVar7 == '\0' && (DAT_febeb18f == '\0')))))) &&
       ((DAT_febef04c != '\0' ||
        (((DAT_febef04d != '\x02' && (DAT_febef04d != '\x03')) && (DAT_febef04d != '\x04')))))) &&
      ((((DAT_febeb11a & 0xff00) != 0x500 && (cVar9 == 'Z')) &&
       ((DAT_febef10e != '\0' || (cVar6 == '\0')))))) &&
     ((DAT_febebeb8 == '\0' || ((DAT_febebeb8 == 'Z' && (DAT_febead93 == '\0')))))) {
    cVar9 = DAT_febeb1bd;
    if (uVar8 < DAT_febeb1c0) goto LAB_000b46d2;
    uVar10 = DAT_febeb1c0 + 1;
    puVar5 = 0xfebeb800u;
    if (uVar8 < uVar10) {
      puVar5 = 0xfebeb800u;
      publish_thermal_reference_record();
      publish_thermal_history_record();
      stage_received_word_age_record13();
      cVar9 = 'Z';
      if (cVar1 == '\0') {
        if ((cVar3 == '\0') && (cVar4 == '\0')) {
          cVar11 = 'D';
        }
        else {
          if (iVar2 == -0x55aaaa56) {
            report_diagnostic_event_failure(0x101,0x32);
            cVar11 = '\x11';
          }
          else {
            report_diagnostic_event_failure(0x99,0x32);
            cVar11 = '\0';
          }
          thunk_increment_indexed_u16_counter_once_until_rearmed_545de(0xf);
          thunk_gate_indexed_event_payload_during_diagnostic_clears_51cf6(7,0x32);
        }
      }
      else {
        report_diagnostic_event_failure(0x90,0x32);
        cVar11 = '\"';
      }
      goto LAB_000b46d2;
    }
  }
  else {
    uVar10 = 0;
    puVar5 = 0xfebeb800u;
    if (DAT_febeb1bd == 'Z') {
      puVar5 = 0xfebeb800u;
      thunk_write_record5_pair_sentinels_4841e();
      invalidate_thermal_history_record();
      if (cVar11 == '\x11') {
        event = 0x101;
      }
      else {
        event = 0x90;
        if (cVar11 == '\0') {
          event = 0x99;
        }
      }
      report_diagnostic_event_pass(event);
    }
  }
  cVar9 = '\0';
LAB_000b46d2:
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x643))))) = cVar9;
  (*((ushort *)camry_host_ptr((uint32_t)(puVar5 + -0x640)))) = uVar10;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x642))))) = cVar11;
  return;
}

void latch_coherence_reentry_after_hold_b46e0(void)

{
  undefined1 uVar1;
  uint32_t puVar2;
  ushort uVar3;
  
  puVar2 = 0xfebeb800u;
  uVar1 = DAT_febeb1bc;
  if (((DAT_febeb1bd == 'Z') && (DAT_febebedd == 'Z')) && (DAT_febebede <= DAT_000aefc4)) {
    uVar3 = DAT_febeb1c2;
    if ((DAT_febeb1c2 <= DAT_000aefc2) && (uVar3 = DAT_febeb1c2 + 1, DAT_000aefc2 < uVar3)) {
      puVar2 = 0xfebeb800u;
      clear_source_coherence_reentry_history();
      uVar1 = 0x5a;
    }
  }
  else {
    uVar3 = 0;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x644))))) = uVar1;
  (*((ushort *)camry_host_ptr((uint32_t)(puVar2 + -0x63e)))) = uVar3;
  return;
}

void publish_or_clear_latched_output_request_four_b4736(void)

{
  uchar uVar1;
  char cVar2;
  int iVar3;
  uint32_t puVar4;
  uint uVar5;
  undefined2 uVar6;
  undefined2 uVar7;
  undefined1 uVar8;
  char cVar9;
  
  iVar3 = DAT_febeb30c;
  uVar6 = DAT_febeb1c2;
  uVar7 = DAT_febeb1c0;
  cVar2 = DAT_febeb1be;
  uVar8 = DAT_febeb1bd;
  cVar9 = DAT_febeb1bc;
  uVar1 = source_coherence_history;
  puVar4 = 0xfebeb800u;
  uVar5 = 0;
  if (DAT_febeb1bc == 'Z') {
    if (DAT_febebcb0 == 0) {
      uVar5 = 0x70017001;
    }
    puVar4 = 0xfebeb800u;
    set_output_request_word('\x04',uVar5);
    if (((uVar1 >> 3 & 1) != 0) || (iVar3 == 0)) {
      set_output_request_word('\x04',0);
      if (cVar2 == '\x11') {
        uVar5 = 0x101;
      }
      else {
        uVar5 = 0x90;
        if (cVar2 == '\0') {
          uVar5 = 0x99;
        }
      }
      report_diagnostic_event_pass(uVar5);
      thunk_write_record5_pair_sentinels_4841e();
      invalidate_thermal_history_record();
      uVar7 = 0;
      uVar6 = 0;
      uVar8 = 0;
      cVar9 = '\0';
    }
  }
  else {
    set_output_request_word('\x04',0);
  }
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar4 + -0x640)))) = uVar7;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x643))))) = uVar8;
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar4 + -0x63e)))) = uVar6;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x644))))) = cVar9;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x642))))) = cVar2;
  return;
}

void update_thermal_capture_hold_and_request_b47c0(void)

{
  debounce_thermal_record_diagnostic_capture_b4546();
  latch_coherence_reentry_after_hold_b46e0();
  publish_or_clear_latched_output_request_four_b4736();
  return;
}

void return_only_stub_b47d4(void)

{
  return;
}

void initialize_b1c4_mode_two_b47d6(void)

{
  DAT_febeb1c4 = 2;
  return;
}

void select_b1c4_from_three_latches_b47de(void)

{
  if (((DAT_febeb1ce == 'Z') || (DAT_febeb1d1 == 'Z')) || (DAT_febeb1bd == 'Z')) {
    DAT_febeb1c4 = 2;
  }
  else {
    DAT_febeb1c4 = 1;
  }
  return;
}

void return_only_stub_b4808(void)

{
  return;
}

void return_only_stub_b480a(void)

{
  return;
}

undefined2 select_bede_or_bee2_by_source_flags_b480c(void)

{
  if ((((published_internal_source_admission_state != '\x03') && ((DAT_febef093 >> 1 & 1) == 0))
      && (DAT_febef013 != '\x02')) && ((DAT_febef013 != '\x03' && ((DAT_febef16a & 0x1010) == 0))))
  {
    return DAT_febebede;
  }
  return DAT_febebee2;
}

void time_b1c9_capture_and_lookup_b483e(void)

{
  char cVar1;
  uint32_t puVar2;
  uint uVar3;
  uint uVar4;
  undefined1 uVar5;
  short sVar6;
  undefined2 uStack_12;
  
  puVar2 = 0xfebeb800u;
  uStack_12 = DAT_febeb1ec;
  uVar4 = (uint)DAT_000af028;
  uVar5 = DAT_febeb1cb;
  cVar1 = DAT_febeb1c9;
  if ((((DAT_febeb1c9 == 'Z') && (DAT_febeb1ca == 'Z')) && (DAT_febeb080 < DAT_000aefca)) &&
     ((DAT_febebeb8 == '\0' || ((DAT_febebeb8 == 'Z' && (DAT_febead93 == '\0')))))) {
    if (DAT_febeb1e4 < DAT_000aefd4) {
      sVar6 = DAT_febeb1e4 + 1;
    }
    else {
      sVar6 = 0;
      if (DAT_febeb1ce != 'Z') {
        puVar2 = 0xfebeb800u;
        uVar3 = select_bede_or_bee2_by_source_flags_b480c();
        uVar5 = 0;
        if (uVar4 <= uVar3) {
          uVar5 = 0x5a;
          interpolate_unsigned16_pairs_to_output_d1ee0(((undefined *)camry_host_ptr(0xaf000u)),uVar3,&uStack_12);
        }
        cVar1 = '\0';
      }
    }
  }
  else {
    sVar6 = 0;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x635))))) = uVar5;
  (*((short *)camry_host_ptr((uint32_t)(puVar2 + -0x61c)))) = sVar6;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x637))))) = cVar1;
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar2 + -0x614)))) = uStack_12;
  return;
}

void expire_b1ca_dual_timers_b48dc(void)

{
  if (((DAT_febeb1ca == 'Z') && (DAT_febef0b3 != 'Z')) && (DAT_febeb1c9 == '\0')) {
    if ((DAT_febef0fe == '\0') && (DAT_febef0fd != '\0')) {
      DAT_febeb1e8 = 0;
    }
    else if (DAT_febeb1e8 < DAT_000aefd8) {
      DAT_febeb1e8 = DAT_febeb1e8 + 1;
    }
    else {
      DAT_febeb1e8 = 0;
      DAT_febeb1ca = '\0';
    }
    if (DAT_febeb1ea < DAT_000aefdc) {
      DAT_febeb1ea = DAT_febeb1ea + 1;
    }
    else {
      DAT_febeb1ea = 0;
      DAT_febeb1ca = '\0';
    }
  }
  else {
    DAT_febeb1e8 = 0;
    DAT_febeb1ea = 0;
  }
  return;
}

void time_b1cc_capture_and_lookup_b4948(void)

{
  char cVar1;
  uint32_t puVar2;
  uint uVar3;
  uint uVar4;
  undefined1 uVar5;
  short sVar6;
  undefined2 uStack_12;
  
  puVar2 = 0xfebeb800u;
  uStack_12 = DAT_febeb1ec;
  uVar4 = (uint)DAT_000af028;
  uVar5 = DAT_febeb1cb;
  cVar1 = DAT_febeb1cc;
  if (((DAT_febeb1cc == 'Z') && ((DAT_febef0b3 == 'Z' || (DAT_febef0b1 == 'Z')))) &&
     ((DAT_febef0fe != '\0' || (DAT_febef0fd == '\0')))) {
    if (DAT_febeb1ee < DAT_000aefda) {
      sVar6 = DAT_febeb1ee + 1;
    }
    else {
      sVar6 = 0;
      if (DAT_febeb1ce != 'Z') {
        puVar2 = 0xfebeb800u;
        uVar3 = select_bede_or_bee2_by_source_flags_b480c();
        uVar5 = 0;
        if (uVar4 <= uVar3) {
          uVar5 = 0x5a;
          interpolate_unsigned16_pairs_to_output_d1ee0(((undefined *)camry_host_ptr(0xaf000u)),uVar3,&uStack_12);
        }
        cVar1 = '\0';
      }
    }
  }
  else {
    sVar6 = 0;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x635))))) = uVar5;
  (*((short *)camry_host_ptr((uint32_t)(puVar2 + -0x612)))) = sVar6;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x634))))) = cVar1;
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar2 + -0x614)))) = uStack_12;
  return;
}

void qualify_health_source_recovery(void)

{
  char cVar1;
  uint32_t puVar2;
  undefined1 uVar3;
  undefined1 uVar4;
  undefined1 uVar5;
  char cVar6;
  char cVar7;
  char cVar8;
  byte bVar9;
  ushort uVar10;
  ushort uVar11;
  
  bVar9 = DAT_febeb1c8;
  puVar2 = 0xfebeb800u;
  cVar1 = '\0';
  uVar5 = DAT_febeb1ce;
  uVar4 = DAT_febeb1d0;
  uVar3 = DAT_febeb1d1;
  cVar8 = DAT_febeb1c9;
  cVar6 = DAT_febeb1ca;
  cVar7 = DAT_febeb1cc;
  uVar11 = DAT_febeb1fa;
  uVar10 = DAT_febeb1fc;
  if (DAT_febeb1cd != '\0') goto LAB_000b4a90;
  if (((DAT_febeb1c9 == '\0') && (DAT_000aefd0 < DAT_febeb080)) && (DAT_febeb080 < DAT_000aefd2)) {
    if (DAT_febeb1fa < DAT_000aefea) {
      uVar11 = DAT_febeb1fa + 1;
    }
    else {
      cVar1 = 'Z';
      uVar11 = 0;
      cVar8 = cVar1;
      cVar6 = cVar1;
    }
  }
  else {
    uVar11 = 0;
  }
  if (((DAT_febeb1cc == '\0') && (DAT_febef0fd == '\x01')) && (DAT_febef0fe == '\0')) {
    if (DAT_febeb1fc < DAT_000aefec) {
      uVar10 = DAT_febeb1fc + 1;
      goto LAB_000b4a68;
    }
    uVar10 = 0;
    cVar7 = 'Z';
  }
  else {
    uVar10 = 0;
LAB_000b4a68:
    if (cVar1 != 'Z') goto LAB_000b4a90;
  }
  puVar2 = 0xfebeb800u;
  report_diagnostic_event_pass(0x8d);
  thunk_set_two_classifier_flags_and_clear_two_counts_515d4();
  clear_source_coherence_reentry_history();
  uVar5 = 0;
  uVar4 = 0x5a;
  uVar3 = 0x5a;
  bVar9 = bVar9 & 0xef | 4;
LAB_000b4a90:
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x637))))) = cVar8;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x636))))) = cVar6;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x634))))) = cVar7;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x632))))) = uVar5;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x630))))) = uVar4;
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x66e))))) == 'Z') {
    uVar3 = 0;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x638))))) = bVar9;
  (*((ushort *)camry_host_ptr((uint32_t)(puVar2 + -0x606)))) = uVar11;
  (*((ushort *)camry_host_ptr((uint32_t)(puVar2 + -0x604)))) = uVar10;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x62f))))) = uVar3;
  return;
}

void latch_health_source_unavailability(void)

{
  char cVar1;
  uint32_t puVar2;
  byte bVar3;
  
  bVar3 = DAT_febeb1c8;
  puVar2 = 0xfebeb800u;
  cVar1 = DAT_febeb1ce;
  if ((((DAT_febeb1cd == '\0') && (DAT_febeb1ce == '\0')) &&
      ((DAT_febeb1ca == '\0' || (DAT_febeb1cc == '\0')))) && (DAT_febeb1cb == 'Z')) {
    puVar2 = 0xfebeb800u;
    report_diagnostic_event_failure(0x8d,0x32);
    cVar1 = 'Z';
    bVar3 = bVar3 & 0xfb | 0x10;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x632))))) = cVar1;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x638))))) = bVar3;
  return;
}

void expire_b1d0_by_elapsed_or_low_sample_hold_b4b04(void)

{
  if ((DAT_febeb1d0 == 'Z') && (DAT_febeb1ce == 'Z')) {
    if ((DAT_febeb1f4 < DAT_febeb1ec) && (DAT_febeb200 < DAT_000aeff2)) {
      if ((DAT_febebedd == 'Z') && (DAT_febebede <= DAT_000aeff0)) {
        DAT_febeb200 = DAT_febeb200 + 1;
      }
      else {
        DAT_febeb200 = 0;
      }
      DAT_febeb1f4 = DAT_febeb1f4 + 1;
    }
    else {
      DAT_febeb1f4 = 0;
      DAT_febeb1d0 = '\0';
      DAT_febeb200 = 0;
    }
  }
  else {
    DAT_febeb1f4 = 0;
    DAT_febeb200 = 0;
  }
  return;
}

void filter_b1f8_between_zero_and_1024_b4b6c(void)

{
  uint8_t stack_record_1e[30];
  ushort uVar1;
  ushort uVar2;
  int iVar3;
  uint32_t puVar4;
  uint uVar5;
  int iVar6;
  char cVar7;
  ushort uVar8;
  
  cVar7 = DAT_febeb1cf;
  puVar4 = 0xfebeb800u;
  iVar6 = (int)((int)(int16_t)DAT_febeb054);
  (*((uint16_t *)(stack_record_1e + 0))) = DAT_febeb1f8;
  (*((uint32_t *)(stack_record_1e + 2))) = DAT_febeb208;
  if (iVar6 + 0x7fff < 0 == (-1 < iVar6 && iVar6 + 0x7fff < 0) && iVar6 != -0x7fff) {
    if (iVar6 < 0) {
      iVar6 = (int)-((int)(int16_t)DAT_febeb054);
    }
  }
  else {
    iVar6 = 0x7fff;
  }
  ((uint16_t *)((stack_record_1e + 6)))[0] = DAT_febeb1f8;
  (*((uint32_t *)(stack_record_1e + 10))) = DAT_febeb208;
  if ((DAT_febeb1cf == '\0') && (DAT_febeb1d0 == '\0')) {
    if (DAT_000aeff4 < DAT_febeb1f8) {
      uVar1 = DAT_000aefe6;
      uVar8 = DAT_febeb1f6;
      if (DAT_febeb1f6 < DAT_000aefe2) {
        iVar3 = (int)DAT_000aefe4;
        uVar8 = DAT_febeb1f6 + 1;
        uVar1 = DAT_000aefe8;
        if (iVar6 - iVar3 < 0 != (iVar6 < 0 != iVar3 < 0 && iVar3 < 0 == iVar6 - iVar3 < 0) ||
            iVar6 == iVar3) goto LAB_000b4bf4;
      }
      ((uint16_t *)((stack_record_1e + 6)))[1] = 0;
      puVar4 = 0xfebeb800u;
      filter_unsigned_sample_accumulator(((uint16_t *)((stack_record_1e + 6))),(uint)uVar1,((uint16_t *)(stack_record_1e)),((uint32_t *)((stack_record_1e + 2))));
    }
    else {
      cVar7 = 'Z';
      uVar8 = 0;
    }
LAB_000b4bf4:
    uVar5 = 0;
    uVar1 = uVar8;
    uVar2 = 0;
    if (0x14 < (*((uint16_t *)(stack_record_1e + 0)))) goto LAB_000b4c38;
  }
  else {
    ((uint16_t *)((stack_record_1e + 6)))[1] = 0x400;
    uVar8 = 0;
    filter_unsigned_sample_accumulator(((uint16_t *)((stack_record_1e + 6))),(uint)DAT_000aefee,((uint16_t *)(stack_record_1e)),((uint32_t *)((stack_record_1e + 2))));
    uVar5 = 0x4000000;
    uVar1 = 0;
    uVar2 = 0x400;
    if ((*((uint16_t *)(stack_record_1e + 0))) < 0x3ec) goto LAB_000b4c38;
  }
  (*((uint16_t *)(stack_record_1e + 0))) = uVar2;
  uVar8 = uVar1;
  (*((uint32_t *)(stack_record_1e + 2))) = uVar5;
LAB_000b4c38:
  (*((ushort *)camry_host_ptr((uint32_t)(puVar4 + -0x608)))) = (*((uint16_t *)(stack_record_1e + 0)));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x631))))) = cVar7;
  (*((ushort *)camry_host_ptr((uint32_t)(puVar4 + -0x60a)))) = uVar8;
  (*((uint *)camry_host_ptr((uint32_t)(puVar4 + -0x5f8)))) = (*((uint32_t *)(stack_record_1e + 2)));
  return;
}

void update_health_secondary_qualification_handshake(void)

{
  char cVar1;
  int iVar2;
  uint32_t puVar3;
  int iVar4;
  undefined1 uVar5;
  int iVar6;
  char cVar7;
  ushort uVar8;
  bool bVar9;
  
  puVar3 = 0xfebeb800u;
  if (DAT_000aefca < DAT_febeb080) {
    if (DAT_febeb204 < DAT_000aefd4) {
      uVar8 = DAT_febeb204 + 1;
      iVar2 = 0;
    }
    else {
      iVar2 = 0x5a;
      uVar8 = DAT_febeb204;
    }
  }
  else {
    uVar8 = 0;
    iVar2 = 0;
  }
  uVar5 = DAT_febeb1d6;
  cVar7 = DAT_febeb1d5;
  if (((int8_t)DAT_febeb1d5) == -0x5b) {
    if (DAT_febef0fe == '\0') {
      bVar9 = DAT_febef0fd == '\x01';
    }
    else {
      bVar9 = iVar2 == 0x5a;
    }
    if (!bVar9) goto LAB_000b4d18;
    if ((DAT_febef100 == '\0') && (DAT_febef0ff == '\x01')) {
      iVar4 = 0x5a;
    }
    else {
      iVar4 = 0;
    }
    if ((DAT_febef102 == '\0') && (DAT_febef101 == '\x01')) {
      iVar6 = 0x5a;
    }
    else {
      iVar6 = 0;
    }
    if (iVar4 == 0x5a) {
      cVar1 = DAT_febef102;
      if (iVar6 != 0x5a) goto LAB_000b4ce2;
    }
    else {
      cVar1 = DAT_febef100;
      if (iVar6 != 0x5a) goto LAB_000b4cf0;
LAB_000b4ce2:
      if (cVar1 == '\0') goto LAB_000b4cf0;
    }
    uVar5 = 0x5a;
    if (DAT_febeb193 == 'Z') {
      cVar7 = 'Z';
    }
  }
LAB_000b4cf0:
  if (DAT_febef0fe == '\0') {
    bVar9 = DAT_febef0fd == '\x01';
  }
  else {
    bVar9 = iVar2 == 0x5a;
  }
  if ((bVar9) &&
     (((DAT_febef100 == '\0' && (DAT_febef0ff == '\0')) ||
      ((DAT_febef102 == '\0' && (DAT_febef101 == '\0')))))) {
    puVar3 = 0xfebeb800u;
    reset_secondary_channel_qualification_history();
    uVar5 = 0;
    cVar7 = -0x5b;
  }
LAB_000b4d18:
  (*((ushort *)camry_host_ptr((uint32_t)(puVar3 + -0x5fc)))) = uVar8;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x62a))))) = uVar5;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x62b))))) = cVar7;
  return;
}

void latch_qualified_health_entry_conditions(void)

{
  ushort uVar1;
  ushort uVar2;
  int iVar3;
  int iVar4;
  
  iVar4 = (int)((int)(int16_t)DAT_febeafdc);
  if (iVar4 + 0x7fff < 0 == (-1 < iVar4 && iVar4 + 0x7fff < 0) && iVar4 != -0x7fff) {
    if (iVar4 < 0) {
      iVar4 = (int)-((int)(int16_t)DAT_febeafdc);
    }
  }
  else {
    iVar4 = 0x7fff;
  }
  uVar2 = DAT_febeb086;
  uVar1 = DAT_febeb088;
  if ((DAT_febeb082 & 1) == 0) {
    uVar1 = DAT_febeb086;
    if ((DAT_febeb082 & 2) == 0) {
      uVar1 = DAT_febeb088;
    }
  }
  else {
    uVar2 = DAT_febeb088;
    if ((DAT_febeb082 & 2) != 0) {
      uVar2 = DAT_febeb086;
    }
  }
  if (DAT_febeb1cd == '\0') {
    if (((((DAT_febeb11a & 0xff00) < 0x700) && (DAT_febeb1a7 != '\0')) || (DAT_febeb1c9 != '\0')) &&
       ((((DAT_febeb1ce != '\0' || ((DAT_febeb1ca != '\0' && (DAT_febeb1cc != '\0')))) ||
         (DAT_febeb1cb != '\0')) && (DAT_febeb1cf != 'Z')))) {
      DAT_febeb1cd = '\0';
      if (((DAT_000aefcc < DAT_febeb080) && (DAT_000aefce < uVar2)) &&
         ((DAT_000aefce < uVar1 &&
          (iVar3 = (int)DAT_000aeffc,
          iVar4 - iVar3 < 0 != (iVar4 < 0 != iVar3 < 0 && iVar3 < 0 == iVar4 - iVar3 < 0))))) {
        if (DAT_000aefe0 <= DAT_febeb1f0) {
          DAT_febeb1c8 = DAT_febeb1c8 | 8;
          DAT_febeb1cd = 0x5a;
          DAT_febeb1d4 = 0x5a;
          DAT_febeb1f0 = 0;
          DAT_febeb1f2 = 0;
          return;
        }
        DAT_febeb1f0 = DAT_febeb1f0 + 1;
        goto LAB_000b4e0c;
      }
    }
    else {
      DAT_febeb1cd = 'Z';
      DAT_febeb1c8 = DAT_febeb1c8 | 8;
    }
  }
  DAT_febeb1f0 = 0;
LAB_000b4e0c:
  if (((((DAT_febeb1cd == '\0') && ((DAT_febeb11a & 0xff00) < 0x501)) && (DAT_febeb1a7 == '\0')) &&
      (DAT_000aefcc < DAT_febeb080)) && ((DAT_febef0fe != '\0' || (DAT_febef0fd == '\0')))) {
    if (DAT_febeb1f2 < DAT_000aefde) {
      DAT_febeb1f2 = DAT_febeb1f2 + 1;
      return;
    }
    DAT_febeb1c8 = DAT_febeb1c8 | 8;
    DAT_febeb1cd = 0x5a;
    DAT_febeb1f2 = 0;
    return;
  }
  DAT_febeb1f2 = 0;
  return;
}

void latch_qualified_health_completion_conditions(void)

{
  if (DAT_febeb1cd == 'Z') {
    if ((DAT_000aeff8 < DAT_febeb080) && (DAT_febeb080 < DAT_000aeffa)) {
      if (DAT_febeb1fe < DAT_000aeff6) {
        DAT_febeb1fe = DAT_febeb1fe + 1;
      }
      else {
        DAT_febeb1c8 = DAT_febeb1c8 | 1;
      }
    }
    else {
      DAT_febeb1fe = 0;
      if (DAT_febeb080 <= DAT_000aeff8) {
        DAT_febeb1fe = 0;
        return;
      }
    }
    if ((DAT_febeb080 < DAT_000aeffa) && ((DAT_febeb11a & 0xff00) == 0x800)) {
      DAT_febeb1c8 = DAT_febeb1c8 | 2;
    }
  }
  return;
}

void select_held_or_live_bede_state_b4eb6(void)

{
  undefined2 uVar1;
  undefined1 uVar2;
  
  if (DAT_febeb1d4 == 'Z') {
    uVar1 = DAT_febeb202;
    uVar2 = DAT_febeb1d2;
    if (DAT_febeb1a7 == 'Z') {
      DAT_febeb1d3 = DAT_febeb1a7;
      return;
    }
  }
  else {
    uVar1 = DAT_febebede;
    uVar2 = DAT_febebef0;
    if (DAT_febeb1f0 != 1) {
      uVar1 = DAT_febeb202;
      uVar2 = DAT_febeb1d2;
    }
  }
  DAT_febeb1d2 = uVar2;
  DAT_febeb202 = uVar1;
  DAT_febeb1d3 = 0;
  return;
}

void update_qualified_health_source_policy(void)

{
  char cVar1;
  uint32_t puVar2;
  ushort uVar3;
  
  cVar1 = DAT_febeb1a7;
  puVar2 = 0xfebeb800u;
  uVar3 = DAT_febeb11a & 0xff00;
  time_b1c9_capture_and_lookup_b483e();
  expire_b1ca_dual_timers_b48dc();
  time_b1cc_capture_and_lookup_b4948();
  qualify_health_source_recovery();
  if ((cVar1 == 'Z') && (uVar3 < 0x501)) {
    latch_health_source_unavailability();
    expire_b1d0_by_elapsed_or_low_sample_hold_b4b04();
    filter_b1f8_between_zero_and_1024_b4b6c();
  }
  else {
    (*((undefined2 *)camry_host_ptr((uint32_t)(puVar2 + -0x608)))) = 0x400;
    (*((undefined4 *)camry_host_ptr((uint32_t)(puVar2 + -0x5f8)))) = 0x4000000;
  }
  update_health_secondary_qualification_handshake();
  latch_qualified_health_entry_conditions();
  latch_qualified_health_completion_conditions();
  select_held_or_live_bede_state_b4eb6();
  return;
}

undefined4 initialize_qualified_health_state(void)

{
  return write_xor_encoded_u8_triplicate_d268c(0,((undefined *)camry_host_ptr(0xfebeb20eu)),((undefined *)camry_host_ptr(0xfebeb20cu)),((undefined *)camry_host_ptr(0xfebeb20du)));
}

void reset_qualified_health_state_entry(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  write_xor_encoded_u8_triplicate_d268c(0,((undefined *)camry_host_ptr(0xfebeb20eu)),((undefined *)camry_host_ptr(0xfebeb20cu)),((undefined *)camry_host_ptr(0xfebeb20du)));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x5f1))))) = 0;
  return;
}

void route_qualified_health_mode_requests(uchar qualified_state)

{
  ushort uVar1;
  undefined4 uVar2;
  
  uVar1 = DAT_febeb11a & 0xff00;
  if (qualified_state == '\x11') {
    if (DAT_febeb11a == 0x522) {
LAB_000b4fc2:
      if (DAT_febebcb0 != 0) {
        return;
      }
      if (DAT_febeafce == '\x11') {
        return;
      }
    }
    else if ((uVar1 == 0x400) || (uVar1 == 0x500)) goto LAB_000b4fde;
  }
  else {
    if (qualified_state != '\"') {
      return;
    }
    if (DAT_febeb11a == 0x522) goto LAB_000b4fc2;
    if ((uVar1 != 0x400) && (uVar1 != 0x500)) {
      if ((uVar1 != 0x700) && (uVar1 != 0x800)) {
        return;
      }
      uVar2 = 2;
      goto LAB_000b4ff4;
    }
LAB_000b4fde:
    if (DAT_febebcb0 != 0) {
      return;
    }
  }
  uVar2 = 1;
LAB_000b4ff4:
  set_indexed_request_and_clear_complement_b15ac(uVar2);
  return;
}

undefined4 advance_qualified_health_state(void)

{
  byte bVar1;
  uint32_t puVar2;
  int iVar3;
  uchar uStack_11;
  
  puVar2 = 0xfebeb800u;
  iVar3 = read_vote_xor_encoded_u8_triplicate_d23b8(((undefined *)camry_host_ptr(0xfebeb20eu)),((undefined *)camry_host_ptr(0xfebeb20cu)),((undefined *)camry_host_ptr(0xfebeb20du)),&uStack_11);
  if (iVar3 == -0xd) {
    uStack_11 = '\0';
  }
  bVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x638)))));
  if (uStack_11 == '\0') {
    if (((bVar1 >> 3 & 1) == 0) && ((bVar1 >> 5 & 1) == 0)) {
      if ((bVar1 >> 4 & 1) != 0) {
        uStack_11 = '3';
      }
      goto LAB_000b508e;
    }
  }
  else {
    if (uStack_11 != '3') {
      if ((uStack_11 == '\x11') && (((bVar1 & 1) != 0 || ((bVar1 >> 1 & 1) != 0)))) {
        uStack_11 = '\"';
        (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x5f1))))) = 0x5a;
        close_health_receive_generation_qualification();
      }
      goto LAB_000b508e;
    }
    if (((bVar1 >> 3 & 1) == 0) && ((bVar1 >> 5 & 1) == 0)) {
      if ((bVar1 >> 2 & 1) != 0) {
        uStack_11 = '\0';
      }
      goto LAB_000b508e;
    }
  }
  uStack_11 = '\x11';
LAB_000b508e:
  route_qualified_health_mode_requests(uStack_11);
  return write_xor_encoded_u8_triplicate_d268c(uStack_11,((undefined *)camry_host_ptr(0xfebeb20eu)),((undefined *)camry_host_ptr(0xfebeb20cu)),((undefined *)camry_host_ptr(0xfebeb20du)));
}
