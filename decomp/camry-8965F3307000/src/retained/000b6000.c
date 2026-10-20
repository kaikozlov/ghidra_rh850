#include "common.h"

void report_two_enabled_diagnostic_bits_b60d0(uint param_1,uint param_2)

{
  int iVar1;
  byte bVar2;
  uint uVar3;
  
  bVar2 = DAT_000aec5c;
  if ((param_1 & 0xff) < 4) {
    uVar3 = 0;
    do {
      if ((bVar2 >> (uVar3 & 0x1f) & 1) != 0) {
        iVar1 = (uVar3 + (param_1 & 0xff) * 2) * 4;
        if (((param_2 & 0xff) >> (uVar3 & 0x1f) & 1) == 0) {
          thunk_clear_event_bit_from_three_bitmaps_and_mark_dirty_524be(*(undefined2 *)(((undefined *)camry_host_ptr((uint32_t)(0xaec80u + (uint32_t)(iVar1) * 1u)))));
        }
        else {
          thunk_route_event_failure_by_e85a_mode_51d38(*(undefined2 *)(((undefined *)camry_host_ptr((uint32_t)(0xaec80u + (uint32_t)(iVar1) * 1u)))),(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xaec82u + (uint32_t)(iVar1) * 1u)))),0x32);
        }
      }
      uVar3 = uVar3 + 1;
    } while (uVar3 < 2);
  }
  return;
}

void clear_record_103_bank_zero_when_ready_b6128(void)

{
  if (DAT_febeb2cd == 'Z') {
    report_two_enabled_diagnostic_bits_b60d0(0,0);
  }
  return;
}

void initialize_record_103_channel_sequence_b6142(uint param_1,int param_2)

{
  int iVar1;
  undefined1 uVar2;
  
  iVar1 = (param_1 & 0xff) * 4;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb290u + (uint32_t)(iVar1) * 1u)))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb291u + (uint32_t)(iVar1) * 1u)))) = (*((undefined1 *)camry_host_ptr((uint32_t)(param_2 + 1))));
  uVar2 = (*((undefined1 *)camry_host_ptr((uint32_t)(param_2 + 2))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb293u + (uint32_t)(iVar1) * 1u)))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb292u + (uint32_t)(iVar1) * 1u)))) = uVar2;
  return;
}

void reset_eight_record_103_channel_sequences_b6160(void)

{
  uchar record[3];
  
  record[0] = 1;
  record[1] = 0;
  record[2] = 0xff;
  initialize_record_103_channel_sequence_b6142(0, camry_host_addr(record));
  record[0] = 1;
  record[1] = 0;
  record[2] = 0xff;
  initialize_record_103_channel_sequence_b6142(1, camry_host_addr(record));
  record[0] = 1;
  record[1] = 0;
  record[2] = 0xff;
  initialize_record_103_channel_sequence_b6142(2, camry_host_addr(record));
  record[0] = 1;
  record[1] = 0;
  record[2] = 0xff;
  initialize_record_103_channel_sequence_b6142(3, camry_host_addr(record));
  record[0] = 1;
  record[1] = 0;
  record[2] = 0xff;
  initialize_record_103_channel_sequence_b6142(4, camry_host_addr(record));
  record[0] = 1;
  record[1] = 0;
  record[2] = 0xff;
  initialize_record_103_channel_sequence_b6142(5, camry_host_addr(record));
  record[0] = 1;
  record[1] = 0;
  record[2] = 0xff;
  initialize_record_103_channel_sequence_b6142(6, camry_host_addr(record));
  record[0] = 1;
  record[1] = 0;
  record[2] = 0xff;
  initialize_record_103_channel_sequence_b6142(7, camry_host_addr(record));
  return;
}

void load_record_103_and_reset_channels_b61e0(void)

{
  load_record_103_codes_and_intersect_masks_b5f76();
  clear_record_103_bank_zero_when_ready_b6128();
  reset_eight_record_103_channel_sequences_b6160();
  return;
}

void update_record_103_channel_sequence_b61f4(uint param_1,byte *param_2,byte param_3)

{
  int iVar1;
  byte bVar2;
  byte bVar3;
  byte bVar4;
  int iVar5;
  undefined1 uVar6;
  byte bVar7;
  char cVar8;
  byte bVar9;
  
  param_1 = param_1 & 0xff;
  iVar1 = param_1 * 4;
  cVar8 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb290u + (uint32_t)(iVar1) * 1u))));
  bVar7 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb291u + (uint32_t)(iVar1) * 1u))));
  bVar2 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb292u + (uint32_t)(iVar1) * 1u))));
  uVar6 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb293u + (uint32_t)(iVar1) * 1u))));
  bVar9 = bVar2;
  if (((int8_t)cVar8) != -1) {
    if ((param_3 & DAT_000aec5d) == 0) {
      cVar8 = -1;
      uVar6 = 0;
      bVar9 = 0xff;
    }
    else {
      bVar3 = param_2[1];
      bVar4 = param_2[2];
      if (((*param_2 & 1) != 0) || (bVar4 == (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xaec4cu + (uint32_t)(param_1) * 1u)))))) {
        bVar7 = bVar3;
      }
      if ((bVar3 != bVar7) && (bVar9 = bVar4, (byte)(bVar3 - bVar7) != 1)) {
        if (bVar2 == bVar4) {
          bVar9 = bVar2;
          if (DAT_000aece0 <= (byte)(bVar3 - bVar7)) {
            cVar8 = -1;
            iVar5 = lookup_record_103_banked_code_word_b5f32(param_1,bVar2);
            uVar6 = 0x5a;
            if (iVar5 != 0) {
              uVar6 = 0;
            }
          }
        }
        else {
          bVar7 = bVar3 - 1;
        }
      }
    }
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb291u + (uint32_t)(iVar1) * 1u)))) = bVar7;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb292u + (uint32_t)(iVar1) * 1u)))) = bVar9;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb290u + (uint32_t)(iVar1) * 1u)))) = cVar8;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb293u + (uint32_t)(iVar1) * 1u)))) = uVar6;
  return;
}

void update_eight_empty_record_103_sequences_b628e(void)

{
  uint8_t stack_record_13[19];
  
  stack_record_13[0] = 1;
  stack_record_13[1] = 0;
  stack_record_13[2] = 0xff;
  update_record_103_channel_sequence_b61f4(0,((uint8_t *)(stack_record_13)), 0x1);
  stack_record_13[0] = 1;
  stack_record_13[1] = 0;
  stack_record_13[2] = 0xff;
  update_record_103_channel_sequence_b61f4(1,((uint8_t *)(stack_record_13)),2);
  stack_record_13[0] = 1;
  stack_record_13[1] = 0;
  stack_record_13[2] = 0xff;
  update_record_103_channel_sequence_b61f4(2,((uint8_t *)(stack_record_13)),4);
  stack_record_13[0] = 1;
  stack_record_13[1] = 0;
  stack_record_13[2] = 0xff;
  update_record_103_channel_sequence_b61f4(3,((uint8_t *)(stack_record_13)),8);
  stack_record_13[0] = 1;
  stack_record_13[1] = 0;
  stack_record_13[2] = 0xff;
  update_record_103_channel_sequence_b61f4(4,((uint8_t *)(stack_record_13)),0x10);
  stack_record_13[0] = 1;
  stack_record_13[1] = 0;
  stack_record_13[2] = 0xff;
  update_record_103_channel_sequence_b61f4(5,((uint8_t *)(stack_record_13)),0x20);
  stack_record_13[0] = 1;
  stack_record_13[1] = 0;
  stack_record_13[2] = 0xff;
  update_record_103_channel_sequence_b61f4(6,((uint8_t *)(stack_record_13)),0x40);
  stack_record_13[0] = 1;
  stack_record_13[1] = 0;
  stack_record_13[2] = 0xff;
  update_record_103_channel_sequence_b61f4(7,((uint8_t *)(stack_record_13)),0x80);
  return;
}

void select_record_103_sequence_update_mode_b6342(void)

{
  undefined1 uVar1;
  uint32_t puVar2;
  undefined1 uVar3;
  
  puVar2 = 0xfebeb800u;
  if (DAT_000aec5d == '\0') {
LAB_000b639c:
    uVar3 = 0x33;
    puVar2 = 0xfebeb800u;
    reset_eight_record_103_channel_sequences_b6160();
  }
  else {
    if (((char)DAT_febeb2d4 == '\x11') && (published_internal_source_admission_state == '\0')) {
      uVar1 = 0x11;
    }
    else {
      if ((DAT_febeb2ce != '\x11') ||
         (((DAT_febeb257 != '\0' || (DAT_febeb1c9 != 'Z')) ||
          (published_internal_source_admission_state != '\0')))) goto LAB_000b639c;
      uVar3 = 0x22;
      uVar1 = 0x22;
      if (DAT_febeb2cd != 'Z') goto LAB_000b63a4;
    }
    uVar3 = uVar1;
    puVar2 = 0xfebeb800u;
    update_eight_empty_record_103_sequences_b628e();
  }
LAB_000b63a4:
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x52f))))) = uVar3;
  return;
}

void stage_record_103_channel_snapshot_b63ac(char param_1)

{
  if (param_1 == '\x01') {
    DAT_febeb2b0 = 0xa55a5aa5;
    DAT_febeb2b8 = DAT_febeb292;
    DAT_febeb2b9 = DAT_febeb296;
    DAT_febeb2ba = DAT_febeb29a;
    DAT_febeb2bb = DAT_febeb29e;
    DAT_febeb2bc = DAT_febeb2a2;
    DAT_febeb2bd = DAT_febeb2a6;
    DAT_febeb2be = DAT_febeb2aa;
    DAT_febeb2bf = DAT_febeb2ae;
  }
  else {
    DAT_febeb2bf = 0xff;
    DAT_febeb2b8 = 0xff;
    DAT_febeb2b0 = 0;
    DAT_febeb2b9 = 0xff;
    DAT_febeb2ba = 0xff;
    DAT_febeb2bb = 0xff;
    DAT_febeb2bc = 0xff;
    DAT_febeb2bd = 0xff;
    DAT_febeb2be = 0xff;
  }
  DAT_febeb2b4 = 0;
  DAT_febeb2c8 = 0x11;
  return;
}

undefined2 finalize_record_103_channel_capture_b6414(undefined2 param_1)

{
  uint uVar1;
  uint32_t puVar2;
  byte bVar3;
  
  puVar2 = 0xfebeb800u;
  if (((byte)(DAT_febeb2ac & 0x80 |
             DAT_febeb2a8 & 0x40 |
             DAT_febeb2a4 & 0x20 |
             DAT_febeb2a0 & 0x10 |
             DAT_febeb29c & 8 | DAT_febeb298 & 4 | DAT_febeb294 & 2 | DAT_febeb290 & 1) == 0xff) ||
     (bVar3 = DAT_febeb2d2, DAT_febeb43c == 'Z')) {
    bVar3 = 0;
    uVar1 = 0;
    do {
      if ((((int8_t)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb290u + (uint32_t)(uVar1 * 4) * 1u))))) != -1) || ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb293u + (uint32_t)(uVar1 * 4) * 1u)))) != '\0')) {
        bVar3 = bVar3 | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xaec54u + (uint32_t)(uVar1) * 1u))));
      }
      uVar1 = uVar1 + 1;
    } while (uVar1 < 8);
    puVar2 = 0xfebeb800u;
    if (bVar3 == 0) {
      stage_record_103_channel_snapshot_b63ac(1);
      param_1 = 0x2211;
    }
    else {
      stage_record_103_channel_snapshot_b63ac(2);
      param_1 = 0x4411;
    }
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x52e))))) = bVar3;
  return param_1;
}

undefined ** finalize_record_103_write_status_b64c8(uint param_1)

{
  uint32_t puVar1;
  undefined1 uVar2;
  undefined **ppuVar3;
  
  puVar1 = 0xfebeb800u;
  ppuVar3 = ((undefined * *)camry_host_ptr((uint32_t)(param_1 & 0xffff)));
  uVar2 = DAT_febeb2d0;
  if (((DAT_febeb2c8 != '\0') && (DAT_febeb2c8 != '\x11')) && (DAT_febeb2c8 != '\"')) {
    puVar1 = 0xfebeb800u;
    if (DAT_febeb2c8 == 'D') {
      puVar1 = 0xfebeb800u;
      report_two_enabled_diagnostic_bits_b60d0(0,DAT_febeb2d2);
      report_two_enabled_diagnostic_bits_b60d0(2,0);
      uVar2 = 0;
      if ((int)camry_host_addr(ppuVar3) >> 8 == 0x22) {
        ppuVar3 = &PTR_LAB_00008822;
        goto LAB_000b6516;
      }
    }
    ppuVar3 = (undefined **)((undefined *)camry_host_ptr(0x8844u));
  }
LAB_000b6516:
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x530))))) = uVar2;
  return ppuVar3;
}

void advance_record_103_capture_status_b651e(void)

{
  int iVar1;
  uint32_t puVar2;
  ushort uVar3;
  
  puVar2 = 0xfebeb800u;
  iVar1 = (int)(uint)DAT_febeb2d4 >> 8;
  uVar3 = DAT_febeb2d4;
  if (iVar1 != 0) {
    if (iVar1 == 0x11) {
      puVar2 = 0xfebeb800u;
      uVar3 = finalize_record_103_channel_capture_b6414((*((volatile uint16_t *)camry_host_ptr(0xfebeb2d4u))));
    }
    else if ((iVar1 == 0x22) || (iVar1 == 0x44)) {
      puVar2 = 0xfebeb800u;
      uVar3 = camry_host_addr(finalize_record_103_write_status_b64c8((*((volatile uint16_t *)camry_host_ptr(0xfebeb2d4u)))));
    }
    else if (iVar1 != 0x88) {
      uVar3 = 0x8844;
    }
  }
  (*((ushort *)camry_host_ptr((uint32_t)(puVar2 + -0x52c)))) = uVar3;
  return;
}

void advance_record_103_staged_write_b655e(void)

{
  uint32_t puVar1;
  uint uVar2;
  char cVar3;
  
  cVar3 = DAT_febeb2c8;
  puVar1 = 0xfebeb800u;
  if (DAT_febeb2c8 == '\x11') {
    if ((DAT_febeb2c9 != '\"') && (DAT_febeb2ca != '\"')) {
      puVar1 = 0xfebeb800u;
      call_nvm_set_record_with_u16_selector_ff09c(0x103,((undefined *)camry_host_ptr(0xfebeb2b0u)));
      cVar3 = '\"';
    }
  }
  else if (DAT_febeb2c8 == '\"') {
    puVar1 = 0xfebeb800u;
    uVar2 = call_nvm_record_status_with_u16_selector_ff0c4(0x103);
    if (uVar2 == 0x10) {
      cVar3 = 'D';
      load_record_103_codes_and_intersect_masks_b5f76();
    }
    else if ((uVar2 & 0xf0) != 0x20) {
      cVar3 = -0x78;
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x533))))) = 0xff;
    }
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x538))))) = cVar3;
  return;
}

uint write_invalid_record_103_b65ca(void)

{
  uint8_t stack_record_14[20];
  
  (*((uint32_t *)(stack_record_14 + 4))) = 0;
  (*((uint32_t *)(stack_record_14 + 0))) = 0;
  stack_record_14[15] = 0xff;
  stack_record_14[14] = 0xff;
  stack_record_14[13] = 0xff;
  stack_record_14[12] = 0xff;
  stack_record_14[11] = 0xff;
  stack_record_14[10] = 0xff;
  stack_record_14[9] = 0xff;
  stack_record_14[8] = 0xff;
  return call_nvm_set_record_with_u16_selector_ff09c(0x103,stack_record_14);
}

void clear_record_103_diagnostic_banks_and_sequences_b65f4(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  report_two_enabled_diagnostic_bits_b60d0(0,0);
  report_two_enabled_diagnostic_bits_b60d0(1,0);
  report_two_enabled_diagnostic_bits_b60d0(2,0);
  report_two_enabled_diagnostic_bits_b60d0(3,0);
  reset_eight_record_103_channel_sequences_b6160();
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x530))))) = 0;
  return;
}

void reset_record_103_codes_and_lookup_masks_b6624(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  
  DAT_febeb2c0 = 0xff;
  DAT_febeb2c1 = 0xff;
  DAT_febeb2c2 = 0xff;
  DAT_febeb2c3 = 0xff;
  DAT_febeb2c4 = 0xff;
  DAT_febeb2c5 = 0xff;
  DAT_febeb2c6 = 0xff;
  DAT_febeb2c7 = 0xff;
  DAT_febeb2cd = 0x33;
  iVar3 = 0;
  do {
    iVar2 = iVar3 + 1;
    *(undefined4 *)(((undefined *)camry_host_ptr((uint32_t)(0xfebeb2d8u + (uint32_t)(iVar3 * 4) * 1u)))) = 0;
    iVar1 = iVar3 + -7;
    iVar3 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  DAT_febeb2f8 = 0;
  return;
}

void monitor_routine_1009_record103_reset(void)

{
  uint32_t puVar1;
  uint uVar2;
  char cVar3;
  
  cVar3 = DAT_febeb2c9;
  puVar1 = 0xfebeb800u;
  if (DAT_febeb2c9 == '\x11') {
    if ((DAT_febeb2c8 != '\"') && (DAT_febeb2ca != '\"')) {
      puVar1 = 0xfebeb800u;
      write_invalid_record_103_b65ca();
      cVar3 = '\"';
    }
  }
  else if (DAT_febeb2c9 == '\"') {
    puVar1 = 0xfebeb800u;
    uVar2 = call_nvm_record_status_with_u16_selector_ff0c4(0x103);
    if (uVar2 == 0x10) {
      cVar3 = 'D';
      clear_record_103_diagnostic_banks_and_sequences_b65f4();
      thunk_publish_routine_or_pending_write_terminal_result_4d0a4(6,0);
      reset_record_103_codes_and_lookup_masks_b6624();
    }
    else if ((uVar2 & 0xf0) != 0x20) {
      cVar3 = -0x78;
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x533))))) = 0xff;
      thunk_publish_routine_or_pending_write_terminal_result_4d0a4(6,0x20);
    }
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x537))))) = cVar3;
  return;
}

void submit_staged_record103_byte_write(void)

{
  uint8_t stack_record_14[20];
  
  stack_record_14[8] = DAT_febeb2c0;
  stack_record_14[9] = DAT_febeb2c1;
  stack_record_14[10] = DAT_febeb2c2;
  stack_record_14[11] = DAT_febeb2c3;
  stack_record_14[12] = DAT_febeb2c4;
  stack_record_14[13] = DAT_febeb2c5;
  stack_record_14[14] = DAT_febeb2c6;
  stack_record_14[15] = DAT_febeb2c7;
  switch(DAT_febeb2cc) {
  case 1:
    stack_record_14[8] = DAT_febeb2cb;
    break;
  case 2:
    stack_record_14[9] = DAT_febeb2cb;
    break;
  case 3:
    stack_record_14[10] = DAT_febeb2cb;
    break;
  case 4:
    stack_record_14[11] = DAT_febeb2cb;
    break;
  case 5:
    stack_record_14[12] = DAT_febeb2cb;
    break;
  case 6:
    stack_record_14[13] = DAT_febeb2cb;
    break;
  case 7:
    stack_record_14[14] = DAT_febeb2cb;
    break;
  case 8:
    stack_record_14[15] = DAT_febeb2cb;
  }
  (*((uint32_t *)(stack_record_14 + 0))) = 0xa55a5aa5;
  (*((uint32_t *)(stack_record_14 + 4))) = 0;
  call_nvm_set_record_with_u16_selector_ff09c(0x103,stack_record_14);
  return;
}

void service_record103_byte_write(void)

{
  uint32_t puVar1;
  uint uVar2;
  char cVar3;
  
  cVar3 = DAT_febeb2ca;
  puVar1 = 0xfebeb800u;
  if (DAT_febeb2ca == '\x11') {
    if ((DAT_febeb2c8 != '\"') && (DAT_febeb2c9 != '\"')) {
      puVar1 = 0xfebeb800u;
      submit_staged_record103_byte_write();
      cVar3 = '\"';
    }
  }
  else if (DAT_febeb2ca == '\"') {
    puVar1 = 0xfebeb800u;
    uVar2 = call_nvm_record_status_with_u16_selector_ff0c4(0x103);
    if (uVar2 == 0x10) {
      cVar3 = 'D';
      clear_record_103_diagnostic_banks_and_sequences_b65f4();
      thunk_publish_routine_or_pending_write_terminal_result_4d0a4(0x15,0);
      load_record_103_codes_and_intersect_masks_b5f76();
    }
    else if ((uVar2 & 0xf0) != 0x20) {
      cVar3 = -0x78;
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x533))))) = 0xff;
      thunk_publish_routine_or_pending_write_terminal_result_4d0a4(0x15,0x20);
    }
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x536))))) = cVar3;
  return;
}

void compare_record_103_codes_and_report_bank_two_b67cc(void)

{
  int iVar1;
  byte bVar2;
  char cVar3;
  uint uVar4;
  uint32_t puVar5;
  undefined1 uVar6;
  byte bVar7;
  byte bVar8;
  char local_18 [8];
  
  bVar2 = DAT_000aec5c;
  puVar5 = 0xfebeb800u;
  uVar6 = DAT_febeb2d0;
  cVar3 = DAT_febeb2ce;
  bVar8 = DAT_febeb2cf;
  if (DAT_febeb2ce != '\x11') goto LAB_000b68fc;
  if (DAT_febeb257 == 'Z') {
    bVar8 = 0;
    puVar5 = 0xfebeb800u;
  }
  else {
    bVar7 = DAT_febeb2ac & 0x80 |
            DAT_febeb2a8 & 0x40 |
            DAT_febeb2a4 & 0x20 |
            DAT_febeb2a0 & 0x10 |
            DAT_febeb29c & 8 | DAT_febeb298 & 4 | DAT_febeb294 & 2 | DAT_febeb290 & 1;
    if (DAT_febeb2cd != 'Z') {
      puVar5 = 0xfebeb800u;
      report_two_enabled_diagnostic_bits_b60d0(2,DAT_000aec5c);
      uVar6 = 0x22;
      cVar3 = 'D';
      bVar8 = bVar2;
      goto LAB_000b68fc;
    }
    if ((bVar7 != 0xff) && (DAT_febeb43d != 'Z')) goto LAB_000b68fc;
    bVar8 = 0;
    local_18[0] = DAT_febeb2c0;
    local_18[1] = DAT_febeb2c1;
    local_18[2] = DAT_febeb2c2;
    local_18[3] = DAT_febeb2c3;
    local_18[4] = DAT_febeb2c4;
    local_18[5] = DAT_febeb2c5;
    local_18[6] = DAT_febeb2c6;
    local_18[7] = DAT_febeb2c7;
    uVar4 = 0;
    do {
      iVar1 = uVar4 * 4;
      if (((((int8_t)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb290u + (uint32_t)(iVar1) * 1u))))) != -1) || ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb293u + (uint32_t)(iVar1) * 1u)))) != '\0')) ||
         ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb292u + (uint32_t)(iVar1) * 1u)))) != local_18[uVar4])) {
        bVar8 = bVar8 | (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xaec54u + (uint32_t)(uVar4) * 1u))));
      }
      uVar4 = uVar4 + 1;
    } while (uVar4 < 8);
    puVar5 = 0xfebeb800u;
    report_two_enabled_diagnostic_bits_b60d0(2,bVar8);
    uVar6 = 0x22;
    if (bVar8 == 0) {
      uVar6 = 0x11;
    }
    cVar3 = 'D';
    if (bVar7 != 0xff) goto LAB_000b68fc;
  }
  cVar3 = '\"';
LAB_000b68fc:
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x532))))) = cVar3;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x531))))) = bVar8;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x530))))) = uVar6;
  return;
}

void run_init_chain_b690a(void)

{
  select_record_103_sequence_update_mode_b6342();
  advance_record_103_capture_status_b651e();
  advance_record_103_staged_write_b655e();
  monitor_routine_1009_record103_reset();
  service_record103_byte_write();
  compare_record_103_codes_and_report_bank_two_b67cc();
  return;
}

void cancel_pending_record_103_comparison_b692a(void)

{
  bool bVar1;
  
  bVar1 = DAT_febeb2ce == '\x11';
  if (bVar1) {
    DAT_febeb2ce = '\0';
  }
  if (bVar1) {
    DAT_febeb2cf = 0xff;
  }
  return;
}

void start_record_103_channel_capture_b6944(void)

{
  bool bVar1;
  char cVar2;
  uint32_t puVar3;
  undefined1 uVar4;
  undefined1 uVar5;
  ushort uVar6;
  
  puVar3 = 0xfebeb800u;
  uVar4 = DAT_febeb2d2;
  uVar5 = DAT_febeb2cd;
  if (DAT_000aec5d == '\0') {
    uVar6 = 0x8822;
  }
  else if (((int)(uint)DAT_febeb2d4 >> 8 == 0) ||
          (uVar6 = DAT_febeb2d4, (int)(uint)DAT_febeb2d4 >> 8 == 0x88)) {
    uVar6 = 0x1111;
    puVar3 = 0xfebeb800u;
    reset_eight_record_103_channel_sequences_b6160();
    cVar2 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x532)))));
    uVar4 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x531)))));
    bVar1 = cVar2 == '\x11';
    if (bVar1) {
      cVar2 = '\0';
    }
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x532))))) = cVar2;
    if (bVar1) {
      uVar4 = 0xff;
    }
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x531))))) = uVar4;
    uVar4 = 0;
    uVar5 = 0;
  }
  (*((ushort *)camry_host_ptr((uint32_t)(puVar3 + -0x52c)))) = uVar6;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x52e))))) = uVar4;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x533))))) = uVar5;
  return;
}

void finish_pending_record_103_capture_b6990(void)

{
  if ((int)(uint)DAT_febeb2d4 >> 8 == 0x11) {
    DAT_febeb2d4 = 0x8822;
  }
  return;
}

void stage_record103_byte_write(uchar selector,uchar value)

{
  bool bVar1;
  
  if ((int)(uint)DAT_febeb2d4 >> 8 == 0x11) {
    DAT_febeb2d4 = 0x8822;
  }
  bVar1 = DAT_febeb2ce == '\x11';
  if (bVar1) {
    DAT_febeb2ce = '\0';
  }
  if (bVar1) {
    DAT_febeb2cf = 0xff;
  }
  DAT_febeb2ca = 0x11;
  DAT_febeb2cc = selector;
  DAT_febeb2cb = value;
  return;
}

void prepare_record_103_invalid_write_b69c6(void)

{
  bool bVar1;
  
  if ((int)(uint)DAT_febeb2d4 >> 8 == 0x11) {
    DAT_febeb2d4 = 0x8822;
  }
  bVar1 = DAT_febeb2ce == '\x11';
  if (bVar1) {
    DAT_febeb2ce = '\0';
  }
  if (bVar1) {
    DAT_febeb2cf = 0xff;
  }
  DAT_febeb2c9 = 0x11;
  return;
}

void start_or_bypass_record_103_comparison_b69de(void)

{
  char cVar1;
  uint32_t puVar2;
  undefined1 uVar3;
  
  puVar2 = 0xfebeb800u;
  uVar3 = DAT_febeb2cf;
  if (DAT_000aec5d == '\0') {
    cVar1 = '\"';
  }
  else {
    cVar1 = DAT_febeb2ce;
    if (DAT_febeb2ce != '\x11') {
      if ((char)DAT_febeb2d4 == '\x11') {
        cVar1 = 'D';
      }
      else {
        puVar2 = 0xfebeb800u;
        reset_eight_record_103_channel_sequences_b6160();
        cVar1 = '\x11';
        uVar3 = 0;
      }
    }
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x532))))) = cVar1;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x531))))) = uVar3;
  return;
}

undefined1 get_record_103_enabled_channel_mask_b6a28(void)

{
  return DAT_000aec5d;
}

void clear_b302_status_b6a32(void)

{
  DAT_febeb302 = 0;
  return;
}

void snapshot_f055_into_b2fe_b6a38(void)

{
  DAT_febeb2fe = DAT_febef055;
  return;
}

void update_b301_from_b314_and_admission_b6a42(void)

{
  if (((DAT_febeb314 == 0) || (DAT_febeb314 == 0x33333333)) || (DAT_febeb314 == -1)) {
    DAT_febeb301 = 0;
    if (DAT_febeb2fc == 1) {
      DAT_febeb2fc = 2;
      DAT_febeb302 = 0x44;
    }
  }
  else if ((DAT_febeb2fc < 2) && (published_internal_source_admission_state < 2)) {
    DAT_febeb301 = 0x5a;
  }
  else {
    DAT_febeb301 = 0;
  }
  return;
}

void count_changed_f055_with_stable_be88_b6a8a(void)

{
  if ((DAT_febeb301 == 'Z') && (DAT_febebe89 == '\0')) {
    if (DAT_febeb2fe != DAT_febef055) {
      if (DAT_febeb2fd == 0) {
        DAT_febeb2fd = DAT_000aef50 != 0;
        DAT_febeb2ff = DAT_febebe88;
      }
      else if (DAT_febeb2ff == DAT_febebe88) {
        if (DAT_febeb2fd < DAT_000aef50) {
          DAT_febeb2fd = DAT_febeb2fd + 1;
        }
      }
      else {
        DAT_febeb2fd = 1;
        DAT_febeb2ff = DAT_febebe88;
      }
    }
  }
  else {
    DAT_febeb2fd = 0;
  }
  DAT_febeb2fe = DAT_febef055;
  return;
}

void evaluate_event_100_marker_consistency_b6ae0(void)

{
  uint32_t puVar1;
  uint uVar2;
  undefined1 uVar3;
  undefined1 uVar4;
  char cVar5;
  
  uVar3 = DAT_febeb302;
  cVar5 = DAT_febeb2fc;
  puVar1 = 0xfebeb800u;
  if (DAT_febeb2fd < DAT_000aef50) {
    uVar4 = DAT_febeb300;
    if ((DAT_febeb2fc != '\x01') || (DAT_febeb43d != 'Z')) goto LAB_000b6b8c;
    uVar4 = 0x22;
    puVar1 = 0xfebeb800u;
    thunk_route_event_failure_by_e85a_mode_51d38(0x100,0x14,100);
    uVar3 = 0x44;
  }
  else {
    puVar1 = 0xfebeb800u;
    if (((DAT_febeb314 == -0x55aaaa56) && (DAT_febeb2ff != 'Z')) ||
       ((DAT_febeb314 == 0x55aaaa55 && (DAT_febeb2ff != '\0')))) {
      uVar4 = 0x22;
      thunk_route_event_failure_by_e85a_mode_51d38(0x100,0x14,100);
    }
    else {
      if (DAT_febeb2fc == '\x01') {
        puVar1 = 0xfebeb800u;
        uVar2 = get_diagnostic_event_state(0x100);
        if ((uVar2 & 1) != 0) {
          report_diagnostic_event_pass(0x100);
        }
        thunk_clear_event_bit_from_three_bitmaps_and_mark_dirty_524be(0x100);
      }
      uVar4 = 0x11;
    }
    if (cVar5 == '\x01') {
      uVar3 = 0x22;
    }
  }
  cVar5 = '\x02';
LAB_000b6b8c:
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x4fe))))) = uVar3;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x500))))) = uVar4;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x504))))) = cVar5;
  return;
}

void update_event_100_change_monitor_b6b9a(void)

{
  update_b301_from_b314_and_admission_b6a42();
  count_changed_f055_with_stable_be88_b6a8a();
  evaluate_event_100_marker_consistency_b6ae0();
  return;
}

void clear_event_100_and_reset_monitor_b6bae(void)

{
  char cVar1;
  uint32_t puVar2;
  uint uVar3;
  
  cVar1 = DAT_febeb2fc;
  puVar2 = 0xfebeb800u;
  uVar3 = get_diagnostic_event_state(0x100);
  if ((uVar3 & 1) != 0) {
    report_diagnostic_event_pass(0x100);
  }
  thunk_clear_event_bit_from_three_bitmaps_and_mark_dirty_524be(0x100);
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x503))))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x500))))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x504))))) = cVar1 == '\x01';
  return;
}

void start_event_100_monitor_b6be6(void)

{
  if ((DAT_febeb302 != '\x11') && (DAT_febeb302 = 'D', (char)DAT_febeb324 != '\x11')) {
    DAT_febeb302 = '\x11';
    DAT_febeb2fc = 1;
    DAT_febeb2fd = 0;
  }
  return;
}

void stop_event_100_monitor_b6c14(void)

{
  if (DAT_febeb2fc == '\x01') {
    DAT_febeb302 = 0;
  }
  DAT_febeb2fc = 2;
  return;
}

void return_only_stub_b6c28(void)

{
  return;
}

void snapshot_f055_into_b305_b6c2a(void)

{
  DAT_febeb305 = DAT_febef055;
  return;
}

void count_b30a_and_latch_timeout_b6c34(void)

{
  if (DAT_febeb30a < DAT_000aef56) {
    DAT_febeb30a = DAT_febeb30a + 1;
  }
  else {
    DAT_febeb309 = 0x5a;
  }
  return;
}

void count_b305_input_changes_with_stable_be88_b6c56(char param_1)

{
  if ((((DAT_febeb314 == 0) || (DAT_febeb314 == 0x33333333)) || (DAT_febeb314 == -1)) ||
     (1 < published_internal_source_admission_state)) {
    DAT_febeb308 = 0;
  }
  else {
    DAT_febeb308 = 0x5a;
    if (DAT_febebe89 == '\0') {
      if (DAT_febeb305 == param_1) {
        DAT_febeb308 = 0x5a;
        return;
      }
      if (DAT_febeb304 == 0) {
        DAT_febeb304 = DAT_000aef54 != 0;
        DAT_febeb306 = DAT_febebe88;
        DAT_febeb308 = 0x5a;
        return;
      }
      if (DAT_febeb306 != DAT_febebe88) {
        DAT_febeb304 = 1;
        DAT_febeb306 = DAT_febebe88;
        DAT_febeb308 = 0x5a;
        return;
      }
      if (DAT_000aef54 <= DAT_febeb304) {
        DAT_febeb308 = 0x5a;
        return;
      }
      DAT_febeb304 = DAT_febeb304 + 1;
      DAT_febeb308 = 0x5a;
      return;
    }
  }
  DAT_febeb304 = 0;
  return;
}

void classify_b314_against_stable_be88_b6cc8(void)

{
  if (DAT_febeb304 < DAT_000aef54) {
    if (DAT_febeb309 != 'Z') {
      return;
    }
  }
  else {
    if ((DAT_febeb314 == -0x55aaaa56) && (DAT_febeb306 == 'Z')) {
      DAT_febeb307 = 0;
      DAT_febeb30c = 0xaa5555aa;
      return;
    }
    if ((DAT_febeb314 == 0x55aaaa55) && (DAT_febeb306 == '\0')) {
      DAT_febeb307 = 0;
      DAT_febeb30c = 0x55aaaa55;
      return;
    }
  }
  DAT_febeb307 = 0x5a;
  return;
}

void update_b30c_marker_acquisition_b6d20(void)

{
  undefined1 uVar1;
  uint32_t puVar2;
  uVar1 = DAT_febef055;
  puVar2 = 0xfebeb800u;
  if ((DAT_febeb30c == -0x55aaaa56) || (DAT_febeb30c == 0x55aaaa55)) {
    DAT_febeb309 = 0;
    DAT_febeb30a = 0;
  }
  else {
    puVar2 = 0xfebeb800u;
    count_b30a_and_latch_timeout_b6c34();
    count_b305_input_changes_with_stable_be88_b6c56(uVar1);
    classify_b314_against_stable_be88_b6cc8();
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x4fb))))) = uVar1;
  return;
}

void fill_constant_block_b6d60(void)

{
  DAT_febeb309 = 0;
  DAT_febeb30a = 0;
  DAT_febeb304 = 0;
  DAT_febeb307 = 0;
  DAT_febeb30c = 0;
  return;
}

void return_only_stub_b6d70(void)

{
  return;
}

void load_record_102_marker_and_report_b6d72(void)

{
  uint32_t puVar1;
  int iVar2;
  int local_10 [2];
  
  puVar1 = 0xfebeb800u;
  iVar2 = call_nvm_get_record_with_u16_selector_ff0b0(0x102,local_10);
  if (iVar2 == 0x10) {
    report_diagnostic_healthy_observed(0x12a);
    if ((local_10[0] != 0) && ((local_10[0] == 0x55aaaa55 || (local_10[0] == -0x55aaaa56)))) {
      report_diagnostic_event_pass(0xff);
      thunk_clear_event_bit_from_three_bitmaps_and_mark_dirty_524be(0x14d);
      iVar2 = local_10[0];
      goto LAB_000b6de6;
    }
  }
  else if (iVar2 != 0x11) {
    iVar2 = -1;
    report_diagnostic_event_failure(0x12a,100);
    goto LAB_000b6de6;
  }
  iVar2 = 0x33333333;
  thunk_route_event_failure_by_e85a_mode_51d38(0xff,0xd,100);
LAB_000b6de6:
  (*((int *)camry_host_ptr((uint32_t)(puVar1 + -0x4ec)))) = iVar2;
  return;
}

void thunk_load_record_102_marker_and_report_b6d72(void)

{
  load_record_102_marker_and_report_b6d72();
  return;
}

int refresh_record_102_marker_without_diagnostics_b6dfa(void)

{
  uint32_t puVar1;
  int iVar2;
  int iVar3;
  int local_10 [2];
  
  iVar3 = DAT_febeb314;
  puVar1 = 0xfebeb800u;
  iVar2 = call_nvm_get_record_with_u16_selector_ff0b0(0x102,local_10);
  if ((iVar2 == 0x10) &&
     ((local_10[0] == 0 ||
      ((iVar3 = local_10[0], local_10[0] != 0x55aaaa55 && (local_10[0] != -0x55aaaa56)))))) {
    iVar3 = 0x33333333;
  }
  (*((int *)camry_host_ptr((uint32_t)(puVar1 + -0x4ec)))) = iVar3;
  return iVar2;
}

uint write_record_102_from_b318_b6e3c(void)

{
  uint8_t stack_record_c[12];
  
  (*((uint32_t *)(stack_record_c + 4))) = 0;
  (*((uint32_t *)(stack_record_c + 0))) = DAT_febeb318;
  return call_nvm_set_record_with_u16_selector_ff09c(0x102,stack_record_c);
}

void advance_record_102_b318_write_b6e58(void)

{
  int iVar1;
  uint32_t puVar2;
  uint uVar3;
  char cVar4;
  
  iVar1 = DAT_febeb318;
  cVar4 = DAT_febeb310;
  puVar2 = 0xfebeb800u;
  if (DAT_febeb310 == '\x11') {
    if ((DAT_febeb311 != '\"') && (DAT_febeb312 != '\"')) {
      puVar2 = 0xfebeb800u;
      write_record_102_from_b318_b6e3c();
      cVar4 = '\"';
    }
  }
  else if (DAT_febeb310 == '\"') {
    puVar2 = 0xfebeb800u;
    uVar3 = call_nvm_record_status_with_u16_selector_ff0c4(0x102);
    if (uVar3 == 0x10) {
      cVar4 = 'D';
      if ((iVar1 == 0x55aaaa55) || (iVar1 == -0x55aaaa56)) {
        report_diagnostic_event_pass(0xff);
        thunk_clear_event_bit_from_three_bitmaps_and_mark_dirty_524be(0x14d);
      }
      else {
        thunk_route_event_failure_by_e85a_mode_51d38(0xff,0xd,100);
        thunk_route_event_failure_by_e85a_mode_51d38(0x14d,0x14,100);
      }
      fill_constant_block_b6d60();
      clear_event_100_and_reset_monitor_b6bae();
    }
    else if ((uVar3 & 0xf0) != 0x20) {
      cVar4 = -0x78;
      report_diagnostic_event_failure(0x132,100);
    }
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x4f0))))) = cVar4;
  return;
}

uint write_zero_record_102_b6f0c(void)

{
  uint8_t stack_record_c[12];
  
  (*((uint32_t *)(stack_record_c + 0))) = 0;
  (*((uint32_t *)(stack_record_c + 4))) = 0;
  return call_nvm_set_record_with_u16_selector_ff09c(0x102,stack_record_c);
}

void advance_record_102_zero_write_b6f24(void)

{
  uint32_t puVar1;
  uint uVar2;
  char cVar3;
  
  cVar3 = DAT_febeb311;
  puVar1 = 0xfebeb800u;
  if (DAT_febeb311 == '\x11') {
    if ((DAT_febeb310 != '\"') && (DAT_febeb312 != '\"')) {
      puVar1 = 0xfebeb800u;
      write_zero_record_102_b6f0c();
      cVar3 = '\"';
    }
  }
  else if (DAT_febeb311 == '\"') {
    puVar1 = 0xfebeb800u;
    uVar2 = call_nvm_record_status_with_u16_selector_ff0c4(0x102);
    if (uVar2 == 0x10) {
      cVar3 = 'D';
      thunk_route_event_failure_by_e85a_mode_51d38(0xff,0xd,100);
      thunk_clear_event_bit_from_three_bitmaps_and_mark_dirty_524be(0x14d);
      fill_constant_block_b6d60();
      clear_event_100_and_reset_monitor_b6bae();
    }
    else if ((uVar2 & 0xf0) != 0x20) {
      cVar3 = -0x78;
      report_diagnostic_event_failure(0x132,100);
    }
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x4ef))))) = cVar3;
  return;
}

uint write_record_102_from_b31c_b6fa8(void)

{
  uint8_t stack_record_c[12];
  
  (*((uint32_t *)(stack_record_c + 4))) = 0;
  (*((uint32_t *)(stack_record_c + 0))) = DAT_febeb31c;
  return call_nvm_set_record_with_u16_selector_ff09c(0x102,stack_record_c);
}

void advance_record_102_b31c_write_b6fc4(void)

{
  uint32_t puVar1;
  undefined4 uVar2;
  uint uVar3;
  char cVar4;
  
  cVar4 = DAT_febeb312;
  puVar1 = 0xfebeb800u;
  if (DAT_febeb312 == '\x11') {
    if ((DAT_febeb310 != '\"') && (DAT_febeb311 != '\"')) {
      puVar1 = 0xfebeb800u;
      write_record_102_from_b31c_b6fa8();
      cVar4 = '\"';
    }
  }
  else if (DAT_febeb312 == '\"') {
    puVar1 = 0xfebeb800u;
    uVar3 = call_nvm_record_status_with_u16_selector_ff0c4(0x102);
    if (uVar3 == 0x10) {
      cVar4 = 'D';
      report_diagnostic_event_pass(0xff);
      thunk_clear_event_bit_from_three_bitmaps_and_mark_dirty_524be(0x14d);
      fill_constant_block_b6d60();
      clear_event_100_and_reset_monitor_b6bae();
      uVar2 = 0;
    }
    else {
      if ((uVar3 & 0xf0) == 0x20) goto LAB_000b704c;
      cVar4 = -0x78;
      report_diagnostic_event_failure(0x132,100);
      uVar2 = 0x20;
    }
    thunk_publish_routine_or_pending_write_terminal_result_4d0a4(0x14,uVar2);
  }
LAB_000b704c:
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x4ee))))) = cVar4;
  return;
}
