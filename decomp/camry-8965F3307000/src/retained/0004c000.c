#include "common.h"

void derive_input_validity_flags_and_scaled_signed_outputs_4c000(void)

{
  ushort uVar1;
  int iVar2;
  ushort uVar3;
  
  uVar1 = DAT_febee8cc & 0xff00;
  DAT_febe80dd = 0;
  if (((uVar1 != 0x400) && ((uVar1 != 0x500 || (DAT_febee81f != '\x11')))) ||
     (uVar3 = DAT_febe6764 & 0x1ff, (DAT_febe6764 & 0x1ff) != 0)) {
    uVar3 = 1;
  }
  DAT_febe80e1 = (char)uVar3;
  if (((uVar1 != 0x400) && ((uVar1 != 0x500 || (DAT_febee81f != '\x11')))) ||
     ((DAT_febee887 != '\0' || (uVar1 = DAT_febe6764 & 0x1ff, (DAT_febe6764 & 0x1ff) != 0)))) {
    uVar1 = 1;
  }
  DAT_febe80e2 = (char)uVar1;
  if ((((DAT_febe82ba == 0) && (DAT_febe82c2 == 0)) && (DAT_febe82c4 == 0)) &&
     ((DAT_febee857 != '\"' && (DAT_febee858 != '\"')))) {
    DAT_febe80de = DAT_febee859 == '\"';
  }
  else {
    DAT_febe80de = true;
  }
  if (uVar1 == 1) {
    DAT_febe8152 = 0;
  }
  else {
    DAT_febe8152 = (short)((((int)(int16_t)DAT_febe66a8) * 100) / 0x100);
    iVar2 = (int)DAT_febe8152;
    if (iVar2 + -1000 < 0 == (iVar2 < 0 && -1 < iVar2 + -1000) && iVar2 != 1000) {
      DAT_febe8152 = 1000;
    }
    else if (iVar2 + 1000 < 0 != (-1 < iVar2 && iVar2 + 1000 < 0)) {
      DAT_febe8152 = -1000;
    }
  }
  DAT_febe8158 = 0;
  if (uVar3 != 1) {
    DAT_febe8158 = (undefined2)((((int)(int16_t)DAT_febe6718) * -100) / 0x80);
  }
  return;
}

void gate_clamp_and_scale_febe64ec_to_signed_word_4c0e8(void)

{
  uint32_t puVar1;
  
  if (((DAT_febee8cc & 0xff00) == 0x400) &&
     (DAT_febe812e = (undefined1)DAT_febe6764, (DAT_febe6764 & 0x1ff) == 0)) {
    puVar1 = ((uint32_t)(((int)(int32_t)DAT_febe64ec)));
    if ((int)(((int)(int32_t)DAT_febe64ec) + -0x8a99) < 0 ==
        ((int)DAT_febe64ec < 0 && -1 < (int)(((int)(int32_t)DAT_febe64ec) + -0x8a99))) {
      puVar1 = (0x8a99u);
    }
    if ((int)((uint32_t)((uint32_t)(0x8abcu + (uint32_t)((int)puVar1) * 1u))) < 0 !=
        (-1 < (int)(puVar1) && (int)((uint32_t)((uint32_t)(0x8abcu + (uint32_t)((int)puVar1) * 1u))) < 0)) {
      puVar1 = ((uint32_t)(0xffff7544));
    }
    DAT_febe8162 = (undefined2)( (int)(((int)(puVar1) * 0x7627)) / (int)0x100000);
  }
  else {
    DAT_febe812e = 1;
    DAT_febe8162 = 0;
  }
  DAT_febe80f5 = 0;
  DAT_febe80fd = 0;
  DAT_febe80fe = 0;
  DAT_febe80ff = 0;
  return;
}

void clear_bytes_febe8103_8104_8108_4c142(void)

{
  DAT_febe8103 = 0;
  DAT_febe8104 = 0;
  DAT_febe8108 = 0;
  return;
}

void pack_status_and_scaled_words_into_eight_bytes_4c14e(void)

{
  uint8_t stack_record_7[7];
  uint32_t puVar1;
  
  puVar1 = 0xfebeb800u;
  DAT_febe810d = (undefined1)((int)(int16_t)DAT_febe8048);
  DAT_febe810b = DAT_febe80de | 0x20;
  DAT_febe810c = (byte)((ushort)((int)(int16_t)DAT_febe8048) >> 8) & 0xf;
  store_s16_max_third_min_first_two_70110((int)((int)(int16_t)DAT_febe7d46),0x7ff,(int)0xfffff800,((uint8_t *)((stack_record_7 + 1))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x36f1))))) = ((uint8_t *)((stack_record_7 + 1)))[0];
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x36f2))))) = ((uint8_t *)((stack_record_7 + 1)))[1] & 0xf;
  store_s16_saturated_to_symmetric_s8_6a5cc((int)( (int)((*((short *)camry_host_ptr((uint32_t)(puVar1 + -0x36ae))))) / (int)10),((uint8_t *)(stack_record_7)));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x36f0))))) = stack_record_7[0];
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x36ef))))) = (char)((ushort)(*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x36a8)))) >> 8);
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x36ee))))) = (char)(*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x36a8))));
  return;
}

char maintain_generation_bounded_z_latch_4c1c0(void)

{
  char cVar1;
  
  if ((DAT_febe8100 == '\x01') && (DAT_febee82b == '\0')) {
    DAT_febe812c = 'Z';
    DAT_febe812b = 0;
    cVar1 = DAT_febee82b;
  }
  else {
    cVar1 = DAT_febe8100;
    if (DAT_febe812c != 'Z') {
      DAT_febe812a = DAT_febe5339;
      return DAT_febee82b;
    }
  }
  if ((DAT_febe812b < DAT_0002fbf8) && (DAT_febe812a == DAT_febe5339)) {
    DAT_febe812b = DAT_febe812b + 1;
  }
  else {
    DAT_febe812b = '\0';
    DAT_febe812c = '\0';
    cVar1 = DAT_febee82b;
  }
  DAT_febe812a = DAT_febe5339;
  return cVar1;
}

void store_status_with_low_two_bit_override_4c216(undefined1 param_1)

{
  if (((DAT_febe6764 & 3) == 0) || (DAT_febe8143 == '\0')) {
    DAT_febe8101 = 0;
  }
  else {
    param_1 = 7;
    DAT_febe8101 = 1;
  }
  DAT_febe8100 = param_1;
  return;
}

undefined4 refresh_latched_status_with_override_4c238(void)

{
  undefined4 uVar1;
  
  uVar1 = (uint)(unsigned char)maintain_generation_bounded_z_latch_4c1c0();
  store_status_with_low_two_bit_override_4c216((undefined1)uVar1);
  return uVar1;
}

void copy_classifier_fields_and_encode_state_group_4c24a(void)

{
  uint uVar1;
  
  uVar1 = DAT_febe82a0 - 1;
  if (3 < uVar1) {
    if (uVar1 == 4) {
      DAT_febe8102 = DAT_febe82ae;
      DAT_febe8105 = DAT_febe82ad;
      DAT_febe8106 = DAT_febe82aa;
      DAT_febe8107 = DAT_febe82ab;
      DAT_febe8109 = DAT_febe82ac;
      DAT_febe810a = 1;
      return;
    }
    if (0xd < uVar1) {
      if (uVar1 == 0xe) {
        DAT_febe8102 = DAT_febe82ae;
        DAT_febe8105 = DAT_febe82ad;
        DAT_febe8106 = DAT_febe82aa;
        DAT_febe8107 = DAT_febe82ab;
        DAT_febe8109 = DAT_febe82ac;
        DAT_febe810a = 2;
        return;
      }
      if (uVar1 != 0xf) {
        DAT_febe8102 = DAT_febe82ae;
        DAT_febe8105 = DAT_febe82ad;
        DAT_febe8106 = DAT_febe82aa;
        DAT_febe8107 = DAT_febe82ab;
        DAT_febe8109 = DAT_febe82ac;
        DAT_febe810a = 0;
        return;
      }
    }
  }
  DAT_febe810a = 3;
  DAT_febe8102 = DAT_febe82ae;
  DAT_febe8105 = DAT_febe82ad;
  DAT_febe8106 = DAT_febe82aa;
  DAT_febe8107 = DAT_febe82ab;
  DAT_febe8109 = DAT_febe82ac;
  return;
}

void copy_byte_febee848_to_febe80e3_4c294(void)

{
  DAT_febe80e3 = DAT_febee848;
  return;
}

void fill_constant_block_4c29e(void)

{
  DAT_febe80e4 = 0;
  DAT_febe80e5 = 0;
  DAT_febe80fc = 0;
  DAT_febe80e6 = 0;
  DAT_febe80e7 = 0;
  DAT_febe80e8 = 0;
  DAT_febe80e9 = 0;
  DAT_febe80ea = 0;
  return;
}

void set_bytes_febe80fa_80fb_to_ff_4c2b4(void)

{
  DAT_febe80fa = 0xff;
  DAT_febe80fb = 0xff;
  return;
}

void fill_constant_block_4c2c0(void)

{
  DAT_febe80f3 = 0;
  DAT_febe80eb = 0;
  DAT_febe80ed = 0;
  DAT_febe80ef = 0;
  DAT_febe80f1 = 0;
  return;
}

void clear_word_febe8154_and_set_byte_febe80df_4c2d0(void)

{
  DAT_febe8154 = 0;
  DAT_febe80df = 1;
  return;
}

void fill_constant_block_4c2dc(void)

{
  DAT_febe80ee = 0;
  DAT_febe80f0 = 0;
  DAT_febe80f2 = 0;
  DAT_febe80ec = DAT_febee834;
  DAT_febe80f4 = 0;
  DAT_febe80f6 = DAT_febee82f;
  DAT_febe80f7 = DAT_febee83d;
  DAT_febe80f8 = DAT_febee83b;
  DAT_febe80f9 = DAT_febee83c;
  DAT_febe80e0 = DAT_febee83a;
  DAT_febe8156 = ((int)(int16_t)DAT_febee8bc);
  return;
}

void copy_byte_febee830_to_febe80dc_4c314(void)

{
  DAT_febe80dc = DAT_febee830;
  return;
}

void fill_constant_block_4c31e(void)

{
  DAT_febe8113 = 0;
  DAT_febe8114 = 0;
  DAT_febe8115 = 0;
  DAT_febe8116 = 0;
  DAT_febe8117 = 0;
  return;
}

void clear_febe8170_815c_and_8118_pair_4c32e(void)

{
  DAT_febe8170 = 0;
  DAT_febe815c = 0;
  DAT_febe8118 = 0;
  DAT_febe8119 = 0;
  return;
}

void clear_febe815a_and_three_status_bytes_4c33c(void)

{
  DAT_febe815a = 0;
  DAT_febe811a = 0;
  DAT_febe811b = 0;
  DAT_febe812d = 0;
  return;
}

void fill_constant_block_4c34a(void)

{
  DAT_febe811d = 0;
  DAT_febe811e = 0;
  DAT_febe811f = 0;
  DAT_febe8121 = 0;
  DAT_febe8123 = 0;
  DAT_febe8120 = 0;
  DAT_febe8122 = 0;
  DAT_febe8124 = 0;
  DAT_febe8126 = 0;
  DAT_febe8135 = 0;
  DAT_febe8131 = 0;
  DAT_febe815e = 0;
  DAT_febe8125 = 0;
  DAT_febe8132 = 0;
  DAT_febe8133 = 0;
  DAT_febe811c = 0;
  return;
}

void fill_constant_block_4c370(void)

{
  DAT_febe8160 = 0;
  DAT_febe8127 = 0;
  DAT_febe8128 = 0;
  DAT_febe8129 = 0;
  DAT_febe8134 = 0;
  return;
}

void scale_febe6776_to_two_saturated_signed_words_4c380(void)

{
  int iVar1;
  
  iVar1 = (int)(((int)(int16_t)DAT_febe6776) / 8);
  if (iVar1 + -0x708 < 0 == (iVar1 < 0 && -1 < iVar1 + -0x708)) {
    iVar1 = 0x708;
  }
  if (iVar1 + 0x708 < 0 != (-1 < iVar1 && iVar1 + 0x708 < 0)) {
    iVar1 = -0x708;
  }
  DAT_febe8166 = (short)iVar1;
  iVar1 = (((int)(int16_t)DAT_febe6776) * 0x652e) / 0x2000;
  if (iVar1 + -0x7fff < 0 == (iVar1 < 0 && -1 < iVar1 + -0x7fff)) {
    iVar1 = 0x7fff;
  }
  if (iVar1 + 0x8000 < 0 == (-1 < iVar1 && iVar1 + 0x8000 < 0)) {
    DAT_febe816a = (undefined2)iVar1;
  }
  else {
    DAT_febe816a = 0x8000;
  }
  return;
}

void scale_three_signed_inputs_and_split_fifteenth_remainder_4c3d2(void)

{
  int limit;
  int scale;
  int remainder;
  int quotient;
  int angle;
  char flag;
  
  limit = (int)DAT_febee94c;
  if (limit >= 0x1ffff) {
    limit = 0x1ffff;
  }
  if (limit < -0x20000) {
    limit = -0x20000;
  }
  scale = (int)((long long)(int)DAT_febee948 * 360);
  scale = scale / 16;
  scale = (int)((long long)scale * 10);
  scale = scale / 0x1000;
  if (scale >= 0x77f8) {
    scale = 0x77f8;
  }
  else if (scale < -0x7807) {
    scale = -0x7807;
  }
  remainder = (int)(int8_t)((int)(0x182b8 + scale) % 15);
  if (remainder >= 8) {
    remainder = remainder + -0xf;
  }
  quotient = (scale - remainder) / 15;
  angle = (int)((long long)(int)DAT_febee954 * 36000);
  angle = (int)(int16_t)(angle / 0x10000);
  if (angle >= 0x7ff) {
    angle = 0x7ff;
  }
  else if (angle < -0x800) {
    angle = -0x800;
  }
  flag = DAT_febee888 == 'Z';
  DAT_febe8174 = (uint)limit;
  DAT_febe8178 = (uint)scale;
  DAT_febe8138 = (char)remainder;
  DAT_febe8164 = (undefined2)quotient;
  DAT_febe8168 = (undefined2)quotient;
  DAT_febe816e = (short)angle;
  DAT_febe813d = flag;
  DAT_febe8139 = flag;
  DAT_febe813b = flag;
  return;
}

void assemble_scaled_signed_status_fields_and_change_latch_4c490(void)

{
  char cVar1;
  ushort uVar2;
  char cVar3;
  uint32_t puVar5;
  undefined1 uVar6;
  int iVar7;
  int iVar8;
  undefined1 uStack_11;
  int iVar4;
  
  puVar5 = 0xfebeb800u;
  scale_febe6776_to_two_saturated_signed_words_4c380();
  scale_three_signed_inputs_and_split_fifteenth_remainder_4c3d2();
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x58ad))))) == 'Z') {
    iVar8 = (int)(short)( (int)(((*((short *)camry_host_ptr((uint32_t)(puVar5 + -0x5158)))) * 100)) / (int)0x100);
    if (iVar8 + -1000 < 0 == (iVar8 < 0 && -1 < iVar8 + -1000) && iVar8 != 1000) {
      iVar8 = 1000;
    }
    else if (iVar8 + 1000 < 0 != (-1 < iVar8 && iVar8 + 1000 < 0)) {
      iVar8 = -1000;
    }
  }
  else {
    iVar8 = (int)(*((short *)camry_host_ptr((uint32_t)(puVar5 + -0x36ae))));
  }
  cVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x522d)))));
  store_s16_saturated_to_symmetric_s8_6a5cc((int)(short)(iVar8 / 10),&uStack_11);
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x36ca))))) = uStack_11;
  cVar3 = (char)((iVar8 + 1000) % 10);
  iVar4 = (int)cVar3;
  if (iVar8 < 0) {
    iVar7 = 6;
  }
  else {
    iVar7 = 5;
  }
  if (iVar4 - iVar7 < 0 == (iVar4 < 0 && -1 < iVar4 - iVar7)) {
    iVar4 = (int)(char)(cVar3 + -10);
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x36be))))) = (char)iVar4;
  uVar6 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x37b0)))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x36c6))))) = (char)((iVar8 - iVar4) / 10);
  cVar3 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x36bc)))));
  if (cVar3 == '\0') {
    if (((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x37af))))) == (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x36bb)))))) || (1 < (byte)(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x3898))))))) {
      uVar6 = 1;
    }
    else {
      cVar3 = 'Z';
    }
  }
  uVar2 = (*((ushort *)camry_host_ptr((uint32_t)(0x30d2u + (int)(puVar5 + 6)))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x36bc))))) = cVar3;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x36bb))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x37af)))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x36c2))))) = uVar6;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-13999))))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-14000))))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x36c9))))) = cVar1 != '\0';
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x36c4))))) = cVar1 != '\0';
  (*((short *)camry_host_ptr((uint32_t)(puVar5 + -0x3694)))) =
       (short)( (int)((((int)(-(int)(*((short *)camry_host_ptr((uint32_t)(puVar5 + -0x50e8)))) * (uint)uVar2) / 0x100) * 100)) / (int)0x2000);
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x36c0))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x3719)))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x36bf))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x371a)))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(-0x36c1))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffbc75u + (uint32_t)((int)puVar5) * 1u))));
  return;
}

void run_init_chain_4c590(void)

{
  derive_input_validity_flags_and_scaled_signed_outputs_4c000();
  gate_clamp_and_scale_febe64ec_to_signed_word_4c0e8();
  clear_bytes_febe8103_8104_8108_4c142();
  pack_status_and_scaled_words_into_eight_bytes_4c14e();
  refresh_latched_status_with_override_4c238();
  copy_classifier_fields_and_encode_state_group_4c24a();
  copy_byte_febee848_to_febe80e3_4c294();
  fill_constant_block_4c29e();
  set_bytes_febe80fa_80fb_to_ff_4c2b4();
  fill_constant_block_4c2c0();
  clear_word_febe8154_and_set_byte_febe80df_4c2d0();
  fill_constant_block_4c2dc();
  copy_byte_febee830_to_febe80dc_4c314();
  fill_constant_block_4c31e();
  clear_febe8170_815c_and_8118_pair_4c32e();
  clear_febe815a_and_three_status_bytes_4c33c();
  fill_constant_block_4c34a();
  fill_constant_block_4c370();
  assemble_scaled_signed_status_fields_and_change_latch_4c490();
  return;
}

void set_byte_febe8143_4c5e8(undefined1 param_1)

{
  DAT_febe8143 = param_1;
  return;
}

void return_only_stub_4c5ee(void)

{
  return;
}

void load_febe8190_counter_threshold_4c5f0(void)

{
  DAT_febe8190 = DAT_0002fbfc;
  return;
}

void update_e82a_zero_duration_latch_4c5fe(void)

{
  if (DAT_febee82a == '\0') {
    if (DAT_febe8190 <= DAT_0002fbfc) {
      DAT_febe8190 = DAT_febe8190 + 1;
    }
  }
  else {
    DAT_febe8190 = 0;
  }
  if ((DAT_febee82a == 'Z') || (DAT_febe8190 <= DAT_0002fbfc)) {
    DAT_febe818c = 0x5a;
  }
  else {
    DAT_febe818c = 0;
  }
  return;
}

uint encode_e836_equals_one_as_z_4c63c(void)

{
  DAT_febe8187 = 0;
  if (DAT_febee836 == '\x01') {
    DAT_febe8187 = 0x5a;
  }
  return DAT_febe8187;
}

uint consume_ten_status_flags_and_update_admission_latch_4c650(void)

{
  int iVar1;
  byte bVar2;
  uchar uVar3;
  char cVar4;
  char cVar5;
  char cVar6;
  byte bVar7;
  uint uVar8;
  byte bVar9;
  int iVar10;
  int iVar11;
  uint uVar12;
  
  cVar6 = DAT_febee87e;
  cVar5 = DAT_febee812;
  cVar4 = DAT_febe818c;
  bVar9 = DAT_febe80c9;
  uVar3 = internal_source_admission_state;
  uVar8 = (uint)DAT_febee8cc;
  iVar11 = (int)((int)(int16_t)DAT_febee8dc);
  iVar10 = (int)((int)(int16_t)DAT_febe6790);
  bVar7 = 0;
  uVar12 = 0;
  do {
    bVar2 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe817du + (uint32_t)(uVar12) * 1u))));
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe817du + (uint32_t)(uVar12) * 1u)))) = 0;
    uVar12 = uVar12 + 1;
    bVar7 = bVar7 | bVar2;
  } while (uVar12 < 10);
  if ((((((uVar8 & 0xff00) - 0x100 < 0x201) || (cVar6 == 'Z')) ||
       (iVar1 = iVar11 + -0x569a, ((iVar1 < 0) || (iVar11 < 0)))) ||
      (iVar11 = iVar10 + -0x569a, ((iVar11 < 0) || (iVar10 < 0)))) ||
     (((uVar3 != '\0' && (uVar3 != '\x01')) ||
      ((cVar5 != '\x11' || ((DAT_febe8188 = bVar9 & 1, (bVar9 & 1) != 0 || (bVar7 == 0x5a)))))))) {
    DAT_febe8188 = 0x5a;
  }
  bVar9 = DAT_febe8188;
  if ((DAT_febe818a != 'Z') && (cVar4 != '\0')) {
    bVar9 = 0;
  }
  DAT_febe818a = bVar9;
  return DAT_febe818a;
}

uint encode_low_mask_and_status_conditions_as_z_4c6e6(void)

{
  DAT_febe8189 = DAT_febe80c9 & 2;
  if ((((((DAT_febe80c9 & 2) != 0) || ((DAT_febe6764 & 0x1ff) != 0)) || (DAT_febe82ba != 0)) ||
      ((DAT_febe82c2 != 0 || (DAT_febe82c4 != 0)))) ||
     ((DAT_febee857 == '\"' || ((DAT_febee858 == '\"' || (DAT_febee859 == '\"')))))) {
    DAT_febe8189 = 0x5a;
  }
  return DAT_febe8189;
}

int prioritize_three_status_flags_into_four_state_code_4c738(void)

{
  undefined1 uVar1;
  uint32_t puVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  
  puVar2 = 0xfebeb800u;
  update_e82a_zero_duration_latch_4c5fe();
  iVar3 = encode_e836_equals_one_as_z_4c63c();
  iVar4 = consume_ten_status_flags_and_update_admission_latch_4c650();
  iVar5 = encode_low_mask_and_status_conditions_as_z_4c6e6();
  if (iVar5 == 0x5a) {
    uVar1 = 3;
  }
  else {
    uVar1 = 2;
    if (iVar4 != 0x5a) {
      uVar1 = iVar3 == 0x5a;
    }
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x3684))))) = uVar1;
  return iVar5;
}

void copy_e88c_e88d_to_status_pair_4c772(void)

{
  DAT_febe818d = DAT_febee88c;
  DAT_febe818e = DAT_febee88d;
  return;
}

void refresh_prioritized_status_and_copied_pair_4c784(void)

{
  prioritize_three_status_flags_into_four_state_code_4c738();
  copy_e88c_e88d_to_status_pair_4c772();
  return;
}

void set_monitor_pending_projection(uchar index,uchar status)

{
  if (index < 10) {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe817du + (uint32_t)(index) * 1u)))) = status;
  }
  return;
}

void return_only_stub_4c7a6(void)

{
  return;
}

void return_only_stub_4c7a8(void)

{
  return;
}

void pack_eight_status_bytes_for_channel3_4c7aa(void)

{
  char cVar1;
  uint32_t puVar2;
  uint uVar3;
  
  puVar2 = 0xfebeb800u;
  DAT_febe8c53 = DAT_febe810b;
  DAT_febe8c54 = DAT_febe810c;
  DAT_febe8c55 = DAT_febe810d;
  DAT_febe8c56 = DAT_febe810e;
  DAT_febe8c57 = DAT_febe810f;
  DAT_febe8c58 = DAT_febe8110;
  DAT_febe8c59 = DAT_febe8111;
  DAT_febe8c5a = DAT_febe8112;
  insert_com_big_endian_signal_without_trigger_7d31e(0x2c,0x27,8,0,((undefined *)camry_host_ptr(0xfebe8c53u)));
  insert_com_big_endian_signal_without_trigger_7d31e(0x2d, 0x28, 8, 0, ((undefined *)camry_host_ptr((uint32_t)(puVar2 + -0x2bac))));
  insert_com_big_endian_signal_without_trigger_7d31e(0x2e, 0x29, 8, 0, ((undefined *)camry_host_ptr((uint32_t)(puVar2 + -0x2bab))));
  insert_com_big_endian_signal_without_trigger_7d31e(0x2f, 0x2a, 8, 0, ((undefined *)camry_host_ptr((uint32_t)(puVar2 + -0x2baa))));
  insert_com_big_endian_signal_without_trigger_7d31e(0x30, 0x2b, 8, 0, ((undefined *)camry_host_ptr((uint32_t)(puVar2 + -0x2ba9))));
  insert_com_big_endian_signal_without_trigger_7d31e(0x31, 0x2c, 8, 0, ((undefined *)camry_host_ptr((uint32_t)(puVar2 + -0x2ba8))));
  insert_com_big_endian_signal_without_trigger_7d31e(0x32, 0x2d, 8, 0, ((undefined *)camry_host_ptr((uint32_t)(puVar2 + -0x2ba7))));
  insert_com_big_endian_signal_without_trigger_7d31e(0x33, 0x2e, 8, 0, ((undefined *)camry_host_ptr((uint32_t)(puVar2 + -0x2ba6))));
  cVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x386a)))));
  uVar3 = get_com_pdu_status_with_group_enable_bit_7d0ea(3);
  if ((cVar1 == 'Z') && ((uVar3 >> 4 & 1) == 0)) {
    set_tx_inhibit_pair_and_flag_7e612(3);
  }
  else if ((cVar1 == '\0') && ((uVar3 >> 4 & 1) != 0)) {
    clear_tx_pending_bit_by_mode_7e46a(3,0x40);
    clear_tx_inhibit_pair_and_flag_7e696(3);
  }
  return;
}

void return_only_stub_4c8dc(void)

{
  return;
}

void return_only_stub_4c8de(void)

{
  return;
}

void pack_constant_fields_for_channel4_4c8e0(void)

{
  char cVar1;
  uint32_t puVar2;
  uint uVar3;
  
  puVar2 = 0xfebeb800u;
  DAT_febe8c5d = 9;
  DAT_febe8c5e = 0;
  DAT_febe8c30 = 0;
  insert_com_big_endian_signal_without_trigger_7d31e(0x34,0x2f,8,0,((undefined *)camry_host_ptr(0xfebe8c5du)));
  insert_com_big_endian_signal_without_trigger_7d31e(0x35, 0x30, 1, 7, ((undefined *)camry_host_ptr((uint32_t)(puVar2 + -0x2ba2))));
  insert_com_big_endian_signal_without_trigger_7d31e(0x36, 0x31, 0x10, 0, ((undefined *)camry_host_ptr((uint32_t)(puVar2 + -0x2bd0))));
  cVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x386a)))));
  uVar3 = get_com_pdu_status_with_group_enable_bit_7d0ea(4);
  if ((cVar1 == 'Z') && ((uVar3 >> 4 & 1) == 0)) {
    set_tx_inhibit_pair_and_flag_7e612(4);
  }
  else if ((cVar1 == '\0') && ((uVar3 >> 4 & 1) != 0)) {
    clear_tx_pending_bit_by_mode_7e46a(4,0x40);
    clear_tx_inhibit_pair_and_flag_7e696(4);
  }
  return;
}

void return_only_stub_4c976(void)

{
  return;
}

void return_only_stub_4c978(void)

{
  return;
}

void pack_channel0_status_fields_and_additive_checksum_4c97a(void)

{
  uint uVar1;
  char *pcVar2;
  uint uVar3;
  uint32_t puVar4;
  char cVar5;
  char acStack_28 [32];
  
  puVar4 = 0xfebeb800u;
  DAT_febe8c4c = 0;
  DAT_febe8c32 = ((int)(int8_t)DAT_febe8136);
  DAT_febe8c33 = DAT_febe8137;
  DAT_febe8c24 = ((int)(int16_t)DAT_febe8164);
  DAT_febe8c34 = ((int)(int8_t)DAT_febe8138);
  DAT_febe8c26 = ((int)(int16_t)DAT_febe8166);
  DAT_febe8c49 = DAT_febe8139;
  DAT_febe8c35 = DAT_febe80de;
  DAT_febe8c36 = DAT_febe80e3;
  DAT_febe8c37 = DAT_febe80e2;
  DAT_febe8c38 = ((int)(int8_t)DAT_febe813a);
  DAT_febe8c28 = ((int)(int16_t)DAT_febe8168);
  DAT_febe8c39 = DAT_febe813b;
  DAT_febe8c20 = DAT_febe8174;
  DAT_febe8c3a = DAT_febe813c;
  DAT_febe8c3b = DAT_febe813d;
  DAT_febe8c3c = DAT_febe813e;
  DAT_febe8c3d = DAT_febe813f;
  DAT_febe8c3e = DAT_febe817c;
  DAT_febe8c2a = ((int)(int16_t)DAT_febe816a);
  DAT_febe8c3f = DAT_febe80f6;
  DAT_febe8c40 = DAT_febe80f7;
  DAT_febe8c41 = DAT_febe80f8;
  DAT_febe8c42 = DAT_febe80f9;
  DAT_febe8c43 = DAT_febe80ec;
  DAT_febe8c44 = DAT_febe8140;
  DAT_febe8c45 = DAT_febe8141;
  DAT_febe8c4a = DAT_febe818e;
  DAT_febe8c4b = DAT_febe818d;
  DAT_febe8c46 = ((int)(int8_t)DAT_febe8142);
  DAT_febe8c47 = DAT_febe80e0;
  DAT_febe8c2c = ((int)(int16_t)DAT_febe8156);
  DAT_febe8c2e = ((int)(int16_t)DAT_febe816c);
  DAT_febe8c4d = DAT_febe8150;
  DAT_febe8c4e = DAT_febe8151;
  insert_com_big_endian_signal_without_trigger_7d31e(0,0,8,0,((undefined *)camry_host_ptr(0xfebe8c32u)));
  insert_com_big_endian_signal_without_trigger_7d31e(1, 2, 1, 1, ((undefined *)camry_host_ptr((uint32_t)(puVar4 + -0x2bb4))));
  insert_com_big_endian_signal_without_trigger_7d31e(2, 2, 1, 0, ((undefined *)camry_host_ptr((uint32_t)(puVar4 + -0x2bcd))));
  insert_com_big_endian_signal_without_trigger_7d31e(3, 3, 0xc, 4, ((undefined *)camry_host_ptr((uint32_t)(puVar4 + -0x2bdc))));
  insert_com_big_endian_signal_without_trigger_7d31e(4, 4, 4, 0, ((undefined *)camry_host_ptr((uint32_t)(puVar4 + -0x2bcc))));
  insert_com_big_endian_signal_without_trigger_7d31e(5, 5, 0xc, 4, ((undefined *)camry_host_ptr((uint32_t)(puVar4 + -0x2bda))));
  insert_com_big_endian_signal_without_trigger_7d31e(6, 6, 1, 3, ((undefined *)camry_host_ptr((uint32_t)(puVar4 + -0x2bb7))));
  insert_com_big_endian_signal_without_trigger_7d31e(7, 6, 1, 2, ((undefined *)camry_host_ptr((uint32_t)(puVar4 + -0x2bcb))));
  insert_com_big_endian_signal_without_trigger_7d31e(8, 6, 1, 1, ((undefined *)camry_host_ptr((uint32_t)(puVar4 + -0x2bca))));
  insert_com_big_endian_signal_without_trigger_7d31e(9, 6, 1, 0, ((undefined *)camry_host_ptr((uint32_t)(puVar4 + -0x2bc9))));
  insert_com_big_endian_signal_without_trigger_7d31e(0xb, 8, 8, 0, ((undefined *)camry_host_ptr((uint32_t)(puVar4 + -0x2bc8))));
  insert_com_big_endian_signal_without_trigger_7d31e(0xc, 9, 0xc, 4, ((undefined *)camry_host_ptr((uint32_t)(puVar4 + -0x2bd8))));
  insert_com_big_endian_signal_without_trigger_7d31e(0xd, 10, 1, 3, ((undefined *)camry_host_ptr((uint32_t)(puVar4 + -0x2bc7))));
  insert_com_big_endian_signal_without_trigger_7d31e(0xe, 0xb, 0x12, 6, ((undefined *)camry_host_ptr((uint32_t)(puVar4 + -0x2be0))));
  insert_com_big_endian_signal_without_trigger_7d31e(0xf, 0xd, 1, 5, ((undefined *)camry_host_ptr((uint32_t)(puVar4 + -0x2bc6))));
  insert_com_big_endian_signal_without_trigger_7d31e(0x10, 0xd, 1, 4, ((undefined *)camry_host_ptr((uint32_t)(puVar4 + -0x2bc5))));
  insert_com_big_endian_signal_without_trigger_7d31e(0x11, 0xd, 1, 3, ((undefined *)camry_host_ptr((uint32_t)(puVar4 + -0x2bc4))));
  insert_com_big_endian_signal_without_trigger_7d31e(0x12, 0xd, 1, 2, ((undefined *)camry_host_ptr((uint32_t)(puVar4 + -0x2bc3))));
  insert_com_big_endian_signal_without_trigger_7d31e(0x13, 0xd, 2, 0, ((undefined *)camry_host_ptr((uint32_t)(puVar4 + -0x2bc2))));
  insert_com_big_endian_signal_without_trigger_7d31e(0x14, 0xe, 0x10, 0, ((undefined *)camry_host_ptr((uint32_t)(puVar4 + -0x2bd6))));
  insert_com_big_endian_signal_without_trigger_7d31e(0x15, 0x10, 1, 5, ((undefined *)camry_host_ptr((uint32_t)(puVar4 + -0x2bc1))));
  insert_com_big_endian_signal_without_trigger_7d31e(0x16, 0x10, 1, 4, ((undefined *)camry_host_ptr((uint32_t)(puVar4 + -0x2bc0))));
  insert_com_big_endian_signal_without_trigger_7d31e(0x17, 0x10, 1, 3, ((undefined *)camry_host_ptr((uint32_t)(puVar4 + -0x2bbf))));
  insert_com_big_endian_signal_without_trigger_7d31e(0x18, 0x10, 2, 1, ((undefined *)camry_host_ptr((uint32_t)(puVar4 + -0x2bbe))));
  insert_com_big_endian_signal_without_trigger_7d31e(0x19, 0x10, 1, 0, ((undefined *)camry_host_ptr((uint32_t)(puVar4 + -0x2bbd))));
  insert_com_big_endian_signal_without_trigger_7d31e(0x1a, 0x11, 1, 7, ((undefined *)camry_host_ptr((uint32_t)(puVar4 + -0x2bbc))));
  insert_com_big_endian_signal_without_trigger_7d31e(0x1b, 0x11, 1, 6, ((undefined *)camry_host_ptr((uint32_t)(puVar4 + -0x2bbb))));
  insert_com_big_endian_signal_without_trigger_7d31e(0x1c, 0x11, 1, 5, ((undefined *)camry_host_ptr((uint32_t)(puVar4 + -0x2bb6))));
  insert_com_big_endian_signal_without_trigger_7d31e(0x1d, 0x11, 1, 4, ((undefined *)camry_host_ptr((uint32_t)(puVar4 + -0x2bb5))));
  insert_com_big_endian_signal_without_trigger_7d31e(0x1e, 0x11, 4, 0, ((undefined *)camry_host_ptr((uint32_t)(puVar4 + -0x2bba))));
  insert_com_big_endian_signal_without_trigger_7d31e(0x1f, 0x13, 1, 0, ((undefined *)camry_host_ptr((uint32_t)(puVar4 + -0x2bb9))));
  insert_com_big_endian_signal_without_trigger_7d31e(0x20, 0x14, 0x10, 0, ((undefined *)camry_host_ptr((uint32_t)(puVar4 + -0x2bd4))));
  insert_com_big_endian_signal_without_trigger_7d31e(0x21, 0x16, 0x10, 0, ((undefined *)camry_host_ptr((uint32_t)(puVar4 + -0x2bd2))));
  insert_com_big_endian_signal_without_trigger_7d31e(0x22, 0x1b, 1, 1, ((undefined *)camry_host_ptr((uint32_t)(puVar4 + -0x2bb3))));
  insert_com_big_endian_signal_without_trigger_7d31e(0x23, 0x1b, 1, 0, ((undefined *)camry_host_ptr((uint32_t)(puVar4 + -0x2bb2))));
  cVar5 = '\0';
  uVar3 = 0;
  do {
    uVar1 = uVar3 + 1;
    acStack_28[uVar3] = '\0';
    uVar3 = uVar1;
  } while (uVar1 < 0x20);
  copy_com_pdu_buffer_and_return_availability_7d05c(0, camry_host_addr(acStack_28));
  uVar3 = 0;
  do {
    pcVar2 = acStack_28 + uVar3;
    uVar3 = uVar3 + 1;
    cVar5 = cVar5 + *pcVar2;
  } while (uVar3 < 7);
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x2bb8))))) = cVar5 + '8';
  insert_com_big_endian_signal_without_trigger_7d31e(10, 7, 8, 0, ((undefined *)camry_host_ptr((uint32_t)(puVar4 + -0x2bb8))));
  cVar5 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x386a)))));
  uVar3 = get_com_pdu_status_with_group_enable_bit_7d0ea(0);
  if ((cVar5 == 'Z') && ((uVar3 & 0x10) == 0)) {
    set_tx_inhibit_pair_and_flag_7e612(0);
  }
  else if ((cVar5 == '\0') && ((uVar3 >> 4 & 1) != 0)) {
    clear_tx_pending_bit_by_mode_7e46a(0,0x40);
    clear_tx_inhibit_pair_and_flag_7e696(0);
  }
  return;
}

void return_only_stub_4ce04(void)

{
  return;
}

void return_only_stub_4ce06(void)

{
  return;
}

void pack_four_change_sensitive_fields_for_channel2_4ce08(void)

{
  char cVar1;
  uint32_t puVar2;
  uint uVar3;
  
  puVar2 = 0xfebeb800u;
  DAT_febe8c4f = DAT_febe8105;
  DAT_febe8c50 = DAT_febe8106;
  DAT_febe8c51 = DAT_febe8107;
  DAT_febe8c52 = DAT_febe8109;
  insert_com_big_endian_signal_and_apply_trigger_policy_7d1dc(0x28,0x25,2,6,((undefined *)camry_host_ptr(0xfebe8c4fu)));
  insert_com_big_endian_signal_and_apply_trigger_policy_7d1dc(0x29, 0x25, 3, 3, ((undefined *)camry_host_ptr((uint32_t)(puVar2 + -0x2bb0))));
  insert_com_big_endian_signal_and_apply_trigger_policy_7d1dc(0x2a, 0x26, 3, 1, ((undefined *)camry_host_ptr((uint32_t)(puVar2 + -0x2baf))));
  insert_com_big_endian_signal_and_apply_trigger_policy_7d1dc(0x2b, 0x26, 1, 0, ((undefined *)camry_host_ptr((uint32_t)(puVar2 + -0x2bae))));
  cVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x386a)))));
  uVar3 = get_com_pdu_status_with_group_enable_bit_7d0ea(2);
  if ((cVar1 == 'Z') && ((uVar3 >> 4 & 1) == 0)) {
    set_tx_inhibit_pair_and_flag_7e612(2);
  }
  else if ((cVar1 == '\0') && ((uVar3 >> 4 & 1) != 0)) {
    clear_tx_pending_bit_by_mode_7e46a(2,0x40);
    clear_tx_pending_bit_by_mode_7e46a(2,0x80);
    clear_tx_inhibit_pair_and_flag_7e696(2);
  }
  return;
}

void return_only_stub_4cecc(void)

{
  return;
}

void return_only_stub_4cece(void)

{
  return;
}

void pack_status_and_override_bit_for_channel1_4ced0(void)

{
  char cVar1;
  uint32_t puVar2;
  uint uVar3;
  
  puVar2 = 0xfebeb800u;
  DAT_febe8c5b = DAT_febe8100;
  DAT_febe8c5c = DAT_febe8101;
  insert_com_big_endian_signal_and_apply_trigger_policy_7d1dc(0x26,0x22,3,5,((undefined *)camry_host_ptr(0xfebe8c5bu)));
  insert_com_big_endian_signal_and_apply_trigger_policy_7d1dc(0x27, 0x22, 1, 4, ((undefined *)camry_host_ptr((uint32_t)(puVar2 + -0x2ba4))));
  cVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x386a)))));
  uVar3 = get_com_pdu_status_with_group_enable_bit_7d0ea(1);
  if ((cVar1 == 'Z') && ((uVar3 >> 4 & 1) == 0)) {
    set_tx_inhibit_pair_and_flag_7e612(1);
  }
  else if ((cVar1 == '\0') && ((uVar3 >> 4 & 1) != 0)) {
    clear_tx_pending_bit_by_mode_7e46a(1,0x40);
    clear_tx_pending_bit_by_mode_7e46a(1,0x80);
    clear_tx_inhibit_pair_and_flag_7e696(1);
  }
  return;
}

void thunk_clear_word_febe81c8_4d4bc(void)

{
  clear_word_febe81c8_4d4bc();
  return;
}

void return_only_stub_4cf64(void)

{
  return;
}

undefined4 return_const_5a_4cf66(void)

{
  return 0x5a;
}

void reset_diagnostic_requests_iteration_and_pending_state_4cf6c(void)

{
  uint uVar1;
  
  uVar1 = 0;
  DAT_febe81b2 = 0;
  DAT_febe8194 = 0;
  DAT_febe8195 = 0;
  DAT_febe81c0 = 0;
  diagnostic_normal_tx_policy_request = '\0';
  dtc_setting_inhibit_request = '\0';
  dtc_requested_status_mask = '\0';
  dtc_iteration_result_count = 0;
  dtc_iteration_catalogue_cursor = 0;
  snapshot_identifier_cached_dtc = 0;
  DAT_febe8199 = 0;
  DAT_febe819a = 0;
  DAT_febe81b8 = 0;
  DAT_febe81ad = 0;
  DAT_febe81ba = 0;
  DAT_febe81bc = 0;
  app_programming_mode_request_latched = '\0';
  DAT_febe81af = 0;
  do {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe819bu + (uint32_t)(uVar1) * 1u)))) = 0;
    uVar1 = uVar1 + 1;
  } while (uVar1 < 0x10);
  return;
}

void refresh_mode_diagnostic_admission(void)

{
  char cVar1;
  char cVar2;
  char cVar3;
  char cVar4;
  undefined1 uVar5;
  uint32_t puVar6;
  int iVar7;
  uint uVar8;
  
  cVar4 = DAT_febee826;
  cVar3 = DAT_febe81b0;
  cVar2 = DAT_febe81ab;
  cVar1 = DAT_febe7f97;
  puVar6 = 0xfebeb800u;
  uVar8 = (uint)DAT_febee8cc;
  iVar7 = return_const_5a_4cf66();
  if ((((cVar4 == '\x11') || (cVar4 == '\"')) || (uVar8 < 0x104)) ||
     ((iVar7 != 0x5a && ((iVar7 != 0xa5 || (2 < uVar8 - 0x700)))))) {
    uVar5 = 0;
  }
  else {
    uVar5 = 0x5a;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(-0x3654))))) = uVar5;
  if (((cVar4 == '\"') || ((cVar4 == '\0' && (cVar2 == '3')))) ||
     ((cVar1 == '\0' && (cVar3 == 'Z')))) {
    call_98898_with_zero_byte_8b120();
    restore_default_dcm_session_when_not_busy_91b50();
    set_matching_dcm_communication_mode_two_917a4(0);
    run_init_chain_8e62a();
    thunk_set_byte_febeaf47_b9320(0x88);
    reset_diagnostic_requests_iteration_and_pending_state_4cf6c();
    clear_word_febe81c8_4d4bc();
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(-0x3655))))) = cVar4;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(-0x3650))))) = cVar1;
  return;
}
