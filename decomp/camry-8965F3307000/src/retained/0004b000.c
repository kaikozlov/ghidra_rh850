#include "common.h"

void return_only_stub_4b04a(void)

{
  return;
}

void return_only_stub_4b04c(void)

{
  return;
}

void decode_receive_slot_6_two_single_bit_fields_4b04e(void)

{
  char cVar1;
  uint32_t puVar2;
  uchar uVar3;
  
  cVar1 = DAT_febe5350;
  puVar2 = 0xfebeb800u;
  if ((internal_source_admission_state < 2) && (DAT_febe800b != DAT_febe5350)) {
    puVar2 = 0xfebeb800u;
    extract_com_big_endian_bitfield_with_optional_sign_extension_7d12a(0x79,0xd1,1,0,0,((undefined *)camry_host_ptr(0xfebe800cu)));
    extract_com_big_endian_bitfield_with_optional_sign_extension_7d12a(0x76, 0xcf, 1, 4, 0, ((undefined *)camry_host_ptr((uint32_t)(puVar2 + -0x37f3))));
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x37f5))))) = cVar1;
  uVar3 = get_application_receive_status(6);
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x37f6))))) = uVar3;
  return;
}

void return_only_stub_4b0ac(void)

{
  return;
}

void return_only_stub_4b0ae(void)

{
  return;
}

void decode_receive_slot_7_signed11_sixbit_and_flag_4b0b0(void)

{
  char cVar1;
  uint32_t puVar2;
  uchar uVar3;
  
  cVar1 = DAT_febe5351;
  puVar2 = 0xfebeb800u;
  if ((internal_source_admission_state < 2) && (DAT_febe8011 != DAT_febe5351)) {
    puVar2 = 0xfebeb800u;
    extract_com_big_endian_bitfield_with_optional_sign_extension_7d12a(0x82,0xda,0xb,0,1,((undefined *)camry_host_ptr(0xfebe800eu)));
    extract_com_big_endian_bitfield_with_optional_sign_extension_7d12a(0x7c, 0xd7, 6, 2, 0, ((undefined *)camry_host_ptr((uint32_t)(puVar2 + -0x37ee))));
    extract_com_big_endian_bitfield_with_optional_sign_extension_7d12a(0x7e, 0xd8, 1, 3, 0, ((undefined *)camry_host_ptr((uint32_t)(puVar2 + -0x37ed))));
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x37ef))))) = cVar1;
  uVar3 = get_application_receive_status(7);
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x37f0))))) = uVar3;
  return;
}

void return_only_stub_4b12a(void)

{
  return;
}

void return_only_stub_4b12c(void)

{
  return;
}

void decode_receive_slot_8_signed16_and_flag_4b12e(void)

{
  char cVar1;
  uint32_t puVar2;
  uchar uVar3;
  
  cVar1 = DAT_febe5352;
  puVar2 = 0xfebeb800u;
  if ((internal_source_admission_state < 2) && (DAT_febe8017 != DAT_febe5352)) {
    puVar2 = 0xfebeb800u;
    extract_com_big_endian_bitfield_with_optional_sign_extension_7d12a(0x86,0xdf,0x10,0,1,((undefined *)camry_host_ptr(0xfebe8014u)));
    extract_com_big_endian_bitfield_with_optional_sign_extension_7d12a(0x87, 0xe2, 1, 1, 0, ((undefined *)camry_host_ptr((uint32_t)(puVar2 + -0x37ea))));
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x37e9))))) = cVar1;
  uVar3 = get_application_receive_status(8);
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x37e8))))) = uVar3;
  return;
}

void return_only_stub_4b190(void)

{
  return;
}

void return_only_stub_4b192(void)

{
  return;
}

void decode_receive_slot_9_byte_and_flag_4b194(void)

{
  char cVar1;
  uint32_t puVar2;
  uchar uVar3;
  
  cVar1 = DAT_febe5353;
  puVar2 = 0xfebeb800u;
  if ((internal_source_admission_state < 2) && (DAT_febe801b != DAT_febe5353)) {
    puVar2 = 0xfebeb800u;
    extract_com_big_endian_bitfield_with_optional_sign_extension_7d12a(0x8a,0xe7,8,0,0,((undefined *)camry_host_ptr(0xfebe8019u)));
    extract_com_big_endian_bitfield_with_optional_sign_extension_7d12a(0x8b, 0xe9, 1, 7, 0, ((undefined *)camry_host_ptr((uint32_t)(puVar2 + -0x37e6))));
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x37e5))))) = cVar1;
  uVar3 = get_application_receive_status(9);
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x37e4))))) = uVar3;
  return;
}

void return_only_stub_4b1f2(void)

{
  return;
}

void return_only_stub_4b1f4(void)

{
  return;
}

void decode_receive_slot_10_signed16_field_4b1f6(void)

{
  char cVar1;
  uint32_t puVar2;
  uchar uVar3;
  
  cVar1 = DAT_febe5354;
  puVar2 = 0xfebeb800u;
  if ((internal_source_admission_state < 2) && (DAT_febe8020 != DAT_febe5354)) {
    puVar2 = 0xfebeb800u;
    extract_com_big_endian_bitfield_with_optional_sign_extension_7d12a(0x8d,0xf1,0x10,0,1,((undefined *)camry_host_ptr(0xfebe801eu)));
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x37e0))))) = cVar1;
  uVar3 = get_application_receive_status(10);
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x37df))))) = uVar3;
  return;
}

void return_only_stub_4b23e(void)

{
  return;
}

void return_only_stub_4b240(void)

{
  return;
}

void decode_receive_slot_11_ten_packed_fields_4b242(void)

{
  char cVar1;
  uint32_t puVar2;
  uchar uVar3;
  
  cVar1 = DAT_febe5355;
  puVar2 = 0xfebeb800u;
  if ((internal_source_admission_state < 2) && (DAT_febe802c != DAT_febe5355)) {
    puVar2 = 0xfebeb800u;
    extract_com_big_endian_bitfield_with_optional_sign_extension_7d12a(0x90,0xf7,4,4,0,((undefined *)camry_host_ptr(0xfebe8022u)));
    extract_com_big_endian_bitfield_with_optional_sign_extension_7d12a(0x91, 0xf7, 4, 0, 0, ((undefined *)camry_host_ptr((uint32_t)(puVar2 + -0x37dd))));
    extract_com_big_endian_bitfield_with_optional_sign_extension_7d12a(0x92, 0xf8, 4, 4, 0, ((undefined *)camry_host_ptr((uint32_t)(puVar2 + -0x37dc))));
    extract_com_big_endian_bitfield_with_optional_sign_extension_7d12a(0x93, 0xf8, 1, 3, 0, ((undefined *)camry_host_ptr((uint32_t)(puVar2 + -0x37db))));
    extract_com_big_endian_bitfield_with_optional_sign_extension_7d12a(0x99, 0xfb, 4, 4, 0, ((undefined *)camry_host_ptr((uint32_t)(puVar2 + -0x37da))));
    extract_com_big_endian_bitfield_with_optional_sign_extension_7d12a(0x96, 0xf9, 4, 4, 0, ((undefined *)camry_host_ptr((uint32_t)(puVar2 + -0x37d9))));
    extract_com_big_endian_bitfield_with_optional_sign_extension_7d12a(0x97, 0xf9, 4, 0, 0, ((undefined *)camry_host_ptr((uint32_t)(puVar2 + -0x37d8))));
    extract_com_big_endian_bitfield_with_optional_sign_extension_7d12a(0x94, 0xf8, 2, 1, 0, ((undefined *)camry_host_ptr((uint32_t)(puVar2 + -0x37d7))));
    extract_com_big_endian_bitfield_with_optional_sign_extension_7d12a(0x98, 0xfa, 4, 0, 0, ((undefined *)camry_host_ptr((uint32_t)(puVar2 + -0x37d6))));
    extract_com_big_endian_bitfield_with_optional_sign_extension_7d12a(0x9a, 0xfb, 4, 0, 0, ((undefined *)camry_host_ptr((uint32_t)(puVar2 + -0x37d5))));
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x37d4))))) = cVar1;
  uVar3 = get_application_receive_status(0xb);
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x37d3))))) = uVar3;
  return;
}

void return_only_stub_4b374(void)

{
  return;
}

void return_only_stub_4b376(void)

{
  return;
}

void refresh_route30_health_inputs(void)

{
  uint32_t puVar1;
  uchar uVar2;
  
  uVar2 = route30_copy_generation;
  puVar1 = 0xfebeb800u;
  if ((internal_source_admission_state < 2) &&
     (route30_consumed_generation != route30_copy_generation)) {
    puVar1 = 0xfebeb800u;
    extract_com_big_endian_bitfield_with_optional_sign_extension_7d12a(0x9d,0xff,1,7,0,((undefined *)camry_host_ptr(0xfebe8031u)));
    extract_com_big_endian_bitfield_with_optional_sign_extension_7d12a(0xa0, 0xff, 4, 0, 0, ((undefined *)camry_host_ptr((uint32_t)(puVar1 + -0x37d0))));
    extract_com_big_endian_bitfield_with_optional_sign_extension_7d12a(0xa6, 0x104, 2, 6, 0, ((undefined *)camry_host_ptr((uint32_t)(puVar1 + -0x37ce))));
    extract_com_big_endian_bitfield_with_optional_sign_extension_7d12a(0xa3, 0x100, 4, 0, 0, ((undefined *)camry_host_ptr((uint32_t)(puVar1 + -0x37cd))));
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x37d2))))) = uVar2;
  uVar2 = get_application_receive_status(0xc);
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x37d1))))) = uVar2;
  return;
}

void return_only_stub_4b40a(void)

{
  return;
}

void return_only_stub_4b40c(void)

{
  return;
}

void decode_receive_slot_13_twobit_and_u32_fields_4b40e(void)

{
  char cVar1;
  uint32_t puVar2;
  uchar uVar3;
  
  cVar1 = DAT_febe5357;
  puVar2 = 0xfebeb800u;
  if ((internal_source_admission_state < 2) && (DAT_febe8039 != DAT_febe5357)) {
    puVar2 = 0xfebeb800u;
    extract_com_big_endian_bitfield_with_optional_sign_extension_7d12a(0xa9,0x10a,2,4,0,((undefined *)camry_host_ptr(0xfebe8038u)));
    extract_com_big_endian_bitfield_with_optional_sign_extension_7d12a(0xab, 0x10b, 0x20, 0, 0, ((undefined *)camry_host_ptr((uint32_t)(puVar2 + -0x37cc))));
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x37c7))))) = cVar1;
  uVar3 = get_application_receive_status(0xd);
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x37c6))))) = uVar3;
  return;
}

void return_only_stub_4b46e(void)

{
  return;
}

void return_only_stub_4b470(void)

{
  return;
}

void decode_receive_slot_14_two_single_bit_fields_4b472(void)

{
  char cVar1;
  uint32_t puVar2;
  uchar uVar3;
  
  cVar1 = DAT_febe5358;
  puVar2 = 0xfebeb800u;
  if ((internal_source_admission_state < 2) && (DAT_febe803d != DAT_febe5358)) {
    puVar2 = 0xfebeb800u;
    extract_com_big_endian_bitfield_with_optional_sign_extension_7d12a(0xac,0x10f,1,0,0,((undefined *)camry_host_ptr(0xfebe803bu)));
    extract_com_big_endian_bitfield_with_optional_sign_extension_7d12a(0xad, 0x110, 1, 0, 0, ((undefined *)camry_host_ptr((uint32_t)(puVar2 + -0x37c4))));
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x37c3))))) = cVar1;
  uVar3 = get_application_receive_status(0xe);
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x37c2))))) = uVar3;
  return;
}

void return_only_stub_4b4d0(void)

{
  return;
}

void return_only_stub_4b4d2(void)

{
  return;
}

void decode_receive_slot_15_six_byte_fields_4b4d4(void)

{
  char cVar1;
  uint32_t puVar2;
  uchar uVar3;
  
  cVar1 = DAT_febe5359;
  puVar2 = 0xfebeb800u;
  if ((internal_source_admission_state < 2) && (DAT_febe8045 != DAT_febe5359)) {
    puVar2 = 0xfebeb800u;
    extract_com_big_endian_bitfield_with_optional_sign_extension_7d12a(0xb1,0x119,8,0,0,((undefined *)camry_host_ptr(0xfebe803fu)));
    extract_com_big_endian_bitfield_with_optional_sign_extension_7d12a(0xb2, 0x11a, 8, 0, 0, ((undefined *)camry_host_ptr((uint32_t)(puVar2 + -0x37c0))));
    extract_com_big_endian_bitfield_with_optional_sign_extension_7d12a(0xb3, 0x11b, 8, 0, 0, ((undefined *)camry_host_ptr((uint32_t)(puVar2 + -0x37bf))));
    extract_com_big_endian_bitfield_with_optional_sign_extension_7d12a(0xb4, 0x11c, 8, 0, 0, ((undefined *)camry_host_ptr((uint32_t)(puVar2 + -0x37be))));
    extract_com_big_endian_bitfield_with_optional_sign_extension_7d12a(0xb5, 0x11d, 8, 0, 0, ((undefined *)camry_host_ptr((uint32_t)(puVar2 + -0x37bd))));
    extract_com_big_endian_bitfield_with_optional_sign_extension_7d12a(0xb6, 0x11e, 8, 0, 0, ((undefined *)camry_host_ptr((uint32_t)(puVar2 + -0x37bc))));
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x37bb))))) = cVar1;
  uVar3 = get_application_receive_status(0xf);
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x37ba))))) = uVar3;
  return;
}

void return_only_stub_4b59a(void)

{
  return;
}

void return_only_stub_4b59c(void)

{
  return;
}

void decode_receive_slot_17_three_signed_fields_and_four_flags_4b59e(void)

{
  char cVar1;
  uint32_t puVar2;
  uchar uVar3;
  
  cVar1 = DAT_febe535b;
  puVar2 = 0xfebeb800u;
  if ((internal_source_admission_state < 2) && (DAT_febe8051 != DAT_febe535b)) {
    puVar2 = 0xfebeb800u;
    extract_com_big_endian_bitfield_with_optional_sign_extension_7d12a(0xbb,0x127,0xc,0,1,((undefined *)camry_host_ptr(0xfebe8048u)));
    extract_com_big_endian_bitfield_with_optional_sign_extension_7d12a(0xbc, 299, 4, 4, 1, ((undefined *)camry_host_ptr((uint32_t)(puVar2 + -0x37b1))));
    extract_com_big_endian_bitfield_with_optional_sign_extension_7d12a(0xbd, 299, 0xc, 0, 1, ((undefined *)camry_host_ptr((uint32_t)(puVar2 + -0x37b6))));
    extract_com_big_endian_bitfield_with_optional_sign_extension_7d12a(0xb8, 0x127, 1, 7, 0, ((undefined *)camry_host_ptr((uint32_t)(puVar2 + -0x37b4))));
    extract_com_big_endian_bitfield_with_optional_sign_extension_7d12a(0xb9, 0x127, 1, 6, 0, ((undefined *)camry_host_ptr((uint32_t)(puVar2 + -0x37b3))));
    extract_com_big_endian_bitfield_with_optional_sign_extension_7d12a(0xba, 0x127, 1, 5, 0, ((undefined *)camry_host_ptr((uint32_t)(puVar2 + -0x37b2))));
    extract_com_big_endian_bitfield_with_optional_sign_extension_7d12a(0xbe, 0x12d, 1, 3, 0, ((undefined *)camry_host_ptr((uint32_t)(puVar2 + -0x37b0))));
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x37af))))) = cVar1;
  uVar3 = get_application_receive_status(0x11);
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x37ae))))) = uVar3;
  return;
}

void return_only_stub_4b686(void)

{
  return;
}

void return_only_stub_4b688(void)

{
  return;
}

void decode_receive_slot_18_four_biased_u15_values_and_flags_4b68a(void)

{
  char cVar1;
  uint32_t puVar2;
  uchar uVar3;
  
  cVar1 = DAT_febe535c;
  puVar2 = 0xfebeb800u;
  if ((internal_source_admission_state < 2) && (DAT_febe8068 != DAT_febe535c)) {
    puVar2 = 0xfebeb800u;
    extract_com_big_endian_bitfield_with_optional_sign_extension_7d12a(0xc3,0x147,0xf,0,0,((undefined *)camry_host_ptr(0xfebe8054u)));
    subtract_signed_bias_from_u16_with_upper_clamp_if_zero_4afcc(0, 0x1a6f, (*((undefined2 *)camry_host_ptr((uint32_t)(puVar2 + -0x37ac)))), ((undefined *)camry_host_ptr((uint32_t)(puVar2 + -0x37a4))));
    extract_com_big_endian_bitfield_with_optional_sign_extension_7d12a(0xc5, 0x149, 0xf, 0, 0, ((undefined *)camry_host_ptr((uint32_t)(puVar2 + -0x37aa))));
    subtract_signed_bias_from_u16_with_upper_clamp_if_zero_4afcc(0, 0x1a6f, (*((undefined2 *)camry_host_ptr((uint32_t)(puVar2 + -0x37aa)))), ((undefined *)camry_host_ptr((uint32_t)(puVar2 + -0x37a2))));
    extract_com_big_endian_bitfield_with_optional_sign_extension_7d12a(199, 0x14b, 0xf, 0, 0, ((undefined *)camry_host_ptr((uint32_t)(puVar2 + -0x37a8))));
    subtract_signed_bias_from_u16_with_upper_clamp_if_zero_4afcc(0, 0x1a6f, (*((undefined2 *)camry_host_ptr((uint32_t)(puVar2 + -0x37a8)))), ((undefined *)camry_host_ptr((uint32_t)(puVar2 + -0x37a0))));
    extract_com_big_endian_bitfield_with_optional_sign_extension_7d12a(0xc9, 0x14d, 0xf, 0, 0, ((undefined *)camry_host_ptr((uint32_t)(puVar2 + -0x37a6))));
    subtract_signed_bias_from_u16_with_upper_clamp_if_zero_4afcc(0, 0x1a6f, (*((undefined2 *)camry_host_ptr((uint32_t)(puVar2 + -0x37a6)))), ((undefined *)camry_host_ptr((uint32_t)(puVar2 + -0x379e))));
    extract_com_big_endian_bitfield_with_optional_sign_extension_7d12a(0xc2, 0x147, 1, 7, 0, ((undefined *)camry_host_ptr((uint32_t)(puVar2 + -0x379c))));
    extract_com_big_endian_bitfield_with_optional_sign_extension_7d12a(0xc4, 0x149, 1, 7, 0, ((undefined *)camry_host_ptr((uint32_t)(puVar2 + -0x379b))));
    extract_com_big_endian_bitfield_with_optional_sign_extension_7d12a(0xc6, 0x14b, 1, 7, 0, ((undefined *)camry_host_ptr((uint32_t)(puVar2 + -0x379a))));
    extract_com_big_endian_bitfield_with_optional_sign_extension_7d12a(200, 0x14d, 1, 7, 0, ((undefined *)camry_host_ptr((uint32_t)(puVar2 + -0x3799))));
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x3798))))) = cVar1;
  uVar3 = get_application_receive_status(0x12);
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x3797))))) = uVar3;
  return;
}

void return_only_stub_4b7d2(void)

{
  return;
}

void return_only_stub_4b7d4(void)

{
  return;
}

void decode_receive_slot_19_three_flags_and_tenbit_field_4b7d6(void)

{
  char cVar1;
  uint32_t puVar2;
  uchar uVar3;
  
  cVar1 = DAT_febe535d;
  puVar2 = 0xfebeb800u;
  if ((internal_source_admission_state < 2) && (DAT_febe806e != DAT_febe535d)) {
    puVar2 = 0xfebeb800u;
    extract_com_big_endian_bitfield_with_optional_sign_extension_7d12a(0xce,0x14f,1,3,0,((undefined *)camry_host_ptr(0xfebe806cu)));
    extract_com_big_endian_bitfield_with_optional_sign_extension_7d12a(0xca, 0x14f, 1, 7, 0, ((undefined *)camry_host_ptr((uint32_t)(puVar2 + -0x3793))));
    extract_com_big_endian_bitfield_with_optional_sign_extension_7d12a(0xd0, 0x151, 1, 3, 0, ((undefined *)camry_host_ptr((uint32_t)(puVar2 + -0x3790))));
    extract_com_big_endian_bitfield_with_optional_sign_extension_7d12a(0xd1, 0x151, 10, 0, 0, ((undefined *)camry_host_ptr((uint32_t)(puVar2 + -0x3796))));
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x3792))))) = cVar1;
  uVar3 = get_application_receive_status(0x13);
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x3791))))) = uVar3;
  return;
}

void return_only_stub_4b86a(void)

{
  return;
}

void return_only_stub_4b86c(void)

{
  return;
}

void decode_changed_rx14_two_signed_words_and_flag_4b86e(void)

{
  char cVar1;
  uint32_t puVar2;
  uchar uVar3;
  
  cVar1 = DAT_febe535e;
  puVar2 = 0xfebeb800u;
  if ((internal_source_admission_state < 2) && (DAT_febe8077 != DAT_febe535e)) {
    puVar2 = 0xfebeb800u;
    extract_com_big_endian_bitfield_with_optional_sign_extension_7d12a(0xd4,0x158,0x10,0,1,((undefined *)camry_host_ptr(0xfebe8072u)));
    extract_com_big_endian_bitfield_with_optional_sign_extension_7d12a(0xd5, 0x15a, 0x10, 0, 1, ((undefined *)camry_host_ptr((uint32_t)(puVar2 + -0x378c))));
    extract_com_big_endian_bitfield_with_optional_sign_extension_7d12a(0xd3, 0x157, 1, 3, 0, ((undefined *)camry_host_ptr((uint32_t)(puVar2 + -0x378a))));
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x3789))))) = cVar1;
  uVar3 = get_application_receive_status(0x14);
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x3788))))) = uVar3;
  return;
}

void return_only_stub_4b8f0(void)

{
  return;
}

void return_only_stub_4b8f2(void)

{
  return;
}

void decode_changed_rx15_eight_bitfields_4b8f4(void)

{
  char cVar1;
  uint32_t puVar2;
  uchar uVar3;
  
  cVar1 = DAT_febe535f;
  puVar2 = 0xfebeb800u;
  if ((internal_source_admission_state < 2) && (DAT_febe8080 != DAT_febe535f)) {
    puVar2 = 0xfebeb800u;
    extract_com_big_endian_bitfield_with_optional_sign_extension_7d12a(0xd7,0x15f,5,3,0,((undefined *)camry_host_ptr(0xfebe8079u)));
    extract_com_big_endian_bitfield_with_optional_sign_extension_7d12a(0xd8, 0x15f, 1, 2, 0, ((undefined *)camry_host_ptr((uint32_t)(puVar2 + -0x3786))));
    extract_com_big_endian_bitfield_with_optional_sign_extension_7d12a(0xd9, 0x15f, 1, 1, 0, ((undefined *)camry_host_ptr((uint32_t)(puVar2 + -0x3785))));
    extract_com_big_endian_bitfield_with_optional_sign_extension_7d12a(0xdb, 0x160, 6, 2, 0, ((undefined *)camry_host_ptr((uint32_t)(puVar2 + -0x3784))));
    extract_com_big_endian_bitfield_with_optional_sign_extension_7d12a(0xdd, 0x160, 1, 0, 0, ((undefined *)camry_host_ptr((uint32_t)(puVar2 + -0x3783))));
    extract_com_big_endian_bitfield_with_optional_sign_extension_7d12a(0xde, 0x161, 1, 6, 0, ((undefined *)camry_host_ptr((uint32_t)(puVar2 + -0x3782))));
    extract_com_big_endian_bitfield_with_optional_sign_extension_7d12a(0xdf, 0x161, 1, 5, 0, ((undefined *)camry_host_ptr((uint32_t)(puVar2 + -0x3781))));
    extract_com_big_endian_bitfield_with_optional_sign_extension_7d12a(0xe0, 0x161, 4, 0, 0, ((undefined *)camry_host_ptr((uint32_t)(puVar2 + -0x377e))));
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x3780))))) = cVar1;
  uVar3 = get_application_receive_status(0x15);
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x377f))))) = uVar3;
  return;
}

void return_only_stub_4b9f0(void)

{
  return;
}

void return_only_stub_4b9f2(void)

{
  return;
}

void decode_changed_rx16_three_ten_bit_values_and_flags_4b9f4(void)

{
  char cVar1;
  uint32_t puVar2;
  uchar uVar3;
  
  cVar1 = DAT_febe5360;
  puVar2 = 0xfebeb800u;
  if ((internal_source_admission_state < 2) && (DAT_febe8097 != DAT_febe5360)) {
    puVar2 = 0xfebeb800u;
    extract_com_big_endian_bitfield_with_optional_sign_extension_7d12a(0xe3,0x167,1,7,0,((undefined *)camry_host_ptr(0xfebe8090u)));
    extract_com_big_endian_bitfield_with_optional_sign_extension_7d12a(0xe4, 0x167, 1, 6, 0, ((undefined *)camry_host_ptr((uint32_t)(puVar2 + -0x376f))));
    extract_com_big_endian_bitfield_with_optional_sign_extension_7d12a(0xe5, 0x167, 10, 0, 0, ((undefined *)camry_host_ptr((uint32_t)(puVar2 + -0x377c))));
    subtract_signed_bias_from_u16_with_upper_clamp_if_zero_4afcc(0, 0x200, (*((undefined2 *)camry_host_ptr((uint32_t)(puVar2 + -0x377c)))), ((undefined *)camry_host_ptr((uint32_t)(puVar2 + -0x3776))));
    extract_com_big_endian_bitfield_with_optional_sign_extension_7d12a(0xe6, 0x169, 1, 7, 0, ((undefined *)camry_host_ptr((uint32_t)(puVar2 + -0x376e))));
    extract_com_big_endian_bitfield_with_optional_sign_extension_7d12a(0xe7, 0x169, 1, 6, 0, ((undefined *)camry_host_ptr((uint32_t)(puVar2 + -0x376d))));
    extract_com_big_endian_bitfield_with_optional_sign_extension_7d12a(0xe8, 0x169, 10, 0, 0, ((undefined *)camry_host_ptr((uint32_t)(puVar2 + -0x377a))));
    subtract_signed_bias_from_u16_with_upper_clamp_if_zero_4afcc(0, 0x200, (*((undefined2 *)camry_host_ptr((uint32_t)(puVar2 + -0x377a)))), ((undefined *)camry_host_ptr((uint32_t)(puVar2 + -0x3774))));
    extract_com_big_endian_bitfield_with_optional_sign_extension_7d12a(0xe9, 0x16b, 1, 7, 0, ((undefined *)camry_host_ptr((uint32_t)(puVar2 + -0x376c))));
    extract_com_big_endian_bitfield_with_optional_sign_extension_7d12a(0xea, 0x16b, 1, 6, 0, ((undefined *)camry_host_ptr((uint32_t)(puVar2 + -0x376b))));
    extract_com_big_endian_bitfield_with_optional_sign_extension_7d12a(0xeb, 0x16b, 10, 0, 0, ((undefined *)camry_host_ptr((uint32_t)(puVar2 + -0x3778))));
    subtract_signed_bias_from_u16_with_upper_clamp_if_zero_4afcc(0, 0x200, (*((undefined2 *)camry_host_ptr((uint32_t)(puVar2 + -0x3778)))), ((undefined *)camry_host_ptr((uint32_t)(puVar2 + -0x3772))));
    extract_com_big_endian_bitfield_with_optional_sign_extension_7d12a(0xf1, 0x183, 4, 4, 0, ((undefined *)camry_host_ptr((uint32_t)(puVar2 + -0x376a))));
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x3769))))) = cVar1;
  uVar3 = get_application_receive_status(0x16);
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x3768))))) = uVar3;
  return;
}

void return_only_stub_4bb5e(void)

{
  return;
}

void return_only_stub_4bb60(void)

{
  return;
}

void decode_changed_rx17_two_words_and_flags_4bb62(void)

{
  char cVar1;
  uint32_t puVar2;
  uchar uVar3;
  undefined1 uStack_9;
  
  cVar1 = DAT_febe5361;
  puVar2 = 0xfebeb800u;
  uStack_9 = DAT_febe80a0;
  if ((internal_source_admission_state < 2) && (DAT_febe80a4 != DAT_febe5361)) {
    puVar2 = 0xfebeb800u;
    extract_com_big_endian_bitfield_with_optional_sign_extension_7d12a(0xf6,0x188,0x10,0,0,((undefined *)camry_host_ptr(0xfebe809au)));
    extract_com_big_endian_bitfield_with_optional_sign_extension_7d12a(0xf7, 0x18a, 0x10, 0, 0, ((undefined *)camry_host_ptr((uint32_t)(puVar2 + -0x3764))));
    extract_com_big_endian_bitfield_with_optional_sign_extension_7d12a(0xf3,0x187,1,7,0,&uStack_9);
    extract_com_big_endian_bitfield_with_optional_sign_extension_7d12a(0xf4, 0x187, 1, 6, 0, ((undefined *)camry_host_ptr((uint32_t)(puVar2 + -0x375f))));
    extract_com_big_endian_bitfield_with_optional_sign_extension_7d12a(0xf9, 0x1a3, 4, 4, 0, ((undefined *)camry_host_ptr((uint32_t)(puVar2 + -0x375d))));
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x375c))))) = cVar1;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x3760))))) = uStack_9;
  uVar3 = get_application_receive_status(0x17);
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x375b))))) = uVar3;
  return;
}

void return_only_stub_4bc24(void)

{
  return;
}

void return_only_stub_4bc26(void)

{
  return;
}

void decode_changed_rx18_four_bytes_4bc28(void)

{
  char cVar1;
  uint32_t puVar2;
  uchar uVar3;
  
  cVar1 = DAT_febe5362;
  puVar2 = 0xfebeb800u;
  if ((internal_source_admission_state < 2) && (DAT_febe80a6 != DAT_febe5362)) {
    puVar2 = 0xfebeb800u;
    extract_com_big_endian_bitfield_with_optional_sign_extension_7d12a(0xfb,0x1a9,8,0,0,((undefined *)camry_host_ptr(0xfebe80a8u)));
    extract_com_big_endian_bitfield_with_optional_sign_extension_7d12a(0xfc, 0x1aa, 8, 0, 0, ((undefined *)camry_host_ptr((uint32_t)(puVar2 + -0x3757))));
    extract_com_big_endian_bitfield_with_optional_sign_extension_7d12a(0xfd, 0x1ac, 8, 0, 0, ((undefined *)camry_host_ptr((uint32_t)(puVar2 + -0x3756))));
    extract_com_big_endian_bitfield_with_optional_sign_extension_7d12a(0xfe, 0x1ad, 8, 0, 0, ((undefined *)camry_host_ptr((uint32_t)(puVar2 + -0x3755))));
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x375a))))) = cVar1;
  uVar3 = get_application_receive_status(0x18);
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x3759))))) = uVar3;
  return;
}

void return_only_stub_4bcbc(void)

{
  return;
}

void return_only_stub_4bcbe(void)

{
  return;
}

void decode_changed_rx19_two_signed_eighteen_bit_fields_4bcc0(void)

{
  char cVar1;
  uint32_t puVar2;
  uchar uVar3;
  
  cVar1 = DAT_febe5363;
  puVar2 = 0xfebeb800u;
  if ((internal_source_admission_state < 2) && (DAT_febe80b5 != DAT_febe5363)) {
    puVar2 = 0xfebeb800u;
    extract_com_big_endian_bitfield_with_optional_sign_extension_7d12a(0xff,0x1b1,0x12,6,1,((undefined *)camry_host_ptr(0xfebe80acu)));
    extract_com_big_endian_bitfield_with_optional_sign_extension_7d12a(0x100, 0x1b3, 1, 5, 0, ((undefined *)camry_host_ptr((uint32_t)(puVar2 + -0x374c))));
    extract_com_big_endian_bitfield_with_optional_sign_extension_7d12a(0x101, 0x1b3, 0x12, 0, 1, ((undefined *)camry_host_ptr((uint32_t)(puVar2 + -0x3750))));
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x374b))))) = cVar1;
  uVar3 = get_application_receive_status(0x19);
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x374a))))) = uVar3;
  return;
}

void return_only_stub_4bd42(void)

{
  return;
}

void return_only_stub_4bd44(void)

{
  return;
}

void decode_changed_rx1a_word_bytes_and_flags_4bd46(void)

{
  char cVar1;
  uint32_t puVar2;
  uchar uVar3;
  
  cVar1 = DAT_febe5364;
  puVar2 = 0xfebeb800u;
  if ((internal_source_admission_state < 2) && (DAT_febe80c8 != DAT_febe5364)) {
    puVar2 = 0xfebeb800u;
    extract_com_big_endian_bitfield_with_optional_sign_extension_7d12a(0x105,0x1ba,6,0,0,((undefined *)camry_host_ptr(0xfebe80bcu)));
    extract_com_big_endian_bitfield_with_optional_sign_extension_7d12a(0x106, 0x1bb, 0x10, 0, 1, ((undefined *)camry_host_ptr((uint32_t)(puVar2 + -0x3748))));
    extract_com_big_endian_bitfield_with_optional_sign_extension_7d12a(0x107, 0x1bd, 1, 7, 0, ((undefined *)camry_host_ptr((uint32_t)(puVar2 + -0x3735))));
    extract_com_big_endian_bitfield_with_optional_sign_extension_7d12a(0x108, 0x1bd, 3, 4, 0, ((undefined *)camry_host_ptr((uint32_t)(puVar2 + -0x3742))));
    extract_com_big_endian_bitfield_with_optional_sign_extension_7d12a(0x109, 0x1bd, 1, 2, 0, ((undefined *)camry_host_ptr((uint32_t)(puVar2 + -0x3740))));
    extract_com_big_endian_bitfield_with_optional_sign_extension_7d12a(0x10a, 0x1bd, 2, 0, 0, ((undefined *)camry_host_ptr((uint32_t)(puVar2 + -0x373f))));
    extract_com_big_endian_bitfield_with_optional_sign_extension_7d12a(0x10b, 0x1be, 2, 6, 0, ((undefined *)camry_host_ptr((uint32_t)(puVar2 + -0x373e))));
    extract_com_big_endian_bitfield_with_optional_sign_extension_7d12a(0x10c, 0x1be, 6, 0, 0, ((undefined *)camry_host_ptr((uint32_t)(puVar2 + -0x373d))));
    extract_com_big_endian_bitfield_with_optional_sign_extension_7d12a(0x10d, 0x1bf, 8, 0, 0, ((undefined *)camry_host_ptr((uint32_t)(puVar2 + -0x373c))));
    extract_com_big_endian_bitfield_with_optional_sign_extension_7d12a(0x10e, 0x1c0, 8, 0, 0, ((undefined *)camry_host_ptr((uint32_t)(puVar2 + -0x373b))));
    extract_com_big_endian_bitfield_with_optional_sign_extension_7d12a(0x10f, 0x1c1, 1, 7, 0, ((undefined *)camry_host_ptr((uint32_t)(puVar2 + -0x373a))));
    extract_com_big_endian_bitfield_with_optional_sign_extension_7d12a(0x110, 0x1c1, 1, 5, 0, ((undefined *)camry_host_ptr((uint32_t)(puVar2 + -0x3734))));
    extract_com_big_endian_bitfield_with_optional_sign_extension_7d12a(0x111, 0x1c1, 3, 0, 0, ((undefined *)camry_host_ptr((uint32_t)(puVar2 + -0x3736))));
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x3738))))) = cVar1;
  uVar3 = get_application_receive_status(0x1a);
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x3737))))) = uVar3;
  return;
}

void return_only_stub_4becc(void)

{
  return;
}

void return_only_stub_4bece(void)

{
  return;
}

void decode_changed_rx1b_three_bytes_4bed0(void)

{
  char cVar1;
  uint32_t puVar2;
  uchar uVar3;
  
  cVar1 = DAT_febe5365;
  puVar2 = 0xfebeb800u;
  if ((internal_source_admission_state < 2) && (DAT_febe80cf != DAT_febe5365)) {
    puVar2 = 0xfebeb800u;
    extract_com_big_endian_bitfield_with_optional_sign_extension_7d12a(0x114,0x1d7,8,0,0,((undefined *)camry_host_ptr(0xfebe80cdu)));
    extract_com_big_endian_bitfield_with_optional_sign_extension_7d12a(0x115, 0x1d8, 8, 0, 0, ((undefined *)camry_host_ptr((uint32_t)(puVar2 + -0x3732))));
    extract_com_big_endian_bitfield_with_optional_sign_extension_7d12a(0x116, 0x1d9, 8, 0, 0, ((undefined *)camry_host_ptr((uint32_t)(puVar2 + -0x372f))));
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x3731))))) = cVar1;
  uVar3 = get_application_receive_status(0x1b);
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x3730))))) = uVar3;
  return;
}

void return_only_stub_4bf4a(void)

{
  return;
}

void return_only_stub_4bf4c(void)

{
  return;
}

void decode_changed_rx1c_three_and_four_bit_fields_4bf4e(void)

{
  char cVar1;
  uint32_t puVar2;
  uchar uVar3;
  
  cVar1 = DAT_febe5366;
  puVar2 = 0xfebeb800u;
  if ((internal_source_admission_state < 2) && (DAT_febe80d4 != DAT_febe5366)) {
    puVar2 = 0xfebeb800u;
    extract_com_big_endian_bitfield_with_optional_sign_extension_7d12a(0x118,0x1df,3,4,0,((undefined *)camry_host_ptr(0xfebe80d2u)));
    extract_com_big_endian_bitfield_with_optional_sign_extension_7d12a(0x119, 0x1df, 4, 0, 0, ((undefined *)camry_host_ptr((uint32_t)(puVar2 + -0x372d))));
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x372c))))) = cVar1;
  uVar3 = get_application_receive_status(0x1c);
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x372b))))) = uVar3;
  return;
}

void return_only_stub_4bfae(void)

{
  return;
}

void return_only_stub_4bfb0(void)

{
  return;
}

void decode_changed_rx1d_low_nibble_4bfb2(void)

{
  char cVar1;
  uint32_t puVar2;
  uchar uVar3;
  
  cVar1 = DAT_febe5367;
  puVar2 = 0xfebeb800u;
  if ((internal_source_admission_state < 2) && (DAT_febe80d7 != DAT_febe5367)) {
    puVar2 = 0xfebeb800u;
    extract_com_big_endian_bitfield_with_optional_sign_extension_7d12a(0x11a,0x1e0,4,0,0,((undefined *)camry_host_ptr(0xfebe80d6u)));
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x3729))))) = cVar1;
  uVar3 = get_application_receive_status(0x1d);
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x3728))))) = uVar3;
  return;
}

void return_only_stub_4bff8(void)

{
  return;
}

void clear_byte_febe8143_4bffa(void)

{
  DAT_febe8143 = 0;
  return;
}
