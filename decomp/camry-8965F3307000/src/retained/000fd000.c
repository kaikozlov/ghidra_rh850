#include "common.h"

void copy_cell_block_fd400(void)

{
  DAT_febee5c4 = ((int)(int16_t)DAT_febeac70);
  DAT_febee5c0 = DAT_febeac2d;
  DAT_febee5c1 = DAT_febeac39;
  DAT_febee5c2 = DAT_febeac3e;
  DAT_febee5c3 = DAT_febeb354;
  return;
}

void snapshot_acquisition_status_to_e740_block_fd426(void)

{
  DAT_febee744 = DAT_febeac1c;
  DAT_febee740 = DAT_febeac08;
  DAT_febee741 = DAT_febeac09;
  DAT_febee742 = DAT_febeac02;
  return;
}

void snapshot_service_byte_and_signed_word_pair_fd444(void)

{
  DAT_febee782 = ((int)(int16_t)DAT_febeaf40);
  DAT_febee780 = DAT_febeaf3d;
  return;
}

void copy_cell_block_fd456(void)

{
  DAT_febeeac4 = DAT_febebede;
  DAT_febeeac0 = DAT_febebef0;
  DAT_febeeac6 = DAT_febebee2;
  DAT_febeead0 = DAT_febeb218;
  DAT_febeeac8 = DAT_febeb138;
  DAT_febeeaca = DAT_febeb13c;
  DAT_febeeac1 = DAT_febeb1a7;
  DAT_febeeacc = DAT_febeb11a;
  DAT_febeeac2 = DAT_febeb112;
  DAT_febeeace = DAT_febeae86;
  DAT_febeeac3 = DAT_febead9e;
  return;
}

void snapshot_rom_bounds_and_retained_control_to_eb00_block_fd49e(void)

{
  DAT_febeeb24 = learned_quad_rom_bounds.pair1_upper;
  DAT_febeeb28 = learned_quad_rom_bounds.pair1_lower;
  DAT_febeeb2c = learned_quad_rom_bounds.pair2_upper;
  DAT_febeeb30 = learned_quad_rom_bounds.pair2_lower;
  DAT_febeeb34 = DAT_000aef6c;
  DAT_febeeb38 = DAT_000aef70;
  DAT_febeeb3c = DAT_000aef74;
  DAT_febeeb40 = DAT_000aef78;
  DAT_febeeb00 = DAT_febebe9b;
  DAT_febeeb0a = DAT_febebe82;
  DAT_febeeb01 = DAT_febebe78;
  DAT_febeeb0c = DAT_febebee2;
  DAT_febeeb44 = received_word_unchanged_age;
  DAT_febeeb0e = received_retained_word;
  DAT_febeeb02 = DAT_febebe60;
  DAT_febeeb10 = ((int)(int16_t)DAT_febeb384);
  DAT_febeeb12 = DAT_febeb142;
  DAT_febeeb14 = DAT_febeb13c;
  DAT_febeeb16 = ((int)(int16_t)DAT_febeae12);
  DAT_febeeb03 = DAT_febeacf1;
  DAT_febeeb18 = ((int)(int16_t)DAT_febeae58);
  DAT_febeeb04 = DAT_febead39;
  DAT_febeeb1a = ((int)(int16_t)DAT_febeae36);
  DAT_febeeb05 = DAT_febead0a;
  DAT_febeeb06 = DAT_febeacf5;
  DAT_febeeb1c = ((int)(int16_t)DAT_febeae16);
  DAT_febeeb1e = DAT_febeb11a;
  DAT_febeeb07 = DAT_febead93;
  DAT_febeeb08 = DAT_febebeb8;
  DAT_febeeb20 = ((int)(int16_t)DAT_febeaecc);
  DAT_febeeb22 = ((int)(int16_t)DAT_febeb38a);
  return;
}

void snapshot_retained_and_coherence_state_to_eb80_block_fd562(void)

{
  DAT_febeeb80 = DAT_febeb1d5;
  DAT_febeeb81 = DAT_febebe9b;
  DAT_febeeb92 = DAT_febebe82;
  DAT_febeeb82 = DAT_febebe78;
  DAT_febeeb83 = DAT_febebef0;
  DAT_febeeb94 = DAT_febebee2;
  DAT_febeebac = received_word_unchanged_age;
  DAT_febeeb96 = received_retained_word;
  DAT_febeeb84 = DAT_febebe60;
  DAT_febeeb98 = DAT_febeb142;
  DAT_febeeb85 = DAT_febeb1a7;
  DAT_febeeb86 = DAT_febeb1ce;
  DAT_febeeb87 = DAT_febeb20e;
  DAT_febeeb88 = DAT_febeb1a8;
  DAT_febeeb9a = DAT_febebcc2;
  DAT_febeeb9c = DAT_febebcd6;
  DAT_febeeb9e = ((int)(int16_t)DAT_febeae12);
  DAT_febeeb89 = DAT_febeacf1;
  DAT_febeeba0 = ((int)(int16_t)DAT_febeae58);
  DAT_febeeb8a = DAT_febead39;
  DAT_febeeba2 = ((int)(int16_t)DAT_febeae36);
  DAT_febeeb8b = DAT_febead0a;
  DAT_febeeb8c = DAT_febeacf5;
  DAT_febeeba4 = ((int)(int16_t)DAT_febeae16);
  DAT_febeeba6 = DAT_febeb11a;
  DAT_febeeb8d = DAT_febead93;
  DAT_febeeb8e = DAT_febebeb8;
  DAT_febeeb8f = source_coherence_history;
  DAT_febeeb90 = DAT_febeb1cd;
  DAT_febeeba8 = ((int)(int16_t)DAT_febeaecc);
  DAT_febeebaa = ((int)(int16_t)DAT_febeb38a);
  return;
}

void call_initialize_cold_control_retained_state_fdc00(void)

{
  initialize_cold_control_retained_state();
  return;
}

void call_initialize_control_application_work_state_fdc14(void)

{
  initialize_control_application_work_state();
  return;
}

void copy_cell_block_c1b24(void)

{
  DAT_febeaf50 = ((int)(int16_t)DAT_febeec04);
  DAT_febeaf52 = ((int)(int16_t)DAT_febeec06);
  DAT_febeaf54 = ((int)(int16_t)DAT_febeec08);
  DAT_febeaf56 = ((int)(int16_t)DAT_febeec0a);
  DAT_febeaf58 = ((int)(int16_t)DAT_febeec0c);
  DAT_febeaf60 = DAT_febeec14;
  DAT_febeaf64 = DAT_febeec18;
  DAT_febeaf68 = DAT_febeec1c;
  DAT_febeaf6c = DAT_febeec20;
  DAT_febeaf5a = ((int)(int16_t)DAT_febeec0e);
  DAT_febeaf70 = DAT_febeec24;
  DAT_febeaf4c = DAT_febeec00;
  DAT_febeaf4d = DAT_febeec01;
  DAT_febeaf4e = DAT_febeec02;
  DAT_febeaf5c = ((int)(int16_t)DAT_febeec10);
  return;
}

void call_snapshot_control_ch2_acquisition_fdc3c(void)

{
  snapshot_control_ch2_acquisition();
  return;
}

void call_snapshot_control_ch2_feedback_fdc50(void)

{
  snapshot_control_ch2_feedback();
  return;
}

void call_snapshot_control_foreground_acquisition_fdc64(void)

{
  snapshot_control_foreground_acquisition();
  return;
}

void call_snapshot_control_foreground_feedback_fdc78(void)

{
  snapshot_control_foreground_feedback();
  return;
}

void call_snapshot_health_and_service_inputs_fdc8c(void)

{
  snapshot_health_and_service_inputs();
  return;
}

void call_mode_transition_dispatch_with_service_substitution_fdcf0(undefined1 param_1,undefined2 param_2,undefined2 param_3)

{
  dispatch_service_substitution_on_mode_transition_c1f7a(param_1,param_2,param_3);
  return;
}

void call_mode_steady_dispatch_with_service_substitution_fdd04(undefined1 param_1,undefined2 param_2)

{
  dispatch_service_substitution_for_current_mode_c2000(param_1,param_2);
  return;
}

void call_mode_transition_dispatch_for_limit_and_assist_groups_fdd18(undefined1 param_1,undefined2 param_2,undefined2 param_3)

{
  dispatch_limit_publication_on_mode_transition_c2044(param_1,param_2,param_3);
  return;
}

void call_mode_steady_dispatch_for_limit_and_assist_groups_fdd2c(undefined1 param_1,undefined2 param_2)

{
  dispatch_limit_publication_for_current_mode_c20f6(param_1,param_2);
  return;
}

void call_control_foreground_transition_dispatch_fdd40(uint param_1,uint param_2,uint param_3)

{
  dispatch_control_foreground_transition(param_1 & 0xff,param_2 & 0xffff,param_3 & 0xffff);
  return;
}

void call_control_foreground_steady_dispatch_fdd54(uint param_1,uint param_2)

{
  dispatch_control_foreground_steady(param_1 & 0xff,param_2 & 0xffff);
  return;
}

void call_restart_application_at_mode100_fdd68(void)

{
  start_mode100_after_foreground_restart();
  return;
}

undefined2 thunk_vote_redundant_application_mode_u16_b1c64(void)

{
  return vote_redundant_application_mode_u16_b1c64();
}

void thunk_set_indexed_bef1_request_to_5a_bef80(undefined4 param_1)

{
  set_indexed_bef1_request_to_5a_bef80(param_1);
  return;
}

void thunk_clear_indexed_bef1_request_bef8e(undefined4 param_1)

{
  clear_indexed_bef1_request_bef8e(param_1);
  return;
}

uint thunk_clear_be28_be2a_and_write_zero_record11_bdcfe(void)

{
  return clear_be28_be2a_and_write_zero_record11_bdcfe();
}

uint thunk_clear_paired_snapshot_fields_and_write_zero_record15_bdf24(void)

{
  return clear_paired_snapshot_fields_and_write_zero_record15_bdf24();
}

void thunk_set_byte_febeaf47_b9320(undefined4 param_1)

{
  set_byte_febeaf47_b9320(param_1);
  return;
}

void snapshot_diagnostic_application(F33DiagnosticApplicationSample *output,ushort capture_kind)

{
  if (capture_kind == 4) {
    snapshot_diagnostic_application_kind4(output);
  }
  else if (capture_kind == 10) {
    snapshot_diagnostic_application_kind10(output);
  }
  else {
    snapshot_diagnostic_application_default(output);
  }
  return;
}

undefined4 thunk_coordinate_two_masked_requests_and_return_status_b90ca(undefined4 param_1, undefined4 param_2)

{
  return coordinate_two_masked_requests_and_return_status_b90ca(param_1, param_2);
}

void thunk_select_snapshot_packer_by_kind_ten_be1f8(undefined4 param_1, undefined4 param_2)

{
  select_snapshot_packer_by_kind_ten_be1f8(param_1, param_2);
  return;
}

void stage_record102_mode_write(uint encoded_mode)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  finish_pending_b324_capture_b72a2();
  stop_event_100_monitor_b6c14();
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x4ee))))) = 0x11;
  (*((uint *)camry_host_ptr((uint32_t)(puVar1 + -0x4e4)))) = encoded_mode;
  return;
}

void thunk_initialize_three_state_groups_and_b214_b524a(void)

{
  initialize_three_state_groups_and_b214_b524a();
  return;
}

undefined4 thunk_check_selected_pair_of_lifecycle_states_idle_b8d9c(undefined4 param_1)

{
  return check_selected_pair_of_lifecycle_states_idle_b8d9c(param_1);
}

void thunk_start_selected_b438_or_b439_lifecycle_group_b8dda(undefined4 param_1)

{
  start_selected_b438_or_b439_lifecycle_group_b8dda(param_1);
  return;
}

void thunk_start_b43a_lifecycle_group_and_clear_counter_b8e52(void)

{
  start_b43a_lifecycle_group_and_clear_counter_b8e52();
  return;
}

void latch_availability_override(void)

{
  DAT_febeb18f = 0x5a;
  return;
}

void latch_health_command_completion(void)

{
  DAT_febeb190 = 0x5a;
  return;
}

void set_owner2_entry_inhibit(uint inhibit)

{
  DAT_febebdb2 = (char)inhibit;
  return;
}

void set_owner3_entry_inhibit(uint inhibit)

{
  DAT_febebdaa = (char)inhibit;
  return;
}

void thunk_set_byte_febebdee_bc93a(undefined4 param_1)

{
  set_byte_febebdee_bc93a(param_1);
  return;
}

void set_owner4_limit_mode(uint mode)

{
  DAT_febebcbd = (char)mode;
  return;
}

void set_current_limit_request(uint owner,ushort limit)

{
  if ((owner & 0xff) < 10) {
    (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebebd34u + (uint32_t)(owner & 0xff) * 2u)))) = limit;
  }
  return;
}

undefined4 thunk_prepare_d113c_and_write_record9_configuration_bdb48(void)

{
  return prepare_d113c_and_write_record9_configuration_bdb48();
}

undefined4 thunk_set_indexed_request_and_clear_complement_b15ac(undefined4 param_1)

{
  return set_indexed_request_and_clear_complement_b15ac(param_1);
}
