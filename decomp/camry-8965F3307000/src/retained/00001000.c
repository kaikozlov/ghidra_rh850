#include "common.h"

void spin_forever_10c4(void)

{
  do {
                    /* WARNING: Do nothing block with infinite loop */
  } while( true );
}

void select_clock3_and_set_divider_80_10c6(void)

{
  camry_write32((camry_sp - 4u) & ~3u, camry_gpr[31]);
  camry_sp -= 4u;
  camry_gpr[3] = camry_sp;

  byte bVar1;
  uint uVar2;
  
  CLKD3DIV = 0;
  CKSC3C = 4;
  uVar2 = CKSC3C;
  __synchronize();
  uVar2 = CKSC3S;
  bVar1 = 0;
  while ((uVar2 != 4 && (bVar1 < 100))) {
    uVar2 = CKSC3S;
    bVar1 = bVar1 + 1;
    __synchronize();
  }
  uVar2 = CLKD3STAT;
  bVar1 = 0;
  while (((uVar2 & 2) == 0 && (bVar1 < 100))) {
    bVar1 = bVar1 + 1;
    __synchronize();
    uVar2 = CLKD3STAT;
  }
  if ((uVar2 & 2) == 2) {
    CLKD3DIV = 0x50;
    uVar2 = CLKD3DIV;
    __synchronize();
  }
  else {
    (camry_gpr[31] = 0x1136u, spin_forever_10c4)();
  }
  uVar2 = CLKD3STAT;
  bVar1 = 0;
  while (((uVar2 >> 1 & 1) == 0 && (bVar1 < 100))) {
    bVar1 = bVar1 + 1;
    __synchronize();
    uVar2 = CLKD3STAT;
  }
  { if (!camry_halted) { camry_gpr[31] = camry_read32((camry_sp + 0u) & ~3u); camry_sp += 4u; camry_gpr[3] = camry_sp; } return; }
}

undefined4 check_ucfd_error_bits_and_clear_ecm_bit19_115a(void)

{
  uint uVar1;
  uint uVar2;
  uchar uVar3;
  undefined4 uVar4;
  
  uVar2 = UCFDERSTR;
  camry_write32(0xffc62008u, 1);
  uVar4 = 0;
  uVar1 = camry_read32(0xffc62008u);
  __synchronize();
  ECMPCMD1 = 0xa5;
  ECMESSTC0 = 0x80000;
  ECMESSTC0 = 0xfff7ffff;
  ECMESSTC0 = 0x80000;
  uVar3 = ECMPS;
  __synchronize();
  if (((uVar2 & 1) != 0) || ((uVar2 >> 2 & 1) != 0)) {
    uVar4 = 1;
  }
  return uVar4;
}

uint boot_validate_application_images(void)

{
  bool bVar1;
  uint uVar2;
  uint uVar3;
  int iVar4;
  int iVar5;
  uint uVar6;
  
  uVar6 = 0;
  while( true ) {
    uVar2 = boot_validate_crc_region(1);
    uVar3 = boot_validate_crc_region(0);
    if ((uVar2 == 0) && (uVar3 == 0)) {
      bVar1 = false;
    }
    else {
      bVar1 = true;
    }
    iVar4 = check_ucfd_error_bits_and_clear_ecm_bit19_115a();
    if ((!bVar1) && (iVar4 == 0)) break;
    uVar6 = uVar6 + 1;
    if (2 < uVar6) {
      return 1;
    }
  }
  uVar6 = 0;
  while( true ) {
    iVar4 = is_completion_marker_word_mismatched_6c5a(((int *)camry_host_ptr((uint32_t)(0xffe00))));
    iVar5 = is_completion_marker_word_mismatched_6c5a(((undefined *)camry_host_ptr(0x17e00u)));
    if ((iVar4 == 0) && (iVar5 == 0)) break;
    uVar6 = uVar6 + 1;
    if (2 < uVar6) {
      return 1;
    }
  }
  return 0;
}

void clear_fffee980_register_block_1206(void)

{
  undefined2 uVar1;
  
  Ramfffee982 = 0;
  Ramfffee988 = 0;
  Ramfffee980 = 0;
  uVar1 = Ramfffee980;
  __synchronize();
  __synchronize();
  return;
}

void set_ffff8000_one_and_synchronize_121a(void)

{
  undefined4 uVar1;
  
  Ramffff8000 = 1;
  uVar1 = Ramffff8000;
  __synchronize();
  return;
}

void configure_ecm_masks_and_clear_status_1228(void)

{
  uchar uVar1;
  uint uVar2;
  
  ECMPEM = 3;
  uVar2 = ECMPEM;
  __synchronize();
  ECMPCMD1 = 0xa5;
  ECMEMK0 = 0xffffffe1;
  ECMEMK0 = 0x1e;
  ECMEMK0 = 0xffffffe1;
  uVar1 = ECMPS;
  ECMPCMD1 = 0xa5;
  ECMEMK1 = 0xffffffff;
  ECMEMK1 = 0;
  ECMEMK1 = 0xffffffff;
  uVar1 = ECMPS;
  ECMPCMD1 = 0xa5;
  ECMEMK2 = 0x3fffffff;
  ECMEMK2 = 0xc0000000;
  ECMEMK2 = 0x3fffffff;
  uVar1 = ECMPS;
  ECMPCMD1 = 0xa5;
  ECMMICFG0 = 0;
  ECMMICFG0 = 0xffffffff;
  ECMMICFG0 = 0;
  uVar1 = ECMPS;
  ECMPCMD1 = 0xa5;
  ECMMICFG1 = 0;
  ECMMICFG1 = 0xffffffff;
  ECMMICFG1 = 0;
  uVar1 = ECMPS;
  ECMPCMD1 = 0xa5;
  ECMMICFG2 = 0;
  ECMMICFG2 = 0xffffffff;
  ECMMICFG2 = 0;
  uVar1 = ECMPS;
  ECMPCMD1 = 0xa5;
  ECMNMICFG0 = 0;
  ECMNMICFG0 = 0xffffffff;
  ECMNMICFG0 = 0;
  uVar1 = ECMPS;
  ECMPCMD1 = 0xa5;
  ECMNMICFG1 = 0;
  ECMNMICFG1 = 0xffffffff;
  ECMNMICFG1 = 0;
  uVar1 = ECMPS;
  ECMPCMD1 = 0xa5;
  ECMNMICFG2 = 0;
  ECMNMICFG2 = 0xffffffff;
  ECMNMICFG2 = 0;
  uVar1 = ECMPS;
  ECMPCMD1 = 0xa5;
  ECMIRCFG0 = 0;
  ECMIRCFG0 = 0xffffffff;
  ECMIRCFG0 = 0;
  uVar1 = ECMPS;
  ECMPCMD1 = 0xa5;
  ECMIRCFG1 = 0;
  ECMIRCFG1 = 0xffffffff;
  ECMIRCFG1 = 0;
  uVar1 = ECMPS;
  ECMPCMD1 = 0xa5;
  ECMIRCFG2 = 0;
  ECMIRCFG2 = 0xffffffff;
  ECMIRCFG2 = 0;
  uVar1 = ECMPS;
  ECMPEM = 0;
  uVar2 = ECMPEM;
  __synchronize();
  ECMPCMD1 = 0xa5;
  ECMESSTC0 = 0xffffffff;
  ECMESSTC0 = 0;
  ECMESSTC0 = 0xffffffff;
  uVar1 = ECMPS;
  ECMPCMD1 = 0xa5;
  ECMESSTC1 = 0xffffffff;
  ECMESSTC1 = 0;
  ECMESSTC1 = 0xffffffff;
  uVar1 = ECMPS;
  ECMPCMD1 = 0xa5;
  ECMESSTC2 = 0x7fffffff;
  ECMESSTC2 = 0x80000000;
  ECMESSTC2 = 0x7fffffff;
  uVar1 = ECMPS;
  __synchronize();
  return;
}

void boot_resident_initialize(void)

{
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)((camry_gp + 0xffff9104u))))) = 1;
  (*((volatile uint32_t *)camry_host_ptr((uint32_t)((camry_gp + 0xffff9100u))))) = 0;
  configure_ffd82_ffd83_exchange_and_check_reply_16f2();
  set_ffff8000_one_and_synchronize_121a();
  configure_ecm_masks_and_clear_status_1228();
  initialize_interrupt_control_halfwords_17c8();
  initialize_configured_channels_buffers_and_filter_routes_3b3c();
  clear_driver_state_and_wait_for_ffa10000_ready_35bc();
  boot_reset_flash_operation_queue();
  fill_constant_block_1f24();
  set_result_2aa2_two_and_clear_flag_2aa3_47ac();
  boot_reset_region_crc_verification();
  initialize_timer_banks_and_start_tauj0_channel2_1ca0();
  enable_and_initialize_boot_diagnostics_770();
  return;
}

void boot_resident_service_iteration(void)

{
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)((camry_gp + 0xffff9104u))))) = 2;
  run_boot_diagnostic_foreground_78c();
  boot_advance_flash_operation();
  clear_result_2aa2_if_flag_2aa3_set_479a();
  boot_advance_region_crc_verification();
  return;
}

void boot_resident_main(void)

{
  uint uVar1;
  uint uVar2;
  uint in_FPEC = camry_SR[0][11];
  uint in_RBASE = camry_SR[1][2];
  uint in_EBASE = camry_SR[1][3];
  uint in_FPIPR = camry_SR[1][7];
  uint in_ISPR = camry_SR[2][10];
  
  boot_resident_initialize();
  restore_pmr_preserving_interrupt_disable_state_7244(0);
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
      if (((camry_psw & 0xbfffffdf) >> 0xf & 1) == 0) {
        in_EBASE = in_RBASE;
      }
      (*(int (*)())camry_indirect((uint32_t)((in_EBASE & 0xfffffe00) + 0x70)))();
    }
  }
  __enable_irq();
  do {
    boot_resident_service_iteration();
  } while( true );
}

void boot_select_application_or_resident(void)

{
  camry_write32((camry_sp - 4u) & ~3u, camry_gpr[29]);
  camry_write32((camry_sp - 8u) & ~3u, camry_gpr[31]);
  camry_sp -= 12u;
  camry_gpr[3] = camry_sp;

  int iVar1;
  int iVar2;
  int iVar3;
  uint32_t puVar4;
  uint uVar5;
  
  puVar4 = (camry_gp + 0x0u);
  (camry_gpr[31] = 0x13b8u, load_tp_configuration_into_ffc1_ffc2_ffc3_banks_c9a)();
  (camry_gpr[31] = 0x13bcu, snapshot_validated_ecm_status_and_clear_errors_e54)();
  (camry_gpr[31] = 0x13c0u, configure_ecm_masks_and_clear_error_outputs_f80)();
  (camry_gpr[31] = 0x13c4u, select_clock3_and_set_divider_80_10c6)();
  uVar5 = (camry_gpr[31] = 0x13c8u, boot_validate_application_images)();
  if (uVar5 == 0) {
    (*(int (*)())camry_indirect((uint32_t)(PTR_application_entry_000ffdb8)))();
  }
  else {
    (camry_gpr[31] = 0x13d0u, clear_fffee980_register_block_1206)();
    (*((undefined4 *)camry_host_ptr((uint32_t)(puVar4 + -0x6ef8)))) = 0xff;
    iVar3 = 1;
    do {
      (*((undefined4 *)camry_host_ptr((uint32_t)(puVar4 + iVar3 * 4 + -0x6ef8)))) = 0xffffffff;
      iVar2 = iVar3 + 1;
      iVar1 = iVar3 + -8;
      iVar3 = iVar2;
    } while (((iVar1 < 0) || (iVar2 < 0)));
    (camry_gpr[31] = 0x13f0u, boot_resident_main)();
  }
  do {
                    /* WARNING: Do nothing block with infinite loop */
  } while( true );
}

void boot_hardware_ram_init_and_select_image(void)

{
  camry_write32((camry_sp - 4u) & ~3u, camry_gpr[31]);
  camry_sp -= 4u;
  camry_gpr[3] = camry_sp;

  uint32_t puVar1;
  
  (camry_gpr[31] = 0x140cu, initialize_ffc604_and_ffc614_register_pairs_79a)();
  (camry_gpr[31] = 0x1410u, configure_ffc654_registers_and_poll_7b6)();
  (camry_gpr[31] = 0x1414u, initialize_codeflash_ecc_controls_and_poll_802)();
  (camry_gpr[31] = 0x1418u, configure_ffc5b0_registers_and_poll_zero_880)();
  (camry_gpr[31] = 0x141cu, configure_ffc640_registers_and_poll_8c8)();
  (camry_gpr[31] = 0x1420u, configure_and_poll_multiple_register_banks_96e)();
  (camry_gpr[31] = 0x1424u, initialize_six_610_8000_register_pairs_c52)();
  __synchronize();
  for (puVar1 = 0xfebf7c00u; puVar1 < 0xfebe7000u; puVar1 += 4u) {
    camry_write32(puVar1, 0);
  }
  for (puVar1 = 0xfebe8000u; puVar1 < 0xfec00000u; puVar1 += 4u)
  {
    camry_write32(puVar1, 0);
  }
  for (puVar1 = 0xfeef8000u; puVar1 < 0xfef08000u; puVar1 += 4u) {
    camry_write32(puVar1, 0);
  }
  camry_write8(0xffc59810u, '\x03');
  (camry_gpr[31] = 0x1474u, boot_select_application_or_resident)();
  { if (!camry_halted) { camry_gpr[31] = camry_read32((camry_sp + 0u) & ~3u); camry_sp += 4u; camry_gpr[3] = camry_sp; } return; }
}

void copy_positive_count_words_forward_1478(undefined4 *param_1,undefined4 *param_2,int param_3)

{
  undefined4 uVar1;
  
  if (0 < param_3) {
    do {
      uVar1 = *param_1;
      param_1 = param_1 + 1;
      *param_2 = uVar1;
      param_2 = param_2 + 1;
      param_3 = param_3 + -1;
    } while (param_3 != 0);
  }
  return;
}

void boot_resident_enter_with_record(uint *handoff_record)

{
  camry_write32((camry_sp - 4u) & ~3u, camry_gpr[31]);
  camry_sp -= 4u;
  camry_gpr[3] = camry_sp;
  camry_gpr[31] = 0x149cu;
  copy_positive_count_words_forward_1478(handoff_record, ((undefined4 *)camry_host_ptr((uint32_t)(((camry_gp + 0xffff9108u))))), 9);
  camry_gpr[31] = 0x14a0u;
  boot_resident_main();
  do {
                    /* WARNING: Do nothing block with infinite loop */
  } while( true );
}

void service_three_callbacks_when_state_two_14a2(void)

{
  if ((*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff9104u)))) == '\x02') {
    dispatch_expired_armed_timer_slots_1d9a();
    service_boot_diagnostic_timers_780();
    service_pending_transport_capacity_states_2250();
  }
  return;
}

undefined4 set_gp_event_mask_bit_guarded_14be(uint param_1)

{
  uint32_t puVar1;
  undefined4 uVar2;
  
  puVar1 = (camry_gp + 0x0u);
  uVar2 = raise_pmr_and_return_previous_mask_721e(0xffff);
  (*((uint *)camry_host_ptr((uint32_t)(puVar1 + -0x6f00)))) = (*((uint *)camry_host_ptr((uint32_t)(puVar1 + -0x6f00)))) | 1 << (param_1 & 0x1f);
  restore_pmr_preserving_interrupt_disable_state_7244(uVar2);
  return uVar2;
}

undefined4 clear_gp_event_mask_bit_guarded_14e8(uint param_1)

{
  uint32_t puVar1;
  undefined4 uVar2;
  
  puVar1 = (camry_gp + 0x0u);
  uVar2 = raise_pmr_and_return_previous_mask_721e(0xffff);
  (*((uint *)camry_host_ptr((uint32_t)(puVar1 + -0x6f00)))) = (*((uint *)camry_host_ptr((uint32_t)(puVar1 + -0x6f00)))) & ~(1 << (param_1 & 0x1f));
  restore_pmr_preserving_interrupt_disable_state_7244(uVar2);
  return uVar2;
}

void copy_gp_words_to_destination_u8_count_1514(undefined4 param_1,undefined1 param_2)

{
  copy_positive_count_words_forward_1478(((undefined4 *)camry_host_ptr((uint32_t)(((camry_gp + 0xffff9108u))))), ((undefined4 *)camry_host_ptr((uint32_t)(param_1))), param_2);
  return;
}

void prepare_and_run_relocated_flash_driver_152a(void)

{
  copy_flash_driver_disable_cache_and_call_ram_entry_36be();
  return_only_stub_798();
  return;
}

void copy_positive_count_bytes_forward_153a(undefined1 *param_1,undefined1 *param_2,int param_3)

{
  undefined1 uVar1;
  
  if (0 < param_3) {
    do {
      uVar1 = *param_1;
      param_1 = param_1 + 1;
      *param_2 = uVar1;
      param_2 = param_2 + 1;
      param_3 = param_3 + -1;
    } while (param_3 != 0);
  }
  return;
}

void set_gp_execution_state_three_1550(void)

{
  (*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff9104u)))) = 3;
  return;
}

void disable_interrupts_stop_clock3_clear_bits_and_spin_1560(void)

{
  ushort uVar1;
  uint uVar2;
  
  __disable_irq();
  uVar2 = CLKD3STAT;
  if ((uVar2 & 2) == 2) {
    CLKD3DIV = 0;
    uVar2 = CLKD3DIV;
    __synchronize();
  }
  uVar1 = Ramffc10100;
  Ramffc10100 = uVar1 & 0xffdf;
  uVar1 = Ramffc10114;
  Ramffc10114 = uVar1 & 0xffdf;
  uVar1 = Ramffc10110;
  Ramffc10110 = uVar1 & 0xffdf;
  do {
                    /* WARNING: Do nothing block with infinite loop */
  } while( true );
}

void set_state_three_and_enter_stop_loop_159e(void)

{
  raise_pmr_and_return_previous_mask_721e(0xffff);
  set_gp_execution_state_three_1550();
  disable_interrupts_stop_clock3_clear_bits_and_spin_1560();
  do {
                    /* WARNING: Do nothing block with infinite loop */
  } while( true );
}

void store_ffd50020_byte_22_15b4(void)

{
  DAT_ffd50020 = 0x22;
  return;
}

uint feed_seven_big_endian_bytes_and_read_inverted_check_15c0(ushort *param_1)

{
  uint uVar1;
  
  DAT_ffd50020 = 0x22;
  Ramffd50004 = 0xff;
  Ramffd50000 = (uint)(*param_1 >> 8);
  Ramffd50000 = *param_1 & 0xff;
  Ramffd50000 = (uint)(param_1[1] >> 8);
  Ramffd50000 = param_1[1] & 0xff;
  Ramffd50000 = (uint)(param_1[2] >> 8);
  Ramffd50000 = param_1[2] & 0xff;
  Ramffd50000 = (uint)(param_1[3] >> 8);
  uVar1 = Ramffd50004;
  return (uVar1 ^ 0xff) & 0xff;
}

undefined4 submit_four_halfwords_to_ffd83008_1626(ushort *param_1)

{
  uint uVar1;
  
  uVar1 = Ramffd82004;
  if ((uVar1 & 0x80) == 0) {
    Ramffd83018 = 0;
    Ramffd83008 = *param_1 | 0x20fe0000;
    Ramffd83008 = param_1[1] | 0x20fe0000;
    Ramffd83008 = param_1[2] | 0x20fe0000;
    Ramffd83008 = param_1[3] | 0xfe0000;
    Ramffd83004 = 0x80040000;
    return 0;
  }
  return 0x5aa5;
}

undefined4 insert_seven_byte_check_and_submit_halfwords_167c(int param_1)

{
  ushort uVar1;
  
  uVar1 = feed_seven_big_endian_bytes_and_read_inverted_check_15c0(((ushort *)camry_host_ptr((uint32_t)(param_1))));
  (*((ushort *)camry_host_ptr((uint32_t)(param_1 + 6)))) = (*((ushort *)camry_host_ptr((uint32_t)(param_1 + 6)))) & 0xff00 | uVar1;
  return submit_four_halfwords_to_ffd83008_1626(((ushort *)camry_host_ptr((uint32_t)(param_1))));
}

undefined * read_four_ffd83014_halfwords_if_ready_169c(undefined2 *param_1)

{
  uint uVar1;
  undefined2 uVar2;
  
  uVar1 = Ramffd82004;
  if (((uVar1 >> 7 & 1) == 0) && (uVar1 = Ramffd83004, (uVar1 & 0x7f) == 4)) {
    uVar1 = Ramffd83018;
    if (((int)uVar1 & 0x7fffff) >> 0x10 != 0) {
      return ((undefined *)camry_host_ptr(0xa55au));
    }
    uVar2 = Ramffd83014;
    *param_1 = uVar2;
    uVar2 = Ramffd83014;
    param_1[1] = uVar2;
    uVar2 = Ramffd83014;
    param_1[2] = uVar2;
    uVar2 = Ramffd83014;
    param_1[3] = uVar2;
    return (undefined *)0x0;
  }
  return ((undefined *)camry_host_ptr((uint32_t)(0x5aa5)));
}

uint configure_ffd82_ffd83_exchange_and_check_reply_16f2(void)

{
  undefined1 uVar1;
  int iVar2;
  uint uVar3;
  byte bVar4;
  ushort header[4];
  ushort record[4];
  
  header[0] = 0;
  header[1] = 0;
  bVar4 = 0;
  header[2] = 0;
  header[3] = 0;
  DAT_ffd82000 = 0;
  uVar1 = DAT_ffd82000;
  __synchronize();
  Ramffd82010 = 0x90;
  Ramffd82014 = 0;
  Ramffd83040 = 0x100;
  Ramffd83018 = 0;
  Ramffd83044 = 0xe000;
  Ramffd83048 = 0x8e000;
  Ramffd8304c = 0x8e000;
  Ramffd83050 = 0x8e000;
  Ramffd83054 = 0x8e000;
  Ramffd83058 = 0x8e000;
  Ramffd8305c = 0x8e000;
  Ramffd83060 = 0x8e000;
  Ramffd83068 = 0x14;
  Ramffd8306c = 0x14;
  Ramffd83070 = 0x14;
  Ramffd83074 = 0x14;
  Ramffd82008 = 0xc10b;
  DAT_ffd82000 = 0xe0;
  store_ffd50020_byte_22_15b4();
  busy_wait_155_decrements_per_unit_7208(0x50);
  record[0] = 0x8c00;
  record[1] = 0;
  record[2] = 0xf000;
  record[3] = 0x1f00;
  insert_seven_byte_check_and_submit_halfwords_167c(camry_host_addr(record));
  busy_wait_155_decrements_per_unit_7208(0x50);
  insert_seven_byte_check_and_submit_halfwords_167c(camry_host_addr(record));
  busy_wait_155_decrements_per_unit_7208(0x50);
  do {
    iVar2 = camry_host_addr(read_four_ffd83014_halfwords_if_ready_169c(header));
    busy_wait_155_decrements_per_unit_7208(1);
    bVar4 = bVar4 + 1;
    if (iVar2 == 0) break;
  } while (bVar4 < 0xc9);
  uVar3 = feed_seven_big_endian_bytes_and_read_inverted_check_15c0(header);
  if ((byte)header[3] != uVar3) {
    do {
                    /* WARNING: Do nothing block with infinite loop */
    } while( true );
  }
  return uVar3;
}

void initialize_interrupt_control_halfwords_17c8(void)

{
  EIC8 = (uint16_t)0x8f;
  DAT_fffeea12 = 0x8f;
  DAT_fffeea20 = 0x8f;
  DAT_fffeea22 = 0x8f;
  DAT_fffeea24 = 0x8f;
  DAT_fffeea26 = 0x8f;
  DAT_fffeea28 = 0x8f;
  DAT_fffeea2a = 0x8f;
  DAT_fffeea2c = 0x8f;
  DAT_fffeea2e = 0x8f;
  DAT_fffeea30 = 0x8f;
  DAT_fffeea32 = 0x8f;
  DAT_fffeea34 = 0x8f;
  DAT_fffeea36 = 0x8f;
  DAT_fffeea38 = 0x8f;
  DAT_fffeea3a = 0x8f;
  DAT_fffeea3c = 0x8f;
  DAT_fffeea3e = 0x8f;
  DAT_ffffb040 = 0x8f;
  DAT_ffffb042 = 0x8f;
  DAT_ffffb044 = 0x8f;
  DAT_ffffb046 = 0x8f;
  DAT_ffffb048 = 0x8f;
  DAT_ffffb050 = 0x8f;
  DAT_ffffb052 = 0x8f;
  DAT_ffffb054 = 0x8f;
  DAT_ffffb056 = 0x8f;
  DAT_ffffb058 = 0x8f;
  DAT_ffffb05a = 0x8f;
  DAT_ffffb05c = 0x8f;
  DAT_ffffb05e = 0x8f;
  DAT_ffffb060 = 0x8f;
  DAT_ffffb062 = 0x8f;
  DAT_ffffb064 = 0x8f;
  DAT_ffffb066 = 0x8f;
  DAT_ffffb068 = 0x8f;
  DAT_ffffb06a = 0x8f;
  DAT_ffffb06c = 0x8f;
  DAT_ffffb06e = 0x8f;
  DAT_ffffb070 = 0x8f;
  DAT_ffffb072 = 0x8f;
  DAT_ffffb074 = 0x8f;
  DAT_ffffb076 = 0x8f;
  DAT_ffffb078 = 0x8f;
  DAT_ffffb07a = 0x8f;
  DAT_ffffb07c = 0x8f;
  DAT_ffffb07e = 0x8f;
  DAT_ffffb080 = 0x8f;
  DAT_ffffb082 = 0x8f;
  DAT_ffffb084 = 0x8f;
  DAT_ffffb086 = 0x8f;
  DAT_ffffb088 = 0x8f;
  DAT_ffffb08a = 0x8f;
  DAT_ffffb08c = 0x8f;
  DAT_ffffb08e = 0x8f;
  DAT_ffffb090 = 0x8f;
  DAT_ffffb092 = 0x8f;
  DAT_ffffb094 = 0x8f;
  DAT_ffffb096 = 0x8f;
  DAT_ffffb098 = 0x8f;
  DAT_ffffb09a = 0x8f;
  DAT_ffffb09c = 0x8f;
  DAT_ffffb09e = 0x8f;
  DAT_ffffb0a0 = 0x8f;
  DAT_ffffb0a2 = 0x8f;
  DAT_ffffb0a4 = 0x8f;
  DAT_ffffb0a6 = 0x8f;
  DAT_ffffb0a8 = 0x8f;
  DAT_ffffb0aa = 0x8f;
  DAT_ffffb0ac = 0x8f;
  DAT_ffffb0ae = 0x8f;
  DAT_ffffb0b0 = 0x8f;
  DAT_ffffb0b2 = 0x8f;
  DAT_ffffb0b4 = 0x8f;
  DAT_ffffb0b6 = 0x8f;
  DAT_ffffb0b8 = 0x8f;
  DAT_ffffb0ba = 0x8f;
  DAT_ffffb0bc = 0x8f;
  DAT_ffffb0be = 0x8f;
  DAT_ffffb0c0 = 0x8f;
  DAT_ffffb0c2 = 0x8f;
  DAT_ffffb0c4 = 0x8f;
  DAT_ffffb0c6 = 0x8f;
  DAT_ffffb0c8 = 0x8f;
  DAT_ffffb0ca = 0x8f;
  DAT_ffffb0cc = 0x8f;
  DAT_ffffb0ce = 0x8f;
  DAT_ffffb0d0 = 0x8f;
  DAT_ffffb0d2 = 0x8f;
  DAT_ffffb0d4 = 0x808f;
  DAT_ffffb0d6 = 0x8f;
  DAT_ffffb0d8 = 0x8f;
  DAT_ffffb0da = 0x808f;
  DAT_ffffb0dc = 0x808f;
  DAT_ffffb0de = 0x8f;
  DAT_ffffb0e0 = 0x8f;
  DAT_ffffb0e2 = 0x808f;
  DAT_ffffb0e4 = 0x8f;
  DAT_ffffb0e6 = 0x8f;
  DAT_ffffb0e8 = 0x8f;
  DAT_ffffb0ea = 0x8f;
  DAT_ffffb0ec = 0x8f;
  DAT_ffffb0ee = 0x8f;
  DAT_ffffb0f0 = 0x808f;
  DAT_ffffb0f2 = 0x808f;
  DAT_ffffb100 = 0x8f;
  DAT_ffffb102 = 0x8f;
  DAT_ffffb104 = 0x8f;
  DAT_ffffb106 = 0x8f;
  DAT_ffffb108 = 0x8f;
  EIC133 = (uint16_t)0x8f;
  EIC134 = (uint16_t)0x8f;
  EIC135 = (uint16_t)0x9;
  EIC136 = (uint16_t)0x8f;
  DAT_ffffb112 = 0x8f;
  DAT_ffffb114 = 0x8f;
  DAT_ffffb116 = 0x8f;
  DAT_ffffb118 = 0x8f;
  DAT_ffffb11a = 0x8f;
  DAT_ffffb11c = 0x8f;
  DAT_ffffb11e = 0x8f;
  DAT_ffffb120 = 0x8f;
  DAT_ffffb122 = 0x8f;
  DAT_ffffb124 = 0x8f;
  DAT_ffffb126 = 0x8f;
  DAT_ffffb128 = 0x8f;
  DAT_ffffb12a = 0x8f;
  DAT_ffffb12c = 0x8f;
  DAT_ffffb12e = 0x8f;
  DAT_ffffb130 = 0x8f;
  DAT_ffffb132 = 0x8f;
  DAT_ffffb134 = 0x8f;
  DAT_ffffb136 = 0x8f;
  DAT_ffffb138 = 0x8f;
  DAT_ffffb13c = 0x8f;
  DAT_ffffb13e = 0x8f;
  DAT_ffffb140 = 0x8f;
  DAT_ffffb142 = 0x8f;
  DAT_ffffb144 = 0x8f;
  DAT_ffffb146 = 0x8f;
  DAT_ffffb148 = 0x8f;
  DAT_ffffb14a = 0x8f;
  DAT_ffffb14c = 0x8f;
  DAT_ffffb14e = 0x8f;
  DAT_ffffb150 = 0x8f;
  DAT_ffffb152 = 0x8f;
  DAT_ffffb154 = 0x8f;
  DAT_ffffb156 = 0x8f;
  DAT_ffffb158 = 0x8f;
  DAT_ffffb15a = 0x8f;
  DAT_ffffb15c = 0x8f;
  DAT_ffffb15e = 0x8f;
  DAT_ffffb160 = 0x8f;
  DAT_ffffb162 = 0x8f;
  DAT_ffffb164 = 0x8f;
  DAT_ffffb166 = 0x8f;
  DAT_ffffb168 = 0x8f;
  DAT_ffffb16a = 0x8f;
  DAT_ffffb16c = 0x8f;
  DAT_ffffb16e = 0x808f;
  DAT_ffffb170 = 0x808f;
  DAT_ffffb172 = 0x808f;
  EIC187 = (uint16_t)0x8009;
  EIC188 = (uint16_t)0x8009;
  DAT_ffffb174 = 0x808f;
  DAT_ffffb17a = 0x808f;
  DAT_ffffb17c = 0x808f;
  DAT_ffffb17e = 0x808f;
  DAT_ffffb180 = 0x808f;
  DAT_ffffb182 = 0x808f;
  DAT_ffffb184 = 0x808f;
  DAT_ffffb186 = 0x808f;
  DAT_ffffb188 = 0x808f;
  DAT_ffffb18a = 0x808f;
  DAT_ffffb18c = 0x808f;
  DAT_ffffb18e = 0x808f;
  DAT_ffffb190 = 0x808f;
  DAT_ffffb192 = 0x808f;
  DAT_ffffb194 = 0x808f;
  DAT_ffffb196 = 0x808f;
  DAT_ffffb198 = 0x808f;
  DAT_ffffb1b4 = 0x808f;
  DAT_ffffb1b6 = 0x8f;
  DAT_ffffb1b8 = 0x8f;
  DAT_ffffb1ba = 0x808f;
  DAT_ffffb1c4 = 0x808f;
  DAT_ffffb1c6 = 0x808f;
  DAT_ffffb1c8 = 0x808f;
  DAT_ffffb1ca = 0x808f;
  DAT_ffffb1cc = 0x808f;
  DAT_ffffb1ce = 0x808f;
  DAT_ffffb1d0 = 0x808f;
  DAT_ffffb1d2 = 0x8f;
  DAT_ffffb1d4 = 0x808f;
  DAT_ffffb1d6 = 0x8f;
  DAT_ffffb1d8 = 0x808f;
  DAT_ffffb1da = 0x8f;
  DAT_ffffb1dc = 0x808f;
  DAT_ffffb1de = 0x8f;
  DAT_ffffb1e0 = 0x808f;
  DAT_ffffb1e2 = 0x8f;
  DAT_ffffb1e4 = 0x808f;
  DAT_ffffb1e6 = 0x8f;
  DAT_ffffb1e8 = 0x808f;
  DAT_ffffb1ea = 0x808f;
  DAT_ffffb1ec = 0x808f;
  DAT_ffffb1ee = 0x808f;
  DAT_ffffb1f0 = 0x808f;
  DAT_ffffb1f2 = 0x808f;
  DAT_ffffb1f4 = 0x808f;
  DAT_ffffb1f6 = 0x808f;
  DAT_ffffb1f8 = 0x808f;
  DAT_ffffb1fa = 0x808f;
  DAT_ffffb1fc = 0x808f;
  DAT_ffffb200 = 0x8f;
  DAT_ffffb202 = 0x8f;
  DAT_ffffb204 = 0x8f;
  DAT_ffffb206 = 0x8f;
  DAT_ffffb208 = 0x8f;
  DAT_ffffb20a = 0x8f;
  DAT_ffffb20c = 0x8f;
  DAT_ffffb20e = 0x8f;
  DAT_ffffb210 = 0x8f;
  DAT_ffffb212 = 0x8f;
  DAT_ffffb214 = 0x8f;
  DAT_ffffb216 = 0x8f;
  DAT_ffffb218 = 0x8f;
  DAT_ffffb21a = 0x8f;
  DAT_ffffb21c = 0x8f;
  DAT_ffffb21e = 0x8f;
  DAT_ffffb220 = 0x8f;
  DAT_ffffb222 = 0x8f;
  DAT_ffffb224 = 0x8f;
  DAT_ffffb226 = 0x8f;
  DAT_ffffb228 = 0x8f;
  DAT_ffffb22a = 0x8f;
  DAT_ffffb22c = 0x8f;
  DAT_ffffb22e = 0x8f;
  DAT_ffffb230 = 0x8f;
  DAT_ffffb232 = 0x8f;
  DAT_ffffb234 = 0x8f;
  DAT_ffffb236 = 0x8f;
  DAT_ffffb238 = 0x8f;
  DAT_ffffb23a = 0x8f;
  DAT_ffffb23c = 0x8f;
  DAT_ffffb23e = 0x8f;
  DAT_ffffb240 = 0x8f;
  DAT_ffffb242 = 0x8f;
  DAT_ffffb244 = 0x8f;
  DAT_ffffb246 = 0x8f;
  DAT_ffffb24c = 0x8f;
  DAT_ffffb24e = 0x8f;
  DAT_ffffb250 = 0x8f;
  DAT_ffffb252 = 0x8f;
  DAT_ffffb254 = 0x8f;
  EIC379 = (uint16_t)0x8f;
  DAT_ffffb2fe = 0x808f;
  return;
}

undefined4 set_selected_eic_mask_bit_guarded_1bbe(short param_1,char param_2)

{
  undefined4 uVar1;
  byte bVar2;
  EIC_Register *pEVar3;
  
  bVar2 = 0x80;
  if (param_2 == '\x01') {
    bVar2 = 0;
  }
  uVar1 = raise_pmr_and_return_previous_mask_721e(0xffff);
  if (param_1 == 0xb8) {
    pEVar3 = (EIC_Register *)((undefined *)camry_host_ptr(0xffffb170u));
  }
  else if (param_1 == 0xb9) {
    pEVar3 = (EIC_Register *)((undefined *)camry_host_ptr(0xffffb172u));
  }
  else if (param_1 == 0xbb) {
    pEVar3 = ((void *)camry_host_ptr((uint32_t)((0xffffb176u))));
  }
  else {
    if (param_1 != 0xbc) goto LAB_00001c16;
    pEVar3 = ((void *)camry_host_ptr((uint32_t)((0xffffb178u))));
  }
  (*((volatile uint8_t *)(pEVar3))) = ((*((volatile uint8_t *)(pEVar3))) & 0x7fu) | (uint8_t)(((uint32_t)(bVar2 >> 7) & 1u) << 7);
  __synchronize();
LAB_00001c16:
  restore_pmr_preserving_interrupt_disable_state_7244(uVar1);
  return uVar1;
}

void initialize_tauj0_with_channel2_period_79999_1c20(void)

{
  TAUJ0TT = '\x0f';
  TAUJ0TPS = 0xfff0;
  (*((volatile uint8_t *)camry_host_ptr(0xffe50094u))) = 0;
  TAUJ0CMUR0 = '\0';
  TAUJ0CMUR1 = '\0';
  TAUJ0CMUR2 = '\0';
  TAUJ0CMUR3 = '\0';
  TAUJ0CMOR0 = 0;
  TAUJ0CMOR1 = 0;
  TAUJ0CMOR2 = 0;
  TAUJ0CMOR3 = 0;
  TAUJ0CDR0 = 0;
  TAUJ0CDR1 = 0;
  TAUJ0CDR2 = 79999;
  TAUJ0CDR3 = 0;
  TAUJ0TOE = '\0';
  TAUJ0TO = '\0';
  TAUJ0RDE = '\0';
  TAUJ0RDM = '\0';
  return;
}

void fill_constant_block_1c60(void)

{
  DAT_ffe51058 = 0xf;
  DAT_ffe51090 = 0xfff2;
  DAT_ffe51094 = 0;
  DAT_ffe51020 = 0;
  DAT_ffe51024 = 0;
  DAT_ffe51028 = 0;
  DAT_ffe5102c = 0;
  DAT_ffe51080 = 0x156;
  DAT_ffe51084 = 0;
  DAT_ffe51088 = 0;
  DAT_ffe5108c = 0;
  DAT_ffe51000 = 0;
  DAT_ffe51004 = 0;
  DAT_ffe51008 = 0;
  DAT_ffe5100c = 0;
  DAT_ffe51060 = 0;
  DAT_ffe5105c = 0;
  DAT_ffe510a0 = 0;
  DAT_ffe510a4 = 0;
  return;
}

void initialize_timer_banks_and_start_tauj0_channel2_1ca0(void)

{
  Ramffe201c8 = 0xffff;
  Ramffe211c8 = 0xffff;
  Ramffe221c8 = 0xffff;
  initialize_tauj0_with_channel2_period_79999_1c20();
  fill_constant_block_1c60();
  DAT_ffe52058 = 0xf;
  DAT_ffe70034 = 1;
  DAT_ffe71034 = 1;
  TAUJ0TS = '\x04';
  DAT_ffe51054 = 1;
  return;
}

void set_indexed_byte_bit_1d0e(byte *param_1,uint param_2)

{
  *param_1 = *param_1 | '\x01' << (param_2 & 7);
  return;
}

undefined4 read_ffe51010_word_1d24(void)

{
  undefined4 uVar1;
  
  uVar1 = DAT_ffe51010;
  return uVar1;
}

int arm_timer_slot_from_tick_with_callback_data_1d2c(ushort param_1,uint param_2,int param_3,undefined1 param_4)

{
  int *piVar1;
  uint32_t puVar2;
  undefined4 uVar3;
  int iVar4;
  
  puVar2 = (camry_gp + 0x0u);
  uVar3 = raise_pmr_and_return_previous_mask_721e(0xffff);
  iVar4 = ((void)(uVar3), read_ffe51010_word_1d24());
  piVar1 = ((int *)camry_host_ptr((uint32_t)(puVar2 + (short)(param_1 & 0xff) * 0xc + -0x6ec8)));
  piVar1[1] = param_3;
  (*((undefined1 *)camry_host_ptr((uint32_t)((int)camry_host_addr(piVar1) + 9)))) = param_4;
  *piVar1 = (param_2 & 0xffff) * 20000 + iVar4;
  *(undefined1 *)(piVar1 + 2) = 1;
  restore_pmr_preserving_interrupt_disable_state_7244(uVar3);
  return iVar4;
}

void disarm_indexed_timer_slot_1d70(ushort param_1)

{
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)((uint32_t)((camry_gp + 0xffff9138u) + (uint32_t)((short)(param_1 & 0xff)) * (uint32_t)sizeof(F33BootTimerSlot)) + (uint32_t)(0) * (uint32_t)sizeof(F33BootTimerSlot) + (uint32_t)offsetof(F33BootTimerSlot, armed))))) = '\0';
  return;
}

uint32_t dispatch_expired_armed_timer_slots_1d9a(void)

{
  uint32_t camry_r10_result;
  uint8_t stack_record_1c[28];
  int iVar1;
  int *piVar2;
  undefined8 uVar3;
  int iVar4;
  undefined4 uVar5;
  int iVar6;
  int iVar7;
  
  uVar3 = 0x869cfebf9800;
  uVar5 = (camry_r10_result = raise_pmr_and_return_previous_mask_721e(0xffff));
  iVar6 = (camry_r10_result = read_ffe51010_word_1d24());
  for (iVar7 = 0; iVar4 = (int)((ulonglong)uVar3 >> 0x20),
      iVar1 = iVar7 - (uint)(*((byte *)camry_host_ptr((uint32_t)(iVar4 + 0x278)))), ((iVar1 < 0) || (iVar7 < 0));
      iVar7 = iVar7 + 1) {
    piVar2 = ((int *)camry_host_ptr((uint32_t)(iVar7 * 0xc + (int)uVar3 + -0x6ec8)));
    if (((char)piVar2[2] != '\0') && (*piVar2 - iVar6 < 0 || *piVar2 == iVar6)) {
      (*((int32_t *)(stack_record_1c + 4))) = piVar2[1];
      *(undefined1 *)(piVar2 + 2) = 0;
      (*((uint32_t *)(stack_record_1c + 8))) = (uint)(*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(piVar2) + 9))));
      (*((int32_t *)(stack_record_1c + 0))) = iVar7;
      (camry_r10_result = invoke_descriptor_callback_and_return_zero_3460((*((undefined4 *)camry_host_ptr((uint32_t)(iVar7 * 4 + (*((volatile int32_t *)camry_host_ptr((uint32_t)(iVar4 + 0x274)))))))), camry_host_addr(((int32_t *)(stack_record_1c)))));
    }
  }
  restore_pmr_preserving_interrupt_disable_state_7244(uVar5);
  return camry_r10_result;
}

void thunk_service_three_callbacks_when_state_two_14a2(void)

{
  service_three_callbacks_when_state_two_14a2();
  return;
}

void raise_interrupt_mask_and_spin_1e10(void)

{
  raise_pmr_and_return_previous_mask_721e(0xffff);
  do {
                    /* WARNING: Do nothing block with infinite loop */
  } while( true );
}

void thunk_raise_interrupt_mask_and_spin_1e10(void)

{
  raise_interrupt_mask_and_spin_1e10();
  return;
}

void raise_interrupt_mask_and_spin_1e36(void)

{
  raise_pmr_and_return_previous_mask_721e(0xffff);
  do {
                    /* WARNING: Do nothing block with infinite loop */
  } while( true );
}

void boot_tauj0_ch2_callback(void)

{
  thunk_service_three_callbacks_when_state_two_14a2();
  return;
}

void service_receive_fifo_channel0_1e50(void)

{
  dispatch_pending_type3_fifo_frames_4048(0);
  return;
}

void service_transmit_status_channel0_1e5e(void)

{
  dispatch_pending_type0_tx_buffer_events_3ef2(0);
  return;
}

void service_receive_fifo_channel1_1e6c(void)

{
  dispatch_pending_type3_fifo_frames_4048(1);
  return;
}

void service_transmit_status_channel1_1e7a(void)

{
  dispatch_pending_type0_tx_buffer_events_3ef2(1);
  return;
}

void service_receive_fifo_channel2_1e88(void)

{
  dispatch_pending_type3_fifo_frames_4048(2);
  return;
}

void service_transmit_status_channel2_1e96(void)

{
  dispatch_pending_type0_tx_buffer_events_3ef2(2);
  return;
}

void raise_interrupt_mask_and_spin_1ea4(void)

{
  raise_pmr_and_return_previous_mask_721e(0xffff);
  do {
                    /* WARNING: Do nothing block with infinite loop */
  } while( true );
}

undefined4 copy_pdu_descriptor_and_submit_1ec0(undefined2 param_1,undefined4 *param_2)

{
  uint8_t stack_record_c[12];
  
  (*((uint32_t *)(stack_record_c + 0))) = *param_2;
  (*((uint16_t *)(stack_record_c + 4))) = *(undefined2 *)(param_2 + 1);
  return submit_at_most_eight_byte_mapped_pdu_4606(param_1,stack_record_c);
}

undefined4 cancel_mapped_transmit_and_return_zero_1ede(undefined2 param_1)

{
  cancel_transmit_by_pdu_mapping_45b2(param_1);
  return 0;
}

void boot_transport_rx_record_callback(void *record)

{
  F33BootPduInfo local_c;
  
  local_c.data = ((uint32_t)((uint32_t)((int)camry_host_addr(record) + 0xc)));
  local_c.length = (ushort)(*((undefined4 *)camry_host_ptr((uint32_t)((int)camry_host_addr(record) + 8))));
  boot_transport_receive_frame((*((ushort *)camry_host_ptr((uint32_t)((int)camry_host_addr(record) + 4)))),&local_c);
  return;
}

void handle_successful_transmit_event_1f0c(char *param_1)

{
  if (*param_1 == '\0') {
    advance_transport_on_transmit_confirmation_2f1c(*(uint *)(param_1 + 4) & 0xffff);
  }
  return;
}

void fill_constant_block_1f24(void)

{
  (*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff9137u)))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff9136u)))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff9135u)))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff9134u)))) = 0;
  (*((volatile uint16_t *)camry_host_ptr((camry_gp + 0xffff912cu)))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff9133u)))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff9132u)))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff9131u)))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff9130u)))) = 0xa5;
  (*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff912fu)))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((camry_gp + 0xffff912eu)))) = 0;
  return;
}

void increment_timer_generation_and_arm_transport_slot_1f60(uint param_1,uint param_2,undefined2 param_3)

{
  int iVar1;
  byte bVar2;
  
  iVar1 = (param_2 & 0xff) + (param_1 & 0xff) * 2;
  bVar2 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)((camry_gp + 0xffff912eu) + (uint32_t)(iVar1) * 1u)))) + 1;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)((camry_gp + 0xffff912eu) + (uint32_t)(iVar1) * 1u)))) = bVar2;
  arm_timer_slot_from_tick_with_callback_data_1d2c((*((volatile uint8_t *)camry_host_ptr((uint32_t)((camry_tp + 0x6b0u) + (uint32_t)(iVar1) * 1u)))),param_3,(uint)bVar2 + (param_1 & 0xff) * 0x100,0);
  return;
}

void send_transport_flow_control_continue_1f98(ushort param_1)

{
  undefined1 uVar1;
  byte bVar2;
  undefined2 uVar3;
  ushort channel;
  uint uVar4;
  uint uVar5;
  uint32_t puVar6;
  int iVar7;
  undefined1 uVar8;
  int iVar9;
  F33BootPduInfo local_1c;
  undefined1 auStack_14 [8];
  
  puVar6 = (camry_gp + 0x0u);
  iVar9 = (short)(param_1 & 0xff) * 0x18;
  uVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)((camry_tp + 0x6bau) + (uint32_t)(iVar9) * 1u))));
  bVar2 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)((camry_tp + 0x6bcu) + (uint32_t)(iVar9) * 1u))));
  iVar7 = (uint)bVar2 * 0x10;
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)((camry_tp + 0x6e4u) + (uint32_t)(iVar7) * 1u)))) == '\x04') {
    auStack_14[0] = (*((volatile uint8_t *)camry_host_ptr((uint32_t)((camry_tp + 0x6e5u) + (uint32_t)(iVar7) * 1u))));
  }
  uVar4 = (uint)((*((volatile uint8_t *)camry_host_ptr((uint32_t)((camry_tp + 0x6e4u) + (uint32_t)(iVar7) * 1u)))) == '\x04');
  auStack_14[uVar4] = 0x30;
  uVar5 = uVar4 + 2;
  auStack_14[uVar4 + 1] = (*((volatile uint8_t *)camry_host_ptr((uint32_t)((camry_tp + 0x6bdu) + (uint32_t)(iVar9) * 1u))));
  uVar8 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)((camry_tp + 0x6beu) + (uint32_t)(iVar9) * 1u))));
  while( true ) {
    auStack_14[uVar5] = uVar8;
    uVar5 = uVar5 + 1 & 0xffff;
    if (7 < uVar5) break;
    uVar8 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)((camry_tp + 0x6e6u) + (uint32_t)(iVar7) * 1u))));
  }
  local_1c.length = 8;
  local_1c.data = camry_host_addr(auStack_14);
  iVar7 = copy_pdu_descriptor_and_submit_1ec0((*((volatile uint16_t *)camry_host_ptr((uint32_t)((camry_tp + 0x6f2u) + (uint32_t)((uint)bVar2 * 8) * 2u)))),&local_1c);
  if (iVar7 == 0) {
    uVar3 = *(undefined2 *)(((undefined *)camry_host_ptr((uint32_t)((camry_tp + 0x6c0u) + (uint32_t)(iVar9) * 1u))));
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(-0x6ec9))))) = 0;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(-0x6ecc))))) = 0;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(-0x6ecf))))) = 0x49;
    increment_timer_generation_and_arm_transport_slot_1f60(uVar1,0,uVar3);
  }
  else {
    channel = *(ushort *)(&(*((volatile uint32_t *)camry_host_ptr((camry_tp + 0x6cau)))) + (short)(param_1 & 0xff) * 6);
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(-0x6ecf))))) = 0;
    boot_transport_receive_complete(channel,'\x01');
  }
  return;
}
