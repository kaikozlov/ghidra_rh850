#include "common.h"

undefined1 latch_request_bits_and_check_signed_magnitude_36066(byte param_1,short param_2)

{
  int iVar1;
  undefined1 uVar2;
  int iVar3;
  
  if ((param_1 & 3) == 0) {
    uVar2 = 1;
  }
  else {
    iVar1 = (int)param_2;
    if (DAT_febe6b2e == 0) {
      if (iVar1 + 0x7fff < 0 == (-1 < iVar1 && iVar1 + 0x7fff < 0) && iVar1 != -0x7fff) {
        if (iVar1 < 0) {
          iVar1 = (int)-param_2;
        }
      }
      else {
        iVar1 = 0x7fff;
      }
      iVar3 = (int)DAT_00030e58;
      uVar2 = iVar1 - iVar3 < 0 == (iVar1 < 0 != iVar3 < 0 && iVar3 < 0 == iVar1 - iVar3 < 0) &&
              iVar1 != iVar3;
    }
    else {
      uVar2 = 2;
    }
    DAT_febe6b2e = DAT_febe6b2e | param_1;
  }
  return uVar2;
}

void request_terminal_output_ramp(void)

{
  DAT_febe6b2c = 0x5a;
  return;
}

void cancel_terminal_output_ramp(void)

{
  DAT_febe6b2c = 0;
  return;
}

void return_only_stub_360cc(void)

{
  return;
}

void initialize_6798_flag_and_countdown_360ce(void)

{
  DAT_febe6798 = 0;
  DAT_febe6799 = DAT_00030e70;
  return;
}

void update_signed_pair_threshold_countdown_360e0(void)

{
  int iVar1;
  bool bVar2;
  char cVar3;
  int iVar4;
  int iVar5;
  int iVar6;
  int iVar7;
  
  iVar5 = -(int)((int)(int16_t)DAT_febe64e2);
  cVar3 = DAT_00030e70;
  if ((DAT_febe64cc & 0x40004) == 0) {
    DAT_febe6798 = 0;
  }
  else {
    iVar6 = (int)((int)(int16_t)DAT_febe6770);
    iVar7 = (int)DAT_00030e72;
    if (((iVar6 - iVar7 < 0 == (iVar6 < 0 != iVar7 < 0 && iVar7 < 0 == iVar6 - iVar7 < 0) &&
          iVar6 != iVar7) &&
        (iVar4 = (int)DAT_00030e74, iVar1 = iVar5 + -iVar4,
        iVar1 < 0 == (iVar5 < 0 != iVar4 < 0 && iVar4 < 0 == iVar1 < 0) &&
        -iVar4 != (int)((int)(int16_t)DAT_febe64e2))) ||
       ((iVar6 + iVar7 < 0 != (iVar6 < 0 != -iVar7 < 0 && -iVar7 < 0 == iVar6 + iVar7 < 0) &&
        (iVar6 = iVar5 + DAT_00030e74, bVar2 = -(int)DAT_00030e74 < 0,
        iVar6 < 0 != (iVar5 < 0 != bVar2 && bVar2 == iVar6 < 0))))) {
      if (DAT_febe6799 == '\0') {
        DAT_febe6798 = 1;
        cVar3 = '\0';
      }
      else {
        cVar3 = DAT_febe6799 + -1;
      }
    }
  }
  DAT_febe6799 = cVar3;
  return;
}

void return_only_stub_36140(void)

{
  return;
}

void return_only_stub_36142(void)

{
  return;
}

void transform_measured_phase_currents(void)

{
  int iVar1;
  int iVar2;
  
  iVar2 = (((((int)(int16_t)DAT_febe7e46) * 2 - (int)((int)(int16_t)DAT_febe7e48)) - (int)((int)(int16_t)DAT_febe7e4a)) * 0x3441) / 0x8000;
  iVar1 = (((int)((int)(int16_t)DAT_febe7e48) - (int)((int)(int16_t)DAT_febe7e4a)) * 0x5a82) / 0x8000;
  DAT_febe6b3c = (iVar1 * (((int)(int16_t)DAT_febe7d4e) / 4) + iVar2 * (((int)(int16_t)DAT_febe7d50) / 4)) / 0x2000;
  DAT_febe6b40 = (iVar1 * (((int)(int16_t)DAT_febe7d50) / 4) - iVar2 * (((int)(int16_t)DAT_febe7d4e) / 4)) / 0x2000;
  if ((int)DAT_febe6b3c + 0x7fff < 0 == (-1 < (int)DAT_febe6b3c && (int)DAT_febe6b3c + 0x7fff < 0) &&
      ((int)(int32_t)DAT_febe6b3c) != -0x7fff) {
    iVar2 = ((int)(int32_t)DAT_febe6b3c);
    if ((int)DAT_febe6b3c + -0x7fff < 0 == ((int)DAT_febe6b3c < 0 && -1 < (int)DAT_febe6b3c + -0x7fff) &&
        ((int)(int32_t)DAT_febe6b3c) != 0x7fff) {
      iVar2 = 0x7fff;
    }
  }
  else {
    iVar2 = -0x7fff;
  }
  DAT_febe6b34 = (short)iVar2;
  if ((int)DAT_febe6b40 + 0x7fff < 0 == (-1 < (int)DAT_febe6b40 && (int)DAT_febe6b40 + 0x7fff < 0) &&
      ((int)(int32_t)DAT_febe6b40) != -0x7fff) {
    iVar2 = ((int)(int32_t)DAT_febe6b40);
    if ((int)DAT_febe6b40 + -0x7fff < 0 == ((int)DAT_febe6b40 < 0 && -1 < (int)DAT_febe6b40 + -0x7fff) &&
        ((int)(int32_t)DAT_febe6b40) != 0x7fff) {
      iVar2 = 0x7fff;
    }
  }
  else {
    iVar2 = -0x7fff;
  }
  DAT_febe6b36 = (short)iVar2;
  iVar2 = (((((int)(int16_t)DAT_febe7e4c) * 2 - (int)((int)(int16_t)DAT_febe7e4e)) - (int)((int)(int16_t)DAT_febe7e50)) * 0x3441) / 0x8000;
  iVar1 = (((int)((int)(int16_t)DAT_febe7e4e) - (int)((int)(int16_t)DAT_febe7e50)) * 0x5a82) / 0x8000;
  DAT_febe6b44 = (iVar1 * (((int)(int16_t)DAT_febe7d5a) / 4) + iVar2 * (((int)(int16_t)DAT_febe7d5c) / 4)) / 0x2000;
  DAT_febe6b48 = (iVar1 * (((int)(int16_t)DAT_febe7d5c) / 4) - iVar2 * (((int)(int16_t)DAT_febe7d5a) / 4)) / 0x2000;
  if ((int)DAT_febe6b44 + 0x7fff < 0 == (-1 < (int)DAT_febe6b44 && (int)DAT_febe6b44 + 0x7fff < 0) &&
      ((int)(int32_t)DAT_febe6b44) != -0x7fff) {
    iVar2 = ((int)(int32_t)DAT_febe6b44);
    if ((int)DAT_febe6b44 + -0x7fff < 0 == ((int)DAT_febe6b44 < 0 && -1 < (int)DAT_febe6b44 + -0x7fff) &&
        ((int)(int32_t)DAT_febe6b44) != 0x7fff) {
      iVar2 = 0x7fff;
    }
  }
  else {
    iVar2 = -0x7fff;
  }
  DAT_febe6b38 = (short)iVar2;
  if ((int)DAT_febe6b48 + 0x7fff < 0 == (-1 < (int)DAT_febe6b48 && (int)DAT_febe6b48 + 0x7fff < 0) &&
      ((int)(int32_t)DAT_febe6b48) != -0x7fff) {
    iVar2 = ((int)(int32_t)DAT_febe6b48);
    if ((int)DAT_febe6b48 + -0x7fff < 0 == ((int)DAT_febe6b48 < 0 && -1 < (int)DAT_febe6b48 + -0x7fff) &&
        ((int)(int32_t)DAT_febe6b48) != 0x7fff) {
      iVar2 = 0x7fff;
    }
  }
  else {
    iVar2 = -0x7fff;
  }
  DAT_febe6b3a = (short)iVar2;
  return;
}

void return_only_stub_36296(void)

{
  return;
}

void return_only_stub_36298(void)

{
  return;
}

void update_transient_current_reference_qualification(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  uchar uVar4;
  int iVar5;
  
  iVar2 = (int)((int)(int16_t)DAT_febe63d8);
  iVar5 = (int)((int)(int16_t)DAT_febe63d4);
  if (((DAT_febeeb94 < current_reference_qualification.window_lower_inclusive) ||
      (current_reference_qualification.window_upper_exclusive <= DAT_febeeb94)) ||
     (((iVar3 = (int)current_reference_qualification.first_absolute_threshold,
       iVar5 - iVar3 < 0 != (iVar5 < 0 != iVar3 < 0 && iVar3 < 0 == iVar5 - iVar3 < 0) &&
       (iVar1 = -iVar3,
       iVar5 + iVar3 < 0 == (iVar5 < 0 != iVar1 < 0 && iVar1 < 0 == iVar5 + iVar3 < 0) &&
       iVar5 != iVar1)) &&
      (((iVar3 = (int)current_reference_qualification.first_combined_threshold,
        iVar5 - iVar3 < 0 != (iVar5 < 0 != iVar3 < 0 && iVar3 < 0 == iVar5 - iVar3 < 0) &&
        (iVar1 = -iVar3,
        iVar5 + iVar3 < 0 == (iVar5 < 0 != iVar1 < 0 && iVar1 < 0 == iVar5 + iVar3 < 0) &&
        iVar5 != iVar1)) ||
       ((iVar5 = (int)current_reference_qualification.second_combined_threshold,
        iVar2 - iVar5 < 0 != (iVar2 < 0 != iVar5 < 0 && iVar5 < 0 == iVar2 - iVar5 < 0) &&
        (iVar3 = -iVar5,
        iVar2 + iVar5 < 0 == (iVar2 < 0 != iVar3 < 0 && iVar3 < 0 == iVar2 + iVar5 < 0) &&
        iVar2 != iVar3)))))))) {
    uVar4 = '\0';
  }
  else {
    uVar4 = 'Z';
  }
  if (((((current_reference_transient.previous_predicate == '\0') && (uVar4 == 'Z')) ||
       ((current_reference_transient.active == 'Z' &&
        (current_reference_transient.invocation_count <
         current_reference_qualification.count_limit)))) &&
      (((DAT_febe7568 == '\0' && (DAT_febee603 == '\0')) && ((DAT_febe71ec & 0x1ff) == 0)))) &&
     (DAT_febeeb83 == '\x11')) {
    current_reference_transient.active = 'Z';
    if (current_reference_transient.invocation_count <
        current_reference_qualification.count_limit) {
      current_reference_transient.invocation_count =
           current_reference_transient.invocation_count + 1;
    }
  }
  else {
    current_reference_transient.active = '\0';
    current_reference_transient.invocation_count = 0;
  }
  current_reference_transient.previous_predicate = uVar4;
  return;
}

void return_only_stub_36344(void)

{
  return;
}

void reset_bank0_current_reference_feedback(void)

{
  (*((volatile int16_t *)camry_host_ptr((uint32_t)(0xfebe6b50u + (uint32_t)(0) * (uint32_t)sizeof(F33CurrentReferenceFeedbackState) + (uint32_t)offsetof(F33CurrentReferenceFeedbackState, request))))) = 0;
  (*((volatile int32_t *)camry_host_ptr((uint32_t)(0xfebe6b50u + (uint32_t)(0) * (uint32_t)sizeof(F33CurrentReferenceFeedbackState) + (uint32_t)offsetof(F33CurrentReferenceFeedbackState, error))))) = 0;
  (*((volatile int16_t *)camry_host_ptr((uint32_t)(0xfebe6b50u + (uint32_t)(0) * (uint32_t)sizeof(F33CurrentReferenceFeedbackState) + (uint32_t)offsetof(F33CurrentReferenceFeedbackState, previous_error))))) = 0;
  (*((volatile int32_t *)camry_host_ptr((uint32_t)(0xfebe6b50u + (uint32_t)(0) * (uint32_t)sizeof(F33CurrentReferenceFeedbackState) + (uint32_t)offsetof(F33CurrentReferenceFeedbackState, opaque_14))))) = 0;
  (*((volatile int32_t *)camry_host_ptr((uint32_t)(0xfebe6b50u + (uint32_t)(0) * (uint32_t)sizeof(F33CurrentReferenceFeedbackState) + (uint32_t)offsetof(F33CurrentReferenceFeedbackState, request_before_global_clamp))))) = 0;
  (*((volatile int32_t *)camry_host_ptr((uint32_t)(0xfebe6b50u + (uint32_t)(0) * (uint32_t)sizeof(F33CurrentReferenceFeedbackState) + (uint32_t)offsetof(F33CurrentReferenceFeedbackState, current_gain))))) = 0;
  (*((volatile int32_t *)camry_host_ptr((uint32_t)(0xfebe6b50u + (uint32_t)(0) * (uint32_t)sizeof(F33CurrentReferenceFeedbackState) + (uint32_t)offsetof(F33CurrentReferenceFeedbackState, previous_gain))))) = 0;
  (*((volatile int32_t *)camry_host_ptr((uint32_t)(0xfebe6b50u + (uint32_t)(0) * (uint32_t)sizeof(F33CurrentReferenceFeedbackState) + (uint32_t)offsetof(F33CurrentReferenceFeedbackState, retained_transient_delta))))) = 0;
  (*((volatile int32_t *)camry_host_ptr((uint32_t)(0xfebe6b50u + (uint32_t)(0) * (uint32_t)sizeof(F33CurrentReferenceFeedbackState) + (uint32_t)offsetof(F33CurrentReferenceFeedbackState, saturated_base_plus_delta))))) = 0;
  return;
}

void initialize_bank0_current_reference_feedback(void)

{
  reset_bank0_current_reference_feedback();
  return;
}

void update_bank0_current_reference_feedback(void)

{
  short sVar1;
  int iVar3;
  int iVar4;
  int iVar5;
  int iVar6;
  int iVar7;
  short sVar2;
  
  iVar5 = (int)shared_second_axis_envelope;
  iVar6 = (int)(*((volatile int16_t *)camry_host_ptr((uint32_t)(0xfebe6be8u + (uint32_t)(0) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeState) + (uint32_t)offsetof(F33RegulatorOutputEnvelopeState, second_upper)))));
  iVar3 = (*((volatile int32_t *)camry_host_ptr((uint32_t)(0xfebe6be8u + (uint32_t)(0) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeState) + (uint32_t)offsetof(F33RegulatorOutputEnvelopeState, second_unclipped)))));
  if ((*((volatile int32_t *)camry_host_ptr((uint32_t)(0xfebe6be8u + (uint32_t)(0) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeState) + (uint32_t)offsetof(F33RegulatorOutputEnvelopeState, second_unclipped))))) + -0x7fff < 0 ==
      ((*((volatile int32_t *)camry_host_ptr((uint32_t)(0xfebe6be8u + (uint32_t)(0) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeState) + (uint32_t)offsetof(F33RegulatorOutputEnvelopeState, second_unclipped))))) < 0 &&
      -1 < (*((volatile int32_t *)camry_host_ptr((uint32_t)(0xfebe6be8u + (uint32_t)(0) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeState) + (uint32_t)offsetof(F33RegulatorOutputEnvelopeState, second_unclipped))))) + -0x7fff)) {
    iVar3 = 0x7fff;
  }
  if (iVar3 + 0x7fff < 0 != (-1 < iVar3 && iVar3 + 0x7fff < 0)) {
    iVar3 = -0x7fff;
  }
  iVar4 = (int)(short)iVar3;
  iVar7 = iVar6;
  if ((((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x31950u + (uint32_t)(0) * (uint32_t)sizeof(F33CurrentReferenceFeedbackCalibration) + (uint32_t)offsetof(F33CurrentReferenceFeedbackCalibration, bypass_shared_ceiling))))) == '\0') &&
      ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x31950u + (uint32_t)(0) * (uint32_t)sizeof(F33CurrentReferenceFeedbackCalibration) + (uint32_t)offsetof(F33CurrentReferenceFeedbackCalibration, shared_ceiling_enabled))))) != '\0')) &&
     (iVar7 = iVar5,
     iVar5 - iVar6 < 0 == (iVar5 < 0 != iVar6 < 0 && iVar6 < 0 == iVar5 - iVar6 < 0) &&
     iVar5 != iVar6)) {
    iVar7 = iVar6;
  }
  if (iVar4 + 0x7fff < 0 == (-1 < iVar4 && iVar4 + 0x7fff < 0) && iVar4 != -0x7fff) {
    if (iVar4 < 0) {
      iVar4 = (int)(short)-(short)iVar3;
    }
  }
  else {
    iVar4 = 0x7fff;
  }
  if (iVar7 == 0) {
    iVar4 = (int)(*((volatile int16_t *)camry_host_ptr((uint32_t)(0x31950u + (uint32_t)(0) * (uint32_t)sizeof(F33CurrentReferenceFeedbackCalibration) + (uint32_t)offsetof(F33CurrentReferenceFeedbackCalibration, ratio_upper)))));
  }
  else {
    iVar4 = iVar4 << 10;
    if (iVar7 != 0) {
      if (iVar4 == -0x80000000 && iVar7 == -1) {
        iVar4 = -0x80000000;
      }
      else {
        iVar4 = (int)iVar4 / (int)iVar7;
      }
    }
  }
  iVar3 = (int)(*((volatile int16_t *)camry_host_ptr((uint32_t)(0x31950u + (uint32_t)(0) * (uint32_t)sizeof(F33CurrentReferenceFeedbackCalibration) + (uint32_t)offsetof(F33CurrentReferenceFeedbackCalibration, ratio_upper)))));
  if (iVar3 - iVar4 < 0 != (iVar3 < 0 != iVar4 < 0 && iVar4 < 0 == iVar3 - iVar4 < 0)) {
    iVar4 = iVar3;
  }
  if (iVar4 < 0) {
    iVar4 = 0;
  }
  (*((volatile int16_t *)camry_host_ptr((uint32_t)(0xfebe6b50u + (uint32_t)(0) * (uint32_t)sizeof(F33CurrentReferenceFeedbackState) + (uint32_t)offsetof(F33CurrentReferenceFeedbackState, ratio))))) = (short)iVar4;
  iVar5 = (int)(*((volatile int16_t *)camry_host_ptr((uint32_t)(0x31950u + (uint32_t)(0) * (uint32_t)sizeof(F33CurrentReferenceFeedbackCalibration) + (uint32_t)offsetof(F33CurrentReferenceFeedbackCalibration, ratio_target))))) - (int)(short)iVar4;
  if (iVar3 - iVar5 < 0 != (iVar3 < 0 != iVar5 < 0 && iVar5 < 0 == iVar3 - iVar5 < 0)) {
    iVar5 = iVar3;
  }
  (*((volatile int32_t *)camry_host_ptr((uint32_t)(0xfebe6b50u + (uint32_t)(0) * (uint32_t)sizeof(F33CurrentReferenceFeedbackState) + (uint32_t)offsetof(F33CurrentReferenceFeedbackState, error))))) =
       (int)(*((volatile int16_t *)camry_host_ptr((uint32_t)(0x31950u + (uint32_t)(0) * (uint32_t)sizeof(F33CurrentReferenceFeedbackCalibration) + (uint32_t)offsetof(F33CurrentReferenceFeedbackCalibration, error_lower)))));
  if (iVar5 - (*((volatile int32_t *)camry_host_ptr((uint32_t)(0xfebe6b50u + (uint32_t)(0) * (uint32_t)sizeof(F33CurrentReferenceFeedbackState) + (uint32_t)offsetof(F33CurrentReferenceFeedbackState, error))))) < 0 ==
      (iVar5 < 0 != (*((volatile int32_t *)camry_host_ptr((uint32_t)(0xfebe6b50u + (uint32_t)(0) * (uint32_t)sizeof(F33CurrentReferenceFeedbackState) + (uint32_t)offsetof(F33CurrentReferenceFeedbackState, error))))) < 0 &&
      (*((volatile int32_t *)camry_host_ptr((uint32_t)(0xfebe6b50u + (uint32_t)(0) * (uint32_t)sizeof(F33CurrentReferenceFeedbackState) + (uint32_t)offsetof(F33CurrentReferenceFeedbackState, error))))) < 0 ==
      iVar5 - (*((volatile int32_t *)camry_host_ptr((uint32_t)(0xfebe6b50u + (uint32_t)(0) * (uint32_t)sizeof(F33CurrentReferenceFeedbackState) + (uint32_t)offsetof(F33CurrentReferenceFeedbackState, error))))) < 0)) {
    (*((volatile int32_t *)camry_host_ptr((uint32_t)(0xfebe6b50u + (uint32_t)(0) * (uint32_t)sizeof(F33CurrentReferenceFeedbackState) + (uint32_t)offsetof(F33CurrentReferenceFeedbackState, error))))) = iVar5;
  }
  if ((DAT_febe71ec & 3) != 0) {
    (*((volatile int32_t *)camry_host_ptr((uint32_t)(0xfebe6b50u + (uint32_t)(0) * (uint32_t)sizeof(F33CurrentReferenceFeedbackState) + (uint32_t)offsetof(F33CurrentReferenceFeedbackState, error))))) = (*((volatile int32_t *)camry_host_ptr((uint32_t)(0xfebe6b50u + (uint32_t)(0) * (uint32_t)sizeof(F33CurrentReferenceFeedbackState) + (uint32_t)offsetof(F33CurrentReferenceFeedbackState, error))))) / 2;
  }
  sVar1 = (*((volatile int16_t *)camry_host_ptr((uint32_t)(0x31950u + (uint32_t)(0) * (uint32_t)sizeof(F33CurrentReferenceFeedbackCalibration) + (uint32_t)offsetof(F33CurrentReferenceFeedbackCalibration, normal_current_gain)))));
  sVar2 = (*((volatile int16_t *)camry_host_ptr((uint32_t)(0x31950u + (uint32_t)(0) * (uint32_t)sizeof(F33CurrentReferenceFeedbackCalibration) + (uint32_t)offsetof(F33CurrentReferenceFeedbackCalibration, normal_previous_gain)))));
  if (current_reference_transient.active == 'Z') {
    sVar1 = (*((volatile int16_t *)camry_host_ptr((uint32_t)(0x31950u + (uint32_t)(0) * (uint32_t)sizeof(F33CurrentReferenceFeedbackCalibration) + (uint32_t)offsetof(F33CurrentReferenceFeedbackCalibration, transient_current_gain)))));
    sVar2 = (*((volatile int16_t *)camry_host_ptr((uint32_t)(0x31950u + (uint32_t)(0) * (uint32_t)sizeof(F33CurrentReferenceFeedbackCalibration) + (uint32_t)offsetof(F33CurrentReferenceFeedbackCalibration, transient_previous_gain)))));
  }
  (*((volatile int32_t *)camry_host_ptr((uint32_t)(0xfebe6b50u + (uint32_t)(0) * (uint32_t)sizeof(F33CurrentReferenceFeedbackState) + (uint32_t)offsetof(F33CurrentReferenceFeedbackState, previous_gain))))) = (int)sVar2;
  (*((volatile int32_t *)camry_host_ptr((uint32_t)(0xfebe6b50u + (uint32_t)(0) * (uint32_t)sizeof(F33CurrentReferenceFeedbackState) + (uint32_t)offsetof(F33CurrentReferenceFeedbackState, current_gain))))) = (int)sVar1;
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)(0x31950u + (uint32_t)(0) * (uint32_t)sizeof(F33CurrentReferenceFeedbackCalibration) + (uint32_t)offsetof(F33CurrentReferenceFeedbackCalibration, error_gain_scaling_enabled))))) == 'Z') {
    iVar3 = (*((volatile int32_t *)camry_host_ptr((uint32_t)(0x31950u + (uint32_t)(0) * (uint32_t)sizeof(F33CurrentReferenceFeedbackCalibration) + (uint32_t)offsetof(F33CurrentReferenceFeedbackCalibration, nonpositive_error_gain_scale)))));
    if (0 < (*((volatile int32_t *)camry_host_ptr((uint32_t)(0xfebe6b50u + (uint32_t)(0) * (uint32_t)sizeof(F33CurrentReferenceFeedbackState) + (uint32_t)offsetof(F33CurrentReferenceFeedbackState, error)))))) {
      iVar3 = (*((volatile int32_t *)camry_host_ptr((uint32_t)(0x31950u + (uint32_t)(0) * (uint32_t)sizeof(F33CurrentReferenceFeedbackCalibration) + (uint32_t)offsetof(F33CurrentReferenceFeedbackCalibration, positive_error_gain_scale)))));
    }
    iVar3 = ((*((volatile int32_t *)camry_host_ptr((uint32_t)(0xfebe6b50u + (uint32_t)(0) * (uint32_t)sizeof(F33CurrentReferenceFeedbackState) + (uint32_t)offsetof(F33CurrentReferenceFeedbackState, error))))) * iVar3) / 0x1000;
    (*((volatile int32_t *)camry_host_ptr((uint32_t)(0xfebe6b50u + (uint32_t)(0) * (uint32_t)sizeof(F33CurrentReferenceFeedbackState) + (uint32_t)offsetof(F33CurrentReferenceFeedbackState, current_gain))))) =
         ((*((volatile int32_t *)camry_host_ptr((uint32_t)(0xfebe6b50u + (uint32_t)(0) * (uint32_t)sizeof(F33CurrentReferenceFeedbackState) + (uint32_t)offsetof(F33CurrentReferenceFeedbackState, current_gain))))) * iVar3) / 0x1000;
    (*((volatile int32_t *)camry_host_ptr((uint32_t)(0xfebe6b50u + (uint32_t)(0) * (uint32_t)sizeof(F33CurrentReferenceFeedbackState) + (uint32_t)offsetof(F33CurrentReferenceFeedbackState, previous_gain))))) =
         ((*((volatile int32_t *)camry_host_ptr((uint32_t)(0xfebe6b50u + (uint32_t)(0) * (uint32_t)sizeof(F33CurrentReferenceFeedbackState) + (uint32_t)offsetof(F33CurrentReferenceFeedbackState, previous_gain))))) * iVar3) / 0x1000;
  }
  iVar6 = (int)first_current_feedback_baseline;
  iVar5 = iVar6 * 0x8000;
  iVar3 = (*((volatile int32_t *)camry_host_ptr((uint32_t)(0xfebe6b50u + (uint32_t)(0) * (uint32_t)sizeof(F33CurrentReferenceFeedbackState) + (uint32_t)offsetof(F33CurrentReferenceFeedbackState, current_gain))))) * (*((volatile int32_t *)camry_host_ptr((uint32_t)(0xfebe6b50u + (uint32_t)(0) * (uint32_t)sizeof(F33CurrentReferenceFeedbackState) + (uint32_t)offsetof(F33CurrentReferenceFeedbackState, error))))) -
          (*((volatile int32_t *)camry_host_ptr((uint32_t)(0xfebe6b50u + (uint32_t)(0) * (uint32_t)sizeof(F33CurrentReferenceFeedbackState) + (uint32_t)offsetof(F33CurrentReferenceFeedbackState, previous_gain))))) *
          (*((volatile int16_t *)camry_host_ptr((uint32_t)(0xfebe6b50u + (uint32_t)(0) * (uint32_t)sizeof(F33CurrentReferenceFeedbackState) + (uint32_t)offsetof(F33CurrentReferenceFeedbackState, previous_error)))));
  if (iVar5 < 1) {
    if ((iVar3 < 1) &&
       (iVar4 = iVar6 * -0x8000 + -0x7fffffff,
       iVar4 - iVar3 < 0 == (iVar4 < 0 != iVar3 < 0 && iVar3 < 0 == iVar4 - iVar3 < 0) &&
       iVar4 != iVar3)) {
      iVar3 = -0x7fffffff;
      goto LAB_00036494;
    }
  }
  else if ((0 < iVar3) &&
          (iVar7 = iVar6 * -0x8000 + 0x7fffffff, iVar4 = iVar7 - iVar3,
          iVar4 < 0 != (iVar7 < 0 != iVar3 < 0 && iVar3 < 0 == iVar4 < 0))) {
    iVar3 = 0x7fffffff;
    goto LAB_00036494;
  }
  iVar3 = iVar3 + iVar5;
LAB_00036494:
  (*((volatile int32_t *)camry_host_ptr((uint32_t)(0xfebe6b50u + (uint32_t)(0) * (uint32_t)sizeof(F33CurrentReferenceFeedbackState) + (uint32_t)offsetof(F33CurrentReferenceFeedbackState, saturated_base_plus_delta))))) = iVar3;
  if (current_reference_transient.active == 'Z') {
    iVar3 = iVar3 + iVar6 * -0x8000;
    if ((*((volatile int32_t *)camry_host_ptr((uint32_t)(0x31950u + (uint32_t)(0) * (uint32_t)sizeof(F33CurrentReferenceFeedbackCalibration) + (uint32_t)offsetof(F33CurrentReferenceFeedbackCalibration, transient_delta_upper))))) - iVar3 < 0 !=
        ((*((volatile int32_t *)camry_host_ptr((uint32_t)(0x31950u + (uint32_t)(0) * (uint32_t)sizeof(F33CurrentReferenceFeedbackCalibration) + (uint32_t)offsetof(F33CurrentReferenceFeedbackCalibration, transient_delta_upper))))) < 0 != iVar3 < 0 &&
        iVar3 < 0 == (*((volatile int32_t *)camry_host_ptr((uint32_t)(0x31950u + (uint32_t)(0) * (uint32_t)sizeof(F33CurrentReferenceFeedbackCalibration) + (uint32_t)offsetof(F33CurrentReferenceFeedbackCalibration, transient_delta_upper))))) - iVar3 < 0
        )) {
      iVar3 = (*((volatile int32_t *)camry_host_ptr((uint32_t)(0x31950u + (uint32_t)(0) * (uint32_t)sizeof(F33CurrentReferenceFeedbackCalibration) + (uint32_t)offsetof(F33CurrentReferenceFeedbackCalibration, transient_delta_upper)))));
    }
    (*((volatile int32_t *)camry_host_ptr((uint32_t)(0xfebe6b50u + (uint32_t)(0) * (uint32_t)sizeof(F33CurrentReferenceFeedbackState) + (uint32_t)offsetof(F33CurrentReferenceFeedbackState, retained_transient_delta))))) =
         (*((volatile int32_t *)camry_host_ptr((uint32_t)(0x31950u + (uint32_t)(0) * (uint32_t)sizeof(F33CurrentReferenceFeedbackCalibration) + (uint32_t)offsetof(F33CurrentReferenceFeedbackCalibration, transient_delta_lower)))));
    if (iVar3 - (*((volatile int32_t *)camry_host_ptr((uint32_t)(0x31950u + (uint32_t)(0) * (uint32_t)sizeof(F33CurrentReferenceFeedbackCalibration) + (uint32_t)offsetof(F33CurrentReferenceFeedbackCalibration, transient_delta_lower))))) < 0 ==
        (iVar3 < 0 != (*((volatile int32_t *)camry_host_ptr((uint32_t)(0x31950u + (uint32_t)(0) * (uint32_t)sizeof(F33CurrentReferenceFeedbackCalibration) + (uint32_t)offsetof(F33CurrentReferenceFeedbackCalibration, transient_delta_lower))))) < 0 &&
        (*((volatile int32_t *)camry_host_ptr((uint32_t)(0x31950u + (uint32_t)(0) * (uint32_t)sizeof(F33CurrentReferenceFeedbackCalibration) + (uint32_t)offsetof(F33CurrentReferenceFeedbackCalibration, transient_delta_lower))))) < 0 ==
        iVar3 - (*((volatile int32_t *)camry_host_ptr((uint32_t)(0x31950u + (uint32_t)(0) * (uint32_t)sizeof(F33CurrentReferenceFeedbackCalibration) + (uint32_t)offsetof(F33CurrentReferenceFeedbackCalibration, transient_delta_lower))))) < 0)) {
      (*((volatile int32_t *)camry_host_ptr((uint32_t)(0xfebe6b50u + (uint32_t)(0) * (uint32_t)sizeof(F33CurrentReferenceFeedbackState) + (uint32_t)offsetof(F33CurrentReferenceFeedbackState, retained_transient_delta))))) = iVar3;
    }
    iVar3 = (*((volatile int32_t *)camry_host_ptr((uint32_t)(0xfebe6b50u + (uint32_t)(0) * (uint32_t)sizeof(F33CurrentReferenceFeedbackState) + (uint32_t)offsetof(F33CurrentReferenceFeedbackState, retained_transient_delta))))) + iVar5;
  }
  (*((volatile int32_t *)camry_host_ptr((uint32_t)(0xfebe6b50u + (uint32_t)(0) * (uint32_t)sizeof(F33CurrentReferenceFeedbackState) + (uint32_t)offsetof(F33CurrentReferenceFeedbackState, request_before_global_clamp))))) = iVar3;
  if ((*((volatile int32_t *)camry_host_ptr((uint32_t)(0x31950u + (uint32_t)(0) * (uint32_t)sizeof(F33CurrentReferenceFeedbackCalibration) + (uint32_t)offsetof(F33CurrentReferenceFeedbackCalibration, request_upper_q15))))) - iVar3 < 0 !=
      ((*((volatile int32_t *)camry_host_ptr((uint32_t)(0x31950u + (uint32_t)(0) * (uint32_t)sizeof(F33CurrentReferenceFeedbackCalibration) + (uint32_t)offsetof(F33CurrentReferenceFeedbackCalibration, request_upper_q15))))) < 0 != iVar3 < 0 &&
      iVar3 < 0 == (*((volatile int32_t *)camry_host_ptr((uint32_t)(0x31950u + (uint32_t)(0) * (uint32_t)sizeof(F33CurrentReferenceFeedbackCalibration) + (uint32_t)offsetof(F33CurrentReferenceFeedbackCalibration, request_upper_q15))))) - iVar3 < 0)) {
    iVar3 = (*((volatile int32_t *)camry_host_ptr((uint32_t)(0x31950u + (uint32_t)(0) * (uint32_t)sizeof(F33CurrentReferenceFeedbackCalibration) + (uint32_t)offsetof(F33CurrentReferenceFeedbackCalibration, request_upper_q15)))));
  }
  (*((volatile int16_t *)camry_host_ptr((uint32_t)(0xfebe6b50u + (uint32_t)(0) * (uint32_t)sizeof(F33CurrentReferenceFeedbackState) + (uint32_t)offsetof(F33CurrentReferenceFeedbackState, previous_error))))) = (short)(*((volatile int32_t *)camry_host_ptr((uint32_t)(0xfebe6b50u + (uint32_t)(0) * (uint32_t)sizeof(F33CurrentReferenceFeedbackState) + (uint32_t)offsetof(F33CurrentReferenceFeedbackState, error)))));
  iVar5 = (*((volatile int32_t *)camry_host_ptr((uint32_t)(0x31950u + (uint32_t)(0) * (uint32_t)sizeof(F33CurrentReferenceFeedbackCalibration) + (uint32_t)offsetof(F33CurrentReferenceFeedbackCalibration, request_lower_q15)))));
  if (iVar3 - (*((volatile int32_t *)camry_host_ptr((uint32_t)(0x31950u + (uint32_t)(0) * (uint32_t)sizeof(F33CurrentReferenceFeedbackCalibration) + (uint32_t)offsetof(F33CurrentReferenceFeedbackCalibration, request_lower_q15))))) < 0 ==
      (iVar3 < 0 != (*((volatile int32_t *)camry_host_ptr((uint32_t)(0x31950u + (uint32_t)(0) * (uint32_t)sizeof(F33CurrentReferenceFeedbackCalibration) + (uint32_t)offsetof(F33CurrentReferenceFeedbackCalibration, request_lower_q15))))) < 0 &&
      (*((volatile int32_t *)camry_host_ptr((uint32_t)(0x31950u + (uint32_t)(0) * (uint32_t)sizeof(F33CurrentReferenceFeedbackCalibration) + (uint32_t)offsetof(F33CurrentReferenceFeedbackCalibration, request_lower_q15))))) < 0 ==
      iVar3 - (*((volatile int32_t *)camry_host_ptr((uint32_t)(0x31950u + (uint32_t)(0) * (uint32_t)sizeof(F33CurrentReferenceFeedbackCalibration) + (uint32_t)offsetof(F33CurrentReferenceFeedbackCalibration, request_lower_q15))))) < 0)) {
    iVar5 = iVar3;
  }
  (*((volatile int16_t *)camry_host_ptr((uint32_t)(0xfebe6b50u + (uint32_t)(0) * (uint32_t)sizeof(F33CurrentReferenceFeedbackState) + (uint32_t)offsetof(F33CurrentReferenceFeedbackState, request))))) = (short)(iVar5 / 0x8000);
  return;
}

void return_only_stub_364dc(void)

{
  return;
}

void reset_bank1_current_reference_feedback(void)

{
  (*((volatile int16_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe6b50u + (uint32_t)(1) * (uint32_t)sizeof(F33CurrentReferenceFeedbackState)) + (uint32_t)(0) * (uint32_t)sizeof(F33CurrentReferenceFeedbackState) + (uint32_t)offsetof(F33CurrentReferenceFeedbackState, request))))) = 0;
  (*((volatile int32_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe6b50u + (uint32_t)(1) * (uint32_t)sizeof(F33CurrentReferenceFeedbackState)) + (uint32_t)(0) * (uint32_t)sizeof(F33CurrentReferenceFeedbackState) + (uint32_t)offsetof(F33CurrentReferenceFeedbackState, error))))) = 0;
  (*((volatile int16_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe6b50u + (uint32_t)(1) * (uint32_t)sizeof(F33CurrentReferenceFeedbackState)) + (uint32_t)(0) * (uint32_t)sizeof(F33CurrentReferenceFeedbackState) + (uint32_t)offsetof(F33CurrentReferenceFeedbackState, previous_error))))) = 0;
  (*((volatile int32_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe6b50u + (uint32_t)(1) * (uint32_t)sizeof(F33CurrentReferenceFeedbackState)) + (uint32_t)(0) * (uint32_t)sizeof(F33CurrentReferenceFeedbackState) + (uint32_t)offsetof(F33CurrentReferenceFeedbackState, opaque_14))))) = 0;
  (*((volatile int32_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe6b50u + (uint32_t)(1) * (uint32_t)sizeof(F33CurrentReferenceFeedbackState)) + (uint32_t)(0) * (uint32_t)sizeof(F33CurrentReferenceFeedbackState) + (uint32_t)offsetof(F33CurrentReferenceFeedbackState, request_before_global_clamp))))) = 0;
  (*((volatile int32_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe6b50u + (uint32_t)(1) * (uint32_t)sizeof(F33CurrentReferenceFeedbackState)) + (uint32_t)(0) * (uint32_t)sizeof(F33CurrentReferenceFeedbackState) + (uint32_t)offsetof(F33CurrentReferenceFeedbackState, current_gain))))) = 0;
  (*((volatile int32_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe6b50u + (uint32_t)(1) * (uint32_t)sizeof(F33CurrentReferenceFeedbackState)) + (uint32_t)(0) * (uint32_t)sizeof(F33CurrentReferenceFeedbackState) + (uint32_t)offsetof(F33CurrentReferenceFeedbackState, previous_gain))))) = 0;
  (*((volatile int32_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe6b50u + (uint32_t)(1) * (uint32_t)sizeof(F33CurrentReferenceFeedbackState)) + (uint32_t)(0) * (uint32_t)sizeof(F33CurrentReferenceFeedbackState) + (uint32_t)offsetof(F33CurrentReferenceFeedbackState, retained_transient_delta))))) = 0;
  (*((volatile int32_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe6b50u + (uint32_t)(1) * (uint32_t)sizeof(F33CurrentReferenceFeedbackState)) + (uint32_t)(0) * (uint32_t)sizeof(F33CurrentReferenceFeedbackState) + (uint32_t)offsetof(F33CurrentReferenceFeedbackState, saturated_base_plus_delta))))) = 0;
  return;
}

void initialize_bank1_current_reference_feedback(void)

{
  reset_bank1_current_reference_feedback();
  return;
}

void update_bank1_current_reference_feedback(void)

{
  short sVar1;
  int iVar3;
  int iVar4;
  int iVar5;
  int iVar6;
  int iVar7;
  short sVar2;
  
  iVar5 = (int)shared_second_axis_envelope;
  iVar6 = (int)(*((volatile int16_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe6be8u + (uint32_t)(1) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeState)) + (uint32_t)(0) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeState) + (uint32_t)offsetof(F33RegulatorOutputEnvelopeState, second_upper)))));
  iVar3 = (*((volatile int32_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe6be8u + (uint32_t)(1) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeState)) + (uint32_t)(0) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeState) + (uint32_t)offsetof(F33RegulatorOutputEnvelopeState, second_unclipped)))));
  if ((*((volatile int32_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe6be8u + (uint32_t)(1) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeState)) + (uint32_t)(0) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeState) + (uint32_t)offsetof(F33RegulatorOutputEnvelopeState, second_unclipped))))) + -0x7fff < 0 ==
      ((*((volatile int32_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe6be8u + (uint32_t)(1) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeState)) + (uint32_t)(0) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeState) + (uint32_t)offsetof(F33RegulatorOutputEnvelopeState, second_unclipped))))) < 0 &&
      -1 < (*((volatile int32_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe6be8u + (uint32_t)(1) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeState)) + (uint32_t)(0) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeState) + (uint32_t)offsetof(F33RegulatorOutputEnvelopeState, second_unclipped))))) + -0x7fff)) {
    iVar3 = 0x7fff;
  }
  if (iVar3 + 0x7fff < 0 != (-1 < iVar3 && iVar3 + 0x7fff < 0)) {
    iVar3 = -0x7fff;
  }
  iVar4 = (int)(short)iVar3;
  iVar7 = iVar6;
  if ((((*((volatile uint8_t *)camry_host_ptr((uint32_t)((uint32_t)(0x31950u + (uint32_t)(1) * (uint32_t)sizeof(F33CurrentReferenceFeedbackCalibration)) + (uint32_t)(0) * (uint32_t)sizeof(F33CurrentReferenceFeedbackCalibration) + (uint32_t)offsetof(F33CurrentReferenceFeedbackCalibration, bypass_shared_ceiling))))) == '\0') &&
      ((*((volatile uint8_t *)camry_host_ptr((uint32_t)((uint32_t)(0x31950u + (uint32_t)(1) * (uint32_t)sizeof(F33CurrentReferenceFeedbackCalibration)) + (uint32_t)(0) * (uint32_t)sizeof(F33CurrentReferenceFeedbackCalibration) + (uint32_t)offsetof(F33CurrentReferenceFeedbackCalibration, shared_ceiling_enabled))))) != '\0')) &&
     (iVar7 = iVar5,
     iVar5 - iVar6 < 0 == (iVar5 < 0 != iVar6 < 0 && iVar6 < 0 == iVar5 - iVar6 < 0) &&
     iVar5 != iVar6)) {
    iVar7 = iVar6;
  }
  if (iVar4 + 0x7fff < 0 == (-1 < iVar4 && iVar4 + 0x7fff < 0) && iVar4 != -0x7fff) {
    if (iVar4 < 0) {
      iVar4 = (int)(short)-(short)iVar3;
    }
  }
  else {
    iVar4 = 0x7fff;
  }
  if (iVar7 == 0) {
    iVar4 = (int)(*((volatile int16_t *)camry_host_ptr((uint32_t)((uint32_t)(0x31950u + (uint32_t)(1) * (uint32_t)sizeof(F33CurrentReferenceFeedbackCalibration)) + (uint32_t)(0) * (uint32_t)sizeof(F33CurrentReferenceFeedbackCalibration) + (uint32_t)offsetof(F33CurrentReferenceFeedbackCalibration, ratio_upper)))));
  }
  else {
    iVar4 = iVar4 << 10;
    if (iVar7 != 0) {
      if (iVar4 == -0x80000000 && iVar7 == -1) {
        iVar4 = -0x80000000;
      }
      else {
        iVar4 = (int)iVar4 / (int)iVar7;
      }
    }
  }
  iVar3 = (int)(*((volatile int16_t *)camry_host_ptr((uint32_t)((uint32_t)(0x31950u + (uint32_t)(1) * (uint32_t)sizeof(F33CurrentReferenceFeedbackCalibration)) + (uint32_t)(0) * (uint32_t)sizeof(F33CurrentReferenceFeedbackCalibration) + (uint32_t)offsetof(F33CurrentReferenceFeedbackCalibration, ratio_upper)))));
  if (iVar3 - iVar4 < 0 != (iVar3 < 0 != iVar4 < 0 && iVar4 < 0 == iVar3 - iVar4 < 0)) {
    iVar4 = iVar3;
  }
  if (iVar4 < 0) {
    iVar4 = 0;
  }
  (*((volatile int16_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe6b50u + (uint32_t)(1) * (uint32_t)sizeof(F33CurrentReferenceFeedbackState)) + (uint32_t)(0) * (uint32_t)sizeof(F33CurrentReferenceFeedbackState) + (uint32_t)offsetof(F33CurrentReferenceFeedbackState, ratio))))) = (short)iVar4;
  iVar5 = (int)(*((volatile int16_t *)camry_host_ptr((uint32_t)((uint32_t)(0x31950u + (uint32_t)(1) * (uint32_t)sizeof(F33CurrentReferenceFeedbackCalibration)) + (uint32_t)(0) * (uint32_t)sizeof(F33CurrentReferenceFeedbackCalibration) + (uint32_t)offsetof(F33CurrentReferenceFeedbackCalibration, ratio_target))))) - (int)(short)iVar4;
  if (iVar3 - iVar5 < 0 != (iVar3 < 0 != iVar5 < 0 && iVar5 < 0 == iVar3 - iVar5 < 0)) {
    iVar5 = iVar3;
  }
  (*((volatile int32_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe6b50u + (uint32_t)(1) * (uint32_t)sizeof(F33CurrentReferenceFeedbackState)) + (uint32_t)(0) * (uint32_t)sizeof(F33CurrentReferenceFeedbackState) + (uint32_t)offsetof(F33CurrentReferenceFeedbackState, error))))) =
       (int)(*((volatile int16_t *)camry_host_ptr((uint32_t)((uint32_t)(0x31950u + (uint32_t)(1) * (uint32_t)sizeof(F33CurrentReferenceFeedbackCalibration)) + (uint32_t)(0) * (uint32_t)sizeof(F33CurrentReferenceFeedbackCalibration) + (uint32_t)offsetof(F33CurrentReferenceFeedbackCalibration, error_lower)))));
  if (iVar5 - (*((volatile int32_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe6b50u + (uint32_t)(1) * (uint32_t)sizeof(F33CurrentReferenceFeedbackState)) + (uint32_t)(0) * (uint32_t)sizeof(F33CurrentReferenceFeedbackState) + (uint32_t)offsetof(F33CurrentReferenceFeedbackState, error))))) < 0 ==
      (iVar5 < 0 != (*((volatile int32_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe6b50u + (uint32_t)(1) * (uint32_t)sizeof(F33CurrentReferenceFeedbackState)) + (uint32_t)(0) * (uint32_t)sizeof(F33CurrentReferenceFeedbackState) + (uint32_t)offsetof(F33CurrentReferenceFeedbackState, error))))) < 0 &&
      (*((volatile int32_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe6b50u + (uint32_t)(1) * (uint32_t)sizeof(F33CurrentReferenceFeedbackState)) + (uint32_t)(0) * (uint32_t)sizeof(F33CurrentReferenceFeedbackState) + (uint32_t)offsetof(F33CurrentReferenceFeedbackState, error))))) < 0 ==
      iVar5 - (*((volatile int32_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe6b50u + (uint32_t)(1) * (uint32_t)sizeof(F33CurrentReferenceFeedbackState)) + (uint32_t)(0) * (uint32_t)sizeof(F33CurrentReferenceFeedbackState) + (uint32_t)offsetof(F33CurrentReferenceFeedbackState, error))))) < 0)) {
    (*((volatile int32_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe6b50u + (uint32_t)(1) * (uint32_t)sizeof(F33CurrentReferenceFeedbackState)) + (uint32_t)(0) * (uint32_t)sizeof(F33CurrentReferenceFeedbackState) + (uint32_t)offsetof(F33CurrentReferenceFeedbackState, error))))) = iVar5;
  }
  if ((DAT_febe71ec & 3) != 0) {
    (*((volatile int32_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe6b50u + (uint32_t)(1) * (uint32_t)sizeof(F33CurrentReferenceFeedbackState)) + (uint32_t)(0) * (uint32_t)sizeof(F33CurrentReferenceFeedbackState) + (uint32_t)offsetof(F33CurrentReferenceFeedbackState, error))))) = (*((volatile int32_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe6b50u + (uint32_t)(1) * (uint32_t)sizeof(F33CurrentReferenceFeedbackState)) + (uint32_t)(0) * (uint32_t)sizeof(F33CurrentReferenceFeedbackState) + (uint32_t)offsetof(F33CurrentReferenceFeedbackState, error))))) / 2;
  }
  sVar1 = (*((volatile int16_t *)camry_host_ptr((uint32_t)((uint32_t)(0x31950u + (uint32_t)(1) * (uint32_t)sizeof(F33CurrentReferenceFeedbackCalibration)) + (uint32_t)(0) * (uint32_t)sizeof(F33CurrentReferenceFeedbackCalibration) + (uint32_t)offsetof(F33CurrentReferenceFeedbackCalibration, normal_current_gain)))));
  sVar2 = (*((volatile int16_t *)camry_host_ptr((uint32_t)((uint32_t)(0x31950u + (uint32_t)(1) * (uint32_t)sizeof(F33CurrentReferenceFeedbackCalibration)) + (uint32_t)(0) * (uint32_t)sizeof(F33CurrentReferenceFeedbackCalibration) + (uint32_t)offsetof(F33CurrentReferenceFeedbackCalibration, normal_previous_gain)))));
  if (current_reference_transient.active == 'Z') {
    sVar1 = (*((volatile int16_t *)camry_host_ptr((uint32_t)((uint32_t)(0x31950u + (uint32_t)(1) * (uint32_t)sizeof(F33CurrentReferenceFeedbackCalibration)) + (uint32_t)(0) * (uint32_t)sizeof(F33CurrentReferenceFeedbackCalibration) + (uint32_t)offsetof(F33CurrentReferenceFeedbackCalibration, transient_current_gain)))));
    sVar2 = (*((volatile int16_t *)camry_host_ptr((uint32_t)((uint32_t)(0x31950u + (uint32_t)(1) * (uint32_t)sizeof(F33CurrentReferenceFeedbackCalibration)) + (uint32_t)(0) * (uint32_t)sizeof(F33CurrentReferenceFeedbackCalibration) + (uint32_t)offsetof(F33CurrentReferenceFeedbackCalibration, transient_previous_gain)))));
  }
  (*((volatile int32_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe6b50u + (uint32_t)(1) * (uint32_t)sizeof(F33CurrentReferenceFeedbackState)) + (uint32_t)(0) * (uint32_t)sizeof(F33CurrentReferenceFeedbackState) + (uint32_t)offsetof(F33CurrentReferenceFeedbackState, previous_gain))))) = (int)sVar2;
  (*((volatile int32_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe6b50u + (uint32_t)(1) * (uint32_t)sizeof(F33CurrentReferenceFeedbackState)) + (uint32_t)(0) * (uint32_t)sizeof(F33CurrentReferenceFeedbackState) + (uint32_t)offsetof(F33CurrentReferenceFeedbackState, current_gain))))) = (int)sVar1;
  if ((*((volatile uint8_t *)camry_host_ptr((uint32_t)((uint32_t)(0x31950u + (uint32_t)(1) * (uint32_t)sizeof(F33CurrentReferenceFeedbackCalibration)) + (uint32_t)(0) * (uint32_t)sizeof(F33CurrentReferenceFeedbackCalibration) + (uint32_t)offsetof(F33CurrentReferenceFeedbackCalibration, error_gain_scaling_enabled))))) == 'Z') {
    iVar3 = (*((volatile int32_t *)camry_host_ptr((uint32_t)((uint32_t)(0x31950u + (uint32_t)(1) * (uint32_t)sizeof(F33CurrentReferenceFeedbackCalibration)) + (uint32_t)(0) * (uint32_t)sizeof(F33CurrentReferenceFeedbackCalibration) + (uint32_t)offsetof(F33CurrentReferenceFeedbackCalibration, nonpositive_error_gain_scale)))));
    if (0 < (*((volatile int32_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe6b50u + (uint32_t)(1) * (uint32_t)sizeof(F33CurrentReferenceFeedbackState)) + (uint32_t)(0) * (uint32_t)sizeof(F33CurrentReferenceFeedbackState) + (uint32_t)offsetof(F33CurrentReferenceFeedbackState, error)))))) {
      iVar3 = (*((volatile int32_t *)camry_host_ptr((uint32_t)((uint32_t)(0x31950u + (uint32_t)(1) * (uint32_t)sizeof(F33CurrentReferenceFeedbackCalibration)) + (uint32_t)(0) * (uint32_t)sizeof(F33CurrentReferenceFeedbackCalibration) + (uint32_t)offsetof(F33CurrentReferenceFeedbackCalibration, positive_error_gain_scale)))));
    }
    iVar3 = ((*((volatile int32_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe6b50u + (uint32_t)(1) * (uint32_t)sizeof(F33CurrentReferenceFeedbackState)) + (uint32_t)(0) * (uint32_t)sizeof(F33CurrentReferenceFeedbackState) + (uint32_t)offsetof(F33CurrentReferenceFeedbackState, error))))) * iVar3) / 0x1000;
    (*((volatile int32_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe6b50u + (uint32_t)(1) * (uint32_t)sizeof(F33CurrentReferenceFeedbackState)) + (uint32_t)(0) * (uint32_t)sizeof(F33CurrentReferenceFeedbackState) + (uint32_t)offsetof(F33CurrentReferenceFeedbackState, current_gain))))) =
         ((*((volatile int32_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe6b50u + (uint32_t)(1) * (uint32_t)sizeof(F33CurrentReferenceFeedbackState)) + (uint32_t)(0) * (uint32_t)sizeof(F33CurrentReferenceFeedbackState) + (uint32_t)offsetof(F33CurrentReferenceFeedbackState, current_gain))))) * iVar3) / 0x1000;
    (*((volatile int32_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe6b50u + (uint32_t)(1) * (uint32_t)sizeof(F33CurrentReferenceFeedbackState)) + (uint32_t)(0) * (uint32_t)sizeof(F33CurrentReferenceFeedbackState) + (uint32_t)offsetof(F33CurrentReferenceFeedbackState, previous_gain))))) =
         ((*((volatile int32_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe6b50u + (uint32_t)(1) * (uint32_t)sizeof(F33CurrentReferenceFeedbackState)) + (uint32_t)(0) * (uint32_t)sizeof(F33CurrentReferenceFeedbackState) + (uint32_t)offsetof(F33CurrentReferenceFeedbackState, previous_gain))))) * iVar3) / 0x1000;
  }
  iVar6 = (int)first_current_feedback_baseline;
  iVar5 = iVar6 * 0x8000;
  iVar3 = (*((volatile int32_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe6b50u + (uint32_t)(1) * (uint32_t)sizeof(F33CurrentReferenceFeedbackState)) + (uint32_t)(0) * (uint32_t)sizeof(F33CurrentReferenceFeedbackState) + (uint32_t)offsetof(F33CurrentReferenceFeedbackState, current_gain))))) * (*((volatile int32_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe6b50u + (uint32_t)(1) * (uint32_t)sizeof(F33CurrentReferenceFeedbackState)) + (uint32_t)(0) * (uint32_t)sizeof(F33CurrentReferenceFeedbackState) + (uint32_t)offsetof(F33CurrentReferenceFeedbackState, error))))) -
          (*((volatile int32_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe6b50u + (uint32_t)(1) * (uint32_t)sizeof(F33CurrentReferenceFeedbackState)) + (uint32_t)(0) * (uint32_t)sizeof(F33CurrentReferenceFeedbackState) + (uint32_t)offsetof(F33CurrentReferenceFeedbackState, previous_gain))))) *
          (*((volatile int16_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe6b50u + (uint32_t)(1) * (uint32_t)sizeof(F33CurrentReferenceFeedbackState)) + (uint32_t)(0) * (uint32_t)sizeof(F33CurrentReferenceFeedbackState) + (uint32_t)offsetof(F33CurrentReferenceFeedbackState, previous_error)))));
  if (iVar5 < 1) {
    if ((iVar3 < 1) &&
       (iVar4 = iVar6 * -0x8000 + -0x7fffffff,
       iVar4 - iVar3 < 0 == (iVar4 < 0 != iVar3 < 0 && iVar3 < 0 == iVar4 - iVar3 < 0) &&
       iVar4 != iVar3)) {
      iVar3 = -0x7fffffff;
      goto LAB_0003662c;
    }
  }
  else if ((0 < iVar3) &&
          (iVar7 = iVar6 * -0x8000 + 0x7fffffff, iVar4 = iVar7 - iVar3,
          iVar4 < 0 != (iVar7 < 0 != iVar3 < 0 && iVar3 < 0 == iVar4 < 0))) {
    iVar3 = 0x7fffffff;
    goto LAB_0003662c;
  }
  iVar3 = iVar3 + iVar5;
LAB_0003662c:
  (*((volatile int32_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe6b50u + (uint32_t)(1) * (uint32_t)sizeof(F33CurrentReferenceFeedbackState)) + (uint32_t)(0) * (uint32_t)sizeof(F33CurrentReferenceFeedbackState) + (uint32_t)offsetof(F33CurrentReferenceFeedbackState, saturated_base_plus_delta))))) = iVar3;
  if (current_reference_transient.active == 'Z') {
    iVar3 = iVar3 + iVar6 * -0x8000;
    if ((*((volatile int32_t *)camry_host_ptr((uint32_t)((uint32_t)(0x31950u + (uint32_t)(1) * (uint32_t)sizeof(F33CurrentReferenceFeedbackCalibration)) + (uint32_t)(0) * (uint32_t)sizeof(F33CurrentReferenceFeedbackCalibration) + (uint32_t)offsetof(F33CurrentReferenceFeedbackCalibration, transient_delta_upper))))) - iVar3 < 0 !=
        ((*((volatile int32_t *)camry_host_ptr((uint32_t)((uint32_t)(0x31950u + (uint32_t)(1) * (uint32_t)sizeof(F33CurrentReferenceFeedbackCalibration)) + (uint32_t)(0) * (uint32_t)sizeof(F33CurrentReferenceFeedbackCalibration) + (uint32_t)offsetof(F33CurrentReferenceFeedbackCalibration, transient_delta_upper))))) < 0 != iVar3 < 0 &&
        iVar3 < 0 == (*((volatile int32_t *)camry_host_ptr((uint32_t)((uint32_t)(0x31950u + (uint32_t)(1) * (uint32_t)sizeof(F33CurrentReferenceFeedbackCalibration)) + (uint32_t)(0) * (uint32_t)sizeof(F33CurrentReferenceFeedbackCalibration) + (uint32_t)offsetof(F33CurrentReferenceFeedbackCalibration, transient_delta_upper))))) - iVar3 < 0
        )) {
      iVar3 = (*((volatile int32_t *)camry_host_ptr((uint32_t)((uint32_t)(0x31950u + (uint32_t)(1) * (uint32_t)sizeof(F33CurrentReferenceFeedbackCalibration)) + (uint32_t)(0) * (uint32_t)sizeof(F33CurrentReferenceFeedbackCalibration) + (uint32_t)offsetof(F33CurrentReferenceFeedbackCalibration, transient_delta_upper)))));
    }
    (*((volatile int32_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe6b50u + (uint32_t)(1) * (uint32_t)sizeof(F33CurrentReferenceFeedbackState)) + (uint32_t)(0) * (uint32_t)sizeof(F33CurrentReferenceFeedbackState) + (uint32_t)offsetof(F33CurrentReferenceFeedbackState, retained_transient_delta))))) =
         (*((volatile int32_t *)camry_host_ptr((uint32_t)((uint32_t)(0x31950u + (uint32_t)(1) * (uint32_t)sizeof(F33CurrentReferenceFeedbackCalibration)) + (uint32_t)(0) * (uint32_t)sizeof(F33CurrentReferenceFeedbackCalibration) + (uint32_t)offsetof(F33CurrentReferenceFeedbackCalibration, transient_delta_lower)))));
    if (iVar3 - (*((volatile int32_t *)camry_host_ptr((uint32_t)((uint32_t)(0x31950u + (uint32_t)(1) * (uint32_t)sizeof(F33CurrentReferenceFeedbackCalibration)) + (uint32_t)(0) * (uint32_t)sizeof(F33CurrentReferenceFeedbackCalibration) + (uint32_t)offsetof(F33CurrentReferenceFeedbackCalibration, transient_delta_lower))))) < 0 ==
        (iVar3 < 0 != (*((volatile int32_t *)camry_host_ptr((uint32_t)((uint32_t)(0x31950u + (uint32_t)(1) * (uint32_t)sizeof(F33CurrentReferenceFeedbackCalibration)) + (uint32_t)(0) * (uint32_t)sizeof(F33CurrentReferenceFeedbackCalibration) + (uint32_t)offsetof(F33CurrentReferenceFeedbackCalibration, transient_delta_lower))))) < 0 &&
        (*((volatile int32_t *)camry_host_ptr((uint32_t)((uint32_t)(0x31950u + (uint32_t)(1) * (uint32_t)sizeof(F33CurrentReferenceFeedbackCalibration)) + (uint32_t)(0) * (uint32_t)sizeof(F33CurrentReferenceFeedbackCalibration) + (uint32_t)offsetof(F33CurrentReferenceFeedbackCalibration, transient_delta_lower))))) < 0 ==
        iVar3 - (*((volatile int32_t *)camry_host_ptr((uint32_t)((uint32_t)(0x31950u + (uint32_t)(1) * (uint32_t)sizeof(F33CurrentReferenceFeedbackCalibration)) + (uint32_t)(0) * (uint32_t)sizeof(F33CurrentReferenceFeedbackCalibration) + (uint32_t)offsetof(F33CurrentReferenceFeedbackCalibration, transient_delta_lower))))) < 0)) {
      (*((volatile int32_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe6b50u + (uint32_t)(1) * (uint32_t)sizeof(F33CurrentReferenceFeedbackState)) + (uint32_t)(0) * (uint32_t)sizeof(F33CurrentReferenceFeedbackState) + (uint32_t)offsetof(F33CurrentReferenceFeedbackState, retained_transient_delta))))) = iVar3;
    }
    iVar3 = (*((volatile int32_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe6b50u + (uint32_t)(1) * (uint32_t)sizeof(F33CurrentReferenceFeedbackState)) + (uint32_t)(0) * (uint32_t)sizeof(F33CurrentReferenceFeedbackState) + (uint32_t)offsetof(F33CurrentReferenceFeedbackState, retained_transient_delta))))) + iVar5;
  }
  (*((volatile int32_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe6b50u + (uint32_t)(1) * (uint32_t)sizeof(F33CurrentReferenceFeedbackState)) + (uint32_t)(0) * (uint32_t)sizeof(F33CurrentReferenceFeedbackState) + (uint32_t)offsetof(F33CurrentReferenceFeedbackState, request_before_global_clamp))))) = iVar3;
  if ((*((volatile int32_t *)camry_host_ptr((uint32_t)((uint32_t)(0x31950u + (uint32_t)(1) * (uint32_t)sizeof(F33CurrentReferenceFeedbackCalibration)) + (uint32_t)(0) * (uint32_t)sizeof(F33CurrentReferenceFeedbackCalibration) + (uint32_t)offsetof(F33CurrentReferenceFeedbackCalibration, request_upper_q15))))) - iVar3 < 0 !=
      ((*((volatile int32_t *)camry_host_ptr((uint32_t)((uint32_t)(0x31950u + (uint32_t)(1) * (uint32_t)sizeof(F33CurrentReferenceFeedbackCalibration)) + (uint32_t)(0) * (uint32_t)sizeof(F33CurrentReferenceFeedbackCalibration) + (uint32_t)offsetof(F33CurrentReferenceFeedbackCalibration, request_upper_q15))))) < 0 != iVar3 < 0 &&
      iVar3 < 0 == (*((volatile int32_t *)camry_host_ptr((uint32_t)((uint32_t)(0x31950u + (uint32_t)(1) * (uint32_t)sizeof(F33CurrentReferenceFeedbackCalibration)) + (uint32_t)(0) * (uint32_t)sizeof(F33CurrentReferenceFeedbackCalibration) + (uint32_t)offsetof(F33CurrentReferenceFeedbackCalibration, request_upper_q15))))) - iVar3 < 0)) {
    iVar3 = (*((volatile int32_t *)camry_host_ptr((uint32_t)((uint32_t)(0x31950u + (uint32_t)(1) * (uint32_t)sizeof(F33CurrentReferenceFeedbackCalibration)) + (uint32_t)(0) * (uint32_t)sizeof(F33CurrentReferenceFeedbackCalibration) + (uint32_t)offsetof(F33CurrentReferenceFeedbackCalibration, request_upper_q15)))));
  }
  (*((volatile int16_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe6b50u + (uint32_t)(1) * (uint32_t)sizeof(F33CurrentReferenceFeedbackState)) + (uint32_t)(0) * (uint32_t)sizeof(F33CurrentReferenceFeedbackState) + (uint32_t)offsetof(F33CurrentReferenceFeedbackState, previous_error))))) = (short)(*((volatile int32_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe6b50u + (uint32_t)(1) * (uint32_t)sizeof(F33CurrentReferenceFeedbackState)) + (uint32_t)(0) * (uint32_t)sizeof(F33CurrentReferenceFeedbackState) + (uint32_t)offsetof(F33CurrentReferenceFeedbackState, error)))));
  iVar5 = (*((volatile int32_t *)camry_host_ptr((uint32_t)((uint32_t)(0x31950u + (uint32_t)(1) * (uint32_t)sizeof(F33CurrentReferenceFeedbackCalibration)) + (uint32_t)(0) * (uint32_t)sizeof(F33CurrentReferenceFeedbackCalibration) + (uint32_t)offsetof(F33CurrentReferenceFeedbackCalibration, request_lower_q15)))));
  if (iVar3 - (*((volatile int32_t *)camry_host_ptr((uint32_t)((uint32_t)(0x31950u + (uint32_t)(1) * (uint32_t)sizeof(F33CurrentReferenceFeedbackCalibration)) + (uint32_t)(0) * (uint32_t)sizeof(F33CurrentReferenceFeedbackCalibration) + (uint32_t)offsetof(F33CurrentReferenceFeedbackCalibration, request_lower_q15))))) < 0 ==
      (iVar3 < 0 != (*((volatile int32_t *)camry_host_ptr((uint32_t)((uint32_t)(0x31950u + (uint32_t)(1) * (uint32_t)sizeof(F33CurrentReferenceFeedbackCalibration)) + (uint32_t)(0) * (uint32_t)sizeof(F33CurrentReferenceFeedbackCalibration) + (uint32_t)offsetof(F33CurrentReferenceFeedbackCalibration, request_lower_q15))))) < 0 &&
      (*((volatile int32_t *)camry_host_ptr((uint32_t)((uint32_t)(0x31950u + (uint32_t)(1) * (uint32_t)sizeof(F33CurrentReferenceFeedbackCalibration)) + (uint32_t)(0) * (uint32_t)sizeof(F33CurrentReferenceFeedbackCalibration) + (uint32_t)offsetof(F33CurrentReferenceFeedbackCalibration, request_lower_q15))))) < 0 ==
      iVar3 - (*((volatile int32_t *)camry_host_ptr((uint32_t)((uint32_t)(0x31950u + (uint32_t)(1) * (uint32_t)sizeof(F33CurrentReferenceFeedbackCalibration)) + (uint32_t)(0) * (uint32_t)sizeof(F33CurrentReferenceFeedbackCalibration) + (uint32_t)offsetof(F33CurrentReferenceFeedbackCalibration, request_lower_q15))))) < 0)) {
    iVar5 = iVar3;
  }
  (*((volatile int16_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe6b50u + (uint32_t)(1) * (uint32_t)sizeof(F33CurrentReferenceFeedbackState)) + (uint32_t)(0) * (uint32_t)sizeof(F33CurrentReferenceFeedbackState) + (uint32_t)offsetof(F33CurrentReferenceFeedbackState, request))))) = (short)(iVar5 / 0x8000);
  return;
}

void return_only_stub_36674(void)

{
  return;
}

void return_only_stub_36676(void)

{
  return;
}

void refresh_phase_compensation_amplitude(void)

{
  int iVar1;
  int iVar2;
  uint uVar3;
  uint uVar4;
  uint uVar5;
  uint uVar6;
  uint uVar7;
  
  if (DAT_febe8a14 != '\x01') {
    return;
  }
  uVar6 = (uint)DAT_febe7db2;
  if ((DAT_000319aa < uVar6) || (uVar6 < DAT_000319ac)) {
    uVar3 = (uint)DAT_000319ba;
    uVar7 = uVar3;
  }
  else {
    uVar4 = (uint)DAT_000319b6;
    uVar3 = (uint)DAT_000319b8;
    uVar7 = (int)DAT_000319b2 + (int)(uVar6 * (int)DAT_000319ae) / 0x100;
    uVar5 = uVar4;
    if ((int)(uVar7 - uVar4) < 0 != ((int)uVar7 < 0 && -1 < (int)(uVar7 - uVar4))) {
      uVar5 = uVar7;
    }
    uVar7 = uVar3;
    if ((int)(uVar5 - uVar3) < 0 == ((int)uVar5 < 0 && -1 < (int)(uVar5 - uVar3))) {
      uVar7 = uVar5;
    }
    uVar6 = (int)DAT_000319b4 + (int)(uVar6 * (int)DAT_000319b0) / 0x100;
    if ((int)(uVar6 - uVar4) < 0 != ((int)uVar6 < 0 && -1 < (int)(uVar6 - uVar4))) {
      uVar4 = uVar6;
    }
    if ((int)(uVar4 - uVar3) < 0 == ((int)uVar4 < 0 && -1 < (int)(uVar4 - uVar3))) {
      uVar3 = uVar4;
    }
    uVar3 = uVar3 & 0xffff;
  }
  uVar6 = (uint)((int)(int16_t)DAT_febe7ea8);
  if ((int)((int)uVar6 + 0x7fff) < 0 == (-1 < (int)uVar6 && (int)((int)uVar6 + 0x7fff) < 0) &&
      uVar6 != 0xffff8001) {
    if ((int)uVar6 < 0) {
      uVar6 = (uint)-((int)(int16_t)DAT_febe7ea8);
    }
  }
  else {
    uVar6 = 0x7fff;
  }
  uVar4 = (uint)DAT_000319bc;
  uVar5 = (uint)DAT_000319be;
  if (DAT_febeeac6 < DAT_000319a8) {
    if ((int)(uVar6 - uVar4) < 0 == ((int)uVar6 < 0 && -1 < (int)(uVar6 - uVar4)) && uVar6 != uVar4)
    {
      uVar3 = (uint)DAT_000319c0;
      if ((int)(uVar6 - uVar5) < 0 == ((int)uVar6 < 0 && -1 < (int)(uVar6 - uVar5)) &&
          uVar6 != uVar5) goto LAB_00036736;
      iVar1 = uVar5 - uVar4;
      iVar2 = (uVar7 - DAT_000319c0) * (uVar6 - uVar4);
      if (iVar1 != 0) {
        if (iVar2 == -0x80000000 && iVar1 == -1) {
          iVar2 = 0;
        }
        else {
          iVar2 = (int)iVar2 / (int)iVar1;
        }
      }
      uVar7 = uVar7 - iVar2;
    }
    uVar3 = uVar7 & 0xffff;
  }
LAB_00036736:
  DAT_febe6b98 = (int)(uVar3 * DAT_febe6be4) / 0x400;
  return;
}

void return_only_stub_3674c(void)

{
  return;
}

void return_only_stub_3674e(void)

{
  return;
}

void compensate_first_regulated_phases(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  
  DAT_febe6ba4 = (int)((int)(int16_t)DAT_febe6e6c);
  DAT_febe6ba0 = (int)((int)(int16_t)DAT_febe6e6a);
  iVar4 = (int)DAT_000319c6;
  DAT_febe6b9c = (int)((int)(int16_t)DAT_febe6e68);
  DAT_febe6bbc = DAT_febe6ba4;
  DAT_febe6bb8 = DAT_febe6ba0;
  iVar2 = (int)((int)(int16_t)DAT_febe6e58);
  DAT_febe6bb4 = DAT_febe6b9c;
  iVar3 = (int)((int)(int16_t)DAT_febe6e5c);
  iVar5 = (int)((int)(int16_t)DAT_febe6e5a);
  iVar1 = -iVar4;
  if (iVar2 + iVar4 < 0 == (iVar2 < 0 != iVar1 < 0 && iVar1 < 0 == iVar2 + iVar4 < 0) &&
      iVar2 != iVar1) {
    DAT_febe6ba8 = DAT_febe6b98;
    if ((iVar2 - iVar4 < 0 != (iVar2 < 0 != iVar4 < 0 && iVar4 < 0 == iVar2 - iVar4 < 0)) &&
       (DAT_febe6ba8 = iVar2 * DAT_febe6b98, iVar4 != 0)) {
      if (DAT_febe6ba8 == -0x80000000 && iVar4 == -1) {
        DAT_febe6ba8 = -0x80000000;
      }
      else {
        DAT_febe6ba8 = (int)DAT_febe6ba8 / (int)iVar4;
      }
    }
  }
  else {
    DAT_febe6ba8 = -DAT_febe6b98;
  }
  if (iVar5 + iVar4 < 0 == (iVar5 < 0 != iVar1 < 0 && iVar1 < 0 == iVar5 + iVar4 < 0) &&
      iVar5 != iVar1) {
    DAT_febe6bac = DAT_febe6b98;
    if ((iVar5 - iVar4 < 0 != (iVar5 < 0 != iVar4 < 0 && iVar4 < 0 == iVar5 - iVar4 < 0)) &&
       (DAT_febe6bac = iVar5 * DAT_febe6b98, iVar4 != 0)) {
      if (DAT_febe6bac == -0x80000000 && iVar4 == -1) {
        DAT_febe6bac = -0x80000000;
      }
      else {
        DAT_febe6bac = (int)DAT_febe6bac / (int)iVar4;
      }
    }
  }
  else {
    DAT_febe6bac = -DAT_febe6b98;
  }
  if (iVar3 + iVar4 < 0 == (iVar3 < 0 != iVar1 < 0 && iVar1 < 0 == iVar3 + iVar4 < 0) &&
      iVar3 != iVar1) {
    DAT_febe6bb0 = DAT_febe6b98;
    if ((iVar3 - iVar4 < 0 != (iVar3 < 0 != iVar4 < 0 && iVar4 < 0 == iVar3 - iVar4 < 0)) &&
       (DAT_febe6bb0 = iVar3 * DAT_febe6b98, iVar4 != 0)) {
      if (DAT_febe6bb0 == -0x80000000 && iVar4 == -1) {
        DAT_febe6bb0 = -0x80000000;
      }
      else {
        DAT_febe6bb0 = (int)DAT_febe6bb0 / (int)iVar4;
      }
    }
  }
  else {
    DAT_febe6bb0 = -DAT_febe6b98;
  }
  if (((int8_t)DAT_febe6d5c) != -0x5b) {
    DAT_febe6b9c = DAT_febe6ba8 + DAT_febe6b9c;
    DAT_febe6ba0 = DAT_febe6bac + DAT_febe6ba0;
    DAT_febe6ba4 = DAT_febe6bb0 + DAT_febe6ba4;
  }
  return;
}

void return_only_stub_367fa(void)

{
  return;
}

void return_only_stub_367fc(void)

{
  return;
}

void compensate_second_regulated_phases(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  
  DAT_febe6bc8 = (int)((int)(int16_t)DAT_febe6e74);
  DAT_febe6bc4 = (int)((int)(int16_t)DAT_febe6e72);
  iVar4 = (int)DAT_000319ca;
  DAT_febe6bc0 = (int)((int)(int16_t)DAT_febe6e70);
  DAT_febe6be0 = DAT_febe6bc8;
  DAT_febe6bdc = DAT_febe6bc4;
  iVar2 = (int)((int)(int16_t)DAT_febe6e60);
  DAT_febe6bd8 = DAT_febe6bc0;
  iVar3 = (int)((int)(int16_t)DAT_febe6e64);
  iVar5 = (int)((int)(int16_t)DAT_febe6e62);
  iVar1 = -iVar4;
  if (iVar2 + iVar4 < 0 == (iVar2 < 0 != iVar1 < 0 && iVar1 < 0 == iVar2 + iVar4 < 0) &&
      iVar2 != iVar1) {
    DAT_febe6bcc = DAT_febe6b98;
    if ((iVar2 - iVar4 < 0 != (iVar2 < 0 != iVar4 < 0 && iVar4 < 0 == iVar2 - iVar4 < 0)) &&
       (DAT_febe6bcc = iVar2 * DAT_febe6b98, iVar4 != 0)) {
      if (DAT_febe6bcc == -0x80000000 && iVar4 == -1) {
        DAT_febe6bcc = -0x80000000;
      }
      else {
        DAT_febe6bcc = (int)DAT_febe6bcc / (int)iVar4;
      }
    }
  }
  else {
    DAT_febe6bcc = -DAT_febe6b98;
  }
  if (iVar5 + iVar4 < 0 == (iVar5 < 0 != iVar1 < 0 && iVar1 < 0 == iVar5 + iVar4 < 0) &&
      iVar5 != iVar1) {
    DAT_febe6bd0 = DAT_febe6b98;
    if ((iVar5 - iVar4 < 0 != (iVar5 < 0 != iVar4 < 0 && iVar4 < 0 == iVar5 - iVar4 < 0)) &&
       (DAT_febe6bd0 = iVar5 * DAT_febe6b98, iVar4 != 0)) {
      if (DAT_febe6bd0 == -0x80000000 && iVar4 == -1) {
        DAT_febe6bd0 = -0x80000000;
      }
      else {
        DAT_febe6bd0 = (int)DAT_febe6bd0 / (int)iVar4;
      }
    }
  }
  else {
    DAT_febe6bd0 = -DAT_febe6b98;
  }
  if (iVar3 + iVar4 < 0 == (iVar3 < 0 != iVar1 < 0 && iVar1 < 0 == iVar3 + iVar4 < 0) &&
      iVar3 != iVar1) {
    DAT_febe6bd4 = DAT_febe6b98;
    if ((iVar3 - iVar4 < 0 != (iVar3 < 0 != iVar4 < 0 && iVar4 < 0 == iVar3 - iVar4 < 0)) &&
       (DAT_febe6bd4 = iVar3 * DAT_febe6b98, iVar4 != 0)) {
      if (DAT_febe6bd4 == -0x80000000 && iVar4 == -1) {
        DAT_febe6bd4 = -0x80000000;
      }
      else {
        DAT_febe6bd4 = (int)DAT_febe6bd4 / (int)iVar4;
      }
    }
  }
  else {
    DAT_febe6bd4 = -DAT_febe6b98;
  }
  if (((int8_t)DAT_febe6d5d) != -0x5b) {
    DAT_febe6bc0 = DAT_febe6bcc + DAT_febe6bc0;
    DAT_febe6bc4 = DAT_febe6bd0 + DAT_febe6bc4;
    DAT_febe6bc8 = DAT_febe6bd4 + DAT_febe6bc8;
  }
  return;
}

void return_only_stub_368a8(void)

{
  return;
}

void clear_6be4_state_368aa(void)

{
  DAT_febe6be4 = 0;
  return;
}

void map_phase_compensation_gain(void)

{
  uint uVar1;
  uint uVar2;
  
  uVar1 = (uint)((int)(int16_t)DAT_febe6e0a);
  if ((int)((int)uVar1 + 0x7fff) < 0 == (-1 < (int)uVar1 && (int)((int)uVar1 + 0x7fff) < 0) &&
      uVar1 != 0xffff8001) {
    if ((int)uVar1 < 0) {
      uVar1 = -uVar1;
    }
  }
  else {
    uVar1 = 0x7fff;
  }
  uVar2 = (uVar1 & 0xffff) >> 4;
  if (uVar2 < 0x7f) {
    DAT_febe6be4 = (*((volatile uint16_t *)camry_host_ptr((uint32_t)((uint32_t)(0x2bd10u + (uint32_t)(uVar2) * (uint32_t)sizeof(F33CurvePointS16U16)) + (uint32_t)(0) * (uint32_t)sizeof(F33CurvePointS16U16) + (uint32_t)offsetof(F33CurvePointS16U16, y))))) +
                   (short)((int)((uVar1 & 0xf) *
                                ((uint)(*((volatile uint16_t *)camry_host_ptr((uint32_t)((uint32_t)(0x2bd10u + (uint32_t)(uVar2 + 1) * (uint32_t)sizeof(F33CurvePointS16U16)) + (uint32_t)(0) * (uint32_t)sizeof(F33CurvePointS16U16) + (uint32_t)offsetof(F33CurvePointS16U16, y))))) -
                                (uint)(*((volatile uint16_t *)camry_host_ptr((uint32_t)((uint32_t)(0x2bd10u + (uint32_t)(uVar2) * (uint32_t)sizeof(F33CurvePointS16U16)) + (uint32_t)(0) * (uint32_t)sizeof(F33CurvePointS16U16) + (uint32_t)offsetof(F33CurvePointS16U16, y))))))) / 0x10);
  }
  else {
    DAT_febe6be4 = 0x400;
  }
  return;
}

void return_only_stub_3690e(void)

{
  return;
}

void initialize_first_regulator_output_envelope_36910(void)

{
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe6be8u + (uint32_t)(0) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeState) + (uint32_t)offsetof(F33RegulatorOutputEnvelopeState, second_saturation))))) = '\0';
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe6be8u + (uint32_t)(0) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeState) + (uint32_t)offsetof(F33RegulatorOutputEnvelopeState, first_saturation))))) = '\0';
  (*((volatile int16_t *)camry_host_ptr((uint32_t)(0xfebe6be8u + (uint32_t)(0) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeState) + (uint32_t)offsetof(F33RegulatorOutputEnvelopeState, first))))) = 0;
  (*((volatile int16_t *)camry_host_ptr((uint32_t)(0xfebe6be8u + (uint32_t)(0) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeState) + (uint32_t)offsetof(F33RegulatorOutputEnvelopeState, second))))) = 0;
  (*((volatile int32_t *)camry_host_ptr((uint32_t)(0xfebe6be8u + (uint32_t)(0) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeState) + (uint32_t)offsetof(F33RegulatorOutputEnvelopeState, first_unclipped))))) = 0;
  (*((volatile int32_t *)camry_host_ptr((uint32_t)(0xfebe6be8u + (uint32_t)(0) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeState) + (uint32_t)offsetof(F33RegulatorOutputEnvelopeState, second_unclipped))))) = 0;
  (*((volatile int32_t *)camry_host_ptr((uint32_t)(0xfebe6be8u + (uint32_t)(0) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeState) + (uint32_t)offsetof(F33RegulatorOutputEnvelopeState, raw_cubic))))) = (*((volatile int32_t *)camry_host_ptr((uint32_t)(0x319e0u + (uint32_t)(0) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeCalibration) + (uint32_t)offsetof(F33RegulatorOutputEnvelopeCalibration, base)))));
  (*((volatile int16_t *)camry_host_ptr((uint32_t)(0xfebe6be8u + (uint32_t)(0) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeState) + (uint32_t)offsetof(F33RegulatorOutputEnvelopeState, selected_second_limit))))) =
       (short)((*((volatile int32_t *)camry_host_ptr((uint32_t)(0x319e0u + (uint32_t)(0) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeCalibration) + (uint32_t)offsetof(F33RegulatorOutputEnvelopeCalibration, base))))) / 0x800);
  (*((volatile int16_t *)camry_host_ptr((uint32_t)(0xfebe6be8u + (uint32_t)(0) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeState) + (uint32_t)offsetof(F33RegulatorOutputEnvelopeState, second_upper))))) =
       (*((volatile int16_t *)camry_host_ptr((uint32_t)(0xfebe6be8u + (uint32_t)(0) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeState) + (uint32_t)offsetof(F33RegulatorOutputEnvelopeState, selected_second_limit)))));
  (*((volatile int32_t *)camry_host_ptr((uint32_t)(0xfebe6be8u + (uint32_t)(0) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeState) + (uint32_t)offsetof(F33RegulatorOutputEnvelopeState, combined_second))))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe6be8u + (uint32_t)(0) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeState) + (uint32_t)offsetof(F33RegulatorOutputEnvelopeState, reset_cleared_status))))) = '\0';
  (*((volatile int32_t *)camry_host_ptr((uint32_t)(0xfebe6be8u + (uint32_t)(0) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeState) + (uint32_t)offsetof(F33RegulatorOutputEnvelopeState, lower_before_clamp))))) =
       (*((volatile int32_t *)camry_host_ptr((uint32_t)(0x319e0u + (uint32_t)(0) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeCalibration) + (uint32_t)offsetof(F33RegulatorOutputEnvelopeCalibration, base))))) -
       (*((volatile int32_t *)camry_host_ptr((uint32_t)(0x319e0u + (uint32_t)(0) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeCalibration) + (uint32_t)offsetof(F33RegulatorOutputEnvelopeCalibration, band_width)))));
  (*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xfebe6be8u + (uint32_t)(0) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeState) + (uint32_t)offsetof(F33RegulatorOutputEnvelopeState, retained_24))))) = 0x400;
  (*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xfebe6be8u + (uint32_t)(0) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeState) + (uint32_t)offsetof(F33RegulatorOutputEnvelopeState, retained_28))))) = 0x400;
  (*((volatile int16_t *)camry_host_ptr((uint32_t)(0xfebe6be8u + (uint32_t)(0) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeState) + (uint32_t)offsetof(F33RegulatorOutputEnvelopeState, second_lower))))) =
       (short)(((*((volatile int32_t *)camry_host_ptr((uint32_t)(0x319e0u + (uint32_t)(0) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeCalibration) + (uint32_t)offsetof(F33RegulatorOutputEnvelopeCalibration, base))))) -
               (*((volatile int32_t *)camry_host_ptr((uint32_t)(0x319e0u + (uint32_t)(0) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeCalibration) + (uint32_t)offsetof(F33RegulatorOutputEnvelopeCalibration, band_width)))))) / 0x800);
  return;
}

int regulator_output_envelope_cubic_bank0(void)

{
  int iVar1;
  int iVar2;
  
  iVar2 = (int)(*((volatile int16_t *)camry_host_ptr((uint32_t)(0xfebe6be8u + (uint32_t)(0) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeState) + (uint32_t)offsetof(F33RegulatorOutputEnvelopeState, first)))));
  if (iVar2 + 0x7fff < 0 == (-1 < iVar2 && iVar2 + 0x7fff < 0) && iVar2 != -0x7fff) {
    if (iVar2 < 0) {
      iVar2 = (int)-(*((volatile int16_t *)camry_host_ptr((uint32_t)(0xfebe6be8u + (uint32_t)(0) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeState) + (uint32_t)offsetof(F33RegulatorOutputEnvelopeState, first)))));
    }
  }
  else {
    iVar2 = 0x7fff;
  }
  iVar2 = (((int)(*((volatile int16_t *)camry_host_ptr((uint32_t)(0x319e0u + (uint32_t)(0) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeCalibration) + (uint32_t)offsetof(F33RegulatorOutputEnvelopeCalibration, linear_coefficient))))) +
           (((int)(*((volatile int16_t *)camry_host_ptr((uint32_t)(0x319e0u + (uint32_t)(0) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeCalibration) + (uint32_t)offsetof(F33RegulatorOutputEnvelopeCalibration, quadratic_coefficient))))) +
            ((int)(short)iVar2 *
            (int)(short)(*((volatile int8_t *)camry_host_ptr((uint32_t)(0x319e0u + (uint32_t)(0) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeCalibration) + (uint32_t)offsetof(F33RegulatorOutputEnvelopeCalibration, cubic_coefficient)))))) / 0x80) *
           iVar2) / 0x400) / 4) * iVar2;
  if (iVar2 < 1) {
    if (((*((volatile int32_t *)camry_host_ptr((uint32_t)(0x319e0u + (uint32_t)(0) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeCalibration) + (uint32_t)offsetof(F33RegulatorOutputEnvelopeCalibration, base))))) < 1) &&
       (iVar1 = -0x7fffffff - iVar2,
       iVar1 - (*((volatile int32_t *)camry_host_ptr((uint32_t)(0x319e0u + (uint32_t)(0) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeCalibration) + (uint32_t)offsetof(F33RegulatorOutputEnvelopeCalibration, base))))) < 0 ==
       (iVar1 < 0 != (*((volatile int32_t *)camry_host_ptr((uint32_t)(0x319e0u + (uint32_t)(0) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeCalibration) + (uint32_t)offsetof(F33RegulatorOutputEnvelopeCalibration, base))))) < 0 &&
       (*((volatile int32_t *)camry_host_ptr((uint32_t)(0x319e0u + (uint32_t)(0) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeCalibration) + (uint32_t)offsetof(F33RegulatorOutputEnvelopeCalibration, base))))) < 0 ==
       iVar1 - (*((volatile int32_t *)camry_host_ptr((uint32_t)(0x319e0u + (uint32_t)(0) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeCalibration) + (uint32_t)offsetof(F33RegulatorOutputEnvelopeCalibration, base))))) < 0) &&
       iVar1 != (*((volatile int32_t *)camry_host_ptr((uint32_t)(0x319e0u + (uint32_t)(0) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeCalibration) + (uint32_t)offsetof(F33RegulatorOutputEnvelopeCalibration, base))))))) {
      return -0x7fffffff;
    }
  }
  else if ((0 < (*((volatile int32_t *)camry_host_ptr((uint32_t)(0x319e0u + (uint32_t)(0) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeCalibration) + (uint32_t)offsetof(F33RegulatorOutputEnvelopeCalibration, base)))))) &&
          (iVar1 = (0x7fffffff - iVar2) - (*((volatile int32_t *)camry_host_ptr((uint32_t)(0x319e0u + (uint32_t)(0) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeCalibration) + (uint32_t)offsetof(F33RegulatorOutputEnvelopeCalibration, base))))),
          iVar1 < 0 !=
          (0x7fffffff - iVar2 < 0 != (*((volatile int32_t *)camry_host_ptr((uint32_t)(0x319e0u + (uint32_t)(0) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeCalibration) + (uint32_t)offsetof(F33RegulatorOutputEnvelopeCalibration, base))))) < 0 &&
          (*((volatile int32_t *)camry_host_ptr((uint32_t)(0x319e0u + (uint32_t)(0) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeCalibration) + (uint32_t)offsetof(F33RegulatorOutputEnvelopeCalibration, base))))) < 0 == iVar1 < 0))) {
    return 0x7fffffff;
  }
  return (*((volatile int32_t *)camry_host_ptr((uint32_t)(0x319e0u + (uint32_t)(0) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeCalibration) + (uint32_t)offsetof(F33RegulatorOutputEnvelopeCalibration, base))))) + iVar2;
}

void compose_regulator_output_bank0(void)

{
  short sVar1;
  uint32_t puVar3;
  int iVar4;
  uint uVar5;
  int iVar6;
  uint uVar7;
  int iVar8;
  int iVar9;
  int iVar10;
  undefined1 *puVar11;
  int iVar2;
  
  puVar3 = 0xfebeb800u;
  if ((DAT_febe8bae != '\0') || ((output_request_status & 0x40004) != 0)) {
    (*((volatile int16_t *)camry_host_ptr((uint32_t)(0xfebe6be8u + (uint32_t)(0) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeState) + (uint32_t)offsetof(F33RegulatorOutputEnvelopeState, selected_second_limit))))) =
         (short)((*((volatile int32_t *)camry_host_ptr((uint32_t)(0x319e0u + (uint32_t)(0) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeCalibration) + (uint32_t)offsetof(F33RegulatorOutputEnvelopeCalibration, base))))) / 0x800);
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe6be8u + (uint32_t)(0) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeState) + (uint32_t)offsetof(F33RegulatorOutputEnvelopeState, second_saturation))))) = '\0';
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe6be8u + (uint32_t)(0) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeState) + (uint32_t)offsetof(F33RegulatorOutputEnvelopeState, first_saturation))))) = '\0';
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe6be8u + (uint32_t)(0) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeState) + (uint32_t)offsetof(F33RegulatorOutputEnvelopeState, reset_cleared_status))))) = '\0';
    (*((volatile int16_t *)camry_host_ptr((uint32_t)(0xfebe6be8u + (uint32_t)(0) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeState) + (uint32_t)offsetof(F33RegulatorOutputEnvelopeState, first))))) = 0;
    (*((volatile int16_t *)camry_host_ptr((uint32_t)(0xfebe6be8u + (uint32_t)(0) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeState) + (uint32_t)offsetof(F33RegulatorOutputEnvelopeState, second))))) = 0;
    (*((volatile int16_t *)camry_host_ptr((uint32_t)(0xfebe6be8u + (uint32_t)(0) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeState) + (uint32_t)offsetof(F33RegulatorOutputEnvelopeState, second_lower))))) =
         (short)(((*((volatile int32_t *)camry_host_ptr((uint32_t)(0x319e0u + (uint32_t)(0) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeCalibration) + (uint32_t)offsetof(F33RegulatorOutputEnvelopeCalibration, base))))) -
                 (*((volatile int32_t *)camry_host_ptr((uint32_t)(0x319e0u + (uint32_t)(0) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeCalibration) + (uint32_t)offsetof(F33RegulatorOutputEnvelopeCalibration, band_width)))))) / 0x800);
    (*((volatile int16_t *)camry_host_ptr((uint32_t)(0xfebe6be8u + (uint32_t)(0) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeState) + (uint32_t)offsetof(F33RegulatorOutputEnvelopeState, second_upper))))) =
         (*((volatile int16_t *)camry_host_ptr((uint32_t)(0xfebe6be8u + (uint32_t)(0) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeState) + (uint32_t)offsetof(F33RegulatorOutputEnvelopeState, selected_second_limit)))));
    (*((volatile int32_t *)camry_host_ptr((uint32_t)(0xfebe6be8u + (uint32_t)(0) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeState) + (uint32_t)offsetof(F33RegulatorOutputEnvelopeState, first_unclipped))))) = 0;
    (*((volatile int32_t *)camry_host_ptr((uint32_t)(0xfebe6be8u + (uint32_t)(0) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeState) + (uint32_t)offsetof(F33RegulatorOutputEnvelopeState, second_unclipped))))) = 0;
    (*((volatile int32_t *)camry_host_ptr((uint32_t)(0xfebe6be8u + (uint32_t)(0) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeState) + (uint32_t)offsetof(F33RegulatorOutputEnvelopeState, raw_cubic))))) = (*((volatile int32_t *)camry_host_ptr((uint32_t)(0x319e0u + (uint32_t)(0) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeCalibration) + (uint32_t)offsetof(F33RegulatorOutputEnvelopeCalibration, base)))))
    ;
    (*((volatile int32_t *)camry_host_ptr((uint32_t)(0xfebe6be8u + (uint32_t)(0) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeState) + (uint32_t)offsetof(F33RegulatorOutputEnvelopeState, lower_before_clamp))))) =
         (*((volatile int32_t *)camry_host_ptr((uint32_t)(0x319e0u + (uint32_t)(0) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeCalibration) + (uint32_t)offsetof(F33RegulatorOutputEnvelopeCalibration, base))))) -
         (*((volatile int32_t *)camry_host_ptr((uint32_t)(0x319e0u + (uint32_t)(0) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeCalibration) + (uint32_t)offsetof(F33RegulatorOutputEnvelopeCalibration, band_width)))));
    (*((volatile int32_t *)camry_host_ptr((uint32_t)(0xfebe6be8u + (uint32_t)(0) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeState) + (uint32_t)offsetof(F33RegulatorOutputEnvelopeState, combined_second))))) = 0;
    (*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xfebe6be8u + (uint32_t)(0) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeState) + (uint32_t)offsetof(F33RegulatorOutputEnvelopeState, retained_24))))) = 0x400;
    (*((volatile uint32_t *)camry_host_ptr((uint32_t)(0xfebe6be8u + (uint32_t)(0) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeState) + (uint32_t)offsetof(F33RegulatorOutputEnvelopeState, retained_28))))) = 0x400;
    return;
  }
  iVar10 = DAT_febe6c8c;
  (*((volatile int32_t *)camry_host_ptr((uint32_t)(0xfebe6be8u + (uint32_t)(0) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeState) + (uint32_t)offsetof(F33RegulatorOutputEnvelopeState, combined_second))))) = DAT_febe6ccc;
  if ((DAT_febe71ec & 3) == 0) {
    iVar10 = (int)((DAT_febe6c78 + DAT_febe6c8c)) / (int)2;
    (*((volatile int32_t *)camry_host_ptr((uint32_t)(0xfebe6be8u + (uint32_t)(0) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeState) + (uint32_t)offsetof(F33RegulatorOutputEnvelopeState, combined_second))))) = (int)((DAT_febe6ca0 + DAT_febe6ccc)) / (int)2;
  }
  uVar5 = (uint)(*((volatile uint16_t *)camry_host_ptr((uint32_t)(0x319e0u + (uint32_t)(0) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeCalibration) + (uint32_t)offsetof(F33RegulatorOutputEnvelopeCalibration, scale_lower)))));
  iVar8 = (*((volatile uint16_t *)camry_host_ptr((uint32_t)(0x319e0u + (uint32_t)(0) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeCalibration) + (uint32_t)offsetof(F33RegulatorOutputEnvelopeCalibration, scale_upper))))) - ((int)(int32_t)DAT_febe6cf0);
  uVar7 = ((int)(int32_t)DAT_febe6cf0);
  if (iVar8 < 0 != ((int)DAT_febe6cf0 < 0 && (int)DAT_febe6cf0 < 0 == iVar8 < 0)) {
    uVar7 = (uint)(*((volatile uint16_t *)camry_host_ptr((uint32_t)(0x319e0u + (uint32_t)(0) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeCalibration) + (uint32_t)offsetof(F33RegulatorOutputEnvelopeCalibration, scale_upper)))));
  }
  if ((int)(uVar7 - uVar5) < 0 == ((int)uVar7 < 0 && -1 < (int)(uVar7 - uVar5))) {
    uVar5 = uVar7;
  }
  iVar10 = iVar10 / 0x100;
  if ((iVar10 == 0) || (uVar5 == 0)) {
    uVar7 = 0;
  }
  else {
    if (iVar10 < 0) {
      if (-1 < (int)uVar5) goto LAB_00036ad4;
    }
    else if ((int)uVar5 < 0) {
LAB_00036ad4:
      iVar8 = (int)((ulonglong)((longlong)(int)uVar5 * (longlong)iVar10) >> 0x20) + 1;
      if ((iVar8 < 0 != (-1 < (longlong)(int)uVar5 * (longlong)iVar10 && iVar8 < 0)) ||
         (uVar7 = iVar10 * uVar5, uVar7 < 0x80000001)) {
        uVar7 = 0x80000001;
      }
      goto LAB_00036aec;
    }
    if ((-1 < (longlong)(int)uVar5 * (longlong)iVar10 &&
         (int)((ulonglong)((longlong)(int)uVar5 * (longlong)iVar10) >> 0x20) != 0) ||
       (uVar7 = iVar10 * (int)uVar5, 0x7fffffff < (int)uVar7)) {
      uVar7 = 0x7fffffff;
    }
  }
LAB_00036aec:
  (*((volatile int32_t *)camry_host_ptr((uint32_t)(0xfebe6be8u + (uint32_t)(0) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeState) + (uint32_t)offsetof(F33RegulatorOutputEnvelopeState, first_unclipped))))) = (int)uVar7 / 0x800;
  iVar10 = (*((volatile int32_t *)camry_host_ptr((uint32_t)(0xfebe6be8u + (uint32_t)(0) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeState) + (uint32_t)offsetof(F33RegulatorOutputEnvelopeState, combined_second))))) / 0x100;
  if ((iVar10 == 0) || (uVar5 == 0)) {
    iVar10 = 0;
    goto LAB_00036b46;
  }
  if (iVar10 < 0) {
    if (-1 < (int)uVar5) goto LAB_00036b2a;
LAB_00036b14:
    if ((-1 < (longlong)(int)uVar5 * (longlong)iVar10 &&
         (int)((ulonglong)((longlong)(int)uVar5 * (longlong)iVar10) >> 0x20) != 0) ||
       (0x7fffffff < iVar10 * (int)uVar5)) {
      iVar10 = 0x7fffffff;
      goto LAB_00036b46;
    }
  }
  else {
    if (-1 < (int)uVar5) goto LAB_00036b14;
LAB_00036b2a:
    iVar8 = (int)((ulonglong)((longlong)(int)uVar5 * (longlong)iVar10) >> 0x20) + 1;
    if ((iVar8 < 0 != (-1 < (longlong)(int)uVar5 * (longlong)iVar10 && iVar8 < 0)) ||
       (iVar10 * uVar5 < 0x80000001)) {
      iVar10 = -0x7fffffff;
      goto LAB_00036b46;
    }
  }
  iVar10 = iVar10 * uVar5;
LAB_00036b46:
  iVar8 = (int)(*((volatile int16_t *)camry_host_ptr((uint32_t)(0x319e0u + (uint32_t)(0) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeCalibration) + (uint32_t)offsetof(F33RegulatorOutputEnvelopeCalibration, first_upper)))));
  iVar10 = iVar10 / 0x800;
  if (iVar8 - (*((volatile int32_t *)camry_host_ptr((uint32_t)(0xfebe6be8u + (uint32_t)(0) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeState) + (uint32_t)offsetof(F33RegulatorOutputEnvelopeState, first_unclipped))))) < 0 ==
      (iVar8 < 0 != (*((volatile int32_t *)camry_host_ptr((uint32_t)(0xfebe6be8u + (uint32_t)(0) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeState) + (uint32_t)offsetof(F33RegulatorOutputEnvelopeState, first_unclipped))))) < 0 &&
      (*((volatile int32_t *)camry_host_ptr((uint32_t)(0xfebe6be8u + (uint32_t)(0) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeState) + (uint32_t)offsetof(F33RegulatorOutputEnvelopeState, first_unclipped))))) < 0 ==
      iVar8 - (*((volatile int32_t *)camry_host_ptr((uint32_t)(0xfebe6be8u + (uint32_t)(0) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeState) + (uint32_t)offsetof(F33RegulatorOutputEnvelopeState, first_unclipped))))) < 0) &&
      iVar8 != (*((volatile int32_t *)camry_host_ptr((uint32_t)(0xfebe6be8u + (uint32_t)(0) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeState) + (uint32_t)offsetof(F33RegulatorOutputEnvelopeState, first_unclipped)))))) {
    (*((volatile int16_t *)camry_host_ptr((uint32_t)(0xfebe6be8u + (uint32_t)(0) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeState) + (uint32_t)offsetof(F33RegulatorOutputEnvelopeState, first))))) =
         (short)(*((volatile int32_t *)camry_host_ptr((uint32_t)(0xfebe6be8u + (uint32_t)(0) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeState) + (uint32_t)offsetof(F33RegulatorOutputEnvelopeState, first_unclipped)))));
    iVar8 = (*((volatile int16_t *)camry_host_ptr((uint32_t)(0x319e0u + (uint32_t)(0) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeCalibration) + (uint32_t)offsetof(F33RegulatorOutputEnvelopeCalibration, first_lower))))) -
            (*((volatile int32_t *)camry_host_ptr((uint32_t)(0xfebe6be8u + (uint32_t)(0) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeState) + (uint32_t)offsetof(F33RegulatorOutputEnvelopeState, first_unclipped)))));
    if (iVar8 < 0 ==
        ((*((volatile int16_t *)camry_host_ptr((uint32_t)(0x319e0u + (uint32_t)(0) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeCalibration) + (uint32_t)offsetof(F33RegulatorOutputEnvelopeCalibration, first_lower))))) < 0 !=
         (*((volatile int32_t *)camry_host_ptr((uint32_t)(0xfebe6be8u + (uint32_t)(0) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeState) + (uint32_t)offsetof(F33RegulatorOutputEnvelopeState, first_unclipped))))) < 0 &&
        (*((volatile int32_t *)camry_host_ptr((uint32_t)(0xfebe6be8u + (uint32_t)(0) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeState) + (uint32_t)offsetof(F33RegulatorOutputEnvelopeState, first_unclipped))))) < 0 == iVar8 < 0)) {
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe6be8u + (uint32_t)(0) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeState) + (uint32_t)offsetof(F33RegulatorOutputEnvelopeState, first_saturation))))) = '\x02';
      (*((volatile int16_t *)camry_host_ptr((uint32_t)(0xfebe6be8u + (uint32_t)(0) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeState) + (uint32_t)offsetof(F33RegulatorOutputEnvelopeState, first))))) =
           (*((volatile int16_t *)camry_host_ptr((uint32_t)(0x319e0u + (uint32_t)(0) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeCalibration) + (uint32_t)offsetof(F33RegulatorOutputEnvelopeCalibration, first_lower)))));
    }
    else {
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe6be8u + (uint32_t)(0) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeState) + (uint32_t)offsetof(F33RegulatorOutputEnvelopeState, first_saturation))))) = '\0';
    }
  }
  else {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe6be8u + (uint32_t)(0) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeState) + (uint32_t)offsetof(F33RegulatorOutputEnvelopeState, first_saturation))))) = '\x01';
    (*((volatile int16_t *)camry_host_ptr((uint32_t)(0xfebe6be8u + (uint32_t)(0) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeState) + (uint32_t)offsetof(F33RegulatorOutputEnvelopeState, first))))) =
         (*((volatile int16_t *)camry_host_ptr((uint32_t)(0x319e0u + (uint32_t)(0) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeCalibration) + (uint32_t)offsetof(F33RegulatorOutputEnvelopeCalibration, first_upper)))));
  }
  (*((volatile int32_t *)camry_host_ptr((uint32_t)(0xfebe6be8u + (uint32_t)(0) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeState) + (uint32_t)offsetof(F33RegulatorOutputEnvelopeState, second_unclipped))))) = iVar10;
  iVar4 = regulator_output_envelope_cubic_bank0();
  iVar9 = (*((volatile int32_t *)camry_host_ptr((uint32_t)(0x319e0u + (uint32_t)(0) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeCalibration) + (uint32_t)offsetof(F33RegulatorOutputEnvelopeCalibration, upper)))));
  iVar8 = (*((volatile int32_t *)camry_host_ptr((uint32_t)(0x319e0u + (uint32_t)(0) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeCalibration) + (uint32_t)offsetof(F33RegulatorOutputEnvelopeCalibration, lower)))));
  puVar11 = ((undefined *)camry_host_ptr((uint32_t)((0xffffb3e8u + (uint32_t)((int)puVar3)))));
  (*((int *)camry_host_ptr((uint32_t)((0xffffb400u + (uint32_t)((int)puVar3)))))) = iVar4;
  if (iVar9 - iVar4 < 0 != (iVar9 < 0 != iVar4 < 0 && iVar4 < 0 == iVar9 - iVar4 < 0)) {
    iVar4 = iVar9;
  }
  iVar9 = iVar8;
  if (iVar4 - iVar8 < 0 == (iVar4 < 0 != iVar8 < 0 && iVar8 < 0 == iVar4 - iVar8 < 0)) {
    iVar9 = iVar4;
  }
  iVar4 = iVar9 - (*((volatile int32_t *)camry_host_ptr((uint32_t)(0x319e0u + (uint32_t)(0) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeCalibration) + (uint32_t)offsetof(F33RegulatorOutputEnvelopeCalibration, band_width)))));
  (*((int *)camry_host_ptr((uint32_t)((0xffffb404u + (uint32_t)((int)puVar3)))))) = iVar4;
  if (iVar8 - iVar4 < 0 == (iVar8 < 0 != iVar4 < 0 && iVar4 < 0 == iVar8 - iVar4 < 0) &&
      iVar8 != iVar4) {
    iVar4 = iVar8;
  }
  iVar9 = iVar9 / 0x800;
  iVar4 = iVar4 / 0x800;
  iVar8 = (int)(*((short *)camry_host_ptr((uint32_t)((0xffffb3eeu + (uint32_t)((int)puVar3))))));
  (*((short *)camry_host_ptr((uint32_t)((0xffffb3f4u + (uint32_t)((int)puVar3)))))) = (short)iVar9;
  (*((short *)camry_host_ptr((uint32_t)((0xffffb3f2u + (uint32_t)((int)puVar3)))))) = (short)iVar4;
  if (iVar10 + 0x7fffffff < 0 == (-1 < iVar10 && iVar10 + 0x7fffffff < 0) && iVar10 != -0x7fffffff)
  {
    iVar6 = iVar10;
    if (iVar10 < 0) {
      iVar6 = -iVar10;
    }
  }
  else {
    iVar6 = 0x7fffffff;
  }
  if (iVar8 + 0x7fffffff < 0 == (-1 < iVar8 && iVar8 + 0x7fffffff < 0) && iVar8 != -0x7fffffff) {
    if (iVar8 < 0) {
      iVar8 = -iVar8;
    }
  }
  else {
    iVar8 = 0x7fffffff;
  }
  iVar2 = iVar4;
  if (((iVar6 - iVar4 < 0 == (iVar6 < 0 != iVar4 < 0 && iVar4 < 0 == iVar6 - iVar4 < 0)) &&
      (iVar2 = iVar9,
      iVar8 - iVar9 < 0 != (iVar8 < 0 != iVar9 < 0 && iVar9 < 0 == iVar8 - iVar9 < 0) ||
      iVar8 == iVar9)) &&
     (iVar2 = iVar4, iVar8 - iVar4 < 0 == (iVar8 < 0 != iVar4 < 0 && iVar4 < 0 == iVar8 - iVar4 < 0)
     )) {
    iVar2 = iVar8;
  }
  sVar1 = (short)iVar2;
  iVar8 = (int)sVar1;
  (*((short *)camry_host_ptr((uint32_t)((0xffffb3f0u + (uint32_t)((int)puVar3)))))) = sVar1;
  if (iVar10 - iVar8 < 0 == (iVar10 < 0 != iVar8 < 0 && iVar8 < 0 == iVar10 - iVar8 < 0)) {
    *puVar11 = 1;
    (*((short *)camry_host_ptr((uint32_t)((0xffffb3eeu + (uint32_t)((int)puVar3)))))) = sVar1;
  }
  else {
    iVar9 = -iVar8;
    if (iVar10 + iVar8 < 0 == (iVar10 < 0 != iVar9 < 0 && iVar9 < 0 == iVar10 + iVar8 < 0) &&
        iVar10 != iVar9) {
      *puVar11 = 0;
      (*((short *)camry_host_ptr((uint32_t)((0xffffb3eeu + (uint32_t)((int)puVar3)))))) = (short)iVar10;
    }
    else {
      *puVar11 = 2;
      (*((short *)camry_host_ptr((uint32_t)((0xffffb3eeu + (uint32_t)((int)puVar3)))))) = (short)iVar9;
    }
  }
  return;
}

void return_only_stub_36c1a(void)

{
  return;
}

void initialize_second_regulator_output_envelope_36c1c(void)

{
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe6be8u + (uint32_t)(1) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeState)) + (uint32_t)(0) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeState) + (uint32_t)offsetof(F33RegulatorOutputEnvelopeState, second_saturation))))) = '\0';
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe6be8u + (uint32_t)(1) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeState)) + (uint32_t)(0) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeState) + (uint32_t)offsetof(F33RegulatorOutputEnvelopeState, first_saturation))))) = '\0';
  (*((volatile int16_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe6be8u + (uint32_t)(1) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeState)) + (uint32_t)(0) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeState) + (uint32_t)offsetof(F33RegulatorOutputEnvelopeState, first))))) = 0;
  (*((volatile int16_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe6be8u + (uint32_t)(1) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeState)) + (uint32_t)(0) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeState) + (uint32_t)offsetof(F33RegulatorOutputEnvelopeState, second))))) = 0;
  (*((volatile int32_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe6be8u + (uint32_t)(1) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeState)) + (uint32_t)(0) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeState) + (uint32_t)offsetof(F33RegulatorOutputEnvelopeState, first_unclipped))))) = 0;
  (*((volatile int32_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe6be8u + (uint32_t)(1) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeState)) + (uint32_t)(0) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeState) + (uint32_t)offsetof(F33RegulatorOutputEnvelopeState, second_unclipped))))) = 0;
  (*((volatile int32_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe6be8u + (uint32_t)(1) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeState)) + (uint32_t)(0) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeState) + (uint32_t)offsetof(F33RegulatorOutputEnvelopeState, raw_cubic))))) = (*((volatile int32_t *)camry_host_ptr((uint32_t)((uint32_t)(0x319e0u + (uint32_t)(1) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeCalibration)) + (uint32_t)(0) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeCalibration) + (uint32_t)offsetof(F33RegulatorOutputEnvelopeCalibration, base)))));
  (*((volatile int16_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe6be8u + (uint32_t)(1) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeState)) + (uint32_t)(0) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeState) + (uint32_t)offsetof(F33RegulatorOutputEnvelopeState, selected_second_limit))))) =
       (short)((*((volatile int32_t *)camry_host_ptr((uint32_t)((uint32_t)(0x319e0u + (uint32_t)(1) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeCalibration)) + (uint32_t)(0) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeCalibration) + (uint32_t)offsetof(F33RegulatorOutputEnvelopeCalibration, base))))) / 0x800);
  (*((volatile int16_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe6be8u + (uint32_t)(1) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeState)) + (uint32_t)(0) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeState) + (uint32_t)offsetof(F33RegulatorOutputEnvelopeState, second_upper))))) =
       (*((volatile int16_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe6be8u + (uint32_t)(1) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeState)) + (uint32_t)(0) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeState) + (uint32_t)offsetof(F33RegulatorOutputEnvelopeState, selected_second_limit)))));
  (*((volatile int32_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe6be8u + (uint32_t)(1) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeState)) + (uint32_t)(0) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeState) + (uint32_t)offsetof(F33RegulatorOutputEnvelopeState, combined_second))))) = 0;
  (*((volatile uint8_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe6be8u + (uint32_t)(1) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeState)) + (uint32_t)(0) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeState) + (uint32_t)offsetof(F33RegulatorOutputEnvelopeState, reset_cleared_status))))) = '\0';
  (*((volatile int32_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe6be8u + (uint32_t)(1) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeState)) + (uint32_t)(0) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeState) + (uint32_t)offsetof(F33RegulatorOutputEnvelopeState, lower_before_clamp))))) =
       (*((volatile int32_t *)camry_host_ptr((uint32_t)((uint32_t)(0x319e0u + (uint32_t)(1) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeCalibration)) + (uint32_t)(0) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeCalibration) + (uint32_t)offsetof(F33RegulatorOutputEnvelopeCalibration, base))))) -
       (*((volatile int32_t *)camry_host_ptr((uint32_t)((uint32_t)(0x319e0u + (uint32_t)(1) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeCalibration)) + (uint32_t)(0) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeCalibration) + (uint32_t)offsetof(F33RegulatorOutputEnvelopeCalibration, band_width)))));
  (*((volatile uint32_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe6be8u + (uint32_t)(1) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeState)) + (uint32_t)(0) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeState) + (uint32_t)offsetof(F33RegulatorOutputEnvelopeState, retained_24))))) = 0x400;
  (*((volatile uint32_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe6be8u + (uint32_t)(1) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeState)) + (uint32_t)(0) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeState) + (uint32_t)offsetof(F33RegulatorOutputEnvelopeState, retained_28))))) = 0x400;
  (*((volatile int16_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe6be8u + (uint32_t)(1) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeState)) + (uint32_t)(0) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeState) + (uint32_t)offsetof(F33RegulatorOutputEnvelopeState, second_lower))))) =
       (short)(((*((volatile int32_t *)camry_host_ptr((uint32_t)((uint32_t)(0x319e0u + (uint32_t)(1) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeCalibration)) + (uint32_t)(0) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeCalibration) + (uint32_t)offsetof(F33RegulatorOutputEnvelopeCalibration, base))))) -
               (*((volatile int32_t *)camry_host_ptr((uint32_t)((uint32_t)(0x319e0u + (uint32_t)(1) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeCalibration)) + (uint32_t)(0) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeCalibration) + (uint32_t)offsetof(F33RegulatorOutputEnvelopeCalibration, band_width)))))) / 0x800);
  return;
}

int regulator_output_envelope_cubic_bank1(void)

{
  int iVar1;
  int iVar2;
  
  iVar2 = (int)(*((volatile int16_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe6be8u + (uint32_t)(1) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeState)) + (uint32_t)(0) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeState) + (uint32_t)offsetof(F33RegulatorOutputEnvelopeState, first)))));
  if (iVar2 + 0x7fff < 0 == (-1 < iVar2 && iVar2 + 0x7fff < 0) && iVar2 != -0x7fff) {
    if (iVar2 < 0) {
      iVar2 = (int)-(*((volatile int16_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe6be8u + (uint32_t)(1) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeState)) + (uint32_t)(0) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeState) + (uint32_t)offsetof(F33RegulatorOutputEnvelopeState, first)))));
    }
  }
  else {
    iVar2 = 0x7fff;
  }
  iVar2 = (((int)(*((volatile int16_t *)camry_host_ptr((uint32_t)((uint32_t)(0x319e0u + (uint32_t)(1) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeCalibration)) + (uint32_t)(0) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeCalibration) + (uint32_t)offsetof(F33RegulatorOutputEnvelopeCalibration, linear_coefficient))))) +
           (((int)(*((volatile int16_t *)camry_host_ptr((uint32_t)((uint32_t)(0x319e0u + (uint32_t)(1) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeCalibration)) + (uint32_t)(0) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeCalibration) + (uint32_t)offsetof(F33RegulatorOutputEnvelopeCalibration, quadratic_coefficient))))) +
            ((int)(short)iVar2 *
            (int)(short)(*((volatile int8_t *)camry_host_ptr((uint32_t)((uint32_t)(0x319e0u + (uint32_t)(1) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeCalibration)) + (uint32_t)(0) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeCalibration) + (uint32_t)offsetof(F33RegulatorOutputEnvelopeCalibration, cubic_coefficient)))))) / 0x80) *
           iVar2) / 0x400) / 4) * iVar2;
  if (iVar2 < 1) {
    if (((*((volatile int32_t *)camry_host_ptr((uint32_t)((uint32_t)(0x319e0u + (uint32_t)(1) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeCalibration)) + (uint32_t)(0) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeCalibration) + (uint32_t)offsetof(F33RegulatorOutputEnvelopeCalibration, base))))) < 1) &&
       (iVar1 = -0x7fffffff - iVar2,
       iVar1 - (*((volatile int32_t *)camry_host_ptr((uint32_t)((uint32_t)(0x319e0u + (uint32_t)(1) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeCalibration)) + (uint32_t)(0) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeCalibration) + (uint32_t)offsetof(F33RegulatorOutputEnvelopeCalibration, base))))) < 0 ==
       (iVar1 < 0 != (*((volatile int32_t *)camry_host_ptr((uint32_t)((uint32_t)(0x319e0u + (uint32_t)(1) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeCalibration)) + (uint32_t)(0) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeCalibration) + (uint32_t)offsetof(F33RegulatorOutputEnvelopeCalibration, base))))) < 0 &&
       (*((volatile int32_t *)camry_host_ptr((uint32_t)((uint32_t)(0x319e0u + (uint32_t)(1) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeCalibration)) + (uint32_t)(0) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeCalibration) + (uint32_t)offsetof(F33RegulatorOutputEnvelopeCalibration, base))))) < 0 ==
       iVar1 - (*((volatile int32_t *)camry_host_ptr((uint32_t)((uint32_t)(0x319e0u + (uint32_t)(1) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeCalibration)) + (uint32_t)(0) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeCalibration) + (uint32_t)offsetof(F33RegulatorOutputEnvelopeCalibration, base))))) < 0) &&
       iVar1 != (*((volatile int32_t *)camry_host_ptr((uint32_t)((uint32_t)(0x319e0u + (uint32_t)(1) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeCalibration)) + (uint32_t)(0) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeCalibration) + (uint32_t)offsetof(F33RegulatorOutputEnvelopeCalibration, base))))))) {
      return -0x7fffffff;
    }
  }
  else if ((0 < (*((volatile int32_t *)camry_host_ptr((uint32_t)((uint32_t)(0x319e0u + (uint32_t)(1) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeCalibration)) + (uint32_t)(0) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeCalibration) + (uint32_t)offsetof(F33RegulatorOutputEnvelopeCalibration, base)))))) &&
          (iVar1 = (0x7fffffff - iVar2) - (*((volatile int32_t *)camry_host_ptr((uint32_t)((uint32_t)(0x319e0u + (uint32_t)(1) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeCalibration)) + (uint32_t)(0) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeCalibration) + (uint32_t)offsetof(F33RegulatorOutputEnvelopeCalibration, base))))),
          iVar1 < 0 !=
          (0x7fffffff - iVar2 < 0 != (*((volatile int32_t *)camry_host_ptr((uint32_t)((uint32_t)(0x319e0u + (uint32_t)(1) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeCalibration)) + (uint32_t)(0) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeCalibration) + (uint32_t)offsetof(F33RegulatorOutputEnvelopeCalibration, base))))) < 0 &&
          (*((volatile int32_t *)camry_host_ptr((uint32_t)((uint32_t)(0x319e0u + (uint32_t)(1) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeCalibration)) + (uint32_t)(0) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeCalibration) + (uint32_t)offsetof(F33RegulatorOutputEnvelopeCalibration, base))))) < 0 == iVar1 < 0))) {
    return 0x7fffffff;
  }
  return (*((volatile int32_t *)camry_host_ptr((uint32_t)((uint32_t)(0x319e0u + (uint32_t)(1) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeCalibration)) + (uint32_t)(0) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeCalibration) + (uint32_t)offsetof(F33RegulatorOutputEnvelopeCalibration, base))))) + iVar2;
}

void compose_regulator_output_bank1(void)

{
  short sVar1;
  uint32_t puVar3;
  int iVar4;
  uint uVar5;
  int iVar6;
  uint uVar7;
  int iVar8;
  int iVar9;
  int iVar10;
  undefined1 *puVar11;
  int iVar2;
  
  puVar3 = 0xfebeb800u;
  if ((DAT_febe8baf != '\0') || ((output_request_status & 0x40004) != 0)) {
    (*((volatile int16_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe6be8u + (uint32_t)(1) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeState)) + (uint32_t)(0) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeState) + (uint32_t)offsetof(F33RegulatorOutputEnvelopeState, selected_second_limit))))) =
         (short)((*((volatile int32_t *)camry_host_ptr((uint32_t)((uint32_t)(0x319e0u + (uint32_t)(1) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeCalibration)) + (uint32_t)(0) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeCalibration) + (uint32_t)offsetof(F33RegulatorOutputEnvelopeCalibration, base))))) / 0x800);
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe6be8u + (uint32_t)(1) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeState)) + (uint32_t)(0) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeState) + (uint32_t)offsetof(F33RegulatorOutputEnvelopeState, second_saturation))))) = '\0';
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe6be8u + (uint32_t)(1) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeState)) + (uint32_t)(0) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeState) + (uint32_t)offsetof(F33RegulatorOutputEnvelopeState, first_saturation))))) = '\0';
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe6be8u + (uint32_t)(1) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeState)) + (uint32_t)(0) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeState) + (uint32_t)offsetof(F33RegulatorOutputEnvelopeState, reset_cleared_status))))) = '\0';
    (*((volatile int16_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe6be8u + (uint32_t)(1) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeState)) + (uint32_t)(0) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeState) + (uint32_t)offsetof(F33RegulatorOutputEnvelopeState, first))))) = 0;
    (*((volatile int16_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe6be8u + (uint32_t)(1) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeState)) + (uint32_t)(0) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeState) + (uint32_t)offsetof(F33RegulatorOutputEnvelopeState, second))))) = 0;
    (*((volatile int16_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe6be8u + (uint32_t)(1) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeState)) + (uint32_t)(0) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeState) + (uint32_t)offsetof(F33RegulatorOutputEnvelopeState, second_lower))))) =
         (short)(((*((volatile int32_t *)camry_host_ptr((uint32_t)((uint32_t)(0x319e0u + (uint32_t)(1) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeCalibration)) + (uint32_t)(0) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeCalibration) + (uint32_t)offsetof(F33RegulatorOutputEnvelopeCalibration, base))))) -
                 (*((volatile int32_t *)camry_host_ptr((uint32_t)((uint32_t)(0x319e0u + (uint32_t)(1) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeCalibration)) + (uint32_t)(0) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeCalibration) + (uint32_t)offsetof(F33RegulatorOutputEnvelopeCalibration, band_width)))))) / 0x800);
    (*((volatile int16_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe6be8u + (uint32_t)(1) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeState)) + (uint32_t)(0) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeState) + (uint32_t)offsetof(F33RegulatorOutputEnvelopeState, second_upper))))) =
         (*((volatile int16_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe6be8u + (uint32_t)(1) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeState)) + (uint32_t)(0) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeState) + (uint32_t)offsetof(F33RegulatorOutputEnvelopeState, selected_second_limit)))));
    (*((volatile int32_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe6be8u + (uint32_t)(1) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeState)) + (uint32_t)(0) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeState) + (uint32_t)offsetof(F33RegulatorOutputEnvelopeState, first_unclipped))))) = 0;
    (*((volatile int32_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe6be8u + (uint32_t)(1) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeState)) + (uint32_t)(0) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeState) + (uint32_t)offsetof(F33RegulatorOutputEnvelopeState, second_unclipped))))) = 0;
    (*((volatile int32_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe6be8u + (uint32_t)(1) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeState)) + (uint32_t)(0) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeState) + (uint32_t)offsetof(F33RegulatorOutputEnvelopeState, raw_cubic))))) = (*((volatile int32_t *)camry_host_ptr((uint32_t)((uint32_t)(0x319e0u + (uint32_t)(1) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeCalibration)) + (uint32_t)(0) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeCalibration) + (uint32_t)offsetof(F33RegulatorOutputEnvelopeCalibration, base)))))
    ;
    (*((volatile int32_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe6be8u + (uint32_t)(1) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeState)) + (uint32_t)(0) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeState) + (uint32_t)offsetof(F33RegulatorOutputEnvelopeState, lower_before_clamp))))) =
         (*((volatile int32_t *)camry_host_ptr((uint32_t)((uint32_t)(0x319e0u + (uint32_t)(1) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeCalibration)) + (uint32_t)(0) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeCalibration) + (uint32_t)offsetof(F33RegulatorOutputEnvelopeCalibration, base))))) -
         (*((volatile int32_t *)camry_host_ptr((uint32_t)((uint32_t)(0x319e0u + (uint32_t)(1) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeCalibration)) + (uint32_t)(0) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeCalibration) + (uint32_t)offsetof(F33RegulatorOutputEnvelopeCalibration, band_width)))));
    (*((volatile int32_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe6be8u + (uint32_t)(1) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeState)) + (uint32_t)(0) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeState) + (uint32_t)offsetof(F33RegulatorOutputEnvelopeState, combined_second))))) = 0;
    (*((volatile uint32_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe6be8u + (uint32_t)(1) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeState)) + (uint32_t)(0) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeState) + (uint32_t)offsetof(F33RegulatorOutputEnvelopeState, retained_24))))) = 0x400;
    (*((volatile uint32_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe6be8u + (uint32_t)(1) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeState)) + (uint32_t)(0) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeState) + (uint32_t)offsetof(F33RegulatorOutputEnvelopeState, retained_28))))) = 0x400;
    return;
  }
  (*((volatile int32_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe6be8u + (uint32_t)(1) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeState)) + (uint32_t)(0) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeState) + (uint32_t)offsetof(F33RegulatorOutputEnvelopeState, combined_second))))) = DAT_febe6ccc;
  iVar10 = DAT_febe6c8c;
  if ((DAT_febe71ec & 3) == 0) {
    (*((volatile int32_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe6be8u + (uint32_t)(1) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeState)) + (uint32_t)(0) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeState) + (uint32_t)offsetof(F33RegulatorOutputEnvelopeState, combined_second))))) = (int)((DAT_febe6ccc - DAT_febe6ca0)) / (int)2;
    iVar10 = (int)((DAT_febe6c8c - DAT_febe6c78)) / (int)2;
  }
  uVar5 = (uint)(*((volatile uint16_t *)camry_host_ptr((uint32_t)((uint32_t)(0x319e0u + (uint32_t)(1) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeCalibration)) + (uint32_t)(0) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeCalibration) + (uint32_t)offsetof(F33RegulatorOutputEnvelopeCalibration, scale_lower)))));
  iVar8 = (*((volatile uint16_t *)camry_host_ptr((uint32_t)((uint32_t)(0x319e0u + (uint32_t)(1) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeCalibration)) + (uint32_t)(0) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeCalibration) + (uint32_t)offsetof(F33RegulatorOutputEnvelopeCalibration, scale_upper))))) - ((int)(int32_t)DAT_febe6cf4);
  uVar7 = ((int)(int32_t)DAT_febe6cf4);
  if (iVar8 < 0 != ((int)DAT_febe6cf4 < 0 && (int)DAT_febe6cf4 < 0 == iVar8 < 0)) {
    uVar7 = (uint)(*((volatile uint16_t *)camry_host_ptr((uint32_t)((uint32_t)(0x319e0u + (uint32_t)(1) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeCalibration)) + (uint32_t)(0) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeCalibration) + (uint32_t)offsetof(F33RegulatorOutputEnvelopeCalibration, scale_upper)))));
  }
  if ((int)(uVar7 - uVar5) < 0 == ((int)uVar7 < 0 && -1 < (int)(uVar7 - uVar5))) {
    uVar5 = uVar7;
  }
  iVar10 = iVar10 / 0x100;
  if ((iVar10 == 0) || (uVar5 == 0)) {
    uVar7 = 0;
  }
  else {
    if (iVar10 < 0) {
      if (-1 < (int)uVar5) goto LAB_00036ddc;
    }
    else if ((int)uVar5 < 0) {
LAB_00036ddc:
      iVar8 = (int)((ulonglong)((longlong)(int)uVar5 * (longlong)iVar10) >> 0x20) + 1;
      if ((iVar8 < 0 != (-1 < (longlong)(int)uVar5 * (longlong)iVar10 && iVar8 < 0)) ||
         (uVar7 = iVar10 * uVar5, uVar7 < 0x80000001)) {
        uVar7 = 0x80000001;
      }
      goto LAB_00036df4;
    }
    if ((-1 < (longlong)(int)uVar5 * (longlong)iVar10 &&
         (int)((ulonglong)((longlong)(int)uVar5 * (longlong)iVar10) >> 0x20) != 0) ||
       (uVar7 = iVar10 * (int)uVar5, 0x7fffffff < (int)uVar7)) {
      uVar7 = 0x7fffffff;
    }
  }
LAB_00036df4:
  (*((volatile int32_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe6be8u + (uint32_t)(1) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeState)) + (uint32_t)(0) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeState) + (uint32_t)offsetof(F33RegulatorOutputEnvelopeState, first_unclipped))))) = (int)uVar7 / 0x800;
  iVar10 = (*((volatile int32_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe6be8u + (uint32_t)(1) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeState)) + (uint32_t)(0) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeState) + (uint32_t)offsetof(F33RegulatorOutputEnvelopeState, combined_second))))) / 0x100;
  if ((iVar10 == 0) || (uVar5 == 0)) {
    iVar10 = 0;
    goto LAB_00036e4e;
  }
  if (iVar10 < 0) {
    if (-1 < (int)uVar5) goto LAB_00036e32;
LAB_00036e1c:
    if ((-1 < (longlong)(int)uVar5 * (longlong)iVar10 &&
         (int)((ulonglong)((longlong)(int)uVar5 * (longlong)iVar10) >> 0x20) != 0) ||
       (0x7fffffff < iVar10 * (int)uVar5)) {
      iVar10 = 0x7fffffff;
      goto LAB_00036e4e;
    }
  }
  else {
    if (-1 < (int)uVar5) goto LAB_00036e1c;
LAB_00036e32:
    iVar8 = (int)((ulonglong)((longlong)(int)uVar5 * (longlong)iVar10) >> 0x20) + 1;
    if ((iVar8 < 0 != (-1 < (longlong)(int)uVar5 * (longlong)iVar10 && iVar8 < 0)) ||
       (iVar10 * uVar5 < 0x80000001)) {
      iVar10 = -0x7fffffff;
      goto LAB_00036e4e;
    }
  }
  iVar10 = iVar10 * uVar5;
LAB_00036e4e:
  iVar8 = (int)(*((volatile int16_t *)camry_host_ptr((uint32_t)((uint32_t)(0x319e0u + (uint32_t)(1) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeCalibration)) + (uint32_t)(0) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeCalibration) + (uint32_t)offsetof(F33RegulatorOutputEnvelopeCalibration, first_upper)))));
  iVar10 = iVar10 / 0x800;
  if (iVar8 - (*((volatile int32_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe6be8u + (uint32_t)(1) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeState)) + (uint32_t)(0) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeState) + (uint32_t)offsetof(F33RegulatorOutputEnvelopeState, first_unclipped))))) < 0 ==
      (iVar8 < 0 != (*((volatile int32_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe6be8u + (uint32_t)(1) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeState)) + (uint32_t)(0) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeState) + (uint32_t)offsetof(F33RegulatorOutputEnvelopeState, first_unclipped))))) < 0 &&
      (*((volatile int32_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe6be8u + (uint32_t)(1) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeState)) + (uint32_t)(0) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeState) + (uint32_t)offsetof(F33RegulatorOutputEnvelopeState, first_unclipped))))) < 0 ==
      iVar8 - (*((volatile int32_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe6be8u + (uint32_t)(1) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeState)) + (uint32_t)(0) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeState) + (uint32_t)offsetof(F33RegulatorOutputEnvelopeState, first_unclipped))))) < 0) &&
      iVar8 != (*((volatile int32_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe6be8u + (uint32_t)(1) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeState)) + (uint32_t)(0) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeState) + (uint32_t)offsetof(F33RegulatorOutputEnvelopeState, first_unclipped)))))) {
    (*((volatile int16_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe6be8u + (uint32_t)(1) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeState)) + (uint32_t)(0) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeState) + (uint32_t)offsetof(F33RegulatorOutputEnvelopeState, first))))) =
         (short)(*((volatile int32_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe6be8u + (uint32_t)(1) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeState)) + (uint32_t)(0) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeState) + (uint32_t)offsetof(F33RegulatorOutputEnvelopeState, first_unclipped)))));
    iVar8 = (*((volatile int16_t *)camry_host_ptr((uint32_t)((uint32_t)(0x319e0u + (uint32_t)(1) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeCalibration)) + (uint32_t)(0) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeCalibration) + (uint32_t)offsetof(F33RegulatorOutputEnvelopeCalibration, first_lower))))) -
            (*((volatile int32_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe6be8u + (uint32_t)(1) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeState)) + (uint32_t)(0) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeState) + (uint32_t)offsetof(F33RegulatorOutputEnvelopeState, first_unclipped)))));
    if (iVar8 < 0 ==
        ((*((volatile int16_t *)camry_host_ptr((uint32_t)((uint32_t)(0x319e0u + (uint32_t)(1) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeCalibration)) + (uint32_t)(0) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeCalibration) + (uint32_t)offsetof(F33RegulatorOutputEnvelopeCalibration, first_lower))))) < 0 !=
         (*((volatile int32_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe6be8u + (uint32_t)(1) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeState)) + (uint32_t)(0) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeState) + (uint32_t)offsetof(F33RegulatorOutputEnvelopeState, first_unclipped))))) < 0 &&
        (*((volatile int32_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe6be8u + (uint32_t)(1) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeState)) + (uint32_t)(0) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeState) + (uint32_t)offsetof(F33RegulatorOutputEnvelopeState, first_unclipped))))) < 0 == iVar8 < 0)) {
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe6be8u + (uint32_t)(1) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeState)) + (uint32_t)(0) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeState) + (uint32_t)offsetof(F33RegulatorOutputEnvelopeState, first_saturation))))) = '\x02';
      (*((volatile int16_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe6be8u + (uint32_t)(1) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeState)) + (uint32_t)(0) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeState) + (uint32_t)offsetof(F33RegulatorOutputEnvelopeState, first))))) =
           (*((volatile int16_t *)camry_host_ptr((uint32_t)((uint32_t)(0x319e0u + (uint32_t)(1) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeCalibration)) + (uint32_t)(0) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeCalibration) + (uint32_t)offsetof(F33RegulatorOutputEnvelopeCalibration, first_lower)))));
    }
    else {
      (*((volatile uint8_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe6be8u + (uint32_t)(1) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeState)) + (uint32_t)(0) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeState) + (uint32_t)offsetof(F33RegulatorOutputEnvelopeState, first_saturation))))) = '\0';
    }
  }
  else {
    (*((volatile uint8_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe6be8u + (uint32_t)(1) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeState)) + (uint32_t)(0) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeState) + (uint32_t)offsetof(F33RegulatorOutputEnvelopeState, first_saturation))))) = '\x01';
    (*((volatile int16_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe6be8u + (uint32_t)(1) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeState)) + (uint32_t)(0) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeState) + (uint32_t)offsetof(F33RegulatorOutputEnvelopeState, first))))) =
         (*((volatile int16_t *)camry_host_ptr((uint32_t)((uint32_t)(0x319e0u + (uint32_t)(1) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeCalibration)) + (uint32_t)(0) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeCalibration) + (uint32_t)offsetof(F33RegulatorOutputEnvelopeCalibration, first_upper)))));
  }
  (*((volatile int32_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe6be8u + (uint32_t)(1) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeState)) + (uint32_t)(0) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeState) + (uint32_t)offsetof(F33RegulatorOutputEnvelopeState, second_unclipped))))) = iVar10;
  iVar4 = regulator_output_envelope_cubic_bank1();
  iVar9 = (*((volatile int32_t *)camry_host_ptr((uint32_t)((uint32_t)(0x319e0u + (uint32_t)(1) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeCalibration)) + (uint32_t)(0) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeCalibration) + (uint32_t)offsetof(F33RegulatorOutputEnvelopeCalibration, upper)))));
  iVar8 = (*((volatile int32_t *)camry_host_ptr((uint32_t)((uint32_t)(0x319e0u + (uint32_t)(1) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeCalibration)) + (uint32_t)(0) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeCalibration) + (uint32_t)offsetof(F33RegulatorOutputEnvelopeCalibration, lower)))));
  puVar11 = ((undefined *)camry_host_ptr((uint32_t)((0xffffb414u + (uint32_t)((int)puVar3)))));
  (*((int *)camry_host_ptr((uint32_t)((0xffffb42cu + (uint32_t)((int)puVar3)))))) = iVar4;
  if (iVar9 - iVar4 < 0 != (iVar9 < 0 != iVar4 < 0 && iVar4 < 0 == iVar9 - iVar4 < 0)) {
    iVar4 = iVar9;
  }
  iVar9 = iVar8;
  if (iVar4 - iVar8 < 0 == (iVar4 < 0 != iVar8 < 0 && iVar8 < 0 == iVar4 - iVar8 < 0)) {
    iVar9 = iVar4;
  }
  iVar4 = iVar9 - (*((volatile int32_t *)camry_host_ptr((uint32_t)((uint32_t)(0x319e0u + (uint32_t)(1) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeCalibration)) + (uint32_t)(0) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeCalibration) + (uint32_t)offsetof(F33RegulatorOutputEnvelopeCalibration, band_width)))));
  (*((int *)camry_host_ptr((uint32_t)((0xffffb430u + (uint32_t)((int)puVar3)))))) = iVar4;
  if (iVar8 - iVar4 < 0 == (iVar8 < 0 != iVar4 < 0 && iVar4 < 0 == iVar8 - iVar4 < 0) &&
      iVar8 != iVar4) {
    iVar4 = iVar8;
  }
  iVar9 = iVar9 / 0x800;
  iVar4 = iVar4 / 0x800;
  iVar8 = (int)(*((short *)camry_host_ptr((uint32_t)((0xffffb41au + (uint32_t)((int)puVar3))))));
  (*((short *)camry_host_ptr((uint32_t)((0xffffb420u + (uint32_t)((int)puVar3)))))) = (short)iVar9;
  (*((short *)camry_host_ptr((uint32_t)((0xffffb41eu + (uint32_t)((int)puVar3)))))) = (short)iVar4;
  if (iVar10 + 0x7fffffff < 0 == (-1 < iVar10 && iVar10 + 0x7fffffff < 0) && iVar10 != -0x7fffffff)
  {
    iVar6 = iVar10;
    if (iVar10 < 0) {
      iVar6 = -iVar10;
    }
  }
  else {
    iVar6 = 0x7fffffff;
  }
  if (iVar8 + 0x7fffffff < 0 == (-1 < iVar8 && iVar8 + 0x7fffffff < 0) && iVar8 != -0x7fffffff) {
    if (iVar8 < 0) {
      iVar8 = -iVar8;
    }
  }
  else {
    iVar8 = 0x7fffffff;
  }
  iVar2 = iVar4;
  if (((iVar6 - iVar4 < 0 == (iVar6 < 0 != iVar4 < 0 && iVar4 < 0 == iVar6 - iVar4 < 0)) &&
      (iVar2 = iVar9,
      iVar8 - iVar9 < 0 != (iVar8 < 0 != iVar9 < 0 && iVar9 < 0 == iVar8 - iVar9 < 0) ||
      iVar8 == iVar9)) &&
     (iVar2 = iVar4, iVar8 - iVar4 < 0 == (iVar8 < 0 != iVar4 < 0 && iVar4 < 0 == iVar8 - iVar4 < 0)
     )) {
    iVar2 = iVar8;
  }
  sVar1 = (short)iVar2;
  iVar8 = (int)sVar1;
  (*((short *)camry_host_ptr((uint32_t)((0xffffb41cu + (uint32_t)((int)puVar3)))))) = sVar1;
  if (iVar10 - iVar8 < 0 == (iVar10 < 0 != iVar8 < 0 && iVar8 < 0 == iVar10 - iVar8 < 0)) {
    *puVar11 = 1;
    (*((short *)camry_host_ptr((uint32_t)((0xffffb41au + (uint32_t)((int)puVar3)))))) = sVar1;
  }
  else {
    iVar9 = -iVar8;
    if (iVar10 + iVar8 < 0 == (iVar10 < 0 != iVar9 < 0 && iVar9 < 0 == iVar10 + iVar8 < 0) &&
        iVar10 != iVar9) {
      *puVar11 = 0;
      (*((short *)camry_host_ptr((uint32_t)((0xffffb41au + (uint32_t)((int)puVar3)))))) = (short)iVar10;
    }
    else {
      *puVar11 = 2;
      (*((short *)camry_host_ptr((uint32_t)((0xffffb41au + (uint32_t)((int)puVar3)))))) = (short)iVar9;
    }
  }
  return;
}

void return_only_stub_36f22(void)

{
  return;
}

void return_only_stub_36f24(void)

{
  return;
}

void filter_weighted_envelope_sum_and_scale_four_outputs_36f26(void)

{
  bool bVar1;
  int iVar2;
  int iVar3;
  uint uVar4;
  int iVar5;
  
  DAT_febe6c4c = DAT_000319c4;
  DAT_febe6c4e = DAT_000319c8;
  DAT_febe6c54 = (((int)((int)(int16_t)DAT_febe6e12) * (int)(*((volatile int16_t *)camry_host_ptr((uint32_t)(0xfebe6be8u + (uint32_t)(0) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeState) + (uint32_t)offsetof(F33RegulatorOutputEnvelopeState, first))))) +
                  (int)((int)(int16_t)DAT_febe6e14) * (int)((int)(int16_t)DAT_febe6cec)) / 0x8000) * (uint)DAT_000319c4;
  DAT_febe6c58 = (((int)((int)(int16_t)DAT_febe6e16) * (int)(*((volatile int16_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe6be8u + (uint32_t)(1) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeState)) + (uint32_t)(0) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeState) + (uint32_t)offsetof(F33RegulatorOutputEnvelopeState, first))))) +
                  (int)((int)(int16_t)DAT_febe6e18) * (int)((int)(int16_t)DAT_febe6cee)) / 0x8000) * (uint)DAT_000319c8;
  DAT_febe6c68 = (int)(( (int)(DAT_febe6c58) / (int)2 + (int)(DAT_febe6c54) / (int)2)) / (int)0x3000;
  if (((int)(int32_t)(int)DAT_febe6c68) + -0x7fff < 0 == (((int)(int32_t)(int)DAT_febe6c68) < 0 && -1 < ((int)(int32_t)(int)DAT_febe6c68) + -0x7fff) &&
      ((int)(int32_t)DAT_febe6c68) != 0x7fff) {
    iVar5 = 0x7fff;
  }
  else {
    iVar5 = (int)(short)((int)(int32_t)DAT_febe6c68);
    if (((int)(int32_t)(int)DAT_febe6c68) + 0x7fff < 0 != (-1 < ((int)(int32_t)(int)DAT_febe6c68) && ((int)(int32_t)(int)DAT_febe6c68) + 0x7fff < 0)) {
      iVar5 = -0x7fff;
    }
  }
  uVar4 = (uint)DAT_00031a2c;
  if (uVar4 == 0) {
    iVar2 = (int)((int)(int16_t)DAT_febe6c4a) << 0x10;
    iVar3 = iVar5 << 0x10;
  }
  else {
    iVar2 = (int)((int)(int16_t)DAT_febe6c4a) * uVar4;
    iVar3 = iVar5 * uVar4;
  }
  DAT_febe6c6c = iVar3 + (DAT_febe6c6c - iVar2);
  DAT_febe6c48 = (short)iVar5;
  DAT_febe6c4a = (short)( (int)(DAT_febe6c6c) / (int)0x10000);
  iVar5 = (int)((int)(int16_t)DAT_febe6c4a);
  if (DAT_00031a20 == 'Z') {
    DAT_febe6c50 = DAT_00031a24;
    if ((DAT_febe71ec & 3) == 0) {
      DAT_febe6c50 = DAT_00031a22;
    }
    iVar2 = (int)DAT_00031a26;
    if ((iVar5 - iVar2 < 0 != (iVar5 < 0 != iVar2 < 0 && iVar2 < 0 == iVar5 - iVar2 < 0) ||
         iVar5 == iVar2) &&
       (((((int)(int32_t)DAT_febe6c60) + -0x80 < 0 != (((int)(int32_t)DAT_febe6c60) < 0 && -1 < ((int)(int32_t)DAT_febe6c60) + -0x80) ||
         (((iVar3 = (int)DAT_00031a28, iVar2 = (*((volatile int16_t *)camry_host_ptr((uint32_t)(0xfebe6b50u + (uint32_t)(0) * (uint32_t)sizeof(F33CurrentReferenceFeedbackState) + (uint32_t)offsetof(F33CurrentReferenceFeedbackState, ratio))))) - iVar3,
           iVar2 < 0 ==
           ((*((volatile int16_t *)camry_host_ptr((uint32_t)(0xfebe6b50u + (uint32_t)(0) * (uint32_t)sizeof(F33CurrentReferenceFeedbackState) + (uint32_t)offsetof(F33CurrentReferenceFeedbackState, ratio))))) < 0 != iVar3 < 0 && iVar3 < 0 == iVar2 < 0) ||
           (iVar2 = (*((volatile int16_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe6b50u + (uint32_t)(1) * (uint32_t)sizeof(F33CurrentReferenceFeedbackState)) + (uint32_t)(0) * (uint32_t)sizeof(F33CurrentReferenceFeedbackState) + (uint32_t)offsetof(F33CurrentReferenceFeedbackState, ratio))))) - iVar3,
           iVar2 < 0 ==
           ((*((volatile int16_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe6b50u + (uint32_t)(1) * (uint32_t)sizeof(F33CurrentReferenceFeedbackState)) + (uint32_t)(0) * (uint32_t)sizeof(F33CurrentReferenceFeedbackState) + (uint32_t)offsetof(F33CurrentReferenceFeedbackState, ratio))))) < 0 != iVar3 < 0 && iVar3 < 0 == iVar2 < 0))) &&
          ((DAT_00031a2a <= DAT_febe7da6 || (DAT_00031a2a <= DAT_febe7da8)))))) && (iVar5 != 0)))) {
      DAT_febe6c5c = (int)DAT_febe6c50 << 7;
      bVar1 = ((int)(int32_t)DAT_febe6c5c) < 0;
      if (iVar5 != 0) {
        if (((int)(int32_t)DAT_febe6c5c) == -0x80000000 && iVar5 == -1) {
          bVar1 = true;
          DAT_febe6c5c = -0x80000000;
        }
        else {
          DAT_febe6c5c = ((int)(int32_t)DAT_febe6c5c) / iVar5;
          bVar1 = ((int)(int32_t)DAT_febe6c5c) < 0;
        }
      }
      if (bVar1) {
        DAT_febe6c5c = -((int)(int32_t)DAT_febe6c5c);
      }
      if (((int)(int32_t)DAT_febe6c5c) + -0x80 < 0 != (((int)(int32_t)DAT_febe6c5c) < 0 && -1 < ((int)(int32_t)DAT_febe6c5c) + -0x80) ||
          ((int)(int32_t)DAT_febe6c5c) == 0x80) goto LAB_00037068;
    }
  }
  DAT_febe6c5c = 0x80;
LAB_00037068:
  uVar4 = (uint)DAT_00031a2e;
  if (uVar4 == 0) {
    iVar5 = (int)(short)((int)(int32_t)DAT_febe6c60) << 0x10;
    iVar2 = (int)(short)((int)(int32_t)DAT_febe6c5c) << 0x10;
  }
  else {
    iVar5 = (int)(short)((int)(int32_t)DAT_febe6c60) * uVar4;
    iVar2 = (int)(short)((int)(int32_t)DAT_febe6c5c) * uVar4;
  }
  DAT_febe6c64 = iVar2 + (DAT_febe6c64 - iVar5);
  DAT_febe6c60 = (int)(short)( (int)(DAT_febe6c64) / (int)0x10000);
  DAT_febe6c42 = (short)( (int)((((int)(int32_t)DAT_febe6c60) * ((int)(int16_t)DAT_febe6cec))) / (int)0x80);
  DAT_febe6c40 = (short)( (int)((((int)(int32_t)DAT_febe6c60) * (*((volatile int16_t *)camry_host_ptr((uint32_t)(0xfebe6be8u + (uint32_t)(0) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeState) + (uint32_t)offsetof(F33RegulatorOutputEnvelopeState, first))))))) / (int)0x80);
  DAT_febe6c46 = (short)( (int)((((int)(int32_t)DAT_febe6c60) * ((int)(int16_t)DAT_febe6cee))) / (int)0x80);
  DAT_febe6c44 = (short)( (int)((((int)(int32_t)DAT_febe6c60) * (*((volatile int16_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe6be8u + (uint32_t)(1) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeState)) + (uint32_t)(0) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeState) + (uint32_t)offsetof(F33RegulatorOutputEnvelopeState, first))))))) / (int)0x80);
  return;
}
