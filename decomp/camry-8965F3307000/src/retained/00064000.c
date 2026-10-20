#include "common.h"

void retry_ecm_output_clear_and_delay_6405e(void)

{
  int iVar1;
  byte bVar2;
  
  bVar2 = 0;
  Ramffc4ca00 = 0x80000000;
  clear_ecm_status_bit2_with_three_attempt_limit_63f24();
  do {
    iVar1 = clear_ecm_error_outputs_and_wait_status_63f94();
    if ((iVar1 != 0) && (1 < bVar2)) {
      record_error_check_failure_or_send_terminal_frames_63ea4(0x11);
    }
    bVar2 = bVar2 + 1;
  } while (iVar1 != 0);
  spin_wait(DAT_00030d9c);
  return;
}

int poll_command_8250_status_bits_clear_640a0(void)

{
  ushort uVar1;
  uint outer_iterations;
  int iVar2;
  int iVar3;
  undefined8 uVar4;
  int iVar5;
  int iVar6;
  byte bVar7;
  undefined2 record[4];
  
  uVar4 = 0xfebeb800;
  bVar7 = 0;
  iVar6 = 0xff;
  do {
    record[0] = 0x8250;
    record[1] = 0;
    record[2] = 0x5018;
    record[3] = 0x1f00;
    append_frame_check_byte_transmit_and_snapshot_61836(record);
    outer_iterations = DAT_00030d98;
    spin_wait(DAT_00030d98);
    record[0] = 0x8250;
    record[1] = 0;
    record[2] = 0x5018;
    record[3] = 0x1f00;
    append_frame_check_byte_transmit_and_snapshot_61836(record);
    spin_wait(outer_iterations);
    poll_serial_frame_and_accept_matching_check_byte_614d4();
    uVar1 = (*((ushort *)camry_host_ptr((uint32_t)((int)uVar4 + -0x7fc8))));
    iVar2 = 0;
    if ((uVar1 >> 7 & 1) != 0) {
      iVar2 = 0x5a;
    }
    iVar3 = 0;
    if ((uVar1 >> 8 & 1) != 0) {
      iVar3 = 0x5a;
    }
    iVar5 = pack_receive_frame_top_three_bits_614b0();
    if (((iVar2 == 0) && (iVar3 == 0)) && (iVar5 == 0)) {
      iVar6 = 0;
    }
    else if (1 < bVar7) {
      iVar6 = 0x11;
    }
    bVar7 = bVar7 + 1;
  } while (iVar6 == 0xff);
  return iVar6;
}

void exercise_ecm_interrupt_configuration_6413c(void)

{
  uchar uVar1;
  uint outer_iterations;
  int iVar2;
  byte bVar3;
  
  clear_ecm_status_bit2_with_three_attempt_limit_63f24();
  bVar3 = 0;
  EIC8 = (uint16_t)0xc0;
  while( true ) {
    ECMPCMD1 = 0xa5;
    ECMMICFG0 = 4;
    ECMMICFG0 = 0xfffffffb;
    ECMMICFG0 = 4;
    uVar1 = ECMPS;
    if (uVar1 == '\0') break;
    bVar3 = bVar3 + 1;
    if (2 < bVar3) {
                    /* WARNING: Subroutine does not return */
      enter_terminal_hardware_sequence();
    }
  }
  write_error_check_mask_bfff7f7f_63f5e();
  outer_iterations = DAT_00030da0;
  spin_wait(DAT_00030da0);
  iVar2 = check_master_clear_checker_set_and_eic8_pending_63f6c();
  bVar3 = 0;
  while (retry_ecm_output_clear_and_delay_6405e(), iVar2 != 0) {
    bVar3 = bVar3 + 1;
    if (2 < bVar3) {
      record_error_check_failure_or_send_terminal_frames_63ea4(0x55);
    }
    write_error_check_mask_bfff7f7f_63f5e();
    spin_wait(outer_iterations);
    iVar2 = check_master_clear_checker_set_and_eic8_pending_63f6c();
  }
  bVar3 = 0;
  do {
    ECMPCMD1 = 0xa5;
    ECMMICFG0 = 0;
    ECMMICFG0 = 0xffffffff;
    ECMMICFG0 = 0;
    uVar1 = ECMPS;
    if (uVar1 == '\0') {
      EIC8 = (uint16_t)0x40;
      iVar2 = poll_command_8250_status_bits_clear_640a0();
      if (iVar2 == 0x11) {
        record_error_check_failure_or_send_terminal_frames_63ea4(0x44);
      }
      return;
    }
    bVar3 = bVar3 + 1;
  } while (bVar3 < 3);
                    /* WARNING: Subroutine does not return */
  enter_terminal_hardware_sequence();
}

void set_ecm_master_error_output_6420e(void)

{
  uchar uVar1;
  byte bVar2;
  
  bVar2 = 0;
  do {
    bVar2 = bVar2 + 1;
    if (3 < bVar2) {
      record_error_check_failure_or_send_terminal_frames_63ea4(0x11);
    }
    ECMMPCMD0 = 0xa5;
    ECMMESET = '\x01';
    ECMMESET = 0xfe;
    ECMMESET = '\x01';
    uVar1 = ECMPS;
  } while (uVar1 != '\0');
  bVar2 = 0;
  do {
    bVar2 = bVar2 + 1;
    if (3 < bVar2) {
      record_error_check_failure_or_send_terminal_frames_63ea4(0x11);
    }
    ECMPCMD1 = 0xa5;
    ECMESSTC2 = 0x10000000;
    ECMESSTC2 = 0xefffffff;
    ECMESSTC2 = 0x10000000;
    uVar1 = ECMPS;
  } while (uVar1 != '\0');
  return;
}

int poll_status_bit7_against_iteration_phase_6427a(byte param_1)

{
  uint outer_iterations;
  int iVar1;
  undefined8 uVar2;
  int iVar3;
  byte bVar4;
  bool bVar5;
  undefined2 record[4];
  
  uVar2 = 0xfebeb800;
  bVar4 = 0;
  iVar3 = 0xff;
  record[0] = 0x8200;
  record[1] = 0;
  record[2] = 0x5018;
  record[3] = 0x1f00;
  append_frame_check_byte_transmit_and_snapshot_61836(record);
  outer_iterations = DAT_00030d98;
  spin_wait(DAT_00030d98);
  do {
    record[0] = 0x8200;
    record[1] = 0;
    record[2] = 0x5018;
    record[3] = 0x1f00;
    append_frame_check_byte_transmit_and_snapshot_61836(record);
    spin_wait(outer_iterations);
    poll_serial_frame_and_accept_matching_check_byte_614d4();
    iVar1 = 0;
    if (((*((byte *)camry_host_ptr((uint32_t)((int)uVar2 + -0x7fc8)))) & 0x80) != 0) {
      iVar1 = 0x5a;
    }
    if (param_1 < 4) {
      bVar5 = iVar1 == 0;
    }
    else {
      bVar5 = iVar1 == 0x5a;
    }
    if (bVar5) {
      iVar3 = 0;
    }
    else if (1 < bVar4) {
      iVar3 = 0x11;
    }
    bVar4 = bVar4 + 1;
  } while (iVar3 == 0xff);
  return iVar3;
}

void clear_ecm_master_output_and_wait_bit31_set_64310(void)

{
  uchar uVar1;
  uint uVar2;
  int iVar3;
  byte bVar4;
  byte bVar5;
  
  bVar4 = 0;
  iVar3 = 0xff;
  do {
    bVar5 = 0;
    if (iVar3 == 0) {
      do {
        bVar5 = bVar5 + 1;
        if (3 < bVar5) {
          record_error_check_failure_or_send_terminal_frames_63ea4(0x11);
        }
        ECMPCMD1 = 0xa5;
        ECMESSTC2 = 0x10000000;
        ECMESSTC2 = 0xefffffff;
        ECMESSTC2 = 0x10000000;
        uVar1 = ECMPS;
      } while (uVar1 != '\0');
      spin_wait(DAT_00030d9c);
      return;
    }
    do {
      bVar5 = bVar5 + 1;
      if (3 < bVar5) {
        record_error_check_failure_or_send_terminal_frames_63ea4(0x11);
      }
      ECMPCMD1 = 0xa5;
      ECMESSTC2 = 0x40000000;
      ECMESSTC2 = 0xbfffffff;
      ECMESSTC2 = 0x40000000;
      uVar1 = ECMPS;
    } while (uVar1 != '\0');
    bVar5 = 0;
    do {
      bVar5 = bVar5 + 1;
      if (3 < bVar5) {
        record_error_check_failure_or_send_terminal_frames_63ea4(0x11);
      }
      ECMMPCMD0 = 0xa5;
      ECMMECLR = '\x01';
      ECMMECLR = 0xfe;
      ECMMECLR = '\x01';
      uVar1 = ECMPS;
    } while (uVar1 != '\0');
    bVar5 = 0;
    uVar2 = 0;
    do {
      if (SUB51(((uint5)uVar2 << 1) >> 0x20,0)) {
        iVar3 = 0;
        goto LAB_000643aa;
      }
      uVar2 = ECMMESSTR2;
      bVar5 = bVar5 + 1;
    } while (bVar5 < 0x1f);
    iVar3 = 0x11;
    if (1 < bVar4) {
      record_error_check_failure_or_send_terminal_frames_63ea4(0x11);
    }
LAB_000643aa:
    bVar4 = bVar4 + 1;
  } while( true );
}

void set_ecm_checker_error_output_643f6(void)

{
  uchar uVar1;
  byte bVar2;
  
  bVar2 = 0;
  do {
    bVar2 = bVar2 + 1;
    if (3 < bVar2) {
      record_error_check_failure_or_send_terminal_frames_63ea4(0x11);
    }
    ECMCPCMD0 = 0xa5;
    ECMCESET = '\x01';
    ECMCESET = 0xfe;
    ECMCESET = '\x01';
    uVar1 = ECMPS;
  } while (uVar1 != '\0');
  bVar2 = 0;
  do {
    bVar2 = bVar2 + 1;
    if (3 < bVar2) {
      record_error_check_failure_or_send_terminal_frames_63ea4(0x11);
    }
    ECMPCMD1 = 0xa5;
    ECMESSTC2 = 0x10000000;
    ECMESSTC2 = 0xefffffff;
    ECMESSTC2 = 0x10000000;
    uVar1 = ECMPS;
  } while (uVar1 != '\0');
  return;
}

void clear_ecm_checker_output_and_wait_bit31_clear_64464(void)

{
  uchar uVar1;
  uint uVar2;
  int iVar3;
  byte bVar4;
  byte bVar5;
  
  bVar4 = 0;
  iVar3 = 0xff;
  do {
    bVar5 = 0;
    if (iVar3 == 0) {
      do {
        bVar5 = bVar5 + 1;
        if (3 < bVar5) {
          record_error_check_failure_or_send_terminal_frames_63ea4(0x11);
        }
        ECMPCMD1 = 0xa5;
        ECMESSTC2 = 0x10000000;
        ECMESSTC2 = 0xefffffff;
        ECMESSTC2 = 0x10000000;
        uVar1 = ECMPS;
      } while (uVar1 != '\0');
      spin_wait(DAT_00030d9c);
      return;
    }
    do {
      bVar5 = bVar5 + 1;
      if (3 < bVar5) {
        record_error_check_failure_or_send_terminal_frames_63ea4(0x11);
      }
      ECMPCMD1 = 0xa5;
      ECMESSTC2 = 0x40000000;
      ECMESSTC2 = 0xbfffffff;
      ECMESSTC2 = 0x40000000;
      uVar1 = ECMPS;
    } while (uVar1 != '\0');
    bVar5 = 0;
    do {
      bVar5 = bVar5 + 1;
      if (3 < bVar5) {
        record_error_check_failure_or_send_terminal_frames_63ea4(0x11);
      }
      ECMCPCMD0 = 0xa5;
      ECMCECLR = '\x01';
      ECMCECLR = 0xfe;
      ECMCECLR = '\x01';
      uVar1 = ECMPS;
    } while (uVar1 != '\0');
    uVar2 = 0x80000000;
    bVar5 = 0;
    do {
      if ((uVar2 & 0x80000000) == 0) {
        iVar3 = 0;
        goto LAB_00064502;
      }
      uVar2 = ECMCESSTR2;
      bVar5 = bVar5 + 1;
    } while (bVar5 < 0x1f);
    iVar3 = 0x11;
    if (1 < bVar4) {
      record_error_check_failure_or_send_terminal_frames_63ea4(0x11);
    }
LAB_00064502:
    bVar4 = bVar4 + 1;
  } while( true );
}

int exercise_selected_ecm_output_four_cycles_6454e(char param_1)

{
  uint8_t stack_record_24[36];
  camry_fill_bytes(stack_record_24, sizeof stack_record_24);
  uint outer_iterations;
  int iVar1;
  int iVar2;
  byte bVar3;
  byte bVar4;
  
  bVar3 = 0;
  bVar4 = 0;
  while( true ) {
    bVar4 = bVar4 + 1;
    if (param_1 == '\x11') {
      set_ecm_master_error_output_6420e();
      spin_wait(DAT_00030da0);
      iVar1 = poll_status_bit7_against_iteration_phase_6427a(bVar4);
      clear_ecm_master_output_and_wait_bit31_set_64310();
    }
    else {
      set_ecm_checker_error_output_643f6();
      spin_wait(DAT_00030da0);
      iVar1 = poll_status_bit7_against_iteration_phase_6427a(bVar4);
      clear_ecm_checker_output_and_wait_bit31_clear_64464();
    }
    if (iVar1 == 0x11) break;
    if (3 < bVar4) {
      (*((uint16_t *)(stack_record_24 + 8))) = 0x8200;
      iVar1 = 0xff;
      (*((uint16_t *)(stack_record_24 + 10))) = 0;
      (*((uint16_t *)(stack_record_24 + 12))) = 0x5018;
      (*((uint16_t *)(stack_record_24 + 14))) = 0x1f00;
      append_frame_check_byte_transmit_and_snapshot_61836(((uint16_t *)((stack_record_24 + 8))));
      outer_iterations = DAT_00030d98;
      spin_wait(DAT_00030d98);
      do {
        (*((uint16_t *)(stack_record_24 + 0))) = 0x8200;
        (*((uint16_t *)(stack_record_24 + 2))) = 0;
        (*((uint16_t *)(stack_record_24 + 4))) = 0x5018;
        (*((uint16_t *)(stack_record_24 + 6))) = 0x1f00;
        append_frame_check_byte_transmit_and_snapshot_61836(((uint16_t *)(stack_record_24)));
        spin_wait(outer_iterations);
        poll_serial_frame_and_accept_matching_check_byte_614d4();
        iVar2 = pack_receive_frame_top_three_bits_614b0();
        if (iVar2 == 4) {
          iVar1 = 0;
        }
        else if (1 < bVar3) {
          iVar1 = 0x11;
        }
        bVar3 = bVar3 + 1;
      } while (iVar1 == 0xff);
      return iVar1;
    }
  }
  return 0x11;
}

int poll_command_8200_status_bit8_set_64620(void)

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
    spin_wait(DAT_00030d98);
    poll_serial_frame_and_accept_matching_check_byte_614d4();
    iVar1 = 0;
    if (((*((byte *)camry_host_ptr((uint32_t)((int)uVar2 + -0x7fc7)))) & 1) != 0) {
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

void check_ecm_output_cycles_and_status_64684(undefined1 param_1)

{
  uint32_t puVar1;
  int iVar2;
  
  puVar1 = 0xfebeb800u;
  iVar2 = exercise_selected_ecm_output_four_cycles_6454e(param_1);
  if (iVar2 == 0x11) {
    record_error_check_failure_or_send_terminal_frames_63ea4(0x22);
  }
  iVar2 = 0;
  if (((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x7fc7))))) & 1) != 0) {
    iVar2 = 0x5a;
  }
  if ((iVar2 != 0x5a) && (iVar2 = poll_command_8200_status_bit8_set_64620(), iVar2 == 0x11)) {
    record_error_check_failure_or_send_terminal_frames_63ea4(0x33);
  }
  iVar2 = poll_command_8250_status_bits_clear_640a0();
  if (iVar2 == 0x11) {
    record_error_check_failure_or_send_terminal_frames_63ea4(0x44);
  }
  return;
}

int set_selected_ecm_output_and_poll_bit7_transition_646d6(char param_1)

{
  uint8_t stack_record_2c[44];
  camry_fill_bytes(stack_record_2c, sizeof stack_record_2c);
  uint outer_iterations;
  undefined8 uVar1;
  int iVar2;
  byte bVar3;
  int iVar4;
  
  uVar1 = 0xfebeb800;
  bVar3 = 0;
  iVar4 = 0xff;
  if (param_1 == '\x11') {
    set_ecm_master_error_output_6420e();
  }
  else {
    set_ecm_checker_error_output_643f6();
  }
  spin_wait(DAT_00030da4);
  (*((uint16_t *)(stack_record_2c + 16))) = 0x8200;
  (*((uint16_t *)(stack_record_2c + 18))) = 0;
  (*((uint16_t *)(stack_record_2c + 20))) = 0x5018;
  (*((uint16_t *)(stack_record_2c + 22))) = 0x1f00;
  append_frame_check_byte_transmit_and_snapshot_61836(((uint16_t *)((stack_record_2c + 16))));
  outer_iterations = DAT_00030d98;
  spin_wait(DAT_00030d98);
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
  if (iVar4 != 0x11) {
    spin_wait(DAT_00030da8);
    for (bVar3 = 0; bVar3 <= DAT_00030db0; bVar3 = bVar3 + 1) {
      if (iVar2 == 0x5a) {
        return 0;
      }
      (*((uint16_t *)(stack_record_2c + 0))) = 0x8200;
      (*((uint16_t *)(stack_record_2c + 2))) = 0;
      (*((uint16_t *)(stack_record_2c + 4))) = 0x5018;
      (*((uint16_t *)(stack_record_2c + 6))) = 0x1f00;
      append_frame_check_byte_transmit_and_snapshot_61836(((uint16_t *)(stack_record_2c)));
      spin_wait(DAT_00030dac);
      poll_serial_frame_and_accept_matching_check_byte_614d4();
      iVar2 = 0;
      if (((*((byte *)camry_host_ptr((uint32_t)((int)uVar1 + -0x7fc8)))) & 0x80) != 0) {
        iVar2 = 0x5a;
      }
    }
    iVar4 = 0x11;
  }
  return iVar4;
}

void check_ecm_timed_transition_and_cleanup_647ea(char param_1)

{
  uint32_t puVar1;
  int iVar2;
  
  puVar1 = 0xfebeb800u;
  iVar2 = set_selected_ecm_output_and_poll_bit7_transition_646d6((uint)(byte)param_1);
  if (iVar2 == 0x11) {
    record_error_check_failure_or_send_terminal_frames_63ea4(0x22);
  }
  iVar2 = 0;
  if (((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x7fc7))))) & 1) != 0) {
    iVar2 = 0x5a;
  }
  if ((iVar2 != 0x5a) && (iVar2 = poll_command_8200_status_bit8_set_64620(), iVar2 == 0x11)) {
    record_error_check_failure_or_send_terminal_frames_63ea4(0x33);
  }
  if (param_1 == '\x11') {
    clear_ecm_master_output_and_wait_bit31_set_64310();
  }
  else {
    clear_ecm_checker_output_and_wait_bit31_clear_64464();
  }
  iVar2 = poll_command_8250_status_bits_clear_640a0();
  if (iVar2 == 0x11) {
    record_error_check_failure_or_send_terminal_frames_63ea4(0x44);
  }
  return;
}

void run_init_chain_6484e(void)

{
  clear_redundant_error_check_flags_and_snapshot_63dba();
  send_error_check_frames_and_snapshot_receive_top_bits_63dea();
  exercise_ecm_interrupt_configuration_6413c();
  check_ecm_output_cycles_and_status_64684(0x11);
  check_ecm_output_cycles_and_status_64684(0x22);
  check_ecm_timed_transition_and_cleanup_647ea(0x11);
  check_ecm_timed_transition_and_cleanup_647ea(0x22);
  return;
}

short read_validated_a55a_marker_febe39cc_64882(void)

{
  int iVar1;
  short sStack_6;
  
  iVar1 = read_xor_redundant_u16_with_vote_status_707ac(((undefined *)camry_host_ptr(0xfebe39ccu)),((undefined *)camry_host_ptr(0xfebe8deeu)),((undefined *)camry_host_ptr(0xfebe8e02u)),&sStack_6);
  if ((iVar1 != 0) || (sStack_6 != -0x5aa6)) {
    sStack_6 = 0;
  }
  return sStack_6;
}

int poll_command_5098_bit7_clear_then_set_648ae(void)

{
  uint8_t stack_record_20[32];
  uint outer_iterations;
  int iVar1;
  undefined8 uVar2;
  byte bVar3;
  int iVar4;
  
  uVar2 = 0xfebeb800;
  bVar3 = 0;
  iVar4 = 0xff;
  spin_wait(DAT_00030db8);
  do {
    (*((uint16_t *)(stack_record_20 + 8))) = 0x8200;
    (*((uint16_t *)(stack_record_20 + 10))) = 0;
    (*((uint16_t *)(stack_record_20 + 12))) = 0x5098;
    (*((uint16_t *)(stack_record_20 + 14))) = 0x1f00;
    append_frame_check_byte_transmit_and_snapshot_61836((stack_record_20 + 8));
    outer_iterations = DAT_00030db4;
    spin_wait(DAT_00030db4);
    poll_serial_frame_and_accept_matching_check_byte_614d4();
    iVar1 = 0;
    if (((*((byte *)camry_host_ptr((uint32_t)((int)uVar2 + -0x7fc8)))) & 0x80) != 0) {
      iVar1 = 0x5a;
    }
    if (iVar1 == 0) {
      iVar4 = 0;
    }
    else if (1 < bVar3) {
      iVar4 = 0x11;
    }
    bVar3 = bVar3 + 1;
  } while (iVar4 == 0xff);
  if (iVar4 != 0x11) {
    bVar3 = 0;
    iVar4 = 0xff;
    spin_wait(DAT_00030dbc);
    do {
      (*((uint16_t *)(stack_record_20 + 0))) = 0x8200;
      (*((uint16_t *)(stack_record_20 + 2))) = 0;
      (*((uint16_t *)(stack_record_20 + 4))) = 0x5098;
      (*((uint16_t *)(stack_record_20 + 6))) = 0x1f00;
      append_frame_check_byte_transmit_and_snapshot_61836(stack_record_20);
      spin_wait(outer_iterations);
      poll_serial_frame_and_accept_matching_check_byte_614d4();
      iVar1 = 0;
      if (((*((byte *)camry_host_ptr((uint32_t)((int)uVar2 + -0x7fc8)))) & 0x80) != 0) {
        iVar1 = 0x5a;
      }
      if (iVar1 == 0x5a) {
        iVar4 = 0;
      }
      else if (1 < bVar3) {
        iVar4 = 0x11;
      }
      bVar3 = bVar3 + 1;
    } while (iVar4 == 0xff);
  }
  return iVar4;
}

int poll_command_5098_bit10_clear_then_transition_64986(void)

{
  uint8_t stack_record_2c[44];
  camry_fill_bytes(stack_record_2c, sizeof stack_record_2c);
  uint outer_iterations;
  int iVar1;
  undefined8 uVar2;
  byte bVar3;
  
  uVar2 = 0xfebeb800;
  bVar3 = 0;
  do {
    (*((uint16_t *)(stack_record_2c + 14))) = 0x1f00;
    (*((uint16_t *)(stack_record_2c + 12))) = 0x5098;
    (*((uint16_t *)(stack_record_2c + 10))) = 0;
    (*((uint16_t *)(stack_record_2c + 8))) = 0x8200;
    append_frame_check_byte_transmit_and_snapshot_61836(((uint16_t *)((stack_record_2c + 8))));
    outer_iterations = DAT_00030db4;
    spin_wait(DAT_00030db4);
    (*((uint16_t *)(stack_record_2c + 6))) = 0x1f00;
    (*((uint16_t *)(stack_record_2c + 4))) = 0x5098;
    (*((uint16_t *)(stack_record_2c + 2))) = 0;
    (*((uint16_t *)(stack_record_2c + 0))) = 0x8200;
    append_frame_check_byte_transmit_and_snapshot_61836(((uint16_t *)(stack_record_2c)));
    spin_wait(outer_iterations);
    poll_serial_frame_and_accept_matching_check_byte_614d4();
    iVar1 = 0;
    if (((*((byte *)camry_host_ptr((uint32_t)((int)uVar2 + -0x7fc7)))) & 4) != 0) {
      iVar1 = 0x5a;
    }
    bVar3 = bVar3 + 1;
  } while ((iVar1 == 0x5a) && (bVar3 < 0x19));
  return poll_command_5098_bit7_clear_then_set_648ae();
}

void record_output_check_failure_and_terminate_649f6(char param_1)

{
  uint8_t stack_record_20[32];
  uint outer_iterations;
  uint32_t puVar1;
  undefined2 *puVar2;
  
  puVar1 = 0xfebeb800u;
  if (param_1 == '\"') {
    publish_redundant_u16
              (0xa55a,(ushort *)((undefined *)camry_host_ptr(0xfebe39d4u)),(ushort *)((undefined *)camry_host_ptr(0xfebe8df0u)),(ushort *)((undefined *)camry_host_ptr(0xfebe8e04u)));
    return;
  }
  if (param_1 == '\x11') {
    store_three_pattern_encoded_control_words_62b90(0x6d6d6d6d);
    puVar2 = ((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x7e30)));
  }
  else {
    if (param_1 != '3') goto LAB_00064a3e;
    puVar2 = ((undefined *)camry_host_ptr(0xfebe39d2u));
  }
  *puVar2 = 0xa55a;
LAB_00064a3e:
  (*((uint16_t *)(stack_record_20 + 8))) = 0x8200;
  (*((uint16_t *)(stack_record_20 + 10))) = 0;
  (*((uint16_t *)(stack_record_20 + 12))) = 0x5058;
  (*((uint16_t *)(stack_record_20 + 14))) = 0x1f00;
  append_frame_check_byte_transmit_and_snapshot_61836(((uint16_t *)((stack_record_20 + 8))));
  outer_iterations = DAT_00030db4;
  spin_wait(DAT_00030db4);
  (*((uint16_t *)(stack_record_20 + 0))) = 0x8000;
  (*((uint16_t *)(stack_record_20 + 2))) = 0;
  (*((uint16_t *)(stack_record_20 + 4))) = 0x5018;
  (*((uint16_t *)(stack_record_20 + 6))) = 0x1f00;
  append_frame_check_byte_transmit_and_snapshot_61836(((uint16_t *)(stack_record_20)));
  spin_wait(outer_iterations);
                    /* WARNING: Subroutine does not return */
  enter_terminal_hardware_sequence();
}

int poll_command_8200_status_bit9_set_64a90(void)

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
    spin_wait(DAT_00030db4);
    poll_serial_frame_and_accept_matching_check_byte_614d4();
    iVar1 = 0;
    if (((*((byte *)camry_host_ptr((uint32_t)((int)uVar2 + -0x7fc7)))) & 2) != 0) {
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

int poll_command_5058_status_bits7_and9_clear_64af4(void)

{
  ushort uVar1;
  uint outer_iterations;
  int iVar2;
  int iVar3;
  undefined8 uVar4;
  int iVar5;
  byte bVar6;
  undefined2 record[4];
  
  uVar4 = 0xfebeb800;
  bVar6 = 0;
  iVar5 = 0xff;
  do {
    record[0] = 0x8200;
    record[1] = 0;
    record[2] = 0x5058;
    record[3] = 0x1f00;
    append_frame_check_byte_transmit_and_snapshot_61836(record);
    outer_iterations = DAT_00030db4;
    spin_wait(DAT_00030db4);
    record[0] = 0x8200;
    record[1] = 0;
    record[2] = 0x5058;
    record[3] = 0x1f00;
    append_frame_check_byte_transmit_and_snapshot_61836(record);
    spin_wait(outer_iterations);
    poll_serial_frame_and_accept_matching_check_byte_614d4();
    uVar1 = (*((ushort *)camry_host_ptr((uint32_t)((int)uVar4 + -0x7fc8))));
    iVar2 = 0;
    if ((uVar1 >> 7 & 1) != 0) {
      iVar2 = 0x5a;
    }
    iVar3 = 0;
    if ((uVar1 >> 9 & 1) != 0) {
      iVar3 = 0x5a;
    }
    if ((iVar2 == 0) && (iVar3 == 0)) {
      iVar5 = 0;
    }
    else if (1 < bVar6) {
      iVar5 = 0x11;
    }
    bVar6 = bVar6 + 1;
  } while (iVar5 == 0xff);
  return iVar5;
}

void poll_command_8000_status_bit16_clear_64b86(void)

{
  uint8_t stack_record_30[48];
  uint outer_iterations;
  int iVar1;
  undefined8 uVar2;
  int iVar3;
  byte bVar4;
  
  uVar2 = 0xfebeb800;
  bVar4 = 0;
  iVar3 = 0xff;
  do {
    (*((uint16_t *)(stack_record_30 + 14))) = 0x1f00;
    (*((uint16_t *)(stack_record_30 + 12))) = 0x5018;
    (*((uint16_t *)(stack_record_30 + 10))) = 0;
    (*((uint16_t *)(stack_record_30 + 8))) = 0x8000;
    append_frame_check_byte_transmit_and_snapshot_61836(((uint16_t *)((stack_record_30 + 8))));
    outer_iterations = DAT_00030db4;
    spin_wait(DAT_00030db4);
    (*((uint16_t *)(stack_record_30 + 6))) = 0x1f00;
    (*((uint16_t *)(stack_record_30 + 4))) = 0x5018;
    (*((uint16_t *)(stack_record_30 + 2))) = 0;
    (*((uint16_t *)(stack_record_30 + 0))) = 0x8000;
    append_frame_check_byte_transmit_and_snapshot_61836(((uint16_t *)(stack_record_30)));
    spin_wait(outer_iterations);
    poll_serial_frame_and_accept_matching_check_byte_614d4();
    iVar1 = 0;
    if (((*((byte *)camry_host_ptr((uint32_t)((int)uVar2 + -0x7fc6)))) & 1) != 0) {
      iVar1 = 0x5a;
    }
    if (iVar1 == 0) {
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

void initialize_markers_and_run_output_status_checks_64c00(void)

{
  uint8_t stack_record_18[24];
  camry_fill_bytes(stack_record_18, sizeof stack_record_18);
  uint uVar1;
  int iVar2;
  uint32_t puVar3;
  ushort *raw;
  ushort *xor5555;
  ushort *xorAAAA;
  
  puVar3 = 0xfebeb800u;
  publish_redundant_u16
            (0,(ushort *)((undefined *)camry_host_ptr(0xfebe39d4u)),(ushort *)((undefined *)camry_host_ptr(0xfebe8df0u)),(ushort *)((undefined *)camry_host_ptr(0xfebe8e04u)));
  raw = ((ushort *)camry_host_ptr((uint32_t)(puVar3 + -0x7e2a)));
  xor5555 = ((ushort *)camry_host_ptr((uint32_t)(puVar3 + -0x2a0e)));
  xorAAAA = ((ushort *)camry_host_ptr((uint32_t)(puVar3 + -0x29fa)));
  publish_redundant_u16(0,raw,xor5555,xorAAAA);
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x7e30)))) = 0;
  iVar2 = 0;
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x7e2e)))) = 0;
  uVar1 = DAT_fff81000;
  if (((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x7fc7))))) & 2) != 0) {
    iVar2 = 0x5a;
  }
  if (iVar2 == 0x5a) {
    if (((((*((int *)camry_host_ptr((uint32_t)(puVar3 + -0x7e4c)))) == 0x7c7c7c7c) && ((*((int *)camry_host_ptr((uint32_t)(puVar3 + -0x2a1c)))) == 0x29292929))
        && ((*((int *)camry_host_ptr((uint32_t)(puVar3 + -0x2a08)))) == -0x2929292a)) && ((uVar1 & 1) == 0)) {
      publish_redundant_u16(0xa55a,raw,xor5555,xorAAAA);
    }
    (*((uint16_t *)(stack_record_18 + 0))) = 0x8200;
    (*((uint16_t *)(stack_record_18 + 2))) = 0;
    (*((uint16_t *)(stack_record_18 + 4))) = 0x5058;
    (*((uint16_t *)(stack_record_18 + 6))) = 0x1f00;
    append_frame_check_byte_transmit_and_snapshot_61836(((uint16_t *)(stack_record_18)));
    spin_wait(DAT_00030db4);
  }
  iVar2 = poll_command_5098_bit10_clear_then_transition_64986();
  if (iVar2 == 0x11) {
    record_output_check_failure_and_terminate_649f6(0x11);
  }
  iVar2 = 0;
  if (((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x7fc7))))) & 2) != 0) {
    iVar2 = 0x5a;
  }
  if ((iVar2 != 0x5a) && (iVar2 = poll_command_8200_status_bit9_set_64a90(), iVar2 == 0x11)) {
    record_output_check_failure_and_terminate_649f6(0x22);
  }
  iVar2 = poll_command_5058_status_bits7_and9_clear_64af4();
  if (iVar2 == 0x11) {
    record_output_check_failure_and_terminate_649f6(0x33);
  }
  poll_command_8000_status_bit16_clear_64b86();
  return;
}

short read_validated_a55a_marker_febe39d4_64d00(void)

{
  int iVar1;
  short sStack_6;
  
  iVar1 = read_xor_redundant_u16_with_vote_status_707ac(((undefined *)camry_host_ptr(0xfebe39d4u)),((undefined *)camry_host_ptr(0xfebe8df0u)),((undefined *)camry_host_ptr(0xfebe8e04u)),&sStack_6);
  if ((iVar1 != 0) || (sStack_6 != -0x5aa6)) {
    sStack_6 = 0;
  }
  return sStack_6;
}

short read_validated_a55a_marker_febe39d6_64d2c(void)

{
  int iVar1;
  short sStack_6;
  
  iVar1 = read_xor_redundant_u16_with_vote_status_707ac(((undefined *)camry_host_ptr(0xfebe39d6u)),((undefined *)camry_host_ptr(0xfebe8df2u)),((undefined *)camry_host_ptr(0xfebe8e06u)),&sStack_6);
  if ((iVar1 != 0) || (sStack_6 != -0x5aa6)) {
    sStack_6 = 0;
  }
  return sStack_6;
}

void initialize_execution_profiles(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  
  iVar3 = 0;
  do {
    iVar2 = iVar3 + 1;
    execution_profiles.ch2_exclusive[iVar3] = 0;
    iVar1 = iVar3 + -9;
    iVar3 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  execution_profiles.slot4_exclusive = 0;
  iVar3 = 0;
  do {
    iVar2 = iVar3 + 1;
    execution_profiles.foreground_exclusive[iVar3] = 0;
    iVar1 = iVar3 + -0xf;
    iVar3 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  iVar3 = 0;
  do {
    iVar2 = iVar3 + 1;
    execution_profiles.ch2_inclusive[iVar3] = 0;
    iVar1 = iVar3 + -9;
    iVar3 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  execution_profiles.slot4_inclusive = 0;
  iVar3 = 0;
  do {
    iVar2 = iVar3 + 1;
    execution_profiles.foreground_inclusive[iVar3] = 0;
    iVar1 = iVar3 + -0xf;
    iVar3 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  execution_profiles.idle_previous = 0;
  execution_profiles.idle_accumulated = 0;
  execution_profiles.idle_last = 0;
  iVar3 = 0;
  do {
    iVar2 = iVar3 + 1;
    execution_profiles.start[iVar3] = 0;
    iVar1 = iVar3 + -5;
    iVar3 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  iVar3 = 0;
  do {
    iVar2 = iVar3 + 1;
    execution_profiles.child_ticks[iVar3] = 0;
    iVar1 = iVar3 + -5;
    iVar3 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  iVar3 = 0;
  do {
    iVar2 = iVar3 + 1;
    execution_profiles.ch0_inclusive[iVar3] = 0;
    iVar1 = iVar3 + -7;
    iVar3 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  iVar3 = 0;
  do {
    iVar2 = iVar3 + 1;
    execution_profiles.ch1_exclusive[iVar3] = 0;
    iVar1 = iVar3 + -7;
    iVar3 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  iVar3 = 0;
  do {
    iVar2 = iVar3 + 1;
    execution_profiles.ch1_inclusive[iVar3] = 0;
    iVar1 = iVar3 + -7;
    iVar3 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  execution_profiles.active = '\x06';
  execution_profiles.ring_heads[0] = '\0';
  execution_profiles.ring_heads[1] = '\0';
  execution_profiles.ring_heads[2] = '\0';
  execution_profiles.ring_heads[3] = '\0';
  iVar3 = 0;
  do {
    iVar2 = iVar3 + 1;
    execution_profiles.parent[iVar3] = '\x06';
    iVar1 = iVar3 + -6;
    iVar3 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  return;
}

uint read_inverted_profile_counter(void)

{
  uint uVar1;
  
  uVar1 = DAT_ffe51010;
  return ~uVar1;
}

void begin_execution_profile(uchar slot,int entry_adjust)

{
  uint uVar1;
  uint uVar2;
  uint uVar3;
  
  uVar3 = (uint)slot;
  uVar1 = DAT_ffe51010;
  uVar1 = ~uVar1 - entry_adjust;
  execution_profiles.parent[uVar3] = execution_profiles.active;
  if (execution_profiles.active == '\x06') {
    uVar1 = uVar1 + 7;
    uVar2 = execution_profiles.idle_accumulated + (uVar1 - execution_profiles.idle_previous)
    ;
    execution_profiles.idle_accumulated = uVar2;
    if (uVar3 == 5) {
      if ((execution_profile_peak_hold == 'Z') && (execution_profiles.idle_last < uVar2)) {
        uVar2 = execution_profiles.idle_last;
      }
      execution_profiles.idle_accumulated = 0;
      execution_profiles.idle_last = uVar2;
    }
  }
  execution_profiles.active = slot;
  execution_profiles.start[uVar3] = uVar1;
  execution_profiles.child_ticks[uVar3] = 0;
  return;
}

void begin_execution_profile_slot0(void)

{
  begin_execution_profile('\0',0x69);
  return;
}

void begin_execution_profile_slot2(void)

{
  uint saved_mask;
  
  saved_mask = priority_mask_enter(0xffc0);
  begin_execution_profile('\x02',0x76);
  priority_mask_restore(saved_mask);
  return;
}

void begin_execution_profile_slot3(void)

{
  uint saved_mask;
  
  saved_mask = priority_mask_enter(0xffc0);
  begin_execution_profile('\x03',0x78);
  priority_mask_restore(saved_mask);
  return;
}

void begin_execution_profile_slot4(void)

{
  uint saved_mask;
  
  saved_mask = priority_mask_enter(0xffc0);
  begin_execution_profile('\x04',0x3b);
  priority_mask_restore(saved_mask);
  return;
}

void begin_execution_profile_slot5(void)

{
  uint saved_mask;
  
  saved_mask = priority_mask_enter(0xffc0);
  begin_execution_profile('\x05',0x1f);
  priority_mask_restore(saved_mask);
  return;
}

uint end_execution_profile(uchar slot,int exit_adjust,uint parent_adjust)

{
  uint uVar1;
  uint uVar2;
  uint uVar3;
  
  execution_profiles.active = execution_profiles.parent[slot];
  uVar3 = (uint)execution_profiles.active;
  uVar2 = DAT_ffe51010;
  uVar1 = (~uVar2 - exit_adjust) - execution_profiles.start[slot];
  uVar2 = ~uVar2 - exit_adjust;
  if (uVar3 != 6) {
    execution_profiles.child_ticks[uVar3] =
         execution_profiles.child_ticks[uVar3] + parent_adjust + uVar1;
    uVar2 = execution_profiles.idle_previous;
  }
  execution_profiles.idle_previous = uVar2;
  return uVar1;
}

void end_execution_profile_slot0(void)

{
  uchar uVar1;
  uint uVar2;
  uint32_t puVar3;
  uint uVar4;
  uint uVar5;
  
  puVar3 = 0xfebeb800u;
  uVar4 = end_execution_profile('\0',-0x13,0x51);
  uVar1 = execution_profile_peak_hold;
  uVar4 = uVar4 & 0xffff;
  uVar2 = (byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x2a5c))))) + 1 & 7;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x2a5c))))) = (byte)uVar2;
  if ((uVar1 == 'Z') &&
     (uVar5 = (uint)execution_profiles.ch0_inclusive[uVar2],
     -1 < (int)(uVar5 - uVar4) && uVar5 != uVar4)) {
    uVar4 = uVar5;
  }
  execution_profiles.ch0_inclusive[uVar2] = (ushort)uVar4;
  return;
}

void end_execution_profile_slot2(void)

{
  int iVar1;
  ushort uVar2;
  uchar uVar3;
  uint32_t puVar4;
  uint32_t puVar5;
  uint uVar6;
  uint uVar7;
  ushort uVar8;
  int iVar9;
  
  puVar4 = 0xfebeb800u;
  uVar6 = priority_mask_enter(0xffc0);
  uVar7 = end_execution_profile('\x02',4,0x75);
  iVar9 = (*((int *)camry_host_ptr((uint32_t)(puVar4 + -0x2a9c))));
  puVar5 = ((uint32_t)(puVar4));
  priority_mask_restore(uVar6);
  uVar3 = execution_profile_peak_hold;
  uVar6 = (byte)(*((volatile undefined *)camry_host_ptr((uint32_t)(0xfebeb800u + (uint32_t)(-0x2a5b) * 1u)))) + 1 & 7;
  (*((volatile undefined *)camry_host_ptr((uint32_t)(0xfebeb800u + (uint32_t)(-0x2a5b) * 1u)))) = (byte)uVar6;
  iVar1 = uVar6 * 2;
  uVar6 = uVar7 & 0xffff;
  uVar8 = (ushort)(uVar7 - iVar9);
  if (uVar3 == 'Z') {
    uVar7 = uVar7 - iVar9 & 0xffff;
    uVar2 = (*((ushort *)camry_host_ptr((uint32_t)(puVar4 + iVar1 + -0x2a7c))));
    if (-1 < (int)(uVar2 - uVar7) && uVar2 != uVar7) {
      uVar8 = uVar2;
    }
    (*((ushort *)camry_host_ptr((uint32_t)(puVar4 + iVar1 + -0x2a7c)))) = uVar8;
    uVar7 = (uint)(*((ushort *)camry_host_ptr((uint32_t)(puVar4 + iVar1 + -0x2a6c))));
    if (-1 < (int)(uVar7 - uVar6) && uVar7 != uVar6) {
      uVar6 = uVar7;
    }
  }
  else {
    (*((ushort *)camry_host_ptr((uint32_t)(puVar4 + iVar1 + -0x2a7c)))) = uVar8;
  }
  (*((short *)camry_host_ptr((uint32_t)(puVar4 + iVar1 + -0x2a6c)))) = (short)uVar6;
  return;
}
