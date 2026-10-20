#include "common.h"

undefined4 thunk_clear_indexed_request_and_set_complement_b14d2(undefined4 param_1)

{
  return clear_indexed_request_and_set_complement_b14d2(param_1);
}

int admit_internal_ba_selector(uint selector,uint authorization)

{
  uint uVar1;
  
  uVar1 = (uint)DAT_febeb11a;
  if ((selector == 3) || (selector - 5 < 3)) {
    if (((uVar1 == 0x400) || (uVar1 == 0x500)) || ((uVar1 - 0x700 < 3 || (uVar1 - 0x700 == 0x100))))
    {
      return 0;
    }
  }
  else {
    if (selector == 4) {
      DAT_febeb112 = 0;
      return 0;
    }
    if (selector == 1) {
      if (((((uVar1 == 0x400) || (uVar1 == 0x500)) || (uVar1 - 0x700 < 3)) ||
          (uVar1 - 0x700 == 0x100)) && (authorization == 0x11294c43)) {
        DAT_febeb110 = 1;
        return 0;
      }
    }
    else if ((selector == 2) && (uVar1 == 0x600)) {
      DAT_febeb111 = 1;
      return 0;
    }
  }
  return -6;
}

int thunk_queue_application_service(uchar service_id)

{
  int iVar1;
  
  iVar1 = queue_application_service(service_id);
  return iVar1;
}

undefined4 thunk_is_distinct_aeba8_index_b5a74(undefined4 param_1)

{
  return is_distinct_aeba8_index_b5a74(param_1);
}

uint request_record101_reset_write(void)

{
  DAT_febeb255 = 0x11;
  return 1;
}

undefined4 return_const_1_b5ed0(void)

{
  return 1;
}

undefined4 return_const_ff_b5ed4(void)

{
  return 0xff;
}

uint stage_encoded_mode_pair_thunk(uint first,uint second)

{
  uint uVar1;
  
  uVar1 = stage_encoded_mode_pair(first,second);
  return uVar1;
}

void thunk_prepare_record_103_invalid_write_b69c6(void)

{
  prepare_record_103_invalid_write_b69c6();
  return;
}

void record103_byte_write_thunk(uchar selector,uchar value)

{
  stage_record103_byte_write(selector,value);
  return;
}

void thunk_snapshot_three_control_input_blocks_fc3cc(void)

{
  snapshot_three_control_input_blocks_fc3cc();
  return;
}

void thunk_snapshot_service_pair_and_control_summary_fc462(void)

{
  snapshot_service_pair_and_control_summary_fc462();
  return;
}

void thunk_snapshot_retained_and_coherence_state_to_eb80_block_fd562(void)

{
  snapshot_retained_and_coherence_state_to_eb80_block_fd562();
  return;
}

int latch_internal_ba_selector(uint selector)

{
  if (selector == 5) {
    DAT_febeb113 = 0x22;
  }
  else if (selector == 6) {
    DAT_febeb113 = 0x44;
  }
  else {
    DAT_febeb113 = 0x88;
    if (selector != 7) {
      DAT_febeb113 = 0x11;
    }
  }
  DAT_febeb112 = 0x5a;
  return 0;
}

uint qualify_service_admission(uchar kind)

{
  ushort uVar1;
  char cVar2;
  ushort uVar3;
  short sVar4;
  ushort uVar5;
  char cVar6;
  uint uVar7;
  int iVar8;
  uint32_t puVar9;
  int iVar10;
  ushort uVar11;
  short sStack_26;
  
  cVar6 = DAT_febebef0;
  uVar5 = DAT_febebede;
  sVar4 = DAT_febeb38c;
  uVar3 = DAT_febeb080;
  cVar2 = DAT_febeb079;
  puVar9 = 0xfebeb800u;
  uVar11 = DAT_febeb11a & 0xff00;
  uVar1 = DAT_febeb082 & 0x81ff;
  store_saturated_signed16_absolute_d1178((int)((int)(int16_t)DAT_febeb054),&sStack_26);
  iVar10 = 0;
  uVar7 = 0;
  do {
    if (((*((ushort *)camry_host_ptr((uint32_t)(puVar9 + uVar7 * 2 + -0x7f0)))) < DAT_000af4a4) && (uVar7 != 5)) {
      iVar10 = 0x5a;
    }
    uVar7 = uVar7 + 1;
  } while (uVar7 < 10);
  if ((((((uVar3 < DAT_000af49a) || (DAT_000af49c < uVar5)) || (cVar6 != '\x11')) ||
       ((cVar2 != '\0' || (0x500 < uVar11)))) ||
      ((iVar10 == 0x5a || ((sVar4 != 0 || (uVar1 != 0)))))) ||
     (iVar8 = (int)DAT_000af49e, iVar10 = sStack_26 - iVar8,
     iVar10 < 0 == (sStack_26 < 0 != iVar8 < 0 && iVar8 < 0 == iVar10 < 0))) {
    uVar7 = 0;
  }
  else {
    uVar7 = 0x5a;
  }
  if ((kind == '\x01' || kind == '\x02') && (iVar10 = check_b054_magnitude_for_b3d2_mode_b8474(), iVar10 == 0)) {
    uVar7 = 0;
  }
  return uVar7;
}

int latch_ba_unsigned_override(uchar value)

{
  DAT_febeb116 = 0x5a;
  DAT_febeb117 = value;
  return 0;
}

void set_service_qualification_mode_thunk(uchar mode)

{
  set_service_qualification_mode(mode);
  return;
}

void set_service_numeric_target_thunk(ushort target)

{
  set_service_numeric_target(target);
  return;
}

int latch_ba_owner5_fast_release(void)

{
  DAT_febeb118 = 0x5a;
  return 0;
}

void thunk_set_b3dc_ready_and_clear_b3cb_b85ae(void)

{
  set_b3dc_ready_and_clear_b3cb_b85ae();
  return;
}

void thunk_set_b3dd_ready_and_clear_b3cb_b85bc(void)

{
  set_b3dd_ready_and_clear_b3cb_b85bc();
  return;
}

void thunk_clear_byte_febeb3dc_b85ca(void)

{
  clear_byte_febeb3dc_b85ca();
  return;
}

void thunk_clear_byte_febeb3dd_b85d0(void)

{
  clear_byte_febeb3dd_b85d0();
  return;
}

void gather_first_control_profile(F33RetainedControlProfile *output,uchar slot)

{
  output->capture_value = (*((volatile int16_t *)camry_host_ptr((uint32_t)(0xfebeb930u + (uint32_t)(slot) * 2u))));
  output->received_composite = (*((volatile int16_t *)camry_host_ptr((uint32_t)(0xfebeb94eu + (uint32_t)(slot) * 2u))));
  output->integrated_source = (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebeb98au + (uint32_t)(slot) * 2u))));
  output->elapsed_groups = (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebeb96cu + (uint32_t)(slot) * 2u))));
  output->scaled_f228 = (*((volatile int32_t *)camry_host_ptr((uint32_t)(0xfebebc2cu + (uint32_t)(slot) * 4u))));
  output->source_u16_max = (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebeb9a8u + (uint32_t)(slot) * 2u))));
  output->source_u16_mean = (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebeb9c6u + (uint32_t)(slot) * 2u))));
  output->f1c6_max = (*((volatile int16_t *)camry_host_ptr((uint32_t)(0xfebeb9e4u + (uint32_t)(slot) * 2u))));
  output->f1c6_mean = (*((volatile int16_t *)camry_host_ptr((uint32_t)(0xfebeba02u + (uint32_t)(slot) * 2u))));
  output->f1c8_max = (*((volatile int16_t *)camry_host_ptr((uint32_t)(0xfebeba20u + (uint32_t)(slot) * 2u))));
  output->f1c8_mean = (*((volatile int16_t *)camry_host_ptr((uint32_t)(0xfebeba3eu + (uint32_t)(slot) * 2u))));
  output->f1ca_max = (*((volatile int16_t *)camry_host_ptr((uint32_t)(0xfebeba5cu + (uint32_t)(slot) * 2u))));
  output->f1ca_mean = (*((volatile int16_t *)camry_host_ptr((uint32_t)(0xfebeba7au + (uint32_t)(slot) * 2u))));
  output->scaled_ae5c_max = (*((volatile int16_t *)camry_host_ptr((uint32_t)(0xfebeba98u + (uint32_t)(slot) * 2u))));
  output->scaled_ae5c_min = (*((volatile int16_t *)camry_host_ptr((uint32_t)(0xfebebab6u + (uint32_t)(slot) * 2u))));
  output->scaled_b054_max = (*((volatile int16_t *)camry_host_ptr((uint32_t)(0xfebebad4u + (uint32_t)(slot) * 2u))));
  output->scaled_b054_mean = (*((volatile int16_t *)camry_host_ptr((uint32_t)(0xfebebaf2u + (uint32_t)(slot) * 2u))));
  output->route31_scalar = (*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xfebebc68u + (uint32_t)(slot) * 4u))));
  output->scalar_kind = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb707u + (uint32_t)(slot) * 1u))));
  output->packed_metadata[0] = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb716u + (uint32_t)(slot) * 1u))));
  output->packed_metadata[1] = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb725u + (uint32_t)(slot) * 1u))));
  output->packed_metadata[2] = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb734u + (uint32_t)(slot) * 1u))));
  output->packed_metadata[3] = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb743u + (uint32_t)(slot) * 1u))));
  output->packed_metadata[4] = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb752u + (uint32_t)(slot) * 1u))));
  output->packed_metadata[5] = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb761u + (uint32_t)(slot) * 1u))));
  output->current_first_profile_validity = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb6dfu + (uint32_t)(slot) * 1u))));
  output->current_elapsed_source_validity = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb770u + (uint32_t)(slot) * 1u))));
  return;
}

void gather_first_ranked_control_profile(F33RetainedControlProfile *output,uchar slot)

{
  uint uVar1;
  
  uVar1 = (uint)slot;
  output->capture_value = (*((volatile int16_t *)camry_host_ptr((uint32_t)(0xfebeb930u + (uint32_t)(uVar1 + 5) * 2u))));
  output->received_composite = (*((volatile int16_t *)camry_host_ptr((uint32_t)(0xfebeb94eu + (uint32_t)(uVar1 + 5) * 2u))));
  output->integrated_source = (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebeb98au + (uint32_t)(uVar1 + 5) * 2u))));
  output->elapsed_groups = (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebeb96cu + (uint32_t)(uVar1 + 5) * 2u))));
  output->scaled_f228 = (*((volatile int32_t *)camry_host_ptr((uint32_t)(0xfebebc2cu + (uint32_t)(uVar1 + 5) * 4u))));
  output->source_u16_max = (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebeb9a8u + (uint32_t)(uVar1 + 5) * 2u))));
  output->source_u16_mean = (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebeb9c6u + (uint32_t)(uVar1 + 5) * 2u))));
  output->f1c6_max = (*((volatile int16_t *)camry_host_ptr((uint32_t)(0xfebeb9e4u + (uint32_t)(uVar1 + 5) * 2u))));
  output->f1c6_mean = (*((volatile int16_t *)camry_host_ptr((uint32_t)(0xfebeba02u + (uint32_t)(uVar1 + 5) * 2u))));
  output->f1c8_max = (*((volatile int16_t *)camry_host_ptr((uint32_t)(0xfebeba20u + (uint32_t)(uVar1 + 5) * 2u))));
  output->f1c8_mean = (*((volatile int16_t *)camry_host_ptr((uint32_t)(0xfebeba3eu + (uint32_t)(uVar1 + 5) * 2u))));
  output->f1ca_max = (*((volatile int16_t *)camry_host_ptr((uint32_t)(0xfebeba5cu + (uint32_t)(uVar1 + 5) * 2u))));
  output->f1ca_mean = (*((volatile int16_t *)camry_host_ptr((uint32_t)(0xfebeba7au + (uint32_t)(uVar1 + 5) * 2u))));
  output->scaled_ae5c_max = (*((volatile int16_t *)camry_host_ptr((uint32_t)(0xfebeba98u + (uint32_t)(uVar1 + 5) * 2u))));
  output->scaled_ae5c_min = (*((volatile int16_t *)camry_host_ptr((uint32_t)(0xfebebab6u + (uint32_t)(uVar1 + 5) * 2u))));
  output->scaled_b054_max = (*((volatile int16_t *)camry_host_ptr((uint32_t)(0xfebebad4u + (uint32_t)(uVar1 + 5) * 2u))));
  output->scaled_b054_mean = (*((volatile int16_t *)camry_host_ptr((uint32_t)(0xfebebaf2u + (uint32_t)(uVar1 + 5) * 2u))));
  output->route31_scalar = (*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xfebebc68u + (uint32_t)(uVar1 + 5) * 4u))));
  output->scalar_kind = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb707u + (uint32_t)(uVar1 + 5) * 1u))));
  output->packed_metadata[0] = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb716u + (uint32_t)(uVar1 + 5) * 1u))));
  output->packed_metadata[1] = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb725u + (uint32_t)(uVar1 + 5) * 1u))));
  output->packed_metadata[2] = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb734u + (uint32_t)(uVar1 + 5) * 1u))));
  output->packed_metadata[3] = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb743u + (uint32_t)(uVar1 + 5) * 1u))));
  output->packed_metadata[4] = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb752u + (uint32_t)(uVar1 + 5) * 1u))));
  output->packed_metadata[5] = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb761u + (uint32_t)(uVar1 + 5) * 1u))));
  output->current_first_profile_validity = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb6dfu + (uint32_t)(uVar1) * 1u))));
  output->current_elapsed_source_validity = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb770u + (uint32_t)(uVar1) * 1u))));
  return;
}

void gather_second_ranked_control_profile(F33RetainedControlProfile *output,uchar slot)

{
  uint uVar1;
  
  uVar1 = (uint)slot;
  output->capture_value = (*((volatile int16_t *)camry_host_ptr((uint32_t)(0xfebeb930u + (uint32_t)(uVar1 + 10) * 2u))));
  output->received_composite = (*((volatile int16_t *)camry_host_ptr((uint32_t)(0xfebeb94eu + (uint32_t)(uVar1 + 10) * 2u))));
  output->integrated_source = (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebeb98au + (uint32_t)(uVar1 + 10) * 2u))));
  output->elapsed_groups = (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebeb96cu + (uint32_t)(uVar1 + 10) * 2u))));
  output->scaled_f228 = (*((volatile int32_t *)camry_host_ptr((uint32_t)(0xfebebc2cu + (uint32_t)(uVar1 + 10) * 4u))));
  output->source_u16_max = (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebeb9a8u + (uint32_t)(uVar1 + 10) * 2u))));
  output->source_u16_mean = (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebeb9c6u + (uint32_t)(uVar1 + 10) * 2u))));
  output->f1c6_max = (*((volatile int16_t *)camry_host_ptr((uint32_t)(0xfebeb9e4u + (uint32_t)(uVar1 + 10) * 2u))));
  output->f1c6_mean = (*((volatile int16_t *)camry_host_ptr((uint32_t)(0xfebeba02u + (uint32_t)(uVar1 + 10) * 2u))));
  output->f1c8_max = (*((volatile int16_t *)camry_host_ptr((uint32_t)(0xfebeba20u + (uint32_t)(uVar1 + 10) * 2u))));
  output->f1c8_mean = (*((volatile int16_t *)camry_host_ptr((uint32_t)(0xfebeba3eu + (uint32_t)(uVar1 + 10) * 2u))));
  output->f1ca_max = (*((volatile int16_t *)camry_host_ptr((uint32_t)(0xfebeba5cu + (uint32_t)(uVar1 + 10) * 2u))));
  output->f1ca_mean = (*((volatile int16_t *)camry_host_ptr((uint32_t)(0xfebeba7au + (uint32_t)(uVar1 + 10) * 2u))));
  output->scaled_ae5c_max = (*((volatile int16_t *)camry_host_ptr((uint32_t)(0xfebeba98u + (uint32_t)(uVar1 + 10) * 2u))));
  output->scaled_ae5c_min = (*((volatile int16_t *)camry_host_ptr((uint32_t)(0xfebebab6u + (uint32_t)(uVar1 + 10) * 2u))));
  output->scaled_b054_max = (*((volatile int16_t *)camry_host_ptr((uint32_t)(0xfebebad4u + (uint32_t)(uVar1 + 10) * 2u))));
  output->scaled_b054_mean = (*((volatile int16_t *)camry_host_ptr((uint32_t)(0xfebebaf2u + (uint32_t)(uVar1 + 10) * 2u))));
  output->route31_scalar = (*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xfebebc68u + (uint32_t)(uVar1 + 10) * 4u))));
  output->scalar_kind = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb707u + (uint32_t)(uVar1 + 10) * 1u))));
  output->packed_metadata[0] = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb716u + (uint32_t)(uVar1 + 10) * 1u))));
  output->packed_metadata[1] = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb725u + (uint32_t)(uVar1 + 10) * 1u))));
  output->packed_metadata[2] = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb734u + (uint32_t)(uVar1 + 10) * 1u))));
  output->packed_metadata[3] = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb743u + (uint32_t)(uVar1 + 10) * 1u))));
  output->packed_metadata[4] = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb752u + (uint32_t)(uVar1 + 10) * 1u))));
  output->packed_metadata[5] = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb761u + (uint32_t)(uVar1 + 10) * 1u))));
  output->current_first_profile_validity = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb6dfu + (uint32_t)(uVar1) * 1u))));
  output->current_elapsed_source_validity = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebeb770u + (uint32_t)(uVar1) * 1u))));
  return;
}

void thunk_publish_routine_or_pending_write_terminal_result_4d0a4(undefined4 param_1, undefined4 param_2)

{
  publish_routine_or_pending_write_terminal_result_4d0a4(param_1, param_2);
  return;
}

void retain_and_clear_fault_record(uint slot)

{
  int iVar1;
  int iVar2;
  uint slot_00;
  
  slot_00 = slot & 0xff;
  if (slot_00 < 0x18) {
    iVar1 = (int)(short)slot_00;
    iVar2 = slot_00 * 2;
    (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe7320u + (uint32_t)(iVar1 * 6) * 2u)))) = (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe7200u + (uint32_t)(iVar1 * 6) * 2u))));
    *(undefined2 *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe710cu + (uint32_t)(iVar2) * 1u)))) = *(undefined2 *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe713cu + (uint32_t)(iVar2) * 1u))));
    (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe7322u + (uint32_t)(iVar1 * 6) * 2u)))) = (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe7202u + (uint32_t)(iVar1 * 6) * 2u))));
    (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe7324u + (uint32_t)(iVar1 * 6) * 2u)))) = (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe7204u + (uint32_t)(iVar1 * 6) * 2u))));
    (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe7326u + (uint32_t)(iVar1 * 6) * 2u)))) = (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe7206u + (uint32_t)(iVar1 * 6) * 2u))));
    (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe7328u + (uint32_t)(iVar1 * 6) * 2u)))) = (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe7208u + (uint32_t)(iVar1 * 6) * 2u))));
    *(undefined2 *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe716cu + (uint32_t)(iVar2) * 1u)))) = *(undefined2 *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe719cu + (uint32_t)(iVar2) * 1u))));
    select_retained_fault_record(slot_00);
    (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe7200u + (uint32_t)(iVar1 * 6) * 2u)))) = 0;
    *(undefined2 *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe713cu + (uint32_t)(iVar2) * 1u)))) = 0xffff;
    (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe7202u + (uint32_t)(iVar1 * 6) * 2u)))) = 0;
    (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe7204u + (uint32_t)(iVar1 * 6) * 2u)))) = 0;
    (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe7206u + (uint32_t)(iVar1 * 6) * 2u)))) = 0;
    (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe7208u + (uint32_t)(iVar1 * 6) * 2u)))) = 0;
    *(undefined2 *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe719cu + (uint32_t)(iVar2) * 1u)))) = 0xffff;
  }
  return;
}

void select_current_fault_record(uint slot)

{
  if ((slot & 0xff) < 0x18) {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe71ccu + (uint32_t)(slot & 0xff) * 1u)))) = 0x5a;
  }
  return;
}

void encode_fault_action_kind(uchar slot,uchar kind)

{
  ushort actions[5];
  
  actions[3] = 0;
  actions[4] = 0;
  actions[2] = 0;
  actions[1] = 0;
  actions[0] = 0;
  switch(kind) {
  case '\x01':
    actions[1] = 4;
    goto LAB_0003c892;
  case '\x02':
    actions[1] = 2;
    goto LAB_0003c892;
  case '\x03':
    actions[1] = 1;
LAB_0003c892:
    actions[0] = 1;
    actions[2] = 0xc;
    break;
  case '\x04':
    actions[1] = 4;
    actions[0] = 0;
    actions[2] = 0x4000;
    break;
  case '\x05':
    actions[1] = 2;
    goto LAB_0003c8c0;
  case '\x06':
    actions[1] = 1;
LAB_0003c8c0:
    actions[0] = 0;
    actions[2] = 0x8080;
    break;
  case '\a':
    actions[1] = 4;
    goto LAB_0003c8cc;
  case '\b':
    actions[1] = 2;
    goto LAB_0003c8cc;
  case '\t':
    actions[1] = 1;
LAB_0003c8cc:
    actions[0] = 0;
    actions[2] = 0;
    break;
  case '\n':
    actions[3] = 2;
    break;
  case '\v':
    actions[2] = 0x10;
    actions[1] = 4;
    actions[3] = 0x6000;
    break;
  case '\r':
    actions[1] = 0x40;
    actions[4] = 4;
    goto LAB_0003ca30;
  case '\x0e':
    actions[1] = 0x40;
    actions[4] = 8;
    goto LAB_0003ca30;
  case '\x0f':
    actions[1] = 0x40;
    actions[4] = 0x10;
    goto LAB_0003ca30;
  case '\x10':
    actions[1] = 0x20;
    actions[4] = actions[1];
    goto LAB_0003ca30;
  case '\x11':
    actions[1] = 0x20;
    actions[4] = 0x40;
    goto LAB_0003ca30;
  case '\x12':
    actions[1] = 0x40;
    actions[4] = 0x20;
    goto LAB_0003ca30;
  case '\x13':
    actions[1] = 0x40;
    actions[4] = actions[1];
    goto LAB_0003ca30;
  case '\x14':
    actions[1] = 0x40;
    goto LAB_0003ca10;
  case '\x15':
    actions[1] = 0x20;
LAB_0003ca10:
    actions[4] = 0x4000;
    goto LAB_0003ca30;
  case '\x16':
    actions[1] = 0x10;
    actions[4] = 0x4000;
    goto LAB_0003ca30;
  case '\x17':
    actions[0] = 8;
    actions[2] = 0x120;
    goto LAB_0003c8f8;
  case '\x18':
    actions[3] = 0x14;
    break;
  case '\x19':
    actions[3] = 0x28;
    break;
  case '\x1a':
    actions[0] = 1;
    actions[2] = 0xc;
LAB_0003c8f8:
    actions[1] = 4;
    actions[3] = 0x3c0;
    break;
  case '\x1b':
    actions[0] = 2;
    actions[1] = 0x40;
    actions[2] = 0x405;
    goto LAB_0003ca42;
  case '\x1c':
    actions[1] = 0x40;
    actions[2] = 0x40a;
    goto LAB_0003ca5e;
  case '\x1d':
    actions[0] = 2;
    actions[1] = 0x40;
    actions[2] = 0x444;
    goto LAB_0003ca42;
  case '\x1e':
    actions[1] = 0x40;
    actions[2] = 0x608;
    goto LAB_0003ca5e;
  case '\x1f':
    actions[0] = 2;
    actions[1] = 0x20;
    actions[2] = 0x1401;
    goto LAB_0003ca42;
  case ' ':
    actions[1] = 0x20;
    actions[2] = 0x2402;
LAB_0003ca5e:
    actions[0] = 2;
LAB_0003caf2:
    actions[4] = 2;
    actions[3] = 0x4280;
    break;
  case '!':
    actions[0] = 2;
    actions[1] = 0x40;
    actions[2] = 0x404;
    break;
  case '\"':
    actions[0] = 2;
    actions[1] = 0x40;
    actions[2] = 0x408;
    break;
  case '#':
    actions[0] = 0x10;
    actions[1] = 0x40;
    actions[2] = 0x825;
LAB_0003ca42:
    actions[3] = 0x2140;
    actions[4] = 1;
    break;
  case '$':
    actions[0] = 0x10;
    actions[1] = 0x40;
    actions[2] = 0x90a;
    goto LAB_0003caf2;
  case '%':
    actions[3] = 4;
    break;
  case '&':
    actions[3] = 0x10;
    break;
  case '\'':
    actions[3] = 8;
    break;
  case '(':
    actions[3] = 0x20;
    break;
  case '/':
    actions[3] = 0x400;
    break;
  case '0':
    actions[3] = 0x800;
    break;
  case '1':
    actions[0] = 1;
    actions[1] = 4;
    actions[2] = 0x4000;
    actions[3] = 0x1000;
    break;
  case '2':
    actions[3] = 0x8000;
    break;
  case '5':
    actions[1] = 0x40;
    actions[4] = 0x80;
    goto LAB_0003ca30;
  case '6':
    actions[1] = 0x40;
    actions[4] = 0x100;
LAB_0003ca30:
    actions[2] = 0x400;
    actions[0] = 2;
  }
  if ((DAT_000317dc & actions[4]) != 0) {
    actions[0] = 0;
    actions[1] = 0;
    actions[2] = 0;
    actions[4] = 0;
    actions[3] = 0;
  }
  merge_fault_action_record(&actions[0],(uint)slot);
  return;
}

void thunk_set_request_word_8aa8_bounded6_56cda(undefined4 param_1, undefined4 param_2)

{
  set_request_word_8aa8_bounded6_56cda(param_1, param_2);
  return;
}

void clear_direct_output_enables(void)

{
  ((volatile uint8_t *)camry_host_ptr(0xfebe8b4cu))[0] = '\0';
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe8b4cu + (uint32_t)(1) * 1u)))) = '\0';
  return;
}

void clear_direct_output_bank0(void)

{
  ((volatile uint8_t *)camry_host_ptr(0xfebe8b4cu))[0] = '\0';
  return;
}

void clear_direct_output_bank1(void)

{
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe8b4cu + (uint32_t)(1) * 1u)))) = '\0';
  return;
}

void set_direct_output_codes_bank0(ushort *codes)

{
  ((volatile uint16_t *)camry_host_ptr(0xfebe8b4eu))[0] = *codes;
  (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe8b4eu + (uint32_t)(1) * 2u)))) = codes[1];
  (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe8b4eu + (uint32_t)(2) * 2u)))) = codes[2];
  return;
}

void set_direct_output_codes_bank1(ushort *codes)

{
  ((volatile uint16_t *)camry_host_ptr(0xfebe8b54u))[0] = *codes;
  (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe8b54u + (uint32_t)(1) * 2u)))) = codes[1];
  (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0xfebe8b54u + (uint32_t)(2) * 2u)))) = codes[2];
  return;
}

void request_direct_output_bank0(void)

{
  ((volatile uint8_t *)camry_host_ptr(0xfebe8b4cu))[0] = 'Z';
  return;
}

void request_direct_output_bank1(void)

{
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe8b4cu + (uint32_t)(1) * 1u)))) = 'Z';
  return;
}

void thunk_set_secondary_priority_mask_bounded2_56f14(undefined4 param_1, undefined4 param_2)

{
  set_secondary_priority_mask_bounded2_56f14(param_1, param_2);
  return;
}

void thunk_set_priority_mask_8a9c_bounded2_56c26(undefined4 param_1, undefined4 param_2)

{
  set_priority_mask_8a9c_bounded2_56c26(param_1, param_2);
  return;
}

void set_output_request_word(uchar owner,uint request)

{
  if (owner < 8) {
    (*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xfebe8b2cu + (uint32_t)(owner) * 4u)))) = request;
  }
  return;
}

void thunk_set_byte_febe82a9_to_z_515ca(void)

{
  set_byte_febe82a9_to_z_515ca();
  return;
}

void thunk_set_two_classifier_flags_and_clear_two_counts_515d4(void)

{
  set_two_classifier_flags_and_clear_two_counts_515d4();
  return;
}

void thunk_reset_classifier_counts_and_rearm_status_flags_515e6(void)

{
  reset_classifier_counts_and_rearm_status_flags_515e6();
  return;
}

void report_diagnostic_event_failure(uint event,ushort capture_kind)

{
  char cVar1;
  uchar classification;
  uchar prior_qualification;
  uint32_t puVar2;
  uint uVar3;
  uint event_00;
  
  puVar2 = 0xfebeb800u;
  event_00 = event & 0xffff;
  if ((((event_00 - 1 < 0x17f) && (DAT_febe82d4 != '\x01')) && (DAT_febe82d4 != '\x02')) &&
     ((DAT_febe82d4 != '\x04' && (DAT_febe82d4 != '\x06')))) {
    cVar1 = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x2fc54u + (uint32_t)(event_00 * 8) * 1u))));
    classification = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x2fc51u + (uint32_t)(event_00 * 8) * 1u))));
    uVar3 = priority_mask_enter(0xff00);
    prior_qualification = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x352b)))));
    if (cVar1 < '\0') {
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x352b))))) = 0x5a;
    }
    priority_mask_restore(uVar3);
    uVar3 = get_diagnostic_event_state(event_00);
    if ((uVar3 & 1) == 0) {
      mark_diagnostic_event_failed(event_00,prior_qualification);
      gate_diagnostic_event_capture(event_00,capture_kind,prior_qualification);
      if (classification != '\0') {
        assert_diagnostic_classifier(classification);
      }
    }
    if (((*((volatile uint8_t *)camry_host_ptr((uint32_t)(puVar2 + (uint32_t)(-0x509b))))) & 0x40) == 0) {
      update_diagnostic_event_statistics(event_00,prior_qualification);
    }
  }
  return;
}

void report_diagnostic_event_pass(uint event)

{
  uchar classification;
  uint uVar1;
  uint event_00;
  
  event_00 = event & 0xffff;
  if ((((event_00 - 1 < 0x17f) && (DAT_febe82d4 != '\x01')) && (DAT_febe82d4 != '\x02')) &&
     ((DAT_febe82d4 != '\x04' && (DAT_febe82d4 != '\x06')))) {
    classification = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x2fc51u + (uint32_t)(event_00 * 8) * 1u))));
    uVar1 = get_diagnostic_event_state(event_00);
    mark_diagnostic_event_passed(event_00);
    if (((uVar1 & 1) != 0) && (classification != '\0')) {
      release_diagnostic_classifier(classification);
    }
  }
  return;
}

void report_diagnostic_healthy_observed(uint event)

{
  if ((event & 0xffff) - 1 < 0x17f) {
    mark_diagnostic_healthy_observed(event & 0xffff);
  }
  return;
}

uint get_diagnostic_event_state(uint event)

{
  int iVar1;
  uint uVar2;
  uint uVar3;
  
  uVar3 = 0;
  uVar2 = event & 0xffff;
  if ((uVar2 != 0) && (uVar2 < 0x180)) {
    iVar1 = (uVar2 >> 5) * 4;
    uVar2 = event & 0x1f;
    uVar3 = (uint)((*(uint *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe6090u + (uint32_t)(iVar1) * 1u)))) >> uVar2 & 1) != 0);
    if ((*(uint *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe60c0u + (uint32_t)(iVar1) * 1u)))) >> uVar2 & 1) != 0) {
      uVar3 = uVar3 | 2;
    }
    if ((*(uint *)(((undefined *)camry_host_ptr((uint32_t)(0xfebe60f0u + (uint32_t)(iVar1) * 1u)))) >> uVar2 & 1) != 0) {
      uVar3 = uVar3 | 4;
    }
  }
  return uVar3;
}

void thunk_clear_event_bit_from_three_bitmaps_and_mark_dirty_524be(undefined4 param_1)

{
  clear_event_bit_from_three_bitmaps_and_mark_dirty_524be(param_1);
  return;
}

void thunk_set_four_learned_quad_halfwords_35772(undefined4 param_1, undefined4 param_2, undefined4 param_3, undefined4 param_4)

{
  set_four_learned_quad_halfwords_35772(param_1, param_2, param_3, param_4);
  return;
}

void thunk_invalidate_learned_quad_record_with_default_payload_3599e(void)

{
  invalidate_learned_quad_record_with_default_payload_3599e();
  return;
}

void thunk_persist_learned_quad_record_100_35780(void)

{
  persist_learned_quad_record_100_35780();
  return;
}

void thunk_set_request_word_8a48_bounded2_5693e(undefined4 param_1, undefined4 param_2)

{
  set_request_word_8a48_bounded2_5693e(param_1, param_2);
  return;
}

void thunk_submit_up_to_eight_response_bytes_or_error_34ea4(undefined4 param_1, undefined4 param_2)

{
  submit_up_to_eight_response_bytes_or_error_34ea4(param_1, param_2);
  return;
}

void thunk_capture_and_persist_record_twelve_samples_45cfc(void)

{
  capture_and_persist_record_twelve_samples_45cfc();
  return;
}

void thunk_load_record_twelve_samples_and_arm_capture_45d98(void)

{
  load_record_twelve_samples_and_arm_capture_45d98();
  return;
}

void thunk_clear_state_bytes_6958_and_counter_695c_32c86(void)

{
  clear_state_bytes_6958_and_counter_695c_32c86();
  return;
}

void thunk_invalidate_fit_record_202_header_34bce(void)

{
  invalidate_fit_record_202_header_34bce();
  return;
}

void cancel_mode600_stimulus_fit(void)

{
  mode600_stimulus_fit_work.active = '\0';
  mode600_stimulus_fit_work.stimulus_valid = '\0';
  mode600_stimulus_fit_work.state = '\x10';
  return;
}

void thunk_set_secondary_channel_request_bounded5_56e66(undefined4 param_1, undefined4 param_2)

{
  set_secondary_channel_request_bounded5_56e66(param_1, param_2);
  return;
}

void publish_thermal_history_record(void)

{
  uint8_t stack_record_3c[60];
  uint32_t puVar1;
  
  puVar1 = 0xfebeb800u;
  if (DAT_febe7071 != '\0') {
    (*((uint16_t *)(stack_record_3c + 0))) = ((int)(int16_t)DAT_febe6f8e);
    (*((uint32_t *)(stack_record_3c + 44))) = 0;
    (*((uint16_t *)(stack_record_3c + 2))) = ((int)(int16_t)DAT_febe6f90);
    (*((uint16_t *)(stack_record_3c + 4))) = ((int)(int16_t)DAT_febe6f9e);
    (*((uint16_t *)(stack_record_3c + 6))) = ((int)(int16_t)DAT_febe6fa0);
    (*((uint16_t *)(stack_record_3c + 8))) = ((int)(int16_t)DAT_febe6f42);
    (*((uint16_t *)(stack_record_3c + 10))) = ((int)(int16_t)DAT_febe6f44);
    (*((uint16_t *)(stack_record_3c + 12))) = ((int)(int16_t)DAT_febe6f56);
    (*((uint16_t *)(stack_record_3c + 14))) = ((int)(int16_t)DAT_febe6f58);
    (*((uint16_t *)(stack_record_3c + 16))) = ((int)(int16_t)DAT_febe6f16);
    (*((uint16_t *)(stack_record_3c + 18))) = ((int)(int16_t)DAT_febe6f18);
    (*((uint16_t *)(stack_record_3c + 24))) = ((int)(int16_t)DAT_febe6eb2);
    (*((uint16_t *)(stack_record_3c + 26))) = ((int)(int16_t)DAT_febe6eb4);
    (*((uint16_t *)(stack_record_3c + 28))) = ((int)(int16_t)DAT_febe6eb6);
    (*((uint16_t *)(stack_record_3c + 30))) = ((int)(int16_t)DAT_febe6eb8);
    (*((uint16_t *)(stack_record_3c + 32))) = ((int)(int16_t)DAT_febe6eba);
    (*((uint16_t *)(stack_record_3c + 34))) = ((int)(int16_t)DAT_febe6ebc);
    (*((uint16_t *)(stack_record_3c + 36))) = ((int)(int16_t)DAT_febe6ff0);
    (*((uint16_t *)(stack_record_3c + 38))) = ((int)(int16_t)DAT_febe6ff2);
    (*((uint16_t *)(stack_record_3c + 40))) = ((int)(int16_t)DAT_febe7000);
    (*((uint16_t *)(stack_record_3c + 42))) = ((int)(int16_t)DAT_febe7002);
    (*((uint16_t *)(stack_record_3c + 20))) = ((int)(int16_t)DAT_febe707c);
    (*((uint16_t *)(stack_record_3c + 22))) = ((int)(int16_t)DAT_febe707a);
    (*((uint16_t *)(stack_record_3c + 48))) = ((int)(int16_t)DAT_febee8ac);
    if (DAT_febe7bf8 == 0) {
      if (((volatile uint8_t *)camry_host_ptr(0xfebe6fb0u))[0] == 0xa5) {
        (*((uint16_t *)(stack_record_3c + 50))) = 0xffff;
      }
      else {
        (*((uint16_t *)(stack_record_3c + 50))) = 0;
      }
    }
    else {
      (*((uint16_t *)(stack_record_3c + 50))) = 0x5aa5;
    }
    (*((uint16_t *)(stack_record_3c + 52))) = ((int)(int16_t)DAT_febe6f00);
    (*((uint16_t *)(stack_record_3c + 54))) = ((int)(int16_t)DAT_febe6f02);
    DAT_febe6ee6 = ((int)(int16_t)DAT_febe6f00);
    DAT_febe6ee8 = ((int)(int16_t)DAT_febe6f02);
    nvm_set_record(6,(uint *)stack_record_3c);
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xffffb6e4u + (uint32_t)((int)puVar1) * 1u)))) = 1;
  }
  return;
}

void invalidate_thermal_history_record(void)

{
  uint8_t stack_record_3c[60];
  
  (*((uint16_t *)(stack_record_3c + 4))) = DAT_0002b4b6;
  (*((uint16_t *)(stack_record_3c + 2))) = DAT_0002b4b4;
  (*((uint16_t *)(stack_record_3c + 6))) = DAT_0002b4b4;
  (*((uint16_t *)(stack_record_3c + 0))) = DAT_0002b4b6;
  (*((uint16_t *)(stack_record_3c + 8))) = DAT_0002b39e;
  (*((uint16_t *)(stack_record_3c + 10))) = DAT_0002b3a0;
  (*((uint16_t *)(stack_record_3c + 12))) = DAT_0002b3ba;
  (*((uint16_t *)(stack_record_3c + 14))) = DAT_0002b3bc;
  (*((uint16_t *)(stack_record_3c + 16))) = DAT_0002b31e;
  (*((uint16_t *)(stack_record_3c + 18))) = DAT_0002b320;
  (*((uint16_t *)(stack_record_3c + 24))) = DAT_0002b2a6;
  (*((uint16_t *)(stack_record_3c + 26))) = DAT_0002b2a8;
  (*((uint16_t *)(stack_record_3c + 28))) = DAT_0002b2aa;
  (*((uint16_t *)(stack_record_3c + 30))) = DAT_0002b2ac;
  (*((uint16_t *)(stack_record_3c + 32))) = DAT_0002b2ae;
  (*((uint16_t *)(stack_record_3c + 34))) = DAT_0002b2b0;
  (*((uint16_t *)(stack_record_3c + 36))) = DAT_0002b532;
  (*((uint32_t *)(stack_record_3c + 44))) = 0;
  (*((uint16_t *)(stack_record_3c + 38))) = DAT_0002b534;
  (*((uint16_t *)(stack_record_3c + 40))) = DAT_0002b54a;
  (*((uint16_t *)(stack_record_3c + 42))) = DAT_0002b54c;
  (*((uint16_t *)(stack_record_3c + 20))) = DAT_0002b5b2;
  (*((uint16_t *)(stack_record_3c + 22))) = DAT_0002b5b0;
  (*((uint16_t *)(stack_record_3c + 48))) = 0x7f80;
  (*((uint16_t *)(stack_record_3c + 50))) = 0xa55a;
  (*((uint16_t *)(stack_record_3c + 52))) = ((int)(int16_t)DAT_febe6ee6);
  (*((uint16_t *)(stack_record_3c + 54))) = ((int)(int16_t)DAT_febe6ee8);
  nvm_set_record(6,(uint *)stack_record_3c);
  return;
}

void thunk_increment_indexed_u16_counter_once_until_rearmed_545de(undefined4 param_1)

{
  increment_indexed_u16_counter_once_until_rearmed_545de(param_1);
  return;
}

void thunk_clear_indexed_counter_rearm_byte_54724(undefined4 param_1)

{
  clear_indexed_counter_rearm_byte_54724(param_1);
  return;
}

void publish_thermal_reference_record(void)

{
  uint8_t stack_record_c[12];
  
  if (DAT_febe7dcc == 'Z') {
    (*((uint16_t *)(stack_record_c + 0))) = ((int)(int16_t)DAT_febe7dce);
    (*((uint32_t *)(stack_record_c + 4))) = 0;
    (*((uint16_t *)(stack_record_c + 2))) = ((int)(int16_t)DAT_febe7dd6);
    DAT_febe7de4 = 1;
    nvm_set_record(5,(uint *)((uint16_t *)(stack_record_c)));
  }
  return;
}

uint thunk_write_record5_pair_sentinels_4841e(void)

{
  return write_record5_pair_sentinels_4841e();
}

void thunk_set_request_word_8a2c_bounded5_568dc(undefined4 param_1, undefined4 param_2)

{
  set_request_word_8a2c_bounded5_568dc(param_1, param_2);
  return;
}

void thunk_set_request_word_8a50_bounded5_569ac(undefined4 param_1, undefined4 param_2)

{
  set_request_word_8a50_bounded5_569ac(param_1, param_2);
  return;
}

void set_channel_owner_request(uchar owner,uint request_mask)

{
  if (owner < 5) {
    channel_request_state.owner_requests[owner] = request_mask;
  }
  return;
}

void thunk_set_indexed_status_mask_word_if_below_five_50c82(undefined4 param_1, undefined4 param_2)

{
  set_indexed_status_mask_word_if_below_five_50c82(param_1, param_2);
  return;
}

int thunk_publish_redundant_mode_marker_a55a_5889a(void)

{
  return publish_redundant_mode_marker_a55a_5889a();
}

undefined4 thunk_test_redundant_status_a5_or_vote_error13_588b6(void)

{
  return test_redundant_status_a5_or_vote_error13_588b6();
}

undefined1 thunk_get_state_byte_8c19_58c84(void)

{
  return get_state_byte_8c19_58c84();
}

uint query_application_nvm_readiness(void)

{
  uint uVar1;
  
  uVar1 = application_nvm_is_ready();
  return uVar1;
}
