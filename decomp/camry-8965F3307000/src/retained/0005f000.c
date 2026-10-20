#include "common.h"

void dispatch_diagnostic_services_mode_entry_5f464(uint param_1,ushort param_2,ushort param_3)

{
  if (0xff < param_2) {
    if (param_3 < 0x100) {
      clear_byte_febe8143_4bffa();
      run_init_chain_4c590();
      load_febe8190_counter_threshold_4c5f0();
      refresh_prioritized_status_and_copied_pair_4c784();
      return_only_stub_4c978();
      pack_channel0_status_fields_and_additive_checksum_4c97a();
      return_only_stub_4ce06();
      pack_four_change_sensitive_fields_for_channel2_4ce08();
      return_only_stub_4c7a8();
      pack_eight_status_bytes_for_channel3_4c7aa();
      return_only_stub_4cece();
      pack_status_and_override_bit_for_channel1_4ced0();
      return_only_stub_4c8de();
    }
    else {
      run_init_chain_4c590();
      refresh_prioritized_status_and_copied_pair_4c784();
      pack_channel0_status_fields_and_additive_checksum_4c97a();
      pack_four_change_sensitive_fields_for_channel2_4ce08();
      pack_eight_status_bytes_for_channel3_4c7aa();
      pack_status_and_override_bit_for_channel1_4ced0();
    }
    pack_constant_fields_for_channel4_4c8e0();
  }
  if (0x100 < param_2) {
    if (param_3 < 0x101) {
      initialize_mode600_latched_state_57e16();
    }
    update_mode600_four_state_output_latch_57e26();
  }
  if (0x102 < param_2) {
    if (param_3 < 0x103) {
      return_only_stub_56f30();
      report_event25_for_up_to_five_ring_samples_56f32();
      return_only_stub_56f2a();
      return_only_stub_56f2c();
      return_only_stub_56f8c();
      report_event27_and_count_status11_occurrences_56f8e();
      return_only_stub_57000();
      report_event28_once_for_any_crypto_profile_flag_57002();
      return_only_stub_567c8();
    }
    else {
      report_event25_for_up_to_five_ring_samples_56f32();
      return_only_stub_56f2c();
      report_event27_and_count_status11_occurrences_56f8e();
      report_event28_once_for_any_crypto_profile_flag_57002();
    }
    latch_event20_on_a55aa55a_status_567ca();
  }
  if (0x101 < param_2) {
    if (param_3 < 0x102) {
      restore_event_bitmaps_history_and_generation_from_nvm_51e8a();
      service_diagnostic_record_transaction();
      restore_three_nvm_capture_slots_and_validity_bytes_52ad4();
      run_init_chain_52de4();
      return_only_stub_54240();
      return_only_stub_54242();
      restore_eighteen_counters_and_ten_values_from_nvm4_54488();
      flush_dirty_counter_record4_and_poll_completion_54566();
      restore_twelve_counters_and_three_records_from_nvm14_54746();
      if ((param_1 & 0x10) != 0) {
        capture_rising_counter_latches_and_persist_records_549c8();
      }
      restore_dual_capture_records_and_select_newer_generation_54ce2();
      poll_and_flush_capture_record_persistence_551bc();
      return_only_stub_564ca();
      return_only_stub_564cc();
      copy_three_classifier_age_thresholds_50fae();
      if ((param_1 >> 1 & 1) != 0) {
        update_diagnostic_classifier_output();
      }
      reset_four_slot_diagnostic_operation_queue_51612();
      service_diagnostic_request_lifecycle();
      reset_eventcc_report_latch_56fc8();
      report_eventcc_once_on_6a150_flag_56fce();
      return_only_stub_56756();
    }
    else {
      service_diagnostic_record_transaction();
      run_init_chain_52de4();
      return_only_stub_54242();
      flush_dirty_counter_record4_and_poll_completion_54566();
      if ((param_1 & 0x10) != 0) {
        capture_rising_counter_latches_and_persist_records_549c8();
      }
      poll_and_flush_capture_record_persistence_551bc();
      return_only_stub_564cc();
      if ((param_1 >> 1 & 1) != 0) {
        update_diagnostic_classifier_output();
      }
      service_diagnostic_request_lifecycle();
      report_eventcc_once_on_6a150_flag_56fce();
    }
    report_events_94_and_93_from_status_bits_56758();
  }
  if (0x102 < param_2) {
    if (param_3 < 0x103) {
      return_only_stub_57056();
    }
    consume_5aa5_aa55_status_and_update_count_57058();
  }
  if (param_2 == 0x702) {
    if (param_3 != 0x702) {
      return_only_stub_567a4();
    }
    dispatch_service28_when_application_nvm_ready_567a6();
  }
  if (0x8ff < param_2) {
    if (param_3 < 0x900) {
      reset_timed_reinitialization_counter_56cf0();
    }
    run_timed_reinitialization_and_send_7f1010_56cf6();
  }
  publish_foreground_ecu_outputs();
  return;
}

void dispatch_monitor_learning_thermal_mode_step_5f610(uint param_1,uint param_2)

{
  uint uVar1;
  
  param_2 = param_2 & 0xffff;
  if (0xff < param_2) {
    snapshot_local_status_link_flags();
  }
  if (param_2 == 0x101) {
    dispatch_service12_when_66f10_returns_zero_5678a();
  }
  if (0xff < param_2) {
    refresh_diagnostic_application_availability();
    combine_and_publish_monitor_inhibit_sources_49e22();
    reconcile_application_normal_network_policy();
    update_internal_source_admission_lifecycle();
    update_application_receive_statuses();
    decode_receive_slot_1_u16_and_u32_fields_4ae72();
    decode_receive_slot_2_byte_and_three_nibbles_4aed6();
    decode_receive_slot_3_two_byte_fields_4af6c();
    decode_receive_slot_5_three_bit_and_single_bit_fields_4afec();
    decode_receive_slot_8_signed16_and_flag_4b12e();
    decode_receive_slot_10_signed16_field_4b1f6();
    decode_receive_slot_11_ten_packed_fields_4b242();
    refresh_route30_health_inputs();
    decode_receive_slot_13_twobit_and_u32_fields_4b40e();
    decode_receive_slot_14_two_single_bit_fields_4b472();
    decode_receive_slot_17_three_signed_fields_and_four_flags_4b59e();
    decode_receive_slot_18_four_biased_u15_values_and_flags_4b68a();
    decode_receive_slot_19_three_flags_and_tenbit_field_4b7d6();
    decode_changed_rx14_two_signed_words_and_flag_4b86e();
    decode_changed_rx15_eight_bitfields_4b8f4();
    decode_changed_rx16_three_ten_bit_values_and_flags_4b9f4();
    decode_changed_rx17_two_words_and_flags_4bb62();
    decode_changed_rx18_four_bytes_4bc28();
    decode_changed_rx19_two_signed_eighteen_bit_fields_4bcc0();
    decode_changed_rx1a_word_bytes_and_flags_4bd46();
    decode_changed_rx1b_three_bytes_4bed0();
    decode_changed_rx1c_three_and_four_bit_fields_4bf4e();
    decode_changed_rx1d_low_nibble_4bfb2();
    decode_receive_slot_6_two_single_bit_fields_4b04e();
    decode_receive_slot_7_signed11_sixbit_and_flag_4b0b0();
    decode_receive_slot_15_six_byte_fields_4b4d4();
    decode_receive_slot_0_byte_field_4ae2a();
    decode_receive_slot_9_byte_and_flag_4b194();
    step_change_triggered_monitor_and_encode_status_4aae8();
    dispatch_route30_codeword_timeout_monitors_4a702();
    dispatch_eight_codeword_timeout_monitors_4aa5c();
    delay_then_update_two_expiring_latches_4ada2();
    initialize_and_update_communication_inhibits_4a49e();
    pack_four_source_bytes_equal_to_one_4adce();
    scale_word_80b0_with_sentinel_to_signed_halfword_4abbe();
    step_latched_monitor_and_record_failing_side_4ac28();
    refresh_diagnostic_admission_and_dispatch_pending_request_4d094();
    clamp_sample_8048_and_compute_enable_gate_47ae0();
    lookup_low_nibble_code_or_zero_47ac4();
  }
  if (0x102 < param_2) {
    if ((param_1 >> 4 & 1) != 0) {
      update_thermistor_channels();
      poll_record5_write_state_483bc();
    }
    if (param_2 < 0x523) {
      update_qualified_local_status_monitor();
      update_paired_local_status_monitor();
      update_individual_local_status_a();
      update_individual_local_status_b();
    }
    publish_local_status_link_fault();
  }
  uVar1 = param_2 - 0x200;
  if (uVar1 < 0x323) {
    update_gated_latched_monitor_a_eleven_42a6a();
    update_gated_latched_monitor_b_eleven_43a2c();
    step_local_channel_mismatch_a_monitor();
    step_local_output_status_a_monitor();
    step_local_channel_mismatch_b_monitor();
    step_local_output_status_b_monitor();
  }
  if (uVar1 < 0xe) {
    if (param_2 == 0x200) {
      step_sample_difference_window_a();
      step_sample_difference_window_b();
    }
    if (param_2 == 0x201) {
      step_bounded_sample_or_status_a();
      step_bounded_sample_or_status_b();
    }
    if (param_2 == 0x202) {
      step_baseline_sample_threshold_a();
      step_baseline_sample_threshold_b();
    }
    if (param_2 == 0x203) {
      step_requested_state_sample_threshold_a();
      step_requested_state_sample_threshold_b();
    }
    if (param_2 == 0x204) {
      step_startup_status_bit_triplet_a();
      step_startup_status_bit_triplet_b();
    }
    if (param_2 == 0x205) {
      step_delayed_status_bit_triplet_a();
      step_delayed_status_bit_triplet_b();
    }
    if (param_2 == 0x206) {
      step_command_status_bit_clear_a();
      step_command_status_bit_clear_b();
    }
    if (param_2 == 0x207) {
      step_observed_state_sample_regions_a();
      step_observed_state_sample_regions_b();
    }
    if (param_2 == 0x208) {
      step_coupled_sample_threshold_both();
    }
    if (param_2 == 0x209) {
      step_asserted_state_sample_threshold_a();
      step_asserted_state_sample_threshold_b();
    }
    if (param_2 == 0x20a) {
      step_matched_state2_status_bit_a();
      step_matched_state2_status_bit_b();
    }
    if (param_2 == 0x20b) {
      step_sample_range_triplet_a();
      step_sample_range_triplet_b();
    }
    if (param_2 == 0x20c) {
      step_matched_state2_startup_triplet_a();
      step_matched_state2_startup_triplet_b();
    }
    if (param_2 == 0x20d) {
      step_matched_state2_status_bit_triplet_a();
      step_matched_state2_status_bit_triplet_b();
    }
    if (uVar1 < 0xe) {
      publish_monitor_failure_count_summary_wrapper_3efd4();
    }
  }
  if (param_2 - 0x301 < 0x222) {
    if ((param_1 >> 3 & 1) != 0) {
      step_paired_scalar_relation_monitor();
      step_qualified_scalar_relation_a_monitor();
      step_qualified_scalar_relation_b_monitor();
      step_admitted_scalar_receive_condition_monitor();
    }
    publish_scalar_relation_monitor_actions();
  }
  if (0x102 < param_2) {
    update_communication_qualification_monitors();
    publish_selected_source_fault_edges();
    publish_source_family_fault_edges();
    report_6879_687a_fault_transitions_and_comm_status_3d54e();
    update_received_content_monitor_a();
    update_received_content_monitor_b();
    compose_communication_status_fault_actions();
    if ((param_1 >> 4 & 1) != 0) {
      step_raw_thermistor_range_a_monitor();
      step_raw_thermistor_range_b_monitor();
      publish_thermistor_range_monitor_actions();
      if (param_2 < 0x103) goto LAB_0005f87a;
    }
    poll_ba_retained_start();
    run_5f6a_counter_update_35c38();
    check_paired_counters_and_clear_pending_flags_35b78();
    refresh_monitor_current_calibration();
    refresh_both_requested_record_halfword_channels_32580();
    service_fit_revalidation_and_status_countdown_347e2();
    step_learned_quad_record_completion();
  }
LAB_0005f87a:
  if (param_2 == 0x512) {
    step_fit_completion();
  }
  if (param_2 == 0x600) {
    step_mode600_fit_request();
    step_fit_completion();
  }
  if (param_2 - 0x101 < 0x10d) {
    request_published_mode200_phase();
  }
  if ((0x700 < param_2) && ((param_1 >> 3 & 1) != 0)) {
    step_thermal_shutdown_request();
  }
  if (0x1ff < param_2) {
    update_signed_pair_threshold_countdown_360e0();
    param_1 = param_1 & 0x10;
    if (param_1 != 0) {
      run_init_chain_3b398();
      restore_and_step_dual_thermal_offset_state_3b88e();
      update_thermal_drive_epoch_maxima();
      update_scaled_pair_sums_and_thermal_squared_inputs_3984a();
      update_ecu_source2_thermal_estimate();
      publish_ecu_source2_thermal_limit_maps();
      update_ecu_source4_thermal_estimate();
      publish_ecu_source4_thermal_limit_maps();
      if (param_1 != 0) {
        update_ecu_source5_thermal_estimate();
        publish_ecu_source5_thermal_limit_maps();
        update_ecu_source3_thermal_estimate();
        publish_ecu_source3_thermal_limit_maps();
      }
    }
    poll_thermal_history_record_status();
    if (param_1 != 0) {
      update_motor_thermal_estimate();
      publish_motor_thermal_limit_maps();
    }
    arbitrate_thermal_current_limits();
    if (param_1 != 0) {
      reset_or_step_704c_latched_monitor_3b478();
      reset_or_step_7040_latched_monitor_3b3d0();
      update_thermal_history_qualification();
    }
  }
  publish_foreground_ecu_outputs();
  return;
}

void dispatch_diagnostic_services_mode_step_5f91c(uint param_1,ushort param_2)

{
  if (0xff < param_2) {
    run_init_chain_4c590();
    refresh_prioritized_status_and_copied_pair_4c784();
    pack_channel0_status_fields_and_additive_checksum_4c97a();
    pack_four_change_sensitive_fields_for_channel2_4ce08();
    pack_eight_status_bytes_for_channel3_4c7aa();
    pack_status_and_override_bit_for_channel1_4ced0();
    pack_constant_fields_for_channel4_4c8e0();
  }
  if (0x100 < param_2) {
    update_mode600_four_state_output_latch_57e26();
  }
  if (0x102 < param_2) {
    report_event25_for_up_to_five_ring_samples_56f32();
    return_only_stub_56f2c();
    report_event27_and_count_status11_occurrences_56f8e();
    report_event28_once_for_any_crypto_profile_flag_57002();
    latch_event20_on_a55aa55a_status_567ca();
  }
  if (0x101 < param_2) {
    service_diagnostic_record_transaction();
    run_init_chain_52de4();
    return_only_stub_54242();
    flush_dirty_counter_record4_and_poll_completion_54566();
    if ((param_1 >> 4 & 1) != 0) {
      capture_rising_counter_latches_and_persist_records_549c8();
    }
    poll_and_flush_capture_record_persistence_551bc();
    return_only_stub_564cc();
    if ((param_1 >> 1 & 1) != 0) {
      update_diagnostic_classifier_output();
    }
    service_diagnostic_request_lifecycle();
    report_eventcc_once_on_6a150_flag_56fce();
    report_events_94_and_93_from_status_bits_56758();
  }
  if (0x102 < param_2) {
    consume_5aa5_aa55_status_and_update_count_57058();
  }
  if (param_2 == 0x702) {
    dispatch_service28_when_application_nvm_ready_567a6();
  }
  if (0x8ff < param_2) {
    run_timed_reinitialization_and_send_7f1010_56cf6();
  }
  publish_foreground_ecu_outputs();
  return;
}

void dispatch_capture_processing_by_status_low2_5f9ce(void)

{
  switch(DAT_febe39da & 3) {
  case 0:
    disable_dma_and_restore_channel_modes_60a10();
    rearm_both_capture_registers_and_dma_reload_60c20();
    break;
  case 1:
    check_repair_adc_scan_configuration_and_refresh_dma_60462();
    break;
  case 2:
    write_two_rom_selected_output_pin_masks_61f96();
    refresh_phase_timer_span_and_dma_reload_61b90();
    write_two_channel_output_pin_masks_62018();
    break;
  case 3:
    restore_serial_pin_mux_under_priority_mask_612dc();
    restore_serial_acquisition_pin_mux_and_dma_reload_628b2();
  }
  return;
}

void run_init_chain_5fa12(void)

{
  enable_dma_and_reset_sixteen_channel_controls_607d0();
  write_configured_output_port_level_b(0);
  write_configured_output_port_level_b(1);
  restore_paired_port_mask_upper_words_61eb8();
  write_channel_requested_level(0);
  write_channel_requested_level(1);
  return;
}

void clear_adc0_sample_rings_and_indices_5fa3a(void)

{
  int iVar1;
  uint uVar2;
  
  uVar2 = 0;
  DAT_feef90e0 = 0;
  do {
    iVar1 = uVar2 * 4;
    uVar2 = uVar2 + 1;
    *(undefined4 *)(((undefined *)camry_host_ptr((uint32_t)(0xfeef80a0u + (uint32_t)(iVar1) * 1u)))) = 0;
  } while (uVar2 < 0x50);
  uVar2 = 0;
  DAT_feef90e4 = 0;
  do {
    iVar1 = uVar2 * 4;
    uVar2 = uVar2 + 1;
    (*((undefined4 *)camry_host_ptr((uint32_t)((0xfeef81e0u) + iVar1)))) = 0;
  } while (uVar2 < 0x1b0);
  DAT_feef90e8 = 0;
  return;
}

void clear_adc1_sample_rings_and_indices_5fa84(void)

{
  int iVar1;
  uint uVar2;
  
  uVar2 = 0;
  DAT_feef90ec = 0;
  do {
    iVar1 = uVar2 * 4;
    uVar2 = uVar2 + 1;
    *(undefined4 *)(((undefined *)camry_host_ptr((uint32_t)(0xfeef88a0u + (uint32_t)(iVar1) * 1u)))) = 0;
  } while (uVar2 < 0x60);
  uVar2 = 0;
  DAT_feef90f0 = 0;
  do {
    iVar1 = uVar2 * 4;
    uVar2 = uVar2 + 1;
    (*((undefined4 *)camry_host_ptr((uint32_t)((0xfeef8a20u) + iVar1)))) = 0;
  } while (uVar2 < 0x1b0);
  DAT_feef90f4 = 0;
  return;
}

void reset_adc_sample_rings_and_check_counters_5face(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  clear_adc0_sample_rings_and_indices_5fa3a();
  clear_adc1_sample_rings_and_indices_5fa84();
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x7ff6))))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x7ff5))))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x7ffa))))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x7ff9))))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x7ff8))))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x7ff7))))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x7ffc))))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x7ffb))))) = 0;
  return;
}

void fill_constant_block_5fafe(void)

{
  DAT_fff89110 = 2;
  DAT_fff91340 = 0;
  DAT_fff92340 = 0;
  DAT_fff91384 = 2;
  DAT_fff92384 = 2;
  DAT_fff91398 = 1;
  DAT_fff92398 = 1;
  DAT_fff913c0 = 0x10;
  DAT_fff923c0 = 0x10;
  DAT_fff913c8 = 4;
  DAT_fff923c8 = 4;
  DAT_fff91800 = 0xfff;
  DAT_fff92800 = 0xfff;
  return;
}

void trigger_paired_conversion_and_poll_busy_5fb52(void)

{
  char cVar1;
  ushort uVar2;
  
  uVar2 = 0;
  DAT_fff91480 = 1;
  DAT_fff92480 = 1;
  for (; ((cVar1 = DAT_fff914a4, cVar1 != '\0' || (cVar1 = DAT_fff924a4, cVar1 != '\0')) &&
         (uVar2 < DAT_00030f24)); uVar2 = uVar2 + 1) {
    spin_wait(1);
  }
  return;
}

int check_adc_parity_channels_above_threshold_5fb96(uint param_1)

{
  bool bVar1;
  byte bVar2;
  int iVar3;
  undefined8 uVar4;
  uint uVar5;
  uint uVar6;
  int iVar7;
  int iVar8;
  int iVar9;
  byte bVar10;
  
  bVar2 = DAT_00030f3e;
  uVar4 = 0xfebeb800;
  param_1 = param_1 & 0xff;
  iVar8 = 0x5a;
  uVar6 = (uint)DAT_00030f28;
  bVar10 = 0;
  iVar7 = iVar8;
  iVar9 = iVar8;
  if (param_1 < 2) {
    do {
      iVar3 = (int)uVar4;
      if (bVar2 <= bVar10) break;
      trigger_paired_conversion_and_poll_busy_5fb52();
      iVar3 = (int)uVar4;
      bVar1 = iVar8 != 0;
      iVar8 = 0;
      if (bVar1) {
        for (uVar5 = 0; (int)(param_1 + uVar5 + -9) < 0; uVar5 = uVar5 + 2 & 0xff) {
          if (((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xfff91200u + (uint32_t)(param_1 + uVar5) * 4u)))) & 0x7ff8) * 2 < uVar6) {
            iVar8 = 0x5a;
          }
        }
      }
      bVar1 = iVar7 != 0;
      iVar7 = 0;
      if (bVar1) {
        for (uVar5 = 0; (int)(param_1 + uVar5 + -10) < 0; uVar5 = uVar5 + 2 & 0xff) {
          if (((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xfff92200u + (uint32_t)(param_1 + uVar5) * 4u)))) & 0x7ff8) * 2 < uVar6) {
            iVar7 = 0x5a;
          }
        }
      }
      if ((iVar8 == 0) && (iVar7 == 0)) {
        iVar9 = 0;
      }
      bVar10 = bVar10 + 1;
    } while (iVar9 != 0);
    (*((byte *)camry_host_ptr((uint32_t)(param_1 + iVar3 + -0x7ffc)))) = bVar10;
    iVar8 = iVar9;
  }
  return iVar8;
}

void set_odd_adc_channel_bit16_test_mode_5fc3c(void)

{
  int iVar1;
  uint uVar2;
  
  DAT_fff913c8 = 0x80000004;
  DAT_fff923c8 = 0x80000004;
  uVar2 = 0;
  do {
    iVar1 = uVar2 * 4;
    uVar2 = uVar2 + 2 & 0xff;
    *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0xfff91004u + (uint32_t)(iVar1) * 1u)))) = *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0xfff91004u + (uint32_t)(iVar1) * 1u)))) | 0x10000;
  } while ((int)(uVar2 - 8) < 0);
  uVar2 = 0;
  do {
    iVar1 = uVar2 * 4;
    uVar2 = uVar2 + 2 & 0xff;
    *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0xfff92004u + (uint32_t)(iVar1) * 1u)))) = *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0xfff92004u + (uint32_t)(iVar1) * 1u)))) | 0x10000;
  } while ((int)(uVar2 - 9) < 0);
  return;
}

int check_odd_adc_channels_below_threshold_5fc94(void)

{
  bool bVar1;
  byte bVar2;
  uint uVar3;
  int iVar4;
  undefined8 uVar5;
  uint uVar6;
  int iVar7;
  int iVar8;
  int iVar9;
  byte bVar10;
  
  bVar2 = DAT_00030f3d;
  uVar5 = 0xfebeb800;
  iVar8 = 0x5a;
  uVar6 = (uint)DAT_00030f26;
  bVar10 = 0;
  iVar7 = iVar8;
  iVar9 = iVar8;
  do {
    iVar4 = (int)uVar5;
    if (bVar2 <= bVar10) break;
    trigger_paired_conversion_and_poll_busy_5fb52();
    iVar4 = (int)uVar5;
    bVar1 = iVar8 != 0;
    iVar8 = 0;
    if (bVar1) {
      uVar3 = 0;
      do {
        if (uVar6 < (*(uint *)(((undefined *)camry_host_ptr((uint32_t)(0xfff91204u + (uint32_t)(uVar3 * 4) * 1u)))) & 0x7ff8) * 2) {
          iVar8 = 0x5a;
        }
        uVar3 = uVar3 + 2 & 0xff;
      } while ((int)(uVar3 - 8) < 0);
    }
    bVar1 = iVar7 != 0;
    iVar7 = 0;
    if (bVar1) {
      uVar3 = 0;
      do {
        if (uVar6 < (*(uint *)(((undefined *)camry_host_ptr((uint32_t)(0xfff92204u + (uint32_t)(uVar3 * 4) * 1u)))) & 0x7ff8) * 2) {
          iVar7 = 0x5a;
        }
        uVar3 = uVar3 + 2 & 0xff;
      } while ((int)(uVar3 - 9) < 0);
    }
    if ((iVar8 == 0) && (iVar7 == 0)) {
      iVar9 = 0;
    }
    bVar10 = bVar10 + 1;
  } while (iVar9 != 0);
  (*((byte *)camry_host_ptr((uint32_t)(iVar4 + -0x7ff7)))) = bVar10;
  return iVar9;
}

void clear_adc_channel_test_bits_5fd2e(void)

{
  int iVar1;
  uint uVar2;
  
  DAT_fff913c8 = 4;
  DAT_fff923c8 = 4;
  DAT_fff913c4 = 0;
  uVar2 = 0;
  DAT_fff923c4 = 0;
  do {
    iVar1 = uVar2 * 4;
    uVar2 = uVar2 + 1;
    *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0xfff91000u + (uint32_t)(iVar1) * 1u)))) = *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0xfff91000u + (uint32_t)(iVar1) * 1u)))) & 0xfffcffff;
  } while (uVar2 < 9);
  uVar2 = 0;
  do {
    iVar1 = uVar2 * 4;
    uVar2 = uVar2 + 1;
    *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0xfff92000u + (uint32_t)(iVar1) * 1u)))) = *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0xfff92000u + (uint32_t)(iVar1) * 1u)))) & 0xfffcffff;
  } while (uVar2 < 10);
  return;
}

int run_odd_adc_channel_threshold_checks_5fd82(void)

{


  byte bVar1;
  int iVar2;
  undefined8 uVar3;
  int iVar4;
  int iVar5;
  byte bVar6;
  
  bVar1 = DAT_00030f3c;
  uVar3 = 0xfebeb800;
  bVar6 = 0;
  iVar5 = 0x5a;
  do {
    iVar2 = (int)uVar3;
    if (bVar1 <= bVar6) break;
    DAT_fff913c4 = 0x80;
    DAT_fff923c4 = 0x80;
    iVar5 = check_adc_parity_channels_above_threshold_5fb96(1);
    if (iVar5 == 0) {
      set_odd_adc_channel_bit16_test_mode_5fc3c();
      iVar5 = check_odd_adc_channels_below_threshold_5fc94();
      if (iVar5 != 0) goto LAB_0005fdc2;
    }
    else {
LAB_0005fdc2:
      bVar6 = bVar6 + 1;
    }
    iVar4 = (clear_adc_channel_test_bits_5fd2e(), (int)(uintptr_t)iVar5);
    iVar2 = (int)uVar3;
  } while (iVar4 != 0);
  (*((byte *)camry_host_ptr((uint32_t)(iVar2 + -0x7ffa)))) = bVar6;
  return iVar5;
}

void set_even_adc_channel_bit16_test_mode_5fdd8(void)

{
  int iVar1;
  uint uVar2;
  
  DAT_fff913c8 = 0x80000004;
  DAT_fff923c8 = 0x80000004;
  uVar2 = 0;
  do {
    iVar1 = uVar2 * 4;
    uVar2 = uVar2 + 2;
    *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0xfff91000u + (uint32_t)(iVar1) * 1u)))) = *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0xfff91000u + (uint32_t)(iVar1) * 1u)))) | 0x10000;
  } while (uVar2 < 9);
  uVar2 = 0;
  do {
    iVar1 = uVar2 * 4;
    uVar2 = uVar2 + 2;
    *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0xfff92000u + (uint32_t)(iVar1) * 1u)))) = *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0xfff92000u + (uint32_t)(iVar1) * 1u)))) | 0x10000;
  } while (uVar2 < 10);
  return;
}

int check_even_adc_channels_below_threshold_5fe24(void)

{
  bool bVar1;
  byte bVar2;
  int iVar3;
  undefined8 uVar4;
  uint uVar5;
  uint uVar6;
  int iVar7;
  int iVar8;
  int iVar9;
  byte bVar10;
  
  bVar2 = DAT_00030f3d;
  uVar4 = 0xfebeb800;
  iVar8 = 0x5a;
  uVar6 = (uint)DAT_00030f26;
  bVar10 = 0;
  iVar7 = iVar8;
  iVar9 = iVar8;
  do {
    iVar3 = (int)uVar4;
    if (bVar2 <= bVar10) break;
    trigger_paired_conversion_and_poll_busy_5fb52();
    iVar3 = (int)uVar4;
    bVar1 = iVar8 != 0;
    iVar8 = 0;
    if (bVar1) {
      uVar5 = 0;
      do {
        if (uVar6 < ((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xfff91200u + (uint32_t)(uVar5) * 4u)))) & 0x7ff8) * 2) {
          iVar8 = 0x5a;
        }
        uVar5 = uVar5 + 2;
      } while (uVar5 < 9);
    }
    bVar1 = iVar7 != 0;
    iVar7 = 0;
    if (bVar1) {
      uVar5 = 0;
      do {
        if (uVar6 < ((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xfff92200u + (uint32_t)(uVar5) * 4u)))) & 0x7ff8) * 2) {
          iVar7 = 0x5a;
        }
        uVar5 = uVar5 + 2;
      } while (uVar5 < 10);
    }
    if ((iVar8 == 0) && (iVar7 == 0)) {
      iVar9 = 0;
    }
    bVar10 = bVar10 + 1;
  } while (iVar9 != 0);
  (*((byte *)camry_host_ptr((uint32_t)(iVar3 + -0x7ff8)))) = bVar10;
  return iVar9;
}

int run_even_adc_channel_threshold_checks_5feb2(void)

{


  byte bVar1;
  int iVar2;
  undefined8 uVar3;
  int iVar4;
  int iVar5;
  byte bVar6;
  
  bVar1 = DAT_00030f3c;
  uVar3 = 0xfebeb800;
  bVar6 = 0;
  iVar5 = 0x5a;
  do {
    iVar2 = (int)uVar3;
    if (bVar1 <= bVar6) break;
    DAT_fff913c4 = 0x81;
    DAT_fff923c4 = 0x81;
    iVar5 = check_adc_parity_channels_above_threshold_5fb96(0);
    if (iVar5 == 0) {
      set_even_adc_channel_bit16_test_mode_5fdd8();
      iVar5 = check_even_adc_channels_below_threshold_5fe24();
      if (iVar5 != 0) goto LAB_0005fef2;
    }
    else {
LAB_0005fef2:
      bVar6 = bVar6 + 1;
    }
    iVar4 = (clear_adc_channel_test_bits_5fd2e(), (int)(uintptr_t)iVar5);
    iVar2 = (int)uVar3;
  } while (iVar4 != 0);
  (*((byte *)camry_host_ptr((uint32_t)(iVar2 + -0x7ff9)))) = bVar6;
  return iVar5;
}

void configure_adc_channels_and_run_threshold_checks_5ff08(void)

{
  uint uVar1;
  int iVar2;
  int iVar3;
  
  uVar1 = 0;
  do {
    iVar2 = uVar1 * 4;
    uVar1 = uVar1 + 1;
    *(undefined4 *)(((undefined *)camry_host_ptr((uint32_t)(0xfff91000u + (uint32_t)(iVar2) * 1u)))) = *(undefined4 *)(((undefined *)camry_host_ptr((uint32_t)(0x30f74u + (uint32_t)(iVar2) * 1u))));
  } while (uVar1 < 9);
  uVar1 = 0;
  do {
    iVar2 = uVar1 * 4;
    uVar1 = uVar1 + 1;
    *(undefined4 *)(((undefined *)camry_host_ptr((uint32_t)(0xfff92000u + (uint32_t)(iVar2) * 1u)))) = *(undefined4 *)(((undefined *)camry_host_ptr((uint32_t)(0x30f4cu + (uint32_t)(iVar2) * 1u))));
  } while (uVar1 < 10);
  DAT_fff91494 = 0;
  DAT_fff92494 = 0;
  DAT_fff91498 = 8;
  DAT_fff92498 = 9;
  DAT_fff9149c = 0;
  DAT_fff9249c = 0;
  DAT_fff91490 = 0;
  DAT_fff92490 = 0;
  iVar2 = run_odd_adc_channel_threshold_checks_5fd82();
  iVar3 = run_even_adc_channel_threshold_checks_5feb2();
  if ((iVar2 == 0) && (iVar3 == 0)) {
    DAT_fff913d8 = 4;
    DAT_fff923d8 = 4;
    return;
  }
                    /* WARNING: Subroutine does not return */
  enter_terminal_hardware_sequence();
}

void load_adc_scan_group_configuration_5ff98(void)

{
  int iVar1;
  int iVar2;
  uint uVar3;
  
  uVar3 = 0;
  do {
    iVar1 = uVar3 * 4;
    uVar3 = uVar3 + 1;
    *(undefined4 *)(((undefined *)camry_host_ptr((uint32_t)(0xfff91000u + (uint32_t)(iVar1) * 1u)))) = *(undefined4 *)(((undefined *)camry_host_ptr((uint32_t)(0x30f98u + (uint32_t)(iVar1) * 1u))));
    *(undefined4 *)(((undefined *)camry_host_ptr((uint32_t)(0xfff92000u + (uint32_t)(iVar1) * 1u)))) = *(undefined4 *)(((undefined *)camry_host_ptr((uint32_t)(0x30ff8u + (uint32_t)(iVar1) * 1u))));
  } while (uVar3 < 0x18);
  DAT_fff913c8 = 4;
  DAT_fff923c8 = 4;
  uVar3 = 0;
  do {
    iVar1 = uVar3 * 8;
    iVar2 = uVar3 * 0x80;
    uVar3 = uVar3 + 1;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfff91494u + (uint32_t)(iVar2) * 1u)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x31059u + (uint32_t)(iVar1) * 1u))));
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfff92494u + (uint32_t)(iVar2) * 1u)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x31081u + (uint32_t)(iVar1) * 1u))));
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfff91498u + (uint32_t)(iVar2) * 1u)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x3105au + (uint32_t)(iVar1) * 1u))));
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfff92498u + (uint32_t)(iVar2) * 1u)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x31082u + (uint32_t)(iVar1) * 1u))));
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfff9149cu + (uint32_t)(iVar2) * 1u)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x31058u + (uint32_t)(iVar1) * 1u))));
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfff9249cu + (uint32_t)(iVar2) * 1u)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x31080u + (uint32_t)(iVar1) * 1u))));
  } while (uVar3 < 5);
  DAT_fff91408 = 0;
  DAT_fff92408 = 0;
  DAT_fff91434 = 0;
  DAT_fff92434 = 0;
  DAT_fff91430 = 0x1a;
  DAT_fff92430 = 0xe;
  uVar3 = 0;
  do {
    iVar1 = uVar3 * 8;
    iVar2 = uVar3 * 0x80;
    uVar3 = uVar3 + 1;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfff91490u + (uint32_t)(iVar2) * 1u)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x3105bu + (uint32_t)(iVar1) * 1u))));
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfff92490u + (uint32_t)(iVar2) * 1u)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x31083u + (uint32_t)(iVar1) * 1u))));
  } while (uVar3 < 5);
  DAT_fff91420 = 0x32;
  DAT_fff92420 = 0x32;
  DAT_fff91424 = 0;
  DAT_fff92424 = 0;
  return;
}
