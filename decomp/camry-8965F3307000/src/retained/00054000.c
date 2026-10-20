#include "common.h"

void return_only_stub_5423e(void)

{
  return;
}

void return_only_stub_54240(void)

{
  return;
}

void return_only_stub_54242(void)

{
  return;
}

void build_diagnostic_capture_default(F33DiagnosticCapture *output)

{
  undefined2 uVar1;
  uchar uVar2;
  uint32_t puVar3;
  F33DiagnosticApplicationSample local_40;
  
  puVar3 = 0xfebeb800u;
  snapshot_diagnostic_application(&local_40,0x32);
  *(undefined4 *)output->profile_prefix = (*((undefined4 *)camry_host_ptr((uint32_t)(puVar3 + -0x517c))));
  *(undefined2 *)(output->profile_prefix + 8) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x515c))));
  output->profile_prefix[0x42] = local_40.raw[0];
  *(undefined2 *)(output->profile_prefix + 4) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x50f2))));
  *(undefined2 *)(output->profile_prefix + 6) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x50dc))));
  *(undefined2 *)(output->profile_prefix + 10) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x5148))));
  *(undefined2 *)(output->profile_prefix + 0xc) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x5158))));
  *(undefined2 *)(output->profile_prefix + 0xe) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x50f4))));
  *(undefined2 *)(output->profile_prefix + 0x10) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x5188))));
  *(undefined2 *)(output->profile_prefix + 0x12) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x5186))));
  *(undefined2 *)(output->profile_prefix + 0x14) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x5184))));
  *(undefined2 *)(output->profile_prefix + 0x16) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x5182))));
  *(undefined2 *)(output->profile_prefix + 0x18) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x5180))));
  *(undefined2 *)(output->profile_prefix + 0x1a) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x517e))));
  *(undefined2 *)(output->profile_prefix + 0x1c) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x51ac))));
  *(undefined2 *)(output->profile_prefix + 0x1e) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x51aa))));
  *(undefined2 *)(output->profile_prefix + 0x20) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x51a8))));
  *(undefined2 *)(output->profile_prefix + 0x22) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x51a6))));
  *(undefined2 *)(output->profile_prefix + 0x24) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x51a4))));
  *(undefined2 *)(output->profile_prefix + 0x26) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x51a2))));
  *(undefined2 *)(output->profile_prefix + 0x28) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x535e))));
  *(undefined2 *)(output->profile_prefix + 0x2a) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x535c))));
  *(undefined2 *)(output->profile_prefix + 0x2c) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x535a))));
  *(undefined2 *)(output->profile_prefix + 0x2e) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x5358))));
  *(undefined2 *)(output->profile_prefix + 0x30) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x5356))));
  *(undefined2 *)(output->profile_prefix + 0x32) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x5354))));
  *(undefined2 *)(output->profile_prefix + 0x34) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x5152))));
  *(undefined2 *)(output->profile_prefix + 0x36) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x5150))));
  *(undefined2 *)(output->profile_prefix + 0x38) = (*((uint16_t *)((uint8_t *)&local_40 + 10u)));
  *(undefined2 *)(output->profile_prefix + 0x3a) = (*((uint16_t *)((uint8_t *)&local_40 + 12u)));
  *(undefined2 *)(output->profile_prefix + 0x3c) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x50da))));
  *(undefined2 *)(output->profile_prefix + 0x3e) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x5146))));
  uVar1 = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x3aba))));
  output->profile_prefix[0x46] = '\0';
  output->profile_prefix[0x47] = '\0';
  *(undefined2 *)(output->profile_prefix + 0x40) = uVar1;
  *(undefined2 *)(output->profile_prefix + 0x44) = (*((uint16_t *)((uint8_t *)&local_40 + 24u)));
  output->profile_prefix[0x43] = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x3814)))));
  output->extended_prefix[5] = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x37fa)))));
  *(undefined2 *)output->extended_prefix = (*((uint16_t *)((uint8_t *)&local_40 + 14u)));
  *(undefined2 *)(output->extended_prefix + 2) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x3a32))));
  output->extended_prefix[4] = local_40.raw[1];
  output->extended_prefix[0xc] = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x3abc)))));
  output->extended_prefix[8] = local_40.raw[2];
  *(undefined2 *)(output->extended_prefix + 6) = (*((uint16_t *)((uint8_t *)&local_40 + 18u)));
  output->extended_prefix[9] = local_40.raw[3];
  *(undefined2 *)(output->extended_prefix + 10) = (*((uint16_t *)((uint8_t *)&local_40 + 20u)));
  output->extended_prefix[0xd] = local_40.raw[4];
  *(undefined2 *)(output->extended_prefix + 0xe) = (*((uint16_t *)((uint8_t *)&local_40 + 22u)));
  *(undefined2 *)(output->extended_prefix + 0x10) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x530e))));
  *(undefined2 *)(output->extended_prefix + 0x12) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x530c))));
  *(undefined2 *)(output->extended_prefix + 0x14) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x530a))));
  *(undefined2 *)(output->extended_prefix + 0x16) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x5308))));
  *(undefined2 *)(output->extended_prefix + 0x1a) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x3766))));
  *(undefined2 *)(output->extended_prefix + 0x1c) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x37b6))));
  *(undefined2 *)(output->extended_prefix + 0x1e) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x37a0))));
  *(undefined2 *)(output->extended_prefix + 0x20) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x379e))));
  output->extended_prefix[0x22] = local_40.raw[5];
  output->selected_sample = (*((uint16_t *)((uint8_t *)&local_40 + 26u)));
  output->extended_prefix[0x23] = '\x11';
  *(undefined2 *)output->extended_middle = (*((uint16_t *)((uint8_t *)&local_40 + 16u)));
  *(undefined4 *)(output->extended_middle + 2) = (*((uint32_t *)((uint8_t *)&local_40 + 32u)));
  output->extended_middle[6] = local_40.raw[6];
  output->extended_middle[7] = local_40.raw[7];
  *(undefined4 *)(output->extended_middle + 0xe) = (*((uint32_t *)((uint8_t *)&local_40 + 36u)));
  output->extended_tail[10] = local_40.raw[0x28];
  output->extended_tail[0xb] = local_40.raw[0x29];
  output->extended_tail[0xc] = local_40.raw[0x2a];
  output->extended_tail[0xd] = local_40.raw[0x2b];
  output->extended_tail[0xe] = local_40.raw[0x2c];
  output->extended_tail[0xf] = local_40.raw[0x2d];
  output->extended_middle[10] = local_40.raw[8];
  *(undefined2 *)(output->extended_middle + 8) = (*((uint16_t *)((uint8_t *)&local_40 + 28u)));
  output->extended_middle[0xb] = local_40.raw[9];
  *(undefined2 *)(output->extended_middle + 0xc) = (*((uint16_t *)((uint8_t *)&local_40 + 30u)));
  output->extended_tail[0x10] = local_40.raw[0x30];
  *(undefined2 *)(output->extended_prefix + 0x18) = (*((uint16_t *)((uint8_t *)&local_40 + 46u)));
  *(undefined2 *)(output->extended_middle + 0x12) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x5200))));
  *(undefined2 *)(output->extended_middle + 0x14) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x51fe))));
  *(undefined2 *)(output->extended_middle + 0x16) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x51f8))));
  *(undefined2 *)(output->extended_middle + 0x18) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x51fc))));
  *(undefined2 *)(output->extended_middle + 0x1a) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x51fa))));
  *(undefined2 *)(output->extended_middle + 0x1c) = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x51f6))));
  output->ecu_thermal_estimate = (*((short *)camry_host_ptr((uint32_t)((0xffffb77au + (uint32_t)((int)puVar3))))));
  output->motor_thermal_estimate = (*((short *)camry_host_ptr((uint32_t)((0xffffb77cu + (uint32_t)((int)puVar3))))));
  output->ecu_thermal_source = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffb76cu + (uint32_t)((int)puVar3) * 1u))));
  uVar2 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffb76du + (uint32_t)((int)puVar3) * 1u))));
  output->extended_tail[0x11] = '\0';
  output->motor_thermal_active = uVar2;
  *(undefined2 *)output->extended_tail = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + -0x3a2a))));
  *(undefined4 *)(output->extended_tail + 2) = (*((undefined4 *)camry_host_ptr((uint32_t)(puVar3 + -0x3568))));
  *(undefined4 *)(output->extended_tail + 6) = (*((undefined4 *)camry_host_ptr((uint32_t)(puVar3 + -0x3564))));
  return;
}

void return_only_stub_54486(void)

{
  return;
}

uint32_t restore_eighteen_counters_and_ten_values_from_nvm4_54488(void)

{
  uint32_t camry_r10_result;
  uint8_t stack_record_40[64];
  int iVar1;
  int iVar2;
  undefined2 uVar3;
  uint *puVar4;
  int iVar5;
  uint uVar6;
  uint32_t puVar7;
  
  puVar4 = ((uint32_t *)(stack_record_40));
  puVar7 = ((uint32_t)(0x21404u));
  do {
    uVar3 = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar7))));
    puVar7 = ((int)puVar7 + 2);
    *(undefined2 *)puVar4 = uVar3;
    puVar4 = ((uint *)camry_host_ptr((uint32_t)((int)camry_host_addr(puVar4) + 2)));
  } while (puVar7 != 0x2143cu);
  uVar6 = (camry_r10_result = nvm_get_record(4, camry_host_addr(((uint32_t *)(stack_record_40)))));
  iVar5 = 0;
  if (uVar6 == 0x11) {
    do {
      iVar2 = iVar5 + 1;
      *(undefined2 *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe860au + (uint32_t)(iVar5 * 2) * 1u)))) = 0;
      iVar1 = iVar5 + -0x11;
      iVar5 = iVar2;
    } while (((iVar1 < 0) || (iVar2 < 0)));
    iVar5 = 0;
    do {
      iVar2 = iVar5 + 1;
      *(undefined2 *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe862eu + (uint32_t)(iVar5 * 2) * 1u)))) = 0;
      iVar1 = iVar5 + -9;
      iVar5 = iVar2;
    } while (((iVar1 < 0) || (iVar2 < 0)));
  }
  else {
    do {
      iVar2 = iVar5 + 1;
      iVar1 = iVar5 + -0x11;
      *(undefined2 *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe860au + (uint32_t)(iVar5 * 2) * 1u)))) = (*((undefined2 *)camry_host_ptr((uint32_t)((int)camry_host_addr(((uint32_t *)(stack_record_40))) + iVar5 * 2))));
      iVar5 = iVar2;
    } while (((iVar1 < 0) || (iVar2 < 0)));
    iVar5 = 0;
    do {
      iVar2 = iVar5 + 1;
      iVar1 = iVar5 + -9;
      *(undefined2 *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe862eu + (uint32_t)(iVar5 * 2) * 1u)))) = ((uint16_t *)((stack_record_40 + 36)))[iVar5];
      iVar5 = iVar2;
    } while (((iVar1 < 0) || (iVar2 < 0)));
  }
  return camry_r10_result;
}

uint32_t snapshot_two_halfword_arrays_to_nvm4_5450e(void)

{
  uint32_t camry_r10_result;
  uint8_t stack_record_44[68];
  int iVar1;
  int iVar2;
  int iVar3;
  uint saved_mask;
  
  saved_mask = (camry_r10_result = priority_mask_enter(0xff00));
  iVar3 = 0;
  do {
    iVar2 = iVar3 + 1;
    iVar1 = iVar3 + -0x11;
    (*((undefined2 *)camry_host_ptr((uint32_t)((int)camry_host_addr(((uint32_t *)(stack_record_44))) + iVar3 * 2)))) = *(undefined2 *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe860au + (uint32_t)(iVar3 * 2) * 1u))));
    iVar3 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  iVar3 = 0;
  do {
    iVar2 = iVar3 + 1;
    iVar1 = iVar3 + -9;
    ((uint16_t *)((stack_record_44 + 36)))[iVar3] = *(undefined2 *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe862eu + (uint32_t)(iVar3 * 2) * 1u))));
    iVar3 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  (camry_r10_result = nvm_set_record(4,((uint32_t *)(stack_record_44))));
  priority_mask_restore(saved_mask);
  return camry_r10_result;
}

void flush_dirty_counter_record4_and_poll_completion_54566(void)

{
  byte bVar1;
  byte bVar2;
  undefined1 uVar3;
  uint32_t puVar4;
  uint uVar5;
  undefined1 uVar6;
  char cVar7;
  
  uVar6 = DAT_febe8608;
  bVar2 = DAT_febe8607;
  cVar7 = DAT_febe8606;
  puVar4 = 0xfebeb800u;
  if (((DAT_febee821 == 'Z') || ((DAT_febe8607 >> 2 & 1) != 0)) && (DAT_febe8607 != 0)) {
    bVar1 = ~DAT_febe8607;
    puVar4 = 0xfebeb800u;
    uVar5 = priority_mask_enter(0xff00);
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x31f9))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x31f9))))) & bVar1;
    priority_mask_restore(uVar5);
    snapshot_two_halfword_arrays_to_nvm4_5450e();
    if ((bVar2 >> 2 & 1) == 0) goto LAB_000545ae;
    cVar7 = '\x01';
  }
  else {
LAB_000545ae:
    if (cVar7 == '\0') goto LAB_000545d2;
  }
  uVar5 = nvm_get_record_status(4);
  uVar3 = 0;
  if (((uVar5 & 0xf0) == 0x10) || (uVar3 = 0x55, (uVar5 & 0xf0) == 0x30)) {
    uVar6 = uVar3;
    cVar7 = '\0';
  }
LAB_000545d2:
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x31f8))))) = uVar6;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x31fa))))) = cVar7;
  return;
}

void increment_indexed_u16_counter_once_until_rearmed_545de(uint param_1)

{
  uint32_t puVar1;
  uint saved_mask;
  
  puVar1 = 0xfebeb800u;
  param_1 = param_1 & 0xff;
  if (param_1 < 0x12) {
    saved_mask = priority_mask_enter(0xff00);
    if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe85f4u + (uint32_t)(param_1) * 1u)))) == '\0') {
      if (*(short *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe860au + (uint32_t)(param_1 * 2) * 1u)))) != -1) {
        *(short *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe860au + (uint32_t)(param_1 * 2) * 1u)))) = *(short *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe860au + (uint32_t)(param_1 * 2) * 1u)))) + 1;
        (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x31f9))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x31f9))))) | 2;
      }
    }
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe85f4u + (uint32_t)(param_1) * 1u)))) = 'Z';
    priority_mask_restore(saved_mask);
  }
  return;
}

void set_indexed_u16_value_and_mark_record4_dirty_54632(uint param_1,undefined2 param_2)

{
  uint32_t puVar1;
  uint saved_mask;
  
  puVar1 = 0xfebeb800u;
  if ((param_1 & 0xff) < 10) {
    saved_mask = priority_mask_enter(0xff00);
    *(undefined2 *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe862eu + (uint32_t)((param_1 & 0xff) * 2) * 1u)))) = param_2;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x31f9))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x31f9))))) | 2;
    priority_mask_restore(saved_mask);
  }
  return;
}

uint clear_eighteen_counters_and_mark_forced_record4_write_54662(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  uint32_t puVar4;
  uint saved_mask;
  
  puVar4 = 0xfebeb800u;
  DAT_febe8608 = 0xaa;
  saved_mask = priority_mask_enter(0xff00);
  iVar3 = 0;
  do {
    iVar2 = iVar3 + 1;
    *(undefined2 *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe860au + (uint32_t)(iVar3 * 2) * 1u)))) = 0;
    iVar1 = iVar3 + -0x11;
    iVar3 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x31f9))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x31f9))))) | 4;
  priority_mask_restore(saved_mask);
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x31f8))))) = 0xa5;
  return saved_mask;
}

uint clear_counter_and_value_arrays_and_mark_forced_write_546a2(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  uint32_t puVar4;
  uint saved_mask;
  
  puVar4 = 0xfebeb800u;
  DAT_febe8608 = 0xaa;
  saved_mask = priority_mask_enter(0xff00);
  iVar3 = 0;
  do {
    iVar2 = iVar3 + 1;
    *(undefined2 *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe860au + (uint32_t)(iVar3 * 2) * 1u)))) = 0;
    iVar1 = iVar3 + -0x11;
    iVar3 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  iVar3 = 0;
  do {
    iVar2 = iVar3 + 1;
    *(undefined2 *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe862eu + (uint32_t)(iVar3 * 2) * 1u)))) = 0;
    iVar1 = iVar3 + -9;
    iVar3 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x31f9))))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x31f9))))) | 4;
  priority_mask_restore(saved_mask);
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar4 + (uint32_t)(-0x31f8))))) = 0xa5;
  return saved_mask;
}

undefined2 get_indexed_u16_counter_or_zero_546f2(uint param_1)

{
  if ((param_1 & 0xff) < 0x12) {
    return *(undefined2 *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe860au + (uint32_t)((param_1 & 0xff) * 2) * 1u))));
  }
  return 0;
}

undefined2 get_indexed_u16_value_or_zero_5470c(uint param_1)

{
  if ((param_1 & 0xff) < 10) {
    return *(undefined2 *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe862eu + (uint32_t)((param_1 & 0xff) * 2) * 1u))));
  }
  return 0;
}

uint clear_indexed_counter_rearm_byte_54724(uint param_1)

{
  uint32_t puVar1;
  uint saved_mask;
  
  puVar1 = 0xfebeb800u;
  saved_mask = priority_mask_enter(0xff00);
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)((param_1 & 0xff) - 0x320c))))) = 0;
  priority_mask_restore(saved_mask);
  return saved_mask;
}

void return_only_stub_54744(void)

{
  return;
}

uint32_t restore_twelve_counters_and_three_records_from_nvm14_54746(void)

{
  uint32_t camry_r10_result;
  uint8_t stack_record_38[56];
  int iVar1;
  int iVar2;
  int iVar3;
  uint *puVar4;
  int iVar5;
  uint uVar6;
  undefined4 uVar7;
  undefined4 *puVar8;
  
  puVar4 = ((uint32_t *)(stack_record_38));
  puVar8 = ((undefined *)camry_host_ptr(0x2143cu));
  do {
    uVar7 = *puVar8;
    puVar8 = puVar8 + 1;
    *puVar4 = uVar7;
    puVar4 = puVar4 + 1;
  } while (camry_host_addr(puVar8)!=((uint32_t)(0x2146cu)));
  uVar6 = (camry_r10_result = nvm_get_record(0xe, camry_host_addr(((uint32_t *)(stack_record_38)))));
  iVar5 = 0;
  if (uVar6 == 0x11) {
    do {
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe8644u + (uint32_t)(iVar5) * 1u)))) = 0;
      iVar2 = iVar5 + 1;
      iVar1 = iVar5 + -0xb;
      iVar5 = iVar2;
    } while (((iVar1 < 0) || (iVar2 < 0)));
    iVar5 = 0;
    do {
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe8662u + (uint32_t)(iVar5) * 1u)))) = 0;
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe8665u + (uint32_t)(iVar5) * 1u)))) = 0;
      (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe866cu + (uint32_t)(iVar5) * 2u)))) = 0;
      (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe8672u + (uint32_t)(iVar5) * 2u)))) = 0;
      (*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xfebe8678u + (uint32_t)(iVar5) * 4u)))) = 0;
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe8668u + (uint32_t)(iVar5) * 1u)))) = 0;
      iVar2 = iVar5 + 1;
      iVar1 = iVar5 + -2;
      iVar5 = iVar2;
    } while (((iVar1 < 0) || (iVar2 < 0)));
  }
  else {
    do {
      iVar2 = iVar5 + 1;
      iVar1 = iVar5 + -0xb;
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe8644u + (uint32_t)(iVar5) * 1u)))) = (*((undefined1 *)camry_host_ptr((uint32_t)((int)camry_host_addr(((uint32_t *)(stack_record_38))) + iVar5))));
      iVar5 = iVar2;
    } while (((iVar1 < 0) || (iVar2 < 0)));
    iVar5 = 0;
    do {
      iVar3 = iVar5 * 0xc;
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe8662u + (uint32_t)(iVar5) * 1u)))) = ((uint8_t *)((stack_record_38 + 12)))[iVar3];
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe8665u + (uint32_t)(iVar5) * 1u)))) = ((uint8_t *)((stack_record_38 + 12)))[iVar3 + 1];
      (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe866cu + (uint32_t)(iVar5) * 2u)))) = *(undefined2 *)(((uint8_t *)((stack_record_38 + 12))) + iVar3 + 2);
      (*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xfebe8678u + (uint32_t)(iVar5) * 4u)))) = *(undefined4 *)(((uint8_t *)((stack_record_38 + 12))) + iVar3 + 4);
      (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe8672u + (uint32_t)(iVar5) * 2u)))) = ((uint16_t *)(stack_record_38 + 20))[iVar5 * 6];
      iVar2 = iVar5 + 1;
      iVar1 = iVar5 + -2;
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe8668u + (uint32_t)(iVar5) * 1u)))) = ((uint8_t *)((stack_record_38 + 22)))[iVar3];
      iVar5 = iVar2;
    } while (((iVar1 < 0) || (iVar2 < 0)));
  }
  return camry_r10_result;
}

void prepend_selected_state_record_and_increment_byte_counter_54818(byte param_1,undefined1 *param_2)

{
  int iVar1;
  ushort uVar2;
  undefined1 uVar3;
  undefined2 uVar4;
  undefined4 uVar5;
  undefined1 uVar6;
  ushort uVar7;
  int iVar8;
  int iVar9;
  char cVar10;
  int iVar11;
  
  uVar5 = DAT_febee90c;
  uVar4 = DAT_febee896;
  uVar3 = DAT_febee815;
  if (DAT_febee920 == 0x55aaaa55) {
    iVar9 = 4;
    uVar7 = DAT_febee890;
  }
  else {
    uVar7 = (ushort)DAT_febee811;
    iVar9 = 5;
  }
  if (param_1 < 2) goto LAB_00054876;
  if (param_1 == 2) {
    iVar11 = 0;
    iVar9 = 1;
    uVar7 = 0;
    goto LAB_000548b8;
  }
  if (param_1 < 4) {
    iVar9 = 1;
    iVar11 = iVar9;
LAB_0005487c:
    uVar7 = (ushort)iVar9;
  }
  else {
    uVar2 = DAT_febe66ba;
    if (param_1 == 4) {
      iVar9 = 2;
      iVar11 = iVar9;
    }
    else {
      if (param_1 < 9) {
LAB_00054876:
        iVar9 = 0;
        iVar11 = 0xff;
        goto LAB_0005487c;
      }
      if (param_1 == 9) {
        iVar9 = 3;
        iVar11 = iVar9;
      }
      else {
        if (param_1 < 0xb) {
          iVar11 = 5;
          iVar9 = 6;
          uVar7 = (ushort)((uint)DAT_febee892 * 100 >> 7);
          goto LAB_000548b8;
        }
        if (param_1 != 0xb) {
          if (param_1 == 0xf) {
            iVar11 = 4;
            goto LAB_000548b8;
          }
          goto LAB_00054876;
        }
        iVar9 = 8;
        iVar11 = 7;
        uVar2 = DAT_febe66b8;
      }
    }
    uVar7 = (ushort)((uint)uVar2 * 10 >> 8);
  }
LAB_000548b8:
  if (((DAT_febee825 == 'Z') || (DAT_febee827 == 'Z')) || (DAT_febee824 == 'Z')) {
    uVar6 = 2;
  }
  else {
    uVar6 = 1;
  }
  if (iVar11 != 0xff) {
    iVar8 = 2;
    do {
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe8662u + (uint32_t)(iVar8) * 1u)))) = (*((undefined1 *)camry_host_ptr((uint32_t)(iVar8 + -0x141799f))));
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe8665u + (uint32_t)(iVar8) * 1u)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe8664u + (uint32_t)(iVar8) * 1u))));
      (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe866cu + (uint32_t)(iVar8) * 2u)))) = *(undefined2 *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe866au + (uint32_t)(iVar8 * 2) * 1u))));
      (*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xfebe8678u + (uint32_t)(iVar8) * 4u)))) = *(undefined4 *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe8674u + (uint32_t)(iVar8 * 2) * 1u))));
      (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe8672u + (uint32_t)(iVar8) * 2u)))) = (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe8670u + (uint32_t)(iVar8) * 2u))));
      iVar1 = iVar8 + -1;
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe8668u + (uint32_t)(iVar8) * 1u)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe8667u + (uint32_t)(iVar8) * 1u))));
      iVar8 = iVar1;
    } while (0 < iVar1);
    cVar10 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe8644u + (uint32_t)(iVar11) * 1u))));
    if (((int8_t)cVar10) != -1) {
      cVar10 = cVar10 + '\x01';
    }
    DAT_febe8672 = uVar7;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe8644u + (uint32_t)(iVar11) * 1u)))) = cVar10;
    DAT_febe8662 = (undefined1)iVar9;
    DAT_febe8665 = uVar3;
    DAT_febe866c = uVar4;
    DAT_febe8678 = uVar5;
    DAT_febe8668 = uVar6;
    *param_2 = 0x5a;
  }
  return;
}

uint serialize_twelve_counters_and_three_records_to_nvm14_54950(void)

{
  uint8_t stack_record_34[52];
  int iVar1;
  int iVar2;
  int iVar3;
  undefined1 uVar4;
  int iVar5;
  
  iVar5 = 0;
  do {
    iVar2 = iVar5 + 1;
    iVar1 = iVar5 + -0xb;
    (*((undefined1 *)camry_host_ptr((uint32_t)((int)camry_host_addr(((uint32_t *)(stack_record_34))) + iVar5)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe8644u + (uint32_t)(iVar5) * 1u))));
    iVar5 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  iVar5 = 0;
  do {
    iVar3 = iVar5 * 0xc;
    ((uint8_t *)((stack_record_34 + 12)))[iVar3] = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe8662u + (uint32_t)(iVar5) * 1u))));
    ((uint8_t *)((stack_record_34 + 12)))[iVar3 + 1] = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe8665u + (uint32_t)(iVar5) * 1u))));
    *(undefined2 *)(((uint8_t *)((stack_record_34 + 12))) + iVar3 + 2) = (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe866cu + (uint32_t)(iVar5) * 2u))));
    *(undefined4 *)(((uint8_t *)((stack_record_34 + 12))) + iVar3 + 4) = (*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xfebe8678u + (uint32_t)(iVar5) * 4u))));
    (((uint16_t *)((stack_record_34 + 20))))[iVar5 * 6] = (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe8672u + (uint32_t)(iVar5) * 2u))));
    uVar4 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe8668u + (uint32_t)(iVar5) * 1u))));
    iVar2 = iVar5 + 1;
    ((uint8_t *)((stack_record_34 + 22)))[iVar3 + 1] = 0;
    iVar1 = iVar5 + -2;
    ((uint8_t *)((stack_record_34 + 22)))[iVar3] = uVar4;
    iVar5 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  return nvm_set_record(0xe,((uint32_t *)(stack_record_34)));
}

void capture_rising_counter_latches_and_persist_records_549c8(void)

{
  char cVar1;
  undefined8 uVar2;
  uint uVar3;
  char cStack_15;
  
  uVar2 = 0xfebeb800;
  if (DAT_febee820 == 'Z') {
    cStack_15 = '\0';
    uVar3 = 0;
    do {
      cVar1 = (*((char *)camry_host_ptr((uint32_t)(uVar3 + (int)uVar2 + -0x320c))));
      if ((cVar1 == 'Z') && ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe8650u + (uint32_t)(uVar3) * 1u)))) == '\0')) {
        prepend_selected_state_record_and_increment_byte_counter_54818(uVar3,&cStack_15);
      }
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe8650u + (uint32_t)(uVar3) * 1u)))) = cVar1;
      uVar3 = uVar3 + 1;
    } while (uVar3 < 0x12);
    if (cStack_15 == 'Z') {
      serialize_twelve_counters_and_three_records_to_nvm14_54950();
    }
  }
  return;
}

uint clear_twelve_counters_three_records_and_nvm14_54a24(void)

{
  uint8_t stack_record_34[52];
  int iVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  
  iVar4 = 0;
  do {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe8644u + (uint32_t)(iVar4) * 1u)))) = 0;
    (*((undefined1 *)camry_host_ptr((uint32_t)((int)camry_host_addr(((uint32_t *)(stack_record_34))) + iVar4)))) = 0;
    iVar2 = iVar4 + 1;
    iVar1 = iVar4 + -0xb;
    iVar4 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  iVar4 = 0;
  do {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe8662u + (uint32_t)(iVar4) * 1u)))) = 0;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe8665u + (uint32_t)(iVar4) * 1u)))) = 0;
    (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe866cu + (uint32_t)(iVar4) * 2u)))) = 0;
    (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe8672u + (uint32_t)(iVar4) * 2u)))) = 0;
    (*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xfebe8678u + (uint32_t)(iVar4) * 4u)))) = 0;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe8668u + (uint32_t)(iVar4) * 1u)))) = 0;
    iVar3 = iVar4 * 0xc;
    iVar2 = iVar4 + 1;
    iVar1 = iVar4 + -2;
    ((uint8_t *)((stack_record_34 + 12)))[iVar3] = 0;
    ((uint8_t *)((stack_record_34 + 12)))[iVar3 + 1] = 0;
    *(undefined2 *)(((uint8_t *)((stack_record_34 + 12))) + iVar3 + 2) = 0;
    *(undefined4 *)(((uint8_t *)((stack_record_34 + 12))) + iVar3 + 4) = 0;
    (((uint16_t *)((stack_record_34 + 20))))[iVar4 * 6] = 0;
    ((uint8_t *)((stack_record_34 + 22)))[iVar3] = 0;
    ((uint8_t *)((stack_record_34 + 22)))[iVar3 + 1] = 0;
    iVar4 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  return nvm_set_record(0xe,((uint32_t *)(stack_record_34)));
}

void __v850_copy_words_24(int param_1,int param_2)

{
  int iVar1;
  uint uVar2;
  
  uVar2 = 0;
  do {
    iVar1 = uVar2 * 4;
    uVar2 = uVar2 + 1;
    (*((undefined4 *)camry_host_ptr((uint32_t)(iVar1 + param_1)))) = (*((undefined4 *)camry_host_ptr((uint32_t)(iVar1 + param_2))));
  } while (uVar2 < 0x18);
  return;
}

void __v850_copy_words_8(int param_1,int param_2)

{
  int iVar1;
  uint uVar2;
  
  uVar2 = 0;
  do {
    iVar1 = uVar2 * 4;
    uVar2 = uVar2 + 1;
    (*((undefined4 *)camry_host_ptr((uint32_t)(iVar1 + param_1)))) = (*((undefined4 *)camry_host_ptr((uint32_t)(iVar1 + param_2))));
  } while (uVar2 < 8);
  return;
}

void initialize_dual96byte_and_twenty32byte_records_54ac6(void)

{
  int iVar1;
  undefined8 uVar2;
  int extraout_r6;
  uint uVar3;
  uint uVar4;
  
  uVar2 = 0xfebeb800;
  __v850_copy_words_24((int)((uint32_t)(0xfebe8684u)), ((uint32_t)(0x2a304u)));
  __v850_copy_words_24((int)uVar2 + -0x311c, 0x2a304);
  iVar1 = (int)uVar2;
  (*((undefined2 *)camry_host_ptr((uint32_t)(iVar1 + -0x317a)))) = 0x1111;
  uVar3 = 0;
  (*((undefined2 *)camry_host_ptr((uint32_t)(iVar1 + -0x311a)))) = 0x1111;
  (*((undefined2 *)camry_host_ptr((uint32_t)(iVar1 + -0x3136)))) = 1;
  (*((undefined2 *)camry_host_ptr((uint32_t)(iVar1 + -0x30d6)))) = 1;
  do {
    uVar4 = 0;
    do {
      __v850_copy_words_8((extraout_r6 = ((short)uVar3 * 5 + uVar4) * 0x20 + (int)uVar2 + -0x30bc), ((uint32_t)(0x2a2e4u)));
      (*((undefined2 *)camry_host_ptr((uint32_t)(extraout_r6 + 4)))) = 0x1111;
      uVar4 = uVar4 + 1;
      (*((undefined2 *)camry_host_ptr((uint32_t)(extraout_r6 + 2)))) = 0;
    } while (uVar4 < 5);
    uVar3 = uVar3 + 1;
  } while (uVar3 < 4);
  return;
}

void restore_nvm11_bitmaps_and_expand_fortyone_mapped_bits_54b2c(void)

{
  int iVar1;
  uint *puVar2;
  uint uVar3;
  uint uVar4;
  undefined4 uVar5;
  undefined4 *puVar6;
  uint local_18 [4];
  
  puVar2 = local_18;
  puVar6 = ((undefined *)camry_host_ptr(0x2146cu));
  do {
    uVar5 = *puVar6;
    puVar6 = puVar6 + 1;
    *puVar2 = uVar5;
    puVar2 = puVar2 + 1;
  } while (camry_host_addr(puVar6)!=((uint32_t)(0x2147cu)));
  uVar4 = nvm_get_record(0x11, camry_host_addr(local_18));
  uVar3 = 0;
  if (uVar4 == 0x10) {
    do {
      uVar4 = uVar3 + 1;
      *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe89f4u + (uint32_t)(uVar3 * 4) * 1u)))) = local_18[uVar3];
      *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe89fcu + (uint32_t)(uVar3 * 4) * 1u)))) = local_18[uVar3 + 2];
      uVar3 = uVar4;
    } while (uVar4 < 2);
  }
  else if (uVar4 == 0x11) {
    do {
      iVar1 = uVar3 * 4;
      uVar3 = uVar3 + 1;
      *(undefined4 *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe89f4u + (uint32_t)(iVar1) * 1u)))) = 0;
      *(undefined4 *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe89fcu + (uint32_t)(iVar1) * 1u)))) = 0;
    } while (uVar3 < 2);
  }
  else {
    do {
      iVar1 = uVar3 * 4;
      uVar3 = uVar3 + 1;
      *(undefined4 *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe89f4u + (uint32_t)(iVar1) * 1u)))) = 0;
      *(undefined4 *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe89fcu + (uint32_t)(iVar1) * 1u)))) = 0;
    } while (uVar3 < 2);
  }
  uVar3 = 0;
  do {
    if ((*(uint *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe89f4u + (uint32_t)((uVar3 >> 5) * 4) * 1u)))) >> (uVar3 & 0x1f) & 1) != 0) {
      iVar1 = (uint)((*((ushort *)camry_host_ptr((uint32_t)(&PTR_DAT_0002aace + uVar3)))) >> 5) * 4;
      *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe8a04u + (uint32_t)(iVar1) * 1u)))) =
           *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe8a04u + (uint32_t)(iVar1) * 1u)))) | 1 << ((*((ushort *)camry_host_ptr((uint32_t)(&PTR_DAT_0002aace + uVar3)))) & 0x1f);
    }
    uVar3 = uVar3 + 1;
  } while (uVar3 < 0x29);
  return;
}

undefined4 map_record_bank_to_nvm_selector_54bec(char param_1)

{
  undefined4 uVar1;
  
  uVar1 = 0x20;
  if (param_1 == '\0') {
    uVar1 = 0x14;
  }
  if (param_1 == '\x03') {
    uVar1 = 0x15;
  }
  if (param_1 == '\x02') {
    uVar1 = 0x17;
  }
  return uVar1;
}

uint32_t restore_valid_five_entry_bank_and_cursor_from_nvm_54c0a(uint param_1)

{
  uint32_t camry_r10_result;
  uint8_t stack_record_bc[188];
  uint *puVar1;
  undefined8 uVar2;
  uint uVar3;
  undefined4 uVar4;
  short sVar5;
  int iVar6;
  undefined4 *puVar7;
  short asStack_b8 [78];
  
  uVar2 = 0x23dfcfebeb800;
  puVar1 = stack_record_bc;
  param_1 = param_1 & 0xff;
  puVar7 = ((undefined *)camry_host_ptr(0x2147cu));
  do {
    uVar4 = *puVar7;
    puVar7 = puVar7 + 1;
    *puVar1 = uVar4;
    puVar1 = puVar1 + 1;
  } while (camry_host_addr(puVar7)!=((uint32_t)(0x21524u)));
  uVar3 = (camry_r10_result = map_record_bank_to_nvm_selector_54bec(param_1));
  if (uVar3 != 0x20) {
    uVar3 = (camry_r10_result = nvm_get_record(uVar3, camry_host_addr(stack_record_bc)));
    sVar5 = 0;
    if (uVar3 == 0x10) {
      iVar6 = 0x5a;
      uVar3 = 0;
      do {
        sVar5 = asStack_b8[uVar3 * 0x10];
        if (((sVar5 == 0) || (sVar5 == 0x4444)) || (sVar5 == 0x2222)) {
          iVar6 = 0;
          __v850_copy_words_8(((short)param_1 * 5 + uVar3) * 0x20 + (int)uVar2 + -0x30bc, camry_host_addr((uint8_t *)stack_record_bc + uVar3 * 32));
        }
        uVar3 = uVar3 + 1;
      } while (uVar3 < 5);
      if (iVar6 == 0x5a) {
        sVar5 = 0;
        stack_record_bc[160] = '\0';
      }
      else {
        uVar3 = 4;
        if (stack_record_bc[160] != '\0') {
          uVar3 = (uint)(byte)(stack_record_bc[160] - 1);
        }
        sVar5 = asStack_b8[uVar3 * 0x10 + -1];
      }
    }
    else {
      stack_record_bc[160] = '\0';
      (*((uint32_t *)(stack_record_bc + 164))) = 0;
    }
    (*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xfebe89e4u + (uint32_t)(param_1) * 4u)))) = (*((uint32_t *)(stack_record_bc + 164)));
    *(short *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe89dau + (uint32_t)(param_1 * 2) * 1u)))) = sVar5;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe89c6u + (uint32_t)(param_1) * 1u)))) = stack_record_bc[160];
    if (param_1 == 0) {
      clear_febe505c_word_6a17a();
    }
    if (param_1 == 2) {
      reset_event27_occurrence_counter_56fbc();
    }
  }
  return camry_r10_result;
}

uint32_t restore_dual_capture_records_and_select_newer_generation_54ce2(void)

{
  uint32_t camry_r10_result;
  uint8_t stack_record_c8[200];
  camry_fill_bytes(stack_record_c8, sizeof stack_record_c8);
  undefined4 *puVar1;
  undefined4 *puVar2;
  uint32_t puVar3;
  undefined4 *puVar4;
  uint uVar5;
  undefined4 uVar6;
  ushort uVar7;
  undefined4 *puVar8;
  ushort record_counter;
  
  puVar3 = 0xfebeb800u;
  puVar2 = ((uint32_t *)(stack_record_c8));
  puVar4 = ((uint32_t *)(stack_record_c8));
  puVar8 = ((undefined *)camry_host_ptr(0x21524u));
  puVar1 = ((uint32_t *)((stack_record_c8 + 96)));
  do {
    uVar6 = *puVar8;
    puVar8 = puVar8 + 1;
    *puVar1 = uVar6;
    puVar1 = puVar1 + 1;
  } while (camry_host_addr(puVar8)!=((uint32_t)(0x21584u)));
  puVar8 = ((undefined *)camry_host_ptr(0x21584u));
  do {
    uVar6 = *puVar8;
    puVar8 = puVar8 + 1;
    *puVar2 = uVar6;
    puVar2 = puVar2 + 1;
  } while (camry_host_addr(puVar8)!=((uint32_t)(0x215e4u)));
  restore_nvm11_bitmaps_and_expand_fortyone_mapped_bits_54b2c();
  uVar5 = (camry_r10_result = nvm_get_record(0x12, camry_host_addr(((uint32_t *)((stack_record_c8 + 96))))));
  if ((uVar5 != 0x10) ||
     (((uVar7 = (*((uint16_t *)(stack_record_c8 + 166))), (*((uint16_t *)((uint8_t *)((uint32_t *)((stack_record_c8 + 96))) + 2u))) != 0 && ((*((uint16_t *)((uint8_t *)((uint32_t *)((stack_record_c8 + 96))) + 2u))) != 0x4444)) &&
      ((*((uint16_t *)((uint8_t *)((uint32_t *)((stack_record_c8 + 96))) + 2u))) != 0x2222)))) {
    (*((uint16_t *)((uint8_t *)((uint32_t *)((stack_record_c8 + 96))) + 2u))) = 0x1111;
    uVar7 = 0;
  }
  uVar5 = (camry_r10_result = nvm_get_record(0x13, camry_host_addr(((uint32_t *)(stack_record_c8)))));
  record_counter = (*((uint16_t *)(stack_record_c8 + 70)));
  if ((uVar5 != 0x10) ||
     ((((*((uint16_t *)((uint8_t *)((uint32_t *)(stack_record_c8)) + 2u))) != 0 && ((*((uint16_t *)((uint8_t *)((uint32_t *)(stack_record_c8)) + 2u))) != 0x4444)) && ((*((uint16_t *)((uint8_t *)((uint32_t *)(stack_record_c8)) + 2u))) != 0x2222)))) {
    record_counter = 0;
    (*((uint16_t *)((uint8_t *)((uint32_t *)(stack_record_c8)) + 2u))) = 0x1111;
  }
  if (((uVar7 < record_counter) || ((uVar7 == 0xff && (record_counter == 1)))) &&
     ((uVar7 != 1 || (record_counter < 0xff)))) {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x2e3b))))) = 2;
    (*((ushort *)camry_host_ptr((uint32_t)(puVar3 + -0x2e28)))) = record_counter;
    __v850_copy_words_24(((uint32_t)((uint32_t)(puVar3 + -0x317c))), camry_host_addr(((uint32_t *)(stack_record_c8))));
    puVar4 = ((uint32_t *)((stack_record_c8 + 96)));
  }
  else {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar3 + (uint32_t)(-0x2e3b))))) = 1;
    (*((ushort *)camry_host_ptr((uint32_t)(puVar3 + -0x2e28)))) = uVar7;
    __v850_copy_words_24(((uint32_t)((uint32_t)(puVar3 + -0x317c))), camry_host_addr(((uint32_t *)((stack_record_c8 + 96)))));
  }
  __v850_copy_words_24(((uint32_t)((uint32_t)(puVar3 + -0x311c))), camry_host_addr(puVar4));
  uVar5 = 0;
  do {
    (camry_r10_result = restore_valid_five_entry_bank_and_cursor_from_nvm_54c0a(uVar5));
    uVar5 = uVar5 + 1;
  } while (uVar5 < 4);
  return camry_r10_result;
}

undefined4 classify_bank_nvm_status_as_pending_success_or_error_54df2(undefined1 param_1)

{
  uint uVar1;
  undefined4 uVar2;
  
  uVar1 = map_record_bank_to_nvm_selector_54bec(param_1);
  if (uVar1 == 0x20) {
    uVar2 = 0;
  }
  else {
    uVar1 = nvm_get_record_status(uVar1);
    if ((uVar1 & 0xf0) == 0x20) {
      uVar2 = 1;
    }
    else if ((uVar1 & 0xf0) == 0x10) {
      uVar2 = 2;
    }
    else {
      uVar2 = 3;
    }
  }
  return uVar2;
}

void poll_dual_record_bitmap_and_bank_write_completion_54e28(void)

{
  char cVar1;
  bool bVar2;
  uint32_t puVar3;
  uint uVar5;
  uint uVar6;
  int iVar7;
  undefined1 uVar8;
  int iVar9;
  char cVar10;
  char cVar11;
  char cVar12;
  uint uVar13;
  char local_28 [4];
  undefined8 uVar4;
  
  cVar10 = DAT_febe89d7;
  cVar11 = DAT_febe89cb;
  cVar12 = DAT_febe89ca;
  uVar8 = DAT_febe89c4;
  uVar4 = 0xfebeb800;
  puVar3 = (0xfebeb800u);
  bVar2 = false;
  uVar13 = 0;
  do {
    cVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe89ccu + (uint32_t)(uVar13) * 1u))));
    local_28[uVar13] = cVar1;
    if (cVar1 != '\0') {
      bVar2 = true;
    }
    uVar13 = uVar13 + 1;
  } while (uVar13 < 4);
  if ((((DAT_febe89ca != '\0') || (DAT_febe89cb != '\0')) || (DAT_febe89d7 != '\0')) || (bVar2)) {
    uVar13 = nvm_get_record_status(0x12);
    uVar5 = nvm_get_record_status(0x13);
    uVar6 = nvm_get_record_status(0x11);
    if ((cVar12 == '\x01') && ((uVar13 & 0xf0) != 0x20)) {
      if ((uVar13 & 0xf0) == 0x10) {
        cVar12 = '\x02';
      }
      else {
        cVar12 = '\x03';
      }
    }
    if ((cVar11 == '\x01') && ((uVar5 & 0xf0) != 0x20)) {
      if ((uVar5 & 0xf0) == 0x10) {
        cVar11 = '\x02';
      }
      else {
        cVar11 = '\x03';
      }
    }
    if ((cVar10 == '\x01') && ((uVar6 & 0xf0) != 0x20)) {
      if ((uVar6 & 0xf0) == 0x10) {
        cVar10 = '\x02';
      }
      else {
        cVar10 = '\x03';
      }
    }
    iVar9 = 0;
    uVar13 = 0;
    do {
      if (local_28[uVar13] == '\x01') {
        iVar7 = classify_bank_nvm_status_as_pending_success_or_error_54df2(uVar13);
        local_28[uVar13] = (char)iVar7;
        if (iVar7 == 1) {
          iVar9 = 1;
        }
      }
      puVar3 = ((uint32_t)(uVar4));
      uVar13 = uVar13 + 1;
    } while (uVar13 < 4);
    if (iVar9 != 1) {
      uVar13 = 0;
      do {
        if (local_28[uVar13] == '\x03') {
          iVar9 = 3;
        }
        uVar13 = uVar13 + 1;
      } while (uVar13 < 4);
    }
    DAT_febe89d7 = cVar10;
    DAT_febe89cb = cVar11;
    DAT_febe89ca = cVar12;
    if ((((cVar12 != '\x01') && (cVar11 != '\x01')) && (cVar10 != '\x01')) && (iVar9 != 1)) {
      if (((cVar12 == '\x03') || (cVar11 == '\x03')) || ((cVar10 == '\x03' || (iVar9 == 3)))) {
        uVar8 = 0x55;
      }
      else {
        uVar8 = 0;
      }
      DAT_febe89ca = '\0';
      DAT_febe89cb = '\0';
      DAT_febe89d7 = '\0';
      uVar13 = 0;
      do {
        local_28[uVar13] = '\0';
        uVar13 = uVar13 + 1;
      } while (uVar13 < 4);
    }
  }
  uVar13 = 0;
  do {
    uVar5 = uVar13 + 1;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe89ccu + (uint32_t)(uVar13) * 1u)))) = local_28[uVar13];
    uVar13 = uVar5;
  } while (uVar5 < 4);
  (*((volatile undefined *)camry_host_ptr((uint32_t)(0xfebeb800u + (uint32_t)(-0x2e3c) * 1u)))) = uVar8;
  return;
}

undefined4 choose_primary_secondary_nvm12_13_record_order_54f6e(char param_1,undefined2 *param_2,undefined2 *param_3)

{
  undefined2 uVar1;
  undefined4 uVar2;
  undefined2 uVar3;
  
  if (DAT_febe89d8 == DAT_febe86ca) {
    if (param_1 == '\x02') {
LAB_00054f92:
      uVar1 = 0x12;
      uVar3 = 0x13;
      uVar2 = 1;
      goto LAB_00054f9c;
    }
  }
  else if (param_1 != '\x02') goto LAB_00054f92;
  uVar1 = 0x13;
  uVar3 = 0x12;
  uVar2 = 2;
LAB_00054f9c:
  *param_2 = uVar1;
  *param_3 = uVar3;
  return uVar2;
}

int sum_bank_selected_u32_values_with_saturation_54fa4(char param_1)

{
  uint uVar1;
  uint32_t puVar2;
  uint uVar3;
  int iVar4;
  uint uVar5;
  
  uVar1 = DAT_febe89e4;
  puVar2 = 0xfebeb800u;
  uVar3 = 0;
  uVar5 = 0;
  if (param_1 == '\0') {
    puVar2 = 0xfebeb800u;
    uVar3 = get_febe505c_word_6a130();
    uVar5 = uVar1;
  }
  if (param_1 == '\x02') {
    uVar3 = (*((uint *)camry_host_ptr((uint32_t)(puVar2 + -0x2d04))));
    uVar5 = DAT_febe89ec;
  }
  if (~uVar5 < uVar3) {
    iVar4 = -1;
  }
  else {
    iVar4 = uVar3 + uVar5;
  }
  return iVar4;
}

uint32_t serialize_five_entry_bank_cursor_and_accumulator_to_nvm_54fda(uint param_1)

{
  uint32_t camry_r10_result;
  uint8_t stack_record_bc[188];
  undefined8 uVar1;
  uint selector;
  uint uVar2;
  
  uVar1 = 0xfebeb800;
  param_1 = param_1 & 0xff;
  selector = (camry_r10_result = map_record_bank_to_nvm_selector_54bec((uint)(byte)param_1));
  if (selector != 0x20) {
    uVar2 = 0;
    do {
      __v850_copy_words_8(camry_host_addr(((uint32_t *)(stack_record_bc)) + uVar2 * 8), ((short)param_1 * 5 + uVar2) * 0x20 + (int)uVar1 + -0x30bc
                  );
      uVar2 = uVar2 + 1;
    } while (uVar2 < 5);
    stack_record_bc[160] = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe89c6u + (uint32_t)(param_1) * 1u))));
    stack_record_bc[161] = 0;
    (*((uint16_t *)(stack_record_bc + 162))) = 0;
    (*((uint32_t *)(stack_record_bc + 164))) = (camry_r10_result = sum_bank_selected_u32_values_with_saturation_54fa4(param_1));
    (camry_r10_result = nvm_set_record(selector,((uint32_t *)(stack_record_bc))));
  }
  return camry_r10_result;
}
