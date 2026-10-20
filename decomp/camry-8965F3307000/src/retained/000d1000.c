#include "common.h"

void restore_and_age_retained_cell_and_event_channels_d10d4(void)

{
  load_ae10_acf0_acef_record_increment_a5_c9e18();
  restore_event_pairs_and_increment_saturated_ages_cf442();
  return;
}

void clear_retained_cell_and_event_channel_state_d10e4(void)

{
  clear_c60c_c60e_c60f_record_c9e0a();
  clear_three_channel_event_markers_ages_and_counts_cf370();
  return;
}

void run_init_chain_d0a3e(void)

{
  initialize_assist_surface_selection();
  initialize_assist_torque_conditioner();
  initialize_torque_memory_correction();
  fill_constant_block_c7a76();
  reset_ac88_delta_filter_and_seed_gain_c557a();
  fill_constant_block_c589e();
  fill_constant_block_c59ae();
  fill_constant_block_c6138();
  fill_constant_block_c635a();
  reset_bf18_table_state_and_select_bank_pair_c28ae();
  fill_constant_block_c73c4();
  reset_c4a4_state_and_select_two_fixed_tables_c8642();
  fill_constant_block_c8970();
  reset_c310_curve_state_and_select_banked_tables_c6d84();
  initialize_nonlinear_torque_compensation();
  initialize_three_term_compensation();
  fill_constant_block_cc596();
  fill_constant_block_c962e();
  initialize_c7c4_fixed_point_control_state_cba80();
  clear_three_command_work_words_d0130();
  fill_constant_block_d04f0();
  fill_constant_block_d01b4();
  fill_constant_block_c79a0();
  initialize_torque_memory_gain();
  reset_c4c4_envelope_and_unity_gain_state_c873e();
  initialize_seven_c2f8_gain_slots_to_unity_c6be0();
  return;
}

void call_assist_command_update_slice_d1100(void)

{
  run_assist_command_slice();
  return;
}

void thunk_initialize_observer_and_waveform_state_chains_d0bda(void)

{
  initialize_observer_and_waveform_state_chains_d0bda();
  return;
}

void call_observer_and_waveform_publication_slice_d1118(void)

{
  run_observer_publication_slice();
  return;
}

void run_init_chain_d0ce8(void)

{
  fill_constant_block_c2c78();
  return_only_stub_c37b8();
  initialize_estimator_helpers_and_c048_state_c3edc();
  initialize_threshold_gain_and_lookup_result_d06ea();
  reset_c2a8_curve_filter_filter_and_gain_state_c66ce();
  reset_c3bc_curve_filter_filter_and_latches_c7540();
  fill_constant_block_c8df6();
  initialize_angle_rate_compensation();
  initialize_directional_rate_compensation();
  clear_c474_c476_curve_outputs_c81ee();
  reset_c478_filter_and_abb8_scaled_output_state_c8224();
  fill_constant_block_c9160();
  set_c5ac_status_one_c9562();
  fill_constant_block_c9590();
  fill_constant_block_c9c7c();
  fill_constant_block_c9df2();
  fill_constant_block_cc148();
  fill_constant_block_cc038();
  initialize_c79c_transition_filter_state_cb548();
  reset_c728_monitors_and_seed_twenty_samples_cb1e8();
  initialize_c868_curve_filter_state_cc530();
  fill_constant_block_c65f0();
  set_angle_controller_mode_seven_ceff4();
  fill_constant_block_ce750();
  fill_constant_block_cec0c();
  fill_constant_block_ce964();
  initialize_c898_ca78_redundant_control_state_cc9ac();
  initialize_angle_envelope_parameters_and_state_cf056();
  fill_constant_block_cf35c();
  fill_constant_block_cfd88();
  clear_waveform_curve_gain_pair_cff6e();
  return;
}

void thunk_run_cadence_gated_control_updates_and_publication_d0eec(void)

{
  run_cadence_gated_control_updates_and_publication_d0eec();
  return;
}

void thunk_clear_retained_cell_and_event_channel_state_d10e4(void)

{
  clear_retained_cell_and_event_channel_state_d10e4();
  return;
}

void thunk_restore_and_age_retained_cell_and_event_channels_d10d4(void)

{
  restore_and_age_retained_cell_and_event_channels_d10d4();
  return;
}

void call_publish_retained_estimator_projection_d1154(void)

{
  publish_retained_estimator_projection();
  return;
}

void call_snapshot_retained_estimator_projection_d1160(void)

{
  snapshot_retained_estimator_projection();
  return;
}

void thunk_publish_retained_cell_and_event_channel_snapshots_d0d6c(void)

{
  publish_retained_cell_and_event_channel_snapshots_d0d6c();
  return;
}

void store_saturated_signed16_absolute_d1178(short param_1,short *param_2)

{
  int iVar1;
  
  iVar1 = (int)param_1;
  if (iVar1 + 0x7fff < 0 == (-1 < iVar1 && iVar1 + 0x7fff < 0) && iVar1 != -0x7fff) {
    if (iVar1 < 0) {
      param_1 = -param_1;
    }
  }
  else {
    param_1 = 0x7fff;
  }
  *param_2 = param_1;
  return;
}

void store_saturated_signed32_absolute_d1194(int param_1,int *param_2)

{
  if (param_1 + 0x7fffffff < 0 == (-1 < param_1 && param_1 + 0x7fffffff < 0) &&
      param_1 != -0x7fffffff) {
    if (param_1 < 0) {
      param_1 = -param_1;
    }
  }
  else {
    param_1 = 0x7fffffff;
  }
  *param_2 = param_1;
  return;
}

void pack_two_low_words_as_big_endian_bytes_d11d6(undefined4 param_1,undefined4 param_2,undefined1 *param_3)

{
  *param_3 = (char)((uint)param_1 >> 8);
  param_3[1] = (char)param_1;
  param_3[2] = (char)((uint)param_2 >> 8);
  param_3[3] = (char)param_2;
  return;
}

void store_nonnegative_signed16_as_word_d1222(short param_1,int *param_2)

{
  int iVar1;
  
  iVar1 = (int)param_1;
  if (iVar1 < 1) {
    iVar1 = 0;
  }
  *param_2 = iVar1;
  return;
}

void scale_signed16_by_unsigned_ratio_with_symmetric_saturation_d1232(short param_1,uint param_2,uint param_3,short *param_4)

{
  int iVar1;
  int iVar2;
  
  param_3 = param_3 & 0xffff;
  if (((param_2 & 0xffff) != 0) && (param_3 != 0)) {
    iVar2 = (int)param_1 * (param_2 & 0xffff);
    if (param_3 != 0) {
      if (iVar2 == -0x80000000 && param_3 == 0xffffffff) {
        iVar2 = -0x80000000;
      }
      else {
        iVar2 = iVar2 / (int)param_3;
      }
    }
    if (iVar2 + 0x7fff < 0 == (-1 < iVar2 && iVar2 + 0x7fff < 0) && iVar2 != -0x7fff) {
      iVar1 = 0x7fff;
      if ((iVar2 + -0x7fff < 0 != (iVar2 < 0 && -1 < iVar2 + -0x7fff) || iVar2 == 0x7fff) &&
         (iVar1 = iVar2,
         iVar2 + 0x8000 < 0 != (-1 < iVar2 && iVar2 + 0x8000 < 0) || iVar2 == -0x8000)) {
        iVar1 = -0x8000;
      }
      param_1 = (short)iVar1;
    }
    else {
      param_1 = -0x7fff;
    }
  }
  *param_4 = param_1;
  return;
}

void scale_signed32_ratio_with_overflow_order_fallback_d1272(uint param_1,uint param_2,uint param_3,uint *param_4)

{
  uint uVar1;
  uint local_c;
  
  param_3 = param_3 & 0xffff;
  param_2 = param_2 & 0xffff;
  uVar1 = param_1;
  if ((param_2 == 0) || (uVar1 = param_1, param_3 == 0)) goto LAB_000d12c4;
  if ((int)((ulonglong)((longlong)(int)param_2 * (longlong)(int)param_1) >> 0x20) + 1U < 2) {
    uVar1 = param_1 * param_2;
    if ((int)param_1 < 0) {
      if (uVar1 < 0x80000001) goto LAB_000d12b4;
    }
    else if (0x7fffffff < (int)uVar1) goto LAB_000d12b4;
    if (param_3 != 0) {
      if (uVar1 == 0x80000000 && param_3 == 0xffffffff) {
        uVar1 = 0x80000000;
      }
      else {
        uVar1 = (int)uVar1 / (int)param_3;
      }
    }
  }
  else {
LAB_000d12b4:
    if (param_3 != 0) {
      if (param_1 == 0x80000000 && param_3 == 0xffffffff) {
        param_1 = 0x80000000;
      }
      else {
        param_1 = (int)param_1 / (int)param_3;
      }
    }
    store_symmetric_saturated_signed32_product_d2330(param_1,param_2,&local_c);
    uVar1 = local_c;
  }
LAB_000d12c4:
  local_c = uVar1;
  *param_4 = local_c;
  return;
}

void filter_unsigned_sample_accumulator
               (ushort *sample,uint coefficient,ushort *output,uint *accumulator)

{
  uint uVar1;
  
  if (0xfffe < coefficient - 1) {
    coefficient = 0x10000;
  }
  uVar1 = sample[1] * coefficient + (*(int *)(sample + 2) - *sample * coefficient);
  *output = (ushort)(uVar1 >> 0x10);
  *accumulator = uVar1;
  return;
}

void reset_application_latched_monitor(F33LatchedMonitorState *state)

{
  state->packed_status = 0;
  state->passing_count = 0;
  state->failing_count = 0;
  state->failing_high_water = 0;
  return;
}

uint step_application_latched_monitor
               (F33LatchedMonitorState *state,F33MonitorLimits *limits,
               F33TwoSidedMonitorCallbacks *callbacks)

{
  ushort uVar1;
  ushort uVar2;
  short sVar3;
  uint uVar4;
  uint uVar5;
  ushort uVar6;
  ushort uVar7;
  ushort uVar8;
  uint32_t pFVar9;
  
  uVar8 = state->failing_count;
  uVar7 = state->passing_count;
  uVar6 = state->failing_high_water;
  uVar1 = limits->passing_limit;
  uVar2 = limits->failing_limit;
  if (uVar8 == 0) {
    if (uVar1 < uVar7) {
      sVar3 = 0x2200;
    }
    else {
      sVar3 = 0;
      if (uVar7 != 0) {
        sVar3 = 0x1100;
      }
    }
  }
  else {
    sVar3 = 0x22;
    if (uVar8 <= uVar2) {
      sVar3 = 0x11;
    }
  }
  if (sVar3 == 0) {
    uVar5 = (*(int (*)())camry_indirect((uint32_t)(callbacks->classify_normal)))(camry_host_addr(state), camry_host_addr(limits), camry_host_addr(callbacks));
    if (uVar5 == 0x11) {
      if ((uVar1 < uVar7) || (uVar7 = uVar7 + 1, uVar1 < uVar7)) {
        uVar5 = 0x2200;
      }
      else {
        uVar5 = 0x11001100;
      }
      uVar8 = 0;
    }
    else if (uVar5 == 0x22) {
      uVar7 = 0;
      if (uVar8 <= uVar2) {
        uVar8 = uVar8 + 1;
      }
      uVar1 = uVar8;
      if (uVar8 <= uVar6) {
        uVar1 = uVar6;
      }
      uVar6 = uVar1;
      uVar5 = 0x22;
      if (uVar8 <= uVar2) {
        uVar5 = 0x110011;
      }
    }
    else if ((uVar5 == 0x33) || (uVar5 == 0x44)) {
      uVar7 = 0;
      uVar8 = 0;
      uVar5 = 0;
    }
    else {
      uVar5 = 0xffff;
    }
    uVar4 = uVar5 & 0xffff;
    if (uVar4 != 0) {
      if (uVar4 == 0x11) {
        if (callbacks->enter_failing !=0x0u) {
          (*(int (*)())camry_indirect((uint32_t)(callbacks->enter_failing)))();
        }
        pFVar9 = (uint32_t)((uint32_t)(callbacks->repeat_pending_failing));
      }
      else if (uVar4 == 0x22) {
        if (callbacks->enter_failing !=0x0u) {
          (*(int (*)())camry_indirect((uint32_t)(callbacks->enter_failing)))();
        }
        if (callbacks->confirm_failing !=0x0u) {
          (*(int (*)())camry_indirect((uint32_t)(callbacks->confirm_failing)))();
        }
        pFVar9 = (uint32_t)((uint32_t)(callbacks->repeat_confirmed_failing));
      }
      else if (uVar4 == 0x1100) {
        if (callbacks->enter_passing !=0x0u) {
          (*(int (*)())camry_indirect((uint32_t)(callbacks->enter_passing)))();
        }
        pFVar9 = (uint32_t)((uint32_t)(callbacks->repeat_pending_passing));
      }
      else {
        if (uVar4 != 0x2200) {
          uVar5 = 0;
          goto LAB_000d1812;
        }
        if (callbacks->enter_passing !=0x0u) {
          (*(int (*)())camry_indirect((uint32_t)(callbacks->enter_passing)))();
        }
        if (callbacks->confirm_passing !=0x0u) {
          (*(int (*)())camry_indirect((uint32_t)(callbacks->confirm_passing)))();
        }
        pFVar9 = (uint32_t)((uint32_t)(callbacks->repeat_confirmed_passing));
      }
      if ((uint32_t)(pFVar9) != 0u) {
        (*(int (*)())camry_indirect((uint32_t)(pFVar9)))();
      }
    }
    goto LAB_000d1812;
  }
  if (sVar3 == 0x11) {
    uVar5 = (*(int (*)())camry_indirect((uint32_t)(callbacks->classify_failing)))();
    if (uVar5 == 0x11) {
      if ((uVar1 < uVar7) || (uVar7 = uVar7 + 1, uVar1 < uVar7)) {
        uVar5 = 0x2200;
      }
      else {
        uVar5 = 0x11001100;
      }
      uVar8 = 0;
    }
    else if (uVar5 == 0x22) {
      uVar7 = 0;
      if (uVar8 <= uVar2) {
        uVar8 = uVar8 + 1;
      }
      uVar1 = uVar8;
      if (uVar8 <= uVar6) {
        uVar1 = uVar6;
      }
      uVar6 = uVar1;
      uVar5 = 0x22;
      if (uVar8 <= uVar2) {
        uVar5 = 0x110011;
      }
    }
    else if ((uVar5 == 0x33) || (uVar5 == 0x44)) {
      uVar7 = 0;
      uVar8 = 0;
      uVar5 = 0;
    }
    else {
      uVar5 = 0xffff;
    }
    uVar4 = uVar5 & 0xffff;
    if (uVar4 == 0) {
      if (callbacks->leave_pending_failing !=0x0u) {
        (*(int (*)())camry_indirect((uint32_t)(callbacks->leave_pending_failing)))(camry_host_addr(state), camry_host_addr(limits), camry_host_addr(callbacks));
      }
    }
    else {
      if (uVar4 == 0x11) {
        pFVar9 = (uint32_t)((uint32_t)(callbacks->repeat_pending_failing));
      }
      else if (uVar4 == 0x22) {
        if (callbacks->confirm_failing !=0x0u) {
          (*(int (*)())camry_indirect((uint32_t)(callbacks->confirm_failing)))();
        }
        pFVar9 = (uint32_t)((uint32_t)(callbacks->repeat_confirmed_failing));
      }
      else if (uVar4 == 0x1100) {
        if (callbacks->leave_pending_failing !=0x0u) {
          (*(int (*)())camry_indirect((uint32_t)(callbacks->leave_pending_failing)))();
        }
        if (callbacks->enter_passing !=0x0u) {
          (*(int (*)())camry_indirect((uint32_t)(callbacks->enter_passing)))();
        }
        pFVar9 = (uint32_t)((uint32_t)(callbacks->repeat_pending_passing));
      }
      else {
        if (uVar4 != 0x2200) {
          if (callbacks->repeat_pending_failing !=0x0u) {
            (*(int (*)())camry_indirect((uint32_t)(callbacks->repeat_pending_failing)))();
          }
          uVar5 = 0x11;
          goto LAB_000d1812;
        }
        if (callbacks->leave_pending_failing !=0x0u) {
          (*(int (*)())camry_indirect((uint32_t)(callbacks->leave_pending_failing)))();
        }
        if (callbacks->enter_passing !=0x0u) {
          (*(int (*)())camry_indirect((uint32_t)(callbacks->enter_passing)))();
        }
        if (callbacks->confirm_passing !=0x0u) {
          (*(int (*)())camry_indirect((uint32_t)(callbacks->confirm_passing)))();
        }
        pFVar9 = (uint32_t)((uint32_t)(callbacks->repeat_confirmed_passing));
      }
      if ((uint32_t)(pFVar9) != 0u) {
        (*(int (*)())camry_indirect((uint32_t)(pFVar9)))();
      }
    }
    goto LAB_000d1812;
  }
  if (sVar3 == 0x1100) {
    uVar5 = (*(int (*)())camry_indirect((uint32_t)(callbacks->classify_normal)))();
    if (uVar5 == 0x11) {
      if ((uVar1 < uVar7) || (uVar7 = uVar7 + 1, uVar1 < uVar7)) {
        uVar5 = 0x2200;
      }
      else {
        uVar5 = 0x11001100;
      }
      uVar8 = 0;
    }
    else if (uVar5 == 0x22) {
      uVar7 = 0;
      if (uVar8 <= uVar2) {
        uVar8 = uVar8 + 1;
      }
      uVar1 = uVar8;
      if (uVar8 <= uVar6) {
        uVar1 = uVar6;
      }
      uVar6 = uVar1;
      uVar5 = 0x22;
      if (uVar8 <= uVar2) {
        uVar5 = 0x110011;
      }
    }
    else if ((uVar5 == 0x33) || (uVar5 == 0x44)) {
      uVar7 = 0;
      uVar8 = 0;
      uVar5 = 0;
    }
    else {
      uVar5 = 0xffff;
    }
    uVar4 = uVar5 & 0xffff;
    if (uVar4 == 0) {
      if (callbacks->leave_pending_passing !=0x0u) {
        (*(int (*)())camry_indirect((uint32_t)(callbacks->leave_pending_passing)))(camry_host_addr(state), camry_host_addr(limits), camry_host_addr(callbacks));
      }
    }
    else {
      if (uVar4 == 0x11) {
        if (callbacks->leave_pending_passing !=0x0u) {
          (*(int (*)())camry_indirect((uint32_t)(callbacks->leave_pending_passing)))();
        }
        if (callbacks->enter_failing !=0x0u) {
          (*(int (*)())camry_indirect((uint32_t)(callbacks->enter_failing)))();
        }
        pFVar9 = (uint32_t)((uint32_t)(callbacks->repeat_pending_failing));
      }
      else if (uVar4 == 0x22) {
        if (callbacks->leave_pending_passing !=0x0u) {
          (*(int (*)())camry_indirect((uint32_t)(callbacks->leave_pending_passing)))();
        }
        if (callbacks->enter_failing !=0x0u) {
          (*(int (*)())camry_indirect((uint32_t)(callbacks->enter_failing)))();
        }
        if (callbacks->confirm_failing !=0x0u) {
          (*(int (*)())camry_indirect((uint32_t)(callbacks->confirm_failing)))();
        }
        pFVar9 = (uint32_t)((uint32_t)(callbacks->repeat_confirmed_failing));
      }
      else if (uVar4 == 0x1100) {
        pFVar9 = (uint32_t)((uint32_t)(callbacks->repeat_pending_passing));
      }
      else {
        if (uVar4 != 0x2200) {
          if (callbacks->repeat_pending_passing !=0x0u) {
            (*(int (*)())camry_indirect((uint32_t)(callbacks->repeat_pending_passing)))();
          }
          uVar5 = 0x1100;
          goto LAB_000d1812;
        }
        if (callbacks->confirm_passing !=0x0u) {
          (*(int (*)())camry_indirect((uint32_t)(callbacks->confirm_passing)))();
        }
        pFVar9 = (uint32_t)((uint32_t)(callbacks->repeat_confirmed_passing));
      }
      if ((uint32_t)(pFVar9) != 0u) {
        (*(int (*)())camry_indirect((uint32_t)(pFVar9)))(camry_host_addr(state), camry_host_addr(limits), camry_host_addr(callbacks));
      }
    }
    goto LAB_000d1812;
  }
  if (sVar3 != 0x2200) {
    if (callbacks->repeat_confirmed_failing !=0x0u) {
      (*(int (*)())camry_indirect((uint32_t)(callbacks->repeat_confirmed_failing)))();
    }
    uVar5 = 0x22;
    goto LAB_000d1812;
  }
  uVar5 = (*(int (*)())camry_indirect((uint32_t)(callbacks->classify_normal)))();
  if (uVar5 == 0x11) {
LAB_000d1422:
    uVar8 = 0;
LAB_000d1424:
    uVar5 = 0x2200;
  }
  else {
    if (uVar5 != 0x22) {
      if ((uVar5 == 0x33) || (uVar5 == 0x44)) goto LAB_000d1422;
      goto LAB_000d1424;
    }
    uVar7 = 0;
    if (uVar8 <= uVar2) {
      uVar8 = uVar8 + 1;
    }
    uVar1 = uVar8;
    if (uVar8 <= uVar6) {
      uVar1 = uVar6;
    }
    uVar6 = uVar1;
    uVar5 = 0x22;
    if (uVar8 <= uVar2) {
      uVar5 = 0x110011;
    }
  }
  uVar4 = uVar5 & 0xffff;
  if (uVar4 == 0) {
    if (callbacks->leave_confirmed_passing !=0x0u) {
      (*(int (*)())camry_indirect((uint32_t)(callbacks->leave_confirmed_passing)))();
    }
  }
  else {
    if (uVar4 == 0x11) {
      if (callbacks->leave_confirmed_passing !=0x0u) {
        (*(int (*)())camry_indirect((uint32_t)(callbacks->leave_confirmed_passing)))();
      }
      if (callbacks->enter_failing !=0x0u) {
        (*(int (*)())camry_indirect((uint32_t)(callbacks->enter_failing)))();
      }
      pFVar9 = (uint32_t)((uint32_t)(callbacks->repeat_pending_failing));
    }
    else if (uVar4 == 0x22) {
      if (callbacks->leave_confirmed_passing !=0x0u) {
        (*(int (*)())camry_indirect((uint32_t)(callbacks->leave_confirmed_passing)))();
      }
      if (callbacks->enter_failing !=0x0u) {
        (*(int (*)())camry_indirect((uint32_t)(callbacks->enter_failing)))();
      }
      if (callbacks->confirm_failing !=0x0u) {
        (*(int (*)())camry_indirect((uint32_t)(callbacks->confirm_failing)))();
      }
      pFVar9 = (uint32_t)((uint32_t)(callbacks->repeat_confirmed_failing));
    }
    else {
      pFVar9 = (uint32_t)((uint32_t)(callbacks->repeat_confirmed_passing));
      if (uVar4 != 0x2200) {
        if ((uint32_t)(pFVar9) != 0u) {
          (*(int (*)())camry_indirect((uint32_t)(pFVar9)))();
        }
        uVar5 = 0x2200;
        goto LAB_000d1812;
      }
    }
    if ((uint32_t)(pFVar9) != 0u) {
      (*(int (*)())camry_indirect((uint32_t)(pFVar9)))(camry_host_addr(state), camry_host_addr(limits), camry_host_addr(callbacks));
    }
  }
LAB_000d1812:
  state->packed_status = uVar5;
  state->passing_count = uVar7;
  state->failing_count = uVar8;
  state->failing_high_water = uVar6;
  return 0x11;
}

undefined4 advance_dual_counter_qualification_and_dispatch_callbacks_d1824(uint *param_1,ushort *param_2,undefined4 *param_3)

{
  ushort uVar1;
  ushort uVar2;
  ushort uVar3;
  ushort uVar4;
  short sVar5;
  uint uVar6;
  uint uVar7;
  int iVar8;
  ushort uVar9;
  ushort uVar10;
  ushort uVar11;
  ushort uVar12;
  ushort uVar13;
  uint32_t pcVar14;
  
  uVar11 = (ushort)param_1[1];
  uVar10 = (*((ushort *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 6))));
  uVar13 = (ushort)param_1[2];
  uVar12 = (*((ushort *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 10))));
  uVar9 = (ushort)param_1[3];
  uVar1 = param_2[1];
  uVar2 = *param_2;
  uVar3 = param_2[2];
  uVar4 = param_2[3];
  if (uVar13 == 0) {
    if (uVar2 < uVar11) {
      sVar5 = 0x2200;
    }
    else {
      sVar5 = 0;
      if (uVar11 != 0) {
        sVar5 = 0x1100;
      }
    }
  }
  else {
    sVar5 = 0x22;
    if (uVar13 <= uVar3) {
      sVar5 = 0x11;
    }
  }
  if (sVar5 == 0) {
    iVar8 = (*(int (*)())camry_indirect((uint32_t)(*param_3)))(camry_host_addr(param_1), camry_host_addr(param_2), camry_host_addr(param_3));
    if (iVar8 == 0x11) {
      if ((uVar1 < uVar10) || (uVar10 = uVar10 + 1, uVar1 < uVar10)) {
        uVar11 = 0;
        uVar10 = 0;
        uVar6 = 0;
      }
      else if ((uVar2 < uVar11) || (uVar11 = uVar11 + 1, uVar2 < uVar11)) {
        uVar6 = 0x2200;
      }
      else {
        uVar6 = 0x11001100;
      }
      uVar13 = 0;
      uVar12 = 0;
    }
    else if (iVar8 == 0x22) {
      uVar11 = 0;
      uVar10 = 0;
      if ((uVar4 < uVar12) || (uVar12 = uVar12 + 1, uVar4 < uVar12)) goto LAB_000d1b52;
      if (uVar13 <= uVar3) {
        uVar13 = uVar13 + 1;
      }
      uVar1 = uVar13;
      if (uVar13 <= uVar9) {
        uVar1 = uVar9;
      }
      uVar9 = uVar1;
      uVar6 = 0x22;
      if (uVar13 <= uVar3) {
        uVar6 = 0x110011;
      }
    }
    else if ((iVar8 == 0x33) || (iVar8 == 0x44)) {
LAB_000d1b52:
      uVar11 = 0;
      uVar10 = 0;
      uVar12 = 0;
      uVar6 = 0;
      uVar13 = uVar10;
    }
    else {
      uVar6 = 0;
    }
    uVar7 = uVar6 & 0xffff;
    if (uVar7 != 0) {
      if (uVar7 == 0x11) {
        if ((uint32_t)(param_3[6] )!=0x0u) {
          (*(int (*)())camry_indirect((uint32_t)(param_3[6])))();
        }
        pcVar14 = (uint32_t)((uint32_t)(param_3[0xb]));
      }
      else if (uVar7 == 0x22) {
        if ((uint32_t)(param_3[6] )!=0x0u) {
          (*(int (*)())camry_indirect((uint32_t)(param_3[6])))();
        }
        if ((uint32_t)(param_3[8] )!=0x0u) {
          (*(int (*)())camry_indirect((uint32_t)(param_3[8])))();
        }
        pcVar14 = (uint32_t)((uint32_t)(param_3[0xc]));
      }
      else if (uVar7 == 0x1100) {
        if ((uint32_t)(param_3[2] )!=0x0u) {
          (*(int (*)())camry_indirect((uint32_t)(param_3[2])))();
        }
        pcVar14 = (uint32_t)((uint32_t)(param_3[9]));
      }
      else {
        if (uVar7 != 0x2200) {
          uVar6 = 0;
          goto LAB_000d1cc6;
        }
        if ((uint32_t)(param_3[2] )!=0x0u) {
          (*(int (*)())camry_indirect((uint32_t)(param_3[2])))();
        }
        if ((uint32_t)(param_3[4] )!=0x0u) {
          (*(int (*)())camry_indirect((uint32_t)(param_3[4])))();
        }
        pcVar14 = (uint32_t)((uint32_t)(param_3[10]));
      }
      if ((uint32_t)(pcVar14) != 0u) {
        (*(int (*)())camry_indirect((uint32_t)(pcVar14)))();
      }
    }
    goto LAB_000d1cc6;
  }
  if (sVar5 == 0x11) {
    iVar8 = (*(int (*)())camry_indirect((uint32_t)(param_3[1])))();
    if ((uVar4 < uVar12) || (uVar12 = uVar12 + 1, uVar4 < uVar12)) {
LAB_000d1c4e:
      uVar11 = 0;
      uVar10 = 0;
      uVar13 = 0;
      uVar12 = 0;
      uVar6 = 0;
    }
    else {
      if (iVar8 == 0x11) {
LAB_000d1c48:
        uVar11 = 0;
        uVar10 = uVar11;
      }
      else {
        if (iVar8 == 0x22) {
          uVar11 = 0;
          uVar10 = 0;
          if (uVar13 <= uVar3) {
            uVar13 = uVar13 + 1;
          }
          uVar1 = uVar13;
          if (uVar13 <= uVar9) {
            uVar1 = uVar9;
          }
          uVar9 = uVar1;
          uVar6 = 0x22;
          if (uVar13 <= uVar3) {
            uVar6 = 0x110011;
          }
          goto LAB_000d1c58;
        }
        if (iVar8 == 0x33) goto LAB_000d1c48;
        if (iVar8 == 0x44) goto LAB_000d1c4e;
      }
      uVar6 = 0x11;
    }
LAB_000d1c58:
    uVar7 = uVar6 & 0xffff;
    if (uVar7 == 0) {
      if ((uint32_t)(param_3[7] )!=0x0u) {
        (*(int (*)())camry_indirect((uint32_t)(param_3[7])))(camry_host_addr(param_1), camry_host_addr(param_2), camry_host_addr(param_3));
      }
    }
    else {
      if (uVar7 == 0x11) {
        pcVar14 = (uint32_t)((uint32_t)(param_3[0xb]));
      }
      else {
        if (uVar7 != 0x22) {
          if ((uint32_t)(param_3[0xb] )!=0x0u) {
            (*(int (*)())camry_indirect((uint32_t)(param_3[0xb])))();
          }
          uVar6 = 0x11;
          goto LAB_000d1cc6;
        }
        if ((uint32_t)(param_3[8] )!=0x0u) {
          (*(int (*)())camry_indirect((uint32_t)(param_3[8])))();
        }
        pcVar14 = (uint32_t)((uint32_t)(param_3[0xc]));
      }
      if ((uint32_t)(pcVar14) != 0u) {
        (*(int (*)())camry_indirect((uint32_t)(pcVar14)))();
      }
    }
    goto LAB_000d1cc6;
  }
  if (sVar5 == 0x1100) {
    iVar8 = (*(int (*)())camry_indirect((uint32_t)(*param_3)))();
    if ((uVar1 < uVar10) || (uVar10 = uVar10 + 1, uVar1 < uVar10)) {
LAB_000d1a0c:
      uVar11 = 0;
      uVar10 = 0;
      uVar12 = 0;
      uVar6 = 0;
      uVar13 = uVar10;
    }
    else if (iVar8 == 0x11) {
      if ((uVar2 < uVar11) || (uVar11 = uVar11 + 1, uVar2 < uVar11)) {
        uVar6 = 0x2200;
      }
      else {
        uVar6 = 0x11001100;
      }
      uVar13 = 0;
      uVar12 = 0;
    }
    else if (iVar8 == 0x22) {
      uVar11 = 0;
      uVar10 = 0;
      if ((uVar4 < uVar12) || (uVar12 = uVar12 + 1, uVar4 < uVar12)) goto LAB_000d1a0c;
      if (uVar13 <= uVar3) {
        uVar13 = uVar13 + 1;
      }
      uVar1 = uVar13;
      if (uVar13 <= uVar9) {
        uVar1 = uVar9;
      }
      uVar9 = uVar1;
      uVar6 = 0x22;
      if (uVar13 <= uVar3) {
        uVar6 = 0x110011;
      }
    }
    else {
      if (iVar8 == 0x33) {
        uVar13 = 0;
        uVar12 = uVar13;
      }
      else if (iVar8 == 0x44) goto LAB_000d1a0c;
      uVar6 = 0x1100;
    }
    uVar7 = uVar6 & 0xffff;
    if (uVar7 == 0) {
      if ((uint32_t)(param_3[3] )!=0x0u) {
        (*(int (*)())camry_indirect((uint32_t)(param_3[3])))();
      }
    }
    else {
      if (uVar7 == 0x11) {
        if ((uint32_t)(param_3[3] )!=0x0u) {
          (*(int (*)())camry_indirect((uint32_t)(param_3[3])))();
        }
        if ((uint32_t)(param_3[6] )!=0x0u) {
          (*(int (*)())camry_indirect((uint32_t)(param_3[6])))();
        }
        pcVar14 = (uint32_t)((uint32_t)(param_3[0xb]));
      }
      else if (uVar7 == 0x22) {
        if ((uint32_t)(param_3[3] )!=0x0u) {
          (*(int (*)())camry_indirect((uint32_t)(param_3[3])))();
        }
        if ((uint32_t)(param_3[6] )!=0x0u) {
          (*(int (*)())camry_indirect((uint32_t)(param_3[6])))();
        }
        if ((uint32_t)(param_3[8] )!=0x0u) {
          (*(int (*)())camry_indirect((uint32_t)(param_3[8])))(camry_host_addr(param_1), camry_host_addr(param_2), camry_host_addr(param_3));
        }
        pcVar14 = (uint32_t)((uint32_t)(param_3[0xc]));
      }
      else if (uVar7 == 0x1100) {
        pcVar14 = (uint32_t)((uint32_t)(param_3[9]));
      }
      else {
        if (uVar7 != 0x2200) {
          if ((uint32_t)(param_3[9] )!=0x0u) {
            (*(int (*)())camry_indirect((uint32_t)(param_3[9])))();
          }
          uVar6 = 0x1100;
          goto LAB_000d1cc6;
        }
        if ((uint32_t)(param_3[4] )!=0x0u) {
          (*(int (*)())camry_indirect((uint32_t)(param_3[4])))();
        }
        pcVar14 = (uint32_t)((uint32_t)(param_3[10]));
      }
      if ((uint32_t)(pcVar14) != 0u) {
        (*(int (*)())camry_indirect((uint32_t)(pcVar14)))();
      }
    }
    goto LAB_000d1cc6;
  }
  if (sVar5 != 0x2200) {
    if ((uint32_t)(param_3[0xc] )!=0x0u) {
      (*(int (*)())camry_indirect((uint32_t)(param_3[0xc])))();
    }
    uVar6 = 0x22;
    goto LAB_000d1cc6;
  }
  iVar8 = (*(int (*)())camry_indirect((uint32_t)(*param_3)))();
  if (iVar8 == 0x11) {
LAB_000d18e0:
    uVar13 = 0;
    uVar12 = 0;
LAB_000d18e4:
    uVar6 = 0x2200;
  }
  else {
    if (iVar8 != 0x22) {
      if ((iVar8 == 0x33) || (iVar8 == 0x44)) goto LAB_000d18e0;
      goto LAB_000d18e4;
    }
    uVar11 = 0;
    uVar10 = 0;
    if ((uVar4 < uVar12) || (uVar12 = uVar12 + 1, uVar4 < uVar12)) {
      uVar13 = 0;
      uVar12 = 0;
      uVar6 = 0;
    }
    else {
      if (uVar13 <= uVar3) {
        uVar13 = uVar13 + 1;
      }
      uVar1 = uVar13;
      if (uVar13 <= uVar9) {
        uVar1 = uVar9;
      }
      uVar9 = uVar1;
      uVar6 = 0x22;
      if (uVar13 <= uVar3) {
        uVar6 = 0x110011;
      }
    }
  }
  uVar7 = uVar6 & 0xffff;
  if (uVar7 == 0) {
    if ((uint32_t)(param_3[5] )!=0x0u) {
      (*(int (*)())camry_indirect((uint32_t)(param_3[5])))();
    }
  }
  else {
    if (uVar7 == 0x11) {
      if ((uint32_t)(param_3[5] )!=0x0u) {
        (*(int (*)())camry_indirect((uint32_t)(param_3[5])))();
      }
      if ((uint32_t)(param_3[6] )!=0x0u) {
        (*(int (*)())camry_indirect((uint32_t)(param_3[6])))(camry_host_addr(param_1), camry_host_addr(param_2), camry_host_addr(param_3));
      }
      pcVar14 = (uint32_t)((uint32_t)(param_3[0xb]));
    }
    else if (uVar7 == 0x22) {
      if ((uint32_t)(param_3[5] )!=0x0u) {
        (*(int (*)())camry_indirect((uint32_t)(param_3[5])))();
      }
      if ((uint32_t)(param_3[6] )!=0x0u) {
        (*(int (*)())camry_indirect((uint32_t)(param_3[6])))();
      }
      if ((uint32_t)(param_3[8] )!=0x0u) {
        (*(int (*)())camry_indirect((uint32_t)(param_3[8])))();
      }
      pcVar14 = (uint32_t)((uint32_t)(param_3[0xc]));
    }
    else {
      pcVar14 = (uint32_t)((uint32_t)(param_3[10]));
      if (uVar7 != 0x2200) {
        if ((uint32_t)(pcVar14) != 0u) {
          (*(int (*)())camry_indirect((uint32_t)(pcVar14)))();
        }
        uVar6 = 0x2200;
        goto LAB_000d1cc6;
      }
    }
    if ((uint32_t)(pcVar14) != 0u) {
      (*(int (*)())camry_indirect((uint32_t)(pcVar14)))(camry_host_addr(param_1), camry_host_addr(param_2), camry_host_addr(param_3));
    }
  }
LAB_000d1cc6:
  *param_1 = uVar6;
  *(ushort *)(param_1 + 1) = uVar11;
  (*((ushort *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 6)))) = uVar10;
  *(ushort *)(param_1 + 2) = uVar13;
  (*((ushort *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 10)))) = uVar12;
  *(ushort *)(param_1 + 3) = uVar9;
  return 0x11;
}

void store_signed16_clamped_between_upper_and_lower_d1cdc(short param_1,short param_2,short param_3,short *param_4)

{
  int iVar1;
  int iVar2;
  int iVar3;
  
  iVar1 = (int)param_1;
  iVar2 = (int)param_2;
  iVar3 = (int)param_3;
  if (iVar2 - iVar1 < 0 != (iVar2 < 0 != iVar1 < 0 && iVar1 < 0 == iVar2 - iVar1 < 0)) {
    iVar1 = iVar2;
  }
  if (iVar3 - iVar1 < 0 != (iVar3 < 0 != iVar1 < 0 && iVar1 < 0 == iVar3 - iVar1 < 0) ||
      iVar3 == iVar1) {
    param_3 = (short)iVar1;
  }
  *param_4 = param_3;
  return;
}

void store_signed32_clamped_between_upper_and_lower_d1cf6(int param_1,int param_2,int param_3,int *param_4)

{
  if (param_2 - param_1 < 0 != (param_2 < 0 != param_1 < 0 && param_1 < 0 == param_2 - param_1 < 0))
  {
    param_1 = param_2;
  }
  if (param_3 - param_1 < 0 == (param_3 < 0 != param_1 < 0 && param_1 < 0 == param_3 - param_1 < 0)
      && param_3 != param_1) {
    param_1 = param_3;
  }
  *param_4 = param_1;
  return;
}

void store_signed_halfword_max(short value,short bound,short *output)

{
  int iVar1;
  int iVar2;
  
  iVar1 = (int)value;
  iVar2 = (int)bound;
  if (iVar2 - iVar1 < 0 == (iVar2 < 0 != iVar1 < 0 && iVar1 < 0 == iVar2 - iVar1 < 0) &&
      iVar2 != iVar1) {
    value = bound;
  }
  *output = value;
  return;
}

void limit_unsigned16_value_to_asymmetric_step_band_d1d1c(ushort *param_1,undefined2 *param_2)

{
  uint uVar1;
  uint uVar2;
  uint uVar3;
  
  uVar3 = (uint)*param_1;
  uVar1 = (uint)param_1[1] - (uint)param_1[3];
  uVar2 = (uint)param_1[2] + (uint)param_1[1];
  if (((int)(uVar3 - uVar2) < 0 || uVar3 == uVar2) &&
     (uVar2 = uVar3,
     (int)(uVar1 - uVar3) < 0 == ((int)uVar1 < 0 && -1 < (int)(uVar1 - uVar3)) && uVar1 != uVar3)) {
    uVar2 = uVar1;
  }
  *param_2 = (short)uVar2;
  return;
}

void store_signed_halfword_min(short value,short bound,short *output)

{
  int iVar1;
  int iVar2;
  
  iVar2 = (int)value;
  iVar1 = bound - iVar2;
  if (iVar1 < 0 != (bound < 0 != iVar2 < 0 && iVar2 < 0 == iVar1 < 0)) {
    value = bound;
  }
  *output = value;
  return;
}

void store_signed32_minimum_d1d4e(int param_1,int param_2,int *param_3)

{
  if (param_2 - param_1 < 0 != (param_2 < 0 != param_1 < 0 && param_1 < 0 == param_2 - param_1 < 0))
  {
    param_1 = param_2;
  }
  *param_3 = param_1;
  return;
}

void store_unsigned16_minimum_d1d5c(ushort param_1,ushort param_2,ushort *param_3)

{
  if (param_2 < param_1) {
    param_1 = param_2;
  }
  *param_3 = param_1;
  return;
}

void store_unsigned32_minimum_d1d6e(uint param_1,uint param_2,uint *param_3)

{
  if (param_2 < param_1) {
    param_1 = param_2;
  }
  *param_3 = param_1;
  return;
}

void interpolate_signed16_pairs_to_output_d1de4(short *param_1,short param_2,short *param_3)

{
  short *psVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  short sVar5;
  
  iVar4 = (int)param_2;
  iVar2 = (int)*param_1;
  if ((iVar2 == 0x7fff) ||
     (iVar2 - iVar4 < 0 == (iVar2 < 0 != iVar4 < 0 && iVar4 < 0 == iVar2 - iVar4 < 0))) {
    sVar5 = param_1[1];
  }
  else {
    iVar2 = 0;
    while( true ) {
      psVar1 = param_1 + iVar2 * 2;
      iVar3 = (int)*psVar1;
      if (iVar3 == 0x7fff) break;
      if (iVar3 - iVar4 < 0 == (iVar3 < 0 != iVar4 < 0 && iVar4 < 0 == iVar3 - iVar4 < 0) &&
          iVar3 != iVar4) {
        iVar3 = iVar3 - psVar1[-2];
        iVar2 = (iVar4 - psVar1[-2]) * ((int)psVar1[1] - (int)psVar1[-1]);
        if (iVar3 != 0) {
          if (iVar2 == -0x80000000 && iVar3 == -1) {
            iVar2 = 0;
          }
          else {
            iVar2 = (int)iVar2 / (int)iVar3;
          }
        }
        sVar5 = psVar1[-1] + (short)iVar2;
        goto LAB_000d1e32;
      }
      iVar2 = iVar2 + 1;
    }
    sVar5 = psVar1[-1];
  }
LAB_000d1e32:
  *param_3 = sVar5;
  return;
}

void interpolate_unsigned16_axis_signed16_values_to_output_d1e8c(ushort *param_1,uint param_2,ushort *param_3)

{
  ushort *puVar1;
  ushort uVar2;
  int iVar3;
  int iVar4;
  uint uVar5;
  
  param_2 = param_2 & 0xffff;
  if ((*param_1 == 0xffff) || (param_2 <= *param_1)) {
    uVar2 = param_1[1];
  }
  else {
    iVar3 = 0;
    while( true ) {
      puVar1 = param_1 + iVar3 * 2;
      uVar5 = (uint)*puVar1;
      if (uVar5 == 0xffff) break;
      if (param_2 < uVar5) {
        iVar3 = uVar5 - puVar1[-2];
        iVar4 = (param_2 - puVar1[-2]) * ((int)(short)puVar1[1] - (int)(short)puVar1[-1]);
        if (iVar3 != 0) {
          if (iVar4 == -0x80000000 && iVar3 == -1) {
            iVar4 = 0;
          }
          else {
            iVar4 = (int)iVar4 / (int)iVar3;
          }
        }
        uVar2 = puVar1[-1] + (short)iVar4;
        goto LAB_000d1eda;
      }
      iVar3 = iVar3 + 1;
    }
    uVar2 = puVar1[-1];
  }
LAB_000d1eda:
  *param_3 = uVar2;
  return;
}

void interpolate_unsigned16_pairs_to_output_d1ee0(ushort *param_1,uint param_2,ushort *param_3)

{
  ushort *puVar1;
  ushort uVar2;
  int iVar3;
  int iVar4;
  uint uVar5;
  
  param_2 = param_2 & 0xffff;
  if ((*param_1 == 0xffff) || (param_2 <= *param_1)) {
    uVar2 = param_1[1];
  }
  else {
    iVar3 = 0;
    while( true ) {
      puVar1 = param_1 + iVar3 * 2;
      uVar5 = (uint)*puVar1;
      if (uVar5 == 0xffff) break;
      if (param_2 < uVar5) {
        iVar3 = uVar5 - puVar1[-2];
        iVar4 = (param_2 - puVar1[-2]) * ((uint)puVar1[1] - (uint)puVar1[-1]);
        if (iVar3 != 0) {
          if (iVar4 == -0x80000000 && iVar3 == -1) {
            iVar4 = 0;
          }
          else {
            iVar4 = (int)iVar4 / (int)iVar3;
          }
        }
        uVar2 = puVar1[-1] + (short)iVar4;
        goto LAB_000d1f2e;
      }
      iVar3 = iVar3 + 1;
    }
    uVar2 = puVar1[-1];
  }
LAB_000d1f2e:
  *param_3 = uVar2;
  return;
}
