#include "common.h"

int thunk_clear_redundant_flag_febf0671_66f84(void)

{
  return clear_redundant_flag_febf0671_66f84();
}

int thunk_clear_redundant_flag_febf0672_66fba(void)

{
  return clear_redundant_flag_febf0672_66fba();
}

uint get_mode_restart_hardware_selector(void)

{
  uint uVar1;
  
  uVar1 = platform_restart_selector_constant_zero();
  return uVar1;
}

int thunk_clear_nvm_work_hold_66fd4(void)

{
  return clear_nvm_work_hold_66fd4();
}

void thunk_restart_nvm_acquisition_with_reset_scan_cursors_66ef4(void)

{
  restart_nvm_acquisition_with_reset_scan_cursors_66ef4();
  return;
}

uint call_nvm_set_record_with_u16_selector_ff09c(uint param_1,uint *param_2)

{
  return nvm_set_record(param_1 & 0xffff,param_2);
}

uint32_t call_nvm_get_record_with_u16_selector_ff0b0(uint param_1,uint *param_2)

{
  return nvm_get_record(param_1 & 0xffff, camry_host_addr(param_2));
}

uint call_nvm_record_status_with_u16_selector_ff0c4(uint param_1)

{
  return nvm_get_record_status(param_1 & 0xffff);
}

void call_terminal_masked_hardware_sequence_ff0d8(void)

{
                    /* WARNING: Subroutine does not return */
  enter_terminal_hardware_sequence();
}

int thunk_set_redundant_terminal_sequence_request_6163e(void)

{
  return set_redundant_terminal_sequence_request_6163e();
}

void thunk_gate_indexed_event_payload_during_diagnostic_clears_51cf6(undefined4 param_1, undefined4 param_2)

{
  gate_indexed_event_payload_during_diagnostic_clears_51cf6(param_1, param_2);
  return;
}

void thunk_set_event_state_dirty_bit1_under_priority_mask_52a10(void)

{
  set_event_state_dirty_bit1_under_priority_mask_52a10();
  return;
}

void thunk_route_event_failure_by_e85a_mode_51d38(undefined4 param_1, undefined4 param_2, undefined4 param_3)

{
  route_event_failure_by_e85a_mode_51d38(param_1, param_2, param_3);
  return;
}

void thunk_promote_capture_bank_dirty_bit3_to_bit1_562fa(void)

{
  promote_capture_bank_dirty_bit3_to_bit1_562fa();
  return;
}

void thunk_clear_quad_status_if_88_35ad6(void)

{
  clear_quad_status_if_88_35ad6();
  return;
}

void consume_ba_retained_admission_count(void)

{
  uint8_t stack_record_1c[28];
  uint32_t puVar1;
  uchar uVar2;
  uchar uVar3;
  
  puVar1 = 0xfebeb800u;
  uVar2 = ba_application_work.admission;
  uVar3 = ba_application_work.remaining_mode700_entries;
  if ((ba_application_work.admission != '\0') &&
     (ba_application_work.remaining_mode700_entries != '\0')) {
    ((int8_t *)(stack_record_1c))[0] = ba_application_work.remaining_mode700_entries + 0xff;
    ((int8_t *)(stack_record_1c))[1] = 0;
    uVar3 = ba_application_work.remaining_mode700_entries + 0xff;
    if (uVar3 == '\0') {
      uVar2 = '\0';
    }
    ((int8_t *)(stack_record_1c))[2] = '\0';
    ((int8_t *)(stack_record_1c))[3] = '\0';
    ((int8_t *)(stack_record_1c))[4] = '\0';
    ((int8_t *)(stack_record_1c))[5] = '\0';
    ((int8_t *)(stack_record_1c))[6] = '\0';
    ((int8_t *)(stack_record_1c))[7] = '\0';
    puVar1 = 0xfebeb800u;
    nvm_set_record(0x18,(uint *)((int8_t *)(stack_record_1c)));
    if (uVar2 == '\0') {
      ((uint32_t *)((stack_record_1c + 8)))[0] = 0;
      ((uint32_t *)((stack_record_1c + 8)))[1] = 0;
      nvm_set_record(0x105,((uint32_t *)((stack_record_1c + 8))));
    }
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x58b0))))) = uVar3;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x58b1))))) = uVar2;
  return;
}

void thunk_set_request_word_8a88_bounded4_56b78(undefined4 param_1, undefined4 param_2)

{
  set_request_word_8a88_bounded4_56b78(param_1, param_2);
  return;
}

undefined4 thunk_get_identity_word_febf0668_62e12(void)

{
  return get_identity_word_febf0668_62e12();
}
