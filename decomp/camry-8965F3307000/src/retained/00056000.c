#include "common.h"

undefined4 serialize_capture_pair_field26_scaled_signed_1000_over_256_5602e(char param_1,undefined4 param_2)

{
  undefined4 uVar1;
  undefined2 *puVar2;
  
  puVar2 = (undefined2 *)((undefined *)camry_host_ptr(0xfebe86e4u));
  if (param_1 == '\0') {
    puVar2 = ((undefined *)camry_host_ptr(0xfebe8684u));
  }
  uVar1 = scale_s16_by1000_over256_clamp_25000_53608((int)(short)puVar2[0x13]);
  store_low_u16_big_endian_bytes_6a5ac(uVar1, ((undefined1 *)camry_host_ptr((uint32_t)(param_2))));
  return uVar1;
}

undefined4 serialize_capture_pair_field28_scaled_signed_1000_over_256_56052(char param_1,undefined4 param_2)

{
  undefined4 uVar1;
  undefined2 *puVar2;
  
  puVar2 = (undefined2 *)((undefined *)camry_host_ptr(0xfebe86e4u));
  if (param_1 == '\0') {
    puVar2 = ((undefined *)camry_host_ptr(0xfebe8684u));
  }
  uVar1 = scale_s16_by1000_over256_clamp_25000_53608((int)(short)puVar2[0x14]);
  store_low_u16_big_endian_bytes_6a5ac(uVar1, ((undefined1 *)camry_host_ptr((uint32_t)(param_2))));
  return uVar1;
}

undefined4 serialize_capture_pair_field2a_scaled_signed_1000_over_256_56076(char param_1,undefined4 param_2)

{
  undefined4 uVar1;
  undefined2 *puVar2;
  
  puVar2 = (undefined2 *)((undefined *)camry_host_ptr(0xfebe86e4u));
  if (param_1 == '\0') {
    puVar2 = ((undefined *)camry_host_ptr(0xfebe8684u));
  }
  uVar1 = scale_s16_by1000_over256_clamp_25000_53608((int)(short)puVar2[0x15]);
  store_low_u16_big_endian_bytes_6a5ac(uVar1, ((undefined1 *)camry_host_ptr((uint32_t)(param_2))));
  return uVar1;
}

undefined4 serialize_capture_pair_field2c_scaled_signed_1000_over_256_5609a(char param_1,undefined4 param_2)

{
  undefined4 uVar1;
  undefined2 *puVar2;
  
  puVar2 = (undefined2 *)((undefined *)camry_host_ptr(0xfebe86e4u));
  if (param_1 == '\0') {
    puVar2 = ((undefined *)camry_host_ptr(0xfebe8684u));
  }
  uVar1 = scale_s16_by1000_over256_clamp_25000_53608((int)(short)puVar2[0x16]);
  store_low_u16_big_endian_bytes_6a5ac(uVar1, ((undefined1 *)camry_host_ptr((uint32_t)(param_2))));
  return uVar1;
}

undefined4 serialize_capture_pair_field2e_scaled_signed_100_over_128_560be(char param_1,undefined4 param_2)

{
  undefined4 uVar1;
  undefined2 *puVar2;
  
  puVar2 = (undefined2 *)((undefined *)camry_host_ptr(0xfebe86e4u));
  if (param_1 == '\0') {
    puVar2 = ((undefined *)camry_host_ptr(0xfebe8684u));
  }
  uVar1 = scale_s16_by100_over128_clamp_symmetric32767_53686((int)(short)puVar2[0x17]);
  store_low_u16_big_endian_bytes_6a5ac(uVar1, ((undefined1 *)camry_host_ptr((uint32_t)(param_2))));
  return uVar1;
}

undefined4 serialize_capture_pair_field30_scaled_signed_100_over_128_560e2(char param_1,undefined4 param_2)

{
  undefined4 uVar1;
  undefined2 *puVar2;
  
  puVar2 = (undefined2 *)((undefined *)camry_host_ptr(0xfebe86e4u));
  if (param_1 == '\0') {
    puVar2 = ((undefined *)camry_host_ptr(0xfebe8684u));
  }
  uVar1 = scale_s16_by100_over128_clamp_symmetric32767_53686((int)(short)puVar2[0x18]);
  store_low_u16_big_endian_bytes_6a5ac(uVar1, ((undefined1 *)camry_host_ptr((uint32_t)(param_2))));
  return uVar1;
}

undefined4 serialize_capture_pair_field32_scaled_signed_100_over_128_56106(char param_1,undefined4 param_2)

{
  undefined4 uVar1;
  undefined2 *puVar2;
  
  puVar2 = (undefined2 *)((undefined *)camry_host_ptr(0xfebe86e4u));
  if (param_1 == '\0') {
    puVar2 = ((undefined *)camry_host_ptr(0xfebe8684u));
  }
  uVar1 = scale_s16_by100_over128_clamp_symmetric32767_53686((int)(short)puVar2[0x19]);
  store_low_u16_big_endian_bytes_6a5ac(uVar1, ((undefined1 *)camry_host_ptr((uint32_t)(param_2))));
  return uVar1;
}

undefined4 serialize_capture_pair_field34_scaled_signed_100_over_128_5612a(char param_1,undefined4 param_2)

{
  undefined4 uVar1;
  undefined2 *puVar2;
  
  puVar2 = (undefined2 *)((undefined *)camry_host_ptr(0xfebe86e4u));
  if (param_1 == '\0') {
    puVar2 = ((undefined *)camry_host_ptr(0xfebe8684u));
  }
  uVar1 = scale_s16_by100_over128_clamp_symmetric32767_53686((int)(short)puVar2[0x1a]);
  store_low_u16_big_endian_bytes_6a5ac(uVar1, ((undefined1 *)camry_host_ptr((uint32_t)(param_2))));
  return uVar1;
}

void serialize_capture_pair_field38_scaled_36000_over_65536_5614e(char param_1, undefined4 param_2)

{
  uint32_t puVar1;
  undefined2 *puVar2;
  
  puVar2 = (undefined2 *)((undefined *)camry_host_ptr(0xfebe86e4u));
  if (param_1 == '\0') {
    puVar2 = ((undefined *)camry_host_ptr(0xfebe8684u));
  }
  puVar1 = ((uint32_t)((uint)(ushort)puVar2[0x1c] * 36000 >> 0x10));
  if (((uint32_t)(0x8c9fu))<(puVar1)) {
    puVar1 = (0x8ca0u);
  }
  store_low_u16_big_endian_bytes_6a574((puVar1), ((undefined1 *)camry_host_ptr((uint32_t)(param_2))));
  return;
}

void serialize_capture_pair_field36_scaled_nonnegative_100_over_128_5617e(char param_1,undefined4 param_2)

{
  undefined2 *puVar1;
  short sStack_a;
  
  puVar1 = (undefined2 *)((undefined *)camry_host_ptr(0xfebe86e4u));
  if (param_1 == '\0') {
    puVar1 = ((undefined *)camry_host_ptr(0xfebe8684u));
  }
  sStack_a = (short)(((short)puVar1[0x1b] * 100) / 0x80);
  store_s16_max_third_min_first_two_70110((int)sStack_a,0x7fff,0,&sStack_a);
  store_low_u16_big_endian_bytes_6a5ac((int)sStack_a, ((undefined1 *)camry_host_ptr((uint32_t)(param_2))));
  return;
}

void serialize_capture_pair_field3c_capped_30000_561c0(char param_1, undefined4 param_2)

{
  ushort uVar1;
  undefined2 *puVar2;
  
  puVar2 = (undefined2 *)((undefined *)camry_host_ptr(0xfebe86e4u));
  if (param_1 == '\0') {
    puVar2 = ((undefined *)camry_host_ptr(0xfebe8684u));
  }
  uVar1 = puVar2[0x1e];
  if (29999 < uVar1) {
    uVar1 = 30000;
  }
  store_low_u16_big_endian_bytes_6a574(uVar1, ((undefined1 *)camry_host_ptr((uint32_t)(param_2))));
  return;
}

void serialize_capture_pair_field3e_clamped_signed16_561e8(char param_1, undefined4 param_2)

{
  int iVar1;
  undefined2 *puVar2;
  
  puVar2 = (undefined2 *)((undefined *)camry_host_ptr(0xfebe86e4u));
  if (param_1 == '\0') {
    puVar2 = ((undefined *)camry_host_ptr(0xfebe8684u));
  }
  iVar1 = (int)(short)puVar2[0x1f];
  if (iVar1 + -0x7fff < 0 == (iVar1 < 0 && -1 < iVar1 + -0x7fff)) {
    iVar1 = 0x7fff;
  }
  if (iVar1 + 0x7fff < 0 != (-1 < iVar1 && iVar1 + 0x7fff < 0)) {
    iVar1 = -0x7fff;
  }
  store_low_u16_big_endian_bytes_6a5ac(iVar1, ((undefined1 *)camry_host_ptr((uint32_t)(param_2))));
  return;
}

void serialize_capture_slot_time_and_presence_56246(int param_1,int param_2)

{
  char cVar1;
  ushort uVar2;
  int iVar3;
  
  uVar2 = (*((ushort *)camry_host_ptr((uint32_t)(param_1 + 10))));
  iVar3 = (*((int *)camry_host_ptr((uint32_t)(param_1 + 0xc))));
  cVar1 = (*((char *)camry_host_ptr((uint32_t)(param_1 + 8))));
  if (0xfffe < uVar2) {
    uVar2 = 0xffff;
  }
  if (iVar3 == -1) {
    iVar3 = -1;
  }
  store_low_u16_big_endian_bytes_6a574(uVar2, ((undefined1 *)camry_host_ptr((uint32_t)(param_2))));
  store_u32_big_endian_bytes_6a55c(iVar3, ((undefined1 *)camry_host_ptr((uint32_t)(param_2 + 2))));
  (*((bool *)camry_host_ptr((uint32_t)(param_2 + 6)))) = cVar1 != '\0';
  return;
}

void serialize_capture_slot_bounded_word_with_count_prefix_56280(int param_1,byte *param_2)

{
  uint32_t puVar1;
  byte bVar2;
  
  puVar1 = (*((volatile uint32_t *)camry_host_ptr((uint32_t)(param_1 + 0x10))));
  bVar2 = (*((byte *)camry_host_ptr((uint32_t)(param_1 + 9))));
  if (0xf423fu < (puVar1)) {
    puVar1 = (0x0);
  }
  if (1 < bVar2) {
    bVar2 = 2;
  }
  store_u32_big_endian_bytes_6a55c((puVar1),  param_2);
  *param_2 = bVar2;
  return;
}

void serialize_capture_slot_field14_be16_562da(int param_1, undefined4 param_2)

{
  store_low_u16_big_endian_bytes_6a574((*((undefined2 *)camry_host_ptr((uint32_t)(param_1 + 0x14)))), ((undefined1 *)camry_host_ptr((uint32_t)(param_2))));
  return;
}

void serialize_capture_slot_field16_be16_562ea(int param_1, undefined4 param_2)

{
  store_low_u16_big_endian_bytes_6a574((*((undefined2 *)camry_host_ptr((uint32_t)(param_1 + 0x16)))), ((undefined1 *)camry_host_ptr((uint32_t)(param_2))));
  return;
}

uint promote_capture_bank_dirty_bit3_to_bit1_562fa(void)

{
  byte bVar1;
  uint saved_mask;
  uint uVar2;
  
  saved_mask = priority_mask_enter(0xff00);
  uVar2 = 0;
  do {
    bVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe89d2u + (uint32_t)(uVar2) * 1u))));
    if ((bVar1 >> 3 & 1) != 0) {
      bVar1 = bVar1 | 2;
    }
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe89d2u + (uint32_t)(uVar2) * 1u)))) = bVar1;
    uVar2 = uVar2 + 1;
  } while (uVar2 < 4);
  priority_mask_restore(saved_mask);
  return saved_mask;
}

void return_only_stub_56330(void)

{
  return;
}

void return_only_stub_56332(void)

{
  return;
}

void return_only_stub_56334(void)

{
  return;
}

void populate_extended_capture_record_mode10_56336(int param_1)

{
  uint8_t stack_record_28[40];
  undefined1 uVar1;
  uint32_t puVar2;
  
  puVar2 = 0xfebeb800u;
  thunk_select_snapshot_packer_by_kind_ten_be1f8(camry_host_addr(stack_record_28), 10);
  (*((undefined2 *)camry_host_ptr((uint32_t)(param_1 + 2)))) = 0;
  (*((undefined1 *)camry_host_ptr((uint32_t)(param_1 + 4)))) = stack_record_28[3];
  (*((undefined1 *)camry_host_ptr((uint32_t)(param_1 + 5)))) = stack_record_28[4];
  (*((undefined2 *)camry_host_ptr((uint32_t)(param_1 + 6)))) = (*((uint16_t *)(stack_record_28 + 8)));
  (*((undefined4 *)camry_host_ptr((uint32_t)(param_1 + 8)))) = (*((uint32_t *)(stack_record_28 + 16)));
  (*((undefined4 *)camry_host_ptr((uint32_t)(param_1 + 0xc)))) = (*((uint32_t *)(stack_record_28 + 20)));
  (*((undefined2 *)camry_host_ptr((uint32_t)(param_1 + 0x10)))) = (*((uint16_t *)(stack_record_28 + 10)));
  (*((undefined2 *)camry_host_ptr((uint32_t)(param_1 + 0x12)))) = (*((uint16_t *)(stack_record_28 + 12)));
  (*((undefined2 *)camry_host_ptr((uint32_t)(param_1 + 0x14)))) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar2 + -0x3a4e))));
  (*((undefined1 *)camry_host_ptr((uint32_t)(param_1 + 0x16)))) = stack_record_28[0];
  (*((undefined *)camry_host_ptr((uint32_t)(param_1 + 0x17)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x3814)))));
  (*((undefined2 *)camry_host_ptr((uint32_t)(param_1 + 0x18)))) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar2 + -0x5428))));
  (*((undefined2 *)camry_host_ptr((uint32_t)(param_1 + 0x1a)))) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar2 + -0x542c))));
  (*((undefined2 *)camry_host_ptr((uint32_t)(param_1 + 0x1c)))) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar2 + -0x3aba))));
  (*((undefined2 *)camry_host_ptr((uint32_t)(param_1 + 0x1e)))) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar2 + -0x3a50))));
  (*((undefined2 *)camry_host_ptr((uint32_t)(param_1 + 0x20)))) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar2 + -0x3a5a))));
  (*((undefined2 *)camry_host_ptr((uint32_t)(param_1 + 0x22)))) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar2 + -0x3a26))));
  (*((undefined1 *)camry_host_ptr((uint32_t)(param_1 + 0x24)))) = stack_record_28[1];
  (*((undefined1 *)camry_host_ptr((uint32_t)(param_1 + 0x25)))) = stack_record_28[2];
  (*((undefined2 *)camry_host_ptr((uint32_t)(param_1 + 0x26)))) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar2 + -0x5552))));
  (*((undefined2 *)camry_host_ptr((uint32_t)(param_1 + 0x28)))) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar2 + -0x5550))));
  (*((undefined2 *)camry_host_ptr((uint32_t)(param_1 + 0x2a)))) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar2 + -0x554e))));
  (*((undefined2 *)camry_host_ptr((uint32_t)(param_1 + 0x2c)))) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar2 + -0x554c))));
  (*((undefined2 *)camry_host_ptr((uint32_t)(param_1 + 0x2e)))) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar2 + -0x53f2))));
  (*((undefined2 *)camry_host_ptr((uint32_t)(param_1 + 0x30)))) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar2 + -0x53e0))));
  (*((undefined2 *)camry_host_ptr((uint32_t)(param_1 + 0x32)))) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar2 + -0x53f4))));
  (*((undefined2 *)camry_host_ptr((uint32_t)(param_1 + 0x34)))) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar2 + -0x53de))));
  (*((undefined2 *)camry_host_ptr((uint32_t)(param_1 + 0x36)))) = (*((uint16_t *)(stack_record_28 + 14)));
  (*((undefined4 *)camry_host_ptr((uint32_t)(param_1 + 0x38)))) = (*((undefined4 *)camry_host_ptr((uint32_t)(puVar2 + -0x544c))));
  (*((undefined2 *)camry_host_ptr((uint32_t)(param_1 + 0x3c)))) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar2 + -0x3766))));
  (*((undefined2 *)camry_host_ptr((uint32_t)(param_1 + 0x3e)))) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar2 + -0x37b6))));
  (*((undefined2 *)camry_host_ptr((uint32_t)(param_1 + 0x40)))) = (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffb77au + (uint32_t)((int)puVar2))))));
  (*((undefined2 *)camry_host_ptr((uint32_t)(param_1 + 0x42)))) = (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffb77cu + (uint32_t)((int)puVar2))))));
  (*((undefined *)camry_host_ptr((uint32_t)(param_1 + 0x44)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffb76cu + (uint32_t)((int)puVar2) * 1u))));
  uVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffb76du + (uint32_t)((int)puVar2) * 1u))));
  (*((undefined1 *)camry_host_ptr((uint32_t)(param_1 + 0x50)))) = 0;
  (*((undefined2 *)camry_host_ptr((uint32_t)(param_1 + 0x4e)))) = 0;
  (*((undefined1 *)camry_host_ptr((uint32_t)(param_1 + 0x51)))) = 0;
  (*((undefined1 *)camry_host_ptr((uint32_t)(param_1 + 0x45)))) = uVar1;
  (*((undefined2 *)camry_host_ptr((uint32_t)(param_1 + 0x52)))) = 0;
  (*((undefined1 *)camry_host_ptr((uint32_t)(param_1 + 0x56)))) = 0;
  (*((undefined2 *)camry_host_ptr((uint32_t)(param_1 + 0x54)))) = 0;
  (*((undefined1 *)camry_host_ptr((uint32_t)(param_1 + 0x48)))) = stack_record_28[24];
  (*((undefined1 *)camry_host_ptr((uint32_t)(param_1 + 0x57)))) = 0;
  (*((undefined2 *)camry_host_ptr((uint32_t)(param_1 + 0x58)))) = 0;
  (*((undefined1 *)camry_host_ptr((uint32_t)(param_1 + 0x5c)))) = 0;
  (*((undefined1 *)camry_host_ptr((uint32_t)(param_1 + 0x49)))) = stack_record_28[25];
  (*((undefined2 *)camry_host_ptr((uint32_t)(param_1 + 0x5a)))) = 0;
  (*((undefined1 *)camry_host_ptr((uint32_t)(param_1 + 0x5d)))) = 0;
  (*((undefined2 *)camry_host_ptr((uint32_t)(param_1 + 0x5e)))) = 0;
  (*((undefined1 *)camry_host_ptr((uint32_t)(param_1 + 0x4a)))) = stack_record_28[26];
  (*((undefined1 *)camry_host_ptr((uint32_t)(param_1 + 0x4b)))) = stack_record_28[27];
  (*((undefined1 *)camry_host_ptr((uint32_t)(param_1 + 0x4c)))) = stack_record_28[28];
  (*((undefined1 *)camry_host_ptr((uint32_t)(param_1 + 0x4d)))) = stack_record_28[29];
  return;
}

void populate_compact_capture_record_mode10_56458(int param_1)

{
  uint8_t stack_record_28[40];
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  thunk_select_snapshot_packer_by_kind_ten_be1f8(camry_host_addr(((uint8_t *)(stack_record_28))), 10);
  (*((undefined2 *)camry_host_ptr((uint32_t)(param_1 + 4)))) = 0;
  (*((undefined2 *)camry_host_ptr((uint32_t)(param_1 + 6)))) = 0;
  (*((undefined1 *)camry_host_ptr((uint32_t)(param_1 + 8)))) = stack_record_28[3];
  (*((undefined1 *)camry_host_ptr((uint32_t)(param_1 + 9)))) = stack_record_28[4];
  (*((undefined2 *)camry_host_ptr((uint32_t)(param_1 + 10)))) = (*((uint16_t *)(stack_record_28 + 8)));
  (*((undefined4 *)camry_host_ptr((uint32_t)(param_1 + 0xc)))) = (*((uint32_t *)(stack_record_28 + 16)));
  (*((undefined4 *)camry_host_ptr((uint32_t)(param_1 + 0x10)))) = (*((uint32_t *)(stack_record_28 + 20)));
  (*((undefined2 *)camry_host_ptr((uint32_t)(param_1 + 0x14)))) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x2d08))));
  (*((undefined2 *)camry_host_ptr((uint32_t)(param_1 + 0x16)))) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x2d0c))));
  (*((undefined1 *)camry_host_ptr((uint32_t)(param_1 + 0x18)))) = 0x35;
  (*((undefined1 *)camry_host_ptr((uint32_t)(param_1 + 0x19)))) = 2;
  (*((undefined1 *)camry_host_ptr((uint32_t)(param_1 + 0x1a)))) = stack_record_28[24];
  (*((undefined1 *)camry_host_ptr((uint32_t)(param_1 + 0x1b)))) = stack_record_28[25];
  (*((undefined1 *)camry_host_ptr((uint32_t)(param_1 + 0x1c)))) = stack_record_28[26];
  (*((undefined1 *)camry_host_ptr((uint32_t)(param_1 + 0x1d)))) = stack_record_28[27];
  (*((undefined1 *)camry_host_ptr((uint32_t)(param_1 + 0x1e)))) = stack_record_28[28];
  (*((undefined1 *)camry_host_ptr((uint32_t)(param_1 + 0x1f)))) = stack_record_28[29];
  return;
}

void return_only_stub_564c8(void)

{
  return;
}

void return_only_stub_564ca(void)

{
  return;
}

void return_only_stub_564cc(void)

{
  return;
}

void populate_extended_capture_record_mode50_564ce(int param_1)

{
  uint8_t stack_record_28[40];
  undefined1 uVar1;
  uint32_t puVar2;
  
  puVar2 = 0xfebeb800u;
  thunk_select_snapshot_packer_by_kind_ten_be1f8(camry_host_addr(stack_record_28), 0x32);
  (*((undefined2 *)camry_host_ptr((uint32_t)(param_1 + 2)))) = 0;
  (*((undefined1 *)camry_host_ptr((uint32_t)(param_1 + 4)))) = stack_record_28[3];
  (*((undefined1 *)camry_host_ptr((uint32_t)(param_1 + 5)))) = stack_record_28[4];
  (*((undefined2 *)camry_host_ptr((uint32_t)(param_1 + 6)))) = (*((uint16_t *)(stack_record_28 + 8)));
  (*((undefined4 *)camry_host_ptr((uint32_t)(param_1 + 8)))) = (*((uint32_t *)(stack_record_28 + 16)));
  (*((undefined4 *)camry_host_ptr((uint32_t)(param_1 + 0xc)))) = (*((uint32_t *)(stack_record_28 + 20)));
  (*((undefined2 *)camry_host_ptr((uint32_t)(param_1 + 0x10)))) = (*((uint16_t *)(stack_record_28 + 10)));
  (*((undefined2 *)camry_host_ptr((uint32_t)(param_1 + 0x12)))) = (*((uint16_t *)(stack_record_28 + 12)));
  (*((undefined2 *)camry_host_ptr((uint32_t)(param_1 + 0x14)))) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar2 + -0x5146))));
  (*((undefined1 *)camry_host_ptr((uint32_t)(param_1 + 0x16)))) = stack_record_28[0];
  (*((undefined *)camry_host_ptr((uint32_t)(param_1 + 0x17)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x3814)))));
  (*((undefined2 *)camry_host_ptr((uint32_t)(param_1 + 0x18)))) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar2 + -0x5158))));
  (*((undefined2 *)camry_host_ptr((uint32_t)(param_1 + 0x1a)))) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar2 + -0x515c))));
  (*((undefined2 *)camry_host_ptr((uint32_t)(param_1 + 0x1c)))) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar2 + -0x3aba))));
  (*((undefined2 *)camry_host_ptr((uint32_t)(param_1 + 0x1e)))) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar2 + -0x5148))));
  (*((undefined2 *)camry_host_ptr((uint32_t)(param_1 + 0x20)))) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar2 + -0x5152))));
  (*((undefined2 *)camry_host_ptr((uint32_t)(param_1 + 0x22)))) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar2 + -0x3a26))));
  (*((undefined1 *)camry_host_ptr((uint32_t)(param_1 + 0x24)))) = stack_record_28[1];
  (*((undefined1 *)camry_host_ptr((uint32_t)(param_1 + 0x25)))) = stack_record_28[2];
  (*((undefined2 *)camry_host_ptr((uint32_t)(param_1 + 0x26)))) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar2 + -0x530e))));
  (*((undefined2 *)camry_host_ptr((uint32_t)(param_1 + 0x28)))) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar2 + -0x530c))));
  (*((undefined2 *)camry_host_ptr((uint32_t)(param_1 + 0x2a)))) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar2 + -0x530a))));
  (*((undefined2 *)camry_host_ptr((uint32_t)(param_1 + 0x2c)))) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar2 + -0x5308))));
  (*((undefined2 *)camry_host_ptr((uint32_t)(param_1 + 0x2e)))) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar2 + -0x50f2))));
  (*((undefined2 *)camry_host_ptr((uint32_t)(param_1 + 0x30)))) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar2 + -0x50dc))));
  (*((undefined2 *)camry_host_ptr((uint32_t)(param_1 + 0x32)))) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar2 + -0x50f4))));
  (*((undefined2 *)camry_host_ptr((uint32_t)(param_1 + 0x34)))) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar2 + -0x50da))));
  (*((undefined2 *)camry_host_ptr((uint32_t)(param_1 + 0x36)))) = (*((uint16_t *)(stack_record_28 + 14)));
  (*((undefined4 *)camry_host_ptr((uint32_t)(param_1 + 0x38)))) = (*((undefined4 *)camry_host_ptr((uint32_t)(puVar2 + -0x517c))));
  (*((undefined2 *)camry_host_ptr((uint32_t)(param_1 + 0x3c)))) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar2 + -0x3766))));
  (*((undefined2 *)camry_host_ptr((uint32_t)(param_1 + 0x3e)))) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar2 + -0x37b6))));
  (*((undefined2 *)camry_host_ptr((uint32_t)(param_1 + 0x40)))) = (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffb77au + (uint32_t)((int)puVar2))))));
  (*((undefined2 *)camry_host_ptr((uint32_t)(param_1 + 0x42)))) = (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffb77cu + (uint32_t)((int)puVar2))))));
  (*((undefined *)camry_host_ptr((uint32_t)(param_1 + 0x44)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffb76cu + (uint32_t)((int)puVar2) * 1u))));
  uVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffb76du + (uint32_t)((int)puVar2) * 1u))));
  (*((undefined1 *)camry_host_ptr((uint32_t)(param_1 + 0x50)))) = 0;
  (*((undefined2 *)camry_host_ptr((uint32_t)(param_1 + 0x4e)))) = 0;
  (*((undefined1 *)camry_host_ptr((uint32_t)(param_1 + 0x51)))) = 0;
  (*((undefined1 *)camry_host_ptr((uint32_t)(param_1 + 0x45)))) = uVar1;
  (*((undefined2 *)camry_host_ptr((uint32_t)(param_1 + 0x52)))) = 0;
  (*((undefined1 *)camry_host_ptr((uint32_t)(param_1 + 0x56)))) = 0;
  (*((undefined2 *)camry_host_ptr((uint32_t)(param_1 + 0x54)))) = 0;
  (*((undefined1 *)camry_host_ptr((uint32_t)(param_1 + 0x48)))) = stack_record_28[24];
  (*((undefined1 *)camry_host_ptr((uint32_t)(param_1 + 0x57)))) = 0;
  (*((undefined2 *)camry_host_ptr((uint32_t)(param_1 + 0x58)))) = 0;
  (*((undefined1 *)camry_host_ptr((uint32_t)(param_1 + 0x5c)))) = 0;
  (*((undefined1 *)camry_host_ptr((uint32_t)(param_1 + 0x49)))) = stack_record_28[25];
  (*((undefined2 *)camry_host_ptr((uint32_t)(param_1 + 0x5a)))) = 0;
  (*((undefined1 *)camry_host_ptr((uint32_t)(param_1 + 0x5d)))) = 0;
  (*((undefined2 *)camry_host_ptr((uint32_t)(param_1 + 0x5e)))) = 0;
  (*((undefined1 *)camry_host_ptr((uint32_t)(param_1 + 0x4a)))) = stack_record_28[26];
  (*((undefined1 *)camry_host_ptr((uint32_t)(param_1 + 0x4b)))) = stack_record_28[27];
  (*((undefined1 *)camry_host_ptr((uint32_t)(param_1 + 0x4c)))) = stack_record_28[28];
  (*((undefined1 *)camry_host_ptr((uint32_t)(param_1 + 0x4d)))) = stack_record_28[29];
  return;
}

void populate_compact_capture_record_mode50_565f2(int param_1)

{
  uint8_t stack_record_28[40];
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  thunk_select_snapshot_packer_by_kind_ten_be1f8(camry_host_addr(((uint8_t *)(stack_record_28))), 0x32);
  (*((undefined2 *)camry_host_ptr((uint32_t)(param_1 + 4)))) = 0;
  (*((undefined2 *)camry_host_ptr((uint32_t)(param_1 + 6)))) = 0;
  (*((undefined1 *)camry_host_ptr((uint32_t)(param_1 + 8)))) = stack_record_28[3];
  (*((undefined1 *)camry_host_ptr((uint32_t)(param_1 + 9)))) = stack_record_28[4];
  (*((undefined2 *)camry_host_ptr((uint32_t)(param_1 + 10)))) = (*((uint16_t *)(stack_record_28 + 8)));
  (*((undefined4 *)camry_host_ptr((uint32_t)(param_1 + 0xc)))) = (*((uint32_t *)(stack_record_28 + 16)));
  (*((undefined4 *)camry_host_ptr((uint32_t)(param_1 + 0x10)))) = (*((uint32_t *)(stack_record_28 + 20)));
  (*((undefined2 *)camry_host_ptr((uint32_t)(param_1 + 0x14)))) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x2d08))));
  (*((undefined2 *)camry_host_ptr((uint32_t)(param_1 + 0x16)))) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x2d0c))));
  (*((undefined1 *)camry_host_ptr((uint32_t)(param_1 + 0x18)))) = 0x35;
  (*((undefined1 *)camry_host_ptr((uint32_t)(param_1 + 0x19)))) = 2;
  (*((undefined1 *)camry_host_ptr((uint32_t)(param_1 + 0x1a)))) = stack_record_28[24];
  (*((undefined1 *)camry_host_ptr((uint32_t)(param_1 + 0x1b)))) = stack_record_28[25];
  (*((undefined1 *)camry_host_ptr((uint32_t)(param_1 + 0x1c)))) = stack_record_28[26];
  (*((undefined1 *)camry_host_ptr((uint32_t)(param_1 + 0x1d)))) = stack_record_28[27];
  (*((undefined1 *)camry_host_ptr((uint32_t)(param_1 + 0x1e)))) = stack_record_28[28];
  (*((undefined1 *)camry_host_ptr((uint32_t)(param_1 + 0x1f)))) = stack_record_28[29];
  return;
}

F33CaptureFieldDescriptor * get_capture_field_descriptors_and_count_56664(undefined2 *param_1)

{
  *param_1 = 0x4b;
  return capture_field_descriptor;
}

undefined * get_ring_capture_field_descriptors_and_count_56674(undefined2 *param_1)

{
  *param_1 = 6;
  return ((undefined *)camry_host_ptr(0x2aa6cu));
}

void return_only_stub_56682(void)

{
  return;
}

void reset_current_control_even_call_flag_56684(void)

{
  DAT_febe8a14 = 0;
  return;
}

void update_current_control_even_call_flag_5668a(void)

{
  uint32_t puVar1;
  uint uVar2;
  
  puVar1 = 0xfebeb800u;
  uVar2 = get_current_control_slice_call_count_58c8a();
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x2dec))))) = (uVar2 & 1) == 0;
  return;
}

void return_only_stub_566a0(void)

{
  return;
}

void reset_monitor_five_call_gate_8a18_566a2(void)

{
  DAT_febe8a18 = 0;
  DAT_febe8a19 = 0;
  return;
}

char update_monitor_five_call_gate_8a18_566ac(void)

{
  undefined1 uVar1;
  uint32_t puVar2;
  char cVar3;
  
  puVar2 = 0xfebeb800u;
  cVar3 = get_ch2_monitor_slice_call_count_58c90();
  if ((byte)(cVar3 - (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x2de7)))))) < 5) {
    uVar1 = 0;
  }
  else {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x2de7))))) = cVar3;
    uVar1 = 0x5a;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x2de8))))) = uVar1;
  return cVar3;
}

void return_only_stub_566d4(void)

{
  return;
}

void reset_inverted_state_bit_gate_8a1c_566d6(void)

{
  DAT_febe8a1c = 0;
  return;
}

void update_inverted_state_bit_gate_8a1c_566dc(void)

{
  DAT_febe8a1c = 0;
  if ((DAT_febe5f28 & 1) == 0) {
    DAT_febe8a1c = 0x5a;
  }
  return;
}

void return_only_stub_566ee(void)

{
  return;
}

void reset_current_control_four_call_gate_566f0(void)

{
  DAT_febe8a20 = 0;
  DAT_febe8a21 = 0;
  return;
}

char update_current_control_four_call_gate_566fa(void)

{
  bool bVar1;
  uint32_t puVar2;
  char cVar3;
  
  puVar2 = 0xfebeb800u;
  cVar3 = get_current_control_slice_call_count_58c8a();
  bVar1 = 3 < (byte)(cVar3 - (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x2ddf))))));
  if (bVar1) {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x2ddf))))) = cVar3;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x2de0))))) = bVar1;
  return cVar3;
}

void return_only_stub_56720(void)

{
  return;
}

void reset_monitor_five_call_gate_8a24_56722(void)

{
  DAT_febe8a24 = 0;
  DAT_febe8a25 = 0;
  return;
}

char update_monitor_five_call_gate_8a24_5672c(void)

{
  undefined1 uVar1;
  uint32_t puVar2;
  char cVar3;
  
  puVar2 = 0xfebeb800u;
  cVar3 = get_ch2_monitor_slice_call_count_58c90();
  if ((byte)(cVar3 - (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x2ddb)))))) < 5) {
    uVar1 = 0;
  }
  else {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x2ddb))))) = cVar3;
    uVar1 = 0x5a;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x2ddc))))) = uVar1;
  return cVar3;
}

void return_only_stub_56754(void)

{
  return;
}

void return_only_stub_56756(void)

{
  return;
}

void report_events_94_and_93_from_status_bits_56758(void)

{
  uint uVar1;
  
  uVar1 = consume_nvm_family0_classification_flags_67874();
  if ((uVar1 & 1) != 0) {
    report_diagnostic_event_failure(0x94,0x32);
  }
  if ((uVar1 >> 1 & 1) != 0) {
    report_diagnostic_event_failure(0x93,0x32);
  }
  return;
}

void return_only_stub_56786(void)

{
  return;
}

void return_only_stub_56788(void)

{
  return;
}

uint32_t dispatch_service12_when_66f10_returns_zero_5678a(void)

{
  uint32_t camry_r10_result;
  int iVar1;
  
  iVar1 = (camry_r10_result = get_nvm_acquisition_active_5a_66f10());
  if (iVar1 == 0) {
    (camry_r10_result = thunk_set_indexed_request_and_clear_complement_b15ac(0x12));
  }
  return camry_r10_result;
}

void return_only_stub_567a2(void)

{
  return;
}

void return_only_stub_567a4(void)

{
  return;
}

uint32_t dispatch_service28_when_application_nvm_ready_567a6(void)

{
  uint32_t camry_r10_result;
  uint uVar1;
  
  uVar1 = (camry_r10_result = application_nvm_is_ready());
  if (uVar1 == 1) {
    (camry_r10_result = thunk_set_indexed_request_and_clear_complement_b15ac(0x28));
  }
  return camry_r10_result;
}

F33MonitorCurrentRecord * get_monitor_current_rom_record_567be(void)

{
  return ((undefined *)camry_host_ptr(0xa000u));
}

void return_only_stub_567c6(void)

{
  return;
}

void return_only_stub_567c8(void)

{
  return;
}

void latch_event20_on_a55aa55a_status_567ca(void)

{
  uint32_t puVar1;
  int iVar2;
  char cVar3;
  
  cVar3 = DAT_febe8a28;
  puVar1 = (0xfebeb800u);
  if ((DAT_febe8a28 == '\0') &&
     (puVar1 = (0xfebeb800u), iVar2 = get_identity_word_febf0668_62e12(), iVar2 == -0x5aa55aa6)) {
    gate_indexed_event_payload_during_diagnostic_clears_51cf6(0x20,0x32);
    cVar3 = 'Z';
  }
  (*((volatile undefined *)camry_host_ptr((uint32_t)(0xfebeb800u + (uint32_t)(-0x2dd8) * 1u)))) = cVar3;
  return;
}

void return_only_stub_567fc(void)

{
  return;
}

void clear_five_request_words_8a2c_567fe(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  
  iVar3 = 0;
  do {
    iVar2 = iVar3 + 1;
    *(undefined4 *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe8a2cu + (uint32_t)(iVar3 * 4) * 1u)))) = 0;
    iVar1 = iVar3 + -4;
    iVar3 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  return;
}

void decode_low_request_bits2_to5_to_status_56814(uint param_1)

{
  undefined4 uVar1;
  
  if ((param_1 >> 2 & 1) == 0) {
    if ((param_1 >> 3 & 1) == 0) {
      if ((param_1 & 0x10) == 0) {
        DAT_febe3866 = 0;
        DAT_febe3873 = 0;
        if ((param_1 >> 5 & 1) == 0) {
          DAT_febe3872 = 0xff;
        }
        else {
          DAT_febe3872 = 0;
        }
        uVar1 = 0;
        goto LAB_00056854;
      }
      DAT_febe3873 = 0xff;
      goto LAB_0005683e;
    }
    DAT_febe3873 = 0xff;
    DAT_febe3872 = 0;
  }
  else {
    DAT_febe3873 = 0;
LAB_0005683e:
    DAT_febe3872 = 0xff;
  }
  DAT_febe3866 = 0xff;
  uVar1 = 2;
LAB_00056854:
  set_request_word_8a88_bounded4_56b78(0,uVar1);
  return;
}

void decode_high_request_bits18_to21_to_status_5685e(uint param_1)

{
  undefined4 uVar1;
  
  if ((param_1 >> 0x12 & 1) == 0) {
    if ((param_1 >> 0x13 & 1) == 0) {
      if ((param_1 & 0x100000) == 0) {
        DAT_febe3865 = 0;
        DAT_febe3871 = 0;
        if ((param_1 >> 0x15 & 1) == 0) {
          DAT_febe3870 = 0xff;
        }
        else {
          DAT_febe3870 = 0;
        }
        uVar1 = 0;
        goto LAB_000568a2;
      }
      DAT_febe3871 = 0xff;
      goto LAB_0005688a;
    }
    DAT_febe3871 = 0xff;
    DAT_febe3870 = 0;
  }
  else {
    DAT_febe3871 = 0;
LAB_0005688a:
    DAT_febe3870 = 0xff;
  }
  DAT_febe3865 = 0xff;
  uVar1 = 0x20000;
LAB_000568a2:
  set_request_word_8a88_bounded4_56b78(1,uVar1);
  return;
}

void aggregate_five_request_words_8a2c_568ac(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  uint32_t puVar4;
  uint uVar5;
  
  puVar4 = 0xfebeb800u;
  uVar5 = 0;
  iVar3 = 0;
  do {
    iVar2 = iVar3 + 1;
    uVar5 = uVar5 | *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe8a2cu + (uint32_t)(iVar3 * 4) * 1u))));
    iVar1 = iVar3 + -4;
    iVar3 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  decode_low_request_bits2_to5_to_status_56814(uVar5);
  decode_high_request_bits18_to21_to_status_5685e(uVar5);
  (*((uint *)camry_host_ptr((uint32_t)(puVar4 + -0x2dc0)))) = uVar5;
  return;
}

void set_request_word_8a2c_bounded5_568dc(uint param_1,undefined4 param_2)

{
  if ((param_1 & 0xff) < 5) {
    *(undefined4 *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe8a2cu + (uint32_t)((param_1 & 0xff) * 4) * 1u)))) = param_2;
  }
  return;
}

void return_only_stub_568f0(void)

{
  return;
}

void clear_two_request_words_8a48_568f2(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  
  iVar3 = 0;
  do {
    iVar2 = iVar3 + 1;
    *(undefined4 *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe8a48u + (uint32_t)(iVar3 * 4) * 1u)))) = 0;
    iVar1 = iVar3 + -1;
    iVar3 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  return;
}

void aggregate_two_requests_to_status_bits0_and1_56908(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  
  DAT_febe8a44 = 0;
  iVar3 = 0;
  do {
    iVar2 = iVar3 + 1;
    DAT_febe8a44 = DAT_febe8a44 | *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe8a48u + (uint32_t)(iVar3 * 4) * 1u))));
    iVar1 = iVar3 + -1;
    iVar3 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  if ((DAT_febe8a44 & 1) == 0) {
    DAT_febe3877 = 0;
  }
  else {
    DAT_febe3877 = 0xff;
  }
  if ((DAT_febe8a44 >> 1 & 1) == 0) {
    DAT_febe3876 = 0;
  }
  else {
    DAT_febe3876 = 0xff;
  }
  return;
}

void set_request_word_8a48_bounded2_5693e(uint param_1,undefined4 param_2)

{
  if ((param_1 & 0xff) < 2) {
    *(undefined4 *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe8a48u + (uint32_t)((param_1 & 0xff) * 4) * 1u)))) = param_2;
  }
  return;
}

void return_only_stub_56952(void)

{
  return;
}

void clear_five_request_words_8a50_56954(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  
  iVar3 = 0;
  do {
    iVar2 = iVar3 + 1;
    *(undefined4 *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe8a50u + (uint32_t)(iVar3 * 4) * 1u)))) = 0;
    iVar1 = iVar3 + -4;
    iVar3 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  return;
}

void publish_request_bits1_and17_at_386f_5696a(uint param_1)

{
  if ((param_1 >> 1 & 1) == 0) {
    DAT_febe386f = 0;
  }
  else {
    DAT_febe386f = 0xff;
  }
  if ((param_1 >> 0x11 & 1) == 0) {
    DAT_febe386e = 0;
  }
  else {
    DAT_febe386e = 0xff;
  }
  return;
}

void aggregate_five_request_words_8a50_56982(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  uint32_t puVar4;
  uint uVar5;
  
  puVar4 = 0xfebeb800u;
  uVar5 = 0;
  iVar3 = 0;
  do {
    iVar2 = iVar3 + 1;
    uVar5 = uVar5 | *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe8a50u + (uint32_t)(iVar3 * 4) * 1u))));
    iVar1 = iVar3 + -4;
    iVar3 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  publish_request_bits1_and17_at_386f_5696a(uVar5);
  (*((uint *)camry_host_ptr((uint32_t)(puVar4 + -0x2d9c)))) = uVar5;
  return;
}

void set_request_word_8a50_bounded5_569ac(uint param_1,undefined4 param_2)

{
  if ((param_1 & 0xff) < 5) {
    *(undefined4 *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe8a50u + (uint32_t)((param_1 & 0xff) * 4) * 1u)))) = param_2;
  }
  return;
}

void return_only_stub_569c0(void)

{
  return;
}

void initialize_channel_owner_request_masks_569c2(void)

{
  channel_request_state.owner_requests[0] = 2;
  channel_request_state.owner_requests[1] = 0x20000;
  channel_request_state.owner_requests[2] = (uint)0x20002u;
  channel_request_state.owner_requests[3] = (uint)0x20002u;
  channel_request_state.owner_requests[4] = (uint)0x20002u;
  return;
}

void apply_channel_request_mask(uint request_mask)

{
  if (((uint32_t)((uint32_t)(request_mask & 0x20002)))==((uint32_t)(0x20002u))) {
    write_channel0_requested_level_66aa2();
    write_channel1_requested_level_66ada();
  }
  else if (request_mask == 0) {
    write_channel0_reference_level_66a94();
    write_channel1_reference_level_66acc();
  }
  if ((request_mask >> 1 & 1) == 0) {
    write_channel0_reference_level_66a94();
  }
  else {
    write_channel0_requested_level_66aa2();
  }
  if ((request_mask >> 0x11 & 1) == 0) {
    write_channel1_reference_level_66acc();
  }
  else {
    write_channel1_requested_level_66ada();
  }
  return;
}

uint read_channel_mismatch_mask(void)

{
  uint uVar1;
  uint uVar2;
  
  uVar1 = channel0_matches_reference();
  if (uVar1 == 0) {
    uVar1 = 2;
  }
  else {
    uVar1 = 0;
  }
  uVar2 = channel1_matches_reference();
  if (uVar2 == 0) {
    uVar1 = uVar1 | 0x20000;
  }
  return uVar1;
}

void debounce_channel0_observed_request_mismatch_56a48(void)

{
  if ((channel_request_state.observed_mismatch & 2) == 0) {
    channel_request_state.channel0_mismatch_calls = '\0';
    if (channel_request_state.channel0_match_calls < DAT_000318f8) {
      channel_request_state.channel0_match_calls =
           channel_request_state.channel0_match_calls + '\x01';
      channel_request_state.channel0_state = '\x03';
    }
    else {
      channel_request_state.channel0_state = '\x02';
    }
  }
  else {
    channel_request_state.channel0_match_calls = '\0';
    if (channel_request_state.channel0_mismatch_calls < DAT_000318f9) {
      channel_request_state.channel0_mismatch_calls =
           channel_request_state.channel0_mismatch_calls + '\x01';
      channel_request_state.channel0_state = '\x01';
    }
    else {
      channel_request_state.channel0_state = '\0';
    }
  }
  return;
}

void debounce_channel1_observed_request_mismatch_56a8c(void)

{
  if ((channel_request_state.observed_mismatch & 0x20000) == 0) {
    channel_request_state.channel1_mismatch_calls = '\0';
    if (channel_request_state.channel1_match_calls < DAT_000318f8) {
      channel_request_state.channel1_match_calls =
           channel_request_state.channel1_match_calls + '\x01';
      channel_request_state.channel1_state = '\x03';
    }
    else {
      channel_request_state.channel1_state = '\x02';
    }
  }
  else {
    channel_request_state.channel1_match_calls = '\0';
    if (channel_request_state.channel1_mismatch_calls < DAT_000318f9) {
      channel_request_state.channel1_mismatch_calls =
           channel_request_state.channel1_mismatch_calls + '\x01';
      channel_request_state.channel1_state = '\x01';
    }
    else {
      channel_request_state.channel1_state = '\0';
    }
  }
  return;
}

void update_channel_requests(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  uint32_t puVar4;
  uint uVar5;
  
  puVar4 = 0xfebeb800u;
  uVar5 = 0;
  iVar3 = 0;
  do {
    iVar2 = iVar3 + 1;
    uVar5 = uVar5 | channel_request_state.owner_requests[iVar3];
    iVar1 = iVar3 + -4;
    iVar3 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  apply_channel_request_mask(uVar5);
  uVar5 = read_channel_mismatch_mask();
  (*((uint *)camry_host_ptr((uint32_t)(puVar4 + -0x2d7c)))) = uVar5;
  debounce_channel0_observed_request_mismatch_56a48();
  debounce_channel1_observed_request_mismatch_56a8c();
  return;
}

void return_only_stub_56b1a(void)

{
  return;
}

void clear_four_request_words_8a88_56b1c(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  
  iVar3 = 0;
  do {
    iVar2 = iVar3 + 1;
    *(undefined4 *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe8a88u + (uint32_t)(iVar3 * 4) * 1u)))) = 0;
    iVar1 = iVar3 + -3;
    iVar3 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  return;
}

void aggregate_requests_with_external_channel_status_56b32(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  
  DAT_febe8a98 = 0;
  iVar3 = 0;
  do {
    iVar2 = iVar3 + 1;
    DAT_febe8a98 = DAT_febe8a98 | *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe8a88u + (uint32_t)(iVar3 * 4) * 1u))));
    iVar1 = iVar3 + -3;
    iVar3 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  if (((DAT_febe8a98 >> 1 & 1) != 0) ||
     (DAT_febe3864 = (byte)DAT_febe71ec & 1, (DAT_febe71ec & 1) != 0)) {
    DAT_febe3864 = 0xff;
  }
  if (((DAT_febe8a98 >> 0x11 & 1) != 0) ||
     (DAT_febe3863 = (byte)DAT_febe71ec & 2, (DAT_febe71ec & 2) != 0)) {
    DAT_febe3863 = 0xff;
  }
  return;
}

void set_request_word_8a88_bounded4_56b78(uint param_1,undefined4 param_2)

{
  if ((param_1 & 0xff) < 4) {
    *(undefined4 *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe8a88u + (uint32_t)((param_1 & 0xff) * 4) * 1u)))) = param_2;
  }
  return;
}

void return_only_stub_56b8c(void)

{
  return;
}

void initialize_two_priority_masks_8a9c_56b8e(void)

{
  DAT_febe8a9c = 4;
  DAT_febe8aa0 = 0x40000;
  return;
}

void decode_low_priority_bits1_and2_at_3882_56b9e(uint param_1)

{
  if ((param_1 >> 2 & 1) == 0) {
    if ((param_1 >> 1 & 1) == 0) {
      DAT_febe3882 = 0xff;
    }
    else {
      DAT_febe3882 = 0;
    }
    DAT_febe3883 = 0xff;
  }
  else {
    DAT_febe3882 = 0xff;
    DAT_febe3883 = 0;
  }
  return;
}

void decode_high_priority_bits17_and18_at_3880_56bc0(uint param_1)

{
  if ((param_1 >> 0x12 & 1) == 0) {
    if ((param_1 >> 0x11 & 1) == 0) {
      DAT_febe3880 = 0xff;
    }
    else {
      DAT_febe3880 = 0;
    }
    DAT_febe3881 = 0xff;
  }
  else {
    DAT_febe3880 = 0xff;
    DAT_febe3881 = 0;
  }
  return;
}

void aggregate_priority_masks_with_channel_mismatch_56be2(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  uint32_t puVar4;
  uint uVar5;
  
  puVar4 = 0xfebeb800u;
  if ((channel_request_state.observed_mismatch >> 1 & 1) == 0) {
    uVar5 = 0;
  }
  else {
    uVar5 = 4;
  }
  if ((channel_request_state.observed_mismatch >> 0x11 & 1) != 0) {
    uVar5 = uVar5 | 0x40000;
  }
  iVar3 = 0;
  do {
    iVar2 = iVar3 + 1;
    uVar5 = uVar5 | (*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xfebe8a9cu + (uint32_t)(iVar3) * 4u))));
    iVar1 = iVar3 + -1;
    iVar3 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  decode_low_priority_bits1_and2_at_3882_56b9e(uVar5);
  decode_high_priority_bits17_and18_at_3880_56bc0(uVar5);
  (*((uint *)camry_host_ptr((uint32_t)(puVar4 + -0x2d5c)))) = uVar5;
  return;
}

void set_priority_mask_8a9c_bounded2_56c26(uint param_1,undefined4 param_2)

{
  if ((param_1 & 0xff) < 2) {
    (*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xfebe8a9cu + (uint32_t)(param_1 & 0xff) * 4u)))) = param_2;
  }
  return;
}

void return_only_stub_56c3a(void)

{
  return;
}

void fill_constant_block_56c3c(void)

{
  DAT_febe8aa8 = 0xc;
  DAT_febe8ab0 = 0;
  DAT_febe8aac = 0xc0000;
  DAT_febe8ab4 = 0;
  DAT_febe8ab8 = 0;
  DAT_febe8abc = 0;
  return;
}

void decode_request_enable_pairs_with_rom_override_56c54(uint param_1)

{
  if (DAT_000318fc != 'Z') {
    if (((param_1 >> 2 & 1) == 0) && ((param_1 & 2) != 0)) {
      DAT_febe3875 = 0xff;
    }
    else {
      DAT_febe3875 = 0;
    }
    if (((param_1 >> 0x12 & 1) == 0) && ((param_1 & 0x20000) != 0)) {
      DAT_febe3874 = 0xff;
    }
    else {
      DAT_febe3874 = 0;
    }
    if ((param_1 >> 3 & 1) == 0) {
      DAT_febe386d = 0;
    }
    else {
      DAT_febe386d = 0xff;
    }
    if ((param_1 >> 0x13 & 1) == 0) {
      DAT_febe386c = 0;
    }
    else {
      DAT_febe386c = 0xff;
    }
    return;
  }
  DAT_febe3875 = 0;
  DAT_febe3874 = 0;
  return;
}

void aggregate_six_request_words_8aa8_56cb0(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  uint32_t puVar4;
  uint uVar5;
  
  puVar4 = 0xfebeb800u;
  uVar5 = 0;
  iVar3 = 0;
  do {
    iVar2 = iVar3 + 1;
    uVar5 = uVar5 | (*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xfebe8aa8u + (uint32_t)(iVar3) * 4u))));
    iVar1 = iVar3 + -5;
    iVar3 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  decode_request_enable_pairs_with_rom_override_56c54(uVar5);
  (*((uint *)camry_host_ptr((uint32_t)(puVar4 + -0x2d40)))) = uVar5;
  return;
}

void set_request_word_8aa8_bounded6_56cda(uint param_1,undefined4 param_2)

{
  if ((param_1 & 0xff) < 6) {
    (*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xfebe8aa8u + (uint32_t)(param_1 & 0xff) * 4u)))) = param_2;
  }
  return;
}

void return_only_stub_56cee(void)

{
  return;
}

void reset_timed_reinitialization_counter_56cf0(void)

{
  DAT_febe8ac4 = 0;
  return;
}

void run_timed_reinitialization_and_send_7f1010_56cf6(void)

{
  int iVar1;
  int iVar2;
  ushort uVar3;
  int iVar4;
  uint32_t puVar5;
  uint uVar6;
  short sVar7;
  F33PduInfo local_18;
  uchar local_10 [8];
  
  uVar3 = DAT_febe8ac4;
  puVar5 = 0xfebeb800u;
  uVar6 = application_nvm_is_ready();
  if (uVar6 == 1) {
    disable_ffc0a000_block_and_transfer_to_boot_65f5e();
  }
  if (uVar3 < DAT_00030d5e) {
    sVar7 = uVar3 + 1;
  }
  else {
    call_98898_with_zero_byte_8b120();
    restore_default_dcm_session_when_not_busy_91b50();
    set_matching_dcm_communication_mode_two_917a4(0);
    run_init_chain_8e62a();
    thunk_set_indexed_request_and_clear_complement_b15ac(0xe);
    thunk_reset_application_programming_admission_state_8b134();
    iVar4 = 0;
    do {
      local_10[iVar4] = '\0';
      iVar2 = iVar4 + 1;
      iVar1 = iVar4 + -7;
      iVar4 = iVar2;
    } while (((iVar1 < 0) || (iVar2 < 0)));
    builtin_memcpy(local_10,"\x03\x7f\x10\x10",4);
    local_18.length = 8;
    local_18.data = camry_host_addr(local_10);
    canif_transmit(0x800,&local_18);
    sVar7 = 0;
  }
  (*((short *)camry_host_ptr((uint32_t)(puVar5 + -0x2d3c)))) = sVar7;
  return;
}

void return_only_stub_56d78(void)

{
  return;
}

void initialize_secondary_channel_request_masks_56d7a(void)

{
  DAT_febe8ad0 = 2;
  DAT_febe8ad4 = 0x20000;
  DAT_febe8ad8 = ((uint32_t)(0x20002u));
  DAT_febe8adc = ((uint32_t)(0x20002u));
  DAT_febe8ae0 = ((uint32_t)(0x20002u));
  return;
}

void publish_inverted_request_bits1_and17_at_3885_56d92(uint param_1)

{
  if ((param_1 >> 1 & 1) == 0) {
    DAT_febe3885 = 0xff;
  }
  else {
    DAT_febe3885 = 0;
  }
  if ((param_1 >> 0x11 & 1) == 0) {
    DAT_febe3884 = 0xff;
  }
  else {
    DAT_febe3884 = 0;
  }
  return;
}

void debounce_secondary_channel0_request_bit1_56daa(void)

{
  if ((DAT_febe8ae4 & 2) == 0) {
    DAT_febe8aca = 0;
    if (DAT_febe8ac9 < DAT_00031900) {
      DAT_febe8ac9 = DAT_febe8ac9 + 1;
      DAT_febe8ac8 = 3;
    }
    else {
      DAT_febe8ac8 = 2;
    }
  }
  else {
    DAT_febe8ac9 = 0;
    if (DAT_febe8aca < DAT_00031901) {
      DAT_febe8aca = DAT_febe8aca + 1;
      DAT_febe8ac8 = 1;
    }
    else {
      DAT_febe8ac8 = 0;
    }
  }
  return;
}

void debounce_secondary_channel1_request_bit17_56dee(void)

{
  if ((DAT_febe8ae4 & 0x20000) == 0) {
    DAT_febe8acd = 0;
    if (DAT_febe8acc < DAT_00031900) {
      DAT_febe8acc = DAT_febe8acc + 1;
      DAT_febe8acb = 3;
    }
    else {
      DAT_febe8acb = 2;
    }
  }
  else {
    DAT_febe8acc = 0;
    if (DAT_febe8acd < DAT_00031901) {
      DAT_febe8acd = DAT_febe8acd + 1;
      DAT_febe8acb = 1;
    }
    else {
      DAT_febe8acb = 0;
    }
  }
  return;
}

void aggregate_secondary_channel_requests_and_debounce_56e34(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  uint32_t puVar4;
  uint uVar5;
  
  puVar4 = 0xfebeb800u;
  uVar5 = 0;
  iVar3 = 0;
  do {
    iVar2 = iVar3 + 1;
    uVar5 = uVar5 | (*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xfebe8ad0u + (uint32_t)(iVar3) * 4u))));
    iVar1 = iVar3 + -4;
    iVar3 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  publish_inverted_request_bits1_and17_at_3885_56d92(uVar5);
  (*((uint *)camry_host_ptr((uint32_t)(puVar4 + -0x2d1c)))) = uVar5;
  debounce_secondary_channel0_request_bit1_56daa();
  debounce_secondary_channel1_request_bit17_56dee();
  return;
}

void set_secondary_channel_request_bounded5_56e66(uint param_1,undefined4 param_2)

{
  if ((param_1 & 0xff) < 5) {
    (*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xfebe8ad0u + (uint32_t)(param_1 & 0xff) * 4u)))) = param_2;
  }
  return;
}

void return_only_stub_56e7a(void)

{
  return;
}

void initialize_two_secondary_priority_masks_56e7c(void)

{
  DAT_febe8ae8 = 4;
  DAT_febe8aec = 0x40000;
  return;
}

void decode_low_priority_bits1_and2_at_387e_56e8c(uint param_1)

{
  if ((param_1 >> 2 & 1) == 0) {
    if ((param_1 >> 1 & 1) == 0) {
      DAT_febe387e = 0xff;
    }
    else {
      DAT_febe387e = 0;
    }
    DAT_febe387f = 0xff;
  }
  else {
    DAT_febe387e = 0xff;
    DAT_febe387f = 0;
  }
  return;
}

void decode_high_priority_bits17_and18_at_387c_56eae(uint param_1)

{
  if ((param_1 >> 0x12 & 1) == 0) {
    if ((param_1 >> 0x11 & 1) == 0) {
      DAT_febe387c = 0xff;
    }
    else {
      DAT_febe387c = 0;
    }
    DAT_febe387d = 0xff;
  }
  else {
    DAT_febe387c = 0xff;
    DAT_febe387d = 0;
  }
  return;
}

void aggregate_secondary_priority_masks_with_requests_56ed0(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  uint32_t puVar4;
  uint uVar5;
  
  puVar4 = 0xfebeb800u;
  if ((DAT_febe8ae4 >> 1 & 1) == 0) {
    uVar5 = 0;
  }
  else {
    uVar5 = 4;
  }
  if ((DAT_febe8ae4 >> 0x11 & 1) != 0) {
    uVar5 = uVar5 | 0x40000;
  }
  iVar3 = 0;
  do {
    iVar2 = iVar3 + 1;
    uVar5 = uVar5 | (*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xfebe8ae8u + (uint32_t)(iVar3) * 4u))));
    iVar1 = iVar3 + -1;
    iVar3 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  decode_low_priority_bits1_and2_at_387e_56e8c(uVar5);
  decode_high_priority_bits17_and18_at_387c_56eae(uVar5);
  (*((uint *)camry_host_ptr((uint32_t)(puVar4 + -0x2d10)))) = uVar5;
  return;
}

void set_secondary_priority_mask_bounded2_56f14(uint param_1,undefined4 param_2)

{
  if ((param_1 & 0xff) < 2) {
    (*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xfebe8ae8u + (uint32_t)(param_1 & 0xff) * 4u)))) = param_2;
  }
  return;
}

void return_only_stub_56f28(void)

{
  return;
}

void return_only_stub_56f2a(void)

{
  return;
}

void return_only_stub_56f2c(void)

{
  return;
}

void return_only_stub_56f2e(void)

{
  return;
}

void return_only_stub_56f30(void)

{
  return;
}

void report_event25_for_up_to_five_ring_samples_56f32(void)

{
  uint uVar1;
  undefined8 uVar2;
  undefined2 uVar3;
  int iVar4;
  uint uVar5;
  uint uVar6;
  
  uVar2 = 0xfebeb800;
  iVar4 = get_febe508f_byte_6a12a();
  if (iVar4 == 0x5a) {
    uVar5 = get_febe508b_byte_6a144();
    uVar6 = get_febe508c_byte_6a14a();
    uVar1 = uVar6 + uVar5 & 0xff;
    if (5 < uVar5) {
      uVar6 = uVar1 + 3 & 7;
      uVar1 = uVar6 + 5;
    }
    for (; uVar6 < uVar1; uVar6 = uVar6 + 1 & 0xff) {
      uVar3 = get_eight_slot_febe50b6_halfword_6a136(uVar6 & 7);
      (*((undefined2 *)camry_host_ptr((uint32_t)((int)uVar2 + -0x2d08)))) = uVar3;
      gate_indexed_event_payload_during_diagnostic_clears_51cf6(0x25,0x32);
    }
  }
  return;
}

void return_only_stub_56f8a(void)

{
  return;
}

void return_only_stub_56f8c(void)

{
  return;
}

void report_event27_and_count_status11_occurrences_56f8e(void)

{
  uint32_t puVar1;
  int iVar2;
  
  puVar1 = 0xfebeb800u;
  iVar2 = get_security_comparison_result_8d9a2();
  if (iVar2 == 0xb) {
    gate_indexed_event_payload_during_diagnostic_clears_51cf6(0x27,0x32);
    if ((*((int *)camry_host_ptr((uint32_t)(puVar1 + -0x2d04)))) != -1) {
      (*((int *)camry_host_ptr((uint32_t)(puVar1 + -0x2d04)))) = (*((int *)camry_host_ptr((uint32_t)(puVar1 + -0x2d04)))) + 1;
    }
    clear_security_comparison_result_8d9ac();
  }
  return;
}

void reset_event27_occurrence_counter_56fbc(void)

{
  DAT_febe8afc = 0;
  return;
}

void reset_eventcc_report_latch_56fc2(void)

{
  DAT_febe8b00 = 0;
  return;
}

void reset_eventcc_report_latch_56fc8(void)

{
  DAT_febe8b00 = 0;
  return;
}

void report_eventcc_once_on_6a150_flag_56fce(void)

{
  uint32_t puVar1;
  int iVar2;
  char cVar3;
  
  cVar3 = DAT_febe8b00;
  puVar1 = (0xfebeb800u);
  if ((DAT_febe8b00 != 'Z') && (puVar1 = (0xfebeb800u), iVar2 = get_crypto_test_failed_byte_6a150(), iVar2 == 0x5a)) {
    report_diagnostic_event_failure(0xcc,0x32);
    cVar3 = 'Z';
  }
  (*((volatile undefined *)camry_host_ptr((uint32_t)(0xfebeb800u + (uint32_t)(-0x2d00) * 1u)))) = cVar3;
  return;
}

void return_only_stub_56ffe(void)

{
  return;
}
