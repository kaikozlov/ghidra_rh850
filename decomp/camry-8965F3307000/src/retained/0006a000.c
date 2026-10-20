#include "common.h"

void crypto_bank_activate_collected_update(void)

{
  if (crypto_collected_activation == '\0') {
    crypto_collected_activation = '\x01';
    crypto_collected_elapsed_calls = 0;
    crypto_collected_phase = '\x11';
    crypto_bank_clear_fragment_history();
    crypto_bank_clear_key_material('\x01');
    crypto_bank_snapshot_key_generations();
  }
  return;
}

void crypto_bank_snapshot_test_generations(void)

{
  ((volatile uint8_t *)camry_host_ptr(0xfebe50abu))[0] = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe5338u + (uint32_t)(DAT_000257d0) * 1u))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe50abu + (uint32_t)(1) * 1u)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe5338u + (uint32_t)(DAT_000257d2) * 1u))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe50abu + (uint32_t)(2) * 1u)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe5338u + (uint32_t)(DAT_000257d4) * 1u))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe50abu + (uint32_t)(3) * 1u)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe5338u + (uint32_t)(DAT_000257d6) * 1u))));
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe50abu + (uint32_t)(4) * 1u)))) = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe5338u + (uint32_t)(DAT_000257d8) * 1u))));
  return;
}

void crypto_bank_activate_test_operation(void)

{
  if (crypto_test_activation == '\0') {
    crypto_test_activation = '\x01';
    crypto_test_elapsed_calls = 0;
    crypto_test_phase = '\x11';
    crypto_bank_clear_test_material();
    crypto_bank_snapshot_test_generations();
  }
  return;
}

uint crypto_bank_compare_aes_result(void)

{
  uint uVar1;
  
  uVar1 = 0;
  do {
    if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe5196u + (uint32_t)(uVar1) * 1u)))) != (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe51a6u + (uint32_t)(uVar1) * 1u))))) {
      return 0x44;
    }
    uVar1 = uVar1 + 1;
  } while (uVar1 < 0x10);
  return 0x33;
}

uint crypto_bank_compare_mac_result(void)

{
  uint uVar1;
  
  uVar1 = 0;
  do {
    if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe5196u + (uint32_t)(uVar1) * 1u)))) != (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe51b6u + (uint32_t)(uVar1) * 1u))))) {
      return 0x44;
    }
    uVar1 = uVar1 + 1;
  } while (uVar1 < 0x10);
  return 0x33;
}

undefined1 get_febe508f_byte_6a12a(void)

{
  return DAT_febe508f;
}

undefined4 get_febe505c_word_6a130(void)

{
  return DAT_febe505c;
}

undefined2 get_eight_slot_febe50b6_halfword_6a136(uint param_1)

{
  return *(undefined2 *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe50b6u + (uint32_t)((param_1 & 7) * 2) * 1u))));
}

undefined1 get_febe508b_byte_6a144(void)

{
  return DAT_febe508b;
}

undefined1 get_febe508c_byte_6a14a(void)

{
  return DAT_febe508c;
}

uchar get_crypto_test_failed_byte_6a150(void)

{
  return crypto_test_failed;
}

void request_crypto_direct_abort_for_mode1_or40_6a156(undefined4 param_1,char param_2)

{
  if (((param_2 == '\x01') || (param_2 == '@')) && (crypto_direct_activation != '\0')) {
    crypto_direct_abort_request = 'Z';
  }
  return;
}

void set_crypto_mode_byte_6a174(uchar param_1)

{
  crypto_mode = param_1;
  return;
}

void clear_febe505c_word_6a17a(void)

{
  DAT_febe505c = 0;
  return;
}

uchar get_crypto_profile_failure_for_index_below_two_6a180(uint param_1)

{
  if ((param_1 & 0xff) < 2) {
    return (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe507au + (uint32_t)(param_1 & 0xff) * 1u))));
  }
  return '\0';
}

undefined4 get_crypto_activation_is_one_5a_6a192(void)

{
  if ((crypto_direct_activation != '\x01') && (crypto_collected_activation != '\x01')) {
    return 0;
  }
  return 0x5a;
}

void set_febe5070_halfword_6a1ac(undefined2 param_1)

{
  DAT_febe5070 = param_1;
  return;
}

void crypto_bank_record_profile_status(uint packed_status)

{
  uint uVar1;
  uint uVar2;
  uint uVar3;
  uchar uVar4;
  uint uVar5;
  uchar *puVar6;
  
  uVar5 = packed_status & 0xffff;
  uVar2 = packed_status >> 0x10;
  uVar3 = (uint)crypto_config_profile_count;
  if (2 < uVar3) {
    uVar3 = 2;
  }
  uVar1 = 0;
  while( true ) {
    DAT_febe5056 = (undefined2)(packed_status >> 0x10);
    DAT_febe5054 = (undefined2)packed_status;
    if (uVar3 <= uVar1) break;
    if (((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe507cu + (uint32_t)(uVar1) * 1u)))) == '\x11') && (uVar5 == DAT_00025840)) {
      if (uVar2 == 0) {
        puVar6 = ((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe507eu + (uint32_t)(uVar1) * 1u)));
        uVar4 = *puVar6;
        if (uVar4 != 0xff) {
          uVar4 = uVar4 + '\x01';
        }
      }
      else {
        puVar6 = ((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe5080u + (uint32_t)(uVar1) * 1u)));
        uVar4 = *puVar6;
        if (uVar4 != 0xff) {
          uVar4 = uVar4 + '\x01';
        }
      }
      *puVar6 = uVar4;
      packed_status = CONCAT22(DAT_febe5056,DAT_febe5054);
    }
    uVar1 = uVar1 + 1 & 0xff;
  }
  return;
}

void append_halfword_to_eight_slot_ring_if_enabled_6a280(undefined2 param_1)

{
  uint uVar1;
  
  if (DAT_febe5090 == '\0') {
    uVar1 = (uint)DAT_febe508a;
    DAT_febe508a = DAT_febe508a + 1;
    *(undefined2 *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe50b6u + (uint32_t)((uVar1 & 7) * 2) * 1u)))) = param_1;
  }
  return;
}

uint crypto_bank_key_update_completed(uchar result)

{
  uchar uVar1;
  
  uVar1 = 'f';
  if (result == '\0') {
    uVar1 = 'D';
  }
  if (crypto_direct_activation == '\x01') {
    crypto_direct_phase = uVar1;
    uVar1 = crypto_collected_phase;
  }
  crypto_collected_phase = uVar1;
  return 0;
}

uint crypto_bank_aes_completed(uchar result)

{
  uint32_t puVar1;
  undefined1 uVar2;
  uint uVar3;
  
  puVar1 = 0xfebeb800u;
  uVar2 = 0x44;
  if (result == '\0') {
    puVar1 = 0xfebeb800u;
    uVar3 = crypto_bank_compare_aes_result();
    uVar2 = (undefined1)uVar3;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6764))))) = uVar2;
  return 0;
}

uint crypto_bank_verification_completed(uchar result)

{
  uchar *puVar1;
  
  if (result != '\0') {
    crypto_verification_result = '\x01';
  }
  puVar1 = ((void *)camry_host_ptr((uint32_t)((0xfebe5097u))));
  if (crypto_direct_activation == '\x01') {
    puVar1 = ((void *)camry_host_ptr((uint32_t)((0xfebe5092u))));
  }
  *puVar1 = 'F';
  return 0;
}

uint crypto_bank_mac_completed(uchar result)

{
  uint32_t puVar1;
  undefined1 uVar2;
  uint uVar3;
  
  puVar1 = 0xfebeb800u;
  uVar2 = 0x44;
  if (result == '\0') {
    puVar1 = 0xfebeb800u;
    uVar3 = crypto_bank_compare_mac_result();
    uVar2 = (undefined1)uVar3;
  }
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar1 + (uint32_t)(-0x6764))))) = uVar2;
  return 0;
}

undefined4 set_febe5088_halfword_return_zero_6a31a(undefined2 param_1)

{
  DAT_febe5088 = param_1;
  return 0;
}

void return_only_stub_6a322(void)

{
  return;
}

undefined4 return_const_0_6a328(void)

{
  return 0;
}

undefined4 validate_enabled_eight_byte_additive_checksum_6a32c(ushort param_1,uint *param_2)

{
  byte *pbVar1;
  int iVar2;
  undefined8 uVar3;
  undefined4 uVar4;
  uint uVar5;
  uint uVar6;
  uint uVar7;
  uint uVar8;
  
  uVar3 = 0x23dfc00000000;
  uVar6 = (uint)DAT_00028fd4;
  uVar4 = 0;
  iVar2 = 0;
  uVar7 = 0;
  while ((uVar7 < uVar6 && (iVar2 == 0))) {
    pbVar1 = ((byte *)camry_host_ptr((uint32_t)(uVar7 * 8 + (int)((ulonglong)uVar3 >> 0x20) + 0x51e8)));
    if ((ushort)*pbVar1 == (param_1 & 0xff)) {
      if ((((pbVar1[7] == 0x5a) && (camry_host_addr((param_2))!= 0)) && (uVar8 = param_2[2], uVar8 != 0)) &&
         (7 < (*((byte *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_2) + 7)))))) {
        iVar2 = 0;
        uVar5 = 0;
        do {
          pbVar1 = ((byte *)camry_host_ptr((uint32_t)(uVar5 + uVar8)));
          uVar5 = uVar5 + 1;
          iVar2 = iVar2 + (uint)*pbVar1;
        } while (uVar5 < 7);
        if ((iVar2 + *param_2 + ((*param_2 & 0x700) >> 8) + 8 & 0xff) == (uint)(*((byte *)camry_host_ptr((uint32_t)(uVar8 + 7)))))
        {
          uVar4 = 0;
        }
        else {
          increment_tracking_counter5398_8e7ba(param_1);
          uVar4 = 1;
        }
      }
      iVar2 = 0x5a;
    }
    uVar7 = uVar7 + 1 & 0xff;
  }
  return uVar4;
}

int conditionally_run_descriptor_checksum_check_6a3be(undefined2 param_1, undefined4 param_2)

{
  uint32_t puVar1;
  int iVar2;
  
  puVar1 = 0x23dfcu;
  iVar2 = 0;
  if (DAT_00028fd6 != 'Z') {
    iVar2 = ((void)(param_1), return_const_0_6a328());
  }
  if (((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x51d8u + (uint32_t)((int)(puVar1 + 3)))))) == (code)0x5a) && (iVar2 == 0)) {
    iVar2 = validate_enabled_eight_byte_additive_checksum_6a32c(param_1, ((uint *)camry_host_ptr((uint32_t)(param_2))));
  }
  return iVar2;
}

undefined4 return_const_0_6a3f0(void)

{
  return 0;
}

undefined4 return_zero_or_invoke_zero_hook_6a3f4(undefined2 param_1)

{
  undefined4 uVar1;
  
  if (DAT_00028fd6 == 'Z') {
    uVar1 = 0;
  }
  else {
    uVar1 = ((void)(param_1), return_const_0_6a3f0());
  }
  return uVar1;
}

void run_guarded_halfword_sequence_then_callback_table_6a410(void)

{
  run_secoc_integrity_and_bounded_work_cycle_8eff8();
  run_round_robin_and_postcycle_callbacks_89dec();
  return;
}

void return_only_stub_6a420(void)

{
  return;
}

void return_only_stub_6a434(void)

{
  return;
}

void initialize_priority_mask_stack_256_entries_6a440(void)

{
  uint uVar1;
  
  DAT_febe39dc = 0;
  uVar1 = 0;
  do {
    *(undefined4 *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe39e0u + (uint32_t)(uVar1 * 4) * 1u)))) = 0xffff;
    uVar1 = uVar1 + 1;
  } while (uVar1 < 0x100);
  return;
}

void store_saturating_absolute_s16_6a522(short param_1,short *param_2)

{
  int iVar1;
  
  iVar1 = (int)param_1;
  if (iVar1 + 0x7fff < 0 == (-1 < iVar1 && iVar1 + 0x7fff < 0) && iVar1 != -0x7fff) {
    if (iVar1 < 0) {
      param_1 = -param_1;
    }
  }
  else {
    param_1 = 0x7fff;
  }
  *param_2 = param_1;
  return;
}

void store_saturating_absolute_s32_6a53e(int param_1,int *param_2)

{
  if (param_1 + 0x7fffffff < 0 == (-1 < param_1 && param_1 + 0x7fffffff < 0) &&
      param_1 != -0x7fffffff) {
    if (param_1 < 0) {
      param_1 = -param_1;
    }
  }
  else {
    param_1 = 0x7fffffff;
  }
  *param_2 = param_1;
  return;
}

void store_u32_big_endian_bytes_6a55c(undefined4 param_1,undefined1 *param_2)

{
  *param_2 = (char)((uint)param_1 >> 0x18);
  param_2[1] = (char)((uint)param_1 >> 0x10);
  param_2[2] = (char)((uint)param_1 >> 8);
  param_2[3] = (char)param_1;
  return;
}

void store_low_u16_big_endian_bytes_6a574(undefined4 param_1,undefined1 *param_2)

{
  *param_2 = (char)((uint)param_1 >> 8);
  param_2[1] = (char)param_1;
  return;
}

void store_u32_big_endian_bytes_6a594(undefined4 param_1,undefined1 *param_2)

{
  *param_2 = (char)((uint)param_1 >> 0x18);
  param_2[1] = (char)((uint)param_1 >> 0x10);
  param_2[2] = (char)((uint)param_1 >> 8);
  param_2[3] = (char)param_1;
  return;
}

void store_low_u16_big_endian_bytes_6a5ac(undefined4 param_1,undefined1 *param_2)

{
  *param_2 = (char)((uint)param_1 >> 8);
  param_2[1] = (char)param_1;
  return;
}

void store_s16_saturated_to_symmetric_s8_6a5cc(short param_1,undefined1 *param_2)

{
  undefined1 uVar1;
  int iVar2;
  
  iVar2 = (int)param_1;
  if (iVar2 + 0x7f < 0 == (-1 < iVar2 && iVar2 + 0x7f < 0)) {
    if (iVar2 + -0x7f < 0 == (iVar2 < 0 && -1 < iVar2 + -0x7f) && iVar2 != 0x7f) {
      uVar1 = 0x7f;
    }
    else {
      if (iVar2 + 0x80 < 0 != (-1 < iVar2 && iVar2 + 0x80 < 0) || iVar2 == -0x80) {
        iVar2 = -0x80;
      }
      uVar1 = (undefined1)iVar2;
    }
  }
  else {
    uVar1 = 0x81;
  }
  *param_2 = uVar1;
  return;
}

void store_s32_saturated_to_symmetric_s16_6a5fa(int param_1,undefined2 *param_2)

{
  undefined2 uVar1;
  
  if (param_1 + 0x7fff < 0 == (-1 < param_1 && param_1 + 0x7fff < 0)) {
    if (param_1 + -0x7fff < 0 == (param_1 < 0 && -1 < param_1 + -0x7fff) && param_1 != 0x7fff) {
      uVar1 = 0x7fff;
    }
    else {
      if (param_1 + 0x8000 < 0 != (-1 < param_1 && param_1 + 0x8000 < 0) || param_1 == -0x8000) {
        param_1 = -0x8000;
      }
      uVar1 = (undefined2)param_1;
    }
  }
  else {
    uVar1 = 0x8001;
  }
  *param_2 = uVar1;
  return;
}

void store_s32_saturated_to_u8_6a624(uint param_1,undefined1 *param_2)

{
  undefined1 uVar1;
  
  uVar1 = 0;
  if (-1 < (int)param_1) {
    if (param_1 < 0xff) {
      uVar1 = (undefined1)param_1;
    }
    else {
      uVar1 = 0xff;
    }
  }
  *param_2 = uVar1;
  return;
}

void follow_s16_fractional
               (F33FractionalFollowing16 *state,uint coefficient,short *output,int *new_accumulator)

{
  int iVar1;
  
  if (0xfffe < coefficient - 1) {
    coefficient = 0x10000;
  }
  iVar1 = (int)state->target * coefficient +
          (state->accumulator - (int)state->previous * coefficient);
  *new_accumulator = iVar1;
  *output = (short)(iVar1 / 0x10000);
  return;
}

void update_u16_q16_delta_accumulator_6a678(ushort *param_1,int param_2,undefined2 *param_3,int *param_4)

{
  int iVar1;
  
  if (0xfffe < param_2 - 1U) {
    param_2 = 0x10000;
  }
  iVar1 = (uint)param_1[1] * param_2 + (*(int *)(param_1 + 2) - (uint)*param_1 * param_2);
  *param_3 = (short)((uint)iVar1 >> 0x10);
  *param_4 = iVar1;
  return;
}

void reset_terminal_monitor(F33TerminalMonitorState *state)

{
  state->status = 0xff;
  state->passing_count = 0;
  state->failing_count = 0;
  state->failing_high_water = 0;
  return;
}

uint step_terminal_monitor
               (F33TerminalMonitorState *state,F33MonitorLimits *thresholds,
               F33TerminalMonitorCallbacks *callbacks)

{
  uint uVar1;
  uint uVar2;
  uint uVar3;
  uint32_t pFVar4;
  ushort uVar5;
  uchar uVar6;
  uchar uVar7;
  uint uVar8;
  uint uVar9;
  
  uVar9 = (uint)state->failing_count;
  uVar2 = (uint)thresholds->failing_limit;
  uVar8 = (uint)state->passing_count;
  uVar5 = state->failing_high_water;
  if ((int)(uVar9 - uVar2) < 0 || uVar9 == uVar2) {
    uVar3 = (uint)thresholds->passing_limit;
    if ((int)(uVar8 - uVar3) < 0 || uVar8 == uVar3) {
      uVar6 = 0xff;
      uVar1 = (*(int (*)())camry_indirect((uint32_t)(callbacks->classify)))(camry_host_addr(state), camry_host_addr(thresholds), camry_host_addr(callbacks));
      if (uVar1 == 0x11) {
        uVar9 = 0;
        if (((int)(uVar8 - uVar3) < 0 || uVar8 == uVar3) &&
           (uVar8 = uVar8 + 1, (int)(uVar8 - uVar3) < 0 || uVar8 == uVar3)) goto LAB_0006a732;
        pFVar4 = (uint32_t)((uint32_t)(callbacks->healthy_observed));
        uVar7 = '\0';
        uVar6 = '\0';
      }
      else {
        if (uVar1 != 0x22) goto LAB_0006a732;
        uVar8 = 0;
        if ((int)(uVar9 - uVar2) < 0 || uVar9 == uVar2) {
          uVar9 = uVar9 + 1;
        }
        uVar3 = uVar9;
        if (-1 < (int)(uVar5 - uVar9)) {
          uVar3 = (uint)uVar5;
        }
        uVar5 = (ushort)uVar3;
        if ((int)(uVar9 - uVar2) < 0 || uVar9 == uVar2) goto LAB_0006a732;
        pFVar4 = (uint32_t)((uint32_t)(callbacks->failed));
        uVar7 = '\"';
        uVar6 = '\"';
      }
      if ((uint32_t)(pFVar4) != 0u) {
        (*(int (*)())camry_indirect((uint32_t)(pFVar4)))();
        uVar6 = uVar7;
      }
    }
    else {
      uVar6 = '\0';
    }
  }
  else {
    uVar6 = '\"';
  }
LAB_0006a732:
  state->status = uVar6;
  state->passing_count = (ushort)uVar8;
  state->failing_count = (ushort)uVar9;
  state->failing_high_water = uVar5;
  return 0x11;
}

undefined4 force_counter_state22_above_failure_threshold_6a780(undefined1 *param_1,ushort *param_2,int param_3)

{
  ushort uVar1;
  undefined4 uVar2;
  uint32_t pcVar3;
  
  uVar2 = 0x11;
  if (((camry_host_addr(param_1)==camry_host_addr((undefined1 *)0x0)) || (camry_host_addr(param_2)==camry_host_addr((ushort *)0x0))) || (param_3 == 0)) {
    uVar2 = 0x22;
  }
  else {
    uVar1 = param_2[1];
    if (((int)((uint)*(ushort *)(param_1 + 4) - (uint)uVar1) < 0 ||
         (uint)*(ushort *)(param_1 + 4) == (uint)uVar1) &&
       ((int)((uint)*(ushort *)(param_1 + 2) - (uint)*param_2) < 0 ||
        (uint)*(ushort *)(param_1 + 2) == (uint)*param_2)) {
      pcVar3 = (uint32_t)(camry_host_addr(*((code * *)camry_host_ptr((uint32_t)(param_3 + 8)))));
      *param_1 = 0x22;
      if ((uint32_t)(pcVar3) != 0u) {
        (*(int (*)())camry_indirect((uint32_t)(pcVar3)))(camry_host_addr(param_1), camry_host_addr(param_2), param_3);
      }
      *(undefined2 *)(param_1 + 2) = 0;
      *(ushort *)(param_1 + 4) = uVar1 + 1;
      *(ushort *)(param_1 + 6) = uVar1 + 1;
    }
  }
  return uVar2;
}

undefined4 advance_two_threshold_counters_and_dispatch_6a7d8(undefined1 *param_1,ushort *param_2,undefined4 *param_3)

{
  int iVar1;
  uint uVar2;
  uint uVar3;
  ushort uVar4;
  uint32_t pcVar5;
  undefined1 uVar6;
  undefined1 uVar7;
  uint uVar8;
  uint uVar9;
  
  if ((((camry_host_addr(param_1)==camry_host_addr((undefined1 *)0x0)) || (camry_host_addr(param_2)==camry_host_addr((ushort *)0x0))) ||
      (camry_host_addr(param_3)==camry_host_addr((undefined4 *)0x0))) || ((uint32_t)(*param_3 )==0x0u)) {
    return 0x22;
  }
  uVar9 = (uint)*(ushort *)(param_1 + 4);
  uVar3 = (uint)param_2[1];
  uVar8 = (uint)*(ushort *)(param_1 + 2);
  uVar4 = *(ushort *)(param_1 + 6);
  if ((int)(uVar9 - uVar3) < 0 || uVar9 == uVar3) {
    uVar2 = (uint)*param_2;
    if ((int)(uVar8 - uVar2) < 0 || uVar8 == uVar2) {
      uVar6 = 0xff;
      iVar1 = (*(int (*)())camry_indirect((uint32_t)(*param_3)))(camry_host_addr(param_1), camry_host_addr(param_2), camry_host_addr(param_3));
      if (iVar1 == 0x11) {
        uVar8 = uVar8 + 1;
        if ((int)(uVar8 - uVar2) < 0 || uVar8 == uVar2) goto LAB_0006a864;
        pcVar5 = (uint32_t)((uint32_t)(param_3[1]));
        uVar7 = 0;
        uVar6 = 0;
      }
      else {
        if (iVar1 != 0x22) goto LAB_0006a864;
        uVar8 = 0;
        if ((int)(uVar9 - uVar3) < 0 || uVar9 == uVar3) {
          uVar9 = uVar9 + 1;
        }
        uVar2 = uVar9;
        if (-1 < (int)(uVar4 - uVar9)) {
          uVar2 = (uint)uVar4;
        }
        uVar4 = (ushort)uVar2;
        if ((int)(uVar9 - uVar3) < 0 || uVar9 == uVar3) goto LAB_0006a864;
        pcVar5 = (uint32_t)((uint32_t)(param_3[2]));
        uVar7 = 0x22;
        uVar6 = 0x22;
      }
      if ((uint32_t)(pcVar5) != 0u) {
        (*(int (*)())camry_indirect((uint32_t)(pcVar5)))();
        uVar6 = uVar7;
      }
    }
    else {
      uVar6 = 0;
    }
  }
  else {
    uVar6 = 0x22;
  }
LAB_0006a864:
  *param_1 = uVar6;
  *(short *)(param_1 + 2) = (short)uVar8;
  *(short *)(param_1 + 4) = (short)uVar9;
  *(ushort *)(param_1 + 6) = uVar4;
  return 0x11;
}

void reset_recoverable_monitor(F33RecoverableMonitorState *state)

{
  state->packed_status = 0;
  state->passing_count = 0;
  state->failing_count = 0;
  state->failing_high_water = 0;
  state->recovery_count = 0;
  return;
}

void retain_disabled_recoverable_monitor
               (F33RecoverableMonitorState *state,F33RecoverableMonitorLimits *limits)

{
  uint uVar1;
  
  if ((uintptr_t)(((limits->failing_limit)))<(uintptr_t)(((state->failing_count)))) {
    uVar1 = 0x22;
  }
  else {
    if ((state->failing_count == 0) && ((uintptr_t)(((limits->passing_limit)))<(uintptr_t)(((state->passing_count))))) {
      uVar1 = 0x2200;
    }
    else {
      state->passing_count = 0;
      uVar1 = 0;
    }
    state->failing_count = 0;
    state->recovery_count = 0;
  }
  state->packed_status = uVar1;
  return;
}

uint step_recoverable_monitor
               (F33RecoverableMonitorState *state,F33RecoverableMonitorLimits *limits,
               F33RecoverableMonitorCallbacks *callbacks)

{
  ushort uVar1;
  ushort uVar2;
  uint uVar3;
  uint uVar4;
  short sVar5;
  ushort uVar6;
  uint32_t pFVar7;
  ushort local_2c;
  F33MonitorRecoveryScratch FStack_2a;
  
  FStack_2a.failing_high_water = state->failing_high_water;
  FStack_2a.passing_count = state->passing_count;
  FStack_2a.failing_count = state->failing_count;
  FStack_2a.recovery_count = state->recovery_count;
  uVar1 = limits->passing_limit;
  local_2c = limits->recovery_limit;
  uVar2 = limits->failing_limit;
  if (FStack_2a.failing_count == 0) {
    if (uVar1 < FStack_2a.passing_count) {
      sVar5 = 0x2200;
    }
    else {
      sVar5 = 0;
      if (FStack_2a.passing_count != 0) {
        sVar5 = 0x1100;
      }
    }
  }
  else {
    sVar5 = 0x22;
    if (FStack_2a.failing_count <= uVar2) {
      sVar5 = 0x11;
    }
  }
  if (sVar5 == 0) {
    uVar4 = (*(int (*)())camry_indirect((uint32_t)(callbacks->classify_normal)))(camry_host_addr(state), camry_host_addr(limits), camry_host_addr(callbacks));
    if (uVar4 == 0x11) {
      if ((uVar1 < FStack_2a.passing_count) ||
         (uVar2 = FStack_2a.passing_count + 1, uVar6 = FStack_2a.passing_count + 1,
         FStack_2a.passing_count = uVar2, uVar1 < uVar6)) {
        uVar4 = 0x2200;
      }
      else {
        uVar4 = 0x11001100;
      }
      FStack_2a.failing_count = 0;
    }
    else if (uVar4 == 0x22) {
      FStack_2a.passing_count = 0;
      if (FStack_2a.failing_count <= uVar2) {
        FStack_2a.failing_count = FStack_2a.failing_count + 1;
      }
      if (FStack_2a.failing_high_water < FStack_2a.failing_count) {
        FStack_2a.failing_high_water = FStack_2a.failing_count;
      }
      uVar4 = 0x22;
      if (FStack_2a.failing_count <= uVar2) {
        uVar4 = 0x110011;
      }
    }
    else if ((uVar4 == 0x33) || (uVar4 == 0x44)) {
      FStack_2a.failing_count = 0;
      FStack_2a.passing_count = 0;
      uVar4 = 0;
    }
    else {
      uVar4 = 0xffff;
    }
    uVar3 = uVar4 & 0xffff;
    if (uVar3 == 0) goto LAB_0006add8;
    if (uVar3 == 0x11) {
      if (callbacks->enter_failing !=0x0u) {
        (*(int (*)())camry_indirect((uint32_t)(callbacks->enter_failing)))();
      }
      pFVar7 = (uint32_t)((uint32_t)(callbacks->repeat_pending_failing));
    }
    else if (uVar3 == 0x22) {
      if (callbacks->enter_failing !=0x0u) {
        (*(int (*)())camry_indirect((uint32_t)(callbacks->enter_failing)))();
      }
      if (callbacks->confirm_failing !=0x0u) {
        (*(int (*)())camry_indirect((uint32_t)(callbacks->confirm_failing)))();
      }
      pFVar7 = (uint32_t)((uint32_t)(callbacks->repeat_confirmed_failing));
    }
    else if (uVar3 == 0x1100) {
      if (callbacks->enter_passing !=0x0u) {
        (*(int (*)())camry_indirect((uint32_t)(callbacks->enter_passing)))();
      }
      pFVar7 = (uint32_t)((uint32_t)(callbacks->repeat_pending_passing));
    }
    else {
      if (uVar3 != 0x2200) {
        uVar4 = 0;
        goto LAB_0006add8;
      }
      if (callbacks->enter_passing !=0x0u) {
        (*(int (*)())camry_indirect((uint32_t)(callbacks->enter_passing)))();
      }
      if (callbacks->confirm_passing !=0x0u) {
        (*(int (*)())camry_indirect((uint32_t)(callbacks->confirm_passing)))();
      }
      pFVar7 = (uint32_t)((uint32_t)(callbacks->repeat_confirmed_passing));
    }
    goto joined_r0x0006abfe;
  }
  if (sVar5 == 0x11) {
    uVar4 = (*(int (*)())camry_indirect((uint32_t)(callbacks->classify_failing)))(camry_host_addr(state), camry_host_addr(limits), camry_host_addr(callbacks));
    if (uVar4 == 0x11) {
      if ((uVar1 < FStack_2a.passing_count) ||
         (uVar2 = FStack_2a.passing_count + 1, uVar6 = FStack_2a.passing_count + 1,
         FStack_2a.passing_count = uVar2, uVar1 < uVar6)) {
        uVar4 = 0x2200;
      }
      else {
        uVar4 = 0x11001100;
      }
      FStack_2a.failing_count = 0;
    }
    else if (uVar4 == 0x22) {
      FStack_2a.passing_count = 0;
      if (FStack_2a.failing_count <= uVar2) {
        FStack_2a.failing_count = FStack_2a.failing_count + 1;
      }
      if (FStack_2a.failing_high_water < FStack_2a.failing_count) {
        FStack_2a.failing_high_water = FStack_2a.failing_count;
      }
      uVar4 = 0x22;
      if (FStack_2a.failing_count <= uVar2) {
        uVar4 = 0x110011;
      }
    }
    else if ((uVar4 == 0x33) || (uVar4 == 0x44)) {
      FStack_2a.failing_count = 0;
      FStack_2a.passing_count = 0;
      uVar4 = 0;
    }
    else {
      uVar4 = 0xffff;
    }
    uVar3 = uVar4 & 0xffff;
    if (uVar3 != 0) {
      if (uVar3 == 0x11) {
        pFVar7 = (uint32_t)((uint32_t)(callbacks->repeat_pending_failing));
      }
      else if (uVar3 == 0x22) {
        if (callbacks->confirm_failing !=0x0u) {
          (*(int (*)())camry_indirect((uint32_t)(callbacks->confirm_failing)))();
        }
        pFVar7 = (uint32_t)((uint32_t)(callbacks->repeat_confirmed_failing));
      }
      else if (uVar3 == 0x1100) {
        if (callbacks->leave_pending_failing !=0x0u) {
          (*(int (*)())camry_indirect((uint32_t)(callbacks->leave_pending_failing)))();
        }
        if (callbacks->enter_passing !=0x0u) {
          (*(int (*)())camry_indirect((uint32_t)(callbacks->enter_passing)))();
        }
        pFVar7 = (uint32_t)((uint32_t)(callbacks->repeat_pending_passing));
      }
      else {
        if (uVar3 != 0x2200) {
          if (callbacks->repeat_pending_failing !=0x0u) {
            (*(int (*)())camry_indirect((uint32_t)(callbacks->repeat_pending_failing)))();
          }
          uVar4 = 0x11;
          goto LAB_0006add8;
        }
        if (callbacks->leave_pending_failing !=0x0u) {
          (*(int (*)())camry_indirect((uint32_t)(callbacks->leave_pending_failing)))();
        }
        if (callbacks->enter_passing !=0x0u) {
          (*(int (*)())camry_indirect((uint32_t)(callbacks->enter_passing)))();
        }
        if (callbacks->confirm_passing !=0x0u) {
          (*(int (*)())camry_indirect((uint32_t)(callbacks->confirm_passing)))();
        }
        pFVar7 = (uint32_t)((uint32_t)(callbacks->repeat_confirmed_passing));
      }
      goto joined_r0x0006abfe;
    }
    pFVar7 = (uint32_t)((uint32_t)(callbacks->leave_pending_failing));
joined_r0x0006ad1a:
    if ((uint32_t)(pFVar7) != 0u) {
      (*(int (*)())camry_indirect((uint32_t)(pFVar7)))(camry_host_addr(state), camry_host_addr(limits), camry_host_addr(callbacks));
    }
  }
  else {
    if (sVar5 == 0x1100) {
      uVar4 = (*(int (*)())camry_indirect((uint32_t)(callbacks->classify_normal)))();
      if (uVar4 == 0x11) {
        if ((uVar1 < FStack_2a.passing_count) ||
           (uVar2 = FStack_2a.passing_count + 1, uVar6 = FStack_2a.passing_count + 1,
           FStack_2a.passing_count = uVar2, uVar1 < uVar6)) {
          uVar4 = 0x2200;
        }
        else {
          uVar4 = 0x11001100;
        }
        FStack_2a.failing_count = 0;
      }
      else if (uVar4 == 0x22) {
        FStack_2a.passing_count = 0;
        if (FStack_2a.failing_count <= uVar2) {
          FStack_2a.failing_count = FStack_2a.failing_count + 1;
        }
        if (FStack_2a.failing_high_water < FStack_2a.failing_count) {
          FStack_2a.failing_high_water = FStack_2a.failing_count;
        }
        uVar4 = 0x22;
        if (FStack_2a.failing_count <= uVar2) {
          uVar4 = 0x110011;
        }
      }
      else if ((uVar4 == 0x33) || (uVar4 == 0x44)) {
        FStack_2a.failing_count = 0;
        FStack_2a.passing_count = 0;
        uVar4 = 0;
      }
      else {
        uVar4 = 0xffff;
      }
      uVar3 = uVar4 & 0xffff;
      if (uVar3 == 0) {
        pFVar7 = (uint32_t)((uint32_t)(callbacks->leave_pending_passing));
        goto joined_r0x0006ad1a;
      }
      if (uVar3 == 0x11) {
        if (callbacks->leave_pending_passing !=0x0u) {
          (*(int (*)())camry_indirect((uint32_t)(callbacks->leave_pending_passing)))();
        }
        if (callbacks->enter_failing !=0x0u) {
          (*(int (*)())camry_indirect((uint32_t)(callbacks->enter_failing)))();
        }
        pFVar7 = (uint32_t)((uint32_t)(callbacks->repeat_pending_failing));
      }
      else if (uVar3 == 0x22) {
        if (callbacks->leave_pending_passing !=0x0u) {
          (*(int (*)())camry_indirect((uint32_t)(callbacks->leave_pending_passing)))();
        }
        if (callbacks->enter_failing !=0x0u) {
          (*(int (*)())camry_indirect((uint32_t)(callbacks->enter_failing)))();
        }
        if (callbacks->confirm_failing !=0x0u) {
          (*(int (*)())camry_indirect((uint32_t)(callbacks->confirm_failing)))();
        }
        pFVar7 = (uint32_t)((uint32_t)(callbacks->repeat_confirmed_failing));
      }
      else if (uVar3 == 0x1100) {
        pFVar7 = (uint32_t)((uint32_t)(callbacks->repeat_pending_passing));
      }
      else {
        if (uVar3 != 0x2200) {
          if (callbacks->repeat_pending_passing !=0x0u) {
            (*(int (*)())camry_indirect((uint32_t)(callbacks->repeat_pending_passing)))(camry_host_addr(state), camry_host_addr(limits), camry_host_addr(callbacks));
          }
          uVar4 = 0x1100;
          goto LAB_0006add8;
        }
        if (callbacks->confirm_passing !=0x0u) {
          (*(int (*)())camry_indirect((uint32_t)(callbacks->confirm_passing)))();
        }
        pFVar7 = (uint32_t)((uint32_t)(callbacks->repeat_confirmed_passing));
      }
    }
    else if (sVar5 == 0x2200) {
      uVar4 = (*(int (*)())camry_indirect((uint32_t)(callbacks->classify_normal)))();
      if (uVar4 == 0x11) {
LAB_0006a970:
        FStack_2a.failing_count = 0;
LAB_0006a974:
        uVar4 = 0x2200;
      }
      else {
        if (uVar4 != 0x22) {
          if ((uVar4 == 0x33) || (uVar4 == 0x44)) goto LAB_0006a970;
          goto LAB_0006a974;
        }
        FStack_2a.passing_count = 0;
        if (FStack_2a.failing_count <= uVar2) {
          FStack_2a.failing_count = FStack_2a.failing_count + 1;
        }
        if (FStack_2a.failing_high_water < FStack_2a.failing_count) {
          FStack_2a.failing_high_water = FStack_2a.failing_count;
        }
        uVar4 = 0x22;
        if (FStack_2a.failing_count <= uVar2) {
          uVar4 = 0x110011;
        }
      }
      uVar3 = uVar4 & 0xffff;
      if (uVar3 == 0) {
        pFVar7 = (uint32_t)((uint32_t)(callbacks->leave_confirmed_passing));
        goto joined_r0x0006ad1a;
      }
      if (uVar3 == 0x11) {
        if (callbacks->leave_confirmed_passing !=0x0u) {
          (*(int (*)())camry_indirect((uint32_t)(callbacks->leave_confirmed_passing)))();
        }
        if (callbacks->enter_failing !=0x0u) {
          (*(int (*)())camry_indirect((uint32_t)(callbacks->enter_failing)))();
        }
        pFVar7 = (uint32_t)((uint32_t)(callbacks->repeat_pending_failing));
      }
      else if (uVar3 == 0x22) {
        if (callbacks->leave_confirmed_passing !=0x0u) {
          (*(int (*)())camry_indirect((uint32_t)(callbacks->leave_confirmed_passing)))();
        }
        if (callbacks->enter_failing !=0x0u) {
          (*(int (*)())camry_indirect((uint32_t)(callbacks->enter_failing)))();
        }
        if (callbacks->confirm_failing !=0x0u) {
          (*(int (*)())camry_indirect((uint32_t)(callbacks->confirm_failing)))();
        }
        pFVar7 = (uint32_t)((uint32_t)(callbacks->repeat_confirmed_failing));
      }
      else {
        pFVar7 = (uint32_t)((uint32_t)(callbacks->repeat_confirmed_passing));
        if (uVar3 != 0x2200) {
          if ((uint32_t)(pFVar7) != 0u) {
            (*(int (*)())camry_indirect((uint32_t)(pFVar7)))();
          }
          uVar4 = 0x2200;
          goto LAB_0006add8;
        }
      }
    }
    else {
      uVar4 = (*(int (*)())camry_indirect((uint32_t)(callbacks->classify_recovery)))(camry_host_addr(state), camry_host_addr(limits), camry_host_addr(callbacks));
      uVar4 = step_monitor_recovery_scratch((uchar)uVar4,&FStack_2a,&local_2c);
      if ((uVar4 & 0xffff) == 0) {
        pFVar7 = (uint32_t)((uint32_t)(callbacks->recover_confirmed_failing));
      }
      else {
        pFVar7 = (uint32_t)((uint32_t)(callbacks->repeat_confirmed_failing));
        if ((uVar4 & 0xffff) != 0x22) {
          if ((uint32_t)(pFVar7) != 0u) {
            (*(int (*)())camry_indirect((uint32_t)(pFVar7)))();
          }
          uVar4 = 0x22;
          goto LAB_0006add8;
        }
      }
    }
joined_r0x0006abfe:
    if ((uint32_t)(pFVar7) != 0u) {
      (*(int (*)())camry_indirect((uint32_t)(pFVar7)))();
    }
  }
LAB_0006add8:
  state->packed_status = uVar4;
  state->passing_count = FStack_2a.passing_count;
  state->failing_count = FStack_2a.failing_count;
  state->failing_high_water = FStack_2a.failing_high_water;
  state->recovery_count = FStack_2a.recovery_count;
  return 0x11;
}

void reset_latched_monitor(F33LatchedMonitorState *state)

{
  state->packed_status = 0;
  state->passing_count = 0;
  state->failing_count = 0;
  state->failing_high_water = 0;
  return;
}

void reset_windowed_monitor(F33WindowedMonitorState *state)

{
  state->packed_status = 0;
  state->passing_count = 0;
  state->passing_window = 0;
  state->failing_count = 0;
  state->failing_window = 0;
  state->failing_high_water = 0;
  return;
}

void retain_disabled_latched_monitor(F33LatchedMonitorState *state,F33MonitorLimits *limits)

{
  uint uVar1;
  
  if ((uintptr_t)(((limits->failing_limit)))<(uintptr_t)(((state->failing_count)))) {
    uVar1 = 0x22;
  }
  else {
    if ((state->failing_count == 0) && ((uintptr_t)(((limits->passing_limit)))<(uintptr_t)(((state->passing_count))))) {
      uVar1 = 0x2200;
    }
    else {
      state->passing_count = 0;
      uVar1 = 0;
    }
    state->failing_count = 0;
  }
  state->packed_status = uVar1;
  return;
}

void classify_counter_limits_and_clear_selected_fields_6ae48(undefined4 *param_1,ushort *param_2)

{
  undefined4 uVar1;
  
  if (param_2[2] < *(ushort *)(param_1 + 2)) {
    uVar1 = 0x22;
  }
  else {
    if ((*(ushort *)(param_1 + 2) == 0) && (*param_2 < *(ushort *)(param_1 + 1))) {
      uVar1 = 0x2200;
    }
    else {
      *(undefined2 *)(param_1 + 1) = 0;
      uVar1 = 0;
      (*((undefined2 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 6)))) = 0;
    }
    *(undefined2 *)(param_1 + 2) = 0;
    (*((undefined2 *)camry_host_ptr((uint32_t)((int)camry_host_addr(param_1) + 10)))) = 0;
  }
  *param_1 = uVar1;
  return;
}

uint step_latched_monitor
               (F33LatchedMonitorState *state,F33MonitorLimits *limits,
               F33TwoSidedMonitorCallbacks *callbacks)

{
  ushort uVar1;
  ushort uVar2;
  short sVar3;
  uint uVar4;
  uint uVar5;
  ushort uVar6;
  ushort uVar7;
  ushort uVar8;
  uint32_t pFVar9;
  
  uVar8 = state->failing_count;
  uVar7 = state->passing_count;
  uVar6 = state->failing_high_water;
  uVar1 = limits->passing_limit;
  uVar2 = limits->failing_limit;
  if (uVar8 == 0) {
    if (uVar1 < uVar7) {
      sVar3 = 0x2200;
    }
    else {
      sVar3 = 0;
      if (uVar7 != 0) {
        sVar3 = 0x1100;
      }
    }
  }
  else {
    sVar3 = 0x22;
    if (uVar8 <= uVar2) {
      sVar3 = 0x11;
    }
  }
  if (sVar3 == 0) {
    uVar5 = (*(int (*)())camry_indirect((uint32_t)(callbacks->classify_normal)))(camry_host_addr(state), camry_host_addr(limits), camry_host_addr(callbacks));
    if (uVar5 == 0x11) {
      if ((uVar1 < uVar7) || (uVar7 = uVar7 + 1, uVar1 < uVar7)) {
        uVar5 = 0x2200;
      }
      else {
        uVar5 = 0x11001100;
      }
      uVar8 = 0;
    }
    else if (uVar5 == 0x22) {
      uVar7 = 0;
      if (uVar8 <= uVar2) {
        uVar8 = uVar8 + 1;
      }
      uVar1 = uVar8;
      if (uVar8 <= uVar6) {
        uVar1 = uVar6;
      }
      uVar6 = uVar1;
      uVar5 = 0x22;
      if (uVar8 <= uVar2) {
        uVar5 = 0x110011;
      }
    }
    else if ((uVar5 == 0x33) || (uVar5 == 0x44)) {
      uVar7 = 0;
      uVar8 = 0;
      uVar5 = 0;
    }
    else {
      uVar5 = 0xffff;
    }
    uVar4 = uVar5 & 0xffff;
    if (uVar4 != 0) {
      if (uVar4 == 0x11) {
        if (callbacks->enter_failing !=0x0u) {
          (*(int (*)())camry_indirect((uint32_t)(callbacks->enter_failing)))();
        }
        pFVar9 = (uint32_t)((uint32_t)(callbacks->repeat_pending_failing));
      }
      else if (uVar4 == 0x22) {
        if (callbacks->enter_failing !=0x0u) {
          (*(int (*)())camry_indirect((uint32_t)(callbacks->enter_failing)))();
        }
        if (callbacks->confirm_failing !=0x0u) {
          (*(int (*)())camry_indirect((uint32_t)(callbacks->confirm_failing)))();
        }
        pFVar9 = (uint32_t)((uint32_t)(callbacks->repeat_confirmed_failing));
      }
      else if (uVar4 == 0x1100) {
        if (callbacks->enter_passing !=0x0u) {
          (*(int (*)())camry_indirect((uint32_t)(callbacks->enter_passing)))();
        }
        pFVar9 = (uint32_t)((uint32_t)(callbacks->repeat_pending_passing));
      }
      else {
        if (uVar4 != 0x2200) {
          uVar5 = 0;
          goto LAB_0006b308;
        }
        if (callbacks->enter_passing !=0x0u) {
          (*(int (*)())camry_indirect((uint32_t)(callbacks->enter_passing)))();
        }
        if (callbacks->confirm_passing !=0x0u) {
          (*(int (*)())camry_indirect((uint32_t)(callbacks->confirm_passing)))();
        }
        pFVar9 = (uint32_t)((uint32_t)(callbacks->repeat_confirmed_passing));
      }
      if ((uint32_t)(pFVar9) != 0u) {
        (*(int (*)())camry_indirect((uint32_t)(pFVar9)))();
      }
    }
    goto LAB_0006b308;
  }
  if (sVar3 == 0x11) {
    uVar5 = (*(int (*)())camry_indirect((uint32_t)(callbacks->classify_failing)))();
    if (uVar5 == 0x11) {
      if ((uVar1 < uVar7) || (uVar7 = uVar7 + 1, uVar1 < uVar7)) {
        uVar5 = 0x2200;
      }
      else {
        uVar5 = 0x11001100;
      }
      uVar8 = 0;
    }
    else if (uVar5 == 0x22) {
      uVar7 = 0;
      if (uVar8 <= uVar2) {
        uVar8 = uVar8 + 1;
      }
      uVar1 = uVar8;
      if (uVar8 <= uVar6) {
        uVar1 = uVar6;
      }
      uVar6 = uVar1;
      uVar5 = 0x22;
      if (uVar8 <= uVar2) {
        uVar5 = 0x110011;
      }
    }
    else if ((uVar5 == 0x33) || (uVar5 == 0x44)) {
      uVar7 = 0;
      uVar8 = 0;
      uVar5 = 0;
    }
    else {
      uVar5 = 0xffff;
    }
    uVar4 = uVar5 & 0xffff;
    if (uVar4 == 0) {
      if (callbacks->leave_pending_failing !=0x0u) {
        (*(int (*)())camry_indirect((uint32_t)(callbacks->leave_pending_failing)))(camry_host_addr(state), camry_host_addr(limits), camry_host_addr(callbacks));
      }
    }
    else {
      if (uVar4 == 0x11) {
        pFVar9 = (uint32_t)((uint32_t)(callbacks->repeat_pending_failing));
      }
      else if (uVar4 == 0x22) {
        if (callbacks->confirm_failing !=0x0u) {
          (*(int (*)())camry_indirect((uint32_t)(callbacks->confirm_failing)))();
        }
        pFVar9 = (uint32_t)((uint32_t)(callbacks->repeat_confirmed_failing));
      }
      else if (uVar4 == 0x1100) {
        if (callbacks->leave_pending_failing !=0x0u) {
          (*(int (*)())camry_indirect((uint32_t)(callbacks->leave_pending_failing)))();
        }
        if (callbacks->enter_passing !=0x0u) {
          (*(int (*)())camry_indirect((uint32_t)(callbacks->enter_passing)))();
        }
        pFVar9 = (uint32_t)((uint32_t)(callbacks->repeat_pending_passing));
      }
      else {
        if (uVar4 != 0x2200) {
          if (callbacks->repeat_pending_failing !=0x0u) {
            (*(int (*)())camry_indirect((uint32_t)(callbacks->repeat_pending_failing)))();
          }
          uVar5 = 0x11;
          goto LAB_0006b308;
        }
        if (callbacks->leave_pending_failing !=0x0u) {
          (*(int (*)())camry_indirect((uint32_t)(callbacks->leave_pending_failing)))();
        }
        if (callbacks->enter_passing !=0x0u) {
          (*(int (*)())camry_indirect((uint32_t)(callbacks->enter_passing)))();
        }
        if (callbacks->confirm_passing !=0x0u) {
          (*(int (*)())camry_indirect((uint32_t)(callbacks->confirm_passing)))();
        }
        pFVar9 = (uint32_t)((uint32_t)(callbacks->repeat_confirmed_passing));
      }
      if ((uint32_t)(pFVar9) != 0u) {
        (*(int (*)())camry_indirect((uint32_t)(pFVar9)))();
      }
    }
    goto LAB_0006b308;
  }
  if (sVar3 == 0x1100) {
    uVar5 = (*(int (*)())camry_indirect((uint32_t)(callbacks->classify_normal)))();
    if (uVar5 == 0x11) {
      if ((uVar1 < uVar7) || (uVar7 = uVar7 + 1, uVar1 < uVar7)) {
        uVar5 = 0x2200;
      }
      else {
        uVar5 = 0x11001100;
      }
      uVar8 = 0;
    }
    else if (uVar5 == 0x22) {
      uVar7 = 0;
      if (uVar8 <= uVar2) {
        uVar8 = uVar8 + 1;
      }
      uVar1 = uVar8;
      if (uVar8 <= uVar6) {
        uVar1 = uVar6;
      }
      uVar6 = uVar1;
      uVar5 = 0x22;
      if (uVar8 <= uVar2) {
        uVar5 = 0x110011;
      }
    }
    else if ((uVar5 == 0x33) || (uVar5 == 0x44)) {
      uVar7 = 0;
      uVar8 = 0;
      uVar5 = 0;
    }
    else {
      uVar5 = 0xffff;
    }
    uVar4 = uVar5 & 0xffff;
    if (uVar4 == 0) {
      if (callbacks->leave_pending_passing !=0x0u) {
        (*(int (*)())camry_indirect((uint32_t)(callbacks->leave_pending_passing)))(camry_host_addr(state), camry_host_addr(limits), camry_host_addr(callbacks));
      }
    }
    else {
      if (uVar4 == 0x11) {
        if (callbacks->leave_pending_passing !=0x0u) {
          (*(int (*)())camry_indirect((uint32_t)(callbacks->leave_pending_passing)))();
        }
        if (callbacks->enter_failing !=0x0u) {
          (*(int (*)())camry_indirect((uint32_t)(callbacks->enter_failing)))();
        }
        pFVar9 = (uint32_t)((uint32_t)(callbacks->repeat_pending_failing));
      }
      else if (uVar4 == 0x22) {
        if (callbacks->leave_pending_passing !=0x0u) {
          (*(int (*)())camry_indirect((uint32_t)(callbacks->leave_pending_passing)))();
        }
        if (callbacks->enter_failing !=0x0u) {
          (*(int (*)())camry_indirect((uint32_t)(callbacks->enter_failing)))();
        }
        if (callbacks->confirm_failing !=0x0u) {
          (*(int (*)())camry_indirect((uint32_t)(callbacks->confirm_failing)))();
        }
        pFVar9 = (uint32_t)((uint32_t)(callbacks->repeat_confirmed_failing));
      }
      else if (uVar4 == 0x1100) {
        pFVar9 = (uint32_t)((uint32_t)(callbacks->repeat_pending_passing));
      }
      else {
        if (uVar4 != 0x2200) {
          if (callbacks->repeat_pending_passing !=0x0u) {
            (*(int (*)())camry_indirect((uint32_t)(callbacks->repeat_pending_passing)))();
          }
          uVar5 = 0x1100;
          goto LAB_0006b308;
        }
        if (callbacks->confirm_passing !=0x0u) {
          (*(int (*)())camry_indirect((uint32_t)(callbacks->confirm_passing)))();
        }
        pFVar9 = (uint32_t)((uint32_t)(callbacks->repeat_confirmed_passing));
      }
      if ((uint32_t)(pFVar9) != 0u) {
        (*(int (*)())camry_indirect((uint32_t)(pFVar9)))(camry_host_addr(state), camry_host_addr(limits), camry_host_addr(callbacks));
      }
    }
    goto LAB_0006b308;
  }
  if (sVar3 != 0x2200) {
    if (callbacks->repeat_confirmed_failing !=0x0u) {
      (*(int (*)())camry_indirect((uint32_t)(callbacks->repeat_confirmed_failing)))();
    }
    uVar5 = 0x22;
    goto LAB_0006b308;
  }
  uVar5 = (*(int (*)())camry_indirect((uint32_t)(callbacks->classify_normal)))();
  if (uVar5 == 0x11) {
LAB_0006af18:
    uVar8 = 0;
LAB_0006af1a:
    uVar5 = 0x2200;
  }
  else {
    if (uVar5 != 0x22) {
      if ((uVar5 == 0x33) || (uVar5 == 0x44)) goto LAB_0006af18;
      goto LAB_0006af1a;
    }
    uVar7 = 0;
    if (uVar8 <= uVar2) {
      uVar8 = uVar8 + 1;
    }
    uVar1 = uVar8;
    if (uVar8 <= uVar6) {
      uVar1 = uVar6;
    }
    uVar6 = uVar1;
    uVar5 = 0x22;
    if (uVar8 <= uVar2) {
      uVar5 = 0x110011;
    }
  }
  uVar4 = uVar5 & 0xffff;
  if (uVar4 == 0) {
    if (callbacks->leave_confirmed_passing !=0x0u) {
      (*(int (*)())camry_indirect((uint32_t)(callbacks->leave_confirmed_passing)))();
    }
  }
  else {
    if (uVar4 == 0x11) {
      if (callbacks->leave_confirmed_passing !=0x0u) {
        (*(int (*)())camry_indirect((uint32_t)(callbacks->leave_confirmed_passing)))();
      }
      if (callbacks->enter_failing !=0x0u) {
        (*(int (*)())camry_indirect((uint32_t)(callbacks->enter_failing)))();
      }
      pFVar9 = (uint32_t)((uint32_t)(callbacks->repeat_pending_failing));
    }
    else if (uVar4 == 0x22) {
      if (callbacks->leave_confirmed_passing !=0x0u) {
        (*(int (*)())camry_indirect((uint32_t)(callbacks->leave_confirmed_passing)))();
      }
      if (callbacks->enter_failing !=0x0u) {
        (*(int (*)())camry_indirect((uint32_t)(callbacks->enter_failing)))();
      }
      if (callbacks->confirm_failing !=0x0u) {
        (*(int (*)())camry_indirect((uint32_t)(callbacks->confirm_failing)))();
      }
      pFVar9 = (uint32_t)((uint32_t)(callbacks->repeat_confirmed_failing));
    }
    else {
      pFVar9 = (uint32_t)((uint32_t)(callbacks->repeat_confirmed_passing));
      if (uVar4 != 0x2200) {
        if ((uint32_t)(pFVar9) != 0u) {
          (*(int (*)())camry_indirect((uint32_t)(pFVar9)))();
        }
        uVar5 = 0x2200;
        goto LAB_0006b308;
      }
    }
    if ((uint32_t)(pFVar9) != 0u) {
      (*(int (*)())camry_indirect((uint32_t)(pFVar9)))(camry_host_addr(state), camry_host_addr(limits), camry_host_addr(callbacks));
    }
  }
LAB_0006b308:
  state->packed_status = uVar5;
  state->passing_count = uVar7;
  state->failing_count = uVar8;
  state->failing_high_water = uVar6;
  return 0x11;
}
