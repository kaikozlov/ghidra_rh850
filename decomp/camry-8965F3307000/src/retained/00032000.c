#include "common.h"

void mark_redundant_byte_6884_for_codes_21_to_34_32036(uint param_1)

{
  if ((param_1 & 0xff) - 0x15 < 0xe) {
    publish_redundant_byte_6884_31ed0(0x5a);
  }
  return;
}

void mark_redundant_byte_6885_for_codes_21_to_34_32050(uint param_1)

{
  if ((param_1 & 0xff) - 0x15 < 0xe) {
    publish_redundant_byte_6885_31eea(0x5a);
  }
  return;
}

void return_only_stub_3206a(void)

{
  return;
}

void initialize_thermal_shutdown_counter(void)

{
  uint32_t puVar1;
  undefined2 uStack_6;
  
  puVar1 = 0xfebeb800u;
  interpolate_s16_axis_u16_values_7025c(((undefined *)camry_host_ptr(0x30e78u)),0,&uStack_6);
  (*((undefined2 *)camry_host_ptr((uint32_t)((int)(0xffffb08cu + (uint32_t)((int)puVar1)))))) = 0;
  (*((undefined2 *)camry_host_ptr((uint32_t)((int)(0xffffb08eu + (uint32_t)((int)puVar1)))))) = uStack_6;
  return;
}

void step_thermal_shutdown_request(void)

{
  if ((thermal_shutdown_count < thermal_shutdown_count_limit) &&
     (((volatile uint8_t *)camry_host_ptr(0xfebe6fb0u))[0] != 0xa5)) {
    thermal_shutdown_count = thermal_shutdown_count + 1;
  }
  else {
    thunk_set_indexed_request_and_clear_complement_b15ac(0x27);
  }
  return;
}

void return_only_stub_320be(void)

{
  return;
}

void return_only_stub_320c0(void)

{
  return;
}

void initialize_dual_halfword_shadows_once_320c2(void)

{
  uint uVar1;
  uint uVar2;
  
  if ((DAT_febe6890 == '\0') && (DAT_febe68b4 != -1)) {
    uVar2 = 0;
    do {
      uVar1 = uVar2 + 1;
      (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe689au + (uint32_t)(uVar2) * 2u)))) = *(undefined2 *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe68aau + (uint32_t)(uVar2 * 2) * 1u))));
      (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe68a0u + (uint32_t)(uVar2) * 2u)))) = *(undefined2 *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe68b0u + (uint32_t)(uVar2 * 2) * 1u))));
      uVar2 = uVar1;
    } while (uVar1 < 2);
    DAT_febe6890 = 'Z';
  }
  return;
}

void set_first_halfword_shadow_by_u8_index_320fe(uint param_1,undefined2 param_2)

{
  (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe689au + (uint32_t)(param_1 & 0xff) * 2u)))) = param_2;
  return;
}

void publish_record_coherence_fault(void)

{
  char cVar1;
  uint32_t puVar2;
  puVar2 = 0xfebeb800u;
  cVar1 = DAT_febe6899;
  if (DAT_febe6899 == '\0') {
    puVar2 = 0xfebeb800u;
    report_diagnostic_event_failure(0x12e,10);
    retain_and_clear_fault_record(0x17);
    encode_fault_action_kind('\x17','\x01');
    select_current_fault_record(0x17);
    cVar1 = 'Z';
  }
  (*((char *)camry_host_ptr((uint32_t)((int)0xffffb098u + (int)(puVar2 + 1))))) = cVar1;
  return;
}

void set_second_halfword_shadow_by_u8_index_32146(uint param_1,undefined2 param_2)

{
  (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe68a0u + (uint32_t)(param_1 & 0xff) * 2u)))) = param_2;
  return;
}

void reconcile_dual_record_halfword_shadows_32152(uint param_1)

{
  short sVar1;
  short sVar2;
  short sVar3;
  char cVar4;
  int iVar5;
  char cVar6;
  char cVar7;
  char cVar8;
  char cVar9;
  
  iVar5 = DAT_febe68b4;
  param_1 = param_1 & 0xff;
  cVar8 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe6891u + (uint32_t)(param_1) * 1u))));
  cVar9 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe6893u + (uint32_t)(param_1) * 1u))));
  cVar7 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe6895u + (uint32_t)(param_1) * 1u))));
  cVar6 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe6897u + (uint32_t)(param_1) * 1u))));
  cVar4 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe68a7u + (uint32_t)(param_1) * 1u))));
  sVar1 = (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe689au + (uint32_t)(param_1) * 2u))));
  sVar2 = (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe68a0u + (uint32_t)(param_1) * 2u))));
  sVar3 = *(short *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe68b0u + (uint32_t)(param_1 * 2) * 1u))));
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe68a5u + (uint32_t)(param_1) * 1u)))) == '\0') {
    if ((int)sVar1 == (int)*(short *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe68aau + (uint32_t)(param_1 * 2) * 1u))))) {
      cVar8 = '\0';
      cVar7 = '\0';
    }
    else {
      cVar7 = 'Z';
      if (DAT_febe68b4 == -0x5aa5a55b) {
        set_first_halfword_shadow_by_u8_index_320fe(param_1,(int)sVar2);
        cVar8 = cVar7;
      }
      else {
        publish_record_coherence_fault();
      }
    }
  }
  if (cVar4 == '\0') {
    if (iVar5 == -0x5aa5a55b) {
      if ((int)sVar2 == (int)sVar3) {
        cVar9 = '\0';
        cVar6 = '\0';
        goto LAB_00032226;
      }
      set_second_halfword_shadow_by_u8_index_32146(param_1,(int)sVar1);
      cVar9 = 'Z';
      cVar6 = cVar9;
    }
    else {
      cVar9 = '\0';
    }
  }
  if ((cVar8 == 'Z') && (cVar9 == 'Z')) {
    publish_record_coherence_fault();
  }
LAB_00032226:
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe6891u + (uint32_t)(param_1) * 1u)))) = cVar8;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe6893u + (uint32_t)(param_1) * 1u)))) = cVar9;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe6895u + (uint32_t)(param_1) * 1u)))) = cVar7;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe6897u + (uint32_t)(param_1) * 1u)))) = cVar6;
  return;
}

void service_two_record_shadow_channels_when_enabled_32240(void)

{
  int iVar1;
  
  iVar1 = DAT_febe68b4;
  if ((DAT_febe8a18 == 'Z') && (initialize_dual_halfword_shadows_once_320c2(), iVar1 != -1)) {
    reconcile_dual_record_halfword_shadows_32152(0);
    reconcile_dual_record_halfword_shadows_32152(1);
  }
  return;
}

void return_only_stub_3226a(void)

{
  return;
}

void load_selected_or_paired_record_halfwords_3226c(char param_1)

{
  uint8_t stack_record_20[32];
  int iVar1;
  uint uVar2;
  uint uVar3;
  
  (*((uint32_t *)(stack_record_20 + 8))) = DAT_00021000;
  (*((uint32_t *)(stack_record_20 + 12))) = DAT_00021004;
  (*((uint32_t *)(stack_record_20 + 0))) = DAT_00021008;
  (*((uint32_t *)(stack_record_20 + 4))) = DAT_0002100c;
  if (param_1 == '\0') {
    uVar2 = nvm_get_record(0x208, camry_host_addr((stack_record_20 + 8)));
    uVar3 = nvm_get_record(0x209, camry_host_addr(stack_record_20));
  }
  else {
    if (param_1 == '\x11') {
      uVar2 = 0x208;
    }
    else {
      if (param_1 != '\"') goto LAB_0003230e;
      uVar2 = 0x209;
    }
    uVar2 = nvm_get_record(uVar2, camry_host_addr((stack_record_20 + 8)));
    uVar3 = 0x10;
  }
  if ((uVar2 == 0x10) && (uVar3 == 0x10)) {
    uVar2 = 0;
    do {
      iVar1 = uVar2 * 2;
      *(undefined2 *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe68aau + (uint32_t)(iVar1) * 1u)))) = (*((undefined2 *)((uint8_t *)(stack_record_20 + 12) + (iVar1))));
      if (param_1 == '\0') {
        *(undefined2 *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe68b0u + (uint32_t)(iVar1) * 1u)))) = (*((undefined2 *)((uint8_t *)(stack_record_20 + 4) + (iVar1))));
      }
      uVar2 = uVar2 + 1;
    } while (uVar2 < 2);
    return;
  }
LAB_0003230e:
  publish_record_coherence_fault();
  return;
}

int compare_record_208_209_halfwords_and_load_if_equal_32316(void)

{
  uint8_t stack_record_1c[28];
  uint uVar1;
  uint uVar2;
  int iVar3;
  
  (*((uint32_t *)(stack_record_1c + 8))) = DAT_00021010;
  (*((uint32_t *)(stack_record_1c + 12))) = DAT_00021014;
  (*((uint32_t *)(stack_record_1c + 0))) = DAT_00021018;
  (*((uint32_t *)(stack_record_1c + 4))) = DAT_0002101c;
  uVar1 = nvm_get_record(0x208, camry_host_addr(stack_record_1c));
  uVar2 = nvm_get_record(0x209, camry_host_addr((stack_record_1c + 8)));
  iVar3 = 0;
  if ((uVar1 == 0x10) && (uVar2 == 0x10)) {
    uVar1 = 0;
    do {
      if ((*((short *)((uint8_t *)(stack_record_1c + 4) + (uVar1 * 2)))) != (*((short *)((uint8_t *)(stack_record_1c + 12) + (uVar1 * 2))))) {
        iVar3 = 0x5a;
      }
      uVar1 = uVar1 + 1;
    } while (uVar1 < 2);
    if (iVar3 == 0) {
      load_selected_or_paired_record_halfwords_3226c(0);
    }
  }
  else {
    iVar3 = 0x5a;
  }
  return iVar3;
}

void classify_dual_record_validity_and_restore_halfwords_32398(void)

{
  uint8_t stack_record_1c[28];
  uint32_t puVar1;
  uint uVar2;
  uint uVar3;
  int iVar4;
  undefined4 uVar5;
  undefined1 uVar6;
  
  puVar1 = 0xfebeb800u;
  uVar2 = nvm_get_record(0x208, camry_host_addr(((uint32_t *)((stack_record_1c + 8)))));
  uVar3 = nvm_get_record(0x209, camry_host_addr(((uint32_t *)(stack_record_1c))));
  if ((uVar2 == 0x10) && (((uint32_t *)((stack_record_1c + 8)))[0] == 0xa55a5aa5)) {
    if ((uVar3 != 0x10) || (((uint32_t *)(stack_record_1c))[0] != 0xa55a5aa5)) {
      uVar5 = 0x11;
LAB_00032412:
      load_selected_or_paired_record_halfwords_3226c(uVar5);
      uVar5 = 0x5aa5a55a;
      uVar6 = 0x22;
      report_diagnostic_event_failure(0x123,0x32);
      goto LAB_0003243c;
    }
    iVar4 = compare_record_208_209_halfwords_and_load_if_equal_32316();
    if (iVar4 == 0) {
      uVar5 = 0xa55a5aa5;
      uVar6 = 0x44;
      report_diagnostic_healthy_observed(0x123);
      report_diagnostic_healthy_observed(0x12e);
      goto LAB_0003243c;
    }
  }
  else if ((uVar3 == 0x10) && (((uint32_t *)(stack_record_1c))[0] == 0xa55a5aa5)) {
    uVar5 = 0x22;
    goto LAB_00032412;
  }
  uVar5 = 0x5aa5a55a;
  uVar6 = 0x22;
  publish_record_coherence_fault();
LAB_0003243c:
  (*((undefined4 *)camry_host_ptr((uint32_t)((int)(0xffffb0b4u + (uint32_t)((int)puVar1)))))) = uVar5;
  (*((undefined1 *)camry_host_ptr((uint32_t)((int)(0xffffb0a4u + (uint32_t)((int)puVar1)))))) = uVar6;
  return;
}

void thunk_classify_dual_record_validity_and_restore_halfwords_32398(void)

{
  classify_dual_record_validity_and_restore_halfwords_32398();
  return;
}

uint32_t publish_family2_group8_halfword(uint index)

{
  uint32_t camry_r10_result;
  uint8_t stack_record_14[20];
  int iVar1;
  undefined2 uVar2;
  uint32_t puVar3;
  uint uVar4;
  
  puVar3 = 0xfebeb800u;
  (*((uint32_t *)(stack_record_14 + 0))) = DAT_00021020;
  (*((uint32_t *)(stack_record_14 + 4))) = DAT_00021024;
  uVar4 = (camry_r10_result = nvm_get_record(0x208, camry_host_addr(stack_record_14)));
  iVar1 = (index & 0xff) * 2;
  if (uVar4 == 0x10) {
    uVar2 = (*((undefined2 *)camry_host_ptr((uint32_t)((int)camry_host_addr((stack_record_14 + 4)) + iVar1))));
  }
  else {
    uVar2 = (*((undefined2 *)camry_host_ptr((uint32_t)(puVar3 + iVar1 + -0x5132))));
  }
  *(undefined2 *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe68aau + (uint32_t)((index & 0xff) * 2) * 1u)))) = uVar2;
  return camry_r10_result;
}

uint reload_record_209_halfword_by_u8_index_3249a(uint param_1)

{
  uint8_t stack_record_14[20];
  int iVar1;
  uint32_t puVar2;
  uint uVar3;
  
  puVar2 = 0xfebeb800u;
  (*((uint32_t *)(stack_record_14 + 0))) = DAT_00021028;
  (*((uint32_t *)(stack_record_14 + 4))) = DAT_0002102c;
  uVar3 = nvm_get_record(0x209, camry_host_addr(stack_record_14));
  if (uVar3 == 0x10) {
    iVar1 = (param_1 & 0xff) * 2;
    (*((undefined2 *)camry_host_ptr((uint32_t)((int)0xffffb0b0u + (int)(puVar2 + iVar1))))) =
         (*((undefined2 *)((uint8_t *)(stack_record_14 + 4) + (iVar1))));
  }
  return uVar3;
}

void report_record_coherence_failure_on_invalid_transition_324d6(int param_1)

{
  if ((DAT_febe68b4 != 0x5aa5a55a) && (param_1 == 0x5aa5a55a)) {
    report_diagnostic_event_failure(0x123,0x32);
  }
  return;
}

void refresh_requested_record_halfword_channel_324fc(uint param_1)

{
  char cVar1;
  uint32_t puVar2;
  int extraout_r10;
  int iVar3;
  undefined1 uVar4;
  undefined1 uVar5;
  undefined4 uVar6;
  
  puVar2 = 0xfebeb800u;
  param_1 = param_1 & 0xff;
  uVar5 = 0;
  uVar4 = 0;
  cVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe66c2u + (uint32_t)(param_1) * 1u))));
  uVar6 = DAT_febe68b4;
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe66c0u + (uint32_t)(param_1) * 1u)))) == 'Z') {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe68a5u + (uint32_t)(param_1) * 1u)))) = 0x5a;
    puVar2 = 0xfebeb800u;
    publish_family2_group8_halfword(param_1);
    uVar6 = 0x5aa5a55a;
    uVar5 = 0x5a;
    if (extraout_r10 == 0x10) {
      uVar6 = 0xa55a5aa5;
      uVar5 = 0;
    }
  }
  if (cVar1 == 'Z') {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe68a7u + (uint32_t)(param_1) * 1u)))) = 0x5a;
    iVar3 = reload_record_209_halfword_by_u8_index_3249a(param_1);
    uVar6 = 0x5aa5a55a;
    uVar4 = 0x5a;
    if (iVar3 == 0x10) {
      uVar6 = 0xa55a5aa5;
      uVar4 = 0;
    }
  }
  report_record_coherence_failure_on_invalid_transition_324d6(uVar6);
  (*((undefined4 *)camry_host_ptr((uint32_t)((int)(0xffffb0b4u + (uint32_t)((int)puVar2)))))) = uVar6;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe68a5u + (uint32_t)(param_1) * 1u)))) = uVar5;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe68a7u + (uint32_t)(param_1) * 1u)))) = uVar4;
  return;
}

void refresh_both_requested_record_halfword_channels_32580(void)

{
  refresh_requested_record_halfword_channel_324fc(0);
  refresh_requested_record_halfword_channel_324fc(1);
  return;
}

int stage_pair_correction(uchar selector,short *values)

{
  short *psVar1;
  int iVar2;
  uint uVar3;
  
  uVar3 = 0;
  if (selector == '\0') {
    do {
      iVar2 = uVar3 * 2;
      psVar1 = values + uVar3;
      uVar3 = uVar3 + 1 & 0xff;
      *(short *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe68aau + (uint32_t)(iVar2) * 1u)))) = *psVar1;
    } while (uVar3 < 2);
    DAT_febe68b4 = 0xa55a5aa5;
    return 0;
  }
  return -6;
}

uint32_t queue_pair_correction_records(void)

{
  uint32_t camry_r10_result;
  uint8_t stack_record_14[20];
  uint uVar1;
  undefined2 uVar2;
  uint32_t puVar3;
  uint uVar4;
  
  puVar3 = 0xfebeb800u;
  (*((uint32_t *)(stack_record_14 + 8))) = 0xa55a5aa5;
  (*((uint32_t *)(stack_record_14 + 0))) = 0xa55a5aa5;
  uVar4 = 0;
  do {
    uVar2 = *(undefined2 *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe68aau + (uint32_t)(uVar4 * 2) * 1u))));
    uVar1 = uVar4 + 1;
    ((uint16_t *)((stack_record_14 + 12)))[uVar4] = uVar2;
    ((uint16_t *)((stack_record_14 + 4)))[uVar4] = uVar2;
    uVar4 = uVar1;
  } while (uVar1 < 2);
  (camry_r10_result = nvm_set_record(0x208,(stack_record_14 + 8)));
  (camry_r10_result = nvm_set_record(0x209,stack_record_14));
  (*((undefined4 *)camry_host_ptr((uint32_t)((int)(0xffffb0b4u + (uint32_t)((int)puVar3)))))) = 0xa55a5aa5;
  return camry_r10_result;
}

void return_only_stub_32620(void)

{
  return;
}

void return_only_stub_32622(void)

{
  return;
}

void average_two_six_channel_u16_groups_over_128_samples_32624(void)

{
  uint8_t stack_record_18[24];
  int iVar1;
  ushort uVar2;
  int iVar3;
  int iVar4;
  uint uVar5;
  
  if (DAT_febeeba6 == 0x600) {
    ((uint16_t *)((stack_record_18 + 12)))[0] = DAT_febe622c;
    ((uint16_t *)((stack_record_18 + 12)))[1] = DAT_febe622e;
    ((uint16_t *)((stack_record_18 + 12)))[2] = DAT_febe6230;
    ((uint16_t *)((stack_record_18 + 12)))[3] = DAT_febe6232;
    (*((uint16_t *)(stack_record_18 + 20))) = DAT_febe6234;
    (*((uint16_t *)(stack_record_18 + 22))) = DAT_febe6236;
    ((uint16_t *)(stack_record_18))[0] = DAT_febe6238;
    ((uint16_t *)(stack_record_18))[1] = DAT_febe623a;
    ((uint16_t *)(stack_record_18))[2] = DAT_febe623c;
    ((uint16_t *)(stack_record_18))[3] = DAT_febe623e;
    (*((uint16_t *)(stack_record_18 + 8))) = DAT_febe6240;
    (*((uint16_t *)(stack_record_18 + 10))) = DAT_febe6242;
    iVar3 = 0;
    if (DAT_febe68b8 < 0x7f) {
      do {
        iVar1 = iVar3 * 4;
        uVar2 = ((uint16_t *)(stack_record_18))[iVar3];
        iVar4 = iVar3 + 1;
        *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe68d4u + (uint32_t)(iVar1) * 1u)))) = *(int *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe68d4u + (uint32_t)(iVar1) * 1u)))) + (uint)((uint16_t *)((stack_record_18 + 12)))[iVar3];
        *(uint *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe68ecu + (uint32_t)(iVar1) * 1u)))) = *(int *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe68ecu + (uint32_t)(iVar1) * 1u)))) + (uint)uVar2;
        iVar1 = iVar3 + -5;
        iVar3 = iVar4;
      } while (((iVar1 < 0) || (iVar4 < 0)));
      DAT_febe68b8 = DAT_febe68b8 + 1;
      return;
    }
    do {
      iVar1 = iVar3 * 4;
      uVar2 = ((uint16_t *)((stack_record_18 + 12)))[iVar3];
      iVar4 = *(int *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe68d4u + (uint32_t)(iVar1) * 1u))));
      *(undefined4 *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe68d4u + (uint32_t)(iVar1) * 1u)))) = 0;
      uVar5 = iVar4 + (uint)uVar2 >> 7;
      if (0xffff < uVar5) {
        uVar5 = 0xffff;
      }
      *(short *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe68bau + (uint32_t)(iVar3 * 2) * 1u)))) = (short)uVar5;
      uVar2 = ((uint16_t *)(stack_record_18))[iVar3];
      iVar4 = *(int *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe68ecu + (uint32_t)(iVar1) * 1u))));
      *(undefined4 *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe68ecu + (uint32_t)(iVar1) * 1u)))) = 0;
      uVar5 = iVar4 + (uint)uVar2 >> 7;
      if (0xffff < uVar5) {
        uVar5 = 0xffff;
      }
      *(short *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe68c6u + (uint32_t)(iVar3 * 2) * 1u)))) = (short)uVar5;
      iVar4 = iVar3 + 1;
      iVar1 = iVar3 + -5;
      iVar3 = iVar4;
    } while (((iVar1 < 0) || (iVar4 < 0)));
  }
  DAT_febe68b8 = 0;
  return;
}

void return_only_stub_32720(void)

{
  return;
}

void return_only_stub_32722(void)

{
  return;
}

uint monitor_current_coefficients_differ(void)

{
  uint uVar1;
  
  if (((((((monitor_current_active_calibration.coefficients.negative_residual_gain[0] ==
            monitor_current_staged_calibration.coefficients.negative_residual_gain[0]) &&
          (monitor_current_active_calibration.coefficients.negative_residual_gain[1] ==
           monitor_current_staged_calibration.coefficients.negative_residual_gain[1])) &&
         (monitor_current_active_calibration.coefficients.negative_residual_gain[2] ==
          monitor_current_staged_calibration.coefficients.negative_residual_gain[2])) &&
        ((monitor_current_active_calibration.coefficients.negative_residual_gain[3] ==
          monitor_current_staged_calibration.coefficients.negative_residual_gain[3] &&
         (monitor_current_active_calibration.coefficients.negative_residual_gain[4] ==
          monitor_current_staged_calibration.coefficients.negative_residual_gain[4])))) &&
       ((monitor_current_active_calibration.coefficients.negative_residual_gain[5] ==
         monitor_current_staged_calibration.coefficients.negative_residual_gain[5] &&
        ((monitor_current_active_calibration.coefficients.nonnegative_residual_gain[0] ==
          monitor_current_staged_calibration.coefficients.nonnegative_residual_gain[0] &&
         (monitor_current_active_calibration.coefficients.nonnegative_residual_gain[1] ==
          monitor_current_staged_calibration.coefficients.nonnegative_residual_gain[1])))))) &&
      (monitor_current_active_calibration.coefficients.nonnegative_residual_gain[2] ==
       monitor_current_staged_calibration.coefficients.nonnegative_residual_gain[2])) &&
     (((((monitor_current_active_calibration.coefficients.nonnegative_residual_gain[3] ==
          monitor_current_staged_calibration.coefficients.nonnegative_residual_gain[3] &&
         (monitor_current_active_calibration.coefficients.nonnegative_residual_gain[4] ==
          monitor_current_staged_calibration.coefficients.nonnegative_residual_gain[4])) &&
        (monitor_current_active_calibration.coefficients.nonnegative_residual_gain[5] ==
         monitor_current_staged_calibration.coefficients.nonnegative_residual_gain[5])) &&
       (((monitor_current_active_calibration.coefficients.bias[0] ==
          monitor_current_staged_calibration.coefficients.bias[0] &&
         (monitor_current_active_calibration.coefficients.bias[1] ==
          monitor_current_staged_calibration.coefficients.bias[1])) &&
        ((monitor_current_active_calibration.coefficients.bias[2] ==
          monitor_current_staged_calibration.coefficients.bias[2] &&
         ((monitor_current_active_calibration.coefficients.bias[3] ==
           monitor_current_staged_calibration.coefficients.bias[3] &&
          (monitor_current_active_calibration.coefficients.bias[4] ==
           monitor_current_staged_calibration.coefficients.bias[4])))))))) &&
      (monitor_current_active_calibration.coefficients.bias[5] ==
       monitor_current_staged_calibration.coefficients.bias[5])))) {
    uVar1 = 0;
  }
  else {
    uVar1 = 0x5a;
  }
  return uVar1;
}

void adopt_monitor_current_coefficients(void)

{
  monitor_current_active_calibration.coefficients.negative_residual_gain[0] =
       monitor_current_staged_calibration.coefficients.negative_residual_gain[0];
  monitor_current_active_calibration.coefficients.negative_residual_gain[1] =
       monitor_current_staged_calibration.coefficients.negative_residual_gain[1];
  monitor_current_active_calibration.coefficients.negative_residual_gain[2] =
       monitor_current_staged_calibration.coefficients.negative_residual_gain[2];
  monitor_current_active_calibration.coefficients.negative_residual_gain[3] =
       monitor_current_staged_calibration.coefficients.negative_residual_gain[3];
  monitor_current_active_calibration.coefficients.negative_residual_gain[4] =
       monitor_current_staged_calibration.coefficients.negative_residual_gain[4];
  monitor_current_active_calibration.coefficients.negative_residual_gain[5] =
       monitor_current_staged_calibration.coefficients.negative_residual_gain[5];
  monitor_current_active_calibration.coefficients.nonnegative_residual_gain[0] =
       monitor_current_staged_calibration.coefficients.nonnegative_residual_gain[0];
  monitor_current_active_calibration.coefficients.nonnegative_residual_gain[1] =
       monitor_current_staged_calibration.coefficients.nonnegative_residual_gain[1];
  monitor_current_active_calibration.coefficients.nonnegative_residual_gain[2] =
       monitor_current_staged_calibration.coefficients.nonnegative_residual_gain[2];
  monitor_current_active_calibration.coefficients.nonnegative_residual_gain[3] =
       monitor_current_staged_calibration.coefficients.nonnegative_residual_gain[3];
  monitor_current_active_calibration.coefficients.nonnegative_residual_gain[4] =
       monitor_current_staged_calibration.coefficients.nonnegative_residual_gain[4];
  monitor_current_active_calibration.coefficients.nonnegative_residual_gain[5] =
       monitor_current_staged_calibration.coefficients.nonnegative_residual_gain[5];
  monitor_current_active_calibration.coefficients.bias[0] =
       monitor_current_staged_calibration.coefficients.bias[0];
  monitor_current_active_calibration.coefficients.bias[1] =
       monitor_current_staged_calibration.coefficients.bias[1];
  monitor_current_active_calibration.coefficients.bias[2] =
       monitor_current_staged_calibration.coefficients.bias[2];
  monitor_current_active_calibration.coefficients.bias[3] =
       monitor_current_staged_calibration.coefficients.bias[3];
  monitor_current_active_calibration.coefficients.bias[4] =
       monitor_current_staged_calibration.coefficients.bias[4];
  monitor_current_active_calibration.coefficients.bias[5] =
       monitor_current_staged_calibration.coefficients.bias[5];
  return;
}

void reset_active_monitor_current_coefficients(void)

{
  monitor_current_active_calibration.coefficients.negative_residual_gain[0] = -0x41ca;
  monitor_current_active_calibration.coefficients.negative_residual_gain[1] = -0x41ca;
  monitor_current_active_calibration.coefficients.negative_residual_gain[2] = -0x41ca;
  monitor_current_active_calibration.coefficients.negative_residual_gain[3] = -0x41ca;
  monitor_current_active_calibration.coefficients.negative_residual_gain[4] = -0x41ca;
  monitor_current_active_calibration.coefficients.negative_residual_gain[5] = -0x41ca;
  monitor_current_active_calibration.coefficients.nonnegative_residual_gain[0] = -0x41ca;
  monitor_current_active_calibration.coefficients.nonnegative_residual_gain[1] = -0x41ca;
  monitor_current_active_calibration.coefficients.nonnegative_residual_gain[2] = -0x41ca;
  monitor_current_active_calibration.coefficients.nonnegative_residual_gain[3] = -0x41ca;
  monitor_current_active_calibration.coefficients.nonnegative_residual_gain[4] = -0x41ca;
  monitor_current_active_calibration.coefficients.nonnegative_residual_gain[5] = -0x41ca;
  monitor_current_active_calibration.coefficients.bias[0] = 0;
  monitor_current_active_calibration.coefficients.bias[1] = 0;
  monitor_current_active_calibration.coefficients.bias[2] = 0;
  monitor_current_active_calibration.coefficients.bias[3] = 0;
  monitor_current_active_calibration.coefficients.bias[4] = 0;
  monitor_current_active_calibration.coefficients.bias[5] = 0;
  return;
}

void update_active_monitor_current_calibration(void)

{
  uint32_t puVar1;
  uint uVar2;
  uint uVar3;
  
  puVar1 = 0xfebeb800u;
  if (DAT_febe8a18 != 'Z') {
    return;
  }
  uVar3 = (uint)monitor_current_active_calibration.changed;
  uVar2 = (uint)monitor_current_active_calibration.range_error;
  if ((monitor_current_staged_calibration.marker == 0xa55a5aa5) &&
     (monitor_current_staged_calibration.busy == '\0')) {
    puVar1 = 0xfebeb800u;
    uVar3 = monitor_current_coefficients_differ();
    if (uVar3 != 0x5a) {
      uVar2 = 0;
      goto LAB_000328c6;
    }
    uVar2 = get_staged_monitor_current_range_status();
    if (uVar2 == 0) {
      adopt_monitor_current_coefficients();
      goto LAB_000328c6;
    }
  }
  reset_active_monitor_current_coefficients();
LAB_000328c6:
  (*((char *)camry_host_ptr((uint32_t)((int)(0xffffb104u + (uint32_t)((int)puVar1)))))) = (char)uVar3;
  (*((char *)camry_host_ptr((uint32_t)((int)0xffffb104u + (int)(puVar1 + 1))))) = (char)uVar2;
  return;
}

void return_only_stub_328d2(void)

{
  return;
}

uint copy_monitor_calibration_from_rom_record(void)

{
  uint8_t stack_record_30[48];
  uint *puVar1;
  uint32_t puVar2;
  uint uVar3;
  undefined4 uVar4;
  undefined4 *puVar5;
  
  puVar2 = 0xfebeb800u;
  puVar1 = stack_record_30;
  puVar5 = ((undefined *)camry_host_ptr(0x21030u));
  do {
    uVar4 = *puVar5;
    puVar5 = puVar5 + 1;
    *puVar1 = uVar4;
    puVar1 = puVar1 + 1;
  } while (camry_host_addr(puVar5)!=((uint32_t)(0x21058u)));
  uVar3 = nvm_get_record(0x200, camry_host_addr(stack_record_30));
  if (uVar3 == 0x10) {
    (*((undefined2 *)camry_host_ptr((uint32_t)((int)(0xffffb12eu + (uint32_t)((int)puVar2)))))) = (*((uint16_t *)(stack_record_30 + 22)));
    (*((undefined2 *)camry_host_ptr((uint32_t)((int)(0xffffb130u + (uint32_t)((int)puVar2)))))) = (*((uint16_t *)(stack_record_30 + 24)));
    (*((undefined2 *)camry_host_ptr((uint32_t)((int)(0xffffb132u + (uint32_t)((int)puVar2)))))) = (*((uint16_t *)(stack_record_30 + 26)));
    (*((undefined2 *)camry_host_ptr((uint32_t)((int)(0xffffb134u + (uint32_t)((int)puVar2)))))) = (*((uint16_t *)(stack_record_30 + 4)));
    (*((undefined2 *)camry_host_ptr((uint32_t)((int)(0xffffb136u + (uint32_t)((int)puVar2)))))) = (*((uint16_t *)(stack_record_30 + 6)));
    (*((undefined2 *)camry_host_ptr((uint32_t)((int)(0xffffb138u + (uint32_t)((int)puVar2)))))) = (*((uint16_t *)(stack_record_30 + 8)));
    (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffb13au + (uint32_t)((int)puVar2)))))) = (*((uint16_t *)(stack_record_30 + 28)));
    (*((undefined2 *)camry_host_ptr((uint32_t)((int)(0xffffb13cu + (uint32_t)((int)puVar2)))))) = (*((uint16_t *)(stack_record_30 + 30)));
    (*((undefined2 *)camry_host_ptr((uint32_t)((int)(0xffffb13eu + (uint32_t)((int)puVar2)))))) = (*((uint16_t *)(stack_record_30 + 32)));
    (*((undefined2 *)camry_host_ptr((uint32_t)((int)(0xffffb140u + (uint32_t)((int)puVar2)))))) = (*((uint16_t *)(stack_record_30 + 10)));
    (*((undefined2 *)camry_host_ptr((uint32_t)((int)(0xffffb142u + (uint32_t)((int)puVar2)))))) = (*((uint16_t *)(stack_record_30 + 12)));
    (*((undefined2 *)camry_host_ptr((uint32_t)((int)(0xffffb144u + (uint32_t)((int)puVar2)))))) = (*((uint16_t *)(stack_record_30 + 14)));
    (*((undefined2 *)camry_host_ptr((uint32_t)((int)(0xffffb146u + (uint32_t)((int)puVar2)))))) = (*((uint16_t *)(stack_record_30 + 34)));
    (*((undefined2 *)camry_host_ptr((uint32_t)((int)(0xffffb148u + (uint32_t)((int)puVar2)))))) = (*((uint16_t *)(stack_record_30 + 36)));
    (*((undefined2 *)camry_host_ptr((uint32_t)((int)(0xffffb14au + (uint32_t)((int)puVar2)))))) = (*((uint16_t *)(stack_record_30 + 38)));
    (*((undefined2 *)camry_host_ptr((uint32_t)((int)(0xffffb14cu + (uint32_t)((int)puVar2)))))) = (*((uint16_t *)(stack_record_30 + 16)));
    (*((undefined2 *)camry_host_ptr((uint32_t)((int)(0xffffb14eu + (uint32_t)((int)puVar2)))))) = (*((uint16_t *)(stack_record_30 + 18)));
    (*((undefined2 *)camry_host_ptr((uint32_t)((int)(0xffffb150u + (uint32_t)((int)puVar2)))))) = (*((uint16_t *)(stack_record_30 + 20)));
  }
  return uVar3;
}

uint validate_staged_monitor_current_coefficients(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  int iVar6;
  uint uVar7;
  int iVar8;
  int iVar9;
  int iVar10;
  int iVar11;
  int iVar12;
  int iVar13;
  int iVar14;
  int iVar15;
  int iVar16;
  int iVar17;
  int iVar18;
  int iVar19;
  int iVar20;
  int iVar21;
  
  iVar15 = (int)monitor_current_staged_calibration.coefficients.negative_residual_gain[0];
  iVar14 = (int)monitor_current_staged_calibration.coefficients.negative_residual_gain[1];
  iVar13 = (int)monitor_current_staged_calibration.coefficients.negative_residual_gain[2];
  iVar12 = (int)monitor_current_staged_calibration.coefficients.nonnegative_residual_gain[0];
  iVar11 = (int)monitor_current_staged_calibration.coefficients.nonnegative_residual_gain[1];
  iVar10 = (int)monitor_current_staged_calibration.coefficients.nonnegative_residual_gain[2];
  iVar5 = (int)monitor_current_staged_calibration.coefficients.negative_residual_gain[3];
  iVar4 = (int)monitor_current_staged_calibration.coefficients.negative_residual_gain[4];
  iVar3 = (int)monitor_current_staged_calibration.coefficients.negative_residual_gain[5];
  iVar2 = (int)monitor_current_staged_calibration.coefficients.nonnegative_residual_gain[3];
  iVar21 = (int)monitor_current_staged_calibration.coefficients.nonnegative_residual_gain[4];
  iVar20 = (int)monitor_current_staged_calibration.coefficients.nonnegative_residual_gain[5];
  iVar9 = (int)monitor_current_staged_calibration.coefficients.bias[0];
  iVar8 = (int)monitor_current_staged_calibration.coefficients.bias[1];
  iVar6 = (int)monitor_current_staged_calibration.coefficients.bias[2];
  iVar19 = (int)monitor_current_staged_calibration.coefficients.bias[3];
  iVar18 = (int)monitor_current_staged_calibration.coefficients.bias[4];
  iVar17 = (int)monitor_current_staged_calibration.coefficients.bias[5];
  iVar1 = (int)((volatile int16_t *)camry_host_ptr(0x30ea0u))[0];
  if (((((((iVar15 - iVar1 < 0 == (iVar15 < 0 != iVar1 < 0 && iVar1 < 0 == iVar15 - iVar1 < 0) &&
            iVar15 != iVar1) ||
          (iVar16 = (int)(*((volatile int16_t *)camry_host_ptr((uint32_t)(0x30ea0u + (uint32_t)(1) * 2u)))),
          iVar15 - iVar16 < 0 != (iVar15 < 0 != iVar16 < 0 && iVar16 < 0 == iVar15 - iVar16 < 0)))
         || (iVar12 - iVar1 < 0 == (iVar12 < 0 != iVar1 < 0 && iVar1 < 0 == iVar12 - iVar1 < 0) &&
             iVar12 != iVar1)) ||
        ((iVar12 - iVar16 < 0 != (iVar12 < 0 != iVar16 < 0 && iVar16 < 0 == iVar12 - iVar16 < 0) ||
         (iVar14 - iVar1 < 0 == (iVar14 < 0 != iVar1 < 0 && iVar1 < 0 == iVar14 - iVar1 < 0) &&
          iVar14 != iVar1)))) ||
       ((iVar14 - iVar16 < 0 != (iVar14 < 0 != iVar16 < 0 && iVar16 < 0 == iVar14 - iVar16 < 0) ||
        ((iVar11 - iVar1 < 0 == (iVar11 < 0 != iVar1 < 0 && iVar1 < 0 == iVar11 - iVar1 < 0) &&
          iVar11 != iVar1 ||
         (iVar11 - iVar16 < 0 != (iVar11 < 0 != iVar16 < 0 && iVar16 < 0 == iVar11 - iVar16 < 0)))))
       )) || (iVar13 - iVar1 < 0 == (iVar13 < 0 != iVar1 < 0 && iVar1 < 0 == iVar13 - iVar1 < 0) &&
              iVar13 != iVar1)) ||
     ((((((iVar13 - iVar16 < 0 != (iVar13 < 0 != iVar16 < 0 && iVar16 < 0 == iVar13 - iVar16 < 0) ||
          (iVar10 - iVar1 < 0 == (iVar10 < 0 != iVar1 < 0 && iVar1 < 0 == iVar10 - iVar1 < 0) &&
           iVar10 != iVar1)) ||
         (iVar10 - iVar16 < 0 != (iVar10 < 0 != iVar16 < 0 && iVar16 < 0 == iVar10 - iVar16 < 0)))
        || (((iVar5 - iVar1 < 0 == (iVar5 < 0 != iVar1 < 0 && iVar1 < 0 == iVar5 - iVar1 < 0) &&
              iVar5 != iVar1 ||
             (iVar5 - iVar16 < 0 != (iVar5 < 0 != iVar16 < 0 && iVar16 < 0 == iVar5 - iVar16 < 0)))
            || ((iVar2 - iVar1 < 0 == (iVar2 < 0 != iVar1 < 0 && iVar1 < 0 == iVar2 - iVar1 < 0) &&
                 iVar2 != iVar1 ||
                ((iVar2 - iVar16 < 0 !=
                  (iVar2 < 0 != iVar16 < 0 && iVar16 < 0 == iVar2 - iVar16 < 0) ||
                 (iVar4 - iVar1 < 0 == (iVar4 < 0 != iVar1 < 0 && iVar1 < 0 == iVar4 - iVar1 < 0) &&
                  iVar4 != iVar1)))))))) ||
       ((((iVar4 - iVar16 < 0 != (iVar4 < 0 != iVar16 < 0 && iVar16 < 0 == iVar4 - iVar16 < 0) ||
          (((iVar21 - iVar1 < 0 == (iVar21 < 0 != iVar1 < 0 && iVar1 < 0 == iVar21 - iVar1 < 0) &&
             iVar21 != iVar1 ||
            (iVar21 - iVar16 < 0 != (iVar21 < 0 != iVar16 < 0 && iVar16 < 0 == iVar21 - iVar16 < 0))
            ) || (iVar3 - iVar1 < 0 == (iVar3 < 0 != iVar1 < 0 && iVar1 < 0 == iVar3 - iVar1 < 0) &&
                  iVar3 != iVar1)))) ||
         (((iVar3 - iVar16 < 0 != (iVar3 < 0 != iVar16 < 0 && iVar16 < 0 == iVar3 - iVar16 < 0) ||
           (iVar20 - iVar1 < 0 == (iVar20 < 0 != iVar1 < 0 && iVar1 < 0 == iVar20 - iVar1 < 0) &&
            iVar20 != iVar1)) ||
          (((iVar20 - iVar16 < 0 != (iVar20 < 0 != iVar16 < 0 && iVar16 < 0 == iVar20 - iVar16 < 0)
            || ((iVar1 = (int)(*((volatile int16_t *)camry_host_ptr((uint32_t)(0x30ea0u + (uint32_t)(2) * 2u)))),
                iVar9 - iVar1 < 0 == (iVar9 < 0 != iVar1 < 0 && iVar1 < 0 == iVar9 - iVar1 < 0) &&
                iVar9 != iVar1 ||
                (iVar2 = (int)(*((volatile int16_t *)camry_host_ptr((uint32_t)(0x30ea0u + (uint32_t)(3) * 2u)))),
                iVar9 - iVar2 < 0 != (iVar9 < 0 != iVar2 < 0 && iVar2 < 0 == iVar9 - iVar2 < 0)))))
           || (iVar8 - iVar1 < 0 == (iVar8 < 0 != iVar1 < 0 && iVar1 < 0 == iVar8 - iVar1 < 0) &&
               iVar8 != iVar1)))))) ||
        ((((iVar8 - iVar2 < 0 != (iVar8 < 0 != iVar2 < 0 && iVar2 < 0 == iVar8 - iVar2 < 0) ||
           (iVar6 - iVar1 < 0 == (iVar6 < 0 != iVar1 < 0 && iVar1 < 0 == iVar6 - iVar1 < 0) &&
            iVar6 != iVar1)) ||
          (iVar6 - iVar2 < 0 != (iVar6 < 0 != iVar2 < 0 && iVar2 < 0 == iVar6 - iVar2 < 0))) ||
         ((iVar19 - iVar1 < 0 == (iVar19 < 0 != iVar1 < 0 && iVar1 < 0 == iVar19 - iVar1 < 0) &&
           iVar19 != iVar1 ||
          (iVar19 - iVar2 < 0 != (iVar19 < 0 != iVar2 < 0 && iVar2 < 0 == iVar19 - iVar2 < 0))))))))
       ) || (((iVar18 - iVar1 < 0 == (iVar18 < 0 != iVar1 < 0 && iVar1 < 0 == iVar18 - iVar1 < 0) &&
               iVar18 != iVar1 ||
              ((iVar18 - iVar2 < 0 != (iVar18 < 0 != iVar2 < 0 && iVar2 < 0 == iVar18 - iVar2 < 0)
               || (iVar17 - iVar1 < 0 ==
                   (iVar17 < 0 != iVar1 < 0 && iVar1 < 0 == iVar17 - iVar1 < 0) && iVar17 != iVar1))
              )) || (iVar17 - iVar2 < 0 !=
                     (iVar17 < 0 != iVar2 < 0 && iVar2 < 0 == iVar17 - iVar2 < 0))))))) {
    uVar7 = 0x5a;
  }
  else {
    uVar7 = 0;
  }
  return uVar7;
}

void reset_staged_monitor_current_coefficients(void)

{
  monitor_current_staged_calibration.coefficients.negative_residual_gain[0] = -0x41ca;
  monitor_current_staged_calibration.coefficients.negative_residual_gain[1] = -0x41ca;
  monitor_current_staged_calibration.coefficients.negative_residual_gain[2] = -0x41ca;
  monitor_current_staged_calibration.coefficients.negative_residual_gain[3] = -0x41ca;
  monitor_current_staged_calibration.coefficients.negative_residual_gain[4] = -0x41ca;
  monitor_current_staged_calibration.coefficients.negative_residual_gain[5] = -0x41ca;
  monitor_current_staged_calibration.coefficients.nonnegative_residual_gain[0] = -0x41ca;
  monitor_current_staged_calibration.coefficients.nonnegative_residual_gain[1] = -0x41ca;
  monitor_current_staged_calibration.coefficients.nonnegative_residual_gain[2] = -0x41ca;
  monitor_current_staged_calibration.coefficients.nonnegative_residual_gain[3] = -0x41ca;
  monitor_current_staged_calibration.coefficients.nonnegative_residual_gain[4] = -0x41ca;
  monitor_current_staged_calibration.coefficients.nonnegative_residual_gain[5] = -0x41ca;
  monitor_current_staged_calibration.coefficients.bias[0] = 0;
  monitor_current_staged_calibration.coefficients.bias[1] = 0;
  monitor_current_staged_calibration.coefficients.bias[2] = 0;
  monitor_current_staged_calibration.coefficients.bias[3] = 0;
  monitor_current_staged_calibration.coefficients.bias[4] = 0;
  monitor_current_staged_calibration.coefficients.bias[5] = 0;
  return;
}

uint validate_or_reset_staged_monitor_current_coefficients(void)

{
  uint32_t puVar1;
  uint uVar2;
  
  puVar1 = 0xfebeb800u;
  uVar2 = validate_staged_monitor_current_coefficients();
  if (uVar2 == 0x5a) {
    (*((undefined2 *)camry_host_ptr((uint32_t)((int)(0xffffb12eu + (uint32_t)((int)puVar1)))))) = 0xbe36;
    (*((undefined2 *)camry_host_ptr((uint32_t)((int)(0xffffb130u + (uint32_t)((int)puVar1)))))) = 0xbe36;
    (*((undefined2 *)camry_host_ptr((uint32_t)((int)(0xffffb132u + (uint32_t)((int)puVar1)))))) = 0xbe36;
    (*((undefined2 *)camry_host_ptr((uint32_t)((int)(0xffffb134u + (uint32_t)((int)puVar1)))))) = 0xbe36;
    (*((undefined2 *)camry_host_ptr((uint32_t)((int)(0xffffb136u + (uint32_t)((int)puVar1)))))) = 0xbe36;
    (*((undefined2 *)camry_host_ptr((uint32_t)((int)(0xffffb138u + (uint32_t)((int)puVar1)))))) = 0xbe36;
    (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffb13au + (uint32_t)((int)puVar1)))))) = 0xbe36;
    (*((undefined2 *)camry_host_ptr((uint32_t)((int)(0xffffb13cu + (uint32_t)((int)puVar1)))))) = 0xbe36;
    (*((undefined2 *)camry_host_ptr((uint32_t)((int)(0xffffb13eu + (uint32_t)((int)puVar1)))))) = 0xbe36;
    (*((undefined2 *)camry_host_ptr((uint32_t)((int)(0xffffb140u + (uint32_t)((int)puVar1)))))) = 0xbe36;
    (*((undefined2 *)camry_host_ptr((uint32_t)((int)(0xffffb142u + (uint32_t)((int)puVar1)))))) = 0xbe36;
    (*((undefined2 *)camry_host_ptr((uint32_t)((int)(0xffffb144u + (uint32_t)((int)puVar1)))))) = 0xbe36;
    (*((undefined2 *)camry_host_ptr((uint32_t)((int)(0xffffb146u + (uint32_t)((int)puVar1)))))) = 0;
    (*((undefined2 *)camry_host_ptr((uint32_t)((int)(0xffffb148u + (uint32_t)((int)puVar1)))))) = 0;
    (*((undefined2 *)camry_host_ptr((uint32_t)((int)(0xffffb14au + (uint32_t)((int)puVar1)))))) = 0;
    (*((undefined2 *)camry_host_ptr((uint32_t)((int)(0xffffb14cu + (uint32_t)((int)puVar1)))))) = 0;
    (*((undefined2 *)camry_host_ptr((uint32_t)((int)(0xffffb14eu + (uint32_t)((int)puVar1)))))) = 0;
    (*((undefined2 *)camry_host_ptr((uint32_t)((int)(0xffffb150u + (uint32_t)((int)puVar1)))))) = 0;
  }
  return uVar2;
}

void restore_monitor_current_calibration(void)

{
  uint32_t puVar1;
  uint uVar2;
  undefined4 uVar3;
  undefined1 uVar4;
  uint local_34 [10];
  
  puVar1 = 0xfebeb800u;
  uVar2 = nvm_get_record(0x200, camry_host_addr(local_34));
  if ((uVar2 == 0x10) && (local_34[0] == 0xa55a5aa5)) {
    copy_monitor_calibration_from_rom_record();
    uVar2 = validate_or_reset_staged_monitor_current_coefficients();
    if (uVar2 == 0) {
      uVar3 = 0xa55a5aa5;
      uVar4 = 0x44;
      report_diagnostic_healthy_observed(0x124);
      goto LAB_00032ae4;
    }
  }
  uVar3 = 0x5aa5a55a;
  uVar4 = 0x22;
  report_diagnostic_event_failure(0x124,0x32);
LAB_00032ae4:
  (*((undefined4 *)camry_host_ptr((uint32_t)((int)(0xffffb154u + (uint32_t)((int)puVar1)))))) = uVar3;
  (*((undefined1 *)camry_host_ptr((uint32_t)((int)(0xffffb12cu + (uint32_t)((int)puVar1)))))) = uVar4;
  return;
}

uint reload_monitor_current_calibration_marker(void)

{
  uint uVar1;
  uint local_2c [10];
  
  uVar1 = nvm_get_record(0x200, camry_host_addr(local_2c));
  if ((uVar1 == 0x10) && (local_2c[0] == 0xa55a5aa5)) {
    copy_monitor_calibration_from_rom_record();
    uVar1 = validate_or_reset_staged_monitor_current_coefficients();
    if (uVar1 == 0) {
      return 0xa55a5aa5;
    }
  }
  return 0x5aa5a55a;
}

void refresh_monitor_current_calibration(void)

{
  uint32_t puVar1;
  uint uVar2;
  undefined1 uVar3;
  
  puVar1 = 0xfebeb800u;
  uVar3 = 0;
  uVar2 = monitor_current_staged_calibration.marker;
  if ((DAT_febe6501 == 'Z') && (monitor_current_staged_calibration.marker == 0xa55a5aa5)) {
    uVar3 = 0x5a;
    monitor_current_staged_calibration.busy = 'Z';
    puVar1 = 0xfebeb800u;
    uVar2 = reload_monitor_current_calibration_marker();
    if (uVar2 == 0xa55a5aa5) {
      uVar3 = 0;
    }
    else {
      report_diagnostic_event_failure(0x124,0x32);
    }
  }
  (*((uint *)camry_host_ptr((uint32_t)((int)(0xffffb154u + (uint32_t)((int)puVar1)))))) = uVar2;
  (*((undefined1 *)camry_host_ptr((uint32_t)((int)0xffffb12cu + (int)(puVar1 + 1))))) = uVar3;
  return;
}

void submit_monitor_current_calibration_record(void)

{
  uint8_t stack_record_30[48];
  uint32_t puVar1;
  
  puVar1 = 0xfebeb800u;
  (*((uint32_t *)(stack_record_30 + 0))) = 0xa55a5aa5;
  (*((int16_t *)(stack_record_30 + 22))) = monitor_current_staged_calibration.coefficients.negative_residual_gain[0];
  (*((int16_t *)(stack_record_30 + 24))) = monitor_current_staged_calibration.coefficients.negative_residual_gain[1];
  (*((int16_t *)(stack_record_30 + 26))) = monitor_current_staged_calibration.coefficients.negative_residual_gain[2];
  (*((int16_t *)(stack_record_30 + 4))) = monitor_current_staged_calibration.coefficients.negative_residual_gain[3];
  (*((int16_t *)(stack_record_30 + 6))) = monitor_current_staged_calibration.coefficients.negative_residual_gain[4];
  (*((int16_t *)(stack_record_30 + 8))) = monitor_current_staged_calibration.coefficients.negative_residual_gain[5];
  (*((int16_t *)(stack_record_30 + 28))) = monitor_current_staged_calibration.coefficients.nonnegative_residual_gain[0];
  (*((int16_t *)(stack_record_30 + 30))) = monitor_current_staged_calibration.coefficients.nonnegative_residual_gain[1];
  (*((int16_t *)(stack_record_30 + 32))) = monitor_current_staged_calibration.coefficients.nonnegative_residual_gain[2];
  (*((int16_t *)(stack_record_30 + 10))) = monitor_current_staged_calibration.coefficients.nonnegative_residual_gain[3];
  (*((int16_t *)(stack_record_30 + 12))) = monitor_current_staged_calibration.coefficients.nonnegative_residual_gain[4];
  (*((int16_t *)(stack_record_30 + 14))) = monitor_current_staged_calibration.coefficients.nonnegative_residual_gain[5];
  (*((int16_t *)(stack_record_30 + 34))) = monitor_current_staged_calibration.coefficients.bias[0];
  (*((int16_t *)(stack_record_30 + 36))) = monitor_current_staged_calibration.coefficients.bias[1];
  (*((int16_t *)(stack_record_30 + 38))) = monitor_current_staged_calibration.coefficients.bias[2];
  (*((int16_t *)(stack_record_30 + 16))) = monitor_current_staged_calibration.coefficients.bias[3];
  (*((int16_t *)(stack_record_30 + 18))) = monitor_current_staged_calibration.coefficients.bias[4];
  (*((int16_t *)(stack_record_30 + 20))) = monitor_current_staged_calibration.coefficients.bias[5];
  nvm_set_record(0x200,stack_record_30);
  (*((undefined4 *)camry_host_ptr((uint32_t)((int)(0xffffb154u + (uint32_t)((int)puVar1)))))) = 0xa55a5aa5;
  return;
}

uint get_staged_monitor_current_range_status(void)

{
  uint uVar1;
  
  uVar1 = validate_staged_monitor_current_coefficients();
  return uVar1;
}

void return_only_stub_32c84(void)

{
  return;
}

void clear_state_bytes_6958_and_counter_695c_32c86(void)

{
  DAT_febe6958 = 0;
  DAT_febe6959 = 0;
  DAT_febe695c = 0;
  DAT_febe695a = 0;
  return;
}

void step_mode600_fit_request(void)

{
  char cVar1;
  uint32_t puVar2;
  undefined1 uVar3;
  undefined2 uVar4;
  undefined1 uVar5;
  
  uVar4 = ((int)(int16_t)DAT_febe695c);
  uVar5 = DAT_febe6959;
  puVar2 = 0xfebeb800u;
  if (DAT_febe695a == 'Z') {
    uVar3 = 0x5a;
    if (DAT_febe6958 == '\0') {
      puVar2 = 0xfebeb800u;
      request_six_channel_fit();
      cVar1 = '\x01';
    }
    else {
      cVar1 = DAT_febe6958;
      if (DAT_febe6958 == '\x01') {
        if (DAT_febe6a5d != '\0') {
          uVar5 = 0x5a;
          uVar4 = DAT_00030ea8;
          cVar1 = '\x02';
        }
      }
      else if (DAT_febe6958 == '\x02') {
        if (DAT_febe6a5d == '\"') {
          uVar5 = 0;
          uVar4 = 0;
          cVar1 = '\x03';
        }
        else if (DAT_febe6a5d == 'D') {
          uVar5 = 0;
          uVar4 = 0;
          cVar1 = '\x04';
        }
      }
      else {
        uVar3 = 0;
      }
    }
    (*((char *)camry_host_ptr((uint32_t)((int)(0xffffb158u + (uint32_t)((int)puVar2)))))) = cVar1;
    (*((undefined1 *)camry_host_ptr((uint32_t)((int)0xffffb158u + (int)(puVar2 + 1))))) = uVar5;
    (*((undefined2 *)camry_host_ptr((uint32_t)((int)(0xffffb15cu + (uint32_t)((int)puVar2)))))) = uVar4;
    (*((undefined1 *)camry_host_ptr((uint32_t)((int)(0xffffb15au + (uint32_t)((int)puVar2)))))) = uVar3;
  }
  return;
}

void return_only_stub_32d22(void)

{
  return;
}

void return_only_stub_32d24(void)

{
  return;
}

uint track_fit_angular_coverage(short angle,uchar required_spans)

{
  int iVar1;
  uint uVar2;
  int iVar3;
  int iVar4;
  
  iVar1 = (int)(short)(angle - six_channel_fit_work.previous_angle);
  six_channel_fit_work.coverage_sum = six_channel_fit_work.coverage_sum + iVar1;
  iVar3 = six_channel_fit_work.coverage_max;
  if ((((-1 < iVar1) || (-1 < six_channel_fit_work.coverage_sum)) ||
      (iVar4 = six_channel_fit_work.coverage_sum,
      six_channel_fit_work.coverage_sum - six_channel_fit_work.coverage_min < 0 ==
      (six_channel_fit_work.coverage_sum < 0 != six_channel_fit_work.coverage_min < 0 &&
      six_channel_fit_work.coverage_min < 0 ==
      six_channel_fit_work.coverage_sum - six_channel_fit_work.coverage_min < 0))) &&
     (((iVar4 = six_channel_fit_work.coverage_min, 0 < iVar1 &&
       (0 < six_channel_fit_work.coverage_sum)) &&
      (iVar3 = six_channel_fit_work.coverage_sum,
      six_channel_fit_work.coverage_sum - six_channel_fit_work.coverage_max < 0 !=
      (six_channel_fit_work.coverage_sum < 0 != six_channel_fit_work.coverage_max < 0 &&
      six_channel_fit_work.coverage_max < 0 ==
      six_channel_fit_work.coverage_sum - six_channel_fit_work.coverage_max < 0) ||
      six_channel_fit_work.coverage_sum == six_channel_fit_work.coverage_max)))) {
    iVar3 = six_channel_fit_work.coverage_max;
  }
  uVar2 = 0;
  iVar1 = (iVar3 - iVar4) + -0x10000;
  if (iVar1 < 0 == (iVar3 - iVar4 < 0 && -1 < iVar1)) {
    six_channel_fit_work.coverage_sum = 0;
    six_channel_fit_work.coverage_count = six_channel_fit_work.coverage_count + 1;
    iVar4 = 0;
    iVar3 = 0;
    uVar2 = 0x5a;
    if (required_spans <= six_channel_fit_work.coverage_count) {
      uVar2 = 0xa5;
    }
  }
  six_channel_fit_work.coverage_min = iVar4;
  six_channel_fit_work.coverage_max = iVar3;
  return uVar2;
}

void step_unsigned_literal_fit_sweep(short angle)

{
  ushort uVar1;
  ushort uVar2;
  ushort uVar3;
  int iVar4;
  uint32_t puVar5;
  uint uVar6;
  uint uVar7;
  int iVar8;
  uint uVar9;
  uint uVar10;
  uint uVar11;
  uint uVar12;
  uint uVar13;
  uint uVar14;
  uint uVar15;
  uint uVar16;
  uchar local_4c;
  uchar uStack_4b;
  ushort uStack_4a;
  ushort uStack_48;
  ushort uStack_46;
  ushort uStack_44;
  ushort uStack_42;
  ushort uStack_40;
  ushort uStack_3e;
  ushort uStack_3c;
  ushort uStack_3a;
  ushort uStack_38;
  ushort uStack_36;
  ushort uStack_34;
  ushort uStack_32;
  ushort uStack_30;
  ushort uStack_2e;
  
  puVar5 = 0xfebeb800u;
  iVar4 = (int)((int)(int16_t)DAT_febe5f36);
  uStack_2e = six_channel_fit_work.unsigned_min[5];
  uStack_4a = six_channel_fit_work.unsigned_previous[3];
  uStack_48 = six_channel_fit_work.unsigned_previous[4];
  uStack_46 = six_channel_fit_work.unsigned_previous[5];
  uStack_38 = six_channel_fit_work.unsigned_min[0];
  uStack_36 = six_channel_fit_work.unsigned_min[1];
  uStack_34 = six_channel_fit_work.unsigned_min[2];
  uStack_32 = six_channel_fit_work.unsigned_min[3];
  uStack_30 = six_channel_fit_work.unsigned_min[4];
  local_4c = six_channel_fit_work.unsigned_initialized;
  uStack_4b = six_channel_fit_work.state;
  uStack_44 = six_channel_fit_work.unsigned_max[0];
  uStack_42 = six_channel_fit_work.unsigned_max[1];
  uStack_40 = six_channel_fit_work.unsigned_max[2];
  uStack_3e = six_channel_fit_work.unsigned_max[3];
  uStack_3c = six_channel_fit_work.unsigned_max[4];
  uStack_3a = six_channel_fit_work.unsigned_max[5];
  if (iVar4 + 0x7fff < 0 == (-1 < iVar4 && iVar4 + 0x7fff < 0) && iVar4 != -0x7fff) {
    if (iVar4 < 0) {
      iVar4 = (int)-((int)(int16_t)DAT_febe5f36);
    }
  }
  else {
    iVar4 = 0x7fff;
  }
  if (((DAT_febe7db0 < fit_parameters.qualifier_lower) ||
      (fit_parameters.qualifier_upper < DAT_febe7db0)) ||
     (iVar8 = (int)fit_parameters.magnitude_upper,
     iVar4 - iVar8 < 0 == (iVar4 < 0 != iVar8 < 0 && iVar8 < 0 == iVar4 - iVar8 < 0) &&
     iVar4 != iVar8)) {
    local_4c = '\0';
  }
  else {
    uVar7 = 0x80000000;
    if (six_channel_fit_work.unsigned_initialized == '\0') {
      uVar16 = 0x8000;
      uStack_4a = 0x8000;
      uStack_48 = 0x8000;
      uStack_46 = 0x8000;
      uVar10 = 0x8000;
      uStack_44 = 0x8000;
      uVar9 = 0x8000;
      uStack_42 = 0x8000;
      uStack_40 = 0x8000;
      uStack_3e = 0x8000;
      uStack_3c = 0x8000;
      uStack_3a = 0x8000;
      uStack_38 = 0x8000;
      uStack_36 = 0x8000;
      uStack_34 = 0x8000;
      uStack_32 = 0x8000;
      uStack_30 = 0x8000;
      uStack_2e = 0x8000;
      six_channel_fit_work.coverage_count = '\0';
      six_channel_fit_work.coverage_sum = 0;
      six_channel_fit_work.coverage_min = 0;
      six_channel_fit_work.coverage_max = 0;
      local_4c = 'Z';
      uVar11 = uVar7;
      uVar12 = uVar7;
      uVar13 = uVar7;
      uVar14 = uVar7;
      uVar15 = uVar7;
    }
    else {
      iVar4 = (uint)fit_parameters.unsigned_filter_half_gain * 2;
      uVar6 = iVar4 - 1;
      if (uVar6 < 0xffff) {
        uVar15 = (uint)fit_parameters.unsigned_filter_half_gain * 0x10000 +
                 (six_channel_fit_work.unsigned_q16[0] -
                 (uint)six_channel_fit_work.unsigned_previous[0] * iVar4);
      }
      else {
        uVar15 = six_channel_fit_work.unsigned_q16[0] +
                 (uint)six_channel_fit_work.unsigned_previous[0] * -0x10000 + 0x80000000;
      }
      uVar16 = uVar15 >> 0x10;
      if (uVar6 < 0xffff) {
        uVar14 = (uint)fit_parameters.unsigned_filter_half_gain * 0x10000 +
                 (six_channel_fit_work.unsigned_q16[1] -
                 (uint)six_channel_fit_work.unsigned_previous[1] * iVar4);
      }
      else {
        uVar14 = six_channel_fit_work.unsigned_q16[1] +
                 (uint)six_channel_fit_work.unsigned_previous[1] * -0x10000 + 0x80000000;
      }
      uVar10 = uVar14 >> 0x10;
      if (uVar6 < 0xffff) {
        uVar13 = (uint)fit_parameters.unsigned_filter_half_gain * 0x10000 +
                 (six_channel_fit_work.unsigned_q16[2] -
                 (uint)six_channel_fit_work.unsigned_previous[2] * iVar4);
      }
      else {
        uVar13 = six_channel_fit_work.unsigned_q16[2] +
                 (uint)six_channel_fit_work.unsigned_previous[2] * -0x10000 + 0x80000000;
      }
      uVar9 = uVar13 >> 0x10;
      if (uVar6 < 0xffff) {
        uVar12 = (uint)fit_parameters.unsigned_filter_half_gain * 0x10000 +
                 (six_channel_fit_work.unsigned_q16[3] -
                 (uint)six_channel_fit_work.unsigned_previous[3] * iVar4);
      }
      else {
        uVar12 = six_channel_fit_work.unsigned_q16[3] +
                 (uint)six_channel_fit_work.unsigned_previous[3] * -0x10000 + 0x80000000;
      }
      uStack_4a = (ushort)(uVar12 >> 0x10);
      if (uVar6 < 0xffff) {
        uVar11 = (uint)fit_parameters.unsigned_filter_half_gain * 0x10000 +
                 (six_channel_fit_work.unsigned_q16[4] -
                 (uint)six_channel_fit_work.unsigned_previous[4] * iVar4);
      }
      else {
        uVar11 = six_channel_fit_work.unsigned_q16[4] +
                 (uint)six_channel_fit_work.unsigned_previous[4] * -0x10000 + 0x80000000;
      }
      uStack_48 = (ushort)(uVar11 >> 0x10);
      if (uVar6 < 0xffff) {
        iVar8 = (uint)fit_parameters.unsigned_filter_half_gain << 0x10;
        uVar7 = six_channel_fit_work.unsigned_q16[5] -
                (uint)six_channel_fit_work.unsigned_previous[5] * iVar4;
      }
      else {
        iVar8 = six_channel_fit_work.unsigned_q16[5] +
                (uint)six_channel_fit_work.unsigned_previous[5] * -0x10000;
      }
      uVar7 = iVar8 + uVar7;
      uVar6 = uVar7 >> 0x10;
      uStack_46 = (ushort)(uVar7 >> 0x10);
      uVar1 = (ushort)(uVar15 >> 0x10);
      if (-1 < (int)(uVar16 - six_channel_fit_work.unsigned_max[0]) &&
          uVar16 != six_channel_fit_work.unsigned_max[0]) {
        uStack_44 = uVar1;
      }
      uVar2 = (ushort)(uVar14 >> 0x10);
      if (-1 < (int)(uVar10 - six_channel_fit_work.unsigned_max[1]) &&
          uVar10 != six_channel_fit_work.unsigned_max[1]) {
        uStack_42 = uVar2;
      }
      uVar3 = (ushort)(uVar13 >> 0x10);
      if (-1 < (int)(uVar9 - six_channel_fit_work.unsigned_max[2]) &&
          uVar9 != six_channel_fit_work.unsigned_max[2]) {
        uStack_40 = uVar3;
      }
      if (-1 < (int)((uint)uStack_4a - (uint)six_channel_fit_work.unsigned_max[3]) &&
          (uint)uStack_4a != (uint)six_channel_fit_work.unsigned_max[3]) {
        uStack_3e = uStack_4a;
      }
      if (-1 < (int)((uint)uStack_48 - (uint)six_channel_fit_work.unsigned_max[4]) &&
          (uint)uStack_48 != (uint)six_channel_fit_work.unsigned_max[4]) {
        uStack_3c = uStack_48;
      }
      if (-1 < (int)(uVar6 - six_channel_fit_work.unsigned_max[5]) &&
          uVar6 != six_channel_fit_work.unsigned_max[5]) {
        uStack_3a = uStack_46;
      }
      if ((int)(uVar16 - six_channel_fit_work.unsigned_min[0]) < 0) {
        uStack_38 = uVar1;
      }
      if ((int)(uVar10 - six_channel_fit_work.unsigned_min[1]) < 0) {
        uStack_36 = uVar2;
      }
      if ((int)(uVar9 - six_channel_fit_work.unsigned_min[2]) < 0) {
        uStack_34 = uVar3;
      }
      if ((int)((uint)uStack_4a - (uint)six_channel_fit_work.unsigned_min[3]) < 0) {
        uStack_32 = uStack_4a;
      }
      if ((int)((uint)uStack_48 - (uint)six_channel_fit_work.unsigned_min[4]) < 0) {
        uStack_30 = uStack_48;
      }
      if ((int)(uVar6 - six_channel_fit_work.unsigned_min[5]) < 0) {
        uStack_2e = uStack_46;
      }
    }
    puVar5 = 0xfebeb800u;
    uVar6 = track_fit_angular_coverage(angle,fit_parameters.unsigned_coverage_spans);
    six_channel_fit_work.unsigned_q16[5] = uVar7;
    six_channel_fit_work.unsigned_q16[4] = uVar11;
    six_channel_fit_work.unsigned_q16[3] = uVar12;
    six_channel_fit_work.unsigned_q16[2] = uVar13;
    six_channel_fit_work.unsigned_q16[1] = uVar14;
    six_channel_fit_work.unsigned_q16[0] = uVar15;
    six_channel_fit_work.unsigned_previous[0] = (ushort)uVar16;
    six_channel_fit_work.unsigned_previous[1] = (ushort)uVar10;
    six_channel_fit_work.unsigned_previous[2] = (ushort)uVar9;
    if (uVar6 == 0xa5) {
      uStack_4b = '\"';
    }
  }
  (*((uchar *)camry_host_ptr((uint32_t)((int)(0xffffb162u + (uint32_t)((int)puVar5)))))) = local_4c;
  (*((uchar *)camry_host_ptr((uint32_t)((int)(0xffffb160u + (uint32_t)((int)puVar5)))))) = uStack_4b;
  six_channel_fit_work.unsigned_max[0] = uStack_44;
  six_channel_fit_work.unsigned_max[1] = uStack_42;
  six_channel_fit_work.unsigned_max[2] = uStack_40;
  six_channel_fit_work.unsigned_max[3] = uStack_3e;
  six_channel_fit_work.unsigned_max[4] = uStack_3c;
  six_channel_fit_work.unsigned_max[5] = uStack_3a;
  six_channel_fit_work.unsigned_min[0] = uStack_38;
  six_channel_fit_work.unsigned_min[1] = uStack_36;
  six_channel_fit_work.unsigned_min[2] = uStack_34;
  six_channel_fit_work.unsigned_min[3] = uStack_32;
  six_channel_fit_work.unsigned_min[4] = uStack_30;
  six_channel_fit_work.unsigned_min[5] = uStack_2e;
  six_channel_fit_work.unsigned_previous[3] = uStack_4a;
  six_channel_fit_work.unsigned_previous[5] = uStack_46;
  six_channel_fit_work.unsigned_previous[4] = uStack_48;
  return;
}
