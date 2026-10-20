#include "common.h"

void return_only_stub_b50a8(void)

{
  return;
}

void return_only_stub_b50aa(void)

{
  return;
}

void aggregate_six_encoded_f2xx_status_words_b50ac(void)

{
  if (((((DAT_febef204 != -0x5aa5a55b) || (DAT_febef210 != -0x5aa5a55b)) ||
       (DAT_febef214 != -0x5aa5a55b)) ||
      ((DAT_febef20c != -0x5aa5a55b || (DAT_febef21c != -0x5aa5a55b)))) ||
     (DAT_febeb218 = DAT_febef208, DAT_febef208 != -0x5aa5a55b)) {
    if (((DAT_febef204 == 0x5aa5a55a) || (DAT_febef210 == 0x5aa5a55a)) ||
       ((DAT_febef214 == 0x5aa5a55a ||
        (((DAT_febef20c == 0x5aa5a55a || (DAT_febef21c == 0x5aa5a55a)) ||
         (DAT_febef208 == 0x5aa5a55a)))))) {
      DAT_febeb218 = 0x5aa5a55a;
    }
    else if (((DAT_febef204 == 0) || (DAT_febef210 == 0)) ||
            ((DAT_febef214 == 0 ||
             (((DAT_febef20c == 0 || (DAT_febef21c == 0)) || (DAT_febef208 == 0)))))) {
      DAT_febeb218 = 0;
    }
    else {
      DAT_febeb218 = -1;
    }
  }
  return;
}

void aggregate_three_encoded_status_and_fault_bytes_b5120(void)

{
  if (((((DAT_febeb314 == -1) || (DAT_febeb300 == '\"')) || (DAT_febeb474 == -1)) ||
      ((DAT_febeb45f == '\"' || (DAT_febeb478 == -1)))) || (DAT_febeb32f == '\"')) {
    DAT_febeb21c = 0x5aa5a55a;
  }
  else if ((((DAT_febeb314 == 0x55aaaa55) || (DAT_febeb314 == -0x55aaaa56)) &&
           ((DAT_febeb474 == 0x55aaaa55 || (DAT_febeb474 == -0x55aaaa56)))) &&
          ((DAT_febeb478 == 0x55aaaa55 || (DAT_febeb478 == -0x55aaaa56)))) {
    DAT_febeb21c = 0xa55a5aa5;
  }
  else if ((DAT_febeb314 == 0x33333333) ||
          ((DAT_febeb474 == 0x33333333 || (DAT_febeb478 == 0x33333333)))) {
    DAT_febeb21c = 0;
  }
  else {
    DAT_febeb21c = 0xffffffff;
  }
  return;
}

void publish_b2d0_mode_22_gate_b51a8(void)

{
  DAT_febeb215 = 0;
  if (DAT_febeb2d0 == '\"') {
    DAT_febeb215 = 0x5a;
  }
  return;
}

void monitor_routine_1106_lifecycle_groups(void)

{
  uint32_t puVar1;
  char cVar2;
  
  puVar1 = 0xfebeb800u;
  cVar2 = DAT_febeb214;
  if (DAT_febeb214 == '\x11') {
    if (((DAT_febeb311 == 'D') && (DAT_febeb471 == 'D')) && (DAT_febeb256 == 'D')) {
      puVar1 = 0xfebeb800u;
      thunk_publish_routine_or_pending_write_terminal_result_4d0a4(9,0);
      cVar2 = '\"';
    }
    else if ((((DAT_febeb311 != '\x11') && (DAT_febeb311 != '\"')) &&
             ((DAT_febeb471 != '\x11' && ((DAT_febeb471 != '\"' && (DAT_febeb256 != '\x11')))))) &&
            (DAT_febeb256 != '\"')) {
      puVar1 = 0xfebeb800u;
      thunk_publish_routine_or_pending_write_terminal_result_4d0a4(9,0x20);
      cVar2 = 'D';
    }
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x5ec))))) = cVar2;
  return;
}

void run_init_chain_b5232(void)

{
  aggregate_six_encoded_f2xx_status_words_b50ac();
  aggregate_three_encoded_status_and_fault_bytes_b5120();
  publish_b2d0_mode_22_gate_b51a8();
  monitor_routine_1106_lifecycle_groups();
  return;
}

void initialize_three_state_groups_and_b214_b524a(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  set_record_101_zero_write_idle_b5ec6();
  prepare_record_102_zero_write_b707a();
  set_byte_b471_to_44_b8fa8();
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x5ec))))) = 0x11;
  return;
}

void fill_constant_block_b5266(void)

{
  DAT_febeb24c = 0;
  DAT_febeb24f = 0;
  DAT_febeb251 = 0;
  DAT_febeb24d = DAT_000aeba8;
  DAT_febeb252 = 0;
  DAT_febeb25a = 0;
  DAT_febeb26c = 0;
  DAT_febeb25c = 0;
  DAT_febeb24e = DAT_000aebb8;
  DAT_febeb250 = 0x5a;
  return;
}

void load_record_101_selected_bytes_b5294(void)

{
  uint8_t stack_record_18[24];
  int iVar1;
  int iVar2;
  undefined4 *puVar3;
  int iVar4;
  undefined4 uVar5;
  undefined1 uVar6;
  undefined4 *puVar7;
  
  puVar3 = ((uint32_t *)(stack_record_18));
  puVar7 = ((undefined *)camry_host_ptr(0x1bdfcu));
  do {
    uVar5 = *puVar7;
    puVar7 = puVar7 + 1;
    *puVar3 = uVar5;
    puVar3 = puVar3 + 1;
  } while (camry_host_addr(puVar7)!=((uint32_t)(0x1be0cu)));
  if (DAT_febeb252 == 'D') {
    iVar4 = call_nvm_get_record_with_u16_selector_ff0b0(0x101,((uint32_t *)(stack_record_18)));
    if (iVar4 == 0x10) {
      iVar4 = 0;
      do {
        switch(iVar4) {
        case 0:
          uVar6 = stack_record_18[8];
          break;
        case 1:
          uVar6 = stack_record_18[9];
          break;
        case 2:
          uVar6 = stack_record_18[10];
          break;
        case 3:
          uVar6 = stack_record_18[11];
          break;
        case 4:
          uVar6 = stack_record_18[12];
          break;
        case 5:
          uVar6 = stack_record_18[14];
          break;
        default:
          uVar6 = 0xff;
        }
        (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb25fu + (uint32_t)(iVar4) * 1u)))) = uVar6;
        iVar2 = iVar4 + 1;
        iVar1 = iVar4 + -0xc;
        iVar4 = iVar2;
      } while (((iVar1 < 0) || (iVar2 < 0)));
    }
  }
  else {
    iVar4 = 0;
    do {
      iVar2 = iVar4 + 1;
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb25fu + (uint32_t)(iVar4) * 1u)))) = 0xff;
      iVar1 = iVar4 + -0xc;
      iVar4 = iVar2;
    } while (((iVar1 < 0) || (iVar2 < 0)));
  }
  return;
}

void initialize_record_101_status_and_defaults_b532a(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  DAT_febeb252 = 0x44;
  DAT_febeb24c = 0;
  DAT_febeb25a = 0x44;
  DAT_febeb24d = DAT_000aeba8;
  DAT_febeb24e = DAT_000aebb8;
  report_diagnostic_healthy_observed(0x129);
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x5b0))))) = 0x5a;
  load_record_101_selected_bytes_b5294();
  return;
}

void reset_record_101_status_and_diagnostics_b5368(void)

{
  undefined1 uVar1;
  uint32_t puVar2;
  char cVar3;
  
  puVar2 = 0xfebeb800u;
  cVar3 = DAT_febeb255;
  if (DAT_febeb255 == '\x11') {
    puVar2 = 0xfebeb800u;
    thunk_publish_routine_or_pending_write_terminal_result_4d0a4(0x13,0);
    cVar3 = 'D';
  }
  report_diagnostic_healthy_observed(0x129);
  thunk_clear_event_bit_from_three_bitmaps_and_mark_dirty_524be(0xbe);
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x5ae))))) = 0x44;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x5a6))))) = 0x44;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x5b4))))) = 0;
  uVar1 = DAT_000aeba8;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x5ab))))) = cVar3;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x5b3))))) = uVar1;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x5b2))))) = DAT_000aebb8;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x5b0))))) = 0x5a;
  return;
}

void reset_record_101_and_reload_selected_bytes_b53c2(void)

{
  reset_record_101_status_and_diagnostics_b5368();
  load_record_101_selected_bytes_b5294();
  return;
}

void select_record_101_defaults_by_index_b53d2(void)

{
  uint8_t stack_record_24[36];
  undefined1 uVar1;
  undefined1 uVar2;
  undefined4 *puVar3;
  uint32_t puVar4;
  int iVar5;
  undefined4 uVar6;
  undefined1 uVar7;
  undefined1 uVar8;
  undefined4 *puVar9;
  
  uVar2 = DAT_febeb24e;
  uVar1 = DAT_febeb24d;
  puVar4 = (0xfebeb800u);
  puVar3 = ((uint32_t *)(stack_record_24));
  puVar9 = ((undefined *)camry_host_ptr(0x1be0cu));
  do {
    uVar6 = *puVar9;
    puVar9 = puVar9 + 1;
    *puVar3 = uVar6;
    puVar3 = puVar3 + 1;
  } while (camry_host_addr(puVar9)!=((uint32_t)(0x1be1cu)));
  uVar8 = DAT_000aeba8;
  uVar7 = DAT_000aebb8;
  if ((DAT_febeb252 == 'D') &&
     (puVar4 = (0xfebeb800u), iVar5 = call_nvm_get_record_with_u16_selector_ff0b0(0x101,((uint32_t *)(stack_record_24))), uVar8 = uVar1, uVar7 = uVar2,
     iVar5 == 0x10)) {
    uVar8 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xaeba8u + (uint32_t)(stack_record_24[4]) * 1u))));
    uVar7 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xaebb8u + (uint32_t)(stack_record_24[4]) * 1u))));
  }
  (*((volatile undefined *)camry_host_ptr((uint32_t)(0xfebeb800u + (uint32_t)(-0x5b3) * 1u)))) = uVar8;
  (*((volatile undefined *)camry_host_ptr((uint32_t)(0xfebeb800u + (uint32_t)(-0x5b2) * 1u)))) = uVar7;
  return;
}

void report_four_enabled_diagnostic_bits_b5440(uint param_1,uint param_2)

{
  int iVar1;
  byte bVar2;
  uint uVar3;
  
  bVar2 = DAT_000aeb88;
  if ((param_1 & 0xff) < 2) {
    uVar3 = 0;
    do {
      if ((bVar2 >> (uVar3 & 0x1f) & 1) != 0) {
        iVar1 = (uVar3 + (param_1 & 0xff) * 4) * 4;
        if (((param_2 & 0xff) >> (uVar3 & 0x1f) & 1) == 0) {
          thunk_clear_event_bit_from_three_bitmaps_and_mark_dirty_524be(*(undefined2 *)(((undefined *)camry_host_ptr((uint32_t)(0xaebc8u + (uint32_t)(iVar1) * 1u)))));
        }
        else {
          thunk_route_event_failure_by_e85a_mode_51d38(*(undefined2 *)(((undefined *)camry_host_ptr((uint32_t)(0xaebc8u + (uint32_t)(iVar1) * 1u)))),(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xaebcau + (uint32_t)(iVar1) * 1u)))),0x32);
        }
      }
      uVar3 = uVar3 + 1;
    } while (uVar3 < 4);
  }
  return;
}

void advance_record_101_staged_write_b5498(void)

{
  char cVar1;
  undefined1 uVar2;
  uint32_t puVar3;
  undefined4 uVar4;
  uint uVar5;
  undefined1 uVar6;
  undefined1 uVar7;
  undefined1 uVar8;
  ushort uVar9;
  uint uVar10;
  undefined1 uVar11;
  char cVar12;
  
  uVar9 = DAT_febeb26c;
  uVar2 = DAT_febeb25d;
  uVar6 = DAT_febeb25a;
  cVar1 = DAT_febeb259;
  uVar7 = DAT_febeb257;
  cVar12 = DAT_febeb254;
  uVar8 = DAT_febeb253;
  uVar11 = DAT_febeb252;
  puVar3 = 0xfebeb800u;
  uVar10 = (uint)DAT_febeb26c;
  if (DAT_febeb254 == '\x11') {
    if ((DAT_febeb255 != '\"') && (DAT_febeb256 != '\"')) {
      puVar3 = 0xfebeb800u;
      call_nvm_set_record_with_u16_selector_ff09c(0x101,((undefined *)camry_host_ptr(0xfebeb220u)));
      cVar12 = '\"';
    }
  }
  else if (DAT_febeb254 == '\"') {
    puVar3 = 0xfebeb800u;
    uVar5 = call_nvm_record_status_with_u16_selector_ff0c4(0x101);
    if (uVar5 == 0x10) {
      if ((int)uVar10 >> 8 == 0x22) {
        uVar11 = 0x44;
        report_diagnostic_event_pass(0xbe);
        uVar9 = 0x8822;
      }
      else {
        uVar11 = 0x11;
        thunk_route_event_failure_by_e85a_mode_51d38(0xbe,0xc,0x32);
        uVar9 = 0x8844;
      }
      report_four_enabled_diagnostic_bits_b5440(0,uVar2);
      report_four_enabled_diagnostic_bits_b5440(1,0);
      uVar4 = 0;
      if (cVar1 == 'Z') {
        uVar4 = 0xff;
      }
      report_two_enabled_diagnostic_bits_b60d0(1,uVar4);
      report_two_enabled_diagnostic_bits_b60d0(3,0);
      uVar8 = 0;
      uVar7 = 0;
      cVar12 = 'D';
      uVar6 = uVar11;
    }
    else if ((uVar5 & 0xf0) != 0x20) {
      report_diagnostic_event_failure(0x131,0x32);
      uVar9 = 0x8844;
      cVar12 = -0x78;
      uVar11 = 0x22;
    }
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x5ac))))) = cVar12;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x5ae))))) = uVar11;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x5ad))))) = uVar8;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x5a9))))) = uVar7;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x5a6))))) = uVar6;
  (*((ushort *)camry_host_ptr((uint32_t)(puVar3 + -0x594)))) = uVar9;
  return;
}

uint write_record_101_marker_and_b25e_b5586(void)

{
  uint8_t stack_record_14[20];
  
  stack_record_14[5] = 0;
  (*((uint16_t *)(stack_record_14 + 6))) = 0xa55a;
  stack_record_14[4] = DAT_febeb25e;
  (*((uint32_t *)(stack_record_14 + 0))) = 0xa55a5aa5;
  stack_record_14[8] = 0;
  stack_record_14[9] = 0;
  stack_record_14[10] = 0;
  stack_record_14[11] = 0;
  stack_record_14[12] = 0;
  stack_record_14[13] = 0;
  stack_record_14[14] = 0;
  stack_record_14[15] = 0;
  return call_nvm_set_record_with_u16_selector_ff09c(0x101,stack_record_14);
}

void advance_record_101_marker_write_b55c0(void)

{
  uint32_t puVar1;
  uint uVar2;
  char cVar3;
  undefined1 uVar4;
  undefined1 uVar5;
  char cVar6;
  char cVar7;
  
  cVar3 = DAT_febeb25a;
  uVar4 = DAT_febeb257;
  cVar7 = DAT_febeb255;
  uVar5 = DAT_febeb253;
  cVar6 = DAT_febeb252;
  puVar1 = 0xfebeb800u;
  if (DAT_febeb255 == '\x11') {
    if ((DAT_febeb254 != '\"') && (DAT_febeb256 != '\"')) {
      puVar1 = 0xfebeb800u;
      write_record_101_marker_and_b25e_b5586();
      cVar7 = '\"';
    }
  }
  else if (DAT_febeb255 == '\"') {
    puVar1 = 0xfebeb800u;
    uVar2 = call_nvm_record_status_with_u16_selector_ff0c4(0x101);
    if (uVar2 == 0x10) {
      cVar6 = 'D';
      report_diagnostic_event_pass(0xbe);
      report_four_enabled_diagnostic_bits_b5440(0,0);
      report_four_enabled_diagnostic_bits_b5440(1,0);
      report_two_enabled_diagnostic_bits_b60d0(1,0);
      report_two_enabled_diagnostic_bits_b60d0(3,0);
      uVar5 = 0;
      thunk_publish_routine_or_pending_write_terminal_result_4d0a4(0x13,0);
      uVar4 = 0x5a;
      cVar7 = cVar6;
      cVar3 = cVar6;
    }
    else if ((uVar2 & 0xf0) != 0x20) {
      report_diagnostic_event_failure(0x131,0x32);
      thunk_publish_routine_or_pending_write_terminal_result_4d0a4(0x13,0x20);
      cVar7 = -0x78;
      cVar6 = '\"';
    }
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x5ae))))) = cVar6;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x5ad))))) = uVar5;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x5ab))))) = cVar7;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x5a9))))) = uVar4;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x5a6))))) = cVar3;
  return;
}

uint write_zero_record_101_b5682(void)

{
  uint8_t stack_record_14[20];
  
  stack_record_14[4] = 0;
  stack_record_14[5] = 0;
  (*((uint16_t *)(stack_record_14 + 6))) = 0;
  (*((uint32_t *)(stack_record_14 + 0))) = 0;
  stack_record_14[8] = 0;
  stack_record_14[9] = 0;
  stack_record_14[10] = 0;
  stack_record_14[11] = 0;
  stack_record_14[12] = 0;
  stack_record_14[13] = 0;
  stack_record_14[14] = 0;
  stack_record_14[15] = 0;
  return call_nvm_set_record_with_u16_selector_ff09c(0x101,stack_record_14);
}

void advance_record_101_zero_write_b56ae(void)

{
  uint32_t puVar1;
  uint uVar2;
  undefined1 uVar3;
  undefined1 uVar4;
  undefined1 uVar5;
  undefined1 uVar6;
  char cVar7;
  
  uVar3 = DAT_febeb25a;
  uVar4 = DAT_febeb257;
  cVar7 = DAT_febeb256;
  uVar5 = DAT_febeb253;
  uVar6 = DAT_febeb252;
  puVar1 = 0xfebeb800u;
  if (DAT_febeb256 == '\x11') {
    if ((DAT_febeb254 != '\"') && (DAT_febeb255 != '\"')) {
      puVar1 = 0xfebeb800u;
      write_zero_record_101_b5682();
      cVar7 = '\"';
    }
  }
  else if (DAT_febeb256 == '\"') {
    puVar1 = 0xfebeb800u;
    uVar2 = call_nvm_record_status_with_u16_selector_ff0c4(0x101);
    if (uVar2 == 0x10) {
      uVar6 = 0x11;
      uVar4 = 0;
      thunk_route_event_failure_by_e85a_mode_51d38(0xbe,0xc,0x32);
      report_four_enabled_diagnostic_bits_b5440(0,0);
      report_four_enabled_diagnostic_bits_b5440(1,0);
      report_two_enabled_diagnostic_bits_b60d0(1,0);
      report_two_enabled_diagnostic_bits_b60d0(3,0);
      uVar5 = 0;
      cVar7 = 'D';
      uVar3 = uVar6;
    }
    else if ((uVar2 & 0xf0) != 0x20) {
      report_diagnostic_event_failure(0x131,0x32);
      cVar7 = -0x78;
      uVar6 = 0x22;
    }
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x5aa))))) = cVar7;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x5ae))))) = uVar6;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x5ad))))) = uVar5;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x5a9))))) = uVar4;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x5a6))))) = uVar3;
  return;
}

undefined4 lookup_banked_code_or_wildcard_word_b5760(uint param_1,char param_2)

{
  char *pcVar1;
  uint uVar2;
  
  uVar2 = 0;
  while( true ) {
    if ((byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xaeb8au + (uint32_t)(param_1 & 0xff) * 1u)))) <= uVar2) {
      return 0;
    }
    pcVar1 = ((void *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xaebe8u + (uint32_t)(param_1 & 0xff) * 4u)))) + uVar2 * 8)));
    if ((*pcVar1 == 'Z') || (param_2 == pcVar1[1])) break;
    uVar2 = uVar2 + 1 & 0xff;
  }
  return *(undefined4 *)(pcVar1 + 4);
}

void update_channel_sequence_and_code_lookup_b57a4(uint param_1,byte *param_2,byte param_3,char param_4)

{
  int iVar1;
  byte bVar2;
  byte bVar3;
  byte bVar4;
  byte bVar5;
  undefined1 extraout_r9;
  int iVar6;
  undefined1 uVar7;
  byte bVar8;
  byte bVar9;
  char cVar10;
  
  param_1 = param_1 & 0xff;
  iVar1 = param_1 * 4;
  uVar7 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb233u + (uint32_t)(iVar1) * 1u))));
  cVar10 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb230u + (uint32_t)(iVar1) * 1u))));
  bVar2 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb232u + (uint32_t)(iVar1) * 1u))));
  bVar3 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb231u + (uint32_t)(iVar1) * 1u))));
  iVar6 = (*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xfebeb270u + (uint32_t)(param_1) * 4u))));
  bVar8 = bVar3;
  bVar9 = bVar2;
  if (((int8_t)cVar10) != -1) {
    if ((param_3 & DAT_000aeb89) == 0) {
      cVar10 = -1;
      iVar6 = lookup_banked_code_or_wildcard_word_b5760(param_1,0xff);
      uVar7 = 0;
      bVar9 = 0xff;
    }
    else {
      bVar4 = param_2[1];
      bVar5 = param_2[2];
      bVar8 = bVar4;
      if ((*param_2 & 1) == 0) {
        bVar8 = bVar3;
      }
      if ((bVar4 != bVar8) && (bVar9 = bVar5, (byte)(bVar4 - bVar8) != 1)) {
        if (bVar2 == bVar5) {
          bVar9 = bVar2;
          if (DAT_000aecd8 <= (byte)(bVar4 - bVar8)) {
            if (param_4 == 'Z') {
              cVar10 = -1;
              iVar6 = lookup_banked_code_or_wildcard_word_b5760(param_1,bVar2);
              uVar7 = ((undefined1)((uint)(byte)param_4));
              if (iVar6 != 0) {
                uVar7 = 0;
              }
            }
            else {
              iVar6 = lookup_banked_code_or_wildcard_word_b5760(param_1,bVar2);
              if (iVar6 == 0) {
                cVar10 = '\0';
                bVar8 = bVar4;
                bVar9 = bVar5;
              }
              else {
                uVar7 = 0;
                cVar10 = -1;
              }
            }
          }
        }
        else {
          cVar10 = '\0';
          bVar8 = bVar4 - 1;
        }
      }
    }
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb231u + (uint32_t)(iVar1) * 1u)))) = bVar8;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb232u + (uint32_t)(iVar1) * 1u)))) = bVar9;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb230u + (uint32_t)(iVar1) * 1u)))) = cVar10;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb233u + (uint32_t)(iVar1) * 1u)))) = uVar7;
  (*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xfebeb270u + (uint32_t)(param_1) * 4u)))) = iVar6;
  return;
}

void initialize_channel_sequence_record_b5868(uint param_1,int param_2)

{
  int iVar1;
  undefined1 uVar2;
  
  iVar1 = (param_1 & 0xff) * 4;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb230u + (uint32_t)(iVar1) * 1u)))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb231u + (uint32_t)(iVar1) * 1u)))) = (*((undefined1 *)camry_host_ptr((uint32_t)(param_2 + 1))));
  uVar2 = (*((undefined1 *)camry_host_ptr((uint32_t)(param_2 + 2))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb233u + (uint32_t)(iVar1) * 1u)))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb232u + (uint32_t)(iVar1) * 1u)))) = uVar2;
  return;
}

void reset_seven_channel_sequence_records_b5886(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  uchar record[3];
  
  DAT_febeb24f = 0;
  iVar3 = 0;
  do {
    iVar2 = iVar3 + 1;
    (*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xfebeb270u + (uint32_t)(iVar3) * 4u)))) = 0;
    iVar1 = iVar3 + -6;
    iVar3 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  record[0] = 1;
  record[1] = 0;
  record[2] = 0xff;
  initialize_channel_sequence_record_b5868(0, camry_host_addr(record));
  record[0] = 1;
  record[1] = 0;
  record[2] = 0xff;
  initialize_channel_sequence_record_b5868(1, camry_host_addr(record));
  record[0] = 1;
  record[1] = 0;
  record[2] = 0xff;
  initialize_channel_sequence_record_b5868(2, camry_host_addr(record));
  record[0] = 1;
  record[1] = 0;
  record[2] = 0xff;
  initialize_channel_sequence_record_b5868(3, camry_host_addr(record));
  record[0] = 1;
  record[1] = 0;
  record[2] = 0xff;
  initialize_channel_sequence_record_b5868(4, camry_host_addr(record));
  record[0] = 1;
  record[1] = 0;
  record[2] = 0xff;
  initialize_channel_sequence_record_b5868(5, camry_host_addr(record));
  record[0] = 1;
  record[1] = 0;
  record[2] = 0xff;
  initialize_channel_sequence_record_b5868(6, camry_host_addr(record));
  return;
}

void update_seven_empty_channel_sequences_b5910(undefined1 param_1)

{
  uint8_t stack_record_b[11];
  
  stack_record_b[0] = 1;
  stack_record_b[1] = 0;
  stack_record_b[2] = 0xff;
  update_channel_sequence_and_code_lookup_b57a4(0,((uint8_t *)(stack_record_b)),1,param_1);
  stack_record_b[0] = 1;
  stack_record_b[1] = 0;
  stack_record_b[2] = 0xff;
  update_channel_sequence_and_code_lookup_b57a4(1,((uint8_t *)(stack_record_b)),2,param_1);
  stack_record_b[0] = 1;
  stack_record_b[1] = 0;
  stack_record_b[2] = 0xff;
  update_channel_sequence_and_code_lookup_b57a4(2,((uint8_t *)(stack_record_b)),4,param_1);
  stack_record_b[0] = 1;
  stack_record_b[1] = 0;
  stack_record_b[2] = 0xff;
  update_channel_sequence_and_code_lookup_b57a4(3,((uint8_t *)(stack_record_b)),8,param_1);
  stack_record_b[0] = 1;
  stack_record_b[1] = 0;
  stack_record_b[2] = 0xff;
  update_channel_sequence_and_code_lookup_b57a4(4,((uint8_t *)(stack_record_b)),0x10,param_1);
  stack_record_b[0] = 1;
  stack_record_b[1] = 0;
  stack_record_b[2] = 0xff;
  update_channel_sequence_and_code_lookup_b57a4(5,((uint8_t *)(stack_record_b)),0x20,param_1);
  stack_record_b[0] = 1;
  stack_record_b[1] = 0;
  stack_record_b[2] = 0xff;
  update_channel_sequence_and_code_lookup_b57a4(6,((uint8_t *)(stack_record_b)),0x40,param_1);
  return;
}

void latch_all_seven_channel_flags_set_b59d8(void)

{
  if ((DAT_febeb24f != 'Z') &&
     (DAT_febeb24f = '\0',
     (byte)(DAT_febeb248 & 0x40 |
            DAT_febeb244 & 0x20 |
            DAT_febeb240 & 0x10 |
            DAT_febeb23c & 8 | DAT_febeb238 & 4 | DAT_febeb234 & 2 | DAT_febeb230 & 1 | 0x80) ==
     0xff)) {
    DAT_febeb24f = 'Z';
  }
  return;
}

undefined4 get_channel_completion_or_record_ready_gate_b5a36(void)

{
  char cVar1;
  char cVar2;
  char cVar3;
  uint32_t puVar4;
  int iVar5;
  undefined4 uVar6;
  
  cVar3 = DAT_febeb43c;
  cVar2 = DAT_febeb43b;
  cVar1 = DAT_febeb24f;
  puVar4 = 0xfebeb800u;
  iVar5 = get_record_103_enabled_channel_mask_b6a28();
  if (((iVar5 == 0) || ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x533))))) != '\0')) &&
     ((cVar1 == 'Z' || ((cVar3 == 'Z' || (cVar2 == 'Z')))))) {
    uVar6 = 0x5a;
  }
  else {
    uVar6 = 0;
  }
  return uVar6;
}

undefined4 is_distinct_aeba8_index_b5a74(uint param_1)

{
  undefined4 uVar1;
  
  param_1 = param_1 & 0xff;
  uVar1 = 0;
  if ((param_1 < 0x10) && ((param_1 == 1 || ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xaeba8u + (uint32_t)(param_1) * 1u)))) != DAT_000aeba8)))) {
    uVar1 = 1;
  }
  return uVar1;
}

undefined4 select_highest_common_channel_mask_code_b5a98(uint param_1,undefined1 *param_2)

{
  uint uVar1;
  uint32_t puVar2;
  undefined1 *extraout_r7;
  int iVar3;
  undefined4 uVar4;
  undefined1 uVar5;
  uint uVar6;
  
  puVar2 = 0xfebeb800u;
  uVar6 = DAT_febeb288 &
          DAT_febeb284 & DAT_febeb280 & DAT_febeb27c & DAT_febeb278 & DAT_febeb274 & DAT_febeb270;
  param_1 = param_1 & uVar6;
  if (param_1 != 0) {
    uVar5 = 0;
    uVar1 = 0;
    do {
      if ((param_1 >> (uVar1 & 0x1f) & 1) != 0) {
        DAT_febeb258 = (undefined1)uVar1;
        uVar5 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xaeb98u + (uint32_t)(uVar1) * 1u))));
      }
      uVar1 = uVar1 + 1;
    } while (uVar1 < 0xd);
    puVar2 = 0xfebeb800u;
    iVar3 = is_distinct_aeba8_index_b5a74(uVar5);
    param_2 = ((undefined1 *)(param_2));
    if (iVar3 == 1) {
      uVar4 = 0;
      goto LAB_000b5af2;
    }
  }
  uVar5 = 0;
  uVar4 = 0x5a;
LAB_000b5af2:
  *param_2 = uVar5;
  (*((uint *)camry_host_ptr((uint32_t)(puVar2 + -0x574)))) = uVar6;
  return uVar4;
}

int aggregate_seven_channel_code_selection_b5afe(void)

{
  char cVar1;
  undefined1 uVar2;
  uint uVar3;
  uint32_t puVar4;
  undefined4 uVar5;
  int iVar6;
  byte bVar7;
  undefined1 uStack_9;
  
  puVar4 = 0xfebeb800u;
  bVar7 = 0;
  uVar3 = 0;
  do {
    if ((((int8_t)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb230u + (uint32_t)(uVar3 * 4) * 1u))))) != -1) || ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb233u + (uint32_t)(uVar3 * 4) * 1u)))) != '\0')) {
      bVar7 = bVar7 | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xaeb91u + (uint32_t)(uVar3) * 1u))));
    }
    uVar3 = uVar3 + 1;
  } while (uVar3 < 7);
  iVar6 = get_record_103_enabled_channel_mask_b6a28();
  if (iVar6 == 0) {
    cVar1 = 'Z';
    uVar5 = 0xffffffff;
  }
  else {
    cVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x533)))));
    uVar5 = (*((undefined4 *)camry_host_ptr((uint32_t)(puVar4 + -0x508))));
  }
  if ((bVar7 == 0) && (cVar1 == 'Z')) {
    iVar6 = select_highest_common_channel_mask_code_b5a98(uVar5,&uStack_9);
    if (iVar6 == 0x5a) {
      uVar2 = 0x5a;
      bVar7 = DAT_000aeb88;
    }
    else {
      uVar2 = 0;
    }
  }
  else {
    uStack_9 = 0;
    uVar2 = 0;
    iVar6 = 0x5a;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x5a3))))) = bVar7;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x5a7))))) = uVar2;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x5b4))))) = uStack_9;
  return iVar6;
}

void stage_record_101_channel_snapshot_b5b8c(char param_1)

{
  if (param_1 == '\x01') {
    DAT_febeb224 = DAT_febeb24c;
    DAT_febeb220 = 0xa55a5aa5;
    DAT_febeb228 = DAT_febeb232;
    DAT_febeb229 = DAT_febeb236;
    DAT_febeb22a = DAT_febeb23a;
    DAT_febeb22b = DAT_febeb23e;
    DAT_febeb22c = DAT_febeb242;
    DAT_febeb22d = DAT_febeb246;
    DAT_febeb22e = DAT_febeb24a;
  }
  else {
    DAT_febeb224 = 0;
    DAT_febeb22e = 0;
    DAT_febeb220 = 0;
    DAT_febeb228 = 0;
    DAT_febeb229 = 0;
    DAT_febeb22a = 0;
    DAT_febeb22b = 0;
    DAT_febeb22c = 0;
    DAT_febeb22d = 0;
  }
  DAT_febeb226 = 0;
  DAT_febeb225 = 0;
  DAT_febeb22f = 0;
  DAT_febeb254 = 0x11;
  return;
}

void evaluate_initial_record_101_channel_capture_b5bf6(void)

{
  uint32_t puVar1;
  int iVar2;
  undefined2 uVar3;
  
  uVar3 = DAT_febeb26c;
  puVar1 = 0xfebeb800u;
  if (DAT_febeb257 == 'Z') {
    uVar3 = 0x8822;
  }
  else {
    if ((DAT_000aecda < DAT_febebede) || (published_internal_source_admission_state != '\0')) {
      puVar1 = 0xfebeb800u;
      reset_seven_channel_sequence_records_b5886();
    }
    else {
      puVar1 = 0xfebeb800u;
      update_seven_empty_channel_sequences_b5910(0x5a);
      latch_all_seven_channel_flags_set_b59d8();
    }
    iVar2 = get_channel_completion_or_record_ready_gate_b5a36();
    if (iVar2 == 0x5a) {
      iVar2 = aggregate_seven_channel_code_selection_b5afe();
      if (iVar2 == 0x5a) {
        stage_record_101_channel_snapshot_b5b8c(2);
        uVar3 = 0x4411;
      }
      else {
        stage_record_101_channel_snapshot_b5b8c(1);
        uVar3 = 0x2211;
      }
    }
  }
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x594)))) = uVar3;
  return;
}

undefined4 get_record_101_comparison_ready_gate_b5c6a(void)

{
  char cVar1;
  
  cVar1 = DAT_febeb24f;
  if ((((DAT_febeb25c != '\x11') || (cVar1 = DAT_febeb43d, DAT_febeb2ce == '\x11')) ||
      (DAT_febeb24f != 'Z')) && (cVar1 != 'Z')) {
    return 0;
  }
  return 0x5a;
}

void compare_record_101_channel_codes_and_report_b5ca2(void)

{
  uint8_t stack_record_28[40];
  char *pcVar1;
  char cVar2;
  undefined4 *puVar3;
  uint uVar4;
  uint32_t puVar5;
  char cVar6;
  int iVar7;
  int iVar8;
  undefined4 uVar9;
  byte bVar10;
  undefined4 *puVar11;
  
  puVar5 = 0xfebeb800u;
  puVar11 = ((undefined *)camry_host_ptr(0x1be1cu));
  puVar3 = ((uint32_t *)((stack_record_28 + 8)));
  do {
    uVar9 = *puVar11;
    puVar11 = puVar11 + 1;
    *puVar3 = uVar9;
    puVar3 = puVar3 + 1;
  } while (camry_host_addr(puVar11)!=((uint32_t)(0x1be2cu)));
  call_nvm_get_record_with_u16_selector_ff0b0(0x101,((uint32_t *)((stack_record_28 + 8))));
  bVar10 = 0;
  ((int8_t *)((stack_record_28 + 1)))[0] = stack_record_28[16];
  ((int8_t *)((stack_record_28 + 1)))[1] = stack_record_28[17];
  ((int8_t *)((stack_record_28 + 1)))[2] = stack_record_28[18];
  ((int8_t *)((stack_record_28 + 1)))[3] = stack_record_28[19];
  ((int8_t *)((stack_record_28 + 1)))[4] = stack_record_28[20];
  ((int8_t *)((stack_record_28 + 1)))[5] = stack_record_28[21];
  ((int8_t *)((stack_record_28 + 1)))[6] = stack_record_28[22];
  uVar4 = 0;
  do {
    pcVar1 = ((undefined *)camry_host_ptr((uint32_t)(puVar5 + uVar4 * 4 + -0x5d0)));
    if (((*pcVar1 != -1) || (pcVar1[3] != '\0')) || (pcVar1[2] != ((int8_t *)((stack_record_28 + 1)))[uVar4])) {
      bVar10 = bVar10 | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xaeb91u + (uint32_t)(uVar4) * 1u))));
    }
    uVar4 = uVar4 + 1;
  } while (uVar4 < 7);
  iVar7 = get_record_103_enabled_channel_mask_b6a28();
  if (iVar7 == 0) {
    cVar2 = 'Z';
    uVar9 = 0xffffffff;
    cVar6 = '\0';
  }
  else {
    cVar6 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x531)))));
    cVar2 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x533)))));
    uVar9 = (*((undefined4 *)camry_host_ptr((uint32_t)(puVar5 + -0x508))));
  }
  if (bVar10 == 0) {
    iVar7 = 0;
    iVar8 = iVar7;
    if (((cVar6 == '\0') && (cVar2 == 'Z')) &&
       ((iVar8 = select_highest_common_channel_mask_code_b5a98(uVar9,((int8_t *)(stack_record_28))),(uintptr_t)(((stack_record_28[12])))!=(uintptr_t)(((stack_record_28[0])))|| (iVar8 == 0x5a)))) {
      iVar7 = 0x5a;
      iVar8 = iVar7;
      bVar10 = DAT_000aeb88;
    }
  }
  else {
    iVar7 = 0;
    iVar8 = 0x5a;
  }
  report_four_enabled_diagnostic_bits_b5440(1,bVar10);
  uVar9 = 0;
  if (iVar7 == 0x5a) {
    uVar9 = 0xff;
  }
  report_two_enabled_diagnostic_bits_b60d0(3,uVar9);
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x5a5))))) = bVar10;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x5a7))))) = (char)iVar7;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x5ad))))) = (char)iVar8;
  return;
}

void update_record_101_comparison_mode_b5dba(void)

{
  char cVar1;
  char cVar2;
  char cVar3;
  undefined1 uVar4;
  uint32_t puVar5;
  int iVar6;
  undefined1 uVar7;
  
  cVar3 = DAT_febeb25c;
  cVar2 = DAT_febeb257;
  cVar1 = DAT_febeb252;
  uVar7 = DAT_febeb250;
  puVar5 = 0xfebeb800u;
  if ((DAT_febeb252 == 'D') && (DAT_febeb257 != 'Z')) {
    if (published_internal_source_admission_state == '\0') {
      uVar4 = 0;
      if (DAT_febeb25c == '\x11') {
        uVar4 = 0x5a;
      }
      puVar5 = 0xfebeb800u;
      update_seven_empty_channel_sequences_b5910(uVar4);
      latch_all_seven_channel_flags_set_b59d8();
    }
    else {
      puVar5 = 0xfebeb800u;
      reset_seven_channel_sequence_records_b5886();
    }
    iVar6 = get_record_101_comparison_ready_gate_b5c6a();
    if (iVar6 != 0x5a) {
LAB_000b5e34:
      uVar4 = 0x11;
      goto LAB_000b5e38;
    }
    compare_record_101_channel_codes_and_report_b5ca2();
    uVar7 = 0x5a;
    if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x5b1))))) == 'Z') {
LAB_000b5e2e:
      uVar7 = 0x5a;
      uVar4 = 0x22;
      goto LAB_000b5e38;
    }
  }
  else {
    reset_seven_channel_sequence_records_b5886();
    if (cVar1 == 'D') {
      if (cVar2 == 'Z') goto LAB_000b5e2e;
      goto LAB_000b5e34;
    }
  }
  uVar4 = 0x44;
LAB_000b5e38:
  if (cVar3 == '\x11') {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x5a4))))) = uVar4;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x5b0))))) = uVar7;
  return;
}

void dispatch_record_101_capture_or_comparison_b5e4a(void)

{
  uint32_t puVar1;
  undefined1 uVar2;
  
  puVar1 = 0xfebeb800u;
  if (DAT_febeb26e < DAT_000aecdc) {
    DAT_febeb26e = DAT_febeb26e + 1;
  }
  else {
    DAT_febeb250 = 'Z';
  }
  if ((DAT_febeb26c & 0xff) == 0x11) {
    uVar2 = 1;
    if ((int)(uint)DAT_febeb26c >> 8 == 0x11) {
      puVar1 = 0xfebeb800u;
      evaluate_initial_record_101_channel_capture_b5bf6();
    }
  }
  else if ((DAT_febeb250 == '\0') || (DAT_febeb25c == '\x11')) {
    uVar2 = 2;
    puVar1 = 0xfebeb800u;
    update_record_101_comparison_mode_b5dba();
  }
  else {
    uVar2 = 3;
    puVar1 = 0xfebeb800u;
    reset_seven_channel_sequence_records_b5886();
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x5af))))) = uVar2;
  return;
}

void set_b250_completion_latch_b5eb0(void)

{
  DAT_febeb250 = 0x5a;
  return;
}

void set_record_101_zero_write_idle_b5ec6(void)

{
  DAT_febeb256 = 0x44;
  return;
}

void initialize_b26c_status_and_b25d_mask_b5eda(void)

{
  DAT_febeb26c = 0x8822;
  DAT_febeb25d = 0;
  return;
}

void finish_b25c_mode_and_clear_mismatch_b5f00(void)

{
  DAT_febeb25c = 0x22;
  DAT_febeb25b = 0;
  DAT_febeb250 = 0x5a;
  return;
}

void reset_record_103_workflow_states_b5f28(void)

{
  DAT_febeb2d4 = 0;
  DAT_febeb2ce = 0;
  return;
}

undefined4 lookup_record_103_banked_code_word_b5f32(uint param_1,char param_2)

{
  char *pcVar1;
  uint uVar2;
  
  uVar2 = 0;
  while( true ) {
    if ((byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xaec44u + (uint32_t)(param_1 & 0xff) * 1u)))) <= uVar2) {
      return 0;
    }
    pcVar1 = ((void *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xaec60u + (uint32_t)(param_1 & 0xff) * 4u)))) + uVar2 * 8)));
    if ((*pcVar1 == 'Z') || (param_2 == pcVar1[1])) break;
    uVar2 = uVar2 + 1 & 0xff;
  }
  return *(undefined4 *)(pcVar1 + 4);
}

void load_record_103_codes_and_intersect_masks_b5f76(void)

{
  uint8_t stack_record_5c[92];
  uint8_t stack_record_3c[60];
  int iVar1;
  int iVar2;
  int *piVar3;
  uint32_t puVar4;
  uint uVar5;
  uint uVar6;
  uint uVar7;
  uint uVar8;
  uint uVar9;
  uint uVar10;
  uint uVar11;
  int iVar12;
  undefined1 uVar13;
  undefined1 uVar14;
  undefined1 uVar15;
  undefined1 uVar16;
  undefined1 uVar17;
  undefined1 uVar18;
  undefined1 uVar19;
  undefined1 uVar20;
  undefined1 uVar21;
  int *piVar22;
  
  uVar14 = DAT_febeb2c7;
  uVar15 = DAT_febeb2c6;
  uVar16 = DAT_febeb2c5;
  uVar17 = DAT_febeb2c4;
  uVar18 = DAT_febeb2c3;
  uVar19 = DAT_febeb2c2;
  uVar20 = DAT_febeb2c1;
  uVar21 = DAT_febeb2c0;
  puVar4 = 0xfebeb800u;
  piVar22 = ((undefined *)camry_host_ptr(0x1be2cu));
  piVar3 = ((int32_t *)(stack_record_3c));
  do {
    iVar12 = *piVar22;
    piVar22 = piVar22 + 1;
    *piVar3 = iVar12;
    piVar3 = piVar3 + 1;
  } while (camry_host_addr(piVar22)!=((uint32_t)(0x1be3cu)));
  iVar12 = call_nvm_get_record_with_u16_selector_ff0b0(0x103,((int32_t *)(stack_record_3c)));
  if (iVar12 == 0x10) {
    if ((((int32_t *)(stack_record_3c))[0] == 0) || (((int32_t *)(stack_record_3c))[0] != -0x5aa5a55b)) {
      uVar21 = 0xff;
      uVar13 = 0x33;
      uVar14 = uVar21;
      uVar15 = uVar21;
      uVar16 = uVar21;
      uVar17 = uVar21;
      uVar18 = uVar21;
      uVar19 = uVar21;
      uVar20 = uVar21;
    }
    else {
      uVar13 = 0x5a;
      uVar21 = stack_record_3c[8];
      uVar14 = stack_record_3c[15];
      uVar15 = stack_record_3c[14];
      uVar16 = stack_record_3c[13];
      uVar17 = stack_record_3c[12];
      uVar18 = stack_record_3c[11];
      uVar19 = stack_record_3c[10];
      uVar20 = stack_record_3c[9];
    }
  }
  else {
    uVar13 = 0xff;
    if (iVar12 == 0x11) {
      uVar13 = 0x33;
    }
  }
  uVar5 = lookup_record_103_banked_code_word_b5f32(0,uVar21);
  ((uint32_t *)(stack_record_5c))[0] = uVar5;
  uVar6 = lookup_record_103_banked_code_word_b5f32(1,uVar20);
  ((uint32_t *)(stack_record_5c))[1] = uVar6;
  uVar7 = lookup_record_103_banked_code_word_b5f32(2,uVar19);
  ((uint32_t *)(stack_record_5c))[2] = uVar7;
  uVar8 = lookup_record_103_banked_code_word_b5f32(3,uVar18);
  ((uint32_t *)(stack_record_5c))[3] = uVar8;
  uVar9 = lookup_record_103_banked_code_word_b5f32(4,uVar17);
  (*((uint32_t *)(stack_record_5c + 16))) = uVar9;
  uVar10 = lookup_record_103_banked_code_word_b5f32(5,uVar16);
  (*((uint32_t *)(stack_record_5c + 20))) = uVar10;
  uVar11 = lookup_record_103_banked_code_word_b5f32(6,uVar15);
  (*((uint32_t *)(stack_record_5c + 24))) = uVar11;
  (*((uint32_t *)(stack_record_5c + 28))) = lookup_record_103_banked_code_word_b5f32(7,uVar14);
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x540))))) = uVar21;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x53f))))) = uVar20;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x53e))))) = uVar19;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x53d))))) = uVar18;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x53c))))) = uVar17;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x53b))))) = uVar16;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x53a))))) = uVar15;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x539))))) = uVar14;
  iVar12 = 0;
  do {
    iVar2 = iVar12 + 1;
    iVar1 = iVar12 + -7;
    *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0xfebeb2d8u + (uint32_t)(iVar12 * 4) * 1u)))) = ((uint32_t *)(stack_record_5c))[iVar12];
    iVar12 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  (*((uint *)camry_host_ptr((uint32_t)(puVar4 + -0x508)))) = (*((uint32_t *)(stack_record_5c + 28))) & uVar11 & uVar10 & uVar9 & uVar8 & uVar7 & uVar6 & uVar5;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x533))))) = uVar13;
  return;
}
