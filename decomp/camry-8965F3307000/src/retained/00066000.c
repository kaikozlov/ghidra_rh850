#include "common.h"

void run_ch2_application_task(void)

{
  uint32_t puVar1;
  int iVar2;
  
  puVar1 = 0xfebeb800u;
  iVar2 = 0;
  if (execution_profiling_enabled == 'Z') {
    puVar1 = 0xfebeb800u;
    begin_execution_profile_slot3();
    iVar2 = 0x5a;
  }
  supervise_scheduled_progress();
  run_init_chain_667b6();
  if (iVar2 == 0x5a) {
    end_execution_profile_slot3();
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x7e26))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x7e26))))) + '\x01';
  return;
}

void run_eic136_foreground_dispatch_loop_66062(void)

{
  byte bVar1;
  undefined8 uVar2;
  int iVar3;
  char *pcVar4;
  
  uVar2 = 0xfebeb800;
  do {
    do {
      bVar1 = (*((volatile uint8_t *)camry_host_ptr(0xffffb111u)));
    } while ((bVar1 & 0x10) == 0);
    bVar1 = (*((volatile uint8_t *)camry_host_ptr(0xffffb111u)));
    (*((volatile uint8_t *)camry_host_ptr(0xffffb111u))) = bVar1 & 0xef;
    iVar3 = 0;
    if (execution_profiling_enabled == 'Z') {
      begin_execution_profile_slot5();
      iVar3 = 0x5a;
    }
    record_foreground_dispatch();
    save_registers_switch_stack_apply_mpu_profile_71378();
    thunk_service_nvm_acquisition_driver_wrapper_68318();
    apply_mpu_profile_restore_stack_and_registers_71398();
    foreground_subsystem_cycle();
    save_registers_switch_stack_apply_mpu_profile_71378();
    nvm_application_cycle();
    apply_mpu_profile_restore_stack_and_registers_71398();
    if (iVar3 == 0x5a) {
      end_execution_profile_slot5();
    }
    pcVar4 = ((char *)camry_host_ptr((uint32_t)((int)uVar2 + -0x7e25)));
    *pcVar4 = *pcVar4 + '\x01';
  } while( true );
}

void initialize_ffe20000_compare_registers_661fc(void)

{
  short sVar1;
  ushort uVar2;
  
  Ramffe20240 = 0x40;
  DAT_ffe20244 = 0;
  Ramffe20200 = 0;
  Ramffe20204 = 0x4000;
  Ramffe2020c = 0;
  Ramffe20214 = 0;
  Ramffe20220 = 0x4000;
  Ramffe20238 = 0x4000;
  DAT_ffe200c0 = 0;
  DAT_ffe200c4 = 0;
  DAT_ffe200cc = 0;
  DAT_ffe200d4 = 0;
  DAT_ffe200e0 = 0;
  DAT_ffe200f8 = 0;
  Ramffe20000 = DAT_00030e16 + DAT_00030e14 + -1;
  Ramffe20004 = DAT_00030e1a + DAT_00030e18 + -1;
  Ramffe2000c = DAT_00030e1e + DAT_00030e1c + -1;
  Ramffe20014 = (short)PTR_LAB_00030e22 + DAT_00030e20 + -1;
  sVar1 = DAT_00030e12 + DAT_00030e10 + -1;
  Ramffe20020 = sVar1;
  Ramffe20038 = sVar1;
  uVar2 = Ramffe2005c;
  Ramffe2005c = uVar2 & 0xbed4;
  uVar2 = Ramffe20058;
  Ramffe20058 = uVar2 & 0xbed4;
  uVar2 = Ramffe20260;
  Ramffe20260 = uVar2 & 0xbed4;
  uVar2 = Ramffe20268;
  Ramffe20268 = uVar2 & 0xbed4;
  uVar2 = Ramffe20264;
  Ramffe20264 = uVar2 & 0xbed4;
  uVar2 = Ramffe2026c;
  Ramffe2026c = uVar2 & 0xbed4;
  return;
}

void initialize_ffe21000_compare_registers_662dc(void)

{
  ushort uVar1;
  
  Ramffe21240 = 0x40;
  DAT_ffe21244 = 0;
  Ramffe21200 = 0;
  Ramffe21204 = 0x4000;
  Ramffe2120c = 0;
  Ramffe21214 = 0;
  DAT_ffe210c0 = 0;
  DAT_ffe210c4 = 0;
  DAT_ffe210cc = 0;
  DAT_ffe210d4 = 0;
  Ramffe21000 = DAT_00030e16 + DAT_00030e14 + -1;
  Ramffe21004 = DAT_00030e1a + DAT_00030e18 + -1;
  Ramffe2100c = DAT_00030e1e + DAT_00030e1c + -1;
  Ramffe21014 = (short)PTR_LAB_00030e22 + DAT_00030e20 + -1;
  uVar1 = Ramffe2105c;
  Ramffe2105c = uVar1 & 0xffd4;
  uVar1 = Ramffe21058;
  Ramffe21058 = uVar1 & 0xffd4;
  uVar1 = Ramffe21260;
  Ramffe21260 = uVar1 & 0xffd4;
  uVar1 = Ramffe21268;
  Ramffe21268 = uVar1 & 0xffd4;
  uVar1 = Ramffe21264;
  Ramffe21264 = uVar1 & 0xffd4;
  uVar1 = Ramffe2126c;
  Ramffe2126c = uVar1 & 0xffd4;
  return;
}

void initialize_tauj0_four_channels_6639c(void)

{
  byte bVar1;
  
  TAUJ0TPS = 0;
  (*((volatile uint8_t *)camry_host_ptr(0xffe50094u))) = 0;
  TAUJ0CMOR0 = 0;
  TAUJ0CMOR1 = 0;
  TAUJ0CMOR2 = 0;
  TAUJ0CMOR3 = 0;
  TAUJ0CMUR0 = '\0';
  TAUJ0CMUR1 = '\0';
  TAUJ0CMUR2 = '\0';
  TAUJ0CMUR3 = '\0';
  TAUJ0CDR0 = (uint)(PTR_FUN_00030df0 + DAT_00030df4 + -1);
  TAUJ0CDR1 = (DAT_00030dfc + DAT_00030df8) - 1;
  TAUJ0CDR2 = (DAT_00030e04 + DAT_00030e00) - 1;
  TAUJ0CDR3 = (DAT_00030e0c + DAT_00030e08) - 1;
  bVar1 = TAUJ0TOE;
  TAUJ0TOE = bVar1 & 0xf0;
  bVar1 = TAUJ0TO;
  TAUJ0TO = bVar1 & 0xf0;
  bVar1 = TAUJ0RDE;
  TAUJ0RDE = bVar1 & 0xf0;
  bVar1 = TAUJ0RDM;
  TAUJ0RDM = bVar1 & 0xf0;
  return;
}

void initialize_ffe51000_single_channel_registers_66440(void)

{
  byte bVar1;
  
  DAT_ffe51090 = 0;
  DAT_ffe51094 = 0;
  DAT_ffe51080 = 0;
  DAT_ffe51020 = 0;
  DAT_ffe51000 = 0xffffffff;
  bVar1 = DAT_ffe51060;
  DAT_ffe51060 = bVar1 & 0xfe;
  bVar1 = DAT_ffe5105c;
  DAT_ffe5105c = bVar1 & 0xfe;
  bVar1 = DAT_ffe510a0;
  DAT_ffe510a0 = bVar1 & 0xfe;
  bVar1 = DAT_ffe510a4;
  DAT_ffe510a4 = bVar1 & 0xfe;
  return;
}

void set_fixed_ffdd_enable_bits_66474(void)

{
  ushort uVar1;
  uint uVar2;
  
  uVar1 = Ramffdd0010;
  Ramffdd0010 = uVar1 | 0x412b;
  uVar1 = Ramffdd0014;
  Ramffdd0014 = uVar1 | 0x2b;
  uVar1 = Ramffdd0018;
  Ramffdd0018 = uVar1 | 799;
  uVar1 = Ramffdd1040;
  Ramffdd1040 = uVar1 | 0x20;
  uVar1 = Ramffdd1044;
  Ramffdd1044 = uVar1 | 2;
  uVar1 = Ramffdd1060;
  Ramffdd1060 = uVar1 | 0x20;
  uVar1 = Ramffdd1064;
  Ramffdd1064 = uVar1 | 2;
  uVar2 = Ramffdd1000;
  Ramffdd1000 = uVar2 | 1;
  uVar2 = Ramffdd1004;
  Ramffdd1004 = uVar2 | 1;
  uVar2 = Ramffdd100c;
  Ramffdd100c = uVar2 | 0x30;
  uVar2 = Ramffdd1020;
  Ramffdd1020 = uVar2 | 2;
  uVar2 = Ramffdd1024;
  Ramffdd1024 = uVar2 | 2;
  uVar2 = Ramffdd102c;
  Ramffdd102c = uVar2 | 0xc0;
  return;
}

void run_init_chain_664f6(void)

{
  initialize_ffe20000_compare_registers_661fc();
  initialize_ffe21000_compare_registers_662dc();
  initialize_tauj0_four_channels_6639c();
  initialize_ffe51000_single_channel_registers_66440();
  set_fixed_ffdd_enable_bits_66474();
  return;
}

uint reload_compare_periods_without_initial_offsets_66512(void)

{
  ushort uVar1;
  byte bVar2;
  uint saved_mask;
  
  saved_mask = priority_mask_enter(0xffc0);
  Ramffe20000 = DAT_00030e14 + -1;
  Ramffe20004 = DAT_00030e18 + -1;
  Ramffe2000c = DAT_00030e1c + -1;
  Ramffe20014 = DAT_00030e20 + -1;
  Ramffe20020 = DAT_00030e10 + -1;
  Ramffe20038 = DAT_00030e10 + -1;
  uVar1 = Ramffe2005c;
  Ramffe2005c = uVar1 & 0xbed4;
  uVar1 = Ramffe20058;
  Ramffe20058 = uVar1 & 0xbed4;
  Ramffe21000 = DAT_00030e14 + -1;
  Ramffe21004 = DAT_00030e18 + -1;
  Ramffe2100c = DAT_00030e1c + -1;
  Ramffe21014 = DAT_00030e20 + -1;
  uVar1 = Ramffe2105c;
  Ramffe2105c = uVar1 & 0xffd0;
  uVar1 = Ramffe21058;
  Ramffe21058 = uVar1 & 0xffd0;
  TAUJ0CDR0 = (uint)(PTR_FUN_00030df0 + -1);
  TAUJ0CDR1 = DAT_00030df8 - 1;
  TAUJ0CDR2 = DAT_00030e00 - 1;
  TAUJ0CDR3 = DAT_00030e08 - 1;
  bVar2 = TAUJ0TOE;
  TAUJ0TOE = bVar2 & 0xf0;
  bVar2 = TAUJ0TO;
  TAUJ0TO = bVar2 & 0xf0;
  priority_mask_restore(saved_mask);
  return saved_mask;
}

void startup_start_timers_and_load_steady_periods(void)

{
  uint uVar1;
  
  DAT_ffdd0004 = 1;
  uVar1 = (uint)DAT_00031672 * 2 + (uint)pwm_compare_offset * 2 & 0xffff;
  spin_wait(1);
  DAT_ffe70144 = uVar1;
  DAT_ffe71144 = uVar1;
  uVar1 = TSG30CMPUE;
  TSG30CMPUE = uVar1;
  uVar1 = TSG31CMPUE;
  TSG31CMPUE = uVar1;
  Ramffe20000 = DAT_00030e14 + -1;
  Ramffe20004 = DAT_00030e18 + -1;
  Ramffe2000c = DAT_00030e1c + -1;
  Ramffe20014 = DAT_00030e20 + -1;
  Ramffe20020 = DAT_00030e10 + -1;
  Ramffe20038 = DAT_00030e10 + -1;
  Ramffe21000 = DAT_00030e14 + -1;
  Ramffe21004 = DAT_00030e18 + -1;
  Ramffe2100c = DAT_00030e1c + -1;
  Ramffe21014 = DAT_00030e20 + -1;
  TAUJ0CDR0 = (uint)(PTR_FUN_00030df0 + -1);
  TAUJ0CDR1 = DAT_00030df8 - 1;
  TAUJ0CDR2 = DAT_00030e00 - 1;
  TAUJ0CDR3 = DAT_00030e08 - 1;
  return;
}

int application_initialize_before_timer_start(void)

{
  enable_dma_and_reset_sixteen_channel_controls_607d0();
  initialize_dma_channel_modes_and_counters_60766();
  configure_enabled_serial_dma_descriptors_60e5a();
  run_init_chain_60178();
  initialize_four_capture_records_and_both_channels_60c06();
  initialize_two_rom_selected_output_pin_levels_61ee8();
  initialize_phase_timer_ports_compares_and_dma_61b56();
  initialize_reset_and_prime_both_acquisition_channels_623c0();
  initialize_two_channel_output_pin_levels_61fce();
  set_byte_fold_control_22_611ee();
  initialize_serial_receive_frame_and_check_byte_613c8();
  reset_redundant_shutdown_sequence_state_61526();
  clear_receive_toggle_tracking_6165a();
  initialize_serial_transmit_bitmap_frame_616fc();
  disable_dma_global_control_607f8();
  initialize_nvm_hold_and_application_families_66bc8();
  initialize_round_robin_after_8844e_89d3c();
  ((void)(0), initialize_secoc_context_and_publish_ready_8ed14());
  crypto_bank_initialize_mode();
  crypto_bank_initialize_work();
  initialize_priority_mask_stack_256_entries_6a440();
  initialize_communication_chain_and_publish_ready_7a132();
  reset_four_96_byte_tracking_arrays_8e74e();
  return_only_stub_6a322();
  call_98898_with_zero_byte_8b120();
  clear_state3800_and_768_byte_buffer_8b070();
  reset_application_programming_admission_state_8b134();
  fill_constant_block_8bfea();
  reset_dtc_count_state_and_scratch_8c318();
  reset_dtc_list_continuation_and_scratch_8c70c();
  fill_constant_block_8cb8c();
  fill_constant_block_8cef0();
  reset_state3b26_to3b29_8b3d4();
  reset_memory_read_status4598_8d4ae();
  app_security_reset_challenge_material();
  reset_communication_local_state_8d9ca();
  reset_write_did_transaction();
  diag_reset_routine_class_state();
  fill_constant_block_8db22();
  fill_constant_block_8de1a();
  reset_proprietary_dispatch_continuation_8e1e0();
  reset_eight_byte_reply_and_memory_mode_flags_98f4c();
  crypto_bank_initialize_verification_report();
  run_init_chain_664f6();
  initialize_supervision_and_clear_four_state_bytes_65f8e();
  startup_classify_retained_token();
  clear_febe5f28_byte_6681e();
  return initialize_application_and_request_first_generation();
}

void fast_control_cycle(void)

{
  publish_staged_phase_compares_and_port_masks_61e72();
  service_serial_acquisition_pair();
  publish_fast_acquisition_inputs();
  dispatch_current_control_slice_by_redundant_mode_588e8();
  return;
}

void run_init_chain_6679e(void)

{
  republish_image_identity_on_redundant_check_error_62df0();
  consume_rsent_sensor_slots();
  dispatch_ch1_processing_slice_by_redundant_mode_5899e();
  delay_if_febe39d9_bit0_set_65d38();
  return;
}

void run_init_chain_667b6(void)

{
  store_paired_adc_configuration_check_results_603c8();
  dispatch_capture_processing_by_status_low2_5f9ce();
  ensure_clock3_divider_50_under_priority_mask_619c0();
  publish_acquisition_diagnostic_snapshot();
  dispatch_ch2_monitor_slice_by_redundant_mode_58a50();
  run_ready_gated_paired_service_calls_7a232();
  update_local_status_packet();
  update_local_status_bit_latch();
  decode_receive_status_bits_and_toggle_changes_61664();
  pack_status_bitmap_and_transmit_serial_frame_6174a();
  return;
}

uint foreground_subsystem_cycle(void)

{
  crypto_bank_foreground_cycle();
  service_ready_communication_policy_and_pdu_chains_7a254();
  dcm_foreground_cycle();
  crypto_bank_maintain_terminal_states();
  dispatch_foreground_mode_generation();
  return reload_compare_periods_without_initial_offsets_66512();
}

void thunk_service_channel_one_transmit_completions_and_sync_8583e(void)

{
  service_channel_one_transmit_completions_and_sync_8583e();
  return;
}

void thunk_service_channel_one_receive_and_sync_83f30(void)

{
  service_channel_one_receive_and_sync_83f30();
  return;
}

void clear_febe5f28_byte_6681e(void)

{
  DAT_febe5f28 = 0;
  return;
}

void publish_fast_acquisition_inputs(void)

{
  uint32_t puVar1;
  F33SerialAcquisitionRecord local_34[2];
  F33AcquisitionGroupPair FStack_1c;
  
  puVar1 = 0xfebeb800u;
  copy_acquisition_group_pair(&FStack_1c);
  (*((ushort *)camry_host_ptr((uint32_t)(puVar1 + -0x5938)))) = FStack_1c.group0[0];
  (*((ushort *)camry_host_ptr((uint32_t)(puVar1 + -0x5936)))) = FStack_1c.group0[1];
  (*((ushort *)camry_host_ptr((uint32_t)(puVar1 + -0x5934)))) = FStack_1c.group0[2];
  (*((ushort *)camry_host_ptr((uint32_t)(puVar1 + -0x592c)))) = FStack_1c.group0[3];
  (*((ushort *)camry_host_ptr((uint32_t)(puVar1 + -0x592a)))) = FStack_1c.group0[4];
  (*((ushort *)camry_host_ptr((uint32_t)(puVar1 + -0x5928)))) = FStack_1c.group0[5];
  (*((ushort *)camry_host_ptr((uint32_t)(puVar1 + -0x5932)))) = FStack_1c.group8[0];
  (*((ushort *)camry_host_ptr((uint32_t)(puVar1 + -0x5930)))) = FStack_1c.group8[1];
  (*((ushort *)camry_host_ptr((uint32_t)(puVar1 + -0x592e)))) = FStack_1c.group8[2];
  (*((ushort *)camry_host_ptr((uint32_t)(puVar1 + -0x5926)))) = FStack_1c.group8[3];
  (*((ushort *)camry_host_ptr((uint32_t)(puVar1 + -0x5924)))) = FStack_1c.group8[4];
  (*((ushort *)camry_host_ptr((uint32_t)(puVar1 + -0x5922)))) = FStack_1c.group8[5];
  copy_cached_serial_acquisition_records(local_34);
  (*((ushort *)camry_host_ptr((uint32_t)(puVar1 + -0x58ee)))) = local_34[0].field14_0;
  (*((ushort *)camry_host_ptr((uint32_t)(puVar1 + -0x58ec)))) = local_34[0].field14_1;
  (*((ushort *)camry_host_ptr((uint32_t)(puVar1 + -0x58ea)))) = local_34[0].field12;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x58d7))))) = local_34[0].rx_count_failures;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x58d6))))) = local_34[0].rx_or_tx_failures;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x58d5))))) = local_34[0].crc_failures;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x58d4))))) = local_34[0].sequence_failures;
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x58e4)))) = local_34[1].field14_0;
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x58e2)))) = local_34[1].field14_1;
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x58e0)))) = local_34[1].field12;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x58d3))))) = local_34[1].rx_count_failures;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x58d2))))) = local_34[1].rx_or_tx_failures;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x58d1))))) = local_34[1].crc_failures;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x58d0))))) = local_34[1].sequence_failures;
  return;
}

void consume_rsent_sensor_slots(void)

{
  uint8_t stack_record_14[20];
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  if ((DAT_febe5f28 & 1) != 0) {
    puVar1 = 0xfebeb800u;
    read_and_reorder_both_capture_status_records_62b32(camry_host_addr(stack_record_14));
    (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x58fe)))) = (*((uint16_t *)(stack_record_14 + 0)));
    (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x58fc)))) = (*((uint16_t *)(stack_record_14 + 2)));
    (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x58fa)))) = (*((uint16_t *)(stack_record_14 + 4)));
    (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x58f8)))) = (*((uint16_t *)(stack_record_14 + 6)));
    (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x58f6)))) = (*((uint16_t *)(stack_record_14 + 8)));
    (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x58f4)))) = (*((uint16_t *)(stack_record_14 + 10)));
    (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x58f2)))) = (*((uint16_t *)(stack_record_14 + 12)));
    (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x58f0)))) = (*((uint16_t *)(stack_record_14 + 14)));
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x58d8))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x58d8))))) + '\x01';
  return;
}

void publish_acquisition_diagnostic_snapshot(void)

{
  uint8_t stack_record_24[36];
  uint32_t puVar1;
  F33SerialAcquisitionMasks local_2c;
  undefined2 uStack_28;
  undefined2 uStack_26;
  
  puVar1 = 0xfebeb800u;
  copy_acquisition_diagnostic_samples((stack_record_24 + 14));
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x5920)))) = (*((uint16_t *)(stack_record_24 + 22)));
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x591e)))) = (*((uint16_t *)(stack_record_24 + 16)));
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x591c)))) = (*((uint16_t *)(stack_record_24 + 26)));
  (*((ushort *)camry_host_ptr((uint32_t)(puVar1 + -0x591a)))) = (*((uint16_t *)(stack_record_24 + 14)));
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x5918)))) = (*((uint16_t *)(stack_record_24 + 24)));
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x5916)))) = (*((uint16_t *)(stack_record_24 + 18)));
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x5914)))) = (*((uint16_t *)(stack_record_24 + 20)));
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x5912)))) = (*((uint16_t *)(stack_record_24 + 28)));
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x5910)))) = (*((uint16_t *)(stack_record_24 + 30)));
  read_paired_adc_transfer_samples_and_clear_metadata_62b18(camry_host_addr(stack_record_24));
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x5902)))) = (*((uint16_t *)(stack_record_24 + 0)));
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x5900)))) = (*((uint16_t *)(stack_record_24 + 2)));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x58da))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x7ff6)))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x58d9))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x7ff5)))));
  rotate_and_copy_serial_acquisition_masks(&local_2c);
  (*((ushort *)camry_host_ptr((uint32_t)(puVar1 + -0x58e8)))) = local_2c.first;
  (*((ushort *)camry_host_ptr((uint32_t)(puVar1 + -0x58e6)))) = local_2c.second;
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x58de)))) = uStack_28;
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x58dc)))) = uStack_26;
  return;
}

void stage_output_bank0_phase_mask(uchar mask)

{
  stage_configured_phase_mask(0,(uint)mask);
  return;
}

void stage_channel0_halfword_pwm_compares_669da(ushort param_1,ushort param_2,ushort param_3)

{
  pwm_stage_halfword_compares(0,param_1,param_2,param_3);
  return;
}

void stage_channel0_word_pwm_compares_669f6(ushort param_1,ushort param_2,ushort param_3)

{
  pwm_stage_word_compares(0,param_1,param_2,param_3);
  return;
}

void write_output_bank0_port_level_a(void)

{
  write_configured_output_port_level_a(0);
  return;
}

void write_output_bank0_port_level_b(void)

{
  write_configured_output_port_level_b(0);
  return;
}

void stage_output_bank1_phase_mask(uchar mask)

{
  stage_configured_phase_mask(1,(uint)mask);
  return;
}

void stage_channel1_halfword_pwm_compares_66a40(ushort param_1,ushort param_2,ushort param_3)

{
  pwm_stage_halfword_compares(1,param_1,param_2,param_3);
  return;
}

void stage_channel1_word_pwm_compares_66a5c(ushort param_1,ushort param_2,ushort param_3)

{
  pwm_stage_word_compares(1,param_1,param_2,param_3);
  return;
}

void write_output_bank1_port_level_a(void)

{
  write_configured_output_port_level_a(1);
  return;
}

void write_output_bank1_port_level_b(void)

{
  write_configured_output_port_level_b(1);
  return;
}

void write_channel0_reference_level_66a94(void)

{
  write_channel_reference_level(0);
  return;
}

void write_channel0_requested_level_66aa2(void)

{
  write_channel_requested_level(0);
  return;
}

uint channel0_matches_reference(void)

{
  uint uVar1;
  
  uVar1 = read_channel_input_level(0);
  return (uint)(uVar1 == (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x312fcu + (uint32_t)(0) * (uint32_t)sizeof(F33ChannelPortDescriptor) + (uint32_t)offsetof(F33ChannelPortDescriptor, reference_level))))));
}

void write_channel1_reference_level_66acc(void)

{
  write_channel_reference_level(1);
  return;
}

void write_channel1_requested_level_66ada(void)

{
  write_channel_requested_level(1);
  return;
}

uint channel1_matches_reference(void)

{
  uint uVar1;
  
  uVar1 = read_channel_input_level(1);
  return (uint)(uVar1 == (*((volatile uint8_t *)camry_host_ptr((uint32_t)((uint32_t)(0x312fcu + (uint32_t)(1) * (uint32_t)sizeof(F33ChannelPortDescriptor)) + (uint32_t)(0) * (uint32_t)sizeof(F33ChannelPortDescriptor) + (uint32_t)offsetof(F33ChannelPortDescriptor, reference_level))))));
}

void or_two_by_two_halfword_state_wrapper_66b04(undefined1 param_1,undefined1 param_2,undefined2 param_3)

{
  or_pending_acquisition_command_bits_under_mask_62a16(param_1,param_2,param_3);
  return;
}

void initialize_nvm_hold_and_application_families_66bc8(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  publish_redundant_u8('Z', ((uchar *)camry_host_ptr((uint32_t)((0xfebf0670u)))), ((uchar *)camry_host_ptr((uint32_t)((0xfebf10a8u)))), ((uchar *)camry_host_ptr((uint32_t)((0xfebf10ccu)))))
  ;
  publish_redundant_u8('\0', ((undefined *)camry_host_ptr((uint32_t)(puVar1 + 0x4e71))), ((undefined *)camry_host_ptr((uint32_t)(puVar1 + 0x58a9))), ((undefined *)camry_host_ptr((uint32_t)(puVar1 + 0x58cd))));
  publish_redundant_u8('\0', ((undefined *)camry_host_ptr((uint32_t)(puVar1 + 0x4e72))), ((undefined *)camry_host_ptr((uint32_t)(puVar1 + 0x58aa))), ((undefined *)camry_host_ptr((uint32_t)(puVar1 + 0x58ce))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x4e73))))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x4e74))))) = 0;
  initialize_nvm_family0_requests_buffers_and_cursors_672c0();
  nvm_initialize_family1_application();
  nvm_initialize_family2_ram();
  nvm_initialize_acquisition();
  nvm_run_bounded_initial_acquisition();
  return;
}

uint nvm_select_acquisition_work(uchar current_work)

{
  uint32_t puVar1;
  uint uVar2;
  uint uVar3;
  uint uVar4;
  
  puVar1 = 0xfebeb800u;
  uVar2 = nvm_get_family0_phase();
  uVar3 = nvm_get_family1_phase();
  uVar4 = read_repair_redundant_u8(((uint32_t)((uint32_t)(puVar1 + 0x4e70))), ((uint32_t)((uint32_t)(puVar1 + 0x58a8))), ((uint32_t)((uint32_t)(puVar1 + 0x58cc))),  '\0');
  if (uVar4 == 0x5a) {
    return 0;
  }
  if (((uVar2 == 0) && (uVar3 == 0)) || ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x4e73))))) != '\0')) {
    uVar2 = nvm_step_acquisition_pass();
    if (uVar2 != 0) {
      return (uint)current_work;
    }
    uVar2 = nvm_select_family1_request();
    if (uVar2 == 1) {
      return 2;
    }
    uVar2 = nvm_select_family0_request();
    if (uVar2 != 1) {
      return (uint)current_work;
    }
  }
  else if (uVar3 != 0) {
    return 2;
  }
  return 1;
}

char poll_selected_nvm_family_and_handle_completion_66cc4(char param_1)

{
  int iVar1;
  
  if (param_1 == '\x01') {
    iVar1 = get_nvm_family0_busy_byte_68924();
    if (iVar1 != 0) {
      return '\x01';
    }
    handle_nvm_family0_operation_completion_674dc();
  }
  else {
    if (param_1 != '\x02') {
      return param_1;
    }
    iVar1 = get_nvm_family1_busy_byte_68a4a();
    if (iVar1 != 0) {
      return '\x02';
    }
    nvm_handle_family1_completion();
  }
  return '\0';
}

void nvm_application_cycle(void)

{
  uint32_t puVar1;
  undefined1 uVar2;
  uint uVar3;
  
  puVar1 = 0xfebeb800u;
  uVar3 = nvm_select_acquisition_work(DAT_febf0674);
  nvm_service_and_release_erase_span();
  uVar2 = poll_selected_nvm_family_and_handle_completion_66cc4(uVar3);
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x4e74))))) = uVar2;
  select_flmd0_internal_pulldown();
  return;
}

uint nvm_request_record_refresh(uint selector)

{
  uint uVar1;
  uint uVar2;
  uint object;
  uint uVar3;
  
  uVar2 = 0;
  uVar3 = selector & 0xff00;
  object = selector & 0xff;
  uVar1 = read_repair_redundant_u8((int)((uint32_t)(0xfebf0671u)), (int)((uint32_t)(0xfebf10a9u)), (int)((uint32_t)(0xfebf10cdu)), '\0');
  if (uVar1 != 0x5a) {
    if (uVar3 == 0) {
      uVar2 = nvm_enqueue_family0_read(object);
    }
    else if (uVar3 == 0x100) {
      uVar2 = nvm_enqueue_family1_read(object);
    }
    else if (uVar3 == 0x200) {
      uVar2 = nvm_refresh_family2_record_status(object);
    }
  }
  return uVar2;
}

uint nvm_set_record(uint selector,uint *source)

{
  uint uVar1;
  uint uVar2;
  uint object;
  uint uVar3;
  
  uVar2 = 0;
  uVar3 = selector & 0xff00;
  object = selector & 0xff;
  uVar1 = read_repair_redundant_u8((int)((uint32_t)(0xfebf0672u)), (int)((uint32_t)(0xfebf10aau)), (int)((uint32_t)(0xfebf10ceu)), '\0');
  if (uVar1 != 0x5a) {
    if (uVar3 == 0) {
      uVar2 = nvm_set_family0_record(object, camry_host_addr(source));
    }
    else if (uVar3 == 0x100) {
      uVar2 = nvm_set_family1_record(object,source);
    }
    else if (uVar3 == 0x200) {
      uVar2 = nvm_set_family2_record(object,source);
    }
  }
  return uVar2;
}

uint nvm_get_record_status(uint selector)

{
  uint uVar1;
  uint object;
  
  uVar1 = selector & 0xff00;
  object = selector & 0xff;
  if (uVar1 == 0) {
    uVar1 = nvm_get_family0_status(object);
  }
  else if (uVar1 == 0x100) {
    uVar1 = nvm_get_family1_status(object);
  }
  else if (uVar1 == 0x200) {
    uVar1 = nvm_get_family2_status(object);
  }
  else {
    uVar1 = 0xff;
  }
  return uVar1;
}

int read_unaligned_nvm_bytes_through_four_byte_buffer_66e7c(uint param_1,int param_2,uint param_3)

{
  undefined1 *puVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  int iVar6;
  uint uVar7;
  undefined1 auStack_20 [4];
  
  iVar4 = 0;
  uVar7 = param_1 & 0xfffc;
  iVar6 = (param_1 & 0xffff) - uVar7;
  iVar5 = 0;
  while( true ) {
    iVar2 = iVar5 - (param_3 & 0xffff);
    if (iVar2 < 0 == (iVar5 < 0 && -1 < iVar2)) {
      return iVar4;
    }
    if (iVar4 != 0) break;
    iVar2 = read_nvm_family0_range_with_direct_request_689f2(uVar7, camry_host_addr(auStack_20), 4);
    if (iVar2 == 0) {
      iVar2 = (param_3 & 0xffff) - iVar5;
      iVar3 = 4 - iVar6;
      if (iVar3 - iVar2 < 0 != (iVar3 < 0 != iVar2 < 0 && iVar2 < 0 == iVar3 - iVar2 < 0)) {
        iVar2 = iVar3;
      }
      for (iVar3 = 0;
          iVar3 - iVar2 < 0 != (iVar3 < 0 != iVar2 < 0 && iVar2 < 0 == iVar3 - iVar2 < 0);
          iVar3 = iVar3 + 1) {
        puVar1 = ((undefined1 *)camry_host_ptr((uint32_t)(iVar5 + param_2)));
        iVar5 = iVar5 + 1;
        *puVar1 = auStack_20[iVar6 + iVar3];
      }
      uVar7 = uVar7 + 4 & 0xffff;
      iVar6 = 0;
    }
    else {
      if (iVar2 == 0x5a) {
        return 0x55555555;
      }
      iVar4 = -1;
    }
  }
  return iVar4;
}

void restart_nvm_acquisition_with_reset_scan_cursors_66ef4(void)

{
  nvm_acquisition_phase = '3';
  reset_nvm_family0_scan_and_probe_cursors_67346();
  reset_nvm_family1_scan_cursor_67a52();
  nvm_arm_initial_read_acquisition();
  return;
}

undefined1 get_nvm_acquisition_active_5a_66f10(void)

{
  undefined1 uVar1;
  
  uVar1 = 0;
  if (nvm_acquisition_phase != '\0') {
    uVar1 = 0x5a;
  }
  return uVar1;
}

uint application_nvm_is_ready(void)

{
  uint32_t puVar1;
  uint uVar2;
  int iVar3;
  int iVar4;
  
  puVar1 = 0xfebeb800u;
  uVar2 = check_no_nvm_family0_status_class20_67984();
  if ((uVar2 == 1) && (uVar2 = check_no_nvm_family1_status_class20_681aa(), uVar2 == 1)) {
    iVar3 = get_nvm_family0_busy_byte_68924();
    iVar4 = get_nvm_family1_busy_byte_68a4a();
    if (((iVar3 == 0xff) || (((iVar3 == 0xa5 || (iVar4 == 0xff)) || (iVar4 == 0xa5)))) ||
       ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x4e73))))) != '\0')) {
      uVar2 = 0;
    }
  }
  return uVar2;
}

int set_redundant_flag_febf0671_66f68(void)

{
  return publish_redundant_u8('Z',((undefined *)camry_host_ptr(0xfebf0671u)),((undefined *)camry_host_ptr(0xfebf10a9u)),((undefined *)camry_host_ptr(0xfebf10cdu)));
}

int clear_redundant_flag_febf0671_66f84(void)

{
  return publish_redundant_u8('\0',((undefined *)camry_host_ptr(0xfebf0671u)),((undefined *)camry_host_ptr(0xfebf10a9u)),((undefined *)camry_host_ptr(0xfebf10cdu)));
}

int set_redundant_flag_febf0672_66f9e(void)

{
  return publish_redundant_u8('Z',((undefined *)camry_host_ptr(0xfebf0672u)),((undefined *)camry_host_ptr(0xfebf10aau)),((undefined *)camry_host_ptr(0xfebf10ceu)));
}

int clear_redundant_flag_febf0672_66fba(void)

{
  return publish_redundant_u8('\0',((undefined *)camry_host_ptr(0xfebf0672u)),((undefined *)camry_host_ptr(0xfebf10aau)),((undefined *)camry_host_ptr(0xfebf10ceu)));
}

int clear_nvm_work_hold_66fd4(void)

{
  return publish_redundant_u8
            ('\0', ((uchar *)camry_host_ptr((uint32_t)((0xfebf0670u)))), ((uchar *)camry_host_ptr((uint32_t)((0xfebf10a8u)))), ((uchar *)camry_host_ptr((uint32_t)((0xfebf10ccu)))));
}

uint platform_restart_selector_constant_zero(void)

{
  return 0;
}

void thunk_service_nvm_acquisition_driver_wrapper_68318(void)

{
  service_nvm_acquisition_driver_wrapper_68318();
  return;
}

void nvm_initialize_family2_ram(void)

{
  ushort uVar1;
  uint uVar2;
  int iVar3;
  undefined8 uVar4;
  uint *puVar5;
  int iVar6;
  
  uVar4 = 0xfebeb800;
  for (iVar6 = 0;
      (int)(iVar6 - (uint)nvm_family2_object_count) < 0 !=
      (iVar6 < 0 && -1 < (int)(iVar6 - (uint)nvm_family2_object_count)); iVar6 = iVar6 + 1) {
    iVar3 = (int)uVar4;
    (*((undefined1 *)camry_host_ptr((uint32_t)(iVar6 + iVar3 + 0x4e5b)))) = 0;
    publish_redundant_u8
              ('\0',((uchar *)camry_host_ptr((uint32_t)(iVar3 + 0x4e50 + iVar6))),((uchar *)camry_host_ptr((uint32_t)(iVar3 + 0x5898 + iVar6))),
               ((uchar *)camry_host_ptr((uint32_t)(iVar3 + 0x58bc + iVar6))));
    uVar1 = (*((volatile uint16_t *)camry_host_ptr((uint32_t)((uint32_t)(0x2af8cu + (uint32_t)(iVar6) * (uint32_t)sizeof(F33NvmFamily2Descriptor)) + (uint32_t)(0) * (uint32_t)sizeof(F33NvmFamily2Descriptor) + (uint32_t)offsetof(F33NvmFamily2Descriptor, payload_bytes)))));
    puVar5 = ((void *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)((uint32_t)(0x2af8cu + (uint32_t)(iVar6) * (uint32_t)sizeof(F33NvmFamily2Descriptor)) + (uint32_t)(0) * (uint32_t)sizeof(F33NvmFamily2Descriptor) + (uint32_t)offsetof(F33NvmFamily2Descriptor, ram_buffer))))))));
    for (uVar2 = 0; uVar2 < uVar1 >> 2; uVar2 = uVar2 + 1 & 0xffff) {
      puVar5[uVar2] = 0;
    }
  }
  return;
}
