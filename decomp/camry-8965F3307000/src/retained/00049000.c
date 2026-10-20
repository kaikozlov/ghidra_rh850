#include "common.h"

void return_only_stub_495a2(void)

{
  return;
}

void fill_constant_block_495a4(void)

{
  DAT_febe7e9c = 0;
  DAT_febe7e9e = 0;
  DAT_febe7ea0 = 0;
  DAT_febe7ea2 = 0;
  DAT_febe7ea4 = 0;
  DAT_febe7ea6 = 0;
  return;
}

void scale_six_unsigned_samples_by_1e06_495b6(void)

{
  int index;
  ushort source[6];
  ushort scaled[6];
  
  if (DAT_febeeba6 < 0x300) {
    source[0] = DAT_febe8212;
    source[1] = DAT_febe8214;
    source[2] = DAT_febe8216;
    source[3] = DAT_febe8218;
    source[4] = DAT_febe821a;
    source[5] = DAT_febe821c;
    for (index = 0; index < 6; index = index + 1) {
      scaled[index] = (ushort)((uint)source[index] * 0x1e06 >> 0x10);
    }
    DAT_febe7e9c = scaled[0];
    DAT_febe7e9e = scaled[1];
    DAT_febe7ea0 = scaled[2];
    DAT_febe7ea2 = scaled[3];
    DAT_febe7ea4 = scaled[4];
    DAT_febe7ea6 = scaled[5];
  }
  return;
}

void return_only_stub_4963c(void)

{
  return;
}

void clear_negated_ratio_filter_history_4963e(void)

{
  DAT_febe7ea8 = 0;
  DAT_febe7eaa = 0;
  DAT_febe7eac = 0;
  DAT_febe7eb0 = 0;
  return;
}

void filter_negated_scaled_signed_ratio_4964c(void)

{
  int iVar1;
  int iVar2;
  uint uVar3;
  int iVar4;
  
  if ((DAT_febe8a14 == '\x01') && (uVar3 = (uint)DAT_febeeac8, uVar3 != 0)) {
    iVar1 = (int)((int)(int16_t)DAT_febe5f36) << 0xe;
    if (uVar3 != 0) {
      if (iVar1 == -0x80000000 && uVar3 == 0xffffffff) {
        iVar1 = -0x80000000;
      }
      else {
        iVar1 = iVar1 / (int)uVar3;
      }
    }
    iVar4 = -iVar1;
    if (iVar4 + 0x7fff < 0 == (-1 < iVar4 && iVar4 + 0x7fff < 0) && iVar1 != 0x7fff) {
      if (iVar4 + -0x7fff < 0 == (iVar4 < 0 && -1 < iVar4 + -0x7fff) && iVar1 != -0x7fff) {
        iVar1 = 0x7fff;
      }
      else {
        iVar1 = (int)(short)iVar4;
      }
    }
    else {
      iVar1 = -0x7fff;
    }
    uVar3 = (uint)DAT_000318a8;
    if ((uVar3 == 0) || (0xffff < uVar3 * 4)) {
      iVar4 = (int)((int)(int16_t)DAT_febe7eaa) << 0x10;
      iVar2 = iVar1 << 0x10;
    }
    else {
      iVar4 = (int)((int)(int16_t)DAT_febe7eaa) * uVar3 * 4;
      iVar2 = iVar1 * uVar3 * 4;
    }
    DAT_febe7ea8 = (undefined2)iVar1;
    DAT_febe7eac = ((int)(int16_t)DAT_febe7eaa);
    DAT_febe7eb0 = iVar2 + (DAT_febe7eb0 - iVar4);
    DAT_febe7eaa = (short)( (int)(DAT_febe7eb0) / (int)0x10000);
  }
  return;
}

void initialize_thirty_receive_timeout_states_496d4(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  
  iVar3 = 0;
  do {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe7ef0u + (uint32_t)(iVar3) * 1u)))) = 0;
    iVar2 = iVar3 + 1;
    *(undefined2 *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe7eb4u + (uint32_t)(iVar3 * 2) * 1u)))) = 0;
    iVar1 = iVar3 + -0x1d;
    iVar3 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  iVar3 = 0;
  do {
    iVar2 = iVar3 + 1;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe7f0eu + (uint32_t)(iVar3) * 1u)))) = '\x01';
    iVar1 = iVar3 + -0x1d;
    iVar3 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  return;
}

void return_only_stub_49706(void)

{
  return;
}

uchar get_application_receive_status(uint selector)

{
  if ((selector & 0xff) < 0x1e) {
    return (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe7f0eu + (uint32_t)(selector & 0xff) * 1u))));
  }
  return '\x01';
}

void return_only_stub_498f4(void)

{
  return;
}

int seed_status_transition_delay_counter_498f6(void)

{
  undefined2 uVar1;
  uint32_t puVar2;
  int iVar3;
  
  puVar2 = 0xfebeb800u;
  iVar3 = test_redundant_status_a5_or_vote_error13_588b6();
  uVar1 = DAT_000317b6;
  if (iVar3 == 0) {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x38cc))))) = 0;
    (*((undefined2 *)camry_host_ptr((uint32_t)(puVar2 + -0x38b8)))) = 0;
    (*((undefined2 *)camry_host_ptr((uint32_t)(puVar2 + -0x38b6)))) = uVar1;
  }
  return iVar3;
}

void update_status_transition_delay_ready_flag_49918(void)

{
  if (((DAT_febee826 == '\"') && (DAT_febe7f37 == '\x11')) ||
     ((DAT_febee826 == '\0' && (DAT_febe7f37 == '3')))) {
    DAT_febe7f48 = 0;
    DAT_febe7f4a = 0;
    if (DAT_febee88e <= DAT_000317b4) {
      DAT_febe7f4a = DAT_000317b4 - DAT_febee88e;
    }
  }
  if (DAT_febe7f48 < DAT_febe7f4a) {
    DAT_febe7f34 = 0;
    DAT_febe7f48 = DAT_febe7f48 + 1;
  }
  else {
    DAT_febe7f34 = 0x5a;
  }
  DAT_febe7f37 = DAT_febee826;
  return;
}

void classify_indexed_channel_admission_4996e(uint param_1)

{
  uint8_t stack_record_2f[47];
  char cVar1;
  uint uVar2;
  char cVar3;
  undefined1 uVar4;
  undefined1 uVar5;
  uint uVar6;
  char cVar7;
  uint uVar8;
  
  cVar1 = DAT_febe7f34;
  uVar2 = param_1 & 0xff;
  cVar7 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe7f2eu + (uint32_t)(uVar2) * 1u))));
  get_normal_network_fault_mask_with_complement_validation_7c652(uVar2,(stack_record_2f + 1));
  if (((*((uint16_t *)(stack_record_2f + 1))) & 0x48) != 0) {
    cVar7 = 'Z';
  }
  uVar5 = 0;
  if (((*((uint16_t *)(stack_record_2f + 1))) & 1) != 0) {
    uVar5 = 0x5a;
  }
  read_record_state_as_compact_code_7e88c(uVar2,stack_record_2f);
  if (((stack_record_2f[0] == '\x02') || (stack_record_2f[0] == '\x03')) || (stack_record_2f[0] == '\x04')) {
    uVar6 = 1 << (param_1 & 0x1f) | 0x100;
  }
  else {
    uVar6 = 0;
  }
  if (uVar2 != 0) {
    uVar8 = uVar6 & 2;
  }
  else {
    uVar8 = uVar6 & 1;
  }
  cVar3 = get_upper_network_indication_zero_one_or_three_7bd3a(uVar2 != 0);
  if ((((uVar6 & 0xff00) == 0x100) && (uVar8 == 1 || uVar8 == 2)) && (cVar7 != 'Z')) {
    if (cVar3 == '\x03') {
      if (cVar1 == 'Z') {
        uVar4 = 2;
        goto LAB_00049a1c;
      }
    }
    else if (cVar3 != '\x01') goto LAB_00049a1a;
    uVar4 = 1;
  }
  else {
LAB_00049a1a:
    uVar4 = 3;
  }
LAB_00049a1c:
  DAT_febe7f3c = (undefined2)uVar6;
  DAT_febe7f3e = (undefined2)(uVar6 & 0xff00);
  *(short *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe7f40u + (uint32_t)(uVar2 * 2) * 1u)))) = (short)uVar8;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe7f32u + (uint32_t)(uVar2) * 1u)))) = cVar3;
  *(ushort *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe7f44u + (uint32_t)(uVar2 * 2) * 1u)))) = (*((uint16_t *)(stack_record_2f + 1)));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe7f2eu + (uint32_t)(uVar2) * 1u)))) = cVar7;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe7f30u + (uint32_t)(uVar2) * 1u)))) = uVar5;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe7f2cu + (uint32_t)(uVar2) * 1u)))) = uVar4;
  return;
}

void request_channel_state_22_on_transition_49a48(uint param_1)

{
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe7f35u + (uint32_t)(param_1 & 0xff) * 1u)))) != '\"') {
    invoke_enabled_network_callback_slot_zero_7bc56((uint)(byte)param_1);
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe7f35u + (uint32_t)(param_1 & 0xff) * 1u)))) = 0x22;
  return;
}

void request_channel_state_11_on_transition_49a70(uint param_1)

{
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe7f35u + (uint32_t)(param_1 & 0xff) * 1u)))) != '\x11') {
    invoke_enabled_network_callback_slot_four_7bc8a((uint)(byte)param_1);
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe7f35u + (uint32_t)(param_1 & 0xff) * 1u)))) = 0x11;
  return;
}

uint pack_four_way_index_and_two_true_flags_49a98(undefined1 param_1,char param_2,char param_3)

{
  uint uVar1;
  
  uVar1 = 0;
  switch(param_1) {
  case 0:
    uVar1 = 1;
    break;
  case 1:
    uVar1 = 2;
    break;
  case 2:
    uVar1 = 4;
    break;
  case 3:
    uVar1 = 8;
  }
  if (param_2 == 'Z') {
    uVar1 = uVar1 | 0x10;
  }
  if (param_3 == 'Z') {
    uVar1 = uVar1 | 0x20;
  }
  return uVar1;
}

void reconcile_application_normal_network_policy(void)

{
  undefined1 uVar1;
  undefined1 uVar2;
  undefined1 uVar3;
  uchar uVar4;
  char cVar5;
  uint32_t puVar6;
  uint32_t puVar7;
  ushort uVar8;
  short sVar9;
  
  cVar5 = DAT_febe81cc;
  uVar4 = diagnostic_normal_tx_policy_request;
  puVar6 = 0xfebeb800u;
  update_status_transition_delay_ready_flag_49918();
  classify_indexed_channel_admission_4996e(0);
  puVar7 = ((uint32_t)((uint32_t)(puVar6)));
  if ((((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(-0x38d4))))) == '\x02') && (uVar4 != '\x11')) && (cVar5 == 'Z')) {
    request_channel_state_11_on_transition_49a70(0);
  }
  else {
    request_channel_state_22_on_transition_49a48(0);
  }
  uVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(-0x38d1)))));
  uVar2 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(-0x38cf)))));
  uVar3 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(-0x38d3)))));
  uVar8 = pack_four_way_index_and_two_true_flags_49a98((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(-0x38d4))))),(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(-0x38d2))))),(*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar6 + (uint32_t)(-0x38d0))))));
  sVar9 = pack_four_way_index_and_two_true_flags_49a98(uVar3,uVar1,uVar2);
  (*((ushort *)camry_host_ptr((uint32_t)(puVar7 + -0x38c6)))) = uVar8 | sVar9 << 8;
  return;
}

void return_only_stub_49b38(void)

{
  return;
}

void return_only_stub_49b3a(void)

{
  return;
}

void fill_constant_block_49b3c(void)

{
  DAT_febe7f54 = 0;
  DAT_febe7f55 = 0;
  DAT_febe7f56 = 0;
  DAT_febe7f57 = 0;
  DAT_febe7f58 = 0;
  DAT_febe7f59 = 0;
  DAT_febe7f5a = 0;
  DAT_febe7f5b = 0;
  DAT_febe7f5c = 0;
  DAT_febe7f5d = 0xff;
  DAT_febe7f5e = 0xff;
  DAT_febe7f5f = 0xff;
  return;
}

char update_status_change_holdoff_latch_49b5c(char param_1)

{
  uint32_t puVar1;
  char extraout_r6;
  char cVar2;
  ushort uVar3;
  
  puVar1 = 0xfebeb800u;
  if (((param_1 == DAT_febe7f53) || (param_1 == '3')) || (DAT_febe7f53 == '\"')) {
    cVar2 = DAT_febe7f4c;
    uVar3 = DAT_febe7f60;
    if (((param_1 != '\x11') && (DAT_febe7f4c == 'Z')) &&
       ((DAT_0002fbf0 < DAT_febe7f60 || (uVar3 = DAT_febe7f60 + 1, DAT_0002fbf0 < uVar3)))) {
      cVar2 = '\0';
    }
  }
  else {
    puVar1 = 0xfebeb800u;
    fill_constant_block_49b3c();
    cVar2 = 'Z';
    uVar3 = 0;
    param_1 = ((char)((uint)(byte)param_1));
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x38b4))))) = cVar2;
  (*((ushort *)camry_host_ptr((uint32_t)(puVar1 + -0x38a0)))) = uVar3;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x38ad))))) = param_1;
  return cVar2;
}

uint update_threshold_holdoff_pair_49bba(char param_1)

{
  char cVar1;
  
  if ((param_1 == '3') || (DAT_febe66b8 < DAT_00030e38)) {
    cVar1 = 'Z';
  }
  else {
    cVar1 = '\0';
  }
  if (DAT_febe66ac != '\0') {
    if (cVar1 == 'Z') {
      DAT_febe7f62 = 0;
      DAT_febe7f4e = 'Z';
      DAT_febe7f4d = 'Z';
    }
    else if (DAT_febe7f4d == 'Z') {
      DAT_febe7f4d = '\0';
    }
    else if ((DAT_febe7f4e == 'Z') &&
            ((DAT_0002fbf2 < DAT_febe7f62 ||
             (DAT_febe7f62 = DAT_febe7f62 + 1, DAT_0002fbf2 < DAT_febe7f62)))) {
      DAT_febe7f4e = '\0';
    }
  }
  return DAT_febe7f4e;
}

uint update_true_flag_holdoff_49c2c(char param_1)

{
  if (param_1 == 'Z') {
    DAT_febe7f64 = 0;
    DAT_febe7f4f = 'Z';
  }
  else if ((DAT_febe7f4f == 'Z') &&
          ((DAT_0002fbf4 < DAT_febe7f64 ||
           (DAT_febe7f64 = DAT_febe7f64 + 1, DAT_0002fbf4 < DAT_febe7f64)))) {
    DAT_febe7f4f = '\0';
  }
  return DAT_febe7f4f;
}

void latch_803d_change_count_threshold_49c64(void)

{
  if (((DAT_febe7f56 == 'Z') || (1 < internal_source_admission_state)) || (DAT_febe803e != '\0')
     ) {
    DAT_febe7f55 = 0;
  }
  else if ((DAT_febe7f54 != DAT_febe803d) &&
          ((DAT_0002fbec <= DAT_febe7f55 ||
           (DAT_febe7f55 = DAT_febe7f55 + 1, DAT_0002fbec <= DAT_febe7f55)))) {
    DAT_febe7f56 = 'Z';
  }
  DAT_febe7f54 = DAT_febe803d;
  return;
}

void latch_8017_change_count_threshold_49cb0(void)

{
  if (((DAT_febe7f59 == 'Z') || (1 < internal_source_admission_state)) || (DAT_febe8018 != '\0')
     ) {
    DAT_febe7f58 = 0;
  }
  else if ((DAT_febe7f57 != DAT_febe8017) &&
          ((DAT_0002fbed <= DAT_febe7f58 ||
           (DAT_febe7f58 = DAT_febe7f58 + 1, DAT_0002fbed <= DAT_febe7f58)))) {
    DAT_febe7f59 = 'Z';
  }
  DAT_febe7f57 = DAT_febe8017;
  return;
}

void latch_800b_change_count_threshold_49cfc(void)

{
  if (((DAT_febe7f5c == 'Z') || (1 < internal_source_admission_state)) || (DAT_febe800a != '\0')
     ) {
    DAT_febe7f5b = 0;
  }
  else if ((DAT_febe7f5a != DAT_febe800b) &&
          ((DAT_0002fbee <= DAT_febe7f5b ||
           (DAT_febe7f5b = DAT_febe7f5b + 1, DAT_0002fbee <= DAT_febe7f5b)))) {
    DAT_febe7f5c = 'Z';
  }
  DAT_febe7f5a = DAT_febe800b;
  return;
}

void update_three_source_change_latches_49d4a(void)

{
  latch_803d_change_count_threshold_49c64();
  latch_8017_change_count_threshold_49cb0();
  latch_800b_change_count_threshold_49cfc();
  return;
}

undefined4 classify_latched_source_zero_values_49d5e(char param_1)

{
  DAT_febe7f5f = -1;
  DAT_febe7f5d = DAT_febe7f5f;
  DAT_febe7f5e = DAT_febe7f5f;
  if (param_1 == '\x01' || param_1 == '\x02') {
    if ((DAT_febe7f56 == 'Z') && (DAT_febe7f5d = DAT_febe803c, param_1 == '\x01')) {
      DAT_febe7f5d = DAT_febe803b;
    }
    if (DAT_febe7f59 == 'Z') {
      DAT_febe7f5e = DAT_febe8016;
    }
    if (DAT_febe7f5c == 'Z') {
      DAT_febe7f5f = DAT_febe800c;
    }
    if (((((((int8_t)DAT_febe7f5d) != -1) || (((int8_t)DAT_febe7f5e) != -1)) || (((int8_t)DAT_febe7f5f) != -1)) &&
        ((DAT_febe7f5d == '\0' || (((int8_t)DAT_febe7f5d) == -1)))) &&
       (((DAT_febe7f5e == '\0' || (DAT_febe7f5f == '\0')) ||
        ((((int8_t)DAT_febe7f5e) == -1 && (((int8_t)DAT_febe7f5f) == -1)))))) {
      return 0x5a;
    }
  }
  return 0;
}

void publish_thirty_table_selected_inhibit_bytes_49de4(void)

{
  undefined1 uVar1;
  undefined1 uVar2;
  undefined1 uVar3;
  undefined1 uVar4;
  uint uVar5;
  
  uVar3 = DAT_febe7f52;
  uVar2 = DAT_febe7f51;
  uVar1 = DAT_febe7f50;
  uVar5 = 0;
  do {
    uVar4 = uVar2;
    if (((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x290dau + (uint32_t)(uVar5 * 8) * 1u)))) != '\x01') &&
       (uVar4 = uVar1, (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x290dau + (uint32_t)(uVar5 * 8) * 1u)))) == '\x02')) {
      uVar4 = uVar3;
    }
    set_tracking_result_byte53f8_8e7d0((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x290d4u + (uint32_t)(uVar5 * 8) * 1u)))),uVar4);
    uVar5 = uVar5 + 1;
  } while (uVar5 < 0x1e);
  return;
}

uint32_t combine_and_publish_monitor_inhibit_sources_49e22(void)

{
  uint32_t camry_r10_result;
  undefined1 uVar1;
  uchar uVar2;
  undefined1 uVar3;
  int iVar4;
  int iVar5;
  int iVar6;
  int iVar7;
  int iVar8;
  
  uVar3 = DAT_febee826;
  uVar2 = dtc_setting_inhibit_request;
  uVar1 = DAT_febe7f97;
  iVar4 = (camry_r10_result = update_status_change_holdoff_latch_49b5c(DAT_febee826));
  iVar5 = (camry_r10_result = update_threshold_holdoff_pair_49bba(uVar3));
  iVar6 = (camry_r10_result = update_true_flag_holdoff_49c2c(uVar1));
  update_three_source_change_latches_49d4a();
  iVar7 = (camry_r10_result = classify_latched_source_zero_values_49d5e(1));
  iVar8 = (camry_r10_result = classify_latched_source_zero_values_49d5e(2));
  if ((((iVar4 == 0) && (iVar5 == 0)) && (uVar2 == '\0')) && (iVar6 == 0)) {
    DAT_febe7f50 = 0;
  }
  else {
    DAT_febe7f50 = 0x5a;
  }
  DAT_febe7f51 = DAT_febe7f50;
  if (iVar7 != 0) {
    DAT_febe7f51 = 0x5a;
  }
  DAT_febe7f52 = DAT_febe7f50;
  if (iVar8 != 0) {
    DAT_febe7f52 = 0x5a;
  }
  publish_thirty_table_selected_inhibit_bytes_49de4();
  return camry_r10_result;
}

void initialize_source_admission_state_blocks_49efe(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  fill_constant_block_49ec6();
  fill_constant_block_49eda();
  fill_constant_block_49eec();
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x3898))))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x3897))))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x3896))))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x3895))))) = 0;
  return;
}

void return_only_stub_49f1e(void)

{
  return;
}
