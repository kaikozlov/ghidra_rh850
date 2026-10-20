#include "common.h"

uint32_t run_init_chain_632c8(void)

{
  uint32_t camry_r10_result;
  initialize_fffee680_eight_register_groups_65458();
  initialize_fixed_register_access_patterns_654aa();
  initialize_ffc49000_eight_register_groups_657fa();
  initialize_fffa0000_register_pair_65852();
  (camry_r10_result = load_mpu_region_bounds_and_enable_profile_6586a());
  clear_febf3400_with_mpu_write_window_6595e();
  return camry_r10_result;
}

void clear_error_control_registers_and_set_gram_stac_632e8(void)

{
  DAT_fffee00d = 0;
  DAT_fffee020 = 0;
  DAT_fffee021 = 0;
  DAT_fffee022 = 0;
  DAT_fffee023 = 0;
  DAT_fffee024 = 0;
  Ramffff7a04 = 0;
  Ramffff7a08 = 0;
  STAC_GRAM = 3;
  return;
}

void delay_1000_then_enter_terminal_sequence_63324(void)

{
  spin_wait(1000);
                    /* WARNING: Subroutine does not return */
  enter_terminal_hardware_sequence();
}

void initialize_ecm_masks_routes_and_clear_error_outputs_63338(void)

{
  uchar uVar1;
  uint uVar2;
  byte bVar3;
  
  bVar3 = 0;
  ECMPEM = 3;
  while( true ) {
    ECMPCMD1 = 0xa5;
    bVar3 = bVar3 + 1;
    ECMEMK0 = 0xffffffe1;
    ECMEMK0 = 0x1e;
    ECMEMK0 = 0xffffffe1;
    uVar1 = ECMPS;
    if (uVar1 == '\0') break;
    if (2 < bVar3) {
      delay_1000_then_enter_terminal_sequence_63324();
    }
  }
  bVar3 = 0;
  while( true ) {
    bVar3 = bVar3 + 1;
    ECMPCMD1 = 0xa5;
    ECMEMK1 = 0xffffffff;
    ECMEMK1 = 0;
    ECMEMK1 = 0xffffffff;
    uVar1 = ECMPS;
    if (uVar1 == '\0') break;
    if (2 < bVar3) {
      delay_1000_then_enter_terminal_sequence_63324();
    }
  }
  bVar3 = 0;
  while( true ) {
    ECMPCMD1 = 0xa5;
    bVar3 = bVar3 + 1;
    ECMEMK2 = 0x3fffffff;
    ECMEMK2 = 0xc0000000;
    ECMEMK2 = 0x3fffffff;
    uVar1 = ECMPS;
    if (uVar1 == '\0') break;
    if (2 < bVar3) {
      delay_1000_then_enter_terminal_sequence_63324();
    }
  }
  bVar3 = 0;
  while( true ) {
    ECMPCMD1 = 0xa5;
    bVar3 = bVar3 + 1;
    ECMMICFG0 = 0;
    ECMMICFG0 = 0xffffffff;
    ECMMICFG0 = 0;
    uVar1 = ECMPS;
    if (uVar1 == '\0') break;
    if (2 < bVar3) {
      delay_1000_then_enter_terminal_sequence_63324();
    }
  }
  bVar3 = 0;
  while( true ) {
    ECMPCMD1 = 0xa5;
    bVar3 = bVar3 + 1;
    ECMMICFG1 = 0;
    ECMMICFG1 = 0xffffffff;
    ECMMICFG1 = 0;
    uVar1 = ECMPS;
    if (uVar1 == '\0') break;
    if (2 < bVar3) {
      delay_1000_then_enter_terminal_sequence_63324();
    }
  }
  bVar3 = 0;
  while( true ) {
    ECMPCMD1 = 0xa5;
    bVar3 = bVar3 + 1;
    ECMMICFG2 = 0;
    ECMMICFG2 = 0xffffffff;
    ECMMICFG2 = 0;
    uVar1 = ECMPS;
    if (uVar1 == '\0') break;
    if (2 < bVar3) {
      delay_1000_then_enter_terminal_sequence_63324();
    }
  }
  bVar3 = 0;
  while( true ) {
    ECMPCMD1 = 0xa5;
    bVar3 = bVar3 + 1;
    ECMNMICFG0 = 0;
    ECMNMICFG0 = 0xffffffff;
    ECMNMICFG0 = 0;
    uVar1 = ECMPS;
    if (uVar1 == '\0') break;
    if (2 < bVar3) {
      delay_1000_then_enter_terminal_sequence_63324();
    }
  }
  bVar3 = 0;
  while( true ) {
    ECMPCMD1 = 0xa5;
    bVar3 = bVar3 + 1;
    ECMNMICFG1 = 0;
    ECMNMICFG1 = 0xffffffff;
    ECMNMICFG1 = 0;
    uVar1 = ECMPS;
    if (uVar1 == '\0') break;
    if (2 < bVar3) {
      delay_1000_then_enter_terminal_sequence_63324();
    }
  }
  bVar3 = 0;
  while( true ) {
    ECMPCMD1 = 0xa5;
    bVar3 = bVar3 + 1;
    ECMNMICFG2 = 0;
    ECMNMICFG2 = 0xffffffff;
    ECMNMICFG2 = 0;
    uVar1 = ECMPS;
    if (uVar1 == '\0') break;
    if (2 < bVar3) {
      delay_1000_then_enter_terminal_sequence_63324();
    }
  }
  bVar3 = 0;
  while( true ) {
    ECMPCMD1 = 0xa5;
    bVar3 = bVar3 + 1;
    ECMIRCFG0 = 0;
    ECMIRCFG0 = 0xffffffff;
    ECMIRCFG0 = 0;
    uVar1 = ECMPS;
    if (uVar1 == '\0') break;
    if (2 < bVar3) {
      delay_1000_then_enter_terminal_sequence_63324();
    }
  }
  bVar3 = 0;
  while( true ) {
    ECMPCMD1 = 0xa5;
    bVar3 = bVar3 + 1;
    ECMIRCFG1 = 0;
    ECMIRCFG1 = 0xffffffff;
    ECMIRCFG1 = 0;
    uVar1 = ECMPS;
    if (uVar1 == '\0') break;
    if (2 < bVar3) {
      delay_1000_then_enter_terminal_sequence_63324();
    }
  }
  bVar3 = 0;
  while( true ) {
    ECMPCMD1 = 0xa5;
    bVar3 = bVar3 + 1;
    ECMIRCFG2 = 0;
    ECMIRCFG2 = 0xffffffff;
    ECMIRCFG2 = 0;
    uVar1 = ECMPS;
    if (uVar1 == '\0') break;
    if (2 < bVar3) {
      delay_1000_then_enter_terminal_sequence_63324();
    }
  }
  bVar3 = 0;
  while( true ) {
    ECMMPCMD0 = 0xa5;
    ECMMECLR = '\x01';
    ECMMECLR = 0xfe;
    bVar3 = bVar3 + 1;
    ECMMECLR = '\x01';
    uVar1 = ECMPS;
    if (uVar1 == '\0') break;
    if (2 < bVar3) {
      delay_1000_then_enter_terminal_sequence_63324();
    }
  }
  bVar3 = 0;
  uVar2 = 0;
  do {
    if ((int)uVar2 < 0) break;
    uVar2 = ECMMESSTR2;
    bVar3 = bVar3 + 1;
  } while (bVar3 < 0x1f);
  bVar3 = 0;
  while( true ) {
    ECMCPCMD0 = 0xa5;
    ECMCECLR = '\x01';
    ECMCECLR = 0xfe;
    ECMCECLR = '\x01';
    uVar1 = ECMPS;
    if (uVar1 == '\0') break;
    bVar3 = bVar3 + 1;
    if (2 < bVar3) {
      delay_1000_then_enter_terminal_sequence_63324();
    }
  }
  uVar2 = 0x80000000;
  bVar3 = 0;
  do {
    if (-1 < (int)uVar2) break;
    uVar2 = ECMCESSTR2;
    bVar3 = bVar3 + 1;
  } while (bVar3 < 0x1f);
  ECMPEM = 0;
  return;
}

void clear_multiple_error_status_banks_and_ecm_latches_63614(void)

{
  undefined4 uVar1;
  uint uVar2;
  uchar uVar3;
  
  Ramffc65408 = 0xffffffff;
  Ramffc6540c = 0xf;
  uVar1 = Ramffc6540c;
  __synchronize();
  clear_febf3402_with_mpu_write_window_65c64();
  camry_write32(0xffc62004u, 0xf);
  camry_write32(0xffc62008u, 1);
  uVar2 = camry_read32(0xffc62008u);
  __synchronize();
  clear_febf3403_with_mpu_write_window_65d4a();
  Ramffc62c08 = 1;
  Ramffc63408 = 1;
  Ramffc66008 = 1;
  Ramffc66408 = 1;
  Ramffc67008 = 1;
  Ramffc67408 = 1;
  Ramffc67808 = 1;
  Ramffc68408 = 1;
  Ramffc6a008 = 1;
  Ramffc6c008 = 1;
  uVar1 = Ramffc6c008;
  __synchronize();
  Ramffddd808 = 1;
  uVar1 = Ramffddd808;
  __synchronize();
  Ramfff94808 = 1;
  uVar1 = Ramfff94808;
  __synchronize();
  Ramffc40808 = 1;
  uVar1 = Ramffc40808;
  __synchronize();
  clear_febf3404_with_mpu_write_window_65e58();
  ECMPCMD1 = 0xa5;
  ECMESSTC0 = 0x10090000;
  ECMESSTC0 = 0xeff6ffff;
  ECMESSTC0 = 0x10090000;
  uVar3 = ECMPS;
  __synchronize();
  return;
}

void startup_copy_helper(void)

{
  undefined4 *puVar1;
  undefined4 *puVar2;
  
  puVar2 = ((undefined *)camry_host_ptr(0xfebf7c00u));
  for (puVar1 = ((undefined *)camry_host_ptr(0x10000u));camry_host_addr(puVar1)<((uint32_t)(0x17df0u)); puVar1 = ((undefined *)camry_host_ptr((uint32_t)(0x10000u + (uint32_t)(1) * 1u)))) {
    *puVar2 = *puVar1;
    puVar2 = puVar2 + 1;
  }
  return;
}

void copy_64_bytes_after_app_info_header_636f8(void)

{
  uint uVar3;
  
  uVar3 = 0;
  do {
    *(volatile uint8_t *)camry_host_ptr(0xfebf7b50u + uVar3) =
         *(volatile uint8_t *)camry_host_ptr(0x20810u + uVar3);
    uVar3 = uVar3 + 1;
  } while (uVar3 < 0x40);
  return;
}

void poll_fff80104_bit0_clear_or_terminate_63718(void)

{
  uint uVar1;
  byte bVar2;
  
  bVar2 = 0;
  do {
    uVar1 = Ramfff80104;
    bVar2 = bVar2 + 1;
    if ((uVar1 & 1) == 0) {
      return;
    }
  } while (bVar2 < 10);
                    /* WARNING: Subroutine does not return */
  enter_terminal_hardware_sequence();
}

void initialize_error_monitors_and_set_ecm_interrupt_mask_63738(void)

{
  uint uVar1;
  uchar uVar2;
  byte bVar3;
  
  clear_febf3401_under_sr26_sel6_control_71610();
  clear_febf3402_with_mpu_write_window_65c64();
  clear_febf3403_with_mpu_write_window_65d4a();
  clear_febf3404_with_mpu_write_window_65e58();
  bVar3 = 0;
  do {
    ECMPCMD1 = 0xa5;
    ECMMICFG0 = 0x100b001e;
    ECMMICFG0 = 0xeff4ffe1;
    ECMMICFG0 = 0x100b001e;
    uVar1 = ECMMICFG0;
    __synchronize();
    uVar2 = ECMPS;
    if (uVar2 == '\0') {
      return;
    }
    bVar3 = bVar3 + 1;
  } while (bVar3 < 3);
                    /* WARNING: Subroutine does not return */
  enter_terminal_hardware_sequence();
}

void startup_validate_resident_boot_crc(void)

{
  uint *puVar1;
  byte bVar2;
  uint uVar3;
  
  bVar2 = 0;
  while( true ) {
    uVar3 = 0;
    camry_write8(0xffd51020u, '\0');
    camry_write32(0xffd51004u, (int)0xffffffff);
    while (uVar3 < 0x2800) {
      puVar1 = ((uint *)camry_host_ptr((uint32_t)(uVar3 * 4)));
      uVar3 = uVar3 + 1;
      camry_write32(0xffd51000u, *puVar1);
    }
    uVar3 = camry_read32(0xffd51004u);
    bVar2 = bVar2 + 1;
    if (uVar3 == 0xffffffff) break;
    if (2 < bVar2) {
                    /* WARNING: Subroutine does not return */
      enter_terminal_hardware_sequence();
    }
  }
  return;
}

void startup_coordinator(void)

{
  camry_write32((camry_sp - 4u) & ~3u, camry_gpr[31]);
  camry_sp -= 4u;
  camry_gpr[3] = camry_sp;

  uint uVar1;
  uint uVar2;
  uint in_FPEC = camry_SR[0][11];
  uint in_RBASE = camry_SR[1][2];
  uint in_FPIPR = camry_SR[1][7];
  uint in_ISPR = camry_SR[2][10];
  
  (camry_gpr[31] = 0x637f6u, application_context_init)();
  clear_application_ram_4k();
  run_init_chain_632c8();
  clear_error_control_registers_and_set_gram_stac_632e8();
  initialize_both_serial_buffers_and_registers_60e3e();
  return_only_stub_610bc();
  initialize_four_halfword_serial_frame_registers_61260();
  initialize_ecm_masks_routes_and_clear_error_outputs_63338();
  startup_capture_retained_token();
  clear_multiple_error_status_banks_and_ecm_latches_63614();
  initialize_port_configuration_and_mux_fields_60d0e();
  initialize_interrupt_control_words_and_verify_priorities_62e6a();
  startup_copy_helper();
  copy_64_bytes_after_app_info_header_636f8();
  poll_fff80104_bit0_clear_or_terminate_63718();
  run_init_chain_6385c();
  clear_fffee980_control_registers_715e0();
  initialize_error_monitors_and_set_ecm_interrupt_mask_63738();
  startup_publish_image_identity_check();
  application_initialize_before_timer_start();
  startup_validate_resident_boot_crc();
  startup_start_timers_and_load_steady_periods();
  priority_mask_restore(0);
  if ((in_FPEC & 1) != 0) {
    in_FPIPR = in_FPIPR & 0x1f;
    if (0xf < in_FPIPR) {
      in_FPIPR = 0x10;
    }
    uVar1 = in_FPIPR;
    if (0xf < in_FPIPR) {
      uVar1 = 0xf;
    }
    uVar2 = PMR;
    if ((((uVar2 & 1 << uVar1) == 0) && ((in_ISPR & (1 << in_FPIPR + 1) - 1U & 0xffff) == 0)) &&
       ((camry_psw & 0x80) == 0)) {
      if (((camry_psw & 0xbfffffdf) >> 0xf & 1) != 0) {
        in_RBASE = camry_SR[1][3];
      }
      (*(int (*)())camry_indirect((uint32_t)((in_RBASE & 0xfffffe00) + 0x70)))();
    }
  }
  __enable_irq();
  run_eic136_foreground_dispatch_loop_66062();
  { if (!camry_halted) { camry_gpr[31] = camry_read32((camry_sp + 0u) & ~3u); camry_sp += 4u; camry_gpr[3] = camry_sp; } return; }
}

void run_init_chain_6385c(void)

{
  initialize_serial_frames_and_wait_receive_bit0_63874();
  reset_handshake_flags_and_run_clock_modes2_0_63d4a();
  run_init_chain_6484e();
  initialize_markers_and_run_output_status_checks_64c00();
  return;
}

void initialize_serial_frames_and_wait_receive_bit0_63874(void)

{
  uint8_t stack_record_38[56];
  uint outer_iterations;
  char cVar1;
  undefined8 uVar2;
  int iVar3;
  byte bVar4;
  
  uVar2 = 0xfebeb800;
  bVar4 = 0;
  iVar3 = 0xff;
  initialize_serial_receive_frame_and_check_byte_613c8();
  initialize_serial_transmit_bitmap_frame_616fc();
  (*((uint16_t *)(stack_record_38 + 16))) = 0x8200;
  (*((uint16_t *)(stack_record_38 + 18))) = 0;
  (*((uint16_t *)(stack_record_38 + 20))) = 0x5018;
  (*((uint16_t *)(stack_record_38 + 22))) = 0x1f00;
  append_frame_check_byte_transmit_and_snapshot_61836(((uint16_t *)((stack_record_38 + 16))));
  outer_iterations = DAT_00030d7c;
  spin_wait(DAT_00030d7c);
  do {
    (*((uint16_t *)(stack_record_38 + 14))) = 0x1f00;
    (*((uint16_t *)(stack_record_38 + 12))) = 0x5018;
    (*((uint16_t *)(stack_record_38 + 10))) = 0;
    (*((uint16_t *)(stack_record_38 + 8))) = 0x8200;
    append_frame_check_byte_transmit_and_snapshot_61836(((uint16_t *)((stack_record_38 + 8))));
    spin_wait(outer_iterations);
    (*((uint16_t *)(stack_record_38 + 6))) = 0x1f00;
    (*((uint16_t *)(stack_record_38 + 4))) = 0x5018;
    (*((uint16_t *)(stack_record_38 + 2))) = 0;
    (*((uint16_t *)(stack_record_38 + 0))) = 0x8200;
    append_frame_check_byte_transmit_and_snapshot_61836(((uint16_t *)(stack_record_38)));
    spin_wait(outer_iterations);
    poll_serial_frame_and_accept_matching_check_byte_614d4();
    cVar1 = '\0';
    if (((*((byte *)camry_host_ptr((uint32_t)((int)uVar2 + -0x7fc6)))) & 1) != 0) {
      cVar1 = 'Z';
    }
    (*((char *)camry_host_ptr((uint32_t)((int)uVar2 + -0x8000)))) = cVar1;
    if (cVar1 == 'Z') {
      iVar3 = 0;
    }
    else if (1 < bVar4) {
                    /* WARNING: Subroutine does not return */
      enter_terminal_hardware_sequence();
    }
    bVar4 = bVar4 + 1;
  } while (iVar3 == 0xff);
  return;
}

int poll_receive_bit7_clear_with_8200_frames_63922(void)

{
  int iVar1;
  undefined8 uVar2;
  int iVar3;
  byte bVar4;
  undefined2 record[4];
  
  uVar2 = 0xfebeb800;
  bVar4 = 0;
  iVar3 = 0xff;
  do {
    record[0] = 0x8200;
    record[1] = 0;
    record[2] = 0x5018;
    record[3] = 0x1f00;
    append_frame_check_byte_transmit_and_snapshot_61836(record);
    spin_wait(DAT_00030d80);
    poll_serial_frame_and_accept_matching_check_byte_614d4();
    iVar1 = 0;
    if (((*((byte *)camry_host_ptr((uint32_t)((int)uVar2 + -0x7fc8)))) & 0x80) != 0) {
      iVar1 = 0x5a;
    }
    if (iVar1 == 0) {
      iVar3 = 0;
    }
    else if (1 < bVar4) {
      iVar3 = 0x11;
    }
    bVar4 = bVar4 + 1;
  } while (iVar3 == 0xff);
  return iVar3;
}

void record_handshake_failure_and_send_terminal_frames_63984(char param_1)

{
  uint8_t stack_record_24[36];
  uint outer_iterations;
  undefined2 *puVar1;
  
  if (param_1 == '3') {
    publish_redundant_u16
              (0xa55a,(ushort *)((undefined *)camry_host_ptr(0xfebe39c6u)),(ushort *)((undefined *)camry_host_ptr(0xfebe8de8u)),(ushort *)((undefined *)camry_host_ptr(0xfebe8dfcu)));
    return;
  }
  puVar1 = ((undefined *)camry_host_ptr(0xfebe39c2u));
  if (((param_1 == '\"') || (puVar1 = ((undefined *)camry_host_ptr(0xfebe39c0u)), param_1 == '\x11')) ||
     (puVar1 = ((undefined *)camry_host_ptr(0xfebe39c4u)), param_1 == 'D')) {
    *puVar1 = 0xa55a;
  }
  (*((uint16_t *)(stack_record_24 + 14))) = 0x1f00;
  (*((uint16_t *)(stack_record_24 + 12))) = 0x5018;
  (*((uint16_t *)(stack_record_24 + 10))) = 0;
  (*((uint16_t *)(stack_record_24 + 8))) = 0x8380;
  append_frame_check_byte_transmit_and_snapshot_61836(((uint16_t *)((stack_record_24 + 8))));
  outer_iterations = DAT_00030d80;
  spin_wait(DAT_00030d80);
  (*((uint16_t *)(stack_record_24 + 6))) = 0x1f00;
  (*((uint16_t *)(stack_record_24 + 4))) = 0x5018;
  (*((uint16_t *)(stack_record_24 + 2))) = 0;
  (*((uint16_t *)(stack_record_24 + 0))) = 0x8000;
  append_frame_check_byte_transmit_and_snapshot_61836(((uint16_t *)(stack_record_24)));
  spin_wait(outer_iterations);
                    /* WARNING: Subroutine does not return */
  enter_terminal_hardware_sequence();
}

undefined4 change_clock_mode_and_check_receive_bit7_transition_63a18(undefined1 param_1)

{
  uint8_t stack_record_2c[44];
  uint outer_iterations;
  undefined8 uVar1;
  int iVar2;
  byte bVar3;
  int iVar4;
  
  uVar1 = 0xfebeb800;
  bVar3 = 0;
  iVar4 = 0xff;
  iVar2 = map_clock3_mode_to_divider_61906(param_1);
  if (iVar2 == 0) {
    spin_wait(DAT_00030d88);
    (*((uint16_t *)(stack_record_2c + 16))) = 0x8200;
    (*((uint16_t *)(stack_record_2c + 18))) = 0;
    (*((uint16_t *)(stack_record_2c + 20))) = 0x5018;
    (*((uint16_t *)(stack_record_2c + 22))) = 0x1f00;
    append_frame_check_byte_transmit_and_snapshot_61836(((uint16_t *)((stack_record_2c + 16))));
    outer_iterations = DAT_00030d80;
    spin_wait(DAT_00030d80);
    do {
      (*((uint16_t *)(stack_record_2c + 8))) = 0x8200;
      (*((uint16_t *)(stack_record_2c + 10))) = 0;
      (*((uint16_t *)(stack_record_2c + 12))) = 0x5018;
      (*((uint16_t *)(stack_record_2c + 14))) = 0x1f00;
      append_frame_check_byte_transmit_and_snapshot_61836(((uint16_t *)((stack_record_2c + 8))));
      spin_wait(outer_iterations);
      poll_serial_frame_and_accept_matching_check_byte_614d4();
      iVar2 = 0;
      if (((*((byte *)camry_host_ptr((uint32_t)((int)uVar1 + -0x7fc8)))) & 0x80) != 0) {
        iVar2 = 0x5a;
      }
      if (iVar2 == 0) {
        iVar4 = 0;
      }
      else if (1 < bVar3) {
        iVar4 = 0x11;
      }
      bVar3 = bVar3 + 1;
    } while (iVar4 == 0xff);
    if (iVar4 == 0x11) {
      return 0x11;
    }
    spin_wait(startup_spin_iteration_count);
    for (bVar3 = 0; bVar3 <= DAT_00030d94; bVar3 = bVar3 + 1) {
      if (iVar2 == 0x5a) {
        return 0;
      }
      (*((uint16_t *)(stack_record_2c + 0))) = 0x8200;
      (*((uint16_t *)(stack_record_2c + 2))) = 0;
      (*((uint16_t *)(stack_record_2c + 4))) = 0x5018;
      (*((uint16_t *)(stack_record_2c + 6))) = 0x1f00;
      append_frame_check_byte_transmit_and_snapshot_61836(((uint16_t *)(stack_record_2c)));
      spin_wait(DAT_00030d90);
      poll_serial_frame_and_accept_matching_check_byte_614d4();
      iVar2 = 0;
      if (((*((byte *)camry_host_ptr((uint32_t)((int)uVar1 + -0x7fc8)))) & 0x80) != 0) {
        iVar2 = 0x5a;
      }
    }
  }
  return 0x11;
}

int poll_receive_bit11_set_with_8200_frames_63b24(void)

{
  uint8_t stack_record_14[20];
  int iVar1;
  undefined8 uVar2;
  int iVar3;
  byte bVar4;
  
  uVar2 = 0xfebeb800;
  bVar4 = 0;
  iVar3 = 0xff;
  do {
    (*((uint16_t *)(stack_record_14 + 0))) = 0x8200;
    (*((uint16_t *)(stack_record_14 + 2))) = 0;
    (*((uint16_t *)(stack_record_14 + 4))) = 0x5018;
    (*((uint16_t *)(stack_record_14 + 6))) = 0x1f00;
    append_frame_check_byte_transmit_and_snapshot_61836(stack_record_14);
    spin_wait(DAT_00030d80);
    poll_serial_frame_and_accept_matching_check_byte_614d4();
    iVar1 = 0;
    if (((*((byte *)camry_host_ptr((uint32_t)((int)uVar2 + -0x7fc7)))) & 8) != 0) {
      iVar1 = 0x5a;
    }
    if (iVar1 == 0x5a) {
      iVar3 = 0;
    }
    else if (1 < bVar4) {
      iVar3 = 0x11;
    }
    bVar4 = bVar4 + 1;
  } while (iVar3 == 0xff);
  return iVar3;
}

int set_clock_mode1_and_poll_receive_bits7_11_clear_63b88(void)

{
  ushort uVar1;
  uint outer_iterations;
  int iVar2;
  undefined8 uVar3;
  int iVar4;
  byte bVar5;
  int iVar6;
  undefined2 record[4];
  
  uVar3 = 0xfebeb800;
  bVar5 = 0;
  iVar6 = 0xff;
  iVar4 = map_clock3_mode_to_divider_61906(1);
  spin_wait(DAT_00030d84);
  record[0] = 0x8380;
  record[1] = 0;
  record[2] = 0x5018;
  record[3] = 0x1f00;
  append_frame_check_byte_transmit_and_snapshot_61836(record);
  outer_iterations = DAT_00030d80;
  spin_wait(DAT_00030d80);
  if (iVar4 == 0) {
    do {
      record[0] = 0x8380;
      record[1] = 0;
      record[2] = 0x5018;
      record[3] = 0x1f00;
      append_frame_check_byte_transmit_and_snapshot_61836(record);
      spin_wait(outer_iterations);
      record[0] = 0x8380;
      record[1] = 0;
      record[2] = 0x5018;
      record[3] = 0x1f00;
      append_frame_check_byte_transmit_and_snapshot_61836(record);
      spin_wait(outer_iterations);
      poll_serial_frame_and_accept_matching_check_byte_614d4();
      uVar1 = (*((ushort *)camry_host_ptr((uint32_t)((int)uVar3 + -0x7fc8))));
      iVar4 = 0;
      if ((uVar1 >> 7 & 1) != 0) {
        iVar4 = 0x5a;
      }
      iVar2 = 0;
      if ((uVar1 >> 0xb & 1) != 0) {
        iVar2 = 0x5a;
      }
      if ((iVar4 == 0) && (iVar2 == 0)) {
        iVar6 = 0;
      }
      else if (1 < bVar5) {
        iVar6 = 0x11;
      }
      bVar5 = bVar5 + 1;
    } while (iVar6 == 0xff);
  }
  else {
    iVar6 = 0x11;
  }
  return iVar6;
}

void run_clock_mode_serial_handshake_checks_63c5c(undefined1 param_1)

{
  uint8_t stack_record_1c[28];
  camry_fill_bytes(stack_record_1c, sizeof stack_record_1c);
  int iVar1;
  int iVar2;
  int iVar3;
  uint32_t puVar4;
  int iVar5;
  
  iVar2 = DAT_febe8df8;
  iVar1 = DAT_febe8de4;
  iVar5 = DAT_febe39b4;
  puVar4 = (0xfebeb800u);
  iVar3 = 0;
  if ((DAT_febe3838 & 0x80) != 0) {
    iVar3 = 0x5a;
  }
  if ((iVar3 != 0) && (puVar4 = (0xfebeb800u), iVar3 = poll_receive_bit7_clear_with_8200_frames_63922(), iVar3 == 0x11)) {
    record_handshake_failure_and_send_terminal_frames_63984(0x11);
  }
  iVar3 = 0;
  if (((*((volatile undefined *)camry_host_ptr((uint32_t)(0xfebeb800u + (uint32_t)(-0x7fc7) * 1u)))) & 8) != 0) {
    iVar3 = 0x5a;
  }
  if (iVar3 == 0x5a) {
    if (((iVar5 == 0x7c7c7c7c) && (iVar1 == 0x29292929)) && (iVar2 == -0x2929292a)) {
      publish_redundant_u16
                (0xa55a,(ushort *)(((undefined *)camry_host_ptr((uint32_t)(0xfebeb800u + (uint32_t)(-0x7e38) * 1u)))),(ushort *)(((undefined *)camry_host_ptr((uint32_t)(0xfebeb800u + (uint32_t)(-0x2a16) * 1u)))),
                 (ushort *)(((undefined *)camry_host_ptr((uint32_t)(0xfebeb800u + (uint32_t)(-0x2a02) * 1u)))));
    }
    (*((uint16_t *)(stack_record_1c + 0))) = 0x8380;
    (*((uint16_t *)(stack_record_1c + 2))) = 0;
    (*((uint16_t *)(stack_record_1c + 4))) = 0x5018;
    (*((uint16_t *)(stack_record_1c + 6))) = 0x1f00;
    append_frame_check_byte_transmit_and_snapshot_61836(((uint16_t *)(stack_record_1c)));
    spin_wait(DAT_00030d80);
  }
  iVar5 = change_clock_mode_and_check_receive_bit7_transition_63a18(param_1);
  if (iVar5 == 0x11) {
    record_handshake_failure_and_send_terminal_frames_63984(0x22);
  }
  iVar5 = 0;
  if (((*((volatile undefined *)camry_host_ptr((uint32_t)(0xfebeb800u + (uint32_t)(-0x7fc7) * 1u)))) & 8) != 0) {
    iVar5 = 0x5a;
  }
  if ((iVar5 != 0x5a) && (iVar5 = poll_receive_bit11_set_with_8200_frames_63b24(), iVar5 == 0x11)) {
    record_handshake_failure_and_send_terminal_frames_63984(0x33);
  }
  iVar5 = set_clock_mode1_and_poll_receive_bits7_11_clear_63b88();
  if (iVar5 == 0x11) {
    record_handshake_failure_and_send_terminal_frames_63984(0x44);
  }
  return;
}

void reset_handshake_flags_and_run_clock_modes2_0_63d4a(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  publish_redundant_u16
            (0,(ushort *)((undefined *)camry_host_ptr(0xfebe39c6u)),(ushort *)((undefined *)camry_host_ptr(0xfebe8de8u)),(ushort *)((undefined *)camry_host_ptr(0xfebe8dfcu)));
  publish_redundant_u16
            (0,((ushort *)camry_host_ptr((uint32_t)(puVar1 + -0x7e38))),((ushort *)camry_host_ptr((uint32_t)(puVar1 + -0x2a16))),
             ((ushort *)camry_host_ptr((uint32_t)(puVar1 + -0x2a02))));
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x7e40)))) = 0;
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x7e3e)))) = 0;
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x7e3c)))) = 0;
  run_clock_mode_serial_handshake_checks_63c5c(2);
  run_clock_mode_serial_handshake_checks_63c5c(0);
  return;
}

short get_redundant_handshake_flag_if_a55a_63d8e(void)

{
  int iVar1;
  short sStack_6;
  
  iVar1 = read_xor_redundant_u16_with_vote_status_707ac(((undefined *)camry_host_ptr(0xfebe39c8u)),((undefined *)camry_host_ptr(0xfebe8deau)),((undefined *)camry_host_ptr(0xfebe8dfeu)),&sStack_6);
  if ((iVar1 != 0) || (sStack_6 != -0x5aa6)) {
    sStack_6 = 0;
  }
  return sStack_6;
}

void clear_redundant_error_check_flags_and_snapshot_63dba(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  publish_redundant_u16
            (0,(ushort *)((undefined *)camry_host_ptr(0xfebe39cau)),(ushort *)((undefined *)camry_host_ptr(0xfebe8decu)),(ushort *)((undefined *)camry_host_ptr(0xfebe8e00u)));
  publish_redundant_u16
            (0,((ushort *)camry_host_ptr((uint32_t)(puVar1 + -0x7e34))),((ushort *)camry_host_ptr((uint32_t)(puVar1 + -0x2a12))),
             ((ushort *)camry_host_ptr((uint32_t)(puVar1 + -0x29fe))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x7e32))))) = 0;
  return;
}

void send_error_check_frames_and_snapshot_receive_top_bits_63dea(void)

{
  uint uVar1;
  int iVar2;
  uint32_t puVar3;
  undefined1 uVar4;
  undefined2 record[4];
  
  puVar3 = 0xfebeb800u;
  iVar2 = 0;
  uVar1 = DAT_fff81000;
  if ((DAT_febe3839 & 1) != 0) {
    iVar2 = 0x5a;
  }
  if (iVar2 == 0x5a) {
    puVar3 = 0xfebeb800u;
    if ((((DAT_febe39b4 == 0x7c7c7c7c) && (DAT_febe8de4 == 0x29292929)) &&
        (DAT_febe8df8 == -0x2929292a)) && ((uVar1 & 1) == 0)) {
      puVar3 = 0xfebeb800u;
      publish_redundant_u16
                (0xa55a,(ushort *)((undefined *)camry_host_ptr(0xfebe39ccu)),(ushort *)((undefined *)camry_host_ptr(0xfebe8deeu)),(ushort *)((undefined *)camry_host_ptr(0xfebe8e02u)));
    }
    record[0] = 0x8250;
    record[1] = 0;
    record[2] = 0x5018;
    record[3] = 0x1f00;
    append_frame_check_byte_transmit_and_snapshot_61836(record);
    spin_wait(DAT_00030d98);
  }
  uVar4 = pack_receive_frame_top_three_bits_614b0();
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x7e32))))) = uVar4;
  record[0] = 0x8210;
  record[1] = 0;
  record[2] = 0x5018;
  record[3] = 0x1f00;
  append_frame_check_byte_transmit_and_snapshot_61836(record);
  spin_wait(DAT_00030d98);
  return;
}

void record_error_check_failure_or_send_terminal_frames_63ea4(char param_1)

{
  uint8_t stack_record_24[36];
  uint outer_iterations;
  
  if (param_1 == '3') {
    publish_redundant_u16
              (0xa55a,(ushort *)((undefined *)camry_host_ptr(0xfebe39cau)),(ushort *)((undefined *)camry_host_ptr(0xfebe8decu)),(ushort *)((undefined *)camry_host_ptr(0xfebe8e00u)));
    return;
  }
  if (param_1 == '\"') {
    store_three_pattern_encoded_control_words_62b90(0x3e3e3e3e);
  }
  (*((uint16_t *)(stack_record_24 + 14))) = 0x1f00;
  (*((uint16_t *)(stack_record_24 + 12))) = 0x5018;
  (*((uint16_t *)(stack_record_24 + 10))) = 0;
  (*((uint16_t *)(stack_record_24 + 8))) = 0x8250;
  append_frame_check_byte_transmit_and_snapshot_61836(((uint16_t *)((stack_record_24 + 8))));
  outer_iterations = DAT_00030d98;
  spin_wait(DAT_00030d98);
  (*((uint16_t *)(stack_record_24 + 6))) = 0x1f00;
  (*((uint16_t *)(stack_record_24 + 4))) = 0x5018;
  (*((uint16_t *)(stack_record_24 + 2))) = 0;
  (*((uint16_t *)(stack_record_24 + 0))) = 0x8000;
  append_frame_check_byte_transmit_and_snapshot_61836(((uint16_t *)(stack_record_24)));
  spin_wait(outer_iterations);
                    /* WARNING: Subroutine does not return */
  enter_terminal_hardware_sequence();
}

void clear_ecm_status_bit2_with_three_attempt_limit_63f24(void)

{
  uchar uVar1;
  byte bVar2;
  
  bVar2 = 0;
  do {
    bVar2 = bVar2 + 1;
    if (3 < bVar2) {
      record_error_check_failure_or_send_terminal_frames_63ea4(0x11);
    }
    ECMPCMD1 = 0xa5;
    ECMESSTC0 = 4;
    ECMESSTC0 = 0xfffffffb;
    ECMESSTC0 = 4;
    uVar1 = ECMPS;
  } while (uVar1 != '\0');
  return;
}

void write_error_check_mask_bfff7f7f_63f5e(void)

{
  Ramffc4ca00 = 0xbfff7f7f;
  return;
}

undefined4 check_master_clear_checker_set_and_eic8_pending_63f6c(void)

{
  uint uVar1;
  uint uVar2;
  uint16_t EVar3;
  
  uVar1 = ECMMESSTR2;
  uVar2 = ECMCESSTR2;
  EVar3 = EIC8;
  if (((!SUB51(((uint5)uVar1 << 1) >> 0x20,0)) && (SUB51(((uint5)uVar2 << 1) >> 0x20,0))) &&
     (((EVar3 >> 12) & 1u) != 0)) {
    return 0;
  }
  return 0x11;
}

undefined4 clear_ecm_error_outputs_and_wait_status_63f94(void)

{
  uchar uVar1;
  uint uVar2;
  uint uVar3;
  byte bVar4;
  
  bVar4 = 0;
  do {
    bVar4 = bVar4 + 1;
    if (3 < bVar4) {
      record_error_check_failure_or_send_terminal_frames_63ea4(0x11);
    }
    ECMMPCMD0 = 0xa5;
    ECMMECLR = '\x01';
    ECMMECLR = 0xfe;
    ECMMECLR = '\x01';
    uVar1 = ECMPS;
  } while (uVar1 != '\0');
  bVar4 = 0;
  do {
    bVar4 = bVar4 + 1;
    if (3 < bVar4) {
      record_error_check_failure_or_send_terminal_frames_63ea4(0x11);
    }
    ECMCPCMD0 = 0xa5;
    ECMCECLR = '\x01';
    ECMCECLR = 0xfe;
    ECMCECLR = '\x01';
    uVar1 = ECMPS;
  } while (uVar1 != '\0');
  bVar4 = 0;
  do {
    bVar4 = bVar4 + 1;
    if (3 < bVar4) {
      record_error_check_failure_or_send_terminal_frames_63ea4(0x11);
    }
    ECMPCMD1 = 0xa5;
    ECMESSTC2 = 0x10000000;
    ECMESSTC2 = 0xefffffff;
    ECMESSTC2 = 0x10000000;
    uVar1 = ECMPS;
  } while (uVar1 != '\0');
  uVar2 = 0x80000000;
  bVar4 = 0;
  uVar3 = 0;
  while ((-1 < (int)uVar3 || ((int)uVar2 < 0))) {
    uVar3 = ECMMESSTR2;
    bVar4 = bVar4 + 1;
    uVar2 = ECMCESSTR2;
    if (0x1e < bVar4) {
      return 0x11;
    }
  }
  return 0;
}
