#include "common.h"

void return_only_stub_4a446(void)

{
  return;
}

void return_only_stub_4a448(void)

{
  return;
}

void seed_communication_inhibit_state_pair_4a44a(void)

{
  DAT_febe7f94 = 0;
  DAT_febe7f95 = 1;
  return;
}

void update_application_communication_inhibits(void)

{
  if ((DAT_febee86d == 'Z') &&
     (((DAT_febe7f95 == '\0' || (DAT_febee860 != '\0')) && (DAT_febe7f94 == '\x01')))) {
    DAT_febe7f98 = 0;
    DAT_febe7f97 = 0x5a;
    DAT_febe7f96 = 0x5a;
  }
  else {
    DAT_febe7f97 = 0;
    if (DAT_febe7f98 < DAT_000317b8) {
      DAT_febe7f98 = DAT_febe7f98 + 1;
    }
    else {
      DAT_febe7f96 = 0;
    }
  }
  return;
}

void initialize_and_update_communication_inhibits_4a49e(void)

{
  seed_communication_inhibit_state_pair_4a44a();
  update_application_communication_inhibits();
  return;
}

void return_only_stub_4a4ae(void)

{
  return;
}

void return_only_stub_4a4b0(void)

{
  return;
}

bool test_nonzero_communication_state_without_two_inhibits_4a4b2(void)

{
  if ((DAT_febee81f != '\0') && (DAT_febee828 != 'Z')) {
    return DAT_febee825 != 'Z';
  }
  return false;
}

void clear_qualified_route30_timeout_progress_4a4d4(void)

{
  DAT_febe7fa8 = 0;
  DAT_febe7fac = 0;
  if (DAT_febe7f9f == '\x11') {
    DAT_febe7f9f = '\0';
  }
  if (DAT_febe7fa1 == '\x11') {
    DAT_febe7fa1 = '\0';
  }
  return;
}

void step_route30_timeout_state_7fa0_4a4f6(void)

{
  if (route30_receive_status == '\0') {
    DAT_febe7fa4 = 0;
    DAT_febe7fa1 = 0;
    DAT_febe7faa = 0;
    DAT_febe7fa0 = 0;
  }
  else if (((DAT_febe7fa0 == '\0') || (DAT_febe7fa0 == '\x11')) && (DAT_febe7faa < DAT_0002baf0)) {
    DAT_febe7faa = DAT_febe7faa + 1;
    DAT_febe7fa0 = 0x11;
  }
  else {
    DAT_febe7fa0 = 0x22;
    DAT_febe7fa4 = 0x5a;
  }
  DAT_febe7f9e = 0;
  DAT_febe7f9f = 0;
  DAT_febe7fa2 = 0;
  DAT_febe7fa3 = 0;
  DAT_febe7fa6 = 0;
  DAT_febe7fa8 = 0;
  return;
}

void step_route30_timeout_state_7f9e_4a54a(void)

{
  if (route30_receive_status == '\0') {
    DAT_febe7fa2 = 0;
    DAT_febe7f9f = 0;
    DAT_febe7fa6 = 0;
    DAT_febe7f9e = 0;
  }
  else if (((DAT_febe7f9e == '\0') || (DAT_febe7f9e == '\x11')) && (DAT_febe7fa6 < DAT_0002baee)) {
    DAT_febe7fa6 = DAT_febe7fa6 + 1;
    DAT_febe7f9e = 0x11;
  }
  else {
    DAT_febe7f9e = 0x22;
    DAT_febe7fa2 = 0x5a;
  }
  DAT_febe7fa0 = 0;
  DAT_febe7fa1 = 0;
  DAT_febe7fa4 = 0;
  DAT_febe7fa5 = 0;
  DAT_febe7faa = 0;
  DAT_febe7fac = 0;
  return;
}

void fill_constant_block_4a59e(void)

{
  DAT_febe7f9e = 0;
  DAT_febe7f9f = 0;
  DAT_febe7fa2 = 0;
  DAT_febe7fa3 = 0;
  DAT_febe7fa6 = 0;
  DAT_febe7fa8 = 0;
  DAT_febe7fa0 = 0;
  DAT_febe7fa1 = 0;
  DAT_febe7fa4 = 0;
  DAT_febe7fa5 = 0;
  DAT_febe7faa = 0;
  DAT_febe7fac = 0;
  return;
}

void clear_unqualified_route30_timeout_progress_4a5bc(void)

{
  DAT_febe7fa6 = 0;
  DAT_febe7faa = 0;
  if (DAT_febe7f9e == '\x11') {
    DAT_febe7f9e = '\0';
  }
  if (DAT_febe7fa0 == '\x11') {
    DAT_febe7fa0 = '\0';
  }
  return;
}

void step_qualified_route30_timeout_state_7fa1_4a5de(void)

{
  if (route30_receive_status == '\0') {
    DAT_febe7fa5 = 0;
    DAT_febe7fa0 = 0;
    DAT_febe7fac = 0;
    DAT_febe7fa4 = 0;
    DAT_febe7fa1 = '\0';
  }
  else if ((DAT_febee812 == '\x11') && (DAT_0002bb24 <= DAT_febee892)) {
    if (((DAT_febe7fa1 == '\0') || (DAT_febe7fa1 == '\x11')) && (DAT_febe7fac < DAT_0002baf2)) {
      DAT_febe7fac = DAT_febe7fac + 1;
      DAT_febe7fa1 = '\x11';
    }
    else {
      DAT_febe7fa1 = '\"';
      DAT_febe7fa5 = 0x5a;
    }
  }
  DAT_febe7f9e = 0;
  DAT_febe7f9f = 0;
  DAT_febe7fa2 = 0;
  DAT_febe7fa3 = 0;
  DAT_febe7fa6 = 0;
  DAT_febe7fa8 = 0;
  return;
}

void step_qualified_route30_timeout_state_7f9f_4a64e(void)

{
  if (route30_receive_status == '\0') {
    DAT_febe7fa3 = 0;
    DAT_febe7f9e = 0;
    DAT_febe7fa8 = 0;
    DAT_febe7fa2 = 0;
    DAT_febe7f9f = '\0';
  }
  else if ((DAT_febee812 == '\x11') && (DAT_0002bb24 <= DAT_febee892)) {
    if (((DAT_febe7f9f == '\0') || (DAT_febe7f9f == '\x11')) && (DAT_febe7fa8 < DAT_0002baf2)) {
      DAT_febe7fa8 = DAT_febe7fa8 + 1;
      DAT_febe7f9f = '\x11';
    }
    else {
      DAT_febe7f9f = '\"';
      DAT_febe7fa3 = 0x5a;
    }
  }
  DAT_febe7fa0 = 0;
  DAT_febe7fa1 = 0;
  DAT_febe7fa4 = 0;
  DAT_febe7fa5 = 0;
  DAT_febe7faa = 0;
  DAT_febe7fac = 0;
  return;
}

void aggregate_four_route30_timeout_states_4a6be(void)

{
  if ((((DAT_febe7f9e == '\"') || (DAT_febe7fa0 == '\"')) || (DAT_febe7f9f == '\"')) ||
     (DAT_febe7fa1 == '\"')) {
    DAT_febe7f9c = 0x22;
  }
  else if (((DAT_febe7f9e != '\0') || (DAT_febe7fa0 != '\0')) ||
          ((DAT_febe7f9f != '\0' || (DAT_febe7f9c = 0, DAT_febe7fa1 != '\0')))) {
    DAT_febe7f9c = 0x11;
  }
  return;
}

void dispatch_route30_codeword_timeout_monitors_4a702(void)

{
  char cVar1;
  uint32_t puVar2;
  uchar uVar3;
  undefined1 uVar4;
  int iVar5;
  int iVar6;
  
  cVar1 = DAT_febe7f2c;
  puVar2 = 0xfebeb800u;
  uVar3 = get_grouped_status_byte(0xc);
  if (DAT_0002bcec == 'Z') {
    fill_constant_block_4a59e();
    goto LAB_0004a7a0;
  }
  iVar6 = (*((int *)camry_host_ptr((uint32_t)(puVar2 + 0x311c))));
  if (((cVar1 != '\x01' && cVar1 != '\x02') || (uVar3 != '\0')) || ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(0x302a))))) != '\0')) {
    if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x38d2))))) != 'Z') {
      clear_unqualified_route30_timeout_progress_4a5bc();
      clear_qualified_route30_timeout_progress_4a4d4();
    }
    goto LAB_0004a7a0;
  }
  iVar5 = test_nonzero_communication_state_without_two_inhibits_4a4b2();
  if (iVar5 == 0) {
    clear_qualified_route30_timeout_progress_4a4d4();
    if (iVar6 == -0x55aaaa56) {
      step_route30_timeout_state_7fa0_4a4f6();
    }
    else if (iVar6 == 0x55aaaa55) {
      step_route30_timeout_state_7f9e_4a54a();
    }
    else {
LAB_0004a782:
      fill_constant_block_4a59e();
    }
  }
  else {
    clear_unqualified_route30_timeout_progress_4a5bc();
    if (iVar6 == -0x55aaaa56) {
      step_qualified_route30_timeout_state_7fa1_4a5de();
    }
    else {
      if (iVar6 != 0x55aaaa55) goto LAB_0004a782;
      step_qualified_route30_timeout_state_7f9f_4a64e();
    }
  }
  uVar4 = (undefined1)iVar5;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x3863))))) = uVar4;
LAB_0004a7a0:
  aggregate_four_route30_timeout_states_4a6be();
  return;
}

void return_only_stub_4a7a8(void)

{
  return;
}

void return_only_stub_4a7aa(void)

{
  return;
}

undefined4 get_communication_state_gate_as_5a_4a7ac(void)

{
  if (((DAT_febee81f != '\0') && (DAT_febee828 != 'Z')) && (DAT_febee825 != 'Z')) {
    return 0x5a;
  }
  return 0;
}

void step_even_codeword_timeout_entries_4a7d0(void)

{
  uint8_t stack_record_10[16];
  int iVar1;
  int iVar2;
  int iVar3;
  
  iVar3 = 0;
  do {
    ((int8_t *)((stack_record_10 + 8)))[iVar3] = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe7fb8u + (uint32_t)(iVar3) * 1u))));
    iVar2 = iVar3 + 1;
    iVar1 = iVar3 + -7;
    ((uint8_t *)(stack_record_10))[iVar3] = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe7fb0u + (uint32_t)(iVar3) * 1u))));
    iVar3 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  iVar3 = 0;
  if (DAT_febe802d == '\0') {
    do {
      ((int8_t *)((stack_record_10 + 8)))[iVar3] = '\0';
      iVar2 = iVar3 + 1;
      iVar1 = iVar3 + -7;
      iVar3 = iVar2;
    } while (((iVar1 < 0) || (iVar2 < 0)));
    ((uint8_t *)(stack_record_10))[0] = 0;
    ((uint8_t *)(stack_record_10))[2] = 0;
    DAT_febe7fc2 = 0;
    ((uint8_t *)(stack_record_10))[4] = 0;
    ((uint8_t *)(stack_record_10))[6] = 0;
  }
  else {
    do {
      if (((int8_t *)((stack_record_10 + 8)))[iVar3] == '\x11') {
        ((int8_t *)((stack_record_10 + 8)))[iVar3] = '\0';
      }
      iVar2 = iVar3 + 1;
      iVar1 = iVar3 + -7;
      iVar3 = iVar2;
    } while (((iVar1 < 0) || (iVar2 < 0)));
    if (DAT_febee91c == 0x55aaaa55) {
      iVar3 = 0;
    }
    else if (DAT_febee91c == -0x55aaaa56) {
      iVar3 = 2;
    }
    else if (DAT_febee91c == 0x33333333) {
      iVar3 = 4;
    }
    else {
      iVar3 = 6;
    }
    if ((((((int8_t *)((stack_record_10 + 8)))[0] == '\"') || (((int8_t *)((stack_record_10 + 8)))[2] == '\"')) || (((int8_t *)((stack_record_10 + 8)))[4] == '\"')) ||
       ((((int8_t *)((stack_record_10 + 8)))[6] == '\"' || (DAT_0002baf4 <= DAT_febe7fc2)))) {
      ((int8_t *)((stack_record_10 + 8)))[iVar3] = '\"';
      ((uint8_t *)(stack_record_10))[iVar3] = 0x5a;
    }
    else {
      DAT_febe7fc2 = DAT_febe7fc2 + 1;
      ((int8_t *)((stack_record_10 + 8)))[iVar3] = '\x11';
    }
  }
  iVar3 = 0;
  do {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe7fb8u + (uint32_t)(iVar3) * 1u)))) = ((int8_t *)((stack_record_10 + 8)))[iVar3];
    iVar2 = iVar3 + 1;
    iVar1 = iVar3 + -7;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe7fb0u + (uint32_t)(iVar3) * 1u)))) = ((uint8_t *)(stack_record_10))[iVar3];
    iVar3 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  DAT_febe7fc4 = 0;
  return;
}

void step_qualified_odd_codeword_timeout_entries_4a8e6(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  char local_10 [16];
  
  iVar3 = 0;
  do {
    local_10[iVar3 + 8] = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe7fb8u + (uint32_t)(iVar3) * 1u))));
    iVar2 = iVar3 + 1;
    iVar1 = iVar3 + -7;
    local_10[iVar3] = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe7fb0u + (uint32_t)(iVar3) * 1u))));
    iVar3 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  if (DAT_febe802d == '\0') {
    DAT_febe7fc4 = 0;
    iVar3 = 0;
    do {
      local_10[iVar3 + 8] = '\0';
      iVar2 = iVar3 + 1;
      iVar1 = iVar3 + -7;
      iVar3 = iVar2;
    } while (((iVar1 < 0) || (iVar2 < 0)));
    local_10[1] = 0;
    local_10[3] = 0;
    local_10[5] = 0;
    local_10[7] = 0;
    local_10[0] = '\0';
    local_10[2] = 0;
    local_10[4] = 0;
    local_10[6] = 0;
  }
  else if ((DAT_febee812 == '\x11') && (DAT_0002bb28 <= DAT_febee892)) {
    iVar3 = 0;
    do {
      if (local_10[iVar3 + 8] == '\x11') {
        local_10[iVar3 + 8] = '\0';
      }
      iVar2 = iVar3 + 1;
      iVar1 = iVar3 + -7;
      iVar3 = iVar2;
    } while (((iVar1 < 0) || (iVar2 < 0)));
    if (DAT_febee91c == 0x55aaaa55) {
      iVar3 = 1;
    }
    else if (DAT_febee91c == -0x55aaaa56) {
      iVar3 = 3;
    }
    else if (DAT_febee91c == 0x33333333) {
      iVar3 = 5;
    }
    else {
      iVar3 = 7;
    }
    if ((((local_10[9] == '\"') || (local_10[0xb] == '\"')) || (local_10[0xd] == '\"')) ||
       ((local_10[0xf] == '\"' || (DAT_0002baf6 <= DAT_febe7fc4)))) {
      local_10[iVar3 + 8] = '\"';
      local_10[iVar3] = 'Z';
    }
    else {
      DAT_febe7fc4 = DAT_febe7fc4 + 1;
      local_10[iVar3 + 8] = '\x11';
    }
  }
  iVar3 = 0;
  do {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe7fb8u + (uint32_t)(iVar3) * 1u)))) = local_10[iVar3 + 8];
    iVar2 = iVar3 + 1;
    iVar1 = iVar3 + -7;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe7fb0u + (uint32_t)(iVar3) * 1u)))) = local_10[iVar3];
    iVar3 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  DAT_febe7fc2 = 0;
  return;
}

void clear_eight_codeword_pending_states_and_timers_4aa1c(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  
  iVar3 = 0;
  do {
    if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe7fb8u + (uint32_t)(iVar3) * 1u)))) == '\x11') {
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe7fb8u + (uint32_t)(iVar3) * 1u)))) = 0;
    }
    iVar2 = iVar3 + 1;
    iVar1 = iVar3 + -7;
    iVar3 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  DAT_febe7fc2 = 0;
  DAT_febe7fc4 = 0;
  return;
}

void clear_eight_codeword_states_flags_and_timers_4aa40(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  
  iVar3 = 0;
  do {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe7fb8u + (uint32_t)(iVar3) * 1u)))) = 0;
    iVar2 = iVar3 + 1;
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe7fb0u + (uint32_t)(iVar3) * 1u)))) = 0;
    iVar1 = iVar3 + -7;
    iVar3 = iVar2;
  } while (((iVar1 < 0) || (iVar2 < 0)));
  DAT_febe7fc2 = 0;
  DAT_febe7fc4 = 0;
  return;
}

void dispatch_eight_codeword_timeout_monitors_4aa5c(void)

{
  char cVar1;
  uint32_t puVar2;
  uchar uVar3;
  int iVar4;
  undefined1 uVar5;
  
  cVar1 = DAT_febe7f2c;
  puVar2 = 0xfebeb800u;
  uVar3 = get_grouped_status_byte(0xb);
  uVar5 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x3840)))));
  if (DAT_0002bcf0 == 'Z') {
    clear_eight_codeword_states_flags_and_timers_4aa40();
  }
  else if (((cVar1 == '\x01' || cVar1 == '\x02') && (uVar3 == '\0')) && ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(0x302a))))) == '\0')) {
    iVar4 = get_communication_state_gate_as_5a_4a7ac();
    uVar5 = (undefined1)iVar4;
    if (iVar4 == 0) {
      step_even_codeword_timeout_entries_4a7d0();
    }
    else {
      step_qualified_odd_codeword_timeout_entries_4a8e6();
    }
  }
  else if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x38d2))))) != 'Z') {
    clear_eight_codeword_pending_states_and_timers_4aa1c();
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x3840))))) = uVar5;
  return;
}

void reset_change_triggered_monitor_7fc8_4aac0(void)

{
  DAT_febe687d = 0;
  clear_byte_state_and_three_halfword_counters_6b7d2(((undefined *)camry_host_ptr(0xfebe7fc8u)));
  return;
}

void reset_change_triggered_monitor_7fc8_4aad4(void)

{
  DAT_febe687d = 0;
  clear_byte_state_and_three_halfword_counters_6b7d2(((undefined *)camry_host_ptr(0xfebe7fc8u)));
  return;
}

void step_change_triggered_monitor_and_encode_status_4aae8(void)

{
  char cVar1;
  char cVar2;
  undefined1 uVar3;
  undefined *puVar4;
  int iVar5;
  char cVar6;
  
  cVar2 = DAT_febe80a4;
  puVar4 = ((undefined *)camry_host_ptr(0xfebeb800u));
  cVar6 = DAT_febe687d;
  if (DAT_febe687c != DAT_febe80a4) {
    cVar6 = 'Z';
  }
  if (DAT_0002bcf4 == 'Z') {
    puVar4 = ((undefined *)camry_host_ptr(0xfebeb800u));
    clear_byte_state_and_three_halfword_counters_6b7d2(((undefined *)camry_host_ptr(0xfebe7fc8u)));
  }
  else if ((cVar6 != '\0') &&
          (puVar4 = ((undefined *)camry_host_ptr(0xfebeb800u)),
          iVar5 = advance_four_phase_threshold_callback_state_6b7f0(((undefined *)camry_host_ptr(0xfebe7fc8u)),((undefined *)camry_host_ptr(0x2baf8u)),&PTR_LAB_000212d0), iVar5 == 0x33)) {
    (*((volatile undefined *)camry_host_ptr((uint32_t)(0xfebeb800u + (uint32_t)(-0x3838) * 1u)))) = 0xff;
  }
  cVar1 = (*((volatile undefined *)camry_host_ptr((uint32_t)(0xfebeb800u + (uint32_t)(-0x3838) * 1u))));
  if (cVar1 == '\0') {
    uVar3 = 0;
  }
  else if (cVar1 == '\x11') {
    uVar3 = 1;
  }
  else if (cVar1 == '\"') {
    uVar3 = 2;
  }
  else {
    uVar3 = 3;
  }
  (*((undefined1 *)camry_host_ptr((uint32_t)((int)0xffffb078u + (int)camry_host_addr(puVar4))))) = uVar3;
  (*((char *)camry_host_ptr((uint32_t)((int)0xffffb07cu + (int)camry_host_addr(puVar4))))) = cVar2;
  (*((char *)camry_host_ptr((uint32_t)((int)0xffffb07cu + (int)((uint32_t)((uint32_t)(0xfebeb800u + (uint32_t)(1) * 1u))))))) = cVar6;
  (*((char *)camry_host_ptr((uint32_t)((int)0xffffb07au + (int)((uint32_t)((uint32_t)(0xfebeb800u + (uint32_t)(1) * 1u))))))) = cVar1;
  return;
}

void return_only_stub_4abba(void)

{
  return;
}

void return_only_stub_4abbc(void)

{
  return;
}

void scale_word_80b0_with_sentinel_to_signed_halfword_4abbe(void)

{
  int iVar1;
  
  if ((DAT_febe80b0 & 0x3ffff) == 0x20000) {
    DAT_febe7fd0 = 0;
  }
  else {
    iVar1 = (int)(DAT_febe80b0 * 0x271d) / 0x100000;
    if (iVar1 + -0x7fff < 0 == (iVar1 < 0 && -1 < iVar1 + -0x7fff)) {
      iVar1 = 0x7fff;
    }
    if (iVar1 + 0x7fff < 0 != (-1 < iVar1 && iVar1 + 0x7fff < 0)) {
      iVar1 = -0x7fff;
    }
    DAT_febe7fd0 = (undefined2)iVar1;
  }
  return;
}

void reset_latched_monitor_7fd4_and_side_flag_4ac00(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  reset_latched_monitor((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe7fd4u)));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x3820))))) = 0;
  return;
}

void reset_latched_monitor_7fd4_and_side_flag_4ac14(void)

{
  uint32_t puVar1;
  puVar1 = 0xfebeb800u;
  reset_latched_monitor((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe7fd4u)));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x3820))))) = 0;
  return;
}

void step_latched_monitor_and_record_failing_side_4ac28(void)

{
  uint32_t puVar1;
  undefined1 uVar2;
  
  puVar1 = 0xfebeb800u;
  if (DAT_0002bcf8 == 'Z') {
    reset_latched_monitor((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe7fd4u)));
  }
  else {
    step_latched_monitor
              ((F33LatchedMonitorState *)((undefined *)camry_host_ptr(0xfebe7fd4u)),(F33MonitorLimits *)((undefined *)camry_host_ptr(0x2bb00u)),
               (F33TwoSidedMonitorCallbacks *)&PTR_FUN_00029210);
  }
  uVar2 = 1;
  if ((((*((uint *)camry_host_ptr((uint32_t)(puVar1 + -0x382c)))) & 0xff) == 0x22) ||
     (uVar2 = 2, ((*((uint *)camry_host_ptr((uint32_t)(puVar1 + -0x382c)))) & 0xff00) == 0x2200)) {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x3820))))) = uVar2;
  }
  return;
}

undefined4 classify_two_magnitudes_with_source_gates_4ac7a(void)

{
  uint8_t stack_record_24[36];
  int iVar1;
  short sVar2;
  char cVar3;
  char cVar4;
  char cVar5;
  char cVar6;
  int iVar7;
  uint32_t puVar8;
  uchar uVar9;
  undefined4 uVar10;
  uint uVar11;
  
  puVar8 = 0xfebeb800u;
  uVar9 = get_grouped_status_byte(0x19);
  cVar3 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar8 + (uint32_t)(0x302a)))));
  cVar4 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar8 + (uint32_t)(-0x3898)))));
  cVar5 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar8 + (uint32_t)(-0x374a)))));
  cVar6 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar8 + (uint32_t)(-0x37ae)))));
  uVar11 = (*((uint *)camry_host_ptr((uint32_t)(puVar8 + -0x3750))));
  sVar2 = (*((short *)camry_host_ptr((uint32_t)(puVar8 + -0x37b8))));
  store_saturating_absolute_s16_6a522((int)(*((short *)camry_host_ptr((uint32_t)(puVar8 + -0x3830)))),((int16_t *)(stack_record_24)));
  store_saturating_absolute_s16_6a522((int)sVar2,((int16_t *)((stack_record_24 + 2))));
  if ((((uVar9 == '\0') && (cVar3 == '\0')) && (cVar4 == '\0')) &&
     ((cVar5 == '\0' && (cVar6 == '\0')))) {
    iVar7 = (int)DAT_0002bb2c;
    iVar1 = (*((int16_t *)(stack_record_24 + 0))) - iVar7;
    if (((iVar1 < 0 == ((*((int16_t *)(stack_record_24 + 0))) < 0 != iVar7 < 0 && iVar7 < 0 == iVar1 < 0)) &&
        ((uVar11 & 0x3ffff) != 0x20000)) ||
       (iVar7 = (int)DAT_0002bb2e, iVar1 = (*((int16_t *)(stack_record_24 + 2))) - iVar7,
       iVar1 < 0 == ((*((int16_t *)(stack_record_24 + 2))) < 0 != iVar7 < 0 && iVar7 < 0 == iVar1 < 0))) {
      uVar10 = 0x22;
    }
    else {
      uVar10 = 0x11;
    }
  }
  else {
    uVar10 = 0x44;
  }
  return uVar10;
}

void submit_gated_event_23_value_32_4ad04(void)

{
  gate_indexed_event_payload_during_diagnostic_clears_51cf6(0x23,0x32);
  return;
}

void return_only_stub_4ad18(void)

{
  return;
}

void fill_constant_block_4ad1a(void)

{
  DAT_febe7fe4 = 0;
  DAT_febe7fe5 = 0;
  DAT_febe7fe6 = 0;
  DAT_febe7fe8 = 0;
  DAT_febe7fe7 = 0;
  DAT_febe7fe9 = 0;
  DAT_febe7fea = 0;
  return;
}

void expire_latch_7fea_after_slot10_clear_delay_4ad2e(void)

{
  if ((internal_source_admission_state < 2) && (DAT_febe8021 == '\0')) {
    if ((DAT_00030e3d <= DAT_febe7fe7) ||
       (DAT_febe7fe7 = DAT_febe7fe7 + 1, DAT_00030e3d <= DAT_febe7fe7)) {
      DAT_febe7fea = 0;
    }
  }
  else {
    DAT_febe7fe7 = 0;
  }
  DAT_febe7fe8 = 0;
  return;
}

void expire_latch_7fe9_after_slot19_clear_delay_4ad68(void)

{
  if ((internal_source_admission_state < 2) && (DAT_febe806f == '\0')) {
    if ((DAT_00030e3d <= DAT_febe7fe6) ||
       (DAT_febe7fe6 = DAT_febe7fe6 + 1, DAT_00030e3d <= DAT_febe7fe6)) {
      DAT_febe7fe9 = 0;
    }
  }
  else {
    DAT_febe7fe6 = 0;
  }
  DAT_febe7fe5 = 0;
  return;
}

void delay_then_update_two_expiring_latches_4ada2(void)

{
  uint32_t puVar1;
  byte bVar2;
  
  bVar2 = DAT_febe7fe4;
  puVar1 = 0xfebeb800u;
  if (DAT_febe7fe4 < DAT_00030e3c) {
    bVar2 = DAT_febe7fe4 + 1;
  }
  else {
    puVar1 = 0xfebeb800u;
    expire_latch_7fea_after_slot10_clear_delay_4ad2e();
    expire_latch_7fe9_after_slot19_clear_delay_4ad68();
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x381c))))) = bVar2;
  return;
}

void return_only_stub_4adca(void)

{
  return;
}

void return_only_stub_4adcc(void)

{
  return;
}

void pack_four_source_bytes_equal_to_one_4adce(void)

{
  DAT_febe7fec = (DAT_febe800c == '\x01') * '\b' +
                 (DAT_febe8016 == '\x01') * '\x04' +
                 (DAT_febe803b == '\x01') * '\x02' + (DAT_febe803c == '\x01');
  return;
}

void return_only_stub_4ae08(void)

{
  return;
}

void return_only_stub_4ae26(void)

{
  return;
}

void return_only_stub_4ae28(void)

{
  return;
}

void decode_receive_slot_0_byte_field_4ae2a(void)

{
  char cVar1;
  uint32_t puVar2;
  uchar uVar3;
  
  cVar1 = DAT_febe533d;
  puVar2 = 0xfebeb800u;
  if ((internal_source_admission_state < 2) && (DAT_febe7ff1 != DAT_febe533d)) {
    puVar2 = 0xfebeb800u;
    extract_com_big_endian_bitfield_with_optional_sign_extension_7d12a(0x3c,0x3a,8,0,0,((undefined *)camry_host_ptr(0xfebe7ff0u)));
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x380f))))) = cVar1;
  uVar3 = get_application_receive_status(0);
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x380e))))) = uVar3;
  return;
}

void return_only_stub_4ae6e(void)

{
  return;
}

void return_only_stub_4ae70(void)

{
  return;
}

void decode_receive_slot_1_u16_and_u32_fields_4ae72(void)

{
  char cVar1;
  uint32_t puVar2;
  uchar uVar3;
  
  cVar1 = DAT_febe533e;
  puVar2 = 0xfebeb800u;
  if ((internal_source_admission_state < 2) && (DAT_febe7ffa != DAT_febe533e)) {
    puVar2 = 0xfebeb800u;
    extract_com_big_endian_bitfield_with_optional_sign_extension_7d12a(0x42,0x41,0x10,0,0,((undefined *)camry_host_ptr(0xfebe7ff8u)));
    extract_com_big_endian_bitfield_with_optional_sign_extension_7d12a(0x43, 0x43, 0x20, 0, 0, ((undefined *)camry_host_ptr((uint32_t)(puVar2 + -0x380c))));
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x3806))))) = cVar1;
  uVar3 = get_application_receive_status(1);
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x3805))))) = uVar3;
  return;
}

void return_only_stub_4aed2(void)

{
  return;
}

void return_only_stub_4aed4(void)

{
  return;
}

void decode_receive_slot_2_byte_and_three_nibbles_4aed6(void)

{
  char cVar1;
  uint32_t puVar2;
  uchar uVar3;
  
  cVar1 = DAT_febe533f;
  puVar2 = 0xfebeb800u;
  if ((internal_source_admission_state < 2) && (DAT_febe8000 != DAT_febe533f)) {
    puVar2 = 0xfebeb800u;
    extract_com_big_endian_bitfield_with_optional_sign_extension_7d12a(0x46,0x49,8,0,0,((undefined *)camry_host_ptr(0xfebe7ffcu)));
    extract_com_big_endian_bitfield_with_optional_sign_extension_7d12a(0x47, 0x4a, 4, 4, 0, ((undefined *)camry_host_ptr((uint32_t)(puVar2 + -0x3803))));
    extract_com_big_endian_bitfield_with_optional_sign_extension_7d12a(0x48, 0x4a, 4, 0, 0, ((undefined *)camry_host_ptr((uint32_t)(puVar2 + -0x3802))));
    extract_com_big_endian_bitfield_with_optional_sign_extension_7d12a(0x49, 0x4b, 4, 4, 0, ((undefined *)camry_host_ptr((uint32_t)(puVar2 + -0x3801))));
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x3800))))) = cVar1;
  uVar3 = get_application_receive_status(2);
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x37ff))))) = uVar3;
  return;
}

void return_only_stub_4af68(void)

{
  return;
}

void return_only_stub_4af6a(void)

{
  return;
}

void decode_receive_slot_3_two_byte_fields_4af6c(void)

{
  char cVar1;
  uint32_t puVar2;
  uchar uVar3;
  
  cVar1 = DAT_febe5340;
  puVar2 = 0xfebeb800u;
  if ((internal_source_admission_state < 2) && (DAT_febe8004 != DAT_febe5340)) {
    puVar2 = 0xfebeb800u;
    extract_com_big_endian_bitfield_with_optional_sign_extension_7d12a(0x53,0x52,8,0,0,((undefined *)camry_host_ptr(0xfebe8002u)));
    extract_com_big_endian_bitfield_with_optional_sign_extension_7d12a(0x55, 0x54, 8, 0, 0, ((undefined *)camry_host_ptr((uint32_t)(puVar2 + -0x37fb))));
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x37fc))))) = cVar1;
  uVar3 = get_application_receive_status(3);
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x37fd))))) = uVar3;
  return;
}

void return_only_stub_4afca(void)

{
  return;
}

void subtract_signed_bias_from_u16_with_upper_clamp_if_zero_4afcc(char param_1,short param_2,uint param_3,undefined2 *param_4)

{
  int iVar1;
  
  if (param_1 == '\0') {
    iVar1 = (param_3 & 0xffff) - (int)param_2;
    if (iVar1 + -0x7fff < 0 == (iVar1 < 0 && -1 < iVar1 + -0x7fff) && iVar1 != 0x7fff) {
      iVar1 = 0x7fff;
    }
    *param_4 = (short)iVar1;
  }
  return;
}

void return_only_stub_4afe8(void)

{
  return;
}

void return_only_stub_4afea(void)

{
  return;
}

void decode_receive_slot_5_three_bit_and_single_bit_fields_4afec(void)

{
  char cVar1;
  uint32_t puVar2;
  uchar uVar3;
  
  cVar1 = DAT_febe534f;
  puVar2 = 0xfebeb800u;
  if ((internal_source_admission_state < 2) && (DAT_febe8008 != DAT_febe534f)) {
    puVar2 = 0xfebeb800u;
    extract_com_big_endian_bitfield_with_optional_sign_extension_7d12a(0x6e,0xc9,3,0,0,((undefined *)camry_host_ptr(0xfebe8006u)));
    extract_com_big_endian_bitfield_with_optional_sign_extension_7d12a(0x6a, 0xc9, 1, 6, 0, ((undefined *)camry_host_ptr((uint32_t)(puVar2 + -0x37f9))));
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x37f8))))) = cVar1;
  uVar3 = get_application_receive_status(5);
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x37f7))))) = uVar3;
  return;
}
