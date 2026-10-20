#include "common.h"

void dispatch_service_substitution_for_current_mode_c2000(undefined4 param_1,uint param_2)

{
  param_2 = param_2 & 0xffff;
  if (0x102 < param_2) {
    publish_inverted_62e12_result_b7374();
  }
  if (param_2 - 0x300 < 0x223) {
    refresh_derived_and_copied_ac_snapshot_then_d1100_bcd02();
  }
  if (param_2 == 0x520) {
    refresh_b42c_correction_when_b431_and_ed00_ready_b8af0();
    refresh_b3c4_correction_when_b3a1_and_ed00_ready_b7a9e();
    publish_service_engine_substitution();
  }
  if (0x101 < param_2) {
    return_only_stub_be06e();
  }
  fill_constant_block_bf33e();
  return;
}

void dispatch_limit_publication_on_mode_transition_c2044(undefined4 param_1,uint param_2,uint param_3)

{
  param_3 = param_3 & 0xffff;
  param_2 = param_2 & 0xffff;
  if (0x102 < param_2) {
    if (param_3 < 0x103) {
      return_only_stub_bdb96();
    }
    clear_four_bytes_febebe20_to_be23_bdb98();
  }
  if (param_2 - 0x200 < 0x323) {
    if (param_3 - 0x200 < 0x323) {
      publish_owner2_deficit_limit_request();
    }
    else {
      reset_owner2_deficit_request();
      publish_owner2_deficit_limit_request();
      return_only_stub_bc5fc();
    }
    latch_bddc_after_any_selected_failure_flag_bc5fe();
  }
  if (0x1ff < param_2) {
    if (param_3 < 0x200) {
      reset_owner1_limit_request();
      publish_owner1_limit_request();
      return_only_stub_bb7f8();
    }
    else {
      publish_owner1_limit_request();
    }
    publish_other_current_limit();
  }
  if (param_2 - 0x300 < 0x223) {
    if (0x222 < param_3 - 0x300) {
      thunk_initialize_observer_and_waveform_state_chains_d0bda();
    }
    run_init_chain_bca62();
  }
  if (0x101 < param_2) {
    if (param_3 < 0x102) {
      return_only_stub_bdfa8();
      return_only_stub_bdfaa();
      return_only_stub_be212();
    }
    else {
      return_only_stub_bdfaa();
    }
    return_only_stub_be214();
  }
  fill_constant_block_bf2f8();
  return;
}

void dispatch_limit_publication_for_current_mode_c20f6(undefined4 param_1,uint param_2)

{
  param_2 = param_2 & 0xffff;
  if (0x102 < param_2) {
    clear_four_bytes_febebe20_to_be23_bdb98();
  }
  if (param_2 - 0x200 < 0x323) {
    publish_owner2_deficit_limit_request();
    latch_bddc_after_any_selected_failure_flag_bc5fe();
  }
  if (0x1ff < param_2) {
    publish_owner1_limit_request();
    publish_other_current_limit();
  }
  if (param_2 - 0x300 < 0x223) {
    run_init_chain_bca62();
  }
  if (0x101 < param_2) {
    return_only_stub_bdfaa();
    return_only_stub_be214();
  }
  fill_constant_block_bf2f8();
  return;
}

void dispatch_control_foreground_transition
               (uint cadence_mask,uint captured_mode,uint previous_mode)

{
  uint uVar1;
  uint uVar2;
  uint uVar3;
  
  uVar2 = captured_mode & 0xffff;
  uVar3 = previous_mode & 0xffff;
  if (0xff < uVar2) {
    if (uVar3 < 0x100) {
      return_only_stub_be324();
      condition_staged_offset_scalar();
      return_only_stub_be302();
    }
    else {
      condition_staged_offset_scalar();
    }
    scale_staged_byte_pair_to_control_raw();
  }
  if (0x100 < uVar2) {
    if (uVar3 < 0x101) {
      return_only_stub_bea54();
      update_delayed_received_startup_qualification();
      return_only_stub_bf0a8();
    }
    else {
      update_delayed_received_startup_qualification();
    }
    update_initialized_record8_confirmation();
    uVar1 = cadence_mask & 2;
    if (uVar3 < 0x101) {
      seed_health_received_source_filter();
      if (uVar1 != 0) {
        refresh_health_received_source_generation();
      }
      return_only_stub_becce();
      if (uVar1 != 0) {
        refresh_bedd_ready_and_bedc_scaled_status_bed90();
      }
      initialize_bef0_status_and_clear_two_requests_bef22();
      if (uVar1 != 0) {
        merge_bedc_status_with_two_bef1_requests_bef3e();
      }
      reset_bee_accumulators_and_publish_bef0_11_marker_beda2();
      if (uVar1 != 0) {
        update_bee4_and_bee2_sample_filters_bef10();
      }
      return_only_stub_be80c();
      if (uVar1 != 0) {
        snapshot_three_status_or_and_group_16_be80e();
      }
      return_only_stub_be844();
      if (uVar1 != 0) {
        compute_clamped_paired_scaled_difference_and_flags_be846();
      }
      return_only_stub_bef9a();
      if (uVar1 != 0) {
        snapshot_three_status_flags_and_group16_bef9c();
      }
      return_only_stub_befd4();
      if (uVar1 != 0) {
        scale_and_bound_two_inputs_into_bf00_difference_befd6();
      }
      return_only_stub_be796();
    }
    else if (uVar1 != 0) {
      refresh_health_received_source_generation();
      refresh_bedd_ready_and_bedc_scaled_status_bed90();
      merge_bedc_status_with_two_bef1_requests_bef3e();
      update_bee4_and_bee2_sample_filters_bef10();
      snapshot_three_status_or_and_group_16_be80e();
      compute_clamped_paired_scaled_difference_and_flags_be846();
      snapshot_three_status_flags_and_group16_bef9c();
      scale_and_bound_two_inputs_into_bf00_difference_befd6();
    }
    refresh_be88_mode_and_be89_status_aggregate_be7fa();
  }
  if (0x101 < uVar2) {
    if (uVar3 < 0x102) {
      initialize_received_word_age_from_record13();
    }
    refresh_received_control_metadata();
  }
  if (0xff < uVar2) {
    if (uVar3 < 0x100) {
      fill_constant_block_bdba8();
    }
    debounce_three_states_and_persist_b11a_b080_bdbe0();
  }
  if (0x102 < uVar2) {
    if (uVar3 < 0x103) {
      load_or_clear_record15_paired_snapshots_bdd22();
      capture_two_debounced_received_word_snapshots_bde16();
      return_only_stub_bdb86();
      return_only_stub_bdb88();
      return_only_stub_bdb8c();
    }
    else {
      capture_two_debounced_received_word_snapshots_bde16();
      return_only_stub_bdb88();
    }
    clear_byte_febebe1c_bdb8e();
  }
  if (0x101 < uVar2) {
    if (uVar3 < 0x102) {
      load_nvm_seven_lifecycle_marker_b918e();
      poll_nvm_seven_and_complete_pending_request_b92f0();
      clear_b494_b495_b496_request_state_b8fe2();
    }
    else {
      poll_nvm_seven_and_complete_pending_request_b92f0();
    }
    monitor_pending_learned_record_updates();
  }
  if (0x102 < uVar2) {
    uVar1 = cadence_mask & 2;
    if (uVar3 < 0x103) {
      return_only_stub_b8b36();
      update_routine_1007_and_1008_lifecycle_groups_b8d8c();
      thunk_load_record_102_marker_and_report_b6d72();
      if (uVar1 != 0) {
        run_init_chain_b7054();
      }
      snapshot_f055_into_b321_b70d8();
      if (uVar1 != 0) {
        advance_b324_record_102_capture_status_b722c();
      }
      snapshot_f055_into_b305_b6c2a();
      if (uVar1 != 0) {
        update_b30c_marker_acquisition_b6d20();
      }
      snapshot_f055_into_b2fe_b6a38();
      if (uVar1 != 0) {
        update_event_100_change_monitor_b6b9a();
      }
      seed_health_words_and_pass_events_20_120_b8f74();
      if (uVar1 != 0) {
        thunk_seed_two_55aaaa55_words_and_report_299_healthy_b8f4a();
      }
      return_only_stub_b8fcc();
      if (uVar1 != 0) {
        return_only_stub_b8fce();
      }
      return_only_stub_b8f3a();
      if (uVar1 != 0) {
        fill_constant_block_b8f16();
      }
      return_only_stub_b8ec8();
      if (uVar1 != 0) {
        fill_constant_block_b8eca();
      }
      return_only_stub_b7354();
      if (uVar1 != 0) {
        return_only_stub_b7356();
      }
      return_only_stub_b733e();
      if (uVar1 != 0) {
        fill_constant_block_b7314();
      }
      return_only_stub_b72c0();
      if (uVar1 != 0) {
        fill_constant_block_b72c2();
      }
      initialize_two_states_and_snapshot_f07b_f02f_b8e9a();
      if (uVar1 != 0) {
        thunk_set_b446_and_b44c_to_one_b8e8e();
      }
      load_record_103_and_reset_channels_b61e0();
      run_init_chain_b690a();
      initialize_record_101_status_and_defaults_b532a();
      reset_record_101_and_reload_selected_bytes_b53c2();
      return_only_stub_b50aa();
    }
    else {
      update_routine_1007_and_1008_lifecycle_groups_b8d8c();
      if (uVar1 != 0) {
        run_init_chain_b7054();
        advance_b324_record_102_capture_status_b722c();
        update_b30c_marker_acquisition_b6d20();
        update_event_100_change_monitor_b6b9a();
        thunk_seed_two_55aaaa55_words_and_report_299_healthy_b8f4a();
        return_only_stub_b8fce();
        fill_constant_block_b8f16();
        fill_constant_block_b8eca();
        if (uVar1 != 0) {
          return_only_stub_b7356();
          fill_constant_block_b7314();
          fill_constant_block_b72c2();
          thunk_set_b446_and_b44c_to_one_b8e8e();
        }
      }
      run_init_chain_b690a();
      reset_record_101_and_reload_selected_bytes_b53c2();
    }
    run_init_chain_b5232();
  }
  if (uVar2 == 0x522) {
    if (uVar3 == 0x522) {
      advance_quad_learning_readiness_delay_b7728();
    }
    else {
      fill_constant_block_b7716();
      advance_quad_learning_readiness_delay_b7728();
      start_quad_sample_learning_window_b738c();
    }
    if ((cadence_mask >> 1 & 1) != 0) {
      accumulate_validate_and_publish_quad_sample_window_b73cc();
    }
  }
  if (0x102 < uVar2) {
    if (uVar3 < 0x103) {
      return_only_stub_b3a54();
      run_init_chain_b3bd2();
      reload_aef4c_scale_factors_b389c();
      reload_aef4c_scale_factors_guarded_b38d2();
      return_only_stub_b391e();
      update_scaled_reference_and_error_b3a42();
      return_only_stub_b342e();
    }
    else {
      run_init_chain_b3bd2();
      reload_aef4c_scale_factors_guarded_b38d2();
      update_scaled_reference_and_error_b3a42();
    }
    select_snapshot_debounce_classification_path_b37da();
  }
  if (0x100 < uVar2) {
    if (uVar3 < 0x101) {
      reset_current_source_coherence_observations();
      update_source_coherence_history();
      reset_health_record_lifecycle_entry();
      advance_health_record_lifecycle();
      return_only_stub_b480a();
      update_qualified_health_source_policy();
      reset_qualified_health_state_entry();
      advance_qualified_health_state();
      reset_b1bc_latches_and_timers_b4538();
      update_thermal_capture_hold_and_request_b47c0();
      initialize_b1c4_mode_two_b47d6();
      select_b1c4_from_three_latches_b47de();
      return_only_stub_b3c6a();
    }
    else {
      update_source_coherence_history();
      advance_health_record_lifecycle();
      update_qualified_health_source_policy();
      advance_qualified_health_state();
      update_thermal_capture_hold_and_request_b47c0();
      select_b1c4_from_three_latches_b47de();
    }
    publish_health_coherence_fault_actions();
    if (uVar3 < 0x101) {
      reset_b1a8_filter_state_b431a();
    }
    update_health_status_delay_summaries();
  }
  if (uVar2 - 0x200 < 0x323) {
    if (uVar3 - 0x200 < 0x323) {
      qualify_owner3_shutdown_signal();
      publish_owner3_shutdown_request();
      if ((cadence_mask & 2) != 0) {
        debounce_event_9a_failure_and_recovery_bc7ce();
      }
    }
    else {
      reset_owner3_signal_qualification();
      qualify_owner3_shutdown_signal();
      reset_owner3_shutdown_request();
      publish_owner3_shutdown_request();
      fill_constant_block_bc7be();
      if ((cadence_mask & 2) != 0) {
        debounce_event_9a_failure_and_recovery_bc7ce();
      }
      fill_constant_block_bc648();
    }
    debounce_b084_threshold_window_and_toggle_request_14_bc65e();
  }
  if (0x1ff < uVar2) {
    uVar1 = cadence_mask & 0x10;
    if (uVar3 < 0x200) {
      reset_bd54_bd55_and_bd90_when_query_zero_bb95e();
      if (uVar1 != 0) {
        run_bd54_offset_pipeline_with_first_read_bbf8a();
      }
      return_only_stub_bad00();
      stage_absolute_limit_seeds();
      reset_owner5_release_state();
      publish_owner5_limit_request();
      reset_owner4_release_state();
      publish_owner4_limit_request();
      reset_owner8_release_state();
      publish_owner8_limit_request();
      reset_owner6_calibration_envelope();
      update_owner6_calibration_envelope();
      reset_owner1_qualification_state();
      qualify_owner1_limit_state();
      reset_lifecycle_difference_monitor_entry();
      if (uVar1 != 0) {
        step_lifecycle_difference_monitor();
      }
      reset_bd48_flags_and_seed_569a_bounds_bb87a();
      update_thermal_release_envelope();
      return_only_stub_ba8ae();
    }
    else {
      if (uVar1 != 0) {
        run_bd54_offset_pipeline_with_first_read_bbf8a();
      }
      stage_absolute_limit_seeds();
      publish_owner5_limit_request();
      publish_owner4_limit_request();
      publish_owner8_limit_request();
      update_owner6_calibration_envelope();
      qualify_owner1_limit_state();
      if (uVar1 != 0) {
        step_lifecycle_difference_monitor();
      }
      update_thermal_release_envelope();
    }
    update_saturated_afe8_ratio_and_range_admission_ba8b0();
  }
  if (uVar2 - 0x300 < 0x223) {
    if (uVar3 - 0x300 < 0x223) {
      refresh_foreground_control_projection();
    }
    else {
      snapshot_f06a_and_run_d1124_chain_bcd22();
      refresh_foreground_control_projection();
      return_only_stub_b9328();
    }
    if ((cadence_mask >> 1 & 1) != 0) {
      run_control_profile_qualification();
    }
  }
  if (0xff < uVar2) {
    if (uVar3 < 0x100) {
      return_only_stub_b9bc0();
    }
    if ((cadence_mask >> 1 & 1) != 0) {
      run_control_profile_retention();
    }
    if (uVar3 < 0x100) {
      initialize_complementary_request_bitmaps_b14b2();
      reconcile_mode_requests();
      reset_mode_readiness_counter();
    }
    else {
      reconcile_mode_requests();
    }
    advance_application_mode();
  }
  if (0x102 < uVar2) {
    if (uVar3 < 0x103) {
      return_only_stub_b784a();
    }
    tick_b38c_and_refresh_scaled_difference_b78d0();
  }
  if (uVar2 == 0x520) {
    if (uVar3 == 0x520) {
      dispatch_service_update_by_b3d5_mode_b83ba();
    }
    else {
      return_only_stub_b7c80();
      dispatch_service_update_by_b3d5_mode_b83ba();
      fill_constant_block_b87e2();
    }
    advance_table_ramp_when_b404_ready_b885c();
  }
  if (0x102 < uVar2) {
    if (uVar3 < 0x103) {
      load_nvm_106_word_and_publish_read_status_b85d8();
    }
    poll_nvm_106_write_completion_b8622();
  }
  if (uVar2 - 0x200 < 0x323) {
    if (0x322 < uVar3 - 0x200) {
      return_only_stub_b797e();
    }
    latch_b3f8_threshold_result_and_invalidate_ratio_b7980();
  }
  if (uVar2 == 0x520) {
    if (uVar3 == 0x520) {
      update_b42c_pi_sum_when_b40c_ready_b89e0();
    }
    else {
      fill_constant_block_b8896();
      update_b42c_pi_sum_when_b40c_ready_b89e0();
      fill_constant_block_b7ae4();
    }
    update_b398_filter_when_b3a8_ready_b7c2c();
  }
  if (0x101 < uVar2) {
    if (uVar3 < 0x102) {
      return_only_stub_bdf80();
      return_only_stub_bdf82();
      return_only_stub_be130();
      return_only_stub_be132();
      return_only_stub_be1f4();
      return_only_stub_be1f6();
      return_only_stub_be28a();
    }
    else {
      return_only_stub_bdf82();
      return_only_stub_be132();
      return_only_stub_be1f6();
    }
    return_only_stub_be28c();
  }
  if (0xff < uVar2) {
    if (uVar3 < 0x100) {
      return_only_stub_bf24a();
    }
    refresh_acquired_scalar_status_publication();
  }
  publish_foreground_control_outputs();
  return;
}

void dispatch_control_foreground_steady(uint cadence_mask,uint captured_mode)

{
  uint uVar1;
  
  uVar1 = captured_mode & 0xffff;
  if (0xff < uVar1) {
    condition_staged_offset_scalar();
    scale_staged_byte_pair_to_control_raw();
  }
  if (0x100 < uVar1) {
    update_delayed_received_startup_qualification();
    update_initialized_record8_confirmation();
    if ((cadence_mask >> 1 & 1) != 0) {
      refresh_health_received_source_generation();
      refresh_bedd_ready_and_bedc_scaled_status_bed90();
      merge_bedc_status_with_two_bef1_requests_bef3e();
      update_bee4_and_bee2_sample_filters_bef10();
      snapshot_three_status_or_and_group_16_be80e();
      compute_clamped_paired_scaled_difference_and_flags_be846();
      snapshot_three_status_flags_and_group16_bef9c();
      scale_and_bound_two_inputs_into_bf00_difference_befd6();
    }
    refresh_be88_mode_and_be89_status_aggregate_be7fa();
  }
  if (0x101 < uVar1) {
    refresh_received_control_metadata();
  }
  if (0xff < uVar1) {
    debounce_three_states_and_persist_b11a_b080_bdbe0();
  }
  if (0x102 < uVar1) {
    capture_two_debounced_received_word_snapshots_bde16();
    return_only_stub_bdb88();
    clear_byte_febebe1c_bdb8e();
  }
  if (0x101 < uVar1) {
    poll_nvm_seven_and_complete_pending_request_b92f0();
    monitor_pending_learned_record_updates();
  }
  if (0x102 < uVar1) {
    update_routine_1007_and_1008_lifecycle_groups_b8d8c();
    if ((cadence_mask & 2) != 0) {
      run_init_chain_b7054();
      advance_b324_record_102_capture_status_b722c();
      update_b30c_marker_acquisition_b6d20();
      update_event_100_change_monitor_b6b9a();
      thunk_seed_two_55aaaa55_words_and_report_299_healthy_b8f4a();
      return_only_stub_b8fce();
      fill_constant_block_b8f16();
      fill_constant_block_b8eca();
      if ((cadence_mask & 2) != 0) {
        return_only_stub_b7356();
        fill_constant_block_b7314();
        fill_constant_block_b72c2();
        thunk_set_b446_and_b44c_to_one_b8e8e();
      }
    }
    run_init_chain_b690a();
    reset_record_101_and_reload_selected_bytes_b53c2();
    run_init_chain_b5232();
  }
  if ((uVar1 == 0x522) && (advance_quad_learning_readiness_delay_b7728(), (cadence_mask >> 1 & 1) != 0)) {
    accumulate_validate_and_publish_quad_sample_window_b73cc();
  }
  if (0x102 < uVar1) {
    run_init_chain_b3bd2();
    reload_aef4c_scale_factors_guarded_b38d2();
    update_scaled_reference_and_error_b3a42();
    select_snapshot_debounce_classification_path_b37da();
  }
  if (0x100 < uVar1) {
    update_source_coherence_history();
    advance_health_record_lifecycle();
    update_qualified_health_source_policy();
    advance_qualified_health_state();
    update_thermal_capture_hold_and_request_b47c0();
    select_b1c4_from_three_latches_b47de();
    publish_health_coherence_fault_actions();
    update_health_status_delay_summaries();
  }
  if (uVar1 - 0x200 < 0x323) {
    qualify_owner3_shutdown_signal();
    publish_owner3_shutdown_request();
    if ((cadence_mask >> 1 & 1) != 0) {
      debounce_event_9a_failure_and_recovery_bc7ce();
    }
    debounce_b084_threshold_window_and_toggle_request_14_bc65e();
  }
  if (0x1ff < uVar1) {
    if ((cadence_mask & 0x10) != 0) {
      run_bd54_offset_pipeline_with_first_read_bbf8a();
    }
    stage_absolute_limit_seeds();
    publish_owner5_limit_request();
    publish_owner4_limit_request();
    publish_owner8_limit_request();
    update_owner6_calibration_envelope();
    qualify_owner1_limit_state();
    if ((cadence_mask & 0x10) != 0) {
      step_lifecycle_difference_monitor();
    }
    update_thermal_release_envelope();
    update_saturated_afe8_ratio_and_range_admission_ba8b0();
  }
  if ((uVar1 - 0x300 < 0x223) &&
     (refresh_foreground_control_projection(), (cadence_mask >> 1 & 1) != 0)) {
    run_control_profile_qualification();
  }
  if (0xff < uVar1) {
    if ((cadence_mask >> 1 & 1) != 0) {
      run_control_profile_retention();
    }
    reconcile_mode_requests();
    advance_application_mode();
  }
  if (0x102 < uVar1) {
    tick_b38c_and_refresh_scaled_difference_b78d0();
  }
  if (uVar1 == 0x520) {
    dispatch_service_update_by_b3d5_mode_b83ba();
    advance_table_ramp_when_b404_ready_b885c();
  }
  if (0x102 < uVar1) {
    poll_nvm_106_write_completion_b8622();
  }
  if (uVar1 - 0x200 < 0x323) {
    latch_b3f8_threshold_result_and_invalidate_ratio_b7980();
  }
  if (uVar1 == 0x520) {
    update_b42c_pi_sum_when_b40c_ready_b89e0();
    update_b398_filter_when_b3a8_ready_b7c2c();
  }
  if (0x101 < uVar1) {
    return_only_stub_bdf82();
    return_only_stub_be132();
    return_only_stub_be1f6();
    return_only_stub_be28c();
  }
  if (0xff < uVar1) {
    refresh_acquired_scalar_status_publication();
  }
  publish_foreground_control_outputs();
  return;
}

void reset_bf18_table_state_and_select_bank_pair_c28ae(void)

{
  DAT_febebf3c = 0;
  DAT_febebf40 = 0;
  DAT_febebf18 = 0;
  DAT_febebf1c = 0;
  DAT_febebf34 = 0;
  DAT_febebf36 = 0;
  DAT_febebf20 = 0;
  DAT_febebf24 = 0;
  DAT_febebf28 = 0;
  DAT_febebf2c = (*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xb144cu + (uint32_t)(DAT_febeac3c & 1) * 4u))));
  DAT_febebf38 = 0;
  DAT_febebf3a = 0;
  DAT_febebf30 = (*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xb144cu + (uint32_t)(DAT_febeac3c & 1) * 4u)))) + 0x44;
  return;
}

void select_calibration_table_pointer_pair_c28fc(int *param_1,undefined4 *param_2)

{
  uint uVar1;
  int iVar2;
  uint32_t puVar3;
  
  iVar2 = (int)((int)(int16_t)DAT_febec1a4);
  if (DAT_febec158 == '\x11') {
    *param_1 = (int)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd2de0u + (uint32_t)(iVar2) * 4u))));
    puVar3 = (*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xd2de4u + (uint32_t)(iVar2) * 4u))));
  }
  else {
    uVar1 = (uint)DAT_febec156;
    if (DAT_febec158 == 'U') {
      puVar3 = (*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xb144cu + (uint32_t)(DAT_febeac3c & 1) * 4u)))) + 0x880;
    }
    else {
      if (DAT_febec158 != 'f') {
        puVar3 = (*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xb144cu + (uint32_t)(DAT_febeac3c & 1) * 4u))));
        *param_1 = (int)(puVar3 + (iVar2 + (uVar1 & 3) * 8) * 0x44);
        puVar3 = puVar3 + (iVar2 + (uVar1 & 3) * 8) * 0x44 + 0x44;
        goto LAB_000c29ac;
      }
      if (DAT_febeac2c == '\"') {
        puVar3 = 0xd2e44;
      }
      else if (DAT_febeac2c == 'D') {
        puVar3 = 0xd2e88;
      }
      else if (((int8_t)DAT_febeac2c) == -0x78) {
        puVar3 = 0xd2ecc;
      }
      else {
        puVar3 = 0xd2e00;
      }
    }
    *param_1 = (int)puVar3;
  }
LAB_000c29ac:
  *param_2 = puVar3;
  return;
}

uint32_t update_signed_speed_torque_assist(void)

{
  uint8_t stack_record_1c[28];
  uint32_t camry_r10_result;
  short value;
  int iVar1;
  uint32_t puVar2;
  short sVar3;
  uint uVar4;
  uint uVar5;
  int iVar6;
  
  value = ((int)(int16_t)DAT_febec128);
  puVar2 = 0xfebeb800u;
  (*((uint32_t *)(stack_record_1c + 0))) = (*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xb144cu + (uint32_t)(DAT_febeac3c & 1) * 4u))));
  iVar6 = (int)((int)(int16_t)DAT_febec1a6);
  (*((uint32_t *)(stack_record_1c + 4))) = (*((uint32_t *)(stack_record_1c + 0))) + 68u;
  select_calibration_table_pointer_pair_c28fc(((uint32_t *)(stack_record_1c)),((uint32_t *)((stack_record_1c + 4))));
  (*((volatile uint32_t *)camry_host_ptr((uint32_t)((puVar2 + 0x72c))))) = (*((uint32_t *)(stack_record_1c + 0)));
  (*((volatile uint32_t *)camry_host_ptr((uint32_t)((puVar2 + 0x730))))) = (*((uint32_t *)(stack_record_1c + 4)));
  sVar3 = (camry_r10_result = abs_s16_wrapping(value));
  uVar4 = (camry_r10_result = curve16_interpolate_with_slope((*((uint32_t *)(stack_record_1c + 0))), sVar3, ((uint32_t)((uint32_t)(puVar2 + 0x734)))));
  uVar5 = (camry_r10_result = curve16_interpolate_with_slope((*((uint32_t *)(stack_record_1c + 4))), sVar3, ((uint32_t)((uint32_t)(puVar2 + 0x736)))));
  iVar1 = DAT_000b1160;
  (*((short *)camry_host_ptr((uint32_t)(puVar2 + 0x73a)))) = (short)uVar5;
  (*((short *)camry_host_ptr((uint32_t)(puVar2 + 0x738)))) = (short)uVar4;
  iVar6 = (int)((uVar5 - uVar4) * iVar6) / 0x400 + uVar4;
  (*((int *)camry_host_ptr((uint32_t)(puVar2 + 0x724)))) = iVar6;
  if ((iVar6 - iVar1 < 0 != (iVar6 < 0 != iVar1 < 0 && iVar1 < 0 == iVar6 - iVar1 < 0) ||
       iVar6 == iVar1) && (iVar1 = iVar6, iVar6 < 1)) {
    iVar1 = 0;
  }
  (*((int *)camry_host_ptr((uint32_t)(puVar2 + 0x728)))) = iVar1;
  sVar3 = DAT_000af88a;
  if (-1 < value) {
    sVar3 = DAT_000af888;
  }
  (*((int *)camry_host_ptr((uint32_t)(puVar2 + 0x720)))) = iVar1;
  (*((int *)camry_host_ptr((uint32_t)(puVar2 + 0x73c)))) = (iVar1 * sVar3) / 0x400;
  return camry_r10_result;
}

void publish_combined_assist_slope(void)

{
  int iVar1;
  int iVar2;
  
  iVar2 = (int)DAT_000af88c;
  DAT_febebf18 = (((int)((int)(int16_t)DAT_febebf36) - (int)((int)(int16_t)DAT_febebf34)) * (int)((int)(int16_t)DAT_febec1a6)) / 0x400 +
                 (int)((int)(int16_t)DAT_febebf34);
  DAT_febebf1c = ((int)(int16_t)DAT_febec44e) + DAT_febebf18;
  iVar1 = (int)DAT_febebf1c;
  if (iVar1 > iVar2) {
    iVar1 = iVar2;
  }
  else if (iVar1 <= -iVar2) {
    iVar1 = -iVar2;
  }
  DAT_febebf40 = (short)iVar1;
  return;
}

void fill_constant_block_c2c78(void)

{
  DAT_febebf44 = 1;
  DAT_febebf45 = 1;
  DAT_febebf46 = 1;
  DAT_febebf47 = 1;
  DAT_febebf48 = 0;
  DAT_febebf49 = 0;
  DAT_febebf4a = 0;
  DAT_febebf4b = 1;
  DAT_febebf4c = 0;
  return;
}

undefined4 classify_two_status_bytes_by_zero_and_bit1_c2ca0(uint param_1,uint param_2)

{
  if (((param_1 & 0xff) == 0) && ((param_2 & 0xff) == 0)) {
    return 0;
  }
  if ((((param_1 & 0xff) >> 1 & 1) == 0) && (((param_2 & 0xff) >> 1 & 1) == 0)) {
    return 1;
  }
  return 2;
}

undefined1 snapshot_bf44_status_class_and_boolean_inputs_c2cc0(void)

{
  byte bVar1;
  undefined1 uVar2;
  uint32_t puVar3;
  undefined1 uVar4;
  
  uVar2 = DAT_febeacc1;
  puVar3 = 0xfebeb800u;
  uVar4 = classify_two_status_bytes_by_zero_and_bit1_c2ca0(DAT_febeacc1,0);
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(0x744))))) = uVar4;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(0x745))))) = uVar2;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(0x746))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0xa91)))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(0x747))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0xa90)))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(0x748))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0xb29))))) & 1;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(0x749))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0xb30))))) & 1;
  if ((((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0xb2d))))) & 1) != 0) || (bVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0xb2e))))) & 1, ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0xb2e))))) & 1) != 0)) {
    bVar1 = 1;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(0x74a))))) = bVar1;
  if (((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0xa8f))))) != '\0') || (uVar2 = 0, (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0xa8e))))) != '\0')) {
    uVar2 = 1;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(0x74b))))) = uVar2;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(0x74c))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0xa24))))) != '\x02';
  return uVar4;
}

void fill_constant_block_c2d3e(void)

{
  DAT_febebf98 = 0;
  DAT_febebf70 = 0;
  DAT_febebf74 = 0;
  DAT_febebf78 = 0;
  DAT_febebf7c = 0;
  DAT_febebf9a = 0;
  DAT_febebf9c = 0;
  DAT_febebf9e = 0;
  DAT_febebf50 = 0;
  DAT_febebfae = 0;
  DAT_febebfaf = 0;
  DAT_febebfb0 = 0;
  DAT_febebfb1 = 0;
  DAT_febebfb2 = 0;
  DAT_febebfb3 = 0;
  DAT_febebfb4 = 0;
  DAT_febebfb5 = 0;
  DAT_febebf6c = 0x22;
  DAT_febebfb6 = 0;
  DAT_febebf84 = 0;
  DAT_febebfb7 = 0;
  DAT_febebfb8 = 0;
  DAT_febebf54 = 0;
  DAT_febebf80 = 0;
  DAT_febebf58 = 0;
  DAT_febebfa0 = 0;
  DAT_febebf5c = 0;
  DAT_febebfa2 = 0;
  DAT_febebf60 = 0;
  DAT_febebfa4 = 0;
  DAT_febebf64 = 0;
  DAT_febebfa6 = 0;
  DAT_febebf68 = 0;
  DAT_febebfa8 = 0;
  DAT_febebfb9 = 0;
  DAT_febeaba0 = 0;
  DAT_febebfba = 0;
  DAT_febebfbb = 0;
  DAT_febebfbc = 0;
  DAT_febebfbd = 0;
  DAT_febebfbe = 0;
  DAT_febebfbf = 0;
  DAT_febebfc0 = 0;
  DAT_febebfaa = 0;
  DAT_febebfac = 0;
  DAT_febebf88 = 0;
  DAT_febebf8c = 0;
  DAT_febebf90 = 0;
  DAT_febebf94 = 0;
  DAT_febebfc1 = 0;
  DAT_febebfc2 = 0;
  DAT_febebfc3 = 0;
  return;
}

void clear_observer_source_term(void)

{
  DAT_febeaba4 = 0;
  DAT_febebfc4 = 0;
  DAT_febebf6d = 0;
  DAT_febebf6e = 0;
  DAT_febebfc5 = 0;
  return;
}

void compute_bf70_scaled_input_terms_c2e2a(void)

{
  uint uVar1;
  int scaled;
  short sVar2;
  
  DAT_febebf78 = -DAT_febeaeec;
  DAT_febebf98 = ((int)(int16_t)DAT_febeadf2);
  uVar1 = ((uint)DAT_febeae3a * 0x1e4) / 0x40000;
  if (uVar1 != 0) {
    scaled = (int)((uint)(int)(int16_t)DAT_febeadf2 << 4);
    if ((uint)scaled == 0x80000000 && uVar1 == 0xffffffff) {
      DAT_febebf70 = 0x80000000;
    }
    else {
      DAT_febebf70 = (uint)(scaled / (int)uVar1);
    }
  }
  DAT_febebf74 = (int)((int)((int)(int16_t)DAT_febecc64) * (uint)DAT_febeae5a) / 0x2000;
  DAT_febebf9a = ((int)(int16_t)DAT_febec172);
  DAT_febebf9c = ((int)(int16_t)DAT_febec1a2);
  sVar2 = (short)(((uint)DAT_febeae38 * 0x18) / 0x400);
  DAT_febebf7c = (int)(short)(((uint)DAT_febeae38 * 0x666) / 0x100000) * (int)(signed char)DAT_febeacc5 +
                 (int)sVar2 * (int)((int)(int16_t)DAT_febeadfe);
  DAT_febebf50 = (int)sVar2 * (int)((int)(int16_t)DAT_febeaed0);
  DAT_febebf9e = ((int)(int16_t)DAT_febeae44);
  return;
}

void set_bfb0_when_acc0_one_and_nine_flags_clear_c2ed0(void)

{
  if ((((((DAT_febeacda == '\0') && (DAT_febeacd9 == '\0')) && (DAT_febeace9 == '\0')) &&
       ((DAT_febeacea == '\0' && (DAT_febeacc0 == '\x01')))) &&
      ((DAT_febeacdc == '\0' && ((DAT_febeacdd == '\0' && (DAT_febeacde == '\0')))))) &&
     ((DAT_febeace3 == '\0' && (DAT_febeace4 == '\0')))) {
    DAT_febebfb0 = 0x5a;
  }
  else {
    DAT_febebfb0 = 0;
  }
  return;
}

void set_bfb1_when_acc0_one_and_eight_flags_clear_c2f26(void)

{
  if ((((((DAT_febeacdb == '\0') && (DAT_febeacd9 == '\0')) && (DAT_febeace7 == '\0')) &&
       ((DAT_febeace8 == '\0' && (DAT_febeacc0 == '\x01')))) &&
      ((DAT_febeacdf == '\0' && ((DAT_febeace1 == '\0' && (DAT_febeace0 == '\0')))))) &&
     (DAT_febebf4b == '\0')) {
    DAT_febebfb1 = 0x5a;
  }
  else {
    DAT_febebfb1 = 0;
  }
  return;
}

void set_bfae_when_status_class_and_inhibits_clear_c2f78(void)

{
  if ((((DAT_febebf44 == '\0') && (DAT_febeacbd < 2)) && (DAT_febeacc4 == '\0')) &&
     ((DAT_febeacc2 == '\0' && (DAT_febebf4c == '\0')))) {
    DAT_febebfae = 0x5a;
  }
  else {
    DAT_febebfae = 0;
  }
  return;
}

void set_bfaf_when_raw_status_and_inhibits_clear_c2fac(void)

{
  if ((((DAT_febebf45 == '\0') && (DAT_febeacbd < 2)) && (DAT_febeacc4 == '\0')) &&
     (DAT_febeacc2 == '\0')) {
    DAT_febebfaf = 0x5a;
  }
  else {
    DAT_febebfaf = 0;
  }
  return;
}

void set_bfb2_when_five_acc7_flags_clear_c2fd8(void)

{
  if ((((DAT_febeacc7 == '\0') && (DAT_febeacc8 == '\0')) && (DAT_febeacc9 == '\0')) &&
     ((DAT_febeacca == '\0' && (DAT_febeaccb == '\0')))) {
    DAT_febebfb2 = 0x5a;
  }
  else {
    DAT_febebfb2 = 0;
  }
  return;
}
