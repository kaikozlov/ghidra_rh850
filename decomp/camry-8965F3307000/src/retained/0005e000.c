#include "common.h"

void return_only_stub_5e200(void)

{
  return;
}

void run_current_control_and_stage_output(uint workmask,ushort state)

{
  uint uVar1;
  
  if ((0x1ff < state) && (uVar1 = workmask & 2, uVar1 != 0)) {
    latch_current_feedback_and_reference_inputs();
    reset_6e04_flags_and_snapshot_6af4_387ba();
    select_and_filter_eight_control_gains_37a92();
    compose_current_feedback();
    lookup_6d78_6d70_signed_five_map_signal_3879e();
    map_sampled_command_to_base_first_current();
    select_feedback_bounded_first_current_request();
    update_additional_first_current_request();
    if (uVar1 != 0) {
      select_actual_and_feedback_first_current_baselines();
      map_first_current_command_with_6e0a_sign_384d8();
      calculate_sixfold_current_correction();
      publish_corrected_current_reference_pairs();
      transform_summed_pairs_to_three_saturated_components_38a58();
      transform_differenced_pairs_to_three_saturated_components_38b6a();
      if (uVar1 != 0) {
        update_coupled_common_error_accumulator_37228();
        update_clamped_differential_error_accumulator_370e6();
        run_or_reset_6ccc_error_accumulator_3777e();
        run_or_reset_6ca0_error_accumulator_37538();
        compose_regulator_output_bank0();
        compose_regulator_output_bank1();
        if (uVar1 != 0) {
          refresh_shared_second_axis_envelope();
          apply_shared_second_axis_envelope();
          filter_weighted_envelope_sum_and_scale_four_outputs_36f26();
          transform_first_regulated_phase_commands();
          if (uVar1 != 0) {
            transform_second_regulated_phase_commands();
            select_phase_modulation_modes();
            map_phase_compensation_gain();
            refresh_phase_compensation_amplitude();
            compensate_first_regulated_phases();
            compensate_second_regulated_phases();
            modulate_first_phase_triplet();
            modulate_second_phase_triplet();
            publish_current_output_slot();
          }
        }
      }
    }
  }
  if ((0x100 < state) && ((workmask >> 1 & 1) != 0)) {
    select_phase_output_slots();
    stage_phase_output_history();
    stage_live_phase_halfword_compares();
  }
  publish_current_control_snapshot();
  return;
}

void dispatch_torque_feedback_mode_entry_5e2da(undefined4 param_1,uint param_2,uint param_3)

{
  param_3 = param_3 & 0xffff;
  param_2 = param_2 & 0xffff;
  if (0xff < param_2) {
    if (param_3 < 0x100) {
      reset_inverted_state_bit_gate_8a1c_566d6();
      update_inverted_state_bit_gate_8a1c_566dc();
      return_only_stub_50afe();
      fill_constant_block_50b00();
      return_only_stub_50a50();
    }
    else {
      update_inverted_state_bit_gate_8a1c_566dc();
      fill_constant_block_50b00();
    }
    refresh_two_three_word_snapshots_when_8a1c_z_50ae2();
  }
  if (0x100 < param_2) {
    if (param_3 < 0x101) {
      fill_constant_block_4843c();
    }
    decode_torque_sensor_channels();
  }
  if (param_2 - 0x301 < 0x222) {
    if (param_3 - 0x301 < 0x222) {
      return_only_stub_4606e();
      count_snapshot_a_flag_sequence_and_pair_range_failures_4663c();
    }
    else {
      return_only_stub_4606c();
      return_only_stub_4606e();
      seed_snapshot_a_modulo_four_sequence_4661e();
      count_snapshot_a_flag_sequence_and_pair_range_failures_4663c();
      seed_snapshot_b_modulo_four_sequence_467d0();
    }
    count_snapshot_b_flag_sequence_and_pair_range_failures_467ee();
  }
  if (0x100 < param_2) {
    if (param_3 < 0x101) {
      clear_halfword_7e0c_4867e();
    }
    publish_selected_torque_feedback();
  }
  if (param_2 == 0x600) {
    if (param_3 != 0x600) {
      clear_state_bytes_6ac8_and_counter_6acc_34c48();
    }
    select_mode600_stimulus_request();
  }
  fill_constant_block_5802e();
  return;
}

void dispatch_motor_command_mode_entry_5e38e(undefined4 param_1,ushort param_2,ushort param_3)

{
  if (0x1ff < param_2) {
    if (param_3 < 0x200) {
      return_only_stub_35c4a();
    }
    sample_motor_command();
  }
  if (0x101 < param_2) {
    if (param_3 < 0x102) {
      return_only_stub_53ffa();
    }
    return_only_stub_53ffc();
  }
  fill_constant_block_5802e();
  return;
}

void dispatch_torque_feedback_mode_step_5e3ca(undefined4 param_1,uint param_2)

{
  param_2 = param_2 & 0xffff;
  if (0xff < param_2) {
    update_inverted_state_bit_gate_8a1c_566dc();
    fill_constant_block_50b00();
    refresh_two_three_word_snapshots_when_8a1c_z_50ae2();
  }
  if (0x100 < param_2) {
    decode_torque_sensor_channels();
  }
  if (param_2 - 0x301 < 0x222) {
    return_only_stub_4606e();
    count_snapshot_a_flag_sequence_and_pair_range_failures_4663c();
    count_snapshot_b_flag_sequence_and_pair_range_failures_467ee();
  }
  if (0x100 < param_2) {
    publish_selected_torque_feedback();
  }
  if (param_2 == 0x600) {
    select_mode600_stimulus_request();
  }
  fill_constant_block_5802e();
  return;
}

void dispatch_motor_command_mode_step_5e420(undefined4 param_1,ushort param_2)

{
  if (param_2 < 0x200) {
    if (param_2 < 0x102) goto LAB_0005e43c;
  }
  else {
    sample_motor_command();
  }
  return_only_stub_53ffc();
LAB_0005e43c:
  fill_constant_block_5802e();
  return;
}

void step_transitioned_channel_monitor_slice
               (uint unused_r6,ushort current_mode,ushort previous_mode)

{
  uint uVar1;
  uint uVar2;
  
  uVar2 = (uint)previous_mode;
  uVar1 = (uint)current_mode;
  if (0xff < uVar1) {
    if (uVar2 < 0x100) {
      reset_monitor_five_call_gate_8a24_56722();
      update_monitor_five_call_gate_8a24_5672c();
      reset_monitor_five_call_gate_8a18_566a2();
      update_monitor_five_call_gate_8a18_566ac();
      return_only_stub_50b24();
      copy_cell_block_50b26();
      return_only_stub_50a04();
      snapshot_acquisition_status_flags();
      return_only_stub_50a1a();
    }
    else {
      update_monitor_five_call_gate_8a24_5672c();
      update_monitor_five_call_gate_8a18_566ac();
      copy_cell_block_50b26();
      snapshot_acquisition_status_flags();
    }
    snapshot_acquisition_range_fields();
  }
  if (0x100 < uVar1) {
    if (uVar2 < 0x101) {
      initialize_six_retained_current_references_to_8000_48d32();
      condition_monitor_current_planes();
      fill_constant_block_495a4();
    }
    else {
      condition_monitor_current_planes();
    }
    scale_six_unsigned_samples_by_1e06_495b6();
  }
  if (0xff < uVar1) {
    if (uVar2 < 0x100) {
      seed_seven_scaled_samples_and_five_accumulators_47f98();
    }
    update_scaled_sample_filters_and_selection_48230();
  }
  if (0x100 < uVar1) {
    if (uVar2 < 0x101) {
      fill_constant_block_45bb2();
    }
    update_scalar_availability();
  }
  if (0x102 < uVar1) {
    if (uVar1 < 0x523) {
      if (uVar2 - 0x103 < 0x420) {
        step_acquisition_status_a_monitor();
        step_acquisition_status_b_monitor();
        step_acquisition_range_a_monitor();
        step_acquisition_range_b_monitor();
      }
      else {
        reset_scalar_monitor_3bab2_3baa2();
        step_acquisition_status_a_monitor();
        reset_scalar_monitor_3bb44_3bb34();
        step_acquisition_status_b_monitor();
        reset_scalar_monitor_3bc4c_3bc3c();
        step_acquisition_range_a_monitor();
        reset_scalar_monitor_3bcfc_3bcec();
        step_acquisition_range_b_monitor();
        return_only_stub_3bbb8();
      }
      publish_acquisition_monitor_actions();
    }
    if (uVar2 < 0x103) {
      return_only_stub_3d6d0();
    }
    compose_local_status_fault_actions();
  }
  if (uVar1 - 0x200 < 0x323) {
    if (uVar2 - 0x200 < 0x323) {
      update_all_six_sample_binmaps_4523e();
      step_paired_source_counter_monitor_a();
      step_paired_source_counter_monitor_b();
      step_paired_source_mask_monitor_a();
      step_paired_source_mask_monitor_b();
      publish_paired_source_difference_changes();
      step_paired_source_difference_monitors_a();
      step_paired_source_difference_monitors_b();
      publish_paired_source_monitor_actions();
      update_event_36_monitor_status_and_healthy_delay_423bc();
      if (uVar1 - 0x20c < 0x317) {
        if (0x316 < uVar2 - 0x20c) {
          clear_midpoint_pair_latched_triplet_41e6c();
        }
        update_midpoint_pair_latched_triplet_41e96();
      }
      step_channel_phase_monitors_a();
      update_sample_sum_window_monitor_a_42caa();
      update_raw_lower_bound_latched_monitor_a_42b94();
      filter_clipped_three_channel_q16_state_42030();
      update_three_channel_residual_window_monitors_4218a();
      publish_channel_monitor_actions_a();
      update_event_19_monitor_status_and_healthy_delay_4337a();
      if (uVar1 - 0x20c < 0x317) {
        if (0x316 < uVar2 - 0x20c) {
          clear_midpoint_pair_b_latched_triplet_42e2a();
        }
        update_midpoint_pair_b_latched_triplet_42e54();
      }
      step_channel_phase_monitors_b();
      update_sample_sum_window_monitor_b_43c6e();
      update_raw_lower_bound_latched_monitor_b_43b56();
      filter_clipped_b_three_channel_q16_state_42fee();
      update_b_three_channel_residual_window_monitors_43148();
      publish_channel_monitor_actions_b();
      if (uVar1 - 0x301 < 0x222) {
        if (0x221 < uVar2 - 0x301) {
          fill_constant_block_43dc6();
        }
        update_dual_threshold_latches_when_enabled_43f1a();
      }
      update_dual_channel_shared_latched_monitor_4441c();
      if (uVar1 - 0x20b < 0x318) {
        if (uVar2 - 0x20b < 0x318) {
          update_direct_source_a_shared_latched_monitor_4460c();
        }
        else {
          reset_latched_monitor_febe79ac_445fc();
          update_direct_source_a_shared_latched_monitor_4460c();
          reset_latched_monitor_febe79b8_446aa();
        }
        update_direct_source_b_shared_latched_monitor_446ba();
      }
      update_a_shared_sample_window_latched_monitor_440bc();
      update_b_shared_sample_window_latched_monitor_4426c();
      update_paired_gate_a_shared_latched_monitor_44768();
      update_paired_gate_b_shared_latched_monitor_44856();
      update_inverse_gate_shared_monitor_seven_43f58();
      update_inverse_gate_shared_monitor_eight_4400a();
      publish_shared_condition_monitor_actions();
      publish_local_channel_monitor_actions_a();
    }
    else {
      return_only_stub_44ecc();
      update_all_six_sample_binmaps_4523e();
      reset_7524_monitor_and_snapshot_even_source_bytes_3dd82();
      step_paired_source_counter_monitor_a();
      reset_7538_monitor_and_snapshot_odd_source_bytes_3df22();
      step_paired_source_counter_monitor_b();
      reset_windowed_monitor_febe757c_3e3ea();
      step_paired_source_mask_monitor_a();
      reset_windowed_monitor_febe758c_3e4bc();
      step_paired_source_mask_monitor_b();
      fill_constant_block_3e1da();
      publish_paired_source_difference_changes();
      reset_74e4_and_74f4_windowed_monitors_3da72();
      step_paired_source_difference_monitors_a();
      reset_7504_and_7514_windowed_monitors_3dbfe();
      step_paired_source_difference_monitors_b();
      return_only_stub_3e22e();
      publish_paired_source_monitor_actions();
      reset_monitor_a_twelve_status_423b6();
      update_event_36_monitor_status_and_healthy_delay_423bc();
      clear_three_window_and_recoverable_monitors_425c4();
      step_channel_phase_monitors_a();
      reset_windowed_monitor_febe7844_42c9a();
      update_sample_sum_window_monitor_a_42caa();
      reset_latched_monitor_febe7838_42b84();
      update_raw_lower_bound_latched_monitor_a_42b94();
      initialize_clipped_three_channel_q16_state_41fbe();
      filter_clipped_three_channel_q16_state_42030();
      clear_three_channel_residual_window_monitors_4215e();
      update_three_channel_residual_window_monitors_4218a();
      return_only_stub_427f0();
      publish_channel_monitor_actions_a();
      reset_monitor_b_twelve_status_43374();
      update_event_19_monitor_status_and_healthy_delay_4337a();
      clear_b_three_window_and_recoverable_monitors_43586();
      step_channel_phase_monitors_b();
      reset_windowed_monitor_febe7954_43c5e();
      update_sample_sum_window_monitor_b_43c6e();
      reset_latched_monitor_febe7948_43b46();
      update_raw_lower_bound_latched_monitor_b_43b56();
      initialize_clipped_b_three_channel_q16_state_42f7c();
      filter_clipped_b_three_channel_q16_state_42fee();
      clear_b_three_channel_residual_window_monitors_4311c();
      update_b_three_channel_residual_window_monitors_43148();
      return_only_stub_437b2();
      publish_channel_monitor_actions_b();
      reset_latched_monitor_febe79a0_4440c();
      update_dual_channel_shared_latched_monitor_4441c();
      reset_latched_monitor_febe7988_440ac();
      update_a_shared_sample_window_latched_monitor_440bc();
      reset_latched_monitor_febe7994_4425c();
      update_b_shared_sample_window_latched_monitor_4426c();
      reset_latched_monitor_febe79c4_44758();
      update_paired_gate_a_shared_latched_monitor_44768();
      reset_latched_monitor_febe79d0_44846();
      update_paired_gate_b_shared_latched_monitor_44856();
      reset_latched_monitor_febe7970_43f48();
      update_inverse_gate_shared_monitor_seven_43f58();
      reset_latched_monitor_febe797c_43ffa();
      update_inverse_gate_shared_monitor_eight_4400a();
      return_only_stub_44926();
      publish_shared_condition_monitor_actions();
      return_only_stub_452a6();
      publish_local_channel_monitor_actions_a();
      return_only_stub_454c2();
    }
    publish_local_channel_monitor_actions_b();
  }
  if (uVar1 - 0x301 < 0x222) {
    if (uVar2 - 0x301 < 0x222) {
      update_and_publish_snapshot_monitor_0_46090();
      update_and_publish_snapshot_monitor_1_46366();
      update_and_publish_snapshot_monitor_2_46b1e();
      update_and_publish_snapshot_monitor_3_46e28();
      update_and_publish_snapshot_monitor_4_4759c();
      update_and_publish_snapshot_monitor_5_476a2();
      update_and_publish_snapshot_monitor_6_4740c();
      update_and_publish_snapshot_monitor_7_474d4();
      update_and_publish_snapshot_monitor_8_477a8();
      update_and_publish_snapshot_monitor_9_47944();
      update_and_publish_selected_source_recoverable_monitor_46a52();
      publish_shared_snapshot_monitor_actions();
      select_clamp_and_publish_decoded_torque_history_46994();
    }
    else {
      reset_shared_snapshot_monitor_0_46080();
      update_and_publish_snapshot_monitor_0_46090();
      reset_shared_snapshot_monitor_1_46356();
      update_and_publish_snapshot_monitor_1_46366();
      reset_shared_snapshot_monitor_2_46b0e();
      update_and_publish_snapshot_monitor_2_46b1e();
      reset_shared_snapshot_monitor_3_46e18();
      update_and_publish_snapshot_monitor_3_46e28();
      reset_shared_snapshot_monitor_4_4758c();
      update_and_publish_snapshot_monitor_4_4759c();
      reset_shared_snapshot_monitor_5_47692();
      update_and_publish_snapshot_monitor_5_476a2();
      reset_shared_snapshot_monitor_6_473fc();
      update_and_publish_snapshot_monitor_6_4740c();
      reset_shared_snapshot_monitor_7_474c4();
      update_and_publish_snapshot_monitor_7_474d4();
      reset_shared_snapshot_monitor_8_47798();
      update_and_publish_snapshot_monitor_8_477a8();
      reset_shared_snapshot_monitor_9_47934();
      update_and_publish_snapshot_monitor_9_47944();
      reset_recoverable_monitor_febe7c68_46a42();
      update_and_publish_selected_source_recoverable_monitor_46a52();
      return_only_stub_47114();
      publish_shared_snapshot_monitor_actions();
      clear_decoded_torque_history_46982();
      select_clamp_and_publish_decoded_torque_history_46994();
      return_only_stub_45254();
    }
    latch_gated_sample_lower_and_upper_crossings_45256();
  }
  if (0x102 < uVar1) {
    if (uVar2 < 0x103) {
      clear_fault_qualification_and_request_counters_3be52();
    }
    aggregate_fault_actions();
    if (uVar2 < 0x103) {
      return_only_stub_32722();
      update_active_monitor_current_calibration();
      return_only_stub_320c0();
      service_two_record_shadow_channels_when_enabled_32240();
      return_only_stub_33ab4();
      step_retained_fit_coherence();
      return_only_stub_35530();
    }
    else {
      update_active_monitor_current_calibration();
      service_two_record_shadow_channels_when_enabled_32240();
      step_retained_fit_coherence();
    }
    refresh_or_default_cached_learned_quad_35598();
  }
  if (uVar1 == 0x600) {
    if (uVar2 != 0x600) {
      return_only_stub_32622();
    }
    average_two_six_channel_u16_groups_over_128_samples_32624();
  }
  if (0x1ff < uVar1) {
    if (uVar2 < 0x200) {
      return_only_stub_35cea();
      update_limit_budget_branch0();
      return_only_stub_35d56();
      update_limit_budget_branch1();
      reset_owner9_budget_limit_state();
    }
    else {
      update_limit_budget_branch0();
      update_limit_budget_branch1();
    }
    publish_owner9_budget_limit();
  }
  publish_application_status_snapshot_at_ee00_57f00();
  return;
}

void update_mode_owned_application_requests(uint context,ushort mode,ushort previous_mode)

{
  uint uVar1;
  uint uVar2;
  
  uVar2 = (uint)previous_mode;
  uVar1 = (uint)mode;
  if (0x1ff < uVar1) {
    if (uVar2 < 0x200) {
      return_only_stub_36298();
      update_transient_current_reference_qualification();
      initialize_6cf0_scale_to_1024_37920();
      compute_7da6_reciprocal_adjusted_scale_3792a();
      initialize_6cf4_scale_to_1024_37956();
      compute_7da8_reciprocal_adjusted_scale_37960();
      initialize_phase_offset_selector();
    }
    else {
      update_transient_current_reference_qualification();
      compute_7da6_reciprocal_adjusted_scale_3792a();
      compute_7da8_reciprocal_adjusted_scale_37960();
    }
    advance_phase_offset_selector();
  }
  if (uVar1 - 0x300 < 0x101) {
    if (0x100 < uVar2 - 0x300) {
      return_only_stub_45ccc();
    }
    clear_reserved_monitor_action_slot();
  }
  if (0x100 < uVar1) {
    if (uVar2 < 0x101) {
      return_only_stub_571b2();
      publish_aggregate_output_requests();
      initialize_direct_output_requests();
      publish_direct_output_requests();
      clear_two_combined_channel_request_words_5711a();
      combine_owner_requests_with_both_channel_masks_57130();
      initialize_secondary_channel_request_masks_56d7a();
      aggregate_secondary_channel_requests_and_debounce_56e34();
      initialize_two_secondary_priority_masks_56e7c();
      aggregate_secondary_priority_masks_with_requests_56ed0();
      initialize_channel_owner_request_masks_569c2();
      update_channel_requests();
      initialize_two_priority_masks_8a9c_56b8e();
      aggregate_priority_masks_with_channel_mismatch_56be2();
      clear_two_request_words_8a48_568f2();
      aggregate_two_requests_to_status_bits0_and1_56908();
      clear_five_request_words_8a50_56954();
      aggregate_five_request_words_8a50_56982();
      clear_five_request_words_8a2c_567fe();
      aggregate_five_request_words_8a2c_568ac();
      clear_four_request_words_8a88_56b1c();
      aggregate_requests_with_external_channel_status_56b32();
      fill_constant_block_56c3c();
      aggregate_six_request_words_8aa8_56cb0();
      clear_five_status_mask_words_50c38();
      merge_five_status_masks_and_publish_low_bit_50c58();
      set_range_exclusion_flag_57eb4();
      update_three_input_range_exclusion_flag_57ebc();
      return_only_stub_570a8();
    }
    else {
      publish_aggregate_output_requests();
      publish_direct_output_requests();
      combine_owner_requests_with_both_channel_masks_57130();
      aggregate_secondary_channel_requests_and_debounce_56e34();
      aggregate_secondary_priority_masks_with_requests_56ed0();
      update_channel_requests();
      aggregate_priority_masks_with_channel_mismatch_56be2();
      aggregate_two_requests_to_status_bits0_and1_56908();
      aggregate_five_request_words_8a50_56982();
      aggregate_five_request_words_8a2c_568ac();
      aggregate_requests_with_external_channel_status_56b32();
      aggregate_six_request_words_8aa8_56cb0();
      merge_five_status_masks_and_publish_low_bit_50c58();
      update_three_input_range_exclusion_flag_57ebc();
    }
    and_three_owner_gates_for_two_status_outputs_570aa();
  }
  if (0x101 < uVar1) {
    if (uVar2 < 0x102) {
      return_only_stub_53db4();
      return_only_stub_53db6();
      return_only_stub_56332();
    }
    else {
      return_only_stub_53db6();
    }
    return_only_stub_56334();
  }
  publish_application_status_snapshot_at_ee00_57f00();
  return;
}

void step_steady_channel_monitor_slice(uint unused_r6,ushort current_mode)

{
  uint uVar1;
  
  uVar1 = (uint)current_mode;
  if (0xff < uVar1) {
    update_monitor_five_call_gate_8a24_5672c();
    update_monitor_five_call_gate_8a18_566ac();
    copy_cell_block_50b26();
    snapshot_acquisition_status_flags();
    snapshot_acquisition_range_fields();
  }
  if (0x100 < uVar1) {
    condition_monitor_current_planes();
    scale_six_unsigned_samples_by_1e06_495b6();
  }
  if (0xff < uVar1) {
    update_scaled_sample_filters_and_selection_48230();
  }
  if (0x100 < uVar1) {
    update_scalar_availability();
  }
  if (0x102 < uVar1) {
    if (uVar1 < 0x523) {
      step_acquisition_status_a_monitor();
      step_acquisition_status_b_monitor();
      step_acquisition_range_a_monitor();
      step_acquisition_range_b_monitor();
      publish_acquisition_monitor_actions();
    }
    compose_local_status_fault_actions();
  }
  if (uVar1 - 0x200 < 0x323) {
    update_all_six_sample_binmaps_4523e();
    step_paired_source_counter_monitor_a();
    step_paired_source_counter_monitor_b();
    step_paired_source_mask_monitor_a();
    step_paired_source_mask_monitor_b();
    publish_paired_source_difference_changes();
    step_paired_source_difference_monitors_a();
    step_paired_source_difference_monitors_b();
    publish_paired_source_monitor_actions();
    update_event_36_monitor_status_and_healthy_delay_423bc();
    if (uVar1 - 0x20c < 0x317) {
      update_midpoint_pair_latched_triplet_41e96();
    }
    step_channel_phase_monitors_a();
    update_sample_sum_window_monitor_a_42caa();
    update_raw_lower_bound_latched_monitor_a_42b94();
    filter_clipped_three_channel_q16_state_42030();
    update_three_channel_residual_window_monitors_4218a();
    publish_channel_monitor_actions_a();
    update_event_19_monitor_status_and_healthy_delay_4337a();
    if (uVar1 - 0x20c < 0x317) {
      update_midpoint_pair_b_latched_triplet_42e54();
    }
    step_channel_phase_monitors_b();
    update_sample_sum_window_monitor_b_43c6e();
    update_raw_lower_bound_latched_monitor_b_43b56();
    filter_clipped_b_three_channel_q16_state_42fee();
    update_b_three_channel_residual_window_monitors_43148();
    publish_channel_monitor_actions_b();
    if (uVar1 - 0x301 < 0x222) {
      update_dual_threshold_latches_when_enabled_43f1a();
    }
    update_dual_channel_shared_latched_monitor_4441c();
    if (uVar1 - 0x20b < 0x318) {
      update_direct_source_a_shared_latched_monitor_4460c();
      update_direct_source_b_shared_latched_monitor_446ba();
    }
    update_a_shared_sample_window_latched_monitor_440bc();
    update_b_shared_sample_window_latched_monitor_4426c();
    update_paired_gate_a_shared_latched_monitor_44768();
    update_paired_gate_b_shared_latched_monitor_44856();
    update_inverse_gate_shared_monitor_seven_43f58();
    update_inverse_gate_shared_monitor_eight_4400a();
    publish_shared_condition_monitor_actions();
    publish_local_channel_monitor_actions_a();
    publish_local_channel_monitor_actions_b();
  }
  if (uVar1 - 0x301 < 0x222) {
    update_and_publish_snapshot_monitor_0_46090();
    update_and_publish_snapshot_monitor_1_46366();
    update_and_publish_snapshot_monitor_2_46b1e();
    update_and_publish_snapshot_monitor_3_46e28();
    update_and_publish_snapshot_monitor_4_4759c();
    update_and_publish_snapshot_monitor_5_476a2();
    update_and_publish_snapshot_monitor_6_4740c();
    update_and_publish_snapshot_monitor_7_474d4();
    update_and_publish_snapshot_monitor_8_477a8();
    update_and_publish_snapshot_monitor_9_47944();
    update_and_publish_selected_source_recoverable_monitor_46a52();
    publish_shared_snapshot_monitor_actions();
    select_clamp_and_publish_decoded_torque_history_46994();
    latch_gated_sample_lower_and_upper_crossings_45256();
  }
  if (0x102 < uVar1) {
    aggregate_fault_actions();
    update_active_monitor_current_calibration();
    service_two_record_shadow_channels_when_enabled_32240();
    step_retained_fit_coherence();
    refresh_or_default_cached_learned_quad_35598();
  }
  if (uVar1 == 0x600) {
    average_two_six_channel_u16_groups_over_128_samples_32624();
  }
  if (0x1ff < uVar1) {
    update_limit_budget_branch0();
    update_limit_budget_branch1();
    publish_owner9_budget_limit();
  }
  publish_application_status_snapshot_at_ee00_57f00();
  return;
}

void update_steady_application_requests(uint context,ushort mode)

{
  uint uVar1;
  
  uVar1 = (uint)mode;
  if (0x1ff < uVar1) {
    update_transient_current_reference_qualification();
    compute_7da6_reciprocal_adjusted_scale_3792a();
    compute_7da8_reciprocal_adjusted_scale_37960();
    advance_phase_offset_selector();
  }
  if (uVar1 - 0x300 < 0x101) {
    clear_reserved_monitor_action_slot();
  }
  if (0x100 < uVar1) {
    publish_aggregate_output_requests();
    publish_direct_output_requests();
    combine_owner_requests_with_both_channel_masks_57130();
    aggregate_secondary_channel_requests_and_debounce_56e34();
    aggregate_secondary_priority_masks_with_requests_56ed0();
    update_channel_requests();
    aggregate_priority_masks_with_channel_mismatch_56be2();
    aggregate_two_requests_to_status_bits0_and1_56908();
    aggregate_five_request_words_8a50_56982();
    aggregate_five_request_words_8a2c_568ac();
    aggregate_requests_with_external_channel_status_56b32();
    aggregate_six_request_words_8aa8_56cb0();
    merge_five_status_masks_and_publish_low_bit_50c58();
    update_three_input_range_exclusion_flag_57ebc();
    and_three_owner_gates_for_two_status_outputs_570aa();
  }
  if (0x101 < uVar1) {
    return_only_stub_53db6();
    return_only_stub_56334();
  }
  publish_application_status_snapshot_at_ee00_57f00();
  return;
}

void dispatch_monitor_learning_thermal_mode_entry_5ec24(uint param_1,uint param_2,uint param_3)

{
  uint uVar1;
  
  param_2 = param_2 & 0xffff;
  param_3 = param_3 & 0xffff;
  if (0xff < param_2) {
    if (param_3 < 0x100) {
      return_only_stub_50c98();
    }
    snapshot_local_status_link_flags();
  }
  if (param_2 == 0x101) {
    if (param_3 != 0x101) {
      return_only_stub_56788();
    }
    dispatch_service12_when_66f10_returns_zero_5678a();
  }
  if (0xff < param_2) {
    if (param_3 < 0x100) {
      return_only_stub_509a2();
      refresh_diagnostic_application_availability();
      return_only_stub_49b3a();
      combine_and_publish_monitor_inhibit_sources_49e22();
      seed_status_transition_delay_counter_498f6();
      reconcile_application_normal_network_policy();
      return_only_stub_49f1e();
      update_internal_source_admission_lifecycle();
      return_only_stub_49706();
      update_application_receive_statuses();
      return_only_stub_4ae70();
      decode_receive_slot_1_u16_and_u32_fields_4ae72();
      return_only_stub_4aed4();
      decode_receive_slot_2_byte_and_three_nibbles_4aed6();
      return_only_stub_4af6a();
      decode_receive_slot_3_two_byte_fields_4af6c();
      return_only_stub_4afea();
      decode_receive_slot_5_three_bit_and_single_bit_fields_4afec();
      return_only_stub_4b12c();
      decode_receive_slot_8_signed16_and_flag_4b12e();
      return_only_stub_4b1f4();
      decode_receive_slot_10_signed16_field_4b1f6();
      return_only_stub_4b240();
      decode_receive_slot_11_ten_packed_fields_4b242();
      return_only_stub_4b376();
      refresh_route30_health_inputs();
      return_only_stub_4b40c();
      decode_receive_slot_13_twobit_and_u32_fields_4b40e();
      return_only_stub_4b470();
      decode_receive_slot_14_two_single_bit_fields_4b472();
      return_only_stub_4b59c();
      decode_receive_slot_17_three_signed_fields_and_four_flags_4b59e();
      return_only_stub_4b688();
      decode_receive_slot_18_four_biased_u15_values_and_flags_4b68a();
      return_only_stub_4b7d4();
      decode_receive_slot_19_three_flags_and_tenbit_field_4b7d6();
      return_only_stub_4b86c();
      decode_changed_rx14_two_signed_words_and_flag_4b86e();
      return_only_stub_4b8f2();
      decode_changed_rx15_eight_bitfields_4b8f4();
      return_only_stub_4b9f2();
      decode_changed_rx16_three_ten_bit_values_and_flags_4b9f4();
      return_only_stub_4bb60();
      decode_changed_rx17_two_words_and_flags_4bb62();
      return_only_stub_4bc26();
      decode_changed_rx18_four_bytes_4bc28();
      return_only_stub_4bcbe();
      decode_changed_rx19_two_signed_eighteen_bit_fields_4bcc0();
      return_only_stub_4bd44();
      decode_changed_rx1a_word_bytes_and_flags_4bd46();
      return_only_stub_4bece();
      decode_changed_rx1b_three_bytes_4bed0();
      return_only_stub_4bf4c();
      decode_changed_rx1c_three_and_four_bit_fields_4bf4e();
      return_only_stub_4bfb0();
      decode_changed_rx1d_low_nibble_4bfb2();
      return_only_stub_4b04c();
      decode_receive_slot_6_two_single_bit_fields_4b04e();
      return_only_stub_4b0ae();
      decode_receive_slot_7_signed11_sixbit_and_flag_4b0b0();
      return_only_stub_4b4d2();
      decode_receive_slot_15_six_byte_fields_4b4d4();
      return_only_stub_4ae28();
      decode_receive_slot_0_byte_field_4ae2a();
      return_only_stub_4b192();
      decode_receive_slot_9_byte_and_flag_4b194();
      reset_change_triggered_monitor_7fc8_4aad4();
      step_change_triggered_monitor_and_encode_status_4aae8();
      return_only_stub_4a4b0();
      dispatch_route30_codeword_timeout_monitors_4a702();
      return_only_stub_4a7aa();
      dispatch_eight_codeword_timeout_monitors_4aa5c();
      fill_constant_block_4ad1a();
      delay_then_update_two_expiring_latches_4ada2();
      return_only_stub_4a448();
      initialize_and_update_communication_inhibits_4a49e();
      return_only_stub_4adcc();
      pack_four_source_bytes_equal_to_one_4adce();
      return_only_stub_4abbc();
      scale_word_80b0_with_sentinel_to_signed_halfword_4abbe();
      reset_latched_monitor_7fd4_and_side_flag_4ac14();
      step_latched_monitor_and_record_failing_side_4ac28();
      return_only_stub_4cf64();
    }
    else {
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
    }
    refresh_diagnostic_admission_and_dispatch_pending_request_4d094();
    if (param_3 < 0x100) {
      return_only_stub_47ade();
      clamp_sample_8048_and_compute_enable_gate_47ae0();
      return_only_stub_47ac2();
    }
    else {
      clamp_sample_8048_and_compute_enable_gate_47ae0();
    }
    lookup_low_nibble_code_or_zero_47ac4();
  }
  if (0x102 < param_2) {
    uVar1 = param_1 & 0x10;
    if (param_3 < 0x103) {
      initialize_record5_pair_and_sample_accumulators_4825c();
      if (uVar1 != 0) {
        update_thermistor_channels();
      }
      clear_record5_write_state_483b6();
      if (uVar1 != 0) goto LAB_0005eeaa;
LAB_0005eeae:
      if (param_2 < 0x103) goto LAB_0005ef00;
    }
    else if (uVar1 != 0) {
      update_thermistor_channels();
LAB_0005eeaa:
      poll_record5_write_state_483bc();
      goto LAB_0005eeae;
    }
    if (param_2 < 0x523) {
      if (param_3 - 0x103 < 0x420) {
        update_qualified_local_status_monitor();
        update_paired_local_status_monitor();
        update_individual_local_status_a();
      }
      else {
        reset_latched_monitor_febe74b0_3d746();
        update_qualified_local_status_monitor();
        reset_74bc_recoverable_monitor_and_flag_3d826();
        update_paired_local_status_monitor();
        reset_recoverable_monitor_febe74cc_3d906();
        update_individual_local_status_a();
        reset_recoverable_monitor_febe74d8_3d9b8();
      }
      update_individual_local_status_b();
    }
    if (param_3 < 0x103) {
      report_8294_fault_bits_when_588b6_zero_3d5e4();
    }
    publish_local_status_link_fault();
  }
LAB_0005ef00:
  uVar1 = param_2 - 0x200;
  if (uVar1 < 0x323) {
    if (param_3 - 0x200 < 0x323) {
      update_gated_latched_monitor_a_eleven_42a6a();
      update_gated_latched_monitor_b_eleven_43a2c();
      step_local_channel_mismatch_a_monitor();
      step_local_output_status_a_monitor();
      step_local_channel_mismatch_b_monitor();
    }
    else {
      reset_latched_monitor_febe782c_42a5a();
      update_gated_latched_monitor_a_eleven_42a6a();
      reset_latched_monitor_febe793c_43a1c();
      update_gated_latched_monitor_b_eleven_43a2c();
      reset_scalar_monitor_45410_45400();
      step_local_channel_mismatch_a_monitor();
      reset_scalar_monitor_45356_45346();
      step_local_output_status_a_monitor();
      reset_scalar_monitor_4562a_4561a();
      step_local_channel_mismatch_b_monitor();
      reset_scalar_monitor_45572_45562();
    }
    step_local_output_status_b_monitor();
  }
  if (uVar1 < 0xe) {
    if (param_2 == 0x200) {
      if (param_3 == 0x200) {
        step_sample_difference_window_a();
      }
      else {
        reset_sample_difference_a_monitor_40042();
        step_sample_difference_window_a();
        reset_sample_difference_b_monitor_40222();
      }
      step_sample_difference_window_b();
    }
    if (param_2 == 0x201) {
      if (param_3 == 0x201) {
        step_bounded_sample_or_status_a();
      }
      else {
        reset_bounded_sample_status_a_monitor_3f702();
        step_bounded_sample_or_status_a();
        reset_bounded_sample_status_b_monitor_3f88e();
      }
      step_bounded_sample_or_status_b();
    }
    if (param_2 == 0x202) {
      if (param_3 == 0x202) {
        step_baseline_sample_threshold_a();
      }
      else {
        reset_baseline_threshold_a_monitor_4087e();
        step_baseline_sample_threshold_a();
        reset_baseline_threshold_b_monitor_409f6();
      }
      step_baseline_sample_threshold_b();
    }
    if (param_2 == 0x203) {
      if (param_3 == 0x203) {
        step_requested_state_sample_threshold_a();
      }
      else {
        reset_requested_state_threshold_a_monitor_3fa1a();
        step_requested_state_sample_threshold_a();
        reset_requested_state_threshold_b_monitor_3fbf4();
      }
      step_requested_state_sample_threshold_b();
    }
    if (param_2 == 0x204) {
      if (param_3 == 0x204) {
        step_startup_status_bit_triplet_a();
      }
      else {
        reset_startup_triplet_a_and_control_41596();
        step_startup_status_bit_triplet_a();
        reset_startup_triplet_b_and_control_417ce();
      }
      step_startup_status_bit_triplet_b();
    }
    if (param_2 == 0x205) {
      if (param_3 == 0x205) {
        step_delayed_status_bit_triplet_a();
      }
      else {
        reset_delayed_triplet_a_and_67a4_state_3e5a6();
        step_delayed_status_bit_triplet_a();
        reset_delayed_triplet_b_and_67ac_state_3e83e();
      }
      step_delayed_status_bit_triplet_b();
    }
    if (param_2 == 0x206) {
      if (param_3 == 0x206) {
        step_command_status_bit_clear_a();
      }
      else {
        reset_command_status_a_monitor_and_delays_3f2d6();
        step_command_status_bit_clear_a();
        reset_command_status_b_monitor_and_delays_3f4ec();
      }
      step_command_status_bit_clear_b();
    }
    if (param_2 == 0x207) {
      if (param_3 == 0x207) {
        step_observed_state_sample_regions_a();
      }
      else {
        reset_observed_state_regions_a_monitor_40b6e();
        step_observed_state_sample_regions_a();
        reset_observed_state_regions_b_monitor_40e08();
      }
      step_observed_state_sample_regions_b();
    }
    if (param_2 == 0x208) {
      if (param_3 != 0x208) {
        reset_coupled_threshold_monitor_and_sequence_3eff0();
      }
      step_coupled_sample_threshold_both();
    }
    if (param_2 == 0x209) {
      if (param_3 == 0x209) {
        step_asserted_state_sample_threshold_a();
      }
      else {
        reset_asserted_state_sample_threshold_a_3fdce();
        step_asserted_state_sample_threshold_a();
        reset_asserted_state_sample_threshold_b_3ff08();
      }
      step_asserted_state_sample_threshold_b();
    }
    if (param_2 == 0x20a) {
      if (param_3 == 0x20a) {
        step_matched_state2_status_bit_a();
      }
      else {
        reset_matched_state2_a_monitor_and_delays_40402();
        step_matched_state2_status_bit_a();
        reset_matched_state2_b_monitor_and_delays_4063e();
      }
      step_matched_state2_status_bit_b();
    }
    if (param_2 == 0x20b) {
      if (param_3 == 0x20b) {
        step_sample_range_triplet_a();
      }
      else {
        reset_sample_range_triplet_a_and_control_410c0();
        step_sample_range_triplet_a();
        reset_sample_range_triplet_b_and_control_4132a();
      }
      step_sample_range_triplet_b();
    }
    if (param_2 == 0x20c) {
      if (param_3 == 0x20c) {
        step_matched_state2_startup_triplet_a();
      }
      else {
        reset_matched_startup_triplet_a_and_control_41a06();
        step_matched_state2_startup_triplet_a();
        reset_matched_startup_triplet_b_and_control_41c36();
      }
      step_matched_state2_startup_triplet_b();
    }
    if (param_2 == 0x20d) {
      if (param_3 == 0x20d) {
        step_matched_state2_status_bit_triplet_a();
      }
      else {
        reset_matched_state2_triplet_a_and_67b4_flags_3eadc();
        step_matched_state2_status_bit_triplet_a();
        reset_triplet_b_monitors_and_control_bytes_3ed0c();
      }
      step_matched_state2_status_bit_triplet_b();
    }
    if (uVar1 < 0xe) {
      if (0xd < param_3 - 0x200) {
        return_only_stub_3ef1a();
      }
      publish_monitor_failure_count_summary_wrapper_3efd4();
    }
  }
  if (param_2 - 0x301 < 0x222) {
    uVar1 = param_1 & 8;
    if (param_3 - 0x301 < 0x222) {
      if (uVar1 != 0) {
        step_paired_scalar_relation_monitor();
        step_qualified_scalar_relation_a_monitor();
        step_qualified_scalar_relation_b_monitor();
        step_admitted_scalar_receive_condition_monitor();
      }
    }
    else {
      reset_scalar_monitor_45838_45828();
      if (uVar1 != 0) {
        step_paired_scalar_relation_monitor();
      }
      reset_scalar_monitor_4599c_4598c();
      if (uVar1 != 0) {
        step_qualified_scalar_relation_a_monitor();
      }
      reset_scalar_monitor_45a6c_45a5c();
      if (uVar1 != 0) {
        step_qualified_scalar_relation_b_monitor();
      }
      reset_scalar_monitor_456fa_456ea();
      if (uVar1 != 0) {
        step_admitted_scalar_receive_condition_monitor();
      }
      return_only_stub_45b1e();
    }
    publish_scalar_relation_monitor_actions();
  }
  if (0x102 < param_2) {
    if (param_3 < 0x103) {
      clear_receive_fault_tracking_and_auxiliary_flags_3cb48();
      update_communication_qualification_monitors();
      return_only_stub_3ce62();
      publish_selected_source_fault_edges();
      return_only_stub_3d028();
      publish_source_family_fault_edges();
      return_only_stub_3d54c();
      report_6879_687a_fault_transitions_and_comm_status_3d54e();
      reset_latched_monitor_febe7490_3d426();
      update_received_content_monitor_a();
      reset_latched_monitor_febe749c_3d4c0();
      update_received_content_monitor_b();
      return_only_stub_3d31a();
    }
    else {
      update_communication_qualification_monitors();
      publish_selected_source_fault_edges();
      publish_source_family_fault_edges();
      report_6879_687a_fault_transitions_and_comm_status_3d54e();
      update_received_content_monitor_a();
      update_received_content_monitor_b();
    }
    compose_communication_status_fault_actions();
    uVar1 = param_1 & 0x10;
    if (param_3 < 0x103) {
      reset_scalar_monitor_45e74_45e64();
      if (uVar1 != 0) {
        step_raw_thermistor_range_a_monitor();
      }
      reset_scalar_monitor_45f32_45f22();
      if (uVar1 != 0) {
        step_raw_thermistor_range_b_monitor();
      }
      return_only_stub_45fd2();
      if (uVar1 != 0) goto LAB_0005f23e;
    }
    else if (uVar1 != 0) {
      step_raw_thermistor_range_a_monitor();
      step_raw_thermistor_range_b_monitor();
LAB_0005f23e:
      publish_thermistor_range_monitor_actions();
    }
    if (0x102 < param_2) {
      if (param_3 < 0x103) {
        reload_ba_admission_records();
        poll_ba_retained_start();
        clear_5f68_counter_and_status_state_35c02();
        run_5f6a_counter_update_35c38();
        fill_constant_block_35aea();
        check_paired_counters_and_clear_pending_flags_35b78();
        restore_monitor_current_calibration();
        refresh_monitor_current_calibration();
        thunk_classify_dual_record_validity_and_restore_halfwords_32398();
        refresh_both_requested_record_halfword_channels_32580();
        initialize_fit_and_record_205_validity_states_346f0();
        service_fit_revalidation_and_status_countdown_347e2();
        initialize_learned_quad_record_100_status_356c8();
      }
      else {
        poll_ba_retained_start();
        run_5f6a_counter_update_35c38();
        check_paired_counters_and_clear_pending_flags_35b78();
        refresh_monitor_current_calibration();
        refresh_both_requested_record_halfword_channels_32580();
        service_fit_revalidation_and_status_countdown_347e2();
      }
      step_learned_quad_record_completion();
    }
  }
  if (param_2 == 0x512) {
    if (param_3 != 0x512) {
      clear_state_byte_pair_6a5c_33d32();
    }
    step_fit_completion();
  }
  if (param_2 == 0x600) {
    if (param_3 == 0x600) {
      step_mode600_fit_request();
    }
    else {
      clear_state_bytes_6958_and_counter_695c_32c86();
      step_mode600_fit_request();
      clear_state_byte_pair_6a5c_33d32();
    }
    step_fit_completion();
  }
  if (param_2 - 0x101 < 0x10d) {
    if (0x10c < param_3 - 0x101) {
      initialize_redundant_bytes_and_vote_error_counters_31f18();
    }
    request_published_mode200_phase();
  }
  if (0x700 < param_2) {
    if (param_3 < 0x701) {
      initialize_thermal_shutdown_counter();
    }
    if ((param_1 >> 3 & 1) != 0) {
      step_thermal_shutdown_request();
    }
  }
  if (0x1ff < param_2) {
    param_1 = param_1 & 0x10;
    if (param_3 < 0x200) {
      initialize_6798_flag_and_countdown_360ce();
      update_signed_pair_threshold_countdown_360e0();
      initialize_two_six_sample_histories_3b134();
      if (param_1 != 0) {
        run_init_chain_3b398();
      }
      clear_eight_channel_7058_state_when_inactive_3b502();
      if (param_1 != 0) {
        restore_and_step_dual_thermal_offset_state_3b88e();
      }
      restore_thermal_drive_epoch_maxima();
      if (param_1 != 0) {
        update_thermal_drive_epoch_maxima();
      }
      return_only_stub_39758();
      if (param_1 != 0) {
        update_scaled_pair_sums_and_thermal_squared_inputs_3984a();
      }
      clear_6f34_if_588b6_returns_zero_39bfe();
      if (param_1 != 0) {
        update_ecu_source2_thermal_estimate();
      }
      initialize_6f68_half_ratio_constants_3a26c();
      if (param_1 != 0) {
        publish_ecu_source2_thermal_limit_maps();
      }
      clear_6f10_if_588b6_returns_zero_3991c();
      if (param_1 != 0) {
        update_ecu_source4_thermal_estimate();
      }
      initialize_6f30_half_ratio_constants_39bb2();
      if (param_1 != 0) {
        publish_ecu_source4_thermal_limit_maps();
      }
      clear_6eac_if_588b6_returns_zero_3905a();
      if (param_1 != 0) {
        update_ecu_source5_thermal_estimate();
      }
      initialize_6ee0_half_ratio_constants_39392();
      if (param_1 != 0) {
        publish_ecu_source5_thermal_limit_maps();
      }
      clear_6fe0_if_588b6_returns_zero_3acf8();
      if (param_1 != 0) {
        update_ecu_source3_thermal_estimate();
      }
      initialize_700c_half_ratio_constants_3b0e8();
      if (param_1 != 0) {
        publish_ecu_source3_thermal_limit_maps();
      }
      snapshot_6f06_and_6f08_halfwords_393de();
      poll_thermal_history_record_status();
      clear_6f80_if_588b6_returns_zero_3a55a();
      if (param_1 != 0) {
        update_motor_thermal_estimate();
      }
      initialize_6fac_half_ratio_constants_3a99c();
      if (param_1 != 0) {
        publish_motor_thermal_limit_maps();
      }
      fill_constant_block_3a2b8();
      arbitrate_thermal_current_limits();
      reset_latched_monitor_febe704c_3b468();
      if (param_1 != 0) {
        reset_or_step_704c_latched_monitor_3b478();
      }
      reset_latched_monitor_febe7040_3b3c0();
      if (param_1 != 0) {
        reset_or_step_7040_latched_monitor_3b3d0();
      }
      return_only_stub_3a9e8();
      if (param_1 == 0) goto LAB_0005f45c;
    }
    else {
      update_signed_pair_threshold_countdown_360e0();
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
      if (param_1 == 0) goto LAB_0005f45c;
      reset_or_step_704c_latched_monitor_3b478();
      reset_or_step_7040_latched_monitor_3b3d0();
    }
    update_thermal_history_qualification();
  }
LAB_0005f45c:
  publish_foreground_ecu_outputs();
  return;
}
