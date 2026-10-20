#include "common.h"

void return_only_stub_be06a(void)

{
  return;
}

void return_only_stub_be06c(void)

{
  return;
}

void return_only_stub_be06e(void)

{
  return;
}

void snapshot_diagnostic_application_kind4(F33DiagnosticApplicationSample *output)

{
  uchar uVar1;
  undefined2 uVar2;
  undefined2 uVar3;
  short sVar4;
  ushort uVar5;
  uint uVar6;
  
  output->raw[0] = DAT_febebe78;
  *(undefined2 *)(output->raw + 10) = DAT_febebee2;
  *(undefined2 *)(output->raw + 0xc) = DAT_febebe82;
  sVar4 = ((int)(int16_t)DAT_febeaf40);
  *(short *)(output->raw + 0x18) = ((int)(int16_t)DAT_febeaf40);
  uVar2 = DAT_febeb11a;
  output->raw[1] = 0 < sVar4;
  uVar3 = ((int)(int16_t)DAT_febeae6e);
  uVar1 = DAT_febeacf1;
  *(undefined2 *)(output->raw + 0xe) = uVar2;
  output->raw[2] = uVar1;
  uVar2 = ((int)(int16_t)DAT_febeae12);
  *(undefined2 *)(output->raw + 0x14) = uVar3;
  *(undefined2 *)(output->raw + 0x12) = uVar2;
  output->raw[3] = DAT_febeacf5;
  output->raw[4] = DAT_febead0a;
  *(undefined2 *)(output->raw + 0x16) = ((int)(int16_t)DAT_febeae36);
  output->raw[5] = DAT_febeb1c4;
  *(undefined2 *)(output->raw + 0x1a) = ((int)(int16_t)DAT_febeac56);
  uVar5 = received_retained_word;
  *(undefined2 *)(output->raw + 0x1c) = uVar3;
  *(undefined2 *)(output->raw + 0x1e) = uVar3;
  *(ushort *)(output->raw + 0x10) = uVar5;
  *(uint *)(output->raw + 0x20) = received_word_unchanged_age;
  output->raw[6] = DAT_febebe60;
  output->raw[7] = DAT_febebe62;
  uVar6 = received_typed_scalar;
  output->raw[0x34] = '\0';
  output->raw[0x35] = '\0';
  output->raw[0x36] = '\0';
  output->raw[0x37] = '\0';
  *(uint *)(output->raw + 0x24) = uVar6;
  output->raw[0x28] = ((volatile uint8_t *)camry_host_ptr(0xfebebe66u))[0];
  output->raw[0x29] = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebebe66u + (uint32_t)(1) * 1u))));
  output->raw[0x2a] = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebebe66u + (uint32_t)(2) * 1u))));
  output->raw[0x2b] = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebebe66u + (uint32_t)(3) * 1u))));
  output->raw[0x2c] = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebebe66u + (uint32_t)(4) * 1u))));
  output->raw[0x2d] = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebebe66u + (uint32_t)(5) * 1u))));
  output->raw[8] = DAT_febead60;
  output->raw[9] = DAT_febead67;
  uVar1 = DAT_febead39;
  output->raw[0x31] = '\0';
  output->raw[0x30] = uVar1;
  uVar2 = ((int)(int16_t)DAT_febeae58);
  output->raw[0x32] = '\0';
  output->raw[0x33] = '\0';
  *(undefined2 *)(output->raw + 0x2e) = uVar2;
  return;
}

void return_only_stub_be12e(void)

{
  return;
}

void return_only_stub_be130(void)

{
  return;
}

void return_only_stub_be132(void)

{
  return;
}

void snapshot_diagnostic_application_default(F33DiagnosticApplicationSample *output)

{
  uchar uVar1;
  undefined2 uVar2;
  undefined2 uVar3;
  short sVar4;
  ushort uVar5;
  uint uVar6;
  
  output->raw[0] = DAT_febebe78;
  *(undefined2 *)(output->raw + 10) = DAT_febebee2;
  *(undefined2 *)(output->raw + 0xc) = DAT_febebe82;
  sVar4 = ((int)(int16_t)DAT_febeafd0);
  *(short *)(output->raw + 0x18) = ((int)(int16_t)DAT_febeafd0);
  uVar2 = DAT_febeb11a;
  output->raw[1] = 0 < sVar4;
  uVar3 = ((int)(int16_t)DAT_febeae6e);
  uVar1 = DAT_febeacf1;
  *(undefined2 *)(output->raw + 0xe) = uVar2;
  output->raw[2] = uVar1;
  uVar2 = ((int)(int16_t)DAT_febeae12);
  *(undefined2 *)(output->raw + 0x14) = uVar3;
  *(undefined2 *)(output->raw + 0x12) = uVar2;
  output->raw[3] = DAT_febeacf5;
  output->raw[4] = DAT_febead0a;
  *(undefined2 *)(output->raw + 0x16) = ((int)(int16_t)DAT_febeae36);
  output->raw[5] = DAT_febeb1c4;
  *(undefined2 *)(output->raw + 0x1a) = ((int)(int16_t)DAT_febeb02c);
  uVar5 = received_retained_word;
  *(undefined2 *)(output->raw + 0x1c) = uVar3;
  *(undefined2 *)(output->raw + 0x1e) = uVar3;
  *(ushort *)(output->raw + 0x10) = uVar5;
  *(uint *)(output->raw + 0x20) = received_word_unchanged_age;
  output->raw[6] = DAT_febebe60;
  output->raw[7] = DAT_febebe62;
  uVar6 = received_typed_scalar;
  output->raw[0x34] = '\0';
  output->raw[0x35] = '\0';
  output->raw[0x36] = '\0';
  output->raw[0x37] = '\0';
  *(uint *)(output->raw + 0x24) = uVar6;
  output->raw[0x28] = ((volatile uint8_t *)camry_host_ptr(0xfebebe66u))[0];
  output->raw[0x29] = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebebe66u + (uint32_t)(1) * 1u))));
  output->raw[0x2a] = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebebe66u + (uint32_t)(2) * 1u))));
  output->raw[0x2b] = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebebe66u + (uint32_t)(3) * 1u))));
  output->raw[0x2c] = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebebe66u + (uint32_t)(4) * 1u))));
  output->raw[0x2d] = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebebe66u + (uint32_t)(5) * 1u))));
  output->raw[8] = DAT_febead60;
  output->raw[9] = DAT_febead67;
  uVar1 = DAT_febead39;
  output->raw[0x31] = '\0';
  output->raw[0x30] = uVar1;
  uVar2 = ((int)(int16_t)DAT_febeae58);
  output->raw[0x32] = '\0';
  output->raw[0x33] = '\0';
  *(undefined2 *)(output->raw + 0x2e) = uVar2;
  return;
}

void return_only_stub_be1f2(void)

{
  return;
}

void return_only_stub_be1f4(void)

{
  return;
}

void return_only_stub_be1f6(void)

{
  return;
}

void select_snapshot_packer_by_kind_ten_be1f8(undefined4 param_1,short param_2)

{
  if (param_2 == 10) {
    pack_received_snapshot_with_af40_scalar_be216(((undefined1 *)camry_host_ptr((uint32_t)(param_1))));
  }
  else {
    pack_received_snapshot_with_afd0_scalar_be28e(((undefined1 *)camry_host_ptr((uint32_t)(param_1))));
  }
  return;
}

void return_only_stub_be210(void)

{
  return;
}

void return_only_stub_be212(void)

{
  return;
}

void return_only_stub_be214(void)

{
  return;
}

void pack_received_snapshot_with_af40_scalar_be216(undefined1 *param_1)

{
  short sVar1;
  undefined1 uVar2;
  undefined2 uVar3;
  
  sVar1 = ((int)(int16_t)DAT_febeaf40);
  param_1[3] = DAT_febebe60;
  param_1[4] = DAT_febebe62;
  *(ushort *)(param_1 + 8) = received_retained_word;
  *(uint *)(param_1 + 0x10) = received_word_unchanged_age;
  *(uint *)(param_1 + 0x14) = received_typed_scalar;
  param_1[0x18] = ((volatile uint8_t *)camry_host_ptr(0xfebebe66u))[0];
  param_1[0x19] = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebebe66u + (uint32_t)(1) * 1u))));
  param_1[0x1a] = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebebe66u + (uint32_t)(2) * 1u))));
  param_1[0x1b] = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebebe66u + (uint32_t)(3) * 1u))));
  param_1[0x1c] = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebebe66u + (uint32_t)(4) * 1u))));
  param_1[0x1d] = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebebe66u + (uint32_t)(5) * 1u))));
  *(undefined2 *)(param_1 + 10) = DAT_febebee2;
  uVar3 = DAT_febebe82;
  *(short *)(param_1 + 0xe) = sVar1;
  *(undefined2 *)(param_1 + 6) = 0;
  *(undefined2 *)(param_1 + 0x1e) = 0;
  *(undefined2 *)(param_1 + 0xc) = uVar3;
  *param_1 = DAT_febebe78;
  uVar2 = DAT_febeb1c4;
  param_1[2] = 0 < sVar1;
  param_1[5] = 0;
  param_1[1] = uVar2;
  return;
}

void return_only_stub_be288(void)

{
  return;
}

void return_only_stub_be28a(void)

{
  return;
}

void return_only_stub_be28c(void)

{
  return;
}

void pack_received_snapshot_with_afd0_scalar_be28e(undefined1 *param_1)

{
  short sVar1;
  undefined1 uVar2;
  undefined2 uVar3;
  
  sVar1 = ((int)(int16_t)DAT_febeafd0);
  param_1[3] = DAT_febebe60;
  param_1[4] = DAT_febebe62;
  *(ushort *)(param_1 + 8) = received_retained_word;
  *(uint *)(param_1 + 0x10) = received_word_unchanged_age;
  *(uint *)(param_1 + 0x14) = received_typed_scalar;
  param_1[0x18] = ((volatile uint8_t *)camry_host_ptr(0xfebebe66u))[0];
  param_1[0x19] = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebebe66u + (uint32_t)(1) * 1u))));
  param_1[0x1a] = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebebe66u + (uint32_t)(2) * 1u))));
  param_1[0x1b] = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebebe66u + (uint32_t)(3) * 1u))));
  param_1[0x1c] = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebebe66u + (uint32_t)(4) * 1u))));
  param_1[0x1d] = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebebe66u + (uint32_t)(5) * 1u))));
  *(undefined2 *)(param_1 + 10) = DAT_febebee2;
  uVar3 = DAT_febebe82;
  *(short *)(param_1 + 0xe) = sVar1;
  *(undefined2 *)(param_1 + 6) = 0;
  *(undefined2 *)(param_1 + 0x1e) = 0;
  *(undefined2 *)(param_1 + 0xc) = uVar3;
  *param_1 = DAT_febebe78;
  uVar2 = DAT_febeb1c4;
  param_1[2] = 0 < sVar1;
  param_1[5] = 0;
  param_1[1] = uVar2;
  return;
}

void return_only_stub_be300(void)

{
  return;
}

void return_only_stub_be302(void)

{
  return;
}

void scale_staged_byte_pair_to_control_raw(void)

{
  scaled_staged_byte_a = (ushort)((uint)((short)(ushort)DAT_febef03d * 0x147b) >> 0xc);
  scaled_staged_byte_b = (ushort)((uint)((short)(ushort)DAT_febef03e * 0x147b) >> 0xc);
  return;
}

void return_only_stub_be322(void)

{
  return;
}

void return_only_stub_be324(void)

{
  return;
}

void condition_staged_offset_scalar(void)

{
  uint32_t puVar1;
  int iVar2;
  char cVar3;
  short sStack_a;
  
  cVar3 = DAT_febef02c;
  puVar1 = 0xfebeb800u;
  if ((uint)(DAT_febef02d - 8) < 0x65u) {
    iVar2 = DAT_febef02d - 0x30;
    sStack_a = (short)iVar2;
    puVar1 = 0xfebeb800u;
    scale_signed16_by_unsigned_ratio_with_symmetric_saturation_d1232(iVar2,0x80,1,&sStack_a);
  }
  else {
    if (DAT_febef02c == '\0') {
      cVar3 = '\x01';
    }
    sStack_a = conditioned_offset_scalar;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x658))))) = cVar3;
  (*((short *)camry_host_ptr((uint32_t)(puVar1 + 0x65e)))) = sStack_a;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x65a))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x385a)))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x659))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x385b)))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x65c))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x385e)))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x65b))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x385f)))));
  return;
}

void return_only_stub_be38a(void)

{
  return;
}

int initialize_received_word_age_from_record13(void)

{
  uint8_t stack_record_c[12];
  uint32_t puVar1;
  int iVar2;
  undefined2 uVar3;
  
  puVar1 = 0xfebeb800u;
  (*((uint32_t *)(stack_record_c + 0))) = DAT_0001bec4;
  (*((uint32_t *)(stack_record_c + 4))) = DAT_0001bec8;
  iVar2 = call_nvm_get_record_with_u16_selector_ff0b0(0xd,stack_record_c);
  if (iVar2 == 0x10) {
    uVar3 = (undefined2)(*((uint32_t *)(stack_record_c + 0)));
  }
  else {
    uVar3 = 0;
    (*((uint32_t *)(stack_record_c + 4))) = 0;
  }
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar1 + 0x66e)))) = uVar3;
  (*((undefined4 *)camry_host_ptr((uint32_t)(puVar1 + 0x670)))) = (*((uint32_t *)(stack_record_c + 4)));
  return iVar2;
}

uint stage_received_word_age_record13(void)

{
  uint8_t stack_record_c[12];
  
  ((uint16_t *)(stack_record_c))[1] = 0;
  ((uint16_t *)(stack_record_c))[0] = received_retained_word;
  (*((uint32_t *)(stack_record_c + 4))) = received_word_unchanged_age;
  return call_nvm_set_record_with_u16_selector_ff09c(0xd,((uint16_t *)(stack_record_c)));
}

void return_only_stub_be620(void)

{
  return;
}

void seed_health_received_source_filter(void)

{
  undefined1 uVar1;
  uint uVar2;
  uint32_t puVar3;
  int local_c;
  
  uVar1 = DAT_febef052;
  puVar3 = 0xfebeb800u;
  store_nonnegative_signed16_as_word_d1222((int)((int)(int16_t)DAT_febef194),&local_c);
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(0x678))))) = uVar1;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(0x67b))))) = 0;
  uVar2 = (uint)(local_c * 800) >> 10;
  (*((short *)camry_host_ptr((uint32_t)(puVar3 + 0x682)))) = (short)uVar2;
  (*((uint *)camry_host_ptr((uint32_t)(puVar3 + 0x684)))) = uVar2 << 0x10;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(0x67a))))) = 0x5a;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(0x679))))) = 0x5a;
  return;
}

void refresh_first_health_source_cache(void)

{
  undefined1 uVar1;
  uint32_t puVar2;
  undefined2 uVar3;
  int local_1c;
  ushort out_half;
  uint out_word;
  struct { ushort first; ushort second; uint word; } sample;
  
  puVar2 = 0xfebeb800u;
  store_nonnegative_signed16_as_word_d1222((int)((int)(int16_t)DAT_febef194),&local_1c);
  store_unsigned32_minimum_d1d6e(local_1c,0x4000,&local_1c);
  sample.first = (*((ushort *)camry_host_ptr((uint32_t)(puVar2 + 0x682))));
  sample.word = (*((uint *)camry_host_ptr((uint32_t)(puVar2 + 0x684))));
  uVar3 = (undefined2)((uint)(local_1c * 800) >> 10);
  sample.second = (ushort)uVar3;
  filter_unsigned_sample_accumulator(&sample.first,(uint)DAT_000aee30 * 100,&out_half,&out_word);
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(0x38fb))))) == '\x01') {
    uVar1 = 0xa5;
  }
  else {
    uVar1 = 0xff;
    if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(0x38fb))))) == '\0') {
      uVar1 = 0x5a;
    }
  }
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar2 + 0x680)))) = uVar3;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(0x679))))) = uVar1;
  (*((ushort *)camry_host_ptr((uint32_t)(puVar2 + 0x682)))) = out_half;
  (*((uint *)camry_host_ptr((uint32_t)(puVar2 + 0x684)))) = out_word;
  return;
}

void refresh_second_health_source_cache(void)

{
  if (DAT_febef052 == '\x01') {
    DAT_febebe7a = 0xa5;
    DAT_febebe7b = true;
  }
  else {
    DAT_febebe7a = 0xff;
    if (DAT_febef052 == '\0') {
      DAT_febebe7a = 0x5a;
    }
    DAT_febebe7b = DAT_febeb18f == 'Z';
  }
  DAT_febebe78 = DAT_febef052;
  return;
}

void refresh_health_channel_classifications(void)

{
  if ((DAT_febef00b == '\0') && (DAT_febef00c == '\0')) {
    DAT_febebe7c = DAT_febef057 & 1;
    if ((DAT_febef057 & 1) == 0) goto LAB_000be74a;
  }
  else if ((DAT_febef00b == '\"') || (DAT_febef00c == '\"')) {
    DAT_febebe7c = 0x22;
    goto LAB_000be74a;
  }
  DAT_febebe7c = 0x11;
LAB_000be74a:
  if ((DAT_febef00d == '\0') && (DAT_febef00e == '\0')) {
    if ((DAT_febef051 & 1) == 0) {
      DAT_febebe7d = DAT_febef051 & 1;
      return;
    }
  }
  else if ((DAT_febef00d == '\"') || (DAT_febef00e == '\"')) {
    DAT_febebe7d = 0x22;
    return;
  }
  DAT_febebe7d = 0x11;
  return;
}

void refresh_health_received_source_generation(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  refresh_first_health_source_cache();
  refresh_second_health_source_cache();
  refresh_health_channel_classifications();
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x67e))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x393f)))));
  return;
}

void return_only_stub_be794(void)

{
  return;
}

void return_only_stub_be796(void)

{
  return;
}

void publish_f056_equals_one_as_be88_5a_be798(void)

{
  DAT_febebe88 = 0;
  if (DAT_febef056 == '\x01') {
    DAT_febebe88 = 0x5a;
  }
  return;
}

void aggregate_four_f00x_statuses_and_f054_bit_be7ac(void)

{
  if ((((DAT_febef003 == '\0') && (DAT_febef005 == '\0')) && (DAT_febef004 == '\0')) &&
     (DAT_febef006 == '\0')) {
    if ((DAT_febef054 & 1) == 0) {
      DAT_febebe89 = DAT_febef054 & 1;
      return;
    }
  }
  else if (((DAT_febef003 == '\"') || (DAT_febef005 == '\"')) ||
          ((DAT_febef004 == '\"' || (DAT_febef006 == '\"')))) {
    DAT_febebe89 = 0x22;
    return;
  }
  DAT_febebe89 = 0x11;
  return;
}

void refresh_be88_mode_and_be89_status_aggregate_be7fa(void)

{
  publish_f056_equals_one_as_be88_5a_be798();
  aggregate_four_f00x_statuses_and_f054_bit_be7ac();
  return;
}

void return_only_stub_be80a(void)

{
  return;
}

void return_only_stub_be80c(void)

{
  return;
}

void snapshot_three_status_or_and_group_16_be80e(void)

{
  uint32_t puVar1;
  uchar uVar2;
  bool bVar3;
  
  puVar1 = 0xfebeb800u;
  if ((DAT_febef09e == '\x01') || (DAT_febef0a6 == '\x01')) {
    bVar3 = true;
  }
  else {
    bVar3 = DAT_febef0a7 == '\x01';
  }
  uVar2 = get_grouped_status_byte(0x16);
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x68c))))) = bVar3;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x68d))))) = uVar2;
  return;
}

void return_only_stub_be842(void)

{
  return;
}

void return_only_stub_be844(void)

{
  return;
}

void compute_clamped_paired_scaled_difference_and_flags_be846(void)

{
  char cVar1;
  char cVar2;
  char cVar3;
  char cVar4;
  int iVar5;
  byte bVar6;
  undefined1 uVar7;
  int iVar8;
  int iVar9;
  uint32_t puVar10;
  int iVar11;
  char cVar12;
  byte bVar13;
  char cVar14;
  byte bVar15;
  char cVar16;
  char cVar17;
  int local_2c;
  
  bVar13 = DAT_febef0aa;
  cVar4 = DAT_febef0a7;
  cVar3 = DAT_febef0a6;
  cVar1 = DAT_febef0a5;
  cVar2 = DAT_febef0a4;
  puVar10 = 0xfebeb800u;
  if (DAT_febebe8d == 'Z') {
    iVar11 = 0;
    iVar9 = 0;
    cVar16 = '\0';
    cVar12 = '\0';
  }
  else {
    int limit;
    limit = (int)DAT_000af3f4;
    iVar11 = ((int)(signed char)DAT_febef098 * 0x931) / 0x10;
    iVar9 = ((int)(signed char)DAT_febef099 * 0x931) / 0x10;
    cVar16 = DAT_febebe91;
    if (iVar11 > limit) {
      iVar11 = limit;
      cVar16 = 'Z';
    }
    else if (iVar11 < -limit) {
      iVar11 = -limit;
      cVar16 = 'Z';
    }
    cVar12 = DAT_febebe91;
    if (iVar9 > limit) {
      iVar9 = limit;
      cVar12 = 'Z';
    }
    else if (iVar9 < -limit) {
      iVar9 = -limit;
      cVar12 = 'Z';
    }
  }
  if ((DAT_febeb11a == 0x400) && (DAT_febebe8d != 'Z')) {
    iVar8 = (((int)(int16_t)DAT_febef1c6) * 0x931) / 0x10;
    local_2c = (((int)(int16_t)DAT_febef1c8) * 0x931) / 0x10;
    if (DAT_febef09c == '\0') {
      iVar8 = -iVar8;
      local_2c = -local_2c;
    }
    iVar5 = DAT_000af3f0;
    if ((iVar8 - DAT_000af3f0 < 0 ==
         (iVar8 < 0 != DAT_000af3f0 < 0 && DAT_000af3f0 < 0 == iVar8 - DAT_000af3f0 < 0) &&
         iVar8 != DAT_000af3f0) ||
       (iVar5 = -DAT_000af3f0, cVar17 = DAT_febebe90,
       iVar8 + DAT_000af3f0 < 0 != (iVar8 < 0 != iVar5 < 0 && iVar5 < 0 == iVar8 + DAT_000af3f0 < 0)
       )) {
      iVar8 = iVar5;
      cVar17 = 'Z';
    }
    iVar5 = DAT_000af3f0;
    if ((local_2c - DAT_000af3f0 < 0 ==
         (local_2c < 0 != DAT_000af3f0 < 0 && DAT_000af3f0 < 0 == local_2c - DAT_000af3f0 < 0) &&
         local_2c != DAT_000af3f0) ||
       (iVar5 = -DAT_000af3f0, cVar14 = DAT_febebe90,
       local_2c + DAT_000af3f0 < 0 !=
       (local_2c < 0 != iVar5 < 0 && iVar5 < 0 == local_2c + DAT_000af3f0 < 0))) {
      local_2c = iVar5;
      cVar14 = 'Z';
    }
    local_2c = local_2c - iVar9;
    if ((DAT_febef0aa >> 1 & 1) == 0) {
      iVar9 = 0x10;
    }
    else {
      iVar9 = 0x10000;
      local_2c = (local_2c + (iVar8 - iVar11)) * 0xb50;
    }
    if (iVar9 != 0) {
      if (local_2c == -0x80000000 && iVar9 == -1) {
        local_2c = -0x80000000;
      }
      else {
        local_2c = (int)local_2c / (int)iVar9;
      }
    }
    puVar10 = 0xfebeb800u;
    store_signed32_clamped_between_upper_and_lower_d1cf6(local_2c,DAT_000af3f8,-DAT_000af3f8,&local_2c);
  }
  else {
    (*((uint16_t *)((uint8_t *)&local_2c + 0u))) = 0;
    cVar17 = '\0';
    cVar14 = '\0';
  }
  (*((undefined2 *)camry_host_ptr((uint32_t)(puVar10 + 0x696)))) = (undefined2)local_2c;
  bVar6 = bVar13 & 2;
  if ((bVar13 & 2) == 0) {
    bVar13 = bVar6;
    if (cVar12 == 'Z') {
      bVar13 = 0x5a;
    }
    bVar15 = bVar6;
    if (cVar14 == 'Z') {
      bVar15 = 0x5a;
    }
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar10 + (uint32_t)(0x691))))) = bVar13;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar10 + (uint32_t)(0x690))))) = bVar15;
    if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar10 + (uint32_t)(0x38a7))))) == '\x01') {
      bVar6 = 0x5a;
    }
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar10 + (uint32_t)(0x692))))) = bVar6;
    cVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar10 + (uint32_t)(0x38a5)))));
joined_r0x000be9f4:
    if (cVar1 != '\x01') {
      uVar7 = 0;
      goto LAB_000be9fa;
    }
  }
  else {
    if ((cVar16 == 'Z') || (cVar12 == 'Z')) {
      uVar7 = 0x5a;
    }
    else {
      uVar7 = 0;
    }
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar10 + (uint32_t)(0x691))))) = uVar7;
    if ((cVar17 == 'Z') || (cVar14 == 'Z')) {
      uVar7 = 0x5a;
    }
    else {
      uVar7 = 0;
    }
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar10 + (uint32_t)(0x690))))) = uVar7;
    if ((cVar3 == '\x01') || (cVar4 == '\x01')) {
      uVar7 = 0x5a;
    }
    else {
      uVar7 = 0;
    }
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar10 + (uint32_t)(0x692))))) = uVar7;
    if (cVar2 != '\x01') goto joined_r0x000be9f4;
  }
  uVar7 = 0x5a;
LAB_000be9fa:
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar10 + (uint32_t)(0x693))))) = uVar7;
  uVar7 = 0;
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar10 + (uint32_t)(0x68c))))) == '\x01') {
    uVar7 = 0x5a;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar10 + (uint32_t)(0x694))))) = uVar7;
  return;
}

void publish_first_fixed_received_marker(void)

{
  DAT_febebed4 = 0x55aaaa55;
  DAT_febebe9d = 0;
  DAT_febebeb3 = 0;
  DAT_febebea7 = 0x5a;
  return;
}

void publish_second_fixed_received_marker(void)

{
  DAT_febebed8 = 0x55aaaa55;
  DAT_febebe9e = 0;
  DAT_febebeb4 = 0;
  DAT_febebea8 = 0x5a;
  return;
}

void initialize_fixed_received_markers(void)

{
  publish_first_fixed_received_marker();
  publish_second_fixed_received_marker();
  return;
}

void return_only_stub_bea54(void)

{
  return;
}

void qualify_received_scalar_startup(void)

{
  if (DAT_febebea2 == '\0') {
    DAT_febebeac = 0;
    if (published_internal_source_admission_state < 2) {
      if (DAT_febebec4 < DAT_000af406) {
        DAT_febebec4 = DAT_febebec4 + 1;
      }
      else {
        DAT_febebea2 = 'Z';
        DAT_febebe98 = 0;
      }
    }
    else {
      DAT_febebec4 = 0;
    }
  }
  DAT_febebead = 0;
  DAT_febebeae = DAT_febebe98;
  return;
}

void qualify_received_channel_b_startup(void)

{
  if (DAT_febebea3 == '\0') {
    if (((published_internal_source_admission_state < 2) && (DAT_febef028 == '\0')) &&
       (DAT_febef02b == '\x01')) {
      if (DAT_febebebc < DAT_000af3fe) {
        DAT_febebebc = DAT_febebebc + 1;
      }
      else {
        DAT_febebea3 = 'Z';
        DAT_febebe99 = DAT_febebea3;
      }
    }
    else {
      DAT_febebebc = 0;
    }
  }
  DAT_febebeaf = 0;
  return;
}

void qualify_received_channel_c_startup(void)

{
  if (DAT_febebea4 == '\0') {
    if ((published_internal_source_admission_state < 2) && (DAT_febef060 == '\0')) {
      if (DAT_febebebe < DAT_000af400) {
        DAT_febebebe = DAT_febebebe + 1;
      }
      else {
        DAT_febebea4 = 'Z';
        DAT_febebe9a = DAT_febebea4;
      }
    }
    else {
      DAT_febebebe = 0;
    }
  }
  DAT_febebeb0 = 0;
  return;
}

void qualify_received_channel_d_startup(void)

{
  if (DAT_febebea5 == '\0') {
    if ((published_internal_source_admission_state < 2) && (DAT_febef069 == '\0')) {
      if (DAT_febebec0 < DAT_000af402) {
        DAT_febebec0 = DAT_febebec0 + 1;
      }
      else {
        DAT_febebea5 = 'Z';
        DAT_febebe9b = DAT_febebea5;
      }
    }
    else {
      DAT_febebec0 = 0;
    }
  }
  DAT_febebeb2 = DAT_febebe9b;
  return;
}

void qualify_received_channel_e_startup(void)

{
  if (DAT_febebea6 == '\0') {
    if ((published_internal_source_admission_state < 2) && (DAT_febef04c == '\0')) {
      if (DAT_febebec2 < DAT_000af404) {
        DAT_febebec2 = DAT_febebec2 + 1;
      }
      else {
        DAT_febebea6 = 'Z';
        DAT_febebe9c = DAT_febebea6;
      }
    }
    else {
      DAT_febebec2 = 0;
    }
  }
  DAT_febebeb1 = DAT_febebe9c;
  return;
}

void publish_received_channel_f_defaults(void)

{
  DAT_febebe9f = 0x5a;
  DAT_febebeb6 = 0x5a;
  return;
}

void publish_received_channel_g_default(void)

{
  DAT_febebea0 = 0x5a;
  return;
}

void publish_received_channel_h_default(void)

{
  DAT_febebea1 = 0x5a;
  return;
}

void publish_fixed_received_channel_defaults(void)

{
  publish_received_channel_f_defaults();
  publish_received_channel_g_default();
  publish_received_channel_h_default();
  return;
}

void clear_fixed_received_metadata(void)

{
  DAT_febebeb8 = 0;
  DAT_febebeb5 = 0;
  return;
}

void qualify_received_paired_channel_startup(void)

{
  if (DAT_febebebb == '\0') {
    if ((published_internal_source_admission_state < 2) &&
       ((DAT_febef148 == '\0' || (DAT_febef149 == '\0')))) {
      if (DAT_febebed0 < DAT_000af40e) {
        DAT_febebed0 = DAT_febebed0 + 1;
      }
      else {
        DAT_febebebb = 'Z';
        DAT_febebeba = DAT_febebebb;
      }
    }
    else {
      DAT_febebed0 = 0;
    }
  }
  DAT_febebeb7 = DAT_febebeba;
  return;
}

void publish_received_startup_delay_default(void)

{
  DAT_febebead = 0;
  return;
}

void update_delayed_received_startup_qualification(void)

{
  uint32_t puVar1;
  ushort uVar2;
  
  uVar2 = received_qualification_startup_count;
  puVar1 = 0xfebeb800u;
  if (received_qualification_startup_count < DAT_000af408) {
    publish_received_startup_delay_default();
    uVar2 = uVar2 + 1;
  }
  else {
    puVar1 = 0xfebeb800u;
    qualify_received_scalar_startup();
    qualify_received_channel_b_startup();
    qualify_received_channel_c_startup();
    qualify_received_channel_d_startup();
    qualify_received_channel_e_startup();
    publish_fixed_received_channel_defaults();
    clear_fixed_received_metadata();
    qualify_received_paired_channel_startup();
  }
  publish_first_fixed_received_marker();
  publish_second_fixed_received_marker();
  (*((ushort *)camry_host_ptr((uint32_t)(puVar1 + 0x6c6)))) = uVar2;
  return;
}

void return_only_stub_beccc(void)

{
  return;
}

void return_only_stub_becce(void)

{
  return;
}

void publish_admission_and_f093_f013_clear_ready_becd0(void)

{
  DAT_febebedd = 0;
  if (((published_internal_source_admission_state < 2) && (DAT_febef093 == '\0')) &&
     (DAT_febef013 == '\0')) {
    DAT_febebedd = 0x5a;
  }
  return;
}

void classify_bedc_status_and_scale_capped_f1b6_becf4(void)

{
  uint32_t puVar1;
  ushort uStack_6;
  
  puVar1 = 0xfebeb800u;
  uStack_6 = DAT_febef1b6;
  if (DAT_febeb218 != 0x5aa5a55a) {
    if ((DAT_febebedd == 'Z') && (DAT_febef002 == '\0')) {
      DAT_febebedc = 0x11;
      goto LAB_000bed6a;
    }
    if (((((DAT_febef013 != '\x02' && DAT_febef013 != '\x03') &&
          (published_internal_source_admission_state != '\x03')) &&
         ((DAT_febef093 >> 1 & 1) == 0)) &&
        (((DAT_febeb1ce != 'Z' && (DAT_febef0b3 != 'Z')) || ((DAT_febef093 & 1) == 0)))) &&
       (DAT_febef002 != 'Z')) {
      DAT_febebedc = 0x22;
      goto LAB_000bed6a;
    }
  }
  DAT_febebedc = 0x44;
LAB_000bed6a:
  store_unsigned16_minimum_d1d5c(DAT_febef1b6,30000,&uStack_6);
  (*((short *)camry_host_ptr((uint32_t)(puVar1 + 0x6de)))) = (short)((uint)uStack_6 * 0x147b >> 0xc);
  return;
}

void refresh_bedd_ready_and_bedc_scaled_status_bed90(void)

{
  publish_admission_and_f093_f013_clear_ready_becd0();
  classify_bedc_status_and_scale_capped_f1b6_becf4();
  return;
}

void return_only_stub_beda0(void)

{
  return;
}

void reset_bee_accumulators_and_publish_bef0_11_marker_beda2(void)

{
  DAT_febebee4 = 0;
  DAT_febebee0 = 0;
  DAT_febebeec = 0;
  DAT_febebee2 = 0;
  DAT_febebee8 = 0;
  if (DAT_febebef0 == '\x11') {
    DAT_febebee0 = 0x5a;
  }
  DAT_febebee1 = 0;
  return;
}

void filter_bee4_sample_or_seed_from_bede_bedc4(void)

{
  uint8_t stack_record_16[22];
  uint32_t puVar1;
  char cVar2;
  
  cVar2 = DAT_febebee1;
  puVar1 = 0xfebeb800u;
  if (DAT_febebee1 == '\0') {
    (*((uint16_t *)(stack_record_16 + 0))) = DAT_febebede;
    (*((uint32_t *)(stack_record_16 + 2))) = (uint)DAT_febebede << 0x10;
    if (DAT_febebef0 == '\x11') {
      cVar2 = 'Z';
    }
  }
  else {
    struct { ushort first; ushort second; uint word; } sample;
    sample.first = DAT_febebee4;
    sample.second = DAT_febebede;
    sample.word = DAT_febebeec;
    puVar1 = 0xfebeb800u;
    filter_unsigned_sample_accumulator
              (&sample.first,(uint)DAT_000af410 * 100,((uint16_t *)(stack_record_16)),((uint32_t *)((stack_record_16 + 2))));
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x6e1))))) = cVar2;
  (*((ushort *)camry_host_ptr((uint32_t)(puVar1 + 0x6e4)))) = (*((uint16_t *)(stack_record_16 + 0)));
  (*((uint *)camry_host_ptr((uint32_t)(puVar1 + 0x6ec)))) = (*((uint32_t *)(stack_record_16 + 2)));
  return;
}

void select_and_filter_bee2_sample_with_override_bee2c(void)

{
  uint8_t stack_record_34[52];
  int iVar1;
  char cVar2;
  byte bVar3;
  char cVar4;
  uint32_t puVar5;
  char cVar6;
  
  cVar4 = DAT_febebef0;
  cVar6 = DAT_febebee0;
  bVar3 = DAT_febeb117;
  cVar2 = DAT_febeb116;
  puVar5 = 0xfebeb800u;
  (*((uint16_t *)(stack_record_34 + 2))) = DAT_febebee2;
  (*((uint32_t *)(stack_record_34 + 8))) = DAT_febebee8;
  if (DAT_febebef0 == '\x11') {
    if (DAT_febebee0 == 'Z') {
      (*((uint16_t *)(stack_record_34 + 14))) = DAT_febebee2;
      (*((uint16_t *)(stack_record_34 + 12))) = DAT_febebee4;
      (*((uint16_t *)(stack_record_34 + 16))) = DAT_000af416;
      (*((uint16_t *)(stack_record_34 + 18))) = DAT_000af418;
      puVar5 = 0xfebeb800u;
      limit_unsigned16_value_to_asymmetric_step_band_d1d1c(((uint16_t *)((stack_record_34 + 12))),((uint16_t *)(stack_record_34)));
    }
    else {
      (*((uint16_t *)(stack_record_34 + 0))) = DAT_febebee4;
    }
  }
  else {
    cVar6 = '\0';
    (*((uint16_t *)(stack_record_34 + 0))) = DAT_febebee2;
    if (DAT_febebef0 == 'D') {
      (*((uint16_t *)(stack_record_34 + 0))) = DAT_000af414;
    }
  }
  if (cVar2 == 'Z') {
    (*((uint16_t *)(stack_record_34 + 0))) = (ushort)bVar3 << 7;
  }
  (*((ushort *)camry_host_ptr((uint32_t)(puVar5 + 0x6e6)))) = (*((uint16_t *)(stack_record_34 + 0)));
  (*((uint32_t *)(stack_record_34 + 4))) = (uint)(*((uint16_t *)(stack_record_34 + 2))) - (uint)(*((uint16_t *)(stack_record_34 + 0)));
  store_saturated_signed32_absolute_d1194((*((uint32_t *)(stack_record_34 + 4))),((uint32_t *)((stack_record_34 + 4))));
  iVar1 = (*((uint32_t *)(stack_record_34 + 4))) - DAT_000af41a;
  if (iVar1 < 0 == ((int)(*((uint32_t *)(stack_record_34 + 4))) < 0 && -1 < iVar1) && (*((uint32_t *)(stack_record_34 + 4))) != DAT_000af41a) {
    (*((uint16_t *)(stack_record_34 + 22))) = (*((uint16_t *)(stack_record_34 + 0)));
    (*((uint16_t *)(stack_record_34 + 20))) = (*((uint16_t *)(stack_record_34 + 2)));
    (*((uint32_t *)(stack_record_34 + 24))) = (*((uint32_t *)(stack_record_34 + 8)));
    filter_unsigned_sample_accumulator
              (((uint16_t *)((stack_record_34 + 20))),(uint)DAT_000af412 * 100,((uint16_t *)((stack_record_34 + 2))),((uint32_t *)((stack_record_34 + 8))));
  }
  else {
    (*((uint16_t *)(stack_record_34 + 2))) = (*((uint16_t *)(stack_record_34 + 0)));
    (*((uint32_t *)(stack_record_34 + 8))) = (uint)(*((uint16_t *)(stack_record_34 + 0))) << 0x10;
    if (cVar4 == '\x11') {
      cVar6 = 'Z';
    }
  }
  (*((ushort *)camry_host_ptr((uint32_t)(puVar5 + 0x6e2)))) = (*((uint16_t *)(stack_record_34 + 2)));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar5 + (uint32_t)(0x6e0))))) = cVar6;
  (*((uint *)camry_host_ptr((uint32_t)(puVar5 + 0x6e8)))) = (*((uint32_t *)(stack_record_34 + 8)));
  return;
}

void update_bee4_and_bee2_sample_filters_bef10(void)

{
  filter_bee4_sample_or_seed_from_bede_bedc4();
  select_and_filter_bee2_sample_with_override_bee2c();
  return;
}

void return_only_stub_bef20(void)

{
  return;
}

void initialize_bef0_status_and_clear_two_requests_bef22(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  
  DAT_febebef0 = 0x11;
  iVar3 = 0;
  do {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebebef1u + (uint32_t)(iVar3) * 1u)))) = 0;
    iVar2 = iVar3 + 1;
    iVar1 = iVar3 + -1;
    iVar3 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  return;
}

void merge_bedc_status_with_two_bef1_requests_bef3e(void)

{
  int iVar1;
  int iVar2;
  char cVar3;
  int iVar4;
  
  cVar3 = DAT_febebedc;
  if (((DAT_febebedc != '\x11') && (DAT_febebedc != 'D')) &&
     (cVar3 = DAT_febebef0, DAT_febebef0 != 'D')) {
    cVar3 = '\"';
  }
  iVar4 = 0;
  do {
    if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebebef1u + (uint32_t)(iVar4) * 1u)))) != '\0') {
      cVar3 = 'D';
    }
    iVar2 = iVar4 + 1;
    iVar1 = iVar4 + -1;
    iVar4 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  DAT_febebef0 = cVar3;
  return;
}

void set_indexed_bef1_request_to_5a_bef80(uint param_1)

{
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebebef1u + (uint32_t)(param_1 & 0xff) * 1u)))) = 0x5a;
  return;
}

void clear_indexed_bef1_request_bef8e(uint param_1)

{
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebebef1u + (uint32_t)(param_1 & 0xff) * 1u)))) = 0;
  return;
}

void return_only_stub_bef98(void)

{
  return;
}

void return_only_stub_bef9a(void)

{
  return;
}

void snapshot_three_status_flags_and_group16_bef9c(void)

{
  uint32_t puVar1;
  uchar uVar2;
  bool bVar3;
  
  puVar1 = 0xfebeb800u;
  if ((DAT_febef09e == '\x01') || (DAT_febef0a6 == '\x01')) {
    bVar3 = true;
  }
  else {
    bVar3 = DAT_febef0a7 == '\x01';
  }
  uVar2 = get_grouped_status_byte(0x16);
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x6f4))))) = bVar3;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(0x6f5))))) = uVar2;
  return;
}

void return_only_stub_befd2(void)

{
  return;
}

void return_only_stub_befd4(void)

{
  return;
}

void scale_and_bound_two_inputs_into_bf00_difference_befd6(void)

{
  char cVar1;
  char cVar2;
  char cVar3;
  char cVar4;
  undefined1 uVar5;
  undefined *puVar6;
  undefined *puVar7;
  undefined *puVar8;
  undefined4 local_18;
  
  cVar4 = DAT_febef0b0;
  cVar3 = DAT_febef0af;
  cVar2 = DAT_febef0ae;
  cVar1 = DAT_febef0ad;
  puVar7 = ((undefined *)camry_host_ptr(0xfebeb800u));
  if (DAT_febebef5 == 'Z') {
    local_18 = 0;
    DAT_febebef9 = 0;
    DAT_febebef8 = 0;
  }
  else {
    puVar8 = ((undefined *)camry_host_ptr((uint32_t)((((int)(int16_t)DAT_febef1c0) * 1999) / 0x100)));
    puVar6 = ((undefined *)camry_host_ptr((uint32_t)((((int)(int16_t)DAT_febef1ca) * 0x3e77) / 0x100)));
    puVar7 = ((void *)camry_host_ptr((uint32_t)(PTR_DAT_000af420)));
    if (((int)camry_host_addr(puVar8) - (int)PTR_DAT_000af420 < 0 ==
         ((int)camry_host_addr(puVar8) < 0 != (int)PTR_DAT_000af420 < 0 &&
         (int)PTR_DAT_000af420 < 0 == (int)camry_host_addr(puVar8) - (int)PTR_DAT_000af420 < 0) &&camry_host_addr(puVar8)!= PTR_DAT_000af420) ||
       (puVar7 = (undefined *)-(int)PTR_DAT_000af420,
       (int)camry_host_addr((puVar8 + (int)PTR_DAT_000af420)) < 0 !=
       ((int)camry_host_addr(puVar8) < 0 != (int)camry_host_addr(puVar7) < 0 &&
       (int)camry_host_addr(puVar7) < 0 == (int)camry_host_addr((puVar8 + (int)PTR_DAT_000af420)) < 0))) {
      puVar8 = puVar7;
      DAT_febebef9 = 0x5a;
    }
    puVar7 = ((void *)camry_host_ptr((uint32_t)(PTR_DAT_000af41c)));
    if (((int)camry_host_addr(puVar6) - (int)PTR_DAT_000af41c < 0 ==
         ((int)camry_host_addr(puVar6) < 0 != (int)PTR_DAT_000af41c < 0 &&
         (int)PTR_DAT_000af41c < 0 == (int)camry_host_addr(puVar6) - (int)PTR_DAT_000af41c < 0) &&camry_host_addr(puVar6)!= PTR_DAT_000af41c) ||
       (puVar7 = (undefined *)-(int)PTR_DAT_000af41c,
       (int)camry_host_addr((puVar6 + (int)PTR_DAT_000af41c)) < 0 !=
       ((int)camry_host_addr(puVar6) < 0 != (int)camry_host_addr(puVar7) < 0 &&
       (int)camry_host_addr(puVar7) < 0 == (int)camry_host_addr((puVar6 + (int)PTR_DAT_000af41c)) < 0))) {
      puVar6 = puVar7;
      DAT_febebef8 = 0x5a;
    }
    puVar7 = ((undefined *)camry_host_ptr(0xfebeb800u));
    store_signed32_clamped_between_upper_and_lower_d1cf6((int)camry_host_addr(puVar6) - (int)camry_host_addr(puVar8),PTR_LAB_000af424,-(int)PTR_LAB_000af424,&local_18);
  }
  *(undefined4 *)(puVar7 + 0x700) = local_18;
  if ((cVar2 == '\x01') || (cVar4 == '\x01')) {
    uVar5 = 0x5a;
  }
  else {
    uVar5 = 0;
  }
  puVar7[0x6fa] = uVar5;
  if ((cVar1 == '\x01') || (cVar3 == '\x01')) {
    uVar5 = 0x5a;
  }
  else {
    uVar5 = 0;
  }
  puVar7[0x6fb] = uVar5;
  uVar5 = 0;
  if (puVar7[0x6f4] == '\x01') {
    uVar5 = 0x5a;
  }
  puVar7[0x6fc] = uVar5;
  return;
}
