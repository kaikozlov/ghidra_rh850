#include "common.h"

undefined4 rdbi_1ca9_callback(undefined4 param_1)

{
  short sStack_a;
  
  sStack_a = (short)((((int)(int16_t)DAT_febe6f00) * 100) / 0x80);
  store_s16_max_third_min_first_two_70110((int)sStack_a,25000,0,&sStack_a);
  store_low_u16_big_endian_bytes_6a574(sStack_a, ((undefined1 *)camry_host_ptr((uint32_t)(param_1))));
  return 0;
}

undefined4 rdbi_1caa_callback(undefined4 param_1)

{
  short sStack_a;
  
  sStack_a = (short)((((int)(int16_t)DAT_febe6f02) * 100) / 0x80);
  store_s16_max_third_min_first_two_70110((int)sStack_a,25000,0,&sStack_a);
  store_low_u16_big_endian_bytes_6a574(sStack_a, ((undefined1 *)camry_host_ptr((uint32_t)(param_1))));
  return 0;
}

undefined4 rdbi_1cab_callback(undefined4 param_1,undefined2 param_2)

{
  serialize_eight_dtc_history_code_status_pairs_52972(param_1,param_2);
  return 0;
}

void serialize_retained_control_profile(uchar *output,F33RetainedControlProfile *profile)

{
  short sVar1;
  short sVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  int iVar6;
  int iVar7;
  int iVar8;
  int iVar9;
  int iVar10;
  int iVar11;
  int iVar12;
  int iVar13;
  uint uVar14;
  ushort uVar15;
  ushort uVar16;
  ushort uVar17;
  ushort uVar18;
  byte bVar19;
  short sStack_34;
  
  iVar3 = (int)profile->capture_value;
  if (iVar3 + -0x7fff < 0 == (iVar3 < 0 && -1 < iVar3 + -0x7fff)) {
    iVar3 = 0x7fff;
  }
  iVar4 = (int)profile->received_composite;
  if (iVar4 + -0x7fff < 0 == (iVar4 < 0 && -1 < iVar4 + -0x7fff)) {
    iVar4 = 0x7fff;
  }
  uVar18 = profile->integrated_source;
  if (0xfffe < uVar18) {
    uVar18 = 0xffff;
  }
  uVar17 = profile->elapsed_groups;
  if (0xfffe < uVar17) {
    uVar17 = 0xffff;
  }
  iVar5 = profile->scaled_f228;
  if (iVar5 + -0x7fff < 0 == (iVar5 < 0 && -1 < iVar5 + -0x7fff)) {
    iVar5 = 0x7fff;
  }
  if (iVar5 + 0x8000 < 0 != (-1 < iVar5 && iVar5 + 0x8000 < 0)) {
    iVar5 = -0x8000;
  }
  uVar16 = profile->source_u16_max;
  if (0xfffe < uVar16) {
    uVar16 = 0xffff;
  }
  uVar15 = profile->source_u16_mean;
  if (0xfffe < uVar15) {
    uVar15 = 0xffff;
  }
  iVar6 = (int)profile->f1c6_max;
  if (iVar6 + -0x1ff < 0 == (iVar6 < 0 && -1 < iVar6 + -0x1ff)) {
    iVar6 = 0x1ff;
  }
  if (iVar6 + 0x200 < 0 != (-1 < iVar6 && iVar6 + 0x200 < 0)) {
    iVar6 = -0x200;
  }
  iVar7 = (int)profile->f1c6_mean;
  if (iVar7 + -0x1ff < 0 == (iVar7 < 0 && -1 < iVar7 + -0x1ff)) {
    iVar7 = 0x1ff;
  }
  if (iVar7 + 0x200 < 0 != (-1 < iVar7 && iVar7 + 0x200 < 0)) {
    iVar7 = -0x200;
  }
  iVar8 = (int)profile->f1c8_max;
  if (iVar8 + -0x1ff < 0 == (iVar8 < 0 && -1 < iVar8 + -0x1ff)) {
    iVar8 = 0x1ff;
  }
  if (iVar8 + 0x200 < 0 != (-1 < iVar8 && iVar8 + 0x200 < 0)) {
    iVar8 = -0x200;
  }
  iVar9 = (int)profile->f1c8_mean;
  if (iVar9 + -0x1ff < 0 == (iVar9 < 0 && -1 < iVar9 + -0x1ff)) {
    iVar9 = 0x1ff;
  }
  if (iVar9 + 0x200 < 0 != (-1 < iVar9 && iVar9 + 0x200 < 0)) {
    iVar9 = -0x200;
  }
  iVar10 = (int)profile->f1ca_max;
  if (iVar10 + -0x12d4 < 0 == (iVar10 < 0 && -1 < iVar10 + -0x12d4)) {
    iVar10 = 0x12d4;
  }
  if (iVar10 + 0x12d4 < 0 != (-1 < iVar10 && iVar10 + 0x12d4 < 0)) {
    iVar10 = -0x12d4;
  }
  iVar11 = (int)profile->f1ca_mean;
  if (iVar11 + -0x12d4 < 0 == (iVar11 < 0 && -1 < iVar11 + -0x12d4)) {
    iVar11 = 0x12d4;
  }
  if (iVar11 + 0x12d4 < 0 != (-1 < iVar11 && iVar11 + 0x12d4 < 0)) {
    iVar11 = -0x12d4;
  }
  sVar1 = profile->scaled_ae5c_max;
  iVar12 = sVar1 + -0x7fff;
  if (iVar12 < 0 == (sVar1 < 0 && -1 < iVar12)) {
    sVar1 = 0x7fff;
  }
  sVar2 = profile->scaled_ae5c_min;
  iVar12 = sVar2 + -0x7fff;
  if (iVar12 < 0 == (sVar2 < 0 && -1 < iVar12)) {
    sVar2 = 0x7fff;
  }
  iVar12 = (int)profile->scaled_b054_max;
  if (iVar12 + -25000 < 0 == (iVar12 < 0 && -1 < iVar12 + -25000)) {
    iVar12 = 25000;
  }
  if (iVar12 + 25000 < 0 != (-1 < iVar12 && iVar12 + 25000 < 0)) {
    iVar12 = -25000;
  }
  iVar13 = (int)profile->scaled_b054_mean;
  if (iVar13 + -25000 < 0 == (iVar13 < 0 && -1 < iVar13 + -25000)) {
    iVar13 = 25000;
  }
  if (iVar13 + 25000 < 0 != (-1 < iVar13 && iVar13 + 25000 < 0)) {
    iVar13 = -25000;
  }
  uVar14 = profile->route31_scalar;
  bVar19 = profile->scalar_kind;
  if (uVar14 == 0xffffffff) {
    uVar14 = 0xffffffff;
  }
  if (2 < bVar19) {
    bVar19 = 3;
  }
  store_low_u16_big_endian_bytes_6a5ac(iVar3,output);
  store_low_u16_big_endian_bytes_6a5ac(iVar4,output + 2);
  store_low_u16_big_endian_bytes_6a574(uVar18,output + 4);
  store_low_u16_big_endian_bytes_6a574(uVar17,output + 6);
  sStack_34 = (short)iVar5;
  store_low_u16_big_endian_bytes_6a5ac((int)sStack_34,output + 8);
  store_low_u16_big_endian_bytes_6a574(uVar16,output + 10);
  store_low_u16_big_endian_bytes_6a574(uVar15,output + 0xc);
  store_low_u16_big_endian_bytes_6a5ac((int)(short)iVar6,output + 0xe);
  store_low_u16_big_endian_bytes_6a5ac((int)(short)iVar7,output + 0x10);
  store_low_u16_big_endian_bytes_6a5ac((int)(short)iVar8,output + 0x12);
  store_low_u16_big_endian_bytes_6a5ac((int)(short)iVar9,output + 0x14);
  store_low_u16_big_endian_bytes_6a5ac((int)(short)iVar10,output + 0x16);
  store_low_u16_big_endian_bytes_6a5ac((int)(short)iVar11,output + 0x18);
  store_low_u16_big_endian_bytes_6a5ac((int)sVar1,output + 0x1a);
  store_low_u16_big_endian_bytes_6a5ac((int)sVar2,output + 0x1c);
  store_low_u16_big_endian_bytes_6a5ac(iVar12,output + 0x1e);
  store_low_u16_big_endian_bytes_6a5ac(iVar13,output + 0x20);
  store_u32_big_endian_bytes_6a55c(uVar14,output + 0x22);
  output[0x26] = bVar19;
  output[0x27] = profile->packed_metadata[0];
  output[0x28] = profile->packed_metadata[1];
  output[0x29] = profile->packed_metadata[2];
  output[0x2a] = profile->packed_metadata[3];
  output[0x2b] = profile->packed_metadata[4];
  output[0x2c] = profile->packed_metadata[5];
  return;
}

void read_first_control_profile(uchar *output,uchar slot)

{
  uint32_t puVar1;
  F33RetainedControlProfile FStack_3c;
  
  puVar1 = 0xfebeb800u;
  gather_first_control_profile(&FStack_3c,slot);
  if (FStack_3c.current_elapsed_source_validity != 'Z') {
    FStack_3c.integrated_source = 0;
    FStack_3c.elapsed_groups = 0;
  }
  if (FStack_3c.current_first_profile_validity != 'Z') {
    FStack_3c.scaled_b054_mean = 0;
    FStack_3c.scaled_b054_max = 0;
    FStack_3c.scaled_ae5c_min = 0;
    FStack_3c.scaled_ae5c_max = 0;
    FStack_3c.f1ca_mean = 0;
    FStack_3c.f1ca_max = 0;
    FStack_3c.f1c8_mean = 0;
    FStack_3c.f1c8_max = 0;
    FStack_3c.f1c6_mean = 0;
    FStack_3c.f1c6_max = 0;
    FStack_3c.source_u16_mean = 0;
    FStack_3c.source_u16_max = 0;
    FStack_3c.capture_value = 0x7fff;
  }
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x3013))))) != 'Z') {
    FStack_3c.packed_metadata[0] = 0xff;
    FStack_3c.packed_metadata[1] = 0xff;
    FStack_3c.packed_metadata[2] = 0xff;
    FStack_3c.packed_metadata[3] = 0xff;
    FStack_3c.packed_metadata[4] = 0xff;
    FStack_3c.packed_metadata[5] = 0xff;
  }
  serialize_retained_control_profile(output,&FStack_3c);
  return;
}

uint rdbi_1cf4_callback(uchar *output,ushort length)

{
  read_first_control_profile(output,'\0');
  return 0;
}

uint rdbi_1cf5_callback(uchar *output,ushort length)

{
  read_first_control_profile(output,'\x01');
  return 0;
}

uint rdbi_1cf6_callback(uchar *output,ushort length)

{
  read_first_control_profile(output,'\x02');
  return 0;
}

uint rdbi_1cf7_callback(uchar *output,ushort length)

{
  read_first_control_profile(output,'\x03');
  return 0;
}

uint rdbi_1cf8_callback(uchar *output,ushort length)

{
  read_first_control_profile(output,'\x04');
  return 0;
}

void read_first_ranked_control_profile(uchar *output,uchar slot)

{
  uint32_t puVar1;
  F33RetainedControlProfile FStack_3c;
  
  puVar1 = 0xfebeb800u;
  gather_first_ranked_control_profile(&FStack_3c,slot);
  if (FStack_3c.current_elapsed_source_validity != 'Z') {
    FStack_3c.integrated_source = 0;
    FStack_3c.elapsed_groups = 0;
  }
  if (FStack_3c.current_first_profile_validity != 'Z') {
    FStack_3c.scaled_b054_mean = 0;
    FStack_3c.scaled_b054_max = 0;
    FStack_3c.scaled_ae5c_min = 0;
    FStack_3c.scaled_ae5c_max = 0;
    FStack_3c.f1ca_mean = 0;
    FStack_3c.f1ca_max = 0;
    FStack_3c.f1c8_mean = 0;
    FStack_3c.f1c8_max = 0;
    FStack_3c.f1c6_mean = 0;
    FStack_3c.f1c6_max = 0;
    FStack_3c.source_u16_mean = 0;
    FStack_3c.source_u16_max = 0;
    FStack_3c.capture_value = 0x7fff;
  }
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x3013))))) != 'Z') {
    FStack_3c.packed_metadata[0] = 0xff;
    FStack_3c.packed_metadata[1] = 0xff;
    FStack_3c.packed_metadata[2] = 0xff;
    FStack_3c.packed_metadata[3] = 0xff;
    FStack_3c.packed_metadata[4] = 0xff;
    FStack_3c.packed_metadata[5] = 0xff;
  }
  serialize_retained_control_profile(output,&FStack_3c);
  return;
}

uint rdbi_1cf9_callback(uchar *output,ushort length)

{
  read_first_ranked_control_profile(output,'\0');
  return 0;
}

void read_second_ranked_control_profile(uchar *output,uchar slot)

{
  uint32_t puVar1;
  F33RetainedControlProfile FStack_3c;
  
  puVar1 = 0xfebeb800u;
  gather_second_ranked_control_profile(&FStack_3c,slot);
  if (FStack_3c.current_elapsed_source_validity != 'Z') {
    FStack_3c.integrated_source = 0;
    FStack_3c.elapsed_groups = 0;
  }
  if (FStack_3c.current_first_profile_validity != 'Z') {
    FStack_3c.scaled_b054_mean = 0;
    FStack_3c.scaled_b054_max = 0;
    FStack_3c.scaled_ae5c_min = 0;
    FStack_3c.scaled_ae5c_max = 0;
    FStack_3c.f1ca_mean = 0;
    FStack_3c.f1ca_max = 0;
    FStack_3c.f1c8_mean = 0;
    FStack_3c.f1c8_max = 0;
    FStack_3c.f1c6_mean = 0;
    FStack_3c.f1c6_max = 0;
    FStack_3c.source_u16_mean = 0;
    FStack_3c.source_u16_max = 0;
    FStack_3c.capture_value = 0x7fff;
  }
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x3013))))) != 'Z') {
    FStack_3c.packed_metadata[0] = 0xff;
    FStack_3c.packed_metadata[1] = 0xff;
    FStack_3c.packed_metadata[2] = 0xff;
    FStack_3c.packed_metadata[3] = 0xff;
    FStack_3c.packed_metadata[4] = 0xff;
    FStack_3c.packed_metadata[5] = 0xff;
  }
  serialize_retained_control_profile(output,&FStack_3c);
  return;
}

uint rdbi_1cfa_callback(uchar *output,ushort length)

{
  read_second_ranked_control_profile(output,'\0');
  return 0;
}

uint rdbi_1cfb_callback(uchar *output,ushort length)

{
  read_first_ranked_control_profile(output,'\x01');
  return 0;
}

uint rdbi_1cfc_callback(uchar *output,ushort length)

{
  read_second_ranked_control_profile(output,'\x01');
  return 0;
}

uint rdbi_1cfd_callback(uchar *output,ushort length)

{
  read_first_ranked_control_profile(output,'\x02');
  return 0;
}

uint rdbi_1cfe_callback(uchar *output,ushort length)

{
  read_second_ranked_control_profile(output,'\x02');
  return 0;
}

uint rdbi_1cff_callback(uchar *output,ushort length)

{
  read_first_ranked_control_profile(output,'\x03');
  return 0;
}

uint rdbi_1d01_callback(uchar *output,ushort length)

{
  read_second_ranked_control_profile(output,'\x03');
  return 0;
}

uint rdbi_1d02_callback(uchar *output,ushort length)

{
  read_first_ranked_control_profile(output,'\x04');
  return 0;
}

uint rdbi_1d03_callback(uchar *output,ushort length)

{
  read_second_ranked_control_profile(output,'\x04');
  return 0;
}

undefined4 rdbi_1f01_callback(char *param_1)

{
  *param_1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x20800u + (uint32_t)(0x10) * 1u))));
  param_1[1] = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x20800u + (uint32_t)(0x11) * 1u))));
  param_1[2] = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x20800u + (uint32_t)(0x12) * 1u))));
  param_1[3] = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x20800u + (uint32_t)(0x13) * 1u))));
  param_1[4] = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x20800u + (uint32_t)(0x14) * 1u))));
  param_1[5] = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x20800u + (uint32_t)(0x15) * 1u))));
  param_1[6] = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x20800u + (uint32_t)(0x16) * 1u))));
  param_1[7] = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x20800u + (uint32_t)(0x17) * 1u))));
  return 0;
}

undefined4 rdbi_1f03_callback(void)

{
  return 0;
}

undefined4 rdbi_1f04_callback(void)

{
  return 0;
}

undefined4 rdbi_2001_callback(undefined1 *param_1)

{
  undefined1 uVar1;
  
  uVar1 = 0xff;
  if (DAT_febee849 == 'D') {
    uVar1 = return_const_1_b5ed0();
  }
  *param_1 = uVar1;
  return 0;
}

undefined4 rdbi_2002_callback(undefined1 *param_1)

{
  undefined1 uVar1;
  
  if (DAT_febee91c == 0x55aaaa55) {
    uVar1 = 0;
  }
  else if (DAT_febee91c == -0x55aaaa56) {
    uVar1 = 1;
  }
  else {
    uVar1 = 0xff;
  }
  *param_1 = uVar1;
  return 0;
}

undefined4 rdbi_2003_callback(undefined1 *param_1)

{
  undefined4 uVar1;
  undefined1 uStack_9;
  
  if (DAT_febee849 == 'D') {
    uVar1 = ((void)(7), return_const_ff_b5ed4());
    uStack_9 = (undefined1)uVar1;
    store_minimum_u8_7016e(uVar1,0xff,&uStack_9);
  }
  else {
    uStack_9 = 0xff;
  }
  *param_1 = uStack_9;
  return 0;
}

undefined4 rdbi_2004_callback(undefined1 *param_1)

{
  undefined4 uVar1;
  undefined1 uStack_9;
  
  if (DAT_febee849 == 'D') {
    uVar1 = ((void)(8), return_const_ff_b5ed4());
    uStack_9 = (undefined1)uVar1;
    store_minimum_u8_7016e(uVar1,0xff,&uStack_9);
  }
  else {
    uStack_9 = 0xff;
  }
  *param_1 = uStack_9;
  return 0;
}

undefined4 rdbi_2005_callback(undefined1 *param_1)

{
  undefined1 uStack_9;
  
  uStack_9 = DAT_febee84d;
  if (DAT_febee84a == 'Z') {
    store_minimum_u8_7016e(DAT_febee84d,0xff,&uStack_9);
  }
  else {
    uStack_9 = 0xff;
  }
  *param_1 = uStack_9;
  return 0;
}

undefined4 rdbi_2006_callback(undefined1 *param_1)

{
  undefined1 uStack_9;
  
  uStack_9 = DAT_febee84e;
  if (DAT_febee84a == 'Z') {
    store_minimum_u8_7016e(DAT_febee84e,0xff,&uStack_9);
  }
  else {
    uStack_9 = 0xff;
  }
  *param_1 = uStack_9;
  return 0;
}

undefined4 rdbi_2007_callback(undefined1 *param_1)

{
  undefined1 uStack_9;
  
  uStack_9 = DAT_febee84f;
  if (DAT_febee84a == 'Z') {
    store_minimum_u8_7016e(DAT_febee84f,0xff,&uStack_9);
  }
  else {
    uStack_9 = 0xff;
  }
  *param_1 = uStack_9;
  return 0;
}

undefined4 rdbi_2008_callback(undefined1 *param_1)

{
  undefined1 uStack_9;
  
  uStack_9 = DAT_febee850;
  if (DAT_febee84a == 'Z') {
    store_minimum_u8_7016e(DAT_febee850,0xff,&uStack_9);
  }
  else {
    uStack_9 = 0xff;
  }
  *param_1 = uStack_9;
  return 0;
}

undefined4 rdbi_2009_callback(undefined1 *param_1)

{
  undefined1 uStack_9;
  
  uStack_9 = DAT_febee851;
  if (DAT_febee84a == 'Z') {
    store_minimum_u8_7016e(DAT_febee851,0xff,&uStack_9);
  }
  else {
    uStack_9 = 0xff;
  }
  *param_1 = uStack_9;
  return 0;
}

undefined4 rdbi_200a_callback(undefined1 *param_1)

{
  uint8_t stack_record_b[11];
  
  if (DAT_febee849 == 'D') {
    stack_record_b[0] = ((void)(9), return_const_ff_b5ed4());
    stack_record_b[1] = ((void)(10), return_const_ff_b5ed4());
    stack_record_b[2] = ((void)(0xb), return_const_ff_b5ed4());
    store_minimum_u8_7016e(stack_record_b[0],0xff,((uint8_t *)(stack_record_b)));
    store_minimum_u8_7016e(stack_record_b[1],0xff,((uint8_t *)((stack_record_b + 1))));
    store_minimum_u8_7016e(stack_record_b[2],0xff,((uint8_t *)((stack_record_b + 2))));
    *param_1 = stack_record_b[0];
    param_1[1] = stack_record_b[1];
  }
  else {
    stack_record_b[2] = 0xff;
    *param_1 = 0xff;
    param_1[1] = 0xff;
  }
  param_1[2] = stack_record_b[2];
  return 0;
}

undefined4 rdbi_200b_callback(undefined1 *param_1)

{
  uint8_t stack_record_c[12];
  
  if (DAT_febee849 == 'D') {
    stack_record_c[0] = ((void)(0), return_const_ff_b5ed4());
    stack_record_c[1] = ((void)(1), return_const_ff_b5ed4());
    stack_record_c[2] = ((void)(2), return_const_ff_b5ed4());
    stack_record_c[3] = ((void)(3), return_const_ff_b5ed4());
    store_minimum_u8_7016e(stack_record_c[0],0xff,((uint8_t *)(stack_record_c)));
    store_minimum_u8_7016e(stack_record_c[1],0xff,((uint8_t *)((stack_record_c + 1))));
    store_minimum_u8_7016e(stack_record_c[2],0xff,((uint8_t *)((stack_record_c + 2))));
    store_minimum_u8_7016e(stack_record_c[3],0xff,((uint8_t *)((stack_record_c + 3))));
    *param_1 = stack_record_c[0];
    param_1[1] = stack_record_c[1];
    param_1[2] = stack_record_c[2];
  }
  else {
    stack_record_c[3] = 0xff;
    *param_1 = 0xff;
    param_1[1] = 0xff;
    param_1[2] = 0xff;
  }
  param_1[3] = stack_record_c[3];
  return 0;
}

undefined4 rdbi_200c_callback(undefined1 *param_1)

{
  undefined4 uVar1;
  undefined1 uStack_9;
  
  if (DAT_febee849 == 'D') {
    uVar1 = ((void)(4), return_const_ff_b5ed4());
    uStack_9 = (undefined1)uVar1;
    store_minimum_u8_7016e(uVar1,0xff,&uStack_9);
  }
  else {
    uStack_9 = 0xff;
  }
  *param_1 = uStack_9;
  return 0;
}

undefined4 rdbi_200d_callback(undefined1 *param_1)

{
  undefined1 uStack_9;
  
  uStack_9 = DAT_febee852;
  if (DAT_febee84a == 'Z') {
    store_minimum_u8_7016e(DAT_febee852,0xff,&uStack_9);
  }
  else {
    uStack_9 = 0xff;
  }
  *param_1 = uStack_9;
  return 0;
}

undefined4 rdbi_200e_callback(undefined1 *param_1)

{
  undefined4 uVar1;
  undefined1 uStack_9;
  
  if (DAT_febee849 == 'D') {
    uVar1 = ((void)(6), return_const_ff_b5ed4());
    uStack_9 = (undefined1)uVar1;
    store_minimum_u8_7016e(uVar1,0xff,&uStack_9);
  }
  else {
    uStack_9 = 0xff;
  }
  *param_1 = uStack_9;
  return 0;
}

undefined4 rdbi_200f_callback(undefined1 *param_1)

{
  undefined4 uVar1;
  undefined1 uStack_9;
  
  if (DAT_febee849 == 'D') {
    uVar1 = ((void)(0xc), return_const_ff_b5ed4());
    uStack_9 = (undefined1)uVar1;
    store_minimum_u8_7016e(uVar1,0xff,&uStack_9);
  }
  else {
    uStack_9 = 0xff;
  }
  *param_1 = uStack_9;
  return 0;
}

undefined4 rdbi_2010_callback(undefined1 *param_1)

{
  undefined1 uVar1;
  
  if ((DAT_febee924 == 0x55aaaa55) && (DAT_febee92c == 0x55aaaa55)) {
    uVar1 = 0;
    goto LAB_0004f976;
  }
  if (DAT_febee924 == -0x55aaaa56) {
    if (DAT_febee92c == 0x55aaaa55) {
      uVar1 = 1;
      goto LAB_0004f976;
    }
    if (DAT_febee92c == -0x55aaaa56) {
      uVar1 = 2;
      goto LAB_0004f976;
    }
  }
  if ((DAT_febee924 == 0x55aaaa55) && (DAT_febee92c == -0x55aaaa56)) {
    uVar1 = 3;
  }
  else {
    uVar1 = 0xff;
  }
LAB_0004f976:
  *param_1 = uVar1;
  return 0;
}

undefined4 rdbi_2012_callback(undefined4 param_1)

{
  (*((bool *)camry_host_ptr((uint32_t)(param_1)))) = DAT_febee81e == 'Z';
  return 0;
}

undefined4 rdbi_2013_callback(undefined4 param_1)

{
  store_low_u16_big_endian_bytes_6a574(DAT_febee8e2, ((undefined1 *)camry_host_ptr((uint32_t)(param_1))));
  return 0;
}

undefined4 rdbi_2014_callback(undefined4 param_1)

{
  (*((bool *)camry_host_ptr((uint32_t)(param_1)))) = DAT_febee886 != '\0';
  return 0;
}

undefined4 rdbi_2030_callback(int param_1)

{
  undefined1 *puVar1;
  undefined1 *puVar2;
  uint uVar3;
  
  uVar3 = 0;
  do {
    puVar1 = ((undefined1 *)camry_host_ptr((uint32_t)(uVar3 + param_1)));
    *puVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x20850u + (uint32_t)(uVar3) * 1u))));
    puVar2 = ((undefined *)camry_host_ptr((uint32_t)(0x17da0u + (uint32_t)(uVar3) * 1u)));
    uVar3 = uVar3 + 1;
    puVar1[8] = *puVar2;
  } while (uVar3 < 8);
  return 0;
}

undefined4 rdbi_2032_callback(undefined1 *param_1)

{
  int iVar1;
  int iVar2;
  int iVar3;
  
  *param_1 = 1;
  iVar3 = get_identity_byte_febf066c_62e18();
  iVar2 = 0;
  if (iVar3 == 0) {
    do {
      iVar1 = iVar2 + 1;
      iVar3 = iVar2 + -0xf;
      param_1[iVar2 + 1] = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x17d80u + (uint32_t)(iVar2) * 1u))));
      iVar2 = iVar1;
    } while (((iVar3 < 0) || (iVar1 < 0)));
  }
  else {
    do {
      iVar1 = iVar2 + 1;
      param_1[iVar2 + 1] = 0x21;
      iVar3 = iVar2 + -0xf;
      iVar2 = iVar1;
    } while (((iVar3 < 0) || (iVar1 < 0)));
  }
  return 0;
}

undefined4 rdbi_f181_callback(undefined1 *param_1)

{
  int iVar1;
  int iVar2;
  int iVar3;
  
  *param_1 = 2;
  iVar3 = get_identity_byte_febf066c_62e18();
  iVar2 = 0;
  if (iVar3 == 0) {
    do {
      param_1[iVar2 + 1] = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x20860u + (uint32_t)(iVar2) * 1u))));
      iVar1 = iVar2 + 1;
      iVar3 = iVar2 + -0xf;
      param_1[iVar2 + 0x11] = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x17dc0u + (uint32_t)(iVar2) * 1u))));
      iVar2 = iVar1;
    } while (((iVar3 < 0) || (iVar1 < 0)));
  }
  else {
    do {
      iVar1 = iVar2 + 1;
      param_1[iVar2 + 1] = 0x21;
      iVar3 = iVar2 + -0xf;
      param_1[iVar2 + 0x11] = 0x21;
      iVar2 = iVar1;
    } while (((iVar3 < 0) || (iVar1 < 0)));
  }
  return 0;
}

undefined4 rdbi_f186_callback(uchar *param_1)

{
  dcm_get_session(param_1);
  return 0;
}

undefined4 rdbi_f18c_callback(int param_1,uint param_2)

{
  uint8_t stack_record_34[52];
  int iVar1;
  uint *puVar2;
  int iVar3;
  uint uVar4;
  undefined4 uVar5;
  undefined4 *puVar6;
  
  puVar2 = stack_record_34;
  puVar6 = ((undefined *)camry_host_ptr(0x21320u));
  do {
    uVar5 = *puVar6;
    puVar6 = puVar6 + 1;
    *puVar2 = uVar5;
    puVar2 = puVar2 + 1;
  } while (camry_host_addr(puVar6)!=((uint32_t)(0x21348u)));
  uVar4 = nvm_get_record(0x207, camry_host_addr(stack_record_34));
  if ((uVar4 == 0x10) && ((*((uint32_t *)(stack_record_34 + 0))) == 0xa55a5aa5)) {
    for (iVar3 = 0; iVar1 = iVar3 - (param_2 & 0xffff), ((iVar1 < 0) || (iVar3 < 0));
        iVar3 = iVar3 + 1) {
      (*((undefined1 *)camry_host_ptr((uint32_t)(iVar3 + param_1)))) = (stack_record_34 + 4)[iVar3];
    }
  }
  else {
    for (iVar3 = 0; iVar1 = iVar3 - (param_2 & 0xffff), ((iVar1 < 0) || (iVar3 < 0));
        iVar3 = iVar3 + 1) {
      (*((undefined1 *)camry_host_ptr((uint32_t)(iVar3 + param_1)))) = 0x3f;
    }
  }
  return 0;
}

undefined4 rdbi_0101_callback(undefined4 param_1,undefined2 param_2)

{
  build_available_direct_did_group_bitmap_4d1a4(param_1,param_2);
  return 0;
}

undefined4 rdbi_0100_callback(uchar *param_1,ushort param_2)

{
  serialize_available_did_bitmap(0x100,param_1,param_2);
  return 0;
}

undefined4 rdbi_0200_callback(uchar *param_1,ushort param_2)

{
  serialize_available_did_bitmap(0x200,param_1,param_2);
  return 0;
}

undefined4 rdbi_1000_callback(uchar *param_1,ushort param_2)

{
  serialize_available_did_bitmap(0x1000,param_1,param_2);
  return 0;
}

undefined4 rdbi_1100_callback(uchar *param_1,ushort param_2)

{
  serialize_available_did_bitmap(0x1100,param_1,param_2);
  return 0;
}

undefined4 rdbi_1c00_callback(uchar *param_1,ushort param_2)

{
  serialize_available_did_bitmap(0x1c00,param_1,param_2);
  return 0;
}

undefined4 rdbi_1d00_callback(uchar *param_1,ushort param_2)

{
  serialize_available_did_bitmap(0x1d00,param_1,param_2);
  return 0;
}

undefined4 rdbi_1f00_callback(uchar *param_1,ushort param_2)

{
  serialize_available_did_bitmap(0x1f00,param_1,param_2);
  return 0;
}

undefined4 rdbi_2000_callback(uchar *param_1,ushort param_2)

{
  serialize_available_did_bitmap(0x2000,param_1,param_2);
  return 0;
}

undefined4 rdbi_f100_callback(uchar *param_1,ushort param_2)

{
  serialize_available_did_bitmap(0xf100,param_1,param_2);
  return 0;
}

undefined4 validate_febe_memory_span_against_five_exclusions_4fbe8(undefined *param_1,uint param_2)

{
  undefined4 uVar1;
  uint uVar2;
  
  uVar1 = 0x5a;
  if ((0xfebdffffu < (uint32_t)camry_host_addr(param_1)) &&
     ((uint32_t)camry_host_addr(param_1) <= (uint32_t)(0xfec00000 - (param_2 & 0xffff)))) {
    uVar2 = 0;
    do {
      if (((uint32_t)camry_host_addr(param_1) <= (*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x29258u + (uint32_t)(uVar2 * 2) * 4u))))) &&
         ((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x29254u + (uint32_t)(uVar2 * 2) * 4u)))) + (1 - (param_2 & 0xffff)) <= (uint32_t)camry_host_addr(param_1))) {
        uVar1 = 0;
      }
      uVar2 = uVar2 + 1;
    } while (uVar2 < 5);
    return uVar1;
  }
  return 0;
}

void copy_bytes_forward_u16_length_4fc2c(uint param_1,int param_2,int param_3)

{
  int iVar1;
  int iVar2;
  
  for (iVar2 = 0; iVar1 = iVar2 - (param_1 & 0xffff), ((iVar1 < 0) || (iVar2 < 0));
      iVar2 = iVar2 + 1) {
    (*((undefined1 *)camry_host_ptr((uint32_t)(iVar2 + param_3)))) = (*((undefined1 *)camry_host_ptr((uint32_t)(iVar2 + param_2))));
  }
  return;
}

undefined4 validate_ff20_memory_span_against_two_exclusions_4fc48(undefined *param_1,uint param_2)

{
  undefined4 uVar1;
  uint uVar2;
  
  uVar1 = 0x5a;
  if ((0xff1fffffu < (uint32_t)camry_host_addr(param_1)) &&
     ((uint32_t)camry_host_addr(param_1) <= (uint32_t)(-(param_2 & 0xffff) - 0xdf8000))) {
    uVar2 = 0;
    do {
      if (((uint32_t)camry_host_addr(param_1) <= (*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x29248u + (uint32_t)(uVar2 * 2) * 4u))))) &&
         ((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x29244u + (uint32_t)(uVar2 * 2) * 4u)))) + (1 - (param_2 & 0xffff)) <= (uint32_t)camry_host_addr(param_1))) {
        uVar1 = 0;
      }
      uVar2 = uVar2 + 1;
    } while (uVar2 < 2);
    return uVar1;
  }
  return 0;
}

uint read_configured_application_memory(uchar *address_record,uchar *output,ushort length)

{
  uint extraout_r6;
  int iVar1;
  int iVar2;
  uint uVar3;
  
  uVar3 = (uint)length;
  iVar2 = (uint)address_record[4] +
          (uint)address_record[3] * 0x100 +
          (uint)address_record[2] * 0x10000 + (uint)address_record[1] * 0x1000000;
  if (uVar3 - 1 < 0xff) {
    if (*address_record == '\x01') {
      iVar1 = validate_febe_memory_span_against_five_exclusions_4fbe8(((undefined *)camry_host_ptr((uint32_t)(iVar2))), uVar3);
      if (iVar1 == 0x5a) {
        copy_bytes_forward_u16_length_4fc2c(uVar3, iVar2, camry_host_addr(output));
        return 0;
      }
    }
    else if ((*address_record == '\x02') && (iVar2 = validate_ff20_memory_span_against_two_exclusions_4fc48(((undefined *)camry_host_ptr((uint32_t)(iVar2))), uVar3), iVar2 == 0x5a)) {
      iVar2 = read_unaligned_nvm_bytes_through_four_byte_buffer_66e7c(extraout_r6 & 0xffff, camry_host_addr(output), uVar3);
      if (iVar2 == 0) {
        return 0;
      }
      goto LAB_0004fcfa;
    }
    uVar3 = 3;
  }
  else {
LAB_0004fcfa:
    uVar3 = 4;
  }
  return uVar3;
}

uint communication_request_sample_above_limit(void)

{
  return (uint)(communication_control_admission_limit < DAT_febee892);
}

void publish_diagnostic_normal_tx_policy_request(uchar network_selector,uchar disable_tx)

{
  uchar uVar1;
  
  uVar1 = '\0';
  if ((disable_tx == '\0') || (uVar1 = '\x11', disable_tx == '\x01')) {
    diagnostic_normal_tx_policy_request = uVar1;
  }
  return;
}

void start_pending_write_mode_request(void)

{
  undefined1 uVar1;
  uint32_t puVar2;
  puVar2 = 0xfebeb800u;
  if (DAT_febe81af == '\x11') {
    puVar2 = 0xfebeb800u;
    request_default_quad_when_marker_and_status_allow_35aa2();
    thunk_set_byte_febeaf47_b9320(0x11);
    uVar1 = 0x12;
  }
  else {
    if (DAT_febe81af != '!') {
      return;
    }
    thunk_set_byte_febeaf47_b9320(0x22);
    uVar1 = 0x22;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x3651))))) = uVar1;
  return;
}

void finish_pending_write_mode_request(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  if (DAT_febe81af != '\x12') {
    if (DAT_febe81af != '\"') {
      return;
    }
    puVar1 = 0xfebeb800u;
    start_or_enqueue_diagnostic_clear_operation6_5199e();
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x3651))))) = 0;
  return;
}

uint write_0204_precondition(void)

{
  uint uVar1;
  
  if (DAT_000318ae < DAT_febee892) {
    uVar1 = 5;
  }
  else {
    uVar1 = 0;
  }
  return uVar1;
}

uint write_0204_stage_mode_persistence(uchar *payload,ushort unused_length)

{
  DAT_febe81af = 0x21;
  if ((payload[1] & 0x80) != 0) {
    DAT_febe81af = 0x11;
  }
  DAT_febe81b2 = 0x2e10;
  return 2;
}

uint write_2001_precondition(void)

{
  uint uVar1;
  
  if (DAT_000318ae < DAT_febee892) {
    uVar1 = 5;
  }
  else {
    uVar1 = 0;
  }
  return uVar1;
}

uint write_2001_request_record101_reset(uchar *payload,ushort unused_length)

{
  undefined2 uVar1;
  uint32_t puVar2;
  int iVar3;
  uint uVar4;
  
  puVar2 = 0xfebeb800u;
  iVar3 = ((void)(unused_length), thunk_is_distinct_aeba8_index_b5a74(*payload));
  if (iVar3 == 1) {
    uVar4 = request_record101_reset_write();
    uVar1 = 0x2e10;
    if (uVar4 == 1) {
      uVar4 = 2;
    }
    else {
      uVar1 = 0;
      uVar4 = 9;
    }
  }
  else {
    uVar4 = 4;
    uVar1 = 0;
  }
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar2 + -0x364e)))) = uVar1;
  return uVar4;
}

uint write_2002_precondition(void)

{
  uint uVar1;
  
  if (DAT_000318ae < DAT_febee892) {
    uVar1 = 5;
  }
  else {
    uVar1 = 0;
  }
  return uVar1;
}

uint write_2002_stage_record102_mode(uchar *payload,ushort unused_length)

{
  uint32_t puVar1;
  uint encoded_mode;
  undefined2 uVar2;
  uint uVar3;
  
  puVar1 = 0xfebeb800u;
  uVar2 = 0x2e10;
  uVar3 = 2;
  if (*payload == '\0') {
    encoded_mode = 0x55aaaa55;
  }
  else {
    if (*payload != '\x01') {
      uVar3 = 4;
      uVar2 = 0;
      goto LAB_0004fe44;
    }
    encoded_mode = 0xaa5555aa;
  }
  puVar1 = 0xfebeb800u;
  stage_record102_mode_write(encoded_mode);
LAB_0004fe44:
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x364e)))) = uVar2;
  return uVar3;
}

uint write_2005_precondition(void)

{
  uint uVar1;
  
  if (DAT_000318ae < DAT_febee892) {
    uVar1 = 5;
  }
  else {
    uVar1 = 0;
  }
  return uVar1;
}

uint write_2005_stage_record103_slot3(uchar *payload,ushort unused_length)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  record103_byte_write_thunk('\x03',*payload);
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x364e)))) = 0x2e10;
  return 2;
}

uint write_2006_precondition(void)

{
  uint uVar1;
  
  if (DAT_000318ae < DAT_febee892) {
    uVar1 = 5;
  }
  else {
    uVar1 = 0;
  }
  return uVar1;
}

uint write_2006_stage_record103_slot4(uchar *payload,ushort unused_length)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  record103_byte_write_thunk('\x04',*payload);
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x364e)))) = 0x2e10;
  return 2;
}

uint write_2007_precondition(void)

{
  uint uVar1;
  
  if (DAT_000318ae < DAT_febee892) {
    uVar1 = 5;
  }
  else {
    uVar1 = 0;
  }
  return uVar1;
}

uint write_2007_stage_record103_slot5(uchar *payload,ushort unused_length)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  record103_byte_write_thunk('\x05',*payload);
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x364e)))) = 0x2e10;
  return 2;
}

uint write_2008_precondition(void)

{
  uint uVar1;
  
  if (DAT_000318ae < DAT_febee892) {
    uVar1 = 5;
  }
  else {
    uVar1 = 0;
  }
  return uVar1;
}

uint write_2008_stage_record103_slot6(uchar *payload,ushort unused_length)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  record103_byte_write_thunk('\x06',*payload);
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x364e)))) = 0x2e10;
  return 2;
}

uint write_2009_precondition(void)

{
  uint uVar1;
  
  if (DAT_000318ae < DAT_febee892) {
    uVar1 = 5;
  }
  else {
    uVar1 = 0;
  }
  return uVar1;
}

uint write_2009_stage_record103_slot7(uchar *payload,ushort unused_length)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  record103_byte_write_thunk('\a',*payload);
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x364e)))) = 0x2e10;
  return 2;
}

uint write_200d_precondition(void)

{
  uint uVar1;
  
  if (DAT_000318ae < DAT_febee892) {
    uVar1 = 5;
  }
  else {
    uVar1 = 0;
  }
  return uVar1;
}

uint write_200d_stage_record103_slot8(uchar *payload,ushort unused_length)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  record103_byte_write_thunk('\b',*payload);
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + -0x364e)))) = 0x2e10;
  return 2;
}

uint write_2010_precondition(void)

{
  uint uVar1;
  
  if (DAT_000318ae < DAT_febee892) {
    uVar1 = 5;
  }
  else {
    uVar1 = 0;
  }
  return uVar1;
}

uint write_2010_stage_mode_pair(uchar *payload,ushort unused_length)

{
  uchar uVar1;
  undefined2 uVar2;
  uint32_t puVar3;
  uint uVar4;
  
  puVar3 = 0xfebeb800u;
  uVar1 = *payload;
  if (uVar1 == '\0') {
    uVar4 = 0x55aaaa55;
  }
  else {
    uVar4 = 0xfffffff4;
    if (uVar1 != '\x01' && uVar1 != '\x02') goto LAB_0004ffca;
    uVar4 = 0xaa5555aa;
  }
  puVar3 = 0xfebeb800u;
  uVar4 = stage_encoded_mode_pair_thunk(uVar4,0x55aaaa55);
LAB_0004ffca:
  uVar4 = diag_translate_application_request_status(uVar4);
  uVar2 = 0;
  if (uVar4 == 2) {
    uVar2 = 0x2e10;
  }
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x364e)))) = uVar2;
  return uVar4;
}

uint write_2012_precondition(void)

{
  return 0;
}

uint write_2012_latch_availability_override(uchar *payload,ushort unused_length)

{
  uint uVar1;
  
  if (*payload == '\x01') {
    latch_availability_override();
    uVar1 = 0;
  }
  else {
    uVar1 = 4;
  }
  return uVar1;
}

uint write_2013_precondition(void)

{
  if (((DAT_febe80a5 == '\0') && (DAT_febe80a0 == '\0')) && (DAT_febee892 <= DAT_000318ae)) {
    return 0;
  }
  return 5;
}
