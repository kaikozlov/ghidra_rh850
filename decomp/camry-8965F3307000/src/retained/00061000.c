#include "common.h"

void copy_serial_fifo_words(uchar channel,ushort *output,uchar offset,uchar count)

{
  uint uVar1;
  uint uVar2;
  uint32_t puVar3;
  
  uVar2 = (uint)offset;
  if (channel < 2) {
    puVar3 = (*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x313fcu + (uint32_t)(channel) * 4u))));
    uVar1 = (uint)(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x31411u + (uint32_t)((short)(ushort)channel * 0x50) * 1u)))) - (uint)count;
    if ((int)(uVar2 - uVar1) < 0 != ((int)uVar1 < 0 && (int)uVar1 < 0 == (int)(uVar2 - uVar1) < 0)
        || uVar2 == uVar1) {
      for (uVar1 = 0; uVar1 < count; uVar1 = uVar1 + 1 & 0xff) {
        output[uVar1] = (*((ushort *)camry_host_ptr((uint32_t)(puVar3 + (uVar2 + uVar1) * 2))));
      }
    }
  }
  return;
}

void read_serial_controller_status
               (uchar channel,ushort acknowledgment,F33SerialControllerStatus *output)

{
  int iVar1;
  undefined4 uVar2;
  undefined4 uVar3;
  uint uVar4;
  
  if (channel < 2) {
    iVar1 = (uint)(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x3140cu + (uint32_t)((short)(ushort)channel * 0x50) * 1u)))) * 0x2000;
    uVar4 = (*((uint *)camry_host_ptr((uint32_t)(iVar1 + -0x27fffc))));
    uVar2 = (*((undefined4 *)camry_host_ptr((uint32_t)(iVar1 + -0x27effc))));
    uVar3 = (*((undefined4 *)camry_host_ptr((uint32_t)(iVar1 + -0x27efe8))));
    output->status_bit8 = (byte)(uVar4 >> 8) & 1;
    output->status_bit7 = (uchar)((uVar4 & 0x80) >> 7);
    output->status_bit3 = (uchar)((uVar4 & 8) >> 3);
    output->count0_7bit = (byte)uVar2 & 0x7f;
    output->count1_7bit = (byte)((uint)uVar3 >> 0x10) & 0x7f;
    output->count2_7bit = (byte)uVar3 & 0x7f;
    (*((ushort *)camry_host_ptr((uint32_t)(iVar1 + -0x27fff8)))) = acknowledgment & 0x100 | (ushort)(uVar4 & 8);
  }
  return;
}

void return_only_stub_610bc(void)

{
  return;
}

void set_byte_fold_control_22_611ee(void)

{
  DAT_ffd50020 = 0x22;
  return;
}

uint fold_seven_big_endian_bytes_through_register_611fa(ushort *param_1)

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

void initialize_four_halfword_serial_frame_registers_61260(void)

{
  uint uVar1;
  
  DAT_ffd82000 = 0;
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
  uVar1 = Ramffc120f8;
  Ramffc120f8 = uVar1 & 0xfff2ef88 | 0x50;
  uVar1 = Ramffc12100;
  Ramffc12100 = uVar1 & 0xfff2ef88 | 0x1060;
  uVar1 = Ramffc12104;
  Ramffc12104 = uVar1 & 0xfff2ef88 | 0x1060;
  return;
}

uint restore_serial_pin_mux_under_priority_mask_612dc(void)

{
  uint uVar1;
  uint saved_mask;
  
  saved_mask = priority_mask_enter(0xffc0);
  uVar1 = Ramffc120f8;
  Ramffc120f8 = uVar1 & 0xfff2ff88 | 0x50;
  uVar1 = Ramffc12100;
  Ramffc12100 = uVar1 & 0xfff2ff88 | 0x60;
  uVar1 = Ramffc12104;
  Ramffc12104 = uVar1 & 0xfff2ff88 | 0x60;
  priority_mask_restore(saved_mask);
  return saved_mask;
}

undefined * receive_four_serial_halfwords_if_ready_6131c(undefined2 *param_1)

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

undefined4 transmit_four_tagged_serial_halfwords_if_idle_61372(ushort *param_1)

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

ushort initialize_serial_receive_frame_and_check_byte_613c8(void)

{
  uint32_t puVar1;
  ushort uVar2;
  
  puVar1 = 0xfebeb800u;
  (*((volatile uint16_t *)camry_host_ptr(0xfebe3838u))) = 0x6400;
  DAT_febe383a = 0;
  DAT_febe383c = 0xf000;
  DAT_febe383e = 0;
  uVar2 = fold_seven_big_endian_bytes_through_register_611fa(((undefined *)camry_host_ptr(0xfebe3838u)));
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x7fcc)))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x7fc0))))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x7fca))))) = 0;
  (*((ushort *)camry_host_ptr((uint32_t)(puVar1 + -0x7fc2)))) = (*((ushort *)camry_host_ptr((uint32_t)(puVar1 + -0x7fc2)))) & 0xff00 | uVar2;
  return uVar2;
}

void update_local_status_packet(void)

{
  ushort uVar1;
  uint32_t puVar2;
  int iVar3;
  uint uVar4;
  char cVar5;
  char cVar6;
  
  puVar2 = 0xfebeb800u;
  if (DAT_febe389e == 'Z') {
    iVar3 = camry_host_addr(receive_four_serial_halfwords_if_ready_6131c(((undefined *)camry_host_ptr(0xfebe382cu))));
    cVar6 = 'D';
    if (iVar3 == 0) {
      uVar4 = fold_seven_big_endian_bytes_through_register_611fa(((undefined *)camry_host_ptr((uint32_t)(puVar2 + -0x7fd4))));
      if ((byte)(*((undefined2 *)camry_host_ptr((uint32_t)(puVar2 + -0x7fce)))) == uVar4) {
        uVar1 = (*((ushort *)camry_host_ptr((uint32_t)(puVar2 + -0x7fd4)))) & 0xe000;
        if (uVar1 == 0x6000) {
          (*((ushort *)camry_host_ptr((uint32_t)(puVar2 + -0x7fc8)))) = (*((ushort *)camry_host_ptr((uint32_t)(puVar2 + -0x7fd4))));
          (*((undefined2 *)camry_host_ptr((uint32_t)(puVar2 + -0x7fc2)))) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar2 + -0x7fce))));
          cVar6 = '\0';
          (*((undefined2 *)camry_host_ptr((uint32_t)(puVar2 + -0x7fc6)))) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar2 + -0x7fd2))));
          (*((undefined2 *)camry_host_ptr((uint32_t)(puVar2 + -0x7fc4)))) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar2 + -0x7fd0))));
        }
        else {
          cVar6 = '3';
          if (uVar1 == 0x8000) {
            cVar6 = '\"';
          }
        }
      }
      else {
        cVar6 = '\x11';
      }
    }
    cVar5 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x7fc0)))));
    uVar1 = (*((ushort *)camry_host_ptr((uint32_t)(puVar2 + -0x7fcc))));
    if (cVar5 != 'Z') {
      if (cVar6 == '\0') {
        uVar1 = 0;
        cVar5 = '\0';
      }
      else if ((DAT_000315c8 <= uVar1) || (uVar1 = uVar1 + 1, DAT_000315c8 <= uVar1)) {
        cVar5 = 'Z';
      }
    }
    (*((ushort *)camry_host_ptr((uint32_t)(puVar2 + -0x7fcc)))) = uVar1;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x7fc0))))) = cVar5;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x7fca))))) = cVar6;
  }
  return;
}

byte pack_receive_frame_top_three_bits_614b0(void)

{
  return (DAT_febe383e >> 0xd & 1) != 0 | ((DAT_febe383e >> 0xe & 1) != 0) << 1 |
         ((short)DAT_febe383e < 0) << 2;
}

uint32_t poll_serial_frame_and_accept_matching_check_byte_614d4(void)

{
  uint32_t camry_r10_result;
  uint8_t stack_record_14[20];
  int iVar1;
  undefined8 uVar2;
  int iVar3;
  uint uVar4;
  byte bVar5;
  
  uVar2 = 0xfebeb800;
  bVar5 = 0;
  do {
    iVar3 = (camry_r10_result = camry_host_addr(receive_four_serial_halfwords_if_ready_6131c(stack_record_14)));
    spin_wait(1);
    iVar1 = (int)uVar2;
    if (iVar3 == 0) {
      uVar4 = (camry_r10_result = fold_seven_big_endian_bytes_through_register_611fa(stack_record_14));
      if ((byte)(*((uint16_t *)(stack_record_14 + 6))) != uVar4) {
        return camry_r10_result;
      }
      (*((undefined2 *)camry_host_ptr((uint32_t)(iVar1 + -0x7fc8)))) = (*((uint16_t *)(stack_record_14 + 0)));
      (*((undefined2 *)camry_host_ptr((uint32_t)(iVar1 + -0x7fc6)))) = (*((uint16_t *)(stack_record_14 + 2)));
      (*((undefined2 *)camry_host_ptr((uint32_t)(iVar1 + -0x7fc2)))) = (*((uint16_t *)(stack_record_14 + 6)));
      (*((undefined2 *)camry_host_ptr((uint32_t)(iVar1 + -0x7fc4)))) = (*((uint16_t *)(stack_record_14 + 4)));
      return camry_r10_result;
    }
    bVar5 = bVar5 + 1;
  } while (bVar5 < 0xc9);
  return camry_r10_result;
}

void reset_redundant_shutdown_sequence_state_61526(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  DAT_febe3841 = 0;
  DAT_febe3842 = 0;
  DAT_febe3843 = 0;
  DAT_febe3844 = 0;
  publish_redundant_u8('\0',((undefined *)camry_host_ptr(0xfebe3845u)),((undefined *)camry_host_ptr(0xfebe8de0u)),((undefined *)camry_host_ptr(0xfebe8df4u)));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x7fba))))) = 0;
  return;
}

void advance_three_stage_terminal_request_counters_61554(void)

{
  if (DAT_febe3842 < DAT_000315cb) {
    DAT_febe388e = 0xff;
    DAT_febe3842 = DAT_febe3842 + 1;
  }
  else {
    DAT_febe3887 = 0;
    DAT_febe3886 = 0;
    if (DAT_febe3843 < DAT_000315cc) {
      DAT_febe3843 = DAT_febe3843 + 1;
    }
    else {
      if (DAT_000315cd <= DAT_febe3844) {
        clear_three_pattern_encoded_control_words_62be8();
                    /* WARNING: Subroutine does not return */
        enter_terminal_hardware_sequence();
      }
      DAT_febe388e = 0;
      DAT_febe3844 = DAT_febe3844 + 1;
    }
  }
  return;
}

void step_terminal_sequence_if_redundant_request_set_615be(void)

{
  int iVar1;
  uchar uStack_5;
  
  iVar1 = vote_redundant_u8(((undefined *)camry_host_ptr(0xfebe3845u)),((undefined *)camry_host_ptr(0xfebe8de0u)),((undefined *)camry_host_ptr(0xfebe8df4u)),&uStack_5);
  if (iVar1 == -0xd) {
    uStack_5 = '\0';
  }
  if (uStack_5 == 'Z') {
    advance_three_stage_terminal_request_counters_61554();
  }
  return;
}

void update_local_status_bit_latch(void)

{
  char cVar1;
  
  if (DAT_febe389e == 'Z') {
    cVar1 = '\0';
    if ((DAT_febe3839 & 4) != 0) {
      cVar1 = 'Z';
    }
    if (cVar1 == '\0') {
      DAT_febe3841 = 0;
    }
    else if ((DAT_000315ca <= DAT_febe3841) ||
            (DAT_febe3841 = DAT_febe3841 + 1, DAT_000315ca <= DAT_febe3841)) {
      DAT_febe3846 = 0x5a;
    }
  }
  step_terminal_sequence_if_redundant_request_set_615be();
  return;
}

int set_redundant_terminal_sequence_request_6163e(void)

{
  return publish_redundant_u8('Z',((undefined *)camry_host_ptr(0xfebe3845u)),((undefined *)camry_host_ptr(0xfebe8de0u)),((undefined *)camry_host_ptr(0xfebe8df4u)));
}

void clear_receive_toggle_tracking_6165a(void)

{
  DAT_febe3847 = 0;
  DAT_febe3848 = 0;
  return;
}

void decode_receive_status_bits_and_toggle_changes_61664(void)

{
  int iVar1;
  char cVar2;
  
  iVar1 = 0;
  if ((DAT_febe3839 & 4) != 0) {
    iVar1 = 0x5a;
  }
  if (iVar1 == 0) {
    cVar2 = '\0';
    if ((DAT_febe383e >> 8 & 1) != 0) {
      cVar2 = 'Z';
    }
    if (cVar2 != DAT_febe3847) {
      DAT_febe3848 = ~DAT_febe3848;
    }
    if ((DAT_febe383e >> 0xc & 1) == 0) {
      DAT_febe385d = 0xff;
    }
    else {
      DAT_febe385d = 0;
    }
    if ((DAT_febe383e >> 0xb & 1) == 0) {
      DAT_febe385e = 0xff;
    }
    else {
      DAT_febe385e = 0;
    }
    if ((DAT_febe383e >> 10 & 1) == 0) {
      DAT_febe385f = 0xff;
    }
    else {
      DAT_febe385f = 0;
    }
    DAT_febe3847 = cVar2;
    DAT_febe385c = DAT_febe3848;
    if ((DAT_febe383e >> 9 & 1) == 0) {
      DAT_febe3860 = 0xff;
    }
    else {
      DAT_febe3860 = 0;
    }
  }
  else {
    DAT_febe385d = 0xff;
    DAT_febe385e = 0xff;
    DAT_febe385f = 0xff;
    DAT_febe3860 = 0xff;
    DAT_febe385c = 0;
    clear_receive_toggle_tracking_6165a();
  }
  return;
}

ushort initialize_serial_transmit_bitmap_frame_616fc(void)

{
  uint uVar1;
  uint32_t puVar2;
  ushort uVar3;
  
  puVar2 = 0xfebeb800u;
  uVar1 = 0;
  do {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe3854u + (uint32_t)(uVar1) * 1u)))) = 0;
    uVar1 = uVar1 + 1;
  } while (uVar1 < 0x40);
  DAT_febe384a = 0x8000;
  DAT_febe384c = 0;
  DAT_febe384e = 0x5098;
  DAT_febe3850 = 0x1e00;
  uVar3 = fold_seven_big_endian_bytes_through_register_611fa(((undefined *)camry_host_ptr(0xfebe384au)));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x7f62))))) = 0;
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar2 + -0x7fae)))) = 0;
  (*((ushort *)camry_host_ptr((uint32_t)(puVar2 + -0x7fb0)))) = (*((ushort *)camry_host_ptr((uint32_t)(puVar2 + -0x7fb0)))) & 0xff00 | uVar3;
  return uVar3;
}

void pack_status_bitmap_and_transmit_serial_frame_6174a(void)

{
  byte *pbVar1;
  undefined1 uVar2;
  uint uVar3;
  uint32_t puVar4;
  ushort uVar5;
  int iVar6;
  uint uVar7;
  uint uVar8;
  
  puVar4 = 0xfebeb800u;
  DAT_febe384a = 0x8000;
  DAT_febe384c = 0;
  DAT_febe384e = 0x98;
  DAT_febe3850 = 0;
  uVar3 = 8;
  do {
    pbVar1 = ((undefined *)camry_host_ptr((uint32_t)(0xfebe3854u + (uint32_t)(uVar3) * 1u)));
    uVar7 = uVar3 & 0xf;
    uVar8 = uVar3 >> 4;
    uVar3 = uVar3 + 1;
    (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe3850u + (uint32_t)(-uVar8) * 2u)))) = (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe3850u + (uint32_t)(-uVar8) * 2u)))) | (ushort)((*pbVar1 & 1) << uVar7);
  } while (uVar3 < 0x3d);
  if (DAT_00031e80 == 'Z') {
    DAT_febe384a = DAT_00031e78 & (DAT_febe384a | DAT_00031e70);
    DAT_febe384c = DAT_00031e7a & (DAT_febe384c | DAT_00031e72);
    DAT_febe384e = DAT_00031e7c & (DAT_febe384e | DAT_00031e74);
    DAT_febe3850 = DAT_00031e7e & (DAT_febe3850 | DAT_00031e76);
  }
  uVar5 = fold_seven_big_endian_bytes_through_register_611fa(((undefined *)camry_host_ptr(0xfebe384au)));
  (*((ushort *)camry_host_ptr((uint32_t)(puVar4 + -0x7fb0)))) = (*((ushort *)camry_host_ptr((uint32_t)(puVar4 + -0x7fb0)))) & 0xff00 | uVar5;
  iVar6 = transmit_four_tagged_serial_halfwords_if_idle_61372(((undefined *)camry_host_ptr((uint32_t)(puVar4 + -0x7fb6))));
  uVar2 = 0;
  if (iVar6 == 0) {
    uVar2 = 0x5a;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x7f62))))) = uVar2;
  (*((short *)camry_host_ptr((uint32_t)(puVar4 + -0x7fae)))) = (short)iVar6;
  return;
}

undefined2 append_frame_check_byte_transmit_and_snapshot_61836(undefined2 *param_1)

{
  uint32_t puVar1;
  ushort uVar2;
  undefined2 uVar3;
  
  puVar1 = 0xfebeb800u;
  uVar2 = fold_seven_big_endian_bytes_through_register_611fa(param_1);
  param_1[3] = param_1[3] & 0xff00 | uVar2;
  uVar3 = transmit_four_tagged_serial_halfwords_if_idle_61372(param_1);
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x7f64)))) = uVar3;
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x7f6c)))) = *param_1;
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x7f6a)))) = param_1[1];
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x7f68)))) = param_1[2];
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x7f66)))) = param_1[3];
  return uVar3;
}

undefined4 select_clock3_source_and_set_divider_61874(uint param_1)

{
  byte bVar1;
  undefined4 uVar2;
  uint uVar3;
  
  CKSC3C = 4;
  uVar3 = CKSC3C;
  __synchronize();
  uVar3 = CKSC3S;
  bVar1 = 0;
  while ((uVar3 != 4 && (bVar1 < 100))) {
    uVar3 = CKSC3S;
    bVar1 = bVar1 + 1;
    __synchronize();
  }
  uVar3 = CLKD3STAT;
  bVar1 = 0;
  while (((uVar3 & 2) == 0 && (bVar1 < 100))) {
    bVar1 = bVar1 + 1;
    __synchronize();
    uVar3 = CLKD3STAT;
  }
  if ((uVar3 & 2) == 2) {
    CLKD3DIV = param_1;
    uVar3 = CLKD3DIV;
    __synchronize();
  }
  uVar3 = CLKD3STAT;
  bVar1 = 0;
  while (((uVar3 & 2) == 0 && (bVar1 < 100))) {
    bVar1 = bVar1 + 1;
    __synchronize();
    uVar3 = CLKD3STAT;
  }
  uVar2 = 0x11;
  if (((uVar3 & 2) == 2) && (uVar3 = CLKD3DIV, uVar3 == param_1)) {
    uVar2 = 0;
  }
  return uVar2;
}

undefined4 map_clock3_mode_to_divider_61906(char param_1)

{
  undefined4 uVar1;
  
  if (param_1 == -1) {
    uVar1 = 0;
  }
  else if (param_1 == '\x01') {
    uVar1 = 0x50;
  }
  else if (param_1 == '\x02') {
    uVar1 = 0x3d;
  }
  else {
    if (param_1 != '\0') {
      return 0x11;
    }
    uVar1 = 0x73;
  }
  uVar1 = select_clock3_source_and_set_divider_61874(uVar1);
  return uVar1;
}

void enter_terminal_hardware_sequence(void)

{
  uint8_t stack_record_c[12];
  undefined4 uVar1;
  
  priority_mask_enter(0xffff);
  apply_mpu_attribute_profile(DAT_00031686);
  write_configured_output_port_level_b(0);
  write_configured_output_port_level_b(1);
  restore_paired_port_mask_upper_words_61eb8();
  write_channel_requested_level(0);
  write_channel_requested_level(1);
  Ramfff80200 = 1;
  uVar1 = Ramfff80200;
  __synchronize();
  map_clock3_mode_to_divider_61906(0xff);
  Ramffc10104 = 0x200000;
  Ramffc10124 = 0x200000;
  Ramffc10120 = 0x200000;
  spin_wait(0x50);
  (*((uint16_t *)(stack_record_c + 0))) = 0x8000;
  (*((uint16_t *)(stack_record_c + 4))) = 0x5018;
  (*((uint16_t *)(stack_record_c + 2))) = 0;
  (*((uint16_t *)(stack_record_c + 6))) = 0x1f00;
  append_frame_check_byte_transmit_and_snapshot_61836(stack_record_c);
  do {
                    /* WARNING: Do nothing block with infinite loop */
  } while( true );
}

void ensure_clock3_divider_50_under_priority_mask_619c0(void)

{
  uint uVar1;
  
  uVar1 = CLKD3DIV;
  if (uVar1 != 0x50) {
    uVar1 = priority_mask_enter(0xffff);
    select_clock3_source_and_set_divider_61874(0x50);
    priority_mask_restore(uVar1);
  }
  return;
}

void initialize_paired_port_mask_upper_words_619ec(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  
  iVar5 = 0;
  do {
    iVar2 = iVar5 + 1;
    iVar3 = (uint)(ushort)(*((volatile uint16_t *)camry_host_ptr((uint32_t)(0x315e8u + (uint32_t)((short)iVar5 * 0xe) * 2u)))) << 0x10;
    iVar4 = (uint)(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x315dbu + (uint32_t)((short)iVar5 * 0x1c) * 1u)))) * 0x40;
    iVar1 = iVar5 + -1;
    (*((int *)camry_host_ptr((uint32_t)(iVar4 + -0x3efffc)))) = iVar3;
    (*((int *)camry_host_ptr((uint32_t)(iVar4 + -0x3effdc)))) = iVar3;
    (*((int *)camry_host_ptr((uint32_t)(iVar4 + -0x3effe0)))) = iVar3;
    iVar5 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  return;
}

void initialize_paired_phase_timer_registers_61a1c(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  
  iVar4 = 0;
  do {
    iVar2 = iVar4 + 1;
    iVar3 = (uint)(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x315d0u + (uint32_t)(iVar4) * 1u)))) * 0x1000;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffe70034u + (uint32_t)(iVar3) * 1u)))) = 1;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffe70208u + (uint32_t)(iVar3) * 1u)))) = 1;
    *(undefined2 *)(((undefined *)camry_host_ptr((uint32_t)(0xffe7020cu + (uint32_t)(iVar3) * 1u)))) = 0;
    *(undefined4 *)(((undefined *)camry_host_ptr((uint32_t)(0xffe70078u + (uint32_t)(iVar3) * 1u)))) = 0;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffe70004u + (uint32_t)(iVar3) * 1u)))) = 0;
    *(undefined4 *)(((undefined *)camry_host_ptr((uint32_t)(0xffe7007cu + (uint32_t)(iVar3) * 1u)))) = 0x80;
    *(undefined2 *)(((undefined *)camry_host_ptr((uint32_t)(0xffe70008u + (uint32_t)(iVar3) * 1u)))) = 0x808;
    iVar1 = iVar4 + -1;
    *(undefined2 *)(((undefined *)camry_host_ptr((uint32_t)(0xffe7000cu + (uint32_t)(iVar3) * 1u)))) = 0x810;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffe70200u + (uint32_t)(iVar3) * 1u)))) = 0;
    *(undefined2 *)(((undefined *)camry_host_ptr((uint32_t)(0xffe70000u + (uint32_t)(iVar3) * 1u)))) = 0;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffe70200u + (uint32_t)(iVar3) * 1u)))) = 0x7e;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffe70204u + (uint32_t)(iVar3) * 1u)))) = 0;
    *(undefined4 *)(((undefined *)camry_host_ptr((uint32_t)(0xffe70074u + (uint32_t)(iVar3) * 1u)))) = 0;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffe70020u + (uint32_t)(iVar3) * 1u)))) = 0;
    iVar4 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  return;
}

void program_paired_phase_timer_period_and_compares_61a76(uint param_1,uint param_2,uint param_3)

{
  int iVar1;
  int iVar2;
  int iVar3;
  uint uVar4;
  uint uVar5;
  int iVar6;
  
  param_1 = param_1 & 0xffff;
  param_2 = param_2 & 0xffff;
  param_3 = param_3 & 0xffff;
  uVar4 = (uint)DAT_00031670;
  iVar6 = 0;
  do {
    iVar2 = iVar6 + 1;
    uVar5 = (uint)(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x315d0u + (uint32_t)(iVar6) * 1u))));
    iVar3 = uVar5 * 0x1000;
    iVar1 = iVar6 + -1;
    *(undefined2 *)(((undefined *)camry_host_ptr((uint32_t)(0xffe70210u + (uint32_t)(iVar3) * 1u)))) = 0;
    *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0xffe7006cu + (uint32_t)(iVar3) * 1u)))) = param_1;
    *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0xffe70070u + (uint32_t)(iVar3) * 1u)))) = param_1;
    *(undefined2 *)(((undefined *)camry_host_ptr((uint32_t)(0xffe70210u + (uint32_t)(iVar3) * 1u)))) = 0xda5a;
    *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0xffe7014cu + (uint32_t)(iVar3) * 1u)))) = param_2;
    (*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xffe70184u + (uint32_t)(uVar5 * 0x400) * 4u)))) = param_3;
    (*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xffe70180u + (uint32_t)(uVar5 * 0x400) * 4u)))) = param_3;
    *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0xffe70148u + (uint32_t)(iVar3) * 1u)))) = param_2 + uVar4 * -2 & 0xffff;
    (*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xffe70144u + (uint32_t)(uVar5 * 0x400) * 4u)))) = param_1 * 2 + param_2 & 0xffff;
    (*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xffe70188u + (uint32_t)(uVar5 * 0x400) * 4u)))) = param_3;
    iVar6 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  return;
}

void configure_both_phase_timer_dma_descriptors_61b22(void)

{
  int iVar1;
  undefined1 uVar2;
  int iVar3;
  int iVar4;
  
  iVar4 = 0;
  do {
    iVar3 = (short)iVar4 * 0x28;
    uVar2 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x3161cu + (uint32_t)(iVar3) * 1u))));
    disable_indexed_dma_channel_607fe(uVar2);
    program_dma_channel_from_descriptor_6082c(((undefined *)camry_host_ptr((uint32_t)(0x3161cu + (uint32_t)(iVar3) * 1u))));
    enable_indexed_dma_channel_6080e(uVar2);
    iVar1 = iVar4 + 1;
    iVar3 = iVar4 + -1;
    iVar4 = iVar1;
  } while (((iVar3 < 0) || (iVar1 < 0)));
  return;
}

void initialize_phase_timer_ports_compares_and_dma_61b56(void)

{
  ushort compare;
  
  compare = pwm_compare_offset + (pwm_compare_span >> 1);
  initialize_paired_port_mask_upper_words_619ec();
  initialize_paired_phase_timer_registers_61a1c();
  program_paired_phase_timer_period_and_compares_61a76((*((volatile uint16_t *)camry_host_ptr(0x3166eu))), (*((volatile uint16_t *)camry_host_ptr(0x3166cu))), compare);
  pwm_initialize_compare_stages(compare);
  configure_both_phase_timer_dma_descriptors_61b22();
  return;
}

uint refresh_phase_timer_span_and_dma_reload_61b90(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  byte bVar4;
  uint uVar5;
  uint uVar6;
  uint saved_mask;
  int iVar7;
  uint uVar8;
  uint uVar9;
  
  uVar8 = (uint)pwm_compare_span;
  uVar9 = (uint)DAT_00031672;
  uVar5 = (uint)pwm_compare_offset;
  uVar6 = (uint)DAT_00031670;
  saved_mask = priority_mask_enter(0xffc0);
  iVar7 = 0;
  do {
    bVar4 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x315d0u + (uint32_t)(iVar7) * 1u))));
    iVar2 = iVar7 + 1;
    iVar3 = (uint)bVar4 * 0x1000;
    iVar1 = iVar7 + -1;
    *(volatile uint32_t *)camry_host_ptr((uint32_t)(0xffe70078u + (uint32_t)iVar3)) = 0;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffe70004u + (uint32_t)(iVar3) * 1u)))) = 0;
    *(volatile uint32_t *)camry_host_ptr((uint32_t)(0xffe7007cu + (uint32_t)iVar3)) = 0x80;
    *(volatile uint32_t *)camry_host_ptr((uint32_t)(0xffe70074u + (uint32_t)iVar3)) = 0;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffe70020u + (uint32_t)(iVar3) * 1u)))) = 0;
    *(volatile uint32_t *)camry_host_ptr((uint32_t)(0xffe7014cu + (uint32_t)iVar3)) = uVar8;
    *(volatile uint32_t *)camry_host_ptr((uint32_t)(0xffe70148u + (uint32_t)iVar3)) = uVar8 + uVar6 * -2 & 0xffff;
    (*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xffe70144u + (uint32_t)((uint)bVar4 * 0x400) * 4u)))) = uVar9 * 2 + uVar5 * 2 & 0xffff;
    iVar7 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  priority_mask_restore(saved_mask);
  uVar9 = 0;
  do {
    if (((int8_t)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x3161cu + (uint32_t)((short)uVar9 * 0x28) * 1u))))) != -1) {
      refresh_dma_reload_descriptor_and_selector_60a6a(((undefined *)camry_host_ptr((uint32_t)(0x3161cu + (uint32_t)((short)uVar9 * 0x28) * 1u))));
    }
    uVar9 = uVar9 + 1;
  } while (uVar9 < 2);
  return saved_mask;
}

void stage_configured_phase_mask(uint bank,uint mask)

{
  ushort uVar1;
  int iVar2;
  
  iVar2 = (short)bank * 0x1c;
  uVar1 = 0;
  if ((mask & 1) == 0) {
    uVar1 = *(ushort *)(((undefined *)camry_host_ptr((uint32_t)(0x315dcu + (uint32_t)(iVar2) * 1u))));
  }
  if ((mask >> 3 & 1) == 0) {
    uVar1 = uVar1 | *(ushort *)(((undefined *)camry_host_ptr((uint32_t)(0x315deu + (uint32_t)(iVar2) * 1u))));
  }
  if ((mask >> 1 & 1) == 0) {
    uVar1 = uVar1 | *(ushort *)(((undefined *)camry_host_ptr((uint32_t)(0x315e0u + (uint32_t)(iVar2) * 1u))));
  }
  if ((mask >> 4 & 1) == 0) {
    uVar1 = uVar1 | *(ushort *)(((undefined *)camry_host_ptr((uint32_t)(0x315e2u + (uint32_t)(iVar2) * 1u))));
  }
  if ((mask >> 2 & 1) == 0) {
    uVar1 = uVar1 | *(ushort *)(((undefined *)camry_host_ptr((uint32_t)(0x315e4u + (uint32_t)(iVar2) * 1u))));
  }
  if ((mask >> 5 & 1) == 0) {
    uVar1 = uVar1 | *(ushort *)(((undefined *)camry_host_ptr((uint32_t)(0x315e6u + (uint32_t)(iVar2) * 1u))));
  }
  (*((volatile uint16_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe38a0u + (uint32_t)(bank) * (uint32_t)sizeof(F33PwmHalfwordStage)) + (uint32_t)(0) * (uint32_t)sizeof(F33PwmHalfwordStage) + (uint32_t)offsetof(F33PwmHalfwordStage, port_mask))))) = uVar1;
  return;
}

void apply_phase_port_enable_mask_61dfa(short param_1,ushort param_2)

{
  int iVar1;
  ushort uVar2;
  ushort uVar3;
  ushort uVar4;
  ushort uVar5;
  ushort uVar6;
  int iVar7;
  
  iVar7 = param_1 * 0x1c;
  uVar6 = ~((*((volatile uint16_t *)camry_host_ptr((uint32_t)(0x315e8u + (uint32_t)(param_1 * 0xe) * 2u)))) & param_2);
  iVar1 = (uint)(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x315dbu + (uint32_t)(iVar7) * 1u)))) * 0x40;
  uVar2 = *(ushort *)(((undefined *)camry_host_ptr((uint32_t)(0x315eeu + (uint32_t)(iVar7) * 1u))));
  uVar5 = (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0x315e8u + (uint32_t)(param_1 * 0xe) * 2u)))) & uVar6;
  uVar3 = *(ushort *)(((undefined *)camry_host_ptr((uint32_t)(0x315ecu + (uint32_t)(iVar7) * 1u))));
  uVar4 = ~uVar5;
  (*((ushort *)camry_host_ptr((uint32_t)(iVar1 + -0x3effe8)))) =
       *(ushort *)(((undefined *)camry_host_ptr((uint32_t)(0x315eau + (uint32_t)(iVar7) * 1u)))) & uVar5 | (*((ushort *)camry_host_ptr((uint32_t)(iVar1 + -0x3effe8)))) & uVar4;
  (*((ushort *)camry_host_ptr((uint32_t)(iVar1 + -0x3effe4)))) = uVar5 & uVar3 | (*((ushort *)camry_host_ptr((uint32_t)(iVar1 + -0x3effe4)))) & uVar4;
  (*((ushort *)camry_host_ptr((uint32_t)(iVar1 + -0x3effd8)))) = uVar5 & uVar2 | uVar4 & (*((ushort *)camry_host_ptr((uint32_t)(iVar1 + -0x3effd8))));
  (*((ushort *)camry_host_ptr((uint32_t)(iVar1 + -0x3ebff8)))) = (*((ushort *)camry_host_ptr((uint32_t)(iVar1 + -0x3ebff8)))) | uVar5;
  (*((ushort *)camry_host_ptr((uint32_t)(iVar1 + -0x3f0000)))) = (*((ushort *)camry_host_ptr((uint32_t)(iVar1 + -0x3f0000)))) & uVar6;
  (*((ushort *)camry_host_ptr((uint32_t)(iVar1 + -0x3effec)))) = (*((ushort *)camry_host_ptr((uint32_t)(iVar1 + -0x3effec)))) | uVar5;
  (*((ushort *)camry_host_ptr((uint32_t)(iVar1 + -0x3effec)))) = (*((ushort *)camry_host_ptr((uint32_t)(iVar1 + -0x3effec)))) & uVar6;
  (*((ushort *)camry_host_ptr((uint32_t)(iVar1 + -0x3efff0)))) = (*((ushort *)camry_host_ptr((uint32_t)(iVar1 + -0x3efff0)))) & uVar6;
  return;
}

void publish_staged_phase_compares_and_port_masks_61e72(void)

{
  int iVar1;
  undefined2 *puVar2;
  int iVar3;
  undefined2 uVar4;
  uint uVar5;
  int iVar7;
  
  iVar7 = 0;
  do {
    puVar2 = (undefined2 *)camry_host_ptr(0xfebe38a0u + (uint)iVar7 * 8u);
    uVar4 = *puVar2;
    uVar5 = (uint)(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x315d0u + (uint32_t)(iVar7) * 1u))));
    (*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xffe70184u + (uint32_t)(uVar5 * 0x400) * 4u)))) = (uint)(ushort)puVar2[2];
    (*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xffe70180u + (uint32_t)(uVar5 * 0x400) * 4u)))) = (uint)(ushort)puVar2[3];
    (*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xffe70188u + (uint32_t)(uVar5 * 0x400) * 4u)))) = (uint)(ushort)puVar2[1];
    apply_phase_port_enable_mask_61dfa(iVar7,uVar4);
    iVar3 = iVar7 + 1;
    iVar1 = iVar7 + -1;
    iVar7 = iVar3;
  } while (((iVar1 < 0) || (iVar3 < 0)));
  return;
}

void restore_paired_port_mask_upper_words_61eb8(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  
  iVar5 = 0;
  do {
    iVar2 = iVar5 + 1;
    iVar3 = (uint)(ushort)(*((volatile uint16_t *)camry_host_ptr((uint32_t)(0x315e8u + (uint32_t)((short)iVar5 * 0xe) * 2u)))) << 0x10;
    iVar4 = (uint)(byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x315dbu + (uint32_t)((short)iVar5 * 0x1c) * 1u)))) * 0x40;
    iVar1 = iVar5 + -1;
    (*((int *)camry_host_ptr((uint32_t)(iVar4 + -0x3efffc)))) = iVar3;
    (*((int *)camry_host_ptr((uint32_t)(iVar4 + -0x3effdc)))) = iVar3;
    (*((int *)camry_host_ptr((uint32_t)(iVar4 + -0x3effe0)))) = iVar3;
    iVar5 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  return;
}

void initialize_two_rom_selected_output_pin_levels_61ee8(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  uint uVar4;
  int iVar5;
  
  iVar5 = 0;
  do {
    uVar4 = (*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x315d4u + (uint32_t)((short)iVar5 * 7) * 4u)))) & 0xf;
    iVar2 = (((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x315d4u + (uint32_t)((short)iVar5 * 7) * 4u)))) & 0xff00) >> 8) * 0x40;
    (*((uint *)camry_host_ptr((uint32_t)(iVar2 + -0x3efffc)))) =
         ((byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x315d9u + (uint32_t)((short)iVar5 * 0x1c) * 1u)))) & 1 | 0x10000) << uVar4;
    iVar1 = iVar5 + 1;
    iVar3 = 0x10000 << uVar4;
    (*((int *)camry_host_ptr((uint32_t)(iVar2 + -0x3effdc)))) = iVar3;
    (*((int *)camry_host_ptr((uint32_t)(iVar2 + -0x3effe0)))) = iVar3;
    iVar2 = iVar5 + -1;
    iVar5 = iVar1;
  } while (((iVar2 < 0) || (iVar1 < 0)));
  return;
}

void write_configured_output_port_level_a(uint bank)

{
  (*((uint *)camry_host_ptr((uint32_t)((((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x315d4u + (uint32_t)((short)bank * 7) * 4u)))) & 0xff00) >> 8) * 0x40 + -0x3efffc)))) =
       ((byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x315d8u + (uint32_t)((short)bank * 0x1c) * 1u)))) & 1 | 0x10000) <<
       ((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x315d4u + (uint32_t)((short)bank * 7) * 4u)))) & 0xf);
  return;
}

void write_configured_output_port_level_b(uint bank)

{
  (*((uint *)camry_host_ptr((uint32_t)((((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x315d4u + (uint32_t)((short)bank * 7) * 4u)))) & 0xff00) >> 8) * 0x40 + -0x3efffc)))) =
       ((byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x315d9u + (uint32_t)((short)bank * 0x1c) * 1u)))) & 1 | 0x10000) <<
       ((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x315d4u + (uint32_t)((short)bank * 7) * 4u)))) & 0xf);
  return;
}

void write_two_rom_selected_output_pin_masks_61f96(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  
  iVar5 = 0;
  do {
    iVar2 = iVar5 + 1;
    iVar3 = 0x10000 << ((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x315d4u + (uint32_t)((short)iVar5 * 7) * 4u)))) & 0xf);
    iVar4 = (((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x315d4u + (uint32_t)((short)iVar5 * 7) * 4u)))) & 0xff00) >> 8) * 0x40;
    iVar1 = iVar5 + -1;
    (*((int *)camry_host_ptr((uint32_t)(iVar4 + -0x3effdc)))) = iVar3;
    (*((int *)camry_host_ptr((uint32_t)(iVar4 + -0x3effe0)))) = iVar3;
    iVar5 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  return;
}

void initialize_two_channel_output_pin_levels_61fce(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  uint uVar4;
  int iVar5;
  
  iVar5 = 0;
  do {
    uVar4 = (*((volatile uint32_t *)camry_host_ptr((uint32_t)((uint32_t)(0x312fcu + (uint32_t)(iVar5) * (uint32_t)sizeof(F33ChannelPortDescriptor)) + (uint32_t)(0) * (uint32_t)sizeof(F33ChannelPortDescriptor) + (uint32_t)offsetof(F33ChannelPortDescriptor, output_selector))))) & 0xf;
    iVar2 = (((*((volatile uint32_t *)camry_host_ptr((uint32_t)((uint32_t)(0x312fcu + (uint32_t)(iVar5) * (uint32_t)sizeof(F33ChannelPortDescriptor)) + (uint32_t)(0) * (uint32_t)sizeof(F33ChannelPortDescriptor) + (uint32_t)offsetof(F33ChannelPortDescriptor, output_selector))))) & 0xff00) >> 8) * 0x40;
    (*((uint *)camry_host_ptr((uint32_t)(iVar2 + -0x3efffc)))) = ((*((volatile uint8_t *)camry_host_ptr((uint32_t)((uint32_t)(0x312fcu + (uint32_t)(iVar5) * (uint32_t)sizeof(F33ChannelPortDescriptor)) + (uint32_t)(0) * (uint32_t)sizeof(F33ChannelPortDescriptor) + (uint32_t)offsetof(F33ChannelPortDescriptor, requested_level))))) & 1 | 0x10000) << uVar4
    ;
    iVar1 = iVar5 + 1;
    iVar3 = 0x10000 << uVar4;
    (*((int *)camry_host_ptr((uint32_t)(iVar2 + -0x3effdc)))) = iVar3;
    (*((int *)camry_host_ptr((uint32_t)(iVar2 + -0x3effe0)))) = iVar3;
    iVar2 = iVar5 + -1;
    iVar5 = iVar1;
  } while (((iVar2 < 0) || (iVar1 < 0)));
  return;
}
