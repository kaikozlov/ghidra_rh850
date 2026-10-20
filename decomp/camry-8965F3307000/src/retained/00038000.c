#include "common.h"

uint select_feedback_bounded_first_current_request(void)

{
  short sVar1;
  uint32_t puVar2;
  uint uVar3;
  int iVar4;
  int iVar5;
  short sVar6;
  int iVar7;
  
  puVar2 = 0xfebeb800u;
  uVar3 = current_reference_curve_feedback_magnitude();
  update_current_reference_curve_floor((ushort)uVar3);
  sVar6 = (*((short *)camry_host_ptr((uint32_t)((0xffffb58cu + (uint32_t)((int)puVar2))))));
  iVar5 = (int)sVar6;
  if ((*((int *)camry_host_ptr((uint32_t)(puVar2 + 0x32d0)))) == 0x5aa5a55a) {
    iVar7 = 0;
    reset_bank0_current_reference_feedback();
  }
  else {
    iVar7 = (int)(*((short *)camry_host_ptr((uint32_t)((0xffffb61au + (uint32_t)((int)puVar2))))));
    iVar4 = (int)(*((short *)camry_host_ptr((uint32_t)((0xffffb61cu + (uint32_t)((int)puVar2))))));
    if (((*((ushort *)camry_host_ptr((uint32_t)((0xffffb9ecu + (uint32_t)((int)puVar2)))))) & 3) == 0) {
      if (iVar4 - iVar7 < 0 != (iVar4 < 0 != iVar7 < 0 && iVar7 < 0 == iVar4 - iVar7 < 0)) {
        iVar7 = iVar4;
      }
      goto LAB_00038130;
    }
    if (((*((ushort *)camry_host_ptr((uint32_t)((0xffffb9ecu + (uint32_t)((int)puVar2)))))) & 1) != 0) {
      reset_bank0_current_reference_feedback();
      iVar7 = iVar4;
      goto LAB_00038130;
    }
  }
  reset_bank1_current_reference_feedback();
LAB_00038130:
  sVar1 = current_reference_floor_calibration.forced_request;
  if (current_reference_floor_calibration.force_enabled == '\x01') {
    reset_bank0_current_reference_feedback();
    reset_bank1_current_reference_feedback();
    sVar6 = sVar1;
  }
  else {
    iVar4 = (int)current_reference_floor_calibration.request_upper;
    if (iVar4 - iVar7 < 0 != (iVar4 < 0 != iVar7 < 0 && iVar7 < 0 == iVar4 - iVar7 < 0)) {
      iVar7 = iVar4;
    }
    if (iVar7 - iVar5 < 0 == (iVar7 < 0 != iVar5 < 0 && iVar5 < 0 == iVar7 - iVar5 < 0)) {
      sVar6 = (short)iVar7;
    }
  }
  (*((short *)camry_host_ptr((uint32_t)((0xffffb58au + (uint32_t)((int)puVar2)))))) = sVar6;
  return uVar3;
}

void return_only_stub_3815e(void)

{
  return;
}

void return_only_stub_38160(void)

{
  return;
}

uint32_t calculate_sixfold_current_correction(void)

{
  uint32_t camry_r10_result;
  uint8_t stack_record_1e[30];
  ushort uVar1;
  undefined2 uVar2;
  uint uVar3;
  uint32_t puVar4;
  int iVar5;
  short sVar6;
  int iVar7;
  int iVar8;
  int iVar9;
  short sVar10;
  int iVar11;
  uint uVar12;
  uint uVar13;
  
  puVar4 = 0xfebeb800u;
  iVar5 = (int)((int)(int16_t)DAT_febe6dd6);
  iVar9 = (int)actual_first_current_command;
  uVar3 = (uint)((int)((int)(int16_t)DAT_febe6dd6) * (int)((int)(int16_t)DAT_febe6dd6) +
                (int)actual_first_current_command * (int)actual_first_current_command) >>
          0xd;
  if (0xffff < uVar3) {
    uVar3 = 0xffff;
  }
  uVar12 = (uVar3 & 0xffff) >> 8;
  DAT_febe6db2 = (undefined2)uVar3;
  if (uVar12 < 0xff) {
    DAT_febe6dbc = (uint)*(ushort *)(((undefined *)camry_host_ptr((uint32_t)(0x2cb26u + (uint32_t)(uVar12 * 4) * 1u)))) +
                   (int)((uVar3 & 0xff) *
                        ((uint)*(ushort *)(((undefined *)camry_host_ptr((uint32_t)(0x2cb26u + (uint32_t)((uVar12 + 1) * 4) * 1u)))) -
                        (uint)*(ushort *)(((undefined *)camry_host_ptr((uint32_t)(0x2cb26u + (uint32_t)(uVar12 * 4) * 1u)))))) / 0x100 & 0xffff;
  }
  else {
    DAT_febe6dbc = 0x400;
  }
  uVar3 = (uint)((int)(int16_t)DAT_febe5f36);
  if ((int)((int)uVar3 + 0x7fff) < 0 == (-1 < (int)uVar3 && (int)((int)uVar3 + 0x7fff) < 0) &&
      uVar3 != 0xffff8001) {
    uVar12 = uVar3;
    if ((int)uVar3 < 0) {
      uVar12 = -uVar3;
    }
  }
  else {
    uVar12 = 0x7fff;
  }
  uVar13 = (uVar12 & 0xffff) >> 1;
  if (uVar13 < 0xff) {
    DAT_febe6d9e = *(ushort *)(((undefined *)camry_host_ptr((uint32_t)(0x2c722u + (uint32_t)(uVar13 * 4) * 1u)))) +
                   (short)((int)((uVar12 & 1) *
                                ((uint)*(ushort *)(((undefined *)camry_host_ptr((uint32_t)(0x2c722u + (uint32_t)((uVar13 + 1) * 4) * 1u)))) -
                                (uint)*(ushort *)(((undefined *)camry_host_ptr((uint32_t)(0x2c722u + (uint32_t)(uVar13 * 4) * 1u)))))) / 2);
  }
  else {
    DAT_febe6d9e = 0;
  }
  sVar6 = -DAT_00031b84;
  iVar8 = (int)DAT_00031b84 - uVar3;
  iVar7 = (int)sVar6;
  sVar10 = ((int)(int16_t)DAT_febe5f36);
  if (iVar8 < 0 != (DAT_00031b84 < 0 != (int)uVar3 < 0 && (int)uVar3 < 0 == iVar8 < 0)) {
    sVar10 = DAT_00031b84;
  }
  iVar8 = sVar10 - iVar7;
  if (iVar8 < 0 == (sVar10 < 0 != iVar7 < 0 && iVar7 < 0 == iVar8 < 0)) {
    sVar6 = sVar10;
  }
  iVar8 = (int)DAT_00031b82;
  if (iVar5 + -0x7fff < 0 == (iVar5 < 0 && -1 < iVar5 + -0x7fff)) {
    iVar5 = 0x7fff;
  }
  if (iVar5 + 0x7fff < 0 != (-1 < iVar5 && iVar5 + 0x7fff < 0)) {
    iVar5 = -0x7fff;
  }
  if (iVar9 + -0x7fff < 0 == (iVar9 < 0 && -1 < iVar9 + -0x7fff)) {
    iVar9 = 0x7fff;
  }
  if (iVar9 + 0x7fff < 0 != (-1 < iVar9 && iVar9 + 0x7fff < 0)) {
    iVar9 = -0x7fff;
  }
  (camry_r10_result = compute_s16_atan2_turn_angle_70be0(iVar9,iVar5,stack_record_1e));
  iVar9 = (int)current_correction_phase_slope;
  iVar5 = (*((int *)camry_host_ptr((uint32_t)((0xffffb5bcu + (uint32_t)((int)puVar4))))));
  uVar1 = (*((ushort *)camry_host_ptr((uint32_t)((0xffffb59eu + (uint32_t)((int)puVar4))))));
  (*((ushort *)camry_host_ptr((uint32_t)((0xffffb5aeu + (uint32_t)((int)puVar4)))))) = (*((uint16_t *)(stack_record_1e + 0)));
  sVar10 = (*((short *)camry_host_ptr((uint32_t)(puVar4 + -0x3ab6))));
  iVar9 = (int)((uint)(*((uint16_t *)(stack_record_1e + 0))) * iVar9) / 0x400;
  (*((short *)camry_host_ptr((uint32_t)((0xffffb5b0u + (uint32_t)((int)puVar4)))))) = (short)iVar9;
  uVar3 = (iVar9 + (int)sVar10 + (sVar6 * iVar8 * 5) / 0x400) * 6;
  uVar2 = (undefined2)uVar3;
  (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffb5a0u + (uint32_t)((int)puVar4)))))) = uVar2;
  compute_q15_sine_cosine_turn_angle_70e32(uVar3 & 0xffff,(stack_record_1e + 2),(stack_record_1e + 4));
  sVar6 = current_correction_coefficient_b;
  (*((short *)camry_host_ptr((uint32_t)((0xffffb5a4u + (uint32_t)((int)puVar4)))))) = (*((int16_t *)(stack_record_1e + 4)));
  sVar10 = current_correction_coefficient_a;
  (*((short *)camry_host_ptr((uint32_t)((0xffffb5a2u + (uint32_t)((int)puVar4)))))) = (*((int16_t *)(stack_record_1e + 2)));
  (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffb5a0u + (uint32_t)((int)puVar4)))))) = uVar2;
  (*((int *)camry_host_ptr((uint32_t)((0xffffb5c0u + (uint32_t)((int)puVar4)))))) = (int)sVar6 * (int)(*((int16_t *)(stack_record_1e + 4)));
  (*((int *)camry_host_ptr((uint32_t)((0xffffb5c4u + (uint32_t)((int)puVar4)))))) = (int)sVar10 * (int)(*((int16_t *)(stack_record_1e + 2)));
  iVar9 = (((((int)sVar6 * (int)(*((int16_t *)(stack_record_1e + 4)))) / 0x100) * iVar5) / 0x400) * (uint)uVar1;
  iVar5 = (((((int)sVar10 * (int)(*((int16_t *)(stack_record_1e + 2)))) / 0x100) * iVar5) / 0x400) * (uint)uVar1;
  (*((int *)camry_host_ptr((uint32_t)((0xffffb5b4u + (uint32_t)((int)puVar4)))))) = iVar9;
  (*((int *)camry_host_ptr((uint32_t)((0xffffb5b8u + (uint32_t)((int)puVar4)))))) = iVar5;
  iVar7 = (int)DAT_00031b92;
  iVar8 = (int)DAT_00031b94;
  if (((*((ushort *)camry_host_ptr((uint32_t)((0xffffb9ecu + (uint32_t)((int)puVar4)))))) & 3) == 0) {
    iVar9 = iVar9 / 0x20000;
    iVar5 = iVar5 / 0x20000;
    if (iVar7 - iVar9 < 0 != (iVar7 < 0 != iVar9 < 0 && iVar9 < 0 == iVar7 - iVar9 < 0)) {
      iVar9 = iVar7;
    }
    iVar11 = iVar8;
    if (iVar9 - iVar8 < 0 == (iVar9 < 0 != iVar8 < 0 && iVar8 < 0 == iVar9 - iVar8 < 0)) {
      iVar11 = iVar9;
    }
    uVar2 = (undefined2)iVar11;
    if (iVar7 - iVar5 < 0 != (iVar7 < 0 != iVar5 < 0 && iVar5 < 0 == iVar7 - iVar5 < 0)) {
      iVar5 = iVar7;
    }
    if (iVar5 - iVar8 < 0 == (iVar5 < 0 != iVar8 < 0 && iVar8 < 0 == iVar5 - iVar8 < 0)) {
      iVar8 = iVar5;
    }
  }
  else {
    uVar2 = 0;
    iVar8 = 0;
  }
  (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffb5a6u + (uint32_t)((int)puVar4)))))) = 0;
  (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffb5a8u + (uint32_t)((int)puVar4)))))) = 0;
  (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffb5aau + (uint32_t)((int)puVar4)))))) = uVar2;
  (*((short *)camry_host_ptr((uint32_t)((0xffffb5acu + (uint32_t)((int)puVar4)))))) = (short)iVar8;
  return camry_r10_result;
}

void return_only_stub_3835a(void)

{
  return;
}

void return_only_stub_3835c(void)

{
  return;
}

void select_actual_and_feedback_first_current_baselines(void)

{
  int iVar1;
  int iVar2;
  
  iVar2 = (int)((int)(int16_t)DAT_febe6dec);
  actual_first_current_command = DAT_00031bf2;
  if ((DAT_00031bf0 != 'Z') &&
     (iVar1 = additional_first_current_reference.output - iVar2,
     actual_first_current_command = ((int)(int16_t)DAT_febe6dec),
     iVar1 < 0 !=
     (additional_first_current_reference.output < 0 != iVar2 < 0 && iVar2 < 0 == iVar1 < 0))) {
    actual_first_current_command = additional_first_current_reference.output;
  }
  iVar1 = current_reference_floor.selected_request - iVar2;
  first_current_feedback_baseline = ((int)(int16_t)DAT_febe6dec);
  if (iVar1 < 0 !=
      (current_reference_floor.selected_request < 0 != iVar2 < 0 && iVar2 < 0 == iVar1 < 0)) {
    first_current_feedback_baseline = current_reference_floor.selected_request;
  }
  return;
}

void return_only_stub_38392(void)

{
  return;
}

void return_only_stub_38394(void)

{
  return;
}

int interpolate_current_curve(short first_component)

{
  uint uVar1;
  int iVar2;
  uint uVar3;
  int iVar4;
  uint uVar5;
  uint uVar6;
  int iVar7;
  int iVar8;
  uint uVar9;
  int iVar10;
  
  iVar4 = (int)first_component;
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
  iVar7 = (int)(int16_t)DAT_00031bfa;
  if (iVar4 - iVar7 < 0 == (iVar4 < 0 != iVar7 < 0 && iVar7 < 0 == iVar4 - iVar7 < 0)) {
    iVar2 = (int)(int16_t)DAT_00031bfe;
    if (iVar4 - iVar2 < 0 == (iVar4 < 0 != iVar2 < 0 && iVar2 < 0 == iVar4 - iVar2 < 0)) {
      iVar10 = 4;
      iVar4 = 4;
      uVar3 = 0x400;
    }
    else {
      iVar8 = (int)(int16_t)DAT_00031bfc;
      if (iVar4 - iVar8 < 0 == (iVar4 < 0 != iVar8 < 0 && iVar8 < 0 == iVar4 - iVar8 < 0)) {
        iVar2 = iVar2 - iVar8;
        uVar3 = (iVar4 - iVar8) * 0x400;
        iVar10 = 3;
        iVar4 = 4;
        if (iVar2 != 0) {
          if (uVar3 == 0x80000000 && iVar2 == -1) {
            uVar3 = 0;
          }
          else {
            uVar3 = (int)uVar3 / iVar2;
          }
        }
      }
      else {
        iVar8 = iVar8 - iVar7;
        uVar3 = (iVar4 - iVar7) * 0x400;
        iVar10 = 2;
        iVar4 = 3;
        if (iVar8 != 0) {
          if (uVar3 == 0x80000000 && iVar8 == -1) {
            uVar3 = 0;
          }
          else {
            uVar3 = (int)uVar3 / iVar8;
          }
        }
      }
      uVar3 = uVar3 & 0xffff;
    }
  }
  else {
    iVar2 = (int)(int16_t)DAT_00031bf8;
    if (iVar4 - iVar2 < 0 == (iVar4 < 0 != iVar2 < 0 && iVar2 < 0 == iVar4 - iVar2 < 0)) {
      iVar7 = iVar7 - iVar2;
      uVar3 = (iVar4 - iVar2) * 0x400;
      iVar10 = 1;
      iVar4 = 2;
      if (iVar7 != 0) {
        if (uVar3 == 0x80000000 && iVar7 == -1) {
          uVar3 = 0;
        }
        else {
          uVar3 = (int)uVar3 / iVar7;
        }
      }
    }
    else {
      iVar7 = (int)(int16_t)DAT_00031bf6;
      iVar10 = 0;
      if (iVar4 - iVar7 < 0 != (iVar4 < 0 != iVar7 < 0 && iVar7 < 0 == iVar4 - iVar7 < 0)) {
        iVar4 = 0;
        uVar3 = 0;
        goto LAB_0003842a;
      }
      iVar2 = iVar2 - iVar7;
      uVar3 = (iVar4 - iVar7) * 0x400;
      iVar4 = 1;
      if (iVar2 != 0) {
        if (uVar3 == 0x80000000 && iVar2 == -1) {
          uVar3 = 0;
        }
        else {
          uVar3 = (int)uVar3 / iVar2;
        }
      }
    }
    uVar3 = uVar3 & 0xffff;
  }
LAB_0003842a:
  uVar9 = (uVar1 & 0xffff) >> 7;
  iVar7 = *(int *)(((undefined *)camry_host_ptr((uint32_t)(0x210e0u + (uint32_t)(iVar4 * 4) * 1u))));
  if (uVar9 < 0xff) {
    uVar5 = (uint)(*((ushort *)camry_host_ptr((uint32_t)(uVar9 * 4 + iVar7 + 2))));
    uVar9 = uVar5 + (int)((uVar1 & 0x7f) * ((*((ushort *)camry_host_ptr((uint32_t)((uVar9 + 1) * 4 + iVar7 + 2)))) - uVar5)) /
                    0x80 & 0xffff;
  }
  else {
    uVar9 = (uint)(*((ushort *)camry_host_ptr((uint32_t)(iVar7 + 0x3fe))));
  }
  uVar5 = (uVar1 & 0xffff) >> 7;
  iVar7 = *(int *)(((undefined *)camry_host_ptr((uint32_t)(0x210e0u + (uint32_t)(iVar10 * 4) * 1u))));
  if (uVar5 < 0xff) {
    uVar6 = (uint)(*((ushort *)camry_host_ptr((uint32_t)(uVar5 * 4 + iVar7 + 2))));
    uVar1 = (int)((uVar1 & 0x7f) * ((*((ushort *)camry_host_ptr((uint32_t)((uVar5 + 1) * 4 + iVar7 + 2)))) - uVar6)) / 0x80 +
            uVar6 & 0xffff;
  }
  else {
    uVar1 = (uint)(*((ushort *)camry_host_ptr((uint32_t)(iVar7 + 0x3fe))));
  }
  DAT_febe6dd4 = (short)uVar9;
  DAT_febe6dd0 = (short)uVar3;
  DAT_febe6dcc = (char)iVar10;
  DAT_febe6dcd = (char)iVar4;
  DAT_febe6dd2 = (short)uVar1;
  return (int)((uVar9 - uVar1) * uVar3) / 0x400 + uVar1;
}

void map_first_current_command_with_6e0a_sign_384d8(void)

{
  short sVar1;
  short sVar2;
  uint32_t puVar3;
  int iVar4;
  
  sVar2 = ((int)(int16_t)DAT_febe6e0a);
  sVar1 = actual_first_current_command;
  puVar3 = 0xfebeb800u;
  iVar4 = interpolate_current_curve(actual_first_current_command);
  if (sVar2 < 1) {
    iVar4 = -iVar4;
  }
  (*((int *)camry_host_ptr((uint32_t)((0xffffb5dcu + (uint32_t)((int)puVar3)))))) = iVar4;
  (*((short *)camry_host_ptr((uint32_t)((0xffffb5ceu + (uint32_t)((int)puVar3)))))) = sVar1;
  (*((short *)camry_host_ptr((uint32_t)((0xffffb5d6u + (uint32_t)((int)puVar3)))))) = (short)iVar4;
  return;
}

void return_only_stub_384fe(void)

{
  return;
}

void return_only_stub_38500(void)

{
  return;
}

void map_sampled_command_to_base_first_current(void)

{
  uint uVar1;
  int iVar2;
  int iVar3;
  uint uVar4;
  
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
  uVar4 = (uVar1 & 0xffff) >> 7;
  if (uVar4 < 0xff) {
    iVar2 = (int)(short)(*(short *)(((undefined *)camry_host_ptr((uint32_t)(0x2e33eu + (uint32_t)(uVar4 * 4) * 1u)))) +
                        (short)((int)((uVar1 & 0x7f) *
                                     ((int)*(short *)(((undefined *)camry_host_ptr((uint32_t)(0x2e33eu + (uint32_t)((uVar4 + 1) * 4) * 1u)))) -
                                     (int)*(short *)(((undefined *)camry_host_ptr((uint32_t)(0x2e33eu + (uint32_t)(uVar4 * 4) * 1u)))))) / 0x80));
  }
  else {
    iVar2 = -0x1c81;
  }
  iVar3 = (int)first_current_curve_upper_bound;
  if (iVar2 - iVar3 < 0 != (iVar2 < 0 != iVar3 < 0 && iVar3 < 0 == iVar2 - iVar3 < 0) ||
      iVar2 == iVar3) {
    iVar3 = iVar2;
  }
  iVar2 = (int)first_current_curve_lower_bound;
  DAT_febe6dee = (short)uVar1;
  DAT_febe6dec = first_current_curve_lower_bound;
  if (iVar3 - iVar2 < 0 == (iVar3 < 0 != iVar2 < 0 && iVar2 < 0 == iVar3 - iVar2 < 0)) {
    DAT_febe6dec = (short)iVar3;
  }
  return;
}

void return_only_stub_3857e(void)

{
  return;
}

void return_only_stub_38580(void)

{
  return;
}

short scale_additional_first_current_request(short request)

{
  additional_first_current_reference.previous_output =
       additional_first_current_reference.output;
  additional_first_current_reference.scaled_request =
       (short)(((int)additional_first_current_reference.gain_q7 * (int)request) / 0x80);
  additional_first_current_reference.delta =
       additional_first_current_reference.scaled_request -
       additional_first_current_reference.output;
  additional_first_current_reference.delta_passthrough =
       additional_first_current_reference.delta;
  additional_first_current_reference.candidate =
       additional_first_current_reference.delta + additional_first_current_reference.output;
  return additional_first_current_reference.delta +
         additional_first_current_reference.output;
}

short clamp_additional_first_current_request(short request)

{
  int iVar1;
  int iVar2;
  short sVar3;
  int iVar4;
  
  iVar2 = (int)request;
  iVar4 = (int)current_reference_floor.curve_floor;
  iVar1 = (int)current_reference_floor_calibration.request_upper;
  if (iVar1 - iVar2 < 0 != (iVar1 < 0 != iVar2 < 0 && iVar2 < 0 == iVar1 - iVar2 < 0)) {
    iVar2 = iVar1;
  }
  sVar3 = current_reference_floor.curve_floor;
  if (iVar2 - iVar4 < 0 == (iVar2 < 0 != iVar4 < 0 && iVar4 < 0 == iVar2 - iVar4 < 0)) {
    sVar3 = (short)iVar2;
  }
  return sVar3;
}

void update_additional_first_current_request(void)

{
  uint8_t stack_record_1c[28];
  uchar uVar1;
  char cVar2;
  uchar uVar3;
  uint32_t puVar4;
  int iVar5;
  short sVar6;
  undefined *puVar7;
  
  uVar3 = additional_current_envelope_qualified;
  sVar6 = current_reference_floor.selected_request;
  cVar2 = DAT_00031d40;
  uVar1 = current_reference_floor_calibration.force_enabled;
  puVar4 = 0xfebeb800u;
  puVar7 = ((void *)camry_host_ptr((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x31ebcu + (uint32_t)(DAT_febee5c3 & 1) * 4u)))))));
  if ((DAT_febee741 == '\x11') || (DAT_febee741 == '\"')) {
    if ((int)DAT_febee744 + -0x7fff < 0 == ((int)DAT_febee744 < 0 && -1 < (int)DAT_febee744 + -0x7fff) &&
        ((int)(int32_t)DAT_febee744) != 0x7fff) {
      iVar5 = 0x7fff;
    }
    else {
      iVar5 = ((int)(int32_t)DAT_febee744);
      if ((int)DAT_febee744 + 0x7fff < 0 != (-1 < (int)DAT_febee744 && (int)DAT_febee744 + 0x7fff < 0)) {
        iVar5 = -0x7fff;
      }
    }
    puVar4 = 0xfebeb800u;
    store_saturating_absolute_s16_6a522((int)(short)iVar5,((uint16_t *)(stack_record_1c)));
    interpolate_u16_axis_s16_values_702b0(puVar7,(*((uint16_t *)(stack_record_1c + 0))),((uint16_t *)((stack_record_1c + 2))));
  }
  else {
    (*((uint16_t *)(stack_record_1c + 2))) = (*((undefined2 *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x31eb4u + (uint32_t)(DAT_febee5c3 & 1) * 4u)))))));
  }
  (*((undefined2 *)camry_host_ptr((uint32_t)((0xffffb5f0u + (uint32_t)((int)puVar4)))))) = (*((uint16_t *)(stack_record_1c + 2)));
  if (((uVar1 != '\x01') && (cVar2 == '\x01')) && (uVar3 == 'Z')) {
    sVar6 = scale_additional_first_current_request(sVar6);
    sVar6 = clamp_additional_first_current_request(sVar6);
  }
  (*((short *)camry_host_ptr((uint32_t)((0xffffb5fau + (uint32_t)((int)puVar4)))))) = sVar6;
  return;
}

void return_only_stub_38674(void)

{
  return;
}

void return_only_stub_38676(void)

{
  return;
}

int lookup_signed_five_map_signal(int value,short selector)

{
  int iVar1;
  int iVar2;
  uint uVar3;
  uint uVar4;
  uint uVar5;
  int iVar6;
  uint uVar7;
  int iVar8;
  uint32_t puVar9;
  int iVar10;
  
  iVar2 = (int)selector;
  if (value + 0x7fffffff < 0 == (-1 < value && value + 0x7fffffff < 0) && value != -0x7fffffff) {
    uVar5 = value;
    if (value < 0) {
      uVar5 = -value;
    }
  }
  else {
    uVar5 = 0x7fffffff;
  }
  iVar6 = (int)DAT_00031d44;
  if ((int)(uVar5 - 0xffff) < 0 == ((int)uVar5 < 0 && -1 < (int)(uVar5 - 0xffff))) {
    uVar5 = 0xffff;
  }
  if ((int)uVar5 < 0) {
    uVar5 = 0;
  }
  if (iVar2 - iVar6 < 0 != (iVar2 < 0 != iVar6 < 0 && iVar6 < 0 == iVar2 - iVar6 < 0)) {
    iVar1 = 0;
    iVar10 = 0;
    uVar3 = 0;
    goto LAB_00038704;
  }
  iVar8 = (int)DAT_00031d46;
  if (iVar2 - iVar8 < 0 == (iVar2 < 0 != iVar8 < 0 && iVar8 < 0 == iVar2 - iVar8 < 0)) {
    iVar6 = (int)DAT_00031d48;
    if (iVar2 - iVar6 < 0 == (iVar2 < 0 != iVar6 < 0 && iVar6 < 0 == iVar2 - iVar6 < 0)) {
      iVar8 = (int)DAT_00031d4a;
      if (iVar2 - iVar8 < 0 != (iVar2 < 0 != iVar8 < 0 && iVar8 < 0 == iVar2 - iVar8 < 0)) {
        iVar1 = 2;
        iVar10 = 3;
        goto LAB_000386da;
      }
      iVar6 = (int)DAT_00031d4c;
      iVar10 = 4;
      if (iVar2 - iVar6 < 0 == (iVar2 < 0 != iVar6 < 0 && iVar6 < 0 == iVar2 - iVar6 < 0)) {
        iVar1 = 4;
        uVar3 = 0x400;
        goto LAB_00038704;
      }
      iVar1 = 3;
    }
    else {
      iVar1 = 1;
      iVar10 = 2;
    }
    iVar6 = iVar6 - iVar8;
    uVar3 = (iVar2 - iVar8) * 0x400;
    if (iVar6 != 0) {
      if (uVar3 == 0x80000000 && iVar6 == -1) {
        uVar3 = 0;
      }
      else {
        uVar3 = (int)uVar3 / iVar6;
      }
    }
  }
  else {
    iVar1 = 0;
    iVar10 = 1;
LAB_000386da:
    iVar8 = iVar8 - iVar6;
    uVar3 = (iVar2 - iVar6) * 0x400;
    if (iVar8 != 0) {
      if (uVar3 == 0x80000000 && iVar8 == -1) {
        uVar3 = 0;
      }
      else {
        uVar3 = (int)uVar3 / iVar8;
      }
    }
  }
  uVar3 = uVar3 & 0xffff;
LAB_00038704:
  uVar7 = (uVar5 & 0xffff) >> 7;
  puVar9 = ((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x210f4u + (uint32_t)(iVar10) * 4u))))));
  if (uVar7 < 0xff) {
    uVar4 = (uint)(*((volatile uint16_t *)camry_host_ptr((uint32_t)(puVar9 + uVar7 * 4 + 2)))) +
            (int)((uVar5 & 0x7f) *
                 ((uint)(*((volatile uint16_t *)camry_host_ptr((uint32_t)(puVar9 + (uVar7 + 1) * 4 + 2)))) -
                 (uint)(*((volatile uint16_t *)camry_host_ptr((uint32_t)(puVar9 + uVar7 * 4 + 2)))))) / 0x80 & 0xffff;
  }
  else {
    uVar4 = (uint)(*((volatile uint16_t *)camry_host_ptr((uint32_t)(puVar9 + 0x3fe))));
  }
  puVar9 = ((uint32_t)((*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x210f4u + (uint32_t)(iVar1) * 4u))))));
  if (uVar7 < 0xff) {
    uVar5 = (uint)(*((volatile uint16_t *)camry_host_ptr((uint32_t)(puVar9 + uVar7 * 4 + 2)))) +
            (int)((uVar5 & 0x7f) *
                 ((uint)(*((volatile uint16_t *)camry_host_ptr((uint32_t)(puVar9 + (uVar7 + 1) * 4 + 2)))) -
                 (uint)(*((volatile uint16_t *)camry_host_ptr((uint32_t)(puVar9 + uVar7 * 4 + 2)))))) / 0x80 & 0xffff;
  }
  else {
    uVar5 = (uint)(*((volatile uint16_t *)camry_host_ptr((uint32_t)(puVar9 + 0x3fe))));
  }
  iVar2 = (int)((uVar4 - uVar5) * uVar3) / 0x400 + uVar5;
  if (value < 1) {
    iVar2 = -iVar2;
  }
  return iVar2;
}

void lookup_6d78_6d70_signed_five_map_signal_3879e(void)

{
  uint32_t puVar1;
  int iVar2;
  
  puVar1 = 0xfebeb800u;
  iVar2 = lookup_signed_five_map_signal(DAT_febe6d78,((int)(int16_t)DAT_febe6d70));
  (*((short *)camry_host_ptr((uint32_t)((0xffffb600u + (uint32_t)((int)puVar1)))))) = (short)iVar2;
  return;
}

void return_only_stub_387b6(void)

{
  return;
}

void return_only_stub_387b8(void)

{
  return;
}

void reset_6e04_flags_and_snapshot_6af4_387ba(void)

{
  DAT_febe6e04 = 0;
  DAT_febe6e05 = 0;
  DAT_febe6e0a = ((int)(int16_t)DAT_febe6af4);
  return;
}

void return_only_stub_387ca(void)

{
  return;
}

void return_only_stub_387cc(void)

{
  return;
}

void latch_current_feedback_and_reference_inputs(void)

{
  DAT_febe6e12 = ((int)(int16_t)DAT_febe6b34);
  DAT_febe6e14 = ((int)(int16_t)DAT_febe6b36);
  DAT_febe6e16 = ((int)(int16_t)DAT_febe6b38);
  DAT_febe6e18 = ((int)(int16_t)DAT_febe6b3a);
  DAT_febe6e28 = DAT_febe6b3c;
  DAT_febe6e2c = DAT_febe6b40;
  DAT_febe6e30 = DAT_febe6b44;
  DAT_febe6e1e = 0;
  DAT_febe6e20 = 0;
  DAT_febe6e34 = DAT_febe6b48;
  DAT_febe6e1a = (*((volatile int16_t *)camry_host_ptr((uint32_t)(0xfebe6b50u + (uint32_t)(0) * (uint32_t)sizeof(F33CurrentReferenceFeedbackState) + (uint32_t)offsetof(F33CurrentReferenceFeedbackState, request)))));
  DAT_febe6e1c = (*((volatile int16_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe6b50u + (uint32_t)(1) * (uint32_t)sizeof(F33CurrentReferenceFeedbackState)) + (uint32_t)(0) * (uint32_t)sizeof(F33CurrentReferenceFeedbackState) + (uint32_t)offsetof(F33CurrentReferenceFeedbackState, request)))));
  DAT_febe6e22 = ((int)(int16_t)DAT_febe6af6);
  DAT_febe6e24 = ((int)(int16_t)DAT_febe6af6);
  DAT_febe6e0c = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe6be8u + (uint32_t)(0) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeState) + (uint32_t)offsetof(F33RegulatorOutputEnvelopeState, first_saturation)))));
  DAT_febe6e0e = (*((volatile uint8_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe6be8u + (uint32_t)(1) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeState)) + (uint32_t)(0) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeState) + (uint32_t)offsetof(F33RegulatorOutputEnvelopeState, first_saturation)))));
  DAT_febe6e0d = (*((volatile uint8_t *)camry_host_ptr((uint32_t)(0xfebe6be8u + (uint32_t)(0) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeState) + (uint32_t)offsetof(F33RegulatorOutputEnvelopeState, second_saturation)))));
  DAT_febe6e0f = (*((volatile uint8_t *)camry_host_ptr((uint32_t)((uint32_t)(0xfebe6be8u + (uint32_t)(1) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeState)) + (uint32_t)(0) * (uint32_t)sizeof(F33RegulatorOutputEnvelopeState) + (uint32_t)offsetof(F33RegulatorOutputEnvelopeState, second_saturation)))));
  return;
}

void return_only_stub_38836(void)

{
  return;
}

void clear_6e40_and_6e44_states_38838(void)

{
  DAT_febe6e40 = 0;
  DAT_febe6e44 = 0;
  return;
}

void modulate_first_phase_triplet(void)

{
  int iVar1;
  int iVar2;
  short sVar3;
  short sVar4;
  short sVar5;
  short sVar6;
  short sVar7;
  uint uVar8;
  uint uVar9;
  uint uVar10;
  int iVar11;
  int iVar12;
  uint uVar13;
  uint uVar14;
  uint uVar15;
  
  sVar3 = (short)((int)(int32_t)DAT_febe6b9c);
  sVar4 = (short)((int)(int32_t)DAT_febe6ba0);
  sVar7 = (short)((int)(int32_t)DAT_febe6ba4);
  if (DAT_febe6d5c == '\0') {
    DAT_febe6e3a = DAT_febe6d5e + sVar3;
    DAT_febe6e3c = DAT_febe6d5e + sVar4;
    DAT_febe6e3e = DAT_febe6d5e + sVar7;
  }
  else if (DAT_febe6d5c == 'Z') {
    iVar12 = ((int)(int32_t)DAT_febe6b9c);
    if (((int)(int32_t)DAT_febe6ba0) - ((int)(int32_t)DAT_febe6b9c) < 0 !=
        (((int)(int32_t)DAT_febe6ba0) < 0 != ((int)(int32_t)DAT_febe6b9c) < 0 && ((int)(int32_t)DAT_febe6b9c) < 0 == ((int)(int32_t)DAT_febe6ba0) - ((int)(int32_t)DAT_febe6b9c) < 0
        )) {
      iVar12 = ((int)(int32_t)DAT_febe6ba0);
    }
    if (((int)(int32_t)DAT_febe6ba4) - iVar12 < 0 !=
        (((int)(int32_t)DAT_febe6ba4) < 0 != iVar12 < 0 && iVar12 < 0 == ((int)(int32_t)DAT_febe6ba4) - iVar12 < 0)) {
      iVar12 = ((int)(int32_t)DAT_febe6ba4);
    }
    iVar11 = ((int)(int32_t)DAT_febe6b9c);
    if (((int)(int32_t)DAT_febe6ba0) - ((int)(int32_t)DAT_febe6b9c) < 0 ==
        (((int)(int32_t)DAT_febe6ba0) < 0 != ((int)(int32_t)DAT_febe6b9c) < 0 && ((int)(int32_t)DAT_febe6b9c) < 0 == ((int)(int32_t)DAT_febe6ba0) - ((int)(int32_t)DAT_febe6b9c) < 0
        ) && ((int)(int32_t)DAT_febe6ba0) != ((int)(int32_t)DAT_febe6b9c)) {
      iVar11 = ((int)(int32_t)DAT_febe6ba0);
    }
    if (((int)(int32_t)DAT_febe6ba4) - iVar11 < 0 ==
        (((int)(int32_t)DAT_febe6ba4) < 0 != iVar11 < 0 && iVar11 < 0 == ((int)(int32_t)DAT_febe6ba4) - iVar11 < 0) &&
        ((int)(int32_t)DAT_febe6ba4) != iVar11) {
      iVar11 = ((int)(int32_t)DAT_febe6ba4);
    }
    sVar5 = DAT_00031e20 - (short)iVar11;
    sVar6 = (short)iVar12 - DAT_00031e22;
    if (phase_offset_selector == 'Z') {
      DAT_febe6e3a = sVar5 + sVar3;
      DAT_febe6e3c = sVar5 + sVar4;
      DAT_febe6e3e = sVar5 + sVar7;
    }
    else {
      DAT_febe6e3a = sVar3 - sVar6;
      DAT_febe6e3c = sVar4 - sVar6;
      DAT_febe6e3e = sVar7 - sVar6;
    }
  }
  else {
    uVar10 = (uint)DAT_00031e24;
    uVar9 = (uint)DAT_00031e26;
    iVar12 = ((int)(int32_t)DAT_febe6b9c);
    if (((int)(int32_t)DAT_febe6ba0) - ((int)(int32_t)DAT_febe6b9c) < 0 !=
        (((int)(int32_t)DAT_febe6ba0) < 0 != ((int)(int32_t)DAT_febe6b9c) < 0 && ((int)(int32_t)DAT_febe6b9c) < 0 == ((int)(int32_t)DAT_febe6ba0) - ((int)(int32_t)DAT_febe6b9c) < 0
        )) {
      iVar12 = ((int)(int32_t)DAT_febe6ba0);
    }
    if (((int)(int32_t)DAT_febe6ba4) - iVar12 < 0 !=
        (((int)(int32_t)DAT_febe6ba4) < 0 != iVar12 < 0 && iVar12 < 0 == ((int)(int32_t)DAT_febe6ba4) - iVar12 < 0)) {
      iVar12 = ((int)(int32_t)DAT_febe6ba4);
    }
    iVar11 = ((int)(int32_t)DAT_febe6b9c);
    if (((int)(int32_t)DAT_febe6ba0) - ((int)(int32_t)DAT_febe6b9c) < 0 ==
        (((int)(int32_t)DAT_febe6ba0) < 0 != ((int)(int32_t)DAT_febe6b9c) < 0 && ((int)(int32_t)DAT_febe6b9c) < 0 == ((int)(int32_t)DAT_febe6ba0) - ((int)(int32_t)DAT_febe6b9c) < 0
        ) && ((int)(int32_t)DAT_febe6ba0) != ((int)(int32_t)DAT_febe6b9c)) {
      iVar11 = ((int)(int32_t)DAT_febe6ba0);
    }
    if (((int)(int32_t)DAT_febe6ba4) - iVar11 < 0 ==
        (((int)(int32_t)DAT_febe6ba4) < 0 != iVar11 < 0 && iVar11 < 0 == ((int)(int32_t)DAT_febe6ba4) - iVar11 < 0) &&
        ((int)(int32_t)DAT_febe6ba4) != iVar11) {
      iVar11 = ((int)(int32_t)DAT_febe6ba4);
    }
    iVar2 = uVar10 - iVar11;
    iVar1 = iVar11 * 3 - uVar10;
    if (iVar1 < 0 != (iVar11 * 3 < 0 && -1 < iVar1) || iVar1 == 0) {
      iVar2 = -(iVar12 - uVar9);
    }
    uVar15 = iVar2 + ((int)(int32_t)DAT_febe6ba4);
    uVar13 = iVar2 + ((int)(int32_t)DAT_febe6b9c);
    uVar8 = iVar2 + ((int)(int32_t)DAT_febe6ba0);
    if ((int)(uVar10 - uVar13) < 0 !=
        ((int)uVar13 < 0 && (int)uVar13 < 0 == (int)(uVar10 - uVar13) < 0)) {
      uVar13 = uVar10;
    }
    uVar14 = uVar9;
    if ((int)(uVar13 - uVar9) < 0 == ((int)uVar13 < 0 && -1 < (int)(uVar13 - uVar9))) {
      uVar14 = uVar13;
    }
    DAT_febe6e3a = (short)uVar14;
    if ((int)(uVar10 - uVar8) < 0 != ((int)uVar8 < 0 && (int)uVar8 < 0 == (int)(uVar10 - uVar8) < 0)
       ) {
      uVar8 = uVar10;
    }
    uVar13 = uVar9;
    if ((int)(uVar8 - uVar9) < 0 == ((int)uVar8 < 0 && -1 < (int)(uVar8 - uVar9))) {
      uVar13 = uVar8;
    }
    DAT_febe6e3c = (short)uVar13;
    if ((int)(uVar10 - uVar15) < 0 !=
        ((int)uVar15 < 0 && (int)uVar15 < 0 == (int)(uVar10 - uVar15) < 0)) {
      uVar15 = uVar10;
    }
    DAT_febe6e3e = DAT_00031e26;
    if ((int)(uVar15 - uVar9) < 0 == ((int)uVar15 < 0 && -1 < (int)(uVar15 - uVar9))) {
      DAT_febe6e3e = (ushort)uVar15;
    }
  }
  return;
}

void return_only_stub_38940(void)

{
  return;
}

void clear_6e50_and_6e54_states_38942(void)

{
  DAT_febe6e50 = 0;
  DAT_febe6e54 = 0;
  return;
}

void modulate_second_phase_triplet(void)

{
  int iVar1;
  int iVar2;
  short sVar3;
  short sVar4;
  short sVar5;
  short sVar6;
  short sVar7;
  uint uVar8;
  uint uVar9;
  uint uVar10;
  int iVar11;
  int iVar12;
  uint uVar13;
  uint uVar14;
  uint uVar15;
  
  sVar3 = (short)((int)(int32_t)DAT_febe6bc0);
  sVar4 = (short)((int)(int32_t)DAT_febe6bc4);
  sVar7 = (short)((int)(int32_t)DAT_febe6bc8);
  if (DAT_febe6d5d == '\0') {
    DAT_febe6e4a = DAT_febe6d60 + sVar3;
    DAT_febe6e4c = DAT_febe6d60 + sVar4;
    DAT_febe6e4e = DAT_febe6d60 + sVar7;
  }
  else if (DAT_febe6d5d == 'Z') {
    iVar12 = ((int)(int32_t)DAT_febe6bc0);
    if (((int)(int32_t)DAT_febe6bc4) - ((int)(int32_t)DAT_febe6bc0) < 0 !=
        (((int)(int32_t)DAT_febe6bc4) < 0 != ((int)(int32_t)DAT_febe6bc0) < 0 && ((int)(int32_t)DAT_febe6bc0) < 0 == ((int)(int32_t)DAT_febe6bc4) - ((int)(int32_t)DAT_febe6bc0) < 0
        )) {
      iVar12 = ((int)(int32_t)DAT_febe6bc4);
    }
    if (((int)(int32_t)DAT_febe6bc8) - iVar12 < 0 !=
        (((int)(int32_t)DAT_febe6bc8) < 0 != iVar12 < 0 && iVar12 < 0 == ((int)(int32_t)DAT_febe6bc8) - iVar12 < 0)) {
      iVar12 = ((int)(int32_t)DAT_febe6bc8);
    }
    iVar11 = ((int)(int32_t)DAT_febe6bc0);
    if (((int)(int32_t)DAT_febe6bc4) - ((int)(int32_t)DAT_febe6bc0) < 0 ==
        (((int)(int32_t)DAT_febe6bc4) < 0 != ((int)(int32_t)DAT_febe6bc0) < 0 && ((int)(int32_t)DAT_febe6bc0) < 0 == ((int)(int32_t)DAT_febe6bc4) - ((int)(int32_t)DAT_febe6bc0) < 0
        ) && ((int)(int32_t)DAT_febe6bc4) != ((int)(int32_t)DAT_febe6bc0)) {
      iVar11 = ((int)(int32_t)DAT_febe6bc4);
    }
    if (((int)(int32_t)DAT_febe6bc8) - iVar11 < 0 ==
        (((int)(int32_t)DAT_febe6bc8) < 0 != iVar11 < 0 && iVar11 < 0 == ((int)(int32_t)DAT_febe6bc8) - iVar11 < 0) &&
        ((int)(int32_t)DAT_febe6bc8) != iVar11) {
      iVar11 = ((int)(int32_t)DAT_febe6bc8);
    }
    sVar5 = DAT_00031e2c - (short)iVar11;
    sVar6 = (short)iVar12 - DAT_00031e2e;
    if (phase_offset_selector == 0xa5) {
      DAT_febe6e4a = sVar5 + sVar3;
      DAT_febe6e4c = sVar5 + sVar4;
      DAT_febe6e4e = sVar5 + sVar7;
    }
    else {
      DAT_febe6e4a = sVar3 - sVar6;
      DAT_febe6e4c = sVar4 - sVar6;
      DAT_febe6e4e = sVar7 - sVar6;
    }
  }
  else {
    uVar10 = (uint)DAT_00031e30;
    uVar9 = (uint)DAT_00031e32;
    iVar12 = ((int)(int32_t)DAT_febe6bc0);
    if (((int)(int32_t)DAT_febe6bc4) - ((int)(int32_t)DAT_febe6bc0) < 0 !=
        (((int)(int32_t)DAT_febe6bc4) < 0 != ((int)(int32_t)DAT_febe6bc0) < 0 && ((int)(int32_t)DAT_febe6bc0) < 0 == ((int)(int32_t)DAT_febe6bc4) - ((int)(int32_t)DAT_febe6bc0) < 0
        )) {
      iVar12 = ((int)(int32_t)DAT_febe6bc4);
    }
    if (((int)(int32_t)DAT_febe6bc8) - iVar12 < 0 !=
        (((int)(int32_t)DAT_febe6bc8) < 0 != iVar12 < 0 && iVar12 < 0 == ((int)(int32_t)DAT_febe6bc8) - iVar12 < 0)) {
      iVar12 = ((int)(int32_t)DAT_febe6bc8);
    }
    iVar11 = ((int)(int32_t)DAT_febe6bc0);
    if (((int)(int32_t)DAT_febe6bc4) - ((int)(int32_t)DAT_febe6bc0) < 0 ==
        (((int)(int32_t)DAT_febe6bc4) < 0 != ((int)(int32_t)DAT_febe6bc0) < 0 && ((int)(int32_t)DAT_febe6bc0) < 0 == ((int)(int32_t)DAT_febe6bc4) - ((int)(int32_t)DAT_febe6bc0) < 0
        ) && ((int)(int32_t)DAT_febe6bc4) != ((int)(int32_t)DAT_febe6bc0)) {
      iVar11 = ((int)(int32_t)DAT_febe6bc4);
    }
    if (((int)(int32_t)DAT_febe6bc8) - iVar11 < 0 ==
        (((int)(int32_t)DAT_febe6bc8) < 0 != iVar11 < 0 && iVar11 < 0 == ((int)(int32_t)DAT_febe6bc8) - iVar11 < 0) &&
        ((int)(int32_t)DAT_febe6bc8) != iVar11) {
      iVar11 = ((int)(int32_t)DAT_febe6bc8);
    }
    iVar2 = uVar10 - iVar11;
    iVar1 = iVar11 * 3 - uVar10;
    if (iVar1 < 0 != (iVar11 * 3 < 0 && -1 < iVar1) || iVar1 == 0) {
      iVar2 = -(iVar12 - uVar9);
    }
    uVar15 = iVar2 + ((int)(int32_t)DAT_febe6bc8);
    uVar13 = iVar2 + ((int)(int32_t)DAT_febe6bc0);
    uVar8 = iVar2 + ((int)(int32_t)DAT_febe6bc4);
    if ((int)(uVar10 - uVar13) < 0 !=
        ((int)uVar13 < 0 && (int)uVar13 < 0 == (int)(uVar10 - uVar13) < 0)) {
      uVar13 = uVar10;
    }
    uVar14 = uVar9;
    if ((int)(uVar13 - uVar9) < 0 == ((int)uVar13 < 0 && -1 < (int)(uVar13 - uVar9))) {
      uVar14 = uVar13;
    }
    DAT_febe6e4a = (short)uVar14;
    if ((int)(uVar10 - uVar8) < 0 != ((int)uVar8 < 0 && (int)uVar8 < 0 == (int)(uVar10 - uVar8) < 0)
       ) {
      uVar8 = uVar10;
    }
    uVar13 = uVar9;
    if ((int)(uVar8 - uVar9) < 0 == ((int)uVar8 < 0 && -1 < (int)(uVar8 - uVar9))) {
      uVar13 = uVar8;
    }
    DAT_febe6e4c = (short)uVar13;
    if ((int)(uVar10 - uVar15) < 0 !=
        ((int)uVar15 < 0 && (int)uVar15 < 0 == (int)(uVar10 - uVar15) < 0)) {
      uVar15 = uVar10;
    }
    DAT_febe6e4e = DAT_00031e32;
    if ((int)(uVar15 - uVar9) < 0 == ((int)uVar15 < 0 && -1 < (int)(uVar15 - uVar9))) {
      DAT_febe6e4e = (ushort)uVar15;
    }
  }
  return;
}

void return_only_stub_38a4a(void)

{
  return;
}

void clear_6e58_three_component_vector_38a4c(void)

{
  DAT_febe6e58 = 0;
  DAT_febe6e5a = 0;
  DAT_febe6e5c = 0;
  return;
}

void transform_summed_pairs_to_three_saturated_components_38a58(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  
  iVar2 = (int)((int)(int16_t)DAT_febe6d82) + (int)((int)(int16_t)DAT_febe6d80);
  iVar4 = (int)((int)(int16_t)DAT_febe6d7e) + (int)((int)(int16_t)DAT_febe6d7c);
  if ((DAT_febe71ec & 3) == 0) {
    iVar2 = iVar2 / 2;
    iVar4 = iVar4 / 2;
  }
  iVar1 = (((iVar2 * (((int)(int16_t)DAT_febe7d56) / 4) - iVar4 * (((int)(int16_t)DAT_febe7d54) / 4)) / 0x8000) * 0x6883) / 0x2000;
  if (iVar1 + 0x7fff < 0 == (-1 < iVar1 && iVar1 + 0x7fff < 0) && iVar1 != -0x7fff) {
    iVar3 = iVar1;
    if (iVar1 + -0x7fff < 0 == (iVar1 < 0 && -1 < iVar1 + -0x7fff) && iVar1 != 0x7fff) {
      iVar3 = 0x7fff;
    }
  }
  else {
    iVar3 = -0x7fff;
  }
  DAT_febe6e58 = (short)iVar3;
  iVar2 = ((((iVar4 / 2 + (iVar2 * 0x6eda) / 0x8000) * (int)(((int)(int16_t)DAT_febe7d54) / 4) +
            ((iVar4 * 0x6eda) / 0x8000 + -iVar2 / 2) * (int)(((int)(int16_t)DAT_febe7d56) / 4)) / 0x8000) * 0x6883)
          / 0x2000;
  if (iVar2 + 0x7fff < 0 == (-1 < iVar2 && iVar2 + 0x7fff < 0) && iVar2 != -0x7fff) {
    if (iVar2 + -0x7fff < 0 == (iVar2 < 0 && -1 < iVar2 + -0x7fff) && iVar2 != 0x7fff) {
      DAT_febe6e5a = 0x7fff;
    }
    else {
      DAT_febe6e5a = (undefined2)iVar2;
    }
  }
  else {
    DAT_febe6e5a = 0x8001;
  }
  iVar2 = iVar2 + iVar1;
  iVar4 = -iVar2;
  if (iVar4 + 0x7fff < 0 == (-1 < iVar4 && iVar4 + 0x7fff < 0) && iVar2 != 0x7fff) {
    if (iVar4 + -0x7fff < 0 == (iVar4 < 0 && -1 < iVar4 + -0x7fff) && iVar2 != -0x7fff) {
      iVar4 = 0x7fff;
    }
    DAT_febe6e5c = (undefined2)iVar4;
  }
  else {
    DAT_febe6e5c = 0x8001;
  }
  return;
}

void return_only_stub_38b5c(void)

{
  return;
}

void clear_6e60_three_component_vector_38b5e(void)

{
  DAT_febe6e60 = 0;
  DAT_febe6e62 = 0;
  DAT_febe6e64 = 0;
  return;
}

void transform_differenced_pairs_to_three_saturated_components_38b6a(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  
  iVar2 = (int)((int)(int16_t)DAT_febe6d80) - (int)((int)(int16_t)DAT_febe6d82);
  iVar4 = (int)((int)(int16_t)DAT_febe6d7c) - (int)((int)(int16_t)DAT_febe6d7e);
  if ((DAT_febe71ec & 3) == 0) {
    iVar2 = iVar2 / 2;
    iVar4 = iVar4 / 2;
  }
  iVar1 = (((iVar2 * (((int)(int16_t)DAT_febe7d62) / 4) - iVar4 * (((int)(int16_t)DAT_febe7d60) / 4)) / 0x8000) * 0x6883) / 0x2000;
  if (iVar1 + 0x7fff < 0 == (-1 < iVar1 && iVar1 + 0x7fff < 0) && iVar1 != -0x7fff) {
    iVar3 = iVar1;
    if (iVar1 + -0x7fff < 0 == (iVar1 < 0 && -1 < iVar1 + -0x7fff) && iVar1 != 0x7fff) {
      iVar3 = 0x7fff;
    }
  }
  else {
    iVar3 = -0x7fff;
  }
  DAT_febe6e60 = (short)iVar3;
  iVar2 = ((((iVar4 / 2 + (iVar2 * 0x6eda) / 0x8000) * (int)(((int)(int16_t)DAT_febe7d60) / 4) +
            ((iVar4 * 0x6eda) / 0x8000 + -iVar2 / 2) * (int)(((int)(int16_t)DAT_febe7d62) / 4)) / 0x8000) * 0x6883)
          / 0x2000;
  if (iVar2 + 0x7fff < 0 == (-1 < iVar2 && iVar2 + 0x7fff < 0) && iVar2 != -0x7fff) {
    if (iVar2 + -0x7fff < 0 == (iVar2 < 0 && -1 < iVar2 + -0x7fff) && iVar2 != 0x7fff) {
      DAT_febe6e62 = 0x7fff;
    }
    else {
      DAT_febe6e62 = (undefined2)iVar2;
    }
  }
  else {
    DAT_febe6e62 = 0x8001;
  }
  iVar2 = iVar2 + iVar1;
  iVar4 = -iVar2;
  if (iVar4 + 0x7fff < 0 == (-1 < iVar4 && iVar4 + 0x7fff < 0) && iVar2 != 0x7fff) {
    if (iVar4 + -0x7fff < 0 == (iVar4 < 0 && -1 < iVar4 + -0x7fff) && iVar2 != -0x7fff) {
      iVar4 = 0x7fff;
    }
    DAT_febe6e64 = (undefined2)iVar4;
  }
  else {
    DAT_febe6e64 = 0x8001;
  }
  return;
}

void return_only_stub_38c6e(void)

{
  return;
}

void clear_6e68_three_component_vector_38c70(void)

{
  DAT_febe6e68 = 0;
  DAT_febe6e6a = 0;
  DAT_febe6e6c = 0;
  return;
}

void transform_first_regulated_phase_commands(void)

{
  int iVar1;
  int iVar2;
  
  iVar1 = ((((int)(((int)(int16_t)DAT_febe7d56) / 4) * (int)((int)(int16_t)DAT_febe6c40) -
            (int)(((int)(int16_t)DAT_febe7d54) / 4) * (int)((int)(int16_t)DAT_febe6c42)) / 0x8000) * 0x6883) / 0x2000;
  if (iVar1 + 0x7fff < 0 == (-1 < iVar1 && iVar1 + 0x7fff < 0) && iVar1 != -0x7fff) {
    iVar2 = iVar1;
    if (iVar1 + -0x7fff < 0 == (iVar1 < 0 && -1 < iVar1 + -0x7fff) && iVar1 != 0x7fff) {
      iVar2 = 0x7fff;
    }
  }
  else {
    iVar2 = -0x7fff;
  }
  DAT_febe6e68 = (short)iVar2;
  iVar2 = (((((int)((int)(int16_t)DAT_febe6c42) / 2 + (int)(short)((((int)(int16_t)DAT_febe6c40) * 0x6eda) / 0x8000)) *
             (int)(((int)(int16_t)DAT_febe7d54) / 4) +
            ((int)(short)((((int)(int16_t)DAT_febe6c42) * 0x6eda) / 0x8000) + -(int)((int)(int16_t)DAT_febe6c40) / 2) *
            (int)(((int)(int16_t)DAT_febe7d56) / 4)) / 0x8000) * 0x6883) / 0x2000;
  if (iVar2 + 0x7fff < 0 == (-1 < iVar2 && iVar2 + 0x7fff < 0) && iVar2 != -0x7fff) {
    if (iVar2 + -0x7fff < 0 == (iVar2 < 0 && -1 < iVar2 + -0x7fff) && iVar2 != 0x7fff) {
      DAT_febe6e6a = 0x7fff;
    }
    else {
      DAT_febe6e6a = (undefined2)iVar2;
    }
  }
  else {
    DAT_febe6e6a = 0x8001;
  }
  iVar2 = iVar2 + iVar1;
  iVar1 = -iVar2;
  if (iVar1 + 0x7fff < 0 == (-1 < iVar1 && iVar1 + 0x7fff < 0) && iVar2 != 0x7fff) {
    if (iVar1 + -0x7fff < 0 == (iVar1 < 0 && -1 < iVar1 + -0x7fff) && iVar2 != -0x7fff) {
      DAT_febe6e6c = 0x7fff;
    }
    else {
      DAT_febe6e6c = (undefined2)iVar1;
    }
  }
  else {
    DAT_febe6e6c = 0x8001;
  }
  return;
}

void return_only_stub_38d5e(void)

{
  return;
}

void clear_6e70_three_component_vector_38d60(void)

{
  DAT_febe6e70 = 0;
  DAT_febe6e72 = 0;
  DAT_febe6e74 = 0;
  return;
}

void transform_second_regulated_phase_commands(void)

{
  int iVar1;
  int iVar2;
  
  iVar1 = ((((int)(((int)(int16_t)DAT_febe7d62) / 4) * (int)((int)(int16_t)DAT_febe6c44) -
            (int)(((int)(int16_t)DAT_febe7d60) / 4) * (int)((int)(int16_t)DAT_febe6c46)) / 0x8000) * 0x6883) / 0x2000;
  if (iVar1 + 0x7fff < 0 == (-1 < iVar1 && iVar1 + 0x7fff < 0) && iVar1 != -0x7fff) {
    iVar2 = iVar1;
    if (iVar1 + -0x7fff < 0 == (iVar1 < 0 && -1 < iVar1 + -0x7fff) && iVar1 != 0x7fff) {
      iVar2 = 0x7fff;
    }
  }
  else {
    iVar2 = -0x7fff;
  }
  DAT_febe6e70 = (short)iVar2;
  iVar2 = (((((int)((int)(int16_t)DAT_febe6c46) / 2 + (int)(short)((((int)(int16_t)DAT_febe6c44) * 0x6eda) / 0x8000)) *
             (int)(((int)(int16_t)DAT_febe7d60) / 4) +
            ((int)(short)((((int)(int16_t)DAT_febe6c46) * 0x6eda) / 0x8000) + -(int)((int)(int16_t)DAT_febe6c44) / 2) *
            (int)(((int)(int16_t)DAT_febe7d62) / 4)) / 0x8000) * 0x6883) / 0x2000;
  if (iVar2 + 0x7fff < 0 == (-1 < iVar2 && iVar2 + 0x7fff < 0) && iVar2 != -0x7fff) {
    if (iVar2 + -0x7fff < 0 == (iVar2 < 0 && -1 < iVar2 + -0x7fff) && iVar2 != 0x7fff) {
      DAT_febe6e72 = 0x7fff;
    }
    else {
      DAT_febe6e72 = (undefined2)iVar2;
    }
  }
  else {
    DAT_febe6e72 = 0x8001;
  }
  iVar2 = iVar2 + iVar1;
  iVar1 = -iVar2;
  if (iVar1 + 0x7fff < 0 == (-1 < iVar1 && iVar1 + 0x7fff < 0) && iVar2 != 0x7fff) {
    if (iVar1 + -0x7fff < 0 == (iVar1 < 0 && -1 < iVar1 + -0x7fff) && iVar2 != -0x7fff) {
      DAT_febe6e74 = 0x7fff;
    }
    else {
      DAT_febe6e74 = (undefined2)iVar1;
    }
  }
  else {
    DAT_febe6e74 = 0x8001;
  }
  return;
}

void return_only_stub_38e4e(void)

{
  return;
}

void return_only_stub_38e50(void)

{
  return;
}

void scale_first_phase_codes(int scale,ushort *triplet)

{
  uint uVar1;
  uint uVar2;
  uint uVar3;
  uint uVar4;
  uint uVar5;
  uint uVar6;
  
  DAT_febe6e90 = (((int)(int16_t)DAT_febe6e3a) * scale) / 0x400;
  uVar6 = (((int)(int16_t)DAT_febe6e3c) * scale) / 0x400;
  uVar1 = (((int)(int16_t)DAT_febe6e3e) * scale) / 0x400;
  DAT_febe6e7c = DAT_00031e3c;
  DAT_febe6e86 = DAT_00031e3a;
  if (DAT_febe6d5c == '\0') {
    DAT_febe6e7c = DAT_00031e40;
    DAT_febe6e86 = DAT_00031e3e;
  }
  uVar5 = (uint)DAT_febe6e86;
  uVar4 = (uint)DAT_febe6e7c;
  uVar2 = uVar5;
  if ((int)(((int)(int32_t)DAT_febe6e90) - uVar5) < 0 != ((int)DAT_febe6e90 < 0 && -1 < (int)(((int)(int32_t)DAT_febe6e90) - uVar5))
     ) {
    uVar2 = ((int)(int32_t)DAT_febe6e90);
  }
  uVar3 = uVar4;
  if ((int)(uVar2 - uVar4) < 0 == ((int)uVar2 < 0 && -1 < (int)(uVar2 - uVar4))) {
    uVar3 = uVar2;
  }
  DAT_febe6e88 = DAT_febe6e7c;
  DAT_febe6e94 = uVar6;
  DAT_febe6e98 = uVar1;
  *triplet = (ushort)uVar3;
  uVar2 = uVar5;
  if ((int)(uVar6 - uVar5) < 0 != ((int)uVar6 < 0 && -1 < (int)(uVar6 - uVar5))) {
    uVar2 = uVar6;
  }
  uVar6 = uVar4;
  if ((int)(uVar2 - uVar4) < 0 == ((int)uVar2 < 0 && -1 < (int)(uVar2 - uVar4))) {
    uVar6 = uVar2;
  }
  triplet[1] = (ushort)uVar6;
  if ((int)(uVar1 - uVar5) < 0 != ((int)uVar1 < 0 && -1 < (int)(uVar1 - uVar5))) {
    uVar5 = uVar1;
  }
  if ((int)(uVar5 - uVar4) < 0 == ((int)uVar5 < 0 && -1 < (int)(uVar5 - uVar4))) {
    DAT_febe6e7c = (ushort)uVar5;
  }
  triplet[2] = DAT_febe6e7c;
  DAT_febe6e78 = (ushort)uVar3;
  DAT_febe6e7a = (ushort)uVar6;
  return;
}

void scale_second_phase_codes(int scale,ushort *triplet)

{
  uint uVar1;
  uint uVar2;
  uint uVar3;
  uint uVar4;
  uint uVar5;
  uint uVar6;
  
  DAT_febe6e9c = (((int)(int16_t)DAT_febe6e4a) * scale) / 0x400;
  uVar6 = (((int)(int16_t)DAT_febe6e4c) * scale) / 0x400;
  uVar1 = (((int)(int16_t)DAT_febe6e4e) * scale) / 0x400;
  DAT_febe6e82 = DAT_00031e3c;
  DAT_febe6e8a = DAT_00031e3a;
  if (DAT_febe6d5d == '\0') {
    DAT_febe6e82 = DAT_00031e40;
    DAT_febe6e8a = DAT_00031e3e;
  }
  uVar5 = (uint)DAT_febe6e8a;
  uVar4 = (uint)DAT_febe6e82;
  uVar2 = uVar5;
  if ((int)(((int)(int32_t)DAT_febe6e9c) - uVar5) < 0 != ((int)DAT_febe6e9c < 0 && -1 < (int)(((int)(int32_t)DAT_febe6e9c) - uVar5))
     ) {
    uVar2 = ((int)(int32_t)DAT_febe6e9c);
  }
  uVar3 = uVar4;
  if ((int)(uVar2 - uVar4) < 0 == ((int)uVar2 < 0 && -1 < (int)(uVar2 - uVar4))) {
    uVar3 = uVar2;
  }
  DAT_febe6e8c = DAT_febe6e82;
  DAT_febe6ea0 = uVar6;
  DAT_febe6ea4 = uVar1;
  *triplet = (ushort)uVar3;
  uVar2 = uVar5;
  if ((int)(uVar6 - uVar5) < 0 != ((int)uVar6 < 0 && -1 < (int)(uVar6 - uVar5))) {
    uVar2 = uVar6;
  }
  uVar6 = uVar4;
  if ((int)(uVar2 - uVar4) < 0 == ((int)uVar2 < 0 && -1 < (int)(uVar2 - uVar4))) {
    uVar6 = uVar2;
  }
  triplet[1] = (ushort)uVar6;
  if ((int)(uVar1 - uVar5) < 0 != ((int)uVar1 < 0 && -1 < (int)(uVar1 - uVar5))) {
    uVar5 = uVar1;
  }
  if ((int)(uVar5 - uVar4) < 0 == ((int)uVar5 < 0 && -1 < (int)(uVar5 - uVar4))) {
    DAT_febe6e82 = (ushort)uVar5;
  }
  triplet[2] = DAT_febe6e82;
  DAT_febe6e7e = (ushort)uVar3;
  DAT_febe6e80 = (ushort)uVar6;
  return;
}

void publish_current_output_slot(void)

{
  ushort first[3];
  ushort second[3];
  int scale;

  scale = (int)DAT_00031e38;
  scale_first_phase_codes(scale, first);
  scale_second_phase_codes(scale, second);
  DAT_febe6e84 = DAT_00031e38;
  write_phase_output_slot_pair(2, 0, first, second);
  activate_phase_output_slot_pair(0);
  return;
}

void return_only_stub_38fa8(void)

{
  return;
}

void return_only_stub_38faa(void)

{
  return;
}

int current_reference_envelope_signed_product(void)

{
  int local_8;
  
  store_symmetric_saturating_s32_product_706ae(DAT_febee744,(int)((int)(int16_t)DAT_febee5c4),&local_8);
  return local_8;
}

uint qualify_additional_current_reference_envelope(int signed_product)

{
  uint uVar1;
  
  if (((((DAT_febee741 == '\x11') || (DAT_febee741 == '\"')) && (0 < signed_product)) ||
      (DAT_febee741 == '\0')) &&
     (((DAT_febeeac0 != '\x11' || (DAT_febeeac6 < (*((ushort *)camry_host_ptr((uint32_t)(*((volatile uint32_t *)camry_host_ptr((uint32_t)(0x31ec4u + (uint32_t)(DAT_febee5c3 & 1) * 4u)))))))))
      && ((DAT_febee740 == '\0' && (DAT_febee742 == '\0')))))) {
    uVar1 = 0x5a;
  }
  else {
    uVar1 = 0;
  }
  if (DAT_000317b0 == 'Z') {
    uVar1 = 0;
  }
  if (DAT_febeeac2 == 'Z') {
    uVar1 = 0;
  }
  return uVar1;
}
