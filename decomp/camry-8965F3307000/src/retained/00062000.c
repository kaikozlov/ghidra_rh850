#include "common.h"

void write_two_channel_output_pin_masks_62018(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  
  iVar5 = 0;
  do {
    iVar2 = iVar5 + 1;
    iVar3 = 0x10000 << ((*((volatile uint32_t *)camry_host_ptr((uint32_t)((uint32_t)(0x312fcu + (uint32_t)(iVar5) * (uint32_t)sizeof(F33ChannelPortDescriptor)) + (uint32_t)(0) * (uint32_t)sizeof(F33ChannelPortDescriptor) + (uint32_t)offsetof(F33ChannelPortDescriptor, output_selector))))) & 0xf);
    iVar4 = (((*((volatile uint32_t *)camry_host_ptr((uint32_t)((uint32_t)(0x312fcu + (uint32_t)(iVar5) * (uint32_t)sizeof(F33ChannelPortDescriptor)) + (uint32_t)(0) * (uint32_t)sizeof(F33ChannelPortDescriptor) + (uint32_t)offsetof(F33ChannelPortDescriptor, output_selector))))) & 0xff00) >> 8) * 0x40;
    iVar1 = iVar5 + -1;
    (*((int *)camry_host_ptr((uint32_t)(iVar4 + -0x3effdc)))) = iVar3;
    (*((int *)camry_host_ptr((uint32_t)(iVar4 + -0x3effe0)))) = iVar3;
    iVar5 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  return;
}

void write_channel_reference_level(uint channel)

{
  (*((uint *)camry_host_ptr((uint32_t)((((*((volatile uint32_t *)camry_host_ptr((uint32_t)((uint32_t)(0x312fcu + (uint32_t)(channel) * (uint32_t)sizeof(F33ChannelPortDescriptor)) + (uint32_t)(0) * (uint32_t)sizeof(F33ChannelPortDescriptor) + (uint32_t)offsetof(F33ChannelPortDescriptor, output_selector))))) & 0xff00) >> 8) * 0x40 + -0x3efffc)))) =
       ((*((volatile uint8_t *)camry_host_ptr((uint32_t)((uint32_t)(0x312fcu + (uint32_t)(channel) * (uint32_t)sizeof(F33ChannelPortDescriptor)) + (uint32_t)(0) * (uint32_t)sizeof(F33ChannelPortDescriptor) + (uint32_t)offsetof(F33ChannelPortDescriptor, reference_level))))) & 1 | 0x10000) <<
       ((*((volatile uint32_t *)camry_host_ptr((uint32_t)((uint32_t)(0x312fcu + (uint32_t)(channel) * (uint32_t)sizeof(F33ChannelPortDescriptor)) + (uint32_t)(0) * (uint32_t)sizeof(F33ChannelPortDescriptor) + (uint32_t)offsetof(F33ChannelPortDescriptor, output_selector))))) & 0xf);
  return;
}

void write_channel_requested_level(uint channel)

{
  (*((uint *)camry_host_ptr((uint32_t)((((*((volatile uint32_t *)camry_host_ptr((uint32_t)((uint32_t)(0x312fcu + (uint32_t)(channel) * (uint32_t)sizeof(F33ChannelPortDescriptor)) + (uint32_t)(0) * (uint32_t)sizeof(F33ChannelPortDescriptor) + (uint32_t)offsetof(F33ChannelPortDescriptor, output_selector))))) & 0xff00) >> 8) * 0x40 + -0x3efffc)))) =
       ((*((volatile uint8_t *)camry_host_ptr((uint32_t)((uint32_t)(0x312fcu + (uint32_t)(channel) * (uint32_t)sizeof(F33ChannelPortDescriptor)) + (uint32_t)(0) * (uint32_t)sizeof(F33ChannelPortDescriptor) + (uint32_t)offsetof(F33ChannelPortDescriptor, requested_level))))) & 1 | 0x10000) <<
       ((*((volatile uint32_t *)camry_host_ptr((uint32_t)((uint32_t)(0x312fcu + (uint32_t)(channel) * (uint32_t)sizeof(F33ChannelPortDescriptor)) + (uint32_t)(0) * (uint32_t)sizeof(F33ChannelPortDescriptor) + (uint32_t)offsetof(F33ChannelPortDescriptor, output_selector))))) & 0xf);
  return;
}

uint read_channel_input_level(uint channel)

{
  return (int)((uint)(*((ushort *)camry_host_ptr((uint32_t)((uint)(*((volatile uint8_t *)camry_host_ptr((uint32_t)((uint32_t)(0x312fcu + (uint32_t)(channel) * (uint32_t)sizeof(F33ChannelPortDescriptor)) + (uint32_t)(0) * (uint32_t)sizeof(F33ChannelPortDescriptor) + (uint32_t)offsetof(F33ChannelPortDescriptor, input_port))))) * 0x40 + -0x3efff4)))) &
              1 << ((*((volatile uint8_t *)camry_host_ptr((uint32_t)((uint32_t)(0x312fcu + (uint32_t)(channel) * (uint32_t)sizeof(F33ChannelPortDescriptor)) + (uint32_t)(0) * (uint32_t)sizeof(F33ChannelPortDescriptor) + (uint32_t)offsetof(F33ChannelPortDescriptor, input_bit))))) & 0x1f)) >>
         ((*((volatile uint8_t *)camry_host_ptr((uint32_t)((uint32_t)(0x312fcu + (uint32_t)(channel) * (uint32_t)sizeof(F33ChannelPortDescriptor)) + (uint32_t)(0) * (uint32_t)sizeof(F33ChannelPortDescriptor) + (uint32_t)offsetof(F33ChannelPortDescriptor, input_bit))))) & 0x1f) & 0xff;
}

ushort select_acquisition_six_entry_base(ushort count,ushort capacity)

{
  ushort uVar1;
  
  if ((count & 1) == 0) {
    if (count < 6) {
      uVar1 = (capacity + count) - 6;
    }
    else {
      uVar1 = count - 6;
    }
  }
  else {
    uVar1 = count - 3;
  }
  return uVar1;
}

uint copy_acquisition_group0_samples(F33AcquisitionGroupPair *output)

{
  int iVar1;
  int iVar2;
  ushort uVar3;
  uint uVar4;
  int iVar5;
  
  uVar3 = count_transfer_entries('\0');
  uVar3 = select_acquisition_six_entry_base(uVar3,0x1b0);
  iVar5 = 0;
  do {
    uVar4 = consume_acquisition_group0_entry((uint)(*((uint8_t *)camry_host_ptr(0x30f2cu + (uint32_t)iVar5))) + uVar3);
    output->group0[iVar5] = (ushort)uVar4;
    iVar2 = iVar5 + 1;
    iVar1 = iVar5 + -5;
    iVar5 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  return uVar4;
}

uint copy_acquisition_group8_samples(F33AcquisitionGroupPair *output)

{
  int iVar1;
  int iVar2;
  ushort uVar3;
  uint uVar4;
  int iVar5;
  
  uVar3 = count_transfer_entries('\b');
  uVar3 = select_acquisition_six_entry_base(uVar3,0x1b0);
  iVar5 = 0;
  do {
    uVar4 = consume_acquisition_group8_entry((uint)(*((uint8_t *)camry_host_ptr(0x30f34u + (uint32_t)iVar5))) + uVar3);
    output->group8[iVar5] = (ushort)uVar4;
    iVar2 = iVar5 + 1;
    iVar1 = iVar5 + -5;
    iVar5 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  return uVar4;
}

void copy_acquisition_group_pair(F33AcquisitionGroupPair *output)

{
  copy_acquisition_group0_samples(output);
  copy_acquisition_group8_samples(output);
  return;
}

void initialize_serial_acquisition_channel(uchar channel)

{
  undefined2 *puVar1;
  int iVar2;
  uint uVar3;
  uint uVar4;
  ushort uVar5;
  int iVar6;
  int iVar7;
  
  if (channel < 2) {
    uVar5 = (ushort)channel;
    iVar7 = (short)uVar5 * 0x5a;
    iVar6 = (short)(ushort)channel * 6;
    uVar3 = 0;
    do {
      puVar1 = (undefined2 *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe3900u + (uint32_t)(uVar3 * 2 + iVar7) * 1u))));
      uVar3 = uVar3 + 1;
      *puVar1 = 0;
      puVar1[10] = 0;
    } while (uVar3 < 10);
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe3928u + (uint32_t)(iVar7) * 1u)))) = 3;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe3929u + (uint32_t)(iVar7) * 1u)))) = 0;
    uVar3 = 0;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe392au + (uint32_t)(iVar7) * 1u)))) = 0;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe392bu + (uint32_t)(iVar7) * 1u)))) = 0;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe392cu + (uint32_t)(iVar7) * 1u)))) = 0;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe392du + (uint32_t)(iVar7) * 1u)))) = 0;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe392eu + (uint32_t)(iVar7) * 1u)))) = 0;
    do {
      iVar2 = uVar3 * 2 + iVar7;
      uVar3 = uVar3 + 1;
      *(undefined2 *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe3900u + (uint32_t)(iVar2 + 0x30) * 1u)))) = 0;
      *(undefined2 *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe3900u + (uint32_t)(iVar2 + 0x38) * 1u)))) = 0;
    } while (uVar3 < 4);
    uVar3 = 0;
    do {
      iVar2 = uVar3 + (uint)channel * 2;
      uVar3 = uVar3 + 1;
      *(undefined2 *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe38c8u + (uint32_t)(iVar2 * 2) * 1u)))) = 0;
    } while (uVar3 < 2);
    uVar3 = 0;
    do {
      *(volatile uint8_t *)camry_host_ptr(0xfebe3900u + (uint32_t)iVar7 + uVar3 + 0x40u) = 0;
      *(undefined2 *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe3900u + (uint32_t)(uVar3 * 2 + iVar7 + 0x42) * 1u)))) = 0;
      uVar4 = 0;
      do {
        iVar2 = (short)uVar3 * 5 + uVar4;
        uVar4 = uVar4 + 1;
        *(undefined2 *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe3900u + (uint32_t)(iVar2 * 2 + iVar7 + 0x46) * 1u)))) = 0;
      } while (uVar4 < 5);
      uVar3 = uVar3 + 1;
    } while (uVar3 < 2);
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe38d0u + (uint32_t)((short)uVar5) * (uint32_t)sizeof(F33SerialAcquisitionRecord)) + (uint32_t)(0) * (uint32_t)sizeof(F33SerialAcquisitionRecord) + (uint32_t)offsetof(F33SerialAcquisitionRecord, sequence_failures))))) = '\0';
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe38d0u + (uint32_t)((short)uVar5) * (uint32_t)sizeof(F33SerialAcquisitionRecord)) + (uint32_t)(0) * (uint32_t)sizeof(F33SerialAcquisitionRecord) + (uint32_t)offsetof(F33SerialAcquisitionRecord, crc_failures))))) = '\0';
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe38d0u + (uint32_t)((short)uVar5) * (uint32_t)sizeof(F33SerialAcquisitionRecord)) + (uint32_t)(0) * (uint32_t)sizeof(F33SerialAcquisitionRecord) + (uint32_t)offsetof(F33SerialAcquisitionRecord, rx_or_tx_failures))))) = '\0';
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe38d0u + (uint32_t)((short)uVar5) * (uint32_t)sizeof(F33SerialAcquisitionRecord)) + (uint32_t)(0) * (uint32_t)sizeof(F33SerialAcquisitionRecord) + (uint32_t)offsetof(F33SerialAcquisitionRecord, rx_count_failures))))) = '\0';
    (*((volatile uint16_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe38d0u + (uint32_t)((short)uVar5) * (uint32_t)sizeof(F33SerialAcquisitionRecord)) + (uint32_t)(0) * (uint32_t)sizeof(F33SerialAcquisitionRecord) + (uint32_t)offsetof(F33SerialAcquisitionRecord, field12))))) = 0x800;
    (*((volatile uint16_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe38d0u + (uint32_t)((short)uVar5) * (uint32_t)sizeof(F33SerialAcquisitionRecord)) + (uint32_t)(0) * (uint32_t)sizeof(F33SerialAcquisitionRecord) + (uint32_t)offsetof(F33SerialAcquisitionRecord, field14_1))))) = 0;
    (*((volatile uint16_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe38d0u + (uint32_t)((short)uVar5) * (uint32_t)sizeof(F33SerialAcquisitionRecord)) + (uint32_t)(0) * (uint32_t)sizeof(F33SerialAcquisitionRecord) + (uint32_t)offsetof(F33SerialAcquisitionRecord, field14_0))))) = 0;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe38edu + (uint32_t)(iVar6) * 1u)))) = 0;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe38ecu + (uint32_t)(iVar6) * 1u)))) = 0;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe38ebu + (uint32_t)(iVar6) * 1u)))) = 0;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe38eau + (uint32_t)(iVar6) * 1u)))) = 0;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe38e9u + (uint32_t)(iVar6) * 1u)))) = 0;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe38e8u + (uint32_t)(iVar6) * 1u)))) = 0;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe38f9u + (uint32_t)(iVar6) * 1u)))) = 0;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe38f8u + (uint32_t)(iVar6) * 1u)))) = 0;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe38f7u + (uint32_t)(iVar6) * 1u)))) = 0;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe38f6u + (uint32_t)(iVar6) * 1u)))) = 0;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe38f5u + (uint32_t)(iVar6) * 1u)))) = 0;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe38f4u + (uint32_t)(iVar6) * 1u)))) = 0;
  }
  return;
}

void stage_and_send_five_halfword_acquisition_frame_62274(uint param_1,int param_2)

{
  undefined1 uVar1;
  int iVar2;
  uint uVar3;
  int iVar4;
  
  param_1 = param_1 & 0xff;
  if (param_1 < 2) {
    iVar4 = (short)param_1 * 0x5a;
    uVar3 = 0;
    do {
      iVar2 = uVar3 * 2;
      uVar3 = uVar3 + 1;
      (*((undefined2 *)camry_host_ptr((uint32_t)(iVar2 + iVar4 + -0x141c6ec)))) = (*((undefined2 *)camry_host_ptr((uint32_t)(iVar2 + param_2))));
    } while (uVar3 < 5);
    *(undefined2 *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe3926u + (uint32_t)(iVar4) * 1u)))) = 0;
    *(undefined2 *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe3924u + (uint32_t)(iVar4) * 1u)))) = 0;
    *(undefined2 *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe3922u + (uint32_t)(iVar4) * 1u)))) = 0;
    *(undefined2 *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe3920u + (uint32_t)(iVar4) * 1u)))) = 0;
    *(undefined2 *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe391eu + (uint32_t)(iVar4) * 1u)))) = 0xe700;
    iVar2 = write_serial_halfword_matrix_when_idle_60efa((*((volatile uint8_t *)camry_host_ptr(0x31674u + (param_1 & 0xff)))),iVar4 + -0x141c6ec);
    uVar1 = 0;
    if (iVar2 != 0) {
      uVar1 = 0x5a;
    }
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe392cu + (uint32_t)(iVar4) * 1u)))) = uVar1;
  }
  return;
}

void send_tag13_table_checked_acquisition_command_622d2(undefined1 param_1,uint param_2)

{
  uint uVar1;
  ushort auStack_e [5];
  
  uVar1 = param_2 & 0xff | 0x13;
  auStack_e[1] = 0;
  auStack_e[2] = 0;
  auStack_e[3] = 0;
  auStack_e[4] = 0;
  auStack_e[0] = (byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x2b118u + (uint32_t)(uVar1 ^ 0xff) * 1u)))) ^ 0xff | (ushort)(uVar1 << 8);
  stage_and_send_five_halfword_acquisition_frame_62274(param_1, camry_host_addr(auStack_e));
  return;
}

void reset_acquisition_channel_with_repeated_e0_commands_6230e(uint param_1)

{
  int iVar1;
  uchar uVar2;
  int iVar3;
  undefined8 uVar4;
  uint uVar5;
  
  uVar4 = 0xfebeb800;
  param_1 = param_1 & 0xff;
  if (param_1 < 2) {
    uVar2 = "\x02\n"[param_1];
    disable_indexed_dma_channel_607fe(uVar2);
    iVar3 = (int)uVar4;
    for (uVar5 = (uint)DAT_00031e8c; uVar5 != 0; uVar5 = uVar5 - 1) {
      send_tag13_table_checked_acquisition_command_622d2(param_1,0xe0);
      set_bounded_serial_transfer_count_60f7c(param_1,0);
      spin_wait((uint)DAT_00031e8d);
      read_serial_controller_status
                ((*((volatile uint8_t *)camry_host_ptr(0x31674u + param_1))),0x100,(F33SerialControllerStatus *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe38f4u + (uint32_t)((short)param_1 * 6) * 1u))))
                );
      iVar3 = (int)uVar4;
    }
    uVar5 = 0;
    iVar3 = (short)param_1 * 0x5a + iVar3;
    do {
      iVar1 = uVar5 * 2;
      uVar5 = uVar5 + 1;
      (*((undefined2 *)camry_host_ptr((uint32_t)((int)(0xffff8100u) + iVar1 + iVar3 + 0x14)))) = 0;
    } while (uVar5 < 10);
    (*((undefined1 *)camry_host_ptr((uint32_t)((int)(0xffff8100u) + iVar3 + 0x2c)))) = 0;
    enable_indexed_dma_channel_6080e(uVar2);
  }
  return;
}

void send_e700_acquisition_frame_6239e(undefined1 param_1)

{
  undefined2 record[5];
  
  record[0] = 0xe700;
  record[1] = 0;
  record[2] = 0;
  record[3] = 0;
  record[4] = 0;
  stage_and_send_five_halfword_acquisition_frame_62274(param_1, camry_host_addr(record));
  return;
}

void initialize_reset_and_prime_both_acquisition_channels_623c0(void)

{
  uint uVar1;
  
  uVar1 = 0;
  do {
    initialize_serial_acquisition_channel((uchar)uVar1);
    reset_acquisition_channel_with_repeated_e0_commands_6230e(uVar1);
    send_e700_acquisition_frame_6239e(uVar1);
    uVar1 = uVar1 + 1;
  } while (uVar1 < 2);
  spin_wait((uint)DAT_00031e88);
  return;
}

undefined4 validate_eight_byte_permuted_table_check_623ee(byte *param_1)

{
  undefined4 uVar1;
  
  uVar1 = 0x5a;
  if (param_1[8] ==
      ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x2b118u + (uint32_t)(param_1[9] ^
        (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x2b118u + (uint32_t)(param_1[6] ^
         (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x2b118u + (uint32_t)(param_1[7] ^
          (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x2b118u + (uint32_t)(param_1[4] ^
           (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x2b118u + (uint32_t)(param_1[5] ^
            (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x2b118u + (uint32_t)(param_1[2] ^ (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x2b118u + (uint32_t)(param_1[3] ^ (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x2b118u + (uint32_t)(*param_1 ^ 0xff) * 1u))))) * 1u))))) * 1u))))) * 1u))))) * 1u))))) * 1u))))) * 1u))))) * 1u)))) ^
      0xff)) {
    uVar1 = 0;
  }
  return uVar1;
}

void accumulate_serial_acquisition_masks(uchar channel,ushort first_mask,ushort second_mask)

{
  int iVar1;
  
  if (channel < 2) {
    iVar1 = ((byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe392eu + (uint32_t)((short)(ushort)channel * 0x5a) * 1u)))) & 3) * 2 +
            (short)(ushort)channel * 0x5a;
    *(ushort *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe3900u + (uint32_t)(iVar1 + 0x30) * 1u)))) =
         *(ushort *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe3900u + (uint32_t)(iVar1 + 0x30) * 1u)))) | first_mask;
    *(ushort *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe3900u + (uint32_t)(iVar1 + 0x38) * 1u)))) =
         *(ushort *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe3900u + (uint32_t)(iVar1 + 0x38) * 1u)))) | second_mask;
  }
  return;
}

void decode_serial_acquisition_frame
               (uchar channel,uchar fifo,uchar *crc_failure,uchar *sequence_failure)

{
  ushort uVar1;
  ushort uVar2;
  ushort uVar3;
  byte bVar4;
  uchar offset;
  uint uVar5;
  int iVar6;
  uchar offset_00;
  ushort uVar7;
  int iVar8;
  
  uVar7 = (ushort)channel;
  iVar8 = (short)uVar7 * 0x5a;
  uVar5 = read_transfer_primary_count_low("\x02\n"[channel]);
  if (uVar5 < 0xb) {
    if (uVar5 < 6) {
      offset_00 = '\n';
      offset = '\x05';
    }
    else {
      offset_00 = '\x05';
      offset = '\0';
    }
  }
  else if (uVar5 < 0x10) {
    offset_00 = '\0';
    offset = '\x0f';
  }
  else {
    offset_00 = '\x0f';
    offset = '\n';
  }
  copy_serial_fifo_words(fifo,(ushort *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe3900u + (uint32_t)(iVar8) * 1u)))),offset,'\x05');
  copy_serial_fifo_words(fifo,(ushort *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe390au + (uint32_t)(iVar8) * 1u)))),offset_00,'\x05');
  iVar6 = validate_eight_byte_permuted_table_check_623ee(((undefined *)camry_host_ptr((uint32_t)(0xfebe390au + (uint32_t)(iVar8) * 1u))));
  *crc_failure = (uchar)iVar6;
  if (iVar6 == 0) {
    bVar4 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe3928u + (uint32_t)(iVar8) * 1u))));
    uVar5 = (int)(*(ushort *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe390au + (uint32_t)(iVar8) * 1u)))) & 0xc0) >> 6;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe3928u + (uint32_t)(iVar8) * 1u)))) = (char)uVar5;
    if (uVar5 == (bVar4 + 1 & 3)) {
      uVar1 = *(ushort *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe390cu + (uint32_t)(iVar8) * 1u))));
      (*((volatile uint16_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe38d0u + (uint32_t)((short)uVar7) * (uint32_t)sizeof(F33SerialAcquisitionRecord)) + (uint32_t)(0) * (uint32_t)sizeof(F33SerialAcquisitionRecord) + (uint32_t)offsetof(F33SerialAcquisitionRecord, field14_0))))) =
           (ushort)((*(ushort *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe390au + (uint32_t)(iVar8) * 1u)))) & 0x3f) << 8) | uVar1 >> 8;
      uVar2 = *(ushort *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe390eu + (uint32_t)(iVar8) * 1u))));
      uVar3 = *(ushort *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe3910u + (uint32_t)(iVar8) * 1u))));
      (*((volatile uint16_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe38d0u + (uint32_t)((short)uVar7) * (uint32_t)sizeof(F33SerialAcquisitionRecord)) + (uint32_t)(0) * (uint32_t)sizeof(F33SerialAcquisitionRecord) + (uint32_t)offsetof(F33SerialAcquisitionRecord, field14_1))))) =
           (uVar1 & 0xff) << 6 | uVar2 >> 10;
      (*((volatile uint16_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe38d0u + (uint32_t)((short)uVar7) * (uint32_t)sizeof(F33SerialAcquisitionRecord)) + (uint32_t)(0) * (uint32_t)sizeof(F33SerialAcquisitionRecord) + (uint32_t)offsetof(F33SerialAcquisitionRecord, field12))))) =
           (uVar2 & 0x3ff) << 2 | uVar3 >> 0xe;
      accumulate_serial_acquisition_masks
                (channel,(ushort)((int)(uVar3 & 0x3ff8) >> 3),
                 (ushort)((uVar3 & 7) << 8) | *(ushort *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe3912u + (uint32_t)(iVar8) * 1u)))) >> 8);
    }
    else {
      *sequence_failure = 'Z';
    }
  }
  return;
}

void sample_serial_acquisition_channel(uchar channel)

{
  uint8_t stack_record_1e[30];
  uchar channel_00;
  undefined1 uVar1;
  undefined1 uVar2;
  int iVar3;
  int iVar4;
  
  if (channel < 2) {
    iVar4 = (short)(ushort)channel * 0x5a;
    stack_record_1e[0] = '\0';
    stack_record_1e[1] = '\0';
    uVar2 = 0;
    iVar3 = (short)(ushort)channel * 6;
    channel_00 = (*((volatile uint8_t *)camry_host_ptr(0x31674u + (uint32_t)channel)));
    read_serial_controller_status
              (channel_00,0,(F33SerialControllerStatus *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe38e8u + (uint32_t)(iVar3) * 1u)))));
    if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe38eau + (uint32_t)(iVar3) * 1u)))) == '\0') {
      uVar1 = 0;
      if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe38ebu + (uint32_t)(iVar3) * 1u)))) == '\n') {
        decode_serial_acquisition_frame(channel,channel_00,((uint8_t *)(stack_record_1e)),((uint8_t *)((stack_record_1e + 1))));
      }
      else {
        uVar2 = 0x5a;
      }
    }
    else {
      uVar1 = 0x5a;
    }
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe392au + (uint32_t)(iVar4) * 1u)))) = uVar1;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe3929u + (uint32_t)(iVar4) * 1u)))) = uVar2;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe392bu + (uint32_t)(iVar4) * 1u)))) = stack_record_1e[0];
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe392du + (uint32_t)(iVar4) * 1u)))) = stack_record_1e[1];
  }
  return;
}

byte compute_five_byte_permuted_table_check_625f6(byte *param_1)

{
  return (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x2b118u + (uint32_t)(param_1[5] ^
          (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x2b118u + (uint32_t)(param_1[2] ^
           (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x2b118u + (uint32_t)(param_1[3] ^ (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x2b118u + (uint32_t)(*param_1 ^ (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x2b118u + (uint32_t)(param_1[1] ^ 0xff) * 1u))))) * 1u))))) * 1u))))) * 1u))))) * 1u)))) ^ 0xff;
}

void pack_acquisition_status_command_and_consume_pending_bits_62636(uint param_1,uint param_2)

{
  ushort uVar1;
  ushort uVar2;
  int iVar3;
  undefined2 record[5];
  
  param_1 = param_1 & 0xff;
  param_2 = param_2 & 0xff;
  if ((param_1 < 2) && (param_2 < 2)) {
    iVar3 = (short)param_1 * 0x5a;
    iVar3 = ((byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe392eu + (uint32_t)(iVar3) * 1u)))) & 3) * 2 + iVar3;
    if (param_2 == 0) {
      uVar1 = *(ushort *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe3900u + (uint32_t)(iVar3 + 0x30) * 1u))));
      uVar2 = 0x20;
    }
    else {
      uVar1 = *(ushort *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe3900u + (uint32_t)(iVar3 + 0x38) * 1u))));
      uVar2 = 0xff81;
    }
    record[1] = (uVar1 & 0x7ff | (ushort)((uVar1 & 0x70) << 7) | (ushort)((uVar1 & 0x40) << 8)) &
                DAT_00031e86;
    uVar1 = *(ushort *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe38c8u + (uint32_t)((param_2 + param_1 * 2) * 2) * 1u))));
    *(ushort *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe38c8u + (uint32_t)((param_2 + param_1 * 2) * 2) * 1u)))) = 0;
    record[2] = 0;
    record[1] = record[1] | uVar1;
    record[0] = (uVar2 | 1) << 8 | 0x10;
    record[2] = compute_five_byte_permuted_table_check_625f6((byte *)record);
    record[3] = 0;
    record[4] = 0;
    stage_and_send_five_halfword_acquisition_frame_62274(param_1, camry_host_addr(record));
  }
  return;
}

void snapshot_five_acquisition_halfwords_to_selected_slot_626d6(ushort param_1,char param_2)

{
  bool bVar1;
  undefined2 *puVar2;
  int iVar3;
  
  if ((param_1 & 0xff) < 2) {
    iVar3 = (short)(param_1 & 0xff) * 0x5a;
    puVar2 = (undefined2 *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe3900u + (uint32_t)(iVar3) * 1u))));
    bVar1 = param_2 != '\0';
    puVar2[(short)(ushort)bVar1 * 5 + 0x23] = *puVar2;
    puVar2[(short)(ushort)bVar1 * 5 + 0x24] = *(undefined2 *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe3902u + (uint32_t)(iVar3) * 1u))));
    puVar2[(short)(ushort)bVar1 * 5 + 0x25] = *(undefined2 *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe3904u + (uint32_t)(iVar3) * 1u))));
    puVar2[(short)(ushort)bVar1 * 5 + 0x26] = *(undefined2 *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe3906u + (uint32_t)(iVar3) * 1u))));
    puVar2[(short)(ushort)bVar1 * 5 + 0x27] = *(undefined2 *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe3908u + (uint32_t)(iVar3) * 1u))));
  }
  return;
}

void send_selected_rom_acquisition_frame_or_zeros_62714(undefined1 param_1,char param_2,char param_3)

{
  uint8_t stack_record_e[14];
  int iVar1;
  
  if (param_3 == 'Z') {
    iVar1 = (short)(ushort)(param_2 != '\0') * 10;
    (*((uint16_t *)(stack_record_e + 0))) = *(undefined2 *)(((undefined *)camry_host_ptr((uint32_t)(0x31e8eu + (uint32_t)(iVar1) * 1u))));
    (*((uint16_t *)(stack_record_e + 2))) = *(undefined2 *)(((undefined *)camry_host_ptr((uint32_t)(0x31e90u + (uint32_t)(iVar1) * 1u))));
    (*((uint16_t *)(stack_record_e + 4))) = *(undefined2 *)(((undefined *)camry_host_ptr((uint32_t)(0x31e92u + (uint32_t)(iVar1) * 1u))));
    (*((uint16_t *)(stack_record_e + 6))) = *(undefined2 *)(((undefined *)camry_host_ptr((uint32_t)(0x31e94u + (uint32_t)(iVar1) * 1u))));
    (*((uint16_t *)(stack_record_e + 8))) = *(undefined2 *)(((undefined *)camry_host_ptr((uint32_t)(0x31e96u + (uint32_t)(iVar1) * 1u))));
  }
  else {
    (*((uint16_t *)(stack_record_e + 6))) = 0;
    (*((uint16_t *)(stack_record_e + 4))) = 0;
    (*((uint16_t *)(stack_record_e + 2))) = 0;
    (*((uint16_t *)(stack_record_e + 0))) = 0;
    (*((uint16_t *)(stack_record_e + 8))) = 0;
  }
  stage_and_send_five_halfword_acquisition_frame_62274(param_1, camry_host_addr(((uint16_t *)(stack_record_e))));
  return;
}

void step_acquisition_rom_frame_countdown_6276c(ushort param_1,char param_2)

{
  int iVar1;
  char cVar2;
  int iVar3;
  uint uVar4;
  undefined2 uVar5;
  short sVar6;
  
  param_1 = param_1 & 0xff;
  if (param_1 < 2) {
    uVar4 = (uint)(param_2 != '\0');
    iVar3 = uVar4 + (short)param_1 * 0x5a;
    cVar2 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x31e8au + (uint32_t)(uVar4) * 1u))));
    iVar1 = uVar4 * 2;
    if ((uint8_t)cVar2 == *(volatile uint8_t *)camry_host_ptr(0xfebe3900u + (uint32_t)iVar3 + 0x40u)) {
      sVar6 = *(short *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe3900u + (uint32_t)(iVar1 + (short)param_1 * 0x5a + 0x42) * 1u))));
    }
    else {
      sVar6 = *(short *)(((undefined *)camry_host_ptr((uint32_t)(0x31e82u + (uint32_t)(iVar1) * 1u))));
    }
    if (sVar6 == 0) {
      uVar5 = 0;
    }
    else {
      if (sVar6 != -1) {
        sVar6 = sVar6 + -1;
      }
      uVar5 = 0x5a;
    }
    send_selected_rom_acquisition_frame_or_zeros_62714(param_1,uVar4,uVar5);
    *(short *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe3900u + (uint32_t)(iVar1 + (short)param_1 * 0x5a + 0x42) * 1u)))) = sVar6;
    *(volatile uint8_t *)camry_host_ptr(0xfebe3900u + (uint32_t)iVar3 + 0x40u) = (uint8_t)cVar2;
  }
  return;
}

void accumulate_serial_acquisition_failures(uchar channel)

{
  int iVar1;
  ushort uVar2;
  
  if (channel < 2) {
    uVar2 = (ushort)channel;
    iVar1 = (short)uVar2 * 0x5a;
    if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe3929u + (uint32_t)(iVar1) * 1u)))) == 'Z') {
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe38d0u + (uint32_t)((short)uVar2) * (uint32_t)sizeof(F33SerialAcquisitionRecord)) + (uint32_t)(0) * (uint32_t)sizeof(F33SerialAcquisitionRecord) + (uint32_t)offsetof(F33SerialAcquisitionRecord, rx_count_failures))))) =
           (*((volatile uint8_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe38d0u + (uint32_t)((short)uVar2) * (uint32_t)sizeof(F33SerialAcquisitionRecord)) + (uint32_t)(0) * (uint32_t)sizeof(F33SerialAcquisitionRecord) + (uint32_t)offsetof(F33SerialAcquisitionRecord, rx_count_failures))))) + '\x01';
    }
    if (((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe392au + (uint32_t)(iVar1) * 1u)))) == 'Z') || ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe392cu + (uint32_t)(iVar1) * 1u)))) == 'Z')) {
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe38d0u + (uint32_t)((short)uVar2) * (uint32_t)sizeof(F33SerialAcquisitionRecord)) + (uint32_t)(0) * (uint32_t)sizeof(F33SerialAcquisitionRecord) + (uint32_t)offsetof(F33SerialAcquisitionRecord, rx_or_tx_failures))))) =
           (*((volatile uint8_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe38d0u + (uint32_t)((short)uVar2) * (uint32_t)sizeof(F33SerialAcquisitionRecord)) + (uint32_t)(0) * (uint32_t)sizeof(F33SerialAcquisitionRecord) + (uint32_t)offsetof(F33SerialAcquisitionRecord, rx_or_tx_failures))))) + '\x01';
    }
    if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe392bu + (uint32_t)(iVar1) * 1u)))) == 'Z') {
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe38d0u + (uint32_t)((short)uVar2) * (uint32_t)sizeof(F33SerialAcquisitionRecord)) + (uint32_t)(0) * (uint32_t)sizeof(F33SerialAcquisitionRecord) + (uint32_t)offsetof(F33SerialAcquisitionRecord, crc_failures))))) =
           (*((volatile uint8_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe38d0u + (uint32_t)((short)uVar2) * (uint32_t)sizeof(F33SerialAcquisitionRecord)) + (uint32_t)(0) * (uint32_t)sizeof(F33SerialAcquisitionRecord) + (uint32_t)offsetof(F33SerialAcquisitionRecord, crc_failures))))) + '\x01';
    }
    if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe392du + (uint32_t)(iVar1) * 1u)))) == 'Z') {
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe38d0u + (uint32_t)((short)uVar2) * (uint32_t)sizeof(F33SerialAcquisitionRecord)) + (uint32_t)(0) * (uint32_t)sizeof(F33SerialAcquisitionRecord) + (uint32_t)offsetof(F33SerialAcquisitionRecord, sequence_failures))))) =
           (*((volatile uint8_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe38d0u + (uint32_t)((short)uVar2) * (uint32_t)sizeof(F33SerialAcquisitionRecord)) + (uint32_t)(0) * (uint32_t)sizeof(F33SerialAcquisitionRecord) + (uint32_t)offsetof(F33SerialAcquisitionRecord, sequence_failures))))) + '\x01';
    }
  }
  return;
}

void service_serial_acquisition_channel(uchar channel)

{
  byte bVar1;
  uint32_t puVar2;
  undefined4 uVar3;
  
  puVar2 = 0xfebeb800u;
  sample_serial_acquisition_channel(channel);
  bVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x7e28))))) & 3;
  if (((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x7e28))))) & 3) == 0) {
    pack_acquisition_status_command_and_consume_pending_bits_62636(channel,bVar1);
    uVar3 = 1;
LAB_00062880:
    snapshot_five_acquisition_halfwords_to_selected_slot_626d6(channel,uVar3);
  }
  else {
    if (bVar1 == 1) {
      uVar3 = 0;
    }
    else {
      uVar3 = 1;
      if (bVar1 == 2) {
        pack_acquisition_status_command_and_consume_pending_bits_62636(channel,1);
        uVar3 = 0;
        goto LAB_00062880;
      }
    }
    step_acquisition_rom_frame_countdown_6276c(channel,uVar3);
  }
  set_bounded_serial_transfer_count_60f7c(channel,0);
  accumulate_serial_acquisition_failures(channel);
  return;
}

void service_serial_acquisition_pair(void)

{
  uint uVar1;
  
  uVar1 = 0;
  do {
    service_serial_acquisition_channel((uchar)uVar1);
    uVar1 = uVar1 + 1;
  } while (uVar1 < 2);
  return;
}

void restore_serial_acquisition_pin_mux_and_dma_reload_628b2(void)

{
  uint uVar1;
  int iVar2;
  uint uVar3;
  
  uVar1 = Ramffc12110;
  uVar3 = 0;
  Ramffc12110 = uVar1 & 0xfff2ff88 | 0x50;
  uVar1 = Ramffc12178;
  Ramffc12178 = uVar1 & 0xfff2ff88 | 100;
  uVar1 = Ramffc12118;
  Ramffc12118 = uVar1 & 0xfff2ff88 | 0x60;
  uVar1 = Ramffc12044;
  Ramffc12044 = uVar1 & 0xfff2ff88 | 0x43;
  uVar1 = Ramffc12048;
  Ramffc12048 = uVar1 & 0xfff2ff88 | 0x55;
  uVar1 = Ramffc1204c;
  Ramffc1204c = uVar1 & 0xfff2ff88 | 0x65;
  uVar1 = Ramffc12050;
  Ramffc12050 = uVar1 & 0xfff2ff88 | 0x65;
  uVar1 = Ramffc120cc;
  Ramffc120cc = uVar1 & 0xfff2ff88 | 0x43;
  do {
    iVar2 = (short)uVar3 * 0x28;
    refresh_dma_reload_descriptor_and_selector_60a6a(((undefined *)camry_host_ptr((uint32_t)(0x314acu + (uint32_t)(iVar2) * 1u))));
    refresh_dma_reload_descriptor_and_selector_60a6a(&PTR_DAT_000314fc + (short)uVar3 * 10);
    refresh_dma_reload_descriptor_and_selector_60a6a(((undefined *)camry_host_ptr((uint32_t)(0x3154cu + (uint32_t)(iVar2) * 1u))));
    uVar3 = uVar3 + 1;
  } while (uVar3 < 2);
  return;
}

void rotate_and_copy_serial_acquisition_masks(F33SerialAcquisitionMasks *output)

{
  F33SerialAcquisitionMasks *pFVar1;
  ushort uVar2;
  int iVar3;
  int iVar4;
  uint uVar5;
  uint uVar6;
  
  uVar5 = 0;
  do {
    iVar4 = (short)uVar5 * 0x5a;
    uVar6 = (byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe392eu + (uint32_t)(iVar4) * 1u)))) & 3;
    iVar3 = (uVar6 - 1 & 3) * 2 + iVar4;
    *(undefined2 *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe3900u + (uint32_t)(iVar3 + 0x30) * 1u)))) = 0;
    *(undefined2 *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe3900u + (uint32_t)(iVar3 + 0x38) * 1u)))) = 0;
    uVar2 = *(ushort *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe3930u + (uint32_t)(uVar6 * 2 + iVar4) * 1u))));
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe392eu + (uint32_t)(iVar4) * 1u)))) = (char)uVar6 + 1U & 3;
    pFVar1 = output + uVar5;
    uVar5 = uVar5 + 1;
    pFVar1->first = uVar2;
    pFVar1->second = *(ushort *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe3900u + (uint32_t)(uVar6 * 2 + iVar4 + 0x38) * 1u))));
  } while (uVar5 < 2);
  return;
}

void copy_cached_serial_acquisition_records(F33SerialAcquisitionRecord *output)

{
  F33SerialAcquisitionRecord *pFVar1;
  ushort uVar2;
  short sVar3;
  uint uVar4;
  
  uVar4 = 0;
  do {
    sVar3 = (short)uVar4;
    pFVar1 = output + sVar3;
    if ((*((volatile uint8_t *)camry_host_ptr(0x31678u + uVar4))) == '\x11') {
      pFVar1->field14_0 = -(*((volatile uint16_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe38d0u + (uint32_t)(sVar3) * (uint32_t)sizeof(F33SerialAcquisitionRecord)) + (uint32_t)(0) * (uint32_t)sizeof(F33SerialAcquisitionRecord) + (uint32_t)offsetof(F33SerialAcquisitionRecord, field14_0))))) & 0x3fff;
      pFVar1->field14_1 = -(*((volatile uint16_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe38d0u + (uint32_t)(sVar3) * (uint32_t)sizeof(F33SerialAcquisitionRecord)) + (uint32_t)(0) * (uint32_t)sizeof(F33SerialAcquisitionRecord) + (uint32_t)offsetof(F33SerialAcquisitionRecord, field14_1))))) & 0x3fff;
      uVar2 = -(*((volatile uint16_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe38d0u + (uint32_t)(sVar3) * (uint32_t)sizeof(F33SerialAcquisitionRecord)) + (uint32_t)(0) * (uint32_t)sizeof(F33SerialAcquisitionRecord) + (uint32_t)offsetof(F33SerialAcquisitionRecord, field12))))) & 0xfff;
    }
    else {
      pFVar1->field14_0 = (*((volatile uint16_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe38d0u + (uint32_t)(sVar3) * (uint32_t)sizeof(F33SerialAcquisitionRecord)) + (uint32_t)(0) * (uint32_t)sizeof(F33SerialAcquisitionRecord) + (uint32_t)offsetof(F33SerialAcquisitionRecord, field14_0)))));
      pFVar1->field14_1 = (*((volatile uint16_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe38d0u + (uint32_t)(sVar3) * (uint32_t)sizeof(F33SerialAcquisitionRecord)) + (uint32_t)(0) * (uint32_t)sizeof(F33SerialAcquisitionRecord) + (uint32_t)offsetof(F33SerialAcquisitionRecord, field14_1)))));
      uVar2 = (*((volatile uint16_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe38d0u + (uint32_t)(sVar3) * (uint32_t)sizeof(F33SerialAcquisitionRecord)) + (uint32_t)(0) * (uint32_t)sizeof(F33SerialAcquisitionRecord) + (uint32_t)offsetof(F33SerialAcquisitionRecord, field12)))));
    }
    pFVar1->field12 = uVar2;
    uVar4 = uVar4 + 1;
    pFVar1->rx_count_failures = (*((volatile uint8_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe38d0u + (uint32_t)(sVar3) * (uint32_t)sizeof(F33SerialAcquisitionRecord)) + (uint32_t)(0) * (uint32_t)sizeof(F33SerialAcquisitionRecord) + (uint32_t)offsetof(F33SerialAcquisitionRecord, rx_count_failures)))));
    pFVar1->rx_or_tx_failures = (*((volatile uint8_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe38d0u + (uint32_t)(sVar3) * (uint32_t)sizeof(F33SerialAcquisitionRecord)) + (uint32_t)(0) * (uint32_t)sizeof(F33SerialAcquisitionRecord) + (uint32_t)offsetof(F33SerialAcquisitionRecord, rx_or_tx_failures)))));
    pFVar1->crc_failures = (*((volatile uint8_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe38d0u + (uint32_t)(sVar3) * (uint32_t)sizeof(F33SerialAcquisitionRecord)) + (uint32_t)(0) * (uint32_t)sizeof(F33SerialAcquisitionRecord) + (uint32_t)offsetof(F33SerialAcquisitionRecord, crc_failures)))));
    pFVar1->sequence_failures = (*((volatile uint8_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe38d0u + (uint32_t)(sVar3) * (uint32_t)sizeof(F33SerialAcquisitionRecord)) + (uint32_t)(0) * (uint32_t)sizeof(F33SerialAcquisitionRecord) + (uint32_t)offsetof(F33SerialAcquisitionRecord, sequence_failures)))));
  } while (uVar4 < 2);
  return;
}

void or_pending_acquisition_command_bits_under_mask_62a16(uint param_1,uint param_2,ushort param_3)

{
  uint32_t puVar1;
  uint saved_mask;
  
  puVar1 = 0xfebeb800u;
  if (((param_1 & 0xff) < 2) && ((param_2 & 0xff) < 2)) {
    saved_mask = priority_mask_enter(0xffc0);
    (*((ushort *)camry_host_ptr((uint32_t)(puVar1 + ((param_2 & 0xff) + (param_1 & 0xff) * 2) * 2 + -0x7f38)))) =
         (*((ushort *)camry_host_ptr((uint32_t)(puVar1 + ((param_2 & 0xff) + (param_1 & 0xff) * 2) * 2 + -0x7f38)))) | param_3;
    priority_mask_restore(saved_mask);
  }
  return;
}

uint32_t copy_transfer_group6_samples(ushort *destination)

{
  uint32_t camry_r10_result;
  int iVar1;
  int iVar2;
  ushort uVar3;
  ushort uVar4;
  int iVar5;
  
  uVar3 = (camry_r10_result = count_transfer_entries('\x06'));
  iVar5 = 0;
  do {
    uVar4 = (camry_r10_result = consume_adc0_ring_sample_u16_60630((byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x30f20u + (uint32_t)(iVar5) * 1u)))) + uVar3));
    destination[iVar5] = uVar4;
    iVar2 = iVar5 + 1;
    iVar1 = iVar5 + -3;
    iVar5 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  return camry_r10_result;
}

uint32_t copy_transfer_group14_samples(ushort *destination)

{
  uint32_t camry_r10_result;
  int iVar1;
  int iVar2;
  ushort uVar3;
  ushort uVar4;
  int iVar5;
  
  uVar3 = (camry_r10_result = count_transfer_entries('\x0e'));
  iVar5 = 0;
  do {
    uVar4 = (camry_r10_result = consume_adc1_ring_sample_u16_606da((byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x30f44u + (uint32_t)(iVar5) * 1u)))) + uVar3));
    destination[iVar5 + 4] = uVar4;
    iVar2 = iVar5 + 1;
    iVar1 = iVar5 + -4;
    iVar5 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  return camry_r10_result;
}

uint32_t copy_acquisition_diagnostic_samples(ushort *destination)

{
  uint32_t camry_r10_result;
  (camry_r10_result = copy_transfer_group6_samples(destination));
  (camry_r10_result = copy_transfer_group14_samples(destination));
  return camry_r10_result;
}

void read_adc0_transfer_relative_sample_62ad0(undefined2 *param_1)

{
  ushort uVar1;
  undefined2 uVar2;
  
  uVar1 = count_transfer_entries('\x06');
  uVar2 = consume_adc0_ring_sample_u16_60630(DAT_00030f3f + uVar1);
  *param_1 = uVar2;
  return;
}

void read_adc1_transfer_relative_sample_62af4(int param_1)

{
  ushort uVar1;
  undefined2 uVar2;
  
  uVar1 = count_transfer_entries('\x0e');
  uVar2 = consume_adc1_ring_sample_u16_606da(DAT_00030f40 + uVar1);
  (*((undefined2 *)camry_host_ptr((uint32_t)(param_1 + 2)))) = uVar2;
  return;
}

void read_paired_adc_transfer_samples_and_clear_metadata_62b18(int param_1)

{
  read_adc0_transfer_relative_sample_62ad0(((undefined2 *)camry_host_ptr((uint32_t)(param_1))));
  read_adc1_transfer_relative_sample_62af4(param_1);
  (*((undefined2 *)camry_host_ptr((uint32_t)(param_1 + 4)))) = 0;
  (*((undefined4 *)camry_host_ptr((uint32_t)(param_1 + 8)))) = 0;
  return;
}

uint32_t read_and_reorder_both_capture_status_records_62b32(int param_1)

{
  uint32_t camry_r10_result;
  uint8_t stack_record_14[20];
  int iVar1;
  undefined2 *puVar2;
  int iVar3;
  uint uVar4;
  int iVar5;
  
  iVar5 = 0;
  do {
    uVar4 = (camry_r10_result = read_transfer_descriptor_head((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x3125cu + (uint32_t)((short)iVar5 * 0x28) * 1u))))));
    read_capture_status_and_consume_overrun_bit_60c60(iVar5,uVar4 < iVar5 * 0x30 + 0xfeef9110U,stack_record_14);
    iVar3 = iVar5 + 1;
    puVar2 = ((undefined2 *)camry_host_ptr((uint32_t)(iVar5 * 8 + param_1)));
    iVar1 = iVar5 + -1;
    *puVar2 = (*((uint16_t *)(stack_record_14 + 4)));
    puVar2[1] = (*((uint16_t *)(stack_record_14 + 6)));
    puVar2[2] = (*((uint16_t *)(stack_record_14 + 2)));
    puVar2[3] = (*((uint16_t *)(stack_record_14 + 0)));
    iVar5 = iVar3;
  } while (((iVar1 < 0) || (iVar3 < 0)));
  return camry_r10_result;
}

void store_three_pattern_encoded_control_words_62b90(uint param_1)

{
  Ramffc0a000 = param_1;
  Ramffc0a004 = param_1 ^ 0x55555555;
  Ramffc0a008 = param_1 ^ 0xaaaaaaaa;
  return;
}

void startup_capture_retained_token(void)

{
  DAT_febe39b4 = Ramffc0a000;
  DAT_febe8de4 = Ramffc0a004;
  DAT_febe8df8 = Ramffc0a008;
  DAT_febe39b8 = Ramffc0a00c;
  Ramffc0a000 = 0xa5a5a5a5;
  Ramffc0a004 = 0xf0f0f0f0;
  Ramffc0a008 = 0xf0f0f0f;
  Ramffc0a00c = 0;
  return;
}

void clear_three_pattern_encoded_control_words_62be8(void)

{
  Ramffc0a000 = 0;
  Ramffc0a004 = 0;
  Ramffc0a008 = 0;
  return;
}

void startup_classify_retained_token(void)

{
  DAT_febe39bf = 0;
  DAT_febe39be = 0;
  DAT_febe39bd = 0;
  DAT_febe39bc = 0;
  if (((DAT_febe39b4 == -0x64646465) && (DAT_febe8de4 == -0x31313132)) &&
     (DAT_febe8df8 == 0x31313131)) {
    DAT_febe39bc = 0x5a;
  }
  if (((DAT_febe39b4 == 0x3e3e3e3e) && (DAT_febe8de4 == 0x6b6b6b6b)) &&
     (DAT_febe8df8 == -0x6b6b6b6c)) {
    DAT_febe39bd = 0x5a;
  }
  if (((DAT_febe39b4 == 0x6d6d6d6d) && (DAT_febe8de4 == 0x38383838)) &&
     (DAT_febe8df8 == -0x38383839)) {
    DAT_febe39be = 0x5a;
  }
  if ((((DAT_febe39b4 == 0x5a5a5a5a) && (DAT_febe8de4 == 0xf0f0f0f)) && (DAT_febe8df8 == -0xf0f0f10)
      ) && ((DAT_febe39b8 & 0xff000000) == 0x5a000000)) {
    DAT_febe39bf = 0x5a;
  }
  store_three_pattern_encoded_control_words_62b90(0x7c7c7c7c);
  DAT_fff81008 = 1;
  return;
}

uint compose_serial_and_monitor_failure_bitmap_62cd4(void)

{
  char cVar1;
  char cVar2;
  char cVar3;
  char cVar4;
  char cVar5;
  char cVar6;
  uint32_t puVar7;
  uint32_t puVar8;
  uint uVar9;
  
  cVar6 = DAT_febe39bf;
  cVar5 = DAT_febe39be;
  cVar4 = DAT_febe39bd;
  cVar3 = DAT_febe39bc;
  cVar2 = DAT_febe3846;
  cVar1 = DAT_febe3840;
  uVar9 = 0;
  puVar7 = (read_validated_a55a_marker_febe39d4_64d00());
  puVar8 = (read_validated_a55a_marker_febe39d6_64d2c());
  if ((cVar2 == 'Z') || (cVar1 == 'Z')) {
    uVar9 = 1;
  }
  if ((puVar7)==((uint32_t)(0xa55au))) {
    uVar9 = uVar9 | 0x1000;
  }
  if ((puVar8)==((uint32_t)(0xa55au))) {
    uVar9 = uVar9 | 0x10000;
  }
  if (cVar3 == 'Z') {
    uVar9 = uVar9 | 0x100000;
  }
  if (cVar4 == 'Z') {
    uVar9 = uVar9 | 0x10000000;
  }
  if (cVar5 == 'Z') {
    uVar9 = uVar9 | 0x80000000;
  }
  if (cVar6 == 'Z') {
    uVar9 = uVar9 | 0x10;
  }
  return uVar9;
}

void return_only_stub_62d54(void)

{
  return;
}

undefined4 zero_output_halfword_and_return_success_62d56(undefined2 *param_1)

{
  *param_1 = 0;
  return 0;
}

void startup_publish_image_identity_check(void)

{
  uint uVar1;
  uint32_t puVar2;
  int iVar3;
  undefined1 uVar4;
  
  puVar2 = 0xfebeb800u;
  iVar3 = 0;
  uVar4 = 0;
  uVar1 = 0;
  do {
    if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x20850u + (uint32_t)(uVar1) * 1u)))) != (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x17da0u + (uint32_t)(uVar1) * 1u))))) {
      iVar3 = -0x5aa55aa6;
      uVar4 = 0x5a;
    }
    uVar1 = uVar1 + 1;
  } while (uVar1 < 8);
  if ((iVar3 == 0) &&
     ((((DAT_00017dc0 != DAT_00020870 || (DAT_00017dc1 != DAT_00020871)) ||
       (DAT_00017dc2 != DAT_00020872)) ||
      ((DAT_00017dc3 != DAT_00020873 || (((volatile uint8_t *)camry_host_ptr(0x17dc4u))[0] != DAT_00020874)))))) {
    iVar3 = -0x5aa55aa6;
  }
  write_xor_redundant_u32_70a92(iVar3,((undefined *)camry_host_ptr(0xfebf0668u)),((undefined *)camry_host_ptr(0xfebf10a4u)),((undefined *)camry_host_ptr(0xfebf10c8u)));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(0x4e6c))))) = uVar4;
  return;
}

void republish_image_identity_on_redundant_check_error_62df0(void)

{
  int iVar1;
  undefined1 auStack_8 [4];
  
  iVar1 = read_xor_redundant_u32_with_vote_status_70822(((undefined *)camry_host_ptr(0xfebf0668u)),((undefined *)camry_host_ptr(0xfebf10a4u)),((undefined *)camry_host_ptr(0xfebf10c8u)),auStack_8);
  if (iVar1 != 0) {
    startup_publish_image_identity_check();
  }
  return;
}

undefined1 get_identity_byte_febf066c_62e18(void)

{
  return DAT_febf066c;
}

void enable_irqs_then_enter_terminal_loop_62e1e(undefined4 param_1, undefined4 param_2, undefined4 param_3, undefined4 param_4)

{
  uint uVar1;
  uint uVar2;
  uint uVar3;
  uint in_FPEC = camry_SR[0][11];
  uint in_RBASE = camry_SR[1][2];
  uint in_EBASE = camry_SR[1][3];
  uint in_FPIPR = camry_SR[1][7];
  uint in_ISPR = camry_SR[2][10];
  
  if ((in_FPEC & 1) != 0) {
    uVar1 = in_FPIPR & 0x1f;
    if (0xf < uVar1) {
      uVar1 = 0x10;
    }
    uVar2 = uVar1;
    if (0xf < uVar1) {
      uVar2 = 0xf;
    }
    uVar3 = PMR;
    if ((((uVar3 & 1 << uVar2) == 0) && ((in_ISPR & (1 << uVar1 + 1) - 1U & 0xffff) == 0)) &&
       ((camry_psw & 0x80) == 0)) {
      if (((camry_psw & 0xbfffffd0) >> 0xf & 1) == 0) {
        in_EBASE = in_RBASE;
      }
      (*(int (*)())camry_indirect((uint32_t)((in_EBASE & 0xfffffe00) + 0x70)))();
    }
  }
  __enable_irq();
  save_registers_and_callt_state_to_ep_frame_712ce(param_1, param_2, param_3, param_4);
  do {
                    /* WARNING: Do nothing block with infinite loop */
  } while( true );
}

void write_halfword_verify_low_nibble_or_terminate_62e44(ushort *param_1,ushort param_2)

{
  byte bVar1;
  
  bVar1 = 0;
  do {
    *param_1 = param_2;
    bVar1 = bVar1 + 1;
    __synchronize();
    if (((*param_1 ^ param_2) & 0xf) == 0) {
      return;
    }
  } while (bVar1 < 10);
                    /* WARNING: Subroutine does not return */
  enter_terminal_hardware_sequence();
}

void initialize_interrupt_control_words_and_verify_priorities_62e6a(void)

{
  DAT_fffeea12 = 0xcf;
  DAT_fffeea20 = 0xcf;
  DAT_fffeea22 = 0xcf;
  DAT_fffeea24 = 0xcf;
  DAT_fffeea26 = 0xcf;
  DAT_fffeea28 = 0xcf;
  DAT_fffeea2a = 0xcf;
  DAT_fffeea2c = 0xcf;
  DAT_fffeea2e = 0xcf;
  DAT_fffeea30 = 0xcf;
  DAT_fffeea32 = 0xcf;
  DAT_fffeea34 = 0xcf;
  DAT_fffeea36 = 0xcf;
  DAT_fffeea38 = 0xcf;
  DAT_fffeea3a = 0xcf;
  DAT_fffeea3c = 0xcf;
  DAT_fffeea3e = 0xcf;
  DAT_ffffb040 = 0xcf;
  DAT_ffffb042 = 0xcf;
  DAT_ffffb044 = 0xcf;
  DAT_ffffb046 = 0xcf;
  DAT_ffffb048 = 0xcf;
  DAT_ffffb050 = 0xcf;
  DAT_ffffb052 = 0xcf;
  DAT_ffffb054 = 0xcf;
  DAT_ffffb056 = 0xcf;
  DAT_ffffb058 = 0xcf;
  DAT_ffffb05a = 0xcf;
  DAT_ffffb05c = 0xcf;
  DAT_ffffb05e = 0xcf;
  DAT_ffffb060 = 0xcf;
  DAT_ffffb062 = 0xcf;
  DAT_ffffb064 = 0xcf;
  DAT_ffffb066 = 0xcf;
  DAT_ffffb068 = 0xcf;
  DAT_ffffb06a = 0xcf;
  DAT_ffffb06c = 0xcf;
  DAT_ffffb06e = 0xcf;
  DAT_ffffb070 = 0xcf;
  DAT_ffffb072 = 0xcf;
  DAT_ffffb074 = 0xcf;
  DAT_ffffb076 = 0xcf;
  DAT_ffffb078 = 0xcf;
  DAT_ffffb07a = 0xcf;
  DAT_ffffb07c = 0xcf;
  DAT_ffffb07e = 0xcf;
  DAT_ffffb080 = 0xcf;
  DAT_ffffb082 = 0xcf;
  DAT_ffffb084 = 0xcf;
  DAT_ffffb086 = 0xcf;
  DAT_ffffb088 = 0xcf;
  DAT_ffffb08a = 0xcf;
  DAT_ffffb08c = 0xcf;
  DAT_ffffb08e = 0xcf;
  DAT_ffffb090 = 0xcf;
  DAT_ffffb092 = 0xcf;
  DAT_ffffb094 = 0xcf;
  DAT_ffffb096 = 0xcf;
  DAT_ffffb098 = 0xcf;
  DAT_ffffb09a = 0xcf;
  DAT_ffffb09c = 0xcf;
  DAT_ffffb09e = 0xcf;
  DAT_ffffb0a0 = 0xcf;
  DAT_ffffb0a2 = 0xcf;
  DAT_ffffb0a4 = 0xcf;
  DAT_ffffb0a6 = 0xcf;
  DAT_ffffb0a8 = 0xcf;
  DAT_ffffb0aa = 0xcf;
  DAT_ffffb0ac = 0xcf;
  DAT_ffffb0ae = 0xcf;
  DAT_ffffb0b0 = 0xcf;
  DAT_ffffb0b2 = 0xcf;
  DAT_ffffb0b4 = 0xcf;
  DAT_ffffb0b6 = 0xcf;
  DAT_ffffb0b8 = 0xcf;
  DAT_ffffb0ba = 0xcf;
  DAT_ffffb0bc = 0xcf;
  DAT_ffffb0be = 0xcf;
  DAT_ffffb0c0 = 0xcf;
  DAT_ffffb0c2 = 0xcf;
  DAT_ffffb0c4 = 0xcf;
  DAT_ffffb0c6 = 0xcf;
  DAT_ffffb0c8 = 0xcf;
  DAT_ffffb0ca = 0xcf;
  DAT_ffffb0cc = 0xcf;
  DAT_ffffb0ce = 0xcf;
  DAT_ffffb0d0 = 0xcf;
  DAT_ffffb0d2 = 0xcf;
  DAT_ffffb0d4 = 0x80cf;
  DAT_ffffb0d6 = 0xcf;
  DAT_ffffb0d8 = 0xcf;
  DAT_ffffb0da = 0x80cf;
  DAT_ffffb0dc = 0x80cf;
  DAT_ffffb0de = 0xcf;
  DAT_ffffb0e0 = 0xcf;
  DAT_ffffb0e2 = 0x80cf;
  DAT_ffffb0e4 = 0xcf;
  DAT_ffffb0e6 = 0xcf;
  DAT_ffffb0e8 = 0xcf;
  DAT_ffffb0ea = 0xcf;
  DAT_ffffb0ec = 0xcf;
  DAT_ffffb0ee = 0xcf;
  DAT_ffffb0f0 = 0x80cf;
  DAT_ffffb0f2 = 0x80cf;
  DAT_ffffb100 = 0xcf;
  DAT_ffffb102 = 0xcf;
  DAT_ffffb104 = 0xcf;
  DAT_ffffb106 = 0xcf;
  DAT_ffffb108 = 0xcf;
  EIC136 = (uint16_t)0xcf;
  DAT_ffffb112 = 0xcf;
  DAT_ffffb114 = 0xcf;
  DAT_ffffb116 = 0xcf;
  DAT_ffffb118 = 0xcf;
  DAT_ffffb11a = 0xcf;
  DAT_ffffb11c = 0xcf;
  DAT_ffffb11e = 0xcf;
  DAT_ffffb120 = 0xcf;
  DAT_ffffb122 = 0xcf;
  DAT_ffffb12a = 0xcf;
  DAT_ffffb12c = 0xcf;
  DAT_ffffb12e = 0xcf;
  DAT_ffffb130 = 0xcf;
  DAT_ffffb132 = 0xcf;
  DAT_ffffb134 = 0xcf;
  DAT_ffffb136 = 0xcf;
  DAT_ffffb138 = 0xcf;
  DAT_ffffb13c = 0xcf;
  DAT_ffffb13e = 0xcf;
  DAT_ffffb140 = 0xcf;
  DAT_ffffb142 = 0xcf;
  DAT_ffffb144 = 0xcf;
  DAT_ffffb146 = 0xcf;
  DAT_ffffb148 = 0xcf;
  DAT_ffffb14a = 0xcf;
  DAT_ffffb14c = 0xcf;
  DAT_ffffb14e = 0xcf;
  DAT_ffffb150 = 0xcf;
  DAT_ffffb152 = 0xcf;
  DAT_ffffb154 = 0xcf;
  DAT_ffffb158 = 0xcf;
  DAT_ffffb15a = 0xcf;
  DAT_ffffb15c = 0xcf;
  DAT_ffffb15e = 0xcf;
  DAT_ffffb160 = 0xcf;
  DAT_ffffb162 = 0xcf;
  DAT_ffffb164 = 0xcf;
  DAT_ffffb166 = 0xcf;
  DAT_ffffb168 = 0xcf;
  DAT_ffffb16a = 0xcf;
  DAT_ffffb16c = 0xcf;
  DAT_ffffb16e = 0x80cf;
  DAT_ffffb174 = 0x80cf;
  DAT_ffffb17a = 0x80cf;
  DAT_ffffb17c = 0x80cf;
  DAT_ffffb17e = 0x80cf;
  DAT_ffffb180 = 0x80cf;
  DAT_ffffb182 = 0x80cf;
  DAT_ffffb184 = 0x80cf;
  DAT_ffffb186 = 0x80cf;
  DAT_ffffb188 = 0x80cf;
  DAT_ffffb18a = 0x80cf;
  DAT_ffffb18c = 0x80cf;
  DAT_ffffb18e = 0x80cf;
  DAT_ffffb190 = 0x80cf;
  DAT_ffffb192 = 0x80cf;
  DAT_ffffb194 = 0x80cf;
  DAT_ffffb196 = 0x80cf;
  DAT_ffffb198 = 0x80cf;
  DAT_ffffb1b4 = 0x80cf;
  DAT_ffffb1b6 = 0xcf;
  DAT_ffffb1b8 = 0xcf;
  DAT_ffffb1ba = 0x80cf;
  DAT_ffffb1c4 = 0x80cf;
  DAT_ffffb1c6 = 0x80cf;
  DAT_ffffb1c8 = 0x80cf;
  DAT_ffffb1ca = 0x80cf;
  DAT_ffffb1cc = 0x80cf;
  DAT_ffffb1ce = 0x80cf;
  DAT_ffffb1d0 = 0x80cf;
  DAT_ffffb1d2 = 0xcf;
  DAT_ffffb1d4 = 0x80cf;
  DAT_ffffb1d6 = 0xcf;
  DAT_ffffb1d8 = 0x80cf;
  DAT_ffffb1da = 0xcf;
  DAT_ffffb1dc = 0x80cf;
  DAT_ffffb1de = 0xcf;
  DAT_ffffb1e0 = 0x80cf;
  DAT_ffffb1e2 = 0xcf;
  DAT_ffffb1e4 = 0x80cf;
  DAT_ffffb1e6 = 0xcf;
  DAT_ffffb1e8 = 0x80cf;
  DAT_ffffb1ea = 0x80cf;
  DAT_ffffb1ec = 0x80cf;
  DAT_ffffb1ee = 0x80cf;
  DAT_ffffb1f0 = 0x80cf;
  DAT_ffffb1f2 = 0x80cf;
  DAT_ffffb1f4 = 0x80cf;
  DAT_ffffb1f6 = 0x80cf;
  DAT_ffffb1f8 = 0x80cf;
  DAT_ffffb1fa = 0x80cf;
  DAT_ffffb1fc = 0x80cf;
  DAT_ffffb200 = 0xcf;
  DAT_ffffb202 = 0xcf;
  DAT_ffffb204 = 0xcf;
  DAT_ffffb206 = 0xcf;
  DAT_ffffb208 = 0xcf;
  DAT_ffffb20a = 0xcf;
  DAT_ffffb20c = 0xcf;
  DAT_ffffb20e = 0xcf;
  DAT_ffffb210 = 0xcf;
  DAT_ffffb212 = 0xcf;
  DAT_ffffb214 = 0xcf;
  DAT_ffffb216 = 0xcf;
  DAT_ffffb218 = 0xcf;
  DAT_ffffb21a = 0xcf;
  DAT_ffffb21c = 0xcf;
  DAT_ffffb21e = 0xcf;
  DAT_ffffb220 = 0xcf;
  DAT_ffffb222 = 0xcf;
  DAT_ffffb224 = 0xcf;
  DAT_ffffb226 = 0xcf;
  DAT_ffffb228 = 0xcf;
  DAT_ffffb22a = 0xcf;
  DAT_ffffb22c = 0xcf;
  DAT_ffffb22e = 0xcf;
  DAT_ffffb230 = 0xcf;
  DAT_ffffb232 = 0xcf;
  DAT_ffffb234 = 0xcf;
  DAT_ffffb236 = 0xcf;
  DAT_ffffb238 = 0xcf;
  DAT_ffffb23a = 0xcf;
  DAT_ffffb23c = 0xcf;
  DAT_ffffb23e = 0xcf;
  DAT_ffffb240 = 0xcf;
  DAT_ffffb242 = 0xcf;
  DAT_ffffb244 = 0xcf;
  DAT_ffffb246 = 0xcf;
  DAT_ffffb24c = 0xcf;
  DAT_ffffb24e = 0xcf;
  DAT_ffffb250 = 0xcf;
  DAT_ffffb252 = 0xcf;
  DAT_ffffb254 = 0xcf;
  DAT_ffffb2fe = 0x80cf;
  write_halfword_verify_low_nibble_or_terminate_62e44(((ushort *)camry_host_ptr((uint32_t)((0xfffeea10u)))), 0x40);
  write_halfword_verify_low_nibble_or_terminate_62e44(((ushort *)camry_host_ptr((uint32_t)((0xffffb10au)))), 0x46);
  write_halfword_verify_low_nibble_or_terminate_62e44(((ushort *)camry_host_ptr((uint32_t)((0xffffb10cu)))), 0x47);
  write_halfword_verify_low_nibble_or_terminate_62e44(((ushort *)camry_host_ptr((uint32_t)((0xffffb10eu)))), 0x49);
  DAT_ffffb124 = 0xcf;
  DAT_ffffb126 = 0xcf;
  DAT_ffffb128 = 0xcf;
  DAT_ffffb156 = 0xcf;
  DAT_ffffb170 = 0x80cf;
  DAT_ffffb172 = 0x80cf;
  write_halfword_verify_low_nibble_or_terminate_62e44(((ushort *)camry_host_ptr((uint32_t)((0xffffb176u)))), 0x8048);
  write_halfword_verify_low_nibble_or_terminate_62e44(((ushort *)camry_host_ptr((uint32_t)((0xffffb178u)))), 0x8048);
  write_halfword_verify_low_nibble_or_terminate_62e44(((ushort *)camry_host_ptr((uint32_t)((0xffffb248u)))), 0x48);
  write_halfword_verify_low_nibble_or_terminate_62e44(((ushort *)camry_host_ptr((uint32_t)((0xffffb24au)))), 0x48);
  write_halfword_verify_low_nibble_or_terminate_62e44(((ushort *)camry_host_ptr((uint32_t)((0xffffb2f6u)))), 0x48);
  return;
}
